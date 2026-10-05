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

## U7 추가분 -- `AnswerOut` 확장 (재개, R6·R7)

`AnswerOut` 은 답 저장 결과(`question_id`·`status`, P2 그대로) **뒤에**
`ChatOut` 과 같은 다섯 필드(`reply`·`stored`·`pending_question`·
`stop_reason`·`trace_ids`)를 이어 붙인다 -- `resume_turn()` 이 돌려주는
`TurnResult` 를 `ChatOut` 과 같은 방식으로 그대로 반사한다(같은 값을
두 가지 모양으로 만들지 않는다). 이 확장은 **기존 응답 모양을 바꾼다**
-- `POST /answers/{question_id}` 는 이제 항상 재개까지 돈 결과를
돌려주므로, `question_id`/`status` 두 필드만 보던 P2 시절의 응답과는
다르다(`tests/test_api.py` 의 기존 단언은 이 확장에 맞춰 갱신했다 --
단언을 없애지 않고 기대값만 넓혔다, 01-plan 리스크 절 "AnswerOut 확장은
기존 테스트를 건드린다" 그대로).

## U6 추가분 -- `BriefingRunIn`/`BriefingRunOut` (P6-briefing `POST /briefings/run`)

Refs: P6-briefing S3.6 R12 원칙9 -- U6. `app.briefing.types.
BriefingRunResult.briefings[]`/`skipped[]` 는 평범한 dict 목록이라
(모듈 docstring 참고) 이 모듈이 그 모양을 그대로 pydantic 모델로
감싼다(결정 11과 같은 경계 -- `*Out` dataclass 를 재사용하지 않는다).
`run_id` 는 `BriefingRunResult.session_id`(`"briefing:<uuid4>"`, 결정
I)를 그대로 옮긴 것이다 -- 그 실행이 남긴 `briefing_run`/
`briefing_compose` trace 를 사용자가 되짚을 수 있다(원칙9). 어떤
필드에도 `raw_utterance` 원문을 담지 않는다(01-plan "지킬 불변식" --
`get_briefing` 의 `EventOut` 결정과 같은 이유, `BriefingItemOut` 은
`app.briefing.run` 이 이미 원문을 뺀 dict 를 그대로 받는다)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnswerIn(BaseModel):
    """`POST /answers/{question_id}` 요청 본문. `answer` 는 저장된
    `pending_questions.options` 안의 문자열이어야 하며, 그 검증은
    `app.tools.questions.answer_question` 이 한다(여기서는 형식만 본다)."""

    answer: str


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


class AnswerOut(BaseModel):
    """`POST /answers/{question_id}` 응답. `question_id`/`status` 는 답
    저장 자체의 결과(P2, 변경 없음)이고, 나머지 다섯 필드는 그 답으로
    재개된 턴(`resume_turn()` 의 `TurnResult`)의 결과다(U7, 모듈 docstring
    "U7 추가분" 참고) -- `ChatOut` 과 같은 다섯 필드를 그대로 쓴다."""

    question_id: int
    status: str
    reply: str
    stored: StoredOut
    pending_question: ChatPendingQuestionOut | None = None
    stop_reason: str | None = None
    trace_ids: list[int] = Field(default_factory=list)


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


# ---------------------------------------------------------------------------
# U6 추가분 -- `POST /briefings/run` (P6-briefing, 모듈 docstring 참고)
# ---------------------------------------------------------------------------


class BriefingRunIn(BaseModel):
    """`POST /briefings/run` 요청 본문. 본문 전체가 선택이다(결정 C(ii))
    -- 본문을 아예 안 보내면 `app.api.routes` 가 이 모델의 기본값
    (`schedule_id=None`)으로 다룬다(`routes.run_briefings_endpoint` 의
    파라미터가 `BriefingRunIn | None = None` 인 이유는 그 라우트 docstring
    참고)."""

    schedule_id: int | None = None


class BriefingBasisOut(BaseModel):
    """줄·제안 공통 근거 모양(`app.briefing.types.BriefingLine`/
    `Suggestion` 의 `basis` 그대로, 결정 D)."""

    fact_keys: list[str] = Field(default_factory=list)
    event_ids: list[int] = Field(default_factory=list)


class BriefingLineOut(BaseModel):
    """요약 줄 하나(`app.briefing.types.BriefingLine.to_dict()` 그대로)."""

    text: str
    basis: BriefingBasisOut


class BriefingSuggestionOut(BaseModel):
    """한 줄 행동 제안(원칙7, `app.briefing.types.Suggestion.to_dict()`
    그대로)."""

    text: str
    basis: BriefingBasisOut


class BriefingPatternSentenceOut(BaseModel):
    """패턴 문장 하나 -- 패턴 판정은 규칙(원칙6), 문장화만 LLM/템플릿."""

    key: str
    sentence: str


class BriefingItemOut(BaseModel):
    """브리핑 생성 성공 일정 하나(`app.briefing.run.run_briefings()` 가
    조립한 `briefings[]` 항목 그대로, 01-plan 76행 응답 모양). `push` 는
    `Notifier.notify()` 의 반환 문자열(결정 J, `NullNotifier` 는 항상
    `"not_configured"`). **원문(`raw_utterance`)을 담는 필드가 없다**
    (01-plan "지킬 불변식")."""

    schedule_id: int
    person_id: int
    composer: Literal["llm", "template"]
    pattern_sentences: list[BriefingPatternSentenceOut] = Field(default_factory=list)
    lines: list[BriefingLineOut] = Field(default_factory=list)
    suggestion: BriefingSuggestionOut | None = None
    push: str


class BriefingSkippedOut(BaseModel):
    """실패해 격리된 일정 하나(`run_briefings()` 의 `skipped[]` 항목 --
    `app/briefing/run.py` "SQLAlchemyError 처리 규약" 절). `reason` 은
    예외 클래스명뿐이다(security §1, 예외 원문 미포함)."""

    schedule_id: int
    reason: str


class BriefingRunOut(BaseModel):
    """`POST /briefings/run` 응답(01-plan 76행 응답 모양). `run_id` 는
    `app.briefing.types.BriefingRunResult.session_id`(`"briefing:<uuid4>"`,
    결정 I)를 그대로 옮긴 것 -- 그 실행이 남긴 `briefing_run`/
    `briefing_compose` trace 를 이 값으로 되짚을 수 있다(원칙9).
    `generated_at` 은 그 실행의 `ctx.now()`(`BriefingRunResult.now`)다."""

    run_id: str
    generated_at: datetime
    briefings: list[BriefingItemOut] = Field(default_factory=list)
    skipped: list[BriefingSkippedOut] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# P7-push U2 추가분 -- `GET /push/vapid-public-key` · `POST /push/subscriptions`
# (Refs: P7-push S3.1 S3.6 R12)
# ---------------------------------------------------------------------------

#: 엔드포인트 길이 상한(01-plan U2 "endpoint 는 … 길이 상한"). 알려진 푸시
#: 서비스(FCM 등) 엔드포인트는 수백 자 수준이고, 2048 은 흔히 쓰이는 URL
#: 길이 상한 관행과 같다 -- `PUSH_*` 코드 상수(U1, `app/settings.py`)와
#: 같은 "근거를 docstring 에" 관례.
_PUSH_ENDPOINT_MAX_LENGTH = 2048

#: base64url 문자 집합(패딩 `=` 없음 -- 브라우저가 돌려주는 `p256dh`/`auth`
#: 값의 실제 인코딩, 01-plan U2 "base64url").
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class VapidPublicKeyOut(BaseModel):
    """`GET /push/vapid-public-key` 응답(결정 F). 공개키만 담는다 --
    개인키 값은 어떤 응답 모델에도 필드로 두지 않는다(security §1)."""

    public_key: str


class PushSubscriptionKeysIn(BaseModel):
    """브라우저 `PushSubscription.toJSON().keys` 그대로(결정 F). 두 값
    모두 비지 않은 base64url 문자열이어야 한다(01-plan U2 판정 3행) --
    그 밖의 값은 pydantic 이 422 로 되돌린다(`ChatIn.utterance` 의
    `Field(min_length=1)` 과 같은 경계, 결정 11)."""

    p256dh: str
    auth: str

    @field_validator("p256dh", "auth")
    @classmethod
    def _validate_base64url(cls, value: str) -> str:
        if not value or not _BASE64URL_RE.fullmatch(value):
            raise ValueError("push subscription key must be a non-empty base64url string")
        return value


class PushSubscriptionIn(BaseModel):
    """`POST /push/subscriptions` 요청 본문(결정 F) -- 브라우저
    `PushSubscription.toJSON()` 모양 그대로 받는다. `expirationTime` 은
    **받기만 하고 저장하지 않는다**(`push_subscriptions` 에 그 열이
    없다, 01-plan 결정 F)."""

    endpoint: str
    keys: PushSubscriptionKeysIn
    expirationTime: float | None = None

    @field_validator("endpoint")
    @classmethod
    def _validate_endpoint(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("endpoint must start with https://")
        if len(value) > _PUSH_ENDPOINT_MAX_LENGTH:
            raise ValueError("endpoint exceeds maximum length")
        return value


class PushSubscriptionOut(BaseModel):
    """`POST /push/subscriptions` 응답(결정 F, 01-plan 판정 1·2행) --
    개인키·구독 비밀 값을 담지 않는다(security §1)."""

    id: int
    created: bool
