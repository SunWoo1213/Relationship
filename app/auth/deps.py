"""Refs: P9b-auth U2 D18 -- 로그인 의존성 `current_user`.

`current_user(request, session, now)` -- 쿠키(이름은 `sessions.cookie_name()`)의 토큰을
해시로 조회해 만료 전 세션의 `User` 를 돌려준다. 쿠키가 없거나 토큰이 모르는 값이거나
만료면 `HTTPException(401, {"code": "unauthenticated"})`.

시계는 `get_auth_now()` 로 주입한다(테스트가 `app.dependency_overrides` 로 바꿔 만료를
본다). 브리핑의 `app.api.deps.get_now` 와 일부러 분리했다 -- 그 시계를 고정하는 기존
테스트가 로그인 만료 판정까지 흔들지 않게.

**순환 import 를 끊은 방법(U3b)**: 이 모듈은 `get_session` 을 `app.db.session` 에서 가져온다
(`app.api` 패키지를 끌어오지 않는다). 예전에는 `app.api.deps.get_session` 을 import 했는데,
`app.api.deps`·`app.api.routes` 가 이 모듈의 `current_user` 를 import 하게 되면서 어느 쪽을
먼저 import 하든 순환이 될 수 있었다. 지금은 `app.api.*` → `app.auth.deps` → `app.db.session`
한 방향뿐이라 `import app.auth.deps` 를 맨 먼저 해도 안전하다(시험: `tests/test_auth_required_routes.py`).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.sessions import cookie_name, find_user_by_token
from app.db.models import User
from app.db.session import get_session


def get_auth_now() -> Callable[[], datetime]:
    """로그인 만료 판정·세션 만료 계산에 쓰는 시계. 운영은 실제 UTC 시계."""
    return lambda: datetime.now(timezone.utc)


def unauthenticated() -> HTTPException:
    return HTTPException(status_code=401, detail={"code": "unauthenticated"})


def current_user(
    request: Request,
    session: Session = Depends(get_session),
    now: Callable[[], datetime] = Depends(get_auth_now),
) -> User:
    token = request.cookies.get(cookie_name())
    if not token:
        raise unauthenticated()
    user = find_user_by_token(session, token, now())
    if user is None:
        raise unauthenticated()
    return user
