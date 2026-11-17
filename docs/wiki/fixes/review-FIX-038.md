# review-FIX-038 · 로그인한 화면에서 아이디를 보이지 않는다 — 커밋 전 리뷰

검토자: verifier (fable) · 2026-11-17 · 기준 HEAD `9fce41d` (dev2) + 작업 트리 미커밋 diff(`web/` 3개 파일, +22/-16) · Refs: FIX-038 P9b-auth CR-007 D18 원칙5

**결과: 통과 — [필수] 0건, [권고] 2건(R-38-1·R-38-2), [참고] 1건.** 변경은 FIX-038 수정안 그대로다(아이디 `span` 과 가운뎃점 하나 제거). 로그인 뒤 화면에서 `state.username` 을 그리는 곳은 남아 있지 않고, 고친 테스트는 계정 구분 단언을 닉네임으로 옮겼으며 내가 돌린 변이 2종을 모두 잡는다.

## 1. 본 것

- `docs/wiki/fixes/FIX-038.md` 증상·원인·수정안·하지 않는 것·기획서 정합성·`계획 점검: 통과`.
- `git diff -- web/src/components/AppShell.tsx web/src/__tests__/auth.test.tsx web/e2e/auth.spec.ts` 전체.
  - `AppShell.tsx`: `sidebar-username` span 과 그 뒤 `<span aria-hidden="true">·</span>` 한 개 삭제, 주석 한 줄 갱신. 닉네임 span·로그아웃 버튼·실패 안내(`role="alert"`)는 글자 하나 바뀌지 않았다.
  - `auth.test.tsx`: 7곳 수정(아래 4절). `e2e/auth.spec.ts`: 1곳 → 닉네임 `toHaveText('민지')` + `sidebar-username` `toHaveCount(0)`.
- `git status --short -- web`: 리뷰 시작·종료 모두 이 3개 파일뿐(`3 files changed, 22 insertions(+), 16 deletions(-)`). `web/src/auth.tsx`·`web/src/api/*`·`web/src/screens/AuthScreen.tsx` 변경 0 → 상태 필드 `username`, `/auth/*` 응답 타입, 가입·로그인 화면 무변경. `app/`·`tests/`·`evaluation/` 의 미커밋 변경은 FIX-037 것이라 위임 지시대로 보지 않았다.
- 직접 grep `grep -rn "username" web/src | grep -v __tests__`: 남은 곳은 `screens/AuthScreen.tsx`(로그인 전 화면의 입력 칸·중복 확인·오류 코드), `auth.tsx:15·44·70`(상태 타입과 대입), `api/types.ts`·`api/client.ts`(계약)뿐이다. **`state.username` 을 읽어 그리는 JSX 는 0곳.** `grep -rn "sidebar-username" web/src web/e2e` 는 테스트의 "없다" 단언 5줄만 낸다.
- 근거 카드:
  - `packages/P9b-auth/01-plan.md:494` 결정 AF — "(i) "<닉네임> · <아이디> · 로그아웃"(아이디는 흐리게 …) (ii) "<닉네임> · 로그아웃"(아이디 숨김)". (ii) 는 계획이 이미 올려 둔 후보다.
  - `decisions/D18-login-user-isolation.md:15` 결정 10 — "닉네임은 사용자 자신의 **화면 표시 이름**이다 — 가입·로그인·내 정보 응답과 사이드바에만 쓰고, 로그인은 여전히 아이디로 한다." 아이디를 사이드바에 보여야 한다는 문장은 없다 → D·S 충돌 없음. 로그인은 여전히 아이디(로그인 본문 단언 `{ username: 'minji_01', password: … }` 유지).
- 구현자 증거 5개 `fixes/evidence/20261117-2227-fix038-vitest.txt`(212 passed) · `-2228-fix038-{lint,typecheck,build,mutation-span-revived}.txt`(변이 4 failed | 40 passed).

## 2. 내가 직접 실행한 것 (전부 `save_evidence.py` 통로, 출력 전문)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `npm --prefix web run test` | **10 files · 212 passed**, exit 0 | `fixes/evidence/20261117-2229-verifier-FIX-038-test.txt` |
| 2 | `npm --prefix web run lint` | exit 0 (경고만 — `AppShell.tsx:24·100` `only-export-components` 는 이번 diff 가 건드리지 않은 `export const` 줄) | `…-2229-verifier-FIX-038-lint.txt` |
| 3 | `npm --prefix web run typecheck` | exit 0 | `…-2229-verifier-FIX-038-typecheck.txt` |
| 4 | `npm --prefix web run build` | `✓ built`, exit 0 | `…-2229-verifier-FIX-038-build.txt` |
| 5 | `npm --prefix web run e2e -- e2e/auth.spec.ts` | **1 passed**, exit 0 (고친 e2e 단언이 실제 브라우저에서 통과) | `…-2230-verifier-FIX-038-e2e-auth.txt` |
| 6 | 변이 2종 — 스크래치패드 사본에서 `npx vitest run src/__tests__/auth.test.tsx` | 아래 표 | `…-2230-verifier-FIX-038-mutations.txt` (M2 는 `--append`) |

변이 사본: `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/fix038-verifier/base/` — `web/` 의 `src public index.html package.json tsconfig*.json vite.config.ts components.json` 만 이름을 지정해 복사했고 `node_modules` 는 심볼릭 링크다(점 파일은 하나도 넣지 않았다). 사본 기준선 44 passed 확인 뒤 변이. 저장소 파일은 고치지 않았다.

| 변이 | 사본에 한 일 | 기대 | 결과 |
|---|---|---|---|
| M1 | `AccountRow` 에 `sidebar-username` span + 가운뎃점을 되살림(FIX-038 이전 모양) | 실패 | **4 failed / 40 passed** — 로그인 성공, FIX-038 회귀 테스트, 가입 직후, 두 계정 테스트 |
| M2 | 아이디 span 없이 `sidebar-nickname` 칸이 `state.username` 을 그림(아이디가 닉네임 자리로 새는 경우) | 실패 | **6 failed / 38 passed** — 위 4개 + 관문 me 200 + 로그아웃 5xx |

M2 는 "칸 이름만 없애고 아이디 글자는 남는" 경우다. `queryByTestId('sidebar-username') === null` 만으로는 못 잡고, 닉네임 값 단언과 `textContent` 에 아이디가 없다는 단언이 잡았다 — 계획의 회귀 ②가 실제로 일을 한다.

## 3. 범위 판정

| 계획 문장(FIX-038 수정안) | 판정 | 근거 |
|---|---|---|
| 아이디 span 과 그 앞 가운뎃점 하나를 뺀다. 결과 = `<닉네임> · 로그아웃` | 지킴 | diff `AppShell.tsx` -4줄, 테스트 `expect(row.textContent).toBe('민지·로그아웃')` |
| 로그인한 화면 어디에도 아이디 글자가 나오지 않는다 | 지킴 | 1절 grep — `state.username` JSX 0곳 |
| 상태 필드 `username`·`/auth/*` 응답 계약 무변경 | 지킴 | `auth.tsx`·`api/` diff 없음, 백엔드 `web/` 밖 변경은 이 FIX 것이 아님 |
| 가입·로그인 화면 아이디 입력 칸 그대로 | 지킴 | `AuthScreen.tsx` diff 없음 |
| 회귀 ①②③ 새 단언 | 있음 | `auth.test.tsx:453-467` |
| 하지 않는 것(백엔드 `username` 제거·닉네임 변경·디자인 변경) | 넘지 않음 | className·구조 그대로, 요소 2개 삭제뿐 |

원칙5(요소 제거뿐, 화면 추가 없음)·원칙7(채팅방 목록 없음 단언 유지)·security(비밀·외부 전송·삭제 없음) 위반 없음.

## 4. 고친 테스트가 약해졌는가

| 위치(수정 뒤) | 전 | 후 | 판정 |
|---|---|---|---|
| `auth.test.tsx:105` 관문 me 200 | 줄 안 `sidebar-username` = `minji_01` | 줄 안 `sidebar-nickname` = `민지` | 동등 — `ME` 는 닉네임≠아이디라 계정 값이 화면에 왔는지 여전히 본다(M2 검출) |
| `:154-155` 로그인 성공 | `sidebar-username` = `minji_01` | 칸 없음 + 줄에 `minji_01` 없음 | **긍정 단언이 사라짐 → R-38-1** |
| `:453-467` FIX-038 회귀 | 닉네임·아이디 둘 다 + `민지·minji_01·로그아웃` | 칸 없음 + 아이디 없음 + 닉네임 + 로그아웃 버튼 + `textContent === '민지·로그아웃'` | 강화(완전 일치) |
| `:477-479` 가입 직후 | 닉네임 `심사위원` + 아이디 `judge01` | 닉네임 `심사위원` + 칸 없음 + `judge01` 없음 | 동등 |
| `:567` 로그아웃 5xx | 아이디 칸이 문서에 있다 | 닉네임 = `민지` | 강화(존재 → 값) |
| `:589-591` 두 계정 | `sidebar-username` = `second_user` | `sidebar-nickname` = `두번째` + 칸 없음 + `second_user` 없음 | 동등 — 첫 계정 닉네임 `민지` 와 다른 값이라 "이전 계정 상태가 남지 않는다" 를 닉네임으로 구분한다. 로그인 응답의 닉네임이 상태에 실리는지도 여기서 본다 |
| `e2e/auth.spec.ts:32-33` | `toHaveText('minji_01')` | 닉네임 `toHaveText('민지')` + `toHaveCount(0)` | 동등, 직접 실행 통과(2절 #5) |

## 5. 소견

- **[권고] R-38-1** `web/src/__tests__/auth.test.tsx:154-155` — 로그인 성공 테스트에서 "로그인 응답의 계정이 사이드바에 보인다" 는 긍정 단언이 빠지고 부정 단언 두 줄만 남았다. 계정 줄이 닉네임을 비워 그려도 이 테스트는 통과한다. 같은 경로(로그인 응답 → 닉네임 표시)를 `:589` 가 `두번째` 로 단언하므로 스위트 전체로는 구멍이 아니어서 필수는 아니다. `expect(screen.getByTestId('sidebar-nickname')).toHaveTextContent('민지')` 한 줄을 더하면 이 테스트 혼자서도 선다.
- **[권고] R-38-2** `docs/wiki/packages/P9b-auth/01-plan.md:494`(결정 AF)·`:339`(U10 설명 "한 줄 **"<닉네임> · <아이디> · 로그아웃"**") — 아직 옛 문장이다(`git status` 에 01-plan 변경 없음). FIX-038 수정안 "문서" 항목이 메인 몫으로 적어 둔 "(2026-11-17 사용자 결정으로 (ii), FIX-038)" 덧붙임을 같은 커밋에 넣어야 코드 주석 "결정 AF (ii)" 와 카드가 맞는다. `:339` 에도 같은 한 마디가 있으면 읽는 사람이 헷갈리지 않는다. 제품 코드 문제가 아니라 필수로 올리지 않았다.
- **[참고]** "아이디 없음" 단언은 `textContent` 만 본다. `title`·`aria-label` 같은 속성으로 아이디가 새는 경우는 잡지 못하지만, 지금 `AccountRow` 에 그런 속성은 없다(파일 49-69행 직접 확인).

## 6. 열린 문제

없음. R-38-1·R-38-2 는 커밋을 막지 않는다.
