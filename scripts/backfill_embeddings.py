"""Refs: P3-er 01-plan 36행·94행(U8)·166~169행(결정6-d) D4 D5 R9 원칙8 --
`person_aliases.embedding IS NULL` 백필 스크립트.

P2 를 embedder 없이 돌린 구간(또는 마이그레이션 직후)에서 생긴 임베딩
누락 별칭을 배치로 채운다. 기본 동작은 **dry-run**(대상 건수·인물 수만
출력, 쓰기 0)이고 `--apply` 를 줘야 실제로 쓴다(원칙8 -- 데이터가 언제
바뀌었는지 증거를 남긴다, 우발적 쓰기를 기본으로 두지 않는다).

`.env` 는 읽지 않는다(security.md §1, `app/embedding.py` 와 같은 규약) --
`OPENAI_API_KEY` 는 `os.environ` 에서만 읽는다(실제로 읽는 것은
`app.embedding.OpenAIEmbeddingProvider`). **`--apply` 일 때만** 그 변수가
없으면 종료 코드 2 로 안내한다 -- dry-run 은 키 없이 돈다. 출력에 키
문자열·임베딩 벡터 원문을 찍지 않는다(건수·id 만).

사용:
    POSTGRES_PORT=5433 python scripts/backfill_embeddings.py --dry-run
    OPENAI_API_KEY=... POSTGRES_PORT=5433 python scripts/backfill_embeddings.py --apply

종료 코드:
    0 = 성공(dry-run 조회 완료 또는 apply 쓰기 완료)
    2 = `--apply` 인데 `OPENAI_API_KEY` 가 없음
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

# 스크립트로 직접 실행될 때 `app` 패키지를 찾을 수 있도록 저장소 루트를
# sys.path 에 넣는다(scripts/db_check.py·scripts/tools_check.py 와 동일).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.models import PersonAlias  # noqa: E402
from app.db.session import session_scope  # noqa: E402
from app.embedding import OpenAIEmbeddingProvider, check_dimension  # noqa: E402

#: 기본 배치 크기(위임 프롬프트 "배치(기본 64)").
DEFAULT_BATCH_SIZE = 64


def select_targets(session: Session, limit: int | None = None) -> list[tuple[int, str]]:
    """`embedding IS NULL` 인 별칭을 `(id, alias)` 목록으로, id 순으로 돌려준다.

    `limit` 이 주어지면 그 건수만 가져온다(`--limit` 인자, 큰 백필을 여러
    번에 나눠 돌릴 때 쓴다).
    """
    stmt = (
        select(PersonAlias.id, PersonAlias.alias)
        .where(PersonAlias.embedding.is_(None))
        .order_by(PersonAlias.id)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    return [(row[0], row[1]) for row in session.execute(stmt).all()]


def _distinct_person_count(session: Session, alias_ids: Sequence[int]) -> int:
    """`alias_ids` 가 속한 서로 다른 `person_id` 수. 빈 목록이면 0(빈
    `IN (...)` 을 만들지 않는다)."""
    if not alias_ids:
        return 0
    stmt = select(PersonAlias.person_id).where(PersonAlias.id.in_(alias_ids)).distinct()
    return len(session.execute(stmt).all())


def chunk(seq: Sequence, n: int) -> list[list]:
    """`seq` 를 `n` 개씩 잘라낸 리스트들의 리스트로 나눈다.

    `n <= 0` 이면 `ValueError`(호출자 실수를 조용히 삼키지 않는다).
    """
    if n <= 0:
        raise ValueError(f"batch size must be positive (got {n})")
    return [list(seq[i : i + n]) for i in range(0, len(seq), n)]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="person_aliases.embedding IS NULL 인 별칭 백필 (기본 dry-run)"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        dest="apply",
        action="store_false",
        help="대상 건수·인물 수만 출력한다. 쓰기 0(기본값)",
    )
    mode.add_argument(
        "--apply",
        dest="apply",
        action="store_true",
        help="실제로 임베딩을 계산해 쓴다. OPENAI_API_KEY 필요",
    )
    parser.set_defaults(apply=False)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"OpenAI 임베딩 배치 호출 크기 (기본 {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처리할 최대 별칭 건수(기본: 전체)",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    args = build_arg_parser().parse_args(argv)
    args.dry_run = not args.apply
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.apply and not os.environ.get("OPENAI_API_KEY"):
        print(
            "[error] OPENAI_API_KEY 환경변수가 설정되지 않았다. --apply 는 "
            "os.environ 에 그 변수를 직접 넣어야 동작한다(.env 는 읽지 않는다, "
            "security.md §1 -- .env.example 참조)."
        )
        return 2

    with session_scope() as session:
        targets = select_targets(session, limit=args.limit)
        alias_ids = [alias_id for alias_id, _alias in targets]
        person_count = _distinct_person_count(session, alias_ids)

        print(
            f"[info] 대상 별칭 {len(targets)}건, 인물 {person_count}명 "
            f"(batch_size={args.batch_size})"
        )

        if args.dry_run:
            print("[dry-run] 쓰기 0건 (--apply 로 실제 반영)")
            return 0

        if not targets:
            print("[ok] 대상 0건 -- 반영할 것이 없다")
            return 0

        provider = OpenAIEmbeddingProvider()
        written = 0
        for batch in chunk(targets, args.batch_size):
            alias_texts = [alias for _alias_id, alias in batch]
            vectors = provider.embed(alias_texts)
            for (alias_id, _alias), vector in zip(batch, vectors):
                check_dimension(vector)
                alias_row = session.get(PersonAlias, alias_id)
                alias_row.embedding = vector
            session.flush()
            written += len(batch)
            print(f"[ok] batch 완료: {written}/{len(targets)}건")

        print(f"[ok] 총 {written}건 반영 완료 (commit 은 session_scope 종료 시)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
