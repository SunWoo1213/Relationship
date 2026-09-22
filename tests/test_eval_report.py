"""Refs: P4-pilot-eval S3.7 원칙8 -- 리포트 생성기(U5) 계약 테스트.

**네트워크·DB·LLM·시계 없음**(순수). 입력은 손으로 만든 소형 JSONL 행을
U4 `build_metrics_document()` 에 넣어 만든 고정 `metrics.json` 문서 하나다.

01-plan 69행이 요구하는 두 가지를 전수로 본다.

1. **두 번 생성하면 바이트가 같다** -- 날짜·시각·환경변수·순회 순서가 본문에
   새면 이 단언이 먼저 깨진다(판정 표 102행 `eval.md` 재생성 diff 0줄).
2. **입력에 없는 수치를 본문에 쓰지 않는다** -- 본문에서 인용 태그(`원칙8`·
   `S3.7`·`D10`·`R-5`·`02-plan-verify` 같은 것)를 걷어낸 뒤 남는 **모든 숫자
   토큰**이, 입력 문서의 수(세 가지 표시 형식)와 입력 문서의 문자열 안 숫자로
   이루어진 집합에 들어 있어야 한다. 템플릿이 키를 참조하지 않고 숫자를
   지어내면(예: 하드코딩한 표본 수·임계치) 이 단언이 깨진다. 값 민감도(픽스처
   값을 바꾸면 본문의 그 자리가 바뀐다)를 짝으로 단언해 "우연히 집합 안에 있는
   상수"가 통과하지 못하게 한다.

그 밖에: 검증 실패 입력은 rc≠0 이고 출력 파일을 만들지 않는다 · `rate: null`
은 `측정 불가(분모 0)` 로 적는다 · `meta.provider` 가 null 이면
`providers_observed` 관측 목록으로 대체 표기한다 · 필수 절(게이트·O-5
순위표·곡선 3계열 × 5방식 × 10점·한계·"방향" 단서)·`curve.csv` 링크 ·
날짜/시각 문자열 없음 · 환경변수를 바꿔도 출력이 같다.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

import pytest

from evaluation.curve import (
    GATE_T_MERGE,
    SERIES,
    T_NEW,
    build_metrics_document,
    validate_metrics_document,
)
from evaluation.report import (
    CURVE_LINK,
    MISSING,
    NULL_RATE,
    ReportError,
    fmt_number,
    fmt_rate_value,
    fmt_ratio,
    fmt_score,
    optimum_candidate,
    render_report,
)
from evaluation.report import main as report_main

METHODS = ("proposed", "exact_raw", "exact_norm", "embedding_only", "llm_single")
GRID = [round(0.5 + 0.05 * i, 2) for i in range(10)]
SCENARIOS = (("sc-001", "promotion"), ("sc-002", "alias"))

#: (mention_index, gold_person_id, gold_db_person_id, mention_kind, ambiguous, allowed)
MENTIONS: tuple[tuple[int, str | None, int | None, str, bool, list[str]], ...] = (
    (0, "p1", 1, "gold", False, ["none"]),
    (1, "p2", 2, "gold", False, ["none", "identity"]),
    (2, "p3", 3, "gold", False, ["none", "identity"]),
    (3, "p9", None, "gold", False, ["new_person"]),
    (4, "p4", 4, "gold", False, ["identity"]),
    (5, "p5", 5, "gold", False, ["none"]),
    (6, None, None, "gold", True, ["identity"]),
    (7, None, None, "passing", False, ["new_person"]),
)


def decide(method: str, t: float, index: int) -> tuple[str, int | None]:
    """방식 × 임계치 × mention -> (decision, person_id).

    - mention 0: 언제나 정답 병합
    - mention 1: `proposed` 는 `T_merge < 0.75` 에서 다른 사람으로 병합(오병합),
      그 위로는 `identity` 로 미룬다 -> 오병합률 비증가·identity 비감소(D10).
      `exact_raw` 는 오병합, `embedding_only` 는 정답 병합, 나머지는 보류.
    - mention 2: 전 방식 `new_person` -> 미검출
    - mention 3: 골드가 DB 밖 -> `new_person` 정답
    - mention 4: 전 방식 `identity` -> 제3 범주
    - mention 5: 세 방식만 정답 병합
    - mention 6: `ambiguous` (분모에서 빠진다)
    - mention 7: `passing` (골드 분모 밖, `new_person` 은 오탐 분자)
    """

    if index == 0:
        return "merge", 1
    if index == 1:
        if method == "proposed":
            return ("merge", 1) if t < 0.75 else ("identity", None)
        if method == "exact_raw":
            return "merge", 1
        if method == "embedding_only":
            return "merge", 2
        return "identity", None
    if index == 2:
        return "new_person", None
    if index == 3:
        return "new_person", None
    if index == 4:
        return "identity", None
    if index == 5:
        if method in {"proposed", "exact_norm", "embedding_only"}:
            return "merge", 5
        return "identity", None
    if index == 6:
        return "identity", None
    return "new_person", None


def _detail(method: str, index: int, *, models: dict[str, tuple[str, str]]) -> dict[str, Any]:
    detail: dict[str, Any] = {}
    if method in models:
        provider, model = models[method]
        detail["provider"] = provider
        detail["model"] = model
    if method == "proposed":
        if index == 2:
            detail["forced_reason"] = "no_candidates"
        if index == 5:
            detail["relaxed_retry"] = True
    if method == "llm_single" and index == 2:
        detail["llm_error"] = "timeout"
    if method == "embedding_only":
        detail["hints"] = {} if index == 0 else {"hierarchy": "상"}
    return detail


def _candidates(method: str, index: int, person_id: int | None) -> list[dict[str, Any]]:
    if method != "proposed" or person_id is None:
        return []
    rule_checked = 0.0 if index == 5 else 1.0
    return [
        {
            "person_id": person_id,
            "signals": {"rule_checked": rule_checked, "s_emb": 0.72, "s_llm": 0.91},
        }
    ]


def make_rows(*, models: dict[str, tuple[str, str]] | None = None) -> list[dict[str, Any]]:
    """다섯 방식 × 격자 10점 × 시나리오 2 × mention 8 = 800 행."""

    models = models or {
        "proposed": ("openai", "gpt-4o-mini"),
        "llm_single": ("openai", "gpt-4o-mini"),
    }
    rows: list[dict[str, Any]] = []
    for method in METHODS:
        for t in GRID:
            fresh = t == GRID[0] and method in models
            for scenario_id, category in SCENARIOS:
                for index, gold_id, gold_db, kind, ambiguous, allowed in MENTIONS:
                    decision, person_id = decide(method, t, index)
                    rows.append(
                        {
                            "method": method,
                            "mention": f"지칭-{index}",
                            "decision": decision,
                            "person_id": person_id,
                            "score": 0.81,
                            "candidates": _candidates(method, index, person_id),
                            "trace_id": None,
                            "tokens_in": 120 if fresh else 0,
                            "tokens_out": 45 if fresh else 0,
                            "detail": _detail(method, index, models=models),
                            "scenario_id": scenario_id,
                            "category": category,
                            "mention_kind": kind,
                            "mention_index": index,
                            "turn": index,
                            "gold_person_id": gold_id,
                            "gold_db_person_id": gold_db,
                            "ambiguous": ambiguous,
                            "expected_ask_user_allowed": list(allowed),
                            "trap_kind": None,
                            "t_merge": t,
                            "t_new": T_NEW,
                            "sweep_index": GRID.index(round(t, 2)),
                            "llm_fresh_call": fresh,
                        }
                    )
    return rows


def make_document(**kwargs: Any) -> dict[str, Any]:
    return build_metrics_document(
        make_rows(**kwargs),
        embedding_model="text-embedding-3-small",
        dataset_hash="sha256:c0ffee",
        run_id="pilot-fixture",
        model_configured={"openai": "gpt-4o-mini"},
    )


@pytest.fixture()
def document() -> dict[str, Any]:
    return make_document()


@pytest.fixture()
def body(document: dict[str, Any]) -> str:
    return render_report(document)


def write_metrics(tmp_path: Path, doc: dict[str, Any], name: str = "metrics.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# 0) 픽스처 자체가 U4 계약을 지키는가 (깨진 입력으로 U5 를 시험하지 않는다)
# ---------------------------------------------------------------------------


def test_fixture_document_passes_u4_validation(document: dict[str, Any]) -> None:
    assert validate_metrics_document(document) == []
    assert document["gate"]["pass"] is True
    assert document["gate"]["dominated_by"] == []


# ---------------------------------------------------------------------------
# 1) 두 번 생성하면 바이트가 같다 (01-plan 69행 · 판정 표 102행)
# ---------------------------------------------------------------------------


def test_cli_output_is_byte_identical_on_rerun(tmp_path: Path, document: dict[str, Any]) -> None:
    metrics = write_metrics(tmp_path, document)
    first = tmp_path / "eval-1.md"
    second = tmp_path / "eval-2.md"
    assert report_main(["--metrics", str(metrics), "--out", str(first)]) == 0
    assert report_main(["--metrics", str(metrics), "--out", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes() == render_report(document).encode("utf-8")


def test_output_uses_lf_only(tmp_path: Path, document: dict[str, Any]) -> None:
    metrics = write_metrics(tmp_path, document)
    out = tmp_path / "eval.md"
    assert report_main(["--metrics", str(metrics), "--out", str(out)]) == 0
    raw = out.read_bytes()
    assert b"\r\n" not in raw
    assert raw.endswith(b"\n")


def test_environment_does_not_change_the_body(
    monkeypatch: pytest.MonkeyPatch, document: dict[str, Any], body: str
) -> None:
    for name in ("LLM_PROVIDER", "OPENAI_MODEL", "POSTGRES_PORT", "TZ", "W_LLM"):
        monkeypatch.setenv(name, "changed-by-test")
    assert render_report(document) == body


def test_body_has_no_date_or_clock_strings(body: str) -> None:
    assert re.search(r"\d{4}-\d{2}-\d{2}", body) is None
    assert re.search(r"\d{1,2}:\d{2}", body) is None
    for word in ("2026", "오늘", "생성 시각", "generated at"):
        assert word not in body


# ---------------------------------------------------------------------------
# 2) 입력에 없는 수치를 본문에 쓰지 않는다 (템플릿이 참조하지 않는 키 감시)
# ---------------------------------------------------------------------------

#: 본문에 남는 인용 태그. 숫자 토큰 검사에서 먼저 걷어낸다(이 문자열들의
#: 숫자는 수치가 아니라 카드 번호다).
CITATION_RE = re.compile(
    r"원칙\d+|S3\.\d+|§\d+|\d+-plan-verify|\d+-plan|CR-\d+|FIX-\d+|L-\d+|"
    r"[RODHU]-?\d+(?=[^\d]|$)|P\d+(?:-[A-Za-z][A-Za-z-]*)?"
)

NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


def _numbers_of(value: Any, out: set[str]) -> None:
    """입력 문서에서 **본문에 나타날 수 있는 숫자 토큰**을 모은다.

    수는 리포트가 쓰는 세 가지 표시 형식(`fmt_number`·`fmt_rate_value`·
    `fmt_score`)으로 펼치고, 문자열 값(규칙 문장·모델명·해시)은 그 안의 숫자를
    그대로 모은다 -- 리포트가 그 문자열을 인용하기 때문이다.
    """

    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        for text in (fmt_number(value), fmt_rate_value(value), fmt_score(value)):
            out.update(NUMBER_RE.findall(text))
        return
    if isinstance(value, str):
        out.update(NUMBER_RE.findall(value))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            out.update(NUMBER_RE.findall(str(key)))
            _numbers_of(item, out)
        return
    if isinstance(value, list):
        for item in value:
            _numbers_of(item, out)


def test_every_number_in_the_body_comes_from_the_metrics_document(
    document: dict[str, Any], body: str
) -> None:
    allowed: set[str] = set()
    _numbers_of(document, allowed)

    stripped = CITATION_RE.sub(" ", body)
    used = set(NUMBER_RE.findall(stripped))
    invented = sorted(used - allowed)
    assert invented == [], f"metrics.json 에 없는 수치가 본문에 있다: {invented}"


@pytest.mark.parametrize(
    "invented",
    ["F1 0.87", "오병합률 3.2%", "표본 40건", "임계치 0.62 를 권장한다", "약 1200 토큰"],
)
def test_the_number_guard_itself_catches_invented_numbers(
    document: dict[str, Any], body: str, invented: str
) -> None:
    """위 단언이 살아 있는지 본다 -- 지어낸 수치(기획서 부록 A 의 예시 수치나
    하드코딩한 임계치·표본 수)를 한 줄 넣으면 걸려야 한다.

    한계: 입력 문서에 이미 있는 토큰(한 자리 수 대부분)은 이 검사로 잡히지
    않는다. 그래서 값 민감도 단언(`test_changing_an_input_value_changes_the_body`)
    을 짝으로 둔다.
    """

    allowed: set[str] = set()
    _numbers_of(document, allowed)
    used = set(NUMBER_RE.findall(CITATION_RE.sub(" ", body + "\n" + invented)))
    assert used - allowed, invented


@pytest.mark.parametrize(
    ("path", "value", "expected_token"),
    [
        (("proposed", "by_t_merge", GATE_T_MERGE, "miss_rate"), {"n": 5, "d": 12, "rate": 5 / 12}, "41.7%"),
        (("exact_raw", "by_t_merge", "0.5", "false_merge_rate"), {"n": 7, "d": 12, "rate": 7 / 12}, "58.3%"),
        (("meta", "scenario_count"), 137, "137"),
        (("meta", "run_id"), "run-xyz-9", "run-xyz-9"),
        (("meta", "embedding_model"), "embed-test-7", "embed-test-7"),
    ],
)
def test_changing_an_input_value_changes_the_body(
    document: dict[str, Any], body: str, path: tuple[str, ...], value: Any, expected_token: str
) -> None:
    """값을 바꾸면 본문의 그 자리가 바뀐다 -- 템플릿이 그 키를 실제로 참조한다."""

    mutated = copy.deepcopy(document)
    target: Any = mutated
    for key in path[:-1]:
        target = target[key]
    old = target[path[-1]]
    target[path[-1]] = value
    assert validate_metrics_document(mutated) == []

    changed = render_report(mutated)
    assert changed != body
    assert expected_token in changed
    if isinstance(old, dict):
        assert fmt_ratio(old) not in changed or fmt_ratio(old) != fmt_ratio(value)


def test_gate_verdict_follows_the_document_not_the_generator(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["gate"]["dominated_by"] = ["exact_raw"]
    mutated["gate"]["pass"] = False
    assert validate_metrics_document(mutated) == []

    changed = render_report(mutated)
    assert "**미달**" in changed
    assert "**통과**" not in changed
    assert "**통과**" in render_report(document)


# ---------------------------------------------------------------------------
# 3) 깨진 입력으로 리포트를 만들지 않는다
# ---------------------------------------------------------------------------


def test_invalid_document_returns_nonzero_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], document: dict[str, Any]
) -> None:
    broken = copy.deepcopy(document)
    broken["meta"]["t_new"] = 0.4
    metrics = write_metrics(tmp_path, broken, "broken.json")
    out = tmp_path / "eval.md"

    assert report_main(["--metrics", str(metrics), "--out", str(out)]) != 0
    assert not out.exists()
    printed = capsys.readouterr().out
    assert "FAIL" in printed
    assert "t_new" in printed


def test_render_report_raises_on_invalid_document(document: dict[str, Any]) -> None:
    broken = copy.deepcopy(document)
    del broken["gate"]
    with pytest.raises(ReportError):
        render_report(broken)


def test_missing_file_returns_nonzero(tmp_path: Path) -> None:
    assert report_main(["--metrics", str(tmp_path / "nope.json")]) != 0


def test_writes_to_stdout_without_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], document: dict[str, Any], body: str
) -> None:
    metrics = write_metrics(tmp_path, document)
    assert report_main(["--metrics", str(metrics)]) == 0
    assert capsys.readouterr().out.replace("\r\n", "\n") == body


# ---------------------------------------------------------------------------
# 4) 표기 규칙 (null 비율 · 공급자 null · 분자/분모)
# ---------------------------------------------------------------------------


def test_null_rate_is_written_as_not_measurable(body: str) -> None:
    assert NULL_RATE in body
    assert f"0/0 ({NULL_RATE})" in body
    # 분모 0 을 0% 로 적지 않는다.
    assert "0/0 (0.0%)" not in body


def test_rates_are_always_written_with_numerator_and_denominator(body: str) -> None:
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        for cell in line.split("|"):
            if "%" in cell:
                assert re.search(r"\d+/\d+ \(\d+\.\d%\)", cell), cell


def test_provider_null_falls_back_to_observed_lists(tmp_path: Path) -> None:
    mixed = make_document(
        models={
            "proposed": ("openai", "gpt-4o-mini"),
            "llm_single": ("gemini", "gemini-2.5-flash"),
        }
    )
    assert mixed["meta"]["provider"] is None
    assert mixed["meta"]["model"] is None

    text = render_report(mixed)
    assert "단일 값 없음" in text
    assert "providers_observed" in text
    for name in ("openai", "gemini", "gpt-4o-mini", "gemini-2.5-flash"):
        assert name in text


def test_missing_optional_meta_key_is_not_invented(document: dict[str, Any], body: str) -> None:
    assert "meta.commit" in body
    assert MISSING in body


def test_meta_section_prints_the_two_policy_rows(
    document: dict[str, Any], body: str
) -> None:
    """결정 H(i) -- `meta.weights` 는 설정값(비율)이라 그것만으로는 어느
    산식으로 결합했는지 알 수 없다. 두 정책을 메타 표에 함께 찍는다."""

    assert "meta.weights_policy" in body
    assert document["meta"]["weights_policy"] in body
    assert "meta.penalized_merge_policy" in body
    assert f"`{document['meta']['penalized_merge_policy']}`" in body


def test_old_schema_metrics_is_rejected_with_the_missing_policy_keys(
    document: dict[str, Any],
) -> None:
    """옛 판(`schema_version` 1 = P4 기준선) `metrics.json` 으로는 리포트를
    만들지 않는다 -- 어느 산식으로 결합했는지 모르는 채 수치를 다시 찍으면
    재현성 주장이 거짓이 된다(원칙8). 무엇이 없는지 이름으로 말한다."""

    old = json.loads(json.dumps(document))
    old["meta"].pop("weights_policy")
    old["meta"].pop("penalized_merge_policy")
    with pytest.raises(ReportError) as excinfo:
        render_report(old)
    assert "weights_policy" in str(excinfo.value)
    assert "penalized_merge_policy" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 5) 필수 절
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "heading",
    [
        "## 실행 메타",
        "## 방식 × 지표",
        "## 게이트 (결정 K — 지배 기준)",
        "## 트레이드오프 곡선",
        "## 운영 최적점",
        "## 한계와 읽는 법",
    ],
)
def test_required_sections_exist(body: str, heading: str) -> None:
    assert any(line.startswith(heading) for line in body.splitlines()), heading


def test_gate_section_carries_the_decision_k_fields(document: dict[str, Any], body: str) -> None:
    gate = document["gate"]
    assert gate["rule"] in body.replace("\\|", "|")
    assert gate["d10_rule"] in body.replace("\\|", "|")
    for key in ("gate.dominated_by", "gate.d10_direction", "gate.pass", "gate.reason"):
        assert key in body


def test_false_merge_ranking_sits_next_to_the_gate(document: dict[str, Any], body: str) -> None:
    """O-5: 순위표가 게이트 결과와 같은 절에, 곡선 절보다 앞에 온다."""

    gate_at = body.index("## 게이트")
    ranking_at = body.index("### 오병합률 순위")
    curve_at = body.index("## 트레이드오프 곡선")
    assert gate_at < ranking_at < curve_at

    ranking = document["gate"]["false_merge_ranking"]
    assert len(ranking) == len(METHODS)
    for entry in ranking:
        assert fmt_ratio(entry["false_merge_rate"]) in body


def test_method_table_has_the_required_columns(body: str) -> None:
    header = next(
        line for line in body.splitlines() if line.startswith("| 방식 | 채점 행 |")
    )
    for column in (
        "오병합률",
        "미검출률",
        "제3 범주(identity 보류)",
        "precision",
        "recall",
        "f1",
        "ask_user(identity)",
        "ask_user(new_person)",
        "ask_user(schedule)",
    ):
        assert column in header


def test_curve_tables_are_three_series_by_five_methods_by_ten_points(body: str) -> None:
    section = body[body.index("## 트레이드오프 곡선") : body.index("## 강제 경로")]
    tables = [
        block
        for block in section.split("\n\n")
        if block.startswith("| 방식 \\ `T_merge`")
    ]
    assert len(tables) == len(SERIES)
    for table in tables:
        lines = table.splitlines()
        assert len(lines) == 2 + len(METHODS)  # 머리글 + 구분선 + 방식 5
        assert len(lines[0].split("|")) == 2 + 1 + len(GRID)  # 방식 열 + 격자 10
        for grid_value in GRID:
            assert f"| {grid_value:g} " in lines[0]


def test_curve_csv_link_is_present_once_per_reference(body: str) -> None:
    assert f"[`{CURVE_LINK}`]({CURVE_LINK})" in body
    assert ".png" not in body


def test_limits_section_carries_r5_and_denominator_rule(
    document: dict[str, Any], body: str
) -> None:
    limits = body[body.index("## 한계와 읽는 법") :]
    assert "`exact_*`·`llm_single` 곡선은 임계치를 읽지 않아 평탄한 것이 정상" in limits
    assert "결정 L" in limits
    for key, sentence in document["meta"]["denominator_rule"].items():
        assert f"`{key}`" in limits
        assert sentence.replace("\n", " ") in limits.replace("\\|", "|")


def test_optimum_paragraph_is_a_direction_not_a_final_value(
    document: dict[str, Any], body: str
) -> None:
    section = body[body.index("## 운영 최적점") : body.index("## 한계와 읽는 법")]
    assert "확정값이 아니다" in section
    assert "방향(direction)" in section
    assert fmt_number(document["meta"]["scenario_count"]) + "건" in section
    assert "P10" in section


def test_optimum_candidate_picks_lowest_threshold_among_minimal_false_merge(
    document: dict[str, Any]
) -> None:
    candidate = optimum_candidate(document)
    points = document["proposed"]["by_t_merge"]
    best = min(
        point["false_merge_rate"]["rate"]
        for point in points.values()
        if point["false_merge_rate"]["rate"] is not None
    )
    assert points[candidate["t_merge"]]["false_merge_rate"]["rate"] == best
    lower = [
        key
        for key in points
        if float(key) < float(candidate["t_merge"])
        and points[key]["false_merge_rate"]["rate"] == best
    ]
    assert lower == []


def test_optimum_candidate_declines_when_every_rate_is_null(
    document: dict[str, Any]
) -> None:
    mutated = copy.deepcopy(document)
    for point in mutated["proposed"]["by_t_merge"].values():
        point["false_merge_rate"] = {"n": 0, "d": 0, "rate": None}
    assert optimum_candidate(mutated)["t_merge"] is None


def test_diagnostics_section_reports_forced_reason_and_llm_error(
    document: dict[str, Any], body: str
) -> None:
    assert "`no_candidates`" in body  # proposed 강제 경로
    assert "`timeout`" in body  # llm_single 공급자 오류
    assert "excluding_llm_error" in body
    assert "by_category" not in body or "## 카테고리별" in body
    for category in ("promotion", "alias"):
        assert f"`{category}`" in body


def test_report_module_reads_nothing_but_the_metrics_file() -> None:
    """입력은 `metrics.json` 하나뿐 -- 시계·환경변수·네트워크·DB 를 만지는
    이름이 모듈 어디에도 없다(01-plan 69행)."""

    source = Path(__import__("evaluation.report", fromlist=["__file__"]).__file__)
    text = source.read_text(encoding="utf-8")
    for forbidden in (
        "datetime",
        "os.environ",
        "getenv",
        "time.time",
        "requests",
        "httpx",
        "sqlalchemy",
        "random",
    ):
        assert forbidden not in text, forbidden
