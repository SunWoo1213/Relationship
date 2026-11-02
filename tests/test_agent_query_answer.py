"""Refs: P5b-query-turn CR-004 D16 S3.6 D11 원칙7 원칙9 R19 -- U3
`app/agent/respond.py` 의 조회 답 생성기·검증기·템플릿 테스트.

DB·루프·API 를 쓰지 않는 순수 층이라 `dbtest` 마커가 없다. 공급자 3종은
스텁 클라이언트로 돌린다(네트워크 0, `tests/test_briefing_compose.py`·
`tests/test_memory_extract.py` 와 같은 관례). 근거 자료는 `PersonCardOut`
을 직접 만들어 넘긴다.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import anthropic
import httpx
import httpx2
import openai
import pytest

from app.agent import (
    QUERY_MORE_HINT,
    QUERY_ONE_AT_A_TIME_HINT,
    FakeQueryAnswerer,
    QueryAnswer,
    answerer_from_env,
    build_query_answer_prompt,
    has_evidence,
    no_mention_reply,
    no_record_reply,
    template_query_answer,
    validate_query_answer,
)
from app.agent.respond import (
    QUERY_ANSWER_SCHEMA,
    QUERY_ANSWER_TOOL_NAME,
    QUERY_ANSWERERS,
    ClaudeQueryAnswerer,
    GeminiQueryAnswerer,
    OpenAIQueryAnswerer,
)
from app.api.schemas import (
    PersonBasicOut,
    PersonCardOut,
    PersonFactOut,
    PersonPatternOut,
    TimelineEventOut,
    UpcomingScheduleOut,
)
from app.briefing.types import BRIEFING_FORBIDDEN_EXPRESSIONS
from app.er.types import JudgeUnavailable
from app.settings import QUERY_ANSWER_MAX_CHARS, QUERY_ANSWER_MAX_LINES, QUERY_TIMELINE_LIMIT

#: secret-guard 오탐 방지용 마커(`tests/test_briefing_compose.py` 와 동일).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

NOW = datetime(2026, 10, 25, 3, 0, 0, tzinfo=timezone.utc)
#: UTC 10-20 16:30 -> 서울(+9) 10월 21일. UTC 로 날짜를 뽑으면 20일이 된다(경계 시각 시드).
BOUNDARY_UTC = datetime(2026, 10, 20, 16, 30, 0, tzinfo=timezone.utc)

QUESTION = "박선우 과장님 요즘 어때?"
EXACT_ONE_FACT_TEMPLATE = (
    "박선우 과장님 — 직장·동, 마지막 접촉 10월 21일, 알고 있는 것 1건. "
    "자세한 건 인물 화면에서 볼 수 있어요."
)


@pytest.fixture(autouse=True)
def _seoul_timezone(monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Seoul")


def _card(
    *,
    facts=(),
    patterns=(),
    timeline=(),
    schedules=(),
    last_contact_at=BOUNDARY_UTC,
    aliases=("과장님", "선우 씨"),
) -> PersonCardOut:
    return PersonCardOut(
        person=PersonBasicOut(id=7777, display_name="박선우 과장님", relation_tag="직장", hierarchy="동"),
        aliases=list(aliases),
        last_contact_at=last_contact_at,
        facts=list(facts),
        patterns=list(patterns),
        timeline=list(timeline),
        upcoming_schedules=list(schedules),
    )


def _fact(key="hobby", value="등산", updated_at=BOUNDARY_UTC) -> PersonFactOut:
    return PersonFactOut(id=8888, key=key, value=value, updated_at=updated_at, source_count=2)


def _pattern(value="3회 (2026-01-01, 2026-02-01, 2026-03-01)") -> PersonPatternOut:
    return PersonPatternOut(id=8889, key="pattern:meal", value=value, source_count=3)


def _event(n: int) -> TimelineEventOut:
    return TimelineEventOut(id=9000 + n, type="meal", content=f"타임라인{n}", occurred_at=BOUNDARY_UTC)


# ---------------------------------------------------------------------------
# 검증기
# ---------------------------------------------------------------------------


def test_forbidden_expression_list_has_fourteen():
    assert len(BRIEFING_FORBIDDEN_EXPRESSIONS) == 14


@pytest.mark.parametrize("bad", BRIEFING_FORBIDDEN_EXPRESSIONS)
def test_validate_rejects_each_forbidden_expression(bad):
    assert validate_query_answer(f"그분은 {bad} 같아요.") == "forbidden_expression"


def test_validate_normal_answer_passes():
    assert validate_query_answer("박선우 과장님은 직장 동료이고 등산을 좋아해요.") is None


def test_validate_line_limit_boundary_three_lines_pass_four_rejected():
    assert QUERY_ANSWER_MAX_LINES == 3
    assert validate_query_answer("가\n나\n다") is None
    assert validate_query_answer("가\n나\n다\n라") == "too_many_lines"


def test_validate_blank_lines_do_not_count():
    assert validate_query_answer("가\n\n나\n  \n다\n") is None


def test_validate_char_limit_boundary_240_pass_241_rejected():
    assert QUERY_ANSWER_MAX_CHARS == 240
    assert validate_query_answer("가" * 240) is None
    assert validate_query_answer("가" * 241) == "too_long"


def test_validate_char_count_uses_stripped_text():
    assert validate_query_answer("  " + "가" * 240 + "\n ") is None


@pytest.mark.parametrize("text", ["", "   ", "\n \n"])
def test_validate_empty_or_blank_is_empty(text):
    assert validate_query_answer(text) == "empty"


def test_validate_order_lines_before_length_before_forbidden():
    assert validate_query_answer("기분\n나\n다\n라") == "too_many_lines"
    assert validate_query_answer("기분" + "가" * 240) == "too_long"


# ---------------------------------------------------------------------------
# 템플릿·고정 응답
# ---------------------------------------------------------------------------


def test_template_with_evidence_exact_string_and_last_contact_in_user_timezone():
    # 경계 시각: UTC 10-20 16:30 -> 서울 10월 21일(UTC 날짜 20일이면 변이로 잡힌다).
    assert template_query_answer(_card(facts=[_fact()]), NOW) == EXACT_ONE_FACT_TEMPLATE


def test_template_count_is_facts_plus_patterns():
    text = template_query_answer(_card(facts=[_fact(), _fact("job", "개발")], patterns=[_pattern()]), NOW)
    assert "알고 있는 것 3건" in text


def test_template_without_last_contact_exact_string():
    card = _card(timeline=[_event(1)], last_contact_at=None)
    assert template_query_answer(card, NOW) == (
        "박선우 과장님 — 직장·동, 마지막 접촉 기록 없음, 알고 있는 것 0건. "
        "자세한 건 인물 화면에서 볼 수 있어요."
    )


def test_template_no_evidence_exact_string_even_with_last_contact():
    card = _card()
    assert not has_evidence(card)
    assert template_query_answer(card, NOW) == (
        "박선우 과장님 — 직장·동로 기억하고 있어요. 그 밖의 기록은 아직 없어요."
    )


@pytest.mark.parametrize(
    "card",
    [
        _card(facts=[_fact()]),
        _card(patterns=[_pattern()]),
        _card(timeline=[_event(1)]),
        _card(schedules=[UpcomingScheduleOut(id=1, title="점심", scheduled_at=BOUNDARY_UTC, briefed_at=None)]),
    ],
)
def test_has_evidence_true_for_each_source(card):
    assert has_evidence(card) is True


def test_template_outputs_pass_validator():
    for card in (_card(facts=[_fact()]), _card(), _card(timeline=[_event(1)], last_contact_at=None)):
        assert validate_query_answer(template_query_answer(card, NOW)) is None


def test_no_record_reply_exact_strings():
    assert no_record_reply(["김철수"]) == '"김철수"에 대한 기록이 없어요.'
    assert no_record_reply(["김철수", "이영희"]) == '"김철수", "이영희"에 대한 기록이 없어요.'


def test_no_record_reply_keeps_input_order():
    assert no_record_reply(["나", "가", "다"]) == '"나", "가", "다"에 대한 기록이 없어요.'


def test_no_mention_reply_exact_string():
    assert no_mention_reply() == "누구에 대해 물어보셨는지 알아듣지 못했어요. 이름을 넣어 다시 물어봐 주세요."


def test_hint_constants_exact_values():
    assert QUERY_ONE_AT_A_TIME_HINT == "한 번에 한 사람씩 물어봐 주세요."
    assert QUERY_MORE_HINT == "자세한 건 인물 화면에서 볼 수 있어요."


# ---------------------------------------------------------------------------
# 프롬프트
# ---------------------------------------------------------------------------

_PRINCIPLE7 = "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다 — 평가·조언·감정 대화는 하지 않는다"


def test_prompt_system_exact_sentences():
    system, _ = build_query_answer_prompt(QUESTION, _card(facts=[_fact()]), NOW)
    assert system == (
        "너는 사용자가 기록해 둔 한 인물의 정보를 묻는 질문에 답하는 보조 도구다. "
        + _PRINCIPLE7
        + " 아래 인물 카드 자료만 근거로 1~3줄 한국어로 답하고, 자료에 없는 것은 '기록이 없어요'라고 답하라. "
        "추측하거나 새 사실을 만들지 마라. 다른 인물과의 관계는 말하지 마라. "
        "위로·조언·감정 표현을 쓰지 마라. report_query_answer 도구로만 답하라."
    )


def test_prompt_user_text_has_question_now_and_evidence_values():
    card = _card(
        facts=[_fact("hobby", "등산")],
        patterns=[_pattern("3회 (2026-01-01, 2026-02-01, 2026-03-01)")],
        timeline=[_event(1)],
        schedules=[UpcomingScheduleOut(id=5, title="저녁 약속", scheduled_at=BOUNDARY_UTC, briefed_at=None)],
    )
    _, user = build_query_answer_prompt(QUESTION, card, NOW)
    assert user.count(QUESTION) == 1
    assert "2026-10-25T12:00:00+09:00" in user  # now 는 사용자 시간대
    for needle in (
        "박선우 과장님",
        "직장·동",
        "과장님, 선우 씨",
        "마지막 접촉: 10월 21일",
        "hobby=등산 (10월 21일)",
        "3회 (2026-01-01, 2026-02-01, 2026-03-01)",
        "[meal] 타임라인1 (10월 21일)",
        "저녁 약속 (10월 21일)",
    ):
        assert needle in user, needle


def test_prompt_excludes_raw_ids_and_secrets():
    card = _card(facts=[_fact()], timeline=[_event(1)])
    system, user = build_query_answer_prompt(QUESTION, card, NOW)
    text = system + "\n" + user
    for banned in ("절대노출금지", "raw_utterance", "7777", "8888", "9001", "source_count", "briefed_at"):
        assert banned not in text, banned
    for banned in ("API_KEY", "ANTHROPIC", "OPENAI", "GEMINI", "LLM_PROVIDER"):
        assert banned not in text, banned


def test_prompt_timeline_limit_keeps_only_first_five():
    assert QUERY_TIMELINE_LIMIT == 5
    card = _card(timeline=[_event(n) for n in range(1, 7)])
    _, user = build_query_answer_prompt(QUESTION, card, NOW)
    for n in range(1, 6):
        assert f"타임라인{n} " in user
    assert "타임라인6" not in user


def test_prompt_last_contact_date_in_user_timezone_not_utc():
    _, user = build_query_answer_prompt(QUESTION, _card(facts=[_fact()]), NOW)
    assert "마지막 접촉: 10월 21일" in user
    assert "10월 20일" not in user


# ---------------------------------------------------------------------------
# Fake·QueryAnswer
# ---------------------------------------------------------------------------


def test_query_answer_trace_tokens_shape():
    answer = QueryAnswer(text="x", tokens_in=3, tokens_out=4, provider="p", model="m")
    assert answer.trace_tokens() == (3, 4)


def test_fake_answerer_table_and_default_and_call_count():
    fake = FakeQueryAnswerer(table={QUESTION: "등산을 좋아해요."})
    got = fake.answer(QUESTION, _card(), NOW)
    assert (got.text, got.provider, got.tokens_in, got.tokens_out) == ("등산을 좋아해요.", "fake", 0, 0)
    assert fake.answer("다른 질문", _card(), NOW).text == ""
    assert fake.call_count == 2


def test_fake_answerer_fail_raises_judge_unavailable_and_counts():
    fake = FakeQueryAnswerer(fail="timeout")
    with pytest.raises(JudgeUnavailable) as excinfo:
        fake.answer(QUESTION, _card(), NOW)
    assert str(excinfo.value) == "timeout"
    assert fake.call_count == 1


# ---------------------------------------------------------------------------
# 스키마
# ---------------------------------------------------------------------------


def test_schema_and_tool_name_exact_values():
    assert QUERY_ANSWER_TOOL_NAME == "report_query_answer"
    assert QUERY_ANSWER_SCHEMA == {
        "type": "object",
        "properties": {"answer": {"type": "string"}},
        "required": ["answer"],
        "additionalProperties": False,
    }


# ---------------------------------------------------------------------------
# 공급자 3종 (스텁 클라이언트)
# ---------------------------------------------------------------------------


class _Calls:
    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict] = []

    def _go(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


class StubClaudeClient(_Calls):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.messages = SimpleNamespace(create=self._go)


class StubOpenAIClient(_Calls):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._go))


class StubGeminiClient(_Calls):
    def __init__(self, response) -> None:
        super().__init__(response)
        self.models = SimpleNamespace(generate_content=self._go)


def _claude_response(output, tokens=(12, 34)):
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=QUERY_ANSWER_TOOL_NAME, input=output)],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model="claude-sonnet-5",
    )


def _openai_response(output, tokens=(5, 6)):
    function = SimpleNamespace(name=QUERY_ANSWER_TOOL_NAME, arguments=json.dumps(output))
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[SimpleNamespace(function=function)]))],
        usage=SimpleNamespace(prompt_tokens=tokens[0], completion_tokens=tokens[1]),
        model="gpt-4o-mini",
    )


def _gemini_response(output, tokens=(7, 8)):
    return SimpleNamespace(
        text=json.dumps(output),
        usage_metadata=SimpleNamespace(prompt_token_count=tokens[0], candidates_token_count=tokens[1]),
        model_version="gemini-test-model",
    )


def _anthropic_request() -> httpx2.Request:
    return httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def _openai_request() -> httpx.Request:
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


_ANSWER = {"answer": "박선우 과장님은 등산을 좋아해요."}
_CARD = _card(facts=[_fact()])


def test_claude_answerer_request_forces_tool_choice_and_schema(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = StubClaudeClient(_claude_response(_ANSWER))
    ClaudeQueryAnswerer(client=client).answer(QUESTION, _CARD, NOW)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "tool", "name": "report_query_answer"}
    assert kwargs["tools"] == [
        {
            "name": "report_query_answer",
            "description": kwargs["tools"][0]["description"],
            "input_schema": QUERY_ANSWER_SCHEMA,
        }
    ]
    assert QUESTION in kwargs["messages"][0]["content"]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "ANTHROPIC" not in body_str
    assert "api_key" not in body_str.lower()


def test_claude_answerer_parses_text_and_usage():
    client = StubClaudeClient(_claude_response(_ANSWER, tokens=(5, 7)))
    got = ClaudeQueryAnswerer(client=client).answer(QUESTION, _CARD, NOW)
    assert got.text == "박선우 과장님은 등산을 좋아해요."
    assert got.trace_tokens() == (5, 7)
    assert got.provider == "anthropic"


def test_claude_answerer_no_tool_use_is_schema_error():
    response = SimpleNamespace(content=[SimpleNamespace(type="text", text="음")], usage=None, model="m")
    with pytest.raises(JudgeUnavailable) as excinfo:
        ClaudeQueryAnswerer(client=StubClaudeClient(response)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "schema"


@pytest.mark.parametrize("bad_output", [{"answer": 123}, {"answer": None}, {}, {"text": "x"}])
def test_claude_answerer_non_string_answer_is_schema_error_not_empty(bad_output):
    client = StubClaudeClient(_claude_response(bad_output))
    with pytest.raises(JudgeUnavailable) as excinfo:
        ClaudeQueryAnswerer(client=client).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "schema"


def test_claude_answerer_empty_string_answer_passes_through_for_validator():
    client = StubClaudeClient(_claude_response({"answer": ""}))
    got = ClaudeQueryAnswerer(client=client).answer(QUESTION, _CARD, NOW)
    assert got.text == ""
    assert validate_query_answer(got.text) == "empty"


def test_claude_answerer_maps_timeout_error():
    exc = anthropic.APITimeoutError(request=_anthropic_request())
    with pytest.raises(JudgeUnavailable) as excinfo:
        ClaudeQueryAnswerer(client=StubClaudeClient(exc)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "timeout"


def test_claude_answerer_maps_rate_limit_error():
    resp = httpx2.Response(429, request=_anthropic_request(), json={"error": {"type": "rate_limit_error"}})
    exc = anthropic.RateLimitError("rate limited", response=resp, body=None)
    with pytest.raises(JudgeUnavailable) as excinfo:
        ClaudeQueryAnswerer(client=StubClaudeClient(exc)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "rate_limit"


def test_claude_answerer_default_model_follows_env_and_reuses_judge_timeout(monkeypatch):
    from app.settings import ER_JUDGE_MAX_RETRIES, ER_JUDGE_TIMEOUT

    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-custom-1")
    answerer = ClaudeQueryAnswerer(client=StubClaudeClient(_claude_response(_ANSWER)))
    assert answerer.model == "claude-custom-1"
    assert answerer.timeout == ER_JUDGE_TIMEOUT
    assert answerer.max_retries == ER_JUDGE_MAX_RETRIES


def test_openai_answerer_request_and_parse():
    client = StubOpenAIClient(_openai_response(_ANSWER, tokens=(5, 6)))
    got = OpenAIQueryAnswerer(client=client).answer(QUESTION, _CARD, NOW)
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "function", "function": {"name": "report_query_answer"}}
    assert kwargs["tools"][0]["function"]["parameters"] == QUERY_ANSWER_SCHEMA
    assert got.text == "박선우 과장님은 등산을 좋아해요."
    assert got.trace_tokens() == (5, 6)
    assert got.provider == "openai"


def test_openai_answerer_no_tool_calls_is_schema_error():
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=None))], usage=None, model="m")
    with pytest.raises(JudgeUnavailable) as excinfo:
        OpenAIQueryAnswerer(client=StubOpenAIClient(response)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "schema"


def test_openai_answerer_non_string_answer_is_schema_error():
    with pytest.raises(JudgeUnavailable) as excinfo:
        OpenAIQueryAnswerer(client=StubOpenAIClient(_openai_response({"answer": 1}))).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "schema"


def test_openai_answerer_maps_timeout_and_connection_errors():
    for exc, want in (
        (openai.APITimeoutError(request=_openai_request()), "timeout"),
        (openai.APIConnectionError(request=_openai_request()), "connection"),
    ):
        with pytest.raises(JudgeUnavailable) as excinfo:
            OpenAIQueryAnswerer(client=StubOpenAIClient(exc)).answer(QUESTION, _CARD, NOW)
        assert str(excinfo.value) == want


def test_openai_answerer_maps_rate_limit_error():
    resp = httpx.Response(429, request=_openai_request(), json={"error": {"type": "rate_limit"}})
    exc = openai.RateLimitError("rate limited", response=resp, body=None)
    with pytest.raises(JudgeUnavailable) as excinfo:
        OpenAIQueryAnswerer(client=StubOpenAIClient(exc)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "rate_limit"


def test_gemini_answerer_requires_model_env(monkeypatch):
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    with pytest.raises(InvalidValue):
        GeminiQueryAnswerer(client=StubGeminiClient(_gemini_response(_ANSWER)))


def test_gemini_answerer_request_uses_schema_and_parses():
    from app.er.judge import _to_gemini_schema

    client = StubGeminiClient(_gemini_response(_ANSWER, tokens=(7, 8)))
    got = GeminiQueryAnswerer(model="gemini-test-model", client=client).answer(QUESTION, _CARD, NOW)
    config = client.calls[0]["config"]
    assert config.response_schema == _to_gemini_schema(QUERY_ANSWER_SCHEMA)
    assert got.text == "박선우 과장님은 등산을 좋아해요."
    assert got.trace_tokens() == (7, 8)
    assert got.provider == "gemini"


def test_gemini_answerer_bad_json_and_non_string_are_schema_errors():
    for response in (
        SimpleNamespace(text="모르겠다", usage_metadata=None, model_version="m"),
        SimpleNamespace(text=None, usage_metadata=None, model_version="m"),
        _gemini_response({"answer": 5}),
    ):
        with pytest.raises(JudgeUnavailable) as excinfo:
            GeminiQueryAnswerer(model="m", client=StubGeminiClient(response)).answer(QUESTION, _CARD, NOW)
        assert str(excinfo.value) == "schema"


def test_gemini_answerer_maps_rate_limit_and_timeout_errors():
    from google.genai import errors as genai_errors

    rate = genai_errors.ClientError(429, {"error": {"message": "rate limited"}}, None)
    with pytest.raises(JudgeUnavailable) as excinfo:
        GeminiQueryAnswerer(model="m", client=StubGeminiClient(rate)).answer(QUESTION, _CARD, NOW)
    assert str(excinfo.value) == "rate_limit"

    with pytest.raises(JudgeUnavailable) as excinfo:
        GeminiQueryAnswerer(model="m", client=StubGeminiClient(httpx.ReadTimeout("t"))).answer(
            QUESTION, _CARD, NOW
        )
    assert str(excinfo.value) == "timeout"


# ---------------------------------------------------------------------------
# 등록표·answerer_from_env
# ---------------------------------------------------------------------------


def test_query_answerers_registry_has_three_providers():
    assert set(QUERY_ANSWERERS) == {"anthropic", "openai", "gemini"}


@pytest.mark.parametrize(
    "provider, key_name, cls, extra_env",
    [
        ("anthropic", "ANTHROPIC_API_KEY", ClaudeQueryAnswerer, {}),
        ("openai", "OPENAI_API_KEY", OpenAIQueryAnswerer, {}),
        ("gemini", "GEMINI_API_KEY", GeminiQueryAnswerer, {"GEMINI_MODEL": "gemini-test-model"}),
    ],
)
def test_answerer_from_env_follows_llm_provider(monkeypatch, provider, key_name, cls, extra_env):
    monkeypatch.setenv(key_name, _FAKE_KEY_MARKER)
    for name, value in extra_env.items():
        monkeypatch.setenv(name, value)
    assert isinstance(answerer_from_env(env={"LLM_PROVIDER": provider}), cls)


def test_answerer_from_env_unknown_and_disabled_rejected():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        answerer_from_env(env={"LLM_PROVIDER": "llama"})
    with pytest.raises(InvalidValue):
        answerer_from_env(env={"LLM_PROVIDER": "gemini", "LLM_PROVIDERS_ENABLED": "anthropic"})
