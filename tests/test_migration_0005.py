"""Refs: P9b-auth U12 CR-008 D19 S3.1 -- 리비전 0005(`mcp_tokens`) 마이그레이션 시험.

0005 는 테이블 생성뿐이라 **데이터를 지우지 않는다**. 공유 테스트 DB 를 흔들지 않도록 0003·0004 시험과
같은 **이름 고정 전용 DB `relationship_test_mig`** 에서 돈다(새 DB 를 만들지 않는다 -- 헬퍼는
`test_migration_0003` 것을 그대로 import, `DROP DATABASE` 0).

모듈 fixture: `downgrade base` -> `upgrade 0004` -> **원시 SQL** 로 0004 상태의 계정 2행(닉네임 포함)·
세션 1행·대화 1행 -> `upgrade head`. 마지막에 head 로 돌려 두므로 이 DB 를 다음 시험이 이어 쓸 수 있다.

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

#: S3.1 0005 보충 -- mcp_tokens 컬럼 집합(6).
MCP_TOKEN_COLUMNS = {"id", "user_id", "token_hash", "created_at", "expires_at", "last_used_at"}

_COUNTED = ("users", "auth_sessions", "chat_messages")


def _counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as c:
        return {t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar_one() for t in _COUNTED}


def _table_exists(engine: Engine, name: str) -> bool:
    with engine.connect() as c:
        return bool(
            c.execute(
                text(
                    "SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = :t"
                ),
                {"t": name},
            ).scalar_one()
        )


@pytest.fixture(scope="module")
def mig(db_engine: Engine) -> Iterator[dict[str, Any]]:
    conn, overrides = _mig_env()
    engine = create_engine(conn.sqlalchemy_url())
    cfg = _alembic_cfg()
    with _in_mig_env(overrides):
        ensure_test_database_ready(conn.sqlalchemy_url(), repo_root=REPO_ROOT)
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "0004")

        with engine.begin() as c:
            c.execute(
                text(
                    "INSERT INTO users (id, username, nickname, password_hash) VALUES "
                    "('mig5-a', 'test', '시험계정', 'h'), ('mig5-b', 'demo_01', '데모', 'h')"
                )
            )
            c.execute(
                text(
                    "INSERT INTO auth_sessions (user_id, token_hash, expires_at) "
                    "VALUES ('mig5-a', 'mig5-session-hash', now() + interval '7 days')"
                )
            )
            c.execute(
                text(
                    "INSERT INTO chat_messages (user_id, role, content) "
                    "VALUES ('mig5-a', 'user', '안녕')"
                )
            )
        before = _counts(engine)
        had_table_before = _table_exists(engine, "mcp_tokens")

        command.upgrade(cfg, "head")
    try:
        yield {
            "engine": engine,
            "env": overrides,
            "cfg": cfg,
            "before": before,
            "had_table_before": had_table_before,
        }
    finally:
        engine.dispose()


# ① head == 0005 · DB 버전 0005
def test_head_is_0005_and_db_is_at_0005(mig):
    with _in_mig_env(mig["env"]):
        head = ScriptDirectory.from_config(mig["cfg"]).get_current_head()
    assert head == "0005"
    assert _version(mig["engine"]) == "0005"
    assert mig["had_table_before"] is False  # 시작 상태(0004)에는 테이블이 없었다


# ② 컬럼 집합 = S3.1 0005 보충(6)
def test_mcp_tokens_columns_match_s3_1(mig):
    assert _columns(mig["engine"], "mcp_tokens") == MCP_TOKEN_COLUMNS


# ③ 삭제 0 -- 기존 행 수 불변
def test_upgrade_deletes_nothing(mig):
    assert mig["before"] == {"users": 2, "auth_sessions": 1, "chat_messages": 1}
    assert _counts(mig["engine"]) == mig["before"]


# ④ UNIQUE 두 개 -- 제약 이름
def test_user_id_is_unique_with_named_constraint(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO mcp_tokens (user_id, token_hash, expires_at) "
        "VALUES ('mig5-a', 'h2', now() + interval '7 days')",
        setup=(
            "INSERT INTO mcp_tokens (user_id, token_hash, expires_at) "
            "VALUES ('mig5-a', 'h1', now() + interval '7 days')",
        ),
    )
    assert err.orig.diag.constraint_name == "uq_mcp_tokens_user_id"


def test_token_hash_is_unique_with_named_constraint(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO mcp_tokens (user_id, token_hash, expires_at) "
        "VALUES ('mig5-b', 'same-hash', now() + interval '7 days')",
        setup=(
            "INSERT INTO mcp_tokens (user_id, token_hash, expires_at) "
            "VALUES ('mig5-a', 'same-hash', now() + interval '7 days')",
        ),
    )
    assert err.orig.diag.constraint_name == "uq_mcp_tokens_token_hash"


# ⑤ FK CASCADE -- 계정을 지우면 그 토큰 행도 사라진다(시험 전용 DB 안, 한 트랜잭션 롤백)
def test_deleting_the_user_cascades_to_the_token_row(mig):
    with mig["engine"].connect() as c:
        trans = c.begin()
        try:
            c.execute(
                text(
                    "INSERT INTO users (id, username, nickname, password_hash) "
                    "VALUES ('mig5-c', 'cascade_user', '연쇄', 'h')"
                )
            )
            c.execute(
                text(
                    "INSERT INTO mcp_tokens (user_id, token_hash, expires_at) "
                    "VALUES ('mig5-c', 'cascade-hash', now() + interval '7 days')"
                )
            )
            c.execute(text("DELETE FROM users WHERE id = 'mig5-c'"))
            left = c.execute(
                text("SELECT count(*) FROM mcp_tokens WHERE user_id = 'mig5-c'")
            ).scalar_one()
        finally:
            trans.rollback()
    assert left == 0


# ⑥ alembic check -- 모델과 DB 가 같다
def test_alembic_check_reports_no_new_operations(mig):
    with _in_mig_env(mig["env"]):
        command.check(mig["cfg"])  # 차이가 있으면 CommandError


# ⑦ downgrade 0004 -> upgrade head 왕복 -- 테이블만 사라지고 계정 행은 남는다
def test_downgrade_to_0004_drops_only_the_table_and_upgrade_restores_it_empty(mig):
    engine = mig["engine"]
    with _in_mig_env(mig["env"]):
        command.downgrade(mig["cfg"], "0004")
        try:
            assert _version(engine) == "0004"
            assert _table_exists(engine, "mcp_tokens") is False
            assert _counts(engine) == mig["before"]  # 계정·세션·대화 행은 그대로
        finally:
            command.upgrade(mig["cfg"], "head")
    assert _version(engine) == "0005"
    assert _table_exists(engine, "mcp_tokens") is True
    assert _columns(engine, "mcp_tokens") == MCP_TOKEN_COLUMNS
    with engine.connect() as c:
        assert c.execute(text("SELECT count(*) FROM mcp_tokens")).scalar_one() == 0
    assert _counts(engine) == mig["before"]
