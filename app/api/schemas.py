"""Refs: P2-tools U8 결정 11 -- HTTP 요청/응답 스키마(pydantic v2).

`app/tools/types.py` 의 `*Out` dataclass(툴 반환 DTO, LLM/함수 경계)와
섞지 않는다 -- 이 모듈의 모델은 HTTP 경계에만 쓰인다(결정 11).

응답 모델 어디에도 접속 문자열·비밀번호·예외 원문을 담는 필드가 없다
(security.md §1) -- `HealthOut` 은 상태 문자열과 alembic 리비전 번호만
돌려준다.

## U6 추가분 -- `ChatIn`/`ChatOut` (P5-loop `POST /chat`)

`ChatOut` 은 `app.agent.types.TurnResult.to_dict()` 와 같은 모양이다 --
루프가 이미 고정한 스키마(01-plan U1 "세 output 스키마" 근처)를 HTTP
경계에서 그대로 반사할 뿐, 새 직렬화 규칙을 만들지 않는다. 라우트는
`ChatOut.model_validate(turn.to_dict())` 로 옮긴다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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


class ChatIn(BaseModel):
    """`POST /chat` 요청 본문. 발화 한 건 = 턴 한 번(01-plan U6 "요청 1건 =
    발화 1건 = 턴 1회")."""

    utterance: str = Field(min_length=1)


class StoredOut(BaseModel):
    """그 턴에 실제로 늘어난 행 수(`app.agent.types.StoredSummary` 와 같은
    모양 -- `app/tools/types.py` 의 `*Out` dataclass 와 섞지 않는다는 결정
    11 을 따라 이 모듈에 별도 pydantic 모델로 둔다)."""

    persons: int
    events: int
    schedules: int


class ChatPendingQuestionOut(BaseModel):
    """되묻기로 끝난 턴의 대기 질문(`app.tools.types.PendingQuestionOut` 과
    같은 모양)."""

    question_id: int
    status: str
    kind: str
    question: str
    options: list[str]


class ChatOut(BaseModel):
    """`POST /chat` 응답 -- `app.agent.types.TurnResult.to_dict()` 를 그대로
    옮긴다(모듈 docstring 참고). `stop_reason` ∈ `{"ask_user","limit",None}`
    (U5 03-log). `pending_question` 이 `None` 이면 그 턴은 되묻기 없이
    끝난 것이다."""

    reply: str
    session_id: str
    stored: StoredOut
    pending_question: ChatPendingQuestionOut | None = None
    stop_reason: str | None = None
    trace_ids: list[int] = Field(default_factory=list)
