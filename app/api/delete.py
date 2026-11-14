"""Refs: P2b-person-delete U1 U2 F-4d2507 security§5 원칙8 원칙9 -- 인물 완전 삭제의
JSONB 참조 판별 규칙(순수 함수, DB 없음)과 삭제 서비스 `delete_person`(U2).

`DELETE /persons/{id}` 는 FK CASCADE 로 5개 테이블(+`fact_sources`)을 지우지만,
`pending_questions.context` 와 `agent_traces.input/output` 은 `person_id` 컬럼이
없는 JSONB 라 CASCADE 가 닿지 않는다. 이 모듈의 `references_person()` 이 "이
JSON 값이 그 인물 id 를 가리키는가" 를 **구조 규칙**으로 판정한다(결정 C-3 (a)).
텍스트에 그 숫자가 있다고 지우지 않는다 -- 이벤트·일정·질문 id 는 인물 id 와
다른 IDENTITY 시퀀스라 값이 겹칠 수 있고, 그걸 지우면 남의 행을 지운다.

## 규칙 (`PERSON_REF_RULES`, 번호는 01-plan 결정 C-3 확정과 같다)

1. 어느 깊이든 키 `person_id`·`matched_person_id` 의 **정수** 값
2. 키 `person` 아래 사전의 `id` (`PersonOut`·`Candidate`·`BriefingOut` 의 직렬화)
3. 툴 이름이 `create_person`·`update_person` 인 trace `output` **최상위** `id`
   (`PersonOut.to_dict()` 는 인물 id 를 `"id"` 로 쓴다. `EventOut.id`·
   `ScheduleOut.id` 는 이벤트/일정 id 라 툴 이름이 다르면 보지 않는다)
4. 키 `candidate_ids`·`person_ids` 아래 사전의 **값**(이름→id, 언급→id)
5. 키 `candidate_person_ids` 아래 배열의 원소

`bool`(`True == 1`)·문자열 `"42"`·실수 `42.0` 은 인물 id 로 보지 않는다.

## 쓰는 곳 전수 목록 (U1, `grep -rn "AgentTrace(\\|ask_payload\\|to_jsonable(" app/`)

`agent_traces` 를 쓰는 곳은 8곳(`app/tools/context.py` 2·`app/memory/hooks.py`·
`app/push/notifier.py`·`app/briefing/run.py` 3·`app/api/routes.py`)이고,
`pending_questions` 는 `app/tools/questions.py::ask_user` 한 곳이 쓴다.

| 쓰는 곳 | JSONB 경로 | 규칙 |
|---|---|---|
| `@traced` 툴 trace (`tools/context.py` 224행) | `input.person_id`(update_person·add_event·add_schedule·get_briefing 인자) | 1 |
| 같은 곳 `output` | `create_person`/`update_person` 최상위 `id` | 3 |
| 같은 곳 `output` | `search_person` 배열 `[].person.id` | 2 |
| 같은 곳 `output` | `get_briefing` `person.id` + `recent_events[]`·`upcoming_schedules[]`·`schedule` 의 `person_id` | 2·1 |
| 같은 곳 `output` | `add_event`·`add_schedule` 의 `person_id`(최상위 `id` 는 이벤트·일정 id -- 규칙 3 이 툴 이름으로 거른다) | 1 |
| `tool_error` (`tools/context.py` 198행) | `input.person_id` | 1 |
| ER `er_resolve` (`er/types.py` `Resolution.to_dict`) | `candidates[].person_id` · `confidence_breakdown.matched_person_id` · `decision.matched_person_id` | 1 |
| ER 적용(`AppliedResolution.to_dict`) | `person_id` | 1 |
| ER 되묻기 (`er/pipeline.py` 197~238행 → `ask_user` trace input·`pending_questions.context`) | `context.candidate_ids`(이름→id) · `context.confidence_breakdown.matched_person_id` | 4·1 |
| 재개 재료 (`agent/types.py` `PendingResume`) | `context.resume.schedule.person_id` (`pending_calls[].args.person` 은 언급 **문자열**이라 해당 없음) | 1 |
| 루프 `loop_resolve*` (`agent/loop.py` 277·303행) | `decisions[].person_id` · `person_ids`(언급→id, `loop_resolve_done.output`) | 1·4 |
| 루프 `loop_query` (`agent/loop.py` 1210·1226행) | `person_id` · `resolutions[].person_id` | 1 |
| 브리핑 `briefing_compose`·`briefing_error` (`briefing/run.py` 148·225·296행) | `input`/`output` 의 `person_id` | 1 |
| 푸시 `push_send` (`push/notifier.py` 241행) | `input.person_id` (`output` 에는 `schedule_id` 만) | 1 |
| 메모리 `memory_promote`·`memory_pattern`·`memory_error`·direct (`memory/types.py`·`hooks.py`) | `person_id` | 1 |
| ER 판정 스키마 (`er/judge.py` 523행) | `candidate_person_ids` -- 스키마 설명에만 있고 trace 에 저장되지 않는다(계획 규칙 5 를 방어적으로 유지) | 5 |

**계획 표와 다른 점(U1 확인)**: 계획은 "`pending_questions.context["resume"].person_ids`"
라 적었지만 `PendingResume.to_dict()` 에는 `person_ids` 가 없다. `person_ids` 는
`ResolveOutcome.to_dict()` -- 곧 `loop_resolve_done` trace output -- 에 있다. 규칙 4 가
키 이름으로 잡으므로 규칙은 그대로다.

**해당 규칙이 없는(남는) 행** -- 인물 id 가 아예 없다(결정 G (i) 한계):
- `loop_extract` input(발화 원문)·`loop_turn`·`loop_query` 의 `reply`
- `briefing_run`(`briefing/run.py` 320행): `selected`/`briefed`/`skipped` 의 **일정 id** 만
  있고 인물 id·이름·문장은 없다. 인물이 지워지면 그 일정 id 가 가리키는 행이 사라질 뿐이다.
- `loop_error`(`api/routes.py` 295행): `input.utterance` 만 있다.

## 새 trace 모양을 만드는 패키지의 의무 (리스크 2)

인물 id 를 **새 키 이름**으로 JSONB 에 넣는 패키지는 이 모듈의 상수를 함께
갱신해야 한다. 갱신하지 않으면 U2 센티널 테스트가 그 경로를 지나가지 않는 한
잡히지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Text, cast, delete, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    AgentTrace,
    Event,
    FactSource,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)
from app.tools.persons import _owned_person
from app.tools.types import ConfirmationRequired

#: `ConfirmationRequired.reason` -- 확인값이 없거나 현재 `display_name` 과 다를 때(결정 A).
CONFIRM_REASON = "person_delete"


@dataclass(frozen=True)
class PersonRefRule:
    """판별 규칙 하나의 설명(번호는 01-plan 결정 C-3 확정과 같다). 실제 판정은
    아래 키 상수로 `references_person()` 이 한다 -- 이 목록은 문서·테스트용이다."""

    number: int
    name: str
    description: str


#: 규칙 1 -- 어느 깊이든 이 키의 정수 값이 인물 id 다.
PERSON_ID_KEYS: tuple[str, ...] = ("person_id", "matched_person_id")
#: 규칙 2 -- 이 키 아래 사전의 `id` 가 인물 id 다.
PERSON_OBJECT_KEYS: tuple[str, ...] = ("person",)
#: 규칙 3 -- 이 툴의 trace `output` 최상위 `id` 가 인물 id 다.
TOP_LEVEL_ID_TOOLS: frozenset[str] = frozenset({"create_person", "update_person"})
#: 규칙 4 -- 이 키 아래 사전의 **값**이 인물 id 다(이름→id, 언급→id).
ID_MAP_KEYS: tuple[str, ...] = ("candidate_ids", "person_ids")
#: 규칙 5 -- 이 키 아래 배열의 원소가 인물 id 다.
ID_LIST_KEYS: tuple[str, ...] = ("candidate_person_ids",)

PERSON_REF_RULES: tuple[PersonRefRule, ...] = (
    PersonRefRule(1, "id_key", "키 person_id·matched_person_id 의 정수 값(어느 깊이든)"),
    PersonRefRule(2, "person_object", "키 person 아래 사전의 id"),
    PersonRefRule(3, "top_level_id", "create_person·update_person trace output 최상위 id"),
    PersonRefRule(4, "id_map_values", "키 candidate_ids·person_ids 아래 사전의 값"),
    PersonRefRule(5, "id_list", "키 candidate_person_ids 아래 배열의 원소"),
)


def _is_id(value: Any, person_id: int) -> bool:
    """`value` 가 정수이고 `person_id` 와 같은가. `bool`·문자열·실수는 아니다."""

    return type(value) is int and value == person_id


def _walk(node: Any, person_id: int) -> bool:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in PERSON_ID_KEYS and _is_id(value, person_id):
                return True
            if key in PERSON_OBJECT_KEYS and isinstance(value, dict) and _is_id(
                value.get("id"), person_id
            ):
                return True
            if key in ID_MAP_KEYS and isinstance(value, dict) and any(
                _is_id(item, person_id) for item in value.values()
            ):
                return True
            if key in ID_LIST_KEYS and isinstance(value, list) and any(
                _is_id(item, person_id) for item in value
            ):
                return True
            if _walk(value, person_id):
                return True
        return False
    if isinstance(node, list | tuple):
        return any(_walk(item, person_id) for item in node)
    return False


def references_person(obj: Any, person_id: int, *, tool_name: str | None = None) -> bool:
    """`obj`(JSONB 로 저장된 값 하나)가 `person_id` 인물을 가리키면 `True`.

    `tool_name` 은 규칙 3 에만 쓴다 -- trace **output** 을 판정할 때 그 행의
    `tool_name` 을 넘긴다(`create_person`·`update_person` 일 때만 최상위 `id` 가
    인물 id). `input`·`pending_questions.context` 를 판정할 때는 넘기지 않는다.
    입력은 바꾸지 않는다.
    """

    if (
        isinstance(obj, dict)
        and tool_name in TOP_LEVEL_ID_TOOLS
        and _is_id(obj.get("id"), person_id)
    ):
        return True
    return _walk(obj, person_id)


# ---------------------------------------------------------------------------
# U2 -- 삭제 서비스
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PersonDeleteSummary:
    """`delete_person` 의 반환(결정 F) -- 테이블별 삭제 건수. 이름·원문은 담지 않는다."""

    person_id: int
    deleted: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {"person_id": self.person_id, "deleted": dict(self.deleted)}


def _count(session: Session, model: Any, *conditions: Any) -> int:
    return session.execute(select(func.count()).select_from(model).where(*conditions)).scalar_one()


def _referencing_question_ids(session: Session, person_id: int) -> list[int]:
    """그 인물을 참조하는 `pending_questions` 행 id(답변 여부 무관, 결정 C-1).

    SQL 은 숫자가 텍스트에 들어 있는 행만 **넉넉히** 거르고(과잉 포함·누락 0),
    정밀 판정은 `references_person` 이 한다(결정 C-3). `tool_name` 은 넘기지 않는다."""

    rows = session.execute(
        select(PendingQuestion.id, PendingQuestion.context)
        .where(cast(PendingQuestion.context, Text).like(f"%{person_id}%"))
        .order_by(PendingQuestion.id)
    ).all()
    return [row.id for row in rows if references_person(row.context, person_id)]


def _referencing_trace_ids(session: Session, person_id: int) -> list[int]:
    """그 인물을 참조하는 `agent_traces` 행 id(전 세션, 결정 C-2·K). `output` 은 행의
    `tool_name` 과 함께, `input` 은 `tool_name` 없이 판정한다(U1 계약)."""

    pattern = f"%{person_id}%"
    rows = session.execute(
        select(AgentTrace.id, AgentTrace.tool_name, AgentTrace.input, AgentTrace.output)
        .where(
            or_(
                cast(AgentTrace.input, Text).like(pattern),
                cast(AgentTrace.output, Text).like(pattern),
            )
        )
        .order_by(AgentTrace.id)
    ).all()
    return [
        row.id
        for row in rows
        if references_person(row.output, person_id, tool_name=row.tool_name)
        or references_person(row.input, person_id)
    ]


def delete_person(
    session: Session, user_id: str, person_id: int, confirm: str | None
) -> PersonDeleteSummary:
    """인물 한 명을 완전히 지운다(P2b U2, 결정 A·C·D·E·F·H·K).

    순서(이 순서가 계약이다 -- 변이 V2-3·V2-5·V2-7 이 지킨다):
    ① 소유 확인 -- 없거나 남의 것이면 `PersonNotFound`(확인값 검사보다 **먼저**, 결정 E)
    ② 확인값 검사 -- `confirm` 이 현재 `display_name` 과 정확히 같지 않으면
       `ConfirmationRequired("person_delete")`. **여기까지 쓰기 0.**
    ③ 삭제 건수 집계(삭제 **전**) ④ `pending_questions` 참조 행 삭제
    ⑤ `agent_traces` 참조 행 삭제 ⑥ `DELETE FROM persons` 한 문장 -- 별칭·사실·
    이벤트·일정과 `fact_sources` 는 FK CASCADE 가 지운다(결정 D, 앱이 따로 지우지 않음)
    ⑦ commit 하지 않는다 -- 트랜잭션 경계는 호출자(`get_session`)다. trace 도 남기지
    않는다(결정 H -- 방금 지운 참조를 다시 만들지 않는다).
    """

    person = _owned_person(session, person_id, user_id)
    if confirm is None or confirm != person.display_name:
        raise ConfirmationRequired(CONFIRM_REASON)

    pid = person.id
    fact_source_condition = or_(
        FactSource.fact_id.in_(select(PersonFact.id).where(PersonFact.person_id == pid)),
        FactSource.event_id.in_(select(Event.id).where(Event.person_id == pid)),
    )
    question_ids = _referencing_question_ids(session, pid)
    trace_ids = _referencing_trace_ids(session, pid)
    deleted = {
        "persons": 1,
        "person_aliases": _count(session, PersonAlias, PersonAlias.person_id == pid),
        "person_facts": _count(session, PersonFact, PersonFact.person_id == pid),
        "fact_sources": _count(session, FactSource, fact_source_condition),
        "events": _count(session, Event, Event.person_id == pid),
        "schedules": _count(session, Schedule, Schedule.person_id == pid),
        "pending_questions": len(question_ids),
        "agent_traces": len(trace_ids),
    }

    if question_ids:
        session.execute(delete(PendingQuestion).where(PendingQuestion.id.in_(question_ids)))
    if trace_ids:
        session.execute(delete(AgentTrace).where(AgentTrace.id.in_(trace_ids)))
    session.execute(delete(Person).where(Person.id == pid).where(Person.user_id == user_id))
    return PersonDeleteSummary(person_id=pid, deleted=deleted)
