"""Refs: P9b-auth U12 CR-008 D19 S3.1 -- `mcp_tokens`(MCP 개인 접근 토큰).

upgrade 는 테이블 생성뿐이다 -- 두 UNIQUE(`uq_mcp_tokens_user_id`·`uq_mcp_tokens_token_hash`)와
`users.id` FK(ON DELETE CASCADE). **`DELETE`·`TRUNCATE`·`UPDATE` 가 없다** -- 기존 계정·
세션·기록 데이터를 건드리지 않는다. 별도 인덱스·CHECK 도 없다(UNIQUE 가 인덱스를 겸한다).

## downgrade

`mcp_tokens` 만 지운다. 발급한 토큰이 모두 무효가 될 뿐 계정·기록은 그대로다.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-17 23:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema -- 테이블 생성뿐(기존 데이터 무변경)."""
    op.create_table(
        "mcp_tokens",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_mcp_tokens_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mcp_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_mcp_tokens_token_hash")),
        sa.UniqueConstraint("user_id", name=op.f("uq_mcp_tokens_user_id")),
    )


def downgrade() -> None:
    """Downgrade schema -- `mcp_tokens` 만 지운다(토큰 무효, 계정·기록 불변)."""
    op.drop_table("mcp_tokens")
