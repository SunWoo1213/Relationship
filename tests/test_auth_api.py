"""Refs: P9b-auth U2 D18 CR-006 결정 A·B·E·F·G F-3 F-7 -- `/auth/*` HTTP 테스트.

`TestClient(create_app())` + `app.dependency_overrides[get_session]` 로 U1 롤백 픽스처
(`db_session`)를 주입한다(P2 결정 13) -- DB 에 행이 남지 않는다. 시계는
`get_auth_now` 오버라이드로 고정한다(만료 경계).

**TestClient 와 Secure 쿠키(03-log 판단)**: 기본값(`AUTH_COOKIE_SECURE` 켜짐)에서는 쿠키가
`Secure` 라 `http://testserver` 로는 다시 보내지 않는다 -> 기본 클라이언트는
`base_url="https://testserver"` 로 만들고(실제 운영과 같은 조건), "끔" 경로만
`AUTH_COOKIE_SECURE=0` + `http://testserver` 로 따로 본다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
테스트가 쓰는 아이디·비밀번호는 전부 시험용 문자열이다. 비밀번호를 단언 메시지에 넣지 않는다.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_embedder, get_proposer, get_session
from app.auth.deps import get_auth_now
from app.auth.passwords import parse_hash
from app.db.models import (
    AgentTrace,
    AuthSession,
    Event,
    PendingQuestion,
    Person,
    PushSubscription,
    User,
)
from app.main import create_app

pytestmark = pytest.mark.dbtest

PW = "test-only-pass-1234"
T0 = datetime(2026, 11, 16, 9, 0, 0, tzinfo=timezone.utc)
SECURE_NAME = "__Host-rel_session"
PLAIN_NAME = "rel_session"


@pytest.fixture(autouse=True)
def _default_cookie_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """바깥 환경의 `AUTH_COOKIE_SECURE` 가 새어 들어오지 않게 기본(켜짐)으로 맞춘다."""
    monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)


@pytest.fixture()
def app_(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    return app


@pytest.fixture()
def client(app_) -> TestClient:
    return TestClient(app_, base_url="https://testserver")


def _set_cookie_headers(resp) -> list[str]:
    return resp.headers.get_list("set-cookie")


def _signup(
    client: TestClient,
    username: str = "alice",
    password: str = PW,
    nickname: str | None = None,
):
    # 닉네임 기본값 = 그 호출의 아이디(시험마다 아이디가 달라 닉네임도 겹치지 않는다).
    return client.post(
        "/auth/signup",
        json={
            "username": username,
            "password": password,
            "nickname": nickname if nickname is not None else username,
            "privacy_notice_accepted": True,
        },
    )


# ---------------------------------------------------------------------------
# 가입
# ---------------------------------------------------------------------------


def test_signup_201_body_and_cookie_attributes(client: TestClient) -> None:
    resp = _signup(client)

    assert resp.status_code == 201
    body = resp.json()
    assert set(body) == {"id", "username", "nickname", "notice_required"}
    assert body["username"] == "alice"
    assert len(body["id"]) == 32 and int(body["id"], 16) >= 0  # uuid4 hex(결정 O)

    cookies = _set_cookie_headers(resp)
    assert len(cookies) == 1
    raw = cookies[0]
    low = raw.lower()
    assert raw.startswith(SECURE_NAME + "=")
    assert "httponly" in low
    assert "samesite=lax" in low
    assert "path=/" in low
    assert "secure" in low
    assert "max-age=604800" in low  # 7일(결정 E)
    assert "domain" not in low  # `__Host-` 접두 조건


def test_cookie_name_secure_on_is_host_prefixed_without_domain(client: TestClient) -> None:
    """Secure 켬 -> `__Host-rel_session`, `Domain` 속성 없음(결정 F, R-5)."""
    raw = _set_cookie_headers(_signup(client))[0]
    assert raw.split("=", 1)[0] == SECURE_NAME
    assert "domain" not in raw.lower()


def test_cookie_name_secure_off_is_plain_without_secure_attribute(
    app_, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Secure 끔(로컬 http) -> `rel_session`, `Secure`·`Domain` 없음, `Path=/` 는 그대로."""
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "0")
    http_client = TestClient(app_, base_url="http://testserver")

    resp = _signup(http_client)

    assert resp.status_code == 201
    raw = _set_cookie_headers(resp)[0]
    low = raw.lower()
    assert raw.split("=", 1)[0] == PLAIN_NAME
    assert "secure" not in low
    assert "domain" not in low
    assert "path=/" in low
    assert "httponly" in low and "samesite=lax" in low
    # http 라도 쿠키가 다시 실려 로그인 상태가 유지된다.
    assert http_client.get("/auth/me").status_code == 200


def test_signup_normalizes_username_to_lowercase(client: TestClient) -> None:
    resp = _signup(client, "DemoUser")
    assert resp.status_code == 201
    assert resp.json()["username"] == "demouser"
    client.cookies.clear()
    login = client.post("/auth/login", json={"username": "DEMOUSER", "password": PW})
    assert login.status_code == 200
    assert login.json()["username"] == "demouser"


def test_signup_duplicate_409_username_taken(client: TestClient, db_session) -> None:
    assert _signup(client, "dupuser").status_code == 201
    again = _signup(client, "dupuser")
    assert again.status_code == 409
    assert again.json() == {"detail": {"code": "username_taken"}}
    # 대소문자만 다른 아이디도 같은 계정이다(정규화 뒤 UNIQUE).
    assert _signup(client, "DUPUSER").status_code == 409
    n = db_session.scalar(select(func.count()).select_from(User).where(User.username == "dupuser"))
    assert n == 1


@pytest.mark.parametrize(
    "username",
    ["ab", "a" * 21, "has space", "한글아이디", "bad-name", "name\n", "dot.name", ""],
)
def test_signup_invalid_username_422(client: TestClient, username: str) -> None:
    resp = _signup(client, username)
    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_username"}}


@pytest.mark.parametrize("username", ["abc", "a" * 20, "user_01", "000"])
def test_signup_username_boundaries_accepted(client: TestClient, username: str) -> None:
    """결정 A 의 경계 -- 3자·20자·밑줄·숫자만도 통과."""
    assert _signup(client, username).status_code == 201


@pytest.mark.parametrize("password", ["", "1234567", "x" * 129])
def test_signup_invalid_password_422(client: TestClient, password: str) -> None:
    resp = _signup(client, "pwcheck", password)
    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_password"}}


@pytest.mark.parametrize("password", ["12345678", "x" * 128, "비밀번호팔자이상입니다"])
def test_signup_password_length_boundaries_accepted(client: TestClient, password: str) -> None:
    """결정 B 의 경계 -- 8자·128자(문자 수, 한글 포함)는 통과."""
    assert _signup(client, "pwbound", password).status_code == 201


def test_signup_validation_error_body_does_not_echo_password(client: TestClient) -> None:
    """형식이 어긋나 FastAPI 기본 422 가 나도 본문에 비밀번호가 되돌아 실리지 않는다
    (`/auth` 라우터의 `_NoInputEchoRoute`, D18 지킬 것 3). 가입·로그인·로그아웃 모두."""
    secret = "echo-canary-pass-987"
    cases = (
        ("/auth/signup", {"password": secret}),  # username 누락
        ("/auth/signup", {"username": ["x"], "password": secret}),  # 타입 오류
        ("/auth/login", {"password": secret}),
        ("/auth/login", {"username": ["x"], "password": secret}),
    )
    for path, payload in cases:
        resp = client.post(path, json=payload)
        assert resp.status_code == 422
        assert secret not in resp.text
        assert all(set(e) <= {"loc", "msg", "type"} for e in resp.json()["detail"])
    # 로그아웃: 로그인 뒤 본문 형식 오류(endpoint 가 숫자)도 비밀번호와 무관하게 input 이 없다.
    assert _signup(client, "echolog").status_code == 201
    resp = client.post("/auth/logout", json={"endpoint": 5, "extra": secret})
    assert resp.status_code == 422
    assert secret not in resp.text
    assert all(set(e) <= {"loc", "msg", "type"} for e in resp.json()["detail"])


# ---------------------------------------------------------------------------
# 로그인
# ---------------------------------------------------------------------------


def test_login_200_sets_cookie(client: TestClient) -> None:
    uid = _signup(client, "loginuser").json()["id"]
    client.cookies.clear()

    resp = client.post("/auth/login", json={"username": "loginuser", "password": PW})

    assert resp.status_code == 200
    assert resp.json() == {
        "id": uid,
        "username": "loginuser",
        "nickname": "loginuser",
        "notice_required": False,
    }
    assert _set_cookie_headers(resp)[0].startswith(SECURE_NAME + "=")
    assert client.get("/auth/me").status_code == 200


def test_login_failures_share_one_response_for_unknown_user_and_wrong_password(
    client: TestClient,
) -> None:
    """없는 아이디·틀린 비밀번호·너무 긴 비밀번호가 같은 상태·같은 본문(V2-6)."""
    _signup(client, "realuser")
    client.cookies.clear()

    unknown = client.post("/auth/login", json={"username": "nouser", "password": PW})
    wrong = client.post("/auth/login", json={"username": "realuser", "password": PW + "x"})
    too_long = client.post("/auth/login", json={"username": "realuser", "password": "x" * 129})

    for resp in (unknown, wrong, too_long):
        assert resp.status_code == 401
        assert resp.json() == {"detail": {"code": "invalid_credentials"}}
        assert not _set_cookie_headers(resp)
    assert unknown.content == wrong.content == too_long.content


def test_login_runs_a_hash_verification_even_for_unknown_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """없는 아이디에도 더미 해시 검증을 한 번 돌린다(응답 시간 차 축소, 결정)."""
    import app.auth.routes as auth_routes

    calls: list[str] = []
    real = auth_routes.verify_password

    def spy(password: str, stored: str) -> bool:
        calls.append("verify")
        return real(password, stored)

    monkeypatch.setattr(auth_routes, "verify_password", spy)
    resp = client.post("/auth/login", json={"username": "ghostuser", "password": PW})
    assert resp.status_code == 401
    assert calls == ["verify"]


# ---------------------------------------------------------------------------
# /auth/me · /auth/logout
# ---------------------------------------------------------------------------


def test_me_with_cookie_200_without_401(client: TestClient) -> None:
    created = _signup(client, "meuser").json()
    ok = client.get("/auth/me")
    assert ok.status_code == 200
    assert ok.json() == created

    client.cookies.clear()
    no = client.get("/auth/me")
    assert no.status_code == 401
    assert no.json() == {"detail": {"code": "unauthenticated"}}


def test_me_with_unknown_token_401(client: TestClient) -> None:
    client.cookies.set(SECURE_NAME, "not-a-real-token")
    resp = client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"code": "unauthenticated"}}


def test_logout_without_cookie_401(client: TestClient) -> None:
    """F-3 -- `/auth/logout` 은 예외 경로가 아니다(V2-10)."""
    resp = client.post("/auth/logout")
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"code": "unauthenticated"}}


def test_logout_204_no_body_clears_cookie_and_deletes_row(
    client: TestClient, db_session
) -> None:
    _signup(client, "logoutuser")
    token = client.cookies.get(SECURE_NAME)
    assert token
    before = db_session.scalar(select(func.count()).select_from(AuthSession))

    resp = client.post("/auth/logout", json={"endpoint": "https://push.example/ep1"})

    assert resp.status_code == 204
    assert resp.content == b""
    cleared = _set_cookie_headers(resp)[0]
    low = cleared.lower()
    assert cleared.startswith(SECURE_NAME + "=")
    assert "max-age=0" in low
    assert "path=/" in low
    after = db_session.scalar(select(func.count()).select_from(AuthSession))
    assert after == before - 1

    # 같은 쿠키를 다시 실어도 401(V2-5 -- 행이 남아 있으면 200).
    client.cookies.set(SECURE_NAME, token)
    assert client.get("/auth/me").status_code == 401


def test_logout_without_body_is_accepted(client: TestClient) -> None:
    _signup(client, "nobodylogout")
    resp = client.post("/auth/logout")
    assert resp.status_code == 204


def test_logout_removes_only_that_session(client: TestClient, app_) -> None:
    """로그인은 기기마다 세션을 따로 만든다 -- 한쪽 로그아웃이 다른 쪽을 끊지 않는다."""
    _signup(client, "twodevices")
    other = TestClient(app_, base_url="https://testserver")
    assert other.post("/auth/login", json={"username": "twodevices", "password": PW}).status_code == 200

    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401
    assert other.get("/auth/me").status_code == 200


# ---------------------------------------------------------------------------
# 만료(시계 주입, 경계)
# ---------------------------------------------------------------------------


def test_session_expiry_boundary_is_exclusive_at_seven_days(app_) -> None:
    """가입 시각 T0 -> `expires_at = T0 + 7일`. 그 1초 전은 유효, **같은 순간은 만료**
    (`expires_at > now`). 경계값을 값으로 단언한다."""
    clock = {"now": T0}
    app_.dependency_overrides[get_auth_now] = lambda: (lambda: clock["now"])
    client = TestClient(app_, base_url="https://testserver")
    _signup(client, "expirer")

    clock["now"] = T0 + timedelta(days=7) - timedelta(seconds=1)
    assert client.get("/auth/me").status_code == 200
    clock["now"] = T0 + timedelta(days=7)
    assert client.get("/auth/me").status_code == 401
    clock["now"] = T0 + timedelta(days=7, seconds=1)
    assert client.get("/auth/me").status_code == 401


def test_session_expires_at_uses_configured_days(app_, db_session) -> None:
    clock = {"now": T0}
    app_.dependency_overrides[get_auth_now] = lambda: (lambda: clock["now"])
    client = TestClient(app_, base_url="https://testserver")
    uid = _signup(client, "expiresat").json()["id"]
    row = db_session.scalars(select(AuthSession).where(AuthSession.user_id == uid)).one()
    assert row.expires_at == T0 + timedelta(days=7)


# ---------------------------------------------------------------------------
# 저장 형태(평문·토큰 원문 0)
# ---------------------------------------------------------------------------


def test_password_hash_has_no_plaintext_substring(client: TestClient, db_session) -> None:
    """`users.password_hash` 에 평문(또는 그 일부)이 없고 scrypt 형식이다(D18 지킬 것 1)."""
    plain = "plaintext-canary-pass-4321"
    uid = _signup(client, "hashcheck", plain).json()["id"]
    stored = db_session.scalar(select(User.password_hash).where(User.id == uid))
    assert stored is not None
    assert plain not in stored
    assert plain[:8] not in stored
    assert parse_hash(stored) is not None
    assert stored.startswith("scrypt$16384$8$1$")


def test_token_hash_is_sha256_of_cookie_not_the_cookie(client: TestClient, db_session) -> None:
    """DB 에는 토큰 해시만 -- 쿠키 값과 다르고 `sha256(쿠키)` 와 같다(V2-2)."""
    uid = _signup(client, "tokencheck").json()["id"]
    cookie_value = client.cookies.get(SECURE_NAME)
    assert cookie_value
    stored = db_session.scalar(select(AuthSession.token_hash).where(AuthSession.user_id == uid))
    assert stored != cookie_value
    assert cookie_value not in (stored or "")
    assert stored == hashlib.sha256(cookie_value.encode()).hexdigest()


def test_auth_endpoints_write_no_agent_traces(client: TestClient, db_session) -> None:
    """`/auth/*` 는 판정이 아니라 trace 를 쓰지 않는다(원칙9 절)."""
    before = db_session.scalar(select(func.count()).select_from(AgentTrace))
    _signup(client, "notrace")
    client.post("/auth/logout")
    client.post("/auth/login", json={"username": "notrace", "password": PW})
    client.get("/auth/me")
    client.post("/auth/login", json={"username": "notrace", "password": "wrong-pass-123"})
    assert db_session.scalar(select(func.count()).select_from(AgentTrace)) == before


# ---------------------------------------------------------------------------
# F-7 ② -- 본문 형식: JSON 이 아닌 콘텐츠 타입은 본문으로 해석하지 않는다
# ---------------------------------------------------------------------------

_WATCHED = (Person, Event, PendingQuestion, PushSubscription, AgentTrace)


def _row_counts(db_session) -> dict[str, int]:
    return {
        m.__tablename__: db_session.scalar(select(func.count()).select_from(m)) for m in _WATCHED
    }


_CHAT_JSON = '{"utterance": "김 대리랑 점심 먹었어"}'
_PUSH_JSON = (
    '{"endpoint": "https://push.example/ep-text-plain", '
    '"keys": {"p256dh": "AAAA", "auth": "BBBB"}}'
)
_ANSWER_JSON = '{"answer": "예"}'


@pytest.mark.parametrize(
    ("path", "json_text"),
    [
        ("/chat", _CHAT_JSON),
        ("/answers/1", _ANSWER_JSON),
        ("/push/subscriptions", _PUSH_JSON),
    ],
)
def test_non_json_content_types_are_rejected_and_write_nothing(
    app_, db_session, path: str, json_text: str
) -> None:
    """로그인 쿠키를 가진 채 `text/plain`(JSON 모양 본문)·폼으로 보내면 4xx(422/415)이고
    관련 테이블 행 수가 불변이다(V2-9). 이 단위에서 라우트는 아직 로그인을 요구하지 않지만
    쿠키를 붙여 두어 U3b 뒤에도 401 이 아닌 **본문 거부**를 본다."""
    app_.dependency_overrides[get_proposer] = lambda: None
    app_.dependency_overrides[get_embedder] = lambda: None
    client = TestClient(app_, base_url="https://testserver")
    assert _signup(client, "formattack").status_code == 201
    before = _row_counts(db_session)

    as_text = client.post(path, content=json_text, headers={"Content-Type": "text/plain"})
    as_form = client.post(
        path,
        content="utterance=x&answer=%EC%98%88&endpoint=https%3A%2F%2Fpush.example%2Fx",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert as_text.status_code in (415, 422)
    assert as_form.status_code in (415, 422)
    assert _row_counts(db_session) == before


def test_answers_route_with_json_content_type_is_reached_control(app_) -> None:
    """대조군 -- 같은 `/answers/1` 에 JSON 콘텐츠 타입이면 본문이 해석돼 라우트에 닿는다
    (없는 질문이라 404). 위 4xx 가 콘텐츠 타입 때문임을 보인다."""
    client = TestClient(app_, base_url="https://testserver")
    _signup(client, "controluser")
    resp = client.post("/answers/1", content=_ANSWER_JSON, headers={"Content-Type": "application/json"})
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "path",
    ["/chat", "/answers/1", "/push/subscriptions", "/auth/signup", "/auth/login"],
)
def test_json_shaped_body_without_content_type_is_rejected_and_writes_nothing(
    app_, db_session, path: str
) -> None:
    """R-1 -- `Content-Type` 헤더가 **아예 없는** JSON 모양 본문(다른 사이트가 프리플라이트 없이
    보낼 수 있는 요청)도 4xx 이고 행 수 불변. 로그인 쿠키를 가진 채로."""
    app_.dependency_overrides[get_proposer] = lambda: None
    app_.dependency_overrides[get_embedder] = lambda: None
    client = TestClient(app_, base_url="https://testserver")
    assert _signup(client, "noctype").status_code == 201
    before = _row_counts(db_session)
    users_before = db_session.scalar(select(func.count()).select_from(User))

    body = (
        '{"utterance": "x", "answer": "예", "username": "noctype2", "password": "test-only-pass-1234", '
        '"endpoint": "https://push.example/ep", "keys": {"p256dh": "AAAA", "auth": "BBBB"}}'
    )
    resp = client.post(path, content=body)  # str 본문 -- httpx 는 Content-Type 을 붙이지 않는다

    assert "content-type" not in {k.lower() for k in resp.request.headers}
    assert 400 <= resp.status_code < 500
    assert _row_counts(db_session) == before
    assert db_session.scalar(select(func.count()).select_from(User)) == users_before


# ---------------------------------------------------------------------------
# 리뷰 F-1·F-2 -- 로그인 없이 보낼 수 있는 이상 입력에 500 이 없다
# ---------------------------------------------------------------------------

NUL = "\x00"
LONE_SURROGATE = chr(0xD800)


def _post_json(client: TestClient, path: str, payload: object):
    """`json.dumps`(ASCII 이스케이프)로 직접 직렬화한다 -- httpx 의 `json=` 은 짝 없는
    서로게이트를 UTF-8 로 인코딩하지 못해 클라이언트 쪽에서 터진다."""
    import json as _json

    return client.post(path, content=_json.dumps(payload), headers={"Content-Type": "application/json"})


@pytest.mark.parametrize(
    "username",
    [
        "ab" + NUL + "cd",
        NUL,
        "ab" + LONE_SURROGATE + "cd",
        "a" * 21,
        "a" * 100_000,
        "",
        "한글아이디",
        "has space",
        "name\n",
    ],
)
def test_login_with_malformed_username_is_the_same_401_and_still_runs_one_hash(
    app_, monkeypatch: pytest.MonkeyPatch, username: str
) -> None:
    """F-1 -- 결정 A 형식에 안 맞는 아이디도 없는 아이디와 같은 401 `invalid_credentials` 이고
    (DB 에 묻지 않아 NUL 의 `DataError` 500 이 없다), 타이밍 평준화를 위한 더미 해시 검증이 한 번 돈다."""
    import app.auth.routes as auth_routes

    client = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)
    unknown = _post_json(client, "/auth/login", {"username": "nouserxx", "password": PW})

    calls: list[str] = []
    real = auth_routes.verify_password

    def spy(password: str, stored: str) -> bool:
        calls.append(stored)
        return real(password, stored)

    monkeypatch.setattr(auth_routes, "verify_password", spy)
    resp = _post_json(client, "/auth/login", {"username": username, "password": PW})

    assert resp.status_code == 401
    assert resp.content == unknown.content
    assert resp.json() == {"detail": {"code": "invalid_credentials"}}
    assert not _set_cookie_headers(resp)
    assert len(calls) == 1
    assert calls[0] == auth_routes.dummy_hash()


def test_signup_with_unencodable_password_is_422_and_creates_no_user(app_, db_session) -> None:
    """F-2 -- 짝 없는 서로게이트가 든 비밀번호(UTF-8 로 못 바꿈)는 계약 안의 422
    `invalid_password`, `users` 행 수 불변(500 아님)."""
    client = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)
    before = db_session.scalar(select(func.count()).select_from(User))

    resp = _post_json(client, "/auth/signup", {"username": "surro1", "password": LONE_SURROGATE + "aaaaaaaaaa", "nickname": "surro1", "privacy_notice_accepted": True})

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_password"}}
    assert db_session.scalar(select(func.count()).select_from(User)) == before


def test_login_with_unencodable_password_is_the_same_401(app_) -> None:
    """F-2 -- 로그인 쪽도 의도된 경로: 같은 401(우연한 `except ValueError` 에 기대지 않고
    `verify_password` 가 명시적으로 False)."""
    client = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)
    _signup(client, "surrologin")
    client.cookies.clear()

    resp = _post_json(client, "/auth/login", {"username": "surrologin", "password": LONE_SURROGATE + "aaaaaaaaaa"})

    assert resp.status_code == 401
    assert resp.json() == {"detail": {"code": "invalid_credentials"}}


def test_login_with_over_128_chars_password_skips_the_hash(
    app_, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-3 -- 128자 초과면 해시를 돌리지 않는다(`verify_password` 호출 0), 같은 401."""
    import app.auth.routes as auth_routes

    client = TestClient(app_, base_url="https://testserver")
    _signup(client, "longpwuser")
    client.cookies.clear()
    calls: list[int] = []
    monkeypatch.setattr(auth_routes, "verify_password", lambda p, s: calls.append(1) or True)

    resp = client.post("/auth/login", json={"username": "longpwuser", "password": "x" * 129})

    assert resp.status_code == 401
    assert resp.json() == {"detail": {"code": "invalid_credentials"}}
    assert calls == []


_BAD_STRINGS = [
    NUL,
    "a" + NUL + "b",
    LONE_SURROGATE,
    "ab" + LONE_SURROGATE + "cdefghij",
    "x" * 100_000,
    "",
]
_BAD_TYPES = [None, 123, True, 1.5, [], {}, ["a"], {"a": 1}]


@pytest.mark.parametrize("path", ["/auth/signup", "/auth/login"])
@pytest.mark.parametrize("field", ["username", "password"])
def test_auth_string_inputs_never_cause_a_server_error(app_, db_session, path: str, field: str) -> None:
    """NUL·짝 없는 서로게이트·아주 긴 값·빈 값·다른 타입 -- 어느 필드에 넣어도 500 이 없다(4xx)."""
    client = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)
    users_before = db_session.scalar(select(func.count()).select_from(User))
    good = {"username": "okname01", "password": PW, "nickname": "okname01"}
    statuses = []
    for value in [*_BAD_STRINGS, *_BAD_TYPES]:
        payload = {**good, field: value}
        resp = _post_json(client, path, payload)
        statuses.append(resp.status_code)
        assert 400 <= resp.status_code < 500, (path, field, type(value).__name__)
        assert "Traceback" not in resp.text
    assert all(s in (401, 422) for s in statuses)
    assert db_session.scalar(select(func.count()).select_from(User)) == users_before


@pytest.mark.parametrize("value", [*_BAD_STRINGS, *_BAD_TYPES])
def test_logout_endpoint_input_never_causes_a_server_error(app_, value: object) -> None:
    """로그아웃 `endpoint` 에 이상 값 -- 204(문자열)나 422(다른 타입)이고 500 이 없다."""
    client = TestClient(app_, base_url="https://testserver", raise_server_exceptions=False)
    assert _signup(client, "logoutfuzz").status_code == 201

    resp = _post_json(client, "/auth/logout", {"endpoint": value})

    assert resp.status_code in (204, 422)


def test_logout_clear_cookie_keeps_secure_and_plain_name_when_off(
    app_, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-2 -- 삭제 쿠키도 켬에서는 `__Host-` 이름·`Secure`·`Path=/`(없으면 브라우저가 버린다),
    끔에서는 `rel_session` 이름·`Secure` 없음."""
    on = TestClient(app_, base_url="https://testserver")
    _signup(on, "clearon")
    raw_on = _set_cookie_headers(on.post("/auth/logout"))[0]
    assert raw_on.startswith(SECURE_NAME + "=")
    assert "secure" in raw_on.lower() and "path=/" in raw_on.lower()
    assert "domain" not in raw_on.lower()

    monkeypatch.setenv("AUTH_COOKIE_SECURE", "0")
    off = TestClient(app_, base_url="http://testserver")
    _signup(off, "clearoff")
    raw_off = _set_cookie_headers(off.post("/auth/logout"))[0]
    assert raw_off.startswith(PLAIN_NAME + "=")
    assert "secure" not in raw_off.lower()
    assert "max-age=0" in raw_off.lower() and "path=/" in raw_off.lower()
