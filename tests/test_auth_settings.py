"""Refs: P9b-auth U2 D18 결정 A·B·E·F -- 인증 설정값·쿠키 이름 함수 단위 테스트(DB 불필요).

계약 값(7일·길이 경계·쿠키 이름)을 값으로 단언한다.
"""

from __future__ import annotations

import pytest

from app import settings
from app.auth.sessions import cookie_name, hash_token
from app.tools.types import InvalidValue


def test_auth_constants_match_the_plan() -> None:
    assert settings.AUTH_SESSION_DAYS == 7  # 결정 E
    assert settings.PASSWORD_MIN_LEN == 8 and settings.PASSWORD_MAX_LEN == 128  # 결정 B
    assert settings.USERNAME_PATTERN == r"[a-z0-9_]{3,20}"  # 결정 A
    assert settings.AUTH_COOKIE_NAME_SECURE == "__Host-rel_session"  # 결정 F
    assert settings.AUTH_COOKIE_NAME_PLAIN == "rel_session"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(None, True), ("", True), ("1", True), ("true", True), ("0", False), ("false", False)],
)
def test_auth_cookie_secure_values(raw: str | None, expected: bool) -> None:
    env = {} if raw is None else {"AUTH_COOKIE_SECURE": raw}
    assert settings.auth_cookie_secure(env) is expected


@pytest.mark.parametrize("raw", ["yes", "2", "False", "off"])
def test_auth_cookie_secure_rejects_unknown_values(raw: str) -> None:
    """조용히 한쪽으로 가지 않는다(원칙8)."""
    with pytest.raises(InvalidValue):
        settings.auth_cookie_secure({"AUTH_COOKIE_SECURE": raw})


def test_auth_cookie_secure_reads_os_environ_when_env_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "0")
    assert settings.auth_cookie_secure() is False
    monkeypatch.delenv("AUTH_COOKIE_SECURE")
    assert settings.auth_cookie_secure() is True


def test_cookie_name_follows_secure_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    assert cookie_name(True) == "__Host-rel_session"
    assert cookie_name(False) == "rel_session"
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "0")
    assert cookie_name() == "rel_session"
    monkeypatch.delenv("AUTH_COOKIE_SECURE")
    assert cookie_name() == "__Host-rel_session"


def test_hash_token_is_sha256_hex() -> None:
    import hashlib

    assert hash_token("abc") == hashlib.sha256(b"abc").hexdigest()
    assert len(hash_token("abc")) == 64
