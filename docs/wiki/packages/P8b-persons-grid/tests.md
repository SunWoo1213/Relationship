# P8b-persons-grid — 테스트 기록

테스트 1건 = 표 1줄. 증거: `evidence/20261027-1436-u0-read-persons-aliases.txt`(파일 17 passed), `evidence/20261027-1436-u0-pytest-all.txt`(전체 1958 passed, skip 0), 변이 `evidence/20261027-1437-u0-mutation.txt`.

## tests/test_api_read_persons.py — U0 `GET /persons` 별칭 (신규 5건 + 변경 1건)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v` → 17 passed.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_api_read_persons.py::test_목록_별칭은_카드_별칭과_같은_값_같은_순서 | 목록 `aliases` 가 카드와 같은 값·순서(코드포인트 순) | 별칭 입력 순 `Zed,가나,apple,Bob` → `["Bob","Zed","apple","가나"]`, 다른 인물 `["Cat","bat","민수형"]`, 두 인물 모두 카드 응답 `aliases` 와 동일 | 통과 · U0-M2(`sorted()` 제거 → `['Zed','가나','apple','Bob']` 로 실패) | 기록 없음 |
| test_api_read_persons.py::test_목록_별칭_없는_인물은_빈_배열 | 별칭 없는 인물 | 별칭 없는 인물 → `[]`, 별칭 1개 인물 → `["비"]` | 통과 · — | 기록 없음 |
| test_api_read_persons.py::test_목록_SELECT_수는_인물_수와_무관한_상수 | N+1 금지 | 인물 3명(별칭 각 2)·10명 각각 `GET /persons` 의 SELECT 수 == 2 (목록 1 + 별칭 1) | 통과 · U0-M1(인물마다 별칭 조회 → 5 != 12 로 실패) | 기록 없음 |
| test_api_read_persons.py::test_목록_별칭에_다른_사용자_별칭이_섞이지_않는다 | 응답에 타 사용자 별칭 없음 | 내 인물(`내별칭`)·타 사용자 인물(`남별칭`) → 응답 `[(내id, ["내별칭"])]`, 본문에 `남별칭` 없음 | 통과 · 질의의 `user_id` 조건 제거(U0-M3)는 **검출 못 함** — 응답이 내 인물 id 로만 조회돼 결과 불변(동등 변이, 질의 범위만 넓어짐) | 기록 없음 |
| test_api_read_persons.py::test_목록_응답에_원문_키가_없다 | 원문 비노출 | 이벤트 raw `절대노출금지`·별칭 있는 인물 → 행 키에 `raw_utterance`·`content` 없음, 본문에 원문 없음 | 통과 · — | 기록 없음 |
| test_api_read_persons.py::test_목록_정렬_최근순_null_뒤_동률은_id순 (변경) | 기대 키 집합 | 137행 집합에 `"aliases"` 추가(응답 필드 추가에 따른 갱신, 그 외 무수정) | 통과 · — | 기록 없음 |

쓰기 0: 기존 `test_쓰기_0_trace_0` 가 `GET /persons` 를 호출하고 `assert_no_writes` 를 건다(무수정, 통과).

## web/src/__tests__/card.test.tsx — U1 인물 화면 카드 그리드 (신규 12 · 변경 6 · 사이드바 최소 수정 4 · 삭제 0)

실행: `npm --prefix web test -- --run src/__tests__/card.test.tsx` → 43 passed (기준선 31 → +12). 전체 `npm --prefix web test -- --run` → 149 passed (9 files, 기준선 137 → +12). 증거 `evidence/20261027-1623-u1-grid-vitest.txt`·`…-u1-vitest-all.txt`·`…-u1-grid.txt`(typecheck)·`…-u1-build.txt`·`…-u1-grep2.txt`, 변이 `evidence/20261027-1623-u1-mutation.txt`(대조군 43 passed + 변이 12건 전부 FAIL, 저장소 무수정 `git status`). describe: "인물 목록 — 카드 그리드 (D15, P8b U1)". 실패 이력은 전부 "기록 없음".

| 테스트 이름(요지) | 구분 | 무엇을 확인하나 · 검출 변이 |
|---|---|---|
| #/persons 진입 시 GET /api/persons 1회, 타일 필드가 서버 값·순서 그대로 | 변경(P8 "서버 순서 그대로… 4개 필드" 재작성) | `<App />` 에서 fetch URL 목록 == `['/api/persons']`, 이름·태그·위계·마지막 접촉 값·`['7','4','9']` · V1-5(간접) |
| 데스크톱 열·간격 클래스(결정 A), 7명 전원 | 신규 | `grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4` 클래스 · 7명 전원(5명 자르기와 무관) |
| 타일 별칭(결정 B) | 신규 | 같은 별칭 제외·최대 2개·"+n"·0개면 칸 없음·정확히 2개면 "+n" 없음 · V1-9a, V1-9b |
| 목록 상태는 본문 폭 전체 — 조상 검사 (R-U10C-3) | 변경(P8 "본문 폭 전체… 폭 상한이 없다" 재작성: section 한 요소 → 그리드부터 main 까지 모든 조상+자신+section 안 감싼 요소) | `mx-auto`·`max-w-*`·`md:w-*` 0 · V1-6, V1-7 |
| 컨트롤은 검색창 1개뿐 — 결정 D 문구·aria-label | 변경(P8 "필터·검색 컨트롤이 없다" 의미 반전) | searchbox 1, combobox·listbox·radio·checkbox·switch 0, type=search · V1-10 |
| 검색: 이름 일부 → 그 타일만, 서버 순서 유지 | 신규 | `선영` → `['30','25']`(이름순이면 뒤바뀜) · V1-1, V1-4 |
| 검색: 별칭 일부 | 신규 | `엄마친` → `['12']` · V1-2 |
| 검색: 태그·위계 글자로는 안 찾음 | 신규 | `직장` → 0건(태그만 일치), `친구` → 별칭 일치 인물만 · V1-1, V1-2 |
| 검색 정규화(결정 C) | 신규 | 앞뒤 공백·안쪽 공백(양쪽)·영문 대소문자(양쪽) 6가지 · V1-3 (V1-4 도 FAIL) |
| 빈·공백뿐 검색어는 전원, 지우면 복귀 | 신규 | `'   '` → 4명, 지우면 4명 · V1-1, V1-3 |
| 0건이면 결정 D 문구 1줄, 그리드 사라짐 | 신규 | `person-grid-empty` 1개, 텍스트 `찾는 인물이 없어요.` · V1-8 |
| 검색어는 컴포넌트 상태뿐 (결정 G) | 신규 | 해시 불변·localStorage 0 |
| 서버 문자열 무가공 (원칙7) | 신규 | 특수문자·앞뒤 공백·대소문자 이름/별칭 `textContent` 완전 일치, 검색 중에도 이름 칸 자식 0 · V1-1~V1-3 |
| PersonGrid 소스: 가공 함수는 한 곳 | 신규 | toUpperCase 0·toLowerCase 1·trim 1·replace( 1·`.sort(` 0, 비교 함수 안 포함 · V1-3, V1-4 |
| 빈 목록 → 빈 상태 문구(검색창 없음) | 변경(P8 "빈 목록이면 빈 상태 문구 하나" 의 대상이 그리드로) | `PERSON_LIST_NOTICE.empty`, `person-grid`·`person-search` 없음 |
| 목록 조회 실패 → 한 줄 안내 | 변경(+그리드 없음 단언) | `PERSON_LIST_NOTICE.failed` |
| 타일 href·클릭 해시 | 변경(P8 "항목 링크는 #/persons/:id" 의 대상이 타일로) | href 배열 `['#/persons/7','#/persons/4','#/persons/9']`, 전부 `<a>`, 클릭 → `#/persons/4` · V1-5 |
| 키보드: Tab → 검색창 → 첫 타일, Enter 이동 | 신규 | 포커스 순서·Enter 해시 · V1-5, V1-10(검색창 뒤 select 로 순서 깨짐) |
| 상세 상태 가운데·75% (무수정) | 유지 | `card-wrap` `mx-auto w-full md:w-3/4` · V1-11 |
| 사이드바: #/persons 에서 사이드바 목록 + 본문 그리드가 같은 순서 | 변경(최소: 본문이 그리드가 되어 `person-list` 2개 기대 제거) | 사이드바 `person-list` 1개·본문 안 0개·링크 href 순서·링크 텍스트 불변 |
| R-U6-2 앱을 열면 GET /persons 1회 | 변경(최소: 대기 대상 `person-list` 2개 → `person-grid`+`person-list`) | 호출 1회 불변 |
| R-U6-2 알림 이벤트만으로도 다시 읽음 | 변경(최소: 같은 이유) | 호출 2회 불변 |
| 본문은 PersonGrid, 사이드바는 PersonList 를 import | 변경(P8 "같은 컴포넌트(PersonList)를 import" 교체) | import 문자열·`<PersonGrid />` · 본문에 PersonList import 없음 |

## web/src/__tests__/card.test.tsx — U2 사이드바 최근 5명 + 전체 보기 (신규 7 · 변경 1 · 삭제 0)

실행: `npm --prefix web test -- --run src/__tests__/card.test.tsx src/__tests__/routes.test.tsx` → 64 passed. 전체 → 156 passed (9 files, 기준선 149 → +7). 증거 `evidence/20261028-0838-u2-sidebar-vitest.txt`·`…-u2-vitest-all.txt`·`…-u2-sidebar.txt`(typecheck)·`…-u2-build.txt`, 변이 `evidence/20261028-0839-u2-mutation.txt`(V2-1a·1b·2a·2b·2c·3a·3b·4·5 + X6 전부 FAIL, 저장소 무수정). 픽스처 `SEVEN`: 서버 순서가 이름·id·날짜 어느 순과도 다르고 뒤 2명은 이름순·날짜 최신순 모두 앞 5명에 든다. `routes.test.tsx` 72~79행은 무수정 통과(인물 조회 전 시점 단언이라 "전체 보기" 링크 없음).

| 테스트 이름(요지) | 구분 | 무엇을 확인하나 · 검출 변이 |
|---|---|---|
| P8b U2 (결정 E): 7명이면 앞 5명 + 전체 보기 → | 신규 | `SIDEBAR_RECENT_LIMIT` 값 5 · 링크 href `['#/persons/51','48','55','50','53','#/persons']`·마지막 텍스트 `전체 보기 →`·`sidebar-see-all` · V2-1a, 1b, 2a, 2b, 2c, 3a, 3b |
| 5명 이하(3명)이면 3명 + 전체 보기 → | 신규 | href `['#/persons/7','4','9','#/persons']` · V2-2b, 2c, 3a, 3b |
| 정확히 5명이면 5명 + 전체 보기 (경계) | 신규 | 링크 6개 · V2-3b |
| 인물 0명이면 전체 보기 없음 | 신규 | `sidebar-see-all` 없음·글자 없음 |
| 조회 실패면 전체 보기 없음 | 신규 | `sidebar-see-all` 없음 |
| #/persons 본문 그리드는 7명 전원 | 신규 | `tileIds()` 7개 서버 순서 + 사이드바 링크 6개 · V2-1a, 1b, 3b, 5 (U1 "7명 전원" 테스트도 V2-5 를 잡음) |
| 좁은 폭 서랍에서 전체 보기 클릭 → `#/persons`·서랍 닫힘 | 신규 | 해시·`주 메뉴` 사라짐 · V2-3a, 3b, 4 |
| P8b U1 그리드 describe "목록 조회가 실패하면 한 줄 안내" | 변경(R-U1-1: `person-search` 없음 1줄 추가) | 실패 상태에서 검색창 그림 · X6 |
