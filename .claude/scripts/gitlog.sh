#!/usr/bin/env bash
# gitlog.sh [태그 …] — 계획·계획 검증·구현 에이전트가 보는 git 이력 요약 (L-001, CLAUDE.md "git log 연동")
#
# 출력: 브랜치 상태, 최근 커밋 20건, 태그별 커밋(인자로 준 태그 또는 CURRENT.md active 패키지 + 그 Refs), 마지막 커밋의 파일 목록.
# 두 경로로 쓰인다:
#   1) Bash 가 있는 에이전트(backend-agent, eval-agent, 메인 세션): bash .claude/scripts/gitlog.sh P0-embed-pilot D4
#   2) Bash 가 없는 에이전트(architect): 훅(session-start, commit-cleanup)이 같은 출력을 .claude/gitlog.md 에 저장해 두므로 그 파일을 Read 한다.
# --write : 출력 대신 .claude/gitlog.md 에 저장한다(훅용).
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
OUT="$ROOT/.claude/gitlog.md"
write=0
tags=()
for a in "$@"; do
  case "$a" in --write) write=1 ;; *) tags+=("$a") ;; esac
done
# 태그를 주지 않았으면 CURRENT.md active 패키지를 태그로 쓴다
if [ ${#tags[@]} -eq 0 ] && [ -f "$ROOT/docs/wiki/CURRENT.md" ]; then
  act="$(grep -E '^active:' "$ROOT/docs/wiki/CURRENT.md" | head -n1 | sed -E 's/^active:[[:space:]]*//' | tr -d '\r')"
  [ -n "$act" ] && [ "$act" != "none" ] && tags+=("$act")
fi

render() {
  cd "$ROOT" || exit 0
  git rev-parse --git-dir >/dev/null 2>&1 || { echo "(git 저장소 아님)"; return; }
  echo "# git log 스냅샷 — $(date +%Y-%m-%d\ %H:%M) (훅·gitlog.sh 자동 생성, 커밋하지 않음)"
  echo
  echo "## 브랜치"
  echo '```'
  git status -sb 2>/dev/null | head -n1
  git branch -vv --no-color 2>/dev/null | sed 's/^/  /'
  echo "main(origin) = $(git rev-parse --short origin/main 2>/dev/null || echo '-')   dev = $(git rev-parse --short dev 2>/dev/null || echo '-')"
  n="$(git rev-list --count origin/main..dev 2>/dev/null || echo 0)"; echo "dev 에 있고 main 에 없는 커밋(승격 대기): $n"
  echo '```'
  echo
  echo "## 최근 커밋 20건"
  echo '```'
  git log --oneline --no-color -20 --date=short --format='%h %ad %s' 2>/dev/null
  echo '```'
  for t in "${tags[@]}"; do
    echo
    echo "## 태그 '$t' 커밋 (git log --grep)"
    echo '```'
    git log --oneline --no-color --format='%h %ad %s' --date=short --grep="$t" 2>/dev/null | head -n 30
    echo '```'
  done
  echo
  echo "## 마지막 커밋의 파일"
  echo '```'
  git show --stat --no-color --format='%h %s%n%b' HEAD 2>/dev/null | head -n 60
  echo '```'
  echo
  echo "## 커밋 안 된 변경 (git status --short)"
  echo '```'
  git status --short 2>/dev/null | head -n 40
  echo '```'
}

if [ "$write" -eq 1 ]; then
  render > "$OUT" 2>/dev/null || true
else
  render
fi
