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


# ---------------------------------------------------------------------------
# U7 -- 루프가 직접 쓴 사실(update_person(facts))의 원문 연결(결정 G(ii))
# ---------------------------------------------------------------------------
#
# `_record_impl()` 을 직접 불러 `RecordOutcome`(fact_keys_by_person/
# event_ids_by_person)을 얻은 뒤, U6 과 같은 방식으로 `hooks_module.
# after_record()` 에 그대로 넘긴다(`_record()` 가 실제로 하는 일과 같다,
# ER 판정은 이 테스트의 관심사가 아니므로 `ResolveOutcome` 을 손으로
# 만든다 -- 위 절 관례와 같은 이유).


def _direct_link_rows(db_session, session_id: str) -> list[AgentTrace]:
    """`memory_promote` step 행 중 U7(`link_direct_facts`)이 남긴 것만
    고른다 -- `source="direct"` 로 LLM 승격(`PromotionResult`) 행과
    구분한다(`app/memory/types.py::DirectFactLinkResult` docstring)."""

    return [
        row
        for row in _trace_rows(db_session, session_id, "memory_promote")
        if isinstance(row.output, dict) and row.output.get("source") == "direct"
    ]


def _run_record_and_after_record(ctx, proposal, outcome, utterance, *, extractor=None):
    """`_record()` 가 하는 일(게이트 -> `_record_impl` -> `after_record`)
    을 손으로 재현한다 -- `loop_record` trace 자체는 이 테스트들의
    관심사가 아니므로 `@traced` 로 감싸지 않고 `_record_impl` 을 직접
    부른다(위 절 관례와 같은 이유)."""

    verdict = gate_check(proposal)
    record = loop_module._record_impl(
        ctx, proposal, verdict, outcome, utterance, resume_byte_limit=LOOP_MAX_RESUME_BYTES
    )
    hooks_module.after_record(
        ctx,
        record.event_person_ids,
        extractor if extractor is not None else FakeFactExtractor(),
        fact_keys_by_person=record.fact_keys_by_person,
        event_ids_by_person=record.event_ids_by_person,
    )
    return record


@dbtest
def test_direct_fact_basic_turn_links_free_key_fact_to_same_turn_event(db_session):
    """기본 -- 같은 턴에 같은 인물로 `add_event` + `update_person(facts)`
    가 함께 실행되면 그 사실에 `fact_sources` 링크가 생긴다. `FACT_KEYS`
    (승격 전용 9종) 밖의 **자유 키**("이직")로 확인한다(01-plan 결정 D-5
    는 승격에만 적용되고, 루프가 직접 쓰는 `update_person(facts)` 는
    여전히 자유 키다 -- 위임 프롬프트 "왜 필요한가" 절이 실 왕복에서 본
    바로 그 키)."""

    session_id = "loop-u7-direct-basic"
    person = _make_person(db_session, display_name="민수")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="민수", type="personal_share", content="이직 준비", occurred_at=NOW),
            _call("update_person", person="민수", facts=[{"key": "이직", "value": "이직 준비 중"}]),
        ],
        raw={},
    )
    outcome = ResolveOutcome(person_ids={"민수": person.id}, stopped=False)

    record = _run_record_and_after_record(ctx, proposal, outcome, "발화")

    assert record.failed == []
    assert record.fact_keys_by_person == {person.id: ["이직"]}
    event_id = record.event_ids_by_person[person.id][0]

    fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person.id).where(PersonFact.key == "이직")
    ).scalar_one()
    assert fact.value == "이직 준비 중"

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert [link.event_id for link in links] == [event_id]

    direct_rows = _direct_link_rows(db_session, session_id)
    assert len(direct_rows) == 1
    assert direct_rows[0].output["person_id"] == person.id
    assert direct_rows[0].output["links"] == [
        {"key": "이직", "action": "linked", "fact_id": fact.id, "event_ids": [event_id], "reason": None}
    ]

    # 원문 불변 -- 이벤트 행은 그대로다.
    events = db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
    assert len(events) == 1
    assert events[0].raw_utterance == "발화"
    assert events[0].content == "이직 준비"


@dbtest
def test_direct_fact_turn_without_event_leaves_fact_unlinked_and_traced(db_session):
    """이벤트 없는 턴 -- `update_person(facts)` 만 실행되고 `add_event`
    가 없으면 링크 0건이고 trace 에 `unlinked` 가 남는다(01-plan 73행)."""

    session_id = "loop-u7-direct-no-event"
    person = _make_person(db_session, display_name="민수")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[_call("update_person", person="민수", facts=[{"key": "hobby", "value": "등산"}])],
        raw={},
    )
    outcome = ResolveOutcome(person_ids={"민수": person.id}, stopped=False)

    record = _run_record_and_after_record(ctx, proposal, outcome, "발화")

    assert record.events == 0
    assert record.event_person_ids == []
    assert record.fact_keys_by_person == {person.id: ["hobby"]}

    fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person.id).where(PersonFact.key == "hobby")
    ).scalar_one()

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert links == []

    direct_rows = _direct_link_rows(db_session, session_id)
    assert len(direct_rows) == 1
    assert direct_rows[0].output["links"] == [
        {
            "key": "hobby",
            "action": "unlinked",
            "fact_id": fact.id,
            "event_ids": [],
            "reason": "no_event_this_turn",
        }
    ]


@dbtest
def test_direct_fact_same_key_twice_in_one_turn_links_once(db_session):
    """중복 -- 같은 턴에 같은 키로 `update_person` 이 두 번 실행되면
    (예: 두 번의 언급이 같은 사실을 다시 확인) 링크가 1건이다(`fact_sources`
    복합 기본키가 중복을 막는다 -- `RecordOutcome.fact_keys_by_person` 이
    턴 단위로 이미 키를 중복 제거해 넘기므로, `link_direct_facts` 는 그
    키에 대해 정확히 한 번만 호출된다)."""

    session_id = "loop-u7-direct-duplicate-key"
    person = _make_person(db_session, display_name="민수")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="민수", type="meeting", content="면접", occurred_at=NOW),
            _call("update_person", person="민수", facts=[{"key": "job", "value": "이직 준비"}]),
            _call("update_person", person="민수", facts=[{"key": "job", "value": "이직 확정"}]),
        ],
        raw={},
    )
    outcome = ResolveOutcome(person_ids={"민수": person.id}, stopped=False)

    record = _run_record_and_after_record(ctx, proposal, outcome, "발화")

    assert len(record.executed) == 3
    # 턴 단위 중복 제거 -- 두 번째 update_person 은 키를 다시 더하지 않는다.
    assert record.fact_keys_by_person == {person.id: ["job"]}

    fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person.id).where(PersonFact.key == "job")
    ).scalar_one()
    assert fact.value == "이직 확정"  # 두 번째 호출이 마지막으로 덮어씀

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert len(links) == 1  # 복합 PK 중복 방지 -- 같은 이벤트가 두 번 이어지지 않는다

    direct_rows = _direct_link_rows(db_session, session_id)
    assert len(direct_rows) == 1
    assert len(direct_rows[0].output["links"]) == 1  # key 도 한 번만 처리됨


@dbtest
def test_direct_fact_does_not_leak_across_different_persons(db_session):
    """다른 인물 섞임 -- A 인물의 사실이 B 인물의 이벤트에 붙지 않는다."""

    session_id = "loop-u7-direct-cross-person"
    person_a = _make_person(db_session, display_name="민수")
    person_b = _make_person(db_session, display_name="지훈")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="민수", type="personal_share", content="이직 이야기", occurred_at=NOW),
            _call("update_person", person="민수", facts=[{"key": "job", "value": "이직 준비"}]),
            _call("add_event", person="지훈", type="meal", content="점심", occurred_at=NOW),
        ],
        raw={},
    )
    outcome = ResolveOutcome(
        person_ids={"민수": person_a.id, "지훈": person_b.id}, stopped=False
    )

    record = _run_record_and_after_record(ctx, proposal, outcome, "발화")

    assert record.fact_keys_by_person == {person_a.id: ["job"]}  # 지훈에는 사실이 없다
    event_id_a = record.event_ids_by_person[person_a.id][0]
    event_id_b = record.event_ids_by_person[person_b.id][0]
    assert event_id_a != event_id_b

    fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person_a.id).where(PersonFact.key == "job")
    ).scalar_one()

    links = db_session.execute(select(FactSource).where(FactSource.fact_id == fact.id)).scalars().all()
    assert [link.event_id for link in links] == [event_id_a]  # 지훈의 이벤트는 섞이지 않는다

    # 지훈 인물에는 어떤 사실도 생기지 않았다.
    facts_b = db_session.execute(select(PersonFact).where(PersonFact.person_id == person_b.id)).scalars().all()
    assert facts_b == []


@dbtest
def test_direct_fact_failed_update_person_call_is_not_collected(db_session):
    """실패한 `update_person` -- 게이트를 지났지만 툴이 `InvalidValue` 로
    실패한 호출의 키는 모으지 않는다(`failed[]` 로 간다). 빈 문자열 값은
    게이트 ③ 의 타입 검사(문자열인지만 봄)를 통과하지만 `update_person`
    자신의 검증(`InvalidValue`)이 막는다."""

    session_id = "loop-u7-direct-failed-update"
    person = _make_person(db_session, display_name="민수")
    ctx = _ctx(db_session, session_id=session_id)

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="민수", type="personal_share", content="근황", occurred_at=NOW),
            _call("update_person", person="민수", facts=[{"key": "job", "value": ""}]),  # 빈 값 -- InvalidValue
        ],
        raw={},
    )
    outcome = ResolveOutcome(person_ids={"민수": person.id}, stopped=False)

    record = _run_record_and_after_record(ctx, proposal, outcome, "발화")

    assert len(record.failed) == 1
    assert record.failed[0]["name"] == "update_person"
    assert record.fact_keys_by_person == {}  # 실패한 호출의 키는 모으지 않는다

    facts = db_session.execute(select(PersonFact).where(PersonFact.person_id == person.id)).scalars().all()
    assert facts == []

    direct_rows = _direct_link_rows(db_session, session_id)
    assert direct_rows == []  # 이을 키가 없으니 link_direct_facts 자체가 불리지 않는다


@dbtest
def test_direct_fact_link_does_not_disturb_promotion_links_in_same_turn(db_session):
    """승격 사실 링크 불변 -- 같은 턴에 승격도 일어났다면 U5 가 만든
    링크가 U7 때문에 바뀌지 않는다. 미승격 이벤트 4건 + 이번 턴 1건으로
    승격 트리거(`MEMORY_PROMOTE_MIN_EVENTS`, 기본 5)를 채우고, 같은 턴에
    자유 키("연락처")로 직접 사실도 함께 쓴다 -- 두 경로는 서로 다른 키를
    쓰므로(승격은 `FACT_KEYS` 9종, 직접 사실은 자유 키) 겹치지 않는다.
    가짜 추출기의 근거는 **기존** 이벤트(id 재사용 없이, 사후에 실제
    id 를 알아낸다 -- DB 시퀀스는 테스트 사이에 리셋되지 않으므로 id 를
    미리 고정하지 않는다) 하나만 가리키게 해, 이번 턴 새 이벤트(직접
    사실의 근거)와 절대 겹치지 않게 한다."""

    session_id = "loop-u7-direct-with-promotion"
    person = _make_person(db_session, display_name="민수")
    ctx = _ctx(db_session, session_id=session_id)

    pre_events = [_add_event(db_session, person, event_type="personal_share") for _ in range(4)]
    promotion_source_id = pre_events[0].id

    extractor = FakeFactExtractor()

    proposal = Proposal(
        tool_calls=[
            _call("add_event", person="민수", type="personal_share", content="근황 공유", occurred_at=NOW),
            _call("update_person", person="민수", facts=[{"key": "연락처", "value": "새 번호로 등록"}]),
        ],
        raw={},
    )
    outcome = ResolveOutcome(person_ids={"민수": person.id}, stopped=False)

    # 승격 배치(오래된 순 5건)는 이번 턴 새 이벤트까지 포함해야 트리거가
    # 걸린다 -- 가짜 추출기의 table 키는 그 5건 id 집합과 정확히 같아야
    # 하므로, _record_impl 을 먼저 불러 실제 새 이벤트 id 를 얻은 뒤 표를
    # 마저 채운다.
    verdict = gate_check(proposal)
    record = loop_module._record_impl(
        ctx, proposal, verdict, outcome, "발화", resume_byte_limit=LOOP_MAX_RESUME_BYTES
    )
    event_id = record.event_ids_by_person[person.id][0]
    extractor.table[frozenset(e.id for e in pre_events) | {event_id}] = [
        {"key": "job", "value": "백엔드 개발자", "source_event_ids": [promotion_source_id]}
    ]

    hooks_module.after_record(
        ctx,
        record.event_person_ids,
        extractor,
        fact_keys_by_person=record.fact_keys_by_person,
        event_ids_by_person=record.event_ids_by_person,
    )

    direct_fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person.id).where(PersonFact.key == "연락처")
    ).scalar_one()
    direct_links = db_session.execute(
        select(FactSource).where(FactSource.fact_id == direct_fact.id)
    ).scalars().all()
    assert [link.event_id for link in direct_links] == [event_id]

    # 승격이 만든 job 사실은 U7 과 무관하게 그대로다 -- 링크는 추출기가
    # 지목한 기존 이벤트(promotion_source_id)뿐이고 이번 턴 새 이벤트
    # (event_id, 직접 사실의 근거)와 섞이지 않는다.
    promoted_fact = db_session.execute(
        select(PersonFact).where(PersonFact.person_id == person.id).where(PersonFact.key == "job")
    ).scalar_one()
    promoted_links = db_session.execute(
        select(FactSource).where(FactSource.fact_id == promoted_fact.id)
    ).scalars().all()
    assert [link.event_id for link in promoted_links] == [promotion_source_id]

    direct_rows = _direct_link_rows(db_session, session_id)
    assert len(direct_rows) == 1
    assert direct_rows[0].output["links"] == [
        {
            "key": "연락처",
            "action": "linked",
            "fact_id": direct_fact.id,
            "event_ids": [event_id],
            "reason": None,
        }
    ]
