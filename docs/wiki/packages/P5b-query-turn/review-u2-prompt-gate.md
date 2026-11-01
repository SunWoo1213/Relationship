# P5b-query-turn U2 인식 프롬프트 (i)(ii)(iii) + 게이트 Q — 조회 턴 기록 제안 거부 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 5(R-U2-1 01-plan 99행 변이 표 2번째 항목은 동등 변이(문구 수정안 포함), R-U2-2 `gate.py` 284·293행의 "①②④③⑤" 표기에 Q 미반영, R-U2-3 조회 턴 테스트 5개 함수에 `_spy_all` 없음, R-U2-4 `tests.md` 헤더 "함수 17개" 는 18개, R-U2-5 03-log 기록 항목). 코드 결함은 찾지 못했다. 변이 15건(계획 표 4 재현 + 대체 변이 1 + 내 변이 8 + R-U1-1 재실행 1) 중 검출 13·동등 변이 2(M2a·M4 — 둘 다 테스트 공백이 아니라 코드 구조상 관측 불가, §3). 전체 회귀 2010 passed(1982 + 28)·skip 0, R-5 회귀 184 passed, ruff 통과, `tools_check` 7/7, 범위 밖 diff 0, 기존 테스트 파일 수정 0.
대상: 작업 트리(HEAD `1dccb95` = U1, 무변경 기준 `8a8767b`) — `git diff HEAD -- app`(`--numstat` `__init__.py 4 0` · `gate.py 23 1` · `propose.py 10 1`, 합 +37/−2) · 신규 `tests/test_agent_query_gate.py`(수집 28 = 함수 18 + parametrize 10) · `docs/wiki/registry.md` 비고 2곳 + 새 행 1 · `docs/wiki/packages/P5b-query-turn/tests.md` U2 절 · 구현 증거 `evidence/20261102-0810-u2-{gate,gate-rerun,pytest-all,regression,ruff,tools-check,diff-filter}.txt`·`20261102-0811-u2-mutation{,-extra}.txt`·`20261102-0812-u2-final-{gate,pytest-all}.txt`·`20261102-0813-u2-final-ruff.txt`. `HANDOFF.md`·`journal.md` 의 문서 diff 는 위임대로 리뷰 대상 아님.
근거 문서: `01-plan.md` 95~99행(U2 계약·테스트 목록·변이 표) · 86~87행(구현 제약 (1)~(5)) · 94행(U1 변이 표 M1 메모 "U2 뒤 M1 재실행") · 160행(판정 R-5 회귀 파일 7개) · 180~195행(결정 B 확정 B-1 `query_turn_no_write` · B-2 ①②Q④③⑤ · B-3 (b)) · `docs/wiki/decisions/D16-query-turn.md` 결정 2("`search_person` 은 여전히 LLM 이 직접 부르지 못한다(게이트 ② 유지)")·결정 6("`intent == "query"` 면 그 턴은 기록 0(조회 우선, 한 턴 한 의도)")·결정 7("'나'·'저' 등은 인식 단계 프롬프트 지시로 언급에서 제외")·"코드에서 지켜야 할 것" 2("`gate.py` 는 `intent == "query"` 턴의 기록 툴 제안을 거부하고 … `search_person`·`ask_user`·`get_briefing` 의 `not_callable_by_llm` 은 그대로다") · `docs/wiki/verification.md` 79~87행(변이 규칙) · `docs/wiki/security.md` · 메인 세션이 정한 (ii) 두 문장 글자 그대로·(i)(iii) 위치 자유 · `review-u1-contract.md` §4·§7 R-U1-1.
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`): `20261102-0816-verifier-u2-tests.txt`(U2 파일 -v) · `20261102-0816-verifier-u2-r5-regression.txt`(R-5 7파일 -q) · `20261102-0817-verifier-u2-full-regression.txt`(전체 `-q -rs`) · `20261102-0817-verifier-u2-lint.txt`(ruff) · `20261102-0817-verifier-u2-tools-check.txt`(7/7) · `20261102-0821-verifier-u2-scope.txt`(범위 diff·`-` 줄 전수·`check()` def 줄·기준 어휘·수집·`git status`) · `20261102-0821-verifier-u2-contract-values.txt`(계약 값 Python 직접 확인 — 3회 append, 1·2회는 내 스크립트의 `sys.path`/`sys.modules` 오류로 exit 1, 3회차 exit 0 이 판정 근거) · `20261102-0821-verifier-u2-grep-constraints.txt`(제약 (1)~(5) + 비밀 패턴, U2 추가 줄 37·누적 96·신규 테스트 279줄 대상 + R-4 현재/기준 대조 + append 로 ⑤ `*.py` 재집계) · `20261102-0821-verifier-u2-mutation.txt`(대조군 2 + 변이 15, append 로 M9 재실행 요약, 끝의 `git status --short`).

---

## 1. 본 것 — 01-plan 95~98행 U2 계약 대조

| 계약(01-plan 글자 그대로) | 코드 위치 | 직접 확인(contract-values 3회차) | 테스트 | 판정 |
|---|---|---|---|---|
| `WRITE_TOOLS = frozenset({"add_event","add_schedule","update_person","create_person"})` | `gate.py` 139~141행 | `frozenset`, `== frozenset(TOOL_NAMES) - NOT_CALLABLE_BY_LLM → True` | `test_write_tools_equals_tool_names_minus_not_callable` | 일치. M3·V7 검출 |
| 거부 사유 1개(결정 B-1 `query_turn_no_write`)를 `GATE_REJECTION_REASONS` 에 더한다 | `gate.py` 112~113행·123행 | 값 `'query_turn_no_write'`, 튜플 7개, 앞 6개가 기준 `8a8767b` 튜플과 순서까지 동일, 7번째가 새 사유 | `test_reason_value_and_vocabulary_order` | 일치. V6·V10 검출 |
| `check()` 순서 ①②Q④③⑤ — ② 다음·④ 앞에 "Q: `proposal.intent == INTENT_QUERY` 이고 `name ∈ WRITE_TOOLS`" | `gate.py` 316~320행(② 310~314, ④ 322~326 사이) | `update_person(person_id=3)`+query → `['query_turn_no_write']`(④ 보다 먼저 True) · `search_person`/`ask_user`/`get_briefing`+query → `not_callable_by_llm` · `delete_person`+query → `unknown_tool` · 8건 섞어 → accepted `[]`, rejected 8, `stop_reason None` | `test_query_turn_update_person_with_person_id_is_query_reason`·`…not_callable_tools_keep_reason[3]`·`…search_person_stays_not_callable`·`…unknown_tool_stays_unknown`·`…never_accepts_anything` | 일치(D16 결정 2·"코드에서 지켜야 할 것" 2). M1·M2a2·M2c·M2d·V11 검출 |
| 모듈 docstring "적용 순서" 절에 Q 를 더한다 | `gate.py` 20~25행 | 20행 `## 적용 순서 (①②Q④③⑤ …)` + Q 설명 4줄 | — | 일치. 단 284행 절 주석·293행 `check()` docstring 은 "①②④③⑤" 그대로 — §7 R-U2-2 |
| 순수 함수·시그니처 그대로 | `gate.py` 288행 | `inspect.signature` 현재 == 기준 `8a8767b`: `(proposal: 'Proposal', *, config: 'GateConfig | None' = None) -> 'GateVerdict'` → True. Q 블록은 `rejected.append`·`continue` 뿐(툴 호출·DB 없음) | 스파이 테스트 4함수(§5) | 일치 |
| 기록 턴(`intent` 기본값) 같은 제안 → 기존 판정 그대로 | — | 4종 각각 + `person_id`·`display_name` + 혼합 10건을 기준 `8a8767b` 의 `gate.check` 와 비교 → accepted/rejected/stop_reason/limits 전부 동일 | `test_record_turn_write_tools_keep_old_verdict[4]`·`…not_callable_tools_keep_reason[3]`·`…explicit_record_intent_same_as_default` + 기존 `test_agent_gate.py` 32건 무수정 통과 | 일치 |
| (i) 의도 분류 지시 — "발화가 이미 기록된 인물 정보를 묻는 질문이면 intent 를 query, 새 사실·사건·일정을 알려주는 말이면 record. 둘이 섞이면 query" | `propose.py` 244~246행 | 구현 문장 "발화가 이미 기록된 인물 정보를 묻는 질문이면 intent 를 query, 새 사실·사건·일정을 알려주는 말이면 record 로 답하라. 둘이 섞이면 query 다." — 계획 문구 글자 그대로 포함은 False(어미 "record." → "record 로 답하라.", "query" → "query 다."), 세 핵심 구("…intent 를 query"·"…말이면 record"·"둘이 섞이면 query")는 글자 그대로 포함. 조회 우선(D16 결정 6) 뜻 보존 | `test_prompt_has_intent_classification_sentence` | 일치(위치 자유·어미 다듬기 — 뜻 보존, 허용). V9 검출 |
| (ii) 기존 "절대 제안하지 마라" 문장 바로 뒤에 두 문장 글자 그대로, 기존 문장 삭제 없음 | `propose.py` 240~243행 | `"절대 제안하지 마라. "` 1회·(ii) 1회, `index(old)+len(old) == index(ii)` → True(사이 문자 0). 기준 system 문장 5개 전부 현재 system 에 있음(유실 0), user 프롬프트 기준과 동일, system 258 → 507자. diff `-` 줄은 `f"절대 제안하지 마라. {PROPOSAL_TOOL_NAME} 도구로만 답하라."` 1줄뿐이고 그 두 조각이 240행·249행에 그대로 남아 있다(줄바꿈 재배치) | `test_prompt_has_query_mention_exception_sentences_after_old_sentence`(인접성까지 단언) + 기존 `tests/test_agent_propose.py` 126~131행 무수정 통과 | 일치(결정 B-3 (b)). V5·V8 검출 |
| (iii) "'나'·'저'·'내'·'제' 처럼 말하는 사용자 자신을 가리키는 말은 인물로 제안하지 마라" | `propose.py` 247~248행 | 글자 그대로 포함 True | `test_prompt_excludes_self_reference` | 일치(D16 결정 7) |
| `app/agent/__init__.py` 재export | import 2 + `__all__` 2 | `ag.REASON_QUERY_TURN_NO_WRITE is gate.…`·`ag.WRITE_TOOLS is gate.WRITE_TOOLS` → True, `__all__` 포함 [True, True]. `import app.agent; app.api; app.main` → ok | 테스트 파일은 `app.agent.gate` 에서 직접 import | 일치 |
| 테스트 목록(01-plan 97행 8항목) | 28건이 8항목 전부를 덮는다(§5) | — | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_agent_query_gate.py -v` | 28 passed in 0.10s, exit 0 | `…-0816-verifier-u2-tests.txt` |
| R-5 `… pytest tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_propose.py tests/test_agent_types.py tests/test_agent_query_types.py -q` | 184 passed, 1 warning in 1.81s, exit 0 | `…-0816-verifier-u2-r5-regression.txt` |
| `… pytest tests/ -q -rs` | 2010 passed, 1 warning in 24.89s — `skip` 문자열 0줄. 기준 1982 + 28 | `…-0817-verifier-u2-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-0817-verifier-u2-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-0817-verifier-u2-tools-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` | 빈 출력(0줄) — 기존 테스트 파일 수정 0 | `…-0821-verifier-u2-scope.txt` (A) |
| `git diff --stat 8a8767b -- app/er app/tools app/api app/briefing app/db app/memory app/main.py alembic web` | 빈 출력(0줄) | 같은 파일 (B) |
| `git diff --name-only HEAD -- app` | `app/agent/__init__.py`·`gate.py`·`propose.py` 3개 — 01-plan 95행이 지정한 두 모듈 + 재export | 같은 파일 (C)(D) |
| `git diff HEAD -- app/agent/propose.py` 의 `-` 줄 전수 | `-        f"절대 제안하지 마라. {PROPOSAL_TOOL_NAME} 도구로만 답하라."` 1줄 — 두 조각 모두 `+` 줄에 남음(문장 유실 0, §1 (ii) 행) | 같은 파일 (E) |
| `git diff HEAD -- app/agent/gate.py` 의 `-` 줄 전수 | `-## 적용 순서 (①②④③⑤ -- ④가 ③보다 먼저)` 1줄(docstring 제목 → Q 포함 제목으로 교체) | 같은 파일 (F) |
| `check()` def 줄 기준 vs 현재 | 272행(기준)·288행(현재) 글자 그대로 같음 | 같은 파일 (H) |
| 구현 제약 (1)~(5) + 비밀 패턴 — U2 추가 줄 37·누적 추가 줄 96·신규 테스트 279줄 대상 `grep -nE` 6패턴 | app 추가 줄: 6패턴 전부 exit 1(0건). 신규 테스트 파일: 패턴 1 `create_person\(` 1건 = 129행 `def test_query_turn_rejects_create_person(` — 01-plan 98행이 지정한 테스트 이름(예외로 판정, 기록해 둔다), 그 밖 0건 | `…-0821-verifier-u2-grep-constraints.txt` |
| R-4 현재 ↔ 기준 `8a8767b` | ① `create_person\(` -B1: `loop.py` 1473행 1건 = 기준 1473행 ② `update_person\(`: `loop.py` 706·805·856·1443 + `respond.py` 18 = 기준과 같은 줄 ③④ 0건 ⑤ `*.py` 19건(`types` 5·`loop` 10·`respond` 4) = 기준 19건, `gate`·`propose`·`__init__` 0 — 동일성(R-U1-2). 첫 집계 22 는 `__pycache__/*.pyc` 3건 포함이었고 append 로 재집계 | 같은 파일 + append |
| 프롬프트 비밀·환경변수 흔적 | `API_KEY`·`OPENAI`·`ANTHROPIC`·`sk-`·`KEY`·`SECRET`·`TOKEN`·`environ` 전부 없음 `[]` | `…-contract-values.txt` §6 |
| `pytest --collect-only -q tests/test_agent_query_gate.py` ↔ `tests.md` | 수집 28건, 함수명 18개 — `tests.md` 표 18행의 `파일::이름` 과 `diff` → `SAME`(1:1). 헤더의 "함수 17개" 만 틀림(§7 R-U2-4) | `…-scope.txt` (K) + 내 비교(§5) |

## 3. 변이 시험 — 내가 직접 (`20261102-0821-verifier-u2-mutation.txt`)

방법: 스크래치패드 `verifier-p5b-u2/mutate.py` 가 변이마다 새 하위 디렉터리에 `app`·`tests`·`alembic`·`pyproject.toml`·`alembic.ini` 를 복사(`__pycache__` 제외)하고 문자열 치환(정확히 1곳 — 아니면 `AssertionError` 중단)을 적용한 뒤 `pytest tests/test_agent_query_gate.py tests/test_agent_gate.py -q -p no:cacheprovider`(60건, DB 없음)를 돈다. M9 는 기록 턴 쪽 `tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py`(76건, DB 5433) + `test_agent_query_gate.py`(28) + `test_agent_query_types.py`(24) = 128건. 저장소 무수정 — 스크립트 끝의 `git status --short` 가 리뷰 전과 같다(제품 파일 3 + 문서 4 + 증거 + 신규 테스트 1). 구현자의 `p5b-u2/mutate.sh`·`mutate2.sh` 와는 별개 디렉터리·별개 스크립트. M9 는 첫 실행의 출력 필터(40줄 상한)가 요약 줄을 잘라 `--append` 로 단독 재실행했다(요약 `42 failed, 86 passed`).

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군(게이트 2파일) | 없음 | 60 passed | — |
| C0b 대조군(기록 턴 루프·API·게이트) | 없음 | 76 passed | — |
| M1 Q 검사 제거(계획 표 1) | Q 블록 삭제 | FAIL 9 | `test_query_turn_rejects_write_tools[4]`·`…rejects_create_person`·`…update_person_with_person_id_is_query_reason`·`…never_accepts_anything`·`…has_no_limit_rejection…`·`…via_fake_proposer` |
| M2a Q 를 ② 앞으로(계획 표 2, 조건 그대로) | ② 블록과 Q 블록 자리 바꿈 | 60 passed — 동등 변이 | 없음. §4 |
| M2a2 대체 변이: Q 를 ② 앞으로 + 조건 `name in app_tools.TOOL_NAMES` | 위 + 조건 확장 | FAIL 4 | `test_query_turn_search_person_stays_not_callable`·`…not_callable_tools_keep_reason[search_person, ask_user, get_briefing]` |
| M2c Q 를 ④ 뒤로(③ 앞) | Q 블록과 ④ 블록 자리 바꿈 | FAIL 1 | `test_query_turn_update_person_with_person_id_is_query_reason`(`['person_id_from_llm'] == ['query_turn_no_write']`) |
| M2d Q 를 ③ 뒤로(버킷 직전) | Q 블록을 `bucket =` 앞으로 | FAIL 1 | 같은 테스트 |
| M3 `WRITE_TOOLS` 에서 `create_person` 제거(계획 표 3) | 집합 리터럴 | FAIL 4 | `test_write_tools_equals_tool_names_minus_not_callable`·`…rejects_write_tools[create_person]`·`…rejects_create_person`·`…never_accepts_anything` |
| M4 조건을 `intent != "record"` 로(계획 표 4) | 비교식 | 60 passed — 동등 변이(계획이 그렇게 적음) | 없음 — `INTENTS` 가 2값뿐이라 `!= record` ≡ `== query` |
| V5 (ii) 두 문장 삭제 | `propose.py` 3줄 삭제 | FAIL 1 | `test_prompt_has_query_mention_exception_sentences_after_old_sentence` |
| V6 사유 문자열 오타 `query_turn_no_writes` | 상수 값 | FAIL 5 | `test_reason_value_and_vocabulary_order` + `…rejects_write_tools[4]`(리터럴 `"query_turn_no_write"` 단언) |
| V7 `WRITE_TOOLS` 에 `search_person` 추가 | 집합 리터럴 | FAIL 1 | `test_write_tools_equals_tool_names_minus_not_callable`(`search_person` 사유는 ② 가 먼저라 그대로 — 집합 등식만 잡는다) |
| V8 (iii) 를 (ii) 앞으로(인접성 깨짐) | 문장 순서 교체 | FAIL 1 | 인접성 단언 `(218 + 11) + 1 == 282` |
| V9 (i) "둘이 섞이면 query" → record(D16 결정 6 위반) | 문자열 | FAIL 1 | `test_prompt_has_intent_classification_sentence` |
| V10 새 사유를 `GATE_REJECTION_REASONS` 에서 누락 | 튜플 원소 삭제 | FAIL 1 | `test_reason_value_and_vocabulary_order`(`'limit' == 'query_turn_no_write'`) |
| V11 Q 가 `continue` 없이 계속 흐름(거부 기록 뒤 ④③⑤ 도 적용) | `continue` 삭제 | FAIL 9 | M1 과 같은 9건(거부와 accepted 가 함께 생김) |
| M9 R-U1-1 재실행: `Proposal.intent` 기본값 → `"query"`(U1 M1) | `types.py` 필드 기본값 | FAIL 42 / 128 | `test_agent_gate.py` 25 · `test_agent_loop.py` 9 · `test_agent_query_gate.py` 6 · `test_agent_query_types.py` 2 · `test_api_chat.py`·`test_api_answers_resume.py` 0. §4 |

검출 13 / 동등 2 (M2a·M4). 동등 변이 2건은 테스트 공백이 아니다 — 둘 다 어떤 입력으로도 출력이 달라지지 않는 코드 구조(§4)라 어떤 테스트도 잡을 수 없다. 생존 변이(출력이 달라지는데 테스트가 통과) 없음.

## 4. 계획 불일치·메모 판정

### 4a. 01-plan 99행 변이 표 2번째 — "Q 를 ② 앞으로 → `test_query_turn_search_person_stays_not_callable` FAIL" 은 성립하지 않는다(동등 변이)

- 재현(§3 M2a): Q 블록을 ② 앞에 둬도 60 passed. 구현자 증거 `…-0811-u2-mutation.txt` `M2-Q-before-2` 도 `28 passed` 로 같다.
- 왜 그런가(코드 읽기): Q 의 조건은 `name in WRITE_TOOLS` 이고 `WRITE_TOOLS ∩ NOT_CALLABLE_BY_LLM = ∅`(`WRITE_TOOLS == TOOL_NAMES − NOT_CALLABLE_BY_LLM`, 테스트가 등식으로 고정). `search_person` 은 `WRITE_TOOLS` 에 없으므로 Q 가 ② 앞에 있어도 Q 는 `search_person` 에 걸리지 않고 ② 가 잡는다. 즉 ② 와 Q 는 서로 배타적인 이름 집합을 보기 때문에 두 검사의 순서는 어떤 입력에서도 관측되지 않는다. 메인 세션 추정이 맞다.
- "`search_person` 은 ② 사유를 유지한다"(D16 결정 2) 라는 의도는 순서가 아니라 집합의 서로소성이 지킨다. 그것을 깨는 변이는 "Q 의 조건을 넓히는 것" 이고, M2a2(조건을 `name in TOOL_NAMES` 로 + ② 앞)와 구현자의 `M2b-Q-before-2-and-all-tools` 가 그것이며 둘 다 `test_query_turn_search_person_stays_not_callable` + `…not_callable_tools_keep_reason[3]` 4건 FAIL 로 잡힌다. V7(`WRITE_TOOLS` 에 `search_person` 추가, Q 는 제자리)은 집합 등식 1건만 잡는데, 그 변이에서도 ② 가 먼저라 `search_person` 의 사유는 안 바뀐다 — 순서 ②→Q 가 실제로 일을 하는 유일한 경우가 이 V7 이고, 그때 결과를 지키는 것은 순서다. 그러니 결정 B-2 "② 다음" 은 집합이 잘못 넓어졌을 때의 2중 안전장치로서 뜻이 있고, 변이 표 문구만 틀렸다.
- 계약 위반인가: 아니다. 코드는 결정 B-2 ①②Q④③⑤ 그대로이고(§1), 변이 표(테스트가 잡아야 할 것)의 2번째 서술이 동등 변이를 적은 것뿐이다.
- 01-plan 99행 수정안(verifier 는 계획 문서를 고치지 않는다 — 메인 세션 판단): "Q 를 ② 앞으로 → `test_query_turn_search_person_stays_not_callable` FAIL" 을 다음으로 바꾼다. "Q 를 ② 앞으로 옮기기만 하면 동등 변이(`search_person ∉ WRITE_TOOLS` 라 ② 와 Q 가 보는 이름 집합이 서로소 — 보고에 그렇게 적는다). ② 사유 유지를 깨는 변이는 Q 조건을 `name in TOOL_NAMES` 로 넓히고 ② 앞에 두는 것 → `test_query_turn_search_person_stays_not_callable`·`test_query_turn_not_callable_tools_keep_reason[3]` FAIL / `WRITE_TOOLS` 에 `search_person` 추가 → `test_write_tools_equals_tool_names_minus_not_callable` FAIL / Q 를 ④ 뒤로 → `test_query_turn_update_person_with_person_id_is_query_reason` FAIL".

### 4b. 01-plan 99행 4번째 — `intent != "record"` 동등 변이

재현(§3 M4): 60 passed. `INTENTS == ("record","query")` 두 값뿐이고 `validate_proposal` 이 enum 밖 값을 `JudgeUnavailable("schema")` 로 막아(U1 리뷰 §1) `Proposal.intent` 에는 두 값만 들어온다 → `!= "record"` ≡ `== "query"`. 계획이 "영향 없음(동등 변이)" 로 적은 그대로다.

### 4c. R-U1-1 메모(01-plan 94행 "U2 뒤 M1 재실행") — 닫을 근거

- U1 리뷰 §4 에서 "기존 기록 턴 테스트 다수 FAIL 은 게이트가 `intent` 를 읽는 U2 뒤에야 성립" 이라고 적었다. 재실행(§3 M9): 이제 42 FAIL — `test_agent_gate.py` 32건 중 25(`Proposal(tool_calls=…)` 를 직접 만드는 기록 턴 테스트가 전부 Q 에서 `query_turn_no_write` 로 거부됨, `test_all_rejection_reasons_are_in_vocabulary` 포함) · `test_agent_loop.py` 16건 중 9(기록 0 → `person_id` 매핑·되묻기 선택지·재개 context 없음) · 신규 `test_agent_query_gate.py` 6(`test_record_turn_*` 대조군 전부) · `test_agent_query_types.py` 2(U1 리뷰 M1 과 같은 2건).
- `test_api_chat.py`·`test_api_answers_resume.py` 는 0 FAIL — 이 파일들은 `FakeProposer` → `validate_proposal()` 경로를 지나고 거기서 `intent` 가 항상 명시 전달되므로(U1 리뷰 §4) dataclass 기본값이 보이지 않는다. 이것은 U1 리뷰의 분석과 정합한다.
- 결론: 01-plan 94행의 괄호 메모는 닫을 수 있다 — "U2 이후 `Proposal.intent` 기본값 변이는 기록 턴 테스트 42건(gate 25·loop 9·query_gate 6·query_types 2)으로 잡힌다". 04-review 가 R-5 와 함께 적으면 된다(§7 R-U2-5).

## 5. `tests.md`·`registry.md`·테스트가 실패 조건을 검사하는가

- `tests.md` U2 절 표 18행 ↔ `--collect-only` 28건(함수 18 + `rejects_write_tools` 3 + `not_callable_tools_keep_reason` 2 + `record_turn_write_tools_keep_old_verdict` 3 + `record_turn_not_callable_tools_keep_reason` 2): 이름 집합 `diff` → `SAME`. 헤더 "신규 28건 = 함수 17개" 의 17 은 18 이 맞다(위임 프롬프트도 17 이라 적었다 — §7 R-U2-4). "28 passed"·"2010 passed, skip 0"·검출 변이 `U2-M1/M2b/M2c/M3`·"첫 실행 1 failed — 테스트 작성 실수(`FakeProposer.table` 값에 `ToolCallProposal` 을 넣음)" 는 구현 증거 `…-0810-u2-gate.txt`(`TypeError: 'ToolCallProposal' object is not iterable`, `propose.py:603`)·`…-gate-rerun.txt`·`…-0812-u2-final-*` 및 내 재실행과 일치. 첫 실패는 제품 코드가 아니라 테스트 입력 모양의 실수이고 수정 뒤 제품 diff 는 없다(`-final-gate` 와 `-gate-rerun` 이 같은 3571바이트).
- 01-plan 97행 테스트 목록 8항목 ↔ 28건: 기록 툴 4종 → 새 사유(4 + `rejects_create_person`) / `search_person`·`ask_user`·`get_briefing` → ② 그대로(3 + `search_person_stays`) / 7종 밖 → `unknown_tool` / `update_person(person_id=3)` → 새 사유(순서) / `accepted == []` 항상(`never_accepts_anything` 8건 섞음 + 모든 조회 턴 테스트가 단언) / 기록 턴 같은 제안 → 기존 판정(4 + 3 + 명시 record = 기본) / `WRITE_TOOLS` 등식 / 프롬프트 (i)(ii)(iii) — 전부 덮인다. 계획에 없는 추가 단언 3개(`GATE_REJECTION_REASONS` 길이 7·끝자리, ⑤ 상한이 조회 턴에 `limit` 를 내지 않음·`stop_reason None`, `FakeProposer(intents=…)` 경유)는 결정 B-1·B-2 "조회 턴에서 `accepted` 는 항상 빈 목록" 의 직접 번역이라 범위 초과 아님.
- 테스트가 실제로 실패 조건을 검사하는가: M1(Q 제거)·V11(`continue` 제거)에서 9건, V6(사유 오타)에서 5건이 FAIL — 조회 턴 테스트가 "거부됐다" 뿐 아니라 "사유 값이 글자 그대로 `query_turn_no_write` 이고 accepted 가 비었다" 를 단언한다. 항상 통과하는 테스트는 없다(§3 에서 변이마다 다른 부분집합이 FAIL).
- `app.tools.*` 스파이 호출 0 단언(위임 7번): `_spy_all()`(77~92행)이 `TOOL_NAMES` 7종을 `functools.wraps` 로 감싸 `monkeypatch.setattr(app_tools, name, …)` 하고 `called == []` 를 단언한다 — `test_query_turn_rejects_write_tools[4]`·`…rejects_create_person`·`…not_callable_tools_keep_reason[3]`·`…unknown_tool_stays_unknown` 4함수 9건. 조회 턴 테스트 중 `…search_person_stays_not_callable`·`…update_person_with_person_id_is_query_reason`·`…never_accepts_anything`·`…has_no_limit_rejection…`·`…via_fake_proposer` 5함수는 스파이가 없다(01-plan 97행 "전부 `_spy` 류로" 와 글자 그대로는 다름 — §7 R-U2-3). 실질 공백은 아니다: 같은 제안 모양이 스파이 있는 테스트에서 호출 0 으로 확인되고, `check()` 는 `app_tools` 의 `TOOL_NAMES`·시그니처만 읽는 순수 함수이며(기준 `8a8767b` 의 `test_agent_gate.py` 32건이 스파이 7종으로 고정), U2 추가 줄 37줄에 `app_tools.<툴>(` 호출은 없다(grep-constraints 패턴 1·2 0건 + diff 전문 §2).
- `registry.md`: 비고 2곳(`propose.py` 행 "P5b U2(해시 pending)": 의도 분류·예외 두 문장 "절대 제안하지 마라." 바로 뒤·자신 지칭 제외·기존 문장 무삭제 / `gate.py` 행: Q 관문·①②Q④③⑤·`WRITE_TOOLS` 4종 = `TOOL_NAMES − NOT_CALLABLE_BY_LLM`·`REASON_QUERY_TURN_NO_WRITE="query_turn_no_write"` 7번째·재export) + 새 행 1(`tests/test_agent_query_gate.py`, 28건, pending, "툴 스파이로 호출 0 확인"). 내용이 §1 의 코드·직접 확인 값과 맞다. `__init__.py` 행에는 U2 비고가 없고 `gate.py` 행에 "`app/agent/__init__.py` 재export 추가" 로 적혀 있다 — 찾을 수 있으니 문제 삼지 않는다. 커밋 뒤 해시 치환은 메인 세션 몫.

## 6. 범위·원칙

- 범위: `app/` 변경 3파일이 01-plan 95~96행이 지정한 `gate.py`·`propose.py` + 재export. `app/er`·`app/tools`·`app/api`·`app/briefing`·`app/db`·`app/memory`·`alembic`·`web` diff 0. 기존 테스트 파일 수정 0. `loop.py`·`respond.py`·`types.py`·`settings.py` 는 U2 에서 손대지 않음(`git diff --name-only HEAD -- app` 3개). "하지 않는 것" — 루프 분기(U4)·답 생성(U3)·`mentions` 필드(결정 B-3 (a) 기각) 전부 없음: `PROPOSAL_SCHEMA` diff 0(propose.py 변경은 system 문자열 10줄뿐), `loop.py` diff 0.
- 원칙1·2·4: 확신도·임계치·ER 단계 무관 — 추가 줄에 `confidence`/`T_merge`/`T_new` 0, `app/er` diff 0. Q 는 ER 결과를 읽지 않는다.
- 원칙7: 프롬프트 추가 문장 3개는 의도 분류·언급 표기·자신 지칭 제외뿐 — 평가·조언·감정 문장 0. 조회 턴 기록 0(D16 결정 6)을 게이트가 코드로 강제.
- 원칙9: 새 사유가 `GATE_REJECTION_REASONS` 어휘에 들어가 `loop_gate.output.rejected[].reason` 으로 남을 재료(D16 "코드에서 지켜야 할 것" 2 "사유를 `loop_gate` trace 에 남긴다" — trace 에 실제로 실리는 것은 기존 `loop_gate` 래퍼 그대로이고 U4 가 조회 분기에서 같은 래퍼를 쓰는지는 U4 리뷰 몫).
- 툴 시그니처 v2·스키마 v2 무변경(`tools_check` 7/7, `alembic` diff 0, `NOT_CALLABLE_BY_LLM`·`INJECTED_ARGS` 기준과 동일).
- security: 추가 줄·프롬프트에 키·환경변수 이름 0, `.env` 미독. 증거 파일은 전부 `save_evidence.py`(비밀 검사 통과). 변이는 스크래치패드 사본에서만.
- 동결·활성: 활성 패키지 P5b-query-turn(`fe4a99e`), U1 커밋 `1dccb95` 위의 두 번째 단위.

## 7. 소견

[필수] 없음.

[권고] (커밋을 막지 않음)

- R-U2-1 · 01-plan 99행 변이 표 2번째 "Q 를 ② 앞으로 → `test_query_turn_search_person_stays_not_callable` FAIL" 은 동등 변이라 성립하지 않는다(§3 M2a 60 passed, 구현자 `M2-Q-before-2` 28 passed). 이유: `WRITE_TOOLS ∩ NOT_CALLABLE_BY_LLM = ∅` 라 ② 와 Q 의 순서는 관측 불가. 계약 위반 아님. 수정안은 §4a 끝 문장(Q 조건을 `TOOL_NAMES` 로 넓히고 ② 앞 → 4건 FAIL / `WRITE_TOOLS` 에 `search_person` 추가 → 집합 등식 FAIL / Q 를 ④ 뒤로 → 순서 테스트 FAIL). 계획 문서 수정은 메인 세션 판단.
- R-U2-2 · `app/agent/gate.py` 284행 절 주석 `# check() -- ①②④③⑤ 를 순서대로 적용하는 게이트 본체` 와 293행 `check()` docstring "적용 순서는 모듈 docstring 의 ①②④③⑤ 그대로다" 가 Q 를 반영하지 않는다(모듈 docstring 20행만 ①②Q④③⑤). 동작 무관·테스트 무관. 01-plan 96행은 "모듈 docstring '적용 순서' 절에 Q 를 더한다" 만 요구했으므로 계약 위반은 아니나, 다음 사람이 293행만 읽으면 Q 를 놓친다. 이번 커밋에 넣을지 U4 에서 같이 고칠지는 메인 세션 판단(backend-agent 몫, 두 줄).
- R-U2-3 · 01-plan 97행 "전부 `_spy` 류로 `app.tools.*` 호출 0 확인" 대비 조회 턴 테스트 5함수(`…search_person_stays_not_callable`·`…update_person_with_person_id_is_query_reason`·`…never_accepts_anything`·`…has_no_limit_rejection_and_no_limit_stop`·`…via_fake_proposer`)에 스파이가 없다(§5). 같은 제안 모양이 스파이 있는 9건에서 호출 0 이고 `check()` 는 순수 함수라 실질 공백은 아니다. 04-review 에서 `tests.md`·registry 의 "툴 스파이로 호출 0 확인" 을 "조회 턴 기록 툴·내부 전용 툴·미지 툴 9건에서" 로 읽으면 된다. 테스트에 `_spy_all` 한 줄씩 더하는 것은 선택.
- R-U2-4 · `tests.md` U2 절 헤더 "신규 28건 = 함수 17개" → 18개(수집 28 = 18 + parametrize 10, 표 18행과 수집 이름 1:1 `SAME`). 위임 프롬프트의 "함수 17" 도 같은 오기. 메인 세션이 `tests.md` 한 글자 고칠 것(verifier 는 고치지 않는다).
- R-U2-5 · 03-log U2 항목에 적을 것(메인 세션). ① R-U1-1 닫힘 — `Proposal.intent` 기본값 변이가 U2 이후 42 FAIL(gate 25·loop 9·query_gate 6·query_types 2, api 0 — `validate_proposal` 경로는 기본값을 안 본다)(§4c). ② 동등 변이 2건(M2a·M4)과 검출 13건(§3). ③ 첫 실행 1 failed 는 테스트 입력 실수(`FakeProposer.table` 값 모양), 제품 diff 없음. ④ `registry.md` 해시 pending 3곳 치환. ⑤ R-4 ⑤ 는 `--include='*.py'` 로 세어야 기준 19 와 같다(`.pyc` 가 섞이면 22). Refs `P5b-query-turn CR-004 D16 S3.2 원칙1 원칙4 원칙7 원칙9 R19`.

## 8. 판정

통과. U2 의 계약 전부 — `WRITE_TOOLS`(`frozenset`, `TOOL_NAMES − NOT_CALLABLE_BY_LLM` 등식)·`REASON_QUERY_TURN_NO_WRITE = "query_turn_no_write"`(`GATE_REJECTION_REASONS` 7번째, 앞 6개 순서 불변)·`check()` 순서 ①②Q④③⑤(`person_id` 보다 먼저, `search_person`·`ask_user`·`get_briefing` 은 ② 사유 그대로, 조회 턴 accepted 항상 `[]`)·시그니처 무변경·기록 턴 판정이 기준 `8a8767b` 모듈과 동일·프롬프트 (i) 뜻 보존(어미만 다듬음)·(ii) 두 문장 글자 그대로 "절대 제안하지 마라. " 바로 뒤 인접·(iii) 글자 그대로·기존 system 문장 유실 0·재export 2 — 가 01-plan 95~98행·결정 B 확정 칸·D16 결정 2·6·7·"코드에서 지켜야 할 것" 2 와 맞고, 내 재실행에서 28 passed·R-5 184 passed·전체 2010 passed(1982 + 28)·skip 0·ruff 통과·`tools_check` 7/7 이다. 변이 15건 중 13 검출, 동등 변이 2(M2a·M4)는 코드 구조상 관측 불가라 테스트 공백이 아니다(계획 표 2번째 문구만 틀림 — R-U2-1). R-U1-1 메모는 M9 42 FAIL 로 닫힌다. 기존 테스트 파일 수정 0, 범위 밖 diff 0, 구현 제약 (1)~(5)·비밀 0(테스트 파일의 `test_query_turn_rejects_create_person(` 1건은 계획 지정 이름). 코드에 요구하는 변경은 없다(권고 R-U2-2 두 줄 주석은 선택). 커밋·승인은 메인 세션·사용자 몫이다.
