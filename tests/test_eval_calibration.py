"""Refs: P4-pilot-eval R4 D3 원칙3 원칙9 -- 보정표(U3) 계약 테스트.

**네트워크·DB·LLM 없음**(순수). 입력은 손으로 만든 소형 행이고 기대값은 손으로
센 정수다 -- 사람이 검산할 수 있어야 "자기보고 점수의 신뢰 근거"(R4)가 성립
한다.

01-plan 67행이 이름으로 요구한 세 가지:
- 경계값(`0.1`·`0.8`·`1.0`)이 어느 칸인지
- 공급자 두 개가 섞인 입력이 그룹으로 분리되는지
- `detail["score_clamped"] == True` 제외와 `excluded_clamped` 수

여기에 더한 것: `llm.skipped`·`llm.error` 분모 제외와 별도 카운트, 방식 분리
(`proposed`·`llm_single` 만), `T_merge` 격자 10행 사본 미집계, "정답" 정의가
U2 채점표와 같은 함수인지, 부정 케이스(`s_llm` 범위 밖·`model` 누락·빈 입력).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from evaluation.calibration import (
    BIN_LABELS,
    BIN_RULE,
    BINS,
    CORRECT_DEFINITION,
    EXCLUSION_REASONS,
    S_LLM_METHODS,
    CalibrationError,
    bin_index,
    bin_label,
    compute_calibration,
    empty_bins,
    main,
    s_llm_status,
)
from evaluation.metrics import MetricsError

# ---------------------------------------------------------------------------
# 행 공장 -- 기본값은 "제안 방식이 골드(DB 안 인물)를 맞게 병합한 행 하나"
# ---------------------------------------------------------------------------

GRID: tuple[float, ...] = (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95)


def proposed_detail(
    s_llm: float = 0.9,
    *,
    matched_person_id: int | None = 1,
    **over: Any,
) -> dict[str, Any]:
    detail: dict[str, Any] = {
        "trace_id": None,
        "forced_reason": None,
        "relaxed_retry": False,
        "band_by_threshold": "merge",
        "provider": "openai",
        "model": "gpt-4o-mini-2024-07-18",
        "llm_self_reported": True,
        "llm_skipped": False,
        "llm_attempts": 1,
        "llm_error": None,
        "confidence_breakdown": {
            "matched_person_id": matched_person_id,
            "s_llm": s_llm,
            "s_emb": 0.8,
            "s_rule": 1.0,
            "weights": {"llm": 0.5, "emb": 0.3, "rule": 0.2},
            "confidence": 0.89,
            "rule_checked": 3,
            "rule_passed": 3,
        },
        "ask_kind": None,
        "excluded_by": {},
    }
    detail.update(over)
    return detail


def single_detail(**over: Any) -> dict[str, Any]:
    detail: dict[str, Any] = {
        "forced_reason": None,
        "raw_decision": "merge",
        "raw_matched_person_id": 1,
        "reason": "같은 사람",
        "dropped_ids": [],
        "candidate_ids_missing": False,
        "person_count": 3,
        "prompt_chars": 400,
        "provider": "openai",
        "model": "gpt-4o-mini-2024-07-18",
        "llm_error": None,
        "llm_calls": 1,
        "ask_kind": None,
        "uses_embedding": False,
        "uses_llm": True,
        "uses_rules": False,
        "uses_thresholds": False,
    }
    detail.update(over)
    return detail


def make_row(**over: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "method": "proposed",
        "mention": "김팀장",
        "decision": "merge",
        "person_id": 1,
        "score": 0.89,
        "candidates": [],
        "trace_id": None,
        "tokens_in": 100,
        "tokens_out": 20,
        "detail": proposed_detail(),
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
        "t_merge": 0.5,
        "t_new": 0.3,
        "sweep_index": 0,
        "llm_fresh_call": True,
    }
    if "decision" in over and "person_id" not in over:
        over = {**over, "person_id": 1 if over["decision"] == "merge" else None}
    row.update(over)
    return row


def single_row(**over: Any) -> dict[str, Any]:
    """`llm_single` 행. `score` = 접힌 자기보고 `s_llm`."""

    score = over.pop("s_llm", 0.7)
    detail = over.pop("detail", None) or single_detail()
    row = make_row(
        method="llm_single",
        score=score,
        detail=detail,
        candidates=[
            {
                "person_id": 1,
                "display_name": "김철수",
                "score": score,
                "signals": {"s_llm": score},
            }
        ],
        trace_id=None,
        **over,
    )
    if row["decision"] != "merge":
        row["candidates"] = []
    return row


def sweep(row: dict[str, Any]) -> list[dict[str, Any]]:
    """한 mention 의 `T_merge` 격자 10행. LLM 응답은 1회(첫 행만 fresh)."""

    out: list[dict[str, Any]] = []
    for index, t_merge in enumerate(GRID):
        copy = json.loads(json.dumps(row))
        copy["t_merge"] = t_merge
        copy["sweep_index"] = index
        copy["llm_fresh_call"] = index == 0
        out.append(copy)
    return out


def only_group(table: dict[str, Any]) -> dict[str, Any]:
    assert len(table["groups"]) == 1, table["groups"]
    return table["groups"][0]


def cell(group: dict[str, Any], label: str) -> dict[str, Any]:
    (found,) = [b for b in group["bins"] if b["bin"] == label]
    return found


# ---------------------------------------------------------------------------
# 0. 구간 계약 (10칸·경계값)
# ---------------------------------------------------------------------------


def test_ten_bins_of_width_zero_point_one() -> None:
    assert len(BINS) == 10
    assert len(set(BIN_LABELS)) == 10
    assert BIN_LABELS[0] == "0.0-0.1"
    assert BIN_LABELS[-1] == "0.9-1.0"
    for lo, hi in BINS:
        assert abs((hi - lo) - 0.1) < 1e-9


def test_bin_labels_sort_in_numeric_order() -> None:
    """수용 기준 판정 명령이 `sorted({b['bin'] …})` 로 10칸을 센다."""

    assert sorted(BIN_LABELS) == list(BIN_LABELS)


@pytest.mark.parametrize(
    ("value", "label"),
    [
        (0.0, "0.0-0.1"),
        (0.05, "0.0-0.1"),
        (0.1, "0.1-0.2"),  # 경계값은 위쪽 칸
        (0.15, "0.1-0.2"),
        (0.2, "0.2-0.3"),
        (0.3, "0.3-0.4"),  # int(0.3*10)==2 함정
        (0.7, "0.7-0.8"),
        (0.79999, "0.7-0.8"),
        (0.8, "0.8-0.9"),  # 경계값은 위쪽 칸
        (0.9, "0.9-1.0"),
        (0.95, "0.9-1.0"),
        (1.0, "0.9-1.0"),  # 마지막 칸만 오른쪽 닫힘
    ],
)
def test_boundary_values_land_in_the_upper_bin(value: float, label: str) -> None:
    assert bin_label(value) == label
    assert bin_index(value) == BIN_LABELS.index(label)


def test_every_tenth_lands_in_its_own_bin() -> None:
    """부동소수로 만든 경계값도 같은 칸이다(0.1 씩 더해 만든 값)."""

    value = 0.0
    seen = []
    for _ in range(10):
        seen.append(bin_label(round(value, 1)))
        value += 0.1
    assert seen == list(BIN_LABELS)


def test_empty_bins_skeleton_has_ten_cells_with_null_accuracy() -> None:
    skeleton = empty_bins()
    assert [c["bin"] for c in skeleton] == list(BIN_LABELS)
    assert all(c["n"] == 0 and c["correct"] == 0 and c["accuracy"] is None for c in skeleton)
    assert [c["right_closed"] for c in skeleton] == [False] * 9 + [True]


def test_bin_rule_is_written_next_to_the_numbers() -> None:
    table = compute_calibration([make_row()])
    assert table["meta"]["bin_rule"] == BIN_RULE
    for token in ("0.1-0.2", "0.8-0.9", "0.9-1.0", "accuracy: null"):
        assert token in table["meta"]["bin_rule"]


# ---------------------------------------------------------------------------
# 1. 기본 집계
# ---------------------------------------------------------------------------


def test_single_correct_row_lands_in_its_bin() -> None:
    table = compute_calibration([make_row()])
    group = only_group(table)
    assert (group["method"], group["provider"], group["model"]) == (
        "proposed",
        "openai",
        "gpt-4o-mini-2024-07-18",
    )
    assert group["n"] == 1 and group["correct"] == 1 and group["accuracy"] == 1.0
    assert cell(group, "0.9-1.0") == {
        "bin": "0.9-1.0",
        "index": 9,
        "lo": 0.9,
        "hi": 1.0,
        "right_closed": True,
        "n": 1,
        "correct": 1,
        "accuracy": 1.0,
    }
    assert sum(c["n"] for c in group["bins"]) == 1


def test_wrong_person_id_is_counted_but_not_correct() -> None:
    """오병합(다른 id)은 분모에 남고 분자에서만 빠진다 -- 보정표는 정확도
    측정이지 성공 사례 모음이 아니다(원칙8)."""

    rows = [
        make_row(scenario_id="sc-001", person_id=1, gold_db_person_id=1),
        make_row(scenario_id="sc-002", person_id=2, gold_db_person_id=1),
    ]
    group = only_group(compute_calibration(rows))
    assert group["n"] == 2
    assert group["correct"] == 1
    assert group["accuracy"] == 0.5
    assert cell(group, "0.9-1.0")["n"] == 2


def test_new_person_on_db_outside_gold_is_correct() -> None:
    """골드가 DB 밖 인물이면 `new_person` 이 정답이다(U2 채점표)."""

    row = make_row(
        decision="new_person",
        gold_db_person_id=None,
        detail=proposed_detail(0.45),
    )
    group = only_group(compute_calibration([row]))
    assert cell(group, "0.4-0.5") == dict(
        cell(group, "0.4-0.5"), n=1, correct=1, accuracy=1.0
    )


def test_new_person_on_db_inside_gold_is_wrong() -> None:
    """같은 사람을 새 인물로 본 것(미검출)은 오답이다."""

    row = make_row(
        decision="new_person",
        gold_db_person_id=1,
        detail=proposed_detail(0.45),
    )
    group = only_group(compute_calibration([row]))
    assert (group["n"], group["correct"], group["accuracy"]) == (1, 0, 0.0)


def test_identity_row_is_counted_as_wrong_not_excluded() -> None:
    """`identity`(사람에게 미룸)는 `decision` 이 골드와 다르므로 오답이다 --
    U2 의 제3 범주(오병합·미검출 어디에도 안 넣음)와 달리 보정표는 결정 F(i)
    한 줄("decision·person_id 가 골드와 일치")만 쓴다."""

    row = make_row(decision="identity", detail=proposed_detail(0.55))
    group = only_group(compute_calibration([row]))
    assert (group["n"], group["correct"]) == (1, 0)
    assert cell(group, "0.5-0.6")["n"] == 1


def test_empty_bin_accuracy_is_null_not_zero() -> None:
    group = only_group(compute_calibration([make_row()]))
    empty = [c for c in group["bins"] if c["n"] == 0]
    assert len(empty) == 9
    assert all(c["accuracy"] is None for c in empty)


def test_correct_definition_is_the_metrics_scorer() -> None:
    """정답 정의는 U2 채점표와 **같은 함수**다(두 파일이 갈라지면 안 된다)."""

    assert "classify_gold_row" in CORRECT_DEFINITION
    assert "merge_correct" in CORRECT_DEFINITION and "new_person_correct" in CORRECT_DEFINITION
    assert compute_calibration([make_row()])["meta"]["correct_definition"] == (
        CORRECT_DEFINITION
    )


# ---------------------------------------------------------------------------
# 2. 공급자·모델·방식 분리 (01-plan 67행 "공급자 두 개가 섞인 입력")
# ---------------------------------------------------------------------------


def test_two_providers_are_split_into_groups() -> None:
    rows = [
        make_row(scenario_id="sc-001", detail=proposed_detail(0.9)),
        make_row(
            scenario_id="sc-002",
            detail=proposed_detail(0.9, provider="gemini", model="gemini-2.5-flash-001"),
        ),
        make_row(
            scenario_id="sc-003",
            person_id=2,
            detail=proposed_detail(0.9, provider="gemini", model="gemini-2.5-flash-001"),
        ),
    ]
    table = compute_calibration(rows)
    assert [(g["provider"], g["model"], g["n"], g["correct"]) for g in table["groups"]] == [
        ("gemini", "gemini-2.5-flash-001", 2, 1),
        ("openai", "gpt-4o-mini-2024-07-18", 1, 1),
    ]
    for group in table["groups"]:
        assert len(group["bins"]) == 10


def test_same_provider_different_model_is_a_different_group() -> None:
    rows = [
        make_row(scenario_id="sc-001"),
        make_row(scenario_id="sc-002", detail=proposed_detail(0.9, model="gpt-4.1-mini")),
    ]
    table = compute_calibration(rows)
    assert [g["model"] for g in table["groups"]] == [
        "gpt-4.1-mini",
        "gpt-4o-mini-2024-07-18",
    ]


def test_methods_are_separate_groups_in_registry_order() -> None:
    rows = [make_row(scenario_id="sc-001"), single_row(scenario_id="sc-001")]
    table = compute_calibration(rows)
    assert [g["method"] for g in table["groups"]] == ["proposed", "llm_single"]
    assert list(S_LLM_METHODS) == ["proposed", "llm_single"]
    assert table["meta"]["methods"] == ["proposed", "llm_single"]


def test_group_model_is_the_response_model_not_the_configured_string() -> None:
    """02-plan-verify R-6 -- 그룹 키는 판정이 돌려준 모델명, 설정 문자열은
    `meta.model_configured`(P3-llm-providers §7 인계 4)."""

    table = compute_calibration(
        [make_row()], model_configured={"openai": "gpt-4o-mini", "gemini": "gemini-2.5-flash"}
    )
    assert only_group(table)["model"] == "gpt-4o-mini-2024-07-18"
    assert table["meta"]["model_configured"] == {
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4o-mini",
    }


def test_model_configured_defaults_to_empty_object() -> None:
    table = compute_calibration([make_row()])
    assert table["meta"]["model_configured"] == {}
    assert "환경변수를 읽지 않는다" in table["meta"]["model_configured_source"]


def test_non_llm_methods_are_ignored_entirely() -> None:
    """`exact_raw`·`exact_norm`·`embedding_only` 는 `s_llm` 이 없다."""

    rows = [
        make_row(scenario_id="sc-001"),
        make_row(scenario_id="sc-001", method="exact_raw", detail={}),
        make_row(scenario_id="sc-001", method="exact_norm", detail={}),
        make_row(scenario_id="sc-001", method="embedding_only", detail={"hints": {}}),
    ]
    table = compute_calibration(rows)
    assert [g["method"] for g in table["groups"]] == ["proposed"]
    assert table["meta"]["ignored_method_rows"] == 3
    assert table["meta"]["rows_selected"] == 1
    assert table["excluded"]["total"] == 0


# ---------------------------------------------------------------------------
# 3. clamp 제외 (01-plan 67행 · P3-baselines 04-review [권고] 2)
# ---------------------------------------------------------------------------


def test_score_clamped_row_is_excluded_and_counted() -> None:
    rows = [
        make_row(scenario_id="sc-001"),
        make_row(scenario_id="sc-002", detail=proposed_detail(0.9, score_clamped=True)),
    ]
    table = compute_calibration(rows)
    group = only_group(table)
    assert group["n"] == 1
    assert cell(group, "0.9-1.0")["n"] == 1
    assert table["excluded_clamped"] == 1
    assert table["excluded"]["score_clamped"] == 1
    assert group["excluded"]["score_clamped"] == 1


def test_clamped_llm_single_row_is_excluded_too() -> None:
    rows = [
        single_row(scenario_id="sc-001"),
        single_row(
            scenario_id="sc-002",
            s_llm=1.0,
            detail=single_detail(score_clamped=True),
        ),
    ]
    table = compute_calibration(rows)
    assert table["excluded_clamped"] == 1
    assert only_group(table)["n"] == 1


def test_excluded_clamped_is_a_top_level_integer() -> None:
    """수용 기준 판정 명령이 `d['excluded_clamped']` 를 그대로 찍는다."""

    table = compute_calibration([make_row()])
    assert table["excluded_clamped"] == 0
    assert isinstance(table["excluded_clamped"], int)


# ---------------------------------------------------------------------------
# 4. llm.skipped · llm.error 제외 + 별도 카운트
# ---------------------------------------------------------------------------


def test_llm_skipped_mention_is_excluded_and_counted() -> None:
    """통과 후보 0 -> 호출 자체가 없었다. `s_llm` 0.0 은 귀속값이다."""

    rows = [
        make_row(scenario_id="sc-001"),
        make_row(
            scenario_id="sc-002",
            decision="new_person",
            gold_db_person_id=None,
            llm_fresh_call=False,
            detail=proposed_detail(
                0.0,
                matched_person_id=None,
                llm_skipped=True,
                llm_attempts=0,
                forced_reason="no_candidates",
                provider=None,
                model=None,
            ),
        ),
    ]
    table = compute_calibration(rows)
    assert only_group(table)["n"] == 1
    assert table["excluded"]["llm_skipped"] == 1
    assert cell(only_group(table), "0.0-0.1")["n"] == 0
    # provider·model 이 없는 행은 그룹에 넣을 수 없으므로 `unassigned` 로 간다
    assert table["unassigned"]["proposed"]["llm_skipped"] == 1


def test_llm_single_zero_calls_is_skipped() -> None:
    row = single_row(
        s_llm=0.0,
        decision="new_person",
        gold_db_person_id=None,
        detail=single_detail(
            raw_decision=None,
            raw_matched_person_id=None,
            llm_calls=0,
            forced_reason="empty_mention",
        ),
    )
    table = compute_calibration([row])
    assert table["excluded"]["llm_skipped"] == 1
    assert table["groups"][0]["excluded"]["llm_skipped"] == 1
    assert table["groups"][0]["n"] == 0


def test_llm_error_rows_are_excluded_and_counted_by_kind() -> None:
    rows = [
        make_row(scenario_id="sc-001"),
        make_row(
            scenario_id="sc-002",
            decision="identity",
            detail=proposed_detail(
                0.0,
                matched_person_id=None,
                llm_error="timeout",
                forced_reason="llm_failed",
                provider=None,
                model=None,
            ),
        ),
        make_row(
            scenario_id="sc-003",
            decision="identity",
            detail=proposed_detail(
                0.0,
                matched_person_id=None,
                llm_error="rate_limit",
                forced_reason="llm_failed",
                provider=None,
                model=None,
            ),
        ),
        make_row(
            scenario_id="sc-004",
            decision="identity",
            detail=proposed_detail(
                0.0,
                matched_person_id=None,
                llm_error="timeout",
                forced_reason="llm_failed",
                provider=None,
                model=None,
            ),
        ),
    ]
    table = compute_calibration(rows)
    assert only_group(table)["n"] == 1
    assert table["excluded"]["llm_error"] == 3
    assert table["excluded"]["llm_error_kinds"] == {"rate_limit": 1, "timeout": 2}
    assert table["excluded"]["total"] == 3


def test_llm_error_row_that_knows_its_model_is_counted_in_the_group() -> None:
    """공급자·모델을 아는 오류 행은 그 그룹의 `excluded` 로 간다(어느 모델이
    몇 번 실패했는지 표에 남는다)."""

    rows = [
        make_row(scenario_id="sc-001"),
        make_row(
            scenario_id="sc-002",
            decision="identity",
            detail=proposed_detail(0.0, matched_person_id=None, llm_error="api_error"),
        ),
    ]
    table = compute_calibration(rows)
    group = only_group(table)
    assert group["n"] == 1
    assert group["excluded"]["llm_error_kinds"] == {"api_error": 1}
    assert table["unassigned"] == {}


def test_placeholder_s_llm_is_excluded_not_binned_at_zero() -> None:
    """강제 경로(`no_matched`)의 `s_llm=0.0` 은 자기보고가 아니라 귀속값이다 --
    `0.0-0.1` 칸을 오염시키지 않고 별도로 센다(app/er/confidence.py
    `_forced_decision`)."""

    rows = [
        make_row(scenario_id="sc-001"),
        make_row(
            scenario_id="sc-002",
            decision="identity",
            detail=proposed_detail(
                0.0, matched_person_id=None, forced_reason="no_matched"
            ),
        ),
    ]
    table = compute_calibration(rows)
    group = only_group(table)
    assert cell(group, "0.0-0.1")["n"] == 0
    assert cell(group, "0.0-0.1")["accuracy"] is None
    assert table["excluded"]["placeholder_s_llm"] == 1
    assert group["excluded"]["placeholder_s_llm"] == 1


def test_llm_single_placeholder_without_raw_decision_is_excluded() -> None:
    row = single_row(
        s_llm=0.0,
        decision="identity",
        detail=single_detail(
            raw_decision=None, raw_matched_person_id=None, forced_reason="timeout_x"
        ),
    )
    table = compute_calibration([row])
    assert table["excluded"]["placeholder_s_llm"] == 1
    assert table["groups"][0]["n"] == 0


def test_genuine_zero_self_report_is_counted() -> None:
    """LLM 이 인물을 고르고 `s_llm=0.0` 을 보고했으면 그것은 자기보고다 --
    placeholder 규칙이 진짜 0 을 삼키지 않는다."""

    row = make_row(detail=proposed_detail(0.0, matched_person_id=1))
    group = only_group(compute_calibration([row]))
    assert cell(group, "0.0-0.1")["n"] == 1
    assert group["n"] == 1


def test_exclusion_reasons_are_listed_in_priority_order() -> None:
    table = compute_calibration([make_row()])
    assert table["meta"]["exclusion_order"] == list(EXCLUSION_REASONS)
    assert EXCLUSION_REASONS == (
        "passing_mention",
        "ambiguous_mention",
        "llm_error",
        "llm_skipped",
        "score_clamped",
        "placeholder_s_llm",
    )


def test_error_wins_over_clamp_when_both_are_present() -> None:
    """우선순위가 흔들리면 수치가 흔들린다 -- 한 곳에서만 정한다."""

    detail = proposed_detail(
        0.9, matched_person_id=None, llm_error="schema", score_clamped=True
    )
    status, value, kind = s_llm_status(make_row(decision="identity", detail=detail))
    assert (status, value, kind) == ("llm_error", None, "schema")


def test_clamp_wins_over_placeholder() -> None:
    detail = proposed_detail(0.9, matched_person_id=None, score_clamped=True)
    status, _value, _kind = s_llm_status(make_row(decision="identity", detail=detail))
    assert status == "score_clamped"


# ---------------------------------------------------------------------------
# 5. 분모 규칙 재사용 (U2) -- passing · ambiguous
# ---------------------------------------------------------------------------


def test_passing_mention_is_excluded_from_the_table() -> None:
    """등록하면 안 되는 지나가는 언급은 골드가 없어 정오를 정의할 수 없다."""

    rows = [
        make_row(scenario_id="sc-038"),
        make_row(
            scenario_id="sc-038",
            mention_kind="passing",
            mention_index=1,
            gold_person_id=None,
            gold_db_person_id=None,
            decision="new_person",
        ),
    ]
    table = compute_calibration(rows)
    assert only_group(table)["n"] == 1
    assert table["excluded"]["passing_mention"] == 1


def test_ambiguous_mention_is_excluded_from_the_table() -> None:
    rows = [
        make_row(scenario_id="sc-013"),
        make_row(
            scenario_id="sc-013",
            mention_index=3,
            ambiguous=True,
            gold_person_id=None,
            gold_db_person_id=None,
        ),
    ]
    table = compute_calibration(rows)
    assert only_group(table)["n"] == 1
    assert table["excluded"]["ambiguous_mention"] == 1


# ---------------------------------------------------------------------------
# 6. 격자 사본 중복 미집계 (결정 C(i))
# ---------------------------------------------------------------------------


def test_ten_grid_copies_of_one_mention_count_once() -> None:
    table = compute_calibration(sweep(make_row()))
    group = only_group(table)
    assert group["n"] == 1
    assert cell(group, "0.9-1.0")["n"] == 1
    assert table["meta"]["row_count"] == 10
    assert table["meta"]["unit_count"] == 1
    assert table["meta"]["counted_units"] == 1
    assert table["meta"]["llm_fresh_calls"] == {"proposed": 1}


def test_two_mentions_two_methods_ten_thresholds_is_four_units() -> None:
    rows: list[dict[str, Any]] = []
    for scenario in ("sc-001", "sc-002"):
        rows += sweep(make_row(scenario_id=scenario))
        rows += sweep(single_row(scenario_id=scenario))
    table = compute_calibration(rows)
    assert table["meta"]["row_count"] == 40
    assert table["meta"]["unit_count"] == 4
    assert sum(g["n"] for g in table["groups"]) == 4
    assert [g["n"] for g in table["groups"]] == [2, 2]
    assert table["meta"]["llm_fresh_calls"] == {"llm_single": 2, "proposed": 2}


def test_default_scoring_row_is_the_fresh_call_row() -> None:
    rows = sweep(make_row())
    table = compute_calibration(rows)
    assert table["meta"]["scored_at_t_merge"] == ["0.5"]
    assert table["meta"]["t_merge_option"] is None


def test_t_merge_option_picks_that_threshold_row() -> None:
    """같은 자기보고 점수라도 밴드는 임계치에 따라 달라진다 -- 어느 임계치로
    채점했는지 파일에 남는다."""

    rows = sweep(make_row())
    for row in rows:
        if row["t_merge"] > 0.85:  # 높은 임계치에서는 병합하지 않았다고 두자
            row["decision"] = "identity"
            row["person_id"] = None
    low = compute_calibration(rows, t_merge=0.5)
    high = compute_calibration(rows, t_merge=0.95)
    assert low["meta"]["scored_at_t_merge"] == ["0.5"]
    assert high["meta"]["scored_at_t_merge"] == ["0.95"]
    assert only_group(low)["correct"] == 1
    assert only_group(high)["correct"] == 0
    assert only_group(high)["n"] == 1  # 분모는 그대로


def test_duplicate_fresh_calls_for_one_mention_stop_the_run() -> None:
    rows = sweep(make_row())
    rows[3]["llm_fresh_call"] = True
    with pytest.raises(CalibrationError, match="fresh LLM calls"):
        compute_calibration(rows)


def test_missing_row_at_requested_threshold_stops_the_run() -> None:
    with pytest.raises(CalibrationError, match="no row at t_merge"):
        compute_calibration([make_row(t_merge=0.5)], t_merge=0.8)


# ---------------------------------------------------------------------------
# 7. 부정 케이스
# ---------------------------------------------------------------------------


def test_empty_input_stops_the_run() -> None:
    with pytest.raises(CalibrationError, match="no rows"):
        compute_calibration([])


@pytest.mark.parametrize("value", [1.5, -0.1, float("nan")])
def test_s_llm_out_of_range_stops_the_run(value: float) -> None:
    with pytest.raises(CalibrationError):
        compute_calibration([make_row(detail=proposed_detail(value))])


@pytest.mark.parametrize("value", ["0.9", None, True])
def test_s_llm_that_is_not_a_number_stops_the_run(value: Any) -> None:
    with pytest.raises(CalibrationError, match="s_llm is not a number"):
        compute_calibration([make_row(detail=proposed_detail(value))])


def test_missing_model_on_a_counted_row_stops_the_run() -> None:
    """그룹 키가 없으면 어느 모델의 보정표인지 말할 수 없다(R-6)."""

    with pytest.raises(CalibrationError, match="detail\\['provider'\\]"):
        compute_calibration([make_row(detail=proposed_detail(0.9, model=None))])


def test_missing_provider_on_a_counted_row_stops_the_run() -> None:
    detail = proposed_detail(0.9)
    detail.pop("provider")
    with pytest.raises(CalibrationError, match="counted row needs"):
        compute_calibration([make_row(detail=detail)])


def test_missing_confidence_breakdown_stops_the_run() -> None:
    detail = proposed_detail(0.9)
    detail.pop("confidence_breakdown")
    with pytest.raises(CalibrationError, match="confidence_breakdown"):
        compute_calibration([make_row(detail=detail)])


def test_breakdown_without_s_llm_stops_the_run() -> None:
    detail = proposed_detail(0.9)
    detail["confidence_breakdown"] = {"matched_person_id": 1, "s_emb": 0.5}
    with pytest.raises(CalibrationError, match="no 's_llm'"):
        compute_calibration([make_row(detail=detail)])


def test_llm_single_score_disagreeing_with_candidate_signal_stops_the_run() -> None:
    row = single_row(s_llm=0.7)
    row["candidates"][0]["signals"]["s_llm"] = 0.4
    with pytest.raises(CalibrationError, match="s_llm disagrees"):
        compute_calibration([row])


def test_unknown_method_in_s_llm_status_stops_the_run() -> None:
    with pytest.raises(CalibrationError, match="does not report s_llm"):
        s_llm_status(make_row(method="exact_raw"))


def test_row_contract_violations_are_reused_from_metrics() -> None:
    """행 계약 검사는 U2 의 `validate_rows` 하나를 쓴다(두 벌 금지)."""

    broken = make_row()
    broken.pop("gold_db_person_id")
    with pytest.raises(MetricsError, match="missing required key"):
        compute_calibration([broken])

    with pytest.raises(MetricsError, match="unknown decision"):
        compute_calibration([make_row(decision="maybe", person_id=None)])


def test_calibration_error_is_a_metrics_error() -> None:
    assert issubclass(CalibrationError, MetricsError)


# ---------------------------------------------------------------------------
# 8. 재현성·CLI
# ---------------------------------------------------------------------------


def test_same_rows_give_the_same_bytes() -> None:
    rows = [
        make_row(scenario_id="sc-002", detail=proposed_detail(0.9, provider="gemini", model="g")),
        single_row(scenario_id="sc-001"),
        make_row(scenario_id="sc-001"),
    ]
    first = json.dumps(compute_calibration(rows), ensure_ascii=False, sort_keys=True)
    second = json.dumps(
        compute_calibration(list(reversed(rows))), ensure_ascii=False, sort_keys=True
    )
    assert first == second


def test_cli_writes_the_table(tmp_path: Any) -> None:
    rows_path = tmp_path / "raw.jsonl"
    rows_path.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False)
            for row in sweep(make_row()) + sweep(single_row())
        )
        + "\n",
        encoding="utf-8",
    )
    out_path = tmp_path / "sub" / "calibration.json"
    rc = main(
        [
            "--rows",
            str(rows_path),
            "--out",
            str(out_path),
            "--model-configured",
            "openai=gpt-4o-mini",
        ]
    )
    assert rc == 0
    table = json.loads(out_path.read_text(encoding="utf-8"))
    assert sorted({b["bin"] for g in table["groups"] for b in g["bins"]}) == list(BIN_LABELS)
    assert table["excluded_clamped"] == 0
    assert table["meta"]["model_configured"] == {"openai": "gpt-4o-mini"}
    assert [g["method"] for g in table["groups"]] == ["proposed", "llm_single"]


def test_cli_prints_to_stdout_without_out(capsys: Any, tmp_path: Any) -> None:
    rows_path = tmp_path / "raw.jsonl"
    rows_path.write_text(json.dumps(make_row(), ensure_ascii=False) + "\n", encoding="utf-8")
    assert main(["--rows", str(rows_path), "--t-merge", "0.5"]) == 0
    table = json.loads(capsys.readouterr().out)
    assert table["meta"]["scored_at_t_merge"] == ["0.5"]


def test_cli_output_is_byte_identical_for_gzip_and_plain(tmp_path: Any) -> None:
    """커밋본 `.jsonl.gz` 로 돌린 보정표가 평문과 **바이트까지** 같다.

    원시 JSONL 은 5MB 한도 때문에 gzip 으로 커밋한다(사용자 결정 2026-09-21,
    결정 E 유지) -- 커밋된 그 파일 하나로 보정표가 재생성돼야 한다(원칙8).
    """

    import gzip

    text = (
        "\n".join(
            json.dumps(row, ensure_ascii=False)
            for row in sweep(make_row()) + sweep(single_row())
        )
        + "\n"
    )
    plain = tmp_path / "raw.jsonl"
    plain.write_text(text, encoding="utf-8")
    packed = tmp_path / "raw.jsonl.gz"
    with gzip.open(packed, "wt", encoding="utf-8", newline="") as handle:
        handle.write(text)

    from_plain = tmp_path / "plain.json"
    from_gz = tmp_path / "gz.json"
    assert main(["--rows", str(plain), "--out", str(from_plain)]) == 0
    assert main(["--rows", str(packed), "--out", str(from_gz)]) == 0
    assert from_gz.read_bytes() == from_plain.read_bytes()


def test_cli_rejects_broken_gzip(tmp_path: Any) -> None:
    broken = tmp_path / "raw.jsonl.gz"
    broken.write_bytes(b"\x1f\x8b not really compressed")
    with pytest.raises(MetricsError, match="gzip 읽기 실패"):
        main(["--rows", str(broken)])


@pytest.mark.parametrize("bad", ["gpt-4o-mini", "openai=", "=gpt"])
def test_cli_rejects_malformed_model_configured(bad: str, tmp_path: Any) -> None:
    rows_path = tmp_path / "raw.jsonl"
    rows_path.write_text(json.dumps(make_row(), ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(CalibrationError, match="provider=model"):
        main(["--rows", str(rows_path), "--model-configured", bad])


def test_schema_version_and_top_level_keys() -> None:
    table = compute_calibration([make_row()])
    assert table["schema_version"] == 1
    assert set(table) == {
        "schema_version",
        "groups",
        "excluded_clamped",
        "excluded",
        "unassigned",
        "meta",
    }


def test_no_network_or_db_imports() -> None:
    """입력은 JSONL 뿐이다 -- 모듈이 DB·네트워크·`app/` 을 끌어오지 않는다."""

    import inspect

    import evaluation.calibration as module

    source = inspect.getsource(module)
    for banned in (
        "import requests",
        "import httpx",
        "from app.",
        "import app",
        "import sqlalchemy",
        "import openai",
        "os.environ",
    ):
        assert banned not in source
