"""Refs: P0-embed-pilot D4 R5 — embed_pilot 의 순수 계산·판정 로직 테스트 (네트워크·OpenAI SDK 없음)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import embed_pilot as ep  # noqa: E402


class FakeProvider:
    """호칭마다 손으로 만든 3차원 벡터. 직장 호칭은 x축, 가족은 y축, 대명사·연인은 z축 근처."""

    name = "fake-3d"

    def __init__(self, table: dict[str, list[float]] | None = None, dimension: int = 3):
        self.table = table or {}
        self._dimension = dimension
        self.calls = 0
        self.usage = {"prompt_tokens": 0, "total_tokens": 0}

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts):
        self.calls += 1
        out = []
        for t in texts:
            if t in self.table:
                out.append(self.table[t])
            else:
                # 기본: 직장 계열 x, 가족 계열 y, 나머지 z 에 약간의 결정적 잡음
                h = (sum(map(ord, t)) % 7) / 100.0
                if any(k in t for k in ("팀장", "부장", "과장", "대리", "사장", "이사", "선배", "후배", "교수")):
                    out.append([1.0, h, 0.0])
                elif any(k in t for k in ("이모", "엄마", "아빠", "삼촌", "고모", "큰아버지", "할머니", "누나")):
                    out.append([h, 1.0, 0.0])
                else:
                    out.append([0.0, h, 1.0])
        return out


def test_titles_are_30_unique_short_strings():
    assert len(ep.TITLES) == 30
    assert len(set(ep.TITLES)) == 30
    assert all(0 < len(t) <= 6 for t in ep.TITLES)


def test_required_check_is_d4_criterion():
    required = [c for c in ep.CHECKS if c[3]]
    assert required == [("팀장", "부장님", "이모", True)]
    for a, near, far, _ in ep.CHECKS:
        assert {a, near, far} <= set(ep.TITLES)


def test_cosine_matrix_properties():
    m = ep.cosine_matrix([[1, 0], [0, 1], [1, 1], [2, 0]])
    n = len(m)
    for i in range(n):
        assert math.isclose(m[i][i], 1.0, abs_tol=1e-9)
        for j in range(n):
            assert math.isclose(m[i][j], m[j][i], abs_tol=1e-12)
    assert math.isclose(m[0][1], 0.0, abs_tol=1e-9)
    assert math.isclose(m[0][3], 1.0, abs_tol=1e-9)  # 크기 무관
    assert math.isclose(m[0][2], 1 / math.sqrt(2), abs_tol=1e-9)


def test_cosine_matrix_zero_vector_does_not_divide_by_zero():
    m = ep.cosine_matrix([[0.0, 0.0], [1.0, 0.0]])
    assert m[0][0] == 0.0 and m[0][1] == 0.0


def test_run_pilot_passes_with_good_provider():
    result = ep.run_pilot(FakeProvider())
    assert result["model"] == "fake-3d"
    assert result["dimension"] == 3
    assert result["n_labels"] == 30
    assert len(result["matrix"]) == 30 and len(result["matrix"][0]) == 30
    assert result["required_passed"] is True
    d4 = result["checks"][0]
    assert (d4["anchor"], d4["near"], d4["far"]) == ("팀장", "부장님", "이모")
    assert d4["sim_near"] > d4["sim_far"]
    # JSON 직렬화 가능(재현용 저장)
    json.dumps(result, ensure_ascii=False)


def test_run_pilot_fails_when_family_is_closer_than_colleague():
    bad = FakeProvider(table={"팀장": [1.0, 0.0, 0.0], "부장님": [0.0, 1.0, 0.0], "이모": [1.0, 0.1, 0.0]})
    result = ep.run_pilot(bad)
    assert result["required_passed"] is False
    assert result["checks"][0]["passed"] is False


def test_run_pilot_rejects_wrong_vector_count():
    class Short(FakeProvider):
        def embed(self, texts):
            return super().embed(texts)[:-1]

    with pytest.raises(RuntimeError):
        ep.run_pilot(Short())


def test_ranked_pairs_are_sorted_and_exclude_self():
    result = ep.run_pilot(FakeProvider())
    top = result["ranked_pairs"]["top"]
    bottom = result["ranked_pairs"]["bottom"]
    assert len(top) == 10 and len(bottom) == 10
    assert all(p["a"] != p["b"] for p in top + bottom)
    assert top[0]["sim"] >= top[-1]["sim"] >= bottom[0]["sim"] >= bottom[-1]["sim"]


def test_summarize_mentions_required_result():
    text = ep.summarize(ep.run_pilot(FakeProvider()))
    assert "팀장↔부장님" in text
    assert "필수 기준: 통과" in text


def test_main_exits_2_without_api_key(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(ep, "_load_dotenv_quietly", lambda: None)
    rc = ep.main(["--out-dir", str(tmp_path)])
    assert rc == 2
    assert not any(tmp_path.iterdir())
