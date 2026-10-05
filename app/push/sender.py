"""Refs: P7-push S3.6 S3.1 R12 원칙9 -- U4 실제 발송기(`PyWebPushSender`).

## 이 모듈이 하는 것 (지킬 불변식 -- 유일한 import 자리)

이 모듈은 결정 D 가 고른 VAPID 발송 라이브러리(`pywebpush`)를 import 하는
**유일한** 모듈이다(01-plan "지킬 불변식" -- `grep -rln "pywebpush" app/`
→ 이 파일 한 줄만 나와야 한다). `app/push/types.py`·`__init__.py`·
`payload.py`·`subscriptions.py`·`notifier.py` 는 그 이름 문자열 자체를
의도적으로 쓰지 않는다(U1~U3 가 이미 세운 관례).

02-plan-verify 권고 R-2 -- 그 라이브러리의 발송 함수(`webpush`)를
**import 시점에 이름으로 묶지 않는다**(`from pywebpush import webpush`
금지). 테스트 "불리면 실패" 픽스처(결정 G)는 `pywebpush.webpush`
**속성 자체**를 바꿔 끼우므로, 모듈 레벨에서 그 이름을 먼저 묶어 두면
이미 묶인 참조는 패치되지 않는다. 그래서 `send()` 는 매 호출마다
`pywebpush.webpush` **속성**을 찾는다(`self._send_fn` 으로 주입도 가능 --
생성자 인자, 테스트가 가짜 발송 함수를 직접 건넬 때 쓴다). U4 evidence 에
이 경로가 실제로 패치되는지(픽스처 on/off 양쪽)를 부정 확인으로 남긴다.

## 예외 -> outcome 매핑 (판정 표 18행)

- 2xx(`pywebpush.webpush()` 는 응답 상태 코드가 202 이하일 때만 예외 없이
  돌려준다) -> `outcome="sent"`, `status_code` = 응답의 상태 코드.
- `pywebpush.WebPushException`(상태 코드 404·410) -> `outcome="gone"`
  (결정 E "구독 행 삭제"), `status_code` 보존.
- `WebPushException`(그 밖의 상태 코드) -> `outcome="failed"`,
  `status_code` 보존.
- `WebPushException`(응답 자체가 없어 상태 코드를 모름 -- 예:
  VAPID 인자 누락처럼 발송 이전에 실패) -> `outcome="error"`,
  `error_class="WebPushException"`.
- **`status_code` 읽기는 `exc.status_code` 속성만 쓴다 -- `str(exc)`/
  `exc.message` 는 절대 읽지 않는다**(security §1, 02-plan-verify 권고
  R-8 -- `WebPushException.__str__` 은 응답 본문·엔드포인트를 메시지에
  섞을 수 있다).
- `requests.exceptions.Timeout`(그 하위 `ConnectTimeout`/`ReadTimeout`
  포함) -> `outcome="timeout"`, `error_class=type(exc).__name__`(클래스
  이름만 -- 메시지는 담지 않는다).
- 그 밖의 모든 예외(연결 오류 포함) -> `outcome="error"`,
  `error_class=type(exc).__name__`.
- **어떤 경우에도 예외를 밖으로 올리지 않는다**(01-plan U4 "예외를 밖으로
  올리지 않는다") -- `WebPushNotifier`(`app/push/notifier.py`)가 구독
  마다 이 메서드를 부르고, 한 구독의 발송 실패가 나머지 구독 발송을
  막지 않는다.

## 이 모듈이 하지 않는 것

- DB(SQLAlchemy 모델)·trace 기록을 하지 않는다 -- `SendResult` 를
  돌려줄 뿐이고, `push_send` trace 는 호출자(`WebPushNotifier`)가 쓴다.
"""

from __future__ import annotations

import json
from typing import Any, Callable

import pywebpush
import requests

from app.push.types import SendResult

#: HTTP 상태 코드 중 "이 구독은 다시는 유효하지 않다"(RFC 8030, 결정 E).
_GONE_STATUS_CODES = (404, 410)


class PyWebPushSender:
    """`PushSender` Protocol 구현체(결정 D·G). 기본 발송 함수는 **호출
    시점에** `pywebpush.webpush` 속성으로 찾는다(모듈 docstring 권고
    R-2). `send_fn` 을 생성자에 주입하면 그 함수를 대신 쓴다(테스트
    전용 -- 운영 코드는 기본값을 쓴다)."""

    def __init__(self, send_fn: Callable[..., Any] | None = None) -> None:
        self._send_fn = send_fn

    def send(
        self,
        *,
        endpoint: str,
        keys: dict[str, str],
        payload: dict[str, Any],
        vapid_private_key: str,
        vapid_subject: str,
        ttl: int,
        timeout: float,
    ) -> SendResult:
        send_fn = self._send_fn if self._send_fn is not None else pywebpush.webpush
        try:
            response = send_fn(
                subscription_info={"endpoint": endpoint, "keys": dict(keys)},
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": vapid_subject},
                ttl=ttl,
                timeout=timeout,
            )
        except pywebpush.WebPushException as exc:
            # 속성만 읽는다 -- str(exc)/exc.message 는 절대 읽지 않는다(R-8).
            status_code = exc.status_code
            if status_code in _GONE_STATUS_CODES:
                return SendResult("gone", status_code=status_code)
            if status_code is not None:
                return SendResult("failed", status_code=status_code)
            return SendResult("error", error_class=type(exc).__name__)
        except requests.exceptions.Timeout as exc:
            return SendResult("timeout", error_class=type(exc).__name__)
        except Exception as exc:  # noqa: BLE001 -- 의도적으로 넓게 잡는다(예외를 밖으로 올리지 않는다, 01-plan U4).
            return SendResult("error", error_class=type(exc).__name__)

        status_code = getattr(response, "status_code", None)
        return SendResult("sent", status_code=status_code if status_code is not None else 201)
