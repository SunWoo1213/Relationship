"""Refs: P9d-sensitive-guard D20 S3.7 CR-009 원칙8 -- 민감 가드 시험 세트 형식 검사기.

`evaluation/sensitive_guard/{dev,test}.jsonl` 두 파일을 읽어 01-plan U1 의
수용 기준을 기계적으로 확인한다. 네트워크·DB·LLM 0, 표준 라이브러리만 쓴다.
판정하지 않고 세는 일만 한다 — 라벨이 맞는지는 verifier 검수(`review-u1.md`)가
본다(L-002, 만든 쪽이 검수하지 않는다).

사용::

    .venv/bin/python -I scripts/validate_sensitive_set.py evaluation/sensitive_guard/

검사(01-plan U1 수용 기준 · 빈자리 ⑧ · R-12):
  1. 형식 — 한 줄이 JSON 객체, 키는 `id`·`text`·`label`·`group`·`note`(필수)와
     `trap`·`form`(선택)뿐, 값은 비어 있지 않은 문자열. `id` 는 두 파일을 통틀어
     유일. `label` 은 `none` | `block:<유형 6>` | `consent:<범주 5>`, `group` 은
     `sensitive`|`plain`|`trap`|`evasion`. `trap` 은 `group=="trap"` 일 때만 있고
     그때는 반드시 있다. `form` 은 있으면 `"query"` 만.
  2. 묶음과 라벨의 정합 — `plain`·`trap` 은 `none`(오탐을 재는 묶음), `sensitive`·
     `evasion` 은 `none` 이 아님(감지를 재는 묶음).
  3. 크기(사용자 결정 12, 파일마다) — `group=="sensitive"` 만 범주·유형별로 세어
     11개 라벨 각각 15~20, `plain` 100 · `trap` 30 · `evasion` 20(우회는 범주
     셈에 들지 않는다). 동의 범주마다 `form=="query"` 가 1건 이상(빈자리 ⑧).
  4. 함정에 호칭형 이름 "교회 오빠"·"정신과 선생님" 이 파일마다 들어 있음.
  5. 문장 중복 0 — NFC·공백 정리 뒤 같은 문장이 한 파일 안이나 dev/test 사이에 없다.
  6. 지어낸 식별번호(R-12) — 주민등록번호 모양(13자리, 앞 6자리가 날짜 모양,
     7번째 1~8 — 한 덩어리든, 이웃한 6자리·7자리 두 덩어리든)은 끝 검증 숫자가
     **맞지 않아야** 한다. 13~19자리 숫자 중 Luhn 이
     맞는 것은 공개된 결제 시험용 번호 목록 안이어야 한다. `block:rrn` 줄에는
     주민등록번호 모양이, `block:card` 줄에는 목록 안 번호가 하나 이상 있어야 한다.

종료 코드: 0 = 오류 0, 1 = 오류 있음, 2 = 입력 파일을 찾지 못함.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# 저장소 루트를 sys.path 에 넣는다(scripts/tools_check.py:43 과 같은 방식 —
# `python -I` 로 실행해도 저장소 모듈을 import 할 수 있게. 지금은 import 0).
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

SPLITS: tuple[str, ...] = ("dev", "test")

#: 동의 범주 5종 — 순서는 D20·01-plan 의 고정 순서(D-1).
CATEGORIES: tuple[str, ...] = ("crime", "health", "sex", "politics_religion", "finance")

#: 가림(차단) 유형 6종 — 사용자 결정 6.
BLOCK_TYPES: tuple[str, ...] = ("rrn", "passport", "driver_license", "account", "card", "password")

SENSITIVE_LABELS: tuple[str, ...] = tuple(f"consent:{c}" for c in CATEGORIES) + tuple(
    f"block:{t}" for t in BLOCK_TYPES
)
LABELS: frozenset[str] = frozenset(("none",) + SENSITIVE_LABELS)

GROUPS: tuple[str, ...] = ("sensitive", "plain", "trap", "evasion")
NONE_GROUPS: frozenset[str] = frozenset({"plain", "trap"})

REQUIRED_KEYS: frozenset[str] = frozenset({"id", "text", "label", "group", "note"})
OPTIONAL_KEYS: frozenset[str] = frozenset({"trap", "form"})
FORM_VALUES: frozenset[str] = frozenset({"query"})

#: 사용자 결정 12 — 파일(dev·test)마다 이 크기.
PER_LABEL_MIN = 15
PER_LABEL_MAX = 20
GROUP_SIZES: dict[str, int] = {"plain": 100, "trap": 30, "evasion": 20}

#: 빈자리 ⑧ — 동의 범주마다 조회형 1건 이상.
QUERY_MIN_PER_CATEGORY = 1

#: 01-plan U1 — 함정 30 에 들어가야 하는 호칭형 이름.
REQUIRED_TRAP_PHRASES: tuple[str, ...] = ("교회 오빠", "정신과 선생님")

#: 공개된 결제 시험용 카드번호(결제 대행사 개발 문서에 실린 번호, Luhn 이 맞다).
#: R-12 — 카드번호 모양은 이 목록 안의 번호만 쓴다.
PUBLIC_TEST_CARDS: frozenset[str] = frozenset(
    {
        "4242424242424242",
        "4000056655665556",
        "4111111111111111",
        "4012888888881881",
        "5555555555554444",
        "2223003122003222",
        "5200828282828210",
        "5105105105105100",
        "378282246310005",
        "371449635398431",
        "6011111111111117",
        "6011000990139424",
        "3056930009020004",
        "36227206271667",
        "3566002020360505",
        "6200000000000005",
    }
)

#: 숫자 덩어리 — 숫자 사이에 공백·하이픈·마침표·빗금이 1~3자 끼어도 한 덩어리로 본다
#: (띄어 쓴 주민등록번호·구분자가 다른 카드번호를 놓치지 않게).
_DIGIT_RUN_RE = re.compile(r"\d+(?:[ \-./]{1,3}\d+)*")
_NON_DIGIT_RE = re.compile(r"\D")
_WS_RE = re.compile(r"\s+")

_RRN_WEIGHTS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5)
CARD_MIN_DIGITS = 13
CARD_MAX_DIGITS = 19


def normalize_text(text: str) -> str:
    """중복 판정용 정규화 — NFC 뒤 공백을 한 칸으로, 앞뒤 공백 제거."""
    return _WS_RE.sub(" ", unicodedata.normalize("NFC", text)).strip()


def digit_runs(text: str) -> list[str]:
    """문장 안 숫자 덩어리를 숫자만 남긴 문자열 목록으로."""
    return [_NON_DIGIT_RE.sub("", m.group(0)) for m in _DIGIT_RUN_RE.finditer(text)]


def is_rrn_shaped(digits: str) -> bool:
    """13자리, 앞 6자리가 YYMMDD 모양(월 01~12·일 01~31), 7번째가 1~8."""
    if len(digits) != 13 or not digits.isdigit():
        return False
    month, day = int(digits[2:4]), int(digits[4:6])
    return 1 <= month <= 12 and 1 <= day <= 31 and digits[6] in "12345678"


def rrn_check_digit(digits: str) -> int:
    """주민등록번호 끝 검증 숫자(앞 12자리 가중합 방식)."""
    total = sum(int(d) * w for d, w in zip(digits[:12], _RRN_WEIGHTS, strict=True))
    return (11 - total % 11) % 10


def rrn_check_matches(digits: str) -> bool:
    """끝 자리가 검증 숫자와 같으면 True(= 실존할 수 있는 모양 — 금지)."""
    return rrn_check_digit(digits) == int(digits[12])


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def rrn_candidates(text: str) -> list[str]:
    """주민등록번호 모양 후보 — 숫자 덩어리 + 이웃한 6자리·7자리 덩어리 쌍 +
    (낱말로 나눠 쓴 경우) 문장 전체 숫자.

    이웃 쌍(U1 재작업, review-u1 R-4 ①): "앞자리 NNNNNN 뒷자리 NNNNNNN" 처럼
    낱말로 나눠 쓴 번호는 문장에 다른 숫자가 하나라도 있으면 "문장 전체 숫자"
    가 13자리가 아니게 되어 검사를 빠져나갔다. R-12 는 주민등록번호 모양이면
    어디에 있든 검증 숫자가 맞지 않아야 한다고 하므로, 차례로 이웃한 두 덩어리가
    6자리·7자리이면 이어 붙여 함께 본다.
    """
    runs = digit_runs(text)
    found = [d for d in runs if is_rrn_shaped(d)]
    for front, back in zip(runs, runs[1:], strict=False):
        if len(front) == 6 and len(back) == 7:
            joined = front + back
            if is_rrn_shaped(joined) and joined not in found:
                found.append(joined)
    whole = _NON_DIGIT_RE.sub("", text)
    if is_rrn_shaped(whole) and whole not in found:
        found.append(whole)
    return found


def _check_row(row: object, where: str, errors: list[str]) -> dict[str, str] | None:
    """한 줄의 형식·정합 검사. 통과한 줄만 dict 로 돌려준다."""
    if not isinstance(row, dict):
        errors.append(f"{where}: JSON 객체가 아님")
        return None
    keys = set(row)
    missing = sorted(REQUIRED_KEYS - keys)
    unknown = sorted(keys - REQUIRED_KEYS - OPTIONAL_KEYS)
    if missing:
        errors.append(f"{where}: 필수 키 없음 {missing}")
    if unknown:
        errors.append(f"{where}: 모르는 키 {unknown}")
    ok = not missing and not unknown
    for key in keys & (REQUIRED_KEYS | OPTIONAL_KEYS):
        value = row[key]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{where}: {key} 가 비어 있지 않은 문자열이 아님")
            ok = False
    if not ok:
        return None
    label, group = row["label"], row["group"]
    if label not in LABELS:
        errors.append(f"{where}: 어휘 밖 label {label!r}")
        ok = False
    if group not in GROUPS:
        errors.append(f"{where}: 어휘 밖 group {group!r}")
        ok = False
    if "form" in row and row["form"] not in FORM_VALUES:
        errors.append(f"{where}: 어휘 밖 form {row['form']!r}")
        ok = False
    if group == "trap" and "trap" not in row:
        errors.append(f"{where}: group=trap 인데 trap 종류 없음")
        ok = False
    if group != "trap" and "trap" in row:
        errors.append(f"{where}: group={group} 인데 trap 키가 있음")
        ok = False
    if ok and group in NONE_GROUPS and label != "none":
        errors.append(f"{where}: group={group} 은 label none 이어야 함(지금 {label})")
        ok = False
    if ok and group not in NONE_GROUPS and label == "none":
        errors.append(f"{where}: group={group} 은 label 이 none 이 아니어야 함")
        ok = False
    return {k: str(v) for k, v in row.items()} if ok else None


def _check_ids(row: dict[str, str], where: str, text: str, label: str, errors: list[str], stats: Counter[str]) -> None:
    """지어낸 식별번호 검사(R-12)."""
    rrns = rrn_candidates(text)
    for d in rrns:
        stats["rrn_shaped"] += 1
        if rrn_check_matches(d):
            stats["rrn_check_match"] += 1
            errors.append(f"{where}: 주민등록번호 모양의 검증 숫자가 맞음(실존 가능 — 끝 자리를 바꿀 것)")
    if label == "block:rrn" and not rrns:
        errors.append(f"{where}: block:rrn 인데 주민등록번호 모양 숫자가 없음")
    card_hits = 0
    for d in digit_runs(text):
        if not (CARD_MIN_DIGITS <= len(d) <= CARD_MAX_DIGITS) or is_rrn_shaped(d):
            continue
        if d in PUBLIC_TEST_CARDS:
            stats["card_public_test"] += 1
            card_hits += 1
        elif label == "block:card" or luhn_ok(d):
            stats["card_outside_list"] += 1
            errors.append(f"{where}: 공개 시험용 목록 밖 카드번호 모양 숫자({len(d)}자리)")
    if label == "block:card" and card_hits == 0:
        errors.append(f"{where}: block:card 인데 공개 시험용 카드번호가 없음")


def validate(root: Path) -> tuple[list[str], list[str]]:
    """(보고 줄, 오류 줄) — 오류가 0 이면 통과."""
    report: list[str] = []
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_text: dict[str, str] = {}
    id_stats: Counter[str] = Counter()
    duplicate_count = 0
    #: 형식 오류(검사 1·2) — 따로 세어 "형식 오류: N" 으로 보고하고, 끝에 errors 에 합친다.
    format_errors: list[str] = []

    for split in SPLITS:
        path = root / f"{split}.jsonl"
        rows: list[dict[str, str]] = []
        lines = path.read_text(encoding="utf-8").split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        for lineno, line in enumerate(lines, start=1):
            where = f"{split}:{lineno}"
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                format_errors.append(f"{where}: JSON 해석 실패 ({exc.msg})")
                continue
            row = _check_row(raw, where, format_errors)
            if row is None:
                continue
            where = f"{split}:{lineno}:{row['id']}"
            if row["id"] in seen_ids:
                errors.append(f"{where}: id 중복(먼저 {seen_ids[row['id']]})")
            else:
                seen_ids[row["id"]] = where
            norm = normalize_text(row["text"])
            if norm in seen_text:
                duplicate_count += 1
                errors.append(f"{where}: 문장 중복(먼저 {seen_text[norm]})")
            else:
                seen_text[norm] = where
            _check_ids(row, where, row["text"], row["label"], errors, id_stats)
            rows.append(row)

        group_counts = Counter(r["group"] for r in rows)
        sensitive = [r for r in rows if r["group"] == "sensitive"]
        label_counts = Counter(r["label"] for r in sensitive)
        query_counts = Counter(r["label"] for r in sensitive if r.get("form") == "query")
        evasion_labels = Counter(r["label"] for r in rows if r["group"] == "evasion")
        trap_kinds = Counter(r["trap"] for r in rows if r["group"] == "trap")
        trap_texts = [r["text"] for r in rows if r["group"] == "trap"]

        report.append(f"[{split}] 유효한 줄 {len(rows)} / 전체 줄 {len(lines)}")
        report.append(f"  sensitive {group_counts['sensitive']} — 범주·유형별(group==sensitive 만, 기준 {PER_LABEL_MIN}~{PER_LABEL_MAX}):")
        for label in SENSITIVE_LABELS:
            n = label_counts[label]
            mark = "OK" if PER_LABEL_MIN <= n <= PER_LABEL_MAX else "FAIL"
            extra = ""
            if label.startswith("consent:"):
                q = query_counts[label]
                extra = f" · 조회형 {q}"
                if q < QUERY_MIN_PER_CATEGORY:
                    errors.append(f"{split}: {label} 조회형 {q}건 (기준 ≥ {QUERY_MIN_PER_CATEGORY})")
                    extra += " FAIL"
            report.append(f"    {label:<28} {n:>3} {mark}{extra}")
            if mark == "FAIL":
                errors.append(f"{split}: {label} {n}건 (기준 {PER_LABEL_MIN}~{PER_LABEL_MAX})")
        for group, want in GROUP_SIZES.items():
            n = group_counts[group]
            mark = "OK" if n == want else "FAIL"
            report.append(f"  {group:<9} {n:>3} (기준 {want}) {mark}")
            if mark == "FAIL":
                errors.append(f"{split}: {group} {n}건 (기준 {want})")
        report.append(f"  조회형 합계 — sensitive {sum(query_counts.values())} · plain {sum(1 for r in rows if r['group'] == 'plain' and r.get('form') == 'query')}")
        report.append("  우회 라벨 분포 — " + ", ".join(f"{k} {v}" for k, v in sorted(evasion_labels.items())))
        report.append("  함정 종류 — " + ", ".join(f"{k} {v}" for k, v in sorted(trap_kinds.items())))
        for phrase in REQUIRED_TRAP_PHRASES:
            hits = sum(1 for t in trap_texts if phrase in t)
            report.append(f"  함정 호칭형 이름 {phrase!r} {hits}건 {'OK' if hits else 'FAIL'}")
            if not hits:
                errors.append(f"{split}: 함정에 호칭형 이름 {phrase!r} 없음")

    report.append(f"형식 오류: {len(format_errors)}")
    errors[:0] = format_errors
    report.append(f"dev/test 문장 중복(한 파일 안 포함): {duplicate_count}")
    report.append(
        f"주민등록번호 모양: {id_stats['rrn_shaped']}건 · 검증 숫자 일치 {id_stats['rrn_check_match']}건(기준 0)"
    )
    report.append(
        f"카드번호 모양: 공개 시험 번호 {id_stats['card_public_test']}건 · 목록 밖 {id_stats['card_outside_list']}건(기준 0)"
    )
    return report, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="민감 가드 시험 세트 형식 검사(P9d U1)")
    parser.add_argument("root", type=Path, help="dev.jsonl·test.jsonl 이 있는 폴더")
    args = parser.parse_args(argv)
    root: Path = args.root
    missing = [s for s in SPLITS if not (root / f"{s}.jsonl").is_file()]
    if missing:
        print(f"입력 파일 없음: {', '.join(f'{s}.jsonl' for s in missing)} ({root})")
        return 2
    report, errors = validate(root)
    for line in report:
        print(line)
    print(f"오류: {len(errors)}")
    for line in errors:
        print(f"  [ERROR] {line}")
    print("결과: PASS" if not errors else "결과: FAIL")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
