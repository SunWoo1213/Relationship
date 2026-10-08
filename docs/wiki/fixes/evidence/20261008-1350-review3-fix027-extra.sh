#!/usr/bin/env bash
# 3차 리뷰 보충: (1) A-전치 형태가 FIX-027 이전(HEAD) 훅에서도 같은지 — 기존 구멍인지 판별
#               (2) `>(cat) app/a.py` 가 실제 git 에서 커밋되는지  (3) C절 라벨 오류 정정 케이스
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
PROJ="/Users/sunwoo/Desktop/Portfolio/Relationship"
H="$PROJ/.claude/hooks"
. "$H/_py.sh"
D='.claude/commit-draft.txt'
mk() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'command':sys.argv[1]}}))" "$1"; }
verdict() { if printf '%s' "$1" | grep -q '"deny"'; then echo DENY; elif [ -z "$1" ]; then echo allow; else echo OTHER; fi; }

echo "== (1) HEAD(FIX-027 이전) 훅 vs 작업 트리 훅 — 마커 없는 격리 저장소 (기대: 규칙 1 DENY) =="
OLD="$(mktemp -d)"; mkdir -p "$OLD/.claude/hooks"
( cd "$PROJ" && git show HEAD:.claude/hooks/commit-guard.sh > "$OLD/.claude/hooks/commit-guard.sh" && cp .claude/hooks/_py.sh "$OLD/.claude/hooks/" )
T="$(mktemp -d)"; mkdir -p "$T/.claude"
printf '%-58s %-8s %-8s\n' "명령(마커 없음)" "HEAD훅" "작업트리훅"
for c in "git commit -m x" "/usr/bin/git commit -m x" "bash -c \"git commit -m x\"" "sh -c 'git commit -m x'" "eval \"git commit -m x\"" \
         "(git commit -m x)" "git -c alias.ci=commit ci -m x" "echo \$(git commit -m x)" "git.exe commit -m x" "echo a | xargs git commit -m x" \
         "git commit -n -F $D" ; do
  o="$(verdict "$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$OLD/.claude/hooks/commit-guard.sh")")"
  n="$(verdict "$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh")")"
  printf '%-58s %-8s %-8s %s\n' "$c" "$o" "$n" "$([ "$o" = "$n" ] && echo '동일(기존 동작)' || echo '달라짐')"
done
rm -rf "$OLD" "$T"

echo "== (2) 실제 git: >(cat) app/a.py / <(true) app/a.py 가 미스테이징 app/a.py 를 커밋에 넣는가 =="
T="$(mktemp -d)"; mkdir -p "$T/.claude" "$T/app"
( cd "$T" && git init -q . && git config user.email t@example.com && git config user.name tester \
  && printf 'init\n' > README.md && git add README.md && git commit -qm init \
  && printf 'y\n' > app/a.py && git add app/a.py && git commit -qm "app 추적" ) >/dev/null 2>&1
printf 'feat(P7-push): x\n\n본문\n' > "$T/$D"
printf 'z\n' > "$T/app/a.py"
( cd "$T" && git commit -q -F $D >(cat) app/a.py; echo "       rc=$? HEAD=$(git log -1 --format=%s) 변경파일=[$(git show --stat --format= HEAD | grep -c 'app/a.py')]" ) 2>&1 | sed 's/^/       >(cat): /'
( cd "$T" && git commit -q -F $D <(true) app/a.py; echo "       rc=$? HEAD=$(git log -1 --format=%s) 변경파일=[$(git show --stat --format= HEAD | grep -c 'app/a.py')]" ) 2>&1 | sed 's/^/       <(true): /'
( cd "$T" && git commit -q -F $D 2>(cat) app/a.py; echo "       rc=$? HEAD=$(git log -1 --format=%s) 변경파일=[$(git show --stat --format= HEAD | grep -c 'app/a.py')]" ) 2>&1 | sed 's/^/       2>(cat): /'
echo "       (작업 트리 app/a.py 미스테이징 상태 유지: $(cd "$T" && git status --short app/a.py))"
rm -rf "$T"

echo "== (3) C절 정정: 제목에 FIX 번호 없음(본문 Refs 에만) → allow =="
T="$(mktemp -d)"; mkdir -p "$T/.claude" "$T/app" "$T/docs/wiki/fixes"
( cd "$T" && git init -q . && git config user.email t@example.com && git config user.name tester \
  && printf 'init\n' > README.md && git add README.md && git commit -qm init && printf 'x\n' > app/a.py && git add app/a.py ) >/dev/null 2>&1
printf 'feat(P7-push): 접두사 처리\n\n본문\nRefs: P7-push FIX-999\n' > "$T/$D"
"$HOOK_PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$T/$D" > "$T/.claude/.commit-approved"
out="$(printf '%s' "$(mk "git commit -F $D")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh")"
echo "       제목 'feat(P7-push): 접두사 처리' + 본문 'Refs: … FIX-999' + app/ 스테이징 → $(verdict "$out") (기대 allow — 정책: 제목만 본다)"
rm -rf "$T"
echo "== 끝 =="
