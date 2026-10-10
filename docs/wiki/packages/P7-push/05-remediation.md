# P7-push · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-10-10 20:10 | 출처: verify-impl | 열림: 2 (필수 0) | 해소: 0
(verifier 추가 2026-10-10 20:20 — 출처 review 소견 1건 `F-c7c1e5` 를 아래에 손으로 더했다. 열림 3 (필수 0). verifier 는 원인 분석 칸까지만 채웠고 해결·재검증은 메인 세션·구현 에이전트 몫이다.)

## F-8aebe7 · [권고] ruff 경고/오류 → evidence/20261010-2010-lint.txt
상태: 이관 | 발견: 2026-10-10 (verify-impl) | 해소: - (P7 무관 — `.claude/scripts/findings.py` 기존 3건, CI 범위 `ruff check app tests scripts evaluation` 은 통과. 하네스 FIX 후보로 넘김. 승인 뒤 재실행 `evidence/20261010-2136-summary.txt` FAIL 0 / WARN 1 = 이 항목)

### 증상 (검증 출력 인용)
```
WARN  ruff 경고/오류 → evidence/20261010-2010-lint.txt
```

### 원인 분석
- 가설: `verify-impl.sh` 는 인자 없는 `ruff check .`(저장소 전체)를 돌리는데, CI 범위 밖인 하네스 스크립트 `.claude/scripts/findings.py` 에 기존 ruff 위반 3건(DTZ005 ×2 — `datetime.now()` tz 없음 129·130행, F541 — 자리표시자 없는 f-string 163행)이 있다. 이 패키지(P7-push)가 만든 파일은 0건이다.
- 확인 방법(명령): `cat docs/wiki/packages/P7-push/evidence/20261010-2010-lint.txt` / `.venv/bin/ruff check app tests scripts evaluation`(CI 워크플로와 같은 범위)
- 확인 결과: lint 파일 = `.claude/scripts/findings.py:129:13 DTZ005`, `:130:11 DTZ005`, `:163:38 F541`, "Found 3 errors." 뿐. CI 범위 재실행 = "All checks passed!"(`evidence/20261010-2005-review-negative-cases.txt` B-[10]). U7 evidence(`20261008-1536-u7-regression.txt` 18행)도 같은 3건을 "CI 범위 밖의 기존 하네스 스크립트" 로 적어 두었다. → P7-push 산출물과 무관한 기존 상태. 해결은 하네스 정리 커밋(또는 verify-impl 의 ruff 범위를 CI 와 맞추는 것) 중 하나 — 사용자 결정.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P7-push` (계획 단계면 `verify-plan.sh P7-push`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-c7c1e5 · [권고] `import app.push` 단독 import 가 순환 import 로 실패한다 (01-plan U1 판정 명령 회귀, FIX 후보)
상태: 해소 | 발견: 2026-10-10 (review — verifier 변이 실험 중 발견) | 해소: 2026-10-10 FIX-029 `e555142`(scheduler 지연 import + `tests/test_import_order.py`, verifier `review-FIX-029.md` 통과, CI run 38049456285 세 job success)

### 증상 (검증 출력 인용)
```
$ .venv/bin/python -c "import app.push"
ImportError: cannot import name 'notifier_from_env' from partially initialized module 'app.push.notifier' (most likely due to a circular import)
(app.push.notifier / sender / payload / subscriptions / types 단독 import 모두 같은 오류. app.briefing·app.main 을 먼저 import 하면 성립.)
```

### 원인 분석
- 가설: U5 `55fc0f3` 가 `app/briefing/scheduler.py` 모듈 상단에 `from app.push.notifier import notifier_from_env` 를 넣었고, `app/briefing/__init__.py` 27행이 scheduler 를 재export 하므로 `app.push.notifier` → `app.briefing.types` → `app/briefing/__init__` → `scheduler` → (부분 초기화된) `app.push.notifier` 순환이 생겼다. U4 `8e9af9e` 시점 scheduler 에는 `app.push` import 가 없었다. 제품 진입점(uvicorn `app.main`)·테스트(conftest 가 `app.main` 을 먼저 올림)·U8 실서버는 `app.briefing` 이 먼저 올라가는 순서라 드러나지 않았다.
- 확인 방법(명령): `.venv/bin/python -c "import app.push"` / `.venv/bin/python -c "import app.briefing, app.push; print('ok')"` / `git show 8e9af9e:app/briefing/scheduler.py | grep -n app.push` / `git show 55fc0f3 -- app/briefing/scheduler.py | grep "^+.*import"`
- 확인 결과: `evidence/20261010-2005-review-import-cycle.txt` — 단독 import 6개 모듈 전부 ImportError, `app.briefing` 선행 시 ok, U4 시점 grep 없음, U5 추가 줄 `+from app.push.notifier import notifier_from_env`. 수용 기준 1~26행·전체 회귀 1873 passed 에는 영향 없음. 해결 방향(구현 에이전트가 정한다): ① `scheduler.py` 의 그 import 를 `default_run_once()` 본문으로 내린다(`composer_from_env` 와 같은 "호출 시점" 규약, 한 줄 이동) 또는 ② `app/briefing/__init__.py` 의 scheduler 재export 를 지연시킨다. 완료 판정 명령은 `python -c "import app.push"` 성공 + `tests/test_push_wiring.py`·`tests/test_briefing_scheduler.py` 통과 + 전체 회귀. 제품 코드(`app/`) 변경이므로 FIX 문서·verifier 리뷰가 필요하다(FIX-027 규칙). 사용자가 [필수] 로 올리면 P7 완료 승인 전에 처리한다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | (구현 에이전트가 채운다 — 위 ① 또는 ②) | `.venv/bin/python -c "import app.push; print('ok')"` | `ok` | 대기 |
| 2 | 회귀 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_push_wiring.py tests/test_briefing_scheduler.py -q` 후 전체 `-rs` | 전부 passed, skip 0 | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P7-push` + 위 완료 판정 명령
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(S3.6·R12 의미 불변, 모듈 경계만) — 01-plan U1 판정 명령 `python -c "import app.push"` 가 HEAD 에서 깨진 상태라는 점만 기록
- FIX/CR 로 올려야 하는가: 예 — FIX 후보(번호는 메인 세션이 부여). CR 아님(기획·명세 불변).

## F-2f0840 · [권고] 미완료 작업 단위 4 개
상태: 해소 | 발견: 2026-10-10 (verify-impl) | 해소: 2026-10-10 완료 승인 뒤 메인 세션이 01-plan U1~U4 를 `[x]` 로(재검증은 아래 verify-impl 재실행)

### 증상 (검증 출력 인용)
```
WARN  미완료 작업 단위 4 개
```

### 원인 분석
- 가설: `01-plan.md` 의 U1~U4 줄이 `- [ ]` 로 남아 있다(U5~U8 만 `[x]`). U1~U4 는 각각 커밋 `85393e0`·`6c98516`·`f256259`·`8e9af9e` 와 03-log 항목·evidence 가 있으므로 작업이 안 끝난 것이 아니라 체크박스 갱신이 빠진 문서 누락이다(U5 커밋 `55fc0f3` 부터 체크박스를 같은 커밋에서 바꾸기 시작했다).
- 확인 방법(명령): `grep -nE '^- \[( |x)\] U[0-9]' docs/wiki/packages/P7-push/01-plan.md` / `git log --oneline --grep "U1\|U2\|U3\|U4" --grep P7-push --all-match`
- 확인 결과: 74~77행 `[ ] U1`·`[ ] U2`·`[ ] U3`·`[ ] U4`, 78~81행 `[x] U5`~`[x] U8`. 커밋 4개와 03-log 13~51행 항목 존재. → 완료 승인 뒤 메인 세션이 네 줄을 `[x]` 로 바꾸면 같은 명령 재실행에서 WARN 이 사라진다(P6-memory 04-review 때와 같은 처리, 제품 코드 변경 아님).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P7-push` (계획 단계면 `verify-plan.sh P7-push`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

