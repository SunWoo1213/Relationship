# P2b-person-delete — 테스트 기록

테스트 1건 = 표 1줄. 증거는 `evidence/` 의 `save_evidence.py` 산출물이다.

**단위별 건수 합계**: U1 41(함수 30개, 파라미터 포함 41건) = **41건**(신규 테스트 파일 1개). 전체 `pytest tests/ -q -rs`: 기준선 2136 → **2177 passed, skip 0**(`evidence/20261109-1634-u1-pytest-all.txt`).

## tests/test_person_refs.py — U1 인물 참조 판별 규칙 (신규 41건 = 함수 30개, 그중 2개가 파라미터 2건·11건)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_person_refs.py -v` → 41 passed(`evidence/20261109-1633-u1-person-refs.txt`). 변이 V1-1~V1-9 `evidence/20261109-1633-u1-mutation.txt`(아홉 번 append, 순서 = V1-1 … V1-9).

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_person_refs.py::test_rule_constants_are_fixed_values | 규칙 키 상수 값 | `PERSON_ID_KEYS`·`PERSON_OBJECT_KEYS`·`TOP_LEVEL_ID_TOOLS`·`ID_MAP_KEYS`·`ID_LIST_KEYS` 가 계획 결정 C-3 값과 같다 | 통과 · V1-1·V1-2·V1-3·V1-4·V1-7 | 기록 없음 |
| test_person_refs.py::test_person_ref_rules_numbered_one_to_five | 규칙 목록 | `PERSON_REF_RULES` 번호 [1..5], 이름 5개 | 통과 · — | 기록 없음 |
| test_person_refs.py::test_identity_question_context_candidate_ids_values | 규칙 4 (실제 `_build_ask_payload` 가 만든 identity context) | `candidate_ids == {"민수":PID,"민준":7}`; PID·7 참, 123 거짓 (`matched_person_id` 는 None 으로 규칙 1 배제) | 통과 · V1-1 | 기록 없음 |
| test_person_refs.py::test_new_person_question_context_references_nobody | new_person 질문 | `candidate_ids == {}` → 거짓 | 통과 · — | 기록 없음 |
| test_person_refs.py::test_resolve_outcome_person_ids_values | 규칙 4 (`ResolveOutcome.to_dict()`) | `person_ids` 값 PID·7 참, 123 거짓, `decisions == []` | 통과 · V1-2 | 기록 없음 |
| test_person_refs.py::test_person_ids_map_in_stored_context_literal | 규칙 4 깊이 무관·값 구분 | 중첩 `person_ids`/`candidate_ids` 에 PID 있으면 참, 없으면 거짓 | 통과 · V1-1·V1-2 | 기록 없음 |
| test_person_refs.py::test_search_person_output_person_object_id | 규칙 2 (`Candidate` 배열 output) | `person.id` PID·7 참, 123 거짓 | 통과 · V1-3 | 기록 없음 |
| test_person_refs.py::test_briefing_out_person_object_id | 규칙 2 (`BriefingOut`, 이벤트·일정 비움) | `person.id == PID` 만으로 참, 7 거짓 | 통과 · V1-3 | 기록 없음 |
| test_person_refs.py::test_person_key_with_string_value_is_not_reference | `person` 이 언급 문자열·id 없는 사전 | `pending_calls[].args.person == "민수"`, `{"person": "987654321"}`, `{"person":{"name":..}}` → 거짓 | 통과 · V1-6(문자열 숫자 오판) | 기록 없음 |
| test_person_refs.py::test_person_out_top_level_id_with_person_tools[create_person·update_person] (2건) | 규칙 3 | `PersonOut` output 최상위 `id` + 툴 이름 → PID 참, 7 거짓 | 통과 · V1-4 | 기록 없음 |
| test_person_refs.py::test_person_out_top_level_id_without_tool_name_is_not_reference | 규칙 3 은 툴 이름 조건부 | 툴 이름 없음·`search_person`·`add_event` → 거짓 | 통과 · V1-5·V1-6 | 기록 없음 |
| test_person_refs.py::test_top_level_id_rule_does_not_apply_to_nested_id | 규칙 3 은 최상위만 | 중첩·배열 안 `id` + `create_person` → 거짓 | 통과 · V1-6 | 기록 없음 |
| test_person_refs.py::test_event_out_id_equal_to_person_id_is_not_reference | 과잉 판정 금지 (`EventOut.id` == 인물 id) | `EventOut(id=PID, person_id=7)` + `add_event` → PID 거짓, 7 참 | 통과 · V1-5·V1-6 | 기록 없음 |
| test_person_refs.py::test_schedule_out_id_equal_to_person_id_is_not_reference | 과잉 판정 금지 (`ScheduleOut.id`) | `ScheduleOut(id=PID, person_id=7)` + `add_schedule` → PID 거짓, 7 참 | 통과 · V1-5·V1-6 | 기록 없음 |
| test_person_refs.py::test_tool_input_person_id | 규칙 1 (툴 input) | `{"person_id":PID}` 참, 다른 값 거짓 | 통과 · — | 기록 없음 |
| test_person_refs.py::test_event_out_and_schedule_out_person_id | 규칙 1 (`EventOut`·`ScheduleOut`·`BriefingOut.recent_events[]`) | PID 참 (`person.id` 는 7, 이벤트의 `person_id` 만 PID) | 통과 · — | 기록 없음 |
| test_person_refs.py::test_er_resolution_candidates_person_id | 규칙 1 (`Resolution.to_dict()` 의 `candidates[].person_id`) | breakdown·decision 비움 → PID 참, 7 거짓 | 통과 · V1-6 | 기록 없음 |
| test_person_refs.py::test_er_breakdown_matched_person_id_only | 규칙 1 (`confidence_breakdown.matched_person_id`) | 그것만 PID → 참, 7 거짓 | 통과 · V1-7·V1-6 | 기록 없음 |
| test_person_refs.py::test_er_decision_matched_person_id_only | 규칙 1 (`decision.matched_person_id`) | 그것만 PID → 참 | 통과 · V1-7 | 기록 없음 |
| test_person_refs.py::test_matched_person_id_none_is_not_reference | `None` 값 | `matched_person_id`·`person_id` 가 None → 거짓 | 통과 · — | 기록 없음 |
| test_person_refs.py::test_candidate_person_ids_list_elements | 규칙 5 | `[3,PID,9]` 참, `[3,9]` 거짓, 사전 값은 거짓 | 통과 · V1-7·V1-6 | 기록 없음 |
| test_person_refs.py::test_resume_schedule_person_id_in_pending_question_context | 규칙 1 (`PendingResume.schedule.person_id`) | PID 참, 7 거짓 | 통과 · V1-6 | 기록 없음 |
| test_person_refs.py::test_loop_mention_decision_person_id | 규칙 1 (`MentionDecision.person_id`) | merge 결정 PID 참, identity(None) 거짓 | 통과 · — | 기록 없음 |
| test_person_refs.py::test_deep_nesting_and_top_level_list | 재귀 | 깊은 중첩·최상위 배열·`matched_person_id` 도 참 | 통과 · V1-7 | 기록 없음 |
| test_person_refs.py::test_same_number_other_meanings_is_not_reference | 과잉 판정 금지 (같은 숫자의 다른 뜻) | `considered_event_ids`·`event_ids`·`schedule_id`·`question_id`·`pending_question_id`·`trace_id`·`fact_id`·`subscription_ids`·`selected`·`briefed`·발화 문자열 모두 PID → 거짓 | 통과 · V1-6 | 기록 없음 |
| test_person_refs.py::test_memory_promote_output_event_ids_only_is_not_reference | `memory_promote` output | `person_id=7`, `considered_event_ids=[PID]` → PID 거짓, 7 참 | 통과 · V1-6 | 기록 없음 |
| test_person_refs.py::test_bool_is_not_integer_id | `bool` 은 정수 id 가 아니다 | 모든 규칙 위치에서 `True` 와 인물 id 1 → 거짓, 대조군 정수 1 참 | 통과 · V1-8 | 기록 없음 |
| test_person_refs.py::test_string_digits_are_not_integer_id | 문자열·실수는 id 가 아니다 | `"987654321"`·`987654321.0` 모든 위치 → 거짓 | 통과 · V1-9 | 기록 없음 |
| test_person_refs.py::test_scalars_and_empties_are_not_reference[11건] | 스칼라·빈 컨테이너 | `None`·0·1·"x"·True·1.5·[]·{}·()·[None]·{"a":None} → 거짓(오류 없음) | 통과 · — | 기록 없음 |
| test_person_refs.py::test_references_person_does_not_mutate_input | 입력 불변 | 호출 전후 deepcopy 동일 | 통과 · — | 기록 없음 |

## 변이 → 잡는 테스트 (U1, `evidence/20261109-1633-u1-mutation.txt`, 저장소 파일 무수정 — 런타임 치환)

| 변이 | 실패한 테스트 |
|---|---|
| V1-1 `candidate_ids` 값 검사 제거 | test_rule_constants_are_fixed_values · test_identity_question_context_candidate_ids_values · test_person_ids_map_in_stored_context_literal (3 failed) |
| V1-2 `person_ids` 값 검사 제거 | test_rule_constants_are_fixed_values · test_resolve_outcome_person_ids_values · test_person_ids_map_in_stored_context_literal (3 failed) |
| V1-3 `person.id` 경로 제거 | test_rule_constants_are_fixed_values · test_search_person_output_person_object_id · test_briefing_out_person_object_id (3 failed) |
| V1-4 `create/update_person` 최상위 `id` 규칙 제거 | test_rule_constants_are_fixed_values · test_person_out_top_level_id_with_person_tools[create_person·update_person] (3 failed) |
| V1-5 최상위 `id` 를 툴 이름과 무관하게 인물 id 로 봄 | test_person_out_top_level_id_without_tool_name_is_not_reference · test_event_out_id_equal_to_person_id_is_not_reference · test_schedule_out_id_equal_to_person_id_is_not_reference (3 failed) |
| V1-6 `str(person_id) in str(obj)` 텍스트 판정 | 15 failed — 그중 test_same_number_other_meanings_is_not_reference · test_memory_promote_output_event_ids_only_is_not_reference · test_event_out_id_equal_to_person_id_is_not_reference |
| V1-7 `matched_person_id`·`candidate_person_ids` 검사 제거 | test_rule_constants_are_fixed_values · test_er_breakdown_matched_person_id_only · test_er_decision_matched_person_id_only · test_candidate_person_ids_list_elements · test_deep_nesting_and_top_level_list (5 failed) |
| V1-8 `bool` 을 정수로 취급 | test_bool_is_not_integer_id (1 failed) |
| V1-9 문자열 `"42"` 를 42 로 취급 | test_string_digits_are_not_integer_id (1 failed) |
