"""Refs: P3-er U2 D4 R9 -- `app/embedding.py` 런타임 공급자·helper 단위 테스트.

네트워크·DB 없음(순수 로직 + 스텁 클라이언트). `OpenAIEmbeddingProvider` 의
실제 API 호출은 `scripts/er_smoke.py`(U8, 키가 있을 때만)가 스모크로 본다.
"""

from __future__ import annotations

import pytest

from app.embedding import (
    EMBEDDING_DIM,
    OpenAIEmbeddingProvider,
    _CallableEmbeddingProvider,
    as_provider,
    check_dimension,
)
from app.tools.types import InvalidValue

#: 테스트 전용 가짜 키 값 -- 실제 API 키 형식이 아니다(secret-guard 패턴
#: 회피 목적이 아니라, 애초에 진짜 키가 아님을 이름으로 드러낸다).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"


# ---------- dimension: 호출 없이 상수를 돌려준다 (결정6-b) ----------


def test_dimension_returns_constant_without_calling_embed():
    provider = OpenAIEmbeddingProvider()
    assert provider.dimension == EMBEDDING_DIM == 1536


def test_dimension_constant_regardless_of_model_name():
    # 결정6-a: 이 클래스는 text-embedding-3-small 고정(D4)이 전제이므로,
    # model 문자열을 바꿔도 dimension 은 상수 그대로다(다른 모델 비교는
    # scripts/embed_pilot.py 의 별도 클래스 몫).
    provider = OpenAIEmbeddingProvider(model="text-embedding-3-large")
    assert provider.dimension == EMBEDDING_DIM


# ---------- as_provider(): embed 속성 존재로 판별 ----------


def test_as_provider_none_stays_none():
    assert as_provider(None) is None


def test_as_provider_wraps_plain_callable():
    def fn(texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]

    wrapped = as_provider(fn)
    assert isinstance(wrapped, _CallableEmbeddingProvider)
    assert wrapped.embed(["a", "b"]) == [[0.0], [0.0]]


def test_as_provider_returns_object_with_embed_attribute_as_is():
    provider = OpenAIEmbeddingProvider(client=object())
    assert as_provider(provider) is provider


def test_as_provider_rejects_non_callable_non_embedder():
    with pytest.raises(TypeError):
        as_provider(object())


class _DangerousDimensionProvider:
    """`dimension` 속성 접근 자체가 예외를 던지는 공급자(과거 파일럿 계약처럼
    "embed() 를 먼저 호출해야 한다"는 방식). `as_provider()` 가 `embed` 하나만
    확인하면 이 속성에 접근하지 않아 오판하지 않는다."""

    @property
    def dimension(self) -> int:
        raise RuntimeError("dimension must not be accessed by as_provider()")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]


def test_as_provider_does_not_trigger_dangerous_dimension_property():
    provider = _DangerousDimensionProvider()
    result = as_provider(provider)
    assert result is provider
    # embed() 는 정상 호출 가능 -- dimension 에는 접근하지 않았다는 증거.
    assert result.embed(["x"]) == [[0.0]]


# ---------- check_dimension(): 정상/불일치 ----------


def test_check_dimension_passes_for_matching_length():
    check_dimension([0.1] * EMBEDDING_DIM)  # 예외 없이 통과


def test_check_dimension_rejects_mismatched_length():
    with pytest.raises(InvalidValue):
        check_dimension([0.1] * 1535)


def test_check_dimension_uses_custom_expected():
    check_dimension([0.1, 0.2, 0.3], expected=3)
    with pytest.raises(InvalidValue):
        check_dimension([0.1, 0.2], expected=3)


# ---------- OpenAIEmbeddingProvider: 키 없음 -> 사람이 읽는 오류, 키 미노출 ----------


def test_openai_provider_raises_human_readable_error_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIEmbeddingProvider()

    with pytest.raises(RuntimeError) as exc_info:
        provider.embed(["팀장"])

    message = str(exc_info.value)
    assert "OPENAI_API_KEY" in message
    # 키가 애초에 설정돼 있지 않으므로 흘릴 값 자체가 없다.
    assert _FAKE_KEY_MARKER not in message


def test_openai_provider_does_not_leak_key_value_when_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)
    provider = OpenAIEmbeddingProvider(client=object())  # 스텁 client 로 키 확인을 우회

    # client 가 이미 있으므로 키 검사 자체를 건너뛴다 -- 오류가 나더라도
    # (client 스텁이 embeddings.create 를 못 가지고 있어 AttributeError)
    # 메시지에 키 문자열이 없어야 한다.
    with pytest.raises(Exception) as exc_info:
        provider.embed(["팀장"])
    assert _FAKE_KEY_MARKER not in str(exc_info.value)


class _FakeDatum:
    def __init__(self, index: int, embedding: list[float]) -> None:
        self.index = index
        self.embedding = embedding


class _FakeEmbeddingsResource:
    def __init__(self, data: list[_FakeDatum]) -> None:
        self._data = data
        self.last_call: dict | None = None

    def create(self, *, model: str, input: list[str]):
        self.last_call = {"model": model, "input": list(input)}

        class _Resp:
            pass

        resp = _Resp()
        resp.data = self._data
        return resp


class _FakeClient:
    def __init__(self, data: list[_FakeDatum]) -> None:
        self.embeddings = _FakeEmbeddingsResource(data)


def test_openai_provider_embed_batches_one_call_and_orders_by_index():
    # 응답이 index 역순으로 와도 embed() 는 요청 순서(0,1)로 정렬해 돌려준다.
    fake_client = _FakeClient(
        [_FakeDatum(index=1, embedding=[0.2]), _FakeDatum(index=0, embedding=[0.1])]
    )
    provider = OpenAIEmbeddingProvider(client=fake_client)

    result = provider.embed(["팀장", "부장님"])

    assert result == [[0.1], [0.2]]
    assert fake_client.embeddings.last_call == {
        "model": "text-embedding-3-small",
        "input": ["팀장", "부장님"],
    }


def test_openai_provider_embed_empty_list_skips_call():
    fake_client = _FakeClient([])
    provider = OpenAIEmbeddingProvider(client=fake_client)

    assert provider.embed([]) == []
    assert fake_client.embeddings.last_call is None
