"""Refs: P2-tools R10 S3.2 S3.6 원칙7 -- `get_briefing`: 자료 조회·
`schedule_id` 시에만 `briefed_at` 기록·문장화 없음.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다(01-plan 결정8).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db.models import AgentTrace, Event, Person, Schedule
from app.tools.briefing import get_briefing
from app.tools.context import ToolContext
from app.tools.types import PersonNotFound, ScheduleNotFound

pytestmark = pytest.mark.dbtest

_NOW = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)


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


def _ctx(
    db_session,
    *,
    session_id: str = "briefing-test",
    user_id: str = "local",
    now=lambda: _NOW,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


def _add_event(db_session, person: Person, *, occurred_at: datetime, content: str) -> Event:
    event = Event(
        person_id=person.id,
        type="meal",
        content=content,
        raw_utterance=f"raw: {content}",
        occurred_at=occurred_at,
    )
    db_session.add(event)
    db_session.flush()
    return event


def _add_schedule(
    db_session,
    person: Person,
    *,
    scheduled_at: datetime,
    title: str = "약속",
    briefed_at: datetime | None = None,
) -> Schedule:
    schedule = Schedule(
        person_id=person.id,
        title=title,
        scheduled_at=scheduled_at,
        briefed_at=briefed_at,
    )
    db_session.add(schedule)
    db_session.flush()
    return schedule


# -- 소유 확인 ----------------------------------------------------------------


def test_get_briefing_missing_person_raises_person_not_found(db_session):
    ctx = _ctx(db_session)

    with pytest.raises(PersonNotFound):
        get_briefing(ctx, 999_999)


def test_get_briefing_other_user_person_raises_person_not_found(db_session):
    other_person = _make_person(db_session, user_id="other-user")
    ctx = _ctx(db_session, user_id="local")

    with pytest.raises(PersonNotFound):
        get_briefing(ctx, other_person.id)


# -- facts --------------------------------------------------------------------


def test_get_briefing_includes_all_facts_sorted_by_updated_at_desc(db_session):
    from app.db.models import PersonFact

    person = _make_person(db_session)
    older = PersonFact(
        person_id=person.id,
        key="생일",
        value="3월",
        confidence=1.0,
        updated_at=_NOW - timedelta(days=10),
    )
    newer = PersonFact(
        person_id=person.id,
        key="회사",
        value="A사",
        confidence=1.0,
        updated_at=_NOW - timedelta(days=1),
    )
    db_session.add_all([older, newer])
    db_session.flush()
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert [f["key"] for f in result.facts] == ["회사", "생일"]
    assert result.facts[0]["value"] == "A사"
    assert result.facts[0]["confidence"] == 1.0
    assert "updated_at" in result.facts[0]


# -- recent_events -------------------------------------------------------------


def test_get_briefing_returns_only_top5_events_desc_without_raw_utterance(db_session):
    person = _make_person(db_session)
    for i in range(6):
        _add_event(
            db_session,
            person,
            occurred_at=_NOW - timedelta(days=i),
            content=f"내용{i}",
        )
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert len(result.recent_events) == 5
    contents = [e.content for e in result.recent_events]
    assert contents == ["내용0", "내용1", "내용2", "내용3", "내용4"]  # 최신순, 가장 오래된 내용5 제외

    for e in result.to_dict()["recent_events"]:
        assert "raw_utterance" not in e


# -- upcoming_schedules ---------------------------------------------------------


def test_get_briefing_upcoming_schedules_excludes_past_and_caps_at_3_asc(db_session):
    person = _make_person(db_session)
    _add_schedule(db_session, person, scheduled_at=_NOW - timedelta(days=1), title="과거")
    future_titles = ["미래1", "미래2", "미래3", "미래4"]
    for i, title in enumerate(future_titles, start=1):
        _add_schedule(db_session, person, scheduled_at=_NOW + timedelta(days=i), title=title)
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert len(result.upcoming_schedules) == 3
    assert [s.title for s in result.upcoming_schedules] == ["미래1", "미래2", "미래3"]


# -- schedule_id: 읽기 전용 vs 기록 ----------------------------------------------


def test_get_briefing_without_schedule_id_does_not_write_any_briefed_at(db_session):
    person = _make_person(db_session)
    s1 = _add_schedule(db_session, person, scheduled_at=_NOW + timedelta(days=1))
    s2 = _add_schedule(db_session, person, scheduled_at=_NOW + timedelta(days=2))
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert result.schedule is None
    db_session.expire_all()
    assert db_session.get(Schedule, s1.id).briefed_at is None
    assert db_session.get(Schedule, s2.id).briefed_at is None


def test_get_briefing_with_schedule_id_marks_only_that_schedule_briefed(db_session):
    person = _make_person(db_session)
    target = _add_schedule(db_session, person, scheduled_at=_NOW + timedelta(days=1))
    other = _add_schedule(db_session, person, scheduled_at=_NOW + timedelta(days=2))
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id, schedule_id=target.id)

    assert result.schedule is not None
    assert result.schedule.id == target.id
    assert result.schedule.briefed_at == _NOW

    db_session.expire_all()
    assert db_session.get(Schedule, target.id).briefed_at == _NOW
    assert db_session.get(Schedule, other.id).briefed_at is None


def test_get_briefing_schedule_id_overwrites_existing_briefed_at(db_session):
    person = _make_person(db_session)
    target = _add_schedule(
        db_session,
        person,
        scheduled_at=_NOW + timedelta(days=1),
        briefed_at=_NOW - timedelta(days=5),
    )
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id, schedule_id=target.id)

    assert result.schedule.briefed_at == _NOW


def test_get_briefing_schedule_id_of_other_person_raises_schedule_not_found(db_session):
    person = _make_person(db_session, display_name="김철수")
    other_person = _make_person(db_session, display_name="이영희")
    other_schedule = _add_schedule(db_session, other_person, scheduled_at=_NOW + timedelta(days=1))
    ctx = _ctx(db_session)

    with pytest.raises(ScheduleNotFound):
        get_briefing(ctx, person.id, schedule_id=other_schedule.id)


def test_get_briefing_missing_schedule_id_raises_schedule_not_found(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    with pytest.raises(ScheduleNotFound):
        get_briefing(ctx, person.id, schedule_id=999_999)


# -- generated_at, 키 집합(원칙7 경계), trace ------------------------------------


def test_get_briefing_generated_at_equals_ctx_now(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert result.generated_at == _NOW


def test_get_briefing_to_dict_key_set_has_no_sentence_fields(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session)

    result = get_briefing(ctx, person.id)

    assert set(result.to_dict().keys()) == {
        "person",
        "aliases",
        "facts",
        "recent_events",
        "upcoming_schedules",
        "schedule",
        "generated_at",
    }
    for forbidden in ("summary", "suggestion", "advice"):
        assert forbidden not in result.to_dict()


def test_get_briefing_writes_exactly_one_agent_trace_row(db_session):
    person = _make_person(db_session)
    ctx = _ctx(db_session, session_id="trace-briefing-1")

    get_briefing(ctx, person.id)

    traces = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-briefing-1")
        ).scalars()
    )
    assert len(traces) == 1
    assert traces[0].step == "tool_call"
    assert traces[0].tool_name == "get_briefing"
