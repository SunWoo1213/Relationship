"""Refs: P3-baselines S3.3 D3 D10 원칙1 원칙9 -- U2 제안 방식 어댑터 테스트.

`evaluation/resolvers/proposed.py` 가 `app.er.resolve()` 의 `Resolution` 을
**그대로** `MentionDecision` 으로 옮기는지만 본다(어댑터는 판정에 개입하지
않는다 -- 개입하면 "제안 방식의 성능"이 어댑터의 성능이 되어 비교가 깨진다,
원칙8).

증명 방식: 같은 `ctx`·같은 `mention`·같은 `FakeJudge`·같은 `ERConfig` 로
**`resolve()` 를 직접 한 번** 부르고(기준값 `Resolution`) **어댑터를 한 번**
불러(변환 결과) 필드끼리 대조한다. `FakeJudge`(P3-er 결정9)와
`fake_embedder`(conftest, sha256 시드)가 둘 다 결정적이라 두 호출은 같은
판정을 낸다 -- 어댑터가 값을 바꿨다면 그 자리에서 드러난다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`),
가짜 임베딩(결정 H -- 네트워크 0·비용 0), 실 LLM 호출 0회.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.judge import FakeJudge
from app.er.pipeline import resolve as er_resolve
from app.er.types import ER_TRACE_STEP, ERConfig, Resolution, ScoredCandidate
from app.tools.context import ToolContext
from evaluation.resolvers import DECISIONS, MentionDecision, RESOLVERS, get_resolver
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.proposed import METHOD_NAME, ProposedResolver, to_mention_decision

CONFIG = ERConfig()


# --- 픽스처 헬퍼(tests/test_er_pipeline.py 의 관행 그대로) ----------------


def _make_person(
    db_session: Any,
    *,
    display_name: str,
    relation_tag: str = "직장",
    hierarchy: str = "동",
    user_id: str = "local",
) -> Person:
    person = Person(
        user_id=user_id,
        display_name=display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session: Any, person: Person, alias: str, embedding: list[float]) -> None:
    db_session.add(
        PersonAlias(
            person_id=person.id,
            alias=alias,
            source=ALIAS_SOURCES[0],
            embedding=embedding,
        )
    )
    db_session.flush()


def _ctx(db_session: Any, *, session_id: str, embedder: Any) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder)


def _row_counts(db_session: Any) -> tuple[int, int, int]:
    """부수효과 0(불변 규약 1)을 재는 세 테이블."""
    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    questions = db_session.execute(
        select(func.count()).select_from(PendingQuestion)
    ).scalar_one()
    return persons, aliases, questions


def _seed_team_lead(db_session: Any, fake_embedder: Any) -> Person:
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", fake_embedder(["팀장"])[0])
    return person


def _assert_faithful_transfer(
    decision: MentionDecision, reference: Resolution, mention: str
) -> None:
    """변환표(01-plan U2)를 한 곳에서 단언한다 -- 세 밴드 테스트가 공유한다.

    `trace_id` 만은 값이 다르다(기준값과 어댑터가 각자 `resolve()` 를 불러
    `agent_traces` 행을 하나씩 남기므로) -- 각 테스트가 따로 확인한다.
    """

    assert decision.method == METHOD_NAME
    assert decision.mention == mention
    assert decision.decision == reference.band
    assert decision.score == pytest.approx(reference.confidence)
    assert decision.tokens_in == reference.llm["tokens_in"]
    assert decision.tokens_out == reference.llm["tokens_out"]

    # candidates[] -- 배제 후보 포함 전체가 순서까지 그대로(원칙9).
    assert [c.person_id for c in decision.candidates] == [
        c.person_id for c in reference.candidates
    ]
    assert [c.display_name for c in decision.candidates] == [
        c.display_name for c in reference.candidates
    ]
    for got, expected in zip(decision.candidates, reference.candidates):
        assert got.signals["s_emb"] == pytest.approx(expected.s_emb)
        assert got.signals["s_rule"] == pytest.approx(expected.s_rule)
        assert got.signals["passed_rules"] == (1.0 if expected.passed_rules else 0.0)
        assert got.signals["rule_checked"] == float(expected.rule_checked)
        assert got.signals["rule_passed"] == float(expected.rule_passed)
        for flag, value in expected.rule_flags.items():
            assert got.signals[flag] == (1.0 if value else 0.0)

    detail = decision.detail
    assert detail["forced_reason"] == reference.forced_reason
    assert detail["relaxed_retry"] == reference.relaxed_retry
    assert detail["band_by_threshold"] == reference.band_by_threshold
    assert detail["provider"] == reference.llm["provider"]
    assert detail["model"] == reference.llm["model"]
    assert detail["llm_skipped"] == reference.llm["skipped"]
    assert detail["llm_error"] == reference.llm["error"]
    assert detail["llm_attempts"] == reference.llm["attempts"]
    assert detail["confidence_breakdown"] == reference.confidence_breakdown
    assert detail["excluded_by"] == {
        str(c.person_id): c.excluded_by
        for c in reference.candidates
        if c.excluded_by is not None
    }
    # 어댑터가 강등에 개입했다면 이 키가 생긴다(정상 경로에는 없다).
    assert "adapter_forced_reason" not in detail
    assert "score_clamped" not in detail


def _assert_trace_row(db_session: Any, decision: MentionDecision) -> None:
    """`trace_id` 가 실재하는 `er_resolve` 행을 가리키고, 전용 필드와
    `detail["trace_id"]` 가 같은 값인지(단일 출처)."""

    assert decision.trace_id is not None
    assert decision.detail["trace_id"] == decision.trace_id
    row = db_session.get(AgentTrace, decision.trace_id)
    assert row is not None
    assert row.step == ER_TRACE_STEP
    # `apply_resolution` 을 부르지 않았으므로 실행 표시가 붙지 않는다.
    assert row.output["decision"]["applied"] is False
    assert row.output["decision"]["pending_question_id"] is None


# --- (a) 세 밴드가 그대로 옮겨진다 ---------------------------------------


@pytest.mark.dbtest
def test_merge_band_transfers_person_id_score_and_tokens(db_session, fake_embedder):
    session_id = "baseline-proposed-merge"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "어제 팀장이랑 저녁 먹었어"
    judge = FakeJudge(table={person.id: 0.95}, tokens=(123, 45))

    reference = er_resolve(ctx, "팀장", utterance, judge=judge, config=CONFIG)
    decision = ProposedResolver(judge=judge).resolve_mention(
        ctx, "팀장", utterance, config=CONFIG
    )

    assert reference.band == "merge"  # 이 테스트가 겨냥한 밴드가 맞는지 먼저
    assert decision.decision == "merge"
    assert decision.person_id == reference.matched_person_id == person.id
    assert decision.score >= CONFIG.t_merge
    assert decision.tokens_in == 123
    assert decision.tokens_out == 45
    assert decision.detail["ask_kind"] is None  # merge 는 묻지 않는다
    assert decision.detail["forced_reason"] is None
    assert decision.detail["provider"] == "fake"

    matched = next(c for c in decision.candidates if c.person_id == person.id)
    assert matched.score == pytest.approx(decision.score)
    assert matched.signals["exact_alias"] == 1.0

    _assert_faithful_transfer(decision, reference, "팀장")
    _assert_trace_row(db_session, decision)
    assert decision.trace_id != reference.trace_id  # 각 호출이 자기 행을 남긴다


@pytest.mark.dbtest
def test_identity_band_keeps_person_id_none_and_carries_score(db_session, fake_embedder):
    """`[T_new, T_merge)` 구간 -- 점수는 0 이 아니지만 인물을 고르지 않는다
    (원칙1·2, 불변 규약 3). `s_llm=0.2` 로 확신도를 그 구간에 넣는다."""

    session_id = "baseline-proposed-identity"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "팀장이 오늘 회의에서 그러더라"
    judge = FakeJudge(table={person.id: 0.2}, tokens=(70, 12))

    reference = er_resolve(ctx, "팀장", utterance, judge=judge, config=CONFIG)
    decision = ProposedResolver(judge=judge).resolve_mention(
        ctx, "팀장", utterance, config=CONFIG
    )

    assert reference.band == "identity"
    assert reference.matched_person_id == person.id  # 판정은 인물을 가리키지만
    assert decision.person_id is None  # 어댑터는 merge 가 아니면 비운다
    assert CONFIG.t_new <= decision.score < CONFIG.t_merge
    assert decision.detail["ask_kind"] == "identity"
    assert decision.detail["forced_reason"] is None
    # 후보 목록이 답이다 -- 사람에게 보여 줄 선택지가 비어 있으면 안 된다.
    assert [c.person_id for c in decision.candidates] == [person.id]

    _assert_faithful_transfer(decision, reference, "팀장")
    _assert_trace_row(db_session, decision)


@pytest.mark.dbtest
def test_new_person_band_carries_excluded_candidates(db_session, fake_embedder):
    """규칙 필터가 전 후보를 배제하면 LLM 을 부르지 않는다(`no_candidates`).
    배제된 후보와 그 사유가 `candidates`/`detail["excluded_by"]` 로 남는지
    (원칙9 -- 배제도 근거다)."""

    session_id = "baseline-proposed-new-person"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "이모가 주말에 온대"
    judge = FakeJudge(table={person.id: 0.9}, tokens=(999, 999))

    reference = er_resolve(ctx, "이모", utterance, judge=judge, config=CONFIG)
    decision = ProposedResolver(judge=judge).resolve_mention(
        ctx, "이모", utterance, config=CONFIG
    )

    assert reference.band == "new_person"
    assert reference.forced_reason == "no_candidates"
    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0
    # LLM 을 부르지 않았으므로 `FakeJudge.tokens` 가 흘러들지 않는다.
    assert (decision.tokens_in, decision.tokens_out) == (0, 0)
    assert decision.detail["llm_skipped"] is True
    assert decision.detail["forced_reason"] == "no_candidates"
    assert decision.detail["ask_kind"] == "new_person"
    assert decision.detail["excluded_by"] == {str(person.id): "relation_tag_conflict"}
    excluded = next(c for c in decision.candidates if c.person_id == person.id)
    assert excluded.score == 0.0
    assert excluded.signals["passed_rules"] == 0.0

    _assert_faithful_transfer(decision, reference, "이모")
    _assert_trace_row(db_session, decision)


@pytest.mark.dbtest
def test_forced_identity_reason_is_transferred_not_swallowed(db_session, fake_embedder):
    """LLM 실패는 예외가 아니라 `identity` 강등으로 온다(불변 규약 2,
    원칙1). `band`(identity)와 `band_by_threshold`(new_person)의 차이가
    "임계치가 아니라 실패 때문에 물었다"를 P4 에 전한다."""

    session_id = "baseline-proposed-forced"
    _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(fail="timeout")

    reference = er_resolve(ctx, "팀장", "발화", judge=judge, config=CONFIG)
    decision = ProposedResolver(judge=judge).resolve_mention(
        ctx, "팀장", "발화", config=CONFIG
    )

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] == "llm_failed"
    assert decision.detail["band_by_threshold"] == "new_person"
    assert decision.detail["llm_error"] == "timeout"
    assert decision.detail["llm_skipped"] is False

    _assert_faithful_transfer(decision, reference, "팀장")


@pytest.mark.dbtest
def test_decision_to_dict_is_json_serializable(db_session, fake_embedder):
    """P4 가 `metrics.json`/캐시로 보존한다(재현성, 원칙8)."""

    session_id = "baseline-proposed-json"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    decision = ProposedResolver(judge=FakeJudge(table={person.id: 0.95})).resolve_mention(
        ctx, "팀장", "발화", config=CONFIG
    )

    payload = json.loads(json.dumps(decision.to_dict(), ensure_ascii=False))
    assert payload["method"] == METHOD_NAME
    assert payload["detail"]["confidence_breakdown"]["s_llm"] == pytest.approx(0.95)
    assert payload["trace_id"] == decision.trace_id


@pytest.mark.dbtest
def test_same_input_twice_gives_same_decision(db_session, fake_embedder):
    """재현성(원칙8) -- `FakeJudge`·가짜 임베딩이면 두 번 불러도 같은 결정.
    `trace_id` 만 호출마다 새로 생긴다."""

    session_id = "baseline-proposed-repeat"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    resolver = ProposedResolver(judge=FakeJudge(table={person.id: 0.95}))

    first = resolver.resolve_mention(ctx, "팀장", "발화", config=CONFIG).to_dict()
    second = resolver.resolve_mention(ctx, "팀장", "발화", config=CONFIG).to_dict()

    first.pop("trace_id")
    second.pop("trace_id")
    first["detail"].pop("trace_id")
    second["detail"].pop("trace_id")
    assert first == second


# --- (b) 부수효과 0 (불변 규약 1) ----------------------------------------


@pytest.mark.dbtest
@pytest.mark.parametrize(
    ("mention", "s_llm", "expected"),
    [("팀장", 0.95, "merge"), ("팀장", 0.2, "identity"), ("이모", 0.9, "new_person")],
    ids=["merge", "identity", "new_person"],
)
def test_no_side_effect_on_persons_aliases_or_questions(
    db_session, fake_embedder, mention: str, s_llm: float, expected: str
):
    """세 밴드 어디에서도 `apply_resolution` 을 부르지 않는다 -- 별칭이
    붙지도(merge) 질문이 저장되지도(identity·new_person) 않는다."""

    session_id = f"baseline-proposed-side-effect-{expected}"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    before = _row_counts(db_session)
    traces_before = db_session.execute(
        select(func.count()).select_from(AgentTrace)
    ).scalar_one()

    decision = ProposedResolver(judge=FakeJudge(table={person.id: s_llm})).resolve_mention(
        ctx, mention, "발화", config=CONFIG
    )

    assert decision.decision == expected
    assert _row_counts(db_session) == before
    # 판정 근거는 남는다(원칙9) -- 부수효과 0 은 인물·별칭·질문에 대한 것이다.
    traces_after = db_session.execute(
        select(func.count()).select_from(AgentTrace)
    ).scalar_one()
    assert traces_after > traces_before


# --- (c) 방식 표 등록 경로 ------------------------------------------------


def test_proposed_is_registered_in_all_methods() -> None:
    assert METHOD_NAME in resolver_registry.ALL_METHODS
    assert RESOLVERS[METHOD_NAME] is ProposedResolver


def test_get_resolver_injects_judge() -> None:
    judge = FakeJudge(table={1: 0.5})
    resolver = get_resolver(METHOD_NAME, judge=judge)

    assert isinstance(resolver, ProposedResolver)
    assert resolver.judge is judge
    assert resolver.name == METHOD_NAME
    assert resolver.supported_decisions == DECISIONS


def test_default_judge_is_none_so_env_factory_decides() -> None:
    """어댑터가 기본 판정자를 새로 정하지 않는다 -- `judge=None` 이면
    `app.er.resolve()` 가 `judge_from_env()` 를 쓴다(설정 출처 단일화)."""

    assert ProposedResolver().judge is None


@pytest.mark.dbtest
def test_get_resolver_path_produces_same_decision_as_direct_construction(
    db_session, fake_embedder
):
    session_id = "baseline-proposed-factory"
    person = _seed_team_lead(db_session, fake_embedder)
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.95})

    via_factory = get_resolver(METHOD_NAME, judge=judge).resolve_mention(
        ctx, "팀장", "발화", config=CONFIG
    )
    direct = ProposedResolver(judge=judge).resolve_mention(ctx, "팀장", "발화", config=CONFIG)

    assert via_factory.decision == direct.decision
    assert via_factory.person_id == direct.person_id
    assert via_factory.score == pytest.approx(direct.score)


# --- (d) `MentionDecision` 규약 + 어댑터 방어(순수, DB 없음) --------------


def _resolution(**overrides: Any) -> Resolution:
    kwargs: dict[str, Any] = {
        "trace_id": 7,
        "mention": "김팀장",
        "candidates": [],
        "confidence": 0.5,
        "band": "identity",
        "band_by_threshold": "identity",
        "llm": {
            "provider": "fake",
            "model": None,
            "self_reported": True,
            "s_llm": 0.5,
            "reason": "r",
            "tokens_in": 0,
            "tokens_out": 0,
            "attempts": 1,
            "skipped": False,
            "error": None,
        },
    }
    kwargs.update(overrides)
    return Resolution(**kwargs)


@pytest.mark.parametrize("band", DECISIONS)
def test_person_id_is_set_only_for_merge(band: str) -> None:
    decision = to_mention_decision(
        _resolution(band=band, band_by_threshold=band, matched_person_id=11), "김팀장"
    )

    assert decision.decision == band
    assert (decision.person_id is not None) is (band == "merge")
    assert decision.decision in ProposedResolver.supported_decisions


def test_merge_without_matched_person_id_is_downgraded_not_raised() -> None:
    """도달 불가 조합이지만 예외로 죽지 않는다(불변 규약 2) -- 한 방식만
    예외로 죽으면 분모가 달라져 비교가 깨진다(원칙8)."""

    decision = to_mention_decision(
        _resolution(band="merge", band_by_threshold="merge", matched_person_id=None),
        "김팀장",
    )

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["adapter_forced_reason"] == "merge_without_person_id"
    assert decision.detail["band_by_threshold"] == "merge"


def test_out_of_range_confidence_is_clamped_not_raised() -> None:
    decision = to_mention_decision(_resolution(confidence=1.4), "김팀장")

    assert decision.score == 1.0
    assert decision.detail["score_clamped"] is True


def test_unknown_band_is_downgraded_to_identity() -> None:
    decision = to_mention_decision(_resolution(band="자동병합"), "김팀장")

    assert decision.decision == "identity"
    assert decision.detail["adapter_forced_reason"] == "unknown_band:자동병합"


def test_candidate_signals_are_all_floats() -> None:
    """`ResolverCandidate.signals` 는 `dict[str, float]` -- 불리언 신호는
    `1.0`/`0.0` 으로 옮기되 키 이름은 바꾸지 않는다(P4 가 이름으로 찾는다)."""

    scored = ScoredCandidate(
        person_id=11,
        display_name="김민수",
        s_emb=0.9,
        s_rule=0.75,
        rule_flags={"exact_alias": True, "embedding_skipped": False},
        rule_checked=4,
        rule_passed=3,
        passed_rules=True,
    )
    decision = to_mention_decision(_resolution(candidates=[scored]), "김팀장")

    signals = decision.candidates[0].signals
    assert all(isinstance(v, float) for v in signals.values())
    assert signals["s_emb"] == pytest.approx(0.9)
    assert signals["s_rule"] == pytest.approx(0.75)
    assert signals["exact_alias"] == 1.0
    assert signals["embedding_skipped"] == 0.0
    assert signals["rule_checked"] == 4.0
    assert signals["rule_passed"] == 3.0
    # 판정된 인물이 아니면 후보 점수는 "없음"(0.0)이다.
    assert decision.candidates[0].score == 0.0
