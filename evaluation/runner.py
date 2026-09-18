"""Refs: P4-pilot-eval S3.7 D5 D10 원칙8 원칙9 -- 파일럿 평가 러너(골격·격리·적재).

01-plan U1(64행). `run_pilot()` 은 시나리오마다 다음 다섯 단계를 **그대로**
밟는다 -- 판정은 하나도 새로 만들지 않고, 이미 있는 것을 순서대로 부른다.

(i)   **격리 경계 열기**(결정 D(i)) -- `ctx.session.begin_nested()` 세이브포인트.
(ii)  **사전 상태 적재** -- `evaluation.scenario_state.load_scenario_state(ctx,
      scenario, embedder=…)` **재사용**(registry 124행, 새 적재기 없음).
(iii) **임베딩 단언** -- `state.embedded_alias_count == state.alias_count`.
      어긋나면 경고가 아니라 `RunnerError` 로 **중단**한다(P3-baselines 인계 8
      -- 별칭 임베딩이 NULL 이면 `embedding_only`·`proposed` 가
      `embedding_skipped` 로 떨어져 "방식이 나쁘다"로 오독된다).
(iv)  **mention × 방식 × `T_merge`** 순회 -- 방식마다 `resolve_mention(ctx,
      mention, utterance, None, config=ERConfig(t_merge=x, t_new=0.3))`.
      `hints` 는 언제나 `None` 이다(방식이 필요하면 스스로 유도한다 --
      `app/er/candidates.py` `derive_hints`).
(v)   **경계 되돌리기** -- 세이브포인트 rollback. 이어서 `persons`·
      `person_aliases`·`pending_questions`·`agent_traces` 의 행 수가 경계를
      열기 전과 같은지 **다시 세고**, 다르면 `RunnerError`(인계 9 "두 벌"
      사고를 실행 중에도 막는다).

## 결정 C(i) -- LLM 판정은 mention 당 1회, 밴드는 임계치마다

임계치를 스윕한다고 LLM 을 10번 부르지 않는다. 그러나 러너가 밴드를 **손으로
다시 매기지도 않는다** -- 방식마다 임계치를 쓰는 규칙이 다르고(`embedding_only`
의 동점 강등은 `merge` 밴드에서만 걸린다 -- 02-plan-verify R-5), 그 규칙을
러너가 옮겨 적으면 평가 장치가 판정 로직의 두 번째 출처가 된다(원칙8).

그래서 **임계치마다 그 방식의 `resolve_mention()` 을 그대로 다시 부르고**,
그 아래의 비싼 호출 두 가지만 기억해 둔다:

- **LLM** -- `proposed` 의 `judge` 와 `llm_single` 의 `caller` 를
  `_MentionMemo*` 로 감싼다. 캐시는 **mention 하나 × 방식 하나** 범위이고
  mention 이 바뀔 때마다 비운다. 같은 입력이면 첫 응답(또는 첫
  `JudgeUnavailable`)을 그대로 돌려주므로 10개 임계치가 **같은 응답**을
  본다(비결정성이 곡선에 섞이지 않는다). `app.er.confidence` 가 임계치를
  읽는 곳은 `band_for()` 뿐이고 후보 검색·규칙 필터·LLM 입력은 임계치와
  무관하므로(02-plan-verify R-5 코드 근거) 캐시는 항상 적중한다. 적중하지
  않은 호출은 `RunSummary.llm_repeat_calls` 로 드러난다(0 이어야 한다).
- **임베딩** -- `_MemoEmbedder` 가 문자열 → 벡터를 실행 전체 범위로 기억한다.
  별칭 적재와 mention 임베딩이 **같은 객체**를 거치므로 두 쪽이 같은 공급자·
  같은 모델이라는 것도 구조로 보장된다(D5).

행마다 `llm_fresh_call` 이 붙는다 -- 그 행의 호출이 실제 LLM 호출을 일으켰으면
`True`. 토큰 합계는 이 값이 `True` 인 행만 더해야 한다(나머지 9행은 같은
응답의 사본이다).

## 공급자 환경(P3-llm-providers §7 인계 1)

러너는 `os.environ` 을 복사한 **자기 env** 를 만들어 `LLM_PROVIDER=openai` 를
**명시**로 넣고 `LLM_PROVIDERS_ENABLED` 는 **빼 둔다**(결정 A(ii) -- 제품
기본값이 바뀌어도 이 러너의 공급자는 바뀌지 않는다). 판정기는
`judge_from_env(env)`, 단일 프롬프트는 `caller_from_env(env)` 로 **같은 env**
에서 고른다. 둘 다 **첫 호출 시점**에 만든다(키 없는 테스트가 생성만으로
실패하지 않는다). `os.environ` 은 바꾸지 않는다. `RunSummary` 에는 두
변수의 값만 남기고 env 전체(키 포함)는 어디에도 쓰지 않는다(security §1).

## 산출물 -- JSONL 한 줄

`MentionDecision.to_dict()` 에 다음을 더한다(키 충돌은 `RunnerError`):
`scenario_id`·`turn`·`t_merge`·`gold_person_id`(01-plan 64행 필수) +
U2 가 JSONL 만으로 분모 규칙을 적용할 수 있게 `category`·`mention_kind`
(`gold`/`passing`)·`mention_index`·`ambiguous`·`gold_db_person_id`·
`expected_ask_user_allowed`·`trap_kind`·`t_new`·`sweep_index`·
`llm_fresh_call`. `trace_id` 는 `to_dict()` 값을 그대로 둔다 -- 제안 방식은
행마다 자기 `er_resolve` trace 를 가진다. 결정 D(i) 롤백 때문에 그 trace 는
**실행 중에만** 조회된다 -- `before_rollback` 콜백(U7 표본 덤프 자리)이
세이브포인트를 되돌리기 직전에 불린다.

## 하지 않는 것

지표 계산(U2)·보정표(U3)·곡선·`metrics.json`(U4)·리포트(U5)·CLI·비용
가드(U6). `app/` 은 부르기만 한다(의존 방향 evaluation → app).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from app.db.models import AgentTrace, PendingQuestion, Person, PersonAlias
from app.embedding import EMBEDDING_DIM, as_provider
from app.er.judge import judge_from_env
from app.er.types import ERConfig, JudgeUnavailable
from evaluation.resolvers import RESOLVERS, get_resolver
from evaluation.resolvers.llm_single import caller_from_env
from evaluation.scenario_state import load_scenario_state

if TYPE_CHECKING:
    from app.tools.context import ToolContext
    from evaluation.scenario_state import ScenarioState

__all__ = [
    "T_MERGE_GRID",
    "T_NEW",
    "RUNNER_LLM_PROVIDER",
    "RunnerError",
    "RunSummary",
    "build_runner_env",
    "run_pilot",
]

#: S3.7·D10 곡선 x축 -- {0.5, 0.55, …, 0.95} 10점. `round(…, 2)` 로 만들어
#: `0.8` 이 `0.8000000000000002` 가 되지 않게 한다(02-plan-verify R-7(2)).
T_MERGE_GRID: tuple[float, ...] = tuple(round(0.5 + 0.05 * i, 2) for i in range(10))

#: S3.7 -- `T_new` 는 스윕하지 않는다.
T_NEW: float = 0.3

#: 결정 A(ii) -- P4 실행 공급자. 러너 env 에 **명시**로 넣는다.
RUNNER_LLM_PROVIDER = "openai"

#: 러너 env 에서 빼 두는 변수(P3-llm-providers §7 인계 1).
_UNSET_ENV_KEYS: tuple[str, ...] = ("LLM_PROVIDERS_ENABLED",)

#: JSONL 행에 러너가 더하는 키. `MentionDecision.to_dict()` 키와 겹치면 오류.
ROW_EXTRA_KEYS: tuple[str, ...] = (
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

#: 판정기를 러너가 감싸 넣는 자리(방식 이름 -> 팩토리 키워드). 이 표 밖의
#: 방식은 LLM 을 부르지 않는다.
_LLM_SLOT: dict[str, str] = {"proposed": "judge", "llm_single": "caller"}


class RunnerError(RuntimeError):
    """러너가 실행을 멈춰야 하는 조건(경고로 넘기지 않는다, 원칙8)."""


# ---------------------------------------------------------------------------
# env
# ---------------------------------------------------------------------------


def build_runner_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """러너 전용 env 사본. `LLM_PROVIDER=openai` 명시, `LLM_PROVIDERS_ENABLED`
    제거. `base` 를 생략하면 `os.environ` 을 복사한다(원본은 바꾸지 않는다)."""

    env = dict(os.environ if base is None else base)
    for key in _UNSET_ENV_KEYS:
        env.pop(key, None)
    env["LLM_PROVIDER"] = RUNNER_LLM_PROVIDER
    return env


# ---------------------------------------------------------------------------
# 기억 래퍼 (결정 C(i))
# ---------------------------------------------------------------------------


class _MemoEmbedder:
    """문자열 -> 벡터를 실행 범위로 기억하는 `EmbeddingProvider`.
    `embed()` 한 번에 **아직 모르는 문자열만** 한 배치로 안쪽 공급자에 보낸다."""

    def __init__(self, inner: Any) -> None:
        provider = as_provider(inner)
        if provider is None:  # 호출자가 이미 거른다 -- 방어.
            raise RunnerError("embedder is None")
        self._inner = provider
        self._cache: dict[str, list[float]] = {}
        self.inner_calls = 0
        self.inner_texts = 0

    @property
    def dimension(self) -> int:
        return int(getattr(self._inner, "dimension", EMBEDDING_DIM))

    def embed(self, texts: list[str]) -> list[list[float]]:
        missing = list(dict.fromkeys(t for t in texts if t not in self._cache))
        if missing:
            vectors = self._inner.embed(missing)
            if len(vectors) != len(missing):
                raise RunnerError(
                    f"embedder returned {len(vectors)} vectors for {len(missing)} texts"
                )
            self.inner_calls += 1
            self.inner_texts += len(missing)
            for text, vector in zip(missing, vectors):
                self._cache[text] = list(vector)
        return [list(self._cache[t]) for t in texts]


class _MentionMemo:
    """mention 하나 범위의 LLM 응답 기억(공통 부분). `reset()` 으로 비운다.
    `JudgeUnavailable` 도 기억해 같은 예외를 다시 던진다 -- 10개 임계치가
    같은 실패를 본다(재시도가 아니다)."""

    def __init__(self, factory: Callable[[], Any]) -> None:
        self._factory = factory
        self._inner: Any = None
        self._cache: dict[Any, tuple[bool, Any]] = {}
        self.inner_calls = 0  # 실행 전체 누적
        self.mention_calls = 0  # 현재 mention 안
        self.repeat_calls = 0  # 한 mention 안에서 2회째 이상 실제 호출

    def _get_inner(self) -> Any:
        if self._inner is None:
            self._inner = self._factory()
        return self._inner

    def reset(self) -> None:
        self._cache.clear()
        self.mention_calls = 0

    def _call(self, key: Any, fn: Callable[[Any], Any]) -> Any:
        if key not in self._cache:
            self.inner_calls += 1
            self.mention_calls += 1
            if self.mention_calls > 1:
                self.repeat_calls += 1
            try:
                self._cache[key] = (True, fn(self._get_inner()))
            except JudgeUnavailable as exc:
                self._cache[key] = (False, exc)
        ok, value = self._cache[key]
        if ok:
            return value
        raise value


class _MemoJudge(_MentionMemo):
    """`app.er.judge.Judge` 모양 -- `proposed` 에 주입한다."""

    def judge(self, mention: str, utterance: str, candidates: list[Any]) -> Any:
        key = (mention, utterance, repr(candidates))
        return self._call(key, lambda inner: inner.judge(mention, utterance, candidates))


class _MemoCaller(_MentionMemo):
    """`llm_single.SingleCaller` 모양 -- `llm_single` 에 주입한다."""

    @property
    def provider(self) -> str | None:
        return getattr(self._inner, "provider", None) if self._inner is not None else None

    @property
    def model(self) -> str | None:
        return getattr(self._inner, "model", None) if self._inner is not None else None

    def complete(self, system: str, user_text: str) -> Any:
        return self._call((system, user_text), lambda inner: inner.complete(system, user_text))


# ---------------------------------------------------------------------------
# 요약
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunSummary:
    """`run_pilot()` 의 반환값. 수치만 담는다(env·키·프롬프트 원문 없음)."""

    out_path: str
    scenario_ids: tuple[str, ...]
    methods: tuple[str, ...]
    t_merge_grid: tuple[float, ...]
    t_new: float
    row_count: int
    mention_count: int
    rows_by_method: dict[str, int] = field(default_factory=dict)
    llm_calls_by_method: dict[str, int] = field(default_factory=dict)
    llm_repeat_calls: int = 0
    tokens_in_by_method: dict[str, int] = field(default_factory=dict)
    tokens_out_by_method: dict[str, int] = field(default_factory=dict)
    embed_calls: int = 0
    embed_texts: int = 0
    alias_count: int = 0
    embedded_alias_count: int = 0
    llm_provider_env: str = RUNNER_LLM_PROVIDER
    llm_providers_enabled_env: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "out_path": self.out_path,
            "scenario_ids": list(self.scenario_ids),
            "methods": list(self.methods),
            "t_merge_grid": list(self.t_merge_grid),
            "t_new": self.t_new,
            "row_count": self.row_count,
            "mention_count": self.mention_count,
            "rows_by_method": dict(self.rows_by_method),
            "llm_calls_by_method": dict(self.llm_calls_by_method),
            "llm_repeat_calls": self.llm_repeat_calls,
            "tokens_in_by_method": dict(self.tokens_in_by_method),
            "tokens_out_by_method": dict(self.tokens_out_by_method),
            "embed_calls": self.embed_calls,
            "embed_texts": self.embed_texts,
            "alias_count": self.alias_count,
            "embedded_alias_count": self.embedded_alias_count,
            "llm_provider_env": self.llm_provider_env,
            "llm_providers_enabled_env": self.llm_providers_enabled_env,
        }


# ---------------------------------------------------------------------------
# 검증 헬퍼
# ---------------------------------------------------------------------------


def _normalize_grid(t_merge_grid: Iterable[float]) -> tuple[float, ...]:
    grid: list[float] = []
    for value in t_merge_grid:
        numeric = float(value)
        rounded = round(numeric, 2)
        if abs(rounded - numeric) > 1e-9:
            raise ValueError(f"t_merge_grid: {value!r} is not on the 0.01 lattice")
        if not (T_NEW <= rounded <= 1.0):
            raise ValueError(f"t_merge_grid: {value!r} outside [{T_NEW}, 1.0]")
        if rounded in grid:
            raise ValueError(f"t_merge_grid: duplicate value {rounded!r}")
        grid.append(rounded)
    if not grid:
        raise ValueError("t_merge_grid is empty")
    return tuple(grid)


def _check_methods(methods: Sequence[str]) -> tuple[str, ...]:
    names = tuple(methods)
    if not names:
        raise ValueError("methods is empty")
    if len(set(names)) != len(names):
        raise ValueError(f"methods has duplicates: {list(names)}")
    unknown = [n for n in names if n not in RESOLVERS]
    if unknown:
        raise KeyError(f"unknown method(s) {unknown}; registered: {list(RESOLVERS)}")
    return names


def _state_counts(ctx: ToolContext) -> dict[str, int]:
    """경계 밖 누수 검사용 행 수(이 사용자·이 세션 범위)."""

    session = ctx.session
    person_ids = select(Person.id).where(Person.user_id == ctx.user_id)
    return {
        "persons": session.execute(
            select(func.count()).select_from(Person).where(Person.user_id == ctx.user_id)
        ).scalar_one(),
        "person_aliases": session.execute(
            select(func.count())
            .select_from(PersonAlias)
            .where(PersonAlias.person_id.in_(person_ids))
        ).scalar_one(),
        "pending_questions": session.execute(
            select(func.count())
            .select_from(PendingQuestion)
            .where(PendingQuestion.session_id == ctx.session_id)
        ).scalar_one(),
        "agent_traces": session.execute(
            select(func.count())
            .select_from(AgentTrace)
            .where(AgentTrace.session_id == ctx.session_id)
        ).scalar_one(),
    }


def _mentions_of(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """골드 mention(원래 순서) 다음에 `passing_mentions`(원래 순서)."""

    items: list[dict[str, Any]] = []
    for index, mention in enumerate(scenario.get("mentions") or []):
        items.append(
            {
                "mention_kind": "gold",
                "mention_index": index,
                "turn": int(mention["turn"]),
                "surface": str(mention["surface"]),
                "gold_person_id": mention.get("gold_person_id"),
                "ambiguous": bool(mention.get("ambiguous", False)),
            }
        )
    for index, mention in enumerate(scenario.get("passing_mentions") or []):
        items.append(
            {
                "mention_kind": "passing",
                "mention_index": index,
                "turn": int(mention["turn"]),
                "surface": str(mention["surface"]),
                "gold_person_id": None,
                "ambiguous": False,
            }
        )
    return items


# ---------------------------------------------------------------------------
# 러너
# ---------------------------------------------------------------------------


def run_pilot(
    ctx_factory: Callable[[str], ToolContext],
    scenarios: Iterable[dict[str, Any]],
    methods: Sequence[str],
    t_merge_grid: Iterable[float],
    *,
    embedder: Any,
    judge: Any = None,
    out_path: Path | str,
    resolver_kwargs: Mapping[str, Mapping[str, Any]] | None = None,
    env: Mapping[str, str] | None = None,
    before_rollback: Callable[[ToolContext, ScenarioState, list[dict[str, Any]]], None]
    | None = None,
    overwrite: bool = False,
) -> RunSummary:
    """시나리오 × mention × 방식 × `T_merge` 를 돌려 JSONL 을 쓴다.

    - `ctx_factory(scenario_id)` -- 그 시나리오를 돌릴 `ToolContext`. 러너가
      `embedder` 로 `ctx.embedder` 를 채운다(이미 다른 공급자가 꽂혀 있으면
      `RunnerError` -- 별칭 벡터와 mention 벡터의 출처가 갈라진다, D5).
    - `embedder` -- **필수**. `None` 이면 DB·파일을 건드리기 전에 즉시
      `RunnerError`(경고 아님, 인계 8).
    - `judge` -- `proposed` 의 판정기. `None` 이면 첫 호출 때
      `judge_from_env(build_runner_env(env))`.
    - `resolver_kwargs` -- 방식 이름 -> `get_resolver()` 추가 인자(테스트 스텁
      주입 자리). `llm_single` 의 `caller`/`client` 는 러너가 소비해
      기억 래퍼로 감싼다.
    - `env` -- 러너 env 의 바탕(생략 시 `os.environ`). 어떤 경우든
      `build_runner_env()` 를 거친다.
    - `before_rollback(ctx, state, rows)` -- 세이브포인트를 되돌리기 직전
      (trace 가 아직 보일 때) 불린다. U7 표본 덤프 자리.
    - `out_path` 가 이미 있으면 `overwrite=True` 가 아닌 한 `FileExistsError`
      (원시 결과를 조용히 덮어쓰지 않는다, 원칙8).
    """

    # --- 0. 입력 검증 (DB·파일 전) ----------------------------------------
    if embedder is None:
        raise RunnerError(
            "run_pilot: embedder is required -- without it every alias embedding "
            "is NULL and embedding_only/proposed degrade to embedding_skipped "
            "(P3-baselines 인계 8)"
        )
    if as_provider(embedder) is None:  # pragma: no cover -- None 은 위에서 걸린다
        raise RunnerError("run_pilot: embedder is not usable")
    names = _check_methods(methods)
    grid = _normalize_grid(t_merge_grid)
    scenario_list = list(scenarios)
    if not scenario_list:
        raise ValueError("scenarios is empty")
    seen_ids: set[str] = set()
    for scenario in scenario_list:
        if not isinstance(scenario, dict) or not isinstance(scenario.get("id"), str):
            raise ValueError("each scenario must be a dict with a str 'id'")
        if scenario["id"] in seen_ids:
            raise ValueError(f"duplicate scenario id {scenario['id']!r}")
        seen_ids.add(scenario["id"])

    out = Path(out_path)
    if out.exists() and not overwrite:
        raise FileExistsError(f"run_pilot: {out} exists (pass overwrite=True)")

    runner_env = build_runner_env(env)
    extra_kwargs = {k: dict(v) for k, v in (resolver_kwargs or {}).items()}
    unknown_kw = [k for k in extra_kwargs if k not in names]
    if unknown_kw:
        raise KeyError(f"resolver_kwargs for methods not in run: {unknown_kw}")

    # --- 1. 방식 인스턴스 + 기억 래퍼 --------------------------------------
    memo_embedder = _MemoEmbedder(embedder)
    memos: dict[str, _MentionMemo] = {}
    resolvers: dict[str, Any] = {}
    for name in names:
        kwargs = extra_kwargs.get(name, {})
        slot = _LLM_SLOT.get(name)
        if slot == "judge":
            given_judge = kwargs.pop("judge", None) or judge
            memo: _MentionMemo = _MemoJudge(
                (lambda j=given_judge: j)
                if given_judge is not None
                else (lambda: judge_from_env(runner_env))
            )
            kwargs["judge"] = memo
            memos[name] = memo
        elif slot == "caller":
            given_caller = kwargs.pop("caller", None)
            client = kwargs.pop("client", None)
            memo = _MemoCaller(
                (lambda c=given_caller: c)
                if given_caller is not None
                else (lambda c=client: caller_from_env(runner_env, client=c))
            )
            kwargs["caller"] = memo
            kwargs.pop("env", None)
            memos[name] = memo
        resolvers[name] = get_resolver(name, **kwargs)

    configs = [ERConfig(t_merge=t, t_new=T_NEW) for t in grid]

    rows_by_method = {n: 0 for n in names}
    tokens_in = {n: 0 for n in names}
    tokens_out = {n: 0 for n in names}
    mention_count = 0
    alias_total = 0
    embedded_total = 0
    row_count = 0

    # --- 2. 시나리오 루프 --------------------------------------------------
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as handle:
        for scenario in scenario_list:
            scenario_id = scenario["id"]
            ctx = ctx_factory(scenario_id)
            if ctx.embedder is not None and ctx.embedder is not embedder:
                raise RunnerError(
                    f"{scenario_id}: ctx.embedder differs from run_pilot(embedder=) "
                    "-- alias and mention vectors would come from different sources (D5)"
                )
            ctx = replace(ctx, embedder=memo_embedder)
            before = _state_counts(ctx)

            savepoint = ctx.session.begin_nested()  # (i)
            try:
                state = load_scenario_state(ctx, scenario, embedder=memo_embedder)  # (ii)
                if state.embedded_alias_count != state.alias_count:  # (iii)
                    raise RunnerError(
                        f"{scenario_id}: embedded_alias_count "
                        f"{state.embedded_alias_count} != alias_count {state.alias_count}"
                    )
                alias_total += state.alias_count
                embedded_total += state.embedded_alias_count

                scenario_rows = _run_scenario(
                    ctx,
                    scenario,
                    state,
                    names,
                    resolvers,
                    memos,
                    grid,
                    configs,
                )  # (iv)
                for row in scenario_rows:
                    handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
                    handle.write("\n")
                    method = row["method"]
                    rows_by_method[method] += 1
                    if row["llm_fresh_call"]:
                        tokens_in[method] += int(row["tokens_in"])
                        tokens_out[method] += int(row["tokens_out"])
                row_count += len(scenario_rows)
                mention_count += len(_mentions_of(scenario))
                handle.flush()

                if before_rollback is not None:
                    before_rollback(ctx, state, scenario_rows)
            finally:
                if savepoint.is_active:  # (v)
                    savepoint.rollback()

            after = _state_counts(ctx)
            if after != before:
                raise RunnerError(
                    f"{scenario_id}: rows leaked past the isolation boundary "
                    f"(before={before}, after={after})"
                )

    return RunSummary(
        out_path=str(out),
        scenario_ids=tuple(s["id"] for s in scenario_list),
        methods=names,
        t_merge_grid=grid,
        t_new=T_NEW,
        row_count=row_count,
        mention_count=mention_count,
        rows_by_method=rows_by_method,
        llm_calls_by_method={n: (memos[n].inner_calls if n in memos else 0) for n in names},
        llm_repeat_calls=sum(m.repeat_calls for m in memos.values()),
        tokens_in_by_method=tokens_in,
        tokens_out_by_method=tokens_out,
        embed_calls=memo_embedder.inner_calls,
        embed_texts=memo_embedder.inner_texts,
        alias_count=alias_total,
        embedded_alias_count=embedded_total,
        llm_provider_env=runner_env["LLM_PROVIDER"],
        llm_providers_enabled_env=runner_env.get("LLM_PROVIDERS_ENABLED"),
    )


def _run_scenario(
    ctx: ToolContext,
    scenario: dict[str, Any],
    state: ScenarioState,
    names: tuple[str, ...],
    resolvers: dict[str, Any],
    memos: dict[str, _MentionMemo],
    grid: tuple[float, ...],
    configs: list[ERConfig],
) -> list[dict[str, Any]]:
    """(iv) mention × 방식 × `T_merge`. 방식별 분기 없음 -- 모든 방식을 같은
    인자(`hints=None`, 같은 `ERConfig`)로 부른다."""

    utterances: list[str] = list(scenario.get("utterances") or [])
    allowed = list((scenario.get("expected_ask_user") or {}).get("allowed") or [])
    trap = scenario.get("trap") or {}
    trap_kind = trap.get("kind") if isinstance(trap, dict) else None
    rows: list[dict[str, Any]] = []

    for item in _mentions_of(scenario):
        turn = item["turn"]
        if not 0 <= turn < len(utterances):
            raise RunnerError(f"{scenario['id']}: mention turn {turn} out of range")
        utterance = utterances[turn]
        gold = item["gold_person_id"]
        for name in names:
            memo = memos.get(name)
            if memo is not None:
                memo.reset()
            for sweep_index, (t_merge, config) in enumerate(zip(grid, configs)):
                calls_before = memo.inner_calls if memo is not None else 0
                decision = resolvers[name].resolve_mention(
                    ctx, item["surface"], utterance, None, config=config
                )
                fresh = memo is not None and memo.inner_calls > calls_before
                row = decision.to_dict()
                extra = {
                    "scenario_id": scenario["id"],
                    "category": scenario.get("category"),
                    "mention_kind": item["mention_kind"],
                    "mention_index": item["mention_index"],
                    "turn": turn,
                    "gold_person_id": gold,
                    "gold_db_person_id": state.person_id_map.get(gold) if gold else None,
                    "ambiguous": item["ambiguous"],
                    "expected_ask_user_allowed": allowed,
                    "trap_kind": trap_kind,
                    "t_merge": t_merge,
                    "t_new": T_NEW,
                    "sweep_index": sweep_index,
                    "llm_fresh_call": fresh,
                }
                clash = set(extra) & set(row)
                if clash:
                    raise RunnerError(f"row key clash with MentionDecision.to_dict(): {clash}")
                row.update(extra)
                rows.append(row)
    return rows
