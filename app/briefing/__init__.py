"""Refs: P6-briefing S3.6 R12 원칙9 -- U1~U2 골격: 패키지 진입점 재export.

이 시점에 재export 할 이름은 `app/briefing/types.py` 의 결과 타입·trace
어휘·금지 표현 목록·`Notifier`/`NullNotifier`(U1), `app/briefing/select.py`
의 `select_due_schedules`(U2), `app/briefing/inputs.py` 의
`build_briefing_input`(U3)다. `BriefingComposer`/`FakeBriefingComposer`/
`template_briefing`(U4)·`run_briefings`(U5) 는 각 단위가 만든 뒤 이
파일에 재export 줄을 더한다(01-plan 산출물 절 "app/briefing/__init__.py
-- 진입점 재export(`run_briefings`·`select_due_schedules`·생성기
Protocol·가짜·`NullNotifier`·trace 상수)").
"""

from __future__ import annotations

from app.briefing.inputs import build_briefing_input
from app.briefing.select import select_due_schedules
from app.briefing.types import (
    BRIEFING_FORBIDDEN_EXPRESSIONS,
    BRIEFING_TRACE_STEPS,
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
    BriefingInput,
    BriefingLine,
    BriefingRunResult,
    ComposedBriefing,
    NullNotifier,
    Notifier,
    Suggestion,
)

__all__ = [
    "BRIEFING_FORBIDDEN_EXPRESSIONS",
    "BRIEFING_TRACE_STEPS",
    "BRIEFING_TRACE_TOOL_NAME",
    "STEP_BRIEFING_COMPOSE",
    "STEP_BRIEFING_ERROR",
    "STEP_BRIEFING_RUN",
    "BriefingInput",
    "BriefingLine",
    "BriefingRunResult",
    "ComposedBriefing",
    "NullNotifier",
    "Notifier",
    "Suggestion",
    "build_briefing_input",
    "select_due_schedules",
]
