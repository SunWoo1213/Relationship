"""Refs: P4-pilot-eval D4 원칙8 L-004 -- 파일럿 평가 실행 CLI(dry-run·비용 가드).

01-plan U6(70행). 이 스크립트는 **판정도 지표도 만들지 않는다** -- U1~U5 가
만든 다섯 조각을 순서대로 부르고 각 단계의 종료 코드를 확인할 뿐이다.

    runner(U1) → metrics(U2) → calibration(U3) → curve(U4) → validate → report(U5)

## 두 가지 모드

- `--dry-run --stub` -- 스텁 판정기·스텁 단일호출·결정적 가짜 임베딩으로
  **네트워크 0**. 사슬이 실제로 이어지는지(JSONL → metrics.json →
  calibration.json → curve.csv → eval.md)를 키 없이 증명한다. 여기서 나온
  수치는 **결과가 아니다**(스텁 점수다) -- 그래서 `--out` 이 `reports/`
  안이면 거부한다(원칙8: 재현 불가능한·의미 없는 수치를 리포트 자리에
  두지 않는다).
- 실 실행(U7 몫) -- `--dry-run` 없이 돌린다. 필요한 키 환경변수가 없으면
  **rc=2** 로 멈추고 **변수 이름만** 안내한다. `.env` 를 읽지 않고
  (security §1) 환경변수를 통째로 출력하지도 않는다. 공급자는 결정 A(ii)
  대로 `LLM_PROVIDER=openai` 이며 러너 env 는 `build_runner_env()` 를
  그대로 쓴다(두 번째 env 조립기를 만들지 않는다).

## 실행 전에 비용을 먼저 찍는다 (결정 B)

어떤 모드든 **실행 전에** 예상 LLM 호출 수·토큰·비용(USD)을 표준출력에
찍는다. `--max-cost-usd`(기본 5, 결정 B -- AWS Budgets $10 알림의 절반)를
넘으면 **한 줄도 실행하지 않고** rc=3 으로 끝난다.

추정의 입력은 **라벨과 실제 프롬프트 빌더**다(지어낸 상수가 아니다):

- 호출 수 = mention 수 × (`proposed` 1 + `llm_single` 1). 결정 C(i) 이므로
  임계치 10점은 같은 응답을 쓴다(LLM 을 10번 부르지 않는다).
- 프롬프트 문자 수 = `evaluation.resolvers.llm_single.build_prompt()` 와
  `app.er.judge.build_prompt()` 를 **그대로 호출**해 센다(사전 상태는
  `seed_person_specs()` 라벨에서 만든다 -- DB·네트워크 없이 순수하게).
  `proposed` 의 후보 수는 `min(ERConfig.top_k, 사전 상태 인물 수)` 로 잡는
  **상한**이다(규칙 필터가 실제로는 더 줄인다).
- 문자 → 토큰과 출력 토큰 수는 **가정값**(`CHARS_PER_TOKEN`·
  `OUTPUT_TOKENS_PER_CALL`)이며 출력에 "가정"이라고 적는다. 실측은 U7 의
  `tokens_in`/`tokens_out` 합계로만 나온다(원칙8 -- 실측이라고 부르지
  않는다).
- 단가는 상수(`PRICE_*`)이고 출처·기준일을 아래에 적었다. 네트워크로
  확인하지 않으므로 실행 전에 `--price-in`/`--price-out`/`--price-embed`
  로 사용자가 덮어쓸 수 있다.

## 재현성 (원칙8)

- `dataset_hash` = `data/scenarios/*.json` 전부를 **경로 정렬 후** 경로
  바이트와 파일 바이트를 이어 sha256 한 값(`sha256:<64자>`). 파일 하나라도
  바뀌면 값이 바뀐다.
- `run_id` = 결정적 입력만으로 만든 sha256 앞 12자
  (`dataset_hash`·방식 목록·격자·`t_new`·`run_mode`·`commit`·
  `embedding_model`·`model_configured`). **시각은 들어가지 않는다** --
  같은 입력이면 `metrics.json` 이 바이트까지 같다. 시각은 원시 JSONL 파일
  이름(`raw-<ts>.jsonl`)에만 쓴다.

## 실행 중 trace 표본 덤프 + 확신도 재계산 (원칙3·원칙9)

결정 D(i)(시나리오별 트랜잭션 롤백) 때문에 `agent_traces` 는 **실행 중에만**
조회된다. 그래서 `run_pilot(before_rollback=…)` 안에서 그 시나리오의
`step='er_resolve' AND tool_name='er'` 행을 `raw-<ts>.jsonl` 과 **같은
stamp** 의 `traces-<ts>.jsonl` 로 덤프하고(제안 방식 행 1개 ↔ 판정 1개),
사슬 끝에서 전 줄의 `confidence` 를 다시 계산해 기록값과 비교한다 --
`[traces] dumped=… recomputed=… max_abs_diff=… path=…`. 하나라도 어긋나면
rc=1 이고 어느 trace 인지 찍는다. 재계산은 `app.er.confidence.combine()`
(제품 코드)을 그대로 부르고 가중치는 trace 에 기록된 값을 쓰되 제품 상수
`app.settings.ER_WEIGHTS`(0.5/0.3/0.2)와 다르면 거부한다. 덤프 파일만 있으면
`--recheck-traces <path>` 로 언제든 다시 돌릴 수 있다(DB·네트워크 0).
프롬프트 원문·`llm.reason` 자유 서술·키는 덤프에 넣지 않는다(security §1).

## 원시 JSONL 은 gzip 으로 커밋한다 (결정 E 이행 방식)

`.githooks/pre-commit` 이 5MB 초과 파일을 막는데 전량 실행의
`raw-<ts>.jsonl` 은 그보다 크다(스텁 실측 7,404,682 bytes). 사용자 결정
(2026-09-21)은 **gzip 으로 커밋**이다 -- 결정 E(원시 판정을 커밋한다)는
그대로 두고 훅도 바꾸지 않는다. 그래서 사슬은

1. 러너가 지금처럼 **평문으로 줄 단위로** 쓰고(중단돼도 거기까지 남는다),
2. 러너가 끝난 뒤 `raw-<ts>.jsonl.gz` 로 압축하고(헤더 `mtime=0`·파일명
   미기록·`compresslevel` 고정 → 같은 입력이면 **같은 바이트**),
3. 다시 풀어 sha256 을 대조한 뒤(`[gzip] roundtrip_sha256=… ok`),
4. **이후 단계(metrics·calibration·curve)에 압축본 경로를 넘긴다** --
   커밋된 파일 하나만으로 지표가 재계산됨을 실행이 매번 증명한다(원칙8).

평문은 기본 **보존**이고 `--drop-raw-plain` 으로만 지운다(검증 통과 후에만).
읽는 쪽은 `evaluation.metrics.open_jsonl()`/`iter_jsonl()` 한 곳이라
`python -m evaluation.metrics --rows …/raw-<ts>.jsonl.gz` 가 그대로 돈다.
`traces-<ts>.jsonl`(~1.7MB)은 한도 안이라 평문 그대로 둔다. 사슬 끝에서
커밋 대상(`raw.gz`·`traces`)의 크기를 `[size]` 로 찍고 한도를 넘으면
`[warn]` 을 낸다(rc 는 바꾸지 않는다 -- `format_commit_sizes` 참조).

## 하지 않는 것

실 API 호출(U7), `reports/` 실물 작성(U7), 실패 케이스 분석(U8). 지표
계산을 여기서 다시 하지 않는다 -- 전부 U2~U5 모듈의 `main(argv)` 을 부르고
돌아온 정수 rc 만 본다.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import random
import re
import shutil
import sys
import zlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover -- `python scripts/...` 직접 실행
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AgentTrace
from app.embedding import EMBEDDING_DIM
from app.er.confidence import combine
from app.er.judge import FakeJudge
from app.er.judge import build_prompt as build_judge_prompt
from app.er.types import (
    ER_TRACE_STEP,
    ER_TRACE_TOOL_NAME,
    ERConfig,
    Judgement,
    ScoredCandidate,
)
from app.settings import ER_WEIGHTS
from app.tools.context import ToolContext
from app.tools.types import InvalidValue
from evaluation import calibration as calibration_mod
from evaluation import curve as curve_mod
from evaluation import metrics as metrics_mod
from evaluation.metrics import GZIP_SUFFIX, MetricsError, iter_jsonl
from evaluation import report as report_mod
from evaluation.resolvers import ALL_METHODS
from evaluation.resolvers.exact_match import KnownPerson
from evaluation.resolvers.llm_single import SingleCallResult
from evaluation.resolvers.llm_single import build_prompt as build_single_prompt
from evaluation.runner import T_MERGE_GRID, T_NEW, RunnerError, build_runner_env, run_pilot
from evaluation.scenario_state import (
    DEFAULT_SCENARIO_DIR,
    ScenarioState,
    load_scenarios,
    seed_person_specs,
)

__all__ = [
    "RC_OK",
    "RC_ERROR",
    "RC_MISSING_KEYS",
    "RC_COST_LIMIT",
    "DEFAULT_MAX_COST_USD",
    "PRICE_IN_PER_1M",
    "PRICE_OUT_PER_1M",
    "PRICE_EMBED_PER_1M",
    "PRICE_SOURCE",
    "CHARS_PER_TOKEN",
    "OUTPUT_TOKENS_PER_CALL",
    "REQUIRED_REAL_ENV",
    "OPTIONAL_REAL_ENV",
    "CostEstimate",
    "dataset_fingerprint",
    "compute_run_id",
    "estimate_run",
    "format_estimate",
    "missing_real_env",
    "StubJudge",
    "StubSingleCaller",
    "StubEmbedder",
    "TRACE_DUMP_SCHEMA_VERSION",
    "TRACE_DUMP_METHOD",
    "TraceDumpError",
    "TraceRecheck",
    "TraceRecheckError",
    "dump_er_traces",
    "recompute_confidence",
    "check_trace_entry",
    "recheck_trace_dump",
    "format_trace_recheck",
    "COMMIT_SIZE_LIMIT_BYTES",
    "GZIP_COMPRESSLEVEL",
    "GzipError",
    "gzip_jsonl",
    "sha256_bytes_of",
    "format_commit_sizes",
    "main",
]

# ---------------------------------------------------------------------------
# 종료 코드 (docs/user-setup/10-pilot-eval-run.md 와 같은 표)
# ---------------------------------------------------------------------------

RC_OK = 0
#: 단계 실패·단언 위반·잘못된 인자
RC_ERROR = 1
#: 실 실행인데 키 환경변수가 없다(이름만 안내, 값은 읽지도 찍지도 않는다)
RC_MISSING_KEYS = 2
#: 예상 비용이 `--max-cost-usd` 를 넘었다(결정 B -- 한 줄도 실행하지 않는다)
RC_COST_LIMIT = 3

# ---------------------------------------------------------------------------
# 비용 상수
# ---------------------------------------------------------------------------

#: 결정 B -- AWS Budgets $10 알림(CLAUDE.md 첫날 필수)의 절반.
DEFAULT_MAX_COST_USD = 5.0

#: 단가(USD / 1M 토큰). **오프라인 상수**다 -- 이 스크립트는 네트워크를
#: 쓰지 않으므로 가격표를 조회해 확인하지 않는다. 실행 전에 사용자가
#: `--price-in`/`--price-out`/`--price-embed` 로 현재 가격을 넣어 덮어쓸 수
#: 있고, 출력에는 언제나 이 출처 문장이 함께 찍힌다(원칙8).
PRICE_IN_PER_1M = 0.15
PRICE_OUT_PER_1M = 0.60
PRICE_EMBED_PER_1M = 0.02
PRICE_SOURCE = (
    "OpenAI 공개 가격표의 gpt-4o-mini(in $0.15 / out $0.60 per 1M)와 "
    "text-embedding-3-small($0.02 per 1M) 기록값 -- 저장소에 적어 둔 "
    "오프라인 상수이며 이 실행은 가격표를 조회하지 않았다. "
    "기준일·현재가는 실행자가 확인하고 --price-in/--price-out/--price-embed 로 덮어쓴다"
)

#: **가정값**. 한국어 + JSON 혼합 프롬프트의 문자당 토큰. 실측은 U7 의
#: `tokens_in` 합계로만 얻는다(그 전에는 "추정"이라고만 적는다, 원칙8).
CHARS_PER_TOKEN = 1.5
#: **가정값**. 구조화 출력 5필드 + 한국어 한 문장 응답의 출력 토큰.
OUTPUT_TOKENS_PER_CALL = 80

# ---------------------------------------------------------------------------
# 실 실행 환경변수 (이름만 다룬다 -- 값을 읽지도, 찍지도 않는다)
# ---------------------------------------------------------------------------

#: 결정 A(ii) -- `LLM_PROVIDER=openai` 는 러너가 강제로 넣으므로 사용자가
#: 둘 필요가 없다. 실제로 없으면 실행이 불가능한 것만 여기 적는다.
REQUIRED_REAL_ENV: tuple[str, ...] = ("OPENAI_API_KEY",)
#: 없어도 기본값으로 돌지만 값이 결과에 남는 것(모델명·DB 포트).
OPTIONAL_REAL_ENV: tuple[str, ...] = ("OPENAI_MODEL", "POSTGRES_PORT")

#: 실 실행에서 임베딩 공급자가 쓰는 모델(D4, `app/embedding.py` 고정값).
REAL_EMBEDDING_MODEL = "text-embedding-3-small"
#: `OPENAI_MODEL` 이 없을 때 `OpenAIJudge` 가 쓰는 기본 모델(app/er/judge.py).
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

#: 스텁 모드에서 `meta` 에 남는 이름(수용 기준 84행 -- 실 실행은 이 문자열이
#: 아니어야 한다).
STUB_PROVIDER = "stub"
STUB_JUDGE_MODEL = "stub-judge"
STUB_SINGLE_MODEL = "stub-single"
STUB_EMBEDDING_MODEL = "stub-embedding"

#: 스텁 실행이 만든 파일을 실 결과 자리에 두지 않는다(원칙8).
FORBIDDEN_STUB_OUT_DIR = "reports"


# ---------------------------------------------------------------------------
# 데이터셋 지문 · run_id (둘 다 결정적 -- 시각·환경변수가 들어가지 않는다)
# ---------------------------------------------------------------------------


def dataset_fingerprint(directory: Path | str = DEFAULT_SCENARIO_DIR) -> str:
    """`data/scenarios/*.json` 전체의 sha256 지문.

    경로(디렉터리 기준 상대 posix 경로)를 정렬한 뒤, 경로 바이트와 파일
    바이트를 `\\0` 로 구분해 이어 붙여 해시한다. 시나리오·manifest·스키마
    중 하나라도 바뀌면 값이 바뀐다(라벨 무변경의 기계 증거, 원칙8).
    """

    root = Path(directory)
    files = sorted(root.glob("*.json"), key=lambda p: p.name)
    if not files:
        raise FileNotFoundError(f"dataset_fingerprint: {root} 에 *.json 이 없다")
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def compute_run_id(
    *,
    dataset_hash: str,
    methods: Sequence[str],
    grid: Sequence[float],
    t_new: float,
    run_mode: str,
    commit: str | None,
    embedding_model: str | None,
    model_configured: Mapping[str, str] | None,
) -> str:
    """결정적 실행 식별자(`run-<12자>`). **시각을 넣지 않는다** -- 같은
    입력으로 두 번 돌리면 `metrics.json` 이 바이트까지 같아야 한다."""

    parts = [
        dataset_hash,
        ",".join(methods),
        ",".join(f"{value:.2f}" for value in grid),
        f"{t_new:.2f}",
        run_mode,
        commit or "",
        embedding_model or "",
        ";".join(f"{k}={v}" for k, v in sorted((model_configured or {}).items())),
    ]
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return f"run-{digest[:12]}"


# ---------------------------------------------------------------------------
# 비용 추정 (순수 -- DB·네트워크·환경변수 0)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CostEstimate:
    """실행 **전에** 계산되는 상한 추정. 실측이 아니다(원칙8)."""

    scenario_count: int
    mention_count: int
    llm_calls_by_method: dict[str, int] = field(default_factory=dict)
    prompt_chars_by_method: dict[str, int] = field(default_factory=dict)
    tokens_in_by_method: dict[str, int] = field(default_factory=dict)
    tokens_out_by_method: dict[str, int] = field(default_factory=dict)
    embed_texts: int = 0
    embed_chars: int = 0
    embed_tokens: int = 0
    price_in_per_1m: float = PRICE_IN_PER_1M
    price_out_per_1m: float = PRICE_OUT_PER_1M
    price_embed_per_1m: float = PRICE_EMBED_PER_1M

    @property
    def llm_calls(self) -> int:
        return sum(self.llm_calls_by_method.values())

    @property
    def tokens_in(self) -> int:
        return sum(self.tokens_in_by_method.values())

    @property
    def tokens_out(self) -> int:
        return sum(self.tokens_out_by_method.values())

    @property
    def usd_in(self) -> float:
        return self.tokens_in / 1_000_000 * self.price_in_per_1m

    @property
    def usd_out(self) -> float:
        return self.tokens_out / 1_000_000 * self.price_out_per_1m

    @property
    def usd_embed(self) -> float:
        return self.embed_tokens / 1_000_000 * self.price_embed_per_1m

    @property
    def usd_total(self) -> float:
        return self.usd_in + self.usd_out + self.usd_embed

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_count": self.scenario_count,
            "mention_count": self.mention_count,
            "llm_calls_by_method": dict(self.llm_calls_by_method),
            "llm_calls": self.llm_calls,
            "prompt_chars_by_method": dict(self.prompt_chars_by_method),
            "tokens_in_by_method": dict(self.tokens_in_by_method),
            "tokens_out_by_method": dict(self.tokens_out_by_method),
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "embed_texts": self.embed_texts,
            "embed_chars": self.embed_chars,
            "embed_tokens": self.embed_tokens,
            "usd": {
                "in": self.usd_in,
                "out": self.usd_out,
                "embed": self.usd_embed,
                "total": self.usd_total,
            },
            "assumptions": {
                "chars_per_token": CHARS_PER_TOKEN,
                "output_tokens_per_call": OUTPUT_TOKENS_PER_CALL,
                "price_in_per_1m": self.price_in_per_1m,
                "price_out_per_1m": self.price_out_per_1m,
                "price_embed_per_1m": self.price_embed_per_1m,
                "price_source": PRICE_SOURCE,
                "llm_calls_rule": (
                    "결정 C(i) -- mention 당 방식별 1회(임계치 10점은 같은 응답 재사용)"
                ),
                "candidate_upper_bound": (
                    "proposed 의 후보 수는 min(ERConfig.top_k, 사전 상태 인물 수) 상한"
                ),
            },
        }


def _mentions_with_utterance(scenario: Mapping[str, Any]) -> list[tuple[str, str]]:
    """(지칭 표면형, 그 턴의 발화) 목록. 골드 + `passing_mentions`."""

    utterances = scenario.get("utterances")
    utterance_list = [u for u in utterances if isinstance(u, str)] if isinstance(utterances, list) else []
    out: list[tuple[str, str]] = []
    for key in ("mentions", "passing_mentions"):
        items = scenario.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, Mapping):
                continue
            surface = item.get("surface")
            turn = item.get("turn")
            if not isinstance(surface, str):
                continue
            utterance = ""
            if isinstance(turn, int) and 0 <= turn < len(utterance_list):
                utterance = utterance_list[turn]
            out.append((surface, utterance))
    return out


def _known_persons(scenario: Mapping[str, Any]) -> list[KnownPerson]:
    """라벨의 사전 상태를 `KnownPerson` 으로(순수 -- DB 를 쓰지 않는다).

    `person_id` 는 추정 전용 자리표(1부터)다 -- 프롬프트 길이에만 쓰이고
    판정에 쓰이지 않는다.
    """

    persons: list[KnownPerson] = []
    for index, spec in enumerate(seed_person_specs(dict(scenario)), start=1):
        names = (spec.display_name, *spec.aliases)
        persons.append(
            KnownPerson(
                person_id=index,
                display_name=spec.display_name,
                names=tuple(dict.fromkeys(names)),
                relation_tag=spec.relation_tag,
                hierarchy=spec.hierarchy,
            )
        )
    return persons


def _as_candidates(persons: Sequence[KnownPerson], top_k: int) -> list[ScoredCandidate]:
    return [
        ScoredCandidate(
            person_id=person.person_id,
            display_name=person.display_name,
            aliases=[n for n in person.all_names() if n != person.display_name],
            relation_tag=person.relation_tag,
            hierarchy=person.hierarchy,
        )
        for person in persons[:top_k]
    ]


def estimate_run(
    scenarios: Iterable[Mapping[str, Any]],
    *,
    price_in_per_1m: float = PRICE_IN_PER_1M,
    price_out_per_1m: float = PRICE_OUT_PER_1M,
    price_embed_per_1m: float = PRICE_EMBED_PER_1M,
    top_k: int | None = None,
) -> CostEstimate:
    """라벨 + 실제 프롬프트 빌더로 계산하는 **상한** 추정(순수)."""

    limit = ERConfig().top_k if top_k is None else top_k
    scenario_list = [dict(s) for s in scenarios]
    llm_calls = {"proposed": 0, "llm_single": 0}
    prompt_chars = {"proposed": 0, "llm_single": 0}
    embed_texts: set[str] = set()
    embed_chars = 0
    mention_total = 0

    for scenario in scenario_list:
        persons = _known_persons(scenario)
        candidates = _as_candidates(persons, limit)
        for surface, utterance in _mentions_with_utterance(scenario):
            mention_total += 1
            system, user_text = build_single_prompt(surface, utterance, persons)
            llm_calls["llm_single"] += 1
            prompt_chars["llm_single"] += len(system) + len(user_text)
            system, user_text = build_judge_prompt(surface, utterance, candidates)
            llm_calls["proposed"] += 1
            prompt_chars["proposed"] += len(system) + len(user_text)
            embed_texts.add(surface)
        # 임베딩되는 것은 `person_aliases.alias` 와 mention 표면형뿐이다
        # (`load_scenario_state` 는 표시 이름을 따로 임베딩하지 않는다).
        # 러너의 기억 래퍼가 문자열 단위로 중복을 없애므로 집합으로 센다.
        for spec in seed_person_specs(scenario):
            embed_texts.update(spec.aliases)

    for text in embed_texts:
        embed_chars += len(text)

    tokens_in = {
        method: math.ceil(chars / CHARS_PER_TOKEN) for method, chars in prompt_chars.items()
    }
    tokens_out = {
        method: calls * OUTPUT_TOKENS_PER_CALL for method, calls in llm_calls.items()
    }
    return CostEstimate(
        scenario_count=len(scenario_list),
        mention_count=mention_total,
        llm_calls_by_method=llm_calls,
        prompt_chars_by_method=prompt_chars,
        tokens_in_by_method=tokens_in,
        tokens_out_by_method=tokens_out,
        embed_texts=len(embed_texts),
        embed_chars=embed_chars,
        embed_tokens=math.ceil(embed_chars / CHARS_PER_TOKEN),
        price_in_per_1m=price_in_per_1m,
        price_out_per_1m=price_out_per_1m,
        price_embed_per_1m=price_embed_per_1m,
    )


def format_estimate(estimate: CostEstimate, *, run_mode: str, max_cost_usd: float) -> list[str]:
    """표준출력 줄 목록(grep 가능한 `key=value` 형식)."""

    calls = estimate.llm_calls_by_method
    return [
        f"[estimate] run_mode={run_mode} scenarios={estimate.scenario_count} "
        f"mentions={estimate.mention_count}",
        f"[estimate] llm_calls total={estimate.llm_calls} "
        f"proposed={calls.get('proposed', 0)} llm_single={calls.get('llm_single', 0)} "
        "(결정 C(i): 임계치 10점은 같은 응답을 재사용한다)",
        f"[estimate] tokens_in={estimate.tokens_in} tokens_out={estimate.tokens_out} "
        f"embed_texts={estimate.embed_texts} embed_tokens={estimate.embed_tokens}",
        f"[estimate] 가정 chars_per_token={CHARS_PER_TOKEN} "
        f"output_tokens_per_call={OUTPUT_TOKENS_PER_CALL} "
        "(실측 아님 -- U7 의 tokens_in/out 합계로만 실측이 된다)",
        f"[estimate] price_per_1m in={estimate.price_in_per_1m} "
        f"out={estimate.price_out_per_1m} embed={estimate.price_embed_per_1m}",
        f"[estimate] price_source={PRICE_SOURCE}",
        f"[estimate] cost_usd total={estimate.usd_total:.4f} "
        f"(in={estimate.usd_in:.4f} out={estimate.usd_out:.4f} embed={estimate.usd_embed:.4f})",
        f"[estimate] max_cost_usd={max_cost_usd}",
    ]


# ---------------------------------------------------------------------------
# 실 실행 환경변수 확인 (이름만)
# ---------------------------------------------------------------------------


def missing_real_env(env: Mapping[str, str] | None = None) -> list[str]:
    """비어 있는 **필수 변수 이름** 목록. 값은 읽지도 돌려주지도 않는다."""

    source = os.environ if env is None else env
    return [name for name in REQUIRED_REAL_ENV if not (source.get(name) or "").strip()]


# ---------------------------------------------------------------------------
# 스텁 (네트워크 0 -- `--stub` 전용)
# ---------------------------------------------------------------------------


class StubJudge:
    """결정적 스텁 판정기. 통과 후보 중 **첫 후보**를 고르고 `s_llm` 은
    (mention, 후보 표시 이름) 해시로 0.05~0.95 사이에서 결정적으로 정한다.

    점수의 입력에 `person_id`(DB 시퀀스 값)를 쓰지 않는다 -- 그 값은 실행
    마다 달라지므로 같은 입력이 같은 `metrics.json` 을 내지 못한다(원칙8).

    점수를 흩어 놓는 이유는 보정표(U3)의 10칸이 한 칸에만 몰리지 않게 해
    사슬이 실제로 칸을 나누는지 보기 위해서다. **품질 주장에 쓰지 않는다**
    -- 이 점수에는 의미가 없다(원칙8).

    범위 검증·후보 밖 id 차단은 `FakeJudge`(=`validate_judgement`) 를 그대로
    거친다(두 번째 검증기를 만들지 않는다). 공급자·모델 이름만
    `stub`/`stub-judge` 로 바꿔 `meta` 에서 스텁임이 드러나게 한다.
    """

    def __init__(self) -> None:
        self.calls = 0

    @staticmethod
    def score_for(mention: str, display_name: str) -> float:
        digest = hashlib.sha256(f"{mention}:{display_name}".encode("utf-8")).digest()
        bucket = digest[0] % 19  # 0..18
        return round(0.05 + bucket * 0.05, 2)

    def judge(self, mention: str, utterance: str, candidates: list[Any]) -> Judgement:
        self.calls += 1
        if not candidates:
            table: dict[int, float] = {}
            pick = None
        else:
            table = {
                c.person_id: self.score_for(mention, c.display_name) for c in candidates
            }
            pick = candidates[0].person_id
        judgement = FakeJudge(table=table, pick=pick, reason="stub", tokens=(0, 0)).judge(
            mention, utterance, candidates
        )
        return replace(judgement, provider=STUB_PROVIDER, model=STUB_JUDGE_MODEL)


class StubSingleCaller:
    """`SingleCaller` 모양 스텁. 인물 목록이 프롬프트에 있으면 첫 id 를
    `merge` 로, 없으면 `new_person` 으로 답한다(결정적). 네트워크 0.

    `s_llm` 해시의 입력에서는 **숫자를 지운다** -- 프롬프트에 실린
    `person_id` 는 DB 시퀀스 값이라 실행마다 달라지고, 그대로 해시하면
    같은 입력이 같은 `metrics.json` 을 내지 못한다(원칙8)."""

    provider = STUB_PROVIDER
    model = STUB_SINGLE_MODEL

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, system: str, user_text: str) -> SingleCallResult:
        self.calls += 1
        ids = _first_person_id(user_text)
        stable = re.sub(r"\d+", "", user_text)
        digest = hashlib.sha256(stable.encode("utf-8")).digest()
        s_llm = round(0.05 + (digest[0] % 19) * 0.05, 2)
        raw: dict[str, Any] = {
            "decision": "merge" if ids is not None else "new_person",
            "matched_person_id": ids,
            "s_llm": s_llm,
            "reason": "stub",
            "candidate_person_ids": [ids] if ids is not None else [],
        }
        return SingleCallResult(
            raw=raw,
            tokens_in=0,
            tokens_out=0,
            model=STUB_SINGLE_MODEL,
            provider=STUB_PROVIDER,
        )


def _first_person_id(user_text: str) -> int | None:
    """스텁 전용 -- 프롬프트에 실린 `"person_id": N` 중 첫 값."""

    marker = '"person_id":'
    index = user_text.find(marker)
    if index < 0:
        return None
    tail = user_text[index + len(marker) :].lstrip()
    digits = ""
    for char in tail:
        if char.isdigit():
            digits += char
        else:
            break
    return int(digits) if digits else None


class StubEmbedder:
    """결정적 가짜 임베딩(`sha256` 시드 → 단위벡터). 네트워크 0.

    문자열마다 독립 벡터라 "팀장 ↔ 부장님" 같은 의미 근접은 만들지
    않는다 -- 사슬이 도는지만 보는 스모크용이고, 이 모드의 수치는 방식
    품질의 근거가 아니다(원칙8).
    """

    model = STUB_EMBEDDING_MODEL

    def __init__(self, dimension: int = EMBEDDING_DIM) -> None:
        self.dimension = dimension
        self.calls = 0
        self.texts = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        self.texts += len(texts)
        return [self._vector(text) for text in texts]

    def _vector(self, value: str) -> list[float]:
        seed = int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")
        rng = random.Random(seed)
        raw = [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]
        norm = sum(v * v for v in raw) ** 0.5 or 1.0
        return [v / norm for v in raw]


# ---------------------------------------------------------------------------
# trace 표본 덤프 · 확신도 재계산 (원칙3·원칙9, 01-plan 106·174행)
# ---------------------------------------------------------------------------


class TraceDumpError(RuntimeError):
    """덤프 단계 실패(trace_id 누락·행 없음·mention 불일치·스키마 결손)."""


class TraceRecheckError(ValueError):
    """재계산 단계 실패(필드 결손·비수치·가중치 불일치)."""


@dataclass(frozen=True)
class TraceRecheck:
    """덤프 파일 하나에 대한 재계산 결과. `failures` 가 비어 있어야 통과."""

    path: str
    dumped: int
    recomputed: int
    max_abs_diff: float
    failures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures and self.dumped > 0 and self.recomputed == self.dumped


@dataclass(frozen=True)
class _Weights:
    """`app.er.confidence.combine()` 이 요구하는 `config` 모양(가중치 3개만).

    가중치는 **이 스크립트가 하드코딩하지 않는다** -- 덤프된 trace 의
    `confidence_breakdown["weights"]`(판정 당시 `ERConfig` 가 실제로 쓴 값)를
    그대로 쓰고, 그 값이 제품 상수 `app.settings.ER_WEIGHTS`(원칙3 의
    0.5/0.3/0.2)와 다르면 재계산을 통과시키지 않는다.
    """

    w_llm: float
    w_emb: float
    w_rule: float


#: 덤프 파일 한 줄의 형식 버전(형식이 바뀌면 올린다).
TRACE_DUMP_SCHEMA_VERSION = 1
#: 덤프 대상 방식 -- `agent_traces` 에 `er_resolve` 행을 남기는 것은 제안
#: 방식뿐이다(01-plan 140행 "proposed +2 = er_resolve + search_person").
TRACE_DUMP_METHOD = "proposed"
#: 덤프에 옮기는 `decision`/`llm` 키(프롬프트 원문·`llm.reason` 자유 서술은
#: 옮기지 않는다 -- security §1, 재계산에 필요하지도 않다).
_TRACE_DECISION_KEYS = (
    "band",
    "band_by_threshold",
    "forced_reason",
    "action",
    "T_merge",
    "T_new",
    "matched_person_id",
    "relaxed_retry",
)
_TRACE_LLM_KEYS = (
    "provider",
    "model",
    "self_reported",
    "s_llm",
    "skipped",
    "error",
    "attempts",
    "tokens_in",
    "tokens_out",
)
#: 귀속된 후보 1개만 옮긴다 -- 후보 전체(`candidates[]`)는 원시 JSONL 의
#: `MentionDecision.candidates` 에 이미 있고(이중 출처·파일 크기), 재계산에
#: 필요한 것은 `confidence_breakdown` 과 "그 값이 귀속 후보의 값과 같은가"
#: 하나뿐이다(원칙9).
_TRACE_CANDIDATE_KEYS = (
    "person_id",
    "s_emb",
    "s_rule",
    "passed_rules",
    "excluded_by",
    "rule_checked",
    "rule_passed",
    "relaxed_pass",
)


def _trace_entry(trace: Any, row: Mapping[str, Any], *, scenario_id: str) -> dict[str, Any]:
    """`agent_traces` 행 1개 + 그 행을 낳은 JSONL 행 1개 → 덤프 한 줄.

    `agent_traces.output` 은 `app.er.types.Resolution.to_dict()` 스키마
    (`{er_version, mention, relaxed_retry, candidates[], confidence_breakdown{},
    decision{}, llm{}}`)다. 여기서 재계산에 필요한 부분과 사람이 되짚을 때
    필요한 식별자만 옮긴다.
    """

    output = trace.output if isinstance(trace.output, dict) else {}
    breakdown = output.get("confidence_breakdown")
    if not isinstance(breakdown, dict):
        raise TraceDumpError(
            f"{scenario_id}: trace {trace.id} 의 output 에 confidence_breakdown 이 없다"
        )
    decision = output.get("decision") if isinstance(output.get("decision"), dict) else {}
    llm = output.get("llm") if isinstance(output.get("llm"), dict) else {}
    candidates = output.get("candidates") if isinstance(output.get("candidates"), list) else []
    trace_mention = output.get("mention")
    if trace_mention != row.get("mention"):
        raise TraceDumpError(
            f"{scenario_id}: trace {trace.id} 의 mention({trace_mention!r}) 이 "
            f"JSONL 행의 mention({row.get('mention')!r}) 과 다르다 -- trace_id 연결이 틀렸다"
        )
    return {
        "schema_version": TRACE_DUMP_SCHEMA_VERSION,
        "scenario_id": scenario_id,
        "session_id": trace.session_id,
        "trace_id": trace.id,
        "step": trace.step,
        "tool_name": trace.tool_name,
        "er_version": output.get("er_version"),
        "method": row.get("method"),
        "mention": trace_mention,
        "mention_index": row.get("mention_index"),
        "mention_kind": row.get("mention_kind"),
        "turn": row.get("turn"),
        "gold_person_id": row.get("gold_person_id"),
        "t_merge": row.get("t_merge"),
        "t_new": row.get("t_new"),
        "sweep_index": row.get("sweep_index"),
        "llm_fresh_call": row.get("llm_fresh_call"),
        "row_decision": row.get("decision"),
        "row_person_id": row.get("person_id"),
        "row_score": row.get("score"),
        "confidence_breakdown": dict(breakdown),
        "decision": {key: decision.get(key) for key in _TRACE_DECISION_KEYS},
        "llm": {key: llm.get(key) for key in _TRACE_LLM_KEYS},
        "candidate_count": len(candidates),
        "matched_candidate": _matched_candidate(candidates, breakdown.get("matched_person_id")),
    }


def _matched_candidate(
    candidates: Sequence[Any], matched_person_id: Any
) -> dict[str, Any] | None:
    """귀속된 후보 1개(없으면 `None`)."""

    if matched_person_id is None:
        return None
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get("person_id") == matched_person_id:
            return {key: candidate.get(key) for key in _TRACE_CANDIDATE_KEYS}
    return None


def dump_er_traces(
    session: Any,
    rows: Sequence[Mapping[str, Any]],
    handle: Any,
    *,
    session_id: str,
    scenario_id: str,
    method: str = TRACE_DUMP_METHOD,
    limit_per_scenario: int | None = None,
) -> int:
    """시나리오 하나의 `er_resolve` trace 를 **롤백 전에** JSONL 로 덤프한다.

    결정 D(i)(시나리오별 트랜잭션 롤백) 때문에 `agent_traces` 는 실행 중에만
    조회된다 -- 그래서 `run_pilot(before_rollback=…)` 안에서 불린다.

    조회 조건은 P3-er §7 재계산 입력 계약 그대로
    `step='er_resolve' AND tool_name='er'` 이고, 대상 id 는 그 시나리오의
    제안 방식 JSONL 행이 들고 있는 `trace_id` 집합이다(행 1개 ↔ 판정 1개).
    제안 방식 행이 있는데 `trace_id` 가 없거나 그 id 의 행이 조회되지 않으면
    `TraceDumpError` 다 -- 01-plan 140행의 "proposed +2" 전제가 깨진
    것이므로 조용히 0행으로 넘어가지 않는다(원칙9).

    `limit_per_scenario` 는 시나리오당 앞에서부터 N 줄로 줄인다(기본
    `None` = 전량. 표본 선택으로 판정을 유리하게 만들 여지를 두지 않으려고
    기본을 전량으로 둔다 -- 원칙8).
    """

    targets = [row for row in rows if row.get("method") == method]
    if not targets:
        return 0
    without_id = [row for row in targets if not isinstance(row.get("trace_id"), int)]
    if without_id:
        raise TraceDumpError(
            f"{scenario_id}: {method} 행 {len(without_id)}/{len(targets)} 개에 trace_id 가 "
            "없다 -- 01-plan 140행 'proposed +2(er_resolve+search_person)' 전제가 깨졌다"
        )
    if limit_per_scenario is not None:
        targets = targets[:limit_per_scenario]
    ids = [int(row["trace_id"]) for row in targets]

    statement = select(AgentTrace).where(
        AgentTrace.id.in_(sorted(set(ids))),
        AgentTrace.session_id == session_id,
        AgentTrace.step == ER_TRACE_STEP,
        AgentTrace.tool_name == ER_TRACE_TOOL_NAME,
    )
    found = {trace.id: trace for trace in session.scalars(statement)}
    absent = sorted({i for i in ids if i not in found})
    if absent:
        raise TraceDumpError(
            f"{scenario_id}: session_id={session_id} 에서 "
            f"step={ER_TRACE_STEP}/tool_name={ER_TRACE_TOOL_NAME} 행을 찾지 못했다 "
            f"(trace_id {absent[:5]}{'…' if len(absent) > 5 else ''}, {len(absent)}개)"
        )

    written = 0
    for row in targets:
        entry = _trace_entry(found[int(row["trace_id"])], row, scenario_id=scenario_id)
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
        written += 1
    handle.flush()
    return written


def recompute_confidence(breakdown: Mapping[str, Any]) -> float:
    """`confidence_breakdown` → `w_llm·s_llm + w_emb·s_emb + w_rule·s_rule`.

    산식을 여기에 다시 적지 않고 **제품 코드**
    `app.er.confidence.combine()` 을 그대로 부른다(두 번째 출처 금지) --
    `s_emb` 클램프와 덧셈 순서까지 같아야 기록값과 비트가 같다.
    가중치는 trace 에 기록된 값을 쓰되 제품 상수 `app.settings.ER_WEIGHTS`
    (원칙3)와 다르면 거부한다.
    """

    weights = breakdown.get("weights")
    if not isinstance(weights, Mapping):
        raise TraceRecheckError("confidence_breakdown.weights 가 없다")
    try:
        recorded = {key: float(weights[key]) for key in ("llm", "emb", "rule")}
    except (KeyError, TypeError, ValueError) as exc:
        raise TraceRecheckError(f"weights 를 읽을 수 없다: {exc}") from exc
    if recorded != {key: float(value) for key, value in ER_WEIGHTS.items()}:
        raise TraceRecheckError(
            f"weights={recorded} 가 제품 상수 ER_WEIGHTS={dict(ER_WEIGHTS)} 와 다르다(원칙3)"
        )
    signals: dict[str, float] = {}
    for key in ("s_llm", "s_emb", "s_rule"):
        value = breakdown.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TraceRecheckError(f"{key}={value!r} 가 수치가 아니다")
        signals[key] = float(value)
    return combine(
        signals["s_llm"],
        signals["s_emb"],
        signals["s_rule"],
        _Weights(w_llm=recorded["llm"], w_emb=recorded["emb"], w_rule=recorded["rule"]),
    )


def check_trace_entry(entry: Mapping[str, Any]) -> float:
    """덤프 한 줄의 `abs(기록 confidence - 재계산 confidence)`.

    **판정 기준은 `diff == 0.0` 이다**(허용오차 없음). 근거:
    `app/er/confidence.py` 는 `round()` 를 어디에도 쓰지 않고(모듈 docstring
    6~16행, F-7fe239) 기록값은 `combine()` 이 낸 double 그대로이며, JSONB·
    `json.dumps` 왕복은 double 을 정확히 복원한다. 같은 함수·같은 연산
    순서로 다시 계산하면 비트까지 같아야 한다.
    """

    breakdown = entry.get("confidence_breakdown")
    if not isinstance(breakdown, Mapping):
        raise TraceRecheckError("confidence_breakdown 이 없다")
    recorded = breakdown.get("confidence")
    if isinstance(recorded, bool) or not isinstance(recorded, (int, float)):
        raise TraceRecheckError(f"기록 confidence={recorded!r} 가 수치가 아니다")
    decision = entry.get("decision") if isinstance(entry.get("decision"), Mapping) else {}
    llm = entry.get("llm") if isinstance(entry.get("llm"), Mapping) else {}
    if decision.get("forced_reason") is None and llm.get("skipped") is False:
        # 정상 경로에서 `decide()` 는 `judgement.s_llm` 을 그대로 쓴다
        # (`app/er/confidence.py` 307행) -- 두 값이 다르면 기록이 깨졌다.
        if isinstance(llm.get("s_llm"), (int, float)) and not isinstance(llm.get("s_llm"), bool):
            if breakdown.get("s_llm") != llm.get("s_llm"):
                raise TraceRecheckError(
                    f"s_llm={breakdown.get('s_llm')!r} 가 llm.s_llm={llm.get('s_llm')!r} 과 다르다"
                    " (강제 경로가 아닌데 자기보고 점수가 어긋난다)"
                )
    matched = entry.get("matched_candidate")
    if isinstance(matched, Mapping):
        # 귀속 후보에서 가져왔다는 값이 정말 그 후보의 값인가(원칙9).
        for breakdown_key, candidate_key in (("s_emb", "s_emb"), ("s_rule", "s_rule")):
            if breakdown.get(breakdown_key) != matched.get(candidate_key):
                raise TraceRecheckError(
                    f"{breakdown_key}={breakdown.get(breakdown_key)!r} 가 귀속 후보 "
                    f"{matched.get('person_id')!r} 의 값 {matched.get(candidate_key)!r} 과 다르다"
                )
    return abs(float(recorded) - recompute_confidence(breakdown))


def recheck_trace_dump(path: Path | str) -> TraceRecheck:
    """덤프 파일 **하나만** 입력으로 전 줄을 재계산한다(DB·네트워크 0).

    실행 중에 불려도(`_run_chain` 끝), 나중에 파일만 들고 다시 불려도
    (`--recheck-traces`) 같은 결과가 나온다. 경로가 `.gz` 면 gzip 으로 읽는다
    (여는 로직은 `evaluation.metrics.iter_jsonl` 하나뿐 -- traces 는 한도
    안이라 평문이 기본이지만 압축본을 줘도 같은 판정이 나온다).
    """

    target = Path(path)
    dumped = 0
    recomputed = 0
    max_abs_diff = 0.0
    failures: list[str] = []
    try:
        for lineno, line in iter_jsonl(target):
            dumped += 1
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                failures.append(f"line {lineno}: JSON 파싱 실패 ({exc})")
                continue
            if not isinstance(entry, dict):
                failures.append(f"line {lineno}: 객체가 아니다")
                continue
            label = f"line {lineno} trace_id={entry.get('trace_id')} " f"{entry.get('scenario_id')}/{entry.get('mention')!r} t_merge={entry.get('t_merge')}"
            try:
                diff = check_trace_entry(entry)
            except (TraceRecheckError, InvalidValue) as exc:
                failures.append(f"{label}: {exc}")
                continue
            recomputed += 1
            max_abs_diff = max(max_abs_diff, diff)
            if diff != 0.0:
                failures.append(
                    f"{label}: abs diff={diff!r} != 0 "
                    f"(기록 {entry['confidence_breakdown'].get('confidence')!r})"
                )
    except MetricsError as exc:  # gzip 손상 -- 조용히 0행으로 넘어가지 않는다
        failures.append(str(exc))
    if dumped == 0:
        failures.append(f"{target}: 덤프가 비어 있다 -- 재계산할 판정이 없다(원칙9)")
    return TraceRecheck(
        path=str(target),
        dumped=dumped,
        recomputed=recomputed,
        max_abs_diff=max_abs_diff,
        failures=failures,
    )


def format_trace_recheck(result: TraceRecheck) -> list[str]:
    """`[traces] …` 요약 줄(성공·실패 공통). 실패는 최대 10건까지 보인다."""

    lines = [
        f"[traces] dumped={result.dumped} recomputed={result.recomputed} "
        f"max_abs_diff={result.max_abs_diff!r} path={result.path}",
        f"[traces] rule=0.5·s_llm+0.3·s_emb+0.2·s_rule (app.er.confidence.combine, "
        f"weights={dict(ER_WEIGHTS)}, 기준 abs diff == 0)",
    ]
    for message in result.failures[:10]:
        lines.append(f"[fail] traces: {message}")
    if len(result.failures) > 10:
        lines.append(f"[fail] traces: … 외 {len(result.failures) - 10}건")
    return lines


# ---------------------------------------------------------------------------
# 커밋용 gzip (결정 E 이행 방식, 사용자 결정 2026-09-21) · 크기 가드
# ---------------------------------------------------------------------------

#: `.githooks/pre-commit` 27행이 막는 파일 크기(bytes). 훅은 이 단위에서
#: 바꾸지 않는다 -- 여기서는 **커밋 대상 산출물이 그 한도 안인지 찍어 준다**.
COMMIT_SIZE_LIMIT_BYTES = 5_242_880

#: gzip 압축 수준. 값이 바뀌면 바이트도 바뀌므로 상수로 고정한다(재현성).
GZIP_COMPRESSLEVEL = 9


class GzipError(RuntimeError):
    """압축·검증 실패(원본 없음 / 왕복 해시 불일치)."""


def sha256_bytes_of(handle: Any, *, chunk: int = 1 << 20) -> str:
    """열린 **바이너리** 핸들을 끝까지 읽어 sha256(hex)."""

    digest = hashlib.sha256()
    while True:
        block = handle.read(chunk)
        if not block:
            break
        digest.update(block)
    return digest.hexdigest()


def gzip_jsonl(
    src: Path | str,
    dest: Path | str | None = None,
    *,
    compresslevel: int = GZIP_COMPRESSLEVEL,
    drop_plain: bool = False,
) -> tuple[Path, str]:
    """평문 JSONL → **결정적** gzip(`<src>.gz`). `(경로, 평문 sha256)` 반환.

    결정적이어야 하는 이유(원칙8): 같은 입력이면 `metrics.json` 이 바이트까지
    같다는 기존 성질과 같은 취지로, 커밋되는 원시 파일도 같은 입력이면 같은
    바이트여야 "이 수치는 이 파일에서 나왔다"를 해시로 말할 수 있다. gzip
    헤더에는 기본으로 **수정 시각과 원본 파일명**이 들어가 실행마다 달라지므로
    `mtime=0`·`filename=""` 로 둔다(압축 수준도 상수).

    쓴 뒤에는 **다시 풀어 평문과 sha256 을 대조한다** -- 검증을 통과해야만
    `drop_plain=True` 가 평문을 지운다(지우고 나서 깨진 것을 발견하면 유료
    실행 결과가 사라진다).
    """

    source = Path(src)
    if not source.is_file():
        raise GzipError(f"gzip: 원본이 없다 -- {source}")
    target = Path(dest) if dest is not None else Path(str(source) + GZIP_SUFFIX)
    with source.open("rb") as raw, target.open("wb") as fileobj:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=fileobj, compresslevel=compresslevel, mtime=0
        ) as compressed:
            shutil.copyfileobj(raw, compressed, length=1 << 20)

    with source.open("rb") as raw:
        plain_digest = sha256_bytes_of(raw)
    try:
        with gzip.open(target, "rb") as unpacked:
            roundtrip_digest = sha256_bytes_of(unpacked)
    except (gzip.BadGzipFile, EOFError, zlib.error) as exc:  # pragma: no cover -- 방어
        raise GzipError(f"gzip: {target} 를 다시 풀 수 없다 ({type(exc).__name__}: {exc})") from exc
    if roundtrip_digest != plain_digest:
        raise GzipError(
            f"gzip: 왕복 sha256 불일치 -- 평문 {plain_digest} != 압축본 {roundtrip_digest}"
        )
    if drop_plain:
        source.unlink()
    return target, plain_digest


def format_commit_sizes(paths: Sequence[Path], *, limit: int = COMMIT_SIZE_LIMIT_BYTES) -> list[str]:
    """커밋 대상 산출물의 크기 줄 + 한도 초과 경고 줄.

    **rc 는 바꾸지 않는다**(0/1/2/3 규약 유지). 한도는 평가의 옳고 그름이
    아니라 커밋 훅의 규칙이고, 유료 실 실행이 끝난 뒤 크기 때문에 rc≠0 을
    돌려주면 "지표가 틀렸다"와 "파일이 크다"가 구분되지 않는다. 대신 경고를
    눈에 띄게 찍어 커밋 전에 사람이 처리하게 한다(03-log 에 근거).
    """

    lines: list[str] = []
    over: list[tuple[Path, int]] = []
    for path in paths:
        if not path.exists():
            lines.append(f"[size] {path} (없음)")
            continue
        size = path.stat().st_size
        state = "OVER" if size > limit else "ok"
        lines.append(f"[size] {path} {size} bytes limit={limit} {state}")
        if size > limit:
            over.append((path, size))
    for path, size in over:
        lines.append(
            f"[warn] 커밋 한도 초과: {path} ({size} bytes > {limit}) -- "
            ".githooks/pre-commit 27행이 이 파일의 커밋을 막는다. "
            "이 실행은 실패가 아니지만(rc 는 그대로) 커밋 전에 처리해야 한다"
        )
    return lines


# ---------------------------------------------------------------------------
# 사슬
# ---------------------------------------------------------------------------


@dataclass
class _Stage:
    name: str
    command: str
    rc: int


def _run_stage(name: str, module: Any, argv: list[str], stages: list[_Stage]) -> int:
    """U2~U5 모듈의 `main(argv)` 을 부르고 rc 를 기록한다."""

    command = f"python -m {module.__name__} " + " ".join(argv)
    print(f"[stage] {name}: {command}")
    rc = int(module.main(argv))
    stages.append(_Stage(name=name, command=command, rc=rc))
    print(f"[stage] {name}: rc={rc}")
    return rc


def _session(engine: Any) -> tuple[Any, Any, Session]:
    """바깥 트랜잭션 + 세이브포인트 세션(테스트 픽스처와 같은 방식).

    평가는 **아무것도 커밋하지 않는다**(결정 D(i)) -- 호출자가 끝에서
    바깥 트랜잭션을 되돌린다.
    """

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    return connection, transaction, session


def _run_chain(args: argparse.Namespace, scenarios: list[dict[str, Any]]) -> int:
    from app.db.session import get_engine

    run_mode = "stub" if args.stub else "real"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    raw_path = out_dir / f"raw-{stamp}.jsonl"
    #: 커밋되는 원시 판정(결정 E). 러너는 평문으로 줄 단위로 쓰고(중단돼도
    #: 거기까지가 남는다), 사슬이 러너가 끝난 뒤 이 이름으로 압축한 다음
    #: 이후 단계에 **압축본 경로를 넘긴다** -- 커밋된 파일 하나만으로 지표가
    #: 다시 계산됨을 실행이 매번 증명한다(원칙8).
    raw_gz_path = Path(str(raw_path) + GZIP_SUFFIX)
    #: 같은 stamp -- 04-review 가 "실행 로그와 같은 ts" 로 대조한다(01-plan 106행).
    traces_path = out_dir / f"traces-{stamp}.jsonl"
    stage_metrics = out_dir / "metrics-stage.json"
    metrics_path = out_dir / "metrics.json"
    calibration_path = out_dir / "calibration.json"
    curve_path = out_dir / "curve.csv"
    report_path = out_dir / "eval.md"

    dataset_hash = dataset_fingerprint(args.scenarios)
    if run_mode == "stub":
        embedding_model = STUB_EMBEDDING_MODEL
        model_configured = f"{STUB_PROVIDER}={STUB_JUDGE_MODEL}"
    else:
        embedding_model = REAL_EMBEDDING_MODEL
        model_configured = "openai=" + (
            os.environ.get("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
        )
    run_id = args.run_id or compute_run_id(
        dataset_hash=dataset_hash,
        methods=ALL_METHODS,
        grid=T_MERGE_GRID,
        t_new=T_NEW,
        run_mode=run_mode,
        commit=args.commit,
        embedding_model=embedding_model,
        model_configured={model_configured.split("=")[0]: model_configured.split("=")[1]},
    )
    print(f"[run] run_mode={run_mode} run_id={run_id}")
    print(f"[run] dataset_hash={dataset_hash}")
    print(f"[run] dataset_hash_method=sorted(data/scenarios/*.json) 의 파일명+내용 sha256")
    print(f"[run] commit={args.commit or '(미지정)'}")
    print(f"[run] out={out_dir}")

    judge = StubJudge() if run_mode == "stub" else None
    caller = StubSingleCaller() if run_mode == "stub" else None
    embedder: Any
    if run_mode == "stub":
        embedder = StubEmbedder()
    else:
        from app.embedding import OpenAIEmbeddingProvider

        embedder = OpenAIEmbeddingProvider()

    resolver_kwargs: dict[str, dict[str, Any]] = {}
    if caller is not None:
        resolver_kwargs["llm_single"] = {"caller": caller}

    mismatches: list[str] = []
    seen_scenarios: list[str] = []
    trace_failures: list[str] = []
    traces_dumped = 0

    def before_rollback(ctx: ToolContext, state: ScenarioState, rows: list[dict[str, Any]]) -> None:
        nonlocal traces_dumped
        ok = state.embedded_alias_count == state.alias_count
        seen_scenarios.append(state.scenario_id)
        # 결정 D(i) 롤백 전에 -- 여기서 안 뜨면 trace 는 사라진다(01-plan 236행).
        dumped = 0
        try:
            dumped = dump_er_traces(
                ctx.session,
                rows,
                traces_handle,
                session_id=ctx.session_id,
                scenario_id=state.scenario_id,
                limit_per_scenario=args.traces_per_scenario,
            )
        except TraceDumpError as exc:
            trace_failures.append(str(exc))
        traces_dumped += dumped
        print(
            f"[scenario] {state.scenario_id} aliases={state.alias_count} "
            f"embedded={state.embedded_alias_count} rows={len(rows)} "
            f"traces={dumped} {'ok' if ok else 'MISMATCH'}"
        )
        if not ok:
            mismatches.append(state.scenario_id)

    engine = get_engine()
    connection, transaction, session = _session(engine)
    traces_handle = traces_path.open("w", encoding="utf-8", newline="\n")
    try:

        def ctx_factory(scenario_id: str) -> ToolContext:
            return ToolContext(
                session=session,
                session_id=f"pilot-{run_id}-{scenario_id}",
                user_id=f"pilot-eval-{run_id}",
            )

        print(
            "[stage] runner: run_pilot(scenarios=%d, methods=%d, grid=%d)"
            % (len(scenarios), len(ALL_METHODS), len(T_MERGE_GRID))
        )
        summary = run_pilot(
            ctx_factory,
            scenarios,
            ALL_METHODS,
            T_MERGE_GRID,
            embedder=embedder,
            judge=judge,
            out_path=raw_path,
            resolver_kwargs=resolver_kwargs or None,
            env=build_runner_env(),
            before_rollback=before_rollback,
        )
    except RunnerError as exc:
        print(f"[fail] runner: {exc}")
        return RC_ERROR
    finally:
        traces_handle.close()
        session.close()
        transaction.rollback()
        connection.close()

    if mismatches:
        print(
            "[fail] embedded_alias_count != alias_count: " + ", ".join(sorted(mismatches))
        )
        return RC_ERROR

    # --- trace 표본 재계산 (원칙3·원칙9, 01-plan 106행 판정 표) --------------
    if trace_failures:
        for message in trace_failures[:10]:
            print(f"[fail] traces: {message}")
        return RC_ERROR
    recheck = recheck_trace_dump(traces_path)
    for line in format_trace_recheck(recheck):
        print(line)
    if recheck.dumped != traces_dumped:
        print(
            f"[fail] traces: 덤프 줄 수 {recheck.dumped} != 쓴 줄 수 {traces_dumped}"
        )
        return RC_ERROR
    expected_traces = summary.rows_by_method.get(TRACE_DUMP_METHOD, 0)
    if args.traces_per_scenario is None and recheck.dumped != expected_traces:
        print(
            f"[fail] traces: 덤프 {recheck.dumped} 행 != {TRACE_DUMP_METHOD} 행 "
            f"{expected_traces} (01-plan 140행 'proposed +2' 전제 -- 판정마다 "
            "er_resolve 1행)"
        )
        return RC_ERROR
    if not recheck.ok:
        return RC_ERROR

    expected_rows = summary.mention_count * len(ALL_METHODS) * len(T_MERGE_GRID)
    print(
        f"[rows] rows={summary.row_count} = mentions={summary.mention_count} "
        f"× methods={len(ALL_METHODS)} × t_merge={len(T_MERGE_GRID)} "
        f"(expected={expected_rows})"
    )
    for method in ALL_METHODS:
        print(f"[rows] {method}={summary.rows_by_method.get(method, 0)}")
    if summary.row_count != expected_rows:
        print("[fail] row_count != mentions × methods × t_merge")
        return RC_ERROR
    if summary.llm_repeat_calls:
        print(f"[fail] llm_repeat_calls={summary.llm_repeat_calls} (결정 C(i) 위반)")
        return RC_ERROR
    print(f"[rows] raw={raw_path}")

    # --- 커밋용 gzip (결정 E 이행 방식, 사용자 결정 2026-09-21) --------------
    plain_bytes = raw_path.stat().st_size
    try:
        raw_gz_path, plain_digest = gzip_jsonl(
            raw_path, raw_gz_path, drop_plain=args.drop_raw_plain
        )
    except GzipError as exc:
        print(f"[fail] {exc}")
        return RC_ERROR
    print(
        f"[gzip] {raw_gz_path} {raw_gz_path.stat().st_size} bytes "
        f"(평문 {plain_bytes} bytes, level={GZIP_COMPRESSLEVEL}, mtime=0·파일명 미기록)"
    )
    print(
        f"[gzip] roundtrip_sha256={plain_digest} ok "
        f"plain={'삭제' if args.drop_raw_plain else '보존'} -- 이후 단계 입력은 압축본이다"
    )
    rows_arg = str(raw_gz_path)

    network_calls = 0 if run_mode == "stub" else summary.llm_calls_by_method.get(
        "proposed", 0
    ) + summary.llm_calls_by_method.get("llm_single", 0) + summary.embed_calls
    print(
        f"[run] run_mode={run_mode} network_calls={network_calls} "
        f"stub_llm_calls={(judge.calls if judge else 0) + (caller.calls if caller else 0)} "
        f"stub_embed_calls={getattr(embedder, 'calls', 0)}"
    )
    print(
        "[run] tokens_in=%d tokens_out=%d (실행 실측 합계, llm_fresh_call 행만%s)"
        % (
            sum(summary.tokens_in_by_method.values()),
            sum(summary.tokens_out_by_method.values()),
            " -- 스텁은 토큰을 세지 않으므로 0 이다" if run_mode == "stub" else "",
        )
    )

    stages: list[_Stage] = []
    rc = _run_stage(
        "metrics",
        metrics_mod,
        ["--rows", rows_arg, "--out", str(stage_metrics)],
        stages,
    )
    if rc != 0:
        return RC_ERROR
    rc = _run_stage(
        "calibration",
        calibration_mod,
        [
            "--rows",
            rows_arg,
            "--out",
            str(calibration_path),
            "--t-merge",
            "0.8",
            "--model-configured",
            model_configured,
        ],
        stages,
    )
    if rc != 0:
        return RC_ERROR
    curve_argv = [
        "--rows",
        rows_arg,
        "--out",
        str(metrics_path),
        "--curve",
        str(curve_path),
        "--dataset-hash",
        dataset_hash,
        "--run-id",
        run_id,
        "--embedding-model",
        embedding_model,
        "--model-configured",
        model_configured,
        "--run-mode",
        run_mode,
    ]
    if args.commit:
        curve_argv += ["--commit", args.commit]
    rc = _run_stage("curve", curve_mod, curve_argv, stages)
    if rc != 0:
        return RC_ERROR
    rc = _run_stage("validate", metrics_mod, ["--validate", str(metrics_path)], stages)
    if rc != 0:
        return RC_ERROR
    rc = _run_stage(
        "report",
        report_mod,
        ["--metrics", str(metrics_path), "--out", str(report_path)],
        stages,
    )
    if rc != 0:
        return RC_ERROR

    missing = [
        p
        for p in (raw_gz_path, traces_path, metrics_path, calibration_path, curve_path, report_path)
        if not p.exists()
    ]
    if missing:
        print("[fail] 산출물 누락: " + ", ".join(str(p) for p in missing))
        return RC_ERROR
    for path in (
        raw_path,
        raw_gz_path,
        traces_path,
        stage_metrics,
        metrics_path,
        calibration_path,
        curve_path,
        report_path,
    ):
        if not path.exists():  # 평문은 --drop-raw-plain 이면 없다
            continue
        print(f"[out] {path} ({path.stat().st_size} bytes)")
    # 커밋 대상(결정 E)만 한도와 대조한다 -- 평문 raw 와 중간 산출물
    # `metrics-stage.json` 은 커밋하지 않는다.
    for line in format_commit_sizes([raw_gz_path, traces_path]):
        print(line)
    print("[ok] 사슬 완료 -- runner → metrics → calibration → curve → validate → report")
    return RC_OK


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python scripts/run_pilot_eval.py",
        description=(
            "파일럿 평가 실행 CLI -- 예상 비용을 먼저 찍고, 상한을 넘지 않으면 "
            "runner→metrics→calibration→curve→report 를 순서대로 돌린다"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="네트워크 0 모드. --stub 과 함께 쓴다(실 공급자를 만들지 않는다)",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="스텁 판정기·스텁 단일호출·결정적 가짜 임베딩(--dry-run 필요)",
    )
    parser.add_argument("--out", default=None, help="산출물 디렉터리(추정만 볼 때는 생략)")
    parser.add_argument(
        "--scenarios", default=str(DEFAULT_SCENARIO_DIR), help="시나리오 디렉터리"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="앞에서부터 N 시나리오만(스모크용)"
    )
    parser.add_argument(
        "--max-cost-usd",
        type=float,
        default=DEFAULT_MAX_COST_USD,
        help=f"예상 비용 상한(USD, 기본 {DEFAULT_MAX_COST_USD} -- 결정 B). 넘으면 실행하지 않는다",
    )
    parser.add_argument("--price-in", type=float, default=PRICE_IN_PER_1M)
    parser.add_argument("--price-out", type=float, default=PRICE_OUT_PER_1M)
    parser.add_argument("--price-embed", type=float, default=PRICE_EMBED_PER_1M)
    parser.add_argument(
        "--commit", default=None, help="평가한 커밋 해시(L-001). meta.commit 에 그대로 실린다"
    )
    parser.add_argument(
        "--run-id", default=None, help="생략하면 결정적으로 계산한다(시각 미포함)"
    )
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="추정만 찍고 끝낸다(실행하지 않는다)",
    )
    parser.add_argument(
        "--traces-per-scenario",
        type=int,
        default=None,
        help=(
            "시나리오당 덤프할 er_resolve trace 줄 수(기본 전량). "
            "표본을 고르는 순간 판정을 유리하게 만들 여지가 생기므로 기본은 전량이다(원칙8)"
        ),
    )
    parser.add_argument(
        "--drop-raw-plain",
        action="store_true",
        help=(
            "gzip 왕복 검증을 통과한 뒤 평문 raw-<ts>.jsonl 을 지운다"
            "(기본은 보존 -- 커밋 대상은 .gz 하나다)"
        ),
    )
    parser.add_argument(
        "--recheck-traces",
        default=None,
        metavar="PATH",
        help=(
            "덤프된 traces-<ts>.jsonl 만 입력으로 확신도를 다시 계산한다"
            "(DB·네트워크 0). 다른 인자는 무시하고 재계산만 하고 끝낸다"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.recheck_traces:
        target = Path(args.recheck_traces)
        if not target.exists():
            print(f"[fail] traces: {target} 가 없다")
            return RC_ERROR
        result = recheck_trace_dump(target)
        for line in format_trace_recheck(result):
            print(line)
        return RC_OK if result.ok else RC_ERROR

    if args.traces_per_scenario is not None and args.traces_per_scenario <= 0:
        parser.error("--traces-per-scenario 는 1 이상이다(0 이면 증거가 없다)")
    if args.stub and not args.dry_run:
        parser.error("--stub 은 --dry-run 과 함께 쓴다(스텁 수치를 실 결과로 두지 않는다)")
    if args.dry_run and not args.stub:
        parser.error("--dry-run 은 --stub 이 필요하다(실 공급자 없이 돌릴 방법이 스텁뿐이다)")

    run_mode = "stub" if args.stub else "real"
    scenarios = [scenario for _, scenario in load_scenarios(args.scenarios)]
    if args.limit is not None:
        if args.limit <= 0:
            parser.error("--limit 는 1 이상이다")
        scenarios = scenarios[: args.limit]

    estimate = estimate_run(
        scenarios,
        price_in_per_1m=args.price_in,
        price_out_per_1m=args.price_out,
        price_embed_per_1m=args.price_embed,
    )
    for line in format_estimate(estimate, run_mode=run_mode, max_cost_usd=args.max_cost_usd):
        print(line)

    if estimate.usd_total > args.max_cost_usd:
        print(
            f"[fail] 예상 비용 {estimate.usd_total:.4f} USD 가 상한 {args.max_cost_usd} USD "
            "를 넘는다 -- 한 줄도 실행하지 않는다(결정 B). --max-cost-usd 로 올리거나 "
            "--limit 로 범위를 줄인다"
        )
        return RC_COST_LIMIT

    if run_mode == "real":
        missing = missing_real_env()
        if missing:
            print(
                "[fail] 실 실행에 필요한 환경변수가 없다(이름만 표시한다): "
                + ", ".join(missing)
            )
            print(
                "[hint] 값은 사용자 셸에만 둔다 -- 이 스크립트는 .env 를 읽지 않는다"
                " (docs/user-setup/10-pilot-eval-run.md)"
            )
            print(f"[hint] 있으면 결과에 남는 선택 변수: {', '.join(OPTIONAL_REAL_ENV)}")
            return RC_MISSING_KEYS

    if args.estimate_only:
        print("[ok] --estimate-only -- 실행하지 않는다")
        return RC_OK
    if not args.out:
        parser.error("--out 이 필요하다(--estimate-only 가 아니면 산출물 디렉터리를 준다)")

    out_dir = Path(args.out).resolve()
    if run_mode == "stub":
        repo_reports = (Path(__file__).resolve().parents[1] / FORBIDDEN_STUB_OUT_DIR).resolve()
        if out_dir == repo_reports or repo_reports in out_dir.parents:
            print(
                f"[fail] 스텁 산출물을 {FORBIDDEN_STUB_OUT_DIR}/ 아래에 쓰지 않는다 "
                "-- 스텁 수치는 결과가 아니다(원칙8). 임시 디렉터리를 쓴다"
            )
            return RC_ERROR

    try:
        return _run_chain(args, scenarios)
    except Exception as exc:  # noqa: BLE001 -- 실패도 결과다(원칙8): 이유를 남기고 rc≠0
        print(f"[fail] {type(exc).__name__}: {exc}")
        return RC_ERROR


if __name__ == "__main__":  # pragma: no cover -- CLI 진입점
    raise SystemExit(main())
