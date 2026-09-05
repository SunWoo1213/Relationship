# P1-schema · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-05 12:27 | 출처: review | 열림: 7 (필수 0) | 해소: 4

## F-b3534b · [필수] 없음: docs/wiki/packages/P1-schema/02-plan-verify.md
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P1-schema/02-plan-verify.md
```

### 원인 분석
- 가설: 02-plan-verify.md 는 verifier(fable)가 쓰는 문서(L-002). 계획 초안 직후 기계 검증에서는 항상 없다 — 절차상 정상.
- 확인 방법(명령): `ls docs/wiki/packages/P1-schema/`
- 확인 결과: 01-plan.md·05-remediation.md·evidence/ 만 존재(2026-09-05 12:18)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | verifier 위임(사용자 승인 + `--stage verifier`) → `02-plan-verify.md` 작성(검증자: verifier (fable), 점검표 8행) | `bash .claude/scripts/verify-plan.sh P1-schema` | `PASS  존재: …02-plan-verify.md`, `PASS  검증자: verifier` | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): (verifier 실행 후 <ts>-verify-plan-3.txt)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2e151b · [필수] backlog 에 같은 문장이 없다: **DB 없이 도는 테스트**(`pytest tests/test_config.py
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: **DB 없이 도는 테스트**(`pytest tests/test_config.py
```

### 원인 분석
- 가설: architect 가 "## 수용 기준" 절 아래에 판정 방법 설명 불릿 3개를 두었다. verify-plan.sh 4번은 그 절의 `- ` 불릿 전부를 backlog 와 글자 그대로 대조하므로 설명 불릿이 FAIL 로 잡혔다. 수용 기준 문장 자체("9개 테이블 생성, `events.type` 제약 존재")는 PASS.
- 확인 방법(명령): `awk '/^## 수용 기준/,/^## 리스크/' 01-plan.md` 로 절 내용 확인
- 확인 결과: 불릿 4개 중 1개만 backlog 문장, 3개는 판정 방법 설명

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan.md: 판정 방법 문단·표·불릿 3개를 새 절 `## 판정 방법` 으로 분리(내용 변경 없음, 메인 세션이 구조만 수정) | `bash .claude/scripts/verify-plan.sh P1-schema` | 해당 FAIL 줄 없음, `PASS  backlog 일치` 1줄만 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): 20260905-1218-2-verify-plan.txt (FAIL 1 = 02-plan-verify 부재만)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2412b4 · [필수] backlog 에 같은 문장이 없다: **DB 가 필요한 검증**: 위 표의 `alembic`·`pg_const
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: **DB 가 필요한 검증**: 위 표의 `alembic`·`pg_const
```

### 원인 분석
- 가설: architect 가 "## 수용 기준" 절 아래에 판정 방법 설명 불릿 3개를 두었다. verify-plan.sh 4번은 그 절의 `- ` 불릿 전부를 backlog 와 글자 그대로 대조하므로 설명 불릿이 FAIL 로 잡혔다. 수용 기준 문장 자체("9개 테이블 생성, `events.type` 제약 존재")는 PASS.
- 확인 방법(명령): `awk '/^## 수용 기준/,/^## 리스크/' 01-plan.md` 로 절 내용 확인
- 확인 결과: 불릿 4개 중 1개만 backlog 문장, 3개는 판정 방법 설명

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan.md: 판정 방법 문단·표·불릿 3개를 새 절 `## 판정 방법` 으로 분리(내용 변경 없음, 메인 세션이 구조만 수정) | `bash .claude/scripts/verify-plan.sh P1-schema` | 해당 FAIL 줄 없음, `PASS  backlog 일치` 1줄만 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): 20260905-1218-2-verify-plan.txt (FAIL 1 = 02-plan-verify 부재만)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-f3e40d · [필수] backlog 에 같은 문장이 없다: 증거 경로: `docs/wiki/packages/P1-schema/evidence/`.
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  backlog 에 같은 문장이 없다: 증거 경로: `docs/wiki/packages/P1-schema/evidence/`.
```

### 원인 분석
- 가설: architect 가 "## 수용 기준" 절 아래에 판정 방법 설명 불릿 3개를 두었다. verify-plan.sh 4번은 그 절의 `- ` 불릿 전부를 backlog 와 글자 그대로 대조하므로 설명 불릿이 FAIL 로 잡혔다. 수용 기준 문장 자체("9개 테이블 생성, `events.type` 제약 존재")는 PASS.
- 확인 방법(명령): `awk '/^## 수용 기준/,/^## 리스크/' 01-plan.md` 로 절 내용 확인
- 확인 결과: 불릿 4개 중 1개만 backlog 문장, 3개는 판정 방법 설명

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan.md: 판정 방법 문단·표·불릿 3개를 새 절 `## 판정 방법` 으로 분리(내용 변경 없음, 메인 세션이 구조만 수정) | `bash .claude/scripts/verify-plan.sh P1-schema` | 해당 FAIL 줄 없음, `PASS  backlog 일치` 1줄만 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): 20260905-1218-2-verify-plan.txt (FAIL 1 = 02-plan-verify 부재만)

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
- 가설: README.md 는 하네스 소유 registry 행이 이미 있다. 계획 U5 는 새 행을 만들지 않고 진행 표 P1 행·마이그레이션 절을 갱신하며 registry 는 기존 행 비고만 갱신한다(P0-compose 와 같은 처리). 의도된 WARN.
- 확인 방법(명령): `grep -n README docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(하네스 소유, 비고에 P0-compose 갱신 이력)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — U5 에서 기존 행 비고 갱신, 새 행 금지(04-review §5 에서 확인) | `grep -c "README" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U5) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): U5 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-c57789 · [권고] registry 에 다른 패키지로 이미 있음: db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
```

### 원인 분석
- 가설: scripts/db_check.py 는 P0-compose 소유 registry 행이 있다. 계획 U5 는 O1 관찰(서버 버전 미출력)에 따라 `SELECT version()` 한 줄만 추가하고 registry 는 기존 행 비고에 "P1-schema: version() 추가" 를 적는다. 새 행 없음. 의도된 WARN.
- 확인 방법(명령): `grep -n db_check docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P0-compose)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — U5 에서 기존 행 비고 갱신, 새 행 금지 | `grep -c "db_check" docs/wiki/registry.md` | 행 수 불변 | 대기(U5) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): U5 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-8c9c5b · [권고] registry 에 다른 패키지로 이미 있음: scripts/db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: scripts/db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
```

### 원인 분석
- 가설: scripts/db_check.py 는 P0-compose 소유 registry 행이 있다. 계획 U5 는 O1 관찰(서버 버전 미출력)에 따라 `SELECT version()` 한 줄만 추가하고 registry 는 기존 행 비고에 "P1-schema: version() 추가" 를 적는다. 새 행 없음. 의도된 WARN.
- 확인 방법(명령): `grep -n db_check docs/wiki/registry.md`
- 확인 결과: 기존 행 1개(소유 P0-compose)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — U5 에서 기존 행 비고 갱신, 새 행 금지 | `grep -c "db_check" docs/wiki/registry.md` | 행 수 불변 | 대기(U5) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): U5 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-ace4dd · [권고] 접속 해석 규칙 이중 구현 위험: app/config.py 와 scripts/db_check.py resolve_connection() — 재사용/재구현 미결정 (01-plan 16행, CLAUDE.md 중복 구현 금지, P0-compose 04-review O5)
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  접속 해석 규칙 이중 구현 위험: app/config.py 와 scripts/db_check.py resolve_connection() — 재사용/재구현 미결정 (01-plan 16행, CLAUDE.md 중복 구현 금지, P0-compose 04-review O5)
```

### 원인 분석
- 가설: 01-plan 16행은 `app/config.py` 가 `db_check.resolve_connection()` 과 "같은 우선순위·같은 변수 이름" 이라고만 적고 재사용/재구현을 정하지 않았다. 재구현이면 같은 규칙이 두 파일에 존재(CLAUDE.md registry 중복 구현 금지). P0-compose 04-review §6 O5 는 "P1/P2 에서 DB 설정 모듈로 흡수될 때 정리" 를 예상했다.
- 확인 방법(명령): `grep -n "DATABASE_URL\|POSTGRES_" scripts/db_check.py app/config.py` (구현 후)
- 확인 결과: 계획 단계 — 01-plan 16·45행, scripts/db_check.py 100~136행(resolve_connection 존재) 확인. 해결은 구현 에이전트: U1 에서 app/config.py 를 단일 구현으로 두고 U5 의 db_check.py 수정 시 import 하거나, 둘을 유지하는 이유를 03-log 에 기록

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `app/config.py` 신설 — `ConnInfo`/`parse_database_url`/`resolve_connection`/`ConnInfo.sqlalchemy_url()`/`sqlalchemy_url()` 을 여기로 옮김(우선순위·변수 이름·경고 문구는 기존 `scripts/db_check.py` 와 동일하게 이동) | `python -c "import app.config"` | 예외 없음 | 완료 |
| 2 | `scripts/db_check.py` 에서 자체 정의(`ConnInfo`·`parse_database_url`·`resolve_connection` 등) 삭제, `from app.config import (...)` 로 대체 + re-export(`__all__`), 스크립트 단독 실행 시 저장소 루트를 `sys.path` 에 넣는 줄 추가 | `grep -n "DATABASE_URL\|POSTGRES_" scripts/db_check.py app/config.py` | `scripts/db_check.py` 는 docstring 설명 줄만 남고 실제 조립 로직(`env.get("POSTGRES_...")` 등)은 `app/config.py` 에만 존재 | 완료 |
| 3 | 회귀 확인 — 기존 `tests/test_db_check.py`(6건, 지금 이름 `db_check.resolve_connection` 등 그대로) 계속 통과 | `python -m pytest tests/test_config.py tests/test_db_check.py -q` | `11 passed` | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): 20260905-1243-remediation-f-ace4dd-f-75c1c1.txt(grep 출력), 20260905-1242-pytest-u1.txt(11 passed)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-081752 · [권고] pending_questions status 파생 규칙 불완전: S3.4 status=expired 는 answered_at IS NULL 외에 created_at 필요 (01-plan 116행) — 스키마 변경 불필요, P2-tools 인계
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  pending_questions status 파생 규칙 불완전: S3.4 status=expired 는 answered_at IS NULL 외에 created_at 필요 (01-plan 116행) — 스키마 변경 불필요, P2-tools 인계
```

### 원인 분석
- 가설: `specs/S3.4-ask-user-protocol.md` "미답변 24시간 후 만료(`answered_at` null 유지, status=expired)" — pending 과 expired 는 둘 다 `answered_at IS NULL` 이라 `created_at` 기준 24h 조건이 추가로 필요. 01-plan 116행 서술은 pending/answered 만 다룬다. S3.1 에 `status` 컬럼이 없으므로 스키마는 계획대로(컬럼 추가 없음)가 맞다.
- 확인 방법(명령): `grep -n "status" docs/wiki/specs/S3.1-schema-v2.md docs/wiki/specs/S3.4-ask-user-protocol.md`
- 확인 결과: S3.1 에 status 없음(0건), S3.4 11행 status=expired 1건. 스키마 변경 불필요. P2-tools 계획(01-plan)에 파생 규칙 명시를 인계 — 이 패키지에서는 04-review §7 인계 항목으로 기록하면 해소

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-08e812 · [권고] NULL 허용 정책이 타임스탬프 계열에만 명시 (01-plan 114행) — U2 결정을 03-log·tests/test_schema_models.py 에 남길 것
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  NULL 허용 정책이 타임스탬프 계열에만 명시 (01-plan 114행) — U2 결정을 03-log·tests/test_schema_models.py 에 남길 것
```

### 원인 분석
- 가설: 01-plan 114행은 `occurred_at`·`scheduled_at` NOT NULL, `briefed_at`·`confirmed_at`·`answer`·`answered_at`·`embedding` nullable 만 정한다. 나머지 문자열·JSONB 컬럼의 NOT NULL 여부는 계획에도 S3.1 에도 없어 구현자 재량이 된다.
- 확인 방법(명령): `grep -n "nullable" app/db/models.py` (구현 후)
- 확인 결과: 계획 단계 — 01-plan 114행 확인. 계획 결함이 아니라 명세 공백. U2 구현 시 결정을 03-log 에 적고 tests/test_schema_models.py 에 nullable 검사를 포함하면 해소

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `app/db/models.py` 모듈 docstring 에 NOT NULL 정책 규칙 명문화: 식별자·FK·툴 시그니처(S3.2) 필수 인자에 대응하는 컬럼은 NOT NULL, 비동기로 나중에 채워지는 컬럼만 nullable(`embedding, confirmed_at, briefed_at, answer, answered_at`) | `grep -n "NOT NULL 정책" app/db/models.py` | docstring 절 존재 | 완료 |
| 2 | `tests/test_schema_models.py::test_nullable_columns_are_exactly_the_five_deferred_fields` — nullable 컬럼 집합이 정확히 5개뿐임을 전수 검사 | `python -m pytest tests/test_schema_models.py -q -k nullable_columns_are_exactly` | `1 passed` | 완료 |
| 3 | `tests/test_schema_models.py::test_not_null_columns_cover_all_tool_signature_required_arguments` — S3.2 필수 인자(`add_event`/`add_schedule`/`ask_user`)에 대응하는 컬럼이 NOT NULL 인지 검사 | `python -m pytest tests/test_schema_models.py -q -k not_null_columns_cover` | `1 passed` | 완료 |

결정 근거: S3.2 툴 시그니처의 필수 인자(`add_event(person_id, type, content, occurred_at, raw_utterance)`, `add_schedule(person_id, title, scheduled_at)`, `ask_user(kind, question, options, context)`)는 호출 시점에 값이 반드시 있으므로 대응 컬럼을 NOT NULL 로 강제해 스키마가 잘못된 호출을 조기에 잡는다. 반대로 `embedding`(별칭 확정 전)·`confirmed_at`(별칭 검증 전)·`briefed_at`(브리핑 전)·`answer`/`answered_at`(답변 전)는 정상적으로 값이 없는 상태가 존재하므로 nullable 로 둔다.

### 재검증
- 명령: `python -m pytest tests/test_schema_models.py -q`
- 결과 파일(evidence/): `docs/wiki/packages/P1-schema/evidence/20260905-1253-pytest-u2-models.txt`(17 passed, nullable/NOT NULL 검사 포함), `docs/wiki/packages/P1-schema/evidence/20260905-1253-pytest-u2-all.txt`(38 passed)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-75c1c1 · [권고] POSTGRES_HOST(P0-compose O5) 처리 미결정 — app/config.py 가 읽으면 .env.example 에 이름 추가, 아니면 db_check.py 132행 정리 여부를 03-log 에
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  POSTGRES_HOST(P0-compose O5) 처리 미결정 — app/config.py 가 읽으면 .env.example 에 이름 추가, 아니면 db_check.py 132행 정리 여부를 03-log 에
```

### 원인 분석
- 가설: P0-compose 04-review §6 O5: `scripts/db_check.py` 132행이 `.env.example` 에 없는 `POSTGRES_HOST` 를 읽는다. 01-plan 16행은 "호스트 기본값 `localhost`" 만 적고 `POSTGRES_HOST` 를 읽을지 말지 정하지 않았다.
- 확인 방법(명령): `grep -n "POSTGRES_HOST" .env.example scripts/db_check.py app/config.py` (구현 후)
- 확인 결과: 계획 단계 — .env.example 에 POSTGRES_HOST 없음(16~19행은 USER/PASSWORD/DB/PORT), db_check.py 132행에 있음. U1/U5 에서 한쪽으로 통일하고 03-log 에 기록하면 해소

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `.env.example` POSTGRES_* 절에 `POSTGRES_HOST=localhost` 한 줄 + "선택. 컨테이너 밖에서 접속할 때만 바꾼다" 주석 추가(이름·기본값만, 비밀 아님). `app/config.py`(단일 구현)가 `env.get("POSTGRES_HOST", DEFAULT_HOST)` 로 계속 읽음 — `scripts/db_check.py` 쪽 자체 구현은 F-ace4dd 해결로 이미 삭제됨(재구현 없음) | `grep -n "POSTGRES_HOST" .env.example app/config.py` | `.env.example:20:POSTGRES_HOST=localhost`, `app/config.py` 에 `env.get("POSTGRES_HOST", DEFAULT_HOST)` 1건 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-schema` (계획 단계면 `verify-plan.sh P1-schema`)
- 결과 파일(evidence/): 20260905-1243-remediation-f-ace4dd-f-75c1c1.txt

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

