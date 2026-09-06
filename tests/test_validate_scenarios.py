"""Refs: P1-pilot-dataset S3.7 S3.1 원칙8 -- scripts/validate_scenarios.py 검증기 테스트.

"위반을 못 잡는 검증기는 검증기가 아니다"(01-plan U1). 그래서 이 파일의 뼈대는
**정상 표본 1건 + 일부러 깨뜨린 표본**이다. 01-plan 42행이 명시한 위반 8종과
H-1(ambiguous) 예외, 결정 E(seed_persons), 함정 수(trap_count)를 각각 독립
테스트로 둔다.

검사 (12) surface-발화 대조·(13) 구어체 규칙(길이·턴 수)도 같은 방식으로 위반
표본과 경계값(8/60자, 2/6턴)을 함께 둔다. 저장소 실물 데이터셋에 대한 단정은
**건수에 의존하지 않는 불변식만** 쓴다(F-7bea05·F-1ba055) — U2~U4 가 데이터를
채우는 동안 깨지는 단정은 검증기가 아니라 달력을 시험한다.

네트워크·DB 를 쓰지 않는다. `tests/conftest.py` 의 `db_engine`/`db_session`
픽스처를 **의존하지 않으므로** PostgreSQL 없이도 전부 돈다(`dbtest` 마커 없음).
`app.db.models` 는 값 집합 튜플을 대조하기 위해서만 import 하며(검증기 본체는
app/ 를 import 하지 않는다) 이 import 는 DB 접속을 하지 않는다.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_scenarios as vs  # noqa: E402

from app.db.models import (  # noqa: E402
    EVENT_TYPES,
    HIERARCHIES,
    QUESTION_KINDS,
    RELATION_TAGS,
)

#: 저장소의 실제 스키마 파일을 tmp 데이터셋에 복사해 쓴다 -- 테스트가 스키마의
#: 사본을 따로 들고 있으면 스키마를 고쳤을 때 테스트만 통과하는 일이 생긴다.
REPO_SCENARIOS = REPO_ROOT / "data" / "scenarios"

CATEGORY_FILES = (
    "promotion.json",
    "pronoun.json",
    "alias.json",
    "normal.json",
    "new_person.json",
)

VALID_SCENARIO: dict = {
    "id": "sc-001",
    "category": "promotion",
    "persons": [
        {
            "person_id": "p1",
            "display_name": "김하늘",
            "relation_tag": "직장",
            "hierarchy": "상",
            "aliases": ["김팀장", "부장님"],
        }
    ],
    "seed_persons": ["p1"],
    "utterances": [
        "오늘 김팀장이랑 또 부딪혔어",
        "이제 부장님이라고 불러야 되나ㅋㅋ",
    ],
    "mentions": [
        {"turn": 0, "surface": "김팀장", "gold_person_id": "p1"},
        {"turn": 1, "surface": "부장님", "gold_person_id": "p1"},
    ],
    "events": [{"turn": 0, "type": "conflict", "occurred_at_kind": "relative"}],
    "expected_ask_user": {"allowed": ["identity", "none"]},
}

VIRTUAL_NAMES = ["김하늘", "김팀장", "부장님"]


# --------------------------------------------------------------------------
# 표본 만들기
# --------------------------------------------------------------------------


def scenario(**overrides) -> dict:
    """정상 시나리오의 깊은 복사본에 덮어쓰기."""
    item = copy.deepcopy(VALID_SCENARIO)
    item.update(copy.deepcopy(overrides))
    return item


def manifest_for(files: dict[str, list[dict]], **overrides) -> dict:
    """실제 내용과 **일치하는** manifest 를 만든다(위반 표본은 여기서 어긋내면 된다)."""
    scenarios = [s for items in files.values() for s in items]
    counts = {c: 0 for c in vs.CATEGORIES}
    for item in scenarios:
        category = item.get("category")
        if category in counts:
            counts[category] += 1
    data = {
        "schema_version": 1,
        "files": list(CATEGORY_FILES),
        "counts": counts,
        "total": len(scenarios),
        "ambiguous_mention_count": sum(
            1
            for s in scenarios
            for m in s.get("mentions", [])
            if m.get("ambiguous") is True
        ),
        "trap_count": sum(1 for s in scenarios if "trap" in s),
        "virtual_names": list(VIRTUAL_NAMES),
        "generator": {
            "model_id": None,
            "prompt_ref": None,
            "seed": None,
            "seed_reason": None,
            "same_family_as_judge": None,
        },
    }
    data.update(overrides)
    return data


def write_dataset(
    tmp_path: Path,
    files: dict[str, list[dict]] | None = None,
    manifest: dict | None = None,
) -> Path:
    """tmp_path 에 최소 데이터셋(스키마 2개 + manifest + 카테고리 파일)을 만든다."""
    files = {"promotion.json": [scenario()]} if files is None else files
    for name in (vs.SCENARIO_SCHEMA_FILE, vs.MANIFEST_SCHEMA_FILE):
        (tmp_path / name).write_text(
            (REPO_SCENARIOS / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    resolved = manifest_for(files) if manifest is None else manifest
    (tmp_path / vs.MANIFEST_FILE).write_text(
        json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for name, items in files.items():
        (tmp_path / name).write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return tmp_path


def checks(report: vs.Report) -> set[str]:
    return {issue.check for issue in report.issues}


def codes(report: vs.Report) -> set[str]:
    return {issue.code for issue in report.issues}


# --------------------------------------------------------------------------
# 정상 표본
# --------------------------------------------------------------------------


def test_valid_sample_passes(tmp_path: Path):
    """정상 표본 1건 + manifest 는 오류 0."""
    report = vs.run(write_dataset(tmp_path))
    assert report.issues == [], [i.line() for i in report.issues]
    assert report.ok is True
    summary = report.summary()
    assert summary["total"] == 1
    assert summary["counts"]["promotion"] == 1
    assert summary["scenario_count"] == 1


def test_valid_sample_exit_code_zero(tmp_path: Path, capsys):
    """CLI 종료 코드 0 + `--json` 이 기계 판독 가능한 요약을 낸다."""
    write_dataset(tmp_path)
    assert vs.main(["--dir", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["issues"] == []
    assert payload["files"][0] == {
        "file": "promotion.json",
        "exists": True,
        "count": 1,
    }


def test_run_is_deterministic(tmp_path: Path):
    """같은 입력 -> 같은 수치·같은 오류 순서(원칙8)."""
    write_dataset(tmp_path, {"promotion.json": [scenario(id="sc-002", seed_persons=["p9"])]})
    first = vs.run(tmp_path).summary()
    second = vs.run(tmp_path).summary()
    assert first == second


# --------------------------------------------------------------------------
# 위반 표본 8종 (01-plan 42행)
# --------------------------------------------------------------------------


def test_violation_1_schema(tmp_path: Path):
    """(1) 스키마 위반 -- id 가 전역 연번 규칙(sc-001)이 아니다(R-7)."""
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [scenario(id="promo-001")]}))
    assert "1" in checks(report)
    assert "SCHEMA" in codes(report)


def test_violation_1_schema_unknown_field(tmp_path: Path):
    """(1) additionalProperties: false -- 모르는 필드는 조용히 통과하지 않는다."""
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [scenario(top_k=5)]}))
    assert "1" in checks(report)


def test_violation_2_orphan_gold_person_id(tmp_path: Path):
    """(2) gold_person_id 가 persons 밖(미아 라벨)."""
    bad = scenario()
    bad["mentions"][0]["gold_person_id"] = "p9"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "GOLD_ID_ORPHAN" in codes(report)
    assert "2" in checks(report)


def test_violation_3_turn_out_of_range(tmp_path: Path):
    """(3) mention 의 turn 이 utterances 범위 밖."""
    bad = scenario()
    bad["mentions"][0]["turn"] = 5
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "TURN_OUT_OF_RANGE" in codes(report)
    assert "3" in checks(report)


def test_violation_3_event_turn_out_of_range(tmp_path: Path):
    """(3) events 의 turn 도 같은 규칙으로 본다."""
    bad = scenario()
    bad["events"][0]["turn"] = 9
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert any(
        i.code == "TURN_OUT_OF_RANGE" and "events[0]" in i.where for i in report.issues
    )


def test_violation_4_duplicate_id_across_files(tmp_path: Path):
    """(4) id 는 파일을 가로질러 전역 유일해야 한다."""
    files = {
        "promotion.json": [scenario()],
        "normal.json": [scenario(category="normal")],
    }
    report = vs.run(write_dataset(tmp_path, files))
    assert "DUPLICATE_ID" in codes(report)
    assert "4" in checks(report)


def test_violation_5_unknown_event_type(tmp_path: Path):
    """(5) events.type 이 고정 7종 밖 -- 스키마와 **별도 메시지**로도 잡힌다."""
    bad = scenario()
    bad["events"][0]["type"] = "gossip"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "EVENT_TYPE_UNKNOWN" in codes(report)
    assert {"1", "5"} <= checks(report)


def test_violation_6_manifest_counts_mismatch(tmp_path: Path):
    """(6) 배분표(counts·total)와 실제 건수 불일치."""
    files = {"promotion.json": [scenario()]}
    bad_manifest = manifest_for(files, counts={"promotion": 2, "pronoun": 0, "alias": 0, "normal": 0, "new_person": 0}, total=2)
    report = vs.run(write_dataset(tmp_path, files, bad_manifest))
    assert {"COUNT_MISMATCH", "TOTAL_MISMATCH"} <= codes(report)
    assert "6" in checks(report)


def test_violation_7_name_outside_virtual_names(tmp_path: Path):
    """(7) manifest.virtual_names 밖의 이름(개인정보 리스크, R-2)."""
    bad = scenario()
    bad["persons"][0]["display_name"] = "박서준"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "NAME_NOT_IN_VIRTUAL_NAMES" in codes(report)
    assert "7" in checks(report)


def test_violation_7_alias_name_pattern(tmp_path: Path):
    """(7) 한글 2~4자 alias 도 화이트리스트 대상(규칙을 넓게 잡았다)."""
    bad = scenario()
    bad["persons"][0]["aliases"] = ["김팀장", "부장님", "이서연"]
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert any(
        i.code == "NAME_NOT_IN_VIRTUAL_NAMES" and "이서연" in i.message
        for i in report.issues
    )


def test_check_7_ignores_long_non_name_alias(tmp_path: Path):
    """(7) 한글 5자 이상 별명은 성명 패턴이 아니라 통과 -- 규칙이 문서와 같다."""
    ok = scenario()
    ok["persons"][0]["aliases"] = ["김팀장", "부장님", "우리회사부장님"]
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [ok]}))
    assert report.issues == [], [i.line() for i in report.issues]


def test_violation_8_ambiguous_count_mismatch(tmp_path: Path):
    """(8) manifest.ambiguous_mention_count 와 실제 ambiguous mention 수 불일치."""
    files = {"promotion.json": [scenario()]}
    report = vs.run(
        write_dataset(tmp_path, files, manifest_for(files, ambiguous_mention_count=1))
    )
    assert "AMBIGUOUS_COUNT_MISMATCH" in codes(report)
    assert "8" in checks(report)


# --------------------------------------------------------------------------
# 결정 E (9) · 함정 (10)
# --------------------------------------------------------------------------


def test_violation_9_seed_person_not_in_persons(tmp_path: Path):
    """(9) seed_persons 가 persons 의 부분집합이 아니다(결정 E)."""
    report = vs.run(
        write_dataset(tmp_path, {"promotion.json": [scenario(seed_persons=["p1", "p7"])]})
    )
    assert "SEED_PERSON_UNKNOWN" in codes(report)
    assert "9" in checks(report)


def test_violation_10_trap_count_mismatch(tmp_path: Path):
    """(10) manifest.trap_count 와 trap 필드를 가진 시나리오 수 불일치."""
    files = {"promotion.json": [scenario()]}
    report = vs.run(write_dataset(tmp_path, files, manifest_for(files, trap_count=1)))
    assert "TRAP_COUNT_MISMATCH" in codes(report)
    assert "10" in checks(report)


def test_trap_scenario_counted(tmp_path: Path):
    """trap 을 단 시나리오는 trap_count 에 세어지고, 맞으면 통과한다."""
    trapped = scenario(trap={"kind": "유사 호칭 동료", "reason": "같은 부서에 김팀장이 둘"})
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [trapped]}))
    assert report.issues == [], [i.line() for i in report.issues]
    assert report.summary()["trap_count"] == 1


# --------------------------------------------------------------------------
# H-1 (ambiguous) 예외
# --------------------------------------------------------------------------


def test_null_gold_without_ambiguous_flag_fails(tmp_path: Path):
    """H-1 -- ambiguous 플래그가 **없으면** gold_person_id: null 은 FAIL."""
    bad = scenario()
    bad["mentions"][0]["gold_person_id"] = None
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "GOLD_NULL_NOT_AMBIGUOUS" in codes(report)


def test_null_gold_with_ambiguous_false_fails(tmp_path: Path):
    """H-1 -- ambiguous: false 인데 null 이면 FAIL(라벨 공백을 숨길 수 없다)."""
    bad = scenario()
    bad["mentions"][0]["gold_person_id"] = None
    bad["mentions"][0]["ambiguous"] = False
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "GOLD_NULL_NOT_AMBIGUOUS" in codes(report)


def test_null_gold_with_ambiguous_true_passes(tmp_path: Path):
    """H-1 -- ambiguous: true 인 mention 만 null 을 허용한다. 개수도 세어진다."""
    ok = scenario(category="pronoun")
    ok["mentions"][0]["gold_person_id"] = None
    ok["mentions"][0]["ambiguous"] = True
    report = vs.run(write_dataset(tmp_path, {"pronoun.json": [ok]}))
    assert report.issues == [], [i.line() for i in report.issues]
    assert report.summary()["ambiguous_mention_count"] == 1


# --------------------------------------------------------------------------
# 적재 (검사 0) · strict 모드
# --------------------------------------------------------------------------


def test_missing_manifest_is_reported(tmp_path: Path):
    """manifest.json 이 없으면 검사 (0) 으로 보고하고 죽지 않는다."""
    write_dataset(tmp_path)
    (tmp_path / vs.MANIFEST_FILE).unlink()
    report = vs.run(tmp_path)
    assert "MANIFEST_LOAD" in codes(report)
    assert report.ok is False


def test_scenario_file_not_array_is_reported(tmp_path: Path):
    """카테고리 파일이 배열이 아니면 검사 (1) 로 보고한다."""
    write_dataset(tmp_path)
    (tmp_path / "promotion.json").write_text('{"id": "sc-001"}', encoding="utf-8")
    report = vs.run(tmp_path)
    assert "FILE_NOT_ARRAY" in codes(report)


def test_missing_file_is_zero_in_default_mode_and_fail_in_strict(tmp_path: Path):
    """남긴 결정 -- 없는 파일은 기본 0건, `--strict` 면 FAIL."""
    files = {"promotion.json": [scenario()]}
    write_dataset(tmp_path, files)
    assert vs.run(tmp_path).ok is True  # 나머지 4파일이 없어도 통과
    strict = vs.run(tmp_path, strict=True)
    assert "FILE_MISSING" in codes(strict)
    assert strict.ok is False


def test_main_returns_2_for_missing_dir(tmp_path: Path):
    assert vs.main(["--dir", str(tmp_path / "없는디렉터리")]) == 2


# --------------------------------------------------------------------------
# 검사 (12) surface 가 그 turn 의 발화 안에 있는가
# --------------------------------------------------------------------------


def test_violation_12_surface_not_in_utterance(tmp_path: Path):
    """(12) 발화에 없는 지칭을 라벨하면 FAIL -- 아무 모델도 맞힐 수 없는 라벨이다."""
    bad = scenario()
    bad["mentions"][0]["surface"] = "박팀장"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "SURFACE_NOT_IN_UTTERANCE" in codes(report)
    assert "12" in checks(report)


def test_check_12_does_not_normalize_whitespace(tmp_path: Path):
    """(12) 공백을 정규화하지 않는다 -- "김 팀장" != "김팀장"."""
    bad = scenario()
    bad["mentions"][0]["surface"] = "김 팀장"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "SURFACE_NOT_IN_UTTERANCE" in codes(report)


def test_check_12_surface_in_wrong_turn_fails(tmp_path: Path):
    """(12) 발화 어딘가가 아니라 **그 turn** 의 발화에 있어야 한다."""
    bad = scenario()
    bad["mentions"][0]["surface"] = "부장님"  # 0턴이 아니라 1턴에 있는 말
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert any(
        i.code == "SURFACE_NOT_IN_UTTERANCE" and "mentions[0]" in i.where
        for i in report.issues
    )


def test_check_12_accepts_partial_substring(tmp_path: Path):
    """(12) 부분 문자열이면 통과한다("김팀장" 안의 "팀장")."""
    ok = scenario()
    ok["mentions"][0]["surface"] = "팀장"
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [ok]}))
    assert report.issues == [], [i.line() for i in report.issues]


def test_check_12_skips_out_of_range_turn(tmp_path: Path):
    """(12) turn 이 범위 밖이면 검사 (3) 만 보고한다(한 결함에 두 번 FAIL 금지)."""
    bad = scenario()
    bad["mentions"][0]["turn"] = 5
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [bad]}))
    assert "TURN_OUT_OF_RANGE" in codes(report)
    assert "SURFACE_NOT_IN_UTTERANCE" not in codes(report)


# --------------------------------------------------------------------------
# 검사 (13) 발화 길이·턴 수 (구어체 규칙)
# --------------------------------------------------------------------------


def shaped(lengths: list[int]) -> dict:
    """길이가 정확히 `lengths` 인 발화들로 시나리오를 만든다(전부 "김팀장" 포함)."""
    return scenario(
        utterances=["김팀장" + "가" * (n - 3) for n in lengths],
        mentions=[{"turn": 0, "surface": "김팀장", "gold_person_id": "p1"}],
        events=[{"turn": 0, "type": "conflict", "occurred_at_kind": "relative"}],
    )


def test_shape_constants_match_plan():
    """경계값은 01-plan 리스크 줄·U2 생성 프롬프트와 같은 숫자여야 한다."""
    assert (vs.UTTERANCE_MIN_CHARS, vs.UTTERANCE_MAX_CHARS) == (8, 60)
    assert (vs.MIN_TURNS, vs.MAX_TURNS) == (2, 6)


@pytest.mark.parametrize("length", [7, 61])
def test_violation_13_utterance_length_out_of_range(tmp_path: Path, length: int):
    """(13) 7자·61자는 FAIL -- 너무 짧으면 지칭이 못 들어가고, 길면 문어체다."""
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [shaped([length, 12])]}))
    assert "UTTERANCE_LENGTH" in codes(report)
    assert "13" in checks(report)


@pytest.mark.parametrize("length", [8, 60])
def test_check_13_accepts_boundary_lengths(tmp_path: Path, length: int):
    """(13) 8자·60자는 통과 -- 경계는 양끝을 **포함**한다."""
    report = vs.run(write_dataset(tmp_path, {"promotion.json": [shaped([length, 12])]}))
    assert report.issues == [], [i.line() for i in report.issues]


@pytest.mark.parametrize("turns", [1, 7])
def test_violation_13_turn_count_out_of_range(tmp_path: Path, turns: int):
    """(13) 1턴·7턴은 FAIL."""
    report = vs.run(
        write_dataset(tmp_path, {"promotion.json": [shaped([12] * turns)]})
    )
    assert "TURN_COUNT" in codes(report)
    assert "13" in checks(report)


@pytest.mark.parametrize("turns", [2, 6])
def test_check_13_accepts_boundary_turn_counts(tmp_path: Path, turns: int):
    """(13) 2턴·6턴은 통과."""
    report = vs.run(
        write_dataset(tmp_path, {"promotion.json": [shaped([12] * turns)]})
    )
    assert report.issues == [], [i.line() for i in report.issues]


def test_check_names_cover_registered_checks():
    """사람이 읽는 출력·`--json` 요약이 새 검사도 다른 검사와 같은 형식으로 낸다."""
    assert set(vs.CHECK_NAMES) == {
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "12", "13"
    }
    assert "11" not in vs.CHECK_NAMES  # U5 예정 -- 하지 않는 검사에 PASS 를 찍지 않는다


# --------------------------------------------------------------------------
# 값 집합이 app.db.models 와 글자 그대로 같은가
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scenario_schema() -> dict:
    return json.loads((REPO_SCENARIOS / "schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest_schema() -> dict:
    return json.loads(
        (REPO_SCENARIOS / "manifest.schema.json").read_text(encoding="utf-8")
    )


def test_schema_event_type_enum_matches_models(scenario_schema: dict):
    """`events.type` enum == app.db.models.EVENT_TYPES (순서까지)."""
    enum = scenario_schema["$defs"]["event"]["properties"]["type"]["enum"]
    assert tuple(enum) == EVENT_TYPES


def test_schema_relation_tag_enum_matches_models(scenario_schema: dict):
    enum = scenario_schema["$defs"]["person"]["properties"]["relation_tag"]["enum"]
    assert tuple(enum) == RELATION_TAGS


def test_schema_hierarchy_enum_matches_models(scenario_schema: dict):
    enum = scenario_schema["$defs"]["person"]["properties"]["hierarchy"]["enum"]
    assert tuple(enum) == HIERARCHIES


def test_expected_ask_user_allowed_is_separate_from_question_kinds(scenario_schema: dict):
    """R-1 -- `expected_ask_user.allowed` 는 `ask_user.kind` 와 별도 enum이다.

    `none`(질문하지 않아도 됨)은 kind 값이 아니고, `schedule` 은 결정 C 로 P1
    에서 라벨하지 않으므로 허용 집합에 없다.
    """
    allowed = scenario_schema["$defs"]["expected_ask_user"]["properties"]["allowed"][
        "items"
    ]["enum"]
    assert tuple(allowed) == ("identity", "new_person", "none")
    assert "schedule" in QUESTION_KINDS
    assert "schedule" not in allowed
    assert "none" not in QUESTION_KINDS


def test_validator_reads_event_types_from_schema_not_hardcoded(scenario_schema: dict):
    """검사 (5) 의 목록은 스키마에서 읽는다(하드코딩 두 벌이 어긋나는 것 방지)."""
    assert vs.event_type_enum(scenario_schema) == EVENT_TYPES


def test_schema_versions_match(scenario_schema: dict, manifest_schema: dict):
    """schema.json·manifest.schema.json·manifest.json 의 판이 1 로 일치한다."""
    real_manifest = json.loads(
        (REPO_SCENARIOS / "manifest.json").read_text(encoding="utf-8")
    )
    assert scenario_schema["schema_version"] == 1
    assert manifest_schema["schema_version"] == 1
    assert manifest_schema["properties"]["schema_version"]["const"] == 1
    assert real_manifest["schema_version"] == 1


# --------------------------------------------------------------------------
# 빈 데이터셋 · 저장소 실물 (시점 무관 단정만)
# --------------------------------------------------------------------------


def test_empty_dataset_passes_with_zero_scenarios(tmp_path: Path, capsys):
    """시나리오 **파일이 하나도 없어도** 검증기는 rc=0 · 총 0건이다.

    U1 의 검사 의도(F-7bea05 해결 1단계)를 저장소 대신 빈 fixture 로 옮겼다.
    저장소를 대상으로 `total == 0` 을 단정하면 U2 가 데이터를 넣는 순간 깨지는
    **시점 의존 단정**이 된다 — 검증기의 성질이 아니라 달력을 시험하게 된다.
    """
    write_dataset(tmp_path, files={})
    assert vs.main(["--dir", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["total"] == 0
    assert payload["scenario_count"] == 0
    assert payload["counts"] == {c: 0 for c in vs.CATEGORIES}
    assert [f["file"] for f in payload["files"]] == list(CATEGORY_FILES)
    assert [f["exists"] for f in payload["files"]] == [False] * len(CATEGORY_FILES)


def test_repository_dataset_satisfies_time_invariant_properties(capsys):
    """저장소 데이터셋: 건수에 의존하지 않는 불변식만 본다(F-7bea05 2단계).

    U2~U4 가 시나리오를 채우는 동안에도 참이어야 하는 것 — rc=0, manifest 와
    실제 건수 일치, 카테고리 키 집합, 파일 순서.
    """
    real_manifest = json.loads(
        (REPO_SCENARIOS / "manifest.json").read_text(encoding="utf-8")
    )
    assert vs.main(["--dir", str(REPO_SCENARIOS), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["total"] == real_manifest["total"]
    assert payload["scenario_count"] == real_manifest["total"]
    assert set(payload["counts"]) == set(vs.CATEGORIES)
    assert payload["counts"] == real_manifest["counts"]
    assert [f["file"] for f in payload["files"]] == list(CATEGORY_FILES)


def test_repository_manifest_generator_keys_exist():
    """H-2 -- generator 키 5종은 값이 비어 있든 채워졌든 **항상** 존재해야 한다.

    값이 채워졌는지(`model_id`·`prompt_ref` != null)는 U5/U7 수용 기준이 본다.
    테스트에 넣으면 U2~U4 진행 중 다시 시점 의존이 된다(F-1ba055 2단계).
    """
    real_manifest = json.loads(
        (REPO_SCENARIOS / "manifest.json").read_text(encoding="utf-8")
    )
    assert set(real_manifest["generator"]) == {
        "model_id",
        "prompt_ref",
        "seed",
        "seed_reason",
        "same_family_as_judge",
    }
    names = real_manifest["virtual_names"]
    # F-1ba055 -- `== []` 는 U1 시점에서만 참이다. 시점 무관 성질만 본다:
    # 문자열 목록이고, 비어 있지 않은 값이며, 중복이 없다(중복은 검사 (7) 의
    # 화이트리스트를 부풀리기만 하고 아무 것도 더 허용하지 않는다).
    assert isinstance(names, list)
    assert all(isinstance(n, str) and n.strip() for n in names)
    assert len(set(names)) == len(names), "virtual_names 에 중복이 있다"


def test_repository_manifest_validates_against_manifest_schema(manifest_schema: dict):
    """저장소의 manifest.json 이 매니페스트 스키마를 통과한다."""
    from jsonschema import Draft202012Validator

    real_manifest = json.loads(
        (REPO_SCENARIOS / "manifest.json").read_text(encoding="utf-8")
    )
    errors = list(Draft202012Validator(manifest_schema).iter_errors(real_manifest))
    assert errors == [], [e.message for e in errors]


def test_prompt_ref_accepts_string_and_list(manifest_schema: dict):
    """R-8 -- prompt_ref 는 string 또는 string[] 둘 다 허용한다."""
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(manifest_schema)
    base = json.loads((REPO_SCENARIOS / "manifest.json").read_text(encoding="utf-8"))
    for value in ("evidence/x-gen-prompt.md", ["a.md", "b.md"]):
        candidate = copy.deepcopy(base)
        candidate["generator"]["prompt_ref"] = value
        assert list(validator.iter_errors(candidate)) == []
