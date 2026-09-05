"""Refs: P2-tools S3.2 -- 툴 반환 DTO·예외 계층.

이 모듈의 dataclass 는 LLM/함수 경계(툴이 돌려주는 값)에 있는 타입이며,
HTTP 요청/응답 스키마(`app/api/schemas.py`, U8)와는 별개다(01-plan 결정 11
-- 섞지 않는다). `Candidate` 는 S3.2 15행 정의 그대로다.

각 `*Out` 은 `to_dict()` 를 제공한다 -- JSON 직렬화 가능한 값(str/int/float/
bool/None/list/dict)만 담는다. `app/tools/context.py` 의 `to_jsonable()` 이
`@traced` 의 output 을 만들 때 `to_dict()` 가 있으면 그것을 우선 쓴다.

예외 계층은 전부 `ToolError` 아래에 둔다. 메시지는 비밀·원문(raw_utterance,
접속 정보)을 담지 않는 짧은 코드성 문자열이어야 한다 -- `@traced` 가 예외
시 `str(e)` 를 그대로 `agent_traces.output.message` 에 저장하기 때문이다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PersonOut:
    id: int
    display_name: str
    relation_tag: str
    hierarchy: str
    aliases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "relation_tag": self.relation_tag,
            "hierarchy": self.hierarchy,
            "aliases": list(self.aliases),
        }


@dataclass(frozen=True)
class Candidate:
    """S3.2: 3단계 LLM 판정의 입력. person 은 배제되지 않은 신호만 담는다
    (01-plan 결정 3 -- `search_person` 은 배제하지 않고 신호만 모은다)."""

    person: PersonOut
    similarity: float
    aliases_matched: list[str] = field(default_factory=list)
    rule_flags: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "person": self.person.to_dict(),
            "similarity": self.similarity,
            "aliases_matched": list(self.aliases_matched),
            "rule_flags": dict(self.rule_flags),
        }


@dataclass(frozen=True)
class EventOut:
    id: int
    person_id: int
    type: str
    content: str
    occurred_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "person_id": self.person_id,
            "type": self.type,
            "content": self.content,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class ScheduleOut:
    id: int
    person_id: int
    title: str
    scheduled_at: datetime
    briefed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "person_id": self.person_id,
            "title": self.title,
            "scheduled_at": self.scheduled_at.isoformat(),
            "briefed_at": self.briefed_at.isoformat() if self.briefed_at else None,
        }


@dataclass(frozen=True)
class PendingQuestionOut:
    question_id: int
    status: str
    kind: str
    question: str
    options: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "status": self.status,
            "kind": self.kind,
            "question": self.question,
            "options": list(self.options),
        }


@dataclass(frozen=True)
class BriefingOut:
    """골격만 -- U7 이 person_facts·recent_events·upcoming_schedules 세부
    구성(결정 7: person/aliases/facts[]/recent_events[N=5]/
    upcoming_schedules[3]/schedule?/generated_at)을 채운다. 문장화·"한 줄
    행동 제안"은 이 DTO 에 없다(P6-briefing 몫, 원칙7)."""

    person: PersonOut
    facts: list[dict[str, Any]] = field(default_factory=list)
    recent_events: list[EventOut] = field(default_factory=list)
    upcoming_schedules: list[ScheduleOut] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "person": self.person.to_dict(),
            "facts": [dict(f) for f in self.facts],
            "recent_events": [e.to_dict() for e in self.recent_events],
            "upcoming_schedules": [s.to_dict() for s in self.upcoming_schedules],
        }


class ToolError(Exception):
    """툴 계층 예외의 공통 베이스. `@traced` 가 `type(e).__name__`·`str(e)`
    를 그대로 trace 에 남기므로, 서브클래스는 짧은 코드성 메시지만 담는다."""


class PersonNotFound(ToolError):
    """`person_id` 가 없거나 다른 `user_id` 소유(security.md §5 격리)."""


class QuestionNotFound(ToolError):
    """`question_id` 가 `pending_questions` 에 없다."""


class QuestionNotAnswerable(ToolError):
    """이미 답했거나(already_answered) 24h 만료된(expired) 질문에 대한 답변
    시도. `reason` 문자열을 메시지에 담되 옵션 문자열 자체는 넣지 않는다."""


class ConfirmationRequired(ToolError):
    """D1/D6 -- answered `new_person`/`identity` 질문 없이 `create_person`
    또는 `update_person(display_name=...)` 를 호출."""


class InvalidValue(ToolError):
    """값 집합(EVENT_TYPES/RELATION_TAGS/HIERARCHIES/QUESTION_KINDS/
    ALIAS_SOURCES) 위반, naive datetime, 저장된 `options` 밖의 답 등."""
