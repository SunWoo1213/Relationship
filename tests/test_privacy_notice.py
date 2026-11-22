"""Refs: P9d-sensitive-guard U4 D20 D18 S3.1 S3.6 원칙9 -- OpenAI API 전송 고지(가입 동의·재고지·
미동의 403·주기 브리핑 건너뜀).

계약(01-plan "값으로 고정하는 계약" 표 그대로, 값으로 단언한다):

- 가입 본문 `privacy_notice_accepted` 가 없거나 `false`/`null` 이면 422
  `{"detail":{"code":"notice_required"}}`(목록 모양 아님), `users` 행 0. 검사 순서는 형식 3종 ->
  동의 -> 409 사전 조회.
- `MeOut.notice_required` -- 현재 판(`PRIVACY_NOTICE_VERSION == 1`) 미동의면 true.
- `POST /auth/privacy-notice` -- 204, 낮거나 NULL 이면 현재 판·지금 시각 기록, 이미 동의했으면
  **행 변경 0**(처음 동의 시각이 남는다).
- 미동의 `POST /chat`·`POST /answers/{id}`·`POST /briefings/run` -> 403 `notice_required`, 의존 객체
  (제안기·판정기·임베더·생성기·알림기)를 아예 만들지 않는다 -> LLM·임베딩·푸시 0.
- 주기 브리핑은 미동의 계정(NULL·낮은 판)·`users` 행 없는 인물을 건너뛴다 -- 생성기 호출 0·발송 0·
  `briefed_at` NULL·그 계정 `briefing_run` trace 0.

실 PostgreSQL(`dbtest`)이 필요하다. 네트워크 0(가짜 제안기·판정기·임베더·생성기·발송기).
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

import app.auth.deps as auth_deps_module
import app.auth.routes as auth_routes_module
import app.briefing.scheduler as scheduler_module
import app.push.notifier as notifier_module
from app.agent.propose import FakeProposer
from app.api.deps import (
    get_briefing_composer,
    get_embedder,
    get_judge,
    get_notifier,
    get_proposer,
    get_session,
)
from app.auth.deps import get_auth_now
from app.briefing.compose import FakeBriefingComposer
from app.db.models import AgentTrace, ChatMessage, PendingQuestion, Person, PushSubscription
from app.db.models import Schedule, User
from app.er.judge import FakeJudge
from app.main import create_app
from app.push.types import FakePushSender
from app.settings import PRIVACY_NOTICE_VERSION
from tests.auth_helpers import logged_in_client, make_user
from tests.test_push_wiring import _generate_vapid_key_pair

pytestmark = pytest.mark.dbtest

PW = "test-only-pass-1234"
T0 = datetime(2026, 11, 22, 9, 0, 0, tzinfo=timezone.utc)
FIRST_ACCEPTED = datetime(2026, 11, 1, 12, 0, 0, tzinfo=timezone.utc)
NOTICE_REQUIRED_422 = {"detail": {"code": "notice_required"}}
NOTICE_REQUIRED_403 = {"detail": {"code": "notice_required"}}


@pytest.fixture(autouse=True)
def _default_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)
    for name in ("VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY", "VAPID_SUBJECT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture()
def app_(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_auth_now] = lambda: (lambda: T0)
    return app


@pytest.fixture()
def client(app_) -> TestClient:
    return TestClient(app_, base_url="https://testserver")


def _count(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model))


def _signup(client: TestClient, username: str = "noticeuser", **overrides):
    body = {
        "username": username,
        "password": PW,
        "nickname": username,
        "privacy_notice_accepted": True,
    }
    body.update(overrides)
    for key in [k for k, v in body.items() if v is _OMIT]:
        del body[key]
    return client.post("/auth/signup", json=body)


_OMIT = object()


def _unconsented_client(app_, db_session, user_id: str = "u-nc") -> TestClient:
    make_user(db_session, user_id, notice_accepted=False)
    return logged_in_client(app_, db_session, user_id)


# ---------------------------------------------------------------------------
# 판 번호
# ---------------------------------------------------------------------------


def test_notice_version_is_one() -> None:
    """판 번호 값 고정(계약 표) -- 문구를 바꾸는 커밋이 값을 올리면 이 시험이 같이 바뀐다."""
    assert PRIVACY_NOTICE_VERSION == 1


# ---------------------------------------------------------------------------
# 가입
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [_OMIT, False, None])
def test_signup_without_acceptance_is_422_notice_required_and_writes_no_user(
    client, db_session, value
) -> None:
    before = _count(db_session, User)

    resp = _signup(client, privacy_notice_accepted=value)

    assert resp.status_code == 422
    assert resp.json() == NOTICE_REQUIRED_422  # `detail` 이 목록이 아니라 dict(N-R7)
    assert _count(db_session, User) == before
    assert db_session.execute(select(User).where(User.username == "noticeuser")).first() is None


def test_signup_with_acceptance_records_version_and_time_and_not_required(
    client, db_session
) -> None:
    resp = _signup(client)

    assert resp.status_code == 201
    assert resp.json()["notice_required"] is False
    row = db_session.execute(select(User).where(User.username == "noticeuser")).scalar_one()
    assert row.privacy_notice_version == 1
    assert row.privacy_notice_accepted_at == T0  # 가입이 동의를 함께 기록(주입한 시계의 값)


def test_signup_check_order_format_then_notice_then_conflict(client, db_session) -> None:
    """형식 위반이 동의보다 먼저, 동의가 409 사전 조회보다 먼저(P3-R3)."""
    assert _signup(client, "firstowner").status_code == 201
    client.cookies.clear()

    # 형식이 틀리고 동의도 없음 -> 형식 오류가 이긴다
    bad_username = _signup(client, "x!", privacy_notice_accepted=False)
    assert bad_username.json() == {"detail": {"code": "invalid_username"}}
    bad_password = _signup(client, "secondone", password="short", privacy_notice_accepted=False)
    assert bad_password.json() == {"detail": {"code": "invalid_password"}}
    bad_nickname = _signup(client, "thirdone", nickname="   ", privacy_notice_accepted=False)
    assert bad_nickname.json() == {"detail": {"code": "invalid_nickname"}}

    # 형식은 맞고 동의가 없고 이미 있는 아이디 -> 409 가 아니라 422 notice_required
    taken = _signup(client, "firstowner", privacy_notice_accepted=False)
    assert taken.status_code == 422
    assert taken.json() == NOTICE_REQUIRED_422

    # 동의가 있으면 그제야 409
    conflict = _signup(client, "firstowner")
    assert conflict.status_code == 409
    assert conflict.json() == {"detail": {"code": "username_taken"}}


# ---------------------------------------------------------------------------
# /auth/me · 재고지 동의
# ---------------------------------------------------------------------------


def test_me_notice_required_is_true_for_null_and_lower_version_false_for_current(
    app_, db_session
) -> None:
    null_client = _unconsented_client(app_, db_session, "u-null")
    assert null_client.get("/auth/me").json()["notice_required"] is True

    lower = make_user(db_session, "u-lower")
    lower.privacy_notice_version = PRIVACY_NOTICE_VERSION - 1
    db_session.flush()
    assert logged_in_client(app_, db_session, "u-lower").get("/auth/me").json()[
        "notice_required"
    ] is True

    current = logged_in_client(app_, db_session, "u-current")  # `make_user` 기본 = 동의
    assert current.get("/auth/me").json()["notice_required"] is False


def test_login_response_carries_notice_required(app_, db_session, client) -> None:
    assert _signup(client, "loginnotice").status_code == 201
    client.cookies.clear()
    user = db_session.execute(select(User).where(User.username == "loginnotice")).scalar_one()
    user.privacy_notice_version = None  # 배포 전 가입자처럼
    db_session.flush()

    resp = client.post("/auth/login", json={"username": "loginnotice", "password": PW})

    assert resp.status_code == 200
    assert resp.json()["notice_required"] is True


def test_reaccept_null_account_flow_null_then_false_then_true_after_version_bump(
    app_, db_session, monkeypatch
) -> None:
    client = _unconsented_client(app_, db_session)
    assert client.get("/auth/me").json()["notice_required"] is True

    resp = client.post("/auth/privacy-notice")

    assert resp.status_code == 204
    assert resp.content == b""
    row = db_session.get(User, "u-nc")
    assert row.privacy_notice_version == 1
    assert row.privacy_notice_accepted_at == T0  # 주입한 시계의 지금 시각
    assert client.get("/auth/me").json()["notice_required"] is False

    # 판 번호를 올리면 같은 계정이 다시 미동의(문구 변경 -> 판 올림의 효과)
    monkeypatch.setattr(auth_deps_module, "PRIVACY_NOTICE_VERSION", 2)
    monkeypatch.setattr(auth_routes_module, "PRIVACY_NOTICE_VERSION", 2)
    assert client.get("/auth/me").json()["notice_required"] is True
    assert client.post("/auth/privacy-notice").status_code == 204
    db_session.refresh(row)
    assert row.privacy_notice_version == 2
    assert client.get("/auth/me").json()["notice_required"] is False


def test_reaccept_lower_version_overwrites_version_and_time(app_, db_session) -> None:
    user = make_user(db_session, "u-low", notice_accepted=False)
    user.privacy_notice_version = 0
    user.privacy_notice_accepted_at = FIRST_ACCEPTED
    db_session.flush()
    client = logged_in_client(app_, db_session, "u-low")

    assert client.post("/auth/privacy-notice").status_code == 204

    db_session.refresh(user)
    assert user.privacy_notice_version == 1
    assert user.privacy_notice_accepted_at == T0


def test_reaccept_on_current_version_is_204_and_changes_no_row(app_, db_session) -> None:
    user = make_user(db_session, "u-keep")
    user.privacy_notice_version = PRIVACY_NOTICE_VERSION
    user.privacy_notice_accepted_at = FIRST_ACCEPTED
    db_session.flush()
    client = logged_in_client(app_, db_session, "u-keep")

    resp = client.post("/auth/privacy-notice")

    assert resp.status_code == 204
    db_session.refresh(user)
    assert user.privacy_notice_version == PRIVACY_NOTICE_VERSION
    assert user.privacy_notice_accepted_at == FIRST_ACCEPTED  # 처음 동의 시각이 남는다(R-7 ⑨)


def test_privacy_notice_without_login_is_401(client, db_session) -> None:
    resp = client.post("/auth/privacy-notice")

    assert resp.status_code == 401
    assert resp.json() == {"detail": {"code": "unauthenticated"}}


# ---------------------------------------------------------------------------
# 미동의 403 -- LLM·임베딩·푸시 0
# ---------------------------------------------------------------------------


def _spy_overrides(app, resolved: list[str]) -> FakeBriefingComposer:
    """LLM·임베딩·푸시 쪽 의존성이 한 번이라도 만들어지면 `resolved` 에 이름이 남는다."""
    composer = FakeBriefingComposer()

    def _track(name: str, value):
        def _factory():
            resolved.append(name)
            return value

        return _factory

    app.dependency_overrides[get_proposer] = _track("proposer", FakeProposer(table={}))
    app.dependency_overrides[get_judge] = _track("judge", FakeJudge(table={}))
    app.dependency_overrides[get_embedder] = _track("embedder", lambda texts: [])
    app.dependency_overrides[get_briefing_composer] = _track("composer", composer)
    app.dependency_overrides[get_notifier] = _track("notifier", None)
    return composer


def test_unconsented_chat_is_403_and_touches_no_llm_no_rows(app_, db_session) -> None:
    client = _unconsented_client(app_, db_session)
    resolved: list[str] = []
    _spy_overrides(app_, resolved)
    traces = _count(db_session, AgentTrace)
    messages = _count(db_session, ChatMessage)

    resp = client.post("/chat", json={"utterance": "김 대리랑 점심 먹었어"})

    assert resp.status_code == 403
    assert resp.json() == NOTICE_REQUIRED_403
    assert resolved == []  # 제안기·판정기·임베더를 만들지도 않았다
    assert _count(db_session, AgentTrace) == traces
    assert _count(db_session, ChatMessage) == messages  # 대화 기록도 쓰지 않았다


def test_unconsented_briefings_run_is_403_and_composes_nothing(app_, db_session) -> None:
    client = _unconsented_client(app_, db_session)
    person = Person(user_id="u-nc", display_name="민수", relation_tag="친구", hierarchy="동")
    db_session.add(person)
    db_session.flush()
    schedule = Schedule(
        person_id=person.id, title="저녁 약속", scheduled_at=datetime.now(timezone.utc) + timedelta(hours=3)
    )
    db_session.add(schedule)
    db_session.flush()
    resolved: list[str] = []
    composer = _spy_overrides(app_, resolved)
    traces = _count(db_session, AgentTrace)

    resp = client.post("/briefings/run", json={})

    assert resp.status_code == 403
    assert resp.json() == NOTICE_REQUIRED_403
    assert composer.call_count == 0
    assert resolved == []
    db_session.refresh(schedule)
    assert schedule.briefed_at is None
    assert _count(db_session, AgentTrace) == traces


def test_unconsented_answers_is_403_then_200_after_notice_accepted(
    app_, db_session, fake_embedder
) -> None:
    """동의 계정이 만든 칩(`new_person`) -> 그 뒤 미동의로 돌아간 계정의 답은 403·질문 그대로 ->
    재고지 동의 뒤 같은 칩 답 200(미만료 칩은 살아 있다)."""
    client = _unconsented_client(app_, db_session)
    assert client.post("/auth/privacy-notice").status_code == 204  # 처음엔 동의한 계정
    utterance = "오늘 새사람이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "새사람",
                "type": "meal",
                "content": "저녁",
                "occurred_at": T0.isoformat(),
            },
        }
    ]
    app_.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app_.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    app_.dependency_overrides[get_embedder] = lambda: fake_embedder
    chat = client.post("/chat", json={"utterance": utterance})
    assert chat.status_code == 200
    question = chat.json()["pending_question"]
    assert question["kind"] == "new_person"
    question_id = question["question_id"]
    answer = "친구로 기억할게요"
    assert answer in question["options"]

    # 고지 판이 올라간 것처럼 다시 미동의 상태로
    user = db_session.get(User, "u-nc")
    user.privacy_notice_version = None
    user.privacy_notice_accepted_at = None
    db_session.flush()
    resolved: list[str] = []
    _spy_overrides(app_, resolved)
    persons = _count(db_session, Person)

    blocked = client.post(f"/answers/{question_id}", json={"answer": answer})

    assert blocked.status_code == 403
    assert blocked.json() == NOTICE_REQUIRED_403
    assert resolved == []
    stored = db_session.get(PendingQuestion, question_id)
    db_session.refresh(stored)
    assert stored.answer is None and stored.answered_at is None  # 질문은 그대로 떠 있다
    assert _count(db_session, Person) == persons

    assert client.post("/auth/privacy-notice").status_code == 204
    app_.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app_.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    app_.dependency_overrides[get_embedder] = lambda: fake_embedder
    resumed = client.post(f"/answers/{question_id}", json={"answer": answer})

    assert resumed.status_code == 200
    assert resumed.json()["status"] == "answered"
    db_session.refresh(stored)
    assert stored.answer == answer
    assert _count(db_session, Person) == persons + 1


def test_consented_user_still_passes_the_notice_gate(app_, db_session) -> None:
    """403 시험이 헛돌지 않게 -- 같은 호출이 동의 계정에서는 403 이 아니다."""
    client = logged_in_client(app_, db_session, "u-ok")
    utterance = "그냥 안부 인사"
    app_.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: []})
    app_.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    app_.dependency_overrides[get_embedder] = lambda: (lambda texts: [])

    resp = client.post("/chat", json={"utterance": utterance})

    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 주기 브리핑 건너뜀 (VR7)
# ---------------------------------------------------------------------------


@contextmanager
def _same_session(db):
    yield db


@pytest.fixture()
def sched(db_session, monkeypatch):
    """`default_run_once` 가 롤백 세션·가짜 생성기·가짜 발송기로 돈다."""
    composer = FakeBriefingComposer()
    sender = FakePushSender()
    public_key, private_key = _generate_vapid_key_pair()
    monkeypatch.setenv("VAPID_PUBLIC_KEY", public_key)
    monkeypatch.setenv("VAPID_PRIVATE_KEY", private_key)
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:u4-notice@example.com")
    monkeypatch.setattr(notifier_module, "PyWebPushSender", lambda: sender)
    monkeypatch.setattr(scheduler_module, "session_scope", lambda: _same_session(db_session))
    monkeypatch.setattr(scheduler_module, "composer_from_env", lambda: composer)
    return db_session, composer, sender


def _clock() -> datetime:
    return T0


def _owner_with_schedule(db, user_id: str, *, user_row: bool, notice: str) -> Schedule:
    """`notice` = `current`(동의) | `null`(미동의) | `lower`(낮은 판). `user_row=False` 면 `users` 행 없음."""
    if user_row:
        user = make_user(db, user_id, notice_accepted=(notice == "current"))
        if notice == "lower":
            user.privacy_notice_version = PRIVACY_NOTICE_VERSION - 1
            user.privacy_notice_accepted_at = FIRST_ACCEPTED
    person = Person(user_id=user_id, display_name=f"{user_id}-p", relation_tag="친구", hierarchy="동")
    db.add(person)
    db.flush()
    schedule = Schedule(person_id=person.id, title="약속", scheduled_at=T0 + timedelta(hours=3))
    db.add(schedule)
    db.add(
        PushSubscription(
            user_id=user_id, endpoint=f"https://push.test/{user_id}", keys={"p256dh": "p", "auth": "a"}
        )
    )
    db.flush()
    return schedule


def _briefing_runs(db) -> list[AgentTrace]:
    return list(
        db.execute(select(AgentTrace).where(AgentTrace.step == "briefing_run")).scalars()
    )


@pytest.mark.parametrize(
    ("user_row", "notice"),
    [(True, "null"), (True, "lower"), (False, "current")],
    ids=["notice-null", "notice-lower-version", "no-users-row"],
)
def test_scheduler_skips_unconsented_account_entirely(sched, user_row, notice) -> None:
    db, composer, sender = sched
    schedule = _owner_with_schedule(db, "u-skip", user_row=user_row, notice=notice)
    before = len(_briefing_runs(db))

    scheduler_module.default_run_once(now=_clock)

    db.refresh(schedule)
    assert schedule.briefed_at is None  # 브리핑되지 않았다
    assert composer.call_count == 0  # LLM 0
    assert sender.calls == []  # 푸시 0
    runs = _briefing_runs(db)[before:]
    # 대상이 0명이라 표식 ctx 한 번뿐이고, 그 trace 는 어떤 일정도 고르지 않았다 -- 그 계정 trace 0
    assert len(runs) == 1
    assert runs[0].output["selected"] == []
    assert runs[0].output["briefed"] == []


def test_scheduler_briefs_only_consented_account_in_a_mixed_run(sched) -> None:
    db, composer, sender = sched
    consented = _owner_with_schedule(db, "u-yes", user_row=True, notice="current")
    skipped = _owner_with_schedule(db, "u-no", user_row=True, notice="null")
    before = len(_briefing_runs(db))

    scheduler_module.default_run_once(now=_clock)

    db.refresh(consented)
    db.refresh(skipped)
    assert consented.briefed_at is not None
    assert skipped.briefed_at is None
    assert composer.call_count == 1  # 동의 계정 일정 1건만 생성
    assert [call["endpoint"] for call in sender.calls] == ["https://push.test/u-yes"]
    runs = _briefing_runs(db)[before:]
    assert len(runs) == 1  # 동의한 한 계정의 실행 trace 만(건너뛴 계정 0)
    assert runs[0].output["selected"] == [consented.id]
