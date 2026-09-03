"""Refs: P0-embed-pilot D4 D5 S3.3 R5 — 임베딩 공급자 파일럿(결정용 코드).

한국어 짧은 호칭 30개를 OpenAI 임베딩 모델 2개로 임베딩해 코사인 유사도 행렬을 만들고,
D4 카드의 검증 기준 "팀장↔부장님 유사도 > 팀장↔이모" 를 판정한다.
결과는 reports/embed_pilot/<model>.json 에 저장한다(재현용). 선택 근거·확정 차원 N 은 reports/embed_pilot.md 에 사람이 쓴다.

- 임베딩 호출은 EmbeddingProvider 인터페이스 뒤에 둔다(D4 "코드에서 지켜야 할 것"). P2/P3 에서 백엔드 모듈로 옮긴다.
- API 키는 환경변수 OPENAI_API_KEY 로만 읽고 절대 출력하지 않는다(security.md §1).

사용:
    python scripts/embed_pilot.py                      # 기본 모델 2개 실행
    python scripts/embed_pilot.py --models text-embedding-3-small
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, Sequence

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "reports" / "embed_pilot"
DEFAULT_MODELS = ("text-embedding-3-small", "text-embedding-3-large")

# 한국어 짧은 호칭 30개 — 직장(위계·이름+직함) / 가족 / 연인·친구·지인 / 대명사.
# 별칭 단위 임베딩(D5)에서 실제로 저장될 형태의 짧은 표현만 넣는다.
TITLES: tuple[str, ...] = (
    # 직장 (12)
    "팀장", "팀장님", "김팀장", "김 팀장님",
    "부장님", "김부장", "과장님", "대리님",
    "사장님", "이사님", "선배", "후배",
    # 가족 (8)
    "이모", "엄마", "아빠", "삼촌", "고모", "큰아버지", "할머니", "누나",
    # 연인·친구·지인 (6)
    "여자친구", "남친", "친구", "동기", "룸메", "교수님",
    # 대명사·지시 표현 (4)
    "그 사람", "그분", "걔", "그 애",
)

# D4 검증 기준(필수) + 참고용 보조 쌍. (a, b) 유사도 > (a, c) 유사도 이어야 통과.
# 첫 항목이 D4 카드가 명시한 기준이며, 나머지는 후보 검색(S3.3 1단계) 관점의 보조 관찰이다.
CHECKS: tuple[tuple[str, str, str, bool], ...] = (
    ("팀장", "부장님", "이모", True),      # D4 필수 기준
    ("팀장", "김팀장", "엄마", False),      # 이름+직함 ↔ 직함
    ("부장님", "김부장", "삼촌", False),    # 존칭 유무
    ("여자친구", "남친", "과장님", False),  # 연인 계열
    ("그 사람", "그분", "할머니", False),   # 대명사끼리
)


class EmbeddingProvider(Protocol):
    """D4: 임베딩 호출은 반드시 이 인터페이스 뒤에 둔다. 공급자 교체 = 클래스 하나 추가."""

    name: str

    @property
    def dimension(self) -> int: ...

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass
class OpenAIEmbeddingProvider:
    """OpenAI 임베딩. 키는 SDK 가 환경변수 OPENAI_API_KEY 에서 읽는다(코드에 키 없음)."""

    model: str = "text-embedding-3-small"
    usage: dict[str, int] = field(default_factory=dict)
    _dimension: int | None = None
    _client: object = None

    @property
    def name(self) -> str:
        return self.model

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError("embed() 를 먼저 호출해야 차원을 알 수 있다")
        return self._dimension

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI  # 지연 import: 테스트는 네트워크·SDK 없이 돈다

            self._client = OpenAI()
        return self._client

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        resp = self._get_client().embeddings.create(model=self.model, input=list(texts))
        vectors = [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
        self._dimension = len(vectors[0])
        if resp.usage is not None:
            self.usage = {
                "prompt_tokens": self.usage.get("prompt_tokens", 0) + resp.usage.prompt_tokens,
                "total_tokens": self.usage.get("total_tokens", 0) + resp.usage.total_tokens,
            }
        return vectors


# ---------- 순수 계산 (네트워크 없음, 테스트 대상) ----------


def cosine_matrix(vectors: Sequence[Sequence[float]]) -> list[list[float]]:
    """코사인 유사도 행렬. 의존성 없이 순수 파이썬(30×N 이라 충분히 빠르다)."""
    norms = [math.sqrt(sum(x * x for x in v)) or 1.0 for v in vectors]
    unit = [[x / n for x in v] for v, n in zip(vectors, norms)]
    return [[sum(a * b for a, b in zip(u, w)) for w in unit] for u in unit]


def similarity(labels: Sequence[str], matrix: Sequence[Sequence[float]], a: str, b: str) -> float:
    i, j = labels.index(a), labels.index(b)
    return matrix[i][j]


def evaluate_checks(labels: Sequence[str], matrix: Sequence[Sequence[float]]) -> list[dict]:
    out = []
    for a, near, far, required in CHECKS:
        s_near = similarity(labels, matrix, a, near)
        s_far = similarity(labels, matrix, a, far)
        out.append(
            {
                "anchor": a,
                "near": near,
                "far": far,
                "sim_near": round(s_near, 4),
                "sim_far": round(s_far, 4),
                "margin": round(s_near - s_far, 4),
                "passed": s_near > s_far,
                "required": required,
            }
        )
    return out


def ranked_pairs(labels: Sequence[str], matrix: Sequence[Sequence[float]], k: int = 10) -> dict:
    pairs = [
        (labels[i], labels[j], matrix[i][j])
        for i in range(len(labels))
        for j in range(i + 1, len(labels))
    ]
    pairs.sort(key=lambda p: p[2], reverse=True)
    fmt = lambda p: {"a": p[0], "b": p[1], "sim": round(p[2], 4)}  # noqa: E731
    return {"top": [fmt(p) for p in pairs[:k]], "bottom": [fmt(p) for p in pairs[-k:]]}


def run_pilot(provider: EmbeddingProvider, labels: Sequence[str] = TITLES) -> dict:
    """공급자 하나로 파일럿을 수행해 JSON 직렬화 가능한 결과를 돌려준다."""
    vectors = provider.embed(labels)
    if len(vectors) != len(labels):
        raise RuntimeError(f"임베딩 수 불일치: {len(vectors)} != {len(labels)}")
    matrix = cosine_matrix(vectors)
    checks = evaluate_checks(labels, matrix)
    return {
        "model": provider.name,
        "dimension": provider.dimension,
        "n_labels": len(labels),
        "labels": list(labels),
        "checks": checks,
        "required_passed": all(c["passed"] for c in checks if c["required"]),
        "optional_passed": sum(1 for c in checks if not c["required"] and c["passed"]),
        "optional_total": sum(1 for c in checks if not c["required"]),
        "ranked_pairs": ranked_pairs(labels, matrix),
        "usage": getattr(provider, "usage", {}),
        "matrix": [[round(x, 4) for x in row] for row in matrix],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def summarize(result: dict) -> str:
    lines = [
        f"[{result['model']}] dimension={result['dimension']} labels={result['n_labels']} "
        f"usage={result['usage'] or 'n/a'}",
    ]
    for c in result["checks"]:
        tag = "필수" if c["required"] else "보조"
        mark = "PASS" if c["passed"] else "FAIL"
        lines.append(
            f"  {mark} ({tag}) {c['anchor']}↔{c['near']} {c['sim_near']:.4f} "
            f"> {c['anchor']}↔{c['far']} {c['sim_far']:.4f}  margin={c['margin']:+.4f}"
        )
    lines.append(
        f"  필수 기준: {'통과' if result['required_passed'] else '미달'} · "
        f"보조 {result['optional_passed']}/{result['optional_total']}"
    )
    return "\n".join(lines)


# ---------- CLI ----------


def _load_dotenv_quietly() -> None:
    """.env 를 환경변수로만 올린다. 값을 읽어 출력하거나 파일을 열어 보여주지 않는다."""
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass


def _force_utf8_console() -> None:
    """Windows 콘솔(cp949)에서 한국어 출력이 깨지지 않게 한다. 실패해도 무시."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    _force_utf8_console()
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args(argv)

    _load_dotenv_quietly()
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "OPENAI_API_KEY 가 설정되지 않았다. 사용자가 .env 에 직접 넣어야 한다 (.env.example 참조).",
            file=sys.stderr,
        )
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rc = 0
    for model in args.models:
        provider = OpenAIEmbeddingProvider(model=model)
        result = run_pilot(provider)
        out = args.out_dir / f"{model}.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(summarize(result))
        print(f"  saved: {out.relative_to(ROOT)}")
        if not result["required_passed"]:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
