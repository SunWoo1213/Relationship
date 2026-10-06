"""Refs: FIX-021 원칙8 -- mypy 오류를 "새 오류만" 실패시키는 기준선 비교.

`app/` 의 SQLAlchemy 모델 열이 대부분 `object` 로 추론되는 연쇄 오류
(결과절 참고)가 많아, 전부 해결하기 전에는 `mypy app` 종료 코드를 그대로
CI 게이트로 쓸 수 없다(모든 PR 이 기존 오류 때문에 항상 실패한다). 그렇다고
mypy 단계를 통째로 건너뛰면(skip=실패 규칙, FIX-007) 새로 생기는 결함을
놓친다. 그래서 알려진 오류 목록(`scripts/mypy_baseline.txt`)과 비교해
**새 오류만** 실패로 본다.

사용::

    python -m mypy app --ignore-missing-imports | python scripts/mypy_check.py
    python scripts/mypy_check.py --run                 # mypy 를 직접 실행(위와 동등)
    python scripts/mypy_check.py --run --update-baseline  # 기준선 재생성(사람이 검토 후 커밋)

동작:
  1. mypy 출력에서 `파일:줄: error: 메시지  [코드]` 줄만 뽑는다(`note:` 줄·
     요약 줄은 무시 -- 코드가 없어 비교 대상이 아니다).
  2. 줄 번호를 지우고 경로 구분자를 `/` 로 통일해 `파일: [코드] 메시지`
     로 정규화한다(Mac 과 Windows 모두, 코드 리팩터로 줄 번호만 바뀌는
     잡음을 피한다).
  3. 기준선과 다중집합(Counter)으로 비교한다 -- 같은 모양의 오류가 기준선
     보다 더 많이 나오면(중복 포함) 새 오류로 본다.
  4. 기준선에는 있지만 이번엔 없는 항목은 "사라짐" 으로만 알리고 실패시키지
     않는다(오류가 고쳐진 것은 환영할 일이지, 기준선을 당장 바꾸라고
     요구하지 않는다 -- `--update-baseline` 으로 사람이 검토 후 반영).

종료 코드:
    0 = 새 오류 없음(기준선에 없던 항목이 없다)
    1 = 새 오류 있음(아래 "[new]" 로 출력)
    2 = mypy 실행 자체가 실패(설치 문제 등, `--run` 모드에서만 해당)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "scripts" / "mypy_baseline.txt"

# `파일:줄: error: 메시지  [코드]` -- note: 줄·요약 줄("Found N errors...")은
# 여기 안 걸린다(일부러).
_ERROR_LINE = re.compile(r"^(?P<file>.+?):(?P<line>\d+): error: (?P<message>.+?)\s*\[(?P<code>[\w-]+)\]\s*$")


def normalize(mypy_output: str) -> list[str]:
    """mypy stdout 전체를 받아 정규화된 오류 줄 목록을 돌려준다(줄번호 제외,
    경로 구분자 `/` 통일). 순서는 mypy 출력 순서 그대로 보존한다(기준선
    파일을 diff 로 읽기 쉽게 하려면 호출자가 정렬한다)."""

    entries: list[str] = []
    for line in mypy_output.splitlines():
        m = _ERROR_LINE.match(line)
        if not m:
            continue
        file_path = m.group("file").replace("\\", "/")
        entries.append(f"{file_path}: [{m.group('code')}] {m.group('message')}")
    return entries


def load_baseline(path: Path = BASELINE_PATH) -> list[str]:
    if not path.is_file():
        return []
    lines = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def write_baseline(entries: list[str], path: Path = BASELINE_PATH) -> None:
    header = (
        "# Refs: FIX-021 -- mypy app --ignore-missing-imports 기준선.\n"
        "# scripts/mypy_check.py 가 생성·비교한다. 줄 번호는 없다(리팩터로\n"
        "# 흔들리는 잡음을 피하려고 정규화). 사람이 검토하고 커밋한 목록만\n"
        "# '알려진 오류' 로 인정한다 -- --update-baseline 출력을 그대로\n"
        "# 커밋하지 않는다(새로 생긴 진짜 결함을 조용히 기준선에 넣는 것을\n"
        "# 막기 위함, 원칙8).\n"
    )
    body = "\n".join(sorted(entries))
    path.write_text(header + body + ("\n" if body else ""), encoding="utf-8")


def compare(current: list[str], baseline: list[str]) -> tuple[Counter, Counter]:
    """(새_오류, 사라진_오류) -- 둘 다 Counter, 다중집합 차집합.

    같은 모양의 오류가 기준선보다 더 많이 나타나면 그 초과분만 "새 오류"다
    (예: 기준선에 같은 메시지가 2개면 3개째부터 새 오류)."""

    current_counts = Counter(current)
    baseline_counts = Counter(baseline)
    new = current_counts - baseline_counts
    gone = baseline_counts - current_counts
    return new, gone


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="store_true",
        help="mypy app --ignore-missing-imports 를 직접 실행해 그 출력을 비교한다"
        "(기본은 stdin 에서 mypy 출력을 읽는다)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="비교 대신 scripts/mypy_baseline.txt 를 지금 결과로 덮어쓴다"
        "(사람이 diff 를 보고 커밋할 것 -- CI 에서 쓰지 않는다)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.run:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", "app", "--ignore-missing-imports"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        mypy_output = proc.stdout
        if proc.returncode not in (0, 1):
            print(proc.stdout, file=sys.stdout)
            print(proc.stderr, file=sys.stderr)
            print(f"[error] mypy 실행 자체가 실패했다(종료 코드 {proc.returncode})", file=sys.stderr)
            return 2
    else:
        mypy_output = sys.stdin.read()

    current = normalize(mypy_output)

    if args.update_baseline:
        write_baseline(current)
        print(f"[ok] {BASELINE_PATH.as_posix()} 를 {len(current)}건으로 갱신했다 -- diff 를 검토하고 커밋할 것")
        return 0

    baseline = load_baseline()
    new, gone = compare(current, baseline)

    if gone:
        print("[info] 기준선에 있었지만 이번엔 없는 오류(알림만, 실패 아님):")
        for entry, count in sorted(gone.items()):
            print(f"  - {entry} (x{count})")

    if new:
        print("[new] 기준선에 없는 새 오류:")
        for entry, count in sorted(new.items()):
            print(f"  + {entry} (x{count})")
        print(f"\n[FAIL] 새 오류 {sum(new.values())}건 -- scripts/mypy_baseline.txt 와 비교해 결함이면 고치고,")
        print("기준선에 넣을 것이면 --update-baseline 로 재생성 후 사람이 검토하고 커밋한다.")
        return 1

    print(f"[ok] 새 오류 없음 (현재 {len(current)}건, 기준선 {len(baseline)}건)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
