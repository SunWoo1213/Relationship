"""Refs: P5-loop S3.2 S3.4 원칙9 -- 루프 계약 타입 + trace 어휘 (U1).

U1 은 **계약 타입만** 정의한다 -- `run_turn`/`resume_turn`(U4 `app/agent/loop.py`)
이 실제로 도는 코드는 아직 없다(01-plan U1 항목 첫 줄). 여기서 고정한 세
output 스키마(`GateVerdict`·`loop_record.output`·`PendingResume`)가 이후
단위(U2~U7)의 판정 표 등식이 서는 바닥이다(01-plan H-1).

## 이 모듈이 하지 않는 것

- 확신도 계산·임계치 비교를 하지 않는다(원칙1·2·4) -- 이 파일은 물론
  `app/agent/` 어디에도 임계치·확신도를 가리키는 영어 어휘를 쓰지 않는다.
  설명이 필요하면 한국어 "확신도"로 쓴다(01-plan 판정 표 6행).
- 거부 사유 어휘(`unknown_tool`/`not_callable_by_llm`/`bad_args`/
  `person_id_from_llm`/`needs_confirmation`/`limit`)를 정의하지 않는다 --
  그 어휘의 단일 출처는 `app/agent/gate.py`(U3)다(01-plan 60행). 이 모듈은
  `reason: str` 로만 받는다.
- 실제 게이트·인식·해석·기록·응답 로직을 담지 않는다(U2~U5).

## 이 모듈이 고정하는 것

- `GateVerdict` = `loop_gate.output` 스키마, `bucket` 어휘(`execute`/
  `hint_only`)는 여기가 단일 출처다(U1 테스트 "bucket 어휘 고정").
- `loop_record.output` 모양(`PendingCall`·`TurnResult` 조합으로 U5 가
  채운다).
- `PendingResume` -- `pending_questions.context["resume"]` 키의 스키마
  (재개 재료, M-0·M-1(d)·M-2(i)).
- 루프 trace 상수 -- `tool_name="agent"`, step 6종(결정 F) + 오류 전용
  `loop_error`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.db.models import EVENT_TYPES, QUESTION_KINDS, RELATION_TAGS
from app.tools.types import InvalidValue, PendingQuestionOut

# ---------------------------------------------------------------------------
# 루프 trace 어휘 (결정 F -- tool_name 고정 + step 6종 + 오류 전용 1종)
# ---------------------------------------------------------------------------

#: `agent_traces.tool_name` -- 루프가 남기는 모든 행의 값(결정 F(i)).
#: `app.tools.TOOL_NAMES`(툴 7종)·`app.er.types.ER_TRACE_TOOL_NAME`("er")
#: 과 겹치지 않는다.
LOOP_TRACE_TOOL_NAME = "agent"

#: 인식 단계 -- LLM 이 제안한 `tool_calls[]` 원문(U2 `propose.py`).
STEP_LOOP_EXTRACT = "loop_extract"
#: 게이트 단계 -- 코드가 화이트리스트·인자 스키마·`person_id` 금지·상한을
#: 적용한 결과(U3 `gate.py`, L(iii) 반영으로 6종에 더해진 step).
STEP_LOOP_GATE = "loop_gate"
#: 해석 단계 요약 -- 언급별 결정(merge/identity/new_person)(U4 `loop.py`).
STEP_LOOP_RESOLVE_DONE = "loop_resolve_done"
#: 기록 단계 -- 어떤 draft 를 어느 툴로 실행했는지(U5).
STEP_LOOP_RECORD = "loop_record"
#: 턴 요약 -- 발화·응답·`stop_reason`(U5/U6).
STEP_LOOP_TURN = "loop_turn"
#: 재개 진입 -- `POST /answers/{question_id}` 뒤 절반(U7).
STEP_LOOP_RESUME = "loop_resume"
#: 오류 전용 -- 기존 `tool_error` 를 쓰지 않고 이 이름으로 따로 남긴다
#: (결정 G·H). 아래 `LOOP_TRACE_STEPS`(6종) 에는 포함하지 않는다 -- 정상
#: 진행 단계가 아니기 때문이다.
STEP_LOOP_ERROR = "loop_error"

#: 결정 F 의 정상 진행 step 6종(고정 순서 -- 한 턴이 지나는 순서와 같다).
LOOP_TRACE_STEPS: tuple[str, ...] = (
    STEP_LOOP_EXTRACT,
    STEP_LOOP_GATE,
    STEP_LOOP_RESOLVE_DONE,
    STEP_LOOP_RECORD,
    STEP_LOOP_TURN,
    STEP_LOOP_RESUME,
)

# ---------------------------------------------------------------------------
# 게이트 버킷 어휘 (`GateVerdict.accepted[].bucket` 의 단일 출처, U1)
# ---------------------------------------------------------------------------

BUCKET_EXECUTE = "execute"
BUCKET_HINT_ONLY = "hint_only"
GATE_BUCKETS: tuple[str, ...] = (BUCKET_EXECUTE, BUCKET_HINT_ONLY)

# ---------------------------------------------------------------------------
# M-1(d) -- new_person 재개 질문의 태그별 긍정 옵션 (RELATION_TAGS 와 1:1)
# ---------------------------------------------------------------------------

#: 01-plan 84행 원문 그대로("가족으로/연인으로/친구로/직장으로/지인으로
#: 기억할게요") -- `RELATION_TAGS` 순서와 1:1 이다(U4 가
#: `dict(zip(NEW_PERSON_TAG_OPTIONS, RELATION_TAGS))` 로 `tag_by_answer`
#: 를 만든다). 조사(으로/로)가 단어마다 달라 규칙 생성 대신 리터럴로
#: 고정하고, 아래 `assert` 로 `RELATION_TAGS` 와의 1:1 을 항상 확인한다.
NEW_PERSON_TAG_OPTIONS: tuple[str, ...] = (
    "가족으로 기억할게요",
    "연인으로 기억할게요",
    "친구로 기억할게요",
    "직장으로 기억할게요",
    "지인으로 기억할게요",
)

assert len(NEW_PERSON_TAG_OPTIONS) == len(RELATION_TAGS), (
    "NEW_PERSON_TAG_OPTIONS 는 RELATION_TAGS 와 1:1 이어야 한다"
)

#: `PendingResume.version` 기본값(`app.er.types.ER_VERSION` 과 같은 문자열
#: 버전 표기 관례). 스키마가 바뀌면 올린다.
LOOP_RESUME_VERSION = "1"


# ---------------------------------------------------------------------------
# 예외 계층
# ---------------------------------------------------------------------------


class LoopError(Exception):
    """`app/agent/` 예외의 공통 베이스. `app.tools.types.ToolError`(툴
    계층)·`app.er.types.JudgeUnavailable`(공급자 오류)와는 **별개** 계층
    이다 -- U6(01-plan 93행)이 라우트에서 셋을 나란히 잡아 삼킨다
    (`LoopError` 계층 / 공급자 오류 6종 / `ToolError` 계층). 메시지는
    `ToolError` 관례와 같이 비밀·원문을 담지 않는 짧은 코드성 문자열이어야
    한다."""


class ResumeContextError(LoopError):
    """저장된 `pending_questions.context["resume"]` 이 `PendingResume`
    스키마를 만족하지 않을 때(U7 재개 경로가 던진다) -- 사유 코드만 담고
    `context` 원문은 메시지에 넣지 않는다."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


# ---------------------------------------------------------------------------
# 인식 단계 -- LLM 제안 (U2 `propose.py` 가 만든다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolCallProposal:
    """LLM 이 구조화 출력으로 제안한 툴 호출 하나. `args` 안의 인물은
    `person_id` 가 아니라 언급 문자열(`args["person"]`)이어야 한다 -- 이
    타입 자체는 강제하지 않는다(강제는 U3 게이트의 일, 01-plan 86행 "형식만
    본다")."""

    name: str
    args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "args": dict(self.args)}


@dataclass(frozen=True)
class Proposal:
    """인식 단계(U2) 산출물 -- `loop_extract.output` 의 바탕이 되는 값.

    `raw` 는 게이트·해석이 참조하지 않는 LLM 구조화 출력 원문(파싱 전
    dict)이다 -- 스키마 위반 디버깅·감사 목적일 뿐, `tool_calls` 가 실제
    실행 경로가 읽는 유일한 값이다(이중 출처 금지, 01-plan 80행 "인자 값은
    거기에만 둔다"의 정신을 `raw` 에도 적용한다)."""

    tool_calls: list[ToolCallProposal] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_calls": [c.to_dict() for c in self.tool_calls],
            "raw": dict(self.raw),
        }


# ---------------------------------------------------------------------------
# 게이트 단계 -- `GateVerdict` = `loop_gate.output` (U3 `gate.py` 가 만든다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AcceptedProposal:
    """게이트를 통과한 제안 하나. `index` 는 `loop_extract.output.tool_calls[]`
    의 위치를 가리킨다(값 자체는 담지 않는다 -- 이중 출처 금지, 01-plan
    80행)."""

    index: int
    name: str
    bucket: str

    def __post_init__(self) -> None:
        if self.bucket not in GATE_BUCKETS:
            raise InvalidValue(
                f"AcceptedProposal.bucket must be one of {GATE_BUCKETS} "
                f"(got {self.bucket!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "name": self.name, "bucket": self.bucket}


@dataclass(frozen=True)
class RejectedProposal:
    """게이트가 거부한 제안 하나. `reason` 어휘의 단일 출처는 `gate.py`
    다(01-plan 60행) -- 이 타입은 문자열을 그대로 받을 뿐 검증하지 않는다."""

    index: int
    name: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "name": self.name, "reason": self.reason}


@dataclass(frozen=True)
class GateLimits:
    """결정 A(i) 상한 4종 + 총 제안 수 상한(R-13). 값 자체는
    `app.settings.LOOP_MAX_*` 가 단일 출처이고, 이 dataclass 는 그 턴에
    실제로 적용된 값을 trace 에 남기는 모양일 뿐이다."""

    mentions: int
    events: int
    schedules: int
    proposals: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "mentions": self.mentions,
            "events": self.events,
            "schedules": self.schedules,
            "proposals": self.proposals,
        }


@dataclass(frozen=True)
class GateVerdict:
    """`loop_gate.output` 스키마(01-plan 79~80행이 고정한 등식의 바탕).

    `accepted` = `executed[].index` ∪ `failed[].index` ∪
    `resume.pending_calls[].index` ∪ `{bucket == "hint_only"}` 의 인덱스
    (U1 등식, 네 집합은 서로 겹치지 않는다) -- 이 등식 자체는 U4/U5 가
    `run_turn`/`resume_turn` 안에서 지킨다. 이 타입은 등식이 설 수 있는
    **모양**만 고정한다.
    """

    accepted: list[AcceptedProposal] = field(default_factory=list)
    rejected: list[RejectedProposal] = field(default_factory=list)
    limits: GateLimits = field(default_factory=lambda: GateLimits(0, 0, 0, 0))
    stop_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": [a.to_dict() for a in self.accepted],
            "rejected": [r.to_dict() for r in self.rejected],
            "limits": self.limits.to_dict(),
            "stop_reason": self.stop_reason,
        }


# ---------------------------------------------------------------------------
# 기록 단계 초안 뷰 -- 응답 문장(결정 B(i))·로그가 쓰는 사람이 읽는 요약.
# 재개 재실행의 실제 근거는 `PendingCall`(제네릭 {index,name,args})이며,
# 이 두 타입은 그것과 별개의 보조 뷰다(R-25(ㄴ) -- 정확한 쓰임은 U4/U5 가
# 정한다. 이 단위는 모양만 고정한다).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EventDraft:
    """확정 전 `add_event` 제안의 요약 -- `person_id` 는 아직 없고 언급
    문자열(`mention`)만 있다."""

    mention: str
    type: str
    content: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.type not in EVENT_TYPES:
            raise InvalidValue(
                f"EventDraft.type must be one of {EVENT_TYPES} (got {self.type!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mention": self.mention,
            "type": self.type,
            "content": self.content,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class ScheduleDraft:
    """확정 전 `add_schedule` 제안의 요약. `scheduled_at` 이 아직 확정되지
    않았으면(결정 K(i)) `None` 이다 -- 그 경우 U5 는 `add_schedule` 을
    부르지 않고 `ask_user(kind="schedule")` 로 되묻는다."""

    mention: str
    title: str
    scheduled_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mention": self.mention,
            "title": self.title,
            "scheduled_at": (
                self.scheduled_at.isoformat() if self.scheduled_at is not None else None
            ),
        }


# ---------------------------------------------------------------------------
# 재개 재료 -- `pending_questions.context["resume"]` (M-0·M-1(d)·M-2(i))
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PendingCall:
    """아직 실행하지 않은 게이트 통과 제안 하나 -- 재개 재실행의 실제
    근거(제네릭, `ToolCallProposal` 과 같은 모양). `index` 는 되묻기가
    일어난 턴의 `loop_extract.output.tool_calls[]` 를 가리킨다."""

    index: int
    name: str
    args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "name": self.name, "args": dict(self.args)}


@dataclass(frozen=True)
class ScheduleResumeRef:
    """M-2(i) -- `schedule` 재개 질문이 실을 `add_schedule` 호출 재료.
    `person_id` 는 **루프가 현재 턴의 `apply_resolution()` merge 에서 얻은
    값을 저장한 것**이다(LLM 값이 아니다 -- 결정 L "바뀌지 않는 것" 절)."""

    person_id: int
    title: str
    call_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_id": self.person_id,
            "title": self.title,
            "call_index": self.call_index,
        }


@dataclass(frozen=True)
class PendingResume:
    """`pending_questions.context["resume"]` 키의 스키마(M-0 "새 결정이
    아니라 C·D·E·J 가 전제한 것을 실행 가능하게 적은 것"). 해당 없는
    질문 종류별 필드는 `to_dict()` 에 싣지 않는다(01-plan 83행).

    발화 원문(`utterance`)은 이 타입에 없다 -- ER 이 이미 `context["utterance"]`
    로 1건 넣었고 루프는 더 넣지 않는다(S3.4 13행 "전체 대화 이력 저장
    금지").

    `held_drafts`/`pending_calls` 의 구분(R-25(ㄴ)): `pending_calls` 는
    재개가 재실행할 제안(위 `PendingCall`)이고, `held_drafts` 는
    `LOOP_MAX_RESUME_BYTES` 초과 시 **버려지는** 보조 자료(예:
    `EventDraft`/`ScheduleDraft` 의 사람이 읽는 요약)다 -- 정확한 채움 규칙은
    U4/U5 가 정한다. 이 단위는 "버려도 `pending_calls` 는 유지된다"는
    모양만 고정한다(01-plan 83행 마지막 문장, 판정 표 24행).
    """

    version: str = LOOP_RESUME_VERSION
    mention: str = ""
    hints: dict[str, str] = field(default_factory=dict)
    pending_calls: list[PendingCall] = field(default_factory=list)
    held_drafts: list[dict[str, Any]] = field(default_factory=list)
    dropped: int = 0
    tag_by_answer: dict[str, str] | None = None
    schedule: ScheduleResumeRef | None = None
    schedule_options: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": self.version,
            "mention": self.mention,
            "hints": dict(self.hints),
            "pending_calls": [c.to_dict() for c in self.pending_calls],
            "held_drafts": [dict(d) for d in self.held_drafts],
            "dropped": self.dropped,
        }
        if self.tag_by_answer is not None:
            payload["tag_by_answer"] = dict(self.tag_by_answer)
        if self.schedule is not None:
            payload["schedule"] = self.schedule.to_dict()
        if self.schedule_options is not None:
            payload["schedule_options"] = dict(self.schedule_options)
        return payload


@dataclass(frozen=True)
class ResumeInput:
    """`resume_turn(ctx, resume_input)` 의 두 번째 인자(U7). `app.api.deps
    .load_resume_input`(U6/U7)이 `PendingQuestion` 행에서 `kind`·`context`
    (저장된 `pending_questions.context`, `PendingResume` 를 담은
    `"resume"` 키 포함)를 읽고, 라우트가 요청 본문의 답 문자열을 `answer`
    로 더해 이 타입을 만든다 -- `app/agent/` 는 `PendingQuestion` ORM 을
    직접 import 하지 않는다(판정 표 23행)."""

    kind: str
    context: dict[str, Any]
    answer: str

    def __post_init__(self) -> None:
        if self.kind not in QUESTION_KINDS:
            raise InvalidValue(
                f"ResumeInput.kind must be one of {QUESTION_KINDS} (got {self.kind!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "context": dict(self.context), "answer": self.answer}


# ---------------------------------------------------------------------------
# 턴 결과 -- `run_turn`/`resume_turn` 의 반환값 (U4 이후가 채운다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StoredSummary:
    """그 턴에 실제로 늘어난 행 수 -- `TurnResult.stored`(01-plan 79행
    "stored{persons,events,schedules}")."""

    persons: int = 0
    events: int = 0
    schedules: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"persons": self.persons, "events": self.events, "schedules": self.schedules}


@dataclass(frozen=True)
class TurnResult:
    """`run_turn`/`resume_turn`(U4~U7) 의 반환값 -- `ChatOut`/`AnswerOut`
    (U6/U7, `app/api/schemas.py`)이 이 값을 HTTP 응답으로 옮긴다.

    `pending_question` 은 되묻기로 끝난 턴에서만 채워진다(`app.tools.types
    .PendingQuestionOut` 재사용 -- 새 직렬화 방식을 만들지 않는다). 비어
    있으면(`None`) 그 턴은 되묻기 없이 끝난 것이다.
    """

    reply: str
    session_id: str
    stored: StoredSummary = field(default_factory=StoredSummary)
    pending_question: PendingQuestionOut | None = None
    stop_reason: str | None = None
    trace_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reply": self.reply,
            "session_id": self.session_id,
            "stored": self.stored.to_dict(),
            "pending_question": (
                self.pending_question.to_dict() if self.pending_question is not None else None
            ),
            "stop_reason": self.stop_reason,
            "trace_ids": list(self.trace_ids),
        }
