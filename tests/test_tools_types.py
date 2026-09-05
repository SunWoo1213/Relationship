"""Refs: P2-tools S3.2 -- DB 없이 도는 순수 단위 테스트.

`app/tools/types.py` 의 `to_dict()` 직렬화, 예외 계층 상속, `ALIAS_SOURCES`
값 집합(3값, `EVENT_TYPES` 와 겹치지 않음)을 검증한다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import ALIAS_SOURCES, EVENT_TYPES
from app.tools.types import (
    BriefingOut,
    Candidate,
    ConfirmationRequired,
    EventOut,
    InvalidValue,
    PendingQuestionOut,
    PersonNotFound,
    PersonOut,
    QuestionNotAnswerable,
    QuestionNotFound,
    ScheduleNotFound,
    ScheduleOut,
    ToolError,
)


def test_person_out_to_dict_is_json_serializable_shape():
    person = PersonOut(
        id=1, display_name="김팀장", relation_tag="직장", hierarchy="상", aliases=["팀장님"]
    )
    assert person.to_dict() == {
        "id": 1,
        "display_name": "김팀장",
        "relation_tag": "직장",
        "hierarchy": "상",
        "aliases": ["팀장님"],
    }


def test_candidate_to_dict_nests_person_and_flags():
    person = PersonOut(id=2, display_name="이대리", relation_tag="직장", hierarchy="동", aliases=[])
    candidate = Candidate(
        person=person,
        similarity=0.87,
        aliases_matched=["이대리"],
        rule_flags={"hierarchy_match": True, "relation_tag_match": False},
    )
    d = candidate.to_dict()
    assert d["person"] == person.to_dict()
    assert d["similarity"] == 0.87
    assert d["aliases_matched"] == ["이대리"]
    assert d["rule_flags"] == {"hierarchy_match": True, "relation_tag_match": False}


def test_event_out_to_dict_serializes_datetime_isoformat():
    when = datetime(2026, 5, 1, 9, 30, tzinfo=timezone.utc)
    created = datetime(2026, 5, 1, 9, 31, tzinfo=timezone.utc)
    event = EventOut(
        id=10, person_id=2, type="meal", content="점심", occurred_at=when, created_at=created
    )
    assert event.to_dict() == {
        "id": 10,
        "person_id": 2,
        "type": "meal",
        "content": "점심",
        "occurred_at": when.isoformat(),
        "created_at": created.isoformat(),
    }


def test_schedule_out_to_dict_handles_missing_briefed_at():
    when = datetime(2026, 6, 1, tzinfo=timezone.utc)
    schedule = ScheduleOut(id=5, person_id=2, title="회식", scheduled_at=when)
    d = schedule.to_dict()
    assert d["briefed_at"] is None
    assert d["scheduled_at"] == when.isoformat()


def test_schedule_out_to_dict_includes_briefed_at_when_set():
    when = datetime(2026, 6, 1, tzinfo=timezone.utc)
    briefed = datetime(2026, 6, 2, tzinfo=timezone.utc)
    schedule = ScheduleOut(id=5, person_id=2, title="회식", scheduled_at=when, briefed_at=briefed)
    assert schedule.to_dict()["briefed_at"] == briefed.isoformat()


def test_pending_question_out_to_dict():
    pq = PendingQuestionOut(
        question_id=7,
        status="pending",
        kind="new_person",
        question="기억할까요?",
        options=["네", "아니오"],
    )
    assert pq.to_dict() == {
        "question_id": 7,
        "status": "pending",
        "kind": "new_person",
        "question": "기억할까요?",
        "options": ["네", "아니오"],
    }


def test_briefing_out_to_dict_nests_lists():
    """U7 이 `generated_at`(필수)·`aliases`·`schedule` 을 추가했다(01-plan
    결정 7). 이 테스트는 U2 시점의 골격 형태를 U7 의 실제 필드 집합으로
    갱신한다."""
    person = PersonOut(id=3, display_name="박부장", relation_tag="직장", hierarchy="상", aliases=["부장님"])
    when = datetime(2026, 7, 1, tzinfo=timezone.utc)
    briefing = BriefingOut(
        person=person,
        generated_at=when,
        aliases=["부장님"],
        facts=[{"key": "생일", "value": "3월"}],
        recent_events=[
            EventOut(id=1, person_id=3, type="meal", content="점심", occurred_at=when, created_at=when)
        ],
        upcoming_schedules=[ScheduleOut(id=1, person_id=3, title="회의", scheduled_at=when)],
    )
    d = briefing.to_dict()
    assert d["person"] == person.to_dict()
    assert d["aliases"] == ["부장님"]
    assert d["facts"] == [{"key": "생일", "value": "3월"}]
    assert d["recent_events"][0]["type"] == "meal"
    assert d["upcoming_schedules"][0]["title"] == "회의"
    assert d["schedule"] is None
    assert d["generated_at"] == when.isoformat()


def test_briefing_out_to_dict_includes_schedule_when_set():
    person = PersonOut(id=3, display_name="박부장", relation_tag="직장", hierarchy="상", aliases=[])
    when = datetime(2026, 7, 1, tzinfo=timezone.utc)
    schedule = ScheduleOut(id=9, person_id=3, title="브리핑용 일정", scheduled_at=when, briefed_at=when)
    briefing = BriefingOut(person=person, generated_at=when, schedule=schedule)

    assert briefing.to_dict()["schedule"] == schedule.to_dict()


def test_schedule_not_found_inherits_tool_error():
    assert issubclass(ScheduleNotFound, ToolError)


def test_exception_hierarchy_all_inherit_tool_error():
    for exc_cls in (
        PersonNotFound,
        QuestionNotFound,
        QuestionNotAnswerable,
        ConfirmationRequired,
        InvalidValue,
        ScheduleNotFound,
    ):
        assert issubclass(exc_cls, ToolError)
    assert issubclass(ToolError, Exception)


def test_tool_error_message_is_short_code_like_string():
    err = PersonNotFound("person_not_found")
    assert str(err) == "person_not_found"


def test_alias_sources_has_three_values_distinct_from_event_types():
    assert ALIAS_SOURCES == ("user_said", "confirmed", "system")
    assert len(ALIAS_SOURCES) == 3
    assert set(ALIAS_SOURCES).isdisjoint(set(EVENT_TYPES))
