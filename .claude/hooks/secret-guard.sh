#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit|NotebookEdit) 훅 — 비밀 파일 쓰기·비밀 문자열 삽입 차단
#
#   1. 비밀 파일 경로(.env, *.pem, *.key, id_rsa, tfstate, tfvars …)는 에이전트가 쓰지 않는다 (.env.example 은 허용)
#   2. 어떤 파일이든 API 키·토큰·개인키 패턴이 들어가면 거부한다 → 환경변수로 옮기고 이름만 .env.example 에
#
# 근거: docs/wiki/security.md

set -u
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 LC_ALL=C.UTF-8
input="$(cat)"

fp="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); ti=d.get("tool_input",{})
    print(ti.get("file_path") or ti.get("notebook_path") or "")
except Exception:
    print("")' 2>/dev/null)"

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[secret-guard] %s (근거: docs/wiki/security.md)"}}\n' "$1"
  exit 0
}

# 1. 경로 검사 (basename 기준)
base="$(printf '%s' "$fp" | sed 's#[\\/]#/#g' | awk -F/ '{print $NF}')"
case "$base" in
  .env.example|.env.sample|.env.template) ;;
  .env|.env.*) deny "비밀 파일 $base 는 에이전트가 쓰지 않는다. 사용자가 직접 만든다. 키 이름만 .env.example 에 적으라" ;;
  *.pem|*.key|*.p12|*.pfx|*.jks|id_rsa|id_rsa.*|id_ed25519|id_ed25519.*|*.tfstate|*.tfstate.*|*.tfvars|credentials|.netrc|.git-credentials)
    deny "비밀·상태 파일($base) 쓰기 금지" ;;
esac

# 2. 내용 검사
content="$(printf '%s' "$input" | python -c 'import sys,json
try:
    d=json.load(sys.stdin); ti=d.get("tool_input",{})
    parts=[]
    for k in ("content","new_string","new_source"):
        v=ti.get(k)
        if isinstance(v,str): parts.append(v)
    for e in ti.get("edits",[]) or []:
        v=e.get("new_string") if isinstance(e,dict) else None
        if isinstance(v,str): parts.append(v)
    sys.stdout.write("\n".join(parts))
except Exception:
    pass' 2>/dev/null)"
[ -n "$content" ] || exit 0

# 알려진 키 형식 (자리표시자는 걸리지 않도록 길이 조건을 둔다)
PATTERNS=(
  'sk-(proj-|ant-)?[A-Za-z0-9_-]{24,}'          # OpenAI / Anthropic
  'AKIA[0-9A-Z]{16}'                             # AWS access key id
  'aws_secret_access_key[[:space:]]*[=:][[:space:]]*[A-Za-z0-9/+]{40}'
  'ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}'
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'xox[baprs]-[A-Za-z0-9-]{20,}'                 # Slack
  'AIza[0-9A-Za-z_-]{35}'                        # Google API
  'eyJ[A-Za-z0-9_-]{20,}[.][A-Za-z0-9_-]{20,}[.][A-Za-z0-9_-]{20,}'  # JWT
  'postgres(ql)?://[^:/[:space:]]+:[^@[:space:]]{8,}@'               # DB URL with password
)
for p in "${PATTERNS[@]}"; do
  if printf '%s' "$content" | grep -Eq -- "$p"; then
    deny "비밀로 보이는 문자열이 파일 내용에 있다. 코드·문서에 키를 넣지 말고 환경변수(os.environ)로 읽고 .env.example 에 이름만 적으라"
  fi
done

exit 0
