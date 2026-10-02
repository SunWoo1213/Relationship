"""Refs: P6-briefing S3.6 R12 원칙9 -- U6 `POST /briefings/run` HTTP 테스트.

`TestClient(create_app())` + `app.dependency_overrides[get_session]`
(U1 롤백 픽스처 `db_session` 주입, P2 결정 13 과 같은 방식)로 DB 에 행을
남기지 않는다. 생성기는 `get_briefing_composer` 로 `FakeBriefingComposer`
(`app.briefing.compose`, 결정적·네트워크 0)를 주입하고, "지금"은
`get_now` 로 고정 시계(`NOW`)를 주입한다(`app/api/deps.py` "U6 추가분"
절 -- 기존 `get_proposer`/`get_judge`/`get_embedder` 오버라이드 관례를
그대로 따른 것이다. 창 선정(`select_due_schedules`)이 `scheduled_at` 과
"지금"의 차이로 대상을 가르므로, `/chat`·`/answers/{id}` 와 달리 이
엔드포인트는 시계 고정이 꼭 필요하다).

각 테스트는 **독립**이다(01-plan 판정 방법 "상태" 열) -- 행마다 새
인물·일정을 만들고 앞 테스트의 결과를 이어 쓰지 않는다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import get_briefing_composer, get_now, get_session
from app.briefing.compose import FakeBriefingComposer
from app.briefing.types import BRIEFING_TRACE_TOOL_NAME, STEP_BRIEFING_COMPOSE, STEP_BRIEFING_RUN
from app.db.models import AgentTrace, Event, Person, PersonFact, Schedule
from app.main import create_app

dbtest = pytest.mark.dbtest
pytestmark = dbtest

#: 창 선정의 기준 "지금"(`get_now` 오버라이드가 돌려주는 고정 시계).
NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 픽스처 · 보조 함수 (tests/test_api_chat.py·test_briefing_run.py 와 같은 모양)
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session):
    """U1 롤백 세션을 `get_session` 자리에 주입한 `(app, client)` 쌍(P2
    결정 13). `get_now` 는 고정 시계(`NOW`)로, `get_briefing_composer`
    는 기본 `FakeBriefingComposer()`(빈 표 -- 어떤 `schedule_id` 든
    빈 브리핑)로 **기본 오버라이드**한다 -- 개별 테스트가 호출 횟수를
    세야 하면(판정 2행) 공유 인스턴스로 다시 오버라이드한다."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    app.dependency_overrides[get_briefing_composer] = lambda: FakeBriefingComposer()
    return app, TestClient(app)


def _make_person(
    db_session,
    *,
    user_id: str = "local",
    display_name: str = "민수",
    relation_tag: str = "친구",
    hierarchy: str = "동",
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _make_schedule(
    db_session,
    person: Person,
    *,
    scheduled_at: datetime,
    briefed_at: datetime | None = None,
    title: str = "저녁 약속",
) -> Schedule:
    schedule = Schedule(
        person_id=person.id, title=title, scheduled_at=scheduled_at, briefed_at=briefed_at
    )
    db_session.add(schedule)
    db_session.flush()
    return schedule


def _add_event(
    db_session,
    person: Person,
    *,
    event_type: str = "meal",
    occurred_at: datetime,
    content: str = "내용",
    raw_utterance: str | None = None,
) -> Event:
    event = Event(
        person_id=person.id,
        type=event_type,
        content=content,
        raw_utterance=raw_utterance or f"raw: {content} ({occurred_at.isoformat()})",
        occurred_at=occurred_at,
    )
    db_session.add(event)
    db_session.flush()
    return event


def _make_fact(
    db_session, person: Person, *, key: str, value: str, confidence: float = 0.9
) -> PersonFact:
    fact = PersonFact(person_id=person.id, key=key, value=value, confidence=confidence)
    db_session.add(fact)
    db_session.flush()
    return fact


def _trace_rows(db_session, step: str) -> list[AgentTrace]:
    """`run_briefings()` 가 실행마다 새 `session_id`("briefing:<uuid4>")를
    만들어(결정 I) 테스트가 미리 알 수 없으므로, `tool_name`·`step` 만
    걸러 조회한다(`tests/test_briefing_run.py::_trace_rows` 와 같은 관례).
    독립 테스트(픽스처마다 새 롤백 트랜잭션)이므로 다른 테스트의 행과
    섞이지 않는다."""

    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
            .where(AgentTrace.step == step)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


# ---------------------------------------------------------------------------
# 판정 1행 -- 양성 한 흐름(ㄱ·ㄴ·ㄷ)
# ---------------------------------------------------------------------------


def test_run_briefings_creates_briefing_and_marks_briefed(app_and_client, db_session) -> None:
    app, client = app_and_client
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _make_fact(db_session, person, key="dislikes", value="고수")
    _make_fact(db_session, person, key="hobby", value="등산")
    for i in range(3):
        _add_event(db_session, person, occurred_at=NOW - timedelta(days=i + 1), content=f"사건{i}")

    resp = client.post("/briefings/run")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["briefings"]) == 1
    assert body["briefings"][0]["schedule_id"] == schedule.id
    assert body["briefings"][0]["person_id"] == person.id
    assert body["skipped"] == []
    assert body["run_id"].startswith("briefing:")

    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW

    assert len(_trace_rows(db_session, STEP_BRIEFING_RUN)) == 1
    assert len(_trace_rows(db_session, STEP_BRIEFING_COMPOSE)) == 1


# ---------------------------------------------------------------------------
# 판정 2행 -- 재실행 멱등
# ---------------------------------------------------------------------------


def test_run_briefings_second_call_finds_nothing(app_and_client, db_session) -> None:
    app, client = app_and_client
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    _add_event(db_session, person, occurred_at=NOW - timedelta(days=1))

    composer = FakeBriefingComposer()
    app.dependency_overrides[get_briefing_composer] = lambda: composer

    resp1 = client.post("/briefings/run")
    resp2 = client.post("/briefings/run")

    assert resp1.status_code == 200
    assert len(resp1.json()["briefings"]) == 1

    assert resp2.status_code == 200
    assert resp2.json()["briefings"] == []
    assert resp2.json()["skipped"] == []

    assert composer.call_count == 1

    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW


# ---------------------------------------------------------------------------
# 판정 8행 -- 다른 사용자 격리
# ---------------------------------------------------------------------------


def test_run_briefings_other_user_schedule_id_returns_404(app_and_client, db_session) -> None:
    app, client = app_and_client
    other_person = _make_person(db_session, user_id="other-user")
    other_schedule = _make_schedule(db_session, other_person, scheduled_at=NOW + timedelta(hours=3))

    resp = client.post("/briefings/run", json={"schedule_id": other_schedule.id})

    assert resp.status_code == 404
    assert resp.json() == {"detail": {"code": "not_found"}}

    db_session.refresh(other_schedule)
    assert other_schedule.briefed_at is None


def test_run_briefings_missing_schedule_id_returns_404(app_and_client, db_session) -> None:
    """존재하지 않는 `schedule_id`(다른 사용자가 아니라 아예 없는 행)도
    같은 404 `not_found` 로 매핑된다(`ScheduleNotFound` 공통 핸들러)."""
    app, client = app_and_client

    resp = client.post("/briefings/run", json={"schedule_id": 999_999_999})

    assert resp.status_code == 404
    assert resp.json() == {"detail": {"code": "not_found"}}


# ---------------------------------------------------------------------------
# 판정 10행 -- 수동 강제(이미 브리핑된 일정을 schedule_id 로 다시)
# ---------------------------------------------------------------------------


def test_run_briefings_schedule_id_forces_regeneration(app_and_client, db_session) -> None:
    app, client = app_and_client
    person = _make_person(db_session)
    schedule = _make_schedule(
        db_session,
        person,
        scheduled_at=NOW + timedelta(hours=3),
        briefed_at=NOW - timedelta(hours=1),
    )
    _add_event(db_session, person, occurred_at=NOW - timedelta(days=1))

    resp = client.post("/briefings/run", json={"schedule_id": schedule.id})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["briefings"]) == 1
    assert body["briefings"][0]["schedule_id"] == schedule.id

    db_session.refresh(schedule)
    assert schedule.briefed_at == NOW


# ---------------------------------------------------------------------------
# 추가 -- 원문(raw_utterance) 미포함
# ---------------------------------------------------------------------------


def test_run_briefings_response_never_contains_raw_utterance(app_and_client, db_session) -> None:
    app, client = app_and_client
    person = _make_person(db_session)
    _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=3))
    secret_raw = "민수가 어제 말한 비밀 원문 토큰 QzR9x7"
    _add_event(
        db_session,
        person,
        occurred_at=NOW - timedelta(days=1),
        content="비밀 내용",
        raw_utterance=secret_raw,
    )

    resp = client.post("/briefings/run")

    assert resp.status_code == 200
    assert secret_raw not in resp.text


# ---------------------------------------------------------------------------
# 추가 -- 본문 없는 요청 허용 (위 판정 1행 테스트가 이미 `client.post("/briefings/run")`
# 로 본문 없이 호출하지만, 이 테스트는 그 사실 자체를 명시적으로 확인한다)
# ---------------------------------------------------------------------------


def test_run_briefings_allows_request_without_body(app_and_client, db_session) -> None:
    app, client = app_and_client
    person = _make_person(db_session)
    _make_schedule(db_session, person, scheduled_at=NOW + timedelta(hours=30))  # 창 밖 -- 대상 0건

    resp = client.post("/briefings/run")

    assert resp.status_code == 200
    body = resp.json()
    assert body["briefings"] == []
    assert body["skipped"] == []
