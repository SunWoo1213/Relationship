#!/usr/bin/env bash
# 변이 시험 2 (재시도): F-27-3 검사(-a/pathspec 두 grep)를 복사본에서 제거하면
#  (a) test-guards.sh 의 F-27-3 세 케이스(실제 저장소, 마커 없음)가 여전히 DENY 인가 → 그렇다면 그 케이스는 검사를 보지 않는다(항상 통과)
#  (b) 마커·초안이 갖춰진 격리 저장소 + feat 초안에서는 allow 로 뒤집히는가 → 검사의 실효성
set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
PROJ="/Users/sunwoo/Desktop/Portfolio/Relationship"
H="$PROJ/.claude/hooks"
. "$H/_py.sh"
mk() { "$HOOK_PY" -c "import json,sys;print(json.dumps({'tool_input':{'command':sys.argv[1]}}))" "$1"; }
M="$(mktemp -d)"; mkdir -p "$M/.claude/hooks" "$M/.claude/scripts"
cp "$H/commit-guard.sh" "$H/_py.sh" "$M/.claude/hooks/"; cp "$PROJ/.claude/scripts/fix_guard_check.py" "$M/.claude/scripts/"
sed -i '' 's/(-a|--all|-i|--include|-o|--only)/(--never-match-xyz)/; s/-F\[\[:space:\]\]+"?\\.claude\/commit-draft\\.txt"?\[\[:space:\]\]+\[^;&|\[:space:\]\]/--never-match-abc/' "$M/.claude/hooks/commit-guard.sh"
echo "변이 적용 확인(원본과 다른 줄):"; diff "$H/commit-guard.sh" "$M/.claude/hooks/commit-guard.sh" | grep '^>' | sed 's/^/   /'

echo "(a) 실제 저장소(마커 없음) — test-guards.sh 의 F-27-3 세 케이스를 변이 복사본으로:"
for c in 'git commit -a -F .claude/commit-draft.txt' 'git commit -F .claude/commit-draft.txt app/a.py' 'git commit --include app/a.py -F .claude/commit-draft.txt'; do
  out="$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$PROJ" bash "$M/.claude/hooks/commit-guard.sh")"
  reason="$(printf '%s' "$out" | "$HOOK_PY" -c 'import sys,json
try: print(json.load(sys.stdin)["hookSpecificOutput"]["permissionDecisionReason"][:60])
except Exception: print("(allow)")')"
  echo "   $c -> $reason"
done

echo "(b) 격리 저장소(마커·초안 있음, feat 초안) — 같은 세 명령을 변이 복사본으로:"
T="$(mktemp -d)"; mkdir -p "$T/.claude" "$T/app"
( cd "$T" && git init -q . && git config user.email t@example.com && git config user.name tester && printf 'init\n' > README.md && git add README.md && git commit -qm init ) >/dev/null 2>&1
printf 'feat(P7-push): 변이\n\n본문\n' > "$T/.claude/commit-draft.txt"
"$HOOK_PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$T/.claude/commit-draft.txt" > "$T/.claude/.commit-approved"
for c in 'git commit -a -F .claude/commit-draft.txt' 'git commit -F .claude/commit-draft.txt app/a.py' 'git commit --include app/a.py -F .claude/commit-draft.txt'; do
  out="$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$M/.claude/hooks/commit-guard.sh")"
  [ -z "$out" ] && echo "   $c -> allow (변이로 뒤집힘 = 검사가 실효)" || echo "   $c -> DENY: $(printf '%s' "$out" | head -c 80)"
done
echo "(c) 같은 격리 저장소를 원본 훅으로(대조):"
for c in 'git commit -a -F .claude/commit-draft.txt' 'git commit -F .claude/commit-draft.txt app/a.py'; do
  out="$(printf '%s' "$(mk "$c")" | CLAUDE_PROJECT_DIR="$T" bash "$H/commit-guard.sh")"
  [ -z "$out" ] && echo "   $c -> allow" || echo "   $c -> DENY"
done
rm -rf "$M" "$T"
