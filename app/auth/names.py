"""Refs: P9b-auth U9 CR-007 D18 -- 닉네임 정규화(가입·중복 조회 공용 한 함수, 지킬 것 10).

처리 순서(결정 X·Y): NFC -> 앞뒤 공백 제거 -> `NICKNAME_PATTERN` `fullmatch` -> 통과하면
`lower()` 한 값이 저장·비교 값이다. 위반이면 `None` -- DB 에 묻기 전에 걸러진다.
"""

from __future__ import annotations

import re
import unicodedata

from app.settings import NICKNAME_PATTERN

_NICKNAME_RE = re.compile(NICKNAME_PATTERN)


def normalize_nickname(raw: str) -> str | None:
    """정규화한 닉네임을 돌려준다. 규칙 위반이면 `None`."""
    s = unicodedata.normalize("NFC", raw).strip()
    if _NICKNAME_RE.fullmatch(s) is None:
        return None
    return s.lower()
