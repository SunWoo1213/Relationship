"""Refs: P9b-auth U5 D18 CR-006 S3.6 결정 U 원칙9 -- 브리핑 주기 작업이 사용자마다 돈다.

`default_run_once(now=...)` 를 롤백 세션 위에서 부른다(`session_scope` 를 같은 `db_session` 을
내주는 대역으로 바꾼다 -- 커밋하지 않으므로 변이 실행에도 안전하다). 시계는 `NOW` 로 고정해 창
경계를 값으로 단언한다. 생성기는 `FakeBriefingComposer`, 발송기는 `FakePushSender`(네트워크 0).

실 PostgreSQL 이 필요하다(`dbtest`).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from sqlalchemy import func, select, text

import app.briefing.run as run_module
import app.briefing.scheduler as scheduler_module
import app.push.notifier as notifier_module
import app.settings as settings_module
from app.briefing.compose import FakeBriefingComposer
from app.db.models import AgentTrace, Person, PushSubscription, Schedule
from app.push.types import STEP_PUSH_SEND, FakePushSender
from tests.auth_helpers import make_user
from tests.test_push_wiring import _generate_vapid_key_pair

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 11, 20, 9, 0, 0, tzinfo=timezone.utc)
A = "u5sched-a"
B = "u5sched-b"
C = "u5sched-c"


def _clock() -> datetime:
    return NOW


@contextmanager
def _same_session(db_session):
    yield db_session


@pytest.fixture()
def env(db_session, monkeypatch):
    monkeypatch.setattr(scheduler_module, "session_scope", lambda: _same_session(db_session))
    monkeypatch.setattr(scheduler_module, "composer_from_env", lambda: FakeBriefingComposer())
    for name in ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT"):
        monkeypatch.delenv(name, raising=False)
    return db_session


def _person(db, user_id: str, name: str = "민수") -> Person:
    make_user(db, user_id)  # 주기 작업이 `users` 를 조인한다(CR-009 U4) -- 동의한 계정 행을 둔다
    person = Person(user_id=user_id, display_name=name, relation_tag="친구", hierarchy="동")
    db.add(person)
    db.flush()
    return person


def _schedule(db, person: Person, at: datetime, title: str = "약속") -> Schedule:
    row = Schedule(person_id=person.id, title=title, scheduled_at=at)
    db.add(row)
    db.flush()
    return row


def _sub(db, user_id: str, endpoint: str) -> PushSubscription:
    row = PushSubscription(
        user_id=user_id, endpoint=endpoint, keys={"p256dh": "p", "auth": "a"}
    )
    db.add(row)
    db.flush()
    return row


def _run_count(db) -> int:
    db.flush()
    return db.execute(
        select(func.count()).select_from(AgentTrace).where(AgentTrace.step == "briefing_run")
    ).scalar_one()


def _spy(monkeypatch) -> list[dict[str, Any]]:
    """`scheduler.run_briefings` 를 호출 기록기로 -- 실제 실행은 하지 않는다."""
    calls: list[dict[str, Any]] = []

    def _record(ctx, **kwargs):
        calls.append({"user_id": ctx.user_id, "kwargs": kwargs})

    monkeypatch.setattr(scheduler_module, "run_briefings", _record)
    return calls


def _full_vapid(monkeypatch) -> FakePushSender:
    public_key, private_key = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    monkeypatch.setenv("VAPID_PRIVATE_KEY", private_key)
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:u5-users@example.com")
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    return sender


# ---------------------------------------------------------------------------
# 사용자마다 돈다
# ---------------------------------------------------------------------------


def test_one_run_briefs_both_users_schedules(env):
    sa = _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    sb = _schedule(env, _person(env, B), NOW + timedelta(hours=5))

    scheduler_module.default_run_once(now=_clock)

    env.refresh(sa)
    env.refresh(sb)
    assert sa.briefed_at == NOW
    assert sb.briefed_at == NOW


def test_each_user_gets_own_ctx_and_exactly_one_call(env, monkeypatch):
    _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    _schedule(env, _person(env, A, "둘째"), NOW + timedelta(hours=4))  # 같은 사용자 둘 -> 1회
    _schedule(env, _person(env, B), NOW + timedelta(hours=5))
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert sorted(c["user_id"] for c in calls) == [A, B]
    assert all(c["kwargs"]["trigger"] == "scheduler" for c in calls)


def test_out_of_window_and_already_briefed_schedules_are_not_processed(env, monkeypatch):
    _schedule(env, _person(env, A), NOW + timedelta(hours=30))  # 창 밖(미래)
    _schedule(env, _person(env, B), NOW - timedelta(hours=1))  # 이미 지남
    done = _schedule(env, _person(env, C), NOW + timedelta(hours=2))
    done.briefed_at = NOW - timedelta(minutes=5)  # 이미 브리핑됨
    env.flush()
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    # 대상이 없으므로 표식 ctx 한 번뿐 -- A·B·C 는 불리지 않는다
    assert [c["user_id"] for c in calls] == [""]


def test_window_boundaries_are_inclusive_at_lead_hours_and_exclude_one_minute_later(
    env, monkeypatch
):
    _schedule(env, _person(env, A), NOW + timedelta(hours=24))  # 정확히 창 끝 -> 포함
    _schedule(env, _person(env, B), NOW + timedelta(hours=24, minutes=1))  # 1분 뒤 -> 제외
    _schedule(env, _person(env, C), NOW)  # 정확히 지금 -> 포함(>=)
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert sorted(c["user_id"] for c in calls) == [A, C]


def test_window_comes_from_settings_at_call_time_for_both_list_and_run(env, monkeypatch):
    """V5-6 -- 상수를 바꾸면 목록 질의와 `run_briefings(lead_hours=)` 가 함께 따라간다."""
    monkeypatch.setattr(settings_module, "BRIEFING_LEAD_HOURS", 2)
    _schedule(env, _person(env, A), NOW + timedelta(hours=2))  # 포함
    _schedule(env, _person(env, B), NOW + timedelta(hours=3))  # 24h 리터럴이면 들어오지만 2h 에선 제외
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert [c["user_id"] for c in calls] == [A]
    assert calls[0]["kwargs"]["lead_hours"] == 2


def test_default_window_is_24_hours_passed_to_run_briefings(env, monkeypatch):
    _schedule(env, _person(env, A), NOW + timedelta(hours=1))
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert calls[0]["kwargs"]["lead_hours"] == 24


# ---------------------------------------------------------------------------
# 사용자 단위 예외 격리
# ---------------------------------------------------------------------------


def _failing_for(monkeypatch, bad_user: str, *, how: str) -> None:
    real = run_module.run_briefings

    def _wrapper(ctx, **kwargs):
        if ctx.user_id == bad_user:
            # 부분 쓰기 하나를 남긴 뒤 실패한다 -- 롤백돼야 한다
            ctx.session.add(
                AgentTrace(
                    session_id="u5-partial-write",
                    step="x",
                    tool_name="x",
                    input={},
                    output={},
                    tokens_in=0,
                    tokens_out=0,
                )
            )
            ctx.session.flush()
            if how == "db":
                ctx.session.execute(text("select 1/0"))
            raise RuntimeError("simulated failure")
        return real(ctx, **kwargs)

    monkeypatch.setattr(scheduler_module, "run_briefings", _wrapper)


@pytest.mark.parametrize("how", ["python", "db"])
def test_one_users_failure_does_not_block_other_user_and_rolls_back_partial_writes(
    env, monkeypatch, caplog, how
):
    sa = _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    sb = _schedule(env, _person(env, B), NOW + timedelta(hours=5))
    _failing_for(monkeypatch, A, how=how)
    # 테스트 DB 부트스트랩의 alembic `fileConfig` 가 기존 로거를 꺼 두므로 이 로거만 되살린다.
    monkeypatch.setattr(scheduler_module.logger, "disabled", False)

    with caplog.at_level(logging.ERROR, logger=scheduler_module.logger.name):
        scheduler_module.default_run_once(now=_clock)  # 예외가 밖으로 나오지 않는다

    env.refresh(sa)
    env.refresh(sb)
    assert sb.briefed_at == NOW  # 다른 사용자는 브리핑됨
    assert sa.briefed_at is None  # 실패한 사용자 것은 그대로
    partial = env.execute(
        select(func.count()).select_from(AgentTrace).where(AgentTrace.session_id == "u5-partial-write")
    ).scalar_one()
    assert partial == 0  # 부분 쓰기 롤백
    # 로그에는 사용자 id 만 -- 일정 제목·본문은 없다
    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert A in logged
    assert "약속" not in logged


# ---------------------------------------------------------------------------
# 알림기는 사용자별 구독으로만 보낸다
# ---------------------------------------------------------------------------


def test_notifier_sends_only_to_each_users_own_subscriptions(env, monkeypatch):
    sender = _full_vapid(monkeypatch)
    _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    _schedule(env, _person(env, B), NOW + timedelta(hours=5))
    _sub(env, A, "https://push.example.test/u5/a1")
    _sub(env, A, "https://push.example.test/u5/a2")
    _sub(env, B, "https://push.example.test/u5/b1")
    # 일정이 없는 사용자 C 의 구독 -- 어느 일정으로도 가지 않는다
    _sub(env, C, "https://push.example.test/u5/c1")

    scheduler_module.default_run_once(now=_clock)

    assert sorted(call["endpoint"] for call in sender.calls) == [
        "https://push.example.test/u5/a1",
        "https://push.example.test/u5/a2",
        "https://push.example.test/u5/b1",
    ]
    # 사용자별 알림기 -> push_send trace 가 사람(일정 소유자)마다 하나씩
    traces = env.execute(
        select(AgentTrace).where(AgentTrace.step == STEP_PUSH_SEND)
    ).scalars().all()
    assert len(traces) == 2


def test_other_users_subscription_is_not_used_for_a_users_schedule(env, monkeypatch):
    sender = _full_vapid(monkeypatch)
    sa = _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    _sub(env, B, "https://push.example.test/u5/only-b")  # A 에겐 구독이 없다

    scheduler_module.default_run_once(now=_clock)

    assert sender.calls == []
    env.refresh(sa)
    assert sa.briefed_at == NOW  # 브리핑은 됐지만 B 의 endpoint 로 가지 않았다


# ---------------------------------------------------------------------------
# 대상 0명 -- 표식 ctx 1회 (결정 U)
# ---------------------------------------------------------------------------


def test_zero_targets_calls_run_briefings_once_with_empty_marker_user(env, monkeypatch):
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert len(calls) == 1
    assert calls[0]["user_id"] == ""
    assert calls[0]["kwargs"]["trigger"] == "scheduler"


def test_zero_targets_leave_exactly_one_briefing_run_trace_in_old_format(env):
    before = _run_count(env)

    scheduler_module.default_run_once(now=_clock)

    assert _run_count(env) == before + 1
    row = env.execute(
        select(AgentTrace)
        .where(AgentTrace.step == "briefing_run")
        .order_by(AgentTrace.id.desc())
        .limit(1)
    ).scalar_one()
    assert row.session_id.startswith("briefing:")
    assert not row.session_id.startswith("briefing-scheduler:")
    assert set(row.output) >= {
        "trigger", "now", "window", "lead_hours", "selected", "skipped", "briefed", "errors"
    }
    assert row.output["trigger"] == "scheduler"
    assert row.output["selected"] == []
    assert row.output["lead_hours"] == 24


def test_one_or_more_targets_never_call_the_marker_ctx(env, monkeypatch):
    _schedule(env, _person(env, A), NOW + timedelta(hours=3))
    calls = _spy(monkeypatch)

    scheduler_module.default_run_once(now=_clock)

    assert [c["user_id"] for c in calls] == [A]
    assert "" not in [c["user_id"] for c in calls]
