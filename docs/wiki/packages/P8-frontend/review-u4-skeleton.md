# P8-frontend U4 프론트 골격·디자인 토큰·도구·CI — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 (재검증 2차, 2026-10-12 23:40) — 1차 [필수] R-U4-1 이 닫혔다: 서랍이 shadcn `Sheet`(Radix Dialog, `side="left"`)로 바뀌어 01-plan 346행을 충족하고 367행 불변식 10 grep 이 `web/src/components/AppShell.tsx` **1파일**(`-recheck-invariant.txt`), 접근성은 탐침으로 실측(role=dialog 이름 "사이드바"·포커스 가둠·바깥 aria-hidden·Esc·포커스 복귀 — `-recheck-probe.txt`). 판정 명령 4개 재실행 exit 0(24 passed, `-recheck-judge.txt`), 재검증 조건 변이 M3·M7·V4 전부 검출 + 1차 공백 V1 닫힘(`-recheck-mutation.txt`), 새 패키지 0(`package.json`·lock 바이트 동일), 1차 [권고] 6건(R-U4-2·3·5·6·7·9) 닫힘, 2건(R-U4-4·8)은 사용자 결정으로 U8·U9 이월. 새 소견은 [권고] 3건(R-U4-11 `proxy.test.ts` 기본 대상 단언의 환경 의존 — 실측 E1 · R-U4-12 서랍 폭 384px vs 고정 사이드바 256px · R-U4-13 registry 잔존 문구 2곳)이고 커밋을 막지 않는다. **[필수] 0.** 1차 판정 원문은 아래에 그대로 남긴다(§1~§11), 2차 근거는 §12.
결과(1차, 21:30): 보류(재작업 필요) — [필수] 1건: 결정 N 서랍이 기성 컴포넌트(shadcn Sheet 류)가 아니라 직접 구현(`Sidebar.tsx` 78~93행, `role="dialog"` 소문자·`aria-modal` 없음·포커스 가둠 없음)이라 01-plan 346행 "서랍은 shadcn/ui 의 Sheet(Radix Dialog 기반) 같은 기성 컴포넌트로 만든다" 와 어긋나고, 그 결과 01-plan 367행 불변식 10(`grep -rlE "Sheet|Dialog|Drawer"` → "1파일뿐")이 **0파일**이 되어 U9 자동 판정이 계획대로 통과할 수 없다(evidence `-grep.txt` 2차 실행 첫 항목). 03-log 의 계획 밖 판단 ①~⑪ 에도 이 항목은 없다(미보고). 그 밖은 통과 수준이다: 판정 명령 4개 재실행 exit 0(20 passed · 빌드 해시 동일), R-U0-3 ①~⑤ 전부 충족(`^`·`~` 0 · `cn@0.4.0` shadcn 공식 · `shadcn` `"dev": true` · `npm audit --omit=dev` 0 · install 스크립트는 `fsevents` 뿐), 01-plan 95행 계약 항목 전부 충족, TS 타입 32모델 중 31개 필드 전수 일치(어긋남 0, `HealthOut` 만 의도적 생략), 내가 돌린 변이 5건 중 4건 검출·1건(프록시 `rewrite`) 테스트 공백, 보안·범위 위반 0. [권고] 9건.
대상: 작업 트리(기준 HEAD `95ca2c0`) — 신규 `web/` 37파일(`git status --short --untracked-files=all | grep '^?? web/'`, node_modules·dist 제외 — 목록은 `-grep.txt`) · `.github/workflows/tests.yml`(`git diff --numstat` `25 0`, hunk 1개) · `docs/wiki/registry.md` U4 행 7개 · 구현 증거 `evidence/20261012-20{23,25,26,30,31,32}-u4-*.txt` 7개. `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U4 시작" 항목만 근거 문서).
근거 문서: `01-plan.md` 95행(U4) · 19~32행(범위·결정 B·C·L·N) · 36~49행(하지 않는 것) · 52~80행(파일 목록) · 229~234행(결정 B) · 236~254행(결정 C) · 289~293행(결정 I) · 295~299행(결정 J) · 305~328행(결정 L) · 330~346행(결정 N) · 355~367행(불변식 1~10) · `03-log.md` 2026-10-12 20:40 항목(메인 세션 해석·1차 결과·계획 밖 판단 ①~⑪·사용자 결정 2개) · `.claude/agents/frontend-agent.md` "하지 말 것" 1~7 · `review-u0-harness.md` §6·R-U0-3 · `app/api/schemas.py` 전체 · `docs/wiki/security.md` §3·§5 · `docs/wiki/verification.md` "변이 시험 방법" · `.github/workflows/tests.yml` 기존 `pytest`·`windows` job · CLAUDE.md 원칙5·7 · `02-plan-verify.md` R-4·N-2.

내 증거(전부 출력 전체, Write 로 저장):
- `evidence/20261012-2037-verifier-u4-judge.txt` — `npm ci` · `npm run typecheck` · `npm test -- --run` · `npm run build` 각각 따로 실행, 전부 exit 0.
- `evidence/20261012-2038-verifier-u4-deps.txt` — `npm ls --depth=0` · `npm audit --omit=dev`(0) · `npm audit`(dev 포함 7 high, 전부 shadcn CLI 경로) · `npm view cn@0.4.0/radix-ui@1.8.0/tw-animate-css@1.4.0/shadcn@4.21.4 repository` · lock 의 shadcn 항목 · `npm install-scripts ls` · lock 의 `hasInstallScript` · resolved 출처.
- `evidence/20261012-2038-verifier-u4-grep.txt` — push-dev · `https?://` · 글꼴/CDN · 스크립트의 셸 명령 · `^`/`~` · 음성 API · raw_utterance · `VITE_*KEY` · 불변식 10 grep(대소문자 구분/무시) · `AppShell` · localStorage · 템플릿 잔재 · favicon · `index.html` meta · `git diff --stat` · CI hunk 수 · `app/alembic/tests` 무변경 · 삭제 파일 · untracked 37 · `web/.gitignore` 효과.
- `evidence/20261012-2040-verifier-u4-mutation-1.txt` · `-2041-…-mutation-2.txt` · `-2042-…-mutation-3.txt` — V0 기준선 + 변이 V1~V5, 원복 확인.
- `evidence/20261012-2043-verifier-u4-types.txt` — 타입 대조 표 32행.

## 1. R-U0-3 고정 점검 (`-deps.txt` · `-grep.txt`)

| # | 항목 | 결과 | 근거 |
|---|---|---|---|
| ① | `scripts` 7개(dev/build/typecheck/test/e2e/lint/preview)에 셸 전용·삭제 명령 | 없음 | `grep -nE 'rm \|rimraf\|…'` 가 `build: "tsc -b && vite build"` 의 `&&` 1건만 — `&&` 는 npm 이 Windows 에서 쓰는 cmd.exe 에서도 동작, 환경변수 대입 문법 없음. 지우기는 `vite.config.ts` 19행 `emptyOutDir: true`(frontend-agent.md 6항 그대로) |
| ② | 의존성 25개 정확한 버전·출처 | 충족 | `grep -nE '"[\^~]' package.json` 0건. `cn@0.4.0` → `github.com/shadcn-ui/cn`, maintainer `shadcn` — 공식. `radix-ui@1.8.0` → `radix-ui/primitives` 모노레포. `shadcn@4.21.4` → `shadcn-ui/ui`. `tw-animate-css@1.4.0` → `Wombosvideo/tw-animate-css`(개인 저장소, MIT — shadcn init 이 기본으로 넣는 3자 패키지, 소견 R-U4-9). lock resolved 557건 전부 `registry.npmjs.org` |
| ③ | lock 동반·`shadcn` `"dev": true` | 충족 | lockfileVersion 3, 7483~7487행 `"node_modules/shadcn": … "dev": true` — 사용자 결정 (1) 반영 |
| ④ | `npm audit --omit=dev` | 0건 재현 | dev 포함 7 high 는 `shadcn → @shadcn/registry → fast-glob → micromatch → braces`·`ts-morph` — CLI 내부, 번들 무관(구현자 분석과 일치) |
| ⑤ | install 스크립트 패키지 | `fsevents` 1개뿐 | lock `"hasInstallScript": true` 1건(`node_modules/fsevents`, macOS optional). `npm install-scripts ls` "No packages with unreviewed install scripts." |

## 2. 01-plan 95행 계약 대조

| 계약(95행) | 구현 | 판정 |
|---|---|---|
| 첫 명령 node/npm 버전 확인 | `-2023-u4-skeleton.txt` §0 `v24.21.0`·`11.19.0`(기대값 일치) | ✓ |
| Vite + React + TS(결정 B) | `package.json` vite 8.3.4·react 19.3.0·typescript 6.0.3, `tsconfig.app.json` strict | ✓ |
| Tailwind + shadcn/ui 초기화·토큰, npx 버전 고정·03-log 기록 | `create-vite@9.2.1`·`shadcn@4.21.4`(`-2026-u4-versions.txt`), 03-log 에 버전 목록 | ✓ |
| 토큰 밝은/어두운 두 벌(결정 L) | `tokens.css` 70~106행 `:root` · 108~144행 `@media (prefers-color-scheme: dark)`, 7행 `@custom-variant dark` — 토글 없음 | ✓ |
| 시스템 글꼴·웹 글꼴 없음·크기 4단계·4px 배수·경고색 | 12행 `--font-sans` 시스템 묶음(계획 324행과 같은 순서), 15~18행 4단계, 21~26행 4·8·12·16·24·32, 87행 `--warning`. `@fontsource`·`fonts.g*` 0건 | ✓ |
| 사이드바: 모든 폭 왼쪽, ≥1024 고정 / 미만 서랍, 항목 선택 시 닫힘, 하단 탭바 없음, 상태만 | `Sidebar.tsx` 8행 `(min-width: 1024px)`, 62~65행 고정 `aside`, 68~93행 메뉴 버튼+서랍, 90행 `onNavigate={close}`, 49~56행 Esc, 83행 배경 클릭, `localStorage` 제품 코드 0건, 탭바 없음. 테스트 "1024px 경계: 1023 은 서랍형, 1024 는 고정" | ✓ 동작 — 단 **기성 컴포넌트가 아님**(§4 ⑫, R-U4-1) |
| 해시 3경로 `#/chat`·`#/persons[/:id]`·`#/briefings`, 알 수 없는 해시 → chat | `routes.ts` 25~33행 `parseHash`, 45~52행 `useRoute`(null 이면 `replaceState(DEFAULT_HASH)`), 쿼리 제거 18~22행. 변이 V4·V5 검출 | ✓ |
| API 클라이언트: `/api` 기본, `X-Session-Id`, 오류 규약 타입 | `client.ts` 4·5행 상수, 45행 헤더, 8~23행 `ApiErrorBody`/`ApiError(status, code)`. 변이 V2 검출, 구현자 M4·M6 검출 | ✓ |
| 프록시 `VITE_API_TARGET` 기본 `http://localhost:8000`, `/api` 접두 제거 | `vite.config.ts` 10~11행 `loadEnv` → 기본값, 23~27행 `'/api': { target, changeOrigin, rewrite: p.replace(/^\/api/, '') }`, `.env.example` 한 줄 — 03-log 메인 세션 해석과 일치 | ✓ 코드 — 자동 테스트 없음(V1 살아남음, R-U4-3) |
| 빈 화면 3개 | `screens/{Chat,PersonCard,Briefing}Screen.tsx` 제목 `h1` 만(채팅/인물/브리핑), `App.tsx` 13~15행 라우트 3분기 | ✓ |
| Vitest + Testing Library + jsdom | devDeps vitest 5.0.4·@testing-library/react 16.3.3·jsdom 30.1.2, `vite.config.ts` 29~34행 `test`, 20건 통과 | ✓ |
| Playwright 설정만 | `playwright.config.ts`(testDir `./e2e`), `e2e/.gitkeep`, `e2e` 스크립트 `--pass-with-no-tests` exit 0(`-2023` §4), 브라우저 미설치 | ✓ (baseURL 5173 은 U9 에서 preview 포트로 바꿔야 함, R-U4-8) |
| `package-lock.json` 커밋 | untracked 목록에 있음(310 kB, lockfileVersion 3) | ✓ |
| `engines` | `"node": ">=24", "npm": ">=11"` — CI `node-version: 24` 와 일치 | ✓ |
| `.gitignore` | `web/.gitignore` 가 node_modules·dist·test-results·playwright-report·blob-report·`.env` 를 막음(untracked 에 node_modules/dist 0). 최상위 `.gitignore` 무변경(01-plan 80행 표는 최상위를 지목, 효과 동일 — R-U4-6) | ✓ |
| CI web job 두 OS, 기존 두 job 무변경 | `tests.yml` +25/−0, hunk 1개(`-grep.txt`), `matrix.os: [ubuntu-latest, windows-latest]`·`fail-fast: false`·node 24·`cache-dependency-path: web/package-lock.json`·`timeout-minutes: 15`·4단계 — 사용자 결정 (2) 반영. E2E 는 U9 | ✓ (Windows 실증은 커밋 뒤 CI run — 열린 항목) |
| 판정 명령 출력 전부 | `-2030-u4-skeleton-rework.txt`(구현자) · `-2037-verifier-u4-judge.txt`(나) — 둘 다 exit 0, 번들 해시 `index-ClEEdF8L.js`/`index-Cdlu2p9I.css` 동일 | ✓ |

## 3. 01-plan 52~80행 파일 목록 대조

- **계획에 있는데 없는 것**
  - `web/tailwind.config.ts`(60행) — Tailwind v4 는 CSS 우선 설정(`tokens.css` 1행 `@import "tailwindcss"`, `@theme inline`)이고 `@tailwindcss/vite` 플러그인을 쓴다. `components.json` `"tailwind": {"config": ""}`. **불필요 — 정당**(03-log ①).
  - `web/src/session.ts`(64행)·`push.ts`(66행)·`public/sw.js`·`manifest.webmanifest`·아이콘(67행)·테스트 7개(69행)·E2E spec·fixtures(70행) — U5·U8·U9 몫. 정당.
- **계획에 없는데 생긴 것**
  - `.oxlintrc.json` + devDep `oxlint@1.87.0` + `lint` 스크립트 — create-vite 9 템플릿 산출. 판정 명령에 없고 해롭지 않으나 03-log ①~⑪ 에 없는 **미보고 추가**(R-U4-5).
  - `hooks/useMediaQuery.ts`(결정 N 1024 경계의 구독), `routes.ts`(61행에 있음), `test-setup.ts`(결정 J 차단 장치 — 69행 `network.test.ts` 의 뜻을 setup 으로 옮김), `__tests__/helpers.ts`(가짜 matchMedia), `tsconfig.app.json`·`tsconfig.node.json`(Vite 템플릿 솔루션 구성), `public/favicon.svg`(템플릿 아이콘 — R-U4-4), `e2e/.gitkeep`, `.env.example` — 각각 계약 구현에 필요하거나 템플릿 표준. favicon 외 정당.
  - `web/.gitignore`(최상위 대신) — R-U4-6.
- `components/ui/` 7개(badge·button·card·collapsible·skeleton·sonner·tabs) = 01-plan 63행 목록(Button·Card·Badge·Collapsible·Toast→Sonner·Skeleton·Tabs) 안. 템플릿 잔재 `App.css`·`assets/`·`README.md`·`index.css`·`vite.svg`·`react.svg` 없음.

## 4. 계획 밖 판단 ①~⑪ (03-log) — 도구 강제 / 구현자 선택 / 결과의 정합

| # | 내용 | 성격 | 결과가 계획·카드와 맞는가 |
|---|---|---|---|
| ① | Tailwind v4 → `tailwind.config.ts` 없음, `@tailwindcss/vite` | 도구 강제 | 맞음(§3) |
| ② | shadcn `-p vega -b radix` | 도구 강제(비대화 플래그 조합) | 맞음 — Radix 기반(결정 L) |
| ③ | Inter 웹폰트·`next-themes` 제거 → 시스템 글꼴·OS 다크모드 | 구현자 선택 | **맞음** — 결정 L 324행 "웹 글꼴을 내려받지 않는다", 327행 "OS 설정, 토글 없음". `sonner.tsx` 8행 `theme="system"` |
| ④ | `cn@0.4.0` | 도구 강제(shadcn 4 템플릿) | 맞음 — 출처 공식(§1 ②) |
| ⑤ | `--warning` 토큰 | 구현자 선택 | 맞음 — 결정 L 326행 "경고색 1개" |
| ⑥ | `typecheck` = `tsc -b` | 구현자 선택 | 맞음 — 85행이 "스크립트 이름은 U4 에서 확정" |
| ⑦ | 라우터 직접 구현(`react-router-dom` 없음) | 구현자 선택 | **맞음** — 결정 C 는 "해시" 라우팅만 정했고 라이브러리를 지정하지 않았다. `useSyncExternalStore` + `hashchange`, 3경로·알 수 없는 해시·쿼리 제거가 테스트로 고정(변이 M1·M5·M8·V4·V5 검출). 의존성 0. 렌더 중 `replaceState`(50행)는 부수효과이지만 멱등 — R-U4-7 |
| ⑧ | `Sidebar.tsx` 가 `AppShell` 을 export | 구현자 선택(`mv` 불가) | 이름 불일치 — 동작 문제 없음. R-U4-2 |
| ⑨ | Playwright `--pass-with-no-tests`·`.gitkeep` | 구현자 선택 | 맞음 — "Playwright 설정만" |
| ⑩ | `test-setup.ts` 가 `fetch` 를 던지게 교체 | 구현자 선택 | 맞음 — 결정 J, 변이 V3 검출 |
| ⑪ | CI ubuntu 하나 | 메인 세션 프롬프트 오류 | 재작업으로 두 OS 복원 — 맞음 |
| ⑫ | **(미보고)** 서랍을 shadcn Sheet 가 아니라 직접 구현 | 구현자 선택(프롬프트가 63행 목록으로 제한한 영향) | **어긋남** — 01-plan 346행·367행 불변식 10. R-U4-1 [필수] |
| ⑬ | (미보고) `oxlint` 추가, `web/.gitignore` 로 대체 | 템플릿 산출 / 구현자 선택 | 해롭지 않음. R-U4-5·R-U4-6 |

**절차(FIX-033 (b)) 미준수 자체의 등급 — [권고].** 이유: ①~⑪ 은 03-log 에 목록으로 남았고 사용자가 그 목록을 보고 결정 2개를 내렸다(사후 보고가 됐다). 결과가 계획과 모순되는 것은 ⑫ 하나이고 그것은 [필수]로 따로 올린다. 다만 ⑫·⑬ 처럼 목록에서 빠진 판단이 있었다는 점이 "멈추고 보고" 를 생략한 비용이다 — 다음 단위(U5)부터는 멈춤을 요구한다(R-U4-10).

## 5. TS 타입 ↔ `schemas.py` 전수 대조 (`-types.txt`)

32모델 중 31개 존재, 필드 이름·타입·선택성·null 가능성 **어긋난 필드 0**. 응답 모델의 `= None`/`default_factory` 는 직렬화에 항상 키가 있으므로 TS "필수 + `| null`" 이 맞고, 요청 모델 `BriefingRunIn.schedule_id`·`PushSubscriptionIn.expirationTime` 만 `?:` — 올바른 구분. `GET /questions/pending` 은 `list[ChatPendingQuestionOut]`(routes.py 470행)이라 별도 타입이 필요 없다. 빠진 것은 `HealthOut` 1개(화면 비사용) — registry 비고 "Out/In 모델 전부" 문구만 부정확(R-U4-5 에 포함).

## 6. 생성 파일 전수 (`-grep.txt`)

- `components/ui/` 7개 = 63행 목록 안. `sonner.tsx` 는 `next-themes` 제거(주석 4행), 외부 import 는 `sonner`·`lucide-react` 뿐.
- `/push-dev/` 0 · `getUserMedia|SpeechRecognition` 0 · `VITE_*KEY|SECRET|TOKEN` 0 · `fonts.googleapis|gstatic|cdn.` 0 · `https?://` 는 `favicon.svg` 의 `xmlns`(네임스페이스, 요청 아님)뿐.
- 서버 문자열을 지어낸 곳 없음 — 제품 코드의 문자열은 화면 제목 3개(채팅/인물/브리핑), 사이드바 항목 3개, `aria-label` 4개(주 메뉴·인물 목록·메뉴 열기·사이드바), `index.html` `<title>관계 메모리</title>`, `test-setup.ts` 오류 메시지(테스트 전용). 원칙7 경계 문구 없음.
- `index.html`: `lang="ko"`, `charset`, `viewport` — 적절. `theme-color`·manifest 링크는 U8.
- `public/favicon.svg`(9.5 kB)는 템플릿이 넣은 보라·파랑 번개 아이콘 — 이 제품의 것이 아니고 특정 도구 로고 모양. R-U4-4.
- `raw_utterance` 는 `types.ts` 의 원문 조회 두 타입(115·129행)에만 — 불변식 4 충족.

## 7. 변이 시험 — 내가 직접 돌린 것 (`-mutation-1/2/3.txt`)

스크래치패드 사본 `vmut`(rsync, node_modules 심볼릭 링크, `diff -rq` 동일)에서 변이마다 `sed -i` → `npm test -- --run` → `cp` 원복, 끝에 `diff -rq` 로 사본이 저장소와 다시 동일함을 확인. 저장소 파일 무수정(`git status --short` M 5건은 변이 전과 같은 메인 세션 문서·CI). 구현자 M1~M9 에 없는 것만.

| 변이 | 바꾼 것 | 결과 |
|---|---|---|
| V0 | 기준선 | 20 passed |
| V1 | `vite.config.ts` 프록시 `rewrite` 삭제(접두를 안 벗김 — 결정 C(ii) 위반) | **20 passed — 살아남음(테스트 공백)** |
| V2 | `client.ts` `!response.ok` → `false`(오류를 삼킴) | 2 failed(api.test "P5 오류 규약"·"규약 밖 본문") |
| V3 | `test-setup.ts` fetch 차단 삭제(결정 J 위반) | 1 failed(api.test "테스트 환경의 기본 fetch …") |
| V4 | `routes.ts` 알 수 없는 해시의 `replaceState` 삭제 | 2 failed(routes.test "알 수 없는 해시"·"빈 해시") |
| V5 | `routes.ts` 해시의 `?query` 를 떼지 않음(U7 `#/briefings?schedule_id=N`) | 1 failed(routes.test "parseHash 경계") |

구현자 M1~M9(`-2031-u4-mutation-full-1/2.txt`)는 전부 FAIL 확인(M1 2건·M2 1·M3 1·M4 2·M5 1·M6 1·M7 1·M8 2·M9 1). 1024 경계(M2)·알 수 없는 해시 목적지(M1)·`X-Session-Id`(M6)는 구현자 표에 있어 중복 실행하지 않았다.

## 8. 증거 규칙 (c)

- 1차 `-2025-u4-mutation.txt`(657행)는 머리말에 "M8 DOM 덤프의 ANSI 색 제어문자만 제거" 라고 적었으나 03-log 가 "class 문자열 축약" 을 자기 보고했다 — 축약본. 2차 `-2031-u4-mutation-full-1/2.txt`(485+190행)는 M0~M9 의 vitest 출력을 `exit=` 줄까지 그대로 옮겼고, 빠진 것은 ESC(0x1b) 바이트뿐이라고 머리말에 명시했다(`[36m` 잔여 표기가 그 증거). ESC 바이트는 보이지 않는 제어문자라 판정 정보가 아니다 — **(c) 충족으로 본다.** 1차 축약본은 "이력 보존용" 으로 남았는데 registry U4 테스트 행이 그 축약본을 가리킨다(R-U4-5).
- `-2023-u4-skeleton.txt` 는 실패한 1차 실행(TS18046 6건)까지 기록했고, `-2030-u4-skeleton-rework.txt` 가 재작업 뒤 판정 명령 전체다. 충족.
- 내 증거는 ANSI 제어문자를 `sed` 로 걷어내고 그 사실을 파일 머리에 적었다.

## 9. 보안·범위

- `git diff --stat -- app alembic tests .gitignore docs/RUNNING.md` 빈 출력 — 백엔드 무변경(frontend-agent.md 1항). 삭제된 추적 파일 0.
- 비밀 0: `web/.env` 없음, `.env.example` 은 `VITE_API_TARGET=http://localhost:8000` 한 줄, `VITE_*KEY|SECRET|TOKEN` 0, lock resolved 전부 npmjs. `loadEnv(mode, cwd, '')` 는 설정 파일 안에서만 쓰이고 클라이언트 노출은 Vite 가 `VITE_` 접두로 제한한다.
- 범위: 화면 3개·라우트 3개(원칙5), 네 번째 화면·설정·토글 없음, 캐시·서비스 워커 없음(U8), `/push-dev/` 0, 음성 0(원칙7).
- security §3: `npx` 는 전부 버전 고정(`create-vite@9.2.1`·`shadcn@4.21.4`), `curl | sh` 류 없음. §5 는 이 단위에 해당 코드 없음.
- Write/Edit 사용은 구현자 자기 보고(03-log "Write/Edit 로만, 도구 생성 파일은 허용") — 훅이 Bash 쓰기를 거부하므로 도구 산출물 외에는 신뢰한다. 도구 산출물(create-vite·shadcn)은 §3·§6 에서 전수 확인했다.

## 10. 소견

- **[필수] R-U4-1** 결정 N 서랍이 기성 컴포넌트가 아니다. `Sidebar.tsx` 78~93행은 `div`+`aside role="dialog"` 직접 구현으로, 01-plan 346행 "서랍은 shadcn/ui 의 Sheet(Radix Dialog 기반) 같은 기성 컴포넌트로 만든다(결정 L 시간 상한)" 와 결정 L 328행 "접근성: Radix 기본" 에 어긋난다 — `aria-modal` 없음·포커스 가둠/복귀 없음·본문 스크롤 잠금 없음(`grep 'aria-modal\|focus' Sidebar.tsx` 0건). 그 결과 **01-plan 367행 불변식 10** `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx | grep -v ui/` 가 "1파일뿐" 이 아니라 **0파일**(`-grep.txt` 2차 첫 항목)이라 U9 자동 판정이 계획대로 통과할 수 없다. 03-log ①~⑪ 에 없는 미보고 판단이며, 메인 세션 프롬프트의 "shadcn 컴포넌트는 63행 목록으로 제한" 이 원인의 일부다(63행은 "… 등" 이라 Sheet 가 금지는 아니었다). 해결 두 갈래 중 사용자가 고른다: (가) `npx shadcn@4.21.4 add sheet` 로 `components/ui/sheet.tsx` 를 받아 서랍을 `Sheet`(side="left")로 바꾼다 — Esc·배경 클릭·포커스 가둠·`aria-modal` 이 Radix 에서 오고 기존 테스트 7건은 역할·이름 기준이라 대부분 그대로 통과한다, 불변식 10 도 1파일이 된다. (나) 직접 구현을 유지하고 01-plan 346·367행을 고친다(사용자 승인 필요 — 계획 변경) + `aria-modal="true"`·포커스 복귀를 보강한다. 어느 쪽이든 변경 파일 이름을 03-log U4 에 적는다(367행 "파일 이름은 U4 에서 정해 03-log 에 기록").
- **[권고] R-U4-2** `components/Sidebar.tsx` 가 `AppShell` 을 default export 한다(03-log ⑧). 파일 이름과 내용이 다르면 registry grep·불변식 10 의 "파일 이름" 기록이 헷갈린다. `AppShell.tsx` 로 Write 하고 `Sidebar.tsx` 삭제는 메인 세션에 요청(bash-write-guard 가 `mv` 를 막는 것이 이유였으므로). R-U4-1 재작업과 같은 커밋에서.
- **[권고] R-U4-3** 프록시 `rewrite` 는 어떤 자동 테스트도 고정하지 않는다(V1 살아남음). 01-plan 자동 판정 24~26행 E2E 는 `vite preview`+`page.route` 라 프록시를 거치지 않으므로 구조적 공백이다. U9 의 `docs/RUNNING.md` "프론트 실행" 절에 수동 확인 한 줄(`curl -s localhost:5173/api/health` → 백엔드 `/health` 응답)을 넣거나, `vite.config.ts` 의 `rewrite` 함수를 export 해 Vitest 1건(`'/api/persons' → '/persons'`)으로 고정한다. U4 재작업에 끼워도 되고 U9 로 미뤄도 된다.
- **[권고] R-U4-4** `public/favicon.svg` 는 템플릿이 넣은 도구 로고 모양 아이콘(9.5 kB, 보라·파랑 번개)이다 — 결정 N 332행 "특정 회사의 로고·상표·고유 디자인은 복제하지 않는다" 취지와 어긋나고 유일한 템플릿 잔재다. U8 이 `icon-192.png`·`icon-512.png` 를 만들 때 같은 도안으로 교체하거나, 지금 단순 도형 SVG 로 바꾼다.
- **[권고] R-U4-5** registry U4 행의 부정확한 문구 세 곳: "Out/In 모델 전부 손으로 옮김" → `HealthOut` 제외(31/32); 테스트 행의 "변이 9종 전부 검출(evidence/20261012-2025-u4-mutation.txt)" → 전체본 `-2031-u4-mutation-full-1/2.txt` 로; `oxlint`·`lint` 스크립트·`.oxlintrc.json` 이 어느 행에도 없다(템플릿 산출이면 그렇게 적고, 쓰지 않을 거면 devDep 과 함께 뺀다 — 판정 명령에 없어 어느 쪽이든 동작 영향 0).
- **[권고] R-U4-6** `.gitignore` 를 최상위(01-plan 80행 표) 대신 `web/.gitignore` 로 했다. 효과는 같고 untracked 에 node_modules/dist 0 을 확인했다. 03-log U4 에 한 줄로 남기면 된다(계획 변경 아님 — 33행 범위 문장은 파일을 지정하지 않았다).
- **[권고] R-U4-7** `routes.ts` 50행 `useRoute` 가 렌더 중 `history.replaceState` 를 부른다. 멱등이라 StrictMode 이중 렌더에 안전하고 V4 가 테스트로 고정됐지만, 렌더 중 부수효과는 React 관례 밖이다. `useEffect` 로 옮기거나 `subscribe` 안에서 정규화하는 편이 안전하다 — U5 전에 손보면 좋고 필수는 아니다.
- **[권고] R-U4-8** `playwright.config.ts` 의 `baseURL: 'http://localhost:5173'` 는 개발 서버 포트다. 01-plan 120행은 E2E 를 `vite preview` 빌드로 돌린다고 했으므로 U9 에서 `webServer: { command: 'npm run preview', url: 'http://localhost:4173' }` 로 바꾸고 baseURL 을 맞춘다. 지금은 테스트 0건이라 영향 없음.
- **[권고] R-U4-9** `tw-animate-css@1.4.0` 은 shadcn init 이 기본으로 넣는 3자(개인 저장소 Wombosvideo) 패키지다. 번들에 들어가는 CSS 유틸(애니메이션 클래스)이고 `npm audit` 0건이지만, 결정 L 이 "맞춤 애니메이션 없음" 이라 실제로 쓰는 클래스가 `sonner`·`collapsible` 기본 전환뿐이다. 지금은 두되 U9 불변식 점검 때 `grep -rn "animate-" web/src` 로 사용처를 적어 두면 뺄지 판단할 수 있다.
- **[권고] R-U4-10** FIX-033 (b) 절차: 계획 밖 판단 11개를 멈추지 않고 진행했고 그 목록에서도 ⑫(서랍 직접 구현)·⑬(oxlint·.gitignore 위치)이 빠졌다. 결과가 계획과 모순된 것은 ⑫ 하나라 절차 미준수 자체는 [권고]로 두지만, U5 위임 프롬프트에 "도구가 강제한 것은 03-log 에 적고 진행, 구현자 선택(라이브러리 유무·컴포넌트 대체·파일 위치)은 멈추고 보고" 를 명시해 둘을 구분하게 한다.

## 11. 판정 근거 요약

- 판정 명령 4개 재실행 exit 0, 번들 해시 구현자와 동일(§2, `-judge.txt`).
- R-U0-3 ①~⑤ 충족(§1, `-deps.txt`).
- 95행 계약 항목 전부 구현·테스트 고정, 변이 M1~M9 + V2~V5 검출(§2·§7).
- 타입 어긋남 0(§5, `-types.txt`).
- 보안·범위 위반 0(§9).
- **보류 사유**: R-U4-1 — 01-plan 346행·367행(불변식 10)과 모순되는 미보고 판단 1건. 해결은 Sheet 교체(가) 또는 계획 수정(나) 중 사용자 선택, 둘 다 작업량이 작다(파일 1개 + 03-log 한 줄). 그 뒤 재검증은 `grep -rlE "Sheet|Dialog|Drawer" web/src --include='*.tsx' | grep -v ui/` 가 1파일, `npm test -- --run` 20건 이상 통과, 변이 M3·M7·V4 재실행으로 끝난다.

## 재검증(2차) — 2026-10-12 23:31~23:40, 재작업 2차(frontend-agent) 뒤

검토자: verifier (fable). 사용자 결정(03-log 21:35): R-U4-1 → (가) Sheet 교체, 권고 R-U4-2·3·5·6·7·9 를 같은 재작업에 묶음, R-U4-4 → U8 · R-U4-8 → U9 이월. 대상: 1차 리뷰 시점과의 차이 9파일(신규 `AppShell.tsx`·`ui/sheet.tsx`·`proxy.ts`·`__tests__/proxy.test.ts` / 수정 `App.tsx`·`routes.ts`·`routes.test.tsx`·`tsconfig.node.json`·`vite.config.ts` / 삭제 `Sidebar.tsx`) + registry U4 행 + 구현자 증거 `-2055-u4-skeleton-rework2.txt`·`-2055-u4-mutation-rework2.txt`·`-2055-u4-versions-rework2.txt`·`-2056-u4-invariant10.txt`. `package.json`·`package-lock.json` 은 1차 시점과 바이트 동일.

내 증거(전부 `evidence/`, 출력 전체):
- `20261012-2331-verifier-u4-recheck-judge.txt` — `npm ci`·`typecheck`·`test`·`build` 각각, 전부 exit 0(24 passed). 빌드 해시가 구현자와 다른 이유(Sidebar.tsx 삭제 → Tailwind 스캔 범위 변화)를 비고에.
- `20261012-2332-verifier-u4-recheck-invariant.txt` — 불변식 10 grep 1파일 · 옛 Sidebar 참조 0 · localStorage 0 · 패키지·lock 동일 · `npm ls` 25개 동일 · `npm audit --omit=dev` 0 · 백엔드 무변경 · 삭제 파일 0 · tw-animate 사용처.
- `20261012-2334-verifier-u4-recheck-probe.txt` — 사본에만 둔 탐침 4건(접근성 2·hashchange 2) 실측, 1차 실패(내 단언 오류) 원문과 수정 뒤 28/28.
- `20261012-2336-verifier-u4-recheck-mutation.txt` — M3·M7·V4·V1 재실행 + 환경 의존 실험 E1.

### 12-1. 1차 재검증 조건 (판정할 것 1)

| 조건 | 결과 | 근거 |
|---|---|---|
| 불변식 10 grep → 1파일 | **충족** — `web/src/components/AppShell.tsx` 1파일(ui/ 밖), ui 포함 2파일(`ui/sheet.tsx`) | `-recheck-invariant.txt` 첫 두 항목(저장소 루트에서 내가 실행; 구현자 `-2056-u4-invariant10.txt` 는 web/ 안에서 실행 — 같은 결과). `routes.test.tsx` 주석의 "Sheet(Radix Dialog)" 문구를 "기성 컴포넌트" 로 바꿔 테스트 파일이 걸리지 않게 한 것은 02-plan-verify N-2 가 예고한 그 경우다 |
| `npm test -- --run` 통과 | **충족** — 3 files · 24 passed | `-recheck-judge.txt` |
| M3 재실행(항목 선택 시 닫지 않음) | **검출** — 1 failed "좁은 폭: 항목을 고르면 서랍이 닫히고…" | `-recheck-mutation.txt` M3 |
| M7 재실행(Esc 막음 — `SheetContent onEscapeKeyDown preventDefault`) | **검출** — 1 failed "Esc 와 바깥(배경) 클릭" | 같은 파일 M7 |
| V4 재실행(useEffect 안 `replaceState` 삭제) | **검출** — 2 failed(알 수 없는 해시·빈 해시) | 같은 파일 V4 |
| V1 1회(rewrite 제거 — 1차 공백) | **검출** — 1 failed `proxy.test.ts` 11행 `rule.rewrite toBe stripApiPrefix` → undefined | 같은 파일 V1. **1차 R-U4-3 공백 닫힘** |

### 12-2. Sheet 교체가 결정 N·접근성을 만족하는가 (판정할 것 2)

| 결정 N 항목 | 코드 | 실측 |
|---|---|---|
| ≥1024 고정 사이드바 | `AppShell.tsx` 9행 `(min-width: 1024px)`, 53~56행 `aside` | routes.test "1024px 경계: 1023 은 서랍형, 1024 는 고정"(24 passed 안) |
| <1024 서랍 | 58~73행 `Sheet open onOpenChange` + `SheetTrigger`(메뉴 버튼, `aria-label="메뉴 열기"`) + `SheetContent side="left"` | routes.test "좁은 폭: 기본은 접혀 있고 메뉴 버튼으로 열린다" |
| 항목 선택 시 닫힘 | 71행 `onNavigate={() => setOpen(false)}` | M3 검출 |
| Esc·바깥 클릭 닫힘 | Radix Dialog 기본(DismissableLayer) — 코드에 별도 처리 없음 | routes.test "Esc 와 바깥(배경) 클릭"(배경 선택자 `[data-slot="sheet-overlay"]`), M7 검출 |
| 하단 탭바 없음 | 파일에 탭바 요소 없음(`nav` 1개, `aside`/`SheetContent` 1개) | — |
| 상태만, localStorage 없음 | 49행 `useState(false)`; 제품 코드 `localStorage` 0건(주석 1) | routes.test "열림/닫힘은 라우트도 localStorage 도 바꾸지 않는다" |
| 접근성(결정 L "Radix 기본") | `ui/sheet.tsx` 3행 `Dialog as SheetPrimitive`(radix-ui), 70행 `SheetTitle` sr-only "사이드바", 67행 `aria-describedby={undefined}` | 탐침(`-recheck-probe.txt` R0'): `role=dialog` 접근 가능한 이름 "사이드바" ✓ · 열리면 포커스가 서랍 안 ✓ · 바깥(트리거)은 `aria-hidden` 조상 아래(hideOthers) ✓ · Tab 6회 동안 포커스 가둠 ✓ · Esc 로 닫힘 ✓ · 포커스 트리거 복귀 ✓ · "Close" 버튼 없음 ✓. **`aria-modal` 속성은 `null`** — Radix Dialog 는 `aria-modal` 대신 바깥을 `aria-hidden` 으로 가리는 기법을 쓴다(위임 메시지의 "aria-modal" 기대는 Radix 의 실제 동작과 다르고, 효과는 같다). 1차 직접 구현에 없던 포커스 가둠·복귀·hideOthers 가 전부 생겼다 |

→ 결정 N 전 항목 충족, 접근성은 결정 L 의 "Radix 기본" 그대로.

### 12-3. 1차 권고 6건의 닫힘 (판정할 것 3)

| 소견 | 상태 | 근거 |
|---|---|---|
| R-U4-2 `Sidebar.tsx`→`AppShell.tsx` | **닫힘** | `ls web/src/components` = `AppShell.tsx`·`ui`; `App.tsx` 1행 import; 옛 이름 참조 0(남은 `SidebarContent` 는 내부 함수) — `-recheck-invariant.txt` |
| R-U4-3 rewrite 테스트 공백 | **닫힘** | `proxy.ts` `stripApiPrefix` + `proxy.test.ts` 4건(연결 1·값 3), V1 검출 |
| R-U4-5 registry 문구 | **닫힘** | registry diff: "`HealthOut` 을 뺀 31개 … 화면 비사용" · "전체 출력 evidence/20261012-2031-u4-mutation-full-1/2.txt" · "`lint`·`oxlint@1.87.0`·`.oxlintrc.json` 은 create-vite 9 템플릿 산출" 모두 반영. 단 새로 잔존 문구 2곳 — R-U4-13 |
| R-U4-6 `.gitignore` 위치 | **닫힘(해당 없음 판정 수용)** | 구현자는 "해당 없음" 으로 분류했지만 registry 프론트 골격 행이 `web/` 경로 아래 `.gitignore` 를 명시하고 최상위 무변경이 `git diff --stat` 로 확인되므로 1차 권고(기록 한 줄)의 목적은 달성됐다 |
| R-U4-7 렌더 중 `replaceState` | **닫힘** — 부작용 없음을 코드·실측으로 확인 | `routes.ts` 48~54행: `unknown = route === null` 을 의존성으로 한 `useEffect` 가 `replaceState` + `dispatchEvent(new HashChangeEvent('hashchange'))`. 흐름: 알 수 없는 해시 → 첫 렌더는 `route ?? {name:'chat'}` 로 chat 을 즉시 그림 → effect 가 주소를 `#/chat` 으로 바꾸고 수동 이벤트 → `useSyncExternalStore` 구독자가 새 해시를 읽어 재렌더 1회 → `unknown=false` 라 effect 재실행 없음. `replaceState` 는 브라우저 hashchange 를 내지 않으므로 수동 발행이 **필요**하고, 발행 뒤 해시는 유효해 두 번째 발행 조건이 없다 → 루프 불가. 실측(탐침 3·4): 알 수 없는 해시마다 수동 발행 정확히 1회, 추가 틱에서 0, StrictMode(이중 effect)에서도 ≤ 2 뒤 정지, 주소 `#/chat`. V4 로 테스트 고정 확인 |
| R-U4-9 `tw-animate-css` | **닫힘(유지 정당)** | 사용처 `ui/sheet.tsx` 38·63행(Sheet 의 fade/slide 전환 — 결정 L "기본 전환 외 애니메이션 없음" 의 '기본 전환'). sonner `animate-spin`·skeleton `animate-pulse` 는 Tailwind 기본. registry 토큰 행에 유지 이유 기록 |
| R-U4-4 favicon · R-U4-8 Playwright 포트 | **이월(열림)** | 사용자 결정 21:35 — U8·U9. 04-review 가 챙길 항목 |
| R-U4-10 절차 | **준수** | 2차 프롬프트에 규칙 명시(03-log), 구현자가 "지시의 구현 안" 2개와 자기 보고 위험 1개를 보고함(12-5) |

### 12-4. `proxy.test.ts` 기본 대상 단언의 환경 의존 (판정할 것 4) — **결함, [권고] R-U4-11**

- 실측 E1(`-recheck-mutation.txt` 끝): 소스 무변경 상태에서 셸 환경변수 `VITE_API_TARGET=http://localhost:9000` 만 주면 `proxy.test.ts` 13행 `expect(rule.target).toBe('http://localhost:8000')` 가 `'http://localhost:9000'` 으로 실패한다. `vite.config.ts` 11행 `loadEnv(mode, process.cwd(), '')` 는 prefix `''` 라 환경 파일(`.env`·`.env.test`·`.env.local`)과 process.env 를 모두 읽으므로, 01-plan 95행 "포트는 설정" 대로 백엔드 포트를 바꾼 개발자(U9 RUNNING 이 안내할 바로 그 경우)의 `npm test` 가 깨진다.
- 등급 **[권고]**(필수 아님): CI 와 새 체크아웃에는 그 값이 없어 U4 판정 명령은 결정적으로 통과하고, 12행까지(rewrite 동일성·값)가 R-U4-3 의 본체라 결함은 13행 한 줄이다. 다만 U5 부터 로컬 포트를 바꾸는 사람이 생기므로 **U5 위임에 끼워 고치기를 권고**.
- 고치는 방법(둘 중 하나, 둘 다 한 줄 수준): (가) 기본값 해석을 `proxy.ts` 로 옮긴다 — `export const DEFAULT_API_TARGET = 'http://localhost:8000'`, `export function resolveApiTarget(env: Record<string, string | undefined>) { return env.VITE_API_TARGET || DEFAULT_API_TARGET }`; `vite.config.ts` 는 `resolveApiTarget(loadEnv(...))`; 테스트는 `resolveApiTarget({})`·`resolveApiTarget({VITE_API_TARGET:'http://x:1'})` 를 순수하게 단언하고 13행은 지운다(연결 테스트는 `rewrite` 동일성만). (나) 연결 테스트 안에서 `vi.mock('vite', async (orig) => ({ ...(await orig<typeof import('vite')>()), loadEnv: () => ({}) }))` 로 `loadEnv` 를 빈 객체로 고정해 13행을 유지한다. (가)가 환경 파일 로직을 테스트에서 완전히 떼어내므로 더 낫다.

### 12-5. "지시의 구현 안" 2개의 분류 (판정할 것 5)

- `SheetTitle` sr-only "사이드바": Radix Dialog 는 `Title` 이 없으면 접근 가능한 이름이 없어 콘솔 오류를 내고 대화상자 이름이 비므로, Sheet 를 쓰라는 지시의 **필수 구성 요소**다(sr-only 는 시각적으로 숨기되 이름은 남기는 shadcn 관례). 멈출 사항 아님 — **분류 적절**. `aria-describedby={undefined}` 도 같은 범주(Description 미사용 경고 억제).
- X 버튼 `showCloseButton={false}`: 결정 N 은 닫는 경로를 "항목 선택·바깥 클릭·Esc" 로 적었고 X 버튼은 언급이 없다. 끄는 것은 컴포넌트의 prop 선택이며 R-U4-10 의 멈춤 범주(라이브러리 유무·컴포넌트 대체·파일 위치)에 들지 않는다 — 보고로 충분, **분류 적절**. 다만 모바일에서 닫기 어포던스가 배경 탭·항목 선택뿐이라는 점은 U10 사람 점검 19항(서랍 여닫기)에서 사용자가 보게 되므로 그때 켤지 정하면 된다(지금 변경 불필요).

### 12-6. R-U0-3 재확인 (판정할 것 6)

`package.json`·`package-lock.json` 은 1차 리뷰 시점 사본과 `diff -q` 동일(바이트 단위), `npm ls --depth=0` 25개 동일, lock `node_modules/` 항목 557·`hasInstallScript` 1(fsevents) 동일, `npm audit --omit=dev` 0 재현 — `-recheck-invariant.txt`. `sheet.tsx` 는 기존 `radix-ui@1.8.0` 의 `Dialog` 를 쓰므로 새 패키지 0(구현자 `-2055-u4-versions-rework2.txt` 의 `add sheet` 출력 "Created 1 file" 과 일치). 스크립트 7개 무변경.

### 12-7. 그 밖에 본 것

- 빌드 산출물 해시가 구현자(`index-CUTMAm14.css 42.94 kB`)와 내 것(`index-B9a6Arut.css 42.71 kB`)이 다르다 — 구현자 빌드 뒤 메인 세션이 `Sidebar.tsx` 를 지웠고 Tailwind v4 가 import 와 무관하게 소스 파일의 클래스를 스캔하므로 CSS 가 0.23 kB 줄었다. JS 크기 동일(333.21 kB), 해시만 CSS 자산명 참조로 바뀜. 소스 차이 아님(`-recheck-judge.txt` 비고).
- 서랍 폭: `AppShell.tsx` 68행 `className="w-64 …"` 이지만 `ui/sheet.tsx` 63행의 변형 클래스 `data-[side=left]:w-3/4 … data-[side=left]:sm:max-w-sm` 이 속성 선택자라 특이도가 높아 이긴다 → 서랍은 폭의 75%(≥640px 에서는 384px 상한), 데스크톱 고정 사이드바는 256px. 동작·계약 무관, 시각 일관성만 — R-U4-12.
- registry 앱 틀 행에 "(옛 `web/src/components/Sidebar.tsx` 는 어디서도 import 안 함 — 삭제 대상)" 이 남아 있으나 이미 삭제됐고, 같은 행 비고 "라이브러리 없이 직접 구현(의존성 없음)" 은 라우터에만 맞고 서랍은 Sheet 다 — R-U4-13.
- 03-log 가 옛 파일 삭제를 "메인 세션이 `rm` 으로" 라고 적었다 — 단일 파일 `rm` 은 security §3 의 재귀 삭제 금지 대상이 아니고, 삭제된 추적 파일 0(untracked 파일이었다). 문제 없음.
- 보안·범위: `app/`·`alembic/`·`tests/`·`docs/RUNNING.md` 무변경, 삭제된 추적 파일 0, `web/` 안에 환경 파일 없음, 비밀 0.

### 12-8. 2차 소견

- **[권고] R-U4-11** `proxy.test.ts` 13행 기본 대상 단언이 환경(`VITE_API_TARGET` 환경변수·환경 파일)에 의존한다 — 실측 E1. 고치는 방법은 12-4 (가) 권장. U5 위임에 끼운다.
- **[권고] R-U4-12** 서랍 폭이 고정 사이드바(256px)와 다르다(75%·최대 384px). `SheetContent` 에 `data-[side=left]:w-64 data-[side=left]:sm:max-w-none`(또는 `className` 에서 `w-64` 대신 변형 접두를 붙인 폭)로 맞추면 된다. U10 사람 점검 1항(같은 앱 틀)에서 드러날 수 있어 U5~U7 중 아무 때나.
- **[권고] R-U4-13** registry 앱 틀 행 잔존 문구 2곳 — "Sidebar.tsx … 삭제 대상"(이미 삭제) 삭제, "라이브러리 없이 직접 구현(의존성 없음)" → "라우터는 직접 구현, 서랍은 shadcn Sheet(radix-ui Dialog)". 이 커밋의 registry 수정에 끼우면 된다.

### 12-9. 2차 판정 근거 요약

- 1차 [필수] R-U4-1 닫힘: Sheet 교체, 불변식 10 1파일, 접근성 실측(12-1·12-2).
- 판정 명령 4개 exit 0, 24 passed(`-recheck-judge.txt`).
- 재검증 조건 변이 M3·M7·V4 전부 검출, V1 공백 닫힘(`-recheck-mutation.txt`).
- 1차 권고 6건 닫힘, 2건 이월(사용자 결정), 절차 준수(12-3).
- 새 패키지 0, 보안·범위 위반 0(12-6·12-7).
- 새 소견 [권고] 3건 — 커밋 차단 사유 없음. **결과: 통과.**
