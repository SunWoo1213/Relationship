#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit|NotebookEdit) 훅 — 단계 게이트
#
# 작업 산출물(코드·데이터·리포트 등 docs/ 와 .claude/ 밖의 파일)을 쓰려면
# docs/wiki/CURRENT.md 에 등록된 활성 작업의 "계획 검증 통과 + 사용자 승인" 기록이 있어야 한다.
#
#   CURRENT.md 형식:   active: P1-schema      (패키지)  또는   active: FIX-003 (수정)
#   패키지 → docs/wiki/packages/<id>/02-plan-verify.md 에 "결과: 통과" 와 "승인: <비어있지 않음>"
#   수정   → docs/wiki/fixes/<id>.md 에 "계획 점검: 통과"(새 템플릿, FIX-027 이후) 또는
#            "검증: 통과"(FIX-001~026 옛 템플릿, 한 줄뿐) 와 "승인: <비어있지 않음>".
#            코드를 쓰기 전 이 게이트가 보는 것은 "계획 점검"(메인 세션)뿐이다. verifier 의
#            실제 `검증:` 판정(통과/보류)은 코드가 다 생긴 뒤 커밋 시점에
#            commit-guard.sh 규칙 6 이 본다 — 역할이 다르다(F-27-1, FIX-027 재작업).
#
# 면제 경로: docs/, .claude/(단 hooks/·scripts/·settings.json 은 제외, R-27-5), reports/,
#           CLAUDE.md, README.md, .gitignore, .env.example, LICENSE, .github/(단 workflows/ 는 제외)

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
CURRENT="$ROOT/docs/wiki/CURRENT.md"

# 파이썬 인터프리터 탐지 (FIX-008). 못 찾으면 통과시키지 않고 차단한다.
. "$(dirname "$0")/_py.sh"
if [ -z "$HOOK_PY" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[stage-gate] %s"}}\n' "$HOOK_PY_MISSING_MSG"
  exit 0
fi

input="$(cat)"
fp="$(printf '%s' "$input" | "$HOOK_PY" -c 'import sys,json
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

# R-27-5: 하네스 자체(훅·스크립트·설정·CI)는 면제 경로 중 가장 느슨한 쓰기였다 — 활성 작업
# 게이트 없이 .claude/* 전체가 통째로 면제됐다. 이 저장소의 가드 결함 이력(FIX-002·003·008·
# 013·014 후보)이 전부 여기서 났고, FIX-027 자신도 독립 리뷰에서 [필수] 4건이 나왔다. 그래서
# 이 네 경로만 면제에서 빼 아래 활성 작업 게이트를 그대로 타게 한다(제품 코드와 동일 취급).
# 순서가 중요하다 — 이 case 가 먼저 와야 다음 case 의 넓은 ".claude/*" 패턴에 먼저 걸려
# 조용히 면제되는 일이 없다.
case "$rel" in
  .claude/hooks/*|.claude/scripts/*|.claude/settings.json|.github/workflows/*) ;;  # 면제하지 않고 아래로 통과(게이트 적용)
  docs/*|.claude/*|.githooks/*|.github/*|reports/*|CLAUDE.md|README.md|.gitignore|.gitattributes|.env.example|LICENSE) exit 0 ;;
esac

# R-27-9: 아래 frozen(CR 동결) 검사는 하네스 경로(.claude/hooks·scripts·settings·workflows)도 막는다 — 의도된 동작이다. CR 이행 중에는 가드 규칙을 바꾸지 않는다(기획서 변경과 가드 변경이 한꺼번에 움직이면 무엇이 원인인지 추적이 안 된다). 훅 결함은 CR 해제(frozen: none) 뒤에 FIX 로 고친다.
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
    # F-27-1: 코드를 쓰기 전 게이트는 "계획 점검"(메인 세션)만 본다. verifier 의 실제
    # `검증:` 판정은 코드가 생긴 뒤 커밋 시점에 commit-guard.sh 규칙 6 이 본다(역할 분담).
    # 새 템플릿은 `계획 점검: 통과` 줄을 쓰고, FIX-001~026 의 옛 템플릿은 `검증: 통과` 한
    # 줄뿐이었으므로 둘 중 하나만 있어도 통과시켜 과거 FIX 문서와 호환한다.
    grep -Eq '^계획 점검:[[:space:]]*통과' "$rec" || grep -Eq '^검증:[[:space:]]*통과' "$rec" \
      || deny "$active 의 계획 점검이 '통과'가 아니다. 원인·수정안·기획서 정합성을 검증하고 '계획 점검: 통과'를 기록하라."
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
