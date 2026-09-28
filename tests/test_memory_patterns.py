"""Refs: P6-memory D14 CR-002 S3.5 R11 security§5 원칙6 원칙8 원칙9 --
U1 골격 상수 테스트(`-k constants`) + U2 `detect_patterns()` 규칙 테스트.

앞쪽 절(`-k constants` 로 걸리는 것)은 U1 이 만든 것만 검증한다:
`app.settings.pattern_config()`/`promote_min_events()` 읽기 함수(기본값·
환경변수 오버라이드·잘못된 값 거부)와 `app.memory.types` 의 trace 어휘
상수·`FACT_KEYS`. DB 를 쓰지 않는다(`dbtest` 마커 없음, `db_session`
픽스처를 쓰지 않음) -- `tests/conftest.py` 의 "dbtest 마커는 실제로
픽스처를 쓰는 테스트에만 붙인다" 관례를 따른다.

뒤쪽 절(U2)은 `app.memory.patterns.detect_patterns(ctx, person_id)` 의
경계값·창·인물/type 분리·갱신·미달 삭제·소유 확인·원문 불변·import
격리를 검증한다(01-plan U2 항목 판정 표 1~8·13행 + 소유 확인 1건 + import
목록 1건). 실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처
(`db_session`, `dbtest` 마커)를 쓴다.
"""

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

import app.settings as settings
from app.db.models import AgentTrace, Event, FactSource, Person, PersonFact
from app.memory.patterns import detect_patterns
from app.memory.types import (
    FACT_KEYS,
    MEMORY_TRACE_STEPS,
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_ERROR,
    STEP_MEMORY_PATTERN,
    STEP_MEMORY_PROMOTE,
)
from app.tools.context import ToolContext
from app.tools.types import InvalidValue, PersonNotFound

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


# ===========================================================================
# U2 -- detect_patterns() (01-plan U2, 판정 표 1~8·13행 + 소유 확인 + import)
# ===========================================================================

#: 이 절의 각 테스트는 `db_session` 을 실제로 쓰는 것만 `@pytest.mark.dbtest`
#: 를 붙인다(모듈 전체 `pytestmark` 를 쓰지 않는다 -- 파일 docstring
#: "dbtest 마커는 실제로 픽스처를 쓰는 테스트에만 붙인다" 관례, U1 이 이미
#: 위 상수 절에서 지킨 것과 같다). 마지막의 import 목록 테스트는 DB 를
#: 쓰지 않으므로 마커가 없다.

#: UTC 04:00 -- Asia/Seoul(+9) 로 변환해도 날짜가 넘어가지 않는 시각을 골라
#: 날짜 경계 혼선을 피한다(04:00 UTC -> 13:00 KST, 같은 달력 날짜).
_NOW = datetime(2026, 9, 20, 4, 0, 0, tzinfo=timezone.utc)
_KST = ZoneInfo("Asia/Seoul")


def _make_person(
    db_session,
    *,
    user_id: str = "local",
    display_name: str = "민수",
    relation_tag: str = "친구",
    hierarchy: str = "동",
) -> Person:
    person = Person(
        user_id=user_id,
        display_name=display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )
    db_session.add(person)
    db_session.flush()
    return person


def _ctx(
    db_session,
    *,
    session_id: str = "patterns-test",
    user_id: str = "local",
    now=lambda: _NOW,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


def _add_event(
    db_session,
    person: Person,
    *,
    event_type: str = "conflict",
    occurred_at: datetime,
    content: str = "내용",
) -> Event:
    event = Event(
        person_id=person.id,
        type=event_type,
        content=content,
        raw_utterance=f"raw: {content} ({occurred_at.isoformat()})",
        occurred_at=occurred_at,
    )
    db_session.add(event)
    db_session.flush()
    return event


def _kst_date(occurred_at: datetime) -> str:
    return occurred_at.astimezone(_KST).date().isoformat()


def _pattern_fact(db_session, person: Person, event_type: str) -> PersonFact | None:
    return (
        db_session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person.id)
            .where(PersonFact.key == f"{settings.PATTERN_KEY_PREFIX}{event_type}")
        )
        .scalars()
        .one_or_none()
    )


def _linked_event_ids(db_session, fact: PersonFact) -> set[int]:
    return set(
        db_session.execute(
            select(FactSource.event_id).where(FactSource.fact_id == fact.id)
        )
        .scalars()
        .all()
    )


def _pattern_traces(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.tool_name == MEMORY_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_MEMORY_PATTERN)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


# -- 1: 양성 -----------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_three_events_creates_pattern_fact(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    occurred = [
        _NOW - timedelta(days=80),
        _NOW - timedelta(days=40),
        _NOW - timedelta(days=5),
    ]
    for when in occurred:
        _add_event(db_session, person, event_type="conflict", occurred_at=when)

    result = detect_patterns(ctx, person.id)

    assert result.window_days == 365
    assert result.min_count == 3
    assert result.counts["conflict"] == 3

    fact = _pattern_fact(db_session, person, "conflict")
    assert fact is not None
    assert fact.confidence == 1.0
    expected_dates = ", ".join(_kst_date(w) for w in sorted(occurred))
    assert fact.value == f"3회 ({expected_dates})"
    assert len(_linked_event_ids(db_session, fact)) == 3

    trace_rows = _pattern_traces(db_session, ctx.session_id)
    assert len(trace_rows) == 1
    assert trace_rows[0].tokens_in == 0
    assert trace_rows[0].tokens_out == 0
    output = trace_rows[0].output
    assert output["window_days"] == 365
    assert output["min_count"] == 3
    assert any(c["type"] == "conflict" and c["action"] == "created" for c in output["changes"])


# -- 2: 경계(부정) -------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_two_events_no_pattern(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=10))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=5))

    result = detect_patterns(ctx, person.id)

    assert result.counts.get("conflict", 0) == 2
    assert _pattern_fact(db_session, person, "conflict") is None


# -- 3: 창 경계 + 환경변수 오버라이드 ------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_window_boundary_inclusive_default(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    # 정확히 now - 365일 -- 포함.
    _add_event(
        db_session,
        person,
        event_type="conflict",
        occurred_at=_NOW - timedelta(days=365),
    )
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=200))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=10))

    result = detect_patterns(ctx, person.id)

    assert result.counts["conflict"] == 3
    assert _pattern_fact(db_session, person, "conflict") is not None


@pytest.mark.dbtest
def test_detect_patterns_window_boundary_exclusive_one_second_early(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    # now - 365일 - 1초 -- 제외.
    _add_event(
        db_session,
        person,
        event_type="conflict",
        occurred_at=_NOW - timedelta(days=365, seconds=1),
    )
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=200))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=10))

    result = detect_patterns(ctx, person.id)

    assert result.counts.get("conflict", 0) == 2
    assert _pattern_fact(db_session, person, "conflict") is None


@pytest.mark.dbtest
def test_detect_patterns_window_boundary_moves_with_env_override(
    db_session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATTERN_WINDOW_DAYS", "90")
    monkeypatch.setenv("PATTERN_MIN_COUNT", "2")
    person = _make_person(db_session)
    ctx = _ctx(db_session, session_id="patterns-test-env-override")
    # 90일 창 기준 경계 안 -- 정확히 now - 90일.
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=90))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=10))

    result = detect_patterns(ctx, person.id)

    assert result.window_days == 90
    assert result.min_count == 2
    assert result.counts["conflict"] == 2

    fact = _pattern_fact(db_session, person, "conflict")
    assert fact is not None
    assert fact.value.startswith("2회 ")

    trace_rows = _pattern_traces(db_session, ctx.session_id)
    assert trace_rows[0].output["window_days"] == 90
    assert trace_rows[0].output["min_count"] == 2


# -- 4: 미래 제외 --------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_excludes_future_occurred_at(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=10))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=5))
    _add_event(db_session, person, event_type="conflict", occurred_at=_NOW + timedelta(days=1))

    result = detect_patterns(ctx, person.id)

    assert result.counts.get("conflict", 0) == 2
    assert _pattern_fact(db_session, person, "conflict") is None


# -- 5: 인물 분리(부정) ---------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_does_not_mix_persons(db_session) -> None:
    minsu = _make_person(db_session, display_name="민수")
    jihoon = _make_person(db_session, display_name="지훈")
    ctx_minsu = _ctx(db_session, session_id="patterns-test-minsu")
    ctx_jihoon = _ctx(db_session, session_id="patterns-test-jihoon")

    _add_event(db_session, minsu, event_type="conflict", occurred_at=_NOW - timedelta(days=10))
    _add_event(db_session, minsu, event_type="conflict", occurred_at=_NOW - timedelta(days=5))
    _add_event(db_session, jihoon, event_type="conflict", occurred_at=_NOW - timedelta(days=3))

    detect_patterns(ctx_minsu, minsu.id)
    detect_patterns(ctx_jihoon, jihoon.id)

    assert _pattern_fact(db_session, minsu, "conflict") is None
    assert _pattern_fact(db_session, jihoon, "conflict") is None


# -- 6: type 분리(부정) ---------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_does_not_mix_types(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    _add_event(db_session, person, event_type="meal", occurred_at=_NOW - timedelta(days=10))
    _add_event(db_session, person, event_type="meal", occurred_at=_NOW - timedelta(days=5))
    _add_event(db_session, person, event_type="meeting", occurred_at=_NOW - timedelta(days=3))

    result = detect_patterns(ctx, person.id)

    assert result.counts.get("meal", 0) == 2
    assert result.counts.get("meeting", 0) == 1
    assert _pattern_fact(db_session, person, "meal") is None
    assert _pattern_fact(db_session, person, "meeting") is None


# -- 7: 갱신 -------------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_updates_existing_fact_same_id_on_new_event(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    occurred = [
        _NOW - timedelta(days=80),
        _NOW - timedelta(days=40),
        _NOW - timedelta(days=5),
    ]
    for when in occurred:
        _add_event(db_session, person, event_type="conflict", occurred_at=when)
    detect_patterns(ctx, person.id)

    fact_before = _pattern_fact(db_session, person, "conflict")
    assert fact_before is not None
    fact_id_before = fact_before.id

    fourth = _NOW - timedelta(days=1)
    _add_event(db_session, person, event_type="conflict", occurred_at=fourth)
    detect_patterns(ctx, person.id)

    fact_after = _pattern_fact(db_session, person, "conflict")
    assert fact_after is not None
    assert fact_after.id == fact_id_before  # 행 id 불변
    expected_dates = ", ".join(_kst_date(w) for w in sorted([*occurred, fourth]))
    assert fact_after.value == f"4회 ({expected_dates})"
    assert len(_linked_event_ids(db_session, fact_after)) == 4


# -- 8: 미달 처리(삭제) ---------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_deletes_fact_when_count_falls_below_threshold(db_session) -> None:
    person = _make_person(db_session)
    events = [
        _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=350)),
        _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=200)),
        _add_event(db_session, person, event_type="conflict", occurred_at=_NOW - timedelta(days=50)),
    ]

    ctx_first = _ctx(db_session, session_id="patterns-test-decay-1", now=lambda: _NOW)
    detect_patterns(ctx_first, person.id)

    fact_before = _pattern_fact(db_session, person, "conflict")
    assert fact_before is not None
    previous_value = fact_before.value
    fact_id = fact_before.id

    # 시계를 20일 앞으로 옮긴다 -- 365일 창이 그만큼 밀려 가장 오래된
    # 이벤트(now-350일)가 창 밖(now2-365 = now+20-365 = now-345)으로 나간다.
    later_now = _NOW + timedelta(days=20)
    ctx_second = _ctx(db_session, session_id="patterns-test-decay-2", now=lambda: later_now)
    detect_patterns(ctx_second, person.id)

    assert _pattern_fact(db_session, person, "conflict") is None
    assert set(
        db_session.execute(
            select(FactSource.event_id).where(FactSource.fact_id == fact_id)
        )
        .scalars()
        .all()
    ) == set()

    trace_rows = _pattern_traces(db_session, ctx_second.session_id)
    assert len(trace_rows) == 1
    changes = trace_rows[0].output["changes"]
    deleted = [c for c in changes if c["type"] == "conflict" and c["action"] == "deleted"]
    assert len(deleted) == 1
    assert deleted[0]["previous_value"] == previous_value
    assert deleted[0]["fact_id"] == fact_id

    # 이벤트 행은 그대로다(원문 불변).
    remaining_ids = {e.id for e in events}
    still_there = (
        db_session.execute(select(Event.id).where(Event.id.in_(remaining_ids)))
        .scalars()
        .all()
    )
    assert set(still_there) == remaining_ids


# -- 13: 원문 불변 --------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_does_not_touch_event_rows(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    occurred = [
        _NOW - timedelta(days=80),
        _NOW - timedelta(days=40),
        _NOW - timedelta(days=5),
    ]
    events = [
        _add_event(db_session, person, event_type="conflict", occurred_at=when, content=f"내용{i}")
        for i, when in enumerate(occurred)
    ]

    before = {
        e.id: (e.content, e.raw_utterance, e.occurred_at) for e in events
    }
    before_count = db_session.execute(select(Event)).scalars().all()
    before_total = len(before_count)

    detect_patterns(ctx, person.id)
    # 갱신 경로도 함께 확인 -- 두 번째 호출(4번째 이벤트 추가 없이 재호출).
    detect_patterns(ctx, person.id)

    after = {
        e.id: (e.content, e.raw_utterance, e.occurred_at)
        for e in db_session.execute(select(Event).where(Event.id.in_(before.keys())))
        .scalars()
        .all()
    }
    assert after == before

    after_total = len(db_session.execute(select(Event)).scalars().all())
    assert after_total == before_total  # 이벤트 행 수 불변(삭제·추가 없음)


# -- 소유 확인(security §5) ----------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_other_users_person_raises_person_not_found(db_session) -> None:
    owner_person = _make_person(db_session, user_id="owner")
    _add_event(db_session, owner_person, event_type="conflict", occurred_at=_NOW - timedelta(days=1))
    ctx_intruder = _ctx(db_session, user_id="intruder")

    with pytest.raises(PersonNotFound):
        detect_patterns(ctx_intruder, owner_person.id)

    assert (
        db_session.execute(
            select(PersonFact).where(PersonFact.person_id == owner_person.id)
        )
        .scalars()
        .first()
        is None
    )


# -- import 목록(원칙6) ---------------------------------------------------------


def test_patterns_module_does_not_import_llm_or_embedding_modules() -> None:
    source_path = Path(__file__).resolve().parent.parent / "app" / "memory" / "patterns.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    forbidden = {"app.memory.extract", "app.er.judge", "app.embedding"}
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)

    assert imported_names & forbidden == set()
