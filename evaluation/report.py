"""Refs: P4-pilot-eval S3.7 원칙8 -- `metrics.json` -> `reports/eval.md` 리포트 생성기.

01-plan U5(69행). **입력은 `metrics.json` 하나뿐이다** -- 원시 JSONL·DB·
네트워크·환경변수·시계를 읽지 않는다. 그래서 같은 파일을 두 번 넣으면
바이트가 같은 `eval.md` 가 나오고(판정 표 102행 "재생성 diff 0줄"),
`metrics.json` 만 보관하면 리포트를 언제든 다시 만들 수 있다(원칙8 ·
eval-harness §5 "metrics.json 만으로 리포트 재생성").

## 본문의 수치는 전부 입력에서 온다

이 모듈은 지표를 **계산하지 않는다**. 세거나 나누는 곳이 없고, 표의 칸은
`metrics.json` 의 `{"n","d","rate"}` 블록을 옮겨 적은 것이다(두 곳에서 세면
두 수치가 생긴다 -- U2·U4 와 같은 자세). 유일한 파생은 표시 형식이다:

| 입력 | 본문 |
|------|------|
| `{"n": 2, "d": 57, "rate": 0.035…}` | `2/57 (3.5%)` |
| `{"n": 0, "d": 0, "rate": null}` | `0/0 (측정 불가(분모 0))` |
| `f1: 0.842…` | `0.842` |

`rate: null` 을 `0%` 로 적지 않는다 -- "측정했더니 0" 과 "분모가 0 이라 재지
못함" 은 다른 사실이다(원칙8).

## 구성 (01-plan 69행 · 02-plan-verify O-5 · 결정 J·K·L)

1. 실행 메타 -- 공급자·모델(단일 값이 없으면 `providers_observed`/
   `models_observed` 관측 목록)·임베딩 모델·데이터셋 해시·`run_id`·`T_new`·
   격자·가중치 출처·`top_k_swept`.
2. 방식 × 지표(`T_merge` = 게이트 임계치) -- 오병합률·미검출률·제3 범주·
   P/R/F1·`ask_user_rate_by_kind` 셋.
3. 게이트(결정 K 지배 기준) -- `dominated_by`·`d10_direction`·`pass`·`reason`
   **바로 옆에** `T_merge=0.8` 오병합률 순위표(O-5). 지배 기준은 두 축을
   대칭으로 보지만 원칙1 은 두 축이 비대칭이라고 말하므로, 독자가 직접
   판단할 수 있어야 한다.
4. 곡선 -- 3계열 × 5방식 × 10점 Markdown 표와 `curve.csv` 링크 한 줄.
   PNG 는 만들지 않는다(결정 J(i), 발표용 그림은 P10).
5. 강제 경로·`llm_error`·부분집합·카테고리별.
6. 운영 최적점 **후보** -- 표본이 작으므로 "방향"이라고 못박는다.
7. 한계 -- R-5(임계치를 읽지 않는 방식의 평탄한 곡선)·분모 규칙 인용·
   결정 L·`provider` 가 null 일 때 읽는 법.

## 하지 않는 것

곡선 그림(P10)·실행(U6·U7)·실패 케이스 서술(U8). 해석 문장도 `metrics.json`
에 있는 수치의 범위를 넘지 않는다 -- 게이트 판정은 `gate.pass` 를 그대로
옮길 뿐, 이 모듈이 다시 판정하지 않는다.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from evaluation.curve import (
    GATE_T_MERGE,
    PROPOSED,
    RESERVED_TOP_KEYS,
    SERIES,
    validate_metrics_document,
)
from evaluation.metrics import ASK_KINDS, MetricsError, format_t_merge

__all__ = [
    "CURVE_LINK",
    "MISSING",
    "NULL_RATE",
    "SERIES_LABEL",
    "ReportError",
    "fmt_number",
    "fmt_ratio",
    "fmt_rate_value",
    "fmt_score",
    "optimum_candidate",
    "render_report",
]


class ReportError(MetricsError):
    """리포트 입력(`metrics.json`)이 계약을 어겼다 -- 깨진 입력으로 리포트를
    만들지 않는다(원칙8: 재현 불가능한 수치를 리포트에 넣지 않는다)."""


#: 분모 0 인 비율의 표기. `0%` 로 적지 않는다.
NULL_RATE = "측정 불가(분모 0)"

#: 입력에 그 키가 없을 때의 표기. 숫자를 지어내지 않는다.
MISSING = "기록 없음"

#: 곡선 원수치 링크(같은 `reports/` 안, 결정 J(i)).
CURVE_LINK = "curve.csv"

#: 곡선 3계열의 사람이 읽는 이름(`evaluation.curve.SERIES` 와 같은 순서).
SERIES_LABEL: dict[str, str] = {
    "false_merge_rate": "오병합률 — 다른 사람을 같은 사람으로 묶은 비율(원칙1)",
    "ask_user_identity_rate": "ask_user(identity) 발생률 — 사람에게 미룬 비율(마찰)",
    "miss_rate": "미검출률 — 아는 사람을 새 인물로 분리한 비율",
}

#: 결과 다섯 가지의 한국어 이름(`metrics.OUTCOMES`).
_OUTCOME_LABEL: dict[str, str] = {
    "merge_correct": "정답 병합",
    "false_merge": "오병합",
    "miss": "미검출",
    "deferred": "제3 범주(identity 보류)",
    "new_person_correct": "신규 판정 정답",
}

_R5_LINE = (
    "`exact_*`·`llm_single` 곡선은 임계치를 읽지 않아 평탄한 것이 정상이다 "
    "— 이 방식들은 `T_merge`·`T_new` 를 전혀 보지 않으므로 x 축을 움직여도 "
    "값이 변하지 않는다(02-plan-verify R-5). 평탄한 선을 \"임계치에 강건하다\" "
    "로 읽으면 안 된다."
)


# ---------------------------------------------------------------------------
# 표시 형식 (유일한 파생 -- 수치 자체는 만들지 않는다)
# ---------------------------------------------------------------------------


def fmt_number(value: Any) -> str:
    """수를 표에 적는 형식(정수는 정수로, 실수는 `%g`). `None` 은 `MISSING`."""

    if value is None:
        return MISSING
    if isinstance(value, bool):
        return "예" if value else "아니오"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):g}"


def fmt_rate_value(rate: Any) -> str:
    """`rate`(0~1) -> 백분율 한 자리. `None` 은 `NULL_RATE`."""

    if rate is None:
        return NULL_RATE
    return f"{float(rate) * 100:.1f}%"


def fmt_score(value: Any) -> str:
    """F1 처럼 분자·분모가 없는 파생 수치 -> 소수 세 자리. `None` 은 `NULL_RATE`."""

    if value is None:
        return NULL_RATE
    return f"{float(value):.3f}"


def fmt_ratio(block: Any) -> str:
    """`{"n","d","rate"}` -> `n/d (비율)`. 블록이 없으면 `MISSING`."""

    if block is None:
        return MISSING
    if not isinstance(block, Mapping) or not {"n", "d", "rate"} <= set(block):
        raise ReportError(f"ratio block expected (got {block!r})")
    return f"{int(block['n'])}/{int(block['d'])} ({fmt_rate_value(block['rate'])})"


def _cell(text: Any) -> str:
    """표 한 칸. 줄바꿈·파이프가 표를 깨뜨리지 않게 한다."""

    value = MISSING if text is None else str(text)
    return value.replace("|", "\\|").replace("\n", " ").strip() or MISSING


def _table(header: Sequence[str], rows: Iterable[Sequence[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(_cell(cell) for cell in header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(cell) for cell in row) + " |")
    return lines


def _join(values: Iterable[Any], *, empty: str = "없음") -> str:
    items = [str(value) for value in values]
    return ", ".join(items) if items else empty


# ---------------------------------------------------------------------------
# 문서 읽기 (입력은 이 함수들로만 만진다)
# ---------------------------------------------------------------------------


def _meta(doc: Mapping[str, Any]) -> Mapping[str, Any]:
    meta = doc.get("meta")
    if not isinstance(meta, Mapping):
        raise ReportError("metrics.json: 'meta' object is required")
    return meta


def _gate(doc: Mapping[str, Any]) -> Mapping[str, Any]:
    gate = doc.get("gate")
    if not isinstance(gate, Mapping):
        raise ReportError("metrics.json: 'gate' object is required")
    return gate


def _methods(doc: Mapping[str, Any]) -> list[str]:
    listed = _meta(doc).get("methods")
    if isinstance(listed, list) and listed:
        return [str(name) for name in listed]
    return [str(key) for key in doc if key not in RESERVED_TOP_KEYS]


def _grid(doc: Mapping[str, Any]) -> list[str]:
    grid = _meta(doc).get("grid")
    if not isinstance(grid, list) or not grid:
        raise ReportError("metrics.json: 'meta.grid' list is required")
    return [format_t_merge(value) for value in grid]


def _points(doc: Mapping[str, Any], method: str) -> dict[str, Mapping[str, Any]]:
    block = doc.get(method)
    if not isinstance(block, Mapping):
        raise ReportError(f"metrics.json: method block {method!r} is missing")
    by_t = block.get("by_t_merge")
    if not isinstance(by_t, Mapping):
        raise ReportError(f"metrics.json: {method}.by_t_merge object is required")
    return {format_t_merge(key): value for key, value in by_t.items()}


def _point(doc: Mapping[str, Any], method: str, t_key: str) -> Mapping[str, Any]:
    points = _points(doc, method)
    if t_key not in points:
        raise ReportError(f"metrics.json: {method} has no point at T_merge={t_key}")
    return points[t_key]


def _gate_key(doc: Mapping[str, Any]) -> str:
    """게이트를 판정한 격자점. `gate.t_merge_key` 가 있으면 그것을, 없으면
    `gate.t_merge` 를 접어서 쓴다(둘 다 없으면 모듈 기본값)."""

    gate = _gate(doc)
    key = gate.get("t_merge_key")
    if isinstance(key, str) and key:
        return format_t_merge(key)
    value = gate.get("t_merge")
    return format_t_merge(value) if value is not None else GATE_T_MERGE


def _series_block(point: Mapping[str, Any], series: str) -> Any:
    if series == "ask_user_identity_rate":
        by_kind = point.get("ask_user_rate_by_kind")
        return by_kind.get("identity") if isinstance(by_kind, Mapping) else None
    return point.get(series)


def _identity_value(meta: Mapping[str, Any], key: str, observed_key: str) -> str:
    """`provider`/`model` 이 null 이면 관측 목록으로 대체 표기한다(U4 는 값이
    둘 이상이면 단일 필드를 null 로 두고 전부를 `*_observed` 에 남긴다)."""

    value = meta.get(key)
    if isinstance(value, str) and value:
        return f"`{value}`"
    observed = meta.get(observed_key)
    if isinstance(observed, list) and observed:
        return "단일 값 없음 · 관측: " + ", ".join(f"`{item}`" for item in observed)
    return MISSING


# ---------------------------------------------------------------------------
# 운영 최적점 **후보** (순수 선택 -- 새 수치를 만들지 않는다)
# ---------------------------------------------------------------------------


def optimum_candidate(doc: Mapping[str, Any]) -> dict[str, Any]:
    """제안 방식 곡선에서 운영 최적점 **후보** 한 점을 고른다.

    규칙(원칙1 의 비대칭 비용을 그대로 옮긴 것): **오병합률이 가장 낮은
    격자점들 중 `T_merge` 가 가장 낮은 점**. 오병합을 먼저 막고, 같은
    오병합률이라면 질문(마찰)이 적은 쪽을 고른다 -- D10 방향이 성립하면
    `T_merge` 가 낮을수록 `ask_user(identity)` 가 적다.

    비교할 `rate` 가 하나도 없으면(전부 `null`) `{"t_merge": None}` 이다.
    """

    points = _points(doc, PROPOSED)
    measurable = [
        (t_key, point)
        for t_key, point in sorted(points.items(), key=lambda item: float(item[0]))
        if isinstance(point.get("false_merge_rate"), Mapping)
        and point["false_merge_rate"].get("rate") is not None
    ]
    if not measurable:
        return {
            "t_merge": None,
            "rule": "오병합률이 측정된 격자점이 없다(분모 0) -- 후보를 고르지 않는다",
        }
    best = min(float(point["false_merge_rate"]["rate"]) for _, point in measurable)
    for t_key, point in measurable:
        if float(point["false_merge_rate"]["rate"]) <= best + 1e-9:
            return {
                "t_merge": t_key,
                "false_merge_rate": point.get("false_merge_rate"),
                "miss_rate": point.get("miss_rate"),
                "ask_user_identity_rate": _series_block(point, "ask_user_identity_rate"),
                "deferred_identity_rate": point.get("deferred_identity_rate"),
                "rule": (
                    "오병합률이 가장 낮은 격자점들 중 T_merge 가 가장 낮은 점"
                    "(원칙1 — 오병합을 먼저 막고, 같은 오병합률이면 질문이 적은 쪽)"
                ),
            }
    raise ReportError("optimum_candidate: unreachable")  # pragma: no cover


# ---------------------------------------------------------------------------
# 절
# ---------------------------------------------------------------------------


def _head_section(doc: Mapping[str, Any]) -> list[str]:
    return [
        "# 파일럿 평가 결과 — 오병합률·미검출률·트레이드오프 곡선",
        "",
        "> 이 문서는 `python -m evaluation.report --metrics <metrics.json> "
        "--out <eval.md>` 의 출력이다.",
        "> 본문의 수치는 **전부 그 `metrics.json` 에서 읽은 것**이고, 생성기는 "
        "날짜·시각·환경변수·DB·네트워크를 읽지 않는다 — 같은 입력이면 같은 "
        "바이트다(원칙8).",
        "> 비율은 언제나 `분자/분모 (비율)` 로 적고, 분모가 0 이면 "
        f"`{NULL_RATE}` 다. `0%` 와 구분한다.",
        "",
    ]


def _meta_section(doc: Mapping[str, Any]) -> list[str]:
    meta = _meta(doc)
    counts = meta.get("mention_counts") if isinstance(meta.get("mention_counts"), Mapping) else {}
    weights = meta.get("weights") if isinstance(meta.get("weights"), Mapping) else {}
    configured = meta.get("model_configured")
    configured_text = (
        _join(f"`{key}` = `{value}`" for key, value in sorted(configured.items()))
        if isinstance(configured, Mapping) and configured
        else MISSING
    )

    rows: list[list[str]] = [
        ["판정 공급자 (`meta.provider`)", _identity_value(meta, "provider", "providers_observed")],
        ["판정 모델 (`meta.model`)", _identity_value(meta, "model", "models_observed")],
        ["설정 모델 문자열 (`meta.model_configured`)", configured_text],
        [
            "임베딩 모델 (`meta.embedding_model`)",
            f"`{meta['embedding_model']}`" if meta.get("embedding_model") else MISSING,
        ],
        [
            "데이터셋 해시 (`meta.dataset_hash`)",
            f"`{meta['dataset_hash']}`" if meta.get("dataset_hash") else MISSING,
        ],
        ["실행 id (`meta.run_id`)", f"`{meta['run_id']}`" if meta.get("run_id") else MISSING],
        [
            "평가 커밋 (`meta.commit`)",
            f"`{meta['commit']}`" if meta.get("commit") else f"{MISSING} — 실행 evidence 와 `run_id` 로 되짚는다(L-001)",
        ],
        ["`metrics.json` 스키마 판 (`meta.schema_version`)", fmt_number(meta.get("schema_version"))],
        ["시나리오 수 (`meta.scenario_count`)", fmt_number(meta.get("scenario_count"))],
        ["행 수 (`meta.row_count`)", fmt_number(meta.get("row_count"))],
        [
            "mention 수 (`meta.mention_counts`)",
            "골드 "
            + fmt_number(counts.get("gold"))
            + " · 채점 "
            + fmt_number(counts.get("gold_scored"))
            + " · ambiguous 제외 "
            + fmt_number(counts.get("ambiguous"))
            + " · passing "
            + fmt_number(counts.get("passing")),
        ],
        ["`T_new` (고정, 스윕하지 않음)", fmt_number(meta.get("t_new"))],
        ["`T_merge` 격자 (x 축)", _join(_grid(doc))],
        [
            "`top_k` 스윕 (`meta.top_k_swept`)",
            fmt_number(meta.get("top_k_swept")) + " — " + _cell(meta.get("top_k_swept_note")),
        ],
        [
            "확신도 가중치 (`meta.weights`)",
            "`s_llm` "
            + fmt_number(weights.get("llm"))
            + " · `s_emb` "
            + fmt_number(weights.get("emb"))
            + " · `s_rule` "
            + fmt_number(weights.get("rule")),
        ],
        ["가중치 출처", _cell(weights.get("source"))],
        # 결정 H(i) -- `meta.weights` 는 설정값(비율)이고 실제 적용값은
        # mention 마다 다르다. 어느 산식·어느 보수 분기로 판정했는지를
        # 메타 표에서 바로 읽을 수 있어야 한다(D12·D13, 원칙8).
        [
            "가중치 결합 정책 (`meta.weights_policy`)",
            f"`{meta['weights_policy']}`" if meta.get("weights_policy") else MISSING,
        ],
        [
            "감점 후보 연결 정책 (`meta.penalized_merge_policy`)",
            f"`{meta['penalized_merge_policy']}`"
            if meta.get("penalized_merge_policy")
            else MISSING,
        ],
        ["방식 (`meta.methods`, 순서 고정)", _join(f"`{name}`" for name in _methods(doc))],
    ]

    lines = ["## 실행 메타", "", *_table(["항목", "값"], rows), ""]

    llm_rows = []
    for method in _methods(doc):
        block = doc.get(method)
        llm = block.get("llm") if isinstance(block, Mapping) else None
        if not isinstance(llm, Mapping):
            continue
        llm_rows.append(
            [
                f"`{method}`",
                fmt_number(llm.get("calls")),
                fmt_number(llm.get("tokens_in")),
                fmt_number(llm.get("tokens_out")),
                fmt_number(llm.get("error_calls")),
                fmt_number(llm.get("mentions")),
                fmt_number(llm.get("skipped_mentions")),
            ]
        )
    if llm_rows:
        lines += [
            "### LLM 호출 (방식별, `llm_fresh_call` 행만)",
            "",
            *_table(
                [
                    "방식",
                    "호출 수",
                    "tokens_in",
                    "tokens_out",
                    "오류 호출",
                    "mention 수",
                    "LLM 건너뜀",
                ],
                llm_rows,
            ),
            "",
        ]
    return lines


def _method_table_section(doc: Mapping[str, Any]) -> list[str]:
    t_key = _gate_key(doc)
    rows: list[list[str]] = []
    for method in _methods(doc):
        point = _point(doc, method, t_key)
        ask = point.get("ask_user_rate_by_kind")
        ask = ask if isinstance(ask, Mapping) else {}
        rows.append(
            [
                f"`{method}`",
                fmt_number(point.get("scored")),
                fmt_ratio(point.get("false_merge_rate")),
                fmt_ratio(point.get("miss_rate")),
                fmt_ratio(point.get("deferred_identity_rate")),
                fmt_ratio(point.get("precision")),
                fmt_ratio(point.get("recall")),
                fmt_score(point.get("f1")),
                *[fmt_ratio(ask.get(kind)) for kind in ASK_KINDS],
                fmt_ratio(point.get("expected_ask_user_allowed")),
            ]
        )

    outcome_rows: list[list[str]] = []
    for method in _methods(doc):
        outcomes = _point(doc, method, t_key).get("outcomes")
        if not isinstance(outcomes, Mapping):
            continue
        outcome_rows.append(
            [f"`{method}`", *[fmt_number(outcomes.get(name)) for name in _OUTCOME_LABEL]]
        )

    lines = [
        f"## 방식 × 지표 (`T_merge` = {t_key})",
        "",
        "모든 칸은 `분자/분모 (비율)` 다. 분모는 채점 대상 골드 mention "
        "(`meta.denominator_rule.scored_base`)이고, `ambiguous` mention 과 "
        "`passing` mention 은 이 분모에 없다(아래 한계 절).",
        "오병합률과 미검출률은 **분리 측정**이다 — 원칙1 은 두 비용이 대칭이 "
        "아니라고 말한다(오병합 = 신뢰 붕괴, 미검출 = 복구 가능).",
        "",
        *_table(
            [
                "방식",
                "채점 행",
                "오병합률",
                "미검출률",
                "제3 범주(identity 보류)",
                "precision",
                "recall",
                "f1",
                *[f"ask_user({kind})" for kind in ASK_KINDS],
                "허용 집합 적중",
            ],
            rows,
        ),
        "",
    ]
    if outcome_rows:
        lines += [
            f"### 결과 분포 (`outcomes`, `T_merge` = {t_key})",
            "",
            *_table(
                ["방식", *[_OUTCOME_LABEL[name] for name in _OUTCOME_LABEL]],
                outcome_rows,
            ),
            "",
        ]
    return lines


def _gate_section(doc: Mapping[str, Any]) -> list[str]:
    gate = _gate(doc)
    t_key = _gate_key(doc)
    passed = gate.get("pass")
    verdict = "통과" if passed is True else "미달" if passed is False else MISSING

    judge_rows = [
        ["판정 격자점 (`gate.t_merge`)", fmt_number(gate.get("t_merge"))],
        ["`T_new` (고정)", fmt_number(gate.get("t_new"))],
        ["제안 방식을 지배한 베이스라인 (`gate.dominated_by`)", _join(f"`{n}`" for n in gate.get("dominated_by") or [])],
        ["비교 불가 (`gate.undetermined`)", _join(f"`{n}`" for n in gate.get("undetermined") or [])],
        ["D10 방향 (`gate.d10_direction`)", fmt_number(gate.get("d10_direction"))],
        ["판정 (`gate.pass`)", f"**{verdict}**"],
        ["이유 (`gate.reason`)", _cell(gate.get("reason")) if gate.get("reason") else "없음"],
    ]

    axes_rows: list[list[str]] = []
    proposed = gate.get("proposed")
    if isinstance(proposed, Mapping):
        axes_rows.append(
            [
                f"`{PROPOSED}` (제안 방식)",
                fmt_ratio(proposed.get("false_merge_rate")),
                fmt_ratio(proposed.get("miss_rate")),
                "—",
            ]
        )
    baselines = gate.get("baselines")
    if isinstance(baselines, Mapping):
        for name in sorted(baselines):
            block = baselines[name]
            if not isinstance(block, Mapping):
                continue
            dominates = block.get("dominates_proposed")
            axes_rows.append(
                [
                    f"`{name}`",
                    fmt_ratio(block.get("false_merge_rate")),
                    fmt_ratio(block.get("miss_rate")),
                    "지배함"
                    if dominates is True
                    else "지배하지 않음"
                    if dominates is False
                    else "판정 불가",
                ]
            )

    ranking_rows: list[list[str]] = []
    for entry in gate.get("false_merge_ranking") or []:
        if not isinstance(entry, Mapping):
            continue
        ranking_rows.append(
            [
                fmt_number(entry.get("rank")),
                f"`{entry.get('method')}`",
                fmt_ratio(entry.get("false_merge_rate")),
            ]
        )

    lines = [
        "## 게이트 (결정 K — 지배 기준)",
        "",
        "> " + _cell(gate.get("rule") or MISSING),
        "",
        "> " + _cell(gate.get("d10_rule") or MISSING),
        "",
        *_table(["항목", "값"], judge_rows),
        "",
    ]
    if axes_rows:
        lines += [
            f"### 두 축 (`T_merge` = {t_key})",
            "",
            *_table(["방식", "오병합률", "미검출률", "제안 방식 지배 여부"], axes_rows),
            "",
        ]
    if ranking_rows:
        lines += [
            f"### 오병합률 순위 (`T_merge` = {t_key}, 02-plan-verify O-5)",
            "",
            "지배 기준은 오병합률·미검출률 두 축을 **대칭**으로 보지만, 원칙1 은 "
            "두 축이 비대칭이라고 말한다. 그래서 게이트 결과 바로 옆에 오병합률만의 "
            "순위를 분자·분모와 함께 싣는다 — 독자가 직접 판단할 수 있어야 한다.",
            "",
            *_table(["순위", "방식", "오병합률"], ranking_rows),
            "",
        ]
    return lines


def _curve_section(doc: Mapping[str, Any]) -> list[str]:
    grid = _grid(doc)
    meta = _meta(doc)
    curve = meta.get("curve") if isinstance(meta.get("curve"), Mapping) else {}
    lines = [
        f"## 트레이드오프 곡선 (x = `T_merge`, `T_new` = {fmt_number(meta.get('t_new'))} 고정)",
        "",
        f"원수치: [`{CURVE_LINK}`]({CURVE_LINK}) — 열 "
        + _join(
            (f"`{name}`" for name in curve.get("csv_columns") or []), empty=MISSING
        )
        + ". 그림(PNG)은 만들지 않는다(결정 J(i) — 발표용 그림은 P10).",
        "",
        "x 축은 `T_merge` **하나**다. `T_new` 는 고정이라 \"질문이 늘었다\"가 "
        "어느 임계치 때문인지 말할 수 있다(S3.7 §4).",
        "",
    ]
    for series in SERIES:
        rows: list[list[str]] = []
        for method in _methods(doc):
            points = _points(doc, method)
            cells = []
            for t_key in grid:
                point = points.get(t_key)
                cells.append(
                    fmt_ratio(_series_block(point, series)) if point is not None else MISSING
                )
            rows.append([f"`{method}`", *cells])
        lines += [
            f"### {SERIES_LABEL.get(series, series)}",
            "",
            *_table(["방식 \\ `T_merge`", *grid], rows),
            "",
        ]
    return lines


def _diagnostics_section(doc: Mapping[str, Any]) -> list[str]:
    t_key = _gate_key(doc)
    meta = _meta(doc)
    forced = meta.get("forced_reason") if isinstance(meta.get("forced_reason"), Mapping) else {}

    forced_rows: list[list[str]] = []
    for method in _methods(doc):
        block = forced.get(method) if isinstance(forced.get(method), Mapping) else None
        entry = block.get(t_key) if isinstance(block, Mapping) else None
        if not isinstance(entry, Mapping):
            continue
        counts = entry.get("counts") if isinstance(entry.get("counts"), Mapping) else {}
        forced_rows.append(
            [
                f"`{method}`",
                fmt_ratio(entry.get("rate")),
                _join(
                    f"`{name}` {fmt_number(value)}" for name, value in sorted(counts.items())
                ),
            ]
        )

    error_rows: list[list[str]] = []
    for method in _methods(doc):
        point = _point(doc, method, t_key)
        errors = point.get("llm_error") if isinstance(point.get("llm_error"), Mapping) else {}
        clean = (
            point.get("excluding_llm_error")
            if isinstance(point.get("excluding_llm_error"), Mapping)
            else {}
        )
        error_rows.append(
            [
                f"`{method}`",
                _join(
                    f"`{name}` {fmt_number(value)}"
                    for name, value in sorted(errors.items())
                    if name != "none"
                ),
                fmt_number(clean.get("removed_rows")),
                fmt_ratio(clean.get("false_merge_rate")),
                fmt_ratio(clean.get("miss_rate")),
            ]
        )

    subset_rows: list[list[str]] = []
    for method in _methods(doc):
        subsets = _point(doc, method, t_key).get("subsets")
        if not isinstance(subsets, Mapping):
            continue
        unchecked = subsets.get("merge_rule_unchecked") or {}
        relaxed = subsets.get("merge_relaxed_retry") or {}
        # D13 위험 계측 -- 규칙이 감점한 후보가 실제로 연결된 건수. 이 열이
        # 없으면 "후보가 늘어 오병합 기회가 는다"는 D13 파급을 리포트만
        # 보고는 확인할 수 없다(`metrics.json` 을 열어야 한다).
        penalized = subsets.get("penalized_merge") or {}
        subset_rows.append(
            [
                f"`{method}`",
                fmt_number(subsets.get("merges")),
                fmt_number(unchecked.get("merges")),
                fmt_ratio(unchecked.get("false_merge_rate")),
                fmt_number(relaxed.get("merges")),
                fmt_ratio(relaxed.get("false_merge_rate")),
                fmt_number(penalized.get("merges")),
                fmt_ratio(penalized.get("false_merge_rate")),
                fmt_number(penalized.get("relaxed_pass_merges")),
            ]
        )

    passing_rows: list[list[str]] = []
    for method in _methods(doc):
        passing = _point(doc, method, t_key).get("passing")
        if not isinstance(passing, Mapping):
            continue
        by_decision = (
            passing.get("by_decision") if isinstance(passing.get("by_decision"), Mapping) else {}
        )
        passing_rows.append(
            [
                f"`{method}`",
                fmt_ratio(passing.get("false_positive")),
                _join(
                    f"`{name}` {fmt_number(value)}"
                    for name, value in sorted(by_decision.items())
                ),
                fmt_ratio(passing.get("expected_ask_user_allowed")),
            ]
        )

    lines = [f"## 강제 경로·LLM 오류·부분집합 (`T_merge` = {t_key})", ""]
    if forced_rows:
        lines += [
            "강제 경로(`forced_reason != null`)는 임계치와 무관하게 밴드가 정해지므로 "
            "곡선의 기울기를 설명하지 않는다 — 계열과 **별도로** 집계한다"
            "(`meta.forced_reason`, P3-er §7). 격자 전체 분포는 `metrics.json` 에 있다.",
            "",
            *_table(["방식", "강제 경로 비율", "내역"], forced_rows),
            "",
        ]
    if error_rows:
        lines += [
            "### `llm_error` (기본 분모에는 남긴다)",
            "",
            "공급자 오류 행을 한 방식에서만 분모에서 빼면 방식 간 비교가 깨진다 — "
            "기본 분모에 남기고, 오류 행을 뺀 같은 지표를 옆에 함께 싣는다"
            "(`point.excluding_llm_error`).",
            "",
            *_table(
                [
                    "방식",
                    "오류 분포",
                    "오류 제외 시 빠진 행",
                    "오류 제외 오병합률",
                    "오류 제외 미검출률",
                ],
                error_rows,
            ),
            "",
        ]
    if subset_rows:
        lines += [
            "### 부분집합 (`merge` 행만, P3-er §7 리스크 계측)",
            "",
            "**감점 후보 merge**(D13 위험 계측)는 2단계 규칙 필터가 감점만 하고 "
            "남긴 후보가 실제로 연결된 건수다 — 배제를 감점으로 바꾸면 후보가 "
            "늘어 오병합 기회도 느는데(D13 파급), 이 열이 그 대가를 직접 센다. "
            "`그중 완화 통과` 는 위계 1칸 완화로 자동 연결이 허용된 예외"
            "(결정 A(i), 승진류)이며 나머지는 `meta.penalized_merge_policy` "
            "정책에 따른다.",
            "",
            *_table(
                [
                    "방식",
                    "merge 수",
                    "규칙 미검사 merge",
                    "그 오병합률",
                    "완화 재검색 merge",
                    "그 오병합률",
                    "감점 후보 merge",
                    "그 오병합률",
                    "그중 완화 통과",
                ],
                subset_rows,
            ),
            "",
        ]
    empty_hints = meta.get("empty_derive_hints")
    if isinstance(empty_hints, Mapping):
        lines += [
            "`derive_hints` 가 빈 dict 인 mention 비율(호칭 사전 누락 계측): "
            + fmt_ratio({k: empty_hints.get(k) for k in ("n", "d", "rate")})
            + " — 분모는 "
            + _cell(empty_hints.get("basis") or MISSING)
            + ".",
            "",
        ]
    if passing_rows:
        lines += [
            f"### `passing_mentions` 오탐 (골드 분모 밖, `T_merge` = {t_key})",
            "",
            *_table(
                ["방식", "오탐율(`new_person` 판정)", "판정 분포", "허용 집합 적중"],
                passing_rows,
            ),
            "",
        ]
    return lines


def _category_section(doc: Mapping[str, Any]) -> list[str]:
    t_key = _gate_key(doc)
    rows: list[list[str]] = []
    for method in _methods(doc):
        by_category = _point(doc, method, t_key).get("by_category")
        if not isinstance(by_category, Mapping):
            continue
        for category in sorted(by_category):
            block = by_category[category]
            if not isinstance(block, Mapping):
                continue
            rows.append(
                [
                    f"`{method}`",
                    f"`{category}`",
                    fmt_number(block.get("scored")),
                    fmt_ratio(block.get("false_merge_rate")),
                    fmt_ratio(block.get("miss_rate")),
                    fmt_ratio(block.get("deferred_identity_rate")),
                ]
            )
    if not rows:
        return []
    return [
        f"## 카테고리별 (`T_merge` = {t_key})",
        "",
        "카테고리당 표본이 적어 한 건이 비율을 크게 흔든다 — 분자·분모를 함께 읽는다.",
        "",
        *_table(
            ["방식", "카테고리", "채점 행", "오병합률", "미검출률", "제3 범주"],
            rows,
        ),
        "",
    ]


def _optimum_section(doc: Mapping[str, Any]) -> list[str]:
    meta = _meta(doc)
    candidate = optimum_candidate(doc)
    scenarios = meta.get("scenario_count")
    sample = (
        f"표본 {fmt_number(scenarios)}건"
        if isinstance(scenarios, int)
        else "이 표본(`meta.scenario_count` 기록 없음)"
    )

    if candidate["t_merge"] is None:
        body = (
            f"제안 방식 곡선에서 오병합률이 측정된 격자점이 없어(`{NULL_RATE}`) "
            "후보를 고르지 않는다. 측정하지 못한 것을 최적점으로 제시하지 않는다(원칙8)."
        )
    else:
        body = (
            f"후보는 `T_merge` = {candidate['t_merge']} 다. 선택 규칙은 "
            f"{candidate['rule']} 이며, 그 점에서 오병합률 "
            f"{fmt_ratio(candidate['false_merge_rate'])} · 미검출률 "
            f"{fmt_ratio(candidate['miss_rate'])} · ask_user(identity) 발생률 "
            f"{fmt_ratio(candidate['ask_user_identity_rate'])} 다. "
            f"`T_merge` 를 더 올리면 질문(마찰)이 늘고, 내리면 오병합이 늘어난다"
            "(D10 방향, 위 곡선)."
        )

    return [
        "## 운영 최적점 **후보** (확정값이 아니다)",
        "",
        body,
        "",
        f"**{sample}이므로 이것은 방향(direction)이지 확정값이 아니다.** 카테고리당 "
        "표본이 한 자리 수라 오병합 한 건이 비율을 크게 흔든다. 운영 `T_merge`·"
        "`T_new` 의 확정과 가중치(D12 -- 비율 5:3:2) 조정은 전체 데이터셋을 쓰는 "
        "P10-final-eval 에서 하고, 이 문서는 후보 구간과 방향까지만 말한다.",
        "",
    ]


def _limits_section(doc: Mapping[str, Any]) -> list[str]:
    meta = _meta(doc)
    rule = meta.get("denominator_rule")
    lines = [
        "## 한계와 읽는 법",
        "",
        f"- **평탄한 곡선**: {_R5_LINE}",
        "- **작은 표본**: 모든 비율에 분자·분모를 함께 적은 이유다. 비율만 보면 "
        "한 건이 몇 %인지 알 수 없다. 신뢰구간과 절대 수치 해석은 P10 의 몫이다.",
        "- **`score` 축 없음**: `score` 의 의미는 방식마다 달라 어떤 표에도 "
        "넣지 않았다(같은 축에 놓으면 비교가 아니라 착시가 된다).",
        "- **게이트 판정은 다시 하지 않는다**: 위 통과/미달은 `metrics.json` 의 "
        "`gate.pass` 를 그대로 옮긴 것이다. 이 생성기는 판정식을 갖고 있지 않다.",
    ]
    provider = meta.get("provider")
    if not (isinstance(provider, str) and provider):
        observed = meta.get("providers_observed") or []
        models = meta.get("models_observed") or []
        lines.append(
            "- **공급자·모델이 단일 값이 아니다**: `meta.provider`/`meta.model` 이 "
            "`null` 이므로 관측 목록(`providers_observed` = "
            + _join(f"`{item}`" for item in observed)
            + ", `models_observed` = "
            + _join(f"`{item}`" for item in models)
            + ")으로 읽는다. 한 벌 실행이 아니었다면 방식 간 비교에 이 차이를 "
            "함께 고려해야 한다."
        )
    if isinstance(rule, Mapping) and rule:
        lines += ["", "### 분모 규칙 (`meta.denominator_rule` 인용)", ""]
        for key in sorted(rule):
            lines.append(f"- **`{key}`** — {_cell(rule[key])}")
        third = rule.get("third_category")
        if third:
            lines += [
                "",
                "그중 **결정 L**(제3 범주의 정의)이 이 리포트의 오병합률·미검출률을 "
                "가른다: `identity` 만 제3 범주이고 `new_person` 은 단정이므로 "
                "골드와 대조해 채점한다. 둘 다 빼면 미검출 분자가 구조적으로 0 이 "
                "되어 게이트의 한 축이 죽는다.",
            ]
    lines += [
        "",
        "### 재현",
        "",
        "- 이 문서는 `metrics.json` 하나로 다시 만들어진다 — 같은 입력이면 "
        "`diff` 가 0줄이다(판정 표 `eval.md` 재생성 행).",
        f"- 곡선 원수치는 [`{CURVE_LINK}`]({CURVE_LINK}), `s_llm` 구간별 실제 "
        "정답률은 `calibration.json` 에 따로 있다.",
        "",
    ]
    return lines


# ---------------------------------------------------------------------------
# 본문
# ---------------------------------------------------------------------------


def render_report(doc: Mapping[str, Any]) -> str:
    """`metrics.json` 문서 -> `eval.md` 본문(끝에 줄바꿈 하나, 줄 끝 공백 없음)."""

    problems = validate_metrics_document(doc)
    if problems:
        raise ReportError(
            "metrics.json failed validation ("
            + str(len(problems))
            + " problem(s)): "
            + "; ".join(problems)
        )

    lines: list[str] = []
    lines += _head_section(doc)
    lines += _meta_section(doc)
    lines += _method_table_section(doc)
    lines += _gate_section(doc)
    lines += _curve_section(doc)
    lines += _diagnostics_section(doc)
    lines += _category_section(doc)
    lines += _optimum_section(doc)
    lines += _limits_section(doc)

    text = "\n".join(line.rstrip() for line in lines).rstrip("\n")
    return text + "\n"


# ---------------------------------------------------------------------------
# CLI (파일 하나를 읽고 파일 하나를 쓴다. 그 밖의 입력은 없다)
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.report",
        description="metrics.json -> eval.md (입력은 metrics.json 하나뿐, DB·네트워크·시계 없음)",
    )
    parser.add_argument("--metrics", required=True, help="reports/metrics.json 경로")
    parser.add_argument("--out", default=None, help="eval.md 경로(생략하면 표준출력)")
    args = parser.parse_args(argv)

    source = Path(args.metrics)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL {source}: {exc}")
        return 1

    problems = validate_metrics_document(document)
    if problems:
        # 깨진 입력으로 리포트를 만들지 않는다 -- 재현 불가능한 수치를 본문에
        # 넣는 것보다 멈추는 것이 낫다(원칙8).
        print(f"FAIL {source}: {len(problems)} problem(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    text = render_report(document)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":  # pragma: no cover -- CLI 진입점
    raise SystemExit(main())
