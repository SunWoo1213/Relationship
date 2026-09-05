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

#: F-b97a06 -- "긍정 답 규약". `ask_user`(U6)가 `pending_questions.context`
#: (JSONB)에 이 키로 긍정 선택지 목록(`list[str]`)을 넣는다. D1/D6 확인 검사
#: (`app/tools/persons.py` 의 `_require_confirmation`)는 답(`answer`)이 이
#: 목록 안에 있을 때만 통과시킨다. 이 키가 `context` 에 없으면(구버전 질문,
#: 호출자 실수 등) **안전한 기본값으로 거부**한다 -- 원칙1(오병합은
#: 미검출보다 훨씬 나쁘다)과 같은 이유로, "긍정으로 판단할 근거가 없으면
#: 확인되지 않은 것으로 취급"한다. `app/tools/questions.py`(U6)도 같은 키를
#: 쓴다(단일 출처).
AFFIRMATIVE_KEY = "affirmative_options"


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
    """U5(`add_event`) 확장 -- `created_at` 추가(01-plan U5 산출물 목록).
    `raw_utterance` 는 여기 담지 않는다(원문 보존은 DB 컬럼·`fact_sources`
    근거 추적의 일이지, 툴 반환 DTO 의 일이 아니다 -- 01-plan 산출물 목록
    "id·person_id·type·content·occurred_at·created_at" 그대로)."""

    id: int
    person_id: int
    type: str
    content: str
    occurred_at: datetime
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "person_id": self.person_id,
            "type": self.type,
            "content": self.content,
            "occurred_at": self.occurred_at.isoformat(),
            "created_at": self.created_at.isoformat(),
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
    """U7(`get_briefing`)이 채운다(01-plan 결정 7): `person`·`aliases`·
    `facts[]`·`recent_events[N=5]`·`upcoming_schedules[3]`·`schedule?`·
    `generated_at`. `aliases` 는 `PersonOut.aliases` 와 값이 같더라도 결정
    7 이 명시한 별도 최상위 필드로 둔다(BriefingOut 자체의 계약). 문장화·
    "한 줄 행동 제안"·감정 언급은 이 DTO 에 없다(P6-briefing 몫, 원칙7 경계
    -- get_briefing 은 자료만 돌려준다, LLM 호출 없음).

    `generated_at`(필수) 은 기본값이 있는 필드들보다 먼저 두되(dataclass
    규칙 -- 기본값 없는 필드가 기본값 있는 필드보다 앞에 와야 한다), 실제
    직렬화 키 순서는 `to_dict()` 가 결정 7 문장 순서 그대로 정한다."""

    person: PersonOut
    generated_at: datetime
    aliases: list[str] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    recent_events: list[EventOut] = field(default_factory=list)
    upcoming_schedules: list[ScheduleOut] = field(default_factory=list)
    schedule: ScheduleOut | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "person": self.person.to_dict(),
            "aliases": list(self.aliases),
            "facts": [dict(f) for f in self.facts],
            "recent_events": [e.to_dict() for e in self.recent_events],
            "upcoming_schedules": [s.to_dict() for s in self.upcoming_schedules],
            "schedule": self.schedule.to_dict() if self.schedule is not None else None,
            "generated_at": self.generated_at.isoformat(),
        }


class ToolError(Exception):
    """툴 계층 예외의 공통 베이스. `@traced` 가 `type(e).__name__`·`str(e)`
    를 그대로 trace 에 남기므로, 서브클래스는 짧은 코드성 메시지만 담는다."""


class PersonNotFound(ToolError):
    """`person_id` 가 없거나 다른 `user_id` 소유(security.md §5 격리)."""


class ScheduleNotFound(ToolError):
    """`get_briefing` 의 `schedule_id` 가 없거나 다른 인물(따라서 다른
    `user_id`)의 일정 -- U7. `person_id` 로 이미 소유가 확인된 인물과
    `schedule.person_id` 가 다르면 존재 여부를 흘리지 않기 위해 `PersonNotFound`
    가 아니라 이 예외를 쓴다(`ConfirmationRequired`/`QuestionNotFound` 와 같은
    "다른 소유는 없음과 같게 취급" 패턴)."""


class QuestionNotFound(ToolError):
    """`question_id` 가 `pending_questions` 에 없다."""


class QuestionNotAnswerable(ToolError):
    """이미 답했거나(already_answered) 24h 만료된(expired) 질문에 대한 답변
    시도. `code`(`"already_answered"` | `"expired"`)를 속성으로 담되 질문
    원문·옵션 문자열 자체는 절대 넣지 않는다(U6, `ConfirmationRequired.reason`
    과 같은 패턴)."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ConfirmationRequired(ToolError):
    """D1/D6 -- answered `new_person`/`identity` 질문 없이 `create_person`
    또는 `update_person(display_name=...)` 를 호출.

    `reason` 은 사유 코드만 담는다(질문 원문·답 문자열은 절대 넣지 않는다 --
    `question_id` 가 존재하는지조차 메시지로 흘리지 않기 위해 "질문 없음"과
    "질문은 있지만 조건 미충족"을 같은 사유 집합으로 다룬다). 사유 코드:
    `no_confirmation` / `not_found` / `wrong_kind` / `not_answered` /
    `session_mismatch` / `not_affirmative`.
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class InvalidValue(ToolError):
    """값 집합(EVENT_TYPES/RELATION_TAGS/HIERARCHIES/QUESTION_KINDS/
    ALIAS_SOURCES) 위반, naive datetime, 저장된 `options` 밖의 답 등."""
