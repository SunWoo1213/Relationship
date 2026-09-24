"""Refs: P5-loop S3.2 원칙1 원칙4 원칙9 -- U3 게이트(`app/agent/gate.py`) 테스트.

네트워크·DB 를 쓰지 않는다(`check()` 는 순수 함수, 01-plan U3 "세션 없이
돈다"). "실행 0회" 주장은 `app.tools.*` 함수를 `functools.wraps` 스파이로
감싸 호출 횟수를 세는 방식으로 확인한다 -- `functools.wraps` 가 남기는
`__wrapped__` 덕분에 `inspect.signature()` 가 여전히 원본 시그니처를
보므로(③ 인자 스키마 검사가 깨지지 않는다), 스파이를 끼워도 게이트의
`inspect.signature(app.tools.<name>)` 대조가 그대로 동작한다.
"""

from __future__ import annotations

import functools
from datetime import datetime, timezone

import pytest

from app.agent.gate import (
    GATE_REJECTION_REASONS,
    NOT_CALLABLE_BY_LLM,
    REASON_BAD_ARGS,
    REASON_LIMIT,
    REASON_NEEDS_CONFIRMATION,
    REASON_NOT_CALLABLE_BY_LLM,
    REASON_PERSON_ID_FROM_LLM,
    REASON_UNKNOWN_TOOL,
    GateConfig,
    check,
)
from app.agent.types import BUCKET_EXECUTE, BUCKET_HINT_ONLY, Proposal, ToolCallProposal
from app import tools as app_tools

NOW = datetime(2026, 9, 24, 19, 0, 0, tzinfo=timezone.utc)


def _call(name: str, **args) -> ToolCallProposal:
    return ToolCallProposal(name=name, args=args)


def _proposal(*calls: ToolCallProposal) -> Proposal:
    return Proposal(tool_calls=list(calls), raw={})


def _valid_add_event(person: str = "민수") -> ToolCallProposal:
    return _call(
        "add_event",
        person=person,
        type="meal",
        content=f"{person}와 저녁",
        occurred_at=NOW,
    )


def _valid_add_schedule(person: str = "민수") -> ToolCallProposal:
    return _call("add_schedule", person=person, title="저녁 약속", scheduled_at=NOW)


def _valid_create_person() -> ToolCallProposal:
    return _call(
        "create_person",
        display_name="민수",
        aliases=["민수"],
        relation_tag="친구",
        hierarchy="동",
    )


def _spy(monkeypatch: pytest.MonkeyPatch, name: str) -> list[tuple]:
    """`app.tools.<name>` 을 스파이로 바꿔치고 호출 인자 목록을 돌려준다.
    `functools.wraps` 가 `__wrapped__` 를 남겨 `inspect.signature()` 가
    원본 시그니처를 그대로 본다."""

    real_fn = getattr(app_tools, name)
    calls: list[tuple] = []

    @functools.wraps(real_fn)
    def wrapper(*args, **kwargs):
        calls.append((args, kwargs))
        return real_fn(*args, **kwargs)

    monkeypatch.setattr(app_tools, name, wrapper)
    return calls


# ---------------------------------------------------------------------------
# ④ person_id 금지 -- L(iii) 핵심 방어 (판정 표 19행)
# ---------------------------------------------------------------------------


def test_person_id_from_llm_rejects_and_does_not_call_update_person(monkeypatch):
    calls = _spy(monkeypatch, "update_person")
    proposal = _proposal(_call("update_person", person_id=3, new_alias="민수"))

    verdict = check(proposal)

    assert verdict.accepted == []
    assert len(verdict.rejected) == 1
    assert verdict.rejected[0].reason == REASON_PERSON_ID_FROM_LLM
    assert verdict.rejected[0].index == 0
    assert calls == []


def test_person_id_from_llm_applies_regardless_of_tool():
    # add_event 도 person_id 를 직접 주면 person_id_from_llm 이다 -- ③(bad_args)
    # 보다 ④ 가 먼저 걸린다(01-plan 28행 "④ 를 먼저 둬야 … 사유가 따로 남는다").
    proposal = _proposal(
        _call("add_event", person_id=3, type="meal", content="x", occurred_at=NOW)
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_PERSON_ID_FROM_LLM


# ---------------------------------------------------------------------------
# ① 화이트리스트 / ② 호출 가능 집합 (판정 표 20행)
# ---------------------------------------------------------------------------


def test_unknown_tool_name_rejected():
    proposal = _proposal(_call("delete_person", person="민수"))
    verdict = check(proposal)
    assert verdict.accepted == []
    assert len(verdict.rejected) == 1
    assert verdict.rejected[0].reason == REASON_UNKNOWN_TOOL
    assert verdict.rejected[0].name == "delete_person"


@pytest.mark.parametrize("name", sorted(NOT_CALLABLE_BY_LLM))
def test_not_callable_by_llm_rejected(name, monkeypatch):
    calls = _spy(monkeypatch, name)
    # 각 툴에 맞는 최소 인자를 준다 -- ②에서 이미 걸려야 하므로 인자
    # 내용 자체는 검사되지 않는다(③ 까지 가지 않는다).
    args = {
        "search_person": {"query": "민수"},
        "ask_user": {"kind": "identity", "question": "?", "options": ["a"], "context": {}},
        "get_briefing": {"person_id": 1},
    }[name]
    proposal = _proposal(_call(name, **args))

    verdict = check(proposal)

    assert verdict.accepted == []
    assert verdict.rejected[0].reason == REASON_NOT_CALLABLE_BY_LLM
    assert calls == []


# ---------------------------------------------------------------------------
# ③ 인자 스키마 -- bad_args (판정 표 21행, R-11 세 케이스)
# ---------------------------------------------------------------------------


def test_bad_args_missing_required():
    proposal = _proposal(_call("add_event", person="민수", type="meal"))  # content 누락
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_bad_args_unknown_key():
    proposal = _proposal(
        _call("add_event", person="민수", type="meal", content="c", occurred_at=NOW, extra="x")
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_bad_args_type_violation_event_type_not_in_fixed_set():
    proposal = _proposal(
        _call("add_event", person="민수", type="hangout", content="c", occurred_at=NOW)
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_bad_args_type_violation_wrong_python_type():
    proposal = _proposal(
        _call("add_event", person="민수", type="meal", content=123, occurred_at=NOW)
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_bad_args_raw_utterance_rejected_no_overwrite(monkeypatch):
    """R-11 -- LLM 이 raw_utterance 를 주면 bad_args 로 거부한다(원문은 루프가
    주입, 덮어쓰기 없음). 실행도 0회다."""
    calls = _spy(monkeypatch, "add_event")
    proposal = _proposal(
        _call(
            "add_event",
            person="민수",
            type="meal",
            content="c",
            occurred_at=NOW,
            raw_utterance="LLM 이 지어낸 원문",
        )
    )
    verdict = check(proposal)
    assert verdict.accepted == []
    assert verdict.rejected[0].reason == REASON_BAD_ARGS
    assert calls == []


def test_needs_confirmation_update_person_display_name(monkeypatch):
    """R-11 -- update_person 제안에 display_name 이 있으면 needs_confirmation
    (D6). 실행 0회."""
    calls = _spy(monkeypatch, "update_person")
    proposal = _proposal(_call("update_person", person="민수", display_name="새이름"))
    verdict = check(proposal)
    assert verdict.accepted == []
    assert verdict.rejected[0].reason == REASON_NEEDS_CONFIRMATION
    assert calls == []


def test_update_person_valid_facts_accepted():
    proposal = _proposal(
        _call("update_person", person="민수", facts=[{"key": "생일", "value": "3월"}])
    )
    verdict = check(proposal)
    assert verdict.rejected == []
    assert verdict.accepted[0].bucket == BUCKET_EXECUTE


# ---------------------------------------------------------------------------
# create_person -- hint_only 버킷, rejected 아님 (판정 표 21행 R-11 세 번째 케이스)
# ---------------------------------------------------------------------------


def test_create_person_hint_only_bucket_not_rejected_not_called(monkeypatch):
    calls = _spy(monkeypatch, "create_person")
    proposal = _proposal(_valid_create_person())

    verdict = check(proposal)

    assert verdict.rejected == []
    assert len(verdict.accepted) == 1
    assert verdict.accepted[0].bucket == BUCKET_HINT_ONLY
    assert verdict.accepted[0].name == "create_person"
    assert calls == []


def test_create_person_bad_args_still_rejected():
    # hint_only 는 ①②④③ 을 모두 지난 뒤에만 붙는다 -- 스키마 위반이면
    # create_person 도 bad_args 로 거부된다(무조건 통과가 아니다).
    proposal = _proposal(_call("create_person", display_name="민수"))  # aliases 등 누락
    verdict = check(proposal)
    assert verdict.accepted == []
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_execute_bucket_for_non_create_person_tools():
    proposal = _proposal(_valid_add_event(), _valid_add_schedule())
    verdict = check(proposal)
    assert verdict.rejected == []
    assert [a.bucket for a in verdict.accepted] == [BUCKET_EXECUTE, BUCKET_EXECUTE]


# ---------------------------------------------------------------------------
# R-23 -- occurred_at/scheduled_at 미확정(None) 은 통과, 파싱 실패 문자열은 거부
# ---------------------------------------------------------------------------


def test_schedule_scheduled_at_none_is_not_rejected():
    proposal = _proposal(_call("add_schedule", person="민수", title="약속", scheduled_at=None))
    verdict = check(proposal)
    assert verdict.rejected == []
    assert verdict.accepted[0].bucket == BUCKET_EXECUTE


def test_schedule_scheduled_at_missing_is_not_rejected():
    proposal = _proposal(_call("add_schedule", person="민수", title="약속"))
    verdict = check(proposal)
    assert verdict.rejected == []


def test_schedule_scheduled_at_unparsed_string_is_bad_args():
    # U2 _convert_datetime_args 가 파싱에 실패하면 문자열이 그대로 남는다 --
    # 이건 "미확정"이 아니라 형식 오류다(R-23).
    proposal = _proposal(
        _call("add_schedule", person="민수", title="약속", scheduled_at="다음 주 언젠가")
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


def test_event_occurred_at_none_is_not_rejected():
    proposal = _proposal(
        _call("add_event", person="민수", type="meal", content="c", occurred_at=None)
    )
    verdict = check(proposal)
    assert verdict.rejected == []


def test_event_occurred_at_unparsed_string_is_bad_args():
    proposal = _proposal(
        _call("add_event", person="민수", type="meal", content="c", occurred_at="어제 저녁")
    )
    verdict = check(proposal)
    assert verdict.rejected[0].reason == REASON_BAD_ARGS


# ---------------------------------------------------------------------------
# ⑤ 상한 -- 결정 A(i)·R-13 (판정 표 "상한 초과분" 부정 케이스)
# ---------------------------------------------------------------------------


def test_limit_mentions_exceeded_rejects_excess_and_sets_stop_reason():
    cfg = GateConfig(max_mentions=2, max_events=99, max_schedules=99, max_proposals=99)
    proposal = _proposal(
        _valid_add_event("민수"),
        _valid_add_event("지훈"),
        _valid_add_event("영희"),  # 세 번째 새 언급 -- 상한 2 초과
    )
    verdict = check(proposal, config=cfg)
    assert [a.index for a in verdict.accepted] == [0, 1]
    assert verdict.rejected == [verdict.rejected[0]]
    assert verdict.rejected[0].index == 2
    assert verdict.rejected[0].reason == REASON_LIMIT
    assert verdict.stop_reason == REASON_LIMIT


def test_limit_mentions_repeated_mention_does_not_count_twice():
    cfg = GateConfig(max_mentions=1, max_events=99, max_schedules=99, max_proposals=99)
    proposal = _proposal(_valid_add_event("민수"), _valid_add_event("민수"))
    verdict = check(proposal, config=cfg)
    # 같은 언급("민수")이 두 번 -- 언급 상한(1)을 넘기지 않는다.
    assert verdict.rejected == []
    assert len(verdict.accepted) == 2


def test_limit_events_exceeded():
    cfg = GateConfig(max_mentions=99, max_events=1, max_schedules=99, max_proposals=99)
    proposal = _proposal(_valid_add_event("민수"), _valid_add_event("지훈"))
    verdict = check(proposal, config=cfg)
    assert [a.index for a in verdict.accepted] == [0]
    assert verdict.rejected[0].index == 1
    assert verdict.rejected[0].reason == REASON_LIMIT


def test_limit_schedules_exceeded():
    cfg = GateConfig(max_mentions=99, max_events=99, max_schedules=1, max_proposals=99)
    proposal = _proposal(_valid_add_schedule("민수"), _valid_add_schedule("지훈"))
    verdict = check(proposal, config=cfg)
    assert [a.index for a in verdict.accepted] == [0]
    assert verdict.rejected[0].index == 1
    assert verdict.rejected[0].reason == REASON_LIMIT


def test_limit_total_proposals_exceeded():
    cfg = GateConfig(max_mentions=99, max_events=99, max_schedules=99, max_proposals=1)
    proposal = _proposal(
        _valid_create_person(),  # hint_only -- 그래도 총 상한에는 든다
        _valid_add_event("민수"),
    )
    verdict = check(proposal, config=cfg)
    assert [a.index for a in verdict.accepted] == [0]
    assert verdict.rejected[0].index == 1
    assert verdict.rejected[0].reason == REASON_LIMIT
    assert verdict.stop_reason == REASON_LIMIT


def test_limit_does_not_count_already_rejected_proposals():
    # 총 상한 1 이지만 첫 제안이 이미 unknown_tool 로 거부됐다 -- limit 은
    # ①②④③ 통과분에만 적용된다(적용 순서 ①②④③⑤).
    cfg = GateConfig(max_mentions=99, max_events=99, max_schedules=99, max_proposals=1)
    proposal = _proposal(_call("delete_person", person="민수"), _valid_add_event("민수"))
    verdict = check(proposal, config=cfg)
    assert [a.index for a in verdict.accepted] == [1]
    assert {r.reason for r in verdict.rejected} == {REASON_UNKNOWN_TOOL}


def test_default_config_matches_settings():
    from app.settings import (
        LOOP_MAX_EVENTS,
        LOOP_MAX_MENTIONS,
        LOOP_MAX_PROPOSALS,
        LOOP_MAX_SCHEDULES,
    )

    verdict = check(_proposal())
    assert verdict.limits.mentions == LOOP_MAX_MENTIONS
    assert verdict.limits.events == LOOP_MAX_EVENTS
    assert verdict.limits.schedules == LOOP_MAX_SCHEDULES
    assert verdict.limits.proposals == LOOP_MAX_PROPOSALS


# ---------------------------------------------------------------------------
# 거부 사유가 loop_gate output(GateVerdict.to_dict()) 에 남는다 (판정 표 22행)
# ---------------------------------------------------------------------------


def test_rejected_reason_appears_in_verdict_to_dict():
    proposal = _proposal(_call("update_person", person_id=3, new_alias="민수"))
    verdict = check(proposal)
    payload = verdict.to_dict()
    assert payload["rejected"] == [{"index": 0, "name": "update_person", "reason": "person_id_from_llm"}]
    assert payload["accepted"] == []


def test_all_rejection_reasons_are_in_vocabulary():
    proposal = _proposal(
        _call("delete_person", person="x"),  # unknown_tool
        _call("search_person", query="x"),  # not_callable_by_llm
        _call("update_person", person_id=1),  # person_id_from_llm
        _call("add_event", person="x", type="bad-type", content="c", occurred_at=NOW),  # bad_args
        _call("update_person", person="x", display_name="y"),  # needs_confirmation
        _valid_add_event("A"),  # ①②④③ 통과 -- 총 상한 1 을 채운다
        _valid_add_event("B"),  # ①②④③ 통과하지만 총 상한 초과 -- limit
    )
    verdict = check(proposal, config=GateConfig(max_proposals=1))
    reasons = {r.reason for r in verdict.rejected}
    assert reasons.issubset(set(GATE_REJECTION_REASONS))
    assert reasons == {
        REASON_UNKNOWN_TOOL,
        REASON_NOT_CALLABLE_BY_LLM,
        REASON_PERSON_ID_FROM_LLM,
        REASON_BAD_ARGS,
        REASON_NEEDS_CONFIRMATION,
        REASON_LIMIT,
    }
    assert [a.index for a in verdict.accepted] == [5]


# ---------------------------------------------------------------------------
# 게이트는 순수 함수 -- 어떤 경우에도 app.tools.* 를 호출하지 않는다
# ---------------------------------------------------------------------------


def test_gate_never_calls_any_tool_regardless_of_verdict(monkeypatch):
    spies = {name: _spy(monkeypatch, name) for name in app_tools.TOOL_NAMES}
    proposal = _proposal(
        _valid_add_event(),
        _valid_add_schedule(),
        _valid_create_person(),
        _call("update_person", person_id=3, new_alias="x"),
        _call("update_person", person="민수", display_name="새이름"),
        _call("search_person", query="민수"),
        _call("ask_user", kind="identity", question="?", options=["a"], context={}),
        _call("get_briefing", person_id=1),
        _call("delete_person", person="민수"),
    )
    check(proposal)
    assert all(calls == [] for calls in spies.values())


def test_empty_proposal_returns_empty_verdict():
    verdict = check(_proposal())
    assert verdict.accepted == []
    assert verdict.rejected == []
    assert verdict.stop_reason is None
