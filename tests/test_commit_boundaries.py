"""Refs: FIX-023 P5-loop P6-briefing 원칙8 원칙9 -- 실제 커밋 경계 테스트.

테스트 1809개의 대부분은 `db_session`(세이브포인트 안에서 돌고 끝나면
롤백, FIX-006)으로 돈다. 이 파일은 그 대신 **요청이 끝났을 때 DB 에
실제로 무엇이 남고 무엇이 사라지는지**를 확인한다 -- `get_session` 을
오버라이드하지 않고 운영 경로 그대로(요청마다 새 커넥션/트랜잭션) 돌린
뒤, **요청이 끝난 뒤 새 `Session`**(별도 커넥션)으로 결과를 조회한다.
LLM·임베딩은 가짜(`FakeProposer`/`FakeJudge`/`fake_embedder`)로 네트워크
0 이다(원칙8).

각 테스트는 고유한 `user_id`/`session_id`(`uuid4` 접미사)로 자신의 행만
만들고, 끝에서 try/finally 로 **그 테스트가 만든 행만** 지운다(FIX-019
교훈 -- 테이블 전체 삭제·TRUNCATE 금지, `tests/test_answer_concurrency.py`
와 같은 관례).

1b 는 **알려진 한계**(P5-loop 01-plan 결정 H)를 고정한다 -- 기록 단계의
`SQLAlchemyError` 는 라우트가 삼키지 않고 그대로 올려 `get_session()` 의
`rollback()` 을 타게 하므로(`PendingRollbackError` 회피), 그 요청이 쓴
`loop_error` trace 조차 함께 사라진다. 이것은 원칙9("판정 근거를 남긴다")
의 예외이자 결정 H 가 받아들인 트레이드오프다 -- 바뀌면(예: 별도
커넥션으로 오류 trace 를 항상 남기기로 재결정하면) 이 테스트를
의도적으로 고친다.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import app.agent.loop as loop_module
from app.agent.propose import FakeProposer
from app.api.deps import get_embedder, get_judge, get_proposer
from app.briefing.run import run_briefings
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    ComposedBriefing,
)
from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    Event,
    PendingQuestion,
    Person,
    PersonAlias,
    Schedule,
)
from app.db.session import session_scope
from app.er.judge import FakeJudge
from app.main import create_app
from app.tools.context import ToolContext

pytestmark = pytest.mark.dbtest

_NOW = datetime(2026, 10, 6, 9, 0, 0, tzinfo=timezone.utc)


def _unique(prefix: str) -> str:
    return f"fix023-{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# 1a -- POST /chat 정상, 새 커넥션으로 인물·사건·trace 확인
# ---------------------------------------------------------------------------


def test_chat_real_commit_persists_event_and_trace(db_engine, fake_embedder, monkeypatch) -> None:
    """`get_session` 을 오버라이드하지 않고(운영 경로 그대로, 요청마다
    새 커넥션) `POST /chat` 한 건을 보낸 뒤, **요청이 끝난 뒤 새
    `Session`** 으로 이벤트·trace 행이 실제로 남았는지 확인한다(FIX-023
    수정안 1a)."""
    user_id = _unique("chat-ok")
    session_id = _unique("chat-ok-session")
    monkeypatch.setenv("APP_USER_ID", user_id)

    setup_session = Session(bind=db_engine)
    try:
        person = Person(
            user_id=user_id, display_name="김민수", relation_tag="직장", hierarchy="동"
        )
        setup_session.add(person)
        setup_session.flush()
        setup_session.add(
            PersonAlias(
                person_id=person.id,
                alias="팀장",
                source=ALIAS_SOURCES[0],
                embedding=fake_embedder(["팀장"])[0],
            )
        )
        setup_session.commit()
        person_id = person.id
    finally:
        setup_session.close()

    try:
        app = create_app()
        app.dependency_overrides[get_embedder] = lambda: fake_embedder
        utterance = "어제 팀장이랑 저녁 먹었어"
        calls = [
            {
                "name": "add_event",
                "args": {
                    "person": "팀장",
                    "type": "meal",
                    "content": "저녁",
                    "occurred_at": _NOW.isoformat(),
                },
            }
        ]
        app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
        app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person_id: 0.95})
        client = TestClient(app)

        resp = client.post(
            "/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["stored"] == {"persons": 0, "events": 1, "schedules": 0}

        # 핵심 확인 -- 이 요청을 처리한 세션과는 다른 새 커넥션으로 조회한다.
        check = Session(bind=db_engine)
        try:
            event = check.execute(
                select(Event).where(Event.person_id == person_id)
            ).scalar_one()
            assert event.raw_utterance == utterance
            assert event.type == "meal"

            trace_rows = (
                check.execute(select(AgentTrace).where(AgentTrace.session_id == session_id))
                .scalars()
                .all()
            )
            steps = {row.step for row in trace_rows}
            assert "loop_record" in steps
            assert len(trace_rows) > 0
        finally:
            check.close()
    finally:
        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(Event).where(Event.person_id == person_id))
            cleanup.execute(delete(PersonAlias).where(PersonAlias.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.execute(delete(AgentTrace).where(AgentTrace.session_id == session_id))
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 1b -- 기록 단계 DB 오류 주입: 그 요청이 쓴 행 0, trace 도 0(알려진 한계)
# ---------------------------------------------------------------------------


def test_chat_db_error_during_record_commits_nothing_and_leaves_no_trace(
    db_engine, fake_embedder, monkeypatch
) -> None:
    """기록 단계(`add_event` 실행)에서 실제 `SQLAlchemyError` 가 나면, 그
    요청이 쓴 행은 0 이고 `loop_error` trace 조차 남지 않는다 -- **알려진
    한계(결정 H)**, 바뀌면 이 테스트를 의도적으로 고친다.

    원인: `POST /chat` 은 `LoopError`/`JudgeUnavailable`/`ToolError` 만
    잡고 `SQLAlchemyError` 는 잡지 않고 그대로 올려 `get_session()` 의
    `rollback()` 을 타게 한다(`PendingRollbackError` 회피, 결정 H). 그
    결과 이 요청이 `begin_nested()` 세이브포인트 안에서 flush 한 모든
    행(업무 데이터는 물론 `tool_error`/`loop_*` 중간 trace 까지)이 함께
    사라지고, 라우트의 `_record_loop_error()` 자체가 호출되지 않으므로
    `loop_error` 행도 생기지 않는다."""
    user_id = _unique("chat-dberr")
    session_id = _unique("chat-dberr-session")
    monkeypatch.setenv("APP_USER_ID", user_id)

    setup_session = Session(bind=db_engine)
    try:
        person = Person(
            user_id=user_id, display_name="박서준", relation_tag="직장", hierarchy="동"
        )
        setup_session.add(person)
        setup_session.flush()
        setup_session.add(
            PersonAlias(
                person_id=person.id,
                alias="팀장",
                source=ALIAS_SOURCES[0],
                embedding=fake_embedder(["팀장"])[0],
            )
        )
        setup_session.commit()
        person_id = person.id
    finally:
        setup_session.close()

    def _raise_db_error(
        ctx: object,
        person_id: int,
        type: str,  # noqa: A002 -- 실제 `add_event` 시그니처 이름 그대로
        content: str,
        occurred_at: object,
        raw_utterance: str,
    ) -> None:
        # 게이트(U3)가 `inspect.signature(app_tools.add_event)` 로 인자
        # 스키마를 대조한다(③, `app/agent/gate.py::_arg_spec`) -- `app_tools`
        # 는 `app.agent.gate`/`app.agent.loop` 가 공유하는 **같은**
        # `app.tools` 모듈 객체이므로, `(*args, **kwargs)` 로 바꿔치면 그
        # 즉시 게이트가 이 제안을 "미지 인자"(`bad_args`)로 거부해 애초에
        # 기록 단계에 닿지도 못한다(헛돎). 그래서 실제 시그니처와 같은
        # 이름으로 선언해 게이트 통과는 그대로 두고 실행만 실패시킨다.
        raise SQLAlchemyError("simulated-fix023-record-failure")

    monkeypatch.setattr(loop_module.app_tools, "add_event", _raise_db_error)

    try:
        app = create_app()
        app.dependency_overrides[get_embedder] = lambda: fake_embedder
        utterance = "어제 팀장이랑 저녁 먹었어"
        calls = [
            {
                "name": "add_event",
                "args": {
                    "person": "팀장",
                    "type": "meal",
                    "content": "저녁",
                    "occurred_at": _NOW.isoformat(),
                },
            }
        ]
        app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
        app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person_id: 0.95})
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.post(
            "/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id}
        )

        assert resp.status_code == 500
        assert resp.json() == {"detail": {"code": "internal_error"}}
        assert "simulated-fix023-record-failure" not in resp.text

        check = Session(bind=db_engine)
        try:
            events = (
                check.execute(select(Event).where(Event.person_id == person_id))
                .scalars()
                .all()
            )
            assert events == []

            trace_rows = (
                check.execute(select(AgentTrace).where(AgentTrace.session_id == session_id))
                .scalars()
                .all()
            )
            # 알려진 한계(결정 H) -- 이 요청의 trace 는 0 행이다(docstring 참고).
            assert trace_rows == []
        finally:
            check.close()
    finally:
        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(Event).where(Event.person_id == person_id))
            cleanup.execute(delete(PersonAlias).where(PersonAlias.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            cleanup.execute(delete(AgentTrace).where(AgentTrace.session_id == session_id))
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 1c -- POST /answers/{id} 재개: 답과 재개 결과가 함께 커밋
# ---------------------------------------------------------------------------


def test_answers_resume_real_commit_persists_answer_and_resume_result(
    db_engine, fake_embedder, monkeypatch
) -> None:
    """`POST /chat` → `new_person` 되묻기 → `POST /answers/{id}` 재개를
    `get_session` 오버라이드 없이(운영 경로 그대로) 돌린 뒤, **새
    `Session`** 으로 답(`answered_at`)과 재개 결과(인물·이벤트)가 함께
    커밋됐는지 확인한다(FIX-023 수정안 1c)."""
    user_id = _unique("resume-ok")
    session_id = _unique("resume-ok-session")
    monkeypatch.setenv("APP_USER_ID", user_id)

    app = create_app()
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    utterance = "오늘 민수랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "민수",
                "type": "meal",
                "content": "저녁",
                "occurred_at": _NOW.isoformat(),
            },
        }
    ]
    app.dependency_overrides[get_proposer] = lambda: FakeProposer(table={utterance: calls})
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={})
    client = TestClient(app)

    person_id: int | None = None
    question_id: int | None = None
    try:
        resp1 = client.post(
            "/chat", json={"utterance": utterance}, headers={"X-Session-Id": session_id}
        )
        assert resp1.status_code == 200
        body1 = resp1.json()
        assert body1["pending_question"] is not None
        assert body1["pending_question"]["kind"] == "new_person"
        question_id = body1["pending_question"]["question_id"]
        tag_answer = "친구로 기억할게요"
        assert tag_answer in body1["pending_question"]["options"]

        resp2 = client.post(f"/answers/{question_id}", json={"answer": tag_answer})
        assert resp2.status_code == 200
        body2 = resp2.json()
        assert body2["status"] == "answered"
        assert body2["stored"] == {"persons": 1, "events": 1, "schedules": 0}

        check = Session(bind=db_engine)
        try:
            question = check.get(PendingQuestion, question_id)
            assert question is not None
            assert question.answered_at is not None
            assert question.answer == tag_answer

            person = check.execute(
                select(Person)
                .where(Person.user_id == user_id)
                .where(Person.display_name == "민수")
            ).scalar_one()
            person_id = person.id
            assert person.relation_tag == "친구"

            event = check.execute(
                select(Event).where(Event.person_id == person.id)
            ).scalar_one()
            assert event.raw_utterance == utterance
        finally:
            check.close()
    finally:
        cleanup = Session(bind=db_engine)
        try:
            if person_id is not None:
                cleanup.execute(delete(Event).where(Event.person_id == person_id))
                cleanup.execute(delete(PersonAlias).where(PersonAlias.person_id == person_id))
                cleanup.execute(delete(Person).where(Person.id == person_id))
            if question_id is not None:
                cleanup.execute(
                    delete(PendingQuestion).where(PendingQuestion.id == question_id)
                )
            cleanup.execute(delete(AgentTrace).where(AgentTrace.session_id == session_id))
            cleanup.commit()
        finally:
            cleanup.close()


# ---------------------------------------------------------------------------
# 1d -- run_briefings 실제 session_scope: 일정 단위 격리 real commit 확인
# ---------------------------------------------------------------------------


class _ScriptedBriefingComposer:
    """일정 id -> `ComposedBriefing` 또는 예외를 미리 정해 두는 테스트 전용
    `BriefingComposer`(`tests/test_briefing_run.py::_ScriptedComposer` 와
    같은 모양 -- 이 파일은 실제 `session_scope()` real commit 경계만
    확인하는 것이 목적이라 가장 단순한 형태로 다시 정의한다, 중복
    구현이 아니라 이 파일만의 작은 더블)."""

    def __init__(
        self, *, responses: dict[int, ComposedBriefing], fail_for: frozenset[int]
    ) -> None:
        self.responses = responses
        self.fail_for = fail_for

    def compose(self, briefing_input: object) -> ComposedBriefing:
        schedule_id = briefing_input.schedule_id  # type: ignore[attr-defined]
        if schedule_id in self.fail_for:
            raise RuntimeError("simulated-fix023-compose-failure")
        return self.responses[schedule_id]


def test_run_briefings_real_session_scope_isolates_failed_schedule(db_engine) -> None:
    """브리핑 `run_briefings()` 를 실 `session_scope()`(주기 작업·
    `app/briefing/scheduler.py::default_run_once` 와 같은 경계)로 돌린다.
    일정 2건 중 하나만 생성기가 실패하면, 실패 일정은 `briefed_at IS
    NULL` 로 남고 세이브포인트와 함께 그 일정의 `briefing_compose` trace
    도 사라지며, 성공 일정만 커밋된다(FIX-023 수정안 1d)."""
    user_id = _unique("briefing-real")

    setup_session = Session(bind=db_engine)
    try:
        person = Person(
            user_id=user_id, display_name="민수", relation_tag="친구", hierarchy="동"
        )
        setup_session.add(person)
        setup_session.flush()
        schedule_fail = Schedule(
            person_id=person.id, title="실패할 일정", scheduled_at=_NOW + timedelta(hours=1)
        )
        schedule_ok = Schedule(
            person_id=person.id, title="성공할 일정", scheduled_at=_NOW + timedelta(hours=2)
        )
        setup_session.add_all([schedule_fail, schedule_ok])
        setup_session.commit()
        person_id = person.id
        schedule_fail_id = schedule_fail.id
        schedule_ok_id = schedule_ok.id
    finally:
        setup_session.close()

    ok_response = ComposedBriefing(
        pattern_sentences=[], lines=[], suggestion=None, tokens_in=1, tokens_out=1, provider="fake"
    )
    composer = _ScriptedBriefingComposer(
        responses={schedule_ok_id: ok_response}, fail_for=frozenset({schedule_fail_id})
    )

    try:
        with session_scope() as session:
            ctx = ToolContext(
                session=session,
                session_id=f"fix023-briefing:{uuid.uuid4()}",
                user_id=user_id,
                now=lambda: _NOW,
            )
            result = run_briefings(ctx, composer=composer, trigger="manual")

        assert result.errors == 1
        run_session_id = result.session_id

        check = Session(bind=db_engine)
        try:
            fail_schedule = check.get(Schedule, schedule_fail_id)
            ok_schedule = check.get(Schedule, schedule_ok_id)
            assert fail_schedule is not None and fail_schedule.briefed_at is None
            assert ok_schedule is not None and ok_schedule.briefed_at == _NOW

            compose_rows = (
                check.execute(
                    select(AgentTrace)
                    .where(AgentTrace.session_id == run_session_id)
                    .where(AgentTrace.step == STEP_BRIEFING_COMPOSE)
                )
                .scalars()
                .all()
            )
            assert [row.output["schedule_id"] for row in compose_rows] == [schedule_ok_id]

            error_rows = (
                check.execute(
                    select(AgentTrace)
                    .where(AgentTrace.session_id == run_session_id)
                    .where(AgentTrace.step == STEP_BRIEFING_ERROR)
                    .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
                )
                .scalars()
                .all()
            )
            assert len(error_rows) == 1
            assert error_rows[0].output["schedule_id"] == schedule_fail_id
        finally:
            check.close()
    finally:
        cleanup = Session(bind=db_engine)
        try:
            cleanup.execute(delete(Schedule).where(Schedule.person_id == person_id))
            cleanup.execute(delete(Person).where(Person.id == person_id))
            if "run_session_id" in locals():
                cleanup.execute(
                    delete(AgentTrace).where(AgentTrace.session_id == run_session_id)
                )
            cleanup.commit()
        finally:
            cleanup.close()
