"""Refs: P0-compose D4 D5 S3.1 -- 로컬 pgvector 접속 검사.

설치(필요 시): pip install "psycopg[binary]"
사용:
    python scripts/db_check.py

동작:
  1. 환경변수 DATABASE_URL 이 있으면 그것으로 접속한다. 없으면
     POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB / POSTGRES_PORT
     (없는 것은 compose 기본값 app / pass / relationship / 5432, host는 localhost)로
     접속 정보를 조립한다.
  2. DATABASE_URL 과 POSTGRES_* 가 둘 다 있고 값이 어긋나면 어긋난 변수 이름만
     경고로 찍는다 (예: "[warn] POSTGRES_PORT 가 DATABASE_URL 과 다르다").
     비밀번호 값·접속 문자열 전체는 어떤 경우에도 출력하지 않는다. 경고는 종료 코드를
     바꾸지 않는다(수용 기준은 쿼리 성공 여부로만 판정한다 -- 01-plan U2).
  3. CREATE EXTENSION IF NOT EXISTS vector; 실행
  4. SELECT extversion FROM pg_extension WHERE extname='vector' 조회·출력
  5. SELECT '[1,2,3]'::vector 실행·결과를 그대로 출력 (수용 기준 문장)
  6. 실패(접속 불가·확장 없음·캐스트 실패) 시 비정상 종료(rc=1).
     psycopg 가 설치되어 있지 않으면 설치 명령을 안내하고 rc=2 로 종료한다.

종료 코드:
    0 = 성공 (SELECT '[1,2,3]'::vector 까지 성공)
    1 = 접속/쿼리 실패
    2 = psycopg 미설치
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from urllib.parse import urlsplit

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


def resolve_connection(env: dict[str, str]) -> tuple[ConnInfo, list[str]]:
    """환경변수 dict 에서 접속 정보와 불일치 경고 목록을 만든다.

    env 는 os.environ 대신 넘길 수 있는 평범한 dict -- 테스트에서 os.environ 을
    건드리지 않고 이 함수를 검증하기 위함.
    """
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


def run_checks(conn: ConnInfo) -> int:
    """실제 DB 접속·쿼리 3개 실행. 성공 시 0, 실패 시 1 반환."""
    try:
        import psycopg
    except ImportError:
        print("[error] psycopg 가 설치되어 있지 않다.")
        print('        설치: pip install "psycopg[binary]"')
        return 2

    print(f"[info] 접속 대상: {conn.safe_summary()}")
    try:
        # 키워드 인자로 접속한다 -- URL 문자열을 조립해 로그·소스에 남기지 않는다.
        with psycopg.connect(connect_timeout=5, **conn.as_keywords()) as pg_conn:
            with pg_conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                pg_conn.commit()
                print("[ok] CREATE EXTENSION IF NOT EXISTS vector;")

                cur.execute("SELECT extversion FROM pg_extension WHERE extname='vector'")
                row = cur.fetchone()
                extversion = row[0] if row else None
                print(f"[ok] extversion = {extversion}")

                cur.execute("SELECT '[1,2,3]'::vector")
                row = cur.fetchone()
                print(f"[ok] SELECT '[1,2,3]'::vector -> {row[0]}")
    except Exception as exc:  # noqa: BLE001 -- 접속·쿼리 실패를 모두 rc=1 로 통일
        print(f"[error] DB 접속/쿼리 실패: {type(exc).__name__}: {exc}")
        return 1
    return 0


def main() -> int:
    conn, warnings = resolve_connection(dict(os.environ))
    for w in warnings:
        print(w)
    return run_checks(conn)


if __name__ == "__main__":
    sys.exit(main())
