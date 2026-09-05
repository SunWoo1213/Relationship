# P2-tools · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-05 15:22 | 출처: verify-plan | 열림: 15 (필수 0) | 해소: 1

## F-8041b0 · [필수] 없음: docs/wiki/packages/P2-tools/02-plan-verify.md
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P2-tools/02-plan-verify.md
```

### 원인 분석
- 가설: 02-plan-verify.md 는 verifier(fable)가 쓰는 문서(L-002). 계획 초안 직후 기계 검증에서는 항상 없다 — 절차상 정상.
- 확인 방법(명령): `ls docs/wiki/packages/P2-tools/`
- 확인 결과: 01-plan.md·05-remediation.md·evidence/ 만 존재

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | verifier 위임(사용자 승인 + `--stage verifier`) → 02-plan-verify.md 작성 | `bash .claude/scripts/verify-plan.sh P2-tools` | `PASS  존재: …02-plan-verify.md` | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): (verifier 실행 후)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-673d47 · [권고] registry 에 다른 패키지로 이미 있음: app/db/models.py → | 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema |
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/db/models.py → | 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema |
```

### 원인 분석
- 가설: 해당 파일은 P1-schema(또는 하네스) 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(config repr=False, models ALIAS_SOURCES 상수, conftest DB 픽스처, test_config 테스트 1건, README 진행 표)만 하고 **새 행을 만들지 않고 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P1-schema/하네스)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-ca32f5 · [권고] registry 에 다른 패키지로 이미 있음: app/config.py → | 모듈 | 백엔드 패키지 골격(DB 접속 설정) | app/config.py | P1-sch
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/config.py → | 모듈 | 백엔드 패키지 골격(DB 접속 설정) | app/config.py | P1-sch
```

### 원인 분석
- 가설: 해당 파일은 P1-schema(또는 하네스) 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(config repr=False, models ALIAS_SOURCES 상수, conftest DB 픽스처, test_config 테스트 1건, README 진행 표)만 하고 **새 행을 만들지 않고 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P1-schema/하네스)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-127d01 · [권고] registry 에 다른 패키지로 이미 있음: tests/conftest.py → | 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftes
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/conftest.py → | 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftes
```

### 원인 분석
- 가설: 해당 파일은 P1-schema(또는 하네스) 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(config repr=False, models ALIAS_SOURCES 상수, conftest DB 픽스처, test_config 테스트 1건, README 진행 표)만 하고 **새 행을 만들지 않고 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P1-schema/하네스)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-320519 · [권고] registry 에 다른 패키지로 이미 있음: tests/test_config.py → | 테스트 | 접속 설정 해석(DB 없이) | tests/test_config.py | P1-schema
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_config.py → | 테스트 | 접속 설정 해석(DB 없이) | tests/test_config.py | P1-schema
```

### 원인 분석
- 가설: 해당 파일은 P1-schema(또는 하네스) 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(config repr=False, models ALIAS_SOURCES 상수, conftest DB 픽스처, test_config 테스트 1건, README 진행 표)만 하고 **새 행을 만들지 않고 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P1-schema/하네스)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: 해당 파일은 P1-schema(또는 하네스) 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(config repr=False, models ALIAS_SOURCES 상수, conftest DB 픽스처, test_config 테스트 1건, README 진행 표)만 하고 **새 행을 만들지 않고 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P1-schema/하네스)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2c37bd · [권고] registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
```

### 원인 분석
- 가설: requirements.txt 는 P1-schema 소유 행이 있다. 개정 1 에서 U1 이 fastapi·uvicorn·httpx 를 추가하지만 새 행이 아니라 기존 행 비고 갱신. 의도된 WARN.
- 확인 방법(명령): `grep -c "| requirements.txt" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(P1-schema)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — U9 에서 기존 행 비고 갱신, 새 행 금지 | `grep -c "| requirements.txt" docs/wiki/registry.md` | 1 | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-08b3db · [권고] 판정 방법 표의 'trace 기록(원칙9)'·'D1 강제(R6)' 두 행이 POSTGRES_PORT=5433 과 -rs 없이 pytest 를 부른다 — 로컬 5433 이 아닌 기본 5432 로 붙어 dbtest 가 조용히 skip 되고 초록으로 끝날 수 있다(계획 자신의 리스크 '실 DB 테스트가 조용히 skip 된다' 대응 (a)와 모순). 04-review 는 이 두 행도 POSTGRES_PORT=5433 … -rs 로 실행한 출력만 증거로 받는다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  판정 방법 표의 'trace 기록(원칙9)'·'D1 강제(R6)' 두 행이 POSTGRES_PORT=5433 과 -rs 없이 pytest 를 부른다 — 로컬 5433 이 아닌 기본 5432 로 붙어 dbtest 가 조용히 skip 되고 초록으로 끝날 수 있다(계획 자신의 리스크 '실 DB 테스트가 조용히 skip 된다' 대응 (a)와 모순). 04-review 는 이 두 행도 POSTGRES_PORT=5433 … -rs 로 실행한 출력만 증거로 받는다
```

### 원인 분석
- 가설: 01-plan 판정 방법 표(117·118행)는 개정 전 초안 문장을 그대로 두어 다른 행과 달리 `POSTGRES_PORT=5433`·`-rs` 가 빠졌다. `db_engine` 픽스처가 접속 실패 시 `pytest.skip` 하므로(결정 8) 5432 로 붙으면 dbtest 전부 skip 후 rc 0.
- 확인 방법(명령): `grep -n 'pytest tests/test_tools' docs/wiki/packages/P2-tools/01-plan.md`
- 확인 결과: 117행 `pytest tests/test_tools_context.py tests/test_tools_persons.py -q`, 118행 `pytest tests/test_tools_persons.py -k confirm -q` — 둘 다 포트·`-rs` 없음. 115·119·122행은 있음. 04-review(verifier)가 두 행을 `POSTGRES_PORT=5433 python -m pytest … -q -rs` 로 직접 실행해 skip 0 을 증거로 남긴다(계획 문서는 고치지 않음).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-b97a06 · [권고] D1 강제 검사가 '답했는가'만 보고 '무엇이라 답했는가'를 보지 않는다 — new_person 질문에 부정 선택지로 답해도 answered_at 이 채워지므로 create_person 이 통과한다. D1 '승인 시에만 create_person'. U4 또는 P5-loop 01-plan 에서 긍정 선택지 규약(예: options 첫 항목 또는 context.affirmative)을 정하고 어느 쪽이 검사하는지 03-log 에 남긴다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  D1 강제 검사가 '답했는가'만 보고 '무엇이라 답했는가'를 보지 않는다 — new_person 질문에 부정 선택지로 답해도 answered_at 이 채워지므로 create_person 이 통과한다. D1 '승인 시에만 create_person'. U4 또는 P5-loop 01-plan 에서 긍정 선택지 규약(예: options 첫 항목 또는 context.affirmative)을 정하고 어느 쪽이 검사하는지 03-log 에 남긴다
```

### 원인 분석
- 가설: 01-plan 리스크 'D1 강제의 구멍'(150행)이 정한 검사 4조건(존재·`kind=new_person`·`answered_at IS NOT NULL`·같은 `session_id`)에 답 내용 조건이 없다. D01 카드 '승인 시에만 `create_person`' 의 '승인' 을 P2 가 판별할 규약(긍정 선택지)이 계획에 없다 — `options` 는 호출자(P3/P5)가 주는 자유 문자열.
- 확인 방법(명령): `grep -n 'answered_at IS NOT NULL' docs/wiki/packages/P2-tools/01-plan.md; grep -n '승인 시에만' docs/wiki/decisions/D01-new-person-confirm.md`
- 확인 결과: 01-plan 150행 조건 목록에 answer 검사 없음. D01 '승인 시에만 `create_person`', '코드에서 지켜야 할 것: answered pending_question 을 거친다' — 계획은 후자를 충족하나 전자(승인 여부)는 P5 루프 몫으로 남는다. U4 03-log 에 '부정 답도 통과한다, 판별은 P5' 를 명시하거나 `context.affirmative` 규약을 U6 에서 정한다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 긍정 답 규약 확정(U4) — `pending_questions.context`(JSONB)에 `AFFIRMATIVE_KEY = "affirmative_options"`(`app/tools/types.py`) 키로 긍정 선택지 목록을 넣는 것으로 규약을 정한다(`ask_user`(U6)가 이 키를 채운다). `app/tools/persons.py` 의 `_require_confirmation(ctx, kinds=...)` 가 `question.answer in context["affirmative_options"]` 를 검사하고, 키가 없으면 안전한 기본값으로 거부(`ConfirmationRequired("not_affirmative")`) | `POSTGRES_PORT=5433 python -m pytest tests/test_tools_persons.py -q -k "negative_answer or without_affirmative"` | 2 passed (부정 답·키 없음 각각 `ConfirmationRequired`) | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): `docs/wiki/packages/P2-tools/evidence/20260905-1620-{pytest-u4,mutation-u4}.txt` — 변이 (b)(긍정 답 검사 제거)에서 두 테스트가 `DID NOT RAISE` 로 FAILED 하는 것을 확인 후 원복, 전체 105 passed 로 재확인

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(D01 "승인 시에만" 을 코드로 구현) | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-4d8d96 · [권고] @traced 의 step='tool_error' 행은 같은 세션에 flush 되므로 호출자(session_scope·get_session)가 예외 시 rollback 하면 함께 사라진다 — 운영에서는 오류 trace 가 남지 않는다. 결정 2(툴은 commit 하지 않음)와 U2 테스트(롤백 전 조회)는 서로 맞지만 원칙9 관점의 한계다. 03-log 에 '오류 trace 는 트랜잭션과 함께 롤백된다'를 명시하거나 별도 커넥션 기록을 P5 로 넘길지 결정
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  @traced 의 step='tool_error' 행은 같은 세션에 flush 되므로 호출자(session_scope·get_session)가 예외 시 rollback 하면 함께 사라진다 — 운영에서는 오류 trace 가 남지 않는다. 결정 2(툴은 commit 하지 않음)와 U2 테스트(롤백 전 조회)는 서로 맞지만 원칙9 관점의 한계다. 03-log 에 '오류 trace 는 트랜잭션과 함께 롤백된다'를 명시하거나 별도 커넥션 기록을 P5 로 넘길지 결정
```

### 원인 분석
- 가설: 결정 2 '툴은 commit 하지 않고 flush 까지' + `session_scope()`/`get_session()` '예외 시 rollback' + 범위 25행 '예외가 나면 step=tool_error 행을 남기고 예외를 다시 올린다' 세 문장이 동시에 성립하면 tool_error 행은 항상 롤백된다. U2 테스트는 롤백 픽스처 안(롤백 전)에서 조회하므로 통과하지만 운영 경로에서는 행이 남지 않는다.
- 확인 방법(명령): `grep -nE 'tool_error|예외 시 rollback|flush' docs/wiki/packages/P2-tools/01-plan.md`
- 확인 결과: 25행(tool_error 기록), 22행·34행(예외 시 rollback), 133행(flush 까지) — 상충 확인. P2 의 예외는 검증 오류(`InvalidValue`·`PersonNotFound`·`ConfirmationRequired`)이므로 원칙9 '판정 근거' 손실은 아니나, 03-log 에 한계를 적고 별도 커넥션 기록 여부를 P5-loop 01-plan 에 넘긴다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `app/tools/context.py` 모듈 docstring 에 "tool_error 행의 한계(F-4d8d96 — 우회 구현 금지)" 절을 명시 — 별도 커넥션 기록 여부는 고치지 않고 P5-loop 01-plan 결정 사항으로 명문 인계 | `grep -n "F-4d8d96" app/tools/context.py` | 모듈 docstring 안에 "F-4d8d96"·"P5-loop 01-plan 이 결정한다" 문구 존재 | 완료(별도 커넥션 기록 여부는 P5-loop 로 인계, 이 소견 자체는 문서화로 닫되 근본 설계는 유지) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-3c8d4a · [권고] 결정 4·5 의 'U8 에서'(registry 26행 비고 좁히기, S3.1 카드 한 줄 추가)는 개정 1 전 번호다 — 개정 후 U8 은 FastAPI 골격이고 문서 단위는 U9. S3.1 카드 갱신(ALIAS_SOURCES 값 집합)은 산출물 목록과 U9 본문 어디에도 없다. 구현자는 U9 에서 docs/wiki/specs/S3.1-schema-v2.md 에 '(P2 결정 5)' 주석으로 한 줄 추가하고 03-log 에 적는다(CR 불필요 — S3.1 의 N=1536 주석과 같은 방식)
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  결정 4·5 의 'U8 에서'(registry 26행 비고 좁히기, S3.1 카드 한 줄 추가)는 개정 1 전 번호다 — 개정 후 U8 은 FastAPI 골격이고 문서 단위는 U9. S3.1 카드 갱신(ALIAS_SOURCES 값 집합)은 산출물 목록과 U9 본문 어디에도 없다. 구현자는 U9 에서 docs/wiki/specs/S3.1-schema-v2.md 에 '(P2 결정 5)' 주석으로 한 줄 추가하고 03-log 에 적는다(CR 불필요 — S3.1 의 N=1536 주석과 같은 방식)
```

### 원인 분석
- 가설: 개정 1 에서 U8(FastAPI)이 삽입되며 문서 단위가 U9 로 밀렸으나 결정 4(135행)·결정 5(136행)의 'U8 에서' 는 갱신되지 않았다. S3.1 카드 한 줄 추가는 산출물 목록(58~91행)과 U9(102행) 어디에도 없다.
- 확인 방법(명령): `grep -n 'U8 에서' docs/wiki/packages/P2-tools/01-plan.md; grep -n 'S3.1-schema-v2.md' docs/wiki/packages/P2-tools/01-plan.md`
- 확인 결과: 135행·136행 'U8 에서' 2건. 산출물·U9 에 S3.1 카드 경로 없음. CR 판단: S3.1 원문(resolution-plan §3.1)은 alias source 값 집합을 정하지 않았고 P1 04-review §7 이 'P2 결정' 으로 넘겼다 — 카드에 '(P2 결정 5)' 주석 한 줄은 S3.1 의 'N=1536: D4 확정' 주석과 같은 갱신이며 기획서 변경이 아니다. CR 불필요. 구현자는 U9 에서 카드 갱신 + 03-log 기록.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-fbaaae · [권고] 결정 12 '없는 id·다른 사용자 → 404' 중 '다른 사용자'는 강제할 수 없다 — pending_questions 에는 user_id 컬럼이 없다(session_id 만, app/db/models.py 201~217행). security.md §5 'user_id 조건'은 persons 경유 조회에만 적용된다. 계획 문구를 '없는 id → 404'로 읽고, pending_questions·agent_traces 의 사용자 격리 부재를 03-log·P5 인계에 명시한다
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05 (U6)

### 증상 (검증 출력 인용)
```
WARN  결정 12 '없는 id·다른 사용자 → 404' 중 '다른 사용자'는 강제할 수 없다 — pending_questions 에는 user_id 컬럼이 없다(session_id 만, app/db/models.py 201~217행). security.md §5 'user_id 조건'은 persons 경유 조회에만 적용된다. 계획 문구를 '없는 id → 404'로 읽고, pending_questions·agent_traces 의 사용자 격리 부재를 03-log·P5 인계에 명시한다
```

### 원인 분석
- 가설: 결정 12(143행) '없는 id·다른 사용자 → 404' 는 `pending_questions` 에 `user_id` 가 있다고 전제하나 스키마 v2(S3.1·`app/db/models.py`)에는 `session_id` 만 있다. 단일 사용자(`APP_USER_ID`)라 실효 문제는 없으나 계획 문구가 구현 불가능한 조건을 담는다.
- 확인 방법(명령): `grep -nE 'class PendingQuestion' -A 20 app/db/models.py | grep -c user_id`
- 확인 결과: 0 (`PendingQuestion` 에 `user_id` 없음, 217행 `session_id` 만). `AgentTrace` 도 동일(246행). security.md §5 'user_id 조건' 은 `persons` 를 거치는 조회에만 걸 수 있다. U8 03-log 에 '404 는 없는 id 만' 으로 적고 두 테이블의 격리 부재를 P5 인계에 명시.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `app/tools/questions.py` 모듈 docstring "user_id 격리 부재(F-fbaaae, 열린 소견)" 절에 `pending_questions`(및 `agent_traces`)가 `user_id` 컬럼이 없어 "다른 사용자의 질문"을 걸러낼 수 없다는 사실과, 이 격리는 P5-loop 의 세션→사용자 귀속 계층이 대신 맡아야 한다는 인계를 명문화(코드 변경 없음, U8 이 만들 `POST /answers/{id}` 는 이 전제를 그대로 상속 — "없는 id → 404"만 강제 가능) | `grep -n "user_id 격리 부재" app/tools/questions.py` | 1건 이상 매치 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): `docs/wiki/packages/P2-tools/evidence/20260905-1645-pytest-u6-final.txt`(166 passed, `answer_question`·`ask_user` 모두 `user_id` 조건 없이 `question_id`/`session_id` 로만 동작함을 테스트가 전제)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 (S3.1 이 `pending_questions` 에 `user_id` 를 두지 않은 것은 P1-schema 결정이며, 이 소견은 그 사실을 문서화하는 것으로 해소한다 — 스키마 변경 아님)
- FIX/CR 로 올려야 하는가: 아니오 (P5-loop 01-plan 이 세션→사용자 귀속 계층으로 이 사각지대를 메울지 결정)

## F-0010e6 · [권고] ALIAS_SOURCES 상수를 U4 에서 추가하지만 U3(search_person) 테스트가 이미 person_aliases 행(source NOT NULL)을 만든다 — U3 픽스처가 문자열을 직접 쓰면 이중 출처. ALIAS_SOURCES 는 U2(툴 공통) 또는 U3 첫머리로 당긴다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  ALIAS_SOURCES 상수를 U4 에서 추가하지만 U3(search_person) 테스트가 이미 person_aliases 행(source NOT NULL)을 만든다 — U3 픽스처가 문자열을 직접 쓰면 이중 출처. ALIAS_SOURCES 는 U2(툴 공통) 또는 U3 첫머리로 당긴다
```

### 원인 분석
- 가설: 작업 단위 순서: U3(96행) `search_person` 테스트가 별칭 행을 만들어야 하는데 `person_aliases.source` 는 NOT NULL(P1 04-review §7)이고 `ALIAS_SOURCES` 는 U4(97행)에서 추가된다. U3 픽스처가 리터럴 `'user_said'` 를 쓰면 상수 도입 후 이중 출처.
- 확인 방법(명령): `grep -nE 'ALIAS_SOURCES' docs/wiki/packages/P2-tools/01-plan.md`
- 확인 결과: 29행(범위)·75행(산출물)·97행(U4) — U3 에는 없음. 구현자가 U2 또는 U3 첫 커밋에 상수를 넣고 03-log '계획과 다르게 한 것' 에 적으면 해소(계획 수정 불필요).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `ALIAS_SOURCES` 상수를 U4 가 아니라 **U2**(`app/db/models.py`, `QUESTION_KINDS` 다음 자리)에 추가 — U3(`search_person`)가 `person_aliases` 행을 만들 때 리터럴 문자열이 아니라 이 상수를 import 하게 함(03-log U2 항목에 기록) | `python -c "from app.db.models import ALIAS_SOURCES; print(ALIAS_SOURCES)"` | `('user_said', 'confirmed', 'system')` | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2418ef · [권고] U4 는 두 툴 + D1 검사 + D6 + 별칭 upsert(미결 7) + 사실 upsert(결정 6) + 임베딩 채우기 — 단위 중 가장 크다. 커밋 하나로 두되 03-log 에 소단계(별칭 보조 → create → update)를 나눠 적고, D6 에서 update_person(display_name=X) 시 X 를 별칭으로도 누적하는지(D5 '새 별칭 확정 시 즉시 임베딩') U4 착수 전에 정한다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  U4 는 두 툴 + D1 검사 + D6 + 별칭 upsert(미결 7) + 사실 upsert(결정 6) + 임베딩 채우기 — 단위 중 가장 크다. 커밋 하나로 두되 03-log 에 소단계(별칭 보조 → create → update)를 나눠 적고, D6 에서 update_person(display_name=X) 시 X 를 별칭으로도 누적하는지(D5 '새 별칭 확정 시 즉시 임베딩') U4 착수 전에 정한다
```

### 원인 분석
- 가설: U4(97행)는 `create_person`·`update_person` 두 툴에 D1 DB 검사·D6 확인 요건·별칭 upsert(미결 7)·사실 upsert(결정 6)·임베딩 채우기(D5)를 모두 담는다. 또 D06 '`display_name` = 가장 최근 호칭, 이전 호칭은 `person_aliases` 에' 에 대해 update_person(display_name=X) 시 X 자체를 별칭으로 누적하는지 계획이 말하지 않는다(create_person 은 결정 5 로 `system` 별칭 자동 생성이 명시됨).
- 확인 방법(명령): `grep -nE 'display_name' docs/wiki/packages/P2-tools/01-plan.md | grep -nE 'U4|미결 6'`
- 확인 결과: 97행·157행 — 확인 요건만 있고 새 표시 이름의 별칭 누적 여부 없음. D05 '새 별칭이 확정되면 즉시 임베딩' 과 S3.3 4단계 '연결(update_person 별칭 누적)' 에 비추어 X 를 `confirmed` 별칭으로 upsert 하는 쪽이 정합. U4 착수 시 03-log 에 결정 기록.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U4 구현 결정: `update_person(display_name=X)` 확인 통과 시 `X` 를 (D05 가 제안한 `confirmed` 가 아니라) **`system`** 별칭으로 upsert — `create_person` 의 "display_name → system 별칭" 규칙과 대칭을 맞춘다(둘 다 "그 순간의 표시 이름"이라는 같은 의미의 파생 별칭이며, `confirmed` 는 사용자가 개별 확인한 *호칭*(`aliases[]`/`new_alias`) 전용으로 남긴다). 이전 표시 이름의 별칭 행은 지우지 않는다(D6). `app/tools/persons.py` `update_person` 구현 | `POSTGRES_PORT=5433 python -m pytest tests/test_tools_persons.py -q -k "display_name_with_confirmation"` | 1 passed — 새 이름이 별칭에 존재, 이전 이름 별칭 유지(행 삭제 0) | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/): `docs/wiki/packages/P2-tools/evidence/20260905-1620-pytest-u4.txt`(105 passed 안에 포함)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(D06 "별칭은 절대 삭제하지 않는다" 그대로 유지) | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-4d2507 · [권고] security.md §5 'DELETE /persons/{id}' 는 backlog 어느 항목에도 없다(grep 0건) — P2 제외는 사용자 결정이나 갈 곳이 없다. architect 가 backlog 에 항목(P5-loop 묶음 또는 별도)을 세운다. 미결 8 의 JSONB 참조 정리 요건을 그 항목에 옮긴다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  security.md §5 'DELETE /persons/{id}' 는 backlog 어느 항목에도 없다(grep 0건) — P2 제외는 사용자 결정이나 갈 곳이 없다. architect 가 backlog 에 항목(P5-loop 묶음 또는 별도)을 세운다. 미결 8 의 JSONB 참조 정리 요건을 그 항목에 옮긴다
```

### 원인 분석
- 가설: security.md §5 첫 항목 '인물 단위 완전 삭제 API' 가 `docs/backlog.md` 어느 패키지 수용 기준에도 없다. 01-plan 미결 8 은 '사용자 결정 필요(P5 묶음 / 별도 항목)' 로 남겼고 journal 16:40 결정은 'P2 제외·미결 인계' 까지만 정했다 — 인계받을 항목이 없다.
- 확인 방법(명령): `grep -nE 'DELETE|delete_person|완전 삭제' docs/backlog.md docs/wiki/INDEX.md`
- 확인 결과: 0건. architect 가 backlog 에 항목을 세우고(P5-loop 엔드포인트 묶음 또는 별도), P1 04-review §7 의 JSONB 참조 정리 요건과 01-plan 미결 8 을 그 항목으로 옮긴다. P2 계획 통과를 막지 않음.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-107a50 · [권고] CLAUDE.md 표의 반환형(Person/Event/Schedule/Briefing/PendingQuestion)과 계획의 반환형(PersonOut 등)이 이름이 다르다 — tools_check 는 매개변수만 대조하므로 수용 기준 판정에는 영향 없음. 04-review 는 tools_check 출력에 실제 시그니처가 ctx 포함 그대로 찍혀 있을 것(예: actual=(ctx, query, hints=None))을 요구한다 — ctx 편차가 기록에 남아야 한다
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  CLAUDE.md 표의 반환형(Person/Event/Schedule/Briefing/PendingQuestion)과 계획의 반환형(PersonOut 등)이 이름이 다르다 — tools_check 는 매개변수만 대조하므로 수용 기준 판정에는 영향 없음. 04-review 는 tools_check 출력에 실제 시그니처가 ctx 포함 그대로 찍혀 있을 것(예: actual=(ctx, query, hints=None))을 요구한다 — ctx 편차가 기록에 남아야 한다
```

### 원인 분석
- 가설: CLAUDE.md 표는 언어 중립 의사 시그니처(`str[]`, `?`, `→ Person`)이고 계획은 `PersonOut` 등 DTO 를 돌려준다. `scripts/tools_check.py` 는 매개변수(이름·순서·옵션)만 대조하므로 반환형 이름 차이는 판정에 들어가지 않는다. 유일한 편차 `ctx` 는 결정 2 가 기계 검사로 강제하지만, 판정 표(113행) 기대 출력 예 `[ok] search_person(query, hints=None)` 에는 `ctx` 가 이미 제거돼 있어 출력만 보면 편차가 보이지 않는다.
- 확인 방법(명령): `grep -n 'inspect.signature' docs/wiki/packages/P2-tools/01-plan.md`
- 확인 결과: 40행·77행·113행·133행. 133행 '첫 매개변수가 정확히 `ctx` 이고 그 뒤가 … 같은지' 규약 존재 → 수용 기준 훼손 아님(통과). 04-review 는 tools_check 출력에 `expected`(CLAUDE.md)와 `actual`(ctx 포함 원형) 두 값이 함께 찍힌 것을 증거로 요구한다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P2-tools` (계획 단계면 `verify-plan.sh P2-tools`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

