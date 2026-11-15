# P9b-auth · 계획 (01-plan)

상태: 개정 2(2026-11-15, architect — verifier 02-plan-verify 1차 보류 F-1~F-7·R-1~R-13, 2차 보류 N-1~N-4·R2-1~R2-4 반영, 처리표는 맨 끝 "개정 이력") — 사용자 결정 표는 **권장안을 기본값으로 채택**(사용자 지시 "계획하고 실행하고 독립 검토까지 진행, 검토할 수 없는 부분만 말해 달라", 2026-11-15) → verify-plan → verifier 재검증 → 활성화 | 담당: backend-agent(sonnet, U1·U2·U3a·U3b·U4·U5) · frontend-agent(sonnet, U6) · 메인 세션(U7 문서·로컬 통합 스모크·증거 저장, U8 진행) · 사용자(U7 서버 반영 SSH·U8 시연 계정 대화·브라우저 점검) · 검증 verifier(fable, 02-plan-verify·단위 리뷰·04-review) | 작성: 2026-11-15
태그 — 패키지: P9b-auth · 닫는 검증: (직접 R 없음) F-fbaaae · R-U10D-3 · 관련 R12·R14 · 기대는 결정: D18(신설) · D17(결정 6 개정) · D2 · D16 · 구현하는 명세: S3.1(보충 0003) · S3.4(답변 소유) · S3.6(사용자별 루프·endpoint 하나) · 관련 원칙: 원칙1 원칙5(폐지 문장) 원칙7 원칙8 원칙9 · 출처 CR: CR-006
의존: P8-frontend(완료 2026-10-21) — 충족 · P5b-query-turn(완료 2026-11-09, `f67d8e4`) — 충족 · P4 게이트(P4b 통과 2026-09-23) — 충족.
관련(선행 완료 조건이 아님): **배포 패키지(P9 인프라)는 U4 기동·바깥 스모크(`7830f6c`)까지, 04-review 보류.** U1~U6 코드는 배포 패키지 산출물에 기대지 않는다. **U7·U8 과 수용 기준 9번은 P9 인프라 U4 산출물(`7830f6c`, 떠 있는 서버 `54-79-202-221.sslip.io`·`docker-compose.prod.yml`·entrypoint)에 기댄다 — 충족**(backlog 99행 "의존: P9-infra U4" 와 같은 말, R-1). 반영 뒤 배포 패키지 04-review 를 함께 닫는다(CURRENT 메모, 사용자 결정 "반드시 평가 전에") · P2b-person-delete 보류(U2 `3a1bcec`) — 영향 없음(라우트 없음), 재개 시 `chat_messages` 재검토.

- **기준 해시**: `<기준>` = **`08c1b49`**(CR-006 문서 커밋 `3d786a5` → 하네스 문장 커밋 `5c0f26d` → FIX-036 `08c1b49`, 메인 세션 2026-11-15).
- **기준선**: pytest **2261 passed · 0 failed · skip 0**(FIX-036 `08c1b49` 뒤, verifier 재실행 `docs/wiki/fixes/evidence/20261115-2026-verifier-FIX-036-pytest-all.txt`). 단위 증거는 "실패 0, skip 0" 을 단언한다. 통과 수는 단위마다 늘어나되 **U5 에서 `tests/test_settings.py`(2건)를 지워 2 줄어든다**(N-2 ② — 03-log 에 수 기록). **이 기기의 `python3` 은 anaconda 라 `pgvector` 가 없어 수집 오류가 난다 → 아래 판정 명령의 `python3 -m pytest`·`python3 scripts/…`·`python3 -m ruff` 는 `.venv/bin/python` 으로 읽는다**(`save_evidence.py` 래퍼 자체는 `python3` 그대로) · mypy 기준선 38 · `tools_check` 7/7 · Vitest·typecheck 는 U6 시작 전 재어 03-log 에.
- **일정 제약(CR-006 결정 3)**: 오늘 2026-11-15(일) 저녁, 졸업평가 **2026-11-18(수)**. 목표 **11-17(화) 저녁까지 구현·검증·배포 반영**. 11-16(월)에 U1~U5·U6, 11-17(화) 오전 U7 로컬 통합·배포 반영, 오후 U8 시연 계정·리허설. 밀리면 아래 "범위 축소 순서" 대로 줄인다. **판단 시점(R-13): 11-16(월) 밤까지 U3b 가 커밋되지 않았으면 축소 1·4 를 적용한다.**

### 코드에서 확인한 사실 (계획의 전제)

1. **사용자 고정**: `app/settings.py:509-518` `app_user_id()` 가 `APP_USER_ID`(기본 `"local"`)를 읽는다. 부르는 곳 — `app/tools/context.py:103`(`ToolContext.user_id` `default_factory`), `app/api/deps.py:156,240,332,346`, `app/api/routes.py:430,441,453,460,468,497`, `app/briefing/scheduler.py:79`(import)·`100`(호출). `.env.example:53`, `docs/user-setup/11-ec2-minimal-deploy.md:58,105` 에 이름이 있다. `evaluation/`·`scripts/` 에는 `app_user_id` 참조 0(grep). **주석·docstring 에 이름이 남은 곳**(verifier 02-plan-verify F-4): `app/settings.py` 4·42·322·350·381·435·492행, `app/api/routes.py` 99·321·440행, `app/api/deps.py` 139·226·329·341행, `app/briefing/scheduler.py:20`, `app/tools/questions.py:61`.
2. **조회·쓰기는 이미 `user_id` 로 좁힌다**: `app/api/read.py` 의 `get_event_raw`(94행)·`get_fact_sources`(119)·`list_persons`(155·164)·`get_person_card`(184 `_owned_person`)·`list_briefings`(294·338) 가 `Person.user_id == user_id` 조건. `app/briefing/select.py:61,76` 은 `ctx.user_id`. 후보 검색 `app/er/candidates.py` 도 `user_id`. 툴도 소유 검사를 한다(`app/tools/persons.py:417` `_owned_person`, `records.py:87,130`, `briefing.py:74`). → **바뀌는 것은 값의 출처뿐**이다.
3. **스키마**(`app/db/models.py`): `user_id` 가 있는 테이블은 `persons`(Text, NOT NULL, 인덱스)·`push_subscriptions`(Text, UNIQUE(user_id, endpoint)). `pending_questions`·`agent_traces` 는 `session_id` 만. 리비전은 `0001_schema_v2`·`0002_unique_upsert_keys` — 새 리비전은 `0003`. `pending_questions` 행을 만드는 곳은 `app/` 전체에서 `app/tools/questions.py:217-223` 하나(F-1).
4. **세션 id**: `app/api/deps.py:201-211` `resolve_session_id` — `X-Session-Id` 헤더(형식 `^[A-Za-z0-9._-]{1,128}$`(198행), 실패 422 `invalid_session_id`), 없으면 uuid4. 프론트 `web/src/session.ts`(localStorage `relationship.session_id`), `web/src/api/client.ts:24,61-82`(`SESSION_HEADER`, 422 면 세션 버림). 세션↔사용자 검증 없음.
5. **답변 소유 없음(F-fbaaae)**: `app/tools/questions.py:57-67`(모듈 docstring)·248행(함수 docstring) — 실제 조회는 **261행**. question_id 만 알면 답할 수 있다. 질문 행을 id 로 읽는 곳(R-2): `app/api/deps.py:150`(`build_ctx` — 질문 행의 `session_id` 로 `ToolContext`)·`:184`(`load_resume_input`)·`app/tools/questions.py:261`(`answer_question`)·`app/tools/persons.py:306`(`confirmed_question_id`).
6. **라우트 12개**(`app/api/routes.py`): `GET /health` · `POST /answers/{question_id}` · `POST /chat` · `POST /briefings/run` · `GET /push/vapid-public-key` · `POST /push/subscriptions` · `GET /persons` · `GET /persons/{person_id}` · `GET /events/{event_id}/raw` · `GET /persons/{person_id}/facts/{fact_id}/sources` · `GET /questions/pending` · `GET /briefings`. 인증·쿠키·CORS 코드 0. `PUSH_DEV_PAGE_ENABLED` 가 켜지면 `app/main.py:95-108` 이 `/push-dev/` 3경로(정적 파일)를 인증 없이 더한다 — 고정 사용자를 쓰지 않는다(R-4 ③).
7. **스케줄러**: `app/briefing/scheduler.py:88-106` `default_run_once` 가 `app_user_id()` 한 사용자로 `ToolContext` 와 `notifier_from_env(session, ctx.user_id, ctx.now)` 를 만들어 `run_briefings` 1회. 한 번 돌 때마다 `briefing_run` trace 1행(P9 S13 판정 근거, `packages/P9-infra/01-plan.md:17`). 창은 `app/briefing/select.py:71` `now + timedelta(hours=lead_hours)`.
8. **대화 기록**: 프론트 `web/src/screens/ChatScreen.tsx:106` 메모리 state 뿐. 서버에 기록 조회 API 없음. `ChatOut{reply, session_id, stored, pending_question, stop_reason, trace_ids}`·`AnswerOut{question_id, status, reply, stored, pending_question, stop_reason, trace_ids}`(`app/api/schemas.py:96-122`).
9. **테스트 영향 규모**: `TestClient(`·`X-Session-Id`·`APP_USER_ID` 가 18파일 58곳, `ToolContext(` 가 36파일 68곳(그중 `app/` 2파일·`scripts/run_pilot_eval.py` 1곳 — `app/` 의 호출은 전부 `user_id=` 를 명시한다), `"local"`/`app_user_id` 값에 기대어 데이터를 넣는 곳 24파일 78곳(F-5). `invalid_session_id` 422 단언은 `tests/test_api_chat.py`·`tests/test_api_questions_pending.py` 에 있다. 테스트 DB 는 `tests/db_bootstrap.py:118-137` 이 `alembic upgrade head` 로 맞춘다 → 0003 은 테스트 DB 에서도 한 번 돈다. 마이그레이션 왕복 테스트 관례는 없다(`test_schema_check.py`·`test_schema_models.py` 뿐). CI 는 `-m "not dbtest"` 작업(`tests.yml:147`)과 E2E(`tests.yml:242-245` `npm run e2e`)를 돈다.
   - **스키마를 숫자·글자로 단언하는 기존 테스트·스크립트**(N-1, verifier 목록 + architect grep `EXPECTED_|S3_1_TABLE_COLUMNS|NULLABLE_COLUMNS|EXPECTED_INDEXES|len\(names\)|== 6 and` 2026-11-15): `tests/test_schema_models.py` — `S3_1_TABLE_COLUMNS`(18~66행)·124행 `len(names) == 9`·143~144행 컬럼 합 `56`·`EXPECTED_FKS`(106~113행)·212행 `len(found) == 6`·**`NULLABLE_COLUMNS`(232~239행 — 새 `chat_messages.question_id` 가 nullable 이라 깨진다, verifier 목록 밖 추가)**·**`EXPECTED_INDEXES`(279~294행)·309행 `total == 10`(새 인덱스 — 추가)**·**194~201행 CHECK 총수 `4`(9테이블 고정 목록이라 깨지지는 않지만 `chat_messages.role` CHECK 를 반영하려면 목록에 테이블을 더하고 5 — 추가)** · `tests/test_schema_check.py` 24행 `len(sc.EXPECTED_TABLES) == 9`·58행 인덱스 이름 수 `10` · `scripts/schema_check.py:237` FK 수 `== 6`(→ 8; 286행 인덱스 `>= 10` 은 하한이라 그대로). 깨지지 않는 것(확인): `tests/helpers_read_api.py:36-46` `_COUNTED_MODELS`(9모델 고정 목록)·`tests/test_api_read_briefings.py:433` `len(before.counts) == 9` — 새 테이블을 세지 않으므로 그대로 통과(읽기 API 쓰기 0 판정에 `chat_messages` 가 빠지는 한계는 리스크 절).
   - **`PendingQuestion(` 을 직접 만드는 테스트**(N-1): `tests/test_person_delete.py:801,808` · `test_tools_persons.py:100` · `test_tools_questions.py:78` · `test_tools_context.py:95` · `test_api.py:53` · `test_api_questions_pending.py:43`.
   - **`app_user_id`·`APP_USER_ID` 를 참조하는 `app/` 밖**(N-2, architect grep `app_user_id|APP_USER_ID|DEFAULT_APP_USER_ID` — `tests/`·`scripts/`·`evaluation/`·`docs/RUNNING.md`·`.github/`·문서 2026-11-15): `tests/test_settings.py`(파일 전체 — 2건) · `tests/test_push_wiring.py:57`(import)·111·127·204(데이터 준비)·344(단언) · `tests/test_answer_concurrency.py:48`(import)·83(+ 71·73·127 docstring) · `tests/test_commit_boundaries.py:81,181,293`(`monkeypatch.setenv("APP_USER_ID", user_id)`) · 주석만: `tests/test_push_subscriptions.py:90`(`row.user_id == "local"` — 값은 그대로 맞음)·`tests/test_api_read_briefings_e2e.py:185` · `.github/workflows/tests.yml:176`(`echo "APP_USER_ID=ci-smoke"` — 스모크 변수 파일, 무해하지만 낡음) · `docs/user-setup/13-user-todo-deploy.md:41,46`(+ 11 문서 58·105행). `scripts/`·`evaluation/`·`docs/RUNNING.md` 0.
10. **운영**: Caddy 가 `/api/*` 접두를 떼고 같은 출처로 프록시(D17 2, `Host` 는 원래 값 전달). backend entrypoint 가 기동 때 `alembic upgrade head`(D17 4) → **배포 반영 = 0003 실행 = 운영 데이터 비우기**. `--workers 1`.
11. **보안 카드**: §4 "셸에서 `DROP`/`TRUNCATE` 금지 → Alembic 마이그레이션 파일로" · §4 "로컬 서버 이외로 `curl -d`" 금지(배포 URL 의 POST 는 사용자 몫, 로컬 `localhost` 는 에이전트 가능) · §5 대화 기록 저장은 CR-006 로 "계정 소유로만" 개정.
12. **fetch 기본 `credentials` 는 `'same-origin'`** — 같은 출처 쿠키는 지금 코드로도 실리지만, 의도를 드러내려 `apiFetch` 에 명시한다(U6). `apiFetch` 는 성공이면 무조건 `response.json()` 을 부른다(`client.ts` 89행 부근) → 204 는 본문을 읽지 않게 고친다(R-3).
13. **배포 호스트와 SameSite(F-7)**: `sslip.io` 는 공개 접미사 목록(PSL)에 없다(verifier 2026-11-15 확인) → 누구나 만들 수 있는 `<임의 IP>.sslip.io` 가 우리와 **같은 사이트**다. `SameSite=Lax` 쿠키는 그 호스트에서 보낸 POST 에도 실린다. 또 그 호스트가 `Domain=sslip.io` 쿠키를 심어 우리 쿠키를 덮을 수 있다(R-5). FastAPI 는 `Content-Type` 이 JSON 이 아니면 본문을 JSON 으로 해석하지 않는다(→ 폼·`text/plain` 위장 POST 는 422 — U2 테스트로 박는다).
14. **로컬 개발 프록시**: `web/vite.config.ts:23-26` 프록시가 `changeOrigin: true` 라 백엔드가 보는 `Host` 가 대상(`localhost:8000`)으로 바뀐다 — 브라우저 `Origin` 은 `http://localhost:5173`. Origin 검사(결정 T)는 `X-Forwarded-Host` 가 있으면 그것과 비교하고, U6 이 프록시에 `xfwd: true` 를 더한다.

## 목표

CR-006 · D18 — 사용자 원문 "이 서비스에 로그인 기능도 추가하고 싶어 그 로그인에 따라서 채팅방이 나오도록 그리고 로그인을 한 계정마다 세션을 별개로 해서 하고싶은데" 를 실현한다. 목적(사용자 원문): "졸업종합평가 날에 시연을 해야하는데 서비스의 구조상 아예 백지인 상태에서 우리의 성능을 보여주긴 어려울 것 같아서 그래 그래서 새로운 계정을 생성하는 모습을 보이고 그리고 이미 데이터가 들어가있으면 어떻게 해주는지 보여주려고 하는거야". 즉 **(가) 새 계정 가입 → 빈 상태에서 첫 언급**, **(나) 데이터가 쌓인 시연 계정으로 로그인 → 인물 카드·브리핑·지난 대화가 그대로**, 그리고 **두 계정의 기억이 섞이지 않음**을 배포 URL 에서 보인다. 구현은 아이디·비밀번호 가입·로그인(HttpOnly 쿠키 + 서버 세션 테이블), 모든 API 의 사용자 출처를 환경변수에서 로그인 계정으로 바꾸기, 계정당 채팅방 하나(서버가 정하는 `session_id = chat:<user_id>` + `chat_messages` 기록), 스케줄러·푸시 사용자별, 리비전 0003(기존 데이터 비우기), 프론트 로그인·가입 화면. 예: 심사자 앞에서 "새 계정 만들기" 로 `judge01` 을 만들면 인물 화면이 비어 있고, 로그아웃 뒤 `demo` 로 로그인하면 김 대리 카드·내일 점심 브리핑·어제 대화가 보인다. `judge01` 의 쿠키로 `GET /api/persons/<demo 의 인물 id>` 를 부르면 404.

## 범위

- 포함:
  - 스키마·리비전 0003: `users`·`auth_sessions`·`chat_messages` 신설, `pending_questions.user_id` 추가와 그 값을 넣는 `ask_user` 한 줄, 기존 사용자 데이터 비우기(U1).
  - 인증 코어와 API 4개 `POST /auth/signup`·`POST /auth/login`·`POST /auth/logout`·`GET /auth/me`, 로그인 의존성, Origin 검사, 쿠키 이름 규칙(U2).
  - 기존 테스트 이관(동작 불변 — `ToolContext(user_id=…)` 명시·로그인 도우미)(U3a).
  - 기존 11개 라우트를 로그인 사용자 기준으로, 미로그인 401, 남의 자원 404, 답변 소유 검사, `session_id` 계정 묶기, `ToolContext.user_id` 기본값 제거(U3b).
  - 대화 기록 저장(`/chat`·`/answers` 같은 트랜잭션)과 `GET /chat/history`(U4).
  - 스케줄러 사용자별 루프(대상 0명이면 표식 `user_id=""` 로 `run_briefings` 1회 — `briefing_run` 1행, 결정 U), 푸시 endpoint 하나 규칙, 로그아웃 시 그 브라우저 구독 떼기, `app_user_id()` 함수·`.env.example` 줄 삭제(U5).
  - 프론트 로그인·가입 화면, 로그아웃, 대화 기록 불러오기, 401 처리, `X-Session-Id` 제거, E2E `/auth/me` 목, Vite 프록시 `xfwd`(U6).
  - 문서·로컬 통합 스모크·배포 반영 절차와 스모크(U7). 시연 계정 데이터 쌓기·시연 두 갈래 리허설(U8).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **비밀번호 재설정·이메일 인증** — 메일 발송 인프라·이메일 수집이 필요하고 평가 전 3일에 맞지 않는다. 시연 계정은 사용자가 비밀번호를 안다.
  - **소셜(구글) 로그인** — CR-006 결정 1. OAuth 클라이언트 등록·콜백 도메인·비밀 값이 필요.
  - **채팅방 목록(여러 대화방)** — CR-006 · 원칙7 제외(사용자 "채팅방 목록은 일부러 넣지 않아 우리는 관계를 기억하는 것이 메인이니까").
  - **관리자 화면·계정 삭제·계정 목록** — 시연에 불필요. 계정 삭제가 없으니 기존 테이블에 FK CASCADE 도 두지 않는다(결정 O).
  - **로그인 시도 제한·CAPTCHA** — 결정 H(권장: 두지 않음).
  - **CSRF 토큰** — 같은 출처 JSON API + Origin 검사(결정 T)로 갈음. 공개 4일.
  - **브리핑 달력 보기** — CR-006 변경 항목 2, 별도 패키지 `P9c-briefing-calendar`(P9b 완료 뒤).
  - **툴 7종·ER 4단계·임계치·확신도·평가 산출물 변경** — 원칙1~4·8. 값의 출처만 바뀐다.
  - **`agent_traces.user_id` 컬럼** — 결정 N. 대화 trace 는 `session_id = chat:<user_id>` 로 계정 추적.
  - **P2b-person-delete U3~U5** — 보류 유지.

## 산출물 (파일 경로)

각 단위 시작 전 `registry.md` grep(이 계획 작성 시 `auth|login|password|users|chat_messages` 행 0 — 있는 관련 행: 247행 `web/src/session.ts`·`postChat`, 242행 `web/src/api/client.ts`, 216행 push 엔드포인트, 45행 `app/config.py`).

**새로 만드는 파일** (이름은 권장 — 구현 에이전트가 registry 관례에 맞게 조정 가능, 바꾸면 03-log 에)
- `alembic/versions/0003_auth_users.py` (U1)
- `app/auth/__init__.py` · `app/auth/passwords.py`(해시·검증) · `app/auth/sessions.py`(토큰 발급·조회·폐기) · `app/auth/deps.py`(`current_user` 의존성) · `app/auth/routes.py`(`/auth/*`) · `app/auth/origin.py`(Origin 검사 — 미들웨어 또는 공통 의존성 한 곳) (U2)
- `app/chat/history.py`(기록 저장·조회) (U4)
- 테스트: `tests/test_migration_0003.py`(U1) · `tests/test_auth_passwords.py`·`tests/test_auth_api.py`·`tests/test_auth_origin.py`(U2) · `tests/auth_helpers.py`(로그인 클라이언트·사용자 행·`ToolContext` 도우미, U3a) · `tests/test_auth_required_routes.py`(라우트 열거 401 계약)·`tests/test_user_isolation.py`(U3b) · `tests/test_chat_history.py`(U4) · `tests/test_briefing_scheduler_users.py`·`tests/test_push_endpoint_owner.py`(U5)
- 프론트: `web/src/screens/AuthScreen.tsx` · `web/src/auth.ts`(또는 `AuthProvider`) · `web/src/__tests__/auth.test.tsx` (U6)
- `docs/wiki/packages/P9b-auth/tests.md`(테스트 1건 = 1줄) · `03-log.md` · `evidence/*.txt`

**고치는 기존 파일**

| 파일 | 고치는 내용 | 단위 |
|---|---|---|
| `app/db/models.py` | `User`·`AuthSession`·`ChatMessage` 모델, `PendingQuestion.user_id` | U1 |
| `app/tools/questions.py` | 질문 저장 시 `user_id=ctx.user_id` 한 줄(F-1) | U1 |
| `app/tools/questions.py` | 답변·조회 소유 검사, F-fbaaae docstring 갱신, 61행 `APP_USER_ID` 언급 삭제 | U3b |
| `scripts/schema_check.py:237` | FK 수 `== 6` → `== 8`(`EXPECTED_TABLES` 는 메타데이터에서 와서 그대로) | U1 |
| **U1 이 고치는 기존 테스트(닫힌 목록, N-1)** — `tests/test_schema_models.py`(`S3_1_TABLE_COLUMNS` 에 새 테이블 3개·`pending_questions.user_id`, 테이블 수 9→12, 컬럼 합 56→새 값, `EXPECTED_FKS` 6→8, `NULLABLE_COLUMNS` 에 `question_id`, `EXPECTED_INDEXES`·총수에 새 인덱스, CHECK 목록에 `chat_messages`·총수 5) · `tests/test_schema_check.py`(9→12, 인덱스 이름 수 10→새 값) · `PendingQuestion(` 직접 생성 6파일(`test_person_delete.py:801,808`·`test_tools_persons.py:100`·`test_tools_questions.py:78`·`test_tools_context.py:95`·`test_api.py:53`·`test_api_questions_pending.py:43`)에 `user_id` 인자 | **S3.1 보충(카드) 반영이지 단언 의미 변경이 아니다** — 값은 카드에서 나온다. 목록 밖 테스트가 깨지면 멈추고 보고 | U1 |
| `tests/test_push_wiring.py`(57·111·127·204행) · `tests/test_answer_concurrency.py`(48·83행 + docstring) | `app_user_id()` 호출·import 를 같은 값 리터럴 `"local"` 로(동작 불변, N-2 ①) | U3a |
| `tests/test_commit_boundaries.py:81,181,293` | `monkeypatch.setenv("APP_USER_ID", user_id)` → 그 `user_id` 로 로그인한 클라이언트(N-2 ③) | U3b |
| `tests/test_settings.py` | **삭제**(`app_user_id()` 해석 규칙 테스트 2건 — 함수가 없어진다, 통과 수 −2, N-2 ②) | U5 |
| `tests/test_push_wiring.py:344` | 기대값 `app_user_id()` → 대상 0명 표식 `""`(결정 U, N-4) | U5 |
| `.github/workflows/tests.yml:176` | `echo "APP_USER_ID=ci-smoke"` 줄 삭제(무해하지만 폐지된 이름) | U5 |
| `app/main.py` | `/auth` 라우터 포함, Origin 검사 등록 | U2 |
| `app/settings.py` | `AUTH_COOKIE_SECURE`(기본 켜짐)·상수(유지 기간·이름 규칙·길이) | U2 |
| `app/settings.py` | `app_user_id()`·`DEFAULT_APP_USER_ID` 삭제, 4·42·322·350·381·435·492행 주석·docstring 의 이름 삭제 | U5 |
| `.env.example` | `AUTH_COOKIE_SECURE` 이름 줄(주석: 로컬 http 개발만 0) | U2 |
| `.env.example` | `APP_USER_ID` 줄 삭제 | U5 |
| `app/api/schemas.py` | `SignupIn`·`LoginIn`·`MeOut`·`LogoutIn` / `ChatHistoryItemOut` | U2 / U4 |
| `scripts/run_pilot_eval.py` | `ToolContext(..., user_id=<지금 기본값과 같은 값>)` 명시(결과 불변) | U3a |
| 기존 테스트 다수(사실 9) | `ToolContext(user_id=…)` 명시·로그인 도우미로 클라이언트 생성 — 동작 불변 | U3a |
| 기존 테스트(닫힌 목록 F-5 의 단언만) | 계약 변경 단언 갱신 | U3b |
| `app/api/deps.py` · `app/api/routes.py` | 11개 라우트에 `current_user`, 요청 경로의 `app_user_id()` 대체, `resolve_session_id` 제거 → 계정 세션, 주석(routes 99·321·440 · deps 139·226·329·341) | U3b |
| `app/tools/context.py` | `user_id` 기본값 제거 | U3b |
| `app/api/read.py:51` | 주석 "(화면 3개 고정, 원칙5)" → 원칙5 개정 반영 | U3b |
| `app/push/subscriptions.py` · `app/briefing/scheduler.py` · `app/auth/routes.py`(로그아웃 endpoint) | endpoint 하나 규칙·로그아웃 삭제 / 사용자별 루프·0명 1행·20행 주석 | U5 |
| `web/src/api/client.ts` · `web/src/session.ts` · `web/src/App.tsx` · `web/src/routes.ts`(주석) · `web/src/components/AppShell.tsx` · `web/src/screens/ChatScreen.tsx` · `web/src/push.ts` · `web/src/api/types.ts` · `web/vite.config.ts`(`xfwd: true`) · `web/e2e/fixtures.ts`(`/auth/me` 목) | 401 처리·204 무본문·`X-Session-Id` 제거·관문·로그아웃·기록 불러오기·주석(원칙5 개정)·프록시·E2E | U6 |
| `docs/RUNNING.md` · `docs/user-setup/11-ec2-minimal-deploy.md`(58·105행 `APP_USER_ID` → 계정) · `docs/user-setup/13-user-todo-deploy.md` · `SERVER-CHECKLIST.md` §5(시연 두 갈래) · `docs/wiki/registry.md` | 문서 | U7 |

### API 계약 (U2~U5 백엔드 ↔ U6 프론트 — U6 이 동시에 시작할 수 있도록 여기서 고정)

| 메서드·경로 | 요청 | 성공 | 실패 |
|---|---|---|---|
| `POST /auth/signup` | `{username, password}` | **201** `{id, username}` + 로그인 쿠키(가입 즉시 로그인 — 결정 G) | 422 `invalid_username`/`invalid_password` · 409 `username_taken` |
| `POST /auth/login` | `{username, password}` | 200 `{id, username}` + 쿠키 | 401 `invalid_credentials`(없는 아이디·틀린 비밀번호 같은 응답) |
| `POST /auth/logout` | `{endpoint?: string}`(그 브라우저 푸시 endpoint, 있으면) | **204**(본문 없음) + 쿠키 삭제 | **미로그인 401 `unauthenticated`**(F-3 — 예외는 `/health`·`/auth/signup`·`/auth/login` 3개뿐). 프론트는 로그아웃의 401 을 "이미 로그아웃됨" 으로 처리 |
| `GET /auth/me` | — | 200 `{id, username}` | 401 `unauthenticated` |
| `GET /chat/history?limit=N` | `limit` 1~200, 기본 결정 I | 200 `[{id, role:"user"\|"assistant", content, question_id\|null, created_at}]` 오래된 것 → 최근 순 | 401 |
| 기존 11개(`/health` 제외) | 그대로(`X-Session-Id` 는 무시) | 그대로. `ChatOut.session_id` = `chat:<user_id>` | 미로그인 401 `unauthenticated` · 남의 자원 404(기존 코드 그대로) |
| (공통) 상태를 바꾸는 메서드(POST·PUT·PATCH·DELETE) | `Origin` 헤더가 있으면 그 호스트(:포트)가 `X-Forwarded-Host`(있으면) 또는 `Host` 와 같아야 함 | 통과 | **403 `bad_origin`**. `Origin` 이 없으면 통과(curl·테스트 클라이언트) — 결정 T |

401 본문은 `{"detail":{"code":"unauthenticated"}}` (기존 오류 본문 모양과 같은 `detail.code`). 403 은 `{"detail":{"code":"bad_origin"}}`.

## 작업 단위 (단위 하나 = 커밋 하나. 끝나면 /commit. 단위마다 verifier 커밋 전 리뷰 + 핵심 계약 변이 시험 최소 1개)

순서·병렬: **(FIX-036, 메인) → U1 → U2 → U3a → U3b → (U4 ∥ U5)** — 백엔드 직렬(같은 `routes.py`·`deps.py` 를 만지므로 U4·U5 만 파일이 갈라져 동시 가능). **U6 은 U2 커밋 뒤 U3a~U5 와 동시**(프론트는 `web/` 만, 위 API 계약과 목 응답으로 테스트). → **U7**(모든 단위 뒤) → **U8**(배포 반영 뒤). 위임 프롬프트에는 이 계획의 해당 U 원문을 인용하고 임의 제한을 덧붙이지 않는다. 계획에 없는 상수·정렬·상한이 필요하면 구현 전에 멈추고 보고한다(FIX-033 (b)).

- [ ] U1 **[backend-agent] 스키마·리비전 0003 — `users`·`auth_sessions`·`chat_messages` 신설, `pending_questions.user_id` 와 `ask_user` 의 값 넣기, 기존 데이터 비우기** / Refs: P9b-auth D18 S3.1 S3.4 CR-006 F-fbaaae security 원칙8
  - 모델(`app/db/models.py`, S3.1 보충 그대로): `users(id Text PK — uuid4 hex(결정 O), username Text UNIQUE NOT NULL, password_hash Text NOT NULL, created_at)` · `auth_sessions(id BIGINT PK, user_id Text FK→users.id ON DELETE CASCADE NOT NULL, token_hash Text UNIQUE NOT NULL, created_at, expires_at NOT NULL)` + 인덱스 `user_id` · `chat_messages(id BIGINT PK, user_id Text FK→users.id CASCADE NOT NULL, role Text NOT NULL CHECK IN ('user','assistant'), content Text NOT NULL, question_id BIGINT NULL, created_at)` + 인덱스 `(user_id, created_at)` · `pending_questions.user_id Text NOT NULL` + 인덱스 `(user_id, answered_at)` 부분 또는 단순 — 구현 에이전트 판단, 03-log 에. 기존 테이블 `persons`·`push_subscriptions`·`pending_questions` 의 `user_id` 에는 **FK 를 두지 않는다**(결정 O). `question_id` 도 FK 없음(질문이 지워져도 기록은 남는다).
  - **`ask_user` 값 넣기(F-1)**: `app/tools/questions.py:217-223` 의 `PendingQuestion(...)` 에 `user_id=ctx.user_id` 한 줄. 이것이 없으면 NOT NULL 로 `ask_user` 를 지나는 모든 경로가 깨진다. 소유 검사·docstring 은 U3b 에 남긴다. 이 시점 `ctx.user_id` 는 아직 `app_user_id()` 기본값이라 기존 테스트는 그대로 통과해야 한다.
  - 리비전 `0003`: **upgrade** = ① 기존 사용자 데이터 삭제(결정 K) — `DELETE FROM persons`(별칭·사실·사건·일정·`fact_sources` 는 FK CASCADE)·`DELETE FROM pending_questions`·`DELETE FROM push_subscriptions`·`DELETE FROM agent_traces` — `TRUNCATE`·`DROP TABLE` 쓰지 않음 ② 새 테이블 3개 ③ `pending_questions.user_id` 추가(NOT NULL — ①로 빈 테이블이라 기본값 없이 추가 가능) ④ 인덱스·제약. **downgrade** = 새 테이블·컬럼·인덱스 제거(데이터 복구 없음 — 모듈 docstring 에 명시).
  - 테스트 `tests/test_migration_0003.py`: ① head == `0003` ② 새 테이블 3개·컬럼 집합이 S3.1 보충과 같다 ③ `users.username` UNIQUE·`auth_sessions.token_hash` UNIQUE·`chat_messages.role` CHECK(위반 INSERT 가 `IntegrityError`) ④ `pending_questions.user_id` NOT NULL ⑤ 비우기 ⑥ `alembic check` 무변경 ⑦ downgrade 0002 → upgrade head 왕복. **⑤⑦ 방식 확정(R-10)**: 공유 테스트 DB 를 흔들지 않도록 **이름 고정 전용 DB `relationship_test_mig`**(없으면 `CREATE DATABASE`, 있으면 재사용 — `DROP DATABASE` 는 쓰지 않는다), 테스트 시작 때 `downgrade base` → `upgrade 0002` → **원시 SQL** 로 0002 상태 행 삽입(ORM 모델은 0003 기준이라 쓰지 않는다) → `upgrade head` → 행 수 0. 이 테스트는 `dbtest` 표식을 달아 CI 의 `-m "not dbtest"` 작업(`tests.yml:147`)에서 빠지고 DB 작업에서 돈다 · skip 0 유지.
  - 판정: `.venv/bin/python -m alembic upgrade head`(개발 DB 는 **사용자 데이터가 지워진다** — 사용자 결정 4, 실행 직전 메인이 사용자에게 한 번 더 알리고 03-log 에 "개발 DB 인물 12명 삭제됨" 기록) · `alembic check` · `.venv/bin/python scripts/schema_check.py` 전부 PASS · 새 테스트 · 전체 pytest 실패 0.
  - **U1 이 고치는 기존 테스트·스크립트 — 닫힌 목록(N-1, 사실 9)**: ① `tests/test_schema_models.py` — `S3_1_TABLE_COLUMNS` 에 새 테이블 3개와 `pending_questions.user_id`, 테이블 수 9→12, 컬럼 합 56→새 값, `EXPECTED_FKS` 6→8(`auth_sessions.user_id`·`chat_messages.user_id` → `users.id`), `NULLABLE_COLUMNS` 에 `question_id`, `EXPECTED_INDEXES` 와 309행 총수에 새 인덱스, CHECK 총수 테스트(194~201행)의 테이블 목록에 `chat_messages`·총수 4→5 ② `tests/test_schema_check.py` — 24행 9→12, 58행 인덱스 이름 수 10→새 값 ③ `scripts/schema_check.py:237` FK 수 6→8 ④ `PendingQuestion(` 을 직접 만드는 6파일(`tests/test_person_delete.py:801,808` · `test_tools_persons.py:100` · `test_tools_questions.py:78` · `test_tools_context.py:95` · `test_api.py:53` · `test_api_questions_pending.py:43`)에 `user_id` 인자(값은 같은 테스트가 쓰는 사용자 값). **이 값들은 S3.1 보충(카드)에서 나오므로 단언 의미 변경이 아니라 카드 반영이다.** 목록 밖 테스트가 깨지면 멈추고 보고. 공통 회귀 "범위" 판정은 이 목록을 U1 산출물로 본다.
  - 변이 → 잡는 테스트: V1-1 upgrade 에서 `DELETE FROM persons` 삭제 → ⑤ · V1-2 `username` UNIQUE 제거 → ③ · V1-3 `pending_questions.user_id` nullable → ④ · **V1-3b `ask_user` 의 `user_id=ctx.user_id` 줄 삭제 → 기존 `ask_user` 테스트(`tests/test_tools_questions.py` 등) NOT NULL 위반으로 실패** · V1-4 `role` CHECK 제거 → ③ · V1-5 downgrade 에서 테이블 하나 남김 → ⑦.

- [ ] U2 **[backend-agent] 인증 코어 — 비밀번호 해시·세션 토큰·쿠키 이름 규칙·`current_user` 의존성·Origin 검사·`/auth/signup`·`/auth/login`·`/auth/logout`·`/auth/me`** / Refs: P9b-auth D18 CR-006 security 원칙9 / 의존: U1
  - `app/auth/passwords.py`: 결정 C — `hashlib.scrypt`(n=2**14, r=8, p=1, dklen=32, 솔트 `secrets.token_bytes(16)`), 저장 형식 `scrypt$16384$8$1$<salt_b64>$<hash_b64>`(파라미터를 문자열에 담아 나중에 올릴 수 있게), 검증은 `hmac.compare_digest`. 새 의존성 0.
  - `app/auth/sessions.py`: 토큰 `secrets.token_urlsafe(32)`, DB 에는 `sha256(token)` hex 만. 만료 `now + AUTH_SESSION_DAYS`(결정 E). 조회는 만료 전만. 로그아웃은 그 행 삭제. 만료 행 정리는 하지 않는다(행 수가 작다 — 리스크 절).
  - 쿠키 이름(결정 F, R-5): `AUTH_COOKIE_SECURE` 가 켜져 있으면 **`__Host-rel_session`**, 꺼져 있으면(로컬 http) `rel_session`. 속성 `HttpOnly`·`SameSite=Lax`·`Path=/`·`Secure`(설정)·`Max-Age`=유지 기간·`Domain` 없음(`__Host-` 접두 조건). **`Path=/` 필수** — 없으면 브라우저 기본 경로가 `/api/auth` 가 되어 다른 API 에 쿠키가 실리지 않는다.
  - `app/auth/deps.py` `current_user(request, session) -> User`: 위 이름의 쿠키 → 해시 조회 → 사용자, 없거나 만료면 `HTTPException(401, {"code":"unauthenticated"})`.
  - `app/auth/origin.py` — **Origin 검사(결정 T, F-7 ③)**: 앱 전역 **한 곳**(미들웨어 또는 모든 라우터 공통 의존성)에서, 메서드가 POST·PUT·PATCH·DELETE 이고 `Origin` 헤더가 있으면 그 호스트(:포트)를 `X-Forwarded-Host`(있으면) 또는 `Host` 와 비교해 다르면 **403 `bad_origin`**. `Origin` 이 없거나 `null` 이 아닌 같은 호스트면 통과(`null` 은 다름으로 본다). **비교 규칙(R2-1 ①)**: 호스트는 소문자로, `Origin` 스킴의 기본 포트(`https`→443, `http`→80)는 양쪽에서 떼고 비교, `X-Forwarded-Host` 에 쉼표가 있으면 첫 값. 사실 10(Caddy 는 `Host` 전달)·사실 14(Vite 는 `xfwd` 로 `X-Forwarded-Host`).
  - `app/auth/routes.py`: 위 "API 계약" 표 그대로. 아이디 규칙 결정 A(소문자로 정규화 후 `^[a-z0-9_]{3,20}$`), 비밀번호 결정 B(8~128자). 가입 = 사용자 생성 + 세션 + 쿠키(결정 G). 로그인 실패는 없는 아이디·틀린 비밀번호를 같은 401 로, **없는 아이디에도 더미 해시 검증을 한 번 돌려** 응답 시간 차를 줄인다. **`/auth/logout` 은 `current_user` 의존성을 갖는다**(미로그인 401, F-3) — 204 본문 없음. 로그아웃의 `endpoint` 처리(푸시 구독 삭제)는 U5 에서 연결한다(이 단위는 인자만 받는다).
  - 로그·trace·응답·예외 메시지에 비밀번호·토큰 0(D18 지킬 것 3). `/auth/*` 는 `agent_traces` 를 쓰지 않는다(판정이 아님).
  - `.env.example` 에 `AUTH_COOKIE_SECURE` 이름 줄(주석: "운영 HTTPS 는 비우거나 1, 로컬 http 개발만 0").
  - 테스트:
    - `tests/test_auth_passwords.py` — 해시 ≠ 평문, 같은 비밀번호 두 번 해시가 다름(솔트), 맞는/틀린 검증, 형식 문자열 파싱.
    - `tests/test_auth_api.py` — 가입 201 + `Set-Cookie` 에 `HttpOnly`·`SameSite=lax`·`Path=/` · **쿠키 이름: Secure 켬 → `__Host-rel_session`, 끔 → `rel_session`(둘 다 `Domain` 속성 없음)** · 중복 409 · 규칙 위반 422 · 로그인 200/401 같은 본문 · `/auth/me` 쿠키 있으면 200 없으면 401 · **`/auth/logout` 쿠키 없이 401**, 쿠키 있으면 204 본문 없음 · 로그아웃 뒤 같은 쿠키로 `/auth/me` 401 · 만료된 세션 401(시계 주입) · DB 의 `users.password_hash` 에 평문 부분 문자열 0 · `auth_sessions.token_hash` ≠ 쿠키 값 · **(F-7 ②) 로그인 쿠키를 가진 채 `Content-Type: text/plain`(본문은 JSON 모양)·`application/x-www-form-urlencoded` 로 `POST /chat`·`POST /answers/{id}`·`POST /push/subscriptions` 를 보내면 4xx(415 또는 422)이고 `persons`·`events`·`pending_questions`·`push_subscriptions`·`agent_traces` 행 수 불변**(이 단위에서는 라우트가 아직 로그인을 요구하지 않지만 쿠키를 붙여 두어 U3b 뒤에도 401 이 아닌 본문 거부를 본다). **TestClient 는 `http://testserver` 라 `Secure` 쿠키를 다시 보내지 않는다** → 테스트는 `base_url="https://testserver"` 또는 `AUTH_COOKIE_SECURE=0` 중 하나로 — 방식 03-log.
    - `tests/test_auth_origin.py` — `Origin: https://evil-1-2-3-4.sslip.io` 로 `POST /auth/logout`·`POST /briefings/run`·`POST /chat` → 403 `bad_origin`, DB 변화 0 · 같은 호스트 `Origin` → 403 아님 · `Origin` 없음 → 403 아님 · `X-Forwarded-Host` 와 같은 `Origin` → 403 아님 · `GET` 에 다른 `Origin` → 403 아님 · **`Origin: https://testserver:443` ↔ `Host: testserver` → 403 아님(기본 포트 제거)** · **`Origin: https://TestServer` ↔ `Host: testserver` → 403 아님(소문자)** · **`X-Forwarded-Host: testserver, evil.example` + `Origin: https://testserver` → 403 아님(첫 값)**.
  - 변이: V2-1 `compare_digest` → `==` (기능 테스트는 통과 — 리뷰 grep 으로만 잡힘, 03-log 에 한계로) · V2-2 토큰 원문을 DB 에 저장 → "token_hash ≠ 쿠키" · V2-3 `HttpOnly` 제거 → 쿠키 속성 테스트 · V2-4 `Path` 제거 → 쿠키 속성 테스트 · V2-5 로그아웃이 행을 안 지움 → 로그아웃 뒤 401 · V2-6 없는 아이디에 404/다른 메시지 → 같은 본문 테스트 · **V2-7 Origin 검사 등록 제거(또는 비교를 항상 참으로) → origin 테스트** · **V2-8 쿠키 이름을 Secure 여부와 무관하게 `rel_session` → 쿠키 이름 테스트** · **V2-9 `/chat` 본문 모델을 `Request.json()` 직접 해석으로 바꿈(콘텐츠 타입 무시) → text/plain 테스트** · V2-10 로그아웃에서 `current_user` 제거 → 로그아웃 401 테스트.

- [ ] U3a **[backend-agent] 기존 테스트 이관(동작 불변) — `ToolContext(` 에 `user_id=` 명시·로그인 도우미** / Refs: P9b-auth D18 CR-006 원칙8 / 의존: U2 (R-9 — "동작 불변 이관" 과 "계약 변경"(U3b)을 리뷰에서 가르기 위해 뗀 단위)
  - `tests/auth_helpers.py`: ① `make_user(session, user_id="local", username=None)` — `users.id` 가 Text 이므로 **기존 값(`"local"` 등)을 id 로 하는 `users` 행을 직접 넣는다**(F-5 — 데이터 준비 코드 24파일 78곳을 건드리지 않기 위해) ② `logged_in_client(app, session_or_factory, user_id="local")` — **앱과 세션(또는 세션 팩토리)을 받는다**(테스트마다 `app.dependency_overrides[get_session]` 이 다르다, R2-2 ③). 그 사용자의 세션 행을 만들고 쿠키를 붙인 `TestClient`. **쿠키 이름은 U2 의 설정 이름 함수에서 얻는다**(하드코딩 금지 — `__Host-`/접두 없음이 설정에 따라 바뀐다, R2-2 ③) ③ `make_ctx(session, user_id=…, **kw)` 또는 각 호출에 `user_id=` 명시 ④ **실제 커밋을 쓰는 테스트용**(R2-2 ②): `tests/test_commit_boundaries.py`·`tests/test_answer_concurrency.py` 는 `get_session` 을 바꿔 끼우지 않고 실제 커밋한다 — 이 파일들의 도우미는 `users`·`auth_sessions` 행을 **커밋**하고 테스트 끝(픽스처 정리)에 지운다(`username` UNIQUE 가 재실행에서 부딪히지 않게; `username` 은 테스트마다 다른 값 권장). `tests/test_commit_boundaries.py:81,181,293` 의 `monkeypatch.setenv("APP_USER_ID", user_id)` 는 U3b 에서 그 `user_id` 로 로그인한 클라이언트로 바뀐다(N-2 ③) — 이 단위에서는 도우미만 준비해 둔다.
  - 사실 9 의 `ToolContext(` 호출 전부에 `user_id=` 를 명시하고(값은 지금 기본값이 주던 값과 같게), API 테스트의 `TestClient` 생성을 `logged_in_client` 로 바꾼다 — 이 단위에서는 라우트가 아직 쿠키를 보지 않으므로 **동작이 같다**. `scripts/run_pilot_eval.py` 의 `ToolContext(` 1곳도 같은 값을 명시(원칙8 — eval 경로 파일이라 03-log 에 따로 표시, `tests/test_eval_runner.py` 통과로 증명).
  - **테스트의 `app_user_id()` 호출·import 를 리터럴로(N-2 ①)**: `tests/test_push_wiring.py:57`(import 삭제)·111·127·204(`user_id=app_user_id()` → `user_id="local"`)·344(단언 우변의 `app_user_id()` → `"local"` — 같은 값, 기대값 변경은 U5 의 결정 U 에서) · `tests/test_answer_concurrency.py:48`(import 삭제)·83(→ `"local"`)·71·73·127 docstring 의 함수 언급. 지금 기본값과 같은 값이라 **동작 불변**. `tests/test_settings.py` 는 이 단위에서 두고 U5 에서 지운다.
  - 단언(기대값)은 바꾸지 않는다. 바꾼 파일 목록·파일별 바뀐 줄 수를 03-log 에.
  - 판정: 전체 pytest 결과가 U2 커밋 시점과 같다(passed 수 동일, 새 실패 0) · `app/` diff 0(`git diff --stat <U2 해시>..HEAD -- app` 빈 출력) · **테스트 쪽 고정 사용자 0**: `… u3a-tests-fixed-user -- bash <SCR>/u3a-tests-fixed-user.sh`(스크립트 안: `grep -rnE 'app_user_id|APP_USER_ID' tests scripts evaluation`) → 일치 줄이 `tests/test_settings.py`(U5 에서 삭제)와 `tests/test_commit_boundaries.py:81,181,293`(U3b 에서 교체)와 주석 2곳(`tests/test_push_subscriptions.py:90`·`tests/test_api_read_briefings_e2e.py:185`)뿐. 기대 exit 0(일치 있음 — 목록 대조), **exit 2 는 실패**(명령 오류).
  - 변이(이관 완결성): **V3a-1 저장소 밖 사본(또는 런타임 치환)에서 `app/tools/context.py` 의 `user_id` 기본값과 `app/settings.py` 의 `app_user_id` 함수를 함께 지운 상태로 `tests/test_settings.py`·`tests/test_commit_boundaries.py` 를 뺀 전체 pytest → U3a 와 같은 결과**(N-2 ① — `app/` 의 `ToolContext(` 4곳은 이미 `user_id=` 를 명시하고 함수 호출은 요청 경로·스케줄러에만 있어, 사본에서는 그 호출자들도 같은 값 리터럴로 치환한다; 실패가 나면 이관이 빠진 테스트·스크립트다 — 빠진 곳 0 이 완료 조건).

- [ ] U3b **[backend-agent] 모든 API 를 로그인 사용자 기준으로 — 401·남의 자원 404·답변 소유·`session_id` 계정 묶기·`ToolContext.user_id` 기본값 제거** / Refs: P9b-auth D18 S3.4 D2 D16 CR-006 F-fbaaae R-U10D-3 원칙5 원칙8 / 의존: U3a
  - `routes.py` 12개 중 `/health` 를 뺀 11개에 `user: User = Depends(current_user)`. **요청 경로**의 `app_user_id()` 를 `user.id` 로(`deps.py:156,240,332,346`, `routes.py:430,441,453,460,468,497`). `deps.py` 의 `ToolContext` 조립 함수 3개와 `get_notifier` 가 `user` 를 받는다. **`app/briefing/scheduler.py` 와 `app_user_id()` 함수 자체는 이 단위에서 건드리지 않는다**(요청 경로가 아님 — U5, F-2 (b)).
  - `session_id`: `/chat`·`/questions/pending` 은 **`chat:<user.id>`**(결정 S). `resolve_session_id`·`X-Session-Id` 헤더 의존 제거(헤더가 와도 무시 — 422 도 내지 않음). `ChatOut.session_id` 는 그 값.
  - 답변 소유(S3.4 보충, R-2 ③): **소유 조건을 거는 곳은 둘** — `app/api/deps.py:150` `build_ctx`(질문 조회에 `PendingQuestion.user_id == user.id`, 없으면 기존 "질문 없음" 404 와 같은 응답)와 `app/tools/questions.py:261` `answer_question`(`ctx.user_id` 조건 — 툴 층 방어). `deps.py:184` `load_resume_input`·`app/tools/persons.py:306`(`confirmed_question_id`)은 `build_ctx` 를 통과한 뒤에만 불리므로 그대로 둔다. `GET /questions/pending` 은 `user_id == user.id AND session_id == chat:<user.id>` 미답변. 모듈 docstring 의 "user_id 격리 부재(F-fbaaae)" 절을 "CR-006 로 해소" 로.
  - `ToolContext.user_id` 기본값 삭제(필드 순서상 `session_id` 다음 — 기본값 있는 필드보다 앞이라 문법 문제 없음). U3a 로 호출자가 모두 명시하므로 이 줄만 바뀐다.
  - 주석·docstring 정리(F-4 — 판정 #4 "0줄" 을 위해): `app/api/routes.py` 99·321·440행, `app/api/deps.py` 139·226·329·341행, `app/tools/questions.py:61` 의 `app_user_id`/`APP_USER_ID` 언급을 사실에 맞게 고친다(남은 `app/settings.py`·`scheduler.py:20` 은 U5). `app/api/read.py:51` 주석의 "(화면 3개 고정, 원칙5)" → "(CR-006 원칙5 개정 — 화면 수는 고정하지 않지만 이 목록은 상한을 둔다)" 식으로 사실만.
  - **바꿔도 되는 기존 단언 — 닫힌 목록(F-5)**: ① `invalid_session_id` 422 단언(`tests/test_api_chat.py`·`tests/test_api_questions_pending.py`) → "헤더가 무시되고 200" ② 응답·trace 의 `session_id` 기대값(헤더 값 또는 uuid 모양) → `chat:<user_id>` ③ 헤더 없는 `/questions/pending` 빈 목록 기대 → 로그인 계정 기준 목록. **③ 에는 "다른 세션 헤더를 보내면 빈 목록"(`tests/test_api_questions_pending.py:136` `_get(client, "none").json() == []`)도 든다**(①③ — 헤더가 무시되므로 기대가 계정 기준 목록으로 바뀐다, R2-2 ①). 다음은 **단언 변경이 아니다**(R2-2 ①·N-2 ③): 쿠키 없는 클라이언트로 남은 테스트에 `logged_in_client` 를 쓰는 것 · 세션 id 를 쓰는 **데이터 준비·조회 조건**(예: `tests/test_api_questions_pending.py` 의 `SID`, trace 를 `session_id` 로 거르는 헬퍼)을 `chat:<user_id>` 로 바꾸는 것 · `tests/test_commit_boundaries.py:81,181,293` 의 `monkeypatch.setenv("APP_USER_ID", user_id)` 를 그 `user_id` 로 로그인한 클라이언트(U3a 의 커밋형 도우미 ④)로 바꾸는 것. **그 밖의 단언을 바꿔야 통과하면 멈추고 보고**(행동 변경 신호). 바꾼 단언을 목록 번호와 함께 03-log 에.
  - 새 테스트:
    - `tests/test_auth_required_routes.py` — **`app.routes` 를 열거**해 `/health`·`/auth/signup`·`/auth/login`·문서 경로(`/docs`·`/redoc`·`/openapi.json`)를 뺀 모든 API 라우트가 쿠키 없이 401 `unauthenticated` 인지(경로 매개변수는 1 로 채움; **`/auth/logout` 은 예외가 아니다** — F-3). 새 라우트가 의존성을 빠뜨리면 실패한다(D18 지킬 것 4). `/push-dev/` 3경로는 기본 꺼짐이라 열거에 나오지 않는다 — 켜진 경우는 정적 개발 페이지라 예외 목록에 이름으로 두고 그 이유를 테스트 주석에(R-4 ③).
    - `tests/test_user_isolation.py` — 계정 A·B 를 만들고 B 의 인물·사건·사실·일정·브리핑 trace·질문을 직접 넣은 뒤 A 쿠키로: `GET /persons` 에 B 인물 0 · `GET /persons/{B}` 404 · `GET /events/{B}/raw` 404 · `GET /persons/{B}/facts/{f}/sources` 404 · `GET /briefings?schedule_id={B}` 404 · `GET /briefings` 에 B 것 0 · `POST /briefings/run {schedule_id:B}` 404 · `GET /questions/pending` 에 B 질문 0 · `POST /answers/{B 질문}` 404 + 그 행 `answer`·`answered_at` 불변 + **재개 루프 호출 0**(루프 진입점을 스텁으로 바꿔 호출 수 0 — R-4 ①) · `POST /chat` 의 `session_id` 가 `chat:<A.id>` 이고 `X-Session-Id: chat:<B.id>` 를 보내도 바뀌지 않는다 · **A 의 `/chat` 에서 스텁 LLM 이 B 의 `person_id` 로 `add_event`·`get_briefing` 을 제안해도 `PersonNotFound` 로 끝나고 B 의 `events`·trace 불변**(R-4 ② — 이제 `person_id` 가 계정 경계).
  - 판정(이 단위): 새 테스트 · 전체 pytest · `… u3b-ctx-default -- grep -n default_factory=app_user_id app/tools/context.py` → 0줄(단일 파일·따옴표 없는 패턴이라 래퍼 그대로; 기대 exit 1, exit 2 는 실패) · 요청 경로 grep — `… u3b-request-path -- bash <SCR>/u3b-request-path.sh`(스크립트 안: **`grep -rnE 'app_user_id|APP_USER_ID' app/api app/tools app/auth`** — 디렉터리라 `-r` 필수, N-3: `-r` 없이 래퍼의 `bash` 에서 돌리면 "Is a directory" exit 2 로 헛통과한다, `evidence/20261115-2036-planverify2-u3b-grep-probe.txt`). **기대 exit 1(일치 없음), exit 2 는 실패**(명령 오류 — 증거에 exit 가 찍힌다). **`app/` 전체 0줄(판정 #4)은 U5 끝에서 본다**(F-2).
  - 변이: V3b-1 라우트 하나(`GET /briefings`)에서 `current_user` 제거 → 열거 401 테스트 · V3b-2 `build_ctx` 의 `user_id` 조건 제거 → 격리 테스트(답변·재개 호출 0) · V3b-3 `session_id` 를 헤더에서 다시 받기 → 격리 테스트(헤더 무시) · V3b-4 `ToolContext.user_id` 기본값 복원 → `grep` 판정 · V3b-5 `list_persons` 에 `user.id` 대신 고정 문자열 → 격리 테스트.

- [ ] U4 **[backend-agent] 계정당 채팅방 하나 — 대화 기록 저장과 `GET /chat/history`** / Refs: P9b-auth D18 CR-006 security 원칙9 / 의존: U3b / U5 와 동시 가능
  - `app/chat/history.py`: `append(session, user_id, role, content, question_id=None)` · `recent(session, user_id, limit)`(최근 N 개를 골라 오래된 것 → 최근 순으로 돌려줌, 정렬 `created_at, id`).
  - 저장 규칙(결정 R): `POST /chat` — 사용자 발화 1행(`role=user`) + 응답 1행(`role=assistant`, `content=reply`, `question_id = pending_question.question_id` 있으면). `POST /answers/{id}` — 사용자가 고른 답 1행(`role=user`, `content=answer`, `question_id=id`) + 응답 1행(`role=assistant`, 새 질문이 있으면 그 id). **라우트의 기존 트랜잭션 안에서** 저장(요청이 실패해 롤백되면 기록도 없다). 루프가 오류를 200 답으로 삼키는 경우(P5 결정)도 그 답을 저장한다.
  - `GET /chat/history?limit=N`: 결정 I(기본 50, 최대 200). 로그인 계정 것만. 읽기 전용, trace 0.
  - `agent_traces`·`pending_questions.context` 에 대화 기록을 복사하지 않는다(security §5).
  - 테스트 `tests/test_chat_history.py`: 채팅 2턴 + 답변 1회(LLM 은 기존 테스트의 스텁 방식) 뒤 `GET /chat/history` 가 6행을 순서대로(user/assistant 교대, 질문이 달린 assistant 행에 `question_id`) · `limit=2` 면 최근 2행을 오래된 것부터 · 계정 B 의 기록 0 · 미로그인 401 · `/chat` 이 500 으로 실패(스텁이 예외)하면 기록 0 · `limit=0`/`201` 422.
  - 변이: V4-1 `recent` 정렬을 최근 → 오래된 것으로 → 순서 테스트 · V4-2 `user_id` 조건 제거 → B 기록 0 테스트 · V4-3 저장을 별도 커밋으로(롤백 밖) → 실패 시 기록 0 테스트.

- [ ] U5 **[backend-agent] 스케줄러·푸시 사용자별 — 사용자마다 브리핑 루프(0명이면 표식 `user_id=""` 로 `run_briefings` 1회), endpoint 는 마지막 구독 계정 하나, 로그아웃 시 그 브라우저 구독 떼기, 고정 사용자 함수 삭제** / Refs: P9b-auth D18 S3.6 R12 CR-006 원칙9 / 의존: U3b / U4 와 동시 가능
  - **창 상수(R2-3)**: 실체는 `app/settings.py:218` **`BRIEFING_LEAD_HOURS`**(`select_due_schedules` 는 인자로 받고, `run_briefings` 의 기본값은 `app/briefing/run.py:174` 에 def 시점에 묶여 있다). 스케줄러는 **호출 시점에 모듈 전역(`settings.BRIEFING_LEAD_HOURS`)을 읽어** 사용자 목록 질의와 `run_briefings(lead_hours=…)` **양쪽에 같은 값을 넘긴다**(이 모듈의 `BRIEFING_INTERVAL_SECONDS` 와 같은 관례 — `scheduler.py` docstring). 값이 갈리면 일정이 있는데 루프에서 빠지는 사용자가 생긴다.
  - `default_run_once`: 창 안(`now ≤ scheduled_at ≤ now + BRIEFING_LEAD_HOURS`) `briefed_at IS NULL` 일정이 있는 사용자 id 목록(`schedules → persons.user_id` DISTINCT — `users` 테이블이 아니라 `persons.user_id` 에서 구하므로 `users` 행 없이 `"local"` 로 데이터를 만드는 기존 스케줄러 테스트도 그대로 대상이 된다)을 구해 사용자마다 `ToolContext(session_id="briefing-scheduler:<uuid>", user_id=uid)` + `notifier_from_env(session, uid, now)` + `run_briefings(..., lead_hours=…)`. `run_briefings` 는 받은 ctx 의 세션 id 를 `briefing:<uuid>` 로 바꿔(`app/briefing/run.py:183`) `briefing_run` 행을 쓴다(`run.py:319-331`) — **행의 `session_id` 는 지금과 같이 `briefing:<uuid>`**(N-4 — 개정 1 의 "`briefing-scheduler:<uuid>` 행" 서술은 실물과 달라 정정). **사용자 단위 예외 격리**: 한 사용자에서 예외가 나면 로그(`logger.exception`, 사용자 id 만)하고 그 사용자 것은 롤백, 다음 사용자로(세션을 사용자마다 따로 여는 방식 권장 — 03-log).
  - **대상 사용자 0명(F-6·N-4 확정, 결정 U)**: **어느 계정과도 겹치지 않는 표식 `user_id` 빈 문자열 `""`** 의 `ToolContext`(+ `notifier_from_env(session, "", now)`)로 `run_briefings` 를 **1회** 부른다. 선택 0건이라 LLM·푸시 호출 0, `briefing_run` 행 1개(기존 형식, `session_id = briefing:<uuid>`)만 남는다 — 배포본에서 주기 작업이 살아 있는지 보는 유일한 신호이고 P9 S13 판정(`packages/P9-infra/01-plan.md:17`)이 그대로 선다. 근거: `users.id` 는 uuid4 hex(결정 O)이고 아이디 규칙(결정 A)도 3자 이상이라 빈 문자열과 겹치는 계정이 없다 → 그 ctx 로는 어떤 계정의 일정도 선택되지 않는다. 기존 테스트 4건(`tests/test_briefing_scheduler.py:202-206` "일정이 없어도 `default_run_once()` 가 `run_briefings` 를 한 번 부른다" · `tests/test_push_wiring.py:308-345` 3건 `captured["kwargs"]["notifier"]`·`captured["ctx"]`)이 그대로 선다. **U5 가 고치는 기존 단언은 `tests/test_push_wiring.py:344` 하나** — `notifier.user_id == ctx.user_id == "local"`(U3a 로 리터럴화) → `== ""`(대상 0명 표식).
  - `app/push/subscriptions.py` 구독 저장: 같은 `endpoint` 를 가진 **다른 사용자** 행을 지운 뒤 upsert(결정 P). `POST /auth/logout` 의 `endpoint` 가 있으면 그 사용자의 그 endpoint 행 삭제(U2 라우트에 연결).
  - **고정 사용자 제거 마무리(F-2 (b))**: `app_user_id()`·`DEFAULT_APP_USER_ID` 삭제, `app/settings.py` 4·42·322·350·381·435·492행과 `app/briefing/scheduler.py:20` 의 주석·docstring 언급 정리, `.env.example` `APP_USER_ID` 줄 삭제(결정 J). **`tests/test_settings.py` 삭제**(그 함수의 해석 규칙 테스트 2건뿐 — 통과 수 −2, 03-log 에 기록, N-2 ②) · `.github/workflows/tests.yml:176` `echo "APP_USER_ID=ci-smoke"` 줄 삭제(폐지된 이름, 무해). 이 단위 커밋에서 판정 #4(`app/` 전체 0줄)와 **`tests`·`scripts`·`evaluation`·`.github` 의 일치가 주석 2곳(`tests/test_push_subscriptions.py:90`·`tests/test_api_read_briefings_e2e.py:185` — 이 단위에서 문구를 "로그인 사용자" 로 고쳐도 됨)뿐**임을 본다: `… u5-outside-app -- bash <SCR>/u5-outside-app.sh`(스크립트 안: `grep -rnE 'app_user_id|APP_USER_ID|DEFAULT_APP_USER_ID' tests scripts evaluation .github`; 기대 exit 1 이면 0줄, exit 0 이면 위 주석 2곳만, exit 2 는 실패).
  - 테스트 `tests/test_briefing_scheduler_users.py`: 사용자 A·B 각각 창 안 일정 1건 → 1회 실행에 두 일정 모두 `briefed_at` · A 처리에서 예외(스텁) → B 는 브리핑됨 · 알림기가 사용자별 구독으로만 보냄(스텁 알림기에 기록된 (user_id, endpoint) 쌍) · 창 밖·남의 일정 미처리 · **창 경계: `lead_hours` 시간 뒤 일정은 포함, 그보다 1분 뒤는 미포함(선택 함수와 같은 결과)** · **대상 0명 → `run_briefings` 가 `user_id == ""` ctx 로 정확히 1회 불리고 `briefing_run` trace 정확히 1행(`session_id` 가 `briefing:` 로 시작), 형식은 기존 테스트(`tests/test_briefing_scheduler.py`)가 보는 키와 같음** · **대상 1명 이상이면 `""` ctx 호출 0**. `tests/test_push_endpoint_owner.py`: A 가 endpoint E 구독 → B 가 같은 E 구독 → A 의 E 행 0, B 1 · A 의 일정 브리핑이 E 로 가지 않음 · 로그아웃 `{endpoint:E}` → 그 사용자 E 행 0, 다른 endpoint 유지.
  - 변이: V5-1 사용자 루프 대신 첫 사용자만 → 두 일정 테스트 · V5-2 예외 격리 제거 → B 브리핑 테스트 · V5-3 다른 사용자 같은 endpoint 삭제 제거 → endpoint 테스트 · V5-4 로그아웃 endpoint 삭제 제거 → 로그아웃 테스트 · **V5-5 0명일 때 `run_briefings` 를 부르지 않음 → 0명 1행 테스트 + 기존 `tests/test_briefing_scheduler.py:202-206`·`tests/test_push_wiring.py:308-345`** · **V5-5b 0명 표식을 `"local"` 같은 실제 사용자 값으로 → `test_push_wiring.py:344`(`== ""`)** · **V5-6 사용자 목록 창을 `now + 24h` 리터럴로(상수 대신) 하고 테스트에서 `settings.BRIEFING_LEAD_HOURS` 를 바꿔 실행 → 창 경계 테스트**.

- [ ] U6 **[frontend-agent] 로그인·가입 화면(관문), 로그아웃, 대화 기록 불러오기, 401 처리, `X-Session-Id` 제거** / Refs: P9b-auth D18 CR-006 원칙5 / 의존: U2 커밋(계약 확정) — **U3a~U5 와 동시**(위 API 계약 + 목 응답)
  - **화면 방식(결정 L): 관문** — `App` 이 시작 때 `GET /auth/me` → 200 이면 지금의 `AppShell`(채팅/인물/브리핑 그대로), 401 이면 `AuthScreen`(로그인·가입 전환 한 화면: 아이디·비밀번호 입력, 가입은 비밀번호 확인 칸, 규칙 안내 한 줄, 409·401·422·403 메시지). 해시 라우트를 더하지 않는다 — 이유: ① 로그인 상태가 곧 분기라 `useRoute` 의 알 수 없는 해시 처리·보호 경로 리다이렉트를 새로 만들 필요가 없다 ② 알림 클릭 주소(`#/briefings?schedule_id=`)가 로그인 뒤 그대로 열린다(관문을 통과하면 해시가 살아 있음) ③ 테스트가 "me 200 → 셸 / 401 → 로그인 화면" 두 갈래로 끝난다. 원칙5 폐지로 정식 라우트도 허용되지만 이 이유로 관문을 고른다.
  - `client.ts`: `credentials: 'same-origin'` 명시, `SESSION_HEADER` 와 세션 헤더 전송 제거, 422 `invalid_session_id` 처리 제거, **204 는 본문을 읽지 않는다**(R-3), **401 이면 전역 "로그아웃됨" 신호**(이벤트 또는 콜백) → `App` 이 관문으로. 새 함수 `signup`·`login`·`logout(endpoint?)`·`getMe`·`getChatHistory(limit?)`. **`logout` 이 401 을 받으면 "이미 로그아웃됨" 으로 보고 오류 없이 관문으로**(F-3). `types.ts` 에 `MeOut`·`ChatHistoryItemOut`. `session.ts` 는 삭제하거나 비워 호출 0 — 남은 localStorage 키는 로그인 성공 때 한 번 지운다.
  - `web/vite.config.ts` 프록시에 `xfwd: true`(사실 14 — 로컬 개발에서 Origin 검사가 `X-Forwarded-Host` 로 통과하도록). `src/proxy.ts`·`proxy.test.ts` 가 프록시 설정을 단언하면 함께.
  - `AppShell`: 사이드바 아래에 "<아이디> · 로그아웃" 한 줄. 로그아웃 = 서비스 워커 구독이 있으면 그 `endpoint` 를 함께 보내고(`push.ts` 의 현재 구독 조회 재사용) → 관문으로. **채팅방 목록은 만들지 않는다**(원칙7).
  - `ChatScreen`: 마운트 때 `getChatHistory()` 로 메시지 목록을 채우고(기존 메시지 모양으로 변환, 결정 I 개수), 미답변 칩은 지금처럼 `getPendingQuestions()`. 기록 불러오기 실패는 한 줄 안내 후 빈 채팅으로(입력은 막지 않음).
  - 주석: `routes.ts:1` "원칙5 — 화면 3개 고정. 새 경로를 더하지 않는다." · `App.tsx:8` 을 원칙5 개정(CR-006)에 맞게 사실만으로. 하네스 `.claude/agents/frontend-agent.md` 25행은 메인 세션이 `5c0f26d` 에서 처리했다(기준 해시) — 위임 프롬프트에 "CR-006 로 원칙5 폐지, 로그인 화면은 계획 U6 범위" 를 인용.
  - **E2E(사실 9 — CI 가 `npm run e2e` 를 돈다, `tests.yml:242-245`)**: 관문이 생기면 `/auth/me` 목이 없는 E2E 는 전부 로그인 화면에서 멈춘다 → **최소 `web/e2e/fixtures.ts` 에 `/auth/me` 200 목을 더한다**(R-11 ①). 로그인 화면 E2E 1건은 일정이 남으면.
  - 테스트(Vitest): `auth.test.tsx` — me 401 → 로그인 화면 · 로그인 성공 → 셸 · 가입 409 메시지 · 비밀번호 확인 불일치 시 요청 0 · API 가 401 을 주면 관문 복귀 · 로그아웃이 endpoint 를 보냄 · **로그아웃이 401 을 받아도 오류 표시 없이 관문** · **로그아웃 204 에서 예외 없음**. `api.test.ts` — `X-Session-Id` 헤더 없음 · `credentials: 'same-origin'` · 204 응답에서 `json()` 을 부르지 않음. `chat.test.tsx` — 마운트 시 기록 표시(순서). 기존 테스트의 세션 관련 단언은 새 계약으로(바꾼 단언 목록 03-log).
  - 판정: `npm --prefix web run typecheck` · `npm --prefix web exec -- vitest run` · `npm --prefix web run build` · `npm --prefix web run e2e`(CI 와 같은 명령) 통과.
  - 변이: V6-1 401 처리 제거 → "401 → 관문 복귀" · V6-2 `X-Session-Id` 다시 보냄 → api 테스트 · V6-3 기록 순서 뒤집기 → chat 테스트 · V6-4 204 에서 `json()` 호출 → 로그아웃 204 테스트.

- [ ] U7 **[메인 세션 + 사용자] 문서·로컬 통합 스모크·배포 반영·바깥 스모크** / Refs: P9b-auth D18 D17 CR-006 security R14 / 의존: **U1~U6 각 단위의 verifier 리뷰 통과 + 반영할 해시에서의 전체 pytest 증거**(R-7)
  - 문서(메인): `docs/RUNNING.md`(로그인·`AUTH_COOKIE_SECURE=0` 로컬 http 개발·개발 DB 비워짐 안내) · `docs/user-setup/11-ec2-minimal-deploy.md` 58·105행(`APP_USER_ID` → "계정으로 나뉜다, 서버 `.env` 의 `APP_USER_ID` 줄은 남아도 무시") · `13-user-todo-deploy.md`(41·46행 `APP_USER_ID` 기억 초기화 안내 → "새 계정으로", P9b 반영 절차·OpenAI 사용량 확인·0003 뒤 되돌릴 수 없음) · `SERVER-CHECKLIST.md` §5(시연 두 갈래) · `registry.md` 새 행(U1~U6 산출물).
  - **Caddy 경유 Origin 스모크(메인, 에이전트 실행 가능 — 로컬 compose, 배포 반영 전 필수)**: Origin 검사(결정 T)가 Caddy 뒤에서 같은 출처 POST 를 막지 않는지는 단위 테스트로 알 수 없다(사실 10 은 Caddy 기본 동작에 대한 이해일 뿐 이 저장소에서 확인한 적 없음). P9 U1 의 로컬 compose 스모크와 같은 방식(`docker-compose.prod.yml`, 프로젝트 이름 분리, 개발 DB 불변)으로 운영 이미지를 띄우고 `curl -k` 로컬: `Origin` 을 접속 호스트와 같게 준 `POST /api/auth/signup` → 201(403 아님) · 다른 `Origin`(`https://evil-1-2-3-4.sslip.io`) → 403 `bad_origin` · 응답 `Set-Cookie` 이름·`Path=/`·`Secure` · **(R2-1 ②) 클라이언트가 `X-Forwarded-Host: evil-1-2-3-4.sslip.io` 와 `Origin: https://evil-1-2-3-4.sslip.io` 를 함께 보내도 403**(Caddy 가 클라이언트의 `X-Forwarded-Host` 를 자기 값으로 덮어쓰는지 실물 확인 — 통과하지 않아도 브라우저 공격 경로는 아니지만(교차 사이트 요청은 이 헤더를 붙이면 사전 요청에서 막힌다) 사실 10 의 빈칸을 증거로 채운다; 403 이 아니면 결과를 03-log 에 적고 메인이 사용자에게 보고). **이 스모크가 실패하면(같은 출처 POST 가 403) 배포 반영을 하지 않는다**(반영되면 브라우저의 모든 POST 가 403 — 시연 불가). **0003 이 운영에 적용된 뒤에는 옛 해시로 되돌릴 수 없으므로**(R2-1 ③ — 리스크 절) 이 스모크와 아래 로컬 브라우저 점검은 반영 전 **필수**다. 증거 `u7-caddy-origin`.
  - **로컬 통합 스모크(메인, 에이전트 실행 가능 — 로컬 서버)**: 개발 DB 에 `alembic upgrade head` 뒤 `uvicorn … --env-file .env`(L-007) 기동(`AUTH_COOKIE_SECURE=0`) → 스크래치패드 스크립트로 `curl` 로컬: 가입 A·B → A 로 `/chat` 1턴(실 LLM — 사용자 `.env` 의 키, 값 노출 없음) → B 쿠키로 `/persons` 에 A 인물 0 → A 의 인물 id 로 B 가 `/persons/{id}` 404 → 다른 `Origin` 으로 A 의 `/chat` 403 → A 로그아웃 뒤 A 쿠키 401 → A 재로그인 `/chat/history` 2행. 비밀번호는 스크래치패드 파일로만, 증거에는 마스킹. 프론트는 `npm --prefix web run dev` 로 사람 점검 1회(로그인·가입·로그아웃·기록 이어보기 — 사용자 또는 메인이 브라우저; Origin 검사가 개발 프록시에서 막지 않는지 포함).
  - **배포 반영(사용자 몫 — 아래 "사용자만 할 수 있는 일" 1~3)**: 서버 SSH 에서 `cd Relationship && git fetch && git checkout <메인이 알려 준 해시>` → `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build` → `docker compose -f docker-compose.prod.yml ps`(세 서비스 running/healthy) → `docker compose -f docker-compose.prod.yml logs --tail=200 backend` 에 Traceback 0 과 alembic `0003` 적용 줄. **이 기동이 운영 데이터를 비운다**(결정 4 — 반영 직전 사용자에게 한 번 더 알린다; 원하면 그 전에 `pg_dump` 1회 — 12 문서 1항 명령). **0003 이 적용된 뒤에는 옛 해시로 되돌릴 수 없다 — 문제는 앞으로 고쳐 다시 올린다**(옛 코드의 entrypoint `alembic upgrade head` 가 모르는 리비전 `0003` 을 만나 backend 가 뜨지 않는다, R2-1 ③). 새 `.env` 값은 **필요 없다**(결정 D). 해시는 dev2 커밋 해시(승격 전 반영 — 평가 일정 때문, 선례 P9 `843e6e7`; 사용자 완성 확인 뒤 dev·main 승격과 해시 일치 확인).
  - **바깥 스모크(메인, 본문 없는 GET 만 — security §4)**: `https://54-79-202-221.sslip.io/api/health` → 200·`alembic_revision` 이 `0003` · `/api/persons`·`/api/auth/me`·`/api/chat/history` 쿠키 없이 401 · `/` 200. 로그인·가입 POST 와 화면은 사용자(브라우저).
  - 판정: 아래 판정 표 #1·#9·#10.

- [ ] U8 **[사용자 + 메인 세션] 시연 계정 데이터 쌓기와 시연 두 갈래 리허설(배포 URL)** / Refs: P9b-auth D18 CR-006 원칙8 원칙1 / 의존: U7 배포 반영
  - 순서(CR-006 §4-6): **비우기(U7 반영 때 0003) → 시연 계정 가입 → 시연 계정에 실제 대화로 데이터 쌓기 → 새 계정 가입으로 (가) 확인 → 시연 계정 재로그인으로 (나) 확인**.
  - 데이터 쌓기(결정 Q 권장): 시연 계정(아이디는 사용자가 정함, 예 `demo`)으로 배포 URL 채팅에 **제품 파이프라인 그대로** 대화를 넣는다 — README "데모 시나리오"·SERVER-CHECKLIST §5 의 발화(첫 언급 → 사건 누적 → 승진 호칭 변이 → 일정 등록 → 브리핑)를 바탕으로 메인 세션이 **발화 목록 10~15개**(인물 3~4명, 사건 유형 여러 개, 같은 유형 3회 이상인 인물 1명 — 패턴 사실 생성, 24시간 안 일정 1건 — 브리핑)를 03-log 에 적어 사용자에게 준다. 확인 칩이 뜨면 사용자가 판단해 누른다(원칙1 — 자동 병합을 강제하지 않는다). 평가 수치와 무관하고 데이터셋·라벨을 바꾸지 않는다(원칙8).
  - 확인(사람, 증거는 사용자가 준 화면 설명·응답을 메인이 Write 로 `evidence/<시각>-u8-*.txt`): (나) 시연 계정 로그아웃 → 재로그인 → 지난 대화가 이어서 보임 · 인물 카드에 사실·타임라인(패턴 포함) · 브리핑 화면에 브리핑 1건 이상. (가) 새 계정 가입 → 인물 화면 0명 · 채팅 빈 기록 · 첫 언급 1턴 → 새 인물 확인 칩. 격리: 새 계정 인물 화면에 시연 계정 인물 0, 시연 계정 인물 상세 주소(`#/persons/<id>`)를 새 계정에서 열면 404 안내.
  - 시드 스크립트(결정 Q 후보 — 권장하지 않음): DB 에 인물·사건을 직접 넣는 스크립트는 화면 모양은 같지만 ER·루프·승격을 거치지 않아 "데이터가 들어 있으면 어떻게 해 주는지" 의 근거가 약하다. 실제 대화가 실패할 때의 예비안으로만 남긴다(쓰면 03-log·시연 설명에 "시드" 라고 밝힌다).

### 3차 검증 권고 반영 (메인 세션 2026-11-15 — 위 단위 문장에 더해 적용한다)
- **R3-1 (U1 닫힌 목록에 추가)**: `tests/test_api.py:91` `assert body["alembic_revision"] == "0002"` → `"0003"`. 리비전 문자열을 단언하는 곳은 저장소에서 이 한 줄뿐이다.
- **R3-2 (재귀 grep 판정 전부)**: `u3a-tests-fixed-user.sh`·`u3b-request-path.sh`·`u5-no-fixed-user.sh` 의 재귀 grep 에 `--include='*.py'` 를 붙인다. `.github` 를 함께 보는 `u5-outside-app.sh` 는 `--exclude-dir=__pycache__`. (`__pycache__/*.pyc` 가 일치해 헛실패하는 것을 막는다.)
- **R3-3 (U7 문서 목록에 추가)**: `docs/reliability.md:101` "이 프로젝트에는 인증이 없다. 서버 환경변수 `APP_USER_ID` …" 를 패키지 뒤 사실로.
- **R3-4 (U3a)**: `tests/test_answer_concurrency.py` 는 docstring 3곳(71·73·127행)의 언급까지 고친다 — 03-log 에 "docstring 포함" 을 적는다.

### 범위 축소 순서 (일정이 밀릴 때 — CR-006 결정 3 "밀리면 범위를 줄인다". 판단 시점: 11-16 밤까지 U3b 미커밋이면 1·4 적용, R-13)
1. U8 의 발화 수를 줄인다(인물 2명·일정 1건).
2. U6 의 E2E 는 **`web/e2e/fixtures.ts` 에 `/auth/me` 200 목만 더하는 최소 갱신**으로 한다(로그인 화면 E2E 는 뺀다 — CI 가 E2E 를 돌므로 갱신 자체는 뺄 수 없다, R-11 ①).
3. U5 의 로그아웃 endpoint 삭제를 뺀다 — **이것은 수용 기준 6번 "다른 계정의 일정 알림이 내 브라우저로 오지 않는다" 를 글자 그대로는 깨뜨리므로(A 로그아웃 뒤 B 가 구독 없이 쓰면 A 알림이 온다) 수용 기준 변경이고 사용자 결정이다**(R-11 ②). 메인이 묻기 전에는 적용하지 않는다.
4. U4 의 `/answers` 기록을 뺀다(채팅 발화·응답만).
**빼지 않는 것**: U1~U3b(격리·401·답변 소유)·U2 Origin 검사·U6 관문·U7 반영 — 이것이 시연 두 갈래의 최소 조건이다. 줄이면 03-log 와 04-review 에 "범위 축소" 로 적고 사용자에게 보고.

## 판정 방법

명령은 저장소 루트에서, 증거는 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> -- <명령>`(FIX-034). 환경변수는 래퍼 앞. **따옴표·`$`·`|` 가 든 안쪽 명령은 스크래치패드 `<SCR>/<이름>.sh` 로 Write 해 `-- bash <SCR>/<이름>.sh`**(P9 F-P9V-2 와 같은 우회 — `save_evidence.py` 는 `--` 뒤 인자를 공백으로 이어 `bash -c` 로 돌려 따옴표가 사라지고 `|` 가 파이프가 된다, 02-plan-verify F-4 `evidence/20261115-2019-planverify-cmd4-probe.txt`). `alembic` 은 `.venv/bin/python -m alembic`. `<URL>` = `https://54-79-202-221.sslip.io`.

### 수용 기준 구절별

| # | 수용 기준 구절 | 판정 | 명령 / 점검 | 실행 | 단위 |
|---|---|---|---|---|---|
| 1 | 가입·로그인·로그아웃·내 정보 API 가 동작하고 비밀번호는 해시로만 저장된다 | 기계 | `… u2-auth -- .venv/bin/python -m pytest tests/test_auth_api.py tests/test_auth_passwords.py -q` 전부 passed · U7 로컬 통합 스모크(가입→me 200→로그아웃→me 401) · `… u2-hash-grep -- .venv/bin/python -m pytest tests/test_auth_api.py -q -k plaintext` | 에이전트 | U2·U7 |
| 2 | `/health`·`/auth/signup`·`/auth/login` 밖의 모든 API 가 로그인 없이 401 | 기계 | `… u3b-auth-required -- .venv/bin/python -m pytest tests/test_auth_required_routes.py -q`(예외는 이 3개 + 문서 경로뿐, `/auth/logout` 포함 401) + 배포 GET 401(#10) | 에이전트 | U3b·U7 |
| 3 | 계정 A 로 계정 B 의 인물·사건 원문·사실 근거·일정 브리핑·대기 질문에 접근하면 404 이고 B 의 질문에 답할 수 없다(F-fbaaae 닫힘) | 기계 | `… u3b-isolation -- .venv/bin/python -m pytest tests/test_user_isolation.py -q` · U7 로컬 통합(B 가 A 인물 404) | 에이전트 | U3b·U7 |
| 4 | 요청 경로의 `app_user_id()` 호출 0·`ToolContext.user_id` 기본값 없음 | 기계 | **U5 커밋 시점**에 `… u5-no-fixed-user -- bash <SCR>/u5-no-fixed-user.sh`(스크립트 안: `grep -rnE 'app_user_id|APP_USER_ID' app`; 기대 0줄 — exit 1 이 기록됨, **exit 2 는 실패**. 주석·docstring 언급도 0 이어야 한다 — U3b·U5 의 정리 목록) · `… u3b-ctx-default -- grep -n default_factory=app_user_id app/tools/context.py` → 0줄(U3b 부터, 기대 exit 1, exit 2 는 실패) | 에이전트 | U3b·U5 |
| 5 | 계정마다 채팅방 하나 — 대화 기록이 서버에 저장되고 다시 로그인하면 이어서 보이며 session_id 는 계정에 묶인다 | 기계 + 사람 | `… u4-history -- .venv/bin/python -m pytest tests/test_chat_history.py -q` · `test_user_isolation.py` 의 `session_id` 단언 · U6 `chat.test.tsx` · U8 (나) 재로그인 이어보기(사람) | 에이전트 + 사용자 | U3b·U4·U6·U8 |
| 6 | 브리핑 주기 작업과 푸시가 사용자마다 돌고 다른 계정의 일정 알림이 내 브라우저로 오지 않는다 | 기계 | `… u5-scheduler-users -- .venv/bin/python -m pytest tests/test_briefing_scheduler_users.py tests/test_push_endpoint_owner.py -q` · 기존 `tests/test_briefing_scheduler.py` 통과 | 에이전트 | U5 |
| 7 | 리비전 0003 이 기존 데이터를 비우고 `alembic upgrade head`·`alembic check` 통과 | 기계 | `… u1-migration -- .venv/bin/python -m pytest tests/test_migration_0003.py -q` · `… u1-upgrade -- .venv/bin/python -m alembic upgrade head` · `… u1-check -- .venv/bin/python -m alembic check` → `No new upgrade operations detected.` · 배포 `/api/health` `alembic_revision` 0003(#10) | 에이전트 | U1·U7 |
| 8 | 프론트 로그인·가입 화면·로그아웃·대화 기록 불러오기·401 시 로그인 화면 복귀 | 기계 + 사람 | `… u6-vitest -- npm --prefix web exec -- vitest run` · `… u6-typecheck -- npm --prefix web run typecheck` · `… u6-build -- npm --prefix web run build` · `… u6-e2e -- npm --prefix web run e2e` · U7 로컬 브라우저 점검 1회 · U8 배포 화면 | 에이전트 + 사용자 | U6·U7·U8 |
| 9 | 배포 URL 에서 시연 두 갈래 재현 — (가) 새 계정 가입 뒤 빈 상태 (나) 데이터가 쌓인 시연 계정으로 로그인해 인물 카드·브리핑·대화 기록이 보이고, 새 계정에는 시연 계정의 인물이 보이지 않는다 | 사람 | U8 확인 목록 → `evidence/<시각>-u8-demo-two-paths.txt` | 사용자 | U8 |
| 10 | (배포 반영 증거 — #2·#7 의 배포 쪽) | 기계 | `… u7-public-health -- curl -fsS <URL>/api/health` → `alembic_revision` 0003 · `… u7-public-401 -- bash <SCR>/u7-401.sh`(스크립트 안: `curl -s -o /dev/null -w '%{http_code}' <URL>/api/persons`·`/api/auth/me`·`/api/chat/history` → 각 401) · `… u7-public-root -- bash <SCR>/u7-root.sh`(`curl -fsS -o /dev/null -w '%{http_code}' <URL>/` → 200) | 에이전트 | U7 |
| 11 | 툴 7종 불변(`tools_check` 7/7) | 기계 | `POSTGRES_PORT=5433 … u<N>-tools-check -- .venv/bin/python scripts/tools_check.py` → 7/7 | 에이전트 | 전 단위 |
| 12 | pytest 전체 통과 skip 0 | 기계 | `POSTGRES_PORT=5433 … u<N>-pytest-all -- .venv/bin/python -m pytest -q` → **실패 0 · skip 0**, 통과 수 = 기준선 2261 + 새 테스트 − (U5 이후) `tests/test_settings.py` 2건 | 에이전트 | 전 단위 |
| 13 | (보안 보강 — 수용 기준 밖, 결정 T·F-7) | 기계 | `… u2-origin -- .venv/bin/python -m pytest tests/test_auth_origin.py -q` · `test_auth_api.py` 의 text/plain·폼 본문 4xx·DB 불변 · 쿠키 이름 단언 | 에이전트 | U2 |

### 단위 공통 회귀 (단위마다, 리뷰 전)

| 항목 | 명령 | 기대 |
|---|---|---|
| 전체 pytest | 위 #12 | 위 #12 기대 |
| ruff | `… u<N>-ruff -- .venv/bin/python -m ruff check app tests scripts evaluation` | 통과 |
| mypy | `… u<N>-mypy -- .venv/bin/python scripts/mypy_check.py --run` | 새 오류 없음(기준선 38) |
| 툴 7종 | 위 #11 | 7/7 |
| ER·평가 무변경 | `… u<N>-er-unchanged -- git diff --stat <기준>..HEAD -- app/er evaluation reports data` | 빈 출력(U3a 의 `scripts/run_pilot_eval.py` 는 이 목록 밖 — 별도 03-log) |
| 범위 | `… u<N>-scope -- git diff --name-only <직전 단위 해시>..HEAD` | 그 단위 산출물 표의 파일만 |
| 비밀 0 | Write 단계 `secret-guard`·`save_evidence.py` 내장 검사 통과 · 증거에 비밀번호·쿠키 값 0(저장 전 메인이 읽는다) | — |

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 가입·로그인·로그아웃·내 정보 API 가 동작하고 비밀번호는 해시로만 저장된다 + `/health`·`/auth/signup`·`/auth/login` 밖의 모든 API 가 로그인 없이 401 + 계정 A 로 계정 B 의 인물·사건 원문·사실 근거·일정 브리핑·대기 질문에 접근하면 404 이고 B 의 질문에 답할 수 없다(F-fbaaae 닫힘) + 요청 경로의 `app_user_id()` 호출 0·`ToolContext.user_id` 기본값 없음 + 계정마다 채팅방 하나 — 대화 기록이 서버에 저장되고 다시 로그인하면 이어서 보이며 session_id 는 계정에 묶인다 + 브리핑 주기 작업과 푸시가 사용자마다 돌고 다른 계정의 일정 알림이 내 브라우저로 오지 않는다 + 리비전 0003 이 기존 데이터를 비우고 `alembic upgrade head`·`alembic check` 통과 + 프론트 로그인·가입 화면·로그아웃·대화 기록 불러오기·401 시 로그인 화면 복귀 + 배포 URL 에서 시연 두 갈래 재현 — (가) 새 계정 가입 뒤 빈 상태 (나) 데이터가 쌓인 시연 계정으로 로그인해 인물 카드·브리핑·대화 기록이 보이고, 새 계정에는 시연 계정의 인물이 보이지 않는다 + 툴 7종 불변(`tools_check` 7/7) + pytest 전체 통과 skip 0

## 사용자 결정 (상수·정책 — **권장안을 기본값으로 채택**, 사용자 지시 2026-11-15. 표는 근거를 보이려고 남긴다. 사용자가 다르게 정하면 그 값으로 바꾼다)

이 계획의 결정은 "P9b 결정 A~U" 로 부른다(CR-006 결정 1~4 와 구별). 이미 확정돼 묻지 않는 것: 아이디+비밀번호 · 계정당 채팅방 하나·목록 없음 · 평가 전 배포 · 기존 데이터 비움 · 원칙5 폐지.

| # | 항목 | 후보 | **채택(권장)** | 이유 |
|---|---|---|---|---|
| A | 아이디 규칙 | (i) `^[a-z0-9_]{3,20}$`, 입력은 소문자로 정규화 (ii) 한글 허용 (iii) 이메일 형식 | **(i)** | 대소문자 혼동·유니코드 정규화 문제 없음, 시연에서 짧게 입력 |
| B | 비밀번호 길이 | (i) 8~128자, 복잡도 규칙 없음 (ii) 10자 + 숫자·기호 필수 (iii) 4자 | **(i)** | NIST 권고 방향(길이 중심), 상한 128 은 해시 입력 상한 |
| C | 해시 알고리즘·라이브러리 | (i) 표준 라이브러리 `hashlib.scrypt`(n=2^14, r=8, p=1, 솔트 16B) (ii) `argon2-cffi`(Argon2id) (iii) `bcrypt` | **(i)** | 새 의존성 0 — ARM(t4g) 휠·이미지 재빌드 위험 없음. (ii) 가 OWASP 1순위지만 의존성 추가·검증 시간이 든다. 형식 문자열에 파라미터를 담아 나중에 올릴 수 있다. 호출당 약 16 MB·약 0.02 s(verifier 측정) |
| D | 로그인 유지 방식 | (i) 서버 DB 세션 테이블 + 무작위 토큰 HttpOnly 쿠키(토큰 해시만 저장) (ii) 서명 쿠키(`itsdangerous`, 서버 `.env` 에 `SESSION_SECRET`) (iii) JWT | **(i)** | **새 서버 비밀 값 0** → 배포 반영에 `.env` 수정이 필요 없다. 로그아웃 즉시 무효. 같은 출처라 CORS 불필요 |
| E | 로그인 유지 기간 | (i) 7일 고정(연장 없음) (ii) 30일 (iii) 브라우저 닫으면 끝(세션 쿠키) | **(i)** | 11-17 준비 → 11-18 시연 → 11-19 종료를 덮는다 |
| F | 쿠키 이름·속성 | (i) 이름 — `AUTH_COOKIE_SECURE` 켬: **`__Host-rel_session`**, 끔(로컬 http): `rel_session` · 속성 `HttpOnly`·`SameSite=Lax`·`Path=/`·`Domain` 없음·`Secure`(설정 `AUTH_COOKIE_SECURE`, 기본 켜짐)·`Max-Age`=E (ii) `SameSite=Strict` (iii) 이름 접두 없음 | **(i)** | **사실대로(F-7)**: `sslip.io` 는 공개 접미사 목록에 없어 다른 `*.sslip.io` 호스트가 우리와 **같은 사이트**다 — `SameSite=Lax` 만으로는 그 호스트에서 오는 POST 를 막지 못한다(보조 방어일 뿐). 주 방어는 JSON 본문 요구(FastAPI 가 JSON 아닌 본문을 해석하지 않음 — U2 테스트) + Origin 검사(결정 T). `__Host-` 접두는 다른 `*.sslip.io` 가 `Domain=sslip.io` 쿠키로 우리 쿠키를 덮는 것을 브라우저가 막게 한다(R-5). Strict 는 알림 클릭으로 열 때 쿠키가 안 실릴 소지 |
| G | 가입 개방·가입 뒤 동작 | (i) 누구나 가입, 가입 즉시 로그인 (ii) 초대 코드(서버 `.env`) (iii) 계정 수 상한 | **(i)** | 시연 (가) 가 "심사자 앞에서 새 계정 만들기". 지금(로그인 없음)보다 노출이 늘지 않는다. LLM 비용 상한은 OpenAI 월 한도 그대로 — 소진 위험은 리스크 절(R-6) |
| H | 로그인 시도 제한 | (i) 두지 않음 (ii) 프로세스 메모리 카운터 — 아이디당 5회 실패 시 5분 잠금(`--workers 1` 이라 가능) | **(i)** | scrypt 가 시도당 수십 ms 로 무차별 대입을 늦추고 공개 기간이 4일. (ii) 는 일정이 남으면 추가 후보(동시 호출이 몰리면 scrypt 메모리 사용 — R-6) |
| I | 대화 기록 불러오기 개수 | (i) 최근 50개, 페이지 없음(`limit` 최대 200) (ii) 전부 (iii) 20개 | **(i)** | 시연 계정 대화 15턴 ≈ 30행을 다 덮고, 무한 스크롤을 만들지 않는다 |
| J | `APP_USER_ID` 처리 | (i) 코드·`.env.example` 에서 삭제(서버 `.env` 에 남아도 무시) — U5 에서 (ii) 개발용 기본 사용자로 유지 | **(i)** | 두 출처가 공존하면 격리 판정이 흐려진다(D18 지킬 것 5) |
| K | 기존 데이터 비우기 | (i) 리비전 0003 안에서 `DELETE`(테스트·개발·운영 DB 각각 첫 upgrade 때 한 번) (ii) 별도 사용자 절차(psql) | **(i)** | security §4 "셸 대신 Alembic 파일로 검토" 와 맞고, 운영은 entrypoint 가 자동으로 — 사용자 SSH 명령이 줄어든다. **DB 별 결과**: 테스트 DB(`relationship_test`) — `db_bootstrap` 의 upgrade 때 비워짐, 테스트는 스스로 데이터를 만들어 영향 없음 · 마이그레이션 테스트 전용 DB(`relationship_test_mig`) — 테스트가 매번 base 부터 다시 올림 · 개발 DB — U1 에서 upgrade 할 때 인물 12명 삭제(사용자 결정 4) · 운영 DB — U7 배포 반영 기동 때 시험 데이터 삭제. 한 번 0003 이 적용된 DB 는 다시 비워지지 않는다 |
| L | 로그인 화면 방식 | (i) 관문(`/auth/me` 401 이면 로그인 화면, 해시 라우트 추가 없음) (ii) 정식 라우트 `#/login`·`#/signup` + 보호 경로 리다이렉트 | **(i)** | U6 이유 ①②③ — 구현이 단순하고 테스트가 두 갈래로 끝난다. 원칙5 폐지로 (ii) 도 허용 |
| M | 대기 질문 소유 | (i) `pending_questions.user_id` 컬럼(NOT NULL) (ii) `session_id == chat:<user_id>` 대조만 | **(i)** | 세션 형식에 기대지 않는 직접 조건. F-fbaaae 를 스키마로 닫는다 |
| N | `agent_traces.user_id` | (i) 추가하지 않음(대화 trace 는 `session_id = chat:<user_id>`) (ii) nullable 추가 | **(i)** | trace 를 쓰는 곳이 많아(툴·루프·브리핑·평가) 일정 위험. 원칙9 재생은 session_id 로 충분 |
| O | `users.id` 타입·기존 테이블 FK | (i) Text(uuid4 hex), 기존 `persons`·`push_subscriptions`·`pending_questions` 에 FK 없음 (ii) BIGINT + 기존 컬럼 타입 변경 + FK CASCADE | **(i)** | `persons.user_id` 가 이미 Text 라 컬럼 변경 0. FK 를 걸면 `users` 행 없이 인물을 만드는 기존 테스트 수백 건이 깨진다. 계정 삭제가 범위 밖이라 CASCADE 불필요. Text 라서 U3a 도우미가 `"local"` 을 id 로 하는 사용자 행을 넣을 수 있다 |
| P | 같은 브라우저 푸시 endpoint | (i) 마지막 구독 계정 하나에만(다른 계정 행 삭제) + 로그아웃 시 그 endpoint 행 삭제 (ii) 그대로(계정마다 행) | **(i)** | (ii) 면 A 로그아웃 뒤 B 가 쓰는 브라우저에 A 의 브리핑 알림이 온다 — 시연 노트북에서 실제로 일어난다 |
| Q | 시연 계정 데이터 준비 | (i) 배포 뒤 시연 계정으로 실제 대화를 넣어 쌓기 (ii) 시드 스크립트(DB 직접 INSERT) | **(i)** | "데이터가 들어 있으면 어떻게 해 주는지" 를 제품 파이프라인으로 보인다. (ii) 는 실패 시 예비안 |
| R | 기록에 무엇을 저장 | (i) role(user/assistant)·text·`question_id`·시각, 칩 답은 user 행으로 답 문자열 (ii) `ChatOut` 전체 JSON | **(i)** | 화면 재구성에 충분하고 저장 최소화(security §5). 칩 상태는 `/questions/pending` 이 원천 |
| S | 계정 대화 `session_id` 형식 | (i) `chat:<user_id>` (ii) `users.chat_session_id` 컬럼(uuid) | **(i)** | 컬럼 0. 서버가 만드는 id 라 형식 검사(`resolve_session_id`, 이 패키지에서 제거)를 거치지 않고, 이미 `briefing-scheduler:<uuid>` 처럼 `:` 를 쓰는 서버 생성 id 선례가 있다(R-2 ①). trace 로 계정 추적 가능(결정 N) |
| T | 상태 변경 요청의 Origin 검사(F-7 ③) | (i) POST·PUT·PATCH·DELETE 에 `Origin` 이 있고 그 호스트가 `X-Forwarded-Host`(있으면, 쉼표면 첫 값)·`Host` 와 다르면 403 `bad_origin`, `Origin` 없으면 통과, 비교는 소문자·기본 포트 제거(R2-1 ①) — 앱 전역 한 곳 (ii) 넣지 않고 리스크로 수용 (iii) CSRF 토큰 | **(i)** | 같은 사이트(`*.sslip.io`) 공격자가 본문 없는 상태 변경(`/auth/logout`, 본문 선택인 `/briefings/run`)을 유발하는 경로를 막는다. 코드 한 곳·테스트 하나로 끝나고 새 비밀 값이 없다. `Origin` 없는 요청(curl·테스트)은 브라우저 교차 요청이 아니라 통과. 개발 프록시는 `xfwd`(사실 14) |
| U | 스케줄러 대상 0명일 때의 `ToolContext.user_id`(N-4) | (i) 빈 문자열 `""` 표식으로 `run_briefings` 1회 — 행 `session_id` 는 기존 `briefing:<uuid>` (ii) `run_briefings` 를 거치지 않고 trace 를 직접 씀 (iii) 아무것도 남기지 않음 | **(i)** | `users.id` 는 uuid4 hex·아이디는 3자 이상이라 `""` 와 겹치는 계정이 없어 어떤 일정도 선택되지 않는다. 기존 테스트 4건(`test_briefing_scheduler.py:202-206`·`test_push_wiring.py:308-345`)이 "일정이 없어도 `run_briefings` 1회" 에 기대므로 (ii) 는 그 4건을 깨고, (iii) 은 P9 S13 생존 신호를 없앤다. 바뀌는 기존 단언은 `test_push_wiring.py:344` 하나 |

## 기획서 원칙과 부딪히는 곳

- **원칙5**: 원문 "화면 3개 고정" 은 CR-006 으로 폐지됐다(사용자 2026-11-15). 이 패키지는 로그인·가입 화면 1개(관문)를 더한다 — 근거는 시연 (가). 채팅·인물·브리핑 핵심 화면은 그대로. 하네스 `frontend-agent.md` 25행은 기준 해시 `5c0f26d` 에서 메인이 처리했다.
- **원칙7**: 채팅방 목록은 만들지 않는다(제외 목록에 추가됨). 계정은 사용자 단위이며 인물 간 관계를 저장하지 않는다. 고민 상담과 무관.
- **원칙9**: 로그인·가입·기록 조회는 판정이 아니라 trace 대상이 아니다. 대화 턴의 trace 는 그대로 남고 `session_id` 로 계정별 판단 흐름을 재생한다. 스케줄러는 사용자마다 `run_briefings` 의 trace, 대상 0명이면 표식 `user_id=""` 로 `run_briefings` 1회 → `briefing_run` 1행(F-6·N-4 확정, 결정 U — 기존 생존 신호 유지).
- **원칙1~4**: 무변경. 후보 검색·툴이 계정 안으로 좁혀져 있어 계정 간 오병합 경로가 없다(U3b 격리 테스트 R-4 ② 가 API 층에서 박는다).
- **원칙8**: 평가 러너의 `ToolContext` 는 같은 값을 명시해 결과 불변(U3a). 시연 데이터는 평가와 분리.
- **security §5 "전체 대화 이력 저장 금지"** 와 대화 기록 저장 — CR-006 에서 "context 에는 넣지 않고, `chat_messages` 에 계정 소유로만" 으로 개정했다.

## 리스크 · 미결

- **[일정] 11-17 저녁까지**: 백엔드 U1→U2→U3a→U3b 직렬 뒤 U4∥U5, 가장 큰 덩어리는 U3a 의 기존 테스트 이관(사실 9)인데 동작 불변이라 리뷰가 가볍고, 계약 변경은 U3b 에 모였다(R-9). U6 은 U2 뒤 동시. 판단 시점: 11-16 밤까지 U3b 미커밋이면 축소 1·4(R-13).
- **[운영 DB 마이그레이션]** 배포 반영 기동이 0003 을 돌려 **운영 데이터를 지운다**(되돌릴 수 없음). 사용자 결정 4 대로지만, 반영 직전에 한 번 더 알리고 원하면 `pg_dump` 1회. 0003 이 실패하면 backend 컨테이너가 죽고(D17 4) 화면은 뜨지만 API 가 502 — 이때(**0003 이 적용되지 않았을 때만**) 되돌리기는 직전 해시 checkout + `up -d --build`(`alembic current` 가 `0002` 인지 먼저 확인, 트랜잭션 DDL 이라 보통 전부 롤백). **0003 이 적용된 뒤에는 옛 해시로 되돌릴 수 없다**(옛 코드의 entrypoint `alembic upgrade head` 가 모르는 리비전을 만나 backend 가 뜨지 않는다) — 반영 뒤 문제(예: 브라우저 POST 403)는 **앞으로 고쳐 다시 올리는 길뿐**이다. 그래서 U7 의 Caddy 경유 Origin 스모크와 로컬 브라우저 점검이 반영 전 필수다(R2-1 ③). 승격 전 dev2 해시를 올리는 것은 수용 기준 9번 때문에 불가피 — U7 의존(R-7)이 관문이다.
- **[OpenAI 월 한도 소진(R-6)]** 누구나 가입(G)·시도 제한 없음(H) 상태의 현실적 실패는 침해가 아니라 **평가 당일 전에 OpenAI 월 한도 $10 가 소진되는 것**이다. 소진되면 채팅이 루프 오류 답으로 바뀐다. 사용자 할 일에 "11-17 저녁·11-18 아침 OpenAI 사용량 확인" 을 넣었다. 인증 없는 가입·로그인이 동시에 몰리면 scrypt(호출당 약 16 MB)로 t4g 메모리를 쓴다 — 결정 H(ii) 는 일정이 남으면.
- **[같은 사이트 공격(F-7)]** `*.sslip.io` 는 같은 사이트라 `SameSite=Lax` 가 막지 못한다 → JSON 본문 요구(테스트로 박음)·Origin 검사(결정 T)·`__Host-` 쿠키 이름(R-5)으로 막는다. 남는 것: `Origin` 헤더를 보내지 않는 오래된 브라우저 — 공개 4일·시연용이라 수용.
- **[Origin 검사와 개발 프록시]** Vite 프록시 `changeOrigin: true` 가 `Host` 를 바꾼다(사실 14) → U6 의 `xfwd: true` 가 빠지면 로컬 개발에서 모든 POST 가 403. U7 로컬 브라우저 점검에 포함.
- **[쿠키 ↔ 서비스 워커·푸시]** 서비스 워커가 `/api` 응답을 캐시하면 다른 계정의 응답이 보일 수 있다 — P8 결정 I "캐시 없음" 이라 지금은 해당 없음으로 보지만 U6 에서 `sw.js` 의 fetch 처리 유무를 확인해 03-log 에. 알림 클릭은 해시 주소만 열어 쿠키와 무관(로그아웃 상태면 관문이 먼저 뜬다). 같은 브라우저 두 계정의 알림 섞임은 결정 P 로 막는다.
- **[Secure 쿠키와 로컬·테스트]** `Secure` 쿠키는 `http://testserver`(TestClient)·Safari 의 `http://localhost` 에서 다시 보내지지 않을 수 있다 → 테스트는 `https://testserver` 또는 설정 끔, 로컬 개발은 `AUTH_COOKIE_SECURE=0`(이때 이름도 `rel_session` — `__Host-` 는 Secure 필수). 운영은 HTTPS 라 문제없다.
- **[쿠키 경로]** Caddy 가 접두를 떼므로 백엔드는 `/auth/login` 을 보지만 브라우저는 `/api/auth/login` 에서 받는다 — `Path=/` 를 명시하지 않으면 쿠키가 `/api/auth` 아래에만 실린다(U2 테스트로 박음, `__Host-` 조건이기도 하다).
- **[스케줄러 0명]** F-6·N-4 로 확정 — 표식 `user_id=""` 로 `run_briefings` 1회(결정 U), `briefing_run` 1행 유지. P9 S13 판정 문장은 바꾸지 않아도 된다.
- **[읽기 전용 판정의 빈칸]** `tests/helpers_read_api.py:36-46` `_COUNTED_MODELS` 는 9모델 고정 목록이라 읽기 API "쓰기 0" 판정이 새 테이블(`users`·`auth_sessions`·`chat_messages`)을 세지 않는다 — 기존 테스트는 깨지지 않는다(사실 9). `GET /chat/history` 의 쓰기 0 은 U4 테스트가 `chat_messages` 행 수로 따로 본다. 목록 확장은 이 패키지 범위 밖(권고 인계).
- **[평가 러너]** `scripts/run_pilot_eval.py` 를 건드린다(값 명시뿐, U3a). P4/P4b 재현성에 영향이 없음을 `tests/test_eval_runner.py`·`test_baseline_*` 통과로 보인다.
- **[P2b 경계]** 인물 완전 삭제(P2b)는 `chat_messages` 속 그 인물 언급을 지우지 않는다 — P2b 재개 때 결정(security §5 에 기록).
- **[만료 세션 행]** 정리 작업을 두지 않는다 — 공개 4일·몇 명 규모라 행 수가 작다. 장기 운영이면 정리 작업 필요(인계).
- **[P9 연결(R-1)]** P9 04-review 는 이 패키지의 배포 반영 뒤 함께 닫는다. 그때 P9 수용 기준 "`git diff --stat -- app web/src alembic` 빈 출력" 의 범위는 **P9 커밋 구간(P9 기준 `4a4d8cb`..`7830f6c`)으로 고정**해야 한다 — 안 그러면 P9b 의 코드 변경이 P9 판정에 잡힌다. P9 의 사용자 Traceback 0 보고(2026-11-15)는 반영 전 상태의 증거이므로, 반영 뒤 U7 에서 다시 받는다.
- **[하네스(R-12)]** `verify-plan.sh` 62·68행이 `P5b-…`·`P9b-…` 처럼 숫자 뒤 글자가 있는 id 를 다루지 못해 "의존 완료"·"P4 게이트" 검사가 빠진다 — 이번에는 verifier 가 손으로 확인. 하네스 FIX 후보(이 패키지 범위 밖).
- **[달력(P9c)]** 이 패키지가 끝나야 시작할 수 있다(한 번에 활성 하나). 평가 전에 못 들어가면 배포본은 로그인만 반영된 상태(브리핑은 목록 보기)로 시연한다.

## 사용자만 할 수 있는 일 · 에이전트가 검증할 수 없는 것 (메인 세션이 모아 전한다)

**사용자만 할 수 있는 일**
1. 서버 SSH 에서 배포 반영: `git fetch && git checkout <해시>` → `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build` → `ps`·`logs --tail=200 backend` 결과를 메인에 붙여 주기(Traceback 수·0003 적용 줄). 이 기동이 운영 데이터를 비운다. **0003 이 적용된 뒤에는 옛 해시로 되돌릴 수 없다 — 문제는 앞으로 고쳐 다시 올린다**(R2-1 ③).
2. (선택) 반영 전 운영 DB `pg_dump` 1회 — 결정 4 로 비우기로 했으므로 필수 아님.
3. 서버 `.env` 수정은 **필요 없다**(결정 D (i)). 남아 있는 `APP_USER_ID` 줄은 지우지 않아도 된다. 결정 D 를 (ii) 서명 쿠키로 바꾸면 그때만 `SESSION_SECRET` 을 사용자가 넣는다.
4. 배포 URL 에서 브라우저로 가입·로그인·로그아웃, 시연 계정 대화 입력과 확인 칩 판단(U8), 알림 권한 창 허용(푸시를 시연에 쓸 때).
5. 시연 계정 아이디·비밀번호 정하기와 보관(저장소·증거에 남기지 않는다).
6. **11-17 저녁·11-18 아침에 OpenAI 대시보드 사용량 확인**(월 한도 $10 소진 대비, R-6).
7. U1 에서 로컬 개발 DB 인물 12명이 지워진다는 것을 실행 직전에 한 번 더 확인(결정 4 — 이미 결정, 알림).
8. (해당 시) 범위 축소 3 을 쓸지 — 수용 기준 6번 변경이라 사용자 결정(R-11 ②).

**에이전트가 검증할 수 없는 것**
1. 배포 URL 의 POST(가입·로그인·채팅) — security §4(로컬 밖 `curl -d` 금지). 에이전트는 본문 없는 GET 으로 401·health 만 본다.
2. 실제 브라우저의 쿠키 동작(`__Host-` 접두·Secure·SameSite·HTTPS)과 Origin 헤더, 로그인 화면 모양 — Vitest·로컬 점검으로 근사, 최종은 사용자 화면.
3. 실제 기기 푸시 수신과 같은 브라우저 두 계정 전환 시 알림 섞임 여부 — 단위 테스트로 규칙만, 실수신은 사용자.
4. 서버 컨테이너 로그·`alembic current`(SSH 안) — 사용자가 붙여 준 출력으로만.
5. 시연 계정 데이터의 내용이 시연에 적절한지(인물·사건 선택) — 사용자 판단.

## 읽은 카드

- `docs/wiki/changes/CR-006.md`(이 계획과 함께 작성) · `CR-005.md` 전문(형식·결정 D(d))
- `docs/wiki/decisions/D17-vercel-deploy.md` 전문 · `decisions/README.md` · `D18-login-user-isolation.md`(작성)
- `docs/wiki/specs/S3.1-schema-v2.md`·`S3.4-ask-user-protocol.md`·`S3.6-briefing-push.md` 전문
- `docs/wiki/security.md` 전문 · `docs/backlog.md` 전문 · `docs/wiki/INDEX.md` 전문 · `docs/wiki/CURRENT.md` 머리·메모 · `docs/wiki/review-index.md` 표
- `docs/wiki/packages/P9b-auth/02-plan-verify.md` 전문(1차 보류 소견 — 개정 1 의 근거)
- `docs/wiki/packages/P9-infra/01-plan.md` 1~232·312~345행(형식·판정 표·리스크)
- `docs/wiki/templates/plan.md`·`change-request.md` · `.claude/skills/devlog/SKILL.md` 28~97행 · `.claude/scripts/verify-plan.sh` grep(45행 단위 정규식 `^- \[[ x]\] U[0-9]+` — `U3a`·`U3b` 도 읽힌다)
- `docs/wiki/registry.md`(grep `auth|login|password|users|chat_messages|session.ts|apiFetch|routes.ts|AppShell`)
- `.claude/gitlog.md`(2026-11-15 19:50, HEAD `7830f6c`)
- 코드: `app/db/models.py` 전문 · `app/settings.py` 495~518 · `app/briefing/scheduler.py` 80~119 · `app/api/read.py` 260~349 · `app/api/routes.py` 라우트 데코레이터 grep·486~498 · `app/api/schemas.py` 필드 grep · grep `user_id|session_id`(`app/api/read.py`·`deps.py`·`briefing/select.py`·`run.py`·`scheduler.py`·`tools/questions.py`·`context.py`) · `web/src/routes.ts` 전문 · `web/src/api/client.ts` grep · `web/vite.config.ts` grep(`changeOrigin`) · Glob `web/src/**` · grep `tests/` (`TestClient(`·`X-Session-Id`·`APP_USER_ID` 개수, `ToolContext(` 개수) · `tests/db_bootstrap.py` grep · Glob `alembic/versions` · grep `원칙5|화면 3개|3화면` 저장소 전체
- 열지 않은 것: `web/src/screens/ChatScreen.tsx`·`AppShell.tsx`·`push.ts`·`sw.js`·`web/e2e/fixtures.ts` 본문(U6 에서 frontend-agent 가 확인) · `app/push/subscriptions.py` 본문(U5) · `app/tools/questions.py` 본문(행 번호는 grep·verifier 대조) · `scripts/schema_check.py`(존재·단언 확인은 U1)

## 개정 이력

- **개정 1(2026-11-15, verifier 02-plan-verify 1차 보류 반영)**

| 소견 | 반영한 곳 |
|---|---|
| F-1 | U1 에 `ask_user` 의 `user_id=ctx.user_id` 한 줄과 변이 V1-3b · 고치는 파일 표 `questions.py` U1/U3b 분리 · 사실 3 |
| F-2 | (b) 안 — U3b 는 요청 경로만, `app_user_id()` 삭제·`.env.example` 줄 삭제·판정 #4 는 U5 · 고치는 파일 표 · 판정 #4 단위 |
| F-3 | API 계약 표 로그아웃 401 · U2 로그아웃 `current_user`·테스트·변이 V2-10 · U3b 열거 테스트 예외에서 로그아웃 제거 · U6 로그아웃 401 처리 · 판정 #2 |
| F-4 | 판정 #4 를 `-- bash <SCR>/u5-no-fixed-user.sh` 로 · 판정 방법 머리 문장 · 사실 1 에 주석 위치 목록 · U3b·U5 정리 목록 |
| F-5 | U3b "바꿔도 되는 단언" 닫힌 목록 3개 · U3a 도우미(`"local"` id 사용자 행 + 쿠키) · 사실 9 · 결정 O 이유 |
| F-6 | U5 대상 0명 → 사용자 없는 `briefing_run` 1행 확정 + 테스트·변이 V5-5 · 창은 `select.py` `lead_hours` 상수 + 테스트·변이 V5-6 · 사실 7 · 원칙9 절 · 리스크 |
| F-7 | 사실 13·14 · 결정 F 이유를 사실대로 · U2 text/plain·폼 본문 테스트·변이 V2-9 · Origin 검사(`app/auth/origin.py`, API 계약 표 공통 행, 테스트 `test_auth_origin.py`, 변이 V2-7, 결정 T, 판정 #13) · U6 `xfwd` · 리스크 2줄 |
| R-1 | 6행 관련 문장 · 리스크 [P9 연결] 에 P9 diff 범위 고정 |
| R-2 | 사실 4(형식 정규식) · 사실 5(261행·id 로 읽는 곳 4) · U3b 소유 조건 거는 곳 2·안 거는 곳 2 · 결정 S 이유 정정 |
| R-3 | 사실 12 · U6 204 무본문·테스트·변이 V6-4 |
| R-4 | U3b 격리 테스트 ① 재개 루프 호출 0 ② 툴 경로 `PersonNotFound` · 열거 테스트의 `/push-dev/` 처리 · 사실 6 |
| R-5 | 결정 F 쿠키 이름 `__Host-rel_session`/`rel_session` · U2 구현·테스트·변이 V2-8 |
| R-6 | 리스크 [OpenAI 월 한도 소진] · 사용자 할 일 6 · 결정 C·G·H 이유 |
| R-7 | U7 의존(단위별 verifier 리뷰 + 반영 해시 전체 pytest) · 리스크 |
| R-8 | 9행 FIX-036 을 U1 전에 · 판정 #12 기대 문장 |
| R-9 | U3 → U3a(테스트 이관, 동작 불변, 변이 V3a-1) + U3b(계약 변경) |
| R-10 | U1 ⑤⑦ 전용 DB `relationship_test_mig`·원시 SQL·`dbtest` 표식·skip 0 · 결정 K |
| R-11 | U6 E2E 사실(CI 가 돈다)·`fixtures.ts` `/auth/me` 목 · 축소 2 최소 갱신 · 축소 3 사용자 결정 · 사용자 할 일 8 |
| R-12 | 리스크 [하네스] 한 줄 |
| R-13 | 10행 판단 시점 · 축소 절 머리 |

- **개정 2(2026-11-15, verifier 02-plan-verify 2차 보류 반영)** — 메인이 고친 8·9행(기준 `08c1b49`, 기준선 2261)과 U7 "Caddy 경유 Origin 스모크" 항목은 유지하고 그 위에 덧붙였다.

| 소견 | 반영한 곳 |
|---|---|
| N-1 | 사실 9 에 스키마 단언·`PendingQuestion(` 직접 생성 목록 · 고치는 파일 표 `scripts/schema_check.py:237` 6→8 행 + "U1 이 고치는 기존 테스트(닫힌 목록)" 행 · U1 판정 뒤 닫힌 목록 ①~④ + "S3.1 보충 반영이지 단언 의미 변경이 아니다" · grep 추가분: `NULLABLE_COLUMNS`(232~239)·`EXPECTED_INDEXES`/309행 `total == 10`·CHECK 총수(194~201) |
| N-2 | 사실 9 에 `app/` 밖 참조 목록 · ① U3a 리터럴화(`test_push_wiring.py`·`test_answer_concurrency.py`) + 판정 `u3a-tests-fixed-user.sh` + V3a-1 을 기본값·함수 둘 다로 ② U5 `tests/test_settings.py` 삭제(−2)·9행·판정 #12 ③ U3a 도우미 ④ + U3b 단언 아님 목록에 `test_commit_boundaries.py:81,181,293` · grep 추가분: `.github/workflows/tests.yml:176`(U5 삭제)·`docs/user-setup/13-user-todo-deploy.md:41,46`(U7)·주석 2곳(`test_push_subscriptions.py:90`·`test_api_read_briefings_e2e.py:185`) · U5 판정 `u5-outside-app.sh` |
| N-3 | U3b 판정: `grep -rnE` + 스크립트, "기대 exit 1, exit 2 는 실패" · `u3b-ctx-default` 명령 형태 · 계획 안 grep 판정 전수 점검(아래 "grep 판정 점검") |
| N-4 | U5: 0명 → `user_id=""` ctx 로 `run_briefings` 1회, 행 `session_id` 는 `briefing:<uuid>`(정정) · `test_push_wiring.py:344` 기대값 변경을 U5 단언으로 · 테스트·변이 V5-5·V5-5b · 결정 표 행 U · 리스크 |
| R2-1 | ① U2 비교 규칙(소문자·기본 포트·쉼표 첫 값) + origin 테스트 3건 + 결정 T ② U7 Caddy 스모크에 `X-Forwarded-Host` 위조 건 ③ "0003 적용 뒤 옛 해시로 되돌릴 수 없다 — 앞으로 고쳐 다시 올린다" 를 리스크·U7(스모크·배포 반영)·사용자 할 일 1 에 |
| R2-2 | ① U3b 닫힌 목록 ③ 에 `test_api_questions_pending.py:136` + 데이터 준비·조회 조건의 세션 id 교체는 단언 변경 아님 ② U3a 도우미 ④ 커밋형(커밋·정리, `username` UNIQUE) ③ `logged_in_client(app, session_or_factory, …)` + 쿠키 이름은 설정 함수에서 |
| R2-3 | U5 창 상수 `app/settings.py:218` `BRIEFING_LEAD_HOURS` · 호출 시점에 모듈 전역을 읽어 사용자 목록 질의와 `run_briefings(lead_hours=…)` 양쪽에 · V5-6 |
| R2-4 | 9행을 현재 값(2261·0 failed)만으로 · 판정 #12 기대 문장(−2 포함) |

**grep 판정 점검(N-3 종류 — 계획 안 모든 grep 명령, 2026-11-15)**: ① 판정 #4 `u5-no-fixed-user.sh` — `grep -rnE`, 스크립트 ✔ ② U3b `u3b-request-path.sh` — `-rnE`, 스크립트(개정 2 에서 고침) ✔ ③ `u3b-ctx-default` — 단일 파일·따옴표 없는 패턴(`default_factory=app_user_id`)이라 래퍼 그대로 ✔ ④ U3a `u3a-tests-fixed-user.sh` — `-rnE`, 스크립트 ✔ ⑤ U5 `u5-outside-app.sh` — `-rnE`, 스크립트 ✔ ⑥ 판정 #1 `-k plaintext` 는 pytest 인자(grep 아님) ✔ ⑦ #10 `u7-401.sh`·`u7-root.sh` — `curl -w '%{http_code}'` 는 스크립트 ✔. 모든 grep 판정은 "기대 exit 1(일치 없음) 또는 목록 대조 exit 0, exit 2 는 실패" 로 읽는다.
