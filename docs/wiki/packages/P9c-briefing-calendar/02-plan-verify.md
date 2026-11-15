# P9c-briefing-calendar · 계획 검증 (02-plan-verify)

대상: 01-plan.md (초안 2026-11-15, architect) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-16

- 기준: dev2 HEAD `1723a84`, Mac 로컬. `docs/wiki/CURRENT.md` 는 `active: P9b-auth` — 이 검증은 **활성화 전 사전 검증**이다.
- 선행 확인(`bash .claude/scripts/gitlog.sh P9c-briefing-calendar P9c`): 태그 `P9c` 커밋은 `3d786a5`(CR-006 문서)·`d9c5a5f`(P9b 계획) 둘뿐, 제품 코드 커밋 0. P9b 구현 커밋은 `0f9223e`·`1cf67cd`·`119a42f`·`75845d1`·`a25123b`·`ca539a1`·`6ecf635`·`fa7ad82`.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P9c-briefing-calendar verify-plan -- bash .claude/scripts/verify-plan.sh P9c-briefing-calendar`
저장: `evidence/20261116-0150-verify-plan.txt` (HEAD `1723a84`, exit 0)
```
== verify-plan P9c-briefing-calendar  (2026-11-16 01:50) ==
PASS  존재: docs/wiki/packages/P9c-briefing-calendar/01-plan.md
PASS  존재: docs/wiki/packages/P9c-briefing-calendar/02-plan-verify.md
PASS  카드 존재: D17
PASS  카드 존재: D18
PASS  Refs 있음: - [ ] U1 **[backend-agent] 월 범위 일정 조회 API `GET /schedules`**
PASS  Refs 있음: - [ ] U2 **[frontend-agent] 브리핑 화면 목록/달력 전환과 달력 컴포넌트** / Ref
PASS  Refs 있음: - [ ] U3 **[메인 세션 + 사용자] registry·문서·배포 반영·사람 점검** / Refs: P
PASS  backlog 일치: 브리핑 화면에서 목록 보기와 달력 보기를 전환할 수 있다 + 월 달력에 그달 일정이 날짜별로 표시되고 브리핑
PASS  의존 완료: P6-briefing
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 1 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: tests/test_api_schedules_range.py
PASS  registry 중복 없음: web/src/components/BriefingCalendar.tsx
PASS  registry 중복 없음: web/src/__tests__/calendar.test.tsx
PASS  registry 중복 없음: docs/wiki/packages/P9c-briefing-calendar/tests.md
PASS  registry 중복 없음: 03-log.md
WARN  registry 에 다른 패키지로 이미 있음: app/api/read.py → | 모듈 | 읽기 전용 조회 `list_persons()`·`get_person_card()` · 상수 `TIMELINE_LIMIT=20`·`U
| 모듈 | 원문 조회 `get_event_raw()`·`get_fact_sources()` · 상수 `FACT_SOURCES_LIMIT=20`
| 모듈 | 브리핑 조회 `list_briefings()` · 상수 `BRIEFINGS_LOOKBACK_DAYS=7`·`BRIEFINGS_LIM
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-tools | 4d58
| 엔드포인트 | POST /chat | app/api/routes.py | P5-loop | d5c8ec9 | 발화 1건 → 인식(LLM 1회
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 엔드포인트 | GET /persons · GET /persons/{person_id} (읽기 전용) | app/api/routes.py | 
| 엔드포인트 | GET /events/{event_id}/raw · GET /persons/{person_id}/facts/{fact_id}/
| 엔드포인트 | GET /questions/pending · GET /briefings (읽기 전용) | app/api/routes.py | 
| 모듈 | 계정 대화 세션 `chat_session_id(user)` = `chat:<user_id>` · 전 라우트 로그인 필수(`/heal
| 모듈 | 대화 기록 `append(session, user_id, role, content, question_id=None)`(flush 만
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools | 4d5817e | `AnswerIn`·`
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 모듈 | 조회 응답 `PersonListItemOut`·`PersonBasicOut`·`PersonFactOut`·`PersonPattern
| 모듈 | 원문 응답 `EventRawOut`·`FactBriefOut`·`FactSourceEventOut`·`FactSourcesOut` 
| 모듈 | 브리핑 조회 응답 `BriefingRecordOut`·`BriefingScheduleOut`·`BriefingPersonOut` |
| API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
| 설정 | 고정 사용자 폐지 — `app_user_id()`·`DEFAULT_APP_USER_ID`·`APP_USER_ID` 삭제(`tests
WARN  registry 에 다른 패키지로 이미 있음: web/src/api/client.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 세션 보관·채팅 호출 | `web/src/session.ts`(`getSessionId`·`setSessionId`·`clearSession
| 인물 카드 화면 | `web/src/screens/PersonCardScreen.tsx`(`PersonCardScreen`·`CARD_NOT
| 브리핑 화면 | `web/src/screens/BriefingScreen.tsx`(`BriefingScreen`·`BRIEFING_NOTIC
| 푸시 구독 | `web/src/push.ts`(`subscribeToPush`·`getPushStatus`·`urlBase64ToUint8A
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
WARN  registry 에 다른 패키지로 이미 있음: types.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/BriefingScreen.tsx → | 브리핑 화면 | `web/src/screens/BriefingScreen.tsx`(`BriefingScreen`·`BRIEFING_NOTIC
| 브리핑 화면 알림 버튼·인앱 배너 | `BriefingScreen.tsx` `PushSubscribe`(미구독 "알림 받기"/진행 "알림 켜
PASS  registry 중복 없음: docs/wiki/registry.md
== 결과: FAIL=0 WARN=7 ==
```
- FAIL 0 · WARN 7 = 점검표 보류 1건(5행) + registry 기존 행 확장 6건.
- 검증 중 실행한 탐침 증거: `evidence/20261116-0151-planverify-probe-401-routes.txt`(로그인 의존성 401 이 필수 쿼리 누락·형식 오류보다 먼저 `401 401` · 현재 API 라우트 17개 열거 · `briefing.test.tsx` 시험 19건). `evidence/20261116-0150-planverify-probe-401-routes.txt` 는 같은 탐침의 첫 실행이 스크립트 경로 문제(`ModuleNotFoundError: No module named 'app'`)로 중간에 끝난 기록이다 — 0151 이 유효본.
- 직전 출력 `evidence/20261116-0144-verify-plan.txt` 는 FAIL 1(이 문서 없음)·WARN 6(registry 기존 행 확장 — `app/api/read.py`·`routes.py`·`schemas.py`·`web/src/api/client.ts`·`types.ts`·`BriefingScreen.tsx`, 새 함수·라우트를 기존 파일에 더하는 것이라 중복 구현이 아님).
- **스크립트가 보지 못하는 것(손으로 확인)**: `verify-plan.sh` 62행 `grep -oE 'P[0-9]{1,2}-[a-z0-9-]+'` 는 숫자 뒤에 글자가 오는 id(`P9b-auth`)를 못 읽는다 → 출력의 "의존 완료" 는 `P6-briefing`·`P8-frontend` 둘뿐이고 **`P9b-auth` 의존은 검사되지 않았다.** 손 확인: `docs/wiki/packages/P9b-auth/04-review.md` 파일 없음(폴더 목록: `01-plan.md`·`02-plan-verify.md`·`03-log.md`·`review-u1~u6.md`·`tests.md`·`u6-notes.md`·`u8-demo-script.md`) → **의존 미완료**. 점검표 5행에 그대로 적는다. P4 게이트는 68행 `sed` 가 `P9c-…` 에서 숫자를 못 뽑아 건너뛰지만 `P4b-er-redesign` 완료(`CURRENT.md` 메모 "P4b-er-redesign 완료(2026-09-23, verifier 04-review `완료`, 사용자 승인)")로 충족.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, 채팅방 목록" — 계획 범위는 조회 API 1개·화면 전환뿐. `changes/CR-006.md` 변경 항목 2 "범위 표(2장): 포함 칸 "만남 전 브리핑 생성" 의 보기 방식 확장 — 제외 칸 변동 없음". 계획 28~31행 "하지 않는 것" 4항(주·일 보기·일정 편집, 새 의존성, 생성 버튼 추가, `GET /briefings` 창·상한 변경)이 명시됨 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙5 `CLAUDE.md` "화면 수를 고정하지 않는다 — 필요한 화면은 계획에서 근거와 함께 더한다(CR-006)" — 새 화면·새 해시 라우트 없음(`web/src/routes.ts` 는 고침 목록에 없음), 근거는 CR-006 변경 항목 2 원문. 원칙7 경계 `changes/CR-006.md` "달력은 이미 만들어진 브리핑과 일정을 **날짜로 배치해 보여 줄 뿐** 새 생성·새 문장이 없다(LLM 호출 0) → 충돌 없음" — 계획 39행 "쓰기·trace·LLM 0". 원칙9 같은 카드 "읽기 전용 조회라 판정이 없고 `agent_traces` 를 쓰지 않는다(기존 `GET /briefings` 와 같은 규약)" — `app/api/read.py` 모듈 docstring "`agent_traces` 기록 없음(툴이 아니라 화면용 조회이므로 `@traced` 를 쓰지 않는다)" 와 같은 규약. 원칙1~4·6·8 은 ER·패턴·평가 경로 무변경이라 무관. 다만 "UI에 시간을 쓰지 않는다" 는 R-4(모바일 칸) 참고 |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `decisions/D18-login-user-isolation.md` 지킬 것 4 "`/health`·`/auth/signup`·`/auth/login` 밖의 모든 라우트가 로그인 의존성을 갖는다 — 라우트 목록을 열거해 미로그인 401 을 단언하는 계약 테스트가 있다(새 라우트가 빠지면 실패)" — 계획 39행 "로그인 필수, P9b 의존성"·47행 "미로그인 401". 실제 계약 시험 `tests/test_auth_required_routes.py` 는 `app.routes` 를 열거하므로 새 `GET /schedules` 가 자동으로 걸린다(쿼리 없이 호출해도 401 이 422 보다 먼저임을 탐침으로 확인 — §3 R-1). 결정 3 "모든 조회·쓰기는 로그인 사용자의 `users.id` 를 `user_id` 로 쓴다" — 계획 46행 "`Person.user_id == user_id`". 지킬 것 9 "툴 7종 시그니처·ER 4단계·임계치·확신도는 바뀌지 않는다" — 계획은 툴을 건드리지 않음. 충돌 없음(계획이 `_MUST_REQUIRE_LOGIN` 확장을 적지 않은 것은 R-1) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.6-briefing-push.md` "보기(CR-006 변경 항목 2, P9c-briefing-calendar): 브리핑 화면에 목록 보기와 함께 **월 달력 보기** — 월 범위 일정과 그 일정의 최신 브리핑 존재 여부를 날짜별로 보인다. 읽기 전용(LLM 0·trace 0), 새 생성 없음" — 계획 목표·API 계약과 같은 문장. 스키마: 계획 14행 "**스키마 변경 0**" — `app/db/models.py` `Schedule(id, person_id, title, scheduled_at, briefed_at)` 가 `CLAUDE.md` 스키마 v2 `schedules(id, person_id, title, scheduled_at, briefed_at)` 와 같고 새 테이블·컬럼 없음. 툴 시그니처·임계치·`ask_user` 는 계획 범위 밖(무변경). 단 카드의 "최신 브리핑 **존재 여부**" 를 계획이 두 값(`briefed_at`·`briefing_trace_id`)으로 내보내며 어느 쪽이 "브리핑됨" 인지 정하지 않은 것은 §3 H-3 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 보류 | `docs/backlog.md` 104행 "의존: **P9b-auth 04-review 완료**(달력 조회가 로그인 사용자 기준)" · 계획 5행 "의존: **P9b-auth 04-review `결과: 완료`**(미충족 …)". `docs/wiki/packages/P9b-auth/04-review.md` 가 없다(1절 손 확인) → 선행 미완료. `CURRENT.md` "active: P9b-auth"(한 번에 활성 하나). P6-briefing·P8-frontend 는 기계 검증 PASS, P4 게이트는 P4b 완료로 충족. **계획의 결함이 아니라 활성화 조건 미충족**이다 — P9b 04-review `결과: 완료` 커밋 해시가 생기면 이 행만 그 해시로 다시 판정한다(H-1) |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | 기계 검증 "PASS  backlog 일치: 브리핑 화면에서 목록 보기와 달력 보기를 전환할 수 있다 + 월 달력에 그달 일정이 날짜별로 표시되고 브리핑…" — 계획 59행 ↔ `docs/backlog.md` 104행 "수용기준:" 뒤 문장(`grep -F` 전체 줄 일치). 다만 그 문장을 **어떤 명령으로 판정하는지는 계획에 없다**(§3 H-5) |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 "PASS  Refs 있음" 3줄 — 계획 45행 U1 "Refs: P9c-briefing-calendar D18 S3.6 CR-006 원칙9" · 49행 U2 "Refs: P9c-briefing-calendar D18 CR-006 원칙5" · 54행 U3 "Refs: P9c-briefing-calendar CR-006 D17". 카드 `decisions/D17-*`·`D18-*`·`specs/S3.6-*`·`changes/CR-006.md` 존재 |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §5 "모든 조회는 `user_id` 조건을 넣는다. (CR-006) `user_id` 는 로그인 계정에서만 온다(환경변수 고정 사용자 폐지), 남의 자원은 404" — 계획 39행 "남의 일정 0"·46행 `Person.user_id == user_id`, trace 는 `user_id` 컬럼이 없으므로 "trace 의 `person_id` 가 일정 인물과 같을 것 — R-U3-2 방어 조건 재사용" 으로 일정 소유에 묶음. §1 "사용자 비밀번호·세션 토큰·쿠키 값은 로그·`agent_traces`·응답 본문·예외 메시지·증거 파일에 남기지 않는다" — 응답 필드(`id, title, scheduled_at, briefed_at, person{id, display_name}, briefing_trace_id`)에 원문(`raw_utterance`)·토큰 없음. §4 "`docker … prune`, `volume rm`, `compose down -v` 금지"·"셸에서 `DROP`/`TRUNCATE` 금지" — 마이그레이션·삭제 없음(계획 55행 "마이그레이션 없음"), 배포 반영은 사용자 SSH(계획 79행). 바깥 점검은 쿠키 없는 GET 401 뿐(데이터 전송 없음) |

## 3. 보류 소견과 조치

05-remediation.md 는 만들지 않았다(기계 검증 FAIL 0, WARN 6 은 의도된 기존 파일 확장, 나머지 WARN 1 은 아래 H-1). 아래는 계획 문서(01-plan.md)에 돌려주는 소견이다. 줄 번호는 01-plan.md 기준.

### [필수] — 닫혀야 `결과: 통과`

- **H-1 (5행 의존, 계획 5·7행)** P9b-auth `04-review.md` `결과: 완료` 가 없다. 조치: P9b 완료·사용자 확인 뒤 ① 7행 "기준 해시" 를 `gitlog.sh` 출력으로 채우고 ② verifier 가 점검표 5행을 그 해시로 재판정한다. 그전에는 `CURRENT.md` 를 바꾸지 않는다.
- **H-2 (시간대 책임이 정해지지 않음 — 39행 계약·53행 V2-1·74행 리스크)** 39행은 서버가 `from`/`to` 를 `APP_TIMEZONE` 으로 해석한다고만 하고, 74행은 "프론트는 응답 시각을 Asia/Seoul 기준으로 … 03-log 에 기준을 적는다" 로 **결정을 구현 때로 미룬다.** 그런데 ① 프론트는 `APP_TIMEZONE` 값을 알 길이 없다(응답·설정에 없음 — 하드코딩하면 서버 설정과 갈린다) ② 같은 화면의 목록 카드는 기기 시간대로 시각을 찍는다(`web/src/lib/format.ts` 1행 "서버가 준 ISO 문자열을 보기 좋게만 바꾼다(사용자 기기 시간대)") — 달력 칸은 서울, 카드 시각은 기기 기준이 된다 ③ U1∥U2 가 계약만 보고 동시에 시작하므로(43행) 계약에 없으면 두 에이전트가 각자 정한다 ④ "오늘 칸 강조"(50행)·처음 여는 달의 기준 시간대도 없다. 조치(권장): **날짜 배치는 서버 책임**으로 고정 — 응답 항목에 `local_date: "YYYY-MM-DD"`(= `scheduled_at` 을 `user_timezone()` 으로 바꾼 날짜)를 더하고, 프론트는 `scheduled_at` 으로 날짜를 계산하지 않고 `local_date` 문자열로만 칸에 넣는다. `from`/`to` 는 같은 시간대의 달력 날짜. "오늘"·처음 달은 기기 날짜(한 줄로 명시). 그러면 V2-1 은 "`local_date` 대신 `new Date(scheduled_at)` 의 기기/UTC 날짜로 배치 → KST 00:30(= 전날 15:30Z) 일정이 전날 칸으로" 로 값이 정해진다. U1 테스트에 "KST 11-30 23:59:59 → `local_date` 11-30, 12-01 00:00:00 → 12-01(그리고 11월 조회에서 제외)" 를 값으로. 다른 안(프론트가 계산)을 택하면 시간대 값을 어디서 받는지를 계약에 적는다.
- **H-3 ("브리핑됨" 의 원천이 둘 — 14행·39행·50행)** 14행은 "`briefed_at` 이 "브리핑됨" 표시" 라 하고 39행 응답은 `briefed_at` 과 `briefing_trace_id` 를 둘 다 주며 50행 배지는 어느 값을 보는지 없다. 둘은 어긋날 수 있다 — `briefed_at` 은 `get_briefing` 툴이 `schedule_id` 가 있을 때 쓰는 값이고(`app/tools/briefing.py` 148행 `schedule_row.briefed_at = now`), 화면이 여는 브리핑 카드는 compose trace 에서 온다(`app/api/read.py` `list_briefings` docstring "원천은 `agent_traces` 중 `tool_name='briefing' AND step='briefing_compose'` 행"). `briefed_at` 으로 배지를 달면 "브리핑됨" 인데 눌러도 카드가 없는 칸이 생길 수 있다. 조치: 계약에 "**브리핑됨 = `briefing_trace_id !== null`**(S3.6 "최신 브리핑 존재 여부")" 한 줄, `briefed_at` 은 응답에서 빼거나 "화면이 쓰지 않는다" 를 명시. U1 테스트에 "`briefed_at` 은 있는데 compose trace 가 없는 일정 → `briefing_trace_id` null" 과 "`briefing_trace_id` == 같은 일정의 `GET /briefings?schedule_id=` 의 `trace_id`" 를 더한다.
- **H-4 (경계 값·오류 본문이 계약에 없음 — 39행·47행)** "구간 최대 42일"·"`from>to` 422" 만 있고 ① `to - from == 42` 가 통과인지(달력 6주 = 정확히 42일이라 경계가 곧 정상 경로다) ② `from == to`(빈 구간)가 200 `[]` 인지 422 인지 ③ 순서·구간 초과 422 의 본문(프로젝트 규약 `{"detail":{"code":…}}` 인지 FastAPI 기본 목록인지) ④ 쿼리 이름 `from` 은 파이썬 예약어라 `Query(alias="from")` 가 필요하다는 점이 없다. FIX-033 (b) 규칙상 구현 에이전트는 계획에 없는 상수에서 멈춰야 하므로 왕복이 생긴다. 조치(권장): "`1 ≤ (to − from).days ≤ 42` 만 200, 그 밖(같음·역순·43 이상)은 기존 `InvalidValue` → 422 `{"detail":{"code":"invalid_value"}}`(`app/main.py` 131~132행 처리기 재사용, 새 오류 코드 0), 날짜 형식 오류는 FastAPI 기본 422" 를 39행에. 테스트는 42 → 200, 43 → 422, 같음 → 422 를 값으로. 변이 V1-4 "상한 비교 `<=` → `<`" 추가.
- **H-5 (판정 방법이 없다 — 57~59행)** 수용 기준 7구절을 **어떤 명령·어떤 기대 exit 로** 판정하는지가 계획 어디에도 없다(P9b 01-plan 223행 "## 판정 방법" 에 해당하는 절 없음, 기준선 수치 없음). 그대로면 04-review 의 증거 열을 채울 수 없다. 조치: "판정 방법" 절을 더한다 — 최소:
  - 기준선: 활성화 시점 pytest 통과 수·Vitest 수를 03-log 에 재어 적고 "실패 0·skip 0" 단언.
  - pytest `.venv/bin/python -m pytest -q -rs tests/`(이 기기 `python3` 은 anaconda — P9b 01-plan 9행 "`python3 -m pytest` … 는 `.venv/bin/python` 으로 읽는다") · `npm --prefix web run typecheck` · `npm --prefix web exec -- vitest run --root web`(registry 301행 "저장소 루트에서는 `npm --prefix web exec -- vitest run --root web`") · `npm --prefix web run build` · CI 가 도는 `npm --prefix web run e2e`(`.github/workflows/tests.yml` 244행).
  - "기존 목록 보기·`GET /briefings` 동작 불변": `git diff --stat <기준 해시>..HEAD -- tests/test_api_read_briefings.py tests/test_api_read_briefings_e2e.py tests/test_api_briefings.py web/src/__tests__/briefing.test.tsx web/e2e/briefing.spec.ts` **빈 출력** + 그 파일들 통과. (47행은 백엔드만 "무수정 통과" 라 했고 프론트 `briefing.test.tsx` 19건에는 같은 조건이 없다.)
  - "새 프론트 의존성 0": `git diff --stat <기준 해시>..HEAD -- web/package.json web/package-lock.json` 빈 출력. **52행의 Vitest "`package.json` 무변경" 시험은 지운다** — 테스트 안에는 비교할 기준이 없어 항상 통과한다(헛통과).
  - "쓰기 0": 47행의 "`agent_traces` 행 수 불변" 만으로는 수용 기준의 "쓰기" 를 못 본다 → 기존 `tests/helpers_read_api.py` `snapshot_db`·`assert_no_writes`("행 수 9개·`briefed_at` 전체·`persons.updated_at` 전체가 모두 같아야 한다")를 쓴다고 명시.
  - "남의 일정 0"·"401": 새 테스트 이름과 변이 V1-1 로.
  - 사람 점검 항목(달력 화면)은 "사람" 으로 구분.
- **H-6 (달력 탭과 기존 동작의 충돌 두 곳 — 50~52행)**
  1. **알림 클릭**: `OpenBriefingListener` 는 해시만 바꾸고(`web/src/components/AppShell.tsx` "알림 클릭 `{type:"open-briefing"}` — … 해시만 바꾼다") `BriefingScreen` 은 `#/briefings` → `#/briefings?schedule_id=N` 에서 다시 마운트되지 않는다(`web/src/App.tsx` `route.name === 'briefings' && <BriefingScreen />`). 탭 상태가 화면 안 state 면 **달력 탭을 보던 중 알림을 누르면 달력에 머물러 강조된 브리핑이 안 보인다.** 51행 "지금처럼 목록 보기로 연다" 는 처음 여는 경우만 덮는다. 조치: "`schedule_id` 쿼리 값이 (새로) 생기면 탭을 목록으로 바꾼다" 한 줄 + U2 테스트 "달력 탭에서 해시에 `?schedule_id=` 가 붙으면 목록 탭·강조 항목이 보인다".
  2. **목록 탭일 때 요청 불변**: `web/src/__tests__/briefing.test.tsx` 의 가짜 fetch 는 표에 없는 요청에 `throw new Error('예상하지 못한 요청: …')` 한다. 달력이 마운트 때(탭 비활성 포함) `getSchedules` 를 부르면 기존 19건이 깨진다. 조치: 50행에 "`getSchedules` 는 달력 탭이 활성일 때만(목록 탭 기본 상태의 요청은 지금과 같다 — `GET /api/briefings` 뿐)" + U2 테스트 "목록 탭에서 `/api/schedules` 호출 0". 변이 V2-3 "달력을 항상 마운트" → 그 테스트.

### [권고]

- **R-1 (P9b 구현 뒤 낡은 전제 — 12·13·83행, 산출물 36행)** 계획은 P9b 전에 쓰여 사실이 어긋난다: `GET /briefings` 는 지금 `app/api/routes.py` 549~559행(12행은 488-497), API 라우트는 17개(13행은 "12개" — `.venv/bin/python` 으로 `create_app().routes` 열거: `/chat/history`·`/auth/*` 4개 추가). 반영할 P9b 산출물: ① 라우트는 `user: User = Depends(current_user)`(`app/auth/deps.py`)를 받고 `user.id`(Text, uuid4 hex)를 넘긴다 ② 테스트 클라이언트는 `tests/auth_helpers.py` `logged_in_client(app, db_session)`·남의 데이터는 `make_user`/`Person(user_id=…)` ③ **`tests/test_auth_required_routes.py` `_MUST_REQUIRE_LOGIN` 에 `("GET", "/schedules")` 를 더하고**(주석 "보호 대상 13개" 도) 그 파일을 "고침" 목록에 넣는다 — 열거 시험 자체는 새 라우트를 자동으로 잡지만 이 집합은 "라우트가 사라지면 알리는" 쪽이라 손으로 넣어야 한다. **깨지는 기존 단언은 0건으로 확인했다**(라우트 수·경로 집합을 숫자로 단언하는 테스트 없음 — `grep -rnE "routes|paths" tests --include="*.py"` 에 `len(`·`== N` 일치 0; `tests/helpers_read_api.py` `_COUNTED_MODELS` 는 모델 고정 목록). 닫힌 목록 = "깨짐 0 · 확장 1(`_MUST_REQUIRE_LOGIN`)" 을 계획에 적고, 목록 밖이 깨지면 멈추고 보고. 탐침(이 검증에서 실행): 로그인 의존성이 401 을 던지는 라우트에 필수 쿼리 `from`·`to` 를 빼거나 형식을 틀려도 응답은 `401 401` — 열거 시험이 쿼리 없이 호출해도 401 이 먼저다(단, 날짜 파싱을 `current_user` 보다 먼저 도는 별도 의존성으로 빼면 순서가 바뀔 수 있으니 쿼리 매개변수로 직접 받는다).
- **R-2 (조회 쿼리 — 46·48행)** ① LEFT JOIN 에서 `rn == 1`·`person_id` 일치 조건은 `WHERE` 가 아니라 **조인 조건**에 둔다(WHERE 에 두면 브리핑 없는 일정이 사라진다 — "없는 일정 null" 테스트가 잡지만 계획 문장에 명시). ② `list_briefings` 의 `ranked` 는 전 계정의 compose trace 전체에 창 함수를 건다(`agent_traces` 에 `tool_name`/`step` 인덱스 없음, `app/db/models.py` 278행 인덱스는 `session_id, created_at` 뿐) — 달력은 구간 일정 id 로 먼저 좁힌 뒤 순위를 매기는 편이 낫다(시연 규모에서는 무해, 결정만 기록). ③ 변이 추가: V1-5 "trace `person_id` 일치 조건 제거 → 남의 인물 id 로 조작한 trace 가 내 일정에 `briefing_trace_id` 를 만드는 테스트"(R-U3-2 재사용이라면 그 시험도 재사용). ④ "LLM 0" 은 구조로 — 새 라우트의 의존성에 `get_judge`·`get_proposer`·`get_briefing_composer`·`get_notifier` 가 없음을 단언하면 값으로 남는다. ⑤ 일정 격리 시험을 `tests/test_user_isolation.py` 형식(계정 둘 `World`)으로도 1건 두면 D18 격리 묶음에서 함께 돈다.
- **R-3 (브리핑 카드 재사용 방법 — 35·50행)** `BriefingItem` 은 `web/src/screens/BriefingScreen.tsx` 89행의 **export 되지 않은 내부 함수**이고 `runState`·`onRun` 을 화면에서 받는다. 새 파일 `components/BriefingCalendar.tsx` 가 이것을 쓰려면 ① 별도 파일로 옮기거나(산출물 목록에 없음) ② `BriefingScreen` 이 렌더 함수를 넘겨야 한다 — 그대로 import 하면 `BriefingScreen ↔ BriefingCalendar` 순환 import 다. 방법을 한 줄로 고정. 또 재사용 카드에는 "지금 브리핑" 버튼이 딸려 온다: 달력에서 누르면 `load()` 는 목록만 다시 읽어 **달력의 배지·날짜 상세가 낡는다** → "성공 뒤 그달 `getSchedules` 와 그날 상세를 다시 읽는다" 또는 "달력 상세의 카드에는 버튼을 두지 않는다" 중 하나를 적는다. 브리핑이 없는 일정에는 버튼을 새로 달지 않는다(30행 "생성 버튼 추가" 제외와 일치)는 것도 명시.
- **R-4 (접근성·모바일 — 50행, 결정 D)** 접근성 문장이 없다: 날짜 칸은 `<button>`(키보드 선택), `aria-label` 에 날짜·일정 수, 오늘은 `aria-current="date"`, 선택된 날 `aria-pressed`, 이전/다음 달 버튼 `aria-label`. 테스트가 역할·이름으로 칸을 찾게 하면 계약이 된다. 결정 D 이유 "모바일 폭에서도 칸이 넘치지 않는다" 는 근거가 약하다 — 360px 폭에서 7열이면 칸이 약 45px 라 제목 2줄은 `truncate`(`min-w-0`) 없이는 넘친다. jsdom 은 폭을 못 재므로 "사람 점검: 360px 폭에서 가로 스크롤 0" 을 U3 사람 점검에 넣고, 넘치면 좁은 폭에서 점 표시(D (ii))로 물러나는 것까지만(원칙5 "UI에 시간을 쓰지 않는다").
- **R-5 (일정·배포 — 8·55·73행)** 영향 0 의 근거는 선다: ① 활성화 전에는 `stage-gate.sh` 가 제품 코드 쓰기를 막는다 ② 서버는 브랜치가 아니라 해시에 고정된다(`docs/user-setup/13-user-todo-deploy.md` 63행 "`git fetch origin && git checkout 4be331b`") ③ 마이그레이션 없음. 다만 계획에 **판단 시점이 없다**("시간이 남을 때만"). P9b 는 사용자 SSH(U7)·시연 계정(U8)·04-review·완성 확인이 남았고 P9c 는 그 뒤 U1·U2 각각 구현 + verifier 리뷰·변이 + U3 재배포(사용자 SSH 한 번 더)·사람 점검이다 — 목표 11-17(화) 저녁까지 넣으려면 평가 전날 재배포가 된다. 권고: "○일 ○시까지 P9b `결과: 완료`·사용자 확인이 없으면 평가 뒤로" 를 한 줄로 박고(값은 사용자·메인), **"서버 해시는 P9c 04-review `결과: 완료` 뒤에만 P9c 커밋으로 옮긴다"**(U1 만·U2 만 올라간 중간 해시를 배포하면 달력 탭이 404 를 부른다)를 U3 에 적는다.
- **R-6 (날짜 상세의 요청 수 — 50행)** 날짜를 누르면 브리핑 있는 일정마다 `getBriefings(scheduleId)` 1회 — 하루 k건이면 k요청. 시연 규모에서는 무해하나 "하루 일정 수만큼(상한 없음)" 임을 계획에 적고 테스트에서 호출 수를 값으로 단언한다. 응답 행 수 상한도 구간 길이뿐임(결정 A)을 한 줄로.
- **R-7 (하네스)** `verify-plan.sh` 31·62·68행 정규식이 `P9b-…`·`P9c-…`·`P4b-…` 형태 id 를 못 읽어 의존·게이트 검사가 조용히 빠진다(1절). 이 패키지 밖 FIX 후보.

### 사용자만 정할 수 있는 것
- 평가(11-18) 전날 재배포를 감수하고 P9c 를 배포본에 넣을지, 넣는다면 포기 시점(R-5). 계획 8행은 "못 들어가면 평가 뒤" 만 정했다.
- 배포 반영 SSH·배포 URL 로그인 뒤 달력 화면 사람 점검(계획 79행 — 이미 사용자 몫으로 분리됨).
- 결정 A~E 는 상수·표시 취향으로 위임 범위("권장안 채택") 안이라고 본다. 그중 C(기본 보기)·D(칸당 표시)·E(주 시작 요일)는 화면 취향이라 완성 확인 때 바꿔 달라고 해도 비용이 작다. H-2(시간대)·H-3(배지 원천)·H-4(경계)는 사용자 결정이 아니라 계약 누락이다 — 메인이 권장안으로 채우면 된다(해외 브라우저에서의 표시 기준만 사용자에게 한 줄 고지).

## 4. 결정
결과: 보류

- 사유: 점검표 5행(선행 `P9b-auth` 04-review 미완료 — 활성화 조건) + [필수] H-2~H-6(계약·판정 방법 누락 — 계획 문서 개정 필요). 점검표 1~4·6~8 은 통과.
- 재검증 조건: 01-plan 개정(H-2~H-6 반영) → P9b `결과: 완료` 커밋 뒤 기준 해시 기입(H-1) → verifier 재검증. H-2~H-6 은 P9b 완료를 기다리지 않고 지금 고칠 수 있다.
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)
