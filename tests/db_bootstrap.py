"""Refs: FIX-006 -- 테스트 전용 DB 이름 계산 + DB/확장/마이그레이션 준비.

`tests/conftest.py` 가 앱·엔진을 import 하기 **전에** 호출해야 하는 로직을
이 파일로 분리했다 -- 이렇게 분리하면 이름 계산(순수 함수)만 따로 단위
테스트할 수 있다(FIX-006 수정안 5행 ③, `tests/test_conftest_test_db.py`).

파일 이름이 `test_` 로 시작하지 않으므로 pytest 가 이 파일 자체를 테스트로
수집하지 않는다 -- 순수한 헬퍼 모듈이다.

이 파일 어디에도 개발 DB 를 지우거나(`DROP`) 비우는(`TRUNCATE`) 코드는
없다. `ensure_test_database_ready()` 는 테스트 DB 가 없을 때 **만들기만**
한다(security.md, FIX-006 승인 방식).
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text

DEFAULT_TEST_DB_NAME = "relationship_test"


class DBNameCollisionError(RuntimeError):
    """테스트 DB 이름이 개발 DB 이름과 같을 때 낸다 -- 개발 DB 를 실수로
    테스트가 건드리는 사고를 막는 안전장치다(FIX-006)."""


def resolve_test_db_name(dev_db_name: str, env: dict[str, str] | None = None) -> str:
    """테스트 DB 이름을 정한다. 개발 DB 이름과 같으면 즉시 예외를 낸다.

    `env` 를 생략하면 `os.environ` 을 읽는다(실제 실행 경로). 테스트는 평범한
    dict 를 직접 넘겨 `os.environ` 을 건드리지 않고 이 함수만 검증한다.
    """
    if env is None:
        env = dict(os.environ)
    test_db_name = env.get("TEST_POSTGRES_DB", DEFAULT_TEST_DB_NAME)
    if test_db_name == dev_db_name:
        raise DBNameCollisionError(
            "FIX-006: 테스트 DB 이름이 개발 DB 이름과 같습니다 "
            f"({test_db_name!r}). TEST_POSTGRES_DB 를 개발 DB(POSTGRES_DB="
            f"{dev_db_name!r} 또는 DATABASE_URL 의 DB 이름)와 다른 값으로 "
            "설정하세요 -- 이 확인은 테스트가 개발 DB 를 건드리는 사고를 "
            "막기 위한 안전장치입니다."
        )
    return test_db_name


def swap_database_url_dbname(url: str, new_dbname: str) -> str:
    """`url` 의 DB 이름만 `new_dbname` 으로 바꾼다(호스트·포트·계정은 유지)."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, f"/{new_dbname}", parts.query, parts.fragment))


def apply_test_database_env(env: dict[str, str] | None = None) -> tuple[str, str]:
    """환경을 테스트 DB 를 가리키도록 바꾼다. `(개발 DB 이름, 테스트 DB 이름)` 반환.

    `env` 가 `None` 이면 `os.environ` 을 실제로 변형한다(운영 경로) --
    `tests/conftest.py` 가 `app.db.session`/`app.embedding` 을 import 하기
    **전에** 이 함수를 호출해야 한다. `get_engine()` 은 최초 호출 시점의
    `os.environ` 을 읽어 엔진을 모듈 전역에 캐시하므로, 한 번이라도 개발 DB
    이름으로 먼저 만들어지면 그 뒤로는 이름을 바꿔도 되돌릴 수 없다.
    """
    from app.config import resolve_connection  # 지연 import: 순수 함수, DB 접속 없음

    target = os.environ if env is None else env
    dev_conn, _warnings = resolve_connection(dict(target))
    test_db_name = resolve_test_db_name(dev_conn.dbname, dict(target))

    if target.get("DATABASE_URL"):
        target["DATABASE_URL"] = swap_database_url_dbname(target["DATABASE_URL"], test_db_name)
    else:
        target["POSTGRES_DB"] = test_db_name
    # DATABASE_URL 이 우선이라 실제 접속에는 안 쓰이지만, 같은 프로세스 안의
    # 다른 코드가 POSTGRES_DB 를 직접 읽을 경우를 대비해 값을 맞춰 둔다.
    if "POSTGRES_DB" in target:
        target["POSTGRES_DB"] = test_db_name

    return dev_conn.dbname, test_db_name


def ensure_test_database_ready(test_db_url: str, *, repo_root: Path) -> None:
    """테스트 DB 가 없으면 만들고, `vector` 확장과 `alembic upgrade head` 를
    적용한다. 이미 있으면 확장 확인 + upgrade 만 한다(둘 다 멱등이라 매
    세션 호출해도 안전하다). 개발 DB 를 지우거나 비우는 코드는 여기 없다.
    """
    parts = urlsplit(test_db_url)
    db_name = parts.path.lstrip("/")
    admin_url = urlunsplit((parts.scheme, parts.netloc, "/postgres", parts.query, parts.fragment))

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar_one_or_none()
            if exists is None:
                # CREATE DATABASE 는 트랜잭션 안에서 실행할 수 없다(AUTOCOMMIT
                # 필요). 식별자는 신뢰할 수 없는 사용자 입력이 아니라 우리가
                # 만든 테스트 DB 이름(TEST_POSTGRES_DB)뿐이지만, 따옴표는
                # 그대로 이스케이프한다.
                safe_name = db_name.replace('"', '""')
                conn.execute(text(f'CREATE DATABASE "{safe_name}"'))
    finally:
        admin_engine.dispose()

    test_engine = create_engine(test_db_url)
    try:
        with test_engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    finally:
        test_engine.dispose()

    _run_alembic_upgrade(repo_root)


def _run_alembic_upgrade(repo_root: Path) -> None:
    """`alembic upgrade head` 를 파이썬 API 로 실행한다.

    `alembic/env.py` 가 `app.config.resolve_connection()` 으로 `os.environ`
    에서 접속 정보를 읽으므로(단일 구현, F-ace4dd), 이 시점에 이미
    `apply_test_database_env()` 가 환경을 테스트 DB 로 바꿔 둔 상태여야
    한다 -- 그래야 이 upgrade 가 테스트 DB 에 적용된다.
    """
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(repo_root / "alembic.ini"))
    # script_location 은 alembic.ini 안에 상대경로("alembic")로만 적혀 있어
    # 현재 작업 디렉터리에 좌우된다 -- pytest 를 저장소 루트가 아닌 곳에서
    # 실행해도 항상 올바른 위치를 찾도록 명시적으로 절대경로를 넣는다.
    cfg.set_main_option("script_location", str(repo_root / "alembic"))
    command.upgrade(cfg, "head")
