"""Refs: P2-tools U8 R7 D2 S3.4 결정 12·13 -- FastAPI 골격 HTTP 테스트.

`TestClient(create_app())` + `app.dependency_overrides[get_session]` 로
U1 의 롤백 픽스처(`db_session`)를 그대로 주입한다(결정 13) -- 테스트가 DB
에 행을 남기지 않고, `answer_question` 이 쓴 행을 **같은 트랜잭션에서**
직접 조회해 저장 여부를 증거로 만든다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
`create_app()` 이 엔진을 만들지 않는다는 것(리스크 A)만은 DB 없이 도는
별도 테스트로 검증한다(`test_create_app_does_not_create_engine`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

import app.db.session as db_session_module
from app.api.deps import get_session
from app.db.models import AgentTrace, PendingQuestion
from app.main import create_app
from app.tools.context import ToolContext
from app.tools.questions import ask_user

#: 모듈 전체가 아니라 `db_session`/`client` 픽스처를 실제로 쓰는 테스트에만
#: 붙인다(conftest.py 지시 -- 마커만 붙고 픽스처를 안 쓰면 "DB 없이도
#: 돈다"는 오해를 만든다). `test_create_app_does_not_create_engine` 는 DB
#: 불필요이므로 붙이지 않는다.
dbtest = pytest.mark.dbtest

_BASE_TIME = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_question_row(
    db_session,
    *,
    session_id: str = "api-test-session",
    kind: str = "schedule",
    question: str = "일정 확인할까요?",
    options: list[str] | None = None,
    context: dict | None = None,
    answer: str | None = None,
    answered_at: datetime | None = None,
    created_at: datetime = _BASE_TIME,
) -> PendingQuestion:
    if options is None:
        options = ["예", "아니오"]
    if context is None:
        context = {}
    row = PendingQuestion(
        session_id=session_id,
        kind=kind,
        question=question,
        options=options,
        context=context,
        answer=answer,
        answered_at=answered_at,
        created_at=created_at,
    )
    db_session.add(row)
    db_session.flush()
    return row


@pytest.fixture()
def client(db_session) -> TestClient:
    """U1 롤백 세션(`db_session`)을 `get_session` 자리에 주입한 `TestClient`
    (결정 13). 오버라이드된 `get_session` 은 commit 하지 않는다(롤백해야
    하므로) -- 툴이 `flush()` 까지 하므로 조회에는 문제가 없다."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


@dbtest
def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["db"] == "up"
    assert body["alembic_revision"] == "0001"

    text = resp.text
    assert "postgresql://" not in text
    assert "password" not in text.lower()


def test_health_degraded_on_db_down() -> None:
    """`get_session` 을 예외 던지는 의존성으로 오버라이드해 DB 다운을
    시뮬레이션한다 -- 503 degraded, 예외 원문(메시지)이 본문에 없어야 한다.

    Starlette 의 `ServerErrorMiddleware` 는 `Exception` 핸들러가 만든 응답을
    보낸 뒤에도 예외를 다시 올린다("서버가 로그를 남기게 하기 위해", 실제
    운영에서는 무해 -- 클라이언트는 이미 전송된 503 응답을 받는다). 기본
    `TestClient` 는 이 재발생을 그대로 드러내므로(`raise_server_exceptions=
    True`), 이 테스트만 `raise_server_exceptions=False` 로 응답을 관찰한다
    (DB 없이 도는 `client` 픽스처가 아니라 별도 인스턴스를 쓴다 -- 다른
    테스트의 진짜 버그를 가리지 않기 위해서다)."""

    def _raise_get_session():
        raise RuntimeError("simulated-connection-failure-detail")

    app = create_app()
    app.dependency_overrides[get_session] = _raise_get_session
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.get("/health")

    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["db"] == "down"
    assert body["alembic_revision"] is None
    assert "simulated-connection-failure-detail" not in resp.text


# ---------------------------------------------------------------------------
# POST /answers/{question_id}
# ---------------------------------------------------------------------------


@dbtest
def test_answer_success_saves_row_same_transaction(client: TestClient, db_session) -> None:
    ctx = ToolContext(session=db_session, session_id="api-answer-success")
    asked = ask_user(
        ctx,
        kind="schedule",
        question="내일 만남 확인할까요?",
        options=["예", "아니오"],
        context={},
    )

    resp = client.post(f"/answers/{asked.question_id}", json={"answer": "예"})

    assert resp.status_code == 200
    body = resp.json()
    assert body == {"question_id": asked.question_id, "status": "answered"}

    # 같은 트랜잭션에서 직접 조회 -- 결정 13.
    row = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == asked.question_id)
    ).scalar_one()
    assert row.answer == "예"
    assert row.answered_at is not None

    trace_rows = list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == "answer_question")
            .where(AgentTrace.session_id == row.session_id)
        ).scalars()
    )
    assert len(trace_rows) == 1
    assert trace_rows[0].session_id == "api-answer-success" == row.session_id


@dbtest
def test_answer_nonexistent_id_returns_404(client: TestClient) -> None:
    resp = client.post("/answers/999999999", json={"answer": "예"})

    assert resp.status_code == 404
    assert resp.json() == {"detail": {"code": "not_found"}}


@dbtest
def test_answer_already_answered_returns_409(client: TestClient, db_session) -> None:
    row = _make_question_row(
        db_session,
        created_at=_BASE_TIME,
        answer="예",
        answered_at=_BASE_TIME + timedelta(minutes=5),
    )

    resp = client.post(f"/answers/{row.id}", json={"answer": "아니오"})

    assert resp.status_code == 409
    body = resp.json()
    assert body["detail"]["code"] == "already_answered"
    assert body["detail"]["question_id"] == row.id


@dbtest
def test_answer_expired_returns_409_and_answered_at_stays_null(
    client: TestClient, db_session
) -> None:
    row = _make_question_row(
        db_session,
        created_at=_BASE_TIME,
    )
    # 25시간 전으로 갱신해 만료시킨다.
    row.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db_session.flush()

    resp = client.post(f"/answers/{row.id}", json={"answer": "예"})

    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "expired"

    db_session.expire_all()
    refreshed = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == row.id)
    ).scalar_one()
    assert refreshed.answered_at is None


@dbtest
def test_answer_option_outside_stored_options_returns_422(
    client: TestClient, db_session
) -> None:
    row = _make_question_row(db_session, created_at=datetime.now(timezone.utc))

    resp = client.post(f"/answers/{row.id}", json={"answer": "전혀 다른 답"})

    assert resp.status_code == 422
    assert resp.json() == {"detail": {"code": "invalid_value"}}


@dbtest
def test_answer_missing_body_field_returns_422_fastapi_default(
    client: TestClient, db_session
) -> None:
    row = _make_question_row(db_session, created_at=datetime.now(timezone.utc))

    resp = client.post(f"/answers/{row.id}", json={})

    assert resp.status_code == 422


@dbtest
def test_answer_malformed_body_returns_422_fastapi_default(
    client: TestClient, db_session
) -> None:
    row = _make_question_row(db_session, created_at=datetime.now(timezone.utc))

    resp = client.post(f"/answers/{row.id}", json={"answer": 12345})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 리스크 A -- create_app() 은 엔진을 만들지 않는다. DB 불필요.
# ---------------------------------------------------------------------------


def test_create_app_does_not_create_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    real_get_engine = db_session_module.get_engine

    def _counting_get_engine():
        calls.append(1)
        return real_get_engine()

    monkeypatch.setattr(db_session_module, "get_engine", _counting_get_engine)

    create_app()

    assert calls == []
