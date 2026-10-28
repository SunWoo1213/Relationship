# P8b-persons-grid U2 사이드바 최근 5명 + "전체 보기 →" — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 4(R-U2-1 `limit` 미지정 기본 경로가 제품 호출·테스트 모두 없음, R-U2-2 조회 뒤 `nav` 링크 3+5+1 단언은 Vitest 에 없고 U3 E2E 몫, R-U2-3 registry `PersonList` 행 본문 열의 시그니처·문장 수가 낡음, R-U2-4 registry 의 "P8b U1(해시 pending)" 6곳이 U1 커밋 `2112a2a` 뒤에도 남아 있음). 코드 결함은 찾지 못했다. 내 변이 18건(계획 V2-1a·1b·2a·2b·2c·3a·3b·4·5 9건 + X6 + verifier 8건) 중 **17건 검출, 1건 생존**(XF — 제품에서 호출자가 없는 기본 경로, 동등 변이). typecheck exit 0 · Vitest **156 passed(9 files, 기준선 149 + 7)** · build 성공 · 범위 밖 diff 0 · 비밀 0 · 저장소 무수정.
대상: 작업 트리(기준 HEAD `2112a2a`(U1), 제품 코드 기준 `3bd5025`) — `git diff HEAD -- web` 3파일 +126/−6(`card.test.tsx` +105 · `AppShell.tsx` +7/−3 · `PersonList.tsx` +20/−6, scope 2b) · `docs/wiki/registry.md` 비고 3행(앱 틀·PersonList·card 테스트) · `docs/wiki/packages/P8b-persons-grid/tests.md` U2 표(신규 7 · 변경 1) · 구현 증거 `evidence/20261028-0838-u2-{sidebar,sidebar-vitest,vitest-all,build}.txt`·`20261028-0839-u2-mutation.txt`. `HANDOFF.md`·`journal.md` 의 문서 diff 는 리뷰 대상 아님. 구현자의 자기 평가는 받지 않았다.
근거 문서: `01-plan.md` 92행(U2 계약)·93~101행(변이 V2-1~V2-5)·139행(판정 4행)·183~184행(결정 E·F 확정 칸)·리스크 3·6·7 · 메인 세션 위임 사전 결정(`limit` 없으면 전원 · testid `sidebar-see-all` · R-U1-1·R-U1-5 를 이 단위에서 처리) · `docs/wiki/decisions/D15-persons-screen-layout.md` 결정 4(9행)·코드 규칙 4번째 줄(26행) · `docs/wiki/packages/P8-frontend/01-plan.md` 결정 N(330~348행) · `docs/wiki/verification.md` · `docs/wiki/security.md` · CLAUDE.md 원칙5·7.
내가 남긴 증거(모두 `docs/wiki/packages/P8b-persons-grid/evidence/`): `20261028-0847-verifier-u2-typecheck.txt` · `20261028-0847-verifier-u2-vitest-all.txt`(`--reporter=verbose` 전체) · `20261028-0847-verifier-u2-build.txt` · `20261028-0848-verifier-u2-scope.txt`(범위 9항목) · `20261028-0848-verifier-u2-d15-grep.txt`(D15·결정 E·F 코드 대조 17항목) · `20261028-0850-verifier-u2-mutation.txt`(대조군 + 변이 18건 + 탐침 PROBE-1·2 + 끝의 `git status --short web`).

---

## 1. 본 것 — 01-plan 92행 U2 계약 · 결정 E·F · D15 결정 4 대조

| 계약(글자 그대로) | 코드 위치 | 테스트(card.test.tsx) | 판정 |
|---|---|---|---|
| 결정 E: 이름 `SIDEBAR_RECENT_LIMIT = 5`, 위치 (a) `AppShell.tsx` export, `PersonList` 에 `limit` 인자 | `AppShell.tsx` 14행 `export const SIDEBAR_RECENT_LIMIT = 5` · 41행 `<PersonList onNavigate={onNavigate} limit={SIDEBAR_RECENT_LIMIT} />`(d15-grep a·b). 사용처는 이 두 줄 + 테스트 import 뿐(d15-grep k) | 550행 `expect(SIDEBAR_RECENT_LIMIT).toBe(5)` + 7명 → 5명 단언 | 일치. V2-1a(5→6)·XC(AppShell 이 상수 대신 4 를 넘김) 검출 |
| 결정 E: 자르기 `persons.slice(0, limit)`(서버 순서 그대로, 재정렬·필터 없음) | `PersonList.tsx` 34행 `const shown = limit === undefined ? persons : persons.slice(0, limit)` · `sort(`/`toSorted(`/`filter(`/`reverse(` 0건(d15-grep d) | 549행 픽스처 `SEVEN`(서버 순서 51·48·55·50·53·49·52 — 이름순·id순·날짜순 어느 쪽과도 다르고, 뒤 2명 가을·가람이 이름순·날짜 최신순 모두 앞 5명에 듦) → href 배열 정확 일치 + 가을·가람 부재 | 일치. V2-1b(자르기 제거)·V2-2a(`slice(-limit)`)·V2-2b(이름순)·V2-2c(날짜순)·V2-2d(`slice(1, limit+1)`) 전부 검출 — 2b·2c 는 U1 의 "같은 순서" 테스트(399행)와 3명 테스트도 같이 잡는다 |
| D15 결정 4: "`GET /persons` 결과의 앞 5명이고 그 아래 `#/persons` 링크 … 서버 정렬을 프론트가 재정렬하지 않는다" | 위와 같음 + 60~67행 `<a href={HREF.persons} … data-testid="sidebar-see-all">전체 보기 →</a>` 가 `</ul>` 바로 뒤, 같은 `sidebar-persons` div 안(AppShell 40~41행, d15-grep q) | 549행 `links[5]` 가 `#/persons`·텍스트 `전체 보기 →`·`sidebar-see-all` 과 같은 요소 | 일치. V2-3a(href `#/chat`)·V2-3b(링크 제거)·XD(화살표 뺌)·XG(링크를 `sidebar-persons` 밖으로) 검출 |
| 결정 F (a): 인물 1명 이상이면 항상, 0명·실패에는 없음, 글자 "전체 보기 →", 목록 바로 아래 | 23~32행 `failed`·`null`·`length === 0` 분기가 링크 앞에서 `return`(d15-grep h) | 572행 3명 + 링크 · 586행 정확히 5명(경계) · 596행 0명 링크 없음 · 606행 실패 링크 없음 | 일치. XB(0명에도 링크)·XE(실패에도 링크) 검출 |
| 서랍에서는 `onNavigate` 로 닫힘(결정 N) | 62행 `onClick={onNavigate}` — 인물 링크(42행)와 같은 방식 | 628행 800px 서랍 → `sidebar-see-all` 클릭 → `#/persons` + `주 메뉴` 사라짐 | 일치. V2-4(미연결) 검출 |
| 사이드바 자르기가 그리드에 번지지 않음 | `PersonGrid.tsx` diff 0(d15-grep i). d15-grep j 의 `slice(0, ALIAS_LIMIT)` 는 U1 별칭 2개 상한이지 인물 자르기가 아니다 | 619행 `#/persons` 7명 전원 `tileIds()` + 사이드바 링크 6개 · U1 177행 | 일치. V2-5 검출(두 테스트) |
| 위임 사전 결정: `limit` 없으면 전원 | 34행 삼항의 왼쪽 가지. 제품에서 `limit` 없이 부르는 곳은 없다(d15-grep k) | 없음 | 코드 있음, 테스트·호출자 없음(XF 생존 → R-U2-1) |
| 위임 사전 결정: testid `sidebar-see-all`(U3 E2E 가 쓴다) | 63행 | 549·572·596·606·628행 | 일치 |
| R-U1-1: 그리드 "조회 실패" 테스트에 `person-search` null 단언 1줄 | — | 371행 `expect(screen.queryByTestId('person-search')).toBeNull()` 추가(diff 1줄) | 일치. **X6 검출**(U1 에서 생존했던 변이) |
| R-U1-5: `PersonList.tsx` 머리 주석 "사이드바 전용" | 1~2행 "사이드바 전용 인물 목록(결정 N·D15 결정 4) … 앞 `limit` 명" | — | 일치 |
| `routes.test.tsx` 72~79행 기대값 확인·갱신 | — | 무수정 통과. 그 테스트는 `render` 직후 동기 단언이고 `test-setup.ts` 10~12행이 `fetch` 를 던지게 해 두어 인물이 절대 그려지지 않는다(`persons === null` 또는 `failed`) → 결정 F (a) 대로 링크 없음 → 링크 3개 그대로. tests.md 의 설명과 같다 | 일치. XG 에서 이 테스트가 깨진 것은 링크를 조건 없이 nav 에 둔 변이라 — 올바른 반응 |
| 판정 명령·증거 이름(`*-u2-sidebar.txt`·`*-u2-mutation.txt`) | 구현 증거 5파일 존재(§5) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `npm --prefix web run typecheck` | exit 0, 출력 없음 | `…-0847-verifier-u2-typecheck.txt` |
| `npm --prefix web test -- --run --reporter=verbose` | **Test Files 9 passed (9) · Tests 156 passed (156)**, `✓` 156줄, skipped/todo 0. 사이드바 describe 에 `P8b U2` 7건(verbose 335~341행) | `…-0847-verifier-u2-vitest-all.txt` |
| `npm --prefix web run build` | `✓ built in 124ms`, exit 0(`index-DB5EDvsy.js` 363.62 kB — 구현 증거와 같은 해시) | `…-0847-verifier-u2-build.txt` |
| `git diff --stat 3bd5025 -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` | 빈 출력 | scope 1 |
| `git diff --stat HEAD -- web/src/routes.ts web/src/screens web/src/components/PersonGrid.tsx web/src/api` | 빈 출력 | scope 2 |
| `git diff --stat HEAD -- web` | 3파일 +126/−6 — 위임 프롬프트의 수치와 같음 | scope 2b |
| `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v ui/` | `web/src/components/AppShell.tsx` 1파일 | scope 3 |
| `ls web/src/components/ui` | 8개(badge·button·card·collapsible·sheet·skeleton·sonner·tabs) | scope 4 |
| `grep -rnE "persons\?\|[?&](q\|limit)=" web/src --exclude-dir=__tests__` | 0건(exit 1) — `limit` 은 컴포넌트 인자일 뿐 쿼리 파라미터가 아니다 | scope 5 |
| `grep -n "export function getPersons()" web/src/api/client.ts` | 107행 1건 | scope 6 |
| `git diff --stat HEAD -- web/package.json web/package-lock.json` | 빈 출력 | scope 7 |
| 비밀 문자열 grep(diff 전체) | 0건(exit 1) | scope 8 |
| D15·결정 E·F 코드 대조 17항목(a~q) | 전부 기대값(§1 에 줄 번호로 인용). `AppShell.tsx` diff 는 상수 3줄·주석 1줄·`limit` 인자 1줄뿐(d15-grep m) — 서랍 `Sheet side="left"`·`showCloseButton={false}`·`SheetTitle` 그대로(d15-grep o) | `…-0848-verifier-u2-d15-grep.txt` |
| `git status --short web`(변이 뒤) | 리뷰 전과 같은 3파일 `M` — 저장소 무수정 | mutation 끝 |

## 3. 변이 시험 — 내가 직접 (`20261028-0850-verifier-u2-mutation.txt`)

방법: 스크래치패드 `verifier-u2/mutate.py` 가 `web/` 를 저장소 밖으로 복사(`node_modules` 는 심볼릭 링크, `dist`·`e2e` 제외)하고 변이마다 `src/` 를 새로 깐 뒤 문자열 치환(각 치환 정확히 1곳 — 아니면 중단)을 적용해 `npm --prefix <사본> test -- --run src/__tests__/card.test.tsx src/__tests__/routes.test.tsx` 를 돌린다. 구현자의 `u2/run.sh` 와 별개 디렉터리·별개 스크립트.

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군 | 없음 | **64 passed** | — |
| V2-1a 상수 5 → 6 | `AppShell.tsx` 14행 | FAIL 2 `expected 6 to be 5` | 7명 테스트 + 그리드 전원(사이드바 링크 6 ≠ 7) |
| V2-1b 자르기 제거 | `shown = persons` | FAIL 2 `Array(8) ≠ Array(6)` | 같음 |
| V2-2a `slice(-limit)` | — | FAIL 1 `아린 없음` | 7명 테스트 |
| V2-2b 이름순 정렬 후 자르기 | `[...persons].sort(localeCompare 'ko').slice(0, limit)` | FAIL 3 `['#/persons/7','#/persons/9',…] ≠ ['#/persons/7','#/persons/4',…]` | U1 같은 순서 + 7명 + 3명 |
| V2-2c 날짜 최신순 정렬 후 자르기 | `last_contact_at` 내림차순 | FAIL 3 | 같음 — 픽스처가 날짜순과도 다르게 설계된 것이 증명됨 |
| V2-2d(verifier) `slice(1, limit + 1)` | 첫 사람 빠짐 | FAIL 8 | 사이드바 describe 거의 전부(R-U6-2·R-U7-2 재조회 테스트가 첫 인물을 찾으므로) |
| V2-3a href → `#/chat` | — | FAIL 3 `'#/chat' ≠ '#/persons'` | 7명·3명·서랍 |
| V2-3b 링크 제거 | 60~67행 삭제 | FAIL 5 `Array(5) ≠ Array(6)` | 7명·3명·5명 경계·그리드 전원·서랍 |
| V2-4 `onClick={onNavigate}` 제거 | — | FAIL 1 `nav … to be null` | 서랍 닫힘 |
| V2-5 그리드에도 `slice(0, 5)` | `PersonGrid.tsx` | FAIL 2 `['51','48','55','50','53'] ≠ 7개` | U1 177행 + U2 619행 |
| **X6 (R-U1-1) 실패 상태에서 그리드가 검색창을 그림** | `PersonGrid.tsx` failed 분기 | **FAIL 1 `<input> to be null`** | 371행 — U1 에서 생존했던 변이가 이번에 잡힘 |
| XA(verifier) 링크를 `<ul>` 안 `<li>` 로 | — | FAIL 1 | U1 399행 `person-list` 안 링크 href 배열(3 → 4) |
| XB(verifier) 0명에도 링크 | — | FAIL 1 | 596행 |
| XC(verifier) AppShell 이 `limit={4}` | — | FAIL 3 `마루 없음` | 7명·5명 경계·그리드 전원 |
| XD(verifier) 글자 `전체 보기` (화살표 뺌) | — | FAIL 2 `'전체 보기' ≠ '전체 보기 →'` | 7명·3명 |
| XE(verifier) 실패 상태에도 링크 | — | FAIL 1 | 606행 |
| **XF(verifier) `limit` 미지정이면 전원 → `[]`** | 34행 왼쪽 가지 | **64 passed — 생존** | 없음 → R-U2-1 (제품에 호출자가 없어 동작 변화 0 — 동등 변이) |
| XG(verifier) 링크를 `sidebar-persons` 밖(nav 끝)으로 | `AppShell.tsx` | FAIL 7 | U2 6건(`within(side)` 범위) + `routes.test` 72행(조건 없는 링크가 나타남) |
| 탐침 PROBE-1(제품 무변경) 조회 뒤 `nav` 안 링크 수 | 7명 응답 | **2 passed** — `toHaveLength(9)` 통과 = 3 + 5 + 1 | → R-U2-2 (기존 테스트에는 이 단언이 없음) |
| 탐침 PROBE-2(제품 무변경) 5번째 인물 링크에서 Tab | — | 통과 — `document.activeElement` 가 `sidebar-see-all` | 접근성 7항 충족(§6) |

집계: 변이 18건 중 **17건 검출, 1건 생존**(XF). 계획 표 V2-1~V2-5(9종)와 X6 전부 검출. 구현자 변이 파일(`…-0839-u2-mutation.txt`)의 "잡힘" 10회와 내 재실행 결과가 같은 테스트 이름·같은 실패 수로 맞는다.

## 4. 판정 4행 대조 (01-plan 139행)

- "서버가 7명을 이름·id·날짜 어느 순서와도 다르게 줌 → `sidebar-persons` 안 인물 링크가 정확히 앞 5명·같은 순서 + 마지막 링크 '전체 보기 →' `href="#/persons"`": 549행 — 픽스처 설계는 V2-2b·2c 가 실제로 실패한 것으로 증명(§3). 충족.
- "인물 3명이면 3명 + 전체 보기(결정 F)": 572행. 충족. 경계 5명(586행)은 계획에 없던 보강.
- "좁은 폭 서랍에서 전체 보기 클릭 → 서랍 닫힘·`#/persons`": 628행 — V2-4 가 이 테스트에서만 실패해 "닫힘" 단언이 형식적이지 않음을 증명. 충족.
- "`routes.test.tsx` 72~79행 갱신 기대 통과": 무수정 통과, 이유는 §1(동기 단언 + `fetch` 차단). 충족.
- "E2E 데스크톱 `sidebar` 링크 수 = 3 + 5 + 1, 모바일 서랍 안 인물 5 + 전체 보기": **U3 몫**(`*-u3-e2e.txt`). Vitest 수준에서는 PROBE-1 로 9개임을 내가 확인했고 기존 테스트에는 그 단언이 없다(R-U2-2).

## 5. `tests.md`·`registry.md`·구현 증거

- `tests.md` U2 표 8행 ↔ `--reporter=verbose` 이름: 신규 7 = verbose 335~341행 `P8b U2 …` 7건과 1:1(7명·3명·5명 경계·0명·실패·그리드 전원·서랍). 변경 1 = U1 describe "목록 조회가 실패하면 한 줄 안내"(verbose 313행, diff 371행 1줄). 삭제 0 — `git diff` 에 `-` 줄은 `card.test.tsx` 에 없다(scope 2b `+105/−0`). 156 − 149 = 7. 표 머리의 "64 passed"는 내 대조군과 같다.
- 표의 "검출 변이" 열(V2-1a·1b·2a·2b·2c·3a·3b·4·5·X6)은 §3 의 내 결과와 테스트 단위로 일치한다.
- `registry.md` 비고 3곳: 앱 틀 행 "`SIDEBAR_RECENT_LIMIT = 5` … `limit` 로 넘김, 다른 부분 무변경"(d15-grep m 으로 확인) · `PersonList` 행 "`limit?: number` … `slice(0, limit)` … `전체 보기 →`(`href=HREF.persons`, `onNavigate`, `sidebar-see-all`; 0명·조회 실패에는 없음), 머리 주석(R-U1-5)" · 테스트 행 "신규 7건 + R-U1-1, 149 → 156" — 전부 코드·수치와 맞다. 다만 `PersonList` 행 **본문 열**은 `PersonList({onNavigate?})`·"고정 문장 3개" 그대로라 `limit?`·6키(U1 에서 3키 추가)가 빠져 있다(R-U2-3). 또 236·237·245·246·247·248행의 "**P8b U1(해시 pending)**" 은 U1 이 `2112a2a` 로 커밋된 뒤에도 치환되지 않았다(R-U2-4).
- 구현 증거: `…-u2-sidebar.txt`(typecheck exit 0) · `…-u2-sidebar-vitest.txt`(64 passed) · `…-u2-vitest-all.txt`(156 passed) · `…-u2-build.txt`(built, 같은 번들 해시) · `…-u2-mutation.txt`(V2-1a~V2-5 9종 + X6 "잡힘" 10회, 끝의 "변이 적용 확인: 2"). 내 재실행 수치와 같다.

## 6. 범위·원칙·접근성

- 원칙5: 라우트 3경로 그대로(`routes.ts` diff 0), 새 화면·패널 0, 서랍 파일 `AppShell.tsx` 1개 그대로(scope 2·3), `Sheet side="left"`·닫힘 방식 무변경(d15-grep o). 결정 N 구조(모든 폭 왼쪽, 모바일 서랍형, 항목 고르면 닫힘, 하단 탭바 없음) 침범 0.
- 원칙7: `PersonList` 표시 경로는 `{p.display_name}`·`{p.relation_tag}`·`{p.hierarchy}` 원문 + 기존 `formatDate`(d15-grep l — `toUpperCase`/`toLowerCase`/`replace(`/`trim(` 0). "전체 보기 →" 는 프론트 고정 문장(01-plan 리스크 9). 새 API·새 파라미터 0(scope 5·6).
- 범위: U0 밖 백엔드·`alembic` diff 0(scope 1), `PersonGrid.tsx`·`screens/`·`api/` diff 0(scope 2), 의존성 변경 0(scope 7), U3 몫(`web/e2e/`) 무접촉(scope 2b 에 없음). 비밀 0(scope 8).
- 접근성(7항): 링크는 `<a href>` 라 Tab 순서에 자동으로 들어가고 `sidebar-persons` div 안에 있다(d15-grep q). PROBE-2 로 5번째 인물 링크 → Tab → `sidebar-see-all` 포커스를 확인했다. 서랍에서는 Radix Dialog 포커스 트랩 안이다(기존 구조).

## 7. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U2-1 · `limit` 미지정 → 전원 기본 경로가 제품 호출자도 테스트도 없다.** 근거: §3 XF 생존(`limit === undefined ? [] : …` 로 바꿔도 64 passed), d15-grep k(`PersonList` 호출은 `AppShell.tsx` 41행 한 곳, 항상 `limit` 전달). 위임 사전 결정("limit 없으면 전원")대로 코드는 맞지만 죽은 가지다. 그대로 두려면 03-log 에 "호출자 없음" 한 줄, 살리려면 `PersonList` 단독 렌더 테스트 1건(`limit` 없이 7명 → 링크 7 + 전체 보기). 메인 세션 판단.
- **R-U2-2 · 조회가 끝난 뒤 `nav`(주 메뉴) 안 링크가 3 + 5 + 1 = 9 라는 단언이 Vitest 에 없다.** 근거: card.test U2 테스트는 전부 `within(side)`(`sidebar-persons`) 범위이고, routes.test 72~79행은 조회 전 시점이다. 01-plan 판정 4행이 이 단언을 E2E(U3)에 배정했으므로 결함이 아니다 — PROBE-1 로 지금 값이 9 임은 확인했다. **U3 에서 `card.spec.ts` 76행 `3 + PERSONS.length` 를 `3 + 5 + 1` 로 바꾸는 것을 빠뜨리지 말 것**(리스크 3).
- **R-U2-3 · `registry.md` 245행 `PersonList` 행 본문 열이 낡았다.** `PersonList({onNavigate?})` → `({onNavigate?, limit?})`, "고정 문장 3개" → 6키(U1 에서 `searchEmpty`·`searchPlaceholder`·`searchLabel` 추가). 비고 열에는 다 적혀 있어 정보 손실은 없지만 registry 의 "무엇이 있는가" 열이 코드와 어긋난다. 커밋 뒤 해시 치환 때 같이.
- **R-U2-4 · `registry.md` 의 "P8b U1(해시 pending)" 6곳(236·237·245·246·247·248행)과 247행 해시 열 `pending` 이 U1 커밋 `2112a2a` 뒤에도 남아 있다.** U2 커밋 뒤 해시 치환 때 U1 분도 함께 `2112a2a` 로. U2 코드와 무관한 메인 세션 후속.

03-log 에 적을 것(메인 세션): ① `AppShell.tsx` 변경은 상수·주석·`limit` 인자뿐(d15-grep m) · ② `routes.test.tsx` 72~79행 무수정 이유(동기 단언 + `test-setup.ts` fetch 차단 → 결정 F (a)) · ③ X6 검출로 R-U1-1 닫힘, R-U1-5 머리 주석 닫힘(`…-verifier-u2-mutation.txt` X6 블록·`PersonList.tsx` 1~2행) · ④ R-U2-1 결정 · Refs `P8b-persons-grid D15 CR-003 결정L 결정N 원칙5 R-U10C-3`.

## 8. 판정

**통과.** `AppShell.tsx` 의 `SIDEBAR_RECENT_LIMIT = 5` export 와 `PersonList` 의 `slice(0, limit)` + "전체 보기 →"(`HREF.persons`·`onNavigate`·`sidebar-see-all`, 0명·실패에는 없음)가 01-plan 92행 U2 계약·결정 E·F 확정 칸·D15 결정 4·코드 규칙 4번째 줄을 값으로 지키고(§1·§2), 내 재실행에서 typecheck exit 0 · Vitest 156 passed(9 files, 기준선 149 + 7, skip 0) · build 성공이다. 계획 변이 V2-1~V2-5 전 변종과 U1 에서 살아남았던 X6 이 전부 검출됐고, 내가 더한 8건 중 7건이 검출됐다(§3). 생존한 1건(XF)은 제품에 호출자가 없는 기본 경로의 동등 변이라 [권고]다. 범위 밖 diff 0·새 의존성 0·비밀 0·저장소 무수정·결정 N 서랍 구조 무변경. 코드에 요구하는 변경은 없다. 커밋·승인은 메인 세션·사용자 몫이다.
