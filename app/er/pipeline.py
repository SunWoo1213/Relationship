"""Refs: P3-er S3.3 D3 D10 R4 R9 결정1 결정3-b 결정3-c 결정4 결정5 결정8
원칙1 원칙4 원칙9 -- 오케스트레이션(`resolve()`, U6) + 실행(`apply_resolution()`,
U7).

## `resolve()` 가 하는 일 (4단계 그대로, 하드코딩된 파이프라인이 아니다)

1. **후보 검색**(`app/er/candidates.py.search_candidates`) -- `search_person`
   재사용 + `hints` 유도(호출자가 안 주면 사전에서). 유도 결과(`effective_hints`)
   는 2단계·trace 양쪽에 **그대로** 재사용한다(U5 인계 (1) -- 다시 유도하지
   않는다).
2. **규칙 필터**(`app/er/rules.py.run_rule_stage`) -- 엄격 적용 → (필요하면)
   완화 1회 재평가. `passed`(통과 후보만)와 `all_scored`(배제 포함 전체)를
   구분해 받는다(U5 인계 (2) -- `decide()`/LLM 에는 `passed`, trace
   `candidates[]` 에는 `all_scored`).
3. **LLM 판정**(`app/er/judge.py.Judge.judge`) -- **통과 후보가 0건이면
   호출하지 않는다**(01-plan 34행 "규칙 통과 후보 0건 최적화", 원칙8 비용
   회피). `JudgeUnavailable` 은 여기서 잡아 `llm_failed=True` 로 흡수한다
   (원칙1 "실패는 죽는 것이 아니라 묻는 것").
4. **확신도 분기**(`app/er/confidence.py.decide`) -- 가중합·두 임계치·
   강제 강등 세 갈래(`no_candidates`/`llm_failed`/`no_matched`)를 전부
   이 함수 하나에 위임한다(이중 출처 금지, 로직 재구현 없음).

이 함수는 **부수효과가 없다**(결정4) -- `persons`/`person_aliases`/
`pending_questions` 에 쓰지 않는다. `ask_user` 페이로드는 여기서 **만들기만**
하고 `Resolution.ask_payload` 에 담아 돌려준다 -- 저장은 `apply_resolution`
(U7)의 몫이다.

## trace 행은 1개 (결정5)

`@traced(ER_TRACE_TOOL_NAME, step=ER_TRACE_STEP)` 로 감싼 내부 함수
(`_traced_pipeline`)가 `app.tools.context.to_jsonable`·문자열 절단·예외
경로를 툴과 같은 한 곳에서 재사용한다(관측 규약 이중 출처 금지, 01-plan
31행). 감싸인 함수의 시그니처에는 **`judge` 를 넣지 않는다** -- `@traced`
는 `ctx` 를 뺀 인자 전부를 `input` 으로 자동 기록하므로, `judge`(콜러블/
클라이언트 객체, JSON 으로 의미 있게 직렬화되지 않고 결정5 trace 입력
스키마에도 없다)를 인자로 두면 원치 않는 값이 `input` 에 섞인다. 대신
`resolve()` 가 클로저로 `judge` 를 감싼 새 함수를 매 호출마다 만들어
넘긴다 -- `judge` 는 그 클로저 안에서만 쓰이고 `inspect.signature` 에
드러나지 않는다.

`Resolution.trace_id` 는 `@traced` 가 flush 후 `ctx.last_trace_id` 에 남긴
값을 `resolve()` 가 읽어 채운다(`app/tools/context.py` "trace 행 id 회수"
절, U6 이 넣은 최소 확장). `Resolution` 은 frozen dataclass 이므로
`dataclasses.replace()` 로 새 인스턴스를 만든다 -- `object.__setattr__` 로
제자리 수정하지 않는다.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from sqlalchemy.orm.attributes import flag_modified

from app.db.models import AgentTrace
from app.er.candidates import search_candidates
from app.er.confidence import decide
from app.er.judge import Judge, JudgeUnavailable, judge_from_env
from app.er.rules import run_rule_stage
from app.er.types import (
    ER_TRACE_STEP,
    ER_TRACE_TOOL_NAME,
    AlreadyApplied,
    AppliedResolution,
    ERConfig,
    Resolution,
    ScoredCandidate,
)
from app.settings import er_config
from app.tools.context import ToolContext, traced
from app.tools.persons import update_person
from app.tools.questions import ask_user
from app.tools.types import AFFIRMATIVE_KEY, InvalidValue

#: identity 질문 옵션에 담을 후보 표시 이름 최대 개수(결정4).
_MAX_IDENTITY_OPTIONS = 3

_IDENTITY_REJECT_OPTION = "아니요, 다른 사람이에요"
_NEW_PERSON_CONFIRM_OPTION = "네, 기억해둘게요"
_NEW_PERSON_REJECT_OPTION = "아니요"


def _build_ask_payload(
    *,
    band: str,
    passed: list[ScoredCandidate],
    mention: str,
    utterance: str,
    confidence_breakdown: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """`ask_user` 에 그대로 넘길 수 있는 페이로드를 **만들기만** 한다(결정4
    -- 저장은 `apply_resolution`, U7). `ask_payload["context"]` 는
    `app.tools.questions.ask_user` 가 요구하는 `AFFIRMATIVE_KEY`(F-b97a06)
    를 이미 채운 채로 돌려준다 -- U7 이 그대로 splat 해 호출할 수 있게.

    반환값 `(ask_payload, suggested_display_name)`:
    - `band == "merge"`: `ask_payload=None`, `suggested_display_name` 은
      귀속된 후보의 `display_name`(결정3-b -- merge 는 별칭만 누적하고
      표시 이름은 확인 후에만 바꾼다).
    - `band == "identity"`: 후보 표시 이름 최대 3개(±`s_emb` 내림차순, 동점은
      `person_id` 로 결정적 정렬) + 거절 문구를 `options` 로, 후보 이름만
      `affirmative_options`/`context[AFFIRMATIVE_KEY]` 로 담는다.
      `context.candidate_ids` 는 이름→id 매핑(P2 04-review §7 이 남긴
      "질문이 인물에 안 묶인다"는 구멍을 P5 가 메울 재료).
    - `band == "new_person"`: 후보 나열 없이 `mention` 하나로 새 인물 생성
      여부를 묻는다(D1 "승인 시에만 create_person").
    """

    if band == "merge":
        matched_person_id = confidence_breakdown.get("matched_person_id")
        matched = next((c for c in passed if c.person_id == matched_person_id), None)
        suggested_display_name = matched.display_name if matched is not None else None
        return None, suggested_display_name

    if band == "identity":
        top = sorted(passed, key=lambda c: (-c.s_emb, c.person_id))[:_MAX_IDENTITY_OPTIONS]
        names = [c.display_name for c in top]
        candidate_ids = {c.display_name: c.person_id for c in top}
        options = list(names) + [_IDENTITY_REJECT_OPTION]
        context = {
            "mention": mention,
            "utterance": utterance,
            "candidate_ids": candidate_ids,
            "confidence_breakdown": dict(confidence_breakdown),
            AFFIRMATIVE_KEY: list(names),
        }
        names_text = "/".join(names) if names else mention
        question = f'"{mention}" -- {names_text} 중 한 분이 맞으실까요?'
        ask_payload = {
            "kind": "identity",
            "question": question,
            "options": options,
            "affirmative_options": list(names),
            "context": context,
        }
        return ask_payload, None

    # band == "new_person"
    context = {
        "mention": mention,
        "utterance": utterance,
        "candidate_ids": {},
        "confidence_breakdown": dict(confidence_breakdown),
        AFFIRMATIVE_KEY: [_NEW_PERSON_CONFIRM_OPTION],
    }
    ask_payload = {
        "kind": "new_person",
        "question": f'"{mention}"을(를) 새 인물로 기억해둘까요?',
        "options": [_NEW_PERSON_CONFIRM_OPTION, _NEW_PERSON_REJECT_OPTION],
        "affirmative_options": [_NEW_PERSON_CONFIRM_OPTION],
        "context": context,
    }
    return ask_payload, None


def _run_pipeline(
    ctx: ToolContext,
    mention: str,
    utterance: str,
    hints: dict[str, str] | None,
    config: ERConfig,
    judge: Judge,
) -> Resolution:
    """4단계 순서 그대로(원칙4). DB 쓰기 없음(결정4) -- `search_candidates`
    가 부르는 `search_person` 자체의 `tool_call` trace 행만 별도로 남는다
    (결정5 "내부에서 부른 search_person 의 tool_call 행은 그대로 별도로
    남는다")."""

    search_result = search_candidates(ctx, mention, hints, top_k=config.top_k)
    effective_hints = search_result.hints

    passed, all_scored, relaxed_retry = run_rule_stage(
        search_result.candidates, effective_hints
    )

    judgement = None
    llm_failed = False
    llm_error: str | None = None
    llm_skipped = not passed
    attempts = 0

    if not llm_skipped:
        attempts = 1
        try:
            judgement = judge.judge(mention, utterance, passed)
        except JudgeUnavailable as exc:
            llm_failed = True
            llm_error = str(exc)

    decision = decide(judgement=judgement, passed=passed, llm_failed=llm_failed, config=config)

    llm_payload: dict[str, Any] = {
        "provider": judgement.provider if judgement is not None else None,
        "model": judgement.model if judgement is not None else None,
        "self_reported": True,
        "s_llm": judgement.s_llm if judgement is not None else 0.0,
        "reason": judgement.reason if judgement is not None else None,
        "tokens_in": judgement.tokens_in if judgement is not None else 0,
        "tokens_out": judgement.tokens_out if judgement is not None else 0,
        "attempts": attempts,
        "skipped": llm_skipped,
        "error": llm_error,
    }

    decision_payload = dict(decision.decision)
    decision_payload["relaxed_retry"] = relaxed_retry
    decision_payload["hierarchy_relaxed_retry"] = relaxed_retry
    decision_payload["applied"] = False
    decision_payload["pending_question_id"] = None
    decision_payload["applied_at"] = None

    ask_payload, suggested_display_name = _build_ask_payload(
        band=decision.band,
        passed=passed,
        mention=mention,
        utterance=utterance,
        confidence_breakdown=decision.confidence_breakdown,
    )

    return Resolution(
        trace_id=None,
        mention=mention,
        candidates=all_scored,
        relaxed_retry=relaxed_retry,
        matched_person_id=decision.matched_person_id,
        confidence=decision.confidence,
        confidence_breakdown=decision.confidence_breakdown,
        band=decision.band,
        band_by_threshold=decision.band_by_threshold,
        forced_reason=decision.forced_reason,
        decision=decision_payload,
        llm=llm_payload,
        ask_payload=ask_payload,
        suggested_display_name=suggested_display_name,
    )


def resolve(
    ctx: ToolContext,
    mention: str,
    utterance: str,
    hints: dict[str, str] | None = None,
    *,
    judge: Judge | None = None,
    config: ERConfig | None = None,
) -> Resolution:
    """S3.3/CLAUDE.md 시그니처 v2: `(ctx, mention, utterance, hints=None, *,
    judge=None, config=None) -> Resolution`. **부수효과 없음**(결정4).

    `config` 가 `None` 이면 `er_config()`(환경변수 오버라이드 포함, 결정8
    2층)를 쓴다. `judge` 가 `None` 이면 `judge_from_env()`(01-plan 결정3
    개정2, 공급자 팩토리)를 쓴다 -- 회귀 테스트는 `judge=FakeJudge(...)` 를
    직접 주입해 실 API 호출 없이 결정적으로 돈다(결정9).

    trace 행 1개(`step=ER_TRACE_STEP`, `tool_name=ER_TRACE_TOOL_NAME`)를
    `agent_traces` 에 남기고, 그 행의 id 를 `Resolution.trace_id` 로 채워
    돌려준다(모듈 docstring 참고).
    """

    resolved_config = config if config is not None else er_config()
    resolved_judge = judge if judge is not None else judge_from_env()

    @traced(ER_TRACE_TOOL_NAME, step=ER_TRACE_STEP)
    def _traced_pipeline(
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None,
        config: ERConfig,
    ) -> Resolution:
        return _run_pipeline(ctx, mention, utterance, hints, config, resolved_judge)

    result = _traced_pipeline(ctx, mention, utterance, hints, resolved_config)
    return replace(result, trace_id=ctx.last_trace_id)


def _load_trace_row(ctx: ToolContext, trace_id: int) -> AgentTrace:
    """`resolution.trace_id` 가 가리키는 `er_resolve` 행을 조회한다.
    없으면(잘못된 `trace_id`, 롤백된 트랜잭션 등) `InvalidValue` -- 존재를
    가정하고 조용히 `None` 필드로 진행하지 않는다(원칙8)."""

    row = ctx.session.get(AgentTrace, trace_id)
    if row is None:
        raise InvalidValue(
            f"apply_resolution: agent_traces row {trace_id!r} not found"
        )
    output = row.output
    decision = output.get("decision") if isinstance(output, dict) else None
    if not isinstance(decision, dict):
        raise InvalidValue(
            "apply_resolution: agent_traces row output.decision missing or malformed"
        )
    return row


def apply_resolution(ctx: ToolContext, resolution: Resolution) -> AppliedResolution:
    """`Resolution`(U6 `resolve()`) 이 정한 행동을 **실제로 실행**한다
    (결정4 -- 판정과 실행 분리). `resolve()` 는 부수효과가 없었으므로,
    `persons`/`person_aliases`/`pending_questions` 를 실제로 바꾸는 것은
    이 함수뿐이다.

    ## 경로별 동작

    - `band == "merge"`: `update_person(ctx, person_id=resolution.
      matched_person_id, new_alias=resolution.mention)` 로 **별칭만
      누적**한다 -- `display_name` 은 바꾸지 않는다(결정3-b, D6). 이미
      같은 별칭 문자열이 있으면 `app/tools/persons.py._add_alias` 의
      기존 upsert(격상) 규약을 그대로 따르며 예외를 던지지 않는다.
      `pending_question_id=None`.
    - `band in {"identity", "new_person"}`: `ask_user(ctx, kind=..., question=
      ..., options=..., context=...)` 로 U6 이 만든 `ask_payload` 의 `kind`/
      `question`/`options`/`context` 를 **그대로** 저장한다(재구성 없음) ->
      `pending_question_id`. **계획과 다르게 한 것**: 01-plan 은 `ask_user(ctx,
      **resolution.ask_payload)` 로 페이로드 전체를 그대로 splat 하라고
      적었으나, U6 이 만든 `ask_payload` 에는 `ask_user` 의 시그니처
      (`kind, question, options, context`)에 없는 `affirmative_options`
      키가 최상위에도 함께 있다(`app.tools.questions.ask_user` 가 요구하는
      값은 `context[AFFIRMATIVE_KEY]` 뿐 -- U6 테스트(`-k identity_payload`)
      가 이미 이 최상위 키를 단언하므로 U6 쪽 스키마를 바꾸지 않는다,
      "재계산 금지 — 읽기만 한다"). 그래서 여기서는 `ask_user` 가 실제로
      받는 4개 키만 뽑아 넘긴다 -- `kind`/`question`/`options`/`context`
      값 자체는 전혀 가공하지 않는다(03-log U7 항목에 기록).

    ## trace 부분 갱신 (결정4 "trace 행의 갱신 주체", F-93f063)

    실행 뒤 `resolution.trace_id` 가 가리키는 **같은** `er_resolve` 행의
    `output["decision"]` 안 `applied`/`pending_question_id`/`applied_at`
    **세 키만** 바꾼다. 갱신 수단은 (a) 조회한 ORM 객체의 `output` dict 를
    제자리에서 수정한 뒤 `sqlalchemy.orm.attributes.flag_modified(row,
    "output")` 로 변경 추적을 강제하는 것 -- (b) 원시 `UPDATE ... SET
    output = jsonb_set(...)` 대안도 있었으나, ORM 이 이미 같은 행을 들고
    있는 이 경로(같은 세션, 같은 요청 트랜잭션)에서는 (a) 가 SQL 문자열을
    새로 조립하지 않고 기존 `to_jsonable`/`AgentTrace` 계약을 그대로 쓸 수
    있어 더 단순하다(원시 SQL 은 JSONB 안의 임의 depth 를 다시 손으로
    지정해야 한다). `MutableDict`(모델 컬럼 정의 변경)는 스키마/모델 변경
    없이 이 단위를 끝내기 위해 채택하지 않았다(01-plan "스키마 변경 없음").
    `flag_modified` 없이 dict 를 제자리에서 바꾸기만 하면 SQLAlchemy 의
    변경 추적이 JSONB 컬럼의 in-place mutation 을 감지하지 못해 `flush()`
    가 아무것도 UPDATE 하지 않는다(F-93f063 증상 그대로) -- 그래서 이
    호출이 반드시 필요하다. `candidates[]`/`confidence_breakdown`/`llm`/
    `band`/`band_by_threshold`/`forced_reason` 은 건드리지 않는다(판정
    필드 불변, 전체 재기록 금지).

    ## 중복 호출 거부 (F-8809f2)

    같은 `Resolution`(같은 `trace_id`)으로 두 번째 호출하면, 첫 번째
    호출이 이미 `decision["applied"] = True` 로 갱신해 두었으므로
    `AlreadyApplied` 를 던지고 **아무것도 쓰지 않는다** -- `ask_user`/
    `update_person` 을 다시 부르지 않는다(identity/new_person 경로가
    `pending_questions` 행을 하나 더 만들거나 `person_aliases` 를 다시
    upsert 하는 것을 막는다, 03-log U7 "거부(예외)" 채택).

    커밋하지 않는다 -- `flush()` 까지만(호출자 트랜잭션, 01-plan 결정2와
    같은 툴 규약).
    """

    if resolution.trace_id is None:
        raise InvalidValue("apply_resolution: resolution.trace_id is required")

    trace_row = _load_trace_row(ctx, resolution.trace_id)
    decision_json = trace_row.output["decision"]

    if decision_json.get("applied") is True:
        raise AlreadyApplied(
            f"apply_resolution: trace {resolution.trace_id!r} was already applied"
        )

    action = resolution.decision.get("action")
    person_id: int | None = None
    pending_question_id: int | None = None
    alias_added = False

    if resolution.band == "merge":
        if resolution.matched_person_id is None:
            raise InvalidValue(
                "apply_resolution: band='merge' requires matched_person_id"
            )
        update_person(
            ctx,
            person_id=resolution.matched_person_id,
            new_alias=resolution.mention,
        )
        person_id = resolution.matched_person_id
        alias_added = True
    else:
        if not resolution.ask_payload:
            raise InvalidValue(
                f"apply_resolution: band={resolution.band!r} requires ask_payload"
            )
        payload = resolution.ask_payload
        question = ask_user(
            ctx,
            kind=payload["kind"],
            question=payload["question"],
            options=payload["options"],
            context=payload["context"],
        )
        pending_question_id = question.question_id

    applied_at = ctx.now()

    decision_json["applied"] = True
    decision_json["pending_question_id"] = pending_question_id
    decision_json["applied_at"] = applied_at.isoformat()
    flag_modified(trace_row, "output")
    ctx.session.flush()

    return AppliedResolution(
        trace_id=resolution.trace_id,
        band=resolution.band,
        action=action,
        person_id=person_id,
        pending_question_id=pending_question_id,
        applied_at=applied_at,
        alias_added=alias_added,
    )
