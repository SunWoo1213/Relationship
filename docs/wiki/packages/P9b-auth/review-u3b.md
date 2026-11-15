# P9b-auth U3b 커밋 전 리뷰 — 모든 API 를 로그인 사용자 기준으로(계정 간 격리 본체)

검토자: verifier (fable)
일시: 2026-11-16 (HEAD `fa7ad82` + 미커밋 작업 트리, dev2). Mac 로컬만 판정.
범위: `app/api/{deps,routes,read}.py` · `app/tools/{context,questions}.py` · `app/db/session.py` · `app/auth/{deps,routes}.py` · 기존 tests 6파일 · 새 `tests/test_auth_required_routes.py`·`tests/test_user_isolation.py` · `03-log.md` "U3b 구현 메모(초안)" · `tests.md` U3b 절 · `evidence/20261116-00*-u3b-*`. 변경되지 않았지만 격리가 기대는 코드(`app/tools/persons.py`·`records.py`·`briefing.py` · `app/agent/loop.py` · `app/briefing/{select,inputs,run}.py` · `app/push/{notifier,subscriptions}.py` · `app/memory/*` · `app/er/candidates.py`)도 id 조회 지점을 따라가 읽었다.

판정: 통과

(2차 재검토 2026-11-16 00:32 — F-1 닫힘, 맨 아래 "6. 재검토" 절. 아래 1~5절은 1차 리뷰 당시 기록이며 1차 판정은 보류였다.)

1차 보류 사유는 [필수] F-1 하나다 — **전체 pytest "실패 0" 이 지금 재현되지 않는다(1 failed)**. 원인은 제품 코드가 아니라 구현자의 변이 실행이 공유 시험 DB 에 남긴 커밋 행 2건이다. **코드에서는 격리 누락을 찾지 못했다**(전 라우트 탐침 BAD 0, 변이 15종 중 격리 계약을 지우는 것은 전부 잡힘). F-1 은 잔여 행 정리 + 전체 pytest 재실행으로 닫히며 코드 재검토는 필요 없다.

## 1. 직접 실행한 명령과 결과

증거는 모두 `docs/wiki/packages/P9b-auth/evidence/` (`save_evidence.py` 저장). `<SCR>` = `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad`. 시험용 DB 를 새로 만들지 않았고 pytest 를 동시에 돌리지 않았으며 저장소 파일은 이 문서와 evidence 밖에는 쓰지 않았다.

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **1 failed, 2467 passed**, skip 0, exit 1 — 실패는 `tests/test_api_chat_query.py::test_chat_query_new_person_no_question_no_writes` (`assert 2 == 0`, 318행) → **F-1** | `20261116-0016-verifier-u3b-pytest-all.txt` |
| 실패 원인 | `bash <SCR>/vu3b/residue.sh` (시험 DB 잔여 읽기 · 그 테스트 단독 · U3b 이전 HEAD 를 `git archive` 로 푼 사본에서 같은 파일) | 시험 DB 에 커밋된 `pending_questions` 2행(id 24899·24900, `user_id='local'`, `session_id='chat:fix023-chat-ok-…'`·`'chat:fix023-chat-dberr-…'`, 생성 2026-11-16 00:12:18 KST). **U3b 이전 사본에서도 같은 테스트가 같은 `2 == 0` 으로 실패** — U3b 코드와 무관 | `20261116-0025-verifier-u3b-testdb-residue.txt` |
| 새 테스트 2파일 단독 | `… -m pytest tests/test_auth_required_routes.py tests/test_user_isolation.py -q -rs` | 29 passed | `20261116-0017-verifier-u3b-new-tests.txt` |
| ruff | `.venv/bin/python -m ruff check app tests scripts evaluation alembic` | All checks passed | `20261116-0017-verifier-u3b-ruff.txt` |
| mypy | `.venv/bin/python scripts/mypy_check.py --run` | 새 오류 없음(38/38) | `20261116-0017-verifier-u3b-mypy.txt` |
| tools_check | `.venv/bin/python scripts/tools_check.py` | 7/7 ok | `20261116-0017-verifier-u3b-tools-check.txt` |
| alembic check | `POSTGRES_PORT=5433 .venv/bin/python -m alembic check` | No new upgrade operations detected | `20261116-0017-verifier-u3b-alembic-check.txt` |
| ER·평가 불변 | `git diff --stat -- app/er evaluation reports data` | 빈 출력 | `20261116-0017-verifier-u3b-er-unchanged.txt` |
| 범위(U5 몫·범위 밖) | `git diff --stat -- app/settings.py app/briefing .env.example app/main.py app/push app/agent app/memory alembic scripts` | 빈 출력 | `20261116-0017-verifier-u3b-scope.txt` |
| 기본값 grep | `grep -n default_factory=app_user_id app/tools/context.py` | 0줄, exit 1(기대대로) | `20261116-0017-verifier-u3b-ctx-default.txt` |
| 정적 판정 묶음 | `bash <SCR>/vu3b/static-checks.sh` — 요청 경로 grep(+통제) · 헤더 재사용 grep · 범위 diff · `get_session` 동일 객체 · 15개 모듈 "맨 먼저 import" · `PUSH_DEV_PAGE_ENABLED=1` 앱의 전 라우트 쿠키 없는 응답 | 아래 2절 | `20261116-0024-verifier-u3b-static-checks.txt` |
| 변이 15종 + 기준선 | `python3 <SCR>/vu3b/vmutate.py all` (저장소 밖 사본 `<SCR>/vu3b/copy`, **롤백형 시험만**) | 기준선 29 + 172 passed. 격리 계약 변이 12종 잡힘, 생존 3종(동등 1 · 하위 시험이 잡음 1 · 미검출 1) — 3절 | `20261116-0020-verifier-u3b-mutations.txt` · `20261116-0022-verifier-u3b-mutations-extra.txt` |
| 두 계정 탐침 | `.venv/bin/python <SCR>/vu3b/probe.py` (롤백 트랜잭션 안, 끝난 뒤 `users`·`persons` 0행) | **BAD 0건** — 4절 | `20261116-0024-verifier-u3b-two-account-probe.txt` |

## 2. 위임 항목별 판정 근거

### 2.1 격리 누락 경로 전수 — 누락 없음

`app.routes` 열거(탐침 (0)): 문서 4 · `/health` · API 11 · `/auth/*` 4. DELETE 라우트는 없다(`app/api/delete.py` 는 라우트에 묶여 있지 않다).

id 로 행을 읽거나 쓰는 지점과 걸린 조건:

| 경로 | 지점 | 조건 |
|---|---|---|
| `GET /persons` | `read.py:153-166` | 목록·별칭 둘 다 `Person.user_id == user_id` |
| `GET /persons/{id}` | `read.py:185` → `persons.py:417-425` `_owned_person` | `Person.id` + `Person.user_id`. 이후 조회는 그 `person.id` 로만 |
| `GET /events/{id}/raw` | `read.py:84-96` | `events → persons` 조인 + `Person.user_id` |
| `GET /persons/{id}/facts/{fid}/sources` | `read.py:115-137` | 사실: `PersonFact.person_id == person_id` + `Person.user_id`. 근거 이벤트: `Event.person_id == person_id` |
| `GET /briefings` | `read.py:290-298`(지정 일정 소유 선검사) · `323-340`(trace → 일정 → 인물 조인, `Person.id == trace.pid AND Person.id == Schedule.person_id`, `Person.user_id`) | `agent_traces` 에 `user_id` 가 없어도(결정 N) 남의 일정 trace 는 조인에서 떨어진다 |
| `POST /briefings/run` | `select.py:56-61`(지정) · `72-76`(창) | 둘 다 `Person.user_id == ctx.user_id`. 그 뒤 `detect_patterns`·`get_briefing`·`promote` 는 각자 `_owned_person`(`patterns.py:126`·`briefing.py:74`·`promote.py:279`). `get_briefing` 의 `session.get(Schedule, …)`(`briefing.py:144`)은 `schedule_row.person_id != person.id` 로 묶인다 |
| 푸시 발송 | `notifier.py:110-125` | `person.user_id != self.user_id` 면 발송 안 함. 구독 조회 `subscriptions.py:79` 는 `user_id` 조건 |
| `POST /push/subscriptions` | `routes.py` → `save_subscription(session, user.id, …)` | 로그인 계정으로 저장 |
| `GET /questions/pending` | `questions.py:304-305` | `user_id == ctx.user_id` AND `session_id == chat:<user.id>` |
| `POST /answers/{id}` | `deps.py:147-149` `build_ctx` · `questions.py:261-263` `answer_question` | 둘 다 소유 불일치 → 같은 `QuestionNotFound` |
| `POST /chat` 루프 | `persons.py:178·204·219`(후보 검색 3곳) · `er/candidates.py:70` · `records.py:87·130` · `persons.py:540` · `loop.py:1269`(`_read_card`) | 전부 `ctx.user_id` |
| trace id 조회 | `context.py:257` · `er/pipeline.py:369` | `ctx.last_trace_id`(같은 턴이 방금 만든 행)만 — 요청 값이 아니다 |

- **재개 경로(`load_resume_input`·`persons.py:306` 에 소유 조건이 없는 이유) — 성립.** ① 둘 다 `build_ctx` 뒤에만 불린다(`routes.py:245-247`; `ctx.confirmed_question_id` 를 세우는 곳은 `loop.py:1874` 한 곳). ② 질문 `context` 의 `person_id`·`candidate_ids` 는 서버가 그 계정의 턴에서 만든 값이고, 설령 남의 인물 id 가 들어 있어도 재개가 쓰는 길은 `update_person`(`loop.py:1845`)·`add_schedule`(`1908`)·`_read_card`(`1684`)·`_execute_call` 뿐이라 전부 `_owned_person(ctx.user_id)` 에서 막힌다. **직접 확인**: A 소유 질문의 context 에 B 의 `person_id` 를 심어 답했다(탐침 (4)) — identity(기록) → 200 `loop_error: PersonNotFound`·저장 0, identity(조회) → "기록이 없어요", schedule → 200 `loop_error: PersonNotFound`. 세 경우 모두 B 의 사건·별칭·사실·일정·`briefed_at`·질문·trace 불변, B 문자열 노출 0.
- **`POST /chat` 에서 남의 `person_id`** — LLM 제안은 언급 문자열만 갖고 `person_id` 는 코드가 ER 결과로 채운다(`loop.py:86-89`). ER 후보가 계정 안으로 좁혀져 있고(변이 VV-8·VV-9 가 잡힘), 툴 층이 다시 막는다(VV-7).
- **`X-Session-Id`** — `app/` 에서 `X-Session-Id|x_session_id|resolve_session_id|Header(|request.headers` 일치는 docstring 3줄뿐(정적 판정 2). 탐침 (5): A 가 `X-Session-Id: chat:<B>` 를 보내도 `ChatOut.session_id`·그 턴 trace 의 `session_id` 집합이 `chat:iso-user-a` 하나, `/questions/pending` 에 B 질문 없음, 형식이 어긋난 헤더도 200.
- **404 구별 불가** — 남의 id 9건 모두 404 `{"detail":{"code":"not_found"}}`, 없는 id 응답과 상태·본문 바이트·content-type·헤더 키 집합이 같다(탐침 (2)(3)). 처리 시간 중앙값 차(40회): GET 4종 +0.01~+0.05 ms, `POST /answers` −0.38 ms — 존재 여부를 가를 크기가 아니다(탐침 (7)).

### 2.2 401 계약 — 확인

탐침 (1): 공개 3개·문서 4개 밖 13개(메서드·경로)가 쿠키 없이 전부 401 `{"detail":{"code":"unauthenticated"}}`. 가짜 쿠키도 401. 숫자 아닌 경로·질의도 401 이 먼저다. `PUSH_DEV_PAGE_ENABLED=1` 앱에서도 같은 13개가 401 이고 더 열리는 것은 `/push-dev/` 정적 3경로뿐이다(정적 판정 7).

열거 테스트가 새 라우트 누락을 잡는가 — **잡는다.** 변이 VV-10(`routes.py` 에 `current_user` 없는 `GET /persons-count` 추가) → `test_every_non_exempt_route_requires_login`(`GET /persons-count -> 200`)·`test_every_api_route_declares_current_user_dependency`(`[('GET', '/persons-count')]`) 둘 다 실패. 구현자 V3b-1 은 기존 라우트의 의존성을 바꾼 것이라 "새 라우트" 는 이 변이가 처음 본다.

### 2.3 닫힌 목록 밖 1건(`_count_selects` 필터) — 수용

- 필터는 문장에 `auth_sessions` 가 든 것만 뺀다. 인증 조회(`sessions.py:76-80`, `users JOIN auth_sessions`)만 해당하고 `list_persons` 의 두 SELECT(`read.py:153-166`)는 `persons`·`events`·`person_aliases` 만 건드린다 — 가려질 다른 SELECT 가 없다.
- N+1 검출력 유지: 변이 VV-14(목록에 인물마다 별칭 SELECT 재도입) → `assert 5 == 12` 로 실패.
- `== 3` 으로 올리는 것과 비교: 둘 다 정직하다. 필터 쪽은 "목록 1 + 별칭 1" 이라는 원래 단언의 뜻을 지키고, `== 3` 쪽은 인증 조회가 2회로 늘어나는 것까지 잡는다. 지금 방식에 "걸러낸 문장이 정확히 1건" 단언 한 줄을 더하면 둘의 장점을 다 갖는다(R-5). 03-log 에 닫힌 목록 밖임을 밝히고 확인을 요청한 처리는 계획 문장("멈추고 보고")의 취지에 맞다.

### 2.4 `get_session` 이동 — 동작 불변, 순환 해소 확인

`app.api.deps.get_session is app.db.session.get_session` · `app.auth.deps`·`app.auth.routes` 의 것도 같은 객체 · `current_user` 의 세션 의존성도 같은 객체(정적 판정 6) → `app.dependency_overrides[get_session]` 키가 그대로 맞는다(전체 pytest 의 롤백 픽스처 시험들이 이를 쓴다). 함수 본문은 옮기기 전과 글자 그대로(commit/rollback/close). 15개 모듈을 각각 새 인터프리터에서 맨 먼저 import — 전부 exit 0. `app/db/session.py`·`app/auth/{deps,routes}.py` 는 계획 "고치는 기존 파일" 표에 없지만 U2 인계(03-log 63행 "U3b 에서 `get_session` 의 위치를 정리한다")가 남긴 수단이고 03-log 에 보고돼 있다.

### 2.5 바꾼 단언 — 전부 닫힌 목록 안, 느슨해진 것 없음

`git diff -U0 -- tests` 전수. 단언이 바뀐 곳은 ① 2건(`test_api_chat.py:236-237`, `test_api_questions_pending.py:82-83`) · ② 5건(`test_api_chat.py:148·209·222`, `test_api_chat_query.py:440`, + `test_commit_boundaries.py:128` 은 **추가**) · ③ 2건(`test_api_questions_pending.py:73`, `:137-139`). 나머지는 데이터 준비·조회 조건(`SID`, `CHAT_SESSION`, trace 를 `session_id` 로 거르는 조건)·로그인 클라이언트 교체다. 03-log 의 전/후 목록과 일치한다. 삭제되거나 약해진 단언은 없다(`uuid.UUID(...)` 파싱 → 값 일치는 더 강하다).

### 2.6 범위 — 확인

`app/settings.py`(`app_user_id()` 554행·`DEFAULT_APP_USER_ID` 107행)·`app/briefing/scheduler.py`·`.env.example:53` 그대로. 요청 경로 grep(`app/api app/tools app/auth`) 0줄 exit 1, 통제(`app` 전체) 14줄 exit 0 — 구현자 증거와 같다. 툴 7종 7/7, ER·평가 diff 0.

## 3. 변이 시험(구현자 표 V3b-1~15 에 없는 것)

| 변이 | 새 시험 2파일 | 기존 롤백형 시험 |
|---|---|---|
| VV-1 사실 근거 조회의 `Person.user_id` 조건 제거 | 잡힘(`test_fact_sources_…` 200≠404) | 잡힘 2건 |
| VV-2 이벤트 원문 조회의 조건 제거 | 잡힘 | 잡힘 |
| VV-3 `POST /briefings/run {schedule_id}` 소유 조건 제거 | 잡힘(200≠404) | 잡힘 |
| VV-4 본문 없는 실행의 창 선정에서 사용자 조건 제거 | **생존** | `test_briefing_select.py::test_select_due_schedules_excludes_other_user` 가 잡음 → R-1 |
| VV-5 브리핑 trace 목록 조회의 조건 제거 | 잡힘(B 일정이 목록에 섞임) | 잡힘 |
| VV-6 `GET /briefings?schedule_id=` 소유 선검사 제거 | 잡힘(200≠404) | 잡힘 4건 |
| VV-7 `_owned_person` 의 사용자 조건 제거 | 잡힘 3건 | 잡힘 5건 |
| VV-8 후보 검색(별칭 일치)의 조건 제거 | 잡힘(`identity` ≠ `new_person`) | 잡힘 |
| VV-9 후보 검색(임베딩 top-K)의 조건 제거 | 잡힘(KeyError 로 — 단언이 아닌 충돌) | 생존 |
| VV-10 `current_user` 없는 새 라우트 | 잡힘 2건 | — |
| VV-11 인물 목록의 별칭 조회에서만 조건 제거 | 생존 | 생존 — **동등 변이**(`by_person.get(p.id)` 가 내 인물 id 로만 꺼낸다) |
| VV-12 `list_pending` 의 세션 조건 제거 | 잡힘 | 잡힘 8건 |
| VV-13 `get_notifier` 가 `user.id` 대신 고정 문자열 | **생존** | **생존**(`test_push_wiring`·`test_push_notifier`·`test_api_briefings`·`test_briefing_run` 45건 통과) → R-2 |
| VV-14 인물 목록 N+1 재도입 | — | 잡힘(`5 == 12`) |
| VV-15 답변 소유 검사 두 곳 모두 제거 | 잡힘 4건 | 생존(새 시험만 본다) |

구현자의 V3b-12~14 는 라우트가 넘기는 값을 고정 문자열로 바꾸는 변이라 조회 함수의 where 절 자체는 보지 않는다. VV-1·2·5·6·7 이 그 빈칸을 메웠고 전부 잡혔다.

## 4. 소견

### [필수]

**F-1 — 전체 pytest "실패 0" 이 재현되지 않는다(시험 DB 잔여 행).**
- 사실: 지금 전체 실행은 `1 failed, 2467 passed`. 실패 단언은 `tests/test_api_chat_query.py:318` `assert _counts(db_session)["pending_questions"] == 0`(테이블 전체 행 수) 이고 값은 2.
- 원인: 구현자 변이 스크립트 `<SCR>/p9b-u3b/mutate.py` 의 시험 목록(26행)에 **실제 커밋을 쓰는 `tests/test_commit_boundaries.py`** 가 들어 있다. 변이 V3b-9(채팅 ctx 의 사용자를 `"local"` 로 고정, 00:12:14 KST 실행)에서 그 파일 3건이 실패하면서 `user_id='local'` 로 커밋된 `pending_questions` 2행(00:12:18)이 남았다 — 그 테스트의 정리는 고유 `user_id` 로 만든 행만 지우므로 `'local'` 행은 지워지지 않는다. V3b-10 의 `session_id='chat:shared'` trace 28행도 같은 경로의 잔여다.
- 제품 코드 결함이 아니라는 근거: U3b 이전 HEAD 사본에서도 같은 테스트가 같은 값으로 실패한다(`…-testdb-residue.txt` 3절). 구현자의 통과 증거 `20261116-0009-u3b-pytest-all.txt`(2468 passed)는 변이 실행(00:11~00:12) **이전** 것이다.
- 완료 조건: ① 시험 DB `relationship_test` 의 잔여 행을 지정 조건으로 지운다(`pending_questions` id 24899·24900, `agent_traces.session_id = 'chat:shared'` — 테이블 전체 삭제·TRUNCATE 금지) ② 전체 pytest 재실행 2468 passed·실패 0·skip 0 증거 ③ `mutate.py` 에서 커밋형 테스트를 빼거나 변이 뒤 잔여 확인을 넣고, 03-log 에 이 경위를 한 줄. verifier 는 DB 를 고치지 않았다.

### [권고]

- **R-1** `test_user_isolation.py::test_briefing_run_without_body_only_briefs_my_schedules` 에 `resp.json()["skipped"] == []` 단언 추가. 창 선정의 사용자 조건이 빠져도(VV-4) 이 시험은 통과한다 — `run_briefings` 가 일정별 예외를 삼켜 `skipped` 에 넣기 때문으로 보인다(`run.py:284-289`; 변이 상태의 응답 본문은 직접 보지 않았다 — 추정). 하위 단위 시험이 잡으므로 필수는 아니다.
- **R-2** `get_notifier` 가 로그인 계정으로 알림기를 만드는지 보는 시험이 없다(VV-13 생존). 틀려도 `notifier.py:125` 가 소유 불일치면 발송하지 않아 안전한 쪽으로 실패하지만, U5 의 `tests/test_push_endpoint_owner.py` 에 "`POST /briefings/run` 의 알림은 로그인 계정의 구독으로만" 을 넣을 것.
- **R-3** 재개 경로에서 질문 `context` 가 남의 `person_id` 를 가리키는 경우의 회귀 시험이 없다. 탐침으로 안전함은 확인했다(2.1). `<SCR>/vu3b/probe.py` (4) 의 세 경우를 `test_user_isolation.py` 로 옮기면 "소유 조건을 안 거는 곳 2" 의 근거가 시험으로 남는다.
- **R-4** 쿠키 없이 **깨진 JSON** 을 `POST /chat` 에 보내면 401 이 아니라 422 `json_invalid` 다(FastAPI 가 의존성보다 본문 해석을 먼저 한다). 데이터 접근은 없고 `/openapi.json` 이 공개라 새로 드러나는 것도 없다. 판정 #2 문구("모든 API 가 로그인 없이 401")의 알려진 예외로 03-log 에 한 줄.
- **R-5** `_count_selects` 에 "걸러낸 `auth_sessions` 문장 수 == 1" 단언을 더하면 인증 조회가 요청당 2회 이상으로 늘어나는 회귀도 잡는다(2.3).
- **R-6** (U5 인계) 같은 푸시 endpoint 를 A·B 가 차례로 구독하면 두 계정에 각각 행이 생긴다(탐침 (6)) — 계획이 U5 로 미룬 "endpoint 하나" 규칙 전까지의 현 상태다. U5 커밋 전에는 배포하지 않는다.
- **R-7** (기존 문제, U3b 무관) 시험 DB 에 `agent_traces` 235행이 쌓여 있다 — `test_answer_concurrency` 가 실행마다 `concurrency-setup-*`·`answer-concurrency-tool-a` trace 를 커밋으로 남긴다. 테이블 전체 행 수를 `== 0` 으로 단언하는 시험(`test_api_chat_query.py:318`)은 이런 잔여에 취약하다. 하네스 FIX 후보.
- **R-8** 무시되는 `X-Session-Id` 를 아직 보내는 곳: `tests/test_api_answers_resume.py:113·350·395·530`, `tests/test_memory_loop.py:297`, 쓰이지 않는 인자가 남은 `tests/test_api_chat_query.py::_post_chat`. 동작에는 영향 없다 — 정리 대상.
- **R-9** `test_push_dev_page_routes_are_the_only_other_exempt` 는 켜진 앱에서 나머지 라우트가 실제로 401 인지 요청으로 보지 않는다(집합 포함만). 정적 판정 7 로 지금은 전부 401 임을 확인했다.

## 5. 다음 단위 인계

- U4(대화 기록)·U5(스케줄러·푸시)는 F-1 이 닫히고 U3b 가 커밋된 뒤 시작한다.
- 변이 시험은 롤백형 시험 파일로만 돌린다(커밋형 `test_commit_boundaries`·`test_answer_concurrency`·`test_briefing_select` 의 동시성 1건은 변이 상태에서 잔여를 남긴다).

## 6. 재검토 (2차, 2026-11-16 — F-1 정리 뒤)

판정: 통과. [필수] 0건.

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2471 passed**, 실패 0, skip 0, exit 0 (2468 + R-3 회귀 3건) | `20261116-0031-verifier-u3b-fix-pytest-all.txt` |
| ruff | `.venv/bin/python -m ruff check app tests scripts evaluation alembic` | All checks passed | `20261116-0032-verifier-u3b-fix-ruff.txt` |
| `app/` 무변경 | `git diff --stat -- app` · `find app -name '*.py' -newer <1차 pytest 증거>` | 8파일 143+/128− — 1차 때 본 파일별 줄 수(116·3·82·13·2·20·7·28)와 같다. 1차 리뷰 뒤 고쳐진 `app/` 파일 0 | `20261116-0032-verifier-u3b-fix-app-diff.txt` |
| 시험 DB 잔여 | `.venv/bin/python <SCR>/vu3b/dbstate.py` | `pending_questions` 0 · `users`·`auth_sessions`·`persons`·`events`·`schedules`·`push_subscriptions`·`chat_messages` 0 · `agent_traces` 225 | `20261116-0032-verifier-u3b-fix-dbstate-after.txt` |
| 추가 단언·회귀 시험 변이 | `python3 <SCR>/vu3b/vmutate_fix.py` (저장소 밖 사본, 롤백형 2파일만) | 기준선 38 passed, 변이 5종 전부 잡힘 — 아래 | `20261116-0032-verifier-u3b-fix-mutations.txt` |

- **삭제가 지정 행에 한정됐는가 — 그렇다.** 구현자 증거: 삭제 전 `pending_questions` 2(id 24899·24900)·`chat:shared` trace 28·trace 전체 235(`…-0028-u3b-fix-residue-before.txt`) → `삭제: {'pending_questions': 2, 'agent_traces': 28}`(`…-0029-u3b-fix-residue-delete2.txt`) → 0·0·207(`…-after2.txt`). 235 − 28 = 207 로 다른 trace 는 지워지지 않았다. 그 뒤 전체 pytest 1회마다 `test_answer_concurrency` 가 trace 9행을 남겨(R-7) 207 → 216(구현자 실행) → 225(내 실행)로 맞아떨어진다. 나머지 테이블은 1차 때(`…-0025-verifier-u3b-testdb-residue.txt`)도 지금도 0 이다. 첫 삭제 시도(`…-residue-delete.txt`, exit 1)는 트랜잭션 오류로 아무것도 지우지 못했고 직후 상태가 그대로임이 `…-residue-after.txt` 에 남아 있다.
- **추가 단언·회귀 시험이 값을 단언하는가 — 그렇다.**
  - R-1 `skipped == []`: VV-4(창 선정 사용자 조건 제거) → `assert [{'reason': …, 'schedule_id': 41209}] == []` 로 실패. 1차의 추정(B 일정이 A 응답의 `skipped` 에 실린다)이 사실로 확인됐다.
  - R-5 `len(skipped) == 1`: VF-1(인증 조회를 요청당 2회로) → `assert 2 == 1` 로 실패.
  - R-3 회귀 3건: VV-7(`_owned_person` 조건 제거) → 3건 모두 실패 · VF-3(`add_event`·`add_schedule` 의 소유 검사 제거) → `[schedule]` 실패 · VF-2(`_read_card` 가 소유자를 무시) → `[identity_query]` 실패.
- `mutate.py` 의 시험 목록에서 `tests/test_commit_boundaries.py` 가 빠졌다(`grep` 일치 0).

### 남은 [권고] (커밋을 막지 않는다)

- **R-10 (새)** `test_resume_context_pointing_at_other_users_person_changes_nothing[identity_query]` 는 변이 상태에서 단언이 아니라 `openai.OpenAIError`(키 없음)로 실패한다 — `world` 픽스처가 조회 답변기를 가짜로 바꾸지 않아, 카드가 읽히면 실제 답변기를 만들려 한다. 이 셸에는 키가 없어 네트워크 호출은 없었지만, `OPENAI_API_KEY` 가 있는 환경에서 회귀가 나면 B 의 카드가 외부로 나갈 수 있다. 이 경우에 가짜 답변기를 끼워 "B 문자열 없음" 단언이 직접 잡게 할 것.
- **R-11 (새)** 같은 시험의 `assert resp.status_code in (200, 404)` 는 느슨하다 — 질문이 다른 이유로 404 가 되면 재개가 돌지 않은 채 통과한다. 지금 세 경우 모두 200 이므로(1차 탐침 (4)) `== 200` 과 `stored == {persons:0, events:0, schedules:0}` 로 좁힐 것.
- R-2(`get_notifier` 사용자 연결 시험, U5) · R-4(쿠키 없는 깨진 JSON 422 — 03-log 한 줄) · R-6(같은 endpoint 두 계정, U5) · R-7(`test_answer_concurrency` 의 trace 누적 — 하네스 FIX 후보) · R-8(무시되는 헤더 전송 정리) · R-9(`/push-dev/` 켜진 앱의 401 실요청)는 그대로 열려 있다. R-1·R-3·R-5 는 반영됐다.
