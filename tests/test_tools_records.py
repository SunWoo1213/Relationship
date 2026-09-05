"""Refs: P2-tools R10 S3.1 S3.2 -- `add_event`·`add_schedule` 값 집합·
`raw_utterance` 원문 보존·tz-aware 시각 요구·타 사용자 차단·패턴 감지 없음.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db.models import EVENT_TYPES, AgentTrace, Person, PersonFact
from app.tools.context import ToolContext
from app.tools.records import add_event, add_schedule
from app.tools.types import InvalidValue, PersonNotFound

pytestmark = pytest.mark.dbtest


def _make_person(
    db_session,
    *,
    user_id: str = "local",
    display_name: str = "김철수",
    relation_tag: str = "지인",
    hierarchy: str = "동",
) -> Person:
    person = Person(
        user_id=user_id,
        display_name=display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )
    db_session.add(person)
    db_session.flush()
    return person


def _ctx(db_session, *, session_id: str = "records-test", user_id: str = "local") -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id)


_AWARE_NOW = datetime(2026, 5, 1, 9, 30, tzinfo=timezone.utc)
_KST = timezone(timedelta(hours=9))


# -- add_event -------------------------------------------------------------


@pytest.mark.parametrize("event_type", EVENT_TYPES)
def test_add_event_succeeds_for_every_event_type(db_session, event_type):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    result = add_event(
        ctx,
        person.id,
        event_type,
        content="내용",
        occurred_at=_AWARE_NOW,
        raw_utterance="원문 그대로",
    )

    assert result.type == event_type
    assert result.person_id == person.id
    assert result.id is not None


def test_add_event_invalid_type_raises_invalid_value(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        add_event(
            ctx,
            person.id,
            "존재하지않는타입",
            content="내용",
            occurred_at=_AWARE_NOW,
            raw_utterance="원문",
        )


@pytest.mark.parametrize("bad_raw_utterance", ["", "   "])
def test_add_event_blank_raw_utterance_raises_invalid_value(db_session, bad_raw_utterance):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        add_event(
            ctx,
            person.id,
            "meal",
            content="내용",
            occurred_at=_AWARE_NOW,
            raw_utterance=bad_raw_utterance,
        )


@pytest.mark.parametrize("bad_content", ["", "   "])
def test_add_event_blank_content_raises_invalid_value(db_session, bad_content):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        add_event(
            ctx,
            person.id,
            "meal",
            content=bad_content,
            occurred_at=_AWARE_NOW,
            raw_utterance="원문",
        )


def test_add_event_naive_occurred_at_raises_invalid_value(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    naive = datetime(2026, 5, 1, 9, 30)  # tzinfo 없음

    with pytest.raises(InvalidValue):
        add_event(
            ctx,
            person.id,
            "meal",
            content="내용",
            occurred_at=naive,
            raw_utterance="원문",
        )


def test_add_event_non_utc_aware_is_normalized_to_same_instant(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    kst_time = datetime(2026, 5, 1, 18, 30, tzinfo=_KST)  # == 09:30 UTC

    result = add_event(
        ctx,
        person.id,
        "meal",
        content="내용",
        occurred_at=kst_time,
        raw_utterance="원문",
    )

    assert result.occurred_at == kst_time  # 같은 순간(instant)
    assert result.occurred_at.utcoffset() == timedelta(0)  # UTC 로 정규화 저장


def test_add_event_other_user_person_raises_person_not_found(db_session):
    other_person = _make_person(db_session, user_id="other-user")
    ctx = _ctx(db_session, user_id="local")

    with pytest.raises(PersonNotFound):
        add_event(
            ctx,
            other_person.id,
            "meal",
            content="내용",
            occurred_at=_AWARE_NOW,
            raw_utterance="원문",
        )


def test_add_event_missing_person_raises_person_not_found(db_session):
    ctx = _ctx(db_session)

    with pytest.raises(PersonNotFound):
        add_event(
            ctx,
            999_999,
            "meal",
            content="내용",
            occurred_at=_AWARE_NOW,
            raw_utterance="원문",
        )


def test_add_event_preserves_raw_utterance_verbatim_in_db(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    raw = "어제 저녁에 김팀장이랑 밥 먹었는데 좀 싸웠어"

    result = add_event(
        ctx,
        person.id,
        "conflict",
        content="다툼",
        occurred_at=_AWARE_NOW,
        raw_utterance=raw,
    )

    from app.db.models import Event

    row = db_session.get(Event, result.id)
    assert row.raw_utterance == raw


def test_add_event_writes_one_row_and_one_trace(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session, session_id="trace-add-event-1")

    from app.db.models import Event

    add_event(
        ctx,
        person.id,
        "meal",
        content="내용",
        occurred_at=_AWARE_NOW,
        raw_utterance="원문",
    )

    events = list(
        db_session.execute(select(Event).where(Event.person_id == person.id)).scalars()
    )
    assert len(events) == 1

    traces = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-add-event-1")
        ).scalars()
    )
    assert len(traces) == 1
    assert traces[0].step == "tool_call"
    assert traces[0].tool_name == "add_event"


def test_add_event_does_not_trigger_pattern_promotion_even_with_three_same_type(db_session):
    """원칙6·D9 경계: 같은 인물의 같은 type 이벤트 3건이 쌓여도 `add_event`
    는 패턴 감지·`person_facts` 승격을 하지 않는다(P6-memory 의 몫)."""
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    for _ in range(3):
        add_event(
            ctx,
            person.id,
            "conflict",
            content="또 다퉜다",
            occurred_at=_AWARE_NOW,
            raw_utterance="또 싸웠어",
        )

    facts = list(
        db_session.execute(select(PersonFact).where(PersonFact.person_id == person.id)).scalars()
    )
    assert facts == []


# -- add_schedule ------------------------------------------------------------


def test_add_schedule_succeeds_with_briefed_at_none(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    result = add_schedule(ctx, person.id, "저녁 약속", _AWARE_NOW)

    assert result.person_id == person.id
    assert result.title == "저녁 약속"
    assert result.briefed_at is None


@pytest.mark.parametrize("bad_title", ["", "   "])
def test_add_schedule_blank_title_raises_invalid_value(db_session, bad_title):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    with pytest.raises(InvalidValue):
        add_schedule(ctx, person.id, bad_title, _AWARE_NOW)


def test_add_schedule_naive_scheduled_at_raises_invalid_value(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    naive = datetime(2026, 5, 1, 9, 30)

    with pytest.raises(InvalidValue):
        add_schedule(ctx, person.id, "약속", naive)


def test_add_schedule_allows_past_scheduled_at(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    past = datetime(2020, 1, 1, tzinfo=timezone.utc)

    result = add_schedule(ctx, person.id, "지난 약속", past)

    assert result.scheduled_at == past


def test_add_schedule_other_user_person_raises_person_not_found(db_session):
    other_person = _make_person(db_session, user_id="other-user")
    ctx = _ctx(db_session, user_id="local")

    with pytest.raises(PersonNotFound):
        add_schedule(ctx, other_person.id, "약속", _AWARE_NOW)


def test_add_schedule_writes_one_agent_trace_row(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session, session_id="trace-add-schedule-1")

    add_schedule(ctx, person.id, "약속", _AWARE_NOW)

    traces = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-add-schedule-1")
        ).scalars()
    )
    assert len(traces) == 1
    assert traces[0].step == "tool_call"
    assert traces[0].tool_name == "add_schedule"
