"""Refs: P1-schema S3.1 -- SQLAlchemy 2.x 선언적 베이스와 명명 규칙.

모델(테이블 9개)은 이 패키지에 넣지 않는다(U2 몫). 여기서는 `Base` 와
제약·인덱스 이름 규칙(`MetaData.naming_convention`)만 정의한다 -- 이름
규칙이 먼저 있어야 U2 의 모델이 일관된 `ck_/fk_/ix_/uq_/pk_` 이름을 받는다.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스. 명명 규칙을 공유한다."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
