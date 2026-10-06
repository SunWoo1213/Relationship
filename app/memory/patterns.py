"""Refs: P6-memory D14 D9(대체됨) S3.5 R11 security§5 원칙6 원칙8 원칙9 --
반복 패턴 감지(규칙 기반, U2). `detect_patterns(ctx, person_id)` 하나만
정의한다.

## 이 모듈이 하지 않는 것 (원칙6)

패턴 판정은 SQL 과 파이썬 산수만으로 한다. `app.memory.extract`(LLM 사실
추출기, U4)·`app.er.judge`(엔티티 해석 LLM 판정)·`app.embedding`(임베딩
공급자)을 **이 모듈은 import 하지 않는다** -- `tests/test_memory_patterns.py`
가 이 파일의 `import` 문 자체(AST)를 검사해 강제한다. `app.tools.context`
가 `ToolContext` 타입을 위해 내부적으로 `app.embedding` 을 끌어오는 것은
이 모듈의 직접 import 가 아니므로 대상이 아니다.

## 소유 확인 (security.md §5)

첫 줄에서 `app.tools.persons._owned_person(session, person_id, user_id)`
를 그대로 재사용한다. 새 소유 검사 함수를 만들지 않는다(01-plan U2 항목,
"기존 산출물 재사용" 표). 다른 사용자의 `person_id` 면 `PersonNotFound`
(`@traced` 가 `step="tool_error"` 로 남긴다) -- 패턴 사실은 0건.

## 창·집계 규칙 (01-plan 결정 C)

- **C-1 시점**: 이 함수는 "언제 부를지"를 스스로 정하지 않는다 -- 이벤트가
  저장된 턴마다 그 인물에 대해 부르는 것은 U6(`app.agent.loop`)의 몫이다.
  이 함수 자체는 호출될 때마다 그 인물의 **전체 7종 type** 을 처음부터
  다시 센다(순수 함수에 가깝다. 유일한 부수효과는 `person_facts`/
  `fact_sources` upsert).
- **C-2 창**: `[ctx.now() - PATTERN_WINDOW_DAYS일, ctx.now()]` 의 UTC
  절대 시간(일수 x 24시간), `occurred_at` 기준. 경계 `now - N일` 은
  포함(`>=`), `now` 초과(미래)는 제외(`<=` 로 자연히 걸러진다). 표기만
  `user_timezone()`(FIX-005, 기본 서울)로 바꾼다 -- 창 계산 자체는 시간대
  영향이 없다(절대 길이).
- **C-3 value 형식**: `"{n}회 (YYYY-MM-DD, YYYY-MM-DD, ...)"`, 날짜
  오름차순(쿼리가 이미 `occurred_at asc` 로 정렬해 주므로 재정렬하지
  않는다 -- UTC 오름차순은 시간대 변환 후에도 날짜 오름차순을 보존한다),
  같은 날 두 건이면 두 번 적는다.
- **C-4 confidence**: `1.0` 고정 (`app.settings.DEFAULT_FACT_CONFIDENCE`
  와 값은 같지만 별개 상수다 -- 그 값은 `update_person` 직접 사실용이고
  이 값은 패턴 전용, `app/settings.py` "PATTERN_*" 절 참고).
- **C-5 기준 미달**: 기존 `pattern:{type}` 사실이 있는데 이번 판정에서
  `count < min_count` 로 떨어지면 그 행을 삭제한다(`fact_sources` 는 FK
  CASCADE 로 함께 사라진다, `events` 행은 손대지 않는다). 이전 `value`
  는 trace `changes[]` 의 `previous_value` 에 남는다(권장 (i)).
- **C-6 재계산 범위**: 이벤트가 실제로 새로 생긴 type 만이 아니라 그
  인물의 `EVENT_TYPES` 7종 전부를 매번 다시 센다(쿼리 1개).

## fact_sources 동기화 (판정 5)

`pattern:{type}` 사실이 유지되는 동안(`count >= min_count`) 이번 창 안
이벤트 id 집합과 `fact_sources` 링크 집합을 정확히 맞춘다 -- 빠진 링크는
추가하고, 창 밖으로 밀려난 링크는 지운다. 값 문자열이 우연히 같아도(예:
같은 개수·같은 날짜 집합인데 이벤트 id 만 바뀐 경우는 실무상 없지만) 링크
집합 자체를 항상 대조해 판정한다 -- 문자열 비교만으로 "변경 없음"을
단정하지 않는다.

## trace (결정 F)

`@traced(MEMORY_TRACE_TOOL_NAME, step=STEP_MEMORY_PATTERN)` 로 감싼다.
`tokens_in`/`tokens_out` 은 반환값에 `trace_tokens()` 가 없으므로 자동으로
`(0, 0)`(LLM 미사용, 원칙6). 반환값 `PatternResult.to_dict()`(U2 가
`app/memory/types.py` 에 추가)가 곧 trace `output` 모양이다 -- `person_id`·
`window{from,to}`·**이번 판정에 실제로 쓴** `window_days`/`min_count`
(D14 "코드에서 지켜야 할 것", 원칙8·9)·`counts`(창 안에 실제로 이벤트가
있었던 type 만, 0건인 type 은 생략 -- 부재 자체가 0 의 증거이므로)·
`changes[]`(만들었거나/갱신했거나/지운 사실만 담는다. 값·링크 모두 그대로면
DB 를 쓰지 않고 `changes` 에도 넣지 않는다 -- "변경 없음"은 로그 부재로
표현한다).

## 동시성 (FIX-026 R-20-1)

`person_facts` 의 `UNIQUE(person_id, key)` 제약(FIX-020, 0002 리비전)이
생긴 뒤에도 이 모듈의 패턴 사실 생성/갱신은 "조회 후 분기"로 남아
있었다 -- 두 커넥션이 동시에 같은 `(person_id, "pattern:{type}")` 을
새로 만들면 둘 다 "없음"을 읽고 둘 다 평범한 `INSERT` 를 내 하나가
`IntegrityError`(턴 전체 500)로 실패했다(`app.memory.promote._upsert_fact`
가 FIX-020 에서 이미 쓴 것과 같은 결함). 이 모듈도 같은 해법을 쓴다 --
"있으면 UPDATE, 없으면 INSERT" 분기를 `INSERT ... ON CONFLICT
(person_id, key) DO UPDATE` 한 문장으로 바꾸고, RETURNING `(xmax = 0)`
으로 "이번 문장에서 새로 삽입됐는가"(`inserted`)를 판정한다(promote.py
와 동일한 관례, 모듈 docstring 아래 `_upsert_or_delete_pattern_fact`
참고). `value`·`confidence`·`fact_sources` 동기화·`PatternChange`
반환값(`created`/`updated`/삭제는 `deleted`, 변경 없음은 로그 부재)은
그대로다 -- 바뀐 것은 저장 문장 하나뿐이다. `updated_at` 은
`app.memory.promote._upsert_fact` 와 같은 이유(F-20-1, `Column(onupdate=
func.now())` 가 Core `ON CONFLICT` 의 `set_` 에는 적용되지 않는다)로
값이 같을 때만 유지하는 CASE 를 쓴다.

세션 식별자 맵 부작용은 promote.py 처럼 `session.expire_all()` 로
전체를 비우지 않는다 -- 이 함수는 한 인물의 7종 type 을 순서대로
처리하며 매 반복이 서로 다른 `PersonFact` 행(서로 다른 `key`)을 다루므로,
이번 반복에서 이미 로드해 둔 `existing`(바로 이 upsert 가 갱신한 행)
**하나만** `session.expire()` 하면 된다 -- 다음에 그 객체의 속성을
다시 읽을 일이 있다면(이 함수 자신은 다시 읽지 않지만, 같은 세션을 쓰는
호출자가 이어서 읽을 수 있다) 새 값을 가져온다.
"""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import case, func, literal_column, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.models import EVENT_TYPES, Event, FactSource, PersonFact
from app.memory.types import (
    MEMORY_TRACE_TOOL_NAME,
    STEP_MEMORY_PATTERN,
    PatternChange,
    PatternResult,
)
from app.settings import PATTERN_KEY_PREFIX, pattern_config, user_timezone
from app.tools.context import ToolContext, traced
from app.tools.persons import _owned_person

#: C-4 -- 패턴 사실의 확신도는 항상 1.0(규칙 판정, D9/D14 불변).
_PATTERN_CONFIDENCE = 1.0


@traced(MEMORY_TRACE_TOOL_NAME, step=STEP_MEMORY_PATTERN)
def detect_patterns(ctx: ToolContext, person_id: int) -> PatternResult:
    """그 인물의 `EVENT_TYPES` 7종을 창 `[now-window_days일, now]` 안에서
    다시 세어 `pattern:{type}` 사실을 upsert/삭제한다(01-plan U2, 모듈
    docstring 참고). `person_id` 가 `ctx.user_id` 소유가 아니면
    `PersonNotFound`(security §5).
    """
    person = _owned_person(ctx.session, person_id, ctx.user_id)

    config = pattern_config()
    window_to = ctx.now()
    window_from = window_to - timedelta(days=config.window_days)

    rows = (
        ctx.session.execute(
            select(Event.id, Event.type, Event.occurred_at)
            .where(Event.person_id == person.id)
            .where(Event.occurred_at >= window_from)
            .where(Event.occurred_at <= window_to)
            .order_by(Event.occurred_at.asc())
        )
        .all()
    )

    events_by_type: dict[str, list[tuple[int, object]]] = {}
    for event_id, event_type, occurred_at in rows:
        events_by_type.setdefault(event_type, []).append((event_id, occurred_at))

    counts = {event_type: len(items) for event_type, items in events_by_type.items()}

    tz = user_timezone()
    changes: list[PatternChange] = []

    for event_type in EVENT_TYPES:
        items = events_by_type.get(event_type, [])
        key = f"{PATTERN_KEY_PREFIX}{event_type}"

        existing = (
            ctx.session.execute(
                select(PersonFact)
                .where(PersonFact.person_id == person.id)
                .where(PersonFact.key == key)
                .order_by(PersonFact.updated_at.desc())
            )
            .scalars()
            .first()
        )

        if len(items) < config.min_count:
            if existing is not None:
                deleted_previous_value = existing.value
                deleted_fact_id = existing.id
                ctx.session.delete(existing)
                ctx.session.flush()
                changes.append(
                    PatternChange(
                        type=event_type,
                        action="deleted",
                        fact_id=deleted_fact_id,
                        event_ids=[],
                        previous_value=deleted_previous_value,
                    )
                )
            continue

        event_ids = [event_id for event_id, _ in items]
        dates = [occurred_at.astimezone(tz).date().isoformat() for _, occurred_at in items]
        value = f"{len(items)}회 ({', '.join(dates)})"
        previous_value = existing.value if existing is not None else None

        # FIX-026(R-20-1) -- "조회 후 분기"가 아니라 `INSERT ... ON
        # CONFLICT (person_id, key) DO UPDATE` 한 문장으로 끝낸다(모듈
        # docstring "동시성(FIX-026 R-20-1)" 절). 위에서 읽은 `existing` 은
        # `previous_value` 표시용 추정치일 뿐 -- 새로 삽입됐는지는 이
        # 문장의 RETURNING `(xmax = 0)` 으로 판정한다(`inserted`,
        # app.memory.promote._upsert_fact 와 같은 관례).
        stmt = (
            pg_insert(PersonFact)
            .values(
                person_id=person.id,
                key=key,
                value=value,
                confidence=_PATTERN_CONFIDENCE,
            )
            .on_conflict_do_update(
                index_elements=["person_id", "key"],
                set_={
                    "value": value,
                    "confidence": _PATTERN_CONFIDENCE,
                    # FIX-026(F-20-1 과 같은 이유 -- `onupdate=func.now()`
                    # 는 Core `ON CONFLICT` 의 `set_` 에 적용되지 않는다)
                    # -- 값이 그대로면 updated_at 을 건드리지 않는다.
                    "updated_at": case(
                        (PersonFact.value == value, PersonFact.updated_at),
                        else_=func.now(),
                    ),
                },
            )
            .returning(PersonFact.id, literal_column("(xmax = 0)").label("inserted"))
        )
        row = ctx.session.execute(stmt).one()
        ctx.session.flush()
        if existing is not None:
            # 이 upsert 는 Core 문이라 ORM 유닛오브워크를 거치지 않는다 --
            # 위에서 이미 로드해 둔 `existing` 객체는 이 UPDATE 를 자동으로
            # 반영하지 않는다(app/memory/promote.py 의 같은 FIX-020 주석
            # 참고). 이 객체 하나만 expire 한다(세션 전체를 비우지 않는다,
            # 모듈 docstring 참고).
            ctx.session.expire(existing)
        fact_id: int = row.id
        inserted: bool = row.inserted

        existing_links = set(
            ctx.session.execute(
                select(FactSource.event_id).where(FactSource.fact_id == fact_id)
            )
            .scalars()
            .all()
        )
        target_links = set(event_ids)
        to_add = target_links - existing_links
        to_remove = existing_links - target_links

        if inserted:
            for event_id in event_ids:
                ctx.session.add(FactSource(fact_id=fact_id, event_id=event_id))
            ctx.session.flush()
            changes.append(
                PatternChange(
                    type=event_type,
                    action="created",
                    fact_id=fact_id,
                    event_ids=event_ids,
                    previous_value=None,
                )
            )
            continue

        value_changed = previous_value != value

        if not value_changed and not to_add and not to_remove:
            # 값·링크 모두 이전과 같다 -- DB 를 건드리지 않고 trace 에도
            # 넣지 않는다("변경 없음"은 changes[] 에 항목이 없는 것으로
            # 표현한다).
            continue

        for event_id in to_add:
            ctx.session.add(FactSource(fact_id=fact_id, event_id=event_id))

        if to_remove:
            stale_links = (
                ctx.session.execute(
                    select(FactSource)
                    .where(FactSource.fact_id == fact_id)
                    .where(FactSource.event_id.in_(to_remove))
                )
                .scalars()
                .all()
            )
            for link in stale_links:
                ctx.session.delete(link)

        ctx.session.flush()
        changes.append(
            PatternChange(
                type=event_type,
                action="updated",
                fact_id=fact_id,
                event_ids=event_ids,
                previous_value=previous_value,
            )
        )

    return PatternResult(
        person_id=person.id,
        window_from=window_from,
        window_to=window_to,
        window_days=config.window_days,
        min_count=config.min_count,
        counts=counts,
        changes=changes,
    )
