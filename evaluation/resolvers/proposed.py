"""Refs: P3-baselines S3.3 D3 D10 원칙1 원칙9 -- 제안 4단계 하이브리드 어댑터.

**두 임계치**(불변 규약 4): 이 어댑터는 `config`(`ERConfig`)를
`app.er.resolve()` 에 **그대로 넘기기만** 하고, `T_merge`/`T_new` 는
`app.er.confidence.band_for()` 가 파이프라인 안에서 적용한다 -- 어댑터는
임계치를 읽지도 재정의하지도 않으므로 P4 의 `T_merge` 스윕(S3.7)이
제품 경로의 분기를 그대로 움직인다.

## 이 모듈이 하는 일 = 자료형 변환뿐

`evaluation/` 은 `app/` 을 **부르기만** 한다(`evaluation/__init__.py` 의
의존 방향). 이 어댑터는 `app.er.resolve(ctx, mention, utterance, hints,
judge=…, config=…)` 를 한 번 부르고 그 `Resolution` 을 `MentionDecision`
으로 옮긴다. **`app/er/` 는 한 줄도 고치지 않는다**(01-plan 54행) --
네 방식을 같은 형태로 비교하기 위해 필요한 변환은 전부 이쪽에서 한다.
그래서 "제안 방식"의 성능은 제품 코드 그대로의 성능이고, 어댑터가
판정에 개입한 지점이 없다(원칙8).

변환표(01-plan U2):

| `Resolution`                    | `MentionDecision`                    |
|---------------------------------|--------------------------------------|
| `band`                          | `decision`                           |
| `matched_person_id`             | `person_id` (**`merge` 일 때만**)     |
| `confidence`                    | `score`                              |
| `candidates[]`(배제 포함 전체)   | `candidates[]` + `signals{s_emb,s_rule,규칙 신호}` |
| `trace_id`                      | `trace_id` = `detail["trace_id"]`     |
| `forced_reason`·`relaxed_retry` | `detail`                             |
| `llm.provider`·`llm.model`      | `detail`                             |
| `llm.tokens_in/out`             | `tokens_in`/`tokens_out`             |
| `confidence_breakdown`          | `detail["confidence_breakdown"]`(3신호 분해, D3) |

`trace_id` 는 전용 필드와 `detail["trace_id"]` 두 곳에 같은 값으로 담긴다
(base.py 는 전용 필드를 두고 01-plan 54·101행은 `detail` 을 요구한다).
값의 출처는 `resolution.trace_id` 하나뿐이라 두 곳이 갈라질 수 없다.

## 부수효과 0 (불변 규약 1, 원칙1)

`resolve()` 는 판정만 하고 실행하지 않는다(P3-er 결정4). 이 어댑터는
`apply_resolution()` 을 **부르지 않으므로** `persons`·`person_aliases`·
`pending_questions` 가 그대로다 -- 병합도 질문 저장도 일어나지 않는다.
남는 것은 `resolve()` 가 쓰는 `agent_traces` 행(그리고 그 안에서 부른
`search_person` 의 `tool_call` 행)뿐이고, 그것은 감싼 함수의 성질이다
(base.py 불변 규약 1). `ask_user` 가 무엇을 물었을지는 `detail["ask_kind"]`
로만 남긴다 -- P4 의 `ask_user_rate_by_kind`(eval-harness §2) 입력이다.

## 예외 비대칭 금지 (불변 규약 2, 원칙8)

`resolve()` 는 LLM 실패·후보 0건을 이미 밴드 강등으로 흡수한다
(`forced_reason` = `llm_failed`/`no_candidates`/`no_matched`). 어댑터는
그 값을 그대로 옮기고 예외로 바꾸지 않는다. 어댑터 자신의 방어(밴드가
`merge` 인데 `matched_person_id` 가 없는 도달 불가 조합, `score` 범위
이탈)도 예외 대신 `detail["adapter_forced_reason"]` 으로 남긴다 -- 한
방식만 예외로 죽으면 분모가 달라져 비교가 깨진다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.er.pipeline import resolve as er_resolve
from app.er.types import Resolution, ScoredCandidate
from evaluation.resolvers.base import DECISIONS, MentionDecision, ResolverCandidate
from evaluation.resolvers.registry import register

if TYPE_CHECKING:
    from app.er.judge import Judge
    from app.er.types import ERConfig
    from app.tools.context import ToolContext

#: `RESOLVERS` 등록 이름 = `MentionDecision.method` = `metrics.json` 키
#: (P4 인계 4). 바꾸면 P4 산출물 스키마가 바뀐다.
METHOD_NAME = "proposed"

#: `ask_user` 를 부르지 않으므로(불변 규약 1) `kind` 는 밴드에서 유도한다.
#: `app.er.pipeline._build_ask_payload` 가 만드는 `ask_payload["kind"]` 와
#: 같은 대응이며, `merge` 는 묻지 않으므로 `None` 이다.
_ASK_KIND_BY_BAND: dict[str, str | None] = {
    "merge": None,
    "identity": "identity",
    "new_person": "new_person",
}


def _clamp_unit(value: float) -> tuple[float, bool]:
    """`score` 를 `[0, 1]` 로 접는다. `MentionDecision.__post_init__` 이
    범위를 강제하므로, 부동소수 오차나 장래의 산식 변경으로 범위를 벗어난
    값이 오면 여기서 예외 대신 접고 그 사실을 `detail` 에 남긴다(불변 규약
    2). 현재 산식(가중치 합 1.0 × 각 신호 `[0,1]`)에서는 접힐 일이 없다."""

    numeric = float(value)
    if numeric != numeric:  # NaN
        return 0.0, True
    if numeric < 0.0:
        return 0.0, True
    if numeric > 1.0:
        return 1.0, True
    return numeric, False


def _candidate_signals(candidate: ScoredCandidate) -> dict[str, float]:
    """후보 하나의 **원자료**(원칙9 -- 배제된 후보도 근거다).

    `s_emb`·`s_rule` 은 확신도 산식의 두 신호(D3)이고, `rule_flags` 6개
    (`exact_alias`·`partial_alias`·`hierarchy_match`·`relation_tag_match`·
    `hierarchy_adjacent`·`embedding_skipped`)는 `search_person` 이 채운
    그대로다. `signals` 는 `dict[str, float]` 이므로 불리언은 `1.0`/`0.0`
    으로 옮긴다(키 이름은 바꾸지 않는다 -- P4 가 이름으로 찾는다).
    배제 사유(`excluded_by`, 문자열)는 수치가 아니므로
    `detail["excluded_by"]` 로 간다."""

    signals: dict[str, float] = {
        "s_emb": float(candidate.s_emb),
        "s_rule": float(candidate.s_rule),
        "rule_checked": float(candidate.rule_checked),
        "rule_passed": float(candidate.rule_passed),
        "passed_rules": 1.0 if candidate.passed_rules else 0.0,
        "relaxed_pass": 1.0 if candidate.relaxed_pass else 0.0,
    }
    for flag, value in candidate.rule_flags.items():
        signals[str(flag)] = 1.0 if value else 0.0
    return signals


def to_mention_decision(resolution: Resolution, mention: str) -> MentionDecision:
    """`Resolution` -> `MentionDecision` 순수 변환(DB·네트워크 없음).

    `mention` 을 따로 받는 이유: `Resolution.mention` 이 이미 같은 값이지만,
    호출자가 넘긴 원문을 그대로 쓰는 편이 "무엇을 물었나"의 단일 출처가
    호출자 쪽에 남는다(P4 러너는 골드 라벨의 `surface` 로 맞춘다).
    """

    band = resolution.band
    forced_reason = resolution.forced_reason
    adapter_forced_reason: str | None = None

    if band not in DECISIONS:  # 도달 불가(밴드 어휘는 D10 로 고정) -- 방어.
        adapter_forced_reason = f"unknown_band:{band}"
        band = "identity"

    person_id = resolution.matched_person_id if band == "merge" else None
    if band == "merge" and person_id is None:
        # `decide()` 는 `matched_person_id=None` 을 이미 `no_matched` 로
        # 강등하므로 도달하지 않는다. 그래도 여기서 죽지 않고 강등한다.
        adapter_forced_reason = "merge_without_person_id"
        band = "identity"

    score, clamped = _clamp_unit(resolution.confidence)

    candidates = [
        ResolverCandidate(
            person_id=candidate.person_id,
            display_name=candidate.display_name,
            # 제안 방식은 후보별 결합 확신도를 계산하지 않는다(3단계 LLM 이
            # 단일 판정을 낸다 -- P3-er 결정3-c(a)). 그래서 확신도를 가진
            # 후보는 판정된 하나뿐이고 나머지는 `0.0`("점수 없음",
            # base.py `ResolverCandidate.score`)이다. 후보별 원자료는
            # `signals` 에 그대로 있다.
            score=score if candidate.person_id == resolution.matched_person_id else 0.0,
            signals=_candidate_signals(candidate),
        )
        for candidate in resolution.candidates
    ]

    llm: dict[str, Any] = resolution.llm
    detail: dict[str, Any] = {
        "trace_id": resolution.trace_id,
        "forced_reason": forced_reason,
        "relaxed_retry": bool(resolution.relaxed_retry),
        # 강제 강등 여부는 `band` 와 `band_by_threshold` 의 차이로 드러난다
        # (원칙9) -- P4 가 "임계치 때문에 물었나, 실패해서 물었나"를 가른다.
        "band_by_threshold": resolution.band_by_threshold,
        "provider": llm.get("provider"),
        "model": llm.get("model"),
        "llm_self_reported": llm.get("self_reported"),
        "llm_skipped": llm.get("skipped"),
        "llm_attempts": llm.get("attempts"),
        "llm_error": llm.get("error"),
        # 3신호 분해(D3, 원칙3) -- P4 보정표(`s_llm` 구간별 정답률,
        # eval-harness §2 `calibration`)의 입력이다.
        "confidence_breakdown": dict(resolution.confidence_breakdown),
        # 실행하지 않으므로(불변 규약 1) 물었을 `kind` 만 남긴다 --
        # P4 `ask_user_rate_by_kind` 입력.
        "ask_kind": _ASK_KIND_BY_BAND.get(band),
        "excluded_by": {
            str(candidate.person_id): candidate.excluded_by
            for candidate in resolution.candidates
            if candidate.excluded_by is not None
        },
    }
    if adapter_forced_reason is not None:
        detail["adapter_forced_reason"] = adapter_forced_reason
    if clamped:
        detail["score_clamped"] = True

    tokens_in, tokens_out = resolution.trace_tokens()

    return MentionDecision(
        method=METHOD_NAME,
        mention=mention,
        decision=band,
        person_id=person_id,
        score=score,
        candidates=candidates,
        trace_id=resolution.trace_id,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        detail=detail,
    )


@register(METHOD_NAME)
class ProposedResolver:
    """제안 4단계 하이브리드(`app.er.resolve`)를 `Resolver` 계약으로 감싼다.

    `judge` 는 **팩토리 인자**다::

        get_resolver("proposed", judge=FakeJudge(table={pid: 0.9}))

    `None` 이면 `app.er.resolve()` 가 `judge_from_env()`(공급자 팩토리)를
    쓴다 -- 자동 테스트는 언제나 `FakeJudge` 를 주입해 실 API 호출 없이
    결정적으로 돈다(P3-er 결정9, 원칙8 재현성). P4 러너가 실 공급자로
    돌릴 때는 인자를 주지 않고 환경변수에 맡긴다.

    `supported_decisions` 는 세 밴드 전부다 -- 제안 방식은 `identity` 를
    낼 수 있고(오히려 그것이 원칙1 의 핵심 행동이다) `new_person` 도 낸다.
    """

    name: str = METHOD_NAME
    supported_decisions: tuple[str, ...] = DECISIONS

    def __init__(self, judge: Judge | None = None) -> None:
        self.judge = judge

    def resolve_mention(
        self,
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: ERConfig | None = None,
    ) -> MentionDecision:
        """`app.er.resolve()` 1회 -> 변환 1회. 그 사이에 어떤 판단도 넣지
        않는다. `config=None` 은 그대로 넘겨 `er_config()`(환경변수 2층,
        P3-er 결정8)가 쓰이게 한다 -- 어댑터가 기본값을 새로 정하면
        네 방식의 설정 출처가 갈라진다(불변 규약 4)."""

        resolution = er_resolve(
            ctx,
            mention,
            utterance,
            hints,
            judge=self.judge,
            config=config,
        )
        return to_mention_decision(resolution, mention)
