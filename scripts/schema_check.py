"""Refs: P1-schema R8 R9 D4 D5 S3.1 -- 스키마 v2 실물 검사 (upgrade/downgrade 왕복 확인용).

사용:
    POSTGRES_PORT=5433 python scripts/schema_check.py
    POSTGRES_PORT=5433 python scripts/schema_check.py --expect-empty   # downgrade base 후 검증

동작:
  1. `app.config.resolve_connection()` 으로 접속 정보를 해석한다(`DATABASE_URL`
     우선, 없으면 `POSTGRES_*` 조립 -- `scripts/db_check.py` 와 완전히 같은
     우선순위·같은 변수 이름). 키워드 인자로 접속한다(URL 문자열을 조립해
     로그에 남기지 않는다). 비밀번호·접속 문자열은 어떤 경우에도 출력하지
     않는다(`ConnInfo.safe_summary()` 만 출력).
  2. 검사 항목마다 `[PASS]`/`[FAIL]`/`[info]`/`[skip]` 로 시작하는 한 줄을
     찍는다. 테이블 존재가 확인된 경우에만(스키마가 완전한 경우에만) CHECK·
     FK·PK·벡터·인덱스 등 테이블에 의존하는 검사를 수행하고, 그렇지 않으면
     `[skip]` 로 건너뛴다(예: `--expect-empty` 로 9개 테이블이 없는 상태).
  3. 기대값(9개 테이블 이름, CHECK 값 집합, 인덱스 이름)은 전부
     `app.db.models`/`app.db.base` 에서 가져온다 -- 이 스크립트에서 다시
     정의하지 않는다(중복 정의 방지, U2 모델이 유일한 진실의 원천).
  4. `person_embeddings` 테이블과 인물-인물 관계처럼 보이는 이름
     (`person_relations`, `relationships`) 의 부재는 스키마 상태와 무관하게
     항상 검사한다(R9, 원칙7).

종료 코드:
    0 = 모든 검사 PASS (FAIL 없음)
    1 = 접속은 성공했지만 검사 중 하나 이상 FAIL
    2 = 접속 실패(psycopg 미설치 포함). 비밀번호는 이 경우에도 출력하지 않는다.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# 스크립트로 직접 실행될 때(`python scripts/schema_check.py`) `app` 패키지를
# 찾을 수 있도록 저장소 루트를 sys.path 에 넣는다(scripts/db_check.py 와 동일).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import resolve_connection  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db import models as m  # noqa: E402  -- 값 집합·CHECK 정의의 단일 출처, import 로 테이블 등록

# S3.1 9개 테이블 이름 -- `Base.metadata` 에서 그대로 가져온다(중복 정의 방지).
EXPECTED_TABLES: tuple[str, ...] = tuple(sorted(Base.metadata.tables.keys()))

# R9/원칙7 -- 이 이름들은 만들지 않는 것이 산출물이므로 여기서만 하드코딩한다
# (모델에 없는 것의 부재를 확인하는 목록이라 모델에서 가져올 수 없다).
FORBIDDEN_TABLES: tuple[str, ...] = ("person_embeddings", "person_relations", "relationships")


@dataclass
class CheckResult:
    name: str
    status: str  # "PASS" | "FAIL" | "INFO" | "SKIP"
    detail: str = ""


_TAG = {"PASS": "[PASS]", "FAIL": "[FAIL]", "INFO": "[info]", "SKIP": "[skip]"}


def _emit(results: list[CheckResult], name: str, status: str, detail: str = "") -> None:
    results.append(CheckResult(name, status, detail))
    line = f"{_TAG[status]} {name}"
    if detail:
        line += f" -> {detail}"
    print(line)


def _missing_values(values: tuple[str, ...], haystack: str) -> list[str]:
    """`values` 중 `haystack` 문자열에 없는 것만 골라낸다. DB 없이도 테스트 가능."""
    return [v for v in values if v not in haystack]


def model_index_expectations() -> tuple[set[str], str | None]:
    """모델(`Base.metadata`)에 정의된 인덱스 이름 집합과, 그중 부분 인덱스 이름 하나를 반환한다.

    DB 없이도 계산 가능 -- 테스트가 이 함수만 호출해 인덱스 총수·부분 인덱스
    존재를 검증한다.
    """
    names: set[str] = set()
    partial_name: str | None = None
    for table in Base.metadata.tables.values():
        for ix in table.indexes:
            names.add(ix.name)
            where = ix.dialect_options.get("postgresql", {}).get("where")
            if where is not None:
                partial_name = ix.name
    return names, partial_name


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="스키마 v2 (9테이블·CHECK·FK·벡터·인덱스) 실물 검사"
    )
    parser.add_argument(
        "--expect-empty",
        action="store_true",
        help="9개 테이블이 모두 없는 상태를 기대한다 (alembic downgrade base 이후 확인용)",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def compute_exit_code(results: list[CheckResult]) -> int:
    """FAIL 이 하나라도 있으면 1, 아니면 0. 접속 실패(rc=2)는 이 함수 이전에 처리된다."""
    return 1 if any(r.status == "FAIL" for r in results) else 0


# ---------------------------------------------------------------------------
# 테이블에 의존하는 개별 검사 (스키마가 완전할 때만 호출된다)
# ---------------------------------------------------------------------------


def _check_events_type(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = %s::regclass AND contype = 'c'",
        ("events",),
    )
    rows = cur.fetchall()
    defs = " | ".join(d for _, d in rows)
    missing = _missing_values(m.EVENT_TYPES, defs)
    ok = len(rows) >= 1 and not missing
    _emit(
        results,
        "events.type CHECK has all EVENT_TYPES values",
        "PASS" if ok else "FAIL",
        defs if ok else f"missing={missing} defs={defs!r}",
    )


def _check_persons_checks(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = %s::regclass AND contype = 'c'",
        ("persons",),
    )
    rows = cur.fetchall()
    all_defs = " | ".join(d for _, d in rows)

    missing_tags = _missing_values(m.RELATION_TAGS, all_defs)
    _emit(
        results,
        "persons.relation_tag CHECK has all RELATION_TAGS values",
        "PASS" if not missing_tags else "FAIL",
        all_defs if not missing_tags else f"missing={missing_tags} defs={all_defs!r}",
    )

    missing_hier = _missing_values(m.HIERARCHIES, all_defs)
    _emit(
        results,
        "persons.hierarchy CHECK has all HIERARCHIES values",
        "PASS" if not missing_hier else "FAIL",
        all_defs if not missing_hier else f"missing={missing_hier} defs={all_defs!r}",
    )


def _check_pending_questions_kind(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = %s::regclass AND contype = 'c'",
        ("pending_questions",),
    )
    rows = cur.fetchall()
    defs = " | ".join(d for _, d in rows)
    missing = _missing_values(m.QUESTION_KINDS, defs)
    ok = len(rows) >= 1 and not missing
    _emit(
        results,
        "pending_questions.kind CHECK has all QUESTION_KINDS values",
        "PASS" if ok else "FAIL",
        defs if ok else f"missing={missing} defs={defs!r}",
    )


def _check_embedding_vector(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
        "WHERE attrelid = %s::regclass AND attname = %s",
        ("person_aliases", "embedding"),
    )
    row = cur.fetchone()
    value = row[0] if row else None
    ok = value == "vector(1536)"
    _emit(
        results,
        "person_aliases.embedding format_type is vector(1536)",
        "PASS" if ok else "FAIL",
        str(value),
    )


def _check_fact_sources_pk(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = %s::regclass AND contype = 'p'",
        ("fact_sources",),
    )
    row = cur.fetchone()
    defn = row[0] if row else None
    ok = defn is not None and "fact_id" in defn and "event_id" in defn
    _emit(
        results,
        "fact_sources PK is (fact_id, event_id) with no surrogate id",
        "PASS" if ok else "FAIL",
        str(defn),
    )


def _check_foreign_keys(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT conrelid::regclass::text, conname, confdeltype FROM pg_constraint "
        "WHERE contype = 'f' AND conrelid::regclass::text = ANY(%s) ORDER BY 1, 2",
        (list(EXPECTED_TABLES),),
    )
    rows = cur.fetchall()
    bad = [r for r in rows if r[2] != "c"]
    ok = len(rows) == 6 and not bad
    detail = "; ".join(f"{t}.{n}={d}" for t, n, d in rows)
    _emit(
        results,
        "6 foreign keys all confdeltype='c' (ON DELETE CASCADE)",
        "PASS" if ok else "FAIL",
        f"count={len(rows)} {detail}",
    )


def _check_indexes(cur, results: list[CheckResult]) -> None:
    expected_names, partial_name = model_index_expectations()

    cur.execute(
        "SELECT indexname, indexdef FROM pg_indexes "
        "WHERE schemaname = 'public' AND tablename = ANY(%s)",
        (list(EXPECTED_TABLES),),
    )
    rows = cur.fetchall()
    actual_names = {r[0] for r in rows}
    missing = sorted(expected_names - actual_names)
    _emit(
        results,
        "all model index names exist in DB",
        "PASS" if not missing else "FAIL",
        f"expected={len(expected_names)} missing={missing}",
    )

    ok_count = len(rows) >= 10
    _emit(
        results,
        "total index count >= 10",
        "PASS" if ok_count else "FAIL",
        f"count={len(rows)}",
    )

    if partial_name:
        defn = next((d for n, d in rows if n == partial_name), None)
        ok_partial = defn is not None and "answered_at IS NULL" in defn
        _emit(
            results,
            f"partial index {partial_name} has WHERE answered_at IS NULL",
            "PASS" if ok_partial else "FAIL",
            str(defn),
        )


# ---------------------------------------------------------------------------
# 항상 실행되는 검사 (스키마 완전 여부와 무관)
# ---------------------------------------------------------------------------


def _check_forbidden_tables_absent(cur, results: list[CheckResult]) -> None:
    cur.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_name = ANY(%s)",
        (list(FORBIDDEN_TABLES),),
    )
    found = {r[0] for r in cur.fetchall()}
    _emit(
        results,
        "person_embeddings / person-person relation tables absent (R9, 원칙7)",
        "PASS" if not found else "FAIL",
        "none found" if not found else f"found forbidden tables: {sorted(found)}",
    )


def _check_alembic_version(cur, results: list[CheckResult]) -> None:
    try:
        cur.execute("SELECT version_num FROM alembic_version")
        rows = cur.fetchall()
        detail = ", ".join(r[0] for r in rows) if rows else "(empty)"
    except Exception as exc:  # noqa: BLE001 -- 정보용 조회, 실패해도 스크립트를 멈추지 않는다
        detail = f"(not found: {type(exc).__name__})"
    _emit(results, "alembic_version", "INFO", detail)


def run_all_checks(cur, expect_empty: bool) -> list[CheckResult]:
    results: list[CheckResult] = []

    cur.execute("SELECT version()")
    _emit(results, "server version", "INFO", cur.fetchone()[0])

    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    row = cur.fetchone()
    if row:
        _emit(results, "vector extension installed", "PASS", f"extversion={row[0]}")
    else:
        _emit(results, "vector extension installed", "FAIL", "pg_extension has no 'vector' row")

    cur.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_name = ANY(%s)",
        (list(EXPECTED_TABLES),),
    )
    present = {r[0] for r in cur.fetchall()}

    if expect_empty:
        ok = len(present) == 0
        _emit(
            results,
            "9 tables absent (--expect-empty)",
            "PASS" if ok else "FAIL",
            "0 tables (as expected)" if ok else f"still present: {sorted(present)}",
        )
    else:
        missing = sorted(set(EXPECTED_TABLES) - present)
        ok = present == set(EXPECTED_TABLES)
        _emit(
            results,
            "9 tables exist exactly",
            "PASS" if ok else "FAIL",
            f"got {len(present)}: {sorted(present)}" + (f" missing={missing}" if missing else ""),
        )

    schema_complete = set(EXPECTED_TABLES) <= present
    if schema_complete:
        _check_events_type(cur, results)
        _check_persons_checks(cur, results)
        _check_pending_questions_kind(cur, results)
        _check_embedding_vector(cur, results)
        _check_fact_sources_pk(cur, results)
        _check_foreign_keys(cur, results)
        _check_indexes(cur, results)
    else:
        _emit(
            results,
            "CHECK/PK/FK/vector/index structural checks",
            "SKIP",
            "9 테이블이 모두 있지 않아 테이블 의존 검사를 건너뜀",
        )

    _check_forbidden_tables_absent(cur, results)
    _check_alembic_version(cur, results)

    return results


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    conn, warnings = resolve_connection(dict(os.environ))
    for w in warnings:
        print(w)
    print(f"[info] 접속 대상: {conn.safe_summary()}")

    try:
        import psycopg
    except ImportError:
        print("[error] psycopg 가 설치되어 있지 않다.")
        print('        설치: pip install "psycopg[binary]"')
        return 2

    try:
        pg_conn = psycopg.connect(connect_timeout=5, **conn.as_keywords())
    except Exception as exc:  # noqa: BLE001 -- 접속 실패를 rc=2 로 통일, 비밀은 출력하지 않는다
        print(f"[error] DB 접속 실패: {type(exc).__name__}: {exc}")
        return 2

    try:
        pg_conn.autocommit = True  # 읽기 전용 조회만 하므로 문장마다 독립 트랜잭션으로 둔다
        with pg_conn.cursor() as cur:
            results = run_all_checks(cur, expect_empty=args.expect_empty)
    finally:
        pg_conn.close()

    return compute_exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
