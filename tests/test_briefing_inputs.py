"""Refs: P6-briefing S3.5 S3.6 D14 원칙6 원칙9 -- U3
`build_briefing_input(ctx, schedule)` 테스트(01-plan 판정 표 11~13행 +
근거 원문 상한·자격·`briefed_at` 기록·인물 격리).

`tests/test_memory_patterns.py`·`tests/test_briefing_select.py` 와 같은
관례를 따른다: 실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백
픽스처(`db_session`, `dbtest` 마커). 각 테스트는 **독립**이다 -- 행마다
새 인물·일정을 만들고 앞 테스트의 결과를 이어 쓰지 않는다(01-plan 94행
"상태: 독립" 규약). 시각은 전부 `ctx.now` 주입으로 고정한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.briefing.inputs import build_briefing_input
from app.db.models import AgentTrace, Event, FactSource, Person, PersonFact, Schedule
from app.memory.patterns import detect_patterns
from app.memory.types import MEMORY_TRACE_TOOL_NAME, STEP_MEMORY_PATTERN
from app.tools.context import ToolContext

pytestmark = pytest.mark.dbtest

_T0 = datetime(2026, 1, 1, 4, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 헬퍼 (test_briefing_select.py·test_memory_patterns.py 와 같은 이름 관례)
# ---------------------------------------------------------------------------


def _make_person(
    db_session,
    *,
    user_id: str = "brief-u3-test-user",
    display_name: str = "민수",
    relation_tag: str = "친구",
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


def _make_schedule(
    db_session,
    person: Person,
    *,
    scheduled_at: datetime,
    briefed_at: datetime | None = None,
    title: str = "저녁 약속",
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


def _add_event(
    db_session,
    person: Person,
    *,
    event_type: str = "conflict",
    occurred_at: datetime,
    content: str = "내용",
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


def _make_fact(
    db_session,
    person: Person,
    *,
    key: str,
    value: str,
    confidence: float = 0.9,
    updated_at: datetime | None = None,
) -> PersonFact:
    kwargs: dict = dict(person_id=person.id, key=key, value=value, confidence=confidence)
    if updated_at is not None:
        kwargs["updated_at"] = updated_at
    fact = PersonFact(**kwargs)
    db_session.add(fact)
    db_session.flush()
    return fact


def _ctx(
    db_session,
    *,
    session_id: str = "briefing:inputs-test",
    user_id: str = "brief-u3-test-user",
    now=lambda: _T0,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


def _pattern_fact(db_session, person: Person, event_type: str) -> PersonFact | None:
    return (
        db_session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person.id)
            .where(PersonFact.key == f"pattern:{event_type}")
        )
        .scalars()
        .one_or_none()
    )


def _pattern_traces(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.tool_name == MEMORY_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_MEMORY_PATTERN)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


# ---------------------------------------------------------------------------
# 판정 표 11행 -- 패턴 재계산(결정 K)
# ---------------------------------------------------------------------------


def test_build_briefing_input_recomputes_pattern_and_deletes_when_window_shrinks(
    db_session,
) -> None:
    person = _make_person(db_session)
    occurred = [
        _T0 - timedelta(days=364),
        _T0 - timedelta(days=200),
        _T0 - timedelta(days=10),
    ]
    for when in occurred:
        _add_event(db_session, person, event_type="conflict", occurred_at=when)

    # 사전 조건: now=_T0 에서는 3건이 창 안이라 pattern:conflict 가 있다.
    detect_patterns(_ctx(db_session, now=lambda: _T0), person.id)
    assert _pattern_fact(db_session, person, "conflict") is not None

    # 시계를 옮기면(창 = [now-365일, now]) 가장 오래된 1건이 창 밖으로
    # 밀려나 2건만 남고(min_count=3 미달) 기존 사실이 삭제돼야 한다.
    later = _T0 + timedelta(days=2)
    schedule = _make_schedule(db_session, person, scheduled_at=later)
    ctx = _ctx(db_session, now=lambda: later)

    def _event_snapshot() -> list[tuple]:
        return [
            (row.id, row.type, row.content, row.raw_utterance, row.occurred_at)
            for row in db_session.execute(
                select(Event).where(Event.person_id == person.id).order_by(Event.id)
            ).scalars()
        ]

    events_before = _event_snapshot()

    result = build_briefing_input(ctx, schedule)

    # 판정 27행(원문 불변, U8 에서 보강) -- 패턴 재계산은 사실만 지우고
    # 근거 이벤트의 원문·내용·시각은 한 글자도 바꾸지 않는다.
    db_session.expire_all()
    assert _event_snapshot() == events_before

    assert all(fact["key"] != "pattern:conflict" for fact in result.used_facts)
    assert all(fact["key"] != "pattern:conflict" for fact in result.excluded_facts)
    assert _pattern_fact(db_session, person, "conflict") is None

    trace_rows = _pattern_traces(db_session, ctx.session_id)
    assert any(
        any(
            change["type"] == "conflict" and change["action"] == "deleted"
            for change in row.output["changes"]
        )
        for row in trace_rows
    )
    assert result.pattern_trace_id == trace_rows[-1].id

    event_count = db_session.execute(
        select(func.count()).select_from(Event).where(Event.person_id == person.id)
    ).scalar_one()
    assert event_count == 3


@pytest.mark.parametrize("module_path", ["app/briefing/select.py", "app/briefing/inputs.py"])
def test_selection_and_inputs_do_not_import_llm_or_embedding(module_path: str) -> None:
    """01-plan "지킬 불변식" ③(U8 에서 보강) -- 대상 선정·입력 조립은 규칙과
    SQL 뿐이다(원칙6 "패턴 판정은 규칙, LLM 은 문장화만"). 두 모듈의 실제
    import 문(docstring 언급 제외)에 LLM·임베딩·생성기 모듈이 없어야 한다."""

    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / module_path).read_text(encoding="utf-8")
    imported: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)

    forbidden = ("app.er", "app.embedding", "app.briefing.compose", "anthropic", "openai", "google")
    offending = [name for name in imported if name.split(".")[0] in forbidden or name.startswith(forbidden)]
    assert imported, "import 문을 하나도 못 찾았다 -- 검사 자체가 깨졌다"
    assert offending == []


# ---------------------------------------------------------------------------
# 판정 표 12행 -- 사실 세 출처(결정 F)
# ---------------------------------------------------------------------------


def test_build_briefing_input_keeps_pattern_and_fact_key_excludes_legacy_key(
    db_session,
) -> None:
    person = _make_person(db_session)
    for i in range(3):
        _add_event(
            db_session,
            person,
            event_type="meal",
            occurred_at=_T0 - timedelta(days=10 * i + 1),
        )
    _make_fact(db_session, person, key="workplace", value="네이버")
    _make_fact(db_session, person, key="소속", value="네이버")

    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))
    ctx = _ctx(db_session)

    result = build_briefing_input(ctx, schedule)

    used_keys = {fact["key"] for fact in result.used_facts}
    assert used_keys == {"pattern:meal", "workplace"}

    excluded = {(fact["key"], fact["reason"]) for fact in result.excluded_facts}
    assert ("소속", "not_fact_key") in excluded


# ---------------------------------------------------------------------------
# 판정 표 13행 -- 같은 키 여러 행은 updated_at desc 첫 행만
#
# Refs: FIX-020 -- `person_facts` 에 `UNIQUE(person_id, key)` 제약이
# 생겨(0002 리비전) 같은 키의 두 번째 행을 **만드는 것 자체가** DB
# 수준에서 막힌다. 이 테스트는 원래 그 전제(같은 키 행이 둘 있는 상태)를
# 직접 만들어 `build_briefing_input` 의 "최신 행만 used_facts, 나머지는
# superseded_by_newer" 방어 분기(app/briefing/inputs.py, 결정 F)를
# 검증했지만, FIX-020 이후로는 그 전제 자체를 재현할 수 없다(같은 세션
# 안에서도 두 번째 INSERT 가 즉시 `IntegrityError` 로 끝난다 -- Postgres
# UNIQUE 제약은 커밋을 기다리지 않고 문장 단위로 검사한다). 방어 분기
# 코드 자체(app/briefing/inputs.py)는 FIX-020 범위 밖이라 건드리지
# 않는다 -- 대신 이 테스트는 그 전제가 이제 DB 제약으로 원천 차단됨을
# 확인한다(dead code 가 된 분기를 "실행해서" 증명할 수 없다는 뜻이지,
# 그 분기가 틀렸다는 뜻은 아니다).
# ---------------------------------------------------------------------------


def test_person_facts_same_key_second_insert_rejected_by_unique_constraint(db_session) -> None:
    person = _make_person(db_session)
    _make_fact(
        db_session, person, key="likes", value="사진찍기", updated_at=_T0 - timedelta(days=5)
    )

    with pytest.raises(IntegrityError, match="uq_person_facts_person_id_key"):
        _make_fact(db_session, person, key="likes", value="등산", updated_at=_T0)


# ---------------------------------------------------------------------------
# 근거 원문 상한·자격(결정 G)
# ---------------------------------------------------------------------------


def test_build_briefing_input_attaches_up_to_two_recent_sources_and_marks_eligibility(
    db_session,
) -> None:
    person = _make_person(db_session)
    fact_linked = _make_fact(db_session, person, key="hobby", value="등산")
    oldest = _add_event(
        db_session,
        person,
        event_type="personal_share",
        occurred_at=_T0 - timedelta(days=30),
        content="오래전",
    )
    middle = _add_event(
        db_session,
        person,
        event_type="personal_share",
        occurred_at=_T0 - timedelta(days=10),
        content="중간",
    )
    newest = _add_event(
        db_session,
        person,
        event_type="personal_share",
        occurred_at=_T0 - timedelta(days=1),
        content="가장 최근",
    )
    for event in (oldest, middle, newest):
        db_session.add(FactSource(fact_id=fact_linked.id, event_id=event.id))
    db_session.flush()

    _make_fact(db_session, person, key="job", value="백엔드 개발자")

    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)

    result = build_briefing_input(ctx, schedule)

    linked = next(fact for fact in result.used_facts if fact["key"] == "hobby")
    assert linked["eligible"] is True
    assert len(linked["sources"]) == 2
    assert [source["event_id"] for source in linked["sources"]] == [newest.id, middle.id]
    assert linked["sources"][0]["raw_utterance"] == newest.raw_utterance

    unlinked = next(fact for fact in result.used_facts if fact["key"] == "job")
    assert unlinked["eligible"] is False
    assert unlinked["sources"] == []


# ---------------------------------------------------------------------------
# briefed_at 기록 (get_briefing 그대로 호출됨을 확인)
# ---------------------------------------------------------------------------


def test_build_briefing_input_records_briefed_at(db_session) -> None:
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)

    build_briefing_input(ctx, schedule)

    db_session.refresh(schedule)
    assert schedule.briefed_at == _T0


# ---------------------------------------------------------------------------
# 다른 인물 격리
# ---------------------------------------------------------------------------


def test_build_briefing_input_does_not_leak_other_person_data(db_session) -> None:
    person_a = _make_person(db_session, user_id="brief-u3-a")
    person_b = _make_person(db_session, user_id="brief-u3-b", display_name="영희")
    _make_fact(db_session, person_b, key="hobby", value="독서")
    _add_event(db_session, person_b, event_type="meal", occurred_at=_T0 - timedelta(days=1))

    _make_fact(db_session, person_a, key="job", value="디자이너")
    schedule_a = _make_schedule(db_session, person_a, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session, user_id="brief-u3-a")

    result = build_briefing_input(ctx, schedule_a)

    used_keys = {fact["key"] for fact in result.used_facts}
    assert used_keys == {"job"}
    assert result.person_id == person_a.id

    b_fact = (
        db_session.execute(select(PersonFact).where(PersonFact.person_id == person_b.id))
        .scalars()
        .one()
    )
    assert b_fact.value == "독서"

    b_event_count = db_session.execute(
        select(func.count()).select_from(Event).where(Event.person_id == person_b.id)
    ).scalar_one()
    assert b_event_count == 1
