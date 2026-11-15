"""Refs: P9b-auth U9 CR-007 D18 결정 10 · 01-plan 개정 3 "API 계약"·"닉네임 규칙" -- 가입 닉네임 HTTP 테스트.

`TestClient(create_app())` + `get_session` 오버라이드로 U1 롤백 픽스처(`db_session`)를 주입한다
(`test_auth_api.py` 와 같은 방식) -- DB 에 행이 남지 않는다. 값(정규화 결과·경계·코드·순서)은
전부 값으로 단언한다. 실 PostgreSQL 이 필요하다(`dbtest`).
"""

from __future__ import annotations

import json
import unicodedata

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_session
from app.db.models import AgentTrace, Person, PersonAlias, User
from app.main import create_app

pytestmark = pytest.mark.dbtest

PW = "test-only-pass-1234"
NUL = "\x00"
LONE_SURROGATE = "\ud800"


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


def _post(client: TestClient, payload: object):
    """`json.dumps`(ASCII 이스케이프)로 직렬화 -- 짝 없는 서로게이트도 서버에 닿게 한다."""
    return client.post(
        "/auth/signup",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )


def _signup(client: TestClient, username: str, nickname: object, password: str = PW):
    return _post(client, {"username": username, "password": password, "nickname": nickname})


def _count(db_session, model) -> int:
    return db_session.scalar(select(func.count()).select_from(model))


# --- 201 응답과 저장 값 ------------------------------------------------------------


def test_signup_201_has_exactly_id_username_nickname(client) -> None:
    resp = _signup(client, "nickuser1", "민지")

    assert resp.status_code == 201
    body = resp.json()
    assert set(body) == {"id", "username", "nickname"}
    assert body["username"] == "nickuser1"
    assert body["nickname"] == "민지"


def test_login_and_me_return_the_same_nickname(client) -> None:
    created = _signup(client, "nickuser2", "심사위원").json()
    client.cookies.clear()

    login = client.post("/auth/login", json={"username": "nickuser2", "password": PW})
    me = client.get("/auth/me")

    assert login.status_code == 200
    assert login.json() == {"id": created["id"], "username": "nickuser2", "nickname": "심사위원"}
    assert me.status_code == 200
    assert me.json() == {"id": created["id"], "username": "nickuser2", "nickname": "심사위원"}


def test_login_ignores_a_nickname_in_the_body(client) -> None:
    _signup(client, "nickuser3", "민지")
    client.cookies.clear()

    resp = client.post(
        "/auth/login", json={"username": "nickuser3", "password": PW, "nickname": "다른이름"}
    )

    assert resp.status_code == 200
    assert resp.json()["nickname"] == "민지"


@pytest.mark.parametrize(
    ("raw", "stored"),
    [
        (" 민지 ", "민지"),
        ("\t민지\n", "민지"),
        (unicodedata.normalize("NFD", "민지"), "민지"),
        ("Demo", "demo"),
        ("DEMO_01", "demo_01"),
        ("민지ABC", "민지abc"),
    ],
)
def test_nickname_is_normalized_nfc_strip_lower(client, db_session, raw: str, stored: str) -> None:
    resp = _signup(client, "normuser", raw)

    assert resp.status_code == 201
    assert resp.json()["nickname"] == stored
    assert db_session.scalar(select(User.nickname).where(User.username == "normuser")) == stored
    # NFD 입력이 NFC 로 저장됐는지 코드포인트로 본다.
    assert unicodedata.is_normalized("NFC", stored)


# --- 경계 ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nickname",
    ["가나", "가" * 20, "ab", "a" * 20, "a_", "12"],
)
def test_nickname_length_boundaries_accepted(client, nickname: str) -> None:
    assert _signup(client, "edgeok", nickname).status_code == 201


@pytest.mark.parametrize("nickname", ["가", "a", "_", "가" * 21, "a" * 21])
def test_nickname_length_boundaries_rejected(client, db_session, nickname: str) -> None:
    before = _count(db_session, User)

    resp = _signup(client, "edgebad", nickname)

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_nickname"}}
    assert _count(db_session, User) == before


# --- 거부 목록 ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "nickname",
    [
        "ㅋㅋ",  # 자모 단독
        "ㅏㅣ",
        "민 지",  # 가운데 일반 공백
        "민 지",  # NBSP
        "민　지",  # 전각 공백
        "민지😀",  # 이모지
        "民智",  # 한자
        "min-ji",
        "min.ji",
        "   ",
        "",
        "​민지",  # 제로폭 공백(R4-1)
        "민지​",
    ],
)
def test_forbidden_nicknames_are_422_invalid_nickname(client, db_session, nickname: str) -> None:
    before = _count(db_session, User)

    resp = _signup(client, "rejuser", nickname)

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_nickname"}}
    assert _count(db_session, User) == before


@pytest.mark.parametrize(
    "nickname",
    [
        NUL,
        "a" + NUL + "b",
        "민\x01지",  # 가운데 제어문자(R4-1)
        "민지\x7f",  # 공백류가 아닌 제어문자(R4-1)
        LONE_SURROGATE,
        "ab" + LONE_SURROGATE + "cd",
        "x" * 100_000,
    ],
)
def test_weird_nickname_strings_are_422_not_500(client, db_session, nickname: str) -> None:
    before = _count(db_session, User)

    resp = _signup(client, "weirduser", nickname)

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_nickname"}}
    assert "Traceback" not in resp.text
    assert _count(db_session, User) == before


def test_leading_trailing_whitespace_control_chars_are_stripped_not_rejected(client) -> None:
    """R4-1 -- `str.strip()` 은 앞뒤 공백류 제어문자(U+001F 등)도 지운다 -> `민지` 로 통과."""
    resp = _signup(client, "stripuser", "\x1f민지")

    assert resp.status_code == 201
    assert resp.json()["nickname"] == "민지"


@pytest.mark.parametrize("bad", [123, None, True, 1.5, [], {}, ["a"], {"a": 1}])
def test_nickname_wrong_type_is_default_422_list_without_input_echo(
    client, db_session, bad: object
) -> None:
    before = _count(db_session, User)

    resp = _signup(client, "typeuser", bad)

    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert isinstance(detail, list)
    assert all("input" not in e and "ctx" not in e for e in detail)
    assert _count(db_session, User) == before


def test_nickname_missing_is_default_422_list(client, db_session) -> None:
    before = _count(db_session, User)

    resp = _post(client, {"username": "missuser", "password": PW})

    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert isinstance(detail, list)
    assert [e["loc"] for e in detail] == [["body", "nickname"]]
    assert _count(db_session, User) == before


# --- 409 ----------------------------------------------------------------------------


def test_same_nickname_other_username_is_409_nickname_taken(client, db_session) -> None:
    assert _signup(client, "firstuser", "민지").status_code == 201
    before = _count(db_session, User)

    resp = _signup(client, "seconduser", "민지")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "nickname_taken"}}
    assert _count(db_session, User) == before


def test_nickname_differing_only_by_case_is_409_nickname_taken(client) -> None:
    assert _signup(client, "caseuser1", "Demo").status_code == 201

    resp = _signup(client, "caseuser2", "DEMO")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "nickname_taken"}}


def test_normalized_equal_nickname_is_409(client) -> None:
    """공백·NFD 가 달라도 정규화 값이 같으면 중복이다."""
    assert _signup(client, "normuser1", "민지").status_code == 201

    resp = _signup(client, "normuser2", " " + unicodedata.normalize("NFD", "민지") + " ")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "nickname_taken"}}


def test_same_username_new_nickname_is_409_username_taken(client) -> None:
    assert _signup(client, "dupname", "첫번째").status_code == 201

    resp = _signup(client, "dupname", "두번째")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "username_taken"}}


def test_both_taken_reports_username_taken_first(client) -> None:
    assert _signup(client, "bothuser", "겹침").status_code == 201

    resp = _signup(client, "bothuser", "겹침")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "username_taken"}}


def test_my_nickname_may_equal_another_accounts_username(client) -> None:
    """결정 Z -- 이름 공간이 따로다."""
    assert _signup(client, "taken_id", "첫닉네임").status_code == 201

    resp = _signup(client, "otheruser", "taken_id")

    assert resp.status_code == 201
    assert resp.json()["nickname"] == "taken_id"


def test_my_nickname_may_equal_my_own_username(client) -> None:
    resp = _signup(client, "selfsame", "selfsame")

    assert resp.status_code == 201
    assert resp.json()["username"] == "selfsame"
    assert resp.json()["nickname"] == "selfsame"


# --- 경합: 사전 조회를 우회해 INSERT 충돌을 일으킨다 -----------------------------------


def test_race_nickname_collision_maps_to_nickname_taken(client, monkeypatch, db_session) -> None:
    assert _signup(client, "raceuser1", "경합닉").status_code == 201
    monkeypatch.setattr("app.auth.routes._exists", lambda *_a, **_k: False)
    before = _count(db_session, User)

    resp = _signup(client, "raceuser2", "경합닉")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "nickname_taken"}}
    assert _count(db_session, User) == before


def test_race_username_collision_maps_to_username_taken(client, monkeypatch, db_session) -> None:
    assert _signup(client, "raceuser3", "경합닉일") .status_code == 201
    monkeypatch.setattr("app.auth.routes._exists", lambda *_a, **_k: False)
    before = _count(db_session, User)

    resp = _signup(client, "raceuser3", "경합닉이")

    assert resp.status_code == 409
    assert resp.json() == {"detail": {"code": "username_taken"}}
    assert _count(db_session, User) == before


def test_race_unknown_constraint_is_not_hidden_as_409(client, monkeypatch) -> None:
    """다른 제약 위반은 409 로 숨기지 않고 다시 올린다(500)."""
    import app.auth.routes as routes

    monkeypatch.setattr(routes, "_CONSTRAINT_CODES", {})
    assert _signup(client, "raceuser4", "경합사").status_code == 201
    monkeypatch.setattr(routes, "_exists", lambda *_a, **_k: False)

    resp = _signup(client, "raceuser5", "경합사")

    assert resp.status_code == 500


# --- 검사 순서 ----------------------------------------------------------------------


def test_422_order_username_then_password_then_nickname(client) -> None:
    both_bad = _post(client, {"username": "x", "password": PW, "nickname": "ㅋ"})
    assert both_bad.json() == {"detail": {"code": "invalid_username"}}

    pw_and_nick = _post(client, {"username": "orderuser", "password": "short", "nickname": "ㅋ"})
    assert pw_and_nick.json() == {"detail": {"code": "invalid_password"}}

    nick_only = _post(client, {"username": "orderuser", "password": PW, "nickname": "ㅋ"})
    assert nick_only.json() == {"detail": {"code": "invalid_nickname"}}


# --- 원칙7·9: 닉네임이 인물·trace 로 가지 않는다 ----------------------------------------


def test_signup_creates_no_person_alias_or_trace_rows(client, db_session) -> None:
    before = (
        _count(db_session, Person),
        _count(db_session, PersonAlias),
        _count(db_session, AgentTrace),
    )

    assert _signup(client, "purityuser", "순수닉네임").status_code == 201

    after = (
        _count(db_session, Person),
        _count(db_session, PersonAlias),
        _count(db_session, AgentTrace),
    )
    assert after == before


def test_422_body_never_echoes_the_password(client) -> None:
    secret = "never-echo-me-1234"
    resp = _post(client, {"username": "echouser", "password": secret, "nickname": "ㅋ"})

    assert resp.status_code == 422
    assert secret not in resp.text
