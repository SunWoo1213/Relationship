# P5b-query-turn U6 API 끝에서 끝 — mypy 새 오류 1건 수정(`assert` 1줄) + `tests/test_api_chat_query.py`(8) + R-U5-1 테스트·R-U5-2 docstring + 판정 표 전 행 evidence + registry 해시·tests.md·`docs/RUNNING.md` — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 3(R-U6-1 U5 구현자 스크래치패드 사본 `p5b-u5/repo` 에 비밀 파일이 아직 남아 있음(R-U5-3 미해결, 이름만 확인·내용 미독·저장소 밖) / R-U6-2 `docs/RUNNING.md` 132행(기존 줄)의 기록 턴 예시가 `stored` 를 목록 `[...]` 로 적는데 실제 `StoredOut` 은 정수 3개 — U6 가 바로 아래 더한 조회 예시는 정수로 맞게 적어 인접한 두 예시가 서로 다르다 / R-U6-3 판정 표 R-4 ⑤ 의 `\b` 는 BSD `grep -E` 에서는 되지만 `git grep -E` 는 지원하지 않아 기준 대조는 `git grep -P` 또는 `git show … | grep -E` 로 해야 한다 — 04-review 메모). 코드 결함은 찾지 못했다. `git diff HEAD -- app` 은 `app/agent/loop.py` 1파일 `+15/−1` 이고 코드 줄은 `assert applied.pending_question_id is not None` 1줄뿐(나머지 14줄은 docstring — 모듈 docstring 1줄 교체 + 2줄, `resume_turn` docstring "조회 재개 분기" 절 11줄). 내 수치: API 8 passed · 전체 2122 passed(2114 + 8)·skip 0 · ruff 통과 · `tools_check` 7/7 · `scripts/mypy_check.py --run` `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 · 판정 표 D-1~D-7·A-1~A-5·R-1~R-8 전 행 기대와 일치 · HTTP 계약 값 직접 확인 80 PASS / 0 FAIL · 변이 12 적용 / 12 검출 / 0 생존(계획 118행 2건 + `assert` 제거 → mypy 새 오류 재발 + 내 변이 9) · 범위 밖 diff 0 · 기존 테스트 파일 수정 0.
대상: 작업 트리(HEAD `49c1c67` = U5, 무변경 기준 `8a8767b`) — `git diff --numstat HEAD -- app` = `15 1 app/agent/loop.py`(1파일) · 신규 `tests/test_api_chat_query.py`(440줄, 수집 8) · `docs/wiki/registry.md`(P5b 해시 `pending` → `1dccb95`/`06b7bb5`/`a002706`/`18219ba`/`49c1c67` 치환, 새 테스트 행 1(`pending`), `loop.py` 행 비고 "P5b U6(해시 pending)") · `docs/wiki/packages/P5b-query-turn/tests.md`(U6 절 8행 + 머리글 합계 164·총계 2122) · `docs/RUNNING.md`(+8줄 조회 발화 예시) · `docs/wiki/packages/P5b-query-turn/01-plan.md`(메인 세션 수정: 공통 판정 84행 `u<n>-mypy` 추가 · D-3 ④ `-k merge_answers_from_card` · R-4 ⑤ `PendingQuestion\b`) · 구현 증거 `evidence/20261102-14{49,51,52,53,55,59}-u6-*.txt`(48). `HANDOFF.md`·`journal.md`·`03-log.md` diff 는 리뷰 대상 아님(03-log 에 U6 항목이 아직 없고 U5 항목 끝에 커밋 해시·CI failure 한 줄만 추가된 사실을 §7 에 적는다). 구현자의 자기 평가(`tests.md` 의 "U6-M1~M5 검출"·구현 변이 증거)는 판정 근거로 쓰지 않았다 — 아래 수치는 전부 내 실행이다.
근거 문서: `01-plan.md` 115~118행(U6 계약·변이 2) · 84행(공통 판정, `u<n>-mypy` 포함) · 86~87행(구현 제약 (1)~(5)) · 140~168행(판정 표) · 결정 K(304~314행 — `answerer=None` 지연 해소, HTTP 는 monkeypatch, R-1 모듈 속성 호출) · 결정 E-5(문구) · 결정 J(두 번째 답 409 는 기존 규약) · `D16-query-turn.md` "코드에서 지켜야 할 것" 1~7 · `verification.md` · `security.md` · `.github/workflows/*.yml` 101~111행(`python scripts/mypy_check.py --run`) · `scripts/mypy_check.py`(`--run` 은 `mypy app --ignore-missing-imports` 를 subprocess 로 돌려 `scripts/mypy_baseline.txt` 와 다중집합 비교) · `tests/test_api_chat.py` 83~118행(픽스처 관례) · 위임문(U4·U5 CI failure 원인 `loop.py:1331 int | None`, 사용자 결정 2026-11-02 D-3d·R-4 ⑤·변이 사본 비밀 파일 금지).
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`, 전부 `save_evidence.py`): `20261102-1500-verifier-u6-{api-tests,lint,tools-check,mypy}.txt` · `-1501-verifier-u6-{full-regression,mypy-check}.txt` · 판정 표 행별 `-150{2,3,4,5}-verifier-u6-<행id>.txt`(§2 표에 유효 파일을 행마다 적는다 — 1회차 1502~1503 의 일부는 내 래퍼의 인용 손실로 깨졌고(exit 2/4/127/128) 1503~1505 재실행이 유효하다) · `-1508-verifier-u6-contract-values.txt`(80 PASS / 0 FAIL) · `-1509-verifier-u6-mutation.txt`(변이 12) · `-1510-verifier-u6-grep-constraints.txt`. 스크립트는 스크래치패드 `verifier-u6/`(`rows.sh`·`rows2.sh`·`contract.py`·`mutate.py`). 변이 사본 `verifier-u6/repo` 최상위 = `alembic`·`alembic.ini`·`app`·`pyproject.toml`·`scripts`·`tests`(+ `.mypy_cache`) — 비밀 파일 없음(mutation 증거 2행·끝 줄). 비밀 파일은 읽지도 복사하지도 않았다.

---

## 1. 본 것 — 01-plan U6 줄·결정 K·D16·위임문 계약 대조

| 계약(01-plan·결정·위임문 글자 그대로) | 코드 위치(작업 트리 행) | 직접 확인(contract-values) | 테스트 | 판정 |
|---|---|---|---|---|
| 위임문: CI failure 원인 `loop.py:1331 Argument "question_id" to "PendingQuestionOut" has incompatible type "int \| None"; expected "int"` 을 이 단위가 좁힌다 — **이 커밋이 CI 를 초록으로** | `app/agent/loop.py` 1332행 `assert applied.pending_question_id is not None`(`_run_query_turn` identity 경로, `apply_resolution` 직후·`PendingQuestionOut(question_id=…)` 직전). 같은 좁히기 관례가 기존 `_pending_question_from_resolve` 1076행 `assert last.pending_question_id is not None` 에 이미 있다. `apply_resolution` identity 경로(`app/er/pipeline.py` 476~486행)는 `ask_user()` 반환의 `question.question_id` 를 넣으므로 실행 시 None 이 될 수 없다 — 타입 좁히기뿐, 동작 변화 0 | mypy: `.venv/bin/mypy app` 39건/15파일 = 기준선 38 + `app/push/sender.py [import-untyped]`(pywebpush 스텁 없음) 1 — 이 1건은 `mypy_check.py --run` 이 붙이는 `--ignore-missing-imports` 가 거르는 항목이고 파일별 건수는 그 1건 외 기준선과 동일(`loop.py` 2 = 기준선 2, 1331행 오류 없음). `.venv/bin/python scripts/mypy_check.py --run` → `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 | 변이 P3(`assert` 제거) → 사본에서 `mypy_check.py --run` 이 `[new] … loop.py: [arg-type] … "int \| None"; expected "int"` exit 1 — 같은 오류가 그대로 재발 | 일치 |
| U6: `tests/test_api_chat_query.py`(`app_and_client` 와 같은 방식 — 새 파일에 같은 픽스처를 둔다, 기존 파일 import 는 하지 않는다) | 51~58행 `app_and_client`(`create_app()` + `get_session`/`get_embedder` 오버라이드) · 61~72행 `_make_person`/`_add_alias` 는 `tests/test_api_chat.py` 83~118행과 같은 문장. `grep -E '^(from\|import) .*test_api_chat'` 0 | — | — | 일치 |
| `POST /chat` 조회 발화 1건 → 200·`reply` 비어 있지 않음·`stored == {0,0,0}`·`pending_question is None`·요청 전후 행 수 불변·`agent_traces` 에 `loop_extract`(output `intent == "query"`)·`loop_gate`(새 사유)·`er_resolve`·`loop_query`·`loop_turn` 각 1 | 테스트 (1) 179~217행 | (i) 200 · reply == `ANSWER + "\n" + QUERY_MORE_HINT` · `stored == {persons 0, events 0, schedules 0}` · `pending_question None`·`stop_reason None` · 7개 테이블 `{persons 1, person_aliases 1, events 8, schedules 2, person_facts 3, fact_sources 0, pending_questions 0}` 전후 동일 · 기록 툴 `tool_call` 0 · 5 step 각 1행, `loop_record`/`loop_resolve_done` 0 · `loop_extract.output.intent == "query"` · `loop_gate.rejected == [{search_person, 0, not_callable_by_llm}]` · `loop_query.person_id` == 시드 · `evidence_counts == {facts 3, patterns 0, timeline 5, schedules 2}` · `loop_query.reply == loop_turn.reply == 응답 reply` · `er_resolve.decision.applied False` · 원문(`raw_utterance`) 이 reply·trace 에 0 | (1) | 일치. P1·P2·V2·V8 검출 |
| identity 조회 → `POST /answers/{id}` 1요청으로 답 → 재개 응답 `reply` 에 카드 근거·저장 0·두 번째 답 409(기존 결정 J 그대로) | (2) 235~276행 · (2b) 279~291행 | (ii) 되묻기 턴 `stop_reason "ask_user"`·`pending_question.kind identity`·`stored 0`·answerer 0회·`pending_questions` 1행 → 후보 답 → 200 · reply == ANSWER + MORE · `stored 0`·`pending_question None`·`stop_reason None` · `person_aliases` 2 → 2 · 7개 테이블 불변 · 기록 툴 0 · `loop_query` 2행 `["ask","llm"]`·재개 `person_id == 김민수 ≠ 김민호` · answerer 가 받은 질문 == 원 발화 · `loop_resume 1 · loop_resolve_done 0 · loop_record 0` → 같은 id 재제출 **409** `{"detail":{"code":"already_answered",…}}` · 409 뒤 answerer 여전히 1회·행 수 불변 | (2)(2b) | 일치. V1·V3·V7·V9 검출 |
| new_person 조회 → `pending_question is None`·`pending_questions` 행 0 | (3) 299~320행 | (iii) `pending_question None` · `pending_questions` 0 · reply == `no_record_reply(["박선우"])` == `"박선우"에 대한 기록이 없어요.` · `stored 0`·행 수 불변 · answerer 0 · `ask_user` tool_call 0 · `persons` 0(인물 생성 없음) | (3) | 일치. V5 검출 |
| 혼합(조회 의도 + `add_event`) → `events` +0·`loop_gate.output.rejected[].reason` 에 `query_turn_no_write` / 기록 턴 대조군 `events` +1 | (4) 328~350행 · (5) 358~380행 | (iv) `events` +0·7개 테이블 불변·`rejected` 에 `{index 1, add_event, query_turn_no_write}` 정확히 · (v) 같은 DB 에서 `intents` 없는 제안 → `stored.events 1`·`events` +1·`loop_query 0`·`loop_record 1`·조회 answerer 스파이 0회 | (4)(5) | 일치. V6 검출 |
| R-U5-1: 조회 identity 질문 뒤 후보 인물 삭제 → `POST /answers` 후보 답 → `reply == no_record_reply([mention])`·저장 0 | (6) 388~419행 — `DELETE FROM persons` 뒤 실제 `app.api.read.get_person_card` 가 `PersonNotFound` 를 내는 것을 `pytest.raises` 로 먼저 보이고 재개 | (vi) 200 · reply == `"팀장"에 대한 기록이 없어요.` · `stored 0`·행 수 불변 · answerer 0 · `loop_query` `["ask","no_record"]` · 재개 `person_id None` · 후속 질문 없음 | (6) | 일치. **V4(U5 생존 변이 V7 과 같은 변이) 가 (6) 으로 검출 — R-U5-1 닫힘** |
| 헤더 없이 `session_id` 발급 | (7) 427~440행 | (vii) 200 · `session_id` uuid4(`f7bc721b-…`) · 그 세션 `loop_query` 1행 · `stored 0` | (7) | 일치. P1·P2·V2 검출 |
| 결정 K (a)+R-1: answerer 주입은 라우트 무수정 + `monkeypatch.setattr("app.agent.respond.answerer_from_env", …)` | `loop.py` `_query_finish` 1405~1407행 `from app.agent import respond as _respond` / `_respond.answerer_from_env()` 모듈 속성 호출(U4 그대로, 이 단위 변경 없음) · 테스트 161행 monkeypatch · `git diff --stat 8a8767b -- app/api` 빈 출력(R-2 ②) | (viii) 패치 A → reply A 의 답, 패치 B → reply B 의 답(매 턴 모듈 속성 해소) · 각 answerer 1회 · 스파이로 바꾸면 라우트 → 루프 호출 1회 · 패치 해제 후 원함수 복원 · identity 되묻기 턴은 `answerer_from_env` 0회(근거 없음) | 전부 | 일치. V2(import 시점 바인딩) 검출 5건 |
| R-U5-2: `resume_turn` docstring 이 조회 재개 분기를 설명 | 1763~1773행 "## 조회 재개 분기 (P5b-query-turn U5, CR-004·D16)" 11줄 — `kind == "identity"` + `resume.intent == "query"` → `_resume_query_turn`, 후보 안/밖 처리, 별칭 누적 0·`update_person` 없음, trace 3행, 옛 context 기본값 `"record"`. 모듈 docstring 185~187행 2줄 추가 | 문장이 §1 (ii)(vi)·U5 리뷰 §1 과 일치(`loop_resume`·`loop_query`·`loop_turn`, `loop_resolve_done`/`loop_record` 없음) | — | 일치 |
| 원칙9 — trace 에 의도·해석·근거 건수·답·토큰 | (i)(ii) `loop_query.output` 10키·`evidence_counts`·`reply` | — | (1)(2) | 일치 |
| 원칙1·2·4·7 — 루프는 band 만, 확신도 어휘 0, 조회 답은 카드 사실 재진술/"기록 없어요" 뿐 | 추가 15줄에 확신도 영어 어휘 0(grep-constraints (2)) · R-8 18 passed | (iii)(vi) 거절·삭제 답에 "새로 기억할까요" 류 후속 질문 0 | R-8 | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_api_chat_query.py -v` | 8 passed in 0.64s, exit 0 — (1)~(7)+(2b) 전부 PASSED | `…-1500-verifier-u6-api-tests.txt` |
| `… pytest tests/ -q -rs` | 2122 passed, 1 warning in 24.29s, exit 0 — skip 줄 0. 2114(U5) + 8 | `…-1501-verifier-u6-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-1500-verifier-u6-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-1500-verifier-u6-tools-check.txt` |
| `.venv/bin/mypy app` | `Found 39 errors in 15 files` exit 1 — 기준선 38 + `app/push/sender.py: error: Skipping analyzing "pywebpush" … [import-untyped]` 1. 파일별 건수 `uniq -c` 대조: `sender.py` 1 외 전부 기준선과 같음(`loop.py` 2 = 2). 같은 출력을 `scripts/mypy_check.py` stdin 모드에 넣으면 `[new] … sender.py [import-untyped] (x1)` 1건만 — `--ignore-missing-imports` 가 거르는 종류 | `…-1500-verifier-u6-mypy.txt` |
| `.venv/bin/python scripts/mypy_check.py --run`(CI 와 같은 명령) | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 | `…-1501-verifier-u6-mypy-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` / `--name-only --diff-filter=M 8a8767b..HEAD -- tests/` | 둘 다 빈 출력 — 기존 테스트 파일 수정 0(작업 트리·HEAD) | `…-1503-verifier-u6-R-1.txt`·`-R-1-wt.txt` |
| 범위 밖 경로 diff(HEAD 기준: `app/api app/er app/tools app/briefing app/memory app/db app/main.py app/push app/agent/{respond,gate,propose,types,__init__}.py app/settings.py alembic web scripts pyproject.toml alembic.ini .github` / `8a8767b` 기준: `app/er app/tools app/api app/db app/briefing app/memory app/main.py app/push alembic web scripts .github pyproject.toml`) | 둘 다 빈 출력 | `…-1503-verifier-u6-R-2b.txt`·`-R-2b-wt.txt`(판정 표 경로), 나머지는 §0 서두 확인(직접 실행, 저장 안 함) |
| `git diff --numstat HEAD -- app` / `-` 줄 전수 / 코드 `+` 줄 | `15 1 app/agent/loop.py` 1파일 / `-` 1줄 = 모듈 docstring `이번에도 확신도 값을 읽지 않는다(\`band\` 만).`(같은 문장이 `+` 로 이어지며 2줄 추가) / docstring 아닌 `+` 줄 = `assert applied.pending_question_id is not None` 1줄 | `…-1510-verifier-u6-grep-constraints.txt` (6) |
| `grep -nE "^(from\|import) .*test_api_chat" tests/test_api_chat_query.py` | 0(출현 2곳은 docstring·주석 "같은 모양, 복사본") | 같은 파일 끝 |
| 계약 값 Python 80 항목((i)~(viii)) | 80 PASS / 0 FAIL, exit 0 | `…-1508-verifier-u6-contract-values.txt` |
| 변이 12건(사본 `verifier-u6/repo`, `tests/test_api_chat_query.py` 8 + P3 는 사본 `scripts/mypy_check.py --run`) | C0 8 passed·mypy `[ok] 38/38` → 12 적용 / 12 검출 / 0 생존. 끝에 `git status --short` 리뷰 전과 동일(제품 1·테스트 1·문서 7·증거), 사본 ↔ 저장소 `loop.py`·`questions.py`·`gate.py` SAME, 비밀 파일 없음 True | `…-1509-verifier-u6-mutation.txt` |
| 구현 제약 (1)~(5) — `git diff HEAD -- app` 추가 줄 15 | (1) `create_person(`/`update_person(` 0 · (2) 확신도 영어 어휘 0 · (3) `sleep`/`while True` 0 · (4) `PendingQuestion\b`/`flag_modified`/`.context =` 0 · (5) 키 패턴 0 / 신규 테스트 파일: 키 패턴 0, 실 공급자 import 0 | `…-1510-verifier-u6-grep-constraints.txt` |
| `--collect-only` 5파일 ↔ `tests.md` | 24·28·71·33·8 = 164 == 머리글 "164건"; U6 절 8행 이름 ↔ 수집 8 `SAME`; 머리글 "2122 passed, skip 0" == 내 전체 실행 | 직접 실행(§5) |

판정 표 전 행 재실행(01-plan 140~168행 명령 그대로; `-wt` 는 `..HEAD` 를 뺀 작업 트리 기준 추가 실행):

| 행 | 결과 | 기대와 | 유효 증거(`…-verifier-u6-`) |
|---|---|---|---|
| D-1 | ① `['intent', 'tool_calls']` / `['record', 'query']` / `True` ② 0줄(HEAD·작업 트리) ③ 24 passed | 일치 | `1503-D-1a` · `1502-D-1b`·`1502-D-1b-wt` · `1502-D-1c` |
| D-2 | 19 passed, 17 deselected | 일치(통과, 수집 > 0) | `1503-D-2` |
| D-3 | ① `resolve(` 1299행·`apply_resolution(` 1329행은 `_run_query_turn`(1276~1358) 의 identity 경로에만(merge 경로 1312행은 "apply_resolution() 을 부르지 않는다" 주석), `get_person_card` 1258·1261행 `_read_card` 지연 import 호출 ② `7/7 ok` ③ 빈 출력(HEAD·작업 트리) ④ 1 passed, 32 deselected(`test_a_merge_answers_from_card_and_writes_nothing`) | 일치 | `1503-D-3a` · `1502-D-3b` · `1502-D-3c`·`-wt` · `1502-D-3d` |
| D-4 | 4 passed, 37 deselected | 일치 | `1503-D-4` |
| D-5 | 3 passed, 38 deselected | 일치 | `1503-D-5`(append 절) |
| D-6 | ① 23 passed, 81 deselected ② `respond.py` import 줄 + `REASON_FORBIDDEN_EXPRESSION` 반환 줄 ③ 빈 출력(HEAD·작업 트리) | 일치 | `1503-D-6a`(append 절) · `1504-D-6b` · `1503-D-6c`·`-wt` |
| D-7 | 빈 출력(HEAD·작업 트리) | 일치 | `1503-D-7`·`-wt` |
| A-1 | 3 passed, 5 deselected(`stored_zero` 3건) | 일치 | `1503-A-1` |
| A-2 | `7/7 ok` | 일치 | `1503-A-2` |
| A-3 | 2 passed, 39 deselected | 일치 | `1503-A-3` |
| A-4 | 2122 passed, skip 0 | 일치(1958 + 164) | `1501-full-regression` |
| A-5 | `All checks passed!` | 일치 | `1503-A-5` |
| R-1 | 빈 출력(HEAD·작업 트리) | 일치 | `1503-R-1`·`-wt` |
| R-2 | ① `app/agent/__init__.py, gate.py, loop.py, propose.py, respond.py, types.py, app/settings.py` — 허용 7개 그대로(부분집합 성립). `__init__.py` 는 U1·U3 재export 로 기준 이후 **변경됨**(구현자 보고와 달리 "무변경" 이 아니다 — 다만 허용 집합 안) ② 빈 출력(HEAD·작업 트리) | 일치 | `1503-R-2a`·`-wt` · `1503-R-2b`·`-wt` |
| R-3 | `No new upgrade operations detected.` | 일치 | `1503-R-3` |
| R-4 ① | 1줄 `loop.py:1867 created = app_tools.create_person(` = 기준 `8a8767b` 1줄(1473행) | 일치 | `1504-R-4-1`·`1504-R-4-1-base`·`1503-R-4-1-added`(추가 줄 0) |
| R-4 ② | `.py` 5줄(`respond.py:18`·`loop.py:741/840/891/1837`) = 기준 5줄 → `SAME-as-base`(`__pycache__` 바이너리 매치 2줄 제외) | 일치 | `1504-R-4-2`·`1504-R-4-2-base`·`1505-R-4-2-cmp-py` |
| R-4 ③④ | 0건 = 기준 0건 | 일치 | `1504-R-4-3`·`-3-base`·`1504-R-4-4`·`-4-base` |
| R-4 ⑤ | `\b` 패턴: 작업 트리 `.py` 5줄(`types.py:423/426`, `loop.py:1067/1454/1713` — 전부 docstring·주석의 `PendingQuestion` ORM 언급) = 기준 5줄(`git grep -P`) → `SAME-as-base`; 추가 줄(`git diff 8a8767b -- app/agent \| grep '^+'`) 0건. 주의: `git grep -E` 는 `\b` 를 지원하지 않아 0건으로 나온다(`1504-R-4-5-base` 는 그래서 빈 출력) — `-P` 재실행이 유효 | 일치 | `1504-R-4-5`·`1505-R-4-5-base-P`·`1505-R-4-5-cmp-P`·`1503-R-4-5-added` |
| R-5 | 160 passed(6파일) | 일치 | `1503-R-5` |
| R-6 | 164 passed(5파일) — 실 공급자 import 0 | 일치 | `1503-R-6` |
| R-7 | `ok` / `ok` | 일치 | `1504-R-7a`·`1504-R-7b` |
| R-8 | 18 passed, 86 deselected | 일치 | `1504-R-8` |

깨진 1회차 파일(인용 손실, 판정에 쓰지 않음): `1502-D-1a`·`1502-D-2`·`1502-D-3a`·`1503-D-6b`·`1503-R-4-{1,2,3,4,5}`·`1503-R-4-{1,2}-base`·`1503-R-7a`·`1503-R-7b`·`1503-R-8`·`1504-R-4-5-base`(`\b` 미지원)·`1504-R-4-{2,5}-cmp`(pyc 잡음). `1503-D-5`·`1503-D-6a` 는 같은 파일 앞부분(exit 4)이 깨진 1회차, `# ===== append` 절이 유효.

## 3. 변이 시험 — 내가 직접 (`20261102-1509-verifier-u6-mutation.txt`)

사본 `verifier-u6/repo`(최상위 `alembic`·`alembic.ini`·`app`·`pyproject.toml`·`scripts`·`tests` — 비밀 파일 없음) 에서 `loop.py`·`questions.py`·`gate.py` 만 바꿔 `tests/test_api_chat_query.py`(8) 를 돌렸다(P3 만 사본 `scripts/mypy_check.py --run`). 대조군 C0 8 passed · mypy `[ok] 38/38`. 12 적용 / 12 검출 / 0 생존 / 패턴 불일치 0.

| id | 변이 | 결과 | 잡은 테스트 |
|---|---|---|---|
| P1 | 계획1 `run_turn` 조회 분기 진입 조건 `"Query"` | 검출 6 | (1)(2)(2b)(3)(6)(7) — 혼합 (4)·대조군 (5) 는 통과(게이트가 `intent` 로 독립 거부) |
| P2 | 계획2 `stored` 를 근거 건수(`timeline`)로 | 검출 4 | (1)(2)(4)(7) `stored == {0,0,0}` |
| P3 | `assert applied.pending_question_id is not None` 제거 | 검출(mypy) | `mypy_check.py --run` exit 1 — `[new] loop.py: [arg-type] Argument "question_id" to "PendingQuestionOut" has incompatible type "int \| None"; expected "int"` |
| V1 | `answer_question` 의 `already_answered` 조건 제거 | 검출 1 | (2b) `assert 200 == 409` |
| V2 | `answerer_from_env` 를 import 시점에 바인딩(`_AFE_BOUND()`) → monkeypatch 무효 | 검출 5 | (1)(2)(2b)(4)(7) — 실 공급자 경로로 빠짐 |
| V3 | `resume_turn` 조회 재개 분기 진입 조건 `"Query"` | 검출 2 | (2)(6) |
| V4 | 재개 후보 답 카드 `None`(`PersonNotFound`) 처리 제거 — U5 생존 V7 | 검출 1 | (6) — R-U5-1 닫힘 |
| V5 | new_person 언급을 "기록 없음" 목록에 넣지 않음 | 검출 1 | (3) reply |
| V6 | `REASON_QUERY_TURN_NO_WRITE` 문자열 변경 | 검출 1 | (4) |
| V7 | `_query_finish` `stop_reason` 항상 None | 검출 1 | (2) `stop_reason == "ask_user"` |
| V8 | merge 경로에서 `apply_resolution` 호출(별칭 누적, 결정 I (a) 위반) | 검출 2 | (1)(4) 행 수 불변 |
| V9 | 재개 후보 답에서 `update_person(new_alias)`(결정 G (b)) | 검출 2 | (2)(6) |

판정: 01-plan 118행 표 2건은 적힌 대로 잡힌다(P1 → HTTP 조회 테스트 6건 FAIL, P2 → `stored == 0` 단언 4건 FAIL). `assert` 제거는 테스트가 아니라 CI 의 mypy 단계가 잡는다(P3) — 이 커밋의 목적인 "CI 초록" 이 `mypy_check.py --run` 38=38 로 성립한다.

## 4. 계획 불일치·메모 판정

### 4a. 계획에 없는 것이 들어갔는가
`git diff HEAD -- app` 추가 15줄 = `assert` 1 + docstring 14. 새 상수·새 분기·새 trace step·`app/api`·`web` 변경 0. `assert` 는 위임문이 지시한 CI 수정이고 기존 관례(1076행)와 같은 형태. docstring 2곳은 R-U5-2 권고 그대로.

### 4b. 메인 세션의 01-plan 수정 2곳
D-3 ④ `-k merge_answers_from_card`: 테스트 이름 `test_a_merge_answers_from_card_and_writes_nothing` 이 토큰을 포함하고 `get_person_card` 스파이 1회를 단언한다(U4 테스트, 무수정) — 1 passed. R-4 ⑤ `PendingQuestion\b`: 작업 트리 BSD `grep -E` 에서 `PendingQuestionOut` 7곳이 빠지고 docstring 5줄만 남아 기준과 동일성 비교가 된다. 단 `git grep -E` 는 `\b` 미지원(R-U6-3).

### 4c. `__init__.py` 무변경 보고
R-2 ① 출력에 `app/agent/__init__.py` 가 있다(U1 `1dccb95`·U3 `a002706` 재export). "기준 이후 변경 없음" 이라는 보고는 틀렸지만 허용 집합 안이고 이 단위의 diff 는 아니다(`git diff HEAD -- app/agent/__init__.py` 빈 출력). registry `__init__.py` 행 비고에 두 해시가 맞게 적혀 있다.

### 4d. `docs/RUNNING.md` 예시 ↔ 실제 API
추가 8줄: `curl -X POST …/chat -d '{"utterance": "박선우 과장님 어떤 분이었지?"}'` 는 기존 예시와 같은 형식 · `"stored": {"persons": 0, "events": 0, "schedules": 0}` 는 `StoredOut`(정수 3개, `app/api/schemas.py` 75~82행)·(i)(iii) 실제 응답과 일치 · `"박선우"에 대한 기록이 없어요.` 는 `no_record_reply(["박선우"])` 와 글자 그대로 일치((iii)) · "자세한 건 인물 화면에서 볼 수 있어요." 는 `QUERY_MORE_HINT`(respond.py 130행) 와 일치 · identity → `POST /answers/{id}` → `stored` 전부 0 은 (ii) 와 일치. 바로 위 132행(기존 줄)의 기록 턴 예시 `"stored": {"persons": [...], …}` 는 실제와 다르다(R-U6-2 — 이 단위가 만든 줄은 아님).

## 5. `tests.md`·`registry.md`·테스트가 실패 조건을 검사하는가

- `tests.md` 머리글 24+28+71+23+10+8 = 164 ↔ `--collect-only` 24·28·71·33·8 = 164 일치; "2122 passed, skip 0" ↔ 내 실행 일치. U6 절 8행 이름 ↔ 수집 `SAME`. "결과 · 검출 변이" 열(U6-M1~M5)은 판정 근거로 쓰지 않았다.
- `registry.md`: `types.py`·`propose.py`·`settings.py` 행 "P5b U1(1dccb95)", `gate.py` "U2(06b7bb5)", `respond.py`·`__init__.py` "U3(a002706)", `loop.py` "U4(18219ba)·U5(49c1c67)·U6(해시 pending)", 테스트 행 4개 `1dccb95`/`06b7bb5`/`a002706`/`18219ba`(+"U5 재개 테스트는 49c1c67 에서") — `git log --oneline -6` 과 일치. 새 행 `tests/test_api_chat_query.py` 8건 `pending`(커밋 뒤 메인 세션이 채운다, 2곳).
- 테스트는 실패 조건을 검사한다: §3 의 12 변이가 모두 이 파일 8건으로만 잡힌다(P3 는 mypy). (1) 은 7개 테이블·`tool_call`·5 step·`evidence_counts`·`er_resolve.applied` 를 값으로 단언하고, (2) 는 실제 `POST /answers` 재개 경로(`answer_question` → `load_resume_input` → `resume_turn`)를 타며 `person_aliases` 포함 행 수 불변·`loop_query` 2행을 본다. (6) 은 실 `get_person_card` 의 `PersonNotFound` 를 `pytest.raises` 로 먼저 보인다. (5) 대조군이 있어 "조회 분기가 기록 턴을 가로채는" 반대 방향 결함도 잡는다.

## 6. 범위·원칙

- 원칙7: (iii)(vi) 거절·삭제·미기록 답은 `no_record_reply` 한 문장, 후속 질문 0. R-8 18 passed.
- 원칙1·2·4: 조회 턴은 `resolve()` 만, identity 만 `apply_resolution()`(D-3 ①), merge 에서 별칭 누적 0((i) `er_resolve.applied False`, V8 검출). 확신도 어휘 0.
- 원칙8: 실 LLM·실 임베딩 0(R-6 164 passed, 신규 테스트 실 공급자 import 0). 변이 결과 조작 없음 — 사본·원복·`git status` 를 증거 끝에 남겼다.
- 원칙9: §1 (i)(ii) trace.
- D16 "코드에서 지켜야 할 것" 1~7 = 판정 표 D-1~D-7 전부 일치(§2).
- security §1: 추가 줄·신규 테스트에 키 패턴 0, `os.environ` 직접 읽기 0(grep-constraints). 비밀 파일 미독·미복사(내 사본 최상위 6항목 + `.mypy_cache`). 구현자 U6 사본 `scratchpad/p5b-u6` 최상위 = `alembic`·`alembic.ini`·`app`·`pyproject.toml`·`scripts`·`tests` — 깨끗함(위임문 지시 준수). U5 사본 `p5b-u5/repo` 는 아직 비밀 파일이 남아 있다(R-U6-1).
- 계획 범위(01-plan U6 줄) 안. 범위 밖 경로 diff 0.

## 7. 소견

- [권고] R-U6-1 — `scratchpad/p5b-u5/repo` 최상위에 비밀 파일(`.e…`)이 아직 있다(U5 리뷰 R-U5-3·journal 2026-11-02 의 삭제 명령 전달 뒤에도 그대로; 이름만 `ls -A | grep -c` 로 확인, 내용 미독). 저장소 밖이라 커밋을 막지 않지만, 사용자가 삭제 명령을 실행했는지 커밋 전에 다시 확인 권고. U6 구현자 사본 `p5b-u6` 는 깨끗하다.
- [권고] R-U6-2 — `docs/RUNNING.md` 132행(기존 줄) 기록 턴 예시의 `stored: {"persons": [...], "events": [...], "schedules": [...]}` 는 실제 `StoredOut`(정수 3개)과 다르고, U6 가 바로 아래에 더한 조회 예시(정수)와 모순된다. 이 단위의 diff 는 아니므로 커밋을 막지 않는다 — 다음 문서 커밋에서 정수로 고치기 권고.
- [권고] R-U6-3 — 01-plan R-4 ⑤ 의 `\b` 는 BSD/GNU `grep -E` 에서는 동작하지만 `git grep -E` 는 지원하지 않는다(`1504-R-4-5-base` 가 0건으로 나온 이유). 04-review 가 기준 대조를 할 때 `git grep -nP` 또는 계획 문장대로 `git show 8a8767b:<파일> | grep -E` 를 쓸 것. 계획 문구 수정은 불필요(계획은 `git show … | grep` 을 적어 두었다).
- 메모(소견 아님): 내 1회차 행별 증거 일부가 래퍼 인용 손실로 깨졌다 — 유효 파일 목록은 §2 표에 적었고, 깨진 파일은 §2 끝에 열거했다. `save_evidence.py` 가 argv 를 공백으로 이어 `bash -c` 에 넘기므로 `-k '… or …'`·`-c "…"` 는 명령 전체를 문자열 하나로 줘야 한다(04-review 메모).
- 03-log 에 적을 내용(메인 세션): U6 항목 — 변경(`loop.py` +15/−1: `assert` 1줄(CI mypy `int | None` 좁히기) + 모듈 docstring 2줄 + `resume_turn` docstring 조회 재개 절 11줄(R-U5-2) / `tests/test_api_chat_query.py` 신규 440줄 8건(merge·identity→answers→409·new_person·혼합·대조군·R-U5-1 삭제·세션 헤더) / registry 해시 치환 5곳 + 새 행 1 + `loop.py` 행 U6 비고 / `tests.md` U6 절 8행·머리글 164/2122 / `docs/RUNNING.md` 조회 예시 8줄 / 01-plan 판정 표 문구 2곳(메인, 사용자 결정)) · 이유(01-plan U6 줄 · U4 `18219ba` CI 41388038128 failure = `scripts/mypy_check.py --run` 새 오류 1건 · R-U5-1·R-U5-2) · 계획과 다른 점(없음; `__init__.py` "무변경" 보고는 사실과 다르나 허용 집합 안) · 검증(구현 증거 48 + verifier: 8·2122 skip 0·ruff·7/7·`mypy_check --run` 38=38·판정 표 20행 일치·계약 값 80/0·변이 12/12/0) · 소견 R-U6-1~3 · 남은 것 U7 실 LLM 왕복(H-1, 사용자·메인) · registry `pending` 2곳(U6 해시).
- D16 갱신 이력에 적을 완료 해시 문구 제안(04-review 가 쓴다): "- 2026-11-02 **P5b-query-turn 구현 완료** — U1 `1dccb95` · U2 `06b7bb5` · U3 `a002706` · U4 `18219ba` · U5 `49c1c67` · U6 `<U6 커밋 해시>`. '코드에서 지켜야 할 것' 1~7 은 01-plan 판정 표 D-1~D-7 로 확인(verifier 재실행 `packages/P5b-query-turn/evidence/20261102-150{2,3,4,5}-verifier-u6-D-*.txt`, 04-review §2). 보정 2건(결정 F·I)은 그대로 — 조회 턴 `apply_resolution()` 은 identity 되묻기 때만(D-3 ①), 답 끝 문장은 `QUERY_MORE_HINT`. 실 LLM 왕복(H-1)은 U7 evidence 로 별도."

## 8. 판정

결과: 통과 — [필수] 0. 커밋 가능. 이 커밋으로 CI 의 mypy 단계(`python scripts/mypy_check.py --run`)가 38=38 로 돌아온다(§2, 변이 P3 로 역방향 확인). [권고] R-U6-1(스크래치패드 U5 사본 비밀 파일 삭제 확인, 사용자)·R-U6-2(`RUNNING.md` 132행 기존 예시, 다음 문서 커밋)·R-U6-3(04-review 의 `git grep -P` 메모)는 이 커밋을 막지 않는다.
