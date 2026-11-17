"""Refs: P9b-auth U3b D18 CR-006 지킬 것 4 -- 라우트 열거 401 계약.

`app.routes` 를 **열거**해 `/health`·`/auth/signup`·`/auth/login`·`GET /auth/availability`(CR-007)·문서 경로를 뺀 모든 API 라우트가
쿠키 없이 401 `unauthenticated` 인지 본다(경로 매개변수는 `1` 로 채운다). **`/auth/logout` 은 예외가
아니다**(F-3). 새 라우트가 `current_user` 의존성을 빠뜨리면 이 시험이 실패한다.

- 면제 목록은 **이름으로** 박는다(`_EXEMPT`) -- 목록 밖 경로가 면제로 새는 것을 막는다.
- `/push-dev/` 세 경로는 `PUSH_DEV_PAGE_ENABLED` 가 켜질 때만 생긴다(기본 꺼짐이라 열거에 나오지 않는다).
  켜진 경우의 정적 개발 페이지는 고정 사용자를 쓰지 않는 파일 서빙이라 이 계약의 대상이 아니다(R-4 ③)
  -- 켜진 앱에서는 그 세 경로만 면제임을 `test_push_dev_page_routes_are_the_only_other_exempt` 가 이름으로 본다.

(CR-008) **`/mcp` 는 면제가 아니라 다른 자격이다**(D18 결정 3 CR-008 보충 -- `Authorization: Bearer`
토큰). `/mcp` 는 `MCP_ENABLED` 를 켠 앱에만 있어 이 열거(스위치 꺼짐)에는 나오지 않는다 -- 켠 앱의 열거는
아래 `test_mcp_route_when_enabled_is_401_without_credentials` 가 본다. `_EXEMPT`·면제 등식은 그대로다.

`import app.auth.deps` 를 **맨 먼저** 해도 순환 import 가 나지 않는지도 새 인터프리터로 본다(U2 인계 —
`app.api.*` → `app.auth.deps` → `app.db.session` 한 방향이어야 한다).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_session
from app.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]

UNAUTHENTICATED = {"detail": {"code": "unauthenticated"}}

#: 로그인 없이 열려 있어야 하는 API(공개 4개 -- CR-007 이 `GET /auth/availability` 를 더했다)
#: + FastAPI 기본 문서 경로.
_EXEMPT = {
    ("GET", "/health"),
    ("POST", "/auth/signup"),
    ("POST", "/auth/login"),
    ("GET", "/auth/availability"),
    ("GET", "/docs"),
    ("GET", "/docs/oauth2-redirect"),
    ("GET", "/redoc"),
    ("GET", "/openapi.json"),
}

#: 로그인을 요구해야 하는 경로 — 이 값 안의 것이 열거에서 빠지면(라우트 삭제·이름 변경) 실패한다.
_MUST_REQUIRE_LOGIN = {
    ("POST", "/answers/{question_id}"),
    ("POST", "/chat"),
    ("POST", "/briefings/run"),
    ("GET", "/push/vapid-public-key"),
    ("POST", "/push/subscriptions"),
    ("GET", "/persons"),
    ("GET", "/persons/{person_id}"),
    ("GET", "/events/{event_id}/raw"),
    ("GET", "/persons/{person_id}/facts/{fact_id}/sources"),
    ("GET", "/questions/pending"),
    ("GET", "/briefings"),
    ("POST", "/auth/logout"),  # F-3 -- 로그아웃도 미로그인 401
    ("GET", "/auth/me"),
    # CR-008 -- MCP 토큰 발급 API 는 쿠키 로그인이 자격이다(`/mcp` 자체는 면제가 아니라 다른 자격).
    ("POST", "/auth/mcp-token"),
    ("GET", "/auth/mcp-token"),
    ("DELETE", "/auth/mcp-token"),
}


def _routes(app) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if path is None or not methods:
            continue
        for method in sorted(methods - {"HEAD", "OPTIONS"}):
            found.append((method, path))
    return found


def _fill_path(path: str) -> str:
    out = path
    while "{" in out:
        start = out.index("{")
        end = out.index("}", start)
        out = out[:start] + "1" + out[end + 1 :]
    return out


@pytest.fixture()
def bare_client():
    """쿠키가 없는 클라이언트. 401 은 DB 에 묻기 전에 나므로 빈 세션을 끼워 DB 접속을 막는다."""
    from sqlalchemy.orm import Session

    app = create_app()

    def _no_db_session():
        yield Session()  # 엔진에 묶이지 않은 세션 -- 쿼리를 보내면 오류(그러면 401 이 아닌 500 이 난다)

    app.dependency_overrides[get_session] = _no_db_session
    return app, TestClient(app, base_url="https://testserver")


def test_enumerated_routes_cover_the_known_api_surface(bare_client):
    app, _client = bare_client
    routes = set(_routes(app))
    # 알려진 보호 대상이 전부 열거에 있다(라우트가 사라지거나 이름이 바뀌면 이 시험이 먼저 알린다).
    assert _MUST_REQUIRE_LOGIN <= routes
    # 면제는 정확히 이름 목록뿐이다 -- 열거된 라우트 중 면제도 보호 대상도 아닌 것은 이 시험이 따로 본다.
    assert {r for r in routes if r in _EXEMPT} == {
        ("GET", "/health"),
        ("POST", "/auth/signup"),
        ("POST", "/auth/login"),
        ("GET", "/auth/availability"),
        ("GET", "/docs"),
        ("GET", "/docs/oauth2-redirect"),
        ("GET", "/redoc"),
        ("GET", "/openapi.json"),
    }


def test_every_non_exempt_route_requires_login(bare_client):
    app, client = bare_client
    checked: list[tuple[str, str]] = []
    for method, path in _routes(app):
        if (method, path) in _EXEMPT:
            continue
        resp = client.request(method, _fill_path(path), json={})
        assert resp.status_code == 401, f"{method} {path} -> {resp.status_code}"
        assert resp.json() == UNAUTHENTICATED, f"{method} {path}"
        checked.append((method, path))
    # 열거가 비어 헛통과하지 않는다 -- 보호 대상 13개가 전부 검사됐다.
    assert _MUST_REQUIRE_LOGIN <= set(checked)


def test_mcp_route_when_enabled_is_401_without_credentials(monkeypatch):
    """(CR-008, 결정 AN) `MCP_ENABLED=1` 인 앱의 열거에는 `/mcp` 세 메서드가 있고, 쿠키·헤더 없이는 DB 조회
    없이 같은 401 `unauthenticated` 다. 면제 등식(`_EXEMPT`)·보호 목록은 그대로다."""
    from sqlalchemy.orm import Session

    monkeypatch.setenv("MCP_ENABLED", "1")
    monkeypatch.setattr("app.main.SessionLocal", lambda: Session())  # DB 에 가면 오류(500)
    app = create_app()
    app.dependency_overrides[get_session] = lambda: Session()
    enumerated = set(_routes(app))

    assert {("GET", "/mcp"), ("POST", "/mcp"), ("DELETE", "/mcp")} <= enumerated
    assert _MUST_REQUIRE_LOGIN <= enumerated
    client = TestClient(app, base_url="https://testserver")
    for method, path in sorted(enumerated):
        if (method, path) in _EXEMPT:
            continue
        resp = client.request(method, _fill_path(path), json={})
        assert resp.status_code == 401, f"{method} {path} -> {resp.status_code}"
        assert resp.json() == UNAUTHENTICATED, f"{method} {path}"


def test_logout_without_login_is_401_not_exempt(bare_client):
    _app, client = bare_client
    resp = client.post("/auth/logout")
    assert resp.status_code == 401
    assert resp.json() == UNAUTHENTICATED


def test_public_routes_stay_open(bare_client):
    """`/auth/signup`·`/auth/login` 은 401 `unauthenticated` 가 아니라 본문 검증으로 넘어간다."""
    _app, client = bare_client
    assert client.post("/auth/signup", json={}).status_code == 422
    assert client.post("/auth/login", json={}).status_code == 422
    # (CR-007 · R4-2) 조회 API 는 쿠키 없이 401 이 아니다 -- `bare_client` 의 세션은 엔진에 묶이지
    # 않아 DB 에 가는 요청은 쓸 수 없으므로 DB 에 가지 않는 두 요청만 쓴다.
    missing = client.get("/auth/availability")
    assert missing.status_code == 422
    assert missing.json() == {"detail": {"code": "missing_query"}}
    empty = client.get("/auth/availability", params={"username": ""})
    assert empty.status_code == 200
    assert empty.json() == {"username": "invalid", "nickname": None}


def test_push_dev_page_routes_are_the_only_other_exempt(monkeypatch):
    """`PUSH_DEV_PAGE_ENABLED=1` 이면 `/push-dev/` 세 경로가 더 생긴다 -- 그 세 경로 말고는 새 면제가 없다."""
    monkeypatch.setenv("PUSH_DEV_PAGE_ENABLED", "1")
    app = create_app()
    extra = {
        (method, path)
        for method, path in _routes(app)
        if path.startswith("/push-dev")
    }
    assert extra == {
        ("GET", "/push-dev/"),
        ("GET", "/push-dev/sw.js"),
        ("GET", "/push-dev/devpage.js"),
    }
    others = {
        (method, path)
        for method, path in _routes(app)
        if not path.startswith("/push-dev") and (method, path) not in _EXEMPT
    }
    assert _MUST_REQUIRE_LOGIN <= others


def test_every_api_route_declares_current_user_dependency():
    """401 이 실제 호출 없이도 구조로 보이게 -- 면제가 아닌 `APIRoute` 는 `current_user` 를 의존한다."""
    from app.auth.deps import current_user

    app = create_app()
    missing = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods - {"HEAD", "OPTIONS"}:
            if (method, route.path) in _EXEMPT:
                continue

            def _calls(dep) -> bool:
                if dep.call is current_user:
                    return True
                return any(_calls(sub) for sub in dep.dependencies)

            if not _calls(route.dependant):
                missing.append((method, route.path))
    assert missing == []


@pytest.mark.parametrize(
    "module",
    ["app.auth.deps", "app.auth.routes", "app.api.deps", "app.api.routes", "app.main"],
)
def test_importing_any_module_first_has_no_circular_import(module):
    """새 인터프리터에서 그 모듈을 **맨 먼저** import 한다(순환 import 를 끊은 방법의 회귀 시험)."""
    proc = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[-800:]
