"""Refs: P9d-sensitive-guard U3 CR-009 D20 S3.1 -- 민감 정보 가드레일(민감 표시·고지 컬럼, kind 4종).

upgrade 는 **컬럼 추가와 CHECK 교체뿐**이다 -- `DELETE`·`TRUNCATE`·`UPDATE`·`DROP TABLE` 이 없다.
기존 행은 전부 NULL 이 된다(= 일반 · 고지 미동의, 소급 없음 -- CR-009 사용자 결정 9).

새 컬럼 6개(S3.1 보충 0006):

- `events.sensitive_category` VARCHAR NULL · `events.consent_question_id` BIGINT NULL(FK 없음 -- P9b 결정 O)
- `person_facts.sensitive_category` VARCHAR NULL
- `schedules.sensitive_category` VARCHAR NULL
- `users.privacy_notice_version` INTEGER NULL · `users.privacy_notice_accepted_at` TIMESTAMPTZ NULL

새 CHECK 3개(세 표의 `sensitive_category` 가 범주 5종 또는 NULL) + `pending_questions.kind` CHECK 를 지우고
4종(`identity`·`new_person`·`schedule`·`sensitive`)으로 다시 만든다. 인덱스·UNIQUE·FK·테이블 추가는 없다.

## downgrade (D20 5절 -- 데이터를 지우지 않고 실패한다)

`kind='sensitive'` 질문 행·`sensitive_category IS NOT NULL` 행(세 표)·`consent_question_id IS NOT NULL`
행이 **하나라도 있으면 아무것도 바꾸지 않고** 개수만 담은 예외를 낸다(원문 0). 전부 0 이면 CHECK 3개를
지우고 컬럼을 지운 뒤 `kind` CHECK 를 3종으로 되돌린다. 고지 컬럼(`users`)은 판정 대상이 아니다(동의 기록일
뿐 민감 데이터가 아니다).

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-22 17:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 마이그레이션은 모델 상수를 import 하지 않는다(리비전은 시점 고정) -- 값은 글자 그대로 둔다.
_CATEGORIES_SQL = "('crime', 'health', 'sex', 'politics_religion', 'finance')"
_KINDS_OLD_SQL = "kind IN ('identity', 'new_person', 'schedule')"
_KINDS_NEW_SQL = "kind IN ('identity', 'new_person', 'schedule', 'sensitive')"
_CATEGORY_TABLES = ("events", "person_facts", "schedules")


def upgrade() -> None:
    """Upgrade schema -- 컬럼 추가와 CHECK 교체뿐(기존 데이터 무변경)."""
    for table in _CATEGORY_TABLES:
        op.add_column(table, sa.Column("sensitive_category", sa.String(), nullable=True))
        op.create_check_constraint(
            op.f(f"ck_{table}_sensitive_category_valid"),
            table,
            f"sensitive_category IN {_CATEGORIES_SQL}",
        )
    op.add_column("events", sa.Column("consent_question_id", sa.BigInteger(), nullable=True))
    op.add_column("users", sa.Column("privacy_notice_version", sa.Integer(), nullable=True))
    op.add_column(
        "users",
        sa.Column("privacy_notice_accepted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.drop_constraint(op.f("ck_pending_questions_kind_valid"), "pending_questions", type_="check")
    op.create_check_constraint(
        op.f("ck_pending_questions_kind_valid"), "pending_questions", _KINDS_NEW_SQL
    )


def _count(conn: sa.engine.Connection, sql: str) -> int:
    return int(conn.execute(sa.text(sql)).scalar_one())


def downgrade() -> None:
    """Downgrade schema -- 민감 행이 하나라도 있으면 아무것도 지우지 않고 실패한다(개수만 담은 메시지)."""
    conn = op.get_bind()
    sensitive_questions = _count(conn, "SELECT count(*) FROM pending_questions WHERE kind = 'sensitive'")
    marked = {
        table: _count(conn, f"SELECT count(*) FROM {table} WHERE sensitive_category IS NOT NULL")
        for table in _CATEGORY_TABLES
    }
    consent_refs = _count(conn, "SELECT count(*) FROM events WHERE consent_question_id IS NOT NULL")
    if sensitive_questions or consent_refs or any(marked.values()):
        raise RuntimeError(
            "0006 downgrade 거부 -- 민감 데이터가 남아 있다(아무것도 지우지 않았다): "
            f"pending_questions.kind='sensitive' {sensitive_questions}건 · "
            f"events.sensitive_category {marked['events']}건 · "
            f"person_facts.sensitive_category {marked['person_facts']}건 · "
            f"schedules.sensitive_category {marked['schedules']}건 · "
            f"events.consent_question_id {consent_refs}건"
        )

    op.drop_constraint(op.f("ck_pending_questions_kind_valid"), "pending_questions", type_="check")
    op.create_check_constraint(
        op.f("ck_pending_questions_kind_valid"), "pending_questions", _KINDS_OLD_SQL
    )

    op.drop_column("users", "privacy_notice_accepted_at")
    op.drop_column("users", "privacy_notice_version")
    op.drop_column("events", "consent_question_id")
    for table in reversed(_CATEGORY_TABLES):
        op.drop_constraint(op.f(f"ck_{table}_sensitive_category_valid"), table, type_="check")
        op.drop_column(table, "sensitive_category")
