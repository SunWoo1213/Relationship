"""Refs: P9b-auth U2 D18 결정 T F-7 R2-1 -- 상태 변경 요청의 Origin 검사 테스트.

앞부분은 DB 없이 도는 비교 함수(`origin_matches`) 표, 뒷부분은 `TestClient` 로 앱 전체에
걸린 미들웨어를 본다(`dbtest`). 기본 클라이언트는 `https://testserver`(Host: testserver).
DB 를 바꾸는 경로가 막힐 때 행이 불변인지도 함께 단언한다.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_embedder, get_proposer, get_session
from app.auth.origin import UNSAFE_METHODS, origin_matches
from app.db.models import AgentTrace, AuthSession, Event, PendingQuestion, Person, PushSubscription, User
from app.main import create_app

EVIL = "https://evil-1-2-3-4.sslip.io"
PW = "test-only-pass-1234"


# ---------------------------------------------------------------------------
# 비교 함수 표(DB 불필요)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("origin", "host", "xfh", "expected"),
    [
        ("https://testserver", "testserver", None, True),
        (EVIL, "testserver", None, False),
        # 기본 포트는 양쪽에서 뗀다(R2-1 ①).
        ("https://testserver:443", "testserver", None, True),
        ("https://testserver", "testserver:443", None, True),
        ("http://testserver:80", "testserver", None, True),
        # 기본 포트가 아닌 포트는 그대로 비교한다.
        ("https://testserver:8443", "testserver", None, False),
        ("https://testserver:8443", "testserver:8443", None, True),
        ("https://testserver", "testserver:8443", None, False),
        # 스킴의 기본 포트만 뗀다 -- https 에 :80 은 기본 포트가 아니다.
        ("https://testserver:80", "testserver", None, False),
        # 소문자 비교.
        ("https://TestServer", "testserver", None, True),
        ("https://testserver", "TESTSERVER", None, True),
        # X-Forwarded-Host 가 있으면 그것과 비교, 쉼표면 첫 값만.
        ("https://app.example", "internal:8000", "app.example", True),
        ("https://app.example", "app.example", "internal:8000", False),
        ("https://testserver", "testserver", "testserver, evil.example", True),
        ("https://testserver", "testserver", "evil.example, testserver", False),
        ("https://app.example", "internal", " app.example ", True),
        # `null`·스킴 없음·알 수 없는 스킴·빈 값은 다름.
        ("null", "testserver", None, False),
        ("testserver", "testserver", None, False),
        ("ftp://testserver", "testserver", None, False),
        ("", "testserver", None, False),
        # 경로가 붙어 있어도 호스트만 본다.
        ("https://testserver/some/path", "testserver", None, True),
    ],
)
def test_origin_matches_table(origin: str, host: str, xfh: str | None, expected: bool) -> None:
    assert origin_matches(origin, host, xfh) is expected


def test_unsafe_methods_set_is_exactly_the_four_state_changing_methods() -> None:
    assert UNSAFE_METHODS == frozenset({"POST", "PUT", "PATCH", "DELETE"})


# ---------------------------------------------------------------------------
# 앱 전역 미들웨어(실 DB)
# ---------------------------------------------------------------------------

dbtest = pytest.mark.dbtest


@pytest.fixture(autouse=True)
def _default_cookie_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)


@pytest.fixture()
def app_(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_proposer] = lambda: None
    app.dependency_overrides[get_embedder] = lambda: None
    return app


@pytest.fixture()
def client(app_) -> TestClient:
    return TestClient(app_, base_url="https://testserver")


_WATCHED = (User, AuthSession, Person, Event, PendingQuestion, PushSubscription, AgentTrace)


def _counts(db_session) -> dict[str, int]:
    return {m.__tablename__: db_session.scalar(select(func.count()).select_from(m)) for m in _WATCHED}


def _logged_in(client: TestClient, username: str = "originuser") -> None:
    resp = client.post(
        "/auth/signup", json={"username": username, "password": PW, "nickname": username}
    )
    assert resp.status_code == 201


BAD = {"detail": {"code": "bad_origin"}}


@dbtest
@pytest.mark.parametrize(
    ("path", "json_body"),
    [
        ("/auth/logout", None),
        ("/briefings/run", {}),
        ("/chat", {"utterance": "김 대리랑 점심 먹었어"}),
        ("/auth/signup", {"username": "evilmade", "password": PW}),
    ],
)
def test_evil_origin_post_is_403_bad_origin_and_changes_nothing(
    client: TestClient, db_session, path: str, json_body: dict | None
) -> None:
    """다른 호스트의 `Origin`(같은 사이트 `*.sslip.io` 가정) -> 403, DB 변화 0(V2-7)."""
    _logged_in(client)
    before = _counts(db_session)

    resp = client.post(path, json=json_body, headers={"Origin": EVIL})

    assert resp.status_code == 403
    assert resp.json() == BAD
    assert _counts(db_session) == before


@dbtest
def test_evil_origin_logout_keeps_the_session_alive(client: TestClient) -> None:
    """위조 로그아웃이 세션을 끊지 못한다 -- 막힌 뒤에도 같은 쿠키로 `/auth/me` 200."""
    _logged_in(client, "keepalive")
    resp = client.post("/auth/logout", headers={"Origin": EVIL})
    assert resp.status_code == 403
    assert client.get("/auth/me").status_code == 200


@dbtest
@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_every_state_changing_method_is_checked_before_routing(
    client: TestClient, method: str
) -> None:
    """메서드가 라우트에 없어(405)도 Origin 이 먼저 -- 403."""
    resp = client.request(method, "/persons/1", headers={"Origin": EVIL})
    assert resp.status_code == 403
    assert resp.json() == BAD


@dbtest
@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS"])
def test_safe_methods_are_not_checked(client: TestClient, method: str) -> None:
    resp = client.request(method, "/auth/me", headers={"Origin": EVIL})
    assert resp.status_code != 403


@dbtest
def test_get_with_other_origin_is_not_403(client: TestClient) -> None:
    _logged_in(client, "getorigin")
    resp = client.get("/auth/me", headers={"Origin": EVIL})
    assert resp.status_code == 200


@dbtest
def test_same_host_origin_passes(client: TestClient) -> None:
    _logged_in(client, "samehost")
    resp = client.post("/auth/logout", headers={"Origin": "https://testserver"})
    assert resp.status_code == 204


@dbtest
def test_no_origin_header_passes(client: TestClient) -> None:
    """`Origin` 이 없으면 통과(curl·테스트 클라이언트) -- 로그인 안 했으니 401 이지 403 이 아니다."""
    resp = client.post("/auth/logout")
    assert resp.status_code == 401


@dbtest
def test_same_origin_without_login_reaches_route_with_401_not_403(client: TestClient) -> None:
    resp = client.post("/auth/logout", headers={"Origin": "https://testserver"})
    assert resp.status_code == 401


@dbtest
def test_x_forwarded_host_equal_to_origin_passes(client: TestClient) -> None:
    """Caddy 뒤가 아니라 프록시가 `Host` 를 바꾸는 개발 환경(사실 14) -- `Origin` 이
    `X-Forwarded-Host` 와 같으면 `Host`(testserver)와 달라도 통과."""
    resp = client.post(
        "/auth/logout",
        headers={"Origin": "https://app.example", "X-Forwarded-Host": "app.example"},
    )
    assert resp.status_code == 401  # 403 아님 -- 라우트에 닿음


@dbtest
def test_origin_not_equal_to_host_without_forwarded_host_is_403(client: TestClient) -> None:
    resp = client.post("/auth/logout", headers={"Origin": "https://app.example"})
    assert resp.status_code == 403


@dbtest
def test_default_port_origin_passes(client: TestClient) -> None:
    """`Origin: https://testserver:443` ↔ `Host: testserver` -> 403 아님(기본 포트 제거)."""
    resp = client.post("/auth/logout", headers={"Origin": "https://testserver:443"})
    assert resp.status_code == 401


@dbtest
def test_non_default_port_origin_is_403(client: TestClient) -> None:
    resp = client.post("/auth/logout", headers={"Origin": "https://testserver:8443"})
    assert resp.status_code == 403


@dbtest
def test_uppercase_origin_host_passes(client: TestClient) -> None:
    """`Origin: https://TestServer` ↔ `Host: testserver` -> 403 아님(소문자 비교)."""
    resp = client.post("/auth/logout", headers={"Origin": "https://TestServer"})
    assert resp.status_code == 401


@dbtest
def test_x_forwarded_host_uses_first_value_only(client: TestClient) -> None:
    """`X-Forwarded-Host: testserver, evil.example` + `Origin: https://testserver` -> 403 아님."""
    ok = client.post(
        "/auth/logout",
        headers={"Origin": "https://testserver", "X-Forwarded-Host": "testserver, evil.example"},
    )
    assert ok.status_code == 401
    # 첫 값이 위조 호스트면 막힌다(뒤쪽 값으로 통과하지 못한다).
    bad = client.post(
        "/auth/logout",
        headers={"Origin": "https://testserver", "X-Forwarded-Host": "evil.example, testserver"},
    )
    assert bad.status_code == 403


@dbtest
def test_null_origin_is_403(client: TestClient) -> None:
    resp = client.post("/auth/logout", headers={"Origin": "null"})
    assert resp.status_code == 403
    assert resp.json() == BAD
