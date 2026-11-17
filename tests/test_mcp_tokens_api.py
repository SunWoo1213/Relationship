"""Refs: P9b-auth U12 CR-008 D19 D18 -- `POST·GET·DELETE /auth/mcp-token` 시험.

계획 01-plan "API 계약 — 개정 4"·"발급 판정 순서"를 값으로 단언한다. `TestClient(create_app())` +
`get_session` 오버라이드로 롤백 픽스처(`db_session`)를 주입한다(`test_auth_nickname.py` 와 같은 방식) --
DB 에 행이 남지 않는다. 시계는 `get_auth_now` 를 덮어써 고정한다. 실 PostgreSQL 이 필요하다(`dbtest`).

토큰 값은 단언 실패 메시지에 넣지 않는다(D19 지킬 것 7).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.api.deps import get_session
from app.auth.deps import get_auth_now
from app.auth.mcp_tokens import user_id_for_mcp_token
from app.auth.sessions import hash_token
from app.db.models import AgentTrace, ChatMessage, Event, McpToken, Person
from app.main import create_app
from tests.auth_helpers import logged_in_client, make_user

pytestmark = pytest.mark.dbtest

#: 고정 시계(UTC). 로그인 세션 행은 이 시각 기준으로 만든다.
T0 = datetime(2026, 11, 18, 9, 0, 0, tzinfo=timezone.utc)

NO_COOKIE_JSON = {"detail": {"code": "unauthenticated"}}


class _Clock:
    """덮어쓸 수 있는 시계 -- `set()` 으로 시각을 옮긴다."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture()
def clock() -> _Clock:
    return _Clock(T0)


@pytest.fixture()
def app_(db_session, clock):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_auth_now] = lambda: clock
    return app


@pytest.fixture()
def client(app_, db_session) -> TestClient:
    # 로그인 세션은 T0 + 1일 기준으로 만든다 -- 토큰(T0 + 7일) 만료 경계에서도 로그인은 살아 있게.
    return logged_in_client(
        app_, db_session, "mcpuser-a", now=T0 + timedelta(days=1), raise_server_exceptions=False
    )


def _rows(db_session) -> list[McpToken]:
    return list(db_session.scalars(select(McpToken).order_by(McpToken.id)))


def _count(db_session, model) -> int:
    return db_session.scalar(select(func.count()).select_from(model))


# ① 쿠키 없이 세 메서드 401 ----------------------------------------------------------------


@pytest.mark.parametrize("method", ["POST", "GET", "DELETE"])
def test_three_methods_without_cookie_are_401_unauthenticated(app_, method) -> None:
    anon = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)

    resp = anon.request(method, "/auth/mcp-token")

    assert resp.status_code == 401
    assert resp.json() == NO_COOKIE_JSON


# ② POST 201 ------------------------------------------------------------------------------


def test_post_returns_201_with_exact_keys_seven_day_expiry_and_no_store(client) -> None:
    resp = client.post("/auth/mcp-token")

    assert resp.status_code == 201
    body = resp.json()
    assert set(body) == {"token", "created_at", "expires_at"}
    assert len(body["token"]) == 43  # secrets.token_urlsafe(32)
    created = datetime.fromisoformat(body["created_at"])
    expires = datetime.fromisoformat(body["expires_at"])
    assert created == T0
    assert expires - created == timedelta(days=7)
    assert created.tzinfo is not None and expires.tzinfo is not None
    assert resp.headers["Cache-Control"] == "no-store"


# ③ DB 에는 해시만 --------------------------------------------------------------------------


def test_row_stores_only_the_hash_never_the_token(client, db_session) -> None:
    token = client.post("/auth/mcp-token").json()["token"]

    rows = _rows(db_session)
    assert len(rows) == 1
    row = rows[0]
    assert row.token_hash == hash_token(token)
    values = [row.id, row.user_id, row.token_hash, row.created_at, row.expires_at, row.last_used_at]
    assert all(str(v) != token for v in values)
    assert token not in " ".join(str(v) for v in values)
    assert row.user_id == "mcpuser-a"
    assert row.last_used_at is None


# ④ 재발급은 upsert -------------------------------------------------------------------------


def test_second_post_keeps_one_row_and_invalidates_the_previous_token(client, db_session, clock) -> None:
    first = client.post("/auth/mcp-token").json()["token"]
    clock.now = T0 + timedelta(hours=1)
    second = client.post("/auth/mcp-token").json()

    assert first != second["token"]
    rows = _rows(db_session)
    assert len(rows) == 1
    assert rows[0].token_hash == hash_token(second["token"])
    assert user_id_for_mcp_token(db_session, first, clock.now) is None
    assert user_id_for_mcp_token(db_session, second["token"], clock.now) == "mcpuser-a"
    # 재발급은 시각도 새로 -- created_at 이 두 번째 발급 시각, 만료도 거기서 7일.
    assert datetime.fromisoformat(second["created_at"]) == T0 + timedelta(hours=1)
    assert datetime.fromisoformat(second["expires_at"]) == T0 + timedelta(hours=1, days=7)


def test_reissue_resets_last_used_at_to_null(client, db_session, clock) -> None:
    token = client.post("/auth/mcp-token").json()["token"]
    assert user_id_for_mcp_token(db_session, token, clock.now) == "mcpuser-a"
    assert _rows(db_session)[0].last_used_at == clock.now

    client.post("/auth/mcp-token")

    assert _rows(db_session)[0].last_used_at is None


# ⑤ GET 상태 ---------------------------------------------------------------------------------


def test_get_without_row_is_inactive_with_three_nulls(client) -> None:
    resp = client.get("/auth/mcp-token")

    assert resp.status_code == 200
    assert resp.json() == {
        "active": False,
        "created_at": None,
        "expires_at": None,
        "last_used_at": None,
    }
    assert resp.headers["Cache-Control"] == "no-store"


def test_get_after_issue_is_active_with_exactly_four_keys_and_no_token(client) -> None:
    token = client.post("/auth/mcp-token").json()["token"]

    resp = client.get("/auth/mcp-token")

    body = resp.json()
    assert set(body) == {"active", "created_at", "expires_at", "last_used_at"}
    assert body["active"] is True
    assert datetime.fromisoformat(body["created_at"]) == T0
    assert datetime.fromisoformat(body["expires_at"]) == T0 + timedelta(days=7)
    assert body["last_used_at"] is None
    assert resp.headers["Cache-Control"] == "no-store"
    assert token not in resp.text


def test_get_expiry_boundary_same_instant_is_inactive_one_second_before_is_active(client, clock) -> None:
    created = client.post("/auth/mcp-token").json()
    expires = datetime.fromisoformat(created["expires_at"])

    clock.now = expires - timedelta(seconds=1)
    before = client.get("/auth/mcp-token").json()
    clock.now = expires  # 같은 순간은 만료(`expires_at > now`)
    at = client.get("/auth/mcp-token").json()

    assert before["active"] is True
    assert at["active"] is False
    # 만료여도 세 값은 행 값 그대로.
    assert datetime.fromisoformat(at["expires_at"]) == expires
    assert datetime.fromisoformat(at["created_at"]) == T0
    assert at["last_used_at"] is None


def test_get_shows_last_used_at_after_the_token_is_used(client, db_session, clock) -> None:
    token = client.post("/auth/mcp-token").json()["token"]
    clock.now = T0 + timedelta(hours=2)
    assert user_id_for_mcp_token(db_session, token, clock.now) == "mcpuser-a"

    body = client.get("/auth/mcp-token").json()

    assert datetime.fromisoformat(body["last_used_at"]) == T0 + timedelta(hours=2)


# ⑥ DELETE ----------------------------------------------------------------------------------


def test_delete_returns_204_removes_the_row_and_is_idempotent(client, db_session) -> None:
    client.post("/auth/mcp-token")
    assert len(_rows(db_session)) == 1

    first = client.delete("/auth/mcp-token")
    after_first = len(_rows(db_session))
    second = client.delete("/auth/mcp-token")

    assert first.status_code == 204 and first.content == b""
    assert after_first == 0
    assert second.status_code == 204 and second.content == b""


# ⑦ Origin 검사 -----------------------------------------------------------------------------


def test_foreign_origin_post_and_delete_are_403_bad_origin_and_change_nothing(client, db_session) -> None:
    client.post("/auth/mcp-token")
    before = [(r.token_hash, r.created_at) for r in _rows(db_session)]

    post = client.post("/auth/mcp-token", headers={"Origin": "https://evil.example"})
    delete = client.delete("/auth/mcp-token", headers={"Origin": "https://evil.example"})

    assert post.status_code == 403 and post.json() == {"detail": {"code": "bad_origin"}}
    assert delete.status_code == 403 and delete.json() == {"detail": {"code": "bad_origin"}}
    assert [(r.token_hash, r.created_at) for r in _rows(db_session)] == before


def test_same_origin_post_is_allowed(client) -> None:
    resp = client.post("/auth/mcp-token", headers={"Origin": "https://testserver"})

    assert resp.status_code == 201


# ⑧ 계정 격리 -------------------------------------------------------------------------------


def test_delete_and_get_are_scoped_to_the_logged_in_account(app_, db_session, clock) -> None:
    a = logged_in_client(app_, db_session, "mcpuser-a", now=T0 + timedelta(days=1))
    b = logged_in_client(app_, db_session, "mcpuser-b", now=T0 + timedelta(days=1))
    a.post("/auth/mcp-token")
    clock.now = T0 + timedelta(hours=5)
    b_token = b.post("/auth/mcp-token").json()["token"]

    a_view = a.get("/auth/mcp-token").json()
    a.delete("/auth/mcp-token")

    # A 의 GET 이 B 의 시각(T0 + 5h)을 보이지 않는다.
    assert datetime.fromisoformat(a_view["created_at"]) == T0
    rows = _rows(db_session)
    assert [r.user_id for r in rows] == ["mcpuser-b"]  # A 의 DELETE 가 B 의 행을 지우지 않았다
    assert rows[0].token_hash == hash_token(b_token)
    b_view = b.get("/auth/mcp-token").json()
    assert datetime.fromisoformat(b_view["created_at"]) == T0 + timedelta(hours=5)
    assert b_view["active"] is True


# ⑨ 다른 테이블 쓰기 0 ------------------------------------------------------------------------


def test_issue_status_revoke_do_not_touch_other_tables(client, db_session) -> None:
    make_user(db_session, "mcpuser-a")  # 로그인 클라이언트가 이미 만들었다(멱등)
    models = (Person, Event, AgentTrace, ChatMessage)
    before = [_count(db_session, m) for m in models]

    client.post("/auth/mcp-token")
    client.get("/auth/mcp-token")
    client.delete("/auth/mcp-token")

    assert [_count(db_session, m) for m in models] == before


# ⑩ 토큰이 로그·응답에 없다 -------------------------------------------------------------------


def test_token_never_appears_in_logs_or_non_issue_responses(client, caplog) -> None:
    with caplog.at_level(logging.DEBUG):
        issued = client.post("/auth/mcp-token")
        token = issued.json()["token"]
        others = [client.get("/auth/mcp-token"), client.delete("/auth/mcp-token")]

    assert all(token not in r.text for r in others)
    assert all(token not in rec.getMessage() for rec in caplog.records)
    assert all(token not in str(rec.args) for rec in caplog.records)


# 보조 — 제약 이름 -----------------------------------------------------------------------------


def test_unique_constraint_names_exist_in_the_database(db_session) -> None:
    names = set(
        db_session.execute(
            text("SELECT conname FROM pg_constraint WHERE conrelid = 'mcp_tokens'::regclass")
        ).scalars()
    )

    assert {"uq_mcp_tokens_user_id", "uq_mcp_tokens_token_hash"} <= names
