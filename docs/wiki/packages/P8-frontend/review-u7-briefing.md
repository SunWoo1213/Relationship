# P8-frontend U7 브리핑 화면 + 수동 브리핑 버튼 (+ U6 이월 R-U6-1·R-U6-2) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 (2026-10-14 19:50) — **[필수] 0, [권고] 4.** 01-plan 98행·결정 G·H·K·사용자 결정 (가) 계약 14항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출로 충족(§1). 판정 명령 재실행 exit 0(typecheck · 92 passed · build, 번들 `index-Cc64Eaft.css`/`index-BP2SAFv1.js` — 구현자 1946·메인 세션 1947 과 동일, `-judge.txt`). 서버 문자열(`sentence`·`text`·`title`·`display_name`) 변환 코드 0, 재정렬·재절단 코드 0, `basis`·`push`·`trace_id`·`composer`·`generated_at` 표시 0(`-grep.txt` 2~5절 + 탐침 P1a: 응답 7자리에 몰래 실은 마커 전부 미표시). 새 라우트·새 화면 0 — `routes.ts` 추가분은 `parseScheduleId`·`useScheduleIdParam` 두 함수뿐이고 `HREF` 3·`Route` 3종·`data-screen` 3·`App.tsx` diff 0(`-grep.txt` 8절); `#/briefings?schedule_id=9` 로 앱 전체를 열어도 해시 유지·브리핑 화면·9 맨 위 강조(탐침 P3). R-U6-1 닫힘(처방 1줄 + 탐침 P3 재현 순서 그대로인 테스트, M16 재실행 1 failed 동일) · R-U6-2 (iii) 닫힘(`GET /persons` 정상 진입 1회·알 수 없는 해시 진입 **2회** 실측, 늦은 응답 덮어쓰기 방지 실측 — 탐침 P2a·b·c). 내 변이 5건 중 3건(V1·V2·V5)은 기존 묶음이 잡고 2건(V3 강조의 보이는 스타일만 제거 · V4 늦은 응답 카운터 제거)은 **기존 묶음이 살려 두고 내 탐침만 가름** — 결함이 아니라 테스트 틈이라 [권고](R-U7-2). 구현자 M1·M5·M13·M16·M19 재실행이 실패 이름·건수까지 구현자 표와 동일. R-U0-3: package·lock 바이트 동일, scripts 7개 무변경, `npm audit --omit=dev` 0(`-deps.txt`). 증거는 전부 `save_evidence.py` 통로이고 변이 출력은 요약 없이 vitest 전체, 스크립트 원문 보존 — R-U6-3 준수(§8). 보안·범위 위반 0(§7).
대상: 작업 트리(기준 HEAD `761cced`) — `git diff -- web` 8파일(`card.test.tsx` 129/5 · `client.ts` 20/0 · `AppShell.tsx` 3/0 · `PersonList.tsx` 3/15 · `routes.ts` 16/0 · `BriefingScreen.tsx` 218/3 · `ChatScreen.tsx` 3/0 · `PersonCardScreen.tsx` 5/1) + 신규 `web/src/__tests__/briefing.test.tsx`(308행)·`web/src/components/PersonsProvider.tsx`(62행) · `docs/wiki/registry.md` U7 행 3개(248~250행) · 구현 증거 `evidence/20261013-1945-u7-briefing.txt`(91 passed, M19 보강 전)·`-1945-u7-mutation.txt`(20변이 + M19 재실행, 5529행)·`-1946-u7-briefing.txt`(최종, 92 passed)·`-1946-u7-mutation-script.txt` · 메인 세션 `-1947-u7-main-recheck.txt`. `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U7 시작" 항목은 근거 문서 — 사용자 결정 (가)·구현 결과·구현자 판단 목록).
근거 문서: `01-plan.md` 98행(U7 원문) · 결정 G(276~279행)·H(282~287행)·K(301~303행) · 19행(브리핑 한 문장)·36~49행(하지 않는 것)·52~80행(파일 목록) · 판정표 115행(ㄷ)·146~147행(20·21행)·152행(26행) · `docs/proposal.md` 348~360행(부록 A ③ 그림) · `app/api/schemas.py` 130~137행(`BriefingRunIn`)·197~211행(`BriefingRecordOut` — 원문 필드 없음, 근거는 `basis` 뿐)·223~233행(`BriefingRunOut`) · `app/api/read.py` 73·77행(`BRIEFINGS_LOOKBACK_DAYS=7`·`BRIEFINGS_LIMIT=20`)·256~277행(`list_briefings` — 서버 정렬 `scheduled_at desc, id desc`, `schedule_id` 지정 시 기간 미적용·없으면 404·compose 없으면 `[]`) · `app/api/routes.py` 380~406행(`/briefings/run`, `ScheduleNotFound` → 공통 404) · CLAUDE.md 원칙5·7 · `review-u6-card.md` R-U6-1·2·3·4 · `review-u0-harness.md` R-U0-3 · `docs/wiki/verification.md`.

내 증거(전부 `save_evidence.py` 통로, `docs/wiki/packages/P8-frontend/evidence/`):
- `20261014-1946-verifier-u7-judge.txt` — `cd web && npm run typecheck && npm test -- --run && npm run build` exit 0, 6 files · 92 passed, 번들 해시 구현자·메인 세션과 동일.
- `20261014-1946-verifier-u7-deps.txt` — package.json·lock `git diff --quiet` exit 0, scripts 7개(HEAD), `npm audit --omit=dev` "found 0 vulnerabilities", `?raw` 2건(U6 그대로), `BriefingScreen`·`PersonsProvider` import 목록(새 부품·패키지 0, `ui/` 8개 그대로). (3절 `cd web` 이 뒤 절에 남아 4·5절이 상대 경로를 못 찾았고 `--append` 로 절대 경로 재실행을 덧붙였다 — 판정과 무관.)
- `20261014-1946-verifier-u7-grep.txt` — 범위(`app/alembic/tests/.github` 빈 출력) · 원칙7 변환 grep · 순서 보존 grep · `basis` 등 숨김 필드 사용처 · 표시 필드 목록 · `innerHTML` 0 · `/push-dev/`·외부 URL 0 · 원칙5 불변식(HREF·Route·data-screen·설정 diff 0·routes.ts 변경 줄 전체) · 상호 import 0 · 같은 `PersonList` import · 결정 H 자리 · `BRIEFING_NOTICE` 9개 · 상담 어휘 0 · 비밀 0 · `test-setup.ts` 차단 유지 · `card.test.tsx` 빠진 줄 5개(전부 `render(` 줄) · registry U7 행 · 스키마 대조 · Provider 카운터·이벤트 · 404 분기·재시도 코드 grep.
- `20261014-1946-verifier-u7-mutation.txt`(3655행) — V0 대조군 + 내 변이 V1~V5 + 구현자 M1·M5·M13·M16·M19 재실행 = 11회. 매회 ① 기존 묶음(탐침 제외) ② 탐침 `zz_probe_u7.test.tsx`(9건) 를 따로 돌려 vitest 출력 전체(`DEBUG_PRINT_LIMIT=0` 으로 DOM 덤프만 끔), 끝에 `git status --short -- web` 으로 저장소 무수정 확인(11회 모두 U7 작업 트리 그대로).
- `20261014-1947-verifier-u7-scripts.txt` — 내 `vmut_u7.mjs`(M16 추가 전·후 두 벌)·`zz_probe_u7.test.tsx`·`grep_u7.sh`·`deps_u7.sh` 원문(줄 수·sha256 앞 16자리) — 스크래치패드는 세션과 함께 사라지므로 재현용 보존.

## 1. 01-plan 98행 · 결정 G·H·K · 사용자 결정 (가) 계약 대조

| # | 계약(98행 / 결정 / (가)) | 구현 | 테스트·변이 | 판정 |
|---|---|---|---|---|
| 1 | `GET /api/briefings` 목록, 서버 순서 보존(결정 G — trace 최신 1행, `read.py` 정렬·7일 창·상한 20 은 서버 몫) | `client.ts` 127~130행 `getBriefings(scheduleId?)` → `/briefings` 또는 `?schedule_id=N`; `BriefingScreen.tsx` 115행 `records = await getBriefings()` → 122행 `setList(records)`; 렌더 165~176행은 `list.forEach` 로 응답 배열 그대로(`.sort/.reverse/.filter/.slice` 0 — `-grep.txt` 3절) | `briefing.test` "서버 순서 그대로" (`LIST = [R5, R2, R9]` 는 id·이름·시각 어느 정렬과도 다름) · 구현자 M1 검출(내 재실행 4 failed, 이름 동일) | ✓ |
| 2 | 머리줄 "일정 시각 · 이름 · 일정 제목" (3요소 순서) | 48행 `{formatDateTime(schedule.scheduled_at)} · {person.display_name} · {schedule.title}` (46행 `h2`, 47행 `📌` 는 `aria-hidden`) | "머리줄은 일정 시각 · 이름 · 일정 제목"(`h2` 3개 `textContent` 완전 일치) · 구현자 M9(이름·제목 뒤집기) 검출 | ✓ |
| 3 | 패턴 문장·요약 줄·제안 한 줄 — 서버 문자열 그대로 | 55행 `{p.sentence}` · 61행 `{l.text}` · 69행 `{record.suggestion.text}` — React 텍스트 노드, 변환 호출 0(`-grep.txt` 2절: `slice` 적중 3건은 전부 `routes.ts` 해시 파싱) | "패턴 문장·요약 줄·제안이 서버 문자열 그대로"(`PATTERN`·`SUGGESTION` 에 앞뒤 공백·`<b>`·`&`·따옴표, `textContent` 완전 일치 + 순서 패턴→줄→제안) · 구현자 M3·M7(trim) 검출 | ✓ |
| 4 | `basis` 미표시 (schemas 197~211행 주석 "근거는 `basis` 뿐") | `basis` 는 3행 주석에만(`-grep.txt` 4절) — `push`·`trace_id`·`composer`·`generated_at` 도 사용처 0 | "basis 는 화면에 나오지 않는다" · 구현자 M2 검출 · **내 탐침 P1a**: 최상위·`schedule`·`person`·`pattern_sentences[]`·`lines[]`·`suggestion` 6자리에 `raw_utterance` + `basis`·`push`·`trace_id`·`composer` 마커 7개 → `textContent`·`innerHTML` 어디에도 없음(9 passed) | ✓ |
| 5 | (가) `?schedule_id=N` 이 목록 안이면 **맨 위 + 강조**, 나머지 서버 순서, 단건 요청 0 | 166행 `inList` → 170~171행 `top` 을 먼저, 나머지 `list.forEach` 순서 그대로; 123행 `records.some(...)` 이면 단건 호출 안 함; 44행 `data-highlight`, 45행 `bg-accent ring-2 ring-primary` | "목록 안에 있으면 맨 위로 올리고 강조하며 … 단건 요청은 0"(`ids()` = `[9,5,2]`, `data-highlight` 1개, 호출 `['/api/briefings']` 뿐) · 구현자 M8·M13 검출(M13 내 재실행 1 failed 동일) · **내 탐침 P3**(앱 전체로 진입) 통과 | ✓ |
| 6 | (가) 목록에 없으면 `GET /briefings?schedule_id=N` **1회 더** → 맨 위 + 강조 | 129행 `getBriefings(scheduleId)` → 131행 `setExtra(one[0] ?? null)`; 173~174행 `extra` 먼저, 그 뒤 목록 | "목록에 없으면 … 1회 더 불러 맨 위에 붙이고 강조한다"(호출 순서 `['/api/briefings', '/api/briefings?schedule_id=77']`, `ids()` = `[77,5,2,9]`) · 구현자 M6(항상 호출)·M14(맨 아래) 검출 · **내 V2**(강조 없이 붙임) 검출(1 failed) | ✓ |
| 7 | 쿼리 없으면 단건 0 · 서버 순서 그대로 | 123행 `scheduleId === null` 이면 `setExtra(null)` 후 return; `routes.ts` 35~45행 `parseScheduleId` — `?` 없으면 null | "쿼리가 없으면 서버 순서 그대로이고 단건 요청은 0" | ✓ |
| 8 | 단건 404 또는 `[]` → 안내 한 줄, 목록 유지 (`read.py` 273~274행: 없거나 남의 일정 404, compose 없으면 `[]`) | 132행 `one.length === 0 ? 'missing'`; 134행 `ApiError && status === 404 ? 'missing' : 'failed'`; 194행 `BRIEFING_NOTICE.scheduleMissing` | "단건이 404 이거나 [] 이면 안내 한 줄 + 나머지 목록 그대로"(두 경우 루프, 강조 0) | ✓ |
| 9 | "지금 브리핑" → `POST /api/briefings/run {schedule_id}` → **목록 다시 읽기**(응답 직접 삽입 아님) | 149행 `postBriefingRun(id)`(`client.ts` 133~136행 본문 `{ schedule_id }` = `BriefingRunIn`) → 156행 `await load()`; `BriefingRunOut.briefings` 는 어디서도 읽지 않음 | "POST 본문은 {schedule_id} 이고, 성공하면 응답을 끼우지 않고 GET /briefings 를 다시 읽어 갱신한다"(POST 1·GET 2·새 줄은 GET 에서만) · 구현자 M4(재요청 제거)·M12(본문 키) 검출 · **내 V1**(재요청을 POST **전**에) — 기존 묶음이 2 failed 로 검출(404·5xx 테스트의 GET 횟수 단언) + 내 탐침 P7(호출 순서 `GET→POST→GET`) 검출 · **내 탐침 P1b**: POST 응답 `briefings[]` 에 넣은 줄·원문 마커 미표시 | ✓ |
| 10 | 결정 K: 404 → "잠시 뒤 다시 시도" 안내만, 자동 재시도 0 | 152행 `status === 404 ? 'locked' : 'failed'` → 82~86행 `role=status` `runLocked`; `setTimeout/setInterval/retry` 0(`-grep.txt` 20절) | "404(잠금 중)이면 … 자동 재시도 없음(POST 1회), 목록 재요청도 없고 버튼은 다시 활성" · 구현자 M5(재시도 주입)·M11(404→일반 실패) 검출(M5 내 재실행 1 failed 동일) | ✓ |
| 11 | 빈 상태 문구 | 204행 `list !== null && items.length === 0` → `empty` | "빈 목록이면 빈 상태 문구 하나" · 구현자 M15 검출 | ✓ |
| 12 | 결정 H: 브리핑 화면 상단 "알림 받기" 한 줄 — 동작은 U8(자리만) | 184~187행 `data-slot="push-subscribe"` 안 `disabled` 버튼; `push.ts`·`sw.js`·`manifest` 없음, `pushManager/vapid/serviceWorker` 제품 코드 0(`-grep.txt` 11절) | "알림 받기는 자리만(비활성)이며 /push-dev/ 링크가 없다" | ✓ — U8 계약과 맞음(99행 "브리핑 화면 '알림 받기'") |
| 13 | 판정 `npm test -- --run src/__tests__/briefing.test.tsx` · 증거 `*-u7-briefing.txt` | 구현자 `-1946-u7-briefing.txt` exit 0(16 + 전체 92 + build) · 메인 `-1947` · 내 `-judge.txt` 92 passed | — | ✓ |
| 14 | 부록 A ③ 그림 모양 — `📌` 머리줄 → `·` 줄들 → `💡 제안` | 47행 `📌`, 54·60행 `·`(둘 다 `aria-hidden`), 67행 `h3` `suggestionTitle = '💡 제안'`, 69행 제안 본문. 그림의 머리줄은 2요소("내일 15:00 · 김팀장 회의")지만 98행이 3요소로 확정했고 날짜는 U6 결정 ②(절대 표기)를 그대로 따른다 | "제안이 없으면 제안 구획이 없다"(`suggestion: null` → `h3` 0) · 판정표 146행 20행과 일치 | ✓ |

**TS 타입**: `types.ts` 173~183행 `BriefingRecordOut` = `schemas.py` 203~211행 필드·null 가능성 1:1(`-grep.txt` 18절). `BriefingRunIn` 185~187행(`schedule_id?: number | null`) = 137행. U3·U4 에서 이미 대조한 것, 이번 변경 없음.

## 2. 원칙7 · 원칙5

- **원칙7**: 변환 호출 grep(`trim/slice/replace/toLowerCase/substring/split/…`) — `BriefingScreen`·`PersonsProvider`·`PersonList`·`client.ts` 0건, `routes.ts` 3건은 해시 문자열 파싱(`pathOf` 19·21행, `parseScheduleId` 42행)이지 서버 문자열이 아니다. 날짜 포맷 호출은 `formatDateTime(schedule.scheduled_at)` 1곳뿐(5절). `innerHTML`/`dangerouslySetInnerHTML` 제품 코드 0(6절). 상담·감정 어휘 0(13절 — 적중 1건은 165행 주석 "마음" 이 아니라 "맨 위로" 안의 글자 조합, 어휘 아님). 고정 문구는 `BRIEFING_NOTICE` **9개**(빈 상태·목록 실패·단건 없음·버튼 2·잠금 안내·실패 안내·제안 제목·알림 받기) — 전부 빈 상태·오류·라벨·버튼 글자, 서버 문장을 대신하는 것 0(12절). 경계 문장(브리핑 제안 = 서버가 준 한 줄)도 지킨다 — 제안은 `record.suggestion.text` 그대로.
- **원칙5**: `routes.ts` 변경 줄 전체가 `parseScheduleId`·`useScheduleIdParam` 두 함수(`-grep.txt` 8절 diff 줄) — `HREF` 3개(10~12행)·`Route` 3종(5~7행)·`parseHash` 반환 3종(27~31행) 그대로, `parseHash` 는 18~22행 `pathOf` 가 쿼리를 떼므로 `#/briefings?schedule_id=3` 은 **기존** `briefings` 라우트(routes.test 55행이 이미 고정, 내 탐침 P3 이 앱 전체로 확인: 해시 유지 `#/briefings?schedule_id=9`, `data-screen="briefings"`, 사이드바 "브리핑" `aria-current=page`). `data-screen` 3개, `App.tsx`·`main.tsx`·`index.html` diff 0. 결정 H 의 "알림 받기" 는 브리핑 화면 안(네 번째 화면 아님). `/push-dev/` 0.

## 3. R-U6-1 · R-U6-2 (iii) 닫힘

- **R-U6-1 닫힘.** `PersonCardScreen.tsx` 76~79행 — `if (state.status === 'error') { setOpen(true); return run() }` (내 U6 처방 그대로). `card.test.tsx` "R-U6-1: 로딩 중 접기 → 요청 실패 → 다시 펼치면 열리고 재시도해 원문이 나온다" — 순서 1) 펼침(로딩) 2) 로딩 중 접음 3) `rejectFirst()` 로 요청 실패 4) 다시 펼침 → 원문 `RAW_A` 완전 일치·요청 2회·버튼 이름 `hideRaw` = 내 U6 탐침 P3 의 재현 순서·단언 3개 그대로. 구현자 M16(처방 되돌리기) 검출, **내 재실행 1 failed(그 테스트, `raw-utterance` 못 찾음) 동일**.
- **R-U6-2 (iii) 닫힘.** `PersonsProvider.tsx`(62행) — 50행 마운트 1회 `load()`, 51행 `hashchange`, 52행 `relationship:persons-changed`(9행 상수, 11~13행 `notifyPersonsChanged`) 때 재조회; 33~44행 `latest` 카운터로 늦은 응답 무시. `AppShell.tsx` 56·82행이 감싸고, `PersonList.tsx` 16행 `usePersons()` 로 읽음(조회 코드 15줄 삭제). `ChatScreen.tsx` 179·204행 `/chat`·`/answers` 응답 `stored.persons > 0` 이면 알림. **실측(탐침 P2)**: 정상 진입(`#/chat`) `GET /persons` **1회** · 알 수 없는 해시(`#/nope`) 진입 **2회**(구현자 보고 "1회 더 가능" 이 정확히 2 — 원인은 `routes.ts` 65~70행 `useRoute` 가 `replaceState` 뒤 `hashchange` 를 직접 dispatch 해 Provider 가 한 번 더 읽는 것; 결함 아님, 03-log 에 수치로 기록 권고) · 느린 1차 응답 + 빠른 2차(알림 이벤트) → 1차가 늦게 와도 사이드바 = 2차("둘째(유지)"); **카운터를 지운 V4 에서는 "첫째(덮임)"** 로 바뀌어 카운터가 실제로 막는 것을 확인. 기존 테스트: `card.test.tsx` R-U6-2 5건(1회·해시 변경 2회·`stored.persons>0` 2회·`=0` 1회·이벤트만) — 구현자 M17·M18·M19 검출, M19 내 재실행 1 failed 동일(`=0` 테스트가 가름). 상호 import: `ChatScreen`→`AppShell` 0, `AppShell`/`PersonsProvider`/`PersonList`→`@/screens` 0(9절) — 창 이벤트로 끊었다. 사이드바·본문 `import PersonList from '@/components/PersonList'` 두 곳 동일(10절), `card.test` 259행 import 동일성 테스트 유지. `card.test.tsx` 에서 빠진 줄은 `render(<PersonCardScreen personId={null} />)` 5개뿐(16절) — 전부 `{ wrapper: PersonsProvider }` 추가, 단언 변경 0.

## 4. 구현자 판단 6개 (03-log 19:46 항목)

| # | 구현 안 | 계획·원칙7 대조 | 판정 |
|---|---|---|---|
| ① | 단건 비-404 실패(5xx·네트워크)에 `listFailed` "브리핑을 불러오지 못했어요." 재사용(134행 `'failed'` → 199행) | 계획에 단건 실패 문구 규정 없음. 다만 이때 **목록은 정상으로 떠 있는데** "불러오지 못했어요" 가 그 위에 나와 뜻이 어긋난다(목록은 왔고 그 일정만 못 가져온 것). 자동 테스트는 404·`[]` 만 다룬다(이 분기 단언 없음) | 모순 없음 — [권고] R-U7-3(U10 사람 점검 항목 또는 문구 1개) |
| ② | 목록 `[]` + 단건 없음 → `empty` 와 `scheduleMissing` 둘 다 | 둘 다 참인 문장이고 각각 98행 "빈 상태 문구"·(가) "없으면 … 안내" 에 대응 | 적합 — 기록 |
| ③ | 수동 브리핑 성공 뒤 쿼리 일정이 창 밖이면 `GET` 2회(목록 + 단건) | (가) "목록 1회 + 없으면 단건 1회" 를 재조회에도 그대로 적용한 것(110행 docstring "항상 이 경로"). 재조회 뒤 그 일정이 창 안으로 들어오면 123행 `some` 이 참이라 단건 0 | 적합 — 기록 |
| ④ | 재조회 실패 시 이전 목록 유지 + 한 줄(116~118행 `setFailed(true)` 만, `list` 유지) | 원칙8 취지(실패를 숨기지 않음)와 사용자 경험 둘 다 맞다. **탐침 P4** 실측: POST 성공 → GET 500 → 목록 3건 그대로 + `listFailed`, `empty` 없음. 기존 테스트는 첫 조회 실패만 단언(내 V5 "실패 시 `setList([])`" 는 그 테스트가 잡았지만 `list !== null` 일 때만 비우는 변이는 살아남는다) | 적합 — 테스트 틈은 R-U7-2 |
| ⑤ | `schedule_id` 양의 정수만(`/^[1-9]\d*$/`, 0·음수·소수·문자 → 쿼리 없음) | 서버 `schedule_id: int`·0 이하는 어차피 404. 알림 URL 은 U8 이 `data.schedule_id`(정수)로 만든다(99행). 잘못된 쿼리를 404 요청 대신 "쿼리 없음" 으로 다루는 것은 요청 1회 절약이고 사용자에게 보이는 차이 없음 | 적합 — 기록. 구현자 M20(0 허용) 검출 |
| ⑥ | 고정 문구 — 03-log "8개" 로 적었으나 `BRIEFING_NOTICE` 키는 **9개**(`subscribe` 포함) | 전부 안내·버튼 글자(§2). 서버 문장 대체 0, 상담·감정 어휘 0 | 적합 — 수 표기만 03-log 에서 9로(R-U7-4) |

## 5. 변이 시험 (`-mutation.txt`, 저장소 무수정 — 11회 전부 끝의 `git status --short -- web` 이 U7 작업 트리 그대로)

| 변이 | 기존 묶음(탐침 제외) | 탐침 9건 | 뜻 |
|---|---|---|---|
| V0 대조군 | 92 passed | 9 passed | 기준선 |
| **V1** 목록 재요청을 POST **전**에 | **2 failed** — 404 테스트(GET 1 기대, 2)·5xx 테스트(GET 2 기대, 3) | P7(호출 순서 `GET→POST→GET`) 1 failed | 검출. "GET 다시 읽기" 테스트 자체는 순서를 못 가르지만 404·5xx 의 GET 횟수 단언이 잡는다 |
| **V2** 창 밖 단건을 강조 없이 붙임 | **1 failed** — "목록에 없으면 … 강조한다"(`data-highlight` 없음) | 9 passed | 검출 |
| **V3** 강조의 보이는 스타일(`bg-accent ring-2 ring-primary`)만 제거, `data-highlight` 유지 | **92 passed — 살아남음** | P6(강조 항목 `ring-2`) 1 failed | 테스트 틈 — 강조 단언이 `data-highlight` 속성뿐이라 사용자가 보는 강조가 사라져도 통과. R-U7-2 |
| **V4** `PersonsProvider` 늦은 응답 카운터 제거(39행) | **92 passed — 살아남음** | P2c "첫째(덮임)" 1 failed | 테스트 틈 — 03-log·registry 가 주장하는 "늦은 응답 무시" 를 가르는 테스트 0. R-U7-2 |
| **V5** 조회 실패 시 `setList([])` | **1 failed** — "목록 조회가 실패하면 한 줄 안내(빈 상태 문구는 아님)" | P4 1 failed(`briefing-list` 없음) | 검출(첫 조회 경로). 재조회 경로 전용 단언은 P4 뿐 |
| M1 재실행(id 오름차순 정렬) | 4 failed — 구현자 1945 표와 이름·건수 동일 | P3·P4 2 failed | 구현자 표 신뢰 |
| M5 재실행(404 자동 재시도) | 1 failed(404 테스트) — 동일 | 9 passed | 〃 |
| M13 재실행(맨 위로 안 올림) | 1 failed — 동일 | P3 1 failed | 〃 |
| M16 재실행(R-U6-1 처방 되돌리기) | 1 failed(R-U6-1 테스트) — 동일 | 9 passed | 〃 |
| M19 재실행(`>= 0`) | 1 failed(`stored.persons=0` 테스트) — 구현자 **재실행**(5529행)과 동일 | 9 passed | 1945 첫 실행 "살아남음" → 테스트 보강 → 검출, 과정이 증거에 그대로 있다 |

탐침 결과(대조군): P1a 몰래 실은 마커 7개 미표시 · P1b POST 응답 줄 미표시 · P2a `#/nope` → `GET /persons` 2회·해시 `#/chat` · P2b `#/chat` → 1회 · P2c 늦은 응답 "둘째(유지)" · P3 앱 전체 진입 해시 유지·강조·단건 0·호출 `["GET /api/briefings","GET /api/persons"]` · P4 재조회 실패 뒤 목록 유지 · P6 강조 `ring-2`/비강조 `ring-1` · P7 `GET→POST→GET`.

## 6. R-U0-3 고정 점검 (`-deps.txt`)

`git diff --quiet -- web/package.json web/package-lock.json` exit 0 — 새 패키지 0. scripts 7개 HEAD 와 동일(`dev/build/typecheck/test/e2e/lint/preview`, 셸 전용·삭제 명령 0). `npm audit --omit=dev` "found 0 vulnerabilities". `BriefingScreen` import 는 `Button`·`Card`(U4 기존 부품)·`formatDateTime`·`cn`·`useScheduleIdParam`, `PersonsProvider` 는 React·`getPersons`·타입뿐 — 새 `shadcn add` 0(`ui/` 8개 그대로). `?raw` 2건은 U6 그대로.

## 7. 보안·범위

- `git status --short -- app alembic tests .github` 빈 출력 — 백엔드·CI 무변경. 삭제 파일 0(`--diff-filter=D` 빈 출력). 신규는 테스트 1·컴포넌트 1·증거 5 뿐.
- 비밀 패턴 0(web diff + 신규 2파일), 외부 URL 0(적중 1건은 U5 `proxy.ts` `localhost:8000` 기존), `/push-dev/` 0, `innerHTML` 0.
- 결정 J: `test-setup.ts` 무변경(10행 기본 `fetch` 는 throw), `briefing.test.tsx` 는 `vi.stubGlobal('fetch')` + `afterEach(vi.unstubAllGlobals)` + `router` 가 표 밖 요청(메서드+경로 키)을 throw — 실 네트워크 0.
- `web/src` 바깥 쓰기 없음. 구현자 변이·내 변이 전부 스크래치패드 사본에서만.

## 8. 증거 규칙 (c) · R-U6-3 · registry · 03-log

- 구현자 증거 5파일 전부 `save_evidence.py` 머리줄 5개 + `# exit`. **R-U6-3 준수**: `mut_u7.mjs` 가 `stdio: 'inherit'` 로 vitest 출력을 그대로 흘려 변이당 ~250행(실패 단언 메시지·스택까지), 스크립트 원문은 `-1946-u7-mutation-script.txt` 에 `cat` 으로 보존. M19 첫 실행 "살아남음" 과 보강 후 재실행이 같은 파일에 순서대로 있다(요약·삭제 0).
- registry U7 행 3개(248~250행) — 코드와 대조: `BRIEFING_NOTICE`·머리줄·`·`·`💡 제안`·`basis` 미표시·버튼 동작·404 안내·(가) 강조·알림 받기 자리·`parseScheduleId`/`useScheduleIdParam`·`getBriefings`/`postBriefingRun` ✓ · `PersonsProvider` 설명(1회·해시·이벤트·늦은 응답 무시)·`AppShell`·`PersonList`·`ChatScreen`·`toggle` ✓ · 16건 + 이월 6건 → 92 ✓ · 변이 20건·M19 재실행·증거 경로 ✓. "(U7 미커밋)" 3칸은 커밋 뒤 해시.
- 03-log "U7 시작" 항목 — 구현 결과 문단이 내 확인과 일치. 완료 항목에 적을 것은 R-U7-4.

## 9. 소견

- **[권고] R-U7-1 · `run` 이 클릭 시점 `load` 를 붙잡는다 — 실행 중 쿼리가 바뀌면 옛 `schedule_id` 기준으로 강조·단건이 적용된다**(`BriefingScreen.tsx` 146~162행 `run` 의 156행 `await load()`, `load` 는 110행 `useCallback(..., [scheduleId])`). 순서: "지금 브리핑" 클릭(POST 진행 중) → 해시가 `?schedule_id=A` 에서 `B` 로 바뀜 → 139~144행 effect 가 `latest++` 뒤 새 `load`(B) 실행 → POST 완료 → **옛** `run` 이 옛 `load`(A) 를 부르며 `++latest` 로 가장 최신이 되어 B 의 응답은 버려지고 A 의 단건·강조가 남는다(주소는 B). 재현 탐침은 쓰지 않았다(코드 읽기 소견) — 발생 조건이 "수동 브리핑 진행 중 알림 클릭" 이라 드물다. 처방 1줄: `load` 를 `useRef` 로 최신을 가리키게 하거나, `run` 에서 재조회 전에 `latest` 를 잡아 두고 `scheduleId` 변경이 있었으면 재조회를 건너뛴다. 커밋을 막지 않는다.
- **[권고] R-U7-2 · 테스트 틈 3개(내 변이 V3·V4 생존 + V5 세분).** ① 강조 단언이 `data-highlight` 속성뿐 — `bg-accent ring-2 ring-primary` 를 지워도 92 passed(V3). 탐침 P6(강조 항목 `className` 에 `ring-2`, 비강조에 없음) 한 줄을 "목록 안에 있으면 맨 위로" 테스트에 더한다. ② `PersonsProvider` 늦은 응답 카운터(39행)를 지워도 92 passed(V4) — 03-log·registry 가 "늦은 응답 덮어쓰기 방지" 를 주장하지만 가르는 테스트가 없다. 탐침 P2c(느린 1차 + `notifyPersonsChanged()` 빠른 2차 → 1차 뒤늦게 resolve → 사이드바 = 2차)를 `card.test.tsx` R-U6-2 묶음에 옮긴다. ③ 구현자 판단 ④(재조회 실패 시 이전 목록 유지)는 첫 조회 실패 테스트가 간접으로만 덮는다 — 탐침 P4(POST 성공 → GET 500 → 목록 3건 유지 + `listFailed`) 를 "지금 브리핑" 묶음에 더한다. 세 탐침 원문은 `-1947-verifier-u7-scripts.txt` 의 `zz_probe_u7.test.tsx` 에 있다(현재 코드에서 전부 통과, 변이에서 실패 확인됨).
- **[권고] R-U7-3 · 구현자 판단 ① — 단건 비-404 실패에 목록 실패 문구를 재사용하면 목록이 떠 있는 채 "브리핑을 불러오지 못했어요." 가 나온다**(134행 `'failed'` → 199행). 계획 모순은 아니다. U10 사람 점검 항목으로 두거나, 그 일정만 못 가져왔다는 문구 1개(`BRIEFING_NOTICE` 10번째)로 바꾼다 — 결정 L 수정 1회 상한 안.
- **[권고] R-U7-4 · 03-log U7 완료 항목·registry 에 적을 것.** ① 알 수 없는 해시 진입 시 `GET /persons` **2회**(실측, 탐침 P2a)·정상 진입 1회 — 원인은 `useRoute` 의 `hashchange` 직접 dispatch, 결함 아님 ② 고정 문구 수 8 → **9**(`subscribe` 포함) ③ `data-slot="push-subscribe"` 가 shadcn 부품의 `data-slot` 관례와 같은 속성 이름을 쓴다(충돌 없음 — 기록, U8 이 자리를 채울 때 유지) ④ 구현자 판단 ①~⑥ 과 이 리뷰 판정(§4) ⑤ R-U6-1·R-U6-2 (iii) 닫힘, R-U6-3 준수 ⑥ 내 증거 5파일 경로와 R-U7-1·2·3 의 처리 결정 ⑦ "(U7 미커밋)" 3칸 → 해시 ⑧ Refs `P8-frontend U7 S3.6 R19 원칙7 D2 R-U6-1 R-U6-2 R-U6-3 FIX-034`.

## 10. 판정 근거 요약

- 판정 명령 3개 재실행 exit 0, 92 passed, 번들 해시 구현자·메인 세션과 동일(`-judge.txt`).
- 98행·결정 G·H·K·(가) 계약 14항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출(§1). 머리줄 3요소·서버 문자열(특수문자·공백 포함) 완전 일치·`basis` 미표시·서버 순서·강조 두 경로·404/`[]`·POST 본문·목록 재요청·404 안내만·빈 상태·알림 받기 자리.
- 원칙7·5: 변환 코드 0, 숨김 필드 표시 0(탐침 P1a·b), 라우트·화면 추가 0(`-grep.txt` 8절 + 탐침 P3).
- R-U6-1·R-U6-2 (iii) 닫힘(§3) — 재현 순서 그대로인 테스트, `GET /persons` 1회/2회 실측, 늦은 응답 방지 실측(V4 대조).
- 구현자 판단 6개 계획 모순 0(§4); ① 은 문구 의미 [권고].
- 변이 5건: 3건 기존 묶음 검출, 2건 탐침만 검출(테스트 틈 → [권고]); 구현자 재실행 5건 전부 표와 동일; 11회 저장소 무수정(§5).
- R-U0-3 충족(§6), 보안·범위 위반 0(§7), 증거 통로·R-U6-3 준수(§8).
- **[필수] 0 → 통과.** R-U7-1(코드 1줄)·R-U7-2(탐침 3건 옮기기)는 이 커밋에서 고쳐도, 다음 단위(U8)에 끼워도 된다 — 커밋을 막지 않는다. R-U7-3 은 사용자 결정(U10 또는 문구 1개).
