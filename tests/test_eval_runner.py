"""Refs: P4-pilot-eval S3.7 D5 D10 원칙8 원칙9 -- U1 러너 골격·격리·적재 테스트.

01-plan 64행이 요구하는 네 단언:

1. 같은 시나리오를 **2회** 돌린 뒤 `persons`/`person_aliases` 행 수 증분 0
   (인계 9 "두 벌" 방지, 결정 D(i) 세이브포인트 롤백).
2. `hints` 인자가 **전 방식에서 `None`**(호출 스파이).
3. 스윕 격자 길이 = 10(`T_MERGE_GRID`, 그리고 JSONL 에서 mention × 방식마다 10행).
4. `embedder=None` 이면 **즉시 실패**(경고가 아니라 오류, DB·파일 접근 전).

그 밖에 결정 C(i)(LLM mention 당 1회)·02-plan-verify R-5(`embedding_only`
동점 강등이 모든 임계치에서 유지)·R-7(2)(`0.8` 정확 표현)·인계 1(러너 env)·
trace_id 가 실행 중 `er_resolve` 행으로 조회된다는 것과 부정 케이스를 본다.

실 PostgreSQL(로컬 5433) + 롤백 픽스처, 가짜 임베딩(`fake_embedder`·
`grouped_embedder`), `FakeJudge`·스텁 caller. 네트워크·실 키 0.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.models import AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.judge import FakeJudge
from app.er.types import ER_TRACE_STEP
from app.tools.context import ToolContext
from evaluation import runner as runner_mod
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.llm_single import SingleCallResult
from evaluation.runner import (
    ROW_EXTRA_KEYS,
    T_MERGE_GRID,
    T_NEW,
    RunnerError,
    build_runner_env,
    run_pilot,
)
from evaluation.scenario_state import load_scenarios

ALL_METHODS: tuple[str, ...] = resolver_registry.ALL_METHODS
USER_ID = "runner-test-user"
SCENARIOS: dict[str, dict[str, Any]] = {sc["id"]: sc for _, sc in load_scenarios()}

#: 라벨에 있는 문자열만(지어낸 별칭 없음) -- 같은 그룹끼리 코사인 ≈0.85.
EMBED_GROUPS: dict[str, list[str]] = {
    "sc-025-p1": ["엄마", "울엄마"],
    "sc-001-p1": ["김팀장", "팀장님", "김부장님", "부장님"],
    "sc-038-p1": ["다인", "다인이"],
}

TO_DICT_KEYS = {
    "method",
    "mention",
    "decision",
    "person_id",
    "score",
    "candidates",
    "trace_id",
    "tokens_in",
    "tokens_out",
    "detail",
}


# ---------------------------------------------------------------------------
# 스텁 · 계수기 (네트워크 0)
# ---------------------------------------------------------------------------


class CountingJudge:
    """`FakeJudge` 를 감싸 실제 판정 호출 수를 센다."""

    def __init__(self, inner: FakeJudge) -> None:
        self._inner = inner
        self.calls = 0

    def judge(self, mention: str, utterance: str, candidates: list[Any]) -> Any:
        self.calls += 1
        return self._inner.judge(mention, utterance, candidates)


class HighestJudge:
    """통과 후보 중 첫 후보를 `s_llm` 0.9 로 고르는 결정적 판정기
    (인물 id 를 미리 몰라도 된다 -- 적재 전에 만들어진다)."""

    def __init__(self) -> None:
        self.calls = 0

    def judge(self, mention: str, utterance: str, candidates: list[Any]) -> Any:
        self.calls += 1
        table = {c.person_id: 0.9 for c in candidates}
        return FakeJudge(table=table, pick=candidates[0].person_id).judge(
            mention, utterance, candidates
        )


class StubCaller:
    """`SingleCaller` 모양 스텁 -- 항상 `new_person`."""

    provider = "openai"
    model = "stub-model"

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, system: str, user_text: str) -> SingleCallResult:
        self.calls += 1
        return SingleCallResult(
            raw={
                "decision": "new_person",
                "matched_person_id": None,
                "s_llm": 0.2,
                "reason": "stub",
                "candidate_person_ids": [],
            },
            tokens_in=11,
            tokens_out=3,
            model="stub-model",
            provider="openai",
        )


class CountingEmbedder:
    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.calls = 0
        self.texts: list[str] = []

    def __call__(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        self.texts.extend(texts)
        return self._inner(texts)


def _counts(session: Any, user_id: str = USER_ID) -> dict[str, int]:
    person_ids = select(Person.id).where(Person.user_id == user_id)
    return {
        "persons": session.execute(
            select(func.count()).select_from(Person).where(Person.user_id == user_id)
        ).scalar_one(),
        "person_aliases": session.execute(
            select(func.count())
            .select_from(PersonAlias)
            .where(PersonAlias.person_id.in_(person_ids))
        ).scalar_one(),
        "pending_questions": session.execute(
            select(func.count()).select_from(PendingQuestion)
        ).scalar_one(),
        "agent_traces": session.execute(
            select(func.count()).select_from(AgentTrace)
        ).scalar_one(),
    }


def _read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _mention_total(scenario: dict[str, Any]) -> int:
    return len(scenario.get("mentions") or []) + len(scenario.get("passing_mentions") or [])


@pytest.fixture()
def harness(db_session, grouped_embedder):
    """`run_pilot` 공통 인자. `ctx_factory` 호출 수를 센다."""

    embedder = CountingEmbedder(grouped_embedder(EMBED_GROUPS))
    judge = HighestJudge()
    caller = StubCaller()
    factory_calls: list[str] = []

    def ctx_factory(scenario_id: str) -> ToolContext:
        factory_calls.append(scenario_id)
        return ToolContext(
            session=db_session,
            session_id=f"runner-{scenario_id}",
            user_id=USER_ID,
        )

    def run(scenario_ids, out_path, *, methods=ALL_METHODS, grid=T_MERGE_GRID, **kw):
        kw.setdefault("judge", judge)
        kw.setdefault("resolver_kwargs", {"llm_single": {"caller": caller}})
        return run_pilot(
            ctx_factory,
            [SCENARIOS[s] for s in scenario_ids],
            methods,
            grid,
            embedder=kw.pop("embedder", embedder),
            out_path=out_path,
            **kw,
        )

    class H:
        pass

    h = H()
    h.session = db_session
    h.embedder = embedder
    h.judge = judge
    h.caller = caller
    h.factory_calls = factory_calls
    h.ctx_factory = ctx_factory
    h.run = run
    return h


# ---------------------------------------------------------------------------
# 순수 층
# ---------------------------------------------------------------------------


def test_grid_is_ten_points_and_t_new_fixed() -> None:
    assert len(T_MERGE_GRID) == 10
    assert T_MERGE_GRID == (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95)
    assert 0.8 in T_MERGE_GRID  # R-7(2): 0.8000000000000002 가 아니다
    assert T_NEW == 0.3


def test_runner_env_forces_openai_and_drops_enabled_switch(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_PROVIDERS_ENABLED", "anthropic")
    env = build_runner_env()
    assert env["LLM_PROVIDER"] == "openai"
    assert "LLM_PROVIDERS_ENABLED" not in env
    # os.environ 은 바꾸지 않는다.
    assert os.environ["LLM_PROVIDER"] == "anthropic"
    assert os.environ["LLM_PROVIDERS_ENABLED"] == "anthropic"
    env2 = build_runner_env({"LLM_PROVIDERS_ENABLED": "gemini", "X": "1"})
    assert env2 == {"LLM_PROVIDER": "openai", "X": "1"}


def test_embedder_none_fails_immediately(tmp_path) -> None:
    called: list[str] = []

    def ctx_factory(scenario_id: str) -> ToolContext:  # pragma: no cover -- 불리면 실패
        called.append(scenario_id)
        raise AssertionError("ctx_factory must not be called")

    out = tmp_path / "raw.jsonl"
    with pytest.raises(RunnerError, match="embedder is required"):
        run_pilot(
            ctx_factory,
            [SCENARIOS["sc-025"]],
            ALL_METHODS,
            T_MERGE_GRID,
            embedder=None,
            out_path=out,
        )
    assert called == []
    assert not out.exists()


@pytest.mark.parametrize(
    "grid, message",
    [
        ([], "empty"),
        ([0.5, 0.5], "duplicate"),
        ([0.8000001], "lattice"),
        ([0.2], "outside"),
        ([1.05], "outside"),
    ],
)
def test_bad_grid_rejected_before_db(tmp_path, fake_embedder, grid, message) -> None:
    def ctx_factory(scenario_id: str) -> ToolContext:  # pragma: no cover
        raise AssertionError("ctx_factory must not be called")

    with pytest.raises(ValueError, match=message):
        run_pilot(
            ctx_factory,
            [SCENARIOS["sc-025"]],
            ALL_METHODS,
            grid,
            embedder=fake_embedder,
            out_path=tmp_path / "raw.jsonl",
        )


def test_grid_float_noise_normalized(tmp_path, fake_embedder, monkeypatch) -> None:
    """`0.5+0.05*7`(=0.8500000000000001)처럼 부동소수 잡음이 낀 값은 0.01
    격자로 접힌다."""

    captured: dict[str, Any] = {}

    def fake_run_scenario(ctx, scenario, state, names, resolvers, memos, grid, configs):
        captured["grid"] = grid
        captured["t_merge"] = [c.t_merge for c in configs]
        captured["t_new"] = {c.t_new for c in configs}
        return []

    monkeypatch.setattr(runner_mod, "_run_scenario", fake_run_scenario)
    monkeypatch.setattr(
        runner_mod, "load_scenario_state", lambda ctx, sc, embedder: _FakeState()
    )
    monkeypatch.setattr(runner_mod, "_state_counts", lambda ctx: {})

    noisy = [0.5 + 0.05 * i for i in range(10)]
    assert any(n != round(n, 2) for n in noisy)  # 잡음이 실제로 있다
    run_pilot(
        lambda sid: ToolContext(session=_NullSession(), session_id="x", user_id="u"),
        [SCENARIOS["sc-025"]],
        ["exact_raw"],
        noisy,
        embedder=fake_embedder,
        out_path=tmp_path / "raw.jsonl",
    )
    assert captured["grid"] == T_MERGE_GRID
    assert captured["t_merge"] == list(T_MERGE_GRID)
    assert captured["t_new"] == {0.3}


class _FakeState:
    alias_count = 0
    embedded_alias_count = 0
    person_id_map: dict[str, int] = {}


class _NullSavepoint:
    is_active = True

    def rollback(self) -> None:
        self.is_active = False


class _NullSession:
    def begin_nested(self) -> _NullSavepoint:
        return _NullSavepoint()


@pytest.mark.parametrize(
    "methods, exc",
    [([], ValueError), (["exact_raw", "exact_raw"], ValueError), (["no_such"], KeyError)],
)
def test_bad_methods_rejected(tmp_path, fake_embedder, methods, exc) -> None:
    with pytest.raises(exc):
        run_pilot(
            lambda sid: (_ for _ in ()).throw(AssertionError("no ctx")),
            [SCENARIOS["sc-025"]],
            methods,
            T_MERGE_GRID,
            embedder=fake_embedder,
            out_path=tmp_path / "raw.jsonl",
        )


def test_existing_out_path_not_overwritten(tmp_path, fake_embedder) -> None:
    out = tmp_path / "raw.jsonl"
    out.write_text("keep\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        run_pilot(
            lambda sid: (_ for _ in ()).throw(AssertionError("no ctx")),
            [SCENARIOS["sc-025"]],
            ALL_METHODS,
            T_MERGE_GRID,
            embedder=fake_embedder,
            out_path=out,
        )
    assert out.read_text(encoding="utf-8") == "keep\n"


def test_empty_or_duplicate_scenarios_rejected(tmp_path, fake_embedder) -> None:
    for scenarios in ([], [SCENARIOS["sc-025"], SCENARIOS["sc-025"]]):
        with pytest.raises(ValueError):
            run_pilot(
                lambda sid: (_ for _ in ()).throw(AssertionError("no ctx")),
                scenarios,
                ALL_METHODS,
                T_MERGE_GRID,
                embedder=fake_embedder,
                out_path=tmp_path / "raw.jsonl",
            )


def test_resolver_kwargs_for_unrun_method_rejected(tmp_path, fake_embedder) -> None:
    with pytest.raises(KeyError):
        run_pilot(
            lambda sid: (_ for _ in ()).throw(AssertionError("no ctx")),
            [SCENARIOS["sc-025"]],
            ["exact_raw"],
            T_MERGE_GRID,
            embedder=fake_embedder,
            out_path=tmp_path / "raw.jsonl",
            resolver_kwargs={"llm_single": {"caller": StubCaller()}},
        )


# ---------------------------------------------------------------------------
# DB 층 -- 01-plan 64행 필수 단언
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_same_scenario_twice_leaves_zero_increment(harness, tmp_path) -> None:
    """인계 9 -- 같은 시나리오 2회 실행 후 `persons`/`person_aliases` 증분 0
    (그리고 `pending_questions`·`agent_traces` 도 0)."""

    before = _counts(harness.session)
    first = harness.run(["sc-025"], tmp_path / "a.jsonl")
    second = harness.run(["sc-025"], tmp_path / "b.jsonl")
    after = _counts(harness.session)

    assert after == before
    assert after["persons"] - before["persons"] == 0
    assert after["person_aliases"] - before["person_aliases"] == 0

    # 실행 중에는 사전 상태가 실제로 있었다 -- 완전일치가 적재된 인물로 merge.
    for path, summary in ((tmp_path / "a.jsonl", first), (tmp_path / "b.jsonl", second)):
        rows = _read_rows(path)
        assert summary.row_count == len(rows) == _mention_total(SCENARIOS["sc-025"]) * 5 * 10
        exact = [r for r in rows if r["method"] == "exact_raw"]
        assert exact and all(r["decision"] == "merge" for r in exact)
        assert all(r["person_id"] == r["gold_db_person_id"] for r in exact)
        assert summary.alias_count == summary.embedded_alias_count == 2


@pytest.mark.dbtest
def test_hints_none_for_every_method(harness, tmp_path, monkeypatch) -> None:
    """전 방식에서 `hints` 가 `None`(호출 스파이)."""

    seen: list[tuple[str, Any]] = []
    real_get_resolver = runner_mod.get_resolver

    class Spy:
        def __init__(self, name: str, inner: Any) -> None:
            self.name = name
            self._inner = inner

        def resolve_mention(self, ctx, mention, utterance, hints=None, *, config=None):
            seen.append((self.name, hints))
            return self._inner.resolve_mention(ctx, mention, utterance, hints, config=config)

    def spy_get_resolver(name, /, **kwargs):
        return Spy(name, real_get_resolver(name, **kwargs))

    monkeypatch.setattr(runner_mod, "get_resolver", spy_get_resolver)
    harness.run(["sc-001"], tmp_path / "raw.jsonl")

    per_method = _mention_total(SCENARIOS["sc-001"]) * len(T_MERGE_GRID)
    assert {name for name, _ in seen} == set(ALL_METHODS)
    for name in ALL_METHODS:
        hints = [h for n, h in seen if n == name]
        assert len(hints) == per_method
        assert all(h is None for h in hints)


@pytest.mark.dbtest
def test_sweep_grid_length_ten_per_mention_and_method(harness, tmp_path) -> None:
    ids = ["sc-001", "sc-038"]
    summary = harness.run(ids, tmp_path / "raw.jsonl")
    rows = _read_rows(tmp_path / "raw.jsonl")

    groups: dict[tuple, list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["scenario_id"], row["mention_kind"], row["mention_index"], row["method"])
        groups.setdefault(key, []).append(row)

    expected_groups = sum(_mention_total(SCENARIOS[s]) for s in ids) * len(ALL_METHODS)
    assert len(groups) == expected_groups
    for group in groups.values():
        assert [r["t_merge"] for r in group] == list(T_MERGE_GRID)
        assert len(group) == 10
        assert [r["sweep_index"] for r in group] == list(range(10))
        assert {r["t_new"] for r in group} == {0.3}
    assert summary.t_merge_grid == T_MERGE_GRID
    assert summary.rows_by_method == {m: len(rows) // 5 for m in ALL_METHODS}


# ---------------------------------------------------------------------------
# 행 형태 · passing · trace
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_row_shape_and_passing_mentions(harness, tmp_path) -> None:
    harness.run(["sc-038"], tmp_path / "raw.jsonl")
    rows = _read_rows(tmp_path / "raw.jsonl")
    for row in rows:
        assert set(row) == TO_DICT_KEYS | set(ROW_EXTRA_KEYS)
        assert row["scenario_id"] == "sc-038"
        assert row["category"] == "new_person"
        assert row["expected_ask_user_allowed"] == ["none"]
        assert row["trap_kind"] == "passing_mention"
    passing = [r for r in rows if r["mention_kind"] == "passing"]
    gold = [r for r in rows if r["mention_kind"] == "gold"]
    assert {r["mention"] for r in passing} == {"남주 배우", "그 아이돌"}
    assert all(r["gold_person_id"] is None and r["gold_db_person_id"] is None for r in passing)
    assert {r["gold_person_id"] for r in gold} == {"p1"}
    assert all(isinstance(r["gold_db_person_id"], int) for r in gold)
    assert all(r["ambiguous"] is False for r in rows)


@pytest.mark.dbtest
def test_ambiguous_flag_carried(db_session, fake_embedder, tmp_path) -> None:
    ctx_factory = lambda sid: ToolContext(session=db_session, session_id="amb", user_id=USER_ID)  # noqa: E731
    run_pilot(
        ctx_factory,
        [SCENARIOS["sc-013"]],
        ["exact_raw"],
        [0.8],
        embedder=fake_embedder,
        out_path=tmp_path / "raw.jsonl",
    )
    rows = _read_rows(tmp_path / "raw.jsonl")
    amb = [r for r in rows if r["ambiguous"]]
    assert [(r["turn"], r["mention"], r["gold_person_id"]) for r in amb] == [(3, "걔", None)]


@pytest.mark.dbtest
def test_trace_id_resolves_to_er_resolve_during_run_only(harness, tmp_path) -> None:
    """제안 방식 `trace_id` 가 실행 중 `agent_traces WHERE step='er_resolve'`
    로 되짚히고(결정 D(i) -- 실행 중에 한함), 롤백 뒤에는 남지 않는다."""

    seen_trace_ids: list[int] = []
    found_steps: list[str] = []

    def before_rollback(ctx, state, rows):
        for row in rows:
            if row["method"] == "proposed":
                trace = ctx.session.get(AgentTrace, row["trace_id"])
                assert trace is not None
                found_steps.append(trace.step)
                seen_trace_ids.append(row["trace_id"])

    harness.run(["sc-001"], tmp_path / "raw.jsonl", before_rollback=before_rollback)
    assert seen_trace_ids and set(found_steps) == {ER_TRACE_STEP}
    # 임계치마다 자기 trace 를 가진다(같은 id 재사용 아님).
    assert len(set(seen_trace_ids)) == len(seen_trace_ids)
    harness.session.expire_all()
    remaining = harness.session.execute(
        select(func.count()).select_from(AgentTrace).where(AgentTrace.id.in_(seen_trace_ids))
    ).scalar_one()
    assert remaining == 0


# ---------------------------------------------------------------------------
# 결정 C(i) -- LLM mention 당 1회
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_llm_called_once_per_mention_across_grid(harness, tmp_path) -> None:
    summary = harness.run(["sc-001"], tmp_path / "raw.jsonl")
    rows = _read_rows(tmp_path / "raw.jsonl")
    n_mentions = _mention_total(SCENARIOS["sc-001"])

    assert harness.caller.calls == n_mentions
    assert summary.llm_calls_by_method["llm_single"] == n_mentions
    assert summary.llm_calls_by_method["proposed"] == harness.judge.calls
    assert 0 < harness.judge.calls <= n_mentions
    assert summary.llm_repeat_calls == 0
    for method in ("exact_raw", "exact_norm", "embedding_only"):
        assert summary.llm_calls_by_method[method] == 0

    fresh = [r for r in rows if r["llm_fresh_call"]]
    assert {r["sweep_index"] for r in fresh} == {0}
    assert len([r for r in fresh if r["method"] == "llm_single"]) == n_mentions
    assert summary.tokens_in_by_method["llm_single"] == 11 * n_mentions
    assert summary.tokens_out_by_method["llm_single"] == 3 * n_mentions

    # 같은 mention 의 10행은 같은 LLM 응답을 본다(s_llm 이 행마다 같다).
    by_group: dict[tuple, set] = {}
    for row in rows:
        if row["method"] == "proposed":
            key = (row["mention_index"],)
            s_llm = row["detail"]["confidence_breakdown"].get("s_llm")
            by_group.setdefault(key, set()).add(s_llm)
    assert all(len(v) == 1 for v in by_group.values())


@pytest.mark.dbtest
def test_llm_failure_is_memoized_not_retried(db_session, grouped_embedder, tmp_path) -> None:
    judge = CountingJudge(FakeJudge(fail="timeout"))
    ctx_factory = lambda sid: ToolContext(session=db_session, session_id="fail", user_id=USER_ID)  # noqa: E731
    run_pilot(
        ctx_factory,
        [SCENARIOS["sc-025"]],
        ["proposed"],
        T_MERGE_GRID,
        embedder=grouped_embedder(EMBED_GROUPS),
        judge=judge,
        out_path=tmp_path / "raw.jsonl",
    )
    rows = _read_rows(tmp_path / "raw.jsonl")
    assert judge.calls == _mention_total(SCENARIOS["sc-025"])
    assert len(rows) == judge.calls * 10
    assert {r["detail"]["llm_error"] for r in rows} == {"timeout"}
    assert {r["detail"]["forced_reason"] for r in rows} == {"llm_failed"}


@pytest.mark.dbtest
def test_embeddings_memoized_across_grid(harness, tmp_path) -> None:
    summary = harness.run(["sc-001"], tmp_path / "raw.jsonl")
    # 같은 문자열을 두 번 임베딩하지 않는다.
    assert len(harness.embedder.texts) == len(set(harness.embedder.texts))
    assert summary.embed_texts == len(harness.embedder.texts)


# ---------------------------------------------------------------------------
# 공급자 env (인계 1)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_default_judge_and_caller_use_runner_env(db_session, grouped_embedder, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_PROVIDERS_ENABLED", "anthropic")
    envs: dict[str, dict[str, str]] = {}
    caller = StubCaller()

    def spy_judge_from_env(env=None):
        envs["judge"] = dict(env)
        return HighestJudge()

    def spy_caller_from_env(env=None, *, client=None, **kw):
        envs["caller"] = dict(env)
        return caller

    monkeypatch.setattr(runner_mod, "judge_from_env", spy_judge_from_env)
    monkeypatch.setattr(runner_mod, "caller_from_env", spy_caller_from_env)
    ctx_factory = lambda sid: ToolContext(session=db_session, session_id="env", user_id=USER_ID)  # noqa: E731
    summary = run_pilot(
        ctx_factory,
        [SCENARIOS["sc-001"]],
        ["proposed", "llm_single"],
        [0.8],
        embedder=grouped_embedder(EMBED_GROUPS),
        out_path=tmp_path / "raw.jsonl",
    )
    assert set(envs) == {"judge", "caller"}
    for env in envs.values():
        assert env["LLM_PROVIDER"] == "openai"
        assert "LLM_PROVIDERS_ENABLED" not in env
    assert summary.llm_provider_env == "openai"
    assert summary.llm_providers_enabled_env is None
    assert os.environ["LLM_PROVIDER"] == "anthropic"  # 원본 불변
    assert caller.calls == _mention_total(SCENARIOS["sc-001"])


# ---------------------------------------------------------------------------
# R-5 -- embedding_only 동점 강등은 모든 임계치에서
# ---------------------------------------------------------------------------


TIE_SCENARIO: dict[str, Any] = {
    "id": "sc-tie-test",
    "category": "alias",
    "persons": [
        {"person_id": "p1", "display_name": "김민수", "relation_tag": "친구", "hierarchy": "동", "aliases": ["민수"]},
        {"person_id": "p2", "display_name": "박민수", "relation_tag": "직장", "hierarchy": "동", "aliases": ["민수"]},
    ],
    "seed_persons": ["p1", "p2"],
    "utterances": ["민수가 오늘 연락함"],
    "mentions": [{"turn": 0, "surface": "민수", "gold_person_id": "p1"}],
}


@pytest.mark.dbtest
def test_embedding_only_tie_never_merges_at_any_threshold(db_session, fake_embedder, tmp_path) -> None:
    ctx_factory = lambda sid: ToolContext(session=db_session, session_id="tie", user_id=USER_ID)  # noqa: E731
    run_pilot(
        ctx_factory,
        [TIE_SCENARIO],
        ["embedding_only"],
        T_MERGE_GRID,
        embedder=fake_embedder,
        out_path=tmp_path / "raw.jsonl",
    )
    rows = _read_rows(tmp_path / "raw.jsonl")
    assert len(rows) == 10
    assert all(r["decision"] != "merge" for r in rows)
    assert {r["detail"]["forced_reason"] for r in rows} == {"tie"}
    assert {r["detail"]["band_by_threshold"] for r in rows} == {"merge"}


# ---------------------------------------------------------------------------
# 부정 -- 적재 단언 · 공급자 혼용
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_embedded_alias_mismatch_stops_and_rolls_back(harness, tmp_path, monkeypatch) -> None:
    real = runner_mod.load_scenario_state

    def broken(ctx, scenario, *, embedder):
        from dataclasses import replace

        state = real(ctx, scenario, embedder=embedder)
        return replace(state, embedded_alias_count=state.alias_count - 1)

    monkeypatch.setattr(runner_mod, "load_scenario_state", broken)
    before = _counts(harness.session)
    with pytest.raises(RunnerError, match="embedded_alias_count"):
        harness.run(["sc-025"], tmp_path / "raw.jsonl")
    assert _counts(harness.session) == before
    assert _read_rows(tmp_path / "raw.jsonl") == []


@pytest.mark.dbtest
def test_ctx_with_different_embedder_rejected(db_session, fake_embedder, grouped_embedder, tmp_path) -> None:
    other = grouped_embedder(EMBED_GROUPS)
    ctx_factory = lambda sid: ToolContext(  # noqa: E731
        session=db_session, session_id="mix", user_id=USER_ID, embedder=other
    )
    before = _counts(db_session)
    with pytest.raises(RunnerError, match="different sources"):
        run_pilot(
            ctx_factory,
            [SCENARIOS["sc-025"]],
            ["exact_raw"],
            [0.8],
            embedder=fake_embedder,
            out_path=tmp_path / "raw.jsonl",
        )
    assert _counts(db_session) == before


@pytest.mark.dbtest
def test_exception_inside_scenario_rolls_back(harness, tmp_path) -> None:
    def boom(ctx, state, rows):
        raise RuntimeError("boom")

    before = _counts(harness.session)
    with pytest.raises(RuntimeError, match="boom"):
        harness.run(["sc-025"], tmp_path / "raw.jsonl", before_rollback=boom)
    assert _counts(harness.session) == before
