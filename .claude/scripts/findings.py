#!/usr/bin/env python
"""findings.py — 검증 출력 → 조치 계획 문서(05-remediation.md) 동기화

사용:
  python .claude/scripts/findings.py <패키지 id> <검증 출력 파일> [--source verify-plan|verify-impl|pytest|eval|review]
  python .claude/scripts/findings.py <패키지 id> --list

동작:
  * 입력에서 `FAIL  ...`, `WARN  ...`, pytest 의 `FAILED ...`/`ERROR ...` 줄을 소견(finding)으로 뽑는다.
  * 소견 ID = F-<메시지 정규화 md5 앞 6자>. 같은 문제는 재실행해도 같은 ID → 진행 상태가 유지된다.
  * docs/wiki/packages/<id>/05-remediation.md 를 만들거나 갱신한다.
      - 새 소견: 템플릿 절(증상·원인 분석·해결 단계·재검증·영향 확인)을 추가한다. 에이전트가 채운다.
      - 기존 소견: 본문·상태를 그대로 둔다.
      - 같은 --source 의 이전 소견이 이번 출력에 없으면 `상태: 해소 (날짜)` 로 바꾼다.
  * 종료 코드: 열린 [필수](FAIL) 소견이 있으면 1, 없으면 0.

이 스크립트는 "검증했더니 문제가 있었다"를 "무엇을 어떤 순서로 고치고 무엇으로 확인하는가"로 강제 변환하는 장치다.
원칙8(실패도 결과다): 소견을 지우지 않는다. 해소만 한다.
"""
import hashlib
import io
import os
import re
import sys
from datetime import datetime

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WIKI = os.path.join(ROOT, "docs", "wiki")

LINE_RE = re.compile(r"^(FAIL|WARN)\s+(.*\S)\s*$")
PYTEST_RE = re.compile(r"^(FAILED|ERROR)\s+(\S.*?)(\s+-\s+.*)?$")
HEAD_RE = re.compile(r"^## (F-[0-9a-f]{6}) · \[(필수|권고)\] (.*)$")


def norm(msg: str) -> str:
    # 시각·해시·숫자 변동을 지워 안정적인 ID 를 만든다
    m = re.sub(r"\d{8}-\d{4}", "<ts>", msg)
    m = re.sub(r"\b[0-9a-f]{7,40}\b", "<hash>", m)
    m = re.sub(r"\d+", "<n>", m)
    return re.sub(r"\s+", " ", m).strip().lower()


def fid(msg: str) -> str:
    return "F-" + hashlib.md5(norm(msg).encode("utf-8")).hexdigest()[:6]


def parse(text: str):
    out = []
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if m:
            sev = "필수" if m.group(1) == "FAIL" else "권고"
            out.append((sev, m.group(2), line.rstrip()))
            continue
        m = PYTEST_RE.match(line)
        if m:
            out.append(("필수", f"{m.group(1)} {m.group(2)}", line.rstrip()))
    return out


def block(fid_, sev, msg, raw, source, pkg, today):
    return f"""## {fid_} · [{sev}] {msg}
상태: 열림 | 발견: {today} ({source}) | 해소: -

### 증상 (검증 출력 인용)
```
{raw}
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh {pkg}` (계획 단계면 `verify-plan.sh {pkg}`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

"""


def split_blocks(text: str):
    """헤더 부분과 {id: block_text} 로 나눈다. 블록 순서는 리스트로 보존."""
    lines = text.splitlines(keepends=True)
    header, blocks, order = [], {}, []
    cur = None
    for ln in lines:
        m = HEAD_RE.match(ln.rstrip("\n"))
        if m:
            cur = m.group(1)
            order.append(cur)
            blocks[cur] = ln
        elif cur:
            blocks[cur] += ln
        else:
            header.append(ln)
    return "".join(header), blocks, order


def status_of(b: str):
    m = re.search(r"^상태:\s*(\S+)", b, re.M)
    return m.group(1) if m else ""


def source_of(b: str):
    m = re.search(r"발견:\s*\d{4}-\d{2}-\d{2}\s*\(([^)]*)\)", b)
    return m.group(1) if m else ""


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    pkg = argv[0]
    pdir = os.path.join(WIKI, "packages", pkg)
    if not os.path.isdir(pdir):
        print(f"FAIL  패키지 폴더 없음: {pdir}")
        return 2
    path = os.path.join(pdir, "05-remediation.md")
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    existing = io.open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    header, blocks, order = split_blocks(existing)

    if argv[1] == "--list":
        for i in order:
            print(i, status_of(blocks[i]), blocks[i].splitlines()[0][len(i) + 4:])
        return 0

    src_file = argv[1]
    source = "verify"
    if "--source" in argv:
        source = argv[argv.index("--source") + 1]
    text = io.open(src_file, encoding="utf-8", errors="replace").read()
    found = parse(text)

    seen = set()
    added = []
    for sev, msg, raw in found:
        i = fid(msg)
        if i in seen:
            continue
        seen.add(i)
        if i not in blocks:
            blocks[i] = block(i, sev, msg, raw, source, pkg, today)
            order.append(i)
            added.append(i)

    closed = []
    for i in order:
        b = blocks[i]
        if i not in seen and status_of(b) == "열림" and source_of(b) == source:
            b = re.sub(r"^상태:\s*열림", f"상태: 해소", b, count=1, flags=re.M)
            b = re.sub(r"\|\s*해소:\s*-", f"| 해소: {today}", b, count=1)
            blocks[i] = b
            closed.append(i)

    open_all = [i for i in order if status_of(blocks[i]) == "열림"]
    open_must = [i for i in open_all if "[필수]" in blocks[i].splitlines()[0]]

    head = (
        f"# {pkg} · 검증 결과 조치 계획 (05-remediation)\n\n"
        f"> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, "
        f"해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).\n"
        f"> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.\n\n"
        f"갱신: {now} | 출처: {source} | 열림: {len(open_all)} (필수 {len(open_must)}) | 해소: {len(order) - len(open_all)}\n\n"
    )
    body = "".join(blocks[i] if blocks[i].endswith("\n") else blocks[i] + "\n" for i in order)
    io.open(path, "w", encoding="utf-8", newline="\n").write(head + body)

    print(f"05-remediation.md 갱신: 새 소견 {len(added)}, 해소 {len(closed)}, 열림 {len(open_all)} (필수 {len(open_must)})")
    for i in added:
        print(f"  + {i}  {blocks[i].splitlines()[0][len(i) + 4:]}")
    for i in closed:
        print(f"  ✓ {i}  해소")
    return 1 if open_must else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
