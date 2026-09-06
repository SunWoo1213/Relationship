"""Refs: P3-er S3.3 D3 D4 D5 R4 결정3 결정3-c F-5a97ef -- U5 3단계(LLM 판정) 테스트.

네트워크 호출 없음(원칙8) -- `ClaudeJudge`/`OpenAIJudge` 는 스텁 클라이언트를
주입해 검증하고, 실 API 스모크는 `scripts/er_smoke.py`(U8)가 따로 한다.
"""

from __future__ import annotations

import json
import os
from types import SimpleNamespace

import httpx
import httpx2
import pytest

import anthropic
import openai

from app.er.judge import (
    JUDGEMENT_SCHEMA,
    ClaudeJudge,
    FakeJudge,
    OpenAIJudge,
    TOOL_NAME,
    build_prompt,
    judge_from_env,
    validate_judgement,
)
from app.er.types import JudgeUnavailable, ScoredCandidate

CANDIDATES = [
    ScoredCandidate(
        person_id=1,
        display_name="김민수",
        aliases=["팀장", "김팀장"],
        relation_tag="직장",
        hierarchy="동",
        s_emb=0.5,
        rule_flags={"exact_alias": True},
        rule_checked=2,
        rule_passed=2,
        s_rule=1.0,
        passed_rules=True,
    ),
    ScoredCandidate(
        person_id=2,
        display_name="이영희",
        aliases=["과장"],
        relation_tag="직장",
        hierarchy="동",
        s_emb=0.3,
        rule_flags={},
        rule_checked=2,
        rule_passed=1,
        s_rule=0.5,
        passed_rules=True,
    ),
]

ALLOWED_IDS = {1, 2}


# ---------------------------------------------------------------------------
# 스텁 클라이언트 (네트워크 없음)
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


def _claude_response(matched_person_id, s_llm, reason="확실", *, tokens=(12, 34), model="claude-sonnet-5"):
    return SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                name=TOOL_NAME,
                input={
                    "matched_person_id": matched_person_id,
                    "s_llm": s_llm,
                    "reason": reason,
                },
            )
        ],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model=model,
        stop_reason="tool_use",
    )


def _openai_response(matched_person_id, s_llm, reason="확실", *, tokens=(12, 34), model="gpt-4o-mini"):
    function = SimpleNamespace(
        name=TOOL_NAME,
        arguments=json.dumps(
            {"matched_person_id": matched_person_id, "s_llm": s_llm, "reason": reason}
        ),
    )
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=tokens[0], completion_tokens=tokens[1]),
        model=model,
    )


def _anthropic_request(url: str = "https://api.anthropic.com/v1/messages") -> httpx2.Request:
    return httpx2.Request("POST", url)


def _openai_request(url: str = "https://api.openai.com/v1/chat/completions") -> httpx.Request:
    return httpx.Request("POST", url)


# ---------------------------------------------------------------------------
# (a) ClaudeJudge 요청 본문
# ---------------------------------------------------------------------------


def test_claude_judge_request_body_forces_tool_choice_and_has_candidates(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = StubClaudeClient(_claude_response(1, 0.9))
    judge = ClaudeJudge(client=client)

    judge.judge("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "tool", "name": TOOL_NAME}
    assert kwargs["tools"] == [
        {
            "name": TOOL_NAME,
            "description": kwargs["tools"][0]["description"],
            "strict": True,
            "input_schema": JUDGEMENT_SCHEMA,
        }
    ]

    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "김민수" in body_str
    assert "부장님" in body_str
    assert "직장" in body_str
    assert "ANTHROPIC" not in body_str
    assert "os.environ" not in body_str
    assert "api_key" not in body_str.lower()


# ---------------------------------------------------------------------------
# (b) 정상 파싱
# ---------------------------------------------------------------------------


def test_claude_judge_parses_tool_use_into_judgement():
    client = StubClaudeClient(_claude_response(1, 0.9, reason="별칭군 일치"))
    judge = ClaudeJudge(client=client)

    result = judge.judge("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)

    assert result.matched_person_id == 1
    assert result.s_llm == 0.9
    assert result.reason == "별칭군 일치"
    assert result.tokens_in == 12
    assert result.tokens_out == 34
    assert result.model == "claude-sonnet-5"
    assert result.provider == "anthropic"


def test_openai_judge_parses_tool_call_into_judgement():
    client = StubOpenAIClient(_openai_response(2, 0.7, reason="과장 별칭"))
    judge = OpenAIJudge(client=client)

    result = judge.judge("과장님", "과장님이 오셨다", CANDIDATES)

    assert result.matched_person_id == 2
    assert result.s_llm == 0.7
    assert result.reason == "과장 별칭"
    assert result.tokens_in == 12
    assert result.tokens_out == 34
    assert result.model == "gpt-4o-mini"
    assert result.provider == "openai"


def test_openai_judge_request_body_forces_tool_choice_and_has_candidates():
    client = StubOpenAIClient(_openai_response(1, 0.9))
    judge = OpenAIJudge(client=client)

    judge.judge("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)

    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "function", "function": {"name": TOOL_NAME}}
    assert kwargs["tools"] == [
        {
            "type": "function",
            "function": {
                "name": TOOL_NAME,
                "description": kwargs["tools"][0]["function"]["description"],
                "parameters": JUDGEMENT_SCHEMA,
                "strict": True,
            },
        }
    ]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "김민수" in body_str
    assert "OPENAI_API_KEY" not in body_str
    assert "os.environ" not in body_str
    assert "api_key" not in body_str.lower()


# ---------------------------------------------------------------------------
# (c)(d)(e) 검증 실패 분기 -- 두 공급자가 같은 validate_judgement 를 공유
# ---------------------------------------------------------------------------


def test_claude_judge_s_llm_out_of_range_is_schema_error():
    client = StubClaudeClient(_claude_response(1, 1.5))
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_openai_judge_s_llm_out_of_range_is_schema_error():
    client = StubOpenAIClient(_openai_response(1, -0.1))
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_claude_judge_out_of_range_matched_id_is_out_of_range_id():
    client = StubClaudeClient(_claude_response(999, 0.9))
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "out_of_range_id"


def test_openai_judge_out_of_range_matched_id_is_out_of_range_id():
    client = StubOpenAIClient(_openai_response(999, 0.9))
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "out_of_range_id"


def test_claude_judge_excluded_candidate_id_is_out_of_range_id():
    # CANDIDATES 에 없는 배제된 후보 id(예: 3) -- 통과 후보 집합 밖.
    client = StubClaudeClient(_claude_response(3, 0.9))
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "out_of_range_id"


def test_claude_judge_no_tool_use_block_is_schema_error():
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="모르겠다")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        model="claude-sonnet-5",
        stop_reason="end_turn",
    )
    client = StubClaudeClient(response)
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_openai_judge_no_tool_call_is_schema_error():
    message = SimpleNamespace(tool_calls=None)
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        model="gpt-4o-mini",
    )
    client = StubOpenAIClient(response)
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


# ---------------------------------------------------------------------------
# (f) 예외 매핑
# ---------------------------------------------------------------------------


def test_claude_judge_maps_timeout_error():
    exc = anthropic.APITimeoutError(request=_anthropic_request())
    client = StubClaudeClient(exc)
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "timeout"


def test_claude_judge_maps_rate_limit_error():
    req = _anthropic_request()
    resp = httpx2.Response(429, request=req, json={"error": {"type": "rate_limit_error"}})
    exc = anthropic.RateLimitError("rate limited", response=resp, body=None)
    client = StubClaudeClient(exc)
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "rate_limit"


def test_claude_judge_maps_api_status_error():
    req = _anthropic_request()
    resp = httpx2.Response(500, request=req, json={"error": {"type": "api_error"}})
    exc = anthropic.APIStatusError("server error", response=resp, body=None)
    client = StubClaudeClient(exc)
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "api_error"


def test_claude_judge_maps_connection_error():
    exc = anthropic.APIConnectionError(request=_anthropic_request())
    client = StubClaudeClient(exc)
    judge = ClaudeJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "connection"


def test_openai_judge_maps_timeout_error():
    exc = openai.APITimeoutError(request=_openai_request())
    client = StubOpenAIClient(exc)
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "timeout"


def test_openai_judge_maps_rate_limit_error():
    req = _openai_request()
    resp = httpx.Response(429, request=req, json={"error": {"message": "rate limited"}})
    exc = openai.RateLimitError("rate limited", response=resp, body=None)
    client = StubOpenAIClient(exc)
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "rate_limit"


def test_openai_judge_maps_api_status_error():
    req = _openai_request()
    resp = httpx.Response(500, request=req, json={"error": {"message": "server error"}})
    exc = openai.APIStatusError("server error", response=resp, body=None)
    client = StubOpenAIClient(exc)
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "api_error"


def test_openai_judge_maps_connection_error():
    exc = openai.APIConnectionError(request=_openai_request())
    client = StubOpenAIClient(exc)
    judge = OpenAIJudge(client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "connection"


# ---------------------------------------------------------------------------
# (g) 기본 모델 -- env 를 따른다
# ---------------------------------------------------------------------------


def test_claude_judge_default_model_follows_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-custom-1")
    judge = ClaudeJudge(client=StubClaudeClient(_claude_response(1, 0.9)))
    assert judge.model == "claude-custom-1"


def test_claude_judge_default_model_is_claude_sonnet_5_without_env(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    judge = ClaudeJudge(client=StubClaudeClient(_claude_response(1, 0.9)))
    assert judge.model == "claude-sonnet-5"


def test_openai_judge_default_model_follows_env(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-custom-1")
    judge = OpenAIJudge(client=StubOpenAIClient(_openai_response(1, 0.9)))
    assert judge.model == "gpt-custom-1"


def test_openai_judge_default_model_is_gpt_4o_mini_without_env(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    judge = OpenAIJudge(client=StubOpenAIClient(_openai_response(1, 0.9)))
    assert judge.model == "gpt-4o-mini"


# ---------------------------------------------------------------------------
# (h) FakeJudge 결정성
# ---------------------------------------------------------------------------


def test_fake_judge_picks_highest_s_llm_among_passed():
    judge = FakeJudge(table={1: 0.4, 2: 0.9})
    result = judge.judge("부장님", "u", CANDIDATES)
    assert result.matched_person_id == 2
    assert result.s_llm == 0.9
    assert result.provider == "fake"


def test_fake_judge_pick_overrides_table_lookup():
    judge = FakeJudge(table={1: 0.4, 2: 0.9}, pick=1)
    result = judge.judge("부장님", "u", CANDIDATES)
    assert result.matched_person_id == 1
    assert result.s_llm == 0.4


def test_fake_judge_fail_raises_judge_unavailable():
    judge = FakeJudge(fail="timeout")
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "timeout"


def test_fake_judge_empty_table_returns_none_matched():
    judge = FakeJudge(table={})
    result = judge.judge("부장님", "u", CANDIDATES)
    assert result.matched_person_id is None
    assert result.s_llm == 0.0


def test_fake_judge_table_disjoint_from_passed_returns_none():
    judge = FakeJudge(table={99: 0.9})
    result = judge.judge("부장님", "u", CANDIDATES)
    assert result.matched_person_id is None
    assert result.s_llm == 0.0


def test_fake_judge_is_deterministic_across_calls():
    judge = FakeJudge(table={1: 0.4, 2: 0.9})
    first = judge.judge("부장님", "u", CANDIDATES)
    second = judge.judge("부장님", "u", CANDIDATES)
    assert first.matched_person_id == second.matched_person_id
    assert first.s_llm == second.s_llm


# ---------------------------------------------------------------------------
# (i) judge_from_env 팩토리
# ---------------------------------------------------------------------------


def test_judge_from_env_defaults_to_anthropic(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    judge = judge_from_env(env={})
    assert isinstance(judge, ClaudeJudge)


def test_judge_from_env_openai(monkeypatch):
    # OpenAI() 클라이언트는 생성 시점에 키 존재를 확인한다(Anthropic() 과
    # 달리) -- 실제로 호출하지 않으므로 더미 값으로 생성만 확인한다.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    judge = judge_from_env(env={"LLM_PROVIDER": "openai"})
    assert isinstance(judge, OpenAIJudge)


def test_judge_from_env_gemini_is_reserved_not_implemented():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        judge_from_env(env={"LLM_PROVIDER": "gemini"})


def test_judge_from_env_unknown_provider_rejected():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        judge_from_env(env={"LLM_PROVIDER": "not-a-provider"})


def test_judge_from_env_uses_os_environ_when_env_omitted(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    judge = judge_from_env()
    assert isinstance(judge, OpenAIJudge)


# ---------------------------------------------------------------------------
# 공유 검증 함수 -- 두 공급자가 같은 validate_judgement 를 쓴다
# ---------------------------------------------------------------------------


def test_both_providers_call_shared_validate_judgement(monkeypatch):
    calls: list[tuple] = []
    original = validate_judgement

    def _spy(raw, allowed_ids):
        calls.append((raw, allowed_ids))
        return original(raw, allowed_ids)

    monkeypatch.setattr("app.er.judge.validate_judgement", _spy)

    ClaudeJudge(client=StubClaudeClient(_claude_response(1, 0.9))).judge(
        "부장님", "u", CANDIDATES
    )
    OpenAIJudge(client=StubOpenAIClient(_openai_response(1, 0.9))).judge(
        "부장님", "u", CANDIDATES
    )

    assert len(calls) == 2
    assert calls[0][1] == ALLOWED_IDS
    assert calls[1][1] == ALLOWED_IDS


# ---------------------------------------------------------------------------
# build_prompt -- 키·환경변수·전체 대화 이력 금지
# ---------------------------------------------------------------------------


def test_build_prompt_has_no_secrets_or_env_names():
    system, user_text = build_prompt("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)
    combined = system + user_text
    assert "ANTHROPIC" not in combined
    assert "OPENAI" not in combined
    assert "os.environ" not in combined
    assert "김민수" in combined
    assert "부장님" in combined
