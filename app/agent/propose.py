"""Refs: P5-loop D11 S3.4 원칙1 원칙7 원칙9 -- U2 인식 단계(발화 -> tool_calls
제안, LLM 1회).

## step 이름과 파일 이름의 어긋남 (R-16)
`agent_traces.step` 의 이름은 결정 F(01-plan)로 고정된 `loop_extract` 다.
파일 이름이 `propose.py` 인 것과 달리 trace step 이름은 다시 열지 않는다
(01-plan 86행) -- `loop_extract.output` 에 담기는 값이 "추출 결과
(mentions/events/schedules)" 에서 "**LLM 이 제안한 tool_calls[] 원문**"
으로 바뀌었을 뿐이다. trace 행을 실제로 쓰는 것은 이 모듈이 아니라
`app/agent/loop.py`(U4)다 -- 이 모듈은 순수하게 `Proposal` 값을 만들
뿐 DB 를 건드리지 않는다(ctx 인자를 받지 않는다).

## R-22 -- 5a·5b grep 의 프롬프트 리터럴 함정 (이 단위에서 정한다)
판정 표 5a·5b(01-plan 124~125행)는 `app/agent/` 소스 파일 안에 툴 이름
바로 뒤에 여는 괄호가 붙은 **리터럴 텍스트**(예: 두 툴 이름 각각에 여는
괄호를 이어붙인 완전한 함수 호출 표기)가 있는지를 본다. 이 모듈이 툴
설명을 그런 완전한 호출 표기 문자열로 프롬프트에 그대로 박아 넣으면(예:
이름 뒤에 인자 나열과 닫는 괄호까지 리터럴로 적으면) 그 문자열이 이
소스 안에 그대로 나타나 두 grep 을 오탐(거짓 FAIL)시킨다. **이 단위는
(ㄴ)을 택한다** -- 프롬프트의 툴 설명을 `inspect.signature(app.tools.
<name>)` 으로 **런타임에** 생성한다(게이트 ③ 과 같은 출처 -- 시그니처가
바뀌면 프롬프트·게이트·`tools_check.py` 가 함께 움직인다). `_tool_signature_
line()` 은 툴 이름을 변수로만 다루고(`f"{name}: ..."` 처럼 이름 뒤에
콜론을 쓴다, 여는 괄호가 아니다) 그 결과를 "이름: 인자" 한 줄로만
보여준다 -- 이 소스 파일 어디에도 두 툴 이름 각각에 여는 괄호가 바로
이어붙은 리터럴이 없다(아래 테스트 `test_build_propose_prompt_no_literal_
parenthesis_call_forms_in_source` 가 **생성된 프롬프트**에도 그 표기가
없음을 확인한다).

## 인식 vs 게이트의 경계 (원칙1 "프롬프트 의존 금지")
이 모듈은 **형식만** 본다 -- LLM 구조화 출력이 `{tool_calls:[{name,args}]}`
모양인지, `occurred_at`/`scheduled_at` 문자열을 `datetime` 으로 바꿀 수
있는지까지만 처리한다. 툴 이름이 화이트리스트 안인지, 인자가 시그니처와
맞는지, `person_id` 를 직접 줬는지는 전부 **게이트(U3 `app/agent/gate.py`)**
의 일이다(R-12 "같은 검사를 두 자리에서 하지 않는다"). `_LLM_NOT_CALLABLE`
은 프롬프트에 "이 셋은 제안하지 마라"라고 적기 위한 **안내용** 목록일
뿐이고, 실제 거부(강제)의 단일 출처는 여전히 게이트다.

## 상대 시각 (결정 K, R-23 은 게이트 몫)
프롬프트에 `now` 를 절대 시각으로 준다. `occurred_at`/`scheduled_at` 이
ISO 8601 문자열이면 `datetime` 으로 바꾼다(형식 변환만). 비어 있거나
(`None`) 파싱에 실패하면 그대로 둔다 -- "이벤트는 now 로 채운다"/
"일정은 되묻는다"는 실제 판단은 U5(`loop.py`)와 게이트(U3, R-23)가
한다. 이 모듈은 그 판단에 필요한 값을 만들 뿐이다.

## 공급자 재사용 (D11) -- `app/er/judge.py` 는 import 만 한다
등록표 개념(`select_provider`/`enabled_providers`)과 오류 매핑
(`call_with_error_mapping`/`call_with_gemini_error_mapping`), Gemini 스키마
변환(`_to_gemini_schema`)을 그대로 재사용한다. `PROPOSERS` 는 이 모듈만의
새 등록표다 -- `JUDGES` 와 스키마(`PROPOSAL_SCHEMA` vs `JUDGEMENT_SCHEMA`)가
달라 그 표를 그대로 쓸 수 없지만, 이름 집합(anthropic/openai/gemini)과
선택 로직(`select_provider`)은 공유한다(같은 `LLM_PROVIDER`/
`LLM_PROVIDERS_ENABLED` 환경변수, D11 R-4 "두 진입점이 같은 규칙을 쓴다"
정신을 `judge_from_env`/`proposer_from_env` 사이에도 적용한다).

**이 단위가 스스로 정한 것(설정값)**: 추출 전용 타임아웃·재시도 상수를
새로 만들지 않고 `app.settings.ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES`
를 재사용한다. 모델 env 이름(`ANTHROPIC_MODEL`/`OPENAI_MODEL`/
`GEMINI_MODEL`)도 `judge.py` 의 `*Judge` 클래스와 같은 이름을 그대로
쓴다 -- ER 판정과 추출 제안이 같은 모델을 쓰는 것을 전제한다(별도
`LOOP_PROPOSE_MODEL` 류 이름은 01-plan 산출물 목록에 없다).
"""

from __future__ import annotations

import inspect
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Protocol

from app import tools as app_tools
from app.agent.types import Proposal, ToolCallProposal
from app.db.models import EVENT_TYPES, HIERARCHIES, RELATION_TAGS
from app.er.judge import (
    call_with_error_mapping,
    call_with_gemini_error_mapping,
    select_provider,
    _to_gemini_schema,
)
from app.er.types import JudgeUnavailable
from app.settings import ER_JUDGE_MAX_RETRIES, ER_JUDGE_TIMEOUT

TOOL_NAMES = app_tools.TOOL_NAMES

#: 프롬프트가 "제안하지 마라"고 안내하는 목록일 뿐 -- 실제 거부의 단일
#: 출처는 게이트(U3, 01-plan 60행)다(모듈 docstring "인식 vs 게이트").
_LLM_NOT_CALLABLE: tuple[str, ...] = ("search_person", "ask_user", "get_briefing")

#: 루프가 주입하는 인자라 프롬프트 설명에서 뺀다(`ctx`·`raw_utterance`).
#: 이 목록은 **프롬프트 편의용 부분집합**이며 검증 강제의 단일 출처가
#: 아니다 -- 그 출처는 게이트(U3)의 주입 인자 집합(`ctx`·`person_id`·
#: `raw_utterance`)이다.
_PROMPT_EXCLUDED_PARAMS: tuple[str, ...] = ("ctx", "raw_utterance")

#: `occurred_at`/`scheduled_at` 처럼 ISO 8601 문자열 -> `datetime` 변환이
#: 필요한 인자 이름(툴별). 다른 툴에는 시각 인자가 없다.
_DATETIME_ARG_NAMES: dict[str, tuple[str, ...]] = {
    "add_event": ("occurred_at",),
    "add_schedule": ("scheduled_at",),
}

PROPOSAL_TOOL_NAME = "propose_tool_calls"

_PROPOSAL_TOOL_DESCRIPTION = (
    "발화 하나를 보고 기억에 필요한 tool_calls 목록을 제안한다. 인물은 "
    "person_id 가 아니라 person(언급 문자열)으로 지칭한다."
)

#: 개별 `tool_calls[]` 원소의 `args` 스키마. 툴 7종의 인자를 합친
#: 느슨한 모양이다(`additionalProperties: True`) -- 실제 필수/타입
#: 검증은 게이트(U3, `inspect.signature` 대조)의 일이다(원칙1). `type`/
#: `relation_tag`/`hierarchy` 만 CLAUDE.md 고정 집합 enum 으로 LLM 을
#: **유도**한다(U2 범위 27행 "PROPOSAL_SCHEMA 의 enum 으로 유도할 뿐,
#: 7종 밖 값의 거부는 게이트가 한다").
PROPOSAL_ARG_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "person": {"type": "string"},
        "type": {"type": "string", "enum": list(EVENT_TYPES)},
        "content": {"type": "string"},
        "occurred_at": {"type": ["string", "null"]},
        "title": {"type": "string"},
        "scheduled_at": {"type": ["string", "null"]},
        "display_name": {"type": "string"},
        "aliases": {"type": "array", "items": {"type": "string"}},
        "relation_tag": {"type": "string", "enum": list(RELATION_TAGS)},
        "hierarchy": {"type": "string", "enum": list(HIERARCHIES)},
        "new_alias": {"type": "string"},
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    "additionalProperties": True,
}

#: 판정 JSON 스키마 단일 출처(이 모듈 안에서). 어느 공급자든 이
#: 딕셔너리 그대로를 도구/함수 스키마의 `input_schema`/`parameters`
#: (또는 Gemini `response_schema`)로 쓴다(`JUDGEMENT_SCHEMA` 와 같은
#: 관례, `app/er/judge.py`).
PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "enum": list(TOOL_NAMES)},
                    "args": PROPOSAL_ARG_SCHEMA,
                },
                "required": ["name", "args"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["tool_calls"],
    "additionalProperties": False,
}


class Proposer(Protocol):
    """인식 단계 인터페이스. `now` 는 상대 시각 해석의 기준(결정 K) --
    루프가 매 턴 현재 시각을 주입한다(테스트는 고정값을 준다, 원칙8)."""

    def propose(self, utterance: str, now: datetime) -> Proposal: ...


# ---------------------------------------------------------------------------
# 프롬프트 조립 (R-22 (ㄴ) -- inspect.signature 런타임 생성)
# ---------------------------------------------------------------------------


def _tool_signature_line(name: str) -> str:
    """`app.tools.<name>` 의 시그니처를 사람이 읽는 한 줄로 만든다(게이트
    ③ 과 같은 출처, R-22). `ctx`/`raw_utterance` 는 루프가 주입하므로
    설명하지 않고, `person_id` 는 `person(언급 문자열)` 로 바꿔 부른다.
    이 함수 본문에는 `name` 과 `"("` 이 리터럴로 나란히 있지 않다 --
    `f"{name}("` 처럼 이름을 변수로만 다룬다(R-22, 판정 표 5a·5b 오탐
    방지)."""

    fn = getattr(app_tools, name)
    signature = inspect.signature(fn)
    labels: list[str] = []
    for param in signature.parameters.values():
        if param.name in _PROMPT_EXCLUDED_PARAMS:
            continue
        label = "person(언급 문자열)" if param.name == "person_id" else param.name
        if param.default is not inspect.Parameter.empty:
            label = f"{label}?"
        labels.append(label)
    joined = ", ".join(labels)
    return f"{name}: {joined}" if joined else name


def build_propose_prompt(utterance: str, now: datetime) -> tuple[str, str]:
    """`(system, user_text)` 를 만든다. 발화 **하나** + `now` 만 넣는다 --
    이전 대화·전체 이력은 넣지 않는다(S3.4 13행, security §1). 키·
    환경변수 이름도 넣지 않는다(security §1, 아래 테스트가 확인)."""

    tool_lines = [_tool_signature_line(name) for name in TOOL_NAMES]
    not_callable = ", ".join(_LLM_NOT_CALLABLE)

    system = (
        "너는 한국어 대화 한 문장을 보고, 그 문장을 기억하는 데 필요한 "
        "툴 호출을 제안하는 보조 도구다. 아래 툴 목록의 이름 중에서만 "
        "골라라. 사람을 가리킬 때는 person_id 를 쓰지 말고 언급 문자열을 "
        "person 필드에 그대로 써라(예: '민수', '팀장님'). "
        f"{not_callable} 은 네가 직접 제안할 수 없는 내부 전용 툴이다 -- "
        f"절대 제안하지 마라. {PROPOSAL_TOOL_NAME} 도구로만 답하라."
    )
    user_text = (
        f'현재 시각(now): "{now.isoformat()}"\n'
        f'발화(utterance): "{utterance}"\n'
        "사용 가능한 툴(이름: 인자):\n"
        + "\n".join(f"- {line}" for line in tool_lines)
        + "\n\n위 발화를 보고 필요한 tool_calls 를 제안하라. 상대 시각"
        "('어제 저녁' 등)은 now 를 기준으로 절대 시각(ISO 8601 문자열)으로 "
        "바꿔서 써라. 시각을 확정할 수 없으면 그 필드를 비우거나 null 로 "
        "둬라. 기억할 것이 없으면 tool_calls 를 빈 배열로 답하라."
    )
    return system, user_text


# ---------------------------------------------------------------------------
# 형식 검증 + 시각 변환 (형식만 -- 의미 검증은 게이트, 원칙1)
# ---------------------------------------------------------------------------


def _parse_iso_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _convert_datetime_args(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """`_DATETIME_ARG_NAMES[name]` 에 해당하는 키가 ISO 8601 문자열이면
    `datetime` 으로 바꾼다(형식 변환만). 값이 없거나(`None`) 파싱에
    실패하면 그대로 둔다 -- 파싱 실패 문자열은 게이트의 타입 검사가
    `bad_args` 로 걸러내고(U3), `None`(결정 K "확정 불가")은 U3/U5 가
    각각 판단한다(R-23)."""

    keys = _DATETIME_ARG_NAMES.get(name, ())
    if not keys:
        return dict(args)
    converted = dict(args)
    for key in keys:
        value = converted.get(key)
        if isinstance(value, str):
            parsed = _parse_iso_datetime(value)
            if parsed is not None:
                converted[key] = parsed
            # 파싱 실패 -- 문자열 그대로 둔다(게이트가 타입 위반으로 처리).
        # None/누락은 그대로 둔다.
    return converted


def validate_proposal(raw: dict[str, Any]) -> Proposal:
    """구조화 출력(이미 dict)을 **형식만** 검증해 `Proposal` 로 바꾼다.
    실패하면 `app.er.types.JudgeUnavailable("schema")` -- `judge.py` 의
    판정 실패와 같은 신호를 쓴다(인식 단계도 "LLM 이 스키마대로 답하지
    못했다"는 같은 실패 종류를 공유한다, 결정 G 가 라우트에서 같이
    잡는다).

    검사하는 것: `raw` 가 dict 이고 `tool_calls` 가 list 이며, 각 원소가
    `{name: str, args: dict}` 모양인가. 검사하지 않는 것: `name` 이
    툴 7종 안인가, `args` 가 그 툴의 시그니처와 맞는가, `person_id` 를
    직접 줬는가(전부 게이트, U3)."""

    if not isinstance(raw, dict):
        raise JudgeUnavailable("schema")

    tool_calls_raw = raw.get("tool_calls")
    if not isinstance(tool_calls_raw, list):
        raise JudgeUnavailable("schema")

    parsed: list[ToolCallProposal] = []
    for item in tool_calls_raw:
        if not isinstance(item, dict):
            raise JudgeUnavailable("schema")
        name = item.get("name")
        args = item.get("args")
        if not isinstance(name, str) or not name:
            raise JudgeUnavailable("schema")
        if not isinstance(args, dict):
            raise JudgeUnavailable("schema")
        parsed.append(ToolCallProposal(name=name, args=_convert_datetime_args(name, args)))

    return Proposal(tool_calls=parsed, raw=raw)


# ---------------------------------------------------------------------------
# 공급자 구현 (judge.py 의 등록표 개념·select_provider·오류 매핑 재사용, D11)
# ---------------------------------------------------------------------------


@dataclass
class ClaudeProposer:
    """Anthropic SDK 로 인식 단계를 수행한다. `judge.py::ClaudeJudge` 와
    같은 관례(생성 시점에 `ANTHROPIC_MODEL` 을 읽는다, 키는 SDK 가 환경
    변수에서 직접 읽는다, security §1)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        if self.client is None:
            import anthropic  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = anthropic.Anthropic(
                timeout=self.timeout, max_retries=self.max_retries
            )

    def propose(self, utterance: str, now: datetime) -> Proposal:
        import anthropic  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_propose_prompt(utterance, now)
        tool_schema = {
            "name": PROPOSAL_TOOL_NAME,
            "description": _PROPOSAL_TOOL_DESCRIPTION,
            "input_schema": PROPOSAL_SCHEMA,
        }

        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_text}],
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": PROPOSAL_TOOL_NAME},
            ),
        )

        tool_use_input = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use":
                tool_use_input = block.input
                break

        if tool_use_input is None:
            raise JudgeUnavailable("schema")

        return validate_proposal(tool_use_input)


@dataclass
class OpenAIProposer:
    """OpenAI SDK 로 인식 단계를 수행한다. `judge.py::OpenAIJudge` 와 같은
    관례(생성 시점에 `OPENAI_MODEL` 을 읽는다, 키는 SDK 가 환경변수에서
    직접 읽는다)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if self.client is None:
            import openai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = openai.OpenAI(timeout=self.timeout, max_retries=self.max_retries)

    def propose(self, utterance: str, now: datetime) -> Proposal:
        import openai  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_propose_prompt(utterance, now)
        tool_schema = {
            "type": "function",
            "function": {
                "name": PROPOSAL_TOOL_NAME,
                "description": _PROPOSAL_TOOL_DESCRIPTION,
                "parameters": PROPOSAL_SCHEMA,
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
                tool_choice={"type": "function", "function": {"name": PROPOSAL_TOOL_NAME}},
            ),
        )

        tool_calls = None
        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            tool_calls = getattr(message, "tool_calls", None) if message is not None else None

        if not tool_calls:
            raise JudgeUnavailable("schema")

        arguments_raw = tool_calls[0].function.arguments
        try:
            raw = json.loads(arguments_raw)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        return validate_proposal(raw)


@dataclass
class GeminiProposer:
    """`google-genai` SDK 로 인식 단계를 수행한다. `judge.py::GeminiJudge`
    와 같은 관례(`GEMINI_MODEL` 기본값 없음, 생성 시점에 읽는다) --
    재시도·오류 매핑은 `call_with_gemini_error_mapping()` 을 그대로
    재사용한다(두 번째 헬퍼를 만들지 않는다, R-6 정신)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT

    def __post_init__(self) -> None:
        if self.model is None:
            model = os.environ.get("GEMINI_MODEL")
            if not model:
                from app.tools.types import InvalidValue

                raise InvalidValue(
                    "GeminiProposer: GEMINI_MODEL 환경변수가 필요하다(기본값 "
                    "없음 -- judge.py::GeminiJudge 와 같은 관례). Google AI "
                    "콘솔에서 확인한 모델 이름을 .env 의 GEMINI_MODEL 에 넣는다"
                )
            self.model = model
        if self.client is None:
            from google import genai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.
            from google.genai import types as genai_types

            self.client = genai.Client(
                http_options=genai_types.HttpOptions(timeout=int(self.timeout * 1000))
            )

    def propose(self, utterance: str, now: datetime) -> Proposal:
        from google.genai import types as genai_types  # 요청 조립용 지연 import.

        system, user_text = build_propose_prompt(utterance, now)

        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            response_mime_type="application/json",
            response_schema=_to_gemini_schema(PROPOSAL_SCHEMA),
        )

        response = call_with_gemini_error_mapping(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=user_text,
                config=config,
            )
        )

        text = getattr(response, "text", None)
        if not text:
            raise JudgeUnavailable("schema")

        try:
            raw = json.loads(text)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        return validate_proposal(raw)


#: 이름 -> 무인자 팩토리의 등록표(D11 정신 -- 이름 집합·선택 로직은
#: `judge.py::JUDGES`/`select_provider` 와 공유하지만, 스키마가 달라
#: 표 자체는 새로 둔다). `FakeProposer` 는 여기 없다(테스트 전용, `judge.py
#: ::JUDGES` 가 `FakeJudge` 를 빼는 것과 같은 이유).
PROPOSERS: dict[str, Callable[[], Proposer]] = {
    "anthropic": ClaudeProposer,
    "openai": OpenAIProposer,
    "gemini": GeminiProposer,
}


def proposer_from_env(env: dict[str, str] | None = None) -> Proposer:
    """`select_provider(env)`(`judge.py` 재사용) -> `PROPOSERS[name]()`.
    `judge_from_env()` 와 같은 2단계 패턴이지만 `JUDGES` 대신 이 모듈의
    `PROPOSERS` 를 쓴다. `env` 를 생략하면 `os.environ` 을 읽는다(`judge_
    from_env()` 와 같은 규약)."""

    return PROPOSERS[select_provider(env)]()


# ---------------------------------------------------------------------------
# FakeProposer -- 테스트용 결정적 Proposer (원칙8, 네트워크 0)
# ---------------------------------------------------------------------------


@dataclass
class FakeProposer:
    """테스트용 결정적 `Proposer`(원칙8 -- LLM 은 재현 불가능하므로 자동
    테스트에 넣지 않는다). `table = {발화: [{"name":..., "args":...}, ...]}`
    -- 표에 없는 발화는 빈 `tool_calls` 를 낸다. `now` 는 무시한다(표가
    이미 절대 시각을 담고 있다고 가정 -- 결정적이어야 하므로 `now` 로
    분기하지 않는다).

    `validate_proposal()` 을 그대로 거쳐 만들어진다 -- 실제 공급자와
    같은 형식 검증·시각 변환 경로를 타서 게이트(U3) 테스트가 두 경로를
    다르게 취급하지 않게 한다."""

    table: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def propose(self, utterance: str, now: datetime) -> Proposal:
        calls = self.table.get(utterance, [])
        return validate_proposal({"tool_calls": [dict(c) for c in calls]})
