"""Refs: P9b-auth U2 D18 -- 로그인 의존성 `current_user`.

`current_user(request, session, now)` -- 쿠키(이름은 `sessions.cookie_name()`)의 토큰을
해시로 조회해 만료 전 세션의 `User` 를 돌려준다. 쿠키가 없거나 토큰이 모르는 값이거나
만료면 `HTTPException(401, {"code": "unauthenticated"})`.

시계는 `get_auth_now()` 로 주입한다(테스트가 `app.dependency_overrides` 로 바꿔 만료를
본다). 브리핑의 `app.api.deps.get_now` 와 일부러 분리했다 -- 그 시계를 고정하는 기존
테스트가 로그인 만료 판정까지 흔들지 않게.

**순환 import 주의(U3b 인계)**: 이 모듈은 `app.api.deps.get_session` 을 import 한다.
`app.api.routes` 가 이 모듈을 import 하게 되면(U3b), `import app.auth.deps` 를 **가장
먼저** 하는 경로에서 `app.api` 패키지 초기화 → `routes` → 아직 덜 불러온 이 모듈의
`current_user` import 로 순환한다. 진입점(`app.main`)은 `app.api` 를 먼저 불러 문제가
없지만, 테스트·스크립트가 `app.auth.deps` 를 맨 처음 import 하지 않게 하거나 U3b 에서
`get_session` 의 위치를 정리한다.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.auth.sessions import cookie_name, find_user_by_token
from app.db.models import User


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
