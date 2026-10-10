"""Refs: P6-briefing S3.6 R12 원칙8 -- U7 1분 주기 작업(`asyncio` 루프 +
`app/main.py` lifespan 진입점).

## 무엇이 어디에 있는가

- 이 모듈(`run_scheduler_loop`/`start_scheduler_task`/`default_run_once`)은
  **루프 자체**만 담는다. "스위치가 꺼져 있으면 아무것도 하지 않는다"는
  판단은 **여기가 아니라 `app/main.py` 의 lifespan**이 한다(결정 A(i)) --
  이 모듈은 스위치(`briefing_scheduler_enabled()`)를 import 하지도 읽지도
  않는다. 그래야 "스위치 검사를 끄면 판정 25(꺼짐)가 실패한다"는 부정
  테스트가 `main.py` 쪽 로직만을 정확히 검사한다.
- `app/main.py` 의 lifespan 은 스위치가 켜져 있을 때만
  `start_scheduler_task()` 를 불러 `asyncio.Task` 를 하나 만들고, 앱
  종료 시 그 태스크를 취소하고 끝날 때까지 기다린다.

## 실행 하나 = `default_run_once()`

주기 작업이 1분(기본)마다 부르는 실행 하나는 U5(`run_briefings`)·U6
(`POST /briefings/run`)과 같은 모양이다: `session_scope()`(`app/db/
session.py`)로 세션을 열고 `ToolContext`(`user_id = app_user_id()`)를
만들어 `run_briefings(ctx, composer=composer_from_env(), trigger=
"scheduler")` 를 부른다. `session_scope()` 가 정상 종료 시 commit, 예외
시 rollback, 항상 close 하므로 이 함수 자신은 커밋하지 않는다(01-plan
결정 2 와 같은 경계 -- U5 `run_briefings()` 는 `flush()` 까지만 한다).

**생성기는 이 호출 안에서(매 실행마다) 만든다** -- `composer_from_env()`
(D11)를 모듈 최상위나 `start_scheduler_task()` 호출 시점이 아니라 이
함수 본문 안에서 부른다. 그래야 LLM 공급자 키가 없는 환경에서도
`import app.briefing.scheduler` 와 앱 기동(`create_app()`) 자체는 깨지지
않는다 -- 실패는 실제로 이 실행이 돌 때(스위치가 켜져 있고 주기가 한
번 지났을 때)만 `JudgeUnavailable` 로 드러나고, `run_briefings()` 가
이미 그 경우 템플릿 대체로 처리한다(U5 결정 D). `POST /briefings/run`
(U6)의 `get_briefing_composer()` 지연 생성과 같은 정신이다.

## 루프 구조 (`run_scheduler_loop`)

간격(`interval_seconds`)마다 `await asyncio.sleep(interval_seconds)` 로
한 번 쉬고 `run_once()` 를 **스레드 풀**(`asyncio.to_thread`)에서
동기적으로 돌려 이벤트 루프(다른 요청 처리)를 막지 않는다. 한 번의
실행이 예외를 내면 `logger.exception(...)` 으로 로그만 남기고 삼켜
루프는 다음 주기에 계속 돈다(01-plan U7 "한 번의 실행이 예외를 내도
루프는 계속 돈다") -- `asyncio.CancelledError` 는 `Exception` 의 자식이
아니므로 `except Exception:` 에 애초에 걸리지 않지만, 의도를 명시하려고
`except asyncio.CancelledError: raise` 를 그 앞에 둔다(앱 종료 시
`task.cancel()` 이 이 예외로 루프를 끝낸다).

## 테스트가 간격·실행 함수를 주입하는 방법 (01-plan U7 "실 시간 1분을
## 기다리지 않는다")

`run_scheduler_loop(interval_seconds=.., run_once=..)` 는 두 값을 **필수
키워드 인자**로 받는다 -- 비-HTTP 테스트는 이 함수를 직접 `asyncio` 태스크로
돌려 아주 짧은 간격과 호출 카운터를 넘긴다.

`start_scheduler_task(interval_seconds=None, run_once=None)` 는 `app/main.py`
의 lifespan 이 부르는 **얇은 래퍼**다. 인자를 생략하면(운영 경로) 이
함수 **본문 안에서** 모듈 전역 `BRIEFING_INTERVAL_SECONDS`/
`default_run_once` 를 읽는다 -- 함수 기본 인자 값(def 시점에 한 번
평가·고정)이 아니라 호출 시점에 모듈 전역을 다시 찾아 읽으므로,
`TestClient` 로 실제 앱(`create_app()`)을 lifespan 까지 띄워 끝에서
끝까지 확인하는 테스트는 `monkeypatch.setattr(scheduler module,
"BRIEFING_INTERVAL_SECONDS", 0.01)`·`monkeypatch.setattr(scheduler
module, "default_run_once", counting_fn)` 로 전역을 바꿔치기한 뒤
`BRIEFING_SCHEDULER_ENABLED=1` 로 `with TestClient(create_app()) as
client:` 에 진입하면 짧은 간격·가짜 실행 함수가 그대로 쓰인다(새
메커니즘이 아니라 파이썬 전역 조회 시점을 이용한 것 -- `app/settings.py`
의 코드 상수를 함수 기본값으로 바로 바인딩하면 이 방식이 통하지 않는다).
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable

from app.briefing.compose import composer_from_env
from app.briefing.run import run_briefings
from app.db.session import session_scope
from app.settings import BRIEFING_INTERVAL_SECONDS, app_user_id
from app.tools.context import ToolContext

logger = logging.getLogger(__name__)

#: `run_once` 콜러블의 타입 별칭 -- 동기 함수다(스레드 풀에서 돈다).
RunOnce = Callable[[], None]


def default_run_once() -> None:
    """주기 작업 한 번의 실제 실행(모듈 docstring "실행 하나" 절). 운영
    경로가 `start_scheduler_task()` 를 통해 기본으로 쓰는 함수다."""

    # 지연 import -- 모듈 상단에 두면 `app.push` 를 먼저 올릴 때
    # push.notifier -> briefing 패키지 -> 이 모듈 -> push.notifier 로 순환한다(FIX-029).
    from app.push.notifier import notifier_from_env

    with session_scope() as session:
        ctx = ToolContext(
            session=session,
            session_id=f"briefing-scheduler:{uuid.uuid4()}",
            user_id=app_user_id(),
        )
        # P7-push U5 -- 같은 세션·같은 시계(`ctx.now`)로 알림기를 만든다. 키가
        # 없으면 `NullNotifier`(기존 동작), 있으면 `WebPushNotifier`. 수동 경로
        # (`app/api/deps.py::get_notifier`)와 같은 함수를 쓴다.
        notifier = notifier_from_env(session, ctx.user_id, ctx.now)
        run_briefings(ctx, composer=composer_from_env(), notifier=notifier, trigger="scheduler")


async def run_scheduler_loop(*, interval_seconds: float, run_once: RunOnce) -> None:
    """`interval_seconds` 마다 `run_once()` 를 스레드 풀에서 한 번 돌리는
    무한 루프(모듈 docstring "루프 구조" 절). 앱 종료 시 바깥에서
    `task.cancel()` 하면 `asyncio.sleep`/`asyncio.to_thread` 대기 지점에서
    `CancelledError` 가 일어나 이 루프가 끝난다(삼키지 않고 그대로
    올린다)."""

    while True:
        await asyncio.sleep(interval_seconds)
        try:
            await asyncio.to_thread(run_once)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 -- 의도적으로 넓게 잡는다(루프 생존, 01-plan U7)
            logger.exception(
                "브리핑 주기 작업 실행 중 예외가 났습니다 -- 다음 주기에 다시 시도합니다"
            )


def start_scheduler_task(
    *,
    interval_seconds: float | None = None,
    run_once: RunOnce | None = None,
) -> "asyncio.Task[None]":
    """`app/main.py` 의 lifespan 이 스위치가 켜졌을 때 부르는 진입점(모듈
    docstring "테스트가 간격·실행 함수를 주입하는 방법" 절 -- 인자를
    생략하면 호출 시점에 이 모듈의 전역 `BRIEFING_INTERVAL_SECONDS`/
    `default_run_once` 를 읽는다)."""

    if interval_seconds is None:
        interval_seconds = BRIEFING_INTERVAL_SECONDS
    if run_once is None:
        run_once = default_run_once
    return asyncio.ensure_future(
        run_scheduler_loop(interval_seconds=interval_seconds, run_once=run_once)
    )
