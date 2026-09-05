"""Refs: P2-tools R10 S3.1 S3.2 -- `add_event`·`add_schedule`: 에피소드 기록.

이 모듈은 `events`/`schedules` 두 테이블에 원문을 그대로 적는 것까지만
한다. **패턴 감지(`pattern:{type}`)·시맨틱 승격(`person_facts` upsert)·
`fact_sources` 채우기는 여기서 하지 않는다** -- 01-plan 49행 "`add_event`
는 승격·패턴을 트리거하지 않는다"(원칙6·D9 는 P6-memory 의 몫이다). 이
함수가 끝나면 events 행 하나가 늘어날 뿐, person_facts 는 절대 변하지
않는다(회귀 테스트로 방어).

## UTC 정규화 결정 (미결 3)

`occurred_at`/`scheduled_at` 컬럼은 `timestamptz` 이므로 어떤 aware
datetime 을 넘겨도(오프셋이 붙어 있으면) PostgreSQL 이 같은 순간(instant)
으로 저장한다 -- naive 만 아니면 그대로 넘겨도 DB 단에서는 정확하다.
그럼에도 이 모듈은 **애플리케이션에서 UTC 로 정규화한 뒤 저장하고, 반환
DTO 도 그 UTC 값을 그대로 돌려준다**. 이유:

1. `@traced` 가 `to_jsonable()` 로 `output` 을 `agent_traces` 에 남길 때
   `isoformat()` 문자열이 되는데, 호출자가 KST/UTC 를 섞어 보내면 같은
   순간이 서로 다른 오프셋 문자열로 trace 에 남아 사람이 훑어볼 때
   헷갈린다(원칙9 "판정 근거를 남긴다"의 가독성).
2. `EventOut`/`ScheduleOut` 을 그대로 비교하는 테스트·향후 P6-memory 의
   "최근 90일" 윈도 계산이 항상 같은 기준(UTC)에서 이루어지게 한다 --
   호출자가 섞어 보낸 오프셋을 매번 변환해야 하는 부담을 이 계층에서
   끝낸다.
3. `datetime` 이 아니거나 naive(`tzinfo is None` 또는 `utcoffset() is
   None`)면 **조용히 UTC 로 가정하지 않고** `InvalidValue` 로 거절한다
   (미결 3 "조용한 UTC 가정 금지"). 상대 시각("어제 저녁") 해석은
   P5-loop 의 책임이며 이 모듈은 이미 절대·aware 인 값만 받는다.

## 소유 확인

`person_id` 는 항상 `app.tools.persons._owned_person` 으로 `ctx.user_id`
소유인지 먼저 확인한다(security.md §5) -- 없거나 다른 사용자 소유면
`PersonNotFound`. 이 helper 는 `update_person` 과 공유하는 단일 출처다
(중복 구현 금지, 01-plan U5 지시).
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import EVENT_TYPES, Event, Schedule
from app.tools.context import ToolContext, traced
from app.tools.persons import _owned_person
from app.tools.types import EventOut, InvalidValue, ScheduleOut


def _require_aware(value: object, name: str) -> datetime:
    """`value` 가 tz-aware `datetime` 인지 검사하고 UTC 로 정규화해 돌려준다.

    naive(`tzinfo is None` 또는 `utcoffset() is None`)이거나 `datetime` 이
    아니면 `InvalidValue` -- "조용한 UTC 가정 금지"(01-plan 미결 3).
    """
    if not isinstance(value, datetime):
        raise InvalidValue(f"{name} must be a tz-aware datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidValue(f"{name} must be tz-aware (naive datetime rejected)")
    return value.astimezone(timezone.utc)


def _require_text(value: object, name: str) -> str:
    """비어 있지 않은 문자열인지 검사하고 strip 한 값을 돌려준다."""
    if not isinstance(value, str) or not value.strip():
        raise InvalidValue(f"{name} must not be empty")
    return value.strip()


@traced("add_event")
def add_event(
    ctx: ToolContext,
    person_id: int,
    type: str,  # noqa: A002 -- CLAUDE.md 툴 7종 표의 매개변수 이름 그대로(내장 가림은 이 함수 안에서만)
    content: str,
    occurred_at: datetime,
    raw_utterance: str,
) -> EventOut:
    """S3.2 시그니처: `(person_id, type, content, occurred_at, raw_utterance) -> Event`.

    `type` 은 `EVENT_TYPES`(7값) 안이어야 한다. `content`·`raw_utterance`
    는 비어 있지 않아야 하며, `raw_utterance` 는 요약·가공 없이 그대로
    저장한다(원칙9 "원문 보존" -- 요약 승격은 P6-memory 의 몫이고 그때도
    이 컬럼 값은 그대로 남는다). `occurred_at` 은 tz-aware 만 받는다.

    **패턴 감지·승격·`fact_sources` 기록 없음**(원칙6·D9 는 P6-memory).
    """
    person = _owned_person(ctx.session, person_id, ctx.user_id)

    if type not in EVENT_TYPES:
        raise InvalidValue(f"add_event: invalid type '{type}'")

    normalized_content = _require_text(content, "content")
    normalized_raw_utterance = _require_text(raw_utterance, "raw_utterance")
    occurred_at_utc = _require_aware(occurred_at, "occurred_at")

    event = Event(
        person_id=person.id,
        type=type,
        content=normalized_content,
        raw_utterance=normalized_raw_utterance,
        occurred_at=occurred_at_utc,
    )
    ctx.session.add(event)
    ctx.session.flush()

    return EventOut(
        id=event.id,
        person_id=event.person_id,
        type=event.type,
        content=event.content,
        occurred_at=event.occurred_at,
        created_at=event.created_at,
    )


@traced("add_schedule")
def add_schedule(
    ctx: ToolContext,
    person_id: int,
    title: str,
    scheduled_at: datetime,
) -> ScheduleOut:
    """S3.2 시그니처: `(person_id, title, scheduled_at) -> Schedule`.

    `briefed_at` 은 항상 `NULL` 로 시작한다(브리핑 트리거는 P6-briefing).
    과거 시각도 **거절하지 않는다** -- 대화 재구성("지난주에 만나기로
    했었는데")으로 과거 일정을 소급 입력하는 것을 막을 이유가 없다. 다만
    `scheduled_at` 은 여전히 tz-aware 만 받는다(미결 3).
    """
    person = _owned_person(ctx.session, person_id, ctx.user_id)

    normalized_title = _require_text(title, "title")
    scheduled_at_utc = _require_aware(scheduled_at, "scheduled_at")

    schedule = Schedule(
        person_id=person.id,
        title=normalized_title,
        scheduled_at=scheduled_at_utc,
        briefed_at=None,
    )
    ctx.session.add(schedule)
    ctx.session.flush()

    return ScheduleOut(
        id=schedule.id,
        person_id=schedule.person_id,
        title=schedule.title,
        scheduled_at=schedule.scheduled_at,
        briefed_at=schedule.briefed_at,
    )
