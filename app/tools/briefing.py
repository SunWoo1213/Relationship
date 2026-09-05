"""Refs: P2-tools R10 S3.2 S3.6 원칙7 -- `get_briefing`: 브리핑 자료 조회.

이 모듈은 만남 직전 필요한 **자료를 모으는 것까지**만 한다(01-plan 결정 7).
문장화·요약·"한 줄 행동 제안"·감정/고민 언급·주기 작업(1분)·
`POST /briefings/run` 은 전부 **P6-briefing**(S3.6 "적용: P6-briefing,
P7-push")이고, 여기에는 **LLM 호출이 없다** -- 원칙7 경계 문장 "브리핑의
'제안'은 기록된 사실에서 도출되는 한 줄 행동 제안으로 한정한다. 감정·고민에
대한 대화는 하지 않는다"는 P6-briefing 이 지킬 제약이며, P2 는 그 제안조차
만들지 않는다(01-plan 138행). 반환값은 `BriefingOut.to_dict()` 가 만드는
키 집합(`person`/`aliases`/`facts`/`recent_events`/`upcoming_schedules`/
`schedule`/`generated_at`) 뿐이고 `summary`/`suggestion`/`advice` 같은
문장형 키는 없다.

## 각 필드의 구성

- `person`/`aliases`: `_owned_person` 으로 소유를 확인한 뒤 `_person_out`
  이 만드는 `PersonOut`(별칭 정렬 포함)과 그 별칭 목록을 그대로 쓴다
  (`app/tools/persons.py` 재사용 -- 소유 확인·별칭 조회 로직을 중복
  구현하지 않는다).
- `facts`: `person_facts` 전부(개수 제한 없음) `{key, value, confidence,
  updated_at}`, `updated_at DESC`.
- `recent_events`: `events` 중 `occurred_at DESC` 상위
  `settings.BRIEFING_RECENT_EVENTS`(5)건. **`raw_utterance` 는 포함하지
  않는다** -- `EventOut` 자체가 그 컬럼을 담지 않으므로(`app/tools/types.py`
  docstring "원문 보존은 DB 컬럼·`fact_sources` 근거 추적의 일이지, 툴 반환
  DTO 의 일이 아니다") 이 함수가 따로 걸러낼 필요가 없다. 이것은 trace
  절단(`TRACE_MAX_STRING`)과는 별개로, 브리핑 자료 자체에 원문 전체를
  싣지 않는다는 명시적 결정이다.
- `upcoming_schedules`: `schedules` 중 `scheduled_at >= generated_at`
  (과거 제외) `ASC` 상위 `settings.BRIEFING_UPCOMING_SCHEDULES`(3)건.
- `schedule`: `schedule_id` 가 주어졌을 때만 채운다. 그 일정이 없거나
  `person_id` 가 다르면(따라서 다른 인물 소유) `ScheduleNotFound` -- 어느
  일정의 브리핑인지 모르는 채로 `briefed_at` 을 남기지 않는다.
- `generated_at`: 이 호출 전체가 쓰는 `ctx.now()` 단일 값(아래 참고).

## `briefed_at` 기록은 `schedule_id` 가 있을 때만 (S3.2 "briefed_at 기록"의
최소 해석)

`schedule_id` 가 없으면 이 함수는 **어떤 행도 쓰지 않는다**(읽기 전용) --
어느 일정을 브리핑했는지 모르는 채로 표시를 남기면 나중에 "언제 브리핑했는지"
를 되짚을 수 없다(원칙9 와 같은 근거 보존 이유). `schedule_id` 가 있으면 그
일정에만 `briefed_at = ctx.now()` 를 **덮어쓴다**(이미 값이 있어도 최신
브리핑 시각으로 갱신 -- 같은 일정을 여러 번 브리핑할 수 있고, 마지막으로
언제 브리핑했는지가 필요한 정보다. 주기 작업의 "이미 브리핑한 일정은
건너뛴다" 판단은 P6-briefing 이 이 컬럼을 보고 내린다).

`ctx.now()` 는 이 함수 안에서 **한 번만** 호출해 `generated_at`·
`upcoming_schedules` 필터·`briefed_at` 기록에 전부 재사용한다 -- 같은
브리핑 호출 안에서 "지금"이 여러 값으로 흩어지지 않게 한다.
"""

from __future__ import annotations

from sqlalchemy import select

from app.db.models import Event, PersonFact, Schedule
from app.settings import BRIEFING_RECENT_EVENTS, BRIEFING_UPCOMING_SCHEDULES
from app.tools.context import ToolContext, traced
from app.tools.persons import _owned_person, _person_out
from app.tools.types import BriefingOut, EventOut, ScheduleNotFound, ScheduleOut


@traced("get_briefing")
def get_briefing(
    ctx: ToolContext, person_id: int, schedule_id: int | None = None
) -> BriefingOut:
    """S3.2 시그니처: `(person_id, schedule_id?) -> Briefing`.

    `person_id` 가 없거나 다른 `user_id` 소유면 `PersonNotFound`
    (`_owned_person`). 문장화·제안·LLM 호출 없음(모듈 docstring). `schedule_id`
    가 주어졌을 때만 그 일정에 `briefed_at` 을 기록한다 -- 그 밖의 모든
    조회는 읽기 전용이다.
    """
    person = _owned_person(ctx.session, person_id, ctx.user_id)
    person_out = _person_out(ctx.session, person)

    now = ctx.now()

    fact_rows = (
        ctx.session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person.id)
            .order_by(PersonFact.updated_at.desc())
        )
        .scalars()
        .all()
    )
    facts = [
        {
            "key": fact.key,
            "value": fact.value,
            "confidence": fact.confidence,
            "updated_at": fact.updated_at.isoformat(),
        }
        for fact in fact_rows
    ]

    event_rows = (
        ctx.session.execute(
            select(Event)
            .where(Event.person_id == person.id)
            .order_by(Event.occurred_at.desc())
            .limit(BRIEFING_RECENT_EVENTS)
        )
        .scalars()
        .all()
    )
    recent_events = [
        EventOut(
            id=event.id,
            person_id=event.person_id,
            type=event.type,
            content=event.content,
            occurred_at=event.occurred_at,
            created_at=event.created_at,
        )
        for event in event_rows
    ]

    upcoming_rows = (
        ctx.session.execute(
            select(Schedule)
            .where(Schedule.person_id == person.id)
            .where(Schedule.scheduled_at >= now)
            .order_by(Schedule.scheduled_at.asc())
            .limit(BRIEFING_UPCOMING_SCHEDULES)
        )
        .scalars()
        .all()
    )
    upcoming_schedules = [
        ScheduleOut(
            id=schedule.id,
            person_id=schedule.person_id,
            title=schedule.title,
            scheduled_at=schedule.scheduled_at,
            briefed_at=schedule.briefed_at,
        )
        for schedule in upcoming_rows
    ]

    schedule_out: ScheduleOut | None = None
    if schedule_id is not None:
        schedule_row = ctx.session.get(Schedule, schedule_id)
        if schedule_row is None or schedule_row.person_id != person.id:
            raise ScheduleNotFound("schedule_not_found")

        schedule_row.briefed_at = now
        ctx.session.flush()

        schedule_out = ScheduleOut(
            id=schedule_row.id,
            person_id=schedule_row.person_id,
            title=schedule_row.title,
            scheduled_at=schedule_row.scheduled_at,
            briefed_at=schedule_row.briefed_at,
        )

    return BriefingOut(
        person=person_out,
        generated_at=now,
        aliases=list(person_out.aliases),
        facts=facts,
        recent_events=recent_events,
        upcoming_schedules=upcoming_schedules,
        schedule=schedule_out,
    )
