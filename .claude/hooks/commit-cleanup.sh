#!/usr/bin/env bash
# PostToolUse(Bash) 훅 — git commit 이 실제로 일어났으면 승인 마커를 지운다 (승인은 1회용).
# 커밋 기록을 docs/wiki/journal.md 에 한 줄 남긴다.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT="$ROOT/.claude/commit-draft.txt"
MARK="$ROOT/.claude/.commit-approved"
JOURNAL="$ROOT/docs/wiki/journal.md"

input="$(cat)"
cmd="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"

PUSH_MARK="$ROOT/.claude/.push-approved"
# 푸시가 일어났으면 푸시 마커를 지운다 (1회용)
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+push([[:space:]]|$)'; then
  if [ -f "$PUSH_MARK" ] && git -C "$ROOT" status -sb 2>/dev/null | head -n1 | grep -Evq 'ahead'; then
    rm -f "$PUSH_MARK"
    if [ -f "$JOURNAL" ]; then
      printf -- '- %s | PUSH | origin %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)" >> "$JOURNAL"
    fi
  fi
  exit 0
fi

printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)' || exit 0
[ -f "$MARK" ] || exit 0
[ -f "$DRAFT" ] || exit 0

# HEAD 커밋 제목이 초안 첫 줄과 같으면 커밋 성공으로 본다
head_subject="$(git -C "$ROOT" log -1 --format=%s 2>/dev/null || true)"
draft_subject="$(head -n1 "$DRAFT" | tr -d '\r')"
if [ -n "$head_subject" ] && [ "$head_subject" = "$draft_subject" ]; then
  rm -f "$MARK"
  hash="$(git -C "$ROOT" log -1 --format=%h 2>/dev/null || true)"
  if [ -f "$JOURNAL" ]; then
    printf -- '- %s | COMMIT | %s %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$hash" "$draft_subject" >> "$JOURNAL"
  fi
fi
exit 0
