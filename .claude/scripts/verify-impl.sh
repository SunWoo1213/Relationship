#!/usr/bin/env bash
# verify-impl.sh <패키지 id> — 구현 검증. 증거 파일을 만들고 04-review 의 증거 열을 검사한다.
#
# 산출: docs/wiki/packages/<id>/evidence/<ts>-*.txt  (테스트 출력·린트·커밋 목록·요약)
#   1 pytest (tests/ 또는 패키지 계획의 테스트 경로) → evidence/<ts>-pytest.txt
#   2 ruff/문법 검사 → evidence/<ts>-lint.txt
#   3 이 패키지 태그가 붙은 커밋 목록 → evidence/<ts>-commits.txt (없으면 FAIL)
#   4 03-log 의 Refs 태그가 커밋에 실제로 있는지
#   5 04-review 수용 기준 표의 증거 열: evidence/ 파일, 커밋 해시(7자 이상 hex), 존재하는 경로 중 하나여야 함
#   6 registry.md 에 이 패키지 행이 있는지 (구현 목록 등록)
#   7 01-plan 작업 단위가 모두 [x] 인지
# 종료 코드: FAIL 있으면 1. "완료했습니다"라는 문장은 증거가 아니다.
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
W="$ROOT/docs/wiki"
id="${1:-}"; shift || true
[ -n "$id" ] || { echo "usage: verify-impl.sh <package-id> [pytest args]"; exit 2; }
P="$W/packages/$id"; E="$P/evidence"
[ -d "$P" ] || { echo "FAIL  패키지 폴더 없음: $P"; exit 1; }
mkdir -p "$E"
ts="$(date +%Y%m%d-%H%M)"
fail=0; warn=0
ok()  { printf 'PASS  %s\n' "$1"; }
bad() { printf 'FAIL  %s\n' "$1"; fail=$((fail+1)); }
wrn() { printf 'WARN  %s\n' "$1"; warn=$((warn+1)); }
cd "$ROOT" || exit 1

echo "== verify-impl $id  ($ts) =="

# 1 테스트
if [ -d tests ] || ls "$ROOT"/*/tests >/dev/null 2>&1; then
  if python -m pytest --version >/dev/null 2>&1; then
    python -m pytest -q "$@" > "$E/$ts-pytest.txt" 2>&1; rc=$?
    tail -n 3 "$E/$ts-pytest.txt"
    [ $rc -eq 0 ] && ok "pytest 통과 → evidence/$ts-pytest.txt" || bad "pytest 실패(rc=$rc) → evidence/$ts-pytest.txt"
  else
    wrn "pytest 미설치 — 테스트 증거 없음"
  fi
else
  wrn "tests/ 없음 — 이 패키지에 자동 테스트가 없다면 04-review 에 사유를 적으라"
fi

# 2 린트
if python -m ruff --version >/dev/null 2>&1; then
  python -m ruff check . > "$E/$ts-lint.txt" 2>&1 && ok "ruff 통과 → evidence/$ts-lint.txt" || wrn "ruff 경고/오류 → evidence/$ts-lint.txt"
else
  compileall_out="$(python -m compileall -q . 2>&1 | grep -v 'venv' || true)"
  printf '%s\n' "${compileall_out:-compileall: ok}" > "$E/$ts-lint.txt"
  [ -z "$compileall_out" ] && ok "compileall 통과 → evidence/$ts-lint.txt" || bad "문법 오류 → evidence/$ts-lint.txt"
fi

# 3 커밋 목록
git log --oneline --grep="$id" > "$E/$ts-commits.txt" 2>/dev/null
n="$(wc -l < "$E/$ts-commits.txt" | tr -d '[:space:]')"
[ "${n:-0}" -gt 0 ] && ok "태그 $id 커밋 $n 건 → evidence/$ts-commits.txt" || bad "태그 $id 가 붙은 커밋이 없다 (/commit 의 Refs 확인)"

# 4 03-log Refs ↔ git log
if [ -f "$P/03-log.md" ]; then
  for t in $(grep -oE 'Refs:.*' "$P/03-log.md" | grep -oE '(D[0-9]{1,2}|S3[.][0-9]|R[0-9]{1,2}|FIX-[0-9]+|CR-[0-9]+)' | sort -u); do
    git log --oneline --grep="$t" | grep -q . && ok "커밋에 태그 존재: $t" || wrn "03-log 에는 있지만 커밋 메시지에 없는 태그: $t"
  done
else
  bad "03-log.md 없음 — 구현 로그가 없으면 이어서 작업할 수 없다"
fi

# 5 04-review 증거 열
if [ -f "$P/04-review.md" ]; then
  # L-002 자기 평가 금지: 완료 검토는 verifier(구현자와 다른 모델)가 써야 한다
  grep -Eq '^날짜:.*검토자:[^|]*verifier' "$P/04-review.md" && ok "검토자 = verifier (L-002)" || bad "04-review 검토자 줄에 verifier 가 없다 — 구현한 쪽이 완료 검토를 쓰면 안 된다 (L-002, verifier 에이전트에 위임)"
  rows="$(awk '/^## ([0-9]+[.] )?수용 기준 대조/{f=1;next} /^## /{f=0} f && /^\|/ && !/^\| *기준|^\|-/ {print}' "$P/04-review.md")"
  [ -n "$rows" ] || bad "04-review 수용 기준 표에 행이 없다"
  while IFS= read -r r; do
    [ -n "$r" ] || continue
    ev="$(printf '%s' "$r" | awk -F'|' '{print $3}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    label="$(printf '%s' "$r" | awk -F'|' '{print $2}' | cut -c1-50)"
    if [ -z "$ev" ]; then bad "증거 없음: $label"; continue; fi
    good=0
    for tok in $(printf '%s' "$ev" | tr ',;()`' '     '); do
      case "$tok" in
        evidence/*) [ -f "$P/$tok" ] && good=1 ;;
        *) if printf '%s' "$tok" | grep -Eq '^[0-9a-f]{7,40}$'; then git cat-file -e "$tok^{commit}" 2>/dev/null && good=1
           elif [ -e "$tok" ] || [ -e "$ROOT/$tok" ]; then good=1; fi ;;
      esac
    done
    [ $good -eq 1 ] && ok "증거 확인: $label ← $(printf '%s' "$ev" | cut -c1-40)" || bad "증거가 파일·커밋·경로가 아니다: $label ← $(printf '%s' "$ev" | cut -c1-40)"
  done <<< "$rows"
else
  wrn "04-review.md 없음 (완료 검토 전이면 정상)"
fi

# 6 registry
if [ -f "$W/registry.md" ]; then
  grep -Fq -- "| $id |" "$W/registry.md" && ok "registry 에 $id 행 있음" || bad "registry.md 에 $id 의 산출물이 등록되지 않았다 (중복·누락 방지용)"
fi

# 7 작업 단위 완료
if [ -f "$P/01-plan.md" ]; then
  open_u="$(grep -cE '^- \[ \] U[0-9]+' "$P/01-plan.md" || true)"
  [ "$open_u" -eq 0 ] && ok "작업 단위 모두 완료 표시" || wrn "미완료 작업 단위 $open_u 개"
fi

{
  echo "verify-impl $id $ts"; echo "FAIL=$fail WARN=$warn"
} > "$E/$ts-summary.txt"
echo "== 결과: FAIL=$fail WARN=$warn → evidence/$ts-summary.txt =="
[ "$fail" -eq 0 ] || exit 1
exit 0
