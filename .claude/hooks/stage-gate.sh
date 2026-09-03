#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit|NotebookEdit) 훅 — 단계 게이트
#
# 작업 산출물(코드·데이터·리포트 등 docs/ 와 .claude/ 밖의 파일)을 쓰려면
# docs/wiki/CURRENT.md 에 등록된 활성 작업의 "계획 검증 통과 + 사용자 승인" 기록이 있어야 한다.
#
#   CURRENT.md 형식:   active: P1-schema      (패키지)  또는   active: FIX-003 (수정)
#   패키지 → docs/wiki/packages/<id>/02-plan-verify.md 에 "결과: 통과" 와 "승인: <비어있지 않음>"
#   수정   → docs/wiki/fixes/<id>.md 에 "검증: 통과" 와 "승인: <비어있지 않음>"
#
# 면제 경로: docs/, .claude/, reports/, CLAUDE.md, README.md, .gitignore, .env.example, LICENSE

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
CURRENT="$ROOT/docs/wiki/CURRENT.md"

input="$(cat)"
fp="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); ti=d.get("tool_input",{})
    print(ti.get("file_path") or ti.get("notebook_path") or "")
except Exception:
    print("")' 2>/dev/null)"
[ -n "$fp" ] || exit 0

deny() {
  reason="$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

# 경로 정규화 (백슬래시 → 슬래시, 루트 기준 상대경로)
fp="$(printf '%s' "$fp" | sed 's#\\#/#g')"
root_fwd="$(printf '%s' "$ROOT" | sed 's#\\#/#g')"
# C:/... 와 /c/... 두 표기 모두 처리
root_drive="$(printf '%s' "$root_fwd" | sed -E 's#^/([a-zA-Z])/#\U\1:/#')"
rel="$fp"
case "$fp" in
  "$root_fwd"/*)   rel="${fp#"$root_fwd"/}" ;;
  "$root_drive"/*) rel="${fp#"$root_drive"/}" ;;
esac
# 대소문자 드라이브 차이 보정
rel_lc="$(printf '%s' "$rel" | tr 'A-Z' 'a-z')"
root_lc="$(printf '%s' "$root_drive" | tr 'A-Z' 'a-z')"
fp_lc="$(printf '%s' "$fp" | tr 'A-Z' 'a-z')"
case "$fp_lc" in "$root_lc"/*) rel="${fp:$((${#root_drive}+1))}" ;; esac

# 프로젝트 밖 파일은 게이트 대상 아님
case "$fp" in "$root_fwd"/*|"$root_drive"/*) ;; *) case "$fp_lc" in "$root_lc"/*) ;; *) exit 0 ;; esac ;; esac

# L-003: dev 푸시 후 사용자 결정(승격/수정) 전에는 다음 작업 금지 — HANDOFF·journal·초안·gitlog 만 허용
AWAIT="$ROOT/.claude/.awaiting-decision"
if [ -f "$AWAIT" ]; then
  case "$rel" in
    docs/wiki/HANDOFF.md|docs/wiki/journal.md|.claude/commit-draft.txt|.claude/gitlog.md) ;;
    *) deny "dev 푸시($(head -c 12 "$AWAIT" 2>/dev/null)) 후 사용자 결정 대기 중이다. main 승격(/commit release) 또는 수정 계속(approve-commit.sh --decision fix)을 AskUserQuestion 으로 정하기 전에는 다음 작업을 시작하지 않는다 (L-003). 허용: HANDOFF.md, journal.md, commit-draft.txt" ;;
  esac
fi

# 면제 경로
case "$rel" in
  docs/*|.claude/*|.githooks/*|.github/*|reports/*|CLAUDE.md|README.md|.gitignore|.gitattributes|.env.example|LICENSE) exit 0 ;;
esac

[ -f "$CURRENT" ] || deny "docs/wiki/CURRENT.md 가 없다. devlog 스킬 절차로 계획·계획검증 기록을 만들고 활성 작업을 등록하라."

# 기획서 변경 요청(CR)이 열려 있으면 제품 코드 쓰기 전면 차단 (docs/·.claude/ 는 위에서 면제됨)
frozen="$(grep -E '^frozen:' "$CURRENT" | head -n1 | sed -E 's/^frozen:[[:space:]]*//' | tr -d '[:space:]\r')"
if [ -n "$frozen" ] && [ "$frozen" != "none" ]; then
  deny "기획서 변경 요청 $frozen 이(가) 열려 있어 제품 코드 쓰기가 동결됐다. docs/wiki/changes/$frozen.md 의 이행 계획을 끝내고 CURRENT.md frozen: none 으로 되돌린 뒤 계속하라."
fi

active="$(grep -E '^active:' "$CURRENT" | head -n1 | sed -E 's/^active:[[:space:]]*//' | tr -d '[:space:]\r')"
[ -n "$active" ] && [ "$active" != "none" ] || deny "활성 작업이 없다(CURRENT.md active: none). /devlog start <패키지id> 로 계획(01-plan) → 계획검증(02-plan-verify) → 사용자 승인 → 등록을 마친 뒤 코드를 쓰라."

case "$active" in
  FIX-*)
    rec="$ROOT/docs/wiki/fixes/$active.md"
    [ -f "$rec" ] || deny "수정 기록 $active 이(가) docs/wiki/fixes/ 에 없다. fix 템플릿으로 먼저 기록하라."
    grep -Eq '^검증:[[:space:]]*통과' "$rec" || deny "$active 의 수정 계획 검증이 '통과'가 아니다. 원인·수정안·기획서 정합성을 검증하고 '검증: 통과'를 기록하라."
    grep -Eq '^승인:[[:space:]]*[^[:space:]]' "$rec" || deny "$active 에 사용자 승인 기록이 없다. AskUserQuestion 으로 승인받고 '승인: 사용자 (날짜)'를 기록하라."
    ;;
  *)
    dir="$ROOT/docs/wiki/packages/$active"
    [ -d "$dir" ] || deny "패키지 폴더 docs/wiki/packages/$active 가 없다. plan 템플릿으로 01-plan.md 부터 만들어라."
    [ -f "$dir/01-plan.md" ] || deny "$active 에 01-plan.md 가 없다."
    [ -f "$dir/02-plan-verify.md" ] || deny "$active 에 02-plan-verify.md 가 없다. devlog 스킬의 정합성 점검표로 기획서 정합성을 검증하고 기록하라."
    grep -Eq '^결과:[[:space:]]*통과' "$dir/02-plan-verify.md" || deny "$active 의 계획 검증 결과가 '통과'가 아니다. 보류 사유를 해소한 뒤 다시 검증하라."
    grep -Eq '^승인:[[:space:]]*[^[:space:]]' "$dir/02-plan-verify.md" || deny "$active 의 계획에 사용자 승인 기록이 없다. AskUserQuestion 으로 승인받고 '승인: 사용자 (날짜)'를 기록하라."
    ;;
esac
exit 0
