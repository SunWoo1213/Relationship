"""Refs: P8-frontend U1 S3.1 S3.5 원칙9 -- 읽기 전용 조회 함수(인물 목록·카드).

DB 를 **읽기만** 한다: INSERT/UPDATE/DELETE 없음, `agent_traces` 기록 없음
(툴이 아니라 화면용 조회이므로 `@traced` 를 쓰지 않는다 -- 01-plan U1).
소유 확인은 `app.tools.persons._owned_person` 을 그대로 재사용한다(보안 판정
로직을 두 곳에 두지 않는다. 밑줄 이름을 같은 패키지 내부에서 가져다 쓰는
것이며 공개 승격은 하지 않았다). 없는 인물·다른 사용자 인물은 모두
`PersonNotFound` -> `app/main.py` 의 공통 404 로 같은 응답이 된다.

집계는 전부 쿼리로 한다(N+1 금지): 목록은 `LEFT JOIN events GROUP BY`,
사실의 `source_count` 는 `LEFT JOIN fact_sources GROUP BY`.
"""

from __future__ import annotations

from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    PersonBasicOut,
    PersonCardOut,
    PersonFactOut,
    PersonListItemOut,
    PersonPatternOut,
    TimelineEventOut,
    UpcomingScheduleOut,
)
from app.db.models import Event, FactSource, Person, PersonAlias, PersonFact, Schedule
from app.settings import PATTERN_KEY_PREFIX
from app.tools.persons import _owned_person

#: 카드 타임라인 최대 건수. 카드 화면은 "최근 무슨 일이 있었나"를 한눈에
#: 보여 주는 용도이고 전체 이력 페이지가 아니다(화면 3개 고정, 원칙5).
#: 모바일 한 화면 스크롤로 훑을 수 있는 20건이면 충분하고 응답 크기도
#: 작게 유지된다. 더 오래된 이벤트는 승격된 사실(facts)·패턴이 요약한다.
TIMELINE_LIMIT = 20

#: 카드에 보일 다가오는 일정 최대 건수. 카드 응답 크기를 묶기 위한 상한이며
#: 가장 가까운 일정부터 채운다(과거 일정은 제외). 24시간 브리핑 범위와는 무관하다.
UPCOMING_SCHEDULES_LIMIT = 10


def list_persons(session: Session, user_id: str) -> list[PersonListItemOut]:
    """사용자의 인물 목록. `last_contact_at` 내림차순, 값이 없는 인물은 뒤,
    동률·null 끼리는 `id` 오름차순(결정적 순서)."""
    last_contact = func.max(Event.occurred_at).label("last_contact_at")
    rows = session.execute(
        select(Person, last_contact)
        .outerjoin(Event, Event.person_id == Person.id)
        .where(Person.user_id == user_id)
        .group_by(Person.id)
        .order_by(last_contact.desc().nulls_last(), Person.id.asc())
    ).all()
    return [
        PersonListItemOut(
            id=p.id,
            display_name=p.display_name,
            relation_tag=p.relation_tag,
            hierarchy=p.hierarchy,
            last_contact_at=lc,
        )
        for p, lc in rows
    ]


def get_person_card(session: Session, user_id: str, person_id: int, now: datetime) -> PersonCardOut:
    """인물 카드. 없거나 다른 사용자 소유면 `PersonNotFound`."""
    person = _owned_person(session, person_id, user_id)

    # 정렬은 DB 콜레이션에 맡기지 않고 `_person_out` 과 같은 Python `sorted()`
    # (코드포인트 순)로 한다. 같은 인물의 별칭 순서가 API 마다 달라지지 않게.
    aliases = sorted(
        session.execute(
            select(PersonAlias.alias).where(PersonAlias.person_id == person.id)
        )
        .scalars()
        .all()
    )

    last_contact_at = cast(
        "datetime | None",
        session.execute(
            select(func.max(Event.occurred_at)).where(Event.person_id == person.id)
        ).scalar_one(),
    )

    source_count = func.count(FactSource.event_id).label("source_count")
    fact_rows = session.execute(
        select(PersonFact, source_count)
        .outerjoin(FactSource, FactSource.fact_id == PersonFact.id)
        .where(PersonFact.person_id == person.id)
        .group_by(PersonFact.id)
        .order_by(PersonFact.updated_at.desc(), PersonFact.id.asc())
    ).all()
    facts: list[PersonFactOut] = []
    patterns: list[PersonPatternOut] = []
    for fact, count in fact_rows:
        if fact.key.startswith(PATTERN_KEY_PREFIX):
            patterns.append(
                PersonPatternOut(id=fact.id, key=fact.key, value=fact.value, source_count=count)
            )
        else:
            facts.append(
                PersonFactOut(
                    id=fact.id,
                    key=fact.key,
                    value=fact.value,
                    updated_at=fact.updated_at,
                    source_count=count,
                )
            )

    # raw_utterance 는 컬럼 자체를 고르지 않는다.
    timeline = [
        TimelineEventOut(id=i, type=t, content=c, occurred_at=o)
        for i, t, c, o in session.execute(
            select(Event.id, Event.type, Event.content, Event.occurred_at)
            .where(Event.person_id == person.id)
            .order_by(Event.occurred_at.desc(), Event.id.desc())
            .limit(TIMELINE_LIMIT)
        ).all()
    ]

    upcoming = [
        UpcomingScheduleOut(id=i, title=t, scheduled_at=s, briefed_at=b)
        for i, t, s, b in session.execute(
            select(Schedule.id, Schedule.title, Schedule.scheduled_at, Schedule.briefed_at)
            .where(Schedule.person_id == person.id)
            .where(Schedule.scheduled_at >= now)
            .order_by(Schedule.scheduled_at.asc(), Schedule.id.asc())
            .limit(UPCOMING_SCHEDULES_LIMIT)
        ).all()
    ]

    return PersonCardOut(
        person=PersonBasicOut(
            id=person.id,
            display_name=person.display_name,
            relation_tag=person.relation_tag,
            hierarchy=person.hierarchy,
        ),
        aliases=aliases,
        last_contact_at=last_contact_at,
        facts=facts,
        patterns=patterns,
        timeline=timeline,
        upcoming_schedules=upcoming,
    )
