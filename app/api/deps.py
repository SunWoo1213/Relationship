"""Refs: P2-tools U8 결정 12 -- 요청 단위 세션 의존성 + `ToolContext` 조립.

`get_session()` 은 제너레이터 의존성이다: `SessionLocal()` 로 요청 단위
세션을 만들고, 정상 종료 시 commit, 예외 시 rollback, finally 에서 항상
close 한다 -- `app/db/session.py` 의 `session_scope()` 와 같은 규약을
FastAPI 의존성 형태로 옮긴 것이다. 툴 함수는 여전히 commit 하지 않는다
(01-plan 결정 2) -- 트랜잭션 경계는 이 의존성(호출자)이 잡는다.

`get_engine()` 은 `SessionLocal()` 이 실제로 호출될 때(즉 요청이 들어와
이 의존성이 실행될 때)까지 지연된다(`app/db/session.py` 의 `_SessionLocalProxy`
-- 리스크 A). 이 모듈을 import 하는 것만으로는 엔진이 생성되지 않는다.

`build_ctx(session, question_id)` 는 **답할 `pending_questions` 행을 먼저
조회해 그 행의 `session_id` 로 `ToolContext` 를 만든다**(결정 12) --
클라이언트가 헤더로 주장하는 세션 값보다 저장된 행이 권위 있고, trace 가
질문을 만든 턴과 같은 세션에 묶인다. `X-Session-Id` 헤더 규약은 세션을
새로 여는 쪽(P5-loop 의 채팅 엔드포인트)이 정한다 -- 이 모듈은 헤더를
읽지 않는다. 행이 없으면 `QuestionNotFound` 를 올린다(라우트에서 404 로
매핑, `app/main.py`).
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.models import PendingQuestion
from app.db.session import SessionLocal
from app.settings import app_user_id
from app.tools.context import ToolContext
from app.tools.types import QuestionNotFound


def get_session() -> Iterator[Session]:
    """요청 단위 세션. 정상 종료 시 commit, 예외 시 rollback, 항상 close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def build_ctx(session: Session, question_id: int) -> ToolContext:
    """답할 `pending_questions` 행을 조회해 그 `session_id` 로 `ToolContext`
    를 만든다(결정 12). 행이 없으면 `QuestionNotFound`.

    `user_id = app_user_id()`(로컬 단일 사용자), `embedder=None`(답 저장은
    별칭을 만들지 않는다), `now` 는 기본값(`datetime.now(timezone.utc)`)."""
    question = session.get(PendingQuestion, question_id)
    if question is None:
        raise QuestionNotFound("question_not_found")
    return ToolContext(
        session=session,
        session_id=question.session_id,
        user_id=app_user_id(),
        embedder=None,
    )
