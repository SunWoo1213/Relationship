# P9b-auth · 계획 검증 (02-plan-verify)

대상: 01-plan.md (개정 2) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-15 (3차)

기준: HEAD `08c1b49`(dev2). **3차 검증**이다.
- 1차(HEAD `5c0f26d`) 결과 보류 — [필수] F-1~F-7 · [권고] R-1~R-13 → 개정 1.
- 2차(HEAD `08c1b49`) 결과 보류 — [필수] N-1~N-4 · [권고] R2-1~R2-4 → 개정 2.
- 3차(이 문서) — 개정 2 를 architect 의 "반영했다" 보고가 아니라 계획 본문과 코드·테스트로 다시 대조했다.

3차에서 본 것 — `01-plan.md` 1~30행·60~100행·101~180행·193~200행·220~246행·278행·289~293행·341~381행(개정된 곳 전부) · 2차에서 읽은 카드(`decisions/D18-login-user-isolation.md`, `specs/S3.1`·`S3.4`·`S3.6`, `security.md`)는 그 뒤 바뀌지 않았다(`git status --short` 에 카드 변경 없음) · 전수 검색: 스키마·리비전 단언(`tests/test_schema_models.py` 150~320행 전부, `tests/test_schema_check.py`, `scripts/schema_check.py` 숫자 비교 줄, 저장소 전체 `0002|alembic_revision`), `app_user_id|APP_USER_ID`(위키 밖 저장소 전체), `X-Session-Id`·`invalid_session_id`·`session_id` 단언(`tests/` 전체), `PendingQuestion(`(`app`·`scripts`·`evaluation`·`tests`), 한 테스트 안에서 세션 id 를 둘 이상 쓰는 곳(구문 분석 스크립트, 0건), `app/api/deps.py` 조립 함수를 직접 부르는 테스트 · N-4 대조: `app/briefing/run.py` 168~335, `app/briefing/scheduler.py` 전문, `app/push/notifier.py:252-270`, `tests/test_push_wiring.py` 159~174·296~400, `tests/test_briefing_scheduler.py` 153~206.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P9b-auth verify-plan -- bash .claude/scripts/verify-plan.sh P9b-auth`
저장: `evidence/20261115-2051-verify-plan.txt` (이 문서를 3차 판정으로 갱신한 뒤 실행, exit 0). 이전 실행: 1차 `evidence/20261115-2021-verify-plan.txt` · 2차 `evidence/20261115-2039-verify-plan.txt`.
```
== verify-plan P9b-auth  (2026-11-15 20:51) ==
PASS  존재: docs/wiki/packages/P9b-auth/01-plan.md
PASS  존재: docs/wiki/packages/P9b-auth/02-plan-verify.md
PASS  카드 존재: D16
PASS  카드 존재: D18
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R14
PASS  Refs 있음: - [ ] U1 **[backend-agent] 스키마·리비전 0003 — `users`·`auth_sess
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인증 코어 — 비밀번호 해시·세션 토큰·쿠키 이름 규칙·`c
PASS  Refs 있음: - [ ] U3a **[backend-agent] 기존 테스트 이관(동작 불변) — `ToolContext(
PASS  Refs 있음: - [ ] U3b **[backend-agent] 모든 API 를 로그인 사용자 기준으로 — 401·남의 자
PASS  Refs 있음: - [ ] U4 **[backend-agent] 계정당 채팅방 하나 — 대화 기록 저장과 `GET /chat
PASS  Refs 있음: - [ ] U5 **[backend-agent] 스케줄러·푸시 사용자별 — 사용자마다 브리핑 루프(0명이면 
PASS  Refs 있음: - [ ] U6 **[frontend-agent] 로그인·가입 화면(관문), 로그아웃, 대화 기록 불러오기,
PASS  Refs 있음: - [ ] U7 **[메인 세션 + 사용자] 문서·로컬 통합 스모크·배포 반영·바깥 스모크** / Refs:
PASS  Refs 있음: - [ ] U8 **[사용자 + 메인 세션] 시연 계정 데이터 쌓기와 시연 두 갈래 리허설(배포 URL)**
PASS  backlog 일치: 가입·로그인·로그아웃·내 정보 API 가 동작하고 비밀번호는 해시로만 저장된다 + `/health`·`/au
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: alembic/versions/0003_auth_users.py
PASS  registry 중복 없음: app/auth/__init__.py
PASS  registry 중복 없음: app/auth/passwords.py
PASS  registry 중복 없음: app/auth/sessions.py
PASS  registry 중복 없음: app/auth/deps.py
PASS  registry 중복 없음: app/auth/routes.py
PASS  registry 중복 없음: app/auth/origin.py
PASS  registry 중복 없음: app/chat/history.py
PASS  registry 중복 없음: tests/test_migration_0003.py
PASS  registry 중복 없음: tests/test_auth_passwords.py
PASS  registry 중복 없음: tests/test_auth_api.py
PASS  registry 중복 없음: tests/test_auth_origin.py
PASS  registry 중복 없음: tests/auth_helpers.py
PASS  registry 중복 없음: tests/test_auth_required_routes.py
PASS  registry 중복 없음: tests/test_user_isolation.py
PASS  registry 중복 없음: tests/test_chat_history.py
PASS  registry 중복 없음: tests/test_briefing_scheduler_users.py
PASS  registry 중복 없음: tests/test_push_endpoint_owner.py
PASS  registry 중복 없음: web/src/screens/AuthScreen.tsx
PASS  registry 중복 없음: web/src/auth.ts
PASS  registry 중복 없음: web/src/__tests__/auth.test.tsx
PASS  registry 중복 없음: docs/wiki/packages/P9b-auth/tests.md
PASS  registry 중복 없음: 03-log.md
== 결과: FAIL=0 WARN=0 ==
```
기계 검증이 **보지 못한 것**(1차 R-12, 그대로 열려 있음): `verify-plan.sh` 62행 정규식이 `P5b-query-turn` 을 잡지 못해 "의존 완료" 줄이 `P8-frontend` 하나뿐이고, 68행 `sed` 가 `P9b-auth` 에서 숫자를 뽑지 못해 P4 게이트 줄이 출력에 없다. 손 확인 — `packages/P5b-query-turn/04-review.md`·`packages/P4b-er-redesign/04-review.md`·`packages/P8-frontend/04-review.md` 모두 "결과: 완료".

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, **채팅방 목록(여러 대화방)** — 계정마다 채팅방은 하나다." ↔ 01-plan 50행 "**채팅방 목록(여러 대화방)** — CR-006 · 원칙7 제외", 185행 `AppShell` 은 "<아이디> · 로그아웃" 한 줄뿐, 283행 "계정은 사용자 단위이며 인물 간 관계를 저장하지 않는다". 53행 "**CSRF 토큰** — 같은 출처 JSON API + Origin 검사(결정 T)로 갈음". 개정 2 가 더한 것(결정 U 표식 `user_id`, 기존 테스트 닫힌 목록)은 범위를 넓히지 않는다. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙5 — `CLAUDE.md` "화면 수를 고정하지 않는다 — 필요한 화면(로그인·가입 등)은 계획에서 근거와 함께 더한다" ↔ 182행 관문 1개 + 이유. 원칙1~4 — 55행 "툴 7종·ER 4단계·임계치·확신도·평가 산출물 변경 — 원칙1~4·8. 값의 출처만 바뀐다", 공통 회귀 244행 `git diff --stat <기준>..HEAD -- app/er evaluation reports data` 빈 출력. 원칙8 — 145행 `scripts/run_pilot_eval.py` 는 같은 값 명시뿐, 125행 "이 값들은 S3.1 보충(카드)에서 나오므로 단언 의미 변경이 아니라 카드 반영이다". 원칙9 — 135행 "`/auth/*` 는 `agent_traces` 를 쓰지 않는다(판정이 아님)", 175행 대상 0명이어도 `run_briefings` 가 `briefing_run` 1행을 기존 형식으로 남긴다(실물 `app/briefing/run.py:319-331`). |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `decisions/D18-login-user-isolation.md` 지킬 것 4 "`/health`·`/auth/signup`·`/auth/login` 밖의 모든 라우트가 로그인 의존성을 갖는다" ↔ 107행 "**미로그인 401 `unauthenticated`**(… 예외는 … 3개뿐)", 159행 "**`/auth/logout` 은 예외가 아니다**". 지킬 것 5 "요청 경로에서 `app_user_id()`·`APP_USER_ID` 참조 0, `ToolContext.user_id` 기본값 0(`grep` 판정)" ↔ 161행 `grep -rnE … app/api app/tools app/auth`(기대 exit 1), 판정 #4(225행). 지킬 것 8 "주기 작업은 사용자마다 별도 `ToolContext(user_id=…)` 로 돌고, 한 사용자의 실패가 다른 사용자의 브리핑을 막지 않는다" ↔ 174행 "**사용자 단위 예외 격리**"; 대상 0명일 때의 표식 `""` 실행(175행)은 어느 계정의 일정도 고르지 않으므로(`app/briefing/select.py:76` `Person.user_id == ctx.user_id`) 이 항목과 부딪히지 않는다. 지킬 것 1·2·3·6·7·9 는 2차와 같은 문장(129·130·131·135·153·160행, 판정 #11). |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.1-schema-v2.md` 27~29행 "users(id, username, password_hash, created_at) … auth_sessions(id, user_id, token_hash, created_at, expires_at) … chat_messages(id, user_id, role, content, question_id, created_at)" ↔ 120행 컬럼 집합 동일. 32행 "기존 테이블의 … `user_id` 는 `users.id` 값을 담되 **FK 는 두지 않는다**" ↔ 120행, 125행 `EXPECTED_FKS` 6→8(새 테이블 2개만). 34행 "0003 은 기존 사용자 데이터(…)를 **비운다**" ↔ 122행. `S3.4-ask-user-protocol.md` 14행 "로그인 사용자와 `user_id` 가 같을 때만 받고, 아니면 404(행·`answer` 변화 0)" ↔ 154행. `S3.6-briefing-push.md` 8행 "대상은 창 안에 미브리핑 일정이 있는 사용자" · 12행 "같은 endpoint 는 마지막으로 구독한 계정 하나에만" ↔ 174·176행. 툴 시그니처·임계치·`ask_user` 비동기는 건드리지 않는다(55행). |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 99행 "의존: P9-infra U4(배포본 기동 `7830f6c`, 04-review 는 P9b 반영 뒤 함께) · P8 · P5b" ↔ 01-plan 5·6행. `packages/P8-frontend/04-review.md`·`P5b-query-turn/04-review.md`·`P4b-er-redesign/04-review.md` "결과: 완료". `CURRENT.md` 3행 "active: none". 단위 순서(117행 "U1 → U2 → U3a → U3b → (U4 ∥ U5)")는 §3 "단위별 통과 가능성" 에서 커밋 시점마다 따졌다. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 99행 "수용기준: 가입·로그인·로그아웃·내 정보 API 가 동작하고 … + pytest 전체 통과 skip 0" ↔ 01-plan 250행(`verify-plan` "PASS backlog 일치"). 판정 #12(233행)가 "통과 수 = 기준선 2261 + 새 테스트 − (U5 이후) `tests/test_settings.py` 2건" 으로 고쳐져 수 변화가 설명된다. 계획 안 grep 판정 5개는 모두 `-rnE`·스크립트 방식이고 "exit 2 는 실패" 가 붙었다(161·148·177행, 판정 #4). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan 119·128·143·151·164·172·181·193·201행 U1·U2·U3a·U3b·U4~U8 아홉 단위 모두 "/ Refs: P9b-auth D18 …"(`verify-plan` "PASS Refs 있음" 9줄). |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | §4 "셸에서 `DROP`/`TRUNCATE` 금지 → Alembic 마이그레이션 파일로 작성해 검토" ↔ 122행(리비전 안 `DELETE` 4문), 123행(전용 DB 는 만들기만 하고 지우지 않는다). §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T` …) 금지" ↔ 195행 Caddy 스모크는 로컬 compose, 198행 "바깥 스모크(메인, 본문 없는 GET 만 — security §4)". §1 "(CR-006 · D18) 사용자 비밀번호·세션 토큰·쿠키 값은 로그·`agent_traces`·응답 본문·예외 메시지·증거 파일에 남기지 않는다" ↔ 135·196·246행. §5 "대화 기록은 … `chat_messages` 에만 **계정 소유로** 저장하고(다른 계정·로그·trace 로 복사 금지)" ↔ 168행. 263행이 `SameSite=Lax` 를 "보조 방어일 뿐" 으로 적고 주 방어를 JSON 본문 요구 + Origin 검사로 둔다. |

## 3. 소견과 조치

증거 파일: `evidence/20261115-2036-planverify2-u3b-grep-probe.txt`(2차 N-3) · `evidence/20261115-2019-planverify-cmd4-probe.txt`(1차 F-4). 그 밖의 근거는 코드·테스트 파일:줄.

### 이력 — 1차 F-1~F-7, 2차 N-1~N-4 의 3차 판정

| 소견 | 3차 | 근거 |
|---|---|---|
| F-1 U1↔U3 순서 | 해소(2차) | 121행, 변이 V1-3b. |
| F-2 U3↔U5 순서 | 해소 | `app/` 쪽은 2차에 해소, 테스트 쪽(N-2)은 아래. |
| F-3 로그아웃 미로그인 | 해소(2차) | 점검표 3행. |
| F-4 판정 #4 명령 | 해소(2차) | 225행. |
| F-5 U3 단언 닫힌 목록 | 해소 | 157행 — 2차 R2-2 ① 까지 반영. |
| F-6 대상 0명 | 해소 | N-4 아래. |
| F-7 CSRF 근거 | 해소(2차) | 2차 "새로 들어온 것" 대조 그대로 유효. |
| **N-1** U1 스키마 단언 | **해소**(한 줄 누락 → R3-1) | 125행 닫힌 목록 ①~④, 파일 표 78·79행, 124행 판정에 `scripts/schema_check.py` 전부 PASS. architect 가 더했다는 항목을 실물로 확인: `tests/test_schema_models.py` `NULLABLE_COLUMNS` 는 **컬럼 이름 집합**을 전 테이블에서 모아 비교하므로(232~239행) 새 nullable `question_id` 가 깨뜨린다 — 맞다. `EXPECTED_INDEXES`·309행 `total == 10` 은 기대 항목만 세므로 깨지지는 않고 반영 대상 — 계획 서술과 같다. 194~201행 CHECK 총수는 9테이블 고정 목록이라 깨지지 않는다 — 계획 서술과 같다. 212행 `len(found) == 6` 은 `EXPECTED_FKS` 와 함께 깨진다 — 사실 9(23행)에 있다. `scripts/schema_check.py` 의 숫자 비교는 237행(`== 6`)·286행(`>= 10`)·356행(`== 0`)뿐 — 계획과 같다. **목록에 없는 것 1건**: `tests/test_api.py:91`. |
| **N-2** `app_user_id` 테스트 참조 | **해소** | 146행(U3a 리터럴화)·148행 판정·149행 V3a-1·177행(U5 삭제·−2)·9행·233행. 위키 밖 저장소 전체 검색 결과가 사실 9(25행)의 목록과 같다 — `tests/` 6파일, `.github/workflows/tests.yml:176`, `docs/user-setup/11…:58,105`·`13…:41,46`. 계획에 없는 문서 1곳은 R3-3. |
| **N-3** U3b grep | **해소** | 161행 `grep -rnE … app/api app/tools app/auth` + "기대 exit 1, exit 2 는 실패". 재귀 검색에 캐시 파일이 섞이는 점은 R3-2. |
| **N-4** 대상 0명 방법 | **해소** | 아래 "N-4 확정안 대조". |

### N-4 확정안 대조 (175행, 결정 U 278행) — 실물·기존 테스트와 맞다
- `ToolContext` 는 `user_id` 값을 검증하지 않는다(`app/tools/context.py:93-109` — `__post_init__` 없음). `notifier_from_env(session, user_id, now)` 도 값을 그대로 넘길 뿐이다(`app/push/notifier.py:252-270`) → `""` 로 불러도 예외가 없다.
- `run_briefings` 는 `select_due_schedules` 로 `Person.user_id == ctx.user_id` 인 일정만 고른다(`app/briefing/select.py:76`). `persons.user_id` 는 로그인 계정의 `users.id`(uuid4 hex)나 테스트의 `"local"` 류 값이므로 `""` 로는 0건이 선택되고, 실행 끝의 `briefing_run` 행 1개만 남는다(`run.py:319-331`, `session_id` 는 `run.py:183` 이 붙이는 `briefing:<uuid>`) — 계획 174·175행 서술과 같다.
- 기존 테스트 4건: `tests/test_briefing_scheduler.py:202-206` 은 실제 `session_scope()` 로 돌지만 다른 테스트의 데이터는 바깥 트랜잭션에 갇혀 보이지 않으므로 대상 0명 → 가짜 `run_briefings` 1회 → `len(calls) == 2` 가 선다. `tests/test_push_wiring.py:308-345` 3건은 `scheduler_env`(172행 — `session_scope` 를 롤백 세션 하나를 내주는 대역으로 바꿈)에서 일정 없이 돌므로 `""` ctx 로 1회 불리고, 344행은 `== ""` 로 바뀐다(계획이 U5 단언으로 적음). 같은 파일의 끝까지 가는 2건(347~384행)은 `"local"` 인물의 `now+3h` 일정을 넣으므로 사용자 목록에 `"local"` 이 잡혀 지금처럼 돈다 — 계획 174행 "`users` 테이블이 아니라 `persons.user_id` 에서 구하므로" 가 이것을 보장한다.
- 구현 때 지킬 점 하나(계획 174행 "세션을 사용자마다 따로 여는 방식 권장" 과 관련): `scheduler_env` 는 `session_scope()` 를 몇 번 불러도 같은 세션을 내주므로 어느 방식이든 테스트는 선다. 03-log 로 흡수된다.

### 단위별 통과 가능성 (커밋 시점마다 전체 pytest)
- **U1** — 닫힌 목록(125행)으로 스키마 단언·`PendingQuestion(` 6파일이 덮인다(`PendingQuestion(` 은 `app` 1곳 + 테스트 6파일 9곳이 전부, 원시 SQL 삽입 0). **남는 1건: `tests/test_api.py:91`**(R3-1).
- **U2** — 기존 테스트에 닿는 변경 없음(라우트 수·OpenAPI 를 단언하는 테스트 없음, `Origin` 을 보내는 테스트 없음).
- **U3a** — `app/` diff 0. 리터럴화 대상 2파일이 146행에 줄 번호로 있다.
- **U3b** — `X-Session-Id` 를 쓰는 곳 19곳·세션 단언 7곳(`tests/test_api_chat.py:148,210,222,225`, `tests/test_api_chat_query.py:437,440`, `tests/test_api_questions_pending.py:75`)이 모두 닫힌 목록 ①②③(157행) 안이다. 한 테스트 안에서 세션 id 둘로 격리를 가르는 테스트는 0건. `resolve_session_id`·`build_ctx`·`build_chat_ctx`·`get_notifier` 를 직접 부르는 테스트 0건(`load_resume_input` 2곳은 시그니처 불변). `app/` 의 `ToolContext(` 4곳은 모두 `user_id=` 명시.
- **U4** — `chat_messages.user_id` FK 는 U3a 의 로그인 도우미가 만든 `users` 행으로 충족.
- **U5** — N-2·N-4 반영으로 고칠 기존 테스트가 줄 번호까지 있다(`tests/test_settings.py` 삭제, `tests/test_push_wiring.py:344`).
- **U6~U8** — 2차와 같다(순서 결함 없음).

### [필수]
없음.

### [권고] — 구현 중 보고·03-log 로 흡수된다. R3-1 만은 활성화 전에 한 줄 더하기를 권한다

- **R3-1 (U1 닫힌 목록에 1줄)** `tests/test_api.py:91` `assert body["alembic_revision"] == "0002"  # FIX-020 -- 0002 리비전 추가`. 테스트 DB 가 0003 이 되면 **U1 에서 반드시 실패**하고 125행 닫힌 목록에 없어 "목록 밖 테스트가 깨지면 멈추고 보고" 가 걸린다(저장소 전체 `0002|alembic_revision` 검색에서 리비전 문자열을 단언하는 곳은 이 한 줄뿐). 고칠 값이 `"0003"` 하나로 정해져 있어 잘못된 구현으로 이끌지는 않지만, 알고 있는 왕복 1회다 → 125행 ② 뒤에 "`tests/test_api.py:91` `"0002"` → `"0003"`(리비전 반영)" 을 더하거나 U1 위임 프롬프트에 같은 문장을 넣는다. 이 한 줄을 더하는 것은 판정에 영향이 없으므로 재검증 없이 해도 된다.
- **R3-2 (재귀 grep 4개에 캐시 제외)** 시스템 grep 의 `-r` 은 `__pycache__/*.pyc` 도 읽는다. 지금 코드에서 `grep -rnE 'app_user_id|APP_USER_ID' tests scripts evaluation` 은 "Binary file tests/__pycache__/test_settings.cpython-314.pyc matches" 같은 줄을 낸다. U5 에서 `tests/test_settings.py` 를 지워도 그 `.pyc` 는 남으므로 `u5-outside-app.sh`(177행)가 "주석 2곳만" 이 아닌 줄을 내고, `u3b-request-path.sh`(161행)·`u5-no-fixed-user.sh`(225행)도 pytest 를 돌리기 전에 실행하면 옛 `.pyc` 때문에 exit 0 이 된다. 헛통과가 아니라 **헛실패** 쪽이다 → 148·161·177·225행의 재귀 grep 에 `--include='*.py'`(`.github` 를 함께 보는 177행은 `--exclude-dir=__pycache__`)를 붙인다.
- **R3-3 (U7 문서 목록에 1곳)** `docs/reliability.md:101` "이 프로젝트에는 **인증이 없다.** 서버 환경변수 `APP_USER_ID` 한 사람을 전제로 하며 …" 가 이 패키지 뒤 사실과 달라진다. 194행 문서 목록에 더한다(제품 코드·테스트와 무관).
- **R3-4 (U3a 판정 문장)** 148행 "일치 줄이 … 뿐" 목록에 `tests/test_answer_concurrency.py` 가 없는 것은 146행이 그 파일의 docstring 언급(71·73·127행)까지 고치기로 했기 때문이다 — 맞다. 다만 docstring 을 남기면 판정이 어긋나므로 03-log 에 "docstring 3곳 포함" 을 적게 한다.
- **R-12 (1차, 하네스)** `verify-plan.sh` 62·68행 — 이 패키지 밖, 그대로 열려 있다.

### 사용자에게 알릴 것 · 사용자만 정할 수 있는 것
2차와 같고 계획에 모두 들어갔다: ① OpenAI 월 한도 소진 가능성(사용자 할 일 6) ② 배포 반영 기동이 운영 데이터를 비우고 **0003 적용 뒤에는 옛 해시로 되돌릴 수 없다**(197행·리스크 291행 — 2차 R2-1 ③ 반영) ③ U1 에서 로컬 개발 DB 인물이 지워진다(124행). 사용자만 정할 수 있는 것: 범위 축소 3 을 쓸 경우의 수용 기준 6번 변경. 3차에서 새로 생긴 항목은 없다.

### 검증하지 못한 것
- 전체 pytest 를 돌리지 않았다 — 위 "단위별 통과 가능성" 은 코드·테스트 파일 대조와 전수 검색으로 판정했다. 검색 패턴 밖의 방식으로 스키마·세션·고정 사용자에 기대는 테스트가 있으면 계획의 "목록 밖이 깨지면 멈추고 보고" 가 받는다.
- Caddy 가 `Host` 를 그대로 넘기고 클라이언트의 `X-Forwarded-Host` 를 덮어쓰는지는 이 저장소에 증거가 없다 — U7 Caddy 스모크(195행)가 배포 반영 전 관문이다.

## 4. 결정
결과: 통과
사유: 점검표 8행 통과, [필수] 0건. 2차 [필수] N-1~N-4 가 계획 본문에서 닫힌 것을 코드·기존 테스트와 대조해 확인했다(스키마 단언·`app_user_id` 참조·세션 단언·`PendingQuestion(` 직접 생성은 전수 검색). 남은 것은 [권고] R3-1~R3-4 와 하네스 R-12 이며, R3-1(`tests/test_api.py:91`)은 U1 에서 반드시 만나는 한 줄이라 활성화 전에 125행이나 위임 프롬프트에 더하기를 권한다.
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)
