# P5b-query-turn — 테스트 기록

테스트 1건 = 표 1줄. 증거: `evidence/20261029-1206-u1-types.txt`(파일 24 passed), `evidence/20261029-1206-u1-pytest-all.txt`(전체 1982 passed, skip 0; 기준선 1958 → +24), 변이 `evidence/20261029-1206-u1-mutation.txt`.

## tests/test_agent_query_types.py — U1 계약 (신규 24건 = 함수 18개, 그중 1개가 파라미터 7건)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_types.py -v` → 24 passed.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_types.py::test_intents_values | 의도 어휘 값 | `INTENT_RECORD=="record"`, `INTENT_QUERY=="query"`, `INTENTS==("record","query")` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_schema_intent_enum | 스키마 최상위 키·intent enum | 키 집합 == `{"tool_calls","intent"}`, `intent == {"type":"string","enum":["record","query"]}` | 통과 · U1-M2(enum 에서 query 제거 → 실패) | 기록 없음 |
| test_agent_query_types.py::test_schema_required_unchanged | `required` 무변경 | `required == ["tool_calls"]` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_schema_tool_calls_embeds_arg_schema | tool_calls 원소 스키마 불변 | `items.properties.args is PROPOSAL_ARG_SCHEMA`, `items.required == ["name","args"]` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_validate_proposal_missing_intent_is_record | intent 키 없음 → record | `{"tool_calls": []}` → `intent == "record"` | 통과 · (validate 쪽 기본값을 query 로 바꾸는 변이를 잡는다; 계획 변이 M1 은 dataclass 기본값이라 아래 두 테스트가 잡음) | 기록 없음 |
| test_agent_query_types.py::test_validate_proposal_null_intent_is_record | intent `null` → record | `{"tool_calls": [], "intent": None}` → `"record"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_validate_proposal_query_intent | query 통과 | `"intent":"query"` → `"query"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_validate_proposal_record_intent | record 통과 | `"intent":"record"` → `"record"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_validate_proposal_bad_intent_is_schema_error[7건] | enum 밖·잘못된 타입 | `"ask"`·`""`·`"QUERY"`·`1`·`True`·`["query"]`·`{"a":1}` → `JudgeUnavailable`, 메시지 `"schema"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_proposal_default_intent_is_record | dataclass 기본값 | `Proposal().intent == "record"` | 통과 · U1-M1(기본값 query → 실패) | 기록 없음 |
| test_agent_query_types.py::test_proposal_to_dict_always_has_intent | `to_dict` 가 항상 intent 를 싣음 | `Proposal().to_dict()["intent"]=="record"`, `Proposal(intent="query")` → `"query"` | 통과 · U1-M1 | 기록 없음 |
| test_agent_query_types.py::test_pending_resume_query_to_dict_has_intent | query 일 때 키를 싣음 | `PendingResume(intent="query").to_dict()["intent"]=="query"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_pending_resume_default_omits_intent | 기본값이면 키 없음 | `PendingResume().intent=="record"`, `"intent" not in to_dict()` | 통과 · U1-M3(항상 싣기 → 실패) | 기록 없음 |
| test_agent_query_types.py::test_pending_resume_version_stays_one | version "1" 유지 | `LOOP_RESUME_VERSION=="1"`, `to_dict()["version"]=="1"` | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_step_loop_query_outside_trace_steps | trace 어휘 | `STEP_LOOP_QUERY=="loop_query"`, `loop_` 접두사, `LOOP_TRACE_STEPS` 밖 | 통과 · U1-M4(튜플에 추가 → 이 테스트와 `test_agent_types.py::test_loop_trace_steps_are_fixed_six_in_order` 실패) | 기록 없음 |
| test_agent_query_types.py::test_fake_proposer_intents_table | 표에 있는 발화만 intent 전달 | `FakeProposer(table={"u":[]}, intents={"u":"query"})` → `u` 는 query, 다른 발화는 record | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_fake_proposer_without_intents_is_record | 기존 호출 호환 | `FakeProposer(table={"u":[]})` → record | 통과 · — | 기록 없음 |
| test_agent_query_types.py::test_query_constants_values | 상수 값 | 5 · 1 · 3 · 240, 240 == 3 × `BRIEFING_SUGGESTION_MAX_CHARS`, `QUERY_MORE_HINT` 는 settings 에 없음(U3 몫) | 통과 · — | 기록 없음 |

## tests/test_agent_query_gate.py — U2 게이트 Q 관문·프롬프트 (신규 28건 = 함수 18개, 파라미터 포함)

증거: `evidence/20261102-0810-u2-gate-rerun.txt`(28 passed), `evidence/20261102-0810-u2-pytest-all.txt`(전체 2010 passed, skip 0), 변이 `evidence/20261102-0811-u2-mutation.txt`·`evidence/20261102-0811-u2-mutation-extra.txt`. `u2-gate.txt` 는 첫 실행(1 failed — 테스트 작성 실수: `FakeProposer.table` 값이 dict 인데 `ToolCallProposal` 을 넣음)이며 테스트를 고친 뒤 rerun 으로 28 passed.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_gate.py::test_reason_value_and_vocabulary_order | 사유 값·어휘 끝자리 | `"query_turn_no_write"`, `GATE_REJECTION_REASONS` 7개 끝이 새 사유 | 통과 · — | 기록 없음 |
| test_agent_query_gate.py::test_write_tools_equals_tool_names_minus_not_callable | 기록 툴 집합 등식 | `WRITE_TOOLS == TOOL_NAMES - NOT_CALLABLE_BY_LLM` == 4종 | 통과 · U2-M3 | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_rejects_write_tools (4건: add_event·add_schedule·update_person·create_person) | 조회 턴 기록 툴 거부 | 각각 → rejected 1건 사유 새 사유, accepted 비어 있음, 툴 호출 0 | 통과 · U2-M1(4건 모두)·U2-M3(create_person) | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_rejects_create_person | 변이 표 지정 이름 | create_person 제안 → 새 사유 | 통과 · U2-M1·U2-M3 | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_not_callable_tools_keep_reason (3건: search_person·ask_user·get_briefing) | ② 사유 유지 | 조회 턴 → `not_callable_by_llm`, 호출 0 | 통과 · U2-M2b | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_search_person_stays_not_callable | 변이 표 지정 이름 | search_person → `not_callable_by_llm` ≠ 새 사유 | 통과 · U2-M2b | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_unknown_tool_stays_unknown | ① 사유 유지 | 7종 밖 이름 → `unknown_tool`, 호출 0 | 통과 · — | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_update_person_with_person_id_is_query_reason | Q 가 ④ 앞 | person_id 낀 update_person → 새 사유 | 통과 · U2-M1·U2-M2c | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_never_accepts_anything | 조회 턴 accepted 항상 [] | 8종 섞어 → accepted [], rejected 8 | 통과 · U2-M1·U2-M3 | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_has_no_limit_rejection_and_no_limit_stop | ⑤ 상한 영향 없음 | 상한 1 인 GateConfig 에서 `limit` 사유 0, `stop_reason is None` | 통과 · U2-M1 | 기록 없음 |
| test_agent_query_gate.py::test_query_turn_via_fake_proposer | FakeProposer 경유 | intents query → `Proposal.intent=="query"`, add_event → 새 사유 | 통과 · U2-M1 | 첫 실행 실패(테스트 작성 실수, 수정) |
| test_agent_query_gate.py::test_record_turn_default_intent_is_record | 기본값 record | `Proposal(...).intent=="record"` | 통과 · U1-M1 | 기록 없음 |
| test_agent_query_gate.py::test_record_turn_write_tools_keep_old_verdict (4건) | 기록 턴 대조군 | add_event·add_schedule·update_person → execute, create_person → hint_only, 거부 0 | 통과 · U1-M1 | 기록 없음 |
| test_agent_query_gate.py::test_record_turn_not_callable_tools_keep_reason (3건) | 기록 턴 ② 그대로 | → `not_callable_by_llm` | 통과 · — | 기록 없음 |
| test_agent_query_gate.py::test_record_turn_explicit_record_intent_same_as_default | 명시 record = 기본 | `check()` 결과 동일 | 통과 · U1-M1 | 기록 없음 |
| test_agent_query_gate.py::test_prompt_has_intent_classification_sentence | (i) 의도 분류 문장 | system 에 "intent 를 query"·"record"·"둘이 섞이면 query" | 통과 · — | 기록 없음 |
| test_agent_query_gate.py::test_prompt_has_query_mention_exception_sentences_after_old_sentence | (ii) 예외 두 문장 글자 그대로·바로 뒤 | 기존 "절대 제안하지 마라." 뒤 한 칸 띄고 바로 이어짐 | 통과 · — | 기록 없음 |
| test_agent_query_gate.py::test_prompt_excludes_self_reference | (iii) 사용자 자신 지칭 제외 | "'나'·'저'·'내'·'제'", "사용자 자신을 가리키는 말은 인물로 제안하지 마라" | 통과 · — | 기록 없음 |
