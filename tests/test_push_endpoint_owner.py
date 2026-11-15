"""Refs: P9b-auth U5 D18 CR-006 결정 P S3.6 R12 -- 푸시 endpoint 는 마지막 구독 계정 하나, 로그아웃 시
그 브라우저 구독 떼기, 수동 브리핑 알림기는 로그인 계정으로 만든다(U3b R-2·R-6 닫기).

롤백 세션 위에서 돈다(커밋 0). 발송기는 `FakePushSender`(네트워크 0).

실 PostgreSQL 이 필요하다(`dbtest`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

import app.push.notifier as notifier_module
from app.api.deps import get_briefing_composer, get_notifier, get_now, get_session
from app.briefing.compose import FakeBriefingComposer
from app.db.models import Person, PushSubscription, Schedule
from app.main import create_app
from app.push.notifier import NullNotifier, WebPushNotifier
from app.push.types import FakePushSender
from tests.auth_helpers import logged_in_client, make_user
from tests.test_push_wiring import _generate_vapid_key_pair

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 11, 20, 9, 0, 0, tzinfo=timezone.utc)
A = "u5push-a"
B = "u5push-b"
EP = "https://push.example.test/u5/shared-endpoint"
OTHER_EP = "https://push.example.test/u5/other-endpoint"
KEYS = {"p256dh": "p256dh-test-value_ABC-123", "auth": "auth-test-value_XYZ-789"}


@pytest.fixture()
def env(db_session, monkeypatch):
    for name in ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT"):
        monkeypatch.delenv(name, raising=False)
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    app.dependency_overrides[get_briefing_composer] = lambda: FakeBriefingComposer()
    a = logged_in_client(app, db_session, A)
    b = logged_in_client(app, db_session, B)
    return app, a, b, db_session


def _subscribe(client, endpoint: str = EP):
    resp = client.post("/push/subscriptions", json={"endpoint": endpoint, "keys": KEYS})
    assert resp.status_code == 200
    return resp.json()


def _rows(db, endpoint: str | None = None) -> list[tuple[str, str]]:
    db.flush()
    stmt = select(PushSubscription.user_id, PushSubscription.endpoint)
    if endpoint is not None:
        stmt = stmt.where(PushSubscription.endpoint == endpoint)
    return sorted(db.execute(stmt).all())


def _full_vapid(monkeypatch) -> FakePushSender:
    public_key, private_key = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    monkeypatch.setenv("VAPID_PRIVATE_KEY", private_key)
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:u5-owner@example.com")
    sender = FakePushSender()
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    return sender


def _schedule_for(db, user_id: str) -> Schedule:
    person = Person(user_id=user_id, display_name="민수", relation_tag="친구", hierarchy="동")
    db.add(person)
    db.flush()
    row = Schedule(person_id=person.id, title="약속", scheduled_at=NOW + timedelta(hours=3))
    db.add(row)
    db.flush()
    return row


# ---------------------------------------------------------------------------
# 같은 endpoint 는 마지막 구독 계정 하나 (결정 P)
# ---------------------------------------------------------------------------


def test_second_account_subscribing_same_endpoint_takes_it_over(env):
    _app, a, b, db = env
    _subscribe(a)
    assert _rows(db, EP) == [(A, EP)]

    resp = _subscribe(b)

    assert resp["created"] is True  # B 입장에서는 새 행
    assert _rows(db, EP) == [(B, EP)]  # A 의 EP 행 0, B 1


def test_takeover_leaves_other_endpoints_of_the_old_account(env):
    _app, a, b, db = env
    _subscribe(a, EP)
    _subscribe(a, OTHER_EP)

    _subscribe(b, EP)

    assert _rows(db) == [(A, OTHER_EP), (B, EP)]


def test_same_account_resubscribing_keeps_one_row_and_created_false(env):
    _app, a, _b, db = env
    first = _subscribe(a)

    second = _subscribe(a)

    assert second["id"] == first["id"]
    assert second["created"] is False
    assert _rows(db, EP) == [(A, EP)]


def test_other_accounts_schedule_briefing_is_not_pushed_to_taken_over_endpoint(
    env, monkeypatch
):
    """R-6 -- 같은 브라우저(endpoint)를 A 가 쓰다 B 가 구독하면, A 의 일정 브리핑은 그 endpoint 로 가지 않는다."""
    _app, a, b, db = env
    sender = _full_vapid(monkeypatch)
    _subscribe(a)
    _subscribe(b)
    schedule_a = _schedule_for(db, A)

    resp = a.post("/briefings/run", json={"schedule_id": schedule_a.id})

    assert resp.status_code == 200
    assert [item["push"] for item in resp.json()["briefings"]] == ["no_subscription"]
    assert sender.calls == []  # B 의 endpoint 로 A 일정 알림이 가지 않았다


# ---------------------------------------------------------------------------
# 수동 브리핑 알림기는 로그인 계정 (U3b R-2)
# ---------------------------------------------------------------------------


def test_manual_briefing_notifier_uses_logged_in_account_subscriptions_only(env, monkeypatch):
    _app, a, b, db = env
    sender = _full_vapid(monkeypatch)
    _subscribe(a, "https://push.example.test/u5/a-only")
    _subscribe(b, "https://push.example.test/u5/b-only")
    _schedule_for(db, A)
    schedule_b = _schedule_for(db, B)

    resp = b.post("/briefings/run", json={"schedule_id": schedule_b.id})

    assert resp.status_code == 200
    assert [item["push"] for item in resp.json()["briefings"]] == ["sent"]
    assert [call["endpoint"] for call in sender.calls] == ["https://push.example.test/u5/b-only"]


def test_get_notifier_builds_notifier_for_the_given_logged_in_user(db_session, monkeypatch):
    for name in ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT"):
        monkeypatch.delenv(name, raising=False)
    _full_vapid(monkeypatch)
    user = make_user(db_session, "u5push-notifier-user")

    notifier = get_notifier(db_session, lambda: NOW, user)

    assert isinstance(notifier, WebPushNotifier)
    assert notifier.user_id == "u5push-notifier-user"
    assert notifier.session is db_session


def test_get_notifier_without_keys_is_null_notifier(db_session, monkeypatch):
    for name in ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT"):
        monkeypatch.delenv(name, raising=False)
    user = make_user(db_session, "u5push-notifier-null")

    assert isinstance(get_notifier(db_session, lambda: NOW, user), NullNotifier)


# ---------------------------------------------------------------------------
# 로그아웃 -- 그 브라우저 구독 떼기
# ---------------------------------------------------------------------------


def test_logout_with_endpoint_deletes_that_users_row_and_keeps_other_endpoints(env):
    _app, a, _b, db = env
    _subscribe(a, EP)
    _subscribe(a, OTHER_EP)

    resp = a.post("/auth/logout", json={"endpoint": EP})

    assert resp.status_code == 204
    assert _rows(db) == [(A, OTHER_EP)]


def test_logout_does_not_delete_another_accounts_row_with_same_endpoint(env):
    _app, a, b, db = env
    _subscribe(a, EP)
    _subscribe(b, EP)  # 결정 P 로 A 의 행은 이미 없고 B 만 남는다
    assert _rows(db, EP) == [(B, EP)]

    resp = a.post("/auth/logout", json={"endpoint": EP})

    assert resp.status_code == 204
    assert _rows(db, EP) == [(B, EP)]  # A 의 로그아웃이 B 의 구독을 건드리지 않는다


def test_logout_without_endpoint_or_body_keeps_subscriptions(env):
    _app, a, b, db = env
    _subscribe(a, EP)
    assert a.post("/auth/logout", json={}).status_code == 204
    _subscribe(b, OTHER_EP)
    assert b.post("/auth/logout").status_code == 204

    assert _rows(db) == [(A, EP), (B, OTHER_EP)]
