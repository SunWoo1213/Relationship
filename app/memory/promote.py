"""Refs: P6-memory S3.5 S3.1 R8 원칙8 원칙9 -- U5 승격.
`promote_person(ctx, person_id, extractor) -> PromotionResult | None`
하나만 정의한다.

## 소유 확인 (security.md §5)

`_promote_and_trace`(이 모듈의 실제 판정 로직) 첫 줄에서
`app.tools.persons._owned_person(session, person_id, user_id)` 를 그대로
재사용한다(U2 와 같음, 새 소유 검사 함수를 만들지 않는다). 다른 사용자의
`person_id` 면 `PersonNotFound` -- `@traced` 가 예외 경로에서 `step=
"tool_error"` 행을 남기고 그대로 다시 던진다. 추출기는 호출되지 않는다.

## ★ 세 판단 (위임 프롬프트가 요구한 것 -- 근거는 03-log U5 항목에도 옮긴다)

01-plan 결정 F(186행)는 "`memory_promote`: 트리거가 걸렸을 때만 1행"과
"트리거 미달은 `memory_pattern` 행에 `unpromoted_count` 를 함께 적는다"를
동시에 적었는데, U2 가 이미 구현한 `PatternResult`/`detect_patterns` 는
승격 이력을 전혀 모른다(패턴 모듈은 `app.memory.extract`/`promote` 를
import 하지 않는다 -- 원칙6, `test_patterns_module_does_not_import_llm_or
_embedding_modules`). 이 모듈은 아래 세 가지를 정한다.

1. **미달 호출에서도 `memory_promote` trace 행을 쓴다.** `patterns.py`
   를 고쳐 `memory_pattern` 에 승격 정보를 얹으면 패턴 모듈이 승격 이력을
   알아야 해 원칙6 이 지키는 모듈 경계(규칙 판정 vs LLM 판정)가 흐려진다.
   대신 이 모듈이 스스로 "왜 승격하지 않았나" 를 자신의 trace 행에
   남긴다 -- 결정 F 문장("트리거가 걸렸을 때만 1행")과는 글자 그대로
   어긋나지만, 그 문장의 **의도**("왜 승격하지 않았는지 남는다")는
   `patterns.py` 를 건드리지 않고 이 방법으로만 채울 수 있다.
2. **`unpromoted_count`/`min_events` 는 `memory_promote` 미달 행 자신에
   싣는다** -- 1번과 같은 선택이다. `person_id`/`unpromoted_count`/
   `min_events` 는 트리거 여부와 무관하게 항상 채운다(R-14 "이번 판정에
   실제로 쓴 min_events").
3. **미달 행의 `considered_event_ids` 는 반드시 빈 목록이다.** 세기만
   한 이벤트를 여기 넣으면 다음 호출의 "이미 본 이벤트" 합집합(결정
   B(ii))에 들어가 그 이벤트들이 영원히 승격되지 않는다(조용한 데이터
   유실). `_promote_and_trace` 의 미달 조기 반환은 `PromotionResult` 의
   `considered_event_ids` 기본값(빈 리스트)을 그대로 두어 이를 코드
   구조로 보장한다 -- `test_promote_person_four_unpromoted_events_are_not
   _lost_and_promote_later_when_fifth_arrives` 가 이 성질 자체를 검증한다.

## 반환값과 trace 출력이 다른 이유 (구현 방법)

`promote_person`(공개, 시그니처 `PromotionResult | None`)이 트리거가
걸리지 않았을 때 `None` 을 돌려주는 것과, 위 1~3번이 요구하는 "미달에도
풍부한 trace 행"은 `@traced` 하나로 동시에 만족할 수 없다 -- `@traced` 는
감싸인 함수의 반환값을 그대로 호출자에게 돌려주는 동시에 그 값을 trace
`output` 으로 쓰기 때문에(`app/tools/context.py::traced`), 함수가 `None`
을 반환하면 `to_jsonable(None)` 이 `None` 을 그대로 돌려줘 trace `output`
이 JSON `null` 이 된다(`AgentTrace.output` 은 `nullable=False` 지만
SQLAlchemy `JSON.none_as_null` 기본값이 `False` 라 SQL NULL 이 아니라 JSON
`null` 로 저장되어 컬럼 제약은 통과한다 -- 이 성질은 라이브러리 기본값에
불과해 이 모듈이 기대는 안전장치가 아니다, 위임 프롬프트가 지적한 함정).

그래서 이 모듈은 실제 판정을 하는 `_promote_and_trace(ctx, person_id,
extractor) -> PromotionResult`(트리거 여부와 무관하게 **항상**
`PromotionResult` 를 돌려준다, 절대 `None` 이 아니다)를 `@traced` 로
감싸고, 공개 `promote_person` 은 그 결과의 `considered_event_ids` 가
비었으면(= 이번 호출에서 추출기를 부르지 않았으면, ★3 이 그 성질을
보장한다) `None` 을, 아니면 그 결과를 그대로 돌려주는 한 줄짜리 래퍼다.
`_owned_person` 은 `_promote_and_trace` 의 첫 줄에 있다 -- `promote_person`
자신은 그 호출 하나뿐이라 "가장 먼저 확인한다"는 실질은 바뀌지 않는다.

## 미승격 판정(결정 B(ii))

`agent_traces` 를 `session_id` 와 무관하게 `tool_name='memory' AND
step='memory_promote' AND output->>'person_id' = '<id>'` 로 누적 조회해,
그 행들의 `considered_event_ids` 합집합을 구한다(`_considered_event_ids`).
그 집합에 없는 그 인물의 `events` 가 미승격이다. 스키마를 바꾸지 않는다
(`events` 에 컬럼을 더하지 않는다, 01-plan 결정 B).

## upsert 규칙 (결정 D-6)

사실마다 `(person_id, key)` 로 기존 `PersonFact` 를 찾는다.
- 없음 -> 새로 만들고(`confidence=DEFAULT_FACT_CONFIDENCE`) 근거
  이벤트 전부를 `fact_sources` 로 잇는다. `action="created"`.
- 있고 값이 같음 -> 값은 그대로 두고 이번 근거 이벤트 중 아직 없는
  링크만 추가한다(`action="same"`, `previous_value=None`).
- 있고 값이 다름 -> 값을 덮어쓰고(`confidence` 도 다시 `DEFAULT_FACT_
  CONFIDENCE` 로 맞춘다) 기존 링크를 전부 지운 뒤 이번 근거 이벤트로
  교체한다. 지워지기 전 값은 `PromotedFact.previous_value` 에 남는다
  (`action="updated"`). 원문 `events` 행 자체는 절대 건드리지 않는다 --
  이 모듈이 `session.delete()` 에 넘기는 것은 `FactSource` 링크뿐이다.

### 동시성 (FIX-020)

`person_facts` 에는 `UNIQUE(person_id, key)` 제약이 있다(0002 리비전).
`_upsert_fact` 는 "있는지 조회 후 분기해서 INSERT/UPDATE"가 아니라
`INSERT ... ON CONFLICT (person_id, key) DO UPDATE` 한 문장으로 끝낸다
-- 두 커넥션이 동시에 같은 키를 upsert 해도 PostgreSQL 이 두 번째 문장을
첫 번째 트랜잭션이 끝날 때까지 블로킹했다가 충돌 처리로 합류시키므로
중복 행이 생기지 않는다(애플리케이션이 조회 후 분기하면 그 사이에 경쟁이
끼어든다 -- FIX-020.md 증상). `action`("created"/"same"/"updated")과
`previous_value` 는 그 원자적 upsert 와는 별도로, upsert 직전에 읽은
"이전 값 추정치"(`existing_value_before`)로 판정한다 -- 이 사전 읽기는
잠그지 않으므로(트레이스 표시용일 뿐 데이터 정합성의 근거가 아니다) 아주
좁은 동시성 창에서는 실제 "직전 값"과 어긋날 수 있지만, upsert 문
자체가 원자적이라 **저장되는 값과 행 개수는 항상 정확하다** -- 어긋날
수 있는 것은 trace 의 `action`/`previous_value` 표시뿐이다.

## 이벤트 상한 (결정 D-4)

미승격 이벤트를 `occurred_at` 오름차순으로 정렬해 그대로 잘라 앞쪽(가장
오래된) `MEMORY_PROMOTE_MAX_EVENTS`(기본 20)건만 추출기에 넘긴다.
"오래된 순" 이므로 재정렬 없이 슬라이스 하나로 끝난다.
"""

from __future__ import annotations

from sqlalchemy import case, literal_column, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.models import AgentTrace, Event, FactSource, PersonFact
from app.memory.extract import ExistingFact, ExtractEvent, FactExtractor, validate_extraction
from app.memory.types import (
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_PROMOTE,
    ExtractedFact,
    PromotedFact,
    PromotionResult,
)
from app.settings import DEFAULT_FACT_CONFIDENCE, MEMORY_PROMOTE_MAX_EVENTS, PATTERN_KEY_PREFIX, promote_min_events
from app.tools.context import ToolContext, traced
from app.tools.persons import _owned_person


def _considered_event_ids(session: Session, person_id: int) -> set[int]:
    """그 인물의 이전 `memory_promote` 행들이 이미 본 이벤트 id 합집합
    (결정 B(ii)) -- `session_id` 와 무관하게 누적 조회한다. `output` 이
    JSON `null` 인 행(있다면)은 `dict` 가 아니므로 건너뛴다."""

    rows = session.execute(
        select(AgentTrace.output)
        .where(AgentTrace.tool_name == MEMORY_TRACE_TOOL_NAME)
        .where(AgentTrace.step == STEP_MEMORY_PROMOTE)
        .where(AgentTrace.output["person_id"].astext == str(person_id))
    ).scalars().all()

    considered: set[int] = set()
    for output in rows:
        if not isinstance(output, dict):
            continue
        considered.update(output.get("considered_event_ids") or [])
    return considered


def _upsert_fact(session: Session, person_id: int, fact: ExtractedFact) -> PromotedFact:
    """`(person_id, fact.key)` 로 upsert 한다(결정 D-6, 모듈 docstring
    "동시성(FIX-020)" 절 참고). `fact` 는 이미 `validate_extraction()` 을
    거쳐 키·값이 정규화되어 있다.

    실제 upsert 는 `INSERT ... ON CONFLICT (person_id, key) DO UPDATE`
    한 문장이다(UNIQUE 제약은 0002 리비전). `existing_value_before` 는
    그 문장 **이전에** 읽은 "이전 값 추정치"일 뿐 -- `action`/
    `previous_value` 판정에만 쓰고, 저장되는 값·행 개수는 전적으로 저
    원자적 SQL 문이 결정한다."""

    existing_value_before = session.execute(
        select(PersonFact.value)
        .where(PersonFact.person_id == person_id)
        .where(PersonFact.key == fact.key)
    ).scalar_one_or_none()

    stmt = (
        pg_insert(PersonFact)
        .values(
            person_id=person_id,
            key=fact.key,
            value=fact.value,
            confidence=DEFAULT_FACT_CONFIDENCE,
        )
        .on_conflict_do_update(
            index_elements=["person_id", "key"],
            set_={
                "value": fact.value,
                # 값이 그대로면(action="same") 기존 confidence 를 건드리지
                # 않는다 -- `PersonFact.value` 는 SET 절 안에서 충돌 대상
                # 행의 갱신 *전* 값을 가리킨다(표준 UPSERT 의미론, EXCLUDED
                # 와 반대편). 기존 코드의 3분기("같음 -> 값만 유지, confidence
                # 불변" 대 "다름 -> 값·confidence 모두 갱신")를 그대로 보존한다.
                "confidence": case(
                    (PersonFact.value == fact.value, PersonFact.confidence),
                    else_=DEFAULT_FACT_CONFIDENCE,
                ),
            },
        )
        .returning(PersonFact.id, literal_column("(xmax = 0)").label("inserted"))
    )
    row = session.execute(stmt).one()
    session.flush()
    # 이 upsert 는 Core 문(ORM 유닛오브워크를 거치지 않는다)이라, 같은
    # 세션에 이미 로드돼 있던 PersonFact ORM 객체(예: `_promote_and_trace`
    # 가 먼저 읽어 둔 `existing_rows`)는 이 UPDATE 를 자동으로 반영하지
    # 않는다 -- `session.get()`/식별자 맵 히트가 갱신 전 값을 그대로
    # 돌려주는 사일런트 버그가 된다(FIX-020 회귀 테스트가 드러냈다).
    # `expire_all()` 로 다음 접근 때 다시 읽게 한다(이미 flush 했으므로
    # 안전 -- 대기 중인 변경을 잃지 않는다).
    session.expire_all()
    fact_id: int = row.id
    inserted: bool = row.inserted

    existing_links = set(
        session.execute(select(FactSource.event_id).where(FactSource.fact_id == fact_id)).scalars().all()
    )

    if inserted:
        # 새 행 -- 충돌 없이 바로 INSERT 됐다(`existing_value_before` 는
        # `None` 이었어야 정상, 아주 좁은 동시성 창에서만 어긋날 수 있다).
        for event_id in fact.source_event_ids:
            session.add(FactSource(fact_id=fact_id, event_id=event_id))
        session.flush()
        return PromotedFact(
            fact_id=fact_id,
            key=fact.key,
            action="created",
            source_event_ids=list(fact.source_event_ids),
            previous_value=None,
        )

    if existing_value_before == fact.value:
        to_add = set(fact.source_event_ids) - existing_links
        for event_id in to_add:
            session.add(FactSource(fact_id=fact_id, event_id=event_id))
        session.flush()
        return PromotedFact(
            fact_id=fact_id,
            key=fact.key,
            action="same",
            source_event_ids=sorted(existing_links | set(fact.source_event_ids)),
            previous_value=None,
        )

    if existing_links:
        stale_links = (
            session.execute(
                select(FactSource)
                .where(FactSource.fact_id == fact_id)
                .where(FactSource.event_id.in_(existing_links))
            )
            .scalars()
            .all()
        )
        for link in stale_links:
            session.delete(link)
        session.flush()

    for event_id in fact.source_event_ids:
        session.add(FactSource(fact_id=fact_id, event_id=event_id))
    session.flush()

    return PromotedFact(
        fact_id=fact_id,
        key=fact.key,
        action="updated",
        source_event_ids=list(fact.source_event_ids),
        previous_value=existing_value_before,
    )


@traced(MEMORY_TRACE_TOOL_NAME, step=STEP_MEMORY_PROMOTE)
def _promote_and_trace(ctx: ToolContext, person_id: int, extractor: FactExtractor) -> PromotionResult:
    """실제 승격 판정. 트리거 여부와 무관하게 **항상** `PromotionResult`
    를 돌려준다(모듈 docstring "반환값과 trace 출력이 다른 이유" 참고) --
    이 값이 그대로 `memory_promote` trace `output` 이 된다. 공개
    `promote_person` 이 이 결과를 보고 `None` 여부를 가른다."""

    person = _owned_person(ctx.session, person_id, ctx.user_id)
    min_events = promote_min_events()

    considered = _considered_event_ids(ctx.session, person.id)

    query = select(Event).where(Event.person_id == person.id).order_by(Event.occurred_at.asc())
    if considered:
        query = query.where(Event.id.notin_(considered))
    unpromoted_events = list(ctx.session.execute(query).scalars().all())
    unpromoted_count = len(unpromoted_events)

    if unpromoted_count < min_events:
        # ★1·★2·★3 -- 미달에도 trace 행은 쓰되(모듈 docstring), 세기만
        # 한 이벤트를 considered_event_ids 에 넣지 않는다(기본값 빈
        # 리스트 그대로 -- 다음 호출에서 다시 미승격으로 잡혀야 한다).
        return PromotionResult(
            person_id=person.id,
            unpromoted_count=unpromoted_count,
            min_events=min_events,
        )

    batch = unpromoted_events[:MEMORY_PROMOTE_MAX_EVENTS]

    existing_rows = (
        ctx.session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person.id)
            .where(~PersonFact.key.startswith(PATTERN_KEY_PREFIX))
            .order_by(PersonFact.key.asc())
        )
        .scalars()
        .all()
    )
    existing_facts = [ExistingFact(key=row.key, value=row.value) for row in existing_rows]

    extract_events = [
        ExtractEvent(
            id=event.id,
            type=event.type,
            content=event.content,
            raw_utterance=event.raw_utterance,
            occurred_at=event.occurred_at,
        )
        for event in batch
    ]

    extraction = extractor.extract(person.display_name, existing_facts, extract_events)
    validated = validate_extraction(extraction, extract_events)

    promoted: list[PromotedFact] = [
        _upsert_fact(ctx.session, person.id, fact) for fact in validated.facts
    ]

    return PromotionResult(
        person_id=person.id,
        unpromoted_count=unpromoted_count,
        min_events=min_events,
        considered_event_ids=[event.id for event in batch],
        facts=promoted,
        rejected=validated.rejected,
        llm_provider=extraction.provider,
        llm_model=extraction.model,
        tokens_in=extraction.tokens_in,
        tokens_out=extraction.tokens_out,
    )


def promote_person(ctx: ToolContext, person_id: int, extractor: FactExtractor) -> PromotionResult | None:
    """01-plan U5 시그니처. 미승격 이벤트가 `promote_min_events()`
    미만이면 추출기를 부르지 않고 `None` 을 돌려준다(트리거 미달) --
    `_promote_and_trace` 가 이미 빈 `considered_event_ids` 로 그 상태를
    표시해 두므로 여기서는 그 성질만 확인한다(모듈 docstring 참고)."""

    result = _promote_and_trace(ctx, person_id, extractor)
    if not result.considered_event_ids:
        return None
    return result
