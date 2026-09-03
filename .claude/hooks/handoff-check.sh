#!/usr/bin/env bash
# Stop 훅 — 턴을 끝내기 전에 HANDOFF.md 가 최신인지 확인한다.
#
# 변경된(추적·미추적) 파일 중 docs/wiki/HANDOFF.md 보다 새로운 것이 있으면 종료를 막고
# "HANDOFF 를 갱신하라"고 돌려보낸다. 컨텍스트가 끊겨도 다음 세션이 이어갈 수 있게 하는 장치다.
# stop_hook_active 가 true 면(이미 한 번 막았던 재시도) 무한 루프를 피하기 위해 통과시킨다.
#
# stdin: {"stop_hook_active": bool, ...}
# stdout(막을 때만): {"decision":"block","reason":"..."}

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
HANDOFF="$ROOT/docs/wiki/HANDOFF.md"

input="$(cat)"
active="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); print("1" if d.get("stop_hook_active") else "0")
except Exception:
    print("0")' 2>/dev/null)"
[ "$active" = "1" ] && exit 0

[ -f "$HANDOFF" ] || { printf '{"decision":"block","reason":"docs/wiki/HANDOFF.md 가 없다. 템플릿 형식으로 만들고 지금 어디까지 했는지, 다음에 무엇을 할지 적은 뒤 끝내라."}\n'; exit 0; }

cd "$ROOT" || exit 0
changed="$(git status --porcelain -uall 2>/dev/null | cut -c4- | sed 's/^"//; s/"$//')"
[ -n "$changed" ] || exit 0

stale=""
count=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in
    docs/wiki/HANDOFF.md|docs/wiki/journal.md|.claude/commit-draft.txt|.claude/.commit-approved|.claude/.push-approved) continue ;;
  esac
  # rename 표기 "a -> b" 처리
  f="${f##* -> }"
  if [ -e "$f" ] && [ "$f" -nt "$HANDOFF" ]; then
    count=$((count+1))
    [ "$count" -le 5 ] && stale="$stale $f"
  fi
done <<< "$changed"

if [ "$count" -gt 0 ]; then
  printf '{"decision":"block","reason":"HANDOFF 미갱신: docs/wiki/HANDOFF.md 보다 새로운 변경 파일이 %d개 있다(%s ). 턴을 끝내기 전에 HANDOFF.md 의 갱신 시각·지금 어디까지·바로 다음에 할 것을 현재 상태로 고쳐 쓰라. 커밋할 단위가 끝났으면 /commit 도 제안하라."}\n' "$count" "$stale"
fi
exit 0
