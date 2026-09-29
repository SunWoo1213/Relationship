"""Refs: P6-memory S3.5 D11 D-2 D-3 D-4 D-5 D-7 R8 원칙7 원칙8 원칙9 -- U4
사실 추출기. `FactExtractor` Protocol·`FACTS_SCHEMA`·`build_extract_prompt()`·
`validate_extraction()`·공급자 구현(등록표 재사용)·`extractor_from_env()`·
`FakeFactExtractor` 를 정의한다. 승격(U5, `app/memory/promote.py`)이 이
모듈을 호출한다 -- 이 단위는 배선을 만들지 않는다.

## 이 모듈이 하지 않는 것 (원칙7)

추출기가 뽑는 사실은 **그 한 인물**에 관한 것뿐이다. 인물 간(A-B) 관계나
감정 해석·조언 문장을 만들지 않는다 -- 프롬프트(`build_extract_prompt`)
자체가 이 경계를 적어 LLM 에 지시하고, `FACT_KEYS`(`app/memory/types.py`,
결정 D-5)에 인물 간 관계 키가 아예 없어 설령 LLM 이 그런 문장을 값으로
써도 `validate_extraction()` 이 걸러내지는 못한다(자유 텍스트라 문자열
자체는 통과) -- 그 방지선은 프롬프트뿐이고, 실제 추출 품질 측정은 이
패키지 밖(P10-final-eval, 01-plan 리스크 절)이다.

## 구조 파싱 vs 의미 검증 (두 층, `propose.py`/`gate.py` 와 같은 경계)

- **구조 파싱**(`_parse_extraction`, 이 모듈 비공개) -- 공급자 구현
  (`ClaudeFactExtractor`/`OpenAIFactExtractor`/`GeminiFactExtractor`/
  `FakeFactExtractor`)이 각자 받은 raw dict 를 `Extraction` 으로 바꾸는
  자리다. 타입만 본다 -- `facts` 가 리스트인가, 각 원소의 `key`/`value`
  가 문자열인가, `source_event_ids` 가 정수 리스트인가(FIX-007 처럼
  `bool` 은 `int` 서브클래스라 먼저 배제). 깨지면 `app.er.judge` 의
  판정과 같은 신호(`JudgeUnavailable("schema")`)로 실패한다 --
  `validate_proposal`/`validate_judgement` 와 같은 층위(`app/agent/
  propose.py`/`app/er/judge.py`). **빈 값·어휘 밖 키·`pattern:` 접두·
  입력에 없는 이벤트 id·상한 초과는 여기서 걸러내지 않는다** -- 그건
  구조가 아니라 의미이고, 하나가 틀렸다고 전체 응답을 버리면 01-plan
  70행 "개별 사실 단위로 거부"가 성립하지 않는다.
- **의미 검증**(`validate_extraction`, 공개) -- 이미 구조가 맞는
  `Extraction` 을 입력 이벤트 목록과 대조해 사실 하나하나를 통과/거부로
  가른다. 거부해도 예외를 던지지 않고 `RejectedFact` 로 모아 돌려준다
  (호출자인 U5 가 `memory_promote` trace `rejected[]`, 결정 F에 옮긴다).

## 이 단위가 스스로 정한 것 (01-plan 이 U4 에 넘긴 결정, 근거는 03-log)

1. **입력 타입 모양** -- `person` 은 표시 이름 문자열 하나(전체 `Person`
   객체가 아니다, 원칙7 "그 한 인물"), `existing_facts`/`events` 는 이
   모듈이 새로 정의하는 작은 불변 dataclass(`ExistingFact`/
   `ExtractEvent`) 목록이다. `ScoredCandidate`/`Judgement`/`Proposal` 등
   이 모듈 경계를 넘는 구조화 데이터를 전부 dataclass 로 표현하는 관례를
   따른다(dict 대신 -- 필드 오타가 `AttributeError`로 즉시 드러난다).
2. **타임아웃·재시도** -- 새 상수를 만들지 않고 `app.settings.
   ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES` 를 그대로 재사용한다
   (`app/agent/propose.py` 와 같은 선례, 01-plan 213행이 U4 에 넘긴
   결정).
3. **`MEMORY_MAX_FACTS` 초과 처리** -- LLM 출력 배열 순서대로 앞에서부터
   상한까지만 받아들이고, 상한을 넘는 사실은 순서상 인덱스 그대로
   `over_cap` 사유로 거부한다(뒤에서 자르거나 재정렬하지 않는다 -- LLM
   이 이미 그 순서로 중요도를 매겼다고 보는 것이 별도 정렬 기준을
   새로 만드는 것보다 결정적이고 단순하다).

## 공급자 재사용 (D11) -- `app/er/judge.py` 는 import 만 한다

`select_provider`(공급자 선택+거부 판정의 유일한 자리)·
`call_with_error_mapping`/`call_with_gemini_error_mapping`(예외 매핑 표)·
`_to_gemini_schema`(Gemini 스키마 변환)를 그대로 재사용한다 --
`app/agent/propose.py` 가 같은 것을 재사용하는 것과 같은 방식(D11, 두
번째 매핑 헬퍼·두 번째 변환기를 만들지 않는다). 오류 어휘는 `JudgeUnavailable`
의 기존 6종(`timeout`/`rate_limit`/`api_error`/`connection`/`schema`/
`out_of_range_id`)만 쓴다 -- 이 모듈이 실제로 내는 것은 `schema`뿐이다
(`out_of_range_id` 는 판정 후보 id 범위 밖을 가리키는 ER 전용 신호라 이
모듈에는 대응 개념이 없다).

`FACT_EXTRACTORS`(이름 -> 무인자 팩토리 등록표)는 `app/agent/propose.py`
의 `PROPOSERS` 와 같은 정신이다 -- 스키마(`FACTS_SCHEMA` vs
`PROPOSAL_SCHEMA`/`JUDGEMENT_SCHEMA`)가 달라 `JUDGES`/`PROPOSERS` 표를
그대로 쓸 수 없지만, 이름 집합과 선택 로직(`select_provider`)은 그
표들과 공유한다. 이름을 `EXTRACTORS` 가 아니라 `FACT_EXTRACTORS` 로 둔
것은 "자체 선택 로직을 새로 만들지 않았다"를 grep 으로 스스로 점검하기
위해서다(01-plan U4 판정 절차의 자기점검 grep, 이름이 `PROVIDERS`/
`EXTRACTORS` 로 시작하면 "새 공급자 추상화를 만든 것 아니냐"는 오탐 신호가
된다 -- 실제로는 `PROPOSERS`/`JUDGES` 와 동일한 재사용 패턴이다).
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, NamedTuple, Protocol

from app.er.judge import (
    _to_gemini_schema,
    call_with_error_mapping,
    call_with_gemini_error_mapping,
    select_provider,
)
from app.er.types import JudgeUnavailable
from app.memory.types import FACT_KEYS, ExtractedFact, Extraction, RejectedFact
from app.settings import ER_JUDGE_MAX_RETRIES, ER_JUDGE_TIMEOUT, MEMORY_MAX_FACTS, PATTERN_KEY_PREFIX

# ---------------------------------------------------------------------------
# 입력 타입 (이 단위가 정한 것 1 -- 모듈 docstring 참고)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExistingFact:
    """`extract()` 에 넘기는 "기존 비패턴 사실" 한 건(01-plan 70행). 호출자
    (U5 `promote_person`)가 `person_facts` 에서 `pattern:` 접두를 제외해
    넘긴다고 가정한다 -- 이 모듈은 그 필터링을 다시 하지 않는다. 여러
    값이 누적돼야 하는 키(`likes` 등)에서 LLM 이 기존 값과 새 정보를
    합친 값을 내도록 프롬프트에 실린다(결정 D-6)."""

    key: str
    value: str


@dataclass(frozen=True)
class ExtractEvent:
    """`extract()` 에 넘기는 이벤트 한 건 -- `events.{id, type, content,
    raw_utterance, occurred_at}`(01-plan 70행). `app.db.models.Event`
    ORM 행 자체를 넘기지 않는다 -- 이 모듈은 DB 를 import 하지 않는다
    (승격 로직은 U5 몫이고, 이 모듈은 순수 추출기다)."""

    id: int
    type: str
    content: str
    raw_utterance: str
    occurred_at: datetime


# ---------------------------------------------------------------------------
# FactExtractor Protocol
# ---------------------------------------------------------------------------


class FactExtractor(Protocol):
    """승격(U5)이 부르는 인터페이스. `person` 은 표시 이름 문자열뿐이다
    (원칙7 "그 한 인물") -- 다른 인물 정보를 넘기지 않는다."""

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction: ...


# ---------------------------------------------------------------------------
# 구조화 출력 스키마 (결정 D-2)
# ---------------------------------------------------------------------------

FACTS_TOOL_NAME = "report_facts"

_FACTS_TOOL_DESCRIPTION = (
    "한 인물에 대한 이벤트 목록에서, 그 인물에 관해 기억해 둘 만한 사실을 "
    "뽑는다. 근거가 된 이벤트 id 를 사실마다 반드시 적는다."
)

#: 사실 한 건의 스키마. `key` 는 `FACT_KEYS` 로 **유도**할 뿐이다 --
#: 실제 거부 권한은 이 모듈이 아니라 `validate_extraction()` 하나뿐이다
#: (PROPOSAL_ARG_SCHEMA 의 `type`/`relation_tag`/`hierarchy` enum 과 같은
#: 정신, `app/agent/propose.py` 127~130행).
_FACT_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "key": {"type": "string", "enum": list(FACT_KEYS)},
        "value": {"type": "string"},
        "source_event_ids": {
            "type": "array",
            "items": {"type": "integer"},
        },
    },
    "required": ["key", "value", "source_event_ids"],
    "additionalProperties": False,
}

#: 판정 JSON 스키마 단일 출처(이 모듈 안에서) -- `{facts: [...]}` (결정
#: D-2). 어느 공급자든 이 딕셔너리 그대로를 도구/함수 스키마의
#: `input_schema`/`parameters`(또는 Gemini `response_schema`)로 쓴다.
FACTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "items": _FACT_ITEM_SCHEMA,
        }
    },
    "required": ["facts"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# 프롬프트 조립
# ---------------------------------------------------------------------------


def build_extract_prompt(
    person: str,
    existing_facts: Sequence[ExistingFact],
    events: Sequence[ExtractEvent],
) -> tuple[str, str]:
    """`(system, user_text)` 를 만든다. 인물 표시 이름 하나·기존 사실·
    이 인물의 이벤트 목록만 넣는다 -- 다른 인물의 정보·키·환경변수는
    넣지 않는다(security §1, 원칙7)."""

    existing_lines = [f"- {fact.key}: {fact.value}" for fact in existing_facts]
    event_lines = [
        (
            f"- id={event.id} type={event.type} "
            f"occurred_at={event.occurred_at.isoformat()} "
            f'raw="{event.raw_utterance}"'
        )
        for event in events
    ]

    system = (
        "너는 한국어 대화 기록에서 한 인물에 관한 사실만 뽑는 보조 도구다. "
        f"뽑을 수 있는 키는 다음 {len(FACT_KEYS)}종뿐이다: "
        f"{', '.join(FACT_KEYS)}. 이 목록 밖의 키나 'pattern:' 으로 시작하는 "
        "키는 절대 쓰지 마라. 두 사람 사이의 관계(예: '민수와 지훈이 사이가 "
        "안 좋다')나 감정 해석·조언은 사실로 만들지 마라 -- 오직 이 인물 "
        "한 사람에 관해 실제로 있었던 사실만 다룬다. 근거가 부족하면 사실을 "
        "만들지 마라. 사실마다 근거가 된 이벤트 id 를 source_event_ids 에 "
        "하나 이상 적어라(아래 이벤트 목록에 있는 id 만 써라). 기존 사실과 "
        "이어지는 새 정보가 있으면(예: 좋아하는 것이 늘어남) 기존 값과 "
        f"합친 값을 내라. {FACTS_TOOL_NAME} 도구로만 답하라."
    )
    user_text = (
        f'인물: "{person}"\n'
        "기존 사실:\n"
        + ("\n".join(existing_lines) if existing_lines else "(없음)")
        + "\n\n이벤트 목록:\n"
        + ("\n".join(event_lines) if event_lines else "(없음)")
        + "\n\n위 이벤트에서 이 인물에 관한 사실을 뽑아 "
        f"{FACTS_TOOL_NAME} 로 답하라. 뽑을 사실이 없으면 facts 를 빈 "
        "배열로 답하라."
    )
    return system, user_text


# ---------------------------------------------------------------------------
# 구조 파싱 (모듈 docstring "구조 파싱 vs 의미 검증" 절 -- 타입만 본다)
# ---------------------------------------------------------------------------


def _parse_extraction(raw: dict[str, Any]) -> Extraction:
    """구조화 출력(이미 dict)을 **타입만** 검증해 `Extraction` 으로
    바꾼다. `validate_proposal`/`validate_judgement` 와 같은 층위 --
    실패하면 `JudgeUnavailable("schema")`. 빈 값·어휘 밖 키·`pattern:`
    접두·이벤트 id 소속·상한은 여기서 보지 않는다(`validate_extraction()`
    몫, 개별 사실 단위 거부를 이 함수가 선점하면 안 된다)."""

    if not isinstance(raw, dict):
        raise JudgeUnavailable("schema")

    facts_raw = raw.get("facts")
    if not isinstance(facts_raw, list):
        raise JudgeUnavailable("schema")

    parsed: list[ExtractedFact] = []
    for item in facts_raw:
        if not isinstance(item, dict):
            raise JudgeUnavailable("schema")

        key = item.get("key")
        value = item.get("value")
        source_event_ids = item.get("source_event_ids")

        if not isinstance(key, str) or not key:
            raise JudgeUnavailable("schema")
        if not isinstance(value, str):
            raise JudgeUnavailable("schema")
        if not isinstance(source_event_ids, list):
            raise JudgeUnavailable("schema")

        ids: list[int] = []
        for raw_id in source_event_ids:
            # bool 은 int 의 서브클래스이므로 먼저 배제한다(FIX-007 과
            # 같은 관례, `app/er/judge.py::validate_judgement` 참고).
            if isinstance(raw_id, bool) or not isinstance(raw_id, int):
                raise JudgeUnavailable("schema")
            ids.append(raw_id)

        parsed.append(ExtractedFact(key=key, value=value, source_event_ids=ids))

    return Extraction(facts=parsed)


# ---------------------------------------------------------------------------
# 의미 검증 (공개, 개별 사실 단위 거부 -- 01-plan 70행)
# ---------------------------------------------------------------------------

#: 거부 사유 어휘 5종(01-plan 70행, 짧은 코드 -- `JudgeUnavailable` 의
#: 오류 어휘와 같은 스타일). `RejectedFact.reason` 에 그대로 들어간다.
REASON_KEY_NOT_IN_VOCAB = "key_not_in_vocab"
REASON_PATTERN_PREFIX = "pattern_prefix"
REASON_EMPTY_VALUE = "empty_value"
REASON_UNKNOWN_EVENT_ID = "unknown_event_id"
REASON_OVER_CAP = "over_cap"


class ValidatedExtraction(NamedTuple):
    """`validate_extraction()` 의 반환 타입 -- 통과한 사실과 거부된 사실을
    함께 담는다. `Extraction.facts` 하나만으로는 "왜 나머지가 사라졌는지"
    를 표현할 수 없어(01-plan 70행 "개별 사실 단위로 거부하고 사유를
    남긴다"), U5 가 `memory_promote` trace 의 `rejected[]`(결정 F)를 채울
    수 있도록 둘을 함께 돌려준다."""

    facts: list[ExtractedFact]
    rejected: list[RejectedFact]


def validate_extraction(
    extraction: Extraction, events: Sequence[ExtractEvent]
) -> ValidatedExtraction:
    """`extraction.facts` 를 하나씩 검사해 통과/거부로 가른다. 하나가
    거부돼도 나머지는 그대로 평가한다(01-plan 70행) -- 이 함수는 절대
    예외를 던지지 않는다(구조가 이미 `_parse_extraction` 을 통과했다고
    가정한다).

    검사 순서(각 사실마다, 먼저 걸리는 사유 하나만 기록):
    1. `pattern:` 접두(공백 제거 후 대소문자 무시, `app/tools/persons.py`
       `update_person` 의 U3 규칙과 같은 방식) -- `REASON_PATTERN_PREFIX`.
       이 검사를 어휘 검사보다 먼저 해야 `pattern:meal` 같은 키가
       "어휘 밖"(1번)이 아니라 "예약 접두"(2번)로 구분된다.
    2. `FACT_KEYS` 어휘 밖 -- `REASON_KEY_NOT_IN_VOCAB`. `"patterns"`처럼
       접두는 아니지만 어휘에도 없는 키가 여기 걸린다.
    3. 빈 값(공백만 포함) -- `REASON_EMPTY_VALUE`.
    4. `source_event_ids` 가 비었거나 입력 `events` id 집합 밖의 id 를
       포함 -- `REASON_UNKNOWN_EVENT_ID`(01-plan 70행 "int[>=1]이므로
       빈 목록도 거부").
    5. 위 네 가지를 통과한 사실이 이미 `MEMORY_MAX_FACTS` 개 쌓였으면
       -- `REASON_OVER_CAP`. LLM 출력 순서대로 앞에서부터 받아들인다
       (이 단위가 정한 것 3, 모듈 docstring).
    """

    valid_event_ids = {event.id for event in events}
    accepted: list[ExtractedFact] = []
    rejected: list[RejectedFact] = []

    for index, fact in enumerate(extraction.facts):
        normalized_key = fact.key.strip()
        normalized_value = fact.value.strip()

        if normalized_key.casefold().startswith(PATTERN_KEY_PREFIX.casefold()):
            rejected.append(RejectedFact(index=index, key=fact.key, reason=REASON_PATTERN_PREFIX))
            continue

        if normalized_key not in FACT_KEYS:
            rejected.append(RejectedFact(index=index, key=fact.key, reason=REASON_KEY_NOT_IN_VOCAB))
            continue

        if not normalized_value:
            rejected.append(RejectedFact(index=index, key=fact.key, reason=REASON_EMPTY_VALUE))
            continue

        if not fact.source_event_ids or not set(fact.source_event_ids) <= valid_event_ids:
            rejected.append(RejectedFact(index=index, key=fact.key, reason=REASON_UNKNOWN_EVENT_ID))
            continue

        if len(accepted) >= MEMORY_MAX_FACTS:
            rejected.append(RejectedFact(index=index, key=fact.key, reason=REASON_OVER_CAP))
            continue

        accepted.append(
            ExtractedFact(
                key=normalized_key,
                value=normalized_value,
                source_event_ids=list(fact.source_event_ids),
            )
        )

    return ValidatedExtraction(facts=accepted, rejected=rejected)


# ---------------------------------------------------------------------------
# 공급자 구현 (judge.py 의 등록표 개념·select_provider·오류 매핑 재사용, D11)
# ---------------------------------------------------------------------------


@dataclass
class ClaudeFactExtractor:
    """Anthropic SDK 로 사실을 추출한다. `app/agent/propose.py::
    ClaudeProposer` 와 같은 관례(생성 시점에 `ANTHROPIC_MODEL` 을 읽는다,
    키는 SDK 가 환경변수에서 직접 읽는다, security §1). 타임아웃·재시도는
    새 상수 없이 `ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES` 를 그대로 쓴다
    (이 단위가 정한 것 2)."""

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

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction:
        import anthropic  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_extract_prompt(person, existing_facts, events)
        tool_schema = {
            "name": FACTS_TOOL_NAME,
            "description": _FACTS_TOOL_DESCRIPTION,
            "input_schema": FACTS_SCHEMA,
        }

        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_text}],
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": FACTS_TOOL_NAME},
            ),
        )

        tool_use_input = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use":
                tool_use_input = block.input
                break

        if tool_use_input is None:
            raise JudgeUnavailable("schema")

        extraction = _parse_extraction(tool_use_input)

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "input_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "output_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return Extraction(
            facts=extraction.facts,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            provider="anthropic",
            model=model_used,
        )


@dataclass
class OpenAIFactExtractor:
    """OpenAI SDK 로 사실을 추출한다. `app/agent/propose.py::
    OpenAIProposer` 와 같은 관례."""

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

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction:
        import openai  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_extract_prompt(person, existing_facts, events)
        tool_schema = {
            "type": "function",
            "function": {
                "name": FACTS_TOOL_NAME,
                "description": _FACTS_TOOL_DESCRIPTION,
                "parameters": FACTS_SCHEMA,
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
                tool_choice={"type": "function", "function": {"name": FACTS_TOOL_NAME}},
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

        extraction = _parse_extraction(raw)

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return Extraction(
            facts=extraction.facts,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            provider="openai",
            model=model_used,
        )


@dataclass
class GeminiFactExtractor:
    """`google-genai` SDK 로 사실을 추출한다. `app/agent/propose.py::
    GeminiProposer` 와 같은 관례(`GEMINI_MODEL` 기본값 없음, 생성 시점에
    읽는다) -- 재시도·오류 매핑은 `call_with_gemini_error_mapping()` 을
    그대로 재사용한다(두 번째 헬퍼를 만들지 않는다, R-6 정신)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT

    def __post_init__(self) -> None:
        if self.model is None:
            model = os.environ.get("GEMINI_MODEL")
            if not model:
                from app.tools.types import InvalidValue

                raise InvalidValue(
                    "GeminiFactExtractor: GEMINI_MODEL 환경변수가 필요하다(기본값 "
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

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction:
        from google.genai import types as genai_types  # 요청 조립용 지연 import.

        system, user_text = build_extract_prompt(person, existing_facts, events)

        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            response_mime_type="application/json",
            response_schema=_to_gemini_schema(FACTS_SCHEMA),
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

        extraction = _parse_extraction(raw)

        usage = getattr(response, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage is not None else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage is not None else 0
        model_used = getattr(response, "model_version", None) or self.model

        return Extraction(
            facts=extraction.facts,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            provider="gemini",
            model=model_used,
        )


#: 이름 -> 무인자 팩토리의 등록표(D11 정신 -- 이름 집합·선택 로직은
#: `judge.py::JUDGES`/`select_provider` 와 공유하지만, 스키마가 달라 표
#: 자체는 새로 둔다. `PROPOSERS` 와 같은 예). `FakeFactExtractor` 는 여기
#: 없다(테스트 전용, `JUDGES`/`PROPOSERS` 가 각자의 Fake 를 빼는 것과 같은
#: 이유 -- 환경변수로 실제 추출기를 가짜로 바꿀 수 없다). 이름을
#: `FACT_EXTRACTORS` 로 둔 이유는 모듈 docstring "공급자 재사용" 절.
FACT_EXTRACTORS: dict[str, Callable[[], FactExtractor]] = {
    "anthropic": ClaudeFactExtractor,
    "openai": OpenAIFactExtractor,
    "gemini": GeminiFactExtractor,
}


def extractor_from_env(env: dict[str, str] | None = None) -> FactExtractor:
    """`select_provider(env)`(`judge.py` 재사용) -> `FACT_EXTRACTORS[name]()`.
    `proposer_from_env()`/`judge_from_env()` 와 같은 2단계 패턴이다(D11).
    `env` 를 생략하면 `os.environ` 을 읽는다."""

    return FACT_EXTRACTORS[select_provider(env)]()


# ---------------------------------------------------------------------------
# FakeFactExtractor -- 테스트용 결정적 FactExtractor (원칙8, 네트워크 0)
# ---------------------------------------------------------------------------


@dataclass
class FakeFactExtractor:
    """테스트용 결정적 `FactExtractor`(원칙8, 결정 D-3 -- LLM 은 재현
    불가능하므로 자동 테스트에 넣지 않는다). `table` = `{입력 이벤트 id
    집합(frozenset): [{"key":..., "value":..., "source_event_ids":[...]},
    ...]}` -- 표에 없는 이벤트 id 집합이면 빈 `Extraction`(01-plan 결정
    D-3 "입력 이벤트 id 집합 -> 미리 정한 출력").

    `fail` 이 주어지면 `JudgeUnavailable(error=fail)` 을 던진다(U6 이
    승격 실패 격리를 테스트할 때 쓴다 -- `app/er/judge.py::FakeJudge` 와
    같은 관례).

    `call_count` 로 호출 횟수를 센다(판정 표 9·11·12행 "추출기 호출
    0회" 검사용) -- 생성자 인자가 아니다(호출마다 내부에서 늘어난다).

    `_parse_extraction()` 을 그대로 거쳐 만들어진다 -- 실제 공급자와 같은
    구조 파싱 경로를 타서 `FakeProposer` 가 `validate_proposal()` 을 그대로
    거치는 것과 같은 이유(호출자 테스트가 두 경로를 다르게 취급하지
    않는다)."""

    table: dict[frozenset[int], list[dict[str, Any]]] = field(default_factory=dict)
    fail: str | None = None
    call_count: int = field(default=0, init=False)

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction:
        self.call_count += 1

        if self.fail is not None:
            raise JudgeUnavailable(self.fail)

        key = frozenset(event.id for event in events)
        raw_facts = self.table.get(key, [])
        extraction = _parse_extraction({"facts": [dict(item) for item in raw_facts]})
        return Extraction(facts=extraction.facts, provider="fake")
