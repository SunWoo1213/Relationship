"""Refs: P9b-auth U3a D18 CR-006 F-5 R2-2 -- `tests/auth_helpers.py` 자체 시험.

도우미가 약속한 값(사용자 id·세션 행 해시·쿠키 이름·커밋 뒤 정리)을 값으로 단언한다.
토큰·쿠키 값은 단언 메시지에 넣지 않는다(D18 지킬 것 3).
실 PostgreSQL(`dbtest`)이 필요하다.
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.auth.passwords import verify_password
from app.auth.sessions import cookie_name, hash_token
from app.db.models import AuthSession, User
from app.main import create_app
from tests.auth_helpers import (
    NO_LOGIN_HASH,
    committed_login,
    logged_in_client,
    make_ctx,
    make_user,
)

pytestmark = pytest.mark.dbtest


@pytest.fixture(autouse=True)
def _default_cookie_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """바깥 환경의 `AUTH_COOKIE_SECURE` 가 새어 들어오지 않게 기본(켜짐)으로 맞춘다."""
    monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)


def _cookie_names(client) -> list[str]:
    return sorted(cookie.name for cookie in client.cookies.jar)


def _has_cookie(client) -> bool:
    return bool(client.cookies.get(cookie_name()))


def _compare_cookie_with_row(client, row: AuthSession) -> tuple[bool, bool]:
    """(해시 일치, 원문 저장 여부). 토큰 원문은 이 함수 안에만 있다."""
    token = client.cookies.get(cookie_name()) or ""
    return row.token_hash == hash_token(token), row.token_hash == token


def _session_row_for_cookie(session: Session, client) -> AuthSession:
    token = client.cookies.get(cookie_name()) or ""
    return session.execute(
        select(AuthSession).where(AuthSession.token_hash == hash_token(token))
    ).scalar_one()


def _count(session: Session, model, *where) -> int:
    return session.execute(select(func.count()).select_from(model).where(*where)).scalar_one()


def test_make_user_uses_given_id_and_is_idempotent(db_session) -> None:
    first = make_user(db_session)
    assert first.id == "local"
    again = make_user(db_session, "local", username="다른이름")
    assert again is first
    assert _count(db_session, User, User.id == "local") == 1


def test_make_user_custom_id_and_username(db_session) -> None:
    user = make_user(db_session, "u-helper-7", username="helper-seven")
    assert (user.id, user.username) == ("u-helper-7", "helper-seven")


def test_make_user_password_cannot_log_in(db_session) -> None:
    user = make_user(db_session, "u-helper-nologin")
    assert user.password_hash == NO_LOGIN_HASH
    assert verify_password("아무 비밀번호", user.password_hash) is False


def test_make_ctx_sets_user_id_explicitly(db_session) -> None:
    default = make_ctx(db_session)
    assert default.user_id == "local"
    assert default.session_id == "test-session"
    other = make_ctx(db_session, "u-other", session_id="s-9", embedder=None)
    assert (other.user_id, other.session_id) == ("u-other", "s-9")


def test_logged_in_client_session_row_matches_cookie(db_session) -> None:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    client = logged_in_client(app, db_session, "u-helper-1", username="helper-one")

    assert _has_cookie(client), "쿠키가 붙지 않았다"
    rows = db_session.execute(
        select(AuthSession).where(AuthSession.user_id == "u-helper-1")
    ).scalars().all()
    assert len(rows) == 1
    # 토큰 값은 이 프레임의 지역변수·단언 식에 두지 않는다(`pytest -l` 에도 안 찍히게, D18 지킬 것 3).
    hash_matches, stored_raw = _compare_cookie_with_row(client, rows[0])
    assert hash_matches, "세션 행의 token_hash 가 쿠키 값의 sha256 과 다르다"
    assert not stored_raw, "토큰 원문이 DB 에 저장됐다"

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"id": "u-helper-1", "username": "helper-one", "nickname": "helper-one"}


def test_logged_in_client_default_user_is_local(db_session) -> None:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    client = logged_in_client(app, db_session)
    assert client.get("/auth/me").json()["id"] == "local"


def test_logged_in_client_two_calls_same_user_share_one_user_row(db_session) -> None:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    logged_in_client(app, db_session)
    logged_in_client(app, db_session)
    assert _count(db_session, User, User.id == "local") == 1
    assert _count(db_session, AuthSession, AuthSession.user_id == "local") == 2


def test_logged_in_client_cookie_name_follows_setting(
    db_session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """쿠키 이름을 하드코딩하지 않는다 -- 설정이 바뀌면 이름도 바뀐다(R2-2 ③)."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    secure_client = logged_in_client(app, db_session, "u-helper-2", username="helper-two")
    # 쿠키 값(토큰)이 실패 출력에 찍히지 않도록 이름만 모아 비교한다.
    assert _cookie_names(secure_client) == ["__Host-rel_session"]

    monkeypatch.setenv("AUTH_COOKIE_SECURE", "0")
    plain_client = logged_in_client(
        app, db_session, "u-helper-3", username="helper-three", base_url="http://testserver"
    )
    assert _cookie_names(plain_client) == ["rel_session"]
    assert plain_client.get("/auth/me").json()["id"] == "u-helper-3"


def test_logged_in_client_without_cookie_is_401(db_session) -> None:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    client = logged_in_client(app, db_session)
    client.cookies.clear()
    assert client.get("/auth/me").status_code == 401


def test_logged_in_client_factory_commits_rows(db_engine) -> None:
    """세션 팩토리 경로 -- 별도 세션에서 커밋한다(정리는 호출자 몫이라 이 시험이 지운다)."""
    app = create_app()

    def factory() -> Session:
        return Session(bind=db_engine)

    client = logged_in_client(app, factory, "u-helper-factory", username="helper-factory")
    try:
        with factory() as check:
            assert _count(check, User, User.id == "u-helper-factory") == 1
            assert _count(check, AuthSession, AuthSession.user_id == "u-helper-factory") == 1
        assert client.cookies.get(cookie_name())
    finally:
        with factory() as cleanup:
            cleanup.query(AuthSession).filter(AuthSession.user_id == "u-helper-factory").delete()
            cleanup.query(User).filter(User.id == "u-helper-factory").delete()
            cleanup.commit()


def test_committed_login_commits_then_cleans_up(db_engine) -> None:
    app = create_app()

    def factory() -> Session:
        return Session(bind=db_engine)

    with committed_login(app, factory, user_id="u-helper-commit") as client:
        with factory() as check:
            user = check.get(User, "u-helper-commit")
            assert user is not None
            assert user.username.startswith("helper-")
            assert _count(check, AuthSession, AuthSession.user_id == "u-helper-commit") == 1
        assert client.cookies.get(cookie_name())

    with factory() as after:
        assert after.get(User, "u-helper-commit") is None
        assert _count(after, AuthSession, AuthSession.user_id == "u-helper-commit") == 0


def test_committed_login_cleans_up_even_when_body_raises(db_engine) -> None:
    app = create_app()

    def factory() -> Session:
        return Session(bind=db_engine)

    with pytest.raises(RuntimeError, match="본문 실패"):
        with committed_login(app, factory, user_id="u-helper-boom"):
            raise RuntimeError("본문 실패")

    with factory() as after:
        assert after.get(User, "u-helper-boom") is None
        assert _count(after, AuthSession, AuthSession.user_id == "u-helper-boom") == 0


def test_committed_login_default_ids_differ_per_call(db_engine) -> None:
    """`user_id`·`username` 을 생략하면 호출마다 다른 값이라 재실행에서 UNIQUE 가 안 부딪힌다."""
    app = create_app()

    def factory() -> Session:
        return Session(bind=db_engine)

    seen: list[tuple[str, str]] = []
    for _ in range(2):
        with committed_login(app, factory) as client:
            with factory() as check:
                row = _session_row_for_cookie(check, client)
                user = check.get(User, row.user_id)
                assert user is not None
                seen.append((user.id, user.username))
    assert seen[0][0] != seen[1][0]
    assert seen[0][1] != seen[1][1]
