# P9-infra · 계획 (01-plan)

상태: **활성(2026-11-14)** — architect AWS 최소 구성 재작성 → 사용자 결정 A t4g.small · B 새 도메인(준비 전 sslip.io) · D SSH · J 11-19 18:00, 나머지 추천안 위임 → verifier 02-plan-verify 1차 보류(F-P9V-1 Caddyfile 404 순서) → 보정 → **재검증 통과**([필수] 0 · [권고] F-P9V-2~7 반영/이관) | 담당: backend-agent(sonnet, U1·U1b) · frontend-agent(sonnet, U2) · 메인 세션(U3 문서·U4 진행·증거 저장) · 사용자(계정·Budgets·EC2·`.env`·OpenAI 한도·U4 사람 점검·종료 절차 실행) · 검증 verifier(fable, 02-plan-verify·단위 리뷰·04-review) | 작성: 2026-11-14
태그 — 패키지: P9-infra · 닫는 검증: R14(재결정 → D17 개정 ②) · 기대는 결정: D17(D7 대체) · D4·D11 유지(키는 서버 `.env`) · 구현하는 명세: S3.6(원문 그대로 — 1분 루프) · 관련 원칙: 원칙5 원칙7 원칙8 원칙9 · 이어받는 소견: R-U10D-1~10(`P8-frontend/review-u10-deploy-validity.md` §10) · F-fbaaae(사용자 격리 없음) · 출처 CR: CR-005 개정 ②(2026-11-14 오후)
의존: P8-frontend(04-review `완료` 2026-10-21) — **충족** · P8b-persons-grid(완료 2026-10-28) — 충족 · P4 게이트(P4b 통과 2026-09-23) — 충족 · P2b-person-delete 는 **U2 `3a1bcec` 뒤 보류**(CR-005 일정 제약 — `delete_person` 은 라우트가 없어 배포본에 노출되지 않는다).

- **기준 해시**: **`4a4d8cb`**(CR-005 개정 ② 문서 커밋 — 메인 세션이 활성화 직전 `bash .claude/scripts/gitlog.sh P9 CR-005 D17` 로 확인, 2026-11-14 13:59; P9·CR-005·D17 태그 커밋은 `53cbefe`·`4a4d8cb` 문서 2건, 코드 커밋 0). 아래 `<기준>` 은 전부 이 해시다. 활성화 커밋 자체는 문서만이라 제품 코드 diff 판정에 영향 없음.
- **기준선**: pytest **2202 passed, skip 0**(P2b U2 `3a1bcec` 포함 — 메인 세션이 2026-11-14 13:59 재실행으로 확정, 27초) · mypy `python3 scripts/mypy_check.py --run` 기준선 38건 · `scripts/tools_check.py` 7/7 · Vitest 는 U2 시작 전 재어 03-log 에.
- **일정 제약**: 오늘 2026-11-14(토), 졸업평가 2026-11-18(수), 공개 종료 2026-11-19(목). 사용자 지시 "실제로 띄우는 건 아직 하지 말고 계획부터" — **계획·파일 작성·로컬 compose 스모크(U1~U3)까지 에이전트, EC2 생성·기동·호스트명(U4)은 사용자가 따로 지시할 때.**

### 코드에서 확인한 사실 (계획의 전제)

1. **앱은 값을 `os.environ` 에서만 읽는다**(`app/config.py` 16~18행, `app/settings.py` 4행). compose `env_file: .env` 가 서버 `.env` 를 컨테이너 환경변수로 넣으면 그대로 동작한다 — 제품 코드 변경 0 의 근거.
2. **`DATABASE_URL` 이 `POSTGRES_*` 보다 우선이고, URL 에 비밀번호가 없으면 `POSTGRES_PASSWORD` 로 채운다**(`app/config.py` 114~123행 — `password=parsed["password"] or postgres["password"]`). 분해는 `urlsplit`(79~89행)이라 비밀번호를 URL 에 넣으면 `@`·`/`·`:`·`%`·`#`·`?` 에서 깨지거나 이중 인코딩되지만, URL 에서 비밀번호를 빼면 `sqlalchemy_url()` 이 `quote()` 로 올바르게 넣는다(69~76행). → 운영 `DATABASE_URL` 은 **비밀번호 없는 URL** `postgresql://<user>@postgres:5432/<db>` 로 두고 비밀번호는 `POSTGRES_PASSWORD` 환경변수로 준다(결정 O).
3. **[하네스 제약] `secret-guard.sh` 68행 패턴 `postgres(ql)?://[^:/[:space:]]+:[^@[:space:]]{8,}@` 은 변수 보간(`${…}:${…}@`)이어도 "비밀번호가 든 DB URL" 로 보고 Write 를 거부한다**(이 계획 초안을 쓰다 실제로 걸렸다). `save_evidence.py` 에도 같은 패턴이 있다. → compose·문서·증거 어디에도 `<user>:<password>@` 꼴을 쓰지 않는다(사실 2 의 비밀번호 없는 URL 이 이 제약도 푼다). backend-agent 위임 시 이 줄을 인용한다.
4. **`/health` 503 분기는 경로 문자열 `/health` 에 묶여 있다**(`app/main.py` 147행). Caddy `handle_path /api/*` 가 접두를 떼고 넘기므로 백엔드가 보는 경로는 `/health` 다 — 분기가 그대로 산다. 라우트는 전부 접두 없음, 프론트 `API_BASE='/api'`, 개발 서버는 Vite 프록시가 `stripApiPrefix` 로 뗀다(`web/vite.config.ts` 22~29행). 운영에서는 Caddy 가 같은 역할을 한다. `vite.config.ts` 에 `base` 없음(루트 배포 전제).
5. **스케줄러는 lifespan 이 워커마다 띄운다**(`app/main.py` 155~172행). `BRIEFING_SCHEDULER_ENABLED` 는 비면 꺼짐, `1`/`true` 만 켜짐, 그 밖은 기동 실패(`app/settings.py`). 한 번 돌 때마다 `briefing_run` trace 1행을 남긴다(`app/briefing/run.py` 6행) → 일정이 0건이어도 로컬 스모크로 S13 을 판정할 수 있다. 워커 수는 **`--workers 1` 로 고정**한다(R-U10D-9).
6. **로컬 `docker-compose.yml` 은 서비스 `postgres`·볼륨 `pgdata` 를 쓰고 프로젝트 이름을 지정하지 않는다** → 같은 디렉터리의 `docker-compose.prod.yml` 도 이름이 없으면 기본 프로젝트 이름(디렉터리명 `relationship`)이 되어 **기존 `relationship_pgdata` 볼륨과 충돌한다**(보정 F-P9V-3: 현재 개발 DB 컨테이너의 실제 프로젝트는 `capstone2`(볼륨 `capstone2_pgdata`)이고 `relationship_pgdata` 는 따로 남아 있는 옛 볼륨 — 운영 compose 는 `--env-file <스크래치>` 로 띄워 `.env` 의 `COMPOSE_PROJECT_NAME` 을 받지 않으므로 `name:` 이 유일한 방어). → 운영 compose 는 최상위 `name: relationship-prod` 필수(U1 테스트로 박는다).
7. `docker/initdb/01-vector.sql`(`CREATE EXTENSION IF NOT EXISTS vector`)이 있고, `alembic` 0001 도 확장을 만든다. 공식 postgres 이미지의 `POSTGRES_USER` 는 슈퍼유저라 entrypoint 의 `alembic upgrade head` 가 확장을 만들 수 있다(RDS 권한 문제 R-U10D-4 는 compose 에서 소멸).
8. **`web/package-lock.json` 에 linux-arm64-gnu 바이너리가 있다**(`@rolldown/binding-linux-arm64-gnu` 3059행 · `@tailwindcss/oxide-linux-arm64-gnu` 3423행 · `lightningcss-linux-arm64-gnu` 5949행). glibc 기반 `node:24-slim` 이면 ARM(t4g)에서도 `npm ci` 가 될 것으로 본다. musl(alpine) 바이너리는 확인하지 않았다 → 빌드 단계에 alpine 을 쓰지 않는다. `web/package.json` `engines` 는 `node >=24`·`npm >=11`, build = `tsc -b && vite build` → `web/dist`(devDependencies 필요 — 빌드 단계에서 `NODE_ENV=production` 을 `npm ci` 앞에 두지 않는다).
9. **`app/` 은 실행 중 `evaluation`·`scripts`·`data`·`reports` 를 import 하지 않는다**(grep 0). 파일을 읽는 곳은 `app/push/devpage`(앱 안)뿐. `alembic.ini` 는 `prepend_sys_path = .`. → 백엔드 이미지에는 `app/`·`alembic/`·`alembic.ini`·`requirements.txt`·`docker/entrypoint.sh` 만 있으면 된다.
10. `.python-version` 없음. `pyproject.toml` ruff `target-version = "py313"`·mypy `python_version = "3.13"`, CI 는 3.13·3.14(`tests.yml` 35행). CI 는 `push` 브랜치 `main, dev, dev2` 와 `pull_request` 에서 돈다(3~8행) — Dockerfile 빌드 job 을 넣으면 dev2 푸시마다 돈다.
11. **보안 카드 §4**: 로컬 이외로 본문을 보내는 `curl -d/-F/-T`·`scp` 는 에이전트가 실행하지 않는다 → 배포 URL `POST /api/chat`(S6)·`pg_dump` 파일 내려받기(scp)는 사용자 몫. 본문 없는 `GET`·`-I` 는 에이전트가 `save_evidence.py` 로 실행할 수 있다. §4 `compose down -v`·`volume rm`·`prune` 금지 — 로컬 스모크는 `down`(볼륨 유지)까지만.
12. **보안 카드 §1·L-007**: 에이전트는 `.env` 를 읽지도 쓰지도 않는다. 로컬 스모크는 사용자의 `.env` 를 쓰지 않고 **스크래치패드의 비밀 없는 변수 파일**(`p9-smoke-vars.txt`, LLM 키 없음)로 compose 를 띄운다. `GET /persons`·`/health`·정적 파일은 LLM 키 없이 동작한다(SDK 지연 import, `requirements.txt` 10~18행 주석).
13. `POST /briefings/run` 은 보호가 없다(지금 동작 그대로). 배포본의 "지금 브리핑" 버튼(`BriefingScreen.tsx` → `POST /briefings/run {schedule_id}`)이 그대로 동작한다. 공개 URL 에서 누구나 부를 수 있다는 점은 `POST /chat` 과 같은 비용 노출이며 CR-005 결정 D(d)(접근 보호 없음)가 감수했다 — OpenAI 월 지출 한도가 상한(리스크 절).

## 목표

CR-005 개정 ②·D17 이 확정한 배포 형태 — **EC2 1대 + Docker Compose 서비스 3개(`caddy` 자동 HTTPS·`/api/*` 접두 제거·프론트 정적 서빙 / `backend` FastAPI + `alembic upgrade head` entrypoint / `postgres` pgvector 볼륨, 호스트 포트 미노출)** — 를 **제품 코드 변경 없이** 배포 파일(`Dockerfile`·`docker/entrypoint.sh`·`docker-compose.prod.yml`·`Caddyfile`·`.dockerignore`)과 사용자 절차 문서로 만들어, 기획서 데모 시나리오 5단계(첫 언급 → 사건 누적 → 승진 호칭 변이(ER 병합 또는 `ask_user`) → 일정 등록 → 브리핑 웹푸시 + 수동 트리거)를 **배포 URL(HTTPS)에서** 재현한다. 1분 브리핑 스케줄러는 서버 안에서 원문(S3.6) 그대로 돈다(`BRIEFING_SCHEDULER_ENABLED=1`, 운영 `.env`). 공개는 ~2026-11-19(목) 한정이고 접근 코드·로그인은 만들지 않는다(CR-005 결정 D(d)). 공개를 끝내는 **종료 절차**(종료 직전 `pg_dump` 1회 → 인스턴스 종료 → EBS·EIP 해제 → 보안 그룹 삭제 → OpenAI·VAPID 회전)를 문서로 남긴다. 예: 심사자가 `https://<호스트명>/#/chat` 을 열어 "김 대리랑 점심 먹었어" 라고 치면 Caddy 가 `/api/chat` 을 `backend:8000/chat` 으로 넘기고 같은 EC2 의 Postgres 에 인물·사건이 쌓인다. 일정 화면 "지금 브리핑" 을 누르면 푸시가 오고, 일정이 24시간 안으로 들어오면 1분 루프가 스스로 브리핑을 만든다.

## 범위

- 포함:
  - 배포 파일: 다단계 `Dockerfile`(백엔드 이미지 + 프론트 빌드를 담은 Caddy 이미지) · `docker/entrypoint.sh` · `docker-compose.prod.yml` · `Caddyfile` · `.dockerignore` · `.env.example` 이름 줄 · 텍스트 검사 테스트 `tests/test_deploy_files.py` · **로컬 compose 스모크**(U1).
  - (결정 H 가 (i) 이면) CI 에 이미지 빌드 + compose 헬스 스모크 job(U1b, R-U10D-1).
  - 프론트 빌드 산출물·`/api` 규약·PWA 루트 경로 확인(기대 변경 0)(U2).
  - 사용자 문서 `docs/user-setup/11-ec2-minimal-deploy.md`(가입 → 기동 → 스모크 → 데모) · `12-shutdown.md`(종료 체크리스트) · registry · security §1 문구 · 관련 문서 상단 안내(U3).
  - 실제 기동·스모크 S1~S17(치환본)·데모 5단계 사람 점검·03-log(U4, **사용자 지시 뒤**).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **제품 코드(`app/`·`web/src/`·`alembic/`) 변경** — D17 "코드에서 지켜야 할 것" 1. 배포 때문에 고칠 점이 나오면 이 패키지에서 고치지 않고 FIX 로 분리해 사용자에게 보고한다.
  - **S3·CloudFront·RDS·ALB·NAT·Terraform·SSM·ECR·GitHub Actions 배포 워크플로** — D17 1·5 "없음". 5일 공개·몇 명 규모에 과하다(09 가이드 §6 논리).
  - **Vercel 안의 4단위(`/api` 래퍼·브리핑 비밀 헤더·DSN 쿼리 보존·Actions 스케줄)** — CR-005 개정 ② "하지 않는다". 1분 루프가 서버 안에서 돌고 Caddy 가 접두를 뗀다.
  - **접근 코드·로그인·사용자 격리(F-fbaaae)** — CR-005 결정 D(d). 격리는 스키마 변경(S3.1)이라 CR 이 따로 필요하다.
  - **자동 백업 파이프라인** — D17 7. 종료 직전 `pg_dump` 1회로 갈음(기간 한정 데모).
  - **CloudWatch 에이전트·중앙 로그·APM·WAF** — 09 가이드 §6. 관측성은 `agent_traces`(원칙9)와 `docker compose logs`.
  - **새 화면·화면 요소** — 원칙5.
  - **P2b-person-delete U3~U5** — 11-19 뒤 재개(CR-005 일정 제약).
  - **P10 최종 평가·P11 데모 리허설 스크립트** — 의존이 P9 뒤다.

## 산출물 (파일 경로)

**새로 만드는 파일** (각 단위 시작 전 `registry.md` grep — 이 계획 작성 시 `Dockerfile`·`Caddy`·`docker-compose.prod`·`entrypoint`·`dockerignore` 행 없음. 있는 행: 42행 `docker-compose.yml`(로컬 DB, P0-compose) · 43행 `docker/initdb/01-vector.sql` · 36행 `docs/user-setup/09-aws-deploy.md` · 267행 `docs/RUNNING.md` 프론트 절)

- `Dockerfile` — 단계 3개(결정 E·F·G 추천안 기준): `web-build`(`node:24-slim`, `web/package*.json` 먼저 복사 → `npm ci` → 나머지 복사 → `npm run build`) · `caddy`(`caddy:2-alpine`, `/srv` ← `web-build` 의 `dist`, `/etc/caddy/Caddyfile` ← `Caddyfile`) · `backend`(`python:3.13-slim`, `pip install --no-cache-dir -r requirements.txt`, `app/`·`alembic/`·`alembic.ini`·`docker/entrypoint.sh` 복사, CR 제거(`sed -i 's/\r$//'` — 이미지 안 RUN, Windows 체크아웃 대비), 비루트 사용자 `app`, `ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]`, `EXPOSE 8000`).
- `docker/entrypoint.sh` — `set -eu` → `python -m alembic upgrade head` → `exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`. 마이그레이션이 실패하면 `set -e` 로 컨테이너가 죽는다(D17 4, `docker compose ps` 에 `Exited`/재시작 루프로 보임).
- `docker-compose.prod.yml` — 최상위 `name: relationship-prod`(사실 6). 서비스:
  - `postgres`: `image: pgvector/pgvector:pg16`(로컬·CI 와 같은 이미지) · `environment` 는 보간만(`POSTGRES_USER: ${POSTGRES_USER:?…}` · `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?…}` · `POSTGRES_DB: ${POSTGRES_DB:?…}`) — **`env_file` 없음**(LLM 키를 DB 컨테이너에 주지 않는다) · **`ports` 없음** · 볼륨 `pgdata:/var/lib/postgresql/data` + `./docker/initdb:/docker-entrypoint-initdb.d:ro` · healthcheck `pg_isready` · `restart: unless-stopped`.
  - `backend`: `build: {context: ., target: backend}` · `image: relationship-backend:${GIT_SHA:-local}`(D17 5 "이미지 태그 = 커밋 해시") · `env_file: - ${APP_ENV_FILE:-.env}` · `environment`(결정 O 추천안 — `env_file` 의 같은 이름을 덮어쓴다): `DATABASE_URL` = 비밀번호 없는 URL(스킴 `postgresql`, 사용자 `${POSTGRES_USER}`, 호스트 `postgres:5432`, DB `${POSTGRES_DB}` — D17 3 "compose 네트워크 이름을 가리킨다", 사실 2·3) · `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?…}`(사실 2 의 대체 경로가 읽는 값) · **`ports` 없음** · `depends_on: postgres: condition: service_healthy` · healthcheck `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"`(slim 이미지에 curl 없음, `start_period` 60s) · `restart: unless-stopped`.
  - `caddy`: `build: {context: ., target: caddy}` · `image: relationship-caddy:${GIT_SHA:-local}` · `ports: "${CADDY_HTTP_PORT:-80}:80"`, `"${CADDY_HTTPS_PORT:-443}:443"` · `environment: SITE_ADDRESS: ${SITE_ADDRESS:?…}` · 볼륨 `caddy_data:/data`(**인증서 보존** — 재빌드마다 재발급하면 발급 한도를 소모한다) · `caddy_config:/config` · `depends_on: [backend]`(`service_started` — 백엔드가 비정상이어도 정적 화면은 뜬다) · `restart: unless-stopped`.
  - 세 서비스 공통 `logging`(결정 L 추천안: `json-file`, `max-size: "10m"`, `max-file: "3"`). 볼륨 `pgdata`·`caddy_data`·`caddy_config`.
- `Caddyfile` — 호스트명은 `{$SITE_ADDRESS}` 자리표시자(하드코딩 0). 블록 안: `encode gzip` · `handle_path /api/* { @docs path /docs* /redoc* /openapi.json ; respond @docs 404 ; reverse_proxy backend:8000 }`(결정 M (i) — **404 는 `handle_path` 블록 안**에서 접두가 떼인 경로로 매칭하고 `reverse_proxy` 보다 **앞**에 둔다. 최상위 `respond` 는 Caddy 지시문 순서상 `handle_path` 뒤에 평가돼 `/api/docs` 가 백엔드 Swagger 200 으로 새어 나간다 — 02-plan-verify F-P9V-1, `caddy adapt` 증거 `evidence/20261114-1406-plan-verify-caddy-order.txt`) · `handle { root * /srv; try_files {path} /index.html; file_server }` · `header /sw.js Cache-Control "no-cache"` · `header /index.html Cache-Control "no-cache"` · `header /manifest.webmanifest Content-Type "application/manifest+json"`(Caddy 의 확장자 MIME 표에 `.webmanifest` 가 있는지 확인하지 않았다 — 명시로 S4 를 보장) · `header -Server`. HTTP→HTTPS 리다이렉트·인증서 발급·갱신은 Caddy 기본 동작(로컬 스모크는 `SITE_ADDRESS=:80` 이라 HTTP 만).
- `.dockerignore` — `.env`·`.env.*` · `.git` · `.venv` · `**/__pycache__` · `web/node_modules` · `web/dist` · `docs` · `tests` · `evaluation` · `reports` · `data` · `.claude` · `*.pem` · `*.key`. 빌드 문맥에 비밀이 들어가지 않는 것이 "이미지에 비밀 값 0" 의 근거.
- `tests/test_deploy_files.py` — 배포 파일 텍스트 검사(DB·Docker·PyYAML 불필요, `encoding="utf-8"`, skip 0). 항목은 U1 참고.
- (결정 H (i)) `.github/workflows/tests.yml` 에 job `deploy-smoke` 추가(새 파일 아님).
- `docs/user-setup/11-ec2-minimal-deploy.md` · `docs/user-setup/12-shutdown.md`.
- `docs/wiki/packages/P9-infra/tests.md`(테스트 1건 = 1줄, 단위마다 누적) · `03-log.md` · `evidence/*.txt`.

**고치는 기존 파일**

| 파일 | 고치는 내용 | 단위 |
|---|---|---|
| `.env.example` | 운영 compose 전용 이름 줄 추가(값 없음): `SITE_ADDRESS=` + 주석("운영 `docker-compose.prod.yml` 전용 — Caddy 호스트명, 로컬 개발은 쓰지 않음"). R-U10D-5 의 미사용 이름 3개(`APP_ENV`·`EMBEDDING_MODEL`·`EMBEDDING_PROVIDER`)에 "코드가 읽지 않음" 주석. `GIT_SHA`·`APP_ENV_FILE`·`CADDY_HTTP_PORT`·`CADDY_HTTPS_PORT` 는 셸에서 주는 값이라 넣지 않는다(11 문서에 적음) | U1 |
| `.github/workflows/tests.yml` | 결정 H (i) 이면 `deploy-smoke` job 1개(아래 U1b) | U1b |
| `docs/user-setup/README.md` | 11·12 목록 줄 | U3 |
| `docs/wiki/security.md` §1 12행 · §5 66행 | "배포는 SSM Parameter Store" → "배포는 서버 `.env`(사용자가 EC2 에 직접 올림, D17 4)" · "VAPID 개인키는 환경변수/SSM" → "환경변수(서버 `.env`)" | U3 |
| `SERVER-CHECKLIST.md` 8행 | 배포 구성 줄을 D17(EC2 1대 + compose, Caddy, CloudFront·RDS·SSM 없음)로 + "1-6 CloudFront 행은 해당 없음" 한 줄 | U3 |
| `docs/user-setup/05-server-secrets.md` | 상단 안내 한 줄(SSM 대신 서버 `.env`, 11 문서 참조) — 파일에 SSM 절차가 있으면 | U3 |
| `docs/RUNNING.md` | "운영 compose(P9)" 짧은 절 — 11 문서로 가는 링크와 로컬 스모크 명령만 | U3 |
| `docs/wiki/registry.md` | U1·U1b·U3 새 행, 42행(`docker-compose.yml`) 비고 "P9: 운영은 `docker-compose.prod.yml` 별도, RDS 재확인 소멸" | U3 |

## 작업 단위 (단위 하나 = 커밋 하나. 끝나면 /commit. 단위마다 verifier 커밋 전 리뷰)

순서: **U1 ∥ U2(동시 — 파일 겹침 없음)** → U1b(결정 H (i) 일 때) → U3 → 04-review 준비 완료 → **[사용자 지시] U4** → 04-review → 사용자 완성 확인 → 승격 → 11-19 종료 절차 실행 기록.

- [ ] U1 **[backend-agent] 배포 파일 5종 + 텍스트 검사 테스트 + 로컬 compose 스모크** / Refs: P9-infra D17 R14 R-U10D-1 R-U10D-2 R-U10D-4 R-U10D-5 R-U10D-9 원칙8 security
  - 만든다: `Dockerfile` · `docker/entrypoint.sh` · `docker-compose.prod.yml` · `Caddyfile` · `.dockerignore` · `tests/test_deploy_files.py` · `.env.example` 이름 줄. **`app/`·`web/`·`alembic/`·`docker-compose.yml` 은 건드리지 않는다.** 사실 3(secret-guard 의 DB URL 패턴)을 위임 프롬프트에 인용한다.
  - 로컬 스모크 변수 파일: 스크래치패드에 Write 로 `p9-smoke-vars.txt` 를 만든다(값은 비밀이 아닌 스모크 전용: `POSTGRES_USER=app` · `POSTGRES_PASSWORD=p9smokelocalonly` · `POSTGRES_DB=relationship` · `SITE_ADDRESS=:80` · `BRIEFING_SCHEDULER_ENABLED=1` · `APP_USER_ID=p9-smoke`. **LLM·VAPID 키 없음**). 사용자의 `.env` 는 읽지도 참조하지도 않는다(사실 12). 이 파일은 compose 보간(`--env-file`)과 백엔드 `env_file`(`APP_ENV_FILE`) 둘 다에 쓴다.
  - 로컬 스모크 순서(아래 판정 표의 명령 그대로, 전부 `save_evidence.py`): ① `docker compose … config --quiet` ② `up -d --build` ③ 백엔드 healthy 대기(`docker compose … ps`) ④ `curl -fsS http://localhost:8088/api/health` → `status ok`·`db up`·`alembic_revision` == `python3 -m alembic heads` ⑤ `/` 200 `text/html` ⑥ `/api/persons` 200 `[]` ⑦ S4 헤더(`/sw.js`·`/manifest.webmanifest`·`/assets/<해시>.js`) ⑧ S10 `/api/docs`·`/api/openapi.json`·`/api/redoc` 404 ⑨ 부정: `/health` 가 JSON 이 아님(`text/html`, SPA fallback) ⑩ S7 `docker compose … exec -T backend python -m alembic current`·`check` ⑪ S13 2분 대기 뒤 `docker compose … exec -T postgres psql -U app -d relationship -tAc "SELECT count(*) FROM agent_traces WHERE step='briefing_run'"` ≥ 1 ⑫ S17 포트: `docker compose … ps --format '{{.Service}} {{.Ports}}'` 에서 `postgres`·`backend` 에 호스트 포트 없음 ⑬ `docker compose … logs --tail=200 backend` 에 Traceback 0 ⑭ `docker compose … down`(**`-v` 없음** — 볼륨 `relationship-prod_pgdata` 는 남긴다, 삭제는 사용자). 로컬 포트는 `CADDY_HTTP_PORT=8088`·`CADDY_HTTPS_PORT=8443`(80/443 충돌 회피). 개발 DB(5433, 프로젝트 `relationship`)가 스모크 전후로 그대로인지 `docker compose -f docker-compose.yml ps` 로 기록(사실 6 회귀).
  - 아키텍처 기록: 로컬 Mac 이 ARM 이면 이미지는 arm64 로 빌드된다(결정 A 가 t4g 면 운영과 같다). `docker image inspect relationship-backend:local --format '{{.Architecture}}'` 를 증거로. 결정 A 가 x86(t3) 이면 amd64 빌드는 U1b CI(ubuntu)가 본다.
  - 테스트 `tests/test_deploy_files.py`(텍스트 검사 — 서비스 블록은 들여쓰기로 잘라 본다):
    ① compose 최상위 `name: relationship-prod` 존재 ② 서비스 `caddy`·`backend`·`postgres` 셋 다 존재 ③ `postgres` 블록에 `ports:` 0 ④ `backend` 블록에 `ports:` 0 ⑤ `postgres` 블록에 `env_file` 0, `backend` 블록에 `env_file` 1 ⑥ 비밀 값 0: compose·Caddyfile·Dockerfile·entrypoint 에 `POSTGRES_PASSWORD` 의 리터럴 값(`${…}` 보간이 아닌 값)·`:-` 기본값 0, 32자 이상 영숫자 덩어리 0, OpenAI·Anthropic 키 접두 패턴 0, PEM 개인키 머리줄 0, `<user>:<password>@` 꼴 DB URL 0 ⑦ `POSTGRES_USER`·`POSTGRES_PASSWORD`·`POSTGRES_DB`·`SITE_ADDRESS` 보간이 `:?` 형태(없으면 기동 거부) ⑧ `restart: unless-stopped` 가 세 서비스 모두 ⑨ 볼륨 `pgdata`·`caddy_data` 선언 + 각 서비스에 마운트 ⑩ `backend` `DATABASE_URL` 이 `@postgres:5432/` 를 가리키고 스킴 뒤 사용자 부분에 `:` 가 없다(비밀번호 없는 URL, 사실 2) + `backend` `environment` 에 `POSTGRES_PASSWORD` 보간 ⑪ Caddyfile: `{$SITE_ADDRESS}` 존재·호스트명 리터럴(`.sslip.io`·`.nip.io`·`.com` 등) 0 · `handle_path /api/*` 블록 안에 `reverse_proxy backend:8000` · `try_files {path} /index.html` · `file_server` · `/sw.js` 의 `no-cache` · (결정 M (i)) `respond @docs 404`(또는 `respond … 404`) 줄이 **`handle_path /api/*` 블록 안**에 있고 같은 블록의 `reverse_proxy` 줄보다 **앞**에 있으며, 매처는 접두 없는 `/docs*`·`/redoc*`·`/openapi.json`(F-P9V-1) ⑫ entrypoint: `set -e`(또는 `set -eu`) · `alembic upgrade head` 줄이 `uvicorn` 줄보다 앞 · `exec` · `--workers 1` · `app.main:app` ⑬ Dockerfile: 단계 `backend`·`caddy`·`web-build` 존재 · `backend` 단계 마지막 `USER` 가 root 가 아님 · 기반 이미지 `python:3.13-slim`·`node:24-slim`(결정 F) · `COPY` 대상에 `.env` 0 · `npm ci` 앞에 `NODE_ENV=production` 0 ⑭ `.dockerignore` 에 `.env`·`.git`·`web/node_modules` 줄 ⑮ `.env.example` 에 `SITE_ADDRESS=` 이름 줄이 있고 값이 비었음.
  - 변이 → 잡는 테스트: V1-1 `postgres` 에 `ports: ["5432:5432"]` 추가 → ③ (+ 스모크 ⑫) · V1-2 `backend` 에 `ports: ["8000:8000"]` → ④ · V1-3 `POSTGRES_PASSWORD` 리터럴 값 또는 `:-` 기본값 → ⑥⑦ · V1-4 entrypoint 에서 `alembic upgrade head` 삭제 또는 uvicorn 뒤로 → ⑫ (+ 스모크 ④ `alembic_revision` null/503) · V1-5 `handle_path` → `handle`(접두 안 뗌) → ⑪ (+ 스모크 ④ 404) · V1-6 `--workers 2` → ⑫ · V1-7 `name:` 삭제(개발 볼륨 공유) → ① · V1-8 `.dockerignore` 에서 `.env` 삭제 → ⑭ · V1-9 `USER app` 삭제 → ⑬ · V1-10 Caddyfile 에 호스트명 하드코딩 → ⑪ · V1-11 `caddy_data` 볼륨 삭제(인증서 재발급) → ⑨ · V1-12 `/sw.js` no-cache 헤더 삭제 → ⑪ (+ 스모크 ⑦) · V1-13 `postgres` 에 `env_file` 추가 → ⑤ · V1-14 docs 차단 삭제 → ⑪ (+ 스모크 ⑧) · V1-14b 404 `respond` 를 `handle_path` 블록 밖 최상위로 옮김(또는 `reverse_proxy` 뒤로) → ⑪ (+ 스모크 ⑧ `/api/docs` 200 으로 실패 — F-P9V-1 재현) · V1-15 `backend` `environment` 에서 `POSTGRES_PASSWORD` 삭제 → ⑩ (+ 스모크 ④ `db down` — 단 `env_file` 에도 있으면 스모크는 통과하므로 테스트가 유일한 방어). 변이는 스크래치패드 사본에 대해 테스트의 경로 상수를 바꿔 돌리거나, 작업 트리에서 Edit → FAIL 기록 → 되돌림(되돌린 뒤 `git diff` 증거). secret-guard 에 걸리는 변이(V1-3 의 일부)는 사본 방식으로만. 방식은 backend-agent 가 03-log 에 적는다.

- [ ] U1b **[backend-agent] CI 이미지 빌드 + compose 헬스 스모크 job (결정 H (i) 확정)** / Refs: P9-infra D17 R-U10D-1 원칙8 / 의존: U1 커밋
  - `.github/workflows/tests.yml` 에 job `deploy-smoke`(ubuntu-latest, timeout 15분): 체크아웃 → 러너 임시 디렉터리(`$RUNNER_TEMP`)에 스모크 변수 파일 생성(U1 과 같은 비밀 없는 값) → `docker compose --env-file "$RUNNER_TEMP/p9-smoke-vars.txt" -f docker-compose.prod.yml config --quiet` → `up -d --build --wait`(헬스체크 대기) → `curl -fsS http://localhost:8088/api/health` 에 `"db":"up"` → `curl -fsS -o /dev/null http://localhost:8088/` → `down`. 실패 시 `docker compose … logs --tail=200` 출력. 비밀·`secrets.*` 사용 0.
  - 기존 job(`pytest`·`windows`·`web`)은 건드리지 않는다. ruff 대상 변경 없음(새 Python 파일은 `tests/` 안).
  - 판정: 이 단위 커밋을 dev2 에 푸시한 뒤 run 의 `deploy-smoke` `success`(메인 세션이 `gh run list --branch dev2 --limit 3` · `gh run view <id>` 를 `save_evidence.py` 로 저장). amd64 빌드 증거를 겸한다(결정 A 가 x86 일 때 중요).
  - 테스트: `tests/test_deploy_files.py` 에 ⑯ 추가 — `tests.yml` 에 `deploy-smoke` job 이 있고 그 안에 `docker-compose.prod.yml` 과 `/api/health` 가 등장, `secrets.` 0.
  - 변이 → 잡는 것: V1b-1 job 삭제 → ⑯ · V1b-2 job 이 `docker-compose.yml`(로컬 DB 파일)을 가리킴 → ⑯ · V1b-3 Caddyfile `handle_path` 오타 → CI run `failure`(헬스 404).

- [ ] U2 **[frontend-agent] 빌드 산출물·`/api` 규약·PWA 루트 경로 확인 (기대 코드 변경 0)** / Refs: P9-infra D17 R-U10D-2 원칙5 / 의존: 없음(U1 과 동시)
  - `web/` 만 본다·쓴다(frontend-agent 규칙). `Dockerfile`·`Caddyfile` 은 U1(backend) 몫 — 고칠 점이 있으면 03-log 에 적어 U1 리뷰에서 반영.
  - 확인(증거): `npm ci && npm run build` 성공 · `web/dist/` 최상위에 `index.html`·`sw.js`·`manifest.webmanifest`·`assets/` · `dist/index.html` 의 자산 경로가 `/assets/…`(루트 기준) · `vite.config.ts` 에 `base` 없음 · `src/api/client.ts` `API_BASE === '/api'` · 서비스 워커 등록 경로 `'/sw.js'`·scope `/` · manifest `scope:"/"`·`start_url:"/#/chat"` · `npm run typecheck`·`npx vitest run` 통과(기준선 대비 증감 0) · 라우팅이 해시 기반(`/#/…`)이라 SPA fallback 은 보험임을 03-log 에 한 줄.
  - 고칠 점이 나오면(예: `sw.js` 가 `dist` 최상위에 없음) **`web/src/` 변경이 되는 수정은 이 단위에서 하지 않는다** — 수용 기준 "제품 코드 무변경" 과 충돌하므로 메인 세션에 보고해 사용자 결정(FIX 분리 또는 CR)을 받는다. `web/public/`·`web/vite.config.ts` 처럼 `web/src/` 밖이면 최소 수정 + Vitest 1건까지 허용 — 단 `web/public/`(sw.js·manifest)은 제품 산출물이므로 수정이 생기면 03-log U2 항목과 04-review 에 "제품 산출물 변경" 으로 따로 표시한다(F-P9V-4; 판정 표의 `git diff -- app web/src alembic` 는 이를 보지 못한다).
  - 변이 → 잡는 확인: V2-1 `vite.config.ts` 에 `base: '/web/'` → `dist/index.html` 자산 경로 grep 이 `/web/assets` 로 바뀌어 판정 실패 · V2-2 `API_BASE` 를 `''` 로 → 기존 `api.test.ts` 실패(되돌림 확인까지).

- [ ] U3 **[메인 세션] 사용자 문서 11·12 + registry + security·SERVER-CHECKLIST 문구** / Refs: P9-infra D17 security R-U10D-3 R-U10D-5 / 의존: U1(파일·변수 이름이 확정돼야 문서가 맞다), U1b·U2 결과 반영, **U4 보다 먼저**(사용자가 이 문서로 콘솔 작업을 한다)
  - `docs/user-setup/11-ec2-minimal-deploy.md` — 단계마다 "끝났다는 증거"(이름·상태만, 계정 ID·키 값 금지):
    1. **계정**: 신규 AWS 계정 가입(Free Plan — 크레딧 금액·기간·적격 인스턴스는 가입 화면 aws.amazon.com/free 에서 재확인해 표에 메모) · 루트 MFA · 관리자 IAM 사용자(또는 Identity Center) + MFA, 이후 루트 미사용 · **비상업·개인 학습** 용도 명시.
    2. **Budgets**: 02 카드대로(결정 I) — **EC2 생성 전에.** 크레딧이 비용을 상쇄해 "실제 비용" 알림이 늦게 울릴 수 있으므로 Budgets 고급 옵션에서 크레딧 포함 여부를 확인(리스크 절). OpenAI 대시보드 월 지출 한도 설정.
    3. **리전** 결정 C → **키 페어**(결정 D (i) 이면 ed25519, `.pem` 은 사용자 PC 에만, 권한 600) → **보안 그룹**: 인바운드 80·443 `0.0.0.0/0`(+`::/0`), 22 는 "내 IP"/32 만(결정 D) — 5432·8000 규칙 없음.
    4. **EC2 생성**: 결정 A 인스턴스, Ubuntu Server 24.04 LTS(결정 A 아키텍처에 맞는 arm64/x86_64 AMI), 루트 EBS gp3 20GB(종료 시 삭제 체크 기본값 유지 확인), 기본 VPC 퍼블릭 서브넷.
    5. **Elastic IP** 할당·연결(호스트명이 IP 에 묶이므로 필수).
    6. **Docker 설치**: Docker 공식 apt 저장소 방식(`curl … | sh` 금지 — security §3) + compose 플러그인, `ubuntu` 사용자 docker 그룹, `systemctl is-enabled docker` = enabled. (결정 A 가 1GB 면) 스왑 2GB 생성.
    7. `git clone https://github.com/SunWoo1213/Relationship.git` → 배포할 커밋 checkout(메인 세션이 알려 준 해시 — 04-review 대상).
    8. **`.env` 작성**(서버에서 사용자가 직접, 권한 600): 이름 표(값 없음) — `POSTGRES_USER`·`POSTGRES_PASSWORD`(생성 예: `openssl rand -hex 24`)·`POSTGRES_DB`·`SITE_ADDRESS`·`OPENAI_API_KEY`·`OPENAI_MODEL`·`LLM_PROVIDER`·`LLM_PROVIDERS_ENABLED`·`VAPID_PUBLIC_KEY`·`VAPID_PRIVATE_KEY`·`VAPID_SUBJECT`·`APP_USER_ID`·`APP_TIMEZONE`·`BRIEFING_SCHEDULER_ENABLED=1` + 결정 K 의 나머지 · **넣지 않는 것**: `DATABASE_URL`(compose 가 덮어씀 — 넣어도 무시되지만 혼동 방지)·`PUSH_DEV_PAGE_ENABLED`(결정 K)·`POSTGRES_PORT`·`POSTGRES_HOST`·Anthropic/Gemini 키(결정 K). VAPID 키 쌍 생성 방법(결정 N, 사용자 터미널, 값은 화면과 `.env` 에만).
    9. **호스트명**(결정 B): 보유 도메인이면 A 레코드 → EIP · 없으면 `<EIP 를 대시로>.sslip.io`(예: `3-35-10-20.sslip.io`) — 확인 `dig +short <호스트명>` == EIP.
    10. **기동**: `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build` → `docker compose -f docker-compose.prod.yml ps`(세 서비스 running/healthy) → `logs --tail=100 caddy` 에 인증서 발급 성공 줄 → `logs --tail=200 backend` Traceback 0.
    11. **스모크**: 아래 판정 표 U4 행 명령 목록(에이전트가 돌릴 GET 과 사용자가 돌릴 것 구분).
    12. **데모 5단계** — README "데모 시나리오 (3분)"·SERVER-CHECKLIST §5 그대로, 발표 직전 한 번 열어 데우기.
    13. **갱신**: `git fetch && git checkout <해시>` → 10번 명령 재실행(마이그레이션은 entrypoint 가 자동). 되돌리기 = 직전 해시로 같은 명령(SERVER-CHECKLIST 0-4·§6).
    14. **평가 직전 기억 초기화가 필요하면**: `.env` 의 `APP_USER_ID` 를 새 값으로 바꾸고 `up -d`(빈 기억으로 시작 — `DROP`/`TRUNCATE`·`down -v` 없이, security §4. F-fbaaae: 모든 방문자가 같은 기억을 공유한다).
    15. **로그**: `docker compose -f docker-compose.prod.yml logs --tail=200 <서비스>` 만(결정 L). 외부 전송 없음.
    16. **비상시**: 서버가 응답하지 않으면 발표는 로컬 실행(`docs/RUNNING.md`)으로.
  - `docs/user-setup/12-shutdown.md` — 실행 시각 = 결정 J. 항목마다 "확인 방법"·"실행 시각·결과" 칸:
    1. 종료 직전 백업: 서버에서 `docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -Fc -U <user> <db> > ~/relationship-final.dump` → 사용자 PC 로 내려받기(사용자 `scp`) — 저장소에 넣지 않는다(제3자 개인정보, security §5). 확인: 로컬 파일 크기 > 0, `pg_restore --list` 가 테이블 목록을 낸다.
    2. `docker compose -f docker-compose.prod.yml down`(선택 — 인스턴스 종료로 함께 사라진다).
    3. EC2 인스턴스 **종료(terminate)** — 확인: 상태 `terminated`.
    4. EBS: 볼륨 목록에 이 인스턴스의 `available` 볼륨 0(루트 볼륨 종료 시 삭제 설정이었는지 포함) · 스냅샷 0.
    5. Elastic IP **해제(release)** — 확인: EIP 목록 0(연결 안 된 EIP 도 과금).
    6. 보안 그룹·키 페어 삭제(콘솔) + 사용자 PC 의 `.pem` 삭제.
    7. 도메인을 썼으면 A 레코드 삭제(sslip.io 는 할 일 없음).
    8. 비밀 회전: OpenAI 키 폐기·재발급(로컬 `.env` 는 새 키로), 배포용 VAPID 키 폐기(결정 N (i) 이면 로컬 영향 없음).
    9. 유지하는 것: AWS Budgets 알림·계정(크레딧 잔여 — 6개월 뒤 Free Plan 종료 안내 확인).
    10. 확인 명령: `curl -sS -m 5 -o /dev/null -w '%{http_code}' https://<호스트명>/` 이 연결 실패(000) · Billing 의 EC2·EBS·퍼블릭 IPv4 사용량이 종료 시각 뒤 증가 0(다음 날 확인).
  - `security.md` §1·§5 문구 · `SERVER-CHECKLIST.md` 8행 · `05-server-secrets.md` 상단(있으면) · `docs/RUNNING.md` 운영 compose 절 · `registry.md` 행 · `docs/user-setup/README.md` 목록.
  - 판정: 아래 표 #6(종료 체크리스트) · 결정 확정 뒤 11 문서에 결정 A·B·C·D 의 확정값이 들어갔는지 `grep`.

- [ ] U4 **[사용자 + 메인 세션] 실제 기동·스모크 S1~S17(치환본)·데모 5단계·03-log — 사용자가 "띄워 달라" 고 지시한 뒤에만** / Refs: P9-infra D17 R14 R-U10D-1~4 R-U10D-8 R-U10D-9 R-U10D-10 원칙8 / 의존: U1~U3 커밋 + 사용자 지시
  - 사용자: 11 문서 1~10단계(계정·Budgets·EC2·`.env`·호스트명·기동).
  - 메인 세션: 판정 표의 "에이전트" 행(배포 URL 에 본문 없는 GET·`-I`)을 `save_evidence.py` 로 실행, "사용자" 행(SSH 안 명령·`curl -d`·브라우저·콘솔)은 사용자가 준 출력을 Write 로 `evidence/<시각>-u4-*.txt` 에(비밀·계정 정보가 없는지 저장 전에 읽는다). 실패하면 재시도 남발 대신 `findings.py` 소견(원칙8) → 원인이 배포 파일이면 U1 FIX, 제품 코드면 사용자 보고.
  - 데모 5단계는 배포 URL 에서, 단계마다 화면 결과·응답 시간을 적는다. 승진 호칭 변이 단계에서 확인 없이 자동 병합되면 원칙1 위반 — 승격하지 않는다(SERVER-CHECKLIST §5·§6).
  - 종료 절차 실행(결정 J 시각)은 04-review 뒤의 일이다 — 03-log·journal 에 항목별 확인 결과를 남기고, 실행될 때까지 HANDOFF 에 "종료 절차 미실행" 을 남긴다.

## 판정 방법

명령은 저장소 루트에서. 증거 저장은 `python3 .claude/scripts/save_evidence.py P9-infra <이름> -- <명령>`. 환경변수는 래퍼 **앞**에 둔다(`env …` 금지). 공백 있는 `-k` 식은 따옴표가 사라지므로 토큰 하나로 쓴다. **따옴표·`$`·`|`·`(` 가 든 안쪽 명령(F-P9V-2)** — `save_evidence.py` 는 `--` 뒤 인자를 공백으로 이어 `bash -c` 로 돌리므로 `ps --format '{{…}}'`·`python -c "…"`·`psql -tAc "…"`·`curl -w '%{http_code}'`·`git grep -nIE '(A|B)'` 는 그대로 넘기면 깨진다. 우회 두 가지 중 하나: ① 바깥 따옴표로 한 번 더 감싸기(`"'{{.Service}} {{.Ports}}'"`) ② 안쪽 명령을 스크래치패드 `<SCR>/u1-<이름>.sh` 로 Write 해 두고 `-- bash <SCR>/u1-<이름>.sh`. `alembic heads` 는 `.venv/bin/python -m alembic heads`(시스템 python3 에는 alembic 이 없다). 기호:
- `<SCR>` = 스크래치패드 절대 경로, `<V>` = `<SCR>/p9-smoke-vars.txt`.
- `<DC>` = `docker compose --env-file <V> -f docker-compose.prod.yml` — 로컬 스모크 명령 앞에는 항상 `APP_ENV_FILE=<V> CADDY_HTTP_PORT=8088 CADDY_HTTPS_PORT=8443` 를 래퍼 앞에 붙인다(예: `APP_ENV_FILE=<V> CADDY_HTTP_PORT=8088 CADDY_HTTPS_PORT=8443 python3 .claude/scripts/save_evidence.py P9-infra u1-smoke-up -- docker compose --env-file <V> -f docker-compose.prod.yml up -d --build`).
- `<URL>` = U4 에서 정해지는 `https://<호스트명>` — 증거 파일에 그대로 남는다(비밀 아님).
- "사용자" 행은 사용자가 직접 실행하고(SSH 안·`curl -d`·브라우저·콘솔) 출력을 메인 세션이 Write 로 `evidence/` 에 저장한다(사실 11).

### 수용 기준 구절별

| # | 수용 기준 구절 | 판정 | 명령 / 점검 | 실행 | 단위 |
|---|---|---|---|---|---|
| 1 | 배포 URL(HTTPS)에서 데모 시나리오 5단계 재현 | 사람 | `<URL>/#/chat` 에서 5단계(첫 언급 → 사건 누적 → 승진 호칭 변이 → 일정 등록 → 브리핑 웹푸시 + 수동 트리거). 단계마다 결과·응답 시간 → `evidence/<시각>-u4-demo5.txt`. 3단계는 ER 판정(병합 또는 `ask_user` 칩)이 카드와 맞는지, 5단계는 "지금 브리핑" → 알림 수신. HTTPS 는 S3 행 | 사용자 | U4 |
| 2 | `git diff --stat -- app web/src alembic` 빈 출력(제품 코드 무변경) | 기계 | `python3 .claude/scripts/save_evidence.py P9-infra u<N>-product-unchanged -- git diff --stat <기준>..HEAD -- app web/src alembic` → 빈 출력. 단위마다 + 04-review 전 1회 | 에이전트 | 전 단위 |
| 3 | `postgres` 호스트 포트 미노출 | 기계 | `test_deploy_files.py` ③④ · 로컬 `… u1-smoke-ports -- <DC> ps --format '{{.Service}} {{.Ports}}'` 에서 `postgres`·`backend` 줄에 `0.0.0.0:`/`->` 0 · 배포: 사용자 서버 `sudo ss -tlnp` 에 5432·8000 LISTEN 0 + 사용자 PC `nc -vz -w 3 <EIP> 5432` 실패 | 에이전트 + 사용자 | U1·U4 |
| 4 | 저장소·compose 파일에 비밀 값 0 | 기계 | `test_deploy_files.py` ⑥⑦⑩⑭ · `… u1-secret-grep -- git grep -nIE '(PASSWORD|SECRET|API_KEY|PRIVATE_KEY)[[:space:]]*[:=][[:space:]]*[^$[:space:]{]' -- Dockerfile docker-compose.prod.yml Caddyfile docker/entrypoint.sh .dockerignore` → 일치 0(exit 1 이 기록됨) · Write 단계의 `secret-guard`·`save_evidence.py` 내장 비밀 검사 통과 · 이미지: `… u1-image-noenv -- docker run --rm --entrypoint sh relationship-backend:local -c 'ls -a /app'` 에 `.env` 없음 | 에이전트 | U1 |
| 5 | 로컬에서 `docker compose -f docker-compose.prod.yml up --build` 스모크(`/api/health` 200, 정적 `/` 200) | 기계 | `… u1-smoke-up -- <DC> up -d --build` → `… u1-smoke-health -- curl -fsS http://localhost:8088/api/health` → `{"status":"ok","db":"up","alembic_revision":"<head>"}` 이고 `… u1-alembic-heads -- python3 -m alembic heads` 와 같음 → `… u1-smoke-root -- curl -fsS -o /dev/null -w '%{http_code} %{content_type}' http://localhost:8088/` → `200 text/html…` → `… u1-smoke-persons -- curl -fsS http://localhost:8088/api/persons` → `[]` | 에이전트 | U1 |
| 6 | 종료 체크리스트 문서 존재 | 기계 | `python3 .claude/scripts/save_evidence.py P9-infra u3-shutdown-doc -- grep -nE 'pg_dump|terminate|종료|EBS|Elastic IP|EIP|보안 그룹|회전|VAPID|OpenAI' docs/user-setup/12-shutdown.md` → 백업·인스턴스·EBS·EIP·보안 그룹·회전 6항목 각각 1줄 이상 | 에이전트 | U3 |
| 7 | 아래 유효성 점검 중 compose·Caddy 대응 항목(RDS·CloudFront 항목은 치환) | 기계·사람 | 아래 치환 표 S1~S15 + 추가 S16·S17 | 표대로 | U1·U1b·U4 |

### 단위 공통 회귀 (단위마다, 리뷰 전)

| 항목 | 명령 | 기대 |
|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 python3 .claude/scripts/save_evidence.py P9-infra u<N>-pytest-all -- python3 -m pytest -q` | 기준선(메인 확정값, 2202 예상) + 새 테스트 수, **skip 0** |
| 새 테스트 | `python3 .claude/scripts/save_evidence.py P9-infra u1-deploy-files -- python3 -m pytest tests/test_deploy_files.py -q` | 전부 passed |
| ruff | `python3 .claude/scripts/save_evidence.py P9-infra u<N>-ruff -- python3 -m ruff check app tests scripts evaluation` | 통과 |
| mypy | `python3 .claude/scripts/save_evidence.py P9-infra u<N>-mypy -- python3 scripts/mypy_check.py --run` | 새 오류 없음(기준선 38) |
| 툴 7종 | `POSTGRES_PORT=5433 python3 .claude/scripts/save_evidence.py P9-infra u<N>-tools-check -- python3 scripts/tools_check.py` | 7/7 |
| 제품 코드 무변경 | 위 #2 | 빈 출력 |
| 기존 테스트 무수정 | `python3 .claude/scripts/save_evidence.py P9-infra u<N>-tests-unmodified -- git diff --stat <기준> -- tests/` | 새 파일만, 기존 파일 변경 0 |
| 범위 | `python3 .claude/scripts/save_evidence.py P9-infra u<N>-scope -- git diff --name-only <기준>` | 그 단위 산출물 표의 파일만 |
| compose 문법 (U1) | `APP_ENV_FILE=<V> python3 .claude/scripts/save_evidence.py P9-infra u1-compose-config -- docker compose --env-file <V> -f docker-compose.prod.yml config --quiet` | exit 0(값을 출력하지 않는 `--quiet`) |
| 필수 변수 누락 시 거부 (U1) | `python3 .claude/scripts/save_evidence.py P9-infra u1-compose-required -- docker compose --env-file /dev/null -f docker-compose.prod.yml config --quiet` | exit ≠ 0, 메시지에 첫 `:?` 변수 이름 |
| 개발 DB 무영향 (U1) | `python3 .claude/scripts/save_evidence.py P9-infra u1-dev-compose-ps -- docker compose -f docker-compose.yml ps` 를 스모크 전·후 + `… u1-compose-ls -- docker compose ls` + `… u1-volume-ls -- docker volume ls` 전·후(F-P9V-3) | 두 출력의 개발 `postgres` 컨테이너 ID·상태 동일 · `docker compose ls` 에 `relationship-prod` 가 새로 생기고 기존 프로젝트(현재 개발 DB 는 `capstone2`, 볼륨 `capstone2_pgdata`; 옛 `relationship_pgdata` 도 존재)는 그대로 · 새 볼륨은 `relationship-prod_*` 만 |
| 프론트 (U2) | `python3 .claude/scripts/save_evidence.py P9-infra u2-build -- npm --prefix web run build` · `… u2-vitest -- npm --prefix web exec -- vitest run` · `… u2-typecheck -- npm --prefix web run typecheck` · `… u2-dist-paths -- grep -o 'src="/assets/[^"]*"' web/dist/index.html` | 성공, Vitest 증감 0, 자산 경로 루트 기준 |

### 배포 유효성 점검 치환 표 (review-u10 §9 S1~S15 → compose·Caddy) — 결정 P

| # | 원안 (D7 풀구성) | 치환 (AWS 최소) | 명령 · 판정 기준 | 실행 | 단위 |
|---|---|---|---|---|---|
| S1 | `docker build/run` + compose postgres + `/health` (CI 에) | **로컬 compose 스모크 + (결정 H) CI `deploy-smoke`** | 위 #5 전부 + `… u1-smoke-backend-health -- <DC> exec -T backend python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"` → 같은 본문 · `… u1-image-arch -- docker image inspect relationship-backend:local --format '{{.Architecture}}'` · U1b run `deploy-smoke` `success` | 에이전트 | U1·U1b |
| S2 | CloudFront 경로 + Caddy 접두 제거 | **Caddy `handle_path /api/*`** | `… u4-s2-health -- curl -fsS <URL>/api/health` → 200 + 위 본문, `alembic_revision` == heads · 부정: `… u4-s2-noprefix -- curl -s -o /dev/null -w '%{http_code} %{content_type}' <URL>/health` → `text/html`(SPA fallback, JSON 아님). 로컬 같은 쌍: `u1-smoke-health`·`u1-smoke-noprefix`(`http://localhost:8088`) | 에이전트 | U1·U4 |
| S3 | ACM·CloudFront TLS | **Caddy 자동 HTTPS(Let's Encrypt, 실패 시 Caddy 기본 대체 발급자)** | `… u4-s3-tls -- curl -fsS -o /dev/null -w '%{http_code} %{ssl_verify_result}' <URL>/`(`-k` 없음) → `200 0` · `… u4-s3-redirect -- curl -sI http://<호스트명>/` → `308`(또는 301) + `location: https://` · 사람: 브라우저 자물쇠·발급자 이름 1줄 | 에이전트 + 사용자 | U4 |
| S4 | S3 MIME·캐시 | **Caddy `file_server` + `header` 지시문** | `… u4-s4-sw -- curl -sI <URL>/sw.js` → `content-type` 에 `javascript`, `cache-control` 에 `no-cache` · `/manifest.webmanifest` → `application/manifest+json` · `/` → `text/html` · `/assets/<해시>.js` 1개 200(파일명은 `/` 본문에서). 로컬 같은 4개: `u1-smoke-s4-*` | 에이전트 | U1·U4 |
| S5 | 읽기 계약(LLM 0) | 같음 | `… u4-s5-<경로> -- curl -fsS <URL>/api/persons` 등 4개(`/api/persons`·`/api/briefings`·`/api/questions/pending`(헤더 없음 → `[]`)·`/api/push/vapid-public-key`(200)) → 저장한 JSON 을 스크래치패드 스크립트로 `app.api.schemas` 모델 `model_validate`. 로컬은 #5 의 `/api/persons` 로 갈음 | 에이전트 | U4 |
| S6 | 쓰기 계약 1회(실 LLM) | 같음 | 사용자: `curl -s -w '\n%{time_total}' -X POST -H 'Content-Type: application/json' -d '{"utterance":"<고정 문장>"}' <URL>/api/chat` → 200, `ChatOut` 모양, `trace_ids` 비지 않음, 응답 시간 기록(R-U10D-8). 답 내용은 단언하지 않는다 | 사용자 | U4 |
| S7 | RDS 마이그레이션 주체·확장 권한 | **entrypoint `alembic upgrade head`(compose Postgres 슈퍼유저)** | 로컬: `… u1-smoke-alembic-current -- <DC> exec -T backend python -m alembic current` == heads · `… u1-smoke-alembic-check -- <DC> exec -T backend python -m alembic check` → `No new upgrade operations detected.` · `… u1-smoke-vector -- <DC> exec -T postgres psql -U app -d relationship -tAc "SELECT extversion FROM pg_extension WHERE extname='vector'"` 1행. 배포: 같은 세 명령을 사용자가 서버에서(`-U`·`-d` 는 서버 `.env` 의 이름 값) | 에이전트 + 사용자 | U1·U4 |
| S8 | RDS 접속 SSL | **DB 경로가 외부에 없음을 판정**(compose 내부 네트워크, TLS 대상 아님 — security §5 개정 ②) | S17 과 #3(호스트 포트 0·보안 그룹 5432 규칙 0·외부 `nc` 실패). `pg_stat_ssl` 은 `f` 가 정상이므로 기대값으로 쓰지 않는다 | 에이전트 + 사용자 | U1·U4 |
| S9 | 환경변수 ↔ SSM | **환경변수 ↔ 서버 `.env` 이름 목록** | 사용자 서버: `cut -d= -f1 .env \| grep -v '^#' \| sort`(이름만) ↔ 11 문서 이름 표: 빠진 이름 0, 넣지 말아야 할 이름(`PUSH_DEV_PAGE_ENABLED`·`DATABASE_URL` 등 결정 K) 0 · `… u4-s9-pushdev -- curl -s -o /dev/null -w '%{http_code}' <URL>/api/push-dev/` → 404 | 사용자 + 에이전트 | U4 |
| S10 | 공개 노출 정책 | **결정 M 값으로 단언** | `… u4-s10-docs -- curl -s -o /dev/null -w '%{http_code}' <URL>/api/docs` · `/api/openapi.json` · `/api/redoc` → 결정 M (i) 이면 셋 다 404. 인증 없음은 CR-005 결정 D(d) 확정 — 공개 기간·종료 절차가 그 대가. 로컬 같은 3개: `u1-smoke-s10-*` | 에이전트 | U1·U4 |
| S11 | SW·PWA(HTTPS 출처) | 같음 | 사용자 Chrome: `<URL>` → 브리핑 화면 "알림 받기" → DevTools Application 탭 Service Worker `activated`·scope `https://<호스트명>/` · Manifest 오류 없음 · 서버 `docker compose -f docker-compose.prod.yml exec -T postgres psql … -tAc "SELECT count(*) FROM push_subscriptions"` +1 | 사용자 | U4 |
| S12 | 실 푸시 발송 | 같음(버튼 경로 보호 없음 — 사실 13) | 일정 1건 → 브리핑 화면 "지금 브리핑"(`POST /api/briefings/run {schedule_id}`) → 화면에 성공 표시 + 알림 수신(사람) · 서버 `agent_traces` 최신 `briefing_run` 행의 푸시 결과 `sent` | 사용자 | U4 |
| S13 | lifespan 스케줄러·워커 수 | 같음(1분 루프, `--workers 1`) | 로컬: 스모크 변수 `BRIEFING_SCHEDULER_ENABLED=1` 로 기동 2분 뒤 `… u1-smoke-s13 -- <DC> exec -T postgres psql -U app -d relationship -tAc "SELECT count(*) FROM agent_traces WHERE step='briefing_run'"` ≥ 1 · `test_deploy_files.py` ⑫ `--workers 1`. 배포: 같은 질의를 사용자가 기동 2분 뒤 + 데모 일정이 24시간 창에 들어온 뒤 `briefing_compose` 행이 일정당 1개 | 에이전트 + 사용자 | U1·U4 |
| S14 | CloudFront 헤더 전달 | **Caddy 헤더 전달** | S6 응답의 `session_id` 로 `… u4-s14-session -- curl -fsS -H 'X-Session-Id: <id>' <URL>/api/questions/pending` → 그 세션 질문(없으면 `[]`, 422 `invalid_session_id` 가 아님) | 에이전트 | U4 |
| S15 | AWS Budgets 3단계 (Terraform plan) | **콘솔 Budgets + OpenAI 한도** | 사용자 보고 1줄: 예산 이름·금액(결정 I)·생성 시각이 EC2 생성보다 앞 · OpenAI 월 지출 한도 있음 · 크레딧 잔액 메모(02 카드 표) | 사용자 | U3·U4 |
| S16 | (추가) 제품 코드 무변경·비밀 0 | — | 판정 표 #2·#4 | — | 전 단위 |
| S17 | (추가) 포트·보안 그룹 | — | 로컬 `u1-smoke-ports`(#3) · 사용자: 보안 그룹 인바운드 규칙 목록 = 80·443 전체 + 22 내 IP(결정 D) 뿐(스크린샷 대신 규칙 텍스트) · `ss -tlnp` 에 0.0.0.0:80·443 만(+22) · 외부 `nc -vz -w 3 <EIP> 5432`·`8000` 실패 | 에이전트 + 사용자 | U1·U4 |

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 배포 URL(HTTPS)에서 데모 시나리오 5단계 재현 + `git diff --stat -- app web/src alembic` 빈 출력(제품 코드 무변경) + `postgres` 호스트 포트 미노출 + 저장소·compose 파일에 비밀 값 0 + 로컬에서 `docker compose -f docker-compose.prod.yml up --build` 스모크(`/api/health` 200, 정적 `/` 200) + 종료 체크리스트 문서 존재 + 아래 유효성 점검 중 compose·Caddy 대응 항목(RDS·CloudFront 항목은 치환).

(위 문장은 backlog 95행 "수용기준:" 뒤 그대로다. 같은 행의 다음 문장 "**실제 EC2 기동은 사용자가 따로 지시할 때(계획·파일·로컬 스모크까지 먼저).**" 는 U4 의 시작 조건으로 반영했다. "아래 유효성 점검" 은 같은 행 뒷부분의 원안 수용기준 ①~④(R-U10D-3·-1·S1~S15·권고 R-U10D-5·-7·-9·-10)를 가리키며, 이 계획의 치환 표가 그 대응이다. backlog 문장의 `git diff --stat -- app web/src alembic` 에는 기준이 없으므로 판정은 `<기준>..HEAD` 로 한다 — 활성화 때 적는 기준 해시.)

권고 소견 처리: R-U10D-1 → U1 Dockerfile + 로컬 S1, CI 는 결정 H · R-U10D-2 → S2·S4 를 로컬(U1)과 배포(U4) 둘 다 · R-U10D-3 → CR-005 결정 D(d) + 결정 M(S10) · R-U10D-4 → S7(entrypoint 주체, 슈퍼유저 확장)·S8(치환) · R-U10D-5 → U1 `.env.example` 주석 · R-U10D-6 → **하지 않음**(`tests.md` 개발 전용 표시는 P9 범위 밖, 04-review 에 이관 기록) · R-U10D-7 → 이번에 하지 않음(5일 공개, S5 pydantic 검증으로 대신) · R-U10D-8 → S6 · R-U10D-9 → `--workers 1` + S13 · R-U10D-10 → U4 데모 5단계가 운영 경로(Caddy → backend → compose Postgres)로 지나간다.

## 결정 항목 (사용자 — `확정:` 비움, 메인 세션이 한 번에 묻는다)

CR-005 의 결정 A~D 와 헷갈리지 않도록 이 계획의 결정은 "P9 결정 A~P" 로 부른다. 이미 확정돼 묻지 않는 것: 구성(EC2 1대 + compose 3서비스)·제품 코드 0·1분 루프·접근 보호 없음·공개 ~11-19·신규 계정 Free Plan·비상업·Budgets 를 EC2 전에·백업 = 종료 직전 `pg_dump` 1회·실제 기동은 사용자 지시 뒤. 이 계획은 인터넷 조회 없이 썼다 — 가격·크레딧·PSL 같은 외부 수치는 "확인 필요" 로 표시했다.

- **결정 A · 인스턴스 유형·디스크**
  - (i) **t4g.small**(ARM Graviton, 2 vCPU, 2GB) + gp3 20GB **[추천]** — uvicorn + Postgres + Caddy 를 한 대에 두고 EC2 에서 프론트(`npm ci`·`tsc -b`·`vite build`)까지 빌드한다(결정 E). 1GB 는 빌드 중 메모리 부족 위험이 크다. 09 가이드 결정 3 과 같다. ARM 호환: `pgvector/pgvector:pg16`(09 가이드 §2 "지원")·`python:3.13-slim`·`node:24-slim`·`caddy:2-alpine` 은 다중 아키텍처 공식 이미지로 알고 있고, npm 잠금 파일에 linux-arm64-gnu 바이너리가 있다(사실 8). 파이썬 휠(psycopg-binary·numpy·cryptography)의 aarch64 휠은 U1 로컬 빌드(ARM Mac 이면)로 확인. Free Plan 적격 목록에 있다(CR-005 개정 ②, 가입 화면 재확인).
  - (ii) t3.micro(x86, 2 vCPU, 1GB) + 스왑 2GB — 가장 싸고 x86 이라 아키텍처 걱정이 없지만 메모리 1GB 에 빌드·Postgres·Python 이 함께 올라간다. 고르면 결정 E 를 (iii)(EC2 밖에서 빌드)로 바꾸는 것을 권한다.
  - (iii) t3.small(x86, 2GB) — 메모리는 (i) 과 같고 x86 이라 로컬 ARM Mac 스모크와 아키텍처가 다르다(그 경우 U1b CI 가 amd64 를 본다). (i) 보다 비싸다.
  - 확정: **(i) t4g.small + gp3 20GB** — 사용자 2026-11-14
- **결정 B · 호스트명(도메인)**
  - (i) **`<EIP 대시 표기>.sslip.io`**(예: `3-35-10-20.sslip.io`) **[추천 — 보유 도메인이 없을 때]** — 비용 0, DNS 작업 0, Caddy 가 그 이름으로 Let's Encrypt 인증서를 받는다. 위험: sslip.io 가 Public Suffix List 에 올라 있지 않다면 Let's Encrypt "등록 도메인당 주간 발급 한도" 를 전 세계 사용자와 공유해 발급이 거절될 수 있다(**PSL 등재 여부 확인 필요**). 대비: Caddy 는 Let's Encrypt 실패 시 기본 대체 발급자(ZeroSSL)로 다시 시도하는 것으로 알고 있다(U4 caddy 로그로 확인) → 그래도 안 되면 (ii) → (iii). `caddy_data` 볼륨으로 인증서를 보존해 재발급 횟수를 줄인다(U1 ⑨).
  - (ii) `nip.io`(같은 방식, 다른 운영자) — (i) 과 같은 한도 위험. (i) 실패 시 대안.
  - (iii) 보유 도메인(또는 새로 구입, 연 1~2만 원) A 레코드 → EIP — 한도 위험 없음, 발표 URL 이 깔끔하다. DNS 전파 대기와 구입 절차가 일정에 더해진다. **보유 도메인이 있으면 이것이 추천.**
  - 확정: **(iii) 새로 구입하는 도메인**(이름은 사용자가 구입 뒤 알림; 11 문서는 `<도메인>` 자리표) — 사용자 2026-11-14. **보조**: 구입·DNS 전파가 기동 시점보다 늦으면 (i) `<EIP>.sslip.io` 로 먼저 띄우고 도메인이 준비되면 Caddyfile 호스트명만 바꿔 재기동(U4 절차에 둘 다 적는다).
- **결정 C · 리전**
  - (i) **`ap-northeast-2`(서울)** **[추천]** — 사용자·심사자가 한국. 09 가이드 결정 1. CloudFront 가 없어 us-east-1 인증서도 필요 없다.
  - (ii) `us-east-1` — 단가가 약간 싸고 OpenAI 와 가깝지만 브라우저 왕복이 길다. 5일 비용 차는 1달러 미만.
  - 확정: **(i) 서울** — 추천안, 사용자 위임 2026-11-14
- **결정 D · 서버 접속**
  - (i) **SSH 키 페어 + 보안 그룹 22 를 "내 IP"/32 로만** **[추천]** — 절차가 가장 짧다(IAM 역할·플러그인 불필요). 대가: 발표 장소에서 IP 가 바뀌면 콘솔에서 규칙을 고쳐야 한다(11 문서에 적음). `.pem` 은 사용자 PC 에만.
  - (ii) SSM Session Manager(22 닫음) — 09 가이드 결정 6 의 권장. 인스턴스 역할(`AmazonSSMManagedInstanceCore`) 부착 단계가 늘고, 로컬 CLI 로 쓰려면 플러그인 설치가 필요(콘솔 브라우저 접속은 바로 가능). 키 파일 관리가 없어 더 안전하다.
  - (iii) EC2 Instance Connect(브라우저) — 22 를 리전의 Instance Connect IP 범위에 열어야 한다.
  - 확정: **(i) SSH 키 페어 + 22 는 내 IP/32** — 사용자 2026-11-14
- **결정 E · 프론트 빌드 위치**
  - (i) **다단계 Dockerfile — `web-build`(node:24-slim) 단계에서 빌드해 `caddy` 이미지 `/srv` 에 포함** **[추천]** — 서버에 Node 설치 불필요, `git pull` + `up -d --build` 한 줄로 프론트·백엔드가 같은 커밋으로 맞는다(재현성, 원칙8). 로컬 스모크·CI 가 운영과 같은 경로를 탄다. 대가: EC2 에서 `npm ci`(수백 MB)·빌드 메모리 — 2GB(결정 A (i))면 충분할 것으로 보지만 실측은 U4.
  - (ii) 호스트 빌드 — EC2 에 Node 24 설치 후 `npm ci && npm run build`, `./web/dist:/srv:ro` 볼륨 마운트. 프론트만 바꿀 때 빠르지만 서버에 Node 를 따로 관리하고 빌드를 잊으면 프론트·백엔드 커밋이 어긋난다.
  - (iii) 사용자 PC 에서 빌드 후 `scp` 로 `dist` 업로드 — 서버 메모리 부담 0(결정 A (ii) 와 짝), 대신 커밋과 배포본이 어긋날 수 있고 수동 단계가 는다.
  - 확정: **(i) 다단계 Dockerfile(node 빌드 → caddy `/srv`)** — 추천안, 사용자 위임 2026-11-14
- **결정 F · 기반 이미지·Python 버전**
  - (i) **백엔드 `python:3.13-slim` · 빌드 `node:24-slim` · 프록시 `caddy:2-alpine` · DB `pgvector/pgvector:pg16`** **[추천]** — `.python-version` 은 없고 ruff·mypy 대상이 3.13(사실 10), CI 가 3.13 을 돈다. Node 24 는 `engines` 와 CI(`node-version: 24`)와 같다. DB 이미지는 로컬·CI 와 같다. 태그는 메이저(·마이너)까지 고정, 다이제스트 고정은 하지 않는다(5일).
  - (ii) 백엔드 `python:3.14-slim` — CI 매트릭스에 있지만 mypy·ruff 기준이 3.13 이다.
  - (iii) 다이제스트(`@sha256:…`)까지 고정 — 재현성은 가장 높지만 U1 에서 다이제스트 조회가 필요하고 ARM/x86 각각 다르다.
  - 확정: **(i) python:3.13-slim · node:24-slim · caddy:2-alpine · pgvector/pgvector:pg16** — 추천안, 사용자 위임 2026-11-14
- **결정 G · 파일 이름·위치**
  - (i) **저장소 루트에 `Dockerfile`(단계 3개)·`docker-compose.prod.yml`·`Caddyfile`·`.dockerignore`, entrypoint 는 `docker/entrypoint.sh`, compose 프로젝트 이름 `relationship-prod`** **[추천]** — D17 1 이 이 이름들을 쓴다. 기존 `docker/initdb/` 와 같은 폴더에 entrypoint. 로컬 `docker-compose.yml` 은 그대로(사실 6 의 이름 충돌은 `name:` 으로 막는다).
  - (ii) `deploy/` 폴더에 모두 — 루트가 덜 붐비지만 D17·backlog 95행 문구(`docker-compose.prod.yml`)와 경로가 달라져 문서 보정이 필요.
  - 확정: **(i) 저장소 루트 + `docker/entrypoint.sh`, 프로젝트 이름 `relationship-prod`** — 추천안, 사용자 위임 2026-11-14
- **결정 H · CI 에 이미지 빌드 스모크 추가 (R-U10D-1)**
  - (i) **추가 — `tests.yml` 에 `deploy-smoke` job(빌드 + compose `--wait` + `/api/health`·`/` curl), U1b** **[추천]** — R-U10D-1 이 "Dockerfile + S1 을 CI 에" 를 [필수]로 요구했다. dev2 푸시마다 배포 파일이 깨지지 않았는지 기계가 본다. ubuntu(amd64) 빌드라 결정 A 가 x86 이면 운영 아키텍처 증거도 된다. 비용: job 1개·실행 수 분, 단위 1개(작음).
  - (ii) 추가하지 않음 — 로컬 스모크(U1) 1회 증거로 갈음. 5일 공개라 이후 회귀 위험은 작지만 R-U10D-1 은 "이관" 으로 04-review 에 남는다.
  - 확정: **(i) 추가(U1b)** — 추천안, 사용자 위임 2026-11-14
- **결정 I · Budgets 금액**
  - (i) **$10 / $30 / $50 실제 비용 알림 3개(02 카드·D17 6 그대로)** **[추천]** — 5일 예상 비용이 $3~4(아래 추정)라 $10 알림은 이상 징후에만 울린다.
  - (ii) (i) + $5 조기 알림 1개 — 예상의 약 1.5배에서 울려 종료 절차 누락(EIP·EBS 남김)을 빨리 알아챈다.
  - 확정: **(i) $10 / $30 / $50** — 추천안, 사용자 위임 2026-11-14
- **결정 J · 종료 시각 (날짜 11-19 확정, 시각만)**
  - (i) 11-19(목) 10:00 KST
  - (ii) **11-19(목) 18:00 KST** **[추천]** — 평가 다음 날 낮 동안 늦은 확인 요청에 대비하고, 업무 시간 안에 실행해 문제가 생기면 같은 날 대응한다. (i)·(ii) 비용 차는 약 $0.2.
  - (iii) 11-19(목) 23:59 KST
  - 확정: **(ii) 11-19(목) 18:00 KST** — 사용자 2026-11-14
- **결정 K · 운영 `.env` 의 스위치·공급자 값** (`BRIEFING_SCHEDULER_ENABLED=1` 은 확정)
  - (i) **`PUSH_DEV_PAGE_ENABLED` 비움(꺼짐) · `LLM_PROVIDER=openai` · `LLM_PROVIDERS_ENABLED=openai` · Anthropic/Gemini 키 넣지 않음 · `APP_USER_ID=demo`(로컬 `local` 과 구분) · `APP_TIMEZONE` 비움(Asia/Seoul) · ER 임계치·가중치·패턴·승격 값은 비움(코드 기본값 = 평가된 값)** **[추천]** — 확인 페이지는 제품 화면이 아니고(원칙5) 공개 URL 에 둘 이유가 없다(S9 404). 서버에 두는 키를 하나(OpenAI — LLM·임베딩 D4)로 줄이면 종료 시 회전 대상도 하나다.
  - (ii) (i) 에서 `PUSH_DEV_PAGE_ENABLED=1` — 푸시 문제를 배포본에서 진단하기 쉬워지지만 공개 노출이 늘고 S9 기대값이 바뀐다.
  - (iii) 공급자 셋 다 켬(키 3개) — 회전 대상이 늘고 데모에 이득이 없다.
  - 확정: **(i)** — 추천안, 사용자 위임 2026-11-14
- **결정 L · 로그 보존**
  - (i) **`docker compose logs` 만 + compose `logging: json-file max-size 10m, max-file 3`(서비스당 최대 30MB)** **[추천]** — 5일 동안 디스크가 로그로 차지 않게 상한만 둔다. 외부 전송 없음(09 가이드 §5).
  - (ii) Docker 기본값(무제한 json-file) — 5일·소규모라 실제로 문제될 가능성은 낮지만 상한이 없다.
  - 확정: **(i) json-file 10m × 3** — 추천안, 사용자 위임 2026-11-14
- **결정 M · 공개 노출 — `/api/docs`·`/api/redoc`·`/api/openapi.json` (R-U10D-3·S10)**
  - (i) **Caddy 에서 세 경로 404** **[추천]** — 제품 코드 변경 0 으로 공개 URL 이 쓰기 API 목록을 광고하지 않는다. 로컬 개발 `localhost:8000/docs` 는 그대로.
  - (ii) 그대로 둠 — `/api/docs` 는 Swagger 화면이 `/openapi.json`(접두 없음)을 찾다가 SPA `index.html` 을 받아 깨진 화면이 되고, `/api/openapi.json` 은 그대로 읽힌다.
  - 확정: **(i) Caddy 404** — 추천안, 사용자 위임 2026-11-14
- **결정 N · 웹푸시 VAPID 키**
  - (i) **배포용 새 키 쌍(사용자 터미널에서 생성, 값은 서버 `.env` 에만)** **[추천]** — 배포 출처는 어차피 새 구독이 필요하고, 종료 때 폐기해도 로컬 개발 구독에 영향이 없다.
  - (ii) 로컬 `.env` 키 재사용 — 종료 시 회전하면 로컬 구독도 다시 해야 한다.
  - 확정: **(i) 배포용 새 키 쌍** — 추천안, 사용자 위임 2026-11-14
- **결정 O · 백엔드 DB 접속값 주입**
  - (i) **compose `backend.environment` 에 비밀번호 없는 `DATABASE_URL`(사용자 `${POSTGRES_USER}` · 호스트 `postgres:5432` · DB `${POSTGRES_DB}`) + `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?…}`** **[추천]** — D17 3("`DATABASE_URL` 은 `postgres:5432` 를 가리킨다") 문구 그대로이면서, `app/config.py` 가 URL 에 비밀번호가 없을 때 `POSTGRES_PASSWORD` 로 채우는 기존 경로(사실 2)를 써서 ① 비밀번호 특수문자의 URL 파싱 문제가 없고 ② `secret-guard` 의 DB URL 패턴(사실 3)에 걸리지 않는다. 서버 `.env` 에 `DATABASE_URL` 을 실수로 넣어도 `environment` 가 덮어쓴다.
  - (ii) `DATABASE_URL: ""` + `POSTGRES_HOST: postgres` + `POSTGRES_PORT: "5432"` — `POSTGRES_*` 갈래로 접속. 결과는 같지만 D17 3 문구("`DATABASE_URL` 이 가리킨다")와 어긋나 D17 보정이 필요하다.
  - (iii) 비밀번호를 넣은 `DATABASE_URL` 보간 — 사실 3 때문에 Write 단계에서 거부되고, 사실 2 의 특수문자 문제도 남는다. **선택 불가에 가깝다**(기록용).
  - 확정: **(i) 비밀번호 없는 `DATABASE_URL` + `POSTGRES_PASSWORD`** — 추천안, 사용자 위임 2026-11-14
- **결정 P · 스모크 치환 표**
  - (i) **위 "배포 유효성 점검 치환 표" S1~S17 그대로** **[추천]** — Dockerfile·compose 는 원안 그대로 살아나고(S1·S7), CloudFront 는 Caddy 로(S2·S4·S14), RDS SSL 은 "외부 경로 없음" 판정으로(S8), Terraform Budgets 는 콘솔로(S15) 치환. 로컬에서 판정 가능한 S1·S2·S4·S7·S10·S13·S17 은 U1 에서 먼저 닫고, 배포 URL 이 필요한 것만 U4 에 남긴다.
  - (ii) 표를 고쳐서(행 추가·삭제·기대값 변경) — 사용자 지정.
  - 확정: **(i) S1~S17 그대로** — 추천안, 사용자 위임 2026-11-14

## 비용 추정 (서울, 온디맨드, 5일 = 120시간 상한 — **단가는 기억에 의존한 대략값, 가입 화면·AWS 요금 페이지로 확인 필요**)

| 결정 A | 인스턴스 시간당 | ×120h | EBS gp3 20GB(약 $0.0912/GB-월 → 120h) | 퍼블릭 IPv4(EIP, $0.005/h ×120h) | 합계 |
|---|---|---|---|---|---|
| t4g.small(추천) | 약 $0.0208 | 약 $2.50 | 약 $0.30 | $0.60 | **약 $3.4** |
| t3.micro | 약 $0.013 | 약 $1.56 | 약 $0.30 | $0.60 | 약 $2.5 |
| t3.small | 약 $0.026 | 약 $3.12 | 약 $0.30 | $0.60 | 약 $4.0 |

- 인터넷 송신은 월 100GB 까지 무료로 알고 있어 데모 트래픽은 0 에 가깝다. 스냅샷·백업 저장 없음(`pg_dump` 는 사용자 PC 로).
- **크레딧 안이다**: Free Plan 가입 크레딧 $100(+ 활동 최대 $100, CR-005 개정 ②)에 비해 3~4% 수준. 적격 인스턴스도 크레딧에서 차감된다(D17 6) — "무료" 가 아니라 "크레딧 차감".
- 실제 기동이 11-17 이면 약 50시간이라 위 값의 절반 이하. 종료 절차에서 EIP·EBS 를 남기면 그 뒤에도 시간당 과금이 계속된다(12 문서 4·5항이 막는다).
- LLM·임베딩 비용은 별도(OpenAI 월 지출 한도가 상한).

## 리스크 · 미결

- **[일정] 11-18 전 기동 가능성**: 에이전트 몫(U1·U2 동시 → U1b → U3)은 계획 검증·활성화 뒤 하루 안에 끝낼 수 있는 크기다. 병목은 사용자 몫 — **신규 AWS 계정 가입·카드 확인·Free Plan 활성화는 수 분~최대 24시간이 걸릴 수 있다**(신규 계정 검증 지연 — 확인 필요). 계정 가입·MFA·Budgets 는 "띄우기" 가 아니므로 사용자가 11-16(월)까지 먼저 해 두면, 11-17(화) 기동 지시 당일에 EC2 생성 → Docker → 기동 → 인증서 → 스모크까지 2~3시간으로 끝낼 수 있다(메인 세션이 결정 질문 때 이 권고를 함께 전한다). 11-17 안에 기동이 안 되면 11-18 데모는 로컬(`docs/RUNNING.md`)로 대체하고 P9 는 열린 채 남는다.
- **[불확실] 외부 수치를 인터넷 조회 없이 썼다**: Free Plan 크레딧·적격 인스턴스·기간(가입 화면), 서울 단가(요금 페이지), sslip.io 의 PSL 등재 여부, Caddy 의 대체 발급자 동작, Caddy MIME 표의 `.webmanifest`(Caddyfile 에 명시해 의존을 없앰). 전부 U4 첫날 드러나며, 배포 파일 쪽 문제는 U1 FIX 1건으로 고칠 수 있게 설정을 `Caddyfile`·`docker-compose.prod.yml` 두 파일에 몰았다.
- **[인증서] 발급 실패 시**: Caddy 로그에 한도·검증 실패가 나오면 ① 80 포트가 보안 그룹에서 열렸는지 ② `dig` 결과가 EIP 인지 ③ 대체 발급자 시도 여부를 본다. 그래도 실패면 결정 B (ii) → (iii) 순. `caddy_data` 볼륨을 지우지 않는다(재발급 = 한도 소모). HTTPS 없이는 서비스 워커·웹푸시가 안 되므로(D17 2) HTTP 로 발표하는 대안은 없다.
- **[메모리] 1GB 인스턴스(결정 A (ii))**: 빌드(`tsc -b`·`vite build`) 중 OOM 으로 `up --build` 가 실패할 수 있다 → 스왑 2GB + 결정 E (iii). 2GB 에서도 빌드 중 Postgres·uvicorn 이 같이 떠 있으므로 U4 에서 `free -m`·`docker stats --no-stream` 을 1회 기록한다.
- **[비용] 공개 중 LLM 비용**: 누구나 `POST /api/chat`·`POST /api/briefings/run`(본문 유무 무관, 사실 13)을 부를 수 있다. OpenAI 월 지출 한도만이 상한이다. 한도에 닿으면 채팅이 루프 오류 답으로 바뀌고 서버는 죽지 않는다. 심사 직전 한도 잔액을 확인한다(11 문서).
- **[가용성] 서버가 꺼지면 데모 불가**: 단일 EC2·단일 AZ, 자동 복구 없음. `restart: unless-stopped` + Docker 서비스 부팅 시 자동 시작(11 문서 6단계)으로 프로세스 종료·재부팅은 버틴다. 인스턴스 장애 시 대안은 로컬 실행(`docs/RUNNING.md`)으로 발표(11 문서 16단계).
- **[크레딧·Budgets]**: 크레딧이 비용을 상쇄하면 Budgets "실제 비용" 이 0 으로 보여 알림이 울리지 않을 수 있다(Budgets 고급 옵션의 크레딧 포함 여부 — **확인 필요**). 12 문서 10항의 "다음 날 사용량 확인" 이 그 보완이다.
- **[데이터] 사용자 격리 없음(F-fbaaae)**: 모든 방문자가 같은 `APP_USER_ID` 의 기억을 공유한다 — 심사자 A 가 입력한 인물을 심사자 B 가 본다. 평가 직전 깨끗한 상태가 필요하면 `APP_USER_ID` 를 바꿔 `up -d`(11 문서 14단계). 입력된 제3자 정보는 종료 시 인스턴스와 함께 삭제되고 `pg_dump` 는 사용자 PC 에만 남는다.
- **[로컬 스모크] 훅·환경**: `docker compose --env-file <스크래치 파일>` 이 `safety-guard` 에 걸리면 우회하지 않고 메인 세션에 "명령 실행 요청" 으로 보고한다(security §6). 로컬 80/443 충돌은 `CADDY_HTTP_PORT=8088` 로 피한다. 로컬 스모크 볼륨 `relationship-prod_pgdata` 는 남는다(삭제는 사용자, security §4).
- **[하네스] secret-guard DB URL 패턴(사실 3)**: 배포 파일·11 문서·증거 어디서든 `<user>:<password>@` 꼴 문자열은 Write·`save_evidence.py` 단계에서 거부된다. 결정 O (i) 가 이를 피하지만, `docker compose config`(값 출력)를 증거로 저장하면 보간된 URL·비밀번호가 찍힐 수 있으므로 항상 `--quiet` 로만 돌린다.
- **[아키텍처] 로컬 ARM Mac ↔ 운영 x86**: 결정 A 가 t3 면 로컬 스모크는 운영과 다른 아키텍처를 빌드한다 → 결정 H (i) 의 CI(amd64)가 보완. 결정 A 가 t4g 면 로컬(ARM)이 운영과 같고 CI 가 amd64 를 덤으로 본다.
- **[CRLF] Windows 체크아웃**: `docker/entrypoint.sh` 가 CRLF 로 체크아웃되면 `sh` 가 `set -e\r` 에서 실패한다 → Dockerfile 안에서 CR 제거 + `sh` 로 실행(실행 비트 불필요). EC2(Ubuntu)는 LF 로 체크아웃된다.
- **[스케줄러] 공개 중 1분 루프**: 일정이 없으면 매분 `briefing_run` trace 1행만 남는다(LLM 호출 0). 5일 × 1440 = 약 7,200행 — 데이터 수 MB 수준이라 문제 없다.
- **[P2b 경계]**: `app/api/delete.py`(U1·U2)는 이미지에 포함되지만 호출하는 라우트가 없다. P9 는 그 파일을 건드리지 않는다.
- **종료 절차는 수용 기준이 "문서 존재" 다**: 실제 실행(결정 J)은 04-review 뒤의 일이라 03-log·journal 에 항목별 확인 결과를 남기고, 실행될 때까지 HANDOFF 에 "종료 절차 미실행" 을 남긴다.

## 읽은 카드

- `docs/wiki/changes/CR-005.md` — 전문(§2-1 Vercel 조사 사실은 기록으로만, **개정 ②** 결정·계정·비용 전제·일정 제약).
- `docs/wiki/decisions/D17-vercel-deploy.md` — 전문(개정 ②, 결정 1~8·"코드에서 지켜야 할 것" 1~6).
- `docs/wiki/security.md` — 전문(§1 비밀·L-007 · §3 `curl | sh` · §4 인프라·외부 전송 · §4b 증거 저장 · §5 개정 ②).
- `.claude/hooks/secret-guard.sh` 55~77행(패턴 9개 — 사실 3).
- `docs/wiki/packages/P8-frontend/review-u10-deploy-validity.md` — §9 S1~S15 표 · §10 R-U10D-1~9.
- `docs/backlog.md` 93~96행(P9 95행 수용 기준 원문).
- `docs/user-setup/09-aws-deploy.md` — 전문(상단 부분 대체 안내 · §2 결정 1~10 · §3 비용 · §4.2·§4.3 골격 · §5·§6·§7).
- `docs/user-setup/02-aws-budgets.md` 1~25행 · `SERVER-CHECKLIST.md` 전문.
- `docs/wiki/templates/plan.md` · `docs/wiki/CURRENT.md`(active·메모 머리 3줄) · `docs/wiki/registry.md`(grep `compose|Dockerfile|Caddy|RUNNING|SERVER-CHECKLIST|initdb` — 34·36·41·42·43·267행).
- 폐기된 Vercel 안 `docs/wiki/packages/P9-infra/01-plan.md`(이 파일의 이전 내용) — 판정 표 형식·S1~S17 치환 표 형식·사람 점검·증거 저장 규약만 재사용.
- `.claude/gitlog.md`(2026-11-14 12:46 스냅샷, HEAD `4a4d8cb`).
- 코드·설정: `docker-compose.yml` · `app/config.py` 전문 · `app/main.py` 전문 · `app/settings.py`(grep `APP_USER_ID|INTERVAL`) · `app/briefing/run.py`(grep `briefing_run`) · `.env.example` · `requirements.txt` · `web/package.json` · `web/vite.config.ts` · `web/package-lock.json`(grep linux-arm64-gnu) · `.github/workflows/tests.yml`(grep 트리거·버전·job) · `pyproject.toml`(grep 버전) · `alembic.ini`(grep) · `docs/RUNNING.md`(grep uvicorn·alembic) · grep `app/` 의 `evaluation|scripts|data|reports` import · grep `tests/` 의 `.env.example`(0) · Glob `.python-version`·`Dockerfile`·`Caddyfile`·`.dockerignore`·`.gitattributes`(전부 없음).
- 열지 않은 것: `docs/user-setup/05-server-secrets.md`(U3 에서 SSM 내용 유무를 보고 상단 안내 여부 결정) · `docs/user-setup/07-demo-rehearsal.md`(데모 5단계는 SERVER-CHECKLIST §5 로 갈음) · `web/src/` 코드(U2 에서 frontend-agent 가 확인 — 이 계획의 프론트 사실은 폐기된 Vercel 안이 이미 확인한 `client.ts`·`BriefingScreen.tsx` 행 번호와 `web/public/` Glob 에 기댄다) · `docs/wiki/specs/S3.6-briefing-push.md`(D17 3 이 "원문 그대로" 라 재확인 생략).
