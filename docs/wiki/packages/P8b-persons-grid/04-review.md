# P8b-persons-grid · 완료 검토 (04-review)

날짜: 2026-10-28 | 검토자: verifier (fable) — 구현자(backend-agent·frontend-agent, sonnet)·메인 세션과 다른 모델·새 컨텍스트(L-002)

근거 문서(연 것만): `01-plan.md` 범위·"하지 않는 것"(35~46행)·수용 기준(113~117행)·판정 표 1~14행(130~154행)·결정 K·A~J 확정 칸(177~189행) · `docs/backlog.md` 89행 · `decisions/D15-persons-screen-layout.md` 결정 1~6·코드 규칙 7문장·갱신 이력 · `changes/CR-003.md` §1~§4 · `INDEX.md` 77행 · `02-plan-verify.md` 120~121행 · `03-log.md` 전문 · `tests.md` 전문 · 단위 리뷰 4편(`review-u0-read-persons-aliases.md`·`review-u1-grid-search.md`·`review-u2-sidebar.md`·`review-u3-e2e.md`) · `verification.md` · `registry.md` P8b 행(222·224·226·236·237·245~248·257행) · `packages/P8-frontend/04-review.md` §6(251~273행)·296~297행 · 코드 `app/api/read.py`·`schemas.py` diff, `web/src/components/PersonGrid.tsx`·`PersonList.tsx`·`AppShell.tsx`, `web/src/__tests__/card.test.tsx` 224~240행, `web/e2e/card.spec.ts` 12·21·77~79·151~153행, `tests/test_api_read_persons.py` 240~300행.

## 1. 기계 검증 출력 (그대로 붙인다)

### 1차 (04-review 작성 전) — `POSTGRES_PORT=5433 python3 .claude/scripts/save_evidence.py P8b-persons-grid verifier-04-verify-impl -- bash .claude/scripts/verify-impl.sh P8b-persons-grid` → `evidence/20261028-1124-verifier-04-verify-impl.txt`

```
# 명령: bash .claude/scripts/verify-impl.sh P8b-persons-grid
# 시각: 2026-10-28T11:24:51+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: fff6e8c (dev2)
# exit: 0
# ---
== verify-impl P8b-persons-grid  (20261028-1124) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1958 passed, 1 warning in 24.12s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261028-1124-pytest.txt
WARN  ruff 경고/오류 → evidence/20261028-1124-lint.txt
PASS  태그 P8b-persons-grid 커밋 7 건 → evidence/20261028-1124-commits.txt
PASS  커밋에 태그 존재: CR-003
PASS  커밋에 태그 존재: D15
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P8b-persons-grid 행 있음
WARN  미완료 작업 단위 6 개
== 결과: FAIL=0 WARN=3 → evidence/20261028-1124-summary.txt ==
```

WARN 3 의 성격: ① ruff — `evidence/20261028-1124-lint.txt` 의 경고는 전부 `.claude/scripts/`(`bash_write_check.py` B007 · `findings.py` DTZ005)로 하네스 파일이며 제품 코드(`app/`) 0 — P8 04-review R-U10R-8 와 같은 이관(§6 R-U5R-8). ② 04-review 부재 — 이 문서로 해소(2차에서 확인). ③ 미완료 작업 단위 6 — `01-plan.md` 75~111행 U0~U5 체크박스가 `- [ ]` 그대로(§6 R-U5R-7, 승인 뒤 메인 세션이 닫는 P8 선례).

FAIL 0 → `05-remediation.md` 신규 소견 없음(파일 없음, 열린 소견 0).

### 2차 (04-review 작성 직후) — `evidence/20261028-1303-verifier-04-verify-impl-2.txt` · **FAIL 14** → 표 형식 문제, 판정 무관

```
# 명령: bash .claude/scripts/verify-impl.sh P8b-persons-grid
# 시각: 2026-10-28T13:03:59+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: fff6e8c (dev2)
# exit: 1
# ---
== verify-impl P8b-persons-grid  (20261028-1303) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1958 passed, 1 warning in 25.10s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261028-1303-pytest.txt
WARN  ruff 경고/오류 → evidence/20261028-1303-lint.txt
PASS  태그 P8b-persons-grid 커밋 7 건 → evidence/20261028-1303-commits.txt
PASS  커밋에 태그 존재: CR-003
PASS  커밋에 태그 존재: D15
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  D15 "코드에서 지켜야 할 것" 전부  ← 판정 1~7행(아래 2.2) · evidence/20261028-1125
PASS  증거 확인:  백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(결 ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  `card.test.tsx`·`routes.test.tsx`·E2E `card.spec. ← 529922f(card.test U2 7건 — verbose 이름 "7명
PASS  증거 확인:  목록 폭 단언 보강(R-U10C-3, 조상 전부 + `boundingBox()`)  ← 2112a2a(`card.test.tsx` 157·202행 조상·자신·s
PASS  증거 확인:  typecheck·Vitest·build·E2E 통과  ← evidence/20261028-1125-verifier-04-typec
PASS  증거 확인:  상세 가운데 75% 는 `3bd5025` 유지  ← evidence/20261028-1125-verifier-04-invar
FAIL  증거가 파일·커밋·경로가 아니다:  #  ← 무엇을
FAIL  증거가 파일·커밋·경로가 아니다:  1  ← D15 코드 규칙 1 — `getPersons()` 인자 없음, 쿼리 파
FAIL  증거가 파일·커밋·경로가 아니다:  2  ← D15 코드 규칙 2 — 필터 컨트롤 0, 검색 `<input>` 1, 
FAIL  증거가 파일·커밋·경로가 아니다:  3  ← D15 코드 규칙 3 — 타일 `href="#/persons/<id>"`
FAIL  증거가 파일·커밋·경로가 아니다:  4  ← D15 코드 규칙 4 — 사이드바 앞 5명 + `#/persons` 링크
FAIL  증거가 파일·커밋·경로가 아니다:  5  ← D15 코드 규칙 5 — 목록 모드 조상·자신에 `max-w-*`·`mx
FAIL  증거가 파일·커밋·경로가 아니다:  6  ← D15 코드 규칙 6 — `ChatScreen`·`BriefingScre
FAIL  증거가 파일·커밋·경로가 아니다:  7  ← D15 코드 규칙 7 — 서버 문자열 가공 0, 하이라이트 0
PASS  증거 확인:  8  ← 백엔드 변경은 `aliases` 뿐(R-U10R-10 기준 `3bd502
FAIL  증거가 파일·커밋·경로가 아니다:  9  ← typecheck · build
FAIL  증거가 파일·커밋·경로가 아니다:  10  ← Vitest 전체 = 기준선 137 + 신규 − 삭제
FAIL  증거가 파일·커밋·경로가 아니다:  11  ← E2E 전체
FAIL  증거가 파일·커밋·경로가 아니다:  12  ← 불변식 — 라우트 3·서랍 1파일·P8 불변식 1·2·4·7·9
FAIL  증거가 파일·커밋·경로가 아니다:  13  ← `tests.md` 행 수 = 테스트 수
FAIL  증거가 파일·커밋·경로가 아니다:  14  ← 사람 점검 ①~⑧(데스크톱·모바일, 밝음·어두움, 수정 반영 n ≤ 1)
PASS  registry 에 P8b-persons-grid 행 있음
WARN  미완료 작업 단위 6 개
== 결과: FAIL=14 WARN=2 → evidence/20261028-1303-summary.txt ==
```

원인: `verify-impl.sh` 102~106행은 2절의 모든 표 행에서 **둘째 열**을 증거로 읽는데, 2.2 표를 `| # | 무엇을 | 증거 | 결과 |` 4열로 써서 "무엇을" 열이 증거로 읽혔다(8행만 우연히 `3bd5025` 해시가 들어 PASS). 증거 자체의 실재와 무관한 형식 문제라 행 번호를 첫 열 머리로 옮겨(`| 1 · … | 증거 | 결과 |`) 3차를 돌렸다. 소견(`findings.sh`)은 만들지 않았다 — 코드·증거 결함이 아니라 이 문서의 표 형식이고 같은 세션에서 바로 고쳤다. 참고: 2.2 표 형식(4열)은 P8 04-review 와 같은 모양이라 다음 검토자도 같은 함정에 걸릴 수 있다(R-U5R-8 과 함께 하네스 메모).

### 3차 (표 수정 뒤) — `evidence/20261028-1305-verifier-04-verify-impl-3.txt` · **FAIL 0 / WARN 2**

```
# 명령: bash .claude/scripts/verify-impl.sh P8b-persons-grid
# 시각: 2026-10-28T13:05:15+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: fff6e8c (dev2)
# exit: 0
# ---
== verify-impl P8b-persons-grid  (20261028-1305) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1958 passed, 1 warning in 25.25s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261028-1305-pytest.txt
WARN  ruff 경고/오류 → evidence/20261028-1305-lint.txt
PASS  태그 P8b-persons-grid 커밋 7 건 → evidence/20261028-1305-commits.txt
PASS  커밋에 태그 존재: CR-003
PASS  커밋에 태그 존재: D15
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  D15 "코드에서 지켜야 할 것" 전부  ← 판정 1~7행(아래 2.2) · evidence/20261028-1125
PASS  증거 확인:  백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(결 ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  `card.test.tsx`·`routes.test.tsx`·E2E `card.spec. ← 529922f(card.test U2 7건 — verbose 이름 "7명
PASS  증거 확인:  목록 폭 단언 보강(R-U10C-3, 조상 전부 + `boundingBox()`)  ← 2112a2a(`card.test.tsx` 157·202행 조상·자신·s
PASS  증거 확인:  typecheck·Vitest·build·E2E 통과  ← evidence/20261028-1125-verifier-04-typec
PASS  증거 확인:  상세 가운데 75% 는 `3bd5025` 유지  ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  1 · D15 코드 규칙 1 — `getPersons()` 인자 없음, 쿼리 파라미터 0 ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  2 · D15 코드 규칙 2 — 필터 컨트롤 0, 검색 `<input>` 1, 이름·별칭 ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  3 · D15 코드 규칙 3 — 타일 `href="#/persons/<id>"`, 라우트 ← evidence/20261028-1125-verifier-04-vites
PASS  증거 확인:  4 · D15 코드 규칙 4 — 사이드바 앞 5명 + `#/persons` 링크, 재정렬 ← `web/src/components/AppShell.tsx` 14행 `e
PASS  증거 확인:  5 · D15 코드 규칙 5 — 목록 모드 조상·자신에 `max-w-*`·`mx-auto ← evidence/20261028-1125-verifier-04-vites
PASS  증거 확인:  6 · D15 코드 규칙 6 — `ChatScreen`·`BriefingScreen` 무 ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  7 · D15 코드 규칙 7 — 서버 문자열 가공 0, 하이라이트 0  ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  8 · 백엔드 변경은 `aliases` 뿐(R-U10R-10 기준 `3bd5025`)  ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  9 · typecheck · build  ← evidence/20261028-1125-verifier-04-typec
PASS  증거 확인:  10 · Vitest 전체 = 기준선 137 + 신규 − 삭제  ← evidence/20261028-1125-verifier-04-vites
PASS  증거 확인:  11 · E2E 전체  ← evidence/20261028-1126-verifier-04-e2e.t
PASS  증거 확인:  12 · 불변식 — 라우트 3·서랍 1파일·P8 불변식 1·2·4·7·9  ← evidence/20261028-1125-verifier-04-invar
PASS  증거 확인:  13 · `tests.md` 행 수 = 테스트 수  ← evidence/20261028-1027-u4-tests-md-check
PASS  증거 확인:  14 · 사람 점검 ①~⑧(데스크톱·모바일, 밝음·어두움, 수정 반영 n ≤ 1)  ← evidence/20261028-1120-u5-check-screens.
PASS  registry 에 P8b-persons-grid 행 있음
WARN  미완료 작업 단위 6 개
== 결과: FAIL=0 WARN=2 → evidence/20261028-1305-summary.txt ==
```

WARN 2 = ruff(하네스, R-U5R-8) · 체크박스 6(R-U5R-7). "검토자 = verifier (L-002)" PASS, 수용 기준 6구절·판정 14행 증거 전부 실재 확인.

## 2. 수용 기준 대조

증거 열은 `evidence/` 파일·커밋 해시·존재하는 경로만. 수용 기준은 `docs/backlog.md` 89행과 `01-plan.md` 115행이 글자 그대로 같음을 내가 직접 대조했다(`sed -n 89p docs/backlog.md` 와 `sed -n 115p 01-plan.md` 의 "수용기준:" 뒤 구절 비교 → IDENTICAL, 2026-10-28 11:31). 기준선 `3bd5025`, HEAD `fff6e8c`, `git status --short app alembic web` 빈 출력(`evidence/20261028-1125-verifier-04-invariants.txt` "== git status product").

### 2.1 backlog 89행 구절

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| D15 "코드에서 지켜야 할 것" 전부 | 판정 1~7행(아래 2.2) · evidence/20261028-1125-verifier-04-invariants.txt · evidence/20261028-1125-verifier-04-vitest-all.txt · evidence/20261028-1126-verifier-04-e2e.txt | 통과 |
| 백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(결정 K (나), 읽기 전용, 스키마 v2 무변경 — `app/api/read.py`·`app/api/schemas.py`·`tests/test_api_read_persons.py` 밖 `app/`·`alembic/` diff 0) | evidence/20261028-1125-verifier-04-invariants.txt(r8a·r8b·r8c 세 diff 모두 빈 출력) · adc650e(`git diff 3bd5025..HEAD -- app/api/read.py app/api/schemas.py` = 별칭 질의 1회 + `aliases=sorted(...)` + `aliases: list[str]` + docstring 1줄뿐 — 내가 직접 읽음) · evidence/20261028-1125-verifier-04-pytest-all.txt(1958 passed, skip 0) · evidence/20261028-1130-verifier-04-live-api.txt(실서버 응답 키 6개 = 5필드 + `aliases`, 별칭 코드포인트 순 True) | 통과 |
| `card.test.tsx`·`routes.test.tsx`·E2E `card.spec.ts` 사이드바 단언 5명으로 갱신 | 529922f(card.test U2 7건 — verbose 이름 "7명이면 사이드바는 서버 순서의 앞 5명만…" evidence/20261028-1125-verifier-04-vitest-all.txt) · a0f4bc3(`web/e2e/card.spec.ts` 77~79행 `3 + SIDEBAR_COUNT + 1`·인물 링크 5·강다온 0, 151~153행 서랍 5 + `sidebar-see-all`) · evidence/20261028-1126-verifier-04-e2e.txt(4 passed) · evidence/20261028-1128-verifier-04-mutation-web.txt(MB·MF 검출) · `routes.test.tsx` 는 무수정 통과(조회 전 동기 단언 — 03-log 33행 사유, `review-u2-sidebar.md` 83행에서 verifier 가 타당 판정) | 통과 |
| 목록 폭 단언 보강(R-U10C-3, 조상 전부 + `boundingBox()`) | 2112a2a(`card.test.tsx` 157·202행 조상·자신·section 안 래퍼 검사) · a0f4bc3(`card.spec.ts` `abs(grid.width − (main.width − 48)) ≤ 2`, 실측 976/1024/0) · evidence/20261028-0822-verifier-u1-mutation.txt(V1-6 = P8 M4 검출) · evidence/20261028-0915-verifier-u3-mutation.txt(V3-1 차 208 FAIL) · evidence/20261028-1126-verifier-04-e2e.txt | 통과 |
| typecheck·Vitest·build·E2E 통과 | evidence/20261028-1125-verifier-04-typecheck.txt(exit 0) · evidence/20261028-1125-verifier-04-vitest-all.txt(156 passed, 9 files) · evidence/20261028-1125-verifier-04-build.txt(exit 0, `web/dist/index.html`·`sw.js`·`manifest.webmanifest` 존재) · evidence/20261028-1126-verifier-04-e2e.txt(4 passed) · CI run 40615729630(fff6e8c, 5 job success — `gh run list --branch dev2`, 2026-10-28 11:23 확인) | 통과 |
| 상세 가운데 75% 는 `3bd5025` 유지 | evidence/20261028-1125-verifier-04-invariants.txt(r5a `card-wrap` grep 339행 1건 · r5b `PersonCardScreen.tsx` diff 는 import 1줄·`<PersonGrid />` 1줄뿐, `card-wrap` 줄 변경 0) · evidence/20261028-1125-verifier-04-vitest-all.txt("상세 상태는 가운데 정렬이고 폭이 본문의 75%…" 통과) · evidence/20261028-1120-u5-check-screens.txt(⑤ 1054.5 = 1406×0.75) | 통과 — 단 `max-w-*` 부재는 테스트가 아니라 grep 으로만 보호(§3 MC 생존, §6 R-U5R-1) |

### 2.2 판정 표 1~14행 (01-plan 130~154행)

(`verify-impl.sh` 가 둘째 열을 증거로 읽으므로 행 번호는 첫 열 머리에 붙인다.)

| 기준 — 판정 행 번호 · 무엇을 | 증거(내가 실행·확인) | 결과 |
|------------------------------|---------------------|------|
| 1 · D15 코드 규칙 1 — `getPersons()` 인자 없음, 쿼리 파라미터 0, 백엔드는 `aliases` 뿐 | evidence/20261028-1125-verifier-04-invariants.txt(r1a `client.ts:107` 1건 · r1b count=0) · adc650e diff(위 2.1) · evidence/20261028-1128-verifier-04-mutation-backend.txt(대조군 17 passed, 값·순서 = 카드·원문 키 0·쓰기 0 테스트 포함) · evidence/20261028-1125-verifier-04-vitest-all.txt("#/persons 진입 시 GET /api/persons 1회…"·"데스크톱 열·간격 클래스(결정 A)… 7명 전원"·"타일 별칭(결정 B)") | PASS |
| 2 · D15 코드 규칙 2 — 필터 컨트롤 0, 검색 `<input>` 1, 이름·별칭 부분 일치만 | evidence/20261028-1125-verifier-04-invariants.txt(r2 count=0) · evidence/20261028-1125-verifier-04-vitest-all.txt("컨트롤은 검색창 1개뿐…"·"검색: 이름 일부…"·"검색: 별칭 일부만…"·"검색: 태그·위계 글자로는 찾지 않는다"·"검색 정규화(결정 C)…"·"빈 검색어…"·"0건이면 결정 D 문구…") · evidence/20261028-1128-verifier-04-mutation-web.txt(MA 별칭 제외 → 4 FAIL · ME `includes`→`startsWith` → 5 FAIL) | PASS |
| 3 · D15 코드 규칙 3 — 타일 `href="#/persons/<id>"`, 라우트 3경로 | evidence/20261028-1125-verifier-04-vitest-all.txt("타일 href 는 서버 순서의 #/persons/:id…"·"키보드: Tab…Enter…"·routes.test 전부) · evidence/20261028-1125-verifier-04-invariants.txt(r12a `routes.ts` diff 빈 출력) · `web/src/components/PersonGrid.tsx` 64행 `href={`${HREF.persons}/${p.id}`}` | PASS |
| 4 · D15 코드 규칙 4 — 사이드바 앞 5명 + `#/persons` 링크, 재정렬 0 | `web/src/components/AppShell.tsx` 14행 `export const SIDEBAR_RECENT_LIMIT = 5`·41행 `limit={SIDEBAR_RECENT_LIMIT}` · `PersonList.tsx` 34행 `persons.slice(0, limit)`, 56~63행 `href={HREF.persons}` `sidebar-see-all` · evidence/20261028-1125-verifier-04-vitest-all.txt(U2 7건) · evidence/20261028-1126-verifier-04-e2e.txt(데스크톱 9링크·모바일 5) · evidence/20261028-1128-verifier-04-mutation-web.txt(MB 전원 → 2 FAIL · MD 0명에도 링크 → 1 FAIL · MF 4명 → E2E 2 FAIL "Expected 9 Received 8"·"Expected 5 Received 4") · evidence/20261028-1130-verifier-04-live-api.txt(실서버 앞 5 = 12·11·9·10·8, 잘리는 6번째 = 7 — U5 ⑥ 기록과 일치) | PASS |
| 5 · D15 코드 규칙 5 — 목록 모드 조상·자신에 `max-w-*`·`mx-auto` 0, 상세 `card-wrap` `mx-auto w-full md:w-3/4` 이고 `max-w-*` 없음 | evidence/20261028-1125-verifier-04-vitest-all.txt("목록 상태는 본문 폭 전체를 쓴다 — 그리드부터 main 까지 모든 조상…") · evidence/20261028-1126-verifier-04-e2e.txt(폭 단언 포함 데스크톱 통과) · evidence/20261028-1125-verifier-04-invariants.txt(r5a 1건 · r5b `card-wrap` 줄 변경 0) · evidence/20261028-0822-verifier-u1-mutation.txt(V1-6·V1-7 검출) · evidence/20261028-1128-verifier-04-mutation-web.txt(**MC `card-wrap`+`max-w-3xl` → 64 passed 생존**) | PASS(코드) — 상세 `max-w-*` 부재는 Vitest 공백, grep 5a 가 잡음 → R-U5R-1 |
| 6 · D15 코드 규칙 6 — `ChatScreen`·`BriefingScreen` 무변경 | evidence/20261028-1125-verifier-04-invariants.txt(r6 빈 출력) | PASS |
| 7 · D15 코드 규칙 7 — 서버 문자열 가공 0, 하이라이트 0 | evidence/20261028-1125-verifier-04-invariants.txt(r7: `PersonGrid.tsx` 15행 한 줄 `s.trim().toLowerCase().replace(/\s+/g, '')` 만 — `normalizeForMatch` 비교 함수 안, `.sort(`·`toSorted` 0) · evidence/20261028-1125-verifier-04-vitest-all.txt("서버 문자열은 가공 없이 보인다 — 특수문자·앞뒤 공백·대소문자 textContent 일치, 검색 중에도 이름 칸 자식 요소 0"·"PersonGrid 소스: 가공은 비교 함수 한 곳에만…") | PASS |
| 8 · 백엔드 변경은 `aliases` 뿐(R-U10R-10 기준 `3bd5025`) | evidence/20261028-1125-verifier-04-invariants.txt(r8a `app alembic ':!read.py' ':!schemas.py'` 빈 · r8b `alembic` 빈 · r8c `tests ':!test_api_read_persons.py'` 빈 — 내가 재실행) | PASS |
| 9 · typecheck · build | evidence/20261028-1125-verifier-04-typecheck.txt(exit 0) · evidence/20261028-1125-verifier-04-build.txt(exit 0, dist 3파일 존재) | PASS |
| 10 · Vitest 전체 = 기준선 137 + 신규 − 삭제 | evidence/20261028-1125-verifier-04-vitest-all.txt(**156 passed, 9 files**) = 137 + 12(U1) + 7(U2) + 0(U3) − 0 | PASS |
| 11 · E2E 전체 | evidence/20261028-1126-verifier-04-e2e.txt(**4 passed** — briefing 1·chat 1·card 2, `expectNoStrayRequests` 포함) | PASS |
| 12 · 불변식 — 라우트 3·서랍 1파일·P8 불변식 1·2·4·7·9 | evidence/20261028-1125-verifier-04-invariants.txt(r12a 빈 · r12b `web/src/components/AppShell.tsx` 1파일 · push-dev 0 · 음성 API 0 · 외부 글꼴 0 · `raw_utterance` 6줄 = U4 `evidence/20261028-1026-u4-invariants-r12-p8inv4.txt` 와 동일 · `VITE_*KEY` 는 U4 `evidence/20261028-1026-u4-invariants-r12-p8inv7.txt` exit 1(0건) — 내 재실행은 자동 분류기가 비밀 탐색으로 거부해 U4 증거로 갈음) | PASS |
| 13 · `tests.md` 행 수 = 테스트 수 | evidence/20261028-1027-u4-tests-md-check.txt(계획 명령 0 · `.py::` 6 · 웹 표 34행 전부 verbose 이름에 대응) · 내가 `awk` 로 절별 행 수 재계산 2026-10-28 11:27: U0 6 · U1 23 · U2 8 · U3 3 · U5 5(집계 제외) → 34 = 신규 19 + 변경 13 + 유지 2 — 03-log 52행 산식과 일치. 계획 148행 명령은 형식 불일치라 U4 가 "절별 표 행 수" 로 보정(사후 계획 수정 — §6 R-U5R-6) | PASS |
| 14 · 사람 점검 ①~⑧(데스크톱·모바일, 밝음·어두움, 수정 반영 n ≤ 1) | evidence/20261028-1120-u5-check-screens.txt(8항 통과, "수정 반영 횟수: 0", 실서버 6명) · 객관 항목 대조 evidence/20261028-1130-verifier-04-live-api.txt(인물 6 = 12·11·9·10·8·7, 김윤서 `친구·동` `2026-10-28T10:00:00Z`, 민수 별칭 `박지훈 과장님` → ③ "지훈" 검색 근거, 앞 5 = ⑥ 기록) · 03-log 59~64행 | PASS(조건부) — 조작 주체가 사용자가 아니라 메인 세션, 모바일 390·어두운 모드는 Playwright 에뮬레이션, 스크린샷 미보존 → R-U5R-2 [권고]+사용자 확인 조건(P8 04-review §6 선례) |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

### 3.1 직접 실행한 부정 케이스

| 케이스 | 명령 | 증거 |
|--------|------|------|
| `GET /persons` 가 쿼리 파라미터를 붙이지 않는다 | `grep -rnE "persons\?\|[?&](q\|limit)=" web/src --exclude-dir=__tests__` → 0건 | evidence/20261028-1125-verifier-04-invariants.txt r1b |
| 인물 화면에 `<select>`·combobox·switch 가 없다 | `grep -rnE "<select\|role=\"(combobox\|switch)\"" web/src/components/PersonGrid.tsx` → 0건 | evidence/20261028-1125-verifier-04-invariants.txt r2 |
| 서랍 컴포넌트는 1파일뿐(원칙5) | `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v ui/` → `AppShell.tsx` 1파일 | evidence/20261028-1125-verifier-04-invariants.txt r12b |
| U0 밖 백엔드·마이그레이션·백엔드 테스트 무변경 | r8a·r8b·r8c 세 diff 빈 출력 | evidence/20261028-1125-verifier-04-invariants.txt |
| 제품 코드 미커밋 변경 0 | `git status --short app alembic web` 빈 출력 | evidence/20261028-1125-verifier-04-invariants.txt "== git status product" |
| 실서버 응답에 원문 키 없음·별칭 정렬 | `GET /persons` 키 = `aliases, display_name, hierarchy, id, last_contact_at, relation_tag`, 코드포인트 순 True | evidence/20261028-1130-verifier-04-live-api.txt |
| 표 밖 네트워크 요청 0 (E2E `expectNoStrayRequests`) | `npm --prefix web run e2e` 4 passed | evidence/20261028-1126-verifier-04-e2e.txt |

### 3.2 변이 시험 — 내가 새로 돌린 7건 (저장소 밖: 스크래치패드 `verifier-04/web` 사본 + pytest 런타임 플러그인 `mut_nplus1.py`; 끝에 `git status --short`·`git diff --stat -- web app alembic` 빈 출력으로 저장소 무수정 확인)

| 변이 | 단위·규칙 | 기대 | 결과 | 증거 |
|------|----------|------|------|------|
| C0/E0/P0 대조군 | — | 통과 | Vitest 64 passed(card+routes) · E2E 4 passed · pytest 17 passed | evidence/20261028-1128-verifier-04-mutation-web.txt · evidence/20261028-1128-verifier-04-mutation-backend.txt |
| MA `PersonGrid` 검색 대상에서 별칭 제외 | U1 · D15 결정 2 | 별칭 검색 테스트 FAIL | **4 FAIL**(별칭 일부·태그 제외·정규화·무가공) — 검출 | …-mutation-web.txt |
| ME `includes` → `startsWith`(부분 일치 → 접두 일치) | U1 · D15 결정 2 "부분 일치" | 이름 일부 테스트 FAIL | **5 FAIL** — 검출 | …-mutation-web.txt |
| MB `PersonList` `slice(0, limit)` 제거(전원) | U2 · D15 결정 4 | 사이드바 5명 테스트 FAIL | **2 FAIL**(앞 5명·그리드 전원) — 검출 | …-mutation-web.txt |
| MD 인물 0명에도 "전체 보기" 링크 | U2 · 결정 F (a) | 0명 테스트 FAIL | **1 FAIL** — 검출 | …-mutation-web.txt |
| MC 상세 `card-wrap` 에 `max-w-3xl` 추가 | D15 결정 5 "상세 … `max-w-*` 가 없다" | 상세 폭 테스트 FAIL | **64 passed — 생존**(테스트 224~233행은 세 클래스의 존재만 봄) → 판정 5a grep·5b diff 가 잡는 층 | …-mutation-web.txt → R-U5R-1 |
| MF `SIDEBAR_RECENT_LIMIT` 5 → 4 (E2E, 사본 build+preview) | U3 · D15 결정 4 | 데스크톱 9링크·모바일 5 FAIL | **2 FAIL**("Expected 9 Received 8"·"Expected 5 Received 4") — 검출 | …-mutation-web.txt |
| MG `routes.list_persons` 를 N+1(인물마다 별칭 SELECT 1회 추가, 응답 동일)로 런타임 치환 | U0 · 01-plan 75행 N+1 금지 | SELECT 수 테스트 FAIL | **`assert 5 == 12` FAIL** — 검출 | …-mutation-backend.txt |

단위 리뷰에서 인용(이미 evidence 에 있음): U0 M1·M2·M4~M7 검출, **M3 생존**(`user_id` 조건 제거 — 출력 동등·질의 비동등, `evidence/20261027-1537-verifier-u0-mutation.txt`) · U1 22건 중 20 검출(V1-6 = P8 M4 검출), 생존 X6(U2 에서 검출됨)·X10(`Card size`), 탐침 X7 `aliases` 부재 크래시(`evidence/20261028-0822-verifier-u1-mutation.txt`) · U2 18건 중 17 검출, 생존 XF(`limit` 미지정 — 호출자 없음, `evidence/20261028-0850-verifier-u2-mutation.txt`) · U3 12건 중 11 검출, 생존 XC2(E2E 정규화 — Vitest 가 덮음, `evidence/20261028-0915-verifier-u3-mutation.txt`).

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)

- 이 패키지가 닫는 R 은 없다(`INDEX.md` 77행 "닫는 R —", 01-plan 4행). `git diff --stat fe76931..HEAD -- docs/wiki/review-index.md` 빈 출력, `git status --short docs/wiki/review-index.md` 빈 출력 — 바꾸지 않았음을 확인(2026-10-28 11:29).
- 이어받은 소견: **R-U10C-3**(P8 M4 생존) → V1-6(Vitest 조상 검사)·V3-1(E2E `boundingBox`) 두 층에서 검출 — 닫힘(`evidence/20261028-0822-verifier-u1-mutation.txt`·`20261028-0915-verifier-u3-mutation.txt`). **R-U10R-10** → 기준 해시 `3bd5025` 로 8행 diff 빈 출력 — 닫힘. **R-U10R-2**(밝은 모드) → U5 ⑧ 세 화면 OS 밝은 모드 확인 — 닫힘(메인 세션 조작, R-U5R-2 조건 안). **R-U10R-3**(모바일 390) → 이번에도 Playwright 에뮬레이션 — 같은 한계로 기록(R-U5R-2).

## 5. registry.md 에 올린 산출물

`grep -n "P8b" docs/wiki/registry.md` → 222·224·226·236·237·245·246·247·248·257행(10행). 전부 확인:
- 경로 실재: `app/api/read.py` · `app/api/schemas.py` · `tests/test_api_read_persons.py` · `web/src/components/AppShell.tsx` · `web/src/api/types.ts` · `web/src/components/PersonList.tsx` · `web/src/screens/PersonCardScreen.tsx` · `web/src/components/PersonGrid.tsx`(신규 행 247, 해시 `2112a2a`) · `web/src/__tests__/card.test.tsx` · `web/e2e/card.spec.ts` — 11경로 전부 존재(2026-10-28 11:29 확인).
- 해시 실재: `adc650e`·`2112a2a`·`529922f`·`a0f4bc3` 전부 `git cat-file -t` = commit. `grep -c "해시 pending" registry.md` = **0**(R-U2-4·R-U3-3 닫힘). 226행의 "U9b(pending)" 은 P8 시절 표기로 이 패키지 밖.
- 행 내용 대조: 222행(별칭 질의 1회·`sorted()`·SELECT 2) = `read.py` diff · 245행 본문 열 `PersonList({onNavigate?, limit?})`·6키(R-U2-3 닫힘) = `PersonList.tsx` 9~17·20행 · 247행 testid·열 클래스·`normalizeForMatch`·`ALIAS_LIMIT=2` = `PersonGrid.tsx` 11~15·59·64~68행 · 257행 976/1024/차 0·x 24 = 내 E2E 와 U3 증거 동일.
- `docs/wiki/packages/P8b-persons-grid/tests.md` 존재(U0 6·U1 23·U2 8·U3 3·U5 5·집계 절).

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

`05-remediation.md` 없음(열린 소견 0). verify-impl FAIL 0 → 새 소견 없음. 코드 결함은 찾지 못했다. **[필수] 0 · [권고] 11.**

**사람 점검(14행)을 메인 세션이 대신한 것과 Playwright 에뮬레이션을 [필수] 로 보지 않는 근거** — P8 04-review §6 "미확인 2건을 [필수] 로 보지 않는 근거" 1~4 와 같은 구조다. ① 수용 기준 6구절의 증거는 전부 자동 테스트·diff·grep·실서버 API 로 있다(§2). 14행은 같은 동작을 사람 눈으로 다시 보는 층이지 증거가 없는 기준이 아니다. ② 조작 주체 대체는 사용자 결정("제가 Chrome 직접 조작", 2026-10-28, 증거 머리글·03-log 59~61행에 숨김 없이 기록)이고, 메인 세션이 적은 객관 항목(인물 6명·id·앞 5명·별칭·`aliases` 키)은 내가 실서버 API 로 대조해 어긋남 0 이다(`evidence/20261028-1130-verifier-04-live-api.txt`). ③ 모바일 390·어두운 모드 에뮬레이션은 P8 R-U10R-3 와 같은 한계이고 E2E 390px 가 1열·서랍을 자동으로 덮는다. ④ 그래서 [권고] + 사용자 확인 조건으로 두고, `승인:` 줄에 사용자가 "확인" 또는 "면제" 를 적으면 된다(P8 승인 줄 선례).

**[권고] (사용자 확인 조건 1 · 테스트 공백 3 · 문서·하네스 4 · 인계 3)**
- **R-U5R-1 · [테스트 공백, FIX 후보] 상세 `card-wrap` 의 `max-w-*` 부재를 Vitest 가 안 본다.** 근거: §3.2 MC `card-wrap` 에 `max-w-3xl` 추가 → 64 passed 생존(`evidence/20261028-1128-verifier-04-mutation-web.txt`). `card.test.tsx` 224~233행은 `mx-auto`·`w-full`·`md:w-3/4` 의 존재만 단언한다. D15 코드 규칙 5 후반 "상세 모드는 `card-wrap` 가 `mx-auto w-full md:w-3/4` 이고 **`max-w-*` 가 없다**" 의 뒷부분은 판정 5a grep(정확 문자열)·5b diff 로만 보호된다. 코드는 규칙대로이므로 결함 아님. 잡으려면 233행에 `expect(hasWidthClass(wrap) /* max-w- */).toBe(false)` 류 1줄 — 다음 `card.test.tsx` 수정 때 또는 FIX.
- **R-U5R-2 · [사용자 확인 조건] 판정 14행의 "사용자 한 줄 의견" 은 메인 세션 문장이고, 모바일 390·어두운 모드는 Playwright 에뮬레이션이며, 스크린샷 9장은 세션 임시 폴더라 evidence 에 없다.** 근거: `evidence/20261028-1120-u5-check-screens.txt` 머리글 2~4줄·끝 "증거 파일" 줄. 객관 항목은 내가 실서버로 대조해 일치(위 근거 ②). 조건(사용자, 1~2분): 넓은 창에서 `#/persons` 그리드·검색·사이드바 5명·"전체 보기 →"·타일 → 상세 가운데 75% 를 한 번 보고 `승인:` 줄에 "확인" 한 줄, 또는 P8 선례대로 "면제". 어두운 모드 실확인은 U10 때 이미 됐고(P8 32행 dark) 이번엔 밝은 모드가 실확인됐으므로 두 모드 모두 한 번씩은 실브라우저로 본 셈이다.
- **R-U5R-3 · [열림, R-U3-1 이월] E2E 픽스처 별칭 순서 `['팀장님', '김 부장']` 이 U0 `sorted()` 규칙(`['김 부장', '팀장님']`)과 다르다.** 근거: HEAD `web/e2e/card.spec.ts` 12·21행(내가 grep, 2026-10-28 11:29). U4(`fff6e8c`)는 spec 을 만지지 않아 교정되지 않았다. 단언 영향 0. 다음에 `card.spec.ts` 를 만질 때 두 줄 교정 — FIX 후보(제품 코드 아님, test 커밋).
- **R-U5R-4 · [열림, R-U0-1 이월, FIX 후보] 별칭 질의의 `user_id` 조건 제거(M3)가 테스트에서 생존한다 — 출력 동등·질의 비동등.** 근거: `evidence/20261027-1537-verifier-u0-mutation.txt` M3 17 passed, `tests.md` U0 4행. 단일 사용자 전제에서 동작 영향 0. `cursor.rowcount` 단언 1건(타 사용자 별칭 다수 → 별칭 SELECT 행 수 == 내 별칭 수)을 다음 백엔드 단위나 FIX 에서.
- **R-U5R-5 · [문서, R-U1-4 이월] `tests.md` 변경 행이 P8 `tests.md` 행 번호 없이 이름 인용으로 적혀 있고, 03-log·tests.md 에 R-U1-4 처리 결정이 없다.** 근거: `grep -c "R-U1-4"` 03-log 0·tests.md 0. 대응 관계는 `review-u1-grid-search.md` §5 가 확인했으므로 정보 손실은 없다 — 메인 세션이 "이름 인용으로 갈음" 을 03-log 한 줄로 기록하거나 행 번호를 더한다.
- **R-U5R-6 · [기록, L 후보] 승인(2026-10-27) 뒤 `01-plan.md` 가 세 커밋에서 고쳐졌다 — `adc650e`(75행 행 번호 177→188, R-U0-3) · `2112a2a`(결정 B·D 비고 "U1 해석 사용자 수용") · `fff6e8c`(148행 13행 명령 보정).** 근거: `git log --oneline -- 01-plan.md`. 세 건 모두 수용 기준(115행, backlog 89행과 IDENTICAL 재확인)과 판정 결과를 바꾸지 않았고 고친 사실이 본문에 적혀 있다. 다만 U1 해석 6가지(`+n` 표기·n 계산·빈/실패 상태 검색창 없음·사이드바 테스트 4건·`Card size="sm"`·토큰 클래스)는 FIX-033 (b) "구현 전 멈추고 보고" 가 아니라 **사후 보고 → 사용자 수용**이었다(03-log 26행이 스스로 적음). 결과는 사용자가 수용했으므로 열린 문제는 아니지만, 다음 패키지 위임문에서 (b) 를 다시 강조하는 L 한 줄(메모리 `preconfirm-plan-gaps-before-delegation` 과 같은 취지)이 맞다 — 메인 세션 판단.
- **R-U5R-7 · [하네스 후속] `01-plan.md` 75~111행 U0~U5 체크박스 6개가 `- [ ]` 그대로(verify-impl WARN "미완료 작업 단위 6 개").** P8 R-U10R-7 선례대로 승인 뒤 메인 세션이 `- [x]` 로 닫고, 같은 커밋에서 D15 갱신 이력 완료 해시(D15 31행 "완료 해시는 그때 적는다")·backlog 89행 체크·`CURRENT.md none`·03-log U5 항목 해시 `pending` 치환.
- **R-U5R-8 · [하네스] ruff WARN 은 전부 `.claude/scripts/`(`bash_write_check.py` B007 · `findings.py` DTZ005), 제품 코드 0.** P8 R-U10R-8 와 같은 이관(FIX 후보).
- **R-U5R-9 · [인계 P10, 범위 밖] 발화 "오늘 학원에서 윤서랑 처음 인사했어" 가 인물·사건·질문 0 으로 끝났다(trace loop_turn 461~464).** 근거: U5 증거 ⓪. 같은 뜻의 "김윤서랑 같이 저녁 먹었어" 는 추출됐다. P8b(화면) 결함이 아니라 P5 추출 품질 — P10 평가 표본("이름 한 글자 줄임 + 호칭 없음" 케이스)으로 인계. P8 R-U10R-4(호칭 단독 자동 병합)와 같은 묶음.
- **R-U5R-10 · [인계 P9, R-U1-2 이월] CloudFront 프론트와 EC2 백엔드가 따로 배포되므로 P8b 를 올릴 때 백엔드(U0 `aliases`)가 먼저 떠 있어야 한다** — `aliases` 없는 응답이면 `PersonGrid.tsx` 20행 `aliases.filter` 가 TypeError(U1 탐침 X7, U5 에서 옛 :8000 프로세스로 실제 재현돼 재시작함 — 03-log 60행). HANDOFF 8행에 이미 메모돼 있다. P9 배포 순서·스모크 S1~S15 의 `GET /persons` 응답 모양에 반영.
- **R-U5R-11 · [L 후보, 03-log 30행 이월] 프론트 단위 커밋 전에 `npm --prefix web run e2e` 도 돌린다.** 근거: U1 `2112a2a`·U2 `529922f` CI run 40602788831·40606057880 failure(E2E 픽스처 `aliases` 부재), U3 `a0f4bc3` 부터 success(40609192773·40615729630). 계획상 예정된 빨강이었지만 CI 가 E2E 를 돌리는 이상 단위 판정에 E2E 를 넣는 편이 맞다 — L-nnn 등록은 메인 세션.

**단위 리뷰 [권고] 15건 처리 상태**

| 소견 | 내용 | 상태 | 근거 |
|------|------|------|------|
| R-U0-1 | 별칭 질의 `user_id` 조건 변이 생존 | 열림 → R-U5R-4(FIX 후보) | tests.md U0 4행 |
| R-U0-2 | 03-log U0 기록 항목 ①~④ | 닫힘 | 03-log 14~18행에 네 항목 전부 |
| R-U0-3 | 01-plan 75행 행 번호 177→188 | 닫힘 | 01-plan 75행 "(U0 뒤 188행)" |
| R-U1-1 | 실패 상태 검색창 null 단언 | 닫힘 | U2 X6 검출(`evidence/20261028-0850-verifier-u2-mutation.txt`), card.test 371행 |
| R-U1-2 | `aliases` 부재 크래시 — 배포 순서 | 기록 → R-U5R-10(P9 인계) | HANDOFF 8행 |
| R-U1-3 | `Card size="sm"` grep 만 보호 | 닫힘(사람 점검) | U5 ⑦ 디자인 언어 통과 |
| R-U1-4 | tests.md P8 행 번호 표기 | 열림 → R-U5R-5(문서) | 03-log·tests.md 에 R-U1-4 0건 |
| R-U1-5 | `PersonList` 머리 주석·registry 본문 열 | 닫힘 | `PersonList.tsx` 1~2행, registry 245행 |
| R-U2-1 | `limit` 미지정 기본 경로 호출자 없음 | 닫힘(기록) | registry 245행 "(제품 호출자 없음 — R-U2-1)" |
| R-U2-2 | nav 링크 3+5+1 단언은 E2E 몫 | 닫힘 | `card.spec.ts` 77행, 내 E2E 통과·MF 검출 |
| R-U2-3 | registry 245행 본문 열 시그니처·6키 | 닫힘 | registry 245행 `PersonList({onNavigate?, limit?})`·6키 |
| R-U2-4 | registry "해시 pending" 6곳 | 닫힘 | `grep -c "해시 pending"` = 0 |
| R-U3-1 | 픽스처 별칭 순서 | 열림 → R-U5R-3 | `card.spec.ts` 12·21행 |
| R-U3-2 | E2E 는 정규화를 안 봄(의도) | 닫힘(기록) | 03-log 45행 |
| R-U3-3 | registry 257행 해시 치환 | 닫힘 | registry 257행 `a0f4bc3` |

**위임문의 관찰 ①~⑦ 판정**: ① 추출 0 → R-U5R-9(P10 인계) · ② → R-U5R-4(FIX 후보) · ③ → R-U5R-10(P9 인계) · ④ → R-U5R-3(열림, test 커밋 FIX 후보) · ⑤ → 닫힘(기록) · ⑥ → R-U5R-6(L 후보) · ⑦ → 판정 13행 PASS, 보정 사실은 R-U5R-6 에 포함.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

**P9-infra**
- **배포 순서**: 백엔드(EC2, U0 `adc650e` 포함)를 먼저, CloudFront 프론트(U1 이후)를 뒤에. 반대 순서면 `#/persons` 가 렌더 중 크래시(R-U5R-10). 스모크 S1~S15 의 `GET /persons` 대조 값에 `aliases: list[str]`(코드포인트 순) 1필드 추가 — 실서버 응답 모양은 `evidence/20261028-1130-verifier-04-live-api.txt`.
- 운영 경로 데모 5단계에 그리드·검색을 넣는다: 사이드바 "전체 보기 →" → `#/persons` 그리드(데스크톱 3열/2열, 모바일 1열) → 검색("선영"·별칭 "지훈") → 타일 → 상세 가운데 75%. 인물이 6명 이상이어야 사이드바 5명 자르기가 보인다(개발 DB `local` 은 지금 6명: 7·8·9·10·11·12).
- 빌드 산출물 경로·명령 무변경(`npm --prefix web run build` → `web/dist/`).

**P10-final-eval**
- 평가 표본: "오늘 학원에서 윤서랑 처음 인사했어" → 추출 0(trace 461~464) vs "김윤서랑 같이 저녁 먹었어" → identity 질문 18 → new_person 질문 19 → 인물 12(R-U5R-9). P8 R-U10R-4(호칭 단독 자동 병합)와 같은 묶음.

**FIX 후보(제품 코드 아님, 테스트·문서)**
- R-U5R-1 `card.test.tsx` 상세 `max-w-*` 부재 단언 1줄 · R-U5R-3 `card.spec.ts` 12·21행 별칭 순서 · R-U5R-4 `test_api_read_persons.py` `rowcount` 단언 1건 · R-U5R-8 하네스 ruff.

**설정값·주의(공통)**
- `SIDEBAR_RECENT_LIMIT = 5`(`web/src/components/AppShell.tsx` 14행, export) · `ALIAS_LIMIT = 2`(`PersonGrid.tsx` 11행) · 결정 J 허용치 2px·상수 48 은 `main` 의 `p-6` 에 묶여 있다(패딩을 바꾸면 `card.spec.ts` 90~94행도 함께 — `review-u3-e2e.md` R-U3-2 관찰).
- 개발 DB `relationship` 의 U5 확인 행은 남긴다(원칙8): 인물 12 김윤서·사건 33·질문 18·19·trace 461~. 테스트는 `relationship_test`.
- 검색어는 `PersonGrid` 컴포넌트 상태뿐(결정 G) — 상세에서 돌아오면 비워진다. 인물이 수백 명이 되면 서버 검색은 별도 결정(D15 이유).

결과: 완료 — [필수] 0 · [권고] 11(사용자 확인 조건 1: R-U5R-2 사람 점검 대체·에뮬레이션). 근거: 기계 검증 1차 FAIL 0/WARN 3(하네스 ruff·04-review 부재·체크박스) · 2차 FAIL 14 는 이 문서 2.2 표의 열 순서 문제라 표를 고쳐 3차 FAIL 0/WARN 2(§1), 내가 직접 재실행한 백엔드 1958 passed skip 0 · typecheck 0 · Vitest 156(9 files) · build 0 · E2E 4 · 판정 8·12행 diff/grep 전부 기대값 · CI fff6e8c success · backlog 89행 6구절과 판정 표 1~13행 전부 증거로 통과 · 14행은 객관 항목을 실서버 API 로 대조해 일치 · 새 변이 7건 중 6건 검출(생존 1건 MC 는 grep 층이 잡는 테스트 공백 → [권고]) · 범위 밖 diff 0·저장소 무수정 · 03-log Refs 6커밋 전부 커밋 메시지에 있음 · registry 10행 경로·해시 실재, pending 0 · review-index 무변경. 승인 전 사용자가 R-U5R-2 를 1~2분에 확인하거나 면제를 `승인:` 줄에 적으면 된다. P9 는 이 문서 뒤 시작 가능(배포 순서 R-U5R-10 유의).
승인: 사용자 (2026-10-28) — AskUserQuestion "승인 — R-U5R-2 면제": 사람 점검을 메인 세션이 대신한 것·모바일 390/어두운 모드 Playwright 에뮬레이션·스크린샷 미보존을 면제한다(갈음: U5 객관 항목의 실서버 API 대조 일치, E2E 390 데스크톱/모바일 4편, U10 과 같은 처리). 메인 세션 재확인: verify-impl FAIL 0/WARN 2(체크박스는 승인 뒤 닫음) · Vitest 156 · `git status --short app alembic web` 0. R-U5R-7 처리: 01-plan 체크박스 6개 `[x]` · D15 갱신 이력 · backlog `[x]` · CURRENT none · journal DONE.
