"""Refs: P0-compose D4 D5 S3.1 · P1-schema(F-ace4dd 접속 조립을 app.config 로 단일화) -- 로컬 pgvector 접속 검사.

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
from pathlib import Path

# 스크립트로 직접 실행될 때(`python scripts/db_check.py`) `app` 패키지를
# 찾을 수 있도록 저장소 루트를 sys.path 에 넣는다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 접속 설정 해석 규칙의 단일 구현은 app.config 다(F-ace4dd). 여기서는
# re-export 만 해서 기존 호출부(main 아래)와 tests/test_db_check.py 가
# `db_check.resolve_connection` 등을 그대로 쓸 수 있게 한다.
from app.config import (  # noqa: E402
    DEFAULT_DB,
    DEFAULT_HOST,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_USER,
    ConnInfo,
    parse_database_url,
    resolve_connection,
)

__all__ = [
    "DEFAULT_DB",
    "DEFAULT_HOST",
    "DEFAULT_PASSWORD",
    "DEFAULT_PORT",
    "DEFAULT_USER",
    "ConnInfo",
    "parse_database_url",
    "resolve_connection",
    "run_checks",
    "main",
]


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
