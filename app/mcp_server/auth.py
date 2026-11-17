"""Refs: P9b-auth U12 CR-008 D19 D18 결정 3 AM AN -- `/mcp` Bearer 토큰 인증 ASGI 래퍼.

인증 순서(01-plan "`/mcp` 인증 순서"):
① `Authorization` 헤더를 읽는다(여러 개면 첫 값) ② `scheme, _, value = header.partition(" ")` --
`scheme.lower() != "bearer"` 또는 `value.strip() == ""` 이면 401(**DB 조회 0**) ③ `hash_token(value.strip())`
으로 `mcp_tokens` 를 찾고 `expires_at > now` 일 때만 사용자 id ④ 없으면 401 ⑤ 있으면 `last_used_at = now`
갱신·commit ⑥ 사용자 id 를 요청 범위(`scope["state"]`)에 싣고 안쪽(SDK) 앱으로.

- **헤더만 읽는다.** 쿠키·쿼리 문자열을 읽는 코드가 없다(D19 지킬 것 3).
- 401 은 이유를 구별하지 않는 한 가지 응답이다: 본문 `{"detail":{"code":"unauthenticated"}}` +
  `WWW-Authenticate: Bearer`(OAuth 메타데이터 없음 -- 결정 AN).
- 사용자 id 는 `scope["state"][USER_ID_STATE_KEY]` 로 도구에 전해진다. contextvar 를 쓰지 않는다 --
  SDK 가 도구를 어느 태스크에서 돌리는지에 기대지 않으려는 것이다(결정 AT 의 갈림길, 03-log 참고).
- 토큰 조회·`last_used_at` commit 은 동기 DB 호출이라 `anyio.to_thread.run_sync` 로 돌린다(R5-3).
- 토큰 값을 로그·예외 메시지에 넣지 않는다(D19 지킬 것 7).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import anyio.to_thread
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.auth.mcp_tokens import user_id_for_mcp_token

#: 인증된 사용자 id 를 싣는 `scope["state"]` 키. 도구(`server.py`)가 같은 이름으로 읽는다.
USER_ID_STATE_KEY = "relmemo_mcp_user_id"

_UNAUTHENTICATED_BODY = {"detail": {"code": "unauthenticated"}}


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=_UNAUTHENTICATED_BODY,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _bearer_token(scope: Scope) -> str | None:
    """`Authorization: Bearer <값>` 의 값. 헤더 없음·다른 스킴·빈 값이면 `None`."""
    header: str | None = None
    for key, raw in scope.get("headers", []):
        if key == b"authorization":  # ASGI 헤더 이름은 소문자 -- 첫 값만 쓴다.
            header = raw.decode("latin-1")
            break
    if header is None:
        return None
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer" or value.strip() == "":
        return None
    return value.strip()


class BearerAuthApp:
    """`inner`(SDK 의 Streamable HTTP ASGI 앱)를 토큰 인증으로 감싼다.

    `session_factory` 는 인자 없이 `Session` 을 돌려주는 호출 가능 객체(운영은 `SessionLocal`),
    `now` 는 UTC 시계(운영은 `get_auth_now()` 와 같은 값 -- 시험이 덮어쓸 수 있게 주입한다).
    """

    def __init__(
        self,
        inner: ASGIApp,
        session_factory: Callable[[], Session],
        now: Callable[[], datetime],
    ) -> None:
        self.inner = inner
        self.session_factory = session_factory
        self.now = now

    def _lookup(self, token: str) -> str | None:
        session = self.session_factory()
        try:
            user_id = user_id_for_mcp_token(session, token, self.now())
            session.commit()  # last_used_at 갱신(찾았을 때만 갱신이 있다)
            return user_id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # `Route` 는 http 만 넘긴다 -- 방어적으로 그대로 닫는다.
            return
        token = _bearer_token(scope)
        if token is None:
            await _unauthorized()(scope, receive, send)  # DB 조회 0
            return
        user_id = await anyio.to_thread.run_sync(self._lookup, token)
        if user_id is None:
            await _unauthorized()(scope, receive, send)
            return
        # 공유될 수 있는 기존 state 딕셔너리를 고치지 않고 새로 만든다.
        scope["state"] = {**scope.get("state", {}), USER_ID_STATE_KEY: user_id}
        await self.inner(scope, receive, send)
