"""Refs: P2-tools U8 결정 11 -- FastAPI 앱 팩토리 + 예외 매핑(한 곳에서).

`create_app()` 은 라우터 등록과 도메인 예외 → HTTP 상태 매핑(예외 핸들러)을
이 한 곳에서 한다(결정 11 -- 라우트마다 try/except 를 흩뿌리지 않는다).

**리스크 A -- `create_app()` 은 엔진을 만들지 않는다.** 이 모듈이 import 하는
`app.api.routes` → `app.api.deps` → `app.db.session` 체인 어디에도 즉시
실행되는 `get_engine()` 호출이 없다(`SessionLocal` 은 호출 시점까지 엔진
생성을 미루는 프록시). `import app.main` 만으로는 DB 접속을 시도하지 않는다
-- 접속 확인은 `GET /health` 가 요청이 왔을 때만 한다. lifespan 훅도 두지
않는다(접속 확인은 lifespan 의 일이 아니다).

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

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import router
from app.tools.types import (
    ConfirmationRequired,
    InvalidValue,
    PersonNotFound,
    QuestionNotAnswerable,
    QuestionNotFound,
    ScheduleNotFound,
    ToolError,
)


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


def create_app() -> FastAPI:
    """앱 팩토리. 엔진을 만들지 않고 DB 접속도 확인하지 않는다(리스크 A)."""
    app = FastAPI(title="관계 메모리 에이전트 API")
    app.include_router(router)

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
