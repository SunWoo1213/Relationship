"""Refs: P2-tools S3.2 S3.3 D4 D5 -- 임베딩 공급자(런타임 단일 출처, P3-er U2).

D4: 임베딩 호출은 반드시 이 인터페이스 뒤에 둔다. 공급자 교체가 클래스 하나
추가로 끝나야 한다. `OpenAIEmbeddingProvider`(`text-embedding-3-small`)가
이 모듈의 **런타임 단일 출처**다(01-plan 결정6-a) -- `scripts/embed_pilot.py`
의 동명 클래스는 **의도적으로 남겨 둔다**: 파일럿은 `text-embedding-3-small`
과 `text-embedding-3-large` 를 둘 다 돌려 실제 반환 벡터의 차원을 비교해야
하는데(D4 결정 근거 자료), 이 모듈의 `dimension` 은 결정6-b 에 따라 모델과
무관하게 **호출 없이 상수 `EMBEDDING_DIM`을 돌려준다** -- 파일럿이 요구하는
"실제로 받은 벡터 길이"와 정반대 계약이라 하나로 합칠 수 없다(같은 이유로
파일럿의 `name`/`usage`(토큰 사용량 집계) 계약도 이 모듈에는 없다). 우회
구현(예: 모델별 차원 조회표를 만들어 두 계약을 합치는 것)을 하지 않고
파일럿 쪽 클래스를 그대로 두었다 -- 자세한 근거는
`docs/wiki/packages/P3-er/03-log.md` U2 항목.

이 모듈과 `app/settings.py`·`scripts/backfill_embeddings.py`·
`scripts/er_smoke.py` 는 `.env` 를 읽지 않고 `os.environ` 만 본다
(security.md §1); `.env` 를 조용히 불러오는 편의 함수는 `scripts/embed_pilot.py`
에만 있다(그 스크립트만 사용자가 직접 실행하는 결정용 도구다).

`EMBEDDING_DIM = 1536` 은 D4 확정값(`text-embedding-3-small`, 근거
`reports/embed_pilot.md`)과 `person_aliases.embedding vector(1536)` 의
차원이 같은 출처에서 나온다는 것을 코드로 보여주는 상수다 -- 마이그레이션의
하드코딩된 `1536` 을 여기서 재정의하지 않는다(값 집합 상수의 단일 출처는
`app/db/models.py` 라는 관례처럼, 이 상수의 단일 출처는 이 모듈이다).
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Protocol

#: D4 확정값(2026-09-03, P0-embed-pilot U2·U3) -- `text-embedding-3-small`.
EMBEDDING_DIM = 1536


class EmbeddingProvider(Protocol):
    """임베딩 공급자 인터페이스. `scripts/embed_pilot.py` 의 동명 Protocol과
    비슷하지만 `name`/`usage` 같은 파일럿 전용 속성은 요구하지 않는다 --
    툴 계층이 실제로 쓰는 것은 `embed()`와 `dimension`(D4, 결정6-b: 호출 없이
    알 수 있는 차원)뿐이다.

    `isinstance(x, EmbeddingProvider)` 로 판별하지 않는다 -- `as_provider()`
    는 `embed` 속성 존재만 확인한다(아래 참고). 이 Protocol 은 타입 힌트
    용도로만 남긴다.
    """

    @property
    def dimension(self) -> int: ...

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
    - `embed` 속성을 가진 객체 -> 그대로 (U2: `isinstance(x, EmbeddingProvider)`
      대신 `embed` 속성 존재만 확인한다 -- Protocol 전체 구조를 검사하면
      `dimension` 같은 다른 속성 접근에서 예외를 던지는 공급자를 만났을 때
      `isinstance()` 자체가 그 예외를 그대로 전파해 오판할 수 있다. `embed`
      하나만 확인하면 그런 부작용 없는 속성만 건드린다).
    - 평범한 콜러블(`list[str] -> list[list[float]]`, 예: `fake_embedder`)
      -> `_CallableEmbeddingProvider` 로 감싼다.
    - 그 밖의 값 -> `TypeError` (호출자 실수를 조용히 삼키지 않는다).
    """
    if embedder is None:
        return None
    if getattr(embedder, "embed", None) is not None:
        return embedder
    if callable(embedder):
        return _CallableEmbeddingProvider(embedder)
    raise TypeError(
        f"ctx.embedder must be None, EmbeddingProvider, or a callable; got {type(embedder)!r}"
    )


def check_dimension(vector: list[float], expected: int = EMBEDDING_DIM) -> None:
    """벡터 길이가 `expected` 와 다르면 저장(flush) **전에** 사람이 읽는
    오류를 낸다(D4 결정6-b, F-ca12ad 와 같은 축 -- F-3ca6b5).

    `app/tools/persons.py._add_alias` 가 `PersonAlias(embedding=...)` 를
    `session.add()`/`flush()` 하기 **직전**에 이 함수를 부른다. 이렇게 하면
    차원 불일치가 pgvector 의 `DataError`(flush 시점에만 드러나고, 실패한
    flush 뒤 같은 세션에 `tool_error` 를 기록하려다 `PendingRollbackError`
    로 원래 예외가 가려지는 F-ca12ad 경로)로 새는 대신, 세션을 무효로
    만들지 않는 평범한 파이썬 예외로 먼저 걸린다.

    오류 클래스는 새로 만들지 않고 이미 있는 툴 검증 오류 계열
    (`app.tools.types.InvalidValue`)을 재사용한다(과제 지시 "툴의 검증
    오류 계열이 이미 있으면 그것"). `app.tools.types` 를 모듈 최상단에서
    import 하면 `app.tools` 패키지(`__init__.py`)가 `app.tools.persons`/
    `app.tools.context` 를 거쳐 다시 이 모듈을 참조하는 순환 임포트가
    생기므로, 호출 시점에만 지연 import 한다.
    """
    if len(vector) != expected:
        from app.tools.types import InvalidValue

        raise InvalidValue(
            f"embedding dimension mismatch: expected {expected}, got {len(vector)}"
        )


class OpenAIEmbeddingProvider:
    """OpenAI 임베딩 런타임 공급자(결정6-a: 이 모듈이 단일 출처).

    `text-embedding-3-small` 고정(D4). `dimension` 은 결정6-b 에 따라
    **호출 없이** 상수 `EMBEDDING_DIM` 을 돌려준다 -- 실제 응답 벡터 길이는
    `check_dimension()` 이 저장 직전에 따로 확인한다(이 클래스 자체는 응답
    길이를 검증하지 않는다 -- 검증은 호출자의 책임, 단일 검증 지점을 두기
    위해서다).

    키는 `os.environ["OPENAI_API_KEY"]` 로만 읽는다 -- `.env` 는 읽지
    않는다(security.md §1, 모듈 docstring). 키가 없으면 클라이언트를 만들기
    **전에** 사람이 읽는 `RuntimeError` 를 내고, 메시지에 키 문자열을 절대
    넣지 않는다. `openai` SDK 는 함수 안에서만 지연 import 한다 -- SDK가
    설치돼 있지 않아도 이 모듈의 나머지 부분과 `app` 임포트가 깨지지 않게
    하기 위해서다.

    `client` 인자는 테스트가 네트워크 없이 스텁을 주입하기 위한 자리다(운영
    경로에서는 쓰지 않는다) -- `client` 를 넘기면 키 존재 확인도 건너뛴다
    (스텁은 이미 "연결된" 상태를 흉내 내는 것이므로).
    """

    def __init__(self, model: str = "text-embedding-3-small", *, client: object = None) -> None:
        self.model = model
        self._client = client

    @property
    def dimension(self) -> int:
        return EMBEDDING_DIM

    def _get_client(self):
        if self._client is None:
            if not os.environ.get("OPENAI_API_KEY"):
                raise RuntimeError(
                    "OPENAI_API_KEY 환경변수가 설정되지 않았다. os.environ 에 "
                    "직접 넣어야 한다(.env.example 참조 -- 이 모듈은 .env 를 "
                    "읽지 않는다, security.md §1)."
                )
            from openai import OpenAI  # 지연 import: 키·SDK 없이도 임포트는 된다

            self._client = OpenAI()
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        """배치 호출 하나로 `texts` 전체를 임베딩한다(호출 수를 늘리지 않는다)."""
        if not texts:
            return []
        client = self._get_client()
        resp = client.embeddings.create(model=self.model, input=list(texts))
        return [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
