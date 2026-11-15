"""Refs: P9b-auth U4 D18 CR-006 security 원칙9 -- 계정당 채팅방 하나의 대화 기록.

`chat_messages` 에 **계정 소유로만** 저장·조회한다(security §5). 이 모듈의 두 함수는 모두
`user_id` 를 필수 인자로 받아 SQL 조건에 건다 -- 다른 계정의 기록이 섞이는 경로가 없다.

- `append(session, user_id, role, content, question_id=None)`: 행 하나를 넣고 **flush 만** 한다.
  커밋하지 않는다 -- 라우트(`POST /chat`·`POST /answers/{id}`)의 기존 트랜잭션 안에서 저장되므로
  요청이 실패해 롤백되면 기록도 함께 사라진다(결정 R).
- `recent(session, user_id, limit)`: 최근 `limit` 개를 골라 **오래된 것 -> 최근 순**으로 돌려준다.
  정렬 키는 `(created_at, id)` 다. 한 트랜잭션 안의 행은 `created_at`(= 트랜잭션 시작 시각)이 같으므로
  `id` 가 사용자 행 -> 응답 행의 순서를 보장한다.

대화 기록을 `agent_traces`·`pending_questions.context` 로 복사하지 않는다(security §5) --
이 모듈은 trace 를 남기지도 않는다(읽기 전용 조회는 trace 0).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CHAT_ROLES, ChatMessage

#: 결정 I -- `GET /chat/history` 의 기본 개수와 최대 개수(페이지 없음).
HISTORY_DEFAULT_LIMIT = 50
HISTORY_MAX_LIMIT = 200


def append(
    session: Session,
    user_id: str,
    role: str,
    content: str,
    question_id: int | None = None,
) -> ChatMessage:
    """`user_id` 계정의 채팅방에 한 줄을 더한다(flush 만 — 커밋은 라우트 트랜잭션이 한다)."""
    if role not in CHAT_ROLES:
        raise ValueError(f"unknown chat role: {role!r}")
    row = ChatMessage(user_id=user_id, role=role, content=content, question_id=question_id)
    session.add(row)
    session.flush()
    return row


def recent(session: Session, user_id: str, limit: int) -> list[ChatMessage]:
    """`user_id` 계정의 최근 `limit` 줄을 오래된 것 -> 최근 순으로 돌려준다."""
    newest_first = (
        session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return list(reversed(newest_first))
