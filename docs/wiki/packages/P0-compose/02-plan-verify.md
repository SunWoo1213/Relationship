# P0-compose · 계획 검증 (02-plan-verify)

대상: 01-plan.md (2026-09-03 개정 1 — F-033bb1·F-0ffff5 반영본) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002), 1차 검증과도 다른 새 컨텍스트 | 날짜: 2026-09-03

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P0-compose | tee docs/wiki/packages/P0-compose/evidence/20260903-verify-plan-2-final.txt` (본 문서를 개정본 기준으로 다시 쓴 뒤 실행한 최종 출력)
```
== verify-plan P0-compose  (2026-09-03 20:11) ==
PASS  존재: docs/wiki/packages/P0-compose/01-plan.md
PASS  존재: docs/wiki/packages/P0-compose/02-plan-verify.md
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-compose
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P9-infra
PASS  Refs 있음: - [ ] U1 `.env.example` 갱신 + compose 파일 + initdb: �
PASS  Refs 있음: - [ ] U2 접속 검사 스크립트 + 실행 증거: `script
PASS  Refs 있음: - [ ] U3 registry·문서 반영: `docs/wiki/registry.md`에
PASS  backlog 일치: `SELECT '[1,2,3]'::vector` 성공
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: .env.examp
PASS  registry 중복 없음: docker-compose.yml
PASS  registry 중복 없음: docker/initdb/01-vector.sql
PASS  registry 중복 없음: scripts/db_check.py
PASS  registry 중복 없음: scripts/db_check.sh
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
PASS  registry 중복 없음: docs/wiki/registry.md
== 결과: FAIL=0 WARN=1 ==
```
증거 파일: `docs/wiki/packages/P0-compose/evidence/20260903-verify-plan-2-final.txt` (최종). 개정본 01-plan 에 대해 본 문서를 고쳐 쓰기 **전**에 실행한 출력(1차 02-plan-verify 의 "보류 1 건"이 남아 WARN=2)은 `evidence/20260903-verify-plan-2.txt`. 1차 검증(개정 전 01-plan)의 출력은 `evidence/20260903-verify-plan.txt`·`-run1.txt`.
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py P0-compose evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다. — 남은 WARN 1건(README.md)은 이미 05-remediation.md F-0ffff5 로 올라가 있고 §3 에서 이유를 적는다. 새 소견은 만들지 않는다.

선행 확인(`bash .claude/scripts/gitlog.sh P0-compose`, 2026-09-03 20:07): 브랜치 `dev` = `ae2076f`(origin/dev 대비 ahead 1 — `docs(readme): 프로젝트 전체 소개 README 추가`), `main` = `4df323f`. 태그 `P0-compose` 커밋 0건(중복 착수 없음). D4 확정 커밋 `e4ab0a4`("docs(P0-embed-pilot): U3 카드 반영·완료 검토 — D4 확정, S3.1 vector(1536)")·`a66f1e2`. 미커밋 변경: `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md`(수정), `docs/wiki/packages/P0-compose/`(신규) — 모두 `/devlog start` 절차의 문서 변경, 제품 코드 변경 없음(`git status --short` 에 `docker-compose.yml`·`scripts/db_check*`·`.env.example` 없음). `docs/wiki/CURRENT.md` `active: none`, `frozen: none`.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 행 번호는 개정된 01-plan.md 기준이다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | CLAUDE.md 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱". 01-plan 13행 "`docker-compose.yml` — 서비스 1개(postgres)", 8행 "이 패키지는 **DB 엔진과 확장까지만** 준비하고 테이블은 만들지 않는다", 18~23행 "하지 않는 것" 5항(스키마·Alembic·RDS/Terraform·app 컨테이너·임베딩 적재/인덱스). 산출물(26~32행)이 DB 엔진·확장·접속 검사·문서뿐이라 제외 목록에 닿는 제품 기능이 없다. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 01-plan 4행 "관련 원칙: 없음". 원칙1~5·9(오병합·임계치·3신호·ER 4단계·화면 3개·trace)는 이 패키지에 해당 코드가 없고 23행 "임베딩 값 적재·인덱스(HNSW/IVFFlat) 설계 — 컬럼이 생긴 뒤(P1-schema/P3-er)"로 경계가 있다. 원칙8(재현 가능) — 16행 "실행 증거: 위 스크립트와 `docker compose ps`/`up` 출력을 … `evidence/`에 `tee`로 저장", 15행 "서버 버전·확장 버전·쿼리 결과를 표준출력에 찍고 실패 시 0이 아닌 종료 코드". 원칙6(패턴 감지)·7은 1행에서 봄. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | D04-embedding-provider.md "차원 N은 설정값이며 마이그레이션에 하드코딩하되 그 근거를 `reports/embed_pilot.md`에 남긴다" → 마이그레이션은 01-plan 20행 "Alembic 도입·마이그레이션 파일 — P1-schema"로 이 패키지 밖. D04 "확정 … N = 1536 … 3072 는 pgvector HNSW 한도(2000) 초과" → 01-plan 8행 "D4가 확정한 차원(`text-embedding-3-small`, N=1536) … S3.1의 `vector(1536)` 컬럼 … P1-schema(Alembic)의 선행 조건이 이 패키지다"와 일치. D04 "환경변수: `OPENAI_API_KEY`(임베딩), `ANTHROPIC_API_KEY`(LLM). `.env.example` 참조" → 01-plan 12행이 `.env.example` 에 `POSTGRES_*` 4개를 **추가**할 뿐 기존 이름을 바꾸지 않는다(현재 `.env.example` 5·11행 `ANTHROPIC_API_KEY=`, `OPENAI_API_KEY=` 그대로). D05-alias-level-embedding.md "인물당 대표 벡터를 만들지 않는다. 새 별칭이 확정(`confirmed_at`)되면 즉시 임베딩한다" → 이 패키지는 벡터를 저장하지 않으므로 충돌 지점 없음. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | S3.1-schema-v2.md 7행 "person_aliases(… embedding vector(1536) …) -- N=1536: D4 확정" → `vector` 타입은 확장 없이는 쓸 수 없고 01-plan 14행 "`docker/initdb/01-vector.sql` — 최초 기동 시 `CREATE EXTENSION IF NOT EXISTS vector;`"가 그 전제를 만든다. S3.1 "`events.type` CHECK 제약", "FK ON DELETE CASCADE" → 01-plan 19행 "스키마·테이블 생성, `events.type` CHECK, FK CASCADE 등 S3.1 구현 — **P1-schema**가 한다. 이 패키지는 확장까지만"으로 테이블 생성이 배제되어 P1-schema 와 겹치지 않는다. 시그니처 v2·임계치 2개·ask_user 비동기(S3.2/S3.4)는 이 패키지가 건드리는 파일(산출물 26~32행)에 없다. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | docs/backlog.md 16행 "[backend-agent] 로컬 docker-compose (pgvector) / 의존: 없음" = 01-plan 5행 "의존: 없음 (착수 준비 항목. 선행 패키지 없음. P4 게이트 해당 없음)". backlog 22행 P1 "스키마 v2 마이그레이션 (Alembic) / 의존: 착수 준비(D4 차원 확정, docker-compose)" → 이 패키지가 P1 의 선행이며 D4 확정은 커밋 `e4ab0a4`(gitlog.sh "docs(P0-embed-pilot): U3 카드 반영·완료 검토 — D4 확정")로 끝나 있다. P4 게이트는 P5 이후 대상이라 P0 에 해당 없음. INDEX.md 63행 "`P0-compose` | 로컬 docker-compose pgvector | backend-agent | —" → 닫는 R 없음 = 01-plan 4행 "닫는 검증: 없음", 49행 미결 3. CURRENT.md "active: none" → 동시 활성 패키지 없음. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | docs/backlog.md 16행 "수용기준: `SELECT '[1,2,3]'::vector` 성공" = 01-plan 40행 "- `SELECT '[1,2,3]'::vector` 성공". docs/resolution-plan.md 215행 "로컬 docker-compose (pgvector) | backend-agent | `docker-compose.yml` | `SELECT '[1,2,3]'::vector` 성공"과도 동일. 기계 검증 "PASS backlog 일치". 기계적 판정 가능: 01-plan 36행 U2 "`db_check` 실행 출력에 `SELECT '[1,2,3]'::vector` 결과가 보이도록 … tee", 15행 "실패 시 0이 아닌 종료 코드", 15행 "경고는 종료 코드를 바꾸지 않는다(수용 기준은 쿼리 성공 여부로만 판정)" — 불일치 경고가 수용 기준 판정을 흐리지 않는다. 65행 "수용 기준 문장은 그대로 두었다". |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan 35·36·37행 U1·U2·U3 각 줄 끝 "Refs: P0-compose D4 D5 S3.1"(기계 검증 "PASS Refs 있음" ×3). 태그가 가리키는 카드 실재: `docs/wiki/decisions/D04-embedding-provider.md`, `docs/wiki/decisions/D05-alias-level-embedding.md`, `docs/wiki/specs/S3.1-schema-v2.md`, `docs/wiki/INDEX.md` 63행 `P0-compose`(기계 검증 "PASS 카드 존재: D4/D5", "PASS 패키지 id 등록됨"). 단위 크기: U1 = 파일 3개(`.env.example` 4줄 추가·compose·initdb), U2 = 스크립트 1개 + 실행 증거, U3 = 문서 2곳 + registry — 각각 커밋 하나 크기. |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | (가) `.env.example` 갱신이 산출물·U1 에 있음 — 01-plan 26행 "- .env.example — DB 절에 이름 4개 추가(`POSTGRES_USER=app`, `POSTGRES_PASSWORD=pass`, `POSTGRES_DB=relationship`, `POSTGRES_PORT=5432` …)", 35행 "U1 `.env.example` 갱신 + compose 파일 + initdb: 먼저 `.env.example` DB 절에 이름 4개 … 주석을 추가한다(`.env` 는 읽지도 쓰지도 않는다)". security.md §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다 / 에이전트는 `.env.example`에 **이름만** 적는다" ↔ 01-plan 12행 "에이전트는 `.env`를 읽지도 쓰지도 않는다(security.md §1)", 44행 "값의 단일 출처는 `.env`이고, `.env.example`은 이름과 예시값만 보여 준다". 예시값 `app/pass/relationship/5432`는 이미 커밋된 `.env.example` 14행 "DATABASE_URL=postgresql://app:pass@localhost:5432/relationship"과 같은 공개 자리표시자이며 사용자 결정(2026-09-03, (a))이 그 값을 지정했다. 훅 대조: `.claude/hooks/secret-guard.sh` 60행 패턴 `postgres(ql)?://[^:/[:space:]]+:[^@[:space:]]{8,}@`(비밀번호 8자 이상만 차단)이라 `pass`(4자)·`POSTGRES_PASSWORD=pass`·`${POSTGRES_PASSWORD:-pass}`는 어느 패턴에도 걸리지 않는다 — U1 이 훅에 막히지 않는다. (나) db_check 가 비밀번호 값을 출력하지 않음 — 01-plan 15행 "접속 문자열의 비밀번호는 출력하지 않는다(security.md §1) … 다르면 **어긋난 변수 이름만** 경고로 찍는다 … 비밀번호는 어느 쪽 값도 출력하지 않고 이름만 알린다", 36행 U2 "불일치 시 변수 이름만 경고·비밀번호 값 출력 금지", 45행 "db_check 출력에 접속 문자열 전체·비밀번호 값을 찍지 않는다(불일치 경고도 변수 이름까지만)" ↔ security.md §1 "로그·trace에 키·비밀을 남기지 않는다", "환경변수 전체 출력 … KEY/SECRET 변수 echo 금지". (다) `down -v` 금지 — 01-plan 46행 "`docker compose down -v`, `docker volume rm`, `docker … prune`은 금지(security.md §4). 컨테이너만 내릴 때는 `docker compose down`. 볼륨을 지워야 하면 명령을 사용자에게 보여주고 직접 실행을 요청한다", 37행 U3 "`down -v` 금지 주의" ↔ security.md §4 "`docker … prune`, `volume rm`, `compose down -v` 금지 / 컨테이너만 내리기(`down`). 볼륨 삭제는 사용자". 43행 Docker 미실행 시 "우회하지 않고 사용자에게 Docker Desktop 실행을 요청하고 멈춘다(security.md §6)" ↔ §6 "우회하지 않고 사용자에게 명령을 그대로 보여주고 직접 실행을 요청한다". 외부 전송: 산출물에 `curl`/`scp` 없음, 16행 evidence 는 로컬 `tee`. |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
- 보류 없음.
- **F-033bb1 (1차 검증 점검표 8행 보류) — 해소 조건 충족(계획 단계).** 1차 보류의 조건은 "산출물·U1 에 `.env.example` 이름 4개 추가를 명시하거나(a) / compose 가 `.env`를 읽지 않게(b)"였고 사용자가 (a) 를 택했다. 개정본 대조(완료 판정 명령 실행 출력 `evidence/20260903-remediation-check-2.txt`): 산출물 26행 `- .env.example — DB 절에 이름 4개 추가(...)` (명령 `grep -n "^- .env.example"` 1건), U1 35행 첫 작업이 `.env.example` 갱신(`grep -n "U1 .*\.env\.example"` 1건), `${POSTGRES_PORT:-5432}` 가 13·35·44행 3곳(기대 2 이상), "불일치" 5회(기대 2 이상). 1차 보류가 지적한 "출처 이원화"는 44행 "값의 단일 출처는 `.env`이고, `.env.example`은 이름과 예시값만 보여 준다" + (1) README 안내(31행) + (2) db_check 이름만 경고(15행)로 닫혔다. 12행 "`.env`에서 읽되" 류의 문구는 사라지고 13행 "환경변수는 위 `.env.example`의 이름 4개를 `${VAR:-기본값}`으로 읽는다 … 기본값은 `.env.example`의 예시값과 같다"로 바뀌었다. 구현 단계(05-remediation F-033bb1 5~7: `.env.example` 실제 4줄, compose `${VAR:-}` 4개, db_check 경고·README 안내)는 지금 시점에 파일이 없어(`grep -c "POSTGRES_" .env.example` → 0, `docker-compose.yml`·`scripts/db_check.*` 없음) "대기"로 두고 04-review 에서 판정한다.
- **F-0ffff5 (1차 권고) — 반영됨(계획 단계).** 개정본 17행 "**registry 기존 README 행 비고 갱신(새 행 금지)**(`docs/wiki/registry.md` 32행 … 비고에 "P0-compose: 로컬 DB 절" 추가. 소유는 `하네스` 그대로)", 32행 "README 는 기존 32행 비고 **갱신**(새 행 금지)", 37행 U3 "README 로컬 DB 절 + registry 기존 README 행(32행) 비고 갱신(새 행 금지)". 1차에서 어긋났던 범위 절의 "README **또는** registry" 문구는 17행 "문서 반영 두 곳"으로 대체되어 산출물·U3 와 일치한다. 완료 판정 명령: "새 행 금지" 4건(기대 3 이상), "기존 32행|기존 README 행" 5건(기대 2 이상), `U3 .*비고 갱신` 1건. 참조 위치 실재 확인: `docs/wiki/registry.md` 32행 `| 문서 | 프로젝트 README(...) | README.md | 하네스 | pending | 패키지 완료마다 진행 상태 표 갱신 |`(`grep -c "| README.md |"` → 1), `README.md` 105행 "## 로컬에서 해 보기", 121행 "로컬 DB(docker-compose + pgvector)와 백엔드 서버 실행 방법은 해당 패키지가 완료되면 이 절에 추가한다". 구현 단계(F-0ffff5 4·5)는 대기.
- **기계 검증 WARN 1건("registry 에 다른 패키지로 이미 있음: README.md")은 보류 사유가 아니다.** 이유: registry 에 `README.md` 행은 32행 하나뿐이고(소유 `하네스`), 이 패키지는 그 파일에 절 하나를 보태고 그 행의 비고를 갱신할 뿐 새 행을 만들지 않는다(01-plan 17·32·37행 "새 행 금지"). README 121행이 이 패키지의 절을 미리 예약해 두었으므로 중복 구현이 아니다. verify-plan.sh 는 산출물 경로가 registry 에 있으면 소유자를 따지지 않고 WARN 을 내므로, 이 WARN 은 U3 가 완료된 뒤에도 남는 것이 정상이다. 04-review 에서는 `grep -c "| README.md |" docs/wiki/registry.md` 가 여전히 `1` 인지로 판정한다(05-remediation F-0ffff5 4단계).
- 참고(보류 아님, 구현·완료 검토 때 볼 것):
  - db_check 불일치 비교(15행)에서 `POSTGRES_*` 가 환경에 **없을 때**의 처리가 계획에 적혀 있지 않다. compose 는 `${VAR:-기본값}`으로 예시값에 떨어지므로, db_check 도 변수가 없으면 같은 기본값(`app`/`pass`/`relationship`/`5432`)과 비교해야 거짓 경고가 나지 않는다. 15행 "경고는 종료 코드를 바꾸지 않는다"라 수용 기준 판정에는 영향이 없다 — U2 구현 시 03-log 에 처리 방식을 적을 것.
  - 05-remediation F-033bb1 5단계 기대값 `grep -c "POSTGRES_" .env.example` = `4` 는 "주석 문장에는 `POSTGRES_` 문자열을 쓰지 않는다"를 전제한다. 01-plan 12행의 주석 문안("이 4개는 `DATABASE_URL`과 같은 값이어야 한다. 실제 비밀번호는 `.env`에만 넣는다")은 그 전제를 만족한다 — U1 에서 문안을 바꾸면 판정 명령도 같이 조정할 것.
  - 저장소에 의존성 선언 파일(`requirements.txt`/`pyproject.toml`)이 없다. 미결 2(48행)의 `psycopg` 우선 → 막히면 `scripts/db_check.sh` 대체는 계획 안에서 결정 가능하며, `README.md` 113행 `pip install openai numpy python-dotenv pytest` 가 의존성을 문서로만 관리하는 선례다. 택한 쪽을 03-log 에 적을 것.
  - 이미지 태그 `pgvector/pgvector:pg16`(13행·47행)은 확장 버전을 고정하지 않지만 15행 "서버 버전·확장 버전 … 표준출력"이 evidence 에 남으면 실제 버전이 기록된다. 미결 1~3 은 모두 이 패키지 안에서 결정 가능하고 사용자 결정이 더 필요한 항목은 없다.
  - 01-plan 53행 "브랜치 dev ahead 2 … 미커밋 변경 `docs/wiki/journal.md` 1건"은 작성 시점 값이고 현재는 `dev = ae2076f`(ahead 1), 미커밋 3건(§1 선행 확인). 판정에 영향 없음.
  - evidence 에 `docker compose config`·`env` 출력은 넣지 않는다(16행은 `ps`/`up`·db_check 출력만). 그대로 유지할 것.

## 4. 결정
결과: 통과
승인: 사용자 (2026-09-03)
