"""Refs: P5-loop U7 R6 R7 D1 D2 S3.4 원칙1 원칙9 -- `POST /answers/{question_id}`
뒤 절반(재개) HTTP 테스트.

`TestClient(create_app())` + `app.dependency_overrides[get_session]`(U1
롤백 픽스처 `db_session` 주입, P2 결정 13)로 DB 에 행을 남기지 않는다.
인식 단계는 `get_proposer` 로 `FakeProposer`(네트워크 0), 판정 단계는
`get_judge` 로 `FakeJudge`(P3-er, 네트워크 0)를 주입한다 -- `app_and_client`
픽스처가 `get_embedder` 도 `fake_embedder` 로 기본 오버라이드한다
(`tests/test_api_chat.py` 와 같은 관례, R-15).

시나리오는 두 갈래로 나눈다: (1) `POST /chat` 으로 실제 되묻기를 먼저
만든 뒤 `POST /answers/{id}` 로 재개하는 왕복(신뢰의 뿌리) -- identity/
new_person 답 테스트가 이 경로다. (2) `schedule` 질문은 재개 재료의
정확한 모양(`resume.schedule`·`resume.schedule_options`)만 있으면 되므로
낮은 층에서 `ask_user()` 로 직접 만들어 답만 검증한다(U5 가 이미 그
모양을 만든다는 것은 `tests/test_agent_loop.py` 가 확인했다 -- 여기서는
그 모양을 받은 재개가 옳게 동작하는지만 본다, 중복 구현 금지).

각 테스트는 먼저 **원하는 경로를 실제로 탔는지**(질문의 `kind`, 되묻기
발생 여부)를 단언한 뒤에 재개 결과를 확인한다(U6 "헛돎" 교훈 -- 임베더가
빠져 merge 로 새는 바람에 테스트 조건이 만들어지지 않았던 사고를
반복하지 않는다).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.agent.propose import FakeProposer
from app.agent.types import (
    NEW_PERSON_TAG_OPTIONS,
    SCHEDULE_UNKNOWN_OPTION,
    PendingCall,
    PendingResume,
    ScheduleResumeRef,
)
from app.api.deps import get_embedder, get_judge, get_proposer, get_session
from app.db.models import ALIAS_SOURCES, Event, PendingQuestion, Person, PersonAlias, Schedule
from app.er.judge import FakeJudge
from app.main import create_app
from app.tools.context import ToolContext
from app.tools.questions import ask_user

dbtest = pytest.mark.dbtest
pytestmark = dbtest

NOW = datetime(2026, 9, 25, 19, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 픽스처 · 보조 함수 (tests/test_api_chat.py 와 같은 모양)
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session, fake_embedder):
    """U1 롤백 세션을 `get_session` 자리에 주입한 `(app, client)` 쌍(P2
    결정 13). `get_embedder` 도 `fake_embedder` 로 기본 오버라이드한다
    (U6 추가 수정과 같은 이유 -- 재개도 `create_person`/`update_person(
    new_alias=…)` 로 별칭을 만든다, R-15)."""
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


def _count(session, model) -> int:
    return len(session.execute(select(model)).scalars().all())


def _start_new_person_question(
    app, client, *, mention: str, session_id: str
) -> tuple[int, list[str]]:
    """`POST /chat` 으로 `new_person` 되묻기를 실제로 만든다(별칭이 전혀
    없는 새 언급 -- `no_candidates` 로 곧장 `new_person`). 반환값은
    `(question_id, options)`. 원하는 경로를 실제로 탔는지 이 함수 자신이
    먼저 단언한다(헛돎 방지)."""
    utterance = f"오늘 {mention}이랑 저녁 먹었어"
    calls = [
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
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})

    resp = client.post("/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["pending_question"] is not None
    assert body["pending_question"]["kind"] == "new_person"
    return body["pending_question"]["question_id"], body["pending_question"]["options"]


def _make_schedule_question(
    db_session, ctx: ToolContext, *, person: Person, title: str = "약속"
) -> tuple[int, dict[str, str]]:
    """`_ask_schedule`(U5)이 만드는 것과 같은 모양의 `schedule` 질문을
    낮은 층에서 직접 만든다(`resume.schedule`·`resume.schedule_options`
    가 정확한 모양인지는 `tests/test_agent_loop.py` 가 이미 확인했다 --
    여기서는 그 모양을 받은 U7 재개만 검증한다, 중복 구현 금지). 반환값은
    `(question_id, {옵션 문자열: ISO 시각})`(`모르겠어요` 제외)."""
    label1, iso1 = "10월 2일 저녁 7시", "2026-10-02T19:00:00+09:00"
    label2, iso2 = "10월 3일 저녁 7시", "2026-10-03T19:00:00+09:00"
    resume = PendingResume(
        pending_calls=[
            PendingCall(index=0, name="add_schedule", args={"person": "팀장", "title": title})
        ],
        schedule=ScheduleResumeRef(person_id=person.id, title=title, call_index=0),
        schedule_options={label1: iso1, label2: iso2},
    )
    asked = ask_user(
        ctx,
        kind="schedule",
        question=f"'{title}' 약속, 언제로 기억할까요?",
        options=[label1, label2, SCHEDULE_UNKNOWN_OPTION],
        context={"utterance": f"{title} 잡기로 했어", "resume": resume.to_dict()},
    )
    db_session.flush()
    return asked.question_id, {label1: iso1, label2: iso2}


# ---------------------------------------------------------------------------
# 왕복 2요청 end-to-end + 태그 답 (요구 목록 1·5)
# ---------------------------------------------------------------------------


def test_answers_resume_round_trip_creates_person_and_stores_event(
    app_and_client, db_session, fake_embedder
):
    """`POST /chat` -> `new_person` 되묻기 -> `POST /answers/{id}` 한 왕복
    안에서 인물이 만들어지고 보류돼 있던 이벤트가 저장된다."""
    app, client = app_and_client
    question_id, options = _start_new_person_question(
        app, client, mention="민수", session_id="resume-roundtrip"
    )
    tag_answer = "친구로 기억할게요"
    assert tag_answer in options

    resp = client.post(f"/answers/{question_id}", json={"answer": tag_answer})

    assert resp.status_code == 200
    body = resp.json()
    assert body["question_id"] == question_id
    assert body["status"] == "answered"
    assert body["stored"] == {"persons": 1, "events": 1, "schedules": 0}
    assert body["pending_question"] is None
    assert body["stop_reason"] is None
    assert body["reply"]

    person = db_session.execute(select(Person).where(Person.display_name == "민수")).scalar_one()
    assert person.relation_tag == "친구"
    assert person.hierarchy == "동"

    event = db_session.execute(select(Event).where(Event.person_id == person.id)).scalar_one()
    assert event.type == "meal"


def test_answers_resume_new_person_tag_answer_sets_relation_tag(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    question_id, _ = _start_new_person_question(
        app, client, mention="이모부", session_id="resume-tag-family"
    )

    resp = client.post(f"/answers/{question_id}", json={"answer": "가족으로 기억할게요"})

    assert resp.status_code == 200
    person = db_session.execute(
        select(Person).where(Person.display_name == "이모부")
    ).scalar_one()
    assert person.relation_tag == "가족"


# ---------------------------------------------------------------------------
# 같은 질문 재개 두 번째 409 (결정 J)
# ---------------------------------------------------------------------------


def test_answers_resume_second_submission_returns_409(app_and_client, db_session, fake_embedder):
    app, client = app_and_client
    question_id, options = _start_new_person_question(
        app, client, mention="수진", session_id="resume-409-twice"
    )
    tag_answer = options[0]
    assert tag_answer in NEW_PERSON_TAG_OPTIONS

    resp1 = client.post(f"/answers/{question_id}", json={"answer": tag_answer})
    assert resp1.status_code == 200

    resp2 = client.post(f"/answers/{question_id}", json={"answer": tag_answer})
    assert resp2.status_code == 409
    assert resp2.json()["detail"]["code"] == "already_answered"


# ---------------------------------------------------------------------------
# context 밖 이름으로는 create_person 이 일어나지 않는다
# ---------------------------------------------------------------------------


def test_answers_resume_create_person_only_targets_context_mention(
    app_and_client, db_session, fake_embedder, monkeypatch: pytest.MonkeyPatch
):
    """`create_person` 스파이가 실제로 불린 인자를 기록한다 -- 답
    문자열(태그 선택지)이 아니라 **`context["mention"]`** 하나만 대상이
    된다는 것을 직접 확인한다(판정 표 5a 의 실행판)."""
    app, client = app_and_client
    question_id, _ = _start_new_person_question(
        app, client, mention="민수", session_id="resume-spy"
    )

    import app.agent.loop as loop_module

    real_create_person = loop_module.app_tools.create_person
    calls_seen: list[tuple[tuple, dict]] = []

    def _spy(ctx, *args, **kwargs):
        calls_seen.append((args, kwargs))
        return real_create_person(ctx, *args, **kwargs)

    monkeypatch.setattr(loop_module.app_tools, "create_person", _spy)

    resp = client.post(f"/answers/{question_id}", json={"answer": "친구로 기억할게요"})

    assert resp.status_code == 200
    assert len(calls_seen) == 1
    _, kwargs = calls_seen[0]
    assert kwargs["display_name"] == "민수"
    assert kwargs["aliases"] == ["민수"]


# ---------------------------------------------------------------------------
# new_person 부정 답이면 create_person 0회 (판정 표 28행)
# ---------------------------------------------------------------------------


def test_answers_resume_new_person_reject_creates_nothing(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    question_id, options = _start_new_person_question(
        app, client, mention="정훈", session_id="resume-reject"
    )
    assert "아니요" in options

    persons_before = _count(db_session, Person)
    events_before = _count(db_session, Event)

    resp = client.post(f"/answers/{question_id}", json={"answer": "아니요"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"] == {"persons": 0, "events": 0, "schedules": 0}
    assert body["pending_question"] is None

    assert _count(db_session, Person) == persons_before
    assert _count(db_session, Event) == events_before


# ---------------------------------------------------------------------------
# 만료 답 거부
# ---------------------------------------------------------------------------


def test_answers_resume_expired_question_returns_409(app_and_client, db_session):
    app, client = app_and_client
    session_id = "resume-expired"
    ctx = ToolContext(session=db_session, session_id=session_id)
    asked = ask_user(
        ctx,
        kind="schedule",
        question="언제로 기억할까요?",
        options=["내일 저녁 7시", SCHEDULE_UNKNOWN_OPTION],
        context={},
    )
    row = db_session.get(PendingQuestion, asked.question_id)
    row.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db_session.flush()

    resp = client.post(f"/answers/{asked.question_id}", json={"answer": "내일 저녁 7시"})

    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "expired"


# ---------------------------------------------------------------------------
# 재개 중 두 번째 언급이 되묻기 -> 새 question_id, 첫 질문은 answered 유지
# ---------------------------------------------------------------------------


def test_answers_resume_second_mention_asks_new_question_first_stays_answered(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    session_id = "resume-chain-identity-newperson"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    utterance = "팀장이랑 저녁 먹고 이모한테도 전화했어"
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
                "person": "이모",
                "type": "other",
                "content": "전화",
                "occurred_at": NOW.isoformat(),
            },
        },
    ]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})

    resp1 = client.post("/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id})
    assert resp1.status_code == 200
    body1 = resp1.json()
    # 원하는 경로를 실제로 탔는지 먼저 확인한다(헛돎 방지) -- identity 되묻기.
    assert body1["pending_question"]["kind"] == "identity"
    q1 = body1["pending_question"]["question_id"]
    assert "김민수" in body1["pending_question"]["options"]

    resp2 = client.post(f"/answers/{q1}", json={"answer": "김민수"})

    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["pending_question"] is not None
    assert body2["pending_question"]["kind"] == "new_person"
    q2 = body2["pending_question"]["question_id"]
    assert q2 != q1
    # 팀장(확정된 언급)의 이벤트는 이 재개 안에서 바로 실행됐다.
    assert body2["stored"]["events"] == 1

    row1 = db_session.get(PendingQuestion, q1)
    assert row1.answered_at is not None
    assert row1.answer == "김민수"

    row2 = db_session.get(PendingQuestion, q2)
    assert row2.answered_at is None


# ---------------------------------------------------------------------------
# identity 답 뒤 schedule 질문
# ---------------------------------------------------------------------------


def test_answers_resume_identity_answer_leads_to_schedule_question(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    session_id = "resume-chain-identity-schedule"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])

    utterance = "팀장이랑 다음에 약속 잡기로 했어"
    calls = [{"name": "add_schedule", "args": {"person": "팀장", "title": "약속"}}]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})

    resp1 = client.post("/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id})
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert body1["pending_question"]["kind"] == "identity"
    q1 = body1["pending_question"]["question_id"]

    resp2 = client.post(f"/answers/{q1}", json={"answer": "김민수"})

    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["pending_question"] is not None
    assert body2["pending_question"]["kind"] == "schedule"
    assert SCHEDULE_UNKNOWN_OPTION in body2["pending_question"]["options"]
    assert body2["stored"]["schedules"] == 0

    row1 = db_session.get(PendingQuestion, q1)
    assert row1.answered_at is not None

    assert _count(db_session, Schedule) == 0


# ---------------------------------------------------------------------------
# schedule 답이면 사전 조회한 시각으로 저장, "모르겠어요"면 0회
# ---------------------------------------------------------------------------


def test_answers_resume_schedule_answer_stores_scheduled_time(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    person = _make_person(db_session, display_name="김민수")
    ctx = ToolContext(session=db_session, session_id="resume-schedule-answer", embedder=fake_embedder)
    question_id, options_map = _make_schedule_question(db_session, ctx, person=person)
    label, iso = next(iter(options_map.items()))

    resp = client.post(f"/answers/{question_id}", json={"answer": label})

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"]["schedules"] == 1
    assert body["pending_question"] is None

    schedule = db_session.execute(
        select(Schedule).where(Schedule.person_id == person.id)
    ).scalar_one()
    # Postgres timestamptz 는 UTC 로 정규화해 돌려주므로(오프셋 표기가
    # 달라진다) 문자열이 아니라 같은 시각인지(datetime 동등 비교)로 본다.
    assert schedule.scheduled_at == datetime.fromisoformat(iso)
    assert schedule.title == "약속"


def test_answers_resume_schedule_unknown_answer_stores_nothing(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    person = _make_person(db_session, display_name="박서준")
    ctx = ToolContext(
        session=db_session, session_id="resume-schedule-unknown", embedder=fake_embedder
    )
    question_id, _ = _make_schedule_question(db_session, ctx, person=person)

    resp = client.post(f"/answers/{question_id}", json={"answer": SCHEDULE_UNKNOWN_OPTION})

    assert resp.status_code == 200
    body = resp.json()
    assert body["stored"]["schedules"] == 0
    assert body["pending_question"] is None

    schedules = db_session.execute(
        select(Schedule).where(Schedule.person_id == person.id)
    ).scalars().all()
    assert schedules == []


# ---------------------------------------------------------------------------
# 재개로 만든 별칭에 임베딩이 채워진다 (R-15, 판정 표 27행)
# ---------------------------------------------------------------------------


def test_answers_resume_new_person_alias_embedding(app_and_client, db_session, fake_embedder):
    app, client = app_and_client
    question_id, _ = _start_new_person_question(
        app, client, mention="채원", session_id="resume-alias-embedding"
    )

    resp = client.post(f"/answers/{question_id}", json={"answer": "친구로 기억할게요"})
    assert resp.status_code == 200

    person = db_session.execute(select(Person).where(Person.display_name == "채원")).scalar_one()
    aliases = (
        db_session.execute(select(PersonAlias).where(PersonAlias.person_id == person.id))
        .scalars()
        .all()
    )
    assert aliases
    assert all(alias.embedding is not None for alias in aliases)
