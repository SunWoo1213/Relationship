"""Refs: P3-er S3.3 D3 D10 R4 R9 결정1 결정3-c 결정4 결정5 원칙1 원칙4 원칙9
F-1d65ac -- U6 `resolve()` 오케스트레이션 + trace 통합 테스트.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`) +
`FakeJudge`(결정9 -- 실 LLM 은 스모크 1회로 분리) + `fake_embedder`. 승진
회귀·이모 배제·동명이인 3종의 **완전한** 규약(정확한 수치·`apply_resolution`
연동)은 U7 이 `grouped_embedder` 로 채운다(01-plan U7 체크리스트) -- 이
파일의 목적은 `resolve()` 자체(4단계 오케스트레이션·trace 스키마·부수효과
0·강제 강등 경로)를 확인하는 것이다.
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.confidence import band_for
from app.er.judge import FakeJudge
from app.er.pipeline import resolve
from app.er.types import ER_TRACE_STEP, ER_TRACE_TOOL_NAME, ERConfig
from app.tools.context import ToolContext
from app.tools.types import AFFIRMATIVE_KEY

pytestmark = pytest.mark.dbtest


def _make_person(
    db_session,
    *,
    user_id: str = "local",
    display_name: str,
    relation_tag: str = "지인",
    hierarchy: str = "동",
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(
    db_session,
    person: Person,
    alias: str,
    *,
    embedding: list[float] | None = None,
    source: str = ALIAS_SOURCES[0],
) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=source, embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


def _ctx(db_session, *, session_id: str, embedder=None) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder)


def _row_counts(db_session) -> tuple[int, int, int]:
    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    questions = db_session.execute(
        select(func.count()).select_from(PendingQuestion)
    ).scalar_one()
    return persons, aliases, questions


def _trace_rows(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == session_id)
        ).scalars()
    )


def test_resolve_records_all_four_stages_in_single_trace_row_stages(db_session, fake_embedder):
    session_id = "er-pipeline-stages"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.9})

    result = resolve(ctx, "팀장", "어제 팀장이랑 저녁 먹었어", judge=judge, config=ERConfig())

    rows = [r for r in _trace_rows(db_session, session_id) if r.step == ER_TRACE_STEP]
    assert len(rows) == 1
    row = rows[0]
    assert row.tool_name == ER_TRACE_TOOL_NAME
    assert result.trace_id == row.id

    output = row.output
    assert output["er_version"]
    assert output["mention"] == "팀장"
    assert isinstance(output["relaxed_retry"], bool)
    assert len(output["candidates"]) >= 1
    assert set(output["confidence_breakdown"]) >= {
        "matched_person_id",
        "s_llm",
        "s_emb",
        "s_rule",
        "weights",
        "confidence",
        "rule_checked",
        "rule_passed",
    }
    assert set(output["decision"]) >= {
        "band",
        "band_by_threshold",
        "forced_reason",
        "action",
        "T_merge",
        "T_new",
        "matched_person_id",
        "relaxed_retry",
        "hierarchy_relaxed_retry",
        "applied",
        "pending_question_id",
        "applied_at",
    }
    assert set(output["llm"]) >= {
        "provider",
        "model",
        "self_reported",
        "s_llm",
        "reason",
        "tokens_in",
        "tokens_out",
        "attempts",
        "skipped",
        "error",
    }


def test_resolve_has_no_side_effect_on_persons_or_questions_no_side_effect(
    db_session, fake_embedder
):
    session_id = "er-pipeline-no-side-effect"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    before = _row_counts(db_session)
    trace_before = len(_trace_rows(db_session, session_id))

    resolve(ctx, "팀장", "발화", judge=FakeJudge(table={person.id: 0.9}), config=ERConfig())

    after = _row_counts(db_session)
    trace_after = len(_trace_rows(db_session, session_id))

    assert before == after
    assert trace_after > trace_before


def test_resolve_confidence_is_recomputable_from_trace_breakdown_recompute(
    db_session, fake_embedder
):
    session_id = "er-pipeline-recompute"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    config = ERConfig()

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    result = resolve(ctx, "팀장", "발화", judge=FakeJudge(table={person.id: 0.9}), config=config)

    assert result.forced_reason is None
    breakdown = result.confidence_breakdown
    recomputed = (
        breakdown["weights"]["llm"] * breakdown["s_llm"]
        + breakdown["weights"]["emb"] * breakdown["s_emb"]
        + breakdown["weights"]["rule"] * breakdown["s_rule"]
    )
    assert abs(recomputed - breakdown["confidence"]) < 1e-9
    assert band_for(breakdown["confidence"], config) == result.band == result.band_by_threshold


def test_resolve_llm_failed_forces_identity_band_llm_failed(db_session, fake_embedder):
    session_id = "er-pipeline-llm-failed"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(fail="timeout")

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.forced_reason == "llm_failed"
    assert result.band == "identity"
    assert result.band_by_threshold == "new_person"
    assert result.llm["skipped"] is False
    assert result.llm["error"] == "timeout"
    assert result.ask_payload is not None
    assert result.ask_payload["kind"] == "identity"


def test_resolve_skips_llm_when_no_candidates_pass_rules_no_candidates(db_session, fake_embedder):
    session_id = "er-pipeline-no-candidates"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    # table 을 채워도(호출됐다면 매치될 수 있는 값) 스킵돼야 한다 --
    # "호출 자체가 없다"를 tokens/attempts 로 확인한다.
    judge = FakeJudge(table={person.id: 0.9})

    result = resolve(ctx, "이모", "발화", judge=judge, config=ERConfig())

    assert result.forced_reason == "no_candidates"
    assert result.band == "new_person"
    assert result.band_by_threshold == "new_person"
    assert result.llm["skipped"] is True
    assert result.llm["tokens_in"] == 0
    assert result.llm["tokens_out"] == 0
    assert result.llm["attempts"] == 0
    assert result.llm["error"] is None
    assert result.ask_payload is not None
    assert result.ask_payload["kind"] == "new_person"

    excluded = next(c for c in result.candidates if c.person_id == person.id)
    assert excluded.passed_rules is False
    assert excluded.excluded_by == "relation_tag_conflict"


def test_resolve_null_matched_person_id_forces_identity_not_new_person_null_path(
    db_session, fake_embedder
):
    """F-1d65ac: `matched_person_id=None`(LLM 자기보고 "아무도 아님")은
    규칙 통과 후보가 있으면 `identity` 로 강등되지 `new_person` 이 아니다
    (결정3-c(b)). "통과 후보 0 + null" 가지는 3단계 LLM 을 아예 부르지
    않으므로(01-plan 34행 최적화) 도달 불가이며 테스트하지 않는다."""
    session_id = "er-pipeline-null-path"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    # table 이 비어 있으면 통과 후보와 교집합이 없어 matched_person_id=None.
    judge = FakeJudge(table={})

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.forced_reason == "no_matched"
    assert result.band == "identity"
    assert result.band_by_threshold == "new_person"
    breakdown = result.confidence_breakdown
    assert breakdown["matched_person_id"] is None
    assert breakdown["s_llm"] == 0.0
    assert breakdown["s_emb"] == 0.0
    assert breakdown["s_rule"] == 0.0
    assert result.llm["skipped"] is False
    assert result.llm["error"] is None
    assert result.ask_payload is not None
    assert result.ask_payload["kind"] == "identity"


def test_resolve_merge_band_has_no_ask_payload_but_suggests_display_name_merge_payload(
    db_session, fake_embedder
):
    session_id = "er-pipeline-merge-payload"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.95})

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.band == "merge"
    assert result.forced_reason is None
    assert result.ask_payload is None
    assert result.suggested_display_name == "김민수"
    assert result.decision["applied"] is False
    assert result.decision["pending_question_id"] is None
    assert result.decision["applied_at"] is None


def test_resolve_identity_band_ask_payload_lists_candidate_options_identity_payload(
    db_session, fake_embedder
):
    session_id = "er-pipeline-identity-payload"
    person1 = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person1, "팀장", embedding=fake_embedder(["팀장"])[0])
    person2 = _make_person(db_session, display_name="박철수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person2, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person1.id: 0.5, person2.id: 0.3})

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.band == "identity"
    ask_payload = result.ask_payload
    assert ask_payload is not None
    assert ask_payload["kind"] == "identity"
    assert ask_payload["options"][-1] == "아니요, 다른 사람이에요"
    assert set(ask_payload["options"][:-1]) == {"김민수", "박철수"}
    assert set(ask_payload["affirmative_options"]) == {"김민수", "박철수"}
    assert ask_payload["context"]["mention"] == "팀장"
    assert ask_payload["context"]["utterance"] == "발화"
    assert ask_payload["context"]["candidate_ids"] == {
        "김민수": person1.id,
        "박철수": person2.id,
    }
    assert ask_payload["context"][AFFIRMATIVE_KEY] == ask_payload["affirmative_options"]


def test_resolve_records_provider_and_self_reported_flag_provider_in_trace(
    db_session, fake_embedder
):
    session_id = "er-pipeline-provider"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.9})

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.llm["provider"] == "fake"
    assert result.llm["model"] is None
    assert result.llm["self_reported"] is True


def test_resolve_sets_applied_fields_false_and_null_before_apply_applied_fields(
    db_session, fake_embedder
):
    session_id = "er-pipeline-applied-fields"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.9})

    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())

    assert result.decision["applied"] is False
    assert result.decision["pending_question_id"] is None
    assert result.decision["applied_at"] is None
