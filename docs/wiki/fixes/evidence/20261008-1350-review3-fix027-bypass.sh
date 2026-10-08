#!/usr/bin/env bash
# verifier 3차 리뷰(FIX-027 2차 재작업) — 허용 목록 파서(commit_args_check.py)·부정어 목록(fix_guard_check.py)·
# 정상 흐름·회귀·이 커밋 자체 통과 여부. 판독: ok=기대와 일치, !!=기대와 다름, 메모=판정에 안 넣는 관찰.
# 실행: bash <이 파일>  (scratchpad 에서 실행, 출력은 같은 접두 -bypass.txt)
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
PROJ="/Users/sunwoo/Desktop/Portfolio/Relationship"
H="$PROJ/.claude/hooks"
. "$H/_py.sh"
D='.claude/commit-draft.txt'
T="$(mktemp -d)"
mkdir -p "$T/.claude" "$T/app" "$T/docs/wiki/fixes"
( cd "$T" && git init -q . && git config user.email t@example.com && git config user.name tester \
  && printf 'init\n' > README.md && git add README.md && git commit -qm init \
  && printf 'y\n' > app/a.py && git add app/a.py && git commit -qm "app 추적" ) >/dev/null 2>&1
printf 'z\n' > "$T/app/a.py"            # 작업 트리만 수정(미스테이징)
printf 'app/a.py\n' > "$T/paths.txt"

mk() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'command':sys.argv[1]}}))" "$1"; }
approve() { "$HOOK_PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$T/$D" > "$T/.claude/.commit-approved"; }
draft() { printf '%s\n\n본문\n' "$1" > "$T/$D"; approve; }
run() { printf '%s' "$(mk "${1:-git commit -F $D}")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh"; }
reason() { printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d["hookSpecificOutput"]["permissionDecisionReason"][:150])
except Exception as e: print("(JSON 아님) "+str(e))'; }
show() {  # show <라벨> <기대 DENY|allow> <출력>
  local v
  if printf '%s' "$3" | grep -q '"deny"'; then v=DENY; elif [ -z "$3" ]; then v=allow; else v=OTHER; fi
  if [ "$v" = "$2" ]; then echo "ok   [$v] $1"; else echo "!!   [$v] (기대 $2) $1"; fi
  [ -n "$3" ] && printf '       -> %s\n' "$(reason "$3")"
}
memo() { local v; if printf '%s' "$3" | grep -q '"deny"'; then v=DENY; elif [ -z "$3" ]; then v=allow; else v=OTHER; fi
  echo "메모 [$v] $1 (참고 기대 $2)"; [ -n "$3" ] && printf '       -> %s\n' "$(reason "$3")"; }
json_ok() { printf '%s' "$1" | "$HOOK_PY" -c 'import sys,json
json.load(sys.stdin)' >/dev/null 2>&1 && echo "       훅 stdout 유효 JSON" || echo "       !! 훅 stdout 이 유효 JSON 이 아님"; }

draft 'feat(P7-push): 인자 시험'   # 규칙 6 비대상 제목 — 인자 검사(규칙 5b)만 본다

echo "== A. 허용 목록 파서 — 셸 문법 형태 (app/a.py 는 추적·미스테이징) =="
show "따옴표: git commit -F '$D' app/a.py" DENY "$(run "git commit -F '$D' app/a.py")"
show "따옴표: git commit -F $D 'app/a.py'" DENY "$(run "git commit -F $D 'app/a.py'")"
show "따옴표: git commit -F $D \"app/a.py\"" DENY "$(run "git commit -F $D \"app/a.py\"")"
show "이스케이프: git commit -F $D app/a\\.py" DENY "$(run "git commit -F $D app/a\\.py")"
show "명령 치환: git commit -F $D \$(echo app/a.py)" DENY "$(run "git commit -F $D \$(echo app/a.py)")"
show "백틱: git commit -F $D \`echo app/a.py\`" DENY "$(run "git commit -F $D \`echo app/a.py\`")"
show "역슬래시 줄바꿈: git commit -F $D \\<NL>app/a.py" DENY "$(run "$(printf 'git commit -F %s \\\nnapp/a.py' "$D" | sed 's/nnapp/app/')")"
show "서브셸: (git commit -F $D app/a.py)" DENY "$(run "(git commit -F $D app/a.py)")"
show "서브셸+cd: ( cd . ; git commit app/a.py -F $D )" DENY "$(run "( cd . ; git commit app/a.py -F $D )")"
show "env git commit -F $D app/a.py" DENY "$(run "env git commit -F $D app/a.py")"
show "command git commit -F $D app/a.py" DENY "$(run "command git commit -F $D app/a.py")"
show "exec git commit -F $D app/a.py" DENY "$(run "exec git commit -F $D app/a.py")"
show "공백 없는 구분자: git commit -F $D;git commit app/a.py -F $D" DENY "$(run "git commit -F $D;git commit app/a.py -F $D")"
show "공백 없는 구분자: git commit -F $D&&git commit -a -F $D" DENY "$(run "git commit -F $D&&git commit -a -F $D")"
show "git -c a=b -c c=d commit -F $D app/a.py" DENY "$(run "git -c a=b -c c=d commit -F $D app/a.py")"
show "git --git-dir=.git commit -F $D app/a.py" DENY "$(run "git --git-dir=.git commit -F $D app/a.py")"
show "git --git-dir .git --work-tree . commit -F $D app/a.py" DENY "$(run "git --git-dir .git --work-tree . commit -F $D app/a.py")"
show "-n(=--no-verify 단축, 옛 규칙 4 는 문자열 --no-verify 만 봤다): git commit -n -F $D" DENY "$(run "git commit -n -F $D")"
show "--signoff/--allow-empty/-q 등 허용 목록 밖 옵션: git commit -q -F $D" DENY "$(run "git commit -q -F $D")"
show "-F 붙여쓰기(git 은 허용): git commit -F$D" DENY "$(run "git commit -F$D")"
show "--file= 뒤 --: git commit --file=$D --" DENY "$(run "git commit --file=$D --")"
show "리다이렉션 뒤 경로: git commit -F $D 2>&1 app/a.py" DENY "$(run "git commit -F $D 2>&1 app/a.py")"
show "리다이렉션 >(…) 뒤 경로: git commit -F $D >(cat) app/a.py" DENY "$(run "git commit -F $D >(cat) app/a.py")"
show "변수 경로(fail-closed): D=$D; git commit -F \$D" DENY "$(run "DR=$D; git commit -F \$DR")"
show "홈 변수 경로(fail-closed): git commit -F \"\$PWD/$D\"" DENY "$(run "git commit -F \"\$PWD/$D\"")"
show "\$'…' 인용: git commit -F $D \$'app/a.py'" DENY "$(run "git commit -F $D \$'app/a.py'")"
show "파이프 뒤 commit: echo x | git commit -F $D app/a.py" DENY "$(run "echo x | git commit -F $D app/a.py")"
out="$(run "git commit -F $D \"app/a b.py\"")"; show "deny 출력 JSON 안전성: 따옴표·공백 경로" DENY "$out"; json_ok "$out"
out="$(run "$(printf 'git commit -F %s app/\\"q\\".py\\\\x' "$D")")"; show "deny 출력 JSON 안전성: 따옴표·역슬래시 섞인 인자" DENY "$out"; json_ok "$out"
show "따옴표 불일치(fail-closed): git commit -F $D \"app/a.py" DENY "$(run "git commit -F $D \"app/a.py")"

echo "== A-허용. 정상 형태(오탐 없어야) =="
show "정상: git commit -F $D" allow "$(run "git commit -F $D")"
show "정상: git commit --file=$D" allow "$(run "git commit --file=$D")"
show "정상: git add a b && git commit -F $D" allow "$(run "git add README.md paths.txt && git commit -F $D")"
show "정상: git commit -F $D && git push origin dev2" allow "$(run "git commit -F $D && git push origin dev2")"
show "정상: git commit -F $D | cat" allow "$(run "git commit -F $D | cat")"
show "정상: git commit -F $D >/dev/null 2>&1" allow "$(run "git commit -F $D >/dev/null 2>&1")"
show "정상: git commit -F $D # 주석 app/a.py" allow "$(run "git commit -F $D # 주석 app/a.py")"
show "정상(두 줄): git add README.md<NL>git commit -F $D" allow "$(run "$(printf 'git add README.md\ngit commit -F %s' "$D")")"
memo "단따옴표 초안 경로: git commit -F '$D' (파서 allow, 규칙 2 case 는 DENY — 불일치지만 fail-closed)" allow "$(run "git commit -F '$D'")"
memo "이중 공백: git commit -F  $D (규칙 2 case 가 단일 공백만 — fail-closed)" allow "$(run "git commit -F  $D")"
memo "인용된 연산자: git commit -F $D '&&' app/a.py (파서는 && 를 구분자로 보고 allow; 실제 git 은 pathspec '&&' 불일치로 실패)" DENY "$(run "git commit -F $D '&&' app/a.py")"
( cd "$T" && git commit -q -F $D '&&' app/a.py ) 2>&1 | sed 's/^/       실제 git: /'

echo "== A-전치. 셸 감지 정규식(bash grep) 앞단을 빗나가는 형태 — 규칙 1~6 전체가 건너뛰어지는지 (마커 제거 상태) =="
rm -f "$T/.claude/.commit-approved"
show "마커 없음 기준: git commit -F $D → 규칙 1 DENY" DENY "$(run "git commit -F $D")"
show "/usr/bin/git commit -F $D app/a.py (마커 없음)" DENY "$(run "/usr/bin/git commit -F $D app/a.py")"
show "bash -c \"git commit -a -F $D\" (마커 없음)" DENY "$(run "bash -c \"git commit -a -F $D\"")"
show "sh -c 'git commit -m x' (마커 없음)" DENY "$(run "sh -c 'git commit -m x'")"
show "eval \"git commit -m x\" (마커 없음)" DENY "$(run "eval \"git commit -m x\"")"
show "git -c alias.ci=commit ci -a -F $D (마커 없음)" DENY "$(run "git -c alias.ci=commit ci -a -F $D")"
show "echo app/a.py | xargs git commit -F $D (마커 없음 — git commit 자체는 감지됨)" DENY "$(run "echo app/a.py | xargs git commit -F $D")"
show "\$(git commit -m x) (마커 없음)" DENY "$(run "echo \$(git commit -m x)")"
show "git.exe commit -m x (Windows 표기, 마커 없음)" DENY "$(run "git.exe commit -m x")"
approve
show "마커 있음: echo app/a.py | xargs git commit -F $D (xargs 가 경로를 덧붙임)" DENY "$(run "echo app/a.py | xargs git commit -F $D")"
echo "       실제 git 재현(xargs):"; ( cd "$T" && echo app/a.py | xargs git commit -q -F $D && git show --stat --format=%s HEAD | grep -E 'app/a.py' ) 2>&1 | sed 's/^/       /'
printf 'w\n' > "$T/app/a.py"

echo "== A-환경. GIT_* 접두 변형 (R-27-8) =="
show "GIT_INDEX_FILE=x git commit -F $D" DENY "$(run "GIT_INDEX_FILE=x git commit -F $D")"
show "export GIT_INDEX_FILE=x; git commit -F $D" DENY "$(run "export GIT_INDEX_FILE=x; git commit -F $D")"
show "env GIT_INDEX_FILE=x git commit -F $D" DENY "$(run "env GIT_INDEX_FILE=x git commit -F $D")"
show "GIT_DIR=/x GIT_WORK_TREE=/y git commit -F $D" DENY "$(run "GIT_DIR=/x GIT_WORK_TREE=/y git commit -F $D")"
memo "git -c core.hooksPath=/dev/null commit -F $D (commit-guard 는 allow; safety-guard 몫)" allow "$(run "git -c core.hooksPath=/dev/null commit -F $D")"
out="$(printf '%s' "$(mk "git -c core.hooksPath=/dev/null commit -F $D")" | CLAUDE_PROJECT_DIR="$T" bash "$H/safety-guard.sh")"; show "같은 명령 safety-guard" DENY "$out"
memo "FOO=1 git commit -F $D (GIT_ 아닌 접두 — allow 가 맞다)" allow "$(run "FOO=1 git commit -F $D")"

echo "== B. 검증: 줄 — 부정어 목록 회피·오탐 (app/ 스테이징, review 문서 R-27-3 충족) =="
( cd "$T" && git add app/a.py )
printf '검토자: verifier (fable)\n' > "$T/docs/wiki/fixes/review-FIX-999.md"; ( cd "$T" && git add docs/wiki/fixes/review-FIX-999.md )
draft 'fix(FIX-999): 검증줄'
vl() { printf '%s\n' "$1" > "$T/docs/wiki/fixes/FIX-999.md"; }
for line in \
  '검증: 통과 — verifier 미검토' '검증: 통과 — verifier 리뷰 없이' '검증: 통과 — verifier 없음' '검증: 통과 — verifier 스킵' \
  '검증: 통과 — verifier (메인 세션 작성)' '검증: 통과 — verifier 불필요' '검증: 통과 — verifier TODO' '검증: 통과 — verifier 보류' \
  '검증: 통과 — verifier (보류, [필수] 2건)' '검증: 통과 — verifier 추후' ; do
  vl "$line"; memo "부정어 목록 밖 표현: $line" DENY "$(run)"; done
for line in '검증: 통过 — verifier' '검증: 통과 — verifier 가 보지 않음' '검증: 통과 — verifier 를 거치지 못함' '검증: 통과 — verifier (메인 세션이 대신 씀)' \
  '검증: 통과 — verifier 생략' '검증: 통과 · verifier (fable)' '검증: 통과 (verifier (fable))' '검증 : 통과 — verifier (fable)' ; do
  vl "$line"; show "거부돼야: $line" DENY "$(run)"; done
echo "-- 정상 판정 줄이 부정어 목록에 걸리는 오탐(fail-closed, verifier 가 어휘를 피해야 함) --"
for line in '검증: 통과 — verifier (fable) 2026-10-08, review-FIX-999.md (R-27-2 제외, 이월)' \
  '검증: 통과 — verifier (fable) 2026-10-08 — 남은 권고는 별도 FIX 예정' \
  '검증: 통과 — verifier (fable) — 아직 Windows CI 미확인' ; do
  vl "$line"; memo "오탐 후보: $line" allow "$(run)"; done
vl '검증: 통과 — verifier 3차 리뷰 (review-FIX-999.md)'; show "이번 리뷰가 쓸 형태: 검증: 통과 — verifier 3차 리뷰 (review-FIX-nnn.md)" allow "$(run)"
vl '검증: 통과 — verifier (fable) 2026-10-08, review-FIX-999.md'; show "SKILL 6단계 예시 형태" allow "$(run)"
printf '  검증: 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show "들여쓴 검증: 줄(strip 후 검사)" allow "$(run)"
printf '**검증:** 통과 — verifier (fable)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show "굵게 표기 **검증:** (줄 0개 → 거부)" DENY "$(run)"
printf '검증: 통과 — verifier (fable)\n> 검증: 옛 줄 인용\n' > "$T/docs/wiki/fixes/FIX-999.md"; show "인용 블록 '> 검증:' 은 세지 않음 → allow" allow "$(run)"
printf '검증: 통과 — verifier (fable)\n검증: 줄은 verifier 가 쓴다(설명 문장)\n' > "$T/docs/wiki/fixes/FIX-999.md"; show "설명 문장이 줄 첫머리에 검증: 으로 시작 → 2줄 → DENY(fail-closed)" DENY "$(run)"

echo "== C. 제목 ID 추출(R-27-7) 경계 =="
rm -f "$T/docs/wiki/fixes/FIX-999.md"
for t in 'fix(FIX_999): 밑줄' 'fix(FIX 999): 공백' ; do draft "$t"; memo "범위 밖(사용자 결정): $t" DENY "$(run)"; done
for t in 'Fix-999 제목' 'fix: fix-0999 소문자' 'harness(FIX-999): x' ; do draft "$t"; show "대상: $t" DENY "$(run)"; done
draft 'feat(P7-push): hotfix-999 적용'; memo "오탐 후보: 'hotfix-999' 가 FIX-999 로 잡혀 DENY(ID_RE 에 단어 경계 없음)" allow "$(run)"
draft 'feat(P7-push): prefix-3 처리'; memo "오탐 후보: 'prefix-3' → FIX-003.md(옛 템플릿 검증 줄) 검사" allow "$(run)"
draft 'feat(P7-push): 접두사 처리 (Refs 본문에만 FIX-999)'; show "제목에 FIX 번호 없음 → 대상 밖 allow" allow "$(run)"
# ↑ 마지막 케이스는 라벨 오류: 제목 괄호 안에 FIX-999 를 넣어 두었으므로 DENY 가 맞다. 정정 케이스는 -extra.sh (3).

echo "== D. 이 커밋(FIX-027 자체) — 실제 저장소 =="
cd "$PROJ"
for t in 'harness(FIX-027): FIX 에도 verifier 검증을 커밋 훅으로 강제' 'fix(FIX-027): x' 'harness(hooks): FIX-027 2차 재작업'; do
  printf '%s\n\n본문\n' "$t" > "$T/d027.txt"
  "$HOOK_PY" "$PROJ/.claude/scripts/fix_guard_check.py" "$PROJ" "$T/d027.txt"; echo "       제목 '$t' → fix_guard_check rc=$? (스테이징 app/·alembic/ $(git diff --cached --name-only | grep -cE '^(app|alembic)/') 개)"
done
printf '%s' "git commit -F $D" | "$HOOK_PY" "$PROJ/.claude/scripts/commit_args_check.py"; echo "       commit 스킬 명령 'git commit -F $D' → commit_args_check rc=$?"
out="$(printf '%s' "$(mk "git commit -F $D")" | bash "$H/commit-guard.sh")"; echo "       실제 저장소(마커 없음) 훅 판정 → $(reason "$out")"
echo "       FIX-027.md '^검증:' 줄 수: $(grep -c '^검증:' docs/wiki/fixes/FIX-027.md) / review-FIX-027.md '검토자: verifier' 줄: $(grep -c '^검토자:.*verifier' docs/wiki/fixes/review-FIX-027.md)"
# 가정: 이 FIX 문서를 app/ 변경 FIX 로 취급했을 때 통과하는가(격리 저장소에 복사)
mkdir -p "$T/docs/wiki/fixes"; cp docs/wiki/fixes/FIX-027.md "$T/docs/wiki/fixes/FIX-027.md"; cp docs/wiki/fixes/review-FIX-027.md "$T/docs/wiki/fixes/review-FIX-027.md"
( cd "$T" && git add docs/wiki/fixes/review-FIX-027.md app/a.py ) >/dev/null 2>&1
cd "$T"; draft 'fix(FIX-027): 가정'; cd "$PROJ"
memo "현재 FIX-027.md(검증: 보류 줄) 를 app/ 변경 FIX 로 가정 → DENY 가 맞다" DENY "$(run)"
"$HOOK_PY" - "$T/docs/wiki/fixes/FIX-027.md" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
s=re.sub(r"^검증:.*$", "검증: 통과 — verifier 3차 리뷰 (review-FIX-027.md)", s, count=1, flags=re.M)
open(p,"w",encoding="utf-8").write(s)
PY
show "검증: 줄을 '통과 — verifier 3차 리뷰 (review-FIX-027.md)' 로 바꾼 사본 + review 문서 스테이징 → allow(교착 없음)" allow "$(run)"

echo "== E. stage-gate 정상 흐름(실제 저장소 active: P7-push) =="
gate() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'file_path':sys.argv[1]}}))" "$1"; }
for p in .claude/hooks/commit-guard.sh .claude/scripts/commit_args_check.py .claude/settings.json .github/workflows/tests.yml app/main.py docs/wiki/fixes/review-FIX-027.md docs/wiki/fixes/FIX-027.md docs/wiki/fixes/evidence/x.txt; do
  out="$(printf '%s' "$(gate "$PROJ/$p")" | bash "$H/stage-gate.sh")"
  if [ -z "$out" ]; then echo "ok   [allow] stage-gate $p"; else echo "!!   [DENY] stage-gate $p -> $(reason "$out")"; fi
done

rm -rf "$T"
echo "== 끝 =="
