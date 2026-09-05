"""Refs: P2-tools S3.2 S3.3 D1 D4 D5 D6 원칙1 원칙2 원칙4 -- `search_person`
후보 검색(신호만 -- 배제·병합·확신도 계산은 P3-er) + `create_person`/
`update_person`(U4 -- D1 확인 강제·F-b97a06 긍정 답 규약·D6 별칭 누적·
결정6 사실 upsert).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다. `ask_user`(U6)가 아직 없으므로 U4 테스트는 `pending_questions` 행을
직접 만들어 확인 상태를 구성한다.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
)
from app.tools.context import ToolContext
from app.tools.persons import create_person, search_person, update_person
from app.tools.types import AFFIRMATIVE_KEY, ConfirmationRequired, InvalidValue, PersonNotFound

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
        user_id=user_id,
        display_name=display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
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


def _ctx(
    db_session,
    *,
    session_id: str = "search-test",
    embedder=None,
    user_id: str = "local",
    confirmed_question_id: int | None = None,
):
    return ToolContext(
        session=db_session,
        session_id=session_id,
        user_id=user_id,
        embedder=embedder,
        confirmed_question_id=confirmed_question_id,
    )


def _make_pending_question(
    db_session,
    *,
    session_id: str = "confirm-test",
    kind: str = "new_person",
    question: str = "저장할까요?",
    options: list[str] | None = None,
    context: dict | None = None,
    answer: str | None = "예",
    answered: bool = True,
) -> PendingQuestion:
    """U6(`ask_user`) 이전이므로 확인 상태를 직접 만든다. 기본값은 D1/F-b97a06
    을 모두 통과하는 "정상" 질문이며, 개별 테스트가 필드 하나씩 깨뜨린다."""
    if options is None:
        options = ["예", "아니오"]
    if context is None:
        context = {AFFIRMATIVE_KEY: ["예"]}
    row = PendingQuestion(
        session_id=session_id,
        kind=kind,
        question=question,
        options=options,
        context=context,
        answer=answer,
        answered_at=datetime.now(timezone.utc) if answered else None,
    )
    db_session.add(row)
    db_session.flush()
    return row


def test_exact_alias_match_ranks_first_and_sets_flag(db_session):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "팀장")
    ctx = _ctx(db_session)

    candidates = search_person(ctx, "팀장")

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.person.id == person.id
    assert candidate.rule_flags["exact_alias"] is True
    assert candidate.rule_flags["partial_alias"] is False
    assert candidate.aliases_matched == ["팀장"]


def test_partial_alias_match_when_query_is_substring_of_alias(db_session):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "김팀장")
    ctx = _ctx(db_session)

    candidates = search_person(ctx, "팀장")

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.rule_flags["partial_alias"] is True
    assert candidate.rule_flags["exact_alias"] is False
    assert candidate.aliases_matched == ["김팀장"]


def test_embedding_similarity_max_per_person_and_not_skipped(db_session, fake_embedder):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "그 사람", embedding=fake_embedder(["그 사람"])[0])
    _add_alias(db_session, person, "그분", embedding=fake_embedder(["그분"])[0])
    other = _make_person(db_session, display_name="이영희")
    _add_alias(db_session, other, "동기", embedding=fake_embedder(["동기"])[0])

    ctx = _ctx(db_session, embedder=fake_embedder)

    candidates = search_person(ctx, "그 사람")

    by_person_id = {c.person.id: c for c in candidates}
    assert person.id in by_person_id
    top = by_person_id[person.id]
    assert top.rule_flags["embedding_skipped"] is False
    assert 0.0 < top.similarity <= 1.0
    assert top.similarity == pytest.approx(1.0, abs=1e-6)
    # 같은 인물의 별칭 2개("그 사람"·"그분")가 후보에 인물 1회로만 집계된다.
    assert sum(1 for c in candidates if c.person.id == person.id) == 1


def test_no_embedder_marks_embedding_skipped_but_alias_match_still_works(db_session):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "팀장")
    ctx = _ctx(db_session, embedder=None)

    candidates = search_person(ctx, "팀장")

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.rule_flags["embedding_skipped"] is True
    assert candidate.similarity == 0.0
    assert candidate.rule_flags["exact_alias"] is True


def test_hints_do_not_exclude_candidates_only_set_rule_flags(db_session):
    """오탐지 배제 금지(원칙1) 회귀: hints 로 후보를 걸러내면 이 테스트가
    실패해야 한다(U3 검증 절차의 변이 테스트 대상)."""
    person = _make_person(db_session, display_name="김상무", hierarchy="상")
    _add_alias(db_session, person, "동료")
    ctx = _ctx(db_session)

    candidates_ha = search_person(ctx, "동료", hints={"hierarchy": "하"})
    assert len(candidates_ha) == 1
    flags_ha = candidates_ha[0].rule_flags
    assert flags_ha["hierarchy_match"] is False
    assert flags_ha["hierarchy_adjacent"] is False  # 상↔하: 두 단계 차이

    candidates_dong = search_person(ctx, "동료", hints={"hierarchy": "동"})
    assert len(candidates_dong) == 1
    flags_dong = candidates_dong[0].rule_flags
    assert flags_dong["hierarchy_match"] is False
    assert flags_dong["hierarchy_adjacent"] is True  # 상↔동: 인접

    candidates_sang = search_person(ctx, "동료", hints={"hierarchy": "상"})
    assert len(candidates_sang) == 1
    flags_sang = candidates_sang[0].rule_flags
    assert flags_sang["hierarchy_match"] is True
    assert flags_sang["hierarchy_adjacent"] is False  # 같은 위계는 인접이 아니다


def test_invalid_hint_value_or_key_raises_invalid_value(db_session):
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        search_person(ctx, "팀장", hints={"hierarchy": "최고"})

    with pytest.raises(InvalidValue):
        search_person(ctx, "팀장", hints={"relation_tag": "동료"})

    with pytest.raises(InvalidValue):
        search_person(ctx, "팀장", hints={"unknown_key": "동"})


def test_other_user_persons_are_excluded(db_session):
    other_person = _make_person(db_session, user_id="other-user", display_name="타인")
    _add_alias(db_session, other_person, "팀장")
    ctx = _ctx(db_session, user_id="local")

    candidates = search_person(ctx, "팀장")

    assert candidates == []


def test_result_ordering_is_deterministic_with_id_tiebreak(db_session):
    person_a = _make_person(db_session, display_name="가나다")
    _add_alias(db_session, person_a, "동료")
    person_b = _make_person(db_session, display_name="라마바")
    _add_alias(db_session, person_b, "동료")
    ctx = _ctx(db_session)

    first = search_person(ctx, "동료")
    second = search_person(ctx, "동료")

    ids_first = [c.person.id for c in first]
    ids_second = [c.person.id for c in second]
    assert ids_first == ids_second
    assert ids_first == sorted(ids_first)


def test_empty_query_raises_invalid_value(db_session):
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        search_person(ctx, "")

    with pytest.raises(InvalidValue):
        search_person(ctx, "   ")


def test_search_person_writes_one_agent_trace_row(db_session):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "팀장")
    ctx = _ctx(db_session, session_id="trace-search-1")

    search_person(ctx, "팀장")

    rows = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-search-1")
        ).scalars()
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.step == "tool_call"
    assert row.tool_name == "search_person"
    assert isinstance(row.output, list)
    assert row.output[0]["person"]["display_name"] == "김철수"
    assert row.tokens_in == 0
    assert row.tokens_out == 0


# ---------------------------------------------------------------------------
# U4: create_person -- D1 확인 강제 + F-b97a06 긍정 답 규약 (직접 호출은
# 실패해야 한다, D01 카드).
# ---------------------------------------------------------------------------


def test_create_person_without_confirmed_question_id_raises(db_session):
    ctx = _ctx(db_session)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", ["팀장"], "직장", "상")


def test_create_person_with_identity_kind_question_raises(db_session):
    """new_person 이 아니라 identity 질문으로는 create_person 을 통과시키지
    않는다(D1)."""
    question = _make_pending_question(db_session, kind="identity")
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", [], "직장", "상")


def test_create_person_with_unanswered_question_raises(db_session):
    question = _make_pending_question(db_session, answered=False)
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", [], "직장", "상")


def test_create_person_with_mismatched_session_id_raises(db_session):
    question = _make_pending_question(db_session, session_id="session-a")
    ctx = _ctx(db_session, session_id="session-b", confirmed_question_id=question.id)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", [], "직장", "상")


def test_create_person_with_negative_answer_raises(db_session):
    """F-b97a06: 답은 했지만 부정 선택지 -- D1 '승인 시에만' 을 통과시키지
    않는다."""
    question = _make_pending_question(db_session, answer="아니오")
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", [], "직장", "상")


def test_create_person_without_affirmative_options_in_context_raises(db_session):
    """context 에 affirmative_options 키가 아예 없으면 안전한 기본값(거부)."""
    question = _make_pending_question(db_session, context={})
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(ConfirmationRequired):
        create_person(ctx, "김철수", [], "직장", "상")


def test_create_person_with_valid_confirmation_succeeds(db_session):
    question = _make_pending_question(db_session)
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    result = create_person(ctx, "김철수", ["팀장", "김팀장", "팀장"], "직장", "상")

    assert result.display_name == "김철수"
    assert result.relation_tag == "직장"
    assert result.hierarchy == "상"
    assert set(result.aliases) == {"팀장", "김팀장", "김철수"}

    rows = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == result.id))
        .scalars()
        .all()
    )
    by_alias = {row.alias: row for row in rows}
    assert len(rows) == 3  # 중복 별칭("팀장" 두 번)은 한 행으로 정리된다
    assert by_alias["팀장"].source == ALIAS_SOURCES[1]
    assert by_alias["팀장"].confirmed_at is not None
    assert by_alias["김팀장"].source == ALIAS_SOURCES[1]
    assert by_alias["김철수"].source == ALIAS_SOURCES[2]


def test_create_person_fills_alias_embedding_when_embedder_present(db_session, fake_embedder):
    question = _make_pending_question(db_session)
    ctx = _ctx(
        db_session,
        session_id=question.session_id,
        confirmed_question_id=question.id,
        embedder=fake_embedder,
    )

    result = create_person(ctx, "이영희", ["동기"], "친구", "동")

    rows = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == result.id))
        .scalars()
        .all()
    )
    assert len(rows) == 2  # "동기" + system 별칭 "이영희"
    for row in rows:
        assert row.embedding is not None
        assert len(row.embedding) == 1536


def test_create_person_leaves_alias_embedding_null_without_embedder(db_session):
    question = _make_pending_question(db_session)
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    result = create_person(ctx, "박민수", ["후배"], "친구", "하")

    rows = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == result.id))
        .scalars()
        .all()
    )
    assert rows
    for row in rows:
        assert row.embedding is None


def test_create_person_invalid_relation_tag_raises(db_session):
    question = _make_pending_question(db_session)
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(InvalidValue):
        create_person(ctx, "김철수", [], "동료", "상")


def test_create_person_invalid_hierarchy_raises(db_session):
    question = _make_pending_question(db_session)
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    with pytest.raises(InvalidValue):
        create_person(ctx, "김철수", [], "직장", "최고")


def test_create_person_writes_one_agent_trace_row(db_session):
    question = _make_pending_question(db_session, session_id="trace-create-1")
    ctx = _ctx(db_session, session_id="trace-create-1", confirmed_question_id=question.id)

    create_person(ctx, "김철수", [], "직장", "상")

    rows = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-create-1")
        ).scalars()
    )
    assert len(rows) == 1
    assert rows[0].tool_name == "create_person"
    assert rows[0].tokens_in == 0
    assert rows[0].tokens_out == 0


# ---------------------------------------------------------------------------
# U4: update_person -- 별칭 누적(격상 규칙)·display_name 확인 요건(D6)·
# facts upsert(결정6)·user_id 격리.
# ---------------------------------------------------------------------------


def test_update_person_new_alias_adds_row(db_session):
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "팀장")
    before = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    ctx = _ctx(db_session)

    result = update_person(ctx, person.id, new_alias="김팀장")

    after = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    assert after == before + 1
    assert "김팀장" in result.aliases


def test_update_person_duplicate_alias_does_not_add_row_and_never_downgrades(db_session):
    """미결 7: 같은 문자열이 이미 `system`(상위)로 있으면 `user_said`(하위)로
    다시 들어와도 새 행을 만들지 않고, 격하도 하지 않는다."""
    person = _make_person(db_session, display_name="김철수")
    _add_alias(db_session, person, "팀장", source=ALIAS_SOURCES[2])
    before = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    ctx = _ctx(db_session)

    update_person(ctx, person.id, new_alias="팀장")

    after = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    assert after == before

    row = db_session.execute(
        select(PersonAlias)
        .where(PersonAlias.person_id == person.id)
        .where(PersonAlias.alias == "팀장")
    ).scalar_one()
    assert row.source == ALIAS_SOURCES[2]  # 격하되지 않음


def test_update_person_display_name_without_confirmation_raises(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session)

    with pytest.raises(ConfirmationRequired):
        update_person(ctx, person.id, display_name="김부장")


def test_update_person_display_name_with_confirmation_updates_and_keeps_old_alias(db_session):
    person = _make_person(db_session, display_name="김팀장")
    _add_alias(db_session, person, "김팀장", source=ALIAS_SOURCES[2])
    question = _make_pending_question(db_session, kind="identity")
    before = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    ctx = _ctx(db_session, session_id=question.session_id, confirmed_question_id=question.id)

    result = update_person(ctx, person.id, display_name="김부장")

    assert result.display_name == "김부장"
    assert "김팀장" in result.aliases  # 이전 호칭 유지(D6, 삭제 없음)
    assert "김부장" in result.aliases  # 새 이름도 별칭으로 누적(F-2418ef)

    after = db_session.execute(
        select(func.count()).select_from(PersonAlias).where(PersonAlias.person_id == person.id)
    ).scalar_one()
    assert after == before + 1  # 삭제 없이 1개만 추가


def test_update_person_display_name_same_value_requires_no_confirmation(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session)  # confirmed_question_id 없음

    result = update_person(ctx, person.id, display_name="김철수")

    assert result.display_name == "김철수"


def test_update_person_facts_upsert_same_key_updates_single_row(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session)

    update_person(ctx, person.id, facts=[{"key": "생일", "value": "3월"}])
    update_person(ctx, person.id, facts=[{"key": "생일", "value": "4월"}])

    rows = (
        db_session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person.id)
            .where(PersonFact.key == "생일")
        )
        .scalars()
        .all()
    )
    assert len(rows) == 1
    assert rows[0].value == "4월"
    assert rows[0].confidence == pytest.approx(1.0)


def test_update_person_facts_different_keys_create_two_rows(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session)

    update_person(
        ctx,
        person.id,
        facts=[{"key": "생일", "value": "3월"}, {"key": "취미", "value": "등산"}],
    )

    rows = (
        db_session.execute(select(PersonFact).where(PersonFact.person_id == person.id))
        .scalars()
        .all()
    )
    assert len(rows) == 2
    assert {row.confidence for row in rows} == {1.0}


def test_update_person_other_users_person_raises_person_not_found(db_session):
    person = _make_person(db_session, user_id="other-user", display_name="타인")
    ctx = _ctx(db_session, user_id="local")

    with pytest.raises(PersonNotFound):
        update_person(ctx, person.id, new_alias="별명")


def test_update_person_no_arguments_raises_invalid_value(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        update_person(ctx, person.id)


def test_update_person_writes_one_agent_trace_row(db_session):
    person = _make_person(db_session, display_name="김철수")
    ctx = _ctx(db_session, session_id="trace-update-1")

    update_person(ctx, person.id, new_alias="별명")

    rows = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-update-1")
        ).scalars()
    )
    assert len(rows) == 1
    assert rows[0].tool_name == "update_person"
    assert rows[0].tokens_in == 0
    assert rows[0].tokens_out == 0
