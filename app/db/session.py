"""Refs: P2-tools S3.2 -- 엔진·세션 팩토리·트랜잭션 경계.

`create_app()`(U8)은 이 모듈을 import 해도 엔진을 만들지 않는다(리스크 A) --
`get_engine()` 은 **지연 생성**(최초 호출 시 1회, 모듈 캐시)이라서, `app`
을 import 하는 것만으로 `POSTGRES_*`/`DATABASE_URL` 환경변수에 접속을
시도하지 않는다. 접속 확인은 `GET /health` 가 요청이 왔을 때만 한다.

트랜잭션 경계는 이 모듈(또는 그 위의 FastAPI 요청 의존성)이 잡는다 --
`app/tools/*` 의 툴 함수는 `flush()` 까지만 하고 commit 하지 않는다(01-plan
결정 2). 그래야 테스트의 롤백 픽스처(tests/conftest.py `db_session`)가
서로 오염되지 않는다.

접속 문자열·비밀번호는 이 모듈 어디에서도 로그·예외 메시지에 찍지 않는다
(security.md §1) -- `app.config.sqlalchemy_url()` 이 반환하는 URL 문자열
자체를 print/raise 하지 않는다.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import sqlalchemy_url

_engine: Engine | None = None


def get_engine() -> Engine:
    """엔진을 최초 호출 시 1회 생성해 모듈 전역에 캐시한다.

    두 번째 이후 호출은 같은 객체를 반환한다(재호출해도 재접속·재생성하지
    않는다). import 시점에는 호출되지 않는다 -- `create_app()` 도 마찬가지로
    이 함수를 부르지 않는다(엔진 생성은 첫 요청/첫 사용까지 미룬다).
    """
    global _engine
    if _engine is None:
        # connect_timeout(초) -- 접속 불가한 포트(테스트의 db_engine skip 경로,
        # 예: 존재하지 않는 POSTGRES_PORT)에서 OS 기본 TCP 타임아웃(수십 초~)
        # 까지 기다리지 않고 빠르게 skip 사유를 내도록 psycopg 드라이버에
        # 넘긴다(scripts/schema_check.py 의 connect_timeout=5 와 같은 값).
        _engine = create_engine(
            sqlalchemy_url(), pool_pre_ping=True, connect_args={"connect_timeout": 5}
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """`get_engine()` 에 바인딩된 `sessionmaker` 를 반환한다.

    `SessionLocal` 모듈 전역은 이 팩토리가 만드는 것과 같은 설정을 쓴다.
    `expire_on_commit=False` -- 커밋 뒤에도 반환한 ORM 객체의 속성을 그대로
    읽을 수 있어야 툴이 만든 `PersonOut` 등을 조립할 수 있다. `autoflush=True`
    -- 조회 직전에 대기 중인 변경을 자동으로 흘려보내 같은 트랜잭션 안에서
    방금 만든 행을 바로 조회할 수 있다(U1 검증 항목).
    """
    return sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=True)


class _SessionLocalProxy:
    """`SessionLocal()` 호출 시점에 `get_engine()` 을 지연 평가하는 얇은 프록시.

    `SessionLocal = sessionmaker(bind=get_engine(), ...)` 을 모듈 로드 시점에
    바로 쓰면 import 만으로 엔진이 생성된다(리스크 A). 이 프록시는 실제
    `sessionmaker` 조립을 `__call__` 시점으로 미룬다.
    """

    def __call__(self, *args: object, **kwargs: object) -> Session:
        factory = get_session_factory()
        return factory(*args, **kwargs)  # type: ignore[arg-type]


SessionLocal = _SessionLocalProxy()


@contextmanager
def session_scope() -> Iterator[Session]:
    """세션 하나를 만들어 정상 종료 시 commit, 예외 시 rollback, 항상 close.

    호출자(스크립트·배치 작업)가 트랜잭션 경계를 잡을 때 쓴다. FastAPI 요청
    경로는 같은 규약을 `app/api/deps.py` 의 `get_session()` 의존성으로
    구현한다(이 함수를 재사용하지 않고 규약만 맞춘다 -- yield 의존성은
    컨텍스트 매니저와 형태가 다르다).
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
