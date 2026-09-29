"""Refs: P6-memory S3.5 D14 D11 원칙6 원칙9 -- 재export 전용.

U1 은 `app.memory.types` 의 결과 타입·trace 어휘·`FACT_KEYS` 만 재export
했다. U2 는 `app/memory/patterns.py::detect_patterns()`(규칙 기반 패턴
감지, LLM·임베딩 미사용)를 여기에 더했다. U4 는 01-plan 41행대로
`app/memory/extract.py` 의 추출기 Protocol(`FactExtractor`)과 가짜
(`FakeFactExtractor`)를 더했다. U5 는 `app/memory/promote.py::
promote_person()`(LLM 사실 추출 + upsert 승격)을 더했다. U6 은
`app/memory/hooks.py::after_record()`(루프 연결 진입점, `app/agent/
loop.py::_record()` 가 이 함수를 부른다)를 더한다. U7 은 `app/memory/
direct_facts.py::link_direct_facts()`(루프가 직접 쓴 사실의 원문 연결,
결정 G(ii))를 더한다 -- `after_record()` 가 패턴·승격 뒤 같은
세이브포인트 안에서 부른다.

`detect_patterns` re-export 는 여전히 네트워크·LLM·임베딩 없이 성공한다
(`app/memory/patterns.py` 는 `app.memory.extract`/`app.er.judge`/
`app.embedding` 을 직접 import 하지 않는다, `patterns.py` 모듈 docstring
참고). `app.memory.extract`·`app.memory.promote`·`app.memory.hooks` 는
`app.er.judge` 를 import 하지만(D11 재사용, `select_provider`/
`call_with_error_mapping`), 실제 LLM 호출은 **함수를 부를 때**
(`ClaudeFactExtractor.__post_init__` 등) 지연 import 로 SDK 를 불러올
뿐이라 `import app.memory` 자체는 네트워크를 타지 않는다."""

from __future__ import annotations

from app.memory.direct_facts import link_direct_facts
from app.memory.extract import FactExtractor, FakeFactExtractor
from app.memory.hooks import after_record
from app.memory.patterns import detect_patterns
from app.memory.promote import promote_person
from app.memory.types import (
    FACT_KEYS,
    MEMORY_TRACE_STEPS,
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_ERROR,
    STEP_MEMORY_PATTERN,
    STEP_MEMORY_PROMOTE,
    DirectFactLink,
    DirectFactLinkResult,
    Extraction,
    ExtractedFact,
    PatternChange,
    PatternResult,
    PromotedFact,
    PromotionResult,
    RejectedFact,
)

__all__ = [
    "FACT_KEYS",
    "MEMORY_TRACE_STEPS",
    "MEMORY_TRACE_TOOL_NAME",
    "STEP_MEMORY_ERROR",
    "STEP_MEMORY_PATTERN",
    "STEP_MEMORY_PROMOTE",
    "DirectFactLink",
    "DirectFactLinkResult",
    "Extraction",
    "ExtractedFact",
    "FactExtractor",
    "FakeFactExtractor",
    "PatternChange",
    "PatternResult",
    "PromotedFact",
    "PromotionResult",
    "RejectedFact",
    "after_record",
    "detect_patterns",
    "link_direct_facts",
    "promote_person",
]
