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
