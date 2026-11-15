"""Refs: P9b-auth U4 D18 CR-006 결정 I 결정 R security 원칙9 -- 계정당 채팅방 하나의 대화 기록
(`chat_messages` 저장 + `GET /chat/history`).

LLM 은 기존 시험과 같은 방식(`FakeProposer`·`FakeJudge`·`fake_embedder`, 네트워크 0)이다.
요청 실패 시 기록이 롤백되는지 보려면 운영의 `get_session`(정상 종료 commit · 예외 rollback)과 같은
모양의 의존성이 필요하다 -- 이 파일의 `env` 픽스처가 그것을 `db_session`(바깥 트랜잭션 + SAVEPOINT)
위에 올린다. 준비 데이터는 `db_session.commit()` 으로 한 번 확정해 두므로 이후 요청이 롤백돼도
준비 데이터는 남고, 그 요청이 쓴 행만 사라진다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError

import app.api.routes as routes_module
from app.agent.propose import FakeProposer
from app.api.deps import get_embedder, get_judge, get_proposer, get_session
from app.chat.history import HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT, append, recent
from app.db.models import ALIAS_SOURCES, AgentTrace, ChatMessage, Person, PersonAlias
from app.er.judge import FakeJudge
from app.er.types import JudgeUnavailable
from app.main import create_app
from tests.auth_helpers import logged_in_client

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 9, 25, 19, 0, 0, tzinfo=timezone.utc)
A_ID = "hist-user-a"
B_ID = "hist-user-b"
IDENTITY_REJECT = "아니요, 다른 사람이에요"

UTT1 = "팀장이랑 점심 먹었어"
UTT2 = "그냥 고마워서 말해봐"
CALLS1 = [
    {
        "name": "add_event",
        "args": {
            "person": "팀장",
            "type": "meal",
            "content": "점심",
            "occurred_at": NOW.isoformat(),
        },
    }
]


class _Env:
    def __init__(self, app, db, client_a, client_b, person) -> None:
        self.app = app
        self.db = db
        self.a = client_a
        self.b = client_b
        self.person = person

    def history(self, client, **params):
        resp = client.get("/chat/history", params=params)
        assert resp.status_code == 200
        return resp.json()

    def count(self, user_id: str) -> int:
        self.db.flush()
        return self.db.execute(
            select(func.count()).select_from(ChatMessage).where(ChatMessage.user_id == user_id)
        ).scalar_one()


@pytest.fixture()
def env(db_session, fake_embedder):
    app = create_app()

    def request_session():
        # 운영 `get_session` 과 같은 규약(정상 commit · 예외 rollback)을 SAVEPOINT 위에서 낸다.
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_session] = request_session
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(
        table={UTT1: CALLS1, UTT2: []}
    )
    client_a = logged_in_client(app, db_session, A_ID, raise_server_exceptions=False)
    client_b = logged_in_client(app, db_session, B_ID, raise_server_exceptions=False)
    person = Person(user_id=A_ID, display_name="김민수", relation_tag="직장", hierarchy="동")
    db_session.add(person)
    db_session.flush()
    db_session.add(
        PersonAlias(
            person_id=person.id,
            alias="팀장",
            source=ALIAS_SOURCES[0],
            embedding=fake_embedder(["팀장"])[0],
        )
    )
    db_session.commit()
    return _Env(app, db_session, client_a, client_b, person)


def _run_flow(env):
    """채팅 → (질문) → 답변 → 채팅. 응답 본문 셋을 돌려준다(질문이 둘 오간다)."""
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    assert r1.status_code == 200
    q1 = r1.json()["pending_question"]
    assert q1 is not None and q1["kind"] == "identity"  # 헛돎 방지 -- 원하는 경로를 탔다
    r2 = env.a.post(f"/answers/{q1['question_id']}", json={"answer": IDENTITY_REJECT})
    assert r2.status_code == 200
    q2 = r2.json()["pending_question"]
    assert q2 is not None and q2["kind"] == "new_person"
    r3 = env.a.post("/chat", json={"utterance": UTT2})
    assert r3.status_code == 200
    return r1.json(), r2.json(), r3.json()


# ---------------------------------------------------------------------------
# 저장 규칙(결정 R) + 조회 모양·순서
# ---------------------------------------------------------------------------


def test_two_chats_and_one_answer_give_six_rows_in_order_with_question_ids(env):
    b1, b2, b3 = _run_flow(env)
    q1 = b1["pending_question"]["question_id"]
    q2 = b2["pending_question"]["question_id"]
    assert q1 != q2

    items = env.history(env.a)

    assert [(i["role"], i["content"], i["question_id"]) for i in items] == [
        ("user", UTT1, None),
        ("assistant", b1["reply"], q1),
        ("user", IDENTITY_REJECT, q1),
        ("assistant", b2["reply"], q2),
        ("user", UTT2, None),
        ("assistant", b3["reply"], None),
    ]
    ids = [i["id"] for i in items]
    assert ids == sorted(ids) and len(set(ids)) == 6


def test_history_item_shape_matches_frontend_type(env):
    _run_flow(env)

    items = env.history(env.a)

    for item in items:
        assert set(item) == {"id", "role", "content", "question_id", "created_at"}
        assert isinstance(item["id"], int)
        assert item["role"] in ("user", "assistant")
        assert isinstance(item["content"], str)
        assert item["question_id"] is None or isinstance(item["question_id"], int)
        created = datetime.fromisoformat(item["created_at"])
        assert created.tzinfo is not None
    assert items[0]["question_id"] is None and items[1]["question_id"] is not None


def test_limit_returns_latest_rows_oldest_first(env):
    _run_flow(env)
    full = env.history(env.a)

    assert env.history(env.a, limit=2) == full[-2:]
    assert env.history(env.a, limit=1) == full[-1:]
    assert env.history(env.a, limit=5) == full[-5:]
    assert env.history(env.a, limit=200) == full


def test_default_limit_is_fifty_and_max_is_two_hundred(env):
    assert (HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT) == (50, 200)
    for n in range(60):
        append(env.db, A_ID, "user" if n % 2 == 0 else "assistant", f"줄 {n}")
    env.db.flush()

    default = env.history(env.a)
    wide = env.history(env.a, limit=200)

    assert [i["content"] for i in default] == [f"줄 {n}" for n in range(10, 60)]
    assert [i["content"] for i in wide] == [f"줄 {n}" for n in range(60)]


@pytest.mark.parametrize("limit", ["0", "201", "-1", "abc"])
def test_limit_out_of_range_is_422(env, limit):
    resp = env.a.get("/chat/history", params={"limit": limit})
    assert resp.status_code == 422


def test_order_is_created_at_then_id_and_latest_pick_uses_same_key(env):
    rows = [append(env.db, A_ID, "user", name) for name in ("r1", "r2", "r3", "r4")]
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # id 순서(r1<r2<r3<r4)와 created_at 순서를 일부러 어긋나게 한다. r3·r4 는 같은 시각(동률 -> id).
    stamps = {
        rows[0].id: base + timedelta(minutes=30),  # r1: 가장 늦음
        rows[1].id: base + timedelta(minutes=10),  # r2: 가장 이름
        rows[2].id: base + timedelta(minutes=20),  # r3
        rows[3].id: base + timedelta(minutes=20),  # r4(r3 과 동률)
    }
    for row_id, stamp in stamps.items():
        env.db.execute(update(ChatMessage).where(ChatMessage.id == row_id).values(created_at=stamp))
    env.db.flush()
    env.db.expire_all()

    assert [r.content for r in recent(env.db, A_ID, 10)] == ["r2", "r3", "r4", "r1"]
    assert [r.content for r in recent(env.db, A_ID, 2)] == ["r4", "r1"]
    assert [r.content for r in recent(env.db, A_ID, 1)] == ["r1"]
    assert [i["content"] for i in env.history(env.a, limit=3)] == ["r3", "r4", "r1"]


def test_same_transaction_rows_keep_insert_order_by_id(env):
    """한 트랜잭션 안(= `created_at` 동률)에서 사용자 줄 -> 응답 줄 순서를 `id` 가 지킨다."""
    for n in range(6):
        append(env.db, A_ID, "user" if n % 2 == 0 else "assistant", f"t{n}")
    env.db.flush()

    assert [i["content"] for i in env.history(env.a, limit=4)] == ["t2", "t3", "t4", "t5"]


def test_append_rejects_unknown_role_and_writes_nothing(env):
    before = env.count(A_ID)
    with pytest.raises(ValueError):
        append(env.db, A_ID, "system", "x")
    assert env.count(A_ID) == before


# ---------------------------------------------------------------------------
# 계정 격리 · 로그인 필수 · 읽기 전용
# ---------------------------------------------------------------------------


def test_other_accounts_history_is_never_mixed(env):
    _run_flow(env)
    # B 의 기록 1줄(같은 질문 id 를 달아도 B 의 것이다).
    append(env.db, B_ID, "user", "B 만의 말 ZXCV", question_id=None)
    env.db.flush()

    a_items = env.history(env.a)
    b_items = env.history(env.b)

    assert len(a_items) == 6
    assert all("ZXCV" not in i["content"] for i in a_items)
    assert [(i["role"], i["content"]) for i in b_items] == [("user", "B 만의 말 ZXCV")]
    assert env.history(env.b, limit=200) == b_items
    assert env.count(A_ID) == 6 and env.count(B_ID) == 1


def test_chat_saves_only_to_the_logged_in_account(env):
    r = env.b.post("/chat", json={"utterance": UTT2})
    assert r.status_code == 200

    assert env.count(B_ID) == 2
    assert env.count(A_ID) == 0
    assert env.history(env.a) == []


def test_answering_other_users_question_is_404_and_saves_nothing_for_either(env):
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    qid = r1.json()["pending_question"]["question_id"]
    a_before, b_before = env.count(A_ID), env.count(B_ID)

    other = env.b.post(f"/answers/{qid}", json={"answer": IDENTITY_REJECT})

    assert other.status_code == 404
    assert (env.count(A_ID), env.count(B_ID)) == (a_before, b_before)
    assert a_before == 2 and b_before == 0


def test_history_requires_login(env):
    from fastapi.testclient import TestClient

    anonymous = TestClient(env.app, base_url="https://testserver", raise_server_exceptions=False)
    resp = anonymous.get("/chat/history")
    assert resp.status_code == 401
    assert anonymous.get("/chat/history", params={"limit": 2}).status_code == 401


def test_history_read_writes_nothing_and_leaves_no_trace(env):
    _run_flow(env)
    env.db.flush()
    msgs = env.count(A_ID)
    traces = env.db.execute(select(func.count()).select_from(AgentTrace)).scalar_one()

    for _ in range(3):
        env.history(env.a)
        env.history(env.a, limit=2)

    assert env.count(A_ID) == msgs
    assert env.db.execute(select(func.count()).select_from(AgentTrace)).scalar_one() == traces


# ---------------------------------------------------------------------------
# 실패 · 롤백 · 루프가 삼킨 오류
# ---------------------------------------------------------------------------


class _DbErrorProposer:
    def propose(self, utterance: str, now: datetime):
        raise SQLAlchemyError("simulated-db-failure-detail")


class _FailingProposer:
    def propose(self, utterance: str, now: datetime):
        raise JudgeUnavailable("timeout")


def test_failed_chat_request_leaves_no_history_rows(env):
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    assert r1.status_code == 200
    assert env.count(A_ID) == 2  # 앞선 성공 턴의 기록은 남는다
    env.app.dependency_overrides[get_proposer] = lambda: _DbErrorProposer()

    resp = env.a.post("/chat", json={"utterance": UTT2})

    assert resp.status_code == 500
    assert env.count(A_ID) == 2
    assert [i["content"] for i in env.history(env.a)][0] == UTT1
    assert UTT2 not in [i["content"] for i in env.history(env.a)]


def test_failed_answer_request_leaves_no_history_rows(env, monkeypatch):
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    qid = r1.json()["pending_question"]["question_id"]
    assert env.count(A_ID) == 2

    def boom(*args, **kwargs):
        raise SQLAlchemyError("simulated-resume-db-failure")

    monkeypatch.setattr(routes_module, "resume_turn", boom)

    resp = env.a.post(f"/answers/{qid}", json={"answer": IDENTITY_REJECT})

    assert resp.status_code == 500
    assert env.count(A_ID) == 2
    assert IDENTITY_REJECT not in [i["content"] for i in env.history(env.a)]


def test_chat_loop_error_swallowed_as_200_still_saves_both_rows(env):
    env.app.dependency_overrides[get_proposer] = lambda: _FailingProposer()

    resp = env.a.post("/chat", json={"utterance": UTT2})

    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == routes_module._LOOP_ERROR_REPLY
    assert [(i["role"], i["content"], i["question_id"]) for i in env.history(env.a)] == [
        ("user", UTT2, None),
        ("assistant", routes_module._LOOP_ERROR_REPLY, None),
    ]


def test_answer_loop_error_swallowed_as_200_still_saves_both_rows(env, monkeypatch):
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    qid = r1.json()["pending_question"]["question_id"]

    def unavailable(*args, **kwargs):
        raise JudgeUnavailable("timeout")

    monkeypatch.setattr(routes_module, "resume_turn", unavailable)

    resp = env.a.post(f"/answers/{qid}", json={"answer": IDENTITY_REJECT})

    assert resp.status_code == 200
    assert resp.json()["reply"] == routes_module._LOOP_ERROR_REPLY
    items = env.history(env.a)
    assert [(i["role"], i["content"], i["question_id"]) for i in items[-2:]] == [
        ("user", IDENTITY_REJECT, qid),
        ("assistant", routes_module._LOOP_ERROR_REPLY, None),
    ]
    assert len(items) == 4


def test_second_answer_409_leaves_history_rows_unchanged(env):
    """U4 R-1 -- 이미 답한 질문에 다시 답하면 409 이고 기록은 4행 그대로(두 번째 답이 안 쌓인다)."""
    r1 = env.a.post("/chat", json={"utterance": UTT1})
    qid = r1.json()["pending_question"]["question_id"]
    r2 = env.a.post(f"/answers/{qid}", json={"answer": IDENTITY_REJECT})
    assert r2.status_code == 200
    before = env.history(env.a)
    assert len(before) == 4

    again = env.a.post(f"/answers/{qid}", json={"answer": IDENTITY_REJECT})

    assert again.status_code == 409
    assert again.json()["detail"]["code"] == "already_answered"
    assert env.history(env.a) == before
    assert env.count(A_ID) == 4


# ---------------------------------------------------------------------------
# 결정 V -- 발화 최대 2000자
# ---------------------------------------------------------------------------


class _CountingProposer(FakeProposer):
    def __init__(self, table):
        super().__init__(table=table)
        self.calls = 0

    def propose(self, utterance, now):
        self.calls += 1
        return super().propose(utterance, now)


def _trace_count(db) -> int:
    db.flush()
    return db.execute(select(func.count()).select_from(AgentTrace)).scalar_one()


def test_utterance_of_exactly_2000_chars_is_accepted_and_2001_is_rejected_with_no_side_effects(
    env,
):
    ok_text = "가" * 2000
    too_long = "가" * 2001
    proposer = _CountingProposer({ok_text: [], too_long: []})
    env.app.dependency_overrides[get_proposer] = lambda: proposer

    ok = env.a.post("/chat", json={"utterance": ok_text})
    assert ok.status_code == 200
    assert proposer.calls == 1
    rows_before = env.count(A_ID)
    traces_before = _trace_count(env.db)

    resp = env.a.post("/chat", json={"utterance": too_long})

    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert isinstance(detail, list) and len(detail) == 1  # 기존 422 와 같은 모양(pydantic 목록)
    assert detail[0]["loc"] == ["body", "utterance"]
    assert detail[0]["type"] == "string_too_long"
    assert proposer.calls == 1  # LLM(인식 단계) 호출 0
    assert env.count(A_ID) == rows_before  # DB 기록 0
    assert _trace_count(env.db) == traces_before  # trace 도 0


def test_existing_chat_validation_unchanged_empty_utterance_still_422(env):
    resp = env.a.post("/chat", json={"utterance": ""})

    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail[0]["loc"] == ["body", "utterance"]
    assert detail[0]["type"] == "string_too_short"
