"""Refs: P5-loop D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4 -- U4 해석 단계
(`resolve_mentions()`).

## 이 단위가 채우는 자리, 채우지 않는 자리

`app/agent/loop.py` 는 오케스트레이션(`run_turn`/`resume_turn`)의 최종
자리이지만, 이 단위(U4)는 **해석 구간**만 채운다. 게이트를 통과한 제안이
가리키는 언급마다 `app.er.resolve()` -> `app.er.apply_resolution()` 을
불러 기존 인물에 연결하거나(merge) 되묻는다(identity/new_person). 이
파일에 `run_turn`/`resume_turn` 이라는 이름은 아직 없다 -- 그 이름을
만들면 기록(U5)·응답(U5)·재개(U7)가 채우지 못한 자리까지 이 단위가
약속한 것으로 오인될 수 있다. 공개 진입점은 `resolve_mentions()` 하나뿐
이고, U5 는 이 함수를 기록 단계 앞에서 그대로 불러 쓴다(반환값
`ResolveOutcome.person_ids` 로 확정된 `person_id` 를 받아 `args["person"]`
자리를 치환한다).

## 이 모듈이 하지 않는 것 (원칙1·2·4, 판정 표 6·19·23행)

- 확신도·두 임계치를 읽지도 비교하지도 않는다 -- `app.er.resolve()` 가
  이미 내린 `band`(merge/identity/new_person) 만 본다. 이 파일 어디에도
  임계치·확신도를 가리키는 영어 어휘를 쓰지 않는다(설명이 필요하면
  한국어 "확신도"로 쓴다). `resolve()` 가 만든 판정 근거(`ask_payload
  ["context"]` 안의 값)는 **키 이름을 적지 않고** 통째로 옮겨 담는다
  (`{**payload["context"], ...}`) -- 어떤 값이 들어 있는지 이 파일이
  검사하지 않는다.
- `create_person`/`update_person` 을 직접 부르지 않는다 -- `merge` 경로의
  별칭 누적은 `apply_resolution()` 안에서 `update_person` 이 대신
  불린다. `create_person` 은 재개 경로(U7)에서, 답한 `new_person` 질문과
  함께만 실행된다(D1). 이 파일 소스에는 이 두 이름을 여는 괄호와 함께
  적은 호출문 표기가 없다(판정 표 5a·5b -- U4 는 이 두 툴을 부르지
  않는다).
- `pending_questions` 를 직접 쓰지 않는다 -- `context` 를 확장하는 유일한
  길은 `dataclasses.replace(resolution, ask_payload=...)` 뒤
  `apply_resolution()` -> `ask_user` 뿐이다(판정 표 23행). 이 파일은 대기
  질문 ORM 모델을 import 하지 않는다(그 이름 자체도 이 파일 어디에도
  쓰지 않는다, 판정 표 23행 grep 대상).

## R-25 (이 단위에서 정한다, 02-plan-verify 211행)

**(ㄱ) `create_person`(hint_only) 힌트가 어느 언급에 붙는가.** 게이트가
`hint_only` 로 통과시킨 `create_person` 제안의 `relation_tag`/`hierarchy`
는, 그 제안의 `args["display_name"]` 또는 `args["aliases"]` 안에 언급
문자열과 **글자 그대로 같은 값**이 있을 때만 그 언급의 힌트로 쓴다
(`_match_create_person_hints`). 부분 일치·유사도 매칭은 오귀속(다른
사람의 태그가 엉뚱한 언급에 붙는 것) 위험이 있어 쓰지 않는다. 이미
힌트가 붙은 언급에는 먼저 매칭된 제안만 쓰고, 어느 언급과도 매칭되지
않는 제안은 조용히 버려진다 -- `create_person` 자체가 `hint_only` 라
실행되지 않으므로(D1) 버려져도 데이터 손실이 없고, 힌트가 없으면
`resolve()` 가 스스로 사전 기반으로 힌트를 유도한다(`hints=None`).

**(ㄴ) `held_drafts` 와 `pending_calls` 의 구분.** `pending_calls` 는
재개(U7)가 그대로 재실행할 근거(제안 인덱스·이름·인자)이고, 절대
버리지 않는다. `held_drafts` 는 그것과 **다른** 정보다 -- 사람이 읽는
미리보기(`content`/`title` 앞 200자)뿐이고 재실행에는 쓰이지 않는다
(`_preview_drafts`). `LOOP_MAX_RESUME_BYTES` 를 넘으면 `held_drafts` 만
통째로 비우고 `dropped` 에 버린 개수를 남긴다 -- `pending_calls` 는
그대로 두므로 재개 자체는 깨지지 않는다(01-plan 83행 마지막 문장).

## 순차 처리와 첫 되묻기에서 턴 종료 (결정 C(i)·D(i))

언급을 처음 등장한 순서대로 하나씩 해석한다. `merge` 면 `person_id` 를
확정하고 다음 언급으로 넘어간다 -- 이미 확정된 언급에 딸린 제안은
기록 단계(U5)가 이 함수가 돌려준 `person_ids` 맵으로 바로 실행하므로
재개 재료(`pending_calls`)에 담지 않는다(결정 D(i) "확정분은 그대로
저장, 미확정분만 보류"). `identity`/`new_person` 이 나오면 그 언급과
그 뒤로 아직 손대지 않은 모든 언급의 제안을 `pending_calls` 로 묶어
그 자리에서 턴을 끝낸다(결정 C(i)) -- 이후 언급은 아예 `resolve()` 를
부르지도 않는다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from typing import Any

from app.agent.types import (
    BUCKET_EXECUTE,
    BUCKET_HINT_ONLY,
    NEW_PERSON_TAG_OPTIONS,
    STEP_LOOP_RESOLVE_DONE,
    LOOP_TRACE_TOOL_NAME,
    GateVerdict,
    PendingCall,
    PendingResume,
    Proposal,
)
from app.db.models import HIERARCHIES, RELATION_TAGS
from app.er import ERConfig, Judge, Resolution, apply_resolution, resolve
from app.settings import LOOP_MAX_RESUME_BYTES
from app.tools.context import ToolContext, to_jsonable, traced
from app.tools.types import AFFIRMATIVE_KEY

# ---------------------------------------------------------------------------
# 해석 구간 산출물 -- `run_turn`(U5)이 기록 단계를 이어가는 재료
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MentionDecision:
    """언급 하나의 해석 결과 요약(`loop_resolve_done.output.decisions[]`).

    `resolution` 은 이 파일 밖(향후 U5·테스트)이 같은 `Resolution` 으로
    `app.er.apply_resolution()` 을 다시 부를 수 있게 남겨 두는 참조용
    필드다 -- `to_dict()` 에는 담지 않는다(그 전체 내용은 이미 `er_resolve`
    trace 행에 있다, 이중 출처 금지). `trace_id` 로 그 행을 가리킨다."""

    mention: str
    index: int
    band: str
    person_id: int | None = None
    pending_question_id: int | None = None
    trace_id: int | None = None
    resolution: Resolution | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mention": self.mention,
            "index": self.index,
            "band": self.band,
            "person_id": self.person_id,
            "pending_question_id": self.pending_question_id,
            "trace_id": self.trace_id,
        }


@dataclass(frozen=True)
class ResolveOutcome:
    """`resolve_mentions()` 반환값 -- `loop_resolve_done.output` 스키마.

    `person_ids`: `merge` 로 확정된 언급 -> `person_id`(기록 단계가
    `args["person"]` 자리를 이 값으로 치환한다). `stopped=True` 면
    되묻기로 이 턴이 끝났다는 뜻(결정 C(i)) -- `pending_question_id` 가
    채워지고, 아직 손대지 않은 언급은 아예 `resolve()` 를 타지 않았다.
    """

    person_ids: dict[str, int] = field(default_factory=dict)
    decisions: list[MentionDecision] = field(default_factory=list)
    stopped: bool = False
    pending_question_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_ids": dict(self.person_ids),
            "decisions": [d.to_dict() for d in self.decisions],
            "stopped": self.stopped,
            "pending_question_id": self.pending_question_id,
        }


# ---------------------------------------------------------------------------
# 언급 목록 + create_person 힌트 매칭 (R-25 (ㄱ))
# ---------------------------------------------------------------------------


def _ordered_mentions(
    proposal: Proposal, verdict: GateVerdict
) -> tuple[list[str], dict[str, int]]:
    """`accepted`(`execute` 버킷) 안의 서로 다른 `person` 언급을 처음
    등장한 순서대로 모은다(결정 C(i) "순차 처리"). 둘째 반환값은 언급 ->
    그 언급이 처음 나타난 `tool_calls[]` 인덱스(관측성 표시용,
    `MentionDecision.index`)."""

    mentions: list[str] = []
    first_index: dict[str, int] = {}
    for accepted in verdict.accepted:
        if accepted.bucket != BUCKET_EXECUTE:
            continue
        mention = proposal.tool_calls[accepted.index].args.get("person")
        if not isinstance(mention, str) or not mention:
            continue
        if mention not in first_index:
            first_index[mention] = accepted.index
            mentions.append(mention)
    return mentions, first_index


def _match_create_person_hints(
    proposal: Proposal, verdict: GateVerdict, mentions: list[str]
) -> dict[str, dict[str, str]]:
    """R-25 (ㄱ) -- `create_person`(`hint_only`) 제안의 `relation_tag`/
    `hierarchy` 를 어느 언급에 붙일지 정한다(모듈 docstring 참고).
    반환값에 없는 언급은 힌트가 없다는 뜻이고, `resolve_mentions` 는 그
    언급을 `hints=None` 으로 넘겨 ER 의 사전 기반 유도에 맡긴다."""

    mention_set = set(mentions)
    matched: dict[str, dict[str, str]] = {}
    for accepted in verdict.accepted:
        if accepted.bucket != BUCKET_HINT_ONLY:
            continue
        args = proposal.tool_calls[accepted.index].args

        names: set[str] = set()
        display_name = args.get("display_name")
        if isinstance(display_name, str):
            names.add(display_name)
        for alias in args.get("aliases") or []:
            if isinstance(alias, str):
                names.add(alias)

        target = next((m for m in mentions if m in names and m in mention_set), None)
        if target is None or target in matched:
            continue

        hint: dict[str, str] = {}
        relation_tag = args.get("relation_tag")
        if relation_tag in RELATION_TAGS:
            hint["relation_tag"] = relation_tag
        hierarchy = args.get("hierarchy")
        if hierarchy in HIERARCHIES:
            hint["hierarchy"] = hierarchy
        if hint:
            matched[target] = hint
    return matched


# ---------------------------------------------------------------------------
# 되묻기 재료 -- `pending_calls`(재실행 근거)·`held_drafts`(버려도 되는 미리보기)
# ---------------------------------------------------------------------------


def _pending_calls_from(
    proposal: Proposal, verdict: GateVerdict, resolved_mentions: set[str]
) -> list[PendingCall]:
    """게이트를 통과했지만(`execute` 버킷) 아직 `person_id` 가 확정되지
    않은 언급에 딸린 제안 -- 첫 되묻기 시점까지 `merge` 로 확정된 언급
    (`resolved_mentions`)은 기록 단계(U5)가 `person_ids` 맵으로 바로
    실행하므로 여기 담지 않는다(결정 D(i))."""

    calls: list[PendingCall] = []
    for accepted in verdict.accepted:
        if accepted.bucket != BUCKET_EXECUTE:
            continue
        args = proposal.tool_calls[accepted.index].args
        mention = args.get("person")
        if isinstance(mention, str) and mention in resolved_mentions:
            continue
        calls.append(PendingCall(index=accepted.index, name=accepted.name, args=dict(args)))
    return calls


_PREVIEW_FIELDS: tuple[str, ...] = ("content", "title")


def _preview_drafts(pending_calls: list[PendingCall]) -> list[dict[str, Any]]:
    """R-25 (ㄴ) -- `held_drafts`: 사람이 읽는 보조 요약뿐이고 재실행에는
    쓰이지 않는다(모듈 docstring 참고)."""

    drafts: list[dict[str, Any]] = []
    for call in pending_calls:
        preview: dict[str, Any] = {"name": call.name}
        for key in _PREVIEW_FIELDS:
            value = call.args.get(key)
            if isinstance(value, str):
                preview[key] = value[:200]
        drafts.append(preview)
    return drafts


def _apply_resume_byte_limit(resume: PendingResume, *, limit: int) -> PendingResume:
    """M-0 "크기 통제" 이중 안전장치 -- `resume` 전체 직렬화가 `limit`
    을 넘으면 `held_drafts` 만 비우고 `dropped` 에 버린 개수를 남긴다.
    `pending_calls` 는 손대지 않는다(판정 표 24행). `pending_calls[].args`
    에는 아직 문자열로 바뀌지 않은 `datetime` 이 섞여 있을 수 있어
    (`add_event.occurred_at` 등) `to_jsonable`(`ask_user` 가 저장 직전에
    쓰는 것과 같은 변환)로 먼저 정규화한 뒤 크기를 잰다 -- 실제 저장될
    바이트 수와 어긋나지 않게 한다."""

    encoded = json.dumps(to_jsonable(resume.to_dict()), ensure_ascii=False).encode("utf-8")
    if len(encoded) <= limit:
        return resume
    return replace(resume, held_drafts=[], dropped=len(resume.held_drafts))


# ---------------------------------------------------------------------------
# M-0 -- `context` 확장 (identity: "resume" 한 키 / new_person: M-1(d)·M-3 안 A)
# ---------------------------------------------------------------------------


def _extend_identity_payload(resolution: Resolution, resume: PendingResume) -> Resolution:
    """`identity` 질문은 `"resume"` 한 키만 더한다 -- 질문 문구·`options`
    등 ER 원본은 그대로다(M-0)."""

    payload = resolution.ask_payload
    assert payload is not None
    context = {**payload["context"], "resume": resume.to_dict()}
    return replace(resolution, ask_payload={**payload, "context": context})


def _extend_new_person_payload(resolution: Resolution, resume: PendingResume) -> Resolution:
    """M-1(d) + M-3 안 A -- 힌트 유무와 관계없이 항상 태그 옵션(5) + ER
    원본 부정 옵션으로 교체한다. `relation_tag` 는 언제나 답에서만
    온다(재개, U7) -- `hints` 는 위계 판단에만 쓰인다."""

    payload = resolution.ask_payload
    assert payload is not None
    negative = [o for o in payload["options"] if o not in payload["affirmative_options"]]
    tags = list(NEW_PERSON_TAG_OPTIONS)
    context = {
        **payload["context"],
        AFFIRMATIVE_KEY: tags,
        "resume": resume.to_dict(),
    }
    new_payload = {
        **payload,
        "options": tags + negative,
        "affirmative_options": tags,
        "context": context,
    }
    return replace(resolution, ask_payload=new_payload)


def _extend_for_ask(
    resolution: Resolution,
    *,
    mention: str,
    hints: dict[str, str],
    pending_calls: list[PendingCall],
    resume_byte_limit: int,
) -> Resolution:
    """되묻기로 이어질 `resolution` 에 재개 재료(`PendingResume`)를 얹은
    새 `Resolution` 을 만든다. `apply_resolution()` 을 부르기 전에
    호출해야 한다(M-0)."""

    resume = PendingResume(
        mention=mention,
        hints=dict(hints),
        pending_calls=pending_calls,
        held_drafts=_preview_drafts(pending_calls),
        dropped=0,
    )
    if resolution.band == "new_person":
        tags = list(NEW_PERSON_TAG_OPTIONS)
        resume = replace(resume, tag_by_answer=dict(zip(tags, RELATION_TAGS)))

    resume = _apply_resume_byte_limit(resume, limit=resume_byte_limit)

    if resolution.band == "new_person":
        return _extend_new_person_payload(resolution, resume)
    return _extend_identity_payload(resolution, resume)


# ---------------------------------------------------------------------------
# 해석 구간 본체
# ---------------------------------------------------------------------------


def _resolve_mentions_impl(
    ctx: ToolContext,
    proposal: Proposal,
    verdict: GateVerdict,
    utterance: str,
    *,
    judge: Judge | None,
    config: ERConfig | None,
    resume_byte_limit: int,
) -> ResolveOutcome:
    mentions, first_index = _ordered_mentions(proposal, verdict)
    hints_by_mention = _match_create_person_hints(proposal, verdict, mentions)

    person_ids: dict[str, int] = {}
    decisions: list[MentionDecision] = []

    for mention in mentions:
        hints = hints_by_mention.get(mention)
        resolution = resolve(ctx, mention, utterance, hints, judge=judge, config=config)

        if resolution.band == "merge":
            applied = apply_resolution(ctx, resolution)
            assert applied.person_id is not None
            person_ids[mention] = applied.person_id
            decisions.append(
                MentionDecision(
                    mention=mention,
                    index=first_index[mention],
                    band="merge",
                    person_id=applied.person_id,
                    trace_id=applied.trace_id,
                    resolution=resolution,
                )
            )
            continue

        # identity / new_person -- 되묻기로 이 턴을 끝낸다(결정 C(i)).
        pending_calls = _pending_calls_from(proposal, verdict, set(person_ids))
        resolution = _extend_for_ask(
            resolution,
            mention=mention,
            hints=hints_by_mention.get(mention, {}),
            pending_calls=pending_calls,
            resume_byte_limit=resume_byte_limit,
        )
        applied = apply_resolution(ctx, resolution)
        decisions.append(
            MentionDecision(
                mention=mention,
                index=first_index[mention],
                band=resolution.band,
                pending_question_id=applied.pending_question_id,
                trace_id=applied.trace_id,
                resolution=resolution,
            )
        )
        return ResolveOutcome(
            person_ids=person_ids,
            decisions=decisions,
            stopped=True,
            pending_question_id=applied.pending_question_id,
        )

    return ResolveOutcome(person_ids=person_ids, decisions=decisions, stopped=False)


def resolve_mentions(
    ctx: ToolContext,
    proposal: Proposal,
    verdict: GateVerdict,
    utterance: str,
    *,
    judge: Judge | None = None,
    config: ERConfig | None = None,
    resume_byte_limit: int | None = None,
) -> ResolveOutcome:
    """U4 해석 구간의 공개 진입점. 게이트를 통과한 제안이 가리키는
    언급마다 `app.er.resolve()` -> `app.er.apply_resolution()` 을 부른다
    (모듈 docstring "순차 처리와 첫 되묻기에서 턴 종료").

    `judge`/`config` 는 `app.er.resolve()` 에 그대로 전달만 한다 -- 이
    함수는 그 값들의 내용을 보지 않는다(원칙1·2·4, 확신도 판정은 ER
    안에서만). 회귀 테스트는 `judge=FakeJudge(...)` 를 주입해 실 LLM 호출
    없이 결정적으로 돈다. `resume_byte_limit` 을 생략하면
    `app.settings.LOOP_MAX_RESUME_BYTES` 를 쓴다(테스트는 작은 값을 주입해
    상한 초과 케이스를 재현한다, `GateConfig` 와 같은 관례).

    `agent_traces` 에 `step="loop_resolve_done"` 행 1개를 남긴다 --
    `output` 은 `ResolveOutcome.to_dict()`(언급별 결정 요약). `judge`/
    `config` 는 JSON 으로 의미 있게 직렬화되지 않으므로(`app.er.resolve()`
    와 같은 이유) 클로저로 감싸 trace 입력에 나타나지 않게 한다."""

    limit = resume_byte_limit if resume_byte_limit is not None else LOOP_MAX_RESUME_BYTES

    @traced(LOOP_TRACE_TOOL_NAME, step=STEP_LOOP_RESOLVE_DONE)
    def _traced_resolve_mentions(
        ctx: ToolContext,
        proposal: Proposal,
        verdict: GateVerdict,
        utterance: str,
        resume_byte_limit: int,
    ) -> ResolveOutcome:
        return _resolve_mentions_impl(
            ctx,
            proposal,
            verdict,
            utterance,
            judge=judge,
            config=config,
            resume_byte_limit=resume_byte_limit,
        )

    return _traced_resolve_mentions(ctx, proposal, verdict, utterance, limit)


# ---------------------------------------------------------------------------
# 아직 없는 것 (U5 가 채운다)
# ---------------------------------------------------------------------------
#
# `run_turn(ctx, utterance, *, proposer=None, judge=None, config=None) ->
# TurnResult` -- 인식(U2 `propose`) -> 게이트(U3 `check`) -> 이 파일의
# `resolve_mentions()` -> 기록(게이트 통과 + `person_id` 확정 제안만
# `add_event`/`add_schedule`/`update_person` 실행) -> 응답(`respond.py`)
# 을 한 턴 안에서 잇는다. `resume_turn(ctx, resume_input) -> TurnResult`
# 는 해석 단계부터 다시 돈다(결정 E(i), 인식 LLM 재호출 없음). 이 이름
# 둘은 U5/U6/U7 이 만든다 -- `app/agent/__init__.py` 도 그때 갱신한다.
