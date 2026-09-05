"""Refs: P1-schema S3.1 F-ace4dd F-75c1c1 -- app.config 접속 설정 해석 규칙 (DB 없이 실행).

각 테스트는 "어떤 잘못을 잡는가"를 이름에 드러낸다. 실제 DB 접속은 하지 않는다.
"""

from __future__ import annotations

import app.config as cfg


def test_database_url_wins_over_postgres_star_even_when_both_present():
    """DATABASE_URL 이 있으면 POSTGRES_* 값이 달라도 DATABASE_URL 을 우선한다."""
    fake = {
        "DATABASE_URL": "postgresql://urluser:pw1@urlhost:1111/urldb",
        "POSTGRES_USER": "starred",
        "POSTGRES_PASSWORD": "pw2",
        "POSTGRES_DB": "stardb",
        "POSTGRES_PORT": "9999",
    }
    conn, _warnings = cfg.resolve_connection(fake)
    assert conn.source == "DATABASE_URL"
    assert conn.user == "urluser"
    assert conn.host == "urlhost"
    assert conn.port == "1111"
    assert conn.dbname == "urldb"


def test_postgres_star_assembly_falls_back_to_default_host_and_port():
    """DATABASE_URL 이 없으면 POSTGRES_* 로 조립하고, POSTGRES_HOST/PORT 를
    지정하지 않으면 기본값(localhost/5432)을 쓴다."""
    fake = {"POSTGRES_USER": "u", "POSTGRES_PASSWORD": "p", "POSTGRES_DB": "d"}
    conn, warnings = cfg.resolve_connection(fake)
    assert conn.source == "POSTGRES_*"
    assert conn.user == "u"
    assert conn.dbname == "d"
    assert conn.host == "localhost"
    assert conn.port == "5432"
    assert warnings == []


def test_postgres_host_env_var_overrides_default_host():
    """POSTGRES_HOST 를 지정하면(F-75c1c1) 기본값 localhost 대신 그 값을 쓴다."""
    fake = {"POSTGRES_HOST": "remote-db.internal"}
    conn, _warnings = cfg.resolve_connection(fake)
    assert conn.host == "remote-db.internal"


def test_mismatch_warning_names_variable_but_never_leaks_password_value():
    """DATABASE_URL 과 POSTGRES_* 가 어긋나면 변수 "이름"만 경고하고 비밀번호 값은
    경고문·safe_summary 어디에도 나타나지 않는다."""
    pwone = "pwone"
    pwtwo = "pwtwo"
    fake = {
        "DATABASE_URL": f"postgresql://app:{pwone}@localhost:5432/relationship",
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": pwtwo,
        "POSTGRES_DB": "relationship",
        "POSTGRES_PORT": "5433",
    }
    conn, warnings = cfg.resolve_connection(fake)
    joined = " ".join(warnings)

    assert "POSTGRES_PASSWORD" in joined
    assert "POSTGRES_PORT" in joined
    assert "POSTGRES_USER" not in joined
    assert "POSTGRES_DB" not in joined

    assert pwone not in joined
    assert pwtwo not in joined
    assert pwone not in conn.safe_summary()
    assert pwtwo not in conn.safe_summary()


def test_sqlalchemy_url_uses_psycopg_driver_and_hides_password_in_summary():
    """`sqlalchemy_url()` 은 `postgresql+psycopg://` 로 시작하고, 비밀번호는
    URL 안에는 있어도 `safe_summary()` 에는 나타나지 않는다."""
    pw = "pwthree"
    fake = {
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": pw,
        "POSTGRES_DB": "relationship",
        "POSTGRES_PORT": "5433",
    }
    conn, _warnings = cfg.resolve_connection(fake)
    url = conn.sqlalchemy_url()

    assert url.startswith("postgresql+psycopg://")
    assert pw in url  # URL 자체는 접속에 필요하므로 포함
    assert pw not in conn.safe_summary()

    # 모듈 함수 경로도 동일 URL 을 낸다.
    assert cfg.sqlalchemy_url(fake) == url


def test_conninfo_repr_and_str_never_contain_password_value():
    """F-8eeb9b -- ConnInfo.password 는 field(repr=False) 이므로 기본
    dataclass repr/str(예외 메시지·로그에 그대로 찍힐 수 있는 경로) 어디에도
    비밀번호 값이 나타나지 않는다(security.md §1)."""
    secret = "UNIQUE_MARKER_9f3a21"
    fake = {
        "POSTGRES_USER": "app",
        "POSTGRES_PASSWORD": secret,
        "POSTGRES_DB": "relationship",
        "POSTGRES_PORT": "5433",
    }
    conn, _warnings = cfg.resolve_connection(fake)

    assert secret not in repr(conn)
    assert secret not in str(conn)
    assert secret not in f"{conn}"
    # 필드 자체는 여전히 살아 있다 -- 접속에는 필요하다.
    assert conn.password == secret
