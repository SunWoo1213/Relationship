"""Refs: P2b-person-delete U1 F-4d2507 security§5 원칙8 원칙9 -- 인물 참조 판별
규칙(`app/api/delete.py::references_person`) 단위 테스트. DB 없음.

픽스처는 손으로 만든 JSON 이 아니라 **실제로 trace·질문에 쓰이는 코드**
(`to_jsonable`·`*Out.to_dict()`·`_build_ask_payload`·`Resolution.to_dict()`·
`PendingResume.to_dict()`·`ResolveOutcome.to_dict()`)가 만든 모양을 쓴다.
양성 하나마다 "그 규칙 하나만 참인" 구조로 만들어, 규칙 하나를 지우면 그
테스트가 실패하게 한다(FIX-033 (a)). 음성(과잉 판정 금지)은 같은 숫자가 이벤트·
일정·질문 id 로만 있는 구조다.
"""

from __future__ import annotations

import copy
from datetime import UTC, datetime

import pytest

from app.agent.types import PendingCall, PendingResume, ScheduleResumeRef
from app.agent.loop import MentionDecision, ResolveOutcome
from app.api.delete import (
    ID_LIST_KEYS,
    ID_MAP_KEYS,
    PERSON_ID_KEYS,
    PERSON_OBJECT_KEYS,
    PERSON_REF_RULES,
    TOP_LEVEL_ID_TOOLS,
    references_person,
)
from app.er.pipeline import _build_ask_payload
from app.er.types import Resolution, ScoredCandidate
from app.tools.context import to_jsonable
from app.tools.types import BriefingOut, Candidate, EventOut, PersonOut, ScheduleOut

PID = 987654321  # 센티널 -- 다른 시퀀스의 id 와 겹치지 않는 큰 값
OTHER = 7
NOW = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)


def _person_out(person_id: int) -> PersonOut:
    return PersonOut(
        id=person_id, display_name="민수", relation_tag="직장", hierarchy="동", aliases=["민수"]
    )


def _scored(person_id: int, name: str = "민수") -> ScoredCandidate:
    return ScoredCandidate(person_id=person_id, display_name=name)


def _event_out(event_id: int, person_id: int) -> EventOut:
    return EventOut(
        id=event_id, person_id=person_id, type="meal", content="점심", occurred_at=NOW, created_at=NOW
    )


def _schedule_out(schedule_id: int, person_id: int) -> ScheduleOut:
    return ScheduleOut(id=schedule_id, person_id=person_id, title="회식", scheduled_at=NOW)


# ---------------------------------------------------------------------------
# 규칙 상수 -- 값으로 고정 (계약)
# ---------------------------------------------------------------------------


def test_rule_constants_are_fixed_values() -> None:
    """규칙 키 상수가 01-plan 결정 C-3 확정 값 그대로다."""
    assert PERSON_ID_KEYS == ("person_id", "matched_person_id")
    assert PERSON_OBJECT_KEYS == ("person",)
    assert TOP_LEVEL_ID_TOOLS == frozenset({"create_person", "update_person"})
    assert ID_MAP_KEYS == ("candidate_ids", "person_ids")
    assert ID_LIST_KEYS == ("candidate_person_ids",)


def test_person_ref_rules_numbered_one_to_five() -> None:
    """`PERSON_REF_RULES` 는 번호 1~5 순서 그대로 5개다."""
    assert [r.number for r in PERSON_REF_RULES] == [1, 2, 3, 4, 5]
    assert [r.name for r in PERSON_REF_RULES] == [
        "id_key",
        "person_object",
        "top_level_id",
        "id_map_values",
        "id_list",
    ]


# ---------------------------------------------------------------------------
# 규칙 4 -- candidate_ids / person_ids 사전의 값 (V1-1, V1-2)
# ---------------------------------------------------------------------------


def test_identity_question_context_candidate_ids_values() -> None:
    """ER identity 질문 context(`_build_ask_payload` 가 만든 실제 모양)의
    `candidate_ids` 값만으로 그 인물을 참조한다고 판정한다(V1-1)."""
    payload, _ = _build_ask_payload(
        band="identity",
        passed=[_scored(PID, "민수"), _scored(OTHER, "민준")],
        mention="민수씨",
        utterance="민수씨랑 점심 먹었어",
        # matched_person_id 를 None 으로 둬서 규칙 1 이 아니라 규칙 4 만 참이 되게 한다.
        confidence_breakdown={"matched_person_id": None, "confidence": 0.5},
    )
    assert payload is not None
    context = to_jsonable(payload["context"])
    assert context["candidate_ids"] == {"민수": PID, "민준": OTHER}
    assert references_person(context, PID) is True
    assert references_person(context, OTHER) is True  # 후보 둘 다 참조다
    assert references_person(context, 123) is False


def test_new_person_question_context_references_nobody() -> None:
    """new_person 질문 context 는 `candidate_ids == {}` 라 어떤 인물도 가리키지 않는다."""
    payload, _ = _build_ask_payload(
        band="new_person",
        passed=[],
        mention="누구",
        utterance="누구랑 밥 먹었어",
        confidence_breakdown={"matched_person_id": None},
    )
    assert payload is not None
    assert references_person(to_jsonable(payload["context"]), PID) is False


def test_resolve_outcome_person_ids_values() -> None:
    """루프 `loop_resolve_done` output(`ResolveOutcome.to_dict()`)의 `person_ids`
    사전 값(언급→id)만으로 참조 판정(V1-2). `decisions` 는 비워 규칙 1 을 배제."""
    outcome = ResolveOutcome(person_ids={"민수": PID, "민준": OTHER})
    data = to_jsonable(outcome.to_dict())
    assert data["person_ids"] == {"민수": PID, "민준": OTHER}
    assert data["decisions"] == []
    assert references_person(data, PID) is True
    assert references_person(data, OTHER) is True
    assert references_person(data, 123) is False


def test_person_ids_map_in_stored_context_literal() -> None:
    """`person_ids`·`candidate_ids` 가 중첩 어디에 있어도 값을 본다(깊이 무관)."""
    nested = {"resume": {"extra": [{"person_ids": {"a": PID}}]}}
    assert references_person(nested, PID) is True
    assert references_person({"candidate_ids": {"a": 1, "b": PID}}, PID) is True
    assert references_person({"candidate_ids": {"a": 1, "b": 2}}, PID) is False


# ---------------------------------------------------------------------------
# 규칙 2 -- person 사전의 id (V1-3)
# ---------------------------------------------------------------------------


def test_search_person_output_person_object_id() -> None:
    """`search_person` output(`Candidate` 배열) 의 `person.id`(V1-3)."""
    output = to_jsonable(
        [Candidate(person=_person_out(PID), similarity=0.9), Candidate(person=_person_out(OTHER), similarity=0.5)]
    )
    assert references_person(output, PID, tool_name="search_person") is True
    assert references_person(output, OTHER, tool_name="search_person") is True
    assert references_person(output, 123, tool_name="search_person") is False


def test_briefing_out_person_object_id() -> None:
    """`get_briefing` output(`BriefingOut`)의 `person.id`. 이벤트·일정이 비어
    규칙 1 이 아니라 규칙 2 만 참이 되게 한다(V1-3)."""
    output = to_jsonable(BriefingOut(person=_person_out(PID), generated_at=NOW))
    assert output["recent_events"] == [] and output["schedule"] is None
    assert references_person(output, PID, tool_name="get_briefing") is True
    assert references_person(output, OTHER, tool_name="get_briefing") is False


def test_person_object_id_does_not_need_tool_name() -> None:
    """규칙 2(`person.id`)는 `tool_name` 없이도 참이다 -- U2 가 `input`·`context` 판정에서
    `tool_name` 을 넘기지 않고도 기대는 계약(R-U1-3)."""
    assert references_person({"person": {"id": PID}}, PID) is True
    candidates = to_jsonable([Candidate(person=_person_out(PID), similarity=0.9)])
    assert references_person(candidates, PID) is True
    assert references_person(candidates, OTHER) is False


def test_person_key_with_string_value_is_not_reference() -> None:
    """`person` 키가 언급 **문자열**(루프 `pending_calls[].args.person`)이면 참조가 아니다."""
    resume = PendingResume(
        mention="민수",
        pending_calls=[PendingCall(index=0, name="add_event", args={"person": "민수", "content": "점심"})],
    )
    context = to_jsonable({"resume": resume.to_dict()})
    assert references_person(context, PID) is False
    assert references_person({"person": str(PID)}, PID) is False
    assert references_person({"person": {"name": "x"}}, PID) is False  # id 키 없는 사전


# ---------------------------------------------------------------------------
# 규칙 3 -- create_person / update_person 최상위 id (V1-4, V1-5)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tool", ["create_person", "update_person"])
def test_person_out_top_level_id_with_person_tools(tool: str) -> None:
    """`PersonOut` output 의 최상위 `id` 는 `create_person`/`update_person` 일 때만 인물 id(V1-4)."""
    output = to_jsonable(_person_out(PID))
    assert references_person(output, PID, tool_name=tool) is True
    assert references_person(output, OTHER, tool_name=tool) is False


def test_person_out_top_level_id_without_tool_name_is_not_reference() -> None:
    """툴 이름이 없거나 다른 툴이면 최상위 `id` 는 보지 않는다(규칙 3 은 툴 이름 조건부)."""
    output = to_jsonable(_person_out(PID))
    assert references_person(output, PID) is False
    assert references_person(output, PID, tool_name="search_person") is False
    assert references_person(output, PID, tool_name="add_event") is False


def test_top_level_id_rule_does_not_apply_to_nested_id() -> None:
    """규칙 3 은 **최상위** `id` 만이다 -- 중첩된 `id` 는 규칙 2(`person` 아래)가 아니면 안 본다."""
    assert references_person({"data": {"id": PID}}, PID, tool_name="create_person") is False
    assert references_person([{"id": PID}], PID, tool_name="create_person") is False


def test_event_out_id_equal_to_person_id_is_not_reference() -> None:
    """`EventOut.id` 가 인물 id 와 같은 숫자여도(`person_id` 는 다른 인물) 참조가 아니다(V1-5)."""
    output = to_jsonable(_event_out(event_id=PID, person_id=OTHER))
    assert output["id"] == PID and output["person_id"] == OTHER
    assert references_person(output, PID, tool_name="add_event") is False
    assert references_person(output, PID) is False
    assert references_person(output, OTHER, tool_name="add_event") is True  # 진짜 인물 id 는 규칙 1


def test_schedule_out_id_equal_to_person_id_is_not_reference() -> None:
    """`ScheduleOut.id` 도 같다(V1-5)."""
    output = to_jsonable(_schedule_out(schedule_id=PID, person_id=OTHER))
    assert references_person(output, PID, tool_name="add_schedule") is False
    assert references_person(output, OTHER, tool_name="add_schedule") is True


# ---------------------------------------------------------------------------
# 규칙 1 -- person_id / matched_person_id 정수 값 (V1-7)
# ---------------------------------------------------------------------------


def test_tool_input_person_id() -> None:
    """툴 trace `input`(인자 그대로)의 `person_id`."""
    assert references_person({"person_id": PID, "type": "meal"}, PID) is True
    assert references_person({"person_id": OTHER, "type": "meal"}, PID) is False


def test_event_out_and_schedule_out_person_id() -> None:
    """`EventOut`/`ScheduleOut` 의 `person_id` 와 `BriefingOut` 안 이벤트·일정 `person_id`."""
    assert references_person(to_jsonable(_event_out(1, PID)), PID, tool_name="add_event") is True
    assert references_person(to_jsonable(_schedule_out(1, PID)), PID, tool_name="add_schedule") is True
    briefing = to_jsonable(
        BriefingOut(
            person=_person_out(OTHER),
            generated_at=NOW,
            recent_events=[_event_out(1, PID)],
        )
    )
    # person.id 는 OTHER, 이벤트의 person_id 만 PID -- 규칙 1 이 깊이 들어가 본다.
    assert references_person(briefing, PID, tool_name="get_briefing") is True


def test_er_resolution_candidates_person_id() -> None:
    """ER `er_resolve` output 의 `candidates[].person_id` 만 참인 구조."""
    resolution = Resolution(trace_id=1, mention="민수", candidates=[_scored(PID)])
    data = to_jsonable(resolution.to_dict())
    assert data["confidence_breakdown"] == {} and data["decision"] == {}
    assert references_person(data, PID, tool_name="er") is True
    assert references_person(data, OTHER, tool_name="er") is False


def test_er_breakdown_matched_person_id_only() -> None:
    """`confidence_breakdown.matched_person_id` 만 참인 구조(V1-7)."""
    data = to_jsonable(
        Resolution(
            trace_id=1, mention="민수", confidence_breakdown={"matched_person_id": PID, "s_llm": 0.9}
        ).to_dict()
    )
    assert data["candidates"] == [] and data["decision"] == {}
    assert references_person(data, PID, tool_name="er") is True
    assert references_person(data, OTHER, tool_name="er") is False


def test_er_decision_matched_person_id_only() -> None:
    """`decision.matched_person_id` 만 참인 구조(V1-7)."""
    data = to_jsonable(
        Resolution(trace_id=1, mention="민수", decision={"band": "merge", "matched_person_id": PID}).to_dict()
    )
    assert data["candidates"] == [] and data["confidence_breakdown"] == {}
    assert references_person(data, PID, tool_name="er") is True


def test_matched_person_id_none_is_not_reference() -> None:
    """`matched_person_id` 가 `None`(후보 없음·되묻기)이면 참조가 아니다."""
    assert references_person({"matched_person_id": None, "person_id": None}, PID) is False


def test_candidate_person_ids_list_elements() -> None:
    """`candidate_person_ids` 배열 원소(규칙 5, V1-7)."""
    assert references_person({"candidate_person_ids": [3, PID, 9]}, PID) is True
    assert references_person({"candidate_person_ids": [3, 9]}, PID) is False
    # 배열이 아니라 사전이면 규칙 5 대상이 아니다(값은 규칙 4 의 키만 본다).
    assert references_person({"candidate_person_ids": {"a": PID}}, PID) is False


def test_resume_schedule_person_id_in_pending_question_context() -> None:
    """`schedule` 질문 context 의 `resume.schedule.person_id`(`ScheduleResumeRef`)."""
    resume = PendingResume(
        mention="민수", schedule=ScheduleResumeRef(person_id=PID, title="회식", call_index=0)
    )
    context = to_jsonable({"mention": "민수", "resume": resume.to_dict()})
    assert references_person(context, PID) is True
    assert references_person(context, OTHER) is False


def test_loop_mention_decision_person_id() -> None:
    """루프 `loop_resolve` 의 `MentionDecision.person_id`."""
    decision = MentionDecision(mention="민수", index=0, band="merge", person_id=PID)
    assert references_person(to_jsonable(decision.to_dict()), PID) is True
    assert references_person(to_jsonable(MentionDecision("민수", 0, "identity").to_dict()), PID) is False


def test_deep_nesting_and_top_level_list() -> None:
    """깊이·배열 무관 -- 재귀로 끝까지 본다. 최상위가 배열이어도 된다."""
    assert references_person({"a": [{"b": {"c": [{"person_id": PID}]}}]}, PID) is True
    assert references_person([{"person_id": PID}], PID) is True
    assert references_person([[[{"matched_person_id": PID}]]], PID) is True


# ---------------------------------------------------------------------------
# 과잉 판정 금지 -- 같은 숫자의 다른 뜻 (V1-6)
# ---------------------------------------------------------------------------


def test_same_number_other_meanings_is_not_reference() -> None:
    """`considered_event_ids`·`schedule_id`·`question_id` 에만 같은 숫자가 있으면 거짓(V1-6)."""
    data = {
        "considered_event_ids": [PID],
        "event_ids": [PID],
        "schedule_id": PID,
        "question_id": PID,
        "pending_question_id": PID,
        "trace_id": PID,
        "fact_id": PID,
        "subscription_ids": [PID],
        "selected": [PID],
        "briefed": [PID],
    }
    assert references_person(data, PID) is False
    assert references_person(data, PID, tool_name="create_person") is False
    # 문자열 안의 숫자(발화·문장)도 아니다.
    assert references_person({"utterance": f"{PID}번 민수", "reply": f"id={PID}"}, PID) is False


def test_memory_promote_output_event_ids_only_is_not_reference() -> None:
    """`memory_promote` output 의 `considered_event_ids` 에만 같은 숫자 -- 그 인물 자신의
    `person_id` 는 다른 값이면 거짓."""
    output = {"person_id": OTHER, "considered_event_ids": [PID], "facts": []}
    assert references_person(output, PID) is False
    assert references_person(output, OTHER) is True


# ---------------------------------------------------------------------------
# 형 엄격성 (V1-8, V1-9)
# ---------------------------------------------------------------------------


def test_bool_is_not_integer_id() -> None:
    """`True == 1` 이지만 인물 id 1 의 참조가 아니다(V1-8). 모든 규칙 위치에서."""
    assert references_person({"person_id": True}, 1) is False
    assert references_person({"matched_person_id": True}, 1) is False
    assert references_person({"person": {"id": True}}, 1) is False
    assert references_person({"candidate_ids": {"a": True}}, 1) is False
    assert references_person({"person_ids": {"a": True}}, 1) is False
    assert references_person({"candidate_person_ids": [True]}, 1) is False
    assert references_person({"id": True}, 1, tool_name="create_person") is False
    assert references_person({"person_id": False}, 0) is False
    # 대조군 -- 진짜 정수 1 은 참조다.
    assert references_person({"person_id": 1}, 1) is True


def test_string_digits_are_not_integer_id() -> None:
    """문자열 `"42"`·실수 `42.0` 은 정수 id 가 아니다(V1-9, 결정 C-3 확정: 정수만)."""
    assert references_person({"person_id": str(PID)}, PID) is False
    assert references_person({"matched_person_id": str(PID)}, PID) is False
    assert references_person({"person": {"id": str(PID)}}, PID) is False
    assert references_person({"candidate_ids": {"a": str(PID)}}, PID) is False
    assert references_person({"candidate_person_ids": [str(PID)]}, PID) is False
    assert references_person({"id": str(PID)}, PID, tool_name="update_person") is False
    assert references_person({"person_id": float(PID)}, PID) is False


# ---------------------------------------------------------------------------
# 기타
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [None, 0, 1, "x", True, 1.5, [], {}, (), [None], {"a": None}])
def test_scalars_and_empties_are_not_reference(value: object) -> None:
    """스칼라·빈 컨테이너는 오류 없이 거짓이다."""
    assert references_person(value, PID) is False
    assert references_person(value, PID, tool_name="create_person") is False


def test_references_person_does_not_mutate_input() -> None:
    """판별은 입력을 바꾸지 않는다."""
    data = {"candidate_ids": {"민수": PID}, "a": [{"person": {"id": PID}}], "person_id": PID}
    before = copy.deepcopy(data)
    assert references_person(data, PID, tool_name="create_person") is True
    assert data == before
