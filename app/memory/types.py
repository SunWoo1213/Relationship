"""Refs: P6-memory S3.5 D14 D11 원칙6 원칙8 원칙9 -- 골격(U1). 결과 타입 +
trace 어휘 상수 + 사실 키 어휘만 정의한다. 도는 로직은 없다.

## 이 모듈이 하지 않는 것

- 패턴 감지·승격 로직을 담지 않는다(`app/memory/patterns.py`·`extract.py`·
  `promote.py` 는 각각 U2·U4·U5 몫, 01-plan "산출물" 절).
- DB·LLM·임베딩을 import 하지 않는다 -- 이 모듈은 순수 데이터클래스·상수
  뿐이다(원칙6 "패턴 판정에 LLM 을 쓰지 않는다"를 값 형식에서도 지킨다).

## 이 모듈이 고정하는 것

- `PatternResult`/`PatternChange` -- `detect_patterns(ctx, person_id)`
  (U2)의 반환 모양. `person_facts(key="pattern:{type}")` upsert 판정을
  사람이 읽을 수 있는 변경 목록으로 담는다(D14 "코드에서 지켜야 할 것" --
  실제로 쓴 `window_days`/`min_count` 를 여기 실어 `memory_pattern`
  trace(결정 F)에 그대로 옮긴다).
- `ExtractedFact`/`Extraction` -- `FactExtractor.extract(...)`(U4)의
  구조화 출력 모양(01-plan 결정 D-2: `{facts: [{key, value,
  source_event_ids}]}`). 검증 전 **원본** LLM 출력을 담는다 -- 어휘·이벤트
  id 검증은 `app/memory/extract.py::validate_extraction()`(U4) 몫이다.
- `PromotedFact`/`RejectedFact`/`PromotionResult` -- `promote_person(ctx,
  person_id, extractor)`(U5)의 반환 모양이자 `memory_promote` trace
  output(결정 F)의 바탕이다.
- `MEMORY_TRACE_TOOL_NAME`("memory")·step 3종(`memory_pattern`/
  `memory_promote`/`memory_error`, 결정 F) -- `agent_traces.tool_name`/
  `.step` 의 단일 출처. `app.agent.types.LOOP_TRACE_TOOL_NAME`("agent")·
  `app.er.types.ER_TRACE_TOOL_NAME`("er") 와 같은 층위이고 겹치지 않는다.
- `FACT_KEYS` -- 승격이 만드는 시맨틱 사실의 고정 키 어휘 9종(01-plan
  결정 D-5). 인물 간(A-B) 관계 키는 없다(원칙7). `pattern:` 로 시작하는
  키는 이 어휘에 없다 -- 패턴 사실은 승격 추출기가 아니라
  `app/memory/patterns.py` 가 ORM 으로 직접 쓴다(결정 D-7, U3 이 `update_
  person` 경로를 막는다).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# 패턴 감지 결과 (U2 `detect_patterns()` 가 반환. 로직은 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PatternChange:
    """`pattern:{type}` 사실 한 건의 이번 판정 변경 내역(결정 C-5, 결정 F
    `memory_pattern.output.changes[]`). `action` 어휘는 `created`/
    `updated`/`deleted`/`unchanged` 4종(U2 가 값을 채운다 -- 이 모듈은
    문자열 자유형으로만 담고 enum 을 강제하지 않는다)."""

    type: str
    action: str
    fact_id: int | None
    event_ids: list[int] = field(default_factory=list)
    previous_value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """`memory_pattern` trace `output.changes[]` 항목 모양(결정 F).
        `@traced`(`app.tools.context.to_jsonable`)가 이 메서드를 우선
        쓴다 -- `PatternResult.to_dict()` 가 재귀 호출한다(U2)."""

        return {
            "type": self.type,
            "action": self.action,
            "fact_id": self.fact_id,
            "event_ids": list(self.event_ids),
            "previous_value": self.previous_value,
        }


@dataclass(frozen=True)
class PatternResult:
    """`detect_patterns(ctx, person_id)`(U2)의 반환 타입. `window_days`/
    `min_count` 는 그 판정에 **실제로 쓴** `pattern_config()` 값이다(D14
    "실제 쓴 기간·횟수를 패턴 trace 에 기록" -- 설정을 바꾼 뒤에도 과거
    판정을 재현할 수 있게, 원칙8·9). `counts` 는 창 안 `events.type` 별
    개수(결정 C-6 -- 그 인물의 7종 전부를 한 번에 다시 센다)."""

    person_id: int
    window_from: datetime
    window_to: datetime
    window_days: int
    min_count: int
    counts: dict[str, int] = field(default_factory=dict)
    changes: list[PatternChange] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """`memory_pattern` trace `output` 모양 그대로(결정 F, U2 가
        `app/memory/patterns.py::detect_patterns()` 에서 채운다).
        `window_from`/`window_to` 는 `window.from`/`window.to` 로
        `isoformat()` 문자열이 된다 -- `app.tools.context.to_jsonable` 이
        `@traced` 로 감싼 함수의 반환값에서 이 메서드를 우선 호출한다."""

        return {
            "person_id": self.person_id,
            "window": {
                "from": self.window_from.isoformat(),
                "to": self.window_to.isoformat(),
            },
            "window_days": self.window_days,
            "min_count": self.min_count,
            "counts": dict(self.counts),
            "changes": [change.to_dict() for change in self.changes],
        }


# ---------------------------------------------------------------------------
# LLM 사실 추출 (U4 `FactExtractor.extract()` 가 반환. 로직은 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractedFact:
    """LLM 구조화 출력의 사실 한 건, **검증 전 원본**(01-plan 결정 D-2).
    `key` 가 `FACT_KEYS` 안에 있는지·`source_event_ids` 가 입력 이벤트
    id 안에 있는지는 `app/memory/extract.py::validate_extraction()`(U4)
    이 검사한다 -- 이 타입 자체는 검증하지 않는다."""

    key: str
    value: str
    source_event_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class Extraction:
    """`FactExtractor.extract(person, existing_facts, events)`(U4)의
    반환 타입. `{facts: [...]}` 스키마 그대로(01-plan 결정 D-2)."""

    facts: list[ExtractedFact] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 승격 결과 (U5 `promote_person()` 이 반환. 로직은 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromotedFact:
    """승격이 upsert 한 사실 한 건(결정 F `memory_promote.output.facts[]`).
    `action` 어휘는 `created`/`updated`/`same` 3종(결정 D-6)."""

    fact_id: int
    key: str
    action: str
    source_event_ids: list[int] = field(default_factory=list)
    previous_value: str | None = None


@dataclass(frozen=True)
class RejectedFact:
    """추출기가 낸 사실 후보 중 검증기가 거부한 것(결정 F
    `memory_promote.output.rejected[]`, 판정 표 14행). `index` 는 LLM
    출력 `facts[]` 안에서의 위치다."""

    index: int
    key: str | None
    reason: str


@dataclass(frozen=True)
class PromotionResult:
    """`promote_person(ctx, person_id, extractor)`(U5)의 반환 타입이자
    `memory_promote` trace output(결정 F)의 바탕. 트리거가 걸리지 않았으면
    (미승격 < `promote_min_events()`) `promote_person` 은 `None` 을
    돌려준다(01-plan 시그니처 `PromotionResult | None`) -- 이 경우 이
    타입은 만들어지지 않는다."""

    person_id: int
    unpromoted_count: int
    considered_event_ids: list[int] = field(default_factory=list)
    facts: list[PromotedFact] = field(default_factory=list)
    rejected: list[RejectedFact] = field(default_factory=list)
    llm_provider: str | None = None
    llm_model: str | None = None


# ---------------------------------------------------------------------------
# agent_traces 어휘 (결정 F -- tool_name 고정 + step 3종)
# ---------------------------------------------------------------------------

#: `agent_traces.tool_name` -- 메모리 계층(패턴·승격)이 남기는 모든 행의
#: 값(결정 F). `app.agent.types.LOOP_TRACE_TOOL_NAME`("agent")·
#: `app.er.types.ER_TRACE_TOOL_NAME`("er") 와 같은 층위이며 겹치지 않는다.
MEMORY_TRACE_TOOL_NAME = "memory"

#: 패턴 감지 단계 -- 이벤트가 저장된 인물마다 1행(결정 C-1, U2). tokens
#: 는 항상 0(LLM 미사용, 원칙6).
STEP_MEMORY_PATTERN = "memory_pattern"

#: 승격 단계 -- 트리거가 걸렸을 때만 1행(U5). tokens in/out 은 추출기
#: 사용량.
STEP_MEMORY_PROMOTE = "memory_promote"

#: 오류 전용 -- 승격·패턴 중 삼킨 예외 1행(U6, 세이브포인트 롤백 뒤
#: 바깥 트랜잭션에서 기록). 정상 진행 step 이 아니므로 아래
#: `MEMORY_TRACE_STEPS` 에는 포함하지 않는다(`app.agent.types.
#: STEP_LOOP_ERROR` 와 같은 관례).
STEP_MEMORY_ERROR = "memory_error"

#: 정상 진행 step 2종(고정 순서 -- 결정 C-1 "패턴 → 승격").
MEMORY_TRACE_STEPS: tuple[str, ...] = (STEP_MEMORY_PATTERN, STEP_MEMORY_PROMOTE)

# ---------------------------------------------------------------------------
# 사실 키 어휘 (01-plan 결정 D-5 -- 고정 집합, 인물 간 관계 키는 없다)
# ---------------------------------------------------------------------------

#: 승격(U5)이 만드는 시맨틱 사실의 고정 키 어휘. `job`(직업·직급)·
#: `workplace`(소속)·`family`(가족 사항)·`hobby`(취미·관심사)·
#: `likes`(좋아하는 것)·`dislikes`(싫어하는 것·피할 것)·`health`(건강·
#: 식이)·`life_event`(이사·결혼·출산 같은 근황)·`contact_note`(연락·만남
#: 습관) 9종. 인물 간(A-B) 관계 키는 두지 않는다(원칙7). `pattern:` 로
#: 시작하는 키는 여기 없다 -- 패턴 사실은 이 어휘가 아니라
#: `app/memory/patterns.py` 가 `PATTERN_KEY_PREFIX`(`app.settings`)로
#: 직접 만든다(결정 D-7).
FACT_KEYS: tuple[str, ...] = (
    "job",
    "workplace",
    "family",
    "hobby",
    "likes",
    "dislikes",
    "health",
    "life_event",
    "contact_note",
)
