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
