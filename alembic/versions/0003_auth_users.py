"""Refs: P9b-auth D18 S3.1 CR-006 F-fbaaae -- 계정·세션·대화 기록 테이블과 질문 소유자.

`users` · `auth_sessions` · `chat_messages` 를 만들고 `pending_questions` 에
`user_id`(NOT NULL)를 더한다. 새 테이블 두 곳의 `user_id` 만 `users.id` FK
(ON DELETE CASCADE)이고, 기존 `persons`·`push_subscriptions`·
`pending_questions` 의 `user_id` 에는 FK 를 두지 않는다(P9b 결정 O).

## 데이터를 비운다 (CR-006 결정 4 "기존 데이터는 모두 비운다", P9b 결정 K)

upgrade 맨 앞에서 `persons`(별칭·사실·사건·일정·`fact_sources` 는 FK CASCADE
로 함께 지워진다)·`pending_questions`·`push_subscriptions`·`agent_traces` 를
`DELETE` 한다. `TRUNCATE`·`DROP TABLE` 은 쓰지 않는다(security §4 — 셸이 아니라
이 리비전 파일에서 검토된 삭제). 이 DB 가 이 리비전을 처음 적용받을 때 한 번만
비워진다 — 이미 0003 인 DB 는 다시 비워지지 않는다. 비운 뒤라야
`pending_questions.user_id` 를 기본값 없이 NOT NULL 로 더할 수 있다.

## downgrade 는 데이터를 되돌리지 못한다

downgrade 는 새 인덱스·컬럼·테이블을 거꾸로 지울 뿐이다. upgrade 가 지운
사용자 데이터는 복구되지 않는다.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-15 22:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ① 기존 사용자 데이터 비우기(결정 K). persons 삭제가 별칭·사실·사건·
    # 일정·fact_sources 를 CASCADE 로 함께 지운다.
    op.execute("DELETE FROM persons")
    op.execute("DELETE FROM pending_questions")
    op.execute("DELETE FROM push_subscriptions")
    op.execute("DELETE FROM agent_traces")

    # ② 새 테이블 3개
    op.create_table(
        "users",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_auth_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_auth_sessions_token_hash")),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("question_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name=op.f("ck_chat_messages_role_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_chat_messages_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_messages")),
    )
    op.create_index(
        "ix_chat_messages_user_id_created_at",
        "chat_messages",
        ["user_id", "created_at"],
        unique=False,
    )

    # ③ pending_questions.user_id — ① 로 빈 테이블이라 기본값 없이 NOT NULL.
    op.add_column("pending_questions", sa.Column("user_id", sa.Text(), nullable=False))
    # ④ 인덱스
    op.create_index(
        "ix_pending_questions_user_id_answered_at",
        "pending_questions",
        ["user_id", "answered_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema — 스키마만 되돌린다. upgrade 가 지운 데이터는 복구되지 않는다."""
    op.drop_index("ix_pending_questions_user_id_answered_at", table_name="pending_questions")
    op.drop_column("pending_questions", "user_id")
    op.drop_index("ix_chat_messages_user_id_created_at", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("users")
