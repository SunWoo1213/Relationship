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
AWAIT="$ROOT/.claude/.awaiting-decision"

# L-004: 계획·구현·검증 단계 위임은 사용자가 AskUserQuestion 으로 "시작"을 택한 직후에만.
#        1회용 마커(.claude/.stage-approved = 에이전트 이름)를 만든다. delegate-guard.sh 가 Agent 호출 시 검사·소비한다.
if [ "${1:-}" = "--stage" ]; then
  case "${2:-}" in
    architect|backend-agent|eval-agent|verifier)
      printf '%s\n' "$2" > "$ROOT/.claude/.stage-approved"
      echo "단계 승인 기록: $2 — 이제 Agent(subagent_type=$2) 를 1회 띄울 수 있다"; exit 0 ;;
    *) echo "usage: approve-commit.sh --stage architect|backend-agent|eval-agent|verifier" >&2; exit 1 ;;
  esac
fi

# L-003: dev 푸시 후 사용자가 "수정 계속"을 택한 경우 — 결정 대기 마커만 지운다
if [ "${1:-}" = "--decision" ]; then
  case "${2:-}" in
    fix) rm -f "$AWAIT"; echo "결정 기록: 수정 계속. 결정 대기 마커 해제됨 — 이제 새 작업·커밋 가능"; exit 0 ;;
    *) echo "usage: approve-commit.sh --decision fix   (승격은 --release)" >&2; exit 1 ;;
  esac
fi

if [ "${1:-}" = "--release" ]; then
  date +%s > "$RELEASE_MARK"
  rm -f "$AWAIT"
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
