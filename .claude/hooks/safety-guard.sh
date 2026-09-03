#!/usr/bin/env bash
# PreToolUse(Bash|PowerShell) 훅 — 파괴적·유출성 명령 차단
#
# 규칙의 근거와 "대신 어떻게 하는가"는 docs/wiki/security.md 에 있다. 이 파일은 그 카드의 집행부다.
# 차단 범주:
#   A. 재귀 삭제 (rm -r, Remove-Item -Recurse, rd /s, shutil.rmtree …) — scratchpad 안은 허용
#   B. git 이력 파괴 (push --force, reset --hard, checkout -- ., clean, branch -D, stash drop, filter-branch …)
#   C. git push 는 origin 으로만, 승인 마커(.claude/.push-approved)가 있을 때만
#   D. git add 는 명시 경로만 (-A, ., --all 금지). 비밀 파일 스테이징 금지
#   E. 비밀 노출 (.env 읽기, 환경변수 KEY/SECRET/TOKEN 출력, ~/.aws/credentials, ~/.ssh)
#   F. 원격 코드 실행 (curl | sh, iex(DownloadString))
#   G. 권한·시스템 (sudo, chmod 777, mkfs, dd, shutdown …)
#   H. 인프라·데이터 파괴 (terraform destroy, aws delete-*, docker prune/down -v, DROP/TRUNCATE)
#   I. 외부로 데이터 전송 (curl -d/-F/-T 를 localhost 이외로, scp/sftp/rclone)
#   J. 훅 우회 (--no-verify, -c core.hooksPath=)
#
# stdin: {"tool_name":"Bash"|"PowerShell","tool_input":{"command":"..."}}
# 거부 시에만 permissionDecision JSON 을 출력한다.

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
PUSH_MARK="$ROOT/.claude/.push-approved"
RELEASE_MARK="$ROOT/.claude/.release-approved"

input="$(cat)"
cmd="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"
[ -n "$cmd" ] || exit 0

deny() {
  # 메시지에는 따옴표·백슬래시를 쓰지 않는다 (JSON 이스케이프 생략)
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[safety-guard] %s (근거: docs/wiki/security.md)"}}\n' "$1"
  exit 0
}
# bash 내장 ERE 매칭 (프로세스 생성 없음 — grep 파이프로 하면 규칙 40개에 호출당 3~4초 걸린다)
has()  { [[ $cmd =~ $1 ]]; }
hasi() { local r; shopt -s nocasematch; [[ $cmd =~ $1 ]]; r=$?; shopt -u nocasematch; return $r; }

# 명령 앵커: 줄 시작 또는 ; & | 공백 뒤
W='(^|[;&|[:space:]])'

# ---------- A. 재귀 삭제 ----------
in_scratch=0
case "$cmd" in *scratchpad*) in_scratch=1 ;; esac
if [ "$in_scratch" -eq 0 ]; then
  has "${W}rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)" && deny "재귀 삭제(rm -r)는 scratchpad 밖에서 금지. 파일을 하나씩 지정하거나 사용자에게 요청하라"
  has "${W}rm[[:space:]]+(-[a-zA-Z]*f[a-zA-Z]*[[:space:]]+)?/([[:space:]]|$)" && deny "루트 삭제 금지"
  hasi "remove-item[^;|]*-recurse|${W}(rd|rmdir)[[:space:]]+/s|${W}del[[:space:]]+/[sq]" && deny "재귀 삭제(Remove-Item -Recurse, rd /s)는 scratchpad 밖에서 금지"
  has "shutil[.]rmtree|${W}rimraf[[:space:]]|${W}find[[:space:]][^|;]*(-delete|-exec[[:space:]]+rm)" && deny "스크립트를 통한 재귀 삭제도 scratchpad 밖에서 금지"
fi

# ---------- J. 훅 우회 ----------
has "--no-verify|core[.]hooksPath=|--no-gpg-sign" && deny "훅 우회 옵션(--no-verify, core.hooksPath=) 금지"

# ---------- B. git 이력 파괴 ----------
GIT="${W}git([[:space:]]+-[^[:space:]]+([[:space:]]+[^[:space:]]+)?)*[[:space:]]+"
if has "${GIT}push([[:space:]]|$)"; then
  has "${GIT}push[^;|&]*([[:space:]]-f([[:space:]]|$)|--force|--mirror|--delete|[[:space:]][+][a-zA-Z])" && deny "강제 푸시(--force, -f, +ref, --mirror, --delete) 금지. 새 커밋으로 고치라"
  has "${GIT}push[^;|&]*[[:space:]](-u[[:space:]]+|--set-upstream[[:space:]]+)?origin([[:space:]]|$)" || deny "푸시는 origin 으로만 허용한다"
  # 브랜치 전략(L-001): 일상 푸시는 origin dev 로만. main 은 dev 를 실서버에서 검증한 뒤 /commit release 로 승격(dev:main)한다.
  if has "${GIT}push[^;|&]*[[:space:]]origin[[:space:]]+dev:main([[:space:]]|$)"; then
    [ -f "$RELEASE_MARK" ] || deny "main 승격(dev:main)은 dev 를 실서버에서 검증한 뒤 /commit release 에서 사용자가 승인해야 한다"
  elif has "${GIT}push[^;|&]*[[:space:]]origin[[:space:]]+dev([[:space:]]|$)"; then
    [ -f "$PUSH_MARK" ] || deny "푸시 승인 마커가 없다. /commit 절차에서 사용자가 푸시를 승인해야 한다"
  else
    deny "푸시는 origin dev 로만 한다. main 직접 푸시 금지 - dev 를 실서버에서 검증한 뒤 /commit release 로 승격(git push origin dev:main)"
  fi
fi
has "${GIT}reset[^;|&]*--hard" && deny "git reset --hard 금지. 되돌리려면 git revert 또는 사용자 요청"
has "${GIT}checkout[[:space:]]+(--[[:space:]]+|[.]([[:space:]]|$))|${GIT}checkout[[:space:]]+[^-][^;|&]*[[:space:]]--[[:space:]]" && deny "git checkout -- <경로> / checkout . 은 작업 내용을 버린다. 금지"
has "${GIT}restore[[:space:]]+([.]([[:space:]]|$)|--worktree|[^-][^;|&]*[[:space:]][.]([[:space:]]|$))" && deny "git restore . 은 작업 내용을 버린다. 금지 (--staged 로 스테이지만 내리는 것은 허용)"
has "${GIT}clean([[:space:]]|$)" && deny "git clean 금지"
has "${GIT}branch[[:space:]]+(-D|--delete[[:space:]]+--force|-[a-zA-Z]*D)" && deny "브랜치 강제 삭제(-D) 금지"
has "${GIT}stash[[:space:]]+(drop|clear)" && deny "stash drop/clear 금지"
has "${GIT}(filter-branch|filter-repo|replace)|${GIT}reflog[[:space:]]+expire|${GIT}update-ref[[:space:]]+-d|${GIT}gc[^;|&]*--prune" && deny "이력 재작성·정리 명령 금지"
has "${GIT}remote[[:space:]]+(set-url|remove|rm|rename)" && deny "원격 변경 금지. 사용자가 직접 한다"
has "${GIT}config[^;|&]*(credential|url[.]|remote[.]|user[.]email|user[.]name)" && deny "git 자격·원격·사용자 설정 변경 금지"

# ---------- D. git add ----------
if has "${GIT}add([[:space:]]|$)"; then
  has "${GIT}add[^;|&]*([[:space:]]-[a-zA-Z]*[Au][a-zA-Z]*([[:space:]]|$)|--all|--update|[[:space:]][.]([[:space:]]|$)|[[:space:]][*]([[:space:]]|$)|[[:space:]]:/)" && deny "git add 는 명시 경로만. -A, -u, ., * 금지 (비밀·임시 파일이 섞인다)"
  hasi "${GIT}add[^;|&]*([[:space:]]|/)([.]env([^.]|$)|[.]env[.](local|prod|dev|staging)|[^[:space:]]*[.](pem|key|p12|pfx|tfstate|tfvars)([[:space:]]|$)|id_rsa|id_ed25519)" && deny "비밀 파일(.env, *.pem, *.key, tfstate 등)은 스테이징 금지"
fi

# ---------- E. 비밀 노출 ----------
# .env 검사는 명령 첫 줄만 본다 (heredoc 본문에 ".env" 라는 글자가 들어가는 .gitignore 작성 등은 허용)
first="${cmd%%$'\n'*}"
ENV_RE='(^|[^A-Za-z0-9_./-])[.]env([^A-Za-z0-9_.]|$)'
ENV_OK_RE='^[[:space:]]*(cd[[:space:]]+[^;&|]*(&&|;)[[:space:]]*)?(ls|test|stat|git[[:space:]]+(status|check-ignore|ls-files)|[[]|find)[[:space:]]'
if [[ $first =~ $ENV_RE ]]; then
  [[ $first =~ $ENV_OK_RE ]] || deny ".env 파일 읽기·복사·출력 금지. 값이 필요하면 코드에서 os.environ 으로 읽고, 키 이름만 .env.example 에 적으라"
fi
hasi "[.]aws/credentials|[.]ssh/id_|[.]netrc|[.]git-credentials|[.]docker/config[.]json" && deny "자격 증명 파일 접근 금지"
hasi "${W}(printenv|env)([[:space:]]|$)|get-childitem[[:space:]]+env:|${W}(gci|ls|dir)[[:space:]]+env:" && deny "환경변수 전체 출력 금지"
hasi "(echo|write-host|write-output|print|printf|cat|type)[^;|&]*[$][{]?(env:)?[A-Za-z_]*(key|secret|token|password|passwd|credential)" && deny "비밀 환경변수 출력 금지"

# ---------- F. 원격 코드 실행 ----------
hasi "(curl|wget|iwr|invoke-webrequest|invoke-restmethod)[^;&]*[|][[:space:]]*(ba|z|k|da)?sh([[:space:]]|$)|(curl|wget)[^;&]*[|][[:space:]]*(python|node|perl|pwsh|powershell)" && deny "다운로드한 스크립트를 바로 실행하는 것 금지. 파일로 저장해 내용을 확인한 뒤 실행"
hasi "(iex|invoke-expression)[^;]*(downloadstring|iwr|invoke-webrequest|net[.]webclient)" && deny "원격 스크립트 iex 실행 금지"

# ---------- G. 권한·시스템 ----------
has "${W}sudo[[:space:]]|${W}su[[:space:]]+-" && deny "sudo/su 금지"
has "${W}chmod[[:space:]]+(-R[[:space:]]+)?[0-7]?777|${W}chown[[:space:]]+-R" && deny "chmod 777 / chown -R 금지"
hasi "${W}(mkfs|fdisk|diskpart|format[[:space:]]+[a-z]:)|${W}dd[[:space:]]+if=|>[[:space:]]*/dev/(sd|nvme|disk)|:[(][)][[:space:]]*[{]|${W}(shutdown|reboot|halt|poweroff|stop-computer|restart-computer)([[:space:]]|$)|${W}reg[[:space:]]+delete|remove-itemproperty[^;]*hklm" && deny "디스크·시스템·레지스트리 파괴 명령 금지"

# ---------- H. 인프라·데이터 파괴 ----------
hasi "${W}terraform[[:space:]]+(destroy|apply[^;|&]*-auto-approve)|${W}tofu[[:space:]]+destroy" && deny "terraform destroy / apply -auto-approve 금지. plan 까지만 실행하고 apply 는 사용자가 한다"
hasi "${W}aws[[:space:]]+([^;|&]*[[:space:]])?(delete-|terminate-|deregister-|remove-|s3[[:space:]]+(rm|rb)([[:space:]]|$)|sync[^;|&]*--delete)" && deny "AWS 삭제·종료 명령 금지. 사용자가 콘솔에서 한다"
hasi "${W}gh[[:space:]]+(repo[[:space:]]+delete|api[^;|&]*-X[[:space:]]+DELETE|secret[[:space:]]+delete)" && deny "GitHub 삭제 계열 명령 금지"
hasi "${W}docker[[:space:]]+(system|volume|image|container|network|builder)[[:space:]]+prune|${W}docker[[:space:]]+volume[[:space:]]+rm|${W}docker[[:space:]]+rm[[:space:]]+-[a-zA-Z]*f|docker([[:space:]]+|-)compose[^;|&]*down[^;|&]*(-v([[:space:]]|$)|--volumes)" && deny "docker prune / volume rm / down -v 는 데이터를 지운다. 금지"
hasi "drop[[:space:]]+(database|schema|table|extension)|truncate[[:space:]]+table" && deny "DROP/TRUNCATE 를 셸에서 직접 실행 금지. Alembic 마이그레이션 파일로 작성해 검토받으라"

# ---------- I. 외부 전송 ----------
if hasi "${W}curl([[:space:]]+[^;|&]*)?[[:space:]]+(-[a-zA-Z]*(d|F|T)([[:space:]]|$)|--data|--form|--upload-file)"; then
  hasi "localhost|127[.]0[.]0[.]1|0[.]0[.]0[.]0|host[.]docker[.]internal" || deny "로컬 서버 이외로의 데이터 전송(curl -d/-F/-T) 금지"
fi
hasi "${W}(scp|sftp|rclone|ftp)[[:space:]]" && deny "파일 외부 전송(scp/sftp/rclone) 금지"

exit 0
