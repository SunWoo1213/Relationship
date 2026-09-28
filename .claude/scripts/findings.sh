#!/usr/bin/env bash
# findings.sh — findings.py 를 OS 에 상관없이 같은 명령으로 돌리는 래퍼 (FIX-011)
#
#   bash .claude/scripts/findings.sh <패키지id> <검증출력파일> --source verify-impl
#
# 왜 래퍼가 필요한가:
#   파이썬 인터프리터 이름이 기기마다 다르다. Windows 는 python, 최근 macOS 는 python3 뿐이고
#   가상환경 경로도 .venv/bin/python 과 .venv/Scripts/python.exe 로 갈린다.
#   문서에 "python ..." 이라고 적어 두면 한쪽 기기에서는 실행되지 않아, FAIL/WARN 을 소견으로
#   옮기는 단계가 아예 시작되지 않는다. 그래서 명령을 하나로 고정한다.
#
# 종료 코드는 findings.py 의 것을 그대로 돌려준다(열린 소견이 있으면 1).
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
. "$ROOT/.claude/hooks/_py.sh"

# findings.py 는 표준 라이브러리만 쓴다. 그래도 venv 를 먼저 보는 쪽이 일관적이다.
PY="$(hook_python_with json "$ROOT" || true)"
PY="${PY:-$HOOK_PY}"
if [ -z "$PY" ]; then
  echo "FAIL  $HOOK_PY_MISSING_MSG" >&2
  exit 2
fi

exec "$PY" "$ROOT/.claude/scripts/findings.py" "$@"
