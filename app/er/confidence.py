"""Refs: P3-er P4b-er-redesign S3.3 D3 D10 D12 R4 결정2 결정3-c 결정5 결정8
-- 4단계(확신도 분기).

이 모듈은 **순수 함수만** 담는다 -- DB·LLM·임베딩 호출이 없다. 입력은
1~3단계(`app/er/candidates.py`·`rules.py`·`judge.py`)가 이미 만든 값이다.

## 허용오차는 단일 비교 함수 하나로만 (F-7fe239)

01-plan 은 `round(confidence, 6) >= round(T, 6)` 과 `math.isclose(abs_tol=1e-9)`
두 갈래를 적었다(28·43·111·201행). `round(·, 6)` 은 오차 폭이 최대 5e-7 이라
`T_merge - 5e-7` 같은 값을 merge 로 판정할 수 있다 -- 이것은 "`confidence`
가 `T_merge` 미만이면 `band != merge`"(원칙1·2, U4 스윕 테스트)와 정확히
반대 방향이다. 그래서 이 모듈은 `round()` 를 어디에도 쓰지 않고, 부동소수
**표현 오차**(예: `0.5*0.2 + 0.2*1.0 == 0.30000000000000004`)만 흡수하는
1e-9 급 단일 함수 `ge_with_tolerance()`(별칭 `_ge`) 하나로 모든 임계치
비교를 한다(`app.settings.ER_TOLERANCE` 가 그 오차의 단일 출처). 경계
테스트와 무작위 스윕 테스트가 같은 함수를 import 해 이 규약을 단언한다.

## s_llm 은 자기보고 점수다 (R4)

`Judgement.s_llm` 은 LLM 이 구조화 출력(tool_use)으로 **직접 보고한** 0~1
점수이며, Claude API 가 제공하지 않는 토큰 로그 확률이 아니다. 이 모듈의
`combine()` 은 그 값을 다른 두 신호와 가중합할 뿐 로그 확률을 계산하거나
가정하지 않는다.

## 관측된 신호만 재정규화한다 (D12, D3 대체)

`confidence = Σ_i w_i·s_i / Σ_i w_i` (i ∈ 관측된 신호). `combine()` 은
`s_rule` 이 **실제로 검사됐는지**를 `rule_checked`(`ScoredCandidate.
rule_checked`, 2단계가 채운 값)로 받는다 -- `s_rule` 자체의 크기가 아니라
"검사했는가"가 재정규화 여부를 가른다.

- `rule_checked > 0`(검사함 -- 전부 충돌해 `rule_passed == 0`인 경우도
  포함, D12 "코드에서 지켜야 할 것" 3항): D3 원식 그대로
  `w_llm*s_llm + w_emb*s_emb + w_rule*s_rule`. `s_rule` 은 그 값 그대로
  (충돌이면 보통 0) 합산된다 -- **재정규화하지 않는다**.
- `rule_checked == 0`(미측정 -- hints 가 비어 규칙을 하나도 검사하지
  못함): `s_rule` 을 분모에서 빼 `(w_llm*s_llm + w_emb*s_emb) /
  (w_llm + w_emb)`(기본 가중치에서 `0.625*s_llm + 0.375*s_emb`)를 쓴다.
  이때 `s_rule` 인자 값은 **완전히 무시된다**(호출부가 실수로 0 이 아닌
  값을 넘겨도 결과에 반영되지 않는다 -- 테스트가 이를 직접 확인한다).

`rule_checked` 를 생략하면 기본값 `1`(측정됨)로 취급해 D3 원식 그대로
계산한다 -- 옛 호출부(인자 없이 부르던 기존 테스트)가 그대로 통과하도록
하는 하위호환 기본값이다(P4b U1).

`confidence_breakdown` 에는 **`weights`(설정값, `ERConfig` 그대로)와
`weights_effective`(실제 적용된 재정규화 가중치)를 모두** 담는다
(`_effective_weights()`). 세 신호가 모두 관측되면 `weights_effective ==
weights`; `rule_checked == 0` 이면 `weights_effective == {llm: w_llm/(w_llm
+w_emb), emb: w_emb/(w_llm+w_emb), rule: 0.0}`. 강제 경로(`_forced_decision`
·`no_candidates`)도 `rule_checked=0` 으로 `_breakdown()` 을 부르므로
`weights_effective` 가 재정규화 값으로 채워진다 -- `confidence` 자체는
세 신호가 모두 0 이라 산식이 무엇이든 0.0 으로 같다(`--recheck-traces`
가 키 부재로 죽지 않게 하는 목적, D12 "코드에서 지켜야 할 것" 1·2·4항).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.er.types import Judgement, ScoredCandidate
from app.settings import ER_TOLERANCE
from app.tools.types import InvalidValue

#: `band` <-> `ask_user`/실행 어휘(`agent-observability` 스킬, 결정5 165행).
_ACTION_BY_BAND = {
    "merge": "merge",
    "identity": "ask_identity",
    "new_person": "ask_new_person",
}

#: `forced_reason` 이 이 값이면 U5/U6 이 `llm.error` 를 API 장애(`timeout`/
#: `api_error`/`schema`)와 구분해 기록할 수 있다(F-5a97ef).
OUT_OF_RANGE_ID = "out_of_range_id"


def ge_with_tolerance(a: float, b: float, tolerance: float = ER_TOLERANCE) -> bool:
    """`a >= b` 를 부동소수 표현 오차만 흡수해 판정하는 단일 비교 함수
    (F-7fe239). `round()` 를 쓰지 않는다 -- 이유는 모듈 docstring 참조.

    `band_for()`·경계 테스트·스윕 테스트가 전부 **이 함수 하나**를 통해
    임계치를 비교한다(이중 출처 금지, 원칙9).
    """
    return a >= b or math.isclose(a, b, abs_tol=tolerance)


#: 테스트가 "경계 테스트와 스윕 테스트가 같은 비교 함수를 쓰는가"를
#: import 로 직접 단언할 수 있도록 짧은 별칭도 공개한다(위임 프롬프트
#: "공개 `_ge`/`ge_with_tolerance` 를 import 해 단언").
_ge = ge_with_tolerance


def combine(
    s_llm: float,
    s_emb: float,
    s_rule: float,
    config: Any,
    *,
    rule_checked: int = 1,
) -> float:
    """세 신호를 `config` 의 가중치로 결합한다 -- **관측된 신호만**
    (D12, D3 대체): `rule_checked > 0` 이면 D3 원식 그대로
    `confidence = w_llm*s_llm + w_emb*s_emb + w_rule*s_rule`; `rule_checked
    == 0`(미측정)이면 `s_rule` 을 분모에서 빼 `(w_llm*s_llm + w_emb*s_emb)
    / (w_llm + w_emb)`. 두 분기의 연산 순서는 각각 D3 원식·재정규화 원식과
    같은 순서를 유지해 세 신호 관측 시 D3 원식과 **부동소수 오차 없이
    같은 값**이 되도록 한다(모듈 docstring "관측된 신호만 재정규화한다"
    참조). `rule_checked` 기본값 `1` 은 이 인자를 생략하는 기존 호출부가
    "측정됨"(재정규화 없음)으로 해석되게 하는 하위호환 기본값이다.

    `s_emb` 가 `[0, 1]` 밖이면 클램프한다(01-plan 43행 -- 코사인 유사도
    구현이나 합성 임베딩이 부동소수 오차로 살짝 벗어날 수 있다). `s_llm`·
    `s_rule` 은 상류(`judge.py`·`rules.py`)가 이미 `[0, 1]` 로 검증하지만,
    이 함수는 방어적으로 다시 확인해 벗어나면 `InvalidValue` 를 던진다
    (원칙8 -- 잘못된 입력으로 조용히 계산하지 않는다).
    """
    if not (0.0 <= s_llm <= 1.0):
        raise InvalidValue(f"combine: s_llm out of [0,1] range (got {s_llm!r})")
    if not (0.0 <= s_rule <= 1.0):
        raise InvalidValue(f"combine: s_rule out of [0,1] range (got {s_rule!r})")
    s_emb_clamped = min(1.0, max(0.0, s_emb))
    if rule_checked > 0:
        return config.w_llm * s_llm + config.w_emb * s_emb_clamped + config.w_rule * s_rule
    denom = config.w_llm + config.w_emb
    return (config.w_llm * s_llm + config.w_emb * s_emb_clamped) / denom


def _effective_weights(rule_checked: int, config: Any) -> dict[str, float]:
    """`confidence_breakdown["weights_effective"]` 의 단일 출처(D12) --
    `combine()` 과 **같은 조건**(`rule_checked > 0`)으로 갈린다. 관측되면
    설정 가중치 그대로, 미측정이면 `w_llm`·`w_emb` 만 재정규화하고 `rule`
    은 0.0 이다."""
    if rule_checked > 0:
        return {"llm": config.w_llm, "emb": config.w_emb, "rule": config.w_rule}
    denom = config.w_llm + config.w_emb
    return {"llm": config.w_llm / denom, "emb": config.w_emb / denom, "rule": 0.0}


def band_for(confidence: float, config: Any) -> str:
    """확신도 → 구간(D10 원칙1·2). `>= T_merge` 는 `"merge"`, `>= T_new` 는
    `"identity"`, 그 외 `"new_person"`. 정확히 `T_merge`/`T_new` 인 값은
    `>=` 쪽으로 판정된다(`ge_with_tolerance()` 단일 비교, F-7fe239)."""
    if ge_with_tolerance(confidence, config.t_merge):
        return "merge"
    if ge_with_tolerance(confidence, config.t_new):
        return "identity"
    return "new_person"


@dataclass(frozen=True)
class Decision:
    """4단계 산출물 -- 결정5 trace 스키마의 `confidence_breakdown`·
    `decision` 두 객체를 만든다(`applied`/`pending_question_id`/
    `applied_at` 세 필드는 U6/`apply_resolution` 이 나중에 채운다).

    `matched_person_id`(최상위)는 **귀속에 실제로 쓰인** 값이다 -- null·
    llm_failed·out_of_range·no_candidates 경로에서는 전부 `None` 이고,
    정상 경로에서만 `judgement.matched_person_id` 값을 갖는다(결정3-c
    불변식: `matched_person_id is None` 이면 어떤 경로든 `band != "merge"`).

    `llm_error_kind` 는 `out_of_range_id` 판정을 API 장애와 구분해 U5/U6
    이 `llm.error` 에 남길 수 있게 하는 표시다(F-5a97ef). 그 외 경로는
    `None`.
    """

    confidence: float
    confidence_breakdown: dict[str, Any]
    band: str
    band_by_threshold: str
    forced_reason: str | None
    action: str
    decision: dict[str, Any]
    matched_person_id: int | None
    llm_error_kind: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence": self.confidence,
            "confidence_breakdown": dict(self.confidence_breakdown),
            "band": self.band,
            "band_by_threshold": self.band_by_threshold,
            "forced_reason": self.forced_reason,
            "action": self.action,
            "decision": dict(self.decision),
            "matched_person_id": self.matched_person_id,
            "llm_error_kind": self.llm_error_kind,
        }


def _breakdown(
    *,
    matched_person_id: int | None,
    s_llm: float,
    s_emb: float,
    s_rule: float,
    confidence: float,
    rule_checked: int,
    rule_passed: int,
    config: Any,
) -> dict[str, Any]:
    return {
        "matched_person_id": matched_person_id,
        "s_llm": s_llm,
        "s_emb": s_emb,
        "s_rule": s_rule,
        "weights": {"llm": config.w_llm, "emb": config.w_emb, "rule": config.w_rule},
        "weights_effective": _effective_weights(rule_checked, config),
        "confidence": confidence,
        "rule_checked": rule_checked,
        "rule_passed": rule_passed,
    }


def _decision_payload(
    *,
    band: str,
    band_by_threshold: str,
    forced_reason: str | None,
    action: str,
    matched_person_id: int | None,
    config: Any,
) -> dict[str, Any]:
    return {
        "band": band,
        "band_by_threshold": band_by_threshold,
        "forced_reason": forced_reason,
        "action": action,
        "T_merge": config.t_merge,
        "T_new": config.t_new,
        "matched_person_id": matched_person_id,
    }


def _forced_decision(
    *,
    forced_reason: str,
    passed: list[ScoredCandidate],
    config: Any,
    llm_error_kind: str | None = None,
) -> Decision:
    """null(`no_matched`)·llm_failed·out_of_range_id 세 경로가 공유하는
    귀속 규약(결정3-c(b), F-f3b245, F-5a97ef): `matched_person_id=None`,
    `s_llm=s_emb=s_rule=0`, `confidence=0`, `band_by_threshold=band_for(0)`
    (`= "new_person"`, `t_new > 0` 인 통상 설정에서). 최종 `band` 는 통과
    후보 유무로만 갈린다 -- `no_candidates` 경로는 이 helper 를 쓰지 않고
    별도로 처리한다(통과 후보가 이미 0 임을 호출부가 안다)."""
    confidence = 0.0
    band_by_threshold = band_for(confidence, config)
    band = "identity" if passed else "new_person"
    breakdown = _breakdown(
        matched_person_id=None,
        s_llm=0.0,
        s_emb=0.0,
        s_rule=0.0,
        confidence=confidence,
        rule_checked=0,
        rule_passed=0,
        config=config,
    )
    decision_payload = _decision_payload(
        band=band,
        band_by_threshold=band_by_threshold,
        forced_reason=forced_reason,
        action=_ACTION_BY_BAND[band],
        matched_person_id=None,
        config=config,
    )
    return Decision(
        confidence=confidence,
        confidence_breakdown=breakdown,
        band=band,
        band_by_threshold=band_by_threshold,
        forced_reason=forced_reason,
        action=_ACTION_BY_BAND[band],
        decision=decision_payload,
        matched_person_id=None,
        llm_error_kind=llm_error_kind,
    )


def decide(
    *,
    judgement: Judgement | None,
    passed: list[ScoredCandidate],
    llm_failed: bool,
    config: Any,
) -> Decision:
    """4단계 확신도 분기(D10 원칙1·2, 결정3-c, 결정5). 경로별 규약:

    - **통과 후보 0건**(34행): `judgement`/`llm_failed` 와 무관하게 최우선
      -- `s_llm=s_emb=s_rule=0`, `band=band_by_threshold="new_person"`,
      `forced_reason="no_candidates"`.
    - **llm_failed**(결정3(c)·F-f3b245): null 과 같은 귀속(`matched_person_id
      =None`, 세 신호 0) + `forced_reason="llm_failed"`, 통과 후보 유무로
      `band` 가 `identity`/`new_person` 로 갈린다.
    - **범위 밖 id**(F-5a97ef): `judgement.matched_person_id` 가 통과 후보
      id 집합(`passed` 의 `person_id` 들) ∪ `{None}` 밖이면 llm_failed 와
      같은 귀속을 쓰되 `llm_error_kind="out_of_range_id"` 를 함께 돌려준다.
    - **null**(결정3-c(b)): `judgement.matched_person_id is None` -> llm_failed
      와 같은 귀속, `forced_reason="no_matched"`.
    - **정상**: `judgement.matched_person_id` 로 통과 후보 하나에 귀속해
      `s_emb`/`s_rule`/`rule_checked`/`rule_passed` 를 그 후보에서 가져오고
      `combine()`·`band_for()` 로 산식 그대로 판정한다(`forced_reason=None`).

    불변식: `matched_person_id is None` 이면 어떤 경로든 `band != "merge"`.
    """
    if not passed:
        confidence = 0.0
        breakdown = _breakdown(
            matched_person_id=None,
            s_llm=0.0,
            s_emb=0.0,
            s_rule=0.0,
            confidence=confidence,
            rule_checked=0,
            rule_passed=0,
            config=config,
        )
        band = "new_person"
        decision_payload = _decision_payload(
            band=band,
            band_by_threshold=band,
            forced_reason="no_candidates",
            action=_ACTION_BY_BAND[band],
            matched_person_id=None,
            config=config,
        )
        return Decision(
            confidence=confidence,
            confidence_breakdown=breakdown,
            band=band,
            band_by_threshold=band,
            forced_reason="no_candidates",
            action=_ACTION_BY_BAND[band],
            decision=decision_payload,
            matched_person_id=None,
        )

    if llm_failed:
        return _forced_decision(forced_reason="llm_failed", passed=passed, config=config)

    if judgement is None:
        # 통과 후보가 있는데 judgement 도 없고 llm_failed 도 아니면 호출
        # 계약 위반이다(U6 오케스트레이션 버그) -- 조용히 넘기지 않는다.
        raise InvalidValue(
            "decide: judgement is None but llm_failed=False and passed "
            "candidates exist -- caller must pass llm_failed=True or a "
            "Judgement"
        )

    passed_ids = {c.person_id for c in passed}

    if judgement.matched_person_id is None:
        return _forced_decision(forced_reason="no_matched", passed=passed, config=config)

    if judgement.matched_person_id not in passed_ids:
        return _forced_decision(
            forced_reason="llm_failed",
            passed=passed,
            config=config,
            llm_error_kind=OUT_OF_RANGE_ID,
        )

    candidate = next(c for c in passed if c.person_id == judgement.matched_person_id)
    s_llm = judgement.s_llm
    s_emb = candidate.s_emb
    s_rule = candidate.s_rule
    confidence = combine(s_llm, s_emb, s_rule, config, rule_checked=candidate.rule_checked)
    band = band_for(confidence, config)

    breakdown = _breakdown(
        matched_person_id=judgement.matched_person_id,
        s_llm=s_llm,
        s_emb=s_emb,
        s_rule=s_rule,
        confidence=confidence,
        rule_checked=candidate.rule_checked,
        rule_passed=candidate.rule_passed,
        config=config,
    )
    decision_payload = _decision_payload(
        band=band,
        band_by_threshold=band,
        forced_reason=None,
        action=_ACTION_BY_BAND[band],
        matched_person_id=judgement.matched_person_id,
        config=config,
    )
    return Decision(
        confidence=confidence,
        confidence_breakdown=breakdown,
        band=band,
        band_by_threshold=band,
        forced_reason=None,
        action=_ACTION_BY_BAND[band],
        decision=decision_payload,
        matched_person_id=judgement.matched_person_id,
    )
