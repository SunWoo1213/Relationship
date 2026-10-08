#!/usr/bin/env python
"""FIX-027 F-27-5 — `git commit` 인자 허용 목록 검사.

`commit-guard.sh` 가 명령에서 git commit 을 감지하면 stdin 으로 명령 전체를 넘겨
이 스크립트를 호출한다. `git commit` 뒤에 올 수 있는 인자는 **오직**
    -F <초안>  /  --file=<초안>  /  --file <초안>
뿐이다(<초안> = `.claude/commit-draft.txt`, 따옴표 유무 무관).

왜 허용 목록인가: 규칙 6(제품 코드 verifier 게이트)은 `git diff --cached` 만 본다.
`-a/--all/-i/--include/-o/--only`, 경로(pathspec, 옵션 앞뒤 어디든), `--` 뒤 경로,
`--pathspec-from-file`·`--pathspec-file-nul` 은 `git add` 없이 커밋 대상을 늘려 그
검사를 거짓 통과시킨다. 이 우회는 "막을 것을 나열" 하는 방식으로는 형태가 계속
새로 나오므로(1차 재작업은 `-F` 뒤만 막아 `--file=`·`-F` 앞 경로가 열렸다) "허용할
것만 나열" 하고 나머지는 전부 거부한다. `-am`·`-aF` 같은 조합 단축 플래그도
허용 목록에 없으므로 자연히 거부된다.

종료 코드: 0 = 통과, 1 = 거부(사유를 stdout 에 한 줄로 출력).
판단 불가(따옴표 불일치 등)도 거부 — fail-closed.
"""

from __future__ import annotations

import re
import shlex
import sys

DRAFT_REL = ".claude/commit-draft.txt"

# git 전역 옵션 중 값을 다음 토큰으로 받는 것(`--opt=값` 형태는 한 토큰이라 해당 없음)
_GLOBAL_OPTS_WITH_VALUE = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
_SEP_CHARS = set(";&|()")


def _tokenize(cmd: str) -> list[str]:
    # 개행은 명령 구분자다. shlex 는 개행을 공백으로 먹으므로 먼저 `;` 로 바꾼다.
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def _is_punct(tok: str) -> bool:
    return bool(tok) and all(c in ";&|()<>" for c in tok)


def check(cmd: str) -> str | None:
    """거부 사유를 돌려준다. 통과면 None."""
    try:
        toks = _tokenize(cmd)
    except ValueError as e:
        return f"명령을 해석할 수 없다({e}) — 커밋 인자를 검사할 수 없어 거부한다."

    found = 0
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        if t.rsplit("/", 1)[-1] != "git":
            i += 1
            continue
        # git 전역 옵션을 건너뛰고 서브커맨드가 commit 인지 본다
        j = i + 1
        while j < n and toks[j].startswith("-"):
            opt = toks[j]
            j += 2 if opt in _GLOBAL_OPTS_WITH_VALUE else 1
        if j >= n or toks[j] != "commit":
            i += 1
            continue
        found += 1
        j += 1
        saw_draft = False
        while j < n:
            a = toks[j]
            if _is_punct(a):
                if set(a) <= _SEP_CHARS:
                    break  # 명령 끝(; && | 등)
                j += 2  # 리다이렉션(`> file`, `2>&1` 의 `>&`) — 연산자와 대상은 건너뜀
                continue
            if j + 1 < n and re.fullmatch(r"\d+", a) and _is_punct(toks[j + 1]) and not (set(toks[j + 1]) <= _SEP_CHARS):
                j += 1  # `2>&1` 앞의 파일 디스크립터 숫자
                continue
            if a == "-F" or a == "--file":
                if j + 1 < n and toks[j + 1] == DRAFT_REL:
                    saw_draft = True
                    j += 2
                    continue
                return f"-F/--file 의 값은 {DRAFT_REL} 여야 한다."
            if a == f"--file={DRAFT_REL}":
                saw_draft = True
                j += 1
                continue
            return (
                f"git commit 인자 '{a}' 는 허용되지 않는다. 허용: -F {DRAFT_REL} (또는 --file=…/--file …) 만. "
                "커밋 대상은 git add 로 스테이징한 것으로만 정한다 — "
                "경로(pathspec)·--pathspec-from-file·-a/--all/-i/--include/-o/--only·-- 는 쓸 수 없다."
            )
        if not saw_draft:
            return f"커밋 메시지는 승인된 초안 파일로만 전달한다: git commit -F {DRAFT_REL}"
        i = j
    if found == 0:
        return "git commit 호출을 해석하지 못했다(따옴표·bash -c 등 안에 감춰진 형태) — 거부한다."
    return None


def main() -> int:
    cmd = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    reason = check(cmd)
    if reason:
        print(reason)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
