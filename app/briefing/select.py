"""Refs: P6-briefing S3.6 S3.1 R12 원칙8 -- U2 대상 선정(`select_due_schedules`).

브리핑 대상 일정을 고르는 순수 SQL 함수 하나만 정의한다. LLM·임베딩·
네트워크 import 없음(`app.briefing.compose`·`app.er.judge`·`app.embedding`
을 이 모듈은 import 하지 않는다 -- 01-plan "지킬 불변식").

## 두 모드 (01-plan U2, 결정 B(i)·C(ii))

- **기본 모드**(`schedule_id=None`): `Schedule ⨝ Person` 에서
  `Person.user_id == ctx.user_id` AND 창
  `now <= scheduled_at <= now + lead_hours`(S3.6 보충 줄 "창은
  `now <= scheduled_at <= now + 24h` -- 이미 지난 일정은 제외", `get_briefing`
  의 `upcoming_schedules`(`scheduled_at >= now`)와 같은 방향) AND
  `briefed_at IS NULL`, `scheduled_at` 오름차순, `FOR UPDATE OF schedules
  SKIP LOCKED`. 동시에 도는 두 실행(주기 작업·수동 트리거)이 같은 일정을
  두 번 집지 않게 한다.
- **지정 모드**(`schedule_id` 가 주어짐, 결정 C(ii)): 그 한 건만 소유 확인
  후 **창·`briefed_at` 과 무관하게** 돌려준다(같은 행 잠금을 쓴다 -- 기본
  모드와 같은 `FOR UPDATE ... SKIP LOCKED`). 없거나 다른 `user_id` 소유면
  기존 `ScheduleNotFound`(`app/tools/types.py`, 새 예외 클래스를 만들지
  않는다).

## 이 모듈이 하지 않는 것

`briefed_at` 을 이 모듈은 쓰지 않는다 -- 그 기록은 `get_briefing`(U3 가
호출, `app/tools/briefing.py`)의 몫이다. 패턴 재계산·브리핑 입력 조립·
문장 생성도 각각 U3·U4 의 몫이고 이 모듈은 대상 일정 목록만 돌려준다.
"""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from app.db.models import Person, Schedule
from app.tools.context import ToolContext
from app.tools.types import ScheduleNotFound


def select_due_schedules(
    ctx: ToolContext,
    *,
    lead_hours: float,
    schedule_id: int | None = None,
) -> list[Schedule]:
    """브리핑 대상 일정을 고른다(모듈 docstring의 두 모드 참고).

    `ctx.now()` 는 이 함수 안에서 한 번만 호출해 창 계산에 재사용한다
    (`get_briefing` 이 `generated_at`에 쓰는 것과 같은 관례).
    """

    now = ctx.now()

    if schedule_id is not None:
        row = (
            ctx.session.execute(
                select(Schedule)
                .join(Person, Schedule.person_id == Person.id)
                .where(Schedule.id == schedule_id)
                .where(Person.user_id == ctx.user_id)
                .with_for_update(of=Schedule, skip_locked=True)
            )
            .scalars()
            .one_or_none()
        )
        if row is None:
            raise ScheduleNotFound("schedule_not_found")
        return [row]

    window_end = now + timedelta(hours=lead_hours)
    rows = (
        ctx.session.execute(
            select(Schedule)
            .join(Person, Schedule.person_id == Person.id)
            .where(Person.user_id == ctx.user_id)
            .where(Schedule.scheduled_at >= now)
            .where(Schedule.scheduled_at <= window_end)
            .where(Schedule.briefed_at.is_(None))
            .order_by(Schedule.scheduled_at.asc())
            .with_for_update(of=Schedule, skip_locked=True)
        )
        .scalars()
        .all()
    )
    return list(rows)
