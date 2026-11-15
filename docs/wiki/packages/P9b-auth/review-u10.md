# P9b-auth U10 커밋 전 코드 리뷰 — 가입 화면 닉네임 칸·아이디·닉네임 "중복 확인"·사이드바 닉네임 (CR-007)

검토자: verifier (fable) | 일시: 2026-11-16 07:21 | 대상: dev2 HEAD `f1ea1b4` + 미커밋 작업 트리 중 `web/` 12파일
결과: 통과
판정: **통과**. 열린 [필수] 0 · 열린 [권고] R-1~R-7.
범위 밖(보지도 판정하지도 않음): `app/`·`alembic/`·`tests/` 의 미커밋 변경(백엔드 U9 진행 중). 백엔드 pytest 는 돌리지 않았다. 서버 쪽 정규화 함수의 실제 동작은 계획 문장("가입과 같은 정규화 함수")으로만 읽었다.

## 1. 본 것

- 계약: `01-plan.md` U10(333~354행) · "API 계약 — 개정 3"(152~165행) · "닉네임 규칙 — 개정 3"(167~181행) · R4-6·R4-7(397~398행) · 판정 표 #14·#15·#18. CLAUDE.md 원칙5·원칙7.
- 변경: `git diff -- web` 12파일 전부(389 추가 · 31 삭제). `git diff -U0 -- web/src/__tests__` 와 `web/e2e` 의 삭제 줄 전수.
- 주변: `web/src/api/client.ts` `apiFetch`·`RequestOptions.signalUnauthorized` · `web/src/components/ui/button.tsx` 변형 목록 · `web/playwright.config.ts`(E2E 는 `vite preview` + 가짜 API 표 — :8000 백엔드를 쓰지 않는다).
- 구현자 증거(출력만): `evidence/20261116-0712-u10-{typecheck,vitest,lint,build,e2e}.txt` · `20261116-0713-u10-mutations.txt`(19건 전부 KILLED).

## 2. 직접 실행한 명령과 결과

| 명령(접두 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> --`) | 결과 | evidence |
|---|---|---|
| `npm --prefix web run typecheck` | exit 0 | `20261116-0717-review-u10-typecheck.txt` |
| `npm --prefix web exec -- vitest run --root web` | 10파일 · **212 passed** · 실패 0 (구현자 증거 212 와 같다) | `20261116-0717-review-u10-vitest.txt` |
| `npm --prefix web run lint` | exit 0 (경고만 — 전부 U10 밖 기존 파일) | `20261116-0717-review-u10-lint.txt` |
| `npm --prefix web run build` | exit 0 | `20261116-0717-review-u10-build.txt` |
| `npm --prefix web run e2e` | **5 passed** (구현자 증거 5 와 같다) | `20261116-0717-review-u10-e2e.txt` |
| 기준선(스크래치패드의 `git archive f1ea1b4 web` 사본에서 vitest) | 191 passed → 191 + 새 시험 21(auth.test 19 · api.test 2) = 212, 수가 맞는다 | 이 문서(증거 파일 없음 — 터미널 출력으로만 확인) |
| 변이 대조군(작업 트리 사본, 무변이) | 212/212 | `20261116-0719-review-u10-mut-control.txt` |
| 변이 10건 | 검출 6 · 생존 4 (아래 표) | `20261116-0719-review-u10-mut-mutants.txt` |
| 탐침 6건(무변이 구현에 새 시험을 더해 실행) | 218/218 — 구현은 여섯 경우 모두 옳게 동작 | `20261116-0720-review-u10-mut-probes.txt` |
| 탐침을 넣은 채 생존 변이 M1·M5·M6 | 셋 다 검출(탐침 P1·P2·P3 이 실패) | `20261116-0720-review-u10-mut-probes-vs-mutants.txt` |

변이·탐침은 스크래치패드 사본 `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/review-u10/work/web/` 에서만 했다(실행기 `…/review-u10/mutate.mjs`, 치환 뒤 원복). 실행 뒤 `diff -rq`(저장소 `web` ↔ 사본, `node_modules`·`dist` 제외) 차이 0줄, `git status --short -- web` 12줄 그대로 — 저장소 무수정.

### 변이 표

| # | 변이 | 구현자가 돌렸나 | 결과 | 잡은 시험 / 비고 |
|---|---|---|---|---|
| M1 | 모드 전환 때 `generation.current++` 삭제(조회 중 전환) | 아니오 | **생존** | 기존 R4-6 ③ 시험은 결과가 온 뒤에 전환한다 → R-1 |
| M2 | 늦은 응답 폐기 조건 `!==` → `===` | 아니오(구현자는 조건 제거) | 검출 — 11 failed | 아이디·닉네임 확인 시험 6건, R4-6 ① 등 |
| M3 | 전환 때 닉네임 결과만 지우고 아이디 결과는 남김 | 아니오 | 검출 — 1 failed | "가입↔로그인 전환 때 … (R4-6 ③)" |
| M4 | `checkAvailability` 의 쿼리 키 `nickname` → `nick` | 아니오 | 검출 — 5 failed | `api.test` URL 시험 + 닉네임 확인 3건 |
| M5 | 물은 칸이 `null` 인 200 응답을 `available` 로 | 아니오 | **생존** | `?? 'failed'` 갈래를 지나는 시험이 없다 → R-2 |
| M6 | 조회 요청 값을 `trim()` 해서 보냄 | 아니오 | **생존** | 공백 붙은 값으로 조회하는 시험이 없다 → R-3 |
| M7 | 한 칸 값이 바뀌면 두 칸 결과를 다 지움 | 아니오 | 검출 — 1 failed | "칸 값을 바꾸면 그 칸의 결과만 사라진다 (R4-6 ②)" |
| M8 | 사이드바 아이디에 접두 `@` | 아니오 | 검출 — 1 failed | 사이드바 줄 글자 `'민지·minji_01·로그아웃'` 단언 |
| M9 | 버려진 응답 뒤 `checking` 을 풀지 않음 | 아니오 | 검출 — 1 failed | R4-6 ① 시험의 끝 `toBeEnabled()` |
| M10 | 가입 본문의 닉네임을 `trim()` 해서 보냄 | 아니오 | **생존** | 계획 "값은 입력 그대로" 를 고정하는 시험이 없다 → R-3 |

## 3. 판정 근거 (요청 항목 순서)

1. **계약 값 일치**
   - 타입: `types.ts` `SignupIn{username, password, nickname}` · `MeOut.nickname: string` · `AvailabilityStatus` 3값 · `AvailabilityOut` 두 필드 `| null` — U10 334행과 같다.
   - 요청: `client.ts` `signup(body: SignupIn)` → `POST /auth/signup` · `checkAvailability` → `GET /auth/availability?<준 키만>`(`q.username !== undefined` 일 때만 `set`), `signalUnauthorized: false` — 335행과 같다. `AuthScreen.tsx` 가입 본문 `{ username, nickname, password }`, 로그인 본문 `{ username, password }` 그대로.
   - 고정 문구: `AUTH_NOTICE` 새 9키와 바뀐 `rules` 를 338행과 글자 단위로 대조 — 전부 같다. `authFailureNotice` 에 `nickname_taken`·`invalid_nickname` 두 줄.
   - 화면: 칸 순서 아이디→닉네임→비밀번호→확인(시험이 `form input` 의 `name` 배열로 단언) · 닉네임 칸 `name="nickname"`·`autoComplete="nickname"`·`required`·`maxLength` 없음 · 라벨은 문구 + 입력만 감싸고 버튼은 라벨 밖 · 버튼 `type="button"`·보이는 글자 `AUTH_NOTICE.check`·`aria-label` `checkUsername`/`checkNickname` · `disabled={value.trim() === '' || checking[field]}` · 결과 줄 `role="status"` + `data-testid` `username-check`/`nickname-check`. 로그인 모드에서는 닉네임 칸·버튼이 `isSignup &&` 로 그려지지 않는다.
   - 사이드바: `AppShell.tsx` `sidebar-nickname`(`font-medium`·`truncate`) · `sidebar-username`(`text-muted-foreground`·`truncate`, 글자는 `{state.username}` 그대로) · 주석 갱신. 채팅방 목록 없음.
   - 계획에 없는 것: 문구·testid·상수 추가 0. 내부 상태 `checks`·`checking`·`latestValue`·`generation` 은 R4-6 을 구현하는 수단이라 계약 밖 추가로 보지 않는다. `CheckResult` 의 `'failed'` 는 `checkFailed` 문구에 대응한다.
2. **닫힌 목록 대조** — 삭제 줄 17개 전수:
   - F1 `auth.test.tsx:78`(도우미 서명) · F2 `:227·240·256·268`(닉네임 입력 추가) · F3 `:260`(시험 이름)·`:270`(본문 단언) · F4 `:20`(`ME`).
   - 바꿔도 되는 목 데이터: `auth.test.tsx:371` · `card.test.tsx:51` · `push.test.ts:347·404·422` · `routes.test.tsx:19` · `e2e/fixtures.ts:45` · `e2e/auth.spec.ts:10·13`.
   - 목록 밖 1줄: `api.test.ts:2` import 에 `checkAvailability` 추가 — 단언이 아니고 새 시험에 필요한 줄이다(소견 아님, R-6 에 기록 요청만).
   - `sidebar-username` 단언: 기존 5곳이 줄 번호만 밀려 그대로 있다(`auth.test.tsx:105·154·560·582`, `e2e/auth.spec.ts:32` — 삭제 줄에 없음). `auth.test.tsx` 의 `AUTH_NOTICE.rules` 참조·`username_taken` 안내 단언도 삭제 줄에 없다.
3. **R4-6 과 경합**
   - ① `onCheck` 가 `requested` 를 잡아 두고 응답 뒤 `latestValue.current[field] !== requested` 면 버린다(시험 있음, M2·M9 검출). 값을 바꿨다가 요청 때 값으로 되돌리면 받아들인다 — 같은 값에 대한 답이므로 옳다(탐침 P5).
   - ② `onChangeField` 가 그 칸 결과만 `null`(M7 검출).
   - ③ `toggle` 이 닉네임 값·`latestValue.nickname`·두 결과·두 `checking` 을 지우고 세대를 올린다(M3 검출, 구현자 변이 2건 검출).
   - ④ 새 시험은 전부 `{ exact: true }`. 새 E2E 는 없고 기존 `e2e/auth.spec.ts:27` `getByLabel('아이디')` 는 로그인 모드(중복 확인 버튼 없음)라 겹치지 않는다 — 5 passed.
   - 연타: 조회 중 버튼이 `disabled` 라 같은 칸에 요청이 겹치지 않는다. 두 칸은 서로 독립(시험이 두 칸을 연달아 누른다).
   - 조회 중 전환: 늦은 응답은 세대 불일치로 버려지고 돌아온 가입 화면의 버튼은 바로 눌린다(탐침 P1 통과). 다만 이 줄을 고정하는 시험이 없다(M1 생존, R-1).
   - 조회 중 제출: 제출은 조회와 무관하게 나간다. 가입 성공으로 화면이 내려간 뒤 늦은 응답이 와도 `console.error` 0·화면 영향 0(탐침 P4 통과 — React 19 는 언마운트 뒤 setState 를 조용히 무시).
   - 제출 실패 뒤: 결과 줄(`status`)과 오류 줄(`alert`)은 따로 관리돼 서로 지우지 않는다.
4. **구현자 판단 세 곳**
   - (가) 조회에 칸 값을 그대로 보냄: 계획과 충돌 없음. 가입 본문도 "값은 입력 그대로 — 정규화는 서버"(337행)이고 조회는 "가입과 같은 정규화 함수"(163행)라, 공백이 붙은 값으로 확인한 결과와 그 값으로 가입한 결과가 같은 정규화 값에 대한 판정이 된다. 화면에서 trim 해 보내면 오히려 R4-6 ① 의 비교 기준(칸 값)과 요청 값이 갈린다. 사용자가 보는 값과 저장 값이 달라지는 것(앞뒤 공백 제거·영문 소문자 접기)은 닉네임 규칙 표와 결정 Y 가 정한 서버 동작이고 화면이 숨기는 것이 아니다 — 가입 뒤 사이드바가 저장 값을 보인다. 시험 고정은 없다(M6·M10 생존, R-3).
   - (나) 물은 칸이 `null` 인 200 응답 → `checkFailed`: 계약 위반 응답을 "사용 가능" 으로 보이지 않는 보수적 처리이고 새 문구가 없다. 충돌 없음. 시험 고정은 없다(M5 생존, R-2).
   - (다) shadcn `Button` `variant="outline"` `size="sm"`: `ui/button.tsx` 에 이미 있는 변형이고 새 의존성·새 화면이 아니다. 계획은 버튼 모양을 정하지 않았다. 충돌 없음.
5. **401·인코딩** — `checkAvailability` 는 `signalUnauthorized: false`(`api.test` 가 401 에서 리스너 미호출을 단언, 구현자 변이 검출). 쿼리는 `URLSearchParams`: `a&b#c+d=e%f 가` → `a%26b%23c%2Bd%3De%25f+%EA%B0%80`, 되풀면 원래 값(탐침 P6). 공백은 `+` 로 가며 쿼리 문자열에서는 서버가 공백으로 읽는 표준 형식이다. 빈 문자열은 `?username=` 로 간다(화면에서는 버튼이 `disabled` 라 닿지 않는다).
6. **닉네임이 밖으로 새지 않는가(원칙7·결정 AE)** — `web/src` 의 제품 코드에서 `nickname` 은 `api/types.ts`·`api/client.ts`·`auth.tsx`(15·44·70행)·`screens/AuthScreen.tsx`·`components/AppShell.tsx`(51~52행 `AccountRow`) 뿐이다(grep). 채팅·브리핑·인물 카드 화면과 `/chat`·`/answers` 요청 본문에 없다. 가입 본문과 조회 쿼리 밖으로 나가는 요청 0.
7. **접근성·보안** — 결과 줄 `role="status"`, 오류 줄은 기존 `role="alert"` 하나(`AuthScreen.tsx:148·242`). 닉네임·아이디는 JSX 텍스트로만 그린다(`dangerouslySetInnerHTML` 0건). 비밀번호는 `onCheck` 가 읽지 않고 조회 요청·`checks`·`latestValue` 에 들어가지 않는다. `console.`·`localStorage` 쓰기 0건(grep — 일치한 3줄은 주석).

## 4. 소견

[필수] 없음.

- **R-1 [권고] 조회 중 모드 전환을 고정하는 시험이 없다.** `AuthScreen.tsx` `toggle` 의 `generation.current++` 를 지워도 212건이 통과한다(M1). 구현은 옳다(탐침 P1). 탐침 P1 과 같은 시험 1건(조회 중 → 로그인 → 가입 → 늦은 응답 → `username-check` 없음)을 더하면 닫힌다. 근거: 01-plan R4-6 ③.
- **R-2 [권고] 물은 칸이 `null` 인 응답 갈래에 시험이 없다.** `out[field] ?? 'failed'` 를 `'available'` 로 바꿔도 통과한다(M5). 잘못된 응답이 "사용할 수 있는 …" 으로 보이는 회귀를 막으려면 탐침 P2 같은 1건. 덧붙여 규약 밖 문자열(예 `"weird"`)은 지금 `invalid` 문구로 떨어진다 — 계약상 오지 않는 값이라 동작은 두되 03-log 에 한 줄.
- **R-3 [권고] "값은 입력 그대로" 가 시험으로 고정돼 있지 않다.** 조회 값(M6)·가입 본문 닉네임(M10)을 `trim()` 해 보내도 통과한다. 계획 337행이 값으로 정한 문장이므로 공백이 붙은 입력 1건으로 조회 URL(`?nickname=+…+`)과 가입 본문을 단언하면 닫힌다(탐침 P3).
- **R-4 [권고] 조회 요청에 중단·시간 제한이 없다.** 응답이 오지 않으면 그 칸의 "중복 확인" 버튼이 값을 바꿔도 계속 비활성이다(`checking[field]` 가 응답 때만 풀린다). 가입 제출은 막히지 않고(결정 AA) 모드를 한 번 오가면 풀리므로 이번 단위에서 고칠 필요는 없다. 고치려면 계획에 없는 상수(시간)가 필요하다 — 계획 변경 사항.
- **R-5 [권고] 결과 줄이 결과가 있을 때만 DOM 에 생긴다.** `role="status"` 는 계획대로지만, 내용과 함께 새로 삽입되는 라이브 영역은 일부 화면 낭독기가 읽지 않는다. 원칙5(UI 에 시간을 쓰지 않는다)에 따라 지금은 두고, 나중에 손볼 때 빈 `role="status"` 를 미리 그려 두는 방식을 고려.
- **R-6 [권고] 03-log 에 남길 것(R4-7 — 메인이 붙인다).** ① 구현자 판단 (가)(나)(다) 와 그 이유 ② Vitest 기준선 191 → 212(새 21) ③ 닫힌 목록 밖 삭제 줄 1개(`api.test.ts:2` import, 단언 아님) ④ 가입 화면 새 E2E 는 넣지 않았다(계획 342행 "일정이 남으면").
- **R-7 [권고] 커밋 뒤 판정 2건은 이 리뷰에서 실행할 수 없었다.** 계획 343행 `u10-scope`(`git diff --name-only <U10 직전 해시>..HEAD`)와 판정 표 #18 `u10-test-diff` 는 커밋 해시가 있어야 한다. 작업 트리 기준으로는 `git status --short -- web` 12파일이 계획 파일 목록 안이고 `web/` 에 새 파일(`??`)은 없다.

## 5. 확인하지 못한 것

- 서버(`app/auth/names.py`·`normalize_username`)가 실제로 계획대로 정규화하는지 — 범위 밖(U9 리뷰 몫). (가) 의 판정은 계획 문장에 기대고 있다.
- 실제 브라우저에서의 화면 모양(버튼 위치·사이드바 한 줄의 말줄임)과 화면 낭독기 동작 — U11 로컬 브라우저 점검 몫.
- 실제 백엔드와의 통합(조회·가입 왕복) — :8000 백엔드를 건드리지 않았다. U11 로컬 Caddy 스모크 몫.
- 기준선 191 은 스크래치패드 사본에서 터미널 출력으로만 확인했고 증거 파일로 남기지 않았다.
