"""Refs: P3-er U4 D3 D10 원칙1 원칙2 결정2 결정3-c 결정5 결정8 F-7fe239
F-f3b245 F-5a97ef -- `app/er/confidence.py` 단위 테스트. DB·LLM 없음
(순수 함수만 검증한다).
"""

from __future__ import annotations

import math
import random

import pytest

from app.er.confidence import (
    OUT_OF_RANGE_ID,
    Decision,
    band_for,
    combine,
    decide,
    ge_with_tolerance,
)
from app.er.confidence import _ge  # noqa: F401 -- 별칭이 같은 객체인지 확인용
from app.er.types import ERConfig, Judgement, ScoredCandidate
from app.settings import ER_TOLERANCE, er_config
from app.tools.types import InvalidValue


def _candidate(person_id: int, *, s_emb: float, s_rule: float, rule_checked: int = 2, rule_passed: int = 1) -> ScoredCandidate:
    return ScoredCandidate(
        person_id=person_id,
        display_name=f"person-{person_id}",
        aliases=[f"alias-{person_id}"],
        s_emb=s_emb,
        rule_checked=rule_checked,
        rule_passed=rule_passed,
        s_rule=s_rule,
        passed_rules=True,
    )


# ---------------------------------------------------------------------------
# 비교 함수 단일 출처 확인
# ---------------------------------------------------------------------------


def test_ge_with_tolerance_is_the_same_object_as_private_alias() -> None:
    assert _ge is ge_with_tolerance


# ---------------------------------------------------------------------------
# boundary — 경계값·부동소수 조합 (F-7fe239 회귀)
# ---------------------------------------------------------------------------


def test_boundary_exactly_t_merge_is_merge() -> None:
    config = ERConfig()
    assert band_for(config.t_merge, config) == "merge"


def test_boundary_exactly_t_new_is_identity() -> None:
    config = ERConfig()
    assert band_for(config.t_new, config) == "identity"


def test_boundary_floating_point_combo_0_3000000000000004() -> None:
    # 0.5*0.2 + 0.2*1.0 == 0.30000000000000004 (표현 오차) — T_new=0.3 이므로
    # identity 쪽으로 판정되어야 한다 (>= 0.3).
    config = ERConfig()
    confidence = combine(s_llm=0.2, s_emb=0.0, s_rule=1.0, config=config)
    assert confidence == 0.30000000000000004
    assert band_for(confidence, config) == "identity"


def test_boundary_sum_over_one_no_extra_clamp_on_confidence() -> None:
    # combine() 은 `config.w_*` 속성만 읽는다(ERConfig 타입을 강제하지
    # 않는다) -- 가중치 합이 1 을 넘는 (검증되지 않은) 설정을 흉내 낸 값을
    # 직접 넣어, 최종 confidence 자체는 클램프하지 않는지 확인한다
    # (s_emb 클램프는 개별 입력에만 적용된다). 0.6*1.0 + 0.3*1.0 + 0.2*1.0 = 1.1.
    class _FakeWeights:
        w_llm = 0.6
        w_emb = 0.3
        w_rule = 0.2

    confidence = combine(s_llm=1.0, s_emb=1.0, s_rule=1.0, config=_FakeWeights())
    assert math.isclose(confidence, 1.1, rel_tol=0, abs_tol=1e-12)
    config = ERConfig()
    assert band_for(confidence, config) == "merge"


def test_boundary_t_merge_minus_5e7_is_not_merge_round_regression() -> None:
    # round(confidence, 6) 이었다면 T_merge - 5e-7 도 merge 로 판정됐을 값
    # (F-7fe239 회귀) -- 1e-9 급 허용오차에서는 merge 가 아니어야 한다.
    config = ERConfig()
    confidence = config.t_merge - 5e-7
    assert band_for(confidence, config) != "merge"
    assert ge_with_tolerance(confidence, config.t_merge) is False


def test_boundary_t_merge_minus_5e10_is_merge_within_tolerance() -> None:
    config = ERConfig()
    confidence = config.t_merge - 5e-10
    assert band_for(confidence, config) == "merge"
    assert ge_with_tolerance(confidence, config.t_merge) is True


# ---------------------------------------------------------------------------
# threshold — 무작위 스윕 (원칙1·2: T_merge 미만·null·llm_failed 는 merge 금지)
# ---------------------------------------------------------------------------


def test_threshold_sweep_confidence_below_t_merge_never_merges() -> None:
    rng = random.Random(20260906)
    t_merge_values = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    count = 0
    for _ in range(2000):
        t_merge = rng.choice(t_merge_values)
        t_new = rng.uniform(0.0, t_merge)
        config = ERConfig(t_new=t_new, t_merge=t_merge)
        confidence = rng.uniform(0.0, 1.0)
        if confidence < t_merge - ER_TOLERANCE * 10:
            band = band_for(confidence, config)
            assert band != "merge", (confidence, t_merge, band)
            count += 1
    assert count > 500  # 스윕이 실제로 다수 조합을 검사했는지 확인.


def test_threshold_sweep_null_matched_person_id_never_merges() -> None:
    rng = random.Random(20260906)
    t_merge_values = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    count = 0
    for i in range(2000):
        t_merge = rng.choice(t_merge_values)
        t_new = rng.uniform(0.0, t_merge)
        config = ERConfig(t_new=t_new, t_merge=t_merge)
        n_passed = rng.randint(0, 3)
        passed = [
            _candidate(pid, s_emb=rng.uniform(0, 1), s_rule=rng.uniform(0, 1))
            for pid in range(n_passed)
        ]
        judgement = Judgement(matched_person_id=None, s_llm=rng.uniform(0, 1), reason="r")
        result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
        assert result.band != "merge", (t_merge, t_new, n_passed, result.band)
        count += 1
    assert count == 2000


def test_threshold_sweep_llm_failed_never_merges() -> None:
    rng = random.Random(20260906)
    t_merge_values = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    count = 0
    for _ in range(2000):
        t_merge = rng.choice(t_merge_values)
        t_new = rng.uniform(0.0, t_merge)
        config = ERConfig(t_new=t_new, t_merge=t_merge)
        n_passed = rng.randint(0, 3)
        passed = [
            _candidate(pid, s_emb=rng.uniform(0, 1), s_rule=rng.uniform(0, 1))
            for pid in range(n_passed)
        ]
        result = decide(judgement=None, passed=passed, llm_failed=True, config=config)
        assert result.band != "merge", (t_merge, t_new, n_passed, result.band)
        count += 1
    assert count == 2000


def test_threshold_sweep_uses_same_comparison_function_as_boundary() -> None:
    # 스윕·경계 테스트가 같은 비교 함수를 쓰는지 -- band_for 내부가
    # ge_with_tolerance 를 호출한다는 것을 값으로 교차검증.
    config = ERConfig()
    for confidence in (config.t_merge, config.t_merge - 1e-10, config.t_merge - 1e-6):
        expected = "merge" if ge_with_tolerance(confidence, config.t_merge) else (
            "identity" if ge_with_tolerance(confidence, config.t_new) else "new_person"
        )
        assert band_for(confidence, config) == expected


# ---------------------------------------------------------------------------
# ERConfig 검증 경유 (가중치 합·임계치 순서)
# ---------------------------------------------------------------------------


def test_weights_must_sum_to_one_rejected_via_combine_config() -> None:
    with pytest.raises(InvalidValue):
        ERConfig(w_llm=0.5, w_emb=0.5, w_rule=0.5)


def test_t_new_greater_than_t_merge_rejected() -> None:
    with pytest.raises(InvalidValue):
        ERConfig(t_new=0.9, t_merge=0.5)


# ---------------------------------------------------------------------------
# combine() — s_rule 분모 0, s_emb 클램프, 자기보고 범위 검증
# ---------------------------------------------------------------------------


def test_combine_s_rule_zero_input_reflected_directly() -> None:
    config = ERConfig()
    confidence = combine(s_llm=1.0, s_emb=1.0, s_rule=0.0, config=config)
    assert math.isclose(confidence, 0.8, abs_tol=1e-12)


def test_combine_s_emb_above_one_is_clamped() -> None:
    config = ERConfig()
    confidence_clamped = combine(s_llm=0.0, s_emb=5.0, s_rule=0.0, config=config)
    confidence_at_one = combine(s_llm=0.0, s_emb=1.0, s_rule=0.0, config=config)
    assert confidence_clamped == confidence_at_one


def test_combine_s_emb_below_zero_is_clamped() -> None:
    config = ERConfig()
    confidence_clamped = combine(s_llm=0.0, s_emb=-5.0, s_rule=0.0, config=config)
    assert confidence_clamped == 0.0


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_combine_s_llm_out_of_range_rejected(bad: float) -> None:
    config = ERConfig()
    with pytest.raises(InvalidValue):
        combine(s_llm=bad, s_emb=0.5, s_rule=0.5, config=config)


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_combine_s_rule_out_of_range_rejected(bad: float) -> None:
    config = ERConfig()
    with pytest.raises(InvalidValue):
        combine(s_llm=0.5, s_emb=0.5, s_rule=bad, config=config)


# ---------------------------------------------------------------------------
# er_config(env) — 환경변수 로더
# ---------------------------------------------------------------------------


def test_er_config_defaults_when_env_missing() -> None:
    config = er_config({})
    assert config.t_merge == 0.8
    assert config.t_new == 0.3
    assert config.w_llm == 0.5
    assert config.w_emb == 0.3
    assert config.w_rule == 0.2


def test_er_config_reads_overrides_from_env() -> None:
    config = er_config(
        {"T_MERGE": "0.9", "T_NEW": "0.4", "W_LLM": "0.6", "W_EMB": "0.3", "W_RULE": "0.1"}
    )
    assert config.t_merge == 0.9
    assert config.t_new == 0.4
    assert config.w_llm == 0.6
    assert config.w_emb == 0.3
    assert config.w_rule == 0.1


def test_er_config_invalid_float_string_raises_invalid_value() -> None:
    with pytest.raises(InvalidValue):
        er_config({"T_MERGE": "not-a-number"})


def test_er_config_empty_string_falls_back_to_default() -> None:
    config = er_config({"T_MERGE": ""})
    assert config.t_merge == 0.8


def test_er_config_uses_os_environ_when_env_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("T_MERGE", "0.85")
    config = er_config()
    assert config.t_merge == 0.85


# ---------------------------------------------------------------------------
# decide() — 경로별 귀속 규약
# ---------------------------------------------------------------------------


def test_decide_normal_path_attributes_to_matched_candidate() -> None:
    config = ERConfig()
    passed = [
        _candidate(1, s_emb=0.9, s_rule=0.8, rule_checked=3, rule_passed=2),
        _candidate(2, s_emb=0.2, s_rule=0.1, rule_checked=3, rule_passed=0),
    ]
    judgement = Judgement(matched_person_id=1, s_llm=0.95, reason="같은 별칭군")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    assert result.matched_person_id == 1
    assert result.confidence_breakdown["matched_person_id"] == 1
    assert result.confidence_breakdown["s_llm"] == 0.95
    assert result.confidence_breakdown["s_emb"] == 0.9
    assert result.confidence_breakdown["s_rule"] == 0.8
    assert result.confidence_breakdown["rule_checked"] == 3
    assert result.confidence_breakdown["rule_passed"] == 2
    assert result.forced_reason is None
    assert result.band == result.band_by_threshold
    expected_confidence = 0.5 * 0.95 + 0.3 * 0.9 + 0.2 * 0.8
    assert math.isclose(result.confidence, expected_confidence, abs_tol=1e-9)
    assert result.band == "merge"
    assert result.action == "merge"
    assert result.decision["matched_person_id"] == 1
    assert result.decision["T_merge"] == config.t_merge
    assert result.decision["T_new"] == config.t_new


def test_decide_null_matched_person_id_with_passed_candidates_is_identity() -> None:
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    judgement = Judgement(matched_person_id=None, s_llm=0.1, reason="확신 없음")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    assert result.matched_person_id is None
    assert result.confidence == 0.0
    assert result.confidence_breakdown["s_llm"] == 0.0
    assert result.confidence_breakdown["s_emb"] == 0.0
    assert result.confidence_breakdown["s_rule"] == 0.0
    assert result.band_by_threshold == "new_person"
    assert result.band == "identity"
    assert result.forced_reason == "no_matched"
    assert result.action == "ask_identity"
    assert result.llm_error_kind is None


def test_decide_llm_failed_with_passed_candidates_is_identity() -> None:
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    result = decide(judgement=None, passed=passed, llm_failed=True, config=config)

    assert result.matched_person_id is None
    assert result.confidence == 0.0
    assert result.confidence_breakdown["s_emb"] == 0.0
    assert result.confidence_breakdown["s_rule"] == 0.0
    assert result.band_by_threshold == "new_person"
    assert result.band == "identity"
    assert result.forced_reason == "llm_failed"
    assert result.action == "ask_identity"
    assert result.llm_error_kind is None


def test_decide_llm_failed_without_passed_candidates_is_new_person() -> None:
    config = ERConfig()
    result = decide(judgement=None, passed=[], llm_failed=True, config=config)
    # 통과 후보가 0 이면 no_candidates 경로가 우선한다 (LLM 은 애초에
    # 호출되지 않으므로 llm_failed=True 는 이 상황에서 나오지 않는 값이지만,
    # decide() 는 방어적으로 no_candidates 를 최우선으로 처리한다).
    assert result.forced_reason == "no_candidates"
    assert result.band == "new_person"


def test_decide_out_of_range_matched_person_id_is_llm_failed_with_error_kind() -> None:
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    judgement = Judgement(matched_person_id=999, s_llm=0.95, reason="존재하지 않는 id")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    assert result.matched_person_id is None
    assert result.forced_reason == "llm_failed"
    assert result.llm_error_kind == OUT_OF_RANGE_ID
    assert result.band == "identity"
    assert result.confidence == 0.0


def test_decide_out_of_range_excluded_candidate_id_is_llm_failed() -> None:
    # 배제된 후보(passed 에 없음)의 id 를 답한 경우도 범위 밖으로 취급한다.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    excluded_id = 42
    judgement = Judgement(matched_person_id=excluded_id, s_llm=0.9, reason="배제된 후보")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    assert result.llm_error_kind == OUT_OF_RANGE_ID
    assert result.forced_reason == "llm_failed"


def test_decide_no_candidates_forces_new_person() -> None:
    config = ERConfig()
    judgement = Judgement(matched_person_id=None, s_llm=0.0, reason="후보 없음")
    result = decide(judgement=judgement, passed=[], llm_failed=False, config=config)

    assert result.confidence == 0.0
    assert result.confidence_breakdown["s_llm"] == 0.0
    assert result.band == "new_person"
    assert result.band_by_threshold == "new_person"
    assert result.forced_reason == "no_candidates"
    assert result.action == "ask_new_person"
    assert result.matched_person_id is None


def test_decide_no_candidates_without_judgement_object() -> None:
    # 통과 후보 0 이면 LLM 을 부르지 않으므로 judgement=None 이 정상 입력이다.
    config = ERConfig()
    result = decide(judgement=None, passed=[], llm_failed=False, config=config)
    assert result.forced_reason == "no_candidates"
    assert result.band == "new_person"


def test_decide_action_mapping_for_all_bands() -> None:
    config = ERConfig()
    # merge
    passed = [_candidate(1, s_emb=1.0, s_rule=1.0)]
    merge_result = decide(
        judgement=Judgement(matched_person_id=1, s_llm=1.0, reason="r"),
        passed=passed,
        llm_failed=False,
        config=config,
    )
    assert merge_result.band == "merge"
    assert merge_result.action == "merge"

    # identity
    passed_mid = [_candidate(1, s_emb=0.5, s_rule=0.5)]
    identity_result = decide(
        judgement=Judgement(matched_person_id=1, s_llm=0.5, reason="r"),
        passed=passed_mid,
        llm_failed=False,
        config=config,
    )
    assert identity_result.band == "identity"
    assert identity_result.action == "ask_identity"

    # new_person
    new_person_result = decide(judgement=None, passed=[], llm_failed=False, config=config)
    assert new_person_result.band == "new_person"
    assert new_person_result.action == "ask_new_person"


def test_decide_without_llm_failed_and_without_judgement_raises() -> None:
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    with pytest.raises(InvalidValue):
        decide(judgement=None, passed=passed, llm_failed=False, config=config)


def test_decide_confidence_recomputable_from_breakdown_within_1e9() -> None:
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.73, s_rule=0.4, rule_checked=3, rule_passed=1)]
    judgement = Judgement(matched_person_id=1, s_llm=0.66, reason="r")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    breakdown = result.confidence_breakdown
    recomputed = (
        breakdown["weights"]["llm"] * breakdown["s_llm"]
        + breakdown["weights"]["emb"] * breakdown["s_emb"]
        + breakdown["weights"]["rule"] * breakdown["s_rule"]
    )
    assert abs(recomputed - breakdown["confidence"]) < 1e-9
    assert abs(recomputed - result.confidence) < 1e-9


def test_decision_to_dict_serializes() -> None:
    config = ERConfig()
    result = decide(judgement=None, passed=[], llm_failed=False, config=config)
    as_dict = result.to_dict()
    assert as_dict["band"] == "new_person"
    assert as_dict["decision"]["forced_reason"] == "no_candidates"
    assert isinstance(result, Decision)


# ---------------------------------------------------------------------------
# D12 -- 관측 신호 재정규화 결합 (P4b U1)
# ---------------------------------------------------------------------------


def test_combine_observed_all_three_matches_d3_formula_exactly() -> None:
    # (i) 세 신호가 모두 관측되면(rule_checked > 0) D3 원식과 abs diff == 0
    # (무작위 표본 >= 100, seed 고정).
    rng = random.Random(20260922)
    config = ERConfig()
    count = 0
    for _ in range(200):
        s_llm = rng.uniform(0.0, 1.0)
        s_emb = rng.uniform(0.0, 1.0)
        s_rule = rng.uniform(0.0, 1.0)
        rule_checked = rng.randint(1, 3)
        confidence = combine(s_llm, s_emb, s_rule, config, rule_checked=rule_checked)
        d3_original = config.w_llm * s_llm + config.w_emb * s_emb + config.w_rule * s_rule
        assert confidence == d3_original, (s_llm, s_emb, s_rule, rule_checked)
        count += 1
    assert count >= 100


def test_combine_rule_checked_omitted_defaults_to_measured() -> None:
    # rule_checked 생략 -> 기본값 1(측정됨)로 D3 원식 그대로(하위호환).
    config = ERConfig()
    confidence_default = combine(s_llm=0.7, s_emb=0.4, s_rule=0.6, config=config)
    confidence_explicit = combine(
        s_llm=0.7, s_emb=0.4, s_rule=0.6, config=config, rule_checked=1
    )
    assert confidence_default == confidence_explicit
    d3_original = config.w_llm * 0.7 + config.w_emb * 0.4 + config.w_rule * 0.6
    assert confidence_default == d3_original


def test_combine_rule_checked_zero_renormalizes_llm_emb_only() -> None:
    # (ii) rule_checked=0 -> 0.625*s_llm + 0.375*s_emb (기본 가중치),
    # s_rule 인자 값은 결과에 반영되지 않는다.
    config = ERConfig()
    s_llm, s_emb = 0.8, 0.6
    confidence = combine(s_llm, s_emb, s_rule=0.9, config=config, rule_checked=0)
    expected = 0.625 * s_llm + 0.375 * s_emb
    assert math.isclose(confidence, expected, abs_tol=1e-9)

    # s_rule 값을 바꿔도(0.0 vs 0.9) rule_checked=0 인 한 결과가 같다.
    confidence_zero_rule = combine(s_llm, s_emb, s_rule=0.0, config=config, rule_checked=0)
    assert confidence == confidence_zero_rule


def test_decide_rule_checked_zero_breakdown_weights_effective() -> None:
    # (ii) decide() 경유 -- confidence_breakdown 의 weights_effective 확인.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.6, s_rule=0.9, rule_checked=0, rule_passed=0)]
    judgement = Judgement(matched_person_id=1, s_llm=0.8, reason="r")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    breakdown = result.confidence_breakdown
    assert breakdown["rule_checked"] == 0
    weights_effective = breakdown["weights_effective"]
    assert math.isclose(weights_effective["llm"], 0.625, abs_tol=1e-9)
    assert math.isclose(weights_effective["emb"], 0.375, abs_tol=1e-9)
    assert weights_effective["rule"] == 0.0
    expected = 0.625 * 0.8 + 0.375 * 0.6
    assert math.isclose(breakdown["confidence"], expected, abs_tol=1e-9)


def test_decide_rule_checked_positive_rule_passed_zero_still_sums_zero_s_rule() -> None:
    # (iii) rule_checked > 0, rule_passed == 0 (검사했는데 전부 충돌) ->
    # 여전히 s_rule=0 으로 "합산"(재정규화하지 않는다), weights_effective
    # == weights.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.6, s_rule=0.0, rule_checked=3, rule_passed=0)]
    judgement = Judgement(matched_person_id=1, s_llm=0.8, reason="r")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    breakdown = result.confidence_breakdown
    assert breakdown["rule_checked"] == 3
    assert breakdown["rule_passed"] == 0
    assert breakdown["s_rule"] == 0.0
    expected = config.w_llm * 0.8 + config.w_emb * 0.6 + config.w_rule * 0.0
    assert math.isclose(breakdown["confidence"], expected, abs_tol=1e-9)
    assert breakdown["weights_effective"] == breakdown["weights"]


def test_breakdown_keys_present_normal_path() -> None:
    # (iv) 정상 경로 -- weights·weights_effective·rule_checked·rule_passed
    # 키가 모두 있다.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8, rule_checked=3, rule_passed=2)]
    judgement = Judgement(matched_person_id=1, s_llm=0.95, reason="r")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    breakdown = result.confidence_breakdown
    for key in ("weights", "weights_effective", "rule_checked", "rule_passed"):
        assert key in breakdown
    assert breakdown["weights_effective"] == breakdown["weights"]


def test_breakdown_keys_present_forced_path_llm_failed() -> None:
    # (iv) 강제 경로(llm_failed) -- 같은 네 키가 있고 weights_effective 는
    # rule_checked=0 이라 재정규화 값이다.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    result = decide(judgement=None, passed=passed, llm_failed=True, config=config)
    breakdown = result.confidence_breakdown
    for key in ("weights", "weights_effective", "rule_checked", "rule_passed"):
        assert key in breakdown
    assert breakdown["rule_checked"] == 0
    weights_effective = breakdown["weights_effective"]
    assert math.isclose(weights_effective["llm"], 0.625, abs_tol=1e-9)
    assert math.isclose(weights_effective["emb"], 0.375, abs_tol=1e-9)
    assert weights_effective["rule"] == 0.0
    assert breakdown["confidence"] == 0.0


def test_breakdown_keys_present_forced_path_no_candidates() -> None:
    # (iv) 강제 경로(no_candidates) -- 같은 규약.
    config = ERConfig()
    result = decide(judgement=None, passed=[], llm_failed=False, config=config)
    breakdown = result.confidence_breakdown
    for key in ("weights", "weights_effective", "rule_checked", "rule_passed"):
        assert key in breakdown
    assert breakdown["rule_checked"] == 0
    weights_effective = breakdown["weights_effective"]
    assert math.isclose(weights_effective["llm"], 0.625, abs_tol=1e-9)
    assert math.isclose(weights_effective["emb"], 0.375, abs_tol=1e-9)
    assert weights_effective["rule"] == 0.0
    assert breakdown["confidence"] == 0.0


def test_breakdown_keys_present_forced_path_out_of_range_id() -> None:
    # (iv) 강제 경로(out_of_range_id) -- 같은 규약.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8)]
    judgement = Judgement(matched_person_id=999, s_llm=0.95, reason="존재하지 않는 id")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    breakdown = result.confidence_breakdown
    for key in ("weights", "weights_effective", "rule_checked", "rule_passed"):
        assert key in breakdown
    assert breakdown["rule_checked"] == 0


def test_original_d3_numeric_expectation_still_holds() -> None:
    # (v) 293행 원식 수치 테스트(test_decide_normal_path_attributes_to_matched_candidate)
    # 가 D12 아래서도 그대로 성립하는지 rule_checked > 0 경로로 재확인한다.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8, rule_checked=3, rule_passed=2)]
    judgement = Judgement(matched_person_id=1, s_llm=0.95, reason="같은 별칭군")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    expected_confidence = 0.5 * 0.95 + 0.3 * 0.9 + 0.2 * 0.8
    assert math.isclose(result.confidence, expected_confidence, abs_tol=1e-9)
    assert result.band == "merge"


def test_weights_effective_sums_to_one_when_unmeasured() -> None:
    # (vi) weights_effective 의 합이 1.0 (관측 신호만) -- U4 recheck 테스트와 짝.
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.5, s_rule=0.5, rule_checked=0, rule_passed=0)]
    result = decide(
        judgement=None, passed=passed, llm_failed=True, config=config
    )
    weights_effective = result.confidence_breakdown["weights_effective"]
    assert math.isclose(sum(weights_effective.values()), 1.0, abs_tol=1e-9)


def test_weights_effective_sums_to_one_when_measured() -> None:
    # (vi) 관측된 경우도 합이 1.0 (기존 가중치 그대로이므로 자명하나 회귀 방지).
    config = ERConfig()
    passed = [_candidate(1, s_emb=0.9, s_rule=0.8, rule_checked=3, rule_passed=2)]
    judgement = Judgement(matched_person_id=1, s_llm=0.95, reason="r")
    result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    weights_effective = result.confidence_breakdown["weights_effective"]
    assert math.isclose(sum(weights_effective.values()), 1.0, abs_tol=1e-9)


def test_effective_weights_helper_matches_combine_branch_condition() -> None:
    # combine() 과 _effective_weights() 가 같은 조건(rule_checked > 0)으로
    # 갈리는지 직접 import 해 교차 확인한다(이중 출처 금지, 원칙9).
    from app.er.confidence import _effective_weights

    config = ERConfig()
    unmeasured = _effective_weights(0, config)
    assert math.isclose(unmeasured["llm"], 0.625, abs_tol=1e-9)
    assert math.isclose(unmeasured["emb"], 0.375, abs_tol=1e-9)
    assert unmeasured["rule"] == 0.0
    assert _effective_weights(1, config) == {"llm": 0.5, "emb": 0.3, "rule": 0.2}
    assert _effective_weights(5, config) == {"llm": 0.5, "emb": 0.3, "rule": 0.2}
