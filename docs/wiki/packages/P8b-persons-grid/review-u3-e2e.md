# P8b-persons-grid U3 E2E 갱신 + 목록 폭 `boundingBox()` — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 3(R-U3-1 픽스처 별칭 순서가 U0 `sorted()` 규칙과 다름, R-U3-2 E2E 는 검색 정규화를 안 본다 — 의도대로지만 03-log 한 줄, R-U3-3 registry 257행 "P8b U3(해시 pending)" 치환). 코드(spec) 결함은 찾지 못했다. 내 변이 12건(계획 V3-1·2·3 + verifier 8건 + 탐침 1건) 중 **11건 검출, 1건 생존**(XC2 — 정규화 제거, E2E 의 검색어가 별칭과 글자 그대로 같아 생존 = 계획이 E2E 에 요구하지 않은 것, Vitest 가 잡는다). E2E **4 passed**(chat 1 · card 2 · briefing 1) · Vitest **156 passed(9 files, skip 0)** · typecheck exit 0 · 결정 J 실측 **grid 976 / main 1024 / 차 0** · 모바일 타일 x **24×6** · `web/src` diff 0 · 백엔드 diff 0 · 비밀 0 · 저장소 무수정 · 4173 포트 닫힘.
대상: 작업 트리(기준 HEAD `529922f`(U2), 제품 코드 기준 `3bd5025`) — `git diff HEAD -- web` **1파일 `web/e2e/card.spec.ts` +62/−13**(scope 3, 위임문 수치와 같음) · `docs/wiki/registry.md` 257행 비고 · `docs/wiki/packages/P8b-persons-grid/tests.md` U3 절(65행~, 표 3행) · `03-log.md` U3 항목(40~45행) · 구현 증거 `evidence/20261028-0905-u3-e2e.txt`(첫 시도 2 failed)·`-0906-u3-{e2e,vitest-all,typecheck}.txt`·`-0907-u3-mutation.txt`. `HANDOFF.md`·`journal.md` 문서 diff 는 리뷰 대상 아님. 구현자의 자기 평가는 받지 않았다.
근거 문서: `01-plan.md` 102행(U3 계약)·103~109행(V3-1~V3-3)·136~146행(판정 1·3·4·5·11행)·188행(결정 J — `abs(grid.width − (main.width − 48)) ≤ 2`)·리스크 3 · `docs/wiki/decisions/D15-persons-screen-layout.md` 코드 규칙 3·4·5번째 줄 · `docs/wiki/packages/P8-frontend/review-u10-closeout.md` R-U10C-3(62행, M4 변이) · `docs/wiki/verification.md` · `docs/wiki/security.md` · CLAUDE.md 원칙5·7.
내가 남긴 증거(모두 `docs/wiki/packages/P8b-persons-grid/evidence/`): `20261028-0913-verifier-u3-e2e.txt` · `20261028-0913-verifier-u3-vitest-all.txt`(`--reporter=verbose` 전체) · `20261028-0913-verifier-u3-typecheck.txt` · `20261028-0915-verifier-u3-mutation.txt`(대조군 + 변이 12건 + 끝의 `git status --short web`·`lsof`) · `20261028-0917-verifier-u3-scope.txt`(범위 11항목).

---

## 1. 본 것 — 01-plan 102행 U3 계약 · 결정 J · D15 코드 규칙 대조 (값으로)

| 계약(글자 그대로) | spec 위치(`web/e2e/card.spec.ts`) | 판정 |
|---|---|---|
| "픽스처 인물 6명 이상(서버 순서가 이름·id 순과 다르게)" | 10~17행 `PERSONS` 6명, 서버 순서 id `8, 3, 4, 12, 6, 9`(id 순 아님) · 이름 최지우·김팀장·이서준·박민수·정하늘·강다온(가나다 순 아님 — 강다온이 마지막) · `last_contact_at` 10-20·10-14·null·09-01·null·08-01(날짜순도 아님, null 섞임) (scope 9) | 충족. 김팀장(id 3)은 2번째 = 앞 5명 안(리스크 3 — 53·108행 사이드바 클릭 인물) |
| CI 빨강 원인 — 픽스처에 `aliases` | 11~16행 6명 전원 `aliases` 필드(scope 5). `CARD_3.aliases`(21행) = `['팀장님', '김 부장']` = 목록 12행 값·순서 동일. `chat.spec.ts` 16행·`briefing.spec.ts` 29행은 `GET /api/persons` → `[]`(scope 6) 라 `aliases` 무관 — 구현자 주장과 같음 | 충족. 단 그 순서가 U0 백엔드 규칙과 다름 → R-U3-1 |
| "데스크톱 1280px — 사이드바 인물 링크 5개 + 전체 보기, 76행 링크 수 갱신"(R-U2-2) | 77행 `sidebar.getByRole('link')` = `3 + SIDEBAR_COUNT + 1` = 9 · 78행 `sidebar-persons` 안 `a[href^="#/persons/"]` = 5 · 79행 `/강다온/` 링크 0(6번째 인물 없음) | 충족. V3-2·XH 검출(§3) |
| "전체 보기 → `#/persons` 그리드" | 82~88행 `sidebar-see-all` 클릭 → URL `/#\/persons$/` → `person-tile` 6개 → `data-person-id` 배열 = `PERSONS.map(id)`(서버 순서) | 충족. XA(5명)·XD(`#/chat`)·XF(역순) 검출 |
| **목록 폭 `boundingBox()`**(결정 J: `abs(grid.width − (main.width − 48)) ≤ 2`, 48 = `main` `p-6` 좌우) | 91~94행 `person-grid`·`main` boundingBox → `Math.abs(gridBox.width - (mainBox.width - 48))` `toBeLessThanOrEqual(2)` — 결정 J 식과 허용치·상수 동일. 93행 `console.log` 로 실측 기록(결정 J "U3 에서 실측값을 03-log 에") | 충족. 실측 976/1024/차 0(§2). V3-1 검출(차 208), PROBE-XG(§3) |
| "검색 1회(이름 또는 별칭) → 타일 클릭 → `#/persons/:id` 카드·원문 펼치기(기존 59~63행 단언 유지)" | 97~99행 `person-search` fill `'팀장님'` → 타일 1 → `data-person-id` `3` · 100~103행 클릭 → `/#\/persons\/3$/` → 카드 heading · 106~110행 = HEAD 59~63행과 **같은 단언**(`timeline-31` 펼치기 → `raw-utterance` `textContent` === `RAW_31` → `GET /api/events/31/raw` 1회). `'팀장님'` 은 `'김팀장'` 의 부분 문자열이 아니라 별칭으로만 맞는다 — XC(별칭 제외) 가 0건으로 실패한 것으로 증명 | 충족. 원문 단언은 "사이드바 클릭 카드" 뒤에서 "타일 클릭 카드" 뒤로 자리만 옮겼고(계획 102행이 그렇게 지정) 내용은 동일 |
| "모바일 390px — 서랍 안 사이드바 5명 + 전체 보기, 그리드 1열(타일 x 좌표가 모두 같음)" | 149~161행 서랍 열기 → `a[href^="#/persons/"]` 5 · `sidebar-see-all` 1 → 클릭 → `navigation` 0(서랍 닫힘) · `/#\/persons$/` → 타일 6 → `getBoundingClientRect().x` 6개 → `new Set(xs).size === 1` | 충족. V3-3(집합 2)·XE(서랍 안 닫힘)·XD·XH 검출 |
| 라우트 3경로·Esc 단언 유지 | 164~169행 그대로, URL 만 `#/persons/3` → `#/persons`(직전 단계가 그리드라 — 타당) | 충족 |
| "`expectNoStrayRequests` 유지(판정 27b)" | 112행·171행 두 테스트 모두(scope 7) | 충족 |
| D15 코드 규칙 3 "타일은 `#/persons/:id`(`href="#/persons/`)" | 99~101행 + XB(`?id=`) 검출 | 충족 |
| D15 코드 규칙 4 "앞 5명이고 그 아래 `#/persons` 링크" | 77~79·82행 · 151~153행 | 충족 |
| D15 코드 규칙 5 / R-U10C-3 "E2E `boundingBox()` 로 목록 폭 ≈ `main` 폭" | 91~94행 — R-U10C-3 의 M4(안쪽 `div` 에 `mx-auto max-w-3xl`)가 **E2E 층에서 잡힌다**(V3-1, 차 208) | 충족 — R-U10C-3 의 E2E 쪽 요구 닫힘 |
| 판정 명령·증거 이름(`*-u3-e2e.txt`·`*-u3-mutation.txt`) | 구현 증거 5파일 존재(§5) | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `lsof -nP -iTCP:4173`(실행 전·변이 끝) | 닫힘(출력 없음) | mutation 끝 |
| `npm --prefix web run e2e` | **4 passed (4.3s)** — briefing 1·chat 1·card 2, exit 0. `[U3 실측] grid.width=976 main.width=1024 차=0` · `모바일 타일 x=24,24,24,24,24,24` | `…-0913-verifier-u3-e2e.txt` |
| `npm --prefix web test -- --run --reporter=verbose` | **Test Files 9 passed (9) · Tests 156 passed (156)**, `✓` 156줄, skipped/todo 0 — U2 리뷰 때와 같은 수(U3 는 Vitest 를 바꾸지 않았다) | `…-0913-verifier-u3-vitest-all.txt` |
| `npm --prefix web run typecheck` | exit 0, 출력 없음(`tsconfig.node.json` 23행 include 에 `e2e` — spec 도 검사 대상, scope 10) | `…-0913-verifier-u3-typecheck.txt` |
| `git diff --stat HEAD -- web/src` | 빈 출력 — **제품 코드 무수정** | scope 1 |
| `git diff --stat 3bd5025 -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` | 빈 출력 | scope 2 |
| `git diff --stat HEAD -- web` | `web/e2e/card.spec.ts | 75 +++…---`, 1 file, +62/−13 | scope 3 |
| `grep -n "aliases" web/e2e/*.ts` | `card.spec.ts` 11~16행 6명 전원 + 21행 `CARD_3`; 다른 spec·fixtures 0건 | scope 5 |
| `grep -n "GET /api/persons" chat.spec.ts briefing.spec.ts` | 둘 다 `{ json: [] }` | scope 6 |
| 비밀 패턴 grep(diff 전체) | 0건(exit 1) | scope 8 |
| `git status --short web`(변이 뒤) | `M web/e2e/card.spec.ts` 뿐 — 리뷰 전과 같음, 저장소 무수정 | mutation 끝 |

## 3. 변이 시험 — 내가 직접 (`20261028-0915-verifier-u3-mutation.txt`)

방법: 스크래치패드 `verifier-u3/mutate.py` 가 `web/` 의 `e2e`·`src`·`public`·설정 파일만 저장소 밖 사본으로 복사(`node_modules` 심볼릭 링크, `dist`·`test-results` 제외)하고 변이마다 `src/` 를 새로 깐 뒤 문자열 치환(각 치환 정확히 1곳 — 아니면 중단)을 적용해 사본 디렉터리에서 `npx playwright test`(webServer 가 사본을 build·preview, 4173 순차)를 돌린다. 변이마다 `diff -r` 로 사본과 저장소 `src` 차이를 출력에 남겼다. 구현자의 `u3/run.sh` 와 별개 디렉터리·별개 스크립트.

| 변이 | 치환 | 결과 | 검출 테스트 · 다른 spec 영향 |
|---|---|---|---|
| C0 대조군 | 없음(`diff -r` 없음) | **4 passed** | — |
| V3-1 그리드 래퍼 `mt-4` div 에 `mx-auto max-w-3xl` | `PersonCardScreen.tsx` 335행 | FAIL 1 — `Received: 208`(≤ 2), 실측 `grid.width=768 main.width=1024` | **데스크톱만**. 모바일·chat·briefing 통과 |
| V3-2 `SIDEBAR_RECENT_LIMIT` 5 → 6 | `AppShell.tsx` 14행 | FAIL 2 — nav 링크 `Expected 9 Received 10` · `a[href^="#/persons/"]` `Expected 5 Received 6` | 데스크톱·모바일 둘 다(두 폭 모두 5명 단언이 있으므로 맞는 반응). chat·briefing 통과 |
| V3-3 `grid-cols-1` → `grid-cols-2` | `PersonGrid.tsx` 61행 | FAIL 1 — `new Set(xs).size` `Expected 1 Received 2` | **모바일만**. 데스크톱(xl 3열이라 무관)·chat·briefing 통과 |
| XA(verifier) 그리드에도 `slice(0, 5)` | `PersonGrid.tsx` 43행 | FAIL 2 — `person-tile` `Expected 6 Received 5` ×2 | 데스크톱·모바일. 계획 V2-5 를 E2E 층에서도 잡음 |
| XB(verifier) 타일 href → `#/persons?id=<id>` | `PersonGrid.tsx` 67행 | FAIL 1 — `toHaveURL /#\/persons\/3$/` ← `"…/#/persons?id=3"` | 데스크톱만(모바일은 타일을 클릭하지 않음) |
| XC(verifier) 검색이 별칭을 안 봄(`[p.display_name]` 만) | `PersonGrid.tsx` 42행 | FAIL 1 — `person-tile` `Expected 1 Received 0` | 데스크톱만. **E2E 검색이 별칭으로 맞는다는 증명** |
| **XC2(verifier) 검색 정규화 제거(`return s`)** | `PersonGrid.tsx` 15행 | **4 passed — 생존** | 없음. 검색어 `'팀장님'` 이 별칭과 글자 그대로 같아 정규화 없이도 맞는다. 계획 102행은 "검색 1회" 만 요구, 정규화 경계는 판정 2행 Vitest(verbose 305행)가 본다 → R-U3-2 |
| XD(verifier) 전체 보기 href → `#/chat` | `PersonList.tsx` 61행 | FAIL 2 — `toHaveURL /#\/persons$/` ← `"…/#/chat"` ×2 | 데스크톱·모바일 |
| XE(verifier) 전체 보기 `onClick={onNavigate}` 제거 | `PersonList.tsx` 62행 | FAIL 1 — `navigation` `Expected 0 Received 1`(서랍 안 닫힘) | **모바일만**(데스크톱은 서랍이 없음). 계획 V2-4 를 E2E 층에서도 잡음 |
| XF(verifier) 그리드 타일 역순 | `PersonGrid.tsx` 62행 `[...visible].reverse()` | FAIL 1 — `toEqual` 배열 불일치(−5/+5) | 데스크톱만(모바일은 순서 단언 없음 — 1열·개수만) |
| XH(verifier) 전체 보기 링크 제거 | `PersonList.tsx` 60~67행 | FAIL 2 — nav 링크 `Expected 9 Received 8` · `sidebar-see-all` `Expected 1 Received 0` | 데스크톱·모바일 |
| PROBE-XG(탐침) `main` `p-6` → `p-8` | `AppShell.tsx` 144행 | FAIL 1 — `Received 16`(실측 `grid.width=960`), 모바일 x 32×6(집합 1이라 통과) | 데스크톱만. 결정 J 의 상수 48 이 `main` 의 `p-6` 에 묶여 있음을 확인 — 패딩이 바뀌면 spec 90행 주석대로 48 도 바꿔야 한다(결함 아님, 결정 J 가 그렇게 정의) |

집계: 변이 12건(탐침 제외 11 + 탐침 1) 중 **11건 검출, 1건 생존**(XC2). 계획 V3-1·V3-2·V3-3 전부 검출되고 각각 계획 표가 지정한 판정 행(5행 데스크톱 폭 / 4행 사이드바 링크 수 / 1행 모바일 1열)의 단언에서 실패했다. chat·briefing spec 은 13회 실행 전부 통과 — 변이가 card.spec 밖으로 번지지 않는다. 구현자 변이 파일(`…-0907-u3-mutation.txt`)의 V3-1 차 208·V3-2 10/6·V3-3 집합 2 와 내 재실행 값이 같다.

## 4. 첫 시도 실패(`…-0905-u3-e2e.txt`)와 수정의 타당성

- 실패: 78행·151행 `sidebar-persons` 안 `getByRole('link')` `Expected 5 Received 6`(2 failed, 다른 2편 통과).
- 원인: `AppShell.tsx` 40~42행 `data-testid="sidebar-persons"` div 가 `<PersonList>` 를 통째로 감싸고, `PersonList.tsx` 59~67행은 `</ul>` 바로 뒤 같은 div 안에 "전체 보기 →"(`href="#/persons"`)를 그린다 — U2 가 D15 결정 4 "그 아래 `#/persons` 링크" 대로 만든 구조다. U2 Vitest 도 같은 방식으로 6개를 센다(`card.test.tsx` 592행·625행 `within(side).getAllByRole('link')).toHaveLength(6)`). 즉 제품 결함이 아니라 spec 의 셈이 틀렸던 것.
- 수정: 인물 링크를 `a[href^="#/persons/"]`(끝 슬래시 포함 — `#/persons` 자체는 제외)로 세고(78·151행), 전체 보기는 따로 `sidebar-see-all` 1개(152행)와 nav 총수 9(77행)로 센다. 제품 코드 무수정(scope 1). D15 규칙("앞 5명 + 그 아래 `#/persons` 링크")과 모순이 아니라 그 규칙을 둘로 나눠 세는 것이고, V3-2(6명 → 인물 링크 6 FAIL)·XH(링크 제거 → see-all 0 FAIL)가 두 셈이 각각 살아 있음을 보였다. 타당.

## 5. `tests.md`·`registry.md`·`03-log.md`·구현 증거 대조

- `tests.md` 65행~ U3 절: "변경 2편 · 신규 0 · 삭제 0" — diff 에 `test(` 추가·삭제 없음(+62/−13 은 기존 2 테스트 본문 변경). 표 1행(데스크톱)의 "링크 9(3+5+1), 인물 링크 5·강다온 없음 · V3-2 / … 타일 6개 id `[8,3,4,12,6,9]` / `abs(grid.width − (main.width − 48)) ≤ 2` · V3-1 / 별칭 `팀장님` 검색 1회 → 타일 1(id 3) → … 원문 단언 / `expectNoStrayRequests`" ↔ spec 77~112행 1:1. 표 2행(모바일)의 "인물 링크 5(`a[href^="#/persons/"]`)·`sidebar-see-all` 1개 · V3-2 / 서랍 닫힘·`#/persons` / `getBoundingClientRect().x` 집합 크기 1(실측 24) · V3-3 / Esc 단언 URL `#/persons`" ↔ 151~169행 1:1. 표 3행 chat·briefing 무변경 ↔ scope 3·6. 머리의 "4 passed · Vitest 156 · typecheck 0 · 976/1024/차 0" = 내 §2 수치.
- `registry.md` 257행 비고 "**P8b U3(해시 pending)**: 픽스처 6명(서버 순서 ≠ 이름·id 순, `aliases` 포함 — CI 빨강 해소), 데스크톱 … 9 → `sidebar-see-all` → 그리드 6타일 → 별칭 검색 1회 → 타일 → 카드·원문 펼치기, `boundingBox` 폭(976 / 1024, 차 0 ≤ 2px), 모바일 서랍 5명+전체 보기·그리드 1열(x 모두 24). 변이 V3-1~3 검출" — 전부 spec·증거와 맞다. 해시는 커밋 뒤 치환(R-U3-3).
- `03-log.md` 40~45행 U3 항목: "제품 코드 무수정" = scope 1 · "`CARD_3.aliases` 와 목록 값·순서 동일" = 12·21행 · "grid.width=976, main.width=1024, −48=976 → 차 0(허용 2px 그대로)" = 구현 `…-0906-u3-e2e.txt` 와 내 `…-0913-verifier-u3-e2e.txt` 동일 · "모바일 x = 24×6" 동일 · "V3-1 차 208 FAIL(데스크톱만) · V3-2 링크 10/인물 6 FAIL(데스크톱·모바일) · V3-3 x 집합 2 FAIL(모바일만) · 대조군 4 passed" = `…-0907-u3-mutation.txt` 와 내 §3 동일 · "`git status --short web` = `M web/e2e/card.spec.ts` 뿐" = 내 mutation 끝 출력 동일 · "관찰: `sidebar-persons` 가 전체 보기까지 감싼다(링크 6) — `a[href^="#/persons/"]` 로 센다" = §4. 수치 불일치 없음. Refs 에 `R-U10C-3`·`R-U2-2` 포함 — 둘 다 이 단위에서 닫힌다.
- 구현 증거 5파일: `…-0905-u3-e2e.txt`(exit 1, 2 failed — 원인 기록용) · `…-0906-u3-e2e.txt`(exit 0, 4 passed, 실측 2줄) · `…-0906-u3-vitest-all.txt`(156) · `…-0906-u3-typecheck.txt`(exit 0) · `…-0907-u3-mutation.txt`(대조군 + V3-1·2·3, 각 변이 `diff -r` 1곳). 전부 머리줄 5개 + 출력 전체(FIX-034 형식).

## 6. 범위·원칙·보안

- 원칙5: 라우트 3경로 그대로 — spec 164~169행 단언 유지, `web/src` diff 0, 새 화면·패널 0. 결정 N 서랍 구조(모바일 서랍형·항목 고르면 닫힘·하단 탭바 없음)를 spec 이 그대로 단언(125~126·135·146·154행).
- 원칙7: spec 은 서버 문자열을 가공해 비교하지 않는다 — 타일 id 는 `data-person-id` 속성, 원문은 `textContent` 완전 일치(R-U9a-1 유지), 검색어는 사용자 입력.
- 범위: 변경 파일 1개(`web/e2e/card.spec.ts`), `web/src`·`app`·`alembic`·`package*.json`·`fixtures.ts`·다른 spec 무접촉(scope 1~6). 계획 102행이 지정한 것 밖의 추가 0. 비밀 0(scope 8). 외부 요청 0(`expectNoStrayRequests` 두 테스트, 통과).
- 보안: `.env` 안 읽음, 네트워크 없음(가짜 API), 저장소 밖 사본만 변이, 끝에 무수정 확인.

## 7. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U3-1 · 픽스처 별칭 순서가 U0 백엔드 규칙과 다르다.** `card.spec.ts` 12행·21행 `['팀장님', '김 부장']` — U0 `app/api/read.py` 176행·188행은 `sorted()` 코드포인트 순이라 실제 서버는 `['김 부장', '팀장님']` 을 준다(`python3 -c "print(sorted(['팀장님','김 부장']))"` → `['김 부장', '팀장님']`). 이 단위의 어떤 단언도 별칭 순서에 걸리지 않아(검색은 `some`, 타일 별칭 칸은 단언 없음) 결과에 영향 0 — 픽스처 사실성만의 문제. 다음에 spec 을 만질 때(U4 또는 뒤) 두 줄을 `['김 부장', '팀장님']` 로. 메인 세션 판단.
- **R-U3-2 · E2E 는 검색 정규화(결정 C)를 보지 않는다 — 의도대로.** §3 XC2 생존. 계획 102행은 "검색 1회(이름 또는 별칭)" 만 요구하고 정규화 경계는 판정 2행 Vitest(verbose 305행)가 맡는다. 코드 변경 불필요 — 03-log 에 "E2E 검색은 별칭 정확 일치 1회, 정규화는 Vitest" 한 줄. (같은 자리에 PROBE-XG 관찰 — 결정 J 의 48 은 `main` `p-6` 에 묶임, 패딩을 바꾸면 spec 90~94행도 함께 — 한 줄.)
- **R-U3-3 · `registry.md` 257행 "P8b U3(해시 pending)" 은 커밋 뒤 해시로 치환.** R-U2-4 와 같은 후속(메인 세션).

03-log 에 적을 것(메인 세션): ① verifier 재실행 4 passed · 156 · typecheck 0 · 실측 976/1024/0 · 24×6 동일 · ② 변이 12건 중 11 검출(계획 3 + XA·XB·XC·XD·XE·XF·XH + 탐침 XG), 생존 XC2 = R-U3-2 · ③ R-U10C-3 의 E2E 쪽(V3-1 = M4 검출)과 R-U2-2(77행 9 단언) 닫힘 · ④ R-U3-1 결정 · Refs `P8b-persons-grid U3 D15 CR-003 결정L 결정N 원칙5 R-U10C-3 R-U2-2`.

## 8. 판정

**통과.** `web/e2e/card.spec.ts` 만 바뀌었고(+62/−13, `web/src`·백엔드 diff 0), 01-plan 102행 U3 계약의 요소 전부 — 6명 픽스처(서버 순서 ≠ 이름·id·날짜 순, 전원 `aliases` → CI 빨강 원인 해소), 데스크톱 nav 링크 9 = 3+5+1(R-U2-2)·인물 링크 5·6번째 인물 없음, `sidebar-see-all` → `#/persons` 그리드 6타일 서버 순서, 결정 J 식 그대로의 `boundingBox()` 단언(허용치 2·상수 48, 실측 976/1024/차 0), 별칭 검색 1회 → 타일 1 → 클릭 → `#/persons/3` → HEAD 59~63행과 같은 원문 단언, 모바일 서랍 5명+전체 보기·서랍 닫힘·타일 x 집합 1(24×6), 라우트 3경로·Esc, `expectNoStrayRequests` 두 테스트 — 를 값으로 지킨다(§1). 내 재실행 E2E 4 passed · Vitest 156 · typecheck 0(§2). 계획 변이 V3-1·2·3 이 각각 계획이 지정한 판정 행의 단언에서만 실패하고, 내가 더한 8건 중 7건이 검출됐으며(§3), 생존 1건(XC2)은 계획이 E2E 에 요구하지 않은 정규화 경계다. 첫 시도 실패의 수정은 제품이 아니라 spec 의 셈이고 D15 규칙과 모순이 없다(§4). `tests.md`·`registry.md`·`03-log.md` 의 수치가 구현 증거·내 증거와 전부 같다(§5). 코드에 요구하는 변경은 없다. 커밋·승인은 메인 세션·사용자 몫이다.
