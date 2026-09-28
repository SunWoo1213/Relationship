"""Refs: P6-memory D14 CR-002 S3.5 원칙9 -- U1 골격 상수 테스트(`-k constants`).

패턴 감지 로직(`detect_patterns()`, U2)은 아직 없다 -- 이 파일은 U1 이
만든 것만 검증한다: `app.settings.pattern_config()`/`promote_min_events()`
읽기 함수(기본값·환경변수 오버라이드·잘못된 값 거부)와 `app.memory.types`
의 trace 어휘 상수·`FACT_KEYS`. DB 를 쓰지 않는다(`dbtest` 마커 없음,
`db_session` 픽스처를 쓰지 않음) -- `tests/conftest.py` 의 "dbtest 마커는
실제로 픽스처를 쓰는 테스트에만 붙인다" 관례를 따른다.

패턴 규칙 자체의 경계값·창·인물 분리 등은 U2 몫(`test_memory_patterns.py`
에 이어서 추가된다 -- 01-plan U2 항목 판정: `pytest tests/test_memory_
patterns.py -v`, 이 파일 전체를 돌린다).
"""

from __future__ import annotations

import pytest

import app.settings as settings
from app.memory.types import (
    FACT_KEYS,
    MEMORY_TRACE_STEPS,
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_ERROR,
    STEP_MEMORY_PATTERN,
    STEP_MEMORY_PROMOTE,
)
from app.tools.types import InvalidValue

# ---------------------------------------------------------------------------
# pattern_config() / promote_min_events() -- 기본값 (환경변수 미설정)
# ---------------------------------------------------------------------------


def test_pattern_config_constants_defaults_when_env_missing() -> None:
    config = settings.pattern_config({})
    assert config.window_days == 365
    assert config.min_count == 3


def test_promote_min_events_constants_default_when_env_missing() -> None:
    assert settings.promote_min_events({}) == 5


# ---------------------------------------------------------------------------
# 빈 문자열 -- 기본값 (미설정과 같게 취급)
# ---------------------------------------------------------------------------


def test_pattern_config_constants_defaults_when_env_empty_string() -> None:
    config = settings.pattern_config({"PATTERN_WINDOW_DAYS": "", "PATTERN_MIN_COUNT": ""})
    assert config.window_days == 365
    assert config.min_count == 3


def test_promote_min_events_constants_default_when_env_empty_string() -> None:
    assert settings.promote_min_events({"MEMORY_PROMOTE_MIN_EVENTS": ""}) == 5


# ---------------------------------------------------------------------------
# 환경변수 덮어쓰기
# ---------------------------------------------------------------------------


def test_pattern_config_constants_reads_overrides_from_env() -> None:
    config = settings.pattern_config({"PATTERN_WINDOW_DAYS": "90", "PATTERN_MIN_COUNT": "2"})
    assert config.window_days == 90
    assert config.min_count == 2


def test_promote_min_events_constants_reads_override_from_env() -> None:
    assert settings.promote_min_events({"MEMORY_PROMOTE_MIN_EVENTS": "7"}) == 7


def test_pattern_config_constants_uses_os_environ_when_env_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PATTERN_WINDOW_DAYS", "120")
    monkeypatch.setenv("PATTERN_MIN_COUNT", "4")
    config = settings.pattern_config()
    assert config.window_days == 120
    assert config.min_count == 4


def test_promote_min_events_constants_uses_os_environ_when_env_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MEMORY_PROMOTE_MIN_EVENTS", "9")
    assert settings.promote_min_events() == 9


# ---------------------------------------------------------------------------
# 잘못된 값 -- 0 · 음수 · 비정수 문자열("abc") · 실수 문자열("3.5") 은
# 전부 InvalidValue (D14 "양의 정수만")
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["0", "-1", "abc", "3.5"])
def test_pattern_config_constants_window_days_invalid_raises(raw: str) -> None:
    with pytest.raises(InvalidValue):
        settings.pattern_config({"PATTERN_WINDOW_DAYS": raw})


@pytest.mark.parametrize("raw", ["0", "-1", "abc", "3.5"])
def test_pattern_config_constants_min_count_invalid_raises(raw: str) -> None:
    with pytest.raises(InvalidValue):
        settings.pattern_config({"PATTERN_MIN_COUNT": raw})


@pytest.mark.parametrize("raw", ["0", "-1", "abc", "3.5"])
def test_promote_min_events_constants_invalid_raises(raw: str) -> None:
    with pytest.raises(InvalidValue):
        settings.promote_min_events({"MEMORY_PROMOTE_MIN_EVENTS": raw})


# ---------------------------------------------------------------------------
# 코드 상수 3종 (환경변수 없음, 01-plan 결정 D-4·D-7)
# ---------------------------------------------------------------------------


def test_memory_code_constants_values() -> None:
    assert settings.PATTERN_KEY_PREFIX == "pattern:"
    assert settings.MEMORY_PROMOTE_MAX_EVENTS == 20
    assert settings.MEMORY_MAX_FACTS == 8


# ---------------------------------------------------------------------------
# agent_traces 어휘 상수 (결정 F -- tool_name 고정 + step 3종)
# ---------------------------------------------------------------------------


def test_memory_trace_vocab_constants_values() -> None:
    assert MEMORY_TRACE_TOOL_NAME == "memory"
    assert STEP_MEMORY_PATTERN == "memory_pattern"
    assert STEP_MEMORY_PROMOTE == "memory_promote"
    assert STEP_MEMORY_ERROR == "memory_error"
    # 정상 진행 step 2종(패턴 -> 승격, 결정 C-1) -- 오류 전용 step 은
    # 포함하지 않는다(app.agent.types.LOOP_TRACE_STEPS 와 같은 관례).
    assert MEMORY_TRACE_STEPS == (STEP_MEMORY_PATTERN, STEP_MEMORY_PROMOTE)
    assert STEP_MEMORY_ERROR not in MEMORY_TRACE_STEPS


# ---------------------------------------------------------------------------
# FACT_KEYS -- 고정 어휘 9종, pattern: 접두 키가 없다 (01-plan 결정 D-5·D-7)
# ---------------------------------------------------------------------------


def test_fact_keys_constants_has_no_pattern_prefixed_key() -> None:
    assert len(FACT_KEYS) == 9
    assert len(set(FACT_KEYS)) == len(FACT_KEYS)  # 중복 없음
    assert all(not key.startswith(settings.PATTERN_KEY_PREFIX) for key in FACT_KEYS)
