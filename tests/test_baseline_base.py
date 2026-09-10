"""Refs: P3-baselines S3.7 D10 원칙2 원칙8 -- 공통 타입·방식 표의 계약 테스트.

**네트워크·DB 없음**(순수). `evaluation/resolvers/base.py` 의 불변 규약과
`registry.py` 의 이름 계약을 값 수준에서 단언한다. 네 방식을 실제로 같은
인자로 호출해 보는 계약 테스트는 U7 `tests/test_baseline_parity.py` 다 --
여기서는 "규약을 어긴 값은 만들 수조차 없다"까지만 본다.

포함하는 것:
- `DECISIONS` 가 `app.er.confidence.band_for()` 의 밴드 어휘와 같은 낱말(D10)
- `decision` 어휘 밖 / `person_id` 규약 / `score` 범위 위반 -> `ValueError`
- frozen dataclass, `to_dict()` 의 JSON 직렬화 가능성(P4 재현성, 원칙8)
- `get_resolver` 오류 메시지에 등록 목록 포함, `register` 등록 순서 유지
- `Resolver` Protocol 만족 여부와 `resolve_mention` 시그니처 고정
- **R-2 역방향 import 금지**: `app/` 이 `evaluation` 을 import 하지 않는다
"""

from __future__ import annotations

import dataclasses
import inspect
import json
import re
from pathlib import Path
from typing import Any

import pytest

from app.er.confidence import band_for
from app.er.types import ERConfig
from evaluation.resolvers import (
    DECISIONS,
    MentionDecision,
    RESOLVERS,
    Resolver,
    ResolverCandidate,
    get_resolver,
    register,
    registry,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def make_decision(**overrides: Any) -> MentionDecision:
    """규약을 만족하는 기본값 + 덮어쓰기. 각 테스트는 어긴 필드 하나만
    바꿔 넣어 "그 필드 때문에 거부됐다"를 분명히 한다."""
    kwargs: dict[str, Any] = {
        "method": "dummy",
        "mention": "김팀장",
        "decision": "new_person",
        "person_id": None,
        "score": 0.0,
        "candidates": [],
    }
    kwargs.update(overrides)
    return MentionDecision(**kwargs)


# --- DECISIONS = band_for 어휘 (D10) -------------------------------------


def test_decisions_matches_band_for_vocabulary() -> None:
    """`band_for()` 를 `[0, 1]` 전 구간에 돌려 나온 밴드 집합이 `DECISIONS`
    와 정확히 같다 -- 어휘가 갈라지면 이 테스트가 깨진다(이중 출처 방지)."""
    config = ERConfig()
    bands = {band_for(i / 100, config) for i in range(101)}
    assert bands == set(DECISIONS)
    assert len(DECISIONS) == len(set(DECISIONS)) == 3


def test_decisions_order_is_high_confidence_first() -> None:
    """튜플 순서도 `band_for` 의 분기 순서(>= T_merge -> >= T_new -> 그 외)
    와 같다. 경계값(정확히 임계치)은 `>=` 쪽으로 간다(F-7fe239)."""
    config = ERConfig(t_merge=0.8, t_new=0.3)
    assert DECISIONS == ("merge", "identity", "new_person")
    assert band_for(1.0, config) == DECISIONS[0]
    assert band_for(config.t_merge, config) == DECISIONS[0]
    assert band_for(config.t_new, config) == DECISIONS[1]
    assert band_for(0.0, config) == DECISIONS[2]


# --- MentionDecision 불변 규약 -------------------------------------------


@pytest.mark.parametrize(
    ("decision", "person_id"),
    [("merge", 7), ("identity", None), ("new_person", None)],
)
def test_valid_decisions_are_accepted(decision: str, person_id: int | None) -> None:
    value = make_decision(decision=decision, person_id=person_id, score=0.5)
    assert value.decision == decision
    assert value.person_id == person_id


@pytest.mark.parametrize("decision", ["ask_user", "MERGE", "", "identity ", "unknown"])
def test_decision_outside_vocabulary_is_rejected(decision: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        make_decision(decision=decision)
    message = str(excinfo.value)
    assert "decision" in message
    for word in DECISIONS:
        assert word in message


@pytest.mark.parametrize("decision", ["identity", "new_person"])
def test_person_id_without_merge_is_rejected(decision: str) -> None:
    """규약 3 -- `identity` 는 "사람에게 묻는다"이므로 단일 인물을 고르지
    않는다(원칙1·2). 후보는 `candidates` 로 답한다."""
    with pytest.raises(ValueError) as excinfo:
        make_decision(decision=decision, person_id=3)
    assert "person_id" in str(excinfo.value)


def test_merge_without_person_id_is_rejected() -> None:
    with pytest.raises(ValueError) as excinfo:
        make_decision(decision="merge", person_id=None, score=0.9)
    assert "person_id" in str(excinfo.value)


@pytest.mark.parametrize("score", [-0.001, -1.0, 1.001, 2.0, float("nan")])
def test_score_outside_unit_interval_is_rejected(score: float) -> None:
    with pytest.raises(ValueError) as excinfo:
        make_decision(score=score)
    assert "score" in str(excinfo.value)


@pytest.mark.parametrize("score", [0.0, 0.5, 1.0])
def test_score_boundaries_are_accepted(score: float) -> None:
    assert make_decision(score=score).score == score


def test_mention_decision_is_frozen() -> None:
    value = make_decision()
    with pytest.raises(dataclasses.FrozenInstanceError):
        value.decision = "merge"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        value.person_id = 1  # type: ignore[misc]


def test_resolver_candidate_is_frozen() -> None:
    candidate = ResolverCandidate(person_id=1, display_name="김민수")
    with pytest.raises(dataclasses.FrozenInstanceError):
        candidate.score = 1.0  # type: ignore[misc]
    assert candidate.score == 0.0
    assert candidate.signals == {}


def test_to_dict_is_json_serializable() -> None:
    """P4 가 `metrics.json`·응답 캐시로 보존한다(재현성, 원칙8)."""
    value = make_decision(
        method="proposed",
        decision="merge",
        person_id=11,
        score=0.87,
        candidates=[
            ResolverCandidate(
                person_id=11,
                display_name="김민수",
                score=0.87,
                signals={"s_emb": 0.71, "s_rule": 1.0},
            ),
            ResolverCandidate(person_id=12, display_name="김지원"),
        ],
        trace_id=42,
        tokens_in=310,
        tokens_out=48,
        detail={"forced_reason": None, "relaxed_retry": False, "provider": "fake"},
    )
    payload = value.to_dict()
    restored = json.loads(json.dumps(payload, ensure_ascii=False))
    assert restored == payload
    assert restored["method"] == "proposed"
    assert restored["decision"] == "merge"
    assert restored["person_id"] == 11
    assert restored["trace_id"] == 42
    assert restored["tokens_in"] == 310 and restored["tokens_out"] == 48
    assert restored["candidates"][0]["signals"] == {"s_emb": 0.71, "s_rule": 1.0}
    assert restored["detail"]["provider"] == "fake"


def test_to_dict_copies_mutable_fields() -> None:
    """반환 dict 를 고쳐도 원본이 바뀌지 않는다(frozen 의 의도가 새지
    않게)."""
    detail = {"forced_reason": "no_candidates"}
    value = make_decision(detail=detail)
    payload = value.to_dict()
    payload["detail"]["forced_reason"] = "tampered"
    payload["candidates"].append({"person_id": 999})
    assert value.detail == {"forced_reason": "no_candidates"}
    assert value.candidates == []


# --- 방식 표(registry) ----------------------------------------------------


@pytest.fixture()
def clean_registry() -> Any:
    """등록 표를 비워 테스트를 결정적으로 만들고, 끝나면 원래대로 되돌린다
    (U2~U5 가 방식을 올려도 이 테스트의 순서 단언이 흔들리지 않는다)."""
    snapshot = RESOLVERS.copy()
    RESOLVERS.clear()
    try:
        yield RESOLVERS
    finally:
        RESOLVERS.clear()
        RESOLVERS.update(snapshot)


class DummyResolver:
    """Protocol 을 상속하지 않는 구조적 구현(네 방식도 같은 형태다)."""

    supported_decisions: tuple[str, ...] = DECISIONS

    def __init__(self, name: str = "dummy", score: float = 0.0) -> None:
        self.name = name
        self.score = score

    def resolve_mention(
        self,
        ctx: Any,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: Any | None = None,
    ) -> MentionDecision:
        return MentionDecision(
            method=self.name,
            mention=mention,
            decision="new_person",
            person_id=None,
            score=self.score,
            candidates=[],
            detail={"forced_reason": "dummy"},
        )


class NotAResolver:
    name = "not_a_resolver"
    supported_decisions: tuple[str, ...] = ()


def test_all_methods_is_empty_when_registry_is_empty(clean_registry: Any) -> None:
    assert registry.ALL_METHODS == ()


def test_register_preserves_insertion_order(clean_registry: Any) -> None:
    """`ALL_METHODS` 순서 = 등록 순서 = P4 표의 열 순서."""
    for name in ("proposed", "exact_raw", "exact_norm"):
        register(name, lambda n=name: DummyResolver(name=n))
    assert registry.ALL_METHODS == ("proposed", "exact_raw", "exact_norm")
    register("llm_single", lambda: DummyResolver(name="llm_single"))
    assert registry.ALL_METHODS == (
        "proposed",
        "exact_raw",
        "exact_norm",
        "llm_single",
    )


def test_register_as_decorator_returns_original(clean_registry: Any) -> None:
    @register("exact_raw")
    class Decorated(DummyResolver):
        pass

    assert Decorated is RESOLVERS["exact_raw"]
    assert issubclass(Decorated, DummyResolver)


def test_register_rejects_duplicate_name(clean_registry: Any) -> None:
    register("exact_raw", DummyResolver)
    with pytest.raises(ValueError) as excinfo:
        register("exact_raw", DummyResolver)
    assert "exact_raw" in str(excinfo.value)


def test_register_rejects_empty_name(clean_registry: Any) -> None:
    with pytest.raises(ValueError):
        register("  ", DummyResolver)


def test_get_resolver_unknown_name_lists_registered(clean_registry: Any) -> None:
    """오타로 한 방식이 조용히 빠진 비교표가 나오지 않게 한다(원칙8)."""
    register("exact_raw", DummyResolver)
    register("embedding_only", DummyResolver)
    with pytest.raises(KeyError) as excinfo:
        get_resolver("exact_match")
    message = str(excinfo.value)
    assert "exact_match" in message
    assert "exact_raw" in message
    assert "embedding_only" in message


def test_get_resolver_message_when_registry_empty(clean_registry: Any) -> None:
    with pytest.raises(KeyError) as excinfo:
        get_resolver("proposed")
    assert "proposed" in str(excinfo.value)


def test_get_resolver_passes_kwargs(clean_registry: Any) -> None:
    register("exact_raw", DummyResolver)
    resolver = get_resolver("exact_raw", name="exact_raw", score=1.0)
    assert isinstance(resolver, DummyResolver)
    assert resolver.name == "exact_raw"
    decision = resolver.resolve_mention(None, "김팀장", "오늘 김팀장이랑 밥 먹었어")
    assert isinstance(decision, MentionDecision)
    assert decision.method == "exact_raw"
    assert decision.decision in DECISIONS


def test_get_resolver_rejects_factory_without_resolve_mention(
    clean_registry: Any,
) -> None:
    register("broken", NotAResolver)
    with pytest.raises(TypeError) as excinfo:
        get_resolver("broken")
    assert "resolve_mention" in str(excinfo.value)


# --- Resolver Protocol ----------------------------------------------------


def test_dummy_resolver_satisfies_protocol() -> None:
    """`Resolver` 는 `@runtime_checkable` 이라 `isinstance()` 로 속성·메서드
    존재를 본다(시그니처는 보지 않는다 -- 그것은 U7 parity 테스트 몫)."""
    assert isinstance(DummyResolver(), Resolver)
    assert not isinstance(NotAResolver(), Resolver)


def test_resolve_mention_signature_is_fixed() -> None:
    """네 방식이 **같은 인자**로 불린다는 계약(eval-harness §3 "동일 데이터")
    을 시그니처 수준에서 고정한다."""
    signature = inspect.signature(Resolver.resolve_mention)
    assert list(signature.parameters) == [
        "self",
        "ctx",
        "mention",
        "utterance",
        "hints",
        "config",
    ]
    assert signature.parameters["hints"].default is None
    config_param = signature.parameters["config"]
    assert config_param.default is None
    assert config_param.kind is inspect.Parameter.KEYWORD_ONLY


def test_package_reexports_public_names() -> None:
    import evaluation.resolvers as package

    for name in (
        "DECISIONS",
        "MentionDecision",
        "Resolver",
        "ResolverCandidate",
        "RESOLVERS",
        "get_resolver",
        "register",
        "ALL_METHODS",
    ):
        assert name in package.__all__
        assert getattr(package, name) is not None
    assert package.ALL_METHODS == tuple(RESOLVERS)


# --- R-2 역방향 import 금지 (02-plan-verify §3) ---------------------------


def _app_python_files() -> list[Path]:
    files = [
        path
        for path in sorted((REPO_ROOT / "app").rglob("*.py"))
        if "__pycache__" not in path.parts
    ]
    assert files, "app/ 아래 .py 를 하나도 찾지 못했다 -- 경로 계산이 틀렸다"
    return files


def test_app_does_not_import_evaluation_package() -> None:
    """제품 코드가 평가 장치를 import 하면 원칙4 가 금지한 대비군(LLM 단일
    프롬프트)이 런타임 경로에 섞일 수 있다. `git diff -- app/` 0줄은
    "수정 없음"만 보이고 "의존 없음"은 보이지 않는다(R-2)."""
    pattern = re.compile(r"^\s*(?:from|import)\s+evaluation\b", re.MULTILINE)
    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in _app_python_files()
        if pattern.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == []


def test_app_does_not_mention_evaluation_package_at_all() -> None:
    """R-2 의 판정 명령(`grep -rn "evaluation" app/ --include=*.py` -> 0줄)
    을 그대로 옮긴 것. 장래에 주석 등으로 이 낱말이 정당하게 필요해지면
    위 import 테스트만 남기고 이 테스트의 범위를 좁힌다(그때는 그 결정을
    03-log 에 남긴다)."""
    hits = [
        f"{path.relative_to(REPO_ROOT)}:{lineno}"
        for path in _app_python_files()
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if "evaluation" in line
    ]
    assert hits == []
