"""Refs: P2b-person-delete U2 F-4d2507 security§5 원칙8 원칙9 -- `delete_person`
(app/api/delete.py) DB 테스트.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`).
**센티널 시나리오**: `persons.id = 987654321`(IDENTITY BY DEFAULT 라 명시 삽입 가능,
다른 시퀀스가 이 값에 닿지 않는다)인 인물과 대조군 인물을 만들고, 손으로 만든
JSON 이 아니라 **실제 쓰는 코드**(`run_turn`·`answer_question`·`run_briefings`·
`after_record` 승격)가 남긴 JSONB 를 정리 대상으로 삼는다 -- 가짜 공급자
(`FakeProposer`·`FakeJudge`·`FakeBriefingComposer`·`FakeFactExtractor`)만 쓰므로
네트워크 0(원칙8). 삭제 뒤 `pending_questions.context::text`·`agent_traces.input::text`
·`output::text` 어디에도 센티널 숫자가 없어야 한다(결정 C-3 이 놓친 모양을 잡는 그물).

사실 3 표(쓰는 곳)와 이 시나리오의 대조는 `tests.md` U2 절 아래 표에 있다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import Text, cast, func, select

from app.agent.loop import run_turn
from app.agent.propose import FakeProposer
from app.api.delete import PersonDeleteSummary, delete_person, references_person
from app.briefing.compose import FakeBriefingComposer
from app.briefing.run import run_briefings
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
from app.memory.extract import FakeFactExtractor
from app.tools.context import ToolContext, to_jsonable
from app.tools.questions import answer_question
from app.tools.types import (
    ConfirmationRequired,
    EventOut,
    PersonNotFound,
    PersonOut,
    ScheduleOut,
)
from tests.helpers_read_api import assert_no_writes, snapshot_db

pytestmark = pytest.mark.dbtest

SENTINEL = 987654321
SENTINEL_NAME = "삭제대상센티널"
USER = "p2b-u2-user"
OTHER_USER = "p2b-u2-other-user"
NOW = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)

#: 결정 A 의 사유 코드 -- 값으로 고정한다.
CONFIRM_REASON = "person_delete"


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _make_person(
    db_session: Any,
    *,
    display_name: str,
    person_id: int | None = None,
    user_id: str = USER,
) -> Person:
    kwargs: dict[str, Any] = {}
    if person_id is not None:
        kwargs["id"] = person_id
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag="직장", hierarchy="동", **kwargs
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session: Any, person: Person, alias: str, embedder: Any) -> PersonAlias:
    row = PersonAlias(
        person_id=person.id,
        alias=alias,
        source=ALIAS_SOURCES[0],
        embedding=embedder([alias])[0],
    )
    db_session.add(row)
    db_session.flush()
    return row


def _add_event(
    db_session: Any, person: Person, *, event_type: str = "conflict", day: int = 1
) -> Event:
    when = NOW - timedelta(days=day)
    event = Event(
        person_id=person.id,
        type=event_type,
        content=f"내용{day}",
        raw_utterance=f"raw: {person.display_name} {day}",
        occurred_at=when,
    )
    db_session.add(event)
    db_session.flush()
    return event


def _ctx(db_session: Any, embedder: Any, session_id: str, *, user_id: str = USER) -> ToolContext:
    return ToolContext(
        session=db_session,
        session_id=session_id,
        user_id=user_id,
        embedder=embedder,
        now=lambda: NOW,
    )


def _turn(
    db_session: Any,
    embedder: Any,
    session_id: str,
    utterance: str,
    calls: list[dict[str, Any]],
    judge: FakeJudge,
    *,
    user_id: str = USER,
    extractor: FakeFactExtractor | None = None,
) -> Any:
    ctx = _ctx(db_session, embedder, session_id, user_id=user_id)
    return run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=judge,
        extractor=extractor if extractor is not None else FakeFactExtractor(),
    )


class _AllEventsExtractor(FakeFactExtractor):
    """승격 입력 이벤트 id 집합을 미리 알 수 없어, 받은 이벤트 전부를 근거로 사실 1개를
    돌려준다(`_parse_extraction` 을 그대로 거친다 -- `FakeFactExtractor.extract` 재사용)."""

    def extract(self, person: str, existing_facts: Any, events: Any) -> Any:
        ids = [event.id for event in events]
        self.table = {
            frozenset(ids): [{"key": "likes", "value": "등산", "source_event_ids": ids[:2]}]
        }
        return super().extract(person, existing_facts, events)


@dataclass
class World:
    session: Any
    embedder: Any
    sentinel: Person
    control: Person
    other_user_person: Person
    unanswered_qid: int
    answered_qid: int
    control_qid: int


def _count(session: Any, model: Any, *conditions: Any) -> int:
    return session.execute(
        select(func.count()).select_from(model).where(*conditions)
    ).scalar_one()


def _text_hits(session: Any, column: Any, needle: int | str) -> int:
    return _count(session, column.class_, cast(column, Text).like(f"%{needle}%"))


def _person_state(session: Any, person_id: int) -> dict[str, list[tuple[Any, ...]]]:
    """한 인물의 5개 테이블 + `fact_sources` 행을 **값**으로 뽑는다(전후 비교용)."""

    def rows(stmt: Any) -> list[tuple[Any, ...]]:
        return [tuple(r) for r in session.execute(stmt).all()]

    fact_ids = select(PersonFact.id).where(PersonFact.person_id == person_id)
    return {
        "persons": rows(
            select(
                Person.id,
                Person.user_id,
                Person.display_name,
                Person.relation_tag,
                Person.hierarchy,
                Person.created_at,
                Person.updated_at,
            ).where(Person.id == person_id)
        ),
        "person_aliases": rows(
            select(PersonAlias.id, PersonAlias.alias, PersonAlias.source, PersonAlias.confirmed_at)
            .where(PersonAlias.person_id == person_id)
            .order_by(PersonAlias.id)
        ),
        "person_facts": rows(
            select(
                PersonFact.id,
                PersonFact.key,
                PersonFact.value,
                PersonFact.confidence,
                PersonFact.updated_at,
            )
            .where(PersonFact.person_id == person_id)
            .order_by(PersonFact.id)
        ),
        "events": rows(
            select(Event.id, Event.type, Event.content, Event.raw_utterance, Event.occurred_at)
            .where(Event.person_id == person_id)
            .order_by(Event.id)
        ),
        "schedules": rows(
            select(Schedule.id, Schedule.title, Schedule.scheduled_at, Schedule.briefed_at)
            .where(Schedule.person_id == person_id)
            .order_by(Schedule.id)
        ),
        "fact_sources": rows(
            select(FactSource.fact_id, FactSource.event_id)
            .where(FactSource.fact_id.in_(fact_ids))
            .order_by(FactSource.fact_id, FactSource.event_id)
        ),
    }


def _unrelated_jsonb_rows(session: Any, needle: int) -> dict[str, list[tuple[Any, ...]]]:
    """센티널 숫자가 텍스트에 **없는** 질문·trace 행 전체(값). 삭제 전후 같아야 한다."""

    questions = session.execute(
        select(
            PendingQuestion.id,
            PendingQuestion.session_id,
            PendingQuestion.kind,
            PendingQuestion.question,
            PendingQuestion.options,
            PendingQuestion.context,
            PendingQuestion.answer,
            PendingQuestion.answered_at,
        )
        .where(cast(PendingQuestion.context, Text).not_like(f"%{needle}%"))
        .order_by(PendingQuestion.id)
    ).all()
    traces = session.execute(
        select(
            AgentTrace.id,
            AgentTrace.session_id,
            AgentTrace.step,
            AgentTrace.tool_name,
            AgentTrace.input,
            AgentTrace.output,
            AgentTrace.tokens_in,
            AgentTrace.tokens_out,
        )
        .where(cast(AgentTrace.input, Text).not_like(f"%{needle}%"))
        .where(cast(AgentTrace.output, Text).not_like(f"%{needle}%"))
        .order_by(AgentTrace.id)
    ).all()
    return {"questions": [tuple(r) for r in questions], "traces": [tuple(r) for r in traces]}


@pytest.fixture()
def world(db_session: Any, fake_embedder: Any) -> World:
    """센티널·대조군 인물을 만들고 실제 코드 경로로 JSONB 를 쌓는다.

    사실 3 표 대조: ① `@traced` 툴 trace(`update_person`·`add_event`·`add_schedule`·
    `get_briefing`·`search_person`) ② ER 되묻기 context·`ask_user` trace
    ③ `loop_resolve_done.person_ids` ④ 브리핑 `briefing_compose`·`briefing_run`
    ⑤ 메모리 `memory_pattern`·`memory_promote`.
    """

    sentinel = _make_person(db_session, display_name=SENTINEL_NAME, person_id=SENTINEL)
    control = _make_person(db_session, display_name="대조군")
    other_user_person = _make_person(db_session, display_name="남의대조", user_id=OTHER_USER)

    _add_alias(db_session, sentinel, SENTINEL_NAME, fake_embedder)
    _add_alias(db_session, sentinel, "그분", fake_embedder)
    _add_alias(db_session, control, "대조군", fake_embedder)
    _add_alias(db_session, control, "그분", fake_embedder)  # 센티널과 함께 후보가 되도록
    _add_alias(db_session, other_user_person, "남의대조", fake_embedder)

    # 센티널: 미승격 이벤트 4건(이번 턴 1건과 합쳐 5건 -> 승격 트리거) -- 같은 type 이라 패턴도 걸린다.
    for day in (5, 4, 3, 2):
        _add_event(db_session, sentinel, day=day)

    # 대조군: 이벤트 2건 + 사실 1건 + 근거 링크 1건 (전후 동일해야 한다)
    control_events = [_add_event(db_session, control, event_type="meal", day=d) for d in (9, 8)]
    control_fact = PersonFact(person_id=control.id, key="hobby", value="독서", confidence=0.9)
    db_session.add(control_fact)
    db_session.flush()
    db_session.add(FactSource(fact_id=control_fact.id, event_id=control_events[0].id))
    db_session.add(
        PushSubscription(user_id=USER, endpoint="https://push.example/p2b-u2", keys={"p": "x"})
    )
    db_session.flush()

    # 센티널 기록 턴(merge): add_event + add_schedule + update_person(facts) + 승격 + 패턴
    utterance = f"{SENTINEL_NAME}랑 점심 먹다 또 싸우고 두 시간 뒤에 보기로 했어"
    _turn(
        db_session,
        fake_embedder,
        "p2b-u2-record",
        utterance,
        [
            {
                "name": "add_event",
                "args": {
                    "person": SENTINEL_NAME,
                    "type": "conflict",
                    "content": "점심 다툼",
                    "occurred_at": NOW.isoformat(),
                },
            },
            {
                "name": "add_schedule",
                "args": {
                    "person": SENTINEL_NAME,
                    "title": "저녁 약속",
                    "scheduled_at": (NOW + timedelta(hours=2)).isoformat(),
                },
            },
            {
                "name": "update_person",
                "args": {"person": SENTINEL_NAME, "facts": [{"key": "취미", "value": "등산"}]},
            },
        ],
        FakeJudge(table={sentinel.id: 0.95}),
        extractor=_AllEventsExtractor(),
    )

    # identity 되묻기 -- 두 인물이 후보, 미답변으로 둔다
    unanswered = _turn(
        db_session,
        fake_embedder,
        "p2b-u2-ask-open",
        "그분이랑 밥 먹었어",
        [
            {
                "name": "add_event",
                "args": {
                    "person": "그분",
                    "type": "meal",
                    "content": "밥",
                    "occurred_at": NOW.isoformat(),
                },
            }
        ],
        FakeJudge(fail="timeout"),
    )
    # identity 되묻기 -- 답변된 질문
    answered = _turn(
        db_session,
        fake_embedder,
        "p2b-u2-ask-answered",
        "그분한테 칭찬 들었어",
        [
            {
                "name": "add_event",
                "args": {
                    "person": "그분",
                    "type": "praise",
                    "content": "칭찬",
                    "occurred_at": NOW.isoformat(),
                },
            }
        ],
        FakeJudge(fail="timeout"),
    )
    answered_row = db_session.get(PendingQuestion, answered.pending_question.question_id)
    answer_question(
        _ctx(db_session, fake_embedder, "p2b-u2-ask-answered"),
        answered_row.id,
        answered_row.options[-1],
    )

    # 브리핑 1회(센티널·대조군 일정 둘 다 24h 안)
    db_session.add(Schedule(person_id=control.id, title="대조군 약속", scheduled_at=NOW + timedelta(hours=3)))
    db_session.flush()
    run_briefings(
        _ctx(db_session, fake_embedder, "p2b-u2-briefing-caller"),
        composer=FakeBriefingComposer(fail="timeout"),
        trigger="manual",
    )

    # 대조군만 나오는 턴: merge 1회 + 다른 사용자 범위의 identity 되묻기 1회
    _turn(
        db_session,
        fake_embedder,
        "p2b-u2-control-turn",
        "대조군이랑 점심 먹었어",
        [
            {
                "name": "add_event",
                "args": {
                    "person": "대조군",
                    "type": "meal",
                    "content": "점심",
                    "occurred_at": NOW.isoformat(),
                },
            }
        ],
        FakeJudge(table={control.id: 0.95}),
    )
    control_ask = _turn(
        db_session,
        fake_embedder,
        "p2b-u2-control-ask",
        "남의대조 얘기 또 나왔어",
        [
            {
                "name": "add_event",
                "args": {
                    "person": "남의대조",
                    "type": "other",
                    "content": "얘기",
                    "occurred_at": NOW.isoformat(),
                },
            }
        ],
        FakeJudge(fail="timeout"),
        user_id=OTHER_USER,
    )

    return World(
        session=db_session,
        embedder=fake_embedder,
        sentinel=sentinel,
        control=control,
        other_user_person=other_user_person,
        unanswered_qid=unanswered.pending_question.question_id,
        answered_qid=answered_row.id,
        control_qid=control_ask.pending_question.question_id,
    )


def _delete_sentinel(world: World, confirm: str | None = SENTINEL_NAME) -> PersonDeleteSummary:
    return delete_person(world.session, USER, SENTINEL, confirm)


# ---------------------------------------------------------------------------
# 시나리오 자체의 전제 -- 삭제 전에 센티널이 실제로 어디에나 들어 있다
# ---------------------------------------------------------------------------


def test_world_sentinel_is_planted_in_questions_and_traces_before_delete(world: World) -> None:
    """전제 확인 -- 삭제 전에는 질문·trace 의 input/output 양쪽에 센티널이 있다
    (이게 0 이면 아래 '삭제 뒤 0' 단언이 아무것도 증명하지 못한다)."""
    s = world.session
    assert _text_hits(s, PendingQuestion.context, SENTINEL) == 2
    assert _text_hits(s, AgentTrace.input, SENTINEL) > 0
    assert _text_hits(s, AgentTrace.output, SENTINEL) > 0
    assert _count(s, Event, Event.person_id == SENTINEL) == 5
    assert _count(s, Schedule, Schedule.person_id == SENTINEL) == 1
    assert _count(s, PersonAlias, PersonAlias.person_id == SENTINEL) == 2
    # 승격(likes)·패턴(pattern:conflict)·직접 사실(취미) -- 사실 3개와 근거 링크
    keys = set(
        s.execute(select(PersonFact.key).where(PersonFact.person_id == SENTINEL)).scalars().all()
    )
    assert keys == {"likes", "pattern:conflict", "취미"}
    assert _count(s, FactSource, FactSource.event_id.in_(select(Event.id).where(Event.person_id == SENTINEL))) > 0


# ---------------------------------------------------------------------------
# CASCADE 5테이블 + fact_sources (결정 D) -- J-1
# ---------------------------------------------------------------------------


def test_cascade_removes_every_row_of_the_person_and_leaves_control_identical(world: World) -> None:
    s = world.session
    control_before = _person_state(s, world.control.id)
    other_before = _person_state(s, world.other_user_person.id)
    push_before = _count(s, PushSubscription)
    assert all(control_before[key] for key in control_before)  # 대조군도 6군데 모두 행이 있다

    summary = _delete_sentinel(world)

    assert summary.person_id == SENTINEL
    state = _person_state(s, SENTINEL)
    assert state == {
        "persons": [],
        "person_aliases": [],
        "person_facts": [],
        "events": [],
        "schedules": [],
        "fact_sources": [],
    }
    assert _person_state(s, world.control.id) == control_before
    assert _person_state(s, world.other_user_person.id) == other_before
    assert _count(s, PushSubscription) == push_before


# ---------------------------------------------------------------------------
# pending_questions (결정 C-1) -- J-2
# ---------------------------------------------------------------------------


def test_pending_questions_referencing_person_are_deleted_answered_or_not(world: World) -> None:
    s = world.session
    assert s.get(PendingQuestion, world.unanswered_qid).answered_at is None
    assert s.get(PendingQuestion, world.answered_qid).answered_at is not None
    control_question = s.get(PendingQuestion, world.control_qid)
    control_question_before = (
        control_question.id,
        control_question.kind,
        control_question.question,
        control_question.options,
        control_question.context,
    )

    summary = _delete_sentinel(world)

    s.expire_all()
    assert s.get(PendingQuestion, world.unanswered_qid) is None
    assert s.get(PendingQuestion, world.answered_qid) is None
    assert summary.deleted["pending_questions"] == 2
    assert _text_hits(s, PendingQuestion.context, SENTINEL) == 0
    survivor = s.get(PendingQuestion, world.control_qid)
    assert survivor is not None
    assert (
        survivor.id,
        survivor.kind,
        survivor.question,
        survivor.options,
        survivor.context,
    ) == control_question_before


# ---------------------------------------------------------------------------
# agent_traces (결정 C-2·C-3) -- J-3
# ---------------------------------------------------------------------------


def test_traces_no_sentinel_text_remains_in_input_or_output(world: World) -> None:
    s = world.session
    _delete_sentinel(world)
    assert _text_hits(s, AgentTrace.input, SENTINEL) == 0
    assert _text_hits(s, AgentTrace.output, SENTINEL) == 0
    assert _text_hits(s, PendingQuestion.context, SENTINEL) == 0


def test_traces_covering_each_shape_in_the_scenario_are_deleted(world: World) -> None:
    """01-plan 리스크 1 대조 -- 시나리오가 사실 3 표의 쓰는 곳을 한 번씩 지나갔는지,
    삭제 전에 step/tool 로 확인하고 삭제 뒤 그 행들이 사라졌는지 본다."""
    s = world.session
    def pairs() -> set[tuple[str, str]]:
        rows = s.execute(
            select(AgentTrace.step, AgentTrace.tool_name).where(
                cast(AgentTrace.input, Text).like(f"%{SENTINEL}%")
                | cast(AgentTrace.output, Text).like(f"%{SENTINEL}%")
            )
        ).all()
        return {(r.step, r.tool_name) for r in rows}

    steps_before = {step for step, _ in pairs()}
    for step in (
        "loop_resolve_done",
        "briefing_compose",
        "memory_pattern",
        "memory_promote",
    ):
        assert step in steps_before, step
    for pair in (
        ("tool_call", "update_person"),
        ("tool_call", "add_event"),
        ("tool_call", "add_schedule"),
        ("tool_call", "get_briefing"),
        ("tool_call", "ask_user"),
    ):
        assert pair in pairs(), pair

    _delete_sentinel(world)
    assert pairs() == set()


def test_traces_control_only_and_unrelated_rows_are_unchanged(world: World) -> None:
    """과잉 삭제 0 -- 센티널 숫자가 없는 질문·trace 행 전체가 값까지 그대로다."""
    s = world.session
    before = _unrelated_jsonb_rows(s, SENTINEL)
    control_ref_traces = [
        row for row in before["traces"] if references_person(row[5], world.control.id, tool_name=row[3])
        or references_person(row[4], world.control.id)
    ]
    assert len(control_ref_traces) >= 3  # 대조군만 참조하는 trace 가 실제로 있다
    assert len(before["questions"]) >= 1

    _delete_sentinel(world)

    assert _unrelated_jsonb_rows(s, SENTINEL) == before


def test_traces_delete_writes_no_trace_row(world: World) -> None:
    """결정 H -- 삭제 자체는 trace 를 남기지 않는다: 전체 trace 수 = 전 - 삭제 건수."""
    s = world.session
    total_before = _count(s, AgentTrace)
    summary = _delete_sentinel(world)
    assert _count(s, AgentTrace) == total_before - summary.deleted["agent_traces"]


# ---------------------------------------------------------------------------
# 반환 건수 (결정 F) -- V2-7
# ---------------------------------------------------------------------------


def test_summary_counts_equal_seeded_counts(world: World) -> None:
    s = world.session
    expected_fact_sources = _count(
        s,
        FactSource,
        FactSource.fact_id.in_(select(PersonFact.id).where(PersonFact.person_id == SENTINEL)),
    )
    expected_traces = _count(
        s, AgentTrace, cast(AgentTrace.input, Text).like(f"%{SENTINEL}%")
    ) + _count(
        s,
        AgentTrace,
        cast(AgentTrace.output, Text).like(f"%{SENTINEL}%"),
        cast(AgentTrace.input, Text).not_like(f"%{SENTINEL}%"),
    )

    summary = _delete_sentinel(world)

    assert summary.to_dict() == {
        "person_id": SENTINEL,
        "deleted": {
            "persons": 1,
            "person_aliases": 2,
            "person_facts": 3,
            "fact_sources": expected_fact_sources,
            "events": 5,
            "schedules": 1,
            "pending_questions": 2,
            "agent_traces": expected_traces,
        },
    }
    assert expected_fact_sources >= 3
    assert expected_traces >= 10


# ---------------------------------------------------------------------------
# 삭제 전 확인 (결정 A) -- J-4, V2-5
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "confirm",
    [None, "", "다른이름", f" {SENTINEL_NAME}", f"{SENTINEL_NAME} ", SENTINEL_NAME.replace("센", "섿"), "대조군"],
)
def test_confirm_missing_or_mismatch_raises_and_writes_nothing(world: World, confirm: str | None) -> None:
    s = world.session
    before = snapshot_db(s)
    with pytest.raises(ConfirmationRequired) as excinfo:
        _delete_sentinel(world, confirm)
    assert excinfo.value.reason == CONFIRM_REASON
    assert_no_writes(before, snapshot_db(s))
    assert _count(s, Person, Person.id == SENTINEL) == 1


def test_confirm_correct_value_deletes_the_person(world: World) -> None:
    s = world.session
    _delete_sentinel(world, SENTINEL_NAME)
    assert _count(s, Person, Person.id == SENTINEL) == 0


def test_confirm_uses_current_display_name_not_alias(world: World) -> None:
    """확인값은 **현재** `display_name` 이다 -- 별칭("그분")이나 옛 이름은 통하지 않는다."""
    world.sentinel.display_name = "바뀐이름"
    world.session.flush()
    before = snapshot_db(world.session)
    for wrong in (SENTINEL_NAME, "그분"):
        with pytest.raises(ConfirmationRequired):
            _delete_sentinel(world, wrong)
    assert_no_writes(before, snapshot_db(world.session))
    _delete_sentinel(world, "바뀐이름")
    assert _count(world.session, Person, Person.id == SENTINEL) == 0


# ---------------------------------------------------------------------------
# 소유 확인 (결정 E) -- J-5, V2-4
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("confirm", ["남의대조", None, "틀린이름"])
def test_other_user_person_is_not_found_whatever_the_confirm_is(world: World, confirm: str | None) -> None:
    """남의 인물이면 확인값이 맞든 틀리든 `PersonNotFound` -- 확인 422 가 존재를 흘리지 않는다."""
    s = world.session
    before = snapshot_db(s)
    with pytest.raises(PersonNotFound):
        delete_person(s, USER, world.other_user_person.id, confirm)
    assert_no_writes(before, snapshot_db(s))
    assert _count(s, Person, Person.id == world.other_user_person.id) == 1


def test_not_found_for_missing_id_even_with_any_confirm(world: World) -> None:
    s = world.session
    before = snapshot_db(s)
    with pytest.raises(PersonNotFound):
        delete_person(s, USER, 123456789012, SENTINEL_NAME)
    with pytest.raises(PersonNotFound):
        delete_person(s, USER, 123456789012, None)
    assert_no_writes(before, snapshot_db(s))


def test_not_found_on_second_delete_of_same_id(world: World) -> None:
    _delete_sentinel(world)
    with pytest.raises(PersonNotFound):
        _delete_sentinel(world)


# ---------------------------------------------------------------------------
# 트랜잭션 경계 (결정 D·P2 결정 2) -- V2-8
# ---------------------------------------------------------------------------


def test_service_does_not_commit_outer_rollback_restores_everything(world: World) -> None:
    s = world.session
    before = snapshot_db(s)
    state_before = _person_state(s, SENTINEL)
    nested = s.begin_nested()
    summary = _delete_sentinel(world)
    assert summary.deleted["persons"] == 1
    assert _count(s, Person, Person.id == SENTINEL) == 0
    nested.rollback()
    assert _count(s, Person, Person.id == SENTINEL) == 1
    assert _person_state(s, SENTINEL) == state_before
    assert_no_writes(before, snapshot_db(s))


# ---------------------------------------------------------------------------
# 같은 숫자의 다른 뜻 (V2-6) -- 텍스트 LIKE 만으로 지우면 남의 행이 사라진다
# ---------------------------------------------------------------------------


def test_traces_same_digits_in_other_roles_are_not_deleted(db_session: Any) -> None:
    """이벤트·일정·질문 id 가 삭제 대상 인물 id 와 같은 숫자여도 그 행들은 남는다.
    이 인물을 가리키는 행만 지워진다: input `person_id` 1 · output `EventOut.person_id` 1 ·
    `create_person` output 최상위 `id`(규칙 3) 1 = 3행."""
    shared = 555000111
    _make_person(db_session, display_name="동숫자대상", person_id=shared)
    bystander = _make_person(db_session, display_name="동숫자구경")

    def trace(step: str, tool: str, input_: Any, output: Any) -> AgentTrace:
        row = AgentTrace(
            session_id="p2b-u2-decoy",
            step=step,
            tool_name=tool,
            input=to_jsonable(input_),
            output=to_jsonable(output),
            tokens_in=0,
            tokens_out=0,
        )
        db_session.add(row)
        db_session.flush()
        return row

    event_out = EventOut(
        id=shared, person_id=bystander.id, type="meal", content="x", occurred_at=NOW, created_at=NOW
    )
    schedule_out = ScheduleOut(id=shared, person_id=bystander.id, title="y", scheduled_at=NOW)
    keep = [
        trace("tool_call", "add_event", {"person_id": bystander.id}, event_out),
        trace("tool_call", "add_schedule", {"person_id": bystander.id}, schedule_out),
        trace(
            "loop_x",
            "agent_loop",
            {"person_id": bystander.id},
            {"considered_event_ids": [shared], "schedule_id": shared, "question_id": shared},
        ),
    ]
    gone = [
        # 규칙 3 만으로 잡히는 행 -- `create_person` 은 input 에 인물 id 가 없고 output 최상위 id 뿐이다.
        trace(
            "tool_call",
            "create_person",
            {"display_name": "동숫자대상", "aliases": []},
            PersonOut(id=shared, display_name="동숫자대상", relation_tag="직장", hierarchy="동", aliases=[]),
        ),
        trace(
            "tool_call",
            "update_person",
            {"person_id": shared},
            PersonOut(id=shared, display_name="동숫자대상", relation_tag="직장", hierarchy="동", aliases=[]),
        ),
        trace(
            "tool_call",
            "add_event",
            {"person_id": bystander.id},
            EventOut(
                id=1, person_id=shared, type="meal", content="x", occurred_at=NOW, created_at=NOW
            ),
        ),
    ]
    keep_question = PendingQuestion(
        session_id="p2b-u2-decoy",
        kind="schedule",
        question="언제?",
        options=["모르겠어요"],
        context={"question_id": shared, "schedule_id": shared, "event_ids": [shared]},
    )
    gone_question = PendingQuestion(
        session_id="p2b-u2-decoy",
        kind="identity",
        question="누구?",
        options=["동숫자대상", "아니요"],
        context={"candidate_ids": {"동숫자대상": shared}, "resume": {"schedule": {"person_id": shared}}},
    )
    db_session.add_all([keep_question, gone_question])
    db_session.flush()
    keep_ids = [row.id for row in keep]
    gone_ids = [row.id for row in gone]

    summary = delete_person(db_session, USER, shared, "동숫자대상")

    db_session.expire_all()
    assert summary.deleted["agent_traces"] == 3
    assert summary.deleted["pending_questions"] == 1
    assert set(
        db_session.execute(select(AgentTrace.id).where(AgentTrace.id.in_(keep_ids))).scalars()
    ) == set(keep_ids)
    assert (
        db_session.execute(select(AgentTrace.id).where(AgentTrace.id.in_(gone_ids))).scalars().all()
        == []
    )
    assert db_session.get(PendingQuestion, keep_question.id) is not None
    assert db_session.get(PendingQuestion, gone_question.id) is None
