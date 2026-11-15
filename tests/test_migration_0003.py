"""Refs: P9b-auth U1 D18 S3.1 CR-006 F-fbaaae -- 리비전 0003 마이그레이션 시험.

0003 은 기존 사용자 데이터를 **비우고**(결정 K) 새 테이블 3개와
`pending_questions.user_id` 를 더한다. 비우기(⑤)와 downgrade→upgrade 왕복(⑦)은
공유 테스트 DB(`relationship_test`)를 흔들면 다른 테스트가 깨지므로, **이름
고정 전용 DB `relationship_test_mig`** 에서 돈다(R-10).

  - 만들기: `tests/db_bootstrap.ensure_test_database_ready` 가 `relationship_test`
    를 만드는 방식 그대로 — 없으면 `CREATE DATABASE`(만들기만 한다, `DROP DATABASE`
    는 쓰지 않는다)·`vector` 확장·`alembic upgrade head`. 있으면 재사용.
  - 모듈 fixture 가 시작 때 `downgrade base` → `upgrade 0002` → **원시 SQL** 로 0002
    상태의 행을 넣고(ORM 모델은 0003 기준이라 쓰지 않는다) → `upgrade head` 한다.
  - 이 모듈이 직접 부르는 alembic 명령은 `Config()` 로 만들어 `alembic.ini` 를 읽지
    않는다 — env.py 의 `fileConfig` 가 다른 테스트의 로거(`caplog`)를 꺼 버리지 않게
    한다. (단 fixture 가 부르는 `ensure_test_database_ready` 는 `alembic.ini` 를 읽는다 —
    `relationship_test` 를 만드는 기존 경로 그대로.)
  - 접속 환경은 `patch.dict(os.environ)` 로 이 모듈 안에서만 바꾼다.

전부 `dbtest` 표식 — CI 의 `-m "not dbtest"` 작업에서는 빠지고 DB 작업에서 돈다.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.config import ConnInfo, resolve_connection
from tests.db_bootstrap import apply_test_database_env, ensure_test_database_ready

pytestmark = pytest.mark.dbtest

REPO_ROOT = Path(__file__).resolve().parent.parent
MIG_DB_NAME = "relationship_test_mig"

# S3.1 보충(0003)에서 글자 그대로 옮긴 새 테이블 컬럼 집합.
NEW_TABLE_COLUMNS = {
    # head 기준 -- 0004 보충(nickname) 포함.
    "users": {"id", "username", "password_hash", "nickname", "created_at"},
    "auth_sessions": {"id", "user_id", "token_hash", "created_at", "expires_at"},
    "chat_messages": {"id", "user_id", "role", "content", "question_id", "created_at"},
}

# 0003 이 비우는 테이블 전부(결정 K) — persons 의 CASCADE 자식 포함.
CLEARED_TABLES = (
    "persons",
    "person_aliases",
    "person_facts",
    "events",
    "fact_sources",
    "schedules",
    "pending_questions",
    "push_subscriptions",
    "agent_traces",
)


class _EnvOverrides(dict):  # type: ignore[type-arg]
    """`patch.dict` 에 줄 "바뀐 키" 만 담는다. 값(접속 URL·비밀번호 가능)이 pytest
    실패 출력에 찍히지 않도록 repr 은 키 이름만 보인다(security §1).

    **주의(review-u1 R-9)**: repr 만 가린다. 이 객체를 `==` 로 비교하는 단언
    (`assert mig["env"] == …`, `dict(...)` 로 풀어 비교하는 것 포함)을 쓰지 않는다 --
    pytest 가 값 차이를 그대로 찍는다(CI 에서는 그 값이 `DATABASE_URL`, 비밀번호 포함).
    쓰는 곳은 `_in_mig_env(...)` 로 환경에 덮어쓰는 것뿐이다."""

    def __repr__(self) -> str:
        return f"<_EnvOverrides keys={sorted(self)}>"


def _mig_env() -> tuple[ConnInfo, _EnvOverrides]:
    """현재(테스트 DB 를 가리키는) 환경을 복사해 전용 DB 이름으로 바꾼다.

    돌려주는 것: (접속 정보 — 비밀번호는 `repr` 에 나오지 않는다, `os.environ` 과 달라진
    키만 담은 덮어쓰기). **전체 환경 사본은 돌려주지 않는다** -- 호출한 fixture 의
    지역변수에 남으면 `pytest -l` 로 실패 출력에 찍힐 수 있다(review-u1 R-8).
    """
    env = dict(os.environ)
    env["TEST_POSTGRES_DB"] = MIG_DB_NAME
    apply_test_database_env(env)
    overrides = _EnvOverrides({k: v for k, v in env.items() if os.environ.get(k) != v})
    conn, _warnings = resolve_connection(env)
    return conn, overrides


@contextmanager
def _in_mig_env(overrides: dict[str, str]) -> Iterator[None]:
    with patch.dict(os.environ, overrides):
        yield


def _alembic_cfg() -> Config:
    cfg = Config()  # alembic.ini 를 읽지 않는다 — fileConfig 부작용 방지(모듈 docstring)
    cfg.set_main_option("script_location", str(REPO_ROOT / "alembic"))
    return cfg


@pytest.fixture(scope="module")
def mig(db_engine: Engine) -> Iterator[dict[str, Any]]:
    """전용 DB 를 0002 상태 + 원시 SQL 행으로 만든 뒤 head 로 올린다.

    `db_engine` 은 테스트 서버에 닿는지(닿지 않으면 skip) 확인하는 용도다.
    yield 값: engine, env(os.environ 과 달라진 키만 담은 덮어쓰기 — 전체 환경 사본 아님),
    before(0002 상태에서 센 행 수), cfg.
    """
    conn, overrides = _mig_env()
    engine = create_engine(conn.sqlalchemy_url())
    cfg = _alembic_cfg()
    with _in_mig_env(overrides):
        # 없으면 만들고(vector 확장 포함) head 까지 올린다 — relationship_test 와 같은 방식.
        ensure_test_database_ready(conn.sqlalchemy_url(), repo_root=REPO_ROOT)
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "0002")

        with engine.begin() as c:
            # 0002 상태의 사용자 데이터(원시 SQL — ORM 은 0003 기준이다).
            c.execute(text(
                "INSERT INTO persons (id, user_id, display_name, relation_tag, hierarchy) "
                "OVERRIDING SYSTEM VALUE VALUES (101, 'mig-user', '김팀장', '직장', '상')"
            ))
            c.execute(text(
                "INSERT INTO person_aliases (person_id, alias, source) "
                "VALUES (101, '팀장님', 'user_said')"
            ))
            c.execute(text(
                "INSERT INTO person_facts (person_id, key, value, confidence) "
                "VALUES (101, 'pattern:meal', '자주 식사', 1.0)"
            ))
            c.execute(text(
                "INSERT INTO events (id, person_id, type, content, raw_utterance, occurred_at) "
                "OVERRIDING SYSTEM VALUE VALUES "
                "(201, 101, 'meal', '점심', '팀장님이랑 점심', now())"
            ))
            c.execute(text(
                "INSERT INTO fact_sources (fact_id, event_id) "
                "SELECT id, 201 FROM person_facts WHERE person_id = 101"
            ))
            c.execute(text(
                "INSERT INTO schedules (person_id, title, scheduled_at) "
                "VALUES (101, '미팅', now() + interval '1 day')"
            ))
            c.execute(text(
                "INSERT INTO pending_questions (session_id, kind, question, options, context) "
                "VALUES ('mig-s', 'identity', '누구?', CAST('[]' AS jsonb), CAST('{}' AS jsonb))"
            ))
            c.execute(text(
                "INSERT INTO push_subscriptions (user_id, endpoint, keys) "
                "VALUES ('mig-user', 'https://push.example/x', CAST('{}' AS jsonb))"
            ))
            c.execute(text(
                "INSERT INTO agent_traces "
                "(session_id, step, tool_name, input, output, tokens_in, tokens_out) "
                "VALUES ('mig-s', '인식', 'search_person', CAST('{}' AS jsonb), "
                "CAST('{}' AS jsonb), 0, 0)"
            ))
        with engine.connect() as c:
            before = {
                t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar_one()
                for t in CLEARED_TABLES
            }

        command.upgrade(cfg, "head")
    try:
        yield {"engine": engine, "env": overrides, "before": before, "cfg": cfg}
    finally:
        engine.dispose()


def _columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as c:
        rows = c.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :t"
            ),
            {"t": table},
        )
        return {r[0] for r in rows}


def _version(engine: Engine) -> str:
    with engine.connect() as c:
        return c.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


def _constraint_violated(
    engine: Engine, sql: str, setup: tuple[str, ...] = ()
) -> IntegrityError:
    """`setup` 을 실행한 뒤 `sql` 이 IntegrityError 를 내는지 확인해 돌려준다.

    전부 한 트랜잭션 안에서 돌고 끝에 항상 롤백한다(시험 행을 남기지 않는다).
    """
    with engine.connect() as c:
        trans = c.begin()
        try:
            for stmt in setup:
                c.execute(text(stmt))
            with pytest.raises(IntegrityError) as info:
                c.execute(text(sql))
            return info.value
        finally:
            trans.rollback()


# ① DB 버전 == 스크립트 head, 0003 이 이력에 있다(head 리터럴은 test_migration_0004 가 본다)
def test_db_is_at_head_and_0003_is_in_history(mig):
    with _in_mig_env(mig["env"]):
        script = ScriptDirectory.from_config(mig["cfg"])
        head = script.get_current_head()
        history = {rev.revision for rev in script.walk_revisions()}
    assert _version(mig["engine"]) == head
    assert "0003" in history


# ② 새 테이블 3개·컬럼 집합이 S3.1 보충과 같다
def test_new_tables_have_exactly_the_s3_1_columns(mig):
    for table, expected in NEW_TABLE_COLUMNS.items():
        assert _columns(mig["engine"], table) == expected, table
    assert "user_id" in _columns(mig["engine"], "pending_questions")


# ③ UNIQUE·CHECK — 위반 INSERT 가 값으로 정해진 제약 이름의 IntegrityError
def test_users_username_is_unique(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO users (id, username, nickname, password_hash) VALUES ('u-b', 'dup', 'dup_b', 'h')",
        setup=(
            "INSERT INTO users (id, username, nickname, password_hash) VALUES ('u-a', 'dup', 'dup_a', 'h')",
        ),
    )
    assert err.orig.diag.constraint_name == "uq_users_username"


def test_auth_sessions_token_hash_is_unique(mig):
    insert = (
        "INSERT INTO auth_sessions (user_id, token_hash, expires_at) "
        "VALUES ('u-t', 'same-hash', now() + interval '7 days')"
    )
    err = _constraint_violated(
        mig["engine"],
        insert,
        setup=(
            "INSERT INTO users (id, username, nickname, password_hash) VALUES ('u-t', 'tok', 'tok', 'h')",
            insert,
        ),
    )
    assert err.orig.diag.constraint_name == "uq_auth_sessions_token_hash"


def test_chat_messages_role_check_rejects_other_values(mig):
    err = _constraint_violated(
        mig["engine"],
        "INSERT INTO chat_messages (user_id, role, content) VALUES ('u-r', 'system', '안녕')",
        setup=(
            "INSERT INTO users (id, username, nickname, password_hash) VALUES ('u-r', 'role', 'role', 'h')",
        ),
    )
    assert err.orig.diag.constraint_name == "ck_chat_messages_role_valid"


def test_chat_messages_role_check_accepts_user_and_assistant(mig):
    with mig["engine"].connect() as c:
        trans = c.begin()
        try:
            c.execute(text(
                "INSERT INTO users (id, username, nickname, password_hash) "
                "VALUES ('u-ok', 'roleok', 'roleok', 'h')"
            ))
            c.execute(text(
                "INSERT INTO chat_messages (user_id, role, content) VALUES "
                "('u-ok', 'user', '안녕'), ('u-ok', 'assistant', '네')"
            ))
            count = c.execute(
                text("SELECT count(*) FROM chat_messages WHERE user_id = 'u-ok'")
            ).scalar_one()
            assert count == 2
        finally:
            trans.rollback()


# FK — 새 테이블 두 곳만 users FK(CASCADE), 기존 user_id 컬럼에는 FK 없음(결정 O)
def test_only_new_tables_have_users_foreign_key_with_cascade(mig):
    with mig["engine"].connect() as c:
        rows = c.execute(text(
            "SELECT conrelid::regclass::text, conname, confdeltype FROM pg_constraint "
            "WHERE contype = 'f' AND confrelid = 'users'::regclass ORDER BY 1"
        )).all()
    assert [(r[0], r[1], r[2]) for r in rows] == [
        ("auth_sessions", "fk_auth_sessions_user_id_users", "c"),
        ("chat_messages", "fk_chat_messages_user_id_users", "c"),
    ]
    with mig["engine"].connect() as c:
        for table in ("persons", "push_subscriptions", "pending_questions"):
            fks = c.execute(text(
                "SELECT count(*) FROM pg_constraint "
                "WHERE contype = 'f' AND conrelid = CAST(:t AS regclass) "
                "AND confrelid = 'users'::regclass"
            ), {"t": table}).scalar_one()
            assert fks == 0, table


# ④ pending_questions.user_id NOT NULL
def test_pending_questions_user_id_is_not_null(mig):
    engine = mig["engine"]
    with engine.connect() as c:
        nullable = c.execute(text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_name = 'pending_questions' AND column_name = 'user_id'"
        )).scalar_one()
    assert nullable == "NO"
    err = _constraint_violated(
        engine,
        "INSERT INTO pending_questions (session_id, kind, question, options, context) "
        "VALUES ('s', 'identity', 'q', CAST('[]' AS jsonb), CAST('{}' AS jsonb))",
    )
    assert err.orig.diag.column_name == "user_id"


# ⑤ 비우기 — 0002 상태의 행이 head 뒤 전부 0
def test_upgrade_clears_all_user_data(mig):
    # 시작 상태가 실제로 채워져 있었음을 먼저 값으로 확인(빈 DB 에서 통과하는 가짜 시험 방지).
    assert mig["before"] == {t: 1 for t in CLEARED_TABLES}
    with mig["engine"].connect() as c:
        after = {
            t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar_one()
            for t in CLEARED_TABLES
        }
    assert after == {t: 0 for t in CLEARED_TABLES}


# ⑥ alembic check — 모델과 DB 가 같다
def test_alembic_check_reports_no_new_operations(mig):
    with _in_mig_env(mig["env"]):
        command.check(mig["cfg"])  # 차이가 있으면 CommandError


# ⑦ downgrade 0002 → upgrade head 왕복
def test_downgrade_to_0002_removes_new_objects_and_upgrade_restores(mig):
    engine = mig["engine"]
    with _in_mig_env(mig["env"]):
        command.downgrade(mig["cfg"], "0002")
        try:
            assert _version(engine) == "0002"
            for table in NEW_TABLE_COLUMNS:
                assert _columns(engine, table) == set(), f"{table} 가 남았다"
            assert "user_id" not in _columns(engine, "pending_questions")
            with engine.connect() as c:
                leftover = c.execute(text(
                    "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND indexname IN "
                    "('ix_pending_questions_user_id_answered_at', 'ix_auth_sessions_user_id', "
                    "'ix_chat_messages_user_id_created_at')"
                )).all()
            assert leftover == []
        finally:
            command.upgrade(mig["cfg"], "head")
    with _in_mig_env(mig["env"]):
        head = ScriptDirectory.from_config(mig["cfg"]).get_current_head()
    assert _version(engine) == head
    for table, expected in NEW_TABLE_COLUMNS.items():
        assert _columns(engine, table) == expected
    assert "user_id" in _columns(engine, "pending_questions")
