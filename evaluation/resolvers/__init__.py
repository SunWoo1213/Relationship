"""Refs: P3-baselines S3.7 D10 원칙2 원칙8 -- 네 방식의 공개 진입점.

P4 러너와 계약 테스트는 이 패키지 하나만 import 한다::

    from evaluation.resolvers import ALL_METHODS, get_resolver
    for name in ALL_METHODS:
        decision = get_resolver(name, **kwargs_by_method[name]).resolve_mention(
            ctx, mention, utterance, hints, config=config
        )

방식 모듈(U2~U5: `proposed`·`exact_match`·`embedding_only`·`llm_single`)은
**여기서 import 해야** `register()` 가 실행되어 `RESOLVERS`/`ALL_METHODS` 에
나타난다. import 순서가 곧 `ALL_METHODS` 순서이고 그 순서로 P4 표가 나온다
-- U2~U5 가 아래 "방식 모듈 import" 자리에 한 줄씩 추가한다(U1 시점에는
방식이 하나도 없으므로 비어 있다).

`ALL_METHODS` 는 접근 시점에 계산된다(`registry.__getattr__`, PEP 562).
`from evaluation.resolvers import ALL_METHODS` 로 받은 값은 그 순간의
스냅샷이므로, 런타임에 추가 등록을 하는 코드는
`from evaluation.resolvers import registry` 후 `registry.ALL_METHODS` 로
읽는다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from evaluation.resolvers.base import (
    DECISIONS,
    MentionDecision,
    Resolver,
    ResolverCandidate,
)
from evaluation.resolvers.registry import (
    RESOLVERS,
    get_resolver,
    register,
)

# --- 방식 모듈 import (등록 순서 = ALL_METHODS 순서) ---------------------
from evaluation.resolvers import proposed  # noqa: F401  -- register("proposed")
from evaluation.resolvers import exact_match  # noqa: F401  -- register("exact_raw"/"exact_norm")
# U4: from evaluation.resolvers import embedding_only  # noqa: F401
# U5: from evaluation.resolvers import llm_single      # noqa: F401

if TYPE_CHECKING:  # 값은 `__getattr__` 이 만든다(등록 시점에 따라 달라진다).
    ALL_METHODS: tuple[str, ...]

__all__ = [
    "DECISIONS",
    "MentionDecision",
    "Resolver",
    "ResolverCandidate",
    "RESOLVERS",
    "get_resolver",
    "register",
    "ALL_METHODS",
]


def __getattr__(attr: str) -> Any:
    if attr == "ALL_METHODS":
        return tuple(RESOLVERS)
    raise AttributeError(f"module {__name__!r} has no attribute {attr!r}")


def __dir__() -> list[str]:
    return sorted([*globals().keys(), "ALL_METHODS"])
