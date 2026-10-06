"""Refs: P6-briefing S3.6 S3.2 R12 원칙7 원칙9 -- U5 실행 함수
(`run_briefings`). 주기 작업(U7)과 수동 트리거(U6)가 **같은 함수**를
부른다(S3.6 "수동 트리거 = 같은 함수"). 대상 선정(U2) -> 일정마다
세이브포인트 안에서 입력 조립(U3) -> 생성(U4, 실패 시 템플릿 대체) ->
푸시 자리(결정 J) -> `briefing_compose` trace 1행 -> 실행 끝에
`briefing_run` trace 1행을 남긴다.

## 시그니처 -- 01-plan 75행과 다르게 한 점(R-5, 02-plan-verify 권고)

01-plan 75행은 `run_briefings(session_factory, *, now, composer, ...)`
로 **세션 팩토리**를 받는 모양을 적었다. 이 단위는 위임 프롬프트의
R-5 처리 결정을 그대로 따라 **이미 열린 세션을 가진 `ToolContext`**를
받는다: `run_briefings(ctx, *, composer, notifier=NullNotifier(),
schedule_id=None, trigger, lead_hours=BRIEFING_LEAD_HOURS) ->
BriefingRunResult`. 이유:

- 커밋은 **호출자 몫**이다. API 경로(U6)는 `get_session()`(요청 단위
  세션, 요청 끝에 commit)을 그대로 의존성으로 받아 이 함수에 넘길
  것이고, 주기 작업(U7)은 실행마다 `session_scope()`로 세션을 열고
  그 범위가 끝날 때 commit·close 한다 -- 둘 다 "트랜잭션 경계는
  호출자가 잡는다"(`app/tools/context.py` 결정 2)는 기존 규약 그대로다.
  `run_briefings` 가 스스로 세션을 만들고 커밋하면 이 규약을 이 함수만
  깨게 된다.
- `select_due_schedules`(U2)의 `FOR UPDATE ... SKIP LOCKED` 잠금과
  이 함수가 일정마다 여는 `begin_nested()` 세이브포인트는 **같은
  트랜잭션** 안에 있어야 한다 -- 세션 팩토리를 받아 그 안에서 새
  트랜잭션을 열면, 그 트랜잭션이 끝나는 시점(커밋 전/후)이 호출자의
  결정과 어긋날 수 있다. `ctx` 를 받으면 호출자가 연 트랜잭션을 그대로
  쓰므로 이 쟁점이 생기지 않는다.
- `app/memory/hooks.py::after_record(ctx, ...)` -- 같은 패키지(P6)
  안에서 "세이브포인트로 실패를 격리하고 롤백 뒤 바깥에서 오류 trace를
  남긴다"는 같은 역할을 하는 함수가 이미 `ctx` 를 받는 모양이다. 같은
  정신의 함수가 한쪽은 세션을, 다른 쪽은 팩토리를 받으면 두 계층의
  트랜잭션 경계 규약이 갈린다.
- 판정 표 3행("두 경로 모두 같은 `run_briefings` 객체를 부름")은 이
  모양으로도 그대로 성립한다 -- `trigger` 값만 다르게 넘기면 된다.

`session_factory`/`now` 인자를 받지 않으므로 "지금"은 `ctx.now()`(기존
`ctx.now` 주입 관례, `get_briefing`/`select_due_schedules` 와 같다)에서
얻는다.

## 실행 하나의 `session_id` (결정 I)

`agent_traces.session_id` 는 "그 판단이 속한 대화/실행"을 묶는 열쇠다
(원칙9 "session_id로 한 대화의 전체 판단 흐름을 재생"). 그런데 이
함수에 들어오는 `ctx` 의 `session_id` 는 호출자가 이미 다른 목적으로
채웠을 수 있다(API 요청 단위 임시 값, 주기 작업 루프가 매번 새로 만든
값 등) -- 그 값을 그대로 쓰면 "브리핑 실행 하나" 라는 경계가 호출자의
관례에 따라 들쭉날쭉해진다. 그래서 이 함수는 **자신만의**
`"briefing:<uuid4>"` 를 만들고, `dataclasses.replace(ctx, session_id=...)`
로 **파생 `ToolContext`**(`run_ctx`)를 만들어 내부에서 쓴다 -- 같은
`session`(DB 세션)·`user_id`·`now`·`embedder`·`confirmed_question_id`
는 그대로 공유하되, 이 실행이 남기는 모든 trace(`briefing_compose`가
부르는 `build_briefing_input`->`detect_patterns`/`get_briefing`의
기존 `memory_pattern`/`get_briefing` trace 포함)의 `session_id` 를
하나로 통일한다. `ctx`(호출자가 쥔 원본 객체)는 수정하지 않는다 --
`ToolContext` 는 frozen 이 아니므로 직접 대입도 가능하지만, 호출자가
같은 `ctx` 를 이 호출 뒤에도 다른 목적으로 쓸 수 있어(예: 같은 요청
안의 다른 처리) 부수효과를 피하려 `replace()` 로 새 객체를 쓴다.

**U6 추가** -- `BriefingRunResult.session_id` 에 `run_ctx.session_id` 를
그대로 담아 돌려준다. `POST /briefings/run`(U6)의 응답 `run_id` 가 이
값이어야 그 실행이 남긴 `briefing_run`/`briefing_compose` trace 를
사용자가 되짚을 수 있다(원칙9) -- U5 시점에는 테스트가 `tool_name`+
`step` 으로 trace 를 찾았으므로 이 필드가 없었다.

## `SQLAlchemyError` 처리 규약 (`app/memory/hooks.py::after_record` 와
## 같은 방식 -- 위임 프롬프트가 요구한 정렬)

일정 하나를 감싸는 `try` 는 두 단으로 나뉜다. `except SQLAlchemyError`:
세이브포인트는 이미 롤백됐으므로, **연결이 끊겼거나(`connection_
invalidated`) 세션이 더 쓸 수 없는 상태면** 그대로 올리고(바깥
`get_session()`/`session_scope()` 가 처리), 그 밖의 DB 오류(제약 위반·
SQL 오류 등)는 **이 일정만 격리**한다. `except Exception`: 공급자 밖
오류·`ToolError`·버그도 같은 방식으로 격리한다. 두 경우 모두 롤백이
끝난 뒤 바깥에서 `briefing_error` 1행을 쓴다.

**`after_record` 와 다른 이유(사용자 결정 2026-10-02, 판정 22행)**:
`after_record` 는 요청 하나 안에서 한 번 돌고 끝나지만, 이 함수는 1분
주기로 반복된다. 한 일정에서만 매번 나는 DB 오류를 올려 버리면 매분
실행 전체가 되돌려져 **다른 일정의 브리핑까지 영원히 막힌다**. 처음
구현은 `after_record` 를 따라 `SQLAlchemyError` 를 올렸고 테스트도
`RuntimeError` 로만 격리를 확인했다 -- 계획의 "DB 예외" 와 어긋나
메인 세션이 고쳤다. 판정 22행 테스트는 이제 실제 SQL 오류(`SELECT 1/0`)
로 트랜잭션을 깨뜨린 뒤에도 다음 일정이 진행되는지 확인한다.

## `stage` 어휘의 실제 범위 (01-plan 결정 I 어휘의 좁힌 구현)

01-plan 결정 I은 `briefing_error.output.stage` 를
`select|patterns|briefing|compose|notify` 5종으로 적었다. 이 모듈은
`build_briefing_input()`(U3, `app/briefing/inputs.py`)을 **수정하지
않고 한 번에 호출**하므로(그 함수 안의 "패턴 재계산"과 "`get_briefing`
호출" 두 단계를 run.py 가 구분해서 알 수 없다), 실제로 기록하는 값은
3종뿐이다: 그 호출 전체(패턴 재계산 + `get_briefing`)에서 실패하면
`"briefing"`, `composer.compose()`(스키마 파싱 포함, `JudgeUnavailable`
이외의 예외) 또는 trace 작성에서 실패하면 `"compose"`, `notifier.
notify()`에서 실패하면 `"notify"`. `select_due_schedules()`(U2) 자체의
실패(예: `schedule_id` 지정 모드의 `ScheduleNotFound`)는 일정별 루프
**밖**에서 일어나므로 세이브포인트로 격리할 "그 일정"이 아직 없다 --
이 함수는 그 예외를 그대로 올린다(호출자가 404 등으로 다룬다, U6 몫).
"""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import timedelta
from typing import Any, Literal

from sqlalchemy.exc import SQLAlchemyError

from app.briefing.compose import BriefingComposer, template_briefing, validate_briefing
from app.briefing.inputs import build_briefing_input
from app.briefing.select import select_due_schedules
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
    BriefingRunResult,
    NullNotifier,
    Notifier,
)
from app.db.models import AgentTrace
from app.er.types import JudgeUnavailable
from app.settings import BRIEFING_LEAD_HOURS
from app.tools.context import ToolContext

#: `briefing_error.output.stage` 어휘(모듈 docstring "stage 어휘" 절) --
#: 01-plan 5종 중 이 모듈이 실제로 구분할 수 있는 3종만 쓴다.
_STAGE_BRIEFING = "briefing"
_STAGE_COMPOSE = "compose"
_STAGE_NOTIFY = "notify"


def _record_briefing_error(
    ctx: ToolContext, *, schedule_id: int, person_id: int, stage: str, error: Exception
) -> None:
    """`briefing_error` trace 행 1개(결정 I). **세이브포인트 롤백이 끝난
    뒤** 바깥 트랜잭션에서만 부른다(`app/memory/hooks.py::
    _record_memory_error` 와 같은 자리 -- 안에서 쓰면 롤백과 함께
    사라진다). output 은 `{schedule_id, person_id, stage, error}` 뿐이다
    -- 프롬프트·공급자명·원문은 담지 않는다(security §1, `error` 는
    `type(error).__name__` 만)."""

    payload = {
        "schedule_id": schedule_id,
        "person_id": person_id,
        "stage": stage,
        "error": type(error).__name__,
    }
    ctx.session.add(
        AgentTrace(
            session_id=ctx.session_id,
            step=STEP_BRIEFING_ERROR,
            tool_name=BRIEFING_TRACE_TOOL_NAME,
            input={"schedule_id": schedule_id, "person_id": person_id, "stage": stage},
            output=payload,
            tokens_in=0,
            tokens_out=0,
        )
    )
    ctx.session.flush()


def run_briefings(
    ctx: ToolContext,
    *,
    composer: BriefingComposer,
    notifier: Notifier = NullNotifier(),  # noqa: B008 -- NullNotifier 는 필드
    # 없는 frozen dataclass(app/briefing/types.py) 라 공유돼도 안전하다(상태 없음).
    schedule_id: int | None = None,
    trigger: Literal["scheduler", "manual"],
    lead_hours: float = BRIEFING_LEAD_HOURS,
) -> BriefingRunResult:
    """대상 선정(U2) -> 일정마다 세이브포인트로 감싸 입력 조립(U3) ->
    생성(U4, 실패 시 템플릿 대체) -> 푸시 자리(결정 J) ->
    `briefing_compose` trace 1행을 남기고, 실행 끝에 `briefing_run`
    trace 1행을 남긴다(모듈 docstring 참고). 커밋은 호출자 몫이다 --
    이 함수는 `ctx.session.flush()` 까지만 한다.
    """

    run_ctx = replace(ctx, session_id=f"briefing:{uuid.uuid4()}")
    now = run_ctx.now()

    schedules = select_due_schedules(run_ctx, lead_hours=lead_hours, schedule_id=schedule_id)
    selected_ids = [schedule.id for schedule in schedules]

    briefings: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    briefed_ids: list[int] = []
    errors = 0

    for schedule in schedules:
        person_id = schedule.person_id
        stage = _STAGE_BRIEFING
        try:
            with run_ctx.session.begin_nested():
                briefing_input = build_briefing_input(run_ctx, schedule)

                stage = _STAGE_COMPOSE
                fallback_reason: str | None = None
                try:
                    raw = composer.compose(briefing_input)
                except JudgeUnavailable as exc:
                    # 결정 D -- 생성기 오류면 템플릿으로 대체한다.
                    # briefed_at 은 build_briefing_input() 이 이미
                    # 기록했고, 이 분기는 세이브포인트를 되돌리지 않으므로
                    # 그대로 남는다.
                    composed = template_briefing(briefing_input)
                    rejected: list[dict[str, Any]] = []
                    composer_name = "template"
                    fallback_reason = str(exc)
                else:
                    composed, rejected = validate_briefing(briefing_input, raw)
                    composer_name = "llm"

                stage = _STAGE_NOTIFY
                push_status = notifier.notify(schedule, composed)

                stage = _STAGE_COMPOSE
                tokens_in, tokens_out = composed.trace_tokens()
                compose_output: dict[str, Any] = {
                    "schedule_id": schedule.id,
                    "person_id": person_id,
                    "pattern_trace_id": briefing_input.pattern_trace_id,
                    "used_facts": [
                        {
                            "key": fact["key"],
                            "fact_id": fact["fact_id"],
                            "eligible": fact["eligible"],
                        }
                        for fact in briefing_input.used_facts
                    ],
                    "excluded_facts": [
                        {
                            "key": fact["key"],
                            "fact_id": fact["fact_id"],
                            "reason": fact["reason"],
                        }
                        for fact in briefing_input.excluded_facts
                    ],
                    "event_ids": [event["id"] for event in briefing_input.recent_events],
                    "composer": composer_name,
                    "pattern_sentences": composed.pattern_sentences,
                    "lines": [line.to_dict() for line in composed.lines],
                    "suggestion": (
                        composed.suggestion.to_dict() if composed.suggestion is not None else None
                    ),
                    "rejected": rejected,
                    "llm": {"provider": composed.provider, "model": composed.model},
                    "push": push_status,
                }
                if fallback_reason is not None:
                    compose_output["fallback_reason"] = fallback_reason

                run_ctx.session.add(
                    AgentTrace(
                        session_id=run_ctx.session_id,
                        step=STEP_BRIEFING_COMPOSE,
                        tool_name=BRIEFING_TRACE_TOOL_NAME,
                        input={"schedule_id": schedule.id, "person_id": person_id},
                        output=compose_output,
                        tokens_in=tokens_in,
                        tokens_out=tokens_out,
                    )
                )
                run_ctx.session.flush()
        except SQLAlchemyError as exc:
            # 모듈 docstring "SQLAlchemyError 처리 규약" -- 세이브포인트는
            # `with` 를 빠져나오며 이미 롤백됐다. 연결 자체가 끊겼으면 더
            # 진행할 수 없으므로 올리고(바깥 get_session()/session_scope()
            # 가 처리), 그 밖의 DB 오류는 이 일정만 격리한다 -- 한 일정의
            # 반복 DB 오류가 매분 나머지 일정까지 막지 않게(사용자 결정
            # 2026-10-02, 판정 22행).
            if getattr(exc, "connection_invalidated", False) or not run_ctx.session.is_active:
                raise
            errors += 1
            _record_briefing_error(
                run_ctx, schedule_id=schedule.id, person_id=person_id, stage=stage, error=exc
            )
            skipped.append({"schedule_id": schedule.id, "reason": type(exc).__name__})
            continue
        except Exception as exc:  # noqa: BLE001 -- 의도적으로 넓게 잡는다(세이브포인트 격리)
            errors += 1
            _record_briefing_error(
                run_ctx, schedule_id=schedule.id, person_id=person_id, stage=stage, error=exc
            )
            skipped.append({"schedule_id": schedule.id, "reason": type(exc).__name__})
            continue

        briefed_ids.append(schedule.id)
        briefings.append(
            {
                "schedule_id": schedule.id,
                "person_id": person_id,
                "composer": composer_name,
                "pattern_sentences": composed.pattern_sentences,
                "lines": [line.to_dict() for line in composed.lines],
                "suggestion": (
                    composed.suggestion.to_dict() if composed.suggestion is not None else None
                ),
                "push": push_status,
            }
        )

    window_end = now + timedelta(hours=lead_hours)
    run_output: dict[str, Any] = {
        "trigger": trigger,
        "now": now.isoformat(),
        "window": {"from": now.isoformat(), "to": window_end.isoformat()},
        "lead_hours": lead_hours,
        "schedule_id_arg": schedule_id,
        "selected": selected_ids,
        "skipped": skipped,
        "briefed": briefed_ids,
        "errors": errors,
    }
    run_ctx.session.add(
        AgentTrace(
            session_id=run_ctx.session_id,
            step=STEP_BRIEFING_RUN,
            tool_name=BRIEFING_TRACE_TOOL_NAME,
            input={"trigger": trigger, "schedule_id": schedule_id, "lead_hours": lead_hours},
            output=run_output,
            tokens_in=0,
            tokens_out=0,
        )
    )
    run_ctx.session.flush()

    return BriefingRunResult(
        trigger=trigger,
        now=now,
        session_id=run_ctx.session_id,
        briefings=briefings,
        skipped=skipped,
        errors=errors,
    )
