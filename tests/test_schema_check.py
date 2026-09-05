"""Refs: P1-schema R8 R9 D4 D5 S3.1 -- scripts/schema_check.py 의 DB 없는 부분 테스트.

DB 접속이 필요한 부분(개별 `_check_*` 함수의 실제 쿼리)은 U4 의 왕복 evidence
로 검증한다. 여기서는 기대값이 `app.db.models`/`app.db.base` 를 그대로
가져오는지(중복 정의 방지), 집계·CLI 파싱이 올바른지만 확인한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import schema_check as sc  # noqa: E402

import app.db.models as models  # noqa: E402
from app.db.base import Base  # noqa: E402


def test_expected_tables_matches_base_metadata_exactly():
    """`EXPECTED_TABLES` 는 하드코딩이 아니라 `Base.metadata.tables` 에서 그대로 가져온 것이다."""
    assert set(sc.EXPECTED_TABLES) == set(Base.metadata.tables.keys())
    assert len(sc.EXPECTED_TABLES) == 9


def test_expected_tables_excludes_person_embeddings_and_relation_tables():
    """R9/원칙7 부재 대상은 애초에 EXPECTED_TABLES(모델)에 없다."""
    for forbidden in ("person_embeddings", "person_relations", "relationships"):
        assert forbidden not in sc.EXPECTED_TABLES
        assert forbidden in sc.FORBIDDEN_TABLES


def test_check_value_constants_are_the_same_object_as_models_not_redefined():
    """schema_check 가 값 집합을 다시 정의하지 않고 app.db.models 를 그대로 참조한다(단일 출처)."""
    assert sc.m is models
    assert sc.m.EVENT_TYPES is models.EVENT_TYPES
    assert sc.m.RELATION_TAGS is models.RELATION_TAGS
    assert sc.m.HIERARCHIES is models.HIERARCHIES
    assert sc.m.QUESTION_KINDS is models.QUESTION_KINDS
    assert len(sc.m.EVENT_TYPES) == 7
    assert len(sc.m.RELATION_TAGS) == 5
    assert len(sc.m.HIERARCHIES) == 3
    assert len(sc.m.QUESTION_KINDS) == 3


def test_missing_values_helper_finds_absent_entries():
    haystack = "CHECK ((type = ANY (ARRAY['conflict'::text, 'praise'::text])))"
    missing = sc._missing_values(("conflict", "praise", "meal"), haystack)
    assert missing == ["meal"]

    complete_haystack = "conflict praise meal meeting personal_share favor other"
    assert sc._missing_values(sc.m.EVENT_TYPES, complete_haystack) == []


def test_model_index_expectations_returns_ten_names_and_the_partial_index():
    names, partial_name = sc.model_index_expectations()
    assert len(names) == 10
    assert partial_name == "ix_pending_questions_session_id_unanswered"
    assert partial_name in names


def test_compute_exit_code_is_zero_when_all_pass_or_info_or_skip():
    results = [
        sc.CheckResult("a", "PASS"),
        sc.CheckResult("b", "INFO", "server info"),
        sc.CheckResult("c", "SKIP", "schema incomplete"),
    ]
    assert sc.compute_exit_code(results) == 0


def test_compute_exit_code_is_one_when_any_single_fail_present():
    """FAIL 하나만 섞여 있어도 exit code 는 1 이다 -- 항상 통과하는 테스트가 아니다."""
    results = [
        sc.CheckResult("a", "PASS"),
        sc.CheckResult("b", "FAIL", "events.type missing 'other'"),
        sc.CheckResult("c", "INFO"),
    ]
    assert sc.compute_exit_code(results) == 1


def test_compute_exit_code_ignores_status_order():
    results = [sc.CheckResult("z", "FAIL"), sc.CheckResult("a", "PASS")]
    assert sc.compute_exit_code(results) == 1
    results2 = [sc.CheckResult("a", "PASS"), sc.CheckResult("z", "FAIL")]
    assert sc.compute_exit_code(results2) == 1


def test_expect_empty_flag_defaults_to_false():
    args = sc.parse_args([])
    assert args.expect_empty is False


def test_expect_empty_flag_true_when_passed():
    args = sc.parse_args(["--expect-empty"])
    assert args.expect_empty is True


def test_emit_records_result_and_prints_tagged_line(capsys):
    results: list[sc.CheckResult] = []
    sc._emit(results, "예시 검사", "FAIL", "상세 사유")
    captured = capsys.readouterr()
    assert results[-1] == sc.CheckResult("예시 검사", "FAIL", "상세 사유")
    assert captured.out.startswith("[FAIL] 예시 검사 -> 상세 사유")
