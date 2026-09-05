"""Refs: P2-tools R7 D1 D2 S3.4 -- `ask_user`/`answer_question`/`question_status`:
비동기 대기 질문 모델의 저장 규약.

이 모듈은 "언제 물을지"(임계치 `T_merge`/`T_new`, 확신도 판정)를 다루지 않는다
-- 그것은 **P3-er** 의 몫이다(01-plan 범위 46행, 원칙2·4). 여기서 하는 일은
`ask_user(kind, question, options, context)` 가 호출됐을 때 `pending_questions`
에 저장하고 `{question_id, status:"pending"}` 을 돌려준 뒤 **그 턴을 그대로
종료**하는 것, 그리고 답이 왔을 때(`answer_question`) 그 답을 검증·저장하는
것뿐이다(D2 "동기 대기(sleep/poll) 금지"). 다른 툴을 호출하지 않는다 --
`ask_user` 를 다른 툴에 합치지 않는다(D2, 원칙4 "모른다를 판단하는 행동").

## status 파생 (F-081752, S3.4)

`pending_questions` 에는 `status` 컬럼이 없다(S3.1, P1 04-review §7). 세 값은
애플리케이션이 파생시킨다(`question_status`, DB 를 건드리지 않는 순수 함수):

- `answered_at IS NOT NULL` → `"answered"`
- `answered_at IS NULL` 이고 `created_at + QUESTION_TTL <= now` → `"expired"`
- 그 밖(`answered_at IS NULL` 이고 아직 만료 전) → `"pending"`

만료되어도 `answered_at` 은 `NULL` 로 남는다(S3.4 "미답변 24시간 후 만료
(`answered_at` null 유지, status=expired)") -- `answer_question` 이 만료된
질문에 답을 시도해도 `answered_at` 을 채우지 않고 거절한다.

## 긍정 답 규약 (F-b97a06, `app/tools/persons.py` 의 단일 출처와 같은 키)

D1("승인 시에만 `create_person`")·D6("확인을 거친 경우에만 `display_name`
갱신")은 `app/tools/persons.py._require_confirmation` 이 `pending_questions
.context[AFFIRMATIVE_KEY]`(`"affirmative_options"`, `app/tools/types.py`)를
긍정 선택지 목록으로 읽는다는 것을 전제한다. `create_person` 경로로 이어지는
`kind`(`identity`/`new_person`, D01 "new_person 질문 → create_person 경로")는
`ask_user` 호출 시점에 이 키가 **없으면 그 자리에서 `InvalidValue`** 로
거절한다 -- 이 검사가 없으면 U4 의 `_require_confirmation` 이 항상
`not_affirmative` 로 막혀 확인 플로우 자체가 죽은 채로 저장된다(01-plan 지시
"이 검사가 없으면 U4 의 create_person 이 항상 막힌다"). `kind == "schedule"`
은 이 확인 경로에 쓰이지 않으므로 선택 사항이다.

## context 저장 규약 (미결 2)

`ask_user` 는 호출자가 준 `context` dict 를 **그대로** 저장한다 -- 어떤 키를
넣을지는 그 값을 만드는 P3-er·P5-loop 이 정한다(미결 2). 이 모듈이 하는 것은
`to_jsonable()` 로 JSON 직렬화 가능한 값으로 바꾸고 긴 문자열을 절단하는
것뿐이다(`app.tools.context.TRACE_MAX_STRING` 과 같은 절단 규칙 -- 저장 값과
trace 값의 절단 기준을 하나로 유지한다). 다만 S3.4 "비밀·전체 대화 이력 저장
금지"의 최소 방어로, 최상위 키 이름에 비밀로 보이는 단어
(`password`/`api_key`/`token`/`secret`/`authorization`, 대소문자 무관)가
있으면 `InvalidValue` 로 거절한다 -- 이것은 탐지이지 마스킹이 아니다: 값이
아니라 **키 이름**만 보고, 값 내용의 비밀 여부는 판단하지 않는다(값까지
검사하려면 별도 스캐너가 필요하고 이 단위 범위 밖이다).

## 동기 대기 없음 (D2)

이 모듈의 어떤 함수도 `time.sleep`·폴링 루프·응답 대기를 하지 않는다.
`ask_user` 는 저장 후 즉시 돌아오고, 답은 별도 호출(`answer_question`,
`POST /answers/{question_id}` 는 U8 몫)로 비동기에 들어온다.

## user_id 격리 부재 (F-fbaaae, 열린 소견)

`pending_questions` 에는 `user_id` 컬럼이 없다(`session_id` 만, S3.1).
`answer_question` 은 "다른 사용자의 질문"을 걸러낼 방법이 없다 -- 로컬 단일
사용자(`APP_USER_ID` 고정) 데모에서는 실효 문제가 없지만, 여러 사용자를
지원하게 되면 `session_id` 를 사용자에게 귀속시키는 계층(P5-loop 의 세션
관리)이 이 격리를 대신 맡아야 한다. 이 모듈은 그 전제를 깨지 않는다 --
`question_id` 하나로 전 세션에 걸쳐 조회 가능한 채로 남겨 두고, 이 사각지대를
여기 문서화하는 것까지가 P2-tools 의 몫이다(05-remediation F-fbaaae).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.db.models import QUESTION_KINDS, PendingQuestion
from app.settings import QUESTION_TTL
from app.tools.context import ToolContext, to_jsonable, traced
from app.tools.types import (
    AFFIRMATIVE_KEY,
    InvalidValue,
    PendingQuestionOut,
    QuestionNotAnswerable,
    QuestionNotFound,
)

#: `question_status` 가 돌려줄 수 있는 값 전체(S3.4 파생 규칙, F-081752).
QUESTION_STATUSES = ("pending", "answered", "expired")

#: `ask_user` 의 context 최상위 키 이름 방어(S3.4 "비밀 저장 금지"의 최소
#: 방어) -- 값이 아니라 키 이름만 본다. 대소문자 무관 부분 일치(예:
#: `"api_key"`/`"apiKey"`/`"user_token"` 모두 걸린다).
_SECRET_KEY_MARKERS = ("password", "api_key", "token", "secret", "authorization")

#: `kind` 가 이 안이면 `ask_user` 호출 시점에 `AFFIRMATIVE_KEY` 를 강제한다
#: (D1/D6 확인 경로로 이어지는 kind -- `_require_confirmation` 이 요구하는
#: kinds 와 같은 집합, `app/tools/persons.py` 참고). `schedule` 은 선택.
_AFFIRMATIVE_REQUIRED_KINDS = ("identity", "new_person")


def _require_aware(value: object, name: str) -> datetime:
    """`value` 가 tz-aware `datetime` 인지 검사한다(정규화는 하지 않는다 --
    `question_status` 는 순수 비교 함수이므로 UTC 변환 없이 그대로 쓴다)."""
    if not isinstance(value, datetime):
        raise InvalidValue(f"{name} must be a tz-aware datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidValue(f"{name} must be tz-aware (naive datetime rejected)")
    return value


def question_status(q: PendingQuestion, now: datetime) -> str:
    """S3.4/F-081752 파생 규칙. 순수 함수 -- DB 를 읽거나 쓰지 않는다.

    `now` 는 tz-aware 여야 한다(naive → `InvalidValue`, "조용한 로컬 시각
    가정 금지" -- `app/tools/records.py._require_aware` 와 같은 원칙).
    """
    _require_aware(now, "now")

    if q.answered_at is not None:
        return "answered"
    if q.created_at + QUESTION_TTL <= now:
        return "expired"
    return "pending"


def _validate_kind(kind: str) -> None:
    if kind not in QUESTION_KINDS:
        raise InvalidValue(f"ask_user: invalid kind '{kind}'")


def _validate_question(question: str) -> str:
    if not isinstance(question, str) or not question.strip():
        raise InvalidValue("ask_user: question must not be empty")
    return question.strip()


def _validate_options(options: list[str]) -> list[str]:
    if not isinstance(options, list) or not options:
        raise InvalidValue("ask_user: options must be a non-empty list")

    normalized: list[str] = []
    seen: set[str] = set()
    for option in options:
        if not isinstance(option, str) or not option.strip():
            raise InvalidValue("ask_user: each option must be a non-empty string")
        stripped = option.strip()
        if stripped in seen:
            raise InvalidValue(f"ask_user: duplicate option '{stripped}'")
        seen.add(stripped)
        normalized.append(stripped)
    return normalized


def _validate_context(context: dict, *, kind: str, options: list[str]) -> dict:
    if not isinstance(context, dict):
        raise InvalidValue("ask_user: context must be a dict")

    for key in context:
        key_lower = str(key).lower()
        for marker in _SECRET_KEY_MARKERS:
            if marker in key_lower:
                raise InvalidValue(
                    f"ask_user: context key '{key}' looks like a secret; not allowed"
                )

    if kind in _AFFIRMATIVE_REQUIRED_KINDS:
        affirmative = context.get(AFFIRMATIVE_KEY)
        if (
            not isinstance(affirmative, list)
            or not affirmative
            or not all(isinstance(item, str) for item in affirmative)
        ):
            raise InvalidValue(
                f"ask_user: context['{AFFIRMATIVE_KEY}'] is required for kind="
                f"'{kind}' and must be a non-empty list of strings"
            )
        if not set(affirmative).issubset(set(options)):
            raise InvalidValue(
                f"ask_user: context['{AFFIRMATIVE_KEY}'] must be a subset of options"
            )

    return context


@traced("ask_user")
def ask_user(
    ctx: ToolContext,
    kind: str,
    question: str,
    options: list[str],
    context: dict,
) -> PendingQuestionOut:
    """S3.2 시그니처: `(kind, question, options, context) -> PendingQuestion`.

    `pending_questions` 에 저장하고 `{question_id, status:"pending"}` 을
    돌려준 뒤 그대로 반환한다(D2 -- **sleep/poll/답 대기 없음**, 다른 툴을
    호출하지 않는다). `session_id = ctx.session_id`, `created_at` 은 서버
    기본값(`func.now()`)에 맡긴다.

    검증 순서: `kind` ∈ `QUESTION_KINDS` → `question` 비어있지 않음 →
    `options` 비어있지 않은 str 리스트·중복 없음 → `context` 가 dict 이고
    비밀로 보이는 최상위 키가 없음 → `kind` 가 확인 경로(`identity`/
    `new_person`)면 `context[AFFIRMATIVE_KEY]` 가 `options` 의 비어있지 않은
    부분집합. 하나라도 어긋나면 `InvalidValue` -- DB 에 아무 것도 쓰지 않는다.
    """
    _validate_kind(kind)
    normalized_question = _validate_question(question)
    normalized_options = _validate_options(options)
    validated_context = _validate_context(
        context, kind=kind, options=normalized_options
    )

    stored_context = to_jsonable(validated_context)
    if not isinstance(stored_context, dict):
        # `to_jsonable` 은 dict 입력에 항상 dict 를 돌려주지만(키를 str() 로만
        # 바꾼다), 방어적으로 명시한다 -- JSONB 컬럼은 dict 만 받는다.
        raise InvalidValue("ask_user: context must serialize to a JSON object")

    row = PendingQuestion(
        session_id=ctx.session_id,
        kind=kind,
        question=normalized_question,
        options=list(normalized_options),
        context=stored_context,
    )
    ctx.session.add(row)
    ctx.session.flush()

    return PendingQuestionOut(
        question_id=row.id,
        status="pending",
        kind=row.kind,
        question=row.question,
        options=list(row.options),
    )


@traced("answer_question")
def answer_question(ctx: ToolContext, question_id: int, answer: str) -> PendingQuestionOut:
    """툴 7종 밖의 보조 함수(LLM 에 노출하지 않는다, 01-plan 범위 21행) --
    `POST /answers/{question_id}`(U8)가 호출할 자리다.

    행 없음 → `QuestionNotFound`. 이미 답했음 →
    `QuestionNotAnswerable("already_answered")`. 만료됨 →
    `QuestionNotAnswerable("expired")`(이때 `answered_at` 은 `NULL` 로 남는다
    -- S3.4). `answer` 가 저장된 `options` 밖이면 `InvalidValue`(행 무변경).
    정상이면 `answer`·`answered_at = ctx.now()` 를 기록하고 `"answered"` 를
    돌려준다.

    **user_id 격리 없음**(F-fbaaae, 모듈 docstring "user_id 격리 부재" 참고)
    -- `pending_questions` 에 `user_id` 컬럼이 없어 "다른 사용자의 질문"을
    걸러낼 수 없다. P5-loop 이 세션을 사용자에게 귀속시키는 계층으로 이
    사각지대를 메워야 한다.
    """
    question = ctx.session.get(PendingQuestion, question_id)
    if question is None:
        raise QuestionNotFound("question_not_found")

    status = question_status(question, ctx.now())
    if status == "answered":
        raise QuestionNotAnswerable("already_answered")
    if status == "expired":
        raise QuestionNotAnswerable("expired")

    if not isinstance(answer, str) or answer not in question.options:
        raise InvalidValue("answer_question: answer must be one of the stored options")

    question.answer = answer
    question.answered_at = ctx.now()
    ctx.session.flush()

    return PendingQuestionOut(
        question_id=question.id,
        status="answered",
        kind=question.kind,
        question=question.question,
        options=list(question.options),
    )


def list_pending(
    ctx: ToolContext, session_id: str | None = None
) -> list[PendingQuestionOut]:
    """미답변·미만료 질문 조회(칩 렌더링용 보조 -- S3.4 "프론트 확인 칩 =
    미답변 pending_questions"). 툴 7종 밖이고 판정을 하지 않는 단순 조회라
    `@traced` 를 붙이지 않는다(01-plan 지시, 03-log 에 이유 기록: 조회 자체가
    "판정"이 아니고, 매 폴링/렌더링마다 `agent_traces` 행이 쌓이면 원칙9가
    지키려는 "판정 근거"의 신호 대 잡음비가 나빠진다 -- 7개 툴 + 답변 저장만
    trace 하는 01-plan 25행 규약을 넘지 않는다).

    `session_id` 를 생략하면 `ctx.session_id`(현재 세션)를 쓴다. `created_at`
    오름차순으로 돌려준다.
    """
    target_session_id = session_id if session_id is not None else ctx.session_id
    rows = (
        ctx.session.execute(
            select(PendingQuestion)
            .where(PendingQuestion.session_id == target_session_id)
            .where(PendingQuestion.answered_at.is_(None))
            .order_by(PendingQuestion.created_at.asc())
        )
        .scalars()
        .all()
    )

    now = ctx.now()
    return [
        PendingQuestionOut(
            question_id=row.id,
            status="pending",
            kind=row.kind,
            question=row.question,
            options=list(row.options),
        )
        for row in rows
        if question_status(row, now) == "pending"
    ]
