"""Refs: FIX-006 수정안 5행 ①~③ -- 테스트 전용 DB 격리 회귀.

개발 DB 에 행을 커밋하는 테스트는 만들지 않는다(FIX-006 제약). ①·②는
`db_engine`/`db_session`(이미 테스트 DB 에만 붙는 픽스처, `tests/conftest.py`)
로 이름·URL 을 비교해 확인하고, ③은 `tests/db_bootstrap.py` 의 순수 함수를
DB 없이 직접 검증한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.db_bootstrap import (  # noqa: E402
    DBNameCollisionError,
    DEFAULT_TEST_DB_NAME,
    resolve_test_db_name,
)

dbtest = pytest.mark.dbtest


# ---------- ① 테스트 세션의 current_database() 가 개발 DB 이름이 아니다 ----------


@dbtest
def test_current_database_is_test_db_not_dev_db(db_session, dev_db_name, test_db_name):
    """`SELECT current_database()` 가 테스트 DB 이름과 같고, 개발 DB 이름과는 다르다."""
    current = db_session.execute(text("SELECT current_database()")).scalar_one()
    assert current == test_db_name
    assert current != dev_db_name


# ---------- ② 개발 DB 에 커밋된 행이 테스트 세션에 보이지 않는다 (엔진 URL 로 증명) ----------


@dbtest
def test_engine_targets_test_db_not_dev_db(db_engine, dev_db_name, test_db_name):
    """엔진이 실제로 접속하는 DB 이름이 테스트 DB 다.

    PostgreSQL 은 같은 서버 안에서도 DB 가 다르면 한 세션이 다른 DB 의 행을
    구조적으로 볼 수 없다(물리적으로 분리된 네임스페이스) -- 그래서 엔진이
    가리키는 DB 이름이 테스트 DB 라는 것을 확인하는 것만으로 "개발 DB 에
    커밋된 행이 이 세션에 보이지 않는다"는 것이 증명된다. 개발 DB 에 임시
    행을 만들지 않고 확인한다(FIX-006 수정안 5행 ②).
    """
    assert db_engine.url.database == test_db_name
    assert db_engine.url.database != dev_db_name


# ---------- ③ 테스트 DB 이름이 개발 DB 이름과 같으면 conftest 가 거부한다 ----------


def test_resolve_test_db_name_rejects_collision_with_dev_db_name():
    with pytest.raises(DBNameCollisionError, match="개발 DB"):
        resolve_test_db_name("relationship", {"TEST_POSTGRES_DB": "relationship"})


def test_resolve_test_db_name_accepts_distinct_name():
    assert (
        resolve_test_db_name("relationship", {"TEST_POSTGRES_DB": "relationship_test"})
        == "relationship_test"
    )


def test_resolve_test_db_name_defaults_when_env_var_absent():
    """`TEST_POSTGRES_DB` 가 없으면 기본값 `relationship_test` 를 쓴다."""
    assert resolve_test_db_name("relationship", {}) == DEFAULT_TEST_DB_NAME
