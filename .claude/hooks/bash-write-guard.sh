#!/usr/bin/env bash
# PreToolUse(Bash|PowerShell) 훅 — 프로젝트 안 파일을 Bash/PowerShell 로 쓰는 것을 거부한다 (FIX-014)
#
# 왜 필요한가:
#   stage-gate.sh·secret-guard.sh 는 Write/Edit 의 tool_input.file_path·content 만 읽는다.
#   Bash 호출에는 그 필드가 없어, `cat > app/x.py <<EOF`·`sed -i`·`tee`·python 인라인 쓰기가
#   활성 작업 게이트·기획서 동결·L-003 잠금·비밀 검사를 전부 지나갔다. 이 훅이 그 사각을 닫는다.
#   방식은 "경로를 뽑아 기존 가드에 태우기"(셸 파싱 복잡·미탐 위험)가 아니라 "프로젝트 안 Bash 쓰기 거부"
#   (사용자 결정 2026-10-11)다 — 프로젝트 파일은 Write/Edit 툴로 쓰게 유도한다.
#
# 판정 본체는 .claude/scripts/bash_write_check.py (명령을 따옴표·;·&&·||·|·줄바꿈·heredoc·치환 단위로
# 쪼개 쓰기 형태와 대상 경로를 본다). 임시 영역(/tmp·$TMPDIR·스크래치패드·/dev/null)은 허용,
# 프로젝트 안은 거부, 경로를 판정할 수 없으면 차단(security.md "검사할 수 없으면 통과가 아니라 차단").
# 한계(의도): pytest·pip·npm·alembic·`python x.py`·git 하위 명령처럼 프로그램이 스스로 파일을 쓰는 것은 막지 않는다.
#
# stdin: {"tool_name":"Bash"|"PowerShell","tool_input":{"command":"..."}}
# stdout: permissionDecision JSON (deny 일 때만). 허용이면 아무것도 출력하지 않음.

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# 파이썬 인터프리터 탐지 (FIX-008). 못 찾으면 통과시키지 않고 차단한다.
HOOK_PY=""
. "$(dirname "$0")/_py.sh" 2>/dev/null
if [ -z "${HOOK_PY:-}" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[bash-write-guard] %s"}}\n' "${HOOK_PY_MISSING_MSG:-파이썬 인터프리터를 찾지 못해 검사할 수 없다 - FIX-008}"
  exit 0
fi

deny() {
  # 사유가 몇 줄이든 어떤 문자든 json.dumps 로 항상 유효한 JSON 한 줄을 만든다 (commit-guard F-27-2 와 같은 방식)
  printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
reason = sys.stdin.read()
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":reason}}))'
  exit 0
}

input="$(cat)"
out="$(printf '%s' "$input" | "$HOOK_PY" "$(dirname "$0")/../scripts/bash_write_check.py" "$ROOT" 2>&1)"
rc=$?
if [ "$rc" -ne 0 ]; then
  [ -n "$out" ] || out="[bash-write-guard] Bash 쓰기 검사 중 알 수 없는 오류(rc=$rc) - 차단한다 (FIX-014)."
  deny "$out"
fi

exit 0
