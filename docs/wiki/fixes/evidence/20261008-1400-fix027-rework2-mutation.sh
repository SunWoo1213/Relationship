#!/usr/bin/env bash
# FIX-027 2차 재작업 변이 시험 — F-27-5 허용 목록 검사(commit_args_check.py)를 복사본에서 무력화(항상 exit 0)하면
# 마커·초안이 있는 격리 저장소의 DENY 케이스가 allow 로 뒤집히는가(= 케이스가 검사를 실제로 본다).
# 또 F-27-6 판정(_verification_line_ok)을 옛 정규식으로 되돌린 복사본에서 신규 케이스가 뒤집히는가.
# 원본 파일은 건드리지 않는다(복사본만 변이).
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
PROJ="/Users/sunwoo/Desktop/Portfolio/Relationship"
H="$PROJ/.claude/hooks"
. "$H/_py.sh"
mk() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'command':sys.argv[1]}}))" "$1"; }

setup_copy() {  # setup_copy <dir>  — 훅·스크립트 복사
  mkdir -p "$1/.claude/hooks" "$1/.claude/scripts"
  cp "$H/commit-guard.sh" "$H/_py.sh" "$1/.claude/hooks/"
  cp "$PROJ/.claude/scripts/fix_guard_check.py" "$PROJ/.claude/scripts/commit_args_check.py" "$1/.claude/scripts/"
}
setup_repo() {  # setup_repo <dir> <초안 첫 줄>
  mkdir -p "$1/.claude" "$1/app" "$1/docs/wiki/fixes"
  ( cd "$1" && git init -q . && git config user.email t@example.com && git config user.name tester \
    && printf 'init\n' > README.md && git add README.md && git commit -qm init \
    && printf 'x\n' > app/a.py && git add app/a.py ) >/dev/null 2>&1
  printf '%s\n\n본문\n' "$2" > "$1/.claude/commit-draft.txt"
  "$HOOK_PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1/.claude/commit-draft.txt" > "$1/.claude/.commit-approved"
}
verdict() { if [ -z "$1" ]; then echo allow; else echo DENY; fi; }

D='.claude/commit-draft.txt'
CASES=("git commit -a -F $D" "git commit -F $D app/a.py" "git commit --file=$D app/a.py" "git commit app/a.py -F $D" \
       "git commit --file $D app/a.py" "git commit --pathspec-from-file=p -F $D" "git commit --include app/a.py -F $D")

echo "== 변이 1: F-27-5 검사 무력화 (commit_args_check.py -> exit 0) =="
M="$(mktemp -d)"; T="$(mktemp -d)"
setup_copy "$M"; printf 'import sys\nsys.exit(0)\n' > "$M/.claude/scripts/commit_args_check.py"
setup_repo "$T" 'feat(P7-push): 변이'
printf '%-62s %-10s %-10s\n' "명령" "원본 훅" "변이 훅"
for c in "${CASES[@]}"; do
  o="$(verdict "$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh")")"
  m="$(verdict "$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$M/.claude/hooks/commit-guard.sh")")"
  printf '%-62s %-10s %-10s %s\n' "$c" "$o" "$m" "$([ "$o" = DENY ] && [ "$m" = allow ] && echo '뒤집힘(케이스 유효)' || echo '!! 뒤집히지 않음')"
done
rm -rf "$M" "$T"

echo
echo "== 변이 2: F-27-6 판정을 옛 정규식(^검증:\\s*통과\\b.*verifier, 한 줄만 맞으면 통과)으로 되돌림 =="
M="$(mktemp -d)"; T="$(mktemp -d)"
setup_copy "$M"
"$HOOK_PY" - "$M/.claude/scripts/fix_guard_check.py" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace("    return bool(VERDICT_RE.match(line)) and not NEGATION_RE.search(line)", "    return bool(re.match(r'^검증:\\s*통과\\b.*verifier', line, re.I))")
s = s.replace("    if len(verdict_lines) != 1:\n        return False\n    line = verdict_lines[0]", "    if not verdict_lines:\n        return False\n    line = next((l for l in verdict_lines if re.match(r'^검증:\\s*통과\\b.*verifier', l, re.I)), verdict_lines[0])")
open(p, "w", encoding="utf-8").write(s)
PY
setup_repo "$T" 'fix(FIX-999): 변이'
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
run_fix() { printf '%s' "$(mk "git commit -F $D")" | CLAUDE_PROJECT_DIR="$T" bash "$1"; }
for body in '검증: 통과 — 메인 세션 (verifier 생략)' '검증: 통과 — verifier 리뷰 생략(문서만)' '검증: (verifier 가 쓴다)\n검증: 통과 — verifier (fable)'; do
  printf "$body\n" > "$T/docs/wiki/fixes/FIX-999.md"
  o="$(verdict "$(run_fix "$H/commit-guard.sh")")"; m="$(verdict "$(run_fix "$M/.claude/hooks/commit-guard.sh")")"
  printf '%-58s 원본 %-6s 변이 %-6s %s\n' "$body" "$o" "$m" "$([ "$o" = DENY ] && [ "$m" = allow ] && echo '뒤집힘(케이스 유효)' || echo '!! 뒤집히지 않음')"
done
rm -rf "$M" "$T"
