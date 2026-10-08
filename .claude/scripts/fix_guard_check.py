#!/usr/bin/env python
"""FIX-027 — 제품 코드를 바꾸는 FIX 커밋에 verifier 검증을 강제한다.

`commit-guard.sh` 가 git commit 을 허용하기 직전에 이 스크립트를 호출한다.
순수 함수가 아니라 git·파일시스템을 읽는 판정기이므로, 판단에 필요한
정보를 하나라도 구하지 못하면(= 판단 불가) **통과가 아니라 거부**로
끝낸다(fail-closed, `_py.sh` 가 명시하는 차단형 가드의 원칙).

쓰는 법:
    python fix_guard_check.py <project_root> <draft_path>
    종료 코드 0 : 이 규칙이 해당 없음(FIX 패턴 아님 · 제품 코드 무변경) 또는 통과
    종료 코드 1 : 무엇이 빠졌는지 stdout 에 적고 거부
    종료 코드 2 : 판단 불가(인자 부족·git 실패) 또는 예기치 않은 예외 — 역시 거부

무엇을 보는가:
    1. 커밋 초안(`commit-draft.txt`)의 **첫 번째 비어 있지 않은 줄**(선행 BOM 제거,
       git 이 선행 빈 줄을 건너뛰는 것과 같은 규칙, R-27-1)에 `FIX-nnn` 이 있는가.
       형태(유형·괄호·구두점)는 따지지 않는다(R-27-7) — 제목 줄 안에 FIX 번호가 있으면
       전부 대상이다. 없으면 이 규칙은 해당 없음(0).
       본문의 `Refs: FIX-nnn` 만 있고 제목에 없는 경우는 **대상 밖**으로 둔다(정책,
       아래 `_extract_fix_ids` docstring 참조).
    2. `git diff --cached --name-only` 에 `app/` 또는 `alembic/` 로 시작하는
       경로가 있는가. 없으면(문서·훅만 바꾼 FIX) 해당 없음(0).
    3. 있으면 제목에서 찾은 **모든** FIX 번호 각각에 대해:
       a. `docs/wiki/fixes/FIX-nnn.md` 에 `검증:` 줄이 **정확히 하나**이고 그 줄이
          `검증: 통과 — verifier …`(구분자 바로 뒤 verifier, 부정·유보 표현 없음)인가
          (F-27-4·F-27-6). 템플릿 자리표(`검증: (verifier 가 쓴다 …)`)는 "통과" 가 없어
          이미 걸린다.
       b. `docs/wiki/fixes/review-FIX-nnn.md` 가 R-27-3 기준을 만족하는가: 디스크에
          존재하고 0바이트가 아니며, `검토자:` 줄에 "verifier" 가 있고, git 색인에
          추적돼 있다(스테이징됐거나 이미 HEAD 에 커밋됨 — 디스크에만 있는 추적 안 된
          파일은 커밋 이력에 증거가 남지 않으므로 거부).
    어느 FIX 번호든 a·b 중 하나라도 빠지면 거부(1), 전부 있으면 통과(0).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# R-27-7: 제목 한 줄 안에 `FIX-nnn` 이 있으면 형태와 무관하게(`fix(FIX-999 재작업)`·
# `fix[FIX-999]`·`fix: FIX-999`·`fix-hooks(FIX-999)` …) 전부 규칙 대상이다. 제목에 FIX 번호를
# 적고 app/ 를 바꾸는 커밋은 전부 FIX 커밋으로 본다. 대소문자 무시, `FIX-27`→027 정규화,
# 복수 ID 는 전부 검사(R-27-1 유지).
ID_RE = re.compile(r"fix-0*(\d+)", re.IGNORECASE)
# F-27-6: `검증:` 줄 = 구분자(— – -) 바로 뒤에 verifier. 통과 판정 줄에 부정·유보 표현이 있으면 거부.
VERDICT_RE = re.compile(r"^검증:\s*통과\s*[—–-]+\s*verifier\b", re.IGNORECASE)
NEGATION_RE = re.compile(r"생략|아직|예정|아님|않|못|미실시|제외|대신")


def _first_nonblank_line(text: str) -> str:
    """BOM 제거 후 첫 '비어 있지 않은' 줄을 돌려준다(R-27-1).

    git 은 커밋 메시지 제목을 만들 때 선행 빈 줄을 건너뛴다 — 초안 파일의 실제 제목이
    사람 기준 2번째 줄일 수 있다. 이 함수가 그 규칙을 흉내 낸다. UTF-8 BOM(`\\ufeff`)이
    파일 맨 앞에 붙어 있어도 유형 글자로 오인하지 않도록 먼저 벗긴다.
    """
    cleaned = text.lstrip("﻿")
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return ""


def _extract_fix_ids(first_line: str) -> list[int] | None:
    """제목에서 FIX 번호 목록을 뽑는다. 패턴이 아예 아니면 None(= 규칙 대상 밖).

    복수 ID 정책(R-27-1): `fix(FIX-999, FIX-998)` 처럼 제목에 여러 개가 있으면 **전부**
    검사 대상이다 — 하나라도 검증·리뷰가 없으면 거부한다.

    본문 Refs 전용 정책: `Refs: FIX-nnn` 이 본문에만 있고 제목이 `<유형>(FIX-nnn)` 형식이
    아니면(예: `fix(P7-push): 본문에만 FIX` 처럼 제목이 패키지 id 를 가리키는 경우) 이
    규칙의 대상이 **아니다**. 커밋 본문 전체에서 `FIX-\\d+` 문자열을 찾는 식으로 넓히면
    무관한 언급(예: "참고: FIX-010 과 같은 문제")에도 반응해 과도하게 넓어진다. 패키지
    작업은 이미 `02-plan-verify.md`/`04-review.md` 로 verifier 게이트가 따로 있으므로,
    제목에 FIX-nnn 을 **명시**한 커밋만 이 규칙의 대상으로 좁힌다.
    """
    ids = sorted({int(n) for n in ID_RE.findall(first_line)})
    return ids or None


def _verification_line_ok(fix_doc: Path) -> bool:
    """FIX-nnn.md 의 `검증:` 줄에 verifier 의 "통과" 판정이 실제로 있는지 본다(F-27-4).

    "통과" 와 "verifier" 가 **둘 다** 있어야 한다. 하나만으로는 부족하다:
      - `검증: 보류 — verifier (fable) …` → "통과" 없음 → 거부(verifier 의 보류 판정이
        게이트를 열지 못해야 한다).
      - `검증: 통과 — 메인 세션` → "verifier" 없음 → 거부(L-002 — 메인 세션이 쓴 통과는
        유효하지 않다).
    인코딩 오류(UTF-8 이 아닌 FIX 문서)는 "검증 없음" 으로 취급해 거부 목록에 들어간다
    (F-27-2) — 외부의 포괄 예외 처리기까지 가지 않고 여기서 바로 깔끔한 사유로 끝난다.
    """
    try:
        text = fix_doc.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    verdict_lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("검증:")]
    # F-27-6 ②: 문서에는 `검증:` 줄이 정확히 하나여야 한다. 둘 이상이면(자리표 + `## 결과` 의
    # 통과 줄, 보류 줄 뒤에 남은 옛 통과 줄 …) 어느 것이 최신 판정인지 기계가 알 수 없으므로 거부.
    if len(verdict_lines) != 1:
        return False
    line = verdict_lines[0]
    # F-27-6 ①: 구분자 바로 뒤 verifier. ③: "통과 — verifier 리뷰 생략(문서만)" 같은 부정·유보
    # 표현이 같은 줄에 있으면 통과 판정이 아니므로 거부한다(진짜 판정 줄은 이런 단어를 쓰지 않는다).
    return bool(VERDICT_RE.match(line)) and not NEGATION_RE.search(line)


def _review_doc_ok(root: Path, review_doc: Path) -> bool:
    """review-FIX-nnn.md 가 R-27-3 기준을 만족하는지 본다.

    기준: (1) 디스크에 존재하고 0바이트가 아니다, (2) `검토자:` 줄에 "verifier" 가
    있다, (3) git 색인에 추적돼 있다(스테이징됐거나 이미 HEAD 에 커밋됨). 디스크에만
    있는 추적 안 된(untracked) 파일은 이 커밋 이력에 증거로 남지 않으므로 거부한다 —
    이전 버전은 디스크 존재만 봐서 0바이트 빈 파일·untracked 파일도 통과시켰다.
    """
    try:
        if not review_doc.is_file() or review_doc.stat().st_size == 0:
            return False
        text = review_doc.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    if not any(
        re.match(r"^검토자:.*verifier", line.strip(), re.IGNORECASE) for line in text.splitlines()
    ):
        return False
    try:
        rel = review_doc.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return False
    try:
        subprocess.run(
            ["git", "ls-files", "--cached", "--error-unmatch", rel],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def _main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("[fix-guard] 사용법: fix_guard_check.py <project_root> <draft_path>")
        return 2

    root = Path(argv[1])
    draft_path = Path(argv[2])

    try:
        draft_text = draft_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[fix-guard] 커밋 초안을 읽을 수 없다: {e}")
        return 2

    first_line = _first_nonblank_line(draft_text)
    ids = _extract_fix_ids(first_line)
    if ids is None:
        return 0  # 제목에 <유형>(FIX-nnn) 형식이 없으면 이 규칙은 해당 없음

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"[fix-guard] 스테이징된 파일 목록을 확인할 수 없다(git diff 실패): {e}")
        return 2

    # git diff --name-only 는 OS 와 무관하게 슬래시(/)로 경로를 낸다.
    # 혹시 모를 역슬래시 혼입(예: 외부 도구가 끼어든 경우)까지 정규화한다.
    staged = [p.strip().replace("\\", "/") for p in result.stdout.splitlines() if p.strip()]
    touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") for p in staged)
    if not touches_product_code:
        return 0  # 문서·훅만 바꾼 FIX 는 이 규칙 대상이 아니다

    missing: list[str] = []
    for n in ids:
        nnn = f"{n:03d}"
        fix_doc = root / "docs" / "wiki" / "fixes" / f"FIX-{nnn}.md"
        review_doc = root / "docs" / "wiki" / "fixes" / f"review-FIX-{nnn}.md"
        if not _verification_line_ok(fix_doc):
            missing.append(
                f"docs/wiki/fixes/FIX-{nnn}.md 의 `검증:` 줄에 verifier 의 '통과' 판정이 없다"
                "(자리표만 있거나, '통과'·'verifier' 중 하나가 빠졌거나, 파일이 없다)"
            )
        if not _review_doc_ok(root, review_doc):
            missing.append(
                f"docs/wiki/fixes/review-FIX-{nnn}.md (verifier 커밋 전 리뷰 문서)가 없거나 "
                "기준(0바이트 아님·검토자: verifier·git 추적)을 충족하지 않는다"
            )

    if missing:
        nnn_list = ", ".join(f"FIX-{n:03d}" for n in ids)
        print(
            "[fix-guard] 제품 코드(app/·alembic/)를 바꾸는 {0} 커밋은 verifier 검증이 "
            "먼저다: {1}. .claude/skills/devlog/SKILL.md 의 `/devlog fix` 절차대로 "
            "구현 에이전트 작업 → verifier 리뷰(review-FIX-nnn.md) → 검증 줄을 받은 뒤 "
            "다시 커밋하라.".format(nnn_list, "; ".join(missing))
        )
        return 1

    return 0


def main(argv: list[str]) -> int:
    """`_main` 이 예상 밖의 예외를 내면(파일 인코딩 오류·git 환경 문제 등) 한 줄 메시지로
    거부한다(F-27-2).

    이전 버전은 `_verification_line_ok` 안의 `UnicodeDecodeError`(`OSError` 가 아니라
    `ValueError` 계열이라 거기서 잡히지 않았다)가 여러 줄 Traceback 으로 그대로
    `commit-guard.sh` 의 `deny()` 에 들어가 깨진 JSON 을 냈다 — 거부하려 했으나 실제로는
    통과(fail-open)됐다. 지금은 그 지점을 `_verification_line_ok`·`_review_doc_ok` 안에서
    직접 잡아 깔끔한 거부 사유로 바꿨지만(1차 방어), 예기치 못한 다른 예외까지 전부
    잡는 이 바깥 쪽 포괄 처리가 2차 방어다 — 판단 불가는 항상 거부(rc=2)이고, 메시지는
    줄바꿈 없는 한 줄로 접어 `commit-guard.sh`(이제 `deny()` 자체도 `json.dumps` 를 써서
    줄바꿈이 섞여도 안전하지만) 쪽 가독성도 지킨다.
    """
    try:
        return _main(argv)
    except Exception as e:  # noqa: BLE001 - 판단 불가는 전부 거부한다(fail-closed)
        msg = f"{e.__class__.__name__}: {e}".replace("\n", " ").replace("\r", " ")
        print(f"[fix-guard] 판단 중 예기치 않은 오류 — 거부: {msg[:300]}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
