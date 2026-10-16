# P8-frontend U10 — 기존 자동 테스트가 "배포 환경"에서도 유효한지 점검 (읽기 전용)

검토자: verifier (fable)
요청: 사용자 2026-10-16 "기존 테스트 방식이 배포환경에서 실제로 유효한 테스트들이었는지 점검해줘" → 메인 세션 위임(읽기 전용, 코드·테스트·계획 무변경)
기준: `docs/backlog.md` 91~93행(P9 미착수) · CLAUDE.md 기술 스택 · D7 카드(`docs/wiki/decisions/D07-tls-caddy.md`) · 01-plan 46·242~252·375·386행(결정 C(ii), 운영은 P9) · `docs/reliability.md` K 절·2절 · `tests.md` · `docs/wiki/verification.md`
HEAD: `735f391` (dev2), 미커밋 변경은 `docs/wiki/` 문서·증거뿐(`gitlog.sh`)

결과: **판정 대상이 아니라 분류다 — 기존 테스트는 "앱 논리 + 실 PostgreSQL 위의 인프로세스 API" 에는 유효하고, "HTTP 경계 밖(Caddy·CloudFront·HTTPS·S3 정적 서빙·RDS·실 공급자·실 푸시·인증)" 에는 전부 무효(미검증)다. [필수] 4 · [권고] 6 (R-U10D-1~10).** 메인 세션 전제 중 틀린 것 2개를 §1 에서 바로잡았다(`Dockerfile` 은 없고, Vitest 는 136 건).

---

## 0. 결론 한 문단

백엔드 pytest 1953 건(74 파일) 중 42 파일은 실 PostgreSQL(pgvector/pg16, `alembic upgrade head`)에 붙어 롤백으로 돌고 그중 15 파일은 FastAPI `TestClient` 로 **같은 ASGI 앱 객체**를 인프로세스 호출한다 — DB 스키마·트랜잭션 경계·동시성(SKIP LOCKED, upsert)·응답 모양은 배포에서도 그대로 유효하다. 26 파일은 환경 무관 순수 논리(ER 확신도·규칙·평가 지표·SDK 예외 매핑)라 어디서나 유효하다. 6 파일은 개발 전용 구성(docker-compose 포트 5433 기본값·테스트 DB 이름·확인 페이지·점검 스크립트)을 시험하므로 배포와 무관하다. 프론트 Vitest 136 건(9 파일) 중 7 파일은 jsdom + 가짜 `fetch` 위의 화면 논리이고, 2 파일(`proxy.test.ts`·`network.test.ts`)은 개발 서버 프록시와 테스트 안전망 자체를 시험한다. Playwright E2E 4 건은 실제 Chromium + `vite preview` 빌드 산출물(S3 에 올릴 그 번들)을 돌리지만 `/api/**` 를 전부 가짜 표가 답하므로 프론트–백엔드 계약은 **TS 타입 수동 복사 + 이번 점검의 기계 대조(32/32 모델 불일치 0)** 외에 자동 검사가 없다. 어떤 테스트도 `Dockerfile`(없음)·CI 이미지 빌드/기동(0 단계)·`/api` 접두 제거(Caddy `handle_path`)·CloudFront 경로 동작·HTTPS·S3 MIME/캐시 헤더·RDS(확장 생성 권한·SSL·마이그레이션 실행 주체)·실 LLM/임베딩 지연·실 VAPID 발송·HTTPS 출처의 서비스 워커/PWA 설치·인증 없음(공개 쓰기 API) 을 건드리지 않는다 — 이것들이 P9 스모크의 대상이다(§9).

## 1. 전제 확인 — 메인 세션 전제와 다른 것

| 전제 | 확인 결과 | 증거 |
|---|---|---|
| "배포 P9 미착수" | 맞음. `docs/backlog.md` 93행 `- [ ] [infra-agent(신설)] Terraform + GitHub Actions + Caddy TLS / 의존: P8`. `docs/wiki/packages/` 에 P9 폴더 없음 | `ls docs/wiki/packages/` (P0~P8 만) |
| "Dockerfile·docker-compose 를 읽어라" | **`Dockerfile` 이 없다.** `docker-compose.yml` 은 `postgres` 서비스 하나(앱 서비스 없음, 3~20행) | `evidence/20261016-1920-verifier-u10-deploy-validity-ci.txt` `[Dockerfile 존재]` → `No such file` |
| "백엔드 pytest 1953 건" | 맞음. `--collect-only -q` → `1953 tests collected` | `…-counts.txt` |
| "프론트 Vitest 135+1 건" | **136 건**(U10 `fix-card-align` 뒤). `vitest list` 는 133 줄인데 `it.each` 를 한 줄로 접기 때문이다(routes 3행→1, chat 2행→1: 133+2+1=136) | `…-counts.txt` 파일별 건수 · `evidence/20261016-1918-u10-fix-card-align-vitest.txt` 16행 `Tests 136 passed (136)` |
| "E2E 4 건" | 맞음. `Total: 4 tests in 3 files` | `…-counts.txt` |
| "CI ubuntu/windows 런너" | 맞음. job 3개(`pytest` 3.13/3.14 ubuntu · `windows` · `web` ubuntu/windows) | `.github/workflows/tests.yml` 25·116·153행 |
| "LLM·임베딩은 가짜" | 맞음. 운영 의존성 `get_proposer/get_judge/get_embedder/get_fact_extractor/get_briefing_composer` 를 `dependency_overrides` 로 바꾼다 | `app/api/deps.py` 245~310행(`get_proposer` 245 · `get_judge` 253 · `get_embedder` 260 · `get_fact_extractor` 271 · `get_briefing_composer` 293), `tests/conftest.py` `fake_embedder`(148행)·`grouped_embedder`(175행) |

## 2. 분류 기준

| 분류 | 뜻 |
|---|---|
| ① 배포에서도 그대로 유효 | 환경 상수·외부 자원 없이 논리만 시험. 어디서 돌려도 같은 뜻 |
| ② 환경 의존 — 배포 모양과 같음 | 실 PostgreSQL(pgvector, alembic head) 또는 같은 ASGI 앱 객체(`TestClient`)를 쓴다. DB·앱 코드 부분은 배포와 같고, **HTTP 서버·프록시 경계는 거치지 않는다** |
| ③ 환경 의존 — 개발 전용 | 배포에서 쓰지 않는 코드·구성(개발 서버 프록시, docker-compose 포트 기본값, 테스트 DB 이름, 확인 페이지, 점검 스크립트, 테스트 안전망)을 시험 |
| ④ 덮지 못하는 배포 위험 | 그 파일이 다루는 주제 중 **배포에서만 생기는** 부분. 분류 열이 아니라 보조 열로 적는다(①②③ 어느 파일에도 붙을 수 있다) |

근거 집계는 `evidence/20261016-1925-verifier-u10-deploy-validity-pytest-table.txt`(파일별 `dbtest`·`TestClient`·`monkeypatch`·가짜 LLM·가짜 임베딩·`setenv`·고정 시계·줄 수) 와 `…-survey.txt` §(2)(프론트 파일별 `vi.fn`·`fetch`·`stubGlobal`·`page.route`·`serviceWorker`·`Notification`·`pushManager`·`localStorage`). `dbtest` 를 언급만 하고 마커가 없는 3 파일(`test_briefing_compose`·`test_memory_extract`·`test_validate_scenarios`)은 Windows CI(`-m "not dbtest"`, DB 접속 정보 없음, `tests.yml` 141~148행)에서 통과하므로 DB 비의존이다.

## 3. 백엔드 pytest — 74 파일 분류 (묶음 단위, 파일 전수)

### 3.1 ② 실 PostgreSQL + `TestClient` 인프로세스 API — 15 파일

`test_api.py` · `test_api_chat.py` · `test_api_answers_resume.py` · `test_api_briefings.py` · `test_api_questions_pending.py` · `test_api_read_persons.py` · `test_api_read_raw.py` · `test_api_read_briefings.py` · `test_api_read_briefings_e2e.py` · `test_answer_concurrency.py` · `test_commit_boundaries.py` · `test_briefing_scheduler.py` · `test_memory_loop.py` · `test_push_subscriptions.py` · `test_push_wiring.py`

| 무엇이 배포와 같은가 | 근거 |
|---|---|
| 앱 객체: `create_app()` 그대로(`app/main.py` 197행 `app = create_app()` 이 uvicorn 진입점) — 라우트·예외 매핑·응답 모델이 동일 | `app/main.py` 175~197행 |
| DB: 실 PostgreSQL, `CREATE EXTENSION vector` + `alembic upgrade head` 적용본, 바깥 트랜잭션 롤백 | `tests/conftest.py` 96~130행 `db_engine`/`db_session`(129행 `outer_transaction.rollback()`), `tests/db_bootstrap.py` 84~137행(`ensure_test_database_ready` → 137행 `command.upgrade(cfg, "head")`) |
| 동시성: 두 요청이 같은 질문에 답할 때 409 (실 DB 잠금) | `test_answer_concurrency.py`(dbtest 4·TestClient 2) |
| 세션 헤더 규약 `X-Session-Id` 검증·발급 | `app/api/deps.py` 201~214행 `resolve_session_id`, `test_api_questions_pending.py` |

| ④ 덮지 못하는 배포 위험 | 근거 |
|---|---|
| HTTP 서버(uvicorn)·Caddy·CloudFront 를 **거치지 않는다** — 헤더 통과(`X-Session-Id` 가 CloudFront 캐시 정책에서 전달되는지), 본문 크기, 프록시 타임아웃, `X-Forwarded-*`, `/api` 접두 제거 | `TestClient` 는 ASGI 직접 호출; `tests.yml` 에 `uvicorn`·`curl` 0 (`…-ci.txt`) |
| DB 가 RDS 가 아니다 — 버전·SSL(`sslmode` 미지정, `app/db/session.py` 44~46행은 `pool_pre_ping=True, connect_args={"connect_timeout": 5}` 뿐)·네트워크 지연·확장 생성 권한 | `…-ci.txt` `[sslmode …]` |
| `test_briefing_scheduler.py` 의 lifespan 은 `TestClient` 컨텍스트 수명 — 실 프로세스 수명·`uvicorn --workers N` 에서 워커마다 뜨는 lifespan 은 미검증(중복 브리핑 자체는 `select.py` 62·81행 `with_for_update(skip_locked=True)` 가 막는다) | `app/main.py` 156~173행 `_lifespan` |
| `test_push_wiring.py`·`test_push_subscriptions.py`: 실 FCM 엔드포인트·실 VAPID 서명 0 | §3.2 푸시 행 |

### 3.2 ② 실 PostgreSQL, HTTP 없음(툴·ER·메모리·브리핑·푸시 발송) — 20 파일

`test_agent_loop.py` · `test_agent_timezone.py` · `test_tools_briefing.py` · `test_tools_context.py` · `test_tools_persons.py` · `test_tools_questions.py` · `test_tools_records.py` · `test_er_candidates.py` · `test_er_pipeline.py` · `test_memory_patterns.py` · `test_memory_promote.py` · `test_briefing_inputs.py` · `test_briefing_run.py` · `test_briefing_select.py` · `test_fact_updated_at.py` · `test_upsert_concurrency.py` · `test_db_session.py` · `test_push_notifier.py` · `test_scenario_state.py` · `test_backfill_embeddings.py`

| 무엇이 배포와 같은가 | 근거 |
|---|---|
| 별칭 임베딩 top-K → 인물별 max(pgvector 연산 실행), 부분 인덱스·upsert 고유키 | `test_er_candidates.py`(fakeEmb 21), `test_upsert_concurrency.py`(dbtest 6) |
| 일정 잠금 `FOR UPDATE SKIP LOCKED` 가 실 DB 에서 동작 | `test_briefing_select.py`(dbtest 13), `app/briefing/select.py` 62행 |
| 시간대: 시스템 시간대 의존 코드 0(`datetime.now()` 무인자·`astimezone()` 무인자 0건, ruff `DTZ` 켜짐 `pyproject.toml` 12행) → Mac(KST)·EC2(UTC) 차이에 무관. `APP_TIMEZONE` 만 결과를 바꾼다 | `test_agent_timezone.py` 240~253행 |

| ④ 덮지 못하는 배포 위험 | 근거 |
|---|---|
| 임베딩은 결정적 가짜(`_deterministic_vector`, sha256 시드) — 실 OpenAI 벡터 분포·지연·429 미검증 | `tests/conftest.py` 133~146행 |
| `test_push_notifier.py`: `pywebpush.webpush` 는 autouse 로 "불리면 실패"(결정 G) — 실 FCM·VAPID 서명·구독 만료(410) 처리는 미검증. P7 U8 에서 데스크톱 Chrome 실수신 1회(`6428180`, CURRENT.md P7 메모)가 유일한 실측 | `tests/test_push_notifier.py` 9~11·67·81행 |
| `test_backfill_embeddings.py`: 운영 DB 규모·배치 비용 미검증 | 스크립트 테스트, dbtest 3 |

### 3.3 ② 실 PostgreSQL — 평가·베이스라인 — 7 파일

`test_baseline_embedding_only.py` · `test_baseline_exact_match.py` · `test_baseline_llm_single.py` · `test_baseline_parity.py` · `test_baseline_proposed.py` · `test_eval_runner.py` · `test_run_pilot_eval.py`

배포와 무관한 평가 도구(`evaluation/`, `scripts/run_pilot_eval.py`)지만 실 DB 위에서 돈다. 배포 환경에서 실행할 일이 없으므로 ④ 없음. 다만 `test_baseline_llm_single.py`(가짜 LLM 35) 가 실 LLM 판정의 대체물이 아니라는 점은 §3.4 와 같다.

### 3.4 ① 환경 무관 논리 — 26 파일

`test_agent_gate.py` · `test_agent_types.py` · `test_agent_propose.py` · `test_baseline_base.py` · `test_embedding_provider.py` · `test_er_confidence.py` · `test_er_dictionary.py` · `test_er_judge.py` · `test_er_rules.py` · `test_er_smoke.py` · `test_er_types.py` · `test_eval_calibration.py` · `test_eval_curve.py` · `test_eval_metrics.py` · `test_eval_report.py` · `test_import_order.py` · `test_properties.py` · `test_push_payload.py` · `test_push_settings.py` · `test_schema_models.py` · `test_settings.py` · `test_tool_signatures.py` · `test_tools_types.py` · `test_briefing_compose.py` · `test_memory_extract.py` · `test_validate_scenarios.py`

| 무엇이 유효한가 | 근거 |
|---|---|
| 확신도 결합·임계치 2개·규칙 감점(원칙2·3) — 순수 함수 | `test_er_confidence.py`(682줄, dbtest 0) |
| 실 공급자 클래스(Anthropic·OpenAI·Gemini 판정기/제안기/추출기/문장기)의 **SDK 예외 → 도메인 예외 매핑**(타임아웃·429·4xx/5xx·연결 오류·재시도 1회) | `test_er_judge.py` 396~625행 10 테스트, `test_agent_propose.py` 435~463행, `test_memory_extract.py` 502~534행 |
| VAPID 설정 3상태(전무/반쪽/전부) 해석, 푸시 페이로드 모양 | `test_push_settings.py`·`test_push_payload.py` |
| 스키마 모델 정의(컬럼·타입·인덱스 선언) — DB 없이 메타데이터만 | `test_schema_models.py` |

| ④ 덮지 못하는 배포 위험 | 근거 |
|---|---|
| 실 공급자 테스트는 **SDK 클라이언트를 가짜로** 바꾼 것(HTTP 전송 가짜 아님) — 실 응답 지연·실 429 빈도·토큰 비용·모델명 유효성(`ANTHROPIC_MODEL=claude-sonnet-5` 등 `.env.example`)은 어떤 테스트도 보지 않는다 | `…-pytest-table.txt` 마지막 절 `[실 공급자 … 가짜 전송]` 0 파일; `test_embedding_provider.py` 161행은 가짜 클라이언트 1회 호출 단언 |
| `test_embedding_provider.py` 109·122행: 키 없음 → 사람이 읽는 오류 / 키 값 미노출만 — 키가 **틀린** 경우(401) 미검증 | 같은 파일 `def test_` 목록 |

### 3.5 ③ 개발 전용 구성 — 6 파일

| 파일 | 무엇을 전제하나 | 배포에서는 |
|---|---|---|
| `test_config.py` | `POSTGRES_*` 조립 기본값 `localhost/5433`(28~42행) — docker-compose 호스트 포트 매핑(FIX-012, `app/config.py` 34~38행 주석) | RDS 는 `DATABASE_URL` 로 주입(5432). 기본값 갈래는 쓰이지 않는다 |
| `test_conftest_test_db.py` | 테스트 DB 이름 `relationship_test` 충돌 방지(FIX-006), `@dbtest` 2건 | 테스트 전용 |
| `test_db_check.py` | `scripts/db_check.py` 접속 정보 조립(DB 없이) | 점검 스크립트 |
| `test_schema_check.py` | `scripts/schema_check.py` 집계·CLI 파싱(DB 없이) | 점검 스크립트 |
| `test_embed_pilot.py` | `scripts/embed_pilot.py` (D4 파일럿) | 파일럿 |
| `test_push_devpage.py` | `PUSH_DEV_PAGE_ENABLED` 확인 페이지 `/push-dev/*`(`app/main.py` 86행 `_register_push_dev_page`) — 운영은 비움(01-plan 386행) | 경로 자체가 없어야 함 → §9 스모크 부정 항목 |

## 4. 프론트 Vitest 9 파일 · E2E 3 파일 분류

| 파일 | 건수 | 분류 | 가짜로 대체하는 것 (근거 `…-survey.txt` §2) | ④ 덮지 못하는 배포 위험 |
|---|---|---|---|---|
| `api.test.ts` | 6 | ① | `fetch` 7·`stubGlobal` 6. `API_BASE='/api'` 상수와 422 `invalid_session_id` 세션 폐기 논리 | `/api` 가 운영에서 CloudFront→Caddy 로 벗겨지는지 |
| `chat.test.tsx` | 22 | ① | `fetch` 5·`localStorage` 5 | — |
| `card.test.tsx` | 30 | ① | `fetch` 2·`stubGlobal` 2·`?raw` 소스 검사 | — |
| `briefing.test.tsx` | 19 | ① | `fetch` 2·`stubGlobal` 2 | — |
| `routes.test.tsx` | 14 | ① | 해시 라우팅(`#/chat` 등) — **배포에 유리**: 깊은 링크에 SPA 폴백(S3 404→index.html) 이 필요 없다 | 루트(`/`) 배포 전제(`manifest.webmanifest` `scope:"/"`, `start_url:"/#/chat"`) |
| `push.test.ts` | 21 | ① | `serviceWorker` 6·`Notification` 3·`pushManager` 4·`fetch` 3 전부 가짜 | HTTPS 출처의 실 등록·권한 창·실 `pushManager.subscribe`(FCM)·`POST /push/subscriptions` 실 저장 |
| `sw.test.ts` | 16 | ① | `sw.js` 를 `?raw` 로 읽어 가짜 `self` 에서 평가(`new Function`), `Notification` 7 | 실 워커 설치·`skipWaiting`/`claim` 동작·`sw.js` MIME/캐시 헤더·`pathname === "/"` 앱 창 판별의 루트 배포 가정(`reliability.md` 214행) |
| `network.test.ts` | 2 | ③ | 테스트 안전망(`test-setup.ts` 10~12행 전역 `fetch` 를 "불리면 실패") 자체를 시험 | — (배포와 무관) |
| `proxy.test.ts` | 6 | ③ | `resolveApiTarget`·`stripApiPrefix`(`web/src/proxy.ts`) — **Vite 개발 서버 프록시 전용**(`vite.config.ts` 22~29행 `server.proxy`, 27행 `rewrite: stripApiPrefix`, 빌드 산출물에 들어가지 않음) | 운영의 접두 제거는 Caddy `handle_path /api/*`(01-plan 243행) — 이 테스트가 그 동작을 보증하지 않는다 |
| `e2e/chat.spec.ts` | 1 | ② | 실제 Chromium + `vite preview` 빌드(배포에 올릴 번들과 같은 `npm run build`, `playwright.config.ts` 21행). `page.route('**/api/**')` 가 전부 답함(`fixtures.ts` 54~75행), 외부 출처 요청 차단(48~50행), `serviceWorkers: 'block'`(17행), 시계 고정 | 백엔드 응답 **값**은 표가 만든 것 — 계약은 §7 수동 대조뿐. HTTP(4173, http) 라 HTTPS 전용 API(SW·푸시·PWA 설치) 0 |
| `e2e/card.spec.ts` | 2 | ② | 같음 | 같음 |
| `e2e/briefing.spec.ts` | 1 | ② | 같음 | 같음 |

## 5. 집계

| 구분 | ① 환경 무관 | ② 배포와 같음(부분) | ③ 개발 전용 | 합계 |
|---|---|---|---|---|
| 백엔드 pytest 파일 | 26 | 42 (HTTP 15 · DB 20 · 평가 7) | 6 | 74 |
| 프론트 Vitest 파일 | 7 (130 건) | 0 | 2 (8 건) | 9 (136 건) |
| E2E 파일 | 0 | 3 (4 건) | 0 | 3 |
| **합계(파일)** | **33** | **45** | **8** | **86** |

④ 는 보조 열이라 파일 수로 세지 않는다. 배포에서만 생기는 위험 중 **어떤 파일도 덮지 않는 것**은 §6 에 따로 센다(15 항목).

## 6. 배포 구성 중 테스트가 전혀 건드리지 않는 것 — 15 항목

| # | 항목 | 지금 상태 | 근거 |
|---|---|---|---|
| 1 | `Dockerfile` / 앱 컨테이너 이미지 | **없음.** compose 는 `postgres` 만 | `…-ci.txt` |
| 2 | CI 의 이미지 빌드·기동·`/health` | **0 단계.** `tests.yml` run 단계 16개 모두 pip/ruff/pytest/alembic/mypy/test-guards/npm (65~184행), `docker`·`curl`·`uvicorn` 0 | `…-ci.txt` `[tests.yml 에서 docker…]` → `(없음)` |
| 3 | CloudFront 경로 동작(`/api/*` → EC2, 기본 → S3) | 설계만(01-plan 243행). 접두가 안 벗겨지면 `GET /api/persons` 가 uvicorn 의 `/api/persons`(없음) → 404 | `app/api/routes.py` 라우트 12개 전부 접두 없음(176~488행) |
| 4 | Caddy `handle_path /api/*`·Let's Encrypt | 01-plan 252행 "Caddy 문서를 열지 않았다 — **확인 필요**" 그대로 | D7 카드 "적용 시점 P9-infra" |
| 5 | HTTPS(CloudFront 오리진 HTTPS, ACM us-east-1) | 미구성 | D7 |
| 6 | CORS | 미들웨어 없음(`CORSMiddleware` 0건) — 결정 C(ii) 같은 출처라 **의도된 것**. 교차 출처(`api.도메인`)로 바꾸면 즉시 장애 | `…-ci.txt` `[CORSMiddleware 사용]` → `(없음)` |
| 7 | 정적 파일 MIME·캐시: `manifest.webmanifest` content-type, `sw.js` `application/javascript` + `Cache-Control: no-cache`(01-plan 386행 권고) | S3 메타데이터·CloudFront 정책 미정 | `web/index.html` 6행 manifest 링크, `web/src/push.ts` 7행 `'/sw.js'` |
| 8 | 루트 배포 전제 | `manifest` `scope:"/"`·`start_url:"/#/chat"`, `sw.js` 앱 창 판별 `pathname === "/"`(63행), `vite.config.ts` `base` 미지정 | 하위 경로 배포면 전부 깨짐 — 스모크로 못 박을 것 |
| 9 | 환경변수 이름 ↔ SSM 파라미터 | 코드가 읽는 이름 22개(`…-survey.txt` §1) + SDK 가 직접 읽는 `ANTHROPIC_API_KEY`·`GEMINI_API_KEY`(`scripts/er_smoke.py` 44·46행이 이름만 참조). `.env.example` 에만 있고 코드가 읽지 않는 이름 **3개: `APP_ENV`·`EMBEDDING_MODEL`·`EMBEDDING_PROVIDER`** (`app/`·`scripts/`·`alembic/` grep 0) | R-U10D-5 |
| 10 | RDS: `CREATE EXTENSION vector` 권한(`alembic/versions/0001_schema_v2.py` 56행 `op.execute`), `alembic upgrade head` 실행 주체·시점(배포 파이프라인 없음), `sslmode` 미지정(psycopg 기본 `prefer`), 벡터 인덱스 없음(`hnsw`·`ivfflat` 0건 → 순차 스캔) | CI 왕복은 `pgvector/pg16` 컨테이너(`tests.yml` 93~100행) | `…-ci.txt` |
| 11 | 인증 없음(F-fbaaae) | 공개 URL 에서 누구나 `POST /api/chat`(실 LLM 비용·데이터 오염)·`POST /api/push/subscriptions`. `backlog.md` 106행 "**P9 배포 전에 다시 꺼내야 하는 부채**" | `app/api/deps.py` `app_user_id()` 고정 |
| 12 | `/docs`·`/openapi.json` 공개 | FastAPI 기본 켜짐(`create_app()` 의 `FastAPI(...)` 에 `docs_url=None` 없음, `app/main.py` 180행). `sw.js` 60행 주석이 `/api/docs` 를 "개발용 창"으로 언급 — CloudFront 를 통해 그대로 노출 | — |
| 13 | 브리핑 스케줄러 프로세스 모델 | `BRIEFING_SCHEDULER_ENABLED=1` 이면 lifespan 이 **워커마다** 태스크를 띄움(`app/main.py` 156~173행). 중복 브리핑은 SKIP LOCKED 가 막지만(`select.py` 62행) 워커 수·재기동 정책은 미정 | `docs/RUNNING.md` 247행은 단일 `uvicorn` |
| 14 | 실 LLM·임베딩 지연/429/비용, 실 VAPID 발송 | 자동 0. 사람 점검: U10 FIX-035(`evidence/20261016-1915-u10-check-chat-fix035.txt`, **Vite 5173 → uvicorn 8000 개발 프록시**로 함 — 운영 경로 아님) · P7 U8 실수신 1회 | `reliability.md` K 절 |
| 15 | AWS Budgets 알림($10/$30/$50), 로그 수집 | CLAUDE.md "첫날 필수" — 코드·테스트 밖 | — |

## 7. 프론트–백엔드 계약 대조 (`app/api/schemas.py` ↔ `web/src/api/types.ts`)

증거: `evidence/20261016-1920-verifier-u10-deploy-validity-contract.txt` (스크래치패드 스크립트 — pydantic `class X(BaseModel)` 필드와 TS `export interface X` 필드를 이름·null·선택성으로 대조).

| 항목 | 결과 |
|---|---|
| pydantic 모델 33 / TS interface 32 | TS 에 없는 모델 = `HealthOut` 1개 — 프론트가 `/health` 를 부르지 않으므로(`client.ts` 호출 함수 11개에 없음) 정상 |
| 공통 32 모델 필드 이름 | 누락 0 · 초과 0 |
| null 가능성(`X | None` ↔ `X | null`) | 불일치 0 (`pending_question`·`stop_reason`·`suggestion`·`last_contact_at`·`briefed_at`·`expirationTime`·`schedule_id`) |
| TS 선택(`?`) ↔ py 기본값 | `BriefingRunIn.schedule_id`·`PushSubscriptionIn.expirationTime` 둘 다 py 기본값 있음 — 일치 |
| 타입 대응 | `datetime`↔`IsoDateTime(string)`, `Literal["llm","template"]`↔`BriefingComposer`, `float`↔`number` — 일치. 프론트 `formatDateTime` 은 `new Date(iso)` 라 pydantic 의 `Z`/`+00:00` 접미 모두 읽는다(`web/src/lib/format.ts`) |
| 경로·메서드 | 프론트 호출 11개(`client.ts`) ↔ 백엔드 라우트 12개(`routes.py` 176~488행) — `/health` 만 프론트 미사용, 나머지 11:11 |
| 오류 코드 문자열 | `invalid_session_id`(app 1 / web 2)·`push_not_configured`(2/1)·`not_found`(4/3) 양쪽 존재. `already_answered`·`expired` 는 프론트가 상태 409 로만 다루고 코드 문자열은 테스트에서만 사용(`chat.test.tsx` 304행 `it.each(['already_answered','expired'])`) — 어긋남 아님 |

**어긋남 0 → [필수] 없음.** 다만 이 대조는 이번에 손으로 한 번 한 것이고 자동 검사가 아니다(R-U10D-2). `types.ts` 1행 주석 "손으로 옮긴 TS 타입" 그대로다.

## 8. CI 가 Docker 이미지 빌드·기동·`/health` 를 검사하는가

**아니오.** `tests.yml` 의 run 단계는 pip·ruff·pytest(+skip 검출)·alembic 왕복·mypy 기준선·test-guards·npm ci/typecheck/test/build·playwright 뿐(`…-ci.txt` `[tests.yml 의 run 단계 전부]` 16줄). `GET /health` 는 `tests/test_api.py` 84·98행이 `TestClient` 로만 부른다(200 `{"status":"ok","db":"up","alembic_revision":…}` / `get_session` 오버라이드로 503 degraded). 이미지가 없으므로 "컨테이너가 뜨고 DB 에 붙는다" 는 어떤 자동 검사에도 없다.

## 9. P9 에 넣어야 할 배포 대상 스모크 테스트 제안

판정 기준은 전부 기계 판정 가능한 값으로 적었다. "자동" = 배포 워크플로(GitHub Actions post-deploy job) 에서 `curl`/Playwright/`python -c` 로 돌릴 수 있음. "반자동" = 브라우저 권한·실 기기가 필요. "사람" = 눈으로.

| # | 항목 | 명령·판정 기준 | 자동화 | §6 위험 |
|---|---|---|---|---|
| S1 | 컨테이너 기동 + 헬스 | `docker build` → `docker run` + compose postgres → `curl -fsS http://localhost:8000/health` 가 `{"status":"ok","db":"up","alembic_revision":"<head>"}`. `alembic_revision` 은 `alembic heads` 출력과 같아야 함 | 자동 — **P9 전에 지금 CI 에 넣을 수 있다** | 1·2 |
| S2 | 배포 URL 헬스(경로 동작 + 접두 제거) | `curl -fsS https://<domain>/api/health` 200 + 같은 본문. **부정**: `curl -s -o /dev/null -w '%{http_code}' https://<domain>/health` 는 200 이 아니어야 함(CloudFront 기본 동작 → S3 라 `/health` 는 index.html 200 이 돌아올 수 있음 — 그러면 `content-type: text/html` 로 판정) | 자동 | 3·4 |
| S3 | TLS | `curl -fsS https://<domain>/`(`-k` 없이) 성공, `curl -sI http://<domain>/` 가 301/308 → https | 자동 | 5 |
| S4 | 정적 파일 MIME·캐시 | `curl -sI https://<domain>/sw.js` → `content-type: application/javascript` 또는 `text/javascript`, `cache-control` 에 `no-cache`/`max-age=0`; `/manifest.webmanifest` → `application/manifest+json`; `/` → `text/html`; `/assets/` 해시 파일 200 | 자동 | 7·8 |
| S5 | 읽기 계약(실 백엔드, LLM 0) | `GET /api/persons`·`/api/briefings`·`/api/questions/pending`(헤더 없음 → `[]`)·`/api/push/vapid-public-key`(200 또는 404 `push_not_configured`) 응답 JSON 을 `python -c "from app.api.schemas import *; PersonListItemOut.model_validate(...)"` 로 검증. E2E `fixtures.ts` 의 `page.route` 를 끄고 같은 spec 의 **읽기 부분만** 배포 URL 로 1회 | 자동(pydantic 검증) · 반자동(E2E) | 3·4·§7 |
| S6 | 쓰기 계약 1회(실 LLM) | `POST /api/chat {"utterance":"<고정 문장>"}` → 200, `ChatOut.model_validate` 통과, `trace_ids` 비어 있지 않음, 응답 시간 기록(`%{time_total}`). 답 내용은 단언하지 않는다(비결정) | 자동(모양만) | 14 |
| S7 | DB 마이그레이션(RDS) | 배포 job 에서 `DATABASE_URL=<RDS>` 로 `alembic upgrade head` → `alembic current` 가 head 와 같음 → `alembic check` "No new upgrade operations detected." → `SELECT extversion FROM pg_extension WHERE extname='vector'` 1행 | 자동 | 10 |
| S8 | DB 접속 SSL | `SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()` → `t`(RDS `rds.force_ssl` 정책에 맞춰 기대값 고정) | 자동 | 10 |
| S9 | 환경변수 이름 대조 | SSM 경로 목록(이름만) ↔ `…-survey.txt` §1 의 22개 + SDK 2개 — 빠진 이름 0, 코드가 읽지 않는 이름 0. `PUSH_DEV_PAGE_ENABLED` 비움 확인: `curl -s -o /dev/null -w '%{http_code}' https://<domain>/api/push-dev/` → 404 | 자동 | 9·§3.5 |
| S10 | 공개 노출 정책 | `GET /api/docs`·`/api/openapi.json` 의 기대 상태를 **먼저 결정**(404 또는 200)하고 그 값으로 단언. 인증 없음 상태로 공개할지(F-fbaaae) 는 P9 착수 조건 | 자동(결정 뒤) | 11·12 |
| S11 | 서비스 워커·PWA(HTTPS 출처) | Playwright `serviceWorkers:'allow'` + `context.grantPermissions(['notifications'])` 로 배포 URL 열고 "알림 받기" 클릭 → `navigator.serviceWorker.getRegistration('/')` 가 `active` 이고 `scope` 가 `https://<domain>/`; `pushManager.getSubscription()` non-null; 서버 `push_subscriptions` 행 +1. Manifest 설치 가능성은 DevTools Application 탭(사람) | 반자동 | 7·8·14 |
| S12 | 실 푸시 발송 | 일정 1건 만들고 `POST /api/briefings/run {"schedule_id":N}` → `briefings[0].push == "sent"`; 수신은 사람(U8 방식) | 자동(서버 쪽) · 사람(수신) | 14 |
| S13 | 스케줄러 | `BRIEFING_SCHEDULER_ENABLED=1` 배포 뒤 2분 내 `agent_traces` 에 `step='briefing_run'`·`trigger='scheduler'` 행 ≥1; 워커 수 N 일 때도 같은 `schedule_id` 의 `briefing_compose` 행이 1개 | 자동 | 13 |
| S14 | 세션 헤더 통과 | `POST /api/chat` 응답 `session_id` 를 `X-Session-Id` 로 `GET /api/questions/pending` 에 보내 그 세션의 질문이 오는지(CloudFront 가 헤더를 오리진에 전달하는지) | 자동 | 3 |
| S15 | 예산 알림 | AWS Budgets 3단계 존재 — Terraform `aws_budgets_budget` 리소스 plan 출력에 3개 | 자동(terraform plan) | 15 |

S1·S9(이름 대조)·§7 대조 스크립트 세 가지는 **P9 전에 지금 CI 에 추가 가능**하다.

## 10. 소견

### [필수]

- **R-U10D-1 — `Dockerfile` 없음 + CI 에 이미지 빌드·기동·`/health` 0.** 배포 단위(컨테이너)가 정의돼 있지 않아 "배포 환경에서 유효한가" 를 지금 측정할 대상 자체가 없다. P9 첫 단위에서 `Dockerfile` 과 S1 을 CI 에 넣는다(§6 1·2, §8).
- **R-U10D-2 — `/api` 접두 제거·CloudFront 경로 동작·정적 MIME/캐시 헤더가 어떤 테스트에도 없다.** `proxy.test.ts` 6 건은 개발 서버 전용이라 운영 보증이 아니다(§4). 01-plan 252행 "Caddy `handle_path` 확인 필요" 가 열린 채다. P9 수용 기준에 S2·S4 를 글자 그대로 넣는다.
- **R-U10D-3 — 인증 없음 상태의 공개 배포 정책 미결(F-fbaaae).** `backlog.md` 106행이 "P9 배포 전에 다시 꺼내야 하는 부채" 라 적었고, 공개 URL 에서 `POST /api/chat` 이 실 LLM 비용을 쓴다. P9 착수 전 사용자 결정(공개 범위·`/api/docs` 노출·최소 보호) → S10 으로 단언.
- **R-U10D-4 — RDS 마이그레이션 실행 주체·확장 권한·SSL 이 미정이고 테스트는 로컬 컨테이너만 본다.** `0001` 의 `CREATE EXTENSION`(56행)은 RDS 에서 권한이 필요하고, `alembic upgrade head` 를 누가 언제 돌리는지 파이프라인이 없다. P9 에 S7·S8.

### [권고]

- **R-U10D-5 — `.env.example` 에 코드가 읽지 않는 이름 3개(`APP_ENV`·`EMBEDDING_MODEL`·`EMBEDDING_PROVIDER`).** SSM 파라미터 목록을 만들 때 혼동·빈 파라미터가 된다. 지우거나 "미사용" 주석(`…-survey.txt` §1). S9 와 같이.
- **R-U10D-6 — `tests.md`/`reliability.md` 에 "배포 무관" 표시.** `proxy.test.ts`(6)·`network.test.ts`(2)·`test_config.py` 기본 포트·`test_push_devpage.py`·`test_conftest_test_db.py` 는 개발 전용이다(§3.5·§4). 기록표에 ③ 표시를 두면 "통과 = 배포 보증" 으로 읽히는 일을 막는다.
- **R-U10D-7 — 계약 대조 자동화.** `types.ts` 는 수동 복사(1행 주석)다. 이번 대조 스크립트(evidence 머리줄의 명령)와 같은 것을 `web` CI job 에 넣거나, S5 의 pydantic 검증을 배포 job 에 둔다. 지금은 32/32 일치라 결함은 아니다.
- **R-U10D-8 — 실 공급자 실패 경로는 SDK 예외 매핑까지만.** 실 지연·429·잘못된 키(401)·모델명 오류는 S6 1회 호출 + 응답 시간 기록으로 최소 확인. `reliability.md` K 절 "대가" 문장과 같은 뜻이며 거기에 S6 을 적는다.
- **R-U10D-9 — 브리핑 스케줄러의 워커 수 전제를 RUNNING/P9 에 명시.** lifespan 이 워커마다 뜬다(`app/main.py` 156~173행). SKIP LOCKED 로 중복은 없지만 `--workers 1` 로 고정하거나 S13 으로 N 워커에서 1회만 생성됨을 단언.
- **R-U10D-10 — U10 사람 점검은 개발 프록시 경로였다.** `evidence/20261016-1915-u10-check-chat-fix035.txt` §0: Vite 5173 → uvicorn 8000. 운영 경로(CloudFront → Caddy → uvicorn, S3 정적) 는 한 번도 지나지 않았다 — P9 의 "배포 URL 에서 데모 5단계 재현"(backlog 93행) 이 그 자리이며, S2~S5·S11 을 그 앞에 둔다.

## 11. 증거 (전부 `docs/wiki/packages/P8-frontend/evidence/`, `save_evidence.py` 통로)

| 파일 | 내용 |
|---|---|
| `20261016-1920-verifier-u10-deploy-validity-survey.txt` | 앱이 읽는 환경변수 22개(파일:행) · `.env.example` 차집합 · 프론트/E2E 파일별 가짜 대체 집계 · 각 파일 머리말 12줄 |
| `20261016-1920-verifier-u10-deploy-validity-contract.txt` | pydantic 33 ↔ TS 32 모델 필드 대조 전문(불일치 0) |
| `20261016-1920-verifier-u10-deploy-validity-ci.txt` | `Dockerfile` 부재 · compose 서비스 · `tests.yml` run 단계 16개 · docker/health/caddy grep `(없음)` · CORS `(없음)` · `session.py` 45행 엔진 옵션 |
| `20261016-1920-verifier-u10-deploy-validity-counts.txt` | pytest `1953 tests collected` · 파일 74 · `vitest list` 파일별 건수 · Playwright `4 tests in 3 files` |
| `20261016-1925-verifier-u10-deploy-validity-pytest-table.txt` | 74 파일별 `dbtest`·`TestClient`·`monkeypatch`·가짜 LLM·가짜 임베딩·`setenv`·고정 시계·줄 수 · 마커 집계(언급 46 / 실제 마커 43 / 언급만 3) |

이 문서는 코드·테스트·계획을 바꾸지 않았다. 고칠 것은 전부 §10 소견으로 돌려준다.
