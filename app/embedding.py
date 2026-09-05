"""Refs: P2-tools S3.2 S3.3 D4 D5 -- 임베딩 공급자 인터페이스(구현체 없음).

D4: 임베딩 호출은 반드시 이 인터페이스 뒤에 둔다. 공급자 교체가 클래스 하나
추가로 끝나야 한다. 이 모듈은 **Protocol 만** 정의한다 -- 실제 공급자
(`OpenAIEmbeddingProvider`, `text-embedding-3-small`)는 `scripts/embed_pilot.py`
에 결정용 코드로만 있고, 그 호출을 `app/` 으로 옮겨 `ctx.embedder` 에 꽂는 일은
**P3-er** 에서 한다(01-plan 결정4 -- P2 단위 테스트가 네트워크·`OPENAI_API_KEY`
에 묶이면 재현성이 깨진다, 원칙8). `openai` 는 여전히 `requirements.txt` 에
없다.

`EMBEDDING_DIM = 1536` 은 D4 확정값(`text-embedding-3-small`, 근거
`reports/embed_pilot.md`)과 `person_aliases.embedding vector(1536)` 의
차원이 같은 출처에서 나온다는 것을 코드로 보여주는 상수다 -- 마이그레이션의
하드코딩된 `1536` 을 여기서 재정의하지 않는다(값 집합 상수의 단일 출처는
`app/db/models.py` 라는 관례처럼, 이 상수의 단일 출처는 이 모듈이다).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

#: D4 확정값(2026-09-03, P0-embed-pilot U2·U3) -- `text-embedding-3-small`.
EMBEDDING_DIM = 1536


@runtime_checkable
class EmbeddingProvider(Protocol):
    """임베딩 공급자 인터페이스. `scripts/embed_pilot.py` 의 동명 Protocol과
    같은 계약(`embed(texts) -> list[list[float]]`)이지만, `dimension`/`name`
    같은 파일럿 전용 속성은 요구하지 않는다 -- 툴 계층이 실제로 쓰는 것은
    `embed()` 하나뿐이다."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...


#: `ToolContext.embedder` 가 아직 `EmbeddingProvider` 로 감싸지지 않은 순수
#: 콜러블(`tests/conftest.py` 의 `fake_embedder` 형태)을 받을 때의 타입.
EmbedderCallable = Callable[[list[str]], list[list[float]]]


class _CallableEmbeddingProvider:
    """평범한 콜러블을 `EmbeddingProvider` 모양으로 감싸는 얇은 어댑터."""

    def __init__(self, fn: EmbedderCallable) -> None:
        self._fn = fn

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._fn(texts)


def as_provider(
    embedder: "EmbeddingProvider | EmbedderCallable | None",
) -> "EmbeddingProvider | None":
    """`ctx.embedder` 를 `EmbeddingProvider` 로 정규화한다.

    - `None` -> `None` (임베딩 단계를 건너뛴다는 신호, 호출자가 그대로 판단).
    - 이미 `embed()` 메서드를 가진 객체(`EmbeddingProvider` 를 만족) -> 그대로.
    - 평범한 콜러블(`list[str] -> list[list[float]]`, 예: `fake_embedder`)
      -> `_CallableEmbeddingProvider` 로 감싼다.
    - 그 밖의 값 -> `TypeError` (호출자 실수를 조용히 삼키지 않는다).
    """
    if embedder is None:
        return None
    if isinstance(embedder, EmbeddingProvider):
        return embedder
    if callable(embedder):
        return _CallableEmbeddingProvider(embedder)
    raise TypeError(
        f"ctx.embedder must be None, EmbeddingProvider, or a callable; got {type(embedder)!r}"
    )
