"""Refs: P2-tools 결정2 결정8 -- app.db.session 의 세션/엔진 계약을 실 DB로 검증.

로컬 PostgreSQL(POSTGRES_PORT 기본 5433)이 필요하다. 접속 실패 시
`db_engine`/`db_session` 픽스처가 skip 한다(`-rs` 로 사유가 보인다).
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.db.models import Person
from app.db.session import get_engine, session_scope

pytestmark = pytest.mark.dbtest

# 두 테스트(삽입/부재확인)가 서로 다른 db_session(=다른 트랜잭션)을 쓰므로
# 실행 순서에 의존하지 않도록 모듈 레벨 고정 문자열로 공유한다.
_ROLLBACK_FIXTURE_NAME = f"u1-db-session-rollback-{uuid.uuid4().hex}"
_SESSION_SCOPE_NAME = f"u1-session-scope-rollback-{uuid.uuid4().hex}"


def test_db_session_insert_and_flush_is_visible_in_same_session(db_session):
    """(a) db_session 으로 persons 에 행 1개 insert+flush → 같은 세션에서 조회됨."""
    person = Person(
        user_id="test-u1",
        display_name=_ROLLBACK_FIXTURE_NAME,
        relation_tag="지인",
        hierarchy="동",
    )
    db_session.add(person)
    db_session.flush()

    found = db_session.execute(
        select(Person).where(Person.display_name == _ROLLBACK_FIXTURE_NAME)
    ).scalar_one()
    assert found.id is not None
    assert found.display_name == _ROLLBACK_FIXTURE_NAME


def test_db_session_rolls_back_between_tests(db_session):
    """(b) 다음 테스트(새 db_session)에서는 그 행이 없다 -- 롤백 확인."""
    found = db_session.execute(
        select(Person).where(Person.display_name == _ROLLBACK_FIXTURE_NAME)
    ).scalar_one_or_none()
    assert found is None


def test_session_scope_rolls_back_on_exception(db_engine):
    """(c) session_scope() 가 예외 시 rollback 하는지 -- 실 DB, 별도 세션에서 부재 확인."""

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with session_scope() as session:
            session.add(
                Person(
                    user_id="test-u1",
                    display_name=_SESSION_SCOPE_NAME,
                    relation_tag="지인",
                    hierarchy="동",
                )
            )
            session.flush()
            raise _Boom("boom")

    with session_scope() as verify_session:
        found = verify_session.execute(
            select(Person).where(Person.display_name == _SESSION_SCOPE_NAME)
        ).scalar_one_or_none()
        assert found is None


def test_get_engine_returns_same_object_on_repeat_calls(db_engine):
    """(d) get_engine() 이 두 번 호출해도 같은 객체."""
    assert get_engine() is get_engine()
