"""Refs: P6-briefing S3.5 S3.6 D14 원칙6 원칙9 -- U3 브리핑 입력 조립
(`build_briefing_input`). 패턴 재계산(결정 K) → `get_briefing` 호출(기존
툴 그대로) → 사실 세 출처 정리(결정 F) → 근거 원문 조회(결정 G) 순서를
그대로 코드로 옮긴다.

## 순서 고정 (01-plan U3)

1. **패턴 재계산(결정 K)** -- `detect_patterns(ctx, person_id)` 를 기존
   함수 그대로 1회 부른다. 그 함수가 `@traced(MEMORY_TRACE_TOOL_NAME,
   step=STEP_MEMORY_PATTERN)` 로 스스로 남기는 `memory_pattern` trace
   행의 id 를 `ctx.last_trace_id` 에서 즉시 읽어 `pattern_trace_id` 로
   둔다 -- 바로 다음 줄에서 `get_briefing` 을 부르면 그 호출도
   `@traced` 라 `ctx.last_trace_id` 를 자기 trace id 로 덮어쓰기 때문에,
   패턴 trace id 는 호출 직후 즉시 꺼내 둬야 한다.
2. **`get_briefing(ctx, person_id, schedule_id)`** -- 기존 툴 그대로
   (`app/tools/briefing.py`). 자료 조회(사실 전부·최근 사건 5·다가오는
   일정 3)와 `briefed_at = ctx.now()` 기록이 여기서 일어난다. 이 모듈은
   같은 조회·기록을 새로 쓰지 않는다.
3. **사실 정리(결정 F)** -- `get_briefing` 의 `facts` 는 `fact_id` 를
   담지 않으므로(`BriefingOut.facts` 는 `{key, value, confidence,
   updated_at}` 뿐, `app/tools/types.py`), 결정 G 의 근거 원문 조회에
   필요한 `fact_id` 를 얻기 위해 `person_facts` 를 **같은 정렬**
   (`updated_at DESC`)로 다시 조회한다 -- `get_briefing` 호출 이후의
   DB 상태를 보므로 패턴 재계산 결과(삭제·갱신)가 이미 반영돼 있다.
   `PATTERN_KEY_PREFIX` 로 시작하거나 `FACT_KEYS` 9종에 속하는 키만
   `used_facts` 로 쓰고, 그 밖 키(옛 자유 키 `소속`·`직장`·`이직` 등)는
   전부 `excluded_facts` 에 `reason="not_fact_key"` 로 넣는다(원본 행은
   수정·삭제하지 않는다). 같은 허용 키가 여러 행이면 `updated_at DESC`
   로 본 **첫 행(최신)만** `used_facts` 에 넣고, 그보다 오래된 나머지
   행은 `excluded_facts` 에 `reason="superseded_by_newer"` 로 남긴다
   (U3 03-log "판단" -- 완전히 버리지 않고 trace 로 추적 가능하게 둔다).
4. **근거 원문(결정 G)** -- `used_facts` 로 고른 사실마다
   `fact_sources → events` 를 조인해 `occurred_at DESC` 로 최근 순
   최대 `_MAX_FACT_SOURCES`(2)건의 `{event_id, raw_utterance,
   occurred_at}` 를 `sources` 에 붙인다. 링크가 1건 이상이면
   `eligible=True`, 없으면 `False`(결정 I `briefing_compose.output.
   used_facts[].eligible` 와 같은 이름 -- U4/U5 가 trace 를 쓸 때 그대로
   옮겨 쓸 수 있게). `events` 는 **읽기만** 한다 -- 이 모듈은
   `insert`/`update`/`delete` 를 하지 않는다.

## 이 모듈이 하지 않는 것

- 브리핑 문장 생성(LLM 호출)은 하지 않는다 -- `app/briefing/compose.py`
  (U4)의 몫이다. 이 모듈은 `app.briefing.compose`·`app.er.judge`·
  `app.embedding` 을 import 하지 않는다(01-plan "지킬 불변식" -- 패턴
  판정·입력 조립에 LLM 없음, 원칙6).
- `person_facts`/`fact_sources` 를 직접 쓰지 않는다 -- 패턴 사실의
  upsert·삭제는 `detect_patterns`(`app/memory/patterns.py`)가 이미 끝낸
  뒤이고, 이 모듈은 그 결과를 읽기만 한다.
- `events` 원문(`raw_utterance`)·`content` 를 수정·삭제하지 않는다
  (01-plan "지킬 불변식" -- 원문 불변).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.briefing.types import BriefingInput
from app.db.models import Event, FactSource, PersonFact, Schedule
from app.memory.patterns import detect_patterns
from app.memory.types import FACT_KEYS
from app.settings import PATTERN_KEY_PREFIX
from app.tools.briefing import get_briefing
from app.tools.context import ToolContext

#: 결정 G 권장 -- 제안 근거로 쓸 원문은 사실당 최근 순(occurred_at DESC)
#: 으로 최대 이 건수만 동봉한다(U3 03-log 선정 기준). 설정값으로 빼지
#: 않는다 -- 바꿀 근거가 생기면 그때 `app.settings` 상수로 옮긴다.
_MAX_FACT_SOURCES = 2


def build_briefing_input(ctx: ToolContext, schedule: Schedule) -> BriefingInput:
    """그 일정 하나의 브리핑 재료를 조립한다(모듈 docstring 순서 1~4).

    `schedule` 은 `select_due_schedules()`(U2)가 이미 소유 확인·잠금을
    끝내고 돌려준 행이다 -- 이 함수는 소유를 다시 확인하지 않는다
    (`get_briefing` 내부의 `_owned_person` 이 한 번 더 확인하긴 하지만,
    `schedule.person_id` 는 이미 `ctx.user_id` 소유임이 보장된 값이다).
    """

    person_id = schedule.person_id

    # ① 패턴 재계산(결정 K) -- 기존 함수 그대로. 바로 다음 줄에서
    # get_briefing 을 부르기 전에 이 호출의 trace id 를 먼저 꺼내 둔다
    # (모듈 docstring 1절 -- ctx.last_trace_id 는 @traced 호출마다 덮인다).
    detect_patterns(ctx, person_id)
    pattern_trace_id = ctx.last_trace_id

    # ② get_briefing(기존 툴 그대로) -- briefed_at = ctx.now() 가 기록된다.
    briefing_out = get_briefing(ctx, person_id, schedule.id)

    # ③ 사실 정리(결정 F) -- get_briefing 이후의 person_facts 상태를
    # updated_at DESC 로 다시 읽는다(fact_id 가 필요해서 재조회한다,
    # 모듈 docstring 3절).
    fact_rows = (
        ctx.session.execute(
            select(PersonFact)
            .where(PersonFact.person_id == person_id)
            .order_by(PersonFact.updated_at.desc())
        )
        .scalars()
        .all()
    )

    used_facts: list[dict[str, Any]] = []
    excluded_facts: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for fact in fact_rows:
        allowed = fact.key.startswith(PATTERN_KEY_PREFIX) or fact.key in FACT_KEYS
        if not allowed:
            excluded_facts.append(
                {"key": fact.key, "fact_id": fact.id, "reason": "not_fact_key"}
            )
            continue

        if fact.key in seen_keys:
            excluded_facts.append(
                {"key": fact.key, "fact_id": fact.id, "reason": "superseded_by_newer"}
            )
            continue
        seen_keys.add(fact.key)

        # ④ 근거 원문(결정 G)
        sources = _fact_sources(ctx, fact.id)
        used_facts.append(
            {
                "key": fact.key,
                "fact_id": fact.id,
                "value": fact.value,
                "confidence": fact.confidence,
                "updated_at": fact.updated_at.isoformat(),
                "eligible": bool(sources),
                "sources": sources,
            }
        )

    return BriefingInput(
        schedule_id=schedule.id,
        person_id=person_id,
        scheduled_at=schedule.scheduled_at,
        title=schedule.title,
        pattern_trace_id=pattern_trace_id,
        used_facts=used_facts,
        excluded_facts=excluded_facts,
        recent_events=[event.to_dict() for event in briefing_out.recent_events],
    )


def _fact_sources(ctx: ToolContext, fact_id: int) -> list[dict[str, Any]]:
    """결정 G -- 사실 하나의 근거 원문을 `occurred_at DESC` 최근 순으로
    최대 `_MAX_FACT_SOURCES` 건 조회한다. `events` 는 읽기만 한다."""

    rows = ctx.session.execute(
        select(Event.id, Event.raw_utterance, Event.occurred_at)
        .join(FactSource, FactSource.event_id == Event.id)
        .where(FactSource.fact_id == fact_id)
        .order_by(Event.occurred_at.desc())
        .limit(_MAX_FACT_SOURCES)
    ).all()

    return [
        {
            "event_id": event_id,
            "raw_utterance": raw_utterance,
            "occurred_at": occurred_at.isoformat(),
        }
        for event_id, raw_utterance, occurred_at in rows
    ]
