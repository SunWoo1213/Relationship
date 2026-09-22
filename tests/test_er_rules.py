"""Refs: P3-er P4b-er-redesign U2 S3.3 결정2 D10 D13 원칙1 원칙9 -- 규칙
필터(`app/er/rules.py`) 단위 테스트. DB·LLM 없음(순수 함수).

D13(규칙 필터 감점, CR-001 2026-09-22) 이후: `relation_tag_conflict`·
`hierarchy_conflict` 는 후보를 목록에서 빼지 않는다(감점, `penalized_by`).
`excluded_by` 에는 `dictionary_conflict` 만 등장한다. `passed_rules` 는
"배제되지 않았다"(=`dictionary_conflict` 없음)를 뜻한다."""

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
# (a) 관계 태그 그룹 불일치 + 호칭 사전 모순 -- "팀장" 후보 vs mention "이모"
#     ("팀장" 이 사전 표제어라 dictionary_conflict 도 함께 뜨므로 D13
#     이후에도 배제가 유지된다 -- 01-plan U3 픽스처 (b) "팀장↔이모" 와 같은
#     조합, `tests/test_er_pipeline.py` 의 aunt 회귀와 짝이다)
# ---------------------------------------------------------------------------


def test_relation_tag_conflict_excludes_and_no_relaxation() -> None:
    candidate = _candidate(1, "팀장", ["팀장"], relation_tag="직장", hierarchy="동")
    hints = dictionary.derive_hints("이모")  # {"relation_tag": "가족", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert passed == []
    assert relaxed_retry is False  # 위계 '만' 으로 탈락한 것이 아니므로 완화 시도 안 함.
    scored = all_scored[0]
    assert scored.passed_rules is False
    # D13: 사전 모순(dictionary_conflict)이 함께 있으므로 배제는 유지된다
    # -- 대표 사유 우선순위가 아니라 dictionary_conflict 단일 사유다.
    assert scored.excluded_by == "dictionary_conflict"
    # 관계 태그·위계 충돌은 배제 사유에서는 빠졌지만 감점 표시로는 남는다
    # (D13 "코드에서 지켜야 할 것" -- 배제된 후보도 근거를 잃지 않는다).
    assert scored.penalized_by == ("relation_tag_conflict", "hierarchy_conflict")


# ---------------------------------------------------------------------------
# (a2) 관계 태그 불일치만(사전 모순 없음) -- D13 의 핵심 변화: 더 이상
#      배제되지 않고 감점된 채 3단계로 전달된다.
# ---------------------------------------------------------------------------


def test_relation_tag_conflict_alone_is_penalized_not_excluded() -> None:
    # 별칭 "민수" 는 호칭 사전 표제어가 아니므로 dictionary_conflict 가
    # 뜨지 않는다 -- 순수하게 relation_tag_conflict 만 남는 케이스.
    candidate = _candidate(7, "민수", ["민수"], relation_tag="친구", hierarchy="상")
    hints = {"relation_tag": "가족", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert relaxed_retry is False  # 관계 태그 충돌은 완화 적격이 아니다.
    assert len(passed) == 1
    scored = passed[0]
    assert scored is all_scored[0]
    assert scored.passed_rules is True
    assert scored.excluded_by is None
    assert scored.penalized_by == ("relation_tag_conflict",)
    assert scored.rule_checked == 2  # 관계 태그 + 위계(사전 검사는 정보 없음으로 스킵)
    assert scored.rule_passed == 1  # 위계만 일치
    assert math.isclose(scored.s_rule, 1 / 2, abs_tol=1e-9)


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
    # D13 + R-4(03-log): 완화 통과(relaxed_pass=True) 후보도 penalized_by
    # 는 엄격 평가의 위계 충돌을 그대로 담는다 -- 자동 연결 허용 여부의
    # 예외 판별은 relaxed_pass 플래그로 별도로 한다(정보 손실 없음).
    assert scored.penalized_by == ("hierarchy_conflict",)

    # 엄격 단계 결과도 함께 확인 -- 위계 불일치만으로 감점됐었다는 근거.
    strict_only = rules.apply_rules([candidate], hints, relaxed=False)[0]
    assert strict_only.passed_rules is True
    assert strict_only.excluded_by is None
    assert strict_only.penalized_by == ("hierarchy_conflict",)
    assert strict_only.relaxed_pass is False


# ---------------------------------------------------------------------------
# (c) 2칸 차이(하 vs 상) -- 완화해도 탈락(감점은 유지, 배제는 아님)
# ---------------------------------------------------------------------------


def test_two_step_hierarchy_gap_never_relaxes() -> None:
    candidate = _candidate(3, "사원", ["사원"], relation_tag="직장", hierarchy="하")
    hints = {"relation_tag": "직장", "hierarchy": "상"}

    passed, all_scored, relaxed_retry = rules.run_rule_stage([candidate], hints)

    assert relaxed_retry is False  # 인접이 아니므로 완화 자체를 시도하지 않는다.
    assert len(passed) == 1  # D13: 배제가 아니라 감점이므로 3단계로 전달된다.
    scored = all_scored[0]
    assert scored.passed_rules is True
    assert scored.excluded_by is None
    assert scored.penalized_by == ("hierarchy_conflict",)

    # 완화를 직접 적용해도(가정) 여전히 감점(2칸 차이는 인접이 아니다).
    relaxed_only = rules.apply_rules([candidate], hints, relaxed=True)[0]
    assert relaxed_only.passed_rules is True
    assert relaxed_only.excluded_by is None
    assert relaxed_only.relaxed_pass is False
    assert relaxed_only.penalized_by == ("hierarchy_conflict",)


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
    assert scored.penalized_by == ()

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
        assert candidate.penalized_by == ()


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

    # 부적격(관계 태그 불일치 + 사전 모순) 케이스 -- strict 1회만, relaxed
    # 재시도 없음(전체 배제라 완화 적격 판정에서 탈락).
    mismatched_candidate = _candidate(1, "팀장", ["팀장"], relation_tag="직장", hierarchy="동")
    rules.run_rule_stage([mismatched_candidate], dictionary.derive_hints("이모"))
    assert relaxed_flags == [False]


# ---------------------------------------------------------------------------
# (g) D13 "코드에서 지켜야 할 것" 2항 -- 3단계 전달 후보 수 == 1단계 후보
#     수 - dictionary_conflict 후보 수
# ---------------------------------------------------------------------------


def test_candidate_count_forwarded_equals_total_minus_dictionary_excluded() -> None:
    hints = dictionary.derive_hints("이모")  # {"relation_tag": "가족", "hierarchy": "상"}
    dict_excluded = _candidate(30, "팀장", ["팀장"], relation_tag="직장", hierarchy="동")
    penalized_only = _candidate(31, "민수", ["민수"], relation_tag="친구", hierarchy="동")

    passed, all_scored, _relaxed_retry = rules.run_rule_stage(
        [dict_excluded, penalized_only], hints
    )

    assert len(all_scored) == 2
    dictionary_excluded_count = sum(
        1 for c in all_scored if c.excluded_by == "dictionary_conflict"
    )
    assert dictionary_excluded_count == 1
    assert len(passed) == len(all_scored) - dictionary_excluded_count
    assert {c.person_id for c in passed} == {31}
    forwarded = passed[0]
    assert forwarded.penalized_by == ("relation_tag_conflict", "hierarchy_conflict")


# ---------------------------------------------------------------------------
# (h) D13 "코드에서 지켜야 할 것" 1항 -- excluded_by 값 집합에는
#     dictionary_conflict 만 등장한다. penalized_by 어휘는 _CONFLICT_PRIORITY
#     순서로 정렬된다.
# ---------------------------------------------------------------------------


def test_excluded_by_domain_is_dictionary_conflict_only() -> None:
    hints = {"relation_tag": "가족", "hierarchy": "상"}
    # 세 별칭 모두 호칭 사전에 없는 고유명사라 dictionary_conflict 자체가
    # 평가되지 않는다(정보 없음, 분모 제외) -- 순수하게 관계 태그·위계
    # 충돌만 남는다.
    relation_only = _candidate(50, "관계만", ["철수"], relation_tag="친구", hierarchy="상")
    hierarchy_only = _candidate(51, "위계만", ["영희"], relation_tag="가족", hierarchy="하")
    both = _candidate(52, "둘다", ["민지"], relation_tag="친구", hierarchy="하")

    scored = rules.apply_rules([relation_only, hierarchy_only, both], hints, relaxed=False)

    excluded_values = {c.excluded_by for c in scored if c.excluded_by is not None}
    assert excluded_values <= {"dictionary_conflict"}
    assert "relation_tag_conflict" not in excluded_values
    assert "hierarchy_conflict" not in excluded_values

    for c in scored:
        assert c.passed_rules is True
        assert c.excluded_by is None

    # penalized_by 어휘가 _CONFLICT_PRIORITY 순서(relation_tag 먼저,
    # hierarchy 다음)로 정렬된다.
    by_id = {c.person_id: c for c in scored}
    assert by_id[50].penalized_by == ("relation_tag_conflict",)
    assert by_id[51].penalized_by == ("hierarchy_conflict",)
    assert by_id[52].penalized_by == ("relation_tag_conflict", "hierarchy_conflict")


# ---------------------------------------------------------------------------
# (i) 완화 트리거(결정 C(i)) -- 감점 없는 후보가 하나라도 있으면 완화 안
#     돌고, 전부 감점이면 1회 돈다.
# ---------------------------------------------------------------------------


def test_relaxation_not_triggered_when_any_candidate_unpenalized() -> None:
    hints = dictionary.derive_hints("부장님")  # {"relation_tag": "직장", "hierarchy": "상"}
    exact = _candidate(10, "김부장", ["부장"], relation_tag="직장", hierarchy="상")
    promoted = _candidate(
        11, "김민수", ["팀장", "김팀장"], relation_tag="직장", hierarchy="동"
    )

    passed, _all_scored, relaxed_retry = rules.run_rule_stage([exact, promoted], hints)

    assert relaxed_retry is False
    assert {c.person_id for c in passed} == {10, 11}
    exact_scored = next(c for c in passed if c.person_id == 10)
    promoted_scored = next(c for c in passed if c.person_id == 11)
    assert exact_scored.penalized_by == ()
    assert promoted_scored.penalized_by == ("hierarchy_conflict",)
    # 완화 재평가를 시도하지 않았으므로 promoted 는 relaxed_pass=False 그대로.
    assert promoted_scored.relaxed_pass is False


def test_relaxation_triggered_when_all_candidates_penalized() -> None:
    hints = dictionary.derive_hints("부장님")  # {"relation_tag": "직장", "hierarchy": "상"}
    a = _candidate(20, "김민수", ["팀장", "김팀장"], relation_tag="직장", hierarchy="동")
    b = _candidate(21, "박서준", ["팀장"], relation_tag="직장", hierarchy="동")

    passed, _all_scored, relaxed_retry = rules.run_rule_stage([a, b], hints)

    assert relaxed_retry is True
    assert {c.person_id for c in passed} == {20, 21}
    for c in passed:
        assert c.relaxed_pass is True
        assert c.penalized_by == ("hierarchy_conflict",)
