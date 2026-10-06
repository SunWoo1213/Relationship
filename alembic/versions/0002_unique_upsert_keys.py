"""Refs: FIX-020 S3.1 -- 세 upsert 키에 UNIQUE 제약을 건다.

`person_facts(person_id, key)` · `person_aliases(person_id, alias)` ·
`push_subscriptions(user_id, endpoint)` 는 전부 애플리케이션이 "조회 후
삽입"으로 유일성을 흉내내던 자리였다(D-6 · D6 미결 7 · P7 결정 F(i)).
두 요청이 동시에 오면 둘 다 "없음"을 읽고 둘 다 INSERT 해 중복 행이
생길 수 있었다(FIX-020.md 증상). 이 리비전은 그 규칙을 DB 제약으로
강제한다 -- 열·테이블·시그니처는 바꾸지 않는다(S3.1 보충 한 줄만).

업그레이드 전에 세 조합 각각 중복 행이 있는지 먼저 검사한다. 하나라도
있으면 **자동으로 지우지 않고** `RuntimeError` 로 멈춘다(FIX-020 수정안
3행 "자동 삭제 금지") -- 메시지에는 테이블 이름과 중복 그룹 수만 담고
실제 값(별칭 문자열·사실 값·구독 endpoint)은 남기지 않는다(비밀·개인
식별 정보를 로그/예외에 남기지 않는 security.md §1 원칙과 같은 이유).

2026-10-05 개발 DB 확인(FIX-020.md, 읽기 전용)에서는 세 조합 모두 중복
행 0 이었다 -- 이 리비전을 개발 DB 에 적용해도 안전할 것으로 보이지만,
실제 적용은 사용자가 `alembic upgrade head` 를 직접 실행한다(이 FIX
작업 자체는 개발 DB 를 건드리지 않는다).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-06 09:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (테이블, 유니크 제약 이름, 제약 컬럼들, 중복 검사 GROUP BY 컬럼들) -- 제약
# 이름은 app/db/base.py 의 naming_convention 이 실제로 내는 이름과 글자
# 그대로 같아야 한다(`uq_%(table_name)s_%(column_0_N_name)s`, 위 모듈
# docstring의 실측 확인 결과 그대로).
_UNIQUE_SPECS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("person_facts", "uq_person_facts_person_id_key", ("person_id", "key")),
    ("person_aliases", "uq_person_aliases_person_id_alias", ("person_id", "alias")),
    (
        "push_subscriptions",
        "uq_push_subscriptions_user_id_endpoint",
        ("user_id", "endpoint"),
    ),
)


def _check_no_duplicates() -> None:
    """세 조합 각각 중복 행이 있으면 멈춘다(자동 삭제 금지, 모듈 docstring)."""
    bind = op.get_bind()
    for table, _constraint_name, columns in _UNIQUE_SPECS:
        column_list = ", ".join(columns)
        result = bind.execute(
            sa.text(
                f"SELECT count(*) FROM ("
                f"SELECT 1 FROM {table} GROUP BY {column_list} HAVING count(*) > 1"
                f") AS dup"
            )
        )
        duplicate_group_count = result.scalar_one()
        if duplicate_group_count:
            raise RuntimeError(
                f"FIX-020: {table} 에 ({column_list}) 조합이 중복인 그룹이 "
                f"{duplicate_group_count}개 있습니다. UNIQUE 제약을 걸기 전에 "
                "먼저 중복을 수동으로 정리하세요(이 리비전은 자동으로 지우지 "
                "않습니다)."
            )


def upgrade() -> None:
    """Upgrade schema."""
    _check_no_duplicates()

    for table, constraint_name, columns in _UNIQUE_SPECS:
        op.create_unique_constraint(constraint_name, table, list(columns))


def downgrade() -> None:
    """Downgrade schema."""
    for table, constraint_name, _columns in reversed(_UNIQUE_SPECS):
        op.drop_constraint(constraint_name, table, type_="unique")
