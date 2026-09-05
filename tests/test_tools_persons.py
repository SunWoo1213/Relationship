"""Refs: P2-tools S3.2 S3.3 D4 D5 원칙1 원칙2 원칙4 -- `search_person` 후보 검색
(신호만 -- 배제·병합·확신도 계산은 P3-er).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다. 이 단위에 `create_person`(U4)이 아직 없으므로 테스트가 직접
`Person`/`PersonAlias` 행을 만든다.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db.models import ALIAS_SOURCES, AgentTrace, Person, PersonAlias
from app.tools.context import ToolContext
from app.tools.persons import search_person
from app.tools.types import InvalidValue

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


def _ctx(db_session, *, session_id: str = "search-test", embedder=None, user_id: str = "local"):
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, embedder=embedder)


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
