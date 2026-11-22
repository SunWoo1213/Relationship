"""Refs: P9d-sensitive-guard U3 CR-009 D20 S3.1 -- 리비전 0006(민감 표시·고지 컬럼, kind 4종) 마이그레이션 시험.

0006 upgrade 는 **컬럼 추가와 CHECK 교체뿐**이라 데이터를 지우지 않는다. downgrade 는 민감 행이 하나라도
있으면 아무것도 지우지 않고 실패한다(D20 5절). 공유 테스트 DB 를 흔들지 않도록 0003~0005 시험과 같은
**이름 고정 전용 DB `relationship_test_mig`** 에서 돈다(헬퍼는 `test_migration_0003` 것을 그대로 import,
`DROP DATABASE` 0).

모듈 fixture: `downgrade base` -> `upgrade 0005` -> 0005 에서 `kind='sensitive'` 삽입이 CHECK 위반임을 확인 ->
원시 SQL 로 0005 상태의 기존 행 -> 구조 목록·행 스냅샷 -> `upgrade head`. 마지막에 head 로 돌려 두므로 이 DB 를
다음 시험이 이어 쓸 수 있다. **민감 행을 넣는 시험은 끝에 그 행을 지운다**(남기면 다음 시험의 `downgrade base` 가
0006 가드에 막힌다).

계약 값(컬럼 이름·타입·nullable·기본값·CHECK 문장·head 리비전)은 값으로 단언한다.

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

#: S3.1 0006 보충 -- 새 컬럼 6개: (테이블, 컬럼) -> (data_type, character_maximum_length).
NEW_COLUMNS = {
    ("events", "sensitive_category"): "character varying",
    ("events", "consent_question_id"): "bigint",
    ("person_facts", "sensitive_category"): "character varying",
    ("schedules", "sensitive_category"): "character varying",
    ("users", "privacy_notice_version"): "integer",
    ("users", "privacy_notice_accepted_at"): "timestamp with time zone",
}

#: 범주 5종(D20 결정 2 — 순서 고정).
CATEGORIES = ("crime", "health", "sex", "politics_religion", "finance")

#: 새 CHECK 3개 -- 제약 이름.
CATEGORY_CHECKS = {
    "events": "ck_events_sensitive_category_valid",
    "person_facts": "ck_person_facts_sensitive_category_valid",
    "schedules": "ck_schedules_sensitive_category_valid",
}
KIND_CHECK = "ck_pending_questions_kind_valid"

_TABLES = (
    "persons", "person_aliases", "person_facts", "fact_sources", "events", "schedules",
    "pending_questions", "push_subscriptions", "agent_traces", "users", "auth_sessions",
    "chat_messages", "mcp_tokens",
)

#: 0005 상태의 기존 행 -- upgrade 가 이 값을 그대로 둬야 한다. 0005 시점의 컬럼을 **시각 컬럼까지
#: 전부** 뽑는다(review-u3 R-2 -- 시각 컬럼이 빠지면 upgrade 가 `updated_at`/`created_at` 을 갱신해도
#: 통과한다). `SELECT *` 는 쓰지 않는다 -- 0006 이 더한 컬럼이 head 쪽 스냅샷에만 생겨 비교가 어긋난다.
#: `created_at`/`updated_at` 은 행 삽입 때 DB 가 정한 값이라 upgrade 가 건드리지 않으면 그대로다.
_SNAPSHOT_SQL = {
    "persons": (
        "SELECT id, user_id, display_name, relation_tag, hierarchy, created_at, updated_at "
        "FROM persons ORDER BY id"
    ),
    "events": (
        "SELECT id, person_id, type, content, raw_utterance, occurred_at, created_at "
        "FROM events ORDER BY id"
    ),
    "person_facts": (
        "SELECT id, person_id, key, value, confidence, updated_at FROM person_facts ORDER BY id"
    ),
    "schedules": "SELECT id, person_id, title, scheduled_at, briefed_at FROM schedules ORDER BY id",
    "pending_questions": (
        "SELECT id, session_id, user_id, kind, question, options, context, answer, "
        "created_at, answered_at FROM pending_questions ORDER BY id"
    ),
    "users": "SELECT id, username, nickname, password_hash, created_at FROM users ORDER BY id",
}


def _counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as c:
        return {t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar_one() for t in _TABLES}


def _snapshot(engine: Engine) -> dict[str, list[tuple[Any, ...]]]:
    with engine.connect() as c:
        return {t: [tuple(r) for r in c.execute(text(sql)).all()] for t, sql in _SNAPSHOT_SQL.items()}


def _structure(engine: Engine) -> dict[str, set[str]]:
    """테이블·인덱스·PK/UNIQUE/FK 이름 목록 -- 0006 이 더하지 않는다."""
    with engine.connect() as c:
        tables = {
            r[0]
            for r in c.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
        }
        indexes = {r[0] for r in c.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"))}
        constraints = {
            r[0]
            for r in c.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE connamespace = 'public'::regnamespace AND contype IN ('p', 'u', 'f')"
                )
            )
        }
    return {"tables": tables, "indexes": indexes, "constraints": constraints}


def _check_names(engine: Engine) -> set[str]:
    with engine.connect() as c:
        return {
            r[0]
            for r in c.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE connamespace = 'public'::regnamespace AND contype = 'c'"
                )
            )
        }


def _check_def(engine: Engine, name: str) -> str:
    with engine.connect() as c:
        return c.execute(
            text("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = :n"), {"n": name}
        ).scalar_one()


def _column_info(engine: Engine, table: str, column: str) -> dict[str, Any] | None:
    with engine.connect() as c:
        row = c.execute(
            text(
                "SELECT data_type, is_nullable, column_default, character_maximum_length "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :t AND column_name = :c"
            ),
            {"t": table, "c": column},
        ).one_or_none()
    if row is None:
        return None
    return {"data_type": row[0], "is_nullable": row[1], "default": row[2], "max_len": row[3]}


@pytest.fixture(scope="module")
def mig(db_engine: Engine) -> Iterator[dict[str, Any]]:
    conn, overrides = _mig_env()
    engine = create_engine(conn.sqlalchemy_url())
    cfg = _alembic_cfg()
    with _in_mig_env(overrides):
        ensure_test_database_ready(conn.sqlalchemy_url(), repo_root=REPO_ROOT)
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "0005")

        with engine.begin() as c:
            c.execute(text("INSERT INTO users (id, username, nickname, password_hash) VALUES ('mig6-a', 'test', '시험', 'h')"))
            c.execute(
                text(
                    "INSERT INTO persons (id, user_id, display_name, relation_tag, hierarchy) "
                    "VALUES (9101, 'mig6-a', '팀장님', '직장', '상')"
                )
            )
            c.execute(
                text(
                    "INSERT INTO events (id, person_id, type, content, raw_utterance, occurred_at) "
                    "VALUES (9201, 9101, 'meal', '점심', '팀장님이랑 점심 먹었다', '2026-11-01T12:00:00+09:00')"
                )
            )
            c.execute(
                text("INSERT INTO person_facts (id, person_id, key, value, confidence) VALUES (9301, 9101, '취미', '등산', 0.9)")
            )
            c.execute(
                text(
                    "INSERT INTO schedules (id, person_id, title, scheduled_at) "
                    "VALUES (9401, 9101, '면담', '2026-12-01T10:00:00+09:00')"
                )
            )
            c.execute(
                text(
                    "INSERT INTO pending_questions (id, session_id, user_id, kind, question, options, context) "
                    "VALUES (9501, 'chat:mig6-a', 'mig6-a', 'identity', '팀장님 맞나요?', '[]'::jsonb, '{}'::jsonb)"
                )
            )
        # 0005 에서는 kind='sensitive' 가 CHECK 위반이다.
        sensitive_at_0005 = _constraint_violated(
            engine,
            "INSERT INTO pending_questions (session_id, user_id, kind, question, options, context) "
            "VALUES ('chat:mig6-a', 'mig6-a', 'sensitive', 'q', '[]'::jsonb, '{}'::jsonb)",
        )
        before = {
            "counts": _counts(engine),
            "snapshot": _snapshot(engine),
            "structure": _structure(engine),
            "checks": _check_names(engine),
            "kind_check_def": _check_def(engine, KIND_CHECK),
            "new_columns": {k: _column_info(engine, *k) for k in NEW_COLUMNS},
            "users_columns": _columns(engine, "users"),
        }
        command.upgrade(cfg, "head")
    try:
        yield {
            "engine": engine,
            "env": overrides,
            "cfg": cfg,
            "before": before,
            "sensitive_at_0005": sensitive_at_0005,
        }
    finally:
        engine.dispose()


# ① head == 0006 · down_revision == 0005 · DB 버전 0006
def test_head_is_0006_and_db_is_at_0006(mig):
    with _in_mig_env(mig["env"]):
        script = ScriptDirectory.from_config(mig["cfg"])
        head = script.get_current_head()
        down = script.get_revision("0006").down_revision
    assert head == "0006"
    assert down == "0005"
    assert _version(mig["engine"]) == "0006"


# ② 0005 상태에는 새 컬럼이 없었고, 0006 뒤에는 이름·타입·nullable·기본값 없음까지 S3.1 과 같다
def test_new_columns_match_s3_1_by_value(mig):
    assert all(v is None for v in mig["before"]["new_columns"].values())  # 시작 상태(0005)에는 없었다
    for (table, column), data_type in NEW_COLUMNS.items():
        info = _column_info(mig["engine"], table, column)
        assert info == {"data_type": data_type, "is_nullable": "YES", "default": None, "max_len": None}, (
            table,
            column,
            info,
        )
    assert _columns(mig["engine"], "users") == mig["before"]["users_columns"] | {
        "privacy_notice_version",
        "privacy_notice_accepted_at",
    }


# ③ 새 CHECK 문장 -- 범주 5종, 0006 뒤 kind CHECK 는 4종
def test_check_sentences_are_the_contract_values(mig):
    expected_in = (
        "CHECK (((sensitive_category)::text = ANY ((ARRAY['crime'::character varying, "
        "'health'::character varying, 'sex'::character varying, "
        "'politics_religion'::character varying, 'finance'::character varying])::text[])))"
    )
    for table, name in CATEGORY_CHECKS.items():
        assert _check_def(mig["engine"], name) == expected_in, table
    kind_def = _check_def(mig["engine"], KIND_CHECK)
    assert kind_def == (
        "CHECK ((kind = ANY (ARRAY['identity'::text, 'new_person'::text, 'schedule'::text, "
        "'sensitive'::text])))"
    )
    assert mig["before"]["kind_check_def"] == (
        "CHECK ((kind = ANY (ARRAY['identity'::text, 'new_person'::text, 'schedule'::text])))"
    )
    # 새 CHECK 는 정확히 3개 늘었다(kind CHECK 는 이름이 같은 채 교체).
    assert _check_names(mig["engine"]) - mig["before"]["checks"] == set(CATEGORY_CHECKS.values())
    assert mig["before"]["checks"] - _check_names(mig["engine"]) == set()


# ④ 0005 에서 kind='sensitive' 는 CHECK 위반, 0006 뒤에는 성공. 모르는 kind 는 여전히 위반
def test_kind_sensitive_violates_at_0005_and_succeeds_at_0006(mig):
    assert mig["sensitive_at_0005"].orig.diag.constraint_name == KIND_CHECK
    engine = mig["engine"]
    with engine.connect() as c:
        trans = c.begin()
        try:
            c.execute(
                text(
                    "INSERT INTO pending_questions (session_id, user_id, kind, question, options, context) "
                    "VALUES ('chat:mig6-a', 'mig6-a', 'sensitive', 'q', '[]'::jsonb, '{}'::jsonb)"
                )
            )
            n = c.execute(text("SELECT count(*) FROM pending_questions WHERE kind = 'sensitive'")).scalar_one()
        finally:
            trans.rollback()
    assert n == 1
    err = _constraint_violated(
        engine,
        "INSERT INTO pending_questions (session_id, user_id, kind, question, options, context) "
        "VALUES ('chat:mig6-a', 'mig6-a', 'bogus', 'q', '[]'::jsonb, '{}'::jsonb)",
    )
    assert err.orig.diag.constraint_name == KIND_CHECK


# ⑤ 세 표의 sensitive_category -- 범주 5종과 NULL 은 통과, 그 밖은 제약 이름으로 위반
@pytest.mark.parametrize("table", sorted(CATEGORY_CHECKS))
def test_sensitive_category_accepts_five_categories_and_null_only(mig, table):
    insert = {
        "events": (
            "INSERT INTO events (person_id, type, content, raw_utterance, occurred_at, sensitive_category) "
            "VALUES (9101, 'other', 'c', 'r', now(), {v})"
        ),
        "person_facts": (
            "INSERT INTO person_facts (person_id, key, value, confidence, sensitive_category) "
            "VALUES (9101, 'k-' || md5(random()::text), 'v', 0.5, {v})"
        ),
        "schedules": "INSERT INTO schedules (person_id, title, scheduled_at, sensitive_category) VALUES (9101, 't', now(), {v})",
    }[table]
    for category in (*CATEGORIES, None):
        literal = "NULL" if category is None else f"'{category}'"
        with mig["engine"].connect() as c:
            trans = c.begin()
            try:
                c.execute(text(insert.format(v=literal)))
            finally:
                trans.rollback()
    err = _constraint_violated(mig["engine"], insert.format(v="'drugs'"))
    assert err.orig.diag.constraint_name == CATEGORY_CHECKS[table]


# ⑥ upgrade 는 기존 행을 바꾸지 않는다 -- 행 수·값 불변, 새 컬럼은 전부 NULL(소급 없음)
def test_upgrade_changes_no_existing_data(mig):
    assert mig["before"]["counts"] == {
        **{t: 0 for t in _TABLES},
        "users": 1,
        "persons": 1,
        "events": 1,
        "person_facts": 1,
        "schedules": 1,
        "pending_questions": 1,
    }
    assert _counts(mig["engine"]) == mig["before"]["counts"]
    assert _snapshot(mig["engine"]) == mig["before"]["snapshot"]
    with mig["engine"].connect() as c:
        assert c.execute(text("SELECT sensitive_category, consent_question_id FROM events")).all() == [(None, None)]
        assert c.execute(text("SELECT sensitive_category FROM person_facts")).all() == [(None,)]
        assert c.execute(text("SELECT sensitive_category FROM schedules")).all() == [(None,)]
        assert c.execute(text("SELECT privacy_notice_version, privacy_notice_accepted_at FROM users")).all() == [
            (None, None)
        ]


# ⑥-b 모델도 같은 계약 값을 갖는다 -- 범주 5종(순서 고정)·CHECK 문장·kind 4종·새 컬럼 타입·nullable
def test_model_carries_the_same_contract_values():
    from sqlalchemy import BigInteger, CheckConstraint, DateTime, Integer, String

    import app.db.models as models
    from app.db.base import Base

    assert models.SENSITIVE_CATEGORIES == CATEGORIES
    assert models.QUESTION_KINDS == ("identity", "new_person", "schedule", "sensitive")
    sentence = "sensitive_category IN ('crime', 'health', 'sex', 'politics_religion', 'finance')"
    for table in CATEGORY_CHECKS:
        sqltexts = [
            str(c.sqltext)
            for c in Base.metadata.tables[table].constraints
            if isinstance(c, CheckConstraint) and "sensitive_category" in str(c.sqltext)
        ]
        assert sqltexts == [sentence], table
    kind_checks = [
        str(c.sqltext)
        for c in Base.metadata.tables["pending_questions"].constraints
        if isinstance(c, CheckConstraint)
    ]
    assert kind_checks == ["kind IN ('identity', 'new_person', 'schedule', 'sensitive')"]
    expected_types = {
        ("events", "sensitive_category"): String,
        ("events", "consent_question_id"): BigInteger,
        ("person_facts", "sensitive_category"): String,
        ("schedules", "sensitive_category"): String,
        ("users", "privacy_notice_version"): Integer,
        ("users", "privacy_notice_accepted_at"): DateTime,
    }
    assert set(expected_types) == set(NEW_COLUMNS)
    for (table, column), type_cls in expected_types.items():
        col = Base.metadata.tables[table].columns[column]
        assert type(col.type) is type_cls, (table, column)
        assert col.nullable is True and col.server_default is None and not col.foreign_keys
    assert Base.metadata.tables["users"].columns["privacy_notice_accepted_at"].type.timezone is True


# ⑥-c `ResumeInput` 은 `QUESTION_KINDS` 를 그대로 읽는다 -- 코드 수정 없이 sensitive 를 받는다
def test_resume_input_accepts_sensitive_kind_without_code_change():
    from app.agent.types import ResumeInput

    assert ResumeInput(kind="sensitive", context={}, answer="네").kind == "sensitive"


# ⑦ 테이블·인덱스·UNIQUE·FK·PK 는 하나도 늘거나 줄지 않았다
def test_no_table_index_unique_or_fk_is_added(mig):
    assert _structure(mig["engine"]) == mig["before"]["structure"]


# ⑧ alembic check -- 모델과 DB 가 같다
def test_alembic_check_reports_no_new_operations(mig):
    with _in_mig_env(mig["env"]):
        command.check(mig["cfg"])  # 차이가 있으면 CommandError


# ⑨ 빈 상태(민감 행 없음)에서 downgrade -1 -> upgrade head 왕복
def test_downgrade_when_no_sensitive_rows_removes_columns_and_restores_three_kinds(mig):
    engine = mig["engine"]
    with _in_mig_env(mig["env"]):
        command.downgrade(mig["cfg"], "-1")
        try:
            assert _version(engine) == "0005"
            assert {k: _column_info(engine, *k) for k in NEW_COLUMNS} == mig["before"]["new_columns"]
            assert _check_names(engine) == mig["before"]["checks"]
            assert _check_def(engine, KIND_CHECK) == mig["before"]["kind_check_def"]
            assert _snapshot(engine) == mig["before"]["snapshot"]  # 기존 행은 그대로
            assert _counts(engine) == mig["before"]["counts"]
            err = _constraint_violated(
                engine,
                "INSERT INTO pending_questions (session_id, user_id, kind, question, options, context) "
                "VALUES ('chat:mig6-a', 'mig6-a', 'sensitive', 'q', '[]'::jsonb, '{}'::jsonb)",
            )
            assert err.orig.diag.constraint_name == KIND_CHECK
        finally:
            command.upgrade(mig["cfg"], "head")
    assert _version(engine) == "0006"
    assert {k: _column_info(engine, *k)["data_type"] for k in NEW_COLUMNS} == NEW_COLUMNS
    assert _snapshot(engine) == mig["before"]["snapshot"]


# ⑩ 민감 행이 하나라도 있으면 downgrade 는 아무것도 지우지 않고 실패한다 -- 다섯 경우를 각각
_SENSITIVE_CASES = {
    "kind_sensitive_question": (
        "INSERT INTO pending_questions (id, session_id, user_id, kind, question, options, context) "
        "VALUES (9502, 'chat:mig6-a', 'mig6-a', 'sensitive', '민감한 질문 원문', '[]'::jsonb, '{}'::jsonb)",
        "DELETE FROM pending_questions WHERE id = 9502",
        "pending_questions.kind='sensitive' 1건",
    ),
    "event_marked": (
        "INSERT INTO events (id, person_id, type, content, raw_utterance, occurred_at, sensitive_category) "
        "VALUES (9202, 9101, 'other', '민감 사건 내용', '민감 사건 원문', now(), 'health')",
        "DELETE FROM events WHERE id = 9202",
        "events.sensitive_category 1건",
    ),
    "fact_marked": (
        "INSERT INTO person_facts (id, person_id, key, value, confidence, sensitive_category) "
        "VALUES (9302, 9101, '민감키', '민감 값 원문', 0.9, 'finance')",
        "DELETE FROM person_facts WHERE id = 9302",
        "person_facts.sensitive_category 1건",
    ),
    "schedule_marked": (
        "INSERT INTO schedules (id, person_id, title, scheduled_at, sensitive_category) "
        "VALUES (9402, 9101, '민감 일정 제목', now(), 'sex')",
        "DELETE FROM schedules WHERE id = 9402",
        "schedules.sensitive_category 1건",
    ),
    "consent_ref_only": (
        "INSERT INTO events (id, person_id, type, content, raw_utterance, occurred_at, consent_question_id) "
        "VALUES (9203, 9101, 'other', '동의 참조 내용', '동의 참조 원문', now(), 9502)",
        "DELETE FROM events WHERE id = 9203",
        "events.consent_question_id 1건",
    ),
}


@pytest.mark.parametrize("case", sorted(_SENSITIVE_CASES))
def test_downgrade_refuses_and_keeps_everything_when_sensitive_rows_exist(mig, case):
    insert_sql, cleanup_sql, expected_count_text = _SENSITIVE_CASES[case]
    engine = mig["engine"]
    with engine.begin() as c:
        c.execute(text(insert_sql))
    try:
        counts_before = _counts(engine)
        snapshot_before = _snapshot(engine)
        checks_before = {n: _check_def(engine, n) for n in (KIND_CHECK, *CATEGORY_CHECKS.values())}
        with _in_mig_env(mig["env"]):
            with pytest.raises(RuntimeError) as info:
                command.downgrade(mig["cfg"], "-1")
        message = str(info.value)
        assert "0006 downgrade 거부" in message
        assert expected_count_text in message
        # 개수만 담는다 -- 원문 0
        for raw in ("민감한 질문 원문", "민감 사건", "민감 값 원문", "민감 일정 제목", "동의 참조"):
            assert raw not in message
        # 아무것도 지우거나 바꾸지 않았다
        assert _version(engine) == "0006"
        assert {k: _column_info(engine, *k)["data_type"] for k in NEW_COLUMNS} == NEW_COLUMNS
        assert _counts(engine) == counts_before
        assert _snapshot(engine) == snapshot_before
        assert {n: _check_def(engine, n) for n in checks_before} == checks_before
    finally:
        with engine.begin() as c:
            c.execute(text(cleanup_sql))
    # 다음 시험의 `downgrade base` 를 막지 않도록 민감 행이 남지 않았다
    assert _counts(engine) == mig["before"]["counts"]


# ⑪ 고지 컬럼은 downgrade 판정 대상이 아니다 -- 동의 기록만 있는 계정은 downgrade 를 막지 않는다
def test_notice_columns_alone_do_not_block_downgrade(mig):
    engine = mig["engine"]
    with engine.begin() as c:
        c.execute(
            text("UPDATE users SET privacy_notice_version = 1, privacy_notice_accepted_at = now() WHERE id = 'mig6-a'")
        )
    try:
        with _in_mig_env(mig["env"]):
            command.downgrade(mig["cfg"], "-1")
            try:
                assert _version(engine) == "0005"
                assert "privacy_notice_version" not in _columns(engine, "users")
            finally:
                command.upgrade(mig["cfg"], "head")
        assert _version(engine) == "0006"
    finally:
        with engine.begin() as c:
            c.execute(
                text(
                    "UPDATE users SET privacy_notice_version = NULL, privacy_notice_accepted_at = NULL "
                    "WHERE id = 'mig6-a'"
                )
            )
