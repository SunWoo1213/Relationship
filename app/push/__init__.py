"""Refs: P7-push S3.6 R12 원칙9 -- 패키지 진입점. U1 은 골격 타입만
재export 한다.

이 모듈은 결정 D 가 고른 VAPID 발송 라이브러리를 import 하지 않는다.
**그 라이브러리를 import 하는 유일한 모듈은 U4 의 `app/push/sender.py`
다**(01-plan 결정 G "지킬 불변식" -- 그 이름이 `app/` 안에 단 한
파일에서만 나타나야 한다. 이 파일은 의도적으로 그 이름 문자열을 쓰지
않는다 -- 글자 그대로 적으면 불변식 grep 이 이 파일도 집어 깨진다).
U4 는 그 라이브러리의 발송 함수 이름을 **import 시점에 묶지 않는다**
(02-plan-verify 권고 R-2 -- "불리면 실패" 로 바꿔 끼우는 테스트
픽스처가 기본 경로를 잡게 하려면, 호출 시점에 속성으로 찾아야 한다.
이 문장이 U1 03-log 가 남기는 방침 기록이다).

## U2 추가분 -- 구독 저장 (Refs: P7-push S3.1 S3.6 R12)

`save_subscription`/`list_subscriptions`/`SavedSubscription`
(`app/push/subscriptions.py`)을 재export 한다. `app/api/routes.py` 의
`GET /push/vapid-public-key`·`POST /push/subscriptions` 가 이 자리에서
가져다 쓴다.

## U3 추가분 -- 푸시 본문 작성기 (Refs: P7-push S3.6 원칙7)

`build_push_payload`(`app/push/payload.py`)를 재export 한다. 순수
함수이고 `composed.lines`/`composed.pattern_sentences` 를 읽지 않는다
(결정 B, 모듈 docstring).

## U4 추가분 -- 발송기·알림기 (Refs: P7-push S3.6 S3.1 R12 원칙9)

`WebPushNotifier`/`MisconfiguredNotifier`/`notifier_from_env`
(`app/push/notifier.py`)와 `PyWebPushSender`(`app/push/sender.py`)를
재export 한다. `app/push/sender.py` 는 결정 D 가 고른 VAPID 발송
라이브러리를 import 하는 **유일한** 모듈이다(지킬 불변식) -- 이 파일은
그 이름을 import 하지 않고 그 모듈이 만든 클래스만 가져온다.
"""

from __future__ import annotations

from app.push.notifier import MisconfiguredNotifier, WebPushNotifier, notifier_from_env
from app.push.payload import build_push_payload
from app.push.sender import PyWebPushSender
from app.push.subscriptions import SavedSubscription, list_subscriptions, save_subscription
from app.push.types import (
    PUSH_STATUSES,
    PUSH_TRACE_TOOL_NAME,
    SEND_OUTCOMES,
    STEP_PUSH_SEND,
    VAPID_PARTIAL,
    FakePushSender,
    PushSender,
    SendResult,
    VapidConfig,
)

__all__ = [
    "PUSH_STATUSES",
    "PUSH_TRACE_TOOL_NAME",
    "SEND_OUTCOMES",
    "STEP_PUSH_SEND",
    "VAPID_PARTIAL",
    "FakePushSender",
    "PushSender",
    "SendResult",
    "VapidConfig",
    "SavedSubscription",
    "list_subscriptions",
    "save_subscription",
    "build_push_payload",
    "WebPushNotifier",
    "MisconfiguredNotifier",
    "notifier_from_env",
    "PyWebPushSender",
]
