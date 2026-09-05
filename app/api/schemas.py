"""Refs: P2-tools U8 결정 11 -- HTTP 요청/응답 스키마(pydantic v2).

`app/tools/types.py` 의 `*Out` dataclass(툴 반환 DTO, LLM/함수 경계)와
섞지 않는다 -- 이 모듈의 모델은 HTTP 경계에만 쓰인다(결정 11).

응답 모델 어디에도 접속 문자열·비밀번호·예외 원문을 담는 필드가 없다
(security.md §1) -- `HealthOut` 은 상태 문자열과 alembic 리비전 번호만
돌려준다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AnswerIn(BaseModel):
    """`POST /answers/{question_id}` 요청 본문. `answer` 는 저장된
    `pending_questions.options` 안의 문자열이어야 하며, 그 검증은
    `app.tools.questions.answer_question` 이 한다(여기서는 형식만 본다)."""

    answer: str


class AnswerOut(BaseModel):
    """`POST /answers/{question_id}` 응답. S3.4 턴 N+1 앞 절반(답 저장)까지
    -- 루프 재개·후속 툴 호출 결과는 담지 않는다(P5-loop 이 이 스키마를
    확장한다)."""

    question_id: int
    status: str


class HealthOut(BaseModel):
    """`GET /health` 응답. 접속 문자열·호스트·포트·비밀번호를 담지 않는다."""

    status: Literal["ok", "degraded"]
    db: Literal["up", "down"]
    alembic_revision: str | None = None
