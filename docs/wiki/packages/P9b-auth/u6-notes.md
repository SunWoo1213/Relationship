# P9b-auth U6 메모 (frontend-agent, 2026-11-15) — 메인이 03-log·tests.md·registry 로 옮긴다

> 03-log·tests.md·registry.md 는 백엔드 에이전트가 동시에 고치고 있어 직접 쓰지 않았다. 이 파일의 세 절을 그대로 옮기면 된다.

## 1. 03-log 메모

- **U6 완료 (frontend-agent)**: 관문 방식(결정 L) — `App` 이 `GET /auth/me` → 200 앱 틀 / 401 로그인·가입 화면(`AuthScreen`) / 그 밖(연결 실패·5xx) 한 줄 안내 + 다시 시도. 로그인 뒤 어떤 API 든 401 이면 관문으로(`client.ts` `onUnauthorized`). `X-Session-Id`·세션 저장·`invalid_session_id` 처리 전부 제거, `credentials: 'same-origin'` 명시, 204 는 본문을 읽지 않음. 대화 기록은 마운트 때 `GET /chat/history?limit=50`(결정 I) + 미답변 칩은 `/questions/pending` 을 같은 `question_id` 의 기록 줄에 붙임. 로그아웃은 현재 푸시 구독 endpoint 를 함께 보내고, 401 이면 "이미 로그아웃됨" 으로 관문. 프록시 `xfwd: true`.
- **기준선**: Vitest 156 passed(9파일) → U6 후 188 passed(10파일, +32). typecheck 통과, build 통과, E2E 5 passed(기존 4 + `auth.spec.ts` 1). 기준선 첫 시도 `u6-baseline-vitest` 는 저장소 루트에서 `--root` 없이 돌려 E2E 파일을 vitest 가 줍는 오류(cwd 실수, 코드 무관) — 정식 기준선은 `u6-baseline-vitest-web`(`--root web`). 계획의 판정 명령 `npm --prefix web exec -- vitest run` 은 **저장소 루트에서는 `--root web` 이 필요**하다(`web/` 안에서는 불필요) — 판정 표 #8 명령을 `--root web` 로 읽어야 한다.
- **sw.js 확인(계획 리스크 항목)**: `web/public/sw.js` 는 `install`·`activate`·`push`·`notificationclick` 리스너뿐이고 `fetch` 리스너·`caches`·`cache` 문자열이 0건(`evidence/*-u6-sw-no-cache2.txt` grep -c 0, `*-u6-sw-no-cache.txt` 리스너 목록). `/api` 응답은 캐시되지 않는다 — 다른 계정 응답 노출 경로 없음. 알림 클릭 `open-briefing` 메시지는 앱 틀이 열린 창만 듣는다(관문 화면에서는 무시, 새 창을 여는 경로는 해시 주소만 열어 관문이 먼저 뜸).
- **바꾼 기존 단언(전부 세션·관문 때문, 계획이 허용한 범위)**:
  1. `api.test.ts` — "POST 는 JSON 본문과 X-Session-Id 헤더를 보낸다"(헤더 `X-Session-Id: abc-1` 단언) → Content-Type 만·`X-Session-Id` 없음으로 · "sessionId 가 null 이면 헤더를 넣지 않는다" 삭제(`sessionId` 옵션 자체가 없어짐).
  2. `chat.test.tsx` — "응답 session_id 를 저장해 두 번째 요청에 보낸다"(localStorage `sess-abc`·둘째 요청 헤더 `sess-abc`) → 저장도 전송도 없음 · "저장된 세션이 있으면 복원 요청에 헤더" → 옛 키가 있어도 헤더 없음 · "422 invalid_session_id 면 세션 버림" 삭제(`NOTICE.sessionReset` 도 삭제) · 기본 라우터에 `/api/chat/history?limit=50` → `[]` · "복원 요청이 실패하면 `restoreFailed`" 는 기록 요청만 성공하는 경우로 좁히고, 둘 다 실패하면 `historyFailed` 인 새 테스트 추가.
  3. `e2e/chat.spec.ts` — 요청 헤더 `x-session-id` 가 `s-1` 이던 단언 3곳 → 전부 `undefined`.
  4. 관문 때문에 App 을 그리는 테스트가 `/auth/me` 200 을 받아야 한다: `routes.test.tsx`(`renderApp()` 으로 관문 통과를 기다림 — 동기 단언 11곳 `await` 화) · `card.test.tsx`(`router` 기본값 `/auth/me`·`/chat/history`, `render(<App />)` 17곳 `await renderApp()`, 요청 목록 단언 `['/api/persons']` → `['/api/auth/me', '/api/persons']`) · `push.test.ts`(`appFetch` 에 `/auth/me`, "open-briefing" 2건은 관문 통과 뒤에 서비스 워커 메시지를 보냄 — 관문 전에는 메시지를 듣지 않는다).
  5. `proxy.test.ts` — `xfwd`·`changeOrigin` 단언 추가(기존 단언 유지).
- **E2E**: `e2e/fixtures.ts` `installFakeApi` 가 기본으로 `GET /api/auth/me` 200 · `GET /api/chat/history?limit=50` → `[]` 를 더한다(표가 같은 키를 주면 표가 우선) + 204 응답은 본문 없이 fulfill. 로그인 화면 E2E 1건(`auth.spec.ts`)도 더했다.
- **프론트가 계획 밖으로 정한 것(보고)**: ① `/auth/me` 가 401 도 200 도 아닐 때 한 줄 안내 + "다시 시도" 버튼 ② 로그아웃이 401 이 아닌 오류로 실패하면 앱 틀에 남고 한 줄 안내(계획은 401 만 규정) ③ `MeOut.id` 를 `string`(users.id 가 Text uuid hex — 계약 표는 id 타입을 적지 않음, 프론트는 id 를 쓰지 않는다) ④ 아이디·비밀번호를 trim·소문자 정규화하지 않고 입력 그대로 보낸다(정규화는 서버 몫, 결정 A) ⑤ 로그인·가입 화면 입력란은 shadcn 에 `input` 컴포넌트가 없어(`components.json` 설치 목록 밖, 새 `npx shadcn` 호출을 피함) 기존 토큰 클래스를 쓴 `<input>` 이다 ⑥ 기록 개수 밖에 있는 미답변 질문은 지금까지처럼 맨 앞에 복원 ⑦ 기록 요청·복원 요청이 모두 실패하면 안내는 기록 실패 한 줄만.

## 2. 프론트가 만든 안내 문구 목록 (서버 문자열 아님)

`AuthScreen.tsx` `AUTH_NOTICE`(라벨·버튼 포함):
- 제목 `로그인` / `가입` · 라벨 `아이디` `비밀번호` `비밀번호 확인` · 버튼 `로그인` `가입하기` · 전환 `계정 만들기` `이미 계정이 있어요`
- 규칙 안내(가입 화면): `아이디는 3~20자의 영문 소문자·숫자·밑줄(_), 비밀번호는 8~128자예요.` (결정 A·B 의 값)
- 오류: `비밀번호가 서로 달라요.`(확인 칸 불일치, 요청 없음) · `invalid_username` → `아이디는 3~20자의 영문 소문자·숫자·밑줄(_)만 쓸 수 있어요.` · `invalid_password` → `비밀번호는 8~128자여야 해요.` · `username_taken` → `이미 쓰고 있는 아이디예요.` · `invalid_credentials` → `아이디 또는 비밀번호가 맞지 않아요.` · `bad_origin` → `요청이 거부됐어요. 이 서비스의 주소로 다시 접속해 주세요.` · 그 밖 → `요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.`

`App.tsx` `GATE_NOTICE`: `서버에 연결하지 못했어요.` · 버튼 `다시 시도`.
`AppShell.tsx` `ACCOUNT_NOTICE`: `로그아웃` · `로그아웃하지 못했어요. 잠시 후 다시 시도해 주세요.`
`ChatScreen.tsx` `NOTICE` 변경: 삭제 `sessionReset`, 추가 `historyFailed` = `이전 대화를 불러오지 못했어요.`

## 3. tests.md 행 (U6 절 — 명령 접두는 모두 저장소 루트에서 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> --`)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| Vitest 전체(기준선 156 → 188, 10파일) | `npm --prefix web exec -- vitest run --root web` | 188 passed · 실패 0 · skip 0 | `u6-baseline-vitest-web`(기준선) · `u6-vitest` |
| 타입 검사 | `npm --prefix web run typecheck` | exit 0 | `u6-baseline-typecheck` · `u6-typecheck` |
| 빌드 | `npm --prefix web run build` | exit 0 | `u6-build` |
| E2E 5건(기존 4 + 로그인 1), 실제 Chromium·가짜 API | `npm --prefix web run e2e` | 5 passed | `u6-e2e` |
| lint(참고, 판정 아님) | `npm --prefix web run lint` | exit 0, 오류 0·경고 19(전부 `only-export-components` 류 — 기존 화면 파일 관행대로 상수·컴포넌트를 한 파일에서 내보내는 것. 새 파일 `auth.tsx`·`AuthScreen.tsx`·`App.tsx` 도 같은 경고) | `u6-lint` |
| `auth.test.tsx` 22건 — me 401 → 로그인 화면·me 200 → 앱 틀+사이드바 한 줄·me 연결 실패 → 안내+다시 시도·로그인 성공 본문/옛 키 삭제/비밀번호 비저장·401 invalid_credentials·403/5xx 안내·알림 해시 유지·가입 속성·확인 불일치 요청 0·409·422×2·201·API 401 → 관문×2·로그아웃 endpoint·204·401·5xx·두 계정 화면 상태 | `auth.test.tsx` | 위 Vitest | `u6-vitest` |
| `api.test.ts` 신규 7건 — `X-Session-Id` 없음·`credentials`·204 `json()` 미호출·401 신호 1회·비 401/끈 401 신호 없음·로그인 401 code·logout 본문·`getChatHistory` limit | `api.test.ts` | 위 Vitest | `u6-vitest` |
| `chat.test.tsx` 신규 4건 — 기록 순서·칩 붙임·기록 밖 질문 맨 앞·기록 실패 안내 | `chat.test.tsx` | 위 Vitest | `u6-vitest` |
| 변이 16건(V6-1~16) 전부 검출 | `python3 -I <스크래치패드>/p9b-u6/mutate.py V6-n` (사본에서만) | 16/16 FAIL | `u6-mutations` |
| sw.js 가 `/api` 응답을 캐시하지 않음 | grep | `fetch`·`caches` 0건 | `u6-sw-no-cache` · `u6-sw-no-cache2` |

### 변이 표 (계획 V6-1~4 + 추가)

| 변이 | 잡는 테스트 |
|---|---|
| V6-1 401 처리 제거 | `auth.test` "대화 기록 조회가 401…"·"발화 전송이 401…", `api.test` "401 이면 전역…" |
| V6-2 `X-Session-Id` 다시 보냄 | `api.test` 2건, `chat.test` 2건 |
| V6-3 기록 순서 뒤집기 | `chat.test` "마운트 때 GET /api/chat/history…" |
| V6-4 204 에서 `json()` 호출 | `api.test` 2건, `auth.test` 로그아웃 4건 |
| V6-5 로그아웃 401 을 삼키지 않음 | `auth.test` "로그아웃이 401 을 받아도…" |
| V6-6 비밀번호 확인 검사 제거 | `auth.test` "비밀번호 확인이 다르면 요청을 한 번도…" |
| V6-7 `credentials` 제거 | `api.test` "모든 요청이 credentials…" |
| V6-8 로그아웃이 endpoint 를 안 보냄 | `api.test` "logout 은 endpoint…", `auth.test` "푸시 구독이 있으면…" |
| V6-9 프록시 `xfwd` 끔 | `proxy.test` "/api 프록시가…" |
| V6-10 기록 개수 50 → 20 | `api.test` "getChatHistory…" 외 7건 |
| V6-11 비밀번호 칸 `type="text"` | `auth.test` "입력란 속성…" |
| V6-12 기록 질문 줄에 칩 안 붙임 | `chat.test` "기록의 질문 줄에 같은 번호의…" |
| V6-13 로그인 성공 때 옛 세션 키 안 지움 | `auth.test` "성공하면 앱 틀이 열린다…" |
| V6-14 로그인 401 도 전역 신호 | `api.test` "로그인 401(invalid_credentials)…" |
| V6-15 me 비 401 실패도 로그인 화면 | `auth.test` "me 가 401 도 200 도 아니면…" |
| V6-16 signOut 이 푸시 endpoint 를 조회하지 않음 | `auth.test` "푸시 구독이 있으면…" |

## 4. registry 행 (새 행·갱신)

| 이름 | 위치 | 무엇 | 패키지·단위 |
|---|---|---|---|
| 로그인 상태·관문 | `web/src/auth.tsx`(`AuthProvider`·`useAuth` — 시작 때 `GET /auth/me` → `user`/`anonymous`/`error`/`loading`, `signedIn`·`signOut`(현재 푸시 endpoint 를 보내 로그아웃, 401 은 이미 로그아웃됨)·`retry`, `onUnauthorized` 구독으로 로그인 뒤 401 이면 `anonymous`) · `web/src/App.tsx`(`Gate`: anonymous→`AuthScreen`, error→`GATE_NOTICE` 한 줄+다시 시도, user→`SignedInApp`; 해시 라우트 추가 없음) | web/src/auth.tsx web/src/App.tsx | P9b-auth U6 · 결정 L |
| 로그인·가입 화면 | `web/src/screens/AuthScreen.tsx`(`AuthScreen`·`AUTH_NOTICE`·`authFailureNotice` — 로그인/가입 한 화면 전환, 가입은 확인 칸(다르면 요청 0), `autocomplete` username/current-password/new-password, 오류 코드별 안내) | web/src/screens/AuthScreen.tsx | P9b-auth U6 |
| 계정 API 클라이언트 | `web/src/api/client.ts` — `signup`·`login`·`getMe`·`logout(endpoint?)`(401=이미 로그아웃됨)·`getChatHistory(limit=CHAT_HISTORY_LIMIT 50)`·`onUnauthorized`; `apiFetch` 가 `credentials:'same-origin'` 명시·204 무본문·401 전역 신호(`signalUnauthorized:false` 로 끔); `SESSION_HEADER`·세션 헤더·`sessionId` 옵션 삭제 · `types.ts` `Credentials`·`MeOut`·`LogoutIn`·`ChatHistoryItemOut` | web/src/api/client.ts web/src/api/types.ts | P9b-auth U6 |
| 푸시 endpoint 조회 | `web/src/push.ts` `getCurrentPushEndpoint()`(권한·등록·네트워크 없이 현재 구독 endpoint 또는 undefined) | web/src/push.ts | P9b-auth U6 |
| 사이드바 계정 줄 | `web/src/components/AppShell.tsx` `AccountRow`·`ACCOUNT_NOTICE`(`<아이디> · 로그아웃`, 실패 한 줄) | web/src/components/AppShell.tsx | P9b-auth U6 |
| 세션 보관(갱신) | `web/src/session.ts` 는 `SESSION_STORAGE_KEY`·`clearLegacySessionId()` 만 남음(로그인·가입 성공 때 옛 키를 한 번 지움) — 기존 `getSessionId`·`setSessionId`·`clearSessionId` 삭제 | web/src/session.ts | P9b-auth U6 (P8 U5 행 갱신) |
| 채팅 화면(갱신) | `ChatScreen` 이 마운트 때 `getChatHistory()`+`getPendingQuestions()` 를 `allSettled` 로 불러 기록을 서버 순서 그대로 그리고 같은 `question_id` 의 assistant 줄에 칩을 붙임(`toHistoryMessage`), `NOTICE.sessionReset` 삭제·`historyFailed` 추가 | web/src/screens/ChatScreen.tsx | P9b-auth U6 (P8 U5 행 갱신) |
| E2E 가짜 API(갱신) | `fixtures.ts` 기본 `/auth/me` 200·`/chat/history?limit=50` 빈 목록 + 204 본문 없음, `e2e/auth.spec.ts`(로그인 → 앱 틀 → 로그아웃) | web/e2e/fixtures.ts web/e2e/auth.spec.ts | P9b-auth U6 (P8 U9a 행 갱신) |
| 프록시(갱신) | `vite.config.ts` `/api` 프록시 `xfwd: true` | web/vite.config.ts | P9b-auth U6 (사실 14) |
| 변이 러너(저장소 밖) | `<스크래치패드>/p9b-u6/mutate.py` — 사본에서만 16건 변이 | (저장소 밖) | P9b-auth U6 |
