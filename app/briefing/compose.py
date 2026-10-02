"""Refs: P6-briefing S3.6 R19 D11 원칙6 원칙7 원칙8 -- U4 문장 생성기·검증기.
`BriefingComposer` Protocol·구조화 출력 스키마(`BRIEFING_SCHEMA`)·
`build_briefing_prompt()`·`validate_briefing()`·공급자 구현(`app/er/judge.py`
의 `select_provider`·`call_with_error_mapping` 재사용, D11)·
`FakeBriefingComposer`·`template_briefing()` 을 정의한다. 실행 함수(U5,
`app/briefing/run.py`)가 이 모듈을 호출해 생성기 오류 시 템플릿으로
대체하고 `agent_traces` 에 남긴다 -- 그 오케스트레이션은 이 모듈의 몫이
아니다(01-plan 75행, U5 "생성기 오류면 결정 D 대로 템플릿 대체").

## 이 모듈이 하지 않는 것

- 생성기 호출 실패 시 템플릿 대체 여부를 **스스로 결정하지 않는다** --
  `compose()` 가 실패하면 `JudgeUnavailable` 을 그대로 올리고, 성공하면
  `validate_briefing()` 으로 거를 뿐이다. "실패 시 템플릿으로" 전환은
  U5 `run_briefings()` 가 `try/except JudgeUnavailable` 로 한다.
- DB 접근·`briefed_at` 기록·`agent_traces` 쓰기를 하지 않는다(U5 몫,
  01-plan "지킬 불변식"과 이 패키지 위임 범위).
- `app.briefing.select`/`app.briefing.inputs`/`app.briefing.run` 을
  import 하지 않는다 -- 역방향 의존을 만들지 않는다.

## 구조 파싱 vs 의미 검증 (두 층, `app/memory/extract.py` 와 같은 경계)

- **구조 파싱**(`_parse_composed`/`_parse_line_item`, 이 모듈 비공개) --
  공급자 구현이 받은 raw dict 를 `ComposedBriefing` 으로 바꾸는 자리다.
  타입만 본다(`pattern_sentences`/`lines`/`suggestion` 이 정해진 모양인가).
  깨지면 `JudgeUnavailable("schema")`(새 오류 클래스를 만들지 않는다,
  D11·01-plan 139행) -- `app/memory/extract.py::_parse_extraction` 과
  같은 층위.
- **의미 검증**(`validate_briefing`, 공개) -- 이미 구조가 맞는
  `ComposedBriefing` 을 `BriefingInput` 과 대조해 **항목 단위로**
  통과/거부를 가른다(01-plan 74행). 거부해도 예외를 던지지 않고
  `rejected:[{item, reason}]` 로 모아 돌려준다. 나머지 항목은 그대로
  유지한다(원칙7 "제안이 버려져도 나머지 줄은 유지").

## 검증기 거부 사유 7종 + R-4 보강

| 사유 코드 | 대상 | 조건 |
|-----------|------|------|
| `no_basis` | 줄·제안 | `basis.fact_keys`·`basis.event_ids` 둘 다 빈 목록 |
| `unknown_basis` | 줄·제안·패턴 | 입력(`BriefingInput`)에 없는 사실 키/이벤트 id. 패턴 문장에서는 R-4 "입력 `pattern:*` 집합 밖의 키"를 이 사유로 재사용한다 |
| `basis_not_eligible` | 제안만 | 제안 근거가 `eligible=False` 인 사실 키뿐이고 이벤트 id 근거도 없음(아래 "근거 자격 판단" 절) |
| `not_one_line` | 제안만 | 줄바꿈 포함 |
| `too_long` | 제안만 | `BRIEFING_SUGGESTION_MAX_CHARS` 초과 |
| `forbidden_expression` | 줄·제안 | `BRIEFING_FORBIDDEN_EXPRESSIONS` 부분 문자열 포함. 요약 줄은 그 줄만 버린다(사용자 결정 2026-10-02 — 실 LLM 확인에서 "부친상을 겪으셔서 힘들어 보입니다" 줄이 통과했다, 03-log U4) |
| `count_mismatch` | 패턴만 | 생성기 문장에서 뽑은 숫자 집합에 규칙 `value` 의 `n` 이 없음 -> 그 패턴만 템플릿 문장(`value` 그대로)으로 대체 |

패턴 사실 중 생성기가 아예 빠뜨린 키는(R-4 "입력 패턴을 생성기가
빠뜨리면 템플릿 문장으로 채운다") `missing_pattern` 사유로 기록하고
템플릿 문장으로 채운다 -- 거부라기보다 보강이지만, 근거 추적을 위해
`rejected[]` 에 함께 남긴다(원칙9).

## 근거 자격 판단(결정 G, U3 03-log 인계 — 이 단위가 정한 것)

제안의 근거가 **이벤트 id** 하나라도 포함하면(입력에 실제로 있는 id,
`unknown_basis` 검사를 이미 통과한 뒤) 그 자체로 자격이 있다고 본다 --
이벤트는 `fact_sources` 를 거치지 않고도 그 자체가 원문(또는 `content`)을
가진 원자료이기 때문이다(`events` 테이블, 01-plan "지킬 불변식" 원문
불변). 반대로 근거가 **사실 키뿐**이면, 그 키들이 전부
`BriefingInput.used_facts[].eligible == False`(연결된 `fact_sources` 원문이
없음, 결정 G)일 때만 `basis_not_eligible` 로 거부한다 -- 하나라도
`eligible` 사실이 섞여 있으면 통과시킨다(제안 전체를 버리기보다, 실제로
위험한 "출처 없는 사실만으로 낸 제안"만 막는 것이 목표다).

## 패턴 숫자 비교 방식(이 단위가 정한 것)

규칙 `value` 는 `app/memory/patterns.py::detect_patterns` 가 만드는
`"{n}회 (YYYY-MM-DD, ...)"` 형식이다(C-3). 맨 앞 숫자+"회" 에서 `n` 을 뽑고,
생성기 문장에서는 **아라비아 숫자**(`3회`/`3번`)와 **고유어 수사**
(`한``두``세``네``다섯``여섯``일곱``여덟``아홉``열` + `번`/`회`, 01-plan
판정 19행 예시 "다섯 번")를 모두 찾아 정수 집합으로 만든다. `n` 이 그
집합 안에 있으면 통과, 집합이 비어 있거나(숫자를 전혀 언급하지 않음)
`n` 이 없으면 `count_mismatch` 다 -- 혼동을 피하기 위해 "숫자를 아예
안 쓴 문장"도 안전한 쪽(템플릿 대체)으로 처리한다(원칙1과 같은
비대칭: 틀린 숫자를 사용자에게 보여주는 것이 템플릿으로 대체하는 것보다
훨씬 나쁘다).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from app.briefing.types import (
    BRIEFING_FORBIDDEN_EXPRESSIONS,
    BriefingInput,
    BriefingLine,
    ComposedBriefing,
    Suggestion,
)
from app.er.judge import (
    _to_gemini_schema,
    call_with_error_mapping,
    call_with_gemini_error_mapping,
    select_provider,
)
from app.er.types import JudgeUnavailable
from app.settings import BRIEFING_SUGGESTION_MAX_CHARS, ER_JUDGE_MAX_RETRIES, ER_JUDGE_TIMEOUT, PATTERN_KEY_PREFIX

# ---------------------------------------------------------------------------
# BriefingComposer Protocol
# ---------------------------------------------------------------------------


class BriefingComposer(Protocol):
    """실행 함수(U5)가 부르는 인터페이스. 입력은 `BriefingInput`(그 한
    일정·한 인물의 재료, U3) 하나뿐이다 -- 원칙7 "그 한 인물"."""

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing: ...


# ---------------------------------------------------------------------------
# 구조화 출력 스키마 (결정 D 권장 구조)
# ---------------------------------------------------------------------------

BRIEFING_TOOL_NAME = "report_briefing"

_BRIEFING_TOOL_DESCRIPTION = (
    "다가오는 만남 직전에 보여줄 브리핑을 쓴다. 패턴 문장·요약 줄·한 줄 "
    "행동 제안(없으면 null)을 모두 입력에 있는 사실 키·이벤트 id 를 "
    "근거로 달아 답한다."
)

#: `{fact_keys:[...], event_ids:[...]}` -- 줄·제안 공통 근거 모양.
_BASIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "fact_keys": {"type": "array", "items": {"type": "string"}},
        "event_ids": {"type": "array", "items": {"type": "integer"}},
    },
    "required": ["fact_keys", "event_ids"],
    "additionalProperties": False,
}

_PATTERN_SENTENCE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "sentence": {"type": "string"},
    },
    "required": ["key", "sentence"],
    "additionalProperties": False,
}

_LINE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "basis": _BASIS_SCHEMA,
    },
    "required": ["text", "basis"],
    "additionalProperties": False,
}

#: 제안은 없을 수 있다(null) -- `_LINE_SCHEMA` 와 같은 모양 + null 허용.
_SUGGESTION_SCHEMA: dict[str, Any] = {
    "type": ["object", "null"],
    "properties": {
        "text": {"type": "string"},
        "basis": _BASIS_SCHEMA,
    },
    "required": ["text", "basis"],
    "additionalProperties": False,
}

#: 구조화 출력 스키마 단일 출처(결정 D) -- `{pattern_sentences, lines,
#: suggestion}`. 어느 공급자든 이 딕셔너리 그대로를 도구/함수 스키마의
#: `input_schema`/`parameters`(또는 Gemini `response_schema`)로 쓴다.
BRIEFING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "pattern_sentences": {"type": "array", "items": _PATTERN_SENTENCE_SCHEMA},
        "lines": {"type": "array", "items": _LINE_SCHEMA},
        "suggestion": _SUGGESTION_SCHEMA,
    },
    "required": ["pattern_sentences", "lines", "suggestion"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# 프롬프트 조립
# ---------------------------------------------------------------------------

#: S3.6 경계 문장 원문(01-plan U4 인용 그대로) -- 프롬프트에 그대로
#: 넣는다(판정 표 20행이 이 문자열 포함을 확인한다).
_BOUNDARY_SENTENCE = (
    "기록된 사실에서 도출되는 한 줄 행동 제안으로 한정, 감정·고민에 대한 "
    "대화는 하지 않는다."
)


def build_briefing_prompt(briefing_input: BriefingInput) -> tuple[str, str]:
    """`(system, user_text)` 를 만든다. 이 인물 한 명의 패턴·사실·최근
    사건만 넣는다(원칙7) -- 다른 인물 정보·환경변수·키는 넣지 않는다
    (security §1). 사실마다 연결 원문(결정 G)을 함께 실어 "사실과 원문이
    어긋나 보이면 그 사실을 제안 근거로 쓰지 말라"고 지시한다."""

    pattern_facts = [
        fact for fact in briefing_input.used_facts if fact["key"].startswith(PATTERN_KEY_PREFIX)
    ]
    other_facts = [
        fact
        for fact in briefing_input.used_facts
        if not fact["key"].startswith(PATTERN_KEY_PREFIX)
    ]

    pattern_lines = [f'- key={fact["key"]} value="{fact["value"]}"' for fact in pattern_facts]

    fact_lines = []
    for fact in other_facts:
        sources = fact.get("sources") or []
        if sources:
            sources_text = "; ".join(
                f'id={source["event_id"]} raw="{source["raw_utterance"]}"' for source in sources
            )
        else:
            sources_text = "(연결된 원문 없음 -- 제안 근거로 쓸 수 없다)"
        fact_lines.append(f'- key={fact["key"]} value="{fact["value"]}" 원문: {sources_text}')

    event_lines = [
        (
            f'- id={event["id"]} type={event["type"]} '
            f'occurred_at={event["occurred_at"]} content="{event["content"]}"'
        )
        for event in briefing_input.recent_events
    ]

    system = (
        "너는 다가오는 만남 직전에 보여줄 한국어 브리핑을 쓰는 보조 도구다. "
        "기록된 사실·패턴·최근 사건만 근거로 쓰고, 추측이나 새로운 사실을 "
        f"만들지 마라. {_BOUNDARY_SENTENCE} 제안은 반드시 한 줄이고 "
        "상담·위로·감정 표현을 쓰지 않는다. 요약 줄(lines)과 제안"
        "(suggestion)에는 반드시 근거(basis.fact_keys 또는 "
        "basis.event_ids)를 달고, 그 값은 아래 목록에 있는 키·id 만 "
        "써라(지어내지 마라). 사실마다 연결된 원문이 함께 제시되면, 사실과 "
        "원문의 뜻이 어긋나 보일 때 그 사실을 제안 근거로 쓰지 마라. "
        "패턴 사실(key 가 'pattern:' 으로 시작)의 횟수·날짜는 입력에 적힌 "
        "값을 그대로 옮기고 숫자를 바꾸거나 반올림하지 마라. 이 인물 한 "
        "사람에 관한 내용만 쓰고 다른 인물과의 관계는 언급하지 마라. "
        f"{BRIEFING_TOOL_NAME} 도구로만 답하라."
    )

    user_text = (
        f'인물 ID: {briefing_input.person_id}\n'
        f'다가오는 일정: "{briefing_input.title}" '
        f"({briefing_input.scheduled_at.isoformat()})\n\n"
        "패턴 사실:\n"
        + ("\n".join(pattern_lines) if pattern_lines else "(없음)")
        + "\n\n그 밖의 사실:\n"
        + ("\n".join(fact_lines) if fact_lines else "(없음)")
        + "\n\n최근 사건:\n"
        + ("\n".join(event_lines) if event_lines else "(없음)")
        + "\n\n위 자료만으로 패턴 문장·요약 줄·한 줄 제안(근거가 부족하면 "
        f"null)을 {BRIEFING_TOOL_NAME} 로 답하라."
    )
    return system, user_text


# ---------------------------------------------------------------------------
# 구조 파싱 (모듈 docstring "구조 파싱 vs 의미 검증" 절)
# ---------------------------------------------------------------------------


def _parse_line_item(item: Any) -> BriefingLine:
    """`{text, basis:{fact_keys, event_ids}}` 모양 하나를 `BriefingLine`
    으로. `Suggestion` 도 같은 모양이라 이 함수를 그대로 재사용한다."""

    if not isinstance(item, dict):
        raise JudgeUnavailable("schema")

    text = item.get("text")
    basis = item.get("basis")

    if not isinstance(text, str) or not text:
        raise JudgeUnavailable("schema")
    if not isinstance(basis, dict):
        raise JudgeUnavailable("schema")

    fact_keys = basis.get("fact_keys")
    event_ids = basis.get("event_ids")

    if not isinstance(fact_keys, list) or not all(isinstance(key, str) for key in fact_keys):
        raise JudgeUnavailable("schema")
    if not isinstance(event_ids, list):
        raise JudgeUnavailable("schema")

    ids: list[int] = []
    for raw_id in event_ids:
        # bool 은 int 의 서브클래스이므로 먼저 배제한다(FIX-007 과 같은
        # 관례, `app/memory/extract.py::_parse_extraction` 참고).
        if isinstance(raw_id, bool) or not isinstance(raw_id, int):
            raise JudgeUnavailable("schema")
        ids.append(raw_id)

    return BriefingLine(text=text, basis={"fact_keys": list(fact_keys), "event_ids": ids})


def _parse_composed(
    raw: dict[str, Any],
    *,
    tokens_in: int = 0,
    tokens_out: int = 0,
    provider: str | None = None,
    model: str | None = None,
) -> ComposedBriefing:
    """구조화 출력(이미 dict)을 **타입만** 검증해 `ComposedBriefing` 으로
    바꾼다. 실패하면 `JudgeUnavailable("schema")`(새 오류 클래스 없음,
    D11). 의미 검증(근거 존재·금지 표현 등)은 `validate_briefing()` 몫 --
    이 함수가 선점하면 안 된다."""

    if not isinstance(raw, dict):
        raise JudgeUnavailable("schema")

    pattern_sentences_raw = raw.get("pattern_sentences")
    lines_raw = raw.get("lines")
    suggestion_raw = raw.get("suggestion")

    if not isinstance(pattern_sentences_raw, list):
        raise JudgeUnavailable("schema")
    if not isinstance(lines_raw, list):
        raise JudgeUnavailable("schema")

    pattern_sentences: list[dict[str, Any]] = []
    for item in pattern_sentences_raw:
        if not isinstance(item, dict):
            raise JudgeUnavailable("schema")
        key = item.get("key")
        sentence = item.get("sentence")
        if not isinstance(key, str) or not key:
            raise JudgeUnavailable("schema")
        if not isinstance(sentence, str):
            raise JudgeUnavailable("schema")
        pattern_sentences.append({"key": key, "sentence": sentence})

    lines = [_parse_line_item(item) for item in lines_raw]

    suggestion: Suggestion | None = None
    if suggestion_raw is not None:
        parsed = _parse_line_item(suggestion_raw)
        suggestion = Suggestion(text=parsed.text, basis=parsed.basis)

    return ComposedBriefing(
        pattern_sentences=pattern_sentences,
        lines=lines,
        suggestion=suggestion,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        provider=provider,
        model=model,
    )


# ---------------------------------------------------------------------------
# 패턴 숫자 비교 (모듈 docstring "패턴 숫자 비교 방식" 절)
# ---------------------------------------------------------------------------

#: 고유어 수사 -> 정수. 길이가 긴 것부터 매칭해야 "한"/"두" 같은 짧은
#: 어절이 다른 단어 속 음절을 잘못 집지 않는다(정렬은 아래 정규식 조립
#: 시점에 한다).
_NATIVE_KOREAN_NUMBERS: dict[str, int] = {
    "아홉": 9,
    "여덟": 8,
    "일곱": 7,
    "여섯": 6,
    "다섯": 5,
    "네": 4,
    "세": 3,
    "두": 2,
    "한": 1,
    "열": 10,
}

_DIGIT_COUNT_RE = re.compile(r"(\d+)\s*(?:회|번)")
_NATIVE_COUNT_RE = re.compile(
    "(" + "|".join(sorted(_NATIVE_KOREAN_NUMBERS, key=len, reverse=True)) + r")\s*(?:회|번)"
)
_RULE_VALUE_COUNT_RE = re.compile(r"^(\d+)회")


def _extract_rule_count(value: str) -> int | None:
    """규칙 `value`(`"{n}회 (...)"`, `app/memory/patterns.py` C-3)에서
    `n` 을 뽑는다. 형식이 어긋나면 `None`(방어적 -- 실무상 발생하지
    않는다)."""

    match = _RULE_VALUE_COUNT_RE.match(value)
    return int(match.group(1)) if match else None


def _extract_mentioned_counts(sentence: str) -> set[int]:
    """생성기 문장에서 "N회"/"N번"(아라비아 숫자)과 고유어 수사 + "번"/"회"
    를 모두 찾아 정수 집합으로 돌려준다."""

    counts = {int(value) for value in _DIGIT_COUNT_RE.findall(sentence)}
    counts |= {_NATIVE_KOREAN_NUMBERS[word] for word in _NATIVE_COUNT_RE.findall(sentence)}
    return counts


def _template_pattern_sentence(value: str) -> str:
    """LLM 0 -- 패턴 문장은 규칙 `value` 그대로(결정 D "패턴은 규칙 value
    그대로"). `template_briefing()`과 `validate_briefing()`의 숫자 불일치
    대체가 공유한다."""

    return value


# ---------------------------------------------------------------------------
# 의미 검증 (공개, 항목 단위 거부 -- 01-plan 74행 + R-4)
# ---------------------------------------------------------------------------

REASON_NO_BASIS = "no_basis"
REASON_UNKNOWN_BASIS = "unknown_basis"
REASON_BASIS_NOT_ELIGIBLE = "basis_not_eligible"
REASON_NOT_ONE_LINE = "not_one_line"
REASON_TOO_LONG = "too_long"
REASON_FORBIDDEN_EXPRESSION = "forbidden_expression"
REASON_COUNT_MISMATCH = "count_mismatch"
#: 거부라기보다 보강 -- 입력에 있던 패턴을 생성기가 빠뜨려 템플릿으로
#: 채운 경우(R-4 두 번째 케이스). 근거 추적을 위해 `rejected[]` 에 함께
#: 남긴다(원칙9).
REASON_MISSING_PATTERN = "missing_pattern"


def _suggestion_basis_ids(fact_keys: list[str], event_ids: list[int]) -> tuple[list[str], list[int]]:
    return list(fact_keys), list(event_ids)


def validate_briefing(
    briefing_input: BriefingInput, raw: ComposedBriefing
) -> tuple[ComposedBriefing, list[dict[str, Any]]]:
    """`raw`(구조는 이미 `_parse_composed` 를 통과한 `ComposedBriefing`)를
    `briefing_input` 과 대조해 항목 단위로 통과/거부를 가른다. 하나가
    거부돼도 나머지는 그대로 유지한다(01-plan 74행, 원칙7) -- 이 함수는
    예외를 던지지 않는다. 반환한 `ComposedBriefing` 의 `tokens_in`/
    `tokens_out`/`provider`/`model` 은 `raw` 의 값을 그대로 옮긴다(검증은
    생성기 사용량을 바꾸지 않는다)."""

    used_facts_by_key = {fact["key"]: fact for fact in briefing_input.used_facts}
    eligible_fact_keys = {
        fact["key"] for fact in briefing_input.used_facts if fact.get("eligible")
    }
    known_fact_keys = set(used_facts_by_key)

    known_event_ids = {event["id"] for event in briefing_input.recent_events}
    for fact in briefing_input.used_facts:
        for source in fact.get("sources") or []:
            known_event_ids.add(source["event_id"])

    allowed_pattern_keys = [
        fact["key"] for fact in briefing_input.used_facts if fact["key"].startswith(PATTERN_KEY_PREFIX)
    ]
    allowed_pattern_key_set = set(allowed_pattern_keys)

    rejected: list[dict[str, Any]] = []

    # --- 패턴 문장 (R-4 포함) ---
    generated_by_key: dict[str, str] = {}
    for entry in raw.pattern_sentences:
        key = entry.get("key")
        sentence = entry.get("sentence", "")
        if key not in allowed_pattern_key_set:
            rejected.append(
                {"item": {"kind": "pattern", "key": key, "sentence": sentence}, "reason": REASON_UNKNOWN_BASIS}
            )
            continue
        generated_by_key[key] = sentence

    final_patterns: list[dict[str, Any]] = []
    for key in allowed_pattern_keys:
        value = used_facts_by_key[key]["value"]
        sentence = generated_by_key.get(key)

        if sentence is None:
            rejected.append({"item": {"kind": "pattern", "key": key}, "reason": REASON_MISSING_PATTERN})
            final_patterns.append({"key": key, "sentence": _template_pattern_sentence(value)})
            continue

        rule_n = _extract_rule_count(value)
        mentioned = _extract_mentioned_counts(sentence)
        if rule_n is not None and rule_n not in mentioned:
            rejected.append(
                {"item": {"kind": "pattern", "key": key, "sentence": sentence}, "reason": REASON_COUNT_MISMATCH}
            )
            final_patterns.append({"key": key, "sentence": _template_pattern_sentence(value)})
            continue

        final_patterns.append({"key": key, "sentence": sentence})

    # --- 요약 줄 ---
    final_lines: list[BriefingLine] = []
    for line in raw.lines:
        fact_keys, event_ids = _suggestion_basis_ids(
            line.basis.get("fact_keys", []), line.basis.get("event_ids", [])
        )

        if not fact_keys and not event_ids:
            rejected.append({"item": {"kind": "line", "text": line.text}, "reason": REASON_NO_BASIS})
            continue

        unknown_keys = [key for key in fact_keys if key not in known_fact_keys]
        unknown_events = [event_id for event_id in event_ids if event_id not in known_event_ids]
        if unknown_keys or unknown_events:
            rejected.append(
                {
                    "item": {
                        "kind": "line",
                        "text": line.text,
                        "unknown_fact_keys": unknown_keys,
                        "unknown_event_ids": unknown_events,
                    },
                    "reason": REASON_UNKNOWN_BASIS,
                }
            )
            continue

        if any(bad in line.text for bad in BRIEFING_FORBIDDEN_EXPRESSIONS):
            rejected.append(
                {"item": {"kind": "line", "text": line.text}, "reason": REASON_FORBIDDEN_EXPRESSION}
            )
            continue

        final_lines.append(line)

    # --- 제안 (원칙7 경계) ---
    final_suggestion: Suggestion | None = None
    if raw.suggestion is not None:
        suggestion = raw.suggestion
        fact_keys, event_ids = _suggestion_basis_ids(
            suggestion.basis.get("fact_keys", []), suggestion.basis.get("event_ids", [])
        )

        reason: str | None = None
        if not fact_keys and not event_ids:
            reason = REASON_NO_BASIS
        else:
            unknown_keys = [key for key in fact_keys if key not in known_fact_keys]
            unknown_events = [event_id for event_id in event_ids if event_id not in known_event_ids]
            if unknown_keys or unknown_events:
                reason = REASON_UNKNOWN_BASIS
            elif "\n" in suggestion.text or "\r" in suggestion.text:
                reason = REASON_NOT_ONE_LINE
            elif len(suggestion.text) > BRIEFING_SUGGESTION_MAX_CHARS:
                reason = REASON_TOO_LONG
            elif any(bad in suggestion.text for bad in BRIEFING_FORBIDDEN_EXPRESSIONS):
                reason = REASON_FORBIDDEN_EXPRESSION
            else:
                has_eligible_fact = any(key in eligible_fact_keys for key in fact_keys)
                has_event_basis = bool(event_ids)
                if not has_eligible_fact and not has_event_basis:
                    reason = REASON_BASIS_NOT_ELIGIBLE

        if reason is not None:
            rejected.append(
                {
                    "item": {"kind": "suggestion", "text": suggestion.text, "basis": dict(suggestion.basis)},
                    "reason": reason,
                }
            )
        else:
            final_suggestion = suggestion

    composed = ComposedBriefing(
        pattern_sentences=final_patterns,
        lines=final_lines,
        suggestion=final_suggestion,
        tokens_in=raw.tokens_in,
        tokens_out=raw.tokens_out,
        provider=raw.provider,
        model=raw.model,
    )
    return composed, rejected


# ---------------------------------------------------------------------------
# 템플릿 대체 생성기 (결정 D(i) -- LLM 0, 제안 없음)
# ---------------------------------------------------------------------------


def template_briefing(briefing_input: BriefingInput) -> ComposedBriefing:
    """LLM 을 전혀 쓰지 않는다. 패턴 문장은 규칙 `value` 그대로, 그 밖의
    사실·최근 사건은 단순 나열하며, **제안은 항상 `None`**(결정 D "제안
    없음")."""

    pattern_sentences = [
        {"key": fact["key"], "sentence": _template_pattern_sentence(fact["value"])}
        for fact in briefing_input.used_facts
        if fact["key"].startswith(PATTERN_KEY_PREFIX)
    ]

    lines: list[BriefingLine] = []
    for fact in briefing_input.used_facts:
        if fact["key"].startswith(PATTERN_KEY_PREFIX):
            continue
        lines.append(
            BriefingLine(
                text=f'{fact["key"]}: {fact["value"]}',
                basis={"fact_keys": [fact["key"]], "event_ids": []},
            )
        )
    for event in briefing_input.recent_events:
        lines.append(
            BriefingLine(
                text=f'{event["occurred_at"]} {event["type"]}: {event["content"]}',
                basis={"fact_keys": [], "event_ids": [event["id"]]},
            )
        )

    return ComposedBriefing(
        pattern_sentences=pattern_sentences,
        lines=lines,
        suggestion=None,
        tokens_in=0,
        tokens_out=0,
        provider="template",
        model=None,
    )


# ---------------------------------------------------------------------------
# 공급자 구현 (judge.py 의 등록표 개념·select_provider·오류 매핑 재사용, D11)
# ---------------------------------------------------------------------------


@dataclass
class ClaudeBriefingComposer:
    """Anthropic SDK 로 브리핑 문장을 생성한다. `app/memory/extract.py::
    ClaudeFactExtractor` 와 같은 관례(생성 시점에 `ANTHROPIC_MODEL` 을
    읽는다, 키는 SDK 가 환경변수에서 직접 읽는다, security §1). 타임아웃·
    재시도는 새 상수 없이 `ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES` 를
    그대로 쓴다."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        if self.client is None:
            import anthropic  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = anthropic.Anthropic(timeout=self.timeout, max_retries=self.max_retries)

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing:
        import anthropic  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_briefing_prompt(briefing_input)
        tool_schema = {
            "name": BRIEFING_TOOL_NAME,
            "description": _BRIEFING_TOOL_DESCRIPTION,
            "input_schema": BRIEFING_SCHEMA,
        }

        response = call_with_error_mapping(
            anthropic,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_text}],
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": BRIEFING_TOOL_NAME},
            ),
        )

        tool_use_input = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use":
                tool_use_input = block.input
                break

        if tool_use_input is None:
            raise JudgeUnavailable("schema")

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "input_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "output_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return _parse_composed(
            tool_use_input,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            provider="anthropic",
            model=model_used,
        )


@dataclass
class OpenAIBriefingComposer:
    """OpenAI SDK 로 브리핑 문장을 생성한다. `app/memory/extract.py::
    OpenAIFactExtractor` 와 같은 관례."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT
    max_retries: int = ER_JUDGE_MAX_RETRIES

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if self.client is None:
            import openai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.

            self.client = openai.OpenAI(timeout=self.timeout, max_retries=self.max_retries)

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing:
        import openai  # 예외 클래스·매핑용 지연 import.

        system, user_text = build_briefing_prompt(briefing_input)
        tool_schema = {
            "type": "function",
            "function": {
                "name": BRIEFING_TOOL_NAME,
                "description": _BRIEFING_TOOL_DESCRIPTION,
                "parameters": BRIEFING_SCHEMA,
            },
        }

        response = call_with_error_mapping(
            openai,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_text},
                ],
                tools=[tool_schema],
                tool_choice={"type": "function", "function": {"name": BRIEFING_TOOL_NAME}},
            ),
        )

        tool_calls = None
        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            tool_calls = getattr(message, "tool_calls", None) if message is not None else None

        if not tool_calls:
            raise JudgeUnavailable("schema")

        arguments_raw = tool_calls[0].function.arguments
        try:
            raw = json.loads(arguments_raw)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage is not None else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage is not None else 0
        model_used = getattr(response, "model", self.model)

        return _parse_composed(
            raw,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            provider="openai",
            model=model_used,
        )


@dataclass
class GeminiBriefingComposer:
    """`google-genai` SDK 로 브리핑 문장을 생성한다. `app/memory/extract.py::
    GeminiFactExtractor` 와 같은 관례(`GEMINI_MODEL` 기본값 없음) --
    재시도·오류 매핑은 `call_with_gemini_error_mapping()` 을 그대로
    재사용한다(두 번째 헬퍼를 만들지 않는다, D11)."""

    model: str | None = None
    client: Any = None
    timeout: float = ER_JUDGE_TIMEOUT

    def __post_init__(self) -> None:
        if self.model is None:
            model = os.environ.get("GEMINI_MODEL")
            if not model:
                from app.tools.types import InvalidValue

                raise InvalidValue(
                    "GeminiBriefingComposer: GEMINI_MODEL 환경변수가 필요하다(기본값 "
                    "없음 -- judge.py::GeminiJudge 와 같은 관례). Google AI "
                    "콘솔에서 확인한 모델 이름을 .env 의 GEMINI_MODEL 에 넣는다"
                )
            self.model = model
        if self.client is None:
            from google import genai  # 지연 import -- 키·SDK 없이도 app 임포트가 깨지지 않게.
            from google.genai import types as genai_types

            self.client = genai.Client(
                http_options=genai_types.HttpOptions(timeout=int(self.timeout * 1000))
            )

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing:
        from google.genai import types as genai_types  # 요청 조립용 지연 import.

        system, user_text = build_briefing_prompt(briefing_input)

        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            response_mime_type="application/json",
            response_schema=_to_gemini_schema(BRIEFING_SCHEMA),
        )

        response = call_with_gemini_error_mapping(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=user_text,
                config=config,
            )
        )

        text = getattr(response, "text", None)
        if not text:
            raise JudgeUnavailable("schema")

        try:
            raw = json.loads(text)
        except (TypeError, ValueError) as exc:
            raise JudgeUnavailable("schema") from exc

        usage = getattr(response, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage is not None else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage is not None else 0
        model_used = getattr(response, "model_version", None) or self.model

        return _parse_composed(
            raw,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            provider="gemini",
            model=model_used,
        )


#: 이름 -> 무인자 팩토리의 등록표(D11 정신 -- 이름 집합·선택 로직은
#: `judge.py::JUDGES`/`select_provider` 와 공유하지만 스키마가 달라 표
#: 자체는 새로 둔다. `app/memory/extract.py::FACT_EXTRACTORS` 와 같은
#: 예). `FakeBriefingComposer` 는 여기 없다(테스트 전용, `JUDGES`/
#: `FACT_EXTRACTORS` 가 각자의 Fake 를 빼는 것과 같은 이유). 이름을
#: `BRIEFING_COMPOSERS` 로 둔 것은 "자체 선택 로직을 새로 만들지 않았다"
#: 를 grep 으로 스스로 점검하기 위해서다(`FACT_EXTRACTORS` 와 같은 이유).
BRIEFING_COMPOSERS: dict[str, Callable[[], BriefingComposer]] = {
    "anthropic": ClaudeBriefingComposer,
    "openai": OpenAIBriefingComposer,
    "gemini": GeminiBriefingComposer,
}


def composer_from_env(env: dict[str, str] | None = None) -> BriefingComposer:
    """`select_provider(env)`(`judge.py` 재사용) ->
    `BRIEFING_COMPOSERS[name]()`. `extractor_from_env()`/`judge_from_env()`
    와 같은 2단계 패턴이다(D11). `env` 를 생략하면 `os.environ` 을 읽는다."""

    return BRIEFING_COMPOSERS[select_provider(env)]()


# ---------------------------------------------------------------------------
# FakeBriefingComposer -- 테스트용 결정적 BriefingComposer (원칙8, 네트워크 0)
# ---------------------------------------------------------------------------


@dataclass
class FakeBriefingComposer:
    """테스트용 결정적 `BriefingComposer`(원칙8 -- LLM 은 재현 불가능하므로
    자동 테스트에 넣지 않는다). `table` = `{schedule_id: {구조화 출력
    raw dict}}` -- `BriefingInput.schedule_id` 로 호출마다 미리 정한
    출력을 고른다(`BriefingInput` 은 일정 하나를 유일하게 가리키므로,
    `app/memory/extract.py::FakeFactExtractor` 가 이벤트 id 집합을 키로
    쓰는 것과 같은 정신으로 이 키를 골랐다 -- 이 단위가 정한 것). 표에
    없는 `schedule_id` 면 빈 브리핑(`pattern_sentences`/`lines` 빈 배열,
    `suggestion=None`)을 돌려준다.

    `fail` 이 주어지면 `JudgeUnavailable(error=fail)` 을 던진다(U5 가
    템플릿 대체·실패 격리를 테스트할 때 쓴다 -- `app/er/judge.py::FakeJudge`
    /`app/memory/extract.py::FakeFactExtractor` 와 같은 관례).

    `call_count` 로 호출 횟수를 센다(판정 표 2·9·24행과 같은 "호출
    0/1회" 검사용) -- 생성자 인자가 아니라 호출마다 내부에서 늘어난다.

    `_parse_composed()` 를 그대로 거쳐 만들어진다 -- 실제 공급자와 같은
    구조 파싱 경로를 타서 `FakeFactExtractor` 가 `_parse_extraction()` 을
    그대로 거치는 것과 같은 이유(호출자 테스트가 두 경로를 다르게
    취급하지 않는다)."""

    table: dict[int, dict[str, Any]] = field(default_factory=dict)
    fail: str | None = None
    call_count: int = field(default=0, init=False)

    def compose(self, briefing_input: BriefingInput) -> ComposedBriefing:
        self.call_count += 1

        if self.fail is not None:
            raise JudgeUnavailable(self.fail)

        raw = self.table.get(
            briefing_input.schedule_id,
            {"pattern_sentences": [], "lines": [], "suggestion": None},
        )
        return _parse_composed(dict(raw), provider="fake")
