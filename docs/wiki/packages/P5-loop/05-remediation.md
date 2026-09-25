# P5-loop · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-25 22:05 (verifier 04-review) | 출처: verify-impl | 열림: 0 (필수 0) | 해소: 23

> **U8 갱신 메모.** [권고] 8건 중 7건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`)의 원인 분석을 채웠다. `F-e93529`(`app/er/judge.py`)는 하네스의 산출물-토큰 스캔 오탐(F-b38c2c 와 같은 계열)이라 이 패키지에서 조치하지 않는다. 나머지 6건은 P4b 선례(F-ed9327 등)와 같이 "기존 파일을 고치는 확장 패키지"라 **의도된 WARN**이며, 해결 단계에 적은 registry.md 비고 확장을 U8 작업에서 실제로 적용했다(커밋 `f0d3e26`). `F-b38c2c`(이미 원인 분석 완료, 하네스 FIX 후보)는 다시 손대지 않았다. 상태는 04-review 전까지 "열림"으로 유지한다(해소 표시는 검증자 몫).
>
> (메모 복원: 2026-09-25 verify-impl 이 머리말을 다시 쓰며 이 단락을 지워서, 재개 세션에서 되살렸다.)

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
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
```

### 원인 분석
- 가설: 하네스 결함(F-b38c2c 와 같은 계열) — `verify-plan.sh` 의 "## 산출물" 절 토큰 스캔이, 01-plan 59행 "`app/agent/propose.py` — … 공급자 구현(`app/er/judge.py` 의 `select_provider`·`enabled_providers`·`call_with_error_mapping` 재사용) …"처럼 **다른 산출물(`app/agent/propose.py`)을 설명하는 문장 속에서 인용된 기존 파일 경로**까지 "이 패키지가 만드는 산출물"로 오인한다. `app/er/judge.py` 는 01-plan "기존 산출물 재사용" 표(206행)에 "**무수정 재사용(import)**"로 명시돼 있고, "새로 만드는 파일" 목록에도 "고치는 기존 파일" 목록(66~73행)에도 이 경로 자체가 독립 항목으로 없다 — 계획 결함이 아니라 이미 다른 파일(`app/agent/propose.py`)을 설명하는 문장 속 인용이 토큰으로 잡힌 것이다.
- 확인 방법(명령): ① `grep -n "app/er/judge.py" docs/wiki/packages/P5-loop/01-plan.md` ② `awk '/^## 산출물/{f=1;next} /^## /{f=0} f' docs/wiki/packages/P5-loop/01-plan.md | grep -n "app/er/judge.py"` ③ `grep -n "app/er/judge.py" docs/wiki/registry.md` ④ `grep -n "무수정 재사용" docs/wiki/packages/P5-loop/01-plan.md | grep "judge.py"`
- 확인 결과(2026-09-25): ① 01-plan 전체에서 5곳 등장(27·59·86·151·394행) — 전부 `app/agent/propose.py`(U2) 또는 판정 표 7행 명령·"읽은 카드"의 **재사용 설명 문장** 안이고, 독립된 산출물 불릿(`- app/er/judge.py — …`)은 없다. ② "## 산출물" 절 안에서는 59행 한 줄만 걸리며 그 줄의 주어는 `app/agent/propose.py`다. ③ registry 84행에 `P3-er`(`b1f2782`) 소속으로 이미 있고 `select_provider`·`enabled_providers`·`call_with_error_mapping`·`JUDGES` 를 담고 있다 — U2·U3 이 실제로 재사용한 함수들과 일치한다. ④ 206행 재사용 표가 "무수정 재사용(import)"로 명시. → 산출물 경로 중복이 아니다. **이 패키지에서는 조치하지 않는다.** 04-review 가 registry 84행에 P5-loop 소속 새 행이나 잘못된 비고가 생기지 않았음을 확인하면 닫는다. 근본 수정(정규식이 "산출물 불릿의 주어"와 "설명문 속 인용 경로"를 구분하도록 `verify-plan.sh` 개선)은 이 패키지 밖의 하네스 FIX 후보다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 84행은 P3-er 소속 그대로, P5-loop 소속 행·비고 0건(163행 propose.py 비고의 '재사용' 설명문만), app/er/judge.py 는 P5-loop 커밋 어디에도 없다 → 원인 분석의 닫힘 조건 충족. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-8e3e74 · [권고] registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
```

### 원인 분석
- 가설: **의도된 경고** — P4b F-ed9327 과 같은 계열이다. 이 패키지는 새 모듈이 아니라 `app/api/routes.py` 를 **수정**하는 확장 패키지다. 01-plan 68행 "`app/api/routes.py` — `POST /chat` 추가, `POST /answers/{question_id}` 에 재개 뒤 절반 연결", 73행 "고치는 기존 파일" 목록, 75행 "허용 파일" 각주가 이 경로를 "고치는 기존 파일"로 명시하고, 95행 U8 이 "고친 기존 파일(`app/api/routes.py`·`schemas.py`·`deps.py`·`app/settings.py`)은 **비고에 P5-loop 한 줄과 커밋 해시를 더한다**(새 행을 만들지 않는다 — F-0ffff5·F-95c6a7 선례)"고 직접 지시한다. 중복 구현이 아니라 같은 행의 비고 확장 대상이다.
- 확인 방법(명령): ① `grep -n "app/api/routes.py" docs/wiki/packages/P5-loop/01-plan.md` ② `grep -n "app/api/routes.py" docs/wiki/registry.md` ③ `git log --oneline --grep "P5-loop" -- app/api/routes.py`
- 확인 결과(2026-09-25): ① 68·75·95·130·211행에 걸쳐 "고치는 기존 파일"로 반복 명시. ② registry 65행 `| 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-tools | 4d5817e | … (재개는 P5-loop, R7·D2) |` — 비고에 이미 "재개는 P5-loop 몫"이라고 예고되어 있었다. ③ `POST /chat` 은 U6(`d5c8ec9`), `/answers` 재개 뒤 절반은 U7(`7df3ada`)에서 추가됐다(03-log·gitlog.sh 확인). → 산출물 중복이 아니라 계획대로 기존 행을 수정한 것이다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/registry.md` 65행 비고에 "P5-loop U6(`d5c8ec9`)·U7(`7df3ada`): `POST /chat`·`/answers` 재개 뒤 절반 추가" 한 줄 추가(새 행 생성 안 함) | `grep -n "app/api/routes.py" docs/wiki/registry.md` | 65행 비고에 `P5-loop` 문자열과 두 해시 포함, 행 수는 그대로 65행 1개 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 65행 비고에 'P5-loop U6(d5c8ec9)·U7(7df3ada)' 포함, 경로 행 수 2 = 기존 행 + 계획된 POST /chat 엔드포인트 신규 행(167행, 01-plan U8 '엔드포인트 1'), git log 로 두 커밋이 routes.py 를 실제로 바꿈. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-6ae8ad · [권고] registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools
```

### 원인 분석
- 가설: **의도된 경고**(F-8e3e74 와 같은 계열) — 01-plan 69행 "`app/api/schemas.py` — `ChatIn`·`ChatOut`·`AnswerOut` 확장(재개 결과 필드)", 73행 "고치는 기존 파일" 목록, 95행 U8 지시가 이 경로를 "고치는 기존 파일"로 명시한다. 중복 구현이 아니라 비고 확장 대상.
- 확인 방법(명령): ① `grep -n "app/api/schemas.py" docs/wiki/packages/P5-loop/01-plan.md` ② `grep -n "app/api/schemas.py" docs/wiki/registry.md` ③ `git log --oneline --grep "P5-loop" -- app/api/schemas.py`
- 확인 결과(2026-09-25): ① 69·75·95·130·213행에서 "고치는 기존 파일"·"갱신해 재사용"으로 일관되게 지시. ② registry 66행 `| 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools | 4d5817e | AnswerIn·AnswerOut·HealthOut … |` — P2 가 만든 기존 스키마. ③ U6(`d5c8ec9`)이 `ChatIn`·`StoredOut`·`ChatPendingQuestionOut`·`ChatOut` 을 추가하고, U7(`7df3ada`)이 `AnswerOut` 을 `ChatOut` 과 같은 5필드로 확장했다(03-log). → 계획대로 기존 행을 수정한 것, 중복 산출물 아님.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/registry.md` 66행 비고에 "P5-loop U6(`d5c8ec9`)·U7(`7df3ada`): `ChatIn`/`ChatOut` 신설, `AnswerOut` 5필드로 확장" 한 줄 추가(새 행 생성 안 함) | `grep -n "app/api/schemas.py" docs/wiki/registry.md` | 66행 비고에 `P5-loop` 문자열과 두 해시 포함, 행 수는 그대로 66행 1개 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 66행 비고에 'P5-loop U6(d5c8ec9)·U7(7df3ada)' 포함, 경로 행 수 1. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-d68447 · [권고] registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
```

### 원인 분석
- 가설: **의도된 경고**(같은 계열) — 01-plan 70행 "`app/api/deps.py` — 채팅용 `ToolContext` 조립 … + 재개 입력 조립 `load_resume_input(...)`", 73행 "고치는 기존 파일" 목록, 95행 U8 지시가 이 경로를 "고치는 기존 파일"로 명시한다.
- 확인 방법(명령): ① `grep -n "app/api/deps.py" docs/wiki/packages/P5-loop/01-plan.md` ② `grep -n "app/api/deps.py" docs/wiki/registry.md` ③ `git log --oneline --grep "P5-loop" -- app/api/deps.py`
- 확인 결과(2026-09-25): ① 70·75·94·130·212행. ② registry 64행 `| 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py | P2-tools | 4d5817e | get_session()·build_ctx()(답할 pending_questions 행의 session_id 사용, 결정12) |`. ③ U6(`d5c8ec9`)이 `resolve_session_id`·`build_chat_ctx`·`_embedder_from_env`·`get_embedder`·`get_proposer`·`get_judge` 를 추가했고, U7(`7df3ada`)이 `load_resume_input`·`build_ctx(embedder=...)` 를 더했다(03-log). `build_ctx` 의 기존 결정 12 규약(답할 행의 `session_id` 권위)은 손대지 않았다(01-plan 70행이 요구한 대로). → 기존 행 수정, 중복 아님.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/registry.md` 64행 비고에 "P5-loop U6(`d5c8ec9`)·U7(`7df3ada`): 채팅용 ctx 조립(`build_chat_ctx`)·`load_resume_input`·임베더/제안자/판정기 의존성 추가" 한 줄 추가(새 행 생성 안 함) | `grep -n "app/api/deps.py" docs/wiki/registry.md` | 64행 비고에 `P5-loop` 문자열과 두 해시 포함, 행 수는 그대로 64행 1개 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 64행 비고에 'P5-loop U6(d5c8ec9)·U7(7df3ada)' 포함, 경로 행 수 1. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-fdb56f · [권고] registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
```

### 원인 분석
- 가설: **의도된 경고**(같은 계열) — 01-plan 71행 "`app/settings.py` — 루프 설정 상수(상한·추출 모델·타임아웃, 결정 A·G)", 73행 "고치는 기존 파일" 목록. 이 파일은 P2-tools(`f217190`)·P3-er(`593c254`·`b1f2782`)·P3-llm-providers(`c01381d`)·P4b(`dbcfca0`)가 이미 여러 차례 비고를 늘려온 **공용 설정 파일**이고, registry 53행 비고 자체가 그 누적 이력이다 — P5 도 같은 관례를 따른다.
- 확인 방법(명령): ① `grep -n "app/settings.py" docs/wiki/packages/P5-loop/01-plan.md` ② `grep -n "app/settings.py" docs/wiki/registry.md` ③ `git log --oneline --grep "P5-loop" -- app/settings.py`
- 확인 결과(2026-09-25): ① 3(담당 각주)·71·75·85·95행. ② registry 53행에 P2-tools 를 원 소속으로 두고 P3-er·P3-llm-providers·P4b-er-redesign 비고가 이미 이어 붙어 있다(선례). ③ U1(`3e4db92`)이 루프 상수(언급 5·이벤트 5·일정 3·`LOOP_MAX_PROPOSALS=13`·`LOOP_MAX_RESUME_BYTES=8192`)를 추가했다(03-log "5·5·3·13·8192"). → 기존 행 비고 확장 대상, 중복 아님.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/registry.md` 53행 비고에 "P5-loop U1(`3e4db92`): `LOOP_MAX_MENTIONS/EVENTS/SCHEDULES=5/5/3`·`LOOP_MAX_PROPOSALS=13`·`LOOP_MAX_RESUME_BYTES=8192` 등 루프 상수 추가" 한 줄 추가(새 행 생성 안 함) | `grep -n "app/settings.py" docs/wiki/registry.md` | 53행 비고에 `P5-loop` 문자열과 해시 포함, 행 수는 그대로 53행 1개 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 53행 비고에 P5-loop U1(3e4db92) 루프 상수 추가 기록, 경로 행 수 1, git log 로 3e4db92 가 settings.py 를 바꿈. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-7e6e84 · [권고] registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
```

### 원인 분석
- 가설: **의도된 경고**(같은 계열) — 01-plan 72행 "`tests/test_api.py` — `AnswerOut` 확장에 따른 기존 단언 갱신(단언을 **없애지 않는다**)", 355행 리스크 절이 "`AnswerOut` 확장은 기존 테스트를 건드린다 … 기대값을 바꾸는 것과 단언을 없애는 것은 다르다(P4b 가 남긴 교훈). 404/409/422 단언은 그대로 유지한다"고 명시한다.
- 확인 방법(명령): ① `grep -n "tests/test_api.py" docs/wiki/packages/P5-loop/01-plan.md` ② `grep -n "tests/test_api.py" docs/wiki/registry.md` ③ `git log --oneline --grep "P5-loop" -- tests/test_api.py` ④ `git show 7df3ada --stat -- tests/test_api.py`
- 확인 결과(2026-09-25): ① 72·215·355행. ② registry 76행 `| 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-tools | 4d5817e | TestClient + dependency_overrides[get_session](결정13) |`. ③④ U7(`7df3ada`)에서 13줄 변경(+/-) — 03-log U7 항목 "`tests/test_api.py` 기존 단언 확장(삭제 없음)"과 일치, 404/409/422 케이스는 그대로 남아 있다(FIX-004 교훈 준수). → 기존 행 비고 확장 대상, 중복 산출물 아님.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/registry.md` 76행 비고에 "P5-loop U7(`7df3ada`): `AnswerOut` 5필드 확장에 따른 200 응답 단언 갱신, 404/409/422 단언 유지" 한 줄 추가(새 행 생성 안 함) | `grep -n "tests/test_api.py" docs/wiki/registry.md` | 76행 비고에 `P5-loop` 문자열과 해시 포함, 행 수는 그대로 76행 1개 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 76행 비고에 'P5-loop U7(7df3ada)' 포함(404/409/422 단언 유지 명시), 경로 행 수 1. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 해소 | 발견: 2026-09-23 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: **의도된 경고, 그러나 형식 하나가 이미 바뀌어 있다** — 01-plan 37·73·95·217행이 "README.md 실행법 한 절"·"진행 표 P5 행 + 로컬 실행법 한 절(절을 새로 만들지 않고 기존 절에 이어 붙인다)"을 지시하고, registry 33행 비고는 P0~P4b 까지 **"진행 표 Pn 행" 갱신 이력**을 나열해 온 선례다. 다만 2026-09-23 "docs(readme): 짧은 공통 형식으로 재작성"(`56ced8b`)·"향후 계획 · 재실행 문단의 날짜 표기 제거"(`4f82d48`)·"향후 계획 · 알려진 한계 절 삭제"(`90a6b53`) 세 커밋이 README 를 캡스톤 공통 양식으로 **전면 재작성**하면서 표 형태의 "진행 표"(Pn 별 행)를 없애고, 로컬 실행 절차도 `docs/RUNNING.md` 로 옮겼다(README 8절은 요약 + 링크만). 따라서 "진행 표 P5 행"을 문자 그대로 만들 대상이 지금 README 에는 없다 — 계획 문서(01-plan)가 그 재작성 이전 README 구조를 전제로 쓰였다.
- 확인 방법(명령): ① `grep -n "진행 표\|진행 상태" README.md docs/RUNNING.md` ② `git log --oneline -- README.md | head -5` ③ `git show 56ced8b --stat -- README.md` ④ `grep -n "README.md" docs/wiki/registry.md`
- 확인 결과(2026-09-25): ① README.md·docs/RUNNING.md 어디에도 "진행 표"라는 이름의 표가 없다(README 16행이 "에이전트 대화 루프 · 브리핑 · 화면 · 배포는 아직 없습니다"라는 **서술형 문장**으로 그 역할을 대신한다). ② README.md 는 `56ced8b`(2026-09-23) 이후 짧은 공통 형식이다. ③ 그 커밋이 섹션을 표 대신 산문(개요·핵심 기능·기술적 차별점)으로 재작성했다(diff 확인). ④ registry 33행 비고가 재작성 이전 관례(Pn 행)를 그대로 적고 있어 **registry 자체도 이 재작성을 아직 따라잡지 못했다**. → 중복 산출물이 아니라 계획대로 수정 대상인 것은 맞지만, 01-plan·registry 의 "진행 표 Pn 행" 표현은 현재 README 구조와 어긋난다(결정·명세를 바꿔야 하는 문제는 아니고, 표현 그대로 대신 README 의 현재 형식에 맞춰 적용한다). 이 패키지에서는 README 16행(개요 상태 문장)과 "핵심 기능" 절에 에이전트 루프·`/chat`·`/answers` 재개를 반영하는 것으로 "진행 표 P5 행"에 대응하는 갱신을 한다(아래 해결 단계). **결정 카드를 바꿔야 하는 문제가 아니므로 FIX/CR 로 올리지 않는다** — 표현 차이를 보고만 남긴다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `README.md` 16행(개요 상태 문장)에서 "에이전트 대화 루프 … 아직 없습니다"를 "에이전트 대화 루프(`POST /chat`·`/answers` 재개)까지 있습니다. 브리핑·화면·배포는 아직 없습니다"로 갱신, "핵심 기능" 절에 에이전트 루프 불릿 추가 | `grep -n "에이전트 대화 루프" README.md` | "아직 없습니다" 문구에서 "에이전트 대화 루프"가 빠지고 "브리핑·화면·배포"만 남는다 | 완료(U8, f0d3e26) |
| 2 | `docs/RUNNING.md` "백엔드 실행 (FastAPI)" 절에 `/chat`·`/answers` 재개 curl 예 이어 붙이기(새 절 신설 안 함) | `grep -n "POST /chat" docs/RUNNING.md` | 해당 절 안에서 1건 이상 일치 | 완료(U8, f0d3e26) |
| 3 | `docs/wiki/registry.md` 33행 비고에 "P5-loop U8: README 16행 개요 문장·핵심 기능 절 갱신(에이전트 루프 반영), `docs/RUNNING.md` 백엔드 실행 절에 `/chat`·재개 curl 이어 붙임 — README 재작성(`56ced8b`) 이후 '진행 표'가 없어 서술형 절로 대응" 한 줄 추가 | `grep -n "P5-loop" docs/wiki/registry.md` | 33행 비고에 `P5-loop` 포함 | 완료(U8, f0d3e26) |

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — README 16행 개요 문장이 '에이전트 루프까지 있습니다. 브리핑·화면·배포는 아직 없습니다' 로 바뀜, 51행 핵심 기능 불릿 추가, docs/RUNNING.md 122행 POST /chat 절, registry 33행 비고에 P5-loop U8 기록 — 해결 단계 1~3 완료 판정 명령 전부 기대 출력과 일치. verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

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
상태: 해소 | 발견: 2026-09-24 (verify-plan) | 해소: 2026-09-25 (verifier 04-review)

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
- 결과 파일(evidence/): `evidence/20260925-2145-verifier-remediation-closure.txt` — registry 에 산출물 경로가 inspect.signa 인 행 0건 → 원인 분석의 닫힘 조건 충족(하네스 FIX 후보는 이 패키지 밖). verify-impl 재실행: `evidence/20260925-2200-verify-impl.txt`(첫 실행 2155 는 04-review 표 형식 FAIL 2, 코드 무관)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-14f3ef · [권고] 04-review.md 없음 (완료 검토 전이면 정상)
상태: 해소 | 발견: 2026-09-25 (verify-impl) | 해소: 2026-09-25 (verifier 04-review)

### 증상 (검증 출력 인용)
```
WARN  04-review.md 없음 (완료 검토 전이면 정상)
```

### 원인 분석
- 가설: 완료 검토 전 정상 경고 — 첫 verifier 세션이 04-review.md 를 쓰기 전에 끊겨(HANDOFF 2026-09-25) 파일이 없었다. 계획·코드 결함 아님.
- 확인 방법(명령): `ls docs/wiki/packages/P5-loop/04-review.md` → `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P5-loop`
- 확인 결과(2026-09-25 verifier): 04-review.md 작성(검토자 verifier, 결과 완료) 뒤 재실행 `evidence/20260925-2200-verify-impl.txt` — `FAIL=0 WARN=0`, "04-review.md 없음" WARN 소멸, 수용 기준 표 10행 증거 전부 PASS.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P5-loop/04-review.md` 작성(verifier) | `bash .claude/scripts/verify-impl.sh P5-loop` | `WARN  04-review.md 없음` 줄이 사라지고 `검토자 = verifier` PASS | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P5-loop` (계획 단계면 `verify-plan.sh P5-loop`)
- 결과 파일(evidence/): `evidence/20260925-2200-verify-impl.txt` (FAIL 0 / WARN 0). 첫 실행 `evidence/20260925-2155-verify-impl.txt` 는 04-review §2b 표 형식 때문에 FAIL 2 — 표를 2단계 절로 분리하고 8행 증거 열을 채운 뒤 재실행.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

