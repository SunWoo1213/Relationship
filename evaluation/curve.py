"""Refs: P4-pilot-eval R3 D10 S3.7 원칙1 원칙2 원칙8 -- 곡선·`metrics.json` 조립.

01-plan U4(68행). **입력은 U1 러너가 쓴 JSONL(또는 그것으로 만든 U2
`compute_metrics()` 결과)뿐이다** -- DB·네트워크·LLM 을 부르지 않는다. 같은
JSONL 을 넣으면 언제나 같은 `metrics.json`·같은 `curve.csv` 가 나온다(원칙8).

## 곡선 (S3.7 §4 · eval-harness §4)

- x 축 = `T_merge` 격자 10점 {0.5, 0.55, …, 0.95} **하나뿐**이고 `T_new` 는
  0.3 **고정**이다(스윕하지 않는다). 두 임계치를 한 축에 겹쳐 그리면
  "질문이 늘었다"가 어느 임계치 때문인지 말할 수 없다.
- y = 세 계열 × 다섯 방식.

  | 계열 | 출처(U2 point) | 뜻 |
  |------|----------------|-----|
  | `false_merge_rate` | `point["false_merge_rate"]` | 다른 사람을 같은 사람으로 묶은 비율(원칙1) |
  | `ask_user_identity_rate` | `point["ask_user_rate_by_kind"]["identity"]` | 판단을 사람에게 미룬 비율 = 마찰 |
  | `miss_rate` | `point["miss_rate"]` | 같은 사람을 새 인물로 분리한 비율 |

  세 계열 모두 `{"n","d","rate"}` 를 그대로 옮긴다 -- 표본 40건에서 비율만
  보면 1건이 몇 %인지 알 수 없다(`reports/curve.csv` 에도 `n`·`d` 열이 있다).

- **`forced_reason != null` 행은 계열과 별도 집계**다(P3-er §7). 강제 경로
  (`no_candidates`·`llm_failed`·`no_matched`·`out_of_range_id`·`tie`…)는
  임계치와 무관하게 밴드가 정해지므로 곡선의 기울기를 설명하지 않는다.
  `meta.forced_reason` 에 방식 × 임계치별 분포로 따로 남긴다.

## 게이트 (결정 K → 개정 (a) 지배 기준, 01-plan 227행)

`T_merge = 0.8` 한 점에서

    베이스라인 b 가 제안 방식 p 를 **지배**한다
      := b.false_merge_rate ≤ p.false_merge_rate
         and b.miss_rate    ≤ p.miss_rate
         and (둘 중 하나는 엄격히 <)

`dominated_by` 는 지배하는 베이스라인 목록이고, `baselines` 키 집합은
`RESOLVERS` − `proposed` = 4개다. **동률(두 축 모두 =)은 미지배**이며
게이트 통과 쪽이다 -- `exact_raw`/`exact_norm` 은 단독 일치 1명일 때만
병합해서 40건에서 오병합 0 이 되기 쉬운데, 원안의 단일 부등식(`<`)은
제안 방식이 오병합 0 이어도 `0 < 0` 이 거짓이라 방식 품질과 무관하게
미달을 냈다(01-plan 227행 개정 사유).

`d10_direction` 은 제안 방식 곡선이 D10 방향인가다 -- `T_merge` 를 높이면
오병합률이 **증가하지 않고** `ask_user(identity)` 발생률이 **감소하지
않는다**(비엄격 단조). 양 끝점이 아니라 **연속 격자점 쌍 전부**를 본다
(02-plan-verify R-7(1)): 결정 C(i) 재밴드 구조상 `proposed` 곡선은 단조여야
하고, 중간에서 역전이 나오면 그것은 러너 버그의 신호다.

`pass = (dominated_by == []) and d10_direction`. 다만 비교에 쓰는 `rate` 가
`null`(분모 0)이면 **조용히 통과시키지 않는다** -- `pass: false` 와 함께
`gate.reason` 에 이유를 적는다(원칙8: 측정하지 못한 것과 0 은 다르다).

O-5(02-plan-verify) 때문에 `gate.false_merge_ranking` 에 `T_merge=0.8` 의
다섯 방식 오병합률 순위를 분자·분모와 함께 같이 싣는다 -- 지배 기준은 두
축을 대칭으로 보지만 원칙1 은 두 축이 비대칭이라고 말하므로, 독자가 직접
판단할 수 있어야 한다.

## `metrics.json` 최상위 구조

    {
      "proposed": {...}, "exact_raw": {...}, "exact_norm": {...},
      "embedding_only": {...}, "llm_single": {...},   # RESOLVERS 순서 고정
      "meta": {...},                                  # 비-방식 키는 이 둘뿐
      "gate": {...}
    }

방식 블록은 U2 `compute_metrics()["methods"][name]` 을 **그대로** 옮긴 것이다
(지표를 여기서 다시 계산하지 않는다 -- 두 곳에서 세면 두 수치가 생긴다).
`meta` 는 U2 `meta`(분모 규칙·격자·제외 수) 위에 실행 정체(`provider`·
`model`·`embedding_model`·`dataset_hash`·`run_id`·`commit`·`run_mode`)와
결정 H(`top_k_swept: false`)·가중치를 얹은 것이다.

`meta.model` 의 출처는 U3 보정표와 **같다**(`detail["model"]` = 판정이 돌려준
모델명). 설정 문자열(`OPENAI_MODEL`)은 `meta.model_configured` 로 따로 적는다
(P3-llm-providers §7 인계 4 -- Gemini 는 `model_version` 이 설정과 다를 수
있다). `embedding_model`·`dataset_hash`·`run_id`·`commit`(L-001, 평가한
커밋)·`run_mode`(`stub`/`real`, 수용 기준 판정 명령이 읽는다) 는 JSONL 에
없는 값이라 **호출자가 넘긴다**(U6 `scripts/run_pilot_eval.py`) -- 여기서
환경변수·git 을 읽으면 같은 입력이 같은 출력을 내지 않는다. 생략하면
`null` 이고 스키마 검증은 그대로 통과한다(U5 리포트는 `기록 없음`).

## 하지 않는 것

리포트 본문(U5 `evaluation/report.py`)·실행 CLI 와 비용 가드(U6)·실 공급자
실행(U7). 이 모듈은 `reports/` 실물을 스스로 만들지 않는다 -- 경로를 받으면
쓸 뿐이다.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from evaluation import metrics as _metrics
from evaluation.metrics import (
    MetricsError,
    compute_metrics,
    format_t_merge,
    load_rows,
    mention_level_rows,
)

__all__ = [
    "CURVE_COLUMNS",
    "EXPECTED_GRID",
    "GATE_T_MERGE",
    "METRICS_SCHEMA_VERSION",
    "PROPOSED",
    "SERIES",
    "T_NEW",
    "CurveError",
    "build_gate",
    "build_metrics_document",
    "curve_rows",
    "forced_reason_summary",
    "validate_metrics_document",
    "write_curve_csv",
]


class CurveError(MetricsError):
    """곡선·`metrics.json` 조립 입력이 계약을 어겼다(원칙8 -- 멈춘다)."""


#: 제안 방식 이름. 나머지 넷이 베이스라인이다(`RESOLVERS` − `proposed`).
PROPOSED = "proposed"

#: `T_new` 는 고정이다(S3.7 §4 -- x 축은 `T_merge` 하나).
T_NEW: float = 0.3

#: x 축 격자 10점. `evaluation/runner.py::T_MERGE_GRID` 와 같은 값이며, 여기서
#: 다시 적는 이유는 `metrics.json` 을 **러너 없이도** 검증할 수 있어야 하기
#: 때문이다(`--validate` 는 JSON 파일 하나만 받는다).
EXPECTED_GRID: tuple[float, ...] = tuple(round(0.5 + 0.05 * i, 2) for i in range(10))

#: 게이트를 판정하는 격자점(결정 K, S3.3 초기값 `T_merge = 0.8`).
GATE_T_MERGE: str = format_t_merge(0.8)

#: 곡선 y 세 계열. 값은 `{"n","d","rate"}` 그대로다.
SERIES: tuple[str, ...] = ("false_merge_rate", "ask_user_identity_rate", "miss_rate")

#: `reports/curve.csv` 열. `t_new` 열은 "스윕하지 않았다"를 파일 안에서
#: 보이게 한다(01-plan 판정 표 104행이 `{'0.3'}` 하나를 요구한다).
CURVE_COLUMNS: tuple[str, ...] = (
    "method",
    "t_merge",
    "t_new",
    "series",
    "n",
    "d",
    "rate",
)

#: `metrics.json` 자체의 스키마 판(구조가 바뀌면 올린다).
METRICS_SCHEMA_VERSION = 1

#: 최상위에서 방식이 아닌 키(O-4 -- 방식 키 5개를 셀 때 이 둘을 뺀다).
RESERVED_TOP_KEYS: tuple[str, ...] = ("meta", "gate")

_GATE_REQUIRED_KEYS: tuple[str, ...] = (
    "t_merge",
    "proposed",
    "baselines",
    "dominated_by",
    "d10_direction",
    "pass",
)

_META_REQUIRED_KEYS: tuple[str, ...] = (
    "provider",
    "model",
    "embedding_model",
    "dataset_hash",
    "schema_version",
    "run_id",
    "t_new",
    "grid",
    "top_k_swept",
    "denominator_rule",
    "methods",
    "weights",
    "model_configured",
)

#: 부동소수 비교 허용 오차. 비율은 정수 나눗셈에서 나오므로 이 정도면 충분하다.
_EPS = 1e-9

DOMINANCE_RULE = (
    "베이스라인 b 가 제안 방식 p 를 지배한다 := b.false_merge_rate <= "
    "p.false_merge_rate and b.miss_rate <= p.miss_rate and (둘 중 하나는 "
    "엄격히 <). 두 축 모두 동률이면 미지배(통과 쪽). pass = (dominated_by "
    "== []) and d10_direction, 단 비교에 쓰는 rate 가 null 이면 pass: false "
    "+ gate.reason (결정 K 개정 (a), 01-plan 227행)."
)

D10_RULE = (
    "제안 방식 곡선의 연속 격자점 쌍 전부에서 T_merge 가 오르면 "
    "false_merge_rate 는 증가하지 않고 ask_user(identity) 발생률은 감소하지 "
    "않는다(비엄격 단조, D10). 양 끝점 비교가 아니다 -- 02-plan-verify R-7(1)."
)


# ---------------------------------------------------------------------------
# 작은 도구
# ---------------------------------------------------------------------------


def _mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CurveError(f"{where}: object expected (got {type(value).__name__})")
    return value


def _rate_of(block: Any, where: str) -> float | None:
    """`{"n","d","rate"}` 에서 `rate` 를 꺼낸다. 모양이 아니면 멈춘다."""

    mapping = _mapping(block, where)
    for key in ("n", "d", "rate"):
        if key not in mapping:
            raise CurveError(f"{where}: missing '{key}' (비율은 n·d 와 함께만 낸다)")
    rate = mapping["rate"]
    if rate is None:
        return None
    return float(rate)


def _series_block(point: Mapping[str, Any], series: str, where: str) -> Mapping[str, Any]:
    if series == "ask_user_identity_rate":
        by_kind = _mapping(point.get("ask_user_rate_by_kind"), f"{where}.ask_user_rate_by_kind")
        block = by_kind.get("identity")
        if block is None:
            raise CurveError(f"{where}.ask_user_rate_by_kind: missing 'identity'")
        return _mapping(block, f"{where}.ask_user_rate_by_kind.identity")
    block = point.get(series)
    if block is None:
        raise CurveError(f"{where}: missing '{series}'")
    return _mapping(block, f"{where}.{series}")


def _methods_block(metrics: Mapping[str, Any]) -> Mapping[str, Any]:
    """두 모양을 다 받는다 -- U2 `compute_metrics()` 결과(`{"methods": …}`)와
    `metrics.json` 문서(방식이 **최상위** 키, 비-방식 키는 `meta`·`gate` 둘)."""

    mapping = _mapping(metrics, "metrics")
    inner = mapping.get("methods")
    if isinstance(inner, Mapping):
        return inner
    methods = {
        name: block for name, block in mapping.items() if name not in RESERVED_TOP_KEYS
    }
    if not methods:
        raise CurveError("metrics: no method blocks")
    return methods


def _ordered_methods(metrics: Mapping[str, Any]) -> list[str]:
    """`RESOLVERS` 등록 순서(P3-baselines 인계 4). U2 가 이미 그 순서로
    담았으므로 키 순서를 그대로 쓰되, 표를 읽을 수 있으면 한 번 더 맞춘다."""

    names = list(_methods_block(metrics))
    # metrics.py 와 같은 함수를 쓴다 -- 순서 규칙이 두 벌이 되지 않게.
    return _metrics._canonical_method_order(names)


# ---------------------------------------------------------------------------
# 곡선
# ---------------------------------------------------------------------------


def curve_rows(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    """`metrics`(U2 `compute_metrics()` 결과 또는 `metrics.json` 문서) →
    곡선 행 목록. 방식(등록 순서) × `T_merge`(오름차순) × 계열(3) 순서다.

    한 행 = `{method, t_merge, t_new, series, n, d, rate}`. `rate` 는 분모 0
    이면 `None` 이고, CSV 에서는 빈 칸이 된다.
    """

    methods = _ordered_methods(metrics)
    rows: list[dict[str, Any]] = []
    for method in methods:
        block = _mapping(_methods_block(metrics)[method], f"methods.{method}")
        by_t = _mapping(block.get("by_t_merge"), f"methods.{method}.by_t_merge")
        for key in sorted(by_t, key=lambda k: float(format_t_merge(k))):
            t_key = format_t_merge(key)
            point = _mapping(by_t[key], f"methods.{method}.by_t_merge[{t_key}]")
            t_new = float(point.get("t_new", T_NEW))
            for series in SERIES:
                value = _series_block(
                    point, series, f"methods.{method}.by_t_merge[{t_key}]"
                )
                rows.append(
                    {
                        "method": method,
                        "t_merge": float(t_key),
                        "t_new": t_new,
                        "series": series,
                        "n": int(value["n"]),
                        "d": int(value["d"]),
                        "rate": None if value["rate"] is None else float(value["rate"]),
                    }
                )
    return rows


def write_curve_csv(path: Path | str, rows: Sequence[Mapping[str, Any]]) -> int:
    """`reports/curve.csv` 를 쓴다(열 = `CURVE_COLUMNS`). 줄바꿈을 `\\n` 으로
    고정해 같은 입력이면 바이트가 같다. 반환값은 데이터 행 수."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(CURVE_COLUMNS)
        for row in rows:
            writer.writerow(
                [
                    row["method"],
                    f"{float(row['t_merge']):g}",
                    f"{float(row['t_new']):g}",
                    row["series"],
                    int(row["n"]),
                    int(row["d"]),
                    "" if row["rate"] is None else repr(float(row["rate"])),
                ]
            )
    return len(rows)


def forced_reason_summary(metrics: Mapping[str, Any]) -> dict[str, Any]:
    """강제 경로(`forced_reason != null`)를 곡선 계열과 **별도로** 집계한다
    (P3-er §7). 값은 U2 `point["forced_reason"]` 분포를 그대로 읽은 것이고,
    `none` 은 강제가 아니므로 분자에서 뺀다."""

    out: dict[str, Any] = {}
    for method in _ordered_methods(metrics):
        block = _mapping(_methods_block(metrics)[method], f"methods.{method}")
        by_t = _mapping(block.get("by_t_merge"), f"methods.{method}.by_t_merge")
        per_t: dict[str, Any] = {}
        for key in sorted(by_t, key=lambda k: float(format_t_merge(k))):
            t_key = format_t_merge(key)
            point = _mapping(by_t[key], f"methods.{method}.by_t_merge[{t_key}]")
            counts = dict(_mapping(point.get("forced_reason", {}), "forced_reason"))
            total_rows = sum(int(v) for v in counts.values())
            forced = {name: int(v) for name, v in sorted(counts.items()) if name != "none"}
            per_t[t_key] = {
                "counts": forced,
                "rate": _metrics.ratio(sum(forced.values()), total_rows),
            }
        out[method] = per_t
    return out


# ---------------------------------------------------------------------------
# 게이트 (결정 K)
# ---------------------------------------------------------------------------


def _gate_point(metrics: Mapping[str, Any], method: str) -> Mapping[str, Any]:
    block = _mapping(_methods_block(metrics)[method], f"methods.{method}")
    by_t = _mapping(block.get("by_t_merge"), f"methods.{method}.by_t_merge")
    for key in by_t:
        if format_t_merge(key) == GATE_T_MERGE:
            return _mapping(by_t[key], f"methods.{method}.by_t_merge[{GATE_T_MERGE}]")
    raise CurveError(
        f"method {method!r} has no point at T_merge={GATE_T_MERGE} "
        "-- 결정 K 는 이 한 점에서 판정한다(01-plan 227행)"
    )


def _axes(point: Mapping[str, Any], where: str) -> dict[str, Any]:
    return {
        "false_merge_rate": dict(_mapping(point["false_merge_rate"], where)),
        "miss_rate": dict(_mapping(point["miss_rate"], where)),
    }


def build_gate(metrics: Mapping[str, Any]) -> dict[str, Any]:
    """결정 K(지배 기준)로 게이트를 판정한다.

    `T_merge = 0.8` 한 점의 오병합률·미검출률만 본다. 판정에 쓰는 수치는
    전부 같은 파일 안에 남아서 04-review 가 독립 재계산할 수 있다(O-4).
    """

    methods = _ordered_methods(metrics)
    if PROPOSED not in methods:
        raise CurveError(f"metrics has no {PROPOSED!r} method -- 게이트를 판정할 수 없다")
    baseline_names = [name for name in methods if name != PROPOSED]

    proposed_point = _gate_point(metrics, PROPOSED)
    proposed_axes = _axes(proposed_point, f"{PROPOSED}@{GATE_T_MERGE}")
    p_fm = _rate_of(proposed_axes["false_merge_rate"], "gate.proposed.false_merge_rate")
    p_miss = _rate_of(proposed_axes["miss_rate"], "gate.proposed.miss_rate")

    reasons: list[str] = []
    if p_fm is None:
        reasons.append("proposed.false_merge_rate.rate is null (분모 0 -- 비교 불가)")
    if p_miss is None:
        reasons.append("proposed.miss_rate.rate is null (분모 0 -- 비교 불가)")

    baselines: dict[str, Any] = {}
    dominated_by: list[str] = []
    undetermined: list[str] = []
    for name in baseline_names:
        axes = _axes(_gate_point(metrics, name), f"{name}@{GATE_T_MERGE}")
        b_fm = _rate_of(axes["false_merge_rate"], f"gate.baselines.{name}.false_merge_rate")
        b_miss = _rate_of(axes["miss_rate"], f"gate.baselines.{name}.miss_rate")
        if None in (b_fm, b_miss, p_fm, p_miss):
            dominates: bool | None = None
            undetermined.append(name)
            reasons.append(f"baseline {name}: rate is null -- 지배 여부를 정할 수 없다")
        else:
            fm_le = b_fm <= p_fm + _EPS
            miss_le = b_miss <= p_miss + _EPS
            strict = (b_fm < p_fm - _EPS) or (b_miss < p_miss - _EPS)
            dominates = bool(fm_le and miss_le and strict)
            if dominates:
                dominated_by.append(name)
        axes["dominates_proposed"] = dominates
        baselines[name] = axes

    direction = _d10_direction(metrics)
    if direction["reason"]:
        reasons.append(direction["reason"])

    ranking: list[dict[str, Any]] = []
    entries = []
    for index, name in enumerate(methods):
        block = dict(
            _mapping(
                _gate_point(metrics, name)["false_merge_rate"],
                f"{name}.false_merge_rate",
            )
        )
        entries.append((block["rate"] is None, block["rate"] or 0.0, index, name, block))
    for rank, (_null, _rate, _index, name, block) in enumerate(sorted(entries), start=1):
        ranking.append({"rank": rank, "method": name, "false_merge_rate": block})

    passed = (
        not dominated_by
        and bool(direction["ok"])
        and not reasons
    )
    return {
        "t_merge": float(GATE_T_MERGE),
        "t_merge_key": GATE_T_MERGE,
        "t_new": T_NEW,
        "rule": DOMINANCE_RULE,
        "d10_rule": D10_RULE,
        "proposed": proposed_axes,
        "baselines": baselines,
        "dominated_by": dominated_by,
        "undetermined": undetermined,
        "false_merge_ranking": ranking,
        "d10_direction": bool(direction["ok"]),
        "d10_detail": {
            "pairs": direction["pairs"],
            "violations": direction["violations"],
        },
        "pass": bool(passed),
        "reason": "; ".join(reasons) if reasons else None,
    }


def _d10_direction(metrics: Mapping[str, Any]) -> dict[str, Any]:
    """제안 방식 곡선의 **연속 격자점 쌍 전부**를 본다(R-7(1))."""

    block = _mapping(_methods_block(metrics)[PROPOSED], f"methods.{PROPOSED}")
    by_t = _mapping(block.get("by_t_merge"), f"methods.{PROPOSED}.by_t_merge")
    keys = sorted((format_t_merge(key) for key in by_t), key=float)
    lookup = {format_t_merge(key): by_t[key] for key in by_t}

    violations: list[dict[str, Any]] = []
    nulls: list[str] = []
    pairs = 0
    for lower, upper in zip(keys, keys[1:]):
        pairs += 1
        a = _mapping(lookup[lower], f"{PROPOSED}[{lower}]")
        b = _mapping(lookup[upper], f"{PROPOSED}[{upper}]")
        a_fm = _rate_of(a["false_merge_rate"], f"{PROPOSED}[{lower}].false_merge_rate")
        b_fm = _rate_of(b["false_merge_rate"], f"{PROPOSED}[{upper}].false_merge_rate")
        a_id = _rate_of(
            _series_block(a, "ask_user_identity_rate", f"{PROPOSED}[{lower}]"),
            f"{PROPOSED}[{lower}].ask_user identity",
        )
        b_id = _rate_of(
            _series_block(b, "ask_user_identity_rate", f"{PROPOSED}[{upper}]"),
            f"{PROPOSED}[{upper}].ask_user identity",
        )
        if None in (a_fm, b_fm, a_id, b_id):
            nulls.append(f"{lower}->{upper}")
            continue
        if b_fm > a_fm + _EPS:
            violations.append(
                {
                    "pair": [float(lower), float(upper)],
                    "axis": "false_merge_rate",
                    "from": a_fm,
                    "to": b_fm,
                }
            )
        if b_id < a_id - _EPS:
            violations.append(
                {
                    "pair": [float(lower), float(upper)],
                    "axis": "ask_user_identity_rate",
                    "from": a_id,
                    "to": b_id,
                }
            )

    reason = ""
    if nulls:
        reason = (
            f"d10_direction: rate is null on pair(s) {nulls} "
            "-- 단조 여부를 정할 수 없다"
        )
    ok = not violations and not nulls
    return {"ok": ok, "pairs": pairs, "violations": violations, "reason": reason}


# ---------------------------------------------------------------------------
# metrics.json 조립
# ---------------------------------------------------------------------------


def _weights_block() -> dict[str, Any]:
    """확신도 가중치(원칙3). `ERConfig` **모듈 기본값**을 읽고 환경변수는
    읽지 않는다 -- 실행 환경이 달라도 같은 JSONL 이면 같은 파일이 나와야
    한다(원칙8). 실행 시 주입된 값이 달랐다면 그것은 러너 evidence 의 몫이다."""

    from app.er.types import ERConfig  # 지연 import -- 이 모듈 자체는 app 없이 읽힌다

    config = ERConfig()
    return {
        "llm": config.w_llm,
        "emb": config.w_emb,
        "rule": config.w_rule,
        "source": (
            "app.er.types.ERConfig() 모듈 기본값(0.5·0.3·0.2, D3). W_LLM/W_EMB/"
            "W_RULE 환경변수를 읽지 않는다 -- 같은 JSONL 이면 같은 metrics.json."
        ),
    }


def _provider_model(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """실행 정체. 출처는 U3 보정표와 **같다**(`detail["provider"]`·
    `detail["model"]` = 판정이 돌려준 값). `s_llm` 을 내는 방식만 이 값을
    남기므로, 없으면 `None` 이고 관측 목록은 빈 리스트다."""

    seen: dict[tuple[str, str, str], int] = {}
    for row in mention_level_rows(rows):
        detail = row.get("detail") or {}
        if not isinstance(detail, Mapping):
            continue
        provider = detail.get("provider")
        model = detail.get("model")
        if not isinstance(provider, str) or not provider:
            continue
        if not isinstance(model, str) or not model:
            continue
        key = (str(row["method"]), provider, model)
        seen[key] = seen.get(key, 0) + 1

    observed = [
        {"method": method, "provider": provider, "model": model, "mentions": count}
        for (method, provider, model), count in sorted(seen.items())
    ]
    providers = sorted({entry["provider"] for entry in observed})
    models = sorted({entry["model"] for entry in observed})
    return {
        "provider": providers[0] if len(providers) == 1 else None,
        "model": models[0] if len(models) == 1 else None,
        "providers_observed": providers,
        "models_observed": models,
        "provider_model_observed": observed,
    }


def build_metrics_document(
    rows: Iterable[Mapping[str, Any]],
    *,
    metrics: Mapping[str, Any] | None = None,
    embedding_model: str | None = None,
    dataset_hash: str | None = None,
    run_id: str | None = None,
    model_configured: Mapping[str, str] | None = None,
    commit: str | None = None,
    run_mode: str | None = None,
) -> dict[str, Any]:
    """U1 JSONL 행 → `reports/metrics.json` 문서.

    `metrics` 를 주면 U2 계산을 건너뛴다(같은 행으로 이미 계산했을 때).
    지표는 여기서 다시 계산하지 않고 그대로 옮긴다.
    """

    row_list = [dict(row) for row in rows]
    if not row_list:
        raise CurveError("no rows")
    computed = dict(metrics) if metrics is not None else compute_metrics(row_list)

    methods_block = _methods_block(computed)
    ordered = _ordered_methods(computed)
    base_meta = dict(_mapping(computed.get("meta"), "metrics.meta"))

    t_new = float(base_meta.get("t_new", T_NEW))
    if abs(t_new - T_NEW) > _EPS:
        raise CurveError(
            f"t_new must stay fixed at {T_NEW} (got {t_new}) -- S3.7 §4 x 축은 T_merge 하나"
        )

    document: dict[str, Any] = {}
    for method in ordered:
        document[method] = json.loads(json.dumps(methods_block[method], ensure_ascii=False))

    identity = _provider_model(row_list)
    meta = dict(base_meta)
    meta.update(
        {
            "schema_version": METRICS_SCHEMA_VERSION,
            "provider": identity["provider"],
            "model": identity["model"],
            "model_source": (
                "detail['model'] -- 판정이 돌려준 모델명(U3 보정표와 같은 출처). "
                "설정 문자열은 meta.model_configured."
            ),
            "providers_observed": identity["providers_observed"],
            "models_observed": identity["models_observed"],
            "provider_model_observed": identity["provider_model_observed"],
            "model_configured": dict(model_configured or {}),
            "embedding_model": embedding_model,
            "dataset_hash": dataset_hash,
            "run_id": run_id,
            "commit": commit,
            "run_mode": run_mode,
            "caller_supplied": [
                "embedding_model",
                "dataset_hash",
                "run_id",
                "model_configured",
                "commit",
                "run_mode",
            ],
            "caller_supplied_note": (
                "JSONL 에 없는 값이라 호출자(U6·U7)가 넘긴다. 이 모듈은 "
                "환경변수·.env·네트워크를 읽지 않는다(원칙8, security §1)."
            ),
            "t_new": t_new,
            "t_new_fixed": True,
            "top_k_swept": False,
            "top_k_swept_note": (
                "결정 H(i)·F-bdd6c5 -- search_person 의 top_k 는 스윕하지 않는다. "
                "x 축은 T_merge 하나다."
            ),
            "weights": _weights_block(),
            "curve": {
                "x_axis": "t_merge",
                "series": list(SERIES),
                "series_source": {
                    "false_merge_rate": "point.false_merge_rate",
                    "ask_user_identity_rate": "point.ask_user_rate_by_kind.identity",
                    "miss_rate": "point.miss_rate",
                },
                "csv_columns": list(CURVE_COLUMNS),
                "point_count": len(ordered) * len(base_meta.get("grid", [])) * len(SERIES),
                "forced_reason_note": (
                    "forced_reason != null 행은 계열과 별도 집계다(meta.forced_reason, "
                    "P3-er §7) -- 강제 경로는 임계치와 무관하게 밴드가 정해진다."
                ),
            },
            "forced_reason": forced_reason_summary(computed),
        }
    )
    document["meta"] = meta
    document["gate"] = build_gate(computed)
    return document


# ---------------------------------------------------------------------------
# 스키마 검증 (`python -m evaluation.metrics --validate <metrics.json>`)
# ---------------------------------------------------------------------------


def _check_ratio(block: Any, where: str, problems: list[str]) -> None:
    if not isinstance(block, Mapping):
        problems.append(f"{where}: object expected (got {type(block).__name__})")
        return
    if set(block) != {"n", "d", "rate"}:
        problems.append(
            f"{where}: keys must be exactly n·d·rate (got {sorted(map(str, block))})"
        )
        return
    n, d, rate = block["n"], block["d"], block["rate"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        problems.append(f"{where}.n: non-negative int expected (got {n!r})")
        return
    if isinstance(d, bool) or not isinstance(d, int) or d < 0:
        problems.append(f"{where}.d: non-negative int expected (got {d!r})")
        return
    if d == 0:
        if rate is not None:
            problems.append(f"{where}.rate: d=0 must give null (got {rate!r})")
        return
    if not isinstance(rate, (int, float)) or isinstance(rate, bool):
        problems.append(f"{where}.rate: number expected when d>0 (got {rate!r})")
        return
    if abs(float(rate) - n / d) > 1e-9:
        problems.append(f"{where}.rate: {rate!r} != n/d ({n}/{d})")


def validate_metrics_document(doc: Any) -> list[str]:
    """`metrics.json` 문서를 검사하고 **문제 목록**을 돌려준다(빈 목록 = 통과).

    보는 것: 방식 키 5개와 순서 · `meta` 필수 키와 `denominator_rule` ·
    격자 10점 · `t_new` 0.3 · `top_k_swept` false · `gate` 필수 키와 베이스라인
    4키 · `pass` 재계산 일치 · 모든 비율의 `{"n","d","rate"}` 형식.
    """

    problems: list[str] = []
    if not isinstance(doc, Mapping):
        return [f"document: object expected (got {type(doc).__name__})"]

    for key in RESERVED_TOP_KEYS:
        if key not in doc:
            problems.append(f"document: missing top-level {key!r}")

    method_keys = [key for key in doc if key not in RESERVED_TOP_KEYS]
    if len(method_keys) != 5:
        problems.append(
            f"document: expected 5 method keys, got {len(method_keys)} ({method_keys})"
        )
    canonical = _metrics._canonical_method_order(method_keys)
    if method_keys != canonical:
        problems.append(
            f"document: method key order must be RESOLVERS order {canonical} (got {method_keys})"
        )

    meta = doc.get("meta")
    if not isinstance(meta, Mapping):
        problems.append("meta: object expected")
        meta = {}
    else:
        missing = [key for key in _META_REQUIRED_KEYS if key not in meta]
        if missing:
            problems.append(f"meta: missing key(s) {missing}")
        rule = meta.get("denominator_rule")
        if not isinstance(rule, Mapping) or not rule:
            problems.append("meta.denominator_rule: non-empty object expected")
        if meta.get("top_k_swept") is not False:
            problems.append(
                f"meta.top_k_swept: must be false (결정 H, got {meta.get('top_k_swept')!r})"
            )
        t_new = meta.get("t_new")
        if not isinstance(t_new, (int, float)) or isinstance(t_new, bool):
            problems.append(f"meta.t_new: number expected (got {t_new!r})")
        elif abs(float(t_new) - T_NEW) > _EPS:
            problems.append(f"meta.t_new: must be {T_NEW} (got {t_new!r})")
        grid = meta.get("grid")
        if not isinstance(grid, list):
            problems.append(f"meta.grid: list expected (got {type(grid).__name__})")
        elif len(grid) != len(EXPECTED_GRID) or any(
            abs(float(a) - b) > _EPS for a, b in zip(grid, EXPECTED_GRID)
        ):
            problems.append(
                f"meta.grid: must be the 10-point grid {list(EXPECTED_GRID)} (got {grid})"
            )
        methods_meta = meta.get("methods")
        if methods_meta != method_keys:
            problems.append(
                f"meta.methods {methods_meta!r} disagrees with method keys {method_keys!r}"
            )

    grid_keys: list[str] = []
    meta_grid = meta.get("grid") if isinstance(meta, Mapping) else None
    if isinstance(meta_grid, list):
        try:
            grid_keys = [format_t_merge(value) for value in meta_grid]
        except MetricsError as exc:
            problems.append(f"meta.grid: {exc}")

    for method in method_keys:
        block = doc[method]
        if not isinstance(block, Mapping):
            problems.append(f"{method}: object expected")
            continue
        by_t = block.get("by_t_merge")
        if not isinstance(by_t, Mapping):
            problems.append(f"{method}.by_t_merge: object expected")
            continue
        if grid_keys and sorted(by_t, key=str) != sorted(grid_keys, key=str):
            problems.append(
                f"{method}.by_t_merge: keys {sorted(by_t, key=str)} != grid {sorted(grid_keys, key=str)}"
            )
        for key in sorted(by_t, key=str):
            point = by_t[key]
            where = f"{method}.by_t_merge[{key}]"
            if not isinstance(point, Mapping):
                problems.append(f"{where}: object expected")
                continue
            _check_ratio(point.get("false_merge_rate"), f"{where}.false_merge_rate", problems)
            _check_ratio(point.get("miss_rate"), f"{where}.miss_rate", problems)
            by_kind = point.get("ask_user_rate_by_kind")
            if not isinstance(by_kind, Mapping):
                problems.append(f"{where}.ask_user_rate_by_kind: object expected")
            else:
                _check_ratio(
                    by_kind.get("identity"),
                    f"{where}.ask_user_rate_by_kind.identity",
                    problems,
                )
            point_t_new = point.get("t_new")
            if isinstance(point_t_new, (int, float)) and not isinstance(point_t_new, bool):
                if abs(float(point_t_new) - T_NEW) > _EPS:
                    problems.append(f"{where}.t_new: must be {T_NEW} (got {point_t_new!r})")
            else:
                problems.append(f"{where}.t_new: number expected (got {point_t_new!r})")

    gate = doc.get("gate")
    if not isinstance(gate, Mapping):
        problems.append("gate: object expected")
        return problems

    missing_gate = [key for key in _GATE_REQUIRED_KEYS if key not in gate]
    if missing_gate:
        problems.append(f"gate: missing key(s) {missing_gate}")
    t_merge = gate.get("t_merge")
    if not isinstance(t_merge, (int, float)) or isinstance(t_merge, bool):
        problems.append(f"gate.t_merge: number expected (got {t_merge!r})")
    elif abs(float(t_merge) - float(GATE_T_MERGE)) > _EPS:
        problems.append(f"gate.t_merge: must be {GATE_T_MERGE} (got {t_merge!r})")

    proposed = gate.get("proposed")
    if not isinstance(proposed, Mapping):
        problems.append("gate.proposed: object expected")
    else:
        _check_ratio(proposed.get("false_merge_rate"), "gate.proposed.false_merge_rate", problems)
        _check_ratio(proposed.get("miss_rate"), "gate.proposed.miss_rate", problems)

    baselines = gate.get("baselines")
    expected_baselines = sorted(name for name in method_keys if name != PROPOSED)
    if not isinstance(baselines, Mapping):
        problems.append("gate.baselines: object expected")
    else:
        if sorted(map(str, baselines)) != expected_baselines:
            problems.append(
                f"gate.baselines: keys must be RESOLVERS − proposed {expected_baselines} "
                f"(got {sorted(map(str, baselines))})"
            )
        for name in sorted(map(str, baselines)):
            block = baselines[name]
            if not isinstance(block, Mapping):
                problems.append(f"gate.baselines.{name}: object expected")
                continue
            _check_ratio(
                block.get("false_merge_rate"),
                f"gate.baselines.{name}.false_merge_rate",
                problems,
            )
            _check_ratio(block.get("miss_rate"), f"gate.baselines.{name}.miss_rate", problems)

    dominated = gate.get("dominated_by")
    if not isinstance(dominated, list) or any(not isinstance(x, str) for x in dominated):
        problems.append(f"gate.dominated_by: list of method names expected (got {dominated!r})")
        dominated = []
    else:
        unknown = [name for name in dominated if name not in expected_baselines]
        if unknown:
            problems.append(f"gate.dominated_by: unknown baseline(s) {unknown}")

    direction = gate.get("d10_direction")
    if not isinstance(direction, bool):
        problems.append(f"gate.d10_direction: bool expected (got {direction!r})")
    passed = gate.get("pass")
    if not isinstance(passed, bool):
        problems.append(f"gate.pass: bool expected (got {passed!r})")
    if isinstance(direction, bool) and isinstance(passed, bool):
        reason = gate.get("reason")
        expected_pass = (not dominated) and direction and not reason
        if passed != expected_pass:
            problems.append(
                f"gate.pass: {passed} disagrees with (dominated_by == [] and d10_direction "
                f"and reason is null) = {expected_pass} (결정 K)"
            )
        if not passed and not reason and (not dominated) and direction:
            problems.append("gate.pass: false without reason (조용히 미달로 두지 않는다)")

    return problems


# ---------------------------------------------------------------------------
# CLI (JSONL -> metrics.json + curve.csv. 파일을 읽고 쓰는 것 말고는 하지 않는다)
# ---------------------------------------------------------------------------


def _parse_model_configured(values: Sequence[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in values or []:
        provider, _, model = item.partition("=")
        if not provider.strip() or not model.strip():
            raise CurveError(f"--model-configured expects provider=model (got {item!r})")
        out[provider.strip()] = model.strip()
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.curve",
        description="U1 파일럿 러너 JSONL -> metrics.json + curve.csv (DB·네트워크 없음)",
    )
    parser.add_argument("--rows", required=True, help="U1 러너가 쓴 JSONL 경로")
    parser.add_argument("--out", default=None, help="metrics.json 경로(생략하면 표준출력)")
    parser.add_argument("--curve", default=None, help="curve.csv 경로(생략하면 쓰지 않는다)")
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--dataset-hash", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--commit",
        default=None,
        help="평가한 커밋 해시(L-001). meta.commit 에 그대로 적는다(생략하면 null)",
    )
    parser.add_argument(
        "--run-mode",
        default=None,
        choices=("stub", "real"),
        help="meta.run_mode -- 스텁 실행인지 실 공급자 실행인지(생략하면 null)",
    )
    parser.add_argument(
        "--model-configured",
        action="append",
        default=None,
        help="설정 문자열(provider=model). meta.model_configured 에 그대로 적는다",
    )
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)

    rows = load_rows(args.rows)
    document = build_metrics_document(
        rows,
        embedding_model=args.embedding_model,
        dataset_hash=args.dataset_hash,
        run_id=args.run_id,
        model_configured=_parse_model_configured(args.model_configured),
        commit=args.commit,
        run_mode=args.run_mode,
    )
    text = json.dumps(document, ensure_ascii=False, indent=args.indent)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.curve:
        write_curve_csv(args.curve, curve_rows(document))
    return 0


if __name__ == "__main__":  # pragma: no cover -- CLI 진입점
    raise SystemExit(main())
