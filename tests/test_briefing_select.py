"""Refs: P6-briefing S3.6 R12 원칙8 원칙9 -- U1 골격 상수 테스트(`-k
constants`) + U2 `select_due_schedules()` 대상 선정 테스트.

앞쪽 절(`-k constants` 로 걸리는 것)은 U1 이 만든 것만 검증한다:
`app.settings` 의 브리핑 상수 3개(`BRIEFING_LEAD_HOURS`·
`BRIEFING_INTERVAL_SECONDS`·`BRIEFING_SUGGESTION_MAX_CHARS`)·주기 작업
스위치 읽기 함수(`briefing_scheduler_enabled()`, 기본 꺼짐·`1`/`true` 만
켜짐·그 밖 값은 `InvalidValue`)와 `app.briefing.types` 의 trace 어휘
상수·금지 표현 목록·`NullNotifier`. DB 를 쓰지 않는다(`dbtest` 마커
없음, `db_session` 픽스처를 쓰지 않음) -- `tests/test_memory_patterns.py`
의 "dbtest 마커는 실제로 픽스처를 쓰는 테스트에만 붙인다" 관례를
따른다.

뒤쪽 절(U2)은 `app.briefing.select.select_due_schedules(ctx, *,
lead_hours, schedule_id=None)` 의 창 경계·`briefed_at`·다른 사용자·
동시 실행을 검증한다(01-plan U2 항목, 판정 표 4~9행). U1 시점에는
아직 만들지 않는다.
"""

from __future__ import annotations

import pytest

import app.settings as settings
from app.briefing.types import (
    BRIEFING_FORBIDDEN_EXPRESSIONS,
    BRIEFING_TRACE_STEPS,
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
    ComposedBriefing,
    NullNotifier,
)
from app.tools.types import InvalidValue

# ---------------------------------------------------------------------------
# 코드 상수 3종 (환경변수 없음, 01-plan 결정 A·B·E)
# ---------------------------------------------------------------------------


def test_briefing_code_constants_values() -> None:
    assert settings.BRIEFING_LEAD_HOURS == 24
    assert settings.BRIEFING_INTERVAL_SECONDS == 60
    assert settings.BRIEFING_SUGGESTION_MAX_CHARS == 80


# ---------------------------------------------------------------------------
# briefing_scheduler_enabled() -- 기본값 (환경변수 미설정·빈 문자열)
# ---------------------------------------------------------------------------


def test_briefing_scheduler_enabled_constants_default_false_when_env_missing() -> None:
    assert settings.briefing_scheduler_enabled({}) is False


def test_briefing_scheduler_enabled_constants_default_false_when_env_empty_string() -> None:
    assert settings.briefing_scheduler_enabled({"BRIEFING_SCHEDULER_ENABLED": ""}) is False


# ---------------------------------------------------------------------------
# briefing_scheduler_enabled() -- "1"/"true" 만 켜짐
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["1", "true"])
def test_briefing_scheduler_enabled_constants_true_values(raw: str) -> None:
    assert settings.briefing_scheduler_enabled({"BRIEFING_SCHEDULER_ENABLED": raw}) is True


def test_briefing_scheduler_enabled_constants_uses_os_environ_when_env_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BRIEFING_SCHEDULER_ENABLED", "1")
    assert settings.briefing_scheduler_enabled() is True


# ---------------------------------------------------------------------------
# briefing_scheduler_enabled() -- 그 밖 값은 InvalidValue(조용히 꺼진
# 채로 되돌아가지 않는다, 원칙8)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["0", "yes", "no", "false", "TRUE", "True", " 1"])
def test_briefing_scheduler_enabled_constants_invalid_raises(raw: str) -> None:
    with pytest.raises(InvalidValue):
        settings.briefing_scheduler_enabled({"BRIEFING_SCHEDULER_ENABLED": raw})


# ---------------------------------------------------------------------------
# agent_traces 어휘 상수 (결정 I -- tool_name 고정 + step 3종)
# ---------------------------------------------------------------------------


def test_briefing_trace_vocab_constants_values() -> None:
    assert BRIEFING_TRACE_TOOL_NAME == "briefing"
    assert STEP_BRIEFING_RUN == "briefing_run"
    assert STEP_BRIEFING_COMPOSE == "briefing_compose"
    assert STEP_BRIEFING_ERROR == "briefing_error"
    # 정상 진행 step 2종(실행 -> 생성, 결정 I) -- 오류 전용 step 은
    # 포함하지 않는다(app.memory.types.MEMORY_TRACE_STEPS 와 같은 관례).
    assert BRIEFING_TRACE_STEPS == (STEP_BRIEFING_RUN, STEP_BRIEFING_COMPOSE)
    assert STEP_BRIEFING_ERROR not in BRIEFING_TRACE_STEPS


# ---------------------------------------------------------------------------
# 금지 표현 목록 (01-plan 결정 E(ii) 초안)
# ---------------------------------------------------------------------------


def test_briefing_forbidden_expressions_constants_values() -> None:
    # 01-plan 결정 E(ii) 초안 문장의 나열 순서 그대로(완전한 목록이 아님
    # -- 193행 한계, 값을 바꾸려면 코드를 고친다).
    assert BRIEFING_FORBIDDEN_EXPRESSIONS == (
        "기분",
        "감정",
        "위로",
        "고민",
        "상담",
        "스트레스",
        "마음이",
        "힘드",
        "우울",
        "속상",
        "서운",
    )
    assert len(set(BRIEFING_FORBIDDEN_EXPRESSIONS)) == len(BRIEFING_FORBIDDEN_EXPRESSIONS)


# ---------------------------------------------------------------------------
# Notifier 자리 (결정 J(i)) -- NullNotifier 는 아무것도 보내지 않는다
# ---------------------------------------------------------------------------


def test_null_notifier_constants_returns_not_configured_and_sends_nothing() -> None:
    notifier = NullNotifier()
    result = notifier.notify(schedule=None, composed=ComposedBriefing())
    assert result == "not_configured"


# ===========================================================================
# U2 -- select_due_schedules() (01-plan U2, 판정 표 4~9행)
# ===========================================================================

#: U1 시점에는 아직 `app/briefing/select.py` 가 없다 -- 이 절은 U2 가
#: 채운다(`tests/test_memory_patterns.py` 가 U1/U2 를 한 파일에 담은
#: 것과 같은 관례).
