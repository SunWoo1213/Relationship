"""Refs: P6-memory R8 S3.5 원칙9 -- U7 루프가 직접 쓴 사실의 원문 연결
(결정 G(ii), 01-plan 73행). `link_direct_facts(ctx, person_id, fact_keys,
event_ids)` 하나만 정의한다.

## 왜 필요한가

`app/agent/loop.py::_record_impl()` 은 게이트를 통과한 `update_person(
facts=…)` 제안을 실행할 뿐, 그 사실이 "어느 대화에서 나왔나"를 스스로
잇지 않는다(그 툴은 `fact_id` 를 돌려주지도 않는다, `app/tools/persons.py`
`update_person`). 그래서 루프가 직접 쓴 사실은 승격(U5, `app/memory/
promote.py`)이 만든 사실과 달리 근거 링크 없이 남았다 -- R8 이 그 한
자리에서만 깨졌다(위임 프롬프트 "왜 필요한가" 절, 실 LLM 왕복으로 확인한
구멍). 이 모듈은 같은 턴·같은 인물의 `add_event` 가 있으면 그 이벤트로
`fact_sources` 를 잇고, 없으면 "연결 없음"을 trace 에 남긴다.

## 호출 시점 (`app/memory/hooks.py::after_record()`)

패턴 감지 → 승격(결정 C-1) **뒤**, 같은 세이브포인트 안에서 인물마다
호출한다. 이 모듈은 `fact_keys_by_person`/`event_ids_by_person`(둘 다
`app/agent/loop.py::RecordOutcome`, U7 이 추가)에 담긴 키·이벤트 id 만
본다 -- 어떤 키를 모을지·어떤 이벤트를 "이번 턴의 것"으로 볼지는 루프의
결정이고, 이 모듈은 주어진 것을 그대로 잇기만 한다.

## 대상 키 (03-log U7 항목 ③)

`fact_keys` 는 이미 `app/agent/loop.py::_fact_keys_from_args()` 가
`pattern:` 접두를 한 번 걸러낸 값이다(U3 가 `update_person` 안에서 이미
거부해 실행 성공 호출에는 나타날 수 없는 불변식이지만, 이 모듈도 자신의
쿼리 결과를 신뢰하지 않는다 -- `PersonFact` 를 직접 조회하므로 그 값이
우연히 `pattern:` 접두라도 이 모듈 자체가 그것을 만들거나 지우지 않는다,
`app/memory/patterns.py` 의 배타적 소유를 건드리지 않는다).

## 중복 방지 (03-log U7 항목, 판정 표 3행)

같은 턴에 같은 키로 `update_person` 이 두 번 실행돼도 `_fact_keys_from_
args`/`RecordOutcome.fact_keys_by_person` 이 이미 턴 단위로 키를 중복
제거해 넘기므로, 이 모듈은 키 하나당 한 번만 링크를 시도한다.
`fact_sources` 의 복합 기본키(`fact_id`, `event_id`)가 있고, 이 모듈도
기존 링크 집합을 먼저 조회해 이미 있는 `(fact_id, event_id)` 쌍은
다시 넣지 않는다(D-6 `_upsert_fact` 와 같은 관례 -- 재실행/재시도에도
안전하다).

## 한 턴에 이벤트가 여러 건이면 (03-log U7 항목 ①)

그 인물의 이번 턴 이벤트 **전부**에 잇는다. 같은 턴 안의 이벤트는 모두
같은 발화(`raw_utterance`)에서 나왔을 가능성이 있고, 어느 하나만 골라
근거로 삼을 객관적 기준이 없다(무작위로 하나만 고르면 "왜 이 이벤트가
근거인가"를 설명할 수 없다) -- R8 의 목적("이 사실이 어느 대화에서
나왔나")은 근거 후보가 여러 개여도 전부 원문으로 거슬러 갈 수 있으면
충족된다. 실무상 한 턴에 같은 인물의 이벤트가 2건 이상인 경우는 드물어
(발화 하나가 보통 그 인물 이벤트 하나로 이어진다) 카드가 시끄러워질
위험은 작다.

## upsert 로직을 새로 만들지 않는다

이 모듈은 `PersonFact` 를 **쓰지 않는다** -- `update_person`(루프가 이미
실행)이 이미 값을 upsert 해 두었으므로, 이 모듈은 그 결과 행을 조회해
`fact_sources` 링크만 추가한다. `(person_id, key)` 조회는 `app/tools/
persons.py::update_person` 과 같은 관례(`updated_at desc` 첫 행)를
따른다."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FactSource, PersonFact
from app.memory.types import (
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_PROMOTE,
    DirectFactLink,
    DirectFactLinkResult,
)
from app.tools.context import ToolContext, traced

#: `DirectFactLink.action` 어휘 2종.
_ACTION_LINKED = "linked"
_ACTION_UNLINKED = "unlinked"

#: `DirectFactLink.reason`(action="unlinked" 일 때만) 어휘 2종.
_REASON_NO_EVENT = "no_event_this_turn"
_REASON_FACT_NOT_FOUND = "fact_not_found"


def _latest_fact(session: Session, person_id: int, key: str) -> PersonFact | None:
    """`(person_id, key)` 로 가장 최근 행을 찾는다 -- `app/tools/persons.py
    ::update_person` 의 upsert 조회와 같은 관례(`updated_at desc` 첫
    행)."""

    return (
        session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person_id)
            .where(PersonFact.key == key)
            .order_by(PersonFact.updated_at.desc())
        )
        .scalars()
        .first()
    )


def _link_fact(session: Session, fact: PersonFact, event_ids: list[int]) -> DirectFactLink:
    """`fact` 에 `event_ids` 전부를 링크한다(이미 있는 링크는 다시 넣지
    않는다). 반환값의 `event_ids` 는 이번 호출 뒤 실제로 존재하는 링크
    전체(기존 + 새로 추가)다."""

    existing_links = set(
        session.execute(select(FactSource.event_id).where(FactSource.fact_id == fact.id))
        .scalars()
        .all()
    )
    to_add = [event_id for event_id in event_ids if event_id not in existing_links]
    for event_id in to_add:
        session.add(FactSource(fact_id=fact.id, event_id=event_id))
    if to_add:
        session.flush()

    return DirectFactLink(
        key=fact.key,
        action=_ACTION_LINKED,
        fact_id=fact.id,
        event_ids=sorted(existing_links | set(event_ids)),
        reason=None,
    )


@traced(MEMORY_TRACE_TOOL_NAME, step=STEP_MEMORY_PROMOTE)
def link_direct_facts(
    ctx: ToolContext, person_id: int, fact_keys: list[str], event_ids: list[int]
) -> DirectFactLinkResult:
    """01-plan 73행(결정 G(ii)) -- `fact_keys` 각각을 `(person_id, key)`
    로 조회해 `event_ids`(이번 턴 그 인물의 이벤트 id 전부)로 잇는다.
    `event_ids` 가 비어 있으면(이번 턴에 이 인물 이벤트가 없음) 모든 키를
    `unlinked`(`reason="no_event_this_turn"`)로 남긴다(01-plan 73행
    "이벤트가 없는 턴의 사실은 연결 없이 두고 trace 에 unlinked 로
    적는다"). 호출자(`app/memory/hooks.py::after_record()`)가 `fact_keys`
    가 빈 턴에는 이 함수를 아예 부르지 않으므로, 여기 닿는 호출은 항상
    이을 대상 키가 하나 이상 있다."""

    links: list[DirectFactLink] = []
    for key in fact_keys:
        # 이벤트 유무와 무관하게 먼저 사실을 조회한다 -- "연결 안 함" 이
        # "사실이 없어서"인지 "이벤트가 없어서"인지 trace 로 구분하기
        # 위함이다(사실이 있으면 `fact_id` 를 채워 unlinked 행에도 어느
        # 사실을 가리키는지 남긴다).
        fact = _latest_fact(ctx.session, person_id, key)
        if fact is None:
            # 방어적 경로 -- update_person 이 같은 턴에 이미 이 키를
            # upsert 했으므로 정상 흐름에서는 일어나지 않는다.
            links.append(
                DirectFactLink(
                    key=key, action=_ACTION_UNLINKED, fact_id=None, reason=_REASON_FACT_NOT_FOUND
                )
            )
            continue

        if not event_ids:
            links.append(
                DirectFactLink(
                    key=key, action=_ACTION_UNLINKED, fact_id=fact.id, reason=_REASON_NO_EVENT
                )
            )
            continue

        links.append(_link_fact(ctx.session, fact, event_ids))

    return DirectFactLinkResult(person_id=person_id, event_ids=list(event_ids), links=links)
