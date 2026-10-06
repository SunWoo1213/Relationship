"""Refs: P6-briefing S3.6 R19 D11 원칙6 원칙7 원칙8 -- U4
`app/briefing/compose.py` 테스트. 검증기(`validate_briefing`)의 거부 사유
7종(+ R-4 패턴 보강 2건)을 항목 단위로 고정하고, 공급자 3종(스텁 클라이언트,
네트워크 0)·`FakeBriefingComposer`·`composer_from_env`(D11 `select_provider`
재사용)·`template_briefing`·프롬프트 경계 문구(판정 표 20행)를 검증한다.

네트워크 호출 없음(원칙8, `tests/test_memory_extract.py`/
`tests/test_er_judge.py` 와 같은 스텁 클라이언트 패턴). DB 를 쓰지 않는다
(`BriefingInput` 은 U3 가 만드는 평범한 dataclass 이고, 이 테스트는 직접
만들어 쓴다) -- `dbtest` 마커가 없다.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.briefing.compose import (
    BRIEFING_COMPOSERS,
    BRIEFING_SCHEMA,
    BRIEFING_TOOL_NAME,
    REASON_BASIS_NOT_ELIGIBLE,
    REASON_COUNT_MISMATCH,
    REASON_FORBIDDEN_EXPRESSION,
    REASON_MISSING_PATTERN,
    REASON_NOT_ONE_LINE,
    REASON_NO_BASIS,
    REASON_TOO_LONG,
    REASON_UNKNOWN_BASIS,
    ClaudeBriefingComposer,
    FakeBriefingComposer,
    GeminiBriefingComposer,
    OpenAIBriefingComposer,
    build_briefing_prompt,
    composer_from_env,
    template_briefing,
    validate_briefing,
)
from app.briefing.types import BriefingInput, BriefingLine, ComposedBriefing, Suggestion
from app.er.types import JudgeUnavailable
from app.settings import BRIEFING_SUGGESTION_MAX_CHARS

#: P3-er F-46f1eb 규약과 같은 마커(secret-guard 오탐 방지, `tests/test_er_judge.py`
#: /`tests/test_memory_extract.py` 와 동일).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

NOW = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 헬퍼 (tests/test_briefing_inputs.py 와 같은 dict 모양 관례)
# ---------------------------------------------------------------------------


def _fact(
    key: str,
    value: str,
    *,
    fact_id: int = 1,
    eligible: bool = True,
    sources: list[dict] | None = None,
) -> dict:
    return {
        "key": key,
        "fact_id": fact_id,
        "value": value,
        "confidence": 1.0,
        "updated_at": NOW.isoformat(),
        "eligible": eligible,
        "sources": sources if sources is not None else [],
    }


def _event(event_id: int, *, type_: str = "meal", content: str = "내용") -> dict:
    return {
        "id": event_id,
        "person_id": 1,
        "type": type_,
        "content": content,
        "occurred_at": NOW.isoformat(),
        "created_at": NOW.isoformat(),
    }


def _briefing_input(
    *,
    used_facts: list[dict] | None = None,
    excluded_facts: list[dict] | None = None,
    recent_events: list[dict] | None = None,
    schedule_id: int = 1,
) -> BriefingInput:
    return BriefingInput(
        schedule_id=schedule_id,
        person_id=1,
        scheduled_at=NOW,
        title="저녁 약속",
        pattern_trace_id=None,
        used_facts=used_facts or [],
        excluded_facts=excluded_facts or [],
        recent_events=recent_events or [],
    )


def _basis(fact_keys: list[str] | None = None, event_ids: list[int] | None = None) -> dict:
    return {"fact_keys": fact_keys or [], "event_ids": event_ids or []}


# ---------------------------------------------------------------------------
# BRIEFING_SCHEMA 구조
# ---------------------------------------------------------------------------


def test_briefing_schema_top_level_keys():
    assert BRIEFING_SCHEMA["required"] == ["pattern_sentences", "lines", "suggestion"]
    assert BRIEFING_SCHEMA["additionalProperties"] is False


def test_briefing_schema_line_and_suggestion_share_basis_shape():
    line_basis = BRIEFING_SCHEMA["properties"]["lines"]["items"]["properties"]["basis"]
    suggestion_basis = BRIEFING_SCHEMA["properties"]["suggestion"]["properties"]["basis"]
    assert line_basis == suggestion_basis
    assert line_basis["required"] == ["fact_keys", "event_ids"]


def test_briefing_schema_suggestion_is_nullable():
    assert "null" in BRIEFING_SCHEMA["properties"]["suggestion"]["type"]


# ---------------------------------------------------------------------------
# 판정 표 20행 -- 프롬프트 경계 문구
# ---------------------------------------------------------------------------


def test_build_briefing_prompt_includes_boundary_sentence_and_no_relation_request():
    briefing_input = _briefing_input(
        used_facts=[_fact("pattern:conflict", "3회 (2026-03-02, 2026-06-11, 2026-09-20)")],
        recent_events=[_event(10)],
    )

    system, user_text = build_briefing_prompt(briefing_input)

    assert "기록된 사실에서 도출되는 한 줄 행동 제안으로 한정, 감정·고민에 대한 대화는 하지 않는다." in system
    # 인물 간 관계를 묻거나 조언을 요청하는 문구가 없어야 한다(원칙7).
    assert "관계는 언급하지 마라" in system
    assert "민수" not in system  # 다른 인물 이름을 넣지 않는다(이 테스트는 이름 자체를 넘기지 않음)
    assert BRIEFING_TOOL_NAME in system
    assert "민수와" not in user_text


# ---------------------------------------------------------------------------
# 정상 경로 -- 모든 항목 통과
# ---------------------------------------------------------------------------


def test_validate_briefing_happy_path_keeps_everything():
    briefing_input = _briefing_input(
        used_facts=[
            _fact("hobby", "등산", sources=[{"event_id": 10, "raw_utterance": "등산 좋아함", "occurred_at": NOW.isoformat()}]),
        ],
        recent_events=[_event(20, type_="meal", content="저녁 식사")],
    )
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[
            BriefingLine(text="등산을 좋아합니다.", basis=_basis(fact_keys=["hobby"])),
            BriefingLine(text="최근 저녁 식사를 함께 했습니다.", basis=_basis(event_ids=[20])),
        ],
        suggestion=Suggestion(text="등산 코스가 있는 식당을 예약하세요.", basis=_basis(fact_keys=["hobby"])),
        tokens_in=11,
        tokens_out=22,
        provider="fake",
        model="fake-model",
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert rejected == []
    assert len(composed.lines) == 2
    assert composed.suggestion is not None
    assert composed.suggestion.text == "등산 코스가 있는 식당을 예약하세요."
    assert composed.tokens_in == 11
    assert composed.tokens_out == 22
    assert composed.provider == "fake"
    assert composed.model == "fake-model"


# ---------------------------------------------------------------------------
# 판정 표 14행 -- 근거 없는 제안
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_suggestion_without_basis():
    briefing_input = _briefing_input(used_facts=[_fact("hobby", "등산")])
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[BriefingLine(text="등산을 좋아합니다.", basis=_basis(fact_keys=["hobby"]))],
        suggestion=Suggestion(text="등산을 같이 가보세요.", basis=_basis()),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert len(composed.lines) == 1  # 나머지 줄은 유지
    assert {"item": {"kind": "suggestion", "text": "등산을 같이 가보세요.", "basis": _basis()}, "reason": REASON_NO_BASIS} in rejected


# ---------------------------------------------------------------------------
# 판정 표 15행 -- 감정·고민 표현
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_suggestion_with_forbidden_expression():
    briefing_input = _briefing_input(used_facts=[_fact("hobby", "등산")])
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(
            text="민수의 기분을 먼저 위로해 주세요.", basis=_basis(fact_keys=["hobby"])
        ),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_FORBIDDEN_EXPRESSION


def test_validate_briefing_rejects_line_with_forbidden_expression_keeps_others():
    """U4 실 LLM 확인(03-log U4, 사용자 결정 2026-10-02) -- 요약 줄 "부친상을
    겪으셔서 힘들어 보입니다" 가 통과했다. 금지 표현 검사를 요약 줄에도 걸어
    그 줄만 버리고, "힘들어" 처럼 "힘드" 로는 안 잡히던 활용형도 잡는다."""

    briefing_input = _briefing_input(
        used_facts=[_fact("life_event", "최근 부친상")],
        recent_events=[_event(30, type_="praise", content="보고서 칭찬")],
    )
    bad_text = "팀장님이 최근 부친상을 겪으셔서 힘들어 보입니다."
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[
            BriefingLine(text=bad_text, basis=_basis(fact_keys=["life_event"])),
            BriefingLine(text="최근 보고서를 칭찬받았습니다.", basis=_basis(event_ids=[30])),
        ],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert [line.text for line in composed.lines] == ["최근 보고서를 칭찬받았습니다."]
    assert {"item": {"kind": "line", "text": bad_text}, "reason": REASON_FORBIDDEN_EXPRESSION} in rejected


def test_validate_briefing_rejects_suggestion_about_their_feelings():
    """U4 실 LLM 재확인에서 통과했던 제안 그대로 -- "마음을"·"배려" 로
    걸러진다. "마음에 드는" 같은 정상 문장은 막지 않는다(조사까지 붙여 좁게)."""

    briefing_input = _briefing_input(recent_events=[_event(30, type_="praise", content="보고서 칭찬")])
    feeling = "면담 전 팀장님의 마음을 이해하고 배려하는 대화를 준비하세요."
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text=feeling, basis=_basis(event_ids=[30])),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_FORBIDDEN_EXPRESSION

    ok = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text="팀장님 마음에 드는 조용한 식당을 고르세요.", basis=_basis(event_ids=[30])),
    )
    composed_ok, rejected_ok = validate_briefing(briefing_input, ok)
    assert composed_ok.suggestion is not None
    assert rejected_ok == []


def test_validate_briefing_rejects_suggestion_with_conjugated_himdeul():
    """"힘드" 만으로는 놓치던 "힘들 거예요" 활용형을 제안에서도 잡는다."""

    briefing_input = _briefing_input(used_facts=[_fact("hobby", "등산")])
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text="요즘 많이 힘들 거예요, 등산을 권해 보세요.", basis=_basis(fact_keys=["hobby"])),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_FORBIDDEN_EXPRESSION


# ---------------------------------------------------------------------------
# 판정 표 16행 -- 한 줄 위반(줄바꿈 / 상한 초과)
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_multiline_suggestion():
    briefing_input = _briefing_input(used_facts=[_fact("hobby", "등산")])
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text="등산을\n같이 가보세요.", basis=_basis(fact_keys=["hobby"])),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_NOT_ONE_LINE


def test_validate_briefing_rejects_suggestion_over_max_chars():
    briefing_input = _briefing_input(used_facts=[_fact("hobby", "등산")])
    long_text = "등" * (BRIEFING_SUGGESTION_MAX_CHARS + 1)
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text=long_text, basis=_basis(fact_keys=["hobby"])),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_TOO_LONG


# ---------------------------------------------------------------------------
# 판정 표 17행 -- 근거 위조(입력에 없는 이벤트 id·사실 키)
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_only_the_line_with_fabricated_basis():
    briefing_input = _briefing_input(
        used_facts=[_fact("hobby", "등산")], recent_events=[_event(20)]
    )
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[
            BriefingLine(text="등산을 좋아합니다.", basis=_basis(fact_keys=["hobby"])),
            BriefingLine(text="지어낸 줄입니다.", basis=_basis(fact_keys=["없는키"])),
            BriefingLine(text="지어낸 이벤트입니다.", basis=_basis(event_ids=[999])),
        ],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert [line.text for line in composed.lines] == ["등산을 좋아합니다."]
    reasons = {item["reason"] for item in rejected}
    assert reasons == {REASON_UNKNOWN_BASIS}
    assert len(rejected) == 2


# ---------------------------------------------------------------------------
# 판정 표 18행 -- 근거 자격(결정 G)
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_suggestion_basis_not_eligible():
    briefing_input = _briefing_input(used_facts=[_fact("job", "백엔드 개발자", eligible=False)])
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(text="이직 축하 인사를 건네세요.", basis=_basis(fact_keys=["job"])),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.suggestion is None
    assert rejected[0]["reason"] == REASON_BASIS_NOT_ELIGIBLE


def test_validate_briefing_accepts_suggestion_basis_backed_by_event_even_if_fact_not_eligible():
    briefing_input = _briefing_input(
        used_facts=[_fact("job", "백엔드 개발자", eligible=False)],
        recent_events=[_event(30, content="이직 소식을 들었다")],
    )
    raw = ComposedBriefing(
        pattern_sentences=[],
        lines=[],
        suggestion=Suggestion(
            text="이직 축하 인사를 건네세요.", basis=_basis(fact_keys=["job"], event_ids=[30])
        ),
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert rejected == []
    assert composed.suggestion is not None


# ---------------------------------------------------------------------------
# 판정 표 19행 -- 패턴 판정은 규칙(원칙6), 숫자 불일치 -> 템플릿 대체
# ---------------------------------------------------------------------------


def test_validate_briefing_replaces_pattern_sentence_with_template_on_count_mismatch():
    rule_value = "3회 (2026-03-02, 2026-06-11, 2026-09-20)"
    briefing_input = _briefing_input(used_facts=[_fact("pattern:conflict", rule_value)])
    raw = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": "민수와 다섯 번 다퉜어요."}],
        lines=[],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.pattern_sentences == [{"key": "pattern:conflict", "sentence": rule_value}]
    assert {"item": {"kind": "pattern", "key": "pattern:conflict", "sentence": "민수와 다섯 번 다퉜어요."}, "reason": REASON_COUNT_MISMATCH} in rejected


def test_validate_briefing_accepts_pattern_sentence_with_matching_native_korean_number():
    rule_value = "3회 (2026-03-02, 2026-06-11, 2026-09-20)"
    briefing_input = _briefing_input(used_facts=[_fact("pattern:conflict", rule_value)])
    raw = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": "민수와 올해 세 번 다퉜어요."}],
        lines=[],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert rejected == []
    assert composed.pattern_sentences == [{"key": "pattern:conflict", "sentence": "민수와 올해 세 번 다퉜어요."}]


# ---------------------------------------------------------------------------
# R-4 보강 1 -- 입력 pattern:* 집합 밖의 키를 지어낼 때
# ---------------------------------------------------------------------------


def test_validate_briefing_rejects_fabricated_pattern_key():
    rule_value = "3회 (2026-03-02, 2026-06-11, 2026-09-20)"
    briefing_input = _briefing_input(used_facts=[_fact("pattern:conflict", rule_value)])
    raw = ComposedBriefing(
        pattern_sentences=[
            {"key": "pattern:conflict", "sentence": "민수와 올해 세 번 다퉜어요."},
            {"key": "pattern:gossip", "sentence": "지어낸 패턴입니다."},
        ],
        lines=[],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert [item["key"] for item in composed.pattern_sentences] == ["pattern:conflict"]
    fabricated = [item for item in rejected if item["item"].get("key") == "pattern:gossip"]
    assert len(fabricated) == 1
    assert fabricated[0]["reason"] == REASON_UNKNOWN_BASIS


def test_validate_briefing_rejects_pattern_sentence_with_unhashable_key():
    """FIX-021 mypy 좁히기 회귀 -- `key` 가 str 이 아니면(여기서는 해시
    불가능한 list) `in` 연산으로 TypeError 가 나던 경로를, 던지지 않고
    거부 목록으로 보내는지 확인한다(모듈 docstring "예외를 던지지 않는다").
    `_parse_composed` 를 거치지 않고 `ComposedBriefing` 을 직접 만들어
    이 가드를 우회 없이 직접 때린다."""

    rule_value = "3회 (2026-03-02, 2026-06-11, 2026-09-20)"
    briefing_input = _briefing_input(used_facts=[_fact("pattern:conflict", rule_value)])
    raw = ComposedBriefing(
        pattern_sentences=[{"key": ["해시", "불가능"], "sentence": "망가진 입력"}],
        lines=[],
        suggestion=None,
    )

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.pattern_sentences == [{"key": "pattern:conflict", "sentence": rule_value}]
    broken = [item for item in rejected if item["item"].get("key") == ["해시", "불가능"]]
    assert len(broken) == 1
    assert broken[0]["reason"] == REASON_UNKNOWN_BASIS


# ---------------------------------------------------------------------------
# R-4 보강 2 -- 입력 패턴을 생성기가 빠뜨리면 템플릿 문장으로 채움
# ---------------------------------------------------------------------------


def test_validate_briefing_fills_missing_pattern_with_template_sentence():
    rule_value = "4회 (2026-01-01, 2026-02-01, 2026-03-01, 2026-04-01)"
    briefing_input = _briefing_input(used_facts=[_fact("pattern:meal", rule_value)])
    raw = ComposedBriefing(pattern_sentences=[], lines=[], suggestion=None)

    composed, rejected = validate_briefing(briefing_input, raw)

    assert composed.pattern_sentences == [{"key": "pattern:meal", "sentence": rule_value}]
    assert {"item": {"kind": "pattern", "key": "pattern:meal"}, "reason": REASON_MISSING_PATTERN} in rejected


# ---------------------------------------------------------------------------
# template_briefing -- LLM 0, 제안 없음, 패턴은 규칙 value 그대로
# ---------------------------------------------------------------------------


def test_template_briefing_has_no_suggestion_and_literal_pattern_value():
    rule_value = "3회 (2026-03-02, 2026-06-11, 2026-09-20)"
    briefing_input = _briefing_input(
        used_facts=[
            _fact("pattern:conflict", rule_value),
            _fact("hobby", "등산"),
        ],
        recent_events=[_event(20, type_="meal", content="저녁 식사")],
    )

    composed = template_briefing(briefing_input)

    assert composed.suggestion is None
    assert composed.pattern_sentences == [{"key": "pattern:conflict", "sentence": rule_value}]
    assert composed.tokens_in == 0 and composed.tokens_out == 0
    assert composed.provider == "template"
    line_texts = [line.text for line in composed.lines]
    assert any("hobby" in text for text in line_texts)
    assert any("저녁 식사" in text for text in line_texts)


# ---------------------------------------------------------------------------
# FakeBriefingComposer -- 결정성·호출 횟수·실패 주입
# ---------------------------------------------------------------------------


def test_fake_briefing_composer_is_deterministic_and_counts_calls():
    table = {
        1: {
            "pattern_sentences": [],
            "lines": [{"text": "등산을 좋아합니다.", "basis": _basis(fact_keys=["hobby"])}],
            "suggestion": None,
        }
    }
    composer = FakeBriefingComposer(table=table)
    briefing_input = _briefing_input(schedule_id=1, used_facts=[_fact("hobby", "등산")])

    first = composer.compose(briefing_input)
    second = composer.compose(briefing_input)

    assert first == second
    assert composer.call_count == 2


def test_fake_briefing_composer_returns_empty_briefing_for_unknown_schedule():
    composer = FakeBriefingComposer(table={})
    briefing_input = _briefing_input(schedule_id=999)

    result = composer.compose(briefing_input)

    assert result.pattern_sentences == []
    assert result.lines == []
    assert result.suggestion is None


def test_fake_briefing_composer_raises_judge_unavailable_when_fail_set():
    composer = FakeBriefingComposer(fail="timeout")
    briefing_input = _briefing_input()

    with pytest.raises(JudgeUnavailable):
        composer.compose(briefing_input)
    assert composer.call_count == 1


# ---------------------------------------------------------------------------
# 스텁 클라이언트 (네트워크 없음, tests/test_memory_extract.py 와 같은 패턴)
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


_SAMPLE_BRIEFING_OUTPUT = {
    "pattern_sentences": [],
    "lines": [{"text": "등산을 좋아합니다.", "basis": {"fact_keys": ["hobby"], "event_ids": []}}],
    "suggestion": None,
}


def _claude_briefing_response(output, *, tokens=(12, 34), model="claude-sonnet-5"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=BRIEFING_TOOL_NAME, input=output)],
        usage=SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]),
        model=model,
        stop_reason="tool_use",
    )


def _openai_briefing_response(output, *, model="gpt-4o-mini"):
    function = SimpleNamespace(name=BRIEFING_TOOL_NAME, arguments=json.dumps(output))
    tool_call = SimpleNamespace(function=function)
    message = SimpleNamespace(tool_calls=[tool_call])
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        model=model,
    )


def _gemini_briefing_response(output, *, model="gemini-test-model"):
    return SimpleNamespace(
        text=json.dumps(output),
        usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=1),
        model_version=model,
    )


_BRIEFING_INPUT_FOR_PROVIDERS = _briefing_input(used_facts=[_fact("hobby", "등산")])


# ---------------------------------------------------------------------------
# ClaudeBriefingComposer
# ---------------------------------------------------------------------------


def test_claude_composer_request_body_forces_tool_choice_and_schema(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = StubClaudeClient(_claude_briefing_response(_SAMPLE_BRIEFING_OUTPUT))
    composer = ClaudeBriefingComposer(client=client)

    composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)

    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["tool_choice"] == {"type": "tool", "name": BRIEFING_TOOL_NAME}
    assert kwargs["tools"] == [
        {
            "name": BRIEFING_TOOL_NAME,
            "description": kwargs["tools"][0]["description"],
            "input_schema": BRIEFING_SCHEMA,
        }
    ]
    body_str = json.dumps(kwargs, default=str, ensure_ascii=False)
    assert "ANTHROPIC" not in body_str
    assert "api_key" not in body_str.lower()


def test_claude_composer_parses_tool_use_into_composed_briefing_with_usage():
    client = StubClaudeClient(_claude_briefing_response(_SAMPLE_BRIEFING_OUTPUT, tokens=(5, 7)))
    composer = ClaudeBriefingComposer(client=client)

    result = composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)

    assert len(result.lines) == 1
    assert result.lines[0].text == "등산을 좋아합니다."
    assert result.tokens_in == 5
    assert result.tokens_out == 7
    assert result.provider == "anthropic"


def test_claude_composer_no_tool_use_block_is_schema_error():
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="모르겠다")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        model="claude-sonnet-5",
        stop_reason="end_turn",
    )
    composer = ClaudeBriefingComposer(client=StubClaudeClient(response))

    with pytest.raises(JudgeUnavailable):
        composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)


# ---------------------------------------------------------------------------
# OpenAIBriefingComposer
# ---------------------------------------------------------------------------


def test_openai_composer_parses_tool_call_into_composed_briefing():
    client = StubOpenAIClient(_openai_briefing_response(_SAMPLE_BRIEFING_OUTPUT))
    composer = OpenAIBriefingComposer(client=client)

    result = composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)

    assert len(result.lines) == 1
    assert result.provider == "openai"
    assert result.tokens_in == 1 and result.tokens_out == 1


def test_openai_composer_no_tool_calls_is_schema_error():
    message = SimpleNamespace(tool_calls=None)
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice], usage=None, model="gpt-4o-mini")
    composer = OpenAIBriefingComposer(client=StubOpenAIClient(response))

    with pytest.raises(JudgeUnavailable):
        composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)


# ---------------------------------------------------------------------------
# GeminiBriefingComposer
# ---------------------------------------------------------------------------


def test_gemini_composer_requires_gemini_model_env(monkeypatch):
    from app.tools.types import InvalidValue

    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    with pytest.raises(InvalidValue):
        GeminiBriefingComposer(client=StubGeminiClient(response=_gemini_briefing_response(_SAMPLE_BRIEFING_OUTPUT)))


def test_gemini_composer_parses_json_text_into_composed_briefing():
    client = StubGeminiClient(_gemini_briefing_response(_SAMPLE_BRIEFING_OUTPUT))
    composer = GeminiBriefingComposer(model="gemini-test-model", client=client)

    result = composer.compose(_BRIEFING_INPUT_FOR_PROVIDERS)

    assert len(result.lines) == 1
    assert result.provider == "gemini"
    assert result.tokens_in == 1 and result.tokens_out == 1


# ---------------------------------------------------------------------------
# 등록표·select_provider 재사용(D11)
# ---------------------------------------------------------------------------


def test_briefing_composers_registry_has_three_providers():
    assert set(BRIEFING_COMPOSERS) == {"anthropic", "openai", "gemini"}


@pytest.mark.parametrize(
    "provider, key_name, composer_cls, extra_env",
    [
        ("anthropic", "ANTHROPIC_API_KEY", ClaudeBriefingComposer, {}),
        ("openai", "OPENAI_API_KEY", OpenAIBriefingComposer, {}),
        ("gemini", "GEMINI_API_KEY", GeminiBriefingComposer, {"GEMINI_MODEL": "gemini-test-model"}),
    ],
)
def test_composer_from_env_builds_each_active_provider(
    monkeypatch, provider, key_name, composer_cls, extra_env
):
    monkeypatch.setenv(key_name, _FAKE_KEY_MARKER)
    for env_name, env_value in extra_env.items():
        monkeypatch.setenv(env_name, env_value)
    composer = composer_from_env(env={"LLM_PROVIDER": provider})
    assert isinstance(composer, composer_cls)


def test_composer_from_env_defaults_to_openai(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    composer = composer_from_env(env={})
    assert isinstance(composer, OpenAIBriefingComposer)


def test_composer_from_env_unknown_provider_rejected():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue):
        composer_from_env(env={"LLM_PROVIDER": "llama"})


def test_composer_from_env_rejects_disabled_provider():
    from app.tools.types import InvalidValue

    with pytest.raises(InvalidValue) as excinfo:
        composer_from_env(env={"LLM_PROVIDER": "gemini", "LLM_PROVIDERS_ENABLED": "anthropic"})
    assert "anthropic" in str(excinfo.value)
