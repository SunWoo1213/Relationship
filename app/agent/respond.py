"""Refs: P5-loop S3.2 S3.4 원칙7 원칙9 -- U5 응답 단계(결정 B(i) 템플릿).

## 이 모듈이 하는 일과 하지 않는 일

`build_reply()` 는 그 턴에 실제로 기록된 것(이벤트·일정 수)과 실패·상한
초과 여부, 되묻기가 있다면 그 질문 문장만 **정해진 한국어 문장 틀**에
끼워 하나의 문자열을 만든다. 감정·고민이 담긴 발화가 들어와도 이 함수가
보는 것은 "몇 건을 기억했는가"라는 숫자뿐이므로, 공감·조언·위로 문장을
만들어낼 자리가 코드 안에 아예 없다(원칙7 경계 "감정·고민에 대한 대화는
하지 않는다" -- 구조적으로 보장한다, 결정 B(i) 확정 근거 ①). LLM 을 다시
부르지 않는다(호출은 인식 단계 1회로 유지, 원칙8 재현성) -- 이 모듈은
어떤 네트워크 호출도, DB 접근도 하지 않는 순수 함수다.

## 템플릿이 다루는 신호

- `stored_events`/`stored_schedules`: 그 턴에 실제로 `add_event`/
  `add_schedule` 이 성공한 건수(기록 단계, U5 `loop.py`).
- `failed_count`: 게이트를 통과했지만 실행 중 `ToolError` 로 끝난 제안 수
  (R-24, `loop_record.output.failed`).
- `limit_hit`: 게이트 상한 초과로 일부 제안이 버려졌는가(결정 A(i)).
- `pending_question`: 그 턴이 되묻기로 끝났다면 그 질문(`identity`/
  `new_person`/`schedule` 공통, `app.tools.types.PendingQuestionOut`) --
  질문 문구만 그대로 붙이고 이 모듈이 다시 쓰지 않는다(질문 문구의 단일
  출처는 ER `_build_ask_payload`/U5 `_ask_schedule` 이다).
"""

from __future__ import annotations

from app.tools.types import PendingQuestionOut

#: 아무것도 기억하지 못한 턴(제안이 없거나 전부 거부됨)의 기본 문장.
_NOTHING_STORED = "이번 발화에서는 새로 기억한 것이 없어요."


def build_reply(
    *,
    stored_events: int,
    stored_schedules: int,
    failed_count: int = 0,
    limit_hit: bool = False,
    pending_question: PendingQuestionOut | None = None,
) -> str:
    """그 턴의 결과를 결정적 한국어 문장 하나로 조립한다(결정 B(i)).

    숫자·불리언·`PendingQuestionOut.question` 문자열만 입력으로 받는다 --
    발화 원문·이벤트 `content`·감정 표현은 이 함수에 들어오지 않으므로
    반영될 수도 없다(원칙7 부정 테스트가 확인하는 지점)."""

    parts: list[str] = []
    if stored_events:
        parts.append(f"이벤트 {stored_events}건")
    if stored_schedules:
        parts.append(f"일정 {stored_schedules}건")

    if parts:
        sentence = "기억했어요: " + ", ".join(parts) + "."
    else:
        sentence = _NOTHING_STORED

    if failed_count:
        sentence += f" ({failed_count}건은 저장하지 못했어요.)"
    if limit_hit:
        sentence += " 한 번에 너무 많아 일부만 기억했어요."

    if pending_question is not None:
        sentence += "\n" + pending_question.question

    return sentence
