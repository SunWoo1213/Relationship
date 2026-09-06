"""Refs: P3-er 01-plan U8 D4 D5 -- scripts/backfill_embeddings.py 단위 테스트.

네트워크(OpenAI) 호출 없음. `select_targets`/`main(["--dry-run"])` 만 실
PostgreSQL(`POSTGRES_PORT`, 기본 5433) 롤백 픽스처(`db_session`/`db_engine`,
`tests/conftest.py`)를 쓴다. 나머지(`parse_args`·`chunk`·`--apply` 키 없음)
는 DB 없이 돈다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import backfill_embeddings as be  # noqa: E402

from app.db.models import Person, PersonAlias  # noqa: E402

#: 테스트 전용 가짜 키 값 -- 실제 API 키 형식이 아니다(값 노출 검사의
#: 대조군일 뿐, secret-guard 회피 목적이 아니다). `tests/test_embedding_provider.py`
#: 와 같은 형태를 쓴다.
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"


# ---------- parse_args ----------


def test_parse_args_defaults_to_dry_run():
    args = be.parse_args([])
    assert args.apply is False
    assert args.dry_run is True
    assert args.batch_size == be.DEFAULT_BATCH_SIZE
    assert args.limit is None


def test_parse_args_apply_flag_sets_dry_run_false():
    args = be.parse_args(["--apply"])
    assert args.apply is True
    assert args.dry_run is False


def test_parse_args_explicit_dry_run_flag():
    args = be.parse_args(["--dry-run"])
    assert args.apply is False
    assert args.dry_run is True


def test_parse_args_batch_size_and_limit():
    args = be.parse_args(["--batch-size", "8", "--limit", "20"])
    assert args.batch_size == 8
    assert args.limit == 20


def test_parse_args_apply_and_dry_run_are_mutually_exclusive():
    with pytest.raises(SystemExit):
        be.parse_args(["--apply", "--dry-run"])


# ---------- chunk ----------


def test_chunk_splits_evenly():
    assert be.chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_chunk_splits_with_remainder():
    assert be.chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_chunk_empty_sequence_yields_no_batches():
    assert be.chunk([], 5) == []


def test_chunk_rejects_non_positive_batch_size():
    with pytest.raises(ValueError):
        be.chunk([1, 2, 3], 0)
    with pytest.raises(ValueError):
        be.chunk([1, 2, 3], -1)


# ---------- select_targets (실 DB 롤백 픽스처) ----------


@pytest.mark.dbtest
def test_select_targets_excludes_aliases_with_embedding(db_session):
    person = Person(
        user_id="u-test-backfill-null",
        display_name="테스트인물",
        relation_tag="지인",
        hierarchy="동",
    )
    db_session.add(person)
    db_session.flush()

    alias_null = PersonAlias(person_id=person.id, alias="널별칭", source="user_said")
    alias_filled = PersonAlias(
        person_id=person.id,
        alias="채워진별칭",
        source="user_said",
        embedding=[0.1] * 1536,
    )
    db_session.add_all([alias_null, alias_filled])
    db_session.flush()

    targets = be.select_targets(db_session)
    target_ids = {alias_id for alias_id, _alias in targets}

    assert alias_null.id in target_ids
    assert alias_filled.id not in target_ids


@pytest.mark.dbtest
def test_select_targets_respects_limit(db_session):
    person = Person(
        user_id="u-test-backfill-limit",
        display_name="테스트인물2",
        relation_tag="지인",
        hierarchy="동",
    )
    db_session.add(person)
    db_session.flush()

    aliases = [
        PersonAlias(person_id=person.id, alias=f"별칭{i}", source="user_said")
        for i in range(5)
    ]
    db_session.add_all(aliases)
    db_session.flush()

    targets = be.select_targets(db_session, limit=2)
    assert len(targets) == 2


# ---------- main(): --apply 키 없음 -> 2, 키 미노출 ----------


def test_main_apply_without_key_returns_2(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    rc = be.main(["--apply"])
    assert rc == 2

    captured = capsys.readouterr()
    assert "OPENAI_API_KEY" in captured.out  # 변수 "이름"은 안내해야 한다


def test_main_apply_without_key_does_not_touch_db_or_leak_key(monkeypatch, capsys):
    # 키 검사가 DB 접속보다 먼저 -- 접속 정보가 잘못돼 있어도(존재하지 않는
    # 포트로 바꿔도) 여전히 rc=2 여야 한다(DB 를 건드리지 않는다는 증거).
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("POSTGRES_PORT", "1")  # 접속 불가능한 포트

    rc = be.main(["--apply"])
    assert rc == 2

    captured = capsys.readouterr()
    assert _FAKE_KEY_MARKER not in captured.out


# ---------- main(): --dry-run 쓰기 0 (실 DB) ----------


def _count_null_embedding_aliases(engine) -> int:
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT count(*) FROM person_aliases WHERE embedding IS NULL")
        ).scalar()


@pytest.mark.dbtest
def test_main_dry_run_writes_nothing(db_engine, capsys):
    before = _count_null_embedding_aliases(db_engine)

    rc = be.main(["--dry-run"])

    after = _count_null_embedding_aliases(db_engine)
    assert rc == 0
    assert after == before

    captured = capsys.readouterr()
    assert "dry-run" in captured.out
    assert "쓰기 0건" in captured.out
