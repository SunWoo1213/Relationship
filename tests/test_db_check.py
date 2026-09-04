"""Refs: P0-compose D4 D5 S3.1 -- db_check 의 접속 정보 조립·불일치 경고 로직 테스트 (DB 없이 실행)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import db_check as dc  # noqa: E402


def test_postgres_only_assembles_conninfo():
    """DATABASE_URL 없이 POSTGRES_* 만 있을 때 그 값으로 조립한다."""
    fake = {
        "POSTGRES_USER": "someone",
        "POSTGRES_PASSWORD": "s3cr3t",
        "POSTGRES_DB": "reldb",
        "POSTGRES_PORT": "5544",
    }
    conn, warnings = dc.resolve_connection(fake)
    assert conn.user == "someone"
    assert conn.password == "s3cr3t"
    assert conn.dbname == "reldb"
    assert conn.port == "5544"
    assert conn.host == dc.DEFAULT_HOST
    assert conn.source == "POSTGRES_*"
    assert warnings == []


def test_defaults_used_when_nothing_set():
    """DATABASE_URL 도 POSTGRES_* 도 없으면 compose 기본값(app/pass/relationship/5432)으로 조립한다."""
    conn, warnings = dc.resolve_connection({})
    assert conn.user == dc.DEFAULT_USER
    assert conn.password == dc.DEFAULT_PASSWORD
    assert conn.dbname == dc.DEFAULT_DB
    assert conn.port == dc.DEFAULT_PORT
    assert conn.host == dc.DEFAULT_HOST
    assert conn.source == "POSTGRES_*"
    assert warnings == []


def test_database_url_used_when_present_without_mismatch():
    fake = {"DATABASE_URL": "postgresql://app:pass@localhost:5432/relationship"}
    conn, warnings = dc.resolve_connection(fake)
    assert conn.user == "app"
    assert conn.host == "localhost"
    assert conn.port == "5432"
    assert conn.dbname == "relationship"
    assert conn.source == "DATABASE_URL"
    assert warnings == []


def test_mismatch_warns_variable_name_only_no_secret_value():
    """DATABASE_URL 과 POSTGRES_* 가 어긋나면 어긋난 변수 이름만 경고하고, 비밀번호 값은 어디에도 없다."""
    url_pw = "pwone"
    star_pw = "pwtwo"
    db_url = "postgresql://app:" + url_pw + "@localhost:5432/relationship"
    fake = {
        "DATABASE_URL": db_url,
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": star_pw,
        "POSTGRES_DB": "relationship",
        "POSTGRES_PORT": "5433",
    }
    conn, warnings = dc.resolve_connection(fake)

    joined = " ".join(warnings)
    assert "POSTGRES_PORT" in joined
    assert "POSTGRES_PASSWORD" in joined
    assert "POSTGRES_USER" not in joined
    assert "POSTGRES_DB" not in joined

    assert url_pw not in joined
    assert star_pw not in joined

    summary = conn.safe_summary()
    assert url_pw not in summary
    assert star_pw not in summary
    assert conn.password not in summary


def test_no_warning_when_postgres_star_matches_database_url():
    fake = {
        "DATABASE_URL": "postgresql://app:pass@localhost:5432/relationship",
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": "pass",
        "POSTGRES_DB": "relationship",
        "POSTGRES_PORT": "5432",
    }
    _conn, warnings = dc.resolve_connection(fake)
    assert warnings == []


def test_parse_database_url_extracts_fields():
    parsed = dc.parse_database_url("postgresql://u:p@h:1234/d")
    assert parsed == {"user": "u", "password": "p", "host": "h", "port": "1234", "dbname": "d"}
