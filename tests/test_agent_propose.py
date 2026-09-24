"""Refs: P5-loop D11 S3.4 원칙1 원칙7 원칙9 -- U2 인식 단계(`app/agent/propose.py`)
테스트.

네트워크 호출 없음(원칙8, 판정 표 2행) -- `ClaudeProposer`/`OpenAIProposer`/
`GeminiProposer` 는 `tests/test_er_judge.py` 와 같은 스텁 클라이언트 패턴을
쓰고, `FakeProposer` 로 게이트·루프 테스트(U3~U5)가 실 LLM 없이 돈다. DB 를
쓰지 않는다(propose.py 는 `ctx`/세션을 받지 않는다).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import httpx
import httpx2
import pytest

import anthropic
import openai

from app.agent.propose import (
    PROPOSAL_ARG_SCHEMA,
    PROPOSAL_SCHEMA,
    PROPOSAL_TOOL_NAME,
    PROPOSERS,
    TOOL_NAMES,
    ClaudeProposer,
    FakeProposer,
    GeminiProposer,
    OpenAIProposer,
    build_propose_prompt,
    proposer_from_env,
    validate_proposal,
)
from app.agent.types import Proposal, ToolCallProposal
from app.db.models import EVENT_TYPES, HIERARCHIES, RELATION_TAGS
from app.er.types import JudgeUnavailable

#: P3-er F-46f1eb 규약과 같은 마커 -- 실제 키 형식이 아닌 표식(secret-guard
#: 오탐 방지, `tests/test_er_judge.py` 와 동일).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

NOW = datetime(2026, 9, 24, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# PROPOSAL_SCHEMA 구조 -- CLAUDE.md 고정 집합과의 정합
# ---------------------------------------------------------------------------


def test_proposal_schema_name_enum_matches_tool_names():
    names = PROPOSAL_SCHEMA["properties"]["tool_calls"]["items"]["properties"]["name"]
    assert names["enum"] == list(TOOL_NAMES)


def test_proposal_schema_type_enum_matches_event_types():
    assert PROPOSAL_ARG_SCHEMA["properties"]["type"]["enum"] == list(EVENT_TYPES)


def test_proposal_schema_relation_tag_enum_matches_relation_tags():
    assert PROPOSAL_ARG_SCHEMA["properties"]["relation_tag"]["enum"] == list(RELATION_TAGS)


def test_proposal_schema_hierarchy_enum_matches_hierarchies():
    assert PROPOSAL_ARG_SCHEMA["properties"]["hierarchy"]["enum"] == list(HIERARCHIES)


def test_proposal_schema_top_level_requires_tool_calls_only():
    assert PROPOSAL_SCHEMA["required"] == ["tool_calls"]
    assert PROPOSAL_SCHEMA["additionalProperties"] is False


def test_proposal_schema_does_not_declare_person_id_property():
    # person_id 는 게이트가 별도로 금지하는 자리다(게이트 ④) -- 스키마
    # 수준에서도 그 이름을 후보 필드로 얹지 않는다(프롬프트 의존이 아니라
    # 형태로도 person 만 쓰게 유도한다, 강제는 여전히 게이트).
    assert "person_id" not in PROPOSAL_ARG_SCHEMA["properties"]


# ---------------------------------------------------------------------------
# build_propose_prompt -- 키·환경변수·전체 대화 이력 금지, R-22 리터럴 안전
# ---------------------------------------------------------------------------


def test_build_propose_prompt_has_utterance_now_and_tool_names():
    system, user_text = build_propose_prompt("어제 민수랑 저녁 먹었어", NOW)
    combined = system + user_text
    assert "어제 민수랑 저녁 먹었어" in combined
    assert NOW.isoformat() in combined
    for name in TOOL_NAMES:
        assert name in combined


def test_build_propose_prompt_marks_not_callable_tools():
    system, _ = build_propose_prompt("u", NOW)
    assert "search_person" in system
    assert "ask_user" in system
    assert "get_briefing" in system
    assert "제안" in system  # "절대 제안하지 마라" 안내문


def test_build_propose_prompt_excludes_injected_args_from_tool_lines():
    _, user_text = build_propose_prompt("u", NOW)
    # add_event 설명 줄에 raw_utterance 가 나타나지 않는다(루프가 주입).
    lines = [line for line in user_text.splitlines() if line.startswith("- add_event:")]
    assert len(lines) == 1
    assert "raw_utterance" not in lines[0]
    assert "person(언급 문자열)" in lines[0]


def test_build_propose_prompt_has_no_secrets_or_env_names():
    system, user_text = build_propose_prompt("어제 민수랑 저녁 먹었어", NOW)
    combined = system + user_text
    assert "ANTHROPIC" not in combined
    assert "OPENAI" not in combined
    assert "GEMINI" not in combined
    assert "os.environ" not in combined
    assert "api_key" not in combined.lower()


def test_build_propose_prompt_no_literal_parenthesis_call_forms_in_source():
    # R-22 오탐 방지 자체 확인 -- 소스가 아니라 "생성된 프롬프트 문자열"에도
    # `create_person(...)`/`update_person(...)` 리터럴 호출 표기가 없다
    # (프롬프트는 "이름: 인자" 한 줄 표기이지 "이름(인자)" 괄호 표기가 아니다).
    _, user_text = build_propose_prompt("u", NOW)
    assert "create_person(" not in user_text
    assert "update_person(" not in user_text


# ---------------------------------------------------------------------------
# validate_proposal -- 스키마 강제(형식만) + 시각 변환
# ---------------------------------------------------------------------------


def test_validate_proposal_builds_proposal_from_well_formed_raw():
    raw = {
        "tool_calls": [
            {"name": "add_event", "args": {"person": "민수", "type": "meal", "content": "저녁", "occurred_at": "2026-09-23T19:00:00+09:00"}}
        ]
    }
    proposal = validate_proposal(raw)
    assert isinstance(proposal, Proposal)
    assert len(proposal.tool_calls) == 1
    call = proposal.tool_calls[0]
    assert isinstance(call, ToolCallProposal)
    assert call.name == "add_event"
    assert isinstance(call.args["occurred_at"], datetime)
    assert proposal.raw is raw


def test_validate_proposal_converts_schedule_datetime_arg():
    raw = {
        "tool_calls": [
            {"name": "add_schedule", "args": {"person": "민수", "title": "저녁", "scheduled_at": "2026-10-02T19:00:00+09:00"}}
        ]
    }
    call = validate_proposal(raw).tool_calls[0]
    assert isinstance(call.args["scheduled_at"], datetime)


def test_validate_proposal_leaves_unparsable_datetime_string_untouched():
    raw = {"tool_calls": [{"name": "add_event", "args": {"occurred_at": "다음주 언젠가"}}]}
    call = validate_proposal(raw).tool_calls[0]
    assert call.args["occurred_at"] == "다음주 언젠가"


def test_validate_proposal_leaves_none_datetime_untouched():
    raw = {"tool_calls": [{"name": "add_schedule", "args": {"scheduled_at": None}}]}
    call = validate_proposal(raw).tool_calls[0]
    assert call.args["scheduled_at"] is None


def test_validate_proposal_does_not_touch_datetime_keys_for_other_tools():
    # update_person 에는 occurred_at/scheduled_at 이 없다 -- 변환 대상이
    # 아니므로 값이 그대로 남는다(형식 변환은 툴별 화이트리스트만).
    raw = {"tool_calls": [{"name": "update_person", "args": {"occurred_at": "2026-01-01T00:00:00"}}]}
    call = validate_proposal(raw).tool_calls[0]
    assert call.args["occurred_at"] == "2026-01-01T00:00:00"


def test_validate_proposal_empty_tool_calls_is_valid():
    proposal = validate_proposal({"tool_calls": []})
    assert proposal.tool_calls == []


@pytest.mark.parametrize(
    "raw",
    [
        "not a dict",
        {},
        {"tool_calls": "not a list"},
        {"tool_calls": ["not a dict"]},
        {"tool_calls": [{"args": {}}]},  # name 없음
        {"tool_calls": [{"name": "", "args": {}}]},  # name 빈 문자열
        {"tool_calls": [{"name": "add_event"}]},  # args 없음
        {"tool_calls": [{"name": "add_event", "args": "not a dict"}]},
        {"tool_calls": [{"name": 3, "args": {}}]},  # name 이 문자열 아님
    ],
)
def test_validate_proposal_malformed_raw_is_schema_error(raw):
    with pytest.raises(JudgeUnavailable) as excinfo:
        validate_proposal(raw)
    assert str(excinfo.value) == "schema"


# ---------------------------------------------------------------------------
# FakeProposer -- 결정적, 네트워크 0(원칙8)
# ---------------------------------------------------------------------------


def test_fake_proposer_returns_table_entry():
    proposer = FakeProposer(
        table={"어제 민수랑 저녁 먹었어": [{"name": "add_event", "args": {"person": "민수", "type": "meal", "content": "저녁", "occurred_at": "2026-09-23T19:00:00+09:00"}}]}
    )
    proposal = proposer.propose("어제 민수랑 저녁 먹었어", NOW)
    assert len(proposal.tool_calls) == 1
    assert proposal.tool_calls[0].name == "add_event"
    assert isinstance(proposal.tool_calls[0].args["occurred_at"], datetime)


def test_fake_proposer_missing_utterance_returns_empty_tool_calls():
    proposer = FakeProposer(table={})
    proposal = proposer.propose("아무 말", NOW)
    assert proposal.tool_calls == []


def test_fake_proposer_is_deterministic_across_calls():
    proposer = FakeProposer(table={"u": [{"name": "add_event", "args": {"type": "meal"}}]})
    first = proposer.propose("u", NOW)
    second = proposer.propose("u", NOW)
    assert first.to_dict() == second.to_dict()


def test_fake_proposer_ignores_now_argument():
    proposer = FakeProposer(table={"u": [{"name": "add_event", "args": {"type": "meal"}}]})
    a = proposer.propose("u", NOW)
    b = proposer.propose("u", datetime(2099, 1, 1, tzinfo=timezone.utc))
    assert a.to_dict() == b.to_dict()


# ---------------------------------------------------------------------------
# 스텁 클라이언트 (네트워크 없음, tests/test_er_judge.py 와 같은 패턴)
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
    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.chat = _StubChat(self)


class _StubGeminiModels:
    def __init__(self, outer: "StubGeminiClient") -> None:
        self._outer = outer

    def generate_content(self, **kwargs):
        self._outer.calls.append(kwargs)
        item = self._outer.queue.pop(0) if self._outer.queue else self._outer.response
        if isinstance(item, BaseException):
            raise item
        return item


class StubGeminiClient:
    def __init__(self, response=None, queue=None) -> None:
        self.response = response
        self.queue: list = list(queue) if queue else []
        self.calls: list[dict] = []
        self.models = _StubGeminiModels(self)


def _claude_tool_calls_response(tool_calls, *, tokens=(12, 34), model="claude-sonnet-5"):
    return SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                name=PROPOSAL_TOOL_NAME,
                input={"tool_calls": tool_calls},
            )
        ],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model=model,
        stop_reason="tool_use",
    )


def _openai_tool_calls_response(tool_calls, *, model="gpt-4o-mini"):
    function = SimpleNamespace(
        name=PROPOSAL_TOOL_NAME, arguments=json.dumps({"tool_calls": tool_calls})
    )
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice], usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model=model)


def _gemini_tool_calls_response(tool_calls, *, model="gemini-test-model"):
    return SimpleNamespace(
        text=json.dumps({"tool_calls": tool_calls}),
        usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=1),
        model_version=model,
    )


def _anthropic_request(url: str = "https://api.anthropic.com/v1/messages") -> httpx2.Request:
    return httpx2.Request("POST", url)


def _openai_request(url: str = "https://api.openai.com/v1/chat/completions") -> httpx.Request:
    return httpx.Request("POST", url)


_SAMPLE_CALL = {"name": "add_event", "args": {"person": "민수", "type": "meal", "content": "저녁"}}


# ---------------------------------------------------------------------------
# ClaudeProposer
# ---------------------------------------------------------------------------


def test_claude_proposer_request_body_forces_tool_choice_and_schema(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = StubClaudeClient(_claude_tool_calls_response([_SAMPLE_CALL]))
    proposer = ClaudeProposer(client=client)

    proposer.propose("민수랑 저녁 먹었어", NOW)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "tool", "name": PROPOSAL_TOOL_NAME}
    assert kwargs["tools"] == [
        {
            "name": PROPOSAL_TOOL_NAME,
            "description": kwargs["tools"][0]["description"],
            "input_schema": PROPOSAL_SCHEMA,
        }
    ]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "민수" in body_str
    assert "ANTHROPIC" not in body_str
    assert "api_key" not in body_str.lower()


def test_claude_proposer_parses_tool_use_into_proposal():
    client = StubClaudeClient(_claude_tool_calls_response([_SAMPLE_CALL]))
    proposer = ClaudeProposer(client=client)

    result = proposer.propose("민수랑 저녁 먹었어", NOW)

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "add_event"
    assert result.tool_calls[0].args["person"] == "민수"


def test_claude_proposer_no_tool_use_block_is_schema_error():
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="모르겠다")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        model="claude-sonnet-5",
        stop_reason="end_turn",
    )
    proposer = ClaudeProposer(client=StubClaudeClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "schema"


def test_claude_proposer_maps_timeout_error():
    exc = anthropic.APITimeoutError(request=_anthropic_request())
    proposer = ClaudeProposer(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "timeout"


def test_claude_proposer_maps_rate_limit_error():
    req = _anthropic_request()
    resp = httpx2.Response(429, request=req, json={"error": {"type": "rate_limit_error"}})
    exc = anthropic.RateLimitError("rate limited", response=resp, body=None)
    proposer = ClaudeProposer(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "rate_limit"


def test_claude_proposer_maps_api_status_error():
    req = _anthropic_request()
    resp = httpx2.Response(500, request=req, json={"error": {"type": "api_error"}})
    exc = anthropic.APIStatusError("server error", response=resp, body=None)
    proposer = ClaudeProposer(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "api_error"


def test_claude_proposer_maps_connection_error():
    exc = anthropic.APIConnectionError(request=_anthropic_request())
    proposer = ClaudeProposer(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "connection"


def test_claude_proposer_default_model_follows_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-custom-1")
    proposer = ClaudeProposer(client=StubClaudeClient(_claude_tool_calls_response([])))
    assert proposer.model == "claude-custom-1"


# ---------------------------------------------------------------------------
# OpenAIProposer
# ---------------------------------------------------------------------------


def test_openai_proposer_request_body_forces_tool_choice_and_schema():
    client = StubOpenAIClient(_openai_tool_calls_response([_SAMPLE_CALL]))
    proposer = OpenAIProposer(client=client)

    proposer.propose("민수랑 저녁 먹었어", NOW)

    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "function", "function": {"name": PROPOSAL_TOOL_NAME}}
    assert kwargs["tools"] == [
        {
            "type": "function",
            "function": {
                "name": PROPOSAL_TOOL_NAME,
                "description": kwargs["tools"][0]["function"]["description"],
                "parameters": PROPOSAL_SCHEMA,
            },
        }
    ]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "민수" in body_str
    assert "OPENAI_API_KEY" not in body_str
    assert "api_key" not in body_str.lower()


def test_openai_proposer_parses_tool_call_into_proposal():
    client = StubOpenAIClient(_openai_tool_calls_response([_SAMPLE_CALL]))
    proposer = OpenAIProposer(client=client)

    result = proposer.propose("민수랑 저녁 먹었어", NOW)

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "add_event"


def test_openai_proposer_no_tool_call_is_schema_error():
    message = SimpleNamespace(tool_calls=None)
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice], usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model="gpt-4o-mini")
    proposer = OpenAIProposer(client=StubOpenAIClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "schema"


def test_openai_proposer_invalid_json_arguments_is_schema_error():
    function = SimpleNamespace(name=PROPOSAL_TOOL_NAME, arguments="{not valid json")
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice], usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model="gpt-4o-mini")
    proposer = OpenAIProposer(client=StubOpenAIClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "schema"


def test_openai_proposer_maps_timeout_error():
    exc = openai.APITimeoutError(request=_openai_request())
    proposer = OpenAIProposer(client=StubOpenAIClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "timeout"


def test_openai_proposer_maps_rate_limit_error():
    req = _openai_request()
    resp = httpx.Response(429, request=req, json={"error": {"message": "rate limited"}})
    exc = openai.RateLimitError("rate limited", response=resp, body=None)
    proposer = OpenAIProposer(client=StubOpenAIClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "rate_limit"


def test_openai_proposer_maps_connection_error():
    exc = openai.APIConnectionError(request=_openai_request())
    proposer = OpenAIProposer(client=StubOpenAIClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "connection"


# ---------------------------------------------------------------------------
# GeminiProposer (네트워크 0, judge.py 의 오류 매핑·스키마 변환 재사용)
# ---------------------------------------------------------------------------


def test_gemini_proposer_missing_model_env_raises_invalid_value(monkeypatch):
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    with pytest.raises(InvalidValue):
        GeminiProposer(client=StubGeminiClient(response=_gemini_tool_calls_response([])))


def test_gemini_proposer_parses_text_into_proposal():
    client = StubGeminiClient(response=_gemini_tool_calls_response([_SAMPLE_CALL]))
    proposer = GeminiProposer(model="gemini-test-model", client=client)

    result = proposer.propose("민수랑 저녁 먹었어", NOW)

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "add_event"
    assert client.calls[0]["model"] == "gemini-test-model"
    assert "민수" in client.calls[0]["contents"]


def test_gemini_proposer_config_uses_proposal_schema():
    from app.er.judge import _to_gemini_schema

    client = StubGeminiClient(response=_gemini_tool_calls_response([]))
    proposer = GeminiProposer(model="gemini-test-model", client=client)
    proposer.propose("u", NOW)

    config = client.calls[0]["config"]
    assert config.response_schema == _to_gemini_schema(PROPOSAL_SCHEMA)
    assert config.temperature == 0
    assert config.response_mime_type == "application/json"


def test_gemini_proposer_text_not_json_is_schema_error():
    response = SimpleNamespace(text="모르겠다", usage_metadata=None, model_version="gemini-test-model")
    proposer = GeminiProposer(model="gemini-test-model", client=StubGeminiClient(response=response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "schema"


def test_gemini_proposer_no_text_is_schema_error():
    response = SimpleNamespace(text=None, usage_metadata=None, model_version="gemini-test-model")
    proposer = GeminiProposer(model="gemini-test-model", client=StubGeminiClient(response=response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        proposer.propose("u", NOW)
    assert str(excinfo.value) == "schema"


# ---------------------------------------------------------------------------
# PROPOSERS 등록표 · proposer_from_env
# ---------------------------------------------------------------------------


def test_proposers_table_has_exactly_three_keys_no_fake():
    assert sorted(PROPOSERS) == ["anthropic", "gemini", "openai"]
    assert "fake" not in PROPOSERS


@pytest.mark.parametrize(
    "provider, key_name, proposer_cls, extra_env",
    [
        ("anthropic", "ANTHROPIC_API_KEY", ClaudeProposer, {}),
        ("openai", "OPENAI_API_KEY", OpenAIProposer, {}),
        ("gemini", "GEMINI_API_KEY", GeminiProposer, {"GEMINI_MODEL": "gemini-test-model"}),
    ],
)
def test_proposer_from_env_builds_each_active_provider(monkeypatch, provider, key_name, proposer_cls, extra_env):
    monkeypatch.setenv(key_name, _FAKE_KEY_MARKER)
    for env_name, env_value in extra_env.items():
        monkeypatch.setenv(env_name, env_value)
    proposer = proposer_from_env(env={"LLM_PROVIDER": provider})
    assert isinstance(proposer, proposer_cls)


def test_proposer_from_env_defaults_to_openai(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    proposer = proposer_from_env(env={})
    assert isinstance(proposer, OpenAIProposer)


def test_proposer_from_env_unknown_provider_rejected():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        proposer_from_env(env={"LLM_PROVIDER": "llama"})


def test_proposer_from_env_rejects_disabled_provider():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue) as excinfo:
        proposer_from_env(env={"LLM_PROVIDER": "gemini", "LLM_PROVIDERS_ENABLED": "anthropic"})
    assert "anthropic" in str(excinfo.value)


def test_proposer_from_env_uses_os_environ_when_env_omitted(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    proposer = proposer_from_env()
    assert isinstance(proposer, OpenAIProposer)


def test_dummy_key_marker_does_not_leak_into_exceptions_or_output(monkeypatch, capsys):
    from app.tools.types import InvalidValue

    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    proposer = proposer_from_env(env={"LLM_PROVIDER": "openai"})
    assert isinstance(proposer, OpenAIProposer)

    with pytest.raises(InvalidValue) as excinfo:
        proposer_from_env(env={"LLM_PROVIDER": "llama"})
    assert _FAKE_KEY_MARKER not in str(excinfo.value)

    captured = capsys.readouterr()
    assert _FAKE_KEY_MARKER not in captured.out
    assert _FAKE_KEY_MARKER not in captured.err
