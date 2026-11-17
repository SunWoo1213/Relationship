"""FIX-037 0번 -- 인식(의도·도구·유형)과 조회 답을 로컬 서버로 재는 프로브.

Refs: FIX-037 P5-loop P5b-query-turn D16 S3.4 원칙7 원칙8

무엇을 재나 (FIX-037 "수정안 0번"):
- 인식: `heldout.jsonl` 의 발화를 **빈 새 시험 계정**에 발화마다 `REPEAT_RECOGNITION`(=5)회
  보낸다. 확인 칩에는 답하지 않는다(저장 0). 각 턴의 `trace_ids` 로 `agent_traces` 의
  `loop_extract`(제안·의도)·`loop_gate`(통과·거부)를 읽어 시도 1건을 만든다.
- 조회 답: `query_answer.json` 의 준비 발화로 사건 3건 이상이 쌓인 카드를 **한 번** 만든 계정
  (자격은 `--secrets-dir` 파일)에 근황 문형 4개 + 기록에 없는 것을 묻는 문형 2개를 각
  `REPEAT_ANSWER`(=3)회 보낸다. 조회 턴은 저장하지 않으므로 수정 전후에 같은 카드를 쓴다.

출력은 표준출력뿐이다(프로젝트 안에 파일을 쓰지 않는다 -- 증거는 save_evidence.py 가 남긴다).
시도 한 건마다 `TRIAL <json>` / `ANSWER <json>` 한 줄, 카드 사진은 `CARD <json>` 한 줄.
`summarize` 는 그 줄들이 들어 있는 파일(증거 파일 그대로)을 읽어 지표를 다시 계산한다 --
같은 증거 파일 -> 같은 수치(원칙8). 비밀번호·쿠키는 출력하지 않는다.

실행(저장소 루트에서):
    .venv/bin/python evaluation/recognition/probe.py run --label before --part recognition --secrets-dir <스크래치>
    .venv/bin/python evaluation/recognition/probe.py run --label before --part answer --secrets-dir <스크래치>
    .venv/bin/python evaluation/recognition/probe.py summarize <증거파일> [<증거파일> ...]

DB 읽기는 `docker exec <컨테이너> psql`(읽기 전용 SELECT 1개)로 한다 -- 서버의 비밀이
필요 없다. 배포 서버는 부르지 않는다(`--base` 기본값은 로컬).
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

HERE = Path(__file__).resolve().parent
HELDOUT = HERE / "heldout.jsonl"
QA_SPEC = HERE / "query_answer.json"

#: FIX-037 0번이 고정한 반복 횟수. 바꾸면 전후 비교가 깨진다.
REPEAT_RECOGNITION = 5
REPEAT_ANSWER = 3

#: `app.db.models.EVENT_TYPES` 와 같은 7종(S3.4). import 하지 않고 적어 두는 이유: 프로브는
#: 서버 밖에서 HTTP 로만 재며, 수정 뒤에도 같은 기준(고정 집합)으로 이탈을 세야 한다.
EVENT_TYPES = ("conflict", "praise", "meal", "meeting", "personal_share", "favor", "other")
#: 라벨에 쓰는 기록 도구(기대 도구 집합의 어휘).
LABEL_TOOLS = ("add_event", "update_person", "add_schedule")

#: "기록이 없어요" 판정. 엄격 = 프롬프트가 지시한 그 문구, 넓게 = 같은 뜻의 변형.
NO_RECORD_STRICT = "기록이 없"
NO_RECORD_BROAD = re.compile(r"기록(이|은|된 (것|게|내용|정보)이?)\s*없|기록(되어|돼) ?있지 않")

LOCAL_BASE = "http://localhost:8000"
#: 프로브가 부를 수 있는 호스트(정확 일치). 배포 서버는 부르지 않는다.
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1"})
DB_CONTAINER = "capstone2-postgres-1"


# ---------------------------------------------------------------------------
# 입출력
# ---------------------------------------------------------------------------


def load_heldout() -> list[dict[str, Any]]:
    return [json.loads(line) for line in HELDOUT.read_text(encoding="utf-8").splitlines() if line.strip()]


def emit(tag: str, obj: dict[str, Any]) -> None:
    print(f"{tag} " + json.dumps(obj, ensure_ascii=False, sort_keys=True), flush=True)


def read_traces(ids: list[int], container: str) -> dict[int, dict[str, Any]]:
    if not ids:
        return {}
    id_list = ",".join(str(int(i)) for i in ids)
    sql = (
        "select coalesce(json_agg(json_build_object('id', id, 'step', step, 'session_id', session_id,"
        " 'output', output) order by id), '[]') from agent_traces where id in (" + id_list + ")"
    )
    out = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "app", "-d", "relationship", "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return {row["id"]: row for row in json.loads(out)}


def client(base: str) -> httpx.Client:
    return httpx.Client(base_url=base, timeout=180)


def set_cookie(c: httpx.Client, resp: httpx.Response) -> None:
    # http 에서는 Secure 쿠키가 실리지 않으므로 Set-Cookie 첫 조각을 헤더로 직접 단다(조사 스크립트 방식).
    c.headers["Cookie"] = resp.headers.get("set-cookie", "").split(";")[0]


def signup(c: httpx.Client, prefix: str, secrets_file: Path) -> str:
    username = prefix + time.strftime("%m%d%H%M%S")
    pw = secrets.token_urlsafe(12)
    secrets_file.write_text(f"{username}\n{pw}\n", encoding="utf-8")
    r = c.post("/auth/signup", json={"username": username, "password": pw, "nickname": username})
    r.raise_for_status()
    set_cookie(c, r)
    return username


def login(c: httpx.Client, secrets_file: Path) -> str:
    username, pw = secrets_file.read_text(encoding="utf-8").split()
    r = c.post("/auth/login", json={"username": username, "password": pw})
    r.raise_for_status()
    set_cookie(c, r)
    return username


# ---------------------------------------------------------------------------
# 한 턴 -> 시도 레코드
# ---------------------------------------------------------------------------


def proposals_of(extract_out: dict[str, Any]) -> list[dict[str, Any]]:
    """`loop_extract.output.tool_calls`(파싱된 제안)에서 도구 이름·유형·사실 키만 뽑는다."""

    rows = []
    for call in extract_out.get("tool_calls") or []:
        args = call.get("args") or {}
        facts = args.get("facts") if isinstance(args.get("facts"), list) else []
        rows.append(
            {
                "name": call.get("name"),
                "type": args.get("type") if call.get("name") == "add_event" else None,
                "fact_keys": [f.get("key") for f in facts if isinstance(f, dict)],
            }
        )
    return rows


def chat_turn(c: httpx.Client, utterance: str, container: str) -> dict[str, Any]:
    r = c.post("/chat", json={"utterance": utterance})
    rec: dict[str, Any] = {"status": r.status_code}
    if r.status_code != 200:
        rec["error"] = r.text[:300]
        return rec
    d = r.json()
    traces = read_traces(d.get("trace_ids") or [], container)
    by_step: dict[str, dict[str, Any]] = {}
    for t in traces.values():
        by_step.setdefault(t["step"], t)
    ext = (by_step.get("loop_extract") or {}).get("output") or {}
    gate = (by_step.get("loop_gate") or {}).get("output") or {}
    query = (by_step.get("loop_query") or {}).get("output")
    raw = ext.get("raw") if isinstance(ext.get("raw"), dict) else {}
    pq = d.get("pending_question")
    rec.update(
        {
            "reply": d.get("reply"),
            "stored": d.get("stored"),
            "stop_reason": d.get("stop_reason"),
            "pending_kind": pq.get("kind") if pq else None,
            "trace_ids": d.get("trace_ids"),
            "intent": ext.get("intent"),
            "raw_intent": raw.get("intent"),
            "proposals": proposals_of(ext),
            "accepted": [a.get("name") for a in gate.get("accepted") or []],
            "rejected": [{"name": x.get("name"), "reason": x.get("reason")} for x in gate.get("rejected") or []],
            "query": None
            if query is None
            else {k: query.get(k) for k in ("answer_source", "fallback_reason", "person_id", "evidence_counts")},
        }
    )
    return rec


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


def run_recognition(args: argparse.Namespace) -> None:
    items = load_heldout()
    c = client(args.base)
    username = signup(c, "fx37r", Path(args.secrets_dir) / f"recognition-{args.label}.txt")
    print(f"ACCOUNT recognition {args.label} {username}", flush=True)
    for rep in range(REPEAT_RECOGNITION):
        for it in items:
            rec = chat_turn(c, it["utterance"], args.container)
            rec.update({"label": args.label, "id": it["id"], "rep": rep})
            emit("TRIAL", rec)


#: 준비 발화 재시도 상한. 준비는 측정이 아니라 카드 만들기다 -- 인식 결함(FIX-037 (a)·(g)) 때문에
#: 한 번에 사건이 3건 안 쌓일 수 있어, 아직 저장되지 않은 준비 발화만 다시 보낸다.
SETUP_MAX_PASSES = 3


def stored_raw_utterances(c: httpx.Client) -> set[str]:
    raws: set[str] = set()
    for p in c.get("/persons").json():
        for ev in c.get(f"/persons/{p['id']}").json().get("timeline") or []:
            raws.add(c.get(f"/events/{ev['id']}/raw").json().get("raw_utterance"))
    return raws


def setup_answer_card(c: httpx.Client, spec: dict[str, Any], utterances: list[str], created: bool) -> None:
    """준비 발화를 넣고 칩에 답해 카드에 사건을 쌓는다. 첫 새 인물 칩은 지정 관계로 확인,
    이후 새 인물 칩은 "아니요"(중복 인물 방지), 같은 사람 확인은 후보 이름(첫 선택지)."""

    for utt in utterances:
        d = c.post("/chat", json={"utterance": utt}).json()
        steps = []
        pq = d.get("pending_question")
        while pq:
            opts = pq["options"]
            if pq["kind"] == "new_person":
                ans = next(o for o in opts if spec["relation"] in o) if not created else opts[-1]
                created = created or ans != opts[-1]
            elif pq["kind"] == "identity":
                ans = opts[0]
            else:
                ans = opts[0]
            r2 = c.post(f"/answers/{pq['question_id']}", json={"answer": ans}).json()
            steps.append({"kind": pq["kind"], "answer": ans, "stored": r2.get("stored")})
            pq = r2.get("pending_question")
        emit("SETUP", {"utterance": utt, "stored": d.get("stored"), "steps": steps})


def card_snapshot(c: httpx.Client) -> dict[str, Any]:
    persons = c.get("/persons").json()
    cards = [c.get(f"/persons/{p['id']}").json() for p in persons]
    return {"persons": persons, "cards": cards}


def run_answer(args: argparse.Namespace) -> None:
    spec = json.loads(QA_SPEC.read_text(encoding="utf-8"))
    c = client(args.base)
    secrets_file = Path(args.secrets_dir) / "answer-card.txt"
    if secrets_file.exists():
        username = login(c, secrets_file)
        print(f"ACCOUNT answer reuse {username}", flush=True)
    else:
        username = signup(c, "fx37a", secrets_file)
        print(f"ACCOUNT answer new {username}", flush=True)
    for npass in range(SETUP_MAX_PASSES):
        snap = card_snapshot(c)
        n_events = max((len(card.get("timeline") or []) for card in snap["cards"]), default=0)
        if n_events >= spec["min_events"]:
            break
        done = stored_raw_utterances(c)
        todo = [u for u in spec["setup_utterances"] if u not in done]
        print(f"SETUP_PASS {npass} 사건 {n_events}건, 다시 보낼 준비 발화 {len(todo)}개", flush=True)
        setup_answer_card(c, spec, todo, created=bool(snap["cards"]))
    snap = card_snapshot(c)
    emit("CARD", {"label": args.label, **snap})
    n_events = max((len(card.get("timeline") or []) for card in snap["cards"]), default=0)
    if len(snap["cards"]) != 1 or n_events < spec["min_events"]:
        print(f"ABORT 카드 조건 미달: 인물 {len(snap['cards'])}명, 최대 사건 {n_events}건", flush=True)
        sys.exit(4)
    for rep in range(REPEAT_ANSWER):
        for q in spec["questions"]:
            rec = chat_turn(c, q["utterance"], args.container)
            rec.update({"label": args.label, "id": q["id"], "kind": q["kind"], "rep": rep})
            emit("ANSWER", rec)


# ---------------------------------------------------------------------------
# summarize -- 증거 파일의 TRIAL/ANSWER 줄만으로 지표를 다시 계산한다
# ---------------------------------------------------------------------------


def parse_lines(paths: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trials, answers = [], []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.startswith("TRIAL "):
                trials.append(json.loads(line[6:]))
            elif line.startswith("ANSWER "):
                answers.append(json.loads(line[7:]))
    return trials, answers


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100.0 * n / d:.1f}%)" if d else f"{n}/0 (-)"


def write_tools(tr: dict[str, Any]) -> set[str]:
    return {p["name"] for p in tr.get("proposals") or [] if p["name"] in LABEL_TOOLS}


def event_types(tr: dict[str, Any]) -> list[Any]:
    return [p["type"] for p in tr.get("proposals") or [] if p["name"] == "add_event"]


def summarize_recognition(label: str, trials: list[dict[str, Any]], items: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ok = [t for t in trials if t.get("status") == 200]
    m: dict[str, Any] = {"label": label, "trials": len(trials), "http_errors": len(trials) - len(ok)}

    def count(pred: Any, rows: list[dict[str, Any]]) -> tuple[int, int]:
        return sum(1 for t in rows if pred(t)), len(rows)

    # 1. 의도 일치율 (전체 · 묶음별)
    m["intent_match"] = count(lambda t: t["intent"] == items[t["id"]]["intent"], ok)
    for g in ("fact", "event", "query", "mixed", "schedule"):
        rows = [t for t in ok if items[t["id"]]["group"] == g]
        m[f"intent_match_{g}"] = count(lambda t: t["intent"] == items[t["id"]]["intent"], rows)
    rec_rows = [t for t in ok if items[t["id"]]["intent"] == "record"]
    m["intent_match_record_labeled"] = count(lambda t: t["intent"] == "record", rec_rows)
    m["intent_missing_raw"] = count(lambda t: t.get("raw_intent") is None, ok)

    # 2. 유형 일치율 -- 기대 유형이 있는 발화: 제안된 add_event 중 기대 유형이 하나라도 있으면 일치
    typed = [t for t in ok if items[t["id"]]["expected_type"]]
    m["type_match"] = count(lambda t: items[t["id"]]["expected_type"] in event_types(t), typed)
    m["type_match_event_group"] = count(
        lambda t: items[t["id"]]["expected_type"] in event_types(t),
        [t for t in typed if items[t["id"]]["group"] == "event"],
    )
    conflict = [t for t in typed if items[t["id"]]["expected_type"] == "conflict"]
    m["type_match_conflict"] = count(lambda t: "conflict" in event_types(t), conflict)
    m["type_no_add_event"] = count(lambda t: not event_types(t), typed)

    # 3. enum 이탈 -- 모든 시도의 add_event 제안 중 7종 밖 유형
    all_types = [x for t in ok for x in event_types(t)]
    m["enum_violation"] = (sum(1 for x in all_types if x not in EVENT_TYPES), len(all_types))
    m["enum_violation_values"] = dict(Counter(str(x) for x in all_types if x not in EVENT_TYPES))
    m["bad_args_rejections"] = sum(1 for t in ok for r in t["rejected"] if r["reason"] == "bad_args")

    # 4. 도구 -- 기대 도구 집합과 제안된 기록 도구 집합
    m["tool_exact"] = count(lambda t: write_tools(t) == set(items[t["id"]]["expected_tools"]), ok)
    m["tool_cover_record_labeled"] = count(lambda t: set(items[t["id"]]["expected_tools"]) <= write_tools(t), rec_rows)
    mixed = [t for t in ok if items[t["id"]]["group"] == "mixed"]
    m["tool_cover_mixed"] = count(lambda t: set(items[t["id"]]["expected_tools"]) <= write_tools(t), mixed)

    # 5. 끝까지 -- 기록 라벨 발화: 의도 record 이고 기대 도구가 모두 게이트를 통과
    m["record_end_to_end"] = count(
        lambda t: t["intent"] == "record" and set(items[t["id"]]["expected_tools"]) <= set(t["accepted"]), rec_rows
    )
    m["query_turn_no_write_turns"] = count(
        lambda t: any(r["reason"] == "query_turn_no_write" for r in t["rejected"]), rec_rows
    )

    # 발화별 표
    per: dict[str, dict[str, Any]] = {}
    for iid in items:
        rows = [t for t in ok if t["id"] == iid]
        per[iid] = {
            "intent": dict(Counter(str(t["intent"]) for t in rows)),
            "tools": dict(Counter("+".join(sorted(write_tools(t))) or "-" for t in rows)),
            "types": dict(Counter(",".join(str(x) for x in event_types(t)) or "-" for t in rows)),
            "accepted": dict(Counter("+".join(sorted(set(t["accepted"]))) or "-" for t in rows)),
            "rejects": dict(Counter(r["reason"] for t in rows for r in t["rejected"] if r["reason"] != "not_callable_by_llm")),
        }
    m["per_item"] = per
    return m


def summarize_answers(label: str, answers: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [a for a in answers if a.get("status") == 200]
    m: dict[str, Any] = {"label": label, "answers": len(answers), "http_errors": len(answers) - len(ok)}

    def no_record(a: dict[str, Any], strict: bool) -> bool:
        reply = a.get("reply") or ""
        return NO_RECORD_STRICT in reply if strict else bool(NO_RECORD_BROAD.search(reply))

    recent = [a for a in ok if a["kind"] == "recent"]
    absent = [a for a in ok if a["kind"] == "absent"]
    # 근황 답변 = 조회 경로(loop_query)로 인물이 확정되고, 답에 "기록 없음" 뜻의 문구가 없다
    answered = [
        a for a in recent if a.get("query") and a["query"].get("person_id") is not None and not no_record(a, strict=False)
    ]
    m["recent_answered"] = (len(answered), len(recent))
    m["absent_no_record_strict"] = (sum(1 for a in absent if no_record(a, strict=True)), len(absent))
    m["absent_no_record_broad"] = (sum(1 for a in absent if no_record(a, strict=False)), len(absent))
    m["query_route"] = (sum(1 for a in ok if a.get("query")), len(ok))
    per: dict[str, dict[str, Any]] = defaultdict(dict)
    for a in ok:
        src = (a.get("query") or {}).get("answer_source") or f"route:{a.get('intent')}"
        per[a["id"]].setdefault("answer_source", Counter())[src] += 1
        per[a["id"]].setdefault("replies", []).append(a.get("reply"))
    m["per_item"] = {k: {"answer_source": dict(v["answer_source"]), "replies": v["replies"]} for k, v in per.items()}
    return m


def fmt(v: Any) -> str:
    return pct(*v) if isinstance(v, tuple) else str(v)


def summarize(paths: list[str]) -> None:
    items = {it["id"]: it for it in load_heldout()}
    trials, answers = parse_lines(paths)
    out: dict[str, Any] = {"recognition": {}, "answer": {}}
    for label in sorted({t["label"] for t in trials}):
        out["recognition"][label] = summarize_recognition(label, [t for t in trials if t["label"] == label], items)
    for label in sorted({a["label"] for a in answers}):
        out["answer"][label] = summarize_answers(label, [a for a in answers if a["label"] == label])
    for section, by_label in out.items():
        for label, m in by_label.items():
            print(f"== {section} [{label}]")
            for k, v in m.items():
                if k != "per_item":
                    print(f"  {k}: {fmt(v)}")
            print("  -- per_item")
            for iid, row in m["per_item"].items():
                print(f"  {iid}: " + json.dumps(row, ensure_ascii=False, sort_keys=True))
    print("SUMMARY_JSON " + json.dumps(out, ensure_ascii=False, sort_keys=True, default=list))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    # 라벨은 측정 회차 이름일 뿐 집계 방식과 무관하다(after3 = FIX-037 2차, after4 = 3차 수정 뒤).
    r.add_argument("--label", required=True, choices=["before", "after", "after3", "after4"])
    r.add_argument("--part", required=True, choices=["recognition", "answer"])
    r.add_argument("--secrets-dir", required=True, help="시험 계정 자격 파일을 둘 프로젝트 밖 디렉터리")
    r.add_argument("--base", default=LOCAL_BASE)
    r.add_argument("--container", default=DB_CONTAINER)
    s = sub.add_parser("summarize")
    s.add_argument("files", nargs="+")
    args = ap.parse_args()
    if args.cmd == "summarize":
        summarize(args.files)
        return
    # R-37-9: 접두 일치가 아니라 호스트를 파싱해 정확히 비교한다(`http://localhost.example.com` 거부).
    parsed = urlsplit(args.base)
    if parsed.scheme != "http" or parsed.hostname not in LOCAL_HOSTS:
        sys.exit("로컬 서버만 잰다(--base 는 localhost)")
    secrets_dir = Path(args.secrets_dir).resolve()
    if secrets_dir.is_relative_to(HERE.parents[1]):
        sys.exit("--secrets-dir 는 저장소 밖이어야 한다(비밀번호 파일)")
    secrets_dir.mkdir(parents=True, exist_ok=True)
    print(f"START {args.part} {args.label} {time.strftime('%Y-%m-%dT%H:%M:%S%z')}", flush=True)
    (run_recognition if args.part == "recognition" else run_answer)(args)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
