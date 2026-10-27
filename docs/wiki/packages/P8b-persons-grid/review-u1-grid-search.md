# P8b-persons-grid U1 인물 화면 카드 그리드 + 이름·별칭 검색 + 폭 단언 보강 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 5(R-U1-1 조회 실패 상태의 검색창 부재를 테스트가 안 봄, R-U1-2 `aliases` 없는 응답이면 렌더 크래시 — 배포 순서 메모, R-U1-3 `Card size="sm"` 은 grep 으로만 보호, R-U1-4 tests.md 변경 행의 P8 행 번호 표기, R-U1-5 registry `PersonList` 행 본문 서술). 코드 결함은 찾지 못했다. 내 변이 22건 중 20건 검출(대조군 43 passed) — 계획 변이 V1-1~V1-11 전부(P8 에서 살아남은 M4 = V1-6 포함) 검출. typecheck exit 0 · Vitest 149 passed(9 files, 기준선 137 + 12) · build 성공 · 범위 밖 diff 0 · 비밀 0.
대상: 작업 트리(기준 HEAD `adc650e`, 제품 코드 기준 `3bd5025`) — `git diff HEAD -- web`(`card.test.tsx` 326 · `types.ts` 2 · `PersonList.tsx` 4 · `PersonCardScreen.tsx` 4, 합계 +281/−55) + 신규 `web/src/components/PersonGrid.tsx`(100행) · `docs/wiki/registry.md` 비고(신규 "인물 그리드" 행 + 비고 4곳 "P8b U1(해시 pending)") · `docs/wiki/packages/P8b-persons-grid/tests.md` U1 표(24행) · 구현 증거 `evidence/20261027-1623-u1-{grid,grid-vitest,vitest-all,build,grep2,mutation}.txt`. `HANDOFF.md`·`journal.md`·`01-plan.md` 의 문서 diff 는 리뷰 대상 아님(01-plan 은 결정 B·D 비고에 "U1 해석(사용자 수용 2026-10-28)" 이 더해진 것만 읽었다 — 다른 줄 변경 없음).
근거 문서: `01-plan.md` 76행(U1 계약·testid 4종·R-6 (a)) · 77~91행(변이 V1-1~V1-11) · 136~142행(판정 1·2·3·5·7행) · 179~189행(결정 A~J, B·D 의 U1 해석 6가지) · 35~46행("하지 않는 것") · `docs/wiki/decisions/D15-persons-screen-layout.md` 결정 1·2·3·5·6 + "코드에서 지켜야 할 것" 2·3·5·7번째 줄 · `docs/wiki/packages/P8-frontend/review-u10-closeout.md` 42행(M4 생존)·62행(R-U10C-3) · `docs/wiki/packages/P8-frontend/tests.md` 189~194·201·454~455행(`card.test.tsx` P8 행) · `docs/wiki/verification.md` 79~87행(변이 규칙) · `docs/wiki/security.md` · CLAUDE.md 원칙5·7.
내가 남긴 증거(모두 `docs/wiki/packages/P8b-persons-grid/evidence/`): `20261028-0820-verifier-u1-typecheck.txt` · `20261028-0820-verifier-u1-vitest-all.txt`(`--reporter=verbose` 전체) · `20261028-0820-verifier-u1-build.txt` · `20261028-0820-verifier-u1-scope.txt`(범위 9항목) · `20261028-0820-verifier-u1-d15-grep.txt`(D15 코드 규칙 grep 16항목) · `20261028-0822-verifier-u1-mutation.txt`(대조군 + 변이 22건 + 탐침 X7 + 끝의 `git status --short web`).

---

## 1. 본 것 — 01-plan 76행 U1 계약 · 결정 A~J 대조

| 계약(01-plan 76행·결정표 글자 그대로) | 코드 위치 | 테스트(card.test.tsx) | 판정 |
|---|---|---|---|
| `PersonGrid` 신설(결정 I (나)), `usePersons()` 값을 검색어로 거른 뒤(결정 C — `Array.prototype.filter` 만, 순서는 서버 그대로) | `PersonGrid.tsx` 25행 `usePersons()` · 40~43행 `const visible = q ? persons.filter(...) : persons` — `sort`·`toSorted`·`reverse` 0(d15-grep d) | 236행 `검색: 이름 일부 → … 서버 순서 유지` — 서버 순서 `['30','21','25','12']` 가 이름순과 다르게 설계됨(`'선영 과장님' < '최선영'`) · 333행 소스 검사 `.sort(` 0 | 일치. V1-4(`toSorted` 로 소스 검사 우회)·V1-4b(`.sort(`) 모두 검출(§3) |
| shadcn `Card` 를 `<a href="#/persons/:id">` 로 감싼 타일(결정 A·H) · U1 해석 `Card size="sm"` + hover/focus-visible 토큰 | 65~72행 `<a href={`${HREF.persons}/${p.id}`} … className="block rounded-xl focus-visible:outline-2 focus-visible:outline-ring"><Card size="sm" className="h-full hover:bg-accent">` — `HREF.persons = '#/persons'`(`routes.ts` 11행) | 360행 href 배열 `['#/persons/7','#/persons/4','#/persons/9']`·전부 `<a>`·클릭 → `#/persons/4` · 369행 키보드 Tab·Enter | 일치. V1-5 검출(href 테스트 + 키보드 테스트 둘 다). `size="sm"` 은 테스트가 안 봄(X10 생존 → R-U1-3) |
| 타일 필드 이름·태그·위계·마지막 접촉(`formatDate`·`noContact` 재사용)·별칭(결정 B·K) | 74~89행 `data-field` 5종, 83행 `formatDate`/`PERSON_LIST_NOTICE.noContact` | 148행 4필드 값·순서 · 176행 별칭 | 일치 |
| 결정 B U1 해석: `별칭1 · 별칭2 +n`, n = 이름과 같은 별칭 뺀 개수 − 2, 보일 별칭 0개면 칸 없음 | 19~22행 `tileAliases`: `rest = aliases.filter(a => a !== displayName)`(완전 일치만 제외), `shown = rest.slice(0, 2)`, `more = rest.length − 2` · 85~89행 `shown.length > 0 &&` · `more > 0 ? ' +n' : ''` | 176~187행: `['대리님','박대리','박 대리','Park']`/이름 `박대리` → `'대리님 · 박 대리 +1'`, 같은 별칭뿐 → 칸 없음, 정확히 2개 → `'가 · 나'`(+0 없음) | 일치. V1-9a·V1-9b·X2(오프바이원)·X9(`+0` 표시) 전부 이 한 테스트가 검출 |
| 검색창 `<input type="search">` 1개(결정 D 문구·`aria-label`), 기존 토큰 클래스만(결정 I (ㄱ)) | 47~55행 — `type="search"`·`aria-label={PERSON_LIST_NOTICE.searchLabel}`·`placeholder={…searchPlaceholder}`·클래스 `w-full rounded-md border border-input bg-background px-3 py-2 text-sm` · `ui/input.tsx` 내려받기 없음(scope 4: ui 8개 그대로, `git status` 빈 출력) | 222행 searchbox 1·combobox/listbox/radio/checkbox/switch 0·`aria-label "인물 검색"`·placeholder `이름이나 별칭으로 찾기` | 일치. V1-10(`<select>` 추가)·X5(`type="text"`) 검출 |
| 0건이면 결정 D 문구 1줄 `찾는 인물이 없어요.`(`data-testid="person-grid-empty"`) | 56~59행 | 293행 `person-grid-empty` 1개·텍스트·그리드 사라짐·검색창 남음 | 일치. V1-8 검출 |
| 빈·실패 상태는 기존 `empty`·`failed` 재사용 · U1 해석: 그때 검색창을 그리지 않음 | 28~38행 — `failed` → `<p role="status">` 만, `length === 0` → `<p>` 만 | 346행 빈 목록: `person-search` 없음 단언 있음 · 353행 실패: `person-grid` 없음만 단언, `person-search` 없음은 **안 봄** | 코드 일치. 실패 상태 검색창은 테스트 공백(X6 생존 → R-U1-1) |
| 검색어는 컴포넌트 상태(결정 G) | 26행 `useState('')` · `localStorage`·`location.hash`·`history` 0(d15-grep m) | 304행 해시 불변·`localStorage.length === 0` | 일치 |
| 결정 C (a): 비교용으로만 `trim`+`toLowerCase`+안쪽 공백 제거, 대상 `display_name`·`aliases[]`, `includes`, 빈/공백뿐 = 전원 | 14~16행 `normalizeForMatch` 한 곳, 40·42행 비교에만 호출(d15-grep e·f: `toLowerCase`·`trim`·`replace` 가 15행 한 줄에만) · 42행 `[p.display_name, ...p.aliases].some(t => normalizeForMatch(t).includes(q))` | 263행 6가지 경계(앞뒤 공백·이름 안쪽 공백·질의 안쪽 공백·질의 대문자·별칭 안쪽 공백·별칭 대문자) · 280행 공백뿐 → 전원 · 252행 태그 글자로는 0건 | 일치. V1-1·V1-2·V1-3a·V1-3b(소스 검사 우회)·X1(`startsWith`)·X4(질의 정규화 생략) 전부 검출 |
| R-6 (a): `isComposing`·`compositionend`·NFC/NFD 없음 | d15-grep l: 0건 | — | 일치 |
| testid 고정(R-5): `person-grid`·`person-tile`(`data-person-id`)·`person-search`·`person-grid-empty` | d15-grep k: 49·57·61·68행 4종 · 69행 `data-person-id={p.id}` | 85행 `tileIds()` 가 모든 순서 단언의 기반 | 일치. X3(index 로 치환) 10건 실패로 검출 |
| 결정 A 열 `grid-cols-1 md:grid-cols-2 xl:grid-cols-3`·`gap-4` | 61행 | 164행 클래스 5개 + 7명 전원 | 일치 |
| `PersonCardScreen.tsx` 목록 분기만 교체(상세 `card-wrap` 무변경) | diff 4행: import 1줄 + `<PersonList />`→`<PersonGrid />` 1줄 · `card-wrap` 줄 `git diff 3bd5025` 변경 0(d15-grep h) | 211행 상세 테스트 무수정 | 일치. V1-11 검출 |
| `card.test.tsx` "인물 목록" describe 재작성 + R-U10C-3 조상 검사(결정 J) | — | 189~209행: `grid → … → main` 조상 사슬 + `section` 자손 중 그리드를 감싼 요소 전부(`wrappers.length ≥ 2` 로 바깥 `div.mt-4` 와 `PersonGrid` 바깥 `div` 가 포함됨을 강제) + `section` 에 `mx-auto`·`max-w-*`·`md:w-*` 0 | 일치. **V1-6(P8 M4 그대로)·V1-6b·V1-7 검출**(§3) |
| `types.ts` `PersonListItemOut.aliases: string[]` 동기화 | diff +2(주석 1·필드 1), 필수 필드 | 픽스처 전부 `aliases` 포함(typecheck 가 강제) | 일치 |
| 판정 명령·증거 이름 | 구현 증거 6파일 존재(§5) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `npm --prefix web run typecheck` | exit 0, 출력 없음 | `20261028-0820-verifier-u1-typecheck.txt` |
| `npm --prefix web test -- --run --reporter=verbose` | **Test Files 9 passed (9) · Tests 149 passed (149)**, skipped/todo/only 0. 파일별 api 6·briefing 19·card **43**·chat 22·network 2·proxy 6·push 21·routes 14·sw 16 = 149. 기준선 137 + 12 | `20261028-0820-verifier-u1-vitest-all.txt` |
| `npm --prefix web run build` | `✓ built in 172ms`, exit 0 (`index-CU34w3TP.js` 363.32 kB) | `20261028-0820-verifier-u1-build.txt` |
| `git diff --stat 3bd5025 -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` | 빈 출력 | scope 1 |
| `git diff --stat HEAD -- web/src/routes.ts …ChatScreen.tsx …BriefingScreen.tsx …AppShell.tsx` (및 `3bd5025` 기준) | 둘 다 빈 출력 | scope 2·2b |
| `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v ui/` | `web/src/components/AppShell.tsx` 1파일 | scope 3 |
| `ls web/src/components/ui` · `git status --short web/src/components/ui` | 8개(badge·button·card·collapsible·sheet·skeleton·sonner·tabs) · 빈 출력 | scope 4 |
| `grep -rnE "persons\?\|[?&](q\|limit)=" web/src --exclude-dir=__tests__` | 0건(exit 1) | scope 5 |
| `grep -n "export function getPersons()" web/src/api/client.ts` | `107:export function getPersons(): Promise<PersonListItemOut[]> {` 1건 | scope 6 |
| `git diff --stat HEAD -- web/package.json web/package-lock.json` | 빈 출력(의존성 변경 0) | scope 8 |
| 비밀 문자열 grep(diff + `PersonGrid.tsx`) | 0건(exit 1) | scope 9 |
| D15 코드 규칙 grep 16항목(`<select`·`role=combobox` 0 · `<input` 1 · `href` 는 `HREF.persons` · `sort(` 0 · 정규화 3종이 15행 한 줄 · 이름 칸 자식 0 · `card-wrap` 1건 무변경 · 목록 분기 조상에 `max-w`/`mx-auto` 0 · `PersonGrid` 안 `max-w-`/`mx-auto`/`md:w-` 0 · testid 4종 · `isComposing` 0 · `localStorage` 0 · `PersonList.tsx` diff 는 상수 3키만) | 전부 기대값 | `20261028-0820-verifier-u1-d15-grep.txt` |
| `git status --short web`(변이 뒤) | 리뷰 전과 같은 5파일(M 4 · ?? 1) — 저장소 무수정 | mutation 끝 |

## 3. 변이 시험 — 내가 직접 (`20261028-0822-verifier-u1-mutation.txt`)

방법: 스크래치패드 `verifier-u1/mutate.py` 가 `web/` 를 저장소 밖으로 복사(`node_modules` 는 심볼릭 링크, `dist`·`e2e` 제외)하고 변이마다 `src/` 를 새로 깐 뒤 문자열 치환(각 치환 정확히 1곳 — 아니면 중단)을 적용해 `npm --prefix <사본> test -- --run src/__tests__/card.test.tsx` 를 돌린다. 구현자의 `u1/mut.py` 와 별개 디렉터리·별개 스크립트. 저장소 무수정(끝의 `git status --short web`).

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군 | 없음 | **43 passed** | — |
| V1-1 필터 제거 | `persons.filter(...)` → `persons` | FAIL 7 | 검색 5건 + 0건 + 원칙7 |
| V1-2 별칭 제외 | `[p.display_name, ...p.aliases]` → `[p.display_name]` | FAIL 4 | 별칭 일부·태그 글자·정규화·원칙7 |
| V1-3a 정규화 본문 제거 | `return s` | FAIL 4 | 정규화·공백뿐·원칙7·소스 검사 |
| V1-3b(verifier) 안쪽 공백 제거만 무력화(토큰 수 유지, 소스 검사 우회) | `.replace(/\s+/g,'')` → `.replace(/^$/,'')` | FAIL 1 `[] ≠ ['25']` | 정규화(`선영과장님`) — 소스 검사가 아니라 **동작** 테스트가 잡음 |
| V1-4 이름순 정렬 — `toSorted`(소스 검사 `.sort(` 우회) | 렌더 직전 `[...visible].toSorted(localeCompare 'ko')` | FAIL 7 `['박대리','엄마','철수'] ≠ ['박대리','철수','엄마']` 외 | 4필드·이름 검색·정규화·공백뿐·href·키보드·사이드바 동일 순서 |
| V1-4b `.sort(` | 같은 자리 `.sort(` | FAIL 8(위 7 + 소스 검사) | — |
| V1-5 href `#/persons?id=` | — | FAIL 2 `'#/persons?id=4' ≠ '#/persons/4'` | href 테스트 + **키보드 Enter 테스트**(Enter 가 실제로 href 로 이동함을 증명) |
| **V1-6 안쪽 래퍼 `div.mt-4` 에 `mx-auto max-w-3xl`(P8 M4)** | `PersonCardScreen.tsx` 336행 | **FAIL 1** `expected true to be false` | 조상 검사(189행) — **P8 에서 생존한 변이, 이번엔 검출** |
| V1-6b(verifier) `PersonGrid` 바깥 `div` 에 `mx-auto max-w-3xl` | 46행 | FAIL 1 | 조상 검사 |
| V1-7 `section` 에 `max-w-4xl` | — | FAIL 1 | 조상 검사 |
| V1-8 0건 문구 미표시 | `visible.length === 0 ?` → `false ?` | FAIL 1 | 0건 |
| V1-9a `ALIAS_LIMIT = 3` | — | FAIL 1 `'대리님 · 박 대리 · Park' ≠ '… +1'` | 별칭 |
| V1-9b 같은 별칭 제외 제거 | `filter(...)` → `slice()` | FAIL 1 `'대리님 · 박대리 +2'` | 별칭 |
| V1-10 태그 `<select>` 추가 | input 뒤 | FAIL 2 | 컨트롤 1개 + 키보드(Tab 순서 깨짐) |
| V1-11 상세 `md:w-3/4` → `md:w-1/2` | — | FAIL 1 | 상세 상태 |
| X1(verifier) `includes` → `startsWith` | — | FAIL 5 `['25'] ≠ ['30','25']` | 이름 검색 외 |
| X2(verifier) `+n` 오프바이원 | `− ALIAS_LIMIT + 1` | FAIL 1 `'+2' ≠ '+1'` | 별칭 |
| X3(verifier) `data-person-id` 를 index 로 | 2곳 치환 | FAIL 10 `['0','1','2'] ≠ ['7','4','9']` | `tileIds()` 기반 전부 |
| X4(verifier) 질의 정규화 생략 | `const q = query` | FAIL 2 `[] ≠ 전원` | 공백뿐·정규화 |
| X5(verifier) `type="search"` → `"text"` | — | FAIL 1 `searchbox` 없음 | 컨트롤 |
| **X6(verifier) 조회 실패 상태에서도 검색창을 그림** | `failed` 분기에 `<input data-testid="person-search">` 추가 | **43 passed — 생존** | 없음 → R-U1-1 |
| X9(verifier) `more >= 0` 이면 `' +0'` 표시 | — | FAIL 1 `'가 · 나 +0'` | 별칭 |
| **X10(verifier) `Card size="sm"` → `"default"`** | — | **43 passed — 생존** | 없음 → R-U1-3 |
| X7 탐침(제품 무변경, 테스트만 추가) `aliases` 키 없는 응답 | 픽스처 `{id, display_name, relation_tag, hierarchy, last_contact_at}` | 렌더 중 **`TypeError: Cannot read properties of undefined (reading 'filter')`**(`tileAliases` 20행) | → R-U1-2 |

집계: 변이 22건(계획 11 + 보강 2 + verifier 9) 중 **20건 검출, 2건 생존**(X6·X10 — 둘 다 코드는 규칙대로이고 테스트 공백). 계획 표 V1-1~V1-11 은 전부 검출.

## 4. 판정 행 대조 (01-plan 136~142행)

- **1행**(`getPersons` 무인자·`?q=`/`?limit=` 0·백엔드 diff 0·`#/persons` 진입 시 `/api/persons` 1회·타일 5필드 서버 값·결정 A·5명 넘게 전원): scope 1·5·6 + 148행(`fetch` URL 목록 `['/api/persons']` 정확히 1회)·164행(7명 전원) — 충족.
- **2행**(searchbox 1·combobox 등 0·`<select` 0·이름 일부·별칭 일부·태그 글자로는 안 나옴·정규화 경계·빈 검색어 전원·0건 문구·서버 순서): 222·236·245·252·263·280·293행 + d15-grep a — 충족. 태그 테스트(252행)는 `'직장'` → 0건과 `'친구'`(최선영의 태그이자 별칭 `엄마친구` 의 일부) → `['12']` 로 "태그는 대상 아님·별칭은 대상" 을 한 번에 가른다.
- **3행**(href 배열·클릭 해시·**Tab 포커스·Enter 이동**·`routes.ts` diff 0): 360행·369행(`user.tab()` 검색창 → 타일[0] → 타일[1], `{Enter}` → `#/persons/4`) + scope 2 — 충족. Enter 테스트가 형식적이지 않음은 V1-5 에서 이 테스트가 `'#/persons?id=4'` 로 실패한 것으로 증명.
- **5행**(조상 전부 + 자신 + 감싼 요소에 `mx-auto`·`max-w-*`·`md:w-*` 0 · `card-wrap` grep 1건·diff 0 · **V1-6 검출**): 189행 + d15-grep h·i·j + §3 V1-6 — 충족. E2E `boundingBox()` 는 U3 몫.
- **7행**(특수문자·앞뒤 공백·대소문자 픽스처 `textContent` 완전 일치·검색 중 이름 칸 자식 0·정규화 grep 이 비교 함수 안에만): 313행(`ODD_NAME = ' <b>Ab&C</b> "q" '`·`ODD_ALIAS = ' ΩX  yZ '`, 검색 `ab`·`ωx` 중에도 `check()` 3회) + 333행 소스 검사 + d15-grep e·f — 충족. 표시 경로(74~89행)에 정규화 호출 없음.

## 5. `tests.md`·`registry.md`·구현 증거

- `tests.md` U1 표 24행 ↔ `--reporter=verbose` 이름: 그리드 describe 19건(신규 12 · 변경 6 · 유지 1)과 사이드바 describe 변경 4건이 수집 이름과 1:1(verbose 목록은 `…-verifier-u1-vitest-all.txt`). 신규 12 = 열·별칭·이름 검색·별칭 검색·태그 글자·정규화·공백뿐·0건·결정 G·원칙7·소스 검사·키보드. 변경 6 = 4필드(P8 189행)·조상 검사(P8 454행)·컨트롤(P8 190행, 의미 반전)·빈 목록(P8 191행)·실패(P8 192행)·href(P8 193행). 유지 1 = 상세(P8 455행). 사이드바 4 = 동일 순서(P8 194행)·1회·알림·import(P8 201행). **삭제 0** — P8 `card.test.tsx` 31행 모두 후속 행이 있다(`git diff` 의 `-` 줄은 전부 재작성된 테스트 본문). 43 = 31 + 12.
- 표의 "변경(P8 … 재작성)" 표기는 P8 테스트 **이름 인용**이고 P8 `tests.md` **행 번호**는 없다(R-U1-4).
- `registry.md`: 신규 "인물 그리드" 행의 내용(컴포넌트·함수 이름·testid·열 클래스·"변이 12건 전부 검출")과 비고 4곳(`types.ts`·`PersonList.tsx`·`PersonCardScreen.tsx`·테스트)이 코드와 맞다. `PersonList.tsx` 행의 **본문 열**은 여전히 "`#/persons` 본문과 `AppShell` 사이드바 아래에 같은 컴포넌트" 라 비고와 어긋난다(R-U1-5). 해시 치환은 커밋 뒤 메인 세션 몫.
- 구현 증거: `…-u1-grid.txt`(typecheck exit 0) · `…-u1-grid-vitest.txt`(43 passed) · `…-u1-vitest-all.txt`(149 passed) · `…-u1-build.txt`(built) · `…-u1-grep2.txt` · `…-u1-mutation.txt`(CONTROL 43 passed, V1-1~V1-11(9a·9b) 12건 `검출(FAIL)` 12회, 끝의 `git status`). 내 재실행 수치와 같다. 구현자 변이 파일의 "생존" 1회는 CONTROL 블록의 라벨이지 변이 생존이 아니다.

## 6. 범위·원칙

- 원칙5: 라우트 3경로 그대로(`routes.ts` diff 0), 새 화면·패널 0, 서랍 파일 `AppShell.tsx` 1개 그대로(scope 2·3).
- 원칙7: 타일·검색이 서버 문자열을 가공하지 않는다 — 표시는 `{p.display_name}`·`{shown.join(' · ')}` 원문, 정규화는 15행 한 함수에서 비교에만(§4 7행). 하이라이트 없음(이름 칸 자식 0). 태그 필터 0·새 파라미터 0·`?q=` 0(scope 5, d15-grep a). "하지 않는 것" 35~46행 중 프론트 항목(필터 컨트롤·새 API·새 라우트·가공·상세 폭·Chat/Briefing·검색어 저장·`ui/input` 내려받기) 전부 지켜짐.
- U0 밖 백엔드·`alembic`·`package.json` diff 0(scope 1·8). 비밀 0(scope 9).
- U2 몫(`AppShell.tsx` 5명·전체 보기) 침범 0 — `AppShell.tsx` diff 0. 사이드바 테스트 수정은 "`person-list` 2개 기대 → 1개" 3건 + import 교체 1건으로 U1 해석 "최소 수정" 범위.

## 7. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U1-1 · 조회 실패 상태에서 검색창이 없다는 U1 해석(결정 D)을 테스트가 안 본다.** 근거: §3 X6 `43 passed` 생존. 코드(28~34행)는 `<p role="status">` 만 돌려주므로 규칙대로다. 353행 `목록 조회가 실패하면 한 줄 안내` 에 `expect(screen.queryByTestId('person-search')).toBeNull()` 한 줄이면 346행(빈 목록)과 대칭이 된다. 다음 프론트 단위(U2) 에서 같이 넣을지는 메인 세션 판단.
- **R-U1-2 · `aliases` 키가 없는 응답(U0 이전 서버)을 받으면 그리드가 렌더 중 크래시한다.** 근거: §3 X7 탐침 `TypeError: Cannot read properties of undefined (reading 'filter')`(`PersonGrid.tsx` 20행 `aliases.filter`, 42행 `...p.aliases` 도 같은 경로). 01-plan 76행이 "U0 응답과 1:1" 을 요구하고 `types.ts` 가 필수 필드이며 U0 백엔드는 이미 HEAD(`adc650e`)에 있으므로 **결함이 아니다**. 다만 CloudFront 프론트와 EC2 백엔드가 따로 배포되므로 P8b 를 `main` 으로 올릴 때 **백엔드(U0)가 먼저 떠 있어야** 한다 — 03-log/HANDOFF 배포 순서 한 줄. `?? []` 가드를 넣는 것은 계약을 느슨하게 하므로 권하지 않는다.
- **R-U1-3 · `Card size="sm"`(결정 D U1 해석)은 grep 으로만 보호된다.** 근거: §3 X10 생존, d15-grep n 72행. 시각 속성이라 U5 사람 점검이 보는 자리이고 Vitest 로 잡을 가치는 낮다 — 기록만.
- **R-U1-4 · `tests.md` 변경 행이 P8 `tests.md` 행 번호 없이 이름 인용으로 적혔다.** 대응은 §5 에서 내가 확인했다(189~194·201·454~455행). 위임 형식("변경/삭제(P8 tests.md n행)")에 맞출지는 메인 세션 판단(verifier 는 문서를 고치지 않는다).
- **R-U1-5 · `registry.md` `PersonList.tsx` 행의 본문 열("… 두 자리에 같은 컴포넌트")이 비고("사이드바 전용")와 어긋난다.** 커밋 뒤 해시 치환 때 본문 열도 "사이드바 전용(U2 가 5명으로 자름)" 으로 맞추는 것이 registry 의 "무엇이 있는가" 역할에 맞다. `PersonList.tsx` 1~2행 머리 주석도 같은 옛 문장이다(코드 동작과 무관, U2 에서 손볼 자리).

03-log 에 적을 것(메인 세션): ① `PERSON_LIST_NOTICE` 에 3키 추가 외 `PersonList.tsx` 본문 무수정 · ② 사이드바 테스트 최소 수정 4건의 내용(§6) · ③ 변이 V1-6 = P8 R-U10C-3 M4 검출(P8 04-review §6 의 열린 문제를 닫는 근거: `…-verifier-u1-mutation.txt` V1-6 블록) · ④ R-U1-2 배포 순서 · Refs `P8b-persons-grid D15 CR-003 결정L 원칙5 원칙7 R-U10C-3`.

## 8. 판정

**통과.** `PersonGrid` 가 01-plan 76행 계약(결정 A·B·C·D·G·H·I 와 B·D 의 U1 해석 6가지, testid 4종, R-6 (a))과 D15 코드 규칙 2·3·5·7번째 줄을 값으로 지키고(§1·§2), 내 재실행에서 typecheck exit 0 · Vitest 149 passed(9 files, 기준선 137 + 12, skip 0) · build 성공이다. 계획 변이 V1-1~V1-11 은 전부 검출됐고 특히 P8 에서 살아남은 M4(V1-6)를 조상 검사 테스트가 잡는다(§3). 생존한 2건(X6·X10)은 코드가 규칙대로임을 grep 으로 확인한 테스트 공백이라 [권고]다. 범위 밖 diff 0·새 의존성 0·비밀 0·저장소 무수정. 코드에 요구하는 변경은 없다. 커밋·승인은 메인 세션·사용자 몫이다.
