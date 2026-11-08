"""Refs: P5-loop S3.2 S3.4 원칙7 원칙9 -- U5 응답 단계(결정 B(i) 템플릿).

## 이 모듈이 하는 일과 하지 않는 일

`build_reply()` 는 그 턴에 실제로 기록된 것(이벤트·일정 수)과 실패·상한
초과 여부, 되묻기가 있다면 그 질문 문장만 **정해진 한국어 문장 틀**에
끼워 하나의 문자열을 만든다. 감정·고민이 담긴 발화가 들어와도 이 함수가
보는 것은 "몇 건을 기억했는가"라는 숫자뿐이므로, 공감·조언·위로 문장을
만들어낼 자리가 코드 안에 아예 없다(원칙7 경계 "감정·고민에 대한 대화는
하지 않는다" -- 구조적으로 보장한다, 결정 B(i) 확정 근거 ①). LLM 을 다시
부르지 않는다(호출은 인식 단계 1회로 유지, 원칙8 재현성) -- 이 모듈은
어떤 네트워크 호출도, DB 접근도 하지 않는 순수 함수다.

## 템플릿이 다루는 신호

- `stored_events`/`stored_schedules`: 그 턴에 실제로 `add_event`/
  `add_schedule` 이 성공한 건수(기록 단계, U5 `loop.py`).
- `stored_facts`(FIX-016): 그 턴에 실행에 성공한 `update_person(facts=…)`
  의 키 수(인물별 중복 제거, `RecordOutcome.fact_keys_by_person`). 사실만
  저장한 턴이 "새로 기억한 것이 없어요" 라고 답하던 것을 막는다. 키·값
  문자열은 받지 않고 건수만 받는다(결정 B(i) 규약 유지).
- `failed_count`: 게이트를 통과했지만 실행 중 `ToolError` 로 끝난 제안 수
  (R-24, `loop_record.output.failed`).
- `limit_hit`: 게이트 상한 초과로 일부 제안이 버려졌는가(결정 A(i)).
- `pending_question`: 그 턴이 되묻기로 끝났다면 그 질문(`identity`/
  `new_person`/`schedule` 공통, `app.tools.types.PendingQuestionOut`) --
  질문 문구만 그대로 붙이고 이 모듈이 다시 쓰지 않는다(질문 문구의 단일
  출처는 ER `_build_ask_payload`/U5 `_ask_schedule` 이다).

## 조회 답 (P5b U3, CR-004 · D16 -- 순수 층)

`build_reply()` 아래에 조회 턴의 답 생성 도구를 둔다. 이 절의 코드는 DB·
루프·API 를 모른다(근거 자료는 `PersonCardOut` 한 건을 인자로 받을 뿐이고,
폴백 분기는 U4 `loop.py` 몫이다 -- 결정 E-4).

- `QueryAnswerer` Protocol·공급자 3종·`FakeQueryAnswerer` -- `app/briefing/
  compose.py` 의 작성기와 같은 모양(구조화 출력 `{answer: string}`).
- `validate_query_answer(text) -> str | None` -- 사유 또는 통과(None).
  검사 순서 empty -> 줄 수 -> 길이 -> 금지 표현(결정 E-2·E-3).
- `template_query_answer()`·`no_record_reply()`·`no_mention_reply()` --
  LLM 0 의 결정적 문구(결정 E-5).
- 프롬프트에는 이벤트 원문(`raw_utterance`)·인물 id·환경변수·키를 넣지
  않는다(카드 응답에 원문 필드가 없다, 결정 D).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Protocol

from app.briefing.compose import REASON_FORBIDDEN_EXPRESSION, REASON_TOO_LONG
from app.briefing.types import BRIEFING_FORBIDDEN_EXPRESSIONS
from app.er.judge import (
    _to_gemini_schema,
    call_with_error_mapping,
    call_with_gemini_error_mapping,
    select_provider,
)
from app.er.types import JudgeUnavailable
from app.settings import (
    ER_JUDGE_MAX_RETRIES,
    ER_JUDGE_TIMEOUT,
    QUERY_ANSWER_MAX_CHARS,
    QUERY_ANSWER_MAX_LINES,
    QUERY_TIMELINE_LIMIT,
    user_timezone,
)
from app.tools.types import PendingQuestionOut

if TYPE_CHECKING:  # 타입 힌트 전용 -- `app.api` 초기화가 `app.agent` 를 다시 import 해 생기는 순환을 피한다.
    from app.api.schemas import PersonCardOut

#: 아무것도 기억하지 못한 턴(제안이 없거나 전부 거부됨)의 기본 문장.
_NOTHING_STORED = "이번 발화에서는 새로 기억한 것이 없어요."


def build_reply(
    *,
    stored_events: int,
    stored_schedules: int,
    stored_facts: int = 0,
    failed_count: int = 0,
    limit_hit: bool = False,
    pending_question: PendingQuestionOut | None = None,
) -> str:
    """그 턴의 결과를 결정적 한국어 문장 하나로 조립한다(결정 B(i)).

    숫자·불리언·`PendingQuestionOut.question` 문자열만 입력으로 받는다 --
    발화 원문·이벤트 `content`·감정 표현은 이 함수에 들어오지 않으므로
    반영될 수도 없다(원칙7 부정 테스트가 확인하는 지점)."""

    parts: list[str] = []
    if stored_events:
        parts.append(f"이벤트 {stored_events}건")
    if stored_schedules:
        parts.append(f"일정 {stored_schedules}건")
    if stored_facts:
        parts.append(f"사실 {stored_facts}건")

    if parts:
        sentence = "기억했어요: " + ", ".join(parts) + "."
    else:
        sentence = _NOTHING_STORED

    if failed_count:
        sentence += f" ({failed_count}건은 저장하지 못했어요.)"
    if limit_hit:
        sentence += " 한 번에 너무 많아 일부만 기억했어요."

    if pending_question is not None:
        sentence += "\n" + pending_question.question

    return sentence


# ---------------------------------------------------------------------------
# 조회 답 -- 사유 어휘·고정 문구 (결정 E-3·E-5·F·J)
# ---------------------------------------------------------------------------

REASON_EMPTY = "empty"
REASON_TOO_MANY_LINES = "too_many_lines"
# REASON_TOO_LONG·REASON_FORBIDDEN_EXPRESSION 은 compose.py 의 것을 재사용한다.

#: 결정 J -- 해석하지 않은 언급이 있을 때 답 끝에 붙는 줄(붙이는 것은 U4).
QUERY_ONE_AT_A_TIME_HINT = "한 번에 한 사람씩 물어봐 주세요."
#: 결정 F ① -- `answer_source == "llm"` 인 답 끝에 붙는 문장(붙이는 것은 U4).
QUERY_MORE_HINT = "자세한 건 인물 화면에서 볼 수 있어요."

_NO_LAST_CONTACT = "마지막 접촉 기록 없음"
_NO_MENTION_REPLY = "누구에 대해 물어보셨는지 알아듣지 못했어요. 이름을 넣어 다시 물어봐 주세요."

QUERY_ANSWER_TOOL_NAME = "report_query_answer"

_QUERY_ANSWER_TOOL_DESCRIPTION = (
    "사용자가 물은 인물 정보에 대해, 주어진 인물 카드 자료에 있는 사실만으로 "
    "짧은 한국어 답을 쓴다."
)

#: 구조화 출력 -- `{answer: string}` 하나(결정 E-1).
QUERY_ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
    "additionalProperties": False,
}

#: 프롬프트 카드의 관계·위계 풀어쓰기(어휘는 `app/db/models.py` 의 RELATION_TAGS·HIERARCHIES).
#: 사전 밖 값은 원문 그대로 쓴다.
_RELATION_DESC = {"가족": "가족", "연인": "연인", "친구": "친구", "직장": "직장 관계", "지인": "지인"}
_HIERARCHY_DESC = {"상": "상(윗사람)", "동": "동(같은 급)", "하": "하(아랫사람)"}

_QUERY_SYSTEM_PROMPT = (
    "너는 사용자가 기록해 둔 한 인물의 정보를 묻는 질문에 답하는 보조 도구다. "
    "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다 — "
    "평가·조언·감정 대화는 하지 않는다"
    f" 아래 인물 카드 자료만 근거로 1~{QUERY_ANSWER_MAX_LINES}줄 한국어로 답하고, "
    "관계나 위계를 물으면 [인물 카드]의 '관계' 줄을 그대로 답하라 — 그것도 기록된 사실이다. "
    "자료에 없는 것은 '기록이 없어요'라고 답하라. 추측하거나 새 사실을 만들지 마라. "
    "다른 인물과의 관계는 말하지 마라. 위로·조언·감정 표현을 쓰지 마라. "
    f"{QUERY_ANSWER_TOOL_NAME} 도구로만 답하라."
)


# ---------------------------------------------------------------------------
# 결과 타입·Protocol
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QueryAnswer:
    """조회 답 생성기의 결과. `text` 는 검증 전 원문이다(검증은
    `validate_query_answer`, 폴백은 U4)."""

    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    provider: str = ""
    model: str | None = None

    def trace_tokens(self) -> tuple[int, int]:
        """`ComposedBriefing.trace_tokens()` 와 같은 반환 모양 -- trace 의
        `tokens_in`/`tokens_out` 을 채운다."""

        return (self.tokens_in, self.tokens_out)


class QueryAnswerer(Protocol):
    def answer(self, question: str, evidence: "PersonCardOut", now: datetime) -> QueryAnswer: ...


# ---------------------------------------------------------------------------
# 날짜·근거 보조
# ---------------------------------------------------------------------------


def _fmt_date(value: datetime) -> str:
    """사용자 시간대 기준 `M월 D일`(0 패딩 없음, 결정 E-5)."""

    local = value.astimezone(user_timezone())
    return f"{local.month}월 {local.day}일"


def has_evidence(evidence: "PersonCardOut") -> bool:
    """사실·패턴·타임라인·일정이 하나라도 있는가(결정 E-5 근거 0건 판별)."""

    return bool(
        evidence.facts or evidence.patterns or evidence.timeline or evidence.upcoming_schedules
    )


# ---------------------------------------------------------------------------
# 프롬프트 (결정 D·E-6)
# ---------------------------------------------------------------------------


def build_query_answer_prompt(
    question: str, evidence: "PersonCardOut", now: datetime
) -> tuple[str, str]:
    """`(system, user_text)`. user_text 에는 질문 원문 1건·현재 시각·인물 카드
    근거만 넣는다 -- 인물/사실/이벤트 id·`source_count`·`briefed_at`·이벤트
    원문·환경변수·키는 넣지 않는다(결정 D). 타임라인은 카드 순서 그대로 앞에서
    `QUERY_TIMELINE_LIMIT` 건만 쓴다."""

    person = evidence.person
    lines: list[str] = [
        f"질문: {question}",
        f"현재 시각: {now.astimezone(user_timezone()).isoformat()}",
        "",
        "[인물 카드]",
        f"이름: {person.display_name}",
        f"관계: {_RELATION_DESC.get(person.relation_tag, person.relation_tag)}, "
        f"위계 {_HIERARCHY_DESC.get(person.hierarchy, person.hierarchy)}",
        "별칭: " + (", ".join(evidence.aliases) if evidence.aliases else "없음"),
        "마지막 접촉: "
        + (_fmt_date(evidence.last_contact_at) if evidence.last_contact_at else "기록 없음"),
        "알고 있는 사실:",
    ]
    if evidence.facts:
        lines += [f"- {f.key}={f.value} ({_fmt_date(f.updated_at)})" for f in evidence.facts]
    else:
        lines.append("- 없음")
    lines.append("반복 패턴:")
    if evidence.patterns:
        lines += [f"- {p.value}" for p in evidence.patterns]
    else:
        lines.append("- 없음")
    lines.append(f"최근 타임라인(최대 {QUERY_TIMELINE_LIMIT}건):")
    timeline = evidence.timeline[:QUERY_TIMELINE_LIMIT]
    if timeline:
        lines += [f"- [{t.type}] {t.content} ({_fmt_date(t.occurred_at)})" for t in timeline]
    else:
        lines.append("- 없음")
    lines.append("예정된 일정:")
    if evidence.upcoming_schedules:
        lines += [f"- {s.title} ({_fmt_date(s.scheduled_at)})" for s in evidence.upcoming_schedules]
    else:
        lines.append("- 없음")
    return _QUERY_SYSTEM_PROMPT, "\n".join(lines)


# ---------------------------------------------------------------------------
# 검증기·템플릿·고정 응답 (결정 E-2·E-3·E-5)
# ---------------------------------------------------------------------------


def validate_query_answer(text: str) -> str | None:
    """사유 문자열 또는 `None`(통과). 순서 empty -> 줄 수 -> 길이 -> 금지
    표현. 상한은 `> 상한` 일 때만 거부한다(상한 자체는 통과)."""

    stripped = text.strip()
    if not stripped:
        return REASON_EMPTY
    non_blank = [line for line in stripped.splitlines() if line.strip()]
    if len(non_blank) > QUERY_ANSWER_MAX_LINES:
        return REASON_TOO_MANY_LINES
    if len(stripped) > QUERY_ANSWER_MAX_CHARS:
        return REASON_TOO_LONG
    if any(bad in text for bad in BRIEFING_FORBIDDEN_EXPRESSIONS):
        return REASON_FORBIDDEN_EXPRESSION
    return None


def template_query_answer(evidence: "PersonCardOut", now: datetime) -> str:
    """LLM 0 의 결정적 답(결정 E-5). 근거가 하나도 없으면 관계만 말한다.
    `now` 는 시그니처 계약상 받는다(날짜는 카드의 시각을 사용자 시간대로
    바꿔 쓴다)."""

    person = evidence.person
    head = f"{person.display_name} — {person.relation_tag}·{person.hierarchy}"
    if not has_evidence(evidence):
        return f"{head}로 기억하고 있어요. 그 밖의 기록은 아직 없어요."
    last = (
        f"마지막 접촉 {_fmt_date(evidence.last_contact_at)}"
        if evidence.last_contact_at
        else _NO_LAST_CONTACT
    )
    count = len(evidence.facts) + len(evidence.patterns)
    return f"{head}, {last}, 알고 있는 것 {count}건. {QUERY_MORE_HINT}"


def no_record_reply(mentions: list[str]) -> str:
    """확정 인물 0 -- 입력 순서대로 `"a", "b"에 대한 기록이 없어요.`"""

    quoted = ", ".join(f'"{m}"' for m in mentions)
    return f"{quoted}에 대한 기록이 없어요."


def no_mention_reply() -> str:
    return _NO_MENTION_REPLY


# ---------------------------------------------------------------------------
# 공급자 구현 (compose.py 작성기와 같은 모양 -- D11)
# ---------------------------------------------------------------------------


def _parse_answer(raw: Any, *, tokens_in: int, tokens_out: int, provider: str, model: str | None) -> QueryAnswer:
    """구조 파싱 -- `answer` 가 문자열이 아니면 스키마 위반이다."""

    answer = raw.get("answer") if isinstance(raw, dict) else None
    if not isinstance(answer, str):
        raise JudgeUnavailable("schema")
    return QueryAnswer(
        text=answer, tokens_in=tokens_in, tokens_out=tokens_out, provider=provider, model=model
    )


@dataclass
class ClaudeQueryAnswerer:
    """Anthropic SDK 강제 `tool_use`. 모델 env·타임아웃·재시도는 브리핑
    작성기와 같은 이름·상수를 공유한다."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        if self.client is None:
            import anthropic  # 지연 import

            self.client = anthropic.Anthropic(timeout=self.timeout, max_retries=self.max_retries)

    def answer(self, question: str, evidence: "PersonCardOut", now: datetime) -> QueryAnswer:
        import anthropic  # 예외 클래스·매핑용 지연 import

        system, user_text = build_query_answer_prompt(question, evidence, now)
        tool_schema = {
            "name": QUERY_ANSWER_TOOL_NAME,
            "description": _QUERY_ANSWER_TOOL_DESCRIPTION,
            "input_schema": QUERY_ANSWER_SCHEMA,
        }
        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_text}],
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": QUERY_ANSWER_TOOL_NAME},
            ),
        )

        tool_use_input = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use":
                tool_use_input = block.input
                break
        if tool_use_input is None:
            raise JudgeUnavailable("schema")

        usage = getattr(response, "usage", None)
        return _parse_answer(
            tool_use_input,
            tokens_in=getattr(usage, "input_tokens", 0) if usage is not None else 0,
            tokens_out=getattr(usage, "output_tokens", 0) if usage is not None else 0,
            provider="anthropic",
            model=getattr(response, "model", self.model),
        )


@dataclass
class OpenAIQueryAnswerer:
    """OpenAI 강제 function-calling."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if self.client is None:
            import openai  # 지연 import

            self.client = openai.OpenAI(timeout=self.timeout, max_retries=self.max_retries)

    def answer(self, question: str, evidence: "PersonCardOut", now: datetime) -> QueryAnswer:
        import openai  # 예외 클래스·매핑용 지연 import

        system, user_text = build_query_answer_prompt(question, evidence, now)
        tool_schema = {
            "type": "function",
            "function": {
                "name": QUERY_ANSWER_TOOL_NAME,
                "description": _QUERY_ANSWER_TOOL_DESCRIPTION,
                "parameters": QUERY_ANSWER_SCHEMA,
            },
        }
        response = call_with_error_mapping(
            openai,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_text},
                ],
                tools=[tool_schema],
                tool_choice={"type": "function", "function": {"name": QUERY_ANSWER_TOOL_NAME}},
            ),
        )

        tool_calls = None
        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            tool_calls = getattr(message, "tool_calls", None) if message is not None else None
        if not tool_calls:
            raise JudgeUnavailable("schema")
        try:
            raw = json.loads(tool_calls[0].function.arguments)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        usage = getattr(response, "usage", None)
        return _parse_answer(
            raw,
            tokens_in=getattr(usage, "prompt_tokens", 0) if usage is not None else 0,
            tokens_out=getattr(usage, "completion_tokens", 0) if usage is not None else 0,
            provider="openai",
            model=getattr(response, "model", self.model),
        )


@dataclass
class GeminiQueryAnswerer:
    """`google-genai` 구조화 출력. `GEMINI_MODEL` 기본값 없음(브리핑
    작성기와 같은 관례)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT

    def __post_init__(self) -> None:
        if self.model is None:
            model = os.environ.get("GEMINI_MODEL")
            if not model:
                from app.tools.types import InvalidValue

                raise InvalidValue(
                    "GeminiQueryAnswerer: GEMINI_MODEL 환경변수가 필요하다(기본값 "
                    "없음 -- judge.py::GeminiJudge 와 같은 관례). Google AI "
                    "콘솔에서 확인한 모델 이름을 .env 의 GEMINI_MODEL 에 넣는다"
                )
            self.model = model
        if self.client is None:
            from google import genai  # 지연 import
            from google.genai import types as genai_types

            self.client = genai.Client(
                http_options=genai_types.HttpOptions(timeout=int(self.timeout * 1000))
            )

    def answer(self, question: str, evidence: "PersonCardOut", now: datetime) -> QueryAnswer:
        from google.genai import types as genai_types  # 요청 조립용 지연 import

        system, user_text = build_query_answer_prompt(question, evidence, now)
        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            response_mime_type="application/json",
            response_schema=_to_gemini_schema(QUERY_ANSWER_SCHEMA),
        )
        response = call_with_gemini_error_mapping(
            lambda: self.client.models.generate_content(
                model=self.model, contents=user_text, config=config
            )
        )

        text = getattr(response, "text", None)
        if not text:
            raise JudgeUnavailable("schema")
        try:
            raw = json.loads(text)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        usage = getattr(response, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage is not None else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage is not None else 0
        return _parse_answer(
            raw,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            provider="gemini",
            model=getattr(response, "model_version", None) or self.model,
        )


#: 이름 -> 무인자 팩토리 등록표(`BRIEFING_COMPOSERS` 와 같은 모양). Fake 는 뺀다.
QUERY_ANSWERERS: dict[str, Callable[[], QueryAnswerer]] = {
    "anthropic": ClaudeQueryAnswerer,
    "openai": OpenAIQueryAnswerer,
    "gemini": GeminiQueryAnswerer,
}


def answerer_from_env(env: dict[str, str] | None = None) -> QueryAnswerer:
    """`select_provider(env)` -> `QUERY_ANSWERERS[name]()` (D11)."""

    return QUERY_ANSWERERS[select_provider(env)]()


@dataclass
class FakeQueryAnswerer:
    """테스트용 결정적 답 생성기(네트워크 0). `table` 키 = 질문 원문 -> 답
    문자열(없으면 `""`). `fail` 이면 `JudgeUnavailable(fail)`. 호출마다
    `call_count` 가 늘어난다."""

    table: dict[str, str] = field(default_factory=dict)
    fail: str | None = None
    call_count: int = field(default=0, init=False)

    def answer(self, question: str, evidence: "PersonCardOut", now: datetime) -> QueryAnswer:
        self.call_count += 1
        if self.fail is not None:
            raise JudgeUnavailable(self.fail)
        return QueryAnswer(
            text=self.table.get(question, ""), tokens_in=0, tokens_out=0, provider="fake", model=None
        )
