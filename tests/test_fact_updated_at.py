"""Refs: FIX-026 FIX-020 S3.1 D14 P6-memory P6-briefing 원칙9 -- 사실 값이
바뀌면 `person_facts.updated_at` 도 갱신되는지(F-20-1 회귀)를 실제 커밋
두 번으로 확인한다.

FIX-020(`7459925`)이 사실 저장을 `INSERT ... ON CONFLICT DO UPDATE` 로
바꾸면서 SQLAlchemy `Column.onupdate`(`app/db/models.py` `updated_at`)가
`set_` 에 적용되지 않아 값이 바뀌어도 `updated_at` 이 멈췄다(검증자 사후
검토 `docs/wiki/fixes/review-FIX-018-025.md` F-20-1, 재현 증거
`docs/wiki/fixes/evidence/20261006-1429-review-fix020-updated-at.txt`).

`now()` 는 트랜잭션 **시작** 시각이라 한 트랜잭션 안의 세이브포인트
롤백(`db_session` 픽스처)으로는 재현할 수 없다(FIX-023 교훈) -- 이 파일은
`db_engine` 으로 직접 `Session` 을 만들어 **실제 커밋을 두 번** 한다.

두 upsert 경로를 각각 확인한다:
- `app.memory.promote._upsert_fact` -- 값이 같으면(action="same") 기존
  ORM 경로도 `.value`/`.confidence` 를 건드리지 않았으므로(아래 "원인"
  참고) `updated_at` 도 그대로였다. 값이 다르면(action="updated") 전진.
- `app.tools.persons.update_person` facts 경로 -- FIX-020 이전 ORM
  코드는 값이 같아도 `existing_fact.value = normalized_value` 를
  **항상** 대입했지만(조건 분기 없음), SQLAlchemy 유닛오브워크는 신규
  값이 기존 값과 같으면(모든 대입 컬럼이 같으면) UPDATE 문 자체를 내지
  않는다 -- 직접 실험으로 확인: `f.value = "등산"`(기존과 같은 값)을
  대입해도 `f in session.dirty` 는 `True` 이지만 `updated_at` 은 전진하지
  않았다. 반대로 `confidence` 만 다른 값으로 바뀌면(값은 같아도)
  `updated_at` 이 전진했다 -- 즉 "이번에 대입하는 모든 컬럼이 기존 값과
  같을 때만" `updated_at` 이 유지된다. `update_person` 은 `value`·
  `confidence` 두 컬럼을 항상 같이 대입하므로, 재현한 FIX-026 수정은 두
  컬럼이 **모두** 같을 때만 `updated_at` 을 유지한다(CASE 조건에 AND).
  이 파일의 아래 테스트들이 그 결론을 실제 커밋으로 고정한다.
"""

from __future__ import annotations

import time
import uuid

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import AgentTrace, Person, PersonFact
from app.memory.promote import _upsert_fact
from app.memory.types import ExtractedFact
from app.settings import DEFAULT_FACT_CONFIDENCE
from app.tools.context import ToolContext
from app.tools.persons import update_person

dbtest = pytest.mark.dbtest
pytestmark = dbtest

#: 커밋 사이 시각 차이를 보장하기 위한 최소 대기(review 증거 스크립트와 같은 값).
_SLEEP = 0.05


def _make_person(engine, *, user_id: str) -> int:
    session = Session(bind=engine)
    try:
        person = Person(
            user_id=user_id, display_name="updated_at검증", relation_tag="친구", hierarchy="동"
        )
        session.add(person)
        session.commit()
        return person.id
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 1) app.memory.promote._upsert_fact
# ---------------------------------------------------------------------------


def test_promote_upsert_fact_advances_updated_at_on_value_change(db_engine) -> None:
    user_id = f"fix026-promote-diff-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)

    session = Session(bind=db_engine)
    try:
        r1 = _upsert_fact(session, person_id, ExtractedFact(key="hobby", value="등산", source_event_ids=[]))
        session.commit()
        assert r1.action == "created"
        t1 = session.execute(
            select(PersonFact.updated_at).where(PersonFact.id == r1.fact_id)
        ).scalar_one()

        time.sleep(_SLEEP)
        r2 = _upsert_fact(
            session, person_id, ExtractedFact(key="hobby", value="클라이밍", source_event_ids=[])
        )
        session.commit()
        t2 = session.execute(
            select(PersonFact.updated_at).where(PersonFact.id == r2.fact_id)
        ).scalar_one()

        assert r2.action == "updated"
        assert r2.fact_id == r1.fact_id
        assert t2 > t1, "값이 바뀌었는데 updated_at 이 전진하지 않았다(FIX-026 F-20-1 회귀)"
    finally:
        session.rollback()
        session.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
        session.execute(delete(Person).where(Person.id == person_id))
        session.commit()
        session.close()


def test_promote_upsert_fact_keeps_updated_at_when_value_unchanged(db_engine) -> None:
    user_id = f"fix026-promote-same-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)

    session = Session(bind=db_engine)
    try:
        r1 = _upsert_fact(session, person_id, ExtractedFact(key="hobby", value="등산", source_event_ids=[]))
        session.commit()
        t1 = session.execute(
            select(PersonFact.updated_at).where(PersonFact.id == r1.fact_id)
        ).scalar_one()

        time.sleep(_SLEEP)
        r2 = _upsert_fact(session, person_id, ExtractedFact(key="hobby", value="등산", source_event_ids=[]))
        session.commit()
        t2 = session.execute(
            select(PersonFact.updated_at).where(PersonFact.id == r2.fact_id)
        ).scalar_one()

        assert r2.action == "same"
        assert t2 == t1, "값이 같은데도 updated_at 이 전진했다(기존 ORM 경로와 다른 동작)"
    finally:
        session.rollback()
        session.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
        session.execute(delete(Person).where(Person.id == person_id))
        session.commit()
        session.close()


# ---------------------------------------------------------------------------
# 2) app.tools.persons.update_person (facts 경로)
# ---------------------------------------------------------------------------


def test_update_person_facts_advances_updated_at_on_value_change(db_engine) -> None:
    user_id = f"fix026-updperson-diff-{uuid.uuid4().hex}"
    session_id = f"fix026-updperson-diff-session-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)

    session = Session(bind=db_engine)
    try:
        ctx = ToolContext(session=session, session_id=session_id, user_id=user_id)
        update_person(ctx, person_id, facts=[{"key": "hobby", "value": "등산"}])
        session.commit()
        t1 = session.execute(
            select(PersonFact.updated_at)
            .where(PersonFact.person_id == person_id)
            .where(PersonFact.key == "hobby")
        ).scalar_one()

        time.sleep(_SLEEP)
        update_person(ctx, person_id, facts=[{"key": "hobby", "value": "클라이밍"}])
        session.commit()
        t2 = session.execute(
            select(PersonFact.updated_at)
            .where(PersonFact.person_id == person_id)
            .where(PersonFact.key == "hobby")
        ).scalar_one()

        assert t2 > t1, "값이 바뀌었는데 updated_at 이 전진하지 않았다(FIX-026 F-20-1 회귀)"
    finally:
        session.rollback()
        session.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
        session.execute(delete(AgentTrace).where(AgentTrace.session_id == session_id))
        session.execute(delete(Person).where(Person.id == person_id))
        session.commit()
        session.close()


def test_update_person_facts_keeps_updated_at_when_value_and_confidence_unchanged(db_engine) -> None:
    """FIX-020 이전 ORM 코드는 값이 같아도 `.value`/`.confidence` 를 항상
    대입했지만(분기 없음), SQLAlchemy 가 대입 전후 값이 모두 같으면 UPDATE
    문 자체를 내지 않아 `updated_at` 이 그대로였다(모듈 docstring 참고,
    `scratchpad/check_orm_same_value.py` 로 확인). `update_person` 은
    `value`·`confidence` 를 항상 같이 쓰므로(이번 호출의 `confidence` 는
    항상 `DEFAULT_FACT_CONFIDENCE`), 두 번째 호출에서 두 컬럼 모두 이전과
    같으면 `updated_at` 이 유지되어야 같은 동작이다."""
    user_id = f"fix026-updperson-same-{uuid.uuid4().hex}"
    session_id = f"fix026-updperson-same-session-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)

    session = Session(bind=db_engine)
    try:
        ctx = ToolContext(session=session, session_id=session_id, user_id=user_id)
        update_person(ctx, person_id, facts=[{"key": "hobby", "value": "등산"}])
        session.commit()
        row1 = session.execute(
            select(PersonFact.updated_at, PersonFact.confidence)
            .where(PersonFact.person_id == person_id)
            .where(PersonFact.key == "hobby")
        ).one()
        assert row1.confidence == DEFAULT_FACT_CONFIDENCE

        time.sleep(_SLEEP)
        update_person(ctx, person_id, facts=[{"key": "hobby", "value": "등산"}])
        session.commit()
        row2 = session.execute(
            select(PersonFact.updated_at, PersonFact.confidence)
            .where(PersonFact.person_id == person_id)
            .where(PersonFact.key == "hobby")
        ).one()

        assert row2.updated_at == row1.updated_at, (
            "값·confidence 가 모두 같은데도 updated_at 이 전진했다(기존 ORM 경로와 다른 동작)"
        )
    finally:
        session.rollback()
        session.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
        session.execute(delete(AgentTrace).where(AgentTrace.session_id == session_id))
        session.execute(delete(Person).where(Person.id == person_id))
        session.commit()
        session.close()
