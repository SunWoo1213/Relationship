"""Refs: P3-er S3.3 D5 R9 결정1 -- U5 1단계(후보 검색 어댑터) 테스트.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다. `search_person`(P2-tools) 을 재사용하는지, hints 유도·`s_emb` 정규화·
`embedding_skipped` 처리가 맞는지, DB 행 수가 바뀌지 않는지 확인한다.
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, Person, PersonAlias
from app.er.candidates import search_candidates
from app.tools.context import ToolContext

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


def _ctx(db_session, *, embedder=None, session_id: str = "er-candidates-test") -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder)


def _row_counts(db_session) -> tuple[int, int]:
    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    return persons, aliases


def test_search_candidates_fills_full_alias_list_and_signals(db_session, fake_embedder):
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    _add_alias(db_session, person, "김팀장", embedding=fake_embedder(["김팀장"])[0])

    other = _make_person(db_session, display_name="이영희", relation_tag="가족", hierarchy="상")
    _add_alias(db_session, other, "이모", embedding=fake_embedder(["이모"])[0])

    before = _row_counts(db_session)
    ctx = _ctx(db_session, embedder=fake_embedder)

    result = search_candidates(ctx, "팀장", {"relation_tag": "직장", "hierarchy": "동"})

    assert _row_counts(db_session) == before  # DB 쓰기 없음(트레이스 행 제외 -- persons/aliases 불변)

    by_id = {c.person_id: c for c in result.candidates}
    assert person.id in by_id
    matched = by_id[person.id]
    assert set(matched.aliases) == {"팀장", "김팀장"}
    assert matched.display_name == "김민수"
    assert matched.relation_tag == "직장"
    assert matched.hierarchy == "동"
    assert 0.0 <= matched.s_emb <= 1.0
    assert matched.rule_flags["embedding_skipped"] is False
    assert result.hints == {"relation_tag": "직장", "hierarchy": "동"}


def test_search_candidates_derives_hints_when_none_given(db_session, fake_embedder):
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    ctx = _ctx(db_session, embedder=fake_embedder)

    # "부장님" -> 사전 유도 {relation_tag: 직장, hierarchy: 상} (결정10 표).
    result = search_candidates(ctx, "부장님", None)

    assert result.hints == {"relation_tag": "직장", "hierarchy": "상"}


def test_search_candidates_derives_empty_hints_for_pronoun(db_session, fake_embedder):
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "그사람", embedding=fake_embedder(["그사람"])[0])

    ctx = _ctx(db_session, embedder=fake_embedder)

    result = search_candidates(ctx, "그사람", None)

    assert result.hints == {}


def test_search_candidates_s_emb_zero_when_embedding_skipped(db_session):
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장")  # embedding=None, embedder=None -> skip

    ctx = _ctx(db_session, embedder=None)

    result = search_candidates(ctx, "팀장", {"relation_tag": "직장"})

    by_id = {c.person_id: c for c in result.candidates}
    matched = by_id[person.id]
    assert matched.rule_flags["embedding_skipped"] is True
    assert matched.s_emb == 0.0


def test_search_candidates_does_not_write_persons_or_aliases(db_session, fake_embedder):
    person = _make_person(db_session, display_name="김민수", relation_tag="직장", hierarchy="동")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    before = _row_counts(db_session)
    ctx = _ctx(db_session, embedder=fake_embedder)
    search_candidates(ctx, "팀장", None)
    after = _row_counts(db_session)

    assert before == after


def test_search_candidates_top_k_parameter_does_not_change_search_person_signature(
    db_session, fake_embedder
):
    """`top_k` 인자를 받아도 `search_person`(S3.2 시그니처 고정)에는 넘기지
    않는다 -- 함수가 예외 없이 돈다는 것 자체가 계약 위반이 없다는 증거."""
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, embedder=fake_embedder)

    result = search_candidates(ctx, "팀장", None, top_k=5)

    assert any(c.person_id == person.id for c in result.candidates)
