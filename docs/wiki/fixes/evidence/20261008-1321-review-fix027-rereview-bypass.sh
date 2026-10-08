#!/usr/bin/env bash
# verifier 재리뷰(FIX-027 재작업) — 재작업 retest 46건에 없던 새 우회·예외 시험.
# 판독: ok=기대와 일치, !!=기대와 다름.
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
  [ -n "$3" ] && printf '       -> %s\n' "$(printf '%s' "$3" | "$HOOK_PY" -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d["hookSpecificOutput"]["permissionDecisionReason"][:160])
except Exception as e: print("(JSON 아님) ", sys.stdin.read()[:160] if False else e)')"; }
json_ok() { printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
json.load(sys.stdin)' >/dev/null 2>&1 && echo "       훅 stdout 유효 JSON" || echo "       !! 훅 stdout 이 유효 JSON 이 아님"; }

echo "== A. 제품 코드 미스테이징 상태에서 커밋 대상을 늘리는 플래그·인자 (F-27-3 추가 형태) =="
# app/a.py 를 추적 상태로 만들고 작업 트리만 수정(스테이징 없음)
printf 'y\n' > "$T/app/a.py"; ( cd "$T" && git add app/a.py && git commit -qm "app 추적" ) >/dev/null 2>&1
printf 'z\n' > "$T/app/a.py"
printf 'app/a.py\n' > "$T/paths.txt"
draft 'fix(FIX-999): 경로'
show 'git commit --file=.claude/commit-draft.txt app/a.py   (--file= 뒤 pathspec)' DENY "$(run 'git commit --file=.claude/commit-draft.txt app/a.py')"
show 'git commit --file .claude/commit-draft.txt app/a.py   (--file 뒤 pathspec)' DENY "$(run 'git commit --file .claude/commit-draft.txt app/a.py')"
show 'git commit app/a.py -F .claude/commit-draft.txt      (pathspec 이 -F 앞)' DENY "$(run 'git commit app/a.py -F .claude/commit-draft.txt')"
show 'git commit --pathspec-from-file=paths.txt -F draft   (pathspec 파일, -F 앞)' DENY "$(run 'git commit --pathspec-from-file=paths.txt -F .claude/commit-draft.txt')"
show 'git commit -F draft --pathspec-from-file=paths.txt   (pathspec 파일, -F 뒤)' DENY "$(run 'git commit -F .claude/commit-draft.txt --pathspec-from-file=paths.txt')"
show 'git commit -aF .claude/commit-draft.txt               (묶음 플래그)' DENY "$(run 'git commit -aF .claude/commit-draft.txt')"
show 'git commit -am x                                       (묶음 플래그 -am)' DENY "$(run 'git commit -am x')"
show 'git -c user.name=x commit -a -F draft                  (git -c 뒤 -a)' DENY "$(run 'git -c user.name=x commit -a -F .claude/commit-draft.txt')"
show 'git commit --all --file=.claude/commit-draft.txt' DENY "$(run 'git commit --all --file=.claude/commit-draft.txt')"
show 'git commit -F draft -- app/a.py                        (-- 구분자)' DENY "$(run 'git commit -F .claude/commit-draft.txt -- app/a.py')"
show 'git commit -i app/a.py -F draft' DENY "$(run 'git commit -i app/a.py -F .claude/commit-draft.txt')"
show 'git commit -o app/a.py -F draft' DENY "$(run 'git commit -o app/a.py -F .claude/commit-draft.txt')"
show 'git commit -F draft && git push origin dev2            (정상 + 후속 명령, 오탐 없어야)' allow "$(run 'git commit -F .claude/commit-draft.txt && git push origin dev2')"
show 'GIT_INDEX_FILE=/tmp/idx git commit -F draft           (환경변수로 색인 바꿔치기)' DENY "$(run 'GIT_INDEX_FILE=/tmp/idx git commit -F .claude/commit-draft.txt')"

echo "== A2. 위 우회가 실제 git 에서 app/ 를 커밋에 넣는지 (이론이 아닌 재현) =="
( cd "$T" && git commit -q --file=.claude/commit-draft.txt app/a.py && git show --stat --format=%s HEAD | grep -E 'app/a.py|fix\(' ) 2>&1 | sed 's/^/       /'
printf 'w\n' > "$T/app/a.py"
( cd "$T" && git commit -q app/a.py -F .claude/commit-draft.txt && git show --stat --format=%s HEAD | grep -E 'app/a.py' ) 2>&1 | sed 's/^/       /'
printf 'v\n' > "$T/app/a.py"
( cd "$T" && git commit -q --pathspec-from-file=paths.txt -F .claude/commit-draft.txt && git show --stat --format=%s HEAD | grep -E 'app/a.py' ) 2>&1 | sed 's/^/       /'

echo "== B. 제목이 FIX-nnn 을 담지만 TITLE_RE 를 빗나가는 형태 (app/ 스테이징 상태) =="
printf 'u\n' > "$T/app/a.py"; ( cd "$T" && git add app/a.py )
rm -f "$T/docs/wiki/fixes/FIX-999.md" "$T/docs/wiki/fixes/review-FIX-999.md"
for t in 'fix(FIX-999 재작업): 괄호 안 추가 단어' 'fix(FIX-999/hooks): 슬래시' 'fix(FIX-999; FIX-998): 세미콜론' 'fix(FIX-999)(hooks): 괄호 둘' \
         'fix-hooks(FIX-999): 유형에 하이픈' 'fix2(FIX-999): 유형에 숫자' 'fix[FIX-999]: 대괄호' 'fix: FIX-999 제목 뒤' \
         'fix(FIX_999): 밑줄' 'fix(FIX 999): 공백' ; do
  draft "$t"; show "$t" DENY "$(run)"; done
draft $'fix(FIX-999): 정상\r\n\r\n본문\r\n'; show 'fix(FIX-999) CRLF 초안 (회귀)' DENY "$(run)"
draft "$(printf ' \tfix(FIX-999): 선행 공백')"; show '제목 앞 공백·탭 (strip 되어 검사되나)' DENY "$(run)"

echo "== C. 검증 줄 문구 (F-27-4 추가 형태) — review 문서는 R-27-3 기준 충족 상태 =="
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
draft 'fix(FIX-999): 검증줄'
for line in '검증: 통과 — 메인 세션 (verifier 생략)' '검증: 통과(점검표 1~8) — verifier 리뷰는 아직' '검증: 통과 — verifier 리뷰 생략(문서만)' \
            '검증: 통과 — 메인 세션, verifier 는 다음 커밋에서' '검증: 통과 — verifier 아님' '검증: 통과하지 못함 — verifier (fable) 보류' \
            '검증: 통과 — Verifier (fable)' '검증:통과—verifier' ; do
  printf '%s\n' "$line" > "$T/docs/wiki/fixes/FIX-999.md"
  case "$line" in *'Verifier (fable)'|'검증:통과—verifier') exp=allow ;; *) exp=DENY ;; esac
  show "$line" "$exp" "$(run)"; done
printf '검증: (verifier 가 쓴다)\n\n## 결과\n검증: 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show '검증: 줄 두 개(자리표 + 결과 절의 통과)' DENY "$(run)"
printf '검증: 보류 — verifier (fable) [필수] 1건\n검증: 통과 — verifier (fable) 이전 판정\n' > "$T/docs/wiki/fixes/FIX-999.md"; show '검증: 보류가 먼저, 통과가 뒤(옛 판정 잔존)' DENY "$(run)"
printf '검증: 통과 — verifier (fable) 2026-10-08, review-FIX-999.md\n' > "$T/docs/wiki/fixes/FIX-999.md"; show '기준: 정상 통과 줄' allow "$(run)"

echo "== D. fail-closed 추가 경로 — 출력이 항상 유효 JSON 인가 =="
draft_raw "$(printf '\xff\xfefix(FIX-999)\n')"; out="$(run)"; show '초안 자체가 UTF-8 아님(outer except 경로)' DENY "$out"; json_ok "$out"
draft 'fix(FIX-999): 리뷰 비UTF8'
printf '\xff\xfe\xff\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
out="$(run)"; show 'review 문서가 UTF-8 아님' DENY "$out"; json_ok "$out"
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
# review 문서가 디렉터리인 경우
rm -f "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git rm -q --cached docs/wiki/fixes/review-FIX-999.md ) >/dev/null 2>&1
mkdir -p "$T/docs/wiki/fixes/review-FIX-999.md"; out="$(run)"; show 'review-FIX-999.md 가 디렉터리' DENY "$out"; json_ok "$out"
rmdir "$T/docs/wiki/fixes/review-FIX-999.md"
# deny() 가 줄바꿈·따옴표·역슬래시를 안전하게 내는가 (규칙 1 메시지에 ROOT 경로가 들어가지 않으므로 규칙 6 메시지로 확인)
printf '검증: 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
show '기준: 정상(회복 확인)' allow "$(run)"
# 저장소 경로에 따옴표·공백이 있을 때 (deny 메시지에 경로가 섞이는 rc=2 경로)
Q="$(mktemp -d)/we\"ird dir"; mkdir -p "$Q/.claude"; cp "$T/.claude/commit-draft.txt" "$T/.claude/.commit-approved" "$Q/.claude/"
out="$(printf '%s' "$(mk 'git commit -F .claude/commit-draft.txt')" | CLAUDE_PROJECT_DIR="$Q" bash "$H/commit-guard.sh")"
show 'ROOT 경로에 따옴표·공백 + git 저장소 아님' DENY "$out"; json_ok "$out"; rm -rf "$(dirname "$Q")"

echo "== E. 회귀 — 비-FIX 커밋·문서만 바꾼 FIX·규칙 1~5 =="
( cd "$T" && git reset -q app/a.py ) 2>/dev/null
printf 'doc\n' > "$T/docs/x.md"; ( cd "$T" && git add docs/x.md )
rm -f "$T/docs/wiki/fixes/FIX-999.md"
draft 'fix(FIX-999): 문서만'; show 'docs/ 만 스테이징한 fix(FIX-999) → 검증 줄 없어도 allow' allow "$(run)"
draft 'harness(FIX-999): 훅만'; printf 'h\n' > "$T/.claude/hooks_x.sh"; ( cd "$T" && git add .claude/hooks_x.sh ); show '.claude/ 만 스테이징한 harness(FIX-999) → allow' allow "$(run)"
( cd "$T" && git add app/a.py )
draft 'feat(P7-push): 제품 코드'; show 'feat(P7-push) + app/ → 규칙 6 미적용 allow' allow "$(run)"
draft 'docs(readme): 문서'; show 'docs(readme) + app/ → 규칙 6 미적용 allow' allow "$(run)"
show '규칙 2: -m' DENY "$(run 'git commit -m x')"
show '규칙 4: --amend' DENY "$(run 'git commit --amend -F .claude/commit-draft.txt')"
show '규칙 1: 마커 없음' DENY "$(rm -f "$T/.claude/.commit-approved"; run)"; approve
show 'git status (커밋 아님) allow' allow "$(run 'git status')"
show 'git log --all (commit 아닌 명령에 --all) allow' allow "$(run 'git log --all --oneline')"
show 'git add -i 는 commit-guard 대상 아님(allow; safety-guard 몫)' allow "$(run 'git add -i app/a.py')"

echo "== F. 실제 저장소(FIX-027 커밋 자체) — 규칙 6 단독 판정 =="
cd "$PROJ"
printf 'harness(FIX-027): 재작업 커밋 제목 가정\n\n본문\n' > "$T/draft027.txt"
"$HOOK_PY" "$PROJ/.claude/scripts/fix_guard_check.py" "$PROJ" "$T/draft027.txt"; echo "       현재 스테이징(0개) + harness(FIX-027) 제목 → rc=$? (0 이면 규칙 6 해당 없음)"
printf 'fix(FIX-027): 재작업 커밋 제목 가정\n\n본문\n' > "$T/draft027.txt"
"$HOOK_PY" "$PROJ/.claude/scripts/fix_guard_check.py" "$PROJ" "$T/draft027.txt"; echo "       fix(FIX-027) 제목 → rc=$?"
echo "       (app/·alembic/ 스테이징 없음: $(git diff --cached --name-only | grep -cE '^(app|alembic)/') 개)"

echo "== G. stage-gate — 실제 저장소 상태(active: P7-push)에서 보호 경로·frozen 상호작용 =="
gate() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'file_path':sys.argv[1]}}))" "$1"; }
for p in .claude/hooks/commit-guard.sh .claude/scripts/fix_guard_check.py .claude/settings.json .github/workflows/tests.yml .claude/commit-draft.txt .claude/gitlog.md .claude/skills/devlog/SKILL.md .claude/agents/verifier.md docs/wiki/CURRENT.md; do
  out="$(printf '%s' "$(gate "$PROJ/$p")" | bash "$H/stage-gate.sh")"
  if [ -z "$out" ]; then echo "ok   [allow] stage-gate $p"; else echo "!!   [DENY] stage-gate $p -> $(printf '%s' "$out" | head -c 120)"; fi
done
# frozen 상태에서 훅 경로가 막히는가(동결 중 하네스 수리 불가 — 메모용)
SG="$(mktemp -d)"; mkdir -p "$SG/docs/wiki"; printf 'active: P7-push\nfrozen: CR-009\n' > "$SG/docs/wiki/CURRENT.md"
out="$(printf '%s' "$(gate "$SG/.claude/hooks/x.sh")" | CLAUDE_PROJECT_DIR="$SG" bash "$H/stage-gate.sh")"
if printf '%s' "$out" | grep -q '"deny"'; then echo "메모  [DENY] frozen 중 .claude/hooks/ 쓰기 (동결 중 훅 수리는 CR 해제 뒤에만 가능)"; else echo "메모  [allow] frozen 중 .claude/hooks/ 쓰기"; fi
printf 'active: FIX-999\nfrozen: none\n' > "$SG/docs/wiki/CURRENT.md"; mkdir -p "$SG/docs/wiki/fixes"
printf '계획 점검: 통과\n승인: 사용자\n' > "$SG/docs/wiki/fixes/FIX-999.md"
out="$(printf '%s' "$(gate "$SG/.claude/hooks/x.sh")" | CLAUDE_PROJECT_DIR="$SG" bash "$H/stage-gate.sh")"
if [ -z "$out" ]; then echo "ok   [allow] active: FIX-nnn(계획 점검: 통과+승인) 으로 .claude/hooks/ 쓰기 — 활성 패키지 없이도 훅 수리 가능(교착 없음)"; else echo "!!   [DENY] active FIX 로도 훅 쓰기 불가 -> $(printf '%s' "$out" | head -c 120)"; fi
# 패키지 쪽: 승인 없는 패키지로는 훅도 못 쓴다(게이트가 실제로 걸림)
printf 'active: P9-x\nfrozen: none\n' > "$SG/docs/wiki/CURRENT.md"; mkdir -p "$SG/docs/wiki/packages/P9-x"; printf '# plan\n' > "$SG/docs/wiki/packages/P9-x/01-plan.md"
out="$(printf '%s' "$(gate "$SG/.claude/hooks/x.sh")" | CLAUDE_PROJECT_DIR="$SG" bash "$H/stage-gate.sh")"
if printf '%s' "$out" | grep -q '"deny"'; then echo "ok   [DENY] 02-plan-verify 없는 패키지로 .claude/hooks/ 쓰기 (R-27-5 가 실제로 건다)"; else echo "!!   [allow] 02-plan-verify 없는데 훅 쓰기 허용"; fi
rm -rf "$SG"

echo "== H. 변이 시험 — test-guards 의 새 케이스가 깨진 검사를 실제로 잡는가 (복사본만 변이, 원본 무변경) =="
M="$(mktemp -d)"; mkdir -p "$M/.claude/hooks" "$M/.claude/scripts"
cp "$H/commit-guard.sh" "$H/_py.sh" "$M/.claude/hooks/"; cp "$PROJ/.claude/scripts/fix_guard_check.py" "$M/.claude/scripts/"
# 변이 1: 검증 줄 검사를 항상 True 로
sed -i '' 's/^    pattern = re.compile(r"^검증:\\s\*통과\\b.\*verifier", re.IGNORECASE)$/    return True/' "$M/.claude/scripts/fix_guard_check.py"
grep -c '^    return True$' "$M/.claude/scripts/fix_guard_check.py" | sed 's/^/       변이1 적용 줄 수: /'
printf '검증: 보류 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md app/a.py )
draft 'fix(FIX-999): 변이'
out="$(printf '%s' "$(mk 'git commit -F .claude/commit-draft.txt')" | CLAUDE_PROJECT_DIR="$T" bash "$M/.claude/hooks/commit-guard.sh")"
if [ -z "$out" ]; then echo "ok   변이1(검증 줄 검사 무력화) → 보류 판정이 allow 로 뒤집힘 = F-27-4 케이스가 이 결함을 잡는다"; else echo "!!   변이1인데도 DENY (케이스가 검사를 안 보고 있을 가능성)"; fi
# 변이 2: F-27-3 플래그 검사 제거
cp "$H/commit-guard.sh" "$M/.claude/hooks/commit-guard.sh"; cp "$PROJ/.claude/scripts/fix_guard_check.py" "$M/.claude/scripts/"
sed -i '' 's/(-a|--all|-i|--include|-o|--only)/(--never-match-xyz)/' "$M/.claude/hooks/commit-guard.sh"
out="$(printf '%s' "$(mk 'git commit -a -F .claude/commit-draft.txt')" | CLAUDE_PROJECT_DIR="$T" bash "$M/.claude/hooks/commit-guard.sh")"
if printf '%s' "$out" | grep -q '"deny"'; then echo "!!   변이2(-a 검사 제거)인데도 -a 가 DENY (다른 규칙에 걸림?) -> $(printf '%s' "$out" | head -c 100)"; else echo "ok   변이2(-a 검사 제거) → git commit -a 가 allow 로 뒤집힘 = F-27-3 케이스가 이 결함을 잡는다"; fi
rm -rf "$M" "$T"
echo "== 끝 =="
