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

## 하지 않는 것

실 API 호출(U7), `reports/` 실물 작성(U7), 실패 케이스 분석(U8). 지표
계산을 여기서 다시 하지 않는다 -- 전부 U2~U5 모듈의 `main(argv)` 을 부르고
돌아온 정수 rc 만 본다.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import random
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover -- `python scripts/...` 직접 실행
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.embedding import EMBEDDING_DIM
from app.er.judge import FakeJudge
from app.er.judge import build_prompt as build_judge_prompt
from app.er.types import ERConfig, Judgement, ScoredCandidate
from app.tools.context import ToolContext
from evaluation import calibration as calibration_mod
from evaluation import curve as curve_mod
from evaluation import metrics as metrics_mod
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

    def before_rollback(ctx: ToolContext, state: ScenarioState, rows: list[dict[str, Any]]) -> None:
        ok = state.embedded_alias_count == state.alias_count
        seen_scenarios.append(state.scenario_id)
        print(
            f"[scenario] {state.scenario_id} aliases={state.alias_count} "
            f"embedded={state.embedded_alias_count} rows={len(rows)} "
            f"{'ok' if ok else 'MISMATCH'}"
        )
        if not ok:
            mismatches.append(state.scenario_id)

    engine = get_engine()
    connection, transaction, session = _session(engine)
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
        session.close()
        transaction.rollback()
        connection.close()

    if mismatches:
        print(
            "[fail] embedded_alias_count != alias_count: " + ", ".join(sorted(mismatches))
        )
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
        ["--rows", str(raw_path), "--out", str(stage_metrics)],
        stages,
    )
    if rc != 0:
        return RC_ERROR
    rc = _run_stage(
        "calibration",
        calibration_mod,
        [
            "--rows",
            str(raw_path),
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
        str(raw_path),
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

    missing = [p for p in (raw_path, metrics_path, calibration_path, curve_path, report_path) if not p.exists()]
    if missing:
        print("[fail] 산출물 누락: " + ", ".join(str(p) for p in missing))
        return RC_ERROR
    for path in (raw_path, stage_metrics, metrics_path, calibration_path, curve_path, report_path):
        print(f"[out] {path} ({path.stat().st_size} bytes)")
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

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
