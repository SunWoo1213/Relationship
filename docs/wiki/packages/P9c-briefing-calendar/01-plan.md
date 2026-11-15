# P9c-briefing-calendar · 계획 (01-plan)

상태: 초안(2026-11-15, architect) — **P9b-auth 04-review 완료 뒤에만 활성화**(한 번에 활성 하나). 사용자 결정 표는 권장안을 기본값으로 채택(사용자 지시 2026-11-15) | 담당: backend-agent(sonnet, U1) · frontend-agent(sonnet, U2) · 메인 세션(U3) · 검증 verifier(fable) | 작성: 2026-11-15
태그 — 패키지: P9c-briefing-calendar · 닫는 검증: — · 기대는 결정: D18(로그인 사용자 기준 조회) · 구현하는 명세: S3.6(보기 보충) · 관련 원칙: 원칙5(폐지 문장) 원칙7 원칙9 · 출처 CR: CR-006 변경 항목 2
의존: **P9b-auth 04-review `결과: 완료`**(미충족 — 조회가 로그인 사용자의 `user_id` 위에서 돈다) · P8-frontend(완료) · P6-briefing(완료).

- **기준 해시**: 활성화 직전 메인이 `bash .claude/scripts/gitlog.sh P9c P9b CR-006` 로 확인해 적는다.
- **일정**: 평가(2026-11-18) 전에는 P9b 가 우선. P9b 배포 반영·시연 준비가 끝나고 시간이 남을 때만 시작한다. **평가 전에 못 들어가면 배포본은 로그인만 반영된 상태**(브리핑 화면은 지금의 목록 보기)로 시연하고, 이 패키지는 평가 뒤 이어간다.

### 코드에서 확인한 사실

1. `GET /briefings`(`app/api/routes.py:488-497` → `app/api/read.py:267` `list_briefings`)는 **`briefing_compose` trace 가 있는 일정만**, `scheduled_at >= now - BRIEFINGS_LOOKBACK_DAYS`, 상한 `BRIEFINGS_LIMIT`, 일정마다 최신 1행. → 브리핑이 아직 없는 일정(예정일)과 임의의 달(과거·먼 미래)을 보일 수 없다.
2. 일정 목록 엔드포인트는 없다(라우트 12개 중 0). 인물 카드의 `upcoming_schedules` 는 인물 한 명 것.
3. `schedules(id, person_id, title, scheduled_at, briefed_at)` — 스키마로 충분(`briefed_at` 이 "브리핑됨" 표시, 최신 브리핑 trace 는 `list_briefings` 와 같은 조인으로 찾는다). **스키마 변경 0.**
4. 사용자 시간대는 `app/settings.py` `user_timezone()`(`APP_TIMEZONE`, 기본 Asia/Seoul) — 달의 경계(1일 00:00 ~ 말일 24:00)는 이 시간대로 자른다.
5. 프론트 shadcn/ui 컴포넌트: `button`·`card`·`badge`·`collapsible`·`skeleton`·`tabs`·`sheet`·`sonner`(`web/src/components/ui/`). 달력 컴포넌트는 없다.

→ **새 엔드포인트 1개가 필요**하다(사실 1·2). 기존 `GET /briefings` 의 창·상한을 바꾸면 목록 보기 동작이 바뀌므로 건드리지 않는다.

## 목표

CR-006 변경 항목 2 — 사용자 원문 "또 추가하고 싶은 기능은 브리핑 날짜를 달력형태로도 볼 수 있게 기능을 추가해줘". 브리핑 화면에 **목록 보기 / 달력 보기 전환**을 두고, 월 달력에 그달 일정을 날짜별로 표시하며(브리핑이 만들어진 일정은 구분), 날짜를 누르면 그날의 일정과 브리핑이 보이게 한다. 읽기 전용(LLM 0·trace 0)이고 기존 목록 보기는 그대로다. 예: 11월 달력의 18일 칸에 "김 대리 점심 ●(브리핑됨)" 이 보이고, 누르면 그 아래에 지금 목록 보기와 같은 브리핑 카드가 열린다.

## 범위

- 포함: 월 범위 일정 조회 API(U1) · 브리핑 화면 목록/달력 전환·월 이동·날짜 선택(U2) · 문서·registry·배포 반영(U3).
- 이 패키지에서 하지 않는 것:
  - **주·일 보기, 일정 추가·수정·드래그** — 일정은 대화(`add_schedule`)로만 만든다. 달력은 보기 전용.
  - **새 프론트 의존성(달력 라이브러리)** — 7열 그리드는 CSS 로 충분하고 번들·검증 부담을 늘리지 않는다(결정 B).
  - **브리핑 생성·재생성 버튼 추가** — 기존 "지금 브리핑" 그대로. 원칙7 경계(제안 한 줄) 무관.
  - **`GET /briefings` 의 창·상한 변경** — 목록 보기 불변(수용 기준).

## 산출물 (파일 경로)

- 새: `tests/test_api_schedules_range.py` · `web/src/components/BriefingCalendar.tsx` · `web/src/__tests__/calendar.test.tsx` · `docs/wiki/packages/P9c-briefing-calendar/tests.md`·`03-log.md`·`evidence/`
- 고침: `app/api/read.py`(`list_schedules_in_range`) · `app/api/routes.py`(`GET /schedules`) · `app/api/schemas.py`(`ScheduleRangeItemOut`) · `web/src/api/client.ts`·`types.ts`(`getSchedules(from, to)`) · `web/src/screens/BriefingScreen.tsx`(전환) · `docs/wiki/registry.md`

### API 계약
`GET /schedules?from=YYYY-MM-DD&to=YYYY-MM-DD` (로그인 필수, P9b 의존성) → 200 `[{id, title, scheduled_at, briefed_at|null, person:{id, display_name}, briefing_trace_id|null}]` 정렬 `scheduled_at, id`. `from ≤ 날짜 < to` 를 사용자 시간대로 해석, 구간 최대 결정 A 일. 오류: 형식·순서·구간 초과 422, 미로그인 401. 남의 일정 0. 쓰기·trace·LLM 0.

## 작업 단위

순서: **U1 ∥ U2**(U2 는 위 계약 + 목 응답) → U3.

- [ ] U1 **[backend-agent] 월 범위 일정 조회 API `GET /schedules`** / Refs: P9c-briefing-calendar D18 S3.6 CR-006 원칙9 / 의존: P9b-auth 완료
  - `list_schedules_in_range(session, user_id, start, end)`: `schedules ⋈ persons` 에 `Person.user_id == user_id`, `start ≤ scheduled_at < end`. `briefing_trace_id` 는 `list_briefings` 와 같은 원천(`tool_name='briefing' AND step='briefing_compose'`, 일정마다 최신 1행, trace 의 `person_id` 가 일정 인물과 같을 것 — R-U3-2 방어 조건 재사용)으로 LEFT JOIN. 상한은 구간 길이로만(결정 A).
  - 테스트: 그달 일정만(경계 1일 00:00 포함·다음 달 1일 00:00 제외, 시간대 Asia/Seoul) · 브리핑 있는 일정에 `briefing_trace_id` · 없는 일정 null · 남의 일정 0 · 미로그인 401 · `from>to`·형식 오류·구간 초과 422 · 호출 전후 `agent_traces` 행 수 불변 · 기존 `GET /briefings` 테스트 무수정 통과.
  - 변이: V1-1 `user_id` 조건 제거 → 남의 일정 테스트 · V1-2 끝 경계 `<` → `<=` → 다음 달 1일 제외 테스트 · V1-3 trace 조인에서 최신 1행 조건 제거 → 중복 행 테스트.
- [ ] U2 **[frontend-agent] 브리핑 화면 목록/달력 전환과 달력 컴포넌트** / Refs: P9c-briefing-calendar D18 CR-006 원칙5 / 의존: P9b-auth 완료(U1 과 동시)
  - `BriefingScreen` 위에 shadcn `tabs` 로 "목록 / 달력"(기본 목록 — 결정 C). 달력: 월 제목 + 이전/다음 달 버튼 + 요일 머리 + 7열 CSS 그리드, 칸마다 그날 일정 제목(최대 2개 + "외 N", 결정 D)과 브리핑됨 표시(`badge`). 날짜를 누르면 아래에 그날 일정 목록, 브리핑이 있으면 기존 목록 보기의 브리핑 카드 컴포넌트를 재사용(`getBriefings(scheduleId)`). 오늘 칸 강조. 월이 바뀔 때만 `getSchedules` 호출(캐시 없음 — P8 결정 I).
  - 새 의존성 0(`web/package.json` diff 0). 알림 클릭 주소 `#/briefings?schedule_id=` 는 지금처럼 목록 보기로 연다.
  - 테스트: 전환 · 그달 일정이 해당 칸에 · 브리핑됨 표시 · 날짜 클릭 → 그날 목록 · 이전/다음 달에 `from`/`to` 가 바뀐 호출 · 일정 0 달은 빈 칸 · `package.json` 무변경.
  - 변이: V2-1 날짜 칸 계산에서 시간대 무시(UTC) → 자정 근처 일정 칸 테스트 · V2-2 월 이동 시 `to` 계산 오류 → 호출 인자 테스트.
- [ ] U3 **[메인 세션 + 사용자] registry·문서·배포 반영·사람 점검** / Refs: P9c-briefing-calendar CR-006 D17 / 의존: U1·U2
  - registry 행 · RUNNING.md 한 줄 · 배포 반영(사용자 SSH — P9b U7 과 같은 명령, 마이그레이션 없음) · 바깥 GET `/api/schedules?from=…&to=…` 쿠키 없이 401 · 사람 점검(시연 계정 달력에 일정·브리핑 표시).

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 브리핑 화면에서 목록 보기와 달력 보기를 전환할 수 있다 + 월 달력에 그달 일정이 날짜별로 표시되고 브리핑이 만들어진 일정은 구분된다 + 날짜를 누르면 그날의 일정·브리핑이 보인다 + 월 범위 일정 조회 API 는 로그인 사용자의 일정만 돌려주고(남의 일정 0) 읽기 전용이다(쓰기·trace·LLM 호출 0) + 기존 목록 보기·`GET /briefings` 동작 불변 + 새 프론트 의존성 0 + pytest·typecheck·Vitest·build 통과

## 사용자 결정 (권장안을 기본값으로 채택)

| # | 항목 | 후보 | **채택(권장)** | 이유 |
|---|---|---|---|---|
| A | 조회 구간 상한 | (i) 최대 42일(6주 달력 한 화면) (ii) 92일 (iii) 무제한 | **(i)** | 달력 한 화면을 덮고 응답 크기를 묶는다 |
| B | 달력 구현 | (i) CSS 그리드 + 기존 shadcn(`tabs`·`button`·`badge`) (ii) `react-day-picker`(shadcn Calendar) 추가 | **(i)** | 새 의존성 0, 일정 표시 칸은 어차피 직접 그려야 한다 |
| C | 기본 보기 | (i) 목록 (ii) 달력 (iii) 마지막 선택 기억(localStorage) | **(i)** | 기존 동작 유지, 알림 클릭 주소와 맞음 |
| D | 칸당 표시 수 | (i) 2개 + "외 N" (ii) 점만 (iii) 전부 | **(i)** | 모바일 폭에서도 칸이 넘치지 않는다 |
| E | 주 시작 요일 | (i) 일요일 (ii) 월요일 | **(i)** | 한국 달력 관례 |

## 리스크 · 미결

- **[순서]** P9b 완료 전에는 활성화할 수 없다. 평가 전 시간이 없으면 평가 뒤로.
- **[시간대]** 일정 시각은 UTC 저장·사용자 시간대 표시 — 서버 범위 계산과 프론트 칸 계산이 같은 시간대(`APP_TIMEZONE`, 프론트는 응답 시각을 Asia/Seoul 기준으로)를 써야 한다. 프론트가 브라우저 시간대를 쓰면 해외 브라우저에서 칸이 하루 밀린다 — 03-log 에 기준을 적는다.
- **[원칙]** 원칙7 경계 문장(브리핑 제안 한 줄)·원칙9 와 충돌 없음 — 생성·판정이 없는 읽기 전용(CR-006 변경 항목 2).

## 사용자만 할 수 있는 일 · 에이전트가 검증할 수 없는 것

- 배포 반영 SSH 명령(P9b U7 과 같음, `.env` 변경 없음) · 배포 URL 에서 로그인 후 달력 화면 확인(쿠키가 필요한 GET 은 사용자 브라우저).

## 읽은 카드

- `docs/wiki/changes/CR-006.md`(변경 항목 2) · `docs/wiki/specs/S3.6-briefing-push.md` · `docs/wiki/packages/P9b-auth/01-plan.md`(형식·의존) · 코드 `app/api/read.py` 260~349 · `app/api/routes.py` 486~498 · Glob `web/src/**`.
