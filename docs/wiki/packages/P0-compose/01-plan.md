# P0-compose · 계획 (01-plan)

상태: 초안(F-033bb1·F-0ffff5 반영 개정) | 담당: architect(계획) / backend-agent(구현) / verifier(검증) — 승인·커밋은 메인 세션 | 작성: 2026-09-03
태그 — 패키지: P0-compose · 닫는 검증: 없음(`docs/wiki/INDEX.md` 패키지 id 표의 "닫는 R" 칸이 `—`) · 기대는 결정: D4 D5 · 구현하는 명세: S3.1 · 관련 원칙: 없음
의존: 없음 (착수 준비 항목. 선행 패키지 없음. P4 게이트 해당 없음)

## 목표
`docs/resolution-plan.md` §4 착수 준비 표의 "로컬 docker-compose (pgvector) | backend-agent | `docker-compose.yml` | `SELECT '[1,2,3]'::vector` 성공" 한 줄을 실현한다. 로컬 개발용 PostgreSQL + pgvector를 `docker compose`로 띄우고, `.env`의 `DATABASE_URL`로 접속해 `CREATE EXTENSION IF NOT EXISTS vector` 후 `SELECT '[1,2,3]'::vector`가 성공하는 것을 실행 출력으로 남긴다. D4가 확정한 차원(`text-embedding-3-small`, N=1536)과 D5(임베딩은 별칭 단위로 `person_aliases.embedding`에 둔다)를 담을 자리가 S3.1의 `vector(1536)` 컬럼이므로, 그 컬럼을 만들 P1-schema(Alembic)의 선행 조건이 이 패키지다. 이 패키지는 **DB 엔진과 확장까지만** 준비하고 테이블은 만들지 않는다.

## 범위
- 포함:
  - `.env.example` — DB 절에 이름 4개 추가: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`. 값은 이미 있는 `DATABASE_URL=postgresql://app:pass@localhost:5432/relationship`과 같은 예시값(`app` / `pass` / `relationship` / `5432`)을 적고, "이 4개는 `DATABASE_URL`과 같은 값이어야 한다. 실제 비밀번호는 `.env`에만 넣는다"는 주석을 붙인다. 에이전트는 `.env`를 읽지도 쓰지도 않는다(security.md §1 "`.env.example`에 이름만 적는다").
  - `docker-compose.yml` — 서비스 1개(postgres). 이미지는 pgvector 확장이 포함된 `pgvector/pgvector:pg16` 계열, 포트 `${POSTGRES_PORT:-5432}:5432`, 이름 있는 볼륨으로 데이터 영속화, `pg_isready` 기반 `healthcheck`. 환경변수는 위 `.env.example`의 이름 4개를 `${VAR:-기본값}`으로 읽는다(`POSTGRES_USER=${POSTGRES_USER:-app}`, `POSTGRES_DB=${POSTGRES_DB:-relationship}`, `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-pass}`) — 기본값은 `.env.example`의 예시값과 같다.
  - `docker/initdb/01-vector.sql` — 최초 기동 시 `CREATE EXTENSION IF NOT EXISTS vector;`. (이미지가 확장 파일만 제공하고 DB에 확장을 만들어주지는 않으므로 initdb로 보장한다.)
  - 접속 검사 스크립트 `scripts/db_check.py`(psycopg 사용, 없으면 `scripts/db_check.sh`로 `psql` 호출) — `DATABASE_URL`로 접속 → `CREATE EXTENSION IF NOT EXISTS vector` → `SELECT '[1,2,3]'::vector` → 서버 버전·확장 버전·쿼리 결과를 표준출력에 찍고 실패 시 0이 아닌 종료 코드. 접속 문자열의 비밀번호는 출력하지 않는다(security.md §1). 추가로 **불일치 경고**: `DATABASE_URL`을 파싱한 user/password/db/port와 환경의 `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`/`POSTGRES_PORT`를 비교해, 다르면 **어긋난 변수 이름만** 경고로 찍는다(예: `WARN: DATABASE_URL 과 POSTGRES_PORT 값이 다릅니다`). 비밀번호는 어느 쪽 값도 출력하지 않고 이름만 알린다. 경고는 종료 코드를 바꾸지 않는다(수용 기준은 쿼리 성공 여부로만 판정).
  - 실행 증거: 위 스크립트와 `docker compose ps`/`up` 출력을 `docs/wiki/packages/P0-compose/evidence/`에 `tee`로 저장.
  - 문서 반영 두 곳: **README 로컬 DB 절**(`README.md` "로컬에서 해 보기" 절 아래, 121행이 "로컬 DB(docker-compose + pgvector) … 해당 패키지가 완료되면 이 절에 추가한다"로 예약해 둔 자리 — 기동·검사·중지 명령, `.env`의 `POSTGRES_*` 4개와 `DATABASE_URL`을 같은 값으로 유지하라는 안내) + **registry 기존 README 행 비고 갱신(새 행 금지)**(`docs/wiki/registry.md` 32행 `| 문서 | 프로젝트 README… | README.md | 하네스 | pending |`의 비고에 "P0-compose: 로컬 DB 절" 추가. 소유는 `하네스` 그대로).
- 이 패키지에서 하지 않는 것:
  - 스키마·테이블 생성, `events.type` CHECK, FK CASCADE 등 S3.1 구현 — **P1-schema**가 한다. 이 패키지는 확장까지만.
  - Alembic 도입·마이그레이션 파일 — P1-schema.
  - RDS·Terraform·SSM·프라이빗 서브넷 등 클라우드 인프라 — P9-infra.
  - 백엔드 애플리케이션 컨테이너(`Dockerfile`, compose의 app 서비스) — P2 이후.
  - 임베딩 값 적재·인덱스(HNSW/IVFFlat) 설계 — 컬럼이 생긴 뒤(P1-schema/P3-er).

## 산출물 (파일 경로)
- .env.example — DB 절에 이름 4개 추가(`POSTGRES_USER=app`, `POSTGRES_PASSWORD=pass`, `POSTGRES_DB=relationship`, `POSTGRES_PORT=5432` — 기존 `DATABASE_URL`과 같은 예시값 + "`DATABASE_URL`과 같은 값 유지, 실제 비밀번호는 `.env`에만" 주석)
- docker-compose.yml — postgres+pgvector 서비스, 포트·볼륨·healthcheck·환경변수(`${VAR:-기본값}`)
- docker/initdb/01-vector.sql — `CREATE EXTENSION IF NOT EXISTS vector;`
- scripts/db_check.py (대안: scripts/db_check.sh) — DATABASE_URL 접속 → 확장 생성 → `SELECT '[1,2,3]'::vector` 출력 + `POSTGRES_*`와 불일치 시 변수 이름만 경고
- docs/wiki/packages/P0-compose/evidence/ — compose 기동 출력, db_check 실행 출력(tee)
- README.md 로컬 DB 절 — "로컬에서 해 보기" 절 121행 예약 자리에 기동·검사·중지 명령과 `POSTGRES_*` ↔ `DATABASE_URL` 일치 안내
- docs/wiki/registry.md — compose·initdb·db_check 행 **추가**, README 는 기존 32행 비고 **갱신**(새 행 금지)

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)
- [ ] U1 `.env.example` 갱신 + compose 파일 + initdb: 먼저 `.env.example` DB 절에 이름 4개(`POSTGRES_USER=app`, `POSTGRES_PASSWORD=pass`, `POSTGRES_DB=relationship`, `POSTGRES_PORT=5432`)와 "`DATABASE_URL`과 같은 값 유지 · 실제 비밀번호는 `.env`에만" 주석을 추가한다(`.env` 는 읽지도 쓰지도 않는다). 그다음 `docker-compose.yml`(pgvector/pgvector:pg16 계열, 포트 `${POSTGRES_PORT:-5432}:5432`, 이름 있는 볼륨, healthcheck, 위 4개를 `${VAR:-기본값}`으로 읽기)과 `docker/initdb/01-vector.sql`(확장 생성) 작성. compose 기본값이 `.env.example`의 사용자·비밀번호·DB 이름·포트와 같은지 대조 / Refs: P0-compose D4 D5 S3.1
- [ ] U2 접속 검사 스크립트 + 실행 증거: `scripts/db_check.py`(psycopg, 실패 시 비정상 종료, `DATABASE_URL`↔`POSTGRES_*` 불일치 시 변수 이름만 경고·비밀번호 값 출력 금지) 작성 → `docker compose up -d` → healthcheck 통과 확인 → `db_check` 실행 출력에 `SELECT '[1,2,3]'::vector` 결과가 보이도록 `docs/wiki/packages/P0-compose/evidence/`에 tee / Refs: P0-compose D4 D5 S3.1
- [ ] U3 registry·문서 반영: `docs/wiki/registry.md`에 compose·initdb·db_check 행 추가 + **README 로컬 DB 절 + registry 기존 README 행(32행) 비고 갱신(새 행 금지)** — README "로컬에서 해 보기" 절 121행 예약 자리에 기동·검사·중지 명령, `.env`의 `POSTGRES_*` 4개와 `DATABASE_URL`을 같은 값으로 유지하라는 안내(포트를 바꾸면 둘 다 바꾼다), `down -v` 금지 주의, P1-schema가 이 산출물을 선행 조건으로 쓴다는 메모 / Refs: P0-compose D4 D5 S3.1

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)
- `SELECT '[1,2,3]'::vector` 성공

## 리스크 · 미결
- **Docker 데몬 미실행**: Windows 환경이라 Docker Desktop이 꺼져 있으면 U2를 실행할 수 없다. 에이전트는 우회하지 않고 사용자에게 Docker Desktop 실행을 요청하고 멈춘다(security.md §6).
- **5432 포트 충돌 · 값 출처 이원화(F-033bb1 결정 (a))**: 로컬에 PostgreSQL이 이미 떠 있으면 기동이 실패한다. 대응 — `.env.example`에 `POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB / POSTGRES_PORT` **이름 4개**를 두고(예시값은 `DATABASE_URL`과 같은 `app` / `pass` / `relationship` / `5432`, 실제 비밀번호는 `.env`에만), compose는 이 이름들을 `${VAR:-기본값}`으로 읽어 포트 매핑을 `${POSTGRES_PORT:-5432}:5432`로 둔다. 사용자는 `.env`에서 포트를 바꿀 수 있으나 **`DATABASE_URL`과 값이 같아야** 하며, 이를 (1) README 로컬 DB 절 안내와 (2) db_check의 불일치 경고(어긋난 변수 이름만 출력, 비밀번호 값 출력 금지) 두 곳으로 알린다. 즉 값의 단일 출처는 `.env`이고, `.env.example`은 이름과 예시값만 보여 준다.
- **비밀**: DB 비밀번호의 실제 값은 `.env`에만 둔다. 에이전트는 `.env`를 읽지도 쓰지도 않고 `.env.example`에는 이름과 공개된 예시값(`pass`)만 적는다(security.md §1). compose 파일에는 `${POSTGRES_PASSWORD:-pass}`처럼 `.env.example`과 동일한 예시값만 기본값으로 둔다. db_check 출력에 접속 문자열 전체·비밀번호 값을 찍지 않는다(불일치 경고도 변수 이름까지만).
- **볼륨 삭제 금지**: `docker compose down -v`, `docker volume rm`, `docker … prune`은 금지(security.md §4). 컨테이너만 내릴 때는 `docker compose down`. 볼륨을 지워야 하면 명령을 사용자에게 보여주고 직접 실행을 요청한다.
- 미결 1 — **이미지 태그 고정**: `pgvector/pgvector:pg16`으로 시작하되, P9-infra의 RDS PostgreSQL 버전과 메이저 버전을 맞춰야 한다. RDS 버전이 정해지기 전이므로 U1에서는 pg16으로 두고, P9-infra 착수 시 재확인한다는 메모를 README 로컬 DB 절과 registry 기존 README 행 비고에 남긴다(새 registry 행을 만들지 않는다).
- 미결 2 — **접속 드라이버**: `psycopg[binary]`를 새 의존성으로 추가할지, 컨테이너 안의 `psql`을 `docker compose exec`로 호출할지. 백엔드가 어차피 psycopg를 쓸 것이므로 `scripts/db_check.py`(psycopg) 우선, 설치가 막히면 `scripts/db_check.sh`(`docker compose exec -T postgres psql`)로 대체하고 그 결정을 03-log에 적는다.
- 미결 3 — 이 패키지에는 닫는 R 항목이 없어 `verify-impl.sh`의 수용 기준 표는 위 한 줄(`SELECT '[1,2,3]'::vector` 성공)만으로 채운다.

## 읽은 카드
- `docs/wiki/INDEX.md` 패키지 id 표(P0-compose 행 — 닫는 R `—`), `docs/wiki/CURRENT.md`(active: none)
- `.claude/gitlog.md`(브랜치 dev ahead 2, 최근 커밋 20건, 미커밋 변경 `docs/wiki/journal.md` 1건 — compose 관련 커밋 없음)
- `docs/backlog.md` "착수 준비" 절 docker-compose 항목, "구현 순서" P1 행(스키마 v2 의존에 docker-compose 명시)
- `docs/resolution-plan.md` §4 착수 준비 표 docker-compose 행, §1 D4·D5 절
- `docs/wiki/decisions/D04-embedding-provider.md` 전문(확정: text-embedding-3-small, N=1536), `docs/wiki/decisions/D05-alias-level-embedding.md` 전문
- `docs/wiki/specs/S3.1-schema-v2.md` 전문(테이블은 P1-schema에서 생성)
- `docs/wiki/security.md` §1 비밀, §4 인프라·데이터(docker prune/`down -v` 금지), §6 예외
- `.env.example` 전문(DB 절은 `DATABASE_URL` 한 줄뿐, `POSTGRES_*` 이름 없음 — U1에서 추가)
- `docs/wiki/registry.md`(grep: compose·docker·pgvector — 해당 없음 / grep README — 32행 `README.md` 소유 `하네스` 이미 존재)
- `README.md` "로컬에서 해 보기" 절 105~121행(121행이 로컬 DB 절 자리를 예약)
- `docs/wiki/templates/plan.md`, `docs/wiki/packages/P0-embed-pilot/01-plan.md`(형식 참고)

## 개정 이력
- 2026-09-03 개정 1 (architect): 02-plan-verify 보류(점검표 8행) 반영. F-033bb1 → 사용자 결정 (a): `.env.example`에 `POSTGRES_*` 이름 4개 추가, compose는 `${VAR:-기본값}`, `DATABASE_URL`과의 일치를 README 안내 + db_check 경고로 담보. F-0ffff5 → 범위·산출물·U3의 "README 또는 registry"를 "README 로컬 DB 절 + registry 기존 README 행 비고 갱신(새 행 금지)"으로 확정. 담당 표기를 L-002 역할 분리에 맞춰 architect(계획)/backend-agent(구현)/verifier(검증)로 수정. 수용 기준 문장은 그대로 두었다.
