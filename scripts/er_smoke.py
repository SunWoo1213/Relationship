"""Refs: P3-er 01-plan 44행·94행(U8)·결정9 -- 실 LLM 1회 호출 ER 판정 스모크.

`judge_from_env()`(`app/er/judge.py`)로 공급자를 고른다(`LLM_PROVIDER`,
기본 `anthropic`). **DB 를 쓰지 않는다** -- 후보 2개를 이 스크립트 안에서
직접 `ScoredCandidate` 로 만들고, mention "부장님" · 짧은 발화 하나로
`judge.judge(...)` 를 1회 호출한다. 자동 테스트(`tests/test_er_smoke.py`)는
`FakeJudge` 로 `run_smoke()` 만 검증하고 **실제 API 호출은 하지 않는다**
(원칙8 -- LLM 출력은 재현 불가능하므로 자동 테스트에 넣지 않는다).

`.env` 는 읽지 않는다(security.md §1) -- 공급자별로 필요한 키
(`anthropic` → `ANTHROPIC_API_KEY`, `openai` → `OPENAI_API_KEY`)가
`os.environ` 에 없으면 종료 코드 2 와 **이름만** 안내한다. `JudgeUnavailable`
이면(타임아웃·API 오류·스키마 위반 등) `{"error": <유형>}` 을 출력하고
종료 코드 3. 출력에는 **프롬프트 원문 전체·키를 절대 넣지 않는다** -- JSON
한 줄에 `provider`·`model`·`tokens_in`·`tokens_out`·`s_llm`·
`matched_person_id`·`reason`·`confidence`·`band` 만 담는다.

사용:
    ANTHROPIC_API_KEY=... python scripts/er_smoke.py
    LLM_PROVIDER=openai OPENAI_API_KEY=... python scripts/er_smoke.py --provider openai
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# 스크립트로 직접 실행될 때 `app` 패키지를 찾을 수 있도록 저장소 루트를
# sys.path 에 넣는다(scripts/db_check.py·scripts/tools_check.py 와 동일).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.er.confidence import band_for, combine  # noqa: E402
from app.er.judge import Judge, judge_from_env  # noqa: E402
from app.er.types import ERConfig, JudgeUnavailable, ScoredCandidate  # noqa: E402

#: 공급자 -> 필요한 키 환경변수 이름(위임 프롬프트 그대로). 여기 없는
#: 공급자(예: `gemini`)는 키 사전 확인을 건너뛰고 `judge_from_env()` 의
#: 오류 메시지에 맡긴다(이름을 지어내지 않는다).
_REQUIRED_KEY_BY_PROVIDER = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}

_MENTION = "부장님"
_UTTERANCE = "부장님이 오늘 회식 잡으라고 하셨어."


def _sample_candidates() -> list[ScoredCandidate]:
    """위임 프롬프트가 못박은 두 후보(규칙 통과 상태로 이미 채점된 값)."""
    return [
        ScoredCandidate(
            person_id=1,
            display_name="김민수",
            aliases=["팀장", "김팀장"],
            relation_tag="직장",
            hierarchy="동",
            s_emb=0.85,
            rule_checked=3,
            rule_passed=2,
            s_rule=0.667,
            passed_rules=True,
        ),
        ScoredCandidate(
            person_id=2,
            display_name="박민수",
            aliases=["친구"],
            relation_tag="친구",
            hierarchy="동",
            s_emb=0.4,
            rule_checked=2,
            rule_passed=1,
            s_rule=0.5,
            passed_rules=True,
        ),
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="실 LLM 1회 호출 ER 판정 스모크")
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM_PROVIDER 를 오버라이드한다(anthropic|openai). 기본은 환경변수/설정값",
    )
    return parser


def run_smoke(
    judge: Judge, candidates: list[ScoredCandidate], config: ERConfig
) -> dict:
    """`judge` 를 1회 호출해 confidence·band 까지 계산한 JSON 가능 dict 를
    만든다. 실 호출·`FakeJudge` 양쪽이 이 함수를 공유한다 -- 자동 테스트는
    `FakeJudge` 를 주입해 이 함수만 검증하고, 실제 네트워크 호출은 하지
    않는다(원칙8).

    `matched_person_id` 가 후보 밖(예: `None`)이면 `s_emb`/`s_rule` 을
    0 으로 두고 `combine()`/`band_for()` 를 그대로 적용한다 -- P3 파이프라인
    (`app/er/confidence.decide`)의 null 귀속 규약(결정3-c)과 같은 방향이다.
    """
    judgement = judge.judge(_MENTION, _UTTERANCE, candidates)
    candidate_by_id = {c.person_id: c for c in candidates}
    matched = candidate_by_id.get(judgement.matched_person_id)
    s_emb = matched.s_emb if matched is not None else 0.0
    s_rule = matched.s_rule if matched is not None else 0.0
    confidence = combine(judgement.s_llm, s_emb, s_rule, config)
    band = band_for(confidence, config)
    return {
        "provider": judgement.provider,
        "model": judgement.model,
        "tokens_in": judgement.tokens_in,
        "tokens_out": judgement.tokens_out,
        "s_llm": judgement.s_llm,
        "matched_person_id": judgement.matched_person_id,
        "reason": judgement.reason,
        "confidence": confidence,
        "band": band,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    env = dict(os.environ)
    if args.provider:
        env["LLM_PROVIDER"] = args.provider

    from app.settings import LLM_PROVIDER as _DEFAULT_PROVIDER
    from app.settings import er_config

    provider_name = env.get("LLM_PROVIDER", _DEFAULT_PROVIDER)
    required_key = _REQUIRED_KEY_BY_PROVIDER.get(provider_name)
    if required_key is not None and not env.get(required_key):
        print(
            f"[error] {required_key} 환경변수가 설정되지 않았다. 실 LLM 호출은 "
            "os.environ 에 그 변수를 직접 넣어야 한다(.env 는 읽지 않는다, "
            "security.md §1 -- .env.example 참조)."
        )
        return 2

    try:
        judge = judge_from_env(env)
        result = run_smoke(judge, _sample_candidates(), er_config(env))
    except JudgeUnavailable as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 3

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
