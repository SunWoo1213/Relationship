# P8-frontend U1 인물 목록·카드 조회 API — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — 재검토(2026-10-11, 아래 "## 재검토" 절) 에서 [필수] R-U1-1 해소 확인(`func.max → func.min` 변이에 테스트 4건 FAIL), R-U1-3(사용자 결정 "10건 유지 + 테스트")·R-U1-4 도 변이로 검출됨. 남은 것은 03-log 기록 항목(R-U1-2·R-U1-5)만이며 코드 변경을 요구하지 않는다. (1차 판정 기록: 보류 — [필수] 1건(R-U1-1, 테스트 공백: `last_contact_at = max(occurred_at)` 계약이 변이 시험에서 검출되지 않음). 코드 자체의 결함은 찾지 못했다.)
대상: 작업 트리(기준 HEAD `440a0e5`) — 신규 `app/api/read.py`(149행) · `app/api/schemas.py`(+66/−0) · `app/api/routes.py`(+22/−0) · 신규 `tests/test_api_read_persons.py`(172행) · 구현 증거 `evidence/20261011-1350-u1-read-persons.txt`·`20261011-1350-u1-full-regression.txt`·`20261011-1351-u1-final-check.txt`. `docs/wiki/HANDOFF.md`·`journal.md` 는 위임 프롬프트대로 리뷰 대상에서 제외.
근거 문서: `01-plan.md` 92행(U1 정의) · 21~49행(범위·"하지 않는 것") · 354~368행(지킬 불변식 5) · 126~129행(판정표 1·2·4행) · 204~210행(재사용 `_owned_person`) · `02-plan-verify.md` 135행 `승인:` 조건 ① · CLAUDE.md 원칙9·데이터 모델(스키마 v2) · `docs/wiki/security.md` §1·§5 · `app/main.py` 33~45행(공통 404 규약)
내가 남긴 증거(모두 `docs/wiki/packages/P8-frontend/evidence/`): `20261011-verifier-u1-tests.txt`(U1 테스트 -v) · `20261011-verifier-u1-full-regression.txt`(전체 회귀) · `20261011-verifier-u1-lint.txt`(ruff·mypy 기준선) · `20261011-verifier-u1-mutation.txt`(변이 시험 4건)
소견 요약: [필수] 1건(R-U1-1) · [권고] 4건(R-U1-2~5). 자세한 것은 §8.

---

## 1. 절차 위반 확인 — Bash 로 쓴 세 파일에 비밀·손상·범위 밖 변경이 없는가

구현 에이전트가 `read.py`·`schemas.py`·`routes.py` 를 Write/Edit 가 아닌 Bash 로 썼다고 보고했다(CLAUDE.md "파일 변경은 Write/Edit 툴로만 한다" 위반 — secret-guard·stage-gate 미경유). 그래서 세 파일 전체 diff 를 읽고 아래를 기계적으로 확인했다.

| 확인 | 명령 | 결과 |
|---|---|---|
| 비밀·키 문자열 | `grep -nEi "sk-[A-Za-z0-9]{8,}\|AKIA[0-9A-Z]{12,}\|BEGIN .*PRIVATE KEY\|api[_-]?key\s*=\s*['\"]\|secret\s*=\|password\s*=\|token\s*="` 4파일 | 0건(exit 1) |
| 인코딩·줄끝·끝 개행 | `file -b` + Python `bytes.decode('utf-8')`, `endswith(b'\n')`, CRLF 개수 | 4파일 모두 UTF-8 정상 · 끝 개행 있음 · CRLF 0 |
| 문법 | `python -m py_compile` 4파일 | compile-ok |
| 중복 정의 | `grep -nE "^(class\|def) "` schemas.py·read.py → `uniq -d` | 중복 이름 0 |
| 기존 코드 손상 | `git diff --numstat app/api/schemas.py app/api/routes.py` | `22 0` · `66 0` — 삭제 0, 순수 추가만. `git diff` 본문도 기존 줄 변경 없음(import 블록에 2줄 삽입 + 1줄 import 추가 + 파일 끝 라우트 2개 추가 / schemas 는 파일 끝 모델 7개 추가) |
| 쓰기 라우트 불변식(01-plan 불변식 5) | `grep -cE "@router\.(post\|put\|patch\|delete)" app/api/routes.py` vs `git show 50fd7fc:…` | 4 = 4. GET 은 2 → 4(U1 두 개) |
| `raw_utterance` 언급 | `grep -n raw_utterance` 3파일 | schemas.py 39·174·279행(모두 주석/docstring, 기존 2 + 신규 설명 1) · read.py 114행(주석 "컬럼 자체를 고르지 않는다") — 코드 식별자로는 0 |
| 쓰기·trace 코드 | `grep -nEi "insert\|update\(\|delete\(\|\.add\(\|\.commit\(\|\.flush\(\|traced\|AgentTrace" app/api/read.py` | docstring 3·4행만(문장), 코드 0 |

판정: 세 파일에 비밀·잘린 줄·중복 블록·인코딩 깨짐·범위 밖 변경 없음. stage-gate 는 `CURRENT.md active: P8-frontend` 상태라 통과했을 변경이고, secret-guard 가 봤어야 할 비밀 문자열은 내 검사에서도 0 이다. **절차 위반 자체는 코드로 되돌릴 수 없으므로 소견 R-U1-2(권고) 로 기록을 요구한다.**

## 2. 01-plan 92행 U1 계약 대조

| 계약(01-plan 92행 글자 그대로) | 코드 위치 | 테스트 | 판정 |
|---|---|---|---|
| `GET /persons` → `[{id, display_name, relation_tag, hierarchy, last_contact_at\|null}]` | `schemas.py` `PersonListItemOut` 5필드(`last_contact_at: datetime \| None`) · `routes.py` `read_persons` `response_model=list[PersonListItemOut]` | `test_목록_정렬…` 75행 `set(body[0]) == {5키}` · 74행 `body[3]["last_contact_at"] is None` | 일치 |
| 정렬 `last_contact_at` 내림차순·없으면 뒤 · 필터 인자 없음 | `read.py` 55행 `.order_by(last_contact.desc().nulls_last(), Person.id.asc())` · 라우트 파라미터 없음(`session` 만) | 73행 `[c, e1, a, b, d]`(C·E 동률 → id 순, A 뒤, 이벤트 없는 B·D 뒤) | 일치. 2차 키 `id asc` 는 계획에 없는 결정적 순서 보강(docstring 48행) — 계약 위반 아님 |
| `GET /persons/{person_id}` → `person{id, display_name, relation_tag, hierarchy}` | `PersonBasicOut` 4필드 | `test_카드_구성…` 111행 dict 동치 | 일치 |
| `aliases[]` | `read.py` 73~79행 `select(PersonAlias.alias) … order_by(alias.asc())` | 114행 `["민수", "민수형"]` | 일치(정렬 기준 R-U1-4 참고) |
| `last_contact_at` = 그 인물 `events.occurred_at` 최댓값 | `read.py` 49행·84행 `func.max(Event.occurred_at)` | 목록: 73행 정렬만 · 카드: 115행 `is not None` 만 | **코드 일치 / 테스트 공백 — R-U1-1 [필수]**(§5 변이 4) |
| `facts[{id, key, value, updated_at, source_count}]`(`pattern:` 접두 제외) | `PersonFactOut` 5필드 · `read.py` 99행 `fact.key.startswith(PATTERN_KEY_PREFIX)` 분기(`app/settings.py` 269행 `"pattern:"`) · 88~95행 `count(FactSource.event_id)` LEFT JOIN GROUP BY | 117~119행 `{"취미","직업"}`, `source_count` 2·0 | 일치 |
| `patterns[{id, key, value, source_count}]`(`pattern:` 접두만) | `PersonPatternOut` 4필드(`updated_at` 없음 — 계획대로) | 120~121행 `["pattern:meal"]`, `source_count` 1 | 일치 |
| `timeline[{id, type, content, occurred_at}]`(최근 순, 상한 코드 상수 — U1 확정) | `TimelineEventOut` 4필드 · `read.py` 118행 컬럼 4개만 select(`raw_utterance` 미선택) · 120행 `occurred_at.desc(), id.desc()` · 39행 `TIMELINE_LIMIT = 20` | 122행 `[e2, e1]` · `test_타임라인_상한` 25건 → 20건·첫 항목 `내용0` | 일치 |
| `upcoming_schedules[{id, title, scheduled_at, briefed_at}]` | `UpcomingScheduleOut` 4필드 · `read.py` 130행 `scheduled_at >= now` · 131행 `scheduled_at.asc(), id.asc()` · 132행 `.limit(UPCOMING_SCHEDULES_LIMIT)` | 123행 `["곧","나중"]`(과거 제외·가까운 순) · 124행 4키 | 필드·정렬 일치. 상한 10 은 계획에 없음 — §4·R-U1-3 |
| 응답 어디에도 `raw_utterance` 없음 | 응답 모델 7개 중 해당 필드 0(`grep` §1) · 타임라인 쿼리가 컬럼을 고르지 않음 | `test_응답에_raw_utterance_가_없다` 139~143행 — 두 URL 의 응답 **원문 텍스트**에서 키·감시 문자열 0회 | 일치. 변이 3 검출(§5) |
| DB 쓰기 0 · trace 0 | `read.py` 에 쓰기·`@traced`·`AgentTrace` 코드 없음(§1) | `test_쓰기_0_trace_0` 7테이블 행 수 before == after(같은 세션이라 autoflush 로 보임) | 일치 |
| N+1 없음 | 목록 1쿼리(LEFT JOIN GROUP BY) · 카드 6쿼리 고정(소유·별칭·최근접촉·사실 집계·타임라인·일정) — 행 수에 무관 | — | 일치 |
| 판정 명령 `pytest tests/test_api_read_persons.py -v` · 증거 `evidence/*-u1-read-persons.txt` | 구현 증거 `20261011-1350-u1-read-persons.txt` 7 passed · 내 재실행 `20261011-verifier-u1-tests.txt` 7 passed | — | 일치 |

## 3. 사용자 격리

- 목록: `read.py` 53행 `.where(Person.user_id == user_id)` — `routes.py` `read_persons` 가 `app_user_id()`(`app/settings.py` 500행) 를 넘긴다. `test_목록은_다른_사용자_인물을_뺀다` 가 `user_id="other"` 인물을 넣고 내 것만 나오는지 본다. **변이 1(필터 제거) → 그 테스트 FAIL**(§5).
- 카드: `read.py` 71행 `_owned_person(session, person_id, user_id)` 재사용(`app/tools/persons.py` 417~429행, security.md §5 격리 helper — 01-plan 210행 "재사용 후보" 그대로, 공개 승격 없음을 docstring 5~7행에 명시). 없는 id·타 사용자 id 모두 `PersonNotFound` → `app/main.py` 184행 공통 404 `{"detail":{"code":"not_found"}}`. `test_없는_인물과_타사용자_인물은_같은_404` 가 두 응답 상태·본문 동치를 단언. **변이 2(소유 조건 제거) → FAIL**(§5).
- 카드의 하위 쿼리(별칭·사실·타임라인·일정)는 모두 `person.id`(소유 확인을 통과한 객체) 로 거른다 — person_id 경로 인자를 직접 쓰는 곳 없음(76·84·92·119·129행 모두 `person.id`).

## 4. 상수 판단

- `TIMELINE_LIMIT = 20`(`read.py` 39행): 01-plan 92행 "상한은 코드 상수 — U1 에서 값 확정" 에 해당. 주석 35~38행에 근거(원칙5 화면 용도·응답 크기·오래된 이벤트는 사실·패턴이 요약). 테스트 `test_타임라인_상한` 이 상수를 import 해 25건 → 20건을 확인. **계약대로.** 03-log 에 "확정값 20" 을 적어야 한다(R-U1-5).
- `UPCOMING_SCHEDULES_LIMIT = 10`(`read.py` 43행): 01-plan 92행 `upcoming_schedules` 항목에는 상한 언급이 없다. 범위("하지 않는 것") 침범은 아니고 응답 필드·정렬 계약도 지키지만, **계획에 없는 절단 동작**이며 **테스트 없는 분기**다(11건 이상일 때의 거동을 아무 테스트도 검사하지 않음). 주석 41~42행의 근거("브리핑 대상은 24시간 이내라 몇 건 안 되며")는 브리핑 창과 카드 조회 범위를 섞은 설명이다 — 카드는 24시간 밖 일정도 보여 준다. 판정: 계약 위반은 아니므로 커밋을 막지 않되, 상한을 두려면 03-log 에 결정·이유를 적고 상한 테스트를 추가하거나, 두지 않으려면 상수를 지운다 — **R-U1-3 [권고]**. 어느 쪽이든 U9 판정표 2행(미래 일정 1건)에는 영향 없다.
- "다가오는" = `scheduled_at >= now`(130행), `now` 는 `Depends(get_now)`(`app/api/deps.py` 304행, P6 U6 와 같은 주입 관례) → 테스트가 `NOW` 고정 시계로 1시간 전·3시간 뒤·2일 뒤를 구별. 적절.

## 5. 테스트 유효성 — 변이 시험 4건 (`evidence/20261011-verifier-u1-mutation.txt`)

저장소 파일을 고치지 않고, 스크래치패드의 pytest 플러그인(`-p <모듈>`, `PYTHONPATH` 로 주입)이 import 시점에 `app.api.read`/`app.api.routes` 의 함수·상수를 런타임 치환했다. 대조군(변이 없음) 7 passed.

| 변이 | 치환 | 기대 | 결과 |
|---|---|---|---|
| 1 | `list_persons` 에서 `.where(Person.user_id == user_id)` 제거 | 격리 테스트 FAIL | **FAIL 1**(`test_목록은_다른_사용자_인물을_뺀다` — `[15719, 15720] == [15719]`) — 검출 |
| 2 | `read._owned_person` 에서 `user_id` 조건 제거 | 404 테스트 FAIL | **FAIL 1**(`test_없는_인물과_타사용자_인물은_같은_404` — `200 == 404`) — 검출 |
| 3 | 카드 라우트 `response_model` 을 `raw_utterance` 포함 모델로 바꾸고 타임라인에 원문 주입 | 원문 없음 테스트 FAIL | **FAIL 1**(`test_응답에_raw_utterance_가_없다` — 응답에 `"raw_utterance":"절대노출금지"`) — 검출 |
| 4 | `read.func.max` → `func.min`(목록·카드 `last_contact_at` 집계) | 계약 "최댓값" 테스트 FAIL | **7 passed — 미검출.** `-s` 재실행으로 호출 시점 치환 로그(`[MUTATION] func.max -> func.min (호출 시점)`) 확인 |

변이 4 가 통과한 이유(테스트 코드 읽기로 확인): 목록 시험의 A 는 이벤트가 5일·9일 전이라 min 이어도 C·E(1일 전) 뒤에 놓여 순서가 같고, 카드 시험은 `body["last_contact_at"] is not None`(115행) 만 단언한다. 즉 01-plan 92행 "`last_contact_at` = 그 인물 `events.occurred_at` 최댓값" 과 판정표 2행 "`last_contact_at` = 최신 `occurred_at`" 을 **아무 테스트도 보호하지 않는다**. 코드(`func.max`)는 맞지만 그 사실을 증명하는 테스트가 없다 → R-U1-1 [필수].

그 밖의 테스트 구조: `db_session`(`tests/conftest.py` 120~130행, 바깥 트랜잭션 + SAVEPOINT, 항상 rollback)을 `get_session` 에 오버라이드하고 `get_now` 를 고정 시계로 — DB 에 잔존물 없음. `pytestmark = dbtest`, 실 PostgreSQL 사용(dbtest 는 autouse 아님, conftest 44~47행). LLM·네트워크 호출 없음(파일에 `Proposer`/`Judge`/`Embedding` 의존 없음).

## 6. 직접 재실행 (내 증거)

| 명령 | 출력 | 증거 |
|---|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v` | `7 passed in 0.49s` | `20261011-verifier-u1-tests.txt` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | `1889 passed, 1 warning in 22.64s` — skipped 줄 0(기준 1889·skip 0 과 같음; 1882 + U1 7) | `20261011-verifier-u1-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `20261011-verifier-u1-lint.txt` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 — 구현 증거 `20261011-1351-u1-final-check.txt` 와 같음. `mypy app --ignore-missing-imports` 직접 실행 38 errors/14 files, U1 세 파일 중 걸린 줄은 `routes.py:408 [union-attr] _VapidPartial`(P7 기존, 기준선 포함) 1건뿐 — U1 추가 줄(427~443행) 오류 0 | 〃 |

주의(재현하는 사람에게): `scripts/mypy_check.py` 를 `--run` 없이 단독 실행하면 stdin 을 읽어 "현재 0건" 이 나온다(내가 처음 그렇게 실행해 잘못된 결과를 얻었고 `--run` 으로 다시 돌렸다). 증거 파일은 `--run` 결과만 남겼다.

## 7. 범위·기타

- 범위 밖 변경 없음: `git status` 의 제품 변경은 `app/api/read.py`·`schemas.py`·`routes.py`·`tests/test_api_read_persons.py` 4개뿐. 스키마 v2·툴 시그니처·루프·ER·메모리·브리핑 코드 무변경(01-plan "하지 않는 것" 8번째 항목). `get_briefing` 툴 미호출(01-plan 범위 둘째 항목 — `read.py` 는 `app.tools.persons._owned_person` 만 import).
- 01-plan 55행 "`app/api/read.py` — 이름은 U1 에서 registry grep 후 확정": `registry.md` 에 `read.py`·`list_persons`·`get_person_card` 행 없음(`grep` 0건). 01-plan U9 가 "`registry.md` 갱신" 을 맡으므로 지금은 결함이 아니다 — 04-review 때 확인 항목.
- `03-log.md` 에 U1 항목 없음 — `/commit` 이 쓰는 것이라 정상. 다만 아래 소견들(Bash 쓰기 사실·상수 값·상한 결정)이 그 항목에 들어가야 한다.
- 별칭 정렬: `read.py` 77행은 SQL `ORDER BY alias ASC`(DB collation), 기존 `_person_out`(`app/tools/persons.py` 446행)은 Python `sorted()`(코드포인트). 한글·대소문자 혼합에서 순서가 갈릴 수 있다. 계약(92행)은 `aliases[]` 순서를 정하지 않으므로 위반은 아님 — R-U1-4 [권고].
- `routes.py` 의 새 라우트 docstring 이 "단일 사용자 전제(`app_user_id()`, 결정 D)" 를 적어 결정 D(01-plan 255~258행)와 연결됨. 좋다.

## 8. 소견

**[필수]** (해소 전에는 `결과: 통과` 가 될 수 없다)

- **R-U1-1 · `last_contact_at = max(events.occurred_at)` 계약을 검사하는 단언이 없다.** 근거: §5 변이 4(`func.max → func.min` 치환 후 7 passed, `evidence/20261011-verifier-u1-mutation.txt`), `tests/test_api_read_persons.py` 115행 `is not None`, 62~75행 목록 픽스처(A 5·9일 전). 01-plan 92행 "`last_contact_at` = 그 인물 `events.occurred_at` 최댓값" · 판정표 2행(128행) "`last_contact_at` = 최신 `occurred_at`" 이 기대값으로 명시돼 있는데 "항상 통과하는" 상태다. 해결 방향(구현 에이전트 몫, 내가 고치지 않음): 카드 시험에서 `body["last_contact_at"]` 을 `e2.occurred_at`(가장 최신)과 비교하고, 목록 시험에서 max/min 이 순서를 바꾸도록 픽스처를 조정(예: A 에 0.5일 전·9일 전 → max 면 A 가 C·E 앞, min 이면 뒤). 완료 판정: 변이 4 플러그인과 같은 치환에서 FAIL 1 이상 — 재검토 때 내가 같은 변이를 다시 돌린다.

**[권고]** (커밋을 막지 않음 — 03-log·다음 단위에서 반영)

- **R-U1-2 · 절차 위반 기록.** 구현 에이전트가 세 제품 파일을 Bash(heredoc·python 치환)로 써서 CLAUDE.md "파일 변경은 Write/Edit 툴로만 한다(2026-09-29 확정)" 를 어겼고 secret-guard·stage-gate 를 거치지 않았다. §1 에서 내용 손상·비밀 0 을 확인했으므로 코드 쪽 후속은 없다. 다만 (a) 03-log U1 항목에 이 사실과 §1 검사 결과를 적고, (b) `docs/wiki/fixes/FIX-014.md`(Bash 쓰기 가드 후보)에 재발 사례로 연결하고, (c) backend-agent 위임 프롬프트에 "Write/Edit 로만" 을 반복 명시하는 것을 메인 세션·사용자 판단에 올린다.
- **R-U1-3 · `UPCOMING_SCHEDULES_LIMIT = 10` 은 계획에 없는 상한이고 테스트가 없다.** 두 갈래 중 하나로: ① 상한을 유지하면 03-log 에 결정·이유를 적고(현재 주석 41~42행의 "24시간 이내" 근거는 카드 조회 범위와 맞지 않으니 고쳐 쓰기) `test_타임라인_상한` 과 같은 식의 상한 테스트 추가, ② 상한이 필요 없다고 보면 상수와 `.limit()` 삭제. 01-plan 과 어긋나지 않는 쪽은 ②이고, ①은 architect/사용자가 인지해야 한다.
- **R-U1-4 · 별칭 정렬 기준 불일치 가능성.** `read.py` 77행 SQL `ORDER BY alias`(DB collation) vs `_person_out` 446행 Python `sorted()`. 프론트(U5 인물 카드)가 툴 응답과 조회 응답을 함께 보일 일은 없지만, 같은 "별칭 목록" 이 두 규칙으로 정렬되면 혼란의 씨앗이다. 하나로 통일하거나 03-log 에 "조회 API 는 DB 정렬" 로 적는다.
- **R-U1-5 · 03-log U1 항목에 적을 것.** `TIMELINE_LIMIT` 확정값 20 과 근거(01-plan 92행 "U1 에서 값 확정"), `app/api/read.py` 이름 확정(01-plan 55행), `_owned_person` 밑줄 이름 재사용·공개 승격 안 함(01-plan 210행), Refs `P8-frontend S3.1 S3.5 원칙9`(파일 1행과 같게).

## 9. 판정

**보류.** 코드는 01-plan 92행 계약과 범위·불변식(쓰기 라우트 4=4, 원문 필드 0, 쓰기·trace 0, 사용자 격리)을 지키고, Bash 로 쓰인 세 파일에 비밀·손상은 없으며, 전체 회귀 1889 passed·ruff·mypy 기준선도 통과했다. 변이 시험 4건 중 3건(격리 2·원문 누설 1)은 테스트가 검출했다. 그러나 계약 항목 하나(`last_contact_at` 최댓값)를 보호하는 테스트가 없어 변이 4 가 통과했고, "항상 통과하는 테스트는 증거가 아니다"(`docs/wiki/verification.md`) 에 따라 그 항목의 증거가 비어 있다. R-U1-1 해소 뒤 같은 변이를 다시 돌려 FAIL 을 확인하면 통과로 바꾼다. 커밋·승인은 메인 세션·사용자 몫이다.

---

## 재검토 (2026-10-11)

검토자: verifier (fable) — 1차 리뷰와 **다른 새 컨텍스트**. 코드는 고치지 않았다.
대상: 재작업 뒤 작업 트리(기준 HEAD `440a0e5`) — `app/api/read.py`(151행) · `app/api/schemas.py`(`git diff --numstat` `66 0`) · `app/api/routes.py`(`22 0`) · `tests/test_api_read_persons.py`(236행, 12 테스트 = 1차 7 + 신규 5) · 재작업 증거 `evidence/20261011-1420-u1-rework-tests.txt`(12 passed + 손계산 근거) · `20261011-1420-u1-rework-regression.txt`(1894 passed · ruff · mypy 38/38).
사용자 결정 반영: R-U1-3 은 "10건 유지 + 테스트".
범위 밖(보지 않음·쓰지 않음): FIX-031 변경(`.claude/scripts/test-guards.sh`, `.github/workflows/tests.yml`, `docs/wiki/fixes/*`) — 다른 verifier 담당. `docs/wiki/HANDOFF.md`·`journal.md` 도 대상 아님.
내가 남긴 증거(모두 `docs/wiki/packages/P8-frontend/evidence/`): `20261011-verifier-u1-recheck-mutation.txt`(대조 + 변이 7건) · `20261011-verifier-u1-recheck-tests.txt`(U1 -v) · `20261011-verifier-u1-recheck-full-regression.txt`(전체) · `20261011-verifier-u1-recheck-lint.txt`(ruff·mypy).

### 재검토 1. R-U1-1 [필수] — 변이 4 재실행 + 변이 1~3 회귀

1차와 같은 방법: 저장소 파일 무수정, 스크래치패드의 pytest 플러그인(`-p <모듈>`, `PYTHONPATH` 주입)으로 `app.api.read` 의 이름을 import 시점에 치환. 1차 플러그인 4개가 스크래치패드에 그대로 남아 있어 **같은 파일**을 재사용했다(`mut_last_contact_min.py` 는 `read.func` 를 프록시로 바꿔 `func.max` 접근 시점에 `func.min` 을 돌려준다 — `-s` 로 "호출 시점" 로그 확인). 대조군(변이 없음) **12 passed**.

| 변이 | 치환 | 1차 결과 | 재검토 결과 | 검출 테스트 |
|---|---|---|---|---|
| 4 | `read.func.max → func.min`(목록·카드 집계) | **7 passed — 미검출** | **4 failed, 8 passed — 검출** | `test_목록_last_contact_는_max_이고_정렬은_max_기준`(`[17047, 17046] == [17046, 17047]` — 순서 뒤집힘) · `test_카드_last_contact_는_가장_늦은_occurred_at`(`2026-01-30 == NOW-1d` — 30일 전이 나옴) · `test_목록_정렬_최근순_null_뒤_동률은_id순`(`2026-02-20 == NOW-5d` — A 가 max(5,9)=5 아닌 9일 전) · `test_카드_구성과_분리_집계`(`2026-02-26 == NOW-2d`) |
| 1 | `list_persons` 의 `user_id` 필터 제거 | FAIL 1 | **FAIL 1**(`[17075, 17076] == [17075]`) | `test_목록은_다른_사용자_인물을_뺀다` |
| 2 | `read._owned_person` 의 `user_id` 조건 제거 | FAIL 1 | **FAIL 1**(`200 == 404`) | `test_없는_인물과_타사용자_인물은_같은_404` |
| 3 | 카드 `response_model` 교체 + 타임라인에 `raw_utterance` 주입 | FAIL 1 | **FAIL 1**(`"raw_utterance":"절대노출금지"` 노출) | `test_응답에_raw_utterance_가_없다` |

판정: R-U1-1 의 완료 조건("변이 4 플러그인과 같은 치환에서 FAIL 1 이상")을 **4 FAIL** 로 충족. 재작업 증거 `20261011-1420-u1-rework-tests.txt` 의 손계산(목록 A{1d,30d}·B{10d} → min 이면 `[B,A]`·`NOW-30d`; 카드 {30,1,10} → min 이면 `NOW-30d`)과 실제 FAIL 메시지가 일치한다. 1차 변이 1~3 도 여전히 검출된다(회귀 없음). 테스트 코드 읽기: `tests/test_api_read_persons.py` 66~76행(목록, 순서와 값 둘 다 단언), 79~85행(카드, `NOW-1d` 와 동치), 136행(기존 목록 시험에 `A: max(5, 9)` 값 단언 추가), 179행(기존 카드 시험에 `NOW-2d` 동치 추가) — 1차 §5 에서 지적한 `is not None` 단언(구 115행)은 값 비교로 바뀌었다.

### 재검토 2. R-U1-3 [권고 → 사용자 결정 "10건 유지 + 테스트"] — 상한·경계 테스트의 유효성

- 주석 근거: `read.py` 41~42행이 "카드 응답 크기를 묶기 위한 상한이며 가장 가까운 일정부터 채운다(과거 일정은 제외). **24시간 브리핑 범위와는 무관하다**" 로 바뀌었다 — 1차 §4 에서 지적한 "24시간 이내" 혼동 문구가 제거됨. 상한 값 10 자체는 01-plan 92행에 없으므로 03-log U1 항목에 "사용자 결정으로 유지" 를 적어야 한다(R-U1-5 와 함께).
- 상한 테스트 `test_다가오는_일정_상한은_10건_가까운_순`(101~109행): 11건을 **역순으로 삽입**(`range(11, 0, -1)`)하고 `일정1..일정10` 순서를 단언 — DB 삽입 순서가 아니라 `scheduled_at asc` 정렬과 상한을 함께 검사한다. **변이 5**(`read.UPCOMING_SCHEDULES_LIMIT = 10_000`, 상한 제거 효과) → **FAIL 1**(`Left contains one more item: '일정11'`).
- 경계 테스트 `test_다가오는_일정_경계_지금은_포함_1초_전은_제외`(112~120행): `NOW` 와 `NOW-1초` 두 건 → `["지금"]` 만. **변이 6**(`read.Schedule` 을 프록시로 바꿔 `scheduled_at.__ge__` 가 `>` 를 돌려주게 함 — `>=` → `>`) → **FAIL 1**(`[] == ['지금']`). `Schedule.scheduled_at` 은 `DateTime(timezone=True)`(`app/db/models.py` 215행) 이므로 tz-aware `NOW` 와의 동치 비교가 유효하다.
- 판정: 두 테스트 모두 실제 실패 조건을 검사한다("항상 통과" 아님).

### 재검토 3. R-U1-4 [권고] — 별칭 정렬 통일

- `read.py` 73~81행: SQL `ORDER BY` 를 빼고 Python `sorted(...)`(코드포인트)로 바꿈 — 기존 `_person_out`(`app/tools/persons.py` 432~447행, 446행 `aliases=sorted(aliases)`)과 **같은 방식**. 주석 73~74행이 그 이유("같은 인물의 별칭 순서가 API 마다 달라지지 않게")를 적었다.
- 테스트 `test_카드_별칭은_파이썬_sorted_코드포인트순`(88~98행): 입력 `("가나","apple","Zed","Bob")` → 기대 리터럴 `["Bob","Zed","apple","가나"]`(대문자 → 소문자 → 한글) 를 고정. **변이 7**(`read.sorted` 를 `sorted(key=str.casefold)` 로 덮어 콜레이션 비슷한 대소문자 무시 정렬) → **FAIL 1**(`['apple','Bob','Zed','가나'] == ['Bob','Zed','apple','가나']`). 1차 §2 의 기존 단언 `["민수", "민수형"]`(177행)도 유지.
- 판정: 통일됐고 테스트가 순서를 고정한다. 주석 89행 "콜레이션 정렬이면 apple 이 Bob 앞에 오지만" 은 DB 콜레이션 설정에 따른 서술이라 내가 검증하지 않았으나, 단언은 리터럴 순서라 그 문구에 의존하지 않는다.

### 재검토 4. 비밀·손상·범위 — diff 재검사(Write/Edit 사용 여부는 확인 불가하므로 결과로 대신)

| 확인 | 명령 | 결과 |
|---|---|---|
| 비밀·키 문자열 | 1차와 같은 `grep -nEi "sk-…\|AKIA…\|BEGIN .*PRIVATE KEY\|api[_-]?key\s*=\|secret\s*=\|password\s*=\|token\s*="` 4파일 | 0건(exit 1) |
| 인코딩·줄끝·끝 개행 | Python `decode('utf-8')`·`endswith(b'\n')`·CRLF 수 | 4파일 UTF-8 정상 · 끝 개행 있음 · CRLF 0(`read.py` 151행 · `schemas.py` 339행 · `routes.py` 443행 · 테스트 236행) |
| 문법 | `py_compile` 4파일 | compile-ok |
| 기존 코드 손상 | `git diff --numstat` | `routes.py 22 0` · `schemas.py 66 0` — 1차와 동일, 삭제 0 |
| 쓰기 라우트 불변식 | `grep -cE "@router\.(post\|put\|patch\|delete)"` vs `git show 50fd7fc:app/api/routes.py` | 4 = 4 |
| `raw_utterance` | `grep -n` 3파일 | `read.py` 116행 주석 · `schemas.py` 39·174·279행 주석/docstring — 코드 식별자 0 |
| 제품 변경 범위 | `git status --short` 의 제품 경로 | `app/api/read.py`·`schemas.py`·`routes.py`·`tests/test_api_read_persons.py` 4개뿐(FIX-031 의 하네스·CI·fixes 경로는 U1 아님). 스키마 v2·툴·루프·ER 무변경 |

### 재검토 5. 직접 재실행

| 명령 | 출력 | 증거 |
|---|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v` | **12 passed in 0.54s** | `20261011-verifier-u1-recheck-tests.txt` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **1894 passed, 1 warning in 22.52s** — skipped 줄 0(기준 1894·skip 0 과 같음 = 1차 1889 + 신규 5) | `20261011-verifier-u1-recheck-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `20261011-verifier-u1-recheck-lint.txt` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 | 〃 |

### 재검토 6. 소견 상태

| 소견 | 상태 | 근거 |
|---|---|---|
| R-U1-1 [필수] | **해소** | 재검토 1 — 변이 4 에서 4 FAIL(`…-recheck-mutation.txt`) |
| R-U1-2 [권고] | 열림(코드 아님) | 1차 Bash 쓰기 사실을 03-log U1 항목에 기록하고 FIX-014 에 연결 — 메인 세션 `/commit` 때. 재작업분의 내용 손상·비밀은 재검토 4 에서 0 |
| R-U1-3 [권고] | **해소**(사용자 결정 "10건 유지 + 테스트") | 재검토 2 — 변이 5·6 각 FAIL 1, 주석 근거 수정됨. 03-log 에 "상한 10 유지는 사용자 결정" 한 줄 필요 |
| R-U1-4 [권고] | **해소** | 재검토 3 — `sorted()` 로 통일, 변이 7 FAIL 1 |
| R-U1-5 [권고] | 열림(코드 아님) | 03-log U1 항목에 적을 것: `TIMELINE_LIMIT=20` 확정, `UPCOMING_SCHEDULES_LIMIT=10` 유지(사용자 결정), `app/api/read.py` 이름 확정, `_owned_person` 재사용, 별칭 정렬은 Python `sorted()`, Refs `P8-frontend S3.1 S3.5 원칙9` |

새 소견 없음. 재작업이 1차 소견 범위(테스트 5건 추가, 상수 주석, 별칭 정렬 1곳)를 넘지 않았다.

### 재검토 7. 판정

**통과.** 1차에서 비어 있던 증거(`last_contact_at` 최댓값 계약)가 테스트 4건의 값 단언으로 채워졌고, 같은 변이에서 FAIL 이 난다. 1차 변이 1~3 과 새 변이 5~7(상한 제거·`>=`→`>`·정렬 방식 변경)까지 **7건 모두 검출**(대조군 12 passed). 전체 회귀 1894 passed·skip 0, ruff·mypy 기준선 유지, 비밀·손상·범위 밖 변경 0. 코드에 요구하는 변경은 없다. 남은 R-U1-2·R-U1-5 는 03-log 기록 항목이며 커밋·승인은 메인 세션·사용자 몫이다.
