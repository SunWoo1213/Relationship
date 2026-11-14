# P9-infra 테스트 기록 — 무엇을 어떻게 시험했나

> 확인 1건 = 표 1줄. 열: 확인 항목 | 명령 | 결과 | evidence. 자동 테스트는 실제 네트워크·LLM·푸시 서비스를 쓰지 않는다(결정 J). 절은 단위별로 쓴 에이전트가 덧붙인다.

## U2 — 프론트 빌드 산출물·`/api` 규약·PWA 루트 경로 (frontend-agent, 2026-11-14, 기대 코드 변경 0)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `npm ci && npm run build`(`tsc -b && vite build`) 성공 | `bash build.sh`(`cd web && npm ci && npm run build`) | exit 0 · npm ci 3.3초 · 빌드 1.6초 · node v24.21.0 / npm 11.19.0 | `evidence/20261114-1422-u2-build.txt` |
| `dist/` 최상위에 `index.html`·`sw.js`·`manifest.webmanifest`·`assets/` | 같은 파일 `ls -la dist` + `paths.sh` 의 `test -e` | 4개 모두 있음(그 외 `favicon.svg`·`icon-192.svg`·`icon-512.svg`) · `assets/` 는 `index-*.js`·`index-*.css` 2개 | `…-u2-build.txt` · `…-u2-paths.txt` |
| `dist` 크기 | `du -sh dist` | 424K(JS 363.6 kB · gzip 115.4 kB / CSS 44.9 kB · gzip 8.2 kB) | `…-u2-build.txt` |
| `dist/index.html` 자산 경로가 루트 기준(`/assets/…`) | `grep -oE '(src\|href)="[^"]*"' dist/index.html` + 상대 경로 개수 | `/favicon.svg`·`/manifest.webmanifest`·`/assets/index-DB5EDvsy.js`·`/assets/index-SUxzZwmI.css`, `./`·`assets/` 상대 참조 0 | `…-u2-paths.txt` |
| `vite.config.ts` 에 `base` 없음 | `grep -nE '^\s*base\s*:' vite.config.ts` | 매치 없음("base 없음") | `…-u2-paths.txt` |
| 서비스 워커 등록 경로 `/sw.js`·scope `/` | `grep` `src/push.ts` · `src` 의 `scope` | `SERVICE_WORKER_URL='/sw.js'`, `register(SERVICE_WORKER_URL)` 에 scope 옵션 없음 → 기본 scope = `/sw.js` 의 디렉터리 = `/` | `…-u2-paths.txt` |
| `dist/sw.js`·`dist/manifest.webmanifest` 가 `public/` 원본과 같다(변경 0) | `cmp dist/sw.js public/sw.js` · `cmp` manifest | 둘 다 "동일" | `…-u2-paths.txt` |
| manifest `scope:"/"`·`start_url:"/#/chat"` | `cat dist/manifest.webmanifest` | `"start_url": "/#/chat"`, `"scope": "/"`, 아이콘 `/icon-192.svg`·`/icon-512.svg`(절대 경로) | `…-u2-paths.txt` |
| 프론트의 API 호출은 `/api` 접두 한 곳 | `grep -n API_BASE src/api/client.ts` · `grep -rn "fetch(" src`(테스트 제외) | `API_BASE='/api'`, `fetch(` 는 `client.ts:67` 한 곳뿐 | `…-u2-paths.txt` |
| 하드코딩 0 | `grep -rn "localhost:8000\|127.0.0.1:8000\|http://" src`(테스트 제외) · `grep -rlE` dist | 비테스트 1건 = `src/proxy.ts:5` `DEFAULT_API_TARGET`(개발 서버 프록시 기본값, `vite.config.ts` 만 import — 번들에 안 들어감) · 번들(`dist`) 0건 | `…-u2-paths.txt` |
| 개발 프록시 규약 = 운영 Caddy `handle_path` (접두 제거) | `stripApiPrefix` 코드·`proxy.test.ts` | `/api/x` → `/x`, `/api` → `/` — Caddy `handle_path /api/*` 도 접두를 떼어 `backend:8000` 으로 넘기므로 같은 규약 | `…-u2-paths.txt` |
| `dist` 가 커밋 대상이 아님 | `git check-ignore -v web/dist web/node_modules` · `git status --short web` | `web/.gitignore:7 dist`, `:6 node_modules` · `git status web` 변경 0 | `…-u2-paths.txt` |
| `npm run typecheck` 통과 | `bash tests.sh` | exit 0, 오류 0 | `evidence/20261114-1422-u2-tests.txt` |
| Vitest 전체 통과(기준선) | `npx vitest run` | **9 파일 · 156 passed**, skip 0, 2.5초 | `…-u2-tests.txt` |
| 라우팅이 해시 기반이라 SPA fallback 은 보험 | `sed -n 1,16p src/routes.ts` | `#/chat`·`#/persons`·`#/briefings` 3경로뿐 — 서버는 `/` 만 받는다 | `…-u2-paths.txt` |

## U1 — 배포 파일 5종 + 텍스트 검사 테스트 + 로컬 compose 스모크 (backend-agent, 2026-11-14, 제품 코드 변경 0)

증거 파일 이름은 모두 `evidence/20261114-14NN-u1-<이름>.txt` — 아래 표에는 `<이름>` 만 쓴다. 변이는 전부 저장소 밖 스크래치패드 사본(`…/scratchpad/p9-u1/mut/<ID>/`)에서만 돌렸고 저장소 파일은 고치지 않았다(`git status --short` 에 새 파일·기존 수정 목록만 — 증거 `scope-untracked`).

### 자동 테스트 `tests/test_deploy_files.py` (17건, DB·Docker 불필요, skip 0)

| # | 테스트 | 무엇을 단언하나 | 결과 |
|---|---|---|---|
| ① | `test_compose_project_name_is_relationship_prod` | 최상위 `name: relationship-prod` | passed |
| ② | `test_compose_has_three_services` | 서비스 집합 == {caddy, backend, postgres} (정확히 셋) | passed |
| ③ | `test_postgres_has_no_host_ports` | postgres 블록에 `ports:` 0 | passed |
| ④ | `test_backend_has_no_host_ports` | backend 블록에 `ports:` 0 | passed |
| ⑤ | `test_env_file_only_on_backend` | postgres `env_file` 0 · backend 1 · caddy 0 | passed |
| ⑥-전제 | `test_secret_detector_catches_samples` | 탐지기가 표본 4종(sk 키·PEM 머리줄·비밀번호 든 DB URL·32자 영숫자)을 실제로 잡고, 비밀번호 없는 URL 은 안 잡는다 | passed |
| ⑥ | `test_no_secret_values_in_deploy_files` | compose·Caddyfile·Dockerfile·entrypoint 에 비밀 패턴 0, `POSTGRES_PASSWORD` 값은 전부 `${POSTGRES_PASSWORD:?` 보간, `:-` 0 | passed |
| ⑦ | `test_required_variables_use_colon_question` | `POSTGRES_USER`·`POSTGRES_PASSWORD`·`POSTGRES_DB`·`SITE_ADDRESS` 는 `:?`, `:-` 기본값 0 | passed |
| ⑧ | `test_restart_unless_stopped_on_all_services` | 세 서비스 모두 `restart: unless-stopped` | passed |
| ⑨ | `test_volumes_declared_and_mounted` | 최상위 `pgdata`·`caddy_data` 선언 + postgres `pgdata:/var/lib/postgresql/data` · caddy `caddy_data:/data` 마운트 | passed |
| ⑩ | `test_backend_database_url_has_no_password` | backend `DATABASE_URL` 이 `postgresql://` · `@postgres:5432/` · 사용자 부분에 `:` 없음 + `POSTGRES_PASSWORD` 보간 존재 | passed |
| ⑪ | `test_caddyfile_routing_contract` | `{$SITE_ADDRESS}` · 호스트명 리터럴 0 · `handle_path /api/*` 안에 `reverse_proxy backend:8000` · 같은 블록 안 `respond @docs 404` 가 `reverse_proxy` 보다 앞 · 매처 집합 == {/docs*, /redoc*, /openapi.json} · 블록 밖 404 respond 0 · `try_files {path} /index.html` · `file_server` · `/sw.js`·`/index.html` no-cache · manifest MIME · `header -Server` | passed |
| ⑫ | `test_entrypoint_migrates_then_execs_single_worker` | `set -e` 계열 · `alembic upgrade head` 줄 < `uvicorn` 줄 · `exec` · `--workers 1` · `app.main:app` | passed |
| ⑬ | `test_dockerfile_stages_user_and_bases` | 단계→기반 이미지 매핑 정확히 {web-build:node:24-slim, caddy:caddy:2-alpine, backend:python:3.13-slim} · backend 마지막 `USER` 가 root/0 아님 · `COPY` 에 `.env` 0 · `npm ci` 앞 `NODE_ENV` 0 | passed |
| ⑭ | `test_dockerignore_excludes_secrets_and_vcs` | `.dockerignore` 에 `.env`·`.env.*`·`.git`·`web/node_modules` 줄 | passed |
| ⑮ | `test_env_example_has_empty_site_address` | `.env.example` 에 값 빈 `SITE_ADDRESS=` 줄 | passed |
| 보조 | `test_compose_backend_dependencies_logging_and_tags` | backend `service_healthy` 의존 · `start_period: 60s` · 헬스체크 URL · 이미지 태그 `${GIT_SHA:-local}` · pg 이미지 · 로그 10m×3 · 세 서비스 `logging: *default-logging` · `${APP_ENV_FILE:-.env}` · `target:` | passed |

실행: `.venv/bin/python -m pytest tests/test_deploy_files.py -v` → **17 passed** (`deploy-files`). 전체: **2219 passed, skip 0** = 기준선 2202 + 17 (`pytest-all`). `ruff check app tests` · `ruff check app tests scripts evaluation` 통과(`ruff`·`ruff-plan-scope`), `tools_check` 7/7(`tools-check`), `mypy_check --run` 38=38(`mypy`), 제품 코드 diff 빈 출력(`product-unchanged` 커밋 구간 · `product-unchanged-worktree` 작업 트리), 기존 테스트 무수정(`tests-unmodified` 빈 출력).

### 변이 → 잡는 테스트 (`mutations` — 무변이 기준선 V0 은 전부 통과, 37종 모두 실패로 감지, 미감지 0)

| 변이 | 내용 | 잡은 테스트 |
|---|---|---|
| V1-1 | postgres 에 `ports: 5432:5432` | ③ |
| V1-2 | backend 에 `ports: 8000:8000` | ④ |
| V1-3a | `POSTGRES_PASSWORD` 리터럴 값 | ⑥ |
| V1-3b | `POSTGRES_PASSWORD` 에 `:-` 기본값 | ⑥ · ⑦ |
| V1-4a | entrypoint 의 `alembic upgrade head` 삭제 | ⑫ |
| V1-4b | `alembic` 을 `uvicorn` 뒤로 | ⑫ |
| V1-5 | `handle_path` → `handle` | ⑪ |
| V1-6 | `--workers 2` | ⑫ |
| V1-7 | `name:` 삭제 | ① |
| V1-8 | `.dockerignore` 의 `.env` 줄 삭제 | ⑭ |
| V1-9 | `USER app` 삭제 | ⑬ |
| V1-10 | Caddyfile 호스트명 하드코딩(`….sslip.io`) | ⑪ |
| V1-11 | `caddy_data` 볼륨(마운트+선언) 삭제 | ⑨ |
| V1-12 | `/sw.js` no-cache 헤더 삭제 | ⑪ |
| V1-13 | postgres 에 `env_file` | ⑤ |
| V1-14 | docs 404 차단 삭제 | ⑪ |
| V1-14b | 404 `respond` 를 `handle_path` 밖 최상위로(F-P9V-1 재현) | ⑪ (+ 스모크 재현: `mut-v14b-smoke` — `/api/docs`·`/api/openapi.json`·`/api/redoc` 이 **200**) |
| V1-14c | 404 `respond` 를 같은 블록의 `reverse_proxy` 뒤로 | ⑪ |
| V1-14d | docs 매처에 `/api` 접두(`/api/docs*`)를 그대로 | ⑪ |
| V1-15 | backend `environment` 의 `POSTGRES_PASSWORD` 삭제 | ⑩ |
| V1-16 | `DATABASE_URL` 에 비밀번호를 넣음 | ⑥ · ⑩ |
| V1-17 | `DATABASE_URL` 호스트를 `localhost` 로 | ⑩ |
| V1-18 | backend 기반 `python:3.14-slim` | ⑬ |
| V1-19 | `npm ci` 앞에 `NODE_ENV=production` | ⑬ |
| V1-20 | `.env.example` `SITE_ADDRESS` 에 값 | ⑮ |
| V1-21 | `SITE_ADDRESS` 의 `:?` 를 보간만으로 | ⑦ |
| V1-22 | postgres `restart` 정책 삭제 | ⑧ |
| V1-23 | entrypoint 의 `exec` 삭제 | ⑫ |
| V1-24 | entrypoint 의 `set -eu` 삭제 | ⑫ |
| V1-25 | Dockerfile 에 `COPY .env` | ⑬ |
| V1-26 | Caddyfile `try_files` 삭제 | ⑪ |
| V1-27 | backend 의존을 `service_started` 로 | 보조 |
| V1-28 | 로그 `max-size` 100m | 보조 |
| V1-29 | 서비스 하나 더(`redis`) | ② |
| V1-30 | compose 에 OpenAI 키 모양 값 | ⑥ |
| V1-31 | `header -Server` 삭제 | ⑪ |
| V1-32 | manifest MIME 헤더 삭제 | ⑪ |

방식: `scratchpad/p9-u1/mutate.py <ID>` 가 배포 파일·테스트 파일을 `mut/<ID>/` 로 복사 → 한 곳을 문자열 치환 → 사본에서 `pytest tests/test_deploy_files.py` → 실패 테스트 이름을 출력(치환 대상 문자열이 없으면 "변이 미적용" 으로 거부). 저장소 파일은 건드리지 않는다(원복 불필요). 계획 외 추가 변이(V1-16~32)는 값 단언 열(`:?`·기반 이미지·`NODE_ENV`·호스트명·`exec`·`set -e` 등)을 직접 두드리려고 더했다.

### 로컬 compose 스모크 (`APP_ENV_FILE=<스크래치 prod.env> CADDY_HTTP_PORT=8088 CADDY_HTTPS_PORT=8443`, 스크래치 변수 파일 — 사용자 `.env` 미사용)

| # | 단계 | 결과 | evidence |
|---|---|---|---|
| ① | `docker compose … config --quiet` | exit 0 | `compose-config` |
| ①′ | 필수 변수 누락(`--env-file /dev/null`) | exit 1 — 누락된 `POSTGRES_PASSWORD`·`SITE_ADDRESS`·`POSTGRES_DB`·`POSTGRES_USER` 이름을 메시지로 거부 | `compose-required` |
| ② | `up -d --build` | exit 0, `relationship-prod-*` 컨테이너·`relationship-prod_pgdata`·`_caddy_data`·`_caddy_config` 볼륨·`relationship-prod_default` 네트워크 | `smoke-up` |
| ③ | 백엔드 healthy 대기 | 최초 폴링에서 `Up 14 seconds (healthy)` | `smoke-wait-healthy` |
| ④ | `GET /api/health` | `200 application/json` · `{"status":"ok","db":"up","alembic_revision":"0002"}` == `alembic heads` `0002 (head)` | `smoke-health` |
| ⑤ | `GET /` | `200 text/html; charset=utf-8` | `smoke-static` |
| ⑥ | `GET /api/persons` | `200 application/json` · `[]` | `smoke-static` |
| ⑦ | S4 헤더 | `/sw.js` `text/javascript; charset=utf-8` + `Cache-Control: no-cache` · `/manifest.webmanifest` `application/manifest+json` · `/index.html` `no-cache` · `/assets/index-DB5EDvsy.js` 200 `text/javascript` · `Server` 헤더 없음 | `smoke-static` |
| ⑧ | S10 docs | `/api/docs` · `/api/openapi.json` · `/api/redoc`(+`/api/docs/oauth2-redirect`·`/api/redoc/x`) 전부 **404**, 대조 `/api/persons` 200 · `/api/nonexistent` 404 `application/json`(백엔드가 답함) | `smoke-docs` |
| ⑨ | 부정: `GET /health` | `200 text/html`(SPA fallback — JSON 아님) | `smoke-static` |
| ⑩ | S7 | `alembic current` `0002 (head)` · `alembic check` `No new upgrade operations detected.` · `pg_extension vector` `0.8.6` · 컨테이너 안 `/health` 같은 본문 · 컨테이너 사용자 `uid=10001(app)` | `smoke-alembic` |
| ⑪ | S13 (기동 2분 뒤) | **키 없음**: `briefing_run` 0행 · Traceback 1(`OpenAIError` — 아래 발견 1) → **더미 키로 재기동**: 130초 뒤 `briefing_run` **2행**(1분 간격 05:28:34·05:29:34 UTC) | `smoke-s13`(키 없음) · `smoke-up-dummykey` · `smoke-wait-2min` · `smoke-s13-dummykey` |
| ⑫ | S17 포트 | `ps`: backend `8000/tcp`·postgres `5432/tcp`(컨테이너 내부 포트뿐), `docker port` 로 postgres·backend 게시 포트 0 · caddy 만 `8088->80`·`8443->443` · 호스트 5432 연결 거부 | `smoke-ports-docker-port`(판정) · `smoke-ports`(8000 nc 는 사용자 개발 uvicorn 이 점유해 무의미 — 판정 아님) |
| ⑬ | backend 로그 Traceback | 더미 키 기동: **0**, `warn` 줄 없음(F-P9V-7: 경고는 `alembic/env.py` 가 출력하지 않음) | `smoke-logs-dummykey` |
| ⑭ | `down`(`-v` 없음) | exit 0 · 이후 `docker volume ls` 에 새 볼륨은 `relationship-prod_caddy_config`·`_caddy_data`·`_pgdata` 3개뿐 | `smoke-down` · `post-volume-ls` |

이미지: `relationship-backend:local` **arm64** · 450MB(`449808080` B) · `User=app` · `/app` 에 `.env` 없음, `relationship-caddy:local` **arm64** · 88.2MB · `/srv` 에 `index.html`·`sw.js`·`manifest.webmanifest`·`assets/` 등 (`smoke-image`). 개발 DB 무영향: `capstone2-postgres-1`(c1399b19337d) 가 스모크 전(`pre-docker-ps`)·중(`mid-dev-compose-ps-capstone2`)·후(`post-docker-ps`) 모두 `Up 2 weeks (healthy)` 5433 그대로, `docker compose ls`(`pre-`/`mid-`/`post-compose-ls`)에 `relationship-prod` 가 스모크 중에만 나타났다 사라지고 `capstone2`·`broker-agent` 불변, 기존 볼륨 `capstone2_pgdata`·`relationship_pgdata`·`broker-agent_pgdata` 불변(`pre-`/`post-volume-ls`).

판정 표 #4 비밀 grep: 계획의 정규식은 `${NAME:?메시지}` 의 `:?` 를 값으로 오인해 `docker-compose.prod.yml` 2줄(전부 `${POSTGRES_PASSWORD:?…}` 보간)을 잡는다(`smoke-secretgrep` — 새 파일이 추적 전이라 `git grep` 이 trivially 빈 출력). 제외 문자 집합에 `?` 를 더한 보정 정규식은 **일치 0**, 리터럴 표본 3줄은 잡는다(`secret-grep-fixed`).
