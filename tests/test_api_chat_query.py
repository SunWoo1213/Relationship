"""Refs: P5b-query-turn CR-004 D16 S3.4 원칙8 원칙9 R19 -- U6 조회 발화 `POST /chat`·
`POST /answers/{id}` 끝에서 끝 HTTP 테스트.

`tests/test_api_chat.py` 와 같은 방식(`create_app()` + `get_session`/`get_embedder`
오버라이드, 롤백 세션)을 **이 파일에 따로** 둔다(기존 파일 import 없음). 인식 단계는
`get_proposer` -> `FakeProposer(intents=...)`, 판정은 `get_judge` -> `FakeJudge`,
답 생성기는 결정 K 방식 -- 라우트는 `answerer` 를 넘기지 않으므로 지연 해소 지점
`app.agent.respond.answerer_from_env` 를 `monkeypatch` 로 바꿔 끼운다(라우트 무수정을
이 테스트가 증명한다). 실 LLM·실 임베딩 호출 0(원칙8).

실 PostgreSQL(로컬 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.agent.propose import FakeProposer
from app.agent.respond import QUERY_MORE_HINT, FakeQueryAnswerer, no_record_reply
from app.api.deps import get_embedder, get_judge, get_proposer, get_session
from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    Event,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)
from app.er.judge import FakeJudge
from app.main import create_app
from app.tools.types import PersonNotFound

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 9, 25, 19, 0, 0, tzinfo=timezone.utc)
ANSWER_TEXT = "민수 팀장님과 최근에 식사를 했어요."
WRITE_TOOLS = ("add_event", "add_schedule", "update_person", "create_person")


# ---------------------------------------------------------------------------
# 픽스처·헬퍼 (tests/test_api_chat.py 와 같은 모양, 복사본)
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session, fake_embedder):
    """롤백 세션을 `get_session` 자리에, `fake_embedder` 를 `get_embedder` 자리에
    주입한 `(app, client)` 쌍."""
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


def _seed_person(db_session, fake_embedder, *, name="김민수", alias="팀장", events=8, facts=3, schedules=2):
    """별칭 1개 + 이벤트·사실·일정을 가진 인물(근거 건수가 시드와 일치하는지 단언용)."""
    person = _make_person(db_session, display_name=name)
    _add_alias(db_session, person, alias, embedding=fake_embedder([alias])[0])
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(events):
        db_session.add(
            Event(
                person_id=person.id,
                type="meal",
                content=f"식사{i}",
                raw_utterance="원문",
                occurred_at=base + timedelta(days=i),
            )
        )
    for i in range(facts):
        db_session.add(PersonFact(person_id=person.id, key=f"k{i}", value=f"v{i}", confidence=0.9))
    future = datetime.now(timezone.utc) + timedelta(days=3)
    for i in range(schedules):
        db_session.add(
            Schedule(person_id=person.id, title=f"일정{i}", scheduled_at=future + timedelta(days=i))
        )
    db_session.flush()
    return person


def _counts(db_session, user_id: str = "local") -> dict[str, int]:
    """저장 0 단언용 -- 7개 테이블 행 수(`tests/test_agent_query_loop.py::_counts` 와 같은 SQL).
    `pending_questions` 는 사용자 열이 없어 전체 행 수다(롤백 픽스처라 전후 비교에 충분)."""

    def one(sql: str) -> int:
        return db_session.execute(text(sql), {"u": user_id}).scalar_one()

    return {
        "persons": one("SELECT count(*) FROM persons WHERE user_id = :u"),
        "person_aliases": one(
            "SELECT count(*) FROM person_aliases a JOIN persons p ON p.id = a.person_id "
            "WHERE p.user_id = :u"
        ),
        "events": one(
            "SELECT count(*) FROM events e JOIN persons p ON p.id = e.person_id WHERE p.user_id = :u"
        ),
        "schedules": one(
            "SELECT count(*) FROM schedules s JOIN persons p ON p.id = s.person_id WHERE p.user_id = :u"
        ),
        "person_facts": one(
            "SELECT count(*) FROM person_facts f JOIN persons p ON p.id = f.person_id "
            "WHERE p.user_id = :u"
        ),
        "fact_sources": one(
            "SELECT count(*) FROM fact_sources fs JOIN person_facts f ON f.id = fs.fact_id "
            "JOIN persons p ON p.id = f.person_id WHERE p.user_id = :u"
        ),
        "pending_questions": one("SELECT count(*) FROM pending_questions"),
    }


def _rows(db_session, session_id: str, step: str) -> list[AgentTrace]:
    return (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id, AgentTrace.step == step)
            .order_by(AgentTrace.id)
        )
        .scalars()
        .all()
    )


def _write_tool_rows(db_session, session_id: str) -> int:
    return db_session.execute(
        text(
            "SELECT count(*) FROM agent_traces WHERE session_id = :s AND step = 'tool_call' "
            "AND tool_name IN ('add_event','add_schedule','update_person','create_person')"
        ),
        {"s": session_id},
    ).scalar_one()


def _setup_query(app, monkeypatch, utterance, calls, *, judge, answer_text=ANSWER_TEXT):
    """조회 의도 제안 + 판정기 + 답 생성기(결정 K -- `answerer_from_env` 바꿔 끼움)를 건다."""
    answerer = FakeQueryAnswerer(table={utterance: answer_text})
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(
        table={utterance: calls}, intents={utterance: "query"}
    )
    app.dependency_overrides[get_judge] = lambda: judge
    monkeypatch.setattr("app.agent.respond.answerer_from_env", lambda env=None: answerer)
    return answerer


def _search(mention: str) -> list[dict]:
    return [{"name": "search_person", "args": {"query": mention}}]


def _post_chat(client, utterance: str, session_id: str | None):
    headers = {"X-Session-Id": session_id} if session_id else {}
    return client.post("/chat", json={"utterance": utterance}, headers=headers)


# ---------------------------------------------------------------------------
# (1) merge 조회 -- 저장 0, 행 수 불변, trace 5종
# ---------------------------------------------------------------------------


def test_chat_query_merge_stored_zero_no_writes_and_trace(app_and_client, db_session, fake_embedder, monkeypatch):
    app, client = app_and_client
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이었지?"
    answerer = _setup_query(app, monkeypatch, utt, _search("팀장"), judge=FakeJudge(table={person.id: 0.95}))
    before = _counts(db_session)

    resp = _post_chat(client, utt, "api-q-merge")

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert body["pending_question"] is None
    assert body["stop_reason"] is None
    # LLM 답 + 끝의 안내 문장(결정 F ①) -- monkeypatch 한 답 생성기가 실제로 쓰였다.
    assert body["reply"] == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert answerer.call_count == 1
    # 요청 전후 행 수 불변(7개 테이블 -- person_aliases·pending_questions 포함).
    assert _counts(db_session) == before
    assert _write_tool_rows(db_session, "api-q-merge") == 0

    # trace -- 각 step 정확히 1행.
    for step in ("loop_extract", "loop_gate", "er_resolve", "loop_query", "loop_turn"):
        assert len(_rows(db_session, "api-q-merge", step)) == 1, step
    assert _rows(db_session, "api-q-merge", "loop_extract")[0].output["intent"] == "query"
    assert _rows(db_session, "api-q-merge", "loop_record") == []
    q = _rows(db_session, "api-q-merge", "loop_query")[0].output
    assert q["intent"] == "query"
    assert q["person_id"] == person.id
    assert q["answer_source"] == "llm"
    assert q["evidence_counts"] == {"facts": 3, "patterns": 0, "timeline": 5, "schedules": 2}
    assert q["reply"] == body["reply"]
    assert _rows(db_session, "api-q-merge", "loop_turn")[0].output["reply"] == body["reply"]
    # er_resolve -- merge 라도 적용(별칭 누적)하지 않는다(결정 I (a)).
    er = _rows(db_session, "api-q-merge", "er_resolve")[0].output
    assert er["decision"]["applied"] is False
    assert q["resolutions"][0]["band"] == "merge"
    assert q["resolutions"][0]["applied"] is False
    assert q["resolutions"][0]["er_trace_id"] == _rows(db_session, "api-q-merge", "er_resolve")[0].id


# ---------------------------------------------------------------------------
# (2) identity 조회 -> 후보 답 -> 재개 -> 두 번째 답 409
# ---------------------------------------------------------------------------


def _ask_identity_over_http(app, client, db_session, fake_embedder, monkeypatch, utt, session_id):
    a = _seed_person(db_session, fake_embedder, name="김민수")
    b = _seed_person(db_session, fake_embedder, name="김민호")
    answerer = _setup_query(app, monkeypatch, utt, _search("팀장"), judge=FakeJudge(fail="timeout"))
    resp = _post_chat(client, utt, session_id)
    assert resp.status_code == 200
    body = resp.json()
    return a, b, answerer, body


def test_chat_query_identity_asks_then_answer_stored_zero_no_writes(
    app_and_client, db_session, fake_embedder, monkeypatch
):
    app, client = app_and_client
    utt = "팀장님 어떤 분이었지?"
    a, b, answerer, body = _ask_identity_over_http(
        app, client, db_session, fake_embedder, monkeypatch, utt, "api-q-ident"
    )
    # 되묻기로 끝난 턴 -- 저장 0, 질문 1행(identity), 답 생성기는 아직 안 불렸다.
    assert body["stop_reason"] == "ask_user"
    assert body["pending_question"]["kind"] == "identity"
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert answerer.call_count == 0
    qid = body["pending_question"]["question_id"]
    assert "김민수" in body["pending_question"]["options"]
    before = _counts(db_session)

    resp = client.post(f"/answers/{qid}", json={"answer": "김민수"})

    assert resp.status_code == 200
    out = resp.json()
    assert out["reply"] == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert out["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert out["pending_question"] is None
    assert out["stop_reason"] is None
    assert answerer.call_count == 1
    # 재개 뒤에도 행 수 불변(별칭 누적 없음 -- 결정 G (a)) · 기록 툴 tool_call 0.
    assert _counts(db_session) == before
    assert _write_tool_rows(db_session, "api-q-ident") == 0
    # 카드 근거 -- 고른 인물(김민수) 의 카드 건수.
    queries = _rows(db_session, "api-q-ident", "loop_query")
    assert len(queries) == 2  # 되묻기 턴(ask) + 재개 턴(llm)
    assert queries[0].output["answer_source"] == "ask"
    q = queries[1].output
    assert q["answer_source"] == "llm"
    assert q["person_id"] == a.id
    assert q["person_id"] != b.id
    assert q["evidence_counts"] == {"facts": 3, "patterns": 0, "timeline": 5, "schedules": 2}
    # 재개 trace -- loop_resume·loop_query·loop_turn, 기록 단계 행 없음.
    assert len(_rows(db_session, "api-q-ident", "loop_resume")) == 1
    assert _rows(db_session, "api-q-ident", "loop_resolve_done") == []
    assert _rows(db_session, "api-q-ident", "loop_record") == []


def test_chat_query_identity_second_answer_returns_409(app_and_client, db_session, fake_embedder, monkeypatch):
    app, client = app_and_client
    utt = "팀장님 어떤 분이었지?"
    _, _, _, body = _ask_identity_over_http(
        app, client, db_session, fake_embedder, monkeypatch, utt, "api-q-409"
    )
    qid = body["pending_question"]["question_id"]

    first = client.post(f"/answers/{qid}", json={"answer": "김민수"})
    second = client.post(f"/answers/{qid}", json={"answer": "김민수"})

    assert first.status_code == 200
    assert second.status_code == 409


# ---------------------------------------------------------------------------
# (3) new_person 조회 -- 질문 없이 "기록 없음"
# ---------------------------------------------------------------------------


def test_chat_query_new_person_no_question_no_writes(app_and_client, db_session, fake_embedder, monkeypatch):
    app, client = app_and_client
    utt = "박선우 과장님 어떤 분이었지?"
    answerer = _setup_query(app, monkeypatch, utt, _search("박선우"), judge=FakeJudge())
    before = _counts(db_session)

    resp = _post_chat(client, utt, "api-q-new")

    assert resp.status_code == 200
    body = resp.json()
    assert body["pending_question"] is None
    assert body["stop_reason"] is None
    assert body["reply"] == no_record_reply(["박선우"])
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert answerer.call_count == 0
    assert _counts(db_session) == before
    assert _counts(db_session)["pending_questions"] == 0
    ask_rows = db_session.execute(
        text("SELECT count(*) FROM agent_traces WHERE session_id = 'api-q-new' AND tool_name = 'ask_user'")
    ).scalar_one()
    assert ask_rows == 0
    assert _write_tool_rows(db_session, "api-q-new") == 0


# ---------------------------------------------------------------------------
# (4) 혼합 발화 -- 기록 제안은 게이트가 거부
# ---------------------------------------------------------------------------


def test_chat_query_turn_mixed_utterance_no_writes_loop_gate_rejects(
    app_and_client, db_session, fake_embedder, monkeypatch
):
    app, client = app_and_client
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이야? 어제 같이 점심 먹었어"
    calls = _search("팀장") + [
        {
            "name": "add_event",
            "args": {"person": "팀장", "type": "meal", "content": "점심", "occurred_at": NOW.isoformat()},
        }
    ]
    _setup_query(app, monkeypatch, utt, calls, judge=FakeJudge(table={person.id: 0.95}))
    before = _counts(db_session)

    resp = _post_chat(client, utt, "api-q-mixed")

    assert resp.status_code == 200
    assert resp.json()["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert _counts(db_session) == before
    assert _write_tool_rows(db_session, "api-q-mixed") == 0
    gate = _rows(db_session, "api-q-mixed", "loop_gate")[0].output
    assert {"index": 1, "name": "add_event", "reason": "query_turn_no_write"} in gate["rejected"]


# ---------------------------------------------------------------------------
# (5) 대조군 -- 기록 턴은 그대로 저장한다
# ---------------------------------------------------------------------------


def test_chat_record_turn_control_still_adds_event(app_and_client, db_session, fake_embedder, monkeypatch):
    app, client = app_and_client
    person = _seed_person(db_session, fake_embedder, events=0, facts=0, schedules=0)
    utt = "어제 팀장이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {"person": "팀장", "type": "meal", "content": "저녁", "occurred_at": NOW.isoformat()},
        }
    ]
    # intents 없음 -> 기본 record. 조회 분기가 새 답 생성기를 부르면 안 된다.
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utt: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person.id: 0.95})
    before = _counts(db_session)

    resp = _post_chat(client, utt, "api-q-control")

    assert resp.status_code == 200
    assert resp.json()["stored"]["events"] == 1
    after = _counts(db_session)
    assert after["events"] == before["events"] + 1
    assert len(_rows(db_session, "api-q-control", "loop_query")) == 0
    assert len(_rows(db_session, "api-q-control", "loop_record")) == 1


# ---------------------------------------------------------------------------
# (6) R-U5-1 -- 조회 identity 질문 뒤 후보 인물이 사라진 경우
# ---------------------------------------------------------------------------


def test_chat_query_resume_person_deleted_says_no_record_stored_zero(
    app_and_client, db_session, fake_embedder, monkeypatch
):
    app, client = app_and_client
    utt = "팀장님 어떤 분이었지?"
    a, _, answerer, body = _ask_identity_over_http(
        app, client, db_session, fake_embedder, monkeypatch, utt, "api-q-gone"
    )
    qid = body["pending_question"]["question_id"]
    # 질문을 낸 뒤 고른 후보(김민수) 가 삭제됐다 -- 실제 카드 조회가 PersonNotFound 를 낸다.
    db_session.execute(text("DELETE FROM persons WHERE id = :i"), {"i": a.id})
    db_session.flush()
    with pytest.raises(PersonNotFound):
        from app.api.read import get_person_card

        get_person_card(db_session, "local", a.id, datetime.now(timezone.utc))
    before = _counts(db_session)

    resp = client.post(f"/answers/{qid}", json={"answer": "김민수"})

    assert resp.status_code == 200
    out = resp.json()
    assert out["reply"] == no_record_reply(["팀장"])
    assert out["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert out["pending_question"] is None
    assert answerer.call_count == 0
    assert _counts(db_session) == before
    queries = _rows(db_session, "api-q-gone", "loop_query")
    assert [r.output["answer_source"] for r in queries] == ["ask", "no_record"]
    q = queries[1].output
    assert q["person_id"] is None
    assert q["answer_source"] == "no_record"


# ---------------------------------------------------------------------------
# (7) 세션 헤더 없이도 동작
# ---------------------------------------------------------------------------


def test_chat_query_issues_session_id_when_header_missing(app_and_client, db_session, fake_embedder, monkeypatch):
    app, client = app_and_client
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이었지?"
    _setup_query(app, monkeypatch, utt, _search("팀장"), judge=FakeJudge(table={person.id: 0.95}))

    resp = _post_chat(client, utt, None)

    assert resp.status_code == 200
    body = resp.json()
    uuid.UUID(body["session_id"])  # uuid4 형식이 아니면 ValueError
    assert body["reply"] == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert len(_rows(db_session, body["session_id"], "loop_query")) == 1
