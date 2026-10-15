"""Refs: P8-frontend U1 U2 U3 S3.1 S3.4 S3.5 S3.6 R8 R12 D2 원칙9 -- 읽기 전용 조회
함수(인물 목록·카드·원문·근거·브리핑·대기 질문 조회).

대기 질문 목록은 새 조회 로직을 두지 않고 `app.tools.questions.list_pending`
을 라우트가 그대로 부른다(`routes.read_pending_questions`). 브리핑 조회
(`list_briefings`)는 `agent_traces` 의 `briefing_compose` 행을 일정마다 최근
1건씩 읽을 뿐 `get_briefing` 툴을 부르지 않는다(결정 G).

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

from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy import BigInteger, func, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    BriefingPersonOut,
    BriefingRecordOut,
    BriefingScheduleOut,
    EventRawOut,
    FactBriefOut,
    FactSourceEventOut,
    FactSourcesOut,
    PersonBasicOut,
    PersonCardOut,
    PersonFactOut,
    PersonListItemOut,
    PersonPatternOut,
    TimelineEventOut,
    UpcomingScheduleOut,
)
from app.briefing.types import BRIEFING_TRACE_TOOL_NAME, STEP_BRIEFING_COMPOSE
from app.db.models import AgentTrace, Event, FactSource, Person, PersonAlias, PersonFact, Schedule
from app.settings import PATTERN_KEY_PREFIX
from app.tools.persons import _owned_person
from app.tools.types import PersonNotFound, ScheduleNotFound

#: 카드 타임라인 최대 건수. 카드 화면은 "최근 무슨 일이 있었나"를 한눈에
#: 보여 주는 용도이고 전체 이력 페이지가 아니다(화면 3개 고정, 원칙5).
#: 모바일 한 화면 스크롤로 훑을 수 있는 20건이면 충분하고 응답 크기도
#: 작게 유지된다. 더 오래된 이벤트는 승격된 사실(facts)·패턴이 요약한다.
TIMELINE_LIMIT = 20

#: 카드에 보일 다가오는 일정 최대 건수. 카드 응답 크기를 묶기 위한 상한이며
#: 가장 가까운 일정부터 채운다(과거 일정은 제외). 24시간 브리핑 범위와는 무관하다.
UPCOMING_SCHEDULES_LIMIT = 10


#: 사실 하나의 근거 원문 최대 건수. 승격은 인물의 미승격 이벤트
#: `MEMORY_PROMOTE_MAX_EVENTS`(20)건 안에서 이뤄지므로 한 사실의 근거는
#: 보통 그 안이다. 같은 20건이면 "근거 보기" 한 번에 원문 전체가 오가도
#: 응답이 작고, 패턴 사실(1년 내 같은 type 반복)이 더 많은 근거를 가져도
#: 가장 최근 20건이면 화면 목적(왜 그렇게 기록했나)에 충분하다.
FACT_SOURCES_LIMIT = 20

#: 브리핑 목록이 돌아보는 기간(일). 대상 일정은 `scheduled_at >= now - 7일`
#: (미래 쪽 상한 없음). 스케줄러의 리드 창(`BRIEFING_LEAD_HOURS=24`)보다 넓어야
#: 이미 지난 일정의 브리핑을 돌아볼 수 있고, 데모 DB 에서 화면이 길어지지
#: 않는 값이다(사용자 확정 2026-10-12). `schedule_id` 를 지정한 조회에는
#: 적용하지 않는다(푸시 알림 클릭으로 들어오는 특정 일정 조회).
BRIEFINGS_LOOKBACK_DAYS = 7

#: 브리핑 목록 최대 건수. 기간으로 이미 좁혀지므로 안전장치이고
#: `TIMELINE_LIMIT`·`FACT_SOURCES_LIMIT` 와 같은 20 이다(사용자 확정 2026-10-12).
BRIEFINGS_LIMIT = 20


def get_event_raw(session: Session, user_id: str, event_id: int) -> EventRawOut:
    """이벤트 원문. `events -> persons` 조인에 `persons.user_id` 를 건다.
    없거나 남의 것이면 `PersonNotFound`(공통 404, 존재 누설 없음)."""
    row = session.execute(
        select(
            Event.id,
            Event.person_id,
            Event.type,
            Event.content,
            Event.occurred_at,
            Event.raw_utterance,
        )
        .join(Person, Person.id == Event.person_id)
        .where(Event.id == event_id)
        .where(Person.user_id == user_id)
    ).one_or_none()
    if row is None:
        raise PersonNotFound("event_not_found")
    return EventRawOut(
        event_id=row[0],
        person_id=row[1],
        type=row[2],
        content=row[3],
        occurred_at=row[4],
        raw_utterance=row[5],
    )


def get_fact_sources(
    session: Session, user_id: str, person_id: int, fact_id: int
) -> FactSourcesOut:
    """사실의 근거 원문. 사실은 `person_facts.person_id = person_id` 이고
    그 인물이 `user_id` 소유일 때만 조회된다(다른 인물의 사실 id 를 경로에
    끼운 넘겨짚기 차단). 아니면 `PersonNotFound`(공통 404)."""
    fact = session.execute(
        select(PersonFact.id, PersonFact.key, PersonFact.value)
        .join(Person, Person.id == PersonFact.person_id)
        .where(PersonFact.id == fact_id)
        .where(PersonFact.person_id == person_id)
        .where(Person.user_id == user_id)
    ).one_or_none()
    if fact is None:
        raise PersonNotFound("fact_not_found")
    rows = session.execute(
        select(
            Event.id,
            Event.type,
            Event.content,
            Event.occurred_at,
            Event.raw_utterance,
        )
        .join(FactSource, FactSource.event_id == Event.id)
        .where(FactSource.fact_id == fact.id)
        .where(Event.person_id == person_id)  # 다른 인물 이벤트가 섞여도 나가지 않는다
        .order_by(Event.occurred_at.desc(), Event.id.desc())
        .limit(FACT_SOURCES_LIMIT)
    ).all()
    return FactSourcesOut(
        fact=FactBriefOut(id=fact[0], key=fact[1], value=fact[2]),
        sources=[
            FactSourceEventOut(
                event_id=i, type=t, content=c, occurred_at=o, raw_utterance=r
            )
            for i, t, c, o, r in rows
        ],
    )


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


def list_briefings(
    session: Session,
    user_id: str,
    now: datetime,
    schedule_id: int | None = None,
) -> list[BriefingRecordOut]:
    """저장된 브리핑 목록(결정 G). 원천은 `agent_traces` 중
    `tool_name='briefing' AND step='briefing_compose'` 행이다 -- 같은
    `tool_name` 의 `briefing_run`·`briefing_error` 행은 섞이지 않는다(R-9).

    일정마다 **가장 최근 1행**(`created_at` 내림차순, 동률이면 `id` 내림차순)만
    쓴다. `output->>'schedule_id'`·`output->>'person_id'` 로 일정·인물을 잇고
    `persons.user_id = user_id` 를 건다. 정렬은 `schedules.scheduled_at`
    내림차순 -> `schedules.id` 내림차순, 상한 `BRIEFINGS_LIMIT`.

    `schedule_id=None` 이면 `scheduled_at >= now - BRIEFINGS_LOOKBACK_DAYS` 인
    일정만(미래는 상한 없음). 지정하면 기간 상수를 적용하지 않고 그 일정만
    조회한다 -- 일정이 없거나 다른 사용자 것이면 `ScheduleNotFound`(공통 404),
    있는데 compose trace 가 없으면 빈 목록.

    응답에는 원문(`raw_utterance`)을 담는 필드가 없다 -- `output` 의 근거는
    `basis{fact_keys, event_ids}` 로만 나간다."""
    if schedule_id is not None:
        owned = session.execute(
            select(Schedule.id)
            .join(Person, Person.id == Schedule.person_id)
            .where(Schedule.id == schedule_id)
            .where(Person.user_id == user_id)
        ).one_or_none()
        if owned is None:
            raise ScheduleNotFound("schedule_not_found")

    # output 은 JSONB 라 키 접근(`->>`)이 가능하지만 모델 타입이 object 라 Any 로 푼다.
    trace_output = cast("Any", AgentTrace.output)
    out_schedule_id = trace_output["schedule_id"].astext.cast(BigInteger)
    out_person_id = trace_output["person_id"].astext.cast(BigInteger)
    ranked = (
        select(
            AgentTrace.id.label("trace_id"),
            AgentTrace.created_at.label("generated_at"),
            AgentTrace.output.label("output"),
            out_schedule_id.label("sid"),
            out_person_id.label("pid"),
            func.row_number()
            .over(
                partition_by=out_schedule_id,
                order_by=(AgentTrace.created_at.desc(), AgentTrace.id.desc()),
            )
            .label("rn"),
        )
        .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
        .where(AgentTrace.step == STEP_BRIEFING_COMPOSE)
        .subquery()
    )

    query = (
        select(
            ranked.c.trace_id,
            ranked.c.generated_at,
            ranked.c.output,
            Schedule.id,
            Schedule.title,
            Schedule.scheduled_at,
            Person.id,
            Person.display_name,
        )
        .join(Schedule, Schedule.id == ranked.c.sid)
        # R-U3-2 -- trace 의 person_id 가 그 일정의 실제 인물과 같아야 한다(손으로 조작한
        # trace 로 남의 일정 제목·시각이 내 목록에 섞이는 틈을 막는 방어 조건).
        .join(Person, (Person.id == ranked.c.pid) & (Person.id == Schedule.person_id))
        .where(ranked.c.rn == 1)
        .where(Person.user_id == user_id)
    )
    if schedule_id is not None:
        query = query.where(Schedule.id == schedule_id)
    else:
        query = query.where(Schedule.scheduled_at >= now - timedelta(days=BRIEFINGS_LOOKBACK_DAYS))
    rows = session.execute(
        query.order_by(Schedule.scheduled_at.desc(), Schedule.id.desc()).limit(BRIEFINGS_LIMIT)
    ).all()

    return [
        BriefingRecordOut(
            schedule=BriefingScheduleOut(id=s_id, title=title, scheduled_at=scheduled_at),
            person=BriefingPersonOut(id=p_id, display_name=display_name),
            generated_at=generated_at,
            composer=output["composer"],
            pattern_sentences=output.get("pattern_sentences") or [],
            lines=output.get("lines") or [],
            suggestion=output.get("suggestion"),
            push=output["push"],
            trace_id=trace_id,
        )
        for trace_id, generated_at, output, s_id, title, scheduled_at, p_id, display_name in rows
    ]
