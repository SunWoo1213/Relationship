"""Refs: P7-push S3.6 원칙7 -- U3 판정: `build_push_payload`(01-plan 판정
표 10·11·13행 "본문 규칙"·"제안 없음"·"길이·TTL" + R-10 "시각은
`user_timezone()` 변환" + 순수성).

DB 를 쓰지 않는다(`schedule` 은 `id`/`title`/`scheduled_at` 속성만 있는
`types.SimpleNamespace` 로 직접 만든다 -- `tests/test_briefing_compose.py`
와 같은 관례). `pywebpush` 를 import 하지 않는다(01-plan "지킬 불변식").
네트워크 호출 없음. 시간은 전부 테스트가 고정해 주입한다(실제 시계를
읽지 않는다).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.briefing.types import BriefingLine, ComposedBriefing, Suggestion
from app.push.payload import build_push_payload
from app.settings import PUSH_BODY_MAX_CHARS, PUSH_TTL_MAX_SECONDS

#: 모든 테스트가 재사용하는 고정 "지금"(요구사항 "시간은 고정값 주입").
_T = datetime(2026, 10, 3, 1, 0, 0, tzinfo=timezone.utc)

#: 요약 줄·패턴 문장 감시 문자열(판정 10행 "어디에도 없음"). 요약 줄에
#: 원문이 글자 그대로 옮겨진 §6-3 관찰을 흉내낸 문구를 쓴다.
_WATCHED_LINE_TEXT = "민수는 고수를 진짜 싫어하더라 요약줄감시문자열"
_WATCHED_PATTERN_SENTENCE = "패턴문장감시문자열: 지난 1년간 갈등이 3회 있었어요"


def _schedule(*, id: int = 1, title: str = "저녁 약속", scheduled_at: datetime) -> SimpleNamespace:
    return SimpleNamespace(id=id, title=title, scheduled_at=scheduled_at)


def _composed_with_suggestion(text: str = "고수 없는 식당을 고르세요") -> ComposedBriefing:
    """요약 줄 2 · 패턴 문장 1 을 담아 "읽히지 않아야 한다"를 실제로
    시험할 수 있게 한다(판정 10행 전제)."""
    return ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": _WATCHED_PATTERN_SENTENCE}],
        lines=[
            BriefingLine(text=_WATCHED_LINE_TEXT, basis={"fact_keys": ["dislikes"], "event_ids": []}),
            BriefingLine(text="요약줄감시문자열 둘째 줄", basis={"fact_keys": [], "event_ids": [1]}),
        ],
        suggestion=Suggestion(text=text, basis={"fact_keys": [], "event_ids": [1]}),
    )


def _payload_strings(payload: dict) -> str:
    """결과 전체를 JSON 문자열로 -- 감시 문자열이 **어디에도** 없음을
    검사할 때 키별로 따로 보지 않고 한 번에 본다(판정 20행과 같은 방식)."""
    return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 판정 10행 -- 본문 규칙(결정 B): 제안 포함, 요약 줄·패턴 문장 미포함
# ---------------------------------------------------------------------------


def test_build_push_payload_includes_time_and_suggestion_only(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)  # 기본값 Asia/Seoul
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion("고수 없는 식당을 고르세요")

    payload = build_push_payload(schedule, "민수", composed, _T)

    assert payload["title"] == "민수 · 저녁 약속"
    # Asia/Seoul = UTC+9 -> 19:00 UTC == 04:00(다음날) KST
    assert payload["body"] == "10/04 04:00 · 제안: 고수 없는 식당을 고르세요"
    assert payload["tag"] == "schedule-1"
    assert payload["schedule_id"] == 1


def test_build_push_payload_never_contains_lines_or_pattern_sentences(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion()

    payload = build_push_payload(schedule, "민수", composed, _T)

    dumped = _payload_strings(payload)
    assert _WATCHED_LINE_TEXT not in dumped
    assert "요약줄감시문자열" not in dumped
    assert _WATCHED_PATTERN_SENTENCE not in dumped
    assert "패턴문장감시문자열" not in dumped


# ---------------------------------------------------------------------------
# 판정 11행 -- 제안 없음
# ---------------------------------------------------------------------------


def test_build_push_payload_without_suggestion_uses_fallback_tail(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": _WATCHED_PATTERN_SENTENCE}],
        lines=[BriefingLine(text=_WATCHED_LINE_TEXT, basis={})],
        suggestion=None,
    )

    payload = build_push_payload(schedule, "민수", composed, _T)

    assert payload["body"] == "10/04 04:00 · 브리핑이 준비됐어요"
    dumped = _payload_strings(payload)
    assert _WATCHED_LINE_TEXT not in dumped
    assert _WATCHED_PATTERN_SENTENCE not in dumped


# ---------------------------------------------------------------------------
# 판정 13행 -- 길이·TTL
# ---------------------------------------------------------------------------


def test_build_push_payload_body_within_limit_for_realistic_suggestion(monkeypatch):
    """제안 80자(`BRIEFING_SUGGESTION_MAX_CHARS`, 검증기를 통과할 수 있는
    실제 상한) + 긴 일정 제목 -- 본문은 title 을 포함하지 않으므로 긴
    제목이 본문 길이에 영향을 주지 않는다는 것과, 80자 제안이 실제로
    "거의 안 잘리는 선"이라는 설계 근거(`app/settings.py` "PUSH_*" 절)를
    함께 확인한다."""
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    long_title = "아주 긴 일정 제목 " * 10
    suggestion_text = "가" * 80
    schedule = _schedule(
        title=long_title, scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc)
    )
    composed = _composed_with_suggestion(suggestion_text)

    payload = build_push_payload(schedule, "민수", composed, _T)

    assert len(payload["body"]) <= PUSH_BODY_MAX_CHARS
    assert payload["body"].endswith(suggestion_text)  # 안 잘렸다
    assert payload["title"] == f"민수 · {long_title}"


def test_build_push_payload_truncates_body_when_exceeding_limit(monkeypatch):
    """설계가 깨졌을 때의 방어선 -- 검증기 상한(80자)을 넘는 비정상적으로
    긴 제안이 들어와도 본문은 `PUSH_BODY_MAX_CHARS` 를 넘지 않고, 말줄임표로
    잘렸음을 알 수 있다(모듈 docstring "자르는 방식")."""
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion("가" * 300)

    payload = build_push_payload(schedule, "민수", composed, _T)

    assert len(payload["body"]) == PUSH_BODY_MAX_CHARS
    assert payload["body"].endswith("…")


@pytest.mark.parametrize(
    "delta, expected_ttl",
    [
        (timedelta(seconds=30), 60),
        (timedelta(hours=3), 10800),
        (timedelta(hours=30), PUSH_TTL_MAX_SECONDS),
    ],
    ids=["t+30s-clamped-to-60", "t+3h-exact", "t+30h-clamped-to-max"],
)
def test_build_push_payload_ttl_clamped_to_range(delta, expected_ttl):
    now = _T
    schedule = _schedule(scheduled_at=now + delta)
    composed = _composed_with_suggestion()

    payload = build_push_payload(schedule, "민수", composed, now)

    assert payload["ttl"] == expected_ttl


# ---------------------------------------------------------------------------
# R-10 -- 시각은 user_timezone() 변환(UTC 가 아닌 APP_TIMEZONE 케이스)
# ---------------------------------------------------------------------------


def test_build_push_payload_time_uses_app_timezone_not_utc(monkeypatch):
    """`APP_TIMEZONE` 을 기본값(Asia/Seoul)과 다른 시간대로 바꿔도
    `build_push_payload` 가 실제로 그 시간대로 변환한 시각을 쓰는지
    확인한다(02-plan-verify R-10) -- UTC 를 그대로 찍으면 이 단언이
    깨진다."""
    monkeypatch.setenv("APP_TIMEZONE", "America/New_York")
    # 2026-10-03 19:00 UTC -> America/New_York 은 그 시점 EDT(UTC-4) ->
    # 2026-10-03 15:00.
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion("제안 문구")

    payload = build_push_payload(schedule, "민수", composed, _T)

    assert payload["body"].startswith("10/03 15:00")


def test_build_push_payload_time_differs_between_timezones(monkeypatch):
    """같은 일정이라도 `APP_TIMEZONE` 이 다르면 본문 시각 표기가 달라진다
    -- 시간대 변환이 실제로 일어난다는 것 자체를 단언한다(UTC 고정이면
    두 값이 같아져 이 테스트가 실패한다)."""
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion("제안 문구")

    monkeypatch.setenv("APP_TIMEZONE", "Asia/Seoul")
    seoul_payload = build_push_payload(schedule, "민수", composed, _T)

    monkeypatch.setenv("APP_TIMEZONE", "America/New_York")
    ny_payload = build_push_payload(schedule, "민수", composed, _T)

    assert seoul_payload["body"] != ny_payload["body"]


# ---------------------------------------------------------------------------
# 순수성 -- 같은 입력 같은 출력, LLM·DB 호출 없음(함수 자체가 import 하지
# 않으므로 호출 자체가 불가능하다는 것은 모듈 docstring·U3 산출물 요건으로
# 보장되고, 여기서는 결정적(deterministic) 동작만 확인한다)
# ---------------------------------------------------------------------------


def test_build_push_payload_is_pure_same_input_same_output(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion()

    first = build_push_payload(schedule, "민수", composed, _T)
    second = build_push_payload(schedule, "민수", composed, _T)

    assert first == second


def test_build_push_payload_does_not_mutate_composed(monkeypatch):
    """입력 `composed`(불변 dataclass)·`schedule` 을 바꾸지 않는다 --
    순수 함수라는 docstring 주장을 실제로 단언한다."""
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    schedule = _schedule(scheduled_at=datetime(2026, 10, 3, 19, 0, 0, tzinfo=timezone.utc))
    composed = _composed_with_suggestion()
    before = composed.to_dict()

    build_push_payload(schedule, "민수", composed, _T)

    assert composed.to_dict() == before
