"""Refs: P5-loop U6 R3 R4 R7 D2 S3.4 원칙9 -- `POST /chat` HTTP 테스트.

`TestClient(create_app())` + `app.dependency_overrides[get_session]`
(U1 롤백 픽스처 `db_session` 주입, P2 결정 13 과 같은 방식)로 DB 에 행을
남기지 않는다. 인식 단계는 `app.dependency_overrides[get_proposer]` 로
`FakeProposer`(U2, 네트워크 0)를, 판정 단계는 `get_judge` 로 `FakeJudge`
(P3-er, 네트워크 0)를 주입한다 -- 실 LLM·실 임베딩 호출이 0 이다(원칙8,
01-plan 판정 표 2행과 같은 방향).

`test_chat_partial_rollback_when_second_mention_resolve_fails` 는
`app.agent.loop.resolve`(ER 진입점의 loop.py 안 이름)를 `monkeypatch` 로
감싸 **두 번째 호출에서만** 예외를 던진다 -- 이 파일(테스트)만 손대는
것이므로 01-plan 75행 "허용 파일"(`app/agent` 무수정)과 무관하다. 실제
운영 경로에서 두 번째 언급이 실패하는 원인(예: `apply_resolution` 내부의
`ToolError`)을 흉내 낼 뿐, `app/agent/loop.py` 자체는 바뀌지 않는다.

`app_and_client` 픽스처가 `app.dependency_overrides[get_embedder]` 를
`fake_embedder`(결정적, 네트워크 0)로 **기본 오버라이드**한다(U6 추가
수정, 사용자 승인) -- `build_chat_ctx()` 가 더 이상 `_embedder_from_env()`
를 스스로 부르지 않고 `routes.chat` 이 `Depends(get_embedder)` 로 받은
값을 그대로 넘기므로, 이 오버라이드가 없으면 `OPENAI_API_KEY` 가 없는
개발 환경에서는 `embedder=None` 이 되어(임베딩 신호가 빠져 merge 문턱을
못 넘고 되묻기로 빠진다) 키가 있는 환경에서는 실제 OpenAI 를 호출한다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

import app.agent.loop as loop_module
from app.agent.propose import FakeProposer
from app.api.deps import get_embedder, get_judge, get_proposer, get_session
from app.db.models import ALIAS_SOURCES, AgentTrace, Event, PendingQuestion, Person, PersonAlias
from app.er.judge import FakeJudge
from app.er.types import JudgeUnavailable
from app.main import create_app
from app.tools.context import ToolContext
from app.tools.questions import ask_user

dbtest = pytest.mark.dbtest
pytestmark = dbtest

NOW = datetime(2026, 9, 25, 19, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 테스트 전용 제안자 -- 공급자 오류·DB 오류를 흉내낸다(원칙8, 네트워크 0)
# ---------------------------------------------------------------------------


class _FailingProposer:
    """인식 단계에서 항상 `JudgeUnavailable(code)` 를 던진다(공급자 오류
    시뮬레이션, `judge.py` 오류 어휘 6종 중 하나를 그대로 쓴다)."""

    def __init__(self, code: str = "timeout") -> None:
        self.code = code

    def propose(self, utterance: str, now: datetime):
        raise JudgeUnavailable(self.code)


class _DbErrorProposer:
    """인식 단계에서 `SQLAlchemyError` 를 던진다 -- R-3 가 "삼키지 않는다"
    고 못박은 예외 범위 밖의 예외를 흉내낸다."""

    def propose(self, utterance: str, now: datetime):
        raise SQLAlchemyError("simulated-db-failure-detail")


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session, fake_embedder):
    """U1 롤백 세션을 `get_session` 자리에 주입한 `(app, client)` 쌍
    (P2 결정 13). `app` 을 함께 돌려줘야 테스트마다 `get_proposer`/
    `get_judge` 오버라이드를 걸 수 있다(`tests/test_api.py::client` 는
    `app` 을 감추므로 이 모듈은 별도 픽스처를 둔다).

    `get_embedder` 도 `fake_embedder` 로 기본 오버라이드한다(U6 추가
    수정, 모듈 docstring 참고) -- 개별 테스트가 필요하면 다시 오버라이드
    할 수 있지만, 이 모듈의 모든 시나리오는 네트워크 0 이 기본이어야
    한다."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    return app, TestClient(app)


def _make_person(db_session, *, display_name: str, user_id: str = "local") -> Person:
    person = Person(user_id=user_id, display_name=display_name, relation_tag="직장", hierarchy="동")
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session, person: Person, alias: str, *, embedding) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=ALIAS_SOURCES[0], embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


# ---------------------------------------------------------------------------
# 한 흐름 -- 저장·응답 (판정 표 3행 방향)
# ---------------------------------------------------------------------------


def test_chat_stores_event_and_replies_in_one_request(app_and_client, db_session, fake_embedder):
    """요청 1건 안에서 이벤트가 저장되고, 원문(raw_utterance)이 그대로
    남고, 빈 응답 문장이 아니다(01-plan 수용기준 해석 "저장"·"응답")."""

    app, client = app_and_client
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    utterance = "어제 팀장이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        }
    ]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person.id: 0.95})

    resp = client.post(
        "/chat", json={"utterance": utterance}, headers={"X-Session-Id": "chat-one-flow"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == "chat-one-flow"
    assert body["stored"] == {"persons": 0, "events": 1, "schedules": 0}
    assert body["reply"]
    assert body["pending_question"] is None
    assert body["stop_reason"] is None

    event = db_session.execute(select(Event).where(Event.person_id == person.id)).scalar_one()
    assert event.raw_utterance == utterance
    assert event.type == "meal"


def test_chat_new_person_returns_pending_question_id(app_and_client, db_session):
    """되묻기로 끝나는 턴 -- 응답에 `question_id`·`options`·`kind` 가 함께
    온다(01-plan 수용기준 해석 "응답")."""

    app, client = app_and_client
    utterance = "오늘 이모랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "이모",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        }
    ]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})

    resp = client.post(
        "/chat", json={"utterance": utterance}, headers={"X-Session-Id": "chat-new-person"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["stop_reason"] == "ask_user"
    assert body["pending_question"] is not None
    assert body["pending_question"]["kind"] == "new_person"
    assert isinstance(body["pending_question"]["question_id"], int)
    assert body["pending_question"]["options"]

    row = db_session.get(PendingQuestion, body["pending_question"]["question_id"])
    assert row is not None
    assert row.answered_at is None


# ---------------------------------------------------------------------------
# 세션 id 발급·재사용 (결정 I)
# ---------------------------------------------------------------------------


def test_chat_issues_session_id_when_header_missing(app_and_client):
    app, client = app_and_client
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={})

    resp = client.post("/chat", json={"utterance": "안녕"})

    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    assert session_id
    uuid.UUID(session_id)  # 파싱되면 uuid4 형식이다 -- 실패하면 ValueError


def test_chat_reuses_given_session_id(app_and_client):
    app, client = app_and_client
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={})

    resp = client.post(
        "/chat", json={"utterance": "안녕"}, headers={"X-Session-Id": "custom-session-1"}
    )

    assert resp.status_code == 200
    assert resp.json()["session_id"] == "custom-session-1"


def test_chat_invalid_session_id_header_returns_422(app_and_client):
    app, client = app_and_client
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={})

    # ASCII 불량값(공백·`!`) -- 한글 헤더 값은 httpx 인코딩에서
    # UnicodeEncodeError 가 나 이 테스트의 목적(형식 검증 422)과 다른
    # 이유로 실패한다(U6 추가 수정, 사용자 승인).
    resp = client.post(
        "/chat", json={"utterance": "안녕"}, headers={"X-Session-Id": "bad id!"}
    )

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 공급자 오류 -- 결정 G (R-3)
# ---------------------------------------------------------------------------


def test_chat_provider_error_returns_200_with_no_storage_and_loop_error_trace(
    app_and_client, db_session
):
    app, client = app_and_client
    session_id = "chat-provider-error"
    app.dependency_overrides[get_proposer] = lambda: _FailingProposer("timeout")

    resp = client.post(
        "/chat", json={"utterance": "아무 발화"}, headers={"X-Session-Id": session_id}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"]
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert body["pending_question"] is None

    rows = (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.step == "loop_error")
        )
        .scalars()
        .all()
    )
    assert len(rows) == 1
    assert rows[0].output["error"] == "JudgeUnavailable"

    # 예외 코드·공급자명·프롬프트가 응답 본문에 노출되지 않는다(security §1).
    text = resp.text.lower()
    assert "anthropic" not in text
    assert "openai" not in text
    assert "gemini" not in text


# ---------------------------------------------------------------------------
# DB 예외는 삼키지 않는다 (R-3)
# ---------------------------------------------------------------------------


def test_chat_db_error_does_not_return_200(db_session, fake_embedder):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_proposer] = lambda: _DbErrorProposer()
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.post(
        "/chat", json={"utterance": "아무 발화"}, headers={"X-Session-Id": "chat-db-error"}
    )

    assert resp.status_code != 200
    assert "simulated-db-failure-detail" not in resp.text


# ---------------------------------------------------------------------------
# 미답변 질문 유지 (D2 파급, R-4)
# ---------------------------------------------------------------------------


def test_chat_pending_survives_when_new_utterance_arrives(app_and_client, db_session):
    """답 없이 새 발화가 오면 대기 질문은 유지되고 새 발화가 먼저 처리된다
    (S3.4 "답 없이 다음 발화가 오면 대기 질문 유지, 새 발화 우선")."""

    app, client = app_and_client
    session_id = "chat-pending-survives"
    ctx = ToolContext(session=db_session, session_id=session_id)
    asked = ask_user(
        ctx,
        kind="schedule",
        question="내일 약속, 언제로 기억할까요?",
        options=["내일 저녁 7시", "모르겠어요"],
        context={},
    )

    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={})

    resp = client.post(
        "/chat", json={"utterance": "그냥 안부 인사"}, headers={"X-Session-Id": session_id}
    )

    assert resp.status_code == 200

    row = db_session.get(PendingQuestion, asked.question_id)
    assert row is not None
    assert row.answered_at is None
    assert row.answer is None


# ---------------------------------------------------------------------------
# 부분 롤백 -- 예외를 삼키는 턴은 "저장 0" 이어야 한다(결정 G, 사용자 승인
# 2026-09-25, F-b3f6a1)
# ---------------------------------------------------------------------------


def test_chat_partial_rollback_when_second_mention_resolve_fails(
    app_and_client, db_session, fake_embedder, monkeypatch: pytest.MonkeyPatch
):
    """발화 한 건에 언급이 둘이면 해석 구간이 순서대로 처리한다(결정
    C(i)). 첫 언급이 `merge` 로 확정돼 별칭이 flush 된 **뒤** 둘째 언급의
    해석에서 예외가 나면, 첫 언급의 쓰기도 세이브포인트와 함께 롤백돼야
    한다(수정 전에는 `get_session()` 의 commit 과 함께 남아 결정 G "저장
    0"과 어긋났다 -- 재현: `app.agent.loop.resolve` 를 두 번째 호출에서만
    실패하도록 몽키패치).

    확인: (1) 200 이 돌아온다. (2) 첫 언급이 **실제로 merge 되고**(밴드
    캡처) 둘째 `resolve` 호출이 **실제로 일어났다**(호출 횟수 카운터) --
    이 단언이 없으면 임베더 부재로 첫 언급부터 `identity`/`new_person`
    으로 빠져 시나리오 자체가 성립하지 않는 채로 통과하는 "헛돎"을
    가려낼 수 없다(U6 추가 수정, 사용자 승인). (3) 첫 언급 인물의 별칭
    **수**가 요청 전후로 같다(전역 개수 단언이 아니라 그 인물 한정 전후
    비교, FIX-004 와 같은 방향). (4) `loop_error` 가 정확히 1행 남는다."""

    app, client = app_and_client
    session_id = "chat-partial-rollback"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    alias_count_before = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == person.id))
        .scalars()
        .all()
    )
    alias_count_before = len(alias_count_before)

    utterance = "김팀장이랑 박대리랑 밥 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        },
        {
            "name": "add_event",
            "args": {
                "person": "박대리",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        },
    ]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person.id: 0.95})

    real_resolve = loop_module.resolve
    state = {"calls": 0}
    bands_seen: list[str] = []

    def _flaky_resolve(ctx, mention, utterance_arg, hints, *, judge=None, config=None):
        state["calls"] += 1
        if state["calls"] == 2:
            # 둘째 언급("박대리")의 해석에서 실패를 흉내낸다 -- 첫 언급은
            # 이미 real_resolve 로 merge 되어 flush 된 뒤다.
            raise JudgeUnavailable("timeout")
        resolution = real_resolve(ctx, mention, utterance_arg, hints, judge=judge, config=config)
        bands_seen.append(resolution.band)
        return resolution

    monkeypatch.setattr(loop_module, "resolve", _flaky_resolve)

    resp = client.post(
        "/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert body["pending_question"] is None

    # 시나리오가 실제로 성립했는지(헛돌지 않았는지) 먼저 확인한다 --
    # 첫 언급은 real_resolve 로 merge 됐고, 둘째 resolve 호출이 실제로
    # 일어났다(그래서 몽키패치가 두 번째에 예외를 던질 기회를 가졌다).
    assert bands_seen == ["merge"]
    assert state["calls"] == 2

    alias_count_after = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == person.id))
        .scalars()
        .all()
    )
    assert len(alias_count_after) == alias_count_before

    event_count = (
        db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
    )
    assert event_count == []

    error_rows = (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.step == "loop_error")
        )
        .scalars()
        .all()
    )
    assert len(error_rows) == 1
