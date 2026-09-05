# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-05 12:50 (P1-schema U1 구현 완료, 커밋 직전)
active: **P1-schema** | frozen: none | 브랜치: dev (dev = origin/dev = **main = 819e1ac**). 착수 커밋 9397066(로컬, 미푸시). 미커밋: U1 산출물(app/, requirements*, tests/conftest·test_config, db_check 리팩터, .env.example POSTGRES_HOST) + 위키 — U1 커밋으로 정리 중

## 지금 어디까지
- **P1-schema 착수 진행 중(2026-09-05)**: 사용자 "P1-schema 시작해줘" → 선행 확인(P0-embed-pilot·P0-compose 04-review 완료, R8 R9, registry 중복 없음) → `--stage architect` → architect(opus) 01-plan 초안(U1 골격·requirements / U2 모델 9개+테스트 / U3 Alembic 0001 / U4 schema_check+왕복 evidence / U5 registry·README·db_check version()) → verify-plan 1차 FAIL 4/WARN 4 → 수용 기준 절의 판정 방법 불릿 3개를 `## 판정 방법` 절로 분리(구조만) → 2차 FAIL 1(02-plan-verify 부재)/WARN 4(README·db_check 기존 행, 의도) → 05-remediation 소견 7건 원인·조치 기입 → `--stage verifier` → verifier 02-plan-verify **통과**(FAIL 0/WARN 4 의도, 점검표 8행, 권고 4건 F-ace4dd 접속조립 단일구현 / F-081752 expired 파생은 P2 / F-08e812 NOT NULL 정책 U2 / F-75c1c1 POSTGRES_HOST U5) → **사용자 계획 승인(2026-09-05)** → active: P1-schema.
- **P0-compose 완료(2026-09-05)** — verifier(fable) 04-review `결과: 완료`, 사용자 승인. verify-impl PASS 10/WARN 0/FAIL 0 (`evidence/20260905-1127-verify-impl.txt`). 부정 케이스 5종을 verifier 가 직접 실행(`evidence/20260905-1121-review-{compose,db-check,mutation,pytest,static}.txt`). 소견 F-033bb1·F-0ffff5 해소, 열린 소견 0. 닫는 R 없음.
- 이번 세션 커밋: 7d20a34(위키 정리), 819e1ac(P0-compose 완료). 2026-09-05 dev 푸시 → 사용자 승격 결정 → main = 819e1ac.
- 04-review §6 관찰 O1~O7 은 조치 없이 기록(P1-schema 인계): db_check.py 서버 버전 미출력(`SELECT version()` 권고), `POSTGRES_HOST` 이름이 .env.example 에 없음, tests/test_db_check.py registry 독립 행 없음, evidence 에 compose config 해석값(예시값) 포함 → 앞으로 `--quiet`, 5432 영구 해결은 사용자 몫.
- **P1-schema 인계(04-review §7)**: 이름 4개 + `DATABASE_URL` 동일값, compose 기본값 = `.env.example` 예시값; `vector` 0.8.6 / `pgvector/pgvector:pg16`; `person_aliases.embedding vector(1536)` 은 Alembic 으로(initdb 에 SQL 추가 금지); 볼륨 삭제는 사용자만; pg16↔RDS 메이저는 P9-infra 재확인; 의존성 선언 파일 없음(`psycopg[binary]` 3.3.5 가 첫 항목).
- .env.example 은 추적 유지 확정(2026-09-04). 다시 꺼내지 않는다.
- Docker: 컨테이너 capstone2-postgres-1 은 **호스트 5433**(5432 는 무관한 finance_postgres). 셸 변수 없이 `docker compose up -d` 하면 충돌 — README 로컬 DB 절 안내대로 .env 포트를 바꾸거나 무관 컨테이너 정리(사용자 몫).
- 팀 밑작업(Agent Teams): 사용자 결정 **보류**.

## 바로 다음에 할 것 (순서대로)
1. (완료) 착수 커밋 9397066. **U1 구현 완료(backend-agent, 2026-09-05)**: requirements.txt(SQLAlchemy 2.0.50·alembic 1.19.2·psycopg[binary] 3.3.5·pgvector 0.5.0)·requirements-dev(pytest 9.0.3), app/config.py(접속 조립 단일 구현 — F-ace4dd, POSTGRES_HOST 선택 — F-75c1c1, sqlalchemy_url), app/db/base.py(Base+naming_convention), db_check.py 는 app.config import·re-export(기존 테스트 6건 무수정), tests/test_config.py 5건. pytest 21 passed, db_check 5433 재현 exit 0. evidence 20260905-1239/1242/1243-*. 03-log U1 항목·01-plan U1 [x]. → `/commit` 진행 중.
2. U2(사용자 승인 → `--stage backend-agent`): app/db/models.py 모델 9개(S3.1 컬럼 1:1, CHECK 4종, FK CASCADE 6, fact_sources 복합 PK, Vector(1536) nullable, 인덱스 9종 + 부분 인덱스, JSONB·timestamptz·IDENTITY, NOT NULL 정책 결정 F-08e812) + tests/test_schema_models.py(DB 없이 메타데이터 검사) → `/commit`. 이후 U3 → U4 → U5. 단위마다 `/commit`, 마이그레이션·schema_check 파일은 Write 도구로(Bash heredoc 에 DROP 문자열 금지).

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P1-schema/01-plan.md`(작업 단위·판정 방법·리스크), `02-plan-verify.md` §3, `05-remediation.md` 권고 4건, `packages/P0-compose/04-review.md` §7(인계)
- `lessons/L-001-dev-branch.md`, `L-002-role-model-separation.md`, `L-003-stop-after-dev-push.md`, `L-004`(위임 게이트)

## 열린 질문 · 사용자 결정 대기
- U1 커밋 승인 → U2 시작 승인(L-004). P0-cost(eval-agent) 착수 시점 — P1 과 병행할지 사용자 결정.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). 메인 세션이 직접 쓰면 verify-plan/impl 이 FAIL.
- **위임은 묻고 시작**(L-004): architect/backend-agent/eval-agent/verifier 는 AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 마커 없으면 delegate-guard 가 거부.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` 이 생기면 승격/수정을 묻고 멈춘다(L-003). 승격은 `approve-commit.sh --release` → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다. 정리 훅은 PostToolUse.
- Bash 명령 문자열에 훅 금지 문구(볼륨을 지우는 compose 옵션, 강제 푸시 옵션, DROP)가 **텍스트로라도** 들어가면 차단된다. 그런 문구가 든 문서는 Write 도구로 쓴다.
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 스크립트가 키 부재를 스스로 보고하게 한다.
- registry 에 README 행이 이미 있다(하네스 소유). 새 행을 만들지 말고 비고만 갱신한다. db_check.py 행(P0-compose 소유)도 같다.
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 를 붙여 실행(콘솔 cp949 에서 출력 중 UnicodeEncodeError — 파일은 써진 뒤라 결과는 유효). verify-plan.sh 의 `## 수용 기준` 절에는 backlog 문장 불릿만 둔다(설명 불릿은 FAIL).
