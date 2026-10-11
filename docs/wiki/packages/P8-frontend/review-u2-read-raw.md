# P8-frontend U2 원문 조회 API — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — 코드에 요구하는 변경 없음. 01-plan 93행 계약(응답 필드·원문 그대로·내림차순+2차 키·상한 상수·사용자 격리 두 곳·`person_facts.person_id`·404 동일 응답·쓰기 0·trace 0)을 전부 지키고, 변이 8건이 모두 새 테스트에 잡혔으며(대조군 18 passed), U1 변이 2건도 여전히 검출된다. 전체 회귀 1912 passed·skip 0, ruff·mypy 기준선 유지, 비밀·손상·범위 밖 변경 0. 소견은 [권고] 4건(03-log 기록·docstring·판정표 7행 보강)만이고 커밋을 막지 않는다.
대상: 작업 트리(기준 HEAD `6c2d0e7`) — `app/api/read.py`(`git diff --numstat` `81 0`) · `app/api/schemas.py`(`39 0`) · `app/api/routes.py`(`18 1` — 삭제 1줄은 `from app.api.read import …` 한 줄을 네 이름으로 늘린 것) · 신규 `tests/test_api_read_raw.py`(304행, 18 테스트) · 구현 증거 `evidence/20261011-1520-u2-read-raw.txt`·`20261011-1520-u2-regression.txt`. 위임 프롬프트대로 `docs/wiki/fixes/FIX-014·031·032·033.md`·`HANDOFF.md`·`journal.md`·U0 증거는 대상 아님.
근거 문서: `01-plan.md` 93행(U2 정의) · 25행(범위 포함) · 36~49행("하지 않는 것") · 55·57행(파일 지도) · 76행("원문 필드는 원문 조회 두 응답에만") · 130~132행(판정표 5·6·7행) · 267~274행(결정 F) · `02-plan-verify.md` 135행 `승인:` 조건 ① · `review-u1-read-persons.md`(앞 단위 — 1차 보류 사유 "계약 값 미단언") · CLAUDE.md 원칙9·스키마 v2 · `app/main.py` 33~45행(공통 404 규약) · `docs/wiki/security.md` §1·§5.
내가 남긴 증거(모두 `docs/wiki/packages/P8-frontend/evidence/`): `20261011-1529-verifier-u2-tests.txt`(U2+U1 -v, 30 passed) · `20261011-1529-verifier-u2-full-regression.txt`(1912 passed) · `20261011-1529-verifier-u2-lint.txt`(ruff·mypy) · `20261011-1529-verifier-u2-mutation.txt`(대조군 + U2 변이 8 + U1 회귀 변이 2).

---

## 1. 01-plan 93행 U2 계약 대조

| 계약(01-plan 93행 글자 그대로) | 코드 위치 | 테스트(`tests/test_api_read_raw.py`) | 판정 |
|---|---|---|---|
| `GET /events/{event_id}/raw` → `{event_id, person_id, type, content, occurred_at, raw_utterance}` | `schemas.py` `EventRawOut` 6필드 · `routes.py` 448행 `response_model=EventRawOut` · `read.py` `get_event_raw` 컬럼 6개 select | `test_이벤트_원문_응답_전체_값` — `set(body) == {6키}` + 6필드 값 전부 동치 | 일치 |
| "저장된 문자열 그대로" | `read.py` 83행 `raw_utterance=row[5]`(가공 없음) · 120행 `raw_utterance=r` | `TRICKY_RAW`(앞뒤 공백·따옴표·HTML·이모지·`\n`·`\t`·`\\n` 리터럴·제로폭 공백) 완전 동치 · `test_이벤트_원문_긴_문자열도_자르지_않는다`(5000자) | 일치. **변이 M6**(`strip()`) → FAIL 2 |
| `GET /persons/{person_id}/facts/{fact_id}/sources` → `{fact{id, key, value}, sources[{event_id, type, content, occurred_at, raw_utterance}]}` | `FactSourcesOut{fact: FactBriefOut(3필드), sources: list[FactSourceEventOut(5필드)]}` | `test_근거_응답_전체_값과_내림차순` — `set(body) == {"fact","sources"}`, `fact` dict 동치, `sources[0]` 5키, 5필드 리스트 전부 값 동치 | 일치 |
| `fact_sources` → `events` 조인, `occurred_at` 내림차순 | `read.py` 110행 `.join(FactSource, FactSource.event_id == Event.id)` · 113행 `.order_by(Event.occurred_at.desc(), Event.id.desc())` | 삽입 순서를 섞어(`mid, old, new`) `[new, mid, old]` 단언 · `test_근거_동률_occurred_at_은_id_내림차순` `[c, b, a]` | 일치. 2차 키 `id desc` 는 계획에 없는 결정적 순서 보강(U1 의 `id` 2차 키와 같은 성격) — 위반 아님. **변이 M4**(desc→asc) → FAIL 3 · **M8**(2차 키 asc) → FAIL 1 |
| "상한 코드 상수" | `read.py` 56행 `FACT_SOURCES_LIMIT = 20` · 114행 `.limit(FACT_SOURCES_LIMIT)` | `test_근거_상한` — 상수 import, 25건 → 20건, 잘리는 쪽이 가장 오래된 5건임을 `원문0..19` 리스트로 단언, `assert FACT_SOURCES_LIMIT == 20` | 일치. 값·근거는 §3. **변이 M5**(상한 제거) → FAIL 1 |
| 사용자 격리 — 두 엔드포인트 모두 `persons.user_id = app_user_id()` 조인 조건 | `get_event_raw` 71·73행 `.join(Person, Person.id == Event.person_id)` … `.where(Person.user_id == user_id)` · `get_fact_sources` 95·98행 같은 조인·조건 · `routes.py` 두 라우트가 `app_user_id()` 를 넘김 | `test_이벤트_404_타사용자_이벤트` · `test_근거_404_남의_인물_경로의_남의_사실`(둘 다 응답 텍스트에 원문 미포함까지 단언) | 일치. **변이 M2**(이벤트 쪽 제거) → FAIL 1 · **M3**(근거 쪽 제거) → FAIL 2 |
| 두 번째는 `person_facts.person_id = person_id` 도 건다 | `read.py` 97행 `.where(PersonFact.person_id == person_id)` | `test_근거_404_내_다른_인물의_사실을_경로_인물에_끼운_경우` · `test_근거_404_없는_인물` · `test_근거_404_남의_인물_경로에_내_사실을_끼운_경우` | 일치. **변이 M1**(조건 제거) → FAIL 4 |
| 없는 것·남의 것은 같은 404 | 두 함수 모두 `PersonNotFound` → `app/main.py` 184행 핸들러 `{"detail":{"code":"not_found"}}` | 이벤트: 없음·타사용자 2경우 모두 `r.json() == NOT_FOUND` · 근거: 없는 사실·없는 인물·타사용자·내 다른 인물 4경우 + `test_근거_세_404_응답이_서로_같다`(`len({r.text}) == 1`) | 일치 — 계획의 "404 네 경우"(엔드포인트 2 × 없음/남의 것) 전부 + 추가 3경우 |
| DB 쓰기 0 · trace 0 | `read.py` 에 `insert/update/delete/.add(/.commit(/.flush(/traced/AgentTrace` 코드 0(docstring 3·4행만, `grep` exit 0 은 그 두 줄) | `test_쓰기_0_trace_0` — 7테이블 행 수 before == after(200 두 번·404 두 번 요청) | 일치(판정표 7행의 `briefed_at`·`updated_at` 값 비교는 없음 — R-U2-4) |
| 판정 `pytest tests/test_api_read_raw.py -v` · 증거 `evidence/*-u2-read-raw.txt` | 구현 증거 `20261011-1520-u2-read-raw.txt` 18 passed · 내 재실행 30 passed(U1 12 포함) | — | 일치 |

판정표(01-plan 130~131행) 5·6행 대조: 5행 "원문에 공백·이모지·줄바꿈 / 다른 사용자 이벤트 / 없는 id → 200 바이트 일치 / 404 / 404" = `TRICKY_RAW` 테스트 + 404 2건. 6행 "사실 1 에 `fact_sources` 2 / 다른 인물의 `fact_id` 를 내 `person_id` 로 / 다른 사용자 인물 → `sources` 2건·최근 순 / 404 / 404" = 근거 테스트(3건으로 더 강함) + 404 2건. 둘 다 충족.

## 2. 계획 밖 판단 — `Event.person_id == person_id`(`read.py` 112행)

- **무엇인가**: 근거 쿼리에 계획(93행 "`fact_sources` → `events` 조인")에 없는 조건 하나를 더해, `fact_sources` 행이 다른 인물의 이벤트를 가리켜도 응답에서 뺀다. 주석 "다른 인물 이벤트가 섞여도 나가지 않는다". 테스트 `test_근거에_다른_인물_이벤트가_연결돼_있어도_나가지_않는다` 가 타사용자 이벤트를 억지로 링크해 제외를 단언한다(**변이 M7** 제거 → FAIL 1).
- **정상 데이터에서 근거가 빠질 수 있는가** — `fact_sources` 를 쓰는 곳 세 군데를 읽었다(`grep -rn "FactSource" app`):
  - `app/memory/promote.py` 284~322행: 승격 배치는 `select(Event).where(Event.person_id == person.id)` 로 그 인물 이벤트만 뽑고, `app/memory/extract.py` 356행 `validate_extraction` 이 `source_event_ids ⊆ 입력 이벤트 id 집합` 이 아니면 `REASON_UNKNOWN_EVENT_ID` 로 거부한다 → 링크되는 이벤트는 항상 같은 인물.
  - `app/memory/patterns.py` 133~140행: `select(Event.id, …).where(Event.person_id == person.id)` 로 모은 이벤트만 `fact_sources` 에 넣는다.
  - `app/memory/direct_facts.py` 129~165행 + `app/memory/hooks.py` 197~198행: `event_ids_by_person.get(person_id)` — "이번 턴 그 인물의 이벤트 id 전부" 만 링크.
  - 즉 **정당하게 다른 인물의 이벤트가 근거로 연결되는 경로는 없다.** 스키마(`app/db/models.py` 165~180행 `FactSource(fact_id, event_id)`)에 "같은 인물" 을 강제하는 제약은 없으므로, 이 조건은 데이터 오염·향후 버그에 대한 방어다.
- **판정**: 계약 위반 아님(계획이 추가 조건을 금지하지 않고, 정상 데이터에서 결과가 달라지지 않는다). 범위 밖도 아님(스키마·툴·메모리 로직을 바꾸지 않고 읽기 조건만 하나 더한 것). 사용자 격리 측면에서는 `persons.user_id` 조인이 이미 사실의 소유를 확인하므로 이 조건이 없어도 **같은 사용자 안에서만** 섞일 수 있었다 — 즉 보안 구멍을 막는 조건이 아니라 "이 인물 카드의 근거에 다른 인물 발화가 보이는" 표시 오류를 막는 조건이다. **사용자에게 물을 필요 없음** — 03-log U2 항목에 "계획에 없는 방어 조건, 정상 경로 영향 없음" 으로 적으면 된다(R-U2-1).
- 참고(권고 아님, 기록만): `app/briefing/inputs.py` 152~163행 `_fact_sources` 는 같은 조인을 이 조건 없이 한다. 쓰기 경로가 위처럼 닫혀 있어 실제 차이는 없고 U2 범위도 아니다.

## 3. 상수 `FACT_SOURCES_LIMIT = 20` — 값·근거

- 01-plan 93행 "상한 코드 상수" 에 해당하며 값 확정은 U2 몫. 주석(`read.py` 51~55행)의 근거: 승격이 `MEMORY_PROMOTE_MAX_EVENTS`(`app/settings.py` 274행 = 20)건 배치 안에서 이뤄져 한 사실의 근거가 보통 그 안이고, 패턴 사실은 더 많을 수 있으나 최근 20건이면 화면 목적에 충분하다.
- 내 확인: 승격 `action="same"`(`promote.py` 231~243행)은 기존 링크에 새 배치 링크를 **더하므로** 한 사실의 근거가 배치 여러 번에 걸쳐 20건을 넘을 수 있고, 패턴 사실(`PATTERN_WINDOW_DAYS` 365일 내 같은 type 전부)도 넘을 수 있다. 그러므로 "보통 그 안" 은 첫 승격 때만 정확하고, 그 뒤에는 **잘림이 실제로 일어날 수 있는 상한**이다. 다만 ① 잘리는 쪽이 가장 오래된 것(내림차순 뒤 `limit`)이고 ② U1 카드 응답의 `facts[].source_count`·`patterns[].source_count`(`review-u1-read-persons.md` §2)가 전체 건수를 주므로 프론트(U6)가 "20건 중 일부" 를 표시할 수 있다 → 잘림이 사용자에게 보이지 않게 숨겨지는 구조는 아니다. 값 20 은 `TIMELINE_LIMIT`(20)과 같은 응답 크기 관점에서 타당하다. 03-log 에 확정값과 "넘을 수 있음·`source_count` 로 구분" 을 적을 것(R-U2-1). 응답에 `total` 필드를 더하지 않은 것은 93행 계약 필드 집합을 지킨 것이라 맞다.

## 4. 변이 시험 — 저장소 파일 무수정 (`evidence/20261011-1529-verifier-u2-mutation.txt`)

방법: 스크래치패드(`/private/tmp/claude-501/…/scratchpad/mut_u2.py`)의 pytest 플러그인을 `-p mut_u2` + `PYTHONPATH` 로 주입. 플러그인이 import 시점에 `app.api.read` 와 `app.api.routes` 양쪽의 `get_event_raw`/`get_fact_sources` 를 변이 사본으로 바꿔 끼운다(`routes.py` 가 이름을 직접 import 하므로 두 곳). 변이 종류는 환경변수 `U2_MUT`. 저장소 파일은 손대지 않았다 — 실행 뒤 `git diff --numstat app/api/read.py` 가 전과 같은 `81 0`.

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| 대조군 | 없음 | **18 passed** | — |
| M1 | `person_facts.person_id == person_id` 제거 | **4 failed** | `test_근거_404_없는_인물` · `…내_다른_인물의_사실을_경로_인물에_끼운_경우` · `…남의_인물_경로에_내_사실을_끼운_경우` · `test_근거_세_404_응답이_서로_같다`(`200 == 404`) |
| M2 | `get_event_raw` 의 `persons.user_id` 제거 | **1 failed** | `test_이벤트_404_타사용자_이벤트`(`200 == 404`) |
| M3 | `get_fact_sources` 의 `persons.user_id` 제거 | **2 failed** | `test_근거_404_남의_인물_경로의_남의_사실` · `test_근거_세_404_응답이_서로_같다` |
| M4 | `occurred_at desc` → `asc`(2차 키도 asc) | **3 failed** | `test_근거_응답_전체_값과_내림차순`(`[mid, old, new] != [new, mid, old]`) · `test_근거_동률…` · `test_근거_상한`(`'원문24' != '원문0'` — 잘리는 쪽이 뒤집힘) |
| M5 | `.limit(FACT_SOURCES_LIMIT)` 제거 | **1 failed** | `test_근거_상한`(`25 == 20`) |
| M6 | `raw_utterance.strip()` 가공 | **2 failed** | `test_이벤트_원문_응답_전체_값` · `test_근거_응답_전체_값과_내림차순`(앞뒤 공백 소실이 diff 로 보임) |
| M7 | 방어 조건 `Event.person_id == person_id` 제거 | **1 failed** | `test_근거에_다른_인물_이벤트가_연결돼_있어도_나가지_않는다`(`['남의 비밀','내 원문'] != ['내 원문']`) |
| M8 | 2차 키 `id desc` → `id asc` | **1 failed** | `test_근거_동률_occurred_at_은_id_내림차순`(`[a,b,c] != [c,b,a]`) |

구현자 보고(`20261011-1520-u2-read-raw.txt` 하단 "변이 확인" 3건: M1 4건·M2 1건·M3 2건 실패)와 내 결과가 **건수·테스트 이름까지 일치**한다. 구현자는 저장소 파일을 임시로 고쳐 돌렸다고 했는데, `git diff app/api/read.py` 에 삭제 줄 0(`grep "^-"` 결과 없음)·추가 81줄만 있고 변이 잔재(주석 처리된 조건, 중복 `.where`, `asc()` 등)가 없음을 diff 전문으로 확인했다 — 원복 완료.

U1 리뷰 1차 보류 사유였던 "계약 값 미단언" 은 U2 에 재발하지 않았다 — 모든 계약 항목이 값(필드 집합·순서 리스트·문자열 동치·건수)으로 단언돼 있고, 위 8변이가 전부 FAIL 로 증명된다.

## 5. U1 회귀 — 이전 변이 재실행 (같은 evidence 파일 하단)

| 변이(1차 리뷰 플러그인 그대로 재사용) | 결과 |
|---|---|
| `mut_last_contact_min.py` — `read.func.max → func.min` | **4 failed, 8 passed**(1차 재검토와 같은 4테스트: `test_목록_last_contact_는_max_이고_정렬은_max_기준` · `test_카드_last_contact_는_가장_늦은_occurred_at` · `test_목록_정렬_최근순_null_뒤_동률은_id순` · `test_카드_구성과_분리_집계`) |
| `mut_card_no_owner.py` — 카드 `_owned_person` 의 `user_id` 조건 제거 | **1 failed, 11 passed**(`test_없는_인물과_타사용자_인물은_같은_404`) |

U2 변경(`read.py` 에 함수 2개·상수 1개·import 추가, `routes.py` import 1줄 확장 + 라우트 2개)이 U1 함수 본문을 건드리지 않았고(`git diff` 에서 `list_persons`·`get_person_card` 영역 변경 0), U1 테스트 12건은 내 재실행에서도 전부 PASSED(`…-verifier-u2-tests.txt`).

## 6. 직접 재실행 (내 증거)

| 명령 | 출력 | 증거 |
|---|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_raw.py tests/test_api_read_persons.py -v` | **30 passed in 0.80s**(U2 18 + U1 12, PASSED 30줄) | `20261011-1529-verifier-u2-tests.txt` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **1912 passed, 1 warning in 25.46s**, skipped 줄 0 — 기준 1912·skip 0 과 같음(= U1 뒤 1894 + U2 18). exit 0 | `20261011-1529-verifier-u2-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `20261011-1529-verifier-u2-lint.txt` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 | 〃 |

## 7. 비밀·손상·범위

| 확인 | 명령 | 결과 |
|---|---|---|
| 비밀·키 문자열 | `grep -nEi "sk-[A-Za-z0-9]{8,}\|AKIA[0-9A-Z]{12,}\|BEGIN .*PRIVATE KEY\|api[_-]?key\s*=\s*['\"]\|secret\s*=\|password\s*=\|token\s*="` 4파일 | 0건(exit 1) |
| 인코딩·줄끝·끝 개행 | Python `decode('utf-8')`·`endswith(b'\n')`·CRLF 수 | 4파일 UTF-8 정상 · 끝 개행 있음 · CRLF 0(`read.py` 232행 · `schemas.py` 378행 · `routes.py` 460행 · 테스트 304행) |
| 문법 | `py_compile` 4파일 | compile-ok |
| 기존 코드 손상 | `git diff --numstat` | `read.py 81 0` · `schemas.py 39 0` · `routes.py 18 1`(삭제 1 = import 한 줄 확장, diff 본문 확인). `git diff app/api/read.py \| grep "^-"` → 삭제 줄 0 |
| 쓰기 라우트 불변식(01-plan 불변식) | `grep -cE "@router\.(post\|put\|patch\|delete)"` HEAD vs 트리 | 4 = 4. GET 은 6 → 8(U2 두 개, `routes.py` 448·455행) |
| `raw_utterance` 가 나가는 자리 | `grep -n raw_utterance app/api/*.py` | 코드 식별자는 `read.py` 69·83·108·120행(U2 두 함수 안)과 `schemas.py` 357·371행(`EventRawOut`·`FactSourceEventOut`)뿐 — 01-plan 76행 "원문 필드는 원문 조회 두 응답에만" 대로. `schemas.py` 345행 주석 "유일한 모델 두 개" 가 이를 명시 |
| 제품 변경 범위 | `git status --short` | 제품 경로는 `app/api/read.py`·`schemas.py`·`routes.py`·`tests/test_api_read_raw.py` 4개뿐. 스키마 v2·툴 7종·루프·ER·메모리·브리핑 코드 무변경(01-plan 46행 "하지 않는 것"). `app/memory/*`·`app/briefing/*` 는 읽기만 했고 diff 없음 |
| registry | `grep` `get_event_raw\|get_fact_sources\|read.py` `docs/wiki/registry.md` | 0건 — U9 가 "registry.md 갱신" 을 맡으므로 지금은 결함 아님(U1 리뷰 §7 과 같은 판단), 04-review 확인 항목 |

## 8. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음 — 03-log·다음 단위에서 반영)

- **R-U2-1 · 03-log U2 항목에 적을 것.** ① `FACT_SOURCES_LIMIT = 20` 확정값과 근거(§3 — 승격 `same` 누적·패턴 사실은 20건을 넘을 수 있고, 그때 가장 오래된 것이 잘리며 전체 건수는 U1 `source_count` 로 구분), ② 계획에 없는 방어 조건 `Event.person_id == person_id`(§2 — 정상 경로에서 결과 차이 없음, 쓰기 경로 세 곳 모두 같은 인물 이벤트만 링크), ③ 2차 정렬 키 `id desc`, ④ Refs `P8-frontend U2 S3.1 R8 원칙9`(테스트 파일 1행과 같게).
- **R-U2-2 · `app/api/read.py` 모듈 docstring 이 U1 시점 그대로다.** 1행 "Refs: P8-frontend U1 S3.1 S3.5 원칙9 -- 읽기 전용 조회 함수(인물 목록·카드)" 와 2~12행이 원문·근거 함수를 언급하지 않는다. 01-plan 55행은 이 파일을 "인물 목록·카드·원문·근거·브리핑 조회" 로 정의한다. U2 커밋에 포함하거나(한 줄 수정) U3 때 함께 고친다 — 어느 쪽이든 03-log 에 적는다.
- **R-U2-3 · 판정표 7행(01-plan 132행)의 `schedules.briefed_at`·`persons.updated_at` 변화 0 은 아직 어느 테스트도 값으로 보지 않는다.** `test_쓰기_0_trace_0`(U2)·U1 의 같은 이름 테스트는 7테이블 **행 수**만 비교한다. 읽기 전용 SELECT 가 이 두 컬럼을 바꿀 경로는 없으므로 결함이 아니라 판정표와 테스트의 어긋남이다 — U3 의 `GET /briefings` 조회(`briefed_at` 과 가까운 코드)를 만들 때 공통 픽스처로 두 값을 함께 단언하거나, U9 판정표 7행의 증거 열에 "행 수 비교로 대체" 를 적고 verifier 가 04-review 에서 받아들일지 판단한다.
- **R-U2-4 · 구현 증거의 변이 확인은 저장소 파일을 임시 수정해 수행됐다**(`20261011-1520-u2-read-raw.txt` "임시로 코드를 고쳐 실행한 뒤 원복"). 결과는 §4 에서 저장소 밖 플러그인으로 재현돼 신뢰할 수 있고 원복도 확인됐으나, 활성 작업 중 제품 파일을 변이 상태로 두는 방식은 그 사이 `git add` 가 끼면 변이가 커밋될 위험이 있다. 다음 단위부터 backend-agent 위임 프롬프트에 "변이 시험은 저장소 밖 사본·런타임 치환으로" 를 넣는 것을 메인 세션 판단에 올린다(코드 변경 아님).

## 9. 판정

**통과.** 01-plan 93행의 계약 항목 전부가 코드에 있고 각 항목을 값으로 단언하는 테스트가 있으며, 그 테스트들이 "항상 통과" 가 아님을 변이 8건(격리 3·사실 소유 1·정렬 2·상한 1·원문 가공 1 — 모두 FAIL)으로 확인했다. 계획 밖 조건(`Event.person_id`)은 쓰기 경로 세 곳을 읽어 정상 데이터에 영향이 없는 방어로 판정했고 사용자 결정이 필요하지 않다. U1 변이 2건이 여전히 검출되고 전체 회귀 1912 passed·skip 0, ruff·mypy 기준선 유지, 비밀·손상·범위 밖 변경 0. [필수] 소견 없음, [권고] 4건은 03-log·U3·U9 에서 받는다. 커밋·승인은 메인 세션·사용자 몫이다.
