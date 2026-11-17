# P9b-auth U13 커밋 전 코드 리뷰 — "AI 연결" 화면(`#/connect`)·사이드바 진입 버튼·MCP 토큰 클라이언트 (CR-008 축소안 · D19)

검토자: verifier (fable) | 일시: 2026-11-17 23:32 | 대상: dev2 HEAD `f9f0097` + 미커밋 작업 트리 중 `web/` 8파일(수정 6 · 새 파일 2)
결과: 통과
판정: **통과**. 열린 [필수] 0 · 열린 [권고] R-1~R-6.
범위 밖(보지도 판정하지도 않음): `app/`·`alembic/`·`tests/`·배포 파일의 미커밋 변경(백엔드 U12 진행 중). 백엔드 pytest 는 돌리지 않았다. 서버가 "API 계약 — 개정 4" 표대로 응답하는지(201 본문 키·`Cache-Control: no-store`·204)는 U12 리뷰와 U14 로컬 Caddy 스모크의 몫이다 — 이 리뷰는 프론트가 그 표를 맞게 부르고 읽는지만 본다. `tests.md`·`registry.md` 는 U13 절·행만 읽었다.

## 1. 본 것

- 계약: `01-plan.md` 개정 4 — "API 계약 — 개정 4"(231~243행) · "AI 연결 화면 고정 문구"(266~299행, `CONNECT_NOTICE` 27행·명령 문자열·시각 표기) · U13(589~608행, 변이 V13-1~8) · 고치는 파일 표(183행) · 범위 축소 순서(627~628행). `decisions/D19-mcp-read-token.md`(결정 2·파급 "제3자 개인정보"·지킬 것 1·7). `security.md` §1 MCP 토큰 행(17행)·71행.
- 변경: `git diff -- web/` 6파일(86 추가 · 3 삭제) 전부 + 새 파일 `web/src/screens/ConnectScreen.tsx`(194행)·`web/src/__tests__/connect.test.tsx`(263행) 전문. 삭제 줄 전수(`git diff -U0 -- web/src/__tests__ web/e2e`).
- 주변: `web/src/api/client.ts` `apiFetch`(본문 없으면 `Content-Type` 미설정·204 → `undefined`·401 신호) · `web/src/components/AppShell.tsx` 전문 · `web/public/sw.js`(fetch 처리기·캐시 0 — 서비스 워커가 발급 응답을 붙잡지 않는다).
- 구현자 증거(출력만): `evidence/20261117-2324-u13-{typecheck,vitest,lint,build,e2e}.txt` · `20261117-2325-u13-mutations.txt`.

## 2. 직접 실행한 명령과 결과

| 명령(접두 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> --`) | 결과 | evidence |
|---|---|---|
| `npm --prefix web run typecheck` | exit 0 | `20261117-2329-verifier-u13-typecheck.txt` |
| `npm --prefix web exec -- vitest run --root web` | 11파일 · **224 passed** · 실패 0 (구현자 증거 224 와 같다. 기준선 212 + 새 12 = `connect.test.tsx` 11 + `api.test.ts` 1) | `20261117-2329-verifier-u13-vitest.txt` |
| `npm --prefix web run lint` | exit 0 (경고만 — 새 파일의 경고 2건은 기존 화면 파일들과 같은 `only-export-components`) | `20261117-2329-verifier-u13-lint.txt` |
| `npm --prefix web run build` | exit 0 | `20261117-2329-verifier-u13-build.txt` |
| `npm --prefix web run e2e` | **5 passed** (구현자 증거 5 와 같다) | `20261117-2329-verifier-u13-e2e.txt` |
| 문구 대조 `notice_diff.py <01-plan.md> <ConnectScreen.tsx>` | 계획 27키 · 구현 27키 · 키 순서 같음 · **불일치 0건** · 명령 문자열 템플릿이 구현에 글자 그대로 있음 | `20261117-2330-verifier-u13-notice-diff.txt` |
| 변이 대조군(작업 트리 사본, 무변이) | 224/224 | `20261117-2330-verifier-u13-mut-control.txt` |
| 변이 11건 | 검출 6 · 생존 5 (아래 표) | `20261117-2330-verifier-u13-mut-mutants.txt` |
| 탐침 7건(무변이 구현에 새 시험을 더해 실행) | 231/231 — 구현은 일곱 경우 모두 옳게 동작 | `20261117-2331-verifier-u13-mut-probes.txt` |
| 탐침을 넣은 채 생존 변이 M7·M8·M9·M10·M5 | M7·M8·M9·M10 검출(탐침 P1·P2·P3·P5), M5 는 여전히 생존 | `20261117-2332-verifier-u13-mut-probes-vs-mutants.txt` |

변이·탐침은 스크래치패드 사본 `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/u13-verifier/web/` 에서만 했다(실행기 `…/u13-verifier/mutate.py`, 탐침 `…/u13-verifier/probe.test.tsx`, 치환 뒤 원복. 사본에 `.env` 계열 미포함 — `rsync --exclude '.env*'`). 실행 뒤 `diff -rq`(저장소 `web` ↔ 사본, `node_modules`·`dist` 제외) 차이는 제외한 `.env.example` 과 사본의 탐침 파일 둘뿐, `git status --short -- web` 8줄 그대로 — 저장소 무수정. 시험 토큰은 가짜 문자열이고 증거 파일에 실리지 않았다.

### 변이 표

| # | 변이 | 구현자가 돌렸나 | 결과 | 잡은 시험 / 비고 |
|---|---|---|---|---|
| M1 | 발급 뒤 토큰을 `localStorage` 에 저장 | 아니오(구현자는 `sessionStorage`) | 검출 — 1 failed | ⑤ |
| M2 | 토큰을 주소 해시에 씀(`#/connect?t=…`) | 아니오 | 검출 — 1 failed | ⑤ `location.href` |
| M3 | 발급 응답을 `console.log` | 아니오 | 검출 — 1 failed | ⑤ console 5종 |
| M4 | 만료 상태에서도 폐기 버튼 | 아니오 | 검출 — 1 failed | ② 만료 |
| M5 | `useRef` 동기 가드만 제거(`disabled` 는 유지) | 아니오 | **생존**(탐침 뒤에도) | `disabled` 가 같은 일을 한다 — 가드는 방어용 중복 → R-4 |
| M6 | 폐기 뒤 토큰 표시를 지우지 않음 | 아니오 | 검출 — 1 failed | ⑦ |
| M7 | `GET` 응답에 `token` 이 있으면 화면에 그림 | 아니오 | **생존** → 탐침 P1 이 검출 | `GET` 응답을 읽어 토큰 칸에 넣는 길을 막는 시험이 없다 → R-1 |
| M8 | `GET` 실패 때 로딩에서 멈춤 | 아니오 | **생존** → 탐침 P2 가 검출 | `GET` 실패 갈래를 지나는 시험이 없다 → R-2 |
| M9 | `getMcpToken` 이 401 관문 신호를 끔 | 아니오 | **생존** → 탐침 P3 이 검출 | 세 함수의 401 → 관문을 고정하는 시험이 없다 → R-2 |
| M10 | 토큰을 `title` 속성에도 둠 | 아니오 | **생존** → 탐침 P5 가 검출 | ⑤ 는 storage·주소·콘솔만 본다(계획 문장 그대로) → R-1 |
| M11 | 발급 뒤 상태 줄을 갱신하지 않음 | 아니오 | 검출 — 3 failed | ③ · ⑦ · ⑨ |

구현자 변이(V13-1~8 + 3종)는 증거 `20261117-2325-u13-mutations.txt` 에서 전부 실패 ≥ 1 — V13-6·V13-7 은 계획이 지목한 기존 시험(`auth.test.tsx`·`routes.test.tsx`)도 함께 잡았다.

## 3. 판정 근거 (요청 항목 순서)

1. **범위**
   - `git status --short -- web/` 8줄 = 계획 183행·166행의 파일 목록과 정확히 같다(`routes.ts`·`App.tsx`·`AppShell.tsx`·`api/types.ts`·`api/client.ts`·`__tests__/api.test.ts` + 새 `ConnectScreen.tsx`·`connect.test.tsx`). `web/e2e`·`package.json`·`package-lock.json`·lint 설정 변경 0.
   - 기존 단언: `git diff --stat -- web/src/__tests__/auth.test.tsx web/src/__tests__/routes.test.tsx web/src/__tests__/card.test.tsx web/e2e` 출력 0줄. 시험 파일의 삭제 줄은 `api.test.ts:2` import 한 줄뿐(이름 셋을 더하느라 여러 줄로 나눔 — 단언 아님). 닫힌 목록 "없음(0)" 과 맞는다.
   - `NAV_ITEMS`: diff 에 없음(3항목 그대로). 진입점은 `<button type="button" data-testid="sidebar-connect">` 이고 `<AccountRow />` 바로 위·`sidebar-account` 밖 — 계획 593행 그대로. 누르면 `window.location.hash = HREF.connect` 뒤 `onNavigate()`.
   - 계획에 없는 추가: 문구·testid·화면·의존성 0. `export function mcpCommand` 는 명령 문자열을 한 곳에서 만드는 도우미(화면과 복사가 같은 문자열을 쓴다).
2. **계약**
   - 문구 27개: 스크립트 대조 불일치 0건(위 증거) + 눈으로 `intro`·`onceNotice`·`revoked`·`commandLabel` 재확인. `copyToken`·`copyCommand` 는 `aria-label`, 보이는 글자는 `copy` — 표의 주석과 같다.
   - 명령 문자열: `ConnectScreen.tsx:44` 가 계획 298행 템플릿과 글자 그대로이고 호스트는 `window.location.origin`. `relmemo.com`·`sslip` 문자열은 `web/src` 에 없다. 시험 ③ 이 jsdom origin 으로 정확 일치를 단언한다(구현자 V13-2·V13-5 검출).
   - API: `getMcpToken` `GET /auth/mcp-token` · `createMcpToken` `POST`(본문 없음 — `api.test` 가 `body: undefined` 단언) · `deleteMcpToken` `DELETE`(204 → `undefined`). 셋 다 기본 `apiFetch`(`signalUnauthorized` 미지정 = 401 이면 관문 신호). `RequestOptions.method` 에 `DELETE` 만 더했고 `apiFetch` 본체 diff 0.
   - 응답 키: `McpTokenCreatedOut{token, created_at, expires_at}` · `McpTokenStatusOut{active, created_at, expires_at, last_used_at}` — 계약 표 235~236행·계획 590행과 같다. 화면은 `active`·`expires_at`·`last_used_at` 과 발급 응답의 `token`·`created_at`·`expires_at` 만 읽는다.
   - 상태 세 갈래: `active` → `statusActive` + 만료 + 마지막 사용(`null` 이면 `neverUsed`) / `active:false` + `expires_at` 있음 → `statusExpired` / 그 밖 → `statusNone`. 시각은 `new Date(x).toLocaleString('ko-KR')` 를 이 파일 안 함수로만(기존 표기 함수 무변경).
3. **토큰 취급(결정 AZ · security §1)**
   - 토큰이 닿는 곳은 `useState` 의 `token` 하나, 그 값을 그리는 `<code>` 두 곳(토큰·명령), `navigator.clipboard.writeText` 호출 둘 — 그뿐이다. `ConnectScreen.tsx` 에 `console.`·`localStorage`·`sessionStorage`·`title=`·`document.cookie`·`history`·모듈 수준 변수 쓰기 0(grep — 일치한 것은 3행 주석 한 줄). `aria-label` 은 고정 문구다.
   - 탐침 P5: 만든 뒤 문서 전체 HTML 에서 토큰 출현은 정확히 2회(두 `<code>` 글자)이고 어떤 요소의 속성 값에도 없다.
   - 화면을 떠나면: `App.tsx` 가 `route.name === 'connect'` 일 때만 그리므로 다른 경로로 가면 컴포넌트가 내려가고 state 가 사라진다(시험 ⑥, 구현자 V13-3 검출). 401 로 관문이 뜨면 앱 틀째 내려간다(탐침 P3). 다시 만들면 옛 토큰 글자는 문서에서 사라진다(탐침 P7).
   - `GET` 응답에 `token` 이 섞여 와도 그리지 않는다(탐침 P1) — 화면은 `GET` 결과를 `status` 에만 넣는다.
   - 서비스 워커(`web/public/sw.js`)에 `fetch` 처리기·`caches` 사용이 없다 — 발급 응답이 브라우저 캐시 저장소에 남는 길이 프론트 쪽에는 없다(서버 `Cache-Control: no-store` 는 U12 몫).
   - 외부 전송 고지: `privacy` "조회한 내용은 연결한 AI 도구의 회사로 전송돼요." 가 상태와 무관하게 항상 화면 위쪽에 그려진다(`ConnectScreen.tsx:124`, 시험 ① 이 단언). D19 파급·security 71행의 "AI 연결 화면에 고지" 를 채운다. `onceNotice` 는 토큰이 보일 때 함께 나온다.
   - 클립보드가 없거나(비보안 출처) 거부되면 `try` 안에서 잡혀 `copyFailed` 로 간다 — 계획 "실패·없음 → `copyFailed`".
4. **구현자가 보고한 "계획과 달라진 점" 5가지**
   - (가) 처음 `GET` 로딩 중 버튼 숨김: 계획 "들어오면 `getMcpToken()` 1회(그동안 `loading`)" 의 범위 안. 상태를 모르는 채 `create`/`recreate` 중 하나를 골라 보이지 않으므로 더 안전하다(상태를 모르는 동안 누르면 살아 있는 토큰이 경고 없이 밀려난다). 충돌 없음.
   - (나) `GET` 실패 → `failed` 한 줄 + 상태 "없음": 계획 "실패(401 제외) → `failed`(`role="alert"` 한 줄)" 를 따랐고 새 문구가 없다. 탐침 P2 로 동작 확인(다음 발급이 성공하면 alert 가 사라진다). 다만 실제로는 토큰이 있는데 조회만 실패한 경우 화면이 "연결 토큰이 없어요." 라고 말하고 `recreateWarn` 없이 `create` 를 보인다 — 사실과 다를 수 있는 한 줄이다. 계획이 이 경우의 상태 줄을 정하지 않았고 alert 가 함께 보이므로 범위 안으로 판정하되 R-3 으로 남긴다.
   - (다) `revoke` 는 `active` 일 때만: 계획 "활성 토큰이 있거나 방금 만들었으면 `revoke` 버튼" 그대로다(방금 만들면 `status.active = true`). 만료 행은 화면에서 지울 수 없지만 이미 무효이고 새로 만들면 덮인다. 충돌 없음(M4 가 이 경계를 검출).
   - (라) `useRef` 동기 가드: 계획 "진행 중 버튼 `disabled`" 를 지키는 구현 수단에 더한 방어. 계약·문구·요청 수에 영향 0. 충돌 없음. 시험으로는 구별되지 않는다(M5 생존, R-4).
   - (마) lint 실행 추가: 계획 판정 목록(typecheck·vitest·build·e2e)보다 하나 더 돌린 것 — 제품 변경이 아니다. 충돌 없음.
   - 다섯 가지 모두 `03-log.md` 에 아직 없다(`grep -n "U13" 03-log.md` 0행) → R-5.
5. **원칙5·7** — 새 화면의 근거가 파일 머리 주석과 계획 594행에 있다(토큰 43자·명령 약 150자를 둘 자리). 채팅방 목록·상담·쓰기 기능 추가 0. 화면이 만드는 문장은 `CONNECT_NOTICE` 고정 문구뿐이고 서버 문장을 그리지 않는다(`dangerouslySetInnerHTML` 0).

## 4. 소견

[필수] 없음.

[권고] (전부 커밋·배포를 막지 않는다. 평가 뒤 정리해도 된다.)

- **R-1 토큰 누출 시험의 폭** — 시험 ⑤ 는 계획 문장대로 storage·주소·콘솔만 본다. `GET` 응답의 `token` 을 그리는 변이(M7)와 토큰을 요소 속성에 두는 변이(M10)가 살아남는다. 탐침 P1(`GET` 에 `token` 이 섞여 와도 문서에 없음)·P5(문서 전체에서 토큰 출현 2회·속성 0)에 해당하는 시험 둘을 `connect.test.tsx` 에 더하면 닫힌다. 현재 구현은 두 탐침을 통과한다.
- **R-2 `GET` 실패·401 갈래 시험 없음** — `GET` 500(M8)과 401 관문(M9)을 지나는 시험이 없다. 탐침 P2·P3 에 해당하는 시험을 더하면 닫힌다. 현재 구현은 통과한다. `DELETE` 실패(탐침 P4 — `failed`, 토큰·활성 상태 유지)도 같은 자리에 더할 만하다.
- **R-3 `GET` 실패 때 상태 줄 "연결 토큰이 없어요."** — `ConnectScreen.tsx:70` 이 실패를 `NONE` 으로 바꿔 그린다. 토큰이 실제로 있는 계정이면 사실과 다른 문장이고, 그 상태에서 `create` 를 누르면 `recreateWarn` 없이 살아 있는 토큰이 밀려난다. 시연에서는 `failed` alert 가 함께 보이므로 위험은 작다. 고친다면 실패 때 상태 줄을 그리지 않는 쪽(새 문구 불필요)이고, 계획이 정하지 않은 동작이라 architect 결정 한 줄이 필요하다.
- **R-4 `useRef` 가드는 시험으로 구별되지 않는다** — M5 생존. `disabled` 와 같은 일을 하는 방어용 중복이라 그대로 둬도 되고, 남긴다면 03-log 에 "방어용, 시험 없음" 을 적어 둔다.
- **R-5 03-log 에 U13 기록 없음** — 계획과 달라진 점 5가지(3절 4항)·기준선 212 → 224·증거 파일 이름을 `03-log.md` U13 절에 적는다(계획 597행 "03-log", 메인 세션 몫). `tests.md` U13 절(438행~)과 `registry.md` 309~310행은 이미 있다 — 310행의 "U13 커밋" 자리는 커밋 뒤 해시로 바꾼다.
- **R-6 진입 버튼에 현재 위치 표시 없음** — `#/connect` 에 있어도 `sidebar-connect` 는 nav 링크처럼 강조(`aria-current`)되지 않는다. 계획이 요구하지 않았고 UI 에 시간을 쓰지 않는다는 원칙5 범위라 그대로 둬도 된다.

## 5. 이 리뷰가 보증하지 않는 것

- 실제 백엔드(U12)와 붙였을 때의 동작 — 모든 시험은 계약 표 모양의 가짜 응답으로 돈다. `POST` 가 Origin 검사에 걸리지 않는지, 201 본문 키, 204 는 U14 로컬 Caddy 스모크·로컬 브라우저 점검이 판정한다.
- 화면의 명령을 실제 Claude Code 에 붙였을 때 연결되는지(U14 사용자 할 일 13).
- 모바일 폭에서의 모양(긴 토큰·명령은 `break-all` 로 줄바꿈되게 돼 있으나 눈으로 보지 않았다).
