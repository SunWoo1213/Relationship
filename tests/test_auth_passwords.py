"""Refs: P9b-auth U2 D18 결정 C -- 비밀번호 해시·검증 단위 테스트(DB 불필요).

테스트가 쓰는 비밀번호는 전부 명백한 시험용 문자열이다(실제 비밀 아님). 해시·평문을
`assert` 메시지에 끌어넣지 않는다(실패 출력에 값이 찍히지 않게).
"""

from __future__ import annotations

import base64

import pytest

from app.auth import passwords
from app.auth.passwords import dummy_hash, hash_password, parse_hash, verify_password

PLAIN = "test-only-pass-1234"


def test_hash_differs_from_plaintext_and_has_no_plaintext_substring() -> None:
    stored = hash_password(PLAIN)
    assert stored != PLAIN
    assert PLAIN not in stored


def test_same_password_hashed_twice_differs_by_salt() -> None:
    a, b = hash_password(PLAIN), hash_password(PLAIN)
    assert a != b
    # 솔트(필드 4)가 서로 다르다.
    assert a.split("$")[4] != b.split("$")[4]


def test_format_carries_parameters_and_sizes() -> None:
    """`scrypt$16384$8$1$<salt_b64>$<hash_b64>` -- 결정 C 의 값을 값으로 단언한다."""
    parts = hash_password(PLAIN).split("$")
    assert parts[:4] == ["scrypt", "16384", "8", "1"]
    assert len(parts) == 6
    assert len(base64.b64decode(parts[4])) == 16  # 솔트 16B
    assert len(base64.b64decode(parts[5])) == 32  # dklen 32


def test_parse_hash_returns_components() -> None:
    parsed = parse_hash(hash_password(PLAIN))
    assert parsed is not None
    n, r, p, salt, digest = parsed
    assert (n, r, p) == (16384, 8, 1)
    assert len(salt) == 16 and len(digest) == 32


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "plain",
        "scrypt$16384$8$1$onlyfive",
        "bcrypt$16384$8$1$AAAA$AAAA",
        "scrypt$x$8$1$AAAA$AAAA",
        "scrypt$16384$8$1$!!!$AAAA",
        "scrypt$16384$8$1$$AAAA",
    ],
)
def test_parse_hash_rejects_malformed(bad: str) -> None:
    assert parse_hash(bad) is None
    assert verify_password(PLAIN, bad) is False  # 예외 없이 False


def test_verify_right_and_wrong_password() -> None:
    stored = hash_password(PLAIN)
    assert verify_password(PLAIN, stored) is True
    assert verify_password(PLAIN + "x", stored) is False
    assert verify_password("", stored) is False


def test_verify_uses_parameters_from_stored_string() -> None:
    """저장 문자열의 파라미터(n)로 검증한다 -- 나중에 파라미터를 올려도 옛 해시가 유효."""
    import hashlib

    salt = b"0123456789abcdef"
    digest = hashlib.scrypt(PLAIN.encode(), salt=salt, n=2**10, r=8, p=1, dklen=32)
    stored = "$".join(
        ["scrypt", "1024", "8", "1", base64.b64encode(salt).decode(), base64.b64encode(digest).decode()]
    )
    assert verify_password(PLAIN, stored) is True
    assert verify_password("other-test-pass", stored) is False


def test_verify_handles_non_ascii_password() -> None:
    stored = hash_password("시험용비밀번호-가나다라")
    assert verify_password("시험용비밀번호-가나다라", stored) is True
    assert verify_password("시험용비밀번호-가나다", stored) is False


def test_unencodable_password_is_explicitly_rejected_not_an_accident() -> None:
    """짝 없는 서로게이트는 UTF-8 로 못 바꾼다 -- `is_utf8_encodable` 이 False 이고
    `verify_password` 는 예외 없이 False(`_derive` 를 부르기 전에 명시적으로 끝낸다)."""
    from app.auth.passwords import is_utf8_encodable

    bad = chr(0xD800) + "aaaaaaaaaa"
    assert is_utf8_encodable(bad) is False
    assert is_utf8_encodable(PLAIN) is True
    assert is_utf8_encodable("한글🙂") is True
    stored = hash_password(PLAIN)
    called: list[int] = []
    real = passwords._derive
    passwords._derive = lambda *a, **k: called.append(1) or real(*a, **k)  # type: ignore[assignment]
    try:
        assert verify_password(bad, stored) is False
    finally:
        passwords._derive = real  # type: ignore[assignment]
    assert called == []


def test_dummy_hash_is_valid_format_and_cached() -> None:
    d = dummy_hash()
    assert parse_hash(d) is not None
    assert dummy_hash() is d  # 프로세스당 한 번
    assert verify_password(PLAIN, d) is False


def test_verify_uses_constant_time_compare(monkeypatch: pytest.MonkeyPatch) -> None:
    """결정 C/D18 지킬 것 1 -- 비교는 `hmac.compare_digest`. (`==` 로 바꾸는 변이는 기능
    테스트로는 안 잡혀서, 호출 여부를 직접 본다. 01-plan V2-1 의 한계 보완.)"""
    calls: list[int] = []
    real = passwords.hmac.compare_digest

    def spy(a: bytes, b: bytes) -> bool:
        calls.append(1)
        return real(a, b)

    monkeypatch.setattr(passwords.hmac, "compare_digest", spy)
    assert verify_password(PLAIN, hash_password(PLAIN)) is True
    assert calls == [1]
