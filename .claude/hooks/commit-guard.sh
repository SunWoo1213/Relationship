#!/usr/bin/env bash
# PreToolUse(Bash) 훅 — git commit 승인 가드
#
# 규칙:
#   1. git commit 은 승인 마커(.claude/.commit-approved)가 있을 때만 허용
#   2. 커밋 메시지는 승인된 초안 파일(.claude/commit-draft.txt)로만 전달 (-F)
#   3. 마커의 해시와 초안 파일의 해시가 같아야 함 (승인 후 초안 변경 금지)
#   4. --amend / --no-verify 금지
#   5. 마커 파일을 직접 만들거나 지우는 명령 금지 (approve-commit.sh 만 허용)
#
# stdin: {"tool_name":"Bash","tool_input":{"command":"..."}}
# stdout: permissionDecision JSON (deny 일 때만). 허용이면 아무것도 출력하지 않음.

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT_REL=".claude/commit-draft.txt"
DRAFT="$ROOT/$DRAFT_REL"
MARK="$ROOT/.claude/.commit-approved"

input="$(cat)"
cmd="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"

deny() {
  # JSON 문자열 이스케이프 최소 처리
  reason="$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

[ -n "$cmd" ] || exit 0

# L-003: dev 푸시 후 사용자 결정 전에는 새 커밋 금지
AWAIT="$ROOT/.claude/.awaiting-decision"
if [ -f "$AWAIT" ] && printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)'; then
  deny "dev 푸시 후 사용자 결정(main 승격 / 수정) 대기 중이라 새 커밋을 만들 수 없다 (L-003). AskUserQuestion 으로 결정을 받고 approve-commit.sh --release 또는 --decision fix 를 실행하라."
fi

# 5. 마커 직접 조작 금지
case "$cmd" in
  *".commit-approved"*) deny "commit 승인 마커는 직접 조작할 수 없다. /commit 절차(초안 → 사용자 승인 → approve-commit.sh)를 따르라." ;;
esac

# git commit 감지 (git -C x commit, cd .. && git commit 등 포함)
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)'; then
  case "$cmd" in
    *"--amend"*)     deny "--amend 는 승인 절차에서 허용하지 않는다. 새 커밋으로 만들어라." ;;
    *"--no-verify"*) deny "--no-verify 는 허용하지 않는다." ;;
  esac
  [ -f "$MARK" ]  || deny "승인 마커가 없다. /commit 스킬로 초안을 만들고 사용자 승인을 받은 뒤 커밋하라."
  [ -f "$DRAFT" ] || deny "커밋 초안($DRAFT_REL)이 없다. /commit 스킬을 따르라."
  case "$cmd" in
    *"-F $DRAFT_REL"*|*"-F \"$DRAFT_REL\""*|*"--file=$DRAFT_REL"*|*"--file $DRAFT_REL"*) ;;
    *) deny "커밋 메시지는 승인된 초안 파일로만 전달한다: git commit -F $DRAFT_REL" ;;
  esac
  want="$(cat "$MARK" 2>/dev/null | tr -d '[:space:]')"
  have="$(sha256sum "$DRAFT" | cut -d' ' -f1)"
  [ "$want" = "$have" ] || deny "초안이 승인 이후에 바뀌었다. 초안을 다시 보여주고 재승인을 받아라."
fi

exit 0
