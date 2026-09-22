# P4-pilot-eval · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-22 15:53 | 출처: verify-impl | 열림: 2 (필수 0) | 해소: 3

## F-0e133a · [필수] 없음: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
상태: 해소 | 발견: 2026-09-15 (verify-plan) | 해소: 2026-09-17 (verifier, `evidence/20260917-0930-verify-plan.txt` FAIL 0)

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
```

### 원인 분석
- 가설: 절차상 순서 — 2026-09-15 16:17 의 verify-plan 은 verifier 위임 **전** 메인 세션의 초안 실행이라 02-plan-verify.md 가 아직 없었다(이전 위임은 읽기 단계에서 중단, 2026-09-17 재위임). 코드·계획 결함 아님.
- 확인 방법(명령): `ls docs/wiki/packages/P4-pilot-eval/` ; `bash .claude/scripts/verify-plan.sh P4-pilot-eval | grep 02-plan-verify`
- 확인 결과: 2026-09-17 09:25 재실행(`evidence/20260917-0922-verify-plan.txt`)에서도 `FAIL  없음: … 02-plan-verify.md` 재현(1a). 문서 작성 후 09:30 재실행(`evidence/20260917-0930-verify-plan.txt`) `PASS  존재: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md` + `PASS  검증자 = verifier (L-002)`·`점검표 8행 존재`·`점검표 모든 행에 근거 있음`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P4-pilot-eval/02-plan-verify.md` 신규 — `templates/plan-verify.md` 형식, `검증자: verifier (fable)`, §1 기계 검증 출력 1a·1b 전문, §2 점검표 8행(카드 인용), §3 H-1·R-1~R-6·O-1~O-3, §3b 인계 대조표(X 0), §3c 결정 A~K, §3d 소견 3건, §4 `결과: 보류` | `bash .claude/scripts/verify-plan.sh P4-pilot-eval \| tail -1` | `== 결과: FAIL=0 WARN=3 ==` | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt` — `== 결과: FAIL=0 WARN=3 ==`

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-95c6a7 · [권고] registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
상태: 해소 | 발견: 2026-09-15 (verify-plan) | 해소: 2026-09-22 (verifier 04-review, `evidence/20260922-1535-review-negative.txt` N19 `| reports/metrics.json |` 행 1)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
```

### 원인 분석
- 가설: 스크립트 5번(registry 중복)이 산출물 경로의 **basename** `metrics.json` 을 registry 전문에서 찾는데, `reports/metrics.json` 행이 아니라 P3-baselines `evaluation/resolvers/registry.py` 행(112행)의 **비고 문구**("예약 이름 5개 … = `metrics.json` 키")에 걸린 오탐. 01-plan 산출물 목록에 `reports/metrics.json` 이 두 번(47행 + 79행 판정 문구) 나와 WARN 도 두 번.
- 확인 방법(명령): `grep -n "metrics.json" docs/wiki/registry.md` ; `grep -n "| reports/metrics.json" docs/wiki/registry.md`
- 확인 결과: `evidence/20260917-0922-plan-refs.txt` — 첫 명령 112행 1건(모듈 행 비고), 둘째 명령 0건. `reports/metrics.json` 은 어느 패키지에도 등록돼 있지 않다 → 신규 산출물이 맞고 중복 구현 아님.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 변경 없음(오탐). 계획·registry 를 고치지 않는다. U9 가 `reports/metrics.json` 을 registry **신규 행**으로 올리면 그때 스크립트 5번의 "다른 패키지" 조건이 자연히 사라진다 | `grep -c "| reports/metrics.json" docs/wiki/registry.md` (U9 이후) | `1`(P4-pilot-eval 행) | 완료 — U9 f01ea35 registry 142행(`reports/metrics.json`, ef18143). verifier 재실행 출력 `registry '| reports/metrics.json |' 행 수: 1`(`evidence/20260922-1535-review-negative.txt` N19); verify-impl 1533 에 이 WARN 없음 |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt` — WARN 잔존(같은 2줄), FAIL 0. 02-plan-verify §1a 에 오탐 사유 기재. 계획 단계에서는 닫지 않고 U9 registry 행 추가 뒤 `verify-impl.sh` 에서 닫는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오 (하네스 관찰: basename 일치는 P3-baselines·P3-llm-providers 에서도 같은 종류의 WARN — L-nnn 후보이나 이 패키지 조치 아님)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 해소 | 발견: 2026-09-15 (verify-plan) | 해소: 2026-09-22 (종료 커밋 — registry 33행 비고에 P4-pilot-eval U9 한 줄; 판정 `sed -n 33p docs/wiki/registry.md | grep -c P4-pilot-eval` → 1, 행 수 1 유지)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: `README.md` 는 registry 33행(하네스, pending)에 이미 있는 **기존 파일**이고, 01-plan 은 새 파일이 아니라 절 하나("파일럿 평가 실행법")를 **이어 붙이는 의도된 확장**이다(01-plan 59행 "registry — 신규 행(기존 행은 비고만)", 120행 "새 절을 만들지 않고 … 이어 붙인다(F-0ffff5 선례 — registry 비고에 한 줄)"). 스크립트 5번은 "기존 파일 확장" 을 표현할 수 없어 WARN 을 낸다(P3-baselines F-0ffff5·P3-llm-providers §6 8 (a) 와 같은 종류).
- 확인 방법(명령): `grep -n "| README.md" docs/wiki/registry.md` ; `grep -n "README" docs/wiki/packages/P4-pilot-eval/01-plan.md`
- 확인 결과: registry 33행 1건(패키지 열 "하네스", 비고에 P0-compose·P1·P3-er·P3-baselines·P3-llm-providers 확장 이력). 01-plan 28·59·71·120행 전부 "절 추가·비고 한 줄" 문언 — 새 README 를 만들지 않는다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 변경 없음(의도된 확장). U9 에서 `README.md` 에 "파일럿 평가 실행법" 절을 붙이고 registry 33행 **비고**에 `P4-pilot-eval U9: "파일럿 평가 실행법" 절 추가` 한 줄 | `grep -c "P4-pilot-eval" <(sed -n 33p docs/wiki/registry.md)` (U9 이후) | `1` | **미완(verifier 04-review 2026-09-22)** — README 330행 `### 파일럿 평가 실행법 (P4)` 절은 f01ea35 에 있으나 registry 33행 비고의 P4 언급은 `0`(`evidence/20260922-1535-review-negative.txt` N19·N29 `registry 33행 README 비고 P4 언급: 0`). 종료 커밋에서 메인 세션이 비고 한 줄 추가 후 같은 명령으로 닫는다 |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt` — WARN 잔존(같은 1줄), FAIL 0. 02-plan-verify §1a 에 의도 사유 기재. 04-review 가 registry 33행 비고를 확인해 닫는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-14f3ef · [권고] 04-review.md 없음 (완료 검토 전이면 정상)
상태: 해소 | 발견: 2026-09-22 (verify-impl) | 해소: 2026-09-22

### 증상 (검증 출력 인용)
```
WARN  04-review.md 없음 (완료 검토 전이면 정상)
```

### 원인 분석
- 가설: 절차상 순서 — verifier 가 `/devlog done` 1단계로 `verify-impl.sh` 를 04-review **작성 전**에 실행했다(스크립트 5번은 04-review 가 있을 때만 증거 열을 검사하고, 없으면 이 WARN 을 낸다). 코드·산출물 결함 아님.
- 확인 방법(명령): `ls docs/wiki/packages/P4-pilot-eval/04-review.md` ; `bash .claude/scripts/verify-impl.sh P4-pilot-eval | grep -E '04-review|증거'`
- 확인 결과: 1차(`evidence/20260922-1533-review-verify-impl.txt`) 시점에 파일 없음 → WARN 재현. verifier 가 04-review 를 쓴 뒤 같은 명령을 재실행한 결과는 아래 재검증 줄(2차 evidence).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P4-pilot-eval/04-review.md` 신규(verifier, `templates/package-review.md` 형식, `검토자: verifier (fable)`, §2 증거 열은 evidence 파일·해시·경로만) | `bash .claude/scripts/verify-impl.sh P4-pilot-eval \| grep -cE '^PASS  (검토자 = verifier\|증거 확인)'` | `1 + 수용 기준 표 행 수`(FAIL 0) | 완료 — 2차 재검증 참조 |

### 재검증
- 명령: `POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-impl.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/<ts>-review-verify-impl-2.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260922-1549-review-verify-impl-2.txt` — `PASS  검토자 = verifier (L-002)`, `PASS  증거 확인` 24행, `== 결과: FAIL=0 WARN=1 ==`(잔여 WARN 은 F-2f0840). `findings.py` 재실행으로 자동 해소

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-2f0840 · [권고] 미완료 작업 단위 9 개
상태: 해소 | 발견: 2026-09-22 (verify-impl) | 해소: 2026-09-22 (종료 커밋 — 01-plan U1~U9 `- [x]` 9개; 판정 `grep -cE "^- \[ \] U[0-9]" 01-plan.md` → 0)

### 증상 (검증 출력 인용)
```
WARN  미완료 작업 단위 9 개
```

### 원인 분석
- 가설: `verify-impl.sh` 7번이 `01-plan.md` 의 `^- \[ \] U[0-9]+` 줄 수를 센다. 01-plan 64~73행 U1~U9 가 전부 `- [ ]` 그대로다 — 작업 단위는 03-log 11항목·커밋 fb81234…f01ea35 로 모두 끝났지만 계획 문서의 체크박스를 아무도 `- [x]` 로 바꾸지 않았다(문서 표기 누락, 코드·결과 결함 아님). 계획 문서는 verifier 가 고치지 않는다.
- 확인 방법(명령): `grep -cE '^- \[ \] U[0-9]' docs/wiki/packages/P4-pilot-eval/01-plan.md` ; `grep -cE '^- \[x\] U[0-9]' docs/wiki/packages/P4-pilot-eval/01-plan.md`
- 확인 결과: `9` / `0`(`evidence/20260922-1535-review-negative.txt` N29 `01-plan 미체크 단위: 9 / 체크: 0`). 단위별 완료 근거는 04-review §2·§5(registry 21행 커밋 해시 MATCH 21/21).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 종료 커밋에서 메인 세션이 `01-plan.md` 64~73행 U1~U9 의 `- [ ]` 를 `- [x]` 로(본문 불변, 사용자 승인 커밋) | `grep -cE '^- \[ \] U[0-9]' docs/wiki/packages/P4-pilot-eval/01-plan.md` | `0` | 대기(메인 세션) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/<ts>-verify-impl.txt`
- 결과 파일(evidence/): (종료 커밋 후)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

