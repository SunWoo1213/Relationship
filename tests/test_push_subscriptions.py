"""Refs: P7-push S3.1 S3.6 R12 -- U2 판정: `app.push.subscriptions`(저장·
목록)·`GET /push/vapid-public-key`·`POST /push/subscriptions`(01-plan
판정 표 1~5행 -- 양성 저장·같은 엔드포인트 갱신·잘못된 본문 422·
공개키 200/404/반쪽 404·사용자 격리).

`TestClient(create_app())` + `app.dependency_overrides[get_session]`
(`db_session` 롤백 픽스처 주입, P2 결정 13 과 같은 방식)로 DB 에 행을
남기지 않는다. VAPID 환경변수는 `monkeypatch.setenv`/`delenv` 로
설정한다 -- `GET /push/vapid-public-key` 라우트가 `app.settings.
vapid_config()` 를 인자 없이(= `os.environ` 읽기) 그대로 부르기 때문이다
(`app/api/routes.py` "P7-push U2" 절 참고, `tests/test_push_settings.py`
의 `monkeypatch.setenv` 와 같은 관례).

이 파일은 `pywebpush` 를 import 하지 않는다(01-plan "지킬 불변식" --
그 이름은 U4 `app/push/sender.py` 한 곳에서만 나타나야 한다). 실제
발송은 이 단위의 범위 밖이다(U4).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import get_session
from app.db.models import PushSubscription
from app.main import create_app
from app.push.subscriptions import list_subscriptions, save_subscription

dbtest = pytest.mark.dbtest
pytestmark = dbtest


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session):
    """U1 롤백 세션을 `get_session` 자리에 주입한 `(app, client)` 쌍
    (`tests/test_api_briefings.py` 와 같은 모양, P2 결정 13)."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    return app, TestClient(app)


#: 테스트가 만드는 가짜 구독 본문(실제 브라우저 값이 아니다 -- 테스트
#: 전용 자리에서 만든 더미 base64url 문자열, 01-plan 결정 G "실비밀이
#: 아니다"와 같은 이유).
_VALID_ENDPOINT = "https://fcm.googleapis.com/fcm/send/test-endpoint-abc123"
_VALID_KEYS = {"p256dh": "p256dh-test-value_ABC-123", "auth": "auth-test-value_XYZ-789"}


def _subscription_body(
    endpoint: str = _VALID_ENDPOINT, keys: dict[str, str] | None = None
) -> dict:
    return {"endpoint": endpoint, "keys": dict(keys if keys is not None else _VALID_KEYS)}


# ---------------------------------------------------------------------------
# 판정 1행 -- 구독 저장 양성
# ---------------------------------------------------------------------------


def test_create_subscription_returns_id_and_created_true(app_and_client):
    app, client = app_and_client

    resp = client.post("/push/subscriptions", json=_subscription_body())

    assert resp.status_code == 200
    body = resp.json()
    assert body["created"] is True
    assert isinstance(body["id"], int)


def test_create_subscription_persists_row_with_user_and_keys(app_and_client, db_session):
    app, client = app_and_client

    resp = client.post("/push/subscriptions", json=_subscription_body())
    assert resp.status_code == 200
    row_id = resp.json()["id"]

    rows = db_session.execute(select(PushSubscription)).scalars().all()
    assert len(rows) == 1
    row = rows[0]
    assert row.id == row_id
    assert row.user_id == "local"  # app_user_id() 기본값(APP_USER_ID 미설정)
    assert row.endpoint == _VALID_ENDPOINT
    assert row.keys == _VALID_KEYS


def test_create_subscription_expiration_time_is_accepted_but_not_stored(app_and_client):
    """01-plan 결정 F -- `expirationTime` 은 받기만 하고 저장하지 않는다
    (그 열이 없다)."""
    app, client = app_and_client
    body = _subscription_body()
    body["expirationTime"] = 1234567890.0

    resp = client.post("/push/subscriptions", json=body)

    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 판정 2행 -- 같은 엔드포인트는 키만 갱신
# ---------------------------------------------------------------------------


def test_create_subscription_same_endpoint_updates_keys_without_new_row(app_and_client, db_session):
    app, client = app_and_client

    first = client.post("/push/subscriptions", json=_subscription_body())
    assert first.status_code == 200
    assert first.json()["created"] is True
    first_id = first.json()["id"]

    new_keys = {"p256dh": "new-p256dh-value_DEF-456", "auth": "new-auth-value_UVW-321"}
    second = client.post("/push/subscriptions", json=_subscription_body(keys=new_keys))

    assert second.status_code == 200
    assert second.json()["created"] is False
    assert second.json()["id"] == first_id

    rows = db_session.execute(select(PushSubscription)).scalars().all()
    assert len(rows) == 1
    assert rows[0].keys == new_keys


# ---------------------------------------------------------------------------
# 판정 3행 -- 잘못된 본문은 422, 행 0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        _subscription_body(endpoint="http://fcm.googleapis.com/fcm/send/abc"),
        _subscription_body(endpoint=""),
        {"endpoint": _VALID_ENDPOINT, "keys": {"p256dh": _VALID_KEYS["p256dh"]}},  # auth 누락
        _subscription_body(keys={"p256dh": "", "auth": _VALID_KEYS["auth"]}),
        _subscription_body(keys={"p256dh": "not base64url!!", "auth": _VALID_KEYS["auth"]}),
        _subscription_body(endpoint="https://" + "a" * 2100),  # 길이 상한 초과
    ],
    ids=[
        "http-not-https",
        "empty-endpoint",
        "missing-auth-key",
        "empty-p256dh",
        "non-base64url-p256dh",
        "endpoint-too-long",
    ],
)
def test_create_subscription_invalid_body_returns_422_and_no_row(app_and_client, db_session, body):
    app, client = app_and_client

    resp = client.post("/push/subscriptions", json=body)

    assert resp.status_code == 422
    rows = db_session.execute(select(PushSubscription)).scalars().all()
    assert rows == []


# ---------------------------------------------------------------------------
# 판정 4행 -- 공개키 API: 설정됨 / 미설정 / 반쪽
# ---------------------------------------------------------------------------


def test_vapid_public_key_returns_200_when_fully_configured(app_and_client, monkeypatch):
    app, client = app_and_client
    monkeypatch.setenv("VAPID_PUBLIC_KEY", "test-public-key-value")
    monkeypatch.setenv("VAPID_PRIVATE_KEY", "test-private-key-value")
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:test@example.com")

    resp = client.get("/push/vapid-public-key")

    assert resp.status_code == 200
    assert resp.json() == {"public_key": "test-public-key-value"}
    # security §1 -- 개인키 값이 응답 본문 어디에도 없다.
    assert "test-private-key-value" not in resp.text


def test_vapid_public_key_returns_404_when_not_configured(app_and_client, monkeypatch):
    app, client = app_and_client
    monkeypatch.delenv("VAPID_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("VAPID_SUBJECT", raising=False)

    resp = client.get("/push/vapid-public-key")

    assert resp.status_code == 404
    assert resp.json() == {"detail": {"code": "push_not_configured"}}


def test_vapid_public_key_returns_404_when_partially_configured(app_and_client, monkeypatch):
    app, client = app_and_client
    monkeypatch.setenv("VAPID_PUBLIC_KEY", "test-public-key-value")
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("VAPID_SUBJECT", raising=False)

    resp = client.get("/push/vapid-public-key")

    assert resp.status_code == 404
    assert resp.json() == {"detail": {"code": "push_not_configured"}}


# ---------------------------------------------------------------------------
# 판정 5행 -- 사용자 격리 (`list_subscriptions`, security §5)
# ---------------------------------------------------------------------------


def test_list_subscriptions_only_returns_own_user(db_session):
    save_subscription(
        db_session, "other-user", "https://example.com/fcm/other", {"p256dh": "p", "auth": "a"}
    )
    mine = save_subscription(
        db_session, "local", "https://example.com/fcm/mine", {"p256dh": "p2", "auth": "a2"}
    )

    rows = list_subscriptions(db_session, "local")

    assert [row.id for row in rows] == [mine.id]


def test_list_subscriptions_same_endpoint_different_users_are_separate_rows(db_session):
    """같은 엔드포인트라도 `user_id` 가 다르면 별개 행이다(결정 F(i)는
    `(user_id, endpoint)` 조합 기준)."""
    endpoint = "https://example.com/fcm/shared"
    first = save_subscription(db_session, "user-a", endpoint, {"p256dh": "p", "auth": "a"})
    second = save_subscription(db_session, "user-b", endpoint, {"p256dh": "p2", "auth": "a2"})

    assert first.id != second.id
    assert [row.id for row in list_subscriptions(db_session, "user-a")] == [first.id]
    assert [row.id for row in list_subscriptions(db_session, "user-b")] == [second.id]
