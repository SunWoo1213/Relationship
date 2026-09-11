# P3-baselines · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-11 13:05 | 출처: verify-impl | 열림: 0 (필수 0) | 해소: 3

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
상태: 해소 | 발견: 2026-09-10 (verify-plan) | 해소: 2026-09-11

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
| 1 | 조치 없음(계획 단계) — U8 에서 `README.md` 에 "베이스라인 실행법" 절을 추가하되 `registry.md` 는 32행 **비고만** 덧붙이고 새 행을 만들지 않는다(01-plan 95행). 04-review §5 에서 verifier 가 행 수를 확인해 닫는다 | `grep -c "\| README.md \|" docs/wiki/registry.md` | `1` (행 수 불변) — 그리고 32행 비고에 `P3-baselines U8:` 문구 존재 | 완료(2026-09-11 닫는 커밋, evidence `20260911-1305-close-f0ffff5.txt`: `grep -c` = 1, 비고 문구 1줄) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-baselines` (U8 후, 04-review 단계)
- 결과 파일(evidence/): U8 후 verify-impl 출력(04-review 에서 기록). 계획 단계 재검증 `20260910-1036-verify-plan-final.txt` 50행에서 WARN 유지 — 예상된 상태.
- 닫음(2026-09-11): 04-review §5 verifier 가 행 수 1 확인, 닫는 커밋에서 32행 비고에 `P3-baselines U8:` 문구 추가 → 해결 단계 1 판정 명령 출력 `20260911-1305-close-f0ffff5.txt`. 판정: 해소.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-445cda · [필수] 04-review 수용 기준 표에 행이 없다
상태: 해소 | 발견: 2026-09-11 (verify-impl) | 해소: 2026-09-11

### 증상 (검증 출력 인용)
```
FAIL  04-review 수용 기준 표에 행이 없다
```

### 원인 분석
- 가설: 검증 순서상 정상인 FAIL — verifier 가 `verify-impl.sh` 5번 항목(04-review `검토자:` 줄 검사)을 통과시키기 위해 **표가 비어 있는 04-review 초안**(검토자 줄만 있는 골격)을 먼저 두고 1a 실행을 돌렸다(P1 04-review §1a 와 같은 절차, F-14f3ef 선례). 코드·계획·카드의 결함이 아니라 04-review 본문이 아직 없던 시점의 출력이다.
- 확인 방법(명령): `sed -n '1,20p' docs/wiki/packages/P3-baselines/04-review.md`(1a 시점 → "(초안 — §1 기계 검증 1a 실행용 …)" 줄과 빈 표) · 본문 작성 후 `awk '/^## 2. 수용 기준 대조/{f=1;next} /^## /{f=0} f && /^\|/ && !/^\| *기준|^\|-/' docs/wiki/packages/P3-baselines/04-review.md | wc -l`(≥ 1)
- 확인 결과: 1a evidence `20260911-1235-review-verify-impl-draft.txt` 12행 `FAIL  04-review 수용 기준 표에 행이 없다`, 같은 파일 11행 `PASS  검토자 = verifier (L-002)`(검토자 줄은 초안에 이미 있었다). verifier 가 본문(§2 표 5행 + §2b·§3~§7)을 작성한 뒤 1b 재실행으로 해소 여부를 본다. (verifier 기록)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P3-baselines/04-review.md` 본문 작성(verifier — 이 소견의 대상 파일은 verifier 의 산출물이므로 구현자 조치 없음) — §2 표 5행의 증거 열을 evidence 파일·해시·경로로만 채운다 | `bash .claude/scripts/verify-impl.sh P3-baselines \| grep -E "수용 기준|증거 확인|^== 결과"` | `PASS  증거 확인: …` 5줄, `== 결과: FAIL=0 WARN=0 ==` | 완료(12:45, 1b 실행) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260911-1245-review-verify-impl-final.txt` → `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python .claude/scripts/findings.py P3-baselines docs/wiki/packages/P3-baselines/evidence/20260911-1245-review-verify-impl-final.txt --source verify-impl`
- 결과 파일(evidence/): `20260911-1245-review-verify-impl-final.txt`(04-review §1b 에 전문) — 재검증 결과는 04-review §1b 와 이 파일 머리 줄의 "열림/해소" 수로 본다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

