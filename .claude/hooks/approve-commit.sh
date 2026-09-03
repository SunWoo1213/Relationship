#!/usr/bin/env bash
# 커밋 초안 승인 마커 생성.
# 반드시 /commit 스킬에서 사용자가 AskUserQuestion 으로 "승인"을 선택한 직후에만 호출한다.
# 마커에는 초안 파일의 sha256 을 기록한다 → 승인 후 초안이 바뀌면 commit-guard 가 거부한다.
# 옵션 --push : 사용자가 "커밋 + 푸시"를 선택한 경우. 푸시 마커(.claude/.push-approved)도 함께 만든다.
#               safety-guard.sh 는 이 마커가 있을 때만 git push origin dev 를 허용한다.
# 옵션 --release : /commit release 에서 사용자가 "main 승격"을 승인한 경우(초안 불필요).
#               승격 마커(.claude/.release-approved)만 만든다. safety-guard.sh 는 이 마커가 있을 때만
#               git push origin dev:main 을 허용한다 (L-001 브랜치 전략).
set -eu
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
DRAFT="$ROOT/.claude/commit-draft.txt"
MARK="$ROOT/.claude/.commit-approved"
PUSH_MARK="$ROOT/.claude/.push-approved"
RELEASE_MARK="$ROOT/.claude/.release-approved"

if [ "${1:-}" = "--release" ]; then
  date +%s > "$RELEASE_MARK"
  echo "승격 마커 생성됨. 다음 명령만 허용된다 (dev → main, fast-forward 만):"
  echo "  git push origin dev:main"
  exit 0
fi

[ -f "$DRAFT" ] || { echo "초안 파일이 없다: .claude/commit-draft.txt" >&2; exit 1; }
[ -s "$DRAFT" ] || { echo "초안 파일이 비어 있다" >&2; exit 1; }

sha256sum "$DRAFT" | cut -d' ' -f1 > "$MARK"
echo "승인 마커 생성됨. 이제 다음 명령으로만 커밋할 수 있다:"
echo "  git commit -F .claude/commit-draft.txt"
if [ "${1:-}" = "--push" ]; then
  date +%s > "$PUSH_MARK"
  echo "푸시 마커 생성됨. 커밋 후 다음 명령만 허용된다:"
  echo "  git push -u origin dev"
fi
