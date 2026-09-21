"""Refs: P4-pilot-eval S3.7 D10 원칙1 원칙2 원칙8 -- 지표 계산기(U2) 계약 테스트.

**네트워크·DB·LLM 없음**(순수). 입력은 손으로 만든 소형 JSONL 행이고, 기대값은
전부 손으로 센 정수다 -- 계산기가 무엇을 세는지 사람이 검산할 수 있어야
"재현 가능한 수치"(원칙8)가 성립한다.

전수 단언하는 것:
- 분모 규칙 1 `ambiguous` 제외 / 2 `passing_mentions` 오탐 분자 / 3 `ask_user`
  제3 범주(01-plan 65행)
- 채점표 6칸(골드가 DB 안/밖 × `merge` 정오·`identity`·`new_person`)
- `expected_ask_user.allowed` **허용 집합** 채점(단일 정답 아님)
- 부정: 필수 키 누락 · 어휘 밖 `decision` · 분모 0(0 으로 나누지 않는다) ·
  `T_merge` 격자 10행 사본의 중복 집계 방지(토큰·LLM 호출·오류 건수)
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pytest

from evaluation.metrics import (
    ALLOWED_ASK_LABELS,
    ASK_KINDS,
    DECISIONS,
    DENOMINATOR_RULE,
    GZIP_SUFFIX,
    OUTCOMES,
    REQUIRED_ROW_KEYS,
    MetricsError,
    classify_gold_row,
    compute_metrics,
    format_t_merge,
    group_rates,
    iter_jsonl,
    load_rows,
    main,
    mention_level_rows,
    open_jsonl,
    ratio,
    validate_rows,
)

# ---------------------------------------------------------------------------
# 행 공장 -- 기본값은 "골드(DB 안 인물)를 맞게 병합한 제안 방식 행 하나"
# ---------------------------------------------------------------------------


def make_row(**over: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "method": "proposed",
        "mention": "김팀장",
        "decision": "merge",
        "person_id": 1,
        "score": 0.9,
        "candidates": [],
        "trace_id": None,
        "tokens_in": 0,
        "tokens_out": 0,
        "detail": {},
        "scenario_id": "sc-001",
        "category": "promotion",
        "mention_kind": "gold",
        "mention_index": 0,
        "turn": 0,
        "gold_person_id": "p1",
        "gold_db_person_id": 1,
        "ambiguous": False,
        "expected_ask_user_allowed": ["none"],
        "trap_kind": None,
        "t_merge": 0.8,
        "t_new": 0.3,
        "sweep_index": 0,
        "llm_fresh_call": False,
    }
    if "decision" in over and "person_id" not in over:
        over = {**over, "person_id": 1 if over["decision"] == "merge" else None}
    row.update(over)
    return row


def point(rows: list[dict[str, Any]], method: str = "proposed", t: str = "0.8") -> Any:
    return compute_metrics(rows)["methods"][method]["by_t_merge"][t]


# ---------------------------------------------------------------------------
# 0. 계약 상수
# ---------------------------------------------------------------------------


def test_required_row_keys_match_runner_contract() -> None:
    """필수 키는 `MentionDecision.to_dict()` + 러너가 더하는 14키다 --
    두 출처가 갈라지면 여기서 깨진다."""

    from evaluation.resolvers.base import MentionDecision
    from evaluation.runner import ROW_EXTRA_KEYS

    produced = MentionDecision(
        method="proposed",
        mention="김팀장",
        decision="identity",
        person_id=None,
        score=0.5,
        candidates=[],
    ).to_dict()
    assert set(REQUIRED_ROW_KEYS) == set(produced) | set(ROW_EXTRA_KEYS)
    assert set(make_row()) == set(REQUIRED_ROW_KEYS)


def test_decision_vocabulary_matches_base() -> None:
    from evaluation.resolvers.base import DECISIONS as BASE_DECISIONS

    assert DECISIONS == BASE_DECISIONS
    assert set(ASK_KINDS) == {"identity", "new_person", "schedule"}
    assert ALLOWED_ASK_LABELS == {"identity", "new_person", "none"}


def test_denominator_rule_is_reported_with_the_numbers() -> None:
    """수용 기준 해석 2 -- 분모 규칙이 수치와 같은 파일에 있어야 한다."""

    meta = compute_metrics([make_row()])["meta"]
    assert meta["denominator_rule"] == DENOMINATOR_RULE
    assert set(DENOMINATOR_RULE) >= {
        "scored_base",
        "ambiguous",
        "passing_mentions",
        "third_category",
        "ask_user",
        "llm_error",
        "sweep_copies",
        "score_axis",
    }


# ---------------------------------------------------------------------------
# 1. ratio -- 분모 0 은 0 으로 나누지 않고 rate=None
# ---------------------------------------------------------------------------


def test_ratio_carries_numerator_and_denominator() -> None:
    assert ratio(2, 57) == {"n": 2, "d": 57, "rate": 2 / 57}


def test_ratio_zero_denominator_is_none_not_zero() -> None:
    block = ratio(0, 0)
    # "측정할 수 없었다"(None)와 "측정했더니 0"(0.0)은 다른 값이다.
    assert block == {"n": 0, "d": 0, "rate": None}
    assert block["rate"] is None
    assert ratio(0, 5)["rate"] == 0.0


@pytest.mark.parametrize("args", [(-1, 3), (1, -3), (4, 3)])
def test_ratio_rejects_impossible_counts(args: tuple[int, int]) -> None:
    with pytest.raises(MetricsError):
        ratio(*args)


def test_format_t_merge_folds_float_noise() -> None:
    assert format_t_merge(0.8000000000000002) == "0.8"
    assert format_t_merge(0.55) == "0.55"
    with pytest.raises(MetricsError):
        format_t_merge(0.813)
    with pytest.raises(MetricsError):
        format_t_merge("x")


# ---------------------------------------------------------------------------
# 2. 채점표 6칸 (전수)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("gold_db", "decision", "person_id", "expected"),
    [
        (1, "merge", 1, "merge_correct"),
        (1, "merge", 2, "false_merge"),
        (1, "identity", None, "deferred"),
        (1, "new_person", None, "miss"),
        (None, "merge", 2, "false_merge"),
        (None, "identity", None, "deferred"),
        (None, "new_person", None, "new_person_correct"),
    ],
)
def test_classify_gold_row_table(
    gold_db: int | None, decision: str, person_id: int | None, expected: str
) -> None:
    row = make_row(gold_db_person_id=gold_db, decision=decision, person_id=person_id)
    assert classify_gold_row(row) == expected
    assert expected in OUTCOMES


def test_classify_rejects_excluded_rows() -> None:
    with pytest.raises(MetricsError):
        classify_gold_row(
            make_row(
                mention_kind="passing", gold_person_id=None, gold_db_person_id=None
            )
        )
    with pytest.raises(MetricsError):
        classify_gold_row(
            make_row(ambiguous=True, gold_person_id=None, gold_db_person_id=None)
        )


# ---------------------------------------------------------------------------
# 3. 분모 규칙 1 -- ambiguous 제외
# ---------------------------------------------------------------------------


def _ambiguous_row(**over: Any) -> dict[str, Any]:
    return make_row(
        ambiguous=True,
        gold_person_id=None,
        gold_db_person_id=None,
        expected_ask_user_allowed=["identity", "none"],
        **over,
    )


def test_ambiguous_mentions_leave_every_denominator() -> None:
    rows = [
        make_row(mention_index=0),  # merge_correct
        make_row(mention_index=1, decision="merge", person_id=2),  # false_merge
        _ambiguous_row(mention_index=2, decision="merge", person_id=9),
        _ambiguous_row(mention_index=3, decision="identity"),
    ]
    p = point(rows)
    assert p["scored"] == 2
    assert p["false_merge_rate"] == {"n": 1, "d": 2, "rate": 0.5}
    assert p["miss_rate"] == {"n": 0, "d": 2, "rate": 0.0}
    assert p["ask_user_rate_by_kind"]["identity"] == {"n": 0, "d": 2, "rate": 0.0}
    assert p["excluded"]["ambiguous_rows"] == 2
    assert sum(p["outcomes"].values()) == 2

    meta = compute_metrics(rows)["meta"]
    assert meta["mention_counts"] == {
        "gold": 4,
        "gold_scored": 2,
        "ambiguous": 2,
        "passing": 0,
    }
    assert meta["excluded"]["ambiguous_rows"] == 2


# ---------------------------------------------------------------------------
# 4. 분모 규칙 2 -- passing_mentions 는 오탐 분자
# ---------------------------------------------------------------------------


def _passing_row(**over: Any) -> dict[str, Any]:
    return make_row(
        scenario_id="sc-038",
        category="new_person",
        mention_kind="passing",
        gold_person_id=None,
        gold_db_person_id=None,
        expected_ask_user_allowed=["none"],
        **over,
    )


def test_passing_mentions_are_a_false_positive_numerator_not_a_gold_denominator() -> None:
    rows = [
        make_row(mention_index=0),  # 골드 1건
        _passing_row(mention_index=0, decision="new_person"),  # 오탐
        _passing_row(mention_index=1, decision="identity"),  # 오탐 아님
        _passing_row(mention_index=2, decision="merge", person_id=3),  # 라벨 밖
    ]
    p = point(rows)
    assert p["scored"] == 1  # passing 3건은 골드 분모에 없다
    assert p["passing"]["false_positive"] == {"n": 1, "d": 3, "rate": 1 / 3}
    assert p["passing"]["by_decision"] == {"merge": 1, "identity": 1, "new_person": 1}
    # allowed=["none"] 이므로 merge 한 건만 허용, 나머지 둘은 위반
    assert p["passing"]["expected_ask_user_allowed"] == {"n": 1, "d": 3, "rate": 1 / 3}
    assert p["excluded"]["passing_rows"] == 3
    # 골드 지표는 passing 결정에 흔들리지 않는다
    assert p["false_merge_rate"] == {"n": 0, "d": 1, "rate": 0.0}


def test_passing_false_positive_denominator_zero_is_none() -> None:
    p = point([make_row()])
    assert p["passing"]["false_positive"] == {"n": 0, "d": 0, "rate": None}
    assert p["passing"]["expected_ask_user_allowed"]["rate"] is None


# ---------------------------------------------------------------------------
# 5. 분모 규칙 3 -- ask_user 제3 범주
# ---------------------------------------------------------------------------


def test_third_category_is_separate_from_false_merge_and_miss() -> None:
    rows = [
        make_row(mention_index=0),  # merge_correct
        make_row(mention_index=1, decision="merge", person_id=2),  # false_merge
        make_row(mention_index=2, decision="identity"),  # 제3 범주
        make_row(mention_index=3, decision="new_person"),  # miss(골드는 DB 안 인물)
        make_row(  # 골드가 DB 밖 인물 -> new_person 이 정답
            mention_index=4, decision="new_person", gold_person_id="p9", gold_db_person_id=None
        ),
    ]
    p = point(rows)
    assert p["scored"] == 5
    assert p["outcomes"] == {
        "merge_correct": 1,
        "false_merge": 1,
        "miss": 1,
        "deferred": 1,
        "new_person_correct": 1,
    }
    assert p["false_merge_rate"] == {"n": 1, "d": 5, "rate": 0.2}
    assert p["miss_rate"] == {"n": 1, "d": 5, "rate": 0.2}
    assert p["deferred_identity_rate"] == {"n": 1, "d": 5, "rate": 0.2}
    # 마찰 축은 배타적이지 않다 -- identity 1 + new_person 2
    assert p["ask_user_rate_by_kind"]["identity"] == {"n": 1, "d": 5, "rate": 0.2}
    assert p["ask_user_rate_by_kind"]["new_person"] == {"n": 2, "d": 5, "rate": 0.4}
    assert p["ask_user_rate_by_kind"]["schedule"] == {"n": 0, "d": 5, "rate": 0.0}


def test_identity_rows_never_enter_false_merge_or_miss_numerators() -> None:
    rows = [make_row(mention_index=i, decision="identity") for i in range(4)]
    p = point(rows)
    assert p["false_merge_rate"]["n"] == 0
    assert p["miss_rate"]["n"] == 0
    assert p["deferred_identity_rate"] == {"n": 4, "d": 4, "rate": 1.0}


def test_precision_recall_f1_are_hand_checkable() -> None:
    rows = [
        make_row(mention_index=0),  # merge 맞음
        make_row(mention_index=1),  # merge 맞음
        make_row(mention_index=2, decision="merge", person_id=2),  # merge 틀림
        make_row(mention_index=3, decision="identity"),  # 미룸(recall 손해)
        make_row(  # 골드가 DB 밖 -> merge 는 오병합, recall 분모 밖
            mention_index=4, decision="merge", person_id=2, gold_person_id="p9",
            gold_db_person_id=None,
        ),
    ]
    p = point(rows)
    assert p["precision"] == {"n": 2, "d": 4, "rate": 0.5}  # merge 4건 중 2건 정답
    assert p["recall"] == {"n": 2, "d": 4, "rate": 0.5}  # DB 안 골드 4건 중 2건
    assert p["f1"] == pytest.approx(0.5)


def test_f1_is_none_when_a_denominator_is_zero() -> None:
    p = point([make_row(decision="identity")])
    assert p["precision"] == {"n": 0, "d": 0, "rate": None}
    assert p["f1"] is None


# ---------------------------------------------------------------------------
# 6. 허용 집합 채점 (단일 정답 아님)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("allowed", "decision", "hit"),
    [
        (["none"], "merge", True),
        (["none"], "identity", False),
        (["none"], "new_person", False),
        (["identity", "none"], "merge", True),
        (["identity", "none"], "identity", True),
        (["identity", "none"], "new_person", False),
        (["identity", "new_person"], "merge", False),
        (["identity", "new_person"], "identity", True),
        (["identity", "new_person"], "new_person", True),
        (["new_person"], "new_person", True),
        (["new_person"], "identity", False),
    ],
)
def test_expected_ask_user_allowed_is_a_set_not_a_single_answer(
    allowed: list[str], decision: str, hit: bool
) -> None:
    rows = [make_row(decision=decision, expected_ask_user_allowed=allowed)]
    assert point(rows)["expected_ask_user_allowed"] == {
        "n": 1 if hit else 0,
        "d": 1,
        "rate": 1.0 if hit else 0.0,
    }


def test_allowed_set_scoring_aggregates_over_rows() -> None:
    rows = [
        make_row(mention_index=0, expected_ask_user_allowed=["identity", "none"]),
        make_row(
            mention_index=1, decision="identity", expected_ask_user_allowed=["identity", "none"]
        ),
        make_row(
            mention_index=2,
            decision="new_person",
            expected_ask_user_allowed=["identity", "none"],
        ),
    ]
    assert point(rows)["expected_ask_user_allowed"] == {"n": 2, "d": 3, "rate": 2 / 3}


# ---------------------------------------------------------------------------
# 7. 10행 사본(T_merge 격자) 중복 집계 방지
# ---------------------------------------------------------------------------


def _sweep_rows(**over: Any) -> list[dict[str, Any]]:
    """한 mention × 한 방식의 10행. LLM 응답은 sweep_index 0 에서 한 번만
    나왔고 나머지 9행은 그 사본이다(러너 결정 C(i))."""

    grid = [round(0.5 + 0.05 * i, 2) for i in range(10)]
    return [
        make_row(
            t_merge=t,
            sweep_index=i,
            llm_fresh_call=(i == 0),
            tokens_in=120,
            tokens_out=30,
            **over,
        )
        for i, t in enumerate(grid)
    ]


def test_tokens_and_llm_calls_count_fresh_rows_only() -> None:
    rows = _sweep_rows(detail={"llm_error": None})
    llm = compute_metrics(rows)["methods"]["proposed"]["llm"]
    assert llm["calls"] == 1  # 10 이 아니다
    assert llm["tokens_in"] == 120
    assert llm["tokens_out"] == 30
    assert llm["mentions"] == 1


def test_llm_error_call_counts_are_not_multiplied_by_the_grid() -> None:
    rows = _sweep_rows(detail={"llm_error": "timeout"}, decision="identity")
    metrics = compute_metrics(rows)
    llm = metrics["methods"]["proposed"]["llm"]
    assert llm["errors"] == {"timeout": 1}  # 호출 1회가 실패했다(10회가 아니다)
    assert llm["error_calls"] == 1
    # 임계치별 분포는 그 임계치의 행만 센다 -- 한 자리 하나
    for t in metrics["methods"]["proposed"]["by_t_merge"].values():
        assert t["llm_error"] == {"timeout": 1}
        assert t["scored"] == 1


def test_two_mentions_over_the_grid_keep_per_point_denominators_at_two() -> None:
    rows = _sweep_rows(mention_index=0) + _sweep_rows(mention_index=1, decision="identity")
    metrics = compute_metrics(rows)
    method = metrics["methods"]["proposed"]
    assert method["rows"] == 20
    assert len(method["by_t_merge"]) == 10
    assert method["llm"]["calls"] == 2
    assert method["llm"]["tokens_in"] == 240
    for t, p in method["by_t_merge"].items():
        assert p["scored"] == 2, t
        assert p["deferred_identity_rate"] == {"n": 1, "d": 2, "rate": 0.5}


def test_duplicate_rows_are_rejected_instead_of_double_counted() -> None:
    rows = [make_row(), make_row()]
    with pytest.raises(MetricsError, match="duplicate row"):
        compute_metrics(rows)


def test_mention_level_rows_take_the_lowest_sweep_index() -> None:
    rows = _sweep_rows()
    picked = mention_level_rows(rows)
    assert len(picked) == 1
    assert picked[0]["sweep_index"] == 0


def test_mention_level_counts_skipped_llm_once() -> None:
    """통과 후보 0 이라 LLM 을 아예 부르지 않은 mention 은 `llm_fresh_call`
    행이 하나도 없다 -- 그래서 mention 단위 행에서 센다(10행 × 1 mention)."""

    rows = [
        make_row(
            t_merge=round(0.5 + 0.05 * i, 2),
            sweep_index=i,
            llm_fresh_call=False,
            decision="new_person",
            detail={"llm_skipped": True},
        )
        for i in range(10)
    ]
    llm = compute_metrics(rows)["methods"]["proposed"]["llm"]
    assert llm["skipped_mentions"] == 1  # 10 이 아니다
    assert llm["calls"] == 0
    assert llm["mentions"] == 1


# ---------------------------------------------------------------------------
# 8. 분포·부분집합·오류 제외 보기
# ---------------------------------------------------------------------------


def test_forced_reason_distribution_counts_each_row_once() -> None:
    rows = [
        make_row(mention_index=0, decision="identity", detail={"forced_reason": "tie"}),
        make_row(mention_index=1, decision="identity", detail={"forced_reason": "tie"}),
        make_row(mention_index=2, detail={"forced_reason": None}),
        _passing_row(mention_index=0, decision="new_person", detail={"forced_reason": "x"}),
    ]
    p = point(rows)
    assert p["forced_reason"] == {"tie": 2, "none": 1, "x": 1}
    assert sum(p["forced_reason"].values()) == 4  # 골드 3 + passing 1


def test_excluding_llm_error_view_removes_error_rows_from_the_denominator() -> None:
    rows = [
        make_row(mention_index=0, decision="merge", person_id=2),  # 오병합
        make_row(mention_index=1, decision="identity", detail={"llm_error": "timeout"}),
        make_row(mention_index=2),
    ]
    p = point(rows)
    assert p["false_merge_rate"] == {"n": 1, "d": 3, "rate": 1 / 3}  # 기본 분모는 유지
    assert p["excluding_llm_error"]["scored"] == 2
    assert p["excluding_llm_error"]["removed_rows"] == 1
    assert p["excluding_llm_error"]["false_merge_rate"] == {"n": 1, "d": 2, "rate": 0.5}
    assert p["llm_error"] == {"timeout": 1, "none": 2}


def test_subset_metrics_for_rule_unchecked_and_relaxed_merges() -> None:
    def merge_with(signals: dict[str, float], **over: Any) -> dict[str, Any]:
        return make_row(
            candidates=[
                {"person_id": 1, "display_name": "김", "score": 0.9, "signals": signals}
            ],
            **over,
        )

    rows = [
        merge_with({"rule_checked": 0.0}, mention_index=0),  # 정답
        merge_with({"rule_checked": 0.0}, mention_index=1, person_id=1, gold_db_person_id=2),
        merge_with({"rule_checked": 2.0}, mention_index=2),
        make_row(mention_index=3, detail={"relaxed_retry": True}, gold_db_person_id=2),
        make_row(mention_index=4, detail={"relaxed_retry": False}),
    ]
    p = point(rows)
    assert p["subsets"]["merges"] == 5
    assert p["subsets"]["merge_rule_unchecked"]["merges"] == 2
    assert p["subsets"]["merge_rule_unchecked"]["false_merge_rate"] == {
        "n": 1,
        "d": 2,
        "rate": 0.5,
    }
    assert p["subsets"]["merge_relaxed_retry"]["merges"] == 1
    assert p["subsets"]["merge_relaxed_retry"]["false_merge_rate"]["rate"] == 1.0


def test_subset_denominator_zero_is_none() -> None:
    p = point([make_row(decision="identity")])
    assert p["subsets"]["merge_rule_unchecked"]["false_merge_rate"] == {
        "n": 0,
        "d": 0,
        "rate": None,
    }


def test_empty_derive_hints_rate_needs_a_method_that_records_hints() -> None:
    bare = compute_metrics([make_row()])["meta"]["empty_derive_hints"]
    assert bare["n"] == 0 and bare["d"] == 0 and bare["rate"] is None

    rows = [
        make_row(method="embedding_only", mention_index=0, detail={"hints": {}}),
        make_row(
            method="embedding_only", mention_index=1, detail={"hints": {"hierarchy": "상"}}
        ),
    ]
    block = compute_metrics(rows)["meta"]["empty_derive_hints"]
    assert block["n"] == 1 and block["d"] == 2 and block["rate"] == 0.5


def test_by_category_breakdown_and_group_rates() -> None:
    rows = [
        make_row(mention_index=0, category="promotion", decision="merge", person_id=2),
        make_row(mention_index=1, category="pronoun", trap_kind="동명이인"),
        make_row(
            mention_index=2,
            category="pronoun",
            trap_kind="동명이인",
            decision="new_person",
        ),
    ]
    p = point(rows)
    assert p["by_category"]["promotion"]["false_merge_rate"] == {"n": 1, "d": 1, "rate": 1.0}
    assert p["by_category"]["pronoun"]["miss_rate"] == {"n": 1, "d": 2, "rate": 0.5}

    grouped = group_rates(rows, "trap_kind", t_merge=0.8)
    assert grouped["proposed"]["동명이인"]["miss_rate"] == {"n": 1, "d": 2, "rate": 0.5}
    assert grouped["proposed"]["None"]["false_merge_rate"]["n"] == 1


# ---------------------------------------------------------------------------
# 9. 부정 케이스 -- 잘못된 행은 조용히 넘어가지 않는다
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", list(REQUIRED_ROW_KEYS))
def test_missing_required_key_is_an_error(key: str) -> None:
    row = make_row()
    row.pop(key)
    with pytest.raises(MetricsError, match="missing required key"):
        validate_rows([row])


def test_unknown_decision_is_an_error() -> None:
    with pytest.raises(MetricsError, match="unknown decision"):
        validate_rows([make_row(decision="link", person_id=None)])


@pytest.mark.parametrize(
    "over",
    [
        {"mention_kind": "seed"},
        {"ambiguous": "true"},
        {"llm_fresh_call": 1},
        {"sweep_index": -1},
        {"sweep_index": True},
        {"detail": []},
        {"t_merge": 0.813},
        {"expected_ask_user_allowed": []},
        {"expected_ask_user_allowed": ["schedule"]},
        {"gold_person_id": None, "gold_db_person_id": None},
    ],
)
def test_malformed_rows_are_rejected(over: dict[str, Any]) -> None:
    with pytest.raises(MetricsError):
        validate_rows([make_row(**over)])


def test_person_id_rule_is_enforced_both_ways() -> None:
    with pytest.raises(MetricsError, match="without person_id"):
        validate_rows([make_row(decision="merge", person_id=None)])
    with pytest.raises(MetricsError, match="only allowed on merge"):
        validate_rows([make_row(decision="identity", person_id=3)])


def test_ask_kind_must_agree_with_decision() -> None:
    rows = [make_row(decision="identity", detail={"ask_kind": "new_person"})]
    with pytest.raises(MetricsError, match="disagrees with decision"):
        compute_metrics(rows)


def test_mixed_t_new_is_an_error() -> None:
    rows = [make_row(mention_index=0), make_row(mention_index=1, t_new=0.4)]
    with pytest.raises(MetricsError, match="t_new"):
        compute_metrics(rows)


def test_method_missing_a_grid_point_is_an_error() -> None:
    rows = [
        make_row(method="proposed", t_merge=0.5, sweep_index=0),
        make_row(method="proposed", t_merge=0.8, sweep_index=6),
        make_row(method="exact_raw", t_merge=0.5, sweep_index=0),
    ]
    with pytest.raises(MetricsError, match="no rows at t_merge"):
        compute_metrics(rows)


def test_empty_input_is_an_error() -> None:
    with pytest.raises(MetricsError):
        compute_metrics([])


# ---------------------------------------------------------------------------
# 10. 방식 축 · 재현성 · 입출력
# ---------------------------------------------------------------------------


def test_method_key_order_follows_the_resolver_registry() -> None:
    from evaluation.resolvers import ALL_METHODS

    rows = [
        make_row(method=name, mention_index=i)
        for i, name in enumerate(reversed(list(ALL_METHODS)))
    ]
    meta = compute_metrics(rows)["meta"]
    assert meta["methods"] == list(ALL_METHODS)


def _walk(node: Any) -> Any:
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


def test_score_is_never_aggregated_across_methods() -> None:
    """`score` 의 의미는 방식마다 다르다(P3-baselines 인계 14) -- 어떤 집계
    키에도 나타나지 않아야 한다."""

    rows = [make_row(mention_index=0, score=0.91), make_row(method="llm_single", score=0.4)]
    metrics = compute_metrics(rows)
    assert "score" not in set(_walk(metrics))
    assert "score_axis" in metrics["meta"]["denominator_rule"]


def test_same_rows_give_the_same_bytes() -> None:
    rows = _sweep_rows(mention_index=0) + [_passing_row(mention_index=0, decision="identity")]
    first = json.dumps(compute_metrics(rows), ensure_ascii=False, sort_keys=True)
    second = json.dumps(compute_metrics(list(reversed(rows))), ensure_ascii=False, sort_keys=True)
    assert first == second


def test_load_rows_reports_the_broken_line(tmp_path: Any) -> None:
    path = tmp_path / "raw.jsonl"
    path.write_text(
        json.dumps(make_row(), ensure_ascii=False) + "\n\n{ not json\n", encoding="utf-8"
    )
    with pytest.raises(MetricsError, match="raw.jsonl:3"):
        load_rows(path)


def test_load_rows_rejects_empty_and_non_object(tmp_path: Any) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_text("\n\n", encoding="utf-8")
    with pytest.raises(MetricsError, match="no rows"):
        load_rows(empty)
    scalar = tmp_path / "scalar.jsonl"
    scalar.write_text("3\n", encoding="utf-8")
    with pytest.raises(MetricsError, match="must be a JSON object"):
        load_rows(scalar)


def test_cli_writes_metrics_json(tmp_path: Any, capsys: Any) -> None:
    raw = tmp_path / "raw.jsonl"
    raw.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in _sweep_rows()) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "sub" / "metrics.json"
    assert main(["--rows", str(raw), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["methods"]["proposed"]["llm"]["calls"] == 1

    assert main(["--rows", str(raw)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == written


# ---------------------------------------------------------------------------
# gzip 입력 (커밋본 `.jsonl.gz` -- 사용자 결정 2026-09-21, 결정 E 이행 방식)
# ---------------------------------------------------------------------------


def _write_pair(tmp_path: Path, rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    """같은 내용을 평문·gzip 두 벌로 쓴다."""

    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    plain = tmp_path / "raw.jsonl"
    plain.write_text(text, encoding="utf-8")
    packed = tmp_path / ("raw.jsonl" + GZIP_SUFFIX)
    with gzip.open(packed, "wt", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return plain, packed


def test_load_rows_reads_gzip_exactly_like_plain(tmp_path: Path) -> None:
    plain, packed = _write_pair(tmp_path, _sweep_rows())
    assert load_rows(packed) == load_rows(plain)
    # 지표까지 같은 바이트여야 커밋본만으로 재계산이 성립한다(원칙8).
    assert json.dumps(compute_metrics(load_rows(packed)), sort_keys=True) == json.dumps(
        compute_metrics(load_rows(plain)), sort_keys=True
    )


def test_open_jsonl_chooses_by_suffix(tmp_path: Path) -> None:
    plain, packed = _write_pair(tmp_path, [make_row()])
    with open_jsonl(packed) as handle:
        from_gz = handle.read()
    with open_jsonl(plain) as handle:
        from_plain = handle.read()
    assert from_gz == from_plain
    # 평문 경로를 gzip 으로 열지 않는다(확장자만 본다).
    assert [n for n, _ in iter_jsonl(plain)] == [n for n, _ in iter_jsonl(packed)] == [1]


def test_load_rows_rejects_broken_gzip(tmp_path: Path) -> None:
    broken = tmp_path / "raw.jsonl.gz"
    broken.write_bytes(b"not a gzip stream at all")
    with pytest.raises(MetricsError, match="gzip 읽기 실패"):
        load_rows(broken)


def test_load_rows_rejects_truncated_gzip(tmp_path: Path) -> None:
    _, packed = _write_pair(tmp_path, _sweep_rows())
    packed.write_bytes(packed.read_bytes()[:-8])  # CRC·길이 꼬리를 자른다
    with pytest.raises(MetricsError, match="gzip 읽기 실패"):
        load_rows(packed)


def test_cli_output_is_byte_identical_for_gzip_and_plain(tmp_path: Path) -> None:
    plain, packed = _write_pair(tmp_path, _sweep_rows())
    from_plain = tmp_path / "plain.json"
    from_gz = tmp_path / "gz.json"
    assert main(["--rows", str(plain), "--out", str(from_plain)]) == 0
    assert main(["--rows", str(packed), "--out", str(from_gz)]) == 0
    assert from_gz.read_bytes() == from_plain.read_bytes()
