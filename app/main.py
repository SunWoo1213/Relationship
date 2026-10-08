"""Refs: P2-tools U8 결정 11 -- FastAPI 앱 팩토리 + 예외 매핑(한 곳에서).

`create_app()` 은 라우터 등록과 도메인 예외 → HTTP 상태 매핑(예외 핸들러)을
이 한 곳에서 한다(결정 11 -- 라우트마다 try/except 를 흩뿌리지 않는다).

**리스크 A -- `create_app()` 은 엔진을 만들지 않는다.** 이 모듈이 import 하는
`app.api.routes` → `app.api.deps` → `app.db.session` 체인 어디에도 즉시
실행되는 `get_engine()` 호출이 없다(`SessionLocal` 은 호출 시점까지 엔진
생성을 미루는 프록시). `import app.main` 만으로는 DB 접속을 시도하지 않는다
-- 접속 확인은 `GET /health` 가 요청이 왔을 때만 한다. **스위치
(`BRIEFING_SCHEDULER_ENABLED`)가 꺼져 있으면 lifespan 은 아무것도 하지
않는다**(기본값이 꺼짐이므로 리스크 A 는 그대로 유지된다). 켜져 있을
때만 lifespan 이 1분 주기 브리핑 작업(P6-briefing U7, `app/briefing/
scheduler.py`)을 띄운다 -- 그 작업 자신이 실행마다 `session_scope()` 로
세션을 여는 것이지, `create_app()`/lifespan 자신이 엔진을 만들거나
DB 접속을 확인하는 것은 아니다(접속 확인은 여전히 `GET /health` 전용).

## 주기 작업 lifespan (P6-briefing U7, S3.6 결정 A(i))

`_lifespan()` 은 `briefing_scheduler_enabled()`(`app/settings.py`)를 앱
시작 시 한 번 읽는다. `False`(기본값)면 아무 태스크도 만들지 않고 바로
`yield` 한다 -- 위 리스크 A 가 그대로 유지된다. `True` 면
`start_scheduler_task()`(`app/briefing/scheduler.py`)로 `asyncio.Task`
하나를 만들어 1분(기본)마다 `run_briefings(trigger="scheduler")` 가
돌게 하고, 앱 종료 시(`finally`) 그 태스크를 취소하고 끝날 때까지
기다린다. 스위치 값이 `1`/`true`/빈 문자열이 아닌 다른 값이면
`briefing_scheduler_enabled()` 가 `InvalidValue` 를 던지고, 그 예외는
여기서 잡지 않는다 -- **앱 시작 자체가 실패한다**(원칙8 "조용히 꺼진
채로 넘어가지 않는다", 02-plan-verify 위임 지시).

예외 매핑 표(01-plan U8 지시):

| 예외 | 상태 | 본문 |
|------|------|------|
| `PersonNotFound`/`QuestionNotFound`/`ScheduleNotFound` | 404 | `{"detail":{"code":"not_found"}}` |
| `QuestionNotAnswerable` | 409 | `{"detail":{"code": e.code, "question_id": id}}` |
| `InvalidValue` | 422 | `{"detail":{"code":"invalid_value"}}` |
| `ConfirmationRequired` | 422 | `{"detail":{"code":"confirmation_required","reason": e.reason}}` |
| 그 밖의 `ToolError` | 400 | `{"detail":{"code":"tool_error"}}` |
| 그 밖의 미처리 예외(`Exception`) | `/health` 경로면 503 degraded 본문, 그 외 500 | 원문 미포함 |

어떤 핸들러도 `str(exc)`(예외 원문)를 응답 본문에 넣지 않는다 -- 사유
코드만 담는다(security.md §1). `PersonNotFound`/`QuestionNotFound` 는
"존재하지 않음"과 "다른 사용자 소유"를 같은 404 로 다뤄 존재 여부를
흘리지 않는다.

마지막의 `Exception` 캐치올은 `GET /health` 가 `Depends(get_session)`
해석 자체가 실패하는 경우(예: 테스트가 `get_session` 을 예외 던지는
의존성으로 오버라이드해 DB 다운을 시뮬레이션)까지 503 degraded 로
받아내기 위한 것이다 -- 이 경로가 아니면(즉 `/health` 가 아니면) 원문을
감춘 채 500 만 돌려준다. `HTTPException`/`RequestValidationError` 는
FastAPI 가 이미 더 구체적인 클래스로 기본 핸들러를 등록해 두었으므로
이 캐치올보다 먼저 매칭된다(예: body 형식 오류 → FastAPI 기본 422).
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from app.api import router
from app.briefing.scheduler import start_scheduler_task
from app.settings import briefing_scheduler_enabled, push_dev_page_enabled
from app.tools.types import (
    ConfirmationRequired,
    InvalidValue,
    PersonNotFound,
    QuestionNotAnswerable,
    QuestionNotFound,
    ScheduleNotFound,
    ToolError,
)


#: 개발·확인 전용 구독 페이지 정적 파일 위치(P7-push U6, 결정 A).
_DEVPAGE_DIR = Path(__file__).resolve().parent / "push" / "devpage"


def _register_push_dev_page(app: FastAPI) -> None:
    """`PUSH_DEV_PAGE_ENABLED` 가 켜졌을 때만 `/push-dev/` 세 경로를 등록한다
    (P7-push U6, 결정 A -- 제품 화면이 아닌 확인 도구). 꺼져 있으면 경로
    자체가 없어 404 다. 세 파일만 명시적으로 서빙하므로 경로 탐색(`..`)이
    불가능하다. 잘못된 스위치 값은 `briefing_scheduler_enabled()` 와 같이
    `InvalidValue` 가 그대로 올라온다(원칙8)."""
    if not push_dev_page_enabled():
        return

    files = {
        "/push-dev/": ("index.html", "text/html; charset=utf-8"),
        "/push-dev/sw.js": ("sw.js", "application/javascript"),
        "/push-dev/devpage.js": ("devpage.js", "application/javascript"),
    }
    for route_path, (filename, media_type) in files.items():
        file_path = _DEVPAGE_DIR / filename

        def _serve(
            file_path: Path = file_path, media_type: str = media_type
        ) -> FileResponse:
            return FileResponse(file_path, media_type=media_type)

        app.add_api_route(route_path, _serve, methods=["GET"], include_in_schema=False)


def _not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": {"code": "not_found"}})


def _question_not_answerable_handler(
    request: Request, exc: QuestionNotAnswerable
) -> JSONResponse:
    raw_question_id = request.path_params.get("question_id")
    try:
        question_id: int | str | None = int(raw_question_id)
    except (TypeError, ValueError):
        question_id = raw_question_id
    return JSONResponse(
        status_code=409,
        content={"detail": {"code": exc.code, "question_id": question_id}},
    )


def _invalid_value_handler(request: Request, exc: InvalidValue) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": {"code": "invalid_value"}})


def _confirmation_required_handler(
    request: Request, exc: ConfirmationRequired
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": {"code": "confirmation_required", "reason": exc.reason}},
    )


def _tool_error_handler(request: Request, exc: ToolError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": {"code": "tool_error"}})


def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if request.url.path == "/health":
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "down", "alembic_revision": None},
        )
    return JSONResponse(status_code=500, content={"detail": {"code": "internal_error"}})


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """스위치(`BRIEFING_SCHEDULER_ENABLED`)가 켜졌을 때만 1분 주기 브리핑
    작업(P6-briefing U7)을 띄운다. 모듈 docstring "주기 작업 lifespan"
    절 참고 -- 꺼져 있으면(기본값) 아무것도 하지 않아 엔진 생성·DB 접속이
    없는 리스크 A 를 그대로 유지한다. `briefing_scheduler_enabled()` 가
    `InvalidValue` 를 던지면 여기서 잡지 않고 그대로 올려 앱 시작을
    실패시킨다(원칙8)."""
    task: asyncio.Task[None] | None = None
    if briefing_scheduler_enabled():
        task = start_scheduler_task()
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


def create_app() -> FastAPI:
    """앱 팩토리. 스위치가 꺼져 있으면(기본값) lifespan 은 아무것도 하지
    않아 엔진을 만들지 않고 DB 접속도 확인하지 않는다(리스크 A). 켜져
    있으면 lifespan 이 1분 주기 브리핑 작업만 띄운다(P6-briefing U7,
    모듈 docstring 참고)."""
    app = FastAPI(title="관계 메모리 에이전트 API", lifespan=_lifespan)
    app.include_router(router)
    _register_push_dev_page(app)

    app.add_exception_handler(PersonNotFound, _not_found_handler)
    app.add_exception_handler(QuestionNotFound, _not_found_handler)
    app.add_exception_handler(ScheduleNotFound, _not_found_handler)
    app.add_exception_handler(QuestionNotAnswerable, _question_not_answerable_handler)
    app.add_exception_handler(InvalidValue, _invalid_value_handler)
    app.add_exception_handler(ConfirmationRequired, _confirmation_required_handler)
    app.add_exception_handler(ToolError, _tool_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)

    return app


#: uvicorn 진입점(`app.main:app`). import 시점에 엔진을 만들지 않는다(리스크 A).
app = create_app()
