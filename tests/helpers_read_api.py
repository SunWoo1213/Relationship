"""Refs: P8-frontend U3 R-U2-3 원칙9 -- 읽기 전용 조회 API 의 "쓰기 0" 을 값으로 단언하는 공통 헬퍼.

판정표 7행 "DB 쓰기 0 · `agent_traces` 0 · `schedules.briefed_at`·
`persons.updated_at` 변화 0" 을 행 수만이 아니라 **값**으로 비교한다.
스냅샷은 (1) 8개 테이블(`agent_traces`·`persons`·`person_aliases`·
`person_facts`·`fact_sources`·`events`·`schedules`·`pending_questions`)의 행 수,
(2) `schedules.briefed_at` 전체 값(id 순), (3) `persons.updated_at` 전체 값(id 순)이다.
행 수가 같아도 UPDATE 로 `briefed_at`·`updated_at` 이 바뀌면 달라진다.

주의: 같은 트랜잭션 안에서 `now()` 는 고정이다. 테스트 데이터의 `updated_at`·
`briefed_at` 을 트랜잭션 시작 시각이 아닌 **과거 값으로 명시**해야 UPDATE
(`onupdate=now()`)가 값 변화로 드러난다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    AgentTrace,
    Event,
    FactSource,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)

_COUNTED_MODELS = (
    AgentTrace,
    Person,
    PersonAlias,
    PersonFact,
    FactSource,
    Event,
    Schedule,
    PendingQuestion,
)


@dataclass(frozen=True)
class DbSnapshot:
    counts: tuple[int, ...]
    briefed_at: tuple[tuple[int, datetime | None], ...]
    persons_updated_at: tuple[tuple[int, datetime], ...]


def snapshot_db(session: Session) -> DbSnapshot:
    """조회 전후 비교용 스냅샷. 세션을 flush 한 뒤 읽는다."""
    session.flush()
    counts = tuple(
        session.execute(select(func.count()).select_from(model)).scalar_one()
        for model in _COUNTED_MODELS
    )
    briefed = tuple(
        (i, b) for i, b in session.execute(select(Schedule.id, Schedule.briefed_at).order_by(Schedule.id)).all()
    )
    updated = tuple(
        (i, u) for i, u in session.execute(select(Person.id, Person.updated_at).order_by(Person.id)).all()
    )
    return DbSnapshot(counts=counts, briefed_at=briefed, persons_updated_at=updated)


def assert_no_writes(before: DbSnapshot, after: DbSnapshot) -> None:
    """행 수 8개·`briefed_at` 전체·`persons.updated_at` 전체가 모두 같아야 한다."""
    assert after.counts == before.counts, "행 수가 달라졌다(쓰기 또는 trace 발생)"
    assert after.briefed_at == before.briefed_at, "schedules.briefed_at 이 바뀌었다"
    assert after.persons_updated_at == before.persons_updated_at, "persons.updated_at 이 바뀌었다"
