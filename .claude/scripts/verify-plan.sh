#!/usr/bin/env bash
# verify-plan.sh <패키지 id> — 계획(01-plan)·계획검증(02-plan-verify)의 기계 검증
#
# "대충 보고 통과"를 막기 위해 사람이 판단하기 전에 기계가 확인할 수 있는 것을 전부 확인하고
# PASS/FAIL/WARN 줄로 출력한다. 출력은 02-plan-verify.md 의 "기계 검증 출력" 절에 그대로 붙인다.
#   1 필수 파일 존재            2 태그(D/S/R)가 가리키는 카드 존재
#   3 작업 단위마다 Refs        4 수용 기준이 backlog 와 글자 그대로 일치
#   5 의존 패키지 완료 + P4 게이트   6 점검표 8행 판정 존재
#   7 산출물 경로가 registry 에 다른 패키지로 이미 있는지(중복 구현 경고)
# 종료 코드: FAIL 이 하나라도 있으면 1
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
W="$ROOT/docs/wiki"
id="${1:-}"
[ -n "$id" ] || { echo "usage: verify-plan.sh <package-id>"; exit 2; }
P="$W/packages/$id"
PLAN="$P/01-plan.md"; PV="$P/02-plan-verify.md"
fail=0; warn=0
ok()   { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=$((fail+1)); }
wrn()  { printf 'WARN  %s\n' "$1"; warn=$((warn+1)); }

echo "== verify-plan $id  ($(date +%Y-%m-%d\ %H:%M)) =="

# 1 필수 파일
for f in "$PLAN" "$PV"; do
  [ -f "$f" ] && ok "존재: ${f#$ROOT/}" || bad "없음: ${f#$ROOT/}"
done
[ -f "$PLAN" ] || { echo "== 결과: FAIL=$fail WARN=$warn =="; exit 1; }

# 2 태그 → 카드 존재
tags="$(grep -oE '(^|[[:space:]])(D[0-9]{1,2}|S3[.][0-9]|R[0-9]{1,2}|P[0-9]{1,2}-[a-z0-9-]+)([[:space:]]|$|[,.)])' "$PLAN" | tr -d ' ,.)' | sort -u)"
[ -n "$tags" ] || bad "01-plan 에 태그(D/S/R/P)가 하나도 없다"
for t in $tags; do
  case "$t" in
    D*)  n="$(printf '%02d' "${t#D}")"; ls "$W/decisions/D$n-"*.md >/dev/null 2>&1 && ok "카드 존재: $t" || bad "카드 없음: $t (decisions/D$n-*.md)";;
    S3.*) ls "$W/specs/$t-"*.md >/dev/null 2>&1 && ok "카드 존재: $t" || bad "카드 없음: $t (specs/$t-*.md)";;
    R*)  grep -Eq "^\| $t \|" "$W/review-index.md" && ok "검증 항목 존재: $t" || bad "review-index 에 없음: $t";;
    P*)  grep -Fq "$t" "$W/INDEX.md" && ok "패키지 id 등록됨: $t" || bad "INDEX.md 패키지 표에 없음: $t";;
  esac
done

# 3 작업 단위마다 Refs
units="$(grep -E '^- \[[ x]\] U[0-9]+' "$PLAN" || true)"
if [ -z "$units" ]; then bad "작업 단위(- [ ] U1 …)가 없다"; else
  while IFS= read -r u; do
    printf '%s' "$u" | grep -q 'Refs:' && ok "Refs 있음: $(printf '%s' "$u" | cut -c1-60)" || bad "Refs 없음: $(printf '%s' "$u" | cut -c1-60)"
  done <<< "$units"
fi

# 4 수용 기준 == backlog (글자 그대로)
crit="$(awk '/^## 수용 기준/{f=1;next} /^## /{f=0} f && /^- /{sub(/^- /,""); print}' "$PLAN")"
if [ -z "$crit" ]; then bad "수용 기준 항목이 없다"; else
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    grep -Fq -- "$c" "$ROOT/docs/backlog.md" && ok "backlog 일치: $(printf '%s' "$c" | cut -c1-60)" || bad "backlog 에 같은 문장이 없다: $(printf '%s' "$c" | cut -c1-60)"
  done <<< "$crit"
fi

# 5 의존 패키지 완료 + P4 게이트
deps="$(grep -E '^의존:' "$PLAN" | grep -oE 'P[0-9]{1,2}-[a-z0-9-]+' | sort -u || true)"
for d in $deps; do
  [ "$d" = "$id" ] && continue
  r="$W/packages/$d/04-review.md"
  if [ -f "$r" ] && grep -Eq '^결과:[[:space:]]*완료' "$r"; then ok "의존 완료: $d"; else bad "의존 미완료: $d (04-review 결과: 완료 없음)"; fi
done
num="$(printf '%s' "$id" | sed -E 's/^P([0-9]+)-.*/\1/')"
if [ "$num" -ge 5 ] 2>/dev/null; then
  g="$W/packages/P4-pilot-eval/04-review.md"
  if [ -f "$g" ] && grep -Eq '^결과:[[:space:]]*완료' "$g"; then ok "P4 게이트 통과"; else bad "P4 게이트 미통과: P5 이후는 P4-pilot-eval 완료 전에 시작할 수 없다"; fi
fi

# 6 점검표 8행
if [ -f "$PV" ]; then
  rows="$(grep -cE '^\| [1-8] \|' "$PV" || true)"
  [ "$rows" -eq 8 ] && ok "점검표 8행 존재" || bad "점검표 행 수 $rows (8 필요)"
  undecided="$(grep -E '^\| [1-8] \|' "$PV" | grep -Evc '통과|보류' || true)"
  [ "$undecided" -eq 0 ] && ok "점검표 모든 행에 판정(통과/보류) 있음" || bad "판정 없는 점검표 행 $undecided 개"
  held="$(grep -E '^\| [1-8] \|' "$PV" | grep -c '보류' || true)"
  [ "$held" -eq 0 ] && ok "보류 0건" || wrn "보류 $held 건 — 결과는 통과가 될 수 없다"
  grep -Eq '^결과:' "$PV" && ok "결과: 줄 존재" || bad "결과: 줄 없음"
  if grep -Eq '^\| [1-8] \|[^|]*\|[^|]*\|[[:space:]]*\|' "$PV"; then bad "근거 열이 비어 있는 점검표 행이 있다 — 카드·절을 인용하라"; else ok "점검표 모든 행에 근거 있음"; fi
fi

# 7 registry 중복
outs="$(awk '/^## 산출물/{f=1;next} /^## /{f=0} f && /^- /{sub(/^- /,""); print}' "$PLAN" | grep -oE '[A-Za-z0-9_./-]+[.][a-z]{1,5}' || true)"
if [ -f "$W/registry.md" ]; then
  for o in $outs; do
    hit="$(grep -F -- "$o" "$W/registry.md" | grep -Fv -- "| $id |" || true)"
    [ -z "$hit" ] && ok "registry 중복 없음: $o" || wrn "registry 에 다른 패키지로 이미 있음: $o → $(printf '%s' "$hit" | cut -c1-80)"
  done
fi

echo "== 결과: FAIL=$fail WARN=$warn =="
[ "$fail" -eq 0 ] || exit 1
exit 0
