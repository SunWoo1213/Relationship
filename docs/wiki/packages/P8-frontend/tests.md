# P8-frontend 테스트 기록 — 무엇을 어떻게 시험했나

> 사용자 지시(2026-10-15): "테스트마다 어떤 테스트를 했는지 기록해주세요." 테스트 1건 = 표 1줄.
> 열: `파일::테스트 이름` | 무엇을 확인하나 | 입력 → 기대 | 결과(마지막 실행 결과 + 그 테스트를 실패시킨 변이 ID).
> 작성: U9a(frontend-agent, 2026-10-15) — 테스트 코드를 읽고 썼다(이름만 보고 짐작하지 않았다). `it.each` 는 경우마다 1줄.
> 자동 테스트는 실제 네트워크·실제 LLM·실제 푸시 서비스를 쓰지 않는다(결정 J). API 는 가짜 응답, 시간은 고정.

## 총계와 세는 법

| 구분 | 파일 | 건수 | 세는 명령 |
|------|------|------|----------|
| 프론트 단위(Vitest) | 9 | **135** | `cd web && npm test -- --run --reporter=verbose` 출력에서 `grep -c " ✓ src/__tests__" <출력 파일>` → 135 (요약 줄 `Test Files  9 passed (9)` · `Tests  135 passed (135)`). 목록만: `cd web && npx vitest list` |
| E2E(Playwright) | 3 | **4** | `cd web && npx playwright test --list` → `Total: 4 tests in 3 files` |
| 백엔드(pytest) | — | — | 아래 "백엔드 (U9b 가 채움)" |

- Vitest 파일별 건수: api 6 · proxy 6 · routes 14 · chat 22 · card 29 · briefing 19 · sw 16 · push 21 · network 2 = 135 (U8 시점 130 → sw +2 · push +1 · network +2).
- 증거: Vitest 전체 verbose `evidence/20261015-1410-u9-vitest-verbose.txt` · 파일별 판정 `evidence/20261015-1410-u9-front-rows.txt` · 전체 판정(`npm ci` → typecheck → test → build → e2e) `evidence/20261015-1409-u9-final-judge.txt` · E2E 목록 `evidence/20261015-1411-u9-e2e-list.txt`.
- 이 표의 첫 열은 verbose 출력의 `파일 > 묶음 > 테스트 이름` 에서 파일과 맨 끝 테스트 이름이다. 같은 이름을 표와 출력에서 기계로 대조한 결과는 03-log U9 에 적는다.

### 결과 열 읽는 법

`통과` 는 마지막 실행(2026-10-15 14:09~14:10, 위 증거)의 결과다. 뒤의 `U5-M3` 같은 표기는 **그 변이를 넣었을 때 이 테스트가 실패해 변이를 검출했다**는 뜻이고 `—` 는 근거가 되는 변이 증거가 없다는 뜻이다(없다고 약하다는 말은 아니다). 변이 ID 는 단위 접두사 + 그 단위 증거 안의 번호다.

| 접두사 | 변이를 돌린 사람 | 증거 파일(`evidence/`) |
|--------|----------------|----------------------|
| `U4-M*`·`U4-R*` | frontend-agent | `20261012-2031-u4-mutation-full-1.txt` · `-full-2.txt` · `20261012-2055-u4-mutation-rework2.txt` |
| `U4-V*` | verifier | `20261012-2040-verifier-u4-mutation-1.txt` · `-2.txt` · `-3.txt` · `20261012-2336-verifier-u4-recheck-mutation.txt` |
| `U5-M*` | frontend-agent | `20261013-1325-u5-mutation.txt` |
| `U5-V*` | verifier | `20261013-1354-verifier-u5-mutation.txt` |
| `U6-M*` | frontend-agent | `20261013-1627-u6-mutation.txt` (결과 요약뿐이라 테스트 이름이 남은 것만 표에 옮김) |
| `U6-V*` | verifier | `20261013-1847-verifier-u6-mutation.txt` |
| `U7-M*` | frontend-agent | `20261013-1945-u7-mutation.txt` |
| `U7-V*` | verifier | `20261014-1946-verifier-u7-mutation.txt` |
| `U8-M*` | frontend-agent | `20261014-2008-u8-mutation.txt` · `20261014-2017-u8-mutation-rework.txt` |
| `U8-V*` | verifier | `20261014-2024-verifier-u8-mutation.txt` |
| `U9-X*` | frontend-agent | `20261015-1404-u9-mutation.txt` (스크립트 `20261015-1414-u9-mutation-script.txt`) |

표의 변이 ID 는 증거 파일의 "× 실패한 테스트 이름" 줄을 **현재 테스트 이름**과 맞춰 뽑았다. 이후 이름이 바뀐 테스트(예: `proxy.test.ts` 의 `/api 프록시가 …` 는 U5 에서 단언을 순수 함수로 바꾸며 이름이 달라짐)는 현재 이름으로 확인되지 않아 `—` 로 두었다. 변이 시험에서 DOM 덤프가 없어진 단위(U6 implementer)는 테스트 이름이 증거에 남은 변이만 적었다.

### 이번 단위(U9a)에서 돌린 변이 U9-X1~X16

| ID | 무엇을 망가뜨렸나 (저장소 밖 사본 `web/` 에서 한 곳만 치환) | 검출한 테스트 |
|----|------------------------------------------------------|--------------|
| X1 | `sw.js` notificationclick 이 앱 창을 고르지 않고 첫 창을 쓴다 (R-U8-3 되돌리기) | `sw.test.ts` 새 2건 |
| X2 | `sw.js` 가 앱 창을 하나도 못 찾는다(항상 새 창) | `sw.test.ts` 기존 "열린 창이 있으면 …" + 새 "앱이 아닌 같은 출처 창이 …" |
| X3 | `AppShell` 이 `open-briefing` 의 `schedule_id` 가 null 이면 이동을 생략 (R-U8-1 틈) | `push.test.ts` 새 "… schedule_id:null …" |
| X4 | `test-setup.ts` 의 가짜 fetch 가 실패 대신 성공 응답을 돌려준다 (27b) | `network.test.ts` 2건 · `api.test.ts` "기본 fetch" (그 밖에 응답을 받아 깨지는 `routes.test.tsx` 3건은 부수 효과라 표에 올리지 않음) |
| X5 | 채팅 칩: 선택 뒤 나머지 칩을 비활성으로 만들지 않음 | `e2e/chat.spec.ts` |
| X6 | 채팅: 새로고침 뒤 대기 질문을 화면에 복원하지 않음 | `e2e/chat.spec.ts` |
| X7 | `X-Session-Id` 헤더를 보내지 않음 | `e2e/chat.spec.ts` |
| X8 | 사이드바 고정 기준 폭 1024 → 1400px (1280px 에서 서랍형이 됨) | `e2e/card.spec.ts` 데스크톱 |
| X9 | 모바일 서랍이 항목을 고른 뒤 닫히지 않음 | `e2e/card.spec.ts` 모바일 |
| X10 | 원문 펼침에 원문(`raw_utterance`) 대신 요약(`content`)을 표시 | `e2e/card.spec.ts` 데스크톱 |
| X11 | 하단 탭바(`role="tablist"`)를 추가 | `e2e/card.spec.ts` 모바일 |
| X12 | 브리핑 강조 표시(`data-highlight`) 제거 | `e2e/briefing.spec.ts` |
| X13 | 쿼리의 일정을 맨 위로 올리지 않고 서버 순서 그대로 | `e2e/briefing.spec.ts` |
| X14 | "지금 브리핑" 뒤 목록 다시 읽기 제거 | `e2e/briefing.spec.ts` |
| X15 | `index.html` 에 외부 글꼴 주소(`fonts.googleapis.com`) 요청 추가 (27b 요청 URL 단언) | E2E 4편 전부(요청 URL 단언) |
| X16 | 앱 시작 때 가짜 표에 없는 `/api/stray` 요청 추가 — 화면에는 영향 없음 (27b) | E2E 4편 전부(`unexpected` 단언) |

X5·X6·X7·X13 은 첫 시도에서 변이가 타입 오류를 내 빌드가 실패했다(변이로서 무효). 타입이 맞는 형태로 고쳐 다시 돌려 검출을 확인했고 두 시도 모두 증거에 남아 있다.

---

## web/src/__tests__/api.test.ts — API 클라이언트 래퍼 (6건)

실행: `cd web && npm test -- --run src/__tests__/api.test.ts` · 증거 `evidence/20261015-1410-u9-vitest-verbose.txt` (파일별 통과 수는 `…-u9-front-rows.txt` 에 없음 — api·proxy 는 전체 verbose 로 확인).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| api.test.ts::기본 경로는 /api 이고 GET 은 본문·Content-Type 이 없다 | 요청 주소 접두와 GET 모양 | `apiFetch('/persons')` → fetch URL `/api/persons`, method `GET`, body 없음, headers `{}` | 통과 · U4-M4 |
| api.test.ts::POST 는 JSON 본문과 X-Session-Id 헤더를 보낸다 | POST 본문 직렬화·세션 헤더 이름 | `apiFetch('/chat',{method:'POST',body:{utterance:'안녕'},sessionId:'abc-1'})` → body `{"utterance":"안녕"}`, headers `Content-Type`+`X-Session-Id: abc-1` | 통과 · U4-M4 · U4-M6 |
| api.test.ts::sessionId 가 null 이면 헤더를 넣지 않는다 | 세션을 일부러 비울 때 | `sessionId: null` → headers `{}` | 통과 · — |
| api.test.ts::P5 오류 규약 {"detail":{"code"}} 를 ApiError 로 올린다 | 오류 본문 → `ApiError(status, code)` | 409 `{detail:{code:'already_answered'}}` → `ApiError`, status 409, code `already_answered` | 통과 · U4-V2 |
| api.test.ts::규약 밖 본문(422 검증 목록, 비-JSON 5xx)은 code 가 null | 규약 밖 오류 본문 | 422 `{detail:[{msg}]}` · 500 `boom` → 둘 다 `code === null`, status 유지 | 통과 · U4-V2 |
| api.test.ts::테스트 환경의 기본 fetch 는 실제 네트워크를 쓰지 않고 실패한다 (결정 J) | setup 의 안전망이 켜져 있다 | 가짜 없이 `apiFetch('/persons')` → "실제 네트워크" 메시지로 reject | 통과 · U4-V3 · U9-X4 |

## web/src/__tests__/proxy.test.ts — 개발 서버 프록시 (6건)

실행: `cd web && npm test -- --run src/__tests__/proxy.test.ts`.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| proxy.test.ts::환경 변수가 없거나 비면 기본값 | 프록시 대상 기본값 | `resolveApiTarget({})` · `{VITE_API_TARGET:''}` → `http://localhost:8000` (`DEFAULT_API_TARGET` 도 같은 값) | 통과 · — |
| proxy.test.ts::VITE_API_TARGET 이 있으면 그 값 | 환경 변수 우선 | `{VITE_API_TARGET:'http://x:9'}` → `http://x:9` | 통과 · U5-M12 |
| proxy.test.ts::/api 프록시가 stripApiPrefix 로 접두를 벗긴다 | `vite.config.ts` 의 `/api` 규칙이 `stripApiPrefix` 로 연결돼 있다 | 설정 함수 호출 → `server.proxy['/api'].rewrite === stripApiPrefix`, `rewrite('/api/persons/3') === '/persons/3'` | 통과 · — (앞 판 이름의 같은 단언이 U4-R1·R2·V1 에 검출됨, 현재 이름으로는 미확인) |
| proxy.test.ts::/api 접두를 벗긴다 | 접두 제거 값 | `/api/persons/3`→`/persons/3`, `/api/chat`→`/chat`, `/api/briefings?schedule_id=4` → 쿼리 유지 | 통과 · U4-R2 |
| proxy.test.ts::/api 만 오면 루트 / | 경계: 접두만 | `/api`→`/`, `/api?x=1`→`/?x=1` | 통과 · U4-R2 |
| proxy.test.ts::/api 로 시작하지 않는 경로는 그대로 (접두가 비슷한 /apix 포함) | 비슷한 접두를 건드리지 않음 | `/other`·`/apix/persons`·`/x/api/persons` → 그대로 | 통과 · — |

## web/src/__tests__/routes.test.tsx — 해시 라우팅·앱 틀(사이드바) (14건)

실행: `cd web && npm test -- --run src/__tests__/routes.test.tsx` → 14 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 13행). 가짜 `matchMedia`(`helpers.ts`)로 폭을 바꾼다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| routes.test.tsx::#/chat 는 chat 빈 화면을 그린다 | 해시 → 화면 하나 (it.each 1/3) | `#/chat` 렌더 → `[data-screen]` 1개 = `chat`, h1 "채팅" | 통과 · — |
| routes.test.tsx::#/persons 는 persons 빈 화면을 그린다 | (it.each 2/3) | `#/persons` → `data-screen=persons`, h1 "인물" | 통과 · — |
| routes.test.tsx::#/briefings 는 briefings 빈 화면을 그린다 | (it.each 3/3) | `#/briefings` → `data-screen=briefings`, h1 "브리핑" | 통과 · — |
| routes.test.tsx::#/persons/:id 는 인물 화면에 id 를 넘긴다 | id 를 화면이 받는다 | `#/persons/12` → `data-person-id="12"` | 통과 · — |
| routes.test.tsx::알 수 없는 해시는 #/chat 으로 보낸다 | 화면 3개 고정(원칙5) — 모르는 주소는 채팅 | `#/nope` → chat 화면 + 주소가 `#/chat` 으로 바뀜 | 통과 · U4-M1 · U4-V4 |
| routes.test.tsx::해시가 비어 있어도 #/chat 으로 보낸다 | 해시 없음 | `/` → chat 화면 + `#/chat` | 통과 · U4-M1 · U4-V4 |
| routes.test.tsx::parseHash 경계: 숫자가 아닌 id·끝 슬래시·쿼리 | 라우트 표 경계 | `#/persons/abc`·`#/persons/`·`#/chat/extra` → null / `#/briefings?schedule_id=3` → briefings / `#/persons/7` → id 7 / `#/persons` → id null | 통과 · U4-M5 · U4-V5 |
| routes.test.tsx::데스크톱 폭에서는 사이드바가 항상 보이고 메뉴 버튼이 없다 | 결정 N 데스크톱 | 1280px → 사이드바 링크 3개 `[채팅 #/chat, 인물 #/persons, 브리핑 #/briefings]`, "메뉴 열기" 없음, 인물 목록 자리 있음 | 통과 · U4-M8 |
| routes.test.tsx::지금 화면 항목에 aria-current 가 붙는다 | 현재 화면 표시 | `#/briefings` → 브리핑 링크 `aria-current=page`, 채팅 링크엔 없음 | 통과 · — |
| routes.test.tsx::좁은 폭: 기본은 접혀 있고 메뉴 버튼으로 열린다 | 모바일 서랍 열기 | 800px → 사이드바 없음, "메뉴 열기" 클릭 → 사이드바 보임 | 통과 · — |
| routes.test.tsx::좁은 폭: 항목을 고르면 서랍이 닫히고 그 화면이 보인다 | 항목 선택 시 닫힘 | 서랍 열고 "브리핑" 클릭 → 사이드바 사라짐 + briefings 화면 | 통과 · U4-M3 · U4-M8 |
| routes.test.tsx::좁은 폭: Esc 와 바깥(배경) 클릭으로도 닫힌다 | 서랍 닫는 두 방법 | Esc → 닫힘 / 다시 열고 `sheet-overlay` 클릭 → 닫힘 | 통과 · U4-M7 |
| routes.test.tsx::열림/닫힘은 라우트도 localStorage 도 바꾸지 않는다 | 서랍 상태는 레이아웃 상태일 뿐 | `#/persons` 에서 서랍 열기 → 해시 그대로, `localStorage.length === 0` | 통과 · U4-M9 |
| routes.test.tsx::1024px 경계: 1023 은 서랍형, 1024 는 고정 사이드바 | 결정 N 기준 폭 | 1023px → "메뉴 열기" 있음 / 1024px → 없음 + 사이드바 | 통과 · U4-M2 |

## web/src/__tests__/chat.test.tsx — 채팅 화면·확인 칩 (22건)

실행: `cd web && npm test -- --run src/__tests__/chat.test.tsx` → 22 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 14~17b행). 가짜 `fetch` 라우터로 `/api/chat`·`/api/answers/{id}`·`/api/questions/pending` 에 답한다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| chat.test.tsx::발화를 POST /api/chat 으로 보내고 내 말풍선과 reply 를 보여 준다 | 전송 흐름·서버 문장 그대로 | "민수랑 점심 먹었어" 입력·전송 → POST `/api/chat` 본문 `{utterance}`, 내 말풍선 `data-role=user`, 서버 `reply` 그대로 | 통과 · — |
| chat.test.tsx::첫 요청에는 X-Session-Id 가 없고, 응답 session_id 를 저장해 두 번째 요청에 보낸다 | 판정 14 세션 보관 | 첫 전송(헤더 없음) → 응답 `sess-abc` → localStorage 저장 → 두 번째 전송 헤더 `X-Session-Id: sess-abc` | 통과 · U5-M3 · U5-M6 |
| chat.test.tsx::저장된 세션이 있으면 진입 시 복원 요청에도 헤더를 보낸다 | 복원 요청도 세션 사용 | localStorage `sess-old` → `GET /api/questions/pending` 1회, 헤더 `sess-old` | 통과 · U5-M3 · U5-V3 |
| chat.test.tsx::422 invalid_session_id 면 저장된 세션을 버리고 다음 요청은 헤더 없이 간다 | 서버가 세션을 모를 때 | 422 `invalid_session_id` → 안내 `세션이 초기화됐어요`, localStorage 비움, 다음 전송 헤더 없음 | 통과 · U5-M9 |
| chat.test.tsx::Enter 는 전송, Shift+Enter 는 줄바꿈 | 판정 17b 입력 키 | "한 줄 Shift+Enter 두 줄" → 요청 0, 값 `한 줄\n두 줄` / Enter → POST 1회, 본문 줄바꿈 유지 | 통과 · U5-M7 |
| chat.test.tsx::빈 입력은 보낼 수 없다 | 빈 전송 방지 | 처음·공백만 입력 → "보내기" 비활성 | 통과 · — |
| chat.test.tsx::응답을 기다리는 동안 타이핑 점이 보이고 끝나면 사라진다 | 판정 17b 대기 표시 + R-U5-4 | 응답 보류 중 → 타이핑 점 표시, 새 글자를 써도 "보내기" 비활성 / 응답 도착 → 점 사라짐, 버튼 활성 | 통과 · — |
| chat.test.tsx::한글 조합 중(isComposing) Enter 는 전송이 아니다 (R-U5-4) | 한글 입력 조합 중 Enter | `keyDown Enter isComposing:true` → POST 0 | 통과 · — |
| chat.test.tsx::확인 칩이 떠 있어도 입력은 막히지 않는다 (결정 E) | 판정 16 새 발화 우선 | 칩이 뜬 상태 → 입력창 활성, 타자 입력됨 | 통과 · — |
| chat.test.tsx::칩 글자와 순서가 options 와 같다 (reply 바로 아래) | 판정 15 / 원칙7 — 칩 문자열 가공 없음 | 가나다 순이 아니고 앞뒤 공백이 든 options 3개 → 칩 `textContent` 가 그대로·같은 순서, 칩 묶음이 그 reply 말풍선 안 | 통과 · U5-M1 · U5-M10 · U6-M10 |
| chat.test.tsx::칩을 누르면 POST /api/answers/{id} 에 그 문자열이 {answer} 로 가고, 선택 고정·나머지 비활성 | 판정 15 칩 클릭 | 두 번째 칩 클릭 → POST `/api/answers/7` 본문 `{answer: 그 문자열}` 1회, 누른 칩 `aria-pressed=true`, 나머지 `false` + 비활성 | 통과 · U5-M2 · U5-M8 · U5-M11 · U6-M10 |
| chat.test.tsx::답 응답의 reply 가 이어 붙고, 새 pending_question 이면 그 아래 새 칩 | 판정 15 재개 | "예" 클릭 → 응답 `reply` 가 이어 붙고 `chips-8` 3개(오늘·내일·모레)가 그 말풍선 안, 앞 칩은 고정 | 통과 · U5-M1 · U5-M10 · U5-M11 · U5-V2 · U6-M10 |
| chat.test.tsx::진입 시 GET /api/questions/pending 으로 미답변 전부를 질문별로 복원한다 | 판정 16 복원 | 미답변 2건 → 질문 글과 칩 묶음 2개(`chips-3`·`chips-4`) 복원, 요청 1회 | 통과 · U5-M1 · U5-M10 |
| chat.test.tsx::답할 때 409 already_answered 면 그 질문 칩을 모두 비활성으로 두고 한 줄 안내 | 판정 17 (it.each 1/2) | 칩 클릭 → 409 → 그 질문 칩 전부 비활성, 안내 "이미 답했거나 만료된 질문이에요.", 다른 질문 칩은 활성, 재시도 없음(요청 1회) | 통과 · U5-M4 · U5-M10 · U5-M11 · U5-M13 |
| chat.test.tsx::답할 때 409 expired 면 그 질문 칩을 모두 비활성으로 두고 한 줄 안내 | (it.each 2/2) 코드가 달라도 같은 처리 | 위와 같고 코드 `expired` | 통과 · U5-M4 · U5-M10 · U5-M11 · U5-M13 · U5-V4 |
| chat.test.tsx::답 전송이 5xx 로 실패하면 안내 한 줄을 띄우고 칩은 다시 누를 수 있다 | 일시 오류는 칩을 영구 잠그지 않음 | `/api/answers/3` 500 → 안내 "요청을 처리하지 못했어요…", 칩 활성 | 통과 · U5-V5 |
| chat.test.tsx::POST /api/chat 이 5xx 면 안내 한 줄 | 판정 17 오류 | `/api/chat` 500 → 안내 한 줄, 내 말풍선은 남음 | 통과 · — |
| chat.test.tsx::네트워크 실패(fetch 거부)면 안내 한 줄 | 전송 중 네트워크 실패 | fetch 가 `TypeError` → 같은 안내 한 줄 | 통과 · — |
| chat.test.tsx::진입 시 복원 요청이 실패하면 한 줄 안내가 뜨고 빈 상태 안내도 남는다 (R-U5-2) | 복원 실패 안내 | 복원 fetch 거부 → `alert` "이전에 남은 질문을…" + 빈 상태 안내 유지 | 통과 · — |
| chat.test.tsx::stored.persons > 0 이면 #/persons 링크가 붙는다 | 카드 화면 링크 조건 | `stored.persons:1` → 링크 "인물 카드 보기" `href="#/persons"` | 통과 · — |
| chat.test.tsx::stored.events > 0 이어도 링크가 붙는다 | 링크 조건(사건) | `stored.events:2` → 링크 있음 | 통과 · — |
| chat.test.tsx::저장된 인물·사건이 없으면(일정만 있어도) 링크가 없다 | 링크 조건 경계 | `stored.schedules:3` 만 → 링크 0 | 통과 · U5-M5 |

## web/src/__tests__/card.test.tsx — 인물 목록·카드·원문 펼치기 (29건)

실행: `cd web && npm test -- --run src/__tests__/card.test.tsx` → 29 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 18·19행). 날짜는 한낮(UTC 12:00)이라 시간대와 무관하다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| card.test.tsx::서버 순서 그대로(재정렬 없음) 이름·태그·위계·마지막 접촉 4개 필드를 보여 준다 | 목록 순서·필드 | 서버가 박대리·철수·엄마(날짜·이름·id 순 어느 쪽도 아님)로 줌 → 그 순서, 태그 `직장·친구·가족`, 위계 `하·동·상`, 마지막 접촉 `2026. 9. 1.`·`2026. 10. 5.`·"기록 없음" | 통과 · U6-M1 |
| card.test.tsx::필터·검색 컨트롤이 없다 | 판정 19 필터 0 | 목록 화면 → textbox·searchbox·combobox 없음 | 통과 · — |
| card.test.tsx::빈 목록이면 빈 상태 문구 하나 | 빈 상태 | `[]` → "아직 기록된 인물이 없어요." | 통과 · — |
| card.test.tsx::목록 조회가 실패하면 한 줄 안내 | 오류 | 500 → "인물 목록을 불러오지 못했어요." | 통과 · — |
| card.test.tsx::항목 링크는 #/persons/:id 이고 누르면 해시가 바뀐다 | 항목 → 카드 이동 | 링크 href `#/persons/7`·`/4`·`/9`, 두 번째 클릭 → `#/persons/4` | 통과 · U6-M1 |
| card.test.tsx::#/persons 본문과 사이드바에 같은 목록이 같은 순서로 그려진다 | 결정 N — 같은 목록 두 자리 | `#/persons` 앱 렌더 → 사이드바 1·본문 1, `innerHTML` 동일, 링크 글자 3줄 같은 순서 | 통과 · U6-M1 |
| card.test.tsx::R-U6-2: 앱을 열면 GET /persons 는 1회(사이드바·본문이 한 번 받은 값을 같이 쓴다) | 중복 조회 방지 | 앱 열기 → `/api/persons` 1회 | 통과 · — |
| card.test.tsx::R-U6-2: 해시 라우트가 바뀌면 다시 읽어 새 인물이 사이드바에 보인다 | 사이드바 갱신 | 서버 목록에 철수 추가 후 `#/persons` 이동 → 사이드바에 철수, 요청 2회 | 통과 · U7-M17 |
| card.test.tsx::R-U6-2: 채팅 응답 stored.persons > 0 이면 다시 읽고, 0 이면 읽지 않는다 | 새 인물 생기면 목록 갱신 | 채팅 응답 `stored.persons:1` → 사이드바에 철수, `/api/persons` 2회 | 통과 · U7-M18 |
| card.test.tsx::R-U6-2: 채팅 응답 stored.persons 가 0 이면(사건만 저장) 인물 목록을 다시 읽지 않는다 | 갱신 경계 | `stored.events:2`·persons 0 → 50ms 뒤에도 `/api/persons` 1회 | 통과 · U7-M19 |
| card.test.tsx::R-U6-2: 알림 이벤트(persons-changed)만으로도 다시 읽는다 | 이벤트 통로 | `notifyPersonsChanged()` → `/api/persons` 2회 | 통과 · — |
| card.test.tsx::R-U7-2 (탐침 P2c): 먼저 보낸 느린 조회가 나중 조회보다 늦게 도착해도 사이드바는 나중 조회 값이다 | 늦게 온 옛 응답 무시 | 1차 조회 보류, 2차 즉시(철수) → 1차 뒤늦게 도착해도 사이드바 = 철수(박대리 없음) | 통과 · U8-M25 |
| card.test.tsx::사이드바와 본문이 같은 컴포넌트(PersonList)를 import 한다 | 같은 컴포넌트 사용(결정 N) | `AppShell.tsx`·`PersonCardScreen.tsx` 소스에 같은 `import PersonList …` 줄 | 통과 · U6-V5 |
| card.test.tsx::좁은 폭: 서랍에서 항목을 고르면 서랍이 닫힌다 | 서랍 안 인물 선택 | 800px, 서랍의 "철수" 클릭 → 해시 `#/persons/4`, 서랍 닫힘 | 통과 · — |
| card.test.tsx::섹션 7개가 부록 A ② 순서로 놓인다 | 카드 섹션 순서 | `data-section` 순서 `header·aliases·last-contact·facts·patterns·timeline·schedules`, h2 `김팀장`·▸알고 있는 것·▸반복 패턴·▸타임라인·▸다가오는 일정 | 통과 · U6-V2 |
| card.test.tsx::각 섹션의 값이 서버가 준 그대로 나온다 | 판정 19 항목 렌더 | 머리 `김팀장`·`직장 · 상`, `별칭: 팀장, 우리 팀장님, 부장님`, `마지막 접촉: 2026. 9. 3.`, 사실 key/value, 패턴 key/value, 일정 제목·날짜 | 통과 · U6-V2 |
| card.test.tsx::타임라인은 서버 순서 그대로, 항목마다 날짜·type·content | 타임라인 순서 | 서버 순서 5·9·2(날짜순 아님) → `timeline-5`,`-9`,`-2`, 첫 항목에 `2026. 8. 21.`·`meal`·`점심 같이 함` | 통과 · U6-M6 |
| card.test.tsx::source_count 가 0 이면 근거 보기 버튼이 없고, 양수면 있다 | 근거 없는 사실엔 버튼 없음 | 사실 11(2건)·21(3건) 버튼 있음, 사실 12(0건) 버튼 없음 | 통과 · — |
| card.test.tsx::비어 있는 섹션은 짧은 빈 문구를 보여 준다 | 빈 상태 문구 | 전부 빈 카드 → `별칭: 없음`, `마지막 접촉: 기록 없음`, 섹션별 빈 문구 4개 | 통과 · U6-V2 |
| card.test.tsx::404 면 안내 한 줄과 목록으로 가는 링크 | 판정 K — 없는 인물 | `/api/persons/3` 404 → `alert` "인물을 찾을 수 없어요." + 링크 "인물 목록으로" `#/persons`, 카드 없음 | 통과 · U6-V4 |
| card.test.tsx::404 가 아닌 실패는 다른 안내 문장 | 오류 구분 | 500 → "인물 카드를 불러오지 못했어요." | 통과 · U6-V4 |
| card.test.tsx::카드·목록 응답에 원문이 없으면 아무 데도 원문이 보이지 않고, 원문 요청도 없다 | 결정 F — 펼치기 전엔 원문 없음 | 카드 렌더 → `raw-utterance` 0, 본문에 원문 글자 없음, 요청은 `/api/persons/3` 하나뿐 | 통과 · — |
| card.test.tsx::첫 펼침에 GET /events/{id}/raw 1회, 원문은 글자 그대로, 접었다 다시 펼쳐도 요청은 1회 | 판정 18 | 특수문자·꼬리 공백·연속 개행 든 원문 → 펼침 1회째 GET 1회, `textContent` 동일 / 접기 → 숨김 / 다시 펼침 → 같은 원문, 요청 계속 1회 | 통과 · U6-M3 |
| card.test.tsx::다른 항목은 각자 한 번씩 요청한다 | 항목별 캐시 | 항목 9·2 펼침 → 각 `/api/events/{id}/raw` 1회 | 통과 · — |
| card.test.tsx::조회 실패는 그 항목 안에만 안내가 뜨고, 다시 누르면 재시도(요청 2회)해 원문이 나온다 | 실패 국소화 | 첫 요청 500 → 그 항목 안 `alert` "원문을 불러오지 못했어요…" 1개뿐, 카드·다른 항목 정상 / 다시 누름 → 요청 2회째 성공 | 통과 · U6-M3 |
| card.test.tsx::R-U6-1: 로딩 중 접기 → 요청 실패 → 다시 펼치면 열리고 재시도해 원문이 나온다 | 경합 경계 | 펼침(로딩) → 접음 → 첫 요청 실패 → 다시 펼침 → 열리고 2회째 요청으로 원문 | 통과 · U7-M16 |
| card.test.tsx::근거 보기: sources 요청 1회, 항목 수·날짜·content·원문이 그대로, 접기, 다시 펼쳐도 재요청 없음 | 판정 19 근거 보기 | "근거 보기" → `GET /api/persons/3/facts/11/sources` 1회, 2건(날짜 · content · 원문 동일) / 접기·다시 펼침 → 재요청 없음 | 통과 · U6-V3 |
| card.test.tsx::패턴의 근거 보기도 그 패턴 id 로 요청한다 | 패턴도 같은 경로 | 패턴 21 "근거 보기" → `/facts/21/sources` 1회, 원문 표시 | 통과 · — |
| card.test.tsx::근거 조회 실패는 그 사실 안에만 안내, 다시 누르면 재시도(요청 2회) | 근거 실패 국소화 | 첫 요청 500 → 그 사실 안 `alert` 1개, 다른 사실엔 없음 / 다시 누름 → 성공, 요청 2회 | 통과 · — |

## web/src/__tests__/briefing.test.tsx — 브리핑 화면·수동 브리핑 (19건)

실행: `cd web && npm test -- --run src/__tests__/briefing.test.tsx` → 19 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 20·21행). 서버 순서를 id·이름·시각 어느 쪽으로 다시 줄 세워도 달라지게 골랐다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| briefing.test.tsx::서버 순서 그대로(재정렬 없음), 머리줄은 일정 시각 · 이름 · 일정 제목 | 판정 20 머리줄·순서 | 응답 5·2·9 → `briefing-5`,`-2`,`-9` 순, h2 `📌 <일정 시각> · 김팀장 · 분기 회의` 등 | 통과 · U7-M1 · U7-M9 |
| briefing.test.tsx::패턴 문장·요약 줄·제안이 서버 문자열 그대로이고 순서(패턴 → 줄 → 제안)를 지킨다 | 원칙7 — 서버 문장 가공 없음 | 꺾쇠·따옴표·꼬리 공백이 든 문장 → `textContent` 동일, 패턴 → 줄1 → 줄2 순, 제안 h3 "💡 제안" | 통과 · U7-M2 · U7-M3 · U7-M7 |
| briefing.test.tsx::basis 는 화면에 나오지 않는다 | 숨김 필드 | `basis` 의 키·id 문자열이 본문에 없음 | 통과 · U7-M2 |
| briefing.test.tsx::제안이 없으면 제안 구획이 없다 | 판정 20 `suggestion: null` | 제안 null 항목 → 제안 구획·h3 없음 | 통과 · — |
| briefing.test.tsx::빈 목록이면 빈 상태 문구 하나 | 판정 20 빈 상태 | `[]` → "아직 만들어진 브리핑이 없어요.", 목록 없음 | 통과 · U7-M15 |
| briefing.test.tsx::목록 조회가 실패하면 한 줄 안내(빈 상태 문구는 아님) | 오류 vs 빈 상태 구분 | 500 → "브리핑을 불러오지 못했어요.", 빈 상태 문구 없음 | 통과 · U7-V5 · U8-M26 |
| briefing.test.tsx::항목마다 "지금 브리핑" 버튼이 있고, 알림 받기 버튼이 활성이며 /push-dev/ 링크가 없다 (구독 동작은 push.test.ts) | 버튼 자리·개발 페이지 링크 없음 | 3건 → "지금 브리핑" 3개, "알림 받기" 활성, `a[href*="push-dev"]` 0 | 통과 · — |
| briefing.test.tsx::쿼리가 없으면 서버 순서 그대로이고 단건 요청은 0 | 쿼리 없을 때 | `#/briefings` → 요청은 `/api/briefings` 하나뿐, `data-highlight` 없음 | 통과 · — |
| briefing.test.tsx::목록 안에 있으면 맨 위로 올리고 강조하며(나머지는 서버 순서) 단건 요청은 0 | 판정 26 단위 대응 — 강조·맨 위 | `?schedule_id=9` → 순서 9·5·2, 9 만 `data-highlight`, 요청 1개, 강조 카드에만 `ring-2` 클래스 | 통과 · U7-M1 · U7-M6 · U7-M8 · U7-M13 · U8-M24 |
| briefing.test.tsx::목록에 없으면 GET /briefings?schedule_id=N 을 1회 더 불러 맨 위에 붙이고 강조한다 | 7일 창 밖 일정 | `?schedule_id=77`(목록에 없음) → 요청 `/api/briefings` + `?schedule_id=77` 각 1회, 순서 77·5·2·9, 77 강조 | 통과 · U7-M1 · U7-M8 · U7-M14 · U7-V2 |
| briefing.test.tsx::단건이 404 이거나 [] 이면 안내 한 줄 + 나머지 목록 그대로 | 없는 일정 | 단건 404 / `[]` 각각 → "그 일정의 브리핑이 아직 없어요.", 목록 5·2·9, 강조 없음 | 통과 · U7-M1 |
| briefing.test.tsx::R-U7-3: 단건 조회가 404 가 아닌 오류로 실패하면 목록 실패 문구가 아니라 "그 일정" 문구 — 목록은 그대로 | 오류 문구 구분 | 단건 500 → `schedule-failed` "그 일정의 브리핑을 불러오지 못했어요.", 목록 실패 문구 없음, 목록 그대로 | 통과 · U8-M20 |
| briefing.test.tsx::parseScheduleId: 양의 정수만 인정한다 | 쿼리 파싱 경계 | `=12`→12, 없음/0/abc/1.5 → null, `x=1&schedule_id=3` → 3 | 통과 · U7-M20 |
| briefing.test.tsx::POST 본문은 {schedule_id} 이고, 성공하면 응답을 끼우지 않고 GET /briefings 를 다시 읽어 갱신한다 | 판정 21 수동 브리핑 | "지금 브리핑"(일정 2) → POST `/api/briefings/run` 본문 `{schedule_id:2}` 1회 → `GET /api/briefings` 2회째, 새 줄 "새로 만든 줄" 표시, 순서 2·9 | 통과 · U7-M2 · U7-M4 · U7-M12 |
| briefing.test.tsx::진행 중에는 그 버튼이 비활성(진행 표시)이고, 끝나면 다시 활성 | 중복 클릭 방지 | POST 보류 중 → 그 항목 "브리핑 만드는 중" 비활성, 다른 항목 버튼은 활성 / 완료 → 다시 활성 | 통과 · U7-M10 |
| briefing.test.tsx::404(잠금 중)이면 "잠시 뒤 다시 시도" 안내만 — 자동 재시도 없음(POST 1회), 목록 재요청도 없고 버튼은 다시 활성 | 판정 21·결정 K | POST 404 → 그 항목에만 "잠시 뒤 다시 시도해 주세요.", 50ms 뒤에도 POST 1회·GET 1회, 버튼 활성 | 통과 · U7-M5 · U7-M11 · U7-V1 |
| briefing.test.tsx::5xx 이면 한 줄 실패 안내(잠금 문구가 아님), 버튼은 다시 활성이고 누르면 다시 보낸다 | 일반 오류 | 첫 POST 500 → `alert` "브리핑을 만들지 못했어요…"(잠금 문구 아님) / 다시 누름 → POST 2회·성공 시 GET 재조회·안내 사라짐 | 통과 · U7-M4 · U7-V1 |
| briefing.test.tsx::R-U7-2 (탐침 P4): 수동 브리핑은 성공했는데 재조회가 실패하면 이전 목록 3건을 그대로 두고 실패 한 줄만 더한다 | 재조회 실패 시 화면 유지 | 재조회 500 → 목록 5·2·9 그대로 + "브리핑을 불러오지 못했어요.", 빈 상태 문구 없음 | 통과 · U8-M26 |
| briefing.test.tsx::R-U7-1: 수동 브리핑이 진행 중일 때 쿼리가 바뀌면, 끝난 뒤 재조회는 바뀐 일정(최신) 기준이다 | 경합 — 최신 쿼리 기준 | 진행 중 `?schedule_id=77` → `88` 로 바뀜 → 끝난 뒤 목록 88·5·2·9, 77 없음, 88 강조 | 통과 · U8-M19 |

## web/src/__tests__/sw.test.ts — 서비스 워커·manifest (16건)

실행: `cd web && npm test -- --run src/__tests__/sw.test.ts` → 16 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 22행). `public/sw.js` 를 `?raw` 로 읽어 가짜 `self`(리스너·registration·clients) 안에서 평가한다. 실제 워커·푸시 서비스는 쓰지 않는다. 이번 단위에서 2건 추가(R-U8-3).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| sw.test.ts::페이로드를 showNotification(title, {body, tag, data:{schedule_id}}) 로 그대로 넘긴다 | 원칙7 — 알림 문장 가공 없음 | `push` `{title:'  김팀장 회의 30분 전 ', body:…, tag:'schedule-12', schedule_id:12, ttl:600}` → `showNotification` 1회, title·body 앞뒤 공백까지 그대로, `data:{schedule_id:12}` | 통과 · U8-M3 · U8-M9 · U8-V1 |
| sw.test.ts::열린 모든 창에 {type:"briefing", schedule_id} 만 보낸다(title·body 는 보내지 않는다) | 열린 창 알림 | 창 2개 → 각 `postMessage({type:'briefing', schedule_id:7})` 정확히 1회 | 통과 · U8-M4 |
| sw.test.ts::schedule_id 가 빠진 페이로드면 data.schedule_id 와 메시지 모두 null | 일정 없는 푸시 | `{title,body,tag}` → `data:{schedule_id:null}`, 창 메시지 `schedule_id:null` | 통과 · U8-M3 · U8-M4 · U8-V1 |
| sw.test.ts::JSON 을 못 읽거나 데이터가 없으면 기본 제목 "알림"·빈 본문으로 띄운다 | 잘못된 페이로드 | `json()` 이 던짐 / `data:null` → 제목 "알림", body "" | 통과 · U8-M3 · U8-M8 |
| sw.test.ts::열린 창이 있으면 알림을 닫고 첫 창을 focus 한 뒤 {type:"open-briefing", schedule_id} 를 보낸다(새 창 없음) | 판정 22 알림 클릭(창 있음) | 앱 창 2개 → 알림 `close` 1회, 첫 창 `focus` 1회 + `postMessage({type:'open-briefing', schedule_id:12})`, 둘째 창 무변화, `openWindow` 0 | 통과 · U8-M6 · U8-M7 · U9-X2 |
| sw.test.ts::앱이 아닌 같은 출처 창이 앞에 있어도 앱 창(client.url 경로 "/")을 골라 focus 한다 | **R-U8-3 (신규)** — 개발용 페이지·`/api/docs` 탭이 앞에 있어도 | 창 `[/dev-page/, /api/docs, /#/persons]` → 앱 창만 `focus`+`postMessage(open-briefing, 12)`, 앞 두 창은 손대지 않음, `openWindow` 0 | 통과 · U9-X1 · U9-X2 |
| sw.test.ts::열린 창이 전부 앱이 아니면 그 창들은 건드리지 않고 openWindow("/#/briefings?schedule_id=N") | **R-U8-3 (신규)** — 앱 창이 없을 때 | 창 `[/dev-page/, /api/docs]` → `openWindow('/#/briefings?schedule_id=12')` 1회, 두 창 `focus`·`postMessage` 0 | 통과 · U9-X1 |
| sw.test.ts::열린 창이 없으면 openWindow("/#/briefings?schedule_id=N") | 판정 22 알림 클릭(창 없음) | 창 0 → `openWindow('/#/briefings?schedule_id=12')` 1회 | 통과 · U8-M5 |
| sw.test.ts::schedule_id 가 없거나 양의 정수가 아니면 일정 없는 브리핑 화면 주소 | 새 창 주소 경계 | `data` 가 null·`{}`·null·0·'12'·1.5 → `openWindow('/#/briefings')` | 통과 · U8-V2 |
| sw.test.ts::start_url 은 /#/chat, display 는 standalone | PWA manifest | `manifest.webmanifest` → `start_url:'/#/chat'`, `display:'standalone'` | 통과 · U8-M27 · U8-M28 |
| sw.test.ts::이름은 index.html <title> 과 같고, 색은 tokens.css 의 primary(#171717)·background(#ffffff) | 이름·색 일치 | `name`·`short_name` = `<title>`, `theme_color #171717`, `background_color #ffffff`, `<meta theme-color>` | 통과 · — |
| sw.test.ts::아이콘은 192·512 두 개이고 각각 실제 파일이다(외부 주소 없음) | 아이콘 2종 | icons `[192x192 /icon-192.svg, 512x512 /icon-512.svg]`, 타입 svg, 경로 `/` 시작, 각 svg 의 `width` | 통과 · U8-V5 |
| sw.test.ts::index.html 이 manifest 를 연결하고, favicon 은 같은 아이콘이다(템플릿 로고 아님) | manifest 연결·favicon | `<link rel="manifest" href="/manifest.webmanifest">`, favicon `fill="#171717"`·글자 "관", 템플릿 색 `#863bff` 없음 | 통과 · U8-M29 · U8-M30 |
| sw.test.ts::등록되는 리스너는 install · activate · push · notificationclick 넷뿐이다 | 결정 I — fetch 리스너 없음 | 등록된 이벤트 이름 정렬 → `['activate','install','notificationclick','push']` | 통과 · U8-M1 |
| sw.test.ts::install 은 skipWaiting, activate 는 clients.claim 만 한다 | 설치·활성 동작 | `install`→`skipWaiting` 1회, `activate`→`clients.claim` 1회 | 통과 · U8-M2 |
| sw.test.ts::코드에 요청 가로채기 리스너·캐시 API 호출이 없다 | 결정 I·M — 캐시 없음 | `sw.js` 소스에 `addEventListener('fetch'`·`onfetch`·`caches`·`Cache`·`fetch(` 없음 | 통과 · U8-M1 · U8-M2 |

## web/src/__tests__/push.test.ts — 푸시 구독·"알림 받기"·인앱 배너 (21건)

실행: `cd web && npm test -- --run src/__tests__/push.test.ts` → 21 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 22·23행). `Notification`·`PushManager`·`navigator.serviceWorker`·`fetch` 전부 가짜. 이번 단위에서 1건 추가(R-U8-1).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| push.test.ts::base64url(-, _, 패딩 없음)을 바이트로 바꾼다 | VAPID 공개키 변환 | `AQID`→[1,2,3], `AQI`→[1,2], `-__-`→[251,255,254] | 통과 · U8-M15 |
| push.test.ts::새 구독: 권한 → 등록(/sw.js) → 공개키 → 구독 → 서버 저장 순서이고, 본문은 PushSubscriptionIn 필드 그대로 | 판정 23 구독 절차 | `subscribeToPush()` → 호출 순서 `permission, register, GET key, getSubscription, subscribe, POST`, `register('/sw.js')`, `userVisibleOnly:true`·키 바이트 [1,2,3], POST 본문 `{endpoint, keys:{p256dh,auth}, expirationTime:null}` | 통과 · U8-M12 · U8-M14 · U8-M16 · U8-V3 |
| push.test.ts::이미 구독돼 있으면 "already" — 구독도 서버 저장(POST)도 하지 않는다 | 이미 구독 | 기존 구독 있음 → `'already'`, `subscribe` 0, POST 0 | 통과 · U8-M10 |
| push.test.ts::권한이 허용되지 않으면 "denied" — 등록·공개키·구독이 없다 | 권한 거부 | 권한 denied → `'denied'`, `register`·`subscribe` 0, fetch 0 | 통과 · U8-M13 |
| push.test.ts::404 push_not_configured 면 "not_configured" — 구독·저장 없이 멈춘다 | 판정 23 서버 미설정 | 공개키 404 `push_not_configured` → `'not_configured'`, `getSubscription`·`subscribe` 0, fetch 1회 | 통과 · U8-M11 |
| push.test.ts::다른 404(코드가 다름)나 5xx 는 "not_configured" 가 아니라 "failed" | 코드까지 확인 | 404 `not_found` · 500 `push_not_configured` → `'failed'` | 통과 · — |
| push.test.ts::구독 실패·서버 저장 실패는 "failed" | 실패 결과 | `subscribe` 거부 / POST 500 → `'failed'` | 통과 · — |
| push.test.ts::서버 저장(POST)이 실패하면 브라우저 구독을 unsubscribe 1회로 되돌리고 "failed" — 404 push_not_configured 도 같다 | 저장 실패 시 되돌리기 | POST 500 · POST 404 → `'failed'`, `unsubscribe` 정확히 1회 | 통과 · U8-M31 |
| push.test.ts::저장 실패 뒤 다음 클릭은 처음부터 다시 — subscribe 재호출·POST 재시도(이번엔 성공) | "이미 켜짐"으로 남지 않음 | 1회째 POST 500 → `'failed'`, 2회째 → `'subscribed'`, `subscribe` 2회·POST 2회 | 통과 · U8-M31 |
| push.test.ts::unsubscribe 자체가 실패해도 예외 없이 "failed" | 되돌리기 실패 삼킴 | POST 500 + `unsubscribe` 거부 → `'failed'`(예외 없음), `unsubscribe` 1회 | 통과 · U8-M31 |
| push.test.ts::미지원 브라우저(serviceWorker·PushManager·Notification 없음)면 "unsupported" — 네트워크 0 | 미지원 | jsdom 기본 → `'unsupported'`, fetch 0 | 통과 · — |
| push.test.ts::미지원 · 구독 없음 · 구독 있음을 가른다(권한 창·네트워크 없음) | `getPushStatus` 3상태 | 미지원 → `unsupported` / 가짜 브라우저 구독 없음 → `unsubscribed` / 있음 → `subscribed`, 권한 요청·등록 0 | 통과 · — |
| push.test.ts::미구독 → 진행 중(비활성) → 켜짐(비활성) 세 상태 | 판정 23 버튼 상태 | "알림 받기"(활성) 클릭 → "알림 켜는 중"(비활성, POST 나간 뒤에도 유지) → POST 완료 → "알림 켜짐"(비활성), "알림 받기" 없음 | 통과 · U8-M18 |
| push.test.ts::들어올 때 이미 구독돼 있으면 곧바로 "알림 켜짐"(비활성) — 클릭 없이, 서버 저장 없이 | 진입 시 상태 | 기존 구독 → 곧바로 "알림 켜짐" 비활성, POST 0 | 통과 · U8-M17 · U8-M18 |
| push.test.ts::안내 한 줄: 권한 거부 · 서버 미설정 · 미지원 · 실패 — 버튼은 다시 "알림 받기"(활성) | 판정 23 안내 문구 4종 | 권한 denied / 공개키 404 push_not_configured / 공개키 500 / 미지원 → 각각 `push-note` 에 대응 안내, 버튼 다시 활성 | 통과 · U8-M11 · U8-M13 |
| push.test.ts::/push-dev/ 링크가 없다 | 개발용 페이지 링크 금지 | 브리핑 화면 → `a[href*="push-dev"]` 0 | 통과 · — |
| push.test.ts::{type:"briefing", schedule_id} 를 받으면 한 줄 배너 — 누르면 #/briefings?schedule_id=N, 누른 뒤 사라진다 | 결정 H 인앱 배너 | 워커 메시지 `{briefing, 9}` → 배너 문구 "새 브리핑 알림이 도착했어요." + 링크 `#/briefings?schedule_id=9` → 클릭 → 해시 이동·배너 사라짐 | 통과 · U8-M21 |
| push.test.ts::닫기 버튼으로 닫는다(주소는 그대로) | 배너 닫기 | `{briefing, 3}` → "닫기" → 배너 없음, 해시 `#/briefings` 그대로 | 통과 · U8-M23 |
| push.test.ts::schedule_id 가 없으면 일정 없는 브리핑 주소, 모양이 다른 메시지는 무시한다 | 메시지 모양 검증 | `{type:'other'}`·`'briefing'`·null → 배너 0 / `{briefing, null}` → 배너 링크 `#/briefings` | 통과 · — |
| push.test.ts::알림을 눌러 온 {type:"open-briefing"} 은 배너 없이 바로 그 일정 주소로 간다 | 판정 22 알림 클릭 → 그 일정 | `#/chat` 에서 `{open-briefing, 12}` → 해시 `#/briefings?schedule_id=12`, 배너 없음 | 통과 · U8-M21 · U8-M22 |
| push.test.ts::알림을 눌러 온 {type:"open-briefing", schedule_id:null} 은 배너 없이 일정 없는 #/briefings 로 간다 (R-U8-1) | **R-U8-1 (신규)** — null 경계 | `#/chat` 에서 `{open-briefing, null}` → 해시 `#/briefings`, 배너 없음 | 통과 · U9-X3 |

## web/src/__tests__/network.test.ts — 실 네트워크 0 (판정 27b행, 신규 2건)

실행: `cd web && npm test -- --run src/__tests__/network.test.ts` → 2 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt`. 모든 테스트가 기대는 `src/test-setup.ts` 의 가짜 `fetch`(불리면 실패)가 살아 있는지 직접 시험한다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| network.test.ts::표에 없는 바깥 주소 fetch("https://example.invalid") 는 실패한다 | 바깥 주소 요청 차단 | `fetch('https://example.invalid')` → reject, 메시지 "실제 네트워크 요청은 허용되지 않는다" | 통과 · U9-X4 |
| network.test.ts::가짜 표 없이 앱 API 를 부르면(apiFetch → /api/persons) 응답 대신 실패한다 | 앱 API 도 가짜 표 없이는 실패 | 가짜 없이 `apiFetch('/persons')` → 같은 메시지로 reject | 통과 · U9-X4 |

---

## E2E (Playwright) — web/e2e (3 파일, 4건, 판정 24~26행·27b행)

실행: `cd web && npm run e2e` (= `playwright test`; 설정이 `npm run build && npm run preview -- --port 4173 --strictPort` 를 띄운다 — 현재 소스의 빌드 산출물이 대상) → `4 passed` · 증거 `evidence/20261015-1409-u9-final-judge.txt`. 브라우저: Chromium(Chrome Headless Shell 156.0.8078.4, Playwright 1.64.0). 규칙(`e2e/fixtures.ts`): `/api/` 요청은 전부 가짜 표가 답하고 표에 없으면 중단·기록, 이 호스트 밖 요청은 전부 중단, 시계 고정. **각 테스트는 끝에서 모은 요청 URL 전부가 "preview 호스트의 앱 파일 또는 `/api/` 경로" 이고 표 밖 요청이 0 임을 단언한다(27b).**

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 |
|---|---|---|---|
| e2e/chat.spec.ts::발화를 보내면 칩이 뜨고, 눌러 재개된 reply 가 보이며, 새로고침하면 남은 질문 칩이 복원된다 | 판정 24 채팅 칩 + 27b | 발화 "어제 민지랑 점심 먹었어" Enter → reply + 칩 `직장·친구·아니요` / "친구" 클릭 → 재개 reply "친구로 기록했어요.", 눌린 칩 `aria-pressed=true`·나머지 비활성, 새 칩 `예·나중에`(질문 8) / **새로고침** → 화면 메모리는 지워지고 `GET /api/questions/pending` 으로 질문 8 칩만 복원 / "예" 클릭 → "일정으로 저장했어요." / 요청: `/api/chat` 본문 `{utterance}`·헤더 없음, `/api/answers/7` 본문 `{answer:'친구'}`·`X-Session-Id: s-1`, `/api/answers/8` `{answer:'예'}`, 새로고침 뒤 복원 요청에도 `s-1` | 통과 · U9-X5 · U9-X6 · U9-X7 · U9-X15 · U9-X16 |
| e2e/card.spec.ts::데스크톱 폭 1280px › 사이드바 인물 목록에서 인물을 눌러 카드를 열고 타임라인 원문을 펼친다 | 판정 25 데스크톱 + 27b | 1280px: 사이드바 항상 보임·"메뉴 열기" 없음 / 사이드바 인물 "김팀장" 클릭 → `#/persons/3`, 본문에 그 카드 / 타임라인 "원문 펼치기" → 원문 표시(`textContent` 완전 일치 — 줄바꿈·이모지 포함 글자 그대로. `toHaveText` 는 공백을 정규화해 R-U9a-1 로 바꿈), `GET /api/events/31/raw` 1회 / 사이드바 항목 채팅·인물·브리핑 클릭 → 각 화면(`data-screen`)·주소·`aria-current` 전환 / 사이드바 링크 5개(항목 3 + 인물 2) | 통과 · U9-X8 · U9-X10 · U9-X15 · U9-X16 · U9-V2(원문 `\n`→공백: 수정 전 E2E 생존, 수정 후 1 failed — `evidence/20261015-1435-u9a-rework-v2-mutation.txt`) |
| e2e/card.spec.ts::모바일 폭 390px › 서랍은 처음엔 닫혀 있고 하단 탭바가 없다. 메뉴 버튼 -> 인물 -> 인물 -> 카드, 항목을 고르면 서랍이 닫힌다 | 판정 25 모바일 + 27b | 390px: 처음엔 `navigation` 0·`tablist` 0, "메뉴 열기" 보임 / 메뉴 → 서랍 열림 → "인물" → 서랍 닫힘·인물 화면·`#/persons` / 다시 열어 서랍 안 "김팀장" → 서랍 닫힘·`#/persons/3`·카드 / 서랍을 열고 Esc 로 닫아도 주소 그대로 `#/persons/3`(라우트 3경로 그대로), 끝까지 탭바 0 | 통과 · U9-X9 · U9-X11 · U9-X15 · U9-X16 |
| e2e/briefing.spec.ts::쿼리의 일정이 맨 위에 강조돼 열리고, 지금 브리핑을 누르면 목록이 다시 읽힌다 | 판정 26 브리핑 + 27b | `#/briefings?schedule_id=7` 직접 열기, 서버 순서 [9, 7] → 목록 7(맨 위, `data-highlight=true`)·9(강조 없음), 머리줄에 `김팀장 · 주간 회의` / 7 의 "지금 브리핑" → POST `/api/briefings/run` 본문 `{schedule_id:7}` 1회 → 목록 다시 읽기(`GET /api/briefings` 총 2회) → 7 의 줄이 새 문장으로 갱신, 7 이 계속 맨 위 | 통과 · U9-X12 · U9-X13 · U9-X14 · U9-X15 · U9-X16 |

---

## 백엔드 (U9b 가 채움)

(backend-agent U9b 가 이 자리에 pytest 절을 채운다 — 같은 열 형식, 실행 명령·통과 수·증거 경로를 절 머리에 적는다.)
