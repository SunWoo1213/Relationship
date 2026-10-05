"""Refs: P7-push S3.6 S3.1 R12 원칙9 -- U4 알림기(`WebPushNotifier`·
`notifier_from_env`).

## 이 모듈이 하는 것

`WebPushNotifier.notify(schedule, composed)` 는 `app.briefing.types.
Notifier` Protocol 구현체다(결정 J). 순서(01-plan U4 그대로): 일정 소유
인물의 `display_name` 조회(**R-6 -- 그 인물의 `user_id` 가 이 알림기의
`user_id` 와 같은지 확인** -- `select_due_schedules`(P6-briefing)가 이미
`Person.user_id == ctx.user_id` 로 걸러 고르므로 지금은 항상 참이지만,
이 알림기 자신도 `security.md` §5 "모든 조회는 user_id 조건"을 스스로
지키는 증거로 한 줄 남긴다. **보완(사용자 결정 2026-10-05)**: 예전에는
`assert` 로 확인했으나 `python -O` 에서 사라지고, 깨지면
`AssertionError` 가 `run_briefings` 세이브포인트를 롤백시켜 `briefed_at`
미기록 → 다음 1분 주기 재선정 → LLM 생성 반복을 낳았다. 지금은 명시적
`if` 로 확인하고, 깨지면 구독 조회·발송을 **하지 않고**(fail-closed)
`push_send` trace(`output.reason="owner_mismatch"`)만 남긴 뒤 `"failed"`
를 돌려준다 -- 예외가 없으므로 `briefed_at` 은 정상 기록되고 재선정도
없다) -> `list_subscriptions` -> 0건이면
`"no_subscription"` -> `build_push_payload` -> 구독마다 `sender.send()`
-> `"gone"` 구독 행 ORM 삭제(결정 E -- 셸 `DELETE`/`DROP` 과 다르다,
02-plan-verify 점검표 8행) -> 상태 집계(`sent`/`partial`/`failed`) ->
`push_send` trace 1행(결정 F) -> 상태 문자열 반환.

**`notify()` 는 발송 실패로 예외를 올리지 않는다**(01-plan 결정 C(i)) --
`PushSender`(U4 `app/push/sender.py::PyWebPushSender`) 구현이 이미 모든
발송 예외를 `SendResult` 로 바꾸므로, 이 메서드 자체는 발송 루프에서
예외를 던질 일이 없다. R-6 user_id 불일치도 이제 같은 원칙으로 예외를
올리지 않고 상태 문자열로 바꾼다(위 문단). 이 알림기 **자신의** DB 조회
(인물·구독 조회) 실패는 그대로 올린다(01-plan 결정 C "권장" 문단 --
"알림기 자체의 DB 조회 실패만 그대로 올린다, 그것은 P6 규약대로 일정
단위 격리가 맞다" -- `app/briefing/run.py` 의 세이브포인트 격리가 그
경우를 처리한다).

`notifier_from_env(session, user_id, now, env=None)` -- `app.settings.
vapid_config(env)` 세 가지 반환값을 그대로 세 알림기로 사상한다: 키 전무
-> `app.briefing.types.NullNotifier`(기존 그대로, 운영 기본값) / 반쪽 ->
`MisconfiguredNotifier`(이 모듈, "조용히 꺼진 것처럼 보이지 않게") / 전부
있음 -> `WebPushNotifier` + `PyWebPushSender()`.

## 이 모듈이 하지 않는 것

- 결정 D 가 고른 VAPID 발송 라이브러리를 import 하지 않는다 -- 그 이름이
  `app/` 안에 나타나는 유일한 자리는 `app/push/sender.py` 다(01-plan
  결정 G "지킬 불변식"). 발송 자체는 `PushSender`(생성자로 주입받은
  `self.sender`)에게 맡긴다.
- `run_briefings()`·`Notifier` Protocol·`NullNotifier` 시그니처를 바꾸지
  않는다(01-plan "하지 않는 것").
- 엔드포인트 URL·구독 키 값을 trace·로그에 쓰지 않는다(security §1) --
  `push_send` trace `output.results[]` 는 `subscription_id`/`outcome`/
  `status_code` 뿐이고, 삭제한 구독도 id 만 `removed` 에 남는다(결정 E
  "엔드포인트 URL 은 trace 에 쓰지 않으므로 … id·응답 코드만").
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.briefing.types import ComposedBriefing, NullNotifier
from app.db.models import AgentTrace, Person
from app.push.payload import build_push_payload
from app.push.sender import PyWebPushSender
from app.push.subscriptions import list_subscriptions
from app.push.types import (
    PUSH_TRACE_TOOL_NAME,
    STEP_PUSH_SEND,
    VAPID_PARTIAL,
    PushSender,
    VapidConfig,
)
from app.settings import PUSH_TIMEOUT_SECONDS, vapid_config

__all__ = ["WebPushNotifier", "MisconfiguredNotifier", "notifier_from_env"]


@dataclass
class MisconfiguredNotifier:
    """VAPID 세 이름 중 **일부만** 설정된 경우(결정 D "반쪽")의 알림기.
    아무것도 보내지 않고 항상 `"misconfigured"` 를 돌려준다 --
    `app.briefing.types.NullNotifier` 와 같은 모양이지만 "키가 아예
    없다"(`not_configured`)와 "반쪽만 있다"(`misconfigured`)를 구분해
    조용히 꺼진 것처럼 보이지 않게 한다(security §1, 01-plan 결정 D).
    `NullNotifier` 와 마찬가지로 trace 를 남기지 않는다 -- 아직 발송
    시도 자체가 없다(발송 대상 조회조차 하지 않는다)."""

    def notify(self, schedule: Any, composed: ComposedBriefing) -> str:
        return "misconfigured"


@dataclass
class WebPushNotifier:
    """실제 `Notifier`(결정 J) 구현체. 구독마다 `sender.send()` 를 불러
    VAPID 서명·암호화 푸시를 보내고, 결과를 집계해 `push_send` trace
    1행을 남긴다(결정 F). 모듈 docstring "이 모듈이 하는 것" 참고."""

    session: Session
    user_id: str
    sender: PushSender
    vapid: VapidConfig
    now: Callable[[], datetime]

    def notify(self, schedule: Any, composed: ComposedBriefing) -> str:
        person = self.session.execute(
            select(Person).where(Person.id == schedule.person_id)
        ).scalar_one()
        # R-6(security §5) -- 알림기 자신도 user_id 경계를 스스로 확인한다.
        # select_due_schedules()(P6-briefing)가 이미 Person.user_id ==
        # ctx.user_id 로 걸러 고르므로 지금은 항상 참이다. 보완(사용자
        # 결정 2026-10-05): 예전에는 `assert`문으로 확인했는데, (1)
        # `python -O` 로 돌리면 그 문이 통째로 사라져 이 안전장치가
        # 조용히 꺼지고, (2) 어쩌다 깨지면 AssertionError 가 `run_briefings` 의
        # 세이브포인트를 롤백시켜 그 일정의 `briefed_at` 이 기록되지
        # 않는다 -- 그러면 다음 1분 주기에 같은 일정이 다시 선정되어
        # LLM 생성이 매번 반복된다(비용·멱등성 문제). 그래서 명시적
        # `if` 로 바꾸고, 깨지면 아무것도 보내지 않은 채(fail-closed)
        # `"failed"` 를 돌려줘 `briefed_at` 은 정상적으로 기록되게 한다
        # -- 예외를 올리지 않으므로 같은 조건으로 재실행해도 재선정되지
        # 않는다(판정은 아래 trace 1행으로 남긴다).
        if person.user_id != self.user_id:
            self._record_trace(
                schedule_id=schedule.id,
                person_id=person.id,
                subscription_ids=[],
                results=[],
                removed=[],
                status="failed",
                payload=None,
                reason="owner_mismatch",
            )
            return "failed"
        display_name = person.display_name

        subscriptions = list_subscriptions(self.session, self.user_id)
        subscription_ids = [sub.id for sub in subscriptions]

        if not subscriptions:
            status = "no_subscription"
            self._record_trace(
                schedule_id=schedule.id,
                person_id=person.id,
                subscription_ids=subscription_ids,
                results=[],
                removed=[],
                status=status,
                payload=None,
            )
            return status

        payload = build_push_payload(schedule, display_name, composed, self.now())

        results: list[dict[str, Any]] = []
        removed: list[int] = []
        outcomes: list[str] = []
        for sub in subscriptions:
            send_result = self.sender.send(
                endpoint=sub.endpoint,
                keys=sub.keys,
                payload=payload,
                vapid_private_key=self.vapid.private_key,
                vapid_subject=self.vapid.subject,
                ttl=payload["ttl"],
                timeout=PUSH_TIMEOUT_SECONDS,
            )
            outcomes.append(send_result.outcome)
            results.append(
                {
                    "subscription_id": sub.id,
                    "outcome": send_result.outcome,
                    "status_code": send_result.status_code,
                }
            )
            if send_result.outcome == "gone":
                # 결정 E -- 제품 코드의 ORM 삭제(셸 DELETE/DROP 과 다르다).
                removed.append(sub.id)
                self.session.delete(sub)

        if all(outcome == "sent" for outcome in outcomes):
            status = "sent"
        elif any(outcome == "sent" for outcome in outcomes):
            status = "partial"
        else:
            status = "failed"

        self._record_trace(
            schedule_id=schedule.id,
            person_id=person.id,
            subscription_ids=subscription_ids,
            results=results,
            removed=removed,
            status=status,
            payload=payload,
        )
        return status

    def _record_trace(
        self,
        *,
        schedule_id: int,
        person_id: int,
        subscription_ids: list[int],
        results: list[dict[str, Any]],
        removed: list[int],
        status: str,
        payload: dict[str, Any] | None,
        reason: str | None = None,
    ) -> None:
        """`push_send` trace 1행(결정 F). `output.payload` 는 `title`/
        `body` 뿐이다 -- 엔드포인트·키 값은 어디에도 없다(security §1,
        판정 20행). `reason` 은 정상 경로에서는 `None`(기존 판정 19행
        trace 모양을 그대로 유지) -- R-6 user_id 불일치로 발송 자체를
        건너뛴 경우에만 `"owner_mismatch"` 를 채운다. 서로 다른
        user_id 값 자체(둘 중 어느 쪽이든)는 여기에 넣지 않는다 --
        "값이 달랐다"는 사실만 trace 에 남는다."""

        output: dict[str, Any] = {
            "schedule_id": schedule_id,
            "status": status,
            "results": results,
            "removed": removed,
            "payload": (
                {"title": payload["title"], "body": payload["body"]}
                if payload is not None
                else None
            ),
            "ttl": payload["ttl"] if payload is not None else None,
            "reason": reason,
        }
        self.session.add(
            AgentTrace(
                session_id=f"push:{uuid.uuid4()}",
                step=STEP_PUSH_SEND,
                tool_name=PUSH_TRACE_TOOL_NAME,
                input={
                    "schedule_id": schedule_id,
                    "person_id": person_id,
                    "subscription_ids": subscription_ids,
                },
                output=output,
                tokens_in=0,
                tokens_out=0,
            )
        )
        self.session.flush()


def notifier_from_env(
    session: Session,
    user_id: str,
    now: Callable[[], datetime],
    env: dict[str, str] | None = None,
) -> NullNotifier | MisconfiguredNotifier | WebPushNotifier:
    """`vapid_config(env)` 세 가지 반환값을 알림기로 사상한다(결정 D).
    키 전무 -> `NullNotifier`(운영 기본값, 기존 그대로) / 반쪽 ->
    `MisconfiguredNotifier` / 전부 있음 -> `WebPushNotifier` +
    `PyWebPushSender()`."""

    vapid = vapid_config(env)
    if vapid is None:
        return NullNotifier()
    if vapid is VAPID_PARTIAL:
        return MisconfiguredNotifier()
    return WebPushNotifier(
        session=session, user_id=user_id, sender=PyWebPushSender(), vapid=vapid, now=now
    )
