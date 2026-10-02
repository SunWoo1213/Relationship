"""Refs: P6-briefing S3.6 S3.2 R12 원칙7 원칙9 -- U5 `run_briefings()`
테스트(01-plan 판정 표 21~24·27행 + 재실행 멱등·`schedule_id` 지정
모드·대상 0건).

`tests/test_briefing_select.py`·`test_briefing_inputs.py` 와 같은 관례:
실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`,
`dbtest` 마커). 각 테스트는 **독립**이다 -- 행마다 새 인물·일정을 만들고
앞 테스트의 결과를 이어 쓰지 않는다. 실 키·네트워크 없이 돈다(원칙8) --
`FakeBriefingComposer`(결정적 표 기반, `app/briefing/compose.py`)와 이
파일의 `_ScriptedComposer`(토큰·제공자 메타데이터까지 지정해야 하는
판정 23행 전용)만 쓴다. `agent_traces` 조회는 `app/memory/promote.py`
119행의 선례(`AgentTrace.output["person_id"].astext == str(person_id)`)
와 같은 JSONB 매칭을 쓴다 -- `run_briefings()`가 실행마다 새
`session_id`("briefing:<uuid4>", 결정 I)를 만들어 테스트가 미리 알 수
없기 때문이다(`app/briefing/run.py` 모듈 docstring "실행 하나의
session_id" 절).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from sqlalchemy import select

from app.briefing.compose import FakeBriefingComposer
from app.briefing.run import run_briefings
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
    BriefingInput,
    BriefingLine,
    ComposedBriefing,
    Suggestion,
)
from app.db.models import AgentTrace, Event, FactSource, Person, PersonFact, Schedule
from app.tools.context import ToolContext

pytestmark = pytest.mark.dbtest

_T0 = datetime(2026, 2, 1, 4, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 헬퍼 (test_briefing_select.py·test_briefing_inputs.py 와 같은 이름 관례)
# ---------------------------------------------------------------------------


def _make_person(
    db_session,
    *,
    user_id: str = "brief-u5-test-user",
    display_name: str = "민수",
    relation_tag: str = "친구",
    hierarchy: str = "동",
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
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
        person_id=person.id, title=title, scheduled_at=scheduled_at, briefed_at=briefed_at
    )
    db_session.add(schedule)
    db_session.flush()
    return schedule


def _add_event(
    db_session,
    person: Person,
    *,
    event_type: str = "meal",
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
    db_session, person: Person, *, key: str, value: str, confidence: float = 0.9
) -> PersonFact:
    fact = PersonFact(person_id=person.id, key=key, value=value, confidence=confidence)
    db_session.add(fact)
    db_session.flush()
    return fact


def _ctx(
    db_session,
    *,
    session_id: str = "caller:run-test",
    user_id: str = "brief-u5-test-user",
    now=lambda: _T0,
) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, user_id=user_id, now=now)


def _trace_rows(db_session, step: str) -> list[AgentTrace]:
    """같은 (롤백 픽스처로 격리된) 테스트 안에서 이 패키지가 쓴 step 의
    trace 행 전부. `run_briefings()` 가 실행마다 새 `session_id` 를
    만들어(결정 I) 테스트가 미리 알 수 없으므로, `tool_name`·`step` 만
    걸러 조회한다(테스트 격리 자체가 다른 실행 데이터를 막아 준다)."""

    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
            .where(AgentTrace.step == step)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


@dataclass
class _ScriptedComposer:
    """일정 id -> 응답(`ComposedBriefing`) 또는 예외를 미리 정해 두는
    테스트 전용 `BriefingComposer`(판정 23행처럼 토큰·공급자 메타데이터
    까지 지정해야 할 때 `FakeBriefingComposer`(표 기반, raw dict 를
    `_parse_composed()`로 거쳐 tokens 가 항상 0)보다 이 쪽이 더
    간단하다). `fail_for` 에 있는 schedule_id 는 `RuntimeError`("그 밖의
    예외" -- `JudgeUnavailable` 이 아니다, `app/briefing/run.py` 모듈
    docstring "SQLAlchemyError 처리 규약" 절)를 던진다."""

    responses: dict[int, ComposedBriefing] = field(default_factory=dict)
    fail_for: frozenset[int] = frozenset()
    call_count: int = field(default=0, init=False)
    seen_schedule_ids: list[int] = field(default_factory=list, init=False)

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing:
        self.call_count += 1
        self.seen_schedule_ids.append(briefing_input.schedule_id)
        if briefing_input.schedule_id in self.fail_for:
            raise RuntimeError("boom")
        return self.responses[briefing_input.schedule_id]


@dataclass
class _FakeNotifier:
    """판정 24행 -- 호출 횟수·인자를 기록하는 테스트 전용 `Notifier`."""

    calls: list[tuple[Any, ComposedBriefing]] = field(default_factory=list)

    def notify(self, schedule: Any, composed: ComposedBriefing) -> str:
        self.calls.append((schedule, composed))
        return "sent"


# ---------------------------------------------------------------------------
# 판정 21행 -- 템플릿 대체(결정 D): JudgeUnavailable -> composer="template",
# 제안 null, briefed_at 기록, fallback_reason
# ---------------------------------------------------------------------------


def test_run_briefings_falls_back_to_template_on_judge_unavailable(db_session) -> None:
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)

    composer = FakeBriefingComposer(fail="timeout")

    result = run_briefings(ctx, composer=composer, trigger="manual")

    assert len(result.briefings) == 1
    briefing = result.briefings[0]
    assert briefing["composer"] == "template"
    assert briefing["suggestion"] is None
    assert result.errors == 0

    db_session.refresh(schedule)
    assert schedule.briefed_at == _T0  # build_briefing_input 의 get_briefing 이 기록, 유지됨

    compose_rows = _trace_rows(db_session, STEP_BRIEFING_COMPOSE)
    assert len(compose_rows) == 1
    assert compose_rows[0].output["composer"] == "template"
    assert compose_rows[0].output["fallback_reason"] == "timeout"
    assert compose_rows[0].session_id.startswith("briefing:")


# ---------------------------------------------------------------------------
# 판정 22행 -- 실패 격리: 일정 2건 중 첫 건이 compose() 중 일반 예외로
# 실패해도(그 밖의 예외) 세이브포인트만 되돌려지고 둘째 건은 정상 처리.
# ---------------------------------------------------------------------------


def test_run_briefings_isolates_failure_other_schedule_still_briefed(db_session) -> None:
    person = _make_person(db_session)
    schedule_a = _make_schedule(
        db_session, person, scheduled_at=_T0 + timedelta(hours=1), title="A 일정"
    )
    schedule_b = _make_schedule(
        db_session, person, scheduled_at=_T0 + timedelta(hours=2), title="B 일정"
    )
    ctx = _ctx(db_session)

    ok_response = ComposedBriefing(
        pattern_sentences=[], lines=[], suggestion=None, tokens_in=3, tokens_out=2, provider="fake"
    )
    composer = _ScriptedComposer(
        responses={schedule_b.id: ok_response}, fail_for=frozenset({schedule_a.id})
    )

    result = run_briefings(ctx, composer=composer, trigger="manual")

    db_session.refresh(schedule_a)
    db_session.refresh(schedule_b)

    # 첫 건 -- 세이브포인트가 되돌려져 briefed_at 이 남지 않는다(build_
    # briefing_input() 이 이미 기록했던 값도 함께 사라진다).
    assert schedule_a.briefed_at is None
    # 둘째 건 -- 정상 처리, briefed_at 기록.
    assert schedule_b.briefed_at == _T0

    assert result.errors == 1
    assert [item["schedule_id"] for item in result.skipped] == [schedule_a.id]
    assert [item["schedule_id"] for item in result.briefings] == [schedule_b.id]

    error_rows = _trace_rows(db_session, STEP_BRIEFING_ERROR)
    assert len(error_rows) == 1
    assert error_rows[0].output == {
        "schedule_id": schedule_a.id,
        "person_id": person.id,
        "stage": "compose",
        "error": "RuntimeError",
    }

    # 첫 건의 briefing_compose trace 는 롤백과 함께 사라지고, 둘째 건만 남는다.
    compose_rows = _trace_rows(db_session, STEP_BRIEFING_COMPOSE)
    assert [row.output["schedule_id"] for row in compose_rows] == [schedule_b.id]


def test_run_briefings_isolates_real_db_error_other_schedule_still_briefed(
    db_session, monkeypatch
) -> None:
    """판정 22행(사용자 결정 2026-10-02) -- **진짜 DB 오류**도 일정 단위로
    격리한다. 첫 일정의 입력 조립 중 `SELECT 1/0` 으로 Postgres 트랜잭션을
    실제로 깨뜨린다(이 상태에서는 세이브포인트로 되돌리지 않으면 다음
    쿼리가 전부 실패한다). 그래도 둘째 일정은 정상 브리핑되고, 첫 일정은
    `briefed_at` 이 남지 않으며 `briefing_error` 가 1행 남아야 한다 --
    한 일정의 반복 DB 오류가 매분 나머지 일정까지 막지 않는다."""

    from sqlalchemy import text

    import app.briefing.run as run_module

    person = _make_person(db_session)
    schedule_a = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1), title="A 일정")
    schedule_b = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=2), title="B 일정")
    ctx = _ctx(db_session)

    real_build = run_module.build_briefing_input

    def build_or_break(run_ctx, schedule):
        briefing_input = real_build(run_ctx, schedule)  # briefed_at 기록까지 한 뒤 깨뜨린다
        if schedule.id == schedule_a.id:
            run_ctx.session.execute(text("SELECT 1/0"))
        return briefing_input

    monkeypatch.setattr(run_module, "build_briefing_input", build_or_break)

    ok_response = ComposedBriefing(
        pattern_sentences=[], lines=[], suggestion=None, tokens_in=3, tokens_out=2, provider="fake"
    )
    composer = _ScriptedComposer(responses={schedule_b.id: ok_response}, fail_for=frozenset())

    result = run_briefings(ctx, composer=composer, trigger="manual")

    db_session.refresh(schedule_a)
    db_session.refresh(schedule_b)
    assert schedule_a.briefed_at is None
    assert schedule_b.briefed_at == _T0
    assert result.errors == 1
    assert [item["schedule_id"] for item in result.briefings] == [schedule_b.id]
    assert [item["schedule_id"] for item in result.skipped] == [schedule_a.id]
    assert result.skipped[0]["reason"] == "DataError"

    error_rows = _trace_rows(db_session, STEP_BRIEFING_ERROR)
    assert len(error_rows) == 1
    assert error_rows[0].output["schedule_id"] == schedule_a.id
    assert error_rows[0].output["error"] == "DataError"


# ---------------------------------------------------------------------------
# 판정 23행 -- trace 전 필드 + tokens = 생성기 사용량
# ---------------------------------------------------------------------------


def test_run_briefings_records_full_trace_fields_with_generator_tokens(db_session) -> None:
    person = _make_person(db_session)
    recent_event = _add_event(
        db_session, person, event_type="meal", occurred_at=_T0 - timedelta(days=1), content="저녁 같이 먹음"
    )
    source_event = _add_event(
        db_session, person, event_type="personal_share", occurred_at=_T0 - timedelta(days=5), content="등산 좋아한다고 함"
    )
    fact = _make_fact(db_session, person, key="hobby", value="등산")
    db_session.add(FactSource(fact_id=fact.id, event_id=source_event.id))
    db_session.flush()

    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))
    ctx = _ctx(db_session)

    response = ComposedBriefing(
        pattern_sentences=[],
        lines=[BriefingLine(text="민수는 등산을 좋아해요.", basis={"fact_keys": ["hobby"], "event_ids": []})],
        suggestion=Suggestion(
            text="등산 갈만한 곳을 추천해 보세요.", basis={"fact_keys": ["hobby"], "event_ids": []}
        ),
        tokens_in=120,
        tokens_out=45,
        provider="fake-provider",
        model="fake-model-1",
    )
    composer = _ScriptedComposer(responses={schedule.id: response})

    result = run_briefings(ctx, composer=composer, trigger="manual")

    assert result.errors == 0
    compose_rows = _trace_rows(db_session, STEP_BRIEFING_COMPOSE)
    assert len(compose_rows) == 1
    row = compose_rows[0]

    assert row.tokens_in == 120
    assert row.tokens_out == 45

    output = row.output
    assert output["schedule_id"] == schedule.id
    assert output["person_id"] == person.id
    assert isinstance(output["pattern_trace_id"], int)
    assert output["used_facts"] == [{"key": "hobby", "fact_id": fact.id, "eligible": True}]
    assert output["excluded_facts"] == []
    # get_briefing 의 recent_events 는 fact_sources 연결 여부와 무관하게
    # occurred_at DESC 상위 5건을 돌려준다 -- 두 이벤트 모두 포함된다.
    assert output["event_ids"] == [recent_event.id, source_event.id]
    assert output["composer"] == "llm"
    assert "fallback_reason" not in output
    assert output["pattern_sentences"] == []
    assert output["lines"] == [
        {"text": "민수는 등산을 좋아해요.", "basis": {"fact_keys": ["hobby"], "event_ids": []}}
    ]
    assert output["suggestion"] == {
        "text": "등산 갈만한 곳을 추천해 보세요.",
        "basis": {"fact_keys": ["hobby"], "event_ids": []},
    }
    assert output["rejected"] == []
    assert output["llm"] == {"provider": "fake-provider", "model": "fake-model-1"}
    assert output["push"] == "not_configured"

    run_rows = _trace_rows(db_session, STEP_BRIEFING_RUN)
    assert len(run_rows) == 1
    run_output = run_rows[0].output
    assert run_output["trigger"] == "manual"
    assert run_output["schedule_id_arg"] is None
    assert run_output["selected"] == [schedule.id]
    assert run_output["skipped"] == []
    assert run_output["briefed"] == [schedule.id]
    assert run_output["errors"] == 0
    assert set(run_output["window"].keys()) == {"from", "to"}
    assert run_rows[0].tokens_in == 0
    assert run_rows[0].tokens_out == 0

    # 같은 실행의 두 trace 행은 같은 session_id 를 공유한다(결정 I).
    assert row.session_id == run_rows[0].session_id
    assert row.session_id.startswith("briefing:")


# ---------------------------------------------------------------------------
# 판정 24행 -- 푸시 없음(결정 J): push == "not_configured", 가짜 Notifier
# 는 호출 1회·인자에 raw_utterance 없음
# ---------------------------------------------------------------------------


def test_run_briefings_push_not_configured_by_default(db_session) -> None:
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)

    result = run_briefings(ctx, composer=FakeBriefingComposer(), trigger="manual")

    assert result.briefings[0]["push"] == "not_configured"
    compose_rows = _trace_rows(db_session, STEP_BRIEFING_COMPOSE)
    assert compose_rows[0].output["push"] == "not_configured"


def test_run_briefings_calls_fake_notifier_once_without_raw_utterance(db_session) -> None:
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)
    notifier = _FakeNotifier()

    result = run_briefings(
        ctx, composer=FakeBriefingComposer(), notifier=notifier, trigger="manual"
    )

    assert notifier.calls.__len__() == 1
    assert result.briefings[0]["push"] == "sent"

    schedule_arg, composed_arg = notifier.calls[0]
    assert schedule_arg.id == schedule.id
    # Schedule ORM 모델 자체에 raw_utterance 컬럼이 없다(01-plan "지킬
    # 불변식" -- 응답·Notifier 인자에 원문을 싣지 않는다).
    assert not hasattr(schedule_arg, "raw_utterance")
    assert isinstance(composed_arg, ComposedBriefing)


# ---------------------------------------------------------------------------
# 판정 27행 -- 원문 불변: events 행 수·raw_utterance·content 동일
# ---------------------------------------------------------------------------


def test_run_briefings_does_not_mutate_events(db_session) -> None:
    person = _make_person(db_session)
    event = _add_event(
        db_session, person, event_type="conflict", occurred_at=_T0 - timedelta(days=1), content="다툼"
    )
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)

    before_raw = event.raw_utterance
    before_content = event.content

    run_briefings(ctx, composer=FakeBriefingComposer(), trigger="manual")

    events = db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
    assert len(events) == 1
    assert events[0].raw_utterance == before_raw
    assert events[0].content == before_content


# ---------------------------------------------------------------------------
# 재실행 멱등 -- 같은 세션 안에서 이미 브리핑한 일정은 다시 안 집는다
# ---------------------------------------------------------------------------


def test_run_briefings_second_run_does_not_repick_briefed_schedule(db_session) -> None:
    person = _make_person(db_session)
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    ctx = _ctx(db_session)
    composer = FakeBriefingComposer()

    first = run_briefings(ctx, composer=composer, trigger="manual")
    second = run_briefings(ctx, composer=composer, trigger="manual")

    assert [item["schedule_id"] for item in first.briefings] == [schedule.id]
    assert second.briefings == []
    assert composer.call_count == 1

    run_rows = _trace_rows(db_session, STEP_BRIEFING_RUN)
    assert len(run_rows) == 2
    assert run_rows[0].output["selected"] == [schedule.id]
    assert run_rows[1].output["selected"] == []


# ---------------------------------------------------------------------------
# schedule_id 지정 모드(결정 C) -- 창 밖·이미 브리핑된 일정도 강제 재생성
# ---------------------------------------------------------------------------


def test_run_briefings_schedule_id_mode_forces_regeneration(db_session) -> None:
    person = _make_person(db_session)
    old_time = _T0 - timedelta(days=1)
    schedule = _make_schedule(
        db_session, person, scheduled_at=_T0 + timedelta(days=10), briefed_at=old_time
    )
    ctx = _ctx(db_session)

    result = run_briefings(
        ctx, composer=FakeBriefingComposer(), schedule_id=schedule.id, trigger="manual"
    )

    assert [item["schedule_id"] for item in result.briefings] == [schedule.id]
    db_session.refresh(schedule)
    assert schedule.briefed_at == _T0

    run_rows = _trace_rows(db_session, STEP_BRIEFING_RUN)
    assert run_rows[0].output["schedule_id_arg"] == schedule.id
    assert run_rows[0].output["selected"] == [schedule.id]


# ---------------------------------------------------------------------------
# 대상 0건 -- briefing_run 1행만 (briefing_compose 는 없음)
# ---------------------------------------------------------------------------


def test_run_briefings_zero_due_schedules_only_writes_run_trace(db_session) -> None:
    _make_person(db_session)  # 일정 없음
    ctx = _ctx(db_session)

    result = run_briefings(ctx, composer=FakeBriefingComposer(), trigger="scheduler")

    assert result.briefings == []
    assert result.skipped == []
    assert result.errors == 0

    run_rows = _trace_rows(db_session, STEP_BRIEFING_RUN)
    assert len(run_rows) == 1
    assert run_rows[0].output["trigger"] == "scheduler"
    assert run_rows[0].output["selected"] == []

    assert _trace_rows(db_session, STEP_BRIEFING_COMPOSE) == []
