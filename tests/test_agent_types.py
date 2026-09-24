"""Refs: P5-loop U1 S3.2 S3.4 원칙9 -- `app/agent/types.py` 단위 테스트.
DB·LLM 없음 (U1 "코드가 도는 건 아직 없다" -- 계약 타입만 검증한다)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.agent import (
    BUCKET_EXECUTE,
    BUCKET_HINT_ONLY,
    GATE_BUCKETS,
    LOOP_RESUME_VERSION,
    LOOP_TRACE_STEPS,
    LOOP_TRACE_TOOL_NAME,
    NEW_PERSON_TAG_OPTIONS,
    STEP_LOOP_ERROR,
    STEP_LOOP_EXTRACT,
    STEP_LOOP_GATE,
    STEP_LOOP_RECORD,
    STEP_LOOP_RESOLVE_DONE,
    STEP_LOOP_RESUME,
    STEP_LOOP_TURN,
    AcceptedProposal,
    EventDraft,
    GateLimits,
    GateVerdict,
    LoopError,
    PendingCall,
    PendingResume,
    Proposal,
    RejectedProposal,
    ResumeContextError,
    ResumeInput,
    ScheduleDraft,
    ScheduleResumeRef,
    StoredSummary,
    ToolCallProposal,
    TurnResult,
)
from app.db.models import EVENT_TYPES, RELATION_TAGS
from app.tools.types import InvalidValue, PendingQuestionOut

# ---------------------------------------------------------------------------
# trace 어휘 (결정 F) -- step 6종 고정, tool_name 고정
# ---------------------------------------------------------------------------


def test_trace_tool_name_is_agent():
    assert LOOP_TRACE_TOOL_NAME == "agent"


def test_loop_trace_steps_are_fixed_six_in_order():
    assert LOOP_TRACE_STEPS == (
        STEP_LOOP_EXTRACT,
        STEP_LOOP_GATE,
        STEP_LOOP_RESOLVE_DONE,
        STEP_LOOP_RECORD,
        STEP_LOOP_TURN,
        STEP_LOOP_RESUME,
    )
    assert len(LOOP_TRACE_STEPS) == 6
    assert len(set(LOOP_TRACE_STEPS)) == 6  # 중복 없음


def test_loop_error_step_is_prefixed_but_not_in_the_six():
    assert STEP_LOOP_ERROR == "loop_error"
    assert STEP_LOOP_ERROR not in LOOP_TRACE_STEPS
    assert all(step.startswith("loop_") for step in (*LOOP_TRACE_STEPS, STEP_LOOP_ERROR))


# ---------------------------------------------------------------------------
# 게이트 버킷 어휘
# ---------------------------------------------------------------------------


def test_gate_buckets_are_fixed_vocabulary():
    assert GATE_BUCKETS == (BUCKET_EXECUTE, BUCKET_HINT_ONLY)
    assert BUCKET_EXECUTE == "execute"
    assert BUCKET_HINT_ONLY == "hint_only"


def test_accepted_proposal_rejects_unknown_bucket():
    AcceptedProposal(index=0, name="add_event", bucket="execute")  # 통과
    with pytest.raises(InvalidValue):
        AcceptedProposal(index=0, name="add_event", bucket="not_a_bucket")


# ---------------------------------------------------------------------------
# M-1(d) -- NEW_PERSON_TAG_OPTIONS 는 RELATION_TAGS 와 1:1
# ---------------------------------------------------------------------------


def test_tag_options_for_new_person_map_onto_relation_tags_one_to_one():
    assert len(NEW_PERSON_TAG_OPTIONS) == len(RELATION_TAGS)
    mapping = dict(zip(NEW_PERSON_TAG_OPTIONS, RELATION_TAGS))
    assert len(mapping) == len(RELATION_TAGS)  # 옵션 문자열 중복 없음
    assert set(mapping.values()) == set(RELATION_TAGS)
    # 01-plan 84행 원문 순서 그대로.
    assert NEW_PERSON_TAG_OPTIONS == (
        "가족으로 기억할게요",
        "연인으로 기억할게요",
        "친구로 기억할게요",
        "직장으로 기억할게요",
        "지인으로 기억할게요",
    )


# ---------------------------------------------------------------------------
# ToolCallProposal / Proposal
# ---------------------------------------------------------------------------


def test_tool_call_proposal_to_dict_round_trips_through_json():
    proposal = ToolCallProposal(name="add_event", args={"person": "민수", "type": "meal"})
    assert json.loads(json.dumps(proposal.to_dict())) == {
        "name": "add_event",
        "args": {"person": "민수", "type": "meal"},
    }


def test_proposal_to_dict_nests_tool_calls_and_raw():
    proposal = Proposal(
        tool_calls=[ToolCallProposal(name="add_event", args={"person": "민수"})],
        raw={"tool_calls": [{"name": "add_event", "args": {"person": "민수"}}]},
    )
    d = proposal.to_dict()
    assert d["tool_calls"] == [{"name": "add_event", "args": {"person": "민수"}}]
    assert d["raw"] == {"tool_calls": [{"name": "add_event", "args": {"person": "민수"}}]}


# ---------------------------------------------------------------------------
# GateVerdict (loop_gate.output 스키마)
# ---------------------------------------------------------------------------


def test_gate_verdict_to_dict_shape():
    verdict = GateVerdict(
        accepted=[AcceptedProposal(index=0, name="add_event", bucket=BUCKET_EXECUTE)],
        rejected=[RejectedProposal(index=1, name="update_person", reason="person_id_from_llm")],
        limits=GateLimits(mentions=5, events=5, schedules=3, proposals=13),
        stop_reason=None,
    )
    d = verdict.to_dict()
    assert d == {
        "accepted": [{"index": 0, "name": "add_event", "bucket": "execute"}],
        "rejected": [
            {"index": 1, "name": "update_person", "reason": "person_id_from_llm"}
        ],
        "limits": {"mentions": 5, "events": 5, "schedules": 3, "proposals": 13},
        "stop_reason": None,
    }
    json.dumps(d)  # JSON 직렬화 가능(agent_traces.output JSONB).


def test_gate_verdict_defaults_are_empty():
    verdict = GateVerdict()
    assert verdict.accepted == []
    assert verdict.rejected == []
    assert verdict.limits.to_dict() == {
        "mentions": 0,
        "events": 0,
        "schedules": 0,
        "proposals": 0,
    }
    assert verdict.stop_reason is None


# ---------------------------------------------------------------------------
# EventDraft -- type 은 EVENT_TYPES 부분집합
# ---------------------------------------------------------------------------


def test_event_draft_type_must_be_in_event_types():
    when = datetime(2026, 9, 23, 19, 0, tzinfo=timezone.utc)
    for event_type in EVENT_TYPES:
        draft = EventDraft(mention="민수", type=event_type, content="저녁", occurred_at=when)
        assert draft.type in EVENT_TYPES

    with pytest.raises(InvalidValue):
        EventDraft(mention="민수", type="not_a_type", content="저녁", occurred_at=when)


def test_schedule_draft_allows_unconfirmed_scheduled_at():
    draft = ScheduleDraft(mention="민수", title="저녁 약속", scheduled_at=None)
    assert draft.to_dict()["scheduled_at"] is None


# ---------------------------------------------------------------------------
# PendingResume -- to_dict() 왕복(질문 종류별 필드 포함), 발화 원문 미포함
# ---------------------------------------------------------------------------


def test_pending_resume_identity_shape_omits_kind_specific_fields():
    resume = PendingResume(
        mention="민수",
        hints={"hierarchy": "동"},
        pending_calls=[PendingCall(index=0, name="add_event", args={"person": "민수"})],
    )
    d = resume.to_dict()
    assert json.loads(json.dumps(d)) == d  # JSON 왕복 -- agent_traces/pending_questions 저장 가능
    assert d["version"] == LOOP_RESUME_VERSION
    assert d["mention"] == "민수"
    assert d["hints"] == {"hierarchy": "동"}
    assert d["pending_calls"] == [{"index": 0, "name": "add_event", "args": {"person": "민수"}}]
    assert d["dropped"] == 0
    # identity 질문은 M-1(d)/M-2(i) 전용 필드를 싣지 않는다(01-plan 83행).
    assert "tag_by_answer" not in d
    assert "schedule" not in d
    assert "schedule_options" not in d


def test_pending_resume_new_person_shape_includes_tag_by_answer():
    tag_by_answer = dict(zip(NEW_PERSON_TAG_OPTIONS, RELATION_TAGS))
    resume = PendingResume(mention="민수", tag_by_answer=tag_by_answer)
    d = resume.to_dict()
    assert json.loads(json.dumps(d)) == d
    assert d["tag_by_answer"] == tag_by_answer
    assert "schedule" not in d
    assert "schedule_options" not in d


def test_pending_resume_schedule_shape_includes_schedule_fields():
    resume = PendingResume(
        mention="민수",
        schedule=ScheduleResumeRef(person_id=7, title="저녁 약속", call_index=0),
        schedule_options={"10월 2일 저녁 7시": "2026-10-02T19:00:00+09:00", "모르겠어요": ""},
    )
    d = resume.to_dict()
    assert json.loads(json.dumps(d)) == d
    assert d["schedule"] == {"person_id": 7, "title": "저녁 약속", "call_index": 0}
    assert d["schedule_options"]["10월 2일 저녁 7시"] == "2026-10-02T19:00:00+09:00"
    assert "tag_by_answer" not in d


def test_pending_resume_never_carries_raw_utterance():
    # S3.4 13행 -- "전체 대화 이력 저장 금지". PendingResume 자체에 발화
    # 원문을 담는 필드가 없어야 한다(ER 이 context["utterance"] 로 1건만
    # 넣는다, 루프는 더 넣지 않는다).
    resume = PendingResume(mention="민수")
    d = resume.to_dict()
    assert "utterance" not in d
    assert "raw_utterance" not in d
    assert not hasattr(resume, "utterance")


def test_pending_resume_dropping_drafts_keeps_pending_calls():
    # 판정 표 24행 -- LOOP_MAX_RESUME_BYTES 초과 시 held_drafts 만 버리고
    # pending_calls·dropped 는 남는다(이 타입은 그 모양만 고정한다).
    resume = PendingResume(
        mention="민수",
        pending_calls=[PendingCall(index=0, name="add_event", args={})],
        held_drafts=[],
        dropped=2,
    )
    d = resume.to_dict()
    assert d["pending_calls"] == [{"index": 0, "name": "add_event", "args": {}}]
    assert d["held_drafts"] == []
    assert d["dropped"] == 2


# ---------------------------------------------------------------------------
# ResumeInput
# ---------------------------------------------------------------------------


def test_resume_input_kind_must_be_a_question_kind():
    ResumeInput(kind="identity", context={"mention": "민수"}, answer="네, 맞아요")
    with pytest.raises(InvalidValue):
        ResumeInput(kind="not_a_kind", context={}, answer="x")


def test_resume_input_to_dict_round_trips_through_json():
    resume_input = ResumeInput(
        kind="new_person", context={"resume": {"mention": "민수"}}, answer="친구로 기억할게요"
    )
    d = resume_input.to_dict()
    assert json.loads(json.dumps(d)) == d
    assert d == {
        "kind": "new_person",
        "context": {"resume": {"mention": "민수"}},
        "answer": "친구로 기억할게요",
    }


# ---------------------------------------------------------------------------
# TurnResult
# ---------------------------------------------------------------------------


def test_turn_result_to_dict_without_pending_question():
    result = TurnResult(
        reply="민수와의 저녁 약속을 기억했어요.",
        session_id="s-1",
        stored=StoredSummary(persons=0, events=1, schedules=0),
        trace_ids=[10, 11, 12],
    )
    d = result.to_dict()
    assert json.loads(json.dumps(d)) == d
    assert d["pending_question"] is None
    assert d["stored"] == {"persons": 0, "events": 1, "schedules": 0}
    assert d["stop_reason"] is None
    assert d["trace_ids"] == [10, 11, 12]


def test_turn_result_to_dict_with_pending_question_reuses_pending_question_out():
    pq = PendingQuestionOut(
        question_id=5,
        status="pending",
        kind="new_person",
        question='"민수"을(를) 새 인물로 기억해둘까요?',
        options=[*NEW_PERSON_TAG_OPTIONS, "아니요"],
    )
    result = TurnResult(
        reply="확인이 필요해요.",
        session_id="s-1",
        pending_question=pq,
        stop_reason="ask_user",
    )
    d = result.to_dict()
    assert d["pending_question"] == pq.to_dict()
    assert d["stop_reason"] == "ask_user"


# ---------------------------------------------------------------------------
# 예외 계층
# ---------------------------------------------------------------------------


def test_loop_error_hierarchy():
    assert issubclass(ResumeContextError, LoopError)
    assert issubclass(LoopError, Exception)
    err = ResumeContextError("missing_resume_key")
    assert err.reason == "missing_resume_key"
    assert str(err) == "missing_resume_key"
