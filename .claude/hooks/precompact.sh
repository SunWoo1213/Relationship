#!/usr/bin/env bash
# PreCompact 훅 — 컨텍스트 압축 직전에 journal 에 표시를 남긴다.
# 압축 뒤 SessionStart(compact) 가 HANDOFF 를 다시 주입하므로, 여기서는 "언제 압축됐는지"만 기록한다.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
J="$ROOT/docs/wiki/journal.md"
input="$(cat)"
trig="$(printf '%s' "$input" | python -c 'import sys,json
try:
    print(json.load(sys.stdin).get("trigger",""))
except Exception:
    print("")' 2>/dev/null)"
if [ -f "$J" ]; then
  printf -- '- %s | NOTE | 컨텍스트 압축(%s). 재개 시 HANDOFF.md 확인 |\n' "$(date +%Y-%m-%d\ %H:%M)" "${trig:-unknown}" >> "$J"
fi
exit 0
