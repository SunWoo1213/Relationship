#!/usr/bin/env bash
# PostToolUse(Bash) 훅 — git commit 이 실제로 일어났으면 승인 마커를 지운다 (승인은 1회용).
# 커밋 기록을 docs/wiki/journal.md 에 한 줄 남긴다.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT="$ROOT/.claude/commit-draft.txt"
MARK="$ROOT/.claude/.commit-approved"
JOURNAL="$ROOT/docs/wiki/journal.md"

# 파이썬 인터프리터 탐지 (FIX-008). PostToolUse 라 차단 권한이 없으므로 경고만 하고 통과한다.
. "$(dirname "$0")/_py.sh"
[ -n "$HOOK_PY" ] || printf '%s\n' "[commit-cleanup] $HOOK_PY_MISSING_MSG" >&2

input="$(cat)"
cmd="$(printf '%s' "$input" | ${HOOK_PY:-false} -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"

PUSH_MARK="$ROOT/.claude/.push-approved"
RELEASE_MARK="$ROOT/.claude/.release-approved"
AWAIT="$ROOT/.claude/.awaiting-decision"

# 한 명령이 두 가지 일을 할 수 있다 (FIX-013).
#   전에는 "이 명령이 무엇인가" 를 하나만 골랐다. 푸시가 보이면 푸시 갈래에서 exit 0 했고,
#   커밋 처리는 그 아래에 있어 도달하지 못했다. 그래서 `commit && push` 한 줄에서
#   승인 마커가 소비되지 않고 남고, journal 의 COMMIT 줄과 gitlog 갱신이 통째로 빠졌다
#   (커밋 0c46913 에서 실제 발생). 지금은 해당되는 처리를 **전부** 한다.
#   커밋을 먼저 처리하는 것은 journal 줄이 실제로 일어난 순서(커밋 → 푸시)대로 남게 하려는
#   것뿐이다. 이 훅은 PostToolUse 라 명령 전체가 끝난 뒤 한 번 돌고, 어느 블록을 먼저
#   돌리든 rev-parse 는 같은 시점을 본다 — 순서는 판정의 정확성에 영향이 없다.

# ── 커밋 처리 ── 승인 마커는 1회용이므로 실제로 커밋됐을 때만 소비한다.
#   세 조건을 블록으로 묶는다. 전에는 `|| exit 0` 세 줄이었는데, 커밋 처리를 앞으로
#   옮기면서 그대로 두면 커밋 조건이 안 맞는 명령에서 아래 푸시 처리까지 끊긴다.
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+commit([[:space:]]|$)' \
   && [ -f "$MARK" ] && [ -f "$DRAFT" ]; then
  # HEAD 커밋 제목이 초안 첫 줄과 같으면 커밋 성공으로 본다
  head_subject="$(git -C "$ROOT" log -1 --format=%s 2>/dev/null || true)"
  draft_subject="$(head -n1 "$DRAFT" | tr -d '\r')"
  if [ -n "$head_subject" ] && [ "$head_subject" = "$draft_subject" ]; then
    rm -f "$MARK"
    hash="$(git -C "$ROOT" log -1 --format=%h 2>/dev/null || true)"
    if [ -f "$JOURNAL" ]; then
      printf -- '- %s | COMMIT | %s %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$hash" "$draft_subject" >> "$JOURNAL"
    fi
    # git log 스냅샷 갱신 (L-001) — 에이전트가 최신 커밋을 .claude/gitlog.md 로 본다
    [ -f "$ROOT/.claude/scripts/gitlog.sh" ] && bash "$ROOT/.claude/scripts/gitlog.sh" --write 2>/dev/null || true
  fi
fi

# ── 푸시 처리 ── 푸시가 일어났으면 푸시 마커를 지운다 (1회용)
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+push([[:space:]]|$)'; then
  # 하위 갈래는 if/elif 사슬이다 — 한 명령에 푸시가 둘이면 더 구체적인 갈래 하나만 탄다.
  # 전에는 각 갈래 끝의 exit 0 이 이 배타를 만들고 있었다. 그 exit 들을 지우면서
  # elif 로 잇지 않으면 한 명령이 여러 갈래를 타서 journal 에 두 줄이 남는다.
  #
  # main 승격(dev:main)이 실제로 반영됐으면 승격 마커를 지우고 RELEASE 를 기록한다 (L-001)
  if printf '%s' "$cmd" | grep -Eq 'origin[[:space:]]+dev:main([[:space:]]|$)' && [ -f "$RELEASE_MARK" ]; then
    git -C "$ROOT" fetch -q origin main 2>/dev/null || true
    if [ "$(git -C "$ROOT" rev-parse origin/main 2>/dev/null)" = "$(git -C "$ROOT" rev-parse dev 2>/dev/null)" ]; then
      rm -f "$RELEASE_MARK" "$AWAIT"
      [ -f "$JOURNAL" ] && printf -- '- %s | RELEASE | origin main ← dev %s\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short dev 2>/dev/null || true)" >> "$JOURNAL"
    fi
  # 검증 승격(dev2:dev)이 실제로 반영됐으면 푸시 마커를 지우고 L-003 대기를 건다.
  # 성공 판정: 푸시가 되면 원격 추적 ref(origin/dev)가 HEAD 로 갱신되고, 실패하면 그대로 남는다.
  elif printf '%s' "$cmd" | grep -Eq 'origin[[:space:]]+dev2:dev([[:space:]]|$)'; then
    if [ "$(git -C "$ROOT" rev-parse origin/dev 2>/dev/null)" = "$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" ]; then
      rm -f "$PUSH_MARK"
      [ -f "$JOURNAL" ] && printf -- '- %s | PUSH | origin dev ← dev2 %s — 사용자 결정 대기(승격/수정) L-003\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)" >> "$JOURNAL"
      # L-003: dev 로 올린 뒤에는 사용자가 승격/수정을 정할 때까지 다음 작업을 막는다
      git -C "$ROOT" rev-parse --short HEAD 2>/dev/null > "$AWAIT" || date +%s > "$AWAIT"
    fi
  # 실험 푸시(dev2)는 승인 판단이 없다. 마커를 쓰지 않고 L-003 대기도 걸지 않는다 —
  # 걸면 실험할 때마다 작업이 잠겨서 "아무때나 민다"는 목적이 사라진다.
  elif printf '%s' "$cmd" | grep -Eq 'origin[[:space:]]+dev2([[:space:]]|$)'; then
    if [ "$(git -C "$ROOT" rev-parse origin/dev2 2>/dev/null)" = "$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" ]; then
      [ -f "$JOURNAL" ] && printf -- '- %s | PUSH-dev2 | origin dev2 %s (실험 푸시)\n' "$(date +%Y-%m-%d\ %H:%M)" "$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)" >> "$JOURNAL"
    fi
  fi
fi
exit 0
