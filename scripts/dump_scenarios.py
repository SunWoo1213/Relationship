"""Refs: P1-pilot-dataset S3.7 원칙8 L-002

평가 시나리오 데이터셋(`data/scenarios/`)을 **사람이 읽는 검수 패킷**(Markdown)
으로 덤프한다. 01-plan U5 — "검수자가 볼 수 있게 시나리오를 사람이 읽는 표로
덤프한다(발화 / 언급 표면형 / 골드 인물 / 카테고리 / 함정 여부). 이 단위는
**검수를 하지 않는다** — 검수 요청까지다."

L-002: 데이터를 만든 eval-agent 는 자기 라벨을 검수하지 않는다. 이 스크립트는
판정을 하지 않고 **판정할 것을 나열**한다. 판정은 verifier(새 컨텍스트) 또는
사용자가 `evidence/<ts>-label-review.md` 에 쓴다.

사용::

    python scripts/dump_scenarios.py
    python scripts/dump_scenarios.py --out docs/wiki/.../evidence/2026...-review-packet.md

**네트워크·DB·LLM 을 쓰지 않는다.** `app/` 도 import 하지 않고, 검증기
(`scripts/validate_scenarios.py`)의 적재 함수만 재사용한다 — JSON 을 읽는 코드가
두 벌이면 어긋난다.

재현성(원칙8): 본문은 같은 입력이면 같은 바이트다. 시각에 의존하는 것은 머리의
"생성" 줄 하나뿐이고, 그 값도 **출력 파일명의 타임스탬프에서 가져온다**(따로
시계를 읽지 않는다). 같은 `--out` 으로 두 번 돌리면 같은 파일이 나온다.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_scenarios import (  # noqa: E402
    DEFAULT_DIR,
    _dict_items,
    _scenario_id,
    load_dataset,
)

#: 기본 출력 디렉터리(패키지 evidence). verifier 의 쓰기 허용 경로이기도 하다(H-3).
DEFAULT_OUT_DIR = Path("docs/wiki/packages/P1-pilot-dataset/evidence")

#: 검수자가 **각 시나리오마다** 판정할 항목. 01-plan 리스크("개인정보",
#: "한국어 구어체 부족", "함정 난이도의 자의성")와 02-plan-verify 권고 R-4
#: (고민 상담 발화 배제)·R-5(new_person 하위 유형)에서 그대로 왔다.
REVIEW_ITEMS: tuple[tuple[str, str], ...] = (
    (
        "라벨 정확성",
        "mentions 의 gold_person_id 가 문맥상 맞는가. ambiguous 표시가 정말 "
        "사람도 못 정하는 건인가. expected_ask_user.allowed 집합이 타당한가(D10 — "
        "임계치에 따라 달라지므로 단일 정답이 아니다).",
    ),
    (
        "함정 난이도",
        "함정(trap) 건을 **사람이 문맥으로 정할 수 있는가**. 너무 쉬우면 오병합률이 "
        "0 으로 나오고, 사람도 못 푸는 수준이면 그 값은 모델이 아니라 저자가 정한 "
        "값이 된다(01-plan 리스크 '함정 난이도의 자의성').",
    ),
    (
        "구어체 규칙",
        "조사 생략·종결어미 축약·ㅋㅋ 허용·오타 1개 이하. 문어체 완결 문장으로 "
        "기울면 P4 수치가 실사용보다 **좋게** 나온다 — 과대평가 방향의 편향이다. "
        "길이 8~60자·턴 수 2~6 은 검증기 검사 (13) 이 이미 세었으니 여기서는 "
        "문체만 본다.",
    ),
    (
        "개인정보·실명 없음",
        "발화 본문에 실존 인물·실제 회사명·연락처가 없는가. 검증기 검사 (7) 은 "
        "persons 의 이름만 보고 **utterances 본문은 보지 않는다** — 이 항목이 그 "
        "구멍을 메운다.",
    ),
    (
        "고민 상담·감정 조언 아님 (R-4)",
        "발화가 고민 상담이나 감정 조언을 요청하는 대화가 아닌가(기획서 2장 제외 "
        "목록, 원칙7). 상황 서술은 괜찮고, 조언을 구하는 문장이면 지적한다.",
    ),
    (
        "events 라벨 타당",
        "events[].type 고정 7종 선택이 발화와 맞는가. occurred_at_kind "
        "(relative/absolute/none)가 맞는가(결정 B — 절대 시각은 라벨하지 않는다).",
    ),
    (
        "new_person 하위 유형 (R-5)",
        "등록 대상(사용자와 관계를 맺는 새 인물)과 지나가는 언급(등록하면 안 되는 "
        "지칭)의 구분이 맞는가. passing_mentions 에 적힌 surface·why 가 타당한가 — "
        "여기서 인물 생성이나 ask_user(new_person)가 나오면 P4 는 오탐으로 센다.",
    ),
)


def esc(value: Any) -> str:
    """Markdown 표 셀용. 파이프와 줄바꿈만 막는다(내용은 바꾸지 않는다)."""
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def stamp_from_path(path: Path) -> str:
    """파일명 앞의 `YYYYMMDD-HHMM` 을 그대로 쓴다(시계를 따로 읽지 않는다)."""
    head = path.name.split("-review-packet")[0]
    return head


def person_rows(scenario: dict[str, Any]) -> list[str]:
    seeds = {s for s in scenario.get("seed_persons", []) if isinstance(s, str)}
    rows = [
        "| person_id | display_name | 관계 태그 | 위계 | aliases | seed |",
        "|---|---|---|---|---|---|",
    ]
    for person in _dict_items(scenario.get("persons")):
        aliases = person.get("aliases")
        alias_text = " / ".join(
            str(a) for a in aliases if isinstance(a, str)
        ) if isinstance(aliases, list) else ""
        rows.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                esc(person.get("person_id")),
                esc(person.get("display_name")),
                esc(person.get("relation_tag")),
                esc(person.get("hierarchy")),
                esc(alias_text),
                "예" if person.get("person_id") in seeds else "아니오(새 인물)",
            )
        )
    return rows


def utterance_rows(scenario: dict[str, Any]) -> list[str]:
    utterances = scenario.get("utterances")
    utterances = utterances if isinstance(utterances, list) else []
    rows = [
        "| 턴 | 발화 | mentions (surface → gold) | passing_mentions (등록 금지) | events |",
        "|---|---|---|---|---|",
    ]
    for turn, utterance in enumerate(utterances):
        mention_cell = []
        for mention in _dict_items(scenario.get("mentions")):
            if mention.get("turn") != turn:
                continue
            if mention.get("ambiguous") is True:
                mention_cell.append(
                    f"{esc(mention.get('surface'))} → **ambiguous(정답 없음, 지표 분모 제외)**"
                )
            else:
                mention_cell.append(
                    f"{esc(mention.get('surface'))} → {esc(mention.get('gold_person_id'))}"
                )
        passing_cell = [
            f"{esc(p.get('surface'))} ({esc(p.get('why'))})"
            for p in _dict_items(scenario.get("passing_mentions"))
            if p.get("turn") == turn
        ]
        event_cell = [
            f"{esc(e.get('type'))} / {esc(e.get('occurred_at_kind'))}"
            for e in _dict_items(scenario.get("events"))
            if e.get("turn") == turn
        ]
        rows.append(
            "| {} | {} | {} | {} | {} |".format(
                turn,
                esc(utterance),
                "<br>".join(mention_cell) or "—",
                "<br>".join(passing_cell) or "—",
                "<br>".join(event_cell) or "—",
            )
        )
    return rows


def scenario_block(file_name: str, scenario: dict[str, Any]) -> list[str]:
    trap = scenario.get("trap")
    trap_kind = trap.get("kind") if isinstance(trap, dict) else None
    allowed = scenario.get("expected_ask_user")
    allowed_list = allowed.get("allowed") if isinstance(allowed, dict) else []
    ambiguous = [
        m
        for m in _dict_items(scenario.get("mentions"))
        if m.get("ambiguous") is True
    ]

    lines = [
        f"### {_scenario_id(scenario)} · {esc(scenario.get('category'))}"
        f" · 함정: {esc(trap_kind) if trap_kind else '없음'}",
        "",
        f"- 파일: `{file_name}`",
        "- expected_ask_user.allowed: "
        + ", ".join(f"`{esc(a)}`" for a in allowed_list if isinstance(a, str)),
        "- seed_persons: "
        + (
            ", ".join(f"`{esc(s)}`" for s in scenario.get("seed_persons", []))
            or "없음(대화 전 메모리가 비어 있다)"
        ),
    ]
    if ambiguous:
        lines.append(
            "- ambiguous mention: "
            + ", ".join(
                f"턴 {esc(m.get('turn'))} `{esc(m.get('surface'))}`" for m in ambiguous
            )
            + " — 사람도 정할 수 없다고 라벨한 건. 지표 분모에서 빠진다(H-1)."
        )
    if isinstance(trap, dict):
        lines.append(f"- trap.reason: {esc(trap.get('reason'))}")
    lines.append("")
    lines.extend(person_rows(scenario))
    lines.append("")
    lines.extend(utterance_rows(scenario))
    lines.append("")
    return lines


def build_packet(directory: Path, stamp: str) -> str:
    dataset, _ = load_dataset(directory, strict=False)
    scenarios = [
        (name, sc) for name, sc in dataset.scenarios if isinstance(sc, dict)
    ]
    manifest = dataset.manifest_dict or {}

    lines: list[str] = [
        f"# P1-pilot-dataset 라벨 검수 패킷 ({stamp})",
        "",
        f"- 생성: `python scripts/dump_scenarios.py` (U5 산출물, 판정 없음 — L-002)",
        f"- 대상: `{directory.as_posix()}` · 시나리오 {len(scenarios)}건"
        f" · schema_version {manifest.get('schema_version')}",
        "- 이 문서는 **검수 요청서**다. 판정은 검수자(verifier 새 컨텍스트 또는"
        " 사용자)가 별도 파일에 쓴다 — 아래 '검수 기록 형식' 참조.",
        "- 데이터를 만든 eval-agent 는 이 패킷을 만들 뿐 자기 라벨을 검수하지"
        " 않는다(L-002).",
        "",
        "## 1. 검수 항목 (시나리오마다 판정)",
        "",
    ]
    for index, (title, detail) in enumerate(REVIEW_ITEMS, start=1):
        lines.append(f"{index}. **{title}** — {detail}")
    lines += [
        "",
        "## 2. 검수 기록 형식 (01-plan 산출물 절 H-3 — 그대로 쓴다)",
        "",
        "기록 파일: `docs/wiki/packages/P1-pilot-dataset/evidence/<ts>-label-review.md`"
        " (이 패킷이 아니라 **새 파일**에 쓴다)",
        "",
        "머리 줄:",
        "",
        "```",
        "검수자: verifier (fable, 새 컨텍스트) | 표본: 40/40 | 사용자 검수: 함정 n건·new_person 지나가는 언급 m건",
        "```",
        "",
        "지적 표(열 이름은 `상태` 하나만 쓴다 — R-10, 헤더에 값 이름을 적으면"
        " 완료 판정 grep 이 헤더를 세어 오탐한다):",
        "",
        "```",
        "| id | 시나리오 id | 지적 | 상태 |",
        "|---|---|---|---|",
        "| 1 | sc-0XX | (지적 내용) | (상태 값) |",
        "```",
        "",
        "상태 셀에 쓰는 값은 셋뿐이다: `반영 <커밋 해시>` / `기각 <사유>` /"
        " 아직 처리되지 않은 것(열려 있음). 완료 판정은 U7 이"
        " `grep -cE '\\| *열림 *\\|'` 로 세며 출력 0 이어야 한다.",
        "- 상태 열을 `반영 <해시>` 로 닫는 것도 **검수자**가 한다(R-11) — U6 을"
        " 수행한 eval-agent 가 자기 지적을 닫지 않는다.",
        "- 전건(40/40) 검수는 verifier, 함정 건과 new_person 지나가는 언급 건은"
        " 사용자도 본다(결정 G).",
        "",
        "## 3. 시나리오 40건",
        "",
        "표 읽는 법: `mentions` 는 **정답이 있는 지칭**(gold 인물 id),"
        " `passing_mentions` 는 **등록하면 안 되는 지칭**이다(인물 생성이나"
        " ask_user(new_person)가 나오면 오탐). `events` 셀은 `type / occurred_at_kind`.",
        "",
    ]
    for file_name, scenario in scenarios:
        lines.extend(scenario_block(file_name, scenario))

    names = manifest.get("virtual_names")
    names = names if isinstance(names, list) else []
    lines += [
        "## 4. 가상 성명 전체 목록 (실존 인물 여부 눈검수)",
        "",
        f"`manifest.json.virtual_names` {len(names)}개. 검증기 검사 (7) 은 이 목록"
        " **안에 있는지**만 보므로, 목록 자체에 실존 인물의 이름이 들어가면 아무도"
        " 잡지 못한다. 실존 인물(연예인·정치인·지인 실명)로 읽히는 항목이 있으면"
        " 지적한다. 직급 호칭(`김팀장`)·호칭어(`엄마`)가 섞여 있는 것은 판정 규칙이"
        " 일부러 넓기 때문이며 정상이다.",
        "",
    ]
    for index, name in enumerate(names, start=1):
        lines.append(f"{index}. {name}")
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="시나리오 데이터셋을 검수용 Markdown 으로 덤프(네트워크·DB 없음)."
    )
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="시나리오 디렉터리")
    parser.add_argument(
        "--out",
        default=None,
        help="출력 파일(기본 evidence/<YYYYMMDD-HHMM>-review-packet.md)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"디렉터리가 없다: {directory.as_posix()}", file=sys.stderr)
        return 2

    if args.out:
        out = Path(args.out)
    else:
        out = DEFAULT_OUT_DIR / (
            datetime.now().strftime("%Y%m%d-%H%M") + "-review-packet.md"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    text = build_packet(directory, stamp_from_path(out))
    out.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(f"[write] {out.as_posix()} ({len(text.splitlines()) + 1}행)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
