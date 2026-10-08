"""Refs: P7-push S3.6 R12 원칙9 -- U5 판정: 수동·주기 두 경로가 알림기를
받는다(01-plan 판정 표 6~9행, 21행 + 02-plan-verify R-1).

## 무엇을 확인하나

- 수동 경로(`POST /briefings/run`): `app.api.deps.get_notifier` 를
  `dependency_overrides` 로 바꿔 끼운 가짜/실제 `WebPushNotifier` 가 **요청과
  같은 세션**을 받아(R-1) `push == "sent"`·`push_send` trace 1행·`briefed_at`
  기록까지 한 흐름으로 이어진다. 오버라이드를 하지 않은 **진짜**
  `get_notifier` 도 VAPID 일회용 키 env + 가짜 발송기 주입으로 끝까지 돈다.
- 주기 경로(`app.briefing.scheduler.default_run_once`): 실제로
  `notifier_from_env()` 결과를 `run_briefings(notifier=...)` 에 넘긴다 --
  키 전무 `NullNotifier` / 반쪽 `MisconfiguredNotifier` / 전부
  `WebPushNotifier`(같은 세션·같은 시계 `ctx.now`).
- 키 없는 환경은 두 경로 모두 예전과 똑같이 `push == "not_configured"`.
- 반쪽 키는 두 경로 모두 `misconfigured`(발송 0, `briefed_at` 기록).

## 네트워크 0 (결정 G, 판정 21행)

파일 전체에 `pywebpush.webpush` "불리면 실패" 픽스처를 autouse 로 건다.
발송은 `FakePushSender` 뿐이다. 테스트 VAPID 키는 매번 이 파일 안에서
그 자리에서 만든 일회용 키이고 값은 어디에도 출력하지 않는다(저장소에 키
문자열을 남기지 않는다). 시간은 수동 경로는 `get_now` 오버라이드, 주기
경로는 `ctx.now` 가 쓰는 실제 시계 기준 상대 시각(`now + 3h`)으로 고정한다
(주기 경로는 시계를 주입할 자리가 없다 -- 일정을 상대 시각으로 둔다).

실 PostgreSQL(`POSTGRES_PORT` 기본 5433, 테스트 DB `relationship_test`)이
필요하다(`dbtest`).
"""

from __future__ import annotations

import base64
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

import py_vapid
import pytest
import pywebpush
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.briefing.scheduler as scheduler_module
import app.push.notifier as notifier_module
from app.api.deps import get_briefing_composer, get_notifier, get_now, get_session
from app.briefing.compose import FakeBriefingComposer
from app.briefing.types import NullNotifier
from app.db.models import AgentTrace, Person, PushSubscription, Schedule
from app.main import create_app
from app.push.notifier import MisconfiguredNotifier, WebPushNotifier
from app.push.types import PUSH_TRACE_TOOL_NAME, STEP_PUSH_SEND, FakePushSender, VapidConfig
from app.settings import app_user_id

dbtest = pytest.mark.dbtest
pytestmark = dbtest

#: 수동 경로의 기준 "지금"(`get_now` 오버라이드).
NOW = datetime(2026, 10, 5, 10, 0, 0, tzinfo=timezone.utc)

_VAPID_NAMES = ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT")


class _PyWebPushPatchMarker(Exception):
    """판정 21행 표식 예외 -- 실제 발송 함수가 불렸다는 뜻."""


def _raise_patch_marker(**_kwargs: object) -> None:
    raise _PyWebPushPatchMarker("실제 발송 경로가 불렸다")


@pytest.fixture(autouse=True)
def _deny_real_webpush(monkeypatch):
    """결정 G·판정 21행 -- `pywebpush.webpush` 가 불리면 실패."""
    monkeypatch.setattr(pywebpush, "webpush", _raise_patch_marker)


@pytest.fixture(autouse=True)
def _clean_vapid_env(monkeypatch):
    """개발 셸의 VAPID env 가 새어 들어와도 결과가 달라지지 않게, 기본은 세
    이름 전부 없는 상태에서 시작한다(각 테스트가 필요한 만큼 다시 채운다)."""
    for name in _VAPID_NAMES:
        monkeypatch.delenv(name, raising=False)


def _generate_vapid_key_pair() -> tuple[str, str]:
    """일회용 VAPID 키 쌍을 그 자리에서 만든다(값은 반환만, 출력 안 함)."""
    vapid = py_vapid.Vapid()
    vapid.generate_keys()
    private_raw = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    private_b64 = base64.urlsafe_b64encode(private_raw).rstrip(b"=").decode()
    public_raw = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    public_b64 = base64.urlsafe_b64encode(public_raw).rstrip(b"=").decode()
    return public_b64, private_b64


def _set_full_vapid_env(monkeypatch) -> tuple[str, str]:
    public_key, private_key = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    monkeypatch.setenv("VAPID_PRIVATE_KEY", private_key)
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:u5-wiring@example.com")
    return public_key, private_key


def _make_person(db_session) -> Person:
    person = Person(
        user_id=app_user_id(), display_name="민수", relation_tag="친구", hierarchy="동"
    )
    db_session.add(person)
    db_session.flush()
    return person


def _make_schedule(db_session, person: Person, *, scheduled_at: datetime) -> Schedule:
    schedule = Schedule(person_id=person.id, title="저녁 약속", scheduled_at=scheduled_at)
    db_session.add(schedule)
    db_session.flush()
    return schedule


def _make_subscription(db_session, *, n: int) -> PushSubscription:
    row = PushSubscription(
        user_id=app_user_id(),
        endpoint=f"https://push.example.test/u5-wiring/{n}",
        keys={"p256dh": "p", "auth": "a"},
    )
    db_session.add(row)
    db_session.flush()
    return row


def _push_traces(db_session) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == PUSH_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_PUSH_SEND)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


@pytest.fixture()
def manual_client(db_session):
    """수동 경로용 `(app, client)`. `get_session` 은 롤백 세션, `get_now` 는
    `NOW`, 생성기는 `FakeBriefingComposer`. `get_notifier` 는 **오버라이드하지
    않는다** -- 각 테스트가 고른다."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    app.dependency_overrides[get_briefing_composer] = lambda: FakeBriefingComposer()
    return app, TestClient(app)


@contextmanager
def _scheduler_session(db_session):
    """`session_scope()` 대역 -- 롤백 픽스처 세션을 그대로 내준다(커밋은
    하지 않는다)."""
    yield db_session


@pytest.fixture()
def scheduler_env(db_session, monkeypatch):
    """`default_run_once()` 가 롤백 세션·가짜 생성기로 돌게 한다. 시계는
    `ctx.now`(실제 시계)라 일정은 호출 쪽이 `datetime.now(utc)+3h` 로 둔다."""
    monkeypatch.setattr(scheduler_module, "session_scope", lambda: _scheduler_session(db_session))
    monkeypatch.setattr(scheduler_module, "composer_from_env", lambda: FakeBriefingComposer())
    return db_session


# ---------------------------------------------------------------------------
# (b) 수동 경로 -- get_notifier 오버라이드(R-1: 요청과 같은 세션)
# ---------------------------------------------------------------------------


def test_manual_path_override_receives_same_session_and_sends(db_session, manual_client):
    """판정 6행 + R-1 -- 오버라이드 함수가 `Depends(get_session)` 을 선언해
    요청과 같은 세션을 받고, 구독 2건에 각각 1회 발송 -> `push == "sent"`,
    `push_send` trace 1행, `briefed_at == NOW`."""
    app, client = manual_client
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _make_subscription(db_session, n=1)
    _make_subscription(db_session, n=2)
    sender = FakePushSender()
    seen: dict[str, Any] = {}

    def _override(
        session: Session = Depends(get_session),
        now: Callable[[], datetime] = Depends(get_now),
    ) -> WebPushNotifier:
        seen["session"] = session
        seen["now"] = now
        vapid = VapidConfig(
            public_key="pub-placeholder", private_key="priv-placeholder", subject="mailto:x@y.z"
        )
        return WebPushNotifier(
            session=session, user_id=app_user_id(), sender=sender, vapid=vapid, now=now
        )

    app.dependency_overrides[get_notifier] = _override

    response = client.post("/briefings/run", json={"schedule_id": schedule.id})

    assert response.status_code == 200
    body = response.json()
    assert [item["push"] for item in body["briefings"]] == ["sent"]
    assert seen["session"] is db_session  # R-1 -- 요청과 같은 세션
    assert seen["now"]() == NOW  # get_now 와 같은 시계
    assert len(sender.calls) == 2  # 구독마다 1회
    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW
    traces = _push_traces(db_session)
    assert len(traces) == 1
    assert traces[0].output["status"] == "sent"


def test_manual_path_real_get_notifier_with_keys_sends_via_fake_sender(
    db_session, manual_client, monkeypatch
):
    """오버라이드 없이 **진짜** `get_notifier` -> `notifier_from_env` 경로:
    일회용 VAPID env + `PyWebPushSender` 자리에 `FakePushSender` 를 주입하면
    `push == "sent"` 까지 이어진다(실제 발송 라이브러리는 불리지 않는다)."""
    _app, client = manual_client
    _set_full_vapid_env(monkeypatch)
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _make_subscription(db_session, n=1)

    response = client.post("/briefings/run", json={"schedule_id": schedule.id})

    assert response.status_code == 200
    assert [item["push"] for item in response.json()["briefings"]] == ["sent"]
    assert len(sender.calls) == 1
    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW
    assert len(_push_traces(db_session)) == 1


# ---------------------------------------------------------------------------
# (a)(d) 수동 경로 -- 키 없음 / 반쪽
# ---------------------------------------------------------------------------


def test_manual_path_without_keys_is_not_configured(db_session, manual_client):
    """판정 8행 -- 키 전무: 기존 동작 그대로 `not_configured`, 발송 0,
    `push_send` trace 0행, `briefed_at` 기록."""
    _app, client = manual_client
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _make_subscription(db_session, n=1)

    response = client.post("/briefings/run", json={"schedule_id": schedule.id})

    assert response.status_code == 200
    assert [item["push"] for item in response.json()["briefings"]] == ["not_configured"]
    assert _push_traces(db_session) == []
    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW


def test_manual_path_half_keys_is_misconfigured(db_session, manual_client, monkeypatch):
    """판정 9행 -- 공개키만 있으면 `misconfigured`, 발송 0, `briefed_at`
    기록(조용히 꺼진 것처럼 보이지 않게)."""
    _app, client = manual_client
    public_key, _private = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _make_subscription(db_session, n=1)

    response = client.post("/briefings/run", json={"schedule_id": schedule.id})

    assert response.status_code == 200
    assert [item["push"] for item in response.json()["briefings"]] == ["misconfigured"]
    assert sender.calls == []
    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW


# ---------------------------------------------------------------------------
# (c) 주기 경로 -- default_run_once 가 notifier_from_env 결과를 넘긴다
# ---------------------------------------------------------------------------


def _spy_run_briefings(monkeypatch) -> dict[str, Any]:
    """`scheduler.run_briefings` 를 호출 인자 기록기로 바꾼다(판정 7행)."""
    captured: dict[str, Any] = {}

    def _spy(ctx, **kwargs):
        captured["ctx"] = ctx
        captured["kwargs"] = kwargs

    monkeypatch.setattr(scheduler_module, "run_briefings", _spy)
    return captured


def test_scheduler_passes_null_notifier_without_keys(scheduler_env, monkeypatch):
    captured = _spy_run_briefings(monkeypatch)

    scheduler_module.default_run_once()

    notifier = captured["kwargs"]["notifier"]
    assert isinstance(notifier, NullNotifier)
    assert captured["kwargs"]["trigger"] == "scheduler"


def test_scheduler_passes_misconfigured_notifier_with_half_keys(scheduler_env, monkeypatch):
    public_key, _private = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    captured = _spy_run_briefings(monkeypatch)

    scheduler_module.default_run_once()

    assert isinstance(captured["kwargs"]["notifier"], MisconfiguredNotifier)


def test_scheduler_passes_web_push_notifier_sharing_session_user_and_clock(
    scheduler_env, monkeypatch
):
    """키가 전부 있으면 `WebPushNotifier` 이고, 주기 작업의 세션·`user_id`·
    시계(`ctx.now`)와 같은 출처를 쓴다."""
    _set_full_vapid_env(monkeypatch)
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    captured = _spy_run_briefings(monkeypatch)

    scheduler_module.default_run_once()

    notifier = captured["kwargs"]["notifier"]
    ctx = captured["ctx"]
    assert isinstance(notifier, WebPushNotifier)
    assert notifier.session is ctx.session is scheduler_env
    assert notifier.user_id == ctx.user_id == app_user_id()
    assert notifier.now is ctx.now
    assert notifier.sender is sender


def test_scheduler_end_to_end_sends_and_records(scheduler_env, monkeypatch):
    """주기 경로를 끝까지 -- 일정 `now+3h`, 구독 1건, 일회용 키 + 가짜 발송기
    -> 발송 1회, `push_send` trace 1행, `briefed_at` 기록."""
    db_session = scheduler_env
    _set_full_vapid_env(monkeypatch)
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    person = _make_person(db_session)
    schedule = _make_schedule(
        db_session, person, scheduled_at=datetime.now(timezone.utc) + timedelta(hours=3)
    )
    _make_subscription(db_session, n=1)

    scheduler_module.default_run_once()

    assert len(sender.calls) == 1
    db_session.refresh(schedule)
    assert schedule.briefed_at is not None
    traces = _push_traces(db_session)
    assert len(traces) == 1
    assert traces[0].output["status"] == "sent"


def test_scheduler_end_to_end_without_keys_keeps_old_behavior(scheduler_env):
    """키 없음 -- 주기 경로도 기존 동작(`not_configured`): 발송·`push_send`
    trace 0, `briefed_at` 기록."""
    db_session = scheduler_env
    person = _make_person(db_session)
    schedule = _make_schedule(
        db_session, person, scheduled_at=datetime.now(timezone.utc) + timedelta(hours=3)
    )
    _make_subscription(db_session, n=1)

    scheduler_module.default_run_once()

    db_session.refresh(schedule)
    assert schedule.briefed_at is not None
    assert _push_traces(db_session) == []
