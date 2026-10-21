# P8-frontend 테스트 기록 — 무엇을 어떻게 시험했나

> 사용자 지시(2026-10-15): "테스트마다 어떤 테스트를 했는지 기록해주세요." 테스트 1건 = 표 1줄.
> 열: `파일::테스트 이름` | 무엇을 확인하나 | 입력 → 기대 | 결과(마지막 실행 결과 + 그 테스트를 실패시킨 변이 ID) | 실패 이력(개발 중 실제로 실패·보류·재작업된 기록 + 출처. 없으면 "기록 없음").
> 작성: 프론트·E2E 절은 U9a(frontend-agent, 2026-10-15), 백엔드 절·"실패 이력" 열은 U9b(backend-agent, 2026-10-15) — 테스트 코드를 읽고 썼다(이름만 보고 짐작하지 않았다). `it.each` 는 경우마다 1줄.
> 자동 테스트는 실제 네트워크·실제 LLM·실제 푸시 서비스를 쓰지 않는다(결정 J). API 는 가짜 응답, 시간은 고정.
> 교수 피드백(2026-10-15 발표): "어떤 테스트로 신뢰성을 올리고 어떤 테스트를 통과하고 실패한 건지 분명하게 드러내야 한다" → 이 표가 그 근거 중 "테스트 단위" 절반이고, 위험 단위의 정리는 `docs/reliability.md`.

## 총계와 세는 법

| 구분 | 파일 | 건수 | 세는 명령 |
|------|------|------|----------|
| 프론트 단위(Vitest) | 9 | **135** | `cd web && npm test -- --run --reporter=verbose` 출력에서 `grep -c " ✓ src/__tests__" <출력 파일>` → 135 (요약 줄 `Test Files  9 passed (9)` · `Tests  135 passed (135)`). 목록만: `cd web && npx vitest list` |
| E2E(Playwright) | 3 | **4** | `cd web && npx playwright test --list` → `Total: 4 tests in 3 files` |
| 백엔드(pytest) | 5 | **64** | `POSTGRES_PORT=5433 .venv/bin/python -m pytest --collect-only -q tests/test_api_read_persons.py tests/test_api_read_raw.py tests/test_api_questions_pending.py tests/test_api_read_briefings.py tests/test_api_read_briefings_e2e.py` → `64 tests collected` (증거 `evidence/20261015-1525-u9-be-collect.txt`). 이 표의 백엔드 행 64줄과 일치 |

- Vitest 파일별 건수: api 6 · proxy 6 · routes 14 · chat 22 · card 29 · briefing 19 · sw 16 · push 21 · network 2 = 135 (U8 시점 130 → sw +2 · push +1 · network +2).
- 백엔드 파일별 건수: persons 12 · raw 18 · questions_pending 8 · briefings 24 · briefings_e2e 2 = 64 (U1~U3 시점 60 → U9b 신규 4: briefings +2(`조작된 trace`·`헬퍼 push_subscriptions`) · briefings_e2e +2(판정표 9·10행)).
- 합계 **203건** (135 + 4 + 64). 이 숫자는 프로젝트 전체 pytest 1946건(`evidence/20261015-1524-u9-be-full-regression.txt`)의 일부이며 P8-frontend 가 새로 만들거나 고친 테스트만 센 것이다.
- 증거: Vitest 전체 verbose `evidence/20261015-1410-u9-vitest-verbose.txt` · 파일별 판정 `evidence/20261015-1410-u9-front-rows.txt` · 전체 판정(`npm ci` → typecheck → test → build → e2e) `evidence/20261015-1409-u9-final-judge.txt` · E2E 목록 `evidence/20261015-1411-u9-e2e-list.txt` · 백엔드 행별 판정 `evidence/20261015-1521~1522-u9-be-rows-*`·`-u9-be-row-*` · 백엔드 변이 `evidence/20261015-1523-u9-be-mutation.txt`.
- 이 표의 첫 열은 verbose 출력의 `파일 > 묶음 > 테스트 이름` 에서 파일과 맨 끝 테스트 이름이다. 같은 이름을 표와 출력에서 기계로 대조한 결과는 03-log U9 에 적는다.

### 결과 열 읽는 법

`통과` 는 마지막 실행(프론트 2026-10-15 14:09~14:10, 백엔드 2026-10-15 15:22~15:24, 위 증거)의 결과다. 뒤의 `U5-M3` 같은 표기는 **그 변이를 넣었을 때 이 테스트가 실패해 변이를 검출했다**는 뜻이고 `—` 는 근거가 되는 변이 증거가 없다는 뜻이다(없다고 약하다는 말은 아니다). 변이 ID 는 단위 접두사 + 그 단위 증거 안의 번호다.

| 접두사 | 변이를 돌린 사람 | 증거 파일(`evidence/`) |
|--------|----------------|----------------------|
| `U1-V*` | verifier (review-u1 "변이 1~7" = V1~V7) | `20261011-verifier-u1-mutation.txt` · `20261011-verifier-u1-recheck-mutation.txt` |
| `U2-M*` | verifier (review-u2 4절 M1~M8) | `20261011-1529-verifier-u2-mutation.txt` |
| `U3-M*` | backend-agent (구현자 24종) | `20261012-1800-u3-mutation.txt` (발췌본 — 스크립트가 FAILED·요약 줄만 추림, review-u3 6절 R-U3-3) |
| `U3-V*` | verifier | `20261012-1733-verifier-u3-mutation.txt` |
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
| `U9b-M*` | backend-agent (이번 단위, 저장소 밖 사본에서 한 곳만 치환) | `20261015-1523-u9-be-mutation.txt` (옛 U1/U2 테스트로 같은 변이를 돌린 대조 `20261015-1523-u9-be-mutation-old-tests.txt`) |

표의 변이 ID 는 증거 파일의 "× 실패한 테스트 이름" 줄을 **현재 테스트 이름**과 맞춰 뽑았다. 이후 이름이 바뀐 테스트(예: `proxy.test.ts` 의 `/api 프록시가 …` 는 U5 에서 단언을 순수 함수로 바꾸며 이름이 달라짐)는 현재 이름으로 확인되지 않아 `—` 로 두었다. 변이 시험에서 DOM 덤프가 없어진 단위(U6 implementer)는 테스트 이름이 증거에 남은 변이만 적었다. 백엔드 `U3-V*` 중 V8(응답 모델에서 `kind` 누락 — pending 테스트 6건 실패)은 실패한 테스트 이름이 증거에 남지 않아 표에 올리지 않았고, `U3-M22`(라우트가 실시계 사용 — 12건 실패)도 같다.

### 실패 이력 열 읽는 법 (U9b 신설 — 사용자 결정 2026-10-15, 교수 피드백)

개발 중 **그 테스트가 실제로 겪은 일**을 기록과 출처로만 적는다. 기록에서 찾지 못하면 "기록 없음"이다 — 추측으로 채우지 않았다. 출처 경로는 이 패키지 폴더(`docs/wiki/packages/P8-frontend/`) 기준이다. 표기는 네 가지다.

| 표기 | 뜻 |
|------|-----|
| **실제 실패** | 개발 중 그 테스트(또는 그 테스트의 전신인 verifier 탐침)가 빨간불이 된 기록 |
| **검출 실패 → 보강** | verifier 가 코드를 망가뜨렸는데(변이) 그때의 테스트가 통과해 버린 것. 테스트가 약했다는 뜻이며 그 뒤 이 테스트를 새로 쓰거나 단언을 고쳤다 |
| **보류·재작업** | verifier 1차 판정이 "보류"였거나 사용자 결정으로 구현이 바뀐 것과 이 테스트가 묶인 경우 |
| **동작 틈 → 보강** | 테스트가 빨개진 것은 아니지만 verifier 실측에서 코드 동작이 이 테스트가 요구하는 값과 달랐던 경우 |
| **기록 없음** | 위 넷 중 어느 것도 기록에서 찾지 못함 |

CI 에서 P8 테스트가 실패한 기록은 없다(U0 CI 의 windows 멈춤은 하네스 자가 점검 `test-guards` 문제였고 FIX-031 로 고쳤다 — 이 표의 테스트가 아니다). 표 앞에서 합계한 **실패 이력이 기록된 행**은 아래 "실패 이력 집계"에 있다.

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

### 이번 단위(U9b)에서 돌린 변이 U9b-M1~M9 (백엔드, 저장소 밖 사본 `/tmp/rel-u9b-mut` 에서 한 곳만 치환)

| ID | 무엇을 망가뜨렸나 | 결과 | 검출한 테스트 |
|----|------------------|------|--------------|
| M1 | R-U3-1: `GET /questions/pending` 의 `replace(ctx, now=now)` 에서 `now=now` 제거(실제 시계가 쓰임) | 6 failed | `questions_pending` 의 `필드_5개`·`created_at_오름차순`·`다른_세션`·`답변된`·`만료_경계`·`쓰기_0` |
| M2 | R-U3-2: 목록 조인에서 `Person.id == Schedule.person_id` 제거 | 1 failed | `briefings::조작된_trace_…` |
| M3 | R-U3-5 ②: `_COUNTED_MODELS` 에서 `PushSubscription` 제거 | 1 failed | `briefings::헬퍼_자체_push_subscriptions_…` (9테이블 단언) |
| M4a | `list_persons` 가 `Person` 을 UPDATE(`onupdate` 로 `updated_at` 변경) | 1 failed | `persons::쓰기_0_trace_0` |
| M4b | `get_person_card` 가 `Schedule.briefed_at` 을 UPDATE | 1 failed | `persons::쓰기_0_trace_0` |
| M4c | `get_event_raw` 가 `Person` 을 UPDATE | 1 failed | `raw::쓰기_0_trace_0` |
| M4d | `get_fact_sources` 가 `Schedule.briefed_at` 을 UPDATE | 1 failed | `raw::쓰기_0_trace_0` |
| M4e | `get_person_card` 가 `push_subscriptions` 에 INSERT | 1 failed | `persons::쓰기_0_trace_0` (1차 시도는 unique 위반 오류로 실패해 무효 — 호출마다 다른 endpoint 로 재실행한 것이 유효, 증거에 둘 다 있음) |
| M5 | 9행: `POST /briefings/run` 이 `trigger="scheduler"` 로 실행 | 1 failed | `briefings_e2e::test_9행_…` |
| M6 | 10행: 조회에서 `briefing_compose` step 필터 제거 | 1 failed | `briefings_e2e::test_10행_…` |
| M7 | 10행: 일정마다 최근 1행(`rn == 1`) 제거 | 1 failed | `briefings_e2e::test_10행_…` |
| M8 | 10행: 목록 쿼리의 `Person.user_id` 격리 제거 | 1 failed | `briefings_e2e::test_10행_…` |
| M9 | 10행: 최근 1행 정렬 2차 키 `AgentTrace.id.desc()` → `asc()` | 1 failed | `briefings_e2e::test_10행_…` |

옛 U1·U2 쓰기 0 테스트(행 수 7테이블만 비교)로 같은 M4a~M4e 를 돌리면 **5종 전부 살아남는다**(`20261015-1523-u9-be-mutation-old-tests.txt` — 전부 `12 passed`/`18 passed`). 그래서 R-U3-5 ①(값까지 보는 공통 헬퍼로 교체)이 필요했다.

---

## web/src/__tests__/api.test.ts — API 클라이언트 래퍼 (6건)

실행: `cd web && npm test -- --run src/__tests__/api.test.ts` · 증거 `evidence/20261015-1410-u9-vitest-verbose.txt` (파일별 통과 수는 `…-u9-front-rows.txt` 에 없음 — api·proxy 는 전체 verbose 로 확인).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| api.test.ts::기본 경로는 /api 이고 GET 은 본문·Content-Type 이 없다 | 요청 주소 접두와 GET 모양 | `apiFetch('/persons')` → fetch URL `/api/persons`, method `GET`, body 없음, headers `{}` | 통과 · U4-M4 | 기록 없음 |
| api.test.ts::POST 는 JSON 본문과 X-Session-Id 헤더를 보낸다 | POST 본문 직렬화·세션 헤더 이름 | `apiFetch('/chat',{method:'POST',body:{utterance:'안녕'},sessionId:'abc-1'})` → body `{"utterance":"안녕"}`, headers `Content-Type`+`X-Session-Id: abc-1` | 통과 · U4-M4 · U4-M6 | 기록 없음 |
| api.test.ts::sessionId 가 null 이면 헤더를 넣지 않는다 | 세션을 일부러 비울 때 | `sessionId: null` → headers `{}` | 통과 · — | 기록 없음 |
| api.test.ts::P5 오류 규약 {"detail":{"code"}} 를 ApiError 로 올린다 | 오류 본문 → `ApiError(status, code)` | 409 `{detail:{code:'already_answered'}}` → `ApiError`, status 409, code `already_answered` | 통과 · U4-V2 | 기록 없음 |
| api.test.ts::규약 밖 본문(422 검증 목록, 비-JSON 5xx)은 code 가 null | 규약 밖 오류 본문 | 422 `{detail:[{msg}]}` · 500 `boom` → 둘 다 `code === null`, status 유지 | 통과 · U4-V2 | 기록 없음 |
| api.test.ts::테스트 환경의 기본 fetch 는 실제 네트워크를 쓰지 않고 실패한다 (결정 J) | setup 의 안전망이 켜져 있다 | 가짜 없이 `apiFetch('/persons')` → "실제 네트워크" 메시지로 reject | 통과 · U4-V3 · U9-X4 | 기록 없음 |

## web/src/__tests__/proxy.test.ts — 개발 서버 프록시 (6건)

실행: `cd web && npm test -- --run src/__tests__/proxy.test.ts`.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| proxy.test.ts::환경 변수가 없거나 비면 기본값 | 프록시 대상 기본값 | `resolveApiTarget({})` · `{VITE_API_TARGET:''}` → `http://localhost:8000` (`DEFAULT_API_TARGET` 도 같은 값) | 통과 · — | 기록 없음 |
| proxy.test.ts::VITE_API_TARGET 이 있으면 그 값 | 환경 변수 우선 | `{VITE_API_TARGET:'http://x:9'}` → `http://x:9` | 통과 · U5-M12 | 기록 없음 |
| proxy.test.ts::/api 프록시가 stripApiPrefix 로 접두를 벗긴다 | `vite.config.ts` 의 `/api` 규칙이 `stripApiPrefix` 로 연결돼 있다 | 설정 함수 호출 → `server.proxy['/api'].rewrite === stripApiPrefix`, `rewrite('/api/persons/3') === '/persons/3'` | 통과 · — (앞 판 이름의 같은 단언이 U4-R1·R2·V1 에 검출됨, 현재 이름으로는 미확인) | **검출 실패 → 보강**: U4 verifier 변이 V1(프록시 `rewrite` 삭제)이 1차 테스트 20건을 통과(R-U4-3). 재작업 2차에서 `proxy.test.ts` 4건(이 행 포함)을 더함 · `review-u4-skeleton.md` 99·125행 · `03-log.md` 69·76행 |
| proxy.test.ts::/api 접두를 벗긴다 | 접두 제거 값 | `/api/persons/3`→`/persons/3`, `/api/chat`→`/chat`, `/api/briefings?schedule_id=4` → 쿼리 유지 | 통과 · U4-R2 | **검출 실패 → 보강**: 위 행과 같음(재작업 2차에서 신설) |
| proxy.test.ts::/api 만 오면 루트 / | 경계: 접두만 | `/api`→`/`, `/api?x=1`→`/?x=1` | 통과 · U4-R2 | **검출 실패 → 보강**: 위 행과 같음(재작업 2차에서 신설) |
| proxy.test.ts::/api 로 시작하지 않는 경로는 그대로 (접두가 비슷한 /apix 포함) | 비슷한 접두를 건드리지 않음 | `/other`·`/apix/persons`·`/x/api/persons` → 그대로 | 통과 · — | **검출 실패 → 보강**: 위 행과 같음(재작업 2차에서 신설) |

## web/src/__tests__/routes.test.tsx — 해시 라우팅·앱 틀(사이드바) (14건)

실행: `cd web && npm test -- --run src/__tests__/routes.test.tsx` → 14 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 13행). 가짜 `matchMedia`(`helpers.ts`)로 폭을 바꾼다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| routes.test.tsx::#/chat 는 chat 빈 화면을 그린다 | 해시 → 화면 하나 (it.each 1/3) | `#/chat` 렌더 → `[data-screen]` 1개 = `chat`, h1 "채팅" | 통과 · — | 기록 없음 |
| routes.test.tsx::#/persons 는 persons 빈 화면을 그린다 | (it.each 2/3) | `#/persons` → `data-screen=persons`, h1 "인물" | 통과 · — | 기록 없음 |
| routes.test.tsx::#/briefings 는 briefings 빈 화면을 그린다 | (it.each 3/3) | `#/briefings` → `data-screen=briefings`, h1 "브리핑" | 통과 · — | 기록 없음 |
| routes.test.tsx::#/persons/:id 는 인물 화면에 id 를 넘긴다 | id 를 화면이 받는다 | `#/persons/12` → `data-person-id="12"` | 통과 · — | 기록 없음 |
| routes.test.tsx::알 수 없는 해시는 #/chat 으로 보낸다 | 화면 3개 고정(원칙5) — 모르는 주소는 채팅 | `#/nope` → chat 화면 + 주소가 `#/chat` 으로 바뀜 | 통과 · U4-M1 · U4-V4 | 기록 없음 |
| routes.test.tsx::해시가 비어 있어도 #/chat 으로 보낸다 | 해시 없음 | `/` → chat 화면 + `#/chat` | 통과 · U4-M1 · U4-V4 | 기록 없음 |
| routes.test.tsx::parseHash 경계: 숫자가 아닌 id·끝 슬래시·쿼리 | 라우트 표 경계 | `#/persons/abc`·`#/persons/`·`#/chat/extra` → null / `#/briefings?schedule_id=3` → briefings / `#/persons/7` → id 7 / `#/persons` → id null | 통과 · U4-M5 · U4-V5 | 기록 없음 |
| routes.test.tsx::데스크톱 폭에서는 사이드바가 항상 보이고 메뉴 버튼이 없다 | 결정 N 데스크톱 | 1280px → 사이드바 링크 3개 `[채팅 #/chat, 인물 #/persons, 브리핑 #/briefings]`, "메뉴 열기" 없음, 인물 목록 자리 있음 | 통과 · U4-M8 | 기록 없음 |
| routes.test.tsx::지금 화면 항목에 aria-current 가 붙는다 | 현재 화면 표시 | `#/briefings` → 브리핑 링크 `aria-current=page`, 채팅 링크엔 없음 | 통과 · — | 기록 없음 |
| routes.test.tsx::좁은 폭: 기본은 접혀 있고 메뉴 버튼으로 열린다 | 모바일 서랍 열기 | 800px → 사이드바 없음, "메뉴 열기" 클릭 → 사이드바 보임 | 통과 · — | **보류·재작업**: U4 verifier 1차 보류(R-U4-1) — 서랍을 기성 `Sheet` 가 아니라 `div`+`aside` 로 직접 구현해 계획 위반(테스트 자체는 실패하지 않음). 재작업 2차에서 `Sheet` 로 교체, 교체 뒤 U4 24건 통과 · `review-u4-skeleton.md` 4행 · `03-log.md` 67·69행 |
| routes.test.tsx::좁은 폭: 항목을 고르면 서랍이 닫히고 그 화면이 보인다 | 항목 선택 시 닫힘 | 서랍 열고 "브리핑" 클릭 → 사이드바 사라짐 + briefings 화면 | 통과 · U4-M3 · U4-M8 | **보류·재작업**: 위 행과 같음(R-U4-1 서랍 교체) |
| routes.test.tsx::좁은 폭: Esc 와 바깥(배경) 클릭으로도 닫힌다 | 서랍 닫는 두 방법 | Esc → 닫힘 / 다시 열고 `sheet-overlay` 클릭 → 닫힘 | 통과 · U4-M7 | **보류·재작업**: 위 행과 같음(R-U4-1 서랍 교체) |
| routes.test.tsx::열림/닫힘은 라우트도 localStorage 도 바꾸지 않는다 | 서랍 상태는 레이아웃 상태일 뿐 | `#/persons` 에서 서랍 열기 → 해시 그대로, `localStorage.length === 0` | 통과 · U4-M9 | **보류·재작업**: 위 행과 같음(R-U4-1 서랍 교체) |
| routes.test.tsx::1024px 경계: 1023 은 서랍형, 1024 는 고정 사이드바 | 결정 N 기준 폭 | 1023px → "메뉴 열기" 있음 / 1024px → 없음 + 사이드바 | 통과 · U4-M2 | 기록 없음 |

## web/src/__tests__/chat.test.tsx — 채팅 화면·확인 칩 (22건)

실행: `cd web && npm test -- --run src/__tests__/chat.test.tsx` → 22 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 14~17b행). 가짜 `fetch` 라우터로 `/api/chat`·`/api/answers/{id}`·`/api/questions/pending` 에 답한다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| chat.test.tsx::발화를 POST /api/chat 으로 보내고 내 말풍선과 reply 를 보여 준다 | 전송 흐름·서버 문장 그대로 | "민수랑 점심 먹었어" 입력·전송 → POST `/api/chat` 본문 `{utterance}`, 내 말풍선 `data-role=user`, 서버 `reply` 그대로 | 통과 · — | 기록 없음 |
| chat.test.tsx::첫 요청에는 X-Session-Id 가 없고, 응답 session_id 를 저장해 두 번째 요청에 보낸다 | 판정 14 세션 보관 | 첫 전송(헤더 없음) → 응답 `sess-abc` → localStorage 저장 → 두 번째 전송 헤더 `X-Session-Id: sess-abc` | 통과 · U5-M3 · U5-M6 | 기록 없음 |
| chat.test.tsx::저장된 세션이 있으면 진입 시 복원 요청에도 헤더를 보낸다 | 복원 요청도 세션 사용 | localStorage `sess-old` → `GET /api/questions/pending` 1회, 헤더 `sess-old` | 통과 · U5-M3 · U5-V3 | 기록 없음 |
| chat.test.tsx::422 invalid_session_id 면 저장된 세션을 버리고 다음 요청은 헤더 없이 간다 | 서버가 세션을 모를 때 | 422 `invalid_session_id` → 안내 `세션이 초기화됐어요`, localStorage 비움, 다음 전송 헤더 없음 | 통과 · U5-M9 | 기록 없음 |
| chat.test.tsx::Enter 는 전송, Shift+Enter 는 줄바꿈 | 판정 17b 입력 키 | "한 줄 Shift+Enter 두 줄" → 요청 0, 값 `한 줄\n두 줄` / Enter → POST 1회, 본문 줄바꿈 유지 | 통과 · U5-M7 | 기록 없음 |
| chat.test.tsx::빈 입력은 보낼 수 없다 | 빈 전송 방지 | 처음·공백만 입력 → "보내기" 비활성 | 통과 · — | 기록 없음 |
| chat.test.tsx::응답을 기다리는 동안 타이핑 점이 보이고 끝나면 사라진다 | 판정 17b 대기 표시 + R-U5-4 | 응답 보류 중 → 타이핑 점 표시, 새 글자를 써도 "보내기" 비활성 / 응답 도착 → 점 사라짐, 버튼 활성 | 통과 · — | 기록 없음 |
| chat.test.tsx::한글 조합 중(isComposing) Enter 는 전송이 아니다 (R-U5-4) | 한글 입력 조합 중 Enter | `keyDown Enter isComposing:true` → POST 0 | 통과 · — | 기록 없음 |
| chat.test.tsx::확인 칩이 떠 있어도 입력은 막히지 않는다 (결정 E) | 판정 16 새 발화 우선 | 칩이 뜬 상태 → 입력창 활성, 타자 입력됨 | 통과 · — | 기록 없음 |
| chat.test.tsx::칩 글자와 순서가 options 와 같다 (reply 바로 아래) | 판정 15 / 원칙7 — 칩 문자열 가공 없음 | 가나다 순이 아니고 앞뒤 공백이 든 options 3개 → 칩 `textContent` 가 그대로·같은 순서, 칩 묶음이 그 reply 말풍선 안 | 통과 · U5-M1 · U5-M10 · U6-M10 | **검출 실패 → 보강**: U5 verifier 변이 V1(`options` 에 trim 주입)이 1차 테스트를 통과(R-U5-1). 테스트 데이터를 비정렬+앞뒤 공백 문자열로 바꿔 검출됨 · `review-u5-chat.md` 4·107행 · `03-log.md` 96행 |
| chat.test.tsx::칩을 누르면 POST /api/answers/{id} 에 그 문자열이 {answer} 로 가고, 선택 고정·나머지 비활성 | 판정 15 칩 클릭 | 두 번째 칩 클릭 → POST `/api/answers/7` 본문 `{answer: 그 문자열}` 1회, 누른 칩 `aria-pressed=true`, 나머지 `false` + 비활성 | 통과 · U5-M2 · U5-M8 · U5-M11 · U6-M10 | 기록 없음 |
| chat.test.tsx::답 응답의 reply 가 이어 붙고, 새 pending_question 이면 그 아래 새 칩 | 판정 15 재개 | "예" 클릭 → 응답 `reply` 가 이어 붙고 `chips-8` 3개(오늘·내일·모레)가 그 말풍선 안, 앞 칩은 고정 | 통과 · U5-M1 · U5-M10 · U5-M11 · U5-V2 · U6-M10 | 기록 없음 |
| chat.test.tsx::진입 시 GET /api/questions/pending 으로 미답변 전부를 질문별로 복원한다 | 판정 16 복원 | 미답변 2건 → 질문 글과 칩 묶음 2개(`chips-3`·`chips-4`) 복원, 요청 1회 | 통과 · U5-M1 · U5-M10 | 기록 없음 |
| chat.test.tsx::답할 때 409 already_answered 면 그 질문 칩을 모두 비활성으로 두고 한 줄 안내 | 판정 17 (it.each 1/2) | 칩 클릭 → 409 → 그 질문 칩 전부 비활성, 안내 "이미 답했거나 만료된 질문이에요.", 다른 질문 칩은 활성, 재시도 없음(요청 1회) | 통과 · U5-M4 · U5-M10 · U5-M11 · U5-M13 | 기록 없음 |
| chat.test.tsx::답할 때 409 expired 면 그 질문 칩을 모두 비활성으로 두고 한 줄 안내 | (it.each 2/2) 코드가 달라도 같은 처리 | 위와 같고 코드 `expired` | 통과 · U5-M4 · U5-M10 · U5-M11 · U5-M13 · U5-V4 | 기록 없음 |
| chat.test.tsx::답 전송이 5xx 로 실패하면 안내 한 줄을 띄우고 칩은 다시 누를 수 있다 | 일시 오류는 칩을 영구 잠그지 않음 | `/api/answers/3` 500 → 안내 "요청을 처리하지 못했어요…", 칩 활성 | 통과 · U5-V5 | 기록 없음 |
| chat.test.tsx::POST /api/chat 이 5xx 면 안내 한 줄 | 판정 17 오류 | `/api/chat` 500 → 안내 한 줄, 내 말풍선은 남음 | 통과 · — | 기록 없음 |
| chat.test.tsx::네트워크 실패(fetch 거부)면 안내 한 줄 | 전송 중 네트워크 실패 | fetch 가 `TypeError` → 같은 안내 한 줄 | 통과 · — | 기록 없음 |
| chat.test.tsx::진입 시 복원 요청이 실패하면 한 줄 안내가 뜨고 빈 상태 안내도 남는다 (R-U5-2) | 복원 실패 안내 | 복원 fetch 거부 → `alert` "이전에 남은 질문을…" + 빈 상태 안내 유지 | 통과 · — | 기록 없음 |
| chat.test.tsx::stored.persons > 0 이면 #/persons 링크가 붙는다 | 카드 화면 링크 조건 | `stored.persons:1` → 링크 "인물 카드 보기" `href="#/persons"` | 통과 · — | 기록 없음 |
| chat.test.tsx::stored.events > 0 이어도 링크가 붙는다 | 링크 조건(사건) | `stored.events:2` → 링크 있음 | 통과 · — | 기록 없음 |
| chat.test.tsx::저장된 인물·사건이 없으면(일정만 있어도) 링크가 없다 | 링크 조건 경계 | `stored.schedules:3` 만 → 링크 0 | 통과 · U5-M5 | 기록 없음 |

## web/src/__tests__/card.test.tsx — 인물 목록·카드·원문 펼치기 (29건)

실행: `cd web && npm test -- --run src/__tests__/card.test.tsx` → 29 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 18·19행). 날짜는 한낮(UTC 12:00)이라 시간대와 무관하다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| card.test.tsx::서버 순서 그대로(재정렬 없음) 이름·태그·위계·마지막 접촉 4개 필드를 보여 준다 | 목록 순서·필드 | 서버가 박대리·철수·엄마(날짜·이름·id 순 어느 쪽도 아님)로 줌 → 그 순서, 태그 `직장·친구·가족`, 위계 `하·동·상`, 마지막 접촉 `2026. 9. 1.`·`2026. 10. 5.`·"기록 없음" | 통과 · U6-M1 | 기록 없음 |
| card.test.tsx::필터·검색 컨트롤이 없다 | 판정 19 필터 0 | 목록 화면 → textbox·searchbox·combobox 없음 | 통과 · — | 기록 없음 |
| card.test.tsx::빈 목록이면 빈 상태 문구 하나 | 빈 상태 | `[]` → "아직 기록된 인물이 없어요." | 통과 · — | 기록 없음 |
| card.test.tsx::목록 조회가 실패하면 한 줄 안내 | 오류 | 500 → "인물 목록을 불러오지 못했어요." | 통과 · — | 기록 없음 |
| card.test.tsx::항목 링크는 #/persons/:id 이고 누르면 해시가 바뀐다 | 항목 → 카드 이동 | 링크 href `#/persons/7`·`/4`·`/9`, 두 번째 클릭 → `#/persons/4` | 통과 · U6-M1 | **실제 실패**(1회, 테스트 쪽 오류): U6 구현 중 테스트 데이터 1차 수정이 이 테스트의 인덱스를 함께 고치지 않아 `expected '#/persons/9' to be '#/persons/4'` — card.test 22건 중 1 failed, exit 1. 인덱스를 고쳐 통과 · `evidence/20261013-1628-u6-card.txt` · `review-u6-card.md` 4절 끝 |
| card.test.tsx::#/persons 본문과 사이드바에 같은 목록이 같은 순서로 그려진다 | 결정 N — 같은 목록 두 자리 | `#/persons` 앱 렌더 → 사이드바 1·본문 1, `innerHTML` 동일, 링크 글자 3줄 같은 순서 | 통과 · U6-M1 | 기록 없음 |
| card.test.tsx::R-U6-2: 앱을 열면 GET /persons 는 1회(사이드바·본문이 한 번 받은 값을 같이 쓴다) | 중복 조회 방지 | 앱 열기 → `/api/persons` 1회 | 통과 · — | **동작 틈 → 보강**: U6 코드에서는 `GET /persons` 가 2회 나갔다(verifier 실측, 계약 위반은 아님). U7 에서 `PersonsProvider` 단일 조회로 바꾸며 이 테스트를 신설 · `review-u6-card.md` 3절 ③ · `03-log.md` 113·122행 |
| card.test.tsx::R-U6-2: 해시 라우트가 바뀌면 다시 읽어 새 인물이 사이드바에 보인다 | 사이드바 갱신 | 서버 목록에 철수 추가 후 `#/persons` 이동 → 사이드바에 철수, 요청 2회 | 통과 · U7-M17 | **실제 실패**(verifier 탐침, 이 테스트의 전신): U6 코드에서 탐침 P2 가 실패 — 라우트를 옮겨도 데스크톱 사이드바가 옛 목록 그대로(R-U6-2). U7 에서 처방 · `review-u6-card.md` 3절·68행 · `evidence/20261013-1847-verifier-u6-mutation.txt` |
| card.test.tsx::R-U6-2: 채팅 응답 stored.persons > 0 이면 다시 읽고, 0 이면 읽지 않는다 | 새 인물 생기면 목록 갱신 | 채팅 응답 `stored.persons:1` → 사이드바에 철수, `/api/persons` 2회 | 통과 · U7-M18 | **실제 실패**(verifier 탐침, 이 테스트의 전신): 위 행과 같은 탐침 P2 — 새 인물이 생겨도 사이드바가 새로고침 전까지 옛 목록 |
| card.test.tsx::R-U6-2: 채팅 응답 stored.persons 가 0 이면(사건만 저장) 인물 목록을 다시 읽지 않는다 | 갱신 경계 | `stored.events:2`·persons 0 → 50ms 뒤에도 `/api/persons` 1회 | 통과 · U7-M19 | 기록 없음 |
| card.test.tsx::R-U6-2: 알림 이벤트(persons-changed)만으로도 다시 읽는다 | 이벤트 통로 | `notifyPersonsChanged()` → `/api/persons` 2회 | 통과 · — | 기록 없음 |
| card.test.tsx::R-U7-2 (탐침 P2c): 먼저 보낸 느린 조회가 나중 조회보다 늦게 도착해도 사이드바는 나중 조회 값이다 | 늦게 온 옛 응답 무시 | 1차 조회 보류, 2차 즉시(철수) → 1차 뒤늦게 도착해도 사이드바 = 철수(박대리 없음) | 통과 · U8-M25 | **검출 실패 → 보강**: U7 verifier 변이 V4(늦은 응답 카운터 제거)가 기존 테스트 92건을 통과(R-U7-2). 탐침 P2c 를 이 테스트로 옮김 · `review-u7-briefing.md` 4·95행 |
| card.test.tsx::사이드바와 본문이 같은 컴포넌트(PersonList)를 import 한다 | 같은 컴포넌트 사용(결정 N) | `AppShell.tsx`·`PersonCardScreen.tsx` 소스에 같은 `import PersonList …` 줄 | 통과 · U6-V5 | 기록 없음 |
| card.test.tsx::좁은 폭: 서랍에서 항목을 고르면 서랍이 닫힌다 | 서랍 안 인물 선택 | 800px, 서랍의 "철수" 클릭 → 해시 `#/persons/4`, 서랍 닫힘 | 통과 · — | 기록 없음 |
| card.test.tsx::섹션 7개가 부록 A ② 순서로 놓인다 | 카드 섹션 순서 | `data-section` 순서 `header·aliases·last-contact·facts·patterns·timeline·schedules`, h2 `김팀장`·▸알고 있는 것·▸반복 패턴·▸타임라인·▸다가오는 일정 | 통과 · U6-V2 | 기록 없음 |
| card.test.tsx::각 섹션의 값이 서버가 준 그대로 나온다 | 판정 19 항목 렌더 | 머리 `김팀장`·`직장 · 상`, `별칭: 팀장, 우리 팀장님, 부장님`, `마지막 접촉: 2026. 9. 3.`, 사실 key/value, 패턴 key/value, 일정 제목·날짜 | 통과 · U6-V2 | 기록 없음 |
| card.test.tsx::타임라인은 서버 순서 그대로, 항목마다 날짜·type·content | 타임라인 순서 | 서버 순서 5·9·2(날짜순 아님) → `timeline-5`,`-9`,`-2`, 첫 항목에 `2026. 8. 21.`·`meal`·`점심 같이 함` | 통과 · U6-M6 | 기록 없음 |
| card.test.tsx::source_count 가 0 이면 근거 보기 버튼이 없고, 양수면 있다 | 근거 없는 사실엔 버튼 없음 | 사실 11(2건)·21(3건) 버튼 있음, 사실 12(0건) 버튼 없음 | 통과 · — | 기록 없음 |
| card.test.tsx::비어 있는 섹션은 짧은 빈 문구를 보여 준다 | 빈 상태 문구 | 전부 빈 카드 → `별칭: 없음`, `마지막 접촉: 기록 없음`, 섹션별 빈 문구 4개 | 통과 · U6-V2 | 기록 없음 |
| card.test.tsx::404 면 안내 한 줄과 목록으로 가는 링크 | 판정 K — 없는 인물 | `/api/persons/3` 404 → `alert` "인물을 찾을 수 없어요." + 링크 "인물 목록으로" `#/persons`, 카드 없음 | 통과 · U6-V4 | 기록 없음 |
| card.test.tsx::404 가 아닌 실패는 다른 안내 문장 | 오류 구분 | 500 → "인물 카드를 불러오지 못했어요." | 통과 · U6-V4 | 기록 없음 |
| card.test.tsx::카드·목록 응답에 원문이 없으면 아무 데도 원문이 보이지 않고, 원문 요청도 없다 | 결정 F — 펼치기 전엔 원문 없음 | 카드 렌더 → `raw-utterance` 0, 본문에 원문 글자 없음, 요청은 `/api/persons/3` 하나뿐 | 통과 · — | 기록 없음 |
| card.test.tsx::첫 펼침에 GET /events/{id}/raw 1회, 원문은 글자 그대로, 접었다 다시 펼쳐도 요청은 1회 | 판정 18 | 특수문자·꼬리 공백·연속 개행 든 원문 → 펼침 1회째 GET 1회, `textContent` 동일 / 접기 → 숨김 / 다시 펼침 → 같은 원문, 요청 계속 1회 | 통과 · U6-M3 | 기록 없음 |
| card.test.tsx::다른 항목은 각자 한 번씩 요청한다 | 항목별 캐시 | 항목 9·2 펼침 → 각 `/api/events/{id}/raw` 1회 | 통과 · — | 기록 없음 |
| card.test.tsx::조회 실패는 그 항목 안에만 안내가 뜨고, 다시 누르면 재시도(요청 2회)해 원문이 나온다 | 실패 국소화 | 첫 요청 500 → 그 항목 안 `alert` "원문을 불러오지 못했어요…" 1개뿐, 카드·다른 항목 정상 / 다시 누름 → 요청 2회째 성공 | 통과 · U6-M3 | 기록 없음 |
| card.test.tsx::R-U6-1: 로딩 중 접기 → 요청 실패 → 다시 펼치면 열리고 재시도해 원문이 나온다 | 경합 경계 | 펼침(로딩) → 접음 → 첫 요청 실패 → 다시 펼침 → 열리고 2회째 요청으로 원문 | 통과 · U7-M16 | **실제 실패**(verifier 탐침, 이 테스트의 전신): U6 코드에서 탐침 P3 가 실패 — 접힌 채 실패한 뒤 다시 누르면 요청만 나가고 항목이 열리지 않음(R-U6-1). U7 에서 처방 1줄 뒤 통과 · `review-u6-card.md` 3절·68행 · `evidence/20261013-1847-verifier-u6-mutation.txt` |
| card.test.tsx::근거 보기: sources 요청 1회, 항목 수·날짜·content·원문이 그대로, 접기, 다시 펼쳐도 재요청 없음 | 판정 19 근거 보기 | "근거 보기" → `GET /api/persons/3/facts/11/sources` 1회, 2건(날짜 · content · 원문 동일) / 접기·다시 펼침 → 재요청 없음 | 통과 · U6-V3 | 기록 없음 |
| card.test.tsx::패턴의 근거 보기도 그 패턴 id 로 요청한다 | 패턴도 같은 경로 | 패턴 21 "근거 보기" → `/facts/21/sources` 1회, 원문 표시 | 통과 · — | 기록 없음 |
| card.test.tsx::근거 조회 실패는 그 사실 안에만 안내, 다시 누르면 재시도(요청 2회) | 근거 실패 국소화 | 첫 요청 500 → 그 사실 안 `alert` 1개, 다른 사실엔 없음 / 다시 누름 → 성공, 요청 2회 | 통과 · — | 기록 없음 |

## web/src/__tests__/briefing.test.tsx — 브리핑 화면·수동 브리핑 (19건)

실행: `cd web && npm test -- --run src/__tests__/briefing.test.tsx` → 19 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 20·21행). 서버 순서를 id·이름·시각 어느 쪽으로 다시 줄 세워도 달라지게 골랐다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| briefing.test.tsx::서버 순서 그대로(재정렬 없음), 머리줄은 일정 시각 · 이름 · 일정 제목 | 판정 20 머리줄·순서 | 응답 5·2·9 → `briefing-5`,`-2`,`-9` 순, h2 `📌 <일정 시각> · 김팀장 · 분기 회의` 등 | 통과 · U7-M1 · U7-M9 | 기록 없음 |
| briefing.test.tsx::패턴 문장·요약 줄·제안이 서버 문자열 그대로이고 순서(패턴 → 줄 → 제안)를 지킨다 | 원칙7 — 서버 문장 가공 없음 | 꺾쇠·따옴표·꼬리 공백이 든 문장 → `textContent` 동일, 패턴 → 줄1 → 줄2 순, 제안 h3 "💡 제안" | 통과 · U7-M2 · U7-M3 · U7-M7 | 기록 없음 |
| briefing.test.tsx::basis 는 화면에 나오지 않는다 | 숨김 필드 | `basis` 의 키·id 문자열이 본문에 없음 | 통과 · U7-M2 | 기록 없음 |
| briefing.test.tsx::제안이 없으면 제안 구획이 없다 | 판정 20 `suggestion: null` | 제안 null 항목 → 제안 구획·h3 없음 | 통과 · — | 기록 없음 |
| briefing.test.tsx::빈 목록이면 빈 상태 문구 하나 | 판정 20 빈 상태 | `[]` → "아직 만들어진 브리핑이 없어요.", 목록 없음 | 통과 · U7-M15 | 기록 없음 |
| briefing.test.tsx::목록 조회가 실패하면 한 줄 안내(빈 상태 문구는 아님) | 오류 vs 빈 상태 구분 | 500 → "브리핑을 불러오지 못했어요.", 빈 상태 문구 없음 | 통과 · U7-V5 · U8-M26 | 기록 없음 |
| briefing.test.tsx::항목마다 "지금 브리핑" 버튼이 있고, 알림 받기 버튼이 활성이며 /push-dev/ 링크가 없다 (구독 동작은 push.test.ts) | 버튼 자리·개발 페이지 링크 없음 | 3건 → "지금 브리핑" 3개, "알림 받기" 활성, `a[href*="push-dev"]` 0 | 통과 · — | 기록 없음 |
| briefing.test.tsx::쿼리가 없으면 서버 순서 그대로이고 단건 요청은 0 | 쿼리 없을 때 | `#/briefings` → 요청은 `/api/briefings` 하나뿐, `data-highlight` 없음 | 통과 · — | 기록 없음 |
| briefing.test.tsx::목록 안에 있으면 맨 위로 올리고 강조하며(나머지는 서버 순서) 단건 요청은 0 | 판정 26 단위 대응 — 강조·맨 위 | `?schedule_id=9` → 순서 9·5·2, 9 만 `data-highlight`, 요청 1개, 강조 카드에만 `ring-2` 클래스 | 통과 · U7-M1 · U7-M6 · U7-M8 · U7-M13 · U8-M24 | **검출 실패 → 보강**: U7 verifier 변이 V3(강조의 보이는 스타일 `ring-2` 만 제거, `data-highlight` 유지)가 기존 테스트를 통과(R-U7-2). `ring-2` 단언을 이 테스트에 더함 · `review-u7-briefing.md` 64·95행 |
| briefing.test.tsx::목록에 없으면 GET /briefings?schedule_id=N 을 1회 더 불러 맨 위에 붙이고 강조한다 | 7일 창 밖 일정 | `?schedule_id=77`(목록에 없음) → 요청 `/api/briefings` + `?schedule_id=77` 각 1회, 순서 77·5·2·9, 77 강조 | 통과 · U7-M1 · U7-M8 · U7-M14 · U7-V2 | 기록 없음 |
| briefing.test.tsx::단건이 404 이거나 [] 이면 안내 한 줄 + 나머지 목록 그대로 | 없는 일정 | 단건 404 / `[]` 각각 → "그 일정의 브리핑이 아직 없어요.", 목록 5·2·9, 강조 없음 | 통과 · U7-M1 | 기록 없음 |
| briefing.test.tsx::R-U7-3: 단건 조회가 404 가 아닌 오류로 실패하면 목록 실패 문구가 아니라 "그 일정" 문구 — 목록은 그대로 | 오류 문구 구분 | 단건 500 → `schedule-failed` "그 일정의 브리핑을 불러오지 못했어요.", 목록 실패 문구 없음, 목록 그대로 | 통과 · U8-M20 | 기록 없음 |
| briefing.test.tsx::parseScheduleId: 양의 정수만 인정한다 | 쿼리 파싱 경계 | `=12`→12, 없음/0/abc/1.5 → null, `x=1&schedule_id=3` → 3 | 통과 · U7-M20 | 기록 없음 |
| briefing.test.tsx::POST 본문은 {schedule_id} 이고, 성공하면 응답을 끼우지 않고 GET /briefings 를 다시 읽어 갱신한다 | 판정 21 수동 브리핑 | "지금 브리핑"(일정 2) → POST `/api/briefings/run` 본문 `{schedule_id:2}` 1회 → `GET /api/briefings` 2회째, 새 줄 "새로 만든 줄" 표시, 순서 2·9 | 통과 · U7-M2 · U7-M4 · U7-M12 | 기록 없음 |
| briefing.test.tsx::진행 중에는 그 버튼이 비활성(진행 표시)이고, 끝나면 다시 활성 | 중복 클릭 방지 | POST 보류 중 → 그 항목 "브리핑 만드는 중" 비활성, 다른 항목 버튼은 활성 / 완료 → 다시 활성 | 통과 · U7-M10 | 기록 없음 |
| briefing.test.tsx::404(잠금 중)이면 "잠시 뒤 다시 시도" 안내만 — 자동 재시도 없음(POST 1회), 목록 재요청도 없고 버튼은 다시 활성 | 판정 21·결정 K | POST 404 → 그 항목에만 "잠시 뒤 다시 시도해 주세요.", 50ms 뒤에도 POST 1회·GET 1회, 버튼 활성 | 통과 · U7-M5 · U7-M11 · U7-V1 | 기록 없음 |
| briefing.test.tsx::5xx 이면 한 줄 실패 안내(잠금 문구가 아님), 버튼은 다시 활성이고 누르면 다시 보낸다 | 일반 오류 | 첫 POST 500 → `alert` "브리핑을 만들지 못했어요…"(잠금 문구 아님) / 다시 누름 → POST 2회·성공 시 GET 재조회·안내 사라짐 | 통과 · U7-M4 · U7-V1 | 기록 없음 |
| briefing.test.tsx::R-U7-2 (탐침 P4): 수동 브리핑은 성공했는데 재조회가 실패하면 이전 목록 3건을 그대로 두고 실패 한 줄만 더한다 | 재조회 실패 시 화면 유지 | 재조회 500 → 목록 5·2·9 그대로 + "브리핑을 불러오지 못했어요.", 빈 상태 문구 없음 | 통과 · U8-M26 | **검출 실패 → 보강**: U7 verifier 가 '재조회 실패 시 이전 목록 유지'를 기존 테스트(첫 조회 실패만 단언)가 고정하지 못한다고 지적 — 목록이 있을 때만 비우는 변이가 살아남음(R-U7-2). 탐침 P4 를 이 테스트로 옮김 · `review-u7-briefing.md` 53·95행 |
| briefing.test.tsx::R-U7-1: 수동 브리핑이 진행 중일 때 쿼리가 바뀌면, 끝난 뒤 재조회는 바뀐 일정(최신) 기준이다 | 경합 — 최신 쿼리 기준 | 진행 중 `?schedule_id=77` → `88` 로 바뀜 → 끝난 뒤 목록 88·5·2·9, 77 없음, 88 강조 | 통과 · U8-M19 | 기록 없음 |

## web/src/__tests__/sw.test.ts — 서비스 워커·manifest (16건)

실행: `cd web && npm test -- --run src/__tests__/sw.test.ts` → 16 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 22행). `public/sw.js` 를 `?raw` 로 읽어 가짜 `self`(리스너·registration·clients) 안에서 평가한다. 실제 워커·푸시 서비스는 쓰지 않는다. 이번 단위에서 2건 추가(R-U8-3).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| sw.test.ts::페이로드를 showNotification(title, {body, tag, data:{schedule_id}}) 로 그대로 넘긴다 | 원칙7 — 알림 문장 가공 없음 | `push` `{title:'  김팀장 회의 30분 전 ', body:…, tag:'schedule-12', schedule_id:12, ttl:600}` → `showNotification` 1회, title·body 앞뒤 공백까지 그대로, `data:{schedule_id:12}` | 통과 · U8-M3 · U8-M9 · U8-V1 | 기록 없음 |
| sw.test.ts::열린 모든 창에 {type:"briefing", schedule_id} 만 보낸다(title·body 는 보내지 않는다) | 열린 창 알림 | 창 2개 → 각 `postMessage({type:'briefing', schedule_id:7})` 정확히 1회 | 통과 · U8-M4 | 기록 없음 |
| sw.test.ts::schedule_id 가 빠진 페이로드면 data.schedule_id 와 메시지 모두 null | 일정 없는 푸시 | `{title,body,tag}` → `data:{schedule_id:null}`, 창 메시지 `schedule_id:null` | 통과 · U8-M3 · U8-M4 · U8-V1 | 기록 없음 |
| sw.test.ts::JSON 을 못 읽거나 데이터가 없으면 기본 제목 "알림"·빈 본문으로 띄운다 | 잘못된 페이로드 | `json()` 이 던짐 / `data:null` → 제목 "알림", body "" | 통과 · U8-M3 · U8-M8 | 기록 없음 |
| sw.test.ts::열린 창이 있으면 알림을 닫고 첫 창을 focus 한 뒤 {type:"open-briefing", schedule_id} 를 보낸다(새 창 없음) | 판정 22 알림 클릭(창 있음) | 앱 창 2개 → 알림 `close` 1회, 첫 창 `focus` 1회 + `postMessage({type:'open-briefing', schedule_id:12})`, 둘째 창 무변화, `openWindow` 0 | 통과 · U8-M6 · U8-M7 · U9-X2 | 기록 없음 |
| sw.test.ts::앱이 아닌 같은 출처 창이 앞에 있어도 앱 창(client.url 경로 "/")을 골라 focus 한다 | **R-U8-3 (신규)** — 개발용 페이지·`/api/docs` 탭이 앞에 있어도 | 창 `[/dev-page/, /api/docs, /#/persons]` → 앱 창만 `focus`+`postMessage(open-briefing, 12)`, 앞 두 창은 손대지 않음, `openWindow` 0 | 통과 · U9-X1 · U9-X2 | 기록 없음 |
| sw.test.ts::열린 창이 전부 앱이 아니면 그 창들은 건드리지 않고 openWindow("/#/briefings?schedule_id=N") | **R-U8-3 (신규)** — 앱 창이 없을 때 | 창 `[/dev-page/, /api/docs]` → `openWindow('/#/briefings?schedule_id=12')` 1회, 두 창 `focus`·`postMessage` 0 | 통과 · U9-X1 | 기록 없음 |
| sw.test.ts::열린 창이 없으면 openWindow("/#/briefings?schedule_id=N") | 판정 22 알림 클릭(창 없음) | 창 0 → `openWindow('/#/briefings?schedule_id=12')` 1회 | 통과 · U8-M5 | 기록 없음 |
| sw.test.ts::schedule_id 가 없거나 양의 정수가 아니면 일정 없는 브리핑 화면 주소 | 새 창 주소 경계 | `data` 가 null·`{}`·null·0·'12'·1.5 → `openWindow('/#/briefings')` | 통과 · U8-V2 | 기록 없음 |
| sw.test.ts::start_url 은 /#/chat, display 는 standalone | PWA manifest | `manifest.webmanifest` → `start_url:'/#/chat'`, `display:'standalone'` | 통과 · U8-M27 · U8-M28 | 기록 없음 |
| sw.test.ts::이름은 index.html <title> 과 같고, 색은 tokens.css 의 primary(#171717)·background(#ffffff) | 이름·색 일치 | `name`·`short_name` = `<title>`, `theme_color #171717`, `background_color #ffffff`, `<meta theme-color>` | 통과 · — | 기록 없음 |
| sw.test.ts::아이콘은 192·512 두 개이고 각각 실제 파일이다(외부 주소 없음) | 아이콘 2종 | icons `[192x192 /icon-192.svg, 512x512 /icon-512.svg]`, 타입 svg, 경로 `/` 시작, 각 svg 의 `width` | 통과 · U8-V5 | 기록 없음 |
| sw.test.ts::index.html 이 manifest 를 연결하고, favicon 은 같은 아이콘이다(템플릿 로고 아님) | manifest 연결·favicon | `<link rel="manifest" href="/manifest.webmanifest">`, favicon `fill="#171717"`·글자 "관", 템플릿 색 `#863bff` 없음 | 통과 · U8-M29 · U8-M30 | 기록 없음 |
| sw.test.ts::등록되는 리스너는 install · activate · push · notificationclick 넷뿐이다 | 결정 I — fetch 리스너 없음 | 등록된 이벤트 이름 정렬 → `['activate','install','notificationclick','push']` | 통과 · U8-M1 | 기록 없음 |
| sw.test.ts::install 은 skipWaiting, activate 는 clients.claim 만 한다 | 설치·활성 동작 | `install`→`skipWaiting` 1회, `activate`→`clients.claim` 1회 | 통과 · U8-M2 | 기록 없음 |
| sw.test.ts::코드에 요청 가로채기 리스너·캐시 API 호출이 없다 | 결정 I·M — 캐시 없음 | `sw.js` 소스에 `addEventListener('fetch'`·`onfetch`·`caches`·`Cache`·`fetch(` 없음 | 통과 · U8-M1 · U8-M2 | 기록 없음 |

## web/src/__tests__/push.test.ts — 푸시 구독·"알림 받기"·인앱 배너 (21건)

실행: `cd web && npm test -- --run src/__tests__/push.test.ts` → 21 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt` (판정 22·23행). `Notification`·`PushManager`·`navigator.serviceWorker`·`fetch` 전부 가짜. 이번 단위에서 1건 추가(R-U8-1).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| push.test.ts::base64url(-, _, 패딩 없음)을 바이트로 바꾼다 | VAPID 공개키 변환 | `AQID`→[1,2,3], `AQI`→[1,2], `-__-`→[251,255,254] | 통과 · U8-M15 | 기록 없음 |
| push.test.ts::새 구독: 권한 → 등록(/sw.js) → 공개키 → 구독 → 서버 저장 순서이고, 본문은 PushSubscriptionIn 필드 그대로 | 판정 23 구독 절차 | `subscribeToPush()` → 호출 순서 `permission, register, GET key, getSubscription, subscribe, POST`, `register('/sw.js')`, `userVisibleOnly:true`·키 바이트 [1,2,3], POST 본문 `{endpoint, keys:{p256dh,auth}, expirationTime:null}` | 통과 · U8-M12 · U8-M14 · U8-M16 · U8-V3 | 기록 없음 |
| push.test.ts::이미 구독돼 있으면 "already" — 구독도 서버 저장(POST)도 하지 않는다 | 이미 구독 | 기존 구독 있음 → `'already'`, `subscribe` 0, POST 0 | 통과 · U8-M10 | 기록 없음 |
| push.test.ts::권한이 허용되지 않으면 "denied" — 등록·공개키·구독이 없다 | 권한 거부 | 권한 denied → `'denied'`, `register`·`subscribe` 0, fetch 0 | 통과 · U8-M13 | 기록 없음 |
| push.test.ts::404 push_not_configured 면 "not_configured" — 구독·저장 없이 멈춘다 | 판정 23 서버 미설정 | 공개키 404 `push_not_configured` → `'not_configured'`, `getSubscription`·`subscribe` 0, fetch 1회 | 통과 · U8-M11 | 기록 없음 |
| push.test.ts::다른 404(코드가 다름)나 5xx 는 "not_configured" 가 아니라 "failed" | 코드까지 확인 | 404 `not_found` · 500 `push_not_configured` → `'failed'` | 통과 · — | 기록 없음 |
| push.test.ts::구독 실패·서버 저장 실패는 "failed" | 실패 결과 | `subscribe` 거부 / POST 500 → `'failed'` | 통과 · — | 기록 없음 |
| push.test.ts::서버 저장(POST)이 실패하면 브라우저 구독을 unsubscribe 1회로 되돌리고 "failed" — 404 push_not_configured 도 같다 | 저장 실패 시 되돌리기 | POST 500 · POST 404 → `'failed'`, `unsubscribe` 정확히 1회 | 통과 · U8-M31 | 기록 없음 |
| push.test.ts::저장 실패 뒤 다음 클릭은 처음부터 다시 — subscribe 재호출·POST 재시도(이번엔 성공) | "이미 켜짐"으로 남지 않음 | 1회째 POST 500 → `'failed'`, 2회째 → `'subscribed'`, `subscribe` 2회·POST 2회 | 통과 · U8-M31 | 기록 없음 |
| push.test.ts::unsubscribe 자체가 실패해도 예외 없이 "failed" | 되돌리기 실패 삼킴 | POST 500 + `unsubscribe` 거부 → `'failed'`(예외 없음), `unsubscribe` 1회 | 통과 · U8-M31 | 기록 없음 |
| push.test.ts::미지원 브라우저(serviceWorker·PushManager·Notification 없음)면 "unsupported" — 네트워크 0 | 미지원 | jsdom 기본 → `'unsupported'`, fetch 0 | 통과 · — | 기록 없음 |
| push.test.ts::미지원 · 구독 없음 · 구독 있음을 가른다(권한 창·네트워크 없음) | `getPushStatus` 3상태 | 미지원 → `unsupported` / 가짜 브라우저 구독 없음 → `unsubscribed` / 있음 → `subscribed`, 권한 요청·등록 0 | 통과 · — | 기록 없음 |
| push.test.ts::미구독 → 진행 중(비활성) → 켜짐(비활성) 세 상태 | 판정 23 버튼 상태 | "알림 받기"(활성) 클릭 → "알림 켜는 중"(비활성, POST 나간 뒤에도 유지) → POST 완료 → "알림 켜짐"(비활성), "알림 받기" 없음 | 통과 · U8-M18 | 기록 없음 |
| push.test.ts::들어올 때 이미 구독돼 있으면 곧바로 "알림 켜짐"(비활성) — 클릭 없이, 서버 저장 없이 | 진입 시 상태 | 기존 구독 → 곧바로 "알림 켜짐" 비활성, POST 0 | 통과 · U8-M17 · U8-M18 | 기록 없음 |
| push.test.ts::안내 한 줄: 권한 거부 · 서버 미설정 · 미지원 · 실패 — 버튼은 다시 "알림 받기"(활성) | 판정 23 안내 문구 4종 | 권한 denied / 공개키 404 push_not_configured / 공개키 500 / 미지원 → 각각 `push-note` 에 대응 안내, 버튼 다시 활성 | 통과 · U8-M11 · U8-M13 | 기록 없음 |
| push.test.ts::/push-dev/ 링크가 없다 | 개발용 페이지 링크 금지 | 브리핑 화면 → `a[href*="push-dev"]` 0 | 통과 · — | 기록 없음 |
| push.test.ts::{type:"briefing", schedule_id} 를 받으면 한 줄 배너 — 누르면 #/briefings?schedule_id=N, 누른 뒤 사라진다 | 결정 H 인앱 배너 | 워커 메시지 `{briefing, 9}` → 배너 문구 "새 브리핑 알림이 도착했어요." + 링크 `#/briefings?schedule_id=9` → 클릭 → 해시 이동·배너 사라짐 | 통과 · U8-M21 | 기록 없음 |
| push.test.ts::닫기 버튼으로 닫는다(주소는 그대로) | 배너 닫기 | `{briefing, 3}` → "닫기" → 배너 없음, 해시 `#/briefings` 그대로 | 통과 · U8-M23 | 기록 없음 |
| push.test.ts::schedule_id 가 없으면 일정 없는 브리핑 주소, 모양이 다른 메시지는 무시한다 | 메시지 모양 검증 | `{type:'other'}`·`'briefing'`·null → 배너 0 / `{briefing, null}` → 배너 링크 `#/briefings` | 통과 · — | 기록 없음 |
| push.test.ts::알림을 눌러 온 {type:"open-briefing"} 은 배너 없이 바로 그 일정 주소로 간다 | 판정 22 알림 클릭 → 그 일정 | `#/chat` 에서 `{open-briefing, 12}` → 해시 `#/briefings?schedule_id=12`, 배너 없음 | 통과 · U8-M21 · U8-M22 | 기록 없음 |
| push.test.ts::알림을 눌러 온 {type:"open-briefing", schedule_id:null} 은 배너 없이 일정 없는 #/briefings 로 간다 (R-U8-1) | **R-U8-1 (신규)** — null 경계 | `#/chat` 에서 `{open-briefing, null}` → 해시 `#/briefings`, 배너 없음 | 통과 · U9-X3 | **검출 실패 → 보강**: U8 verifier 변이 V4(`open-briefing` 의 `schedule_id` 가 null 이면 이동 생략)가 기존 130건을 통과(R-U8-1). 이 테스트를 U9a 에서 신설 · `review-u8-pwa-push.md` 99행 · `03-log.md` 151행 |

## web/src/__tests__/network.test.ts — 실 네트워크 0 (판정 27b행, 신규 2건)

실행: `cd web && npm test -- --run src/__tests__/network.test.ts` → 2 passed · 증거 `evidence/20261015-1410-u9-front-rows.txt`. 모든 테스트가 기대는 `src/test-setup.ts` 의 가짜 `fetch`(불리면 실패)가 살아 있는지 직접 시험한다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| network.test.ts::표에 없는 바깥 주소 fetch("https://example.invalid") 는 실패한다 | 바깥 주소 요청 차단 | `fetch('https://example.invalid')` → reject, 메시지 "실제 네트워크 요청은 허용되지 않는다" | 통과 · U9-X4 | 기록 없음 |
| network.test.ts::가짜 표 없이 앱 API 를 부르면(apiFetch → /api/persons) 응답 대신 실패한다 | 앱 API 도 가짜 표 없이는 실패 | 가짜 없이 `apiFetch('/persons')` → 같은 메시지로 reject | 통과 · U9-X4 | 기록 없음 |

---

## E2E (Playwright) — web/e2e (3 파일, 4건, 판정 24~26행·27b행)

실행: `cd web && npm run e2e` (= `playwright test`; 설정이 `npm run build && npm run preview -- --port 4173 --strictPort` 를 띄운다 — 현재 소스의 빌드 산출물이 대상) → `4 passed` · 증거 `evidence/20261015-1409-u9-final-judge.txt`. 브라우저: Chromium(Chrome Headless Shell 156.0.8078.4, Playwright 1.64.0). 규칙(`e2e/fixtures.ts`): `/api/` 요청은 전부 가짜 표가 답하고 표에 없으면 중단·기록, 이 호스트 밖 요청은 전부 중단, 시계 고정. **각 테스트는 끝에서 모은 요청 URL 전부가 "preview 호스트의 앱 파일 또는 `/api/` 경로" 이고 표 밖 요청이 0 임을 단언한다(27b).**

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| e2e/chat.spec.ts::발화를 보내면 칩이 뜨고, 눌러 재개된 reply 가 보이며, 새로고침하면 남은 질문 칩이 복원된다 | 판정 24 채팅 칩 + 27b | 발화 "어제 민지랑 점심 먹었어" Enter → reply + 칩 `직장·친구·아니요` / "친구" 클릭 → 재개 reply "친구로 기록했어요.", 눌린 칩 `aria-pressed=true`·나머지 비활성, 새 칩 `예·나중에`(질문 8) / **새로고침** → 화면 메모리는 지워지고 `GET /api/questions/pending` 으로 질문 8 칩만 복원 / "예" 클릭 → "일정으로 저장했어요." / 요청: `/api/chat` 본문 `{utterance}`·헤더 없음, `/api/answers/7` 본문 `{answer:'친구'}`·`X-Session-Id: s-1`, `/api/answers/8` `{answer:'예'}`, 새로고침 뒤 복원 요청에도 `s-1` | 통과 · U9-X5 · U9-X6 · U9-X7 · U9-X15 · U9-X16 | 기록 없음 (U9-X5·X6·X7 의 1차 시도는 변이가 타입 오류를 내 빌드가 실패한 무효 회차이며 테스트 실패가 아니다 · `evidence/20261015-1404-u9-mutation.txt`) |
| e2e/card.spec.ts::데스크톱 폭 1280px › 사이드바 인물 목록에서 인물을 눌러 카드를 열고 타임라인 원문을 펼친다 | 판정 25 데스크톱 + 27b | 1280px: 사이드바 항상 보임·"메뉴 열기" 없음 / 사이드바 인물 "김팀장" 클릭 → `#/persons/3`, 본문에 그 카드 / 타임라인 "원문 펼치기" → 원문 표시(`textContent` 완전 일치 — 줄바꿈·이모지 포함 글자 그대로. `toHaveText` 는 공백을 정규화해 R-U9a-1 로 바꿈), `GET /api/events/31/raw` 1회 / 사이드바 항목 채팅·인물·브리핑 클릭 → 각 화면(`data-screen`)·주소·`aria-current` 전환 / 사이드바 링크 5개(항목 3 + 인물 2) | 통과 · U9-X8 · U9-X10 · U9-X15 · U9-X16 · U9-V2(원문 `\n`→공백: 수정 전 E2E 생존, 수정 후 1 failed — `evidence/20261015-1435-u9a-rework-v2-mutation.txt`) | **검출 실패 → 보강**: U9a verifier 변이 V2(원문 줄바꿈 → 공백)가 1차 E2E 를 통과(Vitest 만 검출, R-U9a-1) — Playwright `toHaveText` 가 공백을 정규화해서. 커밋 전 `textContent` 완전 일치로 강화, 재실행에서 1 failed 로 검출 · `review-u9a-e2e.md` 5행 · `evidence/20261015-1443-verifier-u9a-rework-v2-mutation.txt` |
| e2e/card.spec.ts::모바일 폭 390px › 서랍은 처음엔 닫혀 있고 하단 탭바가 없다. 메뉴 버튼 -> 인물 -> 인물 -> 카드, 항목을 고르면 서랍이 닫힌다 | 판정 25 모바일 + 27b | 390px: 처음엔 `navigation` 0·`tablist` 0, "메뉴 열기" 보임 / 메뉴 → 서랍 열림 → "인물" → 서랍 닫힘·인물 화면·`#/persons` / 다시 열어 서랍 안 "김팀장" → 서랍 닫힘·`#/persons/3`·카드 / 서랍을 열고 Esc 로 닫아도 주소 그대로 `#/persons/3`(라우트 3경로 그대로), 끝까지 탭바 0 | 통과 · U9-X9 · U9-X11 · U9-X15 · U9-X16 | 기록 없음 |
| e2e/briefing.spec.ts::쿼리의 일정이 맨 위에 강조돼 열리고, 지금 브리핑을 누르면 목록이 다시 읽힌다 | 판정 26 브리핑 + 27b | `#/briefings?schedule_id=7` 직접 열기, 서버 순서 [9, 7] → 목록 7(맨 위, `data-highlight=true`)·9(강조 없음), 머리줄에 `김팀장 · 주간 회의` / 7 의 "지금 브리핑" → POST `/api/briefings/run` 본문 `{schedule_id:7}` 1회 → 목록 다시 읽기(`GET /api/briefings` 총 2회) → 7 의 줄이 새 문장으로 갱신, 7 이 계속 맨 위 | 통과 · U9-X12 · U9-X13 · U9-X14 · U9-X15 · U9-X16 | 기록 없음 (U9-X13 의 1차 시도는 무효 회차) |

---

## 백엔드 (pytest) — tests/ 5 파일, 64건 (판정표 1~11행·28행 백엔드 부분)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py tests/test_api_read_raw.py tests/test_api_questions_pending.py tests/test_api_read_briefings.py tests/test_api_read_briefings_e2e.py -v` → **64 passed** (파일별: persons 12 · raw 18 · pending 8 · briefings 24 · briefings_e2e 2). 행별 증거 `evidence/20261015-1521-u9-be-rows-1-4-persons.txt`(1~4행) · `…1522-u9-be-rows-5-6-raw.txt`(5·6행) · `…-u9-be-row-8-pending.txt`(8행) · `…-u9-be-row-7-write-zero.txt`(7행) · `…-u9-be-rows-9-10-briefings.txt`(9·10행) · `…-u9-be-row-11-nochange.txt`(11행). 전체 회귀 1946 passed(skip 0) `…1524-u9-be-full-regression.txt`. 모든 테스트는 `TestClient(create_app())` + 롤백되는 `db_session`(실 PostgreSQL)이며 LLM·외부 네트워크 0, "지금" 은 `get_now` 오버라이드로 고정(`NOW = 2026-03-01T09:00Z`).

### tests/test_api_read_persons.py — `GET /persons`·`GET /persons/{id}` (U1, 12건, 판정표 1~4행)

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_read_persons.py::test_목록_last_contact_는_max_이고_정렬은_max_기준 | 목록의 `last_contact_at` 이 이벤트 `occurred_at` **최댓값**이고 그 값으로 정렬 | A(이벤트 30일 전·1일 전)·B(10일 전) → `[A, B]` 순, A = NOW-1일, B = NOW-10일 (min 이면 순서·값이 뒤집힌다) | 통과 · U1-V4 | **검출 실패 → 보강**: U1 verifier 1차 **보류**(R-U1-1) — 변이 4(`max`→`min`)가 1차 테스트 7건을 모두 통과(`7 passed`). 재작업에서 이 테스트를 신설하자 4건이 검출됨 · `review-u1-read-persons.md` 4행·5절·재검토 1 · `03-log.md` 28행 |
| test_api_read_persons.py::test_카드_last_contact_는_가장_늦은_occurred_at | 카드의 `last_contact_at` 값 | 이벤트 30·10·1일 전 → NOW-1일 | 통과 · U1-V4 | **검출 실패 → 보강**: 위 행과 같음(R-U1-1, 재작업에서 신설 — 1차는 `is not None` 만 단언) |
| test_api_read_persons.py::test_카드_별칭은_파이썬_sorted_코드포인트순 | 별칭 정렬이 DB 콜레이션이 아니라 Python `sorted()` | 별칭 `가나·apple·Zed·Bob` → `["Bob","Zed","apple","가나"]` | 통과 · U1-V7 | 기록 없음 (R-U1-4 권고로 재작업에서 신설된 테스트 — 실패 기록은 아님) |
| test_api_read_persons.py::test_다가오는_일정_상한은_10건_가까운_순 | 다가오는 일정 상한 10과 가까운 순 | 일정 11건을 역순 삽입 → `일정1..일정10` | 통과 · U1-V5 | 기록 없음 (R-U1-3 으로 재작업에서 신설) |
| test_api_read_persons.py::test_다가오는_일정_경계_지금은_포함_1초_전은_제외 | `scheduled_at >= now` 경계 | `NOW-1초`·`NOW` → `["지금"]` | 통과 · U1-V6 | 기록 없음 (R-U1-3 으로 재작업에서 신설) |
| test_api_read_persons.py::test_목록_정렬_최근순_null_뒤_동률은_id순 | 목록 정렬 전체(최근순 → null 뒤 → 동률은 id 순)와 필드 5개 | A(5·9일 전)·B(없음)·C(1일 전)·D(없음)·E(C 와 동률) → `[C, E, A, B, D]`, A = NOW-5일(max), B = null, 키 집합 `{id, display_name, relation_tag, hierarchy, last_contact_at}` | 통과 · U1-V4 | **검출 실패 → 보강**: R-U1-1 재작업에서 `A: max(5, 9)` 값 단언을 더함(1차 단언은 순서만이라 `min` 변이를 못 잡았다) · 출처 위와 같음 |
| test_api_read_persons.py::test_목록은_다른_사용자_인물을_뺀다 | 사용자 격리 | user_id `local` 1명·`other` 1명 → `local` 만 | 통과 · U1-V1 | 기록 없음 |
| test_api_read_persons.py::test_카드_구성과_분리_집계 | 카드 구성 전체와 사실/패턴 분리·`source_count` | 별칭 2·이벤트 2·사실 3(`pattern:` 1)·`fact_sources` 3·일정 3 → 별칭 정렬, `last_contact_at` = NOW-2일, `facts` = {취미(source 2), 직업(0)}, `patterns` = [pattern:meal(1)], 타임라인 최근 순, 일정 [곧, 나중](과거 제외) | 통과 · U1-V4 | **검출 실패 → 보강**: R-U1-1 재작업에서 `NOW-2d` 값 단언을 더함(1차는 `is not None` 만) · 출처 위와 같음 |
| test_api_read_persons.py::test_타임라인_상한 | 타임라인 상한 `TIMELINE_LIMIT`(=20) | 이벤트 `TIMELINE_LIMIT+5`건 → 길이 `TIMELINE_LIMIT`, 첫 항목 `내용0` | 통과 · — | 기록 없음 |
| test_api_read_persons.py::test_응답에_raw_utterance_가_없다 | 목록·카드에 원문 없음(결정 F) | 이벤트 원문 "절대노출금지" → 두 응답 텍스트에 감시 문자열·키 `raw_utterance` 0회 | 통과 · U1-V3 | 기록 없음 |
| test_api_read_persons.py::test_없는_인물과_타사용자_인물은_같은_404 | 없는 것·남의 것이 같은 404(존재 누설 없음) | 타 사용자 인물 id / `99999999` → 둘 다 404 `{"detail":{"code":"not_found"}}` | 통과 · U1-V2 | 기록 없음 |
| test_api_read_persons.py::test_쓰기_0_trace_0 | 조회는 DB 를 쓰지 않는다 — 9테이블 행 수 + `briefed_at`·`updated_at` **값**까지 | 인물(`updated_at`=30일 전)·이벤트·사실·근거·일정 2(하나는 `briefed_at` 7시간 전) → `GET /persons`·`GET /persons/{id}`·404 호출 전후 `assert_no_writes`, `briefed_at`·`updated_at` 가 넣은 값 그대로 | 통과 · U9b-M4a · U9b-M4b · U9b-M4e | **검출 실패 → 보강**: 옛 판(행 수 7테이블만 비교)은 쓰기 변이 M4a·M4b·M4e 를 **전부 통과(생존)** — U9b 에서 공통 헬퍼(`helpers_read_api`)로 교체, `updated_at`·`briefed_at` 를 과거 값으로 못 박아 검출됨(R-U3-5 ①) · `evidence/20261015-1523-u9-be-mutation-old-tests.txt` · `review-u3-read-questions-briefings.md` 105행 |

### tests/test_api_read_raw.py — `GET /events/{id}/raw`·`GET /persons/{pid}/facts/{fid}/sources` (U2, 18건, 판정표 5·6행)

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_read_raw.py::test_이벤트_원문_응답_전체_값 | 이벤트 원문 응답 필드 6개와 원문 글자 그대로 | 이벤트(type conflict·content 말다툼·3일 전, 원문 = 특수문자·줄바꿈·탭·이모지·앞뒤 공백 `TRICKY_RAW`) → 200, 키 집합 `{event_id, person_id, type, content, occurred_at, raw_utterance}`, 값 일치, `raw_utterance == TRICKY_RAW` | 통과 · U2-M6 | 기록 없음 |
| test_api_read_raw.py::test_이벤트_원문은_두_이벤트를_섞지_않는다 | 이벤트별 원문 분리 | 같은 인물의 이벤트 2개 → 각자 자기 원문 | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_이벤트_원문_긴_문자열도_자르지_않는다 | 길이 절단 없음 | 5000자 원문 → 그대로 | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_이벤트_404_없는_이벤트 | 없는 이벤트 | `/events/99999999/raw` → 404 `{"detail":{"code":"not_found"}}` | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_이벤트_404_타사용자_이벤트 | 남의 이벤트는 404 이고 원문이 새지 않음 | `other` 사용자 인물의 이벤트(원문 "남의 비밀") → 404, 응답 텍스트에 "남의 비밀" 없음 | 통과 · U2-M2 | 기록 없음 |
| test_api_read_raw.py::test_근거_응답_전체_값과_내림차순 | 근거 응답 구조·값·내림차순 | 이벤트 3개(중간·오래됨·최신)를 섞어 삽입 후 사실 1 에 연결 → 200 `{fact, sources}`, `fact == {id, key 취미, value 등산}`, sources 순서 [최신, 중간, 오래됨], 각 `type`·`content`·`occurred_at`·원문 일치(오래됨은 `TRICKY_RAW`), 원소 키 5개 | 통과 · U2-M4 · U2-M6 | 기록 없음 |
| test_api_read_raw.py::test_근거_동률_occurred_at_은_id_내림차순 | 같은 시각일 때 2차 키 | 같은 `occurred_at` 이벤트 a<b<c 를 사실에 연결 → `[c, b, a]` | 통과 · U2-M4 · U2-M8 | 기록 없음 |
| test_api_read_raw.py::test_근거_상한 | 근거 상한 `FACT_SOURCES_LIMIT`(=20) | 이벤트 25건 연결 → 20건, 최신 20건(`원문0..19`)만 남고 가장 오래된 5건이 잘림 | 통과 · U2-M4 · U2-M5 | 기록 없음 |
| test_api_read_raw.py::test_근거_없는_사실은_빈_목록 | 근거 0건 | 연결 없는 사실 → 200 `{"fact": …, "sources": []}` | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_근거는_다른_사실의_원문을_섞지_않는다 | 사실별 근거 분리 | 사실 1(근거 e1)·사실 2(근거 e2) → 사실 1 의 sources 는 e1 원문 하나 | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_근거_404_없는_사실 | 없는 사실 | `.../facts/99999999/sources` → 404 not_found | 통과 · — | 기록 없음 |
| test_api_read_raw.py::test_근거_404_없는_인물 | 없는 인물 경로 | `/persons/99999999/facts/{내 사실}/sources` → 404 | 통과 · U2-M1 | 기록 없음 |
| test_api_read_raw.py::test_근거_404_남의_인물_경로의_남의_사실 | 남의 인물·남의 사실 | `other` 의 인물·사실 → 404, "남의 비밀" 없음 | 통과 · U2-M3 | 기록 없음 |
| test_api_read_raw.py::test_근거_404_내_다른_인물의_사실을_경로_인물에_끼운_경우 | 넘겨짚기 차단: 내 다른 인물의 사실 id | 경로 인물 A + B 의 사실 → 404, B 의 원문 없음 | 통과 · U2-M1 | 기록 없음 |
| test_api_read_raw.py::test_근거_404_남의_인물_경로에_내_사실을_끼운_경우 | 남의 인물 경로에 내 사실 | 경로 `other` 인물 + 내 사실 → 404 | 통과 · U2-M1 | 기록 없음 |
| test_api_read_raw.py::test_근거_세_404_응답이_서로_같다 | 세 종류 404 의 본문이 같아 존재 여부가 새지 않음 | 없는 사실 / 남의 것 / 내 다른 인물의 사실 → 모두 404, 응답 텍스트 하나로 같음 | 통과 · U2-M1 · U2-M3 | 기록 없음 |
| test_api_read_raw.py::test_근거에_다른_인물_이벤트가_연결돼_있어도_나가지_않는다 | 데이터 오염 방어(`Event.person_id` 조건) | 내 사실에 남의 이벤트를 억지로 연결 → sources 는 내 원문만, "남의 비밀" 없음 | 통과 · U2-M7 | 기록 없음 |
| test_api_read_raw.py::test_쓰기_0_trace_0 | 조회는 DB 를 쓰지 않는다 — 9테이블 행 수 + `briefed_at`·`updated_at` 값까지 | 인물(`updated_at`=30일 전)·이벤트·사실·별칭·일정(`briefed_at` 7시간 전) → 200 두 번·404 두 번 전후 `assert_no_writes`, 값 그대로 | 통과 · U9b-M4c · U9b-M4d | **검출 실패 → 보강**: 옛 판은 쓰기 변이 M4c·M4d 를 **전부 통과(생존)** — 공통 헬퍼로 교체해 검출됨(R-U3-5 ①) · `evidence/20261015-1523-u9-be-mutation-old-tests.txt` · `review-u3-read-questions-briefings.md` 105행 |

### tests/test_api_questions_pending.py — `GET /questions/pending` (U3, 8건, 판정표 8행)

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_questions_pending.py::test_헤더_없으면_빈_목록_이고_쓰기_0 | 헤더 없는 요청은 빈 목록이고 서버가 세션을 새로 저장하지 않음(R-11) | 다른 세션 질문 1건이 있는 채 `X-Session-Id` 없이 호출 → 200 `[]`, 전후 `assert_no_writes` | 통과 · U3-M21 | 기록 없음 |
| test_api_questions_pending.py::test_형식_위반_세션_헤더는_422 | 세션 헤더 형식 검사(`/chat` 과 같은 규칙) | `a b`·`a@b`·129자·`a/b`·빈 문자열 → 422 `{"detail":{"code":"invalid_session_id"}}` | 통과 · — | 기록 없음 |
| test_api_questions_pending.py::test_필드_5개_값_일치 | 응답 필드 5개 값 | new_person 질문 1건(옵션 `기억해줘`·`아니`) → `[{question_id, status:"pending", kind, question, options}]` 완전 일치 | 통과 · U3-M20 · U9b-M1 | 기록 없음 |
| test_api_questions_pending.py::test_created_at_오름차순 | 생성 시각 오름차순 | 삽입 순서와 다르게 3시간 전·1시간 전·1분 전 → 오래된 순 | 통과 · U3-M20 · U9b-M1 | 기록 없음 |
| test_api_questions_pending.py::test_다른_세션_질문은_제외 | 세션 격리 | 세션 S 1건·다른 세션 1건 → S 의 것만 | 통과 · U3-M20 · U9b-M1 | 기록 없음 |
| test_api_questions_pending.py::test_답변된_질문은_제외 | 미답변만 | 열림 1·답변됨 1 → 열림만 | 통과 · U3-M20 · U9b-M1 | 기록 없음 |
| test_api_questions_pending.py::test_만료_경계_24시간 | 24시간 만료 경계 | 23시간 59분 59초 전 / 정확히 24시간 전 / 25시간 전 → 첫째만 | 통과 · U3-M20 · U9b-M1 | 기록 없음 |
| test_api_questions_pending.py::test_쓰기_0_trace_0 | 세 경로에서 쓰기 0 | 열림·답변됨·만료 질문 → 세션 S·세션 `none`·헤더 없음 호출 전후 `assert_no_writes`, 결과 1건·`[]`·`[]` | 통과 · U3-M20 · U3-M21 · U9b-M1 | 기록 없음 |

### tests/test_api_read_briefings.py — `GET /briefings` (U3 + U9b 신규 2건, 24건, 판정표 9·10행의 trace 직접 삽입 부분)

U3 단위 테스트는 `briefing_compose` trace 행을 **직접 넣어** 조회 규칙을 시험한다. 실제 실행이 만든 trace 를 읽는 끝에서 끝은 다음 절(`briefings_e2e`)이다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_read_briefings.py::test_응답_필드_매핑_전체_값 | 항목 9키와 값 매핑 | 인물 김팀장·일정 "주간 회의"(5시간 뒤)·compose trace(composer template·push sent:1·패턴 문장 1·줄 1·suggestion null) → 키 집합 9개, `schedule`/`person` 하위 키, `generated_at` = trace `created_at`, `trace_id` = trace id, 나머지 값 전부 일치 | 통과 · U3-M17 · U3-M18 · U3-M19 | 기록 없음 |
| test_api_read_briefings.py::test_제안이_있으면_basis_그대로 | 제안 `{text, basis}` 가 가공 없이 나감 | 제안이 있는 trace → `suggestion` 완전 일치, composer `llm` | 통과 · — | 기록 없음 |
| test_api_read_briefings.py::test_일정마다_최신_1행만 | 일정마다 가장 최근 compose 1행 | 같은 일정 trace 3개(5·1·3시간 전, 삽입 순서 섞임) → 1건, 1시간 전 것(`최신`) | 통과 · U3-M1 · U3-M15 · U3-M18 · U3-V4 | 기록 없음 |
| test_api_read_briefings.py::test_동률_created_at_이면_id_큰_행 | 같은 `created_at` 일 때 id 큰 행 | 같은 시각 trace a·b(b.id > a.id) → b | 통과 · U3-M2 · U3-M15 · U3-M18 · U3-V4 | 기록 없음 |
| test_api_read_briefings.py::test_run_과_error_행은_섞이지_않는다 | 원천은 `briefing_compose` step 만(R-9) | compose(3시간 전) + 더 최근 `briefing_run`(1시간 전)·`briefing_error`(5분 전) → compose 만 | 통과 · U3-M3 · U3-M18 · U3-V1 | 기록 없음 |
| test_api_read_briefings.py::test_다른_tool_name_의_compose_step_은_제외 | `tool_name='briefing'` 조건 | `tool_name="other_tool"`·step compose → `[]` | 통과 · U3-M4 | 기록 없음 |
| test_api_read_briefings.py::test_error_만_있는_일정은_제외 | `briefing_error` 만 있는 일정은 목록에 없음 | 일정 2(오류만 / 정상) → 정상만 | 통과 · U3-M3 · U3-V1 | 기록 없음 |
| test_api_read_briefings.py::test_다른_사용자_일정은_제외 | 사용자 격리 | 내 일정·`other` 일정 각 compose → 내 것만, 응답에 "남" 없음 | 통과 · U3-M5 · U3-V2 | 기록 없음 |
| test_api_read_briefings.py::test_조작된_trace_남의_일정_id_와_내_인물_id_는_목록에_섞이지_않는다 | **(U9b 신규, R-U3-2)** trace 의 `person_id` 가 그 일정의 실제 인물과 다르면 제외 | 남의 일정 id + 내 인물 id 로 조작한 trace 1개 + (R-U9b-1 재작업) 내 일정 id + 남의 인물 id 로 조작한 trace 1개 + 정상 trace 1개 → 정상 일정만, "남의 비밀 일정"·"조작된 trace" 문자열 없음 | 통과 · U9b-M2 · U9b-V2(verifier: 조인을 `Schedule.person_id` 만으로 — 1차는 64건 생존, 재작업 후 검출) | **검출 실패 → 보강**: verifier 변이 V2 가 1차 64건에서 생존(한 방향만 시험, R-U9b-1) → 반대 방향 조작 trace 단언 추가 · `review-u9b-backend.md` 55행 · `evidence/*-u9b-rework1-v2-mutation.txt` |
| test_api_read_briefings.py::test_기간_경계_정확히_7일전_포함_7일_1초전_제외_미래_포함 | 기간 `BRIEFINGS_LOOKBACK_DAYS`(=7) 경계 | 정확히 7일 전 / 7일 1초 전 / 30일 뒤 → `[미래, 7일 전]`, 7일 1초 전 제외 | 통과 · U3-M6 · U3-M7 · U3-M9 · U3-V3 · U3-V5 | 기록 없음 |
| test_api_read_briefings.py::test_정렬_scheduled_at_내림차순과_2차키_id_내림차순 | 정렬 1차·2차 키 | 일정 4(먼 미래·같은 시각 A·B·과거), trace 생성 순서 섞음 → `[먼 미래, B, A, 과거]` | 통과 · U3-M8 · U3-M9 · U3-V5 | 기록 없음 |
| test_api_read_briefings.py::test_상한_21개_일정이면_20개 | 상한 `BRIEFINGS_LIMIT`(=20) | 일정 21건 → 20건, 가장 이른 1건이 잘림 | 통과 · U3-M9 · U3-M10 · U3-M11 · U3-V5 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_필터_1건 | `schedule_id` 지정 시 그 일정만 | 일정 2 → `?schedule_id=` 지정한 일정 1건, `trace_id` 일치 | 통과 · U3-M16 · U3-M18 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_지정_시_기간_밖도_조회됨 | 지정 모드는 기간 창을 적용하지 않음(푸시 클릭용) | 30일 전 일정 → 기본 모드 `[]`, 지정 모드 `[그 일정]` | 통과 · U3-M12 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_일정은_있으나_trace_없으면_빈_목록 | trace 없는 일정 | 일정만 있음 → 200 `[]` | 통과 · — | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_error_만_있어도_빈_목록 | error trace 만 있는 일정 | 200 `[]` | 통과 · U3-M3 · U3-V1 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_없는_일정은_404 | 없는 일정 | `?schedule_id=99999999` → 404 not_found | 통과 · U3-M13 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_남의_일정은_404 | 남의 일정 | `other` 의 일정 → 404 not_found | 통과 · U3-M13 · U3-M14 | 기록 없음 |
| test_api_read_briefings.py::test_schedule_id_두_404_응답이_같다 | 두 404 본문이 같음 | 없는 일정 / 남의 일정 → 둘 다 404, 본문 동일 | 통과 · U3-M13 · U3-M14 | 기록 없음 |
| test_api_read_briefings.py::test_응답에_raw_utterance_없음 | 원문 필드 0(결정 F) | 이벤트 원문 "…비밀원문XYZ" → 두 모드 응답에 `raw_utterance` 0회·감시 문자열 0회, `event_ids` 만 나감 | 통과 · — (변이 V7 은 동치: 응답 모델이 모르는 키를 버려 막는다 — 테스트 공백이 아니라 다른 층이 막음, `review-u3` 5절) | 기록 없음 |
| test_api_read_briefings.py::test_쓰기_0_trace_0_briefed_at_updated_at_불변 | 조회는 DB 를 쓰지 않는다 — 행 수 + `briefed_at`·`updated_at` 값 | 일정 2(하나는 `briefed_at` 7시간 전)·인물 `updated_at`=30일 전 → 목록·지정·404 호출 전후 `assert_no_writes`, `briefed_at` = {브리핑됨: 원래 값, 미브리핑: NULL} | 통과 · U3-M13 · U3-M16 · U3-M23 · U3-M24 · U3-V5 | 기록 없음 |
| test_api_read_briefings.py::test_헬퍼_자체_briefed_at_또는_updated_at_변경은_잡아낸다 | 공통 헬퍼가 값 변화를 잡는지 | `briefed_at` 를 바꾸면 `AssertionError(briefed_at)`, `display_name` 변경(`onupdate`)이면 `AssertionError(updated_at)` | 통과 · — (같은 헬퍼 변이 M23·M24 는 위 쓰기 0 테스트가 검출) | 기록 없음 |
| test_api_read_briefings.py::test_헬퍼_자체_push_subscriptions_추가도_잡아낸다 | **(U9b 신규, R-U3-5 ②)** 스냅샷이 스키마 v2 의 9테이블(`push_subscriptions` 포함)을 셈 | `len(snapshot.counts) == 9`, `push_subscriptions` 1행 추가 → `AssertionError("행 수")` | 통과 · U9b-M3 | 기록 없음 (신규 — 첫 실행부터 통과) |
| test_api_read_briefings.py::test_응답은_JSON_직렬화_가능 | 응답이 JSON 으로 읽힘 | 정상 trace 1개 → `json.loads(응답 텍스트)` 성공 | 통과 · — | 기록 없음 |

### tests/test_api_read_briefings_e2e.py — 실제 실행이 만든 trace 를 읽는 끝에서 끝 (U9b 신규 2건, 판정표 9·10행)

`FakeBriefingComposer`(결정적, 네트워크 0)·`NullNotifier`·고정 시계. trace 행을 직접 넣지 않고 **실제 `POST /briefings/run` 과 `run_briefings(trigger="scheduler")` 가 `briefing_compose` trace 를 만들게 한 뒤** `GET /briefings` 응답과 그 trace `output` 을 값으로 비교한다(review-u3 32행·R-U3-6 ④ 가 U9 몫으로 넘긴 부분).

**한계(R-U9b-3):** 정렬 1차 키(`created_at`)와 `tool_name` 필터는 이 2건이 고정하지 않는다(같은 트랜잭션이라 `created_at` 동률, 다른 `tool_name` 의 compose 행 없음 — verifier 변이 V1-e2e·V3-e2e 생존). 그 둘은 U3 단위 테스트(`test_일정마다_최신_1행만`·`test_다른_tool_name_의_compose_step_은_제외`)가 고정한다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_read_briefings_e2e.py::test_9행_수동_실행과_주기_실행이_만든_trace_를_그대로_읽는다 | 판정표 9행 — 두 실행 경로의 trace 를 `GET /briefings` 가 그대로 보여 줌 | 인물 김팀장(사실 `hobby`=등산 + 근거 이벤트)·일정 s1(5시간 뒤)·s2(8시간 뒤), 생성기 표 s1 "수동 실행 줄"·s2 "주기 실행 줄" → `POST /briefings/run {schedule_id:s1}` 200·s1 1건, `run_briefings(trigger="scheduler")` 가 s2 만 브리핑(s1 은 `briefed_at` 찍힘) → `GET /briefings` 2건 `[s2, s1]`, 각 항목의 `lines`·`suggestion`·`pattern_sentences`·`composer`(`llm`)·`push`·`trace_id`·`generated_at` 가 그 일정의 compose trace(실제로 1행) 와 같음, 생성기 문장이 거부 없이 실림, `schedule.title`·`person.display_name` 채워짐, `briefing_run` trace 의 `trigger` = `[manual, scheduler]` | 통과 · U9b-M5 | **실제 실패**(1회): 처음 쓴 직후 첫 실행에서 실패 — 시험 데이터의 사실 키 `취미` 가 승격 어휘 `FACT_KEYS` 밖이라 브리핑 입력의 `used_facts` 에 들어가지 못해 생성기 줄·제안이 `unknown_basis` 로 거부되고 `lines == []`. 키를 `hobby` 로 고쳐 통과. 당시 출력은 `save_evidence` 를 거치지 않아 남아 있지 않아 같은 원인으로 재현한 것을 증거로 둔다 · `evidence/20261015-1527-u9-be-first-failure-repro.txt` |
| test_api_read_briefings_e2e.py::test_10행_재실행_사용자_범위_원문_다른_step_혼입 | 판정표 10행 — 재실행·사용자 범위·원문·다른 step 혼입 | 같은 일정 s1 을 지정해 2회 실행(생성기 응답 다르게: "첫째 실행"→"둘째 실행") → compose 행 2개(두 번째 id 가 큼), 사용자 B 일정을 `run_briefings(user_id="other")` 로 실제 실행, s1·s3(오류만) 에 나중 시각 `briefing_error` 행을 직접 추가(`briefing_run` 행 3개는 실제 실행이 남긴 것으로 `output` 에 최상위 `schedule_id` 가 없어 — `run.py` 308~317행 — 혼입 검출 재료가 아니다. 재료는 직접 넣은 `briefing_error` 행이고, run 행 혼입은 U3 단위 `test_run_과_error_행은_섞이지_않는다` 가 맡는다) → `GET /briefings` 는 s1 하나뿐, `trace_id` = 두 번째 compose, 줄 "둘째 실행"·제안 "둘째 제안", `raw_utterance`·"비밀원문XYZ"·"남의 비밀"·"남의 일정" 0회, `?schedule_id=s1` 도 같은 행 | 통과 · U9b-M6 · U9b-M7 · U9b-M8 · U9b-M9 | 기록 없음 — 첫 실행은 `pytest -x` 로 위 테스트에서 멈춰 이 테스트의 결과가 남지 않았다. 같은 원인(사실 키 `취미`)을 재현하면 이 테스트도 `assert [] == ['둘째 실행']` 로 실패하지만, 당시 실제 실패 기록은 아니다(재현은 참고용) · `evidence/20261015-1527-u9-be-first-failure-repro.txt` |

### FIX-035 — identity 거절 → new_person 후속 질문 · 후보 1명 문구 (7건, 아래 "실패 이력 집계"에 포함)

P8 활성 중 들어간 FIX-035(`docs/wiki/fixes/FIX-035.md`)의 테스트다. 맨 위 "총계" 203건은 P8 단위가 만든 것만 센 값이고, 이 7건은 그와 따로 세되 "실패 이력 집계"에는 넣는다(사용자 결정 2026-10-16, R-35-7 — 집계 210건 = 203 + 7)(`tests/test_api_answers_resume.py` 5 · `tests/test_er_pipeline.py` 1 · `tests/test_tools_context.py` 1). 변이 ID 는 `review-FIX-035.md` §2 의 M1~M12 와, 재작업 1차의 `M6a/M6b/M6c`(헬퍼 변이) 이다. 증거: 재작업 변이 `fixes/evidence/20261016-1734-FIX-035-rework1-mutations.txt` · 전체 회귀 1953 passed(skip 0) `…1735-FIX-035-rework1-full-regression.txt` · verifier 변이 `…1722-verifier-FIX-035-mutations.txt`. 모두 `TestClient` + 롤백되는 실 PostgreSQL, LLM·외부 네트워크 0.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| test_api_answers_resume.py::test_answers_resume_identity_reject_asks_new_person_followup_fix035 | identity 거절("아니요, 다른 사람이에요")이 발화를 버리지 않고 같은 언급의 new_person 후속 질문을 낸다 | 후보 1명(김민수, 별칭 `팀장`) identity 질문 → 거절 답 → 후속 질문 `kind=new_person`·문구 `"팀장"을(를) 새 인물로 기억해둘까요?`·칩 = 태그 5 + `아니요`·`stop_reason=ask_user`·`stored` 전부 0·인물/사건 행 수 불변, 첫 질문 answered, 후속 context 의 `resume.pending_calls == [add_event]`·`tag_by_answer` | 통과 · FIX-035-M1 · M2 · M3 · M12 | 기록 없음 |
| test_api_answers_resume.py::test_answers_resume_identity_reject_writes_trace_fields_fix035 | 원칙9 — 거절 전환 사실이 `loop_resume` 행 `output` 에 영속된다 | 거절 답 후 DB 재조회 → `output.identity_rejected is True`·`followup_question_id == 후속 질문 id`·`kind=identity`·`answer=거절 문구` | 통과 · FIX-035-M1 · M6 · M7 · M9 · M6a · M6b | 기록 없음 |
| test_api_answers_resume.py::test_answers_resume_identity_reject_then_tag_creates_person_and_event_fix035 | 후속 질문에 태그 칩으로 답하면 그때만 인물이 생기고 원래 보류 제안(`add_event`)이 저장된다(D1) | 거절 → `직장으로 기억할게요` → `stored = {persons 1, events 1}`·`relation_tag="직장"`·이벤트 `type=meal`·`raw_utterance` 원문 | 통과 · FIX-035-M1 · M2 · M3 · M11 · M12 | 기록 없음 |
| test_api_answers_resume.py::test_answers_resume_identity_reject_then_no_creates_nothing_fix035 | 후속 질문에 `아니요` 면 아무것도 만들지 않는다 | 거절 → `아니요` → `stored` 전부 0·`pending_question=None`·인물/사건 행 수 불변 | 통과 · FIX-035-M1 · M2 · M12 | 기록 없음 |
| test_api_answers_resume.py::test_answers_resume_identity_reject_then_tag_keeps_hierarchy_hint_fix035 | (재작업 1차 R-35-2) 원래 턴의 `create_person` 힌트 위계가 후속 질문을 거쳐 보존된다 | `create_person(hierarchy="상")` 힌트 제안을 함께 넣은 identity 질문 → 거절 → 태그 답 → 후속 context `resume.hints.hierarchy == "상"`·`person.hierarchy == "상"`(유실되면 기본 `동`) | 통과 · FIX-035-rework1-M8 | **검출 실패 → 보강**: verifier 변이 M8(`hints` 미전달)이 기존 36건을 모두 통과(`36 passed`)해 보류(R-35-2) → 재작업 1차에서 이 테스트 신설, M8 검출 · `review-FIX-035.md` §2 #3·4절 |
| test_er_pipeline.py::test_resolve_identity_single_candidate_question_wording_fix035 | 후보 1명이면 identity 질문 문구가 `<이름> 님이 맞으실까요?` | 후보 김민수 1명 → `"팀장" -- 김민수 님이 맞으실까요?` (옵션·`candidate_ids`·긍정 목록 불변) | 통과 · FIX-035-M4 | 기록 없음 |
| test_tools_context.py::test_amend_trace_output_adds_keys_persists_and_refuses_overwrite_fix035 | (재작업 1차 R-35-1) trace 부분 갱신 헬퍼 `amend_trace_output` 의 계약 | `output={"a":1}` 행에 `{"b":True,"c":7}` → DB 재조회로 `{"a":1,"b":True,"c":7}`·`{"a":2}` 는 `ValueError` 이고 `a` 불변·`trace_id=None`/없는 id → `False` | 통과 · M6a · M6b · M6c | 기록 없음 (재작업 1차에서 신설) |

### U10 사람 점검 — FIX-035 실서버 확인 (메인 세션이 Chrome 직접 조작, 2026-10-16, 수동 6건 — 위 총계·집계에 넣지 않는다)

자동 테스트가 아니라 실서버(:8000)·실 LLM·Chrome 154.0.8037.99 에서 사람처럼 눌러 본 기록이다. 코드 `735f391`. 단계별 화면·DB·trace 상세는 `evidence/20261016-1915-u10-check-chat-fix035.txt`, DB 조회 원본은 `evidence/20261016-1911-u10-fix035-db.txt`.

| 시나리오 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| U10-F35-A 거절 → 직장 | identity 거절 뒤 후속 new_person 질문, 태그 선택 시 인물·사건 생성(D1) | `오늘 박선영 과장님이랑 회의했는데 다음 달에 팀을 옮기신대` → q12 identity(후보 3명) → 거절 → q13 new_person 칩 6개 → `직장으로 기억할게요` → persons 10·events 29(raw 원문 그대로) | 통과 · trace 374 `identity_rejected=true`·`followup_question_id=13` · 380 create_person · 382 add_event | 없음 (수동 점검) |
| U10-F35-A3 동시 두 번 답 | 같은 질문에 두 탭이 동시에 답하면 한 번만 처리 | 사용자 탭과 메인 세션 탭이 q12 거절을 거의 동시에 보냄 → 하나는 200, 하나는 409 "이미 답했거나 만료된 질문이에요." | 통과(의도된 409) · 서버 로그 `POST /answers/12` 200 → 409 | 사용자의 실수 클릭으로 우연히 확인됨 |
| U10-F35-A4 새로고침 복원 | 다른 탭에서 생긴 대기 질문이 새로고침 뒤 복원되는가 | F5 → q13 질문·칩 6개 표시 | 통과 | 없음 (수동 점검) |
| U10-F35-A6 카드·원문 | 새 인물 카드와 원문 펼치기 | `#/persons/10` → `직장 · 동`, 타임라인 `meeting 팀을 옮기신다` → [원문 펼치기] = events 29 raw_utterance | 통과 | 없음 (수동 점검) |
| U10-F35-B 거절 → 아니요 | 후속 질문에서 "아니요" 면 생성 0 | `어제 박선희 과장님이 커피를 사주셨어` → q14 identity → 거절 → q15 new_person(새로고침 없이 표시) → `아니요` → 생성 0, persons 10 그대로 | 통과 · trace 396 `identity_rejected=true`·`followup_question_id=15` · 403 stored 전부 0 | 없음 (수동 점검) |
| U10-F35-C 새 인물 재사용 | FIX-035 로 만든 인물이 다음 발화에서 찾아지는가 | `선영 과장님이 오늘 점심을 사주셨어` → 질문 없이 person 10 으로 병합, 별칭 `선영 과장님` 누적, events 30 | 통과 · er_resolve 407 merge confidence 0.8654 ≥ 0.8 | 없음 (수동 점검) — 원래 의도(후보 칩 선택 회귀)는 자동 병합돼 확인 못 함 |

실서버에서 확인하지 못한 것: 후보 1명 문구(개발 DB 인물 10명이라 후보가 늘 3명) — 자동 테스트 `test_resolve_identity_single_candidate_question_wording_fix035` 로만 확인. 관찰(후속 후보): 인물을 새로 만든 턴의 응답이 "이벤트 1건" 만 말하고 인물 생성은 말하지 않는다.

### U10 화면 점검 수정 1회 — 인물 화면 정렬 (자동 2건, 위 총계·집계에 넣지 않는다)

사용자 지시(2026-10-16, CR-003 §3 ⑥)로 규칙을 정했다: 목록은 본문 폭 전체(왼쪽부터), 상세(`#/persons/:id`)는 가운데·폭 본문의 75%(`md:w-3/4`)·모바일 100%(`w-full`). 증거: `evidence/20261016-1933-u10-fix-card-align2-{typecheck,vitest,build,e2e}.txt`(vitest 137 passed), 변이 `20261016-1934-u10-fix-card-align2-mutation.txt`. 네트워크 0(가짜 fetch).

| 테스트 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| card.test.tsx::목록 상태는 본문 폭 전체를 쓰고 가운데 정렬·폭 상한이 없다 | 목록 상태 section 클래스 | `[data-screen="persons"]` 에 `mx-auto`·`max-w-*`·`md:w-*` 없음, `card-wrap` 없음 | 통과 · 변이(section 에 `mx-auto` 추가) 검출 | 없음 (집계 제외) |
| card.test.tsx::상세 상태는 가운데 정렬이고 폭이 본문의 75%(md 이상), 모바일은 100% 이다 | 상세 카드 래퍼 클래스 | `card-wrap` 에 `mx-auto`·`w-full`·`md:w-3/4` 있고 `person-card` 를 감쌈, section 에는 `mx-auto` 없음 | 통과 · 변이(래퍼에서 `mx-auto` 제거) 검출 `1 failed \| 30 passed` | 없음 (집계 제외) — verifier 공백 탐침 M4(목록 안쪽 `mt-4` div 에 `mx-auto max-w-3xl`)는 생존, R-U10C-3 → P8b 보강 |

### U10 사람 점검 — 29~32행 마무리 (메인 세션이 Chrome 직접 조작, 2026-10-21, 수동 8건 — 위 총계·집계에 넣지 않는다)

사용자 지시 "너가 직접 해줘"(2026-10-21)로 01-plan 의 "사용자 확인 문장"(⑤⑧⑫)을 **메인 세션 확인 문장**으로 대신했다. 코드 `75cb4ad`(제품 코드는 `3bd5025`), 실서버 :8000 · 실 LLM(gpt-4o-mini) · 이 Mac 의 Chrome 156.0.0.0, 데스크톱 1710×862 · 모바일 폭 500×667(Chrome 창 최소 폭 — 390 은 불가, 390 은 Playwright E2E 가 덮는다), 어두운 모드만(밝은 모드는 OS 설정을 바꾸지 않아 **미확인**). 서술 `evidence/20261021-2040-u10-check-{chat,card,briefing,screens}.txt`, DB·API 원본 `-2033-u10-check-chat-db.txt` · `-2029-u10-check-card-db.txt` · `-2028-u10-check-briefing-run.txt` · `-2029-u10-check-briefing-db.txt`.

| 시나리오 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력 |
|---|---|---|---|---|
| U10-29 확인 칩 왕복 | 29행 ①~⑤ — 칩이 응답 아래 한 줄, 누른 칩 선택 상태, DB 답 기록 | `오늘 동호회에서 지수랑 처음 인사했어` → q16 identity 칩 3개 → `아니요, 다른 사람이에요` → q17 new_person 칩 6개(FIX-035) → `지인으로 기억할게요` → 인물 11 `지수`(지인·동)·사건 32 | 통과 · q16/q17 answer·answered_at · loop_resume 449 `identity_rejected=true`·`followup_question_id=17` · 사이드바 즉시 갱신 | 없음 (수동 점검) |
| U10-29b 자동 병합 관찰 | 확정 별칭 단독 언급의 귀속 | `오늘 과장님이랑 오후에 커피 마셨어` → 질문 없이 인물 9 에 사건 31 | 통과(설계대로: er_resolve 432 merge 0.95, 별칭 `과장님` 정확 일치) — **관찰**: DB 에 `박선영 과장님` 도 있어 일반 호칭 별칭의 단독 귀속은 오병합 위험(원칙1), FIX/CR 후보 | 없음 (수동 점검) |
| U10-30 카드 원문 | 30행 ⑥~⑧ — 펼친 원문 = DB raw_utterance, 근거 보기 1회 조회 | 인물 9 → 타임라인 사건 28 `⌄` → `GET /api/events/28/raw` 1회 → 원문 / 사실 24 `근거 보기` → `GET /persons/9/facts/24/sources` → 근거 2건(28·27) | 통과 · 화면 원문 = DB `오늘 회사에서 박선우 과장님이랑 점심 먹었는데 다음 주에 이사 간대` 글자 단위 일치 · 다시 펼쳐도 재요청 0 | 없음 (수동 점검) |
| U10-31 브리핑 생성·대조 | 31행 ⑨⑩ — 화면 머리줄·사실 줄·제안 = `briefing_compose` trace output | `내일 저녁 7시에 박선우 과장님이랑 저녁 약속 있어` → 일정 6(10-22 19:00 KST) → `POST /briefings/run`(수동 — 저장된 브리핑 0 이면 화면에 "지금 브리핑" 버튼이 없음) → trace 427 | 통과 · 머리줄 `📌 2026. 10. 22. 오후 7:00 · 박선우 과장님 · 저녁 약속` · 줄·제안 글자 그대로 · 불일치 0 · run 428 trigger manual | 없음 (수동 점검) — 관찰: 열어 둔 브리핑 화면은 자동 갱신 없음(설계), 배너 "브리핑 보기" 로 재조회 |
| U10-31b 푸시 발송·수신 | 31행 ⑪ — 제품 화면 구독으로 `push "sent"`, 수신 | 구독 2행(id 1·3, 호스트 fcm.googleapis.com, "알림 켜짐") → run 응답 `push: "sent"` → 같은 탭에 앱 안 배너 `새 브리핑 알림이 도착했어요.` → `브리핑 보기` → `#/briefings?schedule_id=6` 카드 강조 | 통과 | 없음 (수동 점검) |
| U10-31c OS 알림 클릭 | 31행 ⑫ — 알림을 눌러 그 일정이 열리는가 | OS 알림 클릭 → `#/briefings?schedule_id=6` | **미확인** — 확장이 OS 알림을 누를 수 없다. sw.js `notificationclick` 은 22행 자동 테스트·P7 U8(사용자 실클릭 10-10)로만. 사용자가 하려면 카드 `지금 브리핑` 재발송 뒤 알림 클릭 | 없음 (수행 안 함) |
| U10-32 화면 점검 20항 | 32행 — 체크리스트 1~20, 데스크톱·모바일 폭, 어두운 모드 | 항목별 통과/부분/미확인 + 한 줄 의견 (`-2040-u10-check-screens.txt`) | 통과 17 · 부분 3(7 로딩·오류 안내 손으로 미재현 / 12 모바일 소프트 키보드 미확인 / 15 "새 메시지" 표시 미재현 — 셋 다 자동 테스트로는 닫힘) · 밝은 모드 미확인 · **수정 반영 횟수: 1**(10-16 정렬), 새 "수정 필요" 0 | 없음 (수동 점검) |
| U10-32b 가로 스크롤·폭 수치 | 10항·2항 — scrollWidth = clientWidth, 글자 16px, 카드 폭 | JS: 데스크톱 1710/1710 · 모바일 500/500 · body font 16px · 모바일 카드 452px(=본문 100% − 여백) · 데스크톱 상세 `card-wrap` 75% | 통과 | 없음 (수동 점검) |

### 실패 이력 집계

| 구분 | 행 수 | 비고 |
|------|------|------|
| 실제 실패 | 5 | 프론트 4행: `card` 항목 링크(테스트 쪽 오류, 1회) · `card` R-U6-1 · `card` R-U6-2 두 건(셋은 verifier 탐침 P3·P2 가 전신) / 백엔드 1행: `briefings_e2e` 9행 테스트(처음 쓴 직후 첫 실행) |
| 검출 실패 → 보강 | 18 | 프론트 10행: proxy 4 · chat 칩 1 · card P2c 1 · briefing 강조 1 · briefing P4 1 · push R-U8-1 1 · E2E card 데스크톱 1 / 백엔드 7행: U1 `last_contact` 관련 4 · 쓰기 0 U1·U2 2 · 조작된 trace(verifier V2, R-U9b-1) 1 / FIX-035 1행: 힌트 위계 보존(verifier M8, R-35-2) |
| 보류·재작업 | 4 | 프론트 `routes.test` 서랍 4행(R-U4-1) |
| 동작 틈 → 보강 | 1 | 프론트 `card` R-U6-2 "앱을 열면 1회" |
| 기록 없음 | 182 | 나머지 (P8 176 + FIX-035 6) |
| 합계 | **210** | 5 + 18 + 4 + 1 + 182 = 210 = 프론트 135 + E2E 4 + 백엔드 64 + FIX-035 7 |

세는 법: 이 파일에서 `grep -c "^| .*| \*\*실제 실패\*\*" tests.md` → 5, `… \*\*검출 실패 → 보강\*\*` → 18, `… \*\*보류·재작업\*\*` → 4, `… \*\*동작 틈 → 보강\*\*` → 1, `grep -c "^| .*| 기록 없음" tests.md` → 182. 이 숫자는 "CI·변이 검출 외에 개발 중 실제로 기록된 것"만 센 것이며, **기록에 남지 않은 실패는 센 수 없다** — 특히 FIX-034(2026-10-13) 이전의 증거 파일(U1~U4)은 사람이 옮겨 적은 것이라 중간 실패 실행이 빠져 있을 수 있다.
