"""Refs: P6-briefing S3.6 R12 원칙9 -- U1 골격: 패키지 진입점 재export.

이 시점에 재export 할 이름은 `app/briefing/types.py` 의 결과 타입·trace
어휘·금지 표현 목록·`Notifier`/`NullNotifier` 뿐이다. `select_due_
schedules`(U2)·`build_briefing_input`(U3)·`BriefingComposer`/
`FakeBriefingComposer`/`template_briefing`(U4)·`run_briefings`(U5) 는
각 단위가 만든 뒤 이 파일에 재export 줄을 더한다(01-plan 산출물 절
"app/briefing/__init__.py -- 진입점 재export(`run_briefings`·`select_
due_schedules`·생성기 Protocol·가짜·`NullNotifier`·trace 상수)").
"""

from __future__ import annotations

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
]
