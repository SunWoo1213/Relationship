"""Refs: P5-loop D1 D2 D12 D13 S3.2 S3.3 S3.4 원칙1 원칙2 원칙4 원칙7 원칙9 --
U4 해석 단계(`resolve_mentions()`) + U5 기록·응답 단계(`run_turn()`).

## 이 단위(U5)가 채우는 자리, 채우지 않는 자리

U4 는 **해석 구간**(`resolve_mentions()`)만 채웠다. 이 단위(U5)는 그 위에
**기록 구간**(게이트를 통과하고 `person_id` 가 확정된 제안만 실행)과
**응답 구간**(`app/agent/respond.py` 호출)을 얹어 `run_turn()` 하나로
잇는다 -- 인식(U2 `propose`) -> 게이트(U3 `check`) -> 해석(U4
`resolve_mentions`) -> 기록(이 단위) -> 응답(이 단위)이 한 턴 안에서
전부 돈다. `resume_turn()` 이라는 이름은 아직 없다 -- 재개(U7)가 채울
자리이고, 이 단위가 그 이름을 미리 선언하면 아직 하지 않은 약속(답
처리·`ResumeInput` 소비)을 한 것으로 오인될 수 있다.

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
저장, 미확정분만 보류"). **예외 한 종류**(사용자 수정 요청 2026-09-24,
아래 "일정 시각 미확정" 절): 확정된 언급이라도 그 제안이 `scheduled_at`
미확정 `add_schedule` 이면 `_pending_calls_from` 이 이 예외를 담아
`pending_calls` 에 넣는다 -- 이 턴은 어차피 다른 언급 때문에 되묻기로
끝나므로 기록 단계가 그 제안을 실행할 수도, 두 번째 질문을 낼 수도
없기 때문이다. `identity`/`new_person` 이 나오면 그 언급과 그 뒤로
아직 손대지 않은 모든 언급의 제안을 `pending_calls` 로 묶어 그 자리에서
턴을 끝낸다(결정 C(i)) -- 이후 언급은 아예 `resolve()` 를 부르지도
않는다.

## U5 기록 구간 -- `run_turn()`

`run_turn(ctx, utterance, *, proposer=None, judge=None, config=None)` 은
인식(`app.agent.propose`) -> 게이트(`app.agent.gate.check`) ->
`resolve_mentions()`(위) -> 기록 -> 응답(`app.agent.respond.build_reply`)
을 잇는다. `proposer` 를 생략하면 `proposer_from_env()`(실 LLM, 운영
경로)를 쓴다 -- 테스트는 `FakeProposer` 를 주입해 네트워크 0 으로 돈다.
`judge`/`config` 는 그대로 `resolve_mentions()` 에 넘길 뿐 이 함수가
내용을 보지 않는다(원칙1·2·4, 위 절과 같은 이유).

**기록 대상**: 게이트가 `bucket="execute"` 로 통과시키고(`GateVerdict.
accepted`), 그 제안의 `args["person"]`(언급)이 해석 구간에서 `merge` 로
확정된(`outcome.person_ids` 안에 있는) 제안만 실행한다. `args["person"]`
자리는 실행 직전 **코드가** 그 `person_id` 로 치환한다(01-plan U5 "`args.
person` 을 코드가 `person_id` 로 치환") -- LLM 이 준 값은 언급 문자열
그대로 남아 있을 뿐 한 번도 `person_id` 로 취급되지 않는다. 언급이 아직
확정되지 않은 제안(해석 구간이 되묻기로 멈춰 아예 `resolve()` 를 타지
않은 것들)은 **저장하지 않는다** -- 이미 해석 구간이 그 제안들을
`context["resume"]["pending_calls"]` 에 실어 두었으므로(위 "순차 처리"
절) 여기서 다시 담지 않는다(이중 기록 금지).

`update_person` 실행은 판정 표 5b 허용 목록의 (ㄱ) 자리다 -- 게이트가
`display_name` 있는 제안을 이미 `needs_confirmation` 으로 거부했으므로
(U3), 여기 닿는 제안은 항상 `facts`/`new_alias` 뿐이다. `create_person`
은 `bucket="hint_only"` 라 애초에 이 기록 대상 집합에 없다(D1 -- 재개
경로에서만, U7).

**R-24(02-plan-verify 210행, 이 단위에서 정한다) -- `failed[]` 와 U6
예외 범위의 관계**: 기록 단계는 제안 **하나마다** `app.tools.types.
ToolError` 를 잡아 `loop_record.output.failed[]` 에 담고 다음 제안으로
넘어간다(확정분을 그대로 저장하는 결정 D(i)와 같은 방향 -- 제안 하나의
실패가 같은 턴의 다른 제안 실행을 막지 않는다). `run_turn` 밖으로 나가는
것은 `ToolError` 가 아닌 예외(공급자 오류·`LoopError`·`SQLAlchemyError`
등)뿐이고, 그것을 잡을지/어떻게 응답으로 내릴지는 **U6 의 라우트**가
정한다(01-plan 93행 "삼키는 것은 `LoopError` 계층·공급자 오류·`ToolError`
계층뿐" 은 라우트 단의 규약이지, 기록 단계가 `ToolError` 를 라우트까지
올려 보낸다는 뜻이 아니다) -- `loop_record` 가 "정확히 1행"(U1 81행)이
되려면 기록 단계 자신이 먼저 `ToolError` 를 소비해야 하기 때문이다.

**일정 시각 미확정(결정 K(i)·M-2(i))**: `add_schedule` 제안의
`scheduled_at` 이 `None`(게이트 R-23 이 통과시킨 "미확정")이면, **해석
구간이 아직 되묻기로 멈추지 않은 턴에 한해** `add_schedule` 을 부르지
않고 `ask_user(kind="schedule")` 를 직접 부른다(`_ask_schedule`). 그
시점 이후의(자기 자신 포함) 모든 실행 대상 제안은 `pending_calls` 로
옮겨 담고 턴을 끝낸다 -- 결정 C(i) "첫 되묻기에서 턴 종료"를 해석
구간뿐 아니라 기록 구간에도 같은 규칙으로 적용한 것이다(이 단위에서
정한다).

**해석 구간이 이미 되묻기로 멈춰 있던 턴**(identity/new_person 질문이
이미 나갔다, 사용자 수정 요청 2026-09-24)이라면 한 턴에 질문은 하나만
나간다는 규칙을 지키기 위해 **두 번째 질문을 만들지 않는다** -- 그렇다고
`add_schedule(ctx, person_id, title, None)` 을 강행해 `InvalidValue` 로
잃어버리지도 않는다(이전 구현은 그렇게 했으나, 방금 merge 로 확정한
인물 연결에 딸린 제안을 실패로 버리는 것이었다). 대신 해석 구간
(`_pending_calls_from`)이 이 제안을 **예외로** 그 되묻기 질문의
`context["resume"]["pending_calls"]` 에 이미 실어 두었으므로(위 "순차
처리" 절 D(i) 의 "merge 된 언급은 바로 실행" 원칙에 대한 유일한 예외),
기록 단계는 이 제안을 건너뛰기만 한다(`_needs_schedule_question()` 로
판정, 이중 기록 금지). 재개(U7)가 그 질문에 답한 뒤 이 제안을 다시
실행하려다 시각이 여전히 없다는 것을 보고 **그 자리에서 새 `schedule`
질문**을 띄운다 -- 01-plan U7 "재개 중 남은 언급의 `resolve()` 가 다시
되묻거나 `schedule` 질문이 나오면 그 자리에서 재개 턴을 끝내고"
흐름(R-14 "identity 답 뒤 schedule 질문"과 같은 모양)을 그대로 따른다.

**판정 함수 단일 출처**: "`add_schedule` 인데 `scheduled_at` 이 없다"는
조건은 `_needs_schedule_question()` 하나로 고정한다 -- 해석 구간의 예외
(`_pending_calls_from`)와 기록 구간의 두 분기(질문을 새로 낼지, 건너뛸지)
가 전부 이 함수를 부른다(R-12 "같은 검사를 두 자리에서 하지 않는다").

**후보 시각 생성 규칙(M-2(i), 이 단위에서 정한다)**: `ctx.now()` 기준
내일·모레 저녁 7시(같은 tzinfo) 두 후보 + "모르겠어요"(`SCHEDULE_
UNKNOWN_OPTION`). 발화 속 상대 날짜("다음 주 금요일" 등)를 다시 파싱하지
않는다 -- `scheduled_at` 이 확정되지 않았다는 것은 이미 인식 단계(U2)가
"언제"를 절대 시각으로 바꾸지 못했다는 뜻이므로, 발화를 다시 해석하려
들지 않고 `now` 이후 가장 가까운 이틀을 후보로 제시해 사용자가 직접
고르게 한다(`_schedule_candidates`).

## 이 모듈이 하지 않는 것 (U5 추가분)

- 응답 문장을 스스로 조립하지 않는다 -- `app/agent/respond.py::
  build_reply()` 하나가 유일한 조립 지점이다(결정 B(i), 원칙7 -- 상담성
  문장이 생길 자리를 코드 구조로 없앤다).
- 게이트·인식 결과를 다시 검증하지 않는다 -- `GateVerdict.accepted` 를
  그대로 신뢰하고, 인자 스키마·화이트리스트를 다시 확인하지 않는다
  (R-12 "같은 검사를 두 자리에서 하지 않는다").
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any

from app import tools as app_tools
from app.agent.gate import check as gate_check
from app.agent.propose import Proposer, proposer_from_env
from app.agent.respond import build_reply
from app.agent.types import (
    BUCKET_EXECUTE,
    BUCKET_HINT_ONLY,
    NEW_PERSON_TAG_OPTIONS,
    SCHEDULE_UNKNOWN_OPTION,
    STEP_LOOP_EXTRACT,
    STEP_LOOP_GATE,
    STEP_LOOP_RECORD,
    STEP_LOOP_RESOLVE_DONE,
    STEP_LOOP_TURN,
    LOOP_TRACE_TOOL_NAME,
    GateVerdict,
    PendingCall,
    PendingResume,
    Proposal,
    ScheduleResumeRef,
    StoredSummary,
    TurnResult,
)
from app.db.models import HIERARCHIES, RELATION_TAGS
from app.er import ERConfig, Judge, Resolution, apply_resolution, resolve
from app.settings import LOOP_MAX_RESUME_BYTES
from app.tools.context import ToolContext, to_jsonable, traced
from app.tools.types import AFFIRMATIVE_KEY, PendingQuestionOut, ToolError

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


def _needs_schedule_question(name: str, args: dict[str, Any]) -> bool:
    """`add_schedule` 제안인데 `scheduled_at` 이 아직 확정되지 않았는가
    (결정 K(i)·M-2(i)). U4(`_pending_calls_from` 의 예외)·U5(기록 단계)가
    같은 판정을 공유한다(단일 출처) -- 두 자리에서 다른 조건을 쓰면 등식이
    깨진다(사용자 수정 요청 2026-09-24)."""

    return name == "add_schedule" and args.get("scheduled_at") is None


def _pending_calls_from(
    proposal: Proposal, verdict: GateVerdict, resolved_mentions: set[str]
) -> list[PendingCall]:
    """게이트를 통과했지만(`execute` 버킷) 아직 `person_id` 가 확정되지
    않은 언급에 딸린 제안 -- 첫 되묻기 시점까지 `merge` 로 확정된 언급
    (`resolved_mentions`)은 기록 단계(U5)가 `person_ids` 맵으로 바로
    실행하므로 여기 담지 않는다(결정 D(i)).

    **예외(사용자 수정 요청 2026-09-24)**: `merge` 로 이미 확정된 언급이라도
    그 제안이 `scheduled_at` 미확정 `add_schedule` 이면 이 목록에 **담는다**.
    이유: 이 턴은 이미 다른 언급 때문에 되묻기로 끝나므로(한 턴에 질문은
    하나만, 결정 C(i)) 기록 단계가 이 제안을 위해 **두 번째** `ask_user`
    를 부를 수 없다 -- 그렇다고 `scheduled_at=None` 으로 `add_schedule` 을
    강행해 `InvalidValue` 로 잃어버리면(이전 구현) 사용자가 방금 확정한
    인물 연결이 헛수고가 된다. 이 되묻기가(identity/new_person 답으로)
    재개되면 U7 이 이 `pending_calls` 항목을 이어 실행하다 마찬가지로
    시각이 없다는 것을 보고 `schedule` 질문을 새로 띄운다(01-plan U7
    "재개 중 남은 언급의 resolve() 가 다시 되묻거나 schedule 질문이 나오면
    그 자리에서 재개 턴을 끝내고" 흐름 그대로 -- R-14 "identity 답 뒤
    schedule 질문"과 같은 모양). 판정 함수는 `_needs_schedule_question()`
    하나로 U5 기록 단계와 공유한다(이중 판정 금지)."""

    calls: list[PendingCall] = []
    for accepted in verdict.accepted:
        if accepted.bucket != BUCKET_EXECUTE:
            continue
        args = proposal.tool_calls[accepted.index].args
        mention = args.get("person")
        is_resolved = isinstance(mention, str) and mention in resolved_mentions
        if is_resolved and not _needs_schedule_question(accepted.name, args):
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
# U5 -- 인식/게이트 단계를 loop_extract/loop_gate trace 로 감싸는 얇은 래퍼
# (인식·게이트 자체 구현은 U2 propose.py·U3 gate.py 의 몫 -- 여기서는 그
# 결과를 trace 로 남기는 것만 한다, R-16·결정 F)
# ---------------------------------------------------------------------------


def _propose(ctx: ToolContext, utterance: str, now: datetime, proposer: Proposer) -> Proposal:
    """`loop_extract` trace 행 1개(01-plan 범위 27행 "인식 단계"). `proposer`
    는 클로저로 감싼다 -- trace `input` 에 공급자 객체가 그대로 찍히지
    않게 한다(`resolve_mentions` 가 `judge`/`config` 를 다루는 것과 같은
    방식)."""

    @traced(LOOP_TRACE_TOOL_NAME, step=STEP_LOOP_EXTRACT)
    def _traced(ctx: ToolContext, utterance: str, now: datetime) -> Proposal:
        return proposer.propose(utterance, now)

    return _traced(ctx, utterance, now)


def _gate(ctx: ToolContext, proposal: Proposal) -> GateVerdict:
    """`loop_gate` trace 행 1개(결정 F -- L(iii) 반영으로 더해진 step).
    `gate.check()` 는 세션을 건드리지 않는 순수 함수이므로(U3), 이 함수가
    trace 를 남기는 유일한 이유는 `agent_traces` 에 게이트 판정을
    기록하기 위해서다."""

    @traced(LOOP_TRACE_TOOL_NAME, step=STEP_LOOP_GATE)
    def _traced(ctx: ToolContext, proposal: Proposal) -> GateVerdict:
        return gate_check(proposal)

    return _traced(ctx, proposal)


# ---------------------------------------------------------------------------
# U5 -- 기록 구간: 게이트 통과 + person_id 확정 제안만 실행
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RecordOutcome:
    """`loop_record.output` 스키마(U1 81행) + `run_turn` 이 응답·`TurnResult
    .stored` 를 조립하는 데 쓰는 부가 정보. `to_dict()` 는 U1 이 고정한
    두 키(`executed`/`failed`)만 낸다 -- 나머지 필드는 이중 출처를 만들지
    않기 위해 trace 출력에는 담지 않는다(같은 값이 필요하면 `loop_turn`
    행이 `TurnResult.to_dict()` 로 따로 남긴다)."""

    executed: list[dict[str, Any]] = field(default_factory=list)
    failed: list[dict[str, Any]] = field(default_factory=list)
    events: int = 0
    schedules: int = 0
    schedule_question: PendingQuestionOut | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"executed": list(self.executed), "failed": list(self.failed)}


#: M-2(i) -- 후보 시각 생성 규칙(모듈 docstring "후보 시각 생성 규칙" 참고,
#: 이 단위에서 정한다). 내일(1)·모레(2) 저녁 7시 두 후보.
_SCHEDULE_CANDIDATE_DAY_OFFSETS: tuple[int, ...] = (1, 2)
_SCHEDULE_CANDIDATE_HOUR = 19


def _schedule_candidates(now: datetime) -> list[tuple[str, datetime]]:
    """`now` 와 같은 tzinfo 를 유지한 채 내일·모레 저녁 7시 두 후보를
    `(사람이 읽는 문자열, datetime)` 쌍으로 만든다(모듈 docstring "후보
    시각 생성 규칙")."""

    candidates: list[tuple[str, datetime]] = []
    for offset in _SCHEDULE_CANDIDATE_DAY_OFFSETS:
        target = now + timedelta(days=offset)
        dt = target.replace(
            hour=_SCHEDULE_CANDIDATE_HOUR, minute=0, second=0, microsecond=0
        )
        label = f"{dt.month}월 {dt.day}일 저녁 {_SCHEDULE_CANDIDATE_HOUR - 12}시"
        candidates.append((label, dt))
    return candidates


def _ask_schedule(
    ctx: ToolContext,
    *,
    person_id: int,
    title: str,
    pending_calls: list[PendingCall],
    resume_byte_limit: int,
    now: datetime,
) -> PendingQuestionOut:
    """M-2(i) -- `scheduled_at` 이 확정되지 않은 `add_schedule` 제안을
    대신해 `ask_user(kind="schedule")` 를 직접 부른다. `pending_calls[0]`
    이 이 질문을 일으킨 `add_schedule` 제안 자신이다(`ScheduleResumeRef.
    call_index=0`, 호출자가 그렇게 순서를 맞춰 넘긴다). `now` 는 호출자
    (`_record_impl`)가 이미 읽은 값을 그대로 받는다 -- `ctx.now()` 를 이
    턴 안에서 두 번 불러 값이 갈릴 여지를 남기지 않는다."""

    candidates = _schedule_candidates(now)
    schedule_options = {label: dt.isoformat() for label, dt in candidates}
    options = [label for label, _ in candidates] + [SCHEDULE_UNKNOWN_OPTION]

    resume = PendingResume(
        pending_calls=pending_calls,
        held_drafts=_preview_drafts(pending_calls),
        schedule=ScheduleResumeRef(person_id=person_id, title=title, call_index=0),
        schedule_options=schedule_options,
    )
    resume = _apply_resume_byte_limit(resume, limit=resume_byte_limit)

    question = f"'{title}' 약속, 언제로 기억할까요?"
    return app_tools.ask_user(
        ctx,
        kind="schedule",
        question=question,
        options=options,
        context={"resume": resume.to_dict()},
    )


def _execute_call(
    ctx: ToolContext, name: str, args: dict[str, Any], person_id: int, utterance: str, now: datetime
) -> Any:
    """게이트를 통과한 실행 대상 제안 하나를 실제 툴로 옮긴다. `person_id`
    는 호출자(`_record_impl`)가 해석 구간에서 확정한 값을 넘긴다 -- 이
    함수 자신은 해석을 하지 않는다."""

    if name == "add_event":
        occurred_at = args.get("occurred_at")
        if occurred_at is None:
            # 결정 K(i) -- 이벤트는 확정 못 하면 now 로 채운다.
            occurred_at = now
        return app_tools.add_event(
            ctx, person_id, args["type"], args["content"], occurred_at, utterance
        )
    if name == "add_schedule":
        # 시각 미확정(scheduled_at is None) 제안은 호출자(_record_impl)가
        # _needs_schedule_question() 으로 미리 갈라내 여기 닿지 않는다
        # (되묻기(새 질문) 또는 pending_calls 로 옮겨진다, 사용자 수정
        # 요청 2026-09-24) -- 방어적으로 그대로 넘겨도 add_schedule 자신의
        # InvalidValue 가 막는다.
        return app_tools.add_schedule(ctx, person_id, args["title"], args.get("scheduled_at"))
    if name == "update_person":
        return app_tools.update_person(
            ctx, person_id, facts=args.get("facts"), new_alias=args.get("new_alias")
        )
    raise AssertionError(f"게이트가 execute 버킷으로 통과시킨 알 수 없는 툴 이름: {name!r}")


def _record_impl(
    ctx: ToolContext,
    proposal: Proposal,
    verdict: GateVerdict,
    outcome: ResolveOutcome,
    utterance: str,
    *,
    resume_byte_limit: int,
) -> RecordOutcome:
    now = ctx.now()
    accepted_execute = [a for a in verdict.accepted if a.bucket == BUCKET_EXECUTE]

    executed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    events = 0
    schedules = 0
    schedule_question: PendingQuestionOut | None = None

    for position, accepted in enumerate(accepted_execute):
        call = proposal.tool_calls[accepted.index]
        mention = call.args.get("person")
        if not isinstance(mention, str) or mention not in outcome.person_ids:
            # 해석 구간이 아직 확정하지 못한 언급 -- 되묻기로 멈춘 턴이면
            # 이미 context["resume"]["pending_calls"] 에 실려 있다(위
            # resolve_mentions 절). 여기서 다시 담지 않는다(이중 기록 금지).
            continue

        if outcome.stopped and _needs_schedule_question(accepted.name, call.args):
            # 사용자 수정 요청(2026-09-24) -- 언급은 merge 로 확정됐지만
            # 이 턴은 이미 다른 언급 때문에 identity/new_person 되묻기로
            # 끝났다(한 턴에 질문은 하나만, 결정 C(i)). 그래서 여기서
            # add_schedule(..., None) 을 강행해 실패시키지 않는다 -- 이
            # 제안은 `_pending_calls_from` 의 예외로 이미 그 질문의
            # `context["resume"]["pending_calls"]` 에 실려 있다(U4). 두
            # 번 담지 않도록(이중 기록 금지) 여기서는 건너뛰기만 한다.
            continue
        person_id = outcome.person_ids[mention]

        if (
            not outcome.stopped
            and schedule_question is None
            and _needs_schedule_question(accepted.name, call.args)
        ):
            remaining = accepted_execute[position:]
            pending_calls = [
                PendingCall(
                    index=a.index, name=a.name, args=dict(proposal.tool_calls[a.index].args)
                )
                for a in remaining
            ]
            schedule_question = _ask_schedule(
                ctx,
                person_id=person_id,
                title=call.args.get("title", ""),
                pending_calls=pending_calls,
                resume_byte_limit=resume_byte_limit,
                now=now,
            )
            break

        try:
            _execute_call(ctx, accepted.name, call.args, person_id, utterance, now)
        except ToolError as exc:
            failed.append({"index": accepted.index, "name": accepted.name, "error": type(exc).__name__})
            continue

        executed.append({"index": accepted.index, "name": accepted.name, "trace_id": ctx.last_trace_id})
        if accepted.name == "add_event":
            events += 1
        elif accepted.name == "add_schedule":
            schedules += 1

    return RecordOutcome(
        executed=executed,
        failed=failed,
        events=events,
        schedules=schedules,
        schedule_question=schedule_question,
    )


def _record(
    ctx: ToolContext,
    proposal: Proposal,
    verdict: GateVerdict,
    outcome: ResolveOutcome,
    utterance: str,
    *,
    resume_byte_limit: int,
) -> RecordOutcome:
    """`loop_record` trace 행 1개(U1 81행 "게이트를 지난 턴마다 정확히
    1행" -- 되묻기로 실행이 0건이어도 `executed: []` 로 남긴다)."""

    @traced(LOOP_TRACE_TOOL_NAME, step=STEP_LOOP_RECORD)
    def _traced(
        ctx: ToolContext,
        proposal: Proposal,
        verdict: GateVerdict,
        outcome: ResolveOutcome,
        utterance: str,
    ) -> RecordOutcome:
        return _record_impl(
            ctx, proposal, verdict, outcome, utterance, resume_byte_limit=resume_byte_limit
        )

    return _traced(ctx, proposal, verdict, outcome, utterance)


# ---------------------------------------------------------------------------
# U5 -- run_turn(): 인식 -> 게이트 -> 해석 -> 기록 -> 응답
# ---------------------------------------------------------------------------


def _pending_question_from_resolve(outcome: ResolveOutcome) -> PendingQuestionOut:
    """해석 구간이 만든 identity/new_person 질문을 `PendingQuestionOut`
    으로 다시 만든다 -- `PendingQuestion` ORM 을 조회하지 않고, 이 루프가
    이미 들고 있는 `Resolution.ask_payload`(`MentionDecision.resolution`)
    dict 의 `kind`/`question`/`options` 를 그대로 옮겨 담는다(판정 표
    23행 -- 대기 질문 ORM 을 이 파일이 직접 다루지 않는다)."""

    last = outcome.decisions[-1]
    resolution = last.resolution
    assert resolution is not None and resolution.ask_payload is not None
    payload = resolution.ask_payload
    assert last.pending_question_id is not None
    return PendingQuestionOut(
        question_id=last.pending_question_id,
        status="pending",
        kind=payload["kind"],
        question=payload["question"],
        options=list(payload["options"]),
    )


def run_turn(
    ctx: ToolContext,
    utterance: str,
    *,
    proposer: Proposer | None = None,
    judge: Judge | None = None,
    config: ERConfig | None = None,
) -> TurnResult:
    """U5 오케스트레이션 진입점(01-plan U5 "게이트를 통과하고 person_id
    가 확정된 제안만 실행 ... respond.py 가 결과를 문장으로 만든다").

    `proposer` 를 생략하면 `app.agent.propose.proposer_from_env()`(실
    LLM)를 쓴다 -- 테스트는 `FakeProposer` 를 주입해 네트워크 0 으로
    돈다(원칙8). `judge`/`config` 는 `resolve_mentions()` 로 그대로
    전달한다.

    `resume_turn(ctx, resume_input) -> TurnResult` 은 이 단위(U5)가 아니라
    U7 이 채운다 -- 여기서는 이름조차 선언하지 않는다(해석 단계부터
    다시 도는 재개는 저장된 `context` 를 읽는 별도 진입점이 필요하고,
    그 조립(`app.api.deps.load_resume_input`)은 U6/U7 의 산출물이다)."""

    now = ctx.now()
    active_proposer = proposer if proposer is not None else proposer_from_env()

    proposal = _propose(ctx, utterance, now, active_proposer)
    extract_trace_id = ctx.last_trace_id
    verdict = _gate(ctx, proposal)
    gate_trace_id = ctx.last_trace_id
    outcome = resolve_mentions(ctx, proposal, verdict, utterance, judge=judge, config=config)
    resolve_trace_id = ctx.last_trace_id
    record = _record(
        ctx, proposal, verdict, outcome, utterance, resume_byte_limit=LOOP_MAX_RESUME_BYTES
    )
    record_trace_id = ctx.last_trace_id

    if record.schedule_question is not None:
        pending_question = record.schedule_question
    elif outcome.stopped:
        pending_question = _pending_question_from_resolve(outcome)
    else:
        pending_question = None

    if pending_question is not None:
        stop_reason = "ask_user"
    else:
        stop_reason = verdict.stop_reason

    reply = build_reply(
        stored_events=record.events,
        stored_schedules=record.schedules,
        failed_count=len(record.failed),
        limit_hit=verdict.stop_reason == "limit",
        pending_question=pending_question,
    )

    turn = TurnResult(
        reply=reply,
        session_id=ctx.session_id,
        stored=StoredSummary(persons=0, events=record.events, schedules=record.schedules),
        pending_question=pending_question,
        stop_reason=stop_reason,
        trace_ids=[
            trace_id
            for trace_id in (extract_trace_id, gate_trace_id, resolve_trace_id, record_trace_id)
            if trace_id is not None
        ],
    )

    @traced(LOOP_TRACE_TOOL_NAME, step=STEP_LOOP_TURN)
    def _traced_turn(ctx: ToolContext, utterance: str, turn: TurnResult) -> TurnResult:
        return turn

    return _traced_turn(ctx, utterance, turn)
