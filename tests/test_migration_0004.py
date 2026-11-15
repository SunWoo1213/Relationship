"""Refs: P9b-auth U9 CR-007 D18 S3.1 -- 리비전 0004(`users.nickname`) 마이그레이션 시험.

0004 는 0003 과 달리 **데이터를 지우지 않는다**. 기존 계정의 닉네임을 아이디 값으로 채운 뒤
NOT NULL·UNIQUE 를 건다. 공유 테스트 DB 를 흔들지 않도록 0003 시험과 같은 **이름 고정 전용 DB
`relationship_test_mig`** 에서 돈다(새 DB 를 만들지 않는다 -- 헬퍼는 `test_migration_0003` 것을
그대로 import).

모듈 fixture: `downgrade base` -> `upgrade 0003` -> **원시 SQL** 로 0003 상태의 계정 2행·세션 1행·
대화 1행 -> `upgrade head`. 마지막에 head 로 돌려 두므로 이 DB 를 다음 시험이 이어 쓸 수 있다.

전부 `dbtest` 표식.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from tests.db_bootstrap import ensure_test_database_ready
from tests.test_migration_0003 import (
    REPO_ROOT,
    _alembic_cfg,
    _columns,
    _constraint_violated,
    _in_mig_env,
    _mig_env,
    _version,
)

pytestmark = pytest.mark.dbtest

#: S3.1 0004 보충 -- users 컬럼 집합(5).
USERS_COLUMNS = {"id", "username", "password_hash", "nickname", "created_at"}

_COUNTED = ("users", "auth_sessions", "chat_messages")


def _counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as c:
        return {
            t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar_one() for t in _COUNTED
        }


def _nicknames(engine: Engine) -> dict[str, str]:
    with engine.connect() as c:
        return {
            r[0]: r[1] for r in c.execute(text("SELECT username, nickname FROM users")).all()
        }


@pytest.fixture(scope="module")
def mig(db_engine: Engine) -> Iterator[dict[str, Any]]:
    conn, overrides = _mig_env()
    engine = create_engine(conn.sqlalchemy_url())
    cfg = _alembic_cfg()
    with _in_mig_env(overrides):
        ensure_test_database_ready(conn.sqlalchemy_url(), repo_root=REPO_ROOT)
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "0003")

        with engine.begin() as c:
            c.execute(text(
                "INSERT INTO users (id, username, password_hash) VALUES "
                "('mig4-a', 'test', 'h'), ('mig4-b', 'demo_01', 'h')"
            ))
            c.execute(text(
                "INSERT INTO auth_sessions (user_id, token_hash, expires_at) "
                "VALUES ('mig4-a', 'mig4-token-hash', now() + interval '7 days')"
            ))
            c.execute(text(
                "INSERT INTO chat_messages (user_id, role, content) "
                "VALUES ('mig4-a', 'user', '안녕')"
            ))
        before = _counts(engine)
        columns_before = _columns(engine, "users")

        command.upgrade(cfg, "head")
    try:
        yield {
            "engine": engine,
            "env": overrides,
            "cfg": cfg,
            "before": before,
            "columns_before": columns_before,
        }
    finally:
        engine.dispose()


# ① head == 0004 · DB 버전 0004
def test_head_is_0004_and_db_is_at_0004(mig):
    with _in_mig_env(mig["env"]):
        head = ScriptDirectory.from_config(mig["cfg"]).get_current_head()
    assert head == "0004"
    assert _version(mig["engine"]) == "0004"


# ② users 컬럼 집합 = S3.1 0004 보충(5). 시작 상태(0003)는 nickname 이 없었다.
def test_users_columns_match_s3_1_0004(mig):
    assert mig["columns_before"] == USERS_COLUMNS - {"nickname"}
    assert _columns(mig["engine"], "users") == USERS_COLUMNS


# ③ 백필 -- 두 계정 모두 nickname == username
def test_backfill_sets_nickname_to_username(mig):
    assert _nicknames(mig["engine"]) == {"test": "test", "demo_01": "demo_01"}


# ④ 삭제 0 -- 행 수가 upgrade 전과 같다(시작 상태가 실제로 채워져 있었음도 값으로)
def test_upgrade_deletes_nothing(mig):
    assert mig["before"] == {"users": 2, "auth_sessions": 1, "chat_messages": 1}
    assert _counts(mig["engine"]) == mig["before"]


# ⑤ nickname NOT NULL
def test_nickname_is_not_null(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO users (id, username, password_hash) VALUES ('mig4-x', 'nonick', 'h')",
    )
    assert err.orig.diag.column_name == "nickname"


# ⑥ nickname UNIQUE -- 제약 이름 uq_users_nickname
def test_nickname_is_unique(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO users (id, username, nickname, password_hash) "
        "VALUES ('mig4-y', 'other_name', 'test', 'h')",
    )
    assert err.orig.diag.constraint_name == "uq_users_nickname"


# ⑦ alembic check -- 모델과 DB 가 같다
def test_alembic_check_reports_no_new_operations(mig):
    with _in_mig_env(mig["env"]):
        command.check(mig["cfg"])  # 차이가 있으면 CommandError


# ⑧ downgrade 0003 -> upgrade head 왕복 -- 컬럼·제약만 사라지고 계정 행은 남는다
def test_downgrade_to_0003_keeps_rows_and_upgrade_backfills_again(mig):
    engine = mig["engine"]
    with _in_mig_env(mig["env"]):
        command.downgrade(mig["cfg"], "0003")
        try:
            assert _version(engine) == "0003"
            assert _columns(engine, "users") == USERS_COLUMNS - {"nickname"}
            with engine.connect() as c:
                leftover = c.execute(text(
                    "SELECT conname FROM pg_constraint WHERE conname = 'uq_users_nickname'"
                )).all()
            assert leftover == []
            assert _counts(engine) == mig["before"]  # 계정 행은 그대로
        finally:
            command.upgrade(mig["cfg"], "head")
    assert _version(engine) == "0004"
    assert _columns(engine, "users") == USERS_COLUMNS
    assert _nicknames(engine) == {"test": "test", "demo_01": "demo_01"}
    assert _counts(engine) == mig["before"]
