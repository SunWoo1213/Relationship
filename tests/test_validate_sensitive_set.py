"""Refs: P9d-sensitive-guard D20 S3.7 CR-009 원칙8 -- 민감 가드 시험 세트 검사기의 계약 시험.

`scripts/validate_sensitive_set.py` 는 test 세트를 고칠 때마다 U1 수용 기준의 판정
명령이 된다. 실데이터로는 검사기가 망가져도 `결과: PASS` 가 그대로 나올 수 있어
(review-u1 R-3 — 중복 판정을 파일별로 초기화하는 변이 C01), 계약을 이 파일이 고정한다.

- 저장소의 `evaluation/sensitive_guard/test.jsonl`·`dev.jsonl` 은 **읽지 않는다**
  (test 는 평가에서만 연다 — 01-plan U1·U2). 모든 시험은 `tmp_path` 에 만든 작은
  합성 세트를 쓴다. 합성 문장은 뜻 없는 자리 문장이다.
- 식별번호 모양은 시험 안에서 계산해 만든다: 주민등록번호 모양은 검증 숫자를
  일부러 맞추거나 어긋나게, 목록 밖 카드번호는 실재하지 않는 `9999…` 머리에 Luhn
  끝자리만 맞춘다.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_sensitive_set as vss  # noqa: E402

Row = dict[str, str]

# ---------------------------------------------------------------- 합성 세트 만들기


def _rrn(seed: int, *, valid: bool) -> str:
    """주민등록번호 모양 13자리(하이픈 없이). valid=True 면 검증 숫자가 맞는다."""
    yy = 80 + seed % 20
    mm = 1 + seed % 12
    dd = 1 + seed % 28
    head = f"{yy:02d}{mm:02d}{dd:02d}1{seed:05d}"
    check = vss.rrn_check_digit(head + "0")
    last = check if valid else (check + 1) % 10
    return head + str(last)


def _luhn_outside_list() -> str:
    """Luhn 이 맞는 16자리 — 실재하지 않는 9999 머리, 공개 시험 번호 목록 밖."""
    head = "999999999999999"
    for d in range(10):
        if vss.luhn_ok(head + str(d)):
            return head + str(d)
    raise AssertionError("Luhn 끝자리를 찾지 못함")


def _rows(split: str) -> list[Row]:
    """크기 계약을 정확히 채운 합성 한 파일(파일마다 문장이 다르다)."""
    seed0 = 0 if split == "dev" else 500
    rows: list[Row] = []

    def add(text: str, label: str, group: str, **extra: str) -> None:
        rows.append({"id": f"{split}-{len(rows) + 1:03d}", "text": text, "label": label, "group": group, "note": "합성", **extra})

    for cat in vss.CATEGORIES:
        for i in range(15):
            extra = {"form": "query"} if i < 2 else {}
            add(f"{split} 동의 {cat} 합성 문장 가{i}", f"consent:{cat}", "sensitive", **extra)
    cards = sorted(vss.PUBLIC_TEST_CARDS)
    for btype in vss.BLOCK_TYPES:
        for i in range(15):
            if btype == "rrn":
                d = _rrn(seed0 + i, valid=False)
                add(f"{split} 주민 합성 {d[:6]}-{d[6:]}", "block:rrn", "sensitive")
            elif btype == "card":
                add(f"{split} 카드 합성 {cards[i]}", "block:card", "sensitive")
            else:
                add(f"{split} 가림 {btype} 합성 문장 나{i}", f"block:{btype}", "sensitive")
    for i in range(100):
        add(f"{split} 평범 합성 문장 다{i}", "none", "plain")
    add(f"{split} 교회 오빠 합성 함정", "none", "trap", trap="honorific_name")
    add(f"{split} 정신과 선생님 합성 함정", "none", "trap", trap="honorific_name")
    for i in range(28):
        add(f"{split} 함정 합성 문장 라{i}", "none", "trap", trap="keyword_lookalike")
    # 우회 20 을 모두 consent:crime 으로 둔다 — 우회가 범주 셈에 들어가면 crime 이
    # 35 가 되어 상한 20 을 넘으므로, 대조군 통과 자체가 "우회는 범주 셈 밖" 을 단언한다.
    for i in range(20):
        add(f"{split} 우회 합성 문장 마{i}", "consent:crime", "evasion")
    return rows


def _write(root: Path, dev: list[Row], test: list[Row]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for name, rows in (("dev", dev), ("test", test)):
        body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        (root / f"{name}.jsonl").write_text(body, encoding="utf-8")
    return root


def _validate(tmp_path: Path, dev: list[Row], test: list[Row]) -> tuple[list[str], list[str]]:
    return vss.validate(_write(tmp_path / "set", dev, test))


def _first(rows: list[Row], **match: str) -> Row:
    return next(r for r in rows if all(r.get(k) == v for k, v in match.items()))


def _report_line(report: list[str], split: str, label: str) -> str:
    start = report.index(next(line for line in report if line.startswith(f"[{split}]")))
    return next(line for line in report[start:] if line.strip().startswith(label + " "))


# ---------------------------------------------------------------- 대조군


def test_synthetic_control_passes(tmp_path: Path) -> None:
    """크기 계약을 정확히 채운 합성 세트는 오류 0, 종료 코드 0."""
    dev, test = _rows("dev"), _rows("test")
    report, errors = _validate(tmp_path, dev, test)
    assert errors == []
    assert vss.main([str(tmp_path / "set")]) == 0
    assert "dev/test 문장 중복(한 파일 안 포함): 0" in report


def test_evasion_rows_are_not_counted_in_category(tmp_path: Path) -> None:
    """우회 20(전부 consent:crime)은 범주 셈 밖 — crime 은 sensitive 15 만 센다(빈자리 ⑧)."""
    report, errors = _validate(tmp_path, _rows("dev"), _rows("test"))
    assert errors == []
    assert _report_line(report, "dev", "consent:crime").split()[1:3] == ["15", "OK"]


# ---------------------------------------------------------------- 중복


def test_dev_sentence_copied_into_test_fails(tmp_path: Path) -> None:
    """dev 문장 1줄을 test 에 그대로 → 문장 중복 1건(파일 사이 중복 판정)."""
    dev, test = _rows("dev"), _rows("test")
    _first(test, group="plain")["text"] = _first(dev, group="plain")["text"]
    report, errors = _validate(tmp_path, dev, test)
    # 합성 세트의 첫 평범 줄은 166번째 줄(동의 75 + 가림 90 다음)이다.
    assert errors == ["test:166:test-166: 문장 중복(먼저 dev:166:dev-166)"]
    assert "dev/test 문장 중복(한 파일 안 포함): 1" in report


def test_duplicate_after_nfc_and_whitespace_normalisation_fails(tmp_path: Path) -> None:
    """NFD 로 풀어 쓰고 공백을 늘린 같은 문장도 중복이다(NFC·공백 정리 뒤 비교)."""
    dev, test = _rows("dev"), _rows("test")
    original = _first(dev, group="plain")["text"]
    variant = "  " + unicodedata.normalize("NFD", original).replace(" ", "   ") + " "
    assert variant != original
    _first(test, group="plain")["text"] = variant
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["test:166:test-166: 문장 중복(먼저 dev:166:dev-166)"]


def test_duplicate_within_one_file_fails(tmp_path: Path) -> None:
    """한 파일 안의 같은 문장도 중복이다."""
    dev, test = _rows("dev"), _rows("test")
    plains = [r for r in dev if r["group"] == "plain"]
    plains[1]["text"] = plains[0]["text"]
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["dev:167:dev-167: 문장 중복(먼저 dev:166:dev-166)"]


def test_duplicate_id_across_files_fails(tmp_path: Path) -> None:
    """id 는 두 파일을 통틀어 유일하다."""
    dev, test = _rows("dev"), _rows("test")
    test[0]["id"] = dev[0]["id"]
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["test:1:dev-001: id 중복(먼저 dev:1:dev-001)"]


# ---------------------------------------------------------------- 크기


@pytest.mark.parametrize(("count", "ok"), [(14, False), (15, True), (20, True), (21, False)])
def test_category_count_bounds(tmp_path: Path, count: int, ok: bool) -> None:
    """범주·유형마다 15~20(사용자 결정 12) — 14·21 은 FAIL, 15·20 은 통과(경계 포함)."""
    dev, test = _rows("dev"), _rows("test")
    health = [r for r in test if r["label"] == "consent:health" and r["group"] == "sensitive"]
    plain_part = [r for r in health if "form" not in r]
    if count < 15:
        for r in plain_part[: 15 - count]:
            test.remove(r)
    for i in range(count - 15):
        test.append({"id": f"test-9{i:02d}", "text": f"test 동의 health 추가 합성 문장 바{i}", "label": "consent:health", "group": "sensitive", "note": "합성"})
    _, errors = _validate(tmp_path, dev, test)
    expected = f"test: consent:health {count}건 (기준 15~20)"
    if ok:
        assert errors == []
    else:
        assert errors == [expected]


@pytest.mark.parametrize(("queries", "ok"), [(0, False), (1, True)])
def test_query_minimum_per_category(tmp_path: Path, queries: int, ok: bool) -> None:
    """동의 범주마다 조회형 ≥ 1(빈자리 ⑧) — 0 은 FAIL, 1 은 통과."""
    dev, test = _rows("dev"), _rows("test")
    sex_queries = [r for r in dev if r["label"] == "consent:sex" and r.get("form") == "query"]
    assert len(sex_queries) == 2
    for r in sex_queries[queries:]:
        del r["form"]
    _, errors = _validate(tmp_path, dev, test)
    if ok:
        assert errors == []
    else:
        assert errors == ["dev: consent:sex 조회형 0건 (기준 ≥ 1)"]


@pytest.mark.parametrize(
    ("group", "delta"),
    [("plain", -1), ("plain", 1), ("trap", -1), ("trap", 1), ("evasion", -1), ("evasion", 1)],
)
def test_group_sizes_are_exact(tmp_path: Path, group: str, delta: int) -> None:
    """평범 100·함정 30·우회 20 은 정확히 그 수 — 하나 많거나 적으면 FAIL."""
    dev, test = _rows("dev"), _rows("test")
    want = vss.GROUP_SIZES[group]
    members = [r for r in dev if r["group"] == group and "교회 오빠" not in r["text"] and "정신과 선생님" not in r["text"]]
    if delta < 0:
        dev.remove(members[-1])
    else:
        extra = dict(members[-1])
        extra["id"] = "dev-999"
        extra["text"] = extra["text"] + " 추가"
        dev.append(extra)
    _, errors = _validate(tmp_path, dev, test)
    assert errors == [f"dev: {group} {want + delta}건 (기준 {want})"]


def test_missing_required_trap_phrase_fails(tmp_path: Path) -> None:
    """함정 30 에 호칭형 이름 "교회 오빠" 가 없으면 FAIL(01-plan U1)."""
    dev, test = _rows("dev"), _rows("test")
    _first(test, trap="honorific_name")["text"] = "test 호칭 바꾼 합성 함정"
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["test: 함정에 호칭형 이름 '교회 오빠' 없음"]


# ---------------------------------------------------------------- 묶음과 라벨


def test_plain_row_with_consent_label_fails(tmp_path: Path) -> None:
    """평범 줄에 consent 라벨 → FAIL(평범·함정은 none 이어야 한다)."""
    dev, test = _rows("dev"), _rows("test")
    _first(dev, group="plain")["label"] = "consent:crime"
    _, errors = _validate(tmp_path, dev, test)
    # 형식 오류 줄은 셈에서 빠지므로 평범 99 도 함께 FAIL 이다.
    assert errors == ["dev:166: group=plain 은 label none 이어야 함(지금 consent:crime)", "dev: plain 99건 (기준 100)"]


def test_sensitive_row_with_none_label_fails(tmp_path: Path) -> None:
    """sensitive 줄에 none → FAIL(감지를 재는 묶음)."""
    dev, test = _rows("dev"), _rows("test")
    _first(dev, group="sensitive")["label"] = "none"
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["dev:1: group=sensitive 은 label 이 none 이 아니어야 함", "dev: consent:crime 14건 (기준 15~20)"]


# ---------------------------------------------------------------- 지어낸 식별번호(R-12)


def test_valid_rrn_in_trap_row_fails(tmp_path: Path) -> None:
    """함정 줄에 검증 숫자가 맞는 주민등록번호 모양(한 덩어리) → FAIL."""
    dev, test = _rows("dev"), _rows("test")
    d = _rrn(77, valid=True)
    _first(dev, trap="keyword_lookalike")["text"] = f"dev 함정 합성 {d[:6]}-{d[6:]}"
    _, errors = _validate(tmp_path, dev, test)
    # 합성 세트의 첫 keyword_lookalike 함정은 268번째 줄(동의 75·가림 90·평범 100·호칭형 2 다음)이다.
    assert errors == ["dev:268:dev-268: 주민등록번호 모양의 검증 숫자가 맞음(실존 가능 — 끝 자리를 바꿀 것)"]


@pytest.mark.parametrize(("valid", "ok"), [(True, False), (False, True)])
def test_split_rrn_with_another_number(tmp_path: Path, valid: bool, ok: bool) -> None:
    """앞자리·뒷자리로 나눠 쓰고 문장에 다른 숫자가 있어도 주민등록번호 모양으로 본다
    (review-u1 변이 V09) — 검증 숫자가 맞으면 FAIL, 어긋나면 통과."""
    dev, test = _rows("dev"), _rows("test")
    d = _rrn(88, valid=valid)
    row = _first(dev, label="block:rrn")
    row["text"] = f"dev 합성 앞자리 {d[:6]} 뒷자리 {d[6:]} 학원 3층에 냈대"
    report, errors = _validate(tmp_path, dev, test)
    if ok:
        assert errors == []
    else:
        assert errors == ["dev:76:dev-076: 주민등록번호 모양의 검증 숫자가 맞음(실존 가능 — 끝 자리를 바꿀 것)"]
    # 나눠 쓴 번호도 주민등록번호 모양으로 세어진다(dev 15 + test 15 = 30).
    assert "주민등록번호 모양: 30건" in " ".join(report)


def test_rrn_split_into_word_separated_pieces_is_found(tmp_path: Path) -> None:
    """낱말로 세 토막 이상 나눠 쓴 번호도 문장에 다른 숫자가 없으면 문장 전체 숫자로
    주민등록번호 모양을 찾는다 — 검증 숫자가 맞으면 FAIL."""
    dev, test = _rows("dev"), _rows("test")
    d = _rrn(99, valid=True)
    _first(dev, label="block:rrn")["text"] = f"dev 합성 앞 {d[:6]} 성별 {d[6]} 나머지 {d[7:]}"
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["dev:76:dev-076: 주민등록번호 모양의 검증 숫자가 맞음(실존 가능 — 끝 자리를 바꿀 것)"]


def test_block_rrn_row_without_rrn_fails(tmp_path: Path) -> None:
    """block:rrn 줄에 주민등록번호 모양이 없으면 FAIL."""
    dev, test = _rows("dev"), _rows("test")
    _first(dev, label="block:rrn")["text"] = "dev 주민 합성 번호 없음"
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["dev:76:dev-076: block:rrn 인데 주민등록번호 모양 숫자가 없음"]


def test_luhn_valid_number_outside_public_list_fails(tmp_path: Path) -> None:
    """평범 줄에 공개 시험 번호 목록 밖의 Luhn 유효 16자리 → FAIL."""
    dev, test = _rows("dev"), _rows("test")
    number = _luhn_outside_list()
    assert number not in vss.PUBLIC_TEST_CARDS
    _first(dev, group="plain")["text"] = f"dev 평범 합성 {number}"
    _, errors = _validate(tmp_path, dev, test)
    assert errors == ["dev:166:dev-166: 공개 시험용 목록 밖 카드번호 모양 숫자(16자리)"]


def test_missing_input_file_returns_2(tmp_path: Path) -> None:
    """입력 파일이 없으면 종료 코드 2."""
    root = tmp_path / "empty"
    root.mkdir()
    assert vss.main([str(root)]) == 2
