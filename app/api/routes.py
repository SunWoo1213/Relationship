"""Refs: P2-tools U8 R7 D2 S3.4 -- FastAPI 라우트 2개(`GET /health`,
`POST /answers/{question_id}`).

이 모듈은 도메인 예외를 잡지 않는다 -- 예외가 나면 그대로 올라가
`app/main.py` 의 예외 핸들러(결정 11 "예외 매핑은 한 곳에서")가 처리한다.
유일한 예외는 `GET /health` 의 `alembic_version` 조회 실패(테이블 없음)를
그 자리에서 `None` 으로 흡수하는 것뿐이다 -- 그것은 "판정"이 아니라 값이
없을 때의 기본값 처리다.

P5-loop 이 이 파일에 채팅·재개 라우트를 추가하고 `get_session` 을
재사용한다(01-plan 결정 11).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import build_ctx, get_session
from app.api.schemas import AnswerIn, AnswerOut, HealthOut
from app.tools.questions import answer_question

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health(session: Session = Depends(get_session)) -> HealthOut:
    """DB 접속 확인(리스크 A -- 접속 확인은 여기서만 한다, `create_app()`/
    lifespan 은 엔진을 만들지도 접속을 확인하지도 않는다).

    `SELECT 1` 이 실패하면(또는 `get_session` 자체가 실패하면) 예외가 그대로
    올라가 `app/main.py` 의 전역 `Exception` 핸들러가 503
    `{"status":"degraded","db":"down","alembic_revision":null}` 로 매핑한다
    (비밀·예외 원문 미포함). `alembic_version` 테이블이 없으면(드문 경우)
    `alembic_revision` 만 `None` 으로 두고 `status`/`db` 는 내려가지 않는다
    -- "접속 실패"와 "테이블 없음"은 다른 상황이다.

    이 엔드포인트는 툴이 아니므로 `agent_traces` 를 남기지 않는다(01-plan
    U8 지시).
    """
    session.execute(text("SELECT 1"))
    try:
        revision = session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
    except Exception:
        session.rollback()
        revision = None
    return HealthOut(status="ok", db="up", alembic_revision=revision)


@router.post("/answers/{question_id}", response_model=AnswerOut)
def submit_answer(
    question_id: int,
    body: AnswerIn,
    session: Session = Depends(get_session),
) -> AnswerOut:
    """S3.4 턴 N+1 의 **앞 절반만**(칩 선택 → 답 저장). `answer_question`
    호출까지가 끝이며, 저장된 context 로 루프를 재개하거나 후속 툴을
    호출하지 않는다 -- 그 화살표(턴 N+1 뒤 절반)는 **P5-loop** 이 이
    라우트를 확장해서 잇는다(01-plan 결정 1).
    """
    ctx = build_ctx(session, question_id)
    result = answer_question(ctx, question_id, body.answer)
    return AnswerOut(question_id=result.question_id, status=result.status)
