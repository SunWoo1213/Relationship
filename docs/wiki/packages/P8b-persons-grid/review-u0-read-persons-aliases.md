# P8b-persons-grid U0 `GET /persons` 응답에 `aliases` — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 3(R-U0-1 M3 격리 변이 생존은 출력 동등이나 질의 범위 비동등, R-U0-2 03-log 기록 항목, R-U0-3 01-plan 행 번호 표기). 코드 결함은 찾지 못했다. 변이 7건 중 6건 검출(대조군 17 passed), 전체 회귀 1958 passed·skip 0, ruff 통과, 범위 밖 diff 0.
대상: 작업 트리(기준 HEAD `0973858`, 제품 코드 기준 `3bd5025`) — `git diff 3bd5025 -- app/api/read.py app/api/schemas.py tests/test_api_read_persons.py`(`--numstat` `11 0` · `2 1` · `77 1`) · `docs/wiki/registry.md` 비고 3곳("P8b U0(해시 pending)") · 신규 `docs/wiki/packages/P8b-persons-grid/tests.md` · 구현 증거 `evidence/20261027-1436-u0-read-persons-aliases.txt`·`-1436-u0-pytest-all.txt`·`-1435-u0-ruff.txt`·`-1437-u0-mutation.txt`. `HANDOFF.md`·`journal.md`·`01-plan.md`/`02-plan-verify.md` 의 문서 diff 는 위임대로 리뷰 대상 아님(01-plan U0 줄의 "사용자 확정 (i)" 문구·02-plan-verify 의 `결과:` 표기 수정은 읽기만 했다).
근거 문서: `01-plan.md` 75행(U0 계약) · 35~46행("하지 않는 것") · 136행(판정 1행 U0 몫) · 143행(판정 8행) · `docs/wiki/decisions/D15-persons-screen-layout.md` 23행(코드 규칙 1번째 줄)·33행(결정 2 보정) · `docs/wiki/verification.md` · `docs/wiki/security.md` · CLAUDE.md 원칙7·9 · `app/api/read.py` 186~194행(`get_person_card` 별칭 정렬) · 메인 세션 사전 결정(기존 테스트 137행 키 집합에 `"aliases"` 1줄 추가 허용).
내가 남긴 증거(모두 `docs/wiki/packages/P8b-persons-grid/evidence/`): `20261027-1535-verifier-u0-tests.txt`(U0 파일 -v) · `20261027-1535-verifier-u0-full-regression.txt`(전체 `-q -rs`) · `20261027-1535-verifier-u0-lint.txt`(ruff) · `20261027-1537-verifier-u0-mutation.txt`(대조군 + 변이 7건 + 진단 2건 + 끝의 `git status --short`).

---

## 1. 본 것 — 01-plan 75행 U0 계약 대조

| 계약(01-plan 75행 글자 그대로) | 코드 위치 | 테스트 | 판정 |
|---|---|---|---|
| `PersonListItemOut` 에 `aliases` | `schemas.py` 320행 `aliases: list[str]`(필수 필드, 기본값 없음) · docstring 1줄 갱신 | `test_목록_정렬_최근순_null_뒤_동률은_id순` 137~139행 키 집합 6개 | 일치 |
| 정렬 = 카드와 같은 Python `sorted()` 코드포인트 순 | `read.py` 176행 `aliases=sorted(by_person.get(p.id, []))` — 카드 `read.py` 188행 `aliases = sorted(session.execute(...).scalars().all())` 와 같은 내장 `sorted()`(키 없음) | `test_목록_별칭은_카드_별칭과_같은_값_같은_순서` 224~234행: 리터럴 `["Bob","Zed","apple","가나"]`·`["Cat","bat","민수형"]` + 카드 응답 `aliases` 와 동치 | 일치. 변이 M2(`sorted` 제거)·M6(`key=str.lower`) 모두 검출(§3) |
| 별칭 집계 질의 1회(N+1 금지) — 사용자 확정 (i): 인물 3명·10명 SELECT 수 동일 단언 | `read.py` 161~168행 `select(PersonAlias.person_id, PersonAlias.alias).join(Person).where(Person.user_id == user_id)` 1회 → `by_person` dict | `test_목록_SELECT_수는_인물_수와_무관한_상수` 264~271행: `n3 == n10 == 2` | 일치. 변이 M1(N+1) 검출 `5 == 12`. 계측 유효성은 §4 |
| 원문 필드 없음·쓰기 0(P8 판정 4·7행 단언 유지) | `list_persons` 148~180행에 `raw_utterance`·`content`·`traced`·`AgentTrace`·`commit`·`flush`·`.add(` 0건(`grep` exit 1) · 별칭 질의가 `embedding` 컬럼을 고르지 않음(D1 진단의 SQL 본문) | `test_목록_응답에_원문_키가_없다` 284~290행(행 키 `isdisjoint`, 본문에 감시 문자열 0) · 기존 `test_쓰기_0_trace_0` 293~318행 `assert_no_writes`(9테이블 행 수 + `briefed_at`·`updated_at` 값) 무수정 | 일치 |
| `web/src/api/types.ts` 동기화는 U1 | `git status --short -- web` 0줄 | — | 일치 |
| `_person_out` 재사용 여부는 registry 61행 보고 | 재사용하지 않고 카드와 같은 방식(`sorted()` 직접)으로 구현 — `get_person_card` 도 `_person_out` 을 쓰지 않으므로 일관 | — | 위반 아님. 03-log 에 "재사용 안 함·이유" 한 줄(R-U0-2) |
| 판정 명령 `pytest tests/test_api_read_persons.py -v` · 증거 `*-u0-read-persons-aliases.txt` | 구현 증거 17 passed · 내 재실행 17 passed(`…-verifier-u0-tests.txt`) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v` | **17 passed in 0.72s**, skip 0 | `20261027-1535-verifier-u0-tests.txt` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **1958 passed, 1 warning in 25.35s** — skipped 줄 0. 기준선 1953 + 신규 5 = 1958 | `20261027-1535-verifier-u0-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `20261027-1535-verifier-u0-lint.txt` |
| `git diff 3bd5025 --stat -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` | 빈 출력 | 판정 8행 |
| `git diff 3bd5025 --stat -- tests ':!tests/test_api_read_persons.py'` | 빈 출력 | 판정 8행 |
| `git diff --stat 3bd5025 -- alembic` | 빈 출력(마이그레이션 0) | 판정 8행 |
| `git status --short -- web \| wc -l` | 0 | 범위 |
| `git diff 3bd5025 -- tests/test_api_read_persons.py \| grep -E "^-[^-]"` | 삭제 줄 **1개**뿐(137행 옛 키 집합 단언) — 기존 테스트 11건 본문 무수정, 메인 세션 사전 결정과 일치 | — |
| 비밀 문자열 `grep -nEi "sk-…\|AKIA…\|BEGIN .*PRIVATE KEY\|api[_-]?key\s*=\|secret\s*=\|password\s*=\|token\s*="` (3파일 diff) | 0건(exit 1) | security.md |
| `pytest --collect-only -q tests/test_api_read_persons.py` | 17건 수집 — `tests.md` 표의 6행 이름이 수집 목록과 1:1(§5) | — |

## 3. 변이 시험 — 내가 직접 (`20261027-1537-verifier-u0-mutation.txt`)

방법: 스크래치패드 `verifier-u0/mutate.sh` 가 저장소 밖 사본(`app`·`tests`·`pyproject.toml`·`alembic`·`alembic.ini` 복사)에 문자열 치환(정확히 1곳만 — 아니면 중단)을 적용하고 `pytest tests/test_api_read_persons.py -q -p no:cacheprovider` 를 돌린다. 저장소 무수정 — 스크립트 끝의 `git status --short` 가 리뷰 전과 같다(제품 파일 3 + 문서 + 증거만). 구현자의 `u0/mutate.sh` 와는 별개 디렉터리·별개 스크립트다.

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군 | 없음 | **17 passed** | — |
| M1 N+1 | `by_person.get(p.id, [])` → 인물마다 `select(PersonAlias.alias).where(person_id == p.id)` | **FAIL 1** `assert 5 == 12` | `test_목록_SELECT_수는_인물_수와_무관한_상수` |
| M2 `sorted()` 제거 | `aliases=by_person.get(p.id, [])` | **FAIL 1** `['Zed','가나','apple','Bob'] == ['Bob','Zed','apple','가나']` | `test_목록_별칭은_카드_별칭과_같은_값_같은_순서` |
| M3 별칭 질의 `user_id` 조건 제거 | `.where(Person.user_id == user_id)` 삭제(조인은 유지) | **17 passed — 생존** | 없음 → §3.1 판정 |
| M4(verifier) `aliases` 를 `display_name` 으로 | `aliases=[p.display_name]` | **FAIL 3** `['A'] == ['Bob',…]` · `['A'] == []` · `[(id,['내사람'])] == [(id,['내별칭'])]` | 값·빈 배열·격리 테스트 셋 |
| M5(verifier) 빈 배열 대신 `None` | `read.py` 만 치환됨(`schemas.py` 의 `aliases: list[str]` 는 `PersonCardOut` 에도 있어 "1곳" 조건에 걸려 치환 중단 — 로그의 `AssertionError: 치환 대상이 정확히 1개가 아님: 2`) → 모델이 `None` 을 거부해 `ValidationError` | **FAIL 6**(`read.py:170 ValidationError`, `test_목록_별칭_없는_인물은_빈_배열` 포함) | 필수 필드 `list[str]` 자체가 방어. 스키마까지 `list[str] \| None` 으로 느슨하게 했을 때는 `test_목록_별칭_없는_인물은_빈_배열` 의 `== []` 단언이 잡는다(읽기로 확인, 재실행은 안 함) |
| M6(verifier) 정렬 키 `str.lower` | `sorted(..., key=str.lower)` | **FAIL 1** `['apple','Bob','Zed','가나'] == ['Bob','Zed','apple','가나']` | `test_목록_별칭은_카드_별칭과_같은_값_같은_순서` |
| M7(verifier) 집계 키 오류 | 모든 별칭을 모든 인물에 붙임 | **FAIL 2** `['비'] == []` 외 | 값·빈 배열 테스트 |

### 3.1 M3 판정 — 출력 동등, 질의 비동등. [권고] R-U0-1

- 왜 생존하나(코드 읽기): `rows`(`read.py` 151~158행)는 `Person.user_id == user_id` 로 걸러진 내 인물뿐이고, 응답은 `by_person.get(p.id, [])` 로 **내 인물 id 만** 조회한다. `person_aliases.person_id` 는 한 인물에 속하고 인물은 한 사용자에 속하므로 타 사용자 별칭은 `by_person` 에 **적재되지만 응답으로 나갈 경로가 없다**. 그래서 `test_목록_별칭에_다른_사용자_별칭이_섞이지_않는다`(274~281행)가 통과한다 — 테스트가 틀린 게 아니라 응답 계약으로는 정말 같다.
- 동등하지 않은 점: (a) 성능 — `user_id` 조건이 빠지면 **전체 사용자의 별칭 전부**를 매 목록 호출마다 메모리로 올린다(현재는 단일 사용자 전제(P8 결정 D)라 체감 0). (b) 심층 방어 — 응답 매핑이 바뀌는 날(예: `by_person` 을 그대로 직렬화) 격리가 코드 한 줄에 의존한다. 지금 코드는 조건이 **있으므로** 결함이 아니다.
- 테스트로 잡을 가치: 있다, 그러나 [필수] 는 아니다. 응답 불변식(원칙·D15·01-plan 의 계약)은 이미 보호되고, 질의 범위는 계약에 적혀 있지 않다. 잡으려면 `after_cursor_execute` 로 별칭 SELECT 의 `cursor.rowcount` 가 내 별칭 수와 같음을 단언(타 사용자에게 별칭 여러 개를 심어 두고)하거나, 캡처한 문장에 `persons.user_id` 바인드가 있는지 보는 식 — 후자는 문장 문자열에 묶여 깨지기 쉽다. 방향 선택은 구현 에이전트·사용자 몫.

## 4. 질의 횟수 계측의 유효성

- `_count_selects`(246~261행): `db_session.get_bind()` 는 `Session(bind=connection)`(`tests/conftest.py` 124행)이라 **Connection 객체**를 돌려주고, `event.listen(conn, "before_cursor_execute", …)` 는 그 연결로 나가는 모든 커서 실행을 받는다. TestClient 의 라우트는 `get_session` 오버라이드로 **같은 세션·같은 연결**을 쓰므로(`client` 픽스처 33~37행) 요청 중 SQL 이 빠짐없이 잡힌다. `finally` 에서 `event.remove` 로 리스너를 떼므로 두 번째 호출(10명)에서 중복 집계가 없다.
- 진단 D1(테스트 사본에 문장 출력 추가): 3명·10명 각 호출에서 정확히 2문장 — ① `SELECT persons.… , max(events.occurred_at) …`(목록) ② `SELECT person_aliases.person_id, person_aliases.alias FROM person_aliases JOIN persons ON … WHERE persons.user_id = %(user_id)s`(별칭). 상수 2 는 내 실행에서도 같다. 별칭 질의가 `embedding` 컬럼을 고르지 않는 것도 여기서 확인.
- 진단 D2(`SELECT` 필터를 빼고 모든 문장을 셈): 그래도 `n3 == n10 == 2` 로 통과 — 요청 중 INSERT·SAVEPOINT 가 섞이지 않는다(픽스처 `_alias`·`_person` 이 `flush()` 를 끝내고 호출하기 때문). 즉 `startswith("SELECT")` 필터는 INSERT 픽스처를 잘못 세지 않으며, 없어도 결과가 같다 — 필터는 의도 명시용으로 무해.

## 5. `tests.md`·`registry.md`

- `tests.md` 표 6행 ↔ `--collect-only` 17건: 신규 5 이름(`…같은_값_같은_순서`·`…빈_배열`·`…SELECT_수…`·`…섞이지_않는다`·`…원문_키가_없다`)과 변경 1(`…동률은_id순`) 모두 수집 목록에 있고 이름이 글자 그대로 같다. 표 밖 11건은 P8 에서 기록된 기존 테스트.
- 결과 칸 "17 passed"·"1958 passed, skip 0"·변이 `U0-M1`/`U0-M2` 검출·`U0-M3` 미검출 — 구현 증거 `…-1436-…`·`…-1437-u0-mutation.txt` 및 내 재실행과 일치. M3 행의 "동등 변이" 서술은 §3.1 대로 "출력 동등" 으로 읽어야 정확하다(문서 수정 요구는 아님, R-U0-2 에서 03-log 문구로).
- `registry.md` 비고 3곳(`read.py` 모듈 행·`schemas.py` 모듈 행·테스트 행)이 "P8b U0(해시 pending)" 로 달렸고 내용(질의 1회·`sorted()`·SELECT 2·17건)이 코드와 맞다. 커밋 뒤 해시 치환은 메인 세션 몫.

## 6. 범위·원칙

- 원칙7: 응답 가공 0 — 별칭은 DB 문자열 그대로, 정렬만. 원문(`raw_utterance`·`content`) 0(§1). 제외 범위(필터 컨트롤·새 파라미터·새 라우트)에 닿는 코드 없음 — `routes.py` 무변경(판정 8행 빈 출력).
- 원칙9: 읽기 API 라 trace 0 이 계약(P8 판정 7행) — `test_쓰기_0_trace_0` 의 `agent_traces` 행 수 비교가 그대로 지킨다.
- 스키마 v2·툴 시그니처·`alembic` 무변경(판정 8행 세 diff 빈 출력). "하지 않는 것" 35~46행 중 백엔드 관련 항목(`app/`·`alembic/` U0 밖 변경 0·마이그레이션 0)이 지켜졌다.
- 정렬 동률: `person_aliases(person_id, alias)` UNIQUE(`app/db/models.py` 128행)라 같은 인물 안에 같은 별칭이 없어 `sorted()` 결과가 결정적이다.

## 7. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U0-1 · M3(별칭 질의 `user_id` 조건 제거) 가 테스트에서 생존한다 — 출력 동등이지 질의 동등이 아니다.** 근거: §3 표 M3 `17 passed`, §3.1. 현재 코드는 조건을 갖고 있으므로 결함이 아니다. 질의 범위까지 보호하려면 `cursor.rowcount` 기반 단언(타 사용자 별칭 다수 삽입 → 별칭 SELECT 가 돌려준 행 수 == 내 별칭 수) 한 건을 다음 백엔드 단위나 FIX 에서 고려. 단일 사용자 전제(P8 결정 D)가 유지되는 동안은 성능 영향 0.
- **R-U0-2 · 03-log U0 항목에 적을 것(메인 세션).** ① 기존 테스트 137행 키 집합에 `"aliases"` 1줄 추가(사전 결정) 외 기존 11건 무수정 — `git diff` 삭제 줄 1개로 확인. ② `_person_out` 재사용 안 함(카드 `get_person_card` 와 같은 방식으로 `sorted()` 직접 — registry 61행 보고 요구 충족). ③ M3 는 "출력 동등·질의 비동등"(§3.1). ④ `02-plan-verify.md` `결과:` 줄의 굵게 표기 제거는 `stage-gate.sh` 정규식 때문(하네스 FIX 후보 — 메인 세션이 이미 그 줄에 적었음). Refs `P8b-persons-grid D15 CR-003 원칙7 원칙9 R-U10R-10`.
- **R-U0-3 · 01-plan 75행 "`read.py` 177행과 같은 Python `sorted()`" 의 행 번호는 U0 삽입 뒤 188행이 됐다.** 계약 내용은 그대로이고 행 번호만 어긋난다. 고칠지는 메인 세션 판단(계획 문서는 verifier 가 고치지 않는다).

## 8. 판정

**통과.** `aliases` 추가가 01-plan 75행 계약(카드와 같은 `sorted()` 순·질의 1회·원문 0·쓰기 0·`types.ts` 는 U1)과 D15 코드 규칙 1번째 줄(`read.py`·`schemas.py`·그 테스트 밖 `app/`·`alembic/` diff 0)을 지키고, 내 재실행에서 17 passed·전체 1958 passed(기준 1953 + 5)·skip 0·ruff 통과다. 변이 7건 중 6건을 테스트가 검출했고(대조군 17 passed), 생존한 M3 는 응답 계약 기준으로 동등함을 코드로 확인했다(§3.1 — [권고]). SELECT 수 계측은 실제 두 문장(목록·별칭)을 세며 픽스처 INSERT 를 섞지 않는다(§4). 기존 테스트는 사전 결정한 1줄 외 무수정, 비밀·범위 밖 변경 0. 코드에 요구하는 변경은 없다. 커밋·승인은 메인 세션·사용자 몫이다.
