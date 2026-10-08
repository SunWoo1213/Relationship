#!/usr/bin/env bash
# PreToolUse(Bash) 훅 — git commit 승인 가드
#
# 규칙:
#   1. git commit 은 승인 마커(.claude/.commit-approved)가 있을 때만 허용
#   2. 커밋 메시지는 승인된 초안 파일(.claude/commit-draft.txt)로만 전달 (-F)
#   3. 마커의 해시와 초안 파일의 해시가 같아야 함 (승인 후 초안 변경 금지)
#   4. --amend / --no-verify 금지
#   5. 마커 파일을 직접 만들거나 지우는 명령 금지 (approve-commit.sh 만 허용)
#   5b. git commit 인자는 `-F <초안>` 뿐 (허용 목록, F-27-5) · GIT_* 환경변수 접두 금지 (R-27-8)
#   6. fix(FIX-nnn)/test(FIX-nnn) 초안이 app/·alembic/ 을 스테이징했으면
#      verifier 검증 줄 + review-FIX-nnn.md 가 있어야 허용 (FIX-027)
#
# stdin: {"tool_name":"Bash","tool_input":{"command":"..."}}
# stdout: permissionDecision JSON (deny 일 때만). 허용이면 아무것도 출력하지 않음.

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT_REL=".claude/commit-draft.txt"
DRAFT="$ROOT/$DRAFT_REL"
MARK="$ROOT/.claude/.commit-approved"

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
  # F-27-2: sed 로 \ 와 " 만 이스케이프하면 줄바꿈·제어문자가 그대로 남아 깨진 JSON 을
  # 낼 수 있었다(여러 줄 Traceback 이 이유 문자열에 그대로 들어간 사례, fail-closed 가
  # 아니라 실제로는 fail-open). 파이썬 json.dumps 는 reason 이 몇 줄이든·어떤 문자든
  # 항상 유효한 JSON 한 줄을 만든다 — 이 함수를 쓰는 모든 규칙(1~6)에 공통 적용된다.
  printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
reason = sys.stdin.read()
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":reason}}))'
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

  # F-27-3: 규칙 6(제품 코드 verifier 게이트)은 `git diff --cached` 만 본다. -a/--all 로
  # 미스테이징 변경을 끼워 넣거나, -i/--include·-o/--only·pathspec(커밋 명령 뒤에 경로를
  # 더 붙이는 것)으로 git add 없이 커밋 대상을 늘리면 "스테이징된 파일에 app/ 없음" 으로
  # 거짓 통과한다. 커밋 대상은 git add 로 미리 정한 것으로만 제한한다.
  #
  # F-27-5: 1차 재작업은 "막을 것을 나열"(-a 류 + `-F <초안>` 뒤 경로)이라 `--file=<초안> 경로`,
  # `경로 -F <초안>`, `--pathspec-from-file` 이 열려 있었다. 이제 **허용 목록**이다 —
  # `git commit` 뒤 인자가 `-F|--file[=| ]<초안>` 뿐이어야 하고 그 밖은 전부 거부한다
  # (판정은 commit_args_check.py 의 토큰 파서; 전역 옵션 `-c k=v`·`-C dir` 도 건너뛰어 처리).
  # R-27-8: `GIT_INDEX_FILE=… git commit` 같은 GIT_* 환경변수 접두는 훅이 보는 색인과 커밋이
  # 쓰는 색인을 갈라놓으므로 거부한다.
  if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])GIT_[A-Z_]+='; then
    deny "GIT_* 환경변수 접두(예: GIT_INDEX_FILE=…)가 붙은 git commit 은 허용하지 않는다. 훅이 검사한 색인과 실제 커밋 색인이 달라질 수 있다."
  fi
  args_out="$(printf '%s' "$cmd" | "$HOOK_PY" "$(dirname "$0")/../scripts/commit_args_check.py" 2>&1)"
  args_rc=$?
  if [ "$args_rc" -ne 0 ]; then
    [ -n "$args_out" ] || args_out="git commit 인자 검사 중 알 수 없는 오류(rc=$args_rc) — 거부한다."
    deny "$args_out"
  fi

  [ -f "$MARK" ]  || deny "승인 마커가 없다. /commit 스킬로 초안을 만들고 사용자 승인을 받은 뒤 커밋하라."
  [ -f "$DRAFT" ] || deny "커밋 초안($DRAFT_REL)이 없다. /commit 스킬을 따르라."
  case "$cmd" in
    *"-F $DRAFT_REL"*|*"-F \"$DRAFT_REL\""*|*"--file=$DRAFT_REL"*|*"--file=\"$DRAFT_REL\""*|*"--file $DRAFT_REL"*|*"--file \"$DRAFT_REL\""*) ;;
    *) deny "커밋 메시지는 승인된 초안 파일로만 전달한다: git commit -F $DRAFT_REL" ;;
  esac
  want="$(cat "$MARK" 2>/dev/null | tr -d '[:space:]')"
  have="$(sha256sum "$DRAFT" | cut -d' ' -f1)"
  [ "$want" = "$have" ] || deny "초안이 승인 이후에 바뀌었다. 초안을 다시 보여주고 재승인을 받아라."

  # 6. FIX-027: 제품 코드(app/·alembic/)를 바꾸는 fix(FIX-nnn)/test(FIX-nnn) 커밋은
  #    verifier 검증(`검증:` 줄)·커밋 전 리뷰 문서(review-FIX-nnn.md)가 먼저다.
  #    판단 불가(파이썬·git 실패)도 거부 — 조용히 여는 것이 결함이다(fail-closed).
  # 스크립트 자신의 위치는 _py.sh 처럼 훅 디렉터리 기준(= $0)으로 찾는다 — $ROOT는
  # 테스트에서 CLAUDE_PROJECT_DIR 로 다른 저장소를 가리킬 수 있어, 스크립트 파일 자체를
  # 찾는 데 쓰면 그 임시 저장소 안에서 못 찾는다(스크립트는 항상 이 훅과 함께 있다).
  fix_guard_out="$("$HOOK_PY" "$(dirname "$0")/../scripts/fix_guard_check.py" "$ROOT" "$DRAFT" 2>&1)"
  fix_guard_rc=$?
  if [ "$fix_guard_rc" -ne 0 ]; then
    [ -n "$fix_guard_out" ] || fix_guard_out="[fix-guard] FIX 검증 확인 중 알 수 없는 오류(rc=$fix_guard_rc)."
    deny "$fix_guard_out"
  fi
fi

exit 0
