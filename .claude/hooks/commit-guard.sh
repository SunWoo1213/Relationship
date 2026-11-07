#!/usr/bin/env bash
# PreToolUse(Bash) 훅 — git commit 가드
#
# 규칙 (L-006, 2026-11-07: 사용자 승인 마커 폐지 — 커밋은 자동, 형식·검증 게이트만 남긴다):
#   1. 커밋 메시지는 초안 파일(.claude/commit-draft.txt)로만 전달 (-F) — 메시지 형식·journal 기록의 기준
#   2. --amend / --no-verify 금지
#   3. git commit 인자는 `-F <초안>` 뿐 (허용 목록, F-27-5) · GIT_* 환경변수 접두 금지 (R-27-8)
#   4. fix(FIX-nnn)/test(FIX-nnn) 초안이 app/·alembic/·web/ 을 스테이징했으면
#      verifier 검증 줄 + review-FIX-nnn.md 가 있어야 허용 (FIX-027) — 사람 승인이 아니라 자동 검증 게이트라 유지
#
# 폐지된 것: 승인 마커(.claude/.commit-approved)·초안 해시 비교·L-003 dev 푸시 뒤 대기(.awaiting-decision).
#
# stdin: {"tool_name":"Bash","tool_input":{"command":"..."}}
# stdout: permissionDecision JSON (deny 일 때만). 허용이면 아무것도 출력하지 않음.

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT_REL=".claude/commit-draft.txt"
DRAFT="$ROOT/$DRAFT_REL"

# 파이썬 인터프리터 탐지 (FIX-008). 못 찾으면 통과시키지 않고 차단한다.
. "$(dirname "$0")/_py.sh"
if [ -z "$HOOK_PY" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[commit-guard] %s"}}\n' "$HOOK_PY_MISSING_MSG"
  exit 0
fi

input="$(cat)"
cmd="$(printf '%s' "$input" | "$HOOK_PY" -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"

deny() {
  # F-27-2: 파이썬 json.dumps 는 reason 이 몇 줄이든·어떤 문자든 항상 유효한 JSON 한 줄을 만든다.
  printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
reason = sys.stdin.read()
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":reason}}))'
  exit 0
}

[ -n "$cmd" ] || exit 0

# git commit 감지 (git -C x commit, cd .. && git commit 등 포함)
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)'; then
  case "$cmd" in
    *"--amend"*)     deny "--amend 는 허용하지 않는다. 새 커밋으로 만들어라." ;;
    *"--no-verify"*) deny "--no-verify 는 허용하지 않는다." ;;
  esac

  # F-27-3/F-27-5: 규칙 4(제품 코드 verifier 게이트)는 `git diff --cached` 만 본다. -a/--all·pathspec 등으로
  # git add 없이 커밋 대상을 늘리면 거짓 통과하므로, `git commit` 뒤 인자는 `-F <초안>` 만 허용한다
  # (판정은 commit_args_check.py). R-27-8: GIT_* 환경변수 접두는 훅이 보는 색인과 커밋 색인을 갈라놓으므로 거부.
  if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])GIT_[A-Z_]+='; then
    deny "GIT_* 환경변수 접두(예: GIT_INDEX_FILE=…)가 붙은 git commit 은 허용하지 않는다. 훅이 검사한 색인과 실제 커밋 색인이 달라질 수 있다."
  fi
  args_out="$(printf '%s' "$cmd" | "$HOOK_PY" "$(dirname "$0")/../scripts/commit_args_check.py" 2>&1)"
  args_rc=$?
  if [ "$args_rc" -ne 0 ]; then
    [ -n "$args_out" ] || args_out="git commit 인자 검사 중 알 수 없는 오류(rc=$args_rc) — 거부한다."
    deny "$args_out"
  fi

  [ -f "$DRAFT" ] || deny "커밋 초안($DRAFT_REL)이 없다. /commit 스킬 형식으로 초안을 쓴 뒤 git commit -F $DRAFT_REL 로 커밋하라."
  [ -s "$DRAFT" ] || deny "커밋 초안($DRAFT_REL)이 비어 있다."
  case "$cmd" in
    *"-F $DRAFT_REL"*|*"-F \"$DRAFT_REL\""*|*"--file=$DRAFT_REL"*|*"--file=\"$DRAFT_REL\""*|*"--file $DRAFT_REL"*|*"--file \"$DRAFT_REL\""*) ;;
    *) deny "커밋 메시지는 초안 파일로만 전달한다: git commit -F $DRAFT_REL" ;;
  esac

  # 4. FIX-027: 제품 코드(app/·alembic/·web/)를 바꾸는 fix(FIX-nnn)/test(FIX-nnn) 커밋은
  #    verifier 검증(`검증:` 줄)·커밋 전 리뷰 문서(review-FIX-nnn.md)가 먼저다. 판단 불가도 거부(fail-closed).
  #    스크립트 위치는 훅 디렉터리 기준($0) — $ROOT 는 테스트에서 다른 저장소를 가리킬 수 있다.
  fix_guard_out="$("$HOOK_PY" "$(dirname "$0")/../scripts/fix_guard_check.py" "$ROOT" "$DRAFT" 2>&1)"
  fix_guard_rc=$?
  if [ "$fix_guard_rc" -ne 0 ]; then
    [ -n "$fix_guard_out" ] || fix_guard_out="[fix-guard] FIX 검증 확인 중 알 수 없는 오류(rc=$fix_guard_rc)."
    deny "$fix_guard_out"
  fi
fi

exit 0
