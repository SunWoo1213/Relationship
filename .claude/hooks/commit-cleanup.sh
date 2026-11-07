#!/usr/bin/env bash
# PostToolUse(Bash) 훅 — git commit·push 가 실제로 일어났으면 docs/wiki/journal.md 에 한 줄 남기고
# git log 스냅샷(.claude/gitlog.md)을 갱신한다.
#
# L-006(2026-11-07): 승인 마커(.commit-approved·.push-approved·.release-approved)와 L-003 대기 마커
# (.awaiting-decision)는 폐지됐다. 이 훅은 더는 마커를 만들거나 지우지 않는다 — 기록만 한다.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT="$ROOT/.claude/commit-draft.txt"
JOURNAL="$ROOT/docs/wiki/journal.md"

# 파이썬 인터프리터 탐지 (FIX-008). PostToolUse 라 차단 권한이 없으므로 경고만 하고 통과한다.
. "$(dirname "$0")/_py.sh"
[ -n "$HOOK_PY" ] || printf '%s\n' "[commit-cleanup] $HOOK_PY_MISSING_MSG" >&2

input="$(cat)"

# 결함 ② (FIX-014): 명령 문자열이 아니라 **실제로 실행되는 git 조각**만 본다.
#   따옴표·;·&&·||·|·줄바꿈·heredoc·치환 단위로 쪼갠 뒤 첫 단어가 git 인 조각만 모은다(gitcmd, 한 줄에 조각 하나).
#   판정 스크립트가 없거나 해석에 실패하면 gitcmd 가 비어 아무 일도 하지 않는다(가짜 기록보다 기록 누락이 안전).
gitcmd="$(printf '%s' "$input" | ${HOOK_PY:-false} "$(dirname "$0")/../scripts/bash_write_check.py" --git-fragments 2>/dev/null)"

# 한 명령이 두 가지 일을 할 수 있다 (FIX-013) — 해당되는 처리를 **전부** 한다. 커밋을 먼저 처리해
# journal 줄이 실제 순서(커밋 → 푸시)대로 남게 한다.

# ── 커밋 처리 ── HEAD 커밋 제목이 초안 첫 줄과 같으면 커밋 성공으로 본다
if printf '%s' "$gitcmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)' \
   && [ -f "$DRAFT" ]; then
  head_subject="$(git -C "$ROOT" log -1 --format=%s 2>/dev/null || true)"
  draft_subject="$(head -n1 "$DRAFT" | tr -d '\r')"
  if [ -n "$head_subject" ] && [ "$head_subject" = "$draft_subject" ]; then
    hash="$(git -C "$ROOT" log -1 --format=%h 2>/dev/null || true)"
    if [ -f "$JOURNAL" ]; then
      printf -- '- %s | COMMIT | %s %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$hash" "$draft_subject" >> "$JOURNAL"
    fi
    # git log 스냅샷 갱신 (L-001) — 에이전트가 최신 커밋을 .claude/gitlog.md 로 본다
    [ -f "$ROOT/.claude/scripts/gitlog.sh" ] && bash "$ROOT/.claude/scripts/gitlog.sh" --write 2>/dev/null || true
  fi
fi

# ── 푸시 처리 ── 성공 판정: 원격 추적 ref 가 HEAD(또는 dev)와 같아졌는가. 실패한 푸시는 기록하지 않는다(FIX-009).
if printf '%s' "$gitcmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+push([[:space:]]|$)'; then
  # if/elif 사슬 — 한 명령에 푸시가 둘이면 더 구체적인 갈래 하나만 탄다(배타).
  if printf '%s' "$gitcmd" | grep -Eq 'origin[[:space:]]+dev:main([[:space:]]|$)'; then
    git -C "$ROOT" fetch -q origin main 2>/dev/null || true
    if [ "$(git -C "$ROOT" rev-parse origin/main 2>/dev/null)" = "$(git -C "$ROOT" rev-parse dev 2>/dev/null)" ]; then
      [ -f "$JOURNAL" ] && printf -- '- %s | RELEASE | origin main ← dev %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short dev 2>/dev/null || true)" >> "$JOURNAL"
    fi
  elif printf '%s' "$gitcmd" | grep -Eq 'origin[[:space:]]+dev2:dev([[:space:]]|$)'; then
    if [ "$(git -C "$ROOT" rev-parse origin/dev 2>/dev/null)" = "$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" ]; then
      [ -f "$JOURNAL" ] && printf -- '- %s | PUSH | origin dev ← dev2 %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)" >> "$JOURNAL"
    fi
  elif printf '%s' "$gitcmd" | grep -Eq 'origin[[:space:]]+dev2([[:space:]]|$)'; then
    if [ "$(git -C "$ROOT" rev-parse origin/dev2 2>/dev/null)" = "$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" ]; then
      [ -f "$JOURNAL" ] && printf -- '- %s | PUSH-dev2 | origin dev2 %s (실험 푸시)\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)" >> "$JOURNAL"
    fi
  fi
fi
exit 0
