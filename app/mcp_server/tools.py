"""Refs: P9b-auth U12 CR-008 D19 결정 4 -- MCP 도구 본체 4개(SDK import 0, 순수 함수).

계약은 01-plan "도구 계약 — 개정 4" 그대로다. 조회는 **`app.api.read` 의 세 함수만** 부른다(새 SQL 0,
LLM·임베딩 호출 0, 쓰기 0). 결과는 JSON 객체 하나(`model_dump(mode="json")`). 결과 어디에도
`raw_utterance`·닉네임·토큰·대기 질문·대화 기록·`agent_traces` 가 없다(D19 지킬 것 6) -- 읽는 모델
(`PersonListItemOut`·`PersonCardOut`·`BriefingRecordOut`)에 그 필드가 없고, 브리핑은 `trace_id` 키를
추가로 뺀다(`agent_traces` 를 내보내지 않는다).

상한 상수는 **호출 시점에 `app.settings` 모듈 속성을 읽는다**(시험이 `monkeypatch` 로 줄인다).

예외 클래스 `PersonNotFound`·`ScheduleNotFound` 는 `app.api.read` 의 속성으로 받는다 -- 원래
`app.tools.types` 에 있지만 MCP 모듈은 `app.tools` 를 import 하지 않는다는 규칙(D19 지킬 것 5)을
지키려고 읽는 모듈이 이미 들고 있는 같은 클래스 객체를 쓴다.
"""

from __future__ import annotations

import unicodedata
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app import settings
from app.api import read


class McpToolError(Exception):
    """도구 오류 코드(`invalid_name`·`not_found`·`internal_error`). 메시지 = 코드 -- 이 값만
    MCP 오류 결과의 텍스트가 된다(예외 원문·SQL·스택 0)."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def name_key(s: str) -> str:
    """이름 규칙(결정 AV): NFC -> 대소문자 접기 -> **모든 공백 제거**.

    `박 과장`·`박과장님` 처럼 직함 표기 흔들림을 한 규칙으로 덮는다."""
    return "".join(unicodedata.normalize("NFC", s).casefold().split())


def tool_list_people(session: Session, user_id: str) -> dict[str, Any]:
    persons = read.list_persons(session, user_id)
    limit = settings.MCP_LIST_PEOPLE_LIMIT
    total = len(persons)
    return {
        "people": [p.model_dump(mode="json") for p in persons[:limit]],
        "total": total,
        "truncated": total > limit,
    }


def tool_find_person(session: Session, user_id: str, name: str) -> dict[str, Any]:
    if len(name.strip()) > settings.MCP_FIND_NAME_MAX_LEN:
        raise McpToolError("invalid_name")
    key = name_key(name)
    if key == "":
        raise McpToolError("invalid_name")
    # 일치하는 인물을 전부 -- 하나로 고르지 않는다(원칙1 의 읽기 쪽 비대칭).
    matched = [
        p
        for p in read.list_persons(session, user_id)
        if key in name_key(p.display_name) or any(key in name_key(a) for a in p.aliases)
    ]
    limit = settings.MCP_FIND_PERSON_LIMIT
    total = len(matched)
    return {
        "matches": [p.model_dump(mode="json") for p in matched[:limit]],
        "total": total,
        "truncated": total > limit,
    }


def tool_get_person_card(
    session: Session, user_id: str, person_id: int, now: datetime
) -> dict[str, Any]:
    try:
        card = read.get_person_card(session, user_id, person_id, now)
    except read.PersonNotFound:  # 없음·남의 것 -- 같은 결과
        raise McpToolError("not_found") from None
    return card.model_dump(mode="json")


def tool_list_briefings(
    session: Session, user_id: str, now: datetime, schedule_id: int | None
) -> dict[str, Any]:
    try:
        records = read.list_briefings(session, user_id, now, schedule_id)
    except read.ScheduleNotFound:  # 없음·남의 것 -- 같은 결과
        raise McpToolError("not_found") from None
    # `trace_id` 는 `agent_traces` 행 id 다 -- 내보내지 않는다(D19 결정 4, R5-7).
    return {
        "briefings": [
            {k: v for k, v in r.model_dump(mode="json").items() if k != "trace_id"}
            for r in records
        ]
    }
