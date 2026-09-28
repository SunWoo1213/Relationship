#!/usr/bin/env bash
# 훅 공용 — 파이썬 인터프리터를 찾아 $HOOK_PY 에 넣는다 (FIX-008)
#
# 왜 필요한가:
#   훅은 stdin JSON 을 파이썬으로 파싱한다. 그런데 인터프리터의 이름이 OS 마다 다르다.
#     Windows : python 이 표준. python3 는 없거나 Microsoft Store 를 여는 스텁인 경우가 많다.
#     macOS   : python 이 아예 없다(Apple 이 macOS 12.3 에서 Python 2 를 제거). python3 만 있다.
#               python 이라는 이름은 가상환경(venv)을 활성화했을 때만 생기는데 훅은 venv 밖에서 돈다.
#   이름 하나에 의존하면 반대쪽 OS 에서 깨진다. 그래서 두 이름을 순서대로 본다.
#
# 순서가 python → python3 인 이유:
#   Windows 에서 python 이 먼저 성공하므로 Store 스텁인 python3 를 아예 건드리지 않는다.
#   macOS 에서는 python 이 없어 자연히 python3 로 내려간다.
#
# 존재 여부가 아니라 실제로 도는지로 판단한다:
#   command -v 만 보면 "있지만 실행하면 실패하는" Store 스텁을 거르지 못한다. 한 번 실행해 본다.
#
# 쓰는 법:
#   . "$(dirname "$0")/_py.sh"          # HOOK_PY 가 채워진다(못 찾으면 빈 문자열)
#   [ -n "$HOOK_PY" ] || <이 훅의 실패 처리>
#
# 실패 처리는 훅마다 다르다(FIX-008):
#   차단형 가드(safety·secret·stage-gate·commit·delegate) → deny. 조용히 여는 것이 결함이므로 닫는다.
#   종료 가드(handoff-check) · 보조(commit-cleanup·session-start·precompact) → 경고만 하고 통과.

HOOK_PY=""
for _hook_py_cand in python python3; do
  command -v "$_hook_py_cand" >/dev/null 2>&1 || continue
  "$_hook_py_cand" -c 'pass' >/dev/null 2>&1 || continue
  HOOK_PY="$_hook_py_cand"
  break
done
unset _hook_py_cand

# 인터프리터를 못 찾았다고 알리는 공용 문구 (차단 메시지·경고에 함께 쓴다)
HOOK_PY_MISSING_MSG="파이썬 인터프리터를 찾지 못했다(python·python3 모두 없거나 실행되지 않는다). 훅이 입력을 읽을 수 없어 검사를 할 수 없다. 파이썬을 설치하고 PATH 에 넣으라 - 근거: docs/wiki/security.md, FIX-008"
