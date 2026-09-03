#!/usr/bin/env bash
# PreToolUse(Agent) 훅 — 단계 위임 게이트 (L-004)
#
# 계획(architect)·구현(backend-agent, eval-agent)·검증(verifier) 단계는 자동으로 시작하지 않는다.
# 메인 세션이 AskUserQuestion 으로 사용자에게 "시작할까요?"를 묻고, 승인 직후
#   bash .claude/hooks/approve-commit.sh --stage <agent-name>
# 로 1회용 마커(.claude/.stage-approved, 내용 = 에이전트 이름)를 만든 뒤에만 그 에이전트를 띄울 수 있다.
# 마커는 허용과 동시에 지운다(위임 1건 = 승인 1건). 다른 에이전트(Explore, claude-code-guide 등)는 게이트 대상이 아니다.
#
# stdin: {"tool_name":"Agent","tool_input":{"subagent_type":"...","description":"...","prompt":"..."}}
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
MARK="$ROOT/.claude/.stage-approved"
GATED="architect backend-agent eval-agent verifier"

input="$(cat)"
sub="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("subagent_type","") or "")
except Exception:
    print("")' 2>/dev/null)"
[ -n "$sub" ] || exit 0

deny() {
  reason="$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

gated=0
for g in $GATED; do [ "$sub" = "$g" ] && gated=1; done
[ "$gated" -eq 1 ] || exit 0

if [ ! -f "$MARK" ]; then
  deny "[delegate-guard] '$sub' 단계는 자동으로 시작하지 않는다 (L-004). AskUserQuestion 으로 사용자에게 시작 여부를 묻고, 승인 직후 bash .claude/hooks/approve-commit.sh --stage $sub 를 실행한 뒤 위임하라."
fi
approved="$(head -n1 "$MARK" | tr -d '[:space:]\r')"
if [ "$approved" != "$sub" ]; then
  deny "[delegate-guard] 승인된 단계는 '$approved' 인데 '$sub' 를 띄우려 한다 (L-004). 사용자에게 다시 묻고 approve-commit.sh --stage $sub 로 승인하라."
fi
rm -f "$MARK"   # 1회용
exit 0
