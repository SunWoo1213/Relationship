"""Refs: P3-er S3.3 D3 D10 R4 R9 결정1 결정3-c 결정4 결정5 원칙1 원칙4 원칙9
F-1d65ac -- U6 `resolve()` 오케스트레이션 + trace 통합 테스트, U7
`apply_resolution()` + 회귀 3종(승진·이모 배제·동명이인).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`) +
`FakeJudge`(결정9 -- 실 LLM 은 스모크 1회로 분리) + `fake_embedder`/
`grouped_embedder`(회귀 3종, 결정9 -- 통제된 유사도가 필요한 케이스).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import func, select, text

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.confidence import band_for
from app.er.judge import FakeJudge
from app.er.pipeline import apply_resolution, resolve
from app.er.types import ER_TRACE_STEP, ER_TRACE_TOOL_NAME, AlreadyApplied, ERConfig
from app.tools.context import ToolContext
from app.tools.types import AFFIRMATIVE_KEY

pytestmark = pytest.mark.dbtest

_EVIDENCE_DIR = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "wiki"
    / "packages"
    / "P3-er"
    / "evidence"
)


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


# ---------------------------------------------------------------------------
# U7 -- grouped_embedder 자기 검증
# ---------------------------------------------------------------------------


def test_grouped_embedder_similarity_self_check(grouped_embedder):
    """`grouped_embedder` 픽스처 자체의 계약 검증(위임 프롬프트 "짧은 자기
    검증 테스트 1건") -- 같은 그룹 문자열끼리 코사인 유사도 ≥ 0.8, 다른
    그룹·미등재 문자열은 ≤ 0.2, 단위벡터, 차원 `EMBEDDING_DIM`."""

    from app.embedding import EMBEDDING_DIM

    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"], "park": ["과장"]})
    vectors = embedder(["팀장", "김팀장", "부장님", "과장", "이모"])
    names = ["팀장", "김팀장", "부장님", "과장", "이모"]

    for v in vectors:
        assert len(v) == EMBEDDING_DIM
        norm = sum(x * x for x in v) ** 0.5
        assert abs(norm - 1.0) < 1e-6

    def cos(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    by_name = dict(zip(names, vectors))
    # 같은 그룹("kim"): 팀장/김팀장/부장님 서로 ≥ 0.8.
    for a, b in (("팀장", "김팀장"), ("팀장", "부장님"), ("김팀장", "부장님")):
        assert cos(by_name[a], by_name[b]) >= 0.8

    # 다른 그룹("kim" vs "park")·미등재("이모")는 ≤ 0.2.
    for a, b in (("팀장", "과장"), ("팀장", "이모"), ("과장", "이모")):
        assert abs(cos(by_name[a], by_name[b])) <= 0.2


# ---------------------------------------------------------------------------
# U7 -- apply_resolution() + 회귀 3종
# ---------------------------------------------------------------------------


def _write_evidence(name: str, content: str) -> Path:
    _EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    path = _EVIDENCE_DIR / f"{stamp}-u7-{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def test_apply_resolution_promotion_connects_via_relaxed_retry_promotion(
    db_session, grouped_embedder
):
    """01-plan 결정9 "승진 회귀(a) 픽스처 확정" 그대로 -- 저장 위계(동) ↔
    유도 위계(상) 불일치 -> 엄격 필터 탈락 -> 인접(1칸) -> 완화 1회 재평가
    통과 -> `grouped_embedder` 로 높은 `s_emb` -> `confidence ≈ 0.863
    ≥ T_merge` -> `band="merge"` -> `apply_resolution` 이 별칭만 누적
    (`display_name` 무변경)."""

    session_id = "er-apply-promotion"
    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"]})
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=embedder(["팀장"])[0])
    _add_alias(db_session, person, "김팀장", embedding=embedder(["김팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=embedder)
    judge = FakeJudge(table={person.id: 0.95})

    result = resolve(
        ctx, "부장님", "요즘 부장님이 회식을 자주 잡으셔", judge=judge, config=ERConfig()
    )

    assert result.decision["relaxed_retry"] is True
    candidate = next(c for c in result.candidates if c.person_id == person.id)
    assert candidate.relaxed_pass is True
    assert candidate.rule_checked == 3
    assert candidate.rule_passed == 2
    assert abs(candidate.s_rule - (2 / 3)) < 1e-9
    assert candidate.s_emb >= 0.8

    breakdown = result.confidence_breakdown
    assert breakdown["s_llm"] == 0.95
    assert breakdown["confidence"] >= 0.8
    assert abs(breakdown["confidence"] - 0.863) < 0.01
    assert result.band == "merge"
    assert result.forced_reason is None

    applied = apply_resolution(ctx, result)
    assert applied.trace_id == result.trace_id
    assert applied.band == "merge"
    assert applied.action == "merge"
    assert applied.person_id == person.id
    assert applied.alias_added is True
    assert applied.pending_question_id is None
    assert applied.applied_at is not None

    aliases = (
        db_session.execute(select(PersonAlias.alias).where(PersonAlias.person_id == person.id))
        .scalars()
        .all()
    )
    assert "부장님" in aliases

    db_session.expire_all()
    refreshed = db_session.get(Person, person.id)
    assert refreshed.display_name == "김민수"

    # 판정 방법 표의 SQL 그대로 -- evidence 로 1행을 남긴다.
    sql = (
        "SELECT step, tool_name, output->'confidence_breakdown' AS confidence_breakdown, "
        "output->'decision' AS decision, tokens_in, tokens_out FROM agent_traces "
        "WHERE step='er_resolve' AND session_id=:sid"
    )
    row = db_session.execute(text(sql), {"sid": session_id}).mappings().one()
    _write_evidence(
        "promotion-trace-sql",
        f"SQL:\n{sql}\n\nsession_id={session_id}\n\nrow=\n"
        f"{json.dumps(dict(row), indent=2, ensure_ascii=False, default=str)}\n",
    )


def test_apply_resolution_aunt_excluded_creates_new_person_question_aunt(
    db_session, grouped_embedder
):
    """01-plan 리스크 41행 "팀장 vs 이모 배제" -- 관계 태그 그룹 불일치로
    규칙 필터 탈락(모순, 인접 완화 부적격) -> 규칙 통과 후보 0 -> LLM 생략
    -> `new_person` -> `apply_resolution` 이 `ask_user(kind="new_person")`
    를 저장한다."""

    session_id = "er-apply-aunt"
    embedder = grouped_embedder({"kim": ["팀장"]})
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=embedder)
    judge = FakeJudge(table={person.id: 0.9})

    result = resolve(ctx, "이모", "이모가 또 전화하셨어", judge=judge, config=ERConfig())

    excluded = next(c for c in result.candidates if c.person_id == person.id)
    assert excluded.passed_rules is False
    assert excluded.excluded_by == "relation_tag_conflict"
    assert result.llm["skipped"] is True
    assert result.forced_reason == "no_candidates"
    assert result.band == "new_person"

    applied = apply_resolution(ctx, result)
    assert applied.band == "new_person"
    assert applied.action == "ask_new_person"
    assert applied.person_id is None
    assert applied.pending_question_id is not None

    rows = (
        db_session.execute(
            select(PendingQuestion).where(PendingQuestion.session_id == session_id)
        )
        .scalars()
        .all()
    )
    assert len(rows) == 1
    assert rows[0].kind == "new_person"
    assert rows[0].id == applied.pending_question_id


def test_apply_resolution_homonym_splits_into_identity_question_homonym(
    db_session, grouped_embedder
):
    """01-plan 리스크 42행 "동명이인 분리" -- 같은 별칭("민수")을 가진
    두 인물(둘 다 친구·동) 모두 규칙 통과 -> `FakeJudge` 가 중간 `s_llm`
    으로 하나에 귀속 -> `confidence ∈ [T_new, T_merge)` -> `identity` ->
    `apply_resolution` 이 `ask_user(kind="identity")` 를 저장하고, 두
    후보의 `s_emb`/`s_rule` 은 `candidates[]` 에 그대로 남는다."""

    session_id = "er-apply-homonym"
    embedder = grouped_embedder({"minsu": ["민수"]})
    person1 = _make_person(db_session, display_name="김민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person1, "민수", embedding=embedder(["민수"])[0])
    person2 = _make_person(db_session, display_name="이민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person2, "민수", embedding=embedder(["민수"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=embedder)
    judge = FakeJudge(table={person1.id: 0.55}, pick=person1.id)

    result = resolve(ctx, "민수", "민수가 그러던데", judge=judge, config=ERConfig())

    for candidate in result.candidates:
        assert candidate.passed_rules is True

    config = ERConfig()
    assert config.t_new <= result.confidence < config.t_merge
    assert result.band == "identity"

    by_person = {c.person_id: c for c in result.candidates}
    assert by_person[person1.id].s_rule == 0.0
    assert by_person[person2.id].s_rule == 0.0
    assert by_person[person1.id].s_emb is not None
    assert by_person[person2.id].s_emb is not None

    ask_payload = result.ask_payload
    assert ask_payload is not None
    assert ask_payload["kind"] == "identity"
    assert set(ask_payload["context"]["candidate_ids"].values()) == {person1.id, person2.id}

    applied = apply_resolution(ctx, result)
    assert applied.band == "identity"
    assert applied.action == "ask_identity"
    assert applied.person_id is None
    assert applied.pending_question_id is not None

    rows = (
        db_session.execute(
            select(PendingQuestion).where(PendingQuestion.session_id == session_id)
        )
        .scalars()
        .all()
    )
    assert len(rows) == 1
    assert rows[0].kind == "identity"


def test_apply_resolution_updates_only_three_decision_fields_via_raw_sql_applied(
    db_session, fake_embedder
):
    """F-93f063 -- 부분 갱신을 **원시 SQL 재조회**로 검증한다(같은 세션
    identity map 이 in-place dict 변경을 오탐하지 않도록). `applied`/
    `pending_question_id`/`applied_at` 세 필드만 바뀌고 나머지 판정
    필드(`confidence_breakdown`/`candidates`/`llm`/`band`)는 JSON 문자열
    비교로 완전히 동일해야 한다. `er_resolve` 행 수는 여전히 1."""

    session_id = "er-apply-fields"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.95})
    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())
    assert result.band == "merge"

    sql = "SELECT output FROM agent_traces WHERE id = :id"
    before = db_session.execute(text(sql), {"id": result.trace_id}).scalar_one()
    assert before["decision"]["applied"] is False
    assert before["decision"]["pending_question_id"] is None
    assert before["decision"]["applied_at"] is None
    before_band = before["decision"]["band"]
    before_breakdown = json.dumps(before["confidence_breakdown"], sort_keys=True)
    before_candidates = json.dumps(before["candidates"], sort_keys=True)
    before_llm = json.dumps(before["llm"], sort_keys=True)

    apply_resolution(ctx, result)
    db_session.flush()
    db_session.expire_all()

    after = db_session.execute(text(sql), {"id": result.trace_id}).scalar_one()
    assert after["decision"]["applied"] is True
    assert after["decision"]["pending_question_id"] is None
    assert after["decision"]["applied_at"] is not None
    assert after["decision"]["band"] == before_band
    assert json.dumps(after["confidence_breakdown"], sort_keys=True) == before_breakdown
    assert json.dumps(after["candidates"], sort_keys=True) == before_candidates
    assert json.dumps(after["llm"], sort_keys=True) == before_llm

    rows = [r for r in _trace_rows(db_session, session_id) if r.step == ER_TRACE_STEP]
    assert len(rows) == 1


def test_resolve_without_apply_creates_no_pending_question_no_apply_no_question(
    db_session, fake_embedder
):
    """`resolve()` 만 부르면(결정4 -- 부수효과 없음) `pending_questions`
    행이 생기지 않는다 -- `apply_resolution` 을 불러야만 저장된다."""

    session_id = "er-no-apply"
    person1 = _make_person(db_session, display_name="김민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person1, "민수", embedding=fake_embedder(["민수"])[0])
    person2 = _make_person(db_session, display_name="이민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person2, "민수", embedding=fake_embedder(["민수"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person1.id: 0.55}, pick=person1.id)
    result = resolve(ctx, "민수", "발화", judge=judge, config=ERConfig())
    assert result.band == "identity"

    _, _, questions = _row_counts(db_session)
    assert questions == 0


def test_apply_resolution_twice_raises_and_leaves_state_unchanged_double_apply(
    db_session, fake_embedder
):
    """F-8809f2 -- 같은 `Resolution` 으로 `apply_resolution` 을 두 번
    부르면 두 번째는 `AlreadyApplied` 로 거부되고 `pending_questions`/
    `person_aliases` 행 수가 늘지 않는다."""

    session_id = "er-apply-double"
    person1 = _make_person(db_session, display_name="김민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person1, "민수", embedding=fake_embedder(["민수"])[0])
    person2 = _make_person(db_session, display_name="이민수", relation_tag="친구", hierarchy="동")
    _add_alias(db_session, person2, "민수", embedding=fake_embedder(["민수"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person1.id: 0.55}, pick=person1.id)
    result = resolve(ctx, "민수", "발화", judge=judge, config=ERConfig())
    assert result.band == "identity"

    first = apply_resolution(ctx, result)
    assert first.pending_question_id is not None

    before_counts = _row_counts(db_session)

    with pytest.raises(AlreadyApplied):
        apply_resolution(ctx, result)

    after_counts = _row_counts(db_session)
    assert before_counts == after_counts

    trace_rows = [r for r in _trace_rows(db_session, session_id) if r.step == ER_TRACE_STEP]
    assert len(trace_rows) == 1


def test_apply_resolution_merge_does_not_change_display_name_display_name_unchanged(
    db_session, fake_embedder
):
    """결정3-b/D6 -- merge 구간은 별칭만 누적하고 `display_name` 은
    확인 없이 바꾸지 않는다."""

    session_id = "er-apply-display-name"
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    judge = FakeJudge(table={person.id: 0.95})
    result = resolve(ctx, "팀장", "발화", judge=judge, config=ERConfig())
    assert result.band == "merge"
    assert result.suggested_display_name == "김민수"

    apply_resolution(ctx, result)

    db_session.expire_all()
    refreshed = db_session.get(Person, person.id)
    assert refreshed.display_name == "김민수"
