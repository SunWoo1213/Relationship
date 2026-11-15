"""Refs: P9b-auth U2 D18 결정 C -- 비밀번호 해시·검증.

표준 라이브러리 `hashlib.scrypt`(n=2**14, r=8, p=1, dklen=32, 솔트 16B)만
쓴다 -- 새 의존성 0. 저장 형식은 파라미터를 문자열에 담아 나중에 올릴 수 있게 한다:

    scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64>      (예: scrypt$16384$8$1$....$....)

검증은 `hmac.compare_digest`(상수 시간, D18 지킬 것 1). 평문 비밀번호·해시는
로그·예외 메시지에 넣지 않는다(D18 지킬 것 3) -- 이 모듈의 어떤 예외 문구도 입력 값을
담지 않는다.
"""

from __future__ import annotations

import base64
import binascii
import functools
import hashlib
import hmac
import secrets

#: 결정 C 의 scrypt 파라미터. 형식 문자열에도 같은 값이 들어간다.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SALT_BYTES = 16

_PREFIX = "scrypt"


def _maxmem(n: int, r: int, p: int) -> int:
    """OpenSSL scrypt 의 메모리 상한(기본 32 MiB). 파라미터를 올려도 막히지 않게
    필요량(128·n·r)의 두 배 + 1 MiB 로 잡는다."""
    return 128 * n * r * 2 + 128 * r * p + 1024 * 1024


def _derive(password: str, salt: bytes, n: int, r: int, p: int, dklen: int) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=dklen, maxmem=_maxmem(n, r, p)
    )


def is_utf8_encodable(password: str) -> bool:
    """짝 없는 서로게이트(U+D800 등)가 있으면 UTF-8 로 못 바꾼다 -> False."""
    try:
        password.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def hash_password(password: str) -> str:
    """무작위 솔트로 해시해 `scrypt$n$r$p$salt_b64$hash_b64` 문자열을 돌려준다."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _derive(password, salt, SCRYPT_N, SCRYPT_R, SCRYPT_P, SCRYPT_DKLEN)
    return "$".join(
        (
            _PREFIX,
            str(SCRYPT_N),
            str(SCRYPT_R),
            str(SCRYPT_P),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        )
    )


def parse_hash(stored: str) -> tuple[int, int, int, bytes, bytes] | None:
    """저장 형식을 `(n, r, p, salt, digest)` 로 푼다. 형식이 아니면 `None`."""
    parts = stored.split("$")
    if len(parts) != 6 or parts[0] != _PREFIX:
        return None
    try:
        n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
        salt = base64.b64decode(parts[4], validate=True)
        digest = base64.b64decode(parts[5], validate=True)
    except (ValueError, binascii.Error):
        return None
    if n < 2 or r < 1 or p < 1 or not salt or not digest:
        return None
    return n, r, p, salt, digest


def verify_password(password: str, stored: str) -> bool:
    """`password` 가 `stored` 해시와 맞으면 True. 형식이 깨진 `stored` 는 False
    (예외를 올리지 않는다 -- 호출한 쪽이 같은 실패 응답을 내게)."""
    parsed = parse_hash(stored)
    if parsed is None:
        return False
    n, r, p, salt, digest = parsed
    if not is_utf8_encodable(password):
        return False  # 가입될 수 없는 비밀번호 -- 의도된 실패(예외·500 아님)
    try:
        candidate = _derive(password, salt, n, r, p, len(digest))
    except ValueError:
        return False
    return hmac.compare_digest(candidate, digest)


@functools.cache
def dummy_hash() -> str:
    """없는 아이디의 로그인 시도에도 해시 검증을 한 번 돌려 응답 시간 차를 줄이기
    위한 더미 해시(실제 사용자 비밀번호와 무관한 무작위 값, 프로세스당 한 번)."""
    return hash_password(secrets.token_urlsafe(16))
