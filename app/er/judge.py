"""Refs: P3-er S3.3 D3 D4 D5 R4 결정3 결정3-c F-5a97ef -- 3단계(LLM 판정).

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
- **팩토리** `judge_from_env(env=None)`: `LLM_PROVIDER`(기본 `anthropic`)
  로 고른다. `gemini` 는 새 의존성(`google-genai`)이 필요해 이번에
  구현하지 않고, 사람이 읽는 `InvalidValue` 로 예약만 한다.

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


#: `judge_from_env()` 가 고르는 공급자 이름 -- `app.settings.LLM_PROVIDER`
#: 기본값과 같은 어휘. `gemini` 는 예약만(아래 함수 docstring).
_KNOWN_PROVIDERS = ("anthropic", "openai", "gemini")


def judge_from_env(env: dict[str, str] | None = None) -> Judge:
    """`LLM_PROVIDER`(기본 `anthropic`, `app.settings.LLM_PROVIDER`)로
    판정기를 고른다. 모델은 공급자별 env(`ANTHROPIC_MODEL`/`OPENAI_MODEL`/
    `GEMINI_MODEL`)를 각 판정기 생성자가 그대로 읽는다(이 함수는 모델
    문자열을 여기서 다시 읽지 않는다 -- 단일 출처는 각 Judge 클래스).

    `env` 를 생략하면 `os.environ` 을 읽는다(`app.settings` 의 다른 로더와
    같은 규약). `.env` 는 읽지 않는다.

    - `"anthropic"` -> `ClaudeJudge()`
    - `"openai"` -> `OpenAIJudge()`
    - `"gemini"` -> 아직 구현하지 않는다(`google-genai` 의존성이 없다) --
      `InvalidValue("gemini 판정기는 아직 구현되지 않았다 — google-genai "
      "의존성 추가 필요")` 를 던진다(우회 구현하지 않는다, 원칙8).
    - 그 밖의 값 -> `InvalidValue`.
    """

    from app.settings import LLM_PROVIDER
    from app.tools.types import InvalidValue

    if env is None:
        env = dict(os.environ)

    provider = env.get("LLM_PROVIDER", LLM_PROVIDER)

    if provider == "anthropic":
        return ClaudeJudge()
    if provider == "openai":
        return OpenAIJudge()
    if provider == "gemini":
        raise InvalidValue(
            "gemini 판정기는 아직 구현되지 않았다 — google-genai 의존성 추가 필요"
        )
    raise InvalidValue(
        f"judge_from_env: unknown LLM_PROVIDER {provider!r} "
        f"(expected one of {_KNOWN_PROVIDERS})"
    )
