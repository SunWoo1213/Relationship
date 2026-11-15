"""Refs: P9b-auth U9 CR-007 D18 S3.1 -- `users.nickname` (닉네임, UNIQUE).

upgrade 순서: ① `nickname` 을 nullable 로 추가 ② 기존 행을 `nickname = username` 으로
채움 ③ NOT NULL ④ UNIQUE(`uq_users_nickname`). `username` 이 이미 UNIQUE 라 닉네임 =
아이디 값도 서로 다르므로 ④ 가 깨지지 않는다.

## 데이터를 지우지 않는다 (0003 과 다르다)

`DELETE`·`TRUNCATE`·`DROP TABLE` 이 없다. 기존 계정은 그대로 남고 닉네임만 아이디 값으로
채워진다.

## downgrade

UNIQUE 제약과 `nickname` 컬럼만 지운다. 계정 행은 남고 닉네임 값만 사라진다.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-16 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("nickname", sa.Text(), nullable=True))
    op.execute("UPDATE users SET nickname = username WHERE nickname IS NULL")
    op.alter_column("users", "nickname", nullable=False)
    op.create_unique_constraint(op.f("uq_users_nickname"), "users", ["nickname"])


def downgrade() -> None:
    """Downgrade schema — 제약·컬럼만 지운다. 계정 행은 남고 닉네임 값만 사라진다."""
    op.drop_constraint(op.f("uq_users_nickname"), "users", type_="unique")
    op.drop_column("users", "nickname")
