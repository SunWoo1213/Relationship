"""Refs: P9b-auth U12 CR-008 D19 D18 -- MCP 개인 접근 토큰(발급·조회·상태·폐기).

계정당 행 1개(`mcp_tokens.user_id` UNIQUE). 발급은 그 사용자 행의 upsert 라 이전 토큰은
즉시 무효다. DB 에는 `hash_token()`(auth_sessions 와 같은 sha256) 해시만 둔다. 유효 조건은
`expires_at > now`(같은 순간은 만료 -- `auth_sessions` 규약). **commit 은 호출자가 한다.**
토큰 값을 로그·예외 메시지에 넣지 않는다(D19 지킬 것 7).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.api.schemas import McpTokenStatusOut
from app.auth.sessions import hash_token, new_token
from app.db.models import McpToken
from app.settings import MCP_TOKEN_DAYS


def issue_mcp_token(session: Session, user_id: str, now: datetime) -> tuple[str, datetime, datetime]:
    """새 토큰을 만들고 `(원문, created_at, expires_at)` 를 돌려준다. 그 사용자의 이전
    행은 같은 문장 안에서 덮어써진다(`ON CONFLICT (user_id) DO UPDATE` -- 경합에서도 행 1개)."""
    token = new_token()
    created_at = now
    expires_at = now + timedelta(days=MCP_TOKEN_DAYS)
    stmt = pg_insert(McpToken).values(
        user_id=user_id,
        token_hash=hash_token(token),
        created_at=created_at,
        expires_at=expires_at,
        last_used_at=None,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_mcp_tokens_user_id",
        set_={
            "token_hash": stmt.excluded.token_hash,
            "created_at": stmt.excluded.created_at,
            "expires_at": stmt.excluded.expires_at,
            "last_used_at": None,
        },
    )
    session.execute(stmt)
    session.flush()
    return token, created_at, expires_at


def user_id_for_mcp_token(session: Session, token: str, now: datetime) -> str | None:
    """토큰의 사용자 id. 없거나 만료(`expires_at <= now`)면 `None`. 찾으면 `last_used_at = now`
    로 갱신한다(commit 은 호출자)."""
    row = session.execute(
        select(McpToken.id, McpToken.user_id).where(
            McpToken.token_hash == hash_token(token), McpToken.expires_at > now
        )
    ).first()
    if row is None:
        return None
    session.execute(update(McpToken).where(McpToken.id == row.id).values(last_used_at=now))
    session.flush()
    return str(row.user_id)


def mcp_token_status(session: Session, user_id: str, now: datetime) -> McpTokenStatusOut:
    """그 계정의 토큰 상태. 행이 없으면 모두 `None`·`active=False`, 만료 행은 `active=False`
    이고 시각은 행 값 그대로다. 토큰 값은 어디에도 없다."""
    row = session.execute(select(McpToken).where(McpToken.user_id == user_id)).scalar_one_or_none()
    if row is None:
        return McpTokenStatusOut(active=False, created_at=None, expires_at=None, last_used_at=None)
    return McpTokenStatusOut(
        active=bool(row.expires_at > now),  # type: ignore[operator]
        created_at=row.created_at,  # type: ignore[arg-type]
        expires_at=row.expires_at,  # type: ignore[arg-type]
        last_used_at=row.last_used_at,  # type: ignore[arg-type]
    )


def revoke_mcp_token(session: Session, user_id: str) -> None:
    """그 계정의 토큰 행을 지운다(없어도 오류 없음 -- 멱등)."""
    session.execute(delete(McpToken).where(McpToken.user_id == user_id))
    session.flush()
