"""Refs: P5b-query-turn CR-004 D16 S3.2 원칙1 원칙4 원칙7 원칙9 R19 -- U2 조회 턴
게이트(`app/agent/gate.py` 의 Q 관문)와 인식 프롬프트 문장 테스트.

네트워크·DB 를 쓰지 않는다. "실행 0회" 는 `app.tools.*` 를 스파이로 감싸
호출 횟수 0 으로 확인한다(`functools.wraps` 가 `__wrapped__` 를 남겨 게이트의
시그니처 대조가 그대로 동작한다). 기존 `tests/test_agent_gate.py` 는 건드리지
않고, 같은 제안 모양을 대조군(기록 턴)으로 다시 만든다.
"""

from __future__ import annotations

import functools
from datetime import datetime, timezone

import pytest

from app import tools as app_tools
from app.agent.gate import (
    GATE_REJECTION_REASONS,
    NOT_CALLABLE_BY_LLM,
    REASON_LIMIT,
    REASON_NOT_CALLABLE_BY_LLM,
    REASON_QUERY_TURN_NO_WRITE,
    REASON_UNKNOWN_TOOL,
    WRITE_TOOLS,
    GateConfig,
    check,
)
from app.agent.propose import FakeProposer, build_propose_prompt
from app.agent.types import (
    BUCKET_EXECUTE,
    BUCKET_HINT_ONLY,
    INTENT_QUERY,
    INTENT_RECORD,
    Proposal,
    ToolCallProposal,
)

NOW = datetime(2026, 9, 24, 19, 0, 0, tzinfo=timezone.utc)


def _call(name: str, **args) -> ToolCallProposal:
    return ToolCallProposal(name=name, args=args)


def _query(*calls: ToolCallProposal) -> Proposal:
    return Proposal(tool_calls=list(calls), raw={}, intent=INTENT_QUERY)


def _record(*calls: ToolCallProposal) -> Proposal:
    """`intent` 를 주지 않는다 -- 기본값(record)이 기존 동작임을 함께 확인."""
    return Proposal(tool_calls=list(calls), raw={})


def _add_event() -> ToolCallProposal:
    return _call("add_event", person="민수", type="meal", content="저녁", occurred_at=NOW)


def _add_schedule() -> ToolCallProposal:
    return _call("add_schedule", person="민수", title="저녁 약속", scheduled_at=NOW)


def _mk_update() -> ToolCallProposal:
    return _call("update_person", person="민수", new_alias="민수형")


def _mk_create() -> ToolCallProposal:
    return _call(
        "create_person",
        display_name="민수",
        aliases=["민수"],
        relation_tag="친구",
        hierarchy="동",
    )


def _spy_all(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """툴 7종 전부를 스파이로 바꿔 호출된 이름을 모은다(0 이어야 한다)."""
    called: list[str] = []
    for name in app_tools.TOOL_NAMES:
        real_fn = getattr(app_tools, name)

        def make(n: str, fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                called.append(n)
                return fn(*args, **kwargs)

            return wrapper

        monkeypatch.setattr(app_tools, name, make(name, real_fn))
    return called


# --- 어휘·집합 ---------------------------------------------------------------


def test_reason_value_and_vocabulary_order():
    assert REASON_QUERY_TURN_NO_WRITE == "query_turn_no_write"
    assert GATE_REJECTION_REASONS[-1] == REASON_QUERY_TURN_NO_WRITE
    assert len(GATE_REJECTION_REASONS) == 7
    assert len(set(GATE_REJECTION_REASONS)) == 7


def test_write_tools_equals_tool_names_minus_not_callable():
    assert WRITE_TOOLS == set(app_tools.TOOL_NAMES) - NOT_CALLABLE_BY_LLM
    assert WRITE_TOOLS == {"add_event", "add_schedule", "update_person", "create_person"}


# --- 조회 턴: 기록 툴 4건 거부 ----------------------------------------------


@pytest.mark.parametrize(
    "make",
    [_add_event, _add_schedule, _mk_update, _mk_create],
    ids=["add_event", "add_schedule", "update_person", "create_person"],
)
def test_query_turn_rejects_write_tools(make, monkeypatch):
    called = _spy_all(monkeypatch)
    call = make()
    verdict = check(_query(call))
    assert verdict.accepted == []
    assert len(verdict.rejected) == 1
    rej = verdict.rejected[0]
    assert (rej.index, rej.name, rej.reason) == (0, call.name, "query_turn_no_write")
    assert called == []


def test_query_turn_rejects_create_person(monkeypatch):
    called = _spy_all(monkeypatch)
    verdict = check(_query(_mk_create()))
    assert verdict.accepted == []
    assert [r.reason for r in verdict.rejected] == [REASON_QUERY_TURN_NO_WRITE]
    assert called == []


# --- 조회 턴: 내부 전용 툴은 ② 사유 그대로 ----------------------------------


@pytest.mark.parametrize("name", ["search_person", "ask_user", "get_briefing"])
def test_query_turn_not_callable_tools_keep_reason(name, monkeypatch):
    called = _spy_all(monkeypatch)
    verdict = check(_query(_call(name, query="민수")))
    assert verdict.accepted == []
    assert [r.reason for r in verdict.rejected] == [REASON_NOT_CALLABLE_BY_LLM]
    assert called == []


def test_query_turn_search_person_stays_not_callable():
    verdict = check(_query(_call("search_person", query="민수")))
    assert verdict.rejected[0].reason == "not_callable_by_llm"
    assert verdict.rejected[0].reason != REASON_QUERY_TURN_NO_WRITE


def test_query_turn_unknown_tool_stays_unknown(monkeypatch):
    called = _spy_all(monkeypatch)
    verdict = check(_query(_call("delete_person", person="민수")))
    assert [r.reason for r in verdict.rejected] == [REASON_UNKNOWN_TOOL]
    assert called == []


def test_query_turn_update_person_with_person_id_is_query_reason():
    """Q 가 ④ 보다 먼저 -- person_id 가 껴 있어도 사유는 새 사유(순서 고정)."""
    verdict = check(_query(_call("update_person", person_id=3, new_alias="민수형")))
    assert [r.reason for r in verdict.rejected] == [REASON_QUERY_TURN_NO_WRITE]


def test_query_turn_never_accepts_anything():
    verdict = check(
        _query(
            _add_event(),
            _add_schedule(),
            _mk_update(),
            _mk_create(),
            _call("search_person", query="민수"),
            _call("ask_user", kind="identity"),
            _call("get_briefing", person="민수"),
            _call("nope"),
        )
    )
    assert verdict.accepted == []
    assert len(verdict.rejected) == 8


def test_query_turn_has_no_limit_rejection_and_no_limit_stop():
    cfg = GateConfig(max_mentions=1, max_events=1, max_schedules=1, max_proposals=1)
    verdict = check(_query(_add_event(), _add_event(), _add_schedule(), _mk_update()), config=cfg)
    assert all(r.reason != REASON_LIMIT for r in verdict.rejected)
    assert verdict.stop_reason is None


def test_query_turn_via_fake_proposer():
    proposer = FakeProposer(
        table={
            "민수 뭐 좋아해?": [
                {
                    "name": "add_event",
                    "args": {
                        "person": "민수",
                        "type": "meal",
                        "content": "저녁",
                        "occurred_at": "2026-09-24T19:00:00+00:00",
                    },
                }
            ]
        },
        intents={"민수 뭐 좋아해?": "query"},
    )
    proposal = proposer.propose("민수 뭐 좋아해?", NOW)
    assert proposal.intent == INTENT_QUERY
    verdict = check(proposal)
    assert verdict.accepted == []
    assert [r.reason for r in verdict.rejected] == [REASON_QUERY_TURN_NO_WRITE]


# --- 기록 턴 대조군: 같은 제안이 기존 판정 그대로 -----------------------------


def test_record_turn_default_intent_is_record():
    assert _record().intent == INTENT_RECORD


@pytest.mark.parametrize(
    "make,bucket",
    [
        (_add_event, BUCKET_EXECUTE),
        (_add_schedule, BUCKET_EXECUTE),
        (_mk_update, BUCKET_EXECUTE),
        (_mk_create, BUCKET_HINT_ONLY),
    ],
    ids=["add_event", "add_schedule", "update_person", "create_person"],
)
def test_record_turn_write_tools_keep_old_verdict(make, bucket):
    call = make()
    verdict = check(_record(call))
    assert verdict.rejected == []
    assert [(a.name, a.bucket) for a in verdict.accepted] == [(call.name, bucket)]


@pytest.mark.parametrize("name", ["search_person", "ask_user", "get_briefing"])
def test_record_turn_not_callable_tools_keep_reason(name):
    verdict = check(_record(_call(name, query="민수")))
    assert [r.reason for r in verdict.rejected] == [REASON_NOT_CALLABLE_BY_LLM]


def test_record_turn_explicit_record_intent_same_as_default():
    explicit = Proposal(tool_calls=[_add_event()], raw={}, intent=INTENT_RECORD)
    assert check(explicit) == check(_record(_add_event()))


# --- 프롬프트 문장 -----------------------------------------------------------


def test_prompt_has_intent_classification_sentence():
    system, _ = build_propose_prompt("u", NOW)
    assert "intent 를 query" in system
    assert "record" in system
    assert "둘이 섞이면 query" in system


def test_prompt_has_query_mention_exception_sentences_after_old_sentence():
    system, _ = build_propose_prompt("u", NOW)
    exception = (
        "단, intent 가 query 일 때만 예외로, 물어본 인물마다 search_person 을 "
        "하나씩 제안하고 그 언급을 query 필드에 써라(person 필드에 써도 "
        "받아들인다). 이 제안은 실행되지 않고 대상 표시로만 쓰인다."
    )
    assert exception in system
    old = "절대 제안하지 마라."
    assert old in system
    assert system.index(old) < system.index(exception)
    # 바로 뒤 -- 사이에 다른 문장이 없다.
    assert system.index(old) + len(old) + 1 == system.index(exception)


def test_prompt_excludes_self_reference():
    system, _ = build_propose_prompt("u", NOW)
    assert "'나'·'저'·'내'·'제'" in system
    assert "사용자 자신을 가리키는 말은 인물로 제안하지 마라" in system
