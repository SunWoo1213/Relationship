"""Refs: P9b-auth U2 D18 결정 D·E·F -- 세션 토큰 발급·조회·폐기와 쿠키 규칙.

- 토큰은 `secrets.token_urlsafe(32)`. **DB 에는 `sha256(token)` hex 만** 저장한다
  (`auth_sessions.token_hash`, D18 지킬 것 2) -- 토큰 원문은 응답 쿠키에만 실린다.
- 만료는 `now + AUTH_SESSION_DAYS`. 조회는 **만료 전만**(`expires_at > now`, 같은 순간은
  만료). 로그아웃은 그 행 삭제. 만료 행 정리 작업은 두지 않는다(01-plan 리스크).
- 쿠키 이름은 `AUTH_COOKIE_SECURE` 에 따라 `__Host-rel_session`(켬)/`rel_session`(끔).
  속성은 `HttpOnly`·`SameSite=Lax`·`Path=/`·`Secure`(설정)·`Max-Age`=유지 기간,
  `Domain` 없음(`__Host-` 접두 조건). **`Path=/` 필수** -- Caddy 가 `/api` 접두를 떼므로
  백엔드는 `/auth/login` 을 보지만 브라우저는 `/api/auth/login` 에서 받는다. `Path` 가
  없으면 브라우저 기본 경로가 `/api/auth` 가 되어 다른 API 에 쿠키가 실리지 않는다.

토큰·쿠키 값은 로그·예외 메시지에 넣지 않는다(D18 지킬 것 3).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Literal

from fastapi import Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import AuthSession, User
from app.settings import (
    AUTH_COOKIE_NAME_PLAIN,
    AUTH_COOKIE_NAME_SECURE,
    AUTH_SESSION_DAYS,
    auth_cookie_secure,
)

COOKIE_SAMESITE: Literal["lax"] = "lax"
COOKIE_PATH = "/"


def new_user_id() -> str:
    """`users.id` -- uuid4 hex(결정 O)."""
    return uuid.uuid4().hex


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def cookie_name(secure: bool | None = None) -> str:
    """쿠키 이름. `secure` 를 생략하면 설정(`AUTH_COOKIE_SECURE`)을 읽는다."""
    if secure is None:
        secure = auth_cookie_secure()
    return AUTH_COOKIE_NAME_SECURE if secure else AUTH_COOKIE_NAME_PLAIN


def create_session(session: Session, user_id: str, now: datetime) -> str:
    """세션 행을 만들고 **토큰 원문**을 돌려준다(DB 에는 해시만)."""
    token = new_token()
    session.add(
        AuthSession(
            user_id=user_id,
            token_hash=hash_token(token),
            expires_at=now + timedelta(days=AUTH_SESSION_DAYS),
        )
    )
    session.flush()
    return token


def find_user_by_token(session: Session, token: str, now: datetime) -> User | None:
    """만료 전 세션의 사용자. 없거나 만료(`expires_at <= now`)면 `None`."""
    return session.execute(
        select(User)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(AuthSession.token_hash == hash_token(token), AuthSession.expires_at > now)
    ).scalar_one_or_none()


def delete_session(session: Session, token: str) -> None:
    """그 토큰의 세션 행을 지운다(로그아웃)."""
    session.execute(delete(AuthSession).where(AuthSession.token_hash == hash_token(token)))
    session.flush()


def set_login_cookie(response: Response, token: str) -> None:
    secure = auth_cookie_secure()
    response.set_cookie(
        key=cookie_name(secure),
        value=token,
        max_age=AUTH_SESSION_DAYS * 24 * 60 * 60,
        path=COOKIE_PATH,
        secure=secure,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )


def clear_login_cookie(response: Response) -> None:
    secure = auth_cookie_secure()
    response.delete_cookie(
        key=cookie_name(secure),
        path=COOKIE_PATH,
        secure=secure,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )
