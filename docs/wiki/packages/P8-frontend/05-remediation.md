# P8-frontend · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-10-10 23:40 (verifier 재검증) | 출처: review | 열림: 0 (필수 0) | 해소: 1

## F-ce7d18 · [필수] 01-plan 이 FIX 게이트 규칙 6 경로 확대 대상으로 commit-guard.sh 만 지목 — 실제 판정은 .claude/scripts/fix_guard_check.py 180행 (R-1)
상태: 해소 | 발견: 2026-10-10 (review) | 해소: 2026-10-10 23:40 (verifier (fable) 재검증 — `evidence/20261010-2335-verify-plan-verifier-re.txt`)

### 증상 (검증 출력 인용)
```
FAIL  01-plan 이 FIX 게이트 규칙 6 경로 확대 대상으로 commit-guard.sh 만 지목 — 실제 판정은 .claude/scripts/fix_guard_check.py 180행 (R-1)
```

### 원인 분석
(verifier (fable) 2026-10-10 — 원인 분석 칸까지만 채운다. 해결 단계·재검증은 계획 수정 주체(architect/메인 세션) 몫.)
- 가설: FIX-027 이 규칙 6 을 넣을 때 셸 훅 `commit-guard.sh` 는 호출부(106행)만 두고 경로 판정을 `.claude/scripts/fix_guard_check.py` 로 뺐다(`_py.sh` 로 Mac·Windows 동일 실행). architect 는 Bash 없이 `commit-guard.sh` 를 grep 만 했고(01-plan 409행 "grep 만 … FIX 게이트 범위") 11·100행 **주석** 의 `app/·alembic/` 을 판정 코드로 읽어, 산출물 표(77행)·U0 ④(88행)·판정 grep(91행)이 전부 셸 파일만 가리키게 됐다. 이대로 U0 를 하면 (a) 주석만 고쳐도 판정 grep 이 통과하고, (b) 실제 게이트(`touches_product_code`)는 `web/` 을 계속 모른다. ⑤ test-guards 새 케이스가 제대로 쓰였을 때만 (다) 단계에서 드러난다.
- 확인 방법(명령): `grep -n -E "app/|alembic/|web/" .claude/scripts/fix_guard_check.py` · `grep -n -E "app/|alembic/|web/|fix_guard_check" .claude/hooks/commit-guard.sh` · `sed -n '77p;88p;91p' docs/wiki/packages/P8-frontend/01-plan.md`
- 확인 결과(`evidence/20261010-2314-verify-plan-verifier.txt`): `fix_guard_check.py` 22행 docstring · **180행 `touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") for p in staged)`** · 203행 거부 메시지 "제품 코드(app/·alembic/)". `commit-guard.sh` 11행·100행은 `#` 주석, 106행 `fix_guard_out="$("$HOOK_PY" "$(dirname "$0")/../scripts/fix_guard_check.py" "$ROOT" "$DRAFT" 2>&1)"`. 01-plan 77행 표 파일 열 `.claude/hooks/commit-guard.sh`(fix_guard_check.py 없음), 88행 "④ `commit-guard.sh` 규칙 6 — … `app/`·`alembic/`·`web/` 로 확대", 91행 "`grep -n "web/" .claude/hooks/commit-guard.sh .claude/hooks/stage-gate.sh`". → 계획이 고칠 파일과 판정 대상을 잘못 지목했다. 필요한 수정은 01-plan 세 곳에 `.claude/scripts/fix_guard_check.py`(180·203행, 22행 docstring)를 추가하는 것이며, 코드·훅은 이 소견에서 고치지 않는다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P8-frontend/01-plan.md` 77·88·91행 수정(architect, Edit, 2026-10-10 — 사용자 승인 "R-1 + 권고 전부"): 77행 "고치는 기존 파일" 표에 `.claude/scripts/fix_guard_check.py`(180행 경로 조건 · 203행 메시지 · 22행 docstring) 추가, `commit-guard.sh` 는 11·100행 주석 정합만으로 한정 · 88행 ④ 의 실제 판정 파일을 `fix_guard_check.py` 180행 `touches_product_code` 에 `or p.startswith("web/")` 추가로 명시 · 91행 판정을 `grep -n 'startswith("web/")' .claude/scripts/fix_guard_check.py`(주석만으로는 통과 불가) + test-guards "`web/` FIX 커밋 거부/허용" 실제 시험으로 교체(`commit-guard.sh` grep 은 주석 정합 확인으로만 남김). 같은 취지로 24행(범위)·233행(결정 B)·372행(리스크 2)도 맞춤 | `grep -n "fix_guard_check.py" docs/wiki/packages/P8-frontend/01-plan.md` · `grep -n 'startswith("web/")' docs/wiki/packages/P8-frontend/01-plan.md` | 첫 명령 출력에 77·88·91행이 모두 있음(24·233·372·414행도 나옴) · 둘째 명령 출력에 88·91행 | 완료 — verifier 확인(아래 재검증) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P8-frontend`(계획 단계) + 해결 단계 1행의 완료 판정 명령 2개 + 실제 게이트 시험(아래)
- 결과 파일(evidence/): `20261010-2335-verify-plan-verifier-re.txt` — verifier (fable) 직접 실행, 2026-10-10 23:35
- 결과(verifier 판정, 2026-10-10):
  - `verify-plan.sh`: FAIL 0 / WARN 0.
  - 완료 판정 명령 1 `grep -n "fix_guard_check.py" …/01-plan.md` → 24·77·88·90·91·233·372·414행(기대 "77·88·91 + 24·233·372·414" 를 전부 포함). 명령 2 `grep -n 'startswith("web/")' …/01-plan.md` → 77·88·91행(기대 88·91 포함).
  - 코드 위치 재확인: `grep -n -E 'app/|alembic/|web/' .claude/scripts/fix_guard_check.py` → 22(docstring)·45(주석)·**180(`touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") …)`)**·203(메시지). `commit-guard.sh` 11·71·100행은 `#` 주석, 106행이 파이썬 호출. 01-plan 77·88·91행이 이 네 곳(22·180·203 + commit-guard 주석 정합)을 정확히 가리킨다. `.claude/hooks/approve-commit.sh` 경로도 실재(`ls` 확인).
  - "주석만 고쳐도 통과" 차단 여부를 scratchpad 격리 저장소에서 실제 시험(제품 파일 무변경): 현재 코드 + `web/x.ts` 스테이징 → exit 0(게이트가 `web/` 를 모름) / `app/a.py` → exit 1(거부, 판정은 180행) / 203행 메시지만 바꾼 복사본 + `web/x.ts` → exit 0(주석·메시지만으로는 안 열림) / 180행에 `or p.startswith("web/")` 넣은 복사본 → exit 1(계획 88행 ④ 가 실제로 게이트를 연다). → 계획이 고칠 파일과 판정 대상이 실제 코드와 일치한다.
  - 단, 91행의 `grep -n 'startswith("web/")'` 판정 **단독**은 주석 한 줄(`# … p.startswith("web/")`)로도 1건이 나온다(시험 5: grep 1건·exit 0). 91행이 같은 판정에 test-guards ⑤ "`web/` FIX 커밋 거부/허용" 실제 시험을 함께 요구하므로 소견은 해소하되, 04-review 가 둘을 **묶음으로** 요구해야 한다 — 02-plan-verify §5 새 소견 N-1(권고).

### 확인 결과
- verifier (fable), 2026-10-10 23:40: **해소.** 근거는 위 재검증 절과 `evidence/20261010-2335-verify-plan-verifier-re.txt`. 계획 수정만으로 닫히는 소견이며 코드·훅은 U0 에서 바뀐다(그 diff 는 커밋 전 verifier 리뷰, 01-plan 90행 (라)).

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

