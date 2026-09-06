"""Refs: P3-er U3 S3.3 결정2 D10 원칙1 -- 규칙 필터(`app/er/rules.py`) 단위
테스트. DB·LLM 없음(순수 함수)."""

from __future__ import annotations

import math

from app.er import dictionary, rules
from app.er.types import ScoredCandidate


def _candidate(
    person_id: int,
    display_name: str,
    aliases: list[str],
    relation_tag: str | None,
    hierarchy: str | None,
) -> ScoredCandidate:
    return ScoredCandidate(
        person_id=person_id,
        display_name=display_name,
        aliases=aliases,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )


# ---------------------------------------------------------------------------
# (a) 관계 태그 그룹 불일치 -- "팀장" 후보 vs mention "이모"
# ---------------------------------------------------------------------------


def test_relation_tag_conflict_excludes_and_no_relaxation() -> None:
    candidate = _candidate(1, "팀장", ["팀장"], relation_tag="직장", hierarchy="동")
    hints = dictionary.derive_hints("이모")  # {"relation_tag": "가족", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert passed == []
    assert relaxed_retry is False  # 위계 '만' 으로 탈락한 것이 아니므로 완화 시도 안 함.
    scored = all_scored[0]
    assert scored.passed_rules is False
    assert scored.excluded_by == "relation_tag_conflict"


# ---------------------------------------------------------------------------
# (b) 승진 픽스처 -- 저장 위계 동, 유도 위계 상(부장님)
# ---------------------------------------------------------------------------


def test_promotion_fixture_relaxes_and_merges_with_conservative_scoring() -> None:
    candidate = _candidate(
        2, "김민수", ["팀장", "김팀장"], relation_tag="직장", hierarchy="동"
    )
    hints = dictionary.derive_hints("부장님")  # {"relation_tag": "직장", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert relaxed_retry is True
    assert len(passed) == 1
    scored = passed[0]
    assert scored.relaxed_pass is True
    assert scored.rule_checked == 3
    assert scored.rule_passed == 2  # 완화 통과는 rule_passed 에 미계상(결정2).
    assert math.isclose(scored.s_rule, 2 / 3, abs_tol=1e-9)
    assert scored.passed_rules is True
    assert scored.excluded_by is None

    # 엄격 단계 결과도 함께 확인 -- 위계 불일치만으로 탈락했었다는 근거.
    strict_only = rules.apply_rules([candidate], hints, relaxed=False)[0]
    assert strict_only.passed_rules is False
    assert strict_only.excluded_by == "hierarchy_conflict"


# ---------------------------------------------------------------------------
# (c) 2칸 차이(하 vs 상) -- 완화해도 탈락
# ---------------------------------------------------------------------------


def test_two_step_hierarchy_gap_never_relaxes() -> None:
    candidate = _candidate(3, "사원", ["사원"], relation_tag="직장", hierarchy="하")
    hints = {"relation_tag": "직장", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert passed == []
    assert relaxed_retry is False  # 인접이 아니므로 완화 자체를 시도하지 않는다.
    scored = all_scored[0]
    assert scored.excluded_by == "hierarchy_conflict"

    # 완화를 직접 적용해도(가정) 여전히 탈락함을 별도로 확인.
    relaxed_only = rules.apply_rules([candidate], hints, relaxed=True)[0]
    assert relaxed_only.passed_rules is False
    assert relaxed_only.relaxed_pass is False


# ---------------------------------------------------------------------------
# (d) 정보 없음 -- hints 빈 dict
# ---------------------------------------------------------------------------


def test_no_hints_means_zero_checked_and_no_exclusion() -> None:
    candidate = _candidate(4, "민수", ["민수"], relation_tag="친구", hierarchy="동")

    scored = rules.apply_rules([candidate], {})[0]

    assert scored.rule_checked == 0
    assert scored.rule_passed == 0
    assert scored.s_rule == 0.0
    assert scored.passed_rules is True
    assert scored.excluded_by is None

    passed, _all_scored, relaxed_retry = rules.run_rule_stage([candidate], {})
    assert passed == [scored]
    assert relaxed_retry is False


# ---------------------------------------------------------------------------
# (e) 동명이인 2명 모두 통과
# ---------------------------------------------------------------------------


def test_two_candidates_with_same_alias_both_pass() -> None:
    candidate_a = _candidate(5, "팀장A", ["팀장"], relation_tag="직장", hierarchy="동")
    candidate_b = _candidate(6, "팀장B", ["팀장"], relation_tag="직장", hierarchy="동")
    hints = dictionary.derive_hints("팀장")  # {"relation_tag": "직장", "hierarchy": "동"}

    passed, _all_scored, relaxed_retry = rules.run_rule_stage(
        [candidate_a, candidate_b], hints
    )

    assert relaxed_retry is False
    assert {c.person_id for c in passed} == {5, 6}
    for candidate in passed:
        assert candidate.rule_checked == 3
        assert candidate.rule_passed == 3
        assert candidate.s_rule == 1.0


# ---------------------------------------------------------------------------
# (f) 완화는 1회만 (재귀·반복 없음)
# ---------------------------------------------------------------------------


def test_relaxation_attempts_at_most_once(monkeypatch) -> None:
    original_apply_rules = rules.apply_rules
    relaxed_flags: list[bool] = []

    def spy(candidates, hints, *, relaxed: bool = False):
        relaxed_flags.append(relaxed)
        return original_apply_rules(candidates, hints, relaxed=relaxed)

    monkeypatch.setattr(rules, "apply_rules", spy)

    # 적격(승진) 케이스 -- strict 1회 + relaxed 1회 = 총 2회, 그 이상은 없다.
    promotion_candidate = _candidate(
        2, "김민수", ["팀장", "김팀장"], relation_tag="직장", hierarchy="동"
    )
    rules.run_rule_stage([promotion_candidate], dictionary.derive_hints("부장님"))
    assert relaxed_flags == [False, True]

    relaxed_flags.clear()

    # 부적격(관계 태그 불일치) 케이스 -- strict 1회만, relaxed 재시도 없음.
    mismatched_candidate = _candidate(1, "팀장", ["팀장"], relation_tag="직장", hierarchy="동")
    rules.run_rule_stage([mismatched_candidate], dictionary.derive_hints("이모"))
    assert relaxed_flags == [False]
