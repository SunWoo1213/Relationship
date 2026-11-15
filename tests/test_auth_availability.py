"""Refs: P9b-auth U9 CR-007 D18 결정 11 지킬 것 4·11 -- `GET /auth/availability` 테스트.

로그인 없이 부르는 아이디·닉네임 중복 조회. 쓰기·trace·LLM 호출 0, 형식 위반은 DB 에 묻기 전
`invalid`. 쿼리로는 짝 없는 서로게이트가 서버에 닿지 않으므로(`%ED%A0%80` -> U+FFFD, R4-4) 그
입력은 원시 경로 문자열로 쓰고 기대는 `invalid`. 실 PostgreSQL 이 필요하다(`dbtest`).
"""

from __future__ import annotations

import unicodedata

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_session
from app.db.models import AgentTrace, AuthSession, ChatMessage, User
from app.main import create_app

pytestmark = pytest.mark.dbtest

PW = "test-only-pass-1234"
_WATCHED = (User, AuthSession, ChatMessage, AgentTrace)


@pytest.fixture(autouse=True)
def _default_cookie_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)


@pytest.fixture()
def app_(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    return app


@pytest.fixture()
def client(app_) -> TestClient:
    return TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)


@pytest.fixture()
def seeded(client) -> TestClient:
    """계정 하나(아이디 `taken_user`, 닉네임 `민지`)를 가입시키고 쿠키는 비운다."""
    resp = client.post(
        "/auth/signup", json={"username": "taken_user", "password": PW, "nickname": "민지"}
    )
    assert resp.status_code == 201
    client.cookies.clear()
    return client


def _counts(db_session) -> dict[str, int]:
    return {
        m.__tablename__: db_session.scalar(select(func.count()).select_from(m)) for m in _WATCHED
    }


def test_open_without_cookie_returns_200(seeded) -> None:
    resp = seeded.get("/auth/availability", params={"username": "free_name"})

    assert resp.status_code == 200
    assert resp.json() == {"username": "available", "nickname": None}


def test_same_body_with_a_login_cookie(seeded) -> None:
    without = seeded.get("/auth/availability", params={"username": "taken_user", "nickname": "민지"})
    seeded.post("/auth/login", json={"username": "taken_user", "password": PW})
    assert seeded.get("/auth/me").status_code == 200  # 쿠키가 실제로 실려 있다

    with_cookie = seeded.get(
        "/auth/availability", params={"username": "taken_user", "nickname": "민지"}
    )

    assert with_cookie.status_code == 200
    assert with_cookie.json() == without.json() == {"username": "taken", "nickname": "taken"}


@pytest.mark.parametrize(
    ("username", "expected"),
    [
        ("free_name", "available"),
        ("taken_user", "taken"),
        ("TAKEN_USER", "taken"),  # 대문자 -> 정규화 뒤 taken
        ("Free_Name", "available"),
        ("ab", "invalid"),  # 너무 짧음
        ("a" * 21, "invalid"),
        ("bad-name", "invalid"),
        ("민지민지", "invalid"),
        ("", "invalid"),
    ],
)
def test_username_statuses(seeded, username: str, expected: str) -> None:
    resp = seeded.get("/auth/availability", params={"username": username})

    assert resp.status_code == 200
    assert resp.json() == {"username": expected, "nickname": None}


@pytest.mark.parametrize(
    ("nickname", "expected"),
    [
        ("새닉네임", "available"),
        ("민지", "taken"),
        (" 민지 ", "taken"),  # 정규화 뒤 판정
        (unicodedata.normalize("NFD", "민지"), "taken"),
        ("MINJI", "available"),
        ("가", "invalid"),
        ("ㅋㅋ", "invalid"),
        ("민 지", "invalid"),
        ("min-ji", "invalid"),
        ("가" * 21, "invalid"),
        ("", "invalid"),
    ],
)
def test_nickname_statuses(seeded, nickname: str, expected: str) -> None:
    resp = seeded.get("/auth/availability", params={"nickname": nickname})

    assert resp.status_code == 200
    assert resp.json() == {"username": None, "nickname": expected}


def test_nickname_case_folded_taken_after_signup(client) -> None:
    client.post("/auth/signup", json={"username": "caseowner", "password": PW, "nickname": "Demo"})
    client.cookies.clear()

    resp = client.get("/auth/availability", params={"nickname": "DEMO"})

    assert resp.json() == {"username": None, "nickname": "taken"}


def test_asking_both_returns_both_and_one_returns_other_null(seeded) -> None:
    both = seeded.get(
        "/auth/availability", params={"username": "taken_user", "nickname": "새닉네임"}
    )
    only_nick = seeded.get("/auth/availability", params={"nickname": "새닉네임"})
    only_user = seeded.get("/auth/availability", params={"username": "free_name"})

    assert both.json() == {"username": "taken", "nickname": "available"}
    assert only_nick.json() == {"username": None, "nickname": "available"}
    assert only_user.json() == {"username": "available", "nickname": None}


def test_no_query_is_422_missing_query(client) -> None:
    resp = client.get("/auth/availability")

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "missing_query"}}


def test_empty_string_counts_as_asked_and_is_invalid(client) -> None:
    resp = client.get("/auth/availability", params={"username": ""})

    assert resp.status_code == 200
    assert resp.json() == {"username": "invalid", "nickname": None}


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/auth/availability?username=%00", {"username": "invalid", "nickname": None}),
        ("/auth/availability?username=ab%00cd", {"username": "invalid", "nickname": None}),
        ("/auth/availability?nickname=%00", {"username": None, "nickname": "invalid"}),
        ("/auth/availability?nickname=a%00b", {"username": None, "nickname": "invalid"}),
        # 서로게이트는 쿼리에서 U+FFFD 로 바뀌어 닿는다 -- 그래도 invalid 이고 500 이 없다(R4-4).
        ("/auth/availability?nickname=%ED%A0%80", {"username": None, "nickname": "invalid"}),
        ("/auth/availability?username=%ED%A0%80", {"username": "invalid", "nickname": None}),
        # 10만 자는 httpx 가 URL 길이 상한(65536)으로 클라이언트에서 거부한다 -- 닿을 수 있는 최대에 가깝게.
        ("/auth/availability?nickname=" + "x" * 60_000, {"username": None, "nickname": "invalid"}),
        ("/auth/availability?username=" + "x" * 60_000, {"username": "invalid", "nickname": None}),
    ],
)
def test_weird_query_values_are_invalid_never_500(client, path: str, expected: dict) -> None:
    resp = client.get(path)

    assert resp.status_code == 200
    assert resp.json() == expected


def test_raw_lone_surrogate_string_is_invalid_without_touching_db() -> None:
    """R4-4 -- 짝 없는 서로게이트는 쿼리로 서버에 닿지 않는다(TestClient 도 `UnicodeEncodeError`).
    원시 문자열을 판정 함수에 직접 넣는다 -- 기대는 `invalid` 이고 DB 세션은 쓰이지 않는다."""
    from app.auth.routes import _availability

    class _NoDb:
        def execute(self, *_a, **_k):  # pragma: no cover - 불리면 실패
            raise AssertionError("형식 위반 입력이 DB 에 갔다")

    assert _availability(_NoDb(), "\ud800", "nickname") == "invalid"  # type: ignore[arg-type]
    assert _availability(_NoDb(), "ab\ud800cd", "nickname") == "invalid"  # type: ignore[arg-type]
    assert _availability(_NoDb(), "ab\ud800cd", "username") == "invalid"  # type: ignore[arg-type]
    assert _availability(_NoDb(), "a\x00b", "nickname") == "invalid"  # type: ignore[arg-type]


def test_lookup_writes_nothing(seeded, db_session) -> None:
    before = _counts(db_session)

    seeded.get("/auth/availability", params={"username": "taken_user", "nickname": "민지"})
    seeded.get("/auth/availability", params={"username": "free_name", "nickname": "새닉네임"})
    seeded.get("/auth/availability", params={"nickname": "ㅋ"})
    seeded.get("/auth/availability")

    assert _counts(db_session) == before


def test_response_is_no_store_and_keys_are_exact(seeded) -> None:
    resp = seeded.get("/auth/availability", params={"username": "taken_user", "nickname": "민지"})

    assert resp.headers["cache-control"] == "no-store"
    assert set(resp.json()) == {"username", "nickname"}


def test_get_with_foreign_origin_is_not_403(seeded) -> None:
    resp = seeded.get(
        "/auth/availability",
        params={"username": "free_name"},
        headers={"Origin": "https://evil.example"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"username": "available", "nickname": None}
