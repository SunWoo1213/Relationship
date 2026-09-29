"""Refs: P6-memory S3.5 R8 R11 원칙9 -- U6 루프 연결
(`app/agent/loop.py::_record()` -> `app/memory/hooks.py::after_record()`)
테스트.

01-plan 판정 표 9·16·17·18행 + 위임 프롬프트가 요구한 추가 케이스(추출기
지연 해소·`event_person_ids` 산출)를 검증한다. `FakeProposer`/`FakeJudge`
(네트워크 0)와 `FakeFactExtractor`(결정 D-3, 표 기반·결정적)로만 돌아
실 키·네트워크가 없다(원칙8) -- 트리거가 안 걸리는 대부분의 시나리오는
추출기 자체를 만들지 않으므로(★ R-10 해소) 환경변수도 필요 없다. 실
PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`,
`dbtest` 마커)를 쓴다(`tests/test_memory_promote.py`/`test_agent_loop.py`
와 같은 관례)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

import app.agent.loop as loop_module
import app.memory.hooks as hooks_module
from app.agent.gate import check as gate_check
from app.agent.loop import ResolveOutcome, resume_turn, run_turn
from app.agent.propose import FakeProposer
from app.agent.types import Proposal, ToolCallProposal
from app.settings import LOOP_MAX_RESUME_BYTES
from app.api.deps import get_embedder, get_fact_extractor, get_judge, get_proposer, get_session, load_resume_input
from app.db.models import ALIAS_SOURCES, AgentTrace, Event, FactSource, Person, PersonAlias, PersonFact
from app.er.judge import FakeJudge
from app.main import create_app
from app.memory.extract import FakeFactExtractor
from app.tools.context import ToolContext
from app.tools.questions import answer_question

dbtest = pytest.mark.dbtest

NOW = datetime(2026, 9, 29, 4, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 헬퍼 (tests/test_agent_loop.py · tests/test_memory_promote.py 와 같은 관례)
# ---------------------------------------------------------------------------


def _make_person(
    db_session, *, display_name: str, relation_tag: str = "직장", hierarchy: str = "동", user_id: str = "local"
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session, person: Person, alias: str, *, embedding) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=ALIAS_SOURCES[0], embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


def _add_event(
    db_session, person: Person, *, event_type: str = "conflict", occurred_at: datetime = NOW, content: str = "내용"
) -> Event:
    event = Event(
        person_id=person.id,
        type=event_type,
        content=content,
        raw_utterance=f"raw: {content} ({occurred_at.isoformat()})",
        occurred_at=occurred_at,
    )
    db_session.add(event)
    db_session.flush()
    return event


def _ctx(db_session, *, session_id: str, embedder=None, now=lambda: NOW) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder, now=now)


def _add_event_call(person_mention: str, *, event_type: str = "conflict", content: str = "다툼") -> dict:
    return {
        "name": "add_event",
        "args": {
            "person": person_mention,
            "type": event_type,
            "content": content,
            "occurred_at": NOW.isoformat(),
        },
    }


def _trace_rows(db_session, session_id: str, step: str) -> list[AgentTrace]:
    return (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.step == step)
            .order_by(AgentTrace.id)
        )
        .scalars()
        .all()
    )


def _pattern_fact(db_session, person_id: int, event_type: str) -> PersonFact | None:
    return db_session.execute(
        select(PersonFact)
        .where(PersonFact.person_id == person_id)
        .where(PersonFact.key == f"pattern:{event_type}")
    ).scalar_one_or_none()


# ---------------------------------------------------------------------------
# 판정 표 9행 -- 패턴만 생기는 턴: 추출기 호출 0회, memory_pattern tokens 0
# ---------------------------------------------------------------------------


@dbtest
def test_pattern_only_turn_never_calls_extractor_and_has_zero_tokens(db_session, fake_embedder):
    session_id = "loop-u6-pattern-only"
    person = _make_person(db_session, display_name="민수")
    _add_alias(db_session, person, "민수", embedding=fake_embedder(["민수"])[0])
    # 미리 2건 -- 이번 턴의 1건과 합쳐 정확히 PATTERN_MIN_COUNT(3) 를
    # 채우지만 MEMORY_PROMOTE_MIN_EVENTS(5) 에는 못 미친다.
    _add_event(db_session, person, event_type="conflict")
    _add_event(db_session, person, event_type="conflict")

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "오늘 민수랑 또 싸웠어"
    extractor = FakeFactExtractor()

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: [_add_event_call("민수")]}),
        judge=FakeJudge(table={person.id: 0.95}),
        extractor=extractor,
    )

    assert result.stored.events == 1
    assert extractor.call_count == 0  # 미승격 3건 < 5 -- 승격 트리거 없음

    pattern_rows = _trace_rows(db_session, session_id, "memory_pattern")
    assert len(pattern_rows) == 1
    assert pattern_rows[0].tokens_in == 0
    assert pattern_rows[0].tokens_out == 0

    promote_rows = _trace_rows(db_session, session_id, "memory_promote")
    assert len(promote_rows) == 1
    assert promote_rows[0].output["considered_event_ids"] == []  # 미달 행

    fact = _pattern_fact(db_session, person.id, "conflict")
    assert fact is not None
    assert fact.value.startswith("3회")


# ---------------------------------------------------------------------------
# 판정 표 16행 -- 실패 격리: 승격 오류가 나도 턴은 200, 이벤트는 저장됨
# ---------------------------------------------------------------------------


@dbtest
def test_extractor_failure_is_isolated_event_survives_and_memory_error_is_recorded(
    db_session, fake_embedder
):
    session_id = "loop-u6-promote-fail"
    person = _make_person(db_session, display_name="민수")
    _add_alias(db_session, person, "민수", embedding=fake_embedder(["민수"])[0])
    for _ in range(4):
        _add_event(db_session, person, event_type="conflict")

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "오늘 민수랑 또 싸웠어"

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: [_add_event_call("민수")]}),
        judge=FakeJudge(table={person.id: 0.95}),
        extractor=FakeFactExtractor(fail="timeout"),
    )

    # 턴 응답은 정상 -- 예외가 이 함수까지 올라오지 않는다.
    assert result.stored.events == 1
    assert result.pending_question is None

    events = db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
    assert len(events) == 5  # 미리 4건 + 이번 턴 1건, 전부 저장 유지

    # 패턴(먼저 도는 단계)도 승격 실패와 같은 세이브포인트에서 함께
    # 롤백되므로 사실이 하나도 남지 않는다(01-plan 72행 "전체를 감싼다").
    facts = db_session.execute(select(PersonFact).where(PersonFact.person_id == person.id)).scalars().all()
    assert facts == []

    error_rows = _trace_rows(db_session, session_id, "memory_error")
    assert len(error_rows) == 1
    assert error_rows[0].output == {
        "person_id": person.id,
        "stage": "promote",
        "error": "JudgeUnavailable",
    }

    # 롤백된 memory_pattern/memory_promote 중간 trace 는 남지 않는다.
    assert _trace_rows(db_session, session_id, "memory_pattern") == []
    assert _trace_rows(db_session, session_id, "memory_promote") == []


# ---------------------------------------------------------------------------
# 판정 표 17행 -- 재개 경로: identity 답 뒤 resume_turn 에서 저장, 패턴 생성
# ---------------------------------------------------------------------------


@dbtest
def test_resume_turn_after_identity_answer_reaches_pattern_threshold(db_session, fake_embedder):
    session_id = "loop-u6-resume-pattern"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    _add_event(db_session, person, event_type="conflict")
    _add_event(db_session, person, event_type="conflict")

    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    utterance = "팀장이랑 또 싸웠어"

    result1 = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: [_add_event_call("팀장")]}),
        # 규칙 통과 후보(별칭 "팀장")가 있는 채로 LLM 판정이 실패하면
        # identity 로 강제 확정된다(app/er/pipeline.py, test_agent_loop.py
        # 의 identity 테스트와 같은 경로).
        judge=FakeJudge(fail="timeout"),
    )

    assert result1.pending_question is not None
    assert result1.pending_question.kind == "identity"
    assert result1.stored.events == 0
    question_id = result1.pending_question.question_id

    answer_question(ctx, question_id, "김민수")
    resume_input = load_resume_input(db_session, question_id)

    result2 = resume_turn(ctx, resume_input, question_id=question_id)

    assert result2.stored.events == 1  # 재개 안에서 add_event 가 실행됨

    events = db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
    assert len(events) == 3  # 미리 2건 + 재개로 저장된 1건 = 누적 3건

    fact = _pattern_fact(db_session, person.id, "conflict")
    assert fact is not None
    assert fact.value.startswith("3회")

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert len(links) == 3


# ---------------------------------------------------------------------------
# 판정 표 18행 -- API 한 흐름: POST /chat 3회 뒤 pattern:{type} + 링크 3
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_and_client(db_session, fake_embedder):
    """U1 롤백 세션을 `get_session` 자리에 주입한 `(app, client)` 쌍
    (P2 결정 13, `tests/test_api_chat.py` 와 같은 관례). `get_fact_extractor`
    도 `FakeFactExtractor()` 로 오버라이드한다 -- 운영 기본값(`None`)은
    `_LazyFactExtractor` 를 거치므로, 이 픽스처는 "가짜 추출기가 이미
    주입된 경로" 자체를 확인하는 데 쓴다(판정 표 18행 "가짜 추출기")."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    app.dependency_overrides[get_fact_extractor] = lambda: FakeFactExtractor()
    return app, TestClient(app)


@dbtest
def test_api_chat_three_turns_creates_pattern_fact_with_three_links(
    app_and_client, db_session, fake_embedder
):
    app, client = app_and_client
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    app.dependency_overrides[get_judge] = lambda: FakeJudge(table={person.id: 0.95})

    for i in range(3):
        utterance = f"팀장이랑 또 싸웠어 ({i}번째)"
        app.dependency_overrides[get_proposer] = lambda utterance=utterance: FakeProposer(
            table={utterance: [_add_event_call("팀장")]}
        )
        resp = client.post(
            "/chat", json={"utterance": utterance}, headers={"X-Session-Id": "u6-api-pattern"}
        )
        assert resp.status_code == 200
        assert resp.json()["stored"]["events"] == 1

    fact = _pattern_fact(db_session, person.id, "conflict")
    assert fact is not None
    assert fact.value.startswith("3회")

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert len(links) == 3


# ---------------------------------------------------------------------------
# 추출기 지연 해소 -- 트리거가 안 걸리면 extractor_from_env() 가 안 불린다
# (★ R-10 해소의 근거를 고정한다)
# ---------------------------------------------------------------------------


@dbtest
def test_after_record_does_not_resolve_extractor_from_env_when_trigger_not_met(
    db_session, monkeypatch
):
    def _boom(env=None):
        raise AssertionError("extractor_from_env() 는 트리거 미달일 때 불려서는 안 된다")

    monkeypatch.setattr(hooks_module, "extractor_from_env", _boom)

    person = _make_person(db_session, display_name="민수")
    _add_event(db_session, person, event_type="personal_share")  # 1건 -- 5 미만

    ctx = _ctx(db_session, session_id="loop-u6-lazy-extractor")

    # extractor=None -- after_record 가 _LazyFactExtractor 로 감싸지만
    # promote_person 이 트리거 미달로 extract() 를 아예 부르지 않으므로
    # _boom() 도 불리지 않는다(예외 없이 끝나야 한다).
    hooks_module.after_record(ctx, [person.id], None)

    promote_rows = _trace_rows(db_session, "loop-u6-lazy-extractor", "memory_promote")
    assert len(promote_rows) == 1
    assert promote_rows[0].output["considered_event_ids"] == []


# ---------------------------------------------------------------------------
# RecordOutcome.event_person_ids -- 성공한 add_event 만, 중복 제거, 첫 등장 순
# ---------------------------------------------------------------------------
#
# ER(해석 단계)를 손으로 만든 `ResolveOutcome` 로 대신해 `_record_impl()`
# 을 직접 부른다(`tests/test_agent_loop.py` 의 `_verdict_for` 관례와 같은
# 방향) -- 이 테스트의 관심사는 ER 판정이 아니라 "성공한 add_event 의
# person_id 를 어떻게 모으는가" 뿐이고, 서로 다른 두 인물을 한 턴에 함께
# 두면(둘 다 별칭 임베딩이 있으면) ER 후보 검색이 둘 다 candidates 로
# 돌려줘 FakeJudge 판정이 모호해진다(person_ids 를 직접 확정하면 이
# 모호함을 피할 수 있다).


def _call(name: str, **args) -> ToolCallProposal:
    return ToolCallProposal(name=name, args=args)


@dbtest
def test_record_impl_event_person_ids_dedup_first_appearance_order(db_session):
    session_id = "loop-u6-event-person-ids"
    person_a = _make_person(db_session, display_name="민수")
    person_b = _make_person(db_session, display_name="지훈")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="지훈", type="meal", content="점심", occurred_at=NOW),
            _call("add_event", person="민수", type="conflict", content="다툼", occurred_at=NOW),
            _call("add_event", person="지훈", type="other", content="통화", occurred_at=NOW),
        ],
        raw={},
    )
    verdict = gate_check(proposal)
    outcome = ResolveOutcome(person_ids={"지훈": person_b.id, "민수": person_a.id}, stopped=False)

    record = loop_module._record_impl(
        ctx, proposal, verdict, outcome, "발화", resume_byte_limit=LOOP_MAX_RESUME_BYTES
    )

    assert record.events == 3
    assert record.failed == []
    # 지훈(첫 등장) -> 민수 -> 지훈(중복, 다시 담지 않음)
    assert record.event_person_ids == [person_b.id, person_a.id]
