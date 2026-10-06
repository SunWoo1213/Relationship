"""Refs: FIX-020 FIX-026 P1-schema P2-tools P6-memory P7-push S3.1 D6 원칙1 --
"한 인물·한 키(또는 한 사용자·한 엔드포인트)에 한 행" 규칙이 동시 저장에서도
지켜지는지 검증한다.

증상(FIX-020.md): `person_facts(person_id, key)`·`person_aliases
(person_id, alias)`·`push_subscriptions(user_id, endpoint)` 세 자리 모두
"애플리케이션이 조회 후 삽입"으로 유일성을 흉내낼 뿐, DB 에는 기본키
외 UNIQUE 제약이 없었다. 두 커넥션이 동시에 upsert 하면 둘 다 "없음"을
읽고 둘 다 INSERT 해 **중복 행**이 생긴다.

네 번째 절(FIX-026 R-20-1): `app.memory.patterns.detect_patterns` 의
`pattern:{type}` 사실 저장은 FIX-020 이후에도 "조회 후 삽입"이 남아
있었다. `person_facts` 에는 이미 UNIQUE 제약이 있으므로 중복 행 대신
**충돌한 평범한 INSERT 가 `IntegrityError`** 로 실패한다 -- 두 커넥션
모두 "없음"을 읽고(READ COMMITTED) 둘 다 `INSERT`(ON CONFLICT 없음)를
내면, 하나는 유일 인덱스가 다른 트랜잭션의 미커밋 행과 충돌하는 동안
**블로킹**되었다가(평범한 INSERT 도 유일 인덱스 충돌 후보에 대해서는
PostgreSQL 이 먼저 커밋을 기다린다), 상대가 커밋하는 순간 진짜 충돌로
드러나 `IntegrityError` 를 던진다. ON CONFLICT DO UPDATE 로 바꾸면 그
블로킹 이후 충돌을 그대로 흡수해 갱신으로 합류한다.

세 테스트(1~3)는 같은 틀(`tests/test_answer_concurrency.py` 패턴)을 쓴다:
커넥션 둘(`db_engine` 직접 커밋, `db_session` 롤백 픽스처로는 커밋되지
않은 행이 다른 커넥션에 보이지 않아 경쟁을 재현할 수 없다)로 A 가 upsert
함수를 호출해 행을 아직 커밋하지 않고 있는 동안, B 를 별도 스레드에서
같은 키로 호출한다.

- **수정 전**(UNIQUE 제약 없음): B 의 SELECT 는 A 의 미커밋 행을 보지
  못해(READ COMMITTED) "없음"으로 판단하고 **그대로 INSERT 에 성공**한다
  -- B 가 A 의 커밋을 기다리지 않고 곧바로 끝나 버리므로
  `assert thread_b.is_alive()` 가 실패로 결함을 드러낸다(중복 행 재현).
- **수정 후**(UNIQUE 제약 + `INSERT ... ON CONFLICT`): B 의 INSERT 문이
  A 가 잡고 있는(아직 커밋 전인) 유일 인덱스 항목과 충돌 여부를 확인하려고
  A 의 트랜잭션이 끝날 때까지 **블로킹**된다 -- PostgreSQL 자체의 표준
  동작이라 애플리케이션이 별도로 잠가야 하는 것은 아니다. A 가 커밋하면
  B 는 충돌을 확인하고 `DO UPDATE`/`DO NOTHING` 경로로 합류해 최종 행은
  1개가 된다.

끝에서 이 테스트가 만든 행만 지운다(테이블 전체 삭제·TRUNCATE 금지).
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import AgentTrace, Event, FactSource, Person, PersonAlias, PersonFact, PushSubscription
from app.memory.patterns import detect_patterns
from app.memory.promote import _upsert_fact
from app.memory.types import ExtractedFact
from app.push.subscriptions import save_subscription
from app.tools.context import ToolContext
from app.tools.persons import ALIAS_SOURCES, _add_alias

dbtest = pytest.mark.dbtest
pytestmark = dbtest

#: 스레드 대기 상한(초) -- 교착·무한 대기를 막는다(tests/test_answer_concurrency.py
#: 와 같은 상수값·같은 이유: A 는 항상 이 테스트 코드 자신이 명시적으로
#: 풀어 주므로 이 값을 넘기면 설계가 잘못된 것이지 느린 환경 탓이 아니다).
_WAIT_TIMEOUT = 5.0


def _make_person(engine, *, user_id: str) -> int:
    session = Session(bind=engine)
    try:
        person = Person(
            user_id=user_id, display_name="중복upsert테스트", relation_tag="친구", hierarchy="동"
        )
        session.add(person)
        session.commit()
        return person.id
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 1) person_facts(person_id, key)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_upsert_person_fact_concurrent_connections_result_in_one_row(db_engine) -> None:
    user_id = f"fix020-fact-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    try:
        session_a.begin()
        result_a = _upsert_fact(
            session_a, person_id, ExtractedFact(key="hobby", value="등산", source_event_ids=[])
        )
        assert result_a.action == "created"
        # A 는 아직 커밋하지 않는다 -- (person_id, key) 가 유일 인덱스에
        # 올라갔지만 커밋 전이라 B 가 그 결과를 기다려야 한다(수정 후 기대).

        session_b.begin()
        result_holder: dict[str, object] = {}

        def _call_b() -> None:
            result_holder["result"] = _upsert_fact(
                session_b,
                person_id,
                ExtractedFact(key="hobby", value="등산 (갱신)", source_event_ids=[]),
            )

        thread_b = threading.Thread(target=_call_b)
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 커밋을 기다리지 않고 곧바로 끝났다 -- "
            "person_facts 에 UNIQUE(person_id, key) 제약/ON CONFLICT 가 아직 없다(FIX-020 결함)"
        )

        session_a.commit()

        thread_b.join(timeout=_WAIT_TIMEOUT)
        assert not thread_b.is_alive(), "B 가 A 커밋 후에도 끝나지 않았다"
        session_b.commit()

        assert "result" in result_holder
        result_b = result_holder["result"]
        assert result_b.action == "updated"
        assert result_b.fact_id == result_a.fact_id
        # `previous_value` 는 upsert 문 이전에 읽은 추정치다(app/memory/
        # promote.py 모듈 docstring "동시성(FIX-020)" 절) -- B 의 사전
        # 읽기는 A 가 아직 커밋하지 않은 시점에 실행되므로 `None` 으로
        # 보인다(실제 "직전 값"인 "등산"과 다르다). 저장되는 값·행 개수는
        # 항상 정확하므로(아래 count==1 단언) 이 어긋남은 trace 표시
        # 한정이지 데이터 정합성 문제가 아니다.
        assert result_b.previous_value is None

        check_session = Session(bind=db_engine)
        try:
            rows = (
                check_session.execute(
                    select(PersonFact)
                    .where(PersonFact.person_id == person_id)
                    .where(PersonFact.key == "hobby")
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, f"중복 행 생성됨: {len(rows)}건"
            assert rows[0].value == "등산 (갱신)"
        finally:
            check_session.close()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()

        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 2) person_aliases(person_id, alias)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_add_alias_concurrent_connections_result_in_one_row(db_engine, fake_embedder) -> None:
    user_id = f"fix020-alias-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)
    person_like = SimpleNamespace(id=person_id)

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    try:
        session_a.begin()
        row_a = _add_alias(
            session_a,
            person_like,
            "김팀장",
            source=ALIAS_SOURCES[0],
            embedder=fake_embedder,
        )
        assert row_a.source == ALIAS_SOURCES[0]
        # A 는 아직 커밋하지 않는다.

        session_b.begin()
        result_holder: dict[str, object] = {}
        confirmed_at_b = datetime(2026, 10, 6, 9, 0, 0, tzinfo=timezone.utc)

        def _call_b() -> None:
            result_holder["row"] = _add_alias(
                session_b,
                person_like,
                "김팀장",
                source=ALIAS_SOURCES[1],
                embedder=fake_embedder,
                confirmed_at=confirmed_at_b,
            )

        thread_b = threading.Thread(target=_call_b)
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 커밋을 기다리지 않고 곧바로 끝났다 -- "
            "person_aliases 에 UNIQUE(person_id, alias) 제약/ON CONFLICT 가 아직 없다(FIX-020 결함)"
        )

        session_a.commit()

        thread_b.join(timeout=_WAIT_TIMEOUT)
        assert not thread_b.is_alive(), "B 가 A 커밋 후에도 끝나지 않았다"
        session_b.commit()

        assert "row" in result_holder

        check_session = Session(bind=db_engine)
        try:
            rows = (
                check_session.execute(
                    select(PersonAlias)
                    .where(PersonAlias.person_id == person_id)
                    .where(PersonAlias.alias == "김팀장")
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, f"중복 행 생성됨: {len(rows)}건"
            # B 가 더 상위(confirmed) source 로 왔으므로 격상되어야 한다
            # (모듈 docstring "별칭 격상 규칙").
            assert rows[0].source == ALIAS_SOURCES[1]
            assert rows[0].confirmed_at == confirmed_at_b
        finally:
            check_session.close()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()

        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(PersonAlias).where(PersonAlias.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 3) push_subscriptions(user_id, endpoint)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_save_subscription_concurrent_connections_result_in_one_row(db_engine) -> None:
    user_id = f"fix020-push-{uuid.uuid4().hex}"
    endpoint = "https://example.invalid/push/fix-020"

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    try:
        session_a.begin()
        result_a = save_subscription(session_a, user_id, endpoint, {"p256dh": "AAA", "auth": "BBB"})
        assert result_a.created is True
        # A 는 아직 커밋하지 않는다.

        session_b.begin()
        result_holder: dict[str, object] = {}

        def _call_b() -> None:
            result_holder["result"] = save_subscription(
                session_b, user_id, endpoint, {"p256dh": "CCC", "auth": "DDD"}
            )

        thread_b = threading.Thread(target=_call_b)
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 커밋을 기다리지 않고 곧바로 끝났다 -- "
            "push_subscriptions 에 UNIQUE(user_id, endpoint) 제약/ON CONFLICT 가 아직 없다(FIX-020 결함)"
        )

        session_a.commit()

        thread_b.join(timeout=_WAIT_TIMEOUT)
        assert not thread_b.is_alive(), "B 가 A 커밋 후에도 끝나지 않았다"
        session_b.commit()

        assert "result" in result_holder
        result_b = result_holder["result"]
        assert result_b.created is False
        assert result_b.id == result_a.id

        check_session = Session(bind=db_engine)
        try:
            rows = (
                check_session.execute(
                    select(PushSubscription)
                    .where(PushSubscription.user_id == user_id)
                    .where(PushSubscription.endpoint == endpoint)
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, f"중복 행 생성됨: {len(rows)}건"
            assert rows[0].keys == {"p256dh": "CCC", "auth": "DDD"}
        finally:
            check_session.close()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()

        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(
                delete(PushSubscription).where(PushSubscription.user_id == user_id)
            )
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 4) person_facts(person_id, key) via app.memory.patterns.detect_patterns
#    (FIX-026 R-20-1)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_detect_patterns_concurrent_connections_result_in_one_row(db_engine) -> None:
    user_id = f"fix026-pattern-{uuid.uuid4().hex}"
    person_id = _make_person(db_engine, user_id=user_id)
    now = datetime(2026, 10, 6, 9, 0, 0, tzinfo=timezone.utc)

    # 패턴 기준(기본 PATTERN_MIN_COUNT=3)을 채우는 이벤트를 미리 커밋해
    # 둔다 -- 두 커넥션 모두 이 이벤트들을 그대로 본다. 경쟁은
    # `person_facts(person_id, "pattern:conflict")` 행 생성 자리에서
    # 일어난다.
    setup = Session(bind=db_engine)
    try:
        for days_ago in (10, 5, 1):
            setup.add(
                Event(
                    person_id=person_id,
                    type="conflict",
                    content="내용",
                    raw_utterance="raw",
                    occurred_at=now - timedelta(days=days_ago),
                )
            )
        setup.commit()
    finally:
        setup.close()

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    session_id_a = f"fix026-pattern-a-{uuid.uuid4().hex}"
    session_id_b = f"fix026-pattern-b-{uuid.uuid4().hex}"
    try:
        session_a.begin()
        ctx_a = ToolContext(session=session_a, session_id=session_id_a, user_id=user_id, now=lambda: now)
        result_a = detect_patterns(ctx_a, person_id)
        assert any(change.type == "conflict" and change.action == "created" for change in result_a.changes)
        # A 는 아직 커밋하지 않는다.

        session_b.begin()
        result_holder: dict[str, object] = {}

        def _call_b() -> None:
            ctx_b = ToolContext(
                session=session_b, session_id=session_id_b, user_id=user_id, now=lambda: now
            )
            try:
                result_holder["result"] = detect_patterns(ctx_b, person_id)
            except Exception as exc:  # noqa: BLE001 -- 수정 전에는 IntegrityError 가 나야 정상 재현
                result_holder["error"] = exc

        thread_b = threading.Thread(target=_call_b)
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 커밋을 기다리지 않고 곧바로 끝났다 -- "
            "두 평범한 INSERT 가 유일 인덱스에서 블로킹하지 않았다(예상 밖의 환경)"
        )

        session_a.commit()

        thread_b.join(timeout=_WAIT_TIMEOUT)
        assert not thread_b.is_alive(), "B 가 A 커밋 후에도 끝나지 않았다"

        if "error" in result_holder:
            session_b.rollback()
            pytest.fail(
                "B 가 IntegrityError 로 실패했다 -- patterns.py 의 person_facts 저장이 "
                f"아직 ON CONFLICT 로 바뀌지 않았다(FIX-026 R-20-1): {result_holder['error']!r}"
            )

        session_b.commit()
        assert "result" in result_holder

        check_session = Session(bind=db_engine)
        try:
            rows = (
                check_session.execute(
                    select(PersonFact)
                    .where(PersonFact.person_id == person_id)
                    .where(PersonFact.key == "pattern:conflict")
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, f"중복 행 생성됨: {len(rows)}건"
            assert rows[0].value.startswith("3회")
        finally:
            check_session.close()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()

        cleanup = Session(bind=db_engine)
        try:
            fact_ids = (
                cleanup.execute(select(PersonFact.id).where(PersonFact.person_id == person_id))
                .scalars()
                .all()
            )
            if fact_ids:
                cleanup.execute(delete(FactSource).where(FactSource.fact_id.in_(fact_ids)))
            cleanup.execute(delete(PersonFact).where(PersonFact.person_id == person_id))
            cleanup.execute(delete(Event).where(Event.person_id == person_id))
            cleanup.execute(
                delete(AgentTrace).where(AgentTrace.session_id.in_([session_id_a, session_id_b]))
            )
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.commit()
        finally:
            cleanup.close()
