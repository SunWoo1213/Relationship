"""Refs: P6-memory D11 D-2 D-3 D-4 D-5 D-7 R8 원칙7 원칙8 원칙9 -- U4
`app/memory/extract.py` 테스트. 검증기(`validate_extraction`)의 거부
사유 5종을 개별 사실 단위로 고정하고, 공급자 3종(스텁 클라이언트, 네트워크
0)·`FakeFactExtractor`(결정 D-3)·`extractor_from_env`(D11 `select_provider`
재사용)를 검증한다.

네트워크 호출 없음(원칙8, `tests/test_agent_propose.py`/`tests/test_er_judge.py`
와 같은 스텁 클라이언트 패턴). DB 를 쓰지 않는다(`extract()` 는 `ctx`/
세션을 받지 않는다) -- `dbtest` 마커가 없다.
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

from app.memory.extract import (
    FACT_EXTRACTORS,
    FACTS_SCHEMA,
    FACTS_TOOL_NAME,
    REASON_EMPTY_VALUE,
    REASON_KEY_NOT_IN_VOCAB,
    REASON_OVER_CAP,
    REASON_PATTERN_PREFIX,
    REASON_UNKNOWN_EVENT_ID,
    ClaudeFactExtractor,
    ExistingFact,
    ExtractEvent,
    FakeFactExtractor,
    GeminiFactExtractor,
    OpenAIFactExtractor,
    build_extract_prompt,
    extractor_from_env,
    validate_extraction,
)
from app.memory.types import FACT_KEYS, Extraction, ExtractedFact
from app.er.types import JudgeUnavailable
from app.settings import MEMORY_MAX_FACTS, PATTERN_KEY_PREFIX

#: P3-er F-46f1eb 규약과 같은 마커(secret-guard 오탐 방지, `tests/test_er_judge.py`
#: 와 동일).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

NOW = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)


def _events(*ids: int) -> list[ExtractEvent]:
    return [
        ExtractEvent(
            id=event_id,
            type="personal_share",
            content=f"내용 {event_id}",
            raw_utterance=f"raw {event_id}",
            occurred_at=NOW,
        )
        for event_id in ids
    ]


# ---------------------------------------------------------------------------
# FACTS_SCHEMA 구조 -- FACT_KEYS 와의 정합
# ---------------------------------------------------------------------------


def test_facts_schema_key_enum_matches_fact_keys():
    item_schema = FACTS_SCHEMA["properties"]["facts"]["items"]
    assert item_schema["properties"]["key"]["enum"] == list(FACT_KEYS)


def test_facts_schema_top_level_requires_facts_only():
    assert FACTS_SCHEMA["required"] == ["facts"]
    assert FACTS_SCHEMA["additionalProperties"] is False


def test_facts_schema_item_requires_all_three_fields():
    item_schema = FACTS_SCHEMA["properties"]["facts"]["items"]
    assert set(item_schema["required"]) == {"key", "value", "source_event_ids"}
    assert item_schema["additionalProperties"] is False


# ---------------------------------------------------------------------------
# build_extract_prompt -- 경계 문구·키·환경변수 미노출
# ---------------------------------------------------------------------------


def test_build_extract_prompt_has_person_existing_facts_and_events():
    prompt = build_extract_prompt(
        "민수",
        [ExistingFact(key="hobby", value="등산")],
        _events(1, 2),
    )
    combined = "".join(prompt)
    assert "민수" in combined
    assert "hobby: 등산" in combined
    assert "id=1" in combined and "id=2" in combined


def test_build_extract_prompt_lists_fact_keys_and_pattern_prefix_ban():
    system, _ = build_extract_prompt("민수", [], [])
    for key in FACT_KEYS:
        assert key in system
    assert "pattern:" in system


def test_build_extract_prompt_forbids_cross_person_relations_and_advice():
    system, _ = build_extract_prompt("민수", [], [])
    assert "두 사람 사이의 관계" in system
    assert "감정 해석" in system or "조언" in system


def test_build_extract_prompt_has_no_secrets_or_env_names():
    system, user_text = build_extract_prompt("민수", [], _events(1))
    combined = system + user_text
    assert "ANTHROPIC" not in combined
    assert "OPENAI" not in combined
    assert "GEMINI" not in combined
    assert "os.environ" not in combined
    assert "api_key" not in combined.lower()


def test_build_extract_prompt_empty_events_and_facts_render_placeholder():
    system, user_text = build_extract_prompt("민수", [], [])
    assert "(없음)" in user_text


# ---------------------------------------------------------------------------
# validate_extraction -- 거부 사유 5종, 개별 사실 단위 거부
# ---------------------------------------------------------------------------


def test_validate_extraction_accepts_well_formed_fact():
    extraction = Extraction(
        facts=[ExtractedFact(key="hobby", value="등산", source_event_ids=[1])]
    )
    result = validate_extraction(extraction, _events(1, 2))
    assert result.rejected == []
    assert result.facts == [ExtractedFact(key="hobby", value="등산", source_event_ids=[1])]


def test_validate_extraction_rejects_key_outside_vocab():
    extraction = Extraction(
        facts=[ExtractedFact(key="favorite_color", value="파랑", source_event_ids=[1])]
    )
    result = validate_extraction(extraction, _events(1))
    assert result.facts == []
    assert len(result.rejected) == 1
    assert result.rejected[0].reason == REASON_KEY_NOT_IN_VOCAB
    assert result.rejected[0].index == 0
    assert result.rejected[0].key == "favorite_color"


@pytest.mark.parametrize(
    "raw_key",
    ["pattern:meal", " pattern:meal ", "Pattern:meal", "PATTERN:MEAL", "PaTtErN:conflict"],
)
def test_validate_extraction_rejects_pattern_prefix_key_case_and_space_variants(raw_key):
    extraction = Extraction(facts=[ExtractedFact(key=raw_key, value="3회", source_event_ids=[1])])
    result = validate_extraction(extraction, _events(1))
    assert result.facts == []
    assert len(result.rejected) == 1
    assert result.rejected[0].reason == REASON_PATTERN_PREFIX


def test_validate_extraction_non_prefixed_unknown_key_is_vocab_reason_not_prefix_reason():
    # "patterns" 는 PATTERN_KEY_PREFIX("pattern:") 로 시작하지 않는다 --
    # 사유가 2번(REASON_PATTERN_PREFIX)이 아니라 1번(REASON_KEY_NOT_IN_VOCAB)
    # 이어야 한다(경계 검사, 사유를 구분해서 본다).
    assert not "patterns".startswith(PATTERN_KEY_PREFIX)
    extraction = Extraction(facts=[ExtractedFact(key="patterns", value="x", source_event_ids=[1])])
    result = validate_extraction(extraction, _events(1))
    assert len(result.rejected) == 1
    assert result.rejected[0].reason == REASON_KEY_NOT_IN_VOCAB


@pytest.mark.parametrize("empty_value", ["", "   ", "\t\n"])
def test_validate_extraction_rejects_empty_value(empty_value):
    extraction = Extraction(
        facts=[ExtractedFact(key="hobby", value=empty_value, source_event_ids=[1])]
    )
    result = validate_extraction(extraction, _events(1))
    assert result.facts == []
    assert result.rejected[0].reason == REASON_EMPTY_VALUE


def test_validate_extraction_rejects_source_event_id_not_in_input():
    extraction = Extraction(
        facts=[ExtractedFact(key="hobby", value="등산", source_event_ids=[999])]
    )
    result = validate_extraction(extraction, _events(1, 2))
    assert result.facts == []
    assert result.rejected[0].reason == REASON_UNKNOWN_EVENT_ID


def test_validate_extraction_rejects_empty_source_event_ids():
    extraction = Extraction(facts=[ExtractedFact(key="hobby", value="등산", source_event_ids=[])])
    result = validate_extraction(extraction, _events(1, 2))
    assert result.facts == []
    assert result.rejected[0].reason == REASON_UNKNOWN_EVENT_ID


def test_validate_extraction_rejects_fact_with_partially_unknown_event_ids():
    extraction = Extraction(
        facts=[ExtractedFact(key="hobby", value="등산", source_event_ids=[1, 999])]
    )
    result = validate_extraction(extraction, _events(1, 2))
    assert result.facts == []
    assert result.rejected[0].reason == REASON_UNKNOWN_EVENT_ID


def test_validate_extraction_middle_fact_rejected_others_pass_index_correct():
    extraction = Extraction(
        facts=[
            ExtractedFact(key="job", value="개발자", source_event_ids=[1]),
            ExtractedFact(key="favorite_color", value="파랑", source_event_ids=[1]),
            ExtractedFact(key="family", value="형 있음", source_event_ids=[2]),
        ]
    )
    result = validate_extraction(extraction, _events(1, 2))
    assert [f.key for f in result.facts] == ["job", "family"]
    assert len(result.rejected) == 1
    assert result.rejected[0].index == 1
    assert result.rejected[0].key == "favorite_color"
    assert result.rejected[0].reason == REASON_KEY_NOT_IN_VOCAB


def test_validate_extraction_over_cap_rejects_from_the_index_after_the_cap():
    # FACT_KEYS 는 9종, MEMORY_MAX_FACTS 는 8 -- 9번째(마지막) 키만 상한
    # 초과로 거부된다(이 단위가 정한 것 3: 순서대로 앞에서부터 받아들인다).
    assert len(FACT_KEYS) == MEMORY_MAX_FACTS + 1
    facts = [
        ExtractedFact(key=key, value=f"값 {i}", source_event_ids=[1])
        for i, key in enumerate(FACT_KEYS)
    ]
    result = validate_extraction(Extraction(facts=facts), _events(1))
    assert len(result.facts) == MEMORY_MAX_FACTS
    assert [f.key for f in result.facts] == list(FACT_KEYS[:MEMORY_MAX_FACTS])
    assert len(result.rejected) == 1
    assert result.rejected[0].index == MEMORY_MAX_FACTS
    assert result.rejected[0].key == FACT_KEYS[MEMORY_MAX_FACTS]
    assert result.rejected[0].reason == REASON_OVER_CAP


def test_validate_extraction_strips_whitespace_from_accepted_key_and_value():
    extraction = Extraction(
        facts=[ExtractedFact(key=" hobby ", value=" 등산 ", source_event_ids=[1])]
    )
    result = validate_extraction(extraction, _events(1))
    assert result.facts == [ExtractedFact(key="hobby", value="등산", source_event_ids=[1])]


def test_validate_extraction_empty_input_is_a_noop():
    result = validate_extraction(Extraction(facts=[]), _events(1))
    assert result.facts == []
    assert result.rejected == []


# ---------------------------------------------------------------------------
# FakeFactExtractor -- 결정적·네트워크 0·호출 횟수 (결정 D-3)
# ---------------------------------------------------------------------------


def test_fake_fact_extractor_returns_table_entry_for_matching_event_id_set():
    extractor = FakeFactExtractor(
        table={frozenset({1, 2}): [{"key": "hobby", "value": "등산", "source_event_ids": [1]}]}
    )
    extraction = extractor.extract("민수", [], _events(1, 2))
    assert len(extraction.facts) == 1
    assert extraction.facts[0].key == "hobby"
    assert extraction.provider == "fake"


def test_fake_fact_extractor_missing_table_entry_returns_empty_extraction():
    extractor = FakeFactExtractor(table={})
    extraction = extractor.extract("민수", [], _events(1))
    assert extraction.facts == []


def test_fake_fact_extractor_is_deterministic_across_calls():
    extractor = FakeFactExtractor(
        table={frozenset({1}): [{"key": "hobby", "value": "등산", "source_event_ids": [1]}]}
    )
    first = extractor.extract("민수", [], _events(1))
    second = extractor.extract("민수", [], _events(1))
    assert first.facts == second.facts


def test_fake_fact_extractor_counts_calls():
    extractor = FakeFactExtractor(table={})
    assert extractor.call_count == 0
    extractor.extract("민수", [], _events(1))
    extractor.extract("민수", [], _events(2))
    assert extractor.call_count == 2


def test_fake_fact_extractor_fail_raises_judge_unavailable_and_still_counts():
    extractor = FakeFactExtractor(table={}, fail="timeout")
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "timeout"
    assert extractor.call_count == 1


def test_fake_fact_extractor_ignores_existing_facts_and_person_for_keying():
    extractor = FakeFactExtractor(
        table={frozenset({5}): [{"key": "job", "value": "개발자", "source_event_ids": [5]}]}
    )
    a = extractor.extract("민수", [ExistingFact(key="job", value="예전 직업")], _events(5))
    b = extractor.extract("다른사람", [], _events(5))
    assert a.facts == b.facts


# ---------------------------------------------------------------------------
# 스텁 클라이언트 (네트워크 없음, tests/test_agent_propose.py 와 같은 패턴)
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
        if isinstance(self._outer.response, BaseException):
            raise self._outer.response
        return self._outer.response


class StubGeminiClient:
    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.models = _StubGeminiModels(self)


_SAMPLE_FACT = {"key": "hobby", "value": "등산", "source_event_ids": [1]}


def _claude_facts_response(facts, *, tokens=(12, 34), model="claude-sonnet-5"):
    return SimpleNamespace(
        content=[
            SimpleNamespace(type="tool_use", name=FACTS_TOOL_NAME, input={"facts": facts})
        ],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model=model,
        stop_reason="tool_use",
    )


def _openai_facts_response(facts, *, model="gpt-4o-mini"):
    function = SimpleNamespace(name=FACTS_TOOL_NAME, arguments=json.dumps({"facts": facts}))
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        model=model,
    )


def _gemini_facts_response(facts, *, model="gemini-test-model"):
    return SimpleNamespace(
        text=json.dumps({"facts": facts}),
        usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=1),
        model_version=model,
    )


def _anthropic_request(url: str = "https://api.anthropic.com/v1/messages") -> httpx2.Request:
    return httpx2.Request("POST", url)


def _openai_request(url: str = "https://api.openai.com/v1/chat/completions") -> httpx.Request:
    return httpx.Request("POST", url)


# ---------------------------------------------------------------------------
# ClaudeFactExtractor
# ---------------------------------------------------------------------------


def test_claude_extractor_request_body_forces_tool_choice_and_schema(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = StubClaudeClient(_claude_facts_response([_SAMPLE_FACT]))
    extractor = ClaudeFactExtractor(client=client)

    extractor.extract("민수", [], _events(1))

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "tool", "name": FACTS_TOOL_NAME}
    assert kwargs["tools"] == [
        {
            "name": FACTS_TOOL_NAME,
            "description": kwargs["tools"][0]["description"],
            "input_schema": FACTS_SCHEMA,
        }
    ]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "민수" in body_str
    assert "ANTHROPIC" not in body_str
    assert "api_key" not in body_str.lower()


def test_claude_extractor_parses_tool_use_into_extraction_with_usage():
    client = StubClaudeClient(_claude_facts_response([_SAMPLE_FACT], tokens=(5, 7)))
    extractor = ClaudeFactExtractor(client=client)

    result = extractor.extract("민수", [], _events(1))

    assert len(result.facts) == 1
    assert result.facts[0].key == "hobby"
    assert result.tokens_in == 5
    assert result.tokens_out == 7
    assert result.provider == "anthropic"


def test_claude_extractor_no_tool_use_block_is_schema_error():
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="모르겠다")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        model="claude-sonnet-5",
        stop_reason="end_turn",
    )
    extractor = ClaudeFactExtractor(client=StubClaudeClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "schema"


def test_claude_extractor_maps_timeout_error():
    exc = anthropic.APITimeoutError(request=_anthropic_request())
    extractor = ClaudeFactExtractor(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "timeout"


def test_claude_extractor_maps_rate_limit_error():
    req = _anthropic_request()
    resp = httpx2.Response(429, request=req, json={"error": {"type": "rate_limit_error"}})
    exc = anthropic.RateLimitError("rate limited", response=resp, body=None)
    extractor = ClaudeFactExtractor(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "rate_limit"


def test_claude_extractor_maps_connection_error():
    exc = anthropic.APIConnectionError(request=_anthropic_request())
    extractor = ClaudeFactExtractor(client=StubClaudeClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "connection"


def test_claude_extractor_default_model_follows_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-custom-1")
    extractor = ClaudeFactExtractor(client=StubClaudeClient(_claude_facts_response([])))
    assert extractor.model == "claude-custom-1"


def test_claude_extractor_reuses_er_judge_timeout_default():
    from app.settings import ER_JUDGE_MAX_RETRIES, ER_JUDGE_TIMEOUT

    extractor = ClaudeFactExtractor(client=StubClaudeClient(_claude_facts_response([])))
    assert extractor.timeout == ER_JUDGE_TIMEOUT
    assert extractor.max_retries == ER_JUDGE_MAX_RETRIES


# ---------------------------------------------------------------------------
# OpenAIFactExtractor
# ---------------------------------------------------------------------------


def test_openai_extractor_request_body_forces_tool_choice_and_schema():
    client = StubOpenAIClient(_openai_facts_response([_SAMPLE_FACT]))
    extractor = OpenAIFactExtractor(client=client)

    extractor.extract("민수", [], _events(1))

    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "function", "function": {"name": FACTS_TOOL_NAME}}
    assert kwargs["tools"] == [
        {
            "type": "function",
            "function": {
                "name": FACTS_TOOL_NAME,
                "description": kwargs["tools"][0]["function"]["description"],
                "parameters": FACTS_SCHEMA,
            },
        }
    ]


def test_openai_extractor_parses_tool_call_into_extraction():
    client = StubOpenAIClient(_openai_facts_response([_SAMPLE_FACT]))
    extractor = OpenAIFactExtractor(client=client)

    result = extractor.extract("민수", [], _events(1))

    assert len(result.facts) == 1
    assert result.facts[0].key == "hobby"
    assert result.provider == "openai"


def test_openai_extractor_no_tool_call_is_schema_error():
    message = SimpleNamespace(tool_calls=None)
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(
        choices=[choice], usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model="gpt-4o-mini"
    )
    extractor = OpenAIFactExtractor(client=StubOpenAIClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "schema"


def test_openai_extractor_invalid_json_arguments_is_schema_error():
    function = SimpleNamespace(name=FACTS_TOOL_NAME, arguments="{not valid json")
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(
        choices=[choice], usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model="gpt-4o-mini"
    )
    extractor = OpenAIFactExtractor(client=StubOpenAIClient(response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "schema"


def test_openai_extractor_maps_timeout_error():
    exc = openai.APITimeoutError(request=_openai_request())
    extractor = OpenAIFactExtractor(client=StubOpenAIClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "timeout"


def test_openai_extractor_maps_connection_error():
    exc = openai.APIConnectionError(request=_openai_request())
    extractor = OpenAIFactExtractor(client=StubOpenAIClient(exc))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "connection"


# ---------------------------------------------------------------------------
# GeminiFactExtractor (네트워크 0, judge.py 의 오류 매핑·스키마 변환 재사용)
# ---------------------------------------------------------------------------


def test_gemini_extractor_missing_model_env_raises_invalid_value(monkeypatch):
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    with pytest.raises(InvalidValue):
        GeminiFactExtractor(client=StubGeminiClient(response=_gemini_facts_response([])))


def test_gemini_extractor_request_uses_facts_schema():
    from app.er.judge import _to_gemini_schema

    client = StubGeminiClient(response=_gemini_facts_response([]))
    extractor = GeminiFactExtractor(model="gemini-test-model", client=client)
    extractor.extract("민수", [], _events(1))

    config = client.calls[0]["config"]
    assert config.response_schema == _to_gemini_schema(FACTS_SCHEMA)
    assert config.temperature == 0
    assert config.response_mime_type == "application/json"


def test_gemini_extractor_parses_text_into_extraction():
    client = StubGeminiClient(response=_gemini_facts_response([_SAMPLE_FACT]))
    extractor = GeminiFactExtractor(model="gemini-test-model", client=client)

    result = extractor.extract("민수", [], _events(1))

    assert len(result.facts) == 1
    assert result.provider == "gemini"


def test_gemini_extractor_text_not_json_is_schema_error():
    response = SimpleNamespace(text="모르겠다", usage_metadata=None, model_version="gemini-test-model")
    extractor = GeminiFactExtractor(model="gemini-test-model", client=StubGeminiClient(response=response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "schema"


def test_gemini_extractor_no_text_is_schema_error():
    response = SimpleNamespace(text=None, usage_metadata=None, model_version="gemini-test-model")
    extractor = GeminiFactExtractor(model="gemini-test-model", client=StubGeminiClient(response=response))
    with pytest.raises(JudgeUnavailable) as excinfo:
        extractor.extract("민수", [], _events(1))
    assert str(excinfo.value) == "schema"


# ---------------------------------------------------------------------------
# FACT_EXTRACTORS 등록표 · extractor_from_env (D11 select_provider 재사용)
# ---------------------------------------------------------------------------


def test_fact_extractors_table_has_exactly_three_keys_no_fake():
    assert sorted(FACT_EXTRACTORS) == ["anthropic", "gemini", "openai"]
    assert "fake" not in FACT_EXTRACTORS


@pytest.mark.parametrize(
    "provider, key_name, extractor_cls, extra_env",
    [
        ("anthropic", "ANTHROPIC_API_KEY", ClaudeFactExtractor, {}),
        ("openai", "OPENAI_API_KEY", OpenAIFactExtractor, {}),
        ("gemini", "GEMINI_API_KEY", GeminiFactExtractor, {"GEMINI_MODEL": "gemini-test-model"}),
    ],
)
def test_extractor_from_env_builds_each_active_provider(
    monkeypatch, provider, key_name, extractor_cls, extra_env
):
    monkeypatch.setenv(key_name, _FAKE_KEY_MARKER)
    for env_name, env_value in extra_env.items():
        monkeypatch.setenv(env_name, env_value)
    extractor = extractor_from_env(env={"LLM_PROVIDER": provider})
    assert isinstance(extractor, extractor_cls)


def test_extractor_from_env_defaults_to_openai(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    extractor = extractor_from_env(env={})
    assert isinstance(extractor, OpenAIFactExtractor)


def test_extractor_from_env_unknown_provider_rejected():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        extractor_from_env(env={"LLM_PROVIDER": "llama"})


def test_extractor_from_env_rejects_disabled_provider():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue) as excinfo:
        extractor_from_env(env={"LLM_PROVIDER": "gemini", "LLM_PROVIDERS_ENABLED": "anthropic"})
    assert "anthropic" in str(excinfo.value)


def test_extractor_from_env_uses_os_environ_when_env_omitted(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    extractor = extractor_from_env()
    assert isinstance(extractor, OpenAIFactExtractor)


def test_dummy_key_marker_does_not_leak_into_exceptions_or_output(monkeypatch, capsys):
    from app.tools.types import InvalidValue

    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    extractor = extractor_from_env(env={"LLM_PROVIDER": "openai"})
    assert isinstance(extractor, OpenAIFactExtractor)

    with pytest.raises(InvalidValue) as excinfo:
        extractor_from_env(env={"LLM_PROVIDER": "llama"})
    assert _FAKE_KEY_MARKER not in str(excinfo.value)

    captured = capsys.readouterr()
    assert _FAKE_KEY_MARKER not in captured.out
    assert _FAKE_KEY_MARKER not in captured.err
