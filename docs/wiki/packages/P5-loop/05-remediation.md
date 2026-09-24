# P5-loop · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-24 19:41 | 출처: verify-plan | 열림: 8 (필수 0) | 해소: 14

## F-25b70f · [필수] 없음: docs/wiki/packages/P5-loop/02-plan-verify.md
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-24

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P5-loop/02-plan-verify.md
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-066274 · [필수] 작업 단위(- [ ] U1 …)가 없다
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  작업 단위(- [ ] U1 …)가 없다
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-8ced33 · [필수] backlog 에 같은 문장이 없다: "**에이전트 루프(인식→해석→기록→응답)**"
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**에이전트 루프(인식→해석→기록→응답)**"
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-dfea0a · [필수] backlog 에 같은 문장이 없다: "**발화 →**" → 입력은 `POST /chat` 요청 본문의
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**발화 →**" → 입력은 `POST /chat` 요청 본문의
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-4aa2f9 · [필수] backlog 에 같은 문장이 없다: "**툴 선택**" → 그 턴의 `agent_traces` 에 `tool_nam
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**툴 선택**" → 그 턴의 `agent_traces` 에 `tool_nam
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-1c2305 · [필수] backlog 에 같은 문장이 없다: "**저장**" → 같은 요청 안에서 `events`(또는 `sc
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**저장**" → 같은 요청 안에서 `events`(또는 `sc
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-1d931c · [필수] backlog 에 같은 문장이 없다: "**응답**" → `ChatOut.reply` 가 비어 있지 않고, �
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**응답**" → `ChatOut.reply` 가 비어 있지 않고, �
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-f34275 · [필수] backlog 에 같은 문장이 없다: "**API 한 흐름으로 동작**" → 위 넷이 **HTTP 요�
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**API 한 흐름으로 동작**" → 위 넷이 **HTTP 요�
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-ebd96f · [필수] backlog 에 같은 문장이 없다: "**`POST /answers/{question_id}`로 루프 재개**" → 그
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**`POST /answers/{question_id}`로 루프 재개**" → 그
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-f92e77 · [필수] backlog 에 같은 문장이 없다: "**의존: … P4b 게이트 통과**" → `docs/wiki/packag
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: "**의존: … P4b 게이트 통과**" → `docs/wiki/packag
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-44f125 · [필수] backlog 에 같은 문장이 없다: 덧붙여, 이 패키지가 **닫는다고 선언한 R6·R7*
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: 덧붙여, 이 패키지가 **닫는다고 선언한 R6·R7*
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-4e4fe4 · [필수] P4 게이트 미통과: P5 이후는 P4-pilot-eval 완료 전에 시작할 수 없다
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-23

### 증상 (검증 출력 인용)
```
FAIL  P4 게이트 미통과: P5 이후는 P4-pilot-eval 완료 전에 시작할 수 없다
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-e93529 · [권고] registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-8e3e74 · [권고] registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-6ae8ad · [권고] registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-d68447 · [권고] registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-fdb56f · [권고] registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-7e6e84 · [권고] registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-23 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-d61978 · [필수] Refs 없음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
상태: 해소 | 발견: 2026-09-24 (verify-plan) | 해소: 2026-09-24

### 증상 (검증 출력 인용)
```
FAIL  Refs 없음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-9c9410 · [필수] Refs 없음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
상태: 해소 | 발견: 2026-09-24 (verify-plan) | 해소: 2026-09-24

### 증상 (검증 출력 인용)
```
FAIL  Refs 없음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
```

### 원인 분석
- 가설:
- 확인 방법(명령):
- 확인 결과:

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-b38c2c · [권고] registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
상태: 열림 | 발견: 2026-09-24 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
```

### 원인 분석
- 가설: 하네스 결함(02-plan-verify 2차 R-19). `verify-plan.sh` 7절의 토큰 정규식이 01-plan "산출물" 절 문장 속 `inspect.signature` 를 산출물 **경로**로 오인해 5자 확장자 규칙으로 `inspect.signa` 를 만들고, 그 가짜 토큰이 registry 의 `scripts/tools_check.py` 행 비고("`inspect.signature` 대조")에 `grep -F` 부분 일치한다. 계획 결함이 아니다 — `app/agent/gate.py` 가 `inspect.signature` 를 **호출**한다는 문장이지 그 이름의 파일을 만드는 것이 아니다.
- 확인 방법(명령): ① `sed -n '98p' .claude/scripts/verify-plan.sh` ② `awk '/^## 산출물/{f=1;next} /^## /{f=0} f && /^- /{sub(/^- /,""); print}' docs/wiki/packages/P5-loop/01-plan.md | grep -oE '[A-Za-z0-9_./-]+[.][a-z]{1,5}' | sort -u` ③ `grep -n 'inspect.signa' docs/wiki/registry.md` ④ `grep -n 'inspect.signature' docs/wiki/packages/P5-loop/01-plan.md | head -3`
- 확인 결과(verifier 3차, 2026-09-24): ① `grep -oE '[A-Za-z0-9_./-]+[.][a-z]{1,5}'` — 확장자 자리를 소문자 1~5자로 잡아 `signature` 가 `signa` 에서 잘린다. ② 22 토큰 중 실재 경로가 아닌 것 4: `app.tools`·`dataclasses.repla`·`extract.py`·`inspect.signa`(뒤 셋은 절단·옛 이름). ③ registry 67행 `| 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-tools | f2e9e05 | … \`inspect.signature\` 대조` 에만 일치. ④ 01-plan 60행(산출물 절 `app/agent/gate.py` 항목 "`inspect.signature` 인자 대조")이 토큰의 출처. → 산출물 경로 중복 아님. 해결은 이 패키지 밖(하네스 FIX 후보 — 정규식을 실재 파일 확장자 목록 또는 `[ -e "$ROOT/$o" ]` 검사로 좁힌다). 이 패키지에서는 조치 없음, 04-review 가 registry 에 `inspect.signa` 행이 생기지 않았음을 확인하면 닫는다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

