"""Refs: P1-schema S3.1 -- DB 접속 설정의 단일 구현.

이 모듈이 접속 정보 해석 규칙(우선순위·변수 이름·경고 문구)의 유일한 출처다
(F-ace4dd). `scripts/db_check.py` 는 여기서 `ConnInfo`/`parse_database_url`/
`resolve_connection` 을 import 해서 쓴다 -- 같은 로직을 두 곳에 두지 않는다.

동작 (scripts/db_check.py 와 완전히 동일):
  1. 환경변수 `DATABASE_URL` 이 있으면 그것으로 접속 정보를 만든다. 없으면
     `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` / `POSTGRES_PORT`
     (없는 것은 기본값 app / pass / relationship / 5432)와
     `POSTGRES_HOST`(선택, 기본값 `localhost` -- 컨테이너 밖에서 접속할 때만 바꾼다)로
     접속 정보를 조립한다.
  2. `DATABASE_URL` 과 `POSTGRES_*` 가 둘 다 있고 값이 어긋나면 어긋난 변수
     "이름"만 경고로 낸다. 비밀번호 값·접속 문자열 전체는 어떤 경우에도
     출력하지 않는다.
  3. `.env` 파일은 읽지도 쓰지도 않는다(security.md §1). 값은 `os.environ`
     에서만 읽는다(`resolve_connection` 에 dict 를 직접 넘기는 것은 테스트
     전용 경로).

SQLAlchemy 가 쓸 접속 URL 은 `ConnInfo.sqlalchemy_url()` (또는 모듈 함수
`sqlalchemy_url()`)로 만든다. 드라이버는 `postgresql+psycopg://`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote, urlsplit

DEFAULT_USER = "app"
DEFAULT_PASSWORD = "pass"
DEFAULT_DB = "relationship"
DEFAULT_PORT = "5432"
DEFAULT_HOST = "localhost"


@dataclass
class ConnInfo:
    """접속 정보. 이 값을 출력할 때는 password 필드를 절대 포함하지 않는다."""

    user: str
    password: str
    host: str
    port: str
    dbname: str
    source: str  # "DATABASE_URL" | "POSTGRES_*"

    def as_keywords(self) -> dict[str, str]:
        """psycopg.connect(**kwargs) 에 넘길 키워드. 반환값을 로그에 찍지 않는다."""
        return {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
        }

    def safe_summary(self) -> str:
        """비밀번호를 뺀 요약. 출력용."""
        return (
            f"user={self.user} host={self.host} port={self.port} "
            f"dbname={self.dbname} (source={self.source})"
        )

    def sqlalchemy_url(self) -> str:
        """SQLAlchemy 2.x(psycopg3 드라이버)용 접속 URL. 비밀번호는 URL 인코딩한다.

        반환값을 로그·예외 메시지에 그대로 찍지 않는다 -- 비밀번호가 포함된다.
        """
        user = quote(self.user, safe="")
        password = quote(self.password, safe="")
        return f"postgresql+psycopg://{user}:{password}@{self.host}:{self.port}/{self.dbname}"


def parse_database_url(url: str) -> dict[str, str]:
    """DATABASE_URL 을 user/password/host/port/dbname 으로 분해한다."""
    parts = urlsplit(url)
    dbname = parts.path.lstrip("/")
    return {
        "user": parts.username or "",
        "password": parts.password or "",
        "host": parts.hostname or DEFAULT_HOST,
        "port": str(parts.port) if parts.port else DEFAULT_PORT,
        "dbname": dbname or DEFAULT_DB,
    }


def resolve_connection(env: dict[str, str] | None = None) -> tuple[ConnInfo, list[str]]:
    """환경변수 dict 에서 접속 정보와 불일치 경고 목록을 만든다.

    `env` 를 생략하면 `os.environ` 을 읽는다(실제 실행 경로). 테스트는 평범한
    dict 를 직접 넘겨 `os.environ` 을 건드리지 않고 이 함수를 검증한다.
    """
    if env is None:
        env = dict(os.environ)

    warnings: list[str] = []
    database_url = env.get("DATABASE_URL")

    postgres_present = any(
        k in env for k in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_PORT")
    )
    postgres = {
        "user": env.get("POSTGRES_USER", DEFAULT_USER),
        "password": env.get("POSTGRES_PASSWORD", DEFAULT_PASSWORD),
        "dbname": env.get("POSTGRES_DB", DEFAULT_DB),
        "port": env.get("POSTGRES_PORT", DEFAULT_PORT),
    }

    if database_url:
        parsed = parse_database_url(database_url)
        conn = ConnInfo(
            user=parsed["user"] or postgres["user"],
            password=parsed["password"] or postgres["password"],
            host=parsed["host"],
            port=parsed["port"],
            dbname=parsed["dbname"],
            source="DATABASE_URL",
        )
        if postgres_present:
            # 어긋난 변수 이름만 경고 -- 값은 출력하지 않는다.
            if env.get("POSTGRES_USER") is not None and parsed["user"] != env["POSTGRES_USER"]:
                warnings.append("[warn] POSTGRES_USER 가 DATABASE_URL 과 다르다")
            if (
                env.get("POSTGRES_PASSWORD") is not None
                and parsed["password"] != env["POSTGRES_PASSWORD"]
            ):
                warnings.append("[warn] POSTGRES_PASSWORD 가 DATABASE_URL 과 다르다")
            if env.get("POSTGRES_DB") is not None and parsed["dbname"] != env["POSTGRES_DB"]:
                warnings.append("[warn] POSTGRES_DB 가 DATABASE_URL 과 다르다")
            if env.get("POSTGRES_PORT") is not None and parsed["port"] != env["POSTGRES_PORT"]:
                warnings.append("[warn] POSTGRES_PORT 가 DATABASE_URL 과 다르다")
        return conn, warnings

    # DATABASE_URL 이 없으면 POSTGRES_* (없으면 기본값)로 조립한다.
    conn = ConnInfo(
        user=postgres["user"],
        password=postgres["password"],
        host=env.get("POSTGRES_HOST", DEFAULT_HOST),
        port=postgres["port"],
        dbname=postgres["dbname"],
        source="POSTGRES_*",
    )
    return conn, warnings


def sqlalchemy_url(env: dict[str, str] | None = None) -> str:
    """`resolve_connection` 결과로 SQLAlchemy 접속 URL 문자열을 만든다.

    편의 함수 -- `alembic/env.py` 등에서 `ConnInfo` 를 거치지 않고 바로 쓴다.
    """
    conn, _warnings = resolve_connection(env)
    return conn.sqlalchemy_url()
