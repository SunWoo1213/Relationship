"""Refs: P3-baselines 01-plan 61행·104행(U5) 원칙8 -- 베이스라인 3 실 LLM 1회 스모크.

`evaluation/resolvers/llm_single.py` 의 `caller_from_env()`로 공급자를
고른다(`LLM_PROVIDER`, 기본 `anthropic`). **DB 를 쓰지 않는다** -- 사전
상태 인물 3명을 이 스크립트 안에서 `KnownPerson` 으로 직접 만들고, mention
"부장님" · 짧은 발화 하나로 `resolve_from_state()` 를 1회 호출한다. 평가에서
실제로 도는 것과 **같은 함수**를 부르므로(프롬프트 조립·강등 규칙의 이중
출처가 없다) 여기서 본 것이 P4 에서 도는 것과 같다.

자동 테스트가 아니다(`tests/test_baseline_llm_single.py` 는 전부 스텁
클라이언트로 네트워크 0 이다) -- 실 호출은 **사용자가 직접** 키를 넣어
실행한다(`docs/wiki/user-setup/` 스모크 카드, 원칙8: LLM 출력은 재현
불가능하므로 자동 테스트에 넣지 않는다).

`.env` 는 읽지 않는다(security.md §1) -- 공급자별로 필요한 키
(`anthropic` → `ANTHROPIC_API_KEY`, `openai` → `OPENAI_API_KEY`)가
`os.environ` 에 없으면 **종료 코드 2** 와 이름만 안내한다. 출력에는
**키·프롬프트 원문을 절대 넣지 않는다** -- JSON 한 줄에 `method`·
`decision`·`person_id`·`score`(=`s_llm`)·`tokens_in`/`tokens_out`·
`provider`·`model`·`forced_reason`·`candidate_person_ids`·`dropped_ids`·
`prompt_chars`·`person_count` 만 담는다(프롬프트는 **길이만**).

사용:
    ANTHROPIC_API_KEY=... python scripts/baseline_smoke.py
    LLM_PROVIDER=openai OPENAI_API_KEY=... python scripts/baseline_smoke.py --provider openai
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# 스크립트로 직접 실행될 때 저장소 루트를 sys.path 에 넣는다
# (scripts/er_smoke.py·scripts/tools_check.py 와 동일).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.resolvers.exact_match import KnownPerson  # noqa: E402
from evaluation.resolvers.llm_single import (  # noqa: E402
    METHOD_NAME,
    caller_from_env,
    resolve_from_state,
)

#: 공급자 -> 필요한 키 환경변수 **이름**(값은 읽지도 출력하지도 않는다).
#: `scripts/er_smoke.py` 와 같은 표다.
_REQUIRED_KEY_BY_PROVIDER = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}

_MENTION = "부장님"
_UTTERANCE = "부장님이 오늘 회식 잡으라고 하셨어."


def sample_state() -> list[KnownPerson]:
    """사전 상태 3명(승진 호칭 "부장님"은 **없다**) -- P1 결정 I 가 만든
    성질 그대로다. 이 방식이 맥락만으로 "팀장"과 이으려 하는지, 아니면
    묻는지(`identity`)를 실호출 1회로 눈으로 본다."""

    return [
        KnownPerson(
            person_id=1,
            display_name="김민수",
            names=("팀장", "김팀장"),
            relation_tag="직장",
            hierarchy="상",
        ),
        KnownPerson(
            person_id=2,
            display_name="박민수",
            names=("민수",),
            relation_tag="친구",
            hierarchy="동",
        ),
        KnownPerson(
            person_id=3,
            display_name="이영희",
            names=("과장",),
            relation_tag="직장",
            hierarchy="동",
        ),
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="실 LLM 1회 호출 베이스라인 3(llm_single) 스모크"
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM_PROVIDER 를 오버라이드한다(anthropic|openai). 기본은 환경변수/설정값",
    )
    return parser


def to_output(decision) -> dict:
    """출력용 축약 -- **키·프롬프트 원문을 담지 않는다**(security.md §1).
    `detail` 을 통째로 찍지 않고 필요한 열만 고른다."""

    detail = decision.detail
    return {
        "method": decision.method,
        "mention": decision.mention,
        "decision": decision.decision,
        "person_id": decision.person_id,
        "score": decision.score,
        "tokens_in": decision.tokens_in,
        "tokens_out": decision.tokens_out,
        "provider": detail.get("provider"),
        "model": detail.get("model"),
        "forced_reason": detail.get("forced_reason"),
        "llm_error": detail.get("llm_error"),
        "candidate_person_ids": [c.person_id for c in decision.candidates],
        "dropped_ids": detail.get("dropped_ids"),
        "prompt_chars": detail.get("prompt_chars"),
        "person_count": detail.get("person_count"),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    env = dict(os.environ)
    if args.provider:
        env["LLM_PROVIDER"] = args.provider

    from app.settings import LLM_PROVIDER as _DEFAULT_PROVIDER

    provider_name = env.get("LLM_PROVIDER", _DEFAULT_PROVIDER)
    required_key = _REQUIRED_KEY_BY_PROVIDER.get(provider_name)
    if required_key is not None and not env.get(required_key):
        print(
            f"[error] {required_key} 환경변수가 설정되지 않았다. 실 LLM 호출은 "
            "os.environ 에 그 변수를 직접 넣어야 한다(.env 는 읽지 않는다, "
            "security.md §1 -- .env.example 참조)."
        )
        return 2

    caller = caller_from_env(env)
    decision = resolve_from_state(
        sample_state(), _MENTION, _UTTERANCE, caller=caller
    )

    print(json.dumps(to_output(decision), ensure_ascii=False))

    # 호출 실패도 예외가 아니라 `identity` 강등으로 나온다(불변 규약 2) --
    # 스모크는 그 사실을 종료 코드로 구분해 사용자가 바로 알게 한다.
    if decision.detail.get("llm_error"):
        return 3
    if decision.method != METHOD_NAME:  # 도달 불가 -- 방식 이름 오염 방어.
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
