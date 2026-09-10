"""Refs: P3-baselines S3.7 D3 원칙4 원칙8 -- U5 베이스라인 3(LLM 단일 프롬프트) 테스트.

**네트워크 0·실 키 0**(원칙8) -- 공급자 SDK 클라이언트 자리에 스텁을 주입해
검증한다(`tests/test_er_judge.py` 와 같은 방식). 실 API 1회 호출은
`scripts/baseline_smoke.py` 를 사용자가 직접 돌린다.

네 층으로 나눠 본다.

1. **프롬프트 층** -- 요청 본문에 사전 상태 **인물 전체**(id·표시 이름·
   별칭·관계 태그·위계)가 들어가고, 온도가 0 이며, 모델 이름이
   `ANTHROPIC_MODEL`/`OPENAI_MODEL`(R-4)에서 오고, 도구 호출이 강제되는지.
2. **파싱·변환 층**(순수) -- 세 결정이 그대로 옮겨지는지, 강등 5경로,
   `candidate_person_ids` 필터와 `dropped_ids`(결정 I), `s_llm` clamp.
3. **오류 층** -- SDK 예외 4종 + 스키마 위반이 P3-er `llm.error` 어휘로
   나오고(결정 J: `call_with_error_mapping` 재사용) 예외가 아니라 `identity`
   강등으로 흡수되는지(불변 규약 2).
4. **DB 층**(실 PostgreSQL, 롤백 픽스처) -- 사전 상태 조회만 하고 어떤
   테이블도 늘지 않는지(불변 규약 1), `get_resolver` 주입 경로,
   `ALL_METHODS` 5종 순서.

키 미노출은 별도 절에서 본다 -- 키 자리에 **가짜 표식 문자열**을 넣고
요청 본문·`detail`·`to_dict()`·예외 문자열 어디에도 그 표식이 없음을
단언한다(security.md §1). 실 키는 쓰지 않는다.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx
import httpx2
import openai
import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.judge import call_with_error_mapping
from app.er.types import ERConfig, JudgeUnavailable
from app.tools.context import ToolContext
from evaluation.resolvers import DECISIONS, RESOLVERS, get_resolver
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.exact_match import KnownPerson
from evaluation.resolvers.llm_single import (
    EMPTY_MENTION,
    IDENTITY_WITHOUT_CANDIDATES,
    MERGE_WITHOUT_PERSON_ID,
    METHOD_NAME,
    OUT_OF_RANGE_ID,
    RESOLUTION_SCHEMA,
    TOOL_NAME,
    UNKNOWN_DECISION_PREFIX,
    ClaudeSingleCaller,
    LLMSingleResolver,
    OpenAISingleCaller,
    build_decision,
    build_prompt,
    caller_from_env,
    resolve_from_state,
    validate_resolution,
)

CONFIG = ERConfig()
USER_ID = "llm-single-user"

#: 키 유출 탐지용 **표식 문자열**(실 키가 아니고 네트워크로 나가지도
#: 않는다). 이 표식이 요청 본문·detail·출력·예외에 나타나면 유출 경로가
#: 있다는 뜻이다.
LEAK_CANARY = "CANARY-VALUE-MUST-NOT-APPEAR-IN-OUTPUT"

#: 순수 층이 공유하는 사전 상태 3명.
PERSONS = [
    KnownPerson(
        person_id=1,
        display_name="김민수",
        names=("팀장", "김팀장"),
        relation_tag="직장",
        hierarchy="상",
    ),
    KnownPerson(
        person_id=2,
        display_name="박민수",
        names=("민수",),
        relation_tag="친구",
        hierarchy="동",
    ),
    KnownPerson(person_id=3, display_name="이영희", relation_tag="직장", hierarchy="동"),
]


# ---------------------------------------------------------------------------
# 스텁 클라이언트 (네트워크 없음) -- tests/test_er_judge.py 와 같은 형태
# ---------------------------------------------------------------------------


class _StubMessages:
    def __init__(self, outer: "StubClaudeClient") -> None:
        self._outer = outer

    def create(self, **kwargs):
        self._outer.calls.append(kwargs)
        if isinstance(self._outer.response, BaseException):
            raise self._outer.response
        return self._outer.response


class StubClaudeClient:
    """`anthropic.Anthropic` 을 흉내 내는 스텁 -- `messages.create()` 만."""

    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.messages = _StubMessages(self)


class _StubCompletions:
    def __init__(self, outer: "StubOpenAIClient") -> None:
        self._outer = outer

    def create(self, **kwargs):
        self._outer.calls.append(kwargs)
        if isinstance(self._outer.response, BaseException):
            raise self._outer.response
        return self._outer.response


class _StubChat:
    def __init__(self, outer: "StubOpenAIClient") -> None:
        self.completions = _StubCompletions(outer)


class StubOpenAIClient:
    """`openai.OpenAI` 를 흉내 내는 스텁 -- `chat.completions.create()` 만."""

    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.chat = _StubChat(self)


def _payload(
    decision: str = "merge",
    matched_person_id: Any = 1,
    s_llm: Any = 0.9,
    reason: str = "별칭 일치",
    candidate_person_ids: Any = (),
) -> dict:
    return {
        "decision": decision,
        "matched_person_id": matched_person_id,
        "s_llm": s_llm,
        "reason": reason,
        "candidate_person_ids": list(candidate_person_ids),
    }


def _claude_response(payload: dict, *, tokens=(120, 30), model="claude-sonnet-5"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=TOOL_NAME, input=payload)],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model=model,
        stop_reason="tool_use",
    )


def _openai_response(payload: dict, *, tokens=(120, 30), model="gpt-4o-mini"):
    function = SimpleNamespace(
        name=TOOL_NAME, arguments=json.dumps(payload, ensure_ascii=False)
    )
    message = SimpleNamespace(tool_calls=[SimpleNamespace(function=function)])
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=SimpleNamespace(prompt_tokens=tokens[0], completion_tokens=tokens[1]),
        model=model,
    )


def _anthropic_request(url: str = "https://api.anthropic.com/v1/messages") -> httpx2.Request:
    return httpx2.Request("POST", url)


def _openai_request(url: str = "https://api.openai.com/v1/chat/completions") -> httpx.Request:
    return httpx.Request("POST", url)


def _claude_caller(payload_or_exc, **kw) -> tuple[ClaudeSingleCaller, StubClaudeClient]:
    response = (
        payload_or_exc
        if isinstance(payload_or_exc, BaseException)
        else _claude_response(payload_or_exc)
    )
    client = StubClaudeClient(response)
    return ClaudeSingleCaller(client=client, **kw), client


def _openai_caller(payload_or_exc, **kw) -> tuple[OpenAISingleCaller, StubOpenAIClient]:
    response = (
        payload_or_exc
        if isinstance(payload_or_exc, BaseException)
        else _openai_response(payload_or_exc)
    )
    client = StubOpenAIClient(response)
    return OpenAISingleCaller(client=client, **kw), client


# =========================================================================
# 1. 프롬프트 층 -- 요청 본문
# =========================================================================


def test_prompt_contains_every_person_in_state() -> None:
    """후보를 미리 좁혀 주지 않는다 -- 사전 상태 **전체**가 들어간다
    (01-plan 57행, 원칙8: 베이스라인을 약하게 만들지 않는다)."""

    system, user_text = build_prompt("부장님", "부장님이 회식 잡으래", PERSONS)

    for person in PERSONS:
        assert f'"person_id": {person.person_id}' in user_text
        assert person.display_name in user_text
        for alias in person.names:
            assert alias in user_text
    assert "직장" in user_text and "상" in user_text  # relation_tag·hierarchy
    assert "부장님" in user_text and "회식" in user_text
    assert TOOL_NAME in system


def test_prompt_person_list_is_empty_marker_when_state_is_empty() -> None:
    system, user_text = build_prompt("부장님", "발화", [])

    assert "(없음)" in user_text
    assert TOOL_NAME in system


def test_prompt_is_deterministic() -> None:
    """같은 입력 -> 같은 프롬프트(원칙8 재현성)."""
    assert build_prompt("부장님", "발화", PERSONS) == build_prompt("부장님", "발화", PERSONS)


def test_claude_request_forces_tool_choice_temperature_zero_and_model_from_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test-model")
    caller, client = _claude_caller(_payload())

    resolve_from_state(PERSONS, "부장님", "발화", caller=caller)

    assert len(client.calls) == 1  # LLM 호출 정확히 1회(01-plan 115행)
    kwargs = client.calls[0]
    assert kwargs["model"] == "claude-test-model"
    assert kwargs["temperature"] == 0
    assert kwargs["tool_choice"] == {"type": "tool", "name": TOOL_NAME}
    assert kwargs["tools"][0]["input_schema"] is RESOLUTION_SCHEMA
    assert kwargs["tools"][0]["name"] == TOOL_NAME
    body = kwargs["messages"][0]["content"]
    for person in PERSONS:
        assert person.display_name in body


def test_openai_request_forces_tool_choice_temperature_zero_and_model_from_env(
    monkeypatch,
) -> None:
    """R-4 -- OpenAI 경로는 `OPENAI_MODEL` 을 읽는다(기본값으로 조용히
    떨어지면 "제안 방식과 같은 모델" 보장이 깨진다)."""

    monkeypatch.setenv("OPENAI_MODEL", "gpt-test-model")
    caller, client = _openai_caller(_payload(matched_person_id=2))

    resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["model"] == "gpt-test-model"
    assert kwargs["temperature"] == 0
    assert kwargs["tool_choice"] == {
        "type": "function",
        "function": {"name": TOOL_NAME},
    }
    assert kwargs["tools"][0]["function"]["parameters"] is RESOLUTION_SCHEMA
    body = kwargs["messages"][1]["content"]
    for person in PERSONS:
        assert person.display_name in body


@pytest.mark.parametrize(
    ("env_name", "value", "factory"),
    [
        ("ANTHROPIC_MODEL", "claude-x", ClaudeSingleCaller),
        ("OPENAI_MODEL", "gpt-x", OpenAISingleCaller),
    ],
)
def test_caller_model_defaults_follow_env(monkeypatch, env_name, value, factory) -> None:
    monkeypatch.setenv(env_name, value)
    caller = factory(client=object())
    assert caller.model == value


@pytest.mark.parametrize(
    ("factory", "default"),
    [(ClaudeSingleCaller, "claude-sonnet-5"), (OpenAISingleCaller, "gpt-4o-mini")],
)
def test_caller_model_defaults_without_env(monkeypatch, factory, default) -> None:
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert factory(client=object()).model == default


def test_schema_matches_decision_I_shape() -> None:
    """응답 스키마 = 결정 E(ii) + 결정 I(`candidate_person_ids`)."""
    properties = RESOLUTION_SCHEMA["properties"]

    assert set(properties) == {
        "decision",
        "matched_person_id",
        "s_llm",
        "reason",
        "candidate_person_ids",
    }
    assert properties["decision"]["enum"] == list(DECISIONS)
    assert properties["candidate_person_ids"]["items"] == {"type": "integer"}
    assert RESOLUTION_SCHEMA["additionalProperties"] is False


def test_caller_from_env_selects_provider(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert isinstance(caller_from_env(client=object()), ClaudeSingleCaller)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    assert isinstance(caller_from_env(client=object()), OpenAISingleCaller)


@pytest.mark.parametrize("provider", ["gemini", "llama"])
def test_caller_from_env_rejects_unimplemented_provider(provider: str) -> None:
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        caller_from_env({"LLM_PROVIDER": provider})


def test_error_mapping_helper_is_reused_not_reimplemented() -> None:
    """결정 J -- `app.er.judge.call_with_error_mapping` 을 그대로 쓴다
    (오류 어휘의 단일 출처)."""
    from evaluation.resolvers import llm_single

    assert llm_single.call_with_error_mapping is call_with_error_mapping


# =========================================================================
# 2. 파싱·변환 층 (순수)
# =========================================================================


@pytest.mark.parametrize("caller_factory", [_claude_caller, _openai_caller])
def test_merge_is_carried_through(caller_factory) -> None:
    caller, _ = caller_factory(
        _payload(decision="merge", matched_person_id=1, s_llm=0.93)
    )

    decision = resolve_from_state(PERSONS, "김팀장", "발화", caller=caller)

    assert decision.method == METHOD_NAME
    assert decision.decision == "merge"
    assert decision.person_id == 1
    assert decision.score == pytest.approx(0.93)
    assert [c.person_id for c in decision.candidates] == [1]
    assert decision.candidates[0].signals == {"s_llm": pytest.approx(0.93)}
    assert decision.detail["forced_reason"] is None
    assert decision.detail["ask_kind"] is None
    assert decision.tokens_in == 120 and decision.tokens_out == 30


@pytest.mark.parametrize("caller_factory", [_claude_caller, _openai_caller])
def test_identity_keeps_candidate_ids_and_no_person_id(caller_factory) -> None:
    """`identity` 는 사람에게 묻는다 -- 인물을 고르지 않고 후보 목록이
    답이다(불변 규약 3, 결정 I)."""

    caller, _ = caller_factory(
        _payload(
            decision="identity",
            matched_person_id=None,
            s_llm=0.5,
            candidate_person_ids=(1, 2),
        )
    )

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert [c.person_id for c in decision.candidates] == [1, 2]
    assert [c.score for c in decision.candidates] == [0.0, 0.0]
    assert decision.detail["forced_reason"] is None
    assert decision.detail["ask_kind"] == "identity"


@pytest.mark.parametrize("caller_factory", [_claude_caller, _openai_caller])
def test_new_person_is_carried_through(caller_factory) -> None:
    caller, _ = caller_factory(
        _payload(decision="new_person", matched_person_id=None, s_llm=0.1)
    )

    decision = resolve_from_state(PERSONS, "지훈이", "발화", caller=caller)

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.candidates == []
    assert decision.detail["forced_reason"] is None
    assert decision.detail["ask_kind"] == "new_person"


def test_merge_puts_matched_person_first_in_candidates() -> None:
    caller, _ = _claude_caller(
        _payload(decision="merge", matched_person_id=2, candidate_person_ids=(1, 2))
    )

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert decision.decision == "merge"
    assert [c.person_id for c in decision.candidates] == [2, 1]


def test_candidate_ids_outside_state_are_dropped_and_recorded() -> None:
    """결정 I -- 사전 상태 밖 id(환각)는 후보가 되지 못하고
    `detail["dropped_ids"]` 에 기록된다."""

    caller, _ = _claude_caller(
        _payload(
            decision="identity",
            matched_person_id=None,
            candidate_person_ids=(1, 999, 2, "x"),
        )
    )

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert [c.person_id for c in decision.candidates] == [1, 2]
    assert decision.detail["dropped_ids"] == [999, "x"]
    assert decision.detail["forced_reason"] is None


def test_duplicate_candidate_ids_are_deduped_in_order() -> None:
    caller, _ = _claude_caller(
        _payload(
            decision="identity", matched_person_id=None, candidate_person_ids=(2, 1, 2)
        )
    )

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert [c.person_id for c in decision.candidates] == [2, 1]


@pytest.mark.parametrize(
    ("raw_s_llm", "expected"), [(1.4, 1.0), (-0.2, 0.0), (float("nan"), 0.0)]
)
def test_out_of_range_s_llm_is_clamped(raw_s_llm, expected) -> None:
    """자기보고 점수의 눈금이 어긋난 것은 그 방식의 성질이다 -- 결정을
    버리지 않고 접은 뒤 사실을 남긴다(불변 규약 2)."""

    caller, _ = _claude_caller(
        _payload(decision="merge", matched_person_id=1, s_llm=raw_s_llm)
    )

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "merge"
    assert decision.score == expected
    assert decision.detail["score_clamped"] is True


def test_score_is_not_marked_clamped_when_in_range() -> None:
    caller, _ = _claude_caller(_payload(s_llm=0.42))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert "score_clamped" not in decision.detail


def test_detail_records_raw_decision_and_prompt_size_only() -> None:
    """`detail` 에는 프롬프트 **길이**와 인물 수만 남는다 -- 원문은 어디에도
    저장하지 않는다(security.md §1)."""

    caller, _ = _claude_caller(_payload(reason="별칭군 일치"))

    decision = resolve_from_state(PERSONS, "김팀장", "회식 얘기", caller=caller)
    detail = decision.detail

    assert detail["raw_decision"] == "merge"
    assert detail["raw_matched_person_id"] == 1
    assert detail["reason"] == "별칭군 일치"
    assert detail["person_count"] == len(PERSONS)
    assert detail["prompt_chars"] > 0
    assert detail["llm_calls"] == 1
    assert detail["provider"] == "anthropic"
    assert detail["model"] == "claude-sonnet-5"
    assert (detail["uses_embedding"], detail["uses_llm"]) == (False, True)
    assert (detail["uses_rules"], detail["uses_thresholds"]) == (False, False)
    serialized = json.dumps(decision.to_dict(), ensure_ascii=False)
    assert "이미 아는 인물 목록" not in serialized


def test_to_dict_is_json_serializable() -> None:
    caller, _ = _claude_caller(
        _payload(decision="identity", matched_person_id=None, candidate_person_ids=(1, 7))
    )

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)
    restored = json.loads(json.dumps(decision.to_dict(), ensure_ascii=False))

    assert restored["method"] == METHOD_NAME
    assert restored["detail"]["dropped_ids"] == [7]


def test_same_stubbed_input_gives_same_decision() -> None:
    """스텁을 고정하면 같은 입력에 같은 결정(원칙8 -- 자동 테스트는
    결정적이어야 한다)."""

    first, _ = _claude_caller(_payload())
    second, _ = _claude_caller(_payload())

    a = resolve_from_state(PERSONS, "김팀장", "발화", caller=first)
    b = resolve_from_state(PERSONS, "김팀장", "발화", caller=second)

    assert a.to_dict() == b.to_dict()


# --- 강등 5경로 ------------------------------------------------------------


def test_downgrade_unknown_decision_word() -> None:
    caller, _ = _claude_caller(_payload(decision="link", matched_person_id=1))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] == f"{UNKNOWN_DECISION_PREFIX}link"
    assert decision.detail["raw_decision"] == "link"


def test_downgrade_matched_id_outside_state() -> None:
    caller, _ = _claude_caller(_payload(decision="merge", matched_person_id=999))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] == OUT_OF_RANGE_ID
    assert decision.detail["raw_matched_person_id"] == 999


def test_downgrade_merge_without_person_id() -> None:
    caller, _ = _claude_caller(_payload(decision="merge", matched_person_id=None))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] == MERGE_WITHOUT_PERSON_ID


def test_downgrade_identity_without_candidates() -> None:
    caller, _ = _claude_caller(
        _payload(decision="identity", matched_person_id=None, candidate_person_ids=())
    )

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.candidates == []
    assert decision.detail["forced_reason"] == IDENTITY_WITHOUT_CANDIDATES


def test_downgrade_identity_when_all_candidate_ids_are_hallucinated() -> None:
    caller, _ = _claude_caller(
        _payload(
            decision="identity", matched_person_id=None, candidate_person_ids=(777, 888)
        )
    )

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.detail["forced_reason"] == IDENTITY_WITHOUT_CANDIDATES
    assert decision.detail["dropped_ids"] == [777, 888]


def test_downgrade_on_llm_failure_is_identity_not_merge() -> None:
    """실패를 `merge` 로 흡수하면 오병합이 는다 -- 비대칭 금지
    (원칙1: 오병합이 미검출보다 훨씬 나쁘다)."""

    caller, _ = _claude_caller(anthropic.APITimeoutError(request=_anthropic_request()))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.score == 0.0
    assert decision.detail["forced_reason"] == "timeout"


def test_empty_mention_is_new_person_without_calling_llm() -> None:
    caller, client = _claude_caller(_payload())

    decision = resolve_from_state(PERSONS, "   ", "발화", caller=caller)

    assert decision.decision == "new_person"
    assert decision.detail["forced_reason"] == EMPTY_MENTION
    assert decision.detail["llm_calls"] == 0
    assert client.calls == []


def test_candidate_ids_missing_is_recorded_not_fatal() -> None:
    payload = _payload(decision="identity", matched_person_id=None)
    payload.pop("candidate_person_ids")
    caller, _ = _claude_caller(payload)

    decision = resolve_from_state(PERSONS, "민수", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["candidate_ids_missing"] is True
    assert decision.detail["forced_reason"] == IDENTITY_WITHOUT_CANDIDATES


def test_build_decision_is_pure_and_needs_no_client() -> None:
    """변환은 순수 함수다 -- DB·네트워크 없이 단독으로 검증할 수 있다."""
    parsed = validate_resolution(_payload(decision="merge", matched_person_id=3))

    decision = build_decision(parsed, PERSONS, mention="영희")

    assert decision.decision == "merge"
    assert decision.person_id == 3
    assert decision.detail["llm_calls"] == 1


# =========================================================================
# 3. 오류 층 -- P3-er `llm.error` 어휘 (결정 J)
# =========================================================================


@pytest.mark.parametrize(
    ("exc_factory", "expected"),
    [
        (lambda: anthropic.APITimeoutError(request=_anthropic_request()), "timeout"),
        (
            lambda: anthropic.RateLimitError(
                "rate limited",
                response=httpx2.Response(429, request=_anthropic_request(), json={}),
                body=None,
            ),
            "rate_limit",
        ),
        (
            lambda: anthropic.APIStatusError(
                "server error",
                response=httpx2.Response(500, request=_anthropic_request(), json={}),
                body=None,
            ),
            "api_error",
        ),
        (lambda: anthropic.APIConnectionError(request=_anthropic_request()), "connection"),
    ],
)
def test_claude_sdk_errors_map_to_llm_error_vocabulary(exc_factory, expected) -> None:
    caller, _ = _claude_caller(exc_factory())

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["llm_error"] == expected
    assert decision.detail["forced_reason"] == expected


@pytest.mark.parametrize(
    ("exc_factory", "expected"),
    [
        (lambda: openai.APITimeoutError(request=_openai_request()), "timeout"),
        (
            lambda: openai.RateLimitError(
                "rate limited",
                response=httpx.Response(429, request=_openai_request(), json={}),
                body=None,
            ),
            "rate_limit",
        ),
        (
            lambda: openai.APIStatusError(
                "server error",
                response=httpx.Response(500, request=_openai_request(), json={}),
                body=None,
            ),
            "api_error",
        ),
        (lambda: openai.APIConnectionError(request=_openai_request()), "connection"),
    ],
)
def test_openai_sdk_errors_map_to_llm_error_vocabulary(exc_factory, expected) -> None:
    caller, _ = _openai_caller(exc_factory())

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["llm_error"] == expected


def test_claude_response_without_tool_use_block_is_schema_error() -> None:
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="설명만 함")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        model="claude-sonnet-5",
    )
    caller = ClaudeSingleCaller(client=StubClaudeClient(response))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["llm_error"] == "schema"


def test_openai_response_without_tool_call_is_schema_error() -> None:
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=None))],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        model="gpt-4o-mini",
    )
    caller = OpenAISingleCaller(client=StubOpenAIClient(response))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["llm_error"] == "schema"


def test_openai_non_json_arguments_is_schema_error() -> None:
    function = SimpleNamespace(name=TOOL_NAME, arguments="{not json")
    message = SimpleNamespace(tool_calls=[SimpleNamespace(function=function)])
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        model="gpt-4o-mini",
    )
    caller = OpenAISingleCaller(client=StubOpenAIClient(response))

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.detail["llm_error"] == "schema"


@pytest.mark.parametrize(
    "payload",
    [
        {"decision": 3, "matched_person_id": 1, "s_llm": 0.9, "reason": "r"},
        {"decision": "merge", "matched_person_id": "1", "s_llm": 0.9, "reason": "r"},
        {"decision": "merge", "matched_person_id": True, "s_llm": 0.9, "reason": "r"},
        {"decision": "merge", "matched_person_id": 1, "s_llm": "0.9", "reason": "r"},
        {"decision": "merge", "matched_person_id": 1, "s_llm": True, "reason": "r"},
        {"decision": "merge", "matched_person_id": 1, "s_llm": 0.9, "reason": None},
        {
            "decision": "merge",
            "matched_person_id": 1,
            "s_llm": 0.9,
            "reason": "r",
            "candidate_person_ids": "1,2",
        },
    ],
)
def test_type_violations_are_schema_errors(payload) -> None:
    with pytest.raises(JudgeUnavailable) as excinfo:
        validate_resolution(payload)
    assert str(excinfo.value) == "schema"


def test_schema_error_becomes_identity_not_exception() -> None:
    """스키마 위반도 예외로 나가지 않는다 -- 한 방식만 죽으면 분모가
    달라져 비교가 깨진다(불변 규약 2, 원칙8)."""

    caller, _ = _claude_caller({"decision": "merge"})

    decision = resolve_from_state(PERSONS, "팀장", "발화", caller=caller)

    assert decision.decision == "identity"
    assert decision.detail["forced_reason"] == "schema"


# =========================================================================
# 4. 키 미노출 (security.md §1) -- 실 키를 쓰지 않는다
# =========================================================================


def test_env_secret_never_appears_in_request_body_detail_or_output(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", LEAK_CANARY)
    monkeypatch.setenv("OPENAI_API_KEY", LEAK_CANARY)
    caller, client = _claude_caller(_payload())

    decision = resolve_from_state(PERSONS, "김팀장", "발화", caller=caller)

    request_body = json.dumps(client.calls[0], ensure_ascii=False, default=str)
    output = json.dumps(decision.to_dict(), ensure_ascii=False)
    assert LEAK_CANARY not in request_body
    assert LEAK_CANARY not in output
    assert LEAK_CANARY not in json.dumps(decision.detail, ensure_ascii=False, default=str)


def test_env_secret_never_appears_in_error_paths(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", LEAK_CANARY)
    caller, _ = _claude_caller(anthropic.APIConnectionError(request=_anthropic_request()))

    decision = resolve_from_state(PERSONS, "김팀장", "발화", caller=caller)

    assert LEAK_CANARY not in json.dumps(decision.to_dict(), ensure_ascii=False)
    with pytest.raises(JudgeUnavailable) as excinfo:
        validate_resolution({"decision": None})
    assert LEAK_CANARY not in str(excinfo.value)


# =========================================================================
# 5. DB 층 (실 PostgreSQL · 롤백 픽스처)
# =========================================================================


def _make_person(
    db_session: Any,
    *,
    display_name: str,
    relation_tag: str = "직장",
    hierarchy: str = "동",
    user_id: str = USER_ID,
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


def _add_alias(db_session: Any, person: Person, alias: str) -> None:
    db_session.add(
        PersonAlias(person_id=person.id, alias=alias, source=ALIAS_SOURCES[0])
    )
    db_session.flush()


def _ctx(db_session: Any, *, session_id: str) -> ToolContext:
    """임베딩 공급자를 주지 않는다 -- 이 방식은 임베딩을 쓰지 않는다."""
    return ToolContext(session=db_session, session_id=session_id, user_id=USER_ID)


def _row_counts(db_session: Any) -> tuple[int, int, int, int]:
    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    questions = db_session.execute(
        select(func.count()).select_from(PendingQuestion)
    ).scalar_one()
    traces = db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()
    return persons, aliases, questions, traces


@pytest.mark.dbtest
def test_state_from_db_is_sent_to_the_prompt(db_session) -> None:
    """사전 상태 조회는 `load_known_persons` 재사용 -- 표시 이름·별칭에
    더해 관계 태그·위계가 프롬프트에 실린다."""

    lead = _make_person(db_session, display_name="김민수", hierarchy="상")
    _add_alias(db_session, lead, "팀장")
    friend = _make_person(db_session, display_name="박민수", relation_tag="친구")

    client = StubClaudeClient(_claude_response(_payload(matched_person_id=lead.id)))
    resolver = LLMSingleResolver(client=client, env={"LLM_PROVIDER": "anthropic"})

    decision = resolver.resolve_mention(
        _ctx(db_session, session_id="llm-single-db"), "팀장", "발화", config=CONFIG
    )

    body = client.calls[0]["messages"][0]["content"]
    assert f'"person_id": {lead.id}' in body
    assert f'"person_id": {friend.id}' in body
    assert "팀장" in body and "친구" in body and "상" in body
    assert decision.decision == "merge"
    assert decision.person_id == lead.id
    assert decision.detail["person_count"] == 2


@pytest.mark.dbtest
def test_other_users_persons_are_not_in_the_prompt(db_session) -> None:
    _make_person(db_session, display_name="남의사람", user_id="someone-else")
    client = StubClaudeClient(
        _claude_response(_payload(decision="new_person", matched_person_id=None))
    )
    resolver = LLMSingleResolver(client=client, env={"LLM_PROVIDER": "anthropic"})

    decision = resolver.resolve_mention(
        _ctx(db_session, session_id="llm-single-scope"), "팀장", "발화"
    )

    assert "남의사람" not in client.calls[0]["messages"][0]["content"]
    assert decision.detail["person_count"] == 0
    assert decision.decision == "new_person"


@pytest.mark.dbtest
@pytest.mark.parametrize(
    "decision_word", ["merge", "identity", "new_person"]
)
def test_no_side_effect_on_any_table(db_session, decision_word: str) -> None:
    """불변 규약 1 -- 이 방식은 `agent_traces` 조차 쓰지 않는다."""
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")
    payload = _payload(
        decision=decision_word,
        matched_person_id=lead.id if decision_word == "merge" else None,
        candidate_person_ids=(lead.id,) if decision_word == "identity" else (),
    )

    before = _row_counts(db_session)
    client = StubClaudeClient(_claude_response(payload))
    LLMSingleResolver(client=client, env={"LLM_PROVIDER": "anthropic"}).resolve_mention(
        _ctx(db_session, session_id="llm-single-side-effect"),
        "팀장",
        "발화",
        config=CONFIG,
    )

    assert _row_counts(db_session) == before


@pytest.mark.dbtest
def test_get_resolver_injects_stub_client(db_session, monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")
    client = StubClaudeClient(_claude_response(_payload(matched_person_id=lead.id)))

    resolver = get_resolver(METHOD_NAME, client=client)
    decision = resolver.resolve_mention(
        _ctx(db_session, session_id="llm-single-factory"), "팀장", "발화", config=CONFIG
    )

    assert isinstance(resolver, LLMSingleResolver)
    assert decision.decision == "merge"
    assert decision.person_id == lead.id
    assert len(client.calls) == 1


# =========================================================================
# 6. 방식 표 등록 경로
# =========================================================================


def test_resolver_is_registered_with_all_three_decisions() -> None:
    assert RESOLVERS[METHOD_NAME] is LLMSingleResolver
    assert LLMSingleResolver.supported_decisions == DECISIONS
    assert LLMSingleResolver.name == METHOD_NAME


def test_creating_the_resolver_does_not_require_a_client_or_key() -> None:
    """`for name in ALL_METHODS:` 로 전 방식을 만드는 계약 테스트(U7)가 키
    없이도 돌아야 한다 -- caller 는 **첫 호출 시점에** 만들어진다."""

    resolver = get_resolver(METHOD_NAME)

    assert resolver.caller is None


def test_all_methods_order_after_u5() -> None:
    """등록 순서 = `evaluation/resolvers/__init__.py` 의 import 순서.
    이름은 `metrics.json` 의 키다(P4 인계 4). 베이스라인 3종 + 제안 방식이
    모두 표에 있다는 것이 수용 기준의 절반이다."""

    assert resolver_registry.ALL_METHODS == (
        "proposed",
        "exact_raw",
        "exact_norm",
        "embedding_only",
        "llm_single",
    )
