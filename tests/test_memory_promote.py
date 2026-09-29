"""Refs: P6-memory S3.5 S3.1 R8 원칙8 원칙9 -- U5 `app/memory/promote.py`
테스트.

01-plan 판정 표 10~14행(양성·트리거 경계·재승격 방지·원문 불변·추출기
거부) + 위임 프롬프트가 요구한 추가 케이스(소유·세션 경계·미달 이벤트
영구 소실 방지·D-6 세 갈래·오래된 순 20건 상한·trace 모양)를 검증한다.
`FakeFactExtractor`(결정 D-3, 표 기반·결정적)로만 돌아 실 키·네트워크가
없다(원칙8). 실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처
(`db_session`, `dbtest` 마커)를 쓴다 -- `tests/test_memory_patterns.py` 와
같은 관례(모듈 전체 `pytestmark` 대신 테스트마다 마커를 붙인다, 이 파일은
전부 DB 를 쓰지만 형식을 그대로 맞춘다).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

import app.settings as settings
from app.db.models import AgentTrace, Event, FactSource, Person, PersonFact
from app.memory.extract import FakeFactExtractor
from app.memory.promote import promote_person
from app.memory.types import MEMORY_TRACE_TOOL_NAME, STEP_MEMORY_PROMOTE, Extraction
from app.tools.context import ToolContext
from app.tools.types import PersonNotFound

NOW = datetime(2026, 9, 29, 4, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 헬퍼 (tests/test_memory_patterns.py 와 같은 관례)
# ---------------------------------------------------------------------------


def _make_person(
    db_session,
    *,
    user_id: str = "local",
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


def _ctx(
    db_session,
    *,
    session_id: str = "promote-test",
    user_id: str = "local",
    now=lambda: NOW,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


def _add_event(
    db_session,
    person: Person,
    *,
    event_type: str = "personal_share",
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


def _add_events(
    db_session,
    person: Person,
    count: int,
    *,
    start_days_ago: int = 50,
    step_days: int = 5,
    event_type: str = "personal_share",
) -> list[Event]:
    """`count`건을 오래된 순으로(`start_days_ago`일 전부터 `step_days`일
    간격으로 최근 쪽으로) 만든다 -- 반환 목록도 오래된 순이다."""

    events = []
    for i in range(count):
        when = NOW - timedelta(days=start_days_ago - i * step_days)
        events.append(
            _add_event(db_session, person, event_type=event_type, occurred_at=when, content=f"내용{i}")
        )
    return events


def _promote_traces(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .where(AgentTrace.tool_name == MEMORY_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_MEMORY_PROMOTE)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


def _person_facts(db_session, person: Person) -> list[PersonFact]:
    return list(
        db_session.execute(select(PersonFact).where(PersonFact.person_id == person.id)).scalars().all()
    )


def _linked_event_ids(db_session, fact: PersonFact) -> set[int]:
    return set(
        db_session.execute(select(FactSource.event_id).where(FactSource.fact_id == fact.id)).scalars().all()
    )


@dataclass
class _CapturingExtractor:
    """`existing_facts` 가 실제로 무엇을 받았는지 확인하기 위한 테스트
    전용 `FactExtractor` -- `FakeFactExtractor` 는 이벤트 id 집합으로만
    키를 매기고 `existing_facts`/`person` 을 무시하므로 이 검사에는 쓸 수
    없다(`test_memory_extract.py::test_fake_fact_extractor_ignores_
    existing_facts_and_person_for_keying` 가 그 사실 자체를 고정한다)."""

    captured: list = field(default_factory=list)

    def extract(self, person, existing_facts, events) -> Extraction:
        self.captured.append((person, list(existing_facts), list(events)))
        return Extraction(facts=[], provider="capturing")


# ---------------------------------------------------------------------------
# 판정 표 10행 -- 양성: 미승격 5건 + 가짜 추출기 사실 2개
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_five_unpromoted_events_creates_facts_with_source_links(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]
    before = {e.id: (e.content, e.raw_utterance) for e in events}

    extractor = FakeFactExtractor(
        table={
            frozenset(ids): [
                {"key": "hobby", "value": "등산", "source_event_ids": [ids[0], ids[1]]},
                {"key": "job", "value": "개발자", "source_event_ids": [ids[2]]},
            ]
        }
    )

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    assert extractor.call_count == 1
    assert result.unpromoted_count == 5
    assert set(result.considered_event_ids) == set(ids)
    assert len(result.facts) == 2

    facts = {pf.key: pf for pf in _person_facts(db_session, person)}
    assert facts["hobby"].value == "등산"
    assert _linked_event_ids(db_session, facts["hobby"]) == {ids[0], ids[1]}
    assert facts["job"].value == "개발자"
    assert _linked_event_ids(db_session, facts["job"]) == {ids[2]}

    after = {
        e.id: (e.content, e.raw_utterance)
        for e in db_session.execute(select(Event).where(Event.id.in_(ids))).scalars().all()
    }
    assert after == before


# ---------------------------------------------------------------------------
# 판정 표 11행 -- 트리거 경계(부정): 미승격 4건
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_four_unpromoted_events_does_not_trigger(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    _add_events(db_session, person, 4)
    extractor = FakeFactExtractor(table={})

    result = promote_person(ctx, person.id, extractor)

    assert result is None
    assert extractor.call_count == 0
    assert _person_facts(db_session, person) == []


# ---------------------------------------------------------------------------
# 판정 표 12행 -- 재승격 방지: 5건 승격 후 1건 추가(미승격 1)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_does_not_recount_already_considered_events(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]

    extractor_first = FakeFactExtractor(table={frozenset(ids): []})
    result_first = promote_person(ctx, person.id, extractor_first)
    assert result_first is not None
    assert extractor_first.call_count == 1

    _add_event(db_session, person, occurred_at=NOW - timedelta(days=1))

    extractor_second = FakeFactExtractor(table={})
    result_second = promote_person(ctx, person.id, extractor_second)

    assert result_second is None
    assert extractor_second.call_count == 0


# ---------------------------------------------------------------------------
# ★3 -- 미달 호출로 "본" 이벤트가 영구히 미승격에서 사라지지 않는다
# (considered_event_ids 를 미달 호출에서 채웠다면 이 테스트가 실패한다)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_unpromoted_events_are_not_lost_when_trigger_not_yet_met(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 4)

    extractor_first = FakeFactExtractor(table={})
    result_first = promote_person(ctx, person.id, extractor_first)
    assert result_first is None
    assert extractor_first.call_count == 0

    fifth = _add_event(db_session, person, occurred_at=NOW - timedelta(days=1))
    all_ids = [e.id for e in events] + [fifth.id]

    extractor_second = FakeFactExtractor(
        table={frozenset(all_ids): [{"key": "hobby", "value": "등산", "source_event_ids": [fifth.id]}]}
    )
    result_second = promote_person(ctx, person.id, extractor_second)

    assert result_second is not None
    assert extractor_second.call_count == 1
    assert set(result_second.considered_event_ids) == set(all_ids)


# ---------------------------------------------------------------------------
# 결정 D-6 -- 값이 같으면 링크만 추가
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_upsert_same_value_only_adds_link(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    existing = PersonFact(person_id=person.id, key="hobby", value="등산", confidence=1.0)
    db_session.add(existing)
    db_session.flush()
    existing_id = existing.id

    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]
    extractor = FakeFactExtractor(
        table={frozenset(ids): [{"key": "hobby", "value": "등산", "source_event_ids": [ids[-1]]}]}
    )

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    assert len(result.facts) == 1
    promoted = result.facts[0]
    assert promoted.action == "same"
    assert promoted.fact_id == existing_id
    assert promoted.previous_value is None

    fact = db_session.get(PersonFact, existing_id)
    assert fact.value == "등산"
    assert _linked_event_ids(db_session, fact) == {ids[-1]}


# ---------------------------------------------------------------------------
# 결정 D-6 -- 값이 다르면 덮어쓰고 링크를 교체, 이전 값은 trace 에 남는다
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_upsert_different_value_overwrites_and_replaces_links(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]

    existing = PersonFact(person_id=person.id, key="hobby", value="등산", confidence=1.0)
    db_session.add(existing)
    db_session.flush()
    existing_id = existing.id
    db_session.add(FactSource(fact_id=existing_id, event_id=ids[-1]))
    db_session.flush()

    extractor = FakeFactExtractor(
        table={frozenset(ids): [{"key": "hobby", "value": "등산, 클라이밍", "source_event_ids": [ids[0]]}]}
    )

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    promoted = result.facts[0]
    assert promoted.action == "updated"
    assert promoted.fact_id == existing_id
    assert promoted.previous_value == "등산"

    fact = db_session.get(PersonFact, existing_id)
    assert fact.value == "등산, 클라이밍"
    assert _linked_event_ids(db_session, fact) == {ids[0]}

    trace = _promote_traces(db_session, ctx.session_id)[-1]
    changed = trace.output["facts"][0]
    assert changed["previous_value"] == "등산"
    assert changed["action"] == "updated"


# ---------------------------------------------------------------------------
# 판정 표 13행 -- 원문 불변(트리거·비트리거 호출 둘 다)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_does_not_touch_event_rows(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]
    before = {e.id: (e.content, e.raw_utterance, e.occurred_at) for e in events}
    before_total = len(db_session.execute(select(Event)).scalars().all())

    extractor = FakeFactExtractor(
        table={frozenset(ids): [{"key": "hobby", "value": "등산", "source_event_ids": [ids[0]]}]}
    )
    promote_person(ctx, person.id, extractor)
    # 새 이벤트 없이 재호출(트리거 미달 경로) -- 이것도 원문을 건드리지
    # 않는지 함께 확인한다.
    promote_person(ctx, person.id, FakeFactExtractor(table={}))

    after = {
        e.id: (e.content, e.raw_utterance, e.occurred_at)
        for e in db_session.execute(select(Event).where(Event.id.in_(ids))).scalars().all()
    }
    assert after == before
    after_total = len(db_session.execute(select(Event)).scalars().all())
    assert after_total == before_total


# ---------------------------------------------------------------------------
# 판정 표 14행 -- 추출기 거부: 사실 단위 거부, 나머지는 저장
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_rejects_invalid_facts_but_keeps_valid_ones(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]

    extractor = FakeFactExtractor(
        table={
            frozenset(ids): [
                {"key": "hobby", "value": "등산", "source_event_ids": [ids[0]]},
                {"key": "pattern:meal", "value": "3회", "source_event_ids": [ids[1]]},
                {"key": "not_a_real_key", "value": "x", "source_event_ids": [ids[1]]},
                {"key": "job", "value": "   ", "source_event_ids": [ids[2]]},
                {"key": "likes", "value": "치킨", "source_event_ids": [999999]},
            ]
        }
    )

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    assert len(result.facts) == 1
    assert result.facts[0].key == "hobby"
    assert len(result.rejected) == 4
    assert {r.reason for r in result.rejected} == {
        "pattern_prefix",
        "key_not_in_vocab",
        "empty_value",
        "unknown_event_id",
    }

    facts = _person_facts(db_session, person)
    assert len(facts) == 1
    assert facts[0].key == "hobby"


# ---------------------------------------------------------------------------
# 요구 6 -- 오래된 순 20건 상한
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_caps_batch_at_oldest_twenty_events(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 25, start_days_ago=100, step_days=2)
    ids_oldest_first = [e.id for e in events]
    oldest_twenty = ids_oldest_first[:20]

    extractor = FakeFactExtractor(
        table={frozenset(oldest_twenty): [{"key": "hobby", "value": "등산", "source_event_ids": [oldest_twenty[0]]}]}
    )

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    assert extractor.call_count == 1
    assert result.unpromoted_count == 25
    assert len(result.considered_event_ids) == 20
    assert set(result.considered_event_ids) == set(oldest_twenty)


# ---------------------------------------------------------------------------
# 요구 7 -- trace 모양(결정 F) + min_events 재현성(R-14)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_trace_output_matches_decision_f_schema(db_session) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]
    extractor = FakeFactExtractor(
        table={frozenset(ids): [{"key": "hobby", "value": "등산", "source_event_ids": [ids[0]]}]}
    )

    promote_person(ctx, person.id, extractor)

    trace = _promote_traces(db_session, ctx.session_id)[-1]
    output = trace.output
    assert set(output.keys()) == {
        "person_id",
        "unpromoted_count",
        "min_events",
        "considered_event_ids",
        "facts",
        "rejected",
        "llm",
    }
    assert output["person_id"] == person.id
    assert output["unpromoted_count"] == 5
    assert output["min_events"] == 5
    assert set(output["considered_event_ids"]) == set(ids)
    assert output["llm"]["provider"] == "fake"
    assert trace.tokens_in == 0
    assert trace.tokens_out == 0


@pytest.mark.dbtest
def test_promote_person_trace_records_min_events_from_env_override(
    db_session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MEMORY_PROMOTE_MIN_EVENTS", "2")
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    events = _add_events(db_session, person, 2)
    ids = [e.id for e in events]
    extractor = FakeFactExtractor(table={frozenset(ids): []})

    result = promote_person(ctx, person.id, extractor)

    assert result is not None
    assert extractor.call_count == 1
    trace = _promote_traces(db_session, ctx.session_id)[-1]
    assert trace.output["min_events"] == 2


@pytest.mark.dbtest
def test_promote_person_non_trigger_trace_records_reason_and_empty_considered(db_session) -> None:
    """★1·★2·★3 을 한 번에 고정한다 -- 미달 호출도 trace 행을 쓰되(★1),
    `unpromoted_count`/`min_events` 로 "왜 승격하지 않았나"가 남고(★2),
    `considered_event_ids` 는 반드시 빈 목록이다(★3, 이벤트 영구 소실
    방지)."""

    person = _make_person(db_session)
    ctx = _ctx(db_session)
    _add_events(db_session, person, 4)
    extractor = FakeFactExtractor(table={})

    result = promote_person(ctx, person.id, extractor)

    assert result is None
    assert extractor.call_count == 0

    trace = _promote_traces(db_session, ctx.session_id)[-1]
    output = trace.output
    assert output["unpromoted_count"] == 4
    assert output["min_events"] == 5
    assert output["considered_event_ids"] == []
    assert output["facts"] == []
    assert output["rejected"] == []
    assert output["llm"] == {"provider": None, "model": None}
    assert trace.tokens_in == 0
    assert trace.tokens_out == 0


# ---------------------------------------------------------------------------
# 요구 1 -- 소유 확인(security §5)
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_other_users_person_raises_person_not_found_without_calling_extractor(
    db_session,
) -> None:
    owner_person = _make_person(db_session, user_id="owner")
    _add_events(db_session, owner_person, 5)
    ctx_intruder = _ctx(db_session, user_id="intruder")
    extractor = FakeFactExtractor(table={})

    with pytest.raises(PersonNotFound):
        promote_person(ctx_intruder, owner_person.id, extractor)

    assert extractor.call_count == 0
    assert _person_facts(db_session, owner_person) == []


# ---------------------------------------------------------------------------
# 요구 2 -- 세션 경계(session_id 와 무관하게 누적 조회, 결정 B(ii))
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_ignores_session_id_when_counting_considered_events(db_session) -> None:
    person = _make_person(db_session)
    events = _add_events(db_session, person, 5)
    ids = [e.id for e in events]

    ctx_s1 = _ctx(db_session, session_id="promote-s1")
    extractor_s1 = FakeFactExtractor(table={frozenset(ids): []})
    result_s1 = promote_person(ctx_s1, person.id, extractor_s1)
    assert result_s1 is not None
    assert extractor_s1.call_count == 1

    ctx_s2 = _ctx(db_session, session_id="promote-s2")
    extractor_s2 = FakeFactExtractor(table={})
    result_s2 = promote_person(ctx_s2, person.id, extractor_s2)

    assert result_s2 is None
    assert extractor_s2.call_count == 0


# ---------------------------------------------------------------------------
# 부가 -- existing_facts 에 pattern: 접두 사실을 넘기지 않는다
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_promote_person_excludes_pattern_prefixed_facts_from_existing_facts_sent_to_extractor(
    db_session,
) -> None:
    person = _make_person(db_session)
    ctx = _ctx(db_session)
    db_session.add_all(
        [
            PersonFact(person_id=person.id, key="hobby", value="등산", confidence=1.0),
            PersonFact(
                person_id=person.id,
                key=f"{settings.PATTERN_KEY_PREFIX}conflict",
                value="3회 (2026-01-01)",
                confidence=1.0,
            ),
        ]
    )
    db_session.flush()
    _add_events(db_session, person, 5)

    extractor = _CapturingExtractor()
    promote_person(ctx, person.id, extractor)

    assert len(extractor.captured) == 1
    _, existing_facts, _ = extractor.captured[0]
    keys = {fact.key for fact in existing_facts}
    assert keys == {"hobby"}
