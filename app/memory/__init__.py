"""Refs: P6-memory S3.5 D14 원칙6 원칙9 -- 재export 전용.

U1 은 `app.memory.types` 의 결과 타입·trace 어휘·`FACT_KEYS` 만 재export
했다. U2 는 `app/memory/patterns.py::detect_patterns()`(규칙 기반 패턴
감지, LLM·임베딩 미사용)를 여기에 더한다 -- `promote_person()`/
`after_record()`(U5·U6)는 아직 없다. `detect_patterns` re-export 를
더해도 `python -c "import app.memory"` 는 여전히 네트워크·LLM·임베딩
없이 성공한다(`app/memory/patterns.py` 가 `app.memory.extract`/
`app.er.judge`/`app.embedding` 을 직접 import 하지 않는다, 모듈
docstring 참고).
"""

from __future__ import annotations

from app.memory.patterns import detect_patterns
from app.memory.types import (
    FACT_KEYS,
    MEMORY_TRACE_STEPS,
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_ERROR,
    STEP_MEMORY_PATTERN,
    STEP_MEMORY_PROMOTE,
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
    "Extraction",
    "ExtractedFact",
    "PatternChange",
    "PatternResult",
    "PromotedFact",
    "PromotionResult",
    "RejectedFact",
    "detect_patterns",
]
