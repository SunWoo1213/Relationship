"""Refs: P3-er P3-llm-providers S3.3 D3 D4 D5 D11 R4 R-6 결정3 결정3-c
F-5a97ef -- U5 3단계(LLM 판정) 테스트 + U1 등록표·활성 스위치 테스트 + U2
`GeminiJudge` 테스트.

네트워크 호출 없음(원칙8) -- `ClaudeJudge`/`OpenAIJudge`/`GeminiJudge` 는
스텁 클라이언트를 주입해 검증하고, 실 API 스모크는 `scripts/er_smoke.py`
(U8)가 따로 한다.
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
from google.genai import errors as genai_errors

from app.er.judge import (
    JUDGEMENT_SCHEMA,
    JUDGES,
    ClaudeJudge,
    FakeJudge,
    GeminiJudge,
    OpenAIJudge,
    TOOL_NAME,
    _to_gemini_schema,
    build_prompt,
    enabled_providers,
    judge_from_env,
    select_provider,
    validate_judgement,
)
from app.er.types import JudgeUnavailable, ScoredCandidate

#: P3-er F-46f1eb 규약 -- 더미 키는 실제 키 형식(`sk-…`/`AKIA…`)이 아닌
#: 이 마커를 쓴다(secret-guard 오탐 방지, `tests/test_er_smoke.py` 와 동일).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

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


class _StubGeminiModels:
    """`genai.Client().models` 를 흉내 내는 스텁 -- `generate_content()` 만.
    `queue` 가 주어지면 호출마다 하나씩 소비한다(재시도 횟수 확인용,
    비면 `response` 를 계속 돌려준다)."""

    def __init__(self, outer: "StubGeminiClient") -> None:
        self._outer = outer

    def generate_content(self, **kwargs):
        self._outer.calls.append(kwargs)
        item = self._outer.queue.pop(0) if self._outer.queue else self._outer.response
        if isinstance(item, BaseException):
            raise item
        return item


class StubGeminiClient:
    """`genai.Client` 를 흉내 내는 스텁 -- `models.generate_content()` 만."""

    def __init__(self, response=None, queue=None) -> None:
        self.response = response
        self.queue: list = list(queue) if queue else []
        self.calls: list[dict] = []
        self.models = _StubGeminiModels(self)


def _gemini_response(matched_person_id, s_llm, reason="확실", *, tokens=(12, 34), model="gemini-test-model"):
    return SimpleNamespace(
        text=json.dumps(
            {"matched_person_id": matched_person_id, "s_llm": s_llm, "reason": reason}
        ),
        usage_metadata=SimpleNamespace(
            prompt_token_count=tokens[0], candidates_token_count=tokens[1]
        ),
        model_version=model,
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
# (f-2) GeminiJudge (P3-llm-providers U2, D11, R-6) -- 네트워크 0, 스텁만
# ---------------------------------------------------------------------------


def test_gemini_judge_request_body_has_schema_temperature_zero_and_mime(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = StubGeminiClient(response=_gemini_response(1, 0.9))
    judge = GeminiJudge(model="gemini-test-model", client=client)

    judge.judge("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["model"] == "gemini-test-model"
    assert "김민수" in kwargs["contents"]
    assert "부장님" in kwargs["contents"]

    config = kwargs["config"]
    assert config.temperature == 0
    assert config.response_mime_type == "application/json"
    assert config.response_schema == _to_gemini_schema(JUDGEMENT_SCHEMA)
    assert "직장" in config.system_instruction or "직장" in kwargs["contents"]

    body_str = json.dumps(
        {"contents": kwargs["contents"], "system_instruction": config.system_instruction},
        default=str,
        ensure_ascii=False,
    )
    assert "GEMINI_API_KEY" not in body_str
    assert "os.environ" not in body_str
    assert "api_key" not in body_str.lower()


def test_gemini_judge_parses_text_into_judgement():
    client = StubGeminiClient(response=_gemini_response(2, 0.7, reason="과장 별칭"))
    judge = GeminiJudge(model="gemini-test-model", client=client)

    result = judge.judge("과장님", "과장님이 오셨다", CANDIDATES)

    assert result.matched_person_id == 2
    assert result.s_llm == 0.7
    assert result.reason == "과장 별칭"
    assert result.tokens_in == 12
    assert result.tokens_out == 34
    assert result.model == "gemini-test-model"
    assert result.provider == "gemini"


def test_gemini_judge_s_llm_out_of_range_is_schema_error():
    client = StubGeminiClient(response=_gemini_response(1, 1.5))
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_gemini_judge_out_of_range_matched_id_is_out_of_range_id():
    client = StubGeminiClient(response=_gemini_response(999, 0.9))
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "out_of_range_id"


def test_gemini_judge_excluded_candidate_id_is_out_of_range_id():
    client = StubGeminiClient(response=_gemini_response(3, 0.9))
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "out_of_range_id"


def test_gemini_judge_text_not_json_is_schema_error():
    response = SimpleNamespace(text="모르겠다", usage_metadata=None, model_version="gemini-test-model")
    client = StubGeminiClient(response=response)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_gemini_judge_no_text_is_schema_error():
    # 후보 블록 없음 · 안전 필터로 본문 없음 -- 둘 다 response.text 가 None.
    response = SimpleNamespace(text=None, usage_metadata=None, model_version="gemini-test-model")
    client = StubGeminiClient(response=response)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_gemini_judge_empty_text_is_schema_error():
    response = SimpleNamespace(text="", usage_metadata=None, model_version="gemini-test-model")
    client = StubGeminiClient(response=response)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "schema"


def test_gemini_judge_maps_rate_limit_error_no_retry():
    exc = genai_errors.ClientError(429, {"error": {"message": "rate limited"}}, None)
    client = StubGeminiClient(response=exc)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "rate_limit"
    assert len(client.calls) == 1


def test_gemini_judge_maps_client_4xx_to_api_error_no_retry():
    exc = genai_errors.ClientError(400, {"error": {"message": "bad request"}}, None)
    client = StubGeminiClient(response=exc)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "api_error"
    assert len(client.calls) == 1


def test_gemini_judge_maps_server_5xx_to_api_error_no_retry():
    exc = genai_errors.ServerError(500, {"error": {"message": "server error"}}, None)
    client = StubGeminiClient(response=exc)
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "api_error"
    assert len(client.calls) == 1


def test_gemini_judge_maps_timeout_retries_once_then_raises():
    client = StubGeminiClient(queue=[httpx.TimeoutException("t1"), httpx.TimeoutException("t2")])
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "timeout"
    assert len(client.calls) == 2


def test_gemini_judge_maps_connection_retries_once_then_raises():
    client = StubGeminiClient(queue=[httpx.ConnectError("c1"), httpx.ConnectError("c2")])
    judge = GeminiJudge(model="gemini-test-model", client=client)
    with pytest.raises(JudgeUnavailable) as excinfo:
        judge.judge("부장님", "u", CANDIDATES)
    assert str(excinfo.value) == "connection"
    assert len(client.calls) == 2


def test_gemini_judge_timeout_succeeds_on_retry():
    client = StubGeminiClient(queue=[httpx.TimeoutException("t1"), _gemini_response(1, 0.9)])
    judge = GeminiJudge(model="gemini-test-model", client=client)
    result = judge.judge("부장님", "u", CANDIDATES)
    assert result.matched_person_id == 1
    assert len(client.calls) == 2


def test_gemini_judge_default_model_follows_env(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom-1")
    judge = GeminiJudge(client=StubGeminiClient(response=_gemini_response(1, 0.9)))
    assert judge.model == "gemini-custom-1"


def test_gemini_judge_missing_model_env_raises_invalid_value(monkeypatch):
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    with pytest.raises(InvalidValue):
        GeminiJudge(client=StubGeminiClient(response=_gemini_response(1, 0.9)))


def test_gemini_judge_key_marker_not_in_request_or_output(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", _FAKE_KEY_MARKER)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")

    client = StubGeminiClient(response=_gemini_response(1, 0.9))
    # client 를 주입하므로 GEMINI_API_KEY 를 실제로 읽지는 않지만(SDK 가
    # 감춘 값), 이 테스트는 요청 본문·출력에 마커가 어디에도 없음을
    # 단언한다(SDK 로 흘러들어가는 경로가 생겨도 잡힌다).
    judge = GeminiJudge(client=client)
    judge.judge("부장님", "부장님이 회의를 잡으셨다", CANDIDATES)

    body_str = json.dumps(
        {"contents": client.calls[0]["contents"]}, default=str, ensure_ascii=False
    )
    assert _FAKE_KEY_MARKER not in body_str

    captured = capsys.readouterr()
    assert _FAKE_KEY_MARKER not in captured.out
    assert _FAKE_KEY_MARKER not in captured.err


def test_module_importable_without_google_genai_installed():
    # SDK 없이도 `app.er.judge` 임포트 자체는 깨지지 않는다(지연 import
    # 유지, 판정 표 72행). `sys.modules["google"] = None` 은 import 기계가
    # 즉시 ImportError 를 내게 만드는 표준 기법이다.
    #
    # `importlib.reload()` 는 이 파일이 수집 시점에 `from app.er.judge
    # import ...` 로 미리 들고 있는 클래스 객체(`OpenAIJudge` 등)를 새
    # 객체로 바꿔치기해 다른 테스트의 `isinstance` 단언을 깨뜨린다 --
    # 그래서 원본 모듈 `__dict__` 를 통째로 스냅샷했다가 그대로 복원해,
    # 이 테스트가 끝나면 다른 테스트가 보는 객체 정체성이 그대로다.
    import sys
    import importlib

    import app.er.judge as judge_module

    original_dict = dict(judge_module.__dict__)
    saved: dict[str, object] = {}
    for name in list(sys.modules):
        if name == "google" or name.startswith("google."):
            saved[name] = sys.modules.pop(name)
    sys.modules["google"] = None  # type: ignore[assignment]

    try:
        reloaded = importlib.reload(judge_module)
        assert "gemini" in reloaded.JUDGES
        assert reloaded.JUDGES["gemini"] is reloaded.GeminiJudge
    finally:
        del sys.modules["google"]
        sys.modules.update(saved)
        judge_module.__dict__.clear()
        judge_module.__dict__.update(original_dict)


# ---------------------------------------------------------------------------
# (f-3) `_to_gemini_schema` 변환 함수 (R-6)
# ---------------------------------------------------------------------------


def test_to_gemini_schema_leaves_judgement_schema_object_unchanged():
    import copy

    before = copy.deepcopy(JUDGEMENT_SCHEMA)
    _to_gemini_schema(JUDGEMENT_SCHEMA)
    assert JUDGEMENT_SCHEMA == before


def test_to_gemini_schema_converts_nullable_integer_and_bounded_number():
    converted = _to_gemini_schema(JUDGEMENT_SCHEMA)

    assert converted["required"] == ["matched_person_id", "s_llm", "reason"]
    assert converted["additionalProperties"] is False

    matched = converted["properties"]["matched_person_id"]
    assert matched["type"] == "INTEGER"
    assert matched["nullable"] is True

    s_llm = converted["properties"]["s_llm"]
    assert s_llm["type"] == "NUMBER"
    assert s_llm["minimum"] == 0
    assert s_llm["maximum"] == 1

    reason = converted["properties"]["reason"]
    assert reason["type"] == "STRING"
    assert "nullable" not in reason


def test_to_gemini_schema_converts_array_field():
    # U3 RESOLUTION_SCHEMA 의 candidate_person_ids 꼴 대비.
    schema = {"type": "array", "items": {"type": "integer"}}
    assert _to_gemini_schema(schema) == {"type": "ARRAY", "items": {"type": "INTEGER"}}


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


def test_judge_from_env_defaults_to_openai(monkeypatch):
    # R-1(a) -- D11 결정 2(기본 LLM_PROVIDER=openai)로 기본값이 바뀐다.
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    judge = judge_from_env(env={})
    assert isinstance(judge, OpenAIJudge)


def test_judge_from_env_openai(monkeypatch):
    # OpenAI() 클라이언트는 생성 시점에 키 존재를 확인한다(Anthropic() 과
    # 달리) -- 실제로 호출하지 않으므로 더미 값으로 생성만 확인한다.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    judge = judge_from_env(env={"LLM_PROVIDER": "openai"})
    assert isinstance(judge, OpenAIJudge)


def test_judge_from_env_gemini_builds_with_model_and_key(monkeypatch):
    # R-1(b) 대체 -- U2 이후 `gemini` 는 실제 `GeminiJudge` 를 만든다
    # (생성은 네트워크를 타지 않는다, R-2 -- 더미 키로 `genai.Client()`
    # 생성까지는 성공하고 `judge()` 호출 시점에만 네트워크를 탄다).
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    monkeypatch.setenv("GEMINI_API_KEY", _FAKE_KEY_MARKER)
    judge = judge_from_env(env={"LLM_PROVIDER": "gemini"})
    assert isinstance(judge, GeminiJudge)
    assert judge.model == "gemini-test-model"


def test_judge_from_env_gemini_missing_model_is_invalid_value(monkeypatch):
    # D11 결정 3 -- GEMINI_MODEL 기본값 없음, 미설정이면 InvalidValue
    # (틀린 이유로 통과하던 옛 테스트를 대체 -- 이름·활성 여부가 아니라
    # 모델 미설정이 원인임을 명시적으로 검증한다).
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", _FAKE_KEY_MARKER)
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
# JUDGES 등록표·활성 스위치 (P3-llm-providers U1, D11) -- 네트워크 0, 더미 키만
# ---------------------------------------------------------------------------


def test_judges_table_has_exactly_three_keys_no_fake():
    assert sorted(JUDGES) == ["anthropic", "gemini", "openai"]
    assert "fake" not in JUDGES


@pytest.mark.parametrize(
    "provider, key_name, judge_cls, extra_env",
    [
        ("anthropic", "ANTHROPIC_API_KEY", ClaudeJudge, {}),
        ("openai", "OPENAI_API_KEY", OpenAIJudge, {}),
        ("gemini", "GEMINI_API_KEY", GeminiJudge, {"GEMINI_MODEL": "gemini-test-model"}),
    ],
)
def test_judge_from_env_builds_each_active_provider(
    monkeypatch, provider, key_name, judge_cls, extra_env
):
    monkeypatch.setenv(key_name, _FAKE_KEY_MARKER)
    for env_name, env_value in extra_env.items():
        monkeypatch.setenv(env_name, env_value)
    judge = judge_from_env(env={"LLM_PROVIDER": provider})
    assert isinstance(judge, judge_cls)


def test_select_provider_rejects_disabled_provider_with_active_list_message():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue) as excinfo:
        judge_from_env(
            env={"LLM_PROVIDER": "gemini", "LLM_PROVIDERS_ENABLED": "anthropic"}
        )
    assert "anthropic" in str(excinfo.value)


def test_select_provider_rejects_unknown_provider_with_table_keys_message():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue) as excinfo:
        judge_from_env(env={"LLM_PROVIDER": "llama"})
    message = str(excinfo.value)
    for name in ("anthropic", "openai", "gemini"):
        assert name in message


def test_select_provider_env_is_single_source_os_environ_does_not_leak(monkeypatch):
    # R-3 -- os.environ 의 LLM_PROVIDERS_ENABLED="gemini" 가 있어도 env 인자로
    # 넘긴 LLM_PROVIDERS_ENABLED="anthropic" 만 쓰인다(openai 는 거부된다).
    from app.tools.types import InvalidValue

    monkeypatch.setenv("LLM_PROVIDERS_ENABLED", "gemini")
    with pytest.raises(InvalidValue):
        judge_from_env(
            env={"LLM_PROVIDER": "openai", "LLM_PROVIDERS_ENABLED": "anthropic"}
        )


@pytest.mark.parametrize(
    "raw, expected",
    [
        (" anthropic , OPENAI ", frozenset({"anthropic", "openai"})),
        ("", frozenset({"anthropic", "openai", "gemini"})),
        ("anthropic,,gemini", frozenset({"anthropic", "gemini"})),
        ("Gemini", frozenset({"gemini"})),
    ],
)
def test_enabled_providers_parsing_rules(raw, expected):
    assert enabled_providers({"LLM_PROVIDERS_ENABLED": raw}) == expected


def test_enabled_providers_missing_key_defaults_to_full_table():
    assert enabled_providers({}) == frozenset({"anthropic", "openai", "gemini"})


def test_enabled_providers_rejects_unknown_name_in_list():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        enabled_providers({"LLM_PROVIDERS_ENABLED": "anthropic,llama"})


def test_select_provider_returns_name_string():
    assert select_provider({"LLM_PROVIDER": "openai"}) == "openai"


def test_dummy_key_marker_does_not_leak_into_exceptions_or_output(monkeypatch, capsys):
    from app.tools.types import InvalidValue

    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    judge = judge_from_env(env={"LLM_PROVIDER": "openai"})
    assert isinstance(judge, OpenAIJudge)

    with pytest.raises(InvalidValue) as excinfo:
        judge_from_env(env={"LLM_PROVIDER": "llama"})
    assert _FAKE_KEY_MARKER not in str(excinfo.value)

    captured = capsys.readouterr()
    assert _FAKE_KEY_MARKER not in captured.out
    assert _FAKE_KEY_MARKER not in captured.err


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
