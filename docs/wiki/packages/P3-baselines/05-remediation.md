# P3-baselines · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-10 10:39 | 출처: verify-plan | 열림: 1 (필수 0) | 해소: 1

## F-cf1510 · [필수] 없음: docs/wiki/packages/P3-baselines/02-plan-verify.md
상태: 해소 | 발견: 2026-09-10 (verify-plan) | 해소: 2026-09-10

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P3-baselines/02-plan-verify.md
```

### 원인 분석
- 가설: 검증 순서상 정상인 FAIL — 메인 세션이 `/devlog start` 6단계에서 verifier 위임 **전에** 1차 기계 검증을 돌렸고, 02-plan-verify.md 는 verifier 만 쓰는 파일이므로(L-002, `verify-plan.sh` 6번 항목) 그 시점에 존재할 수 없다. 계획·카드·코드의 결함이 아니다.
- 확인 방법(명령): `ls docs/wiki/packages/P3-baselines/02-plan-verify.md` (1차 시점 → 없음) · `grep -n "검증자:" docs/wiki/packages/P3-baselines/02-plan-verify.md` (작성 후 → `verifier (fable)`)
- 확인 결과: 1차 evidence `20260910-1029-verify-plan.txt` 3행 `FAIL  없음: …/02-plan-verify.md`. verifier(fable, 새 컨텍스트)가 10:36 에 02-plan-verify.md 작성(점검표 8행·카드 인용·§3 권고 R-1~R-9·결과 통과). (verifier 기록)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P3-baselines/02-plan-verify.md` 신규 — `templates/plan-verify.md` 형식, `검증자: verifier (fable)`, §1 기계 검증 출력 2회(1a·1b), §2 점검표 8행 카드 인용, §3 소견·권고, §4 결과 | `bash .claude/scripts/verify-plan.sh P3-baselines \| grep -E "02-plan-verify\|검증자\|점검표\|근거\|^== 결과"` | `PASS 존재: …/02-plan-verify.md` · `PASS 검증자 = verifier (L-002)` · `PASS 점검표 8행 존재` · `PASS 점검표 모든 행에 근거 있음` · `== 결과: FAIL=0 WARN=1 ==` | 완료(10:39) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260910-1036-verify-plan-final.txt` → `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python .claude/scripts/findings.py P3-baselines docs/wiki/packages/P3-baselines/evidence/20260910-1036-verify-plan-final.txt --source verify-plan`
- 결과 파일(evidence/): `20260910-1036-verify-plan-final.txt` — 5행 `PASS  존재: docs/wiki/packages/P3-baselines/02-plan-verify.md`, 51행 `== 결과: FAIL=0 WARN=1 ==`. findings.py 출력 `05-remediation.md 갱신: 새 소견 0, 해소 1, 열림 1 (필수 0)` / `✓ F-cf1510  해소`.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-10 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: **의도된 WARN.** `README.md` 는 `registry.md` 32행에 하네스 소유 행(`| 문서 | 프로젝트 README(…) | README.md | 하네스 | pending | …`)으로 이미 있고, 그 행의 비고에 P0-compose·P1-schema·P2-tools U9·P3-er U9 가 절을 덧붙인 이력이 쌓여 있다. 01-plan 95~96행은 "`docs/wiki/registry.md` — 신규 행 추가(**기존 행은 비고만**)", "`README.md` — 베이스라인 실행법 절" 이므로 이 패키지도 README 행을 새로 만들지 않고 비고만 덧붙인다. `verify-plan.sh` 7번 항목은 산출물 목록의 경로가 다른 패키지 행에 있으면 "확장"과 "재작성"을 구분하지 않고 WARN 을 낸다. 같은 F-id 가 P3-er 에서 같은 판정으로 닫혔다(`packages/P3-er/05-remediation.md` 244~266행 "조치 없음 — … 기존 행 비고 갱신, 새 행 금지 … 판정: 닫힘 … 행 수 1 유지").
- 확인 방법(명령): `grep -n "| README.md |" docs/wiki/registry.md` · `grep -c "| README.md |" docs/wiki/registry.md` · `sed -n 95,96p docs/wiki/packages/P3-baselines/01-plan.md`
- 확인 결과: registry 32행 1개(패키지 열 `하네스`, 비고에 "P3-er U9: … '엔티티 해석(ER) 실행법' 절 추가" 까지 누적). 01-plan 95행 "기존 행은 비고만" 문장 존재. (verifier 기록 — 계획 승인을 막지 않는다. 02-plan-verify §3 참조)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U8 에서 `README.md` 에 "베이스라인 실행법" 절을 추가하되 `registry.md` 는 32행 **비고만** 덧붙이고 새 행을 만들지 않는다(01-plan 95행). 04-review §5 에서 verifier 가 행 수를 확인해 닫는다 | `grep -c "\| README.md \|" docs/wiki/registry.md` | `1` (행 수 불변) — 그리고 32행 비고에 `P3-baselines U8:` 문구 존재 | 대기(U8) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-baselines` (U8 후, 04-review 단계)
- 결과 파일(evidence/): U8 후 verify-impl 출력(04-review 에서 기록). 계획 단계 재검증 `20260910-1036-verify-plan-final.txt` 50행에서 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

