"""Refs: P6-memory S3.5 D14 원칙6 원칙9 -- 골격(U1), 재export 전용.

U2~U6 이 채울 진입점(`after_record()`·`detect_patterns()`·
`promote_person()`, `app/memory/patterns.py`·`extract.py`·`promote.py`)은
**아직 만들지 않는다** -- 이 파일은 `app.memory.types` 의 결과 타입·
trace 어휘·`FACT_KEYS` 만 재export한다. 아직 없는 모듈을 import 하지
않으므로 `python -c "import app.memory"` 가 U1 시점에도 성공한다(01-plan
U1 항목의 판정 명령 중 하나).
"""

from __future__ import annotations

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
]
