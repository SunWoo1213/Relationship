"""Refs: P4-pilot-eval D4 원칙8 L-004 -- 실행 CLI·dry-run·비용 가드(U6) 테스트.

두 층으로 나눈다.

- **순수 층**(DB·네트워크 0) -- 데이터셋 지문·`run_id`·비용 추정·환경변수
  이름 확인·스텁의 결정성·인자 조합 거부. 어디에서도 키를 읽지 않는다.
- **사슬 층**(실 PostgreSQL, 네트워크 0) -- `--dry-run --stub` 로 사슬을
  끝까지 돌려 산출물 5종·`network_calls=0`·바이트 재현성·`meta.commit` 을
  본다. `judge_from_env`/`caller_from_env`(실 공급자 팩토리)를 **부르면
  실패하는** 스파이로 바꿔 두고 돌리므로 "네트워크 0"이 문장이 아니라
  단언이다.

실 실행 경로(rc=2)는 키를 지운 환경에서만 본다 -- 이 파일은 실 API 를
부르지 않는다(원칙8).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import run_pilot_eval as cli  # noqa: E402

from evaluation.runner import T_MERGE_GRID, T_NEW  # noqa: E402
from evaluation.scenario_state import load_scenarios  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = REPO_ROOT / "data" / "scenarios"
OUTPUT_NAMES = ("metrics.json", "calibration.json", "curve.csv", "eval.md")


def _scenarios(limit: int | None = None) -> list[dict[str, Any]]:
    items = [scenario for _, scenario in load_scenarios(SCENARIO_DIR)]
    return items if limit is None else items[:limit]


def _raw_files(out_dir: Path) -> list[Path]:
    return sorted(out_dir.glob("raw-*.jsonl"))


@pytest.fixture()
def no_provider_factories(monkeypatch: pytest.MonkeyPatch) -> None:
    """실 공급자 팩토리를 부르면 즉시 실패시킨다(네트워크 0 의 단언)."""

    def _forbidden(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover -- 불리면 실패
        raise AssertionError("실 공급자 팩토리가 불렸다 -- --stub 모드는 네트워크 0 이다")

    monkeypatch.setattr("evaluation.runner.judge_from_env", _forbidden)
    monkeypatch.setattr("evaluation.runner.caller_from_env", _forbidden)


# ---------------------------------------------------------------------------
# 순수 층 -- 데이터셋 지문
# ---------------------------------------------------------------------------


def test_dataset_fingerprint_is_deterministic() -> None:
    first = cli.dataset_fingerprint(SCENARIO_DIR)
    second = cli.dataset_fingerprint(SCENARIO_DIR)
    assert first == second
    assert first.startswith("sha256:")
    assert len(first) == len("sha256:") + 64


def test_dataset_fingerprint_changes_with_any_file(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text('{"x": 1}', encoding="utf-8")
    (tmp_path / "b.json").write_text('{"y": 2}', encoding="utf-8")
    before = cli.dataset_fingerprint(tmp_path)
    (tmp_path / "b.json").write_text('{"y": 3}', encoding="utf-8")
    assert cli.dataset_fingerprint(tmp_path) != before


def test_dataset_fingerprint_ignores_file_order(tmp_path: Path) -> None:
    (tmp_path / "b.json").write_text('{"y": 2}', encoding="utf-8")
    (tmp_path / "a.json").write_text('{"x": 1}', encoding="utf-8")
    first = cli.dataset_fingerprint(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    (other / "a.json").write_text('{"x": 1}', encoding="utf-8")
    (other / "b.json").write_text('{"y": 2}', encoding="utf-8")
    assert cli.dataset_fingerprint(other) == first


def test_dataset_fingerprint_empty_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        cli.dataset_fingerprint(tmp_path)


# ---------------------------------------------------------------------------
# 순수 층 -- run_id
# ---------------------------------------------------------------------------


def _run_id(**over: Any) -> str:
    base: dict[str, Any] = {
        "dataset_hash": "sha256:abc",
        "methods": ("proposed", "llm_single"),
        "grid": T_MERGE_GRID,
        "t_new": T_NEW,
        "run_mode": "stub",
        "commit": None,
        "embedding_model": "stub-embedding",
        "model_configured": {"stub": "stub-judge"},
    }
    base.update(over)
    return cli.compute_run_id(**base)


def test_run_id_is_deterministic_and_has_no_clock() -> None:
    assert _run_id() == _run_id()
    assert _run_id().startswith("run-")
    assert len(_run_id()) == len("run-") + 12


@pytest.mark.parametrize(
    "field, value",
    [
        ("dataset_hash", "sha256:zzz"),
        ("run_mode", "real"),
        ("commit", "dd6a996"),
        ("embedding_model", "text-embedding-3-small"),
        ("model_configured", {"openai": "gpt-4o-mini"}),
        ("methods", ("proposed",)),
    ],
)
def test_run_id_changes_with_each_input(field: str, value: Any) -> None:
    assert _run_id(**{field: value}) != _run_id()


def test_run_id_source_has_no_datetime() -> None:
    source = Path(cli.__file__).read_text(encoding="utf-8")
    body = source.split("def compute_run_id(", 1)[1].split("\ndef ", 1)[0]
    assert "datetime" not in body
    assert "now(" not in body


# ---------------------------------------------------------------------------
# 순수 층 -- 비용 추정
# ---------------------------------------------------------------------------


def test_estimate_counts_two_llm_calls_per_mention() -> None:
    scenarios = _scenarios(3)
    estimate = cli.estimate_run(scenarios)
    mentions = sum(
        len(s.get("mentions") or []) + len(s.get("passing_mentions") or []) for s in scenarios
    )
    assert estimate.mention_count == mentions
    assert estimate.llm_calls_by_method == {"proposed": mentions, "llm_single": mentions}
    assert estimate.llm_calls == 2 * mentions


def test_estimate_prompt_chars_come_from_real_builders() -> None:
    estimate = cli.estimate_run(_scenarios(3))
    # `llm_single` 은 사전 상태 **전 인물**을 프롬프트에 넣으므로 후보만 넣는
    # 제안 방식보다 길다(P3-baselines 인계 12).
    assert estimate.prompt_chars_by_method["llm_single"] > 0
    assert estimate.prompt_chars_by_method["proposed"] > 0


def test_estimate_is_deterministic_and_scales_with_prices() -> None:
    scenarios = _scenarios(3)
    base = cli.estimate_run(scenarios)
    assert base.to_dict() == cli.estimate_run(scenarios).to_dict()
    doubled = cli.estimate_run(
        scenarios,
        price_in_per_1m=cli.PRICE_IN_PER_1M * 2,
        price_out_per_1m=cli.PRICE_OUT_PER_1M * 2,
        price_embed_per_1m=cli.PRICE_EMBED_PER_1M * 2,
    )
    assert doubled.usd_total == pytest.approx(base.usd_total * 2)


def test_estimate_lines_mark_assumptions_and_price_source() -> None:
    estimate = cli.estimate_run(_scenarios(2))
    lines = cli.format_estimate(estimate, run_mode="stub", max_cost_usd=5.0)
    text = "\n".join(lines)
    assert "가정" in text
    assert "price_source=" in text
    assert "cost_usd total=" in text
    assert "max_cost_usd=5.0" in text


def test_full_dataset_estimate_is_under_default_limit() -> None:
    estimate = cli.estimate_run(_scenarios())
    assert estimate.usd_total < cli.DEFAULT_MAX_COST_USD


# ---------------------------------------------------------------------------
# 순수 층 -- 환경변수는 이름만
# ---------------------------------------------------------------------------


def test_missing_real_env_lists_names_only() -> None:
    assert cli.missing_real_env({}) == list(cli.REQUIRED_REAL_ENV)
    assert cli.missing_real_env({"OPENAI_API_KEY": "  "}) == ["OPENAI_API_KEY"]
    assert cli.missing_real_env({"OPENAI_API_KEY": "value"}) == []


def test_source_never_reads_dotenv_and_never_dumps_env() -> None:
    source = Path(cli.__file__).read_text(encoding="utf-8")
    assert "dotenv" not in source
    assert "open(\".env" not in source
    assert "dict(os.environ)" not in source
    assert "os.environ.items()" not in source
    # 읽는 환경변수는 이름이 코드에 적힌 것뿐이다.
    read_names = {
        line.split('os.environ.get("', 1)[1].split('"', 1)[0]
        for line in source.splitlines()
        if 'os.environ.get("' in line
    }
    assert read_names <= set(cli.REQUIRED_REAL_ENV) | set(cli.OPTIONAL_REAL_ENV)


# ---------------------------------------------------------------------------
# 순수 층 -- 스텁
# ---------------------------------------------------------------------------


class _Candidate:
    def __init__(self, person_id: int, display_name: str) -> None:
        self.person_id = person_id
        self.display_name = display_name


def test_stub_judge_score_does_not_depend_on_person_id() -> None:
    judge = cli.StubJudge()
    first = judge.judge("김팀장", "발화", [_Candidate(1, "김도윤")])
    second = judge.judge("김팀장", "발화", [_Candidate(999, "김도윤")])
    assert first.s_llm == second.s_llm
    assert first.provider == cli.STUB_PROVIDER
    assert first.model == cli.STUB_JUDGE_MODEL


def test_stub_judge_spreads_scores_over_bins() -> None:
    scores = {cli.StubJudge.score_for("mention", f"사람{i}") for i in range(40)}
    assert len(scores) > 3
    assert all(0.0 <= s <= 1.0 for s in scores)


def test_stub_caller_is_deterministic_ignoring_ids() -> None:
    caller = cli.StubSingleCaller()
    text = '이미 아는 인물 목록(전체):\n- {"person_id": 7, "display_name": "김도윤"}'
    other = text.replace('"person_id": 7', '"person_id": 4242')
    first = caller.complete("sys", text)
    second = caller.complete("sys", other)
    assert first.raw["s_llm"] == second.raw["s_llm"]
    assert first.raw["matched_person_id"] == 7
    assert second.raw["matched_person_id"] == 4242
    assert first.provider == cli.STUB_PROVIDER


def test_stub_caller_reports_new_person_without_candidates() -> None:
    result = cli.StubSingleCaller().complete("sys", "이미 아는 인물 목록(전체):\n(없음)")
    assert result.raw["decision"] == "new_person"
    assert result.raw["matched_person_id"] is None


def test_stub_embedder_is_deterministic_unit_vectors() -> None:
    embedder = cli.StubEmbedder(dimension=8)
    first = embedder.embed(["가", "나"])
    second = cli.StubEmbedder(dimension=8).embed(["가", "나"])
    assert first == second
    assert first[0] != first[1]
    for vector in first:
        assert len(vector) == 8
        assert sum(v * v for v in vector) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 순수 층 -- trace 표본 덤프 · 확신도 재계산 (U7 선행, DB·네트워크 0)
# ---------------------------------------------------------------------------


class _FakeTrace:
    """`agent_traces` 행 모양(덤프가 읽는 5개 속성만)."""

    def __init__(self, trace_id: int, session_id: str, output: dict[str, Any]) -> None:
        from app.er.types import ER_TRACE_STEP, ER_TRACE_TOOL_NAME

        self.id = trace_id
        self.session_id = session_id
        self.step = ER_TRACE_STEP
        self.tool_name = ER_TRACE_TOOL_NAME
        self.output = output


class _FakeSession:
    """`session.scalars(select(...))` 만 흉내 낸다 -- **조회 조건을 실제로
    적용해서** 걸러 준다(WHERE 절이 계약대로인지 테스트가 본다)."""

    def __init__(self, traces: list[_FakeTrace]) -> None:
        self.traces = traces
        self.statements: list[Any] = []

    def scalars(self, statement: Any) -> list[_FakeTrace]:
        self.statements.append(statement)
        params = statement.compile().params
        wanted = set(params["id_1"])
        return [
            trace
            for trace in self.traces
            if trace.id in wanted
            and trace.session_id == params["session_id_1"]
            and trace.step == params["step_1"]
            and trace.tool_name == params["tool_name_1"]
        ]


def _resolution_output(
    *,
    mention: str = "김팀장",
    s_llm: float = 0.73,
    s_emb: float = 0.8123456789,
    s_rule: float = 0.6666666666666666,
    t_merge: float = 0.8,
    matched: int | None = 7,
) -> dict[str, Any]:
    """`agent_traces.output` 을 **제품 코드로** 만든다(손으로 적은 숫자가
    아니라 `decide()` → `Resolution.to_dict()` 가 낸 것)."""

    from app.er.confidence import decide
    from app.er.types import ERConfig, Judgement, Resolution, ScoredCandidate

    config = ERConfig(t_merge=t_merge, t_new=T_NEW)
    candidate = ScoredCandidate(
        person_id=7,
        display_name="김도윤",
        aliases=["김팀장"],
        relation_tag="직장",
        hierarchy="상",
        s_emb=s_emb,
        rule_flags={"exact_alias": True},
        rule_checked=2,
        rule_passed=2,
        s_rule=s_rule,
        passed_rules=True,
    )
    judgement = Judgement(
        matched_person_id=matched,
        s_llm=s_llm,
        reason="비밀이 아니라도 덤프에 넣지 않는 자유 서술",
        tokens_in=11,
        tokens_out=7,
        model="stub-judge",
        provider="stub",
    )
    decision = decide(
        judgement=judgement, passed=[candidate], llm_failed=False, config=config
    )
    resolution = Resolution(
        trace_id=None,
        mention=mention,
        candidates=[candidate],
        matched_person_id=decision.matched_person_id,
        confidence=decision.confidence,
        confidence_breakdown=decision.confidence_breakdown,
        band=decision.band,
        band_by_threshold=decision.band_by_threshold,
        forced_reason=decision.forced_reason,
        decision=dict(decision.decision),
        llm={
            "provider": "stub",
            "model": "stub-judge",
            "self_reported": True,
            "s_llm": s_llm,
            "reason": judgement.reason,
            "tokens_in": 11,
            "tokens_out": 7,
            "attempts": 1,
            "skipped": False,
            "error": None,
        },
    )
    return json.loads(json.dumps(resolution.to_dict(), ensure_ascii=False))


def _row(trace_id: int, *, mention: str = "김팀장", t_merge: float = 0.8) -> dict[str, Any]:
    return {
        "method": "proposed",
        "mention": mention,
        "decision": "merge",
        "person_id": 7,
        "score": 0.8,
        "trace_id": trace_id,
        "scenario_id": "sc-001",
        "mention_index": 0,
        "mention_kind": "gold",
        "turn": 0,
        "gold_person_id": "p1",
        "t_merge": t_merge,
        "t_new": T_NEW,
        "sweep_index": 0,
        "llm_fresh_call": True,
    }


def _dump(tmp_path: Path, count: int = 3) -> tuple[Path, _FakeSession, int]:
    """제안 방식 행 `count` 개를 덤프해 파일 경로·세션·줄 수를 돌려준다."""

    session_id = "pilot-run-abc-sc-001"
    traces = [
        _FakeTrace(100 + i, session_id, _resolution_output(s_llm=0.5 + 0.05 * i))
        for i in range(count)
    ]
    rows: list[dict[str, Any]] = [
        _row(100 + i, t_merge=T_MERGE_GRID[i]) for i in range(count)
    ]
    # 다른 방식 행은 섞여 있어도 덤프 대상이 아니다.
    rows.append({**_row(999), "method": "embedding_only", "trace_id": None})
    session = _FakeSession(traces)
    path = tmp_path / "traces-20260101-000000.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        written = cli.dump_er_traces(
            session, rows, handle, session_id=session_id, scenario_id="sc-001"
        )
    return path, session, written


def test_dump_writes_one_line_per_proposed_row(tmp_path: Path) -> None:
    path, session, written = _dump(tmp_path, count=3)
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert written == 3
    assert len(lines) == 3
    entries = [json.loads(line) for line in lines]
    assert [e["trace_id"] for e in entries] == [100, 101, 102]
    assert {e["step"] for e in entries} == {"er_resolve"}
    assert {e["tool_name"] for e in entries} == {"er"}
    assert {e["method"] for e in entries} == {"proposed"}
    assert [e["t_merge"] for e in entries] == list(T_MERGE_GRID[:3])
    # 조회 조건이 P3-er §7 계약 그대로인가
    params = session.statements[0].compile().params
    assert params["step_1"] == "er_resolve"
    assert params["tool_name_1"] == "er"
    assert params["session_id_1"] == "pilot-run-abc-sc-001"


def test_dump_entry_carries_recompute_inputs_and_no_prompt(tmp_path: Path) -> None:
    path, _, _ = _dump(tmp_path, count=1)
    entry = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    breakdown = entry["confidence_breakdown"]
    assert set(breakdown) >= {"s_llm", "s_emb", "s_rule", "weights", "confidence"}
    assert entry["decision"]["T_merge"] == 0.8
    assert entry["decision"]["T_new"] == T_NEW
    assert entry["llm"]["provider"] == "stub"
    # 후보 전체가 아니라 귀속 후보 1개만(원시 JSONL 과 이중 출처 금지)
    assert entry["candidate_count"] == 1
    assert entry["matched_candidate"]["person_id"] == breakdown["matched_person_id"]
    assert entry["matched_candidate"]["s_emb"] == breakdown["s_emb"]
    # 프롬프트 원문·LLM 자유 서술은 옮기지 않는다(security §1)
    blob = json.dumps(entry, ensure_ascii=False)
    assert "reason" not in entry["llm"]
    assert "자유 서술" not in blob  # Judgement.reason 원문
    assert "prompt" not in blob
    assert '"reason"' not in blob  # forced_reason 은 있어도 reason 키는 없다


def test_dump_fails_when_proposed_row_has_no_trace_id(tmp_path: Path) -> None:
    session = _FakeSession([])
    rows = [{**_row(1), "trace_id": None}]
    with (tmp_path / "t.jsonl").open("w", encoding="utf-8") as handle:
        with pytest.raises(cli.TraceDumpError) as exc:
            cli.dump_er_traces(
                session, rows, handle, session_id="s", scenario_id="sc-001"
            )
    assert "trace_id" in str(exc.value)


def test_dump_fails_when_trace_row_is_absent(tmp_path: Path) -> None:
    session = _FakeSession([])  # 롤백 뒤처럼 조회되지 않는 상태
    with (tmp_path / "t.jsonl").open("w", encoding="utf-8") as handle:
        with pytest.raises(cli.TraceDumpError) as exc:
            cli.dump_er_traces(
                session, [_row(100)], handle, session_id="s", scenario_id="sc-001"
            )
    assert "er_resolve" in str(exc.value)


def test_dump_fails_when_trace_mention_differs(tmp_path: Path) -> None:
    session = _FakeSession([_FakeTrace(100, "s", _resolution_output(mention="박대리"))])
    with (tmp_path / "t.jsonl").open("w", encoding="utf-8") as handle:
        with pytest.raises(cli.TraceDumpError) as exc:
            cli.dump_er_traces(
                session, [_row(100)], handle, session_id="s", scenario_id="sc-001"
            )
    assert "mention" in str(exc.value)


def test_recheck_of_untouched_dump_has_zero_diff(tmp_path: Path) -> None:
    path, _, written = _dump(tmp_path, count=3)
    result = cli.recheck_trace_dump(path)
    assert result.dumped == written == 3
    assert result.recomputed == 3
    assert result.max_abs_diff == 0.0
    assert result.failures == []
    assert result.ok


def test_recheck_cli_prints_summary_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path, _, _ = _dump(tmp_path, count=2)
    rc = cli.main(["--recheck-traces", str(path)])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK
    assert "[traces] dumped=2 recomputed=2 max_abs_diff=0.0" in out
    assert str(path) in out


def _rewrite(path: Path, mutate: Any) -> None:
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    mutate(entries)
    path.write_text(
        "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in entries),
        encoding="utf-8",
        newline="\n",
    )


def test_recheck_detects_tampered_confidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path, _, _ = _dump(tmp_path, count=3)

    def bump(entries: list[dict[str, Any]]) -> None:
        entries[1]["confidence_breakdown"]["confidence"] += 1e-12

    _rewrite(path, bump)
    result = cli.recheck_trace_dump(path)
    assert result.max_abs_diff > 0.0
    assert len(result.failures) == 1
    assert "trace_id=101" in result.failures[0]
    assert cli.main(["--recheck-traces", str(path)]) == cli.RC_ERROR
    assert "[fail] traces:" in capsys.readouterr().out


def test_recheck_detects_tampered_signal(tmp_path: Path) -> None:
    path, _, _ = _dump(tmp_path, count=2)

    def bump(entries: list[dict[str, Any]]) -> None:
        entries[0]["confidence_breakdown"]["s_emb"] = 0.1

    _rewrite(path, bump)
    result = cli.recheck_trace_dump(path)
    assert not result.ok
    assert "trace_id=100" in result.failures[0]
    # 귀속 후보의 값과 어긋난 것이 먼저 잡힌다(원칙9)
    assert "귀속 후보" in result.failures[0]


def test_recheck_detects_s_llm_out_of_step_with_llm_block(tmp_path: Path) -> None:
    """강제 경로가 아닌데 `s_llm` 이 `llm.s_llm` 과 다르면 기록이 깨진 것."""

    path, _, _ = _dump(tmp_path, count=1)

    def bump(entries: list[dict[str, Any]]) -> None:
        entries[0]["confidence_breakdown"]["s_llm"] = 0.99

    _rewrite(path, bump)
    result = cli.recheck_trace_dump(path)
    assert not result.ok
    assert "llm.s_llm" in result.failures[0]


def test_recheck_detects_signal_tampered_together_with_candidate(tmp_path: Path) -> None:
    """후보까지 같이 고쳐도 가중합이 맞지 않으면 잡힌다(부정 케이스)."""

    path, _, _ = _dump(tmp_path, count=1)

    def bump(entries: list[dict[str, Any]]) -> None:
        entries[0]["confidence_breakdown"]["s_emb"] = 0.1
        entries[0]["matched_candidate"]["s_emb"] = 0.1

    _rewrite(path, bump)
    result = cli.recheck_trace_dump(path)
    assert not result.ok
    assert result.recomputed == 1
    assert result.max_abs_diff > 0.0
    assert "abs diff=" in result.failures[0]


def test_recheck_rejects_weights_other_than_product_constant(tmp_path: Path) -> None:
    path, _, _ = _dump(tmp_path, count=1)

    def swap(entries: list[dict[str, Any]]) -> None:
        entries[0]["confidence_breakdown"]["weights"] = {
            "llm": 0.4,
            "emb": 0.4,
            "rule": 0.2,
        }

    _rewrite(path, swap)
    result = cli.recheck_trace_dump(path)
    assert not result.ok
    assert "ER_WEIGHTS" in result.failures[0]
    assert result.recomputed == 0


def test_recheck_rejects_missing_fields_and_empty_file(tmp_path: Path) -> None:
    path, _, _ = _dump(tmp_path, count=1)

    def drop(entries: list[dict[str, Any]]) -> None:
        del entries[0]["confidence_breakdown"]["s_llm"]

    _rewrite(path, drop)
    assert not cli.recheck_trace_dump(path).ok

    empty = tmp_path / "traces-empty.jsonl"
    empty.write_text("", encoding="utf-8")
    result = cli.recheck_trace_dump(empty)
    assert result.dumped == 0
    assert not result.ok
    assert cli.main(["--recheck-traces", str(empty)]) == cli.RC_ERROR


def test_recheck_missing_path_returns_error(tmp_path: Path) -> None:
    assert cli.main(["--recheck-traces", str(tmp_path / "없다.jsonl")]) == cli.RC_ERROR


def test_recompute_uses_product_combine_not_a_local_formula() -> None:
    """가중치·산식의 출처가 제품 코드인가(하드코딩 금지)."""

    source = Path(cli.__file__).read_text(encoding="utf-8")
    assert "from app.er.confidence import combine" in source
    assert "from app.settings import ER_WEIGHTS" in source
    assert "0.5 *" not in source and "0.3 *" not in source

    from app.er.confidence import combine
    from app.er.types import ERConfig

    config = ERConfig(t_merge=0.8, t_new=T_NEW)
    breakdown = {
        "s_llm": 0.73,
        "s_emb": 0.8123456789,
        "s_rule": 0.6666666666666666,
        "weights": {"llm": config.w_llm, "emb": config.w_emb, "rule": config.w_rule},
    }
    assert cli.recompute_confidence(breakdown) == combine(
        0.73, 0.8123456789, 0.6666666666666666, config
    )


def test_forced_path_breakdown_recomputes_to_zero(tmp_path: Path) -> None:
    """강제 강등 경로(세 신호 0·confidence 0)도 같은 기준으로 통과한다."""

    from app.er.confidence import decide
    from app.er.types import ERConfig, ScoredCandidate

    config = ERConfig(t_merge=0.8, t_new=T_NEW)
    candidate = ScoredCandidate(person_id=7, display_name="김도윤", passed_rules=True)
    decision = decide(judgement=None, passed=[candidate], llm_failed=True, config=config)
    entry = {
        "confidence_breakdown": decision.confidence_breakdown,
        "matched_candidate": cli._matched_candidate([], None),
    }
    assert entry["matched_candidate"] is None  # 강제 경로는 귀속 후보가 없다
    assert cli.check_trace_entry(entry) == 0.0


def test_traces_per_scenario_zero_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        cli.main(
            [
                "--dry-run",
                "--stub",
                "--traces-per-scenario",
                "0",
                "--out",
                str(tmp_path / "o"),
            ]
        )


# ---------------------------------------------------------------------------
# 커밋용 gzip · 크기 가드 (순수 -- DB·네트워크 0)
# ---------------------------------------------------------------------------


def _jsonl(tmp_path: Path, name: str = "raw.jsonl", lines: int = 50) -> Path:
    path = tmp_path / name
    path.write_text(
        "".join(
            json.dumps({"i": i, "mention": "김팀장"}, ensure_ascii=False) + "\n"
            for i in range(lines)
        ),
        encoding="utf-8",
    )
    return path


def test_gzip_is_byte_identical_across_runs(tmp_path: Path) -> None:
    """같은 입력 → 같은 바이트(원칙8). gzip 헤더의 기본 mtime·파일명이
    실행마다 달라지는 것을 막았는지 본다."""

    import gzip as gzip_mod

    src = _jsonl(tmp_path)
    first, digest_a = cli.gzip_jsonl(src, tmp_path / "a.jsonl.gz")
    second, digest_b = cli.gzip_jsonl(src, tmp_path / "b.jsonl.gz")
    assert first.read_bytes() == second.read_bytes()
    assert digest_a == digest_b
    header = first.read_bytes()[:10]
    assert header[3] & 0x08 == 0  # FNAME 플래그 없음(원본 파일명 미기록)
    assert header[4:8] == b"\x00\x00\x00\x00"  # mtime=0
    with gzip_mod.open(first, "rt", encoding="utf-8") as handle:
        assert handle.read() == src.read_text(encoding="utf-8")


def test_gzip_default_name_and_plain_is_kept(tmp_path: Path) -> None:
    src = _jsonl(tmp_path)
    packed, digest = cli.gzip_jsonl(src)
    assert packed == tmp_path / "raw.jsonl.gz"
    assert src.exists()  # 기본은 평문 보존
    assert digest == hashlib.sha256(src.read_bytes()).hexdigest()


def test_gzip_drop_plain_removes_source_after_verification(tmp_path: Path) -> None:
    src = _jsonl(tmp_path)
    packed, _ = cli.gzip_jsonl(src, drop_plain=True)
    assert packed.exists()
    assert not src.exists()


def test_gzip_missing_source_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(cli.GzipError, match="원본이 없다"):
        cli.gzip_jsonl(tmp_path / "nope.jsonl")


def test_gzip_output_is_read_by_the_shared_loader(tmp_path: Path) -> None:
    """압축본을 여는 로직은 `evaluation.metrics` 한 곳뿐이다(중복 구현 금지)."""

    from evaluation.metrics import load_rows

    src = _jsonl(tmp_path, lines=3)
    packed, _ = cli.gzip_jsonl(src)
    assert load_rows(packed) == load_rows(src)


def test_commit_size_limit_matches_the_hook(tmp_path: Path) -> None:
    """상수 하나가 `.githooks/pre-commit` 의 한도와 같은 값인가(훅은 안 고친다)."""

    hook = (REPO_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert str(cli.COMMIT_SIZE_LIMIT_BYTES) in hook
    assert cli.COMMIT_SIZE_LIMIT_BYTES == 5 * 1024 * 1024


def test_format_commit_sizes_warns_only_over_the_limit(tmp_path: Path) -> None:
    small = tmp_path / "small.gz"
    small.write_bytes(b"0" * 10)
    big = tmp_path / "big.jsonl"
    big.write_bytes(b"0" * 64)
    lines = cli.format_commit_sizes([small, big, tmp_path / "gone"], limit=32)
    joined = "\n".join(lines)
    assert f"[size] {small} 10 bytes limit=32 ok" in joined
    assert f"[size] {big} 64 bytes limit=32 OVER" in joined
    assert f"[size] {tmp_path / 'gone'} (없음)" in joined
    warns = [line for line in lines if line.startswith("[warn]")]
    assert len(warns) == 1 and str(big) in warns[0]
    assert not [line for line in lines if line.startswith("[fail]")]  # rc 규약 불변


def test_recheck_traces_accepts_a_gzipped_dump(tmp_path: Path) -> None:
    path, _, written = _dump(tmp_path, count=3)
    packed, _ = cli.gzip_jsonl(path, drop_plain=True)
    result = cli.recheck_trace_dump(packed)
    assert result.ok and result.dumped == result.recomputed == written
    assert cli.main(["--recheck-traces", str(packed)]) == cli.RC_OK


def test_recheck_traces_rejects_a_broken_gzip(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = tmp_path / "traces.jsonl.gz"
    broken.write_bytes(b"\x1f\x8b garbage garbage")
    rc = cli.main(["--recheck-traces", str(broken)])
    out = capsys.readouterr().out
    assert rc == cli.RC_ERROR
    assert "gzip 읽기 실패" in out


# ---------------------------------------------------------------------------
# CLI 인자 조합 · 가드 (실행하지 않는다)
# ---------------------------------------------------------------------------


def test_stub_requires_dry_run(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--stub", "--out", str(tmp_path)])
    assert exc.value.code == 2  # argparse 사용법 오류


def test_dry_run_requires_stub(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--dry-run", "--out", str(tmp_path)])
    assert exc.value.code == 2


def test_cost_guard_stops_before_running(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(
        [
            "--dry-run",
            "--stub",
            "--limit",
            "1",
            "--max-cost-usd",
            "0.0001",
            "--out",
            str(tmp_path / "out"),
        ]
    )
    out = capsys.readouterr().out
    assert rc == cli.RC_COST_LIMIT == 3
    assert "[estimate] cost_usd total=" in out
    assert "상한" in out
    assert not (tmp_path / "out").exists()
    assert "[stage]" not in out


def test_estimate_only_does_not_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["--dry-run", "--stub", "--limit", "1", "--estimate-only"])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK
    assert "[stage]" not in out
    assert "--estimate-only" in out


def test_real_mode_without_keys_returns_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name in cli.REQUIRED_REAL_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "CANARY-VALUE")
    rc = cli.main(["--limit", "1", "--out", str(tmp_path / "real")])
    out = capsys.readouterr().out
    assert rc == cli.RC_MISSING_KEYS == 2
    assert "OPENAI_API_KEY" in out
    assert "CANARY-VALUE" not in out  # 값은 찍지 않는다(이름만)
    assert "[stage]" not in out
    assert not (tmp_path / "real").exists()


def _reports_snapshot() -> dict[str, tuple[int, int]]:
    """`reports/` 아래 모든 파일의 (크기, mtime_ns). dry-run 전후 비교용 -- U7 이후 `reports/`
    에는 실 실행 산출물(결정 E)이 커밋되어 있으므로 "존재하지 않는다"가 아니라 "바뀌지 않았다"
    를 단언한다."""
    root = REPO_ROOT / "reports"
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_stub_output_cannot_land_in_reports(capsys: pytest.CaptureFixture[str]) -> None:
    before = _reports_snapshot()
    rc = cli.main(
        ["--dry-run", "--stub", "--limit", "1", "--out", str(REPO_ROOT / "reports" / "pilot")]
    )
    out = capsys.readouterr().out
    assert rc == cli.RC_ERROR
    assert "reports/" in out
    assert _reports_snapshot() == before  # 거부됐으므로 reports/ 에 새 파일도, 변경도 없다


# ---------------------------------------------------------------------------
# 사슬 층 (실 PostgreSQL · 네트워크 0)
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_chain_produces_all_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "out"
    rc = cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(out_dir)])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK

    raw = _raw_files(out_dir)
    assert len(raw) == 1
    for name in OUTPUT_NAMES:
        assert (out_dir / name).exists(), name

    assert "run_mode=stub" in out
    assert "network_calls=0" in out
    for stage in ("runner", "metrics", "calibration", "curve", "validate", "report"):
        assert f"[stage] {stage}" in out
    assert "rc=1" not in out

    rows = [json.loads(line) for line in raw[0].read_text(encoding="utf-8").splitlines() if line]
    methods = {row["method"] for row in rows}
    thresholds = {row["t_merge"] for row in rows}
    mentions = {(row["scenario_id"], row["mention_index"], row["mention_kind"]) for row in rows}
    assert len(methods) == 5
    assert len(thresholds) == len(T_MERGE_GRID) == 10
    assert len(rows) == len(mentions) * 5 * 10
    assert {row["t_new"] for row in rows} == {T_NEW}


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_logs_embedded_alias_count_per_scenario(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK
    scenario_lines = [line for line in out.splitlines() if line.startswith("[scenario] ")]
    assert len(scenario_lines) == 2
    for line in scenario_lines:
        aliases = int(line.split("aliases=")[1].split()[0])
        embedded = int(line.split("embedded=")[1].split()[0])
        assert aliases == embedded
        assert line.endswith("ok")


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_dumps_traces_before_rollback_and_rechecks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """결정 D(i) 롤백 뒤에는 `agent_traces` 가 없으므로, 덤프가 실행 중에
    떠져 있어야 한다(01-plan 106·236행)."""

    out_dir = tmp_path / "out"
    rc = cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(out_dir)])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK

    raw = _raw_files(out_dir)[0]
    stamp = raw.name[len("raw-") : -len(".jsonl")]
    traces = out_dir / f"traces-{stamp}.jsonl"
    assert traces.exists()  # raw 와 같은 stamp

    rows = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines() if line]
    proposed = [row for row in rows if row["method"] == cli.TRACE_DUMP_METHOD]
    entries = [
        json.loads(line) for line in traces.read_text(encoding="utf-8").splitlines() if line
    ]
    assert len(entries) == len(proposed) > 0
    assert {e["trace_id"] for e in entries} == {row["trace_id"] for row in proposed}
    assert all(e["session_id"].startswith("pilot-run-") for e in entries)
    assert all(e["step"] == "er_resolve" and e["tool_name"] == "er" for e in entries)

    assert f"[traces] dumped={len(entries)} recomputed={len(entries)} max_abs_diff=0.0" in out
    assert f"path={traces}" in out
    assert "[fail]" not in out

    # 파일만 들고 다시 돌려도 같은 판정
    assert cli.main(["--recheck-traces", str(traces)]) == cli.RC_OK


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_traces_per_scenario_caps_the_dump(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rc = cli.main(
        [
            "--dry-run",
            "--stub",
            "--limit",
            "2",
            "--traces-per-scenario",
            "3",
            "--out",
            str(out_dir),
        ]
    )
    assert rc == cli.RC_OK
    raw = _raw_files(out_dir)[0]
    stamp = raw.name[len("raw-") : -len(".jsonl")]
    lines = [
        line
        for line in (out_dir / f"traces-{stamp}.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(lines) == 6  # 시나리오 2개 × 3줄


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_metrics_json_is_byte_identical(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"
    assert cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(first)]) == 0
    assert cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(second)]) == 0
    for name in OUTPUT_NAMES:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_commit_and_run_mode_land_in_meta(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rc = cli.main(
        [
            "--dry-run",
            "--stub",
            "--limit",
            "1",
            "--commit",
            "0123456789abcdef",
            "--out",
            str(out_dir),
        ]
    )
    assert rc == cli.RC_OK
    document = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    meta = document["meta"]
    assert meta["commit"] == "0123456789abcdef"
    assert meta["run_mode"] == "stub"
    assert meta["dataset_hash"] == cli.dataset_fingerprint(SCENARIO_DIR)
    assert meta["run_id"].startswith("run-")
    assert meta["embedding_model"] == cli.STUB_EMBEDDING_MODEL
    # 리포트는 같은 값을 본문에 적는다(U5 메타 표).
    body = (out_dir / "eval.md").read_text(encoding="utf-8")
    assert "0123456789abcdef" in body


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_chain_gzips_raw_and_feeds_the_gz_to_every_stage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """원시 JSONL 은 gzip 으로 커밋한다(사용자 결정 2026-09-21, 결정 E 유지).

    커밋되는 파일 하나만으로 지표가 나오는지를 실행이 매번 증명해야 하므로
    metrics·calibration·curve 는 **압축본 경로**를 받는다(원칙8).
    """

    from evaluation.metrics import load_rows

    out_dir = tmp_path / "out"
    rc = cli.main(["--dry-run", "--stub", "--limit", "2", "--out", str(out_dir)])
    out = capsys.readouterr().out
    assert rc == cli.RC_OK

    raw = _raw_files(out_dir)[0]  # 평문은 기본 보존
    packed = Path(str(raw) + ".gz")
    assert packed.exists()
    assert load_rows(packed) == load_rows(raw)

    assert f"[gzip] {packed}" in out
    assert "roundtrip_sha256=" in out and "plain=보존" in out
    for stage in ("metrics", "calibration", "curve"):
        line = next(l for l in out.splitlines() if l.startswith(f"[stage] {stage}: python -m"))
        assert f"--rows {packed}" in line
        assert f"--rows {raw} " not in line

    # 커밋 대상 크기 줄(한도는 훅과 같은 상수)
    stamp = raw.name[len("raw-") : -len(".jsonl")]
    traces = out_dir / f"traces-{stamp}.jsonl"
    for path in (packed, traces):
        assert f"[size] {path} {path.stat().st_size} bytes limit={cli.COMMIT_SIZE_LIMIT_BYTES}" in out
    assert "[fail]" not in out


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_chain_drop_raw_plain_leaves_only_the_gz(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "out"
    rc = cli.main(
        ["--dry-run", "--stub", "--limit", "1", "--drop-raw-plain", "--out", str(out_dir)]
    )
    out = capsys.readouterr().out
    assert rc == cli.RC_OK
    assert _raw_files(out_dir) == []  # 평문 없음
    assert len(sorted(out_dir.glob("raw-*.jsonl.gz"))) == 1
    assert "plain=삭제" in out
    for name in OUTPUT_NAMES:
        assert (out_dir / name).exists(), name


@pytest.mark.usefixtures("db_engine", "no_provider_factories")
def test_dry_run_leaves_no_rows_and_no_reports_files(tmp_path: Path) -> None:
    from sqlalchemy import func, select

    from app.db.models import Person
    from app.db.session import get_engine

    engine = get_engine()
    with engine.connect() as connection:
        before = connection.execute(select(func.count()).select_from(Person)).scalar_one()
    reports_before = _reports_snapshot()
    assert cli.main(["--dry-run", "--stub", "--limit", "1", "--out", str(tmp_path / "o")]) == 0
    with engine.connect() as connection:
        after = connection.execute(select(func.count()).select_from(Person)).scalar_one()
    assert after == before  # 결정 D(i) 롤백 -- 평가는 아무것도 커밋하지 않는다
    assert _reports_snapshot() == reports_before  # --out 이 tmp 이므로 reports/ 는 그대로
