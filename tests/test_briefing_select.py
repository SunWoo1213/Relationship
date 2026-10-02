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

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, text
from sqlalchemy.orm import Session

import app.settings as settings
from app.briefing.select import select_due_schedules
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
from app.db.models import Person, Schedule
from app.tools.context import ToolContext
from app.tools.types import InvalidValue, ScheduleNotFound

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
#
# 아래 테스트는 전부 `db_session`(바깥 트랜잭션 + SAVEPOINT, 끝나면 항상
# rollback, `tests/conftest.py`)을 쓴다 -- `tests/test_tools_briefing.py`
# 와 같은 관례(`_make_person`/`_ctx` 헬퍼 이름도 맞춘다). 동시 실행
# (판정 9행)만 예외로 `db_engine` 커밋 픽스처를 따로 쓴다(권고 R-1,
# 아래 두 번째 절 참고) -- 커밋되지 않은 행은 다른 커넥션에 보이지
# 않아 잠금 경쟁을 재현할 수 없기 때문이다.

_T = datetime(2026, 10, 10, 19, 0, 0, tzinfo=timezone.utc)


def _make_person(
    db_session,
    *,
    user_id: str = "brief-u2-test-user",
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


def _make_schedule(
    db_session,
    person: Person,
    *,
    scheduled_at: datetime,
    briefed_at: datetime | None = None,
    title: str = "저녁 약속",
) -> Schedule:
    schedule = Schedule(
        person_id=person.id,
        title=title,
        scheduled_at=scheduled_at,
        briefed_at=briefed_at,
    )
    db_session.add(schedule)
    db_session.flush()
    return schedule


def _ctx(
    db_session,
    *,
    session_id: str = "briefing:select-test",
    user_id: str = "brief-u2-test-user",
    now=lambda: _T,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


# ---------------------------------------------------------------------------
# 판정 표 4~8행 -- 창 경계·briefed_at·다른 사용자
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_select_due_schedules_window_upper_boundary_inclusive(db_session) -> None:
    """판정 4행 -- 창 경계 양성: 일정 T+24h 정확히는 선정된다."""
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T + timedelta(hours=24))
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24)

    assert [row.id for row in result] == [schedule.id]


@pytest.mark.dbtest
def test_select_due_schedules_window_upper_boundary_exclusive(db_session) -> None:
    """판정 5행 -- 창 경계 부정: 일정 T+24h+1s 는 선정되지 않는다."""
    person = _make_person(db_session)
    _make_schedule(db_session, person, scheduled_at=_T + timedelta(hours=24, seconds=1))
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24)

    assert result == []


@pytest.mark.dbtest
def test_select_due_schedules_excludes_past_schedule(db_session) -> None:
    """판정 6행 -- 지난 일정(T-1s, briefed_at NULL)은 결정 B(i) 확정대로
    선정되지 않는다(S3.6 카드 보충 줄)."""
    person = _make_person(db_session)
    _make_schedule(db_session, person, scheduled_at=_T - timedelta(seconds=1))
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24)

    assert result == []


@pytest.mark.dbtest
def test_select_due_schedules_excludes_already_briefed(db_session) -> None:
    """판정 7행 -- briefed_at 이 채워진 T+3h 일정은 선정되지 않는다."""
    person = _make_person(db_session)
    _make_schedule(db_session, person, scheduled_at=_T + timedelta(hours=3), briefed_at=_T)
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24)

    assert result == []


@pytest.mark.dbtest
def test_select_due_schedules_excludes_other_user(db_session) -> None:
    """판정 8행(기본 모드) -- 다른 user_id 인물의 T+3h 일정은 선정되지
    않는다."""
    other_person = _make_person(db_session, user_id="brief-u2-other-user")
    _make_schedule(db_session, other_person, scheduled_at=_T + timedelta(hours=3))
    ctx = _ctx(db_session, user_id="brief-u2-test-user")

    result = select_due_schedules(ctx, lead_hours=24)

    assert result == []


@pytest.mark.dbtest
def test_select_due_schedules_schedule_id_other_user_raises_not_found(db_session) -> None:
    """판정 8행(지정 모드) -- 다른 user_id 소유 일정을 schedule_id 로
    지정하면 ScheduleNotFound(새 예외 클래스를 만들지 않는다)."""
    other_person = _make_person(db_session, user_id="brief-u2-other-user")
    other_schedule = _make_schedule(db_session, other_person, scheduled_at=_T + timedelta(hours=3))
    ctx = _ctx(db_session, user_id="brief-u2-test-user")

    with pytest.raises(ScheduleNotFound):
        select_due_schedules(ctx, lead_hours=24, schedule_id=other_schedule.id)


@pytest.mark.dbtest
def test_select_due_schedules_schedule_id_missing_raises_not_found(db_session) -> None:
    """존재하지 않는 schedule_id 도 ScheduleNotFound."""
    ctx = _ctx(db_session)

    with pytest.raises(ScheduleNotFound):
        select_due_schedules(ctx, lead_hours=24, schedule_id=999999)


# ---------------------------------------------------------------------------
# 그 밖 -- 정렬 순서, 지정 모드(결정 C)가 창 밖·이미 브리핑된 일정도
# 돌려주는 것
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_select_due_schedules_orders_by_scheduled_at_ascending(db_session) -> None:
    person = _make_person(db_session)
    later = _make_schedule(
        db_session, person, scheduled_at=_T + timedelta(hours=10), title="늦은 일정"
    )
    earlier = _make_schedule(
        db_session, person, scheduled_at=_T + timedelta(hours=1), title="이른 일정"
    )
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24)

    assert [row.id for row in result] == [earlier.id, later.id]


@pytest.mark.dbtest
def test_select_due_schedules_schedule_id_mode_ignores_window_and_briefed_at(
    db_session,
) -> None:
    """판정 10행(결정 C) -- schedule_id 지정 시 창 밖(T+10일)이고 이미
    briefed_at 이 채워진 일정도 그대로 돌려준다."""
    person = _make_person(db_session)
    schedule = _make_schedule(
        db_session,
        person,
        scheduled_at=_T + timedelta(days=10),
        briefed_at=_T,
    )
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24, schedule_id=schedule.id)

    assert [row.id for row in result] == [schedule.id]


@pytest.mark.dbtest
def test_select_due_schedules_schedule_id_mode_owned_within_window(db_session) -> None:
    """지정 모드의 양성 기본 경로 -- 소유한 일정이면 창 안이어도
    그대로 돌려준다."""
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T + timedelta(hours=3))
    ctx = _ctx(db_session)

    result = select_due_schedules(ctx, lead_hours=24, schedule_id=schedule.id)

    assert [row.id for row in result] == [schedule.id]


# ---------------------------------------------------------------------------
# 판정 9행 -- 동시 실행(SKIP LOCKED). 권고 R-1: db_session(바깥 트랜잭션+
# 롤백) 으로는 커밋되지 않은 행이 다른 커넥션에 보이지 않아 잠금 경쟁을
# 재현할 수 없다. 그래서 이 테스트만 db_engine 으로 직접 커밋하는 전용
# 데이터를 만들고, 끝에서 그 user_id 의 persons·schedules 행만 지운다
# (테이블 전체 삭제·TRUNCATE·DROP 금지).
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_select_due_schedules_concurrent_sessions_skip_locked(db_engine) -> None:
    """판정 9행 -- 세션(커넥션) 두 개가 같은 순간 고르면, 한 세션이 이미
    잠근 일정은 다른 세션의 결과에 나타나지 않는다(FOR UPDATE ... SKIP
    LOCKED). 일정을 2건 두어, A 가 schedule_id 지정 모드로 한 건만 잠근
    채 커밋하지 않고 있을 때 B 가 기본 모드로 고르면 **나머지 한 건만**
    가져가는 것까지 확인한다.

    동작 확인 방법(위임 프롬프트 6항): 이 테스트를 켜 둔 채 `select.py`
    의 두 `with_for_update(..., skip_locked=True)` 에서 `skip_locked=True`
    를 **일시적으로** 지우면 B 세션이 A 의 잠금을 기다리다 `lock_timeout`
    에 걸려 예외로 실패한다(증거 `evidence/*-u2-lock-negative.txt`). 원복
    후에는 통과한다(증거 `evidence/*-u2-select.txt`).
    """
    user_id = f"brief-u2-lock-{uuid.uuid4().hex}"

    setup_session = Session(bind=db_engine)
    try:
        person = Person(
            user_id=user_id, display_name="락테스트", relation_tag="친구", hierarchy="동"
        )
        setup_session.add(person)
        setup_session.flush()
        schedule_a = Schedule(
            person_id=person.id, title="A 일정", scheduled_at=_T + timedelta(hours=1)
        )
        schedule_b = Schedule(
            person_id=person.id, title="B 일정", scheduled_at=_T + timedelta(hours=2)
        )
        setup_session.add_all([schedule_a, schedule_b])
        setup_session.commit()
        person_id = person.id
        schedule_a_id = schedule_a.id
        schedule_b_id = schedule_b.id
    finally:
        setup_session.close()

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    try:
        session_a.begin()
        ctx_a = ToolContext(
            session=session_a, session_id="briefing:lock-a", user_id=user_id, now=lambda: _T
        )
        # A 가 schedule_a 하나만 잠그고 커밋하지 않은 채 트랜잭션을 열어 둔다.
        locked_by_a = select_due_schedules(ctx_a, lead_hours=24, schedule_id=schedule_a_id)
        assert [row.id for row in locked_by_a] == [schedule_a_id]

        session_b.begin()
        # B 가 A 의 잠금을 영원히 기다리지 않도록 짧은 lock_timeout 을 건다
        # (skip_locked 를 일시적으로 뺐을 때도 테스트가 멈추지 않게 하는
        # 안전장치 -- 위임 프롬프트 6항 괄호 안내).
        session_b.execute(text("SET LOCAL lock_timeout = '2s'"))
        ctx_b = ToolContext(
            session=session_b, session_id="briefing:lock-b", user_id=user_id, now=lambda: _T
        )
        result_b = select_due_schedules(ctx_b, lead_hours=24)

        assert [row.id for row in result_b] == [schedule_b_id]
        assert schedule_a_id not in {row.id for row in result_b}

        session_a.rollback()
        session_b.rollback()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()

        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(Schedule).where(Schedule.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.commit()

            remaining = cleanup.execute(
                text("SELECT count(*) FROM persons WHERE user_id = :user_id"),
                {"user_id": user_id},
            ).scalar_one()
            assert remaining == 0
        finally:
            cleanup.close()
