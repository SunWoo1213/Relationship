#!/usr/bin/env python3
"""FIX-034 — 명령을 실행해 그 출력 전체를 evidence 파일로 직접 저장한다.

Refs: FIX-034 FIX-014 FIX-033 R-U3-3 R-U5-3 원칙8

왜 있는가: bash-write-guard(FIX-014)가 프로젝트 안으로의 `>`·`tee` 를 막아, 구현자가 긴 출력을
Read 한 뒤 Write 로 옮겨 적어야 했다. 옮겨 적는 구조가 요약 압력이 되어 증거 규칙 (c) "명령 출력 전체"
미달이 두 단위 연속 재발했다. 이 스크립트는 "프로그램이 스스로 파일을 쓰는 것은 막지 않는다"는
가드 한계(`bash_write_check.py` 모듈 docstring)를 **의도된 통로 하나**로 쓴다 — 옮겨 적기가 사라진다.

쓰는 법:
    python3 .claude/scripts/save_evidence.py <대상> <이름> [--append] [--note "<한 줄>"] [--root <dir>] -- <명령…>

    <대상>  패키지 id(`docs/wiki/packages/<id>/` 가 있어야 함) 또는 `fixes`(→ `docs/wiki/fixes/evidence/`)
    <이름>  `[A-Za-z0-9._-]+` (경로 구분자·`..` 거부)
    파일    `<evidence>/<YYYYMMDD-HHMM>-<이름>.txt`
            `--append` 면 같은 이름의 가장 최근 파일 끝에 구분선과 함께 덧붙인다(변이 루프용).
            `--append` 가 아닌데 같은 분에 같은 이름의 파일이 이미 있으면 덮어쓰지 않고 거부한다(exit 3).
    명령    `--` 뒤 인자를 공백으로 이어 `bash -c` 로 실행(없으면 `sh -c`). cwd 는 저장소 루트.
            환경에 NO_COLOR=1 FORCE_COLOR=0 CI=1 을 더한다. stdout·stderr 는 한 스트림(순서 보존).
    --root  evidence 뿌리를 바꾼다(테스트용): `<root>/<대상>/evidence`. `<root>/<대상>` 이 있어야 한다.

파일 내용: 머리줄 5개(`# 명령:`·`# 시각:`·`# cwd:`·`# HEAD:`·`# exit:`) + `# ---` + 출력 전체.
ANSI 이스케이프(`\\x1b\\[[0-9;?]*[A-Za-z]`)만 지우고 그 밖 바이트는 건드리지 않는다. 자르지 않는다(출력이
8 MB 를 넘으면 머리줄에 `# 크기:` 만 더한다).

종료 코드: 저장 성공이면 **명령의 exit 코드 그대로**(실패한 테스트도 증거로 남고 호출자는 결과를 안다).
2 = 출력에 비밀로 보이는 문자열이 있어 파일을 쓰지 않음(줄 번호·패턴 이름만 stderr, 값은 내지 않는다),
3 = 인자·환경 오류. 명령 자체가 2·3 으로 끝나면 구분할 수 없으니 stderr 의 "저장:" 줄 유무로 판단한다.

비밀 패턴 9개는 `.claude/hooks/secret-guard.sh` 의 PATTERNS 를 그대로 옮긴 것이다.
**둘을 같이 고친다**(정규식 방언만 다르다: POSIX `[[:space:]]` ↔ 여기서는 `\\s`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# secret-guard.sh PATTERNS 와 같은 순서·같은 의미. 둘을 같이 고친다.
SECRET_PATTERNS: list[tuple[str, str]] = [
    ("openai-anthropic-key", r"sk-(proj-|ant-)?[A-Za-z0-9_-]{24,}"),
    ("aws-access-key-id", r"AKIA[0-9A-Z]{16}"),
    ("aws-secret-access-key", r"aws_secret_access_key\s*[=:]\s*[A-Za-z0-9/+]{40}"),
    ("github-token", r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}"),
    ("private-key-block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("slack-token", r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    ("google-api-key", r"AIza[0-9A-Za-z_-]{35}"),
    ("jwt", r"eyJ[A-Za-z0-9_-]{20,}[.][A-Za-z0-9_-]{20,}[.][A-Za-z0-9_-]{20,}"),
    ("db-url-with-password", r"postgres(ql)?://[^:/\s]+:[^@\s]{8,}@"),
]

ANSI_RE = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SIZE_LIMIT = 8 * 1024 * 1024
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # .claude/scripts/ → 저장소 루트


def _git(*args: str) -> str:
    """저장소 루트에서 git 을 실행해 한 줄을 돌려준다. 실패하면 빈 문자열."""
    try:
        r = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=15, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _head_line() -> str:
    short = _git("rev-parse", "--short", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if not short:
        return "(unknown)"
    return f"{short} ({branch or 'unknown'})"


def _valid_token(s: str) -> bool:
    # R-34-3: `.`·`..` 는 정규식을 통과하지만 경로를 접어 범위를 벗어나므로 따로 거부한다.
    return bool(NAME_RE.match(s)) and ".." not in s and s != "."


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _checked_root(raw: str) -> Path | None:
    """`--root` 검사(R-34-3): 절대 경로 + 저장소 밖 + 임시 영역 아래만 허용. 아니면 None."""
    p = Path(raw)
    if not p.is_absolute():
        return None
    rp = p.resolve()
    if _is_under(rp, REPO_ROOT):
        return None
    temps = {"/tmp", "/private/tmp", "/var/tmp", tempfile.gettempdir(), os.environ.get("TMPDIR", "")}
    for t in temps:
        if t and _is_under(rp, Path(t).resolve()):
            return rp
    return None


def _guard_denial(command: str) -> str | None:
    """안쪽 명령을 bash_write_check.py(bash-write-guard 의 판정 본체)에 태운다(R-34-1).

    거부면 가드 메시지를, 허용이면 None. 입력 형식과 종료 코드 해석은 bash-write-guard.sh 와 같다:
    rc != 0 이 거부이고 메시지는 stdout.
    """
    checker = Path(__file__).resolve().parent / "bash_write_check.py"
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, str(checker), str(REPO_ROOT)],
            input=payload.encode("utf-8"),
            capture_output=True,
            env=env,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return f"가드를 실행하지 못해 거부한다({type(e).__name__})"
    if r.returncode == 0:
        return None
    msg = (r.stdout + r.stderr).decode("utf-8", errors="replace").strip()
    return msg or f"가드가 알 수 없는 이유로 거부했다(rc={r.returncode})"


def _evidence_dir(target: str, root_override: Path | None) -> Path | None:
    """대상 → evidence 디렉터리. 대상이 유효하지 않으면 None."""
    if root_override is not None:
        base = root_override / target
        return base / "evidence" if base.is_dir() else None
    if target == "fixes":
        return REPO_ROOT / "docs" / "wiki" / "fixes" / "evidence"
    pkg = REPO_ROOT / "docs" / "wiki" / "packages" / target
    return pkg / "evidence" if pkg.is_dir() else None


def _scan_secrets(text: str) -> list[tuple[int, str]]:
    """(줄 번호, 패턴 이름) 목록. 값은 돌려주지 않는다."""
    hits: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for name, pat in SECRET_PATTERNS:
            if re.search(pat, line):
                hits.append((lineno, name))
    return hits


def _shell() -> str | None:
    return shutil.which("bash") or shutil.which("sh")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        print("save_evidence: '--' 뒤에 실행할 명령이 필요하다", file=sys.stderr)
        return 3
    cut = argv.index("--")
    own, cmd_parts = argv[:cut], argv[cut + 1 :]
    p = argparse.ArgumentParser(prog="save_evidence.py", add_help=True)
    p.add_argument("target")
    p.add_argument("name")
    p.add_argument("--append", action="store_true")
    p.add_argument("--note", default="")
    p.add_argument("--root", default=None)
    try:
        a = p.parse_args(own)
    except SystemExit as e:
        return 3 if e.code else 0
    if not cmd_parts:
        print("save_evidence: 실행할 명령이 비어 있다", file=sys.stderr)
        return 3
    if not _valid_token(a.name):
        print(f"save_evidence: 이름은 [A-Za-z0-9._-]+ 이고 '..' 이 없어야 한다: {a.name!r}", file=sys.stderr)
        return 3
    if not _valid_token(a.target):
        print(f"save_evidence: 대상이 올바르지 않다: {a.target!r}", file=sys.stderr)
        return 3
    root_override: Path | None = None
    if a.root:
        root_override = _checked_root(a.root)
        if root_override is None:
            print(
                f"save_evidence: --root 는 저장소 밖 임시 영역(/tmp·/var/tmp·$TMPDIR 등)의 절대 경로만 허용한다: {a.root!r}",
                file=sys.stderr,
            )
            return 3
    ev_dir = _evidence_dir(a.target, root_override)
    if ev_dir is None:
        print(f"save_evidence: 대상 '{a.target}' 을(를) 찾을 수 없다(패키지 id 또는 fixes)", file=sys.stderr)
        return 3
    shell = _shell()
    if shell is None:
        print("save_evidence: bash 도 sh 도 PATH 에 없다. Git Bash 를 설치하거나 PATH 에 추가하라", file=sys.stderr)
        return 3

    command = " ".join(cmd_parts)

    # R-34-1: 안쪽 명령도 bash-write-guard 와 같은 판정(bash_write_check.py)을 먼저 통과해야 실행한다.
    denied = _guard_denial(command)
    if denied is not None:
        print("save_evidence: 가드(bash_write_check.py)가 안쪽 명령을 거부해 실행하지 않았다:", file=sys.stderr)
        print(denied, file=sys.stderr)
        return 3

    started = datetime.now().astimezone()
    stamp = started.strftime("%Y%m%d-%H%M")
    # R-34-6: 같은 분 충돌은 명령을 실행하기 전에 검사한다(실행 뒤 거부하면 그 출력이 사라진다).
    if not a.append and (ev_dir / f"{stamp}-{a.name}.txt").exists():
        print(
            f"save_evidence: 이미 있다(덮어쓰지 않는다): {ev_dir / f'{stamp}-{a.name}.txt'} — --append 를 쓰거나 이름을 바꿔라",
            file=sys.stderr,
        )
        return 3

    env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="0", CI="1")
    res = subprocess.run(
        [shell, "-c", command],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        check=False,
    )
    rc = res.returncode if res.returncode >= 0 else 128 - res.returncode
    body = ANSI_RE.sub(b"", res.stdout)

    head = [
        f"# 명령: {command}",
        f"# 시각: {started.isoformat(timespec='seconds')}",
        f"# cwd: {REPO_ROOT}",
        f"# HEAD: {_head_line()}",
        f"# exit: {rc}",
    ]
    if a.note:
        head.append(f"# 메모: {a.note}")
    if len(body) > SIZE_LIMIT:
        head.append(f"# 크기: {len(body)} bytes (8 MB 초과)")
    head.append("# ---")
    # R-34-5: 머리줄(명령·--note)도 ANSI 를 지운 뒤 검사·저장한다(ANSI 로 쪼갠 비밀이 검사를 지나지 못하게).
    head_bytes = ANSI_RE.sub(b"", ("\n".join(head) + "\n").encode("utf-8"))

    hits = _scan_secrets((head_bytes + body).decode("utf-8", errors="replace"))
    if hits:
        print("save_evidence: 비밀로 보이는 문자열이 있어 파일을 쓰지 않았다(값은 출력하지 않는다):", file=sys.stderr)
        for lineno, name in hits:
            print(f"  줄 {lineno}: {name}", file=sys.stderr)
        return 2

    ev_dir.mkdir(parents=True, exist_ok=True)
    if a.append:
        # R-34-2: 접미사가 겹치는 다른 이름(`…-u5-mutation.txt`)을 고르지 않도록 fullmatch 로만 거른다.
        name_re = re.compile(r"\d{8}-\d{4}-" + re.escape(a.name) + r"\.txt")
        existing = sorted(
            (f for f in ev_dir.iterdir() if f.is_file() and name_re.fullmatch(f.name)),
            key=lambda f: (f.name, f.stat().st_mtime),
        )
        path = existing[-1] if existing else ev_dir / f"{stamp}-{a.name}.txt"
        sep = f"\n# ===== append {started.isoformat(timespec='seconds')} =====\n".encode("utf-8")
        with open(path, "ab") as fh:
            fh.write(sep + head_bytes + body)
    else:
        path = ev_dir / f"{stamp}-{a.name}.txt"
        with open(path, "wb") as fh:
            fh.write(head_bytes + body)

    print(f"저장: {path}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
