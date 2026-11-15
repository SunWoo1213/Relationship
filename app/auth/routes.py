"""Refs: P9b-auth U2 U9 D18 CR-006 CR-007 -- `/auth/signup`·`/auth/login`·`/auth/logout`·`/auth/me`·`/auth/availability`.

계약은 `01-plan.md` "API 계약"(개정 3) 표 그대로:

| 경로 | 성공 | 실패 |
|---|---|---|
| `POST /auth/signup` | 201 `{id, username, nickname}` + 로그인 쿠키(가입 즉시 로그인, 결정 G) | 422 `invalid_username` -> `invalid_password` -> `invalid_nickname`(첫 위반) · 409 `username_taken`/`nickname_taken`(둘 다 겹치면 `username_taken`) |
| `POST /auth/login` | 200 `{id, username, nickname}` + 쿠키 | 401 `invalid_credentials`(없는 아이디·틀린 비밀번호 같은 응답) |
| `POST /auth/logout` | 204(본문 없음) + 쿠키 삭제 | 미로그인 401 `unauthenticated`(F-3) |
| `GET /auth/me` | 200 `{id, username, nickname}` | 401 `unauthenticated` |
| `GET /auth/availability` | 200 `{username, nickname}`(각 `available`/`taken`/`invalid`/`null`) · 로그인 불필요 · `Cache-Control: no-store` | 두 쿼리가 모두 없으면 422 `missing_query` |

- 아이디는 소문자로 정규화한 뒤 `^[a-z0-9_]{3,20}$`(결정 A), 비밀번호는 8~128자(결정 B).
- 로그인 실패는 없는 아이디도 **더미 해시 검증을 한 번 돌려** 응답 시간 차를 줄인다.
- 로그·trace·응답·예외 메시지에 비밀번호·토큰 0(D18 지킬 것 3). `/auth/*` 는
  `agent_traces` 를 쓰지 않는다(판정이 아니다, 원칙9 절).
- `/auth/logout` 의 `endpoint` 가 있으면 그 사용자의 그 푸시 구독 행을 지운다(U5).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas import AvailabilityOut, LoginIn, LogoutIn, MeOut, SignupIn
from app.auth.deps import current_user, get_auth_now
from app.auth.names import normalize_nickname
from app.auth.passwords import dummy_hash, hash_password, is_utf8_encodable, verify_password
from app.auth.sessions import (
    clear_login_cookie,
    cookie_name,
    create_session,
    delete_session,
    new_user_id,
    set_login_cookie,
)
from app.db.models import User
from app.push.subscriptions import delete_subscription
from app.db.session import get_session
from app.settings import PASSWORD_MAX_LEN, PASSWORD_MIN_LEN, USERNAME_PATTERN

class _NoInputEchoRoute(APIRoute):
    """형식 오류 422 본문에서 `input`(요청 본문 -- 비밀번호 포함)을 뺀다.

    FastAPI 기본 422 는 `{"detail":[{"type","loc","msg","input"}]}` 이고 `input` 에 요청 본문이
    그대로 실린다(누락 필드 오류에는 본문 전체 dict). 응답 본문에 비밀번호를 남기지 않는다는
    D18 지킬 것 3 을 위해 이 라우터에서만 `input`·`ctx` 를 뺀다(전역 핸들러는 건드리지 않는다).
    """

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            try:
                return await original(request)
            except RequestValidationError as exc:
                errors = [
                    {k: v for k, v in err.items() if k not in ("input", "ctx")}
                    for err in exc.errors()
                ]
                return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})

        return handler


router = APIRouter(prefix="/auth", route_class=_NoInputEchoRoute)

_USERNAME_RE = re.compile(USERNAME_PATTERN)


def normalize_username(raw: str) -> str:
    """결정 A -- 소문자 정규화(검사·조회·저장 모두 이 값)."""
    return raw.lower()


def _invalid(code: str) -> HTTPException:
    return HTTPException(status_code=422, detail={"code": code})


def _taken(code: str) -> HTTPException:
    return HTTPException(status_code=409, detail={"code": code})


#: 가입 INSERT 경합 때 위반된 UNIQUE 제약 이름 -> 409 코드.
_CONSTRAINT_CODES = {
    "uq_users_username": "username_taken",
    "uq_users_nickname": "nickname_taken",
}


def _exists(session: Session, column: Any, value: str) -> bool:
    return session.execute(select(User.id).where(column == value)).first() is not None


def _me_out(user: User) -> MeOut:
    return MeOut(id=user.id, username=user.username, nickname=user.nickname)


@router.post("/signup", response_model=MeOut, status_code=201)
def signup(
    body: SignupIn,
    response: Response,
    session: Session = Depends(get_session),
    now: Callable[[], datetime] = Depends(get_auth_now),
) -> MeOut:
    # ①~③ 형식 검사 -- DB 조회 0(형식 위반 입력이 DB 에 가지 않는다).
    username = normalize_username(body.username)
    if _USERNAME_RE.fullmatch(username) is None:
        raise _invalid("invalid_username")
    if not (PASSWORD_MIN_LEN <= len(body.password) <= PASSWORD_MAX_LEN):
        raise _invalid("invalid_password")
    if not is_utf8_encodable(body.password):
        # 짝 없는 서로게이트 등 UTF-8 로 바꿀 수 없는 비밀번호 -- 해시 전에 422(500 방지).
        raise _invalid("invalid_password")
    nickname = normalize_nickname(body.nickname)
    if nickname is None:
        raise _invalid("invalid_nickname")

    # ④⑤ 사전 조회 -- 아이디 먼저(둘 다 겹치면 `username_taken`, 결정 AB).
    if _exists(session, User.username, username):
        raise _taken("username_taken")
    if _exists(session, User.nickname, nickname):
        raise _taken("nickname_taken")

    user = User(
        id=new_user_id(),
        username=username,
        nickname=nickname,
        password_hash=hash_password(body.password),
    )
    try:
        # ⑥ 사전 조회와 INSERT 사이 경합 -- 세이브포인트로 격리하고 제약 이름으로 코드를 정한다.
        with session.begin_nested():
            session.add(user)
            session.flush()
    except IntegrityError as err:
        constraint = getattr(getattr(err.orig, "diag", None), "constraint_name", None)
        code = _CONSTRAINT_CODES.get(constraint or "")
        if code is None:
            # 다른 제약 위반은 다른 결함이다 -- 409 로 숨기지 않고 다시 올린다(500).
            raise
        raise _taken(code) from None

    token = create_session(session, user.id, now())
    set_login_cookie(response, token)
    return _me_out(user)


@router.post("/login", response_model=MeOut)
def login(
    body: LoginIn,
    response: Response,
    session: Session = Depends(get_session),
    now: Callable[[], datetime] = Depends(get_auth_now),
) -> MeOut:
    username = normalize_username(body.username)
    # 결정 A 형식에 안 맞는 아이디(NUL·서로게이트·길이 초과 등)는 가입될 수 없으므로 DB 에
    # 묻지 않고 "없는 아이디" 로 본다(NUL 은 PostgreSQL 이 받지 못해 DataError -> 500).
    user = (
        session.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if _USERNAME_RE.fullmatch(username) is not None
        else None
    )
    # 없는 아이디에도 해시 검증을 한 번 돌린다(응답 시간 차 축소). 해시 입력 상한(결정 B 의
    # 128자)을 넘는 비밀번호는 가입될 수 없으므로 해시하지 않고 같은 실패로 끝낸다.
    stored = user.password_hash if user is not None else dummy_hash()
    too_long = len(body.password) > PASSWORD_MAX_LEN
    ok = False if too_long else verify_password(body.password, stored)
    if user is None or not ok:
        raise HTTPException(status_code=401, detail={"code": "invalid_credentials"})

    token = create_session(session, user.id, now())
    set_login_cookie(response, token)
    return _me_out(user)


@router.post("/logout", status_code=204, response_class=Response)
def logout(
    request: Request,
    body: LogoutIn | None = None,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> Response:
    # (U5) endpoint 가 오면 그 사용자의 그 브라우저 구독 행을 뗀다(같은 트랜잭션).
    if body is not None and body.endpoint:
        delete_subscription(session, user.id, body.endpoint)
    token = request.cookies.get(cookie_name())
    if token:
        delete_session(session, token)
    response = Response(status_code=204)
    clear_login_cookie(response)
    return response


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user)) -> MeOut:
    return _me_out(user)


def _availability(
    session: Session, raw: str | None, kind: str
) -> Literal["available", "taken", "invalid"] | None:
    """물은 값 하나의 판정. 묻지 않았으면 `None`. 형식 위반은 DB 조회 없이 `invalid`."""
    if raw is None:
        return None
    column: Any
    if kind == "username":
        username = normalize_username(raw)
        if _USERNAME_RE.fullmatch(username) is None:
            return "invalid"
        value, column = username, User.username
    else:
        nickname = normalize_nickname(raw)
        if nickname is None:
            return "invalid"
        value, column = nickname, User.nickname
    return "taken" if _exists(session, column, value) else "available"


@router.get("/availability", response_model=AvailabilityOut)
def availability(
    response: Response,
    username: str | None = None,
    nickname: str | None = None,
    session: Session = Depends(get_session),
) -> AvailabilityOut:
    """로그인 없이 부르는 아이디·닉네임 중복 조회(CR-007 · D18 결정 11).

    결과는 참고용 -- 최종 판정은 DB UNIQUE + 가입 시 409. 쓰기·trace·LLM 호출 0.
    """
    if username is None and nickname is None:
        raise _invalid("missing_query")
    response.headers["Cache-Control"] = "no-store"
    return AvailabilityOut(
        username=_availability(session, username, "username"),
        nickname=_availability(session, nickname, "nickname"),
    )
