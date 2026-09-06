"""Refs: P3-er U3 결정8 -- `app/er/types.py` 단위 테스트. DB·LLM 없음."""

from __future__ import annotations

import pytest

from app.er.types import (
    ER_TRACE_STEP,
    ER_TRACE_TOOL_NAME,
    ER_VERSION,
    ERConfig,
    Judgement,
    JudgeUnavailable,
    Resolution,
    ScoredCandidate,
)
from app.tools.types import InvalidValue


def test_default_config_is_valid() -> None:
    config = ERConfig()
    assert config.t_merge == 0.8
    assert config.t_new == 0.3
    assert config.w_llm == 0.5
    assert config.w_emb == 0.3
    assert config.w_rule == 0.2


def test_weights_must_sum_to_one() -> None:
    with pytest.raises(InvalidValue):
        ERConfig(w_llm=0.6, w_emb=0.3, w_rule=0.2)


def test_weights_within_floating_point_tolerance_are_accepted() -> None:
    # 0.1 + 0.2 + 0.7 처럼 부동소수 오차가 나는 조합도 1e-9 오차 안이면 통과.
    ERConfig(w_llm=0.1, w_emb=0.2, w_rule=0.7)


@pytest.mark.parametrize(
    ("t_new", "t_merge"),
    [
        (0.9, 0.5),  # t_new > t_merge
        (-0.1, 0.8),  # 범위 밖
        (0.3, 1.5),
    ],
)
def test_invalid_threshold_ordering_rejected(t_new: float, t_merge: float) -> None:
    with pytest.raises(InvalidValue):
        ERConfig(t_new=t_new, t_merge=t_merge)


def test_thresholds_may_be_equal() -> None:
    # 0 <= t_new <= t_merge <= 1 이므로 경계에서 같은 값은 허용.
    ERConfig(t_new=0.5, t_merge=0.5)


def test_trace_constants_are_reserved_values() -> None:
    assert ER_TRACE_STEP == "er_resolve"
    assert ER_TRACE_TOOL_NAME == "er"
    assert isinstance(ER_VERSION, str)


def test_scored_candidate_defaults_are_unevaluated() -> None:
    candidate = ScoredCandidate(person_id=1, display_name="팀장", aliases=["팀장"])
    assert candidate.rule_checked == 0
    assert candidate.rule_passed == 0
    assert candidate.s_rule == 0.0
    assert candidate.passed_rules is False
    assert candidate.excluded_by is None
    assert candidate.relaxed_pass is False
    assert candidate.to_dict()["person_id"] == 1


def test_judgement_self_reported_score_round_trips() -> None:
    judgement = Judgement(matched_person_id=1, s_llm=0.9, reason="같은 별칭군")
    as_dict = judgement.to_dict()
    assert as_dict["matched_person_id"] == 1
    assert as_dict["s_llm"] == 0.9


def test_judge_unavailable_is_a_plain_exception() -> None:
    with pytest.raises(JudgeUnavailable):
        raise JudgeUnavailable("timeout")


def test_resolution_to_dict_serializes_candidates() -> None:
    candidate = ScoredCandidate(person_id=1, display_name="팀장", aliases=["팀장"])
    resolution = Resolution(trace_id=42, mention="부장님", candidates=[candidate])
    as_dict = resolution.to_dict()
    assert as_dict["trace_id"] == 42
    assert as_dict["candidates"][0]["person_id"] == 1
    assert as_dict["band"] == "new_person"
