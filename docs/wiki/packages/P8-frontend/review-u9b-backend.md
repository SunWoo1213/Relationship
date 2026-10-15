# P8-frontend U9b 백엔드 행 1~11·전체 회귀·R-U3-1·2·5·끝에서 끝 2건·tests.md 백엔드 절·실패 이력 열·`docs/reliability.md` 초안 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: **통과 — [필수] 0 · [권고] 5 (R-U9b-1~5).** 코드 변경은 계획이 가리킨 두 곳뿐이고(`routes.py` R-U3-1 · `read.py` R-U3-2), 판정표 1~11행과 28행 백엔드 부분을 내가 직접 재실행해 전부 기대값(64 passed · 1946 passed skip 0 · `alembic check`·`tools_check` 7/7·무변경 diff 빈 출력). 구현자 변이 13종 중 5종을 재현해 실패 건수·테스트 이름까지 일치, 내 고유 변이 3종 중 **V2(조인을 `Schedule.person_id` 만으로)가 64건 전체에서 살아남음** — R-U3-2 방어 조건을 한 방향만 시험하는 테스트 틈이며 결함은 아니다(사용자 격리는 V2 에서도 유지, R-U9b-1). tests.md 백엔드 64행은 pytest 수집 이름과 64:64 일치, 203행 전부 5열, 실패 이력 집계 5/16/4/1/177 재계산 일치. `docs/reliability.md` 수치는 전부 원문과 일치(§6 — 출처 귀속 표현 1곳만 정정 권고). 훅이 검사하지 않은 경로(worktree → `git apply`)로 들어온 diff 를 전부 읽었고 범위 밖 변경·비밀 문자열 0(§7). 커밋·승인은 메인 세션·사용자 몫이다.

증거(내가 만든 것): `evidence/20261015-1627-verifier-u9b-mutation.txt`(대조군 64 passed + 변이 10회, 매회 원복 바이트 일치). 그 밖 직접 실행 결과는 본문에 명령·출력 요약으로 적었다(전체 회귀는 백그라운드 실행 — `1946 passed, 1 warning in 23.84s`, exit 0).

기준: 01-plan 100행 U9 항목·판정표 1~11·28행 / 03-log 183행 U9b 몫 / review-u3 101·102·105행(R-U3-1·2·5)·32행·106행 ④ / 사용자 결정 03-log 159·170행.

## 1. 코드 변경 — 계획과의 정합 (`git diff -- app/`)

| 항목 | 코드 | 근거 | 판정 |
|---|---|---|---|
| R-U3-1 (review-u3 101행 "`ctx = replace(build_chat_ctx(session, session_id, None), now=now)`") | `routes.py` 482~484행 — 제안 문장 그대로 + `from dataclasses import replace` 106행 | `run.py` 183행 관례와 같음. `deps.py` 무변경(`git status` 에 없음) | 일치. 변이 M1(`now=now` 제거) 내 재현 **6 failed, 2 passed**(증거 89~317행) — 구현자와 건수·이름 동일 |
| R-U3-2 (102행 "`Person.id == Schedule.person_id` 방어 조건") | `read.py` 323~325행 `.join(Person, (Person.id == ranked.c.pid) & (Person.id == Schedule.person_id))` + 주석 | 정상 데이터(run.py 224~225행 두 키 동일)에서 결과 불변 — 64건 대조군 통과가 그 증거 | 일치. 변이 M2(조건 제거) 내 재현 **1 failed**(`test_조작된_trace_…`, 319~399행). **단방향** — §4 V2 |
| R-U3-5 ① (105행 "U1·U2 `test_쓰기_0_trace_0` 을 헬퍼로") | `test_api_read_persons.py` 217~242행 · `test_api_read_raw.py` 282~305행 — `snapshot_db`/`assert_no_writes` 사용, `updated_at` 30일 전·`briefed_at` 7시간 전으로 못 박고 값 단언 | 옛 판은 7모델 `count()` 만(diff `-` 줄) | 일치. 구현자 M4a~M4e 5종 검출 + **옛 테스트로는 5종 전부 생존**(`-1523-u9-be-mutation-old-tests.txt` 33·62·97·132·161행 `12 passed`/`18 passed`) — 보강 필요성이 증거로 남음 |
| R-U3-5 ② (105행 "`_COUNTED_MODELS` 에 `push_subscriptions`") | `helpers_read_api.py` 45행 `PushSubscription` → 9모델, docstring 5~7행 "9개 테이블" | 스키마 v2(CLAUDE.md) 9테이블 | 일치. 변이 M3 내 재현 **1 failed**(`assert 8 == 9`, 401~457행) |
| 판정표 11행 무변경 | 내 직접 실행: `alembic check` → "No new upgrade operations detected." · `tools_check.py` → "RESULT: 7/7 ok" · `git diff --stat 50fd7fc -- app alembic ':!app/api/routes.py' ':!app/api/schemas.py' ':!app/api/read.py'` → 빈 출력 exit 0 | 01-plan 11행 | 통과 |

계획 밖 상수·방어 조건: `read.py` 의 새 조인 조건은 R-U3-2 가 요구한 그것이고, 그 밖 새 상수·분기 0. "하지 않는 것"(새 엔드포인트·스키마·`deps.py`·`web/`) 침범 0 — `git status --short -- web` 0줄.

## 2. 판정표 1~10행 — 표의 입력·기대 ↔ 테스트

내 대조군 실행(증거 9~84행): 5파일 **64 passed**. 행별 대응:

| 행 | 테스트(현재 이름) | 표의 입력·기대가 코드에 있는가 |
|---|---|---|
| 1 | `persons::test_목록은_다른_사용자_인물을_뺀다`·`test_목록_정렬_최근순_null_뒤_동률은_id순` | 사용자 2명·`last_contact_at` null 뒤·키 5개 — 있음 |
| 2 | `persons::test_카드_구성과_분리_집계` | 별칭 2·사실 3(`pattern:` 1)·`fact_sources`·일정 과거/미래·타임라인 최근 순 — 있음 |
| 3 | `persons::test_없는_인물과_타사용자_인물은_같은_404` | 둘 다 `{"detail":{"code":"not_found"}}` — 있음 |
| 4 | `persons::test_응답에_raw_utterance_가_없다` | 감시 문자열·키 0회 — 있음 |
| 5·6 | `raw::test_이벤트_원문_응답_전체_값`(`TRICKY_RAW` 공백·이모지·줄바꿈)·404 2종 · `test_근거_응답_전체_값과_내림차순`·404 4종·`test_근거_상한`(`FACT_SOURCES_LIMIT+5` → 20, 173~178행) | 있음 |
| 7 | `persons/raw/pending/briefings` 의 `쓰기_0` 5건 + 헬퍼 자체 2건 | 9테이블 행 수 + `briefed_at`·`updated_at` **값**. 9행(`GET /briefings`)의 쓰기 0 은 U3 단위 `test_쓰기_0_trace_0_briefed_at_updated_at_불변` 이 맡고 e2e 2건에는 쓰기 0 단언이 없다 — 표 7행 충족에는 충분 |
| 8 | `pending::test_만료_경계_24시간`(117~119행: 24h−1s / 정확히 24h / 25h)·`test_다른_세션_질문은_제외`·`test_헤더_없으면_빈_목록_이고_쓰기_0`·`test_형식_위반_세션_헤더는_422` | 있음 |
| 9 | `briefings_e2e::test_9행_…` | **trace 를 실제 실행이 만든다**: 경로 1 `client.post("/briefings/run", …)`(144행), 경로 2 `run_briefings(_ctx(…), …, trigger="scheduler")`(148행). 두 항목의 `lines`·`suggestion`·`pattern_sentences`·`composer`·`push`·`trace_id`·`generated_at` 을 compose 행과 값으로 비교, `title`·`display_name` 채워짐, `briefing_run` trace `trigger` 가 `["manual","scheduler"]`(178~184행) — 표 9행 전부. 직접 삽입 0 |
| 10 | `briefings_e2e::test_10행_…` | 재실행 2회(응답 다르게, 201~206행) · 사용자 B 는 **실제 실행**(`run_briefings(_ctx(db, user_id="other"), …)` 211~215행) · 원문 감시 문자열 3종 0회 · 직접 삽입은 `STEP_BRIEFING_ERROR` **만**(220~229행, s1·s3) · `?schedule_id=` 모드 동일 행 — 표 10행 중 "`briefing_run` 행을 `output` 에 같은 `schedule_id`·`person_id` 로 추가" 부분은 §3 R-U9b-2 |

사실 키가 `FACT_KEYS`(`app/memory/types.py` 356~366행, 9종) 안의 `hobby` 여야 생성기 문장이 `unknown_basis` 로 거부되지 않는다는 구현자 관찰은 `-1527-u9-be-first-failure-repro.txt` 66~67행(`reason: unknown_basis`, `assert [] == ['주기 실행 줄']`)에서 재현돼 있다 — 재현임을 머리줄 `# 메모` 와 tests.md 가 모두 밝혔다.

## 3. 끝에서 끝 테스트의 `briefing_run` 혼입 문구 — R-U9b-2

`run.py` 308~317행 `run_output` 의 키는 `trigger·now·window·lead_hours·schedule_id_arg·selected·skipped·briefed·errors` 다 — **최상위 `schedule_id`·`person_id` 가 없다.** 그래서 실제 `briefing_run` 행은 `output->>'schedule_id'` 조인에 걸리지 않아 step 필터를 지워도 섞이지 않는다. `test_10행` docstring·주석(217~219행 "실제 run 행(실행마다 compose 뒤에 남는다) + 직접 넣은 error 행")과 tests.md e2e 10행 "실제 `briefing_run` 행 3개도 같은 `tool_name` 으로 섞여 있음" 은 글자 그대로는 참이지만, 그 행이 **혼입 검출의 재료는 아니다**. 구현자 M6(step 필터 제거)이 `test_10행` 에서 검출된 것은 직접 넣은 `briefing_error` 행(output 에 `schedule_id`·`person_id` 있음) 때문이다. 01-plan 10행의 "`briefing_run` 행을 `output` 에 같은 `schedule_id`·`person_id` 를 넣어 추가" 는 U3 단위 `test_run_과_error_행은_섞이지_않는다`(직접 삽입)가 맡는다 — 판정표 충족에는 문제 없고 **문구 정정만** 필요하다.

## 4. 변이 시험 (`evidence/20261015-1627-verifier-u9b-mutation.txt`, 사본 `/tmp/rel-u9b-verifier`, 저장소 무수정)

| ID | 변이 | 결과 | 비고 |
|---|---|---|---|
| M1(재현) | `routes.py` `now=now` 제거 | **6 failed, 2 passed** | 구현자와 동일(실패 6건 이름 일치) |
| M2(재현) | `read.py` 방어 조건 제거 | **1 failed** `test_조작된_trace_…` | 동일 |
| M3(재현) | `PushSubscription` 제거 | **1 failed** `assert 8 == 9` | 동일 |
| M5(재현) | `/briefings/run` `trigger="scheduler"` | **1 failed** `test_9행_…` | 동일 |
| M8(재현) | 목록 쿼리 `Person.user_id` 제거(e2e+단위) | **2 failed** `test_10행_…`·`test_다른_사용자_일정은_제외` | 구현자는 e2e 만 돌려 1 failed — 단위까지 포함하면 2 |
| **V1-e2e** | 최근 1행 정렬 1차 키 `created_at.desc()` → `asc()` | e2e 2건만: **2 passed(생존)** | 같은 트랜잭션이라 두 compose 행의 `created_at` 동률(PostgreSQL `now()`) — e2e 는 `id` 2차 키만 본다 |
| V1-all | 같은 변이, 64건 | **1 failed** `test_일정마다_최신_1행만` | U3 단위가 잡는다 — 공백 아님 |
| **V2** | 조인을 `.join(Person, Person.id == Schedule.person_id)` 만으로(trace 의 `person_id` 무시) | **64 passed(생존)** | **R-U9b-1** — R-U3-2 테스트가 "남의 일정 + 내 인물" 한 방향만 시험. "내 일정 + 남의/없는 인물 id" 조작 trace 는 현재 코드가 제외하지만 V2 는 포함하는데 어떤 테스트도 가르지 못한다. 사용자 격리(`Schedule → Person.user_id`)는 V2 에서도 유지되므로 보안 결함은 아니고, 01-plan 94행 "`output->>'person_id'` 로 `persons.user_id` 조인" 이 지켜지는지를 테스트가 고정하지 못한다는 뜻 |
| **V3-e2e** | `tool_name == 'briefing'` 필터 제거 | e2e 2건만: **2 passed(생존)** | e2e 데이터에 다른 `tool_name` 의 compose 행이 없다 |
| V3-all | 같은 변이, 64건 | **1 failed** `test_다른_tool_name_의_compose_step_은_제외` | U3 단위가 잡는다 — 공백 아님 |

10회 전부 끝에 `[원복 확인: 바이트 일치=True]`. 구현자 증거 `-1523-u9-be-mutation.txt`(2208행)는 변이마다 pytest 출력 전체 + `[원복 확인: 내용 일치=True]` 가 있어 FIX-033 (c) 충족, M4e 1차(`2 failed` — unique 위반) 무효 표시도 있다(813~1485행, 재실행 2136~2208행).

## 5. tests.md

- **행 수**: `grep -E '^\| test_api'` 64 = `pytest --collect-only -q` 64, `diff` 0 → "64:64 이름 일치"(내 재실행). 전체 테스트 행 203(`::` 포함) = 135 + 4 + 64.
- **열 수**: `|` 로 자른 필드 수 분포 — 테스트 행 203개 전부 **6파이프(5열)**. 6 이 아닌 행 65개는 전부 요약표(총계 3열·변이 ID 4열·실패 이력 정의 2열·M 표 4열)라 정상.
- **실패 이력 집계 재계산**: 실제 실패 5 · 검출 실패 → 보강 16 · 보류·재작업 4 · 동작 틈 → 보강 1 · 기록 없음 177 = 203 — 파일 안 "세는 법" 명령 그대로 내가 실행해 일치. 5종 어느 것도 아닌 테스트 행 0.
- **출처 표본 대조(줄 번호까지)**: U1 `review-u1-read-persons.md` 4행(1차 보류·`max→min` 7 passed) ✓ · `03-log.md` 28행 ✓ · U2 쓰기 0 → `review-u3` 105행(R-U3-5 ①) ✓ · proxy 4행 → `review-u4-skeleton.md` 99행(V1 20 passed)·125행(R-U4-3) ✓, `03-log.md` 69·76행 ✓ · E2E card → `review-u9a-e2e.md` 5행 ✓ · chat 칩 → `review-u5-chat.md` 107행 ✓ · briefing → `review-u7-briefing.md` 95행 ✓ · push → `review-u8-pwa-push.md` 99행 ✓.
- **표본 행 내용 ↔ 코드**: `test_만료_경계_24시간` "23시간 59분 59초 전 / 정확히 24시간 / 25시간" = 117~119행 ✓ · `test_근거_상한` "25건 → 20" = `FACT_SOURCES_LIMIT+5`·`== 20` ✓ · persons `test_쓰기_0_trace_0` 설명 = diff 그대로 ✓ · e2e 2행 설명 = §2 와 일치 ✓.
- **분류 4종과 사용자 결정의 뜻**: 사용자 결정(03-log 170행)은 "어떤 테스트를 통과하고 실패한 건지" 다. 표는 "실제 실패"(빨간불)를 따로 두고 나머지 셋은 "테스트가 빨개진 것은 아니다" 를 정의표에 명시했다(tests.md "실패 이력 열 읽는 법"). 뜻을 넓혔지만 숨기지 않았고 재계산 가능하다 — 다만 **"실제 실패" 5 가 좁은 뜻의 답**이라는 점은 메인 세션이 사용자에게 한 줄로 알려 주는 것이 맞다(결정 사항 아님, 알림).
- **e2e 10행의 "기록 없음 — 첫 실행은 `pytest -x` 로 …"**: 9행에서 멈춰 결과가 남지 않았음을 적었고 재현은 참고용이라고 명시 — 정직하다.

## 6. `docs/reliability.md` 수치 대조 (출처 원문을 전부 열었다)

| 문서 수치 | 원문 | 판정 |
|---|---|---|
| 채점 132 = 골드 135 − ambiguous 3, 시나리오 40 | `reports/eval.md` 19·21행 | 일치 |
| 방식 5종 오병합·미검출·보류·f1 표 | `eval.md` 48~52행(`0/132`·`0/132`·`31/132 (23.5%)`·`0.897` / `exact_raw` `33/132`·`0.826` / `exact_norm` `4/132`·`20/132`·`6/132`·`0.854` / `embedding_only` `1/132`·`0.892` / `llm_single` `9/132`·`20/132`·`0.865`) | 일치 |
| 게이트 통과·지배 없음·D10 방향 | `eval.md` 72~78행 | 일치 |
| `T_merge` 0.5 에서 4/132 (3.0%), 0.8 이상 0/132 | `eval.md` 112행 | 일치 |
| 1차 오병합 1/132 (0.76%)·미검출 1/132·보류 79/132 (59.8%)·f1 0.566·`embedding_only` 지배 | `failure_cases.md` 28·34행(§0 은 0.8% 반올림), §13.6 5~6행 `1 / 132 = 0.76%` | 일치(0.76% 는 §13.6 표기) |
| `rule_checked`=0 100/141 · 79 중 52 | `failure_cases.md` 205·183·336행 | 일치 |
| 감점 병합 14·0/14·전부 `relaxed_pass` · 보수 강등 5건 전부 정답 | §13.4 593·613행·29·38행 | 일치 |
| `s_llm` 상이 60/136 · `sc-015`·`sc-007` "안전한 쪽으로 옮겨짐" · 오병합 기회 증가 | §13.7 4~6행 | 일치 |
| `pass: false → true`, 1→0, 1→0, 79→31 | §13.6 9·15행 | 일치 |
| 98/101 (97.0%)·2/5 (40.0%)·1/1·101/107 (94.4%)·보정표 46.5% (47/101) | §4g 253~258행 | 일치 |
| 공급자 `openai`/`gpt-4o-mini-2024-07-18`, Gemini·Anthropic 실호출 0 · `reason` 원문 없음 | §10 4행·69행 | 일치 |
| P6-memory 1622 · P6-briefing 1721·34행·실 OpenAI · P7 실수신(fcm·`6428180`) · 패턴 문장 인계 | `CURRENT.md` 24·20·17행 | 일치 |
| 135·4·64·203·1946·CI 38558603645·38688947610 | tests.md·`-1524-full-regression.txt`·03-log 157행·HANDOFF 8행 | 일치 |
| `sw.test` 16·`push.test` 21 · 03-log 67·69·171·172·167·182행 · 01-plan 68행 · HANDOFF `[미확인]` Windows · `P4b/04-review.md` 존재 · 인용 테스트 파일 17개 + `test_push_*.py` 6개 존재 | 각 파일 | 일치 |

새로 만든 수치·출처 없는 수치: **0**. 미검증·미달을 숨긴 곳: 없음(§A 1차 미달·§E 옛 테스트 생존·§J 생존 변이·§2 미검증 11항·§4 한계). 진행 중 프로젝트를 완료처럼 쓴 곳: 없음("초안"·"아직 안 함"·"P9/P10" 표기).

**표현 정정 1곳(R-U9b-4)**: §D "서버 환경변수 `APP_USER_ID` 한 사람을 전제로 하며(01-plan 결정 D)" — 01-plan 41행에서 단일 사용자 전제의 근거는 **"P5-loop 결정 I"** 이고, **결정 D** 는 "다중 사용자 격리 부채(F-fbaaae)는 P9-infra 전 과제" 다. 괄호를 "(01-plan 41행 — 단일 사용자 전제는 P5-loop 결정 I, 격리 부채는 결정 D 로 P9 전 과제)" 로 바꾸면 정확하다. 또 상단 "verifier 의 수치 대조 전이다" 와 §4 첫 항목은 이 리뷰로 대조가 끝났으므로 커밋 때 메인 세션이 "verifier 대조 완료(`review-u9b-backend.md` §6)" 로 바꿀지 정한다.

## 7. 작업 경로 이상(worktree → `git apply`) — 훅 미검사 diff 전수 확인

- `git status`: 수정 12 · 신규 16(증거 14 + `reliability.md` + e2e 테스트). 전부 U9b 몫 또는 기록 파일. `web/` 0.
- `.claude/settings.json`: `worktree.bgIsolation: "none"` 3줄 추가만(diff `+` 3줄, 다른 키 변화 0) — 사용자 직접 수정, U9b 범위 밖(기록만).
- `HANDOFF.md` 1행·`journal.md` 자동 2줄(COMMIT/PUSH-dev2 07ec09a)·`03-log.md` +10행(U9b pending 항목, Refs 있음)·`registry.md` 7행 갱신 + 신규 3행(`U9b(pending)` — 커밋 뒤 해시로).
- 비밀 문자열: `git diff` 와 신규 파일 전체에 `sk-`·`api_key`·`AKIA…`·`BEGIN PRIVATE`·`password`·`token=` grep → 0.
- 범위 밖 제품 코드: 판정표 11행 diff 명령 빈 출력(§1).
- 증거 머리줄 `cwd: /private/tmp/rel-u9b`·`HEAD: 07ec09a` — 사본에서 만든 증거임이 파일 자체에 남아 있다. `-1524-u9-be-mypy-baseline-compare.txt` 명령이 메인 체크아웃에서 `mypy` 를 실행했으나 읽기 전용(`.mypy_cache` 만) — 기록.
- `-1524-u9-be-lint.txt` 는 `exit 1` 인데 ruff "All checks passed!" 뒤 mypy 기준선 34건 때문 — 기준선 비교 파일이 34 = 34 를 보인다(R-U9b-5 기록).

## 8. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U9b-1 · R-U3-2 테스트 단방향(V2 생존).** `test_api_read_briefings.py::test_조작된_trace_…` 에 "내 일정 id + 남의(또는 존재하지 않는) 인물 id" 로 조작한 trace 1건을 더해 `_ids(r) == [s_mine.id]` 가 그 행을 제외함을 단언하면 V2 가 검출된다. 현재 코드는 이미 제외한다(코드 수정 0, 테스트 1단언). 다음 백엔드 코드 단위 또는 이 커밋에 포함 — 사용자 결정.
- **R-U9b-2 · `briefing_run` 혼입 문구.** `test_api_read_briefings_e2e.py` 217~219행 주석과 tests.md e2e 10행 "실제 `briefing_run` 행 3개도 같은 `tool_name` 으로 섞여 있음" 을 "run 행은 실제 실행이 남긴 것(output 에 최상위 `schedule_id` 없음 — `run.py` 308~317행) · 혼입 검출 재료는 직접 넣은 `briefing_error` 행과 U3 단위 `test_run_과_error_행은_섞이지_않는다`" 로 정정(§3).
- **R-U9b-3 · 기록용 — e2e 2건만의 한계.** V1-e2e·V3-e2e 생존(같은 트랜잭션 `created_at` 동률·다른 `tool_name` 데이터 없음)은 U3 단위가 메우므로 공백은 아니지만, tests.md e2e 절 머리글에 "정렬 1차 키·`tool_name` 필터는 단위 테스트가 고정한다" 한 줄을 적어 두면 e2e 만 읽는 사람이 과신하지 않는다.
- **R-U9b-4 · `reliability.md` §D 결정 귀속 1곳 정정 + 상단/§4 "대조 전" 문장 갱신 여부**(§6).
- **R-U9b-5 · 기록.** ① lint 증거 `exit 1` 은 mypy 기준선(34 = 34) ② 7행 증거 `-k '쓰기_0 or 헬퍼_자체'` 는 4파일 62 items 중 7 선택(e2e 미포함 — e2e 에는 쓰기 0 단언이 없고 9행 쓰기 0 은 U3 단위가 맡음) ③ M8 을 단위까지 돌리면 2 failed(구현자 1 failed 는 e2e 만) ④ tests.md "실제 실패" 5 가 사용자 결정의 좁은 뜻("통과·실패")에 대한 답이고 나머지 3종은 확장 해석임을 사용자에게 한 줄 알림.

## 9. 판정 근거 요약

- 01-plan 100행 U9 backend 몫(백엔드 행·전체 회귀)·03-log 183행(R-U3-1·2·5·tests.md 백엔드 절·실패 이력 열·`reliability.md` 초안) 전부 산출물 있음.
- 판정표 1~11행: 내 직접 실행 64 passed(§2·증거 9~84행) + 11행 3명령 기대값(§1). 28행 백엔드: `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs` → **1946 passed, skip 0**, exit 0(백그라운드 실행 출력).
- 테스트가 "항상 통과" 가 아님: 구현자 13종 전부 검출(증거 전체 출력·원복 확인), 내 재현 5종 일치, 고유 3종 중 2종(64건 기준) 검출·**V2 생존 → R-U9b-1**.
- 9·10행 끝에서 끝: trace 는 `POST /briefings/run`·`run_briefings(trigger="scheduler")`·`run_briefings(user_id="other")` 실제 실행이 만들고 직접 삽입은 `briefing_error` 뿐(§2). 사실 키 `hobby` 선택 이유와 첫 실패 재현이 증거에 있음.
- tests.md 64:64·5열 203행·집계 재계산 일치·출처 줄 번호 표본 전부 일치(§5). `reliability.md` 수치 전부 원문 일치, 새 수치 0, 미검증 숨김 0(§6).
- 훅 미검사 경로 diff: 범위 밖 변경 0·비밀 0·`settings.json` 3줄만(§7).

---

## 재확인(재작업 1차) — 2026-10-15 19:38

검토자: verifier (fable)
결과: **통과 — R-U9b-1·2·3·4 닫힘, R-U9b-5 기록용(열림 아님). 새 [필수] 0 · 새 [권고] 0 · 기록 2.** `app/` diff 는 1차 리뷰와 바이트 단위로 같고(§1 두 곳), 변경은 테스트 1건의 단언·주석·기록 문서뿐이다.
증거(내가 만든 것): `evidence/20261015-1938-verifier-u9b-rework1-recheck.txt` — 사본 `/tmp/rel-u9b-verifier-rw1` 에서 원본·V2·원복, 저장소에서 전체 회귀, tests.md 집계 재계산, 비밀 grep.

### 소견별

| 소견 | 재작업 내용(내가 읽은 것) | 직접 확인 | 판정 |
|---|---|---|---|
| **R-U9b-1** V2 생존 | `tests/test_api_read_briefings.py` 238~254행: `s_forged`(내 인물의 일정) + `_trace(db_session, s_forged, other, …)`(남의 인물 id) 추가, 단언 `_ids(r) == [s_mine.id]`·`"조작된 trace" not in r.text`. 파일 테스트 수 24 불변 | 사본 원본 `1 passed, 23 deselected` / `24 passed`. V2(조인을 `Person.id == Schedule.person_id` 만으로, 사본 325행 diff 1줄) → `-k 조작된_trace` **1 failed** `assert [9497, 9498] == [9497]`, 5파일 **1 failed, 63 passed**(실패는 그 테스트 하나). 원복 `cmp` 바이트 일치. 구현자 증거 `-1927-u9b-rework1-v2-mutation.txt` 와 같은 결과(id 값만 다름 — 시퀀스). 구현자 증거의 echo 라벨 "25 파일" 은 수집 줄이 `24 items` 라 오타임이 파일 안에서 확인된다 | **닫힘** |
| **R-U9b-2** `briefing_run` 혼입 문구 | e2e 193~196행 주석 "실제 run 행은 … output 에 최상위 schedule_id 가 없다(run.py 308~317행) … 혼입 검출 재료가 아니다. run 행 혼입은 U3 단위 test_run_과_error_행은_섞이지_않는다 가 직접 삽입으로 맡는다", 211행 `run_rows` 단언 옆 주석, tests.md 417행 e2e 10행 같은 취지 | `app/briefing/run.py` 308~317행 `run_output` 키 = `trigger·now·window·lead_hours·schedule_id_arg·selected·skipped·briefed·errors` — 최상위 `schedule_id`·`person_id` 없음(참). `test_run_과_error_행은_섞이지_않는다` 는 `test_api_read_briefings.py` 196행에 실존. 1차 리뷰 §3·111행 문구와 일치, 새 사실 오류 없음 | **닫힘** |
| **R-U9b-3** e2e 2건만의 한계 | tests.md 412행 "**한계(R-U9b-3):** 정렬 1차 키(`created_at`)와 `tool_name` 필터는 이 2건이 고정하지 않는다(… V1-e2e·V3-e2e 생존). 그 둘은 U3 단위 테스트(`test_일정마다_최신_1행만`·`test_다른_tool_name_의_compose_step_은_제외`)가 고정한다" | 두 단위 테스트 이름이 `test_api_read_briefings.py` 172·207행에 실존. 1차 §4 V1-all·V3-all 결과(각 1 failed, 그 테스트)와 일치 | **닫힘** |
| **R-U9b-4** `reliability.md` §D 귀속·"대조 전" | 101행 "(01-plan 41행 — 단일 사용자 전제는 P5-loop 결정 I, 격리 부채는 결정 D 로 P9 전 과제)" · 3행·235행 "verifier 대조 완료(`review-u9b-backend.md` §6)" | 01-plan 41행 원문 "단일 사용자 전제(`app_user_id()`, P5-loop 결정 I). 다중 사용자 격리 부채(F-fbaaae)는 … P9-infra 전 과제다(결정 D)" 와 귀속 일치(1차 92행 제안 문구 그대로). "대조 전" 잔존 0(grep). 이 문서가 "대조 완료" 라 적은 것은 내 §6 판정을 가리키므로 사실 | **닫힘** |
| **R-U9b-5** 기록 ①~④ | 재작업 범위 아님(사용자 결정은 1·2·4, 구현자가 3 포함) | 변경 요구 없음. ④ "실제 실패 5 가 좁은 뜻의 답" 알림은 메인 세션 몫 그대로 | 기록용(열림 아님) |

### 집계·동기

- tests.md "세는 법" 명령 그대로 재실행: 실제 실패 **5** · 검출 실패 → 보강 **17** · 보류·재작업 **4** · 동작 틈 → 보강 **1** · 기록 없음 **176** = **203**. `::` 포함 행 218 = 테스트 행 203 + 표 머리행 15 — 테스트 행 203 전부 5열, 미분류 0. 16→17 로 옮긴 행은 391행 `test_조작된_trace_…` 하나이고 그 출처가 "`review-u9b-backend.md` 55행(V2 행) · `evidence/*-u9b-rework1-v2-mutation.txt`" 로 실존 줄을 가리킨다.
- `docs/reliability.md` 161행 "17행"·200행 "5 · 17 · 4 · 1 · 176 (합계 203)"·229행 "5/17/4/1/176" · `registry.md` 258행 "5/17/4/1/176 (재작업 1차: 조작된 trace 단언 추가)" — 전부 일치. 옛 수치 16·177 잔존 0.
- 03-log 193행 재작업 1차 불릿: 내용이 diff 와 일치(제품 코드 무변경·24 불변·V2 결과·R-2/3/4 위치·집계 이동). Refs 는 커밋 뒤 해시로.

### 범위·비밀·회귀

- `git diff -- app/`: `read.py` +4/−1 · `routes.py` +6/−2 — 1차 리뷰 §1 그대로, 재작업이 제품 코드를 건드리지 않았다. `git status`: 수정 12(1차와 같은 집합) · 미추적 21(1차 16 + 내 1차 증거 1 + 재작업 증거 3 + 이 리뷰 1). `web/` 0. `.claude/settings.json` 3줄·HANDOFF 1행·journal 2행은 1차 §7 과 동일(재작업에서 변화 없음).
- 비밀 문자열: `git diff` + 미추적(evidence 제외) 전체 grep → 실제 적중 0.
- 전체 회귀(저장소, 내 실행): `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs -p no:cacheprovider` → **1946 passed, 1 warning in 25.13s**, skip 줄 없음. 구현자 `-1927-u9b-rework1-full-regression.txt` 와 같은 수.

### 기록(소견 아님)

- K1. 구현자 V2 증거의 echo 라벨 "briefings 25 파일 전체" 는 "24" 오타 — 같은 파일 15행 `collected 24 items` 와 84행 `1 failed, 23 passed` 가 24 를 보이므로 증거 효력에는 영향 없다. 고치지 않아도 된다(증거 파일은 사후 수정하지 않는 것이 원칙).
- K2. 내 전체 회귀 실행에서 셸이 zsh 라 `PIPESTATUS` 가 비어 exit 코드를 못 찍었다. 요약 줄에 `failed`·`error` 가 없고 1946 = 기대값이므로 통과로 본다(구현자 증거는 `# exit: 0`).

커밋·승인은 메인 세션·사용자 몫이다. 이 재확인으로 U9b 커밋 전 조건(사용자 결정 R-U9b-1·2·4)은 충족됐다.
