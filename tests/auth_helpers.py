"""Refs: P9b-auth U3a D18 CR-006 F-5 R2-2 -- 기존 테스트를 로그인 모델로 옮기는 도우미.

이 단위(U3a)에서는 라우트가 아직 쿠키를 보지 않으므로 이 도우미를 써도 **동작이 같다**.
U3b 에서 라우트가 `current_user` 를 요구하면 같은 도우미가 그대로 로그인 쿠키를 공급한다.

네 가지를 준다.

1. `make_user(session, user_id="local", username=None)` -- 기존 데이터 준비 코드가 쓰던
   `"local"` 같은 값을 **그대로 `users.id` 로 하는 행**을 넣는다(`users.id` 는 Text, 결정 O).
   그래서 `Person(user_id="local")` 로 데이터를 넣는 24파일 78곳을 건드리지 않는다.
   같은 id 가 이미 있으면 그 행을 돌려준다(멱등).
2. `logged_in_client(app, session_or_factory, user_id="local")` -- 그 사용자의 세션 행을 만들고
   쿠키를 붙인 `TestClient`. 테스트마다 `app.dependency_overrides[get_session]` 이 다르므로
   **앱과 세션(또는 세션 팩토리)** 을 받는다. 쿠키 이름은 `app.auth.sessions.cookie_name()`
   에서 얻는다(하드코딩 금지 -- `__Host-`/접두 없음이 설정에 따라 바뀐다).
3. `make_ctx(session, user_id="local", session_id=..., **kw)` -- `ToolContext` 를 `user_id` 를
   **명시해** 만든다(U3b 에서 `ToolContext.user_id` 기본값이 사라진다).
4. `committed_login(app, session_factory, user_id=None)` -- **실제 커밋을 쓰는 테스트용**
   (`tests/test_commit_boundaries.py`·`tests/test_answer_concurrency.py` 는 `get_session` 을
   바꿔 끼우지 않고 실제 커밋한다). `users`·`auth_sessions` 행을 **커밋**하고, `with` 를
   벗어날 때(예외 포함) 그 행을 **지정 id 로** 지운다. `username` 은 호출마다 다른 값이라
   UNIQUE 가 재실행에서 부딪히지 않는다.

토큰·쿠키 값은 어디에도 출력하지 않는다(assert 메시지·예외 문자열에 넣지 않는다 -- D18 지킬 것 3).
`users.password_hash` 에는 로그인에 쓸 수 없는 고정 자리표시자를 넣는다(이 사용자로는
`POST /auth/login` 이 항상 401).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth.sessions import cookie_name, create_session
from app.db.models import AuthSession, User
from app.tools.context import ToolContext

#: 로그인에 쓸 수 없는 해시 자리표시자(`parse_hash` 형식이 아니라 `verify_password` 가 항상 False).
NO_LOGIN_HASH = "!helper-no-login"

#: 기존 테스트가 쓰던 고정 사용자 id(= 환경변수 고정 사용자의 기본값).
DEFAULT_USER_ID = "local"

#: 쿠키가 `Secure` 라 운영과 같은 조건(https)으로 요청한다(`tests/test_auth_api.py` 와 같은 방식).
DEFAULT_BASE_URL = "https://testserver"

SessionOrFactory = Session | Callable[[], Session]


def make_user(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    username: str | None = None,
    *,
    nickname: str | None = None,
) -> User:
    """`id == user_id` 인 사용자 행을 보장한다(있으면 그대로, 없으면 flush 로 넣는다)."""
    existing = session.get(User, user_id)
    if existing is not None:
        return existing
    resolved_username = username if username is not None else f"helper-{user_id}"
    user = User(
        id=user_id,
        username=resolved_username,
        # 0004 보충: 생략하면 그 행의 아이디 값(기존 호출 시그니처 불변).
        nickname=nickname if nickname is not None else resolved_username,
        password_hash=NO_LOGIN_HASH,
    )
    session.add(user)
    session.flush()
    return user


def make_ctx(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    *,
    session_id: str = "test-session",
    **kwargs: Any,
) -> ToolContext:
    """`user_id` 를 명시한 `ToolContext`. 나머지 필드(`embedder`·`now` 등)는 키워드로."""
    return ToolContext(session=session, session_id=session_id, user_id=user_id, **kwargs)


def _issue_token(session: Session, user_id: str, username: str | None, now: datetime) -> str:
    make_user(session, user_id, username)
    return create_session(session, user_id, now)


def _client_with_cookie(
    app: FastAPI, token: str, *, base_url: str, raise_server_exceptions: bool
) -> TestClient:
    client = TestClient(
        app, base_url=base_url, raise_server_exceptions=raise_server_exceptions
    )
    client.cookies.set(cookie_name(), token)
    return client


def logged_in_client(
    app: FastAPI,
    session_or_factory: SessionOrFactory,
    user_id: str = DEFAULT_USER_ID,
    *,
    username: str | None = None,
    now: datetime | None = None,
    base_url: str = DEFAULT_BASE_URL,
    raise_server_exceptions: bool = True,
) -> TestClient:
    """그 사용자로 로그인한 쿠키를 가진 `TestClient`.

    - `session_or_factory` 가 `Session`(예: 롤백 픽스처 `db_session`)이면 그 세션에 행을 넣고
      flush 만 한다 -- 픽스처가 끝날 때 롤백으로 사라진다.
    - 세션 팩토리(인자 없이 `Session` 을 돌려주는 호출 가능 객체)면 **별도 세션에서 커밋**한다.
      이 경우 지우는 일은 호출자 몫이다 -- 정리까지 맡기려면 `committed_login` 을 쓴다.
    """
    issued_at = now if now is not None else datetime.now(timezone.utc)
    if isinstance(session_or_factory, Session):
        token = _issue_token(session_or_factory, user_id, username, issued_at)
    else:
        with session_or_factory() as own:
            token = _issue_token(own, user_id, username, issued_at)
            own.commit()
    return _client_with_cookie(
        app, token, base_url=base_url, raise_server_exceptions=raise_server_exceptions
    )


@contextmanager
def committed_login(
    app: FastAPI,
    session_factory: Callable[[], Session],
    user_id: str | None = None,
    *,
    username: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
    raise_server_exceptions: bool = True,
) -> Iterator[TestClient]:
    """실제 커밋을 쓰는 테스트용 로그인 클라이언트. 끝나면 이 사용자 행·세션 행을 지운다.

    `user_id` 를 생략하면 호출마다 새 값(uuid4 hex)이라 다른 테스트와 겹치지 않는다.
    `username` 은 호출마다 다른 값이 기본이다(UNIQUE 가 재실행에서 부딪히지 않게).
    정리는 이 호출이 만든(또는 보장한) 사용자 한 명의 행만 지정 id 로 지운다 -- 테이블 전체
    삭제·TRUNCATE 금지.
    """
    uid = user_id if user_id is not None else uuid.uuid4().hex
    uname = username if username is not None else f"helper-{uuid.uuid4().hex[:12]}"
    with session_factory() as own:
        token = _issue_token(own, uid, uname, datetime.now(timezone.utc))
        own.commit()
    try:
        yield _client_with_cookie(
            app, token, base_url=base_url, raise_server_exceptions=raise_server_exceptions
        )
    finally:
        with session_factory() as cleanup:
            cleanup.execute(delete(AuthSession).where(AuthSession.user_id == uid))
            cleanup.execute(delete(User).where(User.id == uid))
            cleanup.commit()
