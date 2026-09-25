"""Refs: P5-loop D1 D2 D12 D13 S3.2 S3.3 S3.4 원칙1 원칙2 원칙4 원칙7 원칙9 --
U4 해석 단계(`app/agent/loop.py::resolve_mentions`) + U5 기록·응답 단계
(`app/agent/loop.py::run_turn`) 테스트.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`) +
`FakeJudge`(네트워크 0, `app/er/judge.py` 무수정 import) + `fake_embedder`
(스텁 임베더). 제안·게이트는 손으로 만들지 않고 실제 `app.agent.gate.check()`
를 거쳐 `GateVerdict` 를 만든다 -- 게이트·해석 경계가 실제 그대로 맞물리는지
함께 확인한다(U3 산출물 재사용, 중복 구현 금지).

U5 절은 `run_turn()` 을 `FakeProposer`(U2)로 감싸 인식 단계까지 포함한 한
턴 전체를 돌린다 -- 손으로 `Proposal`/`GateVerdict` 를 만들지 않는다(U4
절과 같은 이유, 경계가 실제로 맞물리는지 확인).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import func, select

import app.agent.loop as loop_module
from app.agent.gate import check
from app.agent.loop import resolve_mentions, run_turn
from app.agent.propose import FakeProposer
from app.agent.types import NEW_PERSON_TAG_OPTIONS, Proposal, ToolCallProposal
from app.db.models import AgentTrace, ALIAS_SOURCES, Event, PendingQuestion, Person, PersonAlias, Schedule
from app.er import AlreadyApplied, apply_resolution
from app.er.judge import FakeJudge
from app.tools.context import ToolContext
from app.tools.types import AFFIRMATIVE_KEY

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 9, 24, 19, 0, 0, tzinfo=timezone.utc)


def _make_person(
    db_session, *, display_name: str, relation_tag: str = "직장", hierarchy: str = "동", user_id: str = "local"
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(
    db_session, person: Person, alias: str, *, embedding=None, source: str = ALIAS_SOURCES[0]
) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=source, embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


def _ctx(db_session, *, session_id: str, embedder=None) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder)


def _call(name: str, **args) -> ToolCallProposal:
    return ToolCallProposal(name=name, args=args)


def _verdict_for(*calls: ToolCallProposal) -> tuple[Proposal, "GateVerdict"]:
    proposal = Proposal(tool_calls=list(calls), raw={})
    return proposal, check(proposal)


# ---------------------------------------------------------------------------
# merge -- 언급이 기존 인물로 연결되고 person_id 가 확정된다
# ---------------------------------------------------------------------------


def test_merge_connects_to_existing_person_and_returns_person_id(db_session, fake_embedder):
    session_id = "loop-u4-merge"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(
        ctx, proposal, verdict, "어제 팀장이랑 저녁 먹었어", judge=FakeJudge(table={person.id: 0.95})
    )

    assert outcome.stopped is False
    assert outcome.pending_question_id is None
    assert outcome.person_ids == {"팀장": person.id}
    assert len(outcome.decisions) == 1
    assert outcome.decisions[0].band == "merge"
    assert outcome.decisions[0].person_id == person.id
    assert outcome.decisions[0].trace_id is not None


# ---------------------------------------------------------------------------
# identity -- 되묻기로 턴이 끝나고, 저장된 options 는 ER 원본 그대로다
# ---------------------------------------------------------------------------


def test_identity_ends_turn_with_er_original_options(db_session, fake_embedder):
    session_id = "loop-u4-identity"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    # FakeJudge(fail=...) -> llm_failed -> identity 로 강제 확정(규칙 통과
    # 후보가 있으므로 new_person 이 아니다, app/er/pipeline.py 의 같은 경로를
    # tests/test_er_pipeline.py::test_resolve_llm_failed_forces_identity_band_llm_failed
    # 가 이미 검증한다 -- 여기서는 "루프가 그 옵션을 그대로 저장하는가"만 본다).
    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    assert outcome.stopped is True
    assert outcome.person_ids == {}
    assert outcome.pending_question_id is not None

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    assert row.kind == "identity"
    assert row.options == ["김민수", "아니요, 다른 사람이에요"]
    assert row.context[AFFIRMATIVE_KEY] == ["김민수"]


# ---------------------------------------------------------------------------
# new_person -- M-1(d)·M-3 안 A: 힌트 유무와 관계없이 항상 태그 옵션으로 묻는다
# ---------------------------------------------------------------------------


def test_new_person_uses_tag_options_without_hint(db_session, fake_embedder):
    session_id = "loop-u4-new-person-no-hint"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    # "이모"는 호칭 사전 표제어라 규칙 필터가 유일한 후보를 배제한다
    # (dictionary_conflict) -- 규칙 통과 후보 0건이라 LLM 을 부르지 않고
    # new_person 으로 강제 확정된다(D13, tests/test_er_pipeline.py 의
    # no_candidates 케이스와 같은 설정).
    proposal, verdict = _verdict_for(
        _call("add_event", person="이모", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(table={}))

    assert outcome.stopped is True
    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    assert row.kind == "new_person"
    tags = list(NEW_PERSON_TAG_OPTIONS)
    assert row.options == tags + ["아니요"]
    assert row.context[AFFIRMATIVE_KEY] == tags


def test_new_person_uses_tag_options_even_with_hint_present(db_session, fake_embedder):
    """M-3 안 A -- LLM 힌트(`relation_tag`)가 있어도 태그 옵션은 그대로
    6개다. `hints` 는 위계 판단에만 쓰이고 `relation_tag` 는 항상 답에서
    온다(재개, U7 몫이라 여기서는 저장된 옵션·긍정 목록만 본다)."""

    session_id = "loop-u4-new-person-hint"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="이모", type="meal", content="저녁", occurred_at=NOW),
        _call(
            "create_person",
            display_name="이모",
            aliases=["이모"],
            relation_tag="가족",
            hierarchy="상",
        ),
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(table={}))

    assert outcome.stopped is True
    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    tags = list(NEW_PERSON_TAG_OPTIONS)
    assert row.options == tags + ["아니요"]
    assert row.context[AFFIRMATIVE_KEY] == tags

    resume = row.context["resume"]
    assert resume["hints"] == {"relation_tag": "가족", "hierarchy": "상"}
    assert resume["tag_by_answer"] == dict(zip(tags, ["가족", "연인", "친구", "직장", "지인"]))


# ---------------------------------------------------------------------------
# AlreadyApplied -- 같은 Resolution 을 두 번째로 apply_resolution 하면 거부된다
# ---------------------------------------------------------------------------


def test_already_applied_rejects_second_apply_resolution_call(db_session, fake_embedder):
    session_id = "loop-u4-already-applied"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))
    resolution = outcome.decisions[-1].resolution
    assert resolution is not None

    with pytest.raises(AlreadyApplied):
        apply_resolution(ctx, resolution)


# ---------------------------------------------------------------------------
# 루프는 확신도·임계치를 참조하지 않는다 (판정 표 6행의 pytest 화)
# ---------------------------------------------------------------------------


def test_loop_module_source_never_mentions_thresholds_or_confidence_literal():
    source = Path(loop_module.__file__).read_text(encoding="utf-8")
    for token in ("T_merge", "t_merge", "T_new", "t_new", "confidence"):
        assert token not in source, f"금지 토큰 발견: {token}"


# ---------------------------------------------------------------------------
# 확장된 context["resume"] 가 저장된 행에서 읽힌다 (M-0 크기 통제)
# ---------------------------------------------------------------------------


def test_extended_context_resume_round_trips_from_stored_row(db_session, fake_embedder):
    session_id = "loop-u4-resume-roundtrip"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW),
        _call("add_schedule", person="팀장", title="약속", scheduled_at=NOW),
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["mention"] == "팀장"
    assert resume["dropped"] == 0
    assert {c["name"] for c in resume["pending_calls"]} == {"add_event", "add_schedule"}
    # S3.4 13행 "전체 대화 이력 저장 금지" -- 발화 원문은 ER 이 이미 넣은
    # context["utterance"] 하나뿐이고 resume 에는 다시 넣지 않는다.
    assert "utterance" not in resume


def test_pending_calls_excludes_already_merged_mentions(db_session, fake_embedder):
    """결정 C(i)·D(i) -- 먼저 merge 로 확정된 언급의 제안은 재개 재료에
    담기지 않고, 되묻기를 일으킨(그리고 그 이후) 언급의 제안만 담긴다."""

    session_id = "loop-u4-mixed-mentions"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁1", occurred_at=NOW),
        _call("add_event", person="이모", type="meal", content="저녁2", occurred_at=NOW),
    )

    outcome = resolve_mentions(
        ctx, proposal, verdict, "발화", judge=FakeJudge(table={person.id: 0.95})
    )

    assert outcome.stopped is True
    assert outcome.person_ids == {"팀장": person.id}

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert [c["index"] for c in resume["pending_calls"]] == [1]


# ---------------------------------------------------------------------------
# LOOP_MAX_RESUME_BYTES 초과 -- held_drafts 는 버리고 pending_calls 는 유지
# ---------------------------------------------------------------------------


def test_resume_byte_limit_drops_held_drafts_but_keeps_pending_calls(db_session, fake_embedder):
    session_id = "loop-u4-byte-limit"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    long_content = "긴 내용 " * 100
    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content=long_content, occurred_at=NOW)
    )

    outcome = resolve_mentions(
        ctx,
        proposal,
        verdict,
        "발화",
        judge=FakeJudge(fail="timeout"),
        resume_byte_limit=50,
    )

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["held_drafts"] == []
    assert resume["dropped"] == 1
    assert len(resume["pending_calls"]) == 1
    assert resume["pending_calls"][0]["args"]["content"] == long_content


def test_resume_within_byte_limit_keeps_held_drafts(db_session, fake_embedder):
    """대조군 -- 기본 상한(`app.settings.LOOP_MAX_RESUME_BYTES`)에서는
    `held_drafts` 가 버려지지 않는다(정상 크기의 되묻기)."""

    session_id = "loop-u4-byte-limit-ok"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="짧은 내용", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["dropped"] == 0
    assert resume["held_drafts"] == [{"name": "add_event", "content": "짧은 내용"}]


# ---------------------------------------------------------------------------
# U5 -- run_turn(): 기록 + 응답
# ---------------------------------------------------------------------------


def _trace_rows(db_session, session_id: str) -> list[AgentTrace]:
    return (
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == session_id).order_by(AgentTrace.id)
        )
        .scalars()
        .all()
    )


def _first_output(rows: list[AgentTrace], step: str) -> dict:
    return next(r.output for r in rows if r.step == step)


def _count(db_session, model) -> int:
    """전체 행 수(로컬 DB 는 다른 테스트·수동 재현 명령이 남긴 행과
    공유되므로, `select(model).all() == []` 처럼 "테이블이 비어 있다"를
    직접 단언하지 않고 호출 전후 개수 차이로만 판단한다)."""
    return db_session.execute(select(func.count()).select_from(model)).scalar_one()


def test_run_turn_merge_executes_add_event_and_satisfies_accepted_equation(
    db_session, fake_embedder
):
    """merge 로 끝나는 턴 -- add_event 가 실행되고, 원문이 그대로 저장되고
    (01-plan U5 "원문 그대로 저장"), `executed[].trace_id` 가 실제
    `add_event` tool_call 행을 가리키며, U1 등식이 성립한다."""

    session_id = "loop-u5-merge"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    utterance = "어제 팀장이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        }
    ]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.pending_question is None
    assert result.session_id == session_id
    assert result.stored.events == 1
    assert result.stored.schedules == 0
    assert "이벤트 1건" in result.reply

    event = db_session.execute(select(Event).where(Event.person_id == person.id)).scalar_one()
    assert event.raw_utterance == utterance
    assert event.type == "meal"

    rows = _trace_rows(db_session, session_id)
    gate_out = _first_output(rows, "loop_gate")
    record_out = _first_output(rows, "loop_record")

    assert record_out["failed"] == []
    assert len(record_out["executed"]) == 1
    executed_entry = record_out["executed"][0]
    assert executed_entry["index"] == 0
    assert executed_entry["name"] == "add_event"

    trace_id = executed_entry["trace_id"]
    matched = next(r for r in rows if r.id == trace_id)
    assert matched.step == "tool_call"
    assert matched.tool_name == "add_event"

    accepted_idx = {a["index"] for a in gate_out["accepted"]}
    executed_idx = {e["index"] for e in record_out["executed"]}
    failed_idx = {f["index"] for f in record_out["failed"]}
    hint_only_idx = {a["index"] for a in gate_out["accepted"] if a["bucket"] == "hint_only"}
    assert accepted_idx == executed_idx | failed_idx | hint_only_idx


def test_run_turn_new_person_defers_add_event_to_resume_pending_calls(db_session, fake_embedder):
    """되묻기로 끝나는 턴 -- 확정되지 않은 언급의 `add_event` 는 0회
    실행되고, `context["resume"]["pending_calls"]` 에 그 제안이 실린다
    (01-plan U5 "확정되지 않은 언급에는 add_event 0회·보류 제안이
    resume.pending_calls 에 실림"). U1 등식도 되묻기 턴에서 성립한다."""

    session_id = "loop-u5-new-person"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    events_before = _count(db_session, Event)

    utterance = "오늘 이모랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "이모",
                "type": "meal",
                "content": "저녁",
                "occurred_at": NOW.isoformat(),
            },
        }
    ]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={}),
    )

    assert result.pending_question is not None
    assert result.pending_question.kind == "new_person"
    assert result.stored.events == 0

    assert _count(db_session, Event) == events_before

    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    resume = row.context["resume"]
    assert [c["index"] for c in resume["pending_calls"]] == [0]
    assert resume["pending_calls"][0]["name"] == "add_event"

    rows = _trace_rows(db_session, session_id)
    gate_out = _first_output(rows, "loop_gate")
    record_out = _first_output(rows, "loop_record")
    assert record_out["executed"] == []
    assert record_out["failed"] == []

    accepted_idx = {a["index"] for a in gate_out["accepted"]}
    executed_idx = {e["index"] for e in record_out["executed"]}
    failed_idx = {f["index"] for f in record_out["failed"]}
    pending_idx = {c["index"] for c in resume["pending_calls"]}
    hint_only_idx = {a["index"] for a in gate_out["accepted"] if a["bucket"] == "hint_only"}
    assert accepted_idx == executed_idx | failed_idx | pending_idx | hint_only_idx


def test_run_turn_schedule_without_time_asks_schedule_question(db_session, fake_embedder):
    """결정 K(i)·M-2(i) -- `scheduled_at` 이 확정되지 않은 `add_schedule`
    은 저장되지 않고 `ask_user(kind="schedule")` 로 되묻는다.
    `resume.schedule.person_id` 는 이번 턴의 merge 로 얻은 id 다."""

    session_id = "loop-u5-schedule"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = ToolContext(
        session=db_session, session_id=session_id, embedder=fake_embedder, now=lambda: NOW
    )
    schedules_before = _count(db_session, Schedule)

    utterance = "팀장이랑 다음에 약속 잡기로 했어"
    calls = [{"name": "add_schedule", "args": {"person": "팀장", "title": "약속"}}]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.pending_question is not None
    assert result.pending_question.kind == "schedule"
    assert result.stored.schedules == 0

    assert _count(db_session, Schedule) == schedules_before

    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    assert row.kind == "schedule"
    assert "모르겠어요" in row.options

    resume = row.context["resume"]
    assert resume["schedule"]["person_id"] == person.id
    assert resume["schedule"]["title"] == "약속"
    assert resume["schedule"]["call_index"] == 0
    assert set(resume["schedule_options"]) == set(row.options) - {"모르겠어요"}
    assert [c["name"] for c in resume["pending_calls"]] == ["add_schedule"]


def test_run_turn_stopped_turn_defers_merged_mention_unconfirmed_schedule_to_pending_calls(
    db_session, fake_embedder
):
    """사용자 수정 요청(2026-09-24) -- 다른 언급("이모")이 되묻기로 턴을
    끝내도, 이미 merge 된 언급("팀장")의 시각 미확정 `add_schedule` 은
    `InvalidValue` 로 잃지 않고 그 되묻기 질문의
    `context["resume"]["pending_calls"]` 로 넘어간다(U4
    `_pending_calls_from` 의 예외). `schedules` 행 0·`failed` 에 없음·
    등식 성립을 함께 확인한다."""

    session_id = "loop-u5-schedule-deferred"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    schedules_before = _count(db_session, Schedule)

    utterance = "팀장이랑 저녁 먹고 이모랑도 저녁 먹었는데 팀장이랑 다음에 약속도 잡기로 했어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁1",
                "occurred_at": NOW.isoformat(),
            },
        },
        {
            "name": "add_event",
            "args": {
                "person": "이모",
                "type": "meal",
                "content": "저녁2",
                "occurred_at": NOW.isoformat(),
            },
        },
        {"name": "add_schedule", "args": {"person": "팀장", "title": "약속"}},
    ]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.pending_question is not None
    assert result.pending_question.kind == "new_person"
    assert result.stored.events == 1
    assert result.stored.schedules == 0
    assert _count(db_session, Schedule) == schedules_before

    rows = _trace_rows(db_session, session_id)
    gate_out = _first_output(rows, "loop_gate")
    record_out = _first_output(rows, "loop_record")
    assert record_out["failed"] == []
    assert [e["name"] for e in record_out["executed"]] == ["add_event"]
    assert record_out["executed"][0]["index"] == 0

    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    resume = row.context["resume"]
    pending_by_index = {c["index"]: c["name"] for c in resume["pending_calls"]}
    assert pending_by_index == {1: "add_event", 2: "add_schedule"}

    accepted_idx = {a["index"] for a in gate_out["accepted"]}
    executed_idx = {e["index"] for e in record_out["executed"]}
    failed_idx = {f["index"] for f in record_out["failed"]}
    pending_idx = {c["index"] for c in resume["pending_calls"]}
    hint_only_idx = {a["index"] for a in gate_out["accepted"] if a["bucket"] == "hint_only"}
    assert accepted_idx == executed_idx | failed_idx | pending_idx | hint_only_idx


def test_run_turn_add_event_naive_datetime_is_caught_as_failed(db_session, fake_embedder):
    """R-24 -- 기록 단계가 게이트를 지난 제안 하나를 실행하다 `ToolError`
    로 실패하면 `loop_record.output.failed[]` 에 담기고 다음 제안으로
    넘어간다 -- 턴 전체가 죽지 않는다.

    FIX-005 이후: 오프셋 없는 ISO **문자열**은 `app.agent.propose.
    _convert_datetime_args` 가 사용자 시간대를 붙여 더 이상 naive 로
    남지 않는다(`tests/test_agent_timezone.py` 가 그 경로를 검증한다).
    이 테스트는 그 경로를 우회해 raw **`datetime` 객체**(naive, 문자열이
    아니므로 시간대 보정 대상이 아니다)를 직접 넣어 R-24 의 방어(naive
    가 어떤 경로로든 `add_event` 까지 오면 여전히 거절된다)를 그대로
    확인한다."""

    session_id = "loop-u5-failed"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    utterance = "어제 팀장이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁",
                # raw naive datetime 객체 -- 문자열이 아니므로
                # _convert_datetime_args 의 시간대 보정 대상이 아니다(FIX-005
                # 이후에도 naive 그대로 add_event 에 닿아 거절된다).
                "occurred_at": datetime(2026, 9, 23, 19, 0, 0),
            },
        }
    ]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.stored.events == 0
    assert (
        db_session.execute(select(Event).where(Event.person_id == person.id)).scalars().all()
        == []
    )

    rows = _trace_rows(db_session, session_id)
    record_out = _first_output(rows, "loop_record")
    assert record_out["executed"] == []
    assert record_out["failed"] == [{"index": 0, "name": "add_event", "error": "InvalidValue"}]
    assert "1건은 저장하지 못했어요" in result.reply


def test_run_turn_no_counseling_reply_for_emotional_utterance(db_session, fake_embedder):
    """원칙7 부정 테스트 -- 감정 발화에 아무 툴도 제안되지 않으면(LLM 이
    빈 `tool_calls` 를 냈다고 가정, `FakeProposer` 표에 없는 발화) 응답은
    고정 문장 하나뿐이고 공감·위로·조언 어휘가 들어갈 자리가 없다."""

    session_id = "loop-u5-no-counseling"
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    utterance = "오늘 너무 힘들고 속상했어"
    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={}),
        judge=FakeJudge(table={}),
    )

    assert result.pending_question is None
    assert result.reply == "이번 발화에서는 새로 기억한 것이 없어요."
    for banned in ("힘드셨", "위로", "괜찮", "공감", "힘내", "그랬구나"):
        assert banned not in result.reply
