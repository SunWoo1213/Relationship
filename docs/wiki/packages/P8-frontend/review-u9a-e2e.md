# P8-frontend U9a E2E 3편·27b·프론트 판정 재실행·불변식·RUNNING·tests.md (+ 이월 R-U4-8 · R-U8-1 · R-U8-3) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: **통과 — 재작업 1차 재확인 완료 (2026-10-15 14:46), [필수] 0 · 코드 권고 R-U9a-1·R-U9a-2 닫힘 · 남은 [권고] R-U9a-3 의 커밋 시점 항목(⑦)만.** 재확인 근거는 맨 끝 "재검증 (재작업 1차)" 절 — V2 를 내가 다시 걸어 E2E 1 failed(`card.spec.ts:62`)·Vitest 4 failed 로 양쪽 검출, `serviceWorkers:'block'` 은 대조 시험으로 등록 차단 확인, 판정 명령 재실행 exit 0(135 · E2E 4), 재작업 범위 = `card.spec.ts`·`playwright.config.ts`·tests.md 272행·registry 256행뿐. (아래 14:30 판정 원문은 그대로 둔다.)
결과(1차, 2026-10-15 14:30): 통과 — **[필수] 0, [권고] 3.** 판정 명령 내 재실행 exit 0(typecheck · 9 files 135 passed · build 번들 `index-BsQ5cRBT.css`/`index-CQEgzTJp.js` 가 구현자 1409·메인 1416 과 동일 · `dist/sw.js` 가 `public/sw.js` 와 바이트 동일 · E2E 4 passed, `-judge.txt`). E2E 3편은 판정 24·25·26행의 기대를 가짜 API 의 **상태 변화와 요청 본문·헤더까지** 단언한다(§1 — 가짜 표는 `메서드 경로(쿼리 포함)` 완전 일치만 답하고 표 밖은 중단·기록, 관대하지 않다). 27b: 표 밖 `/api/` 요청(X16 재실행 4 failed)·호스트 밖 요청(X15)·`/api` 밖 경로(내 V4) 전부 실패로 이어진다(§2). 내 변이 6건(V1~V5c) 중 유효 5건: 4건 검출, **V2(원문 줄바꿈 → 공백)는 E2E 에서 살아남고 Vitest 가 잡음** — Playwright `toHaveText` 의 공백 정규화 때문이라 결함이 아니라 E2E 단언의 틈 + tests.md 문구 과장(R-U9a-1). 구현자 X1·X3·X6·X16 재실행이 실패 이름·건수까지 동일(§4). **tests.md: 행 수 135 + 4 = 실제(verbose ✓ 135 = `npx playwright test --list` 4)**, 파일마다 2~3행 표본이 테스트 코드와 일치, 변이 ID 표본 7건 전부 증거에 근거(§5). 불변식 1~10 정정판으로 내가 재실행 전부 기대값(`-invariants.txt`), 원칙5 화면 3·결정 I 캐시 0 유지(§6). R-U0-3: `package.json` 은 `e2e` 스크립트 1줄만, lock 무변경, 의존성 추가 0, `npm audit --omit=dev` 0(§7). 사용자 결정 전제(불변식 1·4 정정 · 구현자 선택 3개)와 코드가 정합(§8). 보안·범위 위반 0(§9).
대상: 작업 트리(기준 HEAD `8fd5463`) — `git diff` 8파일(`.github/workflows/tests.yml` +8 · `docs/RUNNING.md` +53 · `web/package.json` 1줄 · `web/playwright.config.ts` 17/4 · `web/public/sw.js` 8/4 · `web/src/__tests__/push.test.ts` +14 · `sw.test.ts` 34/2 · `web/tsconfig.node.json` 1줄) + 신규 `web/e2e/fixtures.ts`(101행)·`chat.spec.ts`(81)·`card.spec.ts`(123)·`briefing.spec.ts`(65)·`web/src/__tests__/network.test.ts`(16)·`docs/wiki/packages/P8-frontend/tests.md`(280) · `registry.md` U9a 행 6곳 · `01-plan.md` 358·361행(사용자 결정 정정) · 구현자 증거 `evidence/20261015-1404-u9-mutation.txt`(X1~X16, 1483행)·`-1409-u9-final-judge.txt`·`-1410-u9-front-rows.txt`·`-1410-u9-invariants.txt`·`-1410-u9-vitest-verbose.txt`·`-1411-u9-e2e-list.txt`·`-1414-u9-mutation-script.txt`·`-1414-u9-tests-md-check.txt`·`-1415-u9-diff-residue.txt` · 메인 세션 `-1416-u9-main-recheck-{typecheck,test,e2e}.txt`(+ `-1416-u9-main-recheck.txt` exit 254 는 인용 실수 기록). `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U9a 시작" 항목은 근거 문서). 백엔드 행·pytest·회귀는 U9b 몫이라 보지 않았다.
근거 문서: `01-plan.md` 100행(U9 원문) · 판정 표 12~27b행(136~160행) · 120행(판정 규칙 — "가짜 표에 없는 요청은 실패시킨다") · 234행(결정 B (i) CI: E2E 는 ubuntu 만) · 298~299행(결정 J 도구·실 네트워크 0·R-5) · 291행(결정 I 캐시 없음) · 354~367행("지킬 불변식" 1~10, 1·4 는 2026-10-15 정정판) · CLAUDE.md 원칙5·7·8·9 · `review-u4-skeleton.md` 41행(R-U4-8 "baseURL 5173 은 U9 에서 preview 포트로") · `review-u8-pwa-push.md` §11(R-U8-1 처방 "`schedule_id: null` → `#/briefings`·배너 없음 1경우", R-U8-3 처방 "앱 창 고르기 또는 U10 항목") · `review-u0-harness.md` R-U0-3 · `review-u6-card.md` R-U6-3 · 03-log 139~147행(U9a 시작 — 사용자 결정·구현 결과·메인 재실행) · `docs/wiki/security.md` · `docs/wiki/verification.md`.

내 증거(전부 `save_evidence.py` 통로, `docs/wiki/packages/P8-frontend/evidence/`):
- `20261015-1425-verifier-u9a-judge.txt` — `cd web && node --version && npm --version && npm run typecheck && npm test -- --run && npm run build && ls -l dist/… && cmp public/sw.js dist/sw.js && npm run e2e && npx playwright --version && ls ~/Library/Caches/ms-playwright` exit 0. v24.21.0 · 11.19.0 · 135 passed · 번들 해시 동일 · `sw.js 바이트 동일` · E2E 4 passed(4.3s) · Playwright `Version 1.64.0` · 브라우저 `chromium_headless_shell-1248`.
- `20261015-1425-verifier-u9a-mutation.txt`(약 1080행) — V0 대조군 + 내 변이 V1·V2(vitest+e2e)·V3·V4·V5·V5b·V5c + 구현자 X1·X3·X6·X16 재실행 = 12회, 매회 출력 전체(Playwright `list` 리포터 실패 블록·Vitest FAIL 블록 포함) + 끝에 `git status --short -- web`(12회 모두 U9a 작업 트리 그대로, 저장소 무수정).
- `20261015-1428-verifier-u9a-invariants.txt` — 불변식 1~10(1·4 는 정정판 `--exclude-dir=__tests__`) + 추가(e2e 디렉터리 외부 URL·`serviceWorkers` 설정 유무·`app alembic tests scripts` status·verbose ✓ 수).
- 변이 스크립트 원문은 스크래치패드 `vmut_u9a.mjs`(치환 내용은 아래 §4 표에 그대로 옮김 — V5·V5b 무효 사유 포함).

## 1. 판정 24·25·26행 — E2E 가 기대를 실제로 단언하는가 (가짜 API 의 엄격성 포함)

가짜 API(`fixtures.ts` 39~84행)의 성질부터: 표의 키는 `"${method} ${pathname+search}"` 완전 일치(58행)라 쿼리 하나만 달라도 표 밖이고, 표 밖은 `route.abort('failed')` + `unexpected` 기록(64~67행), 값이 함수면 요청마다 호출돼 **상태가 있는 가짜**가 된다(70행). 호스트 밖은 먼저 등록된 규칙이 전부 중단(48~51행). `page.on('request')` 는 `goto` 전에 붙어 앱 파일 요청까지 전부 모은다(45행). 각 spec 끝에서 `expectNoStrayRequests`(90~100행)가 ① 호스트 밖 또는 앱 파일·`/api/` 밖 경로 0 ② `unexpected` 0 ③ 요청 ≥ 1 을 단언한다. → "통과만 하는 관대한 가짜" 가 아니다.

| 행 | 01-plan 기대 | E2E 단언(파일:줄) | 구현자 변이 / 내 변이 | 판정 |
|---|---|---|---|---|
| 24 ㄱ | 발화 → 칩 → 클릭 → 재개 reply → 새로고침 → `GET /api/questions/pending` 복원 | `chat.spec.ts` 36~40행 칩 3개 글자·순서 `['직장','친구','아니요']`(`toHaveText` 배열 = 순서까지) · 43~48행 클릭 → 재개 reply 보임, 눌린 칩 `aria-pressed=true`, 나머지 2개 `toBeDisabled`, 새 칩 8 · 50~56행 **`page.reload()` 뒤** 칩 8 복원·질문 글 보임·이전 reply `toHaveCount(0)`(화면 메모리 소거)·`GET pending` 호출 수 +1 · 59~60행 복원 칩으로 이어서 답함 · 62~76행 요청 본문 `{utterance}`·`{answer:'친구'}`·`{answer:'예'}` 완전 일치, 첫 `/chat` 에 `x-session-id` 없음, `/answers/7`·새로고침 뒤 복원 요청에 `s-1`. 가짜는 `pending` 변수를 POST 마다 바꿔(19·23·27행) 서버 상태를 흉내 — 복원이 **서버 값**에서 오는지 가른다 | X5(나머지 칩 비활성 제거) · X6(복원 제거) · X7(세션 헤더 제거) 검출 · **내 V1**(칩을 가나다순 정렬) 1 failed(40행 `toHaveText` 순서) · X6 내 재실행 1 failed 동일 | ✓ |
| 25 ㄴ | 데스크톱 1280: 사이드바 인물 → 카드·원문, 항목 3개로 화면 3개 전환 / 모바일 390: 서랍 닫힘·탭바 없음 → 메뉴 → 인물 → 카드, 고르면 닫힘, 라우트 3경로 | `card.spec.ts` 48~50행 `navigation[주 메뉴]` 보임·"메뉴 열기" 0 · 53~56행 사이드바 인물 링크 클릭 → URL `#/persons/3`·카드 h1 · 59~61행 "원문 펼치기" → `raw-utterance` 텍스트 · `GET /api/events/31/raw` 1회 · 64~74행 3개 항목 루프: `data-screen` 보임 + URL + `aria-current=page`, 링크 수 3+2 / 88~91행 `navigation` 0·`tablist` 0·메뉴 버튼 · 95~101행 서랍 열림 → "인물" → `navigation` 0 + persons 화면 + URL · 104~110행 서랍 안 인물 → 닫힘 + `#/persons/3` + 카드 + `tablist` 0 · 113~118행 열고 Esc 로 닫아도 URL 불변 | X8(기준 폭 1400) · X9(서랍 안 닫힘) · X10(원문 대신 content) · X11(tablist 추가) 검출 · **내 V5c**(`aria-current` 뒤집기) 1 failed(72행) · **내 V2**(원문 `\n` → 공백) **E2E 4 passed 로 살아남음**, 같은 변이에 Vitest `card.test` 4 failed(`textContent` 완전 일치) | ✓ (V2 는 §3·R-U9a-1) |
| 26 ㄷ | `?schedule_id=N` 직접 열기 → 맨 위·강조 → "지금 브리핑" → 목록 갱신 | `briefing.spec.ts` 43~50행 서버 순서 `[9,7]` 인데 `li` 0번이 `briefing-7`·`data-highlight=true`, 1번 `briefing-9`·강조 없음, 머리줄 `김팀장 · 주간 회의`·줄 문장 · 53~56행 클릭 → **갱신된 문장** 보임·옛 문장 없음·7 이 여전히 맨 위 · 58~61행 POST 본문 `{schedule_id:7}` 1회, `GET /api/briefings` 2회. 가짜는 POST 에서 `lineOf7` 을 바꿔(32행) 재조회 없이는 새 문장이 나올 수 없게 했다 | X12(강조 제거) · X13(맨 위 안 올림) · X14(재조회 제거) 검출 · **내 V3**(POST 본문을 `id+1`) 1 failed(60행 `toEqual`) | ✓ |

## 2. 판정 27b — 표 밖·호스트 밖·`/api` 밖 요청이 실제로 실패로 이어지는가

| 경로 | 처리 | 증거 |
|---|---|---|
| 가짜 표에 없는 `/api/` 요청 | `route.abort('failed')` + `unexpected` 기록 → spec 끝 `expect(api.unexpected).toEqual([])` | X16(`main.tsx` 에 `fetch('/api/stray')`, 화면 영향 0) 구현자 4 failed · **내 재실행 4 failed** "가짜 표에 없는 /api/ 요청" — 화면이 멀쩡해도 잡힌다 |
| preview 호스트 밖 요청 | 48~51행 `abort('blockedbyclient')` + `requests` 에 남아 `strays` 로 | X15(`index.html` 에 `fonts.googleapis`) 구현자 4 failed "앱 파일·/api/ 밖으로 나간 요청" |
| 같은 호스트, `/api/` 도 앱 파일도 아닌 경로 | 가로채기 밖 → 실제 preview 서버로 감 → `requests` 에 남아 `strays` | **내 V4**(`API_BASE='/apiv2'`) 4 failed. 단 실패 지점은 화면 단언(목록 0건·클릭 타임아웃)이었고 끝의 stray 단언까지 가지 못했다 — 검출은 되나 27b 단언 자체가 잡은 것은 아니다(기록) |
| Vitest 쪽 | `network.test.ts` 2건: 전역 `fetch` 가 던지는지(바깥 주소) · `apiFetch('/persons')` 가 가짜 없이 실패하는지 | X4(`test-setup.ts` 차단 제거 → 가짜 성공 응답) 6 failed(network 2 + api 1 + routes 3 부수) |

**V4 가 드러낸 부수 사실**: `vite preview` 는 `server.proxy` 를 그대로 물려받아(`[WebServer] [vite] http proxy error: /apiv2/… ECONNREFUSED` 가 preview 로그에 찍힘) `/api` 로 시작하는 경로가 브라우저 가로채기를 **벗어나면** `localhost:8000` 의 실제 백엔드로 전달된다. 지금은 `page.route('**/api/**')` 가 페이지 요청을 전부 잡고 서비스 워커는 "알림 받기" 를 눌러야만 등록되므로(E2E 는 누르지 않음) 실제로 새는 길은 없다. 그러나 Playwright 의 `page.route` 는 **서비스 워커가 낸 요청을 가로채지 않는다**(`use.serviceWorkers` 기본 `'allow'`). 앞으로 E2E 가 구독 버튼을 누르거나 워커가 `fetch` 를 갖게 되면 27b 가 조용히 뚫린다 → R-U9a-2.

## 3. E2E 단언의 틈 1개 — 내 변이 V2 생존 (결함 아님)

`PersonCardScreen.tsx` 135행 `raw.raw_utterance` 를 `.replace(/\n/g, ' ')` 로 바꿔도 E2E 4 passed. 원인: `card.spec.ts` 60행 `toHaveText(RAW_31)` — Playwright 의 문자열 `toHaveText` 는 앞뒤 공백을 지우고 연속 공백(줄바꿈 포함)을 하나로 접어 비교한다. `RAW_31` 의 `\n` 이 공백이 돼도 같다고 본다. 같은 변이를 Vitest 가 `card.test.tsx` 4건(`textContent` 완전 일치, U6-M3 계열)으로 잡으므로 **원문 보존 자체는 자동 판정 18행이 지킨다**. 문제는 ① E2E 25행이 "원문 그대로" 를 실제로는 "공백 정규화 후 같음" 으로만 보고 있고 ② tests.md 272행이 "원문(줄바꿈·이모지 포함) 그대로" 라고 적어 단언보다 강하게 말한다는 점. 처방은 R-U9a-1.

## 4. 변이 시험 (`-mutation.txt`, 저장소 무수정 — 12회 전부 끝의 `git status --short -- web` 이 U9a 작업 트리 그대로)

| 변이 | 치환(사본 `web/`, 한 곳) | 결과 | 실패 위치 | 뜻 |
|---|---|---|---|---|
| V0 대조군 | 없음 | E2E 4 passed | — | 사본·심볼릭 링크·포트 4173 정상 |
| **V1** | `ChatScreen.tsx` `question.options.map(` → `[...question.options].sort().map(` | **1 failed** | `chat.spec` 40행 칩 순서 | 검출 — 원칙7 "options 순서 그대로" |
| **V2** | `PersonCardScreen.tsx` 135행 `raw.raw_utterance` → `.replace(/\n/g, ' ')` | Vitest **4 failed** / E2E **4 passed(생존)** | `card.test` "첫 펼침 … 글자 그대로" 외 3 | §3 — E2E 단언 틈(R-U9a-1) |
| **V3** | `BriefingScreen.tsx` `postBriefingRun(id)` → `postBriefingRun(id + 1)` | **1 failed** | `briefing.spec` 60행 본문 `{schedule_id:7}` | 검출 — 가짜 표는 본문을 보지 않으므로 단언이 있어야만 잡히는 경우 |
| **V4** | `client.ts` `API_BASE='/api'` → `'/apiv2'` | **4 failed** | 화면 단언(목록 0·클릭 타임아웃) | 검출 — §2 부수 사실 |
| V5 / V5b | `AppShell.tsx` 28행 `aria-current={undefined}` / `… && route.name === 'nope' ? …` | webServer 빌드 실패 exit 2 | — | **무효**(tsc `noUnusedParameters` / 겹치지 않는 비교) — 구현자 X5·6·7·13 1차와 같은 현상 |
| **V5c** | 같은 줄 `===` → `!==`(현재가 아닌 항목에 붙임) | **1 failed** | `card.spec` 72행 `aria-current` | 검출 |
| X1 재실행 | `sw.js` `pathname === "/"` → `true` | 2 failed | 구현자 1404 와 이름·건수 동일(R-U8-3 신규 2건) | 구현자 표 신뢰 |
| X3 재실행 | `AppShell` null 이면 이동 생략 | 1 failed | R-U8-1 신규 1건, 동일 | 〃 |
| X6 재실행 | 복원 제거 | 1 failed | `chat.spec` 53행, 동일 | 〃 |
| X16 재실행 | `/api/stray` | 4 failed | 4편 전부 "가짜 표에 없는 /api/ 요청", 동일 | 〃 |

구현자 증거 대조: X1~X16 "exit 1" 16건 중 X5·X6·X7·X13 의 1차는 `Process from config.webServer was not able to start. Exit code: 2`(빌드 실패) 뿐이고 테스트가 돌지 않았다 — 스크립트가 "exit ≠ 0 → 검출" 로 찍어 **무효를 검출로 표시**한다(구현자가 알아채고 1265행 이후 타입 맞는 형태로 재실행, 4건 모두 1 failed). 2차 치환 원문은 `-1414-u9-mutation-script.txt` 에 있으나 **1차 치환 원문은 어디에도 없다**(출력만 남음). R-U6-3 "스크립트 원문 보존" 의 취지에서 1차본도 남겼어야 한다 → R-U9a-3 ②.

## 5. tests.md 정확성

- **행 수**: `grep -cE '^\| [a-z]+\.test\.tsx?::'` → **135**, `^\| e2e/…spec\.ts::` → **4**. 파일별 api 6·proxy 6·routes 14·chat 22·card 29·briefing 19·sw 16·push 21·network 2 = 135 — 구현자 verbose(`-1410-u9-vitest-verbose.txt` ` ✓ src/__tests__` 135줄, 내 재계수 동일)·`-1411-u9-e2e-list.txt`(`Total: 4 tests in 3 files`)·내 judge 135/4 와 일치. 구현자의 기계 대조(`-1414-u9-tests-md-check.txt`)도 행↔verbose 1:1, 미대응 0, 중복 0.
- **설명 ↔ 코드 표본**(파일마다 2~3행, 테스트 파일 직접 grep): `api.test` 49~53행 `sessionId: null` → `headers {}` ✓ · `proxy.test` 35~37행 `/api?x=1` → `/?x=1`, 40~42행 `/apix/persons` 그대로 ✓ · `routes.test` 130행 `localStorage.length === 0`, 133~134행 1023/1024 ✓ · `chat.test` 192~196행 `isComposing:true` Enter → 전송 아님, 386~387행 `schedules:3` 만 → 링크 0 ✓ · `card.test` 121~122행 searchbox·combobox 없음, 311~315행 `data-section` 순서, 360행 `source_count 0` 버튼 없음 ✓ · `briefing.test` 232~238행 `parseScheduleId` `x=1&schedule_id=3` → 3, 285행 404 잠금 ✓ · `push.test` 115~118행 `AQI`→[1,2]·`-__-`→[251,255,254] ✓ · `sw.test` 210~212행 리스너 정렬 목록, 215~219행 skipWaiting 1회 ✓ · `network.test` 2건 ✓ · E2E 4행은 §1 의 줄 번호 그대로 ✓. 어긋남: **272행 "원문(줄바꿈·이모지 포함) 그대로"** — 실제 단언은 공백 정규화 비교(§3).
- **변이 ID 표본 7건**(증거 파일에서 `×` 줄 확인): U5-M3 → `chat.test` 세션 2건(`-1325-u5-mutation.txt` 148~149행) ✓ · U6-V2 → `card.test` 섹션 7개·각 섹션 값·빈 섹션(`-1847-verifier-u6-mutation.txt` 415~419행) ✓ · U7-M20 → `parseScheduleId`(`-1945-u7-mutation.txt` 5202행) ✓ · U7-M15 → **`briefing.test`** "빈 목록이면 빈 상태 문구 하나"(3747~3993행 `❯ briefing.test.tsx 1 failed`) ✓ — 같은 이름의 `card.test` 행(149행)을 `—` 로 둔 것이 맞고, 구현자 대조 스크립트의 "ID 불일치 2건" 중 하나는 **이름 충돌 오탐**이다(설명이 tests.md·03-log 어디에도 없다 → R-U9a-3 ③) · U8-M31 → push 3건(`-2017-u8-mutation-rework.txt` 193~195행) ✓ · U4-M4 → api 2건(`-2031-u4-mutation-full-1.txt` 254~255행) ✓ · U8-V5 → 아이콘(`-2024-verifier-u8-mutation.txt` 1365행) ✓ · U9-X1~X16 → §4 재실행 4건 동일 ✓.
- 머리 설명(1~38행)의 세는 명령·접두사 표·`—` 의 뜻·`it.each` 1줄 규칙은 표 본문과 일치. 61행 "두 시도 모두 증거에 남아 있다" 는 출력에 한해 참(치환 원문은 2차만, §4).

## 6. 불변식·원칙5·결정 I (`-invariants.txt`)

| # | 명령(정정판) | 결과 | 기대 |
|---|---|---|---|
| 1 | `grep -rn "push-dev" web/src web/public web/index.html --exclude-dir=__tests__` | 0건(exit 1) | ✓ — 구현자 `-1410-u9-invariants.txt` 는 정정 전 명령으로 테스트 4줄이 찍혔고 정정판 실행은 없었다(이 파일이 보충) |
| 2 | 음성 입력 API | 0건 | ✓ |
| 3 | `sw.js` fetch 리스너·`caches.` | 0건 | ✓ 결정 I |
| 4 | `raw_utterance` `--exclude-dir=__tests__` | `PersonCardScreen.tsx` 3·4(주석)·135·172, `types.ts` 115·129 — 두 응답 타입 + 원문 표시 컴포넌트뿐 | ✓ |
| 5 | 쓰기 라우트 수 | 현재 4 = 50fd7fc 4 | ✓ |
| 6 | `git diff --stat 50fd7fc -- app/push/devpage` | 빈 출력 | ✓ |
| 7 | `VITE_*(KEY|SECRET|TOKEN)` | 0건 | ✓ |
| 8 | 추적 파일에 node_modules·dist·test-results·playwright-report | 0건(`.gitignore` 가 Playwright 산출물 4종을 막음) | ✓ |
| 9 | 외부 글꼴·CDN(`web/e2e` 까지 넓혀서) | 0건 | ✓ |
| 10 | 서랍 파일 | `AppShell.tsx` 1개 | ✓ 원칙5 |

원칙5: `routes.ts`·`App.tsx` diff 0, E2E 가 `data-screen` 3개·링크 3+인물 수를 단언(`card.spec` 74행). 결정 I: `sw.js` 변경은 `notificationclick` 의 창 고르기 4줄뿐, 리스너·캐시 변화 0(`sw.test` "리스너는 넷뿐"·"캐시 API 호출 없음" 통과).

## 7. R-U0-3 · 의존성 · Mac/Windows

- `web/package.json` diff = `"e2e": "playwright test --pass-with-no-tests"` → `"playwright test"` 1줄. `package-lock.json` `git status` 빈 출력(바이트 무변경). 의존성 추가 0 — `@playwright/test` 1.64.0 은 U4 부터 devDependencies, `node_modules/@playwright/test` 1.64.0 = `npx playwright --version` 1.64.0 = CI·RUNNING 의 `npx playwright@1.64.0`. `npm audit --omit=dev` "found 0 vulnerabilities"(judge 의 `npm ci` 가 보고한 7 high 는 dev 의존성).
- Mac·Windows: `playwright.config.ts` `webServer.command` `npm run build && npm run preview -- --port 4173 --strictPort` — Playwright 가 셸(`/bin/sh` / `cmd.exe`)로 띄우므로 `&&` 양쪽 동일, `--strictPort` 로 4173 점유 시 바로 실패(RUNNING 에 "비어 있어야 한다" 명시). npm 스크립트에 셸 전용 명령 0. RUNNING ②·④·⑥ 에 bash·PowerShell 블록 각각(5.1 의 `&&` 불가를 적고 한 줄씩), `$env:VITE_API_TARGET="…"; npm run dev` ✓. CI windows 는 E2E 를 돌리지 않으므로(결정 B (i)) 로컬 Windows E2E 는 미확인 — 기록.
- `tsconfig.node.json` `include` 에 `e2e` — `allowImportingTsExtensions`·`noEmit` 이 이미 있어 `./fixtures.ts` import 가 타입 검사만 받고 산출물은 없다(typecheck exit 0, untracked `.js` 0).

## 8. 사용자 결정 전제 · 구현자 선택 3개

| 항목 | 코드 | 판정 |
|---|---|---|
| 불변식 1·4 정정(제품 코드 기준) | `01-plan.md` 358·361행에 `--exclude-dir=__tests__` + 정정 사유. 내 재실행 §6 | 정합 |
| (a) R-U8-3 을 `new URL(c.url).pathname === "/"` 긍정 판별로 | `sw.js` 62~64행 `list.find(...)`, 65행 `if (client)` → focus+postMessage, 없으면 기존 `openWindow`. 앱은 루트 `/` 에서 해시 라우팅(`start_url "/#/chat"`, preview·dev 모두 pathname `/`)이라 앱 창 = pathname `/` 가 맞다. `/push-dev/`·`/api/docs` 는 pathname 이 달라 제외. 리터럴 `push-dev` 를 쓰지 않아 불변식 1 과 충돌 없음 | 적합 — `sw.test` 2건(앱 아닌 창 2 + 앱 창 → 앱 창만 / 전부 앱 아님 → openWindow, 다른 창 무접촉) + X1·X2 검출. 기록: 앱이 하위 경로로 배포되면(P9 결정) 이 비교를 바꿔야 한다 — registry 에 한 줄 |
| (b) CI web job 에 ubuntu 전용 Playwright 설치·`npm run e2e` | `tests.yml` 177~184행 `if: runner.os == 'Linux'` 2단계, `npx playwright@1.64.0 install --with-deps chromium`(R-8 버전 고정 — 로컬 `@playwright/test` 1.64.0 과 같아 npx 가 추가 내려받기 없이 로컬 바이너리를 쓴다) | 적합 — 결정 B (i) 원문 그대로. 기록: 빌드가 CI 에서 두 번 돈다(`npm run build` 단계 + webServer) — 수십 초, 허용 |
| (c) `tsconfig.node.json` include `e2e` | §7 | 적합 — E2E 코드도 타입 검사를 받는다(변이 V5·V5b 가 바로 그 효과로 빌드에서 막혔다) |

이월: **R-U4-8** 닫힘(`baseURL` 4173 + `webServer`, 5173 흔적 0). **R-U8-1** 닫힘(`push.test` 410~422행 — 내 U8 처방 문장 그대로, X3 검출). **R-U8-3** 닫힘(위 (a)).

## 9. 보안·범위

- `app/`·`alembic/`·`tests/`·`scripts/` status 빈 출력. 삭제 0. `web/` 밖 변경은 CI yml·RUNNING·위키뿐.
- 비밀: 새 파일의 `http://` 는 `playwright.config.ts` 7행 `localhost` 뿐, `e2e/` 에 외부 주소 0. 가짜 데이터는 가상 이름(김팀장·이서준·민지). 세션 값 `'s-1'` 더미.
- 실 네트워크: E2E 는 호스트 밖·표 밖 전부 중단(§2). `test-setup.ts` diff 0, `throw` 유지.
- 원칙7: E2E 가 칩·브리핑 줄·원문을 서버 문자열 그대로 단언(V1·X10·X14). 상담·감정 어휘 0.

## 10. 소견

- **[권고] R-U9a-1 · E2E 원문 단언을 완전 일치로 + tests.md 문구 정정.** `card.spec.ts` 60행 `await expect(card.getByTestId('raw-utterance')).toHaveText(RAW_31)` 는 공백 정규화 비교라 줄바꿈·연속 공백·꼬리 공백 훼손을 못 잡는다(내 V2 생존, §3). 처방: `expect(await card.getByTestId('raw-utterance').textContent()).toBe(RAW_31)` 1줄로 바꾸고(Vitest 18행과 같은 강도), `tests.md` 272행 "원문(줄바꿈·이모지 포함) 그대로" 는 단언에 맞게 고치거나 위 수정 뒤 유지 + 결과 열에 `U9-V2`(생존 → 수정 후 검출) 기록. 수정하면 변이 V2 를 다시 돌려 `-mutation.txt` 에 붙인다. 커밋을 막지 않는다(Vitest 가 같은 성질을 지킨다).
- **[권고] R-U9a-2 · `playwright.config.ts` `use.serviceWorkers: 'block'` 1줄(27b 안전망 보강).** `page.route` 는 서비스 워커가 낸 요청을 가로채지 않고, `vite preview` 는 `server.proxy` 를 물려받아 가로채기를 벗어난 `/api/*` 를 실제 `localhost:8000` 으로 넘긴다(§2 V4 로그). 지금은 E2E 가 워커를 등록하지 않아 새는 길이 없지만, 뒤에 "알림 받기" E2E 를 더하면 27b 가 조용히 뚫린다. 대안: `vite.config.ts` 에 `preview: { proxy: {} }`(preview 에서는 프록시 없음). 둘 중 하나, 또는 둘 다. 커밋을 막지 않는다.
- **[권고] R-U9a-3 · 03-log U9a 완료 항목·tests.md·변이 스크립트에 적을 것.** ① 변이 스크립트가 webServer 빌드 실패(`Process from config.webServer was not able to start`)를 "검출" 로 찍는다 — 구현자 X5·6·7·13 1차와 내 V5·V5b 가 그 경우. 다음 단위부터 그 문구가 보이면 `무효` 로 찍게 1줄(FIX-033 "변이 유효성"). ② 1차 치환 원문이 보존되지 않았다(스크립트 파일은 2차본) — 03-log 에 1차 치환 4건의 내용을 적거나 "원문 미보존, 출력만" 이라고 명시(R-U6-3). ③ `-1414-u9-tests-md-check.txt` 의 "ID 불일치 2건" 해설: `card.test`/`briefing.test` 의 같은 이름 "빈 목록이면 빈 상태 문구 하나" 충돌(U7-M15 는 briefing, card 행 `—` 가 맞다) · proxy 행의 `U4-R1` 은 괄호 설명문 안의 옛 이름 근거. ④ 구현자 `-1410-u9-invariants.txt` 는 정정 전 명령이라 1번이 4건 — 정정판 결과는 내 `-1428-verifier-u9a-invariants.txt`(0건)를 참조로 적는다. ⑤ registry: `@playwright/test` 버전을 올릴 때 `tests.yml` 182행·RUNNING 81행의 `playwright@1.64.0` 도 같이 — 세 곳 동기 한 줄; `sw.js` 앱 창 판별이 루트 배포 전제(P9)라는 한 줄; `web/e2e/.gitkeep` 은 이제 불필요(삭제는 선택). ⑥ 03-log 의 "Chrome Headless Shell 156.0.8078.4" 는 내 환경 출력으로는 확인 못 했다(`ls ~/Library/Caches/ms-playwright` 는 빌드 번호 `chromium_headless_shell-1248` 만) — 출처(`npx playwright install` 출력)를 적거나 빌드 번호로 바꾼다. ⑦ 내 증거 3파일 경로 · "(pending)" 6칸 → 해시 · Refs `P8-frontend U9 원칙5 원칙7 원칙8 원칙9 R-U4-8 R-U8-1 R-U8-3 R-U0-3 R-U6-3 FIX-033 FIX-034`.
- 기록(소견 아님): ⓐ V4 는 화면 단언이 먼저 실패해 끝의 stray 단언까지 가지 않았다 — 27b 의 "요청 URL 단언" 이 **단독으로** 잡는 경우는 X15·X16 두 변이로 확인됐다 ⓑ E2E 4건이 `fullyParallel` 4 워커로 preview 서버 하나를 공유한다 — 가짜 API 는 페이지 단위라 간섭 없음(V0 포함 9회 실행 전부 안정) ⓒ `chat.spec` 는 `retries: 0` 그대로라 불안정이 숨지 않는다 ⓓ `playwright.config.ts` 15행 주석 "Mac(zsh)" — 실제 셸은 `/bin/sh`, 뜻은 같다 ⓔ RUNNING ⑥ "`npm run build` — web/dist 가 비워지고" 는 `vite.config.ts` `emptyOutDir: true` 와 일치, "처음 열면 `#/chat`" 은 `routes.ts` 기본 경로와 일치, 프록시 예시 `GET /api/persons → GET http://localhost:8000/persons` 는 `stripApiPrefix` 와 일치.

## 11. 판정 근거 요약

- 판정 명령 내 재실행 exit 0, 135 passed, 번들·`sw.js` 동일, E2E 4 passed(`-judge.txt`).
- E2E 3편이 24·25·26행 기대를 상태 있는 가짜·요청 본문/헤더·순서·속성까지 단언하고, 표 밖·호스트 밖·`/api` 밖 요청이 실패로 이어진다(§1·§2). 구현자 X1~X16 전부 검출(1차 무효 4건 재실행 포함), 내 재실행 4건 동일(§4).
- 내 유효 변이 5건 중 4건 검출, V2 생존은 E2E 단언 틈이며 Vitest 가 같은 성질을 지킨다(R-U9a-1).
- tests.md 행 수 = 실제(135·4), 표본 설명·변이 ID 전부 근거 있음, 문구 과장 1곳(§5).
- 불변식 1~10 정정판 전부 기대값, 원칙5·결정 I 유지(§6). R-U0-3 충족, Mac·Windows 명령 정합(§7). 사용자 결정 전제·구현자 선택 3개 정합, 이월 3건 닫힘(§8). 보안·범위 위반 0(§9).
- **[필수] 0 → 통과.** R-U9a-1(단언 1줄 + 문구)·R-U9a-2(설정 1줄)는 이 커밋에서 고쳐도, U9b·U10 에 끼워도 된다. R-U9a-3 은 03-log 완료 항목·registry·스크립트(메인 세션·다음 단위).

## 재검증 (재작업 1차)

검토자: verifier (fable) · 2026-10-15 14:46 · 대상: HEAD `8fd5463` + 재작업된 작업 트리(frontend-agent 14:35, 메인 세션 03-log 14:36). 코드·계획·카드 수정 0. 저장소 밖 사본(`scratchpad/vmutweb9a`, `node_modules` 심볼릭 링크)에서만 변이·대조를 돌렸고 매 회차 끝의 `git status --short -- web` 이 재작업 작업 트리 그대로다.

내 증거(전부 `save_evidence.py`, `docs/wiki/packages/P8-frontend/evidence/`):
- `20261015-1443-verifier-u9a-rework-v2-mutation.txt`(172행) — V2(`PersonCardScreen.tsx` `raw.raw_utterance` → `.replace(/\n/g, ' ')`)를 **재작업된 스펙이 든 새 사본**에 다시 걸어 Vitest → E2E 순으로 전체 출력.
- `20261015-1443-verifier-u9a-rework-judge.txt`(68행) — 실제 작업 트리에서 `npm run typecheck && npm test -- --run && npm run e2e` + `git diff --stat -- web/src/screens/PersonCardScreen.tsx` + `git status --short -- web` + `card.spec.ts` 59~63행 + `playwright.config.ts` `serviceWorkers` 줄 + `playwright.config.ts` diff --stat. exit 0.
- `20261015-1444-verifier-u9a-rework-x16-recheck.txt` — 구현자 X16(`main.tsx` 에 `fetch('/api/stray')`)을 `serviceWorkers:'block'` 설정 아래에서 재실행.
- `20261015-1446-verifier-u9a-rework-swblock3.txt`(81행) — `serviceWorkers` 대조 시험(유효본). 사본 `e2e/` 에 확인용 스펙 1개(`page.goto('/#/chat')` 뒤 `navigator.serviceWorker.register('/sw.js')` 를 3초 경주로 시도, 결과 문자열이 `registered:` 로 시작하면 실패) → ① 현재 설정 `'block'` ② 사본 설정만 `'allow'`.
- **무효 2건(기록)**: `-1443-verifier-u9a-rework-swblock.txt` — 같은 시험 1차. 내 스펙이 `page.evaluate` 콜백 안에서 `navigator` 를 써서 `tsconfig.node.json`(`lib: ["ES2023"]`, DOM 없음, `include: e2e`) 의 `tsc -b` 가 webServer 빌드를 막음(`Process from config.webServer was not able to start. Exit code: 2`) — R-U9a-3 ① 과 같은 종류의 무효. `-1444-verifier-u9a-rework-swblock2.txt` — 문자열 `evaluate` 로 고친 2차. ① 은 `register()` 가 30초 안에 결정되지 않아 `page.evaluate: Test timeout` 으로 끝났고(실질은 "등록 안 됨"), ② 는 114ms 에 `registered:http://localhost:4173/`. 대조 자체는 성립하나 ① 이 timeout 으로 찍혀 3차(swblock3)로 깔끔히 남겼다.
- 변이·대조 스크립트 원문은 스크래치패드 `vmut_u9a.mjs`(1차 리뷰와 동일, V2 치환은 §4 표 그대로)·`swblock_u9a.mjs`(치환: 사본 `playwright.config.ts` `serviceWorkers: 'block'` → `'allow'` 1곳, 추가 파일: 사본 `e2e/sw-block.spec.ts` 위 내용). 저장소에는 두 파일 모두 없다.

### 1. R-U9a-1 — 원문 완전 일치 단언 (`web/e2e/card.spec.ts` 59~63행)

| 확인 | 근거 | 판정 |
|---|---|---|
| 단언이 바뀌었나 | 60행 주석 "toHaveText 는 공백을 정규화해 … textContent 완전 일치로 단언한다 (R-U9a-1)", 61행 `toBeVisible()`, 62행 `expect(await card.getByTestId('raw-utterance').textContent()).toBe(RAW_31)` — 내 §10 처방 1줄과 같은 강도(Vitest `card.test.tsx` 421행 `expect(raw.textContent).toBe(RAW_A)` 와 같은 형태). `RAW_31`(7행)은 `'어제 김팀장님이\n내 보고서를 칭찬해 주셨다 😀'` 로 줄바꿈·이모지 포함 그대로(judge 58~62행) | ✓ |
| V2 를 **직접** 다시 걸면 E2E 가 실패하나 | `-1443-…-v2-mutation.txt` 129행 `✘ 4 e2e/card.spec.ts:43:3 › 데스크톱 폭 1280px …`, 136~147행 `expect(received).toBe(expected)` · `- 어제 김팀장님이` `- 내 보고서를 칭찬해 주셨다 😀` / `+ 어제 김팀장님이 내 보고서를 칭찬해 주셨다 😀` · `> 62 |`, 156~159행 `1 failed / 3 passed` · `변이 V2 e2e 결과: exit 1`. 같은 사본에서 Vitest 도 `card.test.tsx (29 tests | 4 failed)` · `Tests 4 failed | 131 passed (135)`(12·110~115행) — 1차 리뷰 §3 과 동일 | ✓ **1차 리뷰 때 살아남던 V2 가 이제 E2E 에서도 검출** |
| 구현자 증거와 대조 | 구현자 `-1435-u9a-rework-v2-mutation.txt`: 같은 테스트 1 failed, 같은 62행, 같은 Expected/Received 두 줄, `3 passed`. 이름·건수·줄·diff 전부 일치 | ✓ |
| 되돌린 뒤 통과 · diff 0 | judge 44행 `4 passed (4.2s)`, 45행 아래 `git diff --stat -- PersonCardScreen.tsx` **빈 출력**, 46~57행 `git status --short -- web` 에 `web/src/screens/` 없음. 구현자 `-1435-u9a-rework-e2e.txt` 도 `4 passed` | ✓ |
| 기록(소견 아님) | `PersonCardScreen.tsx` 의 mtime 이 14:35:43 — 구현자는 **실제 트리**에 변이를 걸고 되돌렸다(나는 사본). 구현자 증거 4파일 어디에도 `git diff` 출력이 없어 03-log "diff 0(`evidence/20261015-1435-u9a-rework-*`)" 의 직접 근거는 구현자 파일이 아니라 **내 judge 45행**이다. 결과는 diff 0 이므로 문제 없음. 다음부터 실제 트리에 변이를 걸면 되돌린 뒤 `git diff --stat` 을 같은 증거에 넣는다(R-U6-3 취지) | 기록 |

### 2. R-U9a-2 — `use.serviceWorkers: 'block'` (`web/playwright.config.ts` 16~17행)

| 확인 | 근거 | 판정 |
|---|---|---|
| 설정 1줄 + 주석 | 16행 주석 "page.route 는 서비스 워커 요청을 가로채지 못한다 -- 워커를 막아 27b 가 뚫리지 않게 한다 (R-U9a-2)", 17행 `serviceWorkers: 'block'`. `git diff --stat` 17 → 19(+2 줄, judge 67행). Playwright 1.64.0 자체 문서가 같은 권고(`node_modules/playwright-core/types/types.d.ts` 4444~4448행 "page.route … will not intercept requests intercepted by Service Worker … We recommend disabling Service Workers … by setting serviceWorkers to 'block'"), 타입 `"allow"\|"block"`(11720행) | ✓ |
| E2E 4편 통과 | judge 44행 `4 passed (4.2s)`; 구현자 `-1435-u9a-rework-e2e.txt` · 메인 `-1436-u9a-rework-main-e2e.txt` 모두 `4 passed` | ✓ |
| 27b 의미 유지 | X16 재실행(`-1444-…-x16-recheck.txt`) 4편 전부 `✘` · `Error: 가짜 표에 없는 /api/ 요청` · `fixtures.ts` 98행 `expect(api.unexpected, …).toEqual([])` · `4 failed` — 1차 리뷰 §2 와 동일 | ✓ |
| 설정이 실제로 워커를 막나 | `-1446-…-swblock3.txt`: ① `'block'` → `SW_REGISTER_RESULT=pending-after-3s(등록 안 됨)` · `1 passed` · exit 0(24~28행) ② 사본만 `'allow'` → `SW_REGISTER_RESULT=registered:http://localhost:4173/`(109ms) · `1 failed` · exit 1(45~68행). 즉 `'allow'` 였다면 E2E 가 "알림 받기" 를 누르는 순간 `/sw.js` 가 실제로 등록되고, `'block'` 에서는 등록 자체가 성립하지 않는다 — 1차 리뷰 §2 의 우려가 재현됐고 처방이 그것을 막는다 | ✓ |

### 3. tests.md 272행 · registry 256행

- `tests.md` 272행 "원문 표시(`textContent` 완전 일치 — 줄바꿈·이모지 포함 글자 그대로. `toHaveText` 는 공백을 정규화해 R-U9a-1 로 바꿈)" = 62행 단언과 일치(1차 §5 의 과장 해소). 결과 열 "U9-V2(원문 `\n`→공백: 수정 전 E2E 생존, 수정 후 1 failed — `evidence/20261015-1435-u9a-rework-v2-mutation.txt`)" — 파일 존재·내용(1 failed) 일치, "수정 전 생존" 은 내 `-1425-verifier-u9a-mutation.txt`. ✓
- 다른 행 변경 0: `wc -l` 280(1차와 동일), `^\| [a-z]+\.test\.tsx?::` 135 · `^\| e2e/…spec\.ts::` 4(동일), `grep -n R-U9a` 가 tests.md 에서 **272행 하나**. 재작업 전 사본이 없어 바이트 대조는 못 했다 — 행 수·표 행 수·R-U9a 언급 위치로 판정. ✓
- `registry.md` 256행 비고 "**재작업 1차** — R-U9a-1 원문 단언을 `textContent` 완전 일치로(verifier V2 검출 `evidence/*-u9a-rework-v2-mutation.txt`), R-U9a-2 `playwright.config.ts` `use.serviceWorkers:'block'`" = 코드와 일치. `grep -n R-U9a` 가 registry 에서 **256행 하나**. `U9a` 가 든 행은 239·240·251·256·257·258·259 = 7행 — 1차 리뷰에 "6곳" 이라 적은 것은 내 계수 차이이며 7행의 내용은 전부 1차 §5·§7·§8 에서 본 것이다(재작업 전 registry diff 는 구현자 `-1415-u9-diff-residue.txt` 에 없어 행 추가 여부는 증거로 못 가른다 — 기록). 256행 끝 "Chrome Headless Shell 156.0.8078.4" 는 1차 R-U9a-3 ⑥ 그대로(구현자 보고 출처, 03-log ⑤ 에 기록됨). ✓

### 4. 재작업 범위

- `git diff --stat -- web .github docs/RUNNING.md`: 구현자 재작업 전 `-1415-u9-diff-residue.txt`(8 files, 130+/10-)와 지금(8 files, 132+/10-)의 차이는 **`web/playwright.config.ts` 17 → 19** 뿐. 다른 7파일 줄 수 동일.
- 내 1차 증거(14:28) 이후 mtime 이 바뀐 파일: `web/` 은 `e2e/card.spec.ts`(14:35:11)·`playwright.config.ts`(14:35:12)·`src/screens/PersonCardScreen.tsx`(14:35:43, diff 0 — 위 §1 기록) 3개뿐(`node_modules`·`dist`·`test-results` 제외). `docs/` 는 `tests.md`(14:36:12)·`registry.md`(14:36:15)·`03-log.md`(14:36:41, 메인 세션)·`HANDOFF.md`(메인 세션)·이 리뷰 파일. `app/`·`alembic/`·`tests/`·`scripts/`·`.github/` 변경 0.
- 03-log U9a 항목 맨 끝: "재작업 1차 결과(frontend-agent, 14:35)" 와 "R-U9a-3 기록(메인 세션)" ①~⑤ 존재(1차 §10 의 ①~⑥ 을 메인 세션이 ⑤ 로 묶음). ⑦(내 증거 경로 · "(pending)" → 해시 · Refs)은 커밋 시점 몫이라 아직 열려 있다.

### 5. typecheck · Vitest 135 · E2E 4 재실행

judge(`-1443-verifier-u9a-rework-judge.txt`) exit 0: `tsc -b` 출력 없음(13~15행) · `Test Files 9 passed (9)` · `Tests 135 passed (135)`(19~20행) · `4 passed (4.2s)`(44행). 구현자 `-1435-u9a-rework-{typecheck,test,e2e}.txt`(exit 0 · 135 · 4 passed)·메인 `-1436-u9a-rework-main-e2e.txt`(4 passed)와 동일.

### 6. 판정

- **R-U9a-1 닫힘, R-U9a-2 닫힘. [필수] 0.** 재작업은 권고 2건의 처방 범위(단언 1줄 + 주석, 설정 1줄 + 주석, 문서 2행)를 넘지 않았고 제품 코드 변경 0.
- 남은 [권고]: **R-U9a-3 ⑦**(커밋 시점 — 03-log 완료 항목에 verifier 증거 경로 1차 3 + 재검증 4(무효 2 포함) · registry "(pending)" 6칸 → 해시 · Refs `P8-frontend U9 원칙5 원칙7 원칙8 원칙9 R-U4-8 R-U8-1 R-U8-3 R-U0-3 R-U6-3 FIX-033 FIX-034`). 그 밖 ①~⑥ 은 03-log 에 기록됐다.
- 기록 2건(소견 아님): §1 "실제 트리 변이는 되돌린 뒤 diff --stat 을 같은 증거에" · §3 registry U9a 행 수 7 과 1차 "6곳" 의 차이. **U9a 커밋 가능.**
