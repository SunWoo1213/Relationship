#!/usr/bin/env python
"""FIX-014 — Bash/PowerShell 명령의 "프로젝트 안 파일 쓰기" 판정 + 실제 git 조각 추출.

두 가지 일을 한다(둘 다 "훅이 행위를 적은 문자열이 아니라 행위를 본다"는 한 뿌리다).

1. 기본 모드 (`bash-write-guard.sh` 가 호출)
   stdin: {"tool_name":"Bash"|"PowerShell","tool_input":{"command":"..."}}
   명령을 셸 구조(따옴표·`;`·`&&`·`||`·`|`·줄바꿈·heredoc·명령 치환)대로 쪼갠 뒤 **쓰기 형태**
   (`>`/`>>`·`tee`·`sed -i`·`cp`/`mv`/`install`/`ln` 목적지·`touch`·`truncate`·`dd of=`·
   python/node 인라인 코드의 파일 쓰기·PowerShell `Set-Content` 류)를 찾아 대상 경로를 판정한다.
     - 임시 영역(`/tmp`·`$TMPDIR`·스크래치패드·`/dev/null`) → 허용
     - 프로젝트 안(상대 경로 포함) → 거부 ("Write/Edit 툴로 고쳐라": stage-gate·secret-guard 를 거치도록)
     - 경로를 판정할 수 없음(변수·명령 치환) → 거부 (security.md "검사할 수 없으면 통과가 아니라 차단")
   종료 코드: 0 = 통과(출력 없음), 1 = 거부(사유를 stdout 에 출력).

2. `--git-fragments` 모드 (`commit-cleanup.sh` 가 호출, 결함 ②)
   같은 구조 분해로 "실행되는 명령의 첫 단어가 git 인 조각"만 한 줄씩 출력한다.
   다른 명령의 인자 속 `git push origin dev2` 같은 글자는 실행되는 명령이 아니므로 나오지 않는다.

재작업(R-14-1~3): 인자 없는 셸이 stdin(파이프·here-string·`< 파일`)으로 받는 코드는 리터럴이면 재귀 분석하고
아니면 거부한다. python/node/perl/ruby 의 `-c`/`-e` 인자가 동적(`$(…)`·변수)이면 거부한다.
`find … -exec|-execdir|-ok|-okdir <명령> {} ;|+` 의 명령은 `{}` 를 find 시작 경로로 바꿔 같은 판정에 태운다.

2차 재작업(R-14-12~14): `xargs -I{}` 자리표가 코드 자리(`bash -c {}`·`python3 -c {}`)에 오면 코드는 파이프 입력에서 온 것이라
리터럴이면 치환해 분석하고 아니면 거부한다. 따옴표 없는 heredoc 본문의 `$(…)`·백틱은 바깥 셸이 실행하므로 재귀 분석하고,
`$VAR`·`$(…)` 가 있는 본문이 셸의 stdin 코드면 거부한다. node/ruby/perl/php 가 stdin 으로 받는 코드도 python 과 같은 규칙으로 본다.

한계(수정안 5, 의도): 파일을 쓰는 **프로그램을 실행**하는 것(pytest·pip·npm·alembic·`python x.py`·
`bash x.sh`·git 하위 명령 등)은 막지 않는다. 쓰기 문법이 아니라 도구의 정상 부작용이다.
표준 라이브러리만 쓴다(훅 인터프리터 탐지 FIX-008). Mac·Windows 공통.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field

MAX_DEPTH = 6


class Deny(Exception):
    """거부 사유를 담아 판정을 즉시 끝낸다."""


class ParseError(Exception):
    """따옴표 불일치 등 — 해석 불가."""


# ───────────────────────── 렉서 ─────────────────────────

@dataclass
class Word:
    text: str
    dynamic: bool = False          # $VAR·$(…)·백틱 등 정적으로 값을 알 수 없는 확장을 포함
    subs: list = field(default_factory=list)   # 명령 치환 안쪽 소스 (재귀 분석 대상)


@dataclass
class Redir:
    op: str
    target: "Word | None"


@dataclass
class Frag:
    words: list = field(default_factory=list)
    redirs: list = field(default_factory=list)
    heredocs: list = field(default_factory=list)   # heredoc 본문 문자열들 (정적 here-string `<<<` 도 같은 급으로 모은다)
    stdin_dynamic: bool = False    # stdin 이 동적 here-string 이거나 `< 파일` — 내용을 알 수 없다 (R-14-1)
    piped: bool = False            # 앞 조각의 출력이 파이프로 들어온다
    pipe_src: object = None        # 파이프 앞 조각(Frag). False = 앞이 그룹 `( … )`·`{ … }` 라 출력 원천을 모른다
    heredoc_dyn: bool = False      # 따옴표 없는 구분자의 heredoc 본문에 $(…)·백틱·$VAR·${…} 가 있다 — 본문이 동적 (R-14-13)
    hd_subs: list = field(default_factory=list)    # 그 본문 안 $(…)·백틱의 안쪽 소스 — 바깥 셸이 실행하므로 재귀 분석 대상


_REDIR_RE = re.compile(r"(\d*)(&>>|&>|>>|>\||>&|<<<|<<-|<<|<>|<&|>|<)")
_WORD_STOP = " \t\r\n;|&()<>"


def _match_paren(src: str, i: int) -> int:
    """src[i] == '(' 의 짝 ')' 위치를 돌려준다(따옴표·이스케이프 존중)."""
    depth = 0
    n = len(src)
    j = i
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "'":
            k = src.find("'", j + 1)
            if k < 0:
                raise ParseError("작은따옴표 불일치")
            j = k + 1
            continue
        if c == '"':
            j += 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            if j >= n:
                raise ParseError("큰따옴표 불일치")
            j += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise ParseError("괄호 불일치")


def _match_brace(src: str, i: int) -> int:
    k = src.find("}", i)
    if k < 0:
        raise ParseError("중괄호 불일치")
    return k


def _read_word(src: str, i: int, ps: bool) -> "tuple[Word, int]":
    n = len(src)
    buf: list = []
    dyn = False
    subs: list = []
    # PowerShell here-string  @' … '@  /  @" … "@
    if ps and src[i:i + 2] in ("@'", '@"') and re.match(r"@['\"][ \t]*\r?\n", src[i:]):
        q = src[i + 1]
        m = re.search(r"\r?\n" + q + "@", src[i:])
        if not m:
            raise ParseError("here-string 불일치")
        body_start = src.find("\n", i) + 1
        return Word(src[body_start:i + m.start()]), i + m.end()
    while i < n:
        c = src[i]
        if c in _WORD_STOP:
            break
        if ps and c == "`":                       # PowerShell 이스케이프 문자
            if i + 1 < n:
                buf.append(src[i + 1])
            i += 2
            continue
        if not ps and c == "\\":
            if i + 1 < n:
                if src[i + 1] != "\n":
                    buf.append(src[i + 1])
                i += 2
            else:
                i += 1
            continue
        if c == "'":
            j = i + 1
            while True:
                k = src.find("'", j)
                if k < 0:
                    raise ParseError("작은따옴표 불일치")
                if ps and src[k + 1:k + 2] == "'":      # PowerShell '' = 작은따옴표 하나
                    buf.append(src[j:k + 1])
                    j = k + 2
                    continue
                buf.append(src[j:k])
                i = k + 1
                break
            continue
        if c == '"':
            i += 1
            while True:
                if i >= n:
                    raise ParseError("큰따옴표 불일치")
                d = src[i]
                if d == '"':
                    i += 1
                    break
                if ps and d == "`":
                    if i + 1 < n:
                        buf.append(src[i + 1])
                    i += 2
                    continue
                if not ps and d == "\\" and i + 1 < n and src[i + 1] in '"\\$`\n':
                    if src[i + 1] != "\n":
                        buf.append(src[i + 1])
                    i += 2
                    continue
                if d == "$":
                    i, d_dyn = _read_dollar(src, i, buf, subs, ps, in_dq=True)
                    dyn = dyn or d_dyn
                    continue
                if d == "`" and not ps:
                    k = _find_backtick(src, i)
                    subs.append(src[i + 1:k])
                    buf.append(src[i:k + 1])
                    dyn = True
                    i = k + 1
                    continue
                buf.append(d)
                i += 1
            continue
        if c == "$":
            i, d_dyn = _read_dollar(src, i, buf, subs, ps, in_dq=False)
            dyn = dyn or d_dyn
            continue
        if c == "`" and not ps:
            k = _find_backtick(src, i)
            subs.append(src[i + 1:k])
            buf.append(src[i:k + 1])
            dyn = True
            i = k + 1
            continue
        buf.append(c)
        i += 1
    return Word("".join(buf), dyn, subs), i


def _find_backtick(src: str, i: int) -> int:
    j = i + 1
    while j < len(src):
        if src[j] == "\\":
            j += 2
            continue
        if src[j] == "`":
            return j
        j += 1
    raise ParseError("백틱 불일치")


def _read_dollar(src: str, i: int, buf: list, subs: list, ps: bool, in_dq: bool) -> "tuple[int, bool]":
    """src[i] == '$' 를 읽어 buf 에 원문을 넣고 (새 위치, 동적 여부) 를 돌려준다."""
    nxt = src[i + 1:i + 2]
    if nxt == "(":
        if src[i + 2:i + 3] == "(":              # $(( 산술 ))
            k = _match_paren(src, i + 1)
            buf.append(src[i:k + 1])
            return k + 1, True
        k = _match_paren(src, i + 1)
        subs.append(src[i + 2:k])
        buf.append(src[i:k + 1])
        return k + 1, True
    if nxt == "{":
        k = _match_brace(src, i)
        buf.append(src[i:k + 1])
        return k + 1, True
    if nxt == "'" and not in_dq and not ps:      # $'…' (ANSI-C 따옴표)
        j = i + 2
        while j < len(src) and src[j] != "'":
            j += 2 if src[j] == "\\" else 1
        if j >= len(src):
            raise ParseError("$'…' 불일치")
        buf.append(src[i + 2:j])
        return j + 1, False
    pat = r"[A-Za-z_][\w:]*" if ps else r"[A-Za-z_][A-Za-z0-9_]*|[0-9@#?*!$-]"
    m = re.match(pat, src[i + 1:])
    if m:
        buf.append(src[i:i + 1 + m.end()])
        return i + 1 + m.end(), True
    buf.append("$")
    return i + 1, False


def _heredoc_expansions(body: str) -> "tuple[list, bool]":
    """따옴표 없는 구분자 heredoc 본문의 확장을 찾는다 (R-14-13).

    (명령 치환 안쪽 소스 목록, 동적 여부). `\\$`·`\\`` 로 이스케이프된 것은 확장이 아니다.
    `$VAR`·`${…}`·`$((…))` 는 값이 치환될 뿐 실행되지 않지만 본문이 동적이라는 표시로 남긴다."""
    subs: list = []
    dyn = False
    i, n = 0, len(body)
    while i < n:
        c = body[i]
        if c == "\\":
            i += 2
            continue
        if c == "`":
            k = _find_backtick(body, i)
            subs.append(body[i + 1:k])
            dyn = True
            i = k + 1
            continue
        if c == "$":
            nxt = body[i + 1:i + 2]
            if nxt == "(":
                k = _match_paren(body, i + 1)
                if body[i + 2:i + 3] != "(":                    # $(( 산술 )) 은 명령이 아니다
                    subs.append(body[i + 2:k])
                dyn = True
                i = k + 1
                continue
            if nxt == "{":
                dyn = True
                i += 2                                          # 안쪽 $(…) 도 이어서 찾는다
                continue
            if nxt and re.match(r"[A-Za-z_0-9@#?*!$-]", nxt):
                dyn = True
                i += 2
                continue
        i += 1
    return subs, dyn


def parse(src: str, ps: bool = False) -> list:
    """명령 문자열을 조각(Frag) 목록으로 나눈다. 해석 불가면 ParseError."""
    n = len(src)
    i = 0
    frags: list = []
    cur = Frag()
    pending: list = []                            # (구분자, 탭제거 여부, 조각)
    pipe_state = [False, None]                    # [다음 조각이 파이프 출력을 받는가, 파이프 앞 조각]

    def flush() -> None:
        nonlocal cur
        if cur.words or cur.redirs:
            if pipe_state[0]:
                cur.piped, cur.pipe_src = True, pipe_state[1]
                pipe_state[0], pipe_state[1] = False, None
            frags.append(cur)
        cur = Frag()

    def read_bodies(pos: int) -> int:
        for delim, strip, frag, quoted in pending:
            lines = []
            while pos < n:
                j = src.find("\n", pos)
                line = src[pos:j if j >= 0 else n]
                pos = j + 1 if j >= 0 else n
                cmp_line = line.rstrip("\r")
                if strip:
                    cmp_line = cmp_line.lstrip("\t")
                if cmp_line == delim:
                    break
                lines.append(line)
            body = "\n".join(lines)
            frag.heredocs.append(body)
            if not quoted and not ps:                  # 따옴표 없는 구분자 = 바깥 셸이 본문을 먼저 확장한다 (R-14-13)
                subs, dyn = _heredoc_expansions(body)
                frag.hd_subs.extend(subs)
                frag.heredoc_dyn = frag.heredoc_dyn or dyn
        pending.clear()
        return pos

    while i < n:
        c = src[i]
        if c == "\n":
            flush()
            i += 1
            if pending:
                i = read_bodies(i)
            continue
        if c in " \t\r":
            i += 1
            continue
        if c == "#":                              # 주석
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        m = _REDIR_RE.match(src, i)
        if m:
            fd, op = m.group(1), m.group(2)
            j = m.end()
            if not fd and op in ("<", ">") and src[j:j + 1] == "(":      # 프로세스 치환
                k = _match_paren(src, j)
                cur.words.append(Word("/dev/fd/proc", True, [src[j + 1:k]]))
                i = k + 1
                continue
            while j < n and src[j] in " \t":
                j += 1
            if j >= n or src[j] in "\n;|&()":
                cur.redirs.append(Redir(op, None))
                i = j
                continue
            j0 = j
            target, j = _read_word(src, j, ps)
            cur.redirs.append(Redir(op, target))
            if op in ("<<", "<<-"):
                quoted = any(ch in src[j0:j] for ch in "'\"\\")     # 구분자의 일부라도 인용되면 본문 확장 없음
                pending.append((target.text, op == "<<-", cur, quoted))
            elif op == "<<<" and fd in ("", "0"):      # here-string: heredoc 과 같은 급의 stdin 코드
                if target.dynamic:
                    cur.stdin_dynamic = True
                else:
                    cur.heredocs.append(target.text)
            elif op == "<" and fd in ("", "0"):        # `< 파일` : 내용을 알 수 없는 stdin
                cur.stdin_dynamic = True
            i = j
            continue
        if c == ";":
            flush()
            i += 1
            continue
        if c == "&":
            flush()
            i += 2 if src[i:i + 2] == "&&" else 1
            continue
        if c == "|":
            before = src[:i].rstrip(" \t")
            flush()
            if src[i:i + 2] == "||":
                i += 2
                continue
            i += 2 if src[i:i + 2] == "|&" else 1
            pipe_state[0] = True
            grouped = before.endswith((")", "}")) or not frags
            pipe_state[1] = False if grouped else frags[-1]
            continue
        if c in "()":
            flush()
            i += 1
            continue
        start = i
        word, i = _read_word(src, i, ps)
        if word.text in ("{", "}") and src[start] in "{}":
            flush()                                # 블록 구분자 (PowerShell 스크립트 블록 포함)
            continue
        cur.words.append(word)
    flush()
    return frags


# ───────────────────────── 구조 분해 (재귀) ─────────────────────────

_KEYWORDS = {"if", "then", "elif", "else", "fi", "do", "done", "while", "until", "for", "in",
             "case", "esac", "select", "function", "!", "[[", "]]", "foreach"}
_SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
_PS_SHELLS = {"pwsh", "powershell"}
_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _base(text: str) -> str:
    name = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
    if name.endswith(".exe"):
        name = name[:-4]
    return name


@dataclass
class XArgs:
    """xargs 로 이어져 대상이 stdin 에서 온다는 표시 (항상 참으로 평가된다). `ph` 는 -I/-i/--replace 의 자리표 (R-14-12)."""
    ph: "str | None" = None


# xargs 의 값을 받는 짧은 옵션 (자리표 -I·-i 는 따로 처리)
_XARGS_VAL = "nPdLsE"


def _xargs_opts(w: list) -> "tuple[list, XArgs]":
    """`xargs` 다음 단어 목록에서 옵션을 벗기고 자리표를 읽는다. (남은 단어, XArgs)"""
    xa = XArgs()
    while w and w[0].text.startswith("-") and w[0].text != "-":
        t = w[0].text
        if t == "--":
            w = w[1:]
            break
        if t.startswith("--"):
            name, eq, val = t.partition("=")
            if name == "--replace":
                xa.ph = val or "{}"
            elif name in ("--max-args", "--max-procs", "--delimiter", "--max-lines", "--max-chars") and not eq:
                w = w[1:]                              # 값은 다음 단어
            w = w[1:]
            continue
        letters, skip, k = t[1:], 1, 0
        while k < len(letters):
            ch = letters[k]
            rest = letters[k + 1:]
            if ch == "I":
                if rest:
                    xa.ph = rest
                elif len(w) > 1:
                    xa.ph = w[1].text
                    skip = 2
                break
            if ch == "i":
                xa.ph = rest or "{}"
                break
            if ch in _XARGS_VAL:
                if not rest:
                    skip = 2
                break
            k += 1
        w = w[skip:]
    return w, xa


def strip_prefix(words: list) -> "tuple[list, bool | XArgs]":
    """앞의 변수 대입·제어 키워드·감싸는 명령(env·command·nohup·time·xargs…)을 벗긴다.

    돌려주는 두 번째 값은 xargs 로 이어져 대상이 stdin 에서 온다는 표시다(없으면 False, 있으면 XArgs)."""
    stdin_args = False
    w = list(words)
    while w:
        t = w[0].text
        name = _base(t)
        if _ASSIGN_RE.match(t) or name in _KEYWORDS:
            w = w[1:]
        elif name in ("command", "builtin", "exec", "nohup", "time", "sudo"):
            w = w[1:]
            while w and w[0].text.startswith("-"):
                w = w[1:]
        elif name == "env":
            w = w[1:]
            while w and (w[0].text.startswith("-") or _ASSIGN_RE.match(w[0].text)):
                skip = 2 if w[0].text in ("-u", "-C", "-S") else 1
                w = w[skip:]
        elif name == "nice":
            w = w[1:]
            while w and w[0].text.startswith("-"):
                w = w[2:] if w[0].text == "-n" else w[1:]
        elif name == "timeout":
            w = w[1:]
            while w and w[0].text.startswith("-"):
                w = w[1:]
            w = w[1:]                              # 시간 인자
        elif name == "xargs":
            w, stdin_args = _xargs_opts(w[1:])
        else:
            break
    return w, stdin_args


def _pipe_literal(frag: Frag) -> "str | None":
    """파이프로 들어오는 stdin 의 내용을 정적으로 알 수 있으면 그 문자열, 아니면 None (R-14-1).

    알 수 있는 경우는 앞 조각이 인자가 전부 정적인 echo·printf 이거나, 인자 없는 `cat <<heredoc` 일 때뿐이다."""
    src = frag.pipe_src
    if not isinstance(src, Frag) or src.piped or src.stdin_dynamic:
        return None
    ws, _ = strip_prefix(src.words)
    if not ws:
        return None
    nm, args = _base(ws[0].text), ws[1:]
    if any(a.dynamic for a in args):
        return None
    if nm in ("echo", "printf"):
        texts = [a.text for a in args if not (nm == "echo" and re.fullmatch(r"-[neE]+", a.text))]
        return " ".join(texts).replace("\\n", "\n")
    if nm == "cat" and src.heredocs and not src.heredoc_dyn and not [a for a in args if not a.text.startswith("-")]:
        return "\n".join(src.heredocs)
    return None


def _stdin_codes(frag: Frag, code_ps: bool) -> "list":
    """셸이 stdin 으로 받는 코드들. 내용을 알 수 없으면 (빈 문자열, True) — 판정 불가로 거부된다."""
    out = [(body, False, code_ps) for body in frag.heredocs]
    if frag.heredoc_dyn or frag.stdin_dynamic:         # heredoc 본문이 $(…)·$VAR 를 품으면 실행 코드가 동적이다 (R-14-13)
        out.append(("", True, code_ps))
    if frag.piped:
        lit = _pipe_literal(frag)
        out.append(("", True, code_ps) if lit is None else (lit, False, code_ps))
    return out


def _xargs_input(frag: Frag) -> "str | None":
    """xargs 가 읽는 stdin 의 내용을 정적으로 알 수 있으면 그 문자열, 아니면 None (R-14-12)."""
    if frag.piped:
        return _pipe_literal(frag)
    if frag.stdin_dynamic or frag.heredoc_dyn:
        return None
    return "\n".join(frag.heredocs) if frag.heredocs else None


def _xargs_codes(word: Word, xa, frag: Frag) -> "tuple[list, bool] | None":
    """`xargs -I{} sh -c {}` 처럼 자리표가 **코드 자리**에 오면 코드는 stdin 입력에서 온 것이다 (R-14-12).

    None = 해당 없음(자리표 없음, 또는 코드가 자리표로 시작하지 않아 인자 자리일 뿐).
    (코드 목록, 내용을 아는가) = 입력이 정적 리터럴이면 줄마다 자리표를 바꾼 코드들, 아니면 ([], False) — 판정 불가."""
    if not isinstance(xa, XArgs) or not xa.ph or word.dynamic or not word.text.lstrip().startswith(xa.ph):
        return None
    lit = _xargs_input(frag)
    if lit is None:
        return [], False
    return [word.text.replace(xa.ph, ln) for ln in lit.splitlines() if ln.strip()], True


def _shell_codes(name: str, args: list, frag: Frag, xa=False) -> "list":
    """셸이 실행할 코드 문자열들 [(코드, 동적 여부, 파워셸 여부)]. 스크립트 파일 실행이면 빈 목록."""
    out = []
    if name in _SHELLS:
        for k, a in enumerate(args):
            if re.fullmatch(r"-[a-zA-Z]*c[a-zA-Z]*", a.text) and k + 1 < len(args):
                xc = _xargs_codes(args[k + 1], xa, frag)
                if xc is None:
                    out.append((args[k + 1].text, args[k + 1].dynamic, False))
                elif xc[1]:
                    out.extend((c, False, False) for c in xc[0])
                else:
                    out.append(("", True, False))
                return out
        reads_stdin = any(re.fullmatch(r"-[a-zA-Z]*s[a-zA-Z]*", a.text) for a in args)
        if reads_stdin or not [a for a in args if not a.text.startswith("-")]:    # 스크립트 파일 없음 → stdin
            out.extend(_stdin_codes(frag, False))
    elif name in _PS_SHELLS:
        for k, a in enumerate(args):
            low = a.text.lower()
            if low in ("-command", "-c", "-commandwithargs") and k + 1 < len(args):
                code = " ".join(x.text for x in args[k + 1:])
                out.append((code, any(x.dynamic for x in args[k + 1:]), True))
                return out
            if low.startswith("-enc"):
                out.append(("", True, True))
                return out
        if not [a for a in args if not a.text.startswith("-")]:
            out.extend(_stdin_codes(frag, True))
    elif name == "eval":
        out.append((" ".join(x.text for x in args), any(x.dynamic for x in args), False))
    return out


def iter_cmds(src: str, ps: bool = False, depth: int = 0):
    """(조각, 벗긴 명령 단어들, stdin_args) 를 재귀로 낸다.

    명령 치환·프로세스 치환·`bash -c`·`bash <<heredoc`·`eval` 안쪽까지 내려간다."""
    if depth > MAX_DEPTH:
        raise Deny("명령 중첩이 너무 깊어 검사할 수 없다.")
    for frag in parse(src, ps):
        for w in frag.words + [r.target for r in frag.redirs if r.target is not None]:
            for s in w.subs:
                yield from iter_cmds(s, ps, depth + 1)
        for s in frag.hd_subs:                    # 따옴표 없는 heredoc 본문의 $(…)·백틱 — 바깥 셸이 실행한다 (R-14-13)
            yield from iter_cmds(s, ps, depth + 1)
        words, stdin_args = strip_prefix(frag.words)
        yield from _frag_cmds(frag, words, stdin_args, ps, depth)


def _find_exec_frags(args: list) -> "list":
    """`find <시작경로…> … -exec|-execdir|-ok|-okdir <명령…> {} ;|+` 의 명령을 가짜 조각으로 뗀다 (R-14-3).

    `{}` 는 find 의 시작 경로(없으면 `.`)로 바꿔 같은 쓰기 판정에 태운다 — 시작 경로가 프로젝트 안이면
    그 아래 어떤 파일이든 대상이 될 수 있으므로 거부된다."""
    starts = []
    for a in args:
        if a.text.startswith("-") or a.text in ("!", "(", ")"):
            break
        starts.append(a)
    starts = starts or [Word(".")]
    frags = []
    k = 0
    while k < len(args):
        if args[k].text in ("-exec", "-execdir", "-ok", "-okdir"):
            seg = []
            k += 1
            while k < len(args) and args[k].text not in (";", "+"):
                seg.append(args[k])
                k += 1
            if seg:
                for st in starts:
                    frags.append(Frag(words=[
                        Word(w.text.replace("{}", st.text), w.dynamic or (st.dynamic and "{}" in w.text), w.subs)
                        for w in seg]))
        k += 1
    return frags


def _frag_cmds(frag: Frag, words: list, stdin_args: bool, ps: bool, depth: int):
    if depth > MAX_DEPTH:
        raise Deny("명령 중첩이 너무 깊어 검사할 수 없다.")
    if words:
        name = _base(words[0].text)
        for code, dyn, code_ps in _shell_codes(name, words[1:], frag, stdin_args):
            if not dyn and code:
                yield from iter_cmds(code, code_ps, depth + 1)
    yield frag, words, stdin_args
    if words and _base(words[0].text) == "find":
        for pf in _find_exec_frags(words[1:]):
            w2, sa2 = strip_prefix(pf.words)
            yield from _frag_cmds(pf, w2, sa2, ps, depth + 1)


# ───────────────────────── 경로 판정 ─────────────────────────

_SAFE_DEVICES = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty", "nul", "$null"}
_TMP_DYN_RE = re.compile(
    r"^(\$\{?(TMPDIR|TEMP|TMP|CLAUDE_SCRATCHPAD)\}?|\$env:(TEMP|TMP|TMPDIR))([\\/]|$)", re.IGNORECASE)


def _inside(path: str, base: str) -> bool:
    return path == base or path.startswith(base.rstrip("/\\") + os.sep) or path.startswith(base.rstrip("/\\") + "/")


class PathJudge:
    def __init__(self, root: str, ps: bool = False):
        self.root = root
        self.root_real = os.path.normcase(os.path.realpath(root))
        self.ps = ps
        temps = ["/tmp", "/private/tmp", "/var/tmp", tempfile.gettempdir()]
        for var in ("TMPDIR", "TEMP", "TMP", "CLAUDE_SCRATCHPAD"):
            if os.environ.get(var):
                temps.append(os.environ[var])
        self.temps = [os.path.normcase(os.path.realpath(t)) for t in temps]

    def judge(self, w: Word, form: str, allow_dash: bool = False) -> None:
        """대상 경로가 임시 영역이면 통과, 아니면 Deny."""
        t = w.text
        if t.lower() in _SAFE_DEVICES or t.startswith("/dev/fd/") or (allow_dash and t == "-"):
            return
        if t == "":
            return
        if _TMP_DYN_RE.match(t):
            rest = re.split(r"[\\/]", t)[1:]
            if ".." in rest:
                raise Deny(f"[bash-write-guard] {form}: 임시 영역 변수 뒤에 '..' 가 있어 경로를 판정할 수 없다.")
            return
        if w.dynamic or "$" in t or "`" in t:
            raise Deny(
                f"[bash-write-guard] {form}: 쓰기 대상 경로 '{t}' 를 판정할 수 없다(변수·명령 치환·계산된 경로). "
                "검사할 수 없으면 통과가 아니라 차단한다(security.md). 임시 파일이면 절대 경로(/tmp·$TMPDIR)로, "
                "프로젝트 파일이면 Write/Edit 툴로 쓰라 (FIX-014)."
            )
        p = t
        if self.ps and os.sep == "/":
            p = p.replace("\\", "/")
        if p.startswith("~"):
            p = os.path.expanduser(p)
        if os.name == "nt":
            m = re.match(r"^/([A-Za-z])/(.*)$", p)           # Git Bash 의 /c/Users/…
            if m:
                p = f"{m.group(1)}:/{m.group(2)}"
        is_abs = os.path.isabs(p) or bool(re.match(r"^[A-Za-z]:[\\/]", p))
        full = p if is_abs else os.path.join(self.root, p)
        norm = os.path.normpath(full)
        real = os.path.normcase(os.path.realpath(norm))
        if _inside(real, self.root_real):
            raise Deny(
                f"[bash-write-guard] {form}: 쓰기 대상 '{t}' 는 프로젝트 안이다. 프로젝트 파일은 Bash 로 쓰지 말고 "
                "Write/Edit 툴로 고쳐라 — stage-gate(활성 작업·동결·L-003)와 secret-guard(비밀 검사)를 거치도록 "
                "(FIX-014, CLAUDE.md '파일 변경은 Write/Edit 툴로만'). 임시 파일은 /tmp·$TMPDIR·스크래치패드에 쓴다."
            )
        text = norm.replace("\\", "/")
        if text.startswith(("/tmp/", "/private/tmp/", "/var/tmp/")):
            return
        for tr in self.temps:
            if _inside(real, tr):
                return
        if "scratchpad" in [s.lower() for s in re.split(r"[\\/]", text)]:
            return
        raise Deny(
            f"[bash-write-guard] {form}: 쓰기 대상 '{t}' 는 프로젝트 밖이지만 임시 영역(/tmp·$TMPDIR·스크래치패드)도 아니다. "
            "허용하지 않는다(FIX-014). 필요하면 사용자에게 요청하라."
        )


# ───────────────────────── 인수 파서 ─────────────────────────

def split_args(args: list, short_val: set = frozenset(), long_val: set = frozenset(),
               suffix_letters: set = frozenset()) -> "tuple[list, list]":
    """GNU 스타일 인수를 (위치 인수, [(옵션, 값 Word|None)]) 로 나눈다."""
    pos: list = []
    opts: list = []
    i = 0
    end = False
    while i < len(args):
        a = args[i]
        t = a.text
        if end or not t.startswith("-") or t == "-":
            pos.append(a)
            i += 1
            continue
        if t == "--":
            end = True
            i += 1
            continue
        if t.startswith("--"):
            name, eq, val = t.partition("=")
            if eq:
                opts.append((name, Word(val, a.dynamic)))
            elif name in long_val and i + 1 < len(args):
                opts.append((name, args[i + 1]))
                i += 1
            else:
                opts.append((name, None))
            i += 1
            continue
        letters = t[1:]
        for k, ch in enumerate(letters):
            if ch in suffix_letters:
                opts.append(("-" + ch, None))
                break
            if "-" + ch in short_val:
                rest = letters[k + 1:]
                if rest:
                    opts.append(("-" + ch, Word(rest, a.dynamic)))
                elif i + 1 < len(args):
                    opts.append(("-" + ch, args[i + 1]))
                    i += 1
                else:
                    opts.append(("-" + ch, None))
                break
            opts.append(("-" + ch, None))
        i += 1
    return pos, opts


def _opt(opts: list, *names: str):
    for o, v in opts:
        if o in names:
            return True, v
    return False, None


# ───────────────────────── 인라인 코드 검사 ─────────────────────────

def _call_args(code: str, start: int) -> list:
    """code[start] 는 '(' 바로 다음 위치. 최상위 쉼표로 나눈 인수 문자열 목록."""
    args: list = []
    cur: list = []
    depth = 1
    i = start
    n = len(code)
    while i < n:
        c = code[i]
        if c in "'\"`":
            j = i + 1
            while j < n and code[j] != c:
                j += 2 if code[j] == "\\" else 1
            cur.append(code[i:j + 1])
            i = j + 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                break
        if c == "," and depth == 1:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    last = "".join(cur).strip()
    if last or args:
        args.append(last)
    return args


def _literal(arg: str) -> "str | None":
    m = re.fullmatch(r"(?:[rRbBuU]{0,2})(['\"])(.*)\1", arg, re.DOTALL)
    if m and not re.match(r"[fF]", arg):
        return m.group(2)
    m = re.fullmatch(r"`([^`$]*)`", arg)          # JS 템플릿 리터럴 (보간 없음)
    return m.group(1) if m else None


def _kwarg(args: list, name: str) -> "str | None":
    for a in args:
        m = re.fullmatch(r"%s\s*=\s*(.*)" % re.escape(name), a, re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


_PY_FUNC_MODULES = {"io", "codecs", "gzip", "bz2", "lzma", "os", "tarfile", "zipfile"}


class CodeInspector:
    def __init__(self, judge: PathJudge):
        self.judge = judge

    def _target(self, arg: "str | None", form: str) -> None:
        lit = _literal(arg) if arg is not None else None
        if lit is None:
            raise Deny(
                f"[bash-write-guard] {form}: 인라인 코드가 쓰는 파일 경로를 판정할 수 없다(문자열 상수가 아님). "
                "프로젝트 파일은 Write/Edit 툴로 쓰라 (FIX-014)."
            )
        self.judge.judge(Word(lit), form)

    def python(self, code: str) -> None:
        for m in re.finditer(r"(\.?)\bopen\s*\(", code):
            dot = m.group(1) == "."
            args = _call_args(code, m.end())
            if dot:
                recv = re.search(r"(\w+)\s*$", code[:m.start()])
                func_style = bool(recv and recv.group(1) in _PY_FUNC_MODULES)
            else:
                func_style = True
            if func_style:
                path_arg = args[0] if args else _kwarg(args, "file")
                mode_arg = args[1] if len(args) > 1 and "=" not in args[1].split("(")[0] else _kwarg(args, "mode")
            else:
                path_arg = None
                mode_arg = args[0] if args and not re.match(r"\w+\s*=", args[0]) else _kwarg(args, "mode")
            if mode_arg is None:
                continue                                # 모드 없음 = 읽기
            mode = _literal(mode_arg)
            if mode is None:
                raise Deny("[bash-write-guard] 인라인 python open() 의 모드를 판정할 수 없다(변수). "
                           "프로젝트 파일은 Write/Edit 툴로 쓰라 (FIX-014).")
            if not set(mode) & set("wax+"):
                continue
            if func_style:
                self._target(path_arg, "python open() 쓰기")
            else:
                pm = re.search(r"Path\(\s*(['\"])(.*?)\1\s*\)\s*$", code[:m.start()])
                self._target(f"'{pm.group(2)}'" if pm else None, "python Path.open() 쓰기")
        for m in re.finditer(r"\.write_(?:text|bytes)\s*\(", code):
            pm = re.search(r"Path\(\s*(['\"])(.*?)\1\s*\)\s*$", code[:m.start()])
            self._target(f"'{pm.group(2)}'" if pm else None, "python write_text/write_bytes")
        for m in re.finditer(r"\b(?:shutil\.(?:copy|copy2|copyfile|copytree|move)|os\.(?:rename|replace|link|symlink))\s*\(",
                             code):
            args = _call_args(code, m.end())
            self._target(args[1] if len(args) > 1 else None, "python 파일 복사·이동")

    def node(self, code: str) -> None:
        pat = (r"\b(writeFile|writeFileSync|appendFile|appendFileSync|createWriteStream|"
               r"copyFile|copyFileSync|rename|renameSync|cp|cpSync|Bun\.write|Deno\.writeTextFile(?:Sync)?|Deno\.writeFile(?:Sync)?)\s*\(")
        for m in re.finditer(pat, code):
            args = _call_args(code, m.end())
            idx = 1 if m.group(1) in ("copyFile", "copyFileSync", "rename", "renameSync", "cp", "cpSync") else 0
            self._target(args[idx] if len(args) > idx else None, "node 파일 쓰기")

    def other(self, code: str, lang: str) -> None:
        if re.search(r"File\.(write|open|binwrite)|IO\.(write|binwrite)|FileUtils\.|open\s*\(?\s*\w*\s*,?\s*['\"]\s*\+?>|"
                     r"file_put_contents\s*\(|\bfwrite\s*\(|\bfopen\s*\([^)]*,\s*['\"][wxac]", code):
            raise Deny(f"[bash-write-guard] 인라인 {lang} 코드의 파일 쓰기 대상을 판정할 수 없다. "
                       "프로젝트 파일은 Write/Edit 툴로 쓰라 (FIX-014).")


# ───────────────────────── 쓰기 형태 판정 ─────────────────────────

_PS_PATH_PARAMS = {"path", "filepath", "literalpath", "lp", "pspath", "file"}
_PS_VALUE_PARAMS = {"value", "encoding", "itemtype", "name", "inputobject", "width", "stream", "delimiter",
                    "type", "filter", "include", "exclude", "newname", "depth", "pipelinevariable"}
_PS_WRITERS = {"set-content", "sc", "add-content", "ac", "out-file", "clear-content", "clc", "new-item", "ni",
               "export-csv", "export-clixml", "tee-object"}
_PS_COPIERS = {"copy", "copy-item", "cpi", "move", "move-item", "mi"}
_PS_RENAMERS = {"rename-item", "rni"}
_PS_DOTNET_RE = re.compile(
    r"\[(?:System\.)?IO\.File\]::(?:Write|Append|Create|Copy|Move|Replace|Open)|StreamWriter|FileStream", re.IGNORECASE)


class WriteChecker:
    def __init__(self, root: str, ps: bool):
        self.ps = ps
        self.judge = PathJudge(root, ps)
        self.code = CodeInspector(self.judge)

    def check(self, src: str) -> None:
        if self.ps and _PS_DOTNET_RE.search(src):
            raise Deny("[bash-write-guard] PowerShell 의 .NET 파일 쓰기([IO.File]::Write… · StreamWriter)는 "
                       "대상을 판정할 수 없다. 프로젝트 파일은 Write/Edit 툴로 쓰라 (FIX-014).")
        for frag, words, stdin_args in iter_cmds(src, self.ps):
            self.frag(frag, words, stdin_args)

    # 조각 하나
    def frag(self, frag: Frag, words: list, stdin_args: bool) -> None:
        for r in frag.redirs:
            if r.op in (">", ">>", ">|", "&>", "&>>", ">&"):
                if r.target is None:
                    raise Deny(f"[bash-write-guard] 리다이렉트 '{r.op}' 의 대상을 판정할 수 없다.")
                if r.op == ">&" and re.fullmatch(r"\d+|-", r.target.text):
                    continue                            # >&2 · 2>&1 : 파일 기술자 복제
                self.judge.judge(r.target, f"리다이렉트 '{r.op}'")
        if not words:
            return
        name = _base(words[0].text)
        args = words[1:]
        h = getattr(self, "cmd_" + re.sub(r"\W", "_", name), None)
        if h is not None:
            h(args, frag, stdin_args)
            return
        if re.fullmatch(r"python[\d.]*|py|pypy[\d.]*", name):
            self.cmd_python(args, frag, stdin_args)
        elif name in _SHELLS or name in _PS_SHELLS or name == "eval":
            self.shell_dynamic(name, args, frag, stdin_args)
        elif name in _PS_WRITERS:
            self.ps_write(name, args, stdin_args)
        elif name in _PS_COPIERS:
            self.ps_copy(args)
        elif name in _PS_RENAMERS:
            self.ps_write(name, args, stdin_args)
        elif name in ("vi", "vim", "nvim", "view") and (
                frag.heredocs or any(a.text.startswith(("-c", "-s", "-es", "+")) for a in args)):
            raise Deny("[bash-write-guard] vi/vim 의 스크립트 모드는 파일을 쓴다. Write/Edit 툴로 쓰라 (FIX-014).")

    # ── 개별 명령 ──
    def need(self, targets: list, form: str, stdin_args: bool, allow_empty: bool = False) -> None:
        if not targets:
            if allow_empty and not stdin_args:
                return
            raise Deny(f"[bash-write-guard] {form}: 쓰기 대상 파일을 판정할 수 없다"
                       f"{'(xargs 로 stdin 에서 옴)' if stdin_args else ''}. Write/Edit 툴을 쓰라 (FIX-014).")
        for t in targets:
            self.judge.judge(t, form)

    def cmd_tee(self, args, frag, stdin_args):
        pos, _ = split_args(args)
        self.need(pos, "tee", stdin_args, allow_empty=True)

    def cmd_sed(self, args, frag, stdin_args):
        pos, opts = split_args(args, {"-e", "-f", "-l"}, {"--expression", "--file", "--line-length"}, {"i"})
        inplace = any(o == "-i" or o.startswith("--in-place") for o, _ in opts)
        if not inplace:
            return
        have_script = any(o in ("-e", "-f", "--expression", "--file") for o, _ in opts)
        pos = [p for p in pos if p.text != "" or p.dynamic]           # BSD `-i ''` 의 빈 접미사
        files = pos if have_script else pos[1:]
        self.need(files, "sed -i", stdin_args)

    def cmd_perl(self, args, frag, stdin_args):
        pos, opts = split_args(args, {"-e", "-E", "-I", "-M", "-m", "-x", "-F", "-l"}, set(), {"i"})
        have_code = any(o in ("-e", "-E") for o, _ in opts)
        if have_code:
            for o, v in opts:
                if o in ("-e", "-E") and v is not None:
                    for c in self._codes_of(v, "perl", stdin_args, frag):
                        self.code.other(c, "perl")
        elif not [p for p in pos if p.text != "-"] and not any(o in ("-v", "-c", "-h") for o, _ in opts):
            for c in self._stdin_code_list(frag, "perl"):      # 스크립트도 -e 도 없으면 stdin 이 프로그램이다 (R-14-14)
                self.code.other(c, "perl")
        if any(o == "-i" for o, _ in opts):
            self.need(pos if have_code else pos[1:], "perl -i", stdin_args)

    def cmd_awk(self, args, frag, stdin_args):
        pos, opts = split_args(args, {"-i", "-f", "-v", "-F"}, {"--include", "--file"})
        if any(o == "-i" and v is not None and v.text == "inplace" for o, v in opts):
            have_prog = any(o in ("-f", "--file") for o, _ in opts)
            self.need(pos if have_prog else pos[1:], "awk -i inplace", stdin_args)

    cmd_gawk = cmd_awk

    def _copy_like(self, args, form, stdin_args, short_val, long_val):
        pos, opts = split_args(args, short_val, long_val)
        has_t, tv = _opt(opts, "-t", "--target-directory")
        if has_t and tv is not None:
            self.judge.judge(tv, form)
        elif form.startswith("install") and _opt(opts, "-d", "--directory")[0]:
            self.need(pos, form, stdin_args)
        elif len(pos) >= 2:
            self.judge.judge(pos[-1], form)
        else:
            raise Deny(f"[bash-write-guard] {form}: 목적지를 판정할 수 없다. Write/Edit 툴을 쓰라 (FIX-014).")

    def cmd_cp(self, args, frag, stdin_args):
        self._copy_like(args, "cp 목적지", stdin_args, {"-t", "-S"}, {"--target-directory", "--suffix"})

    def cmd_mv(self, args, frag, stdin_args):
        self._copy_like(args, "mv 목적지", stdin_args, {"-t", "-S"}, {"--target-directory", "--suffix"})

    def cmd_ln(self, args, frag, stdin_args):
        self._copy_like(args, "ln 목적지", stdin_args, {"-t", "-S"}, {"--target-directory", "--suffix"})

    def cmd_install(self, args, frag, stdin_args):
        self._copy_like(args, "install 목적지", stdin_args, {"-m", "-o", "-g", "-t", "-S"},
                        {"--mode", "--owner", "--group", "--target-directory", "--suffix"})

    def cmd_rsync(self, args, frag, stdin_args):
        self._copy_like(args, "rsync 목적지", stdin_args, {"-e"},
                        {"--exclude", "--include", "--exclude-from", "--include-from", "--rsh", "--log-file", "--filter"})

    def cmd_touch(self, args, frag, stdin_args):
        pos, _ = split_args(args, {"-t", "-d", "-r"}, {"--date", "--reference", "--time"})
        self.need(pos, "touch", stdin_args, allow_empty=True)

    def cmd_truncate(self, args, frag, stdin_args):
        pos, _ = split_args(args, {"-s", "-r"}, {"--size", "--reference"})
        self.need(pos, "truncate", stdin_args, allow_empty=True)

    def cmd_dd(self, args, frag, stdin_args):
        for a in args:
            if a.text.startswith("of="):
                self.judge.judge(Word(a.text[3:], a.dynamic), "dd of=")

    def cmd_patch(self, args, frag, stdin_args):
        if not any(a.text in ("--dry-run", "-C", "--check") for a in args):
            raise Deny("[bash-write-guard] patch 는 대상 파일을 직접 고친다. 프로젝트 파일은 Write/Edit 툴로 고쳐라 (FIX-014).")

    def cmd_ed(self, args, frag, stdin_args):
        raise Deny("[bash-write-guard] ed/ex 는 파일을 직접 고친다. Write/Edit 툴로 고쳐라 (FIX-014).")

    cmd_ex = cmd_ed

    def cmd_curl(self, args, frag, stdin_args):
        short = {"-o", "-D", "-c", "-H", "-d", "-X", "-u", "-A", "-e", "-w", "-m", "-b", "-F", "-T", "-K", "-x", "-r"}
        long = {"--output", "--dump-header", "--cookie-jar", "--header", "--data", "--request", "--user",
                "--user-agent", "--output-dir", "--max-time"}
        pos, opts = split_args(args, short, long)
        outdir = next((v for o, v in opts if o == "--output-dir" and v is not None), None)
        for o, v in opts:
            if o in ("-o", "--output", "-D", "--dump-header", "-c", "--cookie-jar") and v is not None:
                self.judge.judge(v, f"curl {o}", allow_dash=True)
            elif o in ("-O", "--remote-name", "--remote-name-all", "-J"):
                if outdir is None:
                    raise Deny("[bash-write-guard] curl -O 는 현재 디렉터리에 파일을 만든다. "
                               "-o <임시경로> 로 대상을 지정하라 (FIX-014).")
                self.judge.judge(outdir, f"curl {o} --output-dir")

    def cmd_wget(self, args, frag, stdin_args):
        pos, opts = split_args(args, {"-O", "-o", "-a", "-P", "-U", "-e"},
                               {"--output-document", "--output-file", "--append-output", "--directory-prefix"})
        out = [(o, v) for o, v in opts if o in ("-O", "--output-document") and v is not None]
        for o, v in opts:
            if o in ("-o", "-a", "--output-file", "--append-output", "-P", "--directory-prefix") and v is not None:
                self.judge.judge(v, f"wget {o}")
        for o, v in out:
            self.judge.judge(v, f"wget {o}", allow_dash=True)
        if not out and pos and not any(o in ("-P", "--directory-prefix") for o, _ in opts):
            raise Deny("[bash-write-guard] wget 은 현재 디렉터리에 파일을 만든다. -O <임시경로> 로 대상을 지정하라 (FIX-014).")

    # ── 인라인 코드 ──
    def cmd_python(self, args, frag, stdin_args):
        codes = []
        script = False
        k = 0
        while k < len(args):
            t = args[k].text
            if re.fullmatch(r"-[A-Za-z]*c", t) and k + 1 < len(args):
                codes.extend(self._codes_of(args[k + 1], "python", stdin_args, frag))
                k += 2
                continue
            if t == "-m":
                script = True
                break
            if not t.startswith("-"):
                script = True
                break
            k += 1
        if not codes and not script:
            if frag.stdin_dynamic:
                raise Deny("[bash-write-guard] python 이 stdin(동적 here-string·파일)에서 코드를 읽는다. "
                           "내용을 검사할 수 없다 (FIX-014).")
            if frag.heredocs:
                codes = list(frag.heredocs)
            else:
                raise Deny("[bash-write-guard] python 이 stdin 에서 코드를 읽는다. 내용을 검사할 수 없다. "
                           "파일 쓰기는 Write/Edit 툴로 하라 (FIX-014).")
        for c in codes:
            self.code.python(c)

    def _need_static(self, word, lang: str) -> None:
        """인라인 코드 인자가 명령 치환·변수를 품으면 내용을 알 수 없다 → 거부 (R-14-2, shell_dynamic 과 같은 규칙)."""
        if word.dynamic:
            raise Deny(f"[bash-write-guard] {lang} 인라인 코드가 변수·명령 치환을 포함해 내용을 판정할 수 없다. "
                       "검사할 수 없으면 차단한다 (FIX-014).")

    def _codes_of(self, word, lang: str, xa, frag) -> list:
        """인라인 코드 인자 하나 → 검사할 코드 문자열 목록. 내용을 알 수 없으면 거부한다.

        xargs 자리표(`-I{}`)가 코드 자리에 오면 코드는 파이프 입력에서 온 것이다 — 리터럴이면 자리표를 바꿔 분석하고
        아니면 판정 불가로 거부 (R-14-12)."""
        xc = _xargs_codes(word, xa, frag)
        if xc is None:
            self._need_static(word, lang)
            return [word.text]
        if not xc[1]:
            raise Deny(f"[bash-write-guard] {lang} 인라인 코드가 xargs 자리표로 파이프 입력에서 온다 — 입력이 정적 리터럴이 아니라 "
                       "내용을 판정할 수 없다. 검사할 수 없으면 차단한다 (FIX-014).")
        return xc[0]

    def _stdin_code_list(self, frag, lang: str) -> list:
        """인자 없는 인터프리터가 stdin(here-string·heredoc·파이프·`< 파일`)으로 받는 코드들 (R-14-14).

        python 과 같은 규칙: 리터럴이면 그 내용을 돌려주고, 파일·명령 출력이면 판정 불가로 거부한다."""
        codes = list(frag.heredocs)
        if frag.stdin_dynamic:
            raise Deny(f"[bash-write-guard] {lang} 가 stdin(동적 here-string·파일)에서 코드를 읽는다. 내용을 검사할 수 없다 (FIX-014).")
        if frag.piped:
            lit = _pipe_literal(frag)
            if lit is None:
                raise Deny(f"[bash-write-guard] {lang} 가 파이프 입력에서 코드를 읽는데 파이프 앞이 정적 리터럴이 아니다. "
                           "내용을 검사할 수 없다 (FIX-014).")
            codes.append(lit)
        return codes

    def _interp_codes(self, args, frag, stdin_args, flags, lang: str, value_opts=(), subcmds=(), code_subcmds=()) -> list:
        """node·ruby·php 등의 검사할 코드: `-e` 류 인라인 인자, 없으면 (스크립트 파일이 없을 때) stdin 코드.

        `subcmds` (deno·bun 의 run·eval·x·exec 등)는 첫 위치인수일 때 위치인수로 세지 않고 건너뛴다 — 뒤에 `-` 나
        인자가 없으면 stdin 코드다 (R-14-16). `code_subcmds` (deno eval)는 바로 뒤 비플래그 인자가 인라인 코드다."""
        codes = []
        for k, a in enumerate(args):
            if a.text in flags and k + 1 < len(args):
                codes.extend(self._codes_of(args[k + 1], lang, stdin_args, frag))
        if codes:
            return codes
        k = 0
        sub = None
        while k < len(args):
            t = args[k].text
            if t in ("-v", "--version", "-h", "--help", "-c", "--check"):
                return list(frag.heredocs)               # 실행이 아니라 정보 출력·문법 검사
            if t in value_opts:
                k += 2
                continue
            if t == "-" or t.startswith("-"):
                k += 1
                continue
            if sub is None and t in subcmds:
                sub = t
                k += 1
                continue
            if sub is not None and sub in code_subcmds:
                return self._codes_of(args[k], lang, stdin_args, frag)   # deno eval "<코드>"
            return list(frag.heredocs)                   # 스크립트 파일 실행 — 파일 내용은 보지 않는다(한계)
        return self._stdin_code_list(frag, lang)

    def cmd_node(self, args, frag, stdin_args):
        for c in self._interp_codes(args, frag, stdin_args, ("-e", "--eval", "-p", "--print"), "node",
                                    ("-r", "--require", "--import", "--loader", "--input-type", "-C", "--conditions")):
            self.code.node(c)

    cmd_nodejs = cmd_node

    def _cmd_runtime(self, args, frag, stdin_args, subcmds, code_subcmds=()):
        """deno·bun: 서브명령(run·eval·x·exec)을 건너뛰고 node 와 같은 규칙 (R-14-16)."""
        for c in self._interp_codes(args, frag, stdin_args, ("-e", "--eval", "-p", "--print"), "node",
                                    ("-r", "--require", "--import", "--loader", "--input-type", "-C", "--conditions"),
                                    subcmds, code_subcmds):
            self.code.node(c)

    def cmd_deno(self, args, frag, stdin_args):
        self._cmd_runtime(args, frag, stdin_args, ("run", "eval", "x"), ("eval",))

    def cmd_bun(self, args, frag, stdin_args):
        self._cmd_runtime(args, frag, stdin_args, ("run", "x", "exec"))

    def cmd_ruby(self, args, frag, stdin_args):
        for c in self._interp_codes(args, frag, stdin_args, ("-e",), "ruby", ("-I", "-r", "-C", "-E")):
            self.code.other(c, "ruby")

    def cmd_php(self, args, frag, stdin_args):
        # `php -r '…'` 인라인은 R-14-5 로 남긴다(범위 밖) — 여기서는 stdin 코드(`… | php`·`php < f`)만 본다 (R-14-14)
        for c in self._interp_codes(args, frag, stdin_args, (), "php", ("-d", "-r", "-f")):
            self.code.other(c, "php")

    def shell_dynamic(self, name, args, frag, xa=False):
        for code, dyn, _ in _shell_codes(name, args, frag, xa):
            if dyn:
                raise Deny(f"[bash-write-guard] {name} 가 실행할 코드를 판정할 수 없다(변수·치환·인코딩). "
                           "검사할 수 없으면 차단한다 (FIX-014).")

    # ── PowerShell ──
    def _ps_params(self, args):
        """(위치 인수, {경로 매개변수 이름: Word})"""
        pos: list = []
        named: dict = {}
        k = 0
        while k < len(args):
            t = args[k].text
            if t.startswith("-") and len(t) > 1 and not re.match(r"-\d", t):
                nm, colon, val = t[1:].partition(":")
                low = nm.lower()
                value = Word(val, args[k].dynamic) if colon and val else None
                if low in _PS_PATH_PARAMS or low in ("destination", "dest"):
                    if value is None and k + 1 < len(args):
                        value = args[k + 1]
                        k += 1
                    if value is not None:
                        named["destination" if low in ("destination", "dest") else "path"] = value
                elif low in _PS_VALUE_PARAMS and value is None:
                    k += 1
                k += 1
                continue
            pos.append(args[k])
            k += 1
        return pos, named

    def ps_write(self, name, args, stdin_args):
        pos, named = self._ps_params(args)
        if "path" in named:
            targets = [named["path"]]
        elif pos:
            targets = [pos[0]]
        else:
            targets = []
        self.need(targets, f"PowerShell {name}", stdin_args, allow_empty=name in ("tee-object",))

    def ps_copy(self, args):
        pos, named = self._ps_params(args)
        if "destination" in named:
            self.judge.judge(named["destination"], "PowerShell 복사·이동 목적지")
        elif len(pos) >= 2:
            self.judge.judge(pos[1], "PowerShell 복사·이동 목적지")
        elif "path" in named and pos:
            self.judge.judge(pos[0], "PowerShell 복사·이동 목적지")
        else:
            raise Deny("[bash-write-guard] PowerShell 복사·이동의 목적지를 판정할 수 없다. Write/Edit 툴을 쓰라 (FIX-014).")


# ───────────────────────── 진입점 ─────────────────────────

def _read_input() -> "tuple[str, bool]":
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    d = json.loads(raw)
    ps = str(d.get("tool_name", "")).lower() == "powershell"
    cmd = (d.get("tool_input") or {}).get("command", "")
    return (cmd if isinstance(cmd, str) else ""), ps


def git_fragments(cmd: str, ps: bool) -> list:
    """실행되는 명령의 첫 단어가 git 인 조각을 '단어 단어 …' 한 줄씩 돌려준다."""
    lines = []
    for _frag, words, _x in iter_cmds(cmd, ps):
        if words and _base(words[0].text) == "git":
            lines.append(" ".join(w.text for w in words))
    return lines


def main(argv: list) -> int:
    mode_git = "--git-fragments" in argv
    rest = [a for a in argv[1:] if a != "--git-fragments"]
    root = rest[0] if rest else os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        cmd, ps = _read_input()
    except Exception as e:                                  # 입력을 읽지 못하면 판정 불가
        if mode_git:
            return 0
        print(f"[bash-write-guard] 훅 입력을 해석할 수 없어 검사하지 못했다({type(e).__name__}) — 차단한다.")
        return 1
    if mode_git:
        try:
            for line in git_fragments(cmd, ps):
                print(line)
        except (ParseError, Deny):
            pass                                            # 해석 불가 = 실행된 git 을 확신할 수 없으니 기록하지 않는다
        return 0
    if not cmd.strip():
        return 0
    try:
        WriteChecker(root, ps).check(cmd)
    except Deny as d:
        print(str(d))
        return 1
    except ParseError as e:
        print(f"[bash-write-guard] 명령을 해석할 수 없어({e}) 쓰기 여부를 검사하지 못했다 — 차단한다 (FIX-014).")
        return 1
    except Exception as e:                                  # 예기치 못한 오류도 열지 않는다(fail-closed)
        print(f"[bash-write-guard] 검사 중 예기치 못한 오류({type(e).__name__}: {e}) — 차단한다 (FIX-014).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
