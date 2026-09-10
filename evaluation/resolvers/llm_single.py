"""Refs: P3-baselines S3.7 D3 원칙4 원칙8 -- 베이스라인 3 LLM 단일 프롬프트.

**두 임계치**(base.py 불변 규약 4): 이 방식은 `T_merge`/`T_new` 를 **쓰지
않는다** -- 결정 어휘까지 LLM 이 한 번에 내므로 바깥에 임계치 분기가
없다(`config` 는 같은 호출 형태를 유지하려고 받되 읽지 않는다). 그래서 P4
`T_merge` 스윕 곡선에서 이 방식의 선은 **수평선**이 되고, 그 수평선이 곧
"확신도 임계치로 오병합을 조절할 수 없는 방식"이라는 비교 정보다(원칙1·2
가 요구하는 조절 손잡이가 없다는 사실 자체가 결과다).

## 무엇을 하는 방식인가 (01-plan 57행·104행, 결정 E(ii))

원칙4 가 금지한 "LLM 한 번 부르고 끝"의 **정확한 재현**이다. 후보 검색
(1단계)·규칙 필터(2단계)·확신도 결합(4단계)이 전부 없다. 사전 상태의
**인물 목록 전체**(id·표시 이름·별칭·관계 태그·위계)와 mention·발화 맥락을
한 번의 강제 구조화 출력 호출로 보내고, 응답에서 결정까지 그대로 받는다::

    {decision: "merge"|"identity"|"new_person",
     matched_person_id: int|null,
     s_llm: 0~1,
     reason: str,
     candidate_person_ids: int[]}          # 결정 I(R-3)

`ClaudeJudge`/`OpenAIJudge`(3단계 판정기)를 재사용하지 **않는다** -- 그것을
쓰면 최종 결정은 여전히 바깥의 임계치 분기가 하므로 "부분 절제(ablation)"
이지 "LLM 단일 프롬프트"가 아니다(결정 E 의 (i) 를 기각한 이유). 다만
**공급자 호출부의 형태**(강제 도구 호출·온도 0·타임아웃·재시도·예외 매핑
표)는 `app/er/judge.py` 와 같게 두고, 예외 매핑은 그 모듈의
`call_with_error_mapping()` 을 **그대로 import 해 재사용**한다(결정 J --
`llm.error` 어휘가 네 방식에 동일해진다, 중복 구현 금지).

## 베이스라인을 약하게 만들지 않는다 (원칙8 -- 이 모듈의 최대 위험)

- 후보를 미리 걸러 주지 않는다(그건 이미 제안 방식의 1단계다). 대신 사전
  상태 **전체**를 준다 -- 이 방식이 낼 수 있는 가장 강한 합리적 형태다.
- 모델·공급자는 제안 방식과 **같은 환경변수**를 읽는다(`LLM_PROVIDER`·
  `ANTHROPIC_MODEL`·`OPENAI_MODEL`, R-4) -- 모델 차이가 방식 차이로
  둔갑하지 않게.
- 온도 0 고정, 타임아웃·재시도는 `ERConfig` 기본값과 같은 수치(20초·1회)를
  기본으로 쓴다.

## 강등 규칙 (불변 규약 2 -- 예외로 죽지 않는다)

한 방식만 예외로 죽으면 분모가 달라져 비교가 깨진다. LLM 이 무엇을 답하든
`MentionDecision` 하나가 나오고, 무슨 일이 있었는지는
`detail["forced_reason"]` 이 말한다. **`identity` 로 강등한다**(오병합이
미검출보다 훨씬 나쁘다 -- 원칙1, 비대칭 금지).

| 상황 | 결정 | `forced_reason` |
|---|---|---|
| LLM 호출·응답 실패 | `identity` | `timeout`/`rate_limit`/`api_error`/`connection`/`schema`(P3-er `llm.error` 어휘 그대로) |
| `decision` 이 어휘 밖 | `identity` | `unknown_decision:<원문>` |
| `matched_person_id` 가 사전 상태 밖 | `identity` | `out_of_range_id` |
| `decision="merge"` 인데 id 가 없음 | `identity` | `merge_without_person_id` |
| `identity` 인데 후보가 하나도 없음 | `identity` | `identity_without_candidates` |
| mention 이 빈 문자열 | `new_person` | `empty_mention`(LLM 을 부르지 않는다) |

사유가 겹치면 **먼저 일어난 것**이 남는다(호출 실패 > 어휘·id 위반 >
후보 없음). 한 자리에 하나만 담는 이유는 P4 가 `forced_reason` 을 범주로
집계하기 때문이다.

`candidate_person_ids` 중 사전 상태 **안**의 id 만 `candidates` 가 되고,
밖의 id(환각)는 버려서 `detail["dropped_ids"]` 에 기록한다(결정 I).
`s_llm` 이 `[0,1]` 밖이면 접고 `detail["score_clamped"]` 를 남긴다.

## 키·프롬프트를 남기지 않는다 (security.md §1)

키는 각 SDK 클라이언트가 환경변수에서 **내부적으로** 읽는다 -- 이 모듈은
키 값을 변수로 옮기지도, 프롬프트·`detail`·예외 메시지에 넣지도 않는다.
`detail` 에 남는 것은 프롬프트 **길이**(`prompt_chars`)와 **인물 수**
(`person_count`)뿐이고 프롬프트 원문은 어디에도 저장하지 않는다. 그래서 P4
비용 추정(01-plan 리스크 "비용")에 필요한 값은 남되 원문은 새지 않는다.

## 부수효과 0 (불변 규약 1)

DB 는 사전 상태 조회(`load_known_persons`, `SELECT` 만)에만 쓴다 --
`persons`·`person_aliases`·`pending_questions` 는 물론 `agent_traces` 도
쓰지 않는다(`@traced` 를 거치지 않는다).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from app.er.judge import call_with_error_mapping
from app.er.types import JudgeUnavailable
from evaluation.resolvers.base import DECISIONS, MentionDecision, ResolverCandidate
from evaluation.resolvers.exact_match import KnownPerson, load_known_persons
from evaluation.resolvers.registry import register

if TYPE_CHECKING:
    from app.er.types import ERConfig
    from app.tools.context import ToolContext

#: `RESOLVERS` 등록 이름 = `MentionDecision.method` = `metrics.json` 키
#: (P4 인계 4). 바꾸면 P4 산출물 스키마가 바뀐다.
METHOD_NAME = "llm_single"

#: 강제 구조화 출력 도구 이름. `app/er/judge.py` 의 `report_judgement` 와
#: **다른 이름**이다 -- 이 프롬프트는 판정이 아니라 **결정**을 받는다
#: (결정 E(ii)). 이름이 같으면 두 프롬프트가 같은 것이라는 오해가 생긴다.
TOOL_NAME = "report_resolution"

_TOOL_DESCRIPTION = (
    "이 mention 이 이미 아는 인물 중 누구인지 스스로 결정한다. 같은 사람이 "
    "확실하면 decision='merge' 와 matched_person_id 를, 누구인지 헷갈리면 "
    "decision='identity' 와 헷갈리는 후보들(candidate_person_ids)을, 아는 "
    "사람이 아니면 decision='new_person' 을 답한다. s_llm 은 스스로 판단한 "
    "확신도 0~1 이다(로그 확률이 아니다)."
)

#: 응답 JSON 스키마(결정 E(ii) + 결정 I). 공급자별 바깥 모양(도구 이름·
#: strict 플래그 위치)만 다르고 이 딕셔너리는 그대로 쓴다.
RESOLUTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": list(DECISIONS)},
        "matched_person_id": {"type": ["integer", "null"]},
        "s_llm": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
        "candidate_person_ids": {"type": "array", "items": {"type": "integer"}},
    },
    "required": [
        "decision",
        "matched_person_id",
        "s_llm",
        "reason",
        "candidate_person_ids",
    ],
    "additionalProperties": False,
}

SYSTEM_PROMPT = (
    "너는 한국어 대화에서 사람 지칭(mention)이 이미 저장된 인물 중 누구인지 "
    "스스로 결정하는 도구다. 아래 인물 목록에 없는 사람을 지어내지 말고, "
    "다른 사람을 같은 사람으로 잘못 묶는 것이 모르는 채로 두는 것보다 훨씬 "
    f"나쁘다는 것을 기억하라. {TOOL_NAME} 도구로만 답하라."
)

#: `detail["forced_reason"]` 어휘(모듈 docstring 표). 호출 실패 사유는
#: `app.er.types.JudgeUnavailable` 이 쓰는 P3-er `llm.error` 어휘를 그대로
#: 쓴다(`timeout`/`rate_limit`/`api_error`/`connection`/`schema`).
EMPTY_MENTION = "empty_mention"
OUT_OF_RANGE_ID = "out_of_range_id"
MERGE_WITHOUT_PERSON_ID = "merge_without_person_id"
IDENTITY_WITHOUT_CANDIDATES = "identity_without_candidates"
UNKNOWN_DECISION_PREFIX = "unknown_decision:"

#: `ask_user` 를 부르지 않으므로(불변 규약 1) 물었을 `kind` 만 남긴다 --
#: P4 `ask_user_rate_by_kind`(eval-harness §2) 입력. `proposed.py`·
#: `exact_match.py`·`embedding_only.py` 와 같은 대응이다.
_ASK_KIND_BY_DECISION: dict[str, str | None] = {
    "merge": None,
    "identity": "identity",
    "new_person": "new_person",
}

#: 기본 타임아웃·재시도. `ERConfig.judge_timeout`/`judge_max_retries` 와
#: 같은 수치이며(제안 방식과 같은 조건), SDK 가 재시도를 수행한다.
DEFAULT_TIMEOUT = 20.0
DEFAULT_MAX_RETRIES = 1


# ---------------------------------------------------------------------------
# 프롬프트 (공급자 무관, 단일 출처)
# ---------------------------------------------------------------------------


def _person_summary(person: KnownPerson) -> dict[str, Any]:
    """프롬프트에 넣을 인물 요약 -- id·표시 이름·별칭·관계 태그·위계만.

    키·환경변수·전체 대화 이력은 넣지 않는다(security.md §1). 별칭은
    `KnownPerson.all_names()` 에서 표시 이름을 뺀 나머지다(표시 이름은 이미
    별도 필드라 두 번 싣지 않는다).
    """

    names = [name for name in person.all_names() if name != person.display_name]
    return {
        "person_id": person.person_id,
        "display_name": person.display_name,
        "aliases": names,
        "relation_tag": person.relation_tag,
        "hierarchy": person.hierarchy,
    }


def build_prompt(
    mention: str, utterance: str, persons: list[KnownPerson]
) -> tuple[str, str]:
    """`(system, user_text)` 를 만든다(공급자 무관, 단일 출처).

    인물 목록은 **사전 상태 전체**다 -- 후보를 미리 좁혀 주면 그건 이미
    제안 방식의 1단계이고, 그렇게 만든 베이스라인은 이 방식의 정의가
    아니다(모듈 docstring "베이스라인을 약하게 만들지 않는다").
    """

    person_lines = [
        f"- {json.dumps(_person_summary(p), ensure_ascii=False, sort_keys=True)}"
        for p in persons
    ]
    user_text = (
        f'지칭(mention): "{mention}"\n'
        f'발화 맥락(utterance): "{utterance}"\n'
        "이미 아는 인물 목록(전체):\n"
        + ("\n".join(person_lines) if person_lines else "(없음)")
        + f"\n\n위 mention 을 어떻게 할지 {TOOL_NAME} 로 결정하라. 같은 사람이 "
        "확실하면 decision=\"merge\" 와 matched_person_id 를, 누구인지 "
        "헷갈리면 decision=\"identity\" 와 헷갈리는 인물들의 id 를 "
        "candidate_person_ids 에, 목록에 없는 새 사람이면 "
        "decision=\"new_person\" 을 보고하라. matched_person_id 와 "
        "candidate_person_ids 는 위 목록 안의 id 만 쓴다. s_llm 은 그 결정에 "
        "대한 확신도 0~1, reason 은 한국어 한 문장으로."
    )
    return SYSTEM_PROMPT, user_text


# ---------------------------------------------------------------------------
# 응답 검증 (공급자 무관, 단일 출처)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RawResolution:
    """구조화 출력에서 **형태만** 검증한 값. 어휘·id 범위 판단은 하지
    않는다 -- 그것은 강등 규칙(`build_decision`)의 몫이다."""

    decision: str
    matched_person_id: int | None
    s_llm: float
    reason: str
    candidate_person_ids: tuple[Any, ...] = ()
    candidate_ids_missing: bool = False


def validate_resolution(raw: dict[str, Any]) -> RawResolution:
    """구조화 출력(이미 dict)의 **자료형**을 검증한다. 위반은
    `JudgeUnavailable("schema")` -- `app/er/judge.py` `validate_judgement()`
    와 같은 어휘·같은 엄격함이다(두 방식이 같은 이유로 실패해야 비교가
    공정하다, 원칙8).

    - `decision` 이 문자열이 아니면 `schema`. **어휘 밖 문자열은 여기서
      막지 않는다** -- 그건 실패가 아니라 강등 대상이다(`unknown_decision:`).
    - `matched_person_id` 가 `int`/`None` 이 아니면 `schema`(`bool` 은
      `int` 의 하위형이라 따로 막는다).
    - `s_llm` 이 수가 아니면 `schema`. **범위 밖은 막지 않고 접는다**
      (`score_clamped`) -- 자기보고 점수의 눈금이 어긋난 것이 곧 그 방식의
      성질이고, 결정 자체를 버리면 분모가 달라진다(불변 규약 2).
    - `reason` 이 문자열이 아니면 `schema`.
    - `candidate_person_ids` 가 없으면 빈 목록으로 보고 그 사실을 남긴다.
      목록이 아니면 `schema`. **원소의 형태는 여기서 보지 않는다** --
      사전 상태 밖 id 와 같은 취급(`dropped_ids`)을 받는다(결정 I).
    """

    if not isinstance(raw, dict):
        raise JudgeUnavailable("schema")

    decision = raw.get("decision")
    matched_person_id = raw.get("matched_person_id")
    s_llm = raw.get("s_llm")
    reason = raw.get("reason")

    if not isinstance(decision, str):
        raise JudgeUnavailable("schema")

    if isinstance(matched_person_id, bool) or not (
        matched_person_id is None or isinstance(matched_person_id, int)
    ):
        raise JudgeUnavailable("schema")

    if isinstance(s_llm, bool) or not isinstance(s_llm, (int, float)):
        raise JudgeUnavailable("schema")

    if not isinstance(reason, str):
        raise JudgeUnavailable("schema")

    candidate_ids_missing = "candidate_person_ids" not in raw
    candidate_person_ids = raw.get("candidate_person_ids", [])
    if candidate_ids_missing:
        candidate_person_ids = []
    if not isinstance(candidate_person_ids, (list, tuple)):
        raise JudgeUnavailable("schema")

    return RawResolution(
        decision=decision,
        matched_person_id=matched_person_id,
        s_llm=float(s_llm),
        reason=reason,
        candidate_person_ids=tuple(candidate_person_ids),
        candidate_ids_missing=candidate_ids_missing,
    )


# ---------------------------------------------------------------------------
# 공급자 호출부 (형태는 app/er/judge.py 와 같다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SingleCallResult:
    """한 번의 호출 결과. `raw` 는 구조화 출력 dict 그대로다."""

    raw: dict[str, Any]
    tokens_in: int = 0
    tokens_out: int = 0
    model: str | None = None
    provider: str = ""


class SingleCaller(Protocol):
    """`(system, user_text) -> SingleCallResult`. 공급자 무관.

    실패는 전부 `JudgeUnavailable`(P3-er `llm.error` 어휘)로 나온다 --
    resolver 가 그것을 `identity` 강등으로 흡수한다(불변 규약 2).
    """

    provider: str
    model: str | None

    def complete(self, system: str, user_text: str) -> SingleCallResult: ...


@dataclass
class ClaudeSingleCaller:
    """Anthropic SDK, 강제 `tool_use` 1회. `ClaudeJudge` 와 **같은 형태**
    (지연 import·키는 SDK 가 환경변수에서 읽음·`max_retries` 를 SDK 에
    맡김)이고 다른 것은 도구 스키마와 `temperature=0` 뿐이다.

    `model` 기본값은 env `ANTHROPIC_MODEL`(제안 방식과 같은 이름, R-4) --
    생성 시점에 읽는다.
    """

    provider: str = "anthropic"
    model: str | None = None
    client: Any = None
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        if self.client is None:
            import anthropic  # 지연 import -- 키·SDK 없이도 import 가 깨지지 않게.

            self.client = anthropic.Anthropic(
                timeout=self.timeout, max_retries=self.max_retries
            )

    def complete(self, system: str, user_text: str) -> SingleCallResult:
        import anthropic  # 예외 클래스·매핑용 지연 import.

        tool_schema = {
            "name": TOOL_NAME,
            "description": _TOOL_DESCRIPTION,
            "strict": True,
            "input_schema": RESOLUTION_SCHEMA,
        }

        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=512,
                temperature=0,
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

        usage = getattr(response, "usage", None)
        return SingleCallResult(
            raw=tool_use_input,
            tokens_in=getattr(usage, "input_tokens", 0) if usage is not None else 0,
            tokens_out=getattr(usage, "output_tokens", 0) if usage is not None else 0,
            model=getattr(response, "model", self.model),
            provider=self.provider,
        )


@dataclass
class OpenAISingleCaller:
    """OpenAI SDK, function calling 1회. `OpenAIJudge` 와 같은 형태이고
    `model` 기본값은 env `OPENAI_MODEL`(R-4 -- 공급자 중립을 말하면서
    Claude 모델 변수만 읽으면 "제안 방식과 같은 모델" 보장이 깨진다)."""

    provider: str = "openai"
    model: str | None = None
    client: Any = None
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if self.client is None:
            import openai  # 지연 import.

            self.client = openai.OpenAI(
                timeout=self.timeout, max_retries=self.max_retries
            )

    def complete(self, system: str, user_text: str) -> SingleCallResult:
        import openai  # 예외 클래스·매핑용 지연 import.

        tool_schema = {
            "type": "function",
            "function": {
                "name": TOOL_NAME,
                "description": _TOOL_DESCRIPTION,
                "parameters": RESOLUTION_SCHEMA,
                "strict": True,
            },
        }

        response = call_with_error_mapping(
            openai,
            lambda: self.client.chat.completions.create(
                model=self.model,
                temperature=0,
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
            tool_calls = (
                getattr(message, "tool_calls", None) if message is not None else None
            )
        if not tool_calls:
            raise JudgeUnavailable("schema")

        try:
            arguments = json.loads(tool_calls[0].function.arguments)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        usage = getattr(response, "usage", None)
        return SingleCallResult(
            raw=arguments,
            tokens_in=getattr(usage, "prompt_tokens", 0) if usage is not None else 0,
            tokens_out=getattr(usage, "completion_tokens", 0) if usage is not None else 0,
            model=getattr(response, "model", self.model),
            provider=self.provider,
        )


def caller_from_env(
    env: dict[str, str] | None = None,
    *,
    client: Any = None,
    model: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> SingleCaller:
    """`LLM_PROVIDER`(기본은 `app.settings.LLM_PROVIDER`)로 공급자를 고른다
    -- **제안 방식(`judge_from_env`)과 같은 환경변수**를 읽는다(R-4). 모델은
    각 caller 생성자가 공급자별 env(`ANTHROPIC_MODEL`/`OPENAI_MODEL`)를
    읽으므로 여기서 다시 읽지 않는다(단일 출처).

    `client` 는 테스트용 스텁 주입 자리다(네트워크 0). `gemini` 는
    `judge_from_env()` 와 같은 이유로 구현하지 않고 사람이 읽는
    `InvalidValue` 를 던진다(우회 구현하지 않는다, 원칙8).
    """

    from app.settings import LLM_PROVIDER
    from app.tools.types import InvalidValue

    if env is None:
        env = dict(os.environ)

    provider = env.get("LLM_PROVIDER", LLM_PROVIDER)

    if provider == "anthropic":
        return ClaudeSingleCaller(
            model=model, client=client, timeout=timeout, max_retries=max_retries
        )
    if provider == "openai":
        return OpenAISingleCaller(
            model=model, client=client, timeout=timeout, max_retries=max_retries
        )
    if provider == "gemini":
        raise InvalidValue(
            "gemini 단일 프롬프트 베이스라인은 아직 구현되지 않았다 — "
            "google-genai 의존성 추가 필요"
        )
    raise InvalidValue(
        f"caller_from_env: unknown LLM_PROVIDER {provider!r} "
        "(expected one of ('anthropic', 'openai', 'gemini'))"
    )


# ---------------------------------------------------------------------------
# 결정 만들기 (순수 -- DB·네트워크 없음)
# ---------------------------------------------------------------------------


def _clamp01(value: float) -> tuple[float, bool]:
    numeric = float(value)
    if numeric != numeric:  # NaN 은 어떤 비교에도 False 라 따로 거른다.
        return 0.0, True
    if numeric < 0.0:
        return 0.0, True
    if numeric > 1.0:
        return 1.0, True
    return numeric, False


@dataclass(frozen=True)
class _Filtered:
    kept: tuple[int, ...] = ()
    dropped: tuple[Any, ...] = ()


def _filter_ids(ids: tuple[Any, ...], state_ids: set[int]) -> _Filtered:
    """사전 상태 안의 id 만 남긴다(순서 유지·중복 제거). 밖의 id·정수가
    아닌 값은 **버리고 기록**한다(결정 I) -- 없는 사람을 후보로 세우면
    그것이 곧 환각을 지표에 섞는 일이다(원칙8)."""

    kept: list[int] = []
    dropped: list[Any] = []
    for value in ids:
        if isinstance(value, bool) or not isinstance(value, int):
            dropped.append(value)
            continue
        if value not in state_ids:
            dropped.append(value)
            continue
        if value not in kept:
            kept.append(value)
    return _Filtered(kept=tuple(kept), dropped=tuple(dropped))


def build_decision(
    parsed: RawResolution | None,
    persons: list[KnownPerson],
    *,
    mention: str,
    prompt_chars: int = 0,
    tokens_in: int = 0,
    tokens_out: int = 0,
    provider: str | None = None,
    model: str | None = None,
    error: str | None = None,
    forced_reason: str | None = None,
) -> MentionDecision:
    """`RawResolution`(또는 실패) -> `MentionDecision` **순수 변환**.

    `parsed` 가 `None` 이면 호출·응답이 실패한 것이고, `error`(P3-er
    `llm.error` 어휘) 또는 `forced_reason`(예: `empty_mention`)이 그 사유다.
    강등 규칙은 모듈 docstring 의 표 그대로이며 **예외를 던지지 않는다**
    (불변 규약 2).
    """

    display_by_id = {p.person_id: p.display_name for p in persons}
    state_ids = set(display_by_id)

    score = 0.0
    score_clamped = False
    reason: str | None = None
    raw_decision: str | None = None
    raw_matched_person_id: Any = None
    dropped: tuple[Any, ...] = ()
    candidate_ids: tuple[int, ...] = ()
    candidate_ids_missing = False
    person_id: int | None = None

    if parsed is None:
        # 호출·응답 실패, 또는 호출하기 전에 이미 결정된 경우(빈 mention).
        decision = "new_person" if forced_reason == EMPTY_MENTION else "identity"
        if forced_reason is None:
            forced_reason = error
    else:
        raw_decision = parsed.decision
        raw_matched_person_id = parsed.matched_person_id
        reason = parsed.reason
        score, score_clamped = _clamp01(parsed.s_llm)
        candidate_ids_missing = parsed.candidate_ids_missing

        filtered = _filter_ids(parsed.candidate_person_ids, state_ids)
        candidate_ids = filtered.kept
        dropped = filtered.dropped

        decision = parsed.decision
        if decision not in DECISIONS:
            decision = "identity"
            forced_reason = f"{UNKNOWN_DECISION_PREFIX}{parsed.decision}"
        elif (
            parsed.matched_person_id is not None
            and parsed.matched_person_id not in state_ids
        ):
            # 사전 상태 밖 id -- API 장애와 구분되는 이름을 남긴다(F-5a97ef
            # 와 같은 어휘).
            decision = "identity"
            forced_reason = OUT_OF_RANGE_ID
        elif decision == "merge" and parsed.matched_person_id is None:
            decision = "identity"
            forced_reason = MERGE_WITHOUT_PERSON_ID
        elif decision == "merge":
            person_id = parsed.matched_person_id
            # 고른 인물은 후보 목록 맨 앞에 온다(근거를 남긴다, 원칙9).
            candidate_ids = (person_id,) + tuple(
                pid for pid in candidate_ids if pid != person_id
            )

        if decision == "identity" and not candidate_ids and forced_reason is None:
            # `identity` 는 "사람에게 묻는다"이므로 후보 목록이 답인데
            # (불변 규약 3) 그 목록이 비었다 -- 결정 I 가 정한 사유.
            forced_reason = IDENTITY_WITHOUT_CANDIDATES

    candidates = [
        ResolverCandidate(
            person_id=pid,
            display_name=display_by_id.get(pid, ""),
            # 이 방식은 후보별 점수를 내지 않는다(결정 하나에 자기보고
            # 확신도 하나) -- 고른 인물에만 `s_llm` 을 싣고 나머지는 0.0
            # ("점수 없음", base.py `ResolverCandidate.score`).
            score=score if pid == person_id else 0.0,
            signals={"s_llm": score} if pid == person_id else {},
        )
        for pid in candidate_ids
    ]

    detail: dict[str, Any] = {
        "forced_reason": forced_reason,
        # LLM 원문 결정(강등 전) -- 강등이 있었는지 P4 가 가른다(원칙9).
        "raw_decision": raw_decision,
        "raw_matched_person_id": raw_matched_person_id,
        "reason": reason,
        "dropped_ids": list(dropped),
        "candidate_ids_missing": candidate_ids_missing,
        "person_count": len(persons),
        # 프롬프트 **길이만** 남긴다 -- 원문·키는 남기지 않는다(security §1).
        # P4 비용 추정(01-plan 리스크 "비용")의 입력이다.
        "prompt_chars": prompt_chars,
        "provider": provider,
        "model": model,
        "llm_error": error,
        "llm_calls": 0 if parsed is None and error is None else 1,
        "ask_kind": _ASK_KIND_BY_DECISION[decision],
        # 이 방식이 쓴/쓰지 않은 신호(원칙4 의 대비군 정의 -- 후보 검색·
        # 규칙 필터·임계치가 **전부 없다**는 것이 이 방식의 정의다).
        "uses_embedding": False,
        "uses_llm": True,
        "uses_rules": False,
        "uses_thresholds": False,
    }
    if score_clamped:
        detail["score_clamped"] = True

    return MentionDecision(
        method=METHOD_NAME,
        mention=mention,
        decision=decision,
        person_id=person_id,
        score=score,
        candidates=candidates,
        trace_id=None,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        detail=detail,
    )


def resolve_from_state(
    persons: list[KnownPerson],
    mention: str,
    utterance: str,
    *,
    caller: SingleCaller,
) -> MentionDecision:
    """사전 상태 목록 + 호출자 -> `MentionDecision`(**DB 없음**).

    `resolve_mention()` 과 `scripts/baseline_smoke.py` 가 이 함수를 공유한다
    -- 스모크가 별도 경로로 프롬프트를 만들면 실호출로 확인한 것이 평가에서
    도는 것과 달라진다(이중 출처 금지).

    LLM 호출은 **정확히 1회**다(01-plan 115행 "LLM 호출 정확히 1회").
    재시도는 SDK 가 `max_retries` 로 수행하며 이 함수는 루프를 돌지 않는다
    (`ClaudeJudge` 와 같은 방식).
    """

    if mention is None or not mention.strip():
        # 부를 필요가 없다 -- 다른 베이스라인과 같은 자리에서 같은 결정을
        # 내고(분모 유지) 비용도 쓰지 않는다(불변 규약 2).
        return build_decision(
            None,
            persons,
            mention=mention or "",
            forced_reason=EMPTY_MENTION,
        )

    system, user_text = build_prompt(mention, utterance, persons)
    prompt_chars = len(system) + len(user_text)

    try:
        result = caller.complete(system, user_text)
        parsed = validate_resolution(result.raw)
    except JudgeUnavailable as exc:
        # 예외 비대칭 금지(불변 규약 2) -- 실패도 결정으로 표현한다.
        # 예외 메시지에는 유형 이름만 있고 키·프롬프트는 없다(security §1).
        return build_decision(
            None,
            persons,
            mention=mention,
            prompt_chars=prompt_chars,
            provider=getattr(caller, "provider", None),
            model=getattr(caller, "model", None),
            error=str(exc),
        )

    return build_decision(
        parsed,
        persons,
        mention=mention,
        prompt_chars=prompt_chars,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        provider=result.provider or getattr(caller, "provider", None),
        model=result.model,
    )


@register(METHOD_NAME)
class LLMSingleResolver:
    """베이스라인 3 -- 한 번의 강제 구조화 출력 호출로 결정까지 받는다.

    팩토리 인자::

        get_resolver("llm_single", client=StubClaudeClient(...))   # 테스트
        get_resolver("llm_single")                                 # P4 실행

    `client` 는 공급자 SDK 클라이언트(또는 그 형태의 스텁)이고, `caller` 는
    `SingleCaller` 자체를 통째로 주입하는 자리다. 둘 다 없으면 **첫 호출
    시점에** `caller_from_env()` 가 환경변수로 공급자를 고른다 -- 생성만
    해서는 SDK·키를 요구하지 않으므로 `for name in ALL_METHODS:` 로 전
    방식을 만드는 계약 테스트가 키 없이도 돈다.

    `supported_decisions` 는 세 밴드 전부다(결정 B(i)).
    """

    name: str = METHOD_NAME
    supported_decisions: tuple[str, ...] = DECISIONS

    def __init__(
        self,
        client: Any = None,
        caller: SingleCaller | None = None,
        *,
        model: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        env: dict[str, str] | None = None,
    ) -> None:
        self.client = client
        self.caller = caller
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.env = env

    def _get_caller(self) -> SingleCaller:
        if self.caller is None:
            self.caller = caller_from_env(
                self.env,
                client=self.client,
                model=self.model,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        return self.caller

    def resolve_mention(
        self,
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: ERConfig | None = None,
    ) -> MentionDecision:
        """사전 상태 조회 1회(`SELECT`) -> LLM 호출 1회 -> 순수 변환 1회.

        `hints`·`config` 는 **받지만 쓰지 않는다** -- `hints` 는 후보 검색용
        이고 이 방식에는 후보 검색이 없다. `config`(`ERConfig`)의 임계치는
        결정을 LLM 이 직접 내므로 적용할 자리가 없다(모듈 docstring "두
        임계치"). 임계치를 여기서 새로 정의하지 않는다(불변 규약 4).

        사전 상태 조회는 `exact_match.load_known_persons()` 를 **재사용**
        한다(중복 구현 금지) -- 네 방식이 같은 사전 상태를 본다는 것이
        "동일 데이터"의 뜻이다.
        """

        persons = load_known_persons(ctx)
        return resolve_from_state(
            persons, mention, utterance, caller=self._get_caller()
        )
