# P0-compose · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-03 22:00 · docs(P0-compose): 계획·계획검증 승인, 패키지 착수 · 23d8700
- 변경: packages/P0-compose/01-plan.md(architect 초안 → 보류 소견 F-033bb1·F-0ffff5 반영 개정), 02-plan-verify.md(verifier 2회: 보류 → 통과, FAIL 0/WARN 1, 승인: 사용자 2026-09-03), 05-remediation.md(계획 단계 해소, 구현 단계 대기), evidence/(verify-plan 1·2·final, remediation-check-2), 03-log 신설. CURRENT active: P0-compose. journal START.
- 이유(기획서·카드 연결): resolution-plan §4 착수 준비 "로컬 docker-compose (pgvector)". backlog P1 "의존: 착수 준비(D4 차원 확정, docker-compose)". D04 확정 N=1536 을 받을 DB 를 로컬에 준비한다.
- 정합성 확인: 원칙7(제외 범위 무관) / D4 D5 / S3.1(테이블은 만들지 않음) / 보안 §1(예시값만, 실제 값은 .env) §4(볼륨 삭제 금지) — 위반 없음 (02-plan-verify 점검표, 검증자 verifier)
- 남은 것 · 다음 단위: U1 .env.example 이름 4개 + docker-compose.yml + docker/initdb (backend-agent, sonnet). 미결 2(psycopg vs db_check.sh)는 U2 에서 결정해 여기 기록.
- Refs: P0-compose D4 D5 S3.1 F-033bb1 F-0ffff5

## 2026-09-04 · feat(P0-compose): U1 로컬 pgvector compose — .env.example 이름 4개·compose·initdb · 749bb8e
- 변경: .env.example(POSTGRES_USER/PASSWORD/DB/PORT 이름 4개 + DATABASE_URL 동일값 주석), docker-compose.yml(pgvector/pgvector:pg16, `${VAR:-기본값}`, `${POSTGRES_PORT:-5432}:5432`, 볼륨 pgdata, initdb 읽기전용 마운트, pg_isready healthcheck), docker/initdb/01-vector.sql(CREATE EXTENSION vector), evidence/20260903-compose-config·up·ps·vector-ext.txt. 구현: backend-agent(sonnet), 2026-09-03 세션. 01-plan U1 체크.
- 이유(기획서·카드 연결): resolution-plan §4 착수 준비 "로컬 docker-compose (pgvector)". D04 N=1536 을 받을 pgvector 확장을 로컬에 준비. F-033bb1 결정 (a): 값의 단일 출처 .env, .env.example 은 이름·예시값만.
- 정합성 확인: 원칙7 / D4 D5 / S3.1(확장만, 테이블은 P1-schema) / 보안 §1(예시값만, .env 미접촉) §4(볼륨 삭제 옵션 없음) — 위반 없음
- 남은 것 · 다음 단위: U2 scripts/db_check.py(psycopg 우선, 대안 compose exec psql — 결정을 여기 기록) + `SELECT '[1,2,3]'::vector` evidence. Docker 데몬은 2026-09-04 세션 시작 시 꺼져 있었음 — U2 전 사용자에게 실행 요청. 미결 1(pg16 태그 고정)은 U3 README·registry 비고에 메모.
- Refs: P0-compose D4 D5 S3.1 F-033bb1

## 2026-09-04 · feat(P0-compose): U2 db_check.py — pgvector 접속 검사·테스트·실행 증거 · 0ee6e25
- 변경: scripts/db_check.py(psycopg v3, DATABASE_URL 우선·없으면 POSTGRES_* → compose 기본값, 불일치 시 변수 이름만 경고, CREATE EXTENSION → extversion → `SELECT '[1,2,3]'::vector`, rc 0/1/2), tests/test_db_check.py(DB 없이 6건: 조립·기본값·불일치 경고에 비밀번호 값 부재), evidence/20260904-compose-up·compose-ps(healthy)·db-check(`[1,2,3]`, exit 0)·pip-psycopg(3.3.5)·pytest-db-check(6 passed). 01-plan U2 체크. 구현: backend-agent(sonnet).
- 이유(기획서·카드 연결): 01-plan U2 행 그대로. 수용 기준 "`SELECT '[1,2,3]'::vector` 성공"을 재현 가능한 스크립트와 출력 파일로 남긴다(원칙8). F-033bb1 결정 (a)의 두 번째 장치(불일치 경고) 구현.
- 정합성 확인: 원칙8(재현) / D4 D5 / S3.1(테이블 없음) / 보안 §1(접속 문자열·비밀번호 미출력, 키워드 인자 접속 — URL 조립은 secret-guard 오탐으로 막혀 채택 안 함) §4(볼륨 삭제 없음) — 위반 없음
- **미결 2 결정**: psycopg[binary] 채택(사용자 site 에 설치 정상, 백엔드도 psycopg 사용 예정). db_check.sh 대안은 만들지 않음. requirements 파일은 P1/P2 백엔드 골격에서 추가.
- **발견(리스크 "5432 포트 충돌" 현실화)**: 이 프로젝트와 무관한 로컬 컨테이너(finance_postgres)가 5432 점유 → 에이전트가 .env 를 건드리지 않고 셸 변수 `POSTGRES_PORT=5433` 을 up·db_check 앞에 1회성으로 붙여 실행(evidence ps 의 5433 매핑이 그 흔적). **영구 해결은 사용자 몫**: .env 의 POSTGRES_PORT 와 DATABASE_URL 포트를 같이 5433 으로 바꾸거나 무관 컨테이너 정리. U3 README 로컬 DB 절에 이 안내를 넣는다.
- 남은 것 · 다음 단위: U3 README "로컬에서 해 보기" 로컬 DB 절 + registry(기존 README 행 비고 갱신, compose·initdb·db_check 행 추가) → verifier 04-review.
- Refs: P0-compose D4 D5 S3.1 F-033bb1

## 2026-09-04 · docs(P0-compose): U3 README 로컬 DB 절·registry 반영, verify-impl 사전 실행 · 7397966
- 변경: README.md("로컬에서 해 보기" 예약 문장 → 로컬 DB 소절: 사전 조건·up/ps/db_check/down·볼륨 삭제 금지·5432 충돌 시 POSTGRES_PORT 와 DATABASE_URL 포트 동시 변경·pg16 태그 P9-infra 재확인·P1-schema 선행 조건; 진행 상태 표 P0 행 "구현 완료 · 검증 대기"), registry.md(README 행 비고 갱신 — 새 행 아님; docker-compose.yml·docker/initdb/01-vector.sql·scripts/db_check.py 행 3개 추가, 소유 P0-compose), 01-plan U3 체크, evidence/20260904-verify-impl-pre.txt + 20260904-1233-{pytest,lint,commits,summary}.txt. 구현: backend-agent(sonnet).
- 이유(기획서·카드 연결): 01-plan U3 행·F-0ffff5(README 로컬 DB 절 + registry 기존 README 행 비고 갱신, 새 행 금지). U2 발견(5432 충돌)과 미결 1(pg16 태그)을 사용자 안내로 닫는다.
- 정합성 확인: 원칙7 / D4 D5 / S3.1 / 보안 §4(README 에 볼륨 삭제 옵션 문자열을 적지 않고 풀어 씀) — 위반 없음. verify-impl 사전 실행: PASS 8 / WARN 1(04-review 없음, 검토 전 정상) / FAIL 0.
- 남은 것 · 다음 단위: 구현 단위 U1~U3 모두 완료. verifier(fable) 04-review(수용 기준 `SELECT '[1,2,3]'::vector` 성공 ↔ evidence/20260904-db-check.txt 대조, 코드 리뷰) → `/devlog done` → 푸시 → L-003.
- Refs: P0-compose D4 D5 S3.1 F-0ffff5
