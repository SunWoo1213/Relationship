"""Refs: P4-pilot-eval R4 D3 원칙3 원칙9 -- `s_llm` 구간별 실제 정답률(보정표).

01-plan U3(67행). **입력은 U1 러너가 쓴 JSONL 한 파일뿐이다** -- DB·네트워크·
LLM 을 부르지 않고 `app/` 도 부르지 않는다. 같은 JSONL 을 넣으면 언제나 같은
파일이 나온다(원칙8). 산출은 `reports/calibration.json` 의 내용이고, 실물
파일은 U7(실 공급자 1회 실행)이 만든다.

## 왜 이 표가 필요한가 (R4)

`confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`(D3)의 `s_llm` 은 LLM 이
구조화 출력으로 **자기보고한** 0~1 점수다(로그 확률이 아니다 -- 원칙3).
자기보고 점수를 가중합의 절반으로 쓰려면 "0.9 라고 말했을 때 실제로 몇 %나
맞았는가"를 보여야 한다. 이 표가 그 근거다(`D03-confidence-formula.md`
**보정** 줄).

## 구간 10칸과 경계값 (`BINS`)

폭 0.1 로 10칸. **왼쪽 닫힘·오른쪽 열림 `[lo, hi)`**, 마지막 칸만 오른쪽도
닫힌다 `[0.9, 1.0]` -- 그래야 `1.0` 이 어디에도 안 들어가는 일이 없다.

| 값 | 칸 | 이유 |
|----|----|------|
| `0.0` | `0.0-0.1` | 왼쪽 닫힘 |
| `0.1` | `0.1-0.2` | 경계값은 **위쪽** 칸 |
| `0.8` | `0.8-0.9` | 경계값은 위쪽 칸(= `T_merge` 기본값과 같은 수지만 임계치와 무관하다) |
| `1.0` | `0.9-1.0` | 마지막 칸만 오른쪽 닫힘 |

비교는 파이썬 float 비교 그대로다(`value >= lo`). 반올림·보정을 하지 않으므로
JSON 에 `0.8` 로 적힌 값은 언제나 `0.8-0.9` 칸이다. 분모가 0 인 칸은
`accuracy: null` 이다 -- 0.0 으로 적으면 "재 보니 0%" 와 "잴 수 없었다" 가
구별되지 않는다(원칙8, `evaluation/metrics.py::ratio` 와 같은 자세).

## 그룹 키 = (방식, `provider`, `model`)

- **방식**은 `s_llm` 을 실제로 내는 둘뿐이다(`S_LLM_METHODS`). `exact_raw`·
  `exact_norm`·`embedding_only` 는 LLM 을 부르지 않으므로 이 파일에 없다.
- `model` 은 **판정이 돌려준 값**(`Judgement.model` -> `detail["model"]`)이다.
  설정 문자열(`OPENAI_MODEL` 등)은 `meta.model_configured` 에 따로 적는다 --
  Gemini 는 `response.model_version` 이 설정값과 다를 수 있다(P3-llm-providers
  §7 인계 4, 02-plan-verify R-6). 설정값은 JSONL 에 없으므로 호출자가
  `--model-configured openai=gpt-4o-mini` 로 넘긴 값을 **그대로** 적는다
  (환경변수를 여기서 읽지 않는다 -- 읽으면 같은 입력이 같은 출력을 내지
  않는다).

## `s_llm` 을 어디서 읽는가

| 방식 | 값 | 자기보고가 아닌 경우(placeholder) |
|------|----|-----------------------------------|
| `proposed` | `detail["confidence_breakdown"]["s_llm"]`(D3 분해) | 같은 분해의 `matched_person_id` 가 `None` |
| `llm_single` | `MentionDecision.score`(= 접힌 `s_llm`), `candidates[].signals["s_llm"]` 와 대조 | `detail["raw_decision"]` 가 `None`(응답 파싱 전 결정) |

`app/er/confidence.py::_forced_decision` 은 강제 경로(`no_matched`·
`llm_failed`·`out_of_range_id`)에서 `s_llm=s_emb=s_rule=0` **귀속 규약**을
쓴다. 그 `0.0` 은 LLM 이 "0.0 이다"라고 말한 것이 아니라 자리를 채운 값이다.
그대로 세면 `0.0-0.1` 칸이 placeholder 로 오염돼 보정표가 거짓말을 한다.
그래서 **`confidence_breakdown["matched_person_id"] is None` 인 행은 세지 않고
`placeholder_s_llm` 으로 따로 센다**(01-plan 67행이 명시한 세 제외에 더한
넷째 -- 숨기지 않고 수를 남긴다, 원칙8). `llm_single` 도 같은 이유로
`raw_decision is None`(호출·파싱 실패로 `score=0.0` 이 놓인 행)을 뺀다.

> 한계: 강제 경로에서 LLM 이 **실제로 보고한** `s_llm` 은 `app/er` 이
> 기록하지 않아(pipeline 의 `llm["s_llm"]` 은 `detail` 로 나오지 않는다)
> 이 표가 그 구간을 볼 수 없다. `app/` 무수정이 이 패키지의 제약이므로
> 수치를 만들지 않고 제외 수만 남긴다(U8·P10 이 다룬다).

## 분모에서 빼는 것 (`EXCLUSION_REASONS`, 우선순위 순)

1. `passing_mention` -- 등록하면 안 되는 지나가는 언급(골드 없음, U2 분모 규칙 2)
2. `ambiguous_mention` -- 사람도 선행사를 못 정하는 mention(U2 분모 규칙 1)
3. `llm_error` -- `timeout/rate_limit/api_error/connection/schema/out_of_range_id`
   (어휘는 `app/er` · `llm_single`). 종류별로 센다
4. `llm_skipped` -- 통과 후보 0 이라 호출 자체가 없었다(`proposed`
   `detail["llm_skipped"]`, `llm_single` `detail["llm_calls"] == 0`)
5. `score_clamped` -- `detail["score_clamped"] == True`(P3-baselines 04-review
   [권고] 2). `llm_single` 은 `[0,1]` 밖 자기보고를 접고, `proposed` 는 결합
   확신도를 접는다 -- **접힌 행의 눈금은 신뢰할 수 없으므로 양쪽 다 뺀다**
6. `placeholder_s_llm` -- 위 표의 placeholder

빠진 수는 그룹마다(`groups[].excluded`) 와 파일 전체(`excluded`)에 남고,
`excluded_clamped` 는 판정 표 100행이 읽는 최상위 정수다.

## 한 mention = 한 줄 (격자 사본 중복 금지)

러너는 mention × 방식마다 `T_merge` 10점을 돌려 10행을 쓰지만 LLM 응답은
**mention 당 1회**뿐이다(결정 C(i)). 같은 자기보고 점수를 10번 세면 표가
10배로 불어난다. 그래서 단위는 **(방식, 시나리오, mention) 하나에 한 행**이고,
기본은 `mention_level_rows()`(= `sweep_index` 최소 행 = `llm_fresh_call` 행)를
쓴다. `--t-merge` 를 주면 그 임계치의 행으로 채점한다(어느 임계치에서
채점했는지는 `meta.scored_at_t_merge`). 한 mention 에 실제 호출이 2회 이상
기록되면(`llm_fresh_call` 행 2개 이상) 기억 래퍼가 깨진 것이므로 멈춘다.

## "정답"의 정의 (결정 F(i))

**그 판정의 `decision` 과 `person_id` 가 골드와 일치하는가.** 코드로는
`evaluation.metrics.classify_gold_row(row) in {"merge_correct",
"new_person_correct"}` 하나다(U2 채점표 재사용 -- 두 모듈이 다른 정답을 쓰면
metrics.json 과 calibration.json 이 어긋난다). 같은 문장이
`meta.correct_definition` 으로 파일에도 들어간다.

## 하지 않는 것

곡선·`metrics.json` 조립(U4), 리포트(U5), 실행 CLI·비용 가드(U6),
`reports/calibration.json` **실물 생성**(U7).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from evaluation.metrics import (
    MetricsError,
    classify_gold_row,
    format_t_merge,
    load_rows,
    mention_level_rows,
    validate_rows,
)

__all__ = [
    "BINS",
    "BIN_LABELS",
    "BIN_RULE",
    "BIN_WIDTH",
    "CORRECT_DEFINITION",
    "EXCLUSION_REASONS",
    "S_LLM_METHODS",
    "CalibrationError",
    "bin_index",
    "bin_label",
    "compute_calibration",
    "empty_bins",
    "main",
    "s_llm_status",
]


class CalibrationError(MetricsError):
    """보정표 입력이 계약을 어겼다. 조용히 건너뛰지 않는다(원칙8).

    `MetricsError` 를 물려받는다 -- 같은 JSONL 계약을 공유하므로 호출자가
    예외 하나만 잡으면 된다."""


#: `s_llm` 을 실제로 내는 방식(01-plan 67행). 순서 = `metrics.json` 키 순서와
#: 같은 `RESOLVERS` 등록 순서. 나머지 세 방식은 LLM 을 부르지 않는다.
S_LLM_METHODS: tuple[str, ...] = ("proposed", "llm_single")

BIN_WIDTH = 0.1

#: 10칸 `[lo, hi)`, 마지막만 `[0.9, 1.0]`. 소수 곱셈(`value * 10`)은 쓰지
#: 않는다 -- `int(0.3 * 10) == 2` 라서 경계값이 아래 칸으로 샌다.
BINS: tuple[tuple[float, float], ...] = (
    (0.0, 0.1),
    (0.1, 0.2),
    (0.2, 0.3),
    (0.3, 0.4),
    (0.4, 0.5),
    (0.5, 0.6),
    (0.6, 0.7),
    (0.7, 0.8),
    (0.8, 0.9),
    (0.9, 1.0),
)

BIN_LABELS: tuple[str, ...] = tuple(f"{lo:.1f}-{hi:.1f}" for lo, hi in BINS)

BIN_RULE = (
    "폭 0.1 의 10칸. [lo, hi) 왼쪽 닫힘·오른쪽 열림이고 마지막 칸만 "
    "[0.9, 1.0] 로 오른쪽도 닫힌다. 경계값은 위쪽 칸 -- 0.1 -> '0.1-0.2', "
    "0.8 -> '0.8-0.9', 1.0 -> '0.9-1.0', 0.0 -> '0.0-0.1'. 비교는 float "
    "그대로(value >= lo)이고 반올림하지 않는다. 분모 0 인 칸은 accuracy: null."
)

CORRECT_DEFINITION = (
    "결정 F(i) -- 그 판정의 decision 과 person_id 가 골드와 일치하면 정답이다"
    "(evaluation.metrics.classify_gold_row(row) in "
    "{'merge_correct', 'new_person_correct'}, U2 채점표와 같은 함수)."
)

#: 분모에서 빠지는 이유(우선순위 순). 모듈 docstring "분모에서 빼는 것".
EXCLUSION_REASONS: tuple[str, ...] = (
    "passing_mention",
    "ambiguous_mention",
    "llm_error",
    "llm_skipped",
    "score_clamped",
    "placeholder_s_llm",
)

_COUNTED = "counted"

#: `s_llm` 을 어디서 읽는지(파일에도 적는다 -- 나중에 사람이 되짚을 근거).
S_LLM_SOURCE: dict[str, str] = {
    "proposed": (
        "detail['confidence_breakdown']['s_llm'](D3 3신호 분해). "
        "같은 분해의 matched_person_id 가 None 이면 app/er/confidence.py 의 "
        "강제 경로 귀속값(placeholder)이라 세지 않는다."
    ),
    "llm_single": (
        "MentionDecision.score(= [0,1] 로 접힌 자기보고 s_llm), "
        "candidates[].signals['s_llm'] 가 있으면 대조한다. "
        "detail['raw_decision'] 가 None 이면 응답을 파싱하기 전 결정이라 "
        "score 0.0 이 placeholder 다."
    ),
}


# ---------------------------------------------------------------------------
# 구간
# ---------------------------------------------------------------------------


def bin_index(value: float) -> int:
    """`s_llm` 값 -> 칸 번호 0~9. `[0, 1]` 밖은 오류다(접는 것은 방식 코드의
    몫이고 여기서 조용히 고치지 않는다 -- 원칙8)."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalibrationError(f"s_llm is not a number: {value!r}")
    numeric = float(value)
    if numeric != numeric:  # NaN
        raise CalibrationError("s_llm is NaN")
    if numeric < 0.0 or numeric > 1.0:
        raise CalibrationError(f"s_llm out of [0,1] range: {numeric!r}")
    for index in range(len(BINS) - 1, -1, -1):
        if numeric >= BINS[index][0]:
            return index
    raise CalibrationError(f"s_llm has no bin: {numeric!r}")  # pragma: no cover


def bin_label(value: float) -> str:
    """`s_llm` 값 -> 칸 이름(`"0.8-0.9"`)."""

    return BIN_LABELS[bin_index(value)]


def empty_bins() -> list[dict[str, Any]]:
    """10칸 뼈대. 값이 하나도 없어도 칸은 10개 그대로 나간다(수용 기준
    해석 3 -- "`s_llm` 0.1 구간 **10칸**이 있고")."""

    return [
        {
            "bin": BIN_LABELS[index],
            "index": index,
            "lo": lo,
            "hi": hi,
            "right_closed": index == len(BINS) - 1,
            "n": 0,
            "correct": 0,
            "accuracy": None,
        }
        for index, (lo, hi) in enumerate(BINS)
    ]


# ---------------------------------------------------------------------------
# 행 읽기
# ---------------------------------------------------------------------------


def _detail(row: Mapping[str, Any]) -> Mapping[str, Any]:
    detail = row["detail"]
    if not isinstance(detail, Mapping):
        raise CalibrationError(f"row detail must be an object (got {type(detail).__name__})")
    return detail


def _unit_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        str(row["method"]),
        str(row["scenario_id"]),
        str(row["mention_kind"]),
        int(row["mention_index"]),
    )


def _group_keys(row: Mapping[str, Any]) -> tuple[str | None, str | None]:
    """`(provider, model)`. 값이 없으면 `None` -- 셀 때(`counted`)만 필수다."""

    detail = _detail(row)
    provider = detail.get("provider")
    model = detail.get("model")
    provider = str(provider) if isinstance(provider, str) and provider else None
    model = str(model) if isinstance(model, str) and model else None
    return provider, model


def _candidate_s_llm(row: Mapping[str, Any]) -> float | None:
    """`llm_single` 이 고른 인물 후보에 실은 `signals["s_llm"]`(있으면)."""

    person_id = row.get("person_id")
    if person_id is None:
        return None
    candidates = row.get("candidates") or []
    if not isinstance(candidates, list):
        raise CalibrationError("row candidates must be a list")
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise CalibrationError("candidate must be an object")
        if candidate.get("person_id") != person_id:
            continue
        signals = candidate.get("signals") or {}
        if not isinstance(signals, Mapping):
            raise CalibrationError("candidate signals must be an object")
        value = signals.get("s_llm")
        return None if value is None else float(value)
    return None


def s_llm_status(row: Mapping[str, Any]) -> tuple[str, float | None, str | None]:
    """한 행 -> `(상태, s_llm, 오류종류)`.

    상태는 `"counted"` 또는 `EXCLUSION_REASONS` 의 하나다(`passing_mention`·
    `ambiguous_mention` 은 행이 아니라 mention 속성이라 호출자가 먼저 거른다).
    우선순위는 모듈 docstring 의 번호 그대로이며 **바꾸면 수치가 바뀐다** --
    재현 가능성을 위해 여기 한 곳에만 적는다.
    """

    method = str(row["method"])
    if method not in S_LLM_METHODS:
        raise CalibrationError(
            f"method {method!r} does not report s_llm (expected one of {list(S_LLM_METHODS)})"
        )
    detail = _detail(row)

    error = detail.get("llm_error")
    if error:
        return "llm_error", None, str(error)

    if method == "proposed":
        if detail.get("llm_skipped") is True:
            return "llm_skipped", None, None
        breakdown = detail.get("confidence_breakdown")
        if not isinstance(breakdown, Mapping):
            raise CalibrationError(
                "proposed row needs detail['confidence_breakdown'] (D3 3신호 분해, 원칙9)"
            )
        if "s_llm" not in breakdown:
            raise CalibrationError("confidence_breakdown has no 's_llm' (D3, 원칙3)")
        value = breakdown["s_llm"]
        placeholder = breakdown.get("matched_person_id") is None
    else:  # llm_single
        if detail.get("llm_calls") == 0:
            return "llm_skipped", None, None
        value = row["score"]
        placeholder = detail.get("raw_decision") is None
        signal = _candidate_s_llm(row)
        if (
            signal is not None
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
            and abs(signal - float(value)) > 1e-9
        ):
            raise CalibrationError(
                f"llm_single s_llm disagrees: score={value!r} vs "
                f"candidates[].signals['s_llm']={signal!r}"
            )

    bin_index(value)  # 형식·범위 검사(밖이면 여기서 멈춘다)
    numeric = float(value)

    if detail.get("score_clamped") is True:
        return "score_clamped", numeric, None
    if placeholder:
        return "placeholder_s_llm", numeric, None
    return _COUNTED, numeric, None


# ---------------------------------------------------------------------------
# 집계
# ---------------------------------------------------------------------------


def _new_excluded() -> dict[str, Any]:
    block: dict[str, Any] = {reason: 0 for reason in EXCLUSION_REASONS}
    block["llm_error_kinds"] = Counter()
    block["total"] = 0
    return block


def _add_excluded(block: dict[str, Any], reason: str, error_kind: str | None) -> None:
    block[reason] += 1
    block["total"] += 1
    if reason == "llm_error" and error_kind:
        block["llm_error_kinds"][error_kind] += 1


def _finish_excluded(block: Mapping[str, Any]) -> dict[str, Any]:
    out = {key: value for key, value in block.items() if key != "llm_error_kinds"}
    out["llm_error_kinds"] = dict(sorted(block["llm_error_kinds"].items()))
    return dict(sorted(out.items()))


def _accuracy(correct: int, n: int) -> float | None:
    return (correct / n) if n else None


def compute_calibration(
    rows: Iterable[Mapping[str, Any]],
    *,
    t_merge: Any | None = None,
    model_configured: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """U1 JSONL 행 전부 -> `reports/calibration.json` 의 내용.

    `t_merge` 를 주면 그 임계치의 행으로 채점하고, 주지 않으면 mention 마다
    `sweep_index` 가 가장 작은 행(= `llm_fresh_call` 행)으로 채점한다. 어느
    쪽이든 mention 하나는 **한 번만** 세어진다(격자 사본 중복 금지).
    """

    row_list = [dict(row) for row in rows]
    if not row_list:
        raise CalibrationError("no rows")
    validate_rows(row_list)

    target = format_t_merge(t_merge) if t_merge is not None else None
    selected = [row for row in row_list if str(row["method"]) in S_LLM_METHODS]
    ignored_method_rows = len(row_list) - len(selected)

    units: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in selected:
        units.setdefault(_unit_key(row), []).append(row)

    base_by_unit = {_unit_key(row): row for row in mention_level_rows(selected)}

    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    unassigned: dict[str, dict[str, Any]] = {}
    totals = _new_excluded()
    scored_t_merge: set[str] = set()
    counted_units = 0

    for key in sorted(units, key=lambda k: (S_LLM_METHODS.index(k[0]), k[1], k[2], k[3])):
        unit_rows = units[key]
        method = key[0]

        fresh = [row for row in unit_rows if row["llm_fresh_call"]]
        if len(fresh) > 1:
            raise CalibrationError(
                f"{key}: {len(fresh)} fresh LLM calls for one mention -- "
                "결정 C(i) 는 mention 당 1회다(러너 기억 래퍼가 깨졌다)"
            )

        if target is None:
            scored = base_by_unit[key]
        else:
            matching = [
                row for row in unit_rows if format_t_merge(row["t_merge"]) == target
            ]
            if not matching:
                raise CalibrationError(f"{key}: no row at t_merge={target}")
            scored = matching[0]
        scored_t_merge.add(format_t_merge(scored["t_merge"]))

        provider, model = _group_keys(scored)

        if scored["mention_kind"] == "passing":
            status, value, error_kind = "passing_mention", None, None
        elif scored["ambiguous"]:
            status, value, error_kind = "ambiguous_mention", None, None
        else:
            status, value, error_kind = s_llm_status(scored)

        if status != _COUNTED:
            _add_excluded(totals, status, error_kind)
            if provider is not None and model is not None:
                group = groups.setdefault(
                    (method, provider, model),
                    {
                        "method": method,
                        "provider": provider,
                        "model": model,
                        "bins": empty_bins(),
                        "excluded": _new_excluded(),
                    },
                )
                _add_excluded(group["excluded"], status, error_kind)
            else:
                block = unassigned.setdefault(method, _new_excluded())
                _add_excluded(block, status, error_kind)
            continue

        if provider is None or model is None:
            raise CalibrationError(
                f"{key}: counted row needs detail['provider']·detail['model'] "
                "(판정이 돌려준 값, 02-plan-verify R-6) -- "
                f"got provider={provider!r} model={model!r}"
            )

        group = groups.setdefault(
            (method, provider, model),
            {
                "method": method,
                "provider": provider,
                "model": model,
                "bins": empty_bins(),
                "excluded": _new_excluded(),
            },
        )
        assert value is not None  # status == counted 면 값이 있다
        cell = group["bins"][bin_index(value)]
        cell["n"] += 1
        if classify_gold_row(scored) in {"merge_correct", "new_person_correct"}:
            cell["correct"] += 1
        counted_units += 1

    group_list: list[dict[str, Any]] = []
    for group_key in sorted(
        groups, key=lambda k: (S_LLM_METHODS.index(k[0]), k[1], k[2])
    ):
        group = groups[group_key]
        for cell in group["bins"]:
            cell["accuracy"] = _accuracy(cell["correct"], cell["n"])
        n = sum(cell["n"] for cell in group["bins"])
        correct = sum(cell["correct"] for cell in group["bins"])
        group_list.append(
            {
                "method": group["method"],
                "provider": group["provider"],
                "model": group["model"],
                "n": n,
                "correct": correct,
                "accuracy": _accuracy(correct, n),
                "bins": group["bins"],
                "excluded": _finish_excluded(group["excluded"]),
            }
        )

    fresh_calls = {
        method: sum(
            1
            for row in selected
            if str(row["method"]) == method and row["llm_fresh_call"]
        )
        for method in S_LLM_METHODS
        if any(str(row["method"]) == method for row in selected)
    }

    meta: dict[str, Any] = {
        "correct_definition": CORRECT_DEFINITION,
        "bin_rule": BIN_RULE,
        "exclusion_order": list(EXCLUSION_REASONS),
        "s_llm_source": dict(S_LLM_SOURCE),
        "methods": [
            method
            for method in S_LLM_METHODS
            if any(str(row["method"]) == method for row in selected)
        ],
        "model_configured": dict(model_configured or {}),
        "model_configured_source": (
            "호출자가 --model-configured 로 넘긴 설정 문자열(OPENAI_MODEL 등). "
            "JSONL 에 없는 값이라 여기서 환경변수를 읽지 않는다 -- 넘기지 "
            "않으면 빈 객체다(P3-llm-providers §7 인계 4)."
        ),
        "unit_rule": (
            "단위 = (방식, 시나리오, mention) 하나에 한 행. LLM 응답은 mention "
            "당 1회뿐이라(결정 C(i)) T_merge 격자 10행을 10번 세지 않는다. "
            "기본은 sweep_index 최소 행(= llm_fresh_call 행)이고 --t-merge 로 "
            "다른 임계치의 행을 고를 수 있다."
        ),
        "scored_at_t_merge": sorted(scored_t_merge, key=float),
        "t_merge_option": target,
        "row_count": len(row_list),
        "rows_selected": len(selected),
        "ignored_method_rows": ignored_method_rows,
        "unit_count": len(units),
        "counted_units": counted_units,
        "llm_fresh_calls": dict(sorted(fresh_calls.items())),
    }

    return {
        "schema_version": 1,
        "groups": group_list,
        "excluded_clamped": totals["score_clamped"],
        "excluded": _finish_excluded(totals),
        "unassigned": {
            method: _finish_excluded(block) for method, block in sorted(unassigned.items())
        },
        "meta": meta,
    }


# ---------------------------------------------------------------------------
# CLI (JSONL -> 보정표 JSON. 파일을 읽고 쓰는 것 말고는 하지 않는다)
# ---------------------------------------------------------------------------


def _parse_model_configured(values: Sequence[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in values or []:
        if "=" not in item:
            raise CalibrationError(
                f"--model-configured expects provider=model (got {item!r})"
            )
        provider, _, model = item.partition("=")
        provider = provider.strip()
        model = model.strip()
        if not provider or not model:
            raise CalibrationError(
                f"--model-configured expects provider=model (got {item!r})"
            )
        out[provider] = model
    return dict(sorted(out.items()))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.calibration",
        description="U1 파일럿 러너 JSONL -> s_llm 구간별 정답률 보정표 (DB·네트워크 없음)",
    )
    parser.add_argument(
        "--rows",
        required=True,
        help="U1 러너가 쓴 JSONL 경로(`.jsonl` 또는 커밋본 `.jsonl.gz`)",
    )
    parser.add_argument("--out", default=None, help="결과 JSON 경로(생략하면 표준출력)")
    parser.add_argument(
        "--t-merge",
        default=None,
        help="채점할 임계치(생략하면 mention 마다 sweep_index 최소 행)",
    )
    parser.add_argument(
        "--model-configured",
        action="append",
        default=None,
        metavar="PROVIDER=MODEL",
        help="설정 문자열(OPENAI_MODEL 등). meta.model_configured 에 그대로 적는다",
    )
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)

    table = compute_calibration(
        load_rows(args.rows),
        t_merge=args.t_merge,
        model_configured=_parse_model_configured(args.model_configured),
    )
    text = json.dumps(table, ensure_ascii=False, indent=args.indent, sort_keys=True)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover -- CLI 진입점
    raise SystemExit(main())
