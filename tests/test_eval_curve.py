"""Refs: P4-pilot-eval R3 D10 S3.7 원칙1 원칙2 원칙8 -- 곡선·게이트(U4) 계약 테스트.

**네트워크·DB·LLM 없음**(순수). 입력은 손으로 만든 소형 JSONL 행과, 게이트
판정식만 보기 위한 손 입력 `metrics` 딕셔너리다 -- 게이트는 P5 착수 여부를
가르는 한 줄이므로(결정 K) 그 판정식이 사람이 검산할 수 있는 수치 위에서
돌아가야 한다.

전수 단언하는 것:
- 격자 10점 · `T_new` 0.3 불변 · 방식 키 5개와 `RESOLVERS` 순서(인계 4)
- `gate` 판정식: **동률 4조합**(=,= / =,< / <,= / =,>)·**지배 1건**·
  **D10 역방향 1건**(중간 격자점 역전) 손 입력
- `rate: null` 이면 조용히 통과하지 않는다(`pass: false` + `gate.reason`)
- `--validate` 통과/거부(방식 키 수·순서·`meta`·`gate`·격자·비율 형식)
- `curve.csv` 열·행 수(5 × 10 × 3)·`t_new` 한 값·바이트 재현성
- `forced_reason` 은 곡선 계열과 별도 집계
- 격자 키의 부동소수 잡음(`0.7999999999999999`)이 `0.8` 로 접힌다(R-7(2))
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from evaluation.curve import (
    CURVE_COLUMNS,
    EXPECTED_GRID,
    GATE_T_MERGE,
    PROPOSED,
    SERIES,
    T_NEW,
    CurveError,
    build_gate,
    build_metrics_document,
    curve_rows,
    forced_reason_summary,
    validate_metrics_document,
    write_curve_csv,
)
from evaluation.metrics import compute_metrics, ratio
from evaluation.metrics import main as metrics_main

METHODS = ("proposed", "exact_raw", "exact_norm", "embedding_only", "llm_single")
GRID = [round(0.5 + 0.05 * i, 2) for i in range(10)]


# ---------------------------------------------------------------------------
# 1) 손 입력 metrics (게이트 판정식 전용 -- 분자·분모를 사람이 센다)
# ---------------------------------------------------------------------------


def make_point(t: float | str, fm: int, miss: int, identity: int, d: int = 10) -> dict[str, Any]:
    return {
        "method": "?",
        "t_merge": float(t),
        "t_new": T_NEW,
        "scored": d,
        "false_merge_rate": ratio(fm, d),
        "miss_rate": ratio(miss, d),
        "ask_user_rate_by_kind": {
            "identity": ratio(identity, d),
            "new_person": ratio(0, d),
            "schedule": ratio(0, d),
        },
        "forced_reason": {"none": d},
    }


def make_metrics(spec: dict[str, dict[Any, tuple[int, int, int]]]) -> dict[str, Any]:
    """`{method: {t: (false_merge, miss, identity)}}` -> U2 모양의 metrics."""

    methods: dict[str, Any] = {}
    for method, by_t in spec.items():
        methods[method] = {
            "grid": [float(t) for t in by_t],
            "by_t_merge": {
                (t if isinstance(t, str) else f"{float(t):g}"): {
                    **make_point(float(t), *counts),
                    "method": method,
                }
                for t, counts in by_t.items()
            },
            "llm": {"calls": 0},
            "rows": 0,
        }
    grid = [float(t) for t in next(iter(spec.values()))]
    return {
        "methods": methods,
        "meta": {
            "methods": list(spec),
            "grid": grid,
            "t_new": T_NEW,
            "denominator_rule": {"scored_base": "손 입력"},
        },
    }


def gate_of(
    proposed: tuple[int, int, int],
    baselines: dict[str, tuple[int, int, int]],
) -> dict[str, Any]:
    """`T_merge=0.8` 한 점만 있는 metrics 로 게이트를 판정한다."""

    spec: dict[str, dict[Any, tuple[int, int, int]]] = {PROPOSED: {0.8: proposed}}
    for name in METHODS[1:]:
        spec[name] = {0.8: baselines.get(name, proposed)}
    return build_gate(make_metrics(spec))


# ---------------------------------------------------------------------------
# 2) 손 입력 JSONL 행 (조립 전체를 통과시키는 소형 실행)
# ---------------------------------------------------------------------------


def make_row(method: str, t: float, **over: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "method": method,
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
        "expected_ask_user_allowed": ["none", "identity"],
        "trap_kind": None,
        "t_merge": t,
        "t_new": T_NEW,
        "sweep_index": GRID.index(round(t, 2)),
        "llm_fresh_call": False,
    }
    row.update(over)
    if row["decision"] != "merge":
        row["person_id"] = None
    return row


def scenario_rows(
    *,
    t_new: float = T_NEW,
    forced_at: str | None = None,
    detail_identity: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """다섯 방식 × 격자 10점 × mention 3개.

    - mention 0: 언제나 맞게 병합(`merge_correct`)
    - mention 1: `proposed` 만 `T_merge < 0.75` 에서 잘못 병합하고 그 위로는
      `identity` 로 미룬다 -> 오병합률은 비증가, identity 발생률은 비감소
      (D10 방향). 베이스라인은 임계치를 읽지 않으므로 평탄하다.
    - mention 2: 골드가 DB 밖 인물 -> `new_person` 이 정답
    """

    rows: list[dict[str, Any]] = []
    for method in METHODS:
        for t in GRID:
            fresh = t == GRID[0]
            detail: dict[str, Any] = dict(detail_identity or {})
            if forced_at == method:
                detail["forced_reason"] = "no_candidates"
            rows.append(
                make_row(method, t, mention_index=0, detail=dict(detail), llm_fresh_call=fresh)
            )
            if method == PROPOSED:
                decision = "merge" if t < 0.75 else "identity"
            else:
                decision = "merge" if method in {"exact_raw", "embedding_only"} else "identity"
            rows.append(
                make_row(
                    method,
                    t,
                    mention_index=1,
                    gold_person_id="p2",
                    gold_db_person_id=2,
                    decision=decision,
                    person_id=1,  # 다른 사람 id = 오병합
                    detail=dict(detail),
                    llm_fresh_call=fresh,
                )
            )
            rows.append(
                make_row(
                    method,
                    t,
                    mention_index=2,
                    gold_person_id="p9",
                    gold_db_person_id=None,
                    decision="new_person",
                    expected_ask_user_allowed=["new_person"],
                    detail=dict(detail),
                    llm_fresh_call=fresh,
                )
            )
    if t_new != T_NEW:
        for row in rows:
            row["t_new"] = t_new
    return rows


@pytest.fixture()
def document() -> dict[str, Any]:
    return build_metrics_document(
        scenario_rows(),
        embedding_model="text-embedding-3-small",
        dataset_hash="sha256:deadbeef",
        run_id="run-1",
        model_configured={"openai": "gpt-4o-mini"},
    )


# ---------------------------------------------------------------------------
# 격자·T_new·방식 키 (01-plan 68행)
# ---------------------------------------------------------------------------


def test_grid_has_ten_points(document: dict[str, Any]) -> None:
    assert document["meta"]["grid"] == list(EXPECTED_GRID)
    assert len(document["meta"]["grid"]) == 10
    for method in METHODS:
        assert len(document[method]["by_t_merge"]) == 10


def test_expected_grid_matches_runner() -> None:
    from evaluation.runner import T_MERGE_GRID, T_NEW as RUNNER_T_NEW

    assert tuple(EXPECTED_GRID) == tuple(T_MERGE_GRID)
    assert RUNNER_T_NEW == T_NEW == 0.3


def test_t_new_is_fixed(document: dict[str, Any]) -> None:
    assert document["meta"]["t_new"] == 0.3
    assert document["meta"]["t_new_fixed"] is True
    assert {
        point["t_new"]
        for method in METHODS
        for point in document[method]["by_t_merge"].values()
    } == {0.3}


def test_t_new_other_than_03_is_rejected() -> None:
    with pytest.raises(CurveError, match="t_new"):
        build_metrics_document(scenario_rows(t_new=0.4))


def test_method_keys_are_five_in_resolver_order(document: dict[str, Any]) -> None:
    keys = [key for key in document if key not in {"meta", "gate"}]
    assert keys == list(METHODS)
    assert len(keys) == 5
    assert document["meta"]["methods"] == list(METHODS)
    assert list(document)[-2:] == ["meta", "gate"]


def test_top_k_is_not_swept(document: dict[str, Any]) -> None:
    assert document["meta"]["top_k_swept"] is False


def test_meta_records_execution_identity(document: dict[str, Any]) -> None:
    meta = document["meta"]
    assert meta["embedding_model"] == "text-embedding-3-small"
    assert meta["dataset_hash"] == "sha256:deadbeef"
    assert meta["run_id"] == "run-1"
    assert meta["model_configured"] == {"openai": "gpt-4o-mini"}
    assert meta["schema_version"] == 1
    assert meta["weights"]["llm"] == 0.5
    assert meta["weights"]["emb"] == 0.3
    assert meta["weights"]["rule"] == 0.2
    assert "환경변수" in meta["weights"]["source"]


def test_meta_model_comes_from_detail_model(document: dict[str, Any]) -> None:
    """U3 보정표와 같은 출처(`detail["model"]`)를 쓴다."""

    assert document["meta"]["provider"] is None  # 손 입력 행에는 판정 detail 이 없다
    assert document["meta"]["model"] is None
    with_model = build_metrics_document(
        scenario_rows(detail_identity={"provider": "openai", "model": "gpt-4o-mini-2024"})
    )
    assert with_model["meta"]["provider"] == "openai"
    assert with_model["meta"]["model"] == "gpt-4o-mini-2024"
    assert with_model["meta"]["models_observed"] == ["gpt-4o-mini-2024"]
    assert with_model["meta"]["model_configured"] == {}


def test_two_models_leave_singleton_fields_null() -> None:
    rows = scenario_rows(detail_identity={"provider": "openai", "model": "a"})
    for row in rows:
        if row["method"] == "llm_single":
            row["detail"] = {"provider": "gemini", "model": "b"}
    doc = build_metrics_document(rows)
    assert doc["meta"]["model"] is None
    assert doc["meta"]["models_observed"] == ["a", "b"]
    assert doc["meta"]["providers_observed"] == ["gemini", "openai"]


def test_metrics_blocks_are_copied_not_recomputed(document: dict[str, Any]) -> None:
    metrics = compute_metrics(scenario_rows())
    for method in METHODS:
        assert document[method] == metrics["methods"][method]


def test_document_is_reproducible() -> None:
    first = build_metrics_document(scenario_rows(), run_id="r")
    second = build_metrics_document(scenario_rows(), run_id="r")
    assert json.dumps(first, ensure_ascii=False) == json.dumps(second, ensure_ascii=False)


def test_empty_rows_rejected() -> None:
    with pytest.raises(CurveError):
        build_metrics_document([])


# ---------------------------------------------------------------------------
# 게이트 판정식 (결정 K -- 동률 4조합 · 지배 1건 · D10 역방향 1건)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("baseline", "dominates", "label"),
    [
        ((2, 2, 0), False, "동률: fm = , miss = -> 미지배(통과 쪽)"),
        ((2, 1, 0), True, "동률: fm = , miss < -> 지배"),
        ((1, 2, 0), True, "동률: fm < , miss = -> 지배"),
        ((2, 3, 0), False, "동률: fm = , miss > -> 미지배"),
    ],
)
def test_gate_tie_combinations(
    baseline: tuple[int, int, int], dominates: bool, label: str
) -> None:
    gate = gate_of((2, 2, 0), {"exact_raw": baseline})
    assert gate["baselines"]["exact_raw"]["dominates_proposed"] is dominates, label
    assert ("exact_raw" in gate["dominated_by"]) is dominates


def test_gate_dominated_case() -> None:
    """베이스라인이 두 축 모두 더 낮다 -> 지배 -> 미달(P5 착수 금지)."""

    gate = gate_of((3, 3, 1), {"exact_norm": (1, 1, 0)})
    assert gate["dominated_by"] == ["exact_norm"]
    assert gate["pass"] is False
    assert gate["d10_direction"] is True


def test_gate_not_dominated_when_one_axis_worse() -> None:
    gate = gate_of((3, 1, 0), {"exact_raw": (1, 4, 0)})
    assert gate["dominated_by"] == []
    assert gate["pass"] is True


def test_gate_pass_shape_matches_judgement_command() -> None:
    """판정 표 108행: `0.8 [] True True`."""

    gate = gate_of((0, 0, 0), {})
    assert (gate["t_merge"], gate["dominated_by"], gate["d10_direction"], gate["pass"]) == (
        0.8,
        [],
        True,
        True,
    )
    assert gate["reason"] is None


def test_gate_baselines_are_the_four_non_proposed_methods() -> None:
    gate = gate_of((1, 1, 0), {})
    assert sorted(gate["baselines"]) == sorted(set(METHODS) - {PROPOSED})
    assert len(gate["baselines"]) == 4
    assert PROPOSED not in gate["baselines"]


def test_gate_false_merge_ranking_has_five_methods_with_counts() -> None:
    gate = gate_of(
        (2, 0, 0),
        {"exact_raw": (0, 5, 0), "exact_norm": (1, 0, 0), "embedding_only": (3, 0, 0)},
    )
    ranking = gate["false_merge_ranking"]
    assert [entry["method"] for entry in ranking][:3] == [
        "exact_raw",
        "exact_norm",
        "proposed",
    ]
    assert len(ranking) == 5
    assert [entry["rank"] for entry in ranking] == [1, 2, 3, 4, 5]
    for entry in ranking:
        assert set(entry["false_merge_rate"]) == {"n", "d", "rate"}


def test_gate_d10_direction_uses_every_consecutive_pair() -> None:
    """양 끝점만 보면 통과하지만 **중간 격자점이 역전**한다(R-7(1))."""

    spec: dict[str, dict[Any, tuple[int, int, int]]] = {
        PROPOSED: {0.75: (2, 0, 1), 0.8: (3, 0, 0), 0.85: (1, 0, 2)},
    }
    for name in METHODS[1:]:
        spec[name] = {0.75: (1, 1, 0), 0.8: (1, 1, 0), 0.85: (1, 1, 0)}
    gate = build_gate(make_metrics(spec))
    assert gate["d10_direction"] is False
    assert gate["pass"] is False
    axes = {violation["axis"] for violation in gate["d10_detail"]["violations"]}
    assert axes == {"false_merge_rate", "ask_user_identity_rate"}
    assert gate["d10_detail"]["pairs"] == 2


def test_gate_d10_direction_monotone_curve_passes() -> None:
    spec: dict[str, dict[Any, tuple[int, int, int]]] = {
        PROPOSED: {0.75: (2, 0, 0), 0.8: (1, 0, 1), 0.85: (0, 1, 2)},
    }
    for name in METHODS[1:]:
        spec[name] = {0.75: (2, 2, 0), 0.8: (2, 2, 0), 0.85: (2, 2, 0)}
    gate = build_gate(make_metrics(spec))
    assert gate["d10_direction"] is True
    assert gate["d10_detail"]["violations"] == []
    assert gate["pass"] is True


def test_gate_rejects_null_rate_instead_of_passing_silently() -> None:
    spec: dict[str, dict[Any, tuple[int, int, int]]] = {PROPOSED: {0.8: (0, 0, 0)}}
    for name in METHODS[1:]:
        spec[name] = {0.8: (0, 0, 0)}
    metrics = make_metrics(spec)
    point = metrics["methods"][PROPOSED]["by_t_merge"]["0.8"]
    point["miss_rate"] = ratio(0, 0)  # 분모 0 -> rate: null
    assert point["miss_rate"]["rate"] is None
    gate = build_gate(metrics)
    assert gate["pass"] is False
    assert "null" in gate["reason"]
    assert gate["undetermined"] == list(METHODS[1:])
    assert gate["dominated_by"] == []


def test_gate_requires_a_point_at_08() -> None:
    spec: dict[str, dict[Any, tuple[int, int, int]]] = {
        name: {0.75: (1, 1, 0), 0.85: (1, 1, 0)} for name in METHODS
    }
    with pytest.raises(CurveError, match="0.8"):
        build_gate(make_metrics(spec))


def test_gate_lookup_folds_float_noise() -> None:
    noisy = 0.1 + 0.7  # 0.7999999999999999
    assert noisy != 0.8
    spec: dict[str, dict[Any, tuple[int, int, int]]] = {name: {noisy: (1, 1, 0)} for name in METHODS}
    gate = build_gate(make_metrics(spec))
    assert gate["t_merge"] == 0.8
    assert GATE_T_MERGE == "0.8"


def test_gate_on_full_document(document: dict[str, Any]) -> None:
    gate = document["gate"]
    assert gate["t_merge"] == 0.8
    # proposed 는 0.8 에서 오병합 0 -> 어떤 베이스라인도 두 축 모두 <= 일 수 없다
    assert gate["proposed"]["false_merge_rate"] == {"n": 0, "d": 3, "rate": 0.0}
    assert gate["proposed"]["miss_rate"] == {"n": 0, "d": 3, "rate": 0.0}
    assert gate["dominated_by"] == []
    assert gate["d10_direction"] is True
    assert gate["pass"] is True
    assert gate["d10_detail"]["pairs"] == 9


# ---------------------------------------------------------------------------
# curve.csv
# ---------------------------------------------------------------------------


def test_curve_rows_count_and_order(document: dict[str, Any]) -> None:
    rows = curve_rows(document)
    assert len(rows) == 5 * 10 * 3
    assert [row["method"] for row in rows[:3]] == [PROPOSED] * 3
    assert [row["series"] for row in rows[:3]] == list(SERIES)
    assert rows[0]["t_merge"] == 0.5
    assert sorted({row["t_merge"] for row in rows}) == list(EXPECTED_GRID)
    assert {row["t_new"] for row in rows} == {0.3}
    assert [row["method"] for row in rows][::30] == list(METHODS)


def test_curve_series_are_the_three_y_axes(document: dict[str, Any]) -> None:
    rows = curve_rows(document)
    assert {row["series"] for row in rows} == set(SERIES)
    identity = [
        row
        for row in rows
        if row["method"] == PROPOSED and row["series"] == "ask_user_identity_rate"
    ]
    point = document[PROPOSED]["by_t_merge"]["0.8"]
    at_08 = next(row for row in identity if row["t_merge"] == 0.8)
    assert (at_08["n"], at_08["d"], at_08["rate"]) == (
        point["ask_user_rate_by_kind"]["identity"]["n"],
        point["ask_user_rate_by_kind"]["identity"]["d"],
        point["ask_user_rate_by_kind"]["identity"]["rate"],
    )


def test_curve_csv_columns_and_row_count(tmp_path, document: dict[str, Any]) -> None:
    import csv

    path = tmp_path / "curve.csv"
    written = write_curve_csv(path, curve_rows(document))
    assert written == 150
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(CURVE_COLUMNS)
        data = list(reader)
    assert len(data) == 150
    # 01-plan 판정 표 104행의 명령과 같은 읽기
    assert sorted({float(row["t_merge"]) for row in data}) == list(EXPECTED_GRID)
    assert {row["t_new"] for row in data} == {"0.3"}
    assert len({row["method"] for row in data}) == 5


def test_curve_csv_is_byte_identical_on_rerun(tmp_path, document: dict[str, Any]) -> None:
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    write_curve_csv(first, curve_rows(document))
    write_curve_csv(second, curve_rows(document))
    assert first.read_bytes() == second.read_bytes()


def test_curve_csv_leaves_null_rate_empty(tmp_path) -> None:
    rows = [{"method": "proposed", "t_merge": 0.8, "t_new": 0.3, "series": SERIES[0], "n": 0, "d": 0, "rate": None}]
    path = tmp_path / "curve.csv"
    write_curve_csv(path, rows)
    line = path.read_text(encoding="utf-8").splitlines()[1]
    assert line == "proposed,0.8,0.3,false_merge_rate,0,0,"


def test_curve_rows_accept_both_shapes(document: dict[str, Any]) -> None:
    metrics = compute_metrics(scenario_rows())
    assert curve_rows(metrics) == curve_rows(document)


# ---------------------------------------------------------------------------
# forced_reason 별도 집계 (P3-er §7)
# ---------------------------------------------------------------------------


def test_forced_reason_is_aggregated_outside_the_curve_series() -> None:
    rows = scenario_rows(forced_at="embedding_only")
    document = build_metrics_document(rows)
    forced = document["meta"]["forced_reason"]
    assert forced["embedding_only"]["0.8"]["counts"] == {"no_candidates": 3}
    assert forced["embedding_only"]["0.8"]["rate"] == {"n": 3, "d": 3, "rate": 1.0}
    assert forced[PROPOSED]["0.8"]["counts"] == {}
    assert forced[PROPOSED]["0.8"]["rate"]["n"] == 0
    # 곡선 계열에는 강제 경로가 섞이지 않는다
    assert {row["series"] for row in curve_rows(document)} == set(SERIES)


def test_forced_reason_summary_drops_the_none_bucket() -> None:
    metrics = compute_metrics(scenario_rows(forced_at=PROPOSED))
    summary = forced_reason_summary(metrics)
    assert "none" not in summary[PROPOSED]["0.5"]["counts"]
    assert summary[PROPOSED]["0.5"]["counts"] == {"no_candidates": 3}
    assert list(summary) == list(METHODS)


# ---------------------------------------------------------------------------
# --validate (판정 표 99행)
# ---------------------------------------------------------------------------


def test_validate_accepts_a_built_document(document: dict[str, Any]) -> None:
    assert validate_metrics_document(document) == []


def test_validate_cli_returns_zero(tmp_path, capsys, document: dict[str, Any]) -> None:
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    assert metrics_main(["--validate", str(path)]) == 0
    assert "OK" in capsys.readouterr().out


def test_validate_cli_returns_nonzero_and_prints_reasons(
    tmp_path, capsys, document: dict[str, Any]
) -> None:
    broken = dict(document)
    broken["meta"] = {**document["meta"], "t_new": 0.4}
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(broken, ensure_ascii=False), encoding="utf-8")
    rc = metrics_main(["--validate", str(path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "FAIL" in out
    assert "meta.t_new" in out


def test_curve_cli_gzip_rows_give_identical_bytes(tmp_path) -> None:
    """커밋본 `.jsonl.gz` 로 만든 `metrics.json`·`curve.csv` 가 평문과 바이트
    동일(사용자 결정 2026-09-21 -- 원시 JSONL 은 gzip 으로 커밋한다)."""

    import gzip

    from evaluation.curve import main as curve_main

    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in scenario_rows()) + "\n"
    plain = tmp_path / "raw.jsonl"
    plain.write_text(text, encoding="utf-8")
    packed = tmp_path / "raw.jsonl.gz"
    with gzip.open(packed, "wt", encoding="utf-8", newline="") as handle:
        handle.write(text)

    made: dict[str, tuple[bytes, bytes]] = {}
    for label, rows_path in (("plain", plain), ("gz", packed)):
        out = tmp_path / f"metrics-{label}.json"
        curve = tmp_path / f"curve-{label}.csv"
        assert (
            curve_main(
                ["--rows", str(rows_path), "--out", str(out), "--curve", str(curve), "--run-id", "r"]
            )
            == 0
        )
        made[label] = (out.read_bytes(), curve.read_bytes())
    assert made["gz"] == made["plain"]


def test_validate_cli_rejects_rows_and_validate_together(tmp_path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        metrics_main(["--validate", str(tmp_path / "m.json"), "--rows", str(tmp_path / "r.jsonl")])
    assert excinfo.value.code == 2


def test_metrics_cli_requires_rows_or_validate() -> None:
    with pytest.raises(SystemExit) as excinfo:
        metrics_main([])
    assert excinfo.value.code == 2


def test_validate_rejects_non_object() -> None:
    assert validate_metrics_document([1, 2]) == [
        "document: object expected (got list)"
    ]


def test_validate_rejects_four_method_keys(document: dict[str, Any]) -> None:
    broken = {key: value for key, value in document.items() if key != "llm_single"}
    broken["meta"] = {**document["meta"], "methods": list(METHODS[:4])}
    problems = validate_metrics_document(broken)
    assert any("expected 5 method keys" in p for p in problems)


def test_validate_rejects_wrong_method_order(document: dict[str, Any]) -> None:
    reordered = {"exact_raw": document["exact_raw"]}
    for key, value in document.items():
        if key != "exact_raw":
            reordered[key] = value
    problems = validate_metrics_document(reordered)
    assert any("method key order" in p for p in problems)


def test_validate_rejects_missing_denominator_rule(document: dict[str, Any]) -> None:
    broken = dict(document)
    meta = {key: value for key, value in document["meta"].items() if key != "denominator_rule"}
    broken["meta"] = meta
    problems = validate_metrics_document(broken)
    assert any("denominator_rule" in p for p in problems)


def test_validate_rejects_nine_point_grid(document: dict[str, Any]) -> None:
    broken = dict(document)
    broken["meta"] = {**document["meta"], "grid": list(EXPECTED_GRID)[:9]}
    problems = validate_metrics_document(broken)
    assert any("meta.grid" in p for p in problems)


def test_validate_rejects_top_k_swept(document: dict[str, Any]) -> None:
    broken = dict(document)
    broken["meta"] = {**document["meta"], "top_k_swept": True}
    assert any("top_k_swept" in p for p in validate_metrics_document(broken))


def test_validate_rejects_missing_gate_keys(document: dict[str, Any]) -> None:
    broken = dict(document)
    broken["gate"] = {key: value for key, value in document["gate"].items() if key != "pass"}
    problems = validate_metrics_document(broken)
    assert any("missing key(s)" in p and "pass" in p for p in problems)


def test_validate_rejects_three_baselines(document: dict[str, Any]) -> None:
    gate = json.loads(json.dumps(document["gate"]))
    gate["baselines"].pop("llm_single")
    broken = {**document, "gate": gate}
    problems = validate_metrics_document(broken)
    assert any("gate.baselines" in p for p in problems)


def test_validate_rejects_broken_ratio_shape(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc[PROPOSED]["by_t_merge"]["0.8"]["false_merge_rate"] = {"rate": 0.5}
    problems = validate_metrics_document(doc)
    assert any("n·d·rate" in p for p in problems)


def test_validate_rejects_rate_that_is_not_n_over_d(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc["gate"]["proposed"]["miss_rate"] = {"n": 1, "d": 4, "rate": 0.9}
    assert any("!= n/d" in p for p in validate_metrics_document(doc))


def test_validate_rejects_zero_denominator_with_a_rate(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc["gate"]["proposed"]["miss_rate"] = {"n": 0, "d": 0, "rate": 0.0}
    assert any("d=0 must give null" in p for p in validate_metrics_document(doc))


def test_validate_rejects_inconsistent_pass(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc["gate"]["dominated_by"] = ["exact_raw"]
    problems = validate_metrics_document(doc)
    assert any("gate.pass" in p for p in problems)


def test_validate_rejects_pass_false_without_reason(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc["gate"]["pass"] = False
    problems = validate_metrics_document(doc)
    assert any("gate.pass" in p for p in problems)


def test_validate_rejects_unknown_dominated_by(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc["gate"]["dominated_by"] = ["proposed"]
    doc["gate"]["pass"] = False
    doc["gate"]["reason"] = "손 입력"
    problems = validate_metrics_document(doc)
    assert any("unknown baseline" in p for p in problems)


def test_validate_rejects_point_t_new_drift(document: dict[str, Any]) -> None:
    doc = json.loads(json.dumps(document))
    doc[PROPOSED]["by_t_merge"]["0.8"]["t_new"] = 0.4
    assert any("t_new" in p for p in validate_metrics_document(doc))
