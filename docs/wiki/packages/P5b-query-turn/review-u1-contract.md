# P5b-query-turn U1 계약 — `intent` 필드·스키마 선택 키·`PendingResume.intent`·`STEP_LOOP_QUERY`·상수 4개·`FakeProposer.intents` — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 3(R-U1-1 01-plan U1 변이 표 M1 문구는 U2 이후에만 성립, R-U1-2 01-plan R-4 ⑤ "0건" 기대는 기준 시점에도 성립하지 않음(동일성으로 읽어야 함), R-U1-3 03-log 기록 항목). 코드 결함은 찾지 못했다. 변이 15건(구현자 M1~M4 재현 4 + 내 V1~V11) 전부 검출(대조군 108 passed), 전체 회귀 1982 passed(1958 + 24)·skip 0, ruff 통과, `tools_check` 7/7, 범위 밖 diff 0, 기존 테스트 파일 수정 0.
대상: 작업 트리(HEAD `fe4a99e`, 무변경 기준 `8a8767b`) — `git diff 8a8767b -- app`(`--numstat` `__init__.py 8 0` · `propose.py 25 7` · `types.py 17 0` · `settings.py 9 0`, 합 +59/−7) · 신규 `tests/test_agent_query_types.py`(수집 24 = 함수 18 + parametrize 7) · `docs/wiki/registry.md` 비고 4곳 + 새 행 1 · 신규 `docs/wiki/packages/P5b-query-turn/tests.md` · 구현 증거 `evidence/20261029-1206-u1-{types,pytest-all,ruff,tools-check,diff-filter,mutation}.txt`. `HANDOFF.md`·`journal.md` 의 문서 diff 는 위임대로 리뷰 대상 아님.
근거 문서: `01-plan.md` 89~94행(U1 계약·테스트 목록·변이 표) · 86~87행(구현 제약 (1)~(5)) · 170~178행(결정 A 확정 (a)) · 196~216행(결정 C) · 결정 D·E·J 확정 칸(상수 4개, 환경변수 오버라이드 없음) · 결정 G 확정 칸(`intent` 1필드·version "1") · 144행(판정 D-1) · 159행(판정 R-4) · `docs/wiki/decisions/D16-query-turn.md` 결정 1·9·"코드에서 지켜야 할 것" 1번째 줄 · `docs/wiki/specs/S3.4-ask-user-protocol.md` 끝 줄 · `docs/wiki/verification.md` 79~87행(변이 규칙) · `docs/wiki/security.md` · `tests/test_agent_propose.py:89-91` · `tests/test_agent_types.py:64`.
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`): `20261029-1229-verifier-u1-tests.txt`(U1 파일 -v) · `20261029-1229-verifier-u1-full-regression.txt`(전체 `-q -rs`) · `20261029-1229-verifier-u1-lint.txt`(ruff) · `20261029-1229-verifier-u1-tools-check.txt`(7/7) · `20261029-1230-verifier-u1-scope.txt`(범위 diff·D-1 ② grep·`propose.py` diff 전문) · `20261029-1230-verifier-u1-grep-constraints.txt`(제약 (1)~(5) + 비밀 패턴, 추가 줄 59줄 대상 + R-4 현재/기준 대조) · `20261029-1230-verifier-u1-contract-values.txt`(계약 값 Python 직접 확인) · `20261029-1232-verifier-u1-mutation.txt`(대조군 2 + 변이 15 + V1 재실행 + 끝의 `git status --short`).

---

## 1. 본 것 — 01-plan 89~92행 U1 계약 대조

| 계약(01-plan 글자 그대로) | 코드 위치 | 테스트 | 판정 |
|---|---|---|---|
| `INTENT_RECORD = "record"`·`INTENT_QUERY = "query"`·`INTENTS = (INTENT_RECORD, INTENT_QUERY)` | `types.py` 73~75행 | `test_intents_values` | 일치. V3(순서 뒤집기) 검출 |
| `Proposal.intent: str = INTENT_RECORD`(frozen), `to_dict()` 에 `"intent"` 항상 | `types.py` 185행·191행. `Proposal.__dataclass_params__.frozen == True`(contract-values) | `test_proposal_default_intent_is_record`·`test_proposal_to_dict_always_has_intent` | 일치. M1·V2 검출 |
| `PendingResume.intent: str = INTENT_RECORD`, `to_dict()` 는 `"query"` 일 때만 싣는다 · version 결정 G("1" 유지) | `types.py` 398행·415~416행. `PendingResume().to_dict()` 키 = `dropped·held_drafts·hints·mention·pending_calls·version`(`intent` 없음), `PendingResume(intent="query").to_dict()["version"] == "1"` | `test_pending_resume_default_omits_intent`·`test_pending_resume_query_to_dict_has_intent`·`test_pending_resume_version_stays_one` | 일치(S3.4 끝 줄 "`intent` 1필드"). M3·V9 검출 |
| `STEP_LOOP_QUERY`(= `loop_query`, 결정 C) — `LOOP_TRACE_STEPS` 밖 | `types.py` 69행. `in LOOP_TRACE_STEPS: False`, `len == 6` | `test_step_loop_query_outside_trace_steps` + 기존 `test_agent_types.py:64` | 일치. M4(기존 64행 테스트도 FAIL)·V10 검출 |
| `PROPOSAL_SCHEMA["properties"]["intent"] = {"type":"string","enum": list(INTENTS)}`, `required` 무변경 `["tool_calls"]`, `additionalProperties` 그대로 | `propose.py` 185행. 직접 확인: `required == ['tool_calls']`·`additionalProperties == False`·최상위 키 `['intent','tool_calls']`·`items.properties.args is PROPOSAL_ARG_SCHEMA → True` | `test_schema_intent_enum`·`test_schema_required_unchanged`·`test_schema_tool_calls_embeds_arg_schema` + 기존 `test_agent_propose.py:89-91` 무수정 통과 | 일치(D16 "코드에서 지켜야 할 것" 1). M2 검출 |
| `PROPOSAL_ARG_SCHEMA`·`tool_calls` 원소 스키마 한 글자도 안 바꿈 | 판정 D-1 ② grep(추가·삭제 줄 중 인자 스키마 키 포함) → `+ "intent": {...}` **1줄뿐**(그 줄 자체가 새 `intent` 속성 — 인자 스키마 줄 변경 0). `propose.py` diff 전문(scope 증거): 변경은 import 1줄·`intent` 속성 3줄(주석 2 + 1)·docstring 3줄·`validate_proposal` 분기 8줄·`return` 1줄·`FakeProposer` 7줄뿐 | — | 일치 |
| `validate_proposal()` — 결정 A: 키 없음/`null` → `"record"`, enum 밖 → `JudgeUnavailable("schema")` | `propose.py` 327~333행. 직접 확인: 없음→record, `None`→record, `"query"`→query, `""`·`"ask"`·`1`·`"QUERY"`·`True` → `JudgeUnavailable` 이고 `str(e) == "schema"`·`e.args == ("schema",)`(기존 어휘 — `propose.py` 325~348행의 다른 `schema` raise 와 같은 값, `tests/test_agent_propose.py` 235·432·523행과 같은 단언 방식) | `test_validate_proposal_{missing,null,query,record}_intent…`·`test_validate_proposal_bad_intent_is_schema_error[7]` | 일치. V1(삼킴)·V5(빈 문자열 허용)·V6(대소문자 무시)·V7(Proposal 에 안 넘김) 검출 |
| `FakeProposer.intents: dict[str,str] = field(default_factory=dict)` — 표에 있는 발화만 `raw["intent"]`, 기존 `FakeProposer(table=…)` 는 기록 턴 | `propose.py` 590행·593~596행. 직접 확인: `intents={"u":"query"}` → query, 없으면 record, `intents={"u":"ask"}` → `JudgeUnavailable("schema")`(검증을 우회하지 않음) | `test_fake_proposer_intents_table`·`test_fake_proposer_without_intents_is_record` | 일치. V8 검출 |
| 상수(결정 D·E·J 확정): `QUERY_TIMELINE_LIMIT=5`·`QUERY_MAX_PERSONS=1`·`QUERY_ANSWER_MAX_LINES=3`·`QUERY_ANSWER_MAX_CHARS=240`, 환경변수 오버라이드 없음 | `settings.py` 197~205행. `settings.py` 에서 `QUERY_` 와 `environ` 이 같이 있는 줄 0(contract-values) | `test_query_constants_values`(240 == 3 × `BRIEFING_SUGGESTION_MAX_CHARS` 도 단언, `QUERY_MORE_HINT` 없음 = U3 몫) | 일치. V4 검출 |
| `app/agent/__init__.py` 재export | import 4 + `__all__` 4(`INTENT_RECORD`·`INTENT_QUERY`·`INTENTS`·`STEP_LOOP_QUERY`), `all(n in ag.__all__) → True` | 테스트 파일이 `app.agent` 에서 import | 일치. V11(누락) 은 수집 단계 ImportError 로 검출 |
| 테스트 목록(01-plan 93행 11항목) | 24건이 11항목을 전부 덮는다(§5) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_agent_query_types.py -v` | 24 passed in 0.13s(PASSED 24줄), exit 0 | `…-1229-verifier-u1-tests.txt` |
| `.venv/bin/python -m pytest tests/ -q -rs` | 1982 passed, 1 warning in 24.63s — `skip` 문자열 0줄. 기준 1958 + 24 | `…-1229-verifier-u1-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-1229-verifier-u1-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-1229-verifier-u1-tools-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` | 빈 출력(기존 테스트 파일 수정 0) | `…-1230-verifier-u1-scope.txt` |
| `git diff --stat 8a8767b -- app/er app/tools app/api app/briefing app/db app/memory app/main.py alembic web` | 빈 출력 | 같은 파일 |
| `git diff --name-only 8a8767b -- app` | `app/agent/__init__.py`·`propose.py`·`types.py`·`app/settings.py` 4개 — 01-plan R-2 허용 집합의 부분집합(`gate.py`·`loop.py`·`respond.py` 는 U1 에서 손대지 않음) | 같은 파일 |
| 판정 D-1 ② `git diff 8a8767b -- app/agent/propose.py \| grep '^[-+]' \| grep 'PROPOSAL_ARG_SCHEMA\|"(person\|…\|facts)"'` | `+        "intent": {"type": "string", "enum": list(INTENTS)},` 1줄 — 인자 스키마 키의 추가·삭제 0. (01-plan 기대 "0줄"은 인자 스키마 줄을 뜻하고 이 1줄은 새 `intent` 속성이므로 기대 충족. 04-review 가 같은 grep 을 돌리면 이 1줄이 나온다 — §7 R-U1-3 에 메모) | 같은 파일 |
| 구현 제약 (1)~(5) + 비밀 패턴 — `git diff 8a8767b -- app` 의 추가 줄 59줄 대상 `grep -nEi` 6패턴 | 전부 exit 1(0건): `create_person\(`·`update_person\(`·`confidence\|T_merge\|t_merge\|T_new\|t_new`·`time\.sleep\|asyncio\.sleep\|while True`·`PendingQuestion\|flag_modified\|\.context *=`·비밀 패턴 | `…-1230-verifier-u1-grep-constraints.txt` |
| R-4 현재 트리 ↔ 기준 `8a8767b` | ① `create_person\(` -B1: 2줄(매치 1 + 문맥 1) = 기준 `loop.py` 1건 ② `update_person\(`: `loop.py` 706·805·856·1443 + `respond.py` 18 — 기준과 같은 줄(diff 에 없음) ③④ 0건 ⑤ 19건 전부 기준 시점 그대로(§7 R-U1-2) | 같은 파일 |
| 계약 값 Python 직접 확인(§1 의 값들) | 전부 기대값. `import app.agent; import app.api, app.main` → `ok`(순환 없음) | `…-1230-verifier-u1-contract-values.txt` |
| `pytest --collect-only -q tests/test_agent_query_types.py` ↔ `tests.md` 이름 | 수집 24건(함수 18) — `tests.md` 표 18행의 `파일::이름` 과 `diff` 결과 `SAME`(1:1) | §5 |

## 3. 변이 시험 — 내가 직접 (`20261029-1232-verifier-u1-mutation.txt`)

방법: 스크래치패드 `verifier-u1/mutate.sh` 가 저장소 밖 사본(`app`·`tests`·`alembic`·`pyproject.toml`·`alembic.ini` 복사, `__pycache__` 제거)에 문자열 치환(정확히 1곳 — 아니면 `AssertionError` 로 중단)을 적용하고 `pytest tests/test_agent_query_types.py tests/test_agent_types.py tests/test_agent_propose.py -q -p no:cacheprovider`(108건) 를 돌린다. M1 은 추가로 기록 턴 쪽 `tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_gate.py`(76건, DB 5433) 도 돌렸다(§4 판정용). 저장소 무수정 — 스크립트 끝의 `git status --short` 가 리뷰 전과 같다(제품 파일 4 + 문서 + 증거만). 구현자의 `p5b-u1/mut.sh` 와는 별개 디렉터리·별개 스크립트. V1 은 첫 실행의 출력 필터(`grep error`)가 테스트 이름의 `error` 에 걸려 요약 줄이 잘렸으므로 `mutate-v1-rerun.sh` 로 재실행해 `--append` 했다(요약 `7 failed, 101 passed`).

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군(3파일) | 없음 | 108 passed | — |
| C0b 대조군(기록 턴 루프·API·게이트) | 없음 | 76 passed | — |
| M1 `Proposal.intent` 기본값 → `"query"`(구현자 재현) | `types.py` Proposal 필드 | FAIL 2 / 기록 턴 76 **전부 통과** | `test_proposal_default_intent_is_record`·`test_proposal_to_dict_always_has_intent`. 구현자 보고와 같다 — §4 |
| M2 스키마 enum 에서 `query` 제거 | `"enum": [INTENT_RECORD]` | FAIL 1 | `test_schema_intent_enum` |
| M3 `PendingResume.to_dict()` 가 `intent` 항상 | 조건 제거 | FAIL 1 | `test_pending_resume_default_omits_intent` |
| M4 `STEP_LOOP_QUERY` 를 `LOOP_TRACE_STEPS` 에 | 튜플 끝에 추가 | FAIL 2 | `test_step_loop_query_outside_trace_steps` + 기존 `test_agent_types.py::test_loop_trace_steps_are_fixed_six_in_order`(64행) |
| V1 enum 밖 값을 `record` 로 삼킴(결정 A (a') 비추천안) | `raise JudgeUnavailable("schema")` → `intent = INTENT_RECORD` | FAIL 7(`DID NOT RAISE`) | `test_validate_proposal_bad_intent_is_schema_error[ask,"",QUERY,1,True,bad5,bad6]` |
| V2 `Proposal.to_dict()` 에서 `intent` 누락(D16 결정 9) | 키 삭제 | FAIL 1(`KeyError: 'intent'`) | `test_proposal_to_dict_always_has_intent` |
| V3 `INTENTS` 순서 뒤집기 | `(INTENT_QUERY, INTENT_RECORD)` | FAIL 2 | `test_intents_values`·`test_schema_intent_enum` |
| V4 `QUERY_ANSWER_MAX_CHARS` 240 → 241 | 상수 | FAIL 1(`241 == 240`) | `test_query_constants_values` |
| V5 빈 문자열을 `None` 과 같이 record 로 | `is None or == ""` | FAIL 1 | `…bad_intent_is_schema_error[]` |
| V6 대소문자 무시(`"QUERY"` 허용) | `.lower() in INTENTS` | FAIL 1 | `…bad_intent_is_schema_error[QUERY]` |
| V7 `validate_proposal` 이 `intent` 를 `Proposal` 에 안 넘김 | `return Proposal(tool_calls=parsed, raw=raw)` | FAIL 2 | `test_validate_proposal_query_intent`·`test_fake_proposer_intents_table` |
| V8 `FakeProposer` 가 `intents` 표 무시 | `if False and …` | FAIL 1 | `test_fake_proposer_intents_table` |
| V9 `PendingResume.intent` 기본값 → `"query"` | 필드 기본값 | FAIL 1(`'query' == 'record'`) | `test_pending_resume_default_omits_intent` |
| V10 `STEP_LOOP_QUERY` 값 오타 `loop_queries` | 상수 | FAIL 1 | `test_step_loop_query_outside_trace_steps` |
| V11 `__init__` 재export 누락(`STEP_LOOP_QUERY`) | import·`__all__` 삭제 | 수집 ERROR 1(ImportError) | 파일 전체 |

15/15 검출. 생존 변이 없음 → 테스트 공백 소견 없음.

## 4. 계획 불일치 1건 판정 — 01-plan 94행 변이 표 M1

01-plan 94행: "`Proposal.intent` 기본값을 `"query"` 로 → 기존 기록 턴 테스트 다수 + `test_validate_proposal_missing_intent_is_record` FAIL". 내 재현(§3 M1): 잡는 테스트는 `test_proposal_default_intent_is_record`·`test_proposal_to_dict_always_has_intent` 2건이고, `test_validate_proposal_missing_intent_is_record` 는 통과하며, 기록 턴 76건도 전부 통과한다. 구현자 보고(`tests.md` 5행 비고)와 같다.

- 왜 그런가(코드 읽기): `validate_proposal()` 327~333행은 키 없음을 **스스로** `INTENT_RECORD` 로 결정해 `Proposal(..., intent=intent)` 로 **항상 명시** 전달한다(351행). 그래서 dataclass 기본값은 `validate_proposal` 경로에 영향이 없고, `Proposal()` 직접 생성에만 영향이 있다. `test_validate_proposal_missing_intent_is_record` 는 다른 변이(validate 의 None→record 분기를 query 로 — V5·V7 류)를 잡는 자리다. 기록 턴 테스트가 통과하는 것은 U1 범위 문장 그대로 "도는 분기는 아직 없다" — `gate.py`·`loop.py` 가 `proposal.intent` 를 읽지 않으므로(두 파일 diff 0) 값이 무엇이든 동작이 같다.
- 계약 위반인가: **아니다.** 결정 A (a) 의 코드 규칙("키 없음/`null` → record, enum 밖 → schema")과 01-plan 90행 "`Proposal.intent: str = INTENT_RECORD`" 는 둘 다 지켜졌고, 그 둘이 독립적으로 보호된다는 것이 M1·V5·V7 결과다. 계약(코드가 지켜야 할 것)과 변이 표(테스트가 잡아야 할 것)의 서술 중 후자가 "어느 테스트가" 를 틀리게 적었을 뿐이다.
- 무엇으로 남기나: **메모 — U2 이후 재확인.** U2 가 `gate.py` 에 `proposal.intent == INTENT_QUERY → WRITE_TOOLS 거부` 를 넣으면 M1(기본값 query)은 기록 턴의 `add_event`·`add_schedule` 제안을 전부 거부하게 되어 "기존 기록 턴 테스트 다수 FAIL" 이 그때 비로소 성립한다. 04-review(판정 R-5 + 단위별 변이 1개)에서 M1 을 다시 돌려 그 문장을 확인하면 된다. 01-plan 문구 수정은 verifier 가 하지 않는다 — §7 R-U1-1.

## 5. `tests.md`·`registry.md`

- `tests.md` 표 18행 ↔ `--collect-only` 24건(함수 18 + `test_validate_proposal_bad_intent_is_schema_error` 파라미터 7): 이름 집합이 글자 그대로 같다(`diff … && echo SAME` → `SAME`). "24 passed"·"1982 passed, skip 0"·검출 변이 `U1-M1~M4` 기록이 구현 증거 `…-1206-u1-types.txt`·`…-1206-u1-pytest-all.txt`·`…-1206-u1-mutation.txt` 및 내 재실행과 일치. 5행 비고(M1 은 dataclass 기본값이라 다른 두 테스트가 잡음)는 §4 와 같은 사실.
- 01-plan 93행 테스트 목록 11항목 ↔ 24건: `INTENTS` 값 / 최상위 키 집합 + enum / `tool_calls` 가 `PROPOSAL_ARG_SCHEMA` 를 그대로 품음(`is`) / 없음→record / query→query / `"ask"`→schema(+6 변형) / `Proposal.to_dict()["intent"]` / `PendingResume(intent="query")` + 기본값 키 없음 / `STEP_LOOP_QUERY` 밖·접두사 / `FakeProposer(intents=…)` / 상수 값 — 전부 덮인다. 계획에 없는 추가 단언 3개(`required` 무변경·version "1"·`QUERY_MORE_HINT` 부재)는 결정 A·G·F 확정 문장의 직접 번역이라 범위 초과 아님.
- `registry.md`: 비고 4곳(`settings.py`·`types.py`·`__init__.py`·`propose.py` 행, 전부 "P5b U1(해시 pending)") + 새 행 1(`tests/test_agent_query_types.py`, 24건, pending). 내용(상수 4개 값·`Proposal.intent` 항상/`PendingResume.intent` 조건부·version "1"·재export 4·`validate_proposal` 규칙·`FakeProposer.intents`)이 코드와 맞다. 커밋 뒤 해시 치환은 메인 세션 몫. 01-plan 117행이 "고친 기존 모듈은 비고에 한 줄(새 행 아님)·새 테스트는 행" 이라 적었고 그대로다.

## 6. 범위·원칙

- 범위: `app/` 변경 4파일이 01-plan 92행·R-2 허용 집합 안. `app/er`·`app/tools`·`app/api`·`app/briefing`·`app/db`·`app/memory`·`alembic`·`web` diff 0. 기존 테스트 파일 수정 0(`--diff-filter=M` 빈 출력) — `tests/test_agent_propose.py:89-91`·`tests/test_agent_types.py:64` 그대로 통과(전체 1982 안). `gate.py`·`loop.py`·`respond.py` 를 손대지 않아 "도는 분기는 아직 없다" 가 코드로 성립(§4).
- 원칙1·2·4: U1 은 확신도·임계치·ER 단계를 건드리지 않는다 — 추가 줄에 `confidence`/`T_merge`/`T_new` 0, `app/er` diff 0.
- 원칙7: 상담·감정 문장 0(추가 줄은 상수·스키마·분기·주석뿐). 제외 범위 침범 없음.
- 원칙9: `Proposal.to_dict()` 가 `intent` 를 항상 실어 `loop_extract.output` 에 의도 분류 결과가 남을 재료가 생겼다(D16 결정 9; 실제로 trace 에 실리는지는 U4 몫). `STEP_LOOP_QUERY` 는 `LOOP_TRACE_STEPS` 6종 밖이라 기록 턴 집계(P10)가 오염되지 않는다(결정 C).
- 스키마 v2·툴 시그니처 v2 무변경(`tools_check` 7/7, `alembic` diff 0). `PROPOSAL_SCHEMA` 는 `additionalProperties: False` 를 유지한 채 선택 키 1개만 늘었다 — 기존 공급자 응답(키 없음)이 그대로 통과한다(기존 1958 통과가 그 증거).
- security: 추가 줄에 키 패턴 0, `.env` 미독. 증거 파일은 전부 `save_evidence.py` 로 저장(비밀 검사 통과).
- 동결·활성: 활성 패키지 P5b-query-turn(`fe4a99e` 에서 활성화), U1 은 그 첫 단위.

## 7. 소견

[필수] 없음.

[권고] (커밋을 막지 않음)

- R-U1-1 · 01-plan 94행 변이 표 M1 의 "잡는 테스트" 서술이 현재 구조와 다르다(§4). `test_validate_proposal_missing_intent_is_record` 가 아니라 `test_proposal_default_intent_is_record`·`test_proposal_to_dict_always_has_intent` 가 잡고, "기존 기록 턴 테스트 다수 FAIL" 은 U2 가 게이트에 `intent` 분기를 넣은 뒤에야 성립한다. 계약 위반 아님. 04-review 에서 U2 이후 M1 을 다시 돌려 그 문장을 확인하고, 01-plan 문구를 고칠지는 메인 세션 판단(계획 문서는 verifier 가 고치지 않는다).
- R-U1-2 · 01-plan 159행 판정 R-4 ⑤ 의 기대 "③④⑤ 0건" 중 ⑤(`PendingQuestion|flag_modified|\.context *=`)는 기준 `8a8767b` 시점에도 0건이 아니다 — `app/agent/*.py` 에 19건(`types.py` 5·`loop.py` 10·`respond.py` 4, 전부 `PendingQuestionOut` 타입명과 "`PendingQuestion` ORM 을 조회하지 않는다" 류 docstring). 이번 추가 줄 59줄에는 0건이고 현재 출력이 기준과 같으므로 같은 행의 괄호 문장("각 출력이 `8a8767b` 시점과 같다")으로 읽으면 통과다. 04-review 가 "0건" 을 글자 그대로 적용하면 거짓 FAIL 이 난다 — 동일성으로 판정할 것을 메모.
- R-U1-3 · 03-log U1 항목에 적을 것(메인 세션). ① 판정 D-1 ② grep 이 `+ "intent": {...}` 1줄을 낸다 — 이는 새 `intent` 속성 줄이고 인자 스키마 줄 변경은 0(§2). ② M1 의 실제 검출 테스트와 "기록 턴 FAIL 은 U2 이후"(§4). ③ 변이 15건 전부 검출·생존 0(§3). ④ `registry.md` 해시 pending 5곳 치환. Refs `P5b-query-turn CR-004 D16 S3.4 원칙1 원칙4 원칙7 원칙9 R19`.

## 8. 판정

통과. U1 의 계약 전부 — `INTENTS`·`Proposal.intent`(frozen, `to_dict` 항상)·`PendingResume.intent`(`"query"` 일 때만, version "1")·`STEP_LOOP_QUERY`(6종 밖)·`PROPOSAL_SCHEMA.intent` enum(`required`·`additionalProperties`·인자 스키마 무변경)·`validate_proposal` 결정 A 규칙(없음/null → record, 그 밖 → `JudgeUnavailable("schema")`, 기존 어휘)·`FakeProposer.intents`·상수 4개(환경변수 없음)·재export 4 — 가 01-plan 89~92행·결정 A·C·D·E·G·J 확정 칸·D16 결정 1·9·S3.4 끝 줄과 글자 그대로 맞고, 내 재실행에서 24 passed·전체 1982 passed(1958 + 24)·skip 0·ruff 통과·`tools_check` 7/7 이다. 변이 15건(구현자 4 재현 + 내 11)을 테스트가 전부 검출했다(대조군 108 passed). 기존 테스트 파일 수정 0, 범위 밖 diff 0, 구현 제약 (1)~(5)·비밀 0. 계획 불일치 1건(M1 변이 표)은 계약 위반이 아니라 변이 표 서술의 정확성 문제로 U2 이후 재확인 메모(R-U1-1). 코드에 요구하는 변경은 없다. 커밋·승인은 메인 세션·사용자 몫이다.
