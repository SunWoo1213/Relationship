"""Refs: P1-schema R8 R9 D4 D5 S3.1 F-08e812 -- app.db.models 메타데이터 검사 (DB 없이 실행).

각 테스트는 "어떤 잘못을 잡는가"를 이름에 드러낸다. `Base.metadata` 만 읽고
실제 DB 접속은 하지 않는다.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, DateTime, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import CreateTable

import app.db.models as m
from app.db.base import Base

# S3.1 권위 정의 (docs/wiki/specs/S3.1-schema-v2.md) -- 이 집합과 글자 그대로 대응해야 한다.
S3_1_TABLE_COLUMNS = {
    "persons": {
        "id",
        "user_id",
        "display_name",
        "relation_tag",
        "hierarchy",
        "created_at",
        "updated_at",
    },
    "person_aliases": {
        "id",
        "person_id",
        "alias",
        "source",
        "embedding",
        "confirmed_at",
    },
    "person_facts": {
        "id",
        "person_id",
        "key",
        "value",
        "confidence",
        "updated_at",
    },
    "fact_sources": {"fact_id", "event_id"},
    "events": {
        "id",
        "person_id",
        "type",
        "content",
        "raw_utterance",
        "occurred_at",
        "created_at",
    },
    "schedules": {"id", "person_id", "title", "scheduled_at", "briefed_at"},
    "pending_questions": {
        "id",
        "session_id",
        "kind",
        "question",
        "options",
        "context",
        "answer",
        "created_at",
        "answered_at",
    },
    "push_subscriptions": {"id", "user_id", "endpoint", "keys", "created_at"},
    "agent_traces": {
        "id",
        "session_id",
        "step",
        "tool_name",
        "input",
        "output",
        "tokens_in",
        "tokens_out",
        "created_at",
    },
}

NULLABLE_COLUMNS = {"embedding", "confirmed_at", "briefed_at", "answer", "answered_at"}

JSONB_COLUMNS = {
    ("pending_questions", "options"),
    ("pending_questions", "context"),
    ("push_subscriptions", "keys"),
    ("agent_traces", "input"),
    ("agent_traces", "output"),
}

TIMESTAMP_COLUMNS = {
    ("persons", "created_at"),
    ("persons", "updated_at"),
    ("person_aliases", "confirmed_at"),
    ("person_facts", "updated_at"),
    ("events", "occurred_at"),
    ("events", "created_at"),
    ("schedules", "scheduled_at"),
    ("schedules", "briefed_at"),
    ("pending_questions", "created_at"),
    ("pending_questions", "answered_at"),
    ("push_subscriptions", "created_at"),
    ("agent_traces", "created_at"),
}

# FK: (table, column, referred_table, referred_column)
EXPECTED_FKS = {
    ("person_aliases", "person_id", "persons", "id"),
    ("person_facts", "person_id", "persons", "id"),
    ("events", "person_id", "persons", "id"),
    ("schedules", "person_id", "persons", "id"),
    ("fact_sources", "fact_id", "person_facts", "id"),
    ("fact_sources", "event_id", "events", "id"),
}


def _table(name: str):
    return Base.metadata.tables[name]


def test_table_name_set_matches_s3_1_exactly_and_person_embeddings_absent():
    """9개 테이블 이름이 S3.1 과 정확히 같고 person_embeddings 는 없다(D5 R9)."""
    names = set(Base.metadata.tables.keys())
    assert names == set(S3_1_TABLE_COLUMNS.keys())
    assert len(names) == 9
    assert "person_embeddings" not in names


def test_each_table_column_set_matches_s3_1_exactly():
    """각 테이블 컬럼 이름 집합이 S3.1 과 정확히 같다(누락·추가 모두 실패)."""
    for table_name, expected_columns in S3_1_TABLE_COLUMNS.items():
        table = _table(table_name)
        actual_columns = {c.name for c in table.columns}
        assert actual_columns == expected_columns, (
            f"{table_name}: expected={expected_columns} actual={actual_columns}"
        )


def test_total_column_count_equals_56_verified_by_literal_transcription_of_s3_1():
    """S3.1 컬럼을 테이블별로 세어 합산하면 56개다 (위임 프롬프트의 "55" 는 오기 —
    03-log 에 근거 표와 함께 기록)."""
    total = sum(len(cols) for cols in S3_1_TABLE_COLUMNS.values())
    actual_total = sum(len(t.columns) for t in Base.metadata.tables.values())
    assert total == 56
    assert actual_total == 56


def _check_constraints(table_name: str) -> list[CheckConstraint]:
    table = _table(table_name)
    return [c for c in table.constraints if isinstance(c, CheckConstraint)]


def test_events_type_check_contains_all_seven_event_types():
    """events.type CHECK 이 EVENT_TYPES 7개 값을 모두 포함한다."""
    checks = _check_constraints("events")
    assert len(checks) == 1
    sql_text = str(checks[0].sqltext)
    assert len(m.EVENT_TYPES) == 7
    for value in m.EVENT_TYPES:
        assert value in sql_text


def test_persons_relation_tag_check_contains_all_five_tags():
    """persons.relation_tag CHECK 이 RELATION_TAGS 5개 값을 모두 포함한다."""
    checks = _check_constraints("persons")
    relation_check = [c for c in checks if "relation_tag" in str(c.sqltext)]
    assert len(relation_check) == 1
    sql_text = str(relation_check[0].sqltext)
    assert len(m.RELATION_TAGS) == 5
    for value in m.RELATION_TAGS:
        assert value in sql_text


def test_persons_hierarchy_check_contains_all_three_values():
    """persons.hierarchy CHECK 이 HIERARCHIES 3개 값을 모두 포함한다."""
    checks = _check_constraints("persons")
    hierarchy_check = [c for c in checks if "hierarchy" in str(c.sqltext)]
    assert len(hierarchy_check) == 1
    sql_text = str(hierarchy_check[0].sqltext)
    assert len(m.HIERARCHIES) == 3
    for value in m.HIERARCHIES:
        assert value in sql_text


def test_pending_questions_kind_check_contains_all_three_kinds():
    """pending_questions.kind CHECK 이 QUESTION_KINDS 3개 값을 모두 포함한다."""
    checks = _check_constraints("pending_questions")
    assert len(checks) == 1
    sql_text = str(checks[0].sqltext)
    assert len(m.QUESTION_KINDS) == 3
    for value in m.QUESTION_KINDS:
        assert value in sql_text


def test_exactly_four_check_constraints_exist_total():
    """CHECK 제약이 정확히 4개(events, persons x2, pending_questions)다."""
    total = sum(
        len(_check_constraints(t))
        for t in ("events", "persons", "pending_questions", "person_aliases", "person_facts",
                   "fact_sources", "schedules", "push_subscriptions", "agent_traces")
    )
    assert total == 4


def test_all_six_foreign_keys_have_ondelete_cascade():
    """FK 6개 모두 ondelete='CASCADE' 이고 기대한 (table, col, ref_table, ref_col) 집합과 같다."""
    found = set()
    for table in Base.metadata.tables.values():
        for fk in table.foreign_keys:
            assert fk.ondelete == "CASCADE", f"{table.name}.{fk.parent.name} ondelete={fk.ondelete}"
            found.add((table.name, fk.parent.name, fk.column.table.name, fk.column.name))
    assert found == EXPECTED_FKS
    assert len(found) == 6


def test_fact_sources_has_composite_primary_key_and_no_surrogate_id_column():
    """fact_sources 는 대리키 id 가 없고 PK 가 정확히 {fact_id, event_id} 다."""
    table = _table("fact_sources")
    pk_columns = {c.name for c in table.primary_key.columns}
    assert pk_columns == {"fact_id", "event_id"}
    assert "id" not in {c.name for c in table.columns}


def test_person_aliases_embedding_is_nullable_vector_of_dimension_1536():
    """person_aliases.embedding 이 Vector(1536) 이고 nullable 이다(D4 D5)."""
    table = _table("person_aliases")
    column = table.columns["embedding"]
    assert type(column.type).__name__ == "VECTOR"  # pgvector.sqlalchemy.Vector 별칭
    assert column.type.dim == 1536
    assert column.nullable is True


def test_nullable_columns_are_exactly_the_five_deferred_fields():
    """nullable 컬럼이 정확히 {embedding, confirmed_at, briefed_at, answer, answered_at} 뿐이다(F-08e812)."""
    nullable_found = set()
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if column.nullable:
                nullable_found.add(column.name)
    assert nullable_found == NULLABLE_COLUMNS


def test_not_null_columns_cover_all_tool_signature_required_arguments():
    """S3.2 필수 인자에 대응하는 컬럼들이 전부 NOT NULL 이다."""
    required_not_null = {
        ("events", "person_id"),
        ("events", "type"),
        ("events", "content"),
        ("events", "occurred_at"),
        ("events", "raw_utterance"),
        ("schedules", "person_id"),
        ("schedules", "title"),
        ("schedules", "scheduled_at"),
        ("pending_questions", "kind"),
        ("pending_questions", "question"),
        ("pending_questions", "options"),
        ("pending_questions", "context"),
    }
    for table_name, column_name in required_not_null:
        column = _table(table_name).columns[column_name]
        assert column.nullable is False, f"{table_name}.{column_name} should be NOT NULL"


def test_jsonb_columns_have_jsonb_type():
    """options/context/keys/input/output 5개 컬럼이 JSONB 타입이다."""
    assert len(JSONB_COLUMNS) == 5
    for table_name, column_name in JSONB_COLUMNS:
        column = _table(table_name).columns[column_name]
        assert isinstance(column.type, JSONB)


def test_all_timestamp_columns_are_timezone_aware():
    """모든 타임스탬프 컬럼이 DateTime(timezone=True) 다."""
    for table_name, column_name in TIMESTAMP_COLUMNS:
        column = _table(table_name).columns[column_name]
        assert isinstance(column.type, DateTime)
        assert column.type.timezone is True


EXPECTED_INDEXES = {
    "persons": [("ix_persons_user_id", None)],
    "person_aliases": [
        ("ix_person_aliases_person_id", None),
        ("ix_person_aliases_alias", None),
    ],
    "events": [("ix_events_person_id_occurred_at", None)],
    "schedules": [("ix_schedules_scheduled_at", None)],
    "pending_questions": [
        ("ix_pending_questions_session_id_created_at", None),
        ("ix_pending_questions_session_id_unanswered", "partial"),
    ],
    "person_facts": [("ix_person_facts_person_id_key", None)],
    "fact_sources": [("ix_fact_sources_event_id", None)],
    "agent_traces": [("ix_agent_traces_session_id_created_at", None)],
}


def test_all_expected_indexes_exist_with_partial_index_having_postgresql_where():
    """계획의 인덱스 목록(부분 인덱스 포함) 10개가 각 테이블에 존재한다."""
    total = 0
    for table_name, expected in EXPECTED_INDEXES.items():
        table = _table(table_name)
        index_by_name: dict[str, Index] = {ix.name: ix for ix in table.indexes}
        for index_name, kind in expected:
            assert index_name in index_by_name, f"missing index {index_name} on {table_name}"
            total += 1
            if kind == "partial":
                where_clause = index_by_name[index_name].dialect_options["postgresql"]["where"]
                assert where_clause is not None
    assert total == 10


def test_ddl_compiles_with_vector_1536_and_on_delete_cascade_in_postgresql_dialect():
    """PostgreSQL dialect 로 컴파일한 DDL 에 vector(1536) 과 ON DELETE CASCADE 가 나온다."""
    aliases_ddl = str(CreateTable(_table("person_aliases")).compile(dialect=postgresql.dialect()))
    assert "VECTOR(1536)" in aliases_ddl.upper()

    events_ddl = str(CreateTable(_table("events")).compile(dialect=postgresql.dialect()))
    assert "ON DELETE CASCADE" in events_ddl

    fact_sources_ddl = str(
        CreateTable(_table("fact_sources")).compile(dialect=postgresql.dialect())
    )
    assert fact_sources_ddl.count("ON DELETE CASCADE") == 2
