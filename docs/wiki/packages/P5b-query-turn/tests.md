# P5b-query-turn — 테스트 기록

테스트 1건 = 표 1줄. 증거: `evidence/20261029-1206-u1-types.txt`(파일 24 passed), `evidence/20261029-1206-u1-pytest-all.txt`(전체 1982 passed, skip 0; 기준선 1958 → +24), 변이 `evidence/20261029-1206-u1-mutation.txt`.

**단위별 건수 합계 (U6 완성)**: U1 24 + U2 28 + U3 71 + U4 23 + U5 10 + U6 8 = **164건**(신규 테스트 파일 5개). 전체 `pytest tests/ -q -rs`: 기준선 1958 → **2122 passed, skip 0**(`evidence/20261102-1452-u6-pytest-all.txt`).

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

## tests/test_agent_query_answer.py — U3 조회 답 생성기·검증기·템플릿 (신규 71건 = 함수 48개, 파라미터 포함)

증거: `evidence/20261102-0856-u3-answer.txt`(71 passed), `evidence/20261102-0856-u3-pytest-all.txt`(전체 2081 passed, skip 0; 기준선 2010 → +71), 변이 `evidence/20261102-0857-u3-mutation.txt`(M1~M7). 첫 실행에서 전부 통과(실패 이력 없음). 변이 번호는 U3-M1~M7.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_answer.py::test_forbidden_expression_list_has_fourteen | 금지 표현 목록 크기 | `len(BRIEFING_FORBIDDEN_EXPRESSIONS)==14` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_validate_rejects_each_forbidden_expression (14건) | 금지 표현 14개 각각 | `"그분은 {bad} 같아요."` → `"forbidden_expression"` | 통과 · U3-M1(14건 모두) | 기록 없음 |
| test_agent_query_answer.py::test_validate_normal_answer_passes | 정상 답 | → `None` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_validate_line_limit_boundary_three_lines_pass_four_rejected | 줄 수 경계 | 3줄 `None`, 4줄 `"too_many_lines"` | 통과 · U3-M3 | 기록 없음 |
| test_agent_query_answer.py::test_validate_blank_lines_do_not_count | 공백 줄 불산입 | 빈 줄 섞인 3줄 → `None` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_validate_char_limit_boundary_240_pass_241_rejected | 글자 수 경계 | 240자 `None`, 241자 `"too_long"` | 통과 · U3-M2 | 기록 없음 |
| test_agent_query_answer.py::test_validate_char_count_uses_stripped_text | strip 후 글자 수 | 앞뒤 공백 붙은 240자 → `None` | 통과 · U3-M2 | 기록 없음 |
| test_agent_query_answer.py::test_validate_empty_or_blank_is_empty (3건) | 빈/공백 | `""`·`"   "`·`"\n \n"` → `"empty"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_validate_order_lines_before_length_before_forbidden | 검사 순서 | 금지어+4줄 → `too_many_lines`, 금지어+241자 → `too_long` | 통과 · U3-M3 | 기록 없음 |
| test_agent_query_answer.py::test_template_with_evidence_exact_string_and_last_contact_in_user_timezone | 템플릿 근거 있음 정확한 문자열 | UTC 10-20 16:30 → 서울 `10월 21일`, 1건 | 통과 · U3-M5 | 기록 없음 |
| test_agent_query_answer.py::test_template_count_is_facts_plus_patterns | n = 사실+패턴 | 사실 2+패턴 1 → `알고 있는 것 3건` | 통과 · U3-M6 | 기록 없음 |
| test_agent_query_answer.py::test_template_without_last_contact_exact_string | `last_contact_at` 없음 정확한 문자열 | 타임라인만 → `마지막 접촉 기록 없음, 알고 있는 것 0건` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_template_no_evidence_exact_string_even_with_last_contact | 근거 0건 정확한 문자열 | → `…동로 기억하고 있어요. 그 밖의 기록은 아직 없어요.` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_has_evidence_true_for_each_source (4건) | 사실·패턴·타임라인·일정 각각 근거 | → `True` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_template_outputs_pass_validator | 폴백이 다시 걸리지 않음 | 템플릿 3종 → `validate_query_answer` `None` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_no_record_reply_exact_strings | 기록 없음 문구 | 1개/2개 정확한 문자열 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_no_record_reply_keeps_input_order | 입력 순서 유지 | `["나","가","다"]` 그대로 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_no_mention_reply_exact_string | 언급 0개 문구 | 정확한 문자열 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_hint_constants_exact_values | 힌트 상수 | `QUERY_ONE_AT_A_TIME_HINT`·`QUERY_MORE_HINT` 값 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_prompt_system_exact_sentences | E-6 system 글자 그대로 | 원칙7 구절 포함 전문 일치 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_prompt_user_text_has_question_now_and_evidence_values | user_text 근거 값 | 질문 1건·`now` 서울 오프셋·이름·관계·별칭·날짜·사실·패턴·타임라인·일정 | 통과 · U3-M5 | 기록 없음 |
| test_agent_query_answer.py::test_prompt_excludes_raw_ids_and_secrets | 원문·id·키 미포함 | `절대노출금지`·`raw_utterance`·id 3종·`source_count`·`briefed_at`·환경변수명 없음 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_prompt_timeline_limit_keeps_only_first_five | 타임라인 5건 상한 | 6건 입력 → 1~5 있음·6 없음 | 통과 · U3-M4 | 기록 없음 |
| test_agent_query_answer.py::test_prompt_last_contact_date_in_user_timezone_not_utc | 프롬프트 날짜 사용자 시간대 | `10월 21일` 있고 `10월 20일` 없음 | 통과 · U3-M5 | 기록 없음 |
| test_agent_query_answer.py::test_query_answer_trace_tokens_shape | `trace_tokens()` 모양 | `(3, 4)` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_fake_answerer_table_and_default_and_call_count | Fake 표·기본값·호출 수 | 표 키 → 답, 없으면 `""`, `fake`, 토큰 0, `call_count==2` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_fake_answerer_fail_raises_judge_unavailable_and_counts | Fake `fail` | `JudgeUnavailable("timeout")`, `call_count==1` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_schema_and_tool_name_exact_values | 스키마·도구 이름 값 | `report_query_answer`, `{answer}`·`required`·`additionalProperties False` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_request_forces_tool_choice_and_schema | Claude 요청 본문 | `tool_choice`·`tools` 값, 질문 포함, 키·환경변수명 없음 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_parses_text_and_usage | Claude 응답 파싱 | 텍스트·`(5,7)`·`anthropic` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_no_tool_use_is_schema_error | tool_use 없음 | `JudgeUnavailable("schema")` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_non_string_answer_is_schema_error_not_empty (4건) | answer 비문자열 | 123·None·키 없음·다른 키 → `"schema"` | 통과 · U3-M7 | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_empty_string_answer_passes_through_for_validator | 빈 문자열은 검증기 몫 | `text==""`, 검증기 `"empty"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_maps_timeout_error | Claude timeout 매핑 | → `"timeout"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_maps_rate_limit_error | Claude rate_limit 매핑 | → `"rate_limit"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_claude_answerer_default_model_follows_env_and_reuses_judge_timeout | 모델 env·타임아웃 재사용 | `ANTHROPIC_MODEL`, `ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_openai_answerer_request_and_parse | OpenAI 요청·파싱 | `tool_choice`·`parameters`, 텍스트·`(5,6)`·`openai` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_openai_answerer_no_tool_calls_is_schema_error | tool_calls 없음 | → `"schema"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_openai_answerer_non_string_answer_is_schema_error | answer 비문자열 | → `"schema"` | 통과 · U3-M7 | 기록 없음 |
| test_agent_query_answer.py::test_openai_answerer_maps_timeout_and_connection_errors | OpenAI 오류 매핑 | → `"timeout"`·`"connection"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_openai_answerer_maps_rate_limit_error | OpenAI rate_limit | → `"rate_limit"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_gemini_answerer_requires_model_env | `GEMINI_MODEL` 필수 | → `InvalidValue` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_gemini_answerer_request_uses_schema_and_parses | Gemini 스키마·파싱 | `_to_gemini_schema` 일치, 텍스트·`(7,8)`·`gemini` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_gemini_answerer_bad_json_and_non_string_are_schema_errors | Gemini 스키마 위반 | JSON 아님·text 없음·answer 숫자 → `"schema"` | 통과 · U3-M7 | 기록 없음 |
| test_agent_query_answer.py::test_gemini_answerer_maps_rate_limit_and_timeout_errors | Gemini 오류 매핑 | 429 → `"rate_limit"`, ReadTimeout → `"timeout"` | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_query_answerers_registry_has_three_providers | 등록표 | 키 집합 3종 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_answerer_from_env_follows_llm_provider (3건) | `LLM_PROVIDER` 선택 | anthropic/openai/gemini → 해당 클래스 | 통과 · — | 기록 없음 |
| test_agent_query_answer.py::test_answerer_from_env_unknown_and_disabled_rejected | 미지·비활성 거부 | → `InvalidValue` | 통과 · — | 기록 없음 |

## tests/test_agent_query_loop.py — U4 루프 조회 분기 (신규 23건)

증거: `evidence/20261102-1231-u4-loop.txt`(23 passed), `evidence/20261102-1231-u4-pytest-all.txt`(전체 2104 passed, skip 0; 기준선 2081 → +23), 변이 `evidence/20261102-1233-u4-mutation.txt`(M1~M14, 16건 전부 검출). 변이 번호는 U4-M1~M14(M3 = a·b, M4 = a·b).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_loop.py::test_a_merge_answers_from_card_and_writes_nothing | (a) merge → 카드 근거 답, 저장 0 | 시드 인물(타임라인 8·사실 3·일정 2) → 7개 테이블 행 수 불변, 기록 툴 `tool_call` 0, `get_person_card` 1회, evidence_counts `{3,0,5,2}`, user_text 타임라인 5줄·사실 3·일정 2, `er_resolve.decision.applied=false`, trace_ids 3개 | 통과 · U4-M1·M3a·M3b·M5·M9·M10 | 기록 없음 |
| test_agent_query_loop.py::test_b_new_person_asks_nothing_and_says_no_record | (b) 빈 DB new_person → 질문 0 | 행 수 불변, `ask_user` 행 0, reply == `no_record_reply(["김철수"])`, answerer 0회 | 통과 · U4-M2·M6·M9 | 기록 없음 |
| test_agent_query_loop.py::test_c_identity_asks_with_query_resume | (c) 후보 2명 identity | `pending_questions` +1(나머지 불변), `context.resume.intent=="query"`, `options` == ER `resolve()` 원본, stop_reason `ask_user`, answer_source `ask` | 통과 · U4-M11·M9 | 기록 없음 |
| test_agent_query_loop.py::test_d_forbidden_expression_falls_back_to_template | (d) 금지 표현 → 템플릿 | "힘들어 보여요" → reply == 템플릿, `fallback_reason=="forbidden_expression"`, `rejected_answer` == 원문 | 통과 · U4-M4b | 기록 없음 |
| test_agent_query_loop.py::test_e_answerer_unavailable_falls_back_without_raising | (e) `JudgeUnavailable("timeout")` | reply == 템플릿, `answerer_error:timeout`, `loop_error`·`tool_error` 행 0 | 통과 · U4-M4a | 기록 없음 |
| test_agent_query_loop.py::test_f_no_evidence_skips_llm | (f) 근거 0건 | `call_count==0`, `no_evidence`, evidence_counts 전부 0, 토큰 `(0,0)` | 통과 · — | 기록 없음 |
| test_agent_query_loop.py::test_g_mixed_utterance_does_not_execute_write | (g) 혼합 발화 | `add_event` 실행 0, 행 수 불변, `loop_gate.output.rejected` 에 `{index:1,name:add_event,reason:query_turn_no_write}` | 통과 · U4-M1 (※ 게이트가 이미 거부해 `_record` 호출 변이는 이 케이스가 아니라 `test_forbidden_callees_are_never_called` 가 잡는다) | 기록 없음 |
| test_agent_query_loop.py::test_h_trace368_title_then_me_resolves_first_only | (h) trace 368 — "박선우 과장님"+"나" | `resolve` 호출 `["박선우 과장님"]`, `mentions_dropped==1`, 저장 0, reply 끝 두 줄 = 한 사람씩 안내·`QUERY_MORE_HINT` | 통과 · U4-M9·M10·M13 | 기록 없음 |
| test_agent_query_loop.py::test_h2_me_first_asks_identity_and_stops | (h) 순서 반대 — "나" 가 먼저 | 후보가 있고 판정이 못 고르면 identity → 그 자리에서 되묻기, `resolve` `["나"]`, `ask` 에는 한 사람씩 안내 없음 | 통과 · U4-M14 | 첫 실행 실패: new_person 으로 가정했으나 후보가 있으면 `no_matched` 강제 identity(ER 정상 동작). 기대를 identity 로 고침(테스트 쪽 가정 오류) |
| test_agent_query_loop.py::test_h3_mention_source_rule | 언급 출처 규칙(결정 B-3 (b)) | `search_person.query`·그 밖 `person`, strip·빈 값 제외·중복 제거·순서 → `["가","나","다"]` | 통과 · — | 기록 없음 |
| test_agent_query_loop.py::test_i_m_no_mention | (i)(m) 언급 0 | reply == `no_mention_reply()`, `no_record_reply` 호출 0, `resolve` 0, answerer 0, `answer_source=="no_mention"` | 통과 · U4-M7 | 기록 없음 |
| test_agent_query_loop.py::test_j_record_turn_does_not_enter_query_branch | (j) 기록 턴 대조군 | `intent` 기본값 → `_run_query_turn` 스파이 0회, `stored.events==1`, `loop_query` 0행·`loop_record` 1행 | 통과 · U4-M9 대조 | 첫 실행 실패: 테스트 시드 별칭 `source="user"` 가 `ALIAS_SOURCES` 밖(`KeyError`) → `ALIAS_SOURCES[0]` 로 수정(테스트 쪽 오류) |
| test_agent_query_loop.py::test_k_loop_query_output_schema | (k) `loop_query.output` 키 집합 | 10키 정확히, `resolutions[]` 6키, `evidence_counts` 4키, `answer_source` 어휘, `tool_name=="agent"` | 통과 · U4-M9·M10 | 기록 없음 |
| test_agent_query_loop.py::test_k2_tokens_come_from_answer | `trace_tokens()` → tokens_in/out | 답 토큰 `(11,7)` → 행 `tokens_in==11, tokens_out==7` | 통과 · U4-M12 | 기록 없음 |
| test_agent_query_loop.py::test_l_raw_utterance_never_exposed | (l) R-U3-1 원문 비노출 | `raw_utterance="절대노출금지원문"` → reply·`loop_query.output` JSON·answerer 입력 user_text 어디에도 없음 | 통과 · — | 기록 없음 |
| test_agent_query_loop.py::test_n_more_hint_only_on_llm | (n) 결정 F 힌트 부착 | llm 답만 `QUERY_MORE_HINT` 1회로 끝남, 템플릿 reply == 템플릿(루프가 더 붙이지 않음), no_record 에는 없음 | 통과 · U4-M6·M4a | 기록 없음 |
| test_agent_query_loop.py::test_o_remaining_mentions_after_merge_are_not_resolved | (o) merge 뒤 남은 언급 | 언급 2개 → `resolve` `["팀장"]` 1회, `mentions_dropped==1`, reply 끝 두 줄 = 안내·`QUERY_MORE_HINT` | 통과 · U4-M10·M13 | 기록 없음 |
| test_agent_query_loop.py::test_p_mention_cap | (p) 언급 상한 | 언급 6개(전부 new_person) → `resolve` 정확히 앞 5개, `mentions_dropped==1`, 저장 0, reply == `no_record_reply(앞 5개)` + 안내 | 통과 · U4-M2·M6·M13 | 기록 없음 |
| test_agent_query_loop.py::test_q_answered_turn_stop_reason_is_none | (q) stop_reason | 답한 턴 `None`(`"limit"` 아님), reply 비지 않음 | 통과 · U4-M8·M10 | 기록 없음 |
| test_agent_query_loop.py::test_r_lazy_resolution_not_called_without_evidence | (r) `answerer=None` + 근거 0건 | `answerer_from_env` 스파이 0회(키 없이 통과), reply == 템플릿 | 통과 · U4-M6·M9 | 기록 없음 |
| test_agent_query_loop.py::test_s_lazy_resolution_uses_module_attribute | (s) `answerer=None` + 근거 있음 | `monkeypatch("app.agent.respond.answerer_from_env")` 가 효과 → llm 답 | 통과 · U4-M9 | 기록 없음 |
| test_agent_query_loop.py::test_forbidden_callees_are_never_called | 부정 — 조회 턴에서 부르지 않는 것 | `resolve_mentions`·`_record`·`_record_impl`·`after_record`·`apply_resolution`(merge)·`app_tools` 기록 툴 4종을 호출 시 예외로 치환 → 답이 정상 | 통과 · U4-M1·M5 | 기록 없음 |
| test_agent_query_loop.py::test_other_user_person_is_not_visible | 격리 | 다른 `user_id` 인물의 같은 별칭 → no_record, answerer 0 | 통과 · U4-M6·M9 | 기록 없음 |

## tests/test_agent_query_loop.py — U5 재개(조회 identity 되묻기 뒤 답하기) (추가 10건 = 함수 8개, 그중 2개가 파라미터 2건)

증거: `evidence/20261102-1328-u5-loop.txt`(33 passed = 23 + 10), `evidence/20261102-1328-u5-pytest-all.txt`(전체 2114 passed, skip 0; 기준선 2104 → +10), 변이 `evidence/20261102-1327-u5-mutation.txt`(M1~M15 전부 검출). 변이 번호는 U5-M1~M15.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_loop.py::test_t_resume_candidate_answer_replies_from_that_card_and_writes_nothing (2건: 김민수·김민호) | (t) 후보 답 → 그 인물 카드로 답, 저장 0 | 실제 조회 턴이 저장한 identity 행 → `answer_question`+`load_resume_input`+`resume_turn(answerer=)` → 7개 테이블 불변(`person_aliases` 포함), `update_person` `tool_call` 0·`apply_resolution`/`resolve`/`_followup_new_person_turn` 호출 0, reply == 답+`QUERY_MORE_HINT`, 답 생성기 입력에 고른 인물 이름만, `trace_ids==[resume,query]`, `loop_query`·`loop_turn` 각 +1, `loop_resolve_done`/`loop_record` 0, `resolutions[0]` 전체 값(`er_trace_id None`·`applied True`·`question_id`) | 통과 · U5-M1·M4·M5·M6·M14·M15 | 첫 실행 통과 |
| test_agent_query_loop.py::test_u_resume_reject_answer_says_no_record_and_asks_nothing | (u) 거절 답 → 후속 질문 0 | ER 부정 옵션 → `pending_questions` +0·행 수 불변·`_followup_new_person_turn` 0·reply == `no_record_reply(["팀장"])`·answerer 0·`answer_source=="no_record"`·`resolutions[0]` 전체 값(`person_id None`·`applied False`) | 통과 · U5-M3·M6·M15 | 기록 없음 |
| test_agent_query_loop.py::test_v_resume_without_intent_key_keeps_record_path | (v) 하위 호환 | 기록 턴이 만든 identity 행(`resume.intent` 키 없음) → `update_person` `tool_call` 1·`person_aliases` +1·`events` +1·`loop_query` +0·`loop_record` +1 | 통과 · U5-M2 | 첫 실행 실패: `loop_record` 총수 1 단언이 첫 턴 행을 못 셈 → 전후 차이 단언으로 수정 |
| test_agent_query_loop.py::test_w_other_kinds_ignore_intent (2건: new_person·schedule) | (w) 다른 kind 는 `intent` 무시 | context 에 `resume.intent="query"` 를 넣어도 `_resume_query_turn` 호출 0·`loop_query` 0·`loop_record` 1 | 통과 · U5-M7 | 기록 없음 |
| test_agent_query_loop.py::test_x_answer_is_stripped_but_rejected_answer_is_verbatim | R-U4-2 (x) | 앞뒤 공백 답 → reply 본문 strip+힌트·`rejected_answer None`; 금지 표현 답(앞뒤 공백) → `rejected_answer` 원문 그대로 | 통과 · U5-M9·M10 | 기록 없음 |
| test_agent_query_loop.py::test_y_person_not_found_on_card_read_says_no_record | R-U4-2 (y) | `get_person_card` → `PersonNotFound` → reply == `no_record_reply(["팀장"])`·`person_id None`·answerer 0 | 통과 · U5-M11 | 기록 없음 |
| test_agent_query_loop.py::test_z_merge_resolution_entry_carries_person_id | R-U4-2 (z) | merge 턴 `loop_query.resolutions[0]` `band=="merge"`·`person_id == person.id` | 통과 · U5-M12 | 기록 없음 |
| test_agent_query_loop.py::test_aa_db_errors_propagate_out_of_run_turn | R-U4-2 (aa) | 답 생성기·`get_person_card` 가 `SQLAlchemyError` → `run_turn` 밖으로 전파 | 통과 · U5-M13 | 기록 없음 |

## tests/test_api_chat_query.py — U6 HTTP 끝에서 끝 (신규 8건)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_chat_query.py -v` → 8 passed (`evidence/20261102-1452-u6-api.txt`). 변이: `evidence/20261102-1453-u6-mutation.txt`(저장소 밖 사본에서 M1~M5). 네트워크 0 — `get_proposer`→`FakeProposer(intents)`, `get_judge`→`FakeJudge`, 답 생성기는 `monkeypatch.setattr("app.agent.respond.answerer_from_env", …)`(결정 K, 라우트 무수정).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_api_chat_query.py::test_chat_query_merge_stored_zero_no_writes_and_trace | merge 조회 `POST /chat` 계약 전부 | 시드 인물(사실 3·이벤트 8·일정 2) + 조회 발화 → 200·`reply == 답 + "\n" + QUERY_MORE_HINT`·`stored=={0,0,0}`·`pending_question None`·7개 테이블 행 수 불변·기록 툴 `tool_call` 0·`loop_extract.intent=="query"`·`loop_gate`·`er_resolve`·`loop_query`·`loop_turn` 각 1행·`loop_record` 0·`evidence_counts=={facts:3,patterns:0,timeline:5,schedules:2}`·`er_resolve.decision.applied is False` | 통과 · U6-M1(진입 조건 `"Query"`)·U6-M2(stored 를 근거 건수로)·U6-M3(`answerer_from_env` 최상단 바인딩) | 첫 실행: `er["decision"]["decision"]` 키 없음(테스트 오타) → `q["resolutions"][0]["band"]` 로 수정 |
| test_api_chat_query.py::test_chat_query_identity_asks_then_answer_stored_zero_no_writes | identity 조회 → `POST /answers` 1요청 | 같은 별칭 인물 2명 + 판정 실패 → `stop_reason=="ask_user"`·kind identity·저장 0·answerer 0회 → 후보 답 → 200·reply 카드 기반·`stored` 0·`pending_question None`·행 수 불변(별칭 누적 없음)·`loop_query` 2행(ask·llm)·`person_id`==고른 인물·`loop_resume` 1·`loop_resolve_done`/`loop_record` 0 | 통과 · U6-M2·M3·M5 | 첫 실행: `loop_query` 가 되묻기 턴 + 재개 턴 2행인데 `[0]` 을 읽음 → `[1]` 로 수정 |
| test_api_chat_query.py::test_chat_query_identity_second_answer_returns_409 | 같은 질문 두 번째 답 | 첫 답 200, 둘째 답 **409**(결정 J) | 통과 · U6-M4(409 조건 제거) | 기록 없음 |
| test_api_chat_query.py::test_chat_query_new_person_no_question_no_writes | new_person 조회 | 빈 DB → `pending_question None`·reply == `no_record_reply(["박선우"])`·행 수 불변·`pending_questions` 0·`ask_user` 행 0·answerer 0회 | 통과 · U6-M1 | 기록 없음 |
| test_api_chat_query.py::test_chat_query_turn_mixed_utterance_no_writes_loop_gate_rejects | 혼합 발화 | 조회 의도 + `add_event` 제안 → `stored` 0·행 수 불변·기록 툴 0·`loop_gate.rejected` 에 `{index:1,name:add_event,reason:query_turn_no_write}` | 통과 · U6-M2·M3 (U6-M1 은 못 잡는다 — 게이트가 `intent` 로 독립 거부, 계획 R-U4-1) | 기록 없음 |
| test_api_chat_query.py::test_chat_record_turn_control_still_adds_event | 기록 턴 대조군 | `intents` 없음 → `stored.events==1`·`events` +1·`loop_query` 0·`loop_record` 1 | 통과 · (조회 분기가 기록 턴을 가로채는 변이를 잡는 대조군; M1 에서도 통과해야 정상) | 기록 없음 |
| test_api_chat_query.py::test_chat_query_resume_person_deleted_says_no_record_stored_zero | R-U5-1 — 되묻기 뒤 후보 인물 삭제 | 질문 후 `DELETE FROM persons`(실 `get_person_card` 가 `PersonNotFound`) → 답 200·reply == `no_record_reply(["팀장"])`·저장 0·`loop_query` answer_source `["ask","no_record"]`·`person_id None`·answerer 0회 | 통과 · U6-M5(재개 분기 진입 조건 오타) | 첫 실행: `loop_query` `[0]` 이 되묻기 턴 행(ask) → `[1]` 로 수정 |
| test_api_chat_query.py::test_chat_query_issues_session_id_when_header_missing | `X-Session-Id` 없이 조회 | 200·`session_id` uuid4 형식·reply 답+힌트·`stored` 0·그 세션에 `loop_query` 1행 | 통과 · U6-M1·M2·M3 | 기록 없음 |

### U6 변이 → 잡는 테스트 (저장소 밖 사본, `evidence/20261102-1453-u6-mutation.txt`)

| 변이 | 결과 |
|---|---|
| M1 `run_turn` 조회 분기 진입 조건 `"Query"` | 8건 중 6 FAIL(merge·identity·409·new_person·resume 삭제·세션 헤더) — 혼합 발화·대조군 2건은 통과(게이트가 독립 거부 / 기록 턴 대조군) |
| M2 `stored` 를 근거 건수(`events=timeline`)로 | 4 FAIL(merge·identity·혼합·세션 헤더 — `stored == {0,0,0}`) |
| M3 `answerer_from_env` 를 최상단 import 로 바인딩 | 5 FAIL(monkeypatch 무효 → 실 공급자 경로 `OpenAIError`) |
| M4 `answer_question` 의 `already_answered` 조건 제거 | 1 FAIL(`assert 200 == 409`) |
| M5 `resume_turn` 조회 재개 분기 진입 조건 `"Query"` | 2 FAIL(identity 재개·인물 삭제 재개) |

## U7 결함 수정(2026-11-07)

실 LLM 이 `search_person` 인자를 `person` 으로 내는 결함(`evidence/20261104-2110-u7r-1-relation.txt`). 변이: `evidence/20261107-1455-u7fix-mutation.txt`(런타임 치환 플러그인, 저장소 파일 변경 없음).

| 파일::이름 | 무엇 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_loop.py::test_h3_mention_source_rule (변경) | 언급 읽기 규칙 | `search_person` `{person:"읽힘"}` 도 언급 · `{query:"라",person:"마"}` → "라"(query 우선) · `{person:"  "}`·`{person:1}` 제외 · (R-U7F-2 추가) `add_event {person:"바",query:"사"}`→"바" · `search_person {query:"  ",person:"아"}`→"아" · `search_person {query:1,person:"자"}`→"자" → `["가","나","읽힘","다","라","바","아","자"]` | 통과 · U7-M1(폴백 제거)·U7-M2(우선순위 뒤집기)·U7-M4(툴 이름 분기 제거)·U7-M5(공백 query 폴백 제거) | 기록 없음 |
| test_agent_query_loop.py::test_u7_real_llm_person_arg_shape (신규) | U7 실제 모양 재현 | `search_person` `{person:"박선우 과장님"}`·`{person:"나"}` → `mentions==["박선우 과장님","나"]`·`answer_source=="llm"`·`person_id==인물`·저장 0·기록 툴 0 · (R-U7F-3 현재 동작 기록) `mentions_dropped==1` · reply `splitlines()[-2]==QUERY_ONE_AT_A_TIME_HINT`('나' 가 폴백으로 언급에 들어와 dropped 1 → 힌트가 붙는 부작용, 코드 필터는 D16 결정 7 사용자 결정) | 통과 · U7-M1 | 기록 없음 |
| test_agent_propose.py::test_proposal_arg_schema_has_query_property (신규) | 스키마 `query` | `PROPOSAL_ARG_SCHEMA["properties"]["query"] == {"type":"string"}` | 통과 · U7-M3(속성 제거) | 기록 없음 |
| test_agent_propose.py::test_build_propose_prompt_tells_query_field_and_accepts_person (신규) | 프롬프트 문장 | system 에 "query 필드에"·"person 필드에 써도 받아들인다"·"절대 제안하지 마라" | 통과 | 기록 없음 |

| 변이 | 기대 | 결과 |
|---|---|---|
| U7-M1 `person` 폴백 제거 | h3·u7 재현 FAIL | 2 FAIL(h3, u7) |
| U7-M2 우선순위 뒤집기(person 먼저) | h3 FAIL | 1 FAIL(h3) |
| U7-M3 스키마 `query` 제거 | 스키마 테스트 FAIL | 1 FAIL |
| U7-M4 툴 이름 분기 제거(모든 툴에서 query 우선) | h3 FAIL | 1 FAIL(h3) · `evidence/20261107-1508-u7fix2-mutation.txt` |
| U7-M5 공백 query 폴백 제거(`strip()` 검사 삭제) | h3 FAIL | 1 FAIL(h3) · 같은 파일 |

| 파일::이름 | 무엇 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_gate.py::test_prompt_has_query_mention_exception_sentences_after_old_sentence (변경) | 조회 예외 문장 위치 | `exception` 문자열을 새 문장으로 교체, "절대 제안하지 마라." 바로 뒤 순서 단언 유지 | 통과 | U7 문장 교체 직후 옛 문장 단언으로 1 FAIL → 문자열 갱신으로 해소 |

이력: 1차 전체 실행(`evidence/20261107-1454-u7fix-pytest-all.txt`)은 위 게이트 테스트가 옛 문장을 못 박아 **1 failed / 2124 passed** — 구현자가 범위 밖 파일이라 멈추고 보고 → 메인이 문자열 교체를 승인 → 2차(`evidence/20261107-1456-u7fix-pytest-all-2.txt`) **2125 passed, skip 0**(기준선 2122 + 신규 3). 메인 재실행(2026-11-07): 대상 5파일 158 passed · ruff check 통과 · `mypy_check.py --run` 38=38.

## U7 3차 — 관계 질문 답 프롬프트 보강(2026-11-07)

실 LLM 왕복 3차에서 "관계가 뭐야?" 에 카드가 `직장·동` 인데도 "기록이 없어요." 로 답한 결함(`evidence/20261107-1534-u7s-1-relation.txt`). 카드 관계 줄을 풀어 쓰고 시스템 프롬프트에 관계 질문 문장을 넣었다. 증거: `evidence/20261107-1538-u7fix3-answer-tests.txt`(115 passed)·`evidence/20261107-1538-u7fix3-pytest-all.txt`(**2127 passed**, skip 0; 기준선 2125 + 신규 2)·`u7fix3-ruff`·`u7fix3-mypy`(38=38). 변이: `evidence/20261107-1539-u7fix3-mutation.txt`(런타임 치환 플러그인, 저장소 무수정).

| 파일::이름 | 무엇 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_agent_query_answer.py::test_prompt_system_exact_sentences (변경) | 시스템 프롬프트 정확 일치 | "…1~3줄 한국어로 답하고, " 뒤·"자료에 없는 것은…" 앞에 관계 질문 문장 | 통과 · M2 | 기록 없음 |
| test_agent_query_answer.py::test_prompt_user_text_has_question_now_and_evidence_values (변경) | user_text 근거 값 | `직장·동` 단언 → `관계: 직장 관계, 위계 동(같은 급)` | 통과 · M1 | 기록 없음 |
| test_agent_query_answer.py::test_prompt_relation_line_is_descriptive (신규) | 관계 줄 풀어쓰기 | 직장/동 → 한 줄 `관계: 직장 관계, 위계 동(같은 급)` | 통과 · M1 | 기록 없음 |
| test_agent_query_answer.py::test_prompt_relation_line_unknown_values_passthrough (신규) | 사전 밖 값 | 기타/? → `관계: 기타, 위계 ?` | 통과 | 기록 없음 |
| test_agent_query_answer.py::test_relation_desc_vocab_matches_models (신규, R-U7F3-2) | 사전 키 = 모델 어휘 | `set(_RELATION_DESC)==set(RELATION_TAGS)`, `set(_HIERARCHY_DESC)==set(HIERARCHIES)` (`app.db.models`) | 통과 · 키 추가/삭제 변이 | 첫 실행 FAIL: import 경로 `app.models` 오기 → `app.db.models` 로 수정(`evidence/20261108-2016-u7fix3-r2-pytest.txt`) |
| test_agent_query_answer.py::test_prompt_relation_and_hierarchy_each_value_is_descriptive (신규, R-U7F3-2, parametrize 8) | 8개 값 각각의 서술 | 가족/연인/친구/직장/지인/상/동/하 → 리터럴 `관계: 가족, `…`, 위계 하(아랫사람)\n` | 통과(82 passed, `evidence/20261108-2016-u7fix3-r2-pytest-rerun.txt`) · M3 | 기록 없음 |

| 변이 | 기대 | 결과 |
|---|---|---|
| M3 `_HIERARCHY_DESC["상"]` 를 `"상"` 으로 | 신규 parametrize `hierarchy-상` FAIL | 1 FAIL(`evidence/20261108-2016-u7fix3-r2-mutation.txt`), 편집으로 원복 · `git diff --stat -- app` = respond.py +8/−1(`evidence/20261108-2016-u7fix3-r2-revert-diffstat.txt`) |

| 변이 | 기대 | 결과 |
|---|---|---|
| M1 `_HIERARCHY_DESC` 를 빈 dict 로 | 신규 1 FAIL | 2 FAIL(신규 descriptive + user_text 변경 테스트) |
| M2 시스템 프롬프트 새 문장 제거 | exact_sentences FAIL | 1 FAIL |
