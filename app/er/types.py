"""Refs: P3-er S3.3 D3 D10 R4 -- 결정1 결정2 결정3 결정3-b 결정3-c 결정4
결정5 결정8. ER 4단계가 공유하는 데이터 계약.

`ScoredCandidate` 는 P2 `app.tools.types.Candidate`(1단계 `search_person`
의 출력) 를 감싸 2단계(규칙 필터, `app/er/rules.py`) 산출물을 더한 것이다.
`Judgement` 는 3단계(LLM 판정) 산출물, `Resolution`/`AppliedResolution` 은
4단계 확신도 분기 + trace 연결까지 담은 최종 산출물이다(결정4 -- 판정과
실행을 분리한다).

이 모듈은 **U3 시점에는 dataclass·상수·예외만** 정의한다. `er_config(env)`
환경변수 로더와 `app/settings.py` 의 `ER_*` 상수는 **U4(확신도 모듈) 몫**
이다(01-plan U3/U4 경계, U3 체크리스트) -- 여기서는 `ERConfig` 데이터클래스
생성 시 검증(결정8)까지만 한다. `resolve`/`apply_resolution`/`Judge`/
`FakeJudge`/`ClaudeJudge` 는 U5~U7 이 만든다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.settings import SEARCH_TOP_K
from app.tools.types import InvalidValue

#: `agent_traces` 예약값(결정5) -- ER 은 툴이 아니므로 `app.tools.TOOL_NAMES`
#: 에 넣지 않는다(P5 의 LLM 툴 스키마 생성기에 노출되지 않는다). 상수는 이
#: 모듈이 단일 출처이고 P4·P5 가 import 한다.
ER_TRACE_STEP = "er_resolve"
ER_TRACE_TOOL_NAME = "er"

#: trace `output.er_version` -- 스키마가 바뀌면 P4 가 구버전 trace 를
#: 구분할 수 있도록 올린다.
ER_VERSION = "1"

#: `ERConfig.__post_init__` 가 가중치 합 검증에 쓰는 허용 오차(결정8:
#: "가중치 합 1.0(오차 1e-9)").
_WEIGHT_SUM_TOLERANCE = 1e-9


class JudgeUnavailable(Exception):
    """3단계 LLM 판정 실패(타임아웃·API 오류·스키마 위반·범위 밖 `s_llm`,
    1회 재시도 후에도 실패 -- 결정3-c). 예외 메시지에는 응답 본문·프롬프트
    원문·키를 담지 않는다(security.md §1). 호출자(`pipeline.py`, U6)는 이
    예외를 잡아 `s_llm=0.0` + 규칙 통과 후보 유무에 따른 강제 강등으로
    바꾼다 -- 위로 다시 던지지 않는다(원칙1: 실패는 "죽는 것"이 아니라
    "묻는 것"으로 흡수한다)."""


class AlreadyApplied(InvalidValue):
    """`apply_resolution()`(U7, F-8809f2)이 같은 `Resolution`(같은
    `trace_id`)으로 두 번 불렸을 때 거부한다 -- trace 행의
    `output.decision.applied` 가 이미 `true` 면 이 예외를 던지고 **아무것도
    쓰지 않는다**(별칭·`pending_questions` 중복 생성 방지, 03-log U7 항목
    "거부(예외)" 채택 근거). `InvalidValue` 를 상속해 기존 `ToolError`
    계층에 편입시킨다 -- 새 예외 계층을 따로 만들지 않는다."""


@dataclass(frozen=True)
class ScoredCandidate:
    """2단계(규칙 필터, `app/er/rules.py`) 산출물을 담은 후보 하나.

    `s_emb` 는 P2 `Candidate.similarity` 를 옮겨 담은 이름이다(결정3-c --
    confidence 신호 이름 `s_llm`/`s_emb`/`s_rule` 과 맞춘다). `rule_flags`
    는 `search_person` 이 이미 채운 6개 신호(`exact_alias`·`partial_alias`·
    `hierarchy_match`·`relation_tag_match`·`hierarchy_adjacent`·
    `embedding_skipped`) 를 그대로 옮겨 담을 뿐이며, `rules.py` 는 이
    필드를 재계산하지 않는다(원본 신호와 규칙 필터 판정을 구분해 남긴다 --
    원칙9).

    `rule_checked`/`rule_passed`/`s_rule`/`passed_rules`/`excluded_by`/
    `relaxed_pass` 는 생성 시 기본값(미평가 상태)이고, `app/er/rules.py`
    의 `apply_rules()` 가 `dataclasses.replace()` 로 값을 채운 새 인스턴스를
    돌려준다(불변 dataclass -- 제자리 수정 없음).
    """

    person_id: int
    display_name: str
    aliases: list[str] = field(default_factory=list)
    relation_tag: str | None = None
    hierarchy: str | None = None
    s_emb: float = 0.0
    rule_flags: dict[str, bool] = field(default_factory=dict)
    rule_checked: int = 0
    rule_passed: int = 0
    s_rule: float = 0.0
    passed_rules: bool = False
    excluded_by: str | None = None
    relaxed_pass: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_id": self.person_id,
            "display_name": self.display_name,
            "aliases": list(self.aliases),
            "relation_tag": self.relation_tag,
            "hierarchy": self.hierarchy,
            "s_emb": self.s_emb,
            "rule_flags": dict(self.rule_flags),
            "rule_checked": self.rule_checked,
            "rule_passed": self.rule_passed,
            "s_rule": self.s_rule,
            "passed_rules": self.passed_rules,
            "excluded_by": self.excluded_by,
            "relaxed_pass": self.relaxed_pass,
        }


@dataclass(frozen=True)
class Judgement:
    """3단계(LLM 판정, `app/er/judge.py`) 산출물 -- 단일 판정(후보별 점수
    배열이 아니다, 결정3-c(a)).

    `s_llm` 은 **LLM 이 구조화 출력(도구/함수 호출)으로 자기보고한 0~1
    점수이며, 로그 확률이 아니다**(R4 -- 어떤 공급자의 API 도 토큰 로그
    확률을 제공하지 않는다). 이 사실은 `judge.py` 모듈 docstring 과 trace
    `llm.self_reported=true` 에도 반복해서 남긴다(R4 를 코드로 닫는 세
    지점 중 하나, 결정3(a)).

    `provider`(사용자 결정 2026-09-06, 공급자 중립 설계)는 실제 판정을
    수행한 공급자 이름(`"anthropic"`/`"openai"`/`"fake"`)이다 -- U5 의
    `judge.py` 가 `Judge` 를 공급자별로 구현하면서 trace `llm.provider`
    에 이 값을 그대로 남긴다. 기본값 `"fake"` 는 `FakeJudge` 가 흔히
    쓰이는 테스트 맥락과 맞춘 것일 뿐, 실제 공급자 구현은 언제나 이
    필드를 명시적으로 채운다.
    """

    matched_person_id: int | None
    s_llm: float
    reason: str
    tokens_in: int = 0
    tokens_out: int = 0
    model: str | None = None
    provider: str = "fake"

    def to_dict(self) -> dict[str, Any]:
        return {
            "matched_person_id": self.matched_person_id,
            "s_llm": self.s_llm,
            "reason": self.reason,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "model": self.model,
            "provider": self.provider,
        }


def _candidate_trace_dict(candidate: ScoredCandidate) -> dict[str, Any]:
    """`candidates[]` 의 trace 형태(결정5 output 스키마, U6). `similarity`
    는 `ScoredCandidate.s_emb`(이미 정규화·클램프된 값)를 그대로 옮긴 것이다
    -- U5(`app/er/candidates.py`)가 P2 `Candidate.similarity` 를 `s_emb` 로
    옮겨 담을 때 원래(클램프 전) 값을 별도로 보존하지 않으므로 두 키는 같은
    값이다(U6 인터페이스 한계, 03-log 명시). `aliases_matched` 도 같은
    이유로 `ScoredCandidate.aliases`(그 인물의 전체 별칭 목록, U5 가 채운
    것)를 그대로 쓴다 -- P2 `Candidate.aliases_matched`(질의와 실제로 일치한
    부분집합)는 U5 변환 과정에서 보존되지 않는다."""

    return {
        "person_id": candidate.person_id,
        "display_name": candidate.display_name,
        "similarity": candidate.s_emb,
        "aliases_matched": list(candidate.aliases),
        "rule_flags": dict(candidate.rule_flags),
        "passed_rules": candidate.passed_rules,
        "excluded_by": candidate.excluded_by,
        "rule_checked": candidate.rule_checked,
        "rule_passed": candidate.rule_passed,
        "relaxed_pass": candidate.relaxed_pass,
        "s_emb": candidate.s_emb,
        "s_rule": candidate.s_rule,
    }


@dataclass(frozen=True)
class Resolution:
    """4단계(확신도 분기, `app/er/confidence.py`) + 오케스트레이션
    (`app/er/pipeline.py`, U6) 산출물. **부수효과 없음**(결정4) -- `resolve()`
    는 `agent_traces` 행 1개만 쓰고 `persons`/`person_aliases`/
    `pending_questions` 는 건드리지 않는다.

    `trace_id` 는 `resolve()` 가 쓴 `er_resolve` 행의 id 다(U6, `app.tools.
    context.ToolContext.last_trace_id` 를 통해 채워진다) -- `apply_resolution`
    (U7)이 같은 행을 다시 찾아 `decision["applied"]`/`decision["pending_question_id"]`/
    `decision["applied_at"]` 세 값만 부분 갱신하는 열쇠다(결정4 "trace 행의
    갱신 주체").

    `to_dict()` 는 **결정5 trace `output` 스키마를 그대로** 낸다 --
    `{er_version, mention, relaxed_retry, candidates[], confidence_breakdown{},
    decision{}, llm{}}`. 이 dataclass 의 나머지 필드(`band`·`band_by_threshold`
    ·`forced_reason`·`matched_person_id`·`confidence`)는 `confidence_breakdown`/
    `decision` 과 같은 값의 **편의 접근자**일 뿐이며 `to_dict()` 출력에는
    중복해서 담지 않는다(이중 출처 방지 -- `confidence_breakdown`/`decision`
    dict 가 단일 출처).

    `candidates`(U6 시점부터 의미가 바뀐다 -- 이전 초안은 필드명만 정의):
    2단계(`run_rule_stage`)가 돌려준 **전체**(배제 후보 포함, `all_scored`)
    목록이다(원칙9 "배제도 근거다").

    `decision`(dict): `app.er.confidence.Decision.decision` 을 `resolve()`
    가 `relaxed_retry`/`hierarchy_relaxed_retry`/`applied`/`pending_question_id`
    /`applied_at` 다섯 키로 확장한 것(U4 03-log "U6/U7 인계" 그대로).

    `llm`(dict): `{provider, model, self_reported, s_llm, reason, tokens_in,
    tokens_out, attempts, skipped, error}` -- `Judgement` 를 그대로 옮기되
    스킵/실패 시 안전 기본값을 쓴다(U5 03-log "U6 인계" (3)).

    `suggested_display_name`(결정3-b): merge 구간은 별칭만 누적하고
    `display_name` 은 바꾸지 않는다 -- 확인을 거친 갱신에 쓰라고 후보
    이름을 여기 실어 P5 재개 경로에 넘긴다.
    """

    trace_id: int | None
    mention: str
    candidates: list[ScoredCandidate] = field(default_factory=list)
    relaxed_retry: bool = False
    matched_person_id: int | None = None
    confidence: float = 0.0
    confidence_breakdown: dict[str, Any] = field(default_factory=dict)
    band: str = "new_person"
    band_by_threshold: str = "new_person"
    forced_reason: str | None = None
    decision: dict[str, Any] = field(default_factory=dict)
    llm: dict[str, Any] = field(default_factory=dict)
    ask_payload: dict[str, Any] | None = None
    suggested_display_name: str | None = None

    def trace_tokens(self) -> tuple[int, int]:
        """`app.tools.context.traced()` 가 `tokens_in`/`tokens_out` 을
        채울 때 쓰는 규약(U1) -- ER 판정의 실제 LLM 사용량(`llm.tokens_in`/
        `tokens_out`)을 그대로 옮긴다. 스킵·실패 시 `llm` 이 이미 `0` 을
        담고 있으므로 별도 분기가 필요 없다."""
        tokens_in = self.llm.get("tokens_in", 0) or 0
        tokens_out = self.llm.get("tokens_out", 0) or 0
        return int(tokens_in), int(tokens_out)

    def to_dict(self) -> dict[str, Any]:
        return {
            "er_version": ER_VERSION,
            "mention": self.mention,
            "relaxed_retry": self.relaxed_retry,
            "candidates": [_candidate_trace_dict(c) for c in self.candidates],
            "confidence_breakdown": dict(self.confidence_breakdown),
            "decision": dict(self.decision),
            "llm": dict(self.llm),
        }


@dataclass(frozen=True)
class AppliedResolution:
    """`apply_resolution()`(U7, `app/er/pipeline.py`) 이 돌려주는 실행
    결과 -- `Resolution` 이 정한 행동(`band`)을 실제로 실행한 뒤의 사실만
    담는다(판정 필드는 `Resolution` 쪽에 그대로 있다, 결정4).

    `trace_id`/`band` 는 실행한 `Resolution` 을 가리키는 최소 참조다(U3
    초안은 `Resolution` 전체를 품었으나, U7 이 필드를 좁혔다 -- 판정
    dataclass 를 통째로 다시 담으면 trace `output` 과 이중 출처가 되고,
    호출자는 이미 `Resolution` 객체를 들고 있어 참조로 충분하다). `action`
    은 `app.er.confidence._ACTION_BY_BAND` 가 이미 계산한 값
    (`Resolution.decision["action"]`)을 그대로 옮긴 것이지 새로 판단하지
    않는다(이중 출처 금지). `alias_added` 는 `band == "merge"` 경로에서만
    `True` -- `update_person(new_alias=...)` 가 항상 upsert(신규 또는
    격상)로 끝나므로(`app/tools/persons.py._add_alias`) 예외 없이 `True`
    로 둔다.
    """

    trace_id: int
    band: str
    action: str  # "merge" | "ask_identity" | "ask_new_person"
    person_id: int | None = None
    pending_question_id: int | None = None
    applied_at: datetime | None = None
    alias_added: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "band": self.band,
            "action": self.action,
            "person_id": self.person_id,
            "pending_question_id": self.pending_question_id,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "alias_added": self.alias_added,
        }


@dataclass(frozen=True)
class ERConfig:
    """임계치·가중치는 설정값이면서 함수 인자다(결정8) -- 모듈 상수(이
    dataclass 의 기본값)가 1층, 환경변수(`.env.example` 의 `T_MERGE`/
    `T_NEW`/`W_LLM`/`W_EMB`/`W_RULE`, `er_config(env)` 로더는 **U4 몫**)가
    2층, `resolve(config=ERConfig(...))` 인자 주입이 3층(최우선)이다. P4
    가 `T_merge ∈ {0.5,…,0.95}` 를 한 프로세스 안에서 스윕해야 하므로
    (S3.7) 세 층을 둔다.

    생성 시 가중치 합 1.0(오차 1e-9)과 `0 ≤ t_new ≤ t_merge ≤ 1` 을
    검증한다 -- 위반하면 `InvalidValue`(원칙8: 튜닝은 P4 결과로만 하고,
    잘못된 설정으로 조용히 돌아가지 않는다).
    """

    t_merge: float = 0.8
    t_new: float = 0.3
    w_llm: float = 0.5
    w_emb: float = 0.3
    w_rule: float = 0.2
    top_k: int = SEARCH_TOP_K
    judge_timeout: float = 20.0
    judge_max_retries: int = 1

    def __post_init__(self) -> None:
        weight_sum = self.w_llm + self.w_emb + self.w_rule
        if abs(weight_sum - 1.0) > _WEIGHT_SUM_TOLERANCE:
            raise InvalidValue(
                f"ERConfig: weights must sum to 1.0 (got {weight_sum!r})"
            )
        if not (0.0 <= self.t_new <= self.t_merge <= 1.0):
            raise InvalidValue(
                "ERConfig: thresholds must satisfy 0 <= t_new <= t_merge <= 1 "
                f"(got t_new={self.t_new!r}, t_merge={self.t_merge!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        """U6 trace `input.config` 형태(위임 프롬프트 "input={mention, utterance,
        hints, config{t_merge,t_new,weights,top_k}}") -- `judge_timeout`/
        `judge_max_retries` 는 이 trace 입력 스키마에 없으므로 담지 않는다.
        `app.tools.context.to_jsonable` 이 `to_dict` 를 우선하므로,
        `resolve()` 가 `ERConfig` 인스턴스를 `@traced` 대상 함수에 그대로
        넘기면 이 메서드가 자동으로 쓰인다(이중 출처 없음)."""
        return {
            "t_merge": self.t_merge,
            "t_new": self.t_new,
            "weights": {"llm": self.w_llm, "emb": self.w_emb, "rule": self.w_rule},
            "top_k": self.top_k,
        }
