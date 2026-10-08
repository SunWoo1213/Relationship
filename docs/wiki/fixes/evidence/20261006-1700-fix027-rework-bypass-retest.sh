#!/usr/bin/env bash
# review-FIX-027 의 verifier 우회·fail-closed 시험 46건을 FIX-027 재작업 이후 다시 돌린다.
# 원본은 docs/wiki/fixes/evidence/20261006-1613-review-fix027-bypass.txt 끝의 bypass.sh.
# 재작업으로 바뀐 두 가지를 반영해 셋업을 고쳤다(로직은 그대로, 셋업만 보강):
#   (1) R-27-3 — review-FIX-nnn.md 는 이제 "검토자: verifier" 줄 + git 추적(스테이징)을
#       요구한다. 원본 스크립트는 review 문서를 한 번도 git add 하지 않았다(그 자체가
#       review 문서 결함 재현 목적이었던 2곳 제외). "허용돼야 하는" 셋업에는 git add 를
#       더했다 — 안 더하면 "허용" 기대가 R-27-3 자체와 충돌해 무의미한 실패가 된다.
#   (2) F-27-1 정책 결정 — 제목이 FIX-nnn 을 명시하지 않는 커밋(`fix(P7-push)`)은 이
#       규칙 대상 밖으로 두기로 했다(패키지는 02-plan-verify 가 따로 게이트). 그래서
#       이 한 줄만 기대값을 DENY → allow 로 바꿨다(정책, 버그 아님). 주석에 이유를 적는다.
# 판독: "ok"=기대와 일치, "!!"=기대와 다름(사전에 알려진 범위 밖 항목은 "--"로 표시).
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
PROJ="/Users/sunwoo/Desktop/Portfolio/Relationship"
H="$PROJ/.claude/hooks"
. "$H/_py.sh"
T="$(mktemp -d)"
mkdir -p "$T/.claude" "$T/app" "$T/alembic" "$T/docs/wiki/fixes"
( cd "$T" && git init -q . && git config user.email t@example.com && git config user.name tester \
  && printf 'init\n' > README.md && git add README.md && git commit -qm init ) >/dev/null 2>&1

mk() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'command':sys.argv[1]}}))" "$1"; }
draft_raw() { printf '%s' "$1" > "$T/.claude/commit-draft.txt"; approve; }
draft() { printf '%s\n\n본문\n' "$1" > "$T/.claude/commit-draft.txt"; approve; }
approve() { "$HOOK_PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$T/.claude/commit-draft.txt" > "$T/.claude/.commit-approved"; }
run() { printf '%s' "$(mk "${1:-git commit -F .claude/commit-draft.txt}")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh"; }
show() { local verdict
  if printf '%s' "$3" | grep -q '"deny"'; then verdict=DENY; elif [ -z "$3" ]; then verdict=allow; else verdict="OTHER"; fi
  if [ "$verdict" = "$2" ]; then echo "ok   [$verdict] $1"; else echo "!!   [$verdict] (기대 $2) $1"; fi
  [ -n "$3" ] && printf '       -> %s\n' "$(printf '%s' "$3" | head -c 220)"; }
stage_app() { printf 'x\n' > "$T/app/a.py"; ( cd "$T" && git add app/a.py ); }
clear_docs() { rm -f "$T/docs/wiki/fixes/FIX-999.md" "$T/docs/wiki/fixes/review-FIX-999.md"; }
review_ok() { printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md ); }

# A
stage_app; clear_docs
for t in 'fix(FIX-999): 정상' 'Fix(FIX-999): 대문자' 'FIX(FIX-999): 대문자2' 'fix (FIX-999): 공백' 'fix(FIX-999, FIX-998): 둘' 'fix(FIX-999)!: 느낌표' 'feat(FIX-999): feat' 'docs(FIX-999): docs' 'harness(FIX-999): harness' 'chore(FIX-999): chore' 'fix(FIX-27): 세 자리 아님' ; do
  draft "$t"; show "$t" DENY "$(run)"; done
# 정책 결정(F-27-1): 제목이 패키지 id 를 가리키면(FIX-nnn 명시 없음) 이 규칙 대상 밖 — allow 가 맞다.
draft 'fix(P7-push): 본문에만 FIX'; show 'fix(P7-push): 본문에만 FIX [정책: 대상 밖]' allow "$(run)"
draft_raw $'\nfix(FIX-999): 첫 줄 공백\n\n본문\n';  show 'draft 첫 줄이 빈 줄' DENY "$(run)"
draft_raw $'\xef\xbb\xbffix(FIX-999): BOM\n\n본문\n'; show 'draft 첫 줄 UTF-8 BOM' DENY "$(run)"
draft_raw $'fix(FIX-999): CRLF\r\n\r\n본문\r\n';      show 'draft CRLF 줄끝' DENY "$(run)"
# B
draft 'fix(FIX-999): 경로'; ( cd "$T" && git reset -q app/a.py )
printf 'x\n' > "$T/alembic/v1.py"; ( cd "$T" && git add alembic/v1.py ); show 'alembic/ 만 스테이징' DENY "$(run)"
( cd "$T" && git reset -q alembic/v1.py )
printf 'x\n' > "$T/app/한글.py"; ( cd "$T" && git add 'app/한글.py' ); show 'app/한글.py [범위 밖: R-27-2, 이번 라운드 미처리]' allow "$(run)"
( cd "$T" && git reset -q 'app/한글.py' && rm -f 'app/한글.py' )
printf 'y\n' > "$T/app/a.py"; ( cd "$T" && git add app/a.py && git commit -qm "app 추적" && printf 'z\n' > app/a.py )
show 'git commit -a -F draft' DENY "$(run 'git commit -a -F .claude/commit-draft.txt')"
show 'git commit -F draft app/a.py' DENY "$(run 'git commit -F .claude/commit-draft.txt app/a.py')"
show 'git commit --include app/a.py -F draft' DENY "$(run 'git commit --include app/a.py -F .claude/commit-draft.txt')"
( cd "$T" && git add app/a.py )
# C — review 문서는 R-27-3 기준(검토자: verifier + 스테이징)을 갖춰 둔다. 그래야 각 줄의
# "allow 기대" 가 FIX 문서의 검증 줄 자체 때문인지 review 문서 때문인지가 섞이지 않는다.
review_ok
for line in '검증: 보류 — verifier (fable) 2026-10-06, review-FIX-999.md [필수] 2건' '검증: 통과(점검표 1~8) — verifier 리뷰는 아직' '검증: verifier 에게 요청 예정' '검증: 통과 — 메인 세션 (verifier 생략)' ; do
  printf '%s\n' "$line" > "$T/docs/wiki/fixes/FIX-999.md"; show "$line" DENY "$(run)"; done
printf '검증: (verifier 가 쓴다)\n\n## 결과\n검증: 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show '검증: 줄 두 개' DENY "$(run)"
printf '> 검증: 통과 — verifier (fable)\n- 검증: 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show '인용·목록 안의 검증 줄만' DENY "$(run)"
printf '검증: 통과 — verifier (fable) 2026-10-06, review-FIX-999.md\r\n' > "$T/docs/wiki/fixes/FIX-999.md"; show 'FIX 문서 CRLF' allow "$(run)"
printf '검증: 통과 — verifier (fable) 2026-10-06, review-FIX-999.md\n' > "$T/docs/wiki/fixes/FIX-999.md"
: > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md ); show 'review 문서 0바이트' DENY "$(run)"
printf '# 아무 내용\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md ); show 'review 문서에 검토자 줄 없음' DENY "$(run)"
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git reset -q docs/wiki/fixes/review-FIX-999.md )
show 'review 문서 untracked(디스크에만)' DENY "$(run)"
( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
printf '\xff\xfe검증: 통과 — verifier\n' > "$T/docs/wiki/fixes/FIX-999.md"; out="$(run)"; show 'FIX 문서가 UTF-8 아님' DENY "$out"
printf '%s' "$out" | "$HOOK_PY" -c 'import sys,json
try: json.load(sys.stdin); print("       훅 stdout 은 유효한 JSON")
except Exception as e: print("       !! 훅 stdout 이 유효한 JSON 이 아니다:", e)'
# D
printf '검증: 통과 — verifier (fable), review-FIX-999.md\n' > "$T/docs/wiki/fixes/FIX-999.md"; review_ok
show '기준: 정상' allow "$(run)"
NG="$(mktemp -d)"; mkdir -p "$NG/.claude"; cp "$T/.claude/commit-draft.txt" "$T/.claude/.commit-approved" "$NG/.claude/"
show 'ROOT 가 git 저장소가 아님' DENY "$(printf '%s' "$(mk 'git commit -F .claude/commit-draft.txt')" | CLAUDE_PROJECT_DIR="$NG" bash "$H/commit-guard.sh")"; rm -rf "$NG"
HC="$(mktemp -d)"; mkdir -p "$HC/.claude/hooks" "$HC/.claude/scripts"; cp "$H/commit-guard.sh" "$H/_py.sh" "$HC/.claude/hooks/"
show '훅 복사본에서 fix_guard_check.py 부재' DENY "$(printf '%s' "$(mk 'git commit -F .claude/commit-draft.txt')" | CLAUDE_PROJECT_DIR="$T" bash "$HC/.claude/hooks/commit-guard.sh")"; rm -rf "$HC"
"$HOOK_PY" "$PROJ/.claude/scripts/fix_guard_check.py" "$T" >/dev/null 2>&1; echo "   인자 부족 rc=$?"
"$HOOK_PY" "$PROJ/.claude/scripts/fix_guard_check.py" "$T" "$T/없는초안.txt" >/dev/null 2>&1; echo "   초안 없음 rc=$?"
draft 'feat(P7): 기존 규칙 유지 확인'
show '기존 1: 마커 없음' DENY "$(rm -f "$T/.claude/.commit-approved"; run)"; approve
show '기존 2: -m 사용' DENY "$(run 'git commit -m x')"
show '기존 3: 해시 불일치' DENY "$(printf 'changed\n' >> "$T/.claude/commit-draft.txt"; run)"; approve
show '기존 4: --amend' DENY "$(run 'git commit --amend -F .claude/commit-draft.txt')"
show '기존 4b: --no-verify' DENY "$(run 'git commit --no-verify -F .claude/commit-draft.txt')"
show '기존 5: 마커 조작' DENY "$(run 'rm .claude/.commit-approved')"
show '기존: 정상 feat 커밋 허용' allow "$(run)"
# E
printf 'active: FIX-999\nfrozen: none\n' > "$T/docs/wiki/CURRENT.md"
printf '# FIX-999\n\n계획 점검: 통과(메인 세션, 점검표 1~8)\n검증: (verifier 가 쓴다 — 제품 코드를 바꾸면 커밋 전 review-FIX-nnn.md 와 함께)\n승인: 사용자 (2026-10-06)\n' > "$T/docs/wiki/fixes/FIX-999.md"
gate() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'file_path':sys.argv[1]}}))" "$1"; }
show 'stage-gate: 새 템플릿으로 app/ 쓰기' allow "$(printf '%s' "$(gate "$T/app/new.py")" | CLAUDE_PROJECT_DIR="$T" bash "$H/stage-gate.sh")"
printf '# FIX-999\n\n검증: 통과(점검표 1~8)\n승인: 사용자 (2026-10-06)\n' > "$T/docs/wiki/fixes/FIX-999.md"
show 'stage-gate: 옛 템플릿' allow "$(printf '%s' "$(gate "$T/app/new.py")" | CLAUDE_PROJECT_DIR="$T" bash "$H/stage-gate.sh")"
rm -rf "$T"
