"""Refs: P9b-auth U3b D18 S3.4 CR-006 F-fbaaae 원칙1 원칙9 -- 계정 간 격리(이 패키지의 본체).

계정 A·B 를 만들고 **B 의 인물·별칭·사건·사실·일정·브리핑 trace·질문을 직접 넣은 뒤** A 의 쿠키로 모든
API 를 두드린다. 남의 자원은 "없는 자원"과 **구별되지 않는** 같은 404 여야 하고(존재 여부 비노출),
B 의 데이터는 어떤 경로로도 바뀌지 않는다.

- 응답 구별 불가: 남의 id 에 대한 응답과 **존재하지 않는 id** 에 대한 응답이 상태·본문 모두 같다.
- 답변 소유(F-fbaaae): B 의 질문에 A 가 답하면 404, 그 행의 `answer`·`answered_at` 불변, **재개 루프
  호출 0**(`resume_turn` 을 호출 수를 세는 스텁으로 바꿔 본다 -- 통제 케이스로 스텁이 실제로 불리는
  경로에서는 1 이 되는 것도 함께 본다).
- `session_id` 는 서버가 계정에서 만든 `chat:<user_id>` 다. 헤더 `X-Session-Id: chat:<B>` 를 보내도
  바뀌지 않는다.
- 툴 층도 계정 경계다: A 의 ctx 로 B 의 인물에 `add_event`·`get_briefing`·`add_schedule`·`update_person`
  을 부르면 `PersonNotFound` 이고 B 의 행은 그대로다(`person_id` 가 이제 계정 경계, R-4 ②).

실 PostgreSQL 필요(`dbtest`). LLM·외부 네트워크 0.
"""

from __future__ import annotations

import dataclasses
import inspect
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

import app.agent.loop as loop_module
import app.api.routes as routes_module
from app.agent.propose import FakeProposer
from app.api.deps import (
    get_briefing_composer,
    get_embedder,
    get_judge,
    get_notifier,
    get_now,
    get_proposer,
    get_session,
)
from app.briefing.compose import FakeBriefingComposer
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    NullNotifier,
)
from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    Event,
    FactSource,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    PushSubscription,
    Schedule,
)
from app.er.judge import FakeJudge
from app.main import create_app
from app.tools import add_event, add_schedule, answer_question, get_briefing, update_person
from app.tools.context import ToolContext
from app.tools.types import PersonNotFound, QuestionNotFound
from tests.auth_helpers import logged_in_client, make_ctx, make_user

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
NOT_FOUND = {"detail": {"code": "not_found"}}
A_ID = "iso-user-a"
B_ID = "iso-user-b"
#: 존재하지 않는 id(테스트 DB 의 시퀀스가 도달할 수 없는 값).
MISSING = 987_654_321
B_RAW = "B 만의 비밀 원문 QWERTY"


class World:
    """계정 A·B 와 B 의 자원 하나씩 + 각자의 로그인 클라이언트."""

    def __init__(self, app, db, fake_embedder) -> None:
        self.app = app
        self.db = db
        self.user_a = make_user(db, A_ID)
        self.user_b = make_user(db, B_ID)
        self.client_a = logged_in_client(app, db, A_ID)
        self.client_b = logged_in_client(app, db, B_ID)

        # --- A 의 자원(통제 케이스: 같은 API 가 내 것에는 200 을 준다) ---
        self.a_person = self._person(A_ID, "에이사람", "에이별칭", fake_embedder)
        self.a_event = self._event(self.a_person, "A 원문 ASDF")
        self.a_fact = self._fact(self.a_person, [self.a_event])
        self.a_schedule = self._schedule(self.a_person, NOW + timedelta(hours=3))
        self.a_trace = self._briefing_trace(self.a_schedule, self.a_person)

        # --- B 의 자원(A 가 건드릴 수 없어야 한다). 별칭은 A 의 언급과 같은 "민수"다 ---
        self.b_person = self._person(B_ID, "민수", "민수", fake_embedder)
        self.b_event = self._event(self.b_person, B_RAW)
        self.b_fact = self._fact(self.b_person, [self.b_event])
        self.b_schedule = self._schedule(self.b_person, NOW + timedelta(hours=5))
        self.b_trace = self._briefing_trace(self.b_schedule, self.b_person)
        self.b_question = self._question(B_ID, f"chat:{B_ID}")

    # ----- 데이터 준비 -----
    def _person(self, user_id, name, alias, fake_embedder) -> Person:
        p = Person(
            user_id=user_id,
            display_name=name,
            relation_tag="친구",
            hierarchy="동",
            updated_at=NOW - timedelta(days=30),
        )
        self.db.add(p)
        self.db.flush()
        self.db.add(
            PersonAlias(
                person_id=p.id,
                alias=alias,
                source=ALIAS_SOURCES[0],
                embedding=fake_embedder([alias])[0],
            )
        )
        self.db.flush()
        return p

    def _event(self, person, raw) -> Event:
        e = Event(
            person_id=person.id,
            type="meal",
            content="저녁",
            raw_utterance=raw,
            occurred_at=NOW - timedelta(days=1),
        )
        self.db.add(e)
        self.db.flush()
        return e

    def _fact(self, person, events) -> PersonFact:
        f = PersonFact(person_id=person.id, key="취미", value="등산", confidence=1.0)
        self.db.add(f)
        self.db.flush()
        for e in events:
            self.db.add(FactSource(fact_id=f.id, event_id=e.id))
        self.db.flush()
        return f

    def _schedule(self, person, when) -> Schedule:
        s = Schedule(person_id=person.id, title="약속", scheduled_at=when)
        self.db.add(s)
        self.db.flush()
        return s

    def _briefing_trace(self, schedule, person) -> AgentTrace:
        t = AgentTrace(
            session_id="briefing:test",
            step=STEP_BRIEFING_COMPOSE,
            tool_name=BRIEFING_TRACE_TOOL_NAME,
            input={"schedule_id": schedule.id, "person_id": person.id},
            output={
                "schedule_id": schedule.id,
                "person_id": person.id,
                "pattern_trace_id": None,
                "used_facts": [],
                "excluded_facts": [],
                "event_ids": [],
                "composer": "template",
                "pattern_sentences": [],
                "lines": [],
                "suggestion": None,
                "rejected": [],
                "llm": {"provider": "fake", "model": "fake-1"},
                "push": "not_configured",
            },
            tokens_in=0,
            tokens_out=0,
            created_at=NOW - timedelta(hours=1),
        )
        self.db.add(t)
        self.db.flush()
        return t

    def _question(self, user_id, session_id, *, kind="schedule") -> PendingQuestion:
        q = PendingQuestion(
            session_id=session_id,
            user_id=user_id,
            kind=kind,
            question="질문",
            options=["예", "아니오"],
            context={},
            created_at=NOW - timedelta(minutes=1),
        )
        self.db.add(q)
        self.db.flush()
        return q


@pytest.fixture()
def world(db_session, fake_embedder):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    app.dependency_overrides[get_notifier] = lambda: NullNotifier()
    composer = FakeBriefingComposer()
    app.dependency_overrides[get_briefing_composer] = lambda: composer
    w = World(app, db_session, fake_embedder)
    w.composer = composer
    return w


def _counts(db) -> dict[str, int]:
    db.flush()
    return {
        name: db.execute(select(func.count()).select_from(model)).scalar_one()
        for name, model in {
            "persons": Person,
            "aliases": PersonAlias,
            "events": Event,
            "facts": PersonFact,
            "schedules": Schedule,
            "questions": PendingQuestion,
            "traces": AgentTrace,
            "subs": PushSubscription,
        }.items()
    }


# ---------------------------------------------------------------------------
# 읽기 -- 남의 자원은 "없음" 과 같은 404, 내 것은 그대로 200(통제)
# ---------------------------------------------------------------------------


def test_persons_list_has_only_my_persons(world):
    body = world.client_a.get("/persons").json()
    assert [p["id"] for p in body] == [world.a_person.id]
    assert "민수" not in str(body)
    # B 쪽에서도 대칭
    assert [p["id"] for p in world.client_b.get("/persons").json()] == [world.b_person.id]


def test_person_card_of_other_user_is_404_same_as_missing(world):
    other = world.client_a.get(f"/persons/{world.b_person.id}")
    missing = world.client_a.get(f"/persons/{MISSING}")
    assert other.status_code == 404
    assert other.json() == NOT_FOUND
    assert (other.status_code, other.json()) == (missing.status_code, missing.json())
    # 통제: 내 카드는 200 이고 내 이름이다.
    mine = world.client_a.get(f"/persons/{world.a_person.id}")
    assert mine.status_code == 200
    assert mine.json()["person"]["display_name"] == "에이사람"
    assert mine.json()["person"]["id"] == world.a_person.id


def test_event_raw_of_other_user_is_404_same_as_missing(world):
    other = world.client_a.get(f"/events/{world.b_event.id}/raw")
    missing = world.client_a.get(f"/events/{MISSING}/raw")
    assert other.status_code == 404
    assert other.json() == NOT_FOUND
    assert (other.status_code, other.json()) == (missing.status_code, missing.json())
    assert B_RAW not in other.text
    # 통제: 내 원문은 그대로 200.
    mine = world.client_a.get(f"/events/{world.a_event.id}/raw")
    assert mine.status_code == 200
    assert "A 원문 ASDF" in mine.text


def test_fact_sources_of_other_user_is_404_same_as_missing(world):
    b_path = f"/persons/{world.b_person.id}/facts/{world.b_fact.id}/sources"
    other = world.client_a.get(b_path)
    missing = world.client_a.get(f"/persons/{MISSING}/facts/{MISSING}/sources")
    assert other.status_code == 404
    assert other.json() == NOT_FOUND
    assert (other.status_code, other.json()) == (missing.status_code, missing.json())
    assert B_RAW not in other.text
    # 섞어 넣기: 내 인물 id + B 의 사실 id 도 404.
    cross = world.client_a.get(f"/persons/{world.a_person.id}/facts/{world.b_fact.id}/sources")
    assert cross.status_code == 404
    assert B_RAW not in cross.text
    # 통제: 내 사실 근거는 200.
    mine = world.client_a.get(f"/persons/{world.a_person.id}/facts/{world.a_fact.id}/sources")
    assert mine.status_code == 200
    assert "A 원문 ASDF" in mine.text


def test_briefings_list_and_schedule_filter_are_scoped(world):
    # 목록에는 내 일정 것만(B 의 것 0).
    body = world.client_a.get("/briefings").json()
    assert [b["schedule"]["id"] for b in body] == [world.a_schedule.id]
    # schedule_id 로 남의 일정을 지정하면 404 — 없는 일정과 같은 응답.
    other = world.client_a.get(f"/briefings?schedule_id={world.b_schedule.id}")
    missing = world.client_a.get(f"/briefings?schedule_id={MISSING}")
    assert other.status_code == 404
    assert other.json() == NOT_FOUND
    assert (other.status_code, other.json()) == (missing.status_code, missing.json())


# ---------------------------------------------------------------------------
# 쓰기 -- 브리핑 실행·푸시 구독
# ---------------------------------------------------------------------------


def test_briefing_run_with_other_users_schedule_is_404_and_changes_nothing(world):
    before = _counts(world.db)
    b_briefed_before = world.b_schedule.briefed_at
    resp = world.client_a.post("/briefings/run", json={"schedule_id": world.b_schedule.id})
    missing = world.client_a.post("/briefings/run", json={"schedule_id": MISSING})
    assert resp.status_code == 404
    assert resp.json() == NOT_FOUND
    assert (resp.status_code, resp.json()) == (missing.status_code, missing.json())
    world.db.refresh(world.b_schedule)
    assert world.b_schedule.briefed_at == b_briefed_before
    assert _counts(world.db) == before
    assert world.composer.call_count == 0


def test_briefing_run_without_body_only_briefs_my_schedules(world):
    """주기 선정과 같은 창 선정 — B 의 일정(창 안)이 있어도 A 의 실행은 A 의 일정만 만든다."""
    resp = world.client_a.post("/briefings/run")
    assert resp.status_code == 200
    briefed = [item["schedule_id"] for item in resp.json()["briefings"]]
    assert briefed == [world.a_schedule.id]
    assert resp.json()["skipped"] == []  # B 일정이 건너뜀 목록에도 나타나지 않는다
    world.db.refresh(world.a_schedule)
    world.db.refresh(world.b_schedule)
    assert world.a_schedule.briefed_at == NOW
    assert world.b_schedule.briefed_at is None
    assert world.composer.call_count == 1


def test_push_subscription_belongs_to_the_logged_in_user(world):
    sub = {
        "endpoint": "https://push.example.test/iso/1",
        "keys": {"p256dh": "p256dh-value", "auth": "auth-value"},
    }
    resp = world.client_a.post("/push/subscriptions", json=sub)
    assert resp.status_code == 200
    rows = world.db.execute(select(PushSubscription)).scalars().all()
    assert [(r.user_id, r.endpoint) for r in rows] == [(A_ID, sub["endpoint"])]


# ---------------------------------------------------------------------------
# 대기 질문 -- 목록·답변 소유(F-fbaaae)
# ---------------------------------------------------------------------------


def test_pending_questions_list_has_only_my_chatroom_questions(world):
    mine = world._question(A_ID, f"chat:{A_ID}")
    # 같은 세션 이름이라도 소유가 B 면 나가지 않는다(소유 조건이 세션 조건과 별개로 걸린다).
    world._question(B_ID, f"chat:{A_ID}")
    ids = [q["question_id"] for q in world.client_a.get("/questions/pending").json()]
    assert ids == [mine.id]
    # B 의 목록에는 B 의 질문(자기 채팅방) 하나.
    b_ids = [q["question_id"] for q in world.client_b.get("/questions/pending").json()]
    assert b_ids == [world.b_question.id]


def _spy_resume(monkeypatch):
    calls = {"n": 0}
    real = routes_module.resume_turn

    def _spy(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(routes_module, "resume_turn", _spy)
    return calls


def test_answering_other_users_question_is_404_no_change_no_resume(world, monkeypatch):
    calls = _spy_resume(monkeypatch)
    before = _counts(world.db)
    q = world.b_question

    resp = world.client_a.post(f"/answers/{q.id}", json={"answer": "예"})
    missing = world.client_a.post(f"/answers/{MISSING}", json={"answer": "예"})

    assert resp.status_code == 404
    assert resp.json() == NOT_FOUND
    assert (resp.status_code, resp.json()) == (missing.status_code, missing.json())
    world.db.refresh(q)
    assert q.answer is None
    assert q.answered_at is None
    assert calls["n"] == 0  # 재개 루프 호출 0
    assert _counts(world.db) == before


def test_answering_question_in_my_chatroom_but_owned_by_other_is_404(world, monkeypatch):
    """세션 이름만 내 채팅방(`chat:A`)이고 소유가 B 인 질문 — 소유(user_id) 조건이 걸려야 막힌다."""
    calls = _spy_resume(monkeypatch)
    q = world._question(B_ID, f"chat:{A_ID}")
    resp = world.client_a.post(f"/answers/{q.id}", json={"answer": "예"})
    assert resp.status_code == 404
    world.db.refresh(q)
    assert (q.answer, q.answered_at) == (None, None)
    assert calls["n"] == 0


def test_answer_question_tool_rejects_other_users_question(world):
    """툴 층 방어(`build_ctx` 가 아니라 `answer_question` 의 `ctx.user_id` 조건)."""
    ctx_a = make_ctx(world.db, A_ID, session_id=f"chat:{A_ID}", now=lambda: NOW)
    q = world.b_question
    with pytest.raises(QuestionNotFound):
        answer_question(ctx_a, q.id, "예")
    world.db.refresh(q)
    assert (q.answer, q.answered_at) == (None, None)
    # 통제: B 의 ctx 로는 답할 수 있다(소유자는 된다).
    ctx_b = dataclasses.replace(ctx_a, user_id=B_ID)
    assert answer_question(ctx_b, q.id, "예").status == "answered"


def _chat_new_mention(client, mention="민수"):
    utterance = f"오늘 {mention}이랑 저녁 먹었어"
    return utterance, [
        {
            "name": "add_event",
            "args": {
                "person": mention,
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        }
    ]


def test_my_own_question_flow_still_works_and_creates_my_person(world, monkeypatch):
    """통제 케이스 + ER 격리 -- 빈 계정 C 의 "민수" 는 (같은 별칭·같은 임베딩을 가진) B 의 "민수" 로
    연결되지 않고 후보 0 으로 새 인물 확인을 묻는다. 답하면 인물이 **C 의 id** 로 생기고(B 는 그대로),
    재개 루프가 정확히 1회 불린다. 남(A·B)은 C 의 질문에 답할 수 없다(재개 0)."""
    calls = _spy_resume(monkeypatch)
    c_id = "iso-user-c"
    make_user(world.db, c_id)
    client_c = logged_in_client(world.app, world.db, c_id)
    utterance, tool_calls = _chat_new_mention(client_c)
    world.app.dependency_overrides[get_proposer] = lambda: FakeProposer(
        table={utterance: tool_calls}
    )
    before = _counts(world.db)

    r1 = client_c.post("/chat", json={"utterance": utterance})
    assert r1.status_code == 200
    assert r1.json()["session_id"] == f"chat:{c_id}"
    pq = r1.json()["pending_question"]
    assert pq is not None
    assert pq["kind"] == "new_person"  # B 의 "민수" 가 후보로 잡히면 identity 가 된다
    # ER trace 에 후보가 하나도 없다(B 의 별칭은 검색 범위 밖).
    er = world.db.execute(
        select(AgentTrace).where(
            AgentTrace.session_id == f"chat:{c_id}", AgentTrace.step == "er_resolve"
        )
    ).scalar_one()
    assert er.output["candidates"] == []
    row = world.db.get(PendingQuestion, pq["question_id"])
    assert (row.user_id, row.session_id) == (c_id, f"chat:{c_id}")

    # A·B 는 이 질문에 답할 수 없다(소유 검사) -- 재개 0.
    for other_client in (world.client_a, world.client_b):
        other = other_client.post(
            f"/answers/{pq['question_id']}", json={"answer": "친구로 기억할게요"}
        )
        assert other.status_code == 404
    assert calls["n"] == 0
    world.db.refresh(row)
    assert (row.answer, row.answered_at) == (None, None)

    r2 = client_c.post(f"/answers/{pq['question_id']}", json={"answer": "친구로 기억할게요"})
    assert r2.status_code == 200
    assert r2.json()["stored"] == {"persons": 1, "events": 1, "schedules": 0}
    assert calls["n"] == 1
    created = world.db.execute(
        select(Person).where(Person.display_name == "민수", Person.user_id == c_id)
    ).scalar_one()
    assert created.id != world.b_person.id
    # 늘어난 것은 C 의 인물 1명·사건 1건뿐 — B 의 인물·사건은 그대로.
    after = _counts(world.db)
    assert after["persons"] == before["persons"] + 1
    assert after["events"] == before["events"] + 1
    assert (
        world.db.execute(
            select(func.count()).select_from(Event).where(Event.person_id == world.b_person.id)
        ).scalar_one()
        == 1
    )


# ---------------------------------------------------------------------------
# session_id -- 서버가 계정에서 만든다
# ---------------------------------------------------------------------------


def test_chat_session_id_is_account_session_and_header_is_ignored(world):
    resp = world.client_a.post(
        "/chat", json={"utterance": "안녕"}, headers={"X-Session-Id": f"chat:{B_ID}"}
    )
    assert resp.status_code == 200
    assert resp.json()["session_id"] == f"chat:{A_ID}"
    sessions = {
        s
        for (s,) in world.db.execute(
            select(AgentTrace.session_id).where(AgentTrace.step.like("loop_%"))
        ).all()
    }
    assert f"chat:{A_ID}" in sessions
    assert f"chat:{B_ID}" not in sessions


def test_chat_session_id_without_header_is_account_session(world):
    resp = world.client_b.post("/chat", json={"utterance": "안녕"})
    assert resp.json()["session_id"] == f"chat:{B_ID}"


# ---------------------------------------------------------------------------
# person_id 가 계정 경계다 (R-4 ②) -- LLM 이 남의 인물을 가리켜도 끝난다
# ---------------------------------------------------------------------------


def test_loop_resolving_to_other_users_person_ends_with_person_not_found(world, monkeypatch):
    """ER 이 (가정상) B 의 인물을 골라도 툴 층이 `PersonNotFound` 로 막는다 -- 200 오류 답, B 불변."""
    utterance, tool_calls = _chat_new_mention(world.client_a)
    world.app.dependency_overrides[get_proposer] = lambda: FakeProposer(
        table={utterance: tool_calls}
    )
    real_resolve = loop_module.resolve

    def _force_b(ctx, mention, utterance_arg, hints, *, judge=None, config=None):
        res = real_resolve(ctx, mention, utterance_arg, hints, judge=judge, config=config)
        return dataclasses.replace(res, band="merge", matched_person_id=world.b_person.id)

    monkeypatch.setattr(loop_module, "resolve", _force_b)
    b_counts_before = _counts(world.db)
    b_traces_before = world.db.execute(
        select(func.count()).select_from(AgentTrace).where(AgentTrace.session_id == f"chat:{B_ID}")
    ).scalar_one()

    resp = world.client_a.post("/chat", json={"utterance": utterance})

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    errors = world.db.execute(
        select(AgentTrace).where(
            AgentTrace.session_id == f"chat:{A_ID}", AgentTrace.step == "loop_error"
        )
    ).scalars().all()
    assert [e.output["error"] for e in errors] == ["PersonNotFound"]
    # B 의 사건·별칭·trace 는 그대로.
    assert (
        world.db.execute(
            select(func.count()).select_from(Event).where(Event.person_id == world.b_person.id)
        ).scalar_one()
        == 1
    )
    assert (
        world.db.execute(
            select(func.count())
            .select_from(PersonAlias)
            .where(PersonAlias.person_id == world.b_person.id)
        ).scalar_one()
        == 1
    )
    assert (
        world.db.execute(
            select(func.count()).select_from(AgentTrace).where(AgentTrace.session_id == f"chat:{B_ID}")
        ).scalar_one()
        == b_traces_before
    )
    after = _counts(world.db)
    for key in ("persons", "aliases", "events", "facts", "schedules", "questions", "subs"):
        assert after[key] == b_counts_before[key], key


def test_tools_with_other_users_person_id_raise_person_not_found(world):
    ctx_a = make_ctx(world.db, A_ID, session_id=f"chat:{A_ID}")
    b_pid = world.b_person.id
    before = _counts(world.db)

    with pytest.raises(PersonNotFound):
        add_event(ctx_a, b_pid, "meal", "침투", NOW, "침투 원문")
    with pytest.raises(PersonNotFound):
        get_briefing(ctx_a, b_pid, world.b_schedule.id)
    with pytest.raises(PersonNotFound):
        add_schedule(ctx_a, b_pid, "침투 일정", NOW + timedelta(days=1))
    with pytest.raises(PersonNotFound):
        update_person(ctx_a, b_pid, new_alias="침투별칭")

    world.db.refresh(world.b_schedule)
    assert world.b_schedule.briefed_at is None
    after = _counts(world.db)
    for key in ("persons", "aliases", "events", "facts", "schedules", "questions", "subs"):
        assert after[key] == before[key], key


# ---------------------------------------------------------------------------
# 재개 context 가 남의 person_id 를 가리키는 경우 (review-u3b R-3)
# ---------------------------------------------------------------------------


def _b_state(world):
    db = world.db
    db.flush()
    db.expire_all()
    q = db.get(PendingQuestion, world.b_question.id)

    def n(model, col, val):
        return db.execute(select(func.count()).select_from(model).where(col == val)).scalar_one()

    return {
        "events": n(Event, Event.person_id, world.b_person.id),
        "aliases": n(PersonAlias, PersonAlias.person_id, world.b_person.id),
        "facts": n(PersonFact, PersonFact.person_id, world.b_person.id),
        "schedules": n(Schedule, Schedule.person_id, world.b_person.id),
        "briefed_at": db.get(Schedule, world.b_schedule.id).briefed_at,
        "question": (q.answer, q.answered_at),
        "traces": n(AgentTrace, AgentTrace.session_id, f"chat:{B_ID}"),
    }


@pytest.mark.parametrize("case", ["identity_record", "identity_query", "schedule"])
def test_resume_context_pointing_at_other_users_person_changes_nothing(world, case):
    """A 소유 질문의 `context` 에 B 의 `person_id` 를 심어도(`context` 는 소유 검사 대상이 아니다)
    B 의 사건·별칭·일정·브리핑·질문·trace 는 그대로이고 응답에 B 의 문자열이 없다."""
    resume = {"version": 1, "mention": "민수", "hints": {}, "held_drafts": [], "dropped": 0}
    ev_call = {
        "index": 0,
        "name": "add_event",
        "args": {"person": "민수", "type": "meal", "content": "침투", "occurred_at": NOW.isoformat()},
    }
    if case == "identity_record":
        kind, options, answer = "identity", ["민수 맞아요", "다른 사람"], "민수 맞아요"
        context = {
            "utterance": "민수랑 밥",
            "mention": "민수",
            "candidate_ids": {"민수 맞아요": world.b_person.id},
            "resume": {**resume, "pending_calls": [ev_call]},
        }
    elif case == "identity_query":
        kind, options, answer = "identity", ["민수 맞아요", "다른 사람"], "민수 맞아요"
        context = {
            "utterance": "민수 어떤 사람이었지?",
            "mention": "민수",
            "candidate_ids": {"민수 맞아요": world.b_person.id},
            "resume": {**resume, "pending_calls": [], "intent": "query"},
        }
    else:
        kind, options, answer = "schedule", ["내일", "모르겠어요"], "내일"
        context = {
            "utterance": "민수랑 약속",
            "resume": {
                **resume,
                "pending_calls": [
                    {"index": 0, "name": "add_schedule", "args": {"person": "민수", "title": "침투 약속"}},
                    {**ev_call, "index": 1},
                ],
                "schedule": {"person_id": world.b_person.id, "title": "침투 약속", "call_index": 0},
                "schedule_options": {"내일": (NOW + timedelta(days=1)).isoformat()},
            },
        }
    q = PendingQuestion(
        session_id=f"chat:{A_ID}",
        user_id=A_ID,
        kind=kind,
        question="q",
        options=options,
        context=context,
        created_at=datetime.now(timezone.utc),
    )
    world.db.add(q)
    world.db.flush()
    before = _b_state(world)

    resp = world.client_a.post(f"/answers/{q.id}", json={"answer": answer})

    assert resp.status_code in (200, 404)
    assert _b_state(world) == before
    assert B_RAW not in resp.text
    assert "등산" not in resp.text


# ---------------------------------------------------------------------------
# ToolContext.user_id 는 기본값이 없다 (D18 지킬 것 5)
# ---------------------------------------------------------------------------


def test_tool_context_user_id_has_no_default(db_session):
    param = inspect.signature(ToolContext).parameters["user_id"]
    assert param.default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        ToolContext(session=db_session, session_id="x")  # type: ignore[call-arg]
