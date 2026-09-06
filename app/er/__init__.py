"""app/er -- 엔티티 해석 4단계 파이프라인 패키지 (P3-er, 01-plan 결정1).

`.claude/skills/entity-resolution` 의 절차(후보 검색 → 규칙 필터 → LLM
판정 → 확신도 분기)를 모듈 4개로 그대로 옮긴다 -- 한 파일에서 LLM 을
한 번만 부르고 끝내는 지름길을 구조로 막는다(원칙4).

U6(`app/er/pipeline.py`)이 `resolve()` 를, U7 이 `apply_resolution()` 을
재export 한다(결정4 -- 판정과 실행 분리, 둘 다 이 패키지의 공개 API).
"""

from __future__ import annotations

from app.er.judge import FakeJudge, Judge, judge_from_env
from app.er.pipeline import apply_resolution, resolve
from app.er.types import (
    ER_TRACE_STEP,
    ER_TRACE_TOOL_NAME,
    ER_VERSION,
    AlreadyApplied,
    AppliedResolution,
    ERConfig,
    JudgeUnavailable,
    Resolution,
)

__all__ = [
    "resolve",
    "apply_resolution",
    "Judge",
    "FakeJudge",
    "judge_from_env",
    "Resolution",
    "AppliedResolution",
    "AlreadyApplied",
    "ERConfig",
    "JudgeUnavailable",
    "ER_TRACE_STEP",
    "ER_TRACE_TOOL_NAME",
    "ER_VERSION",
]
