"""Refs: P4-pilot-eval S3.7 D10 원칙1 원칙2 원칙8 -- U1 JSONL -> 방식별 지표.

01-plan U2(65행). **입력은 U1 러너가 쓴 JSONL 한 파일뿐이다** -- DB·네트워크·
LLM 을 부르지 않고 `app/` 도 부르지 않는다(방식 이름의 표준 순서를 읽을 때만
`evaluation.resolvers` 를 시도하고, 못 읽으면 등장 순서로 떨어진다). 같은
JSONL 을 넣으면 언제나 같은 수치가 나온다(원칙8).

## 분모 규칙 세 개 (01-plan 65행 -- `meta.denominator_rule` 로도 나간다)

1. **`ambiguous: true` mention 은 제외한다.** 사람도 선행사를 정할 수 없는
   mention 3건(sc-013 t3 · sc-022 t1 · sc-024 t4, `data/scenarios/schema.json`
   `$defs/mention.ambiguous`)은 골드가 `null` 이라 채점 대상이 아니다. 제외한
   행 수는 `meta.excluded` 에 남는다(조용히 버리지 않는다).
2. **`passing_mentions` 는 오탐 분자다.** 등록하면 안 되는 지나가는 언급
   6건(sc-038·sc-039·sc-040)에는 골드 인물이 없다. 여기서 인물 생성 =
   `decision == "new_person"`(= `ask_user(kind="new_person")`, 불변 규약 1 상
   실행은 하지 않으므로 결정만 본다)이 나오면 **오탐**으로 센다
   (`passing.false_positive`). 이 6건은 오병합률·미검출률의 분모에 넣지
   않는다(골드가 없어 옳고 그름을 정의할 수 없다).
3. **`ask_user` 로 간 mention 은 제3 범주다.** 오병합에도 미검출에도 넣지
   않고 `deferred_identity` 로 따로 집계한다. **여기서 제3 범주 =
   `decision == "identity"`** 다 -- 판단을 사람에게 미룬 행. `new_person`
   결정은 제품에서는 `ask_user(kind="new_person")` 이지만 "이 사람은 아는
   누구도 아니다"라는 **단정**이므로 골드와 대조해 정오를 가린다(골드가 DB
   밖 인물이면 정답, DB 안 인물이면 **미검출** -- eval-harness §2 "같은
   사람을 다른 사람으로 분리한 비율"). 두 결정을 모두 채점에서 빼면
   `miss` 분자가 구조적으로 0 이 되어 미검출률과 결정 K 의 지배 기준이
   무의미해진다. 마찰 축(`ask_user_rate_by_kind`)에서는 `identity` 와
   `new_person` 을 **둘 다** ask_user 로 센다 -- 정확도 축과 마찰 축은 배타적
   이지 않으며, 그래서 따로 집계한다.

## 채점표 (골드 mention 한 행 = 결과 하나, `classify_gold_row()`)

| 골드 | `merge`(맞는 id) | `merge`(다른 id) | `identity` | `new_person` |
|------|------------------|------------------|------------|--------------|
| DB 안 인물(`gold_db_person_id` 있음) | `merge_correct` | **`false_merge`** | `deferred` | **`miss`** |
| DB 밖 인물(아직 없는 사람) | — | **`false_merge`** | `deferred` | `new_person_correct` |

`gold_db_person_id` 는 러너가 `ScenarioState.person_id_map` 으로 채운 값이다.
시나리오 사전 상태(`seed_persons`)에 없는 인물을 가리키는 mention 은 정답이
"새 인물"이며, 그 mention 을 기존 인물에 붙이면 오병합이다(원칙1).

## 분모가 0 이면 `rate` 는 `None`

`{"n": 분자, "d": 분모, "rate": 비율}` 형태로만 비율을 낸다(01-plan 231행
"표본 40건" 리스크 -- 분자·분모 없이 비율만 보면 1건이 몇 %인지 알 수 없다).
분모가 0 이면 **0 으로 나누지 않고 `rate: null`** 이다. 0.0 으로 적으면
"측정했더니 0" 과 "측정할 수 없었다" 가 구별되지 않는다(원칙8).

## 한 mention = 10행 (`T_merge` 격자)이라는 함정

러너는 mention × 방식마다 `T_merge` 10점을 돌려 **10행**을 쓴다. LLM 응답은
mention 당 1회만 받고 나머지 9행은 그 사본이다(결정 C(i)). 그래서:

- **토큰·LLM 호출·호출 오류 "건수"** 는 `llm_fresh_call == True` 행만 센다
  (`methods[m].llm`). 10배 부풀리지 않는다.
- **mention 단위 수치**(`llm_skipped`·`derive_hints` 빈 dict)는 방식·mention
  마다 `sweep_index` 가 가장 작은 행 하나만 본다(`mention_level_rows()`).
- **임계치별 분포**(`forced_reason`·`llm_error`)는 그 임계치의 행만 세므로
  사본 중복이 없다. 임계치를 가로질러 합산하지 않는다(01-plan "한 자리 하나").

## 방식 간 분모는 같게 둔다

`llm_error` 행(공급자 장애)은 **기본 분모에 남긴다**. 한 방식만 분모가 줄면
비교가 깨지기 때문이다(`evaluation/resolvers/base.py` 불변 규약 2 -- "그것은
그 방식의 성능이 아니라 평가의 결함이다"). 01-plan 233행 리스크가 요구한
"오류 건을 별도 범주로, 분모에서 뺀 수를 남긴다"는 `point.llm_error` 분포와
`point.excluding_llm_error`(오류 행을 뺀 같은 지표)로 **함께** 낸다. 어느
쪽으로 읽든 수치가 리포트에 있다.

## `score` 는 방식 간 공통 축이 아니다

`score` 의 의미는 방식마다 다르다(제안=3신호 확신도, 임베딩 단독=`s_emb`,
완전일치=일치 여부, LLM 단일=자기보고 `s_llm` -- P3-baselines 인계 14).
그래서 이 모듈은 `score` 를 **어떤 집계에도 쓰지 않는다**. `s_llm` 구간별
정답률은 U3 보정표가 방식·공급자·모델 키로 나눠서 낸다.

## 하지 않는 것

보정표(U3)·곡선과 `metrics.json` 조립·`gate`(U4)·리포트(U5)·CLI 비용
가드(U6). `--validate` 스키마 검증(판정 표 98행)은 `metrics.json` 을 만드는
U4 가 그 구조를 확정한 뒤에 이 모듈에 붙인다.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

__all__ = [
    "ASK_KINDS",
    "ALLOWED_ASK_LABELS",
    "DECISIONS",
    "DENOMINATOR_RULE",
    "MENTION_KINDS",
    "OUTCOMES",
    "REQUIRED_ROW_KEYS",
    "MetricsError",
    "classify_gold_row",
    "compute_metrics",
    "format_t_merge",
    "group_rates",
    "load_rows",
    "mention_level_rows",
    "ratio",
    "validate_rows",
]


class MetricsError(RuntimeError):
    """입력 JSONL 이 계약을 어겼다. 조용히 건너뛰지 않는다(원칙8)."""


#: `evaluation/resolvers/base.py` 와 같은 어휘(D10). 밖의 값은 오류다.
DECISIONS: tuple[str, ...] = ("merge", "identity", "new_person")

#: 러너가 붙이는 mention 구분(`evaluation/runner.py::_mentions_of`).
MENTION_KINDS: tuple[str, ...] = ("gold", "passing")

#: `ask_user_rate_by_kind` 의 키(S3.1 `pending_questions.kind`). `schedule` 은
#: 이 파일럿에서 구조적으로 0 이다 -- mention 해석은 일정 질문을 만들지
#: 않는다(P5-loop 이후 P10 범위, `meta.denominator_rule.ask_user`).
ASK_KINDS: tuple[str, ...] = ("identity", "new_person", "schedule")

#: `expected_ask_user.allowed` 의 라벨(`data/scenarios/schema.json`). ask_kind
#: 와 **별도 어휘**이며 `none` = "질문하지 않는 것이 허용됨" 이다.
ALLOWED_ASK_LABELS: frozenset[str] = frozenset({"identity", "new_person", "none"})

#: `MentionDecision.to_dict()` 키(evaluation/resolvers/base.py:147).
_DECISION_ROW_KEYS: tuple[str, ...] = (
    "method",
    "mention",
    "decision",
    "person_id",
    "score",
    "candidates",
    "trace_id",
    "tokens_in",
    "tokens_out",
    "detail",
)

#: 러너가 더하는 키(`evaluation/runner.py::ROW_EXTRA_KEYS`).
_EXTRA_ROW_KEYS: tuple[str, ...] = (
    "scenario_id",
    "category",
    "mention_kind",
    "mention_index",
    "turn",
    "gold_person_id",
    "gold_db_person_id",
    "ambiguous",
    "expected_ask_user_allowed",
    "trap_kind",
    "t_merge",
    "t_new",
    "sweep_index",
    "llm_fresh_call",
)

#: 행 하나가 반드시 가져야 하는 키. 하나라도 없으면 `MetricsError`.
REQUIRED_ROW_KEYS: tuple[str, ...] = _DECISION_ROW_KEYS + _EXTRA_ROW_KEYS

OUTCOME_MERGE_CORRECT = "merge_correct"
OUTCOME_FALSE_MERGE = "false_merge"
OUTCOME_MISS = "miss"
OUTCOME_DEFERRED = "deferred"
OUTCOME_NEW_CORRECT = "new_person_correct"

#: 골드 mention 한 행이 받는 결과 다섯 가지(위 채점표). 합 = 채점 대상 행 수.
OUTCOMES: tuple[str, ...] = (
    OUTCOME_MERGE_CORRECT,
    OUTCOME_FALSE_MERGE,
    OUTCOME_MISS,
    OUTCOME_DEFERRED,
    OUTCOME_NEW_CORRECT,
)

#: 이 모듈이 적용한 규칙을 수치와 같은 파일에 남긴다(수용 기준 해석 2 --
#: "분모 규칙이 `meta.denominator_rule` 에 기록돼 있다").
DENOMINATOR_RULE: dict[str, Any] = {
    "scored_base": (
        "mention_kind == 'gold' and ambiguous == false. 한 (방식, t_merge) 점의 "
        "오병합률·미검출률·ask_user 발생률·제3 범주가 모두 이 분모를 쓴다."
    ),
    "ambiguous": (
        "ambiguous == true 인 mention 은 골드가 null 이므로 모든 분모에서 제외 "
        "(schema.json $defs/mention.ambiguous, 01-plan 65행). 제외 수는 "
        "meta.excluded.ambiguous_rows."
    ),
    "passing_mentions": (
        "mention_kind == 'passing' 은 골드가 없어 오병합률·미검출률 분모에 "
        "넣지 않는다. decision == 'new_person'(= create_person / "
        "ask_user(kind=new_person))이면 passing.false_positive 의 분자다. "
        "decision == 'merge' 는 라벨이 정의하지 않으므로 분자로 세지 않고 "
        "passing.by_decision 에 수만 남긴다."
    ),
    "third_category": (
        "decision == 'identity'(사람에게 미룬 행)는 오병합에도 미검출에도 "
        "넣지 않고 deferred_identity 로 따로 집계한다. decision == "
        "'new_person' 은 단정이므로 골드와 대조해 miss / new_person_correct "
        "로 채점한다 -- 둘 다 빼면 miss 분자가 구조적으로 0 이 된다."
    ),
    "ask_user": (
        "ask_user_rate_by_kind 는 마찰 축이며 정확도 축(오병합·미검출)과 "
        "배타적이지 않다. identity = decision 'identity', new_person = "
        "decision 'new_person', schedule 은 mention 해석이 만들지 않으므로 "
        "언제나 n=0 이다(P5-loop 이후 P10 범위)."
    ),
    "expected_ask_user_allowed": (
        "단일 정답이 아니라 허용 집합으로 채점한다(schema.json "
        "$defs/expected_ask_user). 관측 라벨 = merge 면 'none', 그 외에는 "
        "decision 그대로. 관측 라벨이 allowed 안에 있으면 분자."
    ),
    "llm_error": (
        "llm_error 행은 기본 분모에 남긴다(방식 간 분모 동일 -- base.py 불변 "
        "규약 2). 분포는 point.llm_error, 오류 행을 뺀 같은 지표는 "
        "point.excluding_llm_error 에 함께 낸다(01-plan 233행)."
    ),
    "sweep_copies": (
        "한 mention × 방식은 T_merge 격자만큼의 행을 갖고 LLM 응답은 그중 "
        "llm_fresh_call == true 행 하나에서만 나왔다. 토큰·LLM 호출·호출 "
        "오류 건수는 그 행만 세고, mention 단위 수치는 sweep_index 최소 행만 "
        "본다. 임계치별 분포는 임계치 안에서만 센다(한 자리 하나)."
    ),
    "score_axis": (
        "score 의 의미는 방식마다 다르므로(P3-baselines 인계 14) 이 모듈은 "
        "어떤 집계에도 score 를 쓰지 않는다 -- 출력 어디에도 score 키가 없다."
    ),
}


# ---------------------------------------------------------------------------
# 작은 도구
# ---------------------------------------------------------------------------


def ratio(n: int, d: int) -> dict[str, Any]:
    """비율은 언제나 분자·분모와 함께 낸다. 분모 0 이면 `rate` 는 `None`
    (0 으로 나누지 않고, 조용히 0.0 으로 만들지도 않는다 -- 원칙8)."""

    n_int = int(n)
    d_int = int(d)
    if n_int < 0 or d_int < 0:
        raise MetricsError(f"ratio: negative counts (n={n_int}, d={d_int})")
    if n_int > d_int:
        raise MetricsError(f"ratio: n > d (n={n_int}, d={d_int})")
    return {"n": n_int, "d": d_int, "rate": (n_int / d_int) if d_int else None}


def format_t_merge(value: Any) -> str:
    """`T_merge` 를 JSON 키로 쓸 문자열로. 격자는 0.01 단위이므로 두 자리로
    접어 `0.8` 이 `0.8000000000000002` 로 새지 않게 한다(02-plan-verify R-7(2))."""

    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise MetricsError(f"t_merge is not a number: {value!r}") from exc
    if numeric != numeric:  # NaN
        raise MetricsError("t_merge is NaN")
    rounded = round(numeric, 2)
    if abs(rounded - numeric) > 1e-9:
        raise MetricsError(f"t_merge {value!r} is not on the 0.01 lattice")
    return f"{rounded:g}"


def _f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _detail(row: Mapping[str, Any]) -> Mapping[str, Any]:
    detail = row["detail"]
    if not isinstance(detail, Mapping):
        raise MetricsError(f"row detail must be an object (got {type(detail).__name__})")
    return detail


def _row_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    """같은 값이 두 번 나오면 중복 적재다(사본을 두 번 세지 않는다)."""

    return (
        row["method"],
        row["scenario_id"],
        row["mention_kind"],
        row["mention_index"],
        format_t_merge(row["t_merge"]),
    )


def _mention_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (row["scenario_id"], row["mention_kind"], row["mention_index"])


# ---------------------------------------------------------------------------
# 입력
# ---------------------------------------------------------------------------


def load_rows(path: Path | str) -> list[dict[str, Any]]:
    """U1 JSONL 을 읽는다. 빈 줄은 건너뛰고, 깨진 줄은 줄 번호와 함께 오류."""

    rows: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise MetricsError(f"{path}:{lineno}: invalid JSON ({exc.msg})") from exc
            if not isinstance(row, dict):
                raise MetricsError(f"{path}:{lineno}: row must be a JSON object")
            rows.append(row)
    if not rows:
        raise MetricsError(f"{path}: no rows")
    return rows


def validate_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """필수 키·어휘·중복을 본다. 하나라도 어긋나면 멈춘다 -- 잘못된 행이
    조용히 지표로 흘러 들어가지 않게(원칙8, base.py `__post_init__` 과 같은
    자세)."""

    if not rows:
        raise MetricsError("no rows to validate")
    seen: dict[tuple[Any, ...], int] = {}
    for index, row in enumerate(rows):
        where = f"row[{index}]"
        if not isinstance(row, Mapping):
            raise MetricsError(f"{where}: row must be a mapping")
        missing = [key for key in REQUIRED_ROW_KEYS if key not in row]
        if missing:
            raise MetricsError(f"{where}: missing required key(s) {missing}")
        decision = row["decision"]
        if decision not in DECISIONS:
            raise MetricsError(
                f"{where}: unknown decision {decision!r} (expected one of {list(DECISIONS)})"
            )
        kind = row["mention_kind"]
        if kind not in MENTION_KINDS:
            raise MetricsError(f"{where}: unknown mention_kind {kind!r}")
        person_id = row["person_id"]
        if decision == "merge" and person_id is None:
            raise MetricsError(f'{where}: decision="merge" without person_id (불변 규약 3)')
        if decision != "merge" and person_id is not None:
            raise MetricsError(
                f"{where}: person_id is only allowed on merge (decision={decision!r})"
            )
        if not isinstance(row["ambiguous"], bool):
            raise MetricsError(f"{where}: ambiguous must be a bool")
        if not isinstance(row["llm_fresh_call"], bool):
            raise MetricsError(f"{where}: llm_fresh_call must be a bool")
        sweep_index = row["sweep_index"]
        if isinstance(sweep_index, bool) or not isinstance(sweep_index, int) or sweep_index < 0:
            raise MetricsError(f"{where}: sweep_index must be a non-negative int")
        _detail(row)
        format_t_merge(row["t_merge"])
        if kind == "gold" and not row["ambiguous"] and row["gold_person_id"] is None:
            raise MetricsError(
                f"{where}: gold mention without gold_person_id must be ambiguous"
            )
        allowed = row["expected_ask_user_allowed"]
        if not isinstance(allowed, list) or not allowed:
            raise MetricsError(f"{where}: expected_ask_user_allowed must be a non-empty list")
        unknown = sorted(set(map(str, allowed)) - ALLOWED_ASK_LABELS)
        if unknown:
            raise MetricsError(f"{where}: unknown expected_ask_user label(s) {unknown}")
        key = _row_key(row)
        if key in seen:
            raise MetricsError(
                f"{where}: duplicate row for {key} (first seen at row[{seen[key]}]) -- "
                "같은 (방식, 시나리오, mention, t_merge) 행을 두 번 세지 않는다"
            )
        seen[key] = index


def mention_level_rows(rows: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """방식 × mention 마다 `sweep_index` 가 가장 작은 행 하나. `T_merge`
    격자 사본을 10번 세지 않기 위한 기준선이다(mention 단위 수치 전용)."""

    best: dict[tuple[Any, ...], Mapping[str, Any]] = {}
    for row in rows:
        key = (row["method"], *_mention_key(row))
        current = best.get(key)
        if current is None or row["sweep_index"] < current["sweep_index"]:
            best[key] = row
    return [best[key] for key in sorted(best, key=lambda k: tuple(map(str, k)))]


# ---------------------------------------------------------------------------
# 채점
# ---------------------------------------------------------------------------


def classify_gold_row(row: Mapping[str, Any]) -> str:
    """골드 mention 한 행의 결과(모듈 docstring 채점표). `passing`·`ambiguous`
    행은 채점 대상이 아니므로 오류다."""

    if row["mention_kind"] != "gold":
        raise MetricsError("classify_gold_row: not a gold mention")
    if row["ambiguous"]:
        raise MetricsError("classify_gold_row: ambiguous mention is excluded (분모 규칙 1)")
    decision = row["decision"]
    gold_db = row["gold_db_person_id"]
    if gold_db is not None:
        if decision == "merge":
            return (
                OUTCOME_MERGE_CORRECT if row["person_id"] == gold_db else OUTCOME_FALSE_MERGE
            )
        if decision == "new_person":
            return OUTCOME_MISS
        return OUTCOME_DEFERRED
    if decision == "merge":
        return OUTCOME_FALSE_MERGE
    if decision == "new_person":
        return OUTCOME_NEW_CORRECT
    return OUTCOME_DEFERRED


def _observed_ask_label(row: Mapping[str, Any]) -> str:
    """허용 집합 채점용 관측 라벨. `merge` 는 "묻지 않았다" = `none`."""

    return "none" if row["decision"] == "merge" else str(row["decision"])


def _ask_kind(row: Mapping[str, Any]) -> str | None:
    """그 행이 물었을 `ask_user.kind`. `detail["ask_kind"]` 가 있으면 대조해
    어긋나면 멈춘다(두 출처가 갈라진 채로 집계하지 않는다)."""

    derived = None if row["decision"] == "merge" else str(row["decision"])
    recorded = _detail(row).get("ask_kind")
    if recorded is not None and recorded != derived:
        raise MetricsError(
            f"detail.ask_kind {recorded!r} disagrees with decision {row['decision']!r}"
        )
    return derived


def _rate_block(counter: Counter[str], d: int, names: Iterable[str]) -> dict[str, Any]:
    return {name: ratio(counter.get(name, 0), d) for name in names}


def _outcome_rates(gold_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """오병합률·미검출률·제3 범주·P/R/F1 (한 묶음의 골드 행에 대해)."""

    outcomes = Counter(classify_gold_row(row) for row in gold_rows)
    d = len(gold_rows)
    gold_existing = sum(1 for row in gold_rows if row["gold_db_person_id"] is not None)
    merges = sum(1 for row in gold_rows if row["decision"] == "merge")
    tp = outcomes.get(OUTCOME_MERGE_CORRECT, 0)
    precision = ratio(tp, merges)
    recall = ratio(tp, gold_existing)
    return {
        "scored": d,
        "outcomes": {name: outcomes.get(name, 0) for name in OUTCOMES},
        "false_merge_rate": ratio(outcomes.get(OUTCOME_FALSE_MERGE, 0), d),
        "miss_rate": ratio(outcomes.get(OUTCOME_MISS, 0), d),
        "deferred_identity_rate": ratio(outcomes.get(OUTCOME_DEFERRED, 0), d),
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision["rate"], recall["rate"]),
    }


def _point(method: str, t_merge: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """한 (방식, `T_merge`) 점의 지표 전부."""

    gold_all = [row for row in rows if row["mention_kind"] == "gold"]
    gold = [row for row in gold_all if not row["ambiguous"]]
    ambiguous = [row for row in gold_all if row["ambiguous"]]
    passing = [row for row in rows if row["mention_kind"] == "passing"]
    scored = gold + passing  # 분포(forced_reason·llm_error)의 기준

    base = _outcome_rates(gold)
    d = base["scored"]

    ask_counter: Counter[str] = Counter()
    for row in gold:
        kind = _ask_kind(row)
        if kind is not None:
            ask_counter[kind] += 1

    allowed_hits = sum(
        1 for row in gold if _observed_ask_label(row) in set(row["expected_ask_user_allowed"])
    )
    passing_allowed_hits = sum(
        1
        for row in passing
        if _observed_ask_label(row) in set(row["expected_ask_user_allowed"])
    )

    forced = Counter(str(_detail(row).get("forced_reason") or "none") for row in scored)
    llm_error = Counter(str(_detail(row).get("llm_error") or "none") for row in scored)

    clean = [row for row in gold if _detail(row).get("llm_error") is None]
    clean_base = _outcome_rates(clean)

    # 부분집합(P3-er §7 리스크 계측) -- merge 행만 본다.
    merge_rows = [row for row in gold if row["decision"] == "merge"]
    unchecked = [row for row in merge_rows if _matched_signal(row, "rule_checked") == 0.0]
    relaxed = [row for row in merge_rows if _detail(row).get("relaxed_retry") is True]

    by_category: dict[str, Any] = {}
    for category in sorted({str(row["category"]) for row in gold}):
        subset = [row for row in gold if str(row["category"]) == category]
        sub = _outcome_rates(subset)
        by_category[category] = {
            "scored": sub["scored"],
            "false_merge_rate": sub["false_merge_rate"],
            "miss_rate": sub["miss_rate"],
            "deferred_identity_rate": sub["deferred_identity_rate"],
        }

    return {
        "method": method,
        "t_merge": float(t_merge),
        "t_new": float(rows[0]["t_new"]),
        "scored": d,
        "rows": len(rows),
        "excluded": {"ambiguous_rows": len(ambiguous), "passing_rows": len(passing)},
        "outcomes": base["outcomes"],
        "false_merge_rate": base["false_merge_rate"],
        "miss_rate": base["miss_rate"],
        "deferred_identity_rate": base["deferred_identity_rate"],
        "precision": base["precision"],
        "recall": base["recall"],
        "f1": base["f1"],
        "ask_user_rate_by_kind": _rate_block(ask_counter, d, ASK_KINDS),
        "expected_ask_user_allowed": ratio(allowed_hits, d),
        "passing": {
            "false_positive": ratio(
                sum(1 for row in passing if row["decision"] == "new_person"), len(passing)
            ),
            "by_decision": {
                name: sum(1 for row in passing if row["decision"] == name)
                for name in DECISIONS
            },
            "expected_ask_user_allowed": ratio(passing_allowed_hits, len(passing)),
        },
        "forced_reason": dict(sorted(forced.items())),
        "llm_error": dict(sorted(llm_error.items())),
        "excluding_llm_error": {
            "scored": clean_base["scored"],
            "false_merge_rate": clean_base["false_merge_rate"],
            "miss_rate": clean_base["miss_rate"],
            "removed_rows": d - clean_base["scored"],
        },
        "subsets": {
            "merge_rule_unchecked": {
                "merges": len(unchecked),
                "false_merge_rate": ratio(
                    sum(
                        1
                        for row in unchecked
                        if classify_gold_row(row) == OUTCOME_FALSE_MERGE
                    ),
                    len(unchecked),
                ),
            },
            "merge_relaxed_retry": {
                "merges": len(relaxed),
                "false_merge_rate": ratio(
                    sum(
                        1 for row in relaxed if classify_gold_row(row) == OUTCOME_FALSE_MERGE
                    ),
                    len(relaxed),
                ),
            },
            "merges": len(merge_rows),
        },
        "by_category": by_category,
    }


def _matched_signal(row: Mapping[str, Any], name: str) -> float | None:
    """`merge` 로 고른 후보의 신호 값(`candidates[i].signals[name]`). 후보
    목록에 그 인물이 없거나 신호가 없으면 `None`(없는 것을 0 으로 세지
    않는다 -- 제안 방식 외 방식은 이 신호 자체가 없다)."""

    person_id = row.get("person_id")
    if person_id is None:
        return None
    candidates = row.get("candidates") or []
    if not isinstance(candidates, list):
        raise MetricsError("row candidates must be a list")
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise MetricsError("candidate must be an object")
        if candidate.get("person_id") != person_id:
            continue
        signals = candidate.get("signals") or {}
        if not isinstance(signals, Mapping):
            raise MetricsError("candidate signals must be an object")
        value = signals.get(name)
        return None if value is None else float(value)
    return None


# ---------------------------------------------------------------------------
# 집계
# ---------------------------------------------------------------------------


def _canonical_method_order(names: Sequence[str]) -> list[str]:
    """`RESOLVERS` 등록 순서(P3-baselines 인계 4 -- `metrics.json` 키 순서).
    그 표를 읽을 수 없는 환경이면 등장 순서로 떨어진다(수치는 그대로다)."""

    try:  # pragma: no cover -- 설치된 환경에서는 언제나 성공한다
        from evaluation.resolvers import ALL_METHODS

        canonical = list(ALL_METHODS)
    except Exception:  # pragma: no cover -- import 실패도 지표를 막지 않는다
        canonical = []
    ordered = [name for name in canonical if name in names]
    ordered += [name for name in names if name not in ordered]
    return ordered


def _llm_block(method_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """토큰·호출·호출 오류는 `llm_fresh_call == True` 행만 센다(사본 9행을
    더하면 10배가 된다). `llm_skipped` 는 호출이 아예 없던 mention 이라
    fresh 행이 없으므로 mention 단위 행에서 센다."""

    fresh = [row for row in method_rows if row["llm_fresh_call"]]
    errors = Counter(
        str(_detail(row).get("llm_error")) for row in fresh if _detail(row).get("llm_error")
    )
    mention_rows = mention_level_rows(method_rows)
    return {
        "calls": len(fresh),
        "tokens_in": sum(int(row["tokens_in"]) for row in fresh),
        "tokens_out": sum(int(row["tokens_out"]) for row in fresh),
        "errors": dict(sorted(errors.items())),
        "error_calls": sum(errors.values()),
        "mentions": len(mention_rows),
        "skipped_mentions": sum(
            1 for row in mention_rows if _detail(row).get("llm_skipped") is True
        ),
    }


def _empty_derive_hints(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """`derive_hints` 가 빈 dict 인 mention 비율(P3-er §7 리스크 계측 --
    호칭 사전 누락). 유도된 hints 를 행에 남기는 방식(`embedding_only`
    `detail["hints"]`)에서만 측정할 수 있고, 그 값은 mention 문자열만의
    함수라 방식과 무관하다. 남긴 방식이 없으면 분모 0 -> `rate: null`."""

    seen: dict[tuple[Any, ...], bool] = {}
    for row in sorted(mention_level_rows(rows), key=lambda r: str(r["method"])):
        detail = _detail(row)
        if "hints" not in detail:
            continue
        key = _mention_key(row)
        if key in seen:
            continue
        hints = detail.get("hints") or {}
        seen[key] = not hints
    block = ratio(sum(1 for empty in seen.values() if empty), len(seen))
    block["basis"] = "detail['hints'] 를 남기는 방식의 mention (sweep_index 최소 행)"
    return block


def group_rates(
    rows: Iterable[Mapping[str, Any]], key: str, *, t_merge: Any | None = None
) -> dict[str, Any]:
    """임의의 행 키(`category`·`trap_kind` 등)로 나눈 오병합률·미검출률.
    U8 실패 케이스 분석이 함정 유형별 거동을 볼 때 쓴다(`metrics.json` 을
    불리지 않으려고 함수로 연다)."""

    selected = [
        row
        for row in rows
        if row["mention_kind"] == "gold"
        and not row["ambiguous"]
        and (t_merge is None or format_t_merge(row["t_merge"]) == format_t_merge(t_merge))
    ]
    out: dict[str, Any] = {}
    for method in _canonical_method_order(sorted({str(r["method"]) for r in selected})):
        by_value: dict[str, Any] = {}
        method_rows = [row for row in selected if row["method"] == method]
        for value in sorted({str(row.get(key)) for row in method_rows}):
            subset = [row for row in method_rows if str(row.get(key)) == value]
            block = _outcome_rates(subset)
            by_value[value] = {
                "scored": block["scored"],
                "false_merge_rate": block["false_merge_rate"],
                "miss_rate": block["miss_rate"],
                "deferred_identity_rate": block["deferred_identity_rate"],
                "outcomes": block["outcomes"],
            }
        out[method] = by_value
    return out


def compute_metrics(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """JSONL 행 전부 -> `{"methods": {...}, "meta": {...}}`.

    `methods[m]["by_t_merge"][t]` 가 곡선의 한 점이다(U4 가 `metrics.json`
    최상위로 옮겨 담고 `gate` 를 얹는다). 같은 입력이면 같은 출력이다 --
    집계 순서는 전부 고정(정렬)되어 있다.
    """

    row_list = [dict(row) for row in rows]
    validate_rows(row_list)

    t_new_values = {float(row["t_new"]) for row in row_list}
    if len(t_new_values) != 1:
        raise MetricsError(
            f"t_new must be a single fixed value (S3.7), got {sorted(t_new_values)}"
        )
    t_new = t_new_values.pop()

    grid = sorted({format_t_merge(row["t_merge"]) for row in row_list}, key=float)
    method_names = _canonical_method_order(sorted({str(row["method"]) for row in row_list}))

    methods: dict[str, Any] = {}
    for method in method_names:
        method_rows = [row for row in row_list if row["method"] == method]
        by_t_merge: dict[str, Any] = {}
        for t_merge in grid:
            point_rows = [
                row for row in method_rows if format_t_merge(row["t_merge"]) == t_merge
            ]
            if not point_rows:
                raise MetricsError(
                    f"method {method!r} has no rows at t_merge={t_merge} "
                    "-- 방식마다 같은 격자를 돌아야 비교가 성립한다"
                )
            by_t_merge[t_merge] = _point(method, t_merge, point_rows)
        methods[method] = {
            "grid": [float(t) for t in grid],
            "by_t_merge": by_t_merge,
            "llm": _llm_block(method_rows),
            "rows": len(method_rows),
        }

    gold_rows = [row for row in row_list if row["mention_kind"] == "gold"]
    mention_rows = mention_level_rows(row_list)
    gold_mentions = {
        _mention_key(row) for row in mention_rows if row["mention_kind"] == "gold"
    }
    ambiguous_mentions = {
        _mention_key(row)
        for row in mention_rows
        if row["mention_kind"] == "gold" and row["ambiguous"]
    }
    passing_mentions = {
        _mention_key(row) for row in mention_rows if row["mention_kind"] == "passing"
    }

    meta = {
        "row_count": len(row_list),
        "scenario_count": len({str(row["scenario_id"]) for row in row_list}),
        "methods": list(method_names),
        "grid": [float(t) for t in grid],
        "t_new": t_new,
        "mention_counts": {
            "gold": len(gold_mentions),
            "gold_scored": len(gold_mentions) - len(ambiguous_mentions),
            "ambiguous": len(ambiguous_mentions),
            "passing": len(passing_mentions),
        },
        "excluded": {
            "ambiguous_rows": sum(1 for row in gold_rows if row["ambiguous"]),
            "ambiguous_mentions": len(ambiguous_mentions),
            "passing_rows": sum(
                1 for row in row_list if row["mention_kind"] == "passing"
            ),
            "passing_mentions": len(passing_mentions),
        },
        "empty_derive_hints": _empty_derive_hints(row_list),
        "denominator_rule": dict(DENOMINATOR_RULE),
    }
    return {"methods": methods, "meta": meta}


# ---------------------------------------------------------------------------
# CLI (JSONL -> 지표 JSON. 파일을 읽고 쓰는 것 말고는 하지 않는다)
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.metrics",
        description="U1 파일럿 러너 JSONL -> 방식별 지표 JSON (DB·네트워크 없음)",
    )
    parser.add_argument("--rows", required=True, help="U1 러너가 쓴 JSONL 경로")
    parser.add_argument("--out", default=None, help="결과 JSON 경로(생략하면 표준출력)")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)

    metrics = compute_metrics(load_rows(args.rows))
    text = json.dumps(metrics, ensure_ascii=False, indent=args.indent, sort_keys=True)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover -- CLI 진입점
    raise SystemExit(main())
