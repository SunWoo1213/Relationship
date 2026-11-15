# P9c-briefing-calendar · 계획 (01-plan)

상태: 개정 1(2026-11-16, architect — verifier 02-plan-verify 사전 검증 보류 [필수] H-2~H-6·[권고] R-1~R-7 반영, P9b-auth 구현(U1~U6, HEAD `1723a84`) 뒤의 실제 코드로 전제를 다시 맞춤. 처리표는 맨 끝 "개정 이력") — **P9b-auth 04-review 완료 뒤에만 활성화**(한 번에 활성 하나). 사용자 결정 표는 권장안을 기본값으로 채택(사용자 지시 2026-11-15) | 담당: backend-agent(sonnet, U1) · frontend-agent(sonnet, U2) · 메인 세션(U3) · 사용자(U3 배포 반영 SSH·사람 점검) · 검증 verifier(fable) | 작성: 2026-11-15, 개정 2026-11-16
태그 — 패키지: P9c-briefing-calendar · 닫는 검증: — · 기대는 결정: D18(로그인 사용자 기준 조회) · 구현하는 명세: S3.6(보기 보충) · 관련 원칙: 원칙5(폐지 문장) 원칙7 원칙9 · 출처 CR: CR-006 변경 항목 2
의존: **P9b-auth 04-review `결과: 완료`**(미충족 — 조회가 로그인 사용자의 `user_id` 위에서 돈다. **P9b `결과: 완료` 커밋 뒤 메인이 그 해시를 여기에 채우고 verifier 가 점검표 5행을 재판정한다**, H-1) · P8-frontend(완료) · P6-briefing(완료) · P4 게이트(P4b 완료 2026-09-23).

- **기준 해시**: **P9b `결과: 완료` 뒤 메인이 채운다**(`bash .claude/scripts/gitlog.sh P9c P9b CR-006` 출력으로, H-1). 아래 `<기준>` 은 그 해시.
- **기준선**: 활성화 시점에 메인이 pytest 통과 수(`.venv/bin/python -m pytest -q -rs tests/`)·Vitest 수(`npm --prefix web exec -- vitest run --root web`)를 재어 03-log 에 적는다. 단위 증거는 "실패 0 · skip 0" 을 단언한다. 판정은 **Mac 로컬**에서 한다(Windows CI 는 확인하지 않음 — 사용자 지시 2026-11-15).
- **일정(R-5)**: 평가(2026-11-18 수) 전에는 P9b 가 우선(사용자 SSH 반영·시연 계정·04-review·완성 확인이 남음). **포기 시점: 2026-11-17(화) 12:00 까지 P9c U1·U2 가 verifier 리뷰를 통과하지 못하면 평가 전 배포에서 뺀다.** **서버 해시는 P9c 04-review `결과: 완료` 뒤에만 P9c 커밋으로 옮긴다**(U1 만·U2 만 들어간 중간 해시를 올리면 달력 탭이 404 를 부르거나 API 만 남는다). **못 들어가면 배포본은 `4be331b`(P9b 로그인만 반영 — `docs/user-setup/13-user-todo-deploy.md` 63행) 그대로**이고 브리핑 화면은 지금의 목록 보기로 시연하며, 이 패키지는 평가 뒤 이어간다.

### 코드에서 확인한 사실 (P9b 구현 뒤 HEAD `1723a84` 기준으로 다시 맞춤, R-1)

1. `GET /briefings`(`app/api/routes.py:549-559` → `app/api/read.py` `list_briefings`)는 `user: User = Depends(current_user)` 를 받아 `user.id` 로 조회하고, **`briefing_compose` trace 가 있는 일정만**, `scheduled_at >= now - BRIEFINGS_LOOKBACK_DAYS`, 상한 `BRIEFINGS_LIMIT`, 일정마다 최신 1행. → 브리핑이 아직 없는 일정(예정일)과 임의의 달(과거·먼 미래)을 보일 수 없다.
2. API 라우트는 **17개**(P9b 가 `/chat/history`·`/auth/signup`·`/auth/login`·`/auth/logout`·`/auth/me` 를 더함, verifier 탐침 `evidence/20261116-0151-planverify-probe-401-routes.txt`). 일정 목록 엔드포인트는 없다. 인물 카드의 `upcoming_schedules` 는 인물 한 명 것.
3. 라우트 규약(P9b): 인자 `user: User = Depends(current_user)`(`app/auth/deps.py`), 값은 `user.id`(Text, uuid4 hex). 로그인 의존성의 401 은 필수 쿼리 누락·형식 오류보다 **먼저** 나온다(verifier 탐침 `401 401`) — 단 날짜 파싱을 `current_user` 보다 먼저 도는 별도 의존성으로 빼면 순서가 바뀔 수 있으므로 **쿼리 매개변수로 직접 받는다**.
4. `tests/test_auth_required_routes.py` 는 `app.routes` 를 열거해 미로그인 401 을 단언하므로 새 라우트가 자동으로 걸린다. 다만 `_MUST_REQUIRE_LOGIN`(45~59행, "보호 대상 13개" — 124행 주석)은 "라우트가 사라지면 알리는" 고정 집합이라 **손으로 `("GET", "/schedules")` 를 더해야 한다**. 같은 파일 164행 `test_every_api_route_declares_current_user_dependency` 가 의존성 선언도 본다.
5. 테스트 도우미(P9b U3a): `tests/auth_helpers.py` `make_user(session, user_id, username)`·`make_ctx(...)`·`logged_in_client(app, session_or_factory, user_id, ...)`(쿠키 이름은 `cookie_name()` 에서)·`committed_login(...)`(실제 커밋형). 격리 묶음 `tests/test_user_isolation.py` 의 `World` 픽스처(77·209행 — 계정 둘). 쓰기 0 판정 `tests/helpers_read_api.py` `snapshot_db`·`assert_no_writes`(9모델 행 수·`briefed_at` 전체·`persons.updated_at` 전체가 같아야 함).
6. `schedules(id, person_id, title, scheduled_at, briefed_at)` — 스키마로 충분. **스키마 변경 0.** `briefed_at` 은 `get_briefing` 툴이 `schedule_id` 가 있을 때 쓰는 값(`app/tools/briefing.py:148`)이고, 화면이 여는 브리핑 카드는 compose trace 에서 온다 — 둘은 어긋날 수 있다(H-3).
7. 사용자 시간대는 `app/settings.py:484` `user_timezone()`(`APP_TIMEZONE`, 기본 Asia/Seoul). 프론트는 이 값을 모른다(응답·설정에 없음). 목록 카드의 시각은 기기 시간대로 찍는다(`web/src/lib/format.ts` 1행) — H-2.
8. 오류 처리: `InvalidValue` → 422 `{"detail":{"code":"invalid_value"}}`(`app/main.py:131-132` 처리기, 193행 등록). 새 오류 코드를 만들지 않는다.
9. 프론트: `web/src/App.tsx` 가 관문(`/auth/me`) 뒤 `route.name === 'briefings' && <BriefingScreen />` 를 렌더한다 — `#/briefings` → `#/briefings?schedule_id=N` 에서 **다시 마운트되지 않는다**. 알림 클릭은 `OpenBriefingListener`(`AppShell.tsx`)가 해시만 바꾼다. `BriefingScreen.tsx` 는 `useScheduleIdParam()`(157행)·`getBriefings()`(171행)·`getBriefings(scheduleId)`(185행)를 쓰고, 카드 `BriefingItem`(89행)은 **export 되지 않은 내부 함수**이며 `runState`·`onRun` 을 받는다(R-3). 쓰는 shadcn/ui: `button`·`card`·`badge`·`collapsible`·`skeleton`·`tabs`·`sheet`·`sonner`(`web/src/components/ui/`) — 달력 컴포넌트는 없다.
10. `web/src/__tests__/briefing.test.tsx`(19건)의 가짜 fetch 는 표에 없는 요청에 `throw new Error('예상하지 못한 요청: …')` 한다 → 목록 탭 기본 상태에서 새 요청이 생기면 19건이 깨진다(H-6 ②). E2E(`web/e2e/fixtures.ts`)도 `/api/**` 를 표로 답한다. CI 는 `npm --prefix web run e2e`(`.github/workflows/tests.yml` 244행).
11. `agent_traces` 에 `tool_name`/`step` 인덱스는 없다(`app/db/models.py` 278행 인덱스는 `session_id, created_at` 뿐) — `list_briefings` 의 순위 창 함수는 전 계정 compose trace 전체에 걸린다(R-2 ②).

→ **새 엔드포인트 1개가 필요**하다(사실 1·2). 기존 `GET /briefings` 의 창·상한을 바꾸면 목록 보기 동작이 바뀌므로 건드리지 않는다.

## 목표

CR-006 변경 항목 2 — 사용자 원문 "또 추가하고 싶은 기능은 브리핑 날짜를 달력형태로도 볼 수 있게 기능을 추가해줘". 브리핑 화면에 **목록 보기 / 달력 보기 전환**을 두고, 월 달력에 그달 일정을 날짜별로 표시하며(브리핑이 만들어진 일정은 구분), 날짜를 누르면 그날의 일정과 브리핑이 보이게 한다. 읽기 전용(LLM 0·trace 0·쓰기 0)이고 기존 목록 보기는 그대로다. 예: 11월 달력의 18일 칸에 "김 대리 점심 ●(브리핑됨)" 이 보이고, 누르면 그 아래에 지금 목록 보기와 같은 모양의 브리핑 카드(버튼 없음)가 열린다.

## 범위

- 포함: 월 범위 일정 조회 API(U1) · 브리핑 화면 목록/달력 전환·월 이동·날짜 선택(U2) · 문서·registry·배포 반영(U3).
- 이 패키지에서 하지 않는 것:
  - **주·일 보기, 일정 추가·수정·드래그** — 일정은 대화(`add_schedule`)로만 만든다. 달력은 보기 전용.
  - **새 프론트 의존성(달력 라이브러리)** — 7열 그리드는 CSS 로 충분하고 번들·검증 부담을 늘리지 않는다(결정 B).
  - **브리핑 생성·재생성 버튼 추가, 달력 상세의 "지금 브리핑" 버튼** — 달력은 읽기 전용(R-3 확정). 목록 탭의 기존 "지금 브리핑" 은 그대로. 브리핑이 없는 일정에 버튼을 새로 달지 않는다. 원칙7 경계(제안 한 줄) 무관.
  - **`GET /briefings` 의 창·상한 변경** — 목록 보기 불변(수용 기준).
  - **`tests/helpers_read_api.py` `_COUNTED_MODELS` 확장** — P9b 인계 권고(새 테이블 미집계), 이 패키지 범위 밖.

## 산출물 (파일 경로)

- 새: `tests/test_api_schedules_range.py` · `web/src/components/BriefingCalendar.tsx` · `web/src/components/BriefingCard.tsx`(R-3 — `BriefingItem` 을 옮겨 export) · `web/src/__tests__/calendar.test.tsx` · `docs/wiki/packages/P9c-briefing-calendar/tests.md`·`03-log.md`·`evidence/`
- 고침(registry 기존 행 확장 — 새 함수·라우트를 기존 파일에 더하는 것이라 중복 구현 아님): `app/api/read.py`(`list_schedules_in_range`) · `app/api/routes.py`(`GET /schedules`) · `app/api/schemas.py`(`ScheduleRangeItemOut`) · `web/src/api/client.ts`·`web/src/api/types.ts`(`getSchedules(from, to)`·타입) · `web/src/screens/BriefingScreen.tsx`(탭 전환 · `BriefingItem` → `BriefingCard` import) · `tests/test_auth_required_routes.py`(`_MUST_REQUIRE_LOGIN` 에 `("GET", "/schedules")`, 124행 주석 "13개" → 14개) · `tests/test_user_isolation.py`(일정 격리 1건, R-2 ⑤) · `docs/wiki/registry.md`

### 깨뜨릴 기존 단언 — 닫힌 목록(P9b 교훈, R-1)
verifier 확인(`grep -rnE "routes|paths" tests --include="*.py"` 에 `len(`·`== N` 일치 0; `_COUNTED_MODELS` 는 모델 고정 목록): **깨짐 0 · 확장 1**(`tests/test_auth_required_routes.py` `_MUST_REQUIRE_LOGIN` + 같은 파일 124행 주석의 수). `web/src/__tests__/briefing.test.tsx`·`web/e2e/briefing.spec.ts`·`tests/test_api_read_briefings*.py`·`tests/test_api_briefings.py` 는 **diff 0**(판정 #6). 목록 밖이 깨지면 멈추고 보고한다.

### API 계약 (U1 ↔ U2 — 동시에 시작하므로 여기서 고정)
`GET /schedules?from=YYYY-MM-DD&to=YYYY-MM-DD`(로그인 필수 — `user: User = Depends(current_user)`, 쿼리는 `Query(alias="from")`·`Query(alias="to")` 로 **직접** 받는다, 사실 3)

- 날짜 해석: `from`·`to` 는 **사용자 시간대(`user_timezone()`)의 달력 날짜**. 구간은 `[from 00:00, to 00:00)` 를 그 시간대로 바꾼 반열린 구간.
- 구간 규칙(H-4): **`1 ≤ (to − from).days ≤ 42` 만 200**. 그 밖(같음·역순·43 이상)은 기존 `InvalidValue` → **422 `{"detail":{"code":"invalid_value"}}`**(새 오류 코드 0). 날짜 형식 오류·누락은 FastAPI 기본 422(단 미로그인이면 401 이 먼저).
- 응답 200 `[{id, title, scheduled_at, local_date, person:{id, display_name}, briefing_trace_id|null}]`, 정렬 `scheduled_at, id`.
  - **`local_date: "YYYY-MM-DD"`**(H-2) = `scheduled_at` 을 `user_timezone()` 으로 바꾼 날짜. **프론트는 날짜 칸 배치에 이 문자열만 쓴다**(`scheduled_at` 으로 날짜를 계산하지 않는다).
  - **"브리핑됨" = `briefing_trace_id !== null`**(H-3, S3.6 "최신 브리핑 존재 여부"). `briefing_trace_id` 는 `list_briefings` 와 같은 원천(compose trace, 일정마다 최신 1행)의 `trace_id`. **`briefed_at` 은 응답에 넣지 않는다.**
- 남의 일정 0. 쓰기·trace·LLM 0. 행 수 상한은 구간 길이(최대 42일)뿐(결정 A, R-6).
- **"오늘 칸"·처음 여는 달(H-2 확정)**: 프론트는 **기기 날짜**를 쓴다(브라우저 `new Date()` 의 연·월·일). 한계: 기기 시간대가 서버 시간대(Asia/Seoul)와 다르면 "오늘 칸" 이 하루 어긋날 수 있다 — 일정의 날짜 배치는 서버 `local_date` 라 어긋나지 않는다. (`today` 를 응답에 더하는 안은 매 호출 응답 모양이 바뀌어 택하지 않는다.) 리스크·사용자 고지 절에 한 줄.

## 작업 단위

순서: **U1 ∥ U2**(U2 는 위 계약 + 목 응답, 파일 겹침 없음) → U3. 각 단위 커밋 시점에 **전체 pytest·Vitest 가 통과 가능한지** 위 "닫힌 목록" 으로 따졌다 — U1 은 백엔드 테스트 확장 1(`_MUST_REQUIRE_LOGIN`)만, U2 는 `briefing.test.tsx` 무수정(목록 탭 요청 불변, H-6 ②). 공통 규칙: 자동 수정 명령(`ruff --fix` 등) 금지 · 변이 실행에 커밋형 테스트(`committed_login` 을 쓰는 것)를 넣지 않는다 · 계획에 없는 상수·정렬·상한이 필요하면 구현 전에 멈추고 보고(FIX-033 (b)).

- [ ] U1 **[backend-agent] 월 범위 일정 조회 API `GET /schedules`** / Refs: P9c-briefing-calendar D18 S3.6 CR-006 원칙9 / 의존: P9b-auth 완료
  - `list_schedules_in_range(session, user_id, start_date, end_date, tz)`: `schedules ⋈ persons` 에 `Person.user_id == user_id`, `start ≤ scheduled_at < end`(tz 로 바꾼 경계). 먼저 구간 일정 id 로 좁힌 뒤(R-2 ②) 그 일정들의 compose trace(`tool_name='briefing' AND step='briefing_compose'`)에 일정마다 최신 1행 순위를 매겨 **LEFT JOIN** — **`rn == 1` 과 trace `person_id` == 일정 `person_id`(R-U3-2 방어 조건) 는 `WHERE` 가 아니라 조인 조건에 둔다**(WHERE 에 두면 브리핑 없는 일정이 사라진다, R-2 ①). `local_date` 는 `scheduled_at.astimezone(tz).date().isoformat()`. 상한은 구간 길이로만(결정 A).
  - 라우트: `@router.get("/schedules", response_model=list[ScheduleRangeItemOut])`, 인자 `from_: date = Query(alias="from")`·`to: date = Query(alias="to")`·`user: User = Depends(current_user)`·`session`. 구간 규칙 위반은 `InvalidValue`. **새 라우트의 의존성에 `get_judge`·`get_proposer`·`get_briefing_composer`·`get_notifier` 가 없다**(LLM 0 을 구조로, R-2 ④).
  - `tests/test_auth_required_routes.py`: `_MUST_REQUIRE_LOGIN` 에 `("GET", "/schedules")`, 124행 주석 "13개" → "14개"(확장 1 — 닫힌 목록).
  - 테스트 `tests/test_api_schedules_range.py`(클라이언트는 `logged_in_client(app, db_session)`, 남의 데이터는 `make_user`·`Person(user_id=…)`, 시간대 Asia/Seoul):
    - 경계·`local_date`(H-2 값): `from=2026-11-01&to=2026-12-01` 에서 KST `2026-11-01 00:00:00` 일정 포함·`local_date` `2026-11-01` · KST `2026-11-30 23:59:59` 포함·`local_date` `2026-11-30` · KST `2026-12-01 00:00:00` **제외**(다음 조회 `from=2026-12-01&to=2026-12-02` 에서 `local_date` `2026-12-01`) · **KST `2026-11-15 00:30`(= `2026-11-14T15:30:00Z`) 일정의 `local_date` 가 `2026-11-15`**.
    - 구간(H-4 값): `to−from` = 42일 → 200 · 43일 → 422 `{"detail":{"code":"invalid_value"}}` · 같음 → 422 같은 본문 · 역순 → 422 같은 본문 · `from=2026-13-01` → 422(FastAPI 기본) · 쿼리 없이 미로그인 → 401(로그인 우선).
    - 브리핑됨(H-3): compose trace 있는 일정에 `briefing_trace_id` · **그 값 == 같은 일정 `GET /briefings?schedule_id=` 의 `trace_id`** · **`briefed_at` 은 있는데 compose trace 가 없는 일정 → `briefing_trace_id` null** · 같은 일정에 trace 2개면 최신 것 · **남의 인물 id 로 조작한 compose trace 가 내 일정에 `briefing_trace_id` 를 만들지 않는다**(R-2 ③) · 응답 항목 키 집합에 `briefed_at` 없음.
    - 격리·쓰기 0: 남의 일정 0 · `snapshot_db` 를 호출 전후로 찍어 `assert_no_writes`(H-5) · 라우트 의존성에 LLM 계열 의존성 없음(R-2 ④).
    - 기존 `GET /briefings` 테스트 무수정 통과(판정 #6).
  - `tests/test_user_isolation.py` 에 `World` 형식 1건: A 쿠키로 `GET /schedules` 에 B 의 일정 0(R-2 ⑤).
  - 변이 → 잡는 테스트: V1-1 `user_id` 조건 제거 → 남의 일정 테스트 · V1-2 끝 경계 `<` → `<=` → 12-01 00:00 제외 테스트 · V1-3 trace 조인에서 최신 1행 조건 제거 → 중복 행 테스트 · **V1-4 상한 비교 `<= 42` → `< 42` → 42일 200 테스트**(H-4) · **V1-5 trace `person_id` 일치 조건 제거 → 조작 trace 테스트**(R-2 ③) · V1-6 `rn == 1` 을 WHERE 로 옮김 → 브리핑 없는 일정 null 테스트(R-2 ①) · V1-7 `local_date` 를 UTC 날짜로 → 00:30 KST 테스트(H-2). 변이는 저장소 밖 사본 또는 작업 트리 Edit → FAIL 기록 → 되돌림(`git diff` 증거). 커밋형 테스트는 변이 실행 대상에 넣지 않는다.

- [ ] U2 **[frontend-agent] 브리핑 화면 목록/달력 전환과 달력 컴포넌트** / Refs: P9c-briefing-calendar D18 CR-006 원칙5 / 의존: P9b-auth 완료(U1 과 동시)
  - 카드 재사용(R-3 확정): `BriefingScreen.tsx` 89행 `BriefingItem` 을 **`web/src/components/BriefingCard.tsx` 로 옮겨 export** 한다(`BriefingCard({record, highlighted?, runState?, onRun?})` — `onRun` 이 없으면 "지금 브리핑" 버튼과 실행 상태 줄을 그리지 않는다). `BriefingScreen` 은 이 컴포넌트에 지금과 같은 `runState`·`onRun` 을 넘겨 **목록 탭 DOM 을 바꾸지 않는다**(`briefing.test.tsx` diff 0 으로 증명). `BriefingCalendar` 는 `BriefingCard` 를 `onRun` 없이 쓴다 → 달력 상세에는 버튼이 없다(읽기 전용). `BriefingScreen ↔ BriefingCalendar` 순환 import 없음(둘 다 `components/BriefingCard` 를 import).
  - `BriefingScreen` 위에 shadcn `tabs` 로 "목록 / 달력"(기본 목록 — 결정 C). **`getSchedules` 는 달력 탭이 활성일 때만 호출**(달력 컴포넌트는 탭 활성 시에만 마운트 — 목록 탭 기본 상태의 요청은 지금과 같이 `GET /api/briefings` 뿐, H-6 ②). **`schedule_id` 쿼리 값이 (새로) 생기면 탭을 목록으로 바꾼다**(알림 클릭 — `BriefingScreen` 이 다시 마운트되지 않으므로 `useScheduleIdParam()` 값 변화에 반응, H-6 ①).
  - 달력: 월 제목 + 이전/다음 달 버튼(`aria-label` "이전 달"·"다음 달") + 요일 머리(일요일 시작 — 결정 E) + 7열 CSS 그리드(6주 = 42칸, 조회 `from` = 첫 칸 날짜, `to` = 첫 칸 + 42일). 칸은 `<button>`(키보드 선택), `aria-label` 에 날짜와 일정 수, 오늘 칸 `aria-current="date"`, 선택된 날 `aria-pressed="true"`(R-4). 칸마다 그날 일정 제목(최대 2개 + "외 N", 결정 D, `truncate`·`min-w-0`)과 브리핑됨 표시(`badge` — **`briefing_trace_id !== null`** 일 때만, H-3). 날짜 배치는 **응답 `local_date` 문자열로만**(H-2). 오늘 칸·처음 달은 기기 날짜(계약 절).
  - 날짜를 누르면 아래에 그날 일정 목록, 브리핑 있는 일정마다 `getBriefings(scheduleId)` 1회 → `BriefingCard`(버튼 없음). **요청 수 = 그날 브리핑 있는 일정 수(상한 없음)**(R-6). 월이 바뀔 때만 `getSchedules` 재호출(캐시 없음 — P8 결정 I).
  - 새 의존성 0(`web/package.json`·`package-lock.json` diff 0 — 판정 #7). **Vitest 안에 "`package.json` 무변경" 시험은 두지 않는다**(비교 기준이 없어 헛통과, H-5).
  - 테스트 `web/src/__tests__/calendar.test.tsx`(역할·이름으로 칸을 찾는다 — R-4):
    - 전환 · 목록 탭에서 `/api/schedules` 호출 0(가짜 fetch 의 호출 목록으로, H-6 ②) · 달력 탭 활성 시 `from`/`to` 가 6주 범위로 1회 호출.
    - 그달 일정이 `local_date` 칸에 — **`scheduled_at: "2026-11-14T15:30:00Z"`, `local_date: "2026-11-15"` 인 항목이 15일 칸에**(기기 시간대와 무관, H-2) · 브리핑됨 배지는 `briefing_trace_id` 가 있는 항목에만 · 날짜 클릭 → 그날 목록 + `getBriefings` 호출 수 = 그날 브리핑 있는 일정 수(R-6) · 상세 카드에 "지금 브리핑" 버튼 없음(R-3) · 이전/다음 달에 `from`/`to` 가 바뀐 호출 · 일정 0 달은 빈 칸 · 오늘 칸에 `aria-current="date"` · 선택 칸 `aria-pressed`.
    - **달력 탭을 보던 중 해시에 `?schedule_id=N` 이 붙으면 목록 탭과 강조 항목이 보인다**(H-6 ①).
  - 변이 → 잡는 확인: V2-1 날짜 배치를 `local_date` 대신 `new Date(scheduled_at)` 의 기기/UTC 날짜로 → `2026-11-14T15:30:00Z` 항목이 14일 칸으로 가서 15일 칸 테스트 실패(H-2) · V2-2 월 이동 시 `to` 계산 오류 → 호출 인자 테스트 · **V2-3 달력을 탭과 무관하게 항상 마운트 → "목록 탭에서 `/api/schedules` 호출 0" 테스트 + 기존 `briefing.test.tsx`("예상하지 못한 요청")**(H-6 ②) · V2-4 `schedule_id` 변화에 탭 전환 제거 → 알림 테스트(H-6 ①) · V2-5 배지 조건을 항상 참 → 배지 테스트(H-3).

- [ ] U3 **[메인 세션 + 사용자] registry·문서·배포 반영·사람 점검** / Refs: P9c-briefing-calendar CR-006 D17 / 의존: U1·U2 커밋과 각 verifier 리뷰 통과 + **P9c 04-review `결과: 완료`**(R-5)
  - registry 행(새 라우트·함수·컴포넌트, 기존 행 확장 6건 비고) · `docs/RUNNING.md` 한 줄.
  - 배포 반영(사용자 SSH — P9b U7 과 같은 명령, 마이그레이션 없음, `.env` 변경 없음): **P9c 04-review `결과: 완료` 뒤에만** 서버 해시를 P9c 커밋으로 옮긴다(R-5). 포기 시점을 넘기면 반영하지 않고 `4be331b` 를 유지.
  - 바깥 GET(본문 없음, security §4): 스크래치 스크립트 `u3-public-401.sh`(`curl -s -o /dev/null -w '%{http_code}' '<URL>/api/schedules?from=2026-11-01&to=2026-12-01'` → 401).
  - 사람 점검(사용자, 배포 URL 로그인 뒤): 시연 계정 달력에 일정·브리핑 배지 · 날짜 클릭 상세 · **360px 폭에서 가로 스크롤 0**(넘치면 좁은 폭에서만 점 표시 — 결정 D (ii) — 로 물러나는 것까지만, 원칙5 "UI에 시간을 쓰지 않는다", R-4) · 알림 클릭 시 목록 탭으로.

## 판정 방법 (H-5)

명령은 저장소 루트에서, 증거는 `python3 .claude/scripts/save_evidence.py P9c-briefing-calendar <이름> -- <명령>`(FIX-034). 이 기기의 `python3` 은 anaconda 라 테스트·스크립트 실행은 **`.venv/bin/python`**. 따옴표·`|`·`$`·`%` 가 든 안쪽 명령은 스크래치패드 `<SCR>/<이름>.sh` 로 Write 해 `-- bash <SCR>/<이름>.sh`(래퍼가 인자를 공백으로 이어 `bash -c` 로 돌려 따옴표가 사라진다). 재귀 grep 은 `grep -rnE … --include=…` 로 쓰고 "기대 exit 1(일치 없음), exit 2 는 실패" 로 읽는다. 판정은 Mac 로컬.

| # | 수용 기준 구절 | 판정 | 명령 / 점검 | 실행 | 단위 |
|---|---|---|---|---|---|
| 1 | 브리핑 화면에서 목록 보기와 달력 보기를 전환할 수 있다 | 기계 + 사람 | `… u2-vitest -- npm --prefix web exec -- vitest run --root web` 의 `calendar.test.tsx` 전환 시험 · U3 사람 점검 | 에이전트 + 사용자 | U2·U3 |
| 2 | 월 달력에 그달 일정이 날짜별로 표시되고 브리핑이 만들어진 일정은 구분된다 | 기계 + 사람 | `calendar.test.tsx`(`local_date` 칸·배지) · `… u1-range -- .venv/bin/python -m pytest -q -rs tests/test_api_schedules_range.py`(`local_date`·`briefing_trace_id`) · U3 사람 점검 | 에이전트 + 사용자 | U1·U2·U3 |
| 3 | 날짜를 누르면 그날의 일정·브리핑이 보인다 | 기계 + 사람 | `calendar.test.tsx` 날짜 클릭 시험 · U3 사람 점검 | 에이전트 + 사용자 | U2·U3 |
| 4 | 월 범위 일정 조회 API 는 로그인 사용자의 일정만 돌려주고(남의 일정 0) | 기계 | `test_api_schedules_range.py` 남의 일정 시험 · `… u1-isolation -- .venv/bin/python -m pytest -q -rs tests/test_user_isolation.py tests/test_auth_required_routes.py` · 변이 V1-1 · 바깥 401(U3) | 에이전트 | U1·U3 |
| 5 | 읽기 전용이다(쓰기·trace·LLM 호출 0) | 기계 | `test_api_schedules_range.py` 의 `snapshot_db`·`assert_no_writes`(쓰기·trace 행 수 0) + 라우트 의존성에 LLM 계열 없음 시험 | 에이전트 | U1 |
| 6 | 기존 목록 보기·`GET /briefings` 동작 불변 | 기계 | `… u<N>-briefing-unchanged -- git diff --stat <기준>..HEAD -- tests/test_api_read_briefings.py tests/test_api_read_briefings_e2e.py tests/test_api_briefings.py web/src/__tests__/briefing.test.tsx web/e2e/briefing.spec.ts` → **빈 출력** + `… u<N>-briefing-tests -- .venv/bin/python -m pytest -q -rs tests/test_api_read_briefings.py tests/test_api_read_briefings_e2e.py tests/test_api_briefings.py` 통과 + Vitest `briefing.test.tsx` 통과 | 에이전트 | U1·U2 |
| 7 | 새 프론트 의존성 0 | 기계 | `… u2-no-new-deps -- git diff --stat <기준>..HEAD -- web/package.json web/package-lock.json` → **빈 출력** | 에이전트 | U2 |
| 8 | pytest·typecheck·Vitest·build 통과 | 기계 | `… u<N>-pytest-all -- .venv/bin/python -m pytest -q -rs tests/` → 실패 0·skip 0 · `… u2-typecheck -- npm --prefix web run typecheck` · `… u2-vitest -- npm --prefix web exec -- vitest run --root web` · `… u2-build -- npm --prefix web run build` · (CI 와 같은 명령) `… u2-e2e -- npm --prefix web run e2e` | 에이전트 | 전 단위 |

단위 공통: ruff `… u<N>-ruff -- .venv/bin/python -m ruff check app tests scripts evaluation`(**`--fix` 금지**) · mypy `… u<N>-mypy -- .venv/bin/python scripts/mypy_check.py --run`(새 오류 없음) · 툴 7종 `POSTGRES_PORT=5433 … u<N>-tools-check -- .venv/bin/python scripts/tools_check.py` 7/7 · 범위 `… u<N>-scope -- git diff --name-only <직전 해시>..HEAD`(그 단위 산출물만). 사람 점검 항목은 "사람" 으로 구분하고 사용자가 준 결과를 메인이 Write 로 `evidence/` 에.

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 브리핑 화면에서 목록 보기와 달력 보기를 전환할 수 있다 + 월 달력에 그달 일정이 날짜별로 표시되고 브리핑이 만들어진 일정은 구분된다 + 날짜를 누르면 그날의 일정·브리핑이 보인다 + 월 범위 일정 조회 API 는 로그인 사용자의 일정만 돌려주고(남의 일정 0) 읽기 전용이다(쓰기·trace·LLM 호출 0) + 기존 목록 보기·`GET /briefings` 동작 불변 + 새 프론트 의존성 0 + pytest·typecheck·Vitest·build 통과

## 사용자 결정 (권장안을 기본값으로 채택)

| # | 항목 | 후보 | **채택(권장)** | 이유 |
|---|---|---|---|---|
| A | 조회 구간 상한 | (i) 최대 42일(6주 달력 한 화면) (ii) 92일 (iii) 무제한 | **(i)** | 달력 한 화면을 덮고 응답 크기를 묶는다. 경계 42일은 통과(H-4) |
| B | 달력 구현 | (i) CSS 그리드 + 기존 shadcn(`tabs`·`button`·`badge`) (ii) `react-day-picker`(shadcn Calendar) 추가 | **(i)** | 새 의존성 0, 일정 표시 칸은 어차피 직접 그려야 한다 |
| C | 기본 보기 | (i) 목록 (ii) 달력 (iii) 마지막 선택 기억(localStorage) | **(i)** | 기존 동작·요청 불변, 알림 클릭 주소와 맞음 |
| D | 칸당 표시 수 | (i) 2개 + "외 N"(`truncate`) (ii) 점만 | **(i)** | 넓은 화면에서 제목이 보인다. 360px 폭에서는 칸이 약 45px 라 넘칠 수 있다 — 사람 점검에서 넘치면 좁은 폭만 (ii) 로 물러남(R-4) |
| E | 주 시작 요일 | (i) 일요일 (ii) 월요일 | **(i)** | 한국 달력 관례 |

## 리스크 · 미결

- **[순서·포기 시점]** P9b 완료 전에는 활성화할 수 없다. **2026-11-17(화) 12:00 까지 U1·U2 가 verifier 리뷰를 통과하지 못하면 평가 전 배포에서 뺀다** — 배포본은 `4be331b`(로그인만) 그대로(R-5).
- **[시간대 — 사용자 고지]** 일정의 날짜 칸은 **서버 시간대(Asia/Seoul) 기준**이다. 해외 시간대 브라우저에서도 칸은 서울 날짜로 보이고, 같은 화면의 목록 카드 시각은 기기 시간대로 찍혀 서로 다르게 보일 수 있다. "오늘 칸" 은 기기 날짜라 시간대가 다르면 하루 어긋날 수 있다(H-2).
- **[카드 이동]** `BriefingItem` 을 `BriefingCard` 로 옮기면서 목록 탭 DOM 이 바뀌면 `briefing.test.tsx` 가 잡는다 — 그 파일은 diff 0 이어야 한다(판정 #6).
- **[성능]** 날짜 상세는 그날 브리핑 있는 일정 수만큼 요청(상한 없음, R-6). 순위 창 함수는 구간 일정으로 먼저 좁힌다(R-2 ②) — 시연 규모에서는 무해.
- **[원칙]** 원칙7 경계 문장(브리핑 제안 한 줄)·원칙9 와 충돌 없음 — 생성·판정이 없는 읽기 전용(CR-006 변경 항목 2).
- **[하네스(R-7)]** `verify-plan.sh` 31·62·68행 정규식이 `P9b-…`·`P9c-…`·`P4b-…` 형태 id 를 못 읽어 의존·게이트 검사가 조용히 빠진다 — 이 패키지 밖 하네스 FIX 후보.

## 사용자만 할 수 있는 일 · 에이전트가 검증할 수 없는 것

- 배포 반영 SSH 명령(P9b U7 과 같음, `.env` 변경 없음) — P9c 04-review `결과: 완료` 뒤에만, 포기 시점 전에.
- 배포 URL 에서 로그인 후 달력 화면 확인(쿠키가 필요한 GET 은 사용자 브라우저), 360px 폭 가로 스크롤, 알림 클릭 시 목록 탭 전환(실기기).
- 해외 시간대 브라우저에서의 표시 기준(위 고지)을 받아들이는지.

## 읽은 카드

- `docs/wiki/changes/CR-006.md`(변경 항목 2) · `docs/wiki/specs/S3.6-briefing-push.md` · `docs/wiki/packages/P9b-auth/01-plan.md`(형식·의존·판정 방법) · `docs/wiki/packages/P9c-briefing-calendar/02-plan-verify.md` 전문(사전 검증 소견 — 개정 1 의 근거)
- 코드(HEAD `1723a84`): `app/api/routes.py` grep(`current_user`·`/briefings` 549행) · `app/api/read.py` 260~349(P9b 전 읽음) · `app/settings.py` grep(`user_timezone` 484행) · `app/main.py` grep(`InvalidValue` 131·193행) · `tests/auth_helpers.py` 55~114 · `tests/test_auth_required_routes.py` 40~61·grep · `tests/test_user_isolation.py` grep · `tests/helpers_read_api.py` grep · `web/src/screens/BriefingScreen.tsx` grep · Glob `web/src/**`.
- 열지 않은 것: `docs/wiki/packages/P9b-auth/03-log.md`·`registry.md` P9b 행 본문(02-plan-verify 의 인용과 위 grep 으로 갈음) · `web/src/App.tsx`·`AppShell.tsx`·`client.ts` 본문(사실 9 는 02-plan-verify H-6 인용) · `web/src/__tests__/briefing.test.tsx` 본문(가짜 fetch 규약은 02-plan-verify H-6 ② 인용).

## 개정 이력

- **개정 1(2026-11-16, verifier 02-plan-verify 사전 검증 보류 반영)**

| 소견 | 반영한 곳 |
|---|---|
| H-1 | 5·7행에 "P9b `결과: 완료` 뒤 메인이 채운다"(지금 닫지 않음) |
| H-2 | 사실 7 · API 계약 `local_date`·날짜 해석·"오늘 칸·처음 달 = 기기 날짜" 확정 · U1 경계 값 테스트(11-01 00:00·11-30 23:59:59·12-01 제외·KST 00:30) + V1-7 · U2 `local_date` 로만 배치 + 테스트 값 + V2-1 · 리스크·사용자 고지 |
| H-3 | 사실 6 · 계약 "브리핑됨 = `briefing_trace_id !== null`", `briefed_at` 응답에서 제거 · U1 테스트 2건(+ 키 집합에 `briefed_at` 없음) · U2 배지 조건 + V2-5 |
| H-4 | 사실 8 · 계약 `1 ≤ days ≤ 42` 만 200, 그 밖 `InvalidValue` 422 `invalid_value`, 형식 오류 FastAPI 기본, `Query(alias="from")` · U1 테스트 42/43/같음/역순 + V1-4 · 결정 A 이유 |
| H-5 | 새 "판정 방법" 절(구절별 8행 + 단위 공통) · 기준선 절 · `.venv/bin/python`·`--root web`·`git diff --stat` 빈 출력·`snapshot_db`/`assert_no_writes`·스크립트 방식·`--include` · Vitest "`package.json` 무변경" 시험 삭제 |
| H-6 | 사실 9·10 · U2 "`schedule_id` 가 생기면 목록 탭" + 테스트 + V2-4 · "`getSchedules` 는 달력 탭 활성일 때만" + "목록 탭 `/api/schedules` 0" 테스트 + V2-3 |
| R-1 | 사실 1~5 를 HEAD `1723a84` 로 정정(라우트 17개·549행·`current_user`·도우미 이름) · 산출물에 `tests/test_auth_required_routes.py`(`_MUST_REQUIRE_LOGIN`·124행 주석) · "깨뜨릴 기존 단언 — 닫힌 목록(깨짐 0 · 확장 1)" 절 · 쿼리를 직접 받는 이유 |
| R-2 | U1 ① 조인 조건 ② 구간 일정으로 먼저 좁힘(사실 11) ③ V1-5 조작 trace ④ LLM 의존성 없음 단언 ⑤ `test_user_isolation.py` 1건 · V1-6 |
| R-3 | `BriefingItem` → `components/BriefingCard.tsx` 로 옮겨 export, 달력은 `onRun` 없이(버튼 없음·읽기 전용 확정), 순환 import 없음 · 범위 "하지 않는 것" · 리스크 [카드 이동] |
| R-4 | U2 접근성(`<button>`·`aria-label`·`aria-current="date"`·`aria-pressed`) + 역할·이름으로 찾는 테스트 · U3 360px 가로 스크롤 0 사람 점검 · 결정 D 이유 |
| R-5 | 8행 포기 시점(2026-11-17 12:00)·"서버 해시는 P9c 04-review 완료 뒤에만"·못 들어가면 `4be331b` · U3 의존·배포 반영 · 리스크 |
| R-6 | 계약 행 수 상한 = 구간 길이 · U2 요청 수(상한 없음) + 호출 수 테스트 · 리스크 [성능] |
| R-7 | 리스크 [하네스] 한 줄 |
| P9b 교훈 | 작업 단위 머리: 단위별 통과 가능성·닫힌 목록·`ruff --fix` 금지·변이에 커밋형 테스트 제외 · 기준선 절: Mac 로컬 판정(Windows CI 미확인) |
