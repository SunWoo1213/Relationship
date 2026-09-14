"""Refs: P3-llm-providers D11 S3.3 D3 D4 D5 R4 결정3 결정3-c F-5a97ef -- 3단계(LLM 판정).

`s_llm` 은 **LLM 이 구조화 출력(도구/함수 호출)으로 자기보고한 0~1 점수이며,
어떤 공급자의 API 도 제공하지 않는 토큰 로그 확률이 아니다**(R4, D3). 이
모듈의 판정기들은 그 값을 강제 스키마로 받아 그대로 `Judgement.s_llm` 에
담을 뿐, 로그 확률을 계산·가정하지 않는다.

## 공급자 중립 설계 (사용자 결정 2026-09-06)

LLM 판정기를 Anthropic 하나에 묶지 않는다 -- **공급자 중립 핵심**과
**공급자별 구현**을 분리한다:

- **핵심**(공급자 무관, 이 절이 단일 출처): `Judge` Protocol,
  `build_prompt()`(system·user 텍스트 조립), `JUDGEMENT_SCHEMA`(판정 JSON
  스키마 딕셔너리 하나 -- `matched_person_id`/`s_llm`/`reason`),
  `validate_judgement(raw, allowed_ids)`, `JudgeUnavailable.error` 유형
  어휘(`timeout`/`rate_limit`/`api_error`/`connection`/`schema`/
  `out_of_range_id`), `FakeJudge`. 어느 공급자든 이 핵심을 그대로 쓰고
  "구조화 출력을 받아 dict 로 만드는 부분"만 구현한다.
- **공급자 구현**: `ClaudeJudge`(Anthropic, 강제 `tool_use`)·
  `OpenAIJudge`(OpenAI, function calling). 둘 다 `call_with_error_mapping()`
  (예외 매핑 표 공유)과 `validate_judgement()`(응답 검증 공유)를 거친다 --
  요청 조립만 SDK 마다 다르다(도구 스키마를 감싸는 바깥 모양이 다를 뿐
  `JUDGEMENT_SCHEMA` 자체는 같다).
- **팩토리** `judge_from_env(env=None)`: `LLM_PROVIDER`(기본 `openai`,
  D11 결정 2)로 등록표 `JUDGES` 에서 고른다. `gemini` 는 `GeminiJudge`
  (P3-llm-providers U2, `google-genai` SDK)로 구현되어 있다 --
  `GEMINI_MODEL` 기본값은 두지 않는다(D11 결정 3, 미설정 시
  `InvalidValue`).

## 등록표·활성 스위치 (P3-llm-providers U1, D11)

`JUDGES: dict[str, Callable[[], Judge]]` 하나가 이름 -> 무인자 팩토리의
**유일한** 등록표다(`FakeJudge` 는 여기 없다 -- 환경변수로 진짜 판정기를
가짜로 바꿀 수 없다, D11 "코드에서 지켜야 할 것"). `select_provider(env)`
가 `LLM_PROVIDER`/`LLM_PROVIDERS_ENABLED` 를 **같은 `env` 매핑**에서 읽어
거부(미지 이름 -- 표 키 목록 / 비활성 -- 활성 목록)를 판정하는 **유일한**
자리다 -- 베이스라인 단일 프롬프트 caller 모듈(`llm_single.py`)의
`caller_from_env()` 가 이 함수를 import 해 재사용한다(자체 표·자체 거부
로직 금지). `env` 를
생략하면 `os.environ` 을 읽고, `env` 가 주어지면 `os.environ` 을 보지
않는다(R-3 단일 출처).

키(`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`)는 각 SDK 클라이언트가 **내부에서**
환경변수로 읽는다 -- 이 모듈의 코드는 그 값을 변수로 옮기거나 프롬프트·
trace·예외 메시지에 넣지 않는다(security.md §1). `.env` 는 읽지 않는다.

## Judge 계약

`Judge.judge(mention, utterance, candidates) -> Judgement` 의 `candidates`
는 **2단계(`app/er/rules.py`) 규칙 통과 후보만**이다(01-plan 34행 "LLM 에
넘기는 후보 집합도 규칙 통과 후보뿐"). 배제된 후보를 이 함수에 넘기지
않는다 -- 넘기면 LLM 이 배제된 후보를 골라 오병합 위험을 키운다(원칙1).

## 범위 밖 id 조기 차단 (F-5a97ef)

`decide()`(`app/er/confidence.py`)가 이미 `passed` 밖 id 를 llm_failed 로
강등하는 방어를 갖고 있지만(U4), 그 방어는 `llm.error` 유형을 채우지
않는다. 이 모듈은 **같은 판정을 더 일찍** 한다 -- `validate_judgement()`
가 통과 후보 id 집합(`allowed_ids`) ∪ `{None}` 밖의 `matched_person_id` 를
`JudgeUnavailable(error="out_of_range_id")` 로 바꿔, `llm.error` 에
API 장애와 구분되는 이름이 남게 한다. 모든 구현이 이 **같은 함수**를
공유해 검증 로직의 이중 출처를 막는다.

## Gemini 전용 (P3-llm-providers U2, D11, R-6 실측)

`google-genai`(2.23.0, R-6 evidence)는 Anthropic·OpenAI 와 예외 계층이
다르다 -- `errors.ClientError`/`errors.ServerError`(둘 다
`errors.APIError` 의 서브클래스, `.code` 가 HTTP 상태 코드)만 있고 별도
`RateLimitError`/`APITimeoutError` 클래스가 없다. 그래서 기존
`call_with_error_mapping`(모듈 덕타이핑 -- anthropic·openai 가 우연히
같은 이름을 쓴다)은 **고치지 않고**, 같은 어휘 6종을 내는
`call_with_gemini_error_mapping()` 을 따로 둔다. timeout·connection 은
SDK 가 감싸지 않고 `httpx`/`httpx2` 의 `TimeoutException`/`ConnectError`
를 그대로 던지며(R-6 evidence), `HttpOptions.retry_options` 는 기본으로
재시도가 없고 켜더라도 429/5xx 까지 함께 재시도하게 되어 "timeout·
connection 에만" 이라는 이 프로젝트의 어휘별 재시도 정책과 맞지 않는다
-- 그래서 이 헬퍼 안에 **1회만** 재시도하는 최소 루프를 둔다(재시도
횟수를 늘리지 않는다, 01-plan 96행).

`_to_gemini_schema(schema)` 는 `JUDGEMENT_SCHEMA`(및 U3 의
`RESOLUTION_SCHEMA`)의 JSON Schema 부분집합을 `response_schema` 가 받는
딕셔너리로 변환한다 -- `"type": [..., "null"]` 을 `nullable=True` + 단일
타입으로, JSON Schema 타입 이름을 Gemini `Type` 대문자 이름으로 바꾼다.
`JUDGEMENT_SCHEMA` 객체 자체는 절대 바꾸지 않는다(항상 새 딕셔너리를
만든다) -- R-6 이 요구하는 "원 스키마 불변" 을 이 함수 하나가 담당한다.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from app.er.types import Judgement, JudgeUnavailable, ScoredCandidate

TOOL_NAME = "report_judgement"

_TOOL_DESCRIPTION = (
    "이 mention 이 후보 중 누구인지 판정한다. 후보 목록 안의 person_id "
    "하나를 고르거나, 아무도 아니면 null 을 준다. s_llm 은 스스로 판단한 "
    "확신도 0~1 이다(로그 확률이 아니다)."
)

#: 판정 JSON 스키마 **단일 출처**(사용자 결정 2026-09-06) -- 어느 공급자든
#: 이 딕셔너리 그대로를 도구/함수 스키마의 `input_schema`/`parameters` 로
#: 쓴다. 공급자별 바깥 모양(도구 이름·strict 플래그 위치)만 다르다.
JUDGEMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "matched_person_id": {"type": ["integer", "null"]},
        "s_llm": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
    },
    "required": ["matched_person_id", "s_llm", "reason"],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = (
    "너는 한국어 대화에서 사람 지칭(mention)이 이전에 저장된 인물 후보 중 "
    "누구를 가리키는지 판정하는 보조 도구다. 후보 목록에 없는 사람을 "
    "지어내지 말고, 확신이 없으면 null 을 골라라. report_judgement 도구로만 "
    "답하라."
)


class Judge(Protocol):
    """3단계(LLM 판정) 인터페이스. `candidates` 는 **규칙 통과 후보만**
    받는다(모듈 docstring "Judge 계약"). 공급자 무관."""

    def judge(
        self, mention: str, utterance: str, candidates: list[ScoredCandidate]
    ) -> Judgement: ...


def _candidate_summary(candidate: ScoredCandidate) -> dict[str, Any]:
    """프롬프트에 넣을 후보 요약 -- id·표시 이름·별칭·관계 태그·위계·
    `rule_flags` 만(키·환경변수·전체 대화 이력 금지, 모듈 docstring)."""

    return {
        "person_id": candidate.person_id,
        "display_name": candidate.display_name,
        "aliases": list(candidate.aliases),
        "relation_tag": candidate.relation_tag,
        "hierarchy": candidate.hierarchy,
        "rule_flags": dict(candidate.rule_flags),
    }


def build_prompt(
    mention: str, utterance: str, candidates: list[ScoredCandidate]
) -> tuple[str, str]:
    """`(system, user_text)` 를 만든다(공급자 무관, 단일 출처). 후보의
    id·표시 이름·별칭·관계 태그·위계·`rule_flags` 와 발화 맥락만 넣는다 --
    **키·환경변수·전체 대화 이력은 넣지 않는다**(01-plan U5 항목)."""

    candidate_lines = [f"- {_candidate_summary(c)}" for c in candidates]
    user_text = (
        f'지칭(mention): "{mention}"\n'
        f'발화 맥락(utterance): "{utterance}"\n'
        "후보 목록:\n" + ("\n".join(candidate_lines) if candidate_lines else "(없음)")
        + "\n\n위 mention 이 후보 중 누구인지 report_judgement 로 답하라. "
        "후보 중 하나가 확실하면 그 person_id 와 확신도(s_llm)를, 아무도 "
        "아니거나 확신이 없으면 matched_person_id=null 과 낮은 s_llm 을 "
        "보고하라. reason 은 한국어 한 문장으로."
    )
    return _SYSTEM_PROMPT, user_text


def validate_judgement(raw: dict[str, Any], allowed_ids: set[int]) -> Judgement:
    """구조화 출력(이미 dict)을 검증해 `Judgement` 로 바꾼다. **모든
    공급자 구현이 공유**하는 단일 검증 함수다(F-5a97ef "이중 출처를 막는다").

    - `s_llm` 이 `float`(또는 `int`, 그대로 float 변환)가 아니거나
      `0 <= s_llm <= 1` 을 벗어나면 `JudgeUnavailable(error="schema")`.
    - `matched_person_id` 가 `int`/`None` 이 아니면 `error="schema"`.
    - `matched_person_id` 가 `allowed_ids ∪ {None}` 밖이면
      `error="out_of_range_id"`(F-5a97ef -- API 장애와 구분되는 유형).
    - `reason` 이 문자열이 아니면 `error="schema"`.

    반환된 `Judgement.provider` 는 항상 기본값 `"fake"` 다 -- 호출부
    (`ClaudeJudge.judge`/`OpenAIJudge.judge`)가 실제 공급자 이름으로
    덮어써서 돌려준다(이 함수는 공급자를 모른다).
    """

    if not isinstance(raw, dict):
        raise JudgeUnavailable("schema")

    matched_person_id = raw.get("matched_person_id")
    s_llm = raw.get("s_llm")
    reason = raw.get("reason")

    if matched_person_id is not None and not isinstance(matched_person_id, int):
        raise JudgeUnavailable("schema")

    if isinstance(s_llm, bool) or not isinstance(s_llm, (int, float)):
        raise JudgeUnavailable("schema")
    s_llm = float(s_llm)
    if not (0.0 <= s_llm <= 1.0):
        raise JudgeUnavailable("schema")

    if not isinstance(reason, str):
        raise JudgeUnavailable("schema")

    if matched_person_id is not None and matched_person_id not in allowed_ids:
        raise JudgeUnavailable("out_of_range_id")

    return Judgement(
        matched_person_id=matched_person_id,
        s_llm=s_llm,
        reason=reason,
    )


def call_with_error_mapping(errors_module: Any, fn: Callable[[], Any]) -> Any:
    """공급자 SDK 예외를 `JudgeUnavailable` 로 통일 매핑하는 **공유 표**
    (사용자 결정 2026-09-06 "예외 매핑 표"). `errors_module` 은 `anthropic`
    또는 `openai` 모듈이다 -- 두 SDK 모두 같은 이름의 예외 클래스
    (`APITimeoutError`/`RateLimitError`/`APIStatusError`/
    `APIConnectionError`)를 노출하므로, 클래스 자체가 아니라 **모듈**을
    받아 어느 공급자든 같은 매핑 로직 한 곳을 쓴다."""

    try:
        return fn()
    except errors_module.APITimeoutError as exc:
        raise JudgeUnavailable("timeout") from exc
    except errors_module.RateLimitError as exc:
        raise JudgeUnavailable("rate_limit") from exc
    except errors_module.APIStatusError as exc:
        raise JudgeUnavailable("api_error") from exc
    except errors_module.APIConnectionError as exc:
        raise JudgeUnavailable("connection") from exc


#: 옛 이름(밑줄) 호환 별칭 -- 승격 전 이름을 참조하는 코드가 있어도
#: 깨지지 않게 남긴다(결정 J: 동작 무변경).
_call_with_error_mapping = call_with_error_mapping


@dataclass
class ClaudeJudge:
    """Anthropic SDK 로 3단계 LLM 판정을 수행한다(결정3, 강제 `tool_use`).

    `model` 기본값은 env `ANTHROPIC_MODEL`(`.env.example` 에 이미 이름·
    기본값 `claude-sonnet-5` 가 있다) -- **생성 시점**에 읽는다(호출마다
    바뀌지 않는다, 테스트는 `monkeypatch.setenv`/`delenv` 로 확인한다).

    `client` 가 `None` 이면 `anthropic` 을 지연 import 해
    `anthropic.Anthropic(timeout=timeout, max_retries=max_retries)` 를
    만든다 -- 키는 인자로 넘기지 않고 SDK 가 `ANTHROPIC_API_KEY` 를
    환경변수에서 읽게 둔다(security.md §1). 테스트는 `client` 자리에
    스텁을 주입해 네트워크 없이 돈다.

    SDK 자체가 `max_retries` 만큼 재시도하므로 이 클래스는 재시도 루프를
    직접 구현하지 않는다(결정3-c "1회만" = `ER_JUDGE_MAX_RETRIES=1` 을
    SDK 에 그대로 넘기는 것으로 충족).
    """

    model: str | None = None
    client: Any = None
    timeout: float = 20.0
    max_retries: int = 1

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        if self.client is None:
            import anthropic  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = anthropic.Anthropic(
                timeout=self.timeout, max_retries=self.max_retries
            )

    def judge(
        self, mention: str, utterance: str, candidates: list[ScoredCandidate]
    ) -> Judgement:
        import anthropic  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_prompt(mention, utterance, candidates)
        allowed_ids = {c.person_id for c in candidates}

        tool_schema = {
            "name": TOOL_NAME,
            "description": _TOOL_DESCRIPTION,
            "strict": True,
            "input_schema": JUDGEMENT_SCHEMA,
        }

        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system=system,
                messages=[{"role": "user", "content": user_text}],
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": TOOL_NAME},
            ),
        )

        tool_use_input = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use":
                tool_use_input = block.input
                break

        if tool_use_input is None:
            raise JudgeUnavailable("schema")

        judgement = validate_judgement(tool_use_input, allowed_ids)

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "input_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "output_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return Judgement(
            matched_person_id=judgement.matched_person_id,
            s_llm=judgement.s_llm,
            reason=judgement.reason,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=model_used,
            provider="anthropic",
        )


@dataclass
class OpenAIJudge:
    """OpenAI SDK(`openai==2.33.0`, 이미 requirements 에 핀) 로 3단계 LLM
    판정을 수행한다(사용자 결정 2026-09-06 -- 공급자 중립). `chat.completions`
    의 function calling 으로 강제 도구 호출을 받는다.

    `model` 기본값은 env `OPENAI_MODEL`(없으면 `gpt-4o-mini`) -- 생성
    시점에 읽는다. `client` 가 `None` 이면 `openai` 를 지연 import 해
    `openai.OpenAI(timeout=timeout, max_retries=max_retries)` 를 만든다 --
    키는 SDK 가 `OPENAI_API_KEY` 를 환경변수에서 읽는다(security.md §1).
    """

    model: str | None = None
    client: Any = None
    timeout: float = 20.0
    max_retries: int = 1

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if self.client is None:
            import openai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = openai.OpenAI(timeout=self.timeout, max_retries=self.max_retries)

    def judge(
        self, mention: str, utterance: str, candidates: list[ScoredCandidate]
    ) -> Judgement:
        import openai  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_prompt(mention, utterance, candidates)
        allowed_ids = {c.person_id for c in candidates}

        tool_schema = {
            "type": "function",
            "function": {
                "name": TOOL_NAME,
                "description": _TOOL_DESCRIPTION,
                "parameters": JUDGEMENT_SCHEMA,
                "strict": True,
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
                tool_choice={"type": "function", "function": {"name": TOOL_NAME}},
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
            arguments = json.loads(arguments_raw)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        judgement = validate_judgement(arguments, allowed_ids)

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return Judgement(
            matched_person_id=judgement.matched_person_id,
            s_llm=judgement.s_llm,
            reason=judgement.reason,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=model_used,
            provider="openai",
        )


@dataclass
class FakeJudge:
    """테스트용 결정적 `Judge`(원칙8 -- LLM 은 재현 불가능하므로 자동
    테스트에 넣지 않는다). `table` = `{person_id: s_llm}`.

    - `pick` 이 주어지면 그 id 와 `table[pick]` 을 그대로 돌려준다(호출자가
      `KeyError` 를 감수 -- 회귀 3종처럼 특정 후보를 정확히 겨냥할 때 쓴다).
    - `pick` 이 없으면 `table` 과 **통과 후보 교집합** 중 `s_llm` 최고인
      id 하나를 고른다. 교집합이 비었거나(`table` 이 비었거나 통과 후보와
      안 겹치면) `matched_person_id=None, s_llm=0.0`.
    - `fail` 이 주어지면 `JudgeUnavailable(error=fail)` 을 던진다
      (`llm_failed` 경로 테스트용).

    범위 검증은 `ClaudeJudge`/`OpenAIJudge` 와 **같은 함수**
    (`validate_judgement`)를 거친다(F-5a97ef "이중 출처를 막는다") --
    `pick`/`table` 로 통과 후보 밖 id 를 만들면 실제 공급자와 동일하게
    `out_of_range_id` 로 걸린다."""

    table: dict[int, float] = field(default_factory=dict)
    pick: int | None = None
    reason: str = "fake"
    tokens: tuple[int, int] = (0, 0)
    fail: str | None = None

    def judge(
        self, mention: str, utterance: str, candidates: list[ScoredCandidate]
    ) -> Judgement:
        if self.fail is not None:
            raise JudgeUnavailable(self.fail)

        allowed_ids = {c.person_id for c in candidates}

        if self.pick is not None:
            matched_person_id = self.pick
            s_llm = self.table[self.pick]
        else:
            passed_ids = allowed_ids & set(self.table)
            if not passed_ids:
                matched_person_id = None
                s_llm = 0.0
            else:
                matched_person_id = max(passed_ids, key=lambda pid: self.table[pid])
                s_llm = self.table[matched_person_id]

        judgement = validate_judgement(
            {
                "matched_person_id": matched_person_id,
                "s_llm": s_llm,
                "reason": self.reason,
            },
            allowed_ids,
        )
        tokens_in, tokens_out = self.tokens
        return Judgement(
            matched_person_id=judgement.matched_person_id,
            s_llm=judgement.s_llm,
            reason=judgement.reason,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=None,
            provider="fake",
        )


# ---------------------------------------------------------------------------
# Gemini 전용 절 (P3-llm-providers U2, D11) -- 이 절 밖의 공유 자산
# (JUDGEMENT_SCHEMA·build_prompt·validate_judgement·call_with_error_mapping)
# 은 이 절에서 읽기만 한다. `_to_gemini_schema`/`call_with_gemini_error_mapping`
# 은 U3(`llm_single.py` 의 Gemini caller)가 그대로 import 해 재사용한다
# (두 번째 변환기·두 번째 매핑 헬퍼를 만들지 않는다, R-6).
# ---------------------------------------------------------------------------

#: JSON Schema 타입 이름 -> Gemini `types.Schema.type` 이 받는 대문자
#: 이름(R-6 실측, `types.Type` enum 값과 동일한 문자열). 실측하지 않은
#: 이름을 추측으로 늘리지 않는다(원칙8) -- 이 프로젝트의 스키마(
#: `JUDGEMENT_SCHEMA`·U3 `RESOLUTION_SCHEMA`)가 실제로 쓰는 6개뿐이다.
_JSON_TYPE_TO_GEMINI: dict[str, str] = {
    "object": "OBJECT",
    "array": "ARRAY",
    "string": "STRING",
    "number": "NUMBER",
    "integer": "INTEGER",
    "boolean": "BOOLEAN",
    "null": "NULL",
}


def _to_gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """`JUDGEMENT_SCHEMA` 부분집합(및 U3 `RESOLUTION_SCHEMA`)을 Gemini
    `response_schema` 가 받는 딕셔너리로 변환한다(R-6). **입력을 제자리
    수정하지 않고 항상 새 딕셔너리를 만든다** -- `JUDGEMENT_SCHEMA` 객체는
    세 공급자 공유 자산이라 이 함수가 절대 바꾸지 않는다.

    - `"type": [..., "null"]`(nullable 유니온, 예 `matched_person_id`) ->
      남은 단일 타입을 `type`(대문자)으로, `nullable=True` 를 덧붙인다
      (01-plan 124행 "nullable integer" 표현 -- R-6 실측으로
      `types.Schema` 에 `nullable` 필드가 있어 표현 가능함을 확인했다).
    - `"type": "integer"|"string"|"number"|"boolean"|"array"|"object"` ->
      `_JSON_TYPE_TO_GEMINI` 로 대문자 이름 하나.
    - `properties` -> 각 값을 재귀 변환. `items` -> 재귀 변환(U3 의
      `candidate_person_ids: {"type":"array","items":{"type":"integer"}}`
      대비 -- 두 번째 변환기를 만들지 않는다).
    - `required`/`minimum`/`maximum`/`enum`/`description` -> 그대로
      옮긴다(`s_llm` 의 `minimum`/`maximum` 0~1 이 이 경로로 유지된다).
    - `additionalProperties` -> 같은 camelCase 키로 그대로 전달한다
      (`google.genai.types.Schema` 가 pydantic alias 로 받는다).
    """

    if not isinstance(schema, dict):
        return schema

    result: dict[str, Any] = {}

    json_type = schema.get("type")
    nullable = False
    if isinstance(json_type, list):
        remaining = [t for t in json_type if t != "null"]
        nullable = "null" in json_type
        json_type = remaining[0] if remaining else None

    if json_type is not None:
        result["type"] = _JSON_TYPE_TO_GEMINI[json_type]
    if nullable:
        result["nullable"] = True

    if "properties" in schema:
        result["properties"] = {
            key: _to_gemini_schema(value) for key, value in schema["properties"].items()
        }
    if "items" in schema:
        result["items"] = _to_gemini_schema(schema["items"])
    if "required" in schema:
        result["required"] = list(schema["required"])
    if "minimum" in schema:
        result["minimum"] = schema["minimum"]
    if "maximum" in schema:
        result["maximum"] = schema["maximum"]
    if "enum" in schema:
        result["enum"] = list(schema["enum"])
    if "description" in schema:
        result["description"] = schema["description"]
    if "additionalProperties" in schema:
        result["additionalProperties"] = schema["additionalProperties"]

    return result


def call_with_gemini_error_mapping(fn: Callable[[], Any]) -> Any:
    """Gemini 전용 오류 매핑 + **1회만** 재시도(모듈 docstring "Gemini
    전용" 절, R-6). 기존 `call_with_error_mapping`(anthropic·openai
    덕타이핑)은 고치지 않는다(원칙4 -- 두 공급자의 회귀 위험).

    - `errors.ClientError`(4xx, `.code`) 중 429 -> `rate_limit`. 그 밖
      `ClientError`/`ServerError`(5xx)/`APIError`(그 밖 코드) -> `api_error`.
      **재시도하지 않는다**(호출 1회) -- Claude/OpenAI 의 `max_retries` 는
      429/5xx 도 재시도하지만, 이 프로젝트의 6종 어휘 계약은 재시도
      여부를 어휘가 아니라 두 공급자 SDK 설정에 위임했을 뿐이므로 이
      비대칭은 Gemini 쪽 설계 선택이다 -- **timeout·connection 에만**
      재시도한다(01-plan 96행, 아래).
    - `httpx.TimeoutException`/`httpx2.TimeoutException`(+ 표준
      `TimeoutError`, 방어적)-> **1회 재시도 후에도 실패하면** `timeout`
      (호출 2회 한도).
    - `httpx.ConnectError`/`httpx2.ConnectError`(+ 표준 `ConnectionError`,
      방어적) -> **1회 재시도 후에도 실패하면** `connection`(호출 2회
      한도).

    google-genai 의 `HttpOptions.retry_options` 는 기본으로 재시도가
    없고(R-6 실측 `_api_client.retry_args` -- `options is None` 이면
    `stop_after_attempt(1)`), 켜더라도 429/5xx 를 포함한 상태 코드
    기준으로 재시도해 "timeout·connection 에만" 이라는 이 어휘의 재시도
    정책을 표현할 수 없다(빈 `http_status_codes=()` 는 falsy 라 기본
    목록으로 되돌아간다) -- 그래서 이 함수 안에 최소 재시도 루프를 둔다.
    """

    from google.genai import errors as genai_errors
    import httpx
    import httpx2

    timeout_exc: tuple[type[BaseException], ...] = (
        httpx.TimeoutException,
        httpx2.TimeoutException,
        TimeoutError,
    )
    connection_exc: tuple[type[BaseException], ...] = (
        httpx.ConnectError,
        httpx2.ConnectError,
        ConnectionError,
    )

    for attempt in (1, 2):
        try:
            return fn()
        except genai_errors.ClientError as exc:
            if exc.code == 429:
                raise JudgeUnavailable("rate_limit") from exc
            raise JudgeUnavailable("api_error") from exc
        except genai_errors.ServerError as exc:
            raise JudgeUnavailable("api_error") from exc
        except genai_errors.APIError as exc:
            raise JudgeUnavailable("api_error") from exc
        except timeout_exc as exc:
            if attempt == 2:
                raise JudgeUnavailable("timeout") from exc
        except connection_exc as exc:
            if attempt == 2:
                raise JudgeUnavailable("connection") from exc

    raise AssertionError("unreachable -- loop always returns or raises")


@dataclass
class GeminiJudge:
    """`google-genai` SDK 로 3단계 LLM 판정을 수행한다(D11, P3-llm-providers
    U2).

    `model` 기본값은 **두지 않는다**(D11 결정 3) -- **생성 시점**에
    `os.environ.get("GEMINI_MODEL")` 을 읽고, 없으면
    `app.tools.types.InvalidValue` 로 거부한다(`ClaudeJudge`/`OpenAIJudge`
    와 같은 "생성 시점에 읽는다" 규약이나, 이름을 추측으로 박지 않는다는
    점이 다르다 -- 콘솔에서 확인한 모델 이름을 `.env` 의 `GEMINI_MODEL` 에
    넣게 한다).

    `client` 가 `None` 이면 `google.genai` 를 지연 import 해
    `genai.Client(http_options=types.HttpOptions(timeout=...))` 를
    만든다 -- 키는 인자로 넘기지 않고 SDK 가 `GEMINI_API_KEY`(또는
    `GOOGLE_API_KEY`)를 환경변수에서 읽는다(security.md §1). R-2 실측 --
    키가 없으면 `genai.Client()` 자체가 `ValueError`("No API key was
    provided...", 키 값 없음)를 낸다. 테스트는 `client` 자리에 스텁을
    주입해 네트워크 없이 돈다.

    이 SDK 에는 `max_retries` 같은 "이 어휘에만 재시도" 설정이 없다(R-6) --
    재시도는 `call_with_gemini_error_mapping()` 안에서 한다.
    """

    model: str | None = None
    client: Any = None
    timeout: float = 20.0

    def __post_init__(self) -> None:
        if self.model is None:
            model = os.environ.get("GEMINI_MODEL")
            if not model:
                from app.tools.types import InvalidValue

                raise InvalidValue(
                    "GeminiJudge: GEMINI_MODEL 환경변수가 필요하다(기본값 "
                    "없음 -- D11 결정 3). Google AI 콘솔에서 확인한 모델 "
                    "이름을 .env 의 GEMINI_MODEL 에 넣는다"
                )
            self.model = model
        if self.client is None:
            from google import genai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.
            from google.genai import types as genai_types

            self.client = genai.Client(
                http_options=genai_types.HttpOptions(timeout=int(self.timeout * 1000))
            )

    def judge(
        self, mention: str, utterance: str, candidates: list[ScoredCandidate]
    ) -> Judgement:
        from google.genai import types as genai_types  # 요청 조립용 지연 import.

        system, user_text = build_prompt(mention, utterance, candidates)
        allowed_ids = {c.person_id for c in candidates}

        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            response_mime_type="application/json",
            response_schema=_to_gemini_schema(JUDGEMENT_SCHEMA),
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
            # 후보 블록 없음 · 안전 필터로 본문 없음 -- 둘 다 "스키마대로
            # 된 판정을 못 받았다" 는 점에서 같다(D11 결정 4, 어휘를
            # 늘리지 않는다).
            raise JudgeUnavailable("schema")

        try:
            raw = json.loads(text)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        judgement = validate_judgement(raw, allowed_ids)

        usage = getattr(response, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage is not None else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage is not None else 0
        model_used = getattr(response, "model_version", None) or self.model

        return Judgement(
            matched_person_id=judgement.matched_person_id,
            s_llm=judgement.s_llm,
            reason=judgement.reason,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            model=model_used,
            provider="gemini",
        )


#: 이름 -> 무인자 팩토리의 **유일한** 등록표(D11 "코드에서 지켜야 할 것",
#: R-5 -- `grep -c "^JUDGES" app/er/judge.py` = 1). `ClaudeJudge`/
#: `OpenAIJudge`/`GeminiJudge` 는 dataclass 라 클래스 자체가 무인자 호출
#: 가능한 팩토리다. `FakeJudge` 는 여기 없다(테스트 전용 -- 환경변수로
#: 실제 판정기를 가짜로 바꿀 수 있으면 원칙8·원칙9 의 근거가 무의미해진다).
JUDGES: dict[str, Callable[[], Judge]] = {
    "anthropic": ClaudeJudge,
    "openai": OpenAIJudge,
    "gemini": GeminiJudge,
}


def enabled_providers(env: dict[str, str] | None = None) -> frozenset[str]:
    """`LLM_PROVIDERS_ENABLED`(D11 결정 1, R-4 파싱 규칙)를 파싱해 활성
    공급자 집합을 돌려준다.

    규칙: 쉼표로 분리 -> 각 항목 `strip().lower()` -> 빈 항목 제거.
    **미설정 또는 공백만 남으면** `app.settings.LLM_PROVIDERS_ENABLED_DEFAULT`
    (표 전체 켬) -- 이 상수가 단일 출처이고, 이 함수는 기본 목록 리터럴을
    다시 쓰지 않는다(R-4). 파싱 결과에 `JUDGES` 표에 없는 이름이 섞여
    있으면 오타를 조용히 무시하지 않고 `InvalidValue`(표 키 목록 포함)를
    던진다(원칙8 재현성).

    `env` 를 생략하면 `os.environ` 을 읽는다. `env` 가 주어지면
    `os.environ` 을 보지 않는다(R-3 단일 출처, `select_provider()` 와
    같은 규약).
    """

    from app.settings import LLM_PROVIDERS_ENABLED_DEFAULT
    from app.tools.types import InvalidValue

    if env is None:
        env = dict(os.environ)

    raw = env.get("LLM_PROVIDERS_ENABLED")
    if raw is None or raw.strip() == "":
        raw = LLM_PROVIDERS_ENABLED_DEFAULT

    names = [item.strip().lower() for item in raw.split(",")]
    names = [name for name in names if name]

    unknown = sorted(set(names) - set(JUDGES))
    if unknown:
        raise InvalidValue(
            f"enabled_providers: LLM_PROVIDERS_ENABLED has unknown name(s) "
            f"{unknown} (expected subset of {sorted(JUDGES)})"
        )

    return frozenset(names)


def select_provider(env: dict[str, str] | None = None) -> str:
    """`LLM_PROVIDER`/`LLM_PROVIDERS_ENABLED` 를 **같은 `env` 매핑**에서
    읽어 이번 호출에서 쓸 공급자 이름을 고르는 **유일한** 거부 판정
    자리다(D11, R-5) -- `judge_from_env()` 와 베이스라인 단일 프롬프트
    caller 모듈(`llm_single.py`)의 `caller_from_env()` 가 이 함수 하나를
    import 해 재사용한다(두 진입점이 같은 환경변수·같은 거부 규칙을
    쓴다는 R-4 를 유지, 자체 표 금지).

    - `LLM_PROVIDER` 값을 `strip().lower()` 한 뒤 `JUDGES` 에서 조회한다.
      표에 없으면 `InvalidValue`(메시지에 `JUDGES` 키 목록).
    - 표에 있어도 `enabled_providers(env)` 의 활성 집합 밖이면
      `InvalidValue`(메시지에 활성 목록).
    - 오류 메시지에 키 값·프롬프트는 넣지 않는다.

    `env` 를 생략하면 `os.environ` 을 읽는다(`app.settings` 의 다른
    로더와 같은 규약). `env` 가 주어지면 `os.environ` 을 보지 않는다
    (R-3).
    """

    from app.settings import LLM_PROVIDER
    from app.tools.types import InvalidValue

    if env is None:
        env = dict(os.environ)

    raw_name = env.get("LLM_PROVIDER", LLM_PROVIDER)
    name = raw_name.strip().lower()

    if name not in JUDGES:
        raise InvalidValue(
            f"select_provider: unknown LLM_PROVIDER {raw_name!r} "
            f"(expected one of {sorted(JUDGES)})"
        )

    active = enabled_providers(env)
    if name not in active:
        raise InvalidValue(
            f"select_provider: LLM_PROVIDER {raw_name!r} is not in "
            f"LLM_PROVIDERS_ENABLED (active: {sorted(active)})"
        )

    return name


def judge_from_env(env: dict[str, str] | None = None) -> Judge:
    """`select_provider(env)` -> `JUDGES[name]()` 2단계로 판정기를
    고른다(D11, U1 -- `if provider == "anthropic"` 사다리를 등록표
    조회로 대체). 모델은 공급자별 env(`ANTHROPIC_MODEL`/`OPENAI_MODEL`/
    `GEMINI_MODEL`)를 각 판정기 생성자가 그대로 읽는다(이 함수는 모델
    문자열을 여기서 다시 읽지 않는다 -- 단일 출처는 각 Judge 클래스).

    `env` 를 생략하면 `os.environ` 을 읽는다. `.env` 는 읽지 않는다.
    """

    return JUDGES[select_provider(env)]()
