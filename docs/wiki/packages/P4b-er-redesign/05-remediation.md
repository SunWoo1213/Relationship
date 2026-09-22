# P4b-er-redesign · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-22 17:19 | 출처: verify-plan | 열림: 22 (필수 0) | 해소: 0

## F-ed9327 · [권고] registry 에 다른 패키지로 이미 있음: app/er/confidence.py → | 모듈 | 확신도·두 임계치(4단계, 순수 함수) | app/er/confidence.
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/confidence.py → | 모듈 | 확신도·두 임계치(4단계, 순수 함수) | app/er/confidence.
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-99f745 · [권고] registry 에 다른 패키지로 이미 있음: app/er/rules.py → | 모듈 | 규칙 필터(2단계, 순수 함수) | app/er/rules.py | P3-er | 02e
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/rules.py → | 모듈 | 규칙 필터(2단계, 순수 함수) | app/er/rules.py | P3-er | 02e
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-ead503 · [권고] registry 에 다른 패키지로 이미 있음: app/er/pipeline.py → | 모듈 | ER 오케스트레이션(resolve/apply_resolution) | app/er/pipeline.
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/pipeline.py → | 모듈 | ER 오케스트레이션(resolve/apply_resolution) | app/er/pipeline.
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-c4dc23 · [권고] registry 에 다른 패키지로 이미 있음: app/er/types.py → | 모듈 | ER 공용 타입 | app/er/types.py | P3-er | cc5d24f | `ScoredCandida
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/types.py → | 모듈 | ER 공용 타입 | app/er/types.py | P3-er | cc5d24f | `ScoredCandida
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-fdb56f · [권고] registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-3e8c8f · [권고] registry 에 다른 패키지로 이미 있음: scripts/run_pilot_eval.py → | 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: scripts/run_pilot_eval.py → | 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-111cde · [권고] registry 에 다른 패키지로 이미 있음: evaluation/curve.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: evaluation/curve.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-c9f2fe · [권고] registry 에 다른 패키지로 이미 있음: evaluation/metrics.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: evaluation/metrics.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-63a805 · [권고] registry 에 다른 패키지로 이미 있음: evaluation/calibration.py → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: evaluation/calibration.py → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-a58eb4 · [권고] registry 에 다른 패키지로 이미 있음: evaluation/resolvers/proposed.py → | 모듈 | 제안 4단계 하이브리드 어댑터(`app.er.resolve` -> `Mention
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: evaluation/resolvers/proposed.py → | 모듈 | 제안 4단계 하이브리드 어댑터(`app.er.resolve` -> `Mention
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2e533b · [권고] registry 에 다른 패키지로 이미 있음: tests/test_er_confidence.py → | 테스트 | 확신도 가중합·경계값·임계치 스윕 | tests/test_er_c
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_er_confidence.py → | 테스트 | 확신도 가중합·경계값·임계치 스윕 | tests/test_er_c
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-107c92 · [권고] registry 에 다른 패키지로 이미 있음: test_er_rules.py → | 테스트 | 규칙 필터 배제·완화 재평가·s_rule 분모 | tests/test
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: test_er_rules.py → | 테스트 | 규칙 필터 배제·완화 재평가·s_rule 분모 | tests/test
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-8439c7 · [권고] registry 에 다른 패키지로 이미 있음: test_er_pipeline.py → | 테스트 | ER 파이프라인 회귀(승진·이모 배제·동명이인)·tr
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: test_er_pipeline.py → | 테스트 | ER 파이프라인 회귀(승진·이모 배제·동명이인)·tr
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-27a843 · [권고] registry 에 다른 패키지로 이미 있음: test_run_pilot_eval.py → | 테스트 | 실행 CLI 순수 층(지문·run_id·비용 추정·환경변수
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: test_run_pilot_eval.py → | 테스트 | 실행 CLI 순수 층(지문·run_id·비용 추정·환경변수
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-fcf0a9 · [권고] registry 에 다른 패키지로 이미 있음: .jsonl.gz → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: .jsonl.gz → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
```

### 원인 분석
- 가설: 스크립트 basename 오탐 — 01-plan 산출물 줄 `reports/pilot/raw-\<새 ts\>.jsonl.gz · traces-\<새 ts\>.jsonl` · `reports/metrics.json · calibration.json · curve.csv · eval.md` 를 verify-plan.sh 7번이 공백으로 쪼개 `.jsonl.gz`·`calibration.json`·`curve.csv`·`eval.md` 토큰으로 registry 를 grep 했다(P4 04-review 230행 "verify-plan.sh 5번 basename 오탐(F-95c6a7 계열) 관찰 유지"와 같은 계열). 실제 산출물은 새 stamp 파일·최상위 4파일 갱신이며 registry 에는 새 stamp 행 추가 + 기존 행 비고 확장으로 등재한다.
- 확인 방법(명령): `grep -n "^- reports/" docs/wiki/packages/P4b-er-redesign/01-plan.md` · `sed -n 88,93p .claude/scripts/verify-plan.sh`
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — 토큰이 파일 경로가 아니라 산출물 줄의 조각. 해소 = U7 registry 등재(새 stamp raw/traces 행, 최상위 4파일 비고 확장) + 04-review §5. 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-5d4642 · [권고] registry 에 다른 패키지로 이미 있음: reports/metrics.json → | 리포트 | 파일럿 지표(5방식 × 10임계치 · 게이트 판정) | rep
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: reports/metrics.json → | 리포트 | 파일럿 지표(5방식 × 10임계치 · 게이트 판정) | rep
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-a4bedc · [권고] registry 에 다른 패키지로 이미 있음: calibration.json → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: calibration.json → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
```

### 원인 분석
- 가설: 스크립트 basename 오탐 — 01-plan 산출물 줄 `reports/pilot/raw-\<새 ts\>.jsonl.gz · traces-\<새 ts\>.jsonl` · `reports/metrics.json · calibration.json · curve.csv · eval.md` 를 verify-plan.sh 7번이 공백으로 쪼개 `.jsonl.gz`·`calibration.json`·`curve.csv`·`eval.md` 토큰으로 registry 를 grep 했다(P4 04-review 230행 "verify-plan.sh 5번 basename 오탐(F-95c6a7 계열) 관찰 유지"와 같은 계열). 실제 산출물은 새 stamp 파일·최상위 4파일 갱신이며 registry 에는 새 stamp 행 추가 + 기존 행 비고 확장으로 등재한다.
- 확인 방법(명령): `grep -n "^- reports/" docs/wiki/packages/P4b-er-redesign/01-plan.md` · `sed -n 88,93p .claude/scripts/verify-plan.sh`
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — 토큰이 파일 경로가 아니라 산출물 줄의 조각. 해소 = U7 registry 등재(새 stamp raw/traces 행, 최상위 4파일 비고 확장) + 04-review §5. 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-09ad74 · [권고] registry 에 다른 패키지로 이미 있음: curve.csv → | 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: curve.csv → | 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
```

### 원인 분석
- 가설: 스크립트 basename 오탐 — 01-plan 산출물 줄 `reports/pilot/raw-\<새 ts\>.jsonl.gz · traces-\<새 ts\>.jsonl` · `reports/metrics.json · calibration.json · curve.csv · eval.md` 를 verify-plan.sh 7번이 공백으로 쪼개 `.jsonl.gz`·`calibration.json`·`curve.csv`·`eval.md` 토큰으로 registry 를 grep 했다(P4 04-review 230행 "verify-plan.sh 5번 basename 오탐(F-95c6a7 계열) 관찰 유지"와 같은 계열). 실제 산출물은 새 stamp 파일·최상위 4파일 갱신이며 registry 에는 새 stamp 행 추가 + 기존 행 비고 확장으로 등재한다.
- 확인 방법(명령): `grep -n "^- reports/" docs/wiki/packages/P4b-er-redesign/01-plan.md` · `sed -n 88,93p .claude/scripts/verify-plan.sh`
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — 토큰이 파일 경로가 아니라 산출물 줄의 조각. 해소 = U7 registry 등재(새 stamp raw/traces 행, 최상위 4파일 비고 확장) + 04-review §5. 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-3f9278 · [권고] registry 에 다른 패키지로 이미 있음: eval.md → | 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: eval.md → | 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
```

### 원인 분석
- 가설: 스크립트 basename 오탐 — 01-plan 산출물 줄 `reports/pilot/raw-\<새 ts\>.jsonl.gz · traces-\<새 ts\>.jsonl` · `reports/metrics.json · calibration.json · curve.csv · eval.md` 를 verify-plan.sh 7번이 공백으로 쪼개 `.jsonl.gz`·`calibration.json`·`curve.csv`·`eval.md` 토큰으로 registry 를 grep 했다(P4 04-review 230행 "verify-plan.sh 5번 basename 오탐(F-95c6a7 계열) 관찰 유지"와 같은 계열). 실제 산출물은 새 stamp 파일·최상위 4파일 갱신이며 registry 에는 새 stamp 행 추가 + 기존 행 비고 확장으로 등재한다.
- 확인 방법(명령): `grep -n "^- reports/" docs/wiki/packages/P4b-er-redesign/01-plan.md` · `sed -n 88,93p .claude/scripts/verify-plan.sh`
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — 토큰이 파일 경로가 아니라 산출물 줄의 조각. 해소 = U7 registry 등재(새 stamp raw/traces 행, 최상위 4파일 비고 확장) + 04-review §5. 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-00846b · [권고] registry 에 다른 패키지로 이미 있음: reports/failure_cases.md → | 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: reports/failure_cases.md → | 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-225938 · [권고] registry 에 다른 패키지로 이미 있음: docs/user-setup/10-pilot-eval-run.md → | 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
상태: 열림 | 발견: 2026-09-22 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: docs/user-setup/10-pilot-eval-run.md → | 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
```

### 원인 분석
- 가설: 의도된 경고 — 이 패키지는 기존 파일을 **수정**하는 확장 패키지다(01-plan 26행 "registry 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표). 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md` · 01-plan 115~127행 재사용 표에서 해당 행의 "수정/무수정/갱신해 재사용" 분류 확인
- 확인 결과: verifier 계획 검증(02-plan-verify §1a 판정) — registry 기존 행이 P3-er/P2-tools/P4-pilot-eval 소속이며 01-plan 재사용 표가 같은 경로를 "수정"(새 모듈 없음)으로 분류. 해소 = U7 registry 비고 확장 + 04-review §5 등록(구현 에이전트·04-review). 계획 단계 조치 없음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P4b-er-redesign` (계획 단계면 `verify-plan.sh P4b-er-redesign`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

