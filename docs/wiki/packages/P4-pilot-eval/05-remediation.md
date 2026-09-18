# P4-pilot-eval · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-17 09:30 (verifier) | 출처: verify-plan | 열림: 2 (필수 0 · 권고 2, 둘 다 오탐/의도 — 조치 없음) | 해소: 1

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
상태: 열림 | 발견: 2026-09-15 (verify-plan) | 해소: -

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
| 1 | 변경 없음(오탐). 계획·registry 를 고치지 않는다. U9 가 `reports/metrics.json` 을 registry **신규 행**으로 올리면 그때 스크립트 5번의 "다른 패키지" 조건이 자연히 사라진다 | `grep -c "| reports/metrics.json" docs/wiki/registry.md` (U9 이후) | `1`(P4-pilot-eval 행) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt` — WARN 잔존(같은 2줄), FAIL 0. 02-plan-verify §1a 에 오탐 사유 기재. 계획 단계에서는 닫지 않고 U9 registry 행 추가 뒤 `verify-impl.sh` 에서 닫는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오 (하네스 관찰: basename 일치는 P3-baselines·P3-llm-providers 에서도 같은 종류의 WARN — L-nnn 후보이나 이 패키지 조치 아님)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-15 (verify-plan) | 해소: -

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
| 1 | 변경 없음(의도된 확장). U9 에서 `README.md` 에 "파일럿 평가 실행법" 절을 붙이고 registry 33행 **비고**에 `P4-pilot-eval U9: "파일럿 평가 실행법" 절 추가` 한 줄 | `grep -c "P4-pilot-eval" <(sed -n 33p docs/wiki/registry.md)` (U9 이후) | `1` | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
- 결과 파일(evidence/): `docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt` — WARN 잔존(같은 1줄), FAIL 0. 02-plan-verify §1a 에 의도 사유 기재. 04-review 가 registry 33행 비고를 확인해 닫는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

