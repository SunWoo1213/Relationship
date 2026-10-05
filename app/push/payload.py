"""Refs: P7-push S3.6 원칙7 -- U3 푸시 본문 작성기(`build_push_payload`).

## 이 모듈이 하지 않는 것

- 발송(`app/push/sender.py`)·알림기(`app/push/notifier.py`)·구독 저장
  (`app/push/subscriptions.py`)을 담지 않는다 -- 이 모듈은 발송·DB·LLM
  과 무관한 **순수 함수** 하나뿐이다(01-plan "산출물" 절 -- "LLM·DB
  import 없음"). 결정 D 가 고른 VAPID 발송 라이브러리를 import 하지
  않는다 -- 그 이름이 `app/` 안에 나타나는 유일한 자리는 U4
  `app/push/sender.py` 다(01-plan 결정 G "지킬 불변식" -- `app/push/
  types.py`·`__init__.py` 와 같은 이유로 이 모듈도 그 이름 문자열을
  의도적으로 쓰지 않는다).
- `schedule` 인자의 타입을 `app.db.models.Schedule` 로 좁히지 않는다 --
  `app/briefing/types.py::Notifier.notify()` 와 같은 이유로 `Any` 로
  적는다(이 모듈에서 실제로 읽는 속성은 `id`/`title`/`scheduled_at`
  셋뿐이다). `display_name` 을 별도 인자로 받으므로 인물(`Person`)
  조회도 하지 않는다 -- 호출자(U4 `WebPushNotifier`)가 이미 조회해
  넘긴다.
- **`composed.lines`·`composed.pattern_sentences` 를 읽지 않는다**
  (01-plan 결정 B "원문 노출 차단" -- P6-briefing 실서버 확인에서 요약
  줄이 사용자 원문을 글자 그대로 옮긴 사례가 반복 관찰됐다, §6-3 인계).
  이 함수가 읽는 `ComposedBriefing` 필드는 `suggestion` 하나뿐이고,
  그 `suggestion.text` 는 P6-briefing 검증기(`validate_briefing`)를
  이미 통과한 문장이다(근거 필수·한 줄·`BRIEFING_SUGGESTION_MAX_CHARS`
  =80자·금지 표현 14개, R19) -- 다만 검증기가 원문 인용 자체를 걸러내지
  는 않으므로(01-plan 결정 B 한계), 원문이 완전히 섞이지 않는다고
  보장하지는 않는다.

## 이 모듈이 고정하는 것

- `build_push_payload(schedule, display_name, composed, now)` --
  반환 `{title, body, tag, schedule_id, ttl}`(01-plan 산출물 절 시그니처
  그대로).
  - `title = "{display_name} · {schedule.title}"`.
  - `body` -- 제안이 있으면
    `"{시각(user_timezone, MM/DD HH:MM)} · 제안: {suggestion.text}"`,
    없으면 `"{시각} · 브리핑이 준비됐어요"`(01-plan 결정 B(ii)). 시각은
    `schedule.scheduled_at` 을 `app.settings.user_timezone()`(FIX-005,
    기본 `Asia/Seoul`)으로 변환한 값이다 -- "지금"(`now`)이 아니라
    **그 일정의 시각**이다(예시: "민수 · 저녁 약속 / 10/03 19:00 · 제안:
    …", 01-plan 목표 절).
  - **자르는 방식**(판정 표 13행 "본문 ≤ `PUSH_BODY_MAX_CHARS`") --
    글자 수가 `app.settings.PUSH_BODY_MAX_CHARS` 를 넘으면 앞에서부터
    `PUSH_BODY_MAX_CHARS - 1` 글자만 남기고 말줄임표(`"…"`) 한 글자를
    덧붙인다. 그래서 잘린 본문의 길이는 **항상** `PUSH_BODY_MAX_CHARS`
    와 같다(그 이하가 아니라 정확히 같다 -- 말줄임표가 "여기서 잘렸다"
    는 신호를 알림 센터에 남긴다). 실제 운용에서는 검증기를 통과한
    제안이 최대 80자이고 `PUSH_BODY_MAX_CHARS=120` 이 그 제안이 "거의
    안 잘리는 선"으로 골랐으므로(`app/settings.py` "PUSH_*" 절), 이
    경로는 설계가 깨졌을 때의 방어선이지 정상 경로가 아니다.
  - `tag = "schedule-{schedule.id}"`(같은 일정 알림은 덮어쓴다, 01-plan
    산출물 절).
  - `ttl` -- `schedule.scheduled_at - now` 를 초로 환산해(`int()`,
    0 방향 절사) `[60, app.settings.PUSH_TTL_MAX_SECONDS]` 범위로 자른
    정수다. 일정이 이미 지났거나 60초 미만으로 임박해도 최소 60초를
    보장한다(웹푸시 `ttl` 헤더가 0이면 일부 푸시 서비스가 즉시 폐기할
    수 있다는 상식적 여유 -- 01-plan 이 구체 하한을 정하지 않아 U3 가
    `PUSH_TIMEOUT_SECONDS` 와 겹치지 않는 값으로 60을 그대로 썼다).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.briefing.types import ComposedBriefing
from app.settings import PUSH_BODY_MAX_CHARS, PUSH_TTL_MAX_SECONDS, user_timezone

#: 제안이 없을 때의 본문 꼬리(01-plan 결정 B(ii) 그대로).
_NO_SUGGESTION_TAIL = "브리핑이 준비됐어요"


def build_push_payload(
    schedule: Any, display_name: str, composed: ComposedBriefing, now: datetime
) -> dict[str, Any]:
    """일정 하나의 웹푸시 페이로드를 만든다(결정 B(ii), 모듈 docstring).

    `schedule` 은 `id`/`title`/`scheduled_at` 속성만 읽는다(실제로는
    `app.db.models.Schedule` 이지만 이 모듈은 DB 를 import 하지 않으므로
    `Any`). `composed` 에서 읽는 필드는 `suggestion` 뿐이다 --
    `composed.lines`·`composed.pattern_sentences` 는 절대 읽지 않는다."""

    local_time = schedule.scheduled_at.astimezone(user_timezone())
    time_str = local_time.strftime("%m/%d %H:%M")

    title = f"{display_name} · {schedule.title}"

    if composed.suggestion is not None:
        body = f"{time_str} · 제안: {composed.suggestion.text}"
    else:
        body = f"{time_str} · {_NO_SUGGESTION_TAIL}"

    if len(body) > PUSH_BODY_MAX_CHARS:
        body = body[: PUSH_BODY_MAX_CHARS - 1] + "…"

    ttl_seconds = int((schedule.scheduled_at - now).total_seconds())
    ttl = max(60, min(ttl_seconds, PUSH_TTL_MAX_SECONDS))

    return {
        "title": title,
        "body": body,
        "tag": f"schedule-{schedule.id}",
        "schedule_id": schedule.id,
        "ttl": ttl,
    }
