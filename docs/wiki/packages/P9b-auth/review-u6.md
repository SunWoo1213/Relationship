# P9b-auth U6 커밋 전 코드 리뷰 — 프론트 로그인·가입 관문, 로그아웃, 대화 기록, 401 처리

검토자: verifier (fable) | 일시: 2026-11-15 21:35 | 대상: dev2 HEAD `0f9223e` + 미커밋 작업 트리 중 `web/` 와 `u6-notes.md`·`evidence/*u6*`
판정: **통과**. 열린 [필수] 0 · 열린 [권고] R-1~R-6.
범위 밖(판정하지 않음): `app/`·`tests/`·`.env.example`·`03-log.md`·`tests.md` 의 미커밋 변경(백엔드 U2 진행 중). 백엔드 pytest 는 돌리지 않았다.

## 1. 본 것

- 계약: `01-plan.md` "API 계약" 표(101~113행) · U6(181~191행) · "고치는 기존 파일" 표 U6 행(98행) · 결정 A·B·I·L·P · 판정 표 #8 · 사실 4·8·12·14 · 리스크 "쿠키 ↔ 서비스 워커"(304행). CLAUDE.md 원칙5(개정)·원칙7.
- 변경: `git diff -- web` 17파일 전부 · 새 파일 `web/src/auth.tsx`(86줄)·`web/src/screens/AuthScreen.tsx`(151줄)·`web/src/__tests__/auth.test.tsx`(382줄)·`web/e2e/auth.spec.ts`(40줄) 전부. `ChatScreen.tsx` 는 diff 가 아니라 현재 본문 전체.
- 주변: `web/src/components/PersonsProvider.tsx`(언마운트 처리) · `web/src/routes.ts` · `web/public/sw.js` 리스너 목록 · `web/src/push.ts` 등록·조회 경로.
- 구현자 메모·증거: `u6-notes.md` 1~4절 · `evidence/20261115-2124…2126-u6-*.txt`(vitest 188·e2e 5·변이 16건·sw grep).
- 백엔드 모양 대조(읽기만, 판정 아님): `app/api/schemas.py` `MeOut{id: str, username: str}`·`LogoutIn{endpoint: str | None}` — 프론트 `types.ts` 와 맞는다.

## 2. 직접 실행한 명령과 결과

| 명령(접두 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> --`) | 결과 | evidence |
|---|---|---|
| `npm --prefix web run typecheck` | exit 0 | `20261115-2129-verifier-u6-typecheck.txt` |
| `npm --prefix web exec -- vitest run --root web` | 10파일 · 188 passed · 실패 0 | `20261115-2129-verifier-u6-vitest.txt` |
| `npm --prefix web run build` | exit 0 | `20261115-2129-verifier-u6-build.txt` |
| `npm --prefix web run e2e` | 5 passed | `20261115-2129-verifier-u6-e2e.txt` |
| `npm --prefix web run lint`(참고) | exit 0 | `20261115-2129-verifier-u6-lint.txt` |
| 변이 A(사본): `Gate` 가 `loading` 에서 앱 틀을 그림(me 200 전에 셸) | **검출** — 2 failed(`auth.test` "me 401 이면 … 앱 틀은 그려지지 않는다", `card.test` 요청 목록 단언) | `20261115-2131-verifier-u6-mut-gate-shell-before-me.txt` |
| 변이 B(사본): `ChatScreen` 메시지를 모듈 변수에 남겨 로그아웃 뒤에도 살아 있게 함 | **검출** — 1 failed(`auth.test` "로그아웃 뒤 다시 로그인하면 이전 계정의 화면 상태가 남지 않는다") | `20261115-2131-verifier-u6-mut-chat-state-survives-logout.txt` |
| 탐침(사본, 새 테스트 2건): P1 계정 A 의 늦은 200 응답(기록·인물)이 B 화면에 그려지는가 / P2 A 의 늦은 401 이 B 를 밀어내는가 | P1 **통과**(그려지지 않음) · P2 **실패**(B 가 로그인 화면으로 밀려남 — R-1) | `20261115-2131-verifier-u6-probe-late-response.txt` |

변이·탐침은 스크래치패드 사본 `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/vu6/web/` 에서만 했다(저장소 무수정 — 실행 뒤 `git status --short -- web` 21줄 그대로). 두 변이 모두 구현자의 V6-1~16 에 없는 것이다.

## 3. 판정 근거 (줄 단위)

- **401 전역 신호**: `client.ts:98` `response.status === 401 && options.signalUnauthorized !== false` 일 때만 리스너 호출. `signup`·`login`·`getMe`·`logout` 넷이 `signalUnauthorized: false`(188·192·197·207행) → 로그인 401(`invalid_credentials`)은 신호 없이 `AuthScreen` 이 안내, 로그아웃 401 은 `logout()` 이 삼킨다(209행). `api.test` 3건이 신호 유무를 단언.
- **관문 상태 전이**: `auth.tsx:36` 초기 `loading` → `getMe` 200 `user` / 401 `anonymous` / 그 밖 `error`(48행). `latest` 카운터로 늦은 `/auth/me` 응답이 `signedIn`·`signOut`·401 신호 뒤 상태를 덮지 않는다(41·61·69·76행). `App.tsx:34` `loading` 은 빈 틀 — 앱 틀·API 호출 0(변이 A 로 확인).
- **로그아웃**: `auth.tsx:74-77` `getCurrentPushEndpoint()` → `logout(endpoint)` → `anonymous`. 서버가 401 이 아닌 실패면 던져서 `AppShell.tsx` `AccountRow` 가 한 줄 안내하고 앱 틀에 남는다(상태를 먼저 바꾸지 않음 — 쿠키가 살아 있는데 로그인 화면이 뜨는 일이 없다). `push.ts:55-65` 는 권한 창·등록·네트워크 없이 현재 등록의 구독만 읽고 예외는 `undefined`.
- **204 무본문·credentials**: `client.ts:104` 204 는 `json()` 미호출, `:86` `credentials: 'same-origin'`. `api.test` 가 `json` 스파이 미호출·GET/POST 양쪽 `credentials` 를 단언.
- **비밀번호**: `AuthScreen` 의 `useState` 와 요청 본문에만 있다. `ApiError` 는 `status`·`code` 만 담는다(`client.ts:38-43`). `web/src` 에 `console.`·`localStorage.setItem`·`sessionStorage` 0건(grep). 로그인 성공·모드 전환 때 화면이 내려가거나 칸을 비운다(`AuthScreen.tsx:63-64`). `auth.test:142-158` 이 콘솔 5종 미호출·localStorage 에 비밀번호 없음을 단언. 스냅샷 테스트 없음.
- **입력 속성**: `type="password"`, `autoComplete` `username`/`current-password`/`new-password`(가입 두 칸) — `AuthScreen.tsx:99,114,127`, 테스트 단언 있음.
- **XSS**: `web/src`·`web/index.html`·`web/public` 에 `dangerouslySetInnerHTML`·`innerHTML` 0건. 아이디·기록 문장은 JSX 텍스트로만 그린다.
- **두 계정 화면 상태(가장 중요)**: `App.tsx:45-46` 관문이 `anonymous` 에서 `SignedInApp` 을 통째로 내린다 → `ChatScreen`(메시지 `useState`)·`PersonsProvider`·`BriefingScreen`·`PersonCardScreen` 상태가 전부 사라진다. `web/src` 의 모듈 수준 가변 상태는 `client.ts:60` 리스너 집합 하나뿐(데이터 아님, grep). 프론트 캐시·localStorage 데이터 0, `sw.js` 는 `install`·`activate`·`push`·`notificationclick` 뿐이고 `fetch`·`cache` 0건. 늦은 응답: `PersonsProvider.tsx:54` 언마운트 때 `latest++`, `ChatScreen.tsx:151` `alive` 로 무시 — 탐침 P1 로 실측(A 의 늦은 기록·인물이 B 화면에 없음). 변이 B 가 이 계약을 지키는 테스트가 실제로 실패함을 보였다.
- **대화 기록**: 서버 순서 그대로 `map`(재정렬 없음, `ChatScreen.tsx:155`), 같은 `question_id` 의 assistant 줄에 칩 1회(`toHistoryMessage`), 기록 밖 미답변 질문은 맨 앞. `chat.test` 4건이 순서·칩 위치·질문 문장 1회·실패 안내를 단언.
- **바뀐 기존 단언**: 전부 세션 헤더·세션 저장·관문 통과(`/auth/me`) 때문이다. `card.test` 요청 목록은 `['/api/auth/me', '/api/persons']` 로 **정확 일치를 유지**, `routes.test`·`push.test` 는 `await renderApp()`·관문 통과 대기만 더했고 단언 본문은 그대로. `chat.test` "복원 요청 실패" 는 기록만 성공하는 경우로 좁히고 둘 다 실패하는 테스트를 새로 더했다 — 느슨해진 단언 없음. 삭제 3건(`sessionId: null`, `invalid_session_id`, 세션 복원 헤더)은 없어진 기능의 단언이다. 계획이 열거하지 않은 `routes.test`·`card.test`·`push.test` 변경은 `App` 을 그리는 테스트가 관문 뒤에 놓인 필연적 결과라 타당하다.
- **범위**: `web/package.json`·`package-lock.json`·`components.json` diff 0(새 의존성 0). `routes.ts` 는 주석만 변경 — 해시 라우트 3개 그대로. 채팅방 목록 없음(`auth.test:107` 사이드바 링크 3개 정확 일치). `/push-dev/` 링크 0(grep). `web/` 밖 U6 산출물은 `u6-notes.md` 와 evidence 뿐.
- **안내 문구(원칙7)**: `AUTH_NOTICE`·`GATE_NOTICE`·`ACCOUNT_NOTICE`·`NOTICE.historyFailed` 모두 폼 라벨·오류 안내다. 감정·조언 문구 없음, 서버 문장 가공 없음(서버 오류는 `detail.code` 만 읽어 고정 문구로 바꾼다).

## 4. 계획에 없던 판단 ①~⑦

| # | 판단 | 판정 |
|---|---|---|
| ① | me 가 401·200 이 아니면 안내 + 다시 시도 | 타당. 서버 장애를 "로그아웃됨" 으로 보이면 사실과 다르다 |
| ② | 로그아웃이 401 밖 오류면 앱 틀에 남고 안내 | 타당. 쿠키가 살아 있는데 관문으로 보내지 않는다 |
| ③ | `MeOut.id: string` | 타당. 백엔드 `MeOut.id: str` 과 일치 |
| ④ | 아이디를 정규화하지 않고 그대로 전송 | 타당(결정 A — 정규화는 서버). 화면은 서버가 준 `username` 을 쓴다 |
| ⑤ | shadcn `input` 없이 `<input>` | 타당. 새 의존성·생성 파일 0 |
| ⑥ | 기록 개수 밖 미답변 질문은 맨 앞 | 타당. 기존 동작 유지 |
| ⑦ | 둘 다 실패하면 기록 실패 한 줄만 | 타당. 안내 한 줄 원칙 |

사용자만 정할 수 있는 것(상수·범위)은 섞이지 않았다. 숫자는 결정 A·B·I 의 값 그대로다.

## 5. 소견

[필수] 없음.

- **[권고] R-1 늦은 401 이 새 로그인을 밀어낸다**: `client.ts:98-100` 의 신호에 "어느 로그인 때 보낸 요청인가" 구분이 없다. 계정 A 때 보낸 요청의 401 이 B 로그인 뒤 도착하면 B 가 로그인 화면으로 돌아간다(탐침 P2 실측). 데이터 노출은 없고 다시 로그인하면 된다. 실제로는 쿠키 만료 순간 여러 요청이 동시에 401 을 받고 사용자가 곧바로 다시 로그인하는 좁은 경우뿐이라 시연 경로(로그아웃 → 로그인)에서는 일어나지 않는다. 고친다면 요청 시작 시점의 로그인 세대 번호를 신호와 비교.
- **[권고] R-2 여러 탭**: 탭 1 이 A 로 열린 채 탭 2 에서 B 로 바꾸면 탭 1 은 A 의 메시지·아이디를 메모리에 그대로 보여 주면서 요청은 B 쿠키로 나간다(탭 1 에서 보낸 발화는 B 계정에 저장). 쿠키 세션의 일반적 한계이고 계획 범위 밖이다. **시연은 탭 하나로 하거나 계정 전환 뒤 새로고침** — U8 절차·SERVER-CHECKLIST §5 에 한 줄 권한다.
- **[권고] R-3 로그아웃 뒤 해시 유지**: A 가 `#/persons/12` 에서 로그아웃하고 B 가 로그인하면 B 의 첫 화면이 "인물을 찾을 수 없어요." 다(서버 404 — 노출 아님). 결정 L 의 "해시가 관문을 지나 살아 있다" 는 알림 클릭을 위한 것이라, 로그아웃 때만 `#/chat` 으로 돌리는 것을 고려할 만하다. 시연에서는 채팅 화면에서 로그아웃하면 된다.
- **[권고] R-4 규칙 안내 문구**: "아이디는 … 영문 소문자" 라고 적지만 서버는 대문자를 소문자로 정규화해 받는다(결정 A). 틀린 말은 아니나 `Minji` 로 가입하면 `minji` 로 표시된다 — U7 로컬 브라우저 점검 때 한 번 확인.
- **[권고] R-5 판정 명령**: 계획 판정 표 #8 의 `npm --prefix web exec -- vitest run` 은 저장소 루트에서 E2E 파일을 줍는다(구현자 기준선 증거 `u6-baseline-vitest`). tests.md·04-review 에는 `--root web` 을 붙인 명령으로 적는다.
- **[권고] R-6 백엔드 의존 가정**: 칩 붙이기는 `/chat/history` 의 assistant 줄이 그 질문의 `question_id` 를 담는다는 전제다(계약 표·결정 R). U4 리뷰에서 "질문을 낸 assistant 행에 `question_id` 가 실린다" 를 확인해야 한다 — 실리지 않으면 프론트는 깨지지 않고 질문이 맨 앞에 따로 복원될 뿐이다(⑥ 경로).

## 6. 메인 세션이 옮길 것

`u6-notes.md` 1~4절을 `03-log.md`·`tests.md`·`registry.md` 로 옮길 때 이 리뷰의 증거 8개(§2 표)를 tests.md 에 함께 적는다.

## 7. CI 수정 리뷰 (2026-11-15, `web/src/__tests__/push.test.ts` 미커밋 diff)

검토자: verifier (fable)
판정: **통과** (이 diff 한정). 열린 [필수] 0 · 새 소견 C-1(별도 수정 필요) · C-2~C-4 [권고].
범위: `push.test.ts` diff(+8줄) · `u6-notes.md` 5절 · `evidence/*u6-cifix*`. HEAD `1cf67cd` + 미커밋. 백엔드(`tests/`·`scripts/`) 변경은 보지 않았고 pytest 는 돌리지 않았다. 범위 축소 지시(사용자, 조율자 경유)에 따라 **Mac 에서만** 확인했다 — Windows 러너 재현·분석은 하지 않았다.

### 7.1 증거 (모두 `evidence/`, 변이는 저장소 밖 사본 `<스크래치패드>/vu6fix/web` 에서만)

| 파일 | 내용 | 결과 |
|---|---|---|
| `20261115-2158-verifier-u6-cifix-repro.txt` | 고치기 전(HEAD)·고친 테스트 × 변이 | 고치기 전+변이 없음 21 passed / 고치기 전+리스너 150ms 지연 **5 failed**(`Unable to find … push-banner` 3, 해시 단언 2 — CI 와 같은 모양, 1012~1040ms) / 고친 것+같은 지연 21 passed / 고친 것+리스너를 아예 안 붙임 **5 failed**(`expected false to be true`) / 고친 것+`setBanner` 삭제 **3 failed** |
| `20261115-2159-verifier-u6-cifix-probe.txt` | 탐침: App 을 그려 관문 통과를 기다린 **직후** 리스너 유무(150라운드 × 12회 × 2) | 변이 없이 자연 발생 — 3600라운드 중 9라운드에서 리스너가 아직 없었다. 파일 `afterEach` 는 App 이 마운트된 채로 `unstubAllGlobals` 를 먼저 돈다(`App mounted=true`, 직후 `matchMedia=undefined`) |
| `20261115-2200-verifier-u6-cifix-vitest.txt` | 실제 저장소 `npm --prefix web exec -- vitest run --root web` 8회 | 7회 188 passed, **1회 실패**(`routes.test.tsx` "지금 화면 항목에 aria-current", `window.matchMedia is not a function`) — push.test 는 8회 모두 통과 |
| `20261115-2200-verifier-u6-cifix-typecheck.txt` · `…-lint.txt` | `tsc -b` · oxlint | exit 0 (lint 경고는 기존 것) |

### 7.2 판정 근거

1. **원인 진단은 맞다.** 탐침이 지연 변이 없이도 "화면은 보이는데 `WorkerMessages` 의 effect 는 아직 안 돈" 순간을 잡았다(약 400라운드에 1번, Mac). 관문 뒤 마운트는 `/auth/me` 응답이 일으키는 `act` 밖 갱신이라 DOM 반영과 passive effect 사이에 틈이 있고, 고치기 전 테스트는 그 틈에 `world.post` 를 불렀다. 구현자의 변이 설명(150ms 지연 → 5건 실패 / 고친 뒤 통과)도 직접 실행으로 같은 결과였다.
2. **단언이 느슨해지지 않았다.** diff 는 `hasListener()` 1개와 `world.post` 앞 `waitFor` 5줄뿐 — 기존 단언·타임아웃 변경 없음, sleep 없음. 리스너를 붙이지 않는 제품 변이는 고친 테스트에서 5건 모두 실패하고(대기가 통과 조건이 아니라 실패 조건으로 동작), 배너를 띄우지 않는 변이도 3건 실패한다.
3. **구현자 증거 2개는 증거가 아니다**(판정에 쓰지 않음): `20261115-2153-u6-cifix-mutation.txt` 는 `echo` 문법 오류(exit 2)라 변이 출력이 없고, `20261115-2154-u6-cifix-repeat.txt` 는 6회 모두 `Tests  no tests`(경로 필터 불일치)다. `u6-notes.md` 5절의 "재현·변이" 줄은 위 verifier 증거로 대체해 적어야 한다.

### 7.3 "제품 버그 아님" 검증 — 알림을 눌렀을 때 (`web/public/sw.js` 54~73행 · `AppShell.tsx` 120~138행 · `App.tsx` 32~47행)

| 경우 | 경로 | 결과 |
|---|---|---|
| (a) 앱 창 열림 + 로그인됨 | `matchAll` → 경로 `/` 창 `focus()` → `postMessage(open-briefing)` → `WorkerMessages` 리스너가 해시 변경 | 도착한다 |
| (b) 앱 창 없음 | `openWindow("/#/briefings?schedule_id=N")` — 메시지에 기대지 않는다. 로그아웃 상태면 로그인 뒤에도 해시가 남아 브리핑이 열린다(01-plan 182행 ②, `AuthScreen` 은 해시를 건드리지 않음) | 도착한다 |
| (c) 앱 창 열림 + 관문 `loading`(새로고침·첫 로드 직후 `/auth/me` 응답 전, `retry` 직후 포함) | 창이 있으므로 `postMessage` 로 간다. 이때 `AppShell` 이 없어 리스너가 없다 → 메시지는 버려지고 `openWindow` 도 불리지 않는다 | **유실된다** — 창만 앞으로 오고 원래 화면에 머문다. 알림은 `notification.close()` 로 이미 닫혔다 |
| (d) 앱 창 열림 + 로그인 화면(`anonymous`) | (c) 와 같다. 로그인해도 해시가 안 바뀌어 채팅으로 간다 | **유실된다** — (b) 와 동작이 어긋난다(창이 없으면 로그인 뒤 브리핑, 창이 있으면 채팅) |

- "제품 버그 아님" 은 **CI 실패 원인에 대해서는 맞다**(테스트 쪽 경합). 그러나 "유실 경로 없음" 은 아니다 — (c)(d) 는 U6 가 관문을 넣으면서 생긴 경로다(그 전에는 `AppShell` 이 첫 렌더에 마운트됐다).
- **(c) 는 [권고]** 로 본다. 근거: 창이 열린 지 `/auth/me` 왕복(수십~수백 ms) 안에 알림을 눌러야 하고, 잃는 것은 화면 이동 한 번뿐이며(사이드바 "브리핑" 한 번으로 복구, 데이터 손실 없음), 계획의 수용 기준·판정 표에 이 순간에 대한 요구가 없다. 같은 창에 온 `briefing`(배너)도 이 순간엔 유실되지만 OS 알림은 그대로 뜬다.
- **(d) 도 [권고]** 지만 (c) 보다 현실적이다 — 로그아웃은 구독을 지우므로(`signOut` 이 endpoint 를 보냄) 평소엔 푸시가 오지 않지만, **세션 만료**로 로그인 화면이 된 창에는 구독이 살아 있어 알림이 온다. 구현자가 "의도된 동작" 으로 적었으나 계획 근거는 없다(304행은 "로그아웃 상태면 관문이 먼저 뜬다" 까지만 말한다).

### 7.4 소견

- **C-1 (별도 수정 필요 — 이 diff 의 결함은 아니다)**: 같은 계열의 간헐 실패가 **Mac 에서 재현된다** — 전체 실행 8회 중 1회(`routes.test.tsx`, `window.matchMedia is not a function`, sonner `Toaster` 의 passive effect). 원인: `afterEach` 가 스택 순서라 파일의 `vi.unstubAllGlobals()` 가 `test-setup.ts` 의 `cleanup()` 보다 먼저 돌고, 밀려 있던 effect 가 스텁이 걷힌 뒤 실행된다. `<App />` 을 그리는 4개 파일(`routes`·`push`·`auth`·`card`) 모두 해당. 최소 수정안: 그 파일들의 `afterEach` 맨 앞에서 `cleanup()` 을 먼저 부른다 — 탐침에서 수정 없이 12회 중 4회 실패, 수정하면 12회 중 0회(`…-probe.txt`). 고치지 않으면 CI 가 이 diff 와 무관하게 다시 빨개질 수 있다.
- **C-2 [권고]** (c)(d): `open-briefing` 리스너를 관문 위(`App`/`AuthProvider` 높이)로 올려 로그인 상태와 무관하게 해시만 바꾸면 둘 다 닫힌다(해시는 관문을 지나도 남는다). 제품 코드 변경이라 별도 단위·테스트가 필요하다.
- **C-3 [권고]** 같은 약점이 남은 테스트: 관문 통과 직후 서비스 워커 메시지를 보내는 곳은 `push.test.ts` 의 5곳뿐이고 모두 고쳐졌다. 다른 파일은 관문 뒤에 `userEvent`·`waitFor` 단언만 써서 "보낸 이벤트 유실" 형태는 없다 — 남은 것은 C-1 의 정리 순서 문제다.
- **C-4 [권고]** `u6-notes.md` 5절: "재현·변이" 줄의 증거 경로와 "제품 버그 아님" 줄을 7.3 표에 맞게 고친다((c) 유실 경로 누락, (d) "의도된 동작" 은 근거 없음).

## 8. 추가 수정 리뷰 (C-1·C-2) (2026-11-15, `web/` 미커밋 diff)

검토자: verifier (fable)
판정: **통과**. 열린 [필수] 0 · [권고] D-1~D-4.
범위: `web/vite.config.ts`(+3줄) · `web/src/App.tsx`(+2/-1) · `web/src/components/AppShell.tsx`(+20/-2) · `web/src/__tests__/auth.test.tsx`(+3건) · `u6-notes.md` 5절 · `evidence/*u6-fix2*`. HEAD `1cf67cd` + 미커밋. `tests/`(백엔드)는 보지 않았고 pytest 는 돌리지 않았다. **Mac 로컬로만** 판정했다(Windows CI 미확인 — 사용자 지시). 변이·탐침은 저장소 밖 사본(`<스크래치패드>/vu6fix2/web`)에서만 했고 저장소 파일은 고치지 않았다.

### 8.1 증거 (모두 `evidence/`)

| 파일 | 내용 | 결과 |
|---|---|---|
| `20261115-2355-verifier-u6-fix2-vitest-x30.txt` | 실제 저장소 전체 Vitest 30회 연속 | **실패 0 / 30** (매회 10 files · 191 passed) |
| `20261115-2357-verifier-u6-fix2-noseq-x30.txt` | 사본에서 `sequence` 줄만 뺀 채 30회 | **실패 2 / 30** — `window.matchMedia is not a function`(`routes.test` 2건 · `auth.test` 1건). 구현자 x40(5/40)과 같은 모양 |
| `20261115-2354-verifier-u6-fix2-probe-noseq.txt` | 탐침 P2: 파일 `afterEach` 가 돌 때 화면이 이미 내려갔는가(결정적, 1회로 판별) | 줄을 빼면 `body-empty=false` 로 **실패**, 줄이 있으면 `body-empty=true` 로 통과(`…-probe.txt`) |
| `20261115-2354-verifier-u6-fix2-probe.txt` | 탐침 P1~P10(18건, 아래 8.3) | 18 passed |
| `20261115-2359-verifier-u6-fix2-mutations-rerun.txt` | 제품 변이 6건 × 저장소의 `auth.test`+`push.test` | 기준 46 passed / M1 **3 failed** / M2 **1 failed** / M3 **2 failed** / M5 **3 failed** / M4·M6 **생존**(46 passed) |
| `20261115-2354-verifier-u6-fix2-mutations.txt` | 같은 러너 1차 | 변이 결과는 위와 같다. 다만 기준 실행이 `exit=-6`(출력 없이 프로세스 중단, 1회) — 재실행에서 재현되지 않아 판정에 쓰지 않는다 |
| `20261115-2359-verifier-u6-fix2-typecheck.txt` · `…-lint.txt` · `…-e2e.txt` | `tsc -b` · oxlint · Playwright(빌드 포함) | exit 0 · exit 0(경고는 기존 종류) · 5 passed |

### 8.2 C-1 — `sequence: { hooks: 'list' }`

1. **원인을 닫는다.** 탐침 P2 가 순서를 직접 쟀다 — 줄이 있으면 파일의 `afterEach` 시점에 `document.body` 가 비어 있고(`cleanup()` 이 먼저), 줄을 빼면 App 이 아직 붙어 있다. 간헐 실패도 줄 유무로 갈린다(0/30 대 2/30, 구현자 0/40 대 5/40).
2. **다른 훅의 순서 의존을 깨지 않는다.** 훅 전수: `test-setup.ts`(afterEach 1) · `push`(beforeEach 2 — 파일·`describe` 중첩, afterEach 1) · `routes`·`chat`·`auth`·`briefing`·`card`(각 beforeEach 1·afterEach 1) · `api`(afterEach 1). `beforeAll`/`afterAll` 은 없다. 한 범위에 같은 종류 훅이 둘 이상인 곳이 없어 바뀌는 것은 "setup `cleanup()` ↔ 파일 afterEach" 한 쌍뿐이다. 파일 afterEach 가 하는 일(`unstubAllGlobals`·`serviceWorker` 삭제·`useRealTimers`·`restoreAllMocks`·해시 복원)은 모두 언마운트 **뒤에** 해도 되는 것이고, 오히려 그 순서가 의도다. `chat.test` 는 가짜 타이머가 켜진 채 `cleanup()` 이 돌게 되지만 30회 모두 통과했다. `beforeEach` 순서(바깥→안)는 `list` 에서도 같다.

### 8.3 C-2 — `OpenBriefingListener` (`AppShell.tsx` 125~137행 · `App.tsx` 52행)

| 본 것 | 근거 | 결과 |
|---|---|---|
| (c) loading · (d) 로그인 화면에서 해시 변경, 로그인 뒤 그 브리핑 | 저장소 테스트 (c)(d) + 변이 M1·M2·M5 가 실패로 잡음 | 맞다 |
| 로그인된 상태의 기존 동작 | 탐침 P6: 리스너 2개, `open-briefing` 1회에 `hashchange` **1회**, 배너 1개→사라짐. `push.test` 5건 통과 | 유지. 해시 대입은 한 곳(관문 위)뿐, `WorkerMessages` 는 `setBanner(null)` 만 |
| 정보 노출 — loading·로그인 화면 | 컴포넌트가 `null` 을 반환, 메시지는 `readWorkerMessage` 가 `{type, scheduleId}` 만 남긴다. 탐침 P3(loading: `body.textContent === ''`)·P4(로그인 화면: 메시지에 `title`·`body` 를 실어 보내도 `innerHTML` 불변) | 경로 없음. `sw.js` 도 창에는 `schedule_id` 만 보낸다(50·68행) |
| 다른 계정으로 로그인 | 탐침 P5: 해시 `schedule_id=12` 인 채 `other_02` 로 로그인, 단건이 404 → `schedule-missing` 안내("그 일정의 브리핑이 아직 없어요.")만, `briefing-list` 없음. 로그아웃·401 때 `SignedInApp` 이 언마운트되어 이전 계정 상태는 남지 않는다 | 이전 계정 데이터 안 보임. 남의 일정에 404 를 주는 것은 백엔드(U3b) 몫 — 여기서 확인하지 않았다 |
| 메시지 출처 | `navigator.serviceWorker.addEventListener('message')` 만. 탐침 P8: `window.postMessage`·`window` 의 `MessageEvent` 로는 해시 불변 | 맞다 |
| `schedule_id` 검증·주입 | `readWorkerMessage` 111행(양의 정수만) + `briefingHref` 가 숫자만 끼움. 탐침 P7 8종(문자열 `'12'`, `'12&x=<script>…#/persons/1'`, 1.5, -3, 0, 객체, NaN, Infinity) 모두 해시가 정확히 `#/briefings` | 주입 없음 |
| 새 라우트·화면, 원칙7 | `routes.ts` 무변경(diff 없음). 새 문구 0, 서버 문장을 그리지 않음 | 0 |
| 정리 | 탐침 P10: 언마운트 뒤 리스너 0. `main.tsx` 의 StrictMode 이중 실행에도 cleanup 이 짝을 맞춘다 | 맞다 |

### 8.4 새 테스트 3건

값을 단언한다 — M1(리스너를 앱 틀 안으로 되돌림) 3건 실패, M2(loading 에서는 리스너 없음) (c) 만 실패, M3(type 을 가리지 않음) 3번째 테스트가 `expected '#/briefings?schedule_id=9' to be '#/chat'` 로 실패, M5(일정 번호 버림) (c)(d) 실패. 다만 3번째 테스트의 "배너 없음" 두 줄은 고치기 전 코드에서도 참이라 이 변경을 가르는 것은 해시 단언 한 줄이다.

### 8.5 `u6-notes.md` 5절

5.1·5.2 의 서술(한 곳 수정, 리스너 위치, 테스트 3건, 191 passed, 40회 0 / 줄 제거 5/40, typecheck·build·E2E 5 passed)은 증거 파일과 맞다. "의도된 동작" 철회와 무효 증거 3개(`…-cifix-mutation`·`…-cifix-repeat`·`…-2203-u6-fix2-vitest-x15`) 표시도 돼 있다. 어긋난 곳은 D-4.

### 8.6 소견 (모두 [권고] — 커밋을 막지 않는다)

- **D-1** 숫자 검증에 테스트가 없다: M4(`readWorkerMessage` 의 양의 정수 검사 제거)가 저장소 테스트 46건을 모두 통과한다. 이 검사는 이번 diff 이전 코드지만, 리스너가 관문 위로 올라와 로그인 전에도 해시에 닿게 됐으므로 문자열·소수·음수 `schedule_id` → `#/briefings` 단언 1건을 더하는 편이 낫다(탐침 P7 이 그대로 쓸 수 있는 모양).
- **D-2** 주석이 코드와 어긋난다: `AppShell.tsx` 115~119행의 `WorkerMessages` 설명이 `OpenBriefingListener` 설명 위에 떠 있고(문서 주석 두 개가 연달아 한 함수 앞), "`open-briefing` 은 배너 없이 바로 그 주소로 간다" 는 이제 그 컴포넌트의 일이 아니다. `push.test.ts` 411·429행 주석 "관문을 통과한 뒤에야 서비스 워커 메시지를 듣는다" 도 사실이 아니게 됐다.
- **D-3** M6(앱 틀 안에서도 해시를 다시 대입)은 생존한다 — 같은 값 대입이라 동작 차이가 없어 결함은 아니다. 기록만 한다. 아주 큰 정수(예: `1e21`)는 `Number.isInteger` 를 통과해 해시에 지수 표기로 남지만 `parseScheduleId` 가 거부해 일정 없는 브리핑으로 읽힌다(탐침 P7b) — 서버가 그런 값을 보내지 않으므로 조치 불필요.
- **D-4** `u6-notes.md`: ① 87행 `…-cifix-mutation.txt` 는 "echo 한 줄 요약" 이 아니라 **문법 오류(exit 2)로 출력이 없는 파일**이다. ② 5.2 "변이" 줄(46건 중 3 failed)은 증거 파일이 없다 — `20261115-2359-verifier-u6-fix2-mutations-rerun.txt` 의 M1 로 대체해 적는다.
- 확인하지 못한 것: Windows 러너(범위 밖), 실제 브라우저의 서비스 워커 `postMessage` 경로(E2E 는 `serviceWorkers: 'block'` 이라 단위 테스트의 가짜 컨테이너로만 봤다), 백엔드의 남의 일정 404(U3b).
