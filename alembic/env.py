"""Refs: P1-schema R8 R9 D4 D5 S3.1 -- Alembic 실행 환경.

`alembic.ini` 의 `sqlalchemy.url` 은 비워 둔다(비밀 금지, security.md §1).
접속 정보는 이 파일이 `app.config.resolve_connection()` 으로 `os.environ`
에서 해석해 런타임에만 주입한다 -- `DATABASE_URL` 이 있으면 그것을, 없으면
`POSTGRES_*`(+ 기본값)로 조립한다. `scripts/db_check.py`/`app/config.py`
와 완전히 같은 우선순위·같은 변수 이름이다(단일 구현, F-ace4dd).

접속 URL 문자열(비밀번호 포함)은 어떤 경우에도 로그·예외 메시지에 찍지
않는다. `alembic` 이 자체적으로 찍는 로그도 `sqlalchemy.url` 값을 그대로
쓰지 않도록 `config.set_main_option` 으로만 주입하고 별도 print 를 하지
않는다(설정을 확인하고 싶으면 `ConnInfo.safe_summary()` 를 쓴다).

`render_item` 훅: `pgvector.sqlalchemy.Vector` 는 Alembic autogenerate 가
기본으로 인식하지 못해 `NullType` 으로 흘리거나 import 를 빠뜨릴 수 있다
(01-plan 리스크). 여기서 명시적으로 `Vector(N)` 문자열로 렌더하고
`autogen_context.imports` 에 import 문을 추가해 이 문제를 막는다.
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool

from alembic import context

# 저장소 루트를 sys.path 에 추가해 `app` 패키지를 import 할 수 있게 한다.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import resolve_connection  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db import models  # noqa: E402,F401  -- import 로 테이블을 메타데이터에 등록

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 대상 메타데이터 -- app/db/models.py 가 진실의 원천(01-plan 결정 1).
target_metadata = Base.metadata

# 접속 정보는 os.environ 에서만 해석한다(.env 미접촉, security.md §1).
# 반환값(URL 문자열)에 비밀번호가 포함되므로 여기서 print/log 하지 않는다.
_conn_info, _warnings = resolve_connection()
config.set_main_option("sqlalchemy.url", _conn_info.sqlalchemy_url())


def render_item(type_, obj, autogen_context):
    """pgvector Vector 타입을 `Vector(N)` 으로 렌더하고 import 를 추가한다.

    이걸 하지 않으면 autogenerate 가 `person_aliases.embedding` 컬럼을
    `NullType` 이나 import 누락 상태로 낼 수 있다(01-plan 리스크).
    """
    if type_ == "type" and type(obj).__module__.startswith("pgvector"):
        autogen_context.imports.add("from pgvector.sqlalchemy import Vector")
        return f"Vector({obj.dim})"
    # 기본 렌더러를 계속 쓰게 한다.
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_item=render_item,
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item,
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
