"""Refs: P5b-query-turn U1 CR-004 D16 S3.4 원칙1 원칙4 원칙7 원칙9 R19 --
`intent` 필드·스키마·재개 재료·trace 어휘·상수 계약 테스트.
DB·LLM 없음 (U1 은 도는 분기가 없다 -- 계약 값만 값으로 단언한다)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app import settings
from app.agent import (
    INTENT_QUERY,
    INTENT_RECORD,
    INTENTS,
    LOOP_RESUME_VERSION,
    LOOP_TRACE_STEPS,
    PROPOSAL_ARG_SCHEMA,
    PROPOSAL_SCHEMA,
    STEP_LOOP_QUERY,
    FakeProposer,
    PendingResume,
    Proposal,
    validate_proposal,
)
from app.er.types import JudgeUnavailable

NOW = datetime(2026, 10, 29, 9, 0, tzinfo=timezone.utc)


def test_intents_values():
    assert INTENT_RECORD == "record"
    assert INTENT_QUERY == "query"
    assert INTENTS == ("record", "query")


def test_schema_intent_enum():
    assert set(PROPOSAL_SCHEMA["properties"]) == {"tool_calls", "intent"}
    assert PROPOSAL_SCHEMA["properties"]["intent"] == {
        "type": "string",
        "enum": ["record", "query"],
    }


def test_schema_required_unchanged():
    # intent 는 선택 키 -- required 는 tool_calls 만.
    assert PROPOSAL_SCHEMA["required"] == ["tool_calls"]


def test_schema_tool_calls_embeds_arg_schema():
    item = PROPOSAL_SCHEMA["properties"]["tool_calls"]["items"]
    assert item["properties"]["args"] is PROPOSAL_ARG_SCHEMA
    assert item["required"] == ["name", "args"]


def test_validate_proposal_missing_intent_is_record():
    assert validate_proposal({"tool_calls": []}).intent == "record"


def test_validate_proposal_null_intent_is_record():
    assert validate_proposal({"tool_calls": [], "intent": None}).intent == "record"


def test_validate_proposal_query_intent():
    assert validate_proposal({"tool_calls": [], "intent": "query"}).intent == "query"


def test_validate_proposal_record_intent():
    assert validate_proposal({"tool_calls": [], "intent": "record"}).intent == "record"


@pytest.mark.parametrize("bad", ["ask", "", "QUERY", 1, True, ["query"], {"a": 1}])
def test_validate_proposal_bad_intent_is_schema_error(bad):
    with pytest.raises(JudgeUnavailable) as excinfo:
        validate_proposal({"tool_calls": [], "intent": bad})
    assert str(excinfo.value) == "schema"


def test_proposal_default_intent_is_record():
    assert Proposal().intent == "record"


def test_proposal_to_dict_always_has_intent():
    assert Proposal().to_dict()["intent"] == "record"
    assert Proposal(intent="query").to_dict()["intent"] == "query"


def test_pending_resume_query_to_dict_has_intent():
    assert PendingResume(intent="query").to_dict()["intent"] == "query"


def test_pending_resume_default_omits_intent():
    assert PendingResume().intent == "record"
    assert "intent" not in PendingResume().to_dict()


def test_pending_resume_version_stays_one():
    assert LOOP_RESUME_VERSION == "1"
    assert PendingResume(intent="query").to_dict()["version"] == "1"


def test_step_loop_query_outside_trace_steps():
    assert STEP_LOOP_QUERY == "loop_query"
    assert STEP_LOOP_QUERY.startswith("loop_")
    assert STEP_LOOP_QUERY not in LOOP_TRACE_STEPS


def test_fake_proposer_intents_table():
    fake = FakeProposer(table={"u": []}, intents={"u": "query"})
    assert fake.propose("u", NOW).intent == "query"
    # 표에 없는 발화는 기록 턴
    assert fake.propose("other", NOW).intent == "record"


def test_fake_proposer_without_intents_is_record():
    assert FakeProposer(table={"u": []}).propose("u", NOW).intent == "record"


def test_query_constants_values():
    assert settings.QUERY_TIMELINE_LIMIT == 5
    assert settings.QUERY_MAX_PERSONS == 1
    assert settings.QUERY_ANSWER_MAX_LINES == 3
    assert settings.QUERY_ANSWER_MAX_CHARS == 240
    assert settings.QUERY_ANSWER_MAX_CHARS == 3 * settings.BRIEFING_SUGGESTION_MAX_CHARS
    assert not hasattr(settings, "QUERY_MORE_HINT")  # U3 몫
