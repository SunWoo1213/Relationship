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
