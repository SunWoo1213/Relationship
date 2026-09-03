#!/usr/bin/env bash
# SessionStart 훅 (startup | resume | compact) — 재개 문서를 컨텍스트에 자동 주입한다.
# stdout 이 그대로 모델 컨텍스트에 들어간다. 짧게: HANDOFF 전체 + CURRENT 상태 + journal 마지막 5줄.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
W="$ROOT/docs/wiki"

input="$(cat)"
src="$(printf '%s' "$input" | python -c 'import sys,json
try:
    print(json.load(sys.stdin).get("source",""))
except Exception:
    print("")' 2>/dev/null)"

echo "=== 세션 재개 컨텍스트 (source: ${src:-unknown}) — 전문 읽기 금지, 아래와 INDEX.md 만으로 시작 ==="
if [ -f "$W/CURRENT.md" ]; then
  echo "--- CURRENT ---"
  grep -E '^(active|frozen):' "$W/CURRENT.md"
fi
if [ -f "$W/HANDOFF.md" ]; then
  echo "--- HANDOFF (docs/wiki/HANDOFF.md) ---"
  cat "$W/HANDOFF.md"
else
  echo "--- HANDOFF 없음: docs/wiki/templates 형식으로 만들 것 ---"
fi
if [ -f "$W/journal.md" ]; then
  echo "--- journal 최근 5줄 ---"
  grep -E '^- ' "$W/journal.md" | tail -n 5
fi
changed="$(git -C "$ROOT" status --porcelain -uall 2>/dev/null | head -n 20)"
if [ -n "$changed" ]; then
  echo "--- 커밋 안 된 변경 (최대 20개) ---"
  printf '%s\n' "$changed"
  echo "--- 재개 규칙: 위 변경과 HANDOFF 의 '진행 중' 항목은 중단된 작업이다. 다른 어떤 일보다 먼저 사용자에게 이 목록을 보이고 AskUserQuestion 으로 우선순위(이어서 완료 / 보류 / 폐기)를 정한 뒤 시작하라 (/devlog resume). ---"
fi
if [ -d "$W/packages" ]; then
  for r in "$W"/packages/*/05-remediation.md; do
    [ -f "$r" ] || continue
    n="$(grep -c '^상태: 열림' "$r" || true)"
    [ "${n:-0}" -gt 0 ] && echo "--- 열린 소견 $n 건: ${r#$ROOT/} ---"
  done
fi
if [ "$src" = "compact" ]; then
  echo "--- 주의: 컨텍스트가 압축됐다. 위 HANDOFF 가 압축 전 상태와 다르면 먼저 HANDOFF 를 고치고 계속하라. ---"
fi
echo "=== 규칙: 작업 단위마다 /commit, 턴 종료 전 HANDOFF 갱신(Stop 훅이 검사), 제품 코드는 CURRENT active 등록 후 ==="
exit 0
