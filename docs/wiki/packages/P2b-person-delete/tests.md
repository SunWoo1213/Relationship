# P2b-person-delete — 테스트 기록

테스트 1건 = 표 1줄. 증거는 `evidence/` 의 `save_evidence.py` 산출물이다.

**단위별 건수 합계**: U1 41(함수 30개, 파라미터 포함 41건) + U2 24건 + U2 가 U1 파일에 더한 R-U1-3 1건 = **66건**(신규 테스트 파일 2개). 전체 `pytest tests/ -q -rs`: 기준선 2136 → U1 후 **2177 passed, skip 0**(`evidence/20261109-1634-u1-pytest-all.txt`) → U2 후 **2202 passed, skip 0**(`evidence/*-u2-pytest-all.txt`).

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

## tests/test_person_refs.py — U2 에 함께 넣은 U1 권고 R-U1-3 (신규 1건, 이 파일은 U1 의 새 파일)

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_person_refs.py::test_person_object_id_does_not_need_tool_name | 규칙 2(`person.id`)는 `tool_name` 없이도 참 — U2 가 `input`·`context` 판정에서 기대는 계약 | `{"person":{"id":PID}}`·`to_jsonable([Candidate(PersonOut(PID))])` 를 `tool_name` 없이 → PID 참, 7 거짓 | 통과 · V1-3 (U1 의 규칙 2 테스트는 `tool_name` 을 넘긴 픽스처뿐이라, `tool_name` 없는 호출 계약은 이 건이 처음 고정한다) | 기록 없음 |

## tests/test_person_delete.py — U2 삭제 서비스 `delete_person` (신규 24건 = 함수 16개, 그중 2개가 파라미터 7·3건)

실행: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_person_delete.py tests/test_person_refs.py -v` → 66 passed(`evidence/*-u2-person-delete.txt`). 센티널 시나리오 픽스처 `world` 는 실제 코드 경로(`run_turn` merge·`run_turn` identity 되묻기 2회+`answer_question`·`run_briefings`·`after_record` 승격+패턴·다른 사용자 범위 되묻기)가 남긴 JSONB 를 쓴다 — 손으로 만든 JSON 은 `test_traces_same_digits_in_other_roles_are_not_deleted` 의 decoy 행뿐이다.

| 파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 · 검출 변이 | 실패 이력 |
|---|---|---|---|---|
| test_person_delete.py::test_world_sentinel_is_planted_in_questions_and_traces_before_delete | 시나리오 전제 — 삭제 전에 센티널이 질문·trace input/output 에 있다 | 질문 context 2건·trace input·output > 0, 센티널 이벤트 5·일정 1·별칭 2, 사실 키 {likes, pattern:conflict, 취미}, 근거 링크 > 0 | 통과 · (그물이 비어 있지 않음을 보장) | 기록 없음 |
| test_person_delete.py::test_cascade_removes_every_row_of_the_person_and_leaves_control_identical | CASCADE 5테이블+`fact_sources` 센티널 행 0, 대조군·남의 사용자 인물 6군데 값 전후 동일, `push_subscriptions` 수 불변 | 삭제 후 `_person_state` 6군데 모두 `[]`, 대조군 상태 == 삭제 전 | 통과 · — | 기록 없음 |
| test_person_delete.py::test_pending_questions_referencing_person_are_deleted_answered_or_not | 결정 C-1 — 미답변·답변됨 질문 행 삭제, 대조군(다른 사용자 범위) 질문 전후 동일 | 두 질문 `get` → None, `deleted.pending_questions == 2`, 질문 context 에 센티널 0, 대조군 질문 5필드 동일 | 통과 · V2-1·V2-10 | 기록 없음 |
| test_person_delete.py::test_traces_no_sentinel_text_remains_in_input_or_output | 결정 C-3 그물 — trace input·output·질문 context 어디에도 센티널 숫자 0 | `_text_hits` 3종 == 0 | 통과 · V2-1·V2-2a·V2-2b·V2-2c·V2-10 | 기록 없음 |
| test_person_delete.py::test_traces_covering_each_shape_in_the_scenario_are_deleted | 리스크 1 — 사실 3 표의 쓰는 곳을 시나리오가 한 번씩 지나가고 삭제 뒤 그 행이 전부 사라진다 | 삭제 전 step {loop_resolve_done·briefing_compose·memory_pattern·memory_promote}·(tool_call, update_person·add_event·add_schedule·get_briefing·ask_user) 존재 → 삭제 뒤 센티널 포함 (step, tool) 쌍 집합 == ∅ | 통과 · V2-2a·V2-2b·V2-2c | 기록 없음 |
| test_person_delete.py::test_traces_control_only_and_unrelated_rows_are_unchanged | 과잉 삭제 0 — 센티널 숫자가 없는 질문·trace 행 전체가 값까지 동일 | 대조군을 참조하는 trace ≥ 3, 질문 ≥ 1 확인 후 `_unrelated_jsonb_rows` 전후 `==` | 통과 · (V2-6 은 decoy 테스트가 잡는다) | 기록 없음 |
| test_person_delete.py::test_traces_delete_writes_no_trace_row | 결정 H — 삭제가 trace 를 남기지 않는다 | `count(agent_traces)` 후 == 전 − `deleted.agent_traces` | 통과 · — | 기록 없음 |
| test_person_delete.py::test_summary_counts_equal_seeded_counts | 결정 F — 건수가 시드와 같다 | `to_dict() == {person_id, deleted:{persons 1, person_aliases 2, person_facts 3, fact_sources=테스트 쪽 집계, events 5, schedules 1, pending_questions 2, agent_traces=테스트 쪽 LIKE 집계}}` | 통과 · V2-1·V2-2a·V2-2b·V2-2c·V2-7·V2-10 | 기록 없음 |
| test_person_delete.py::test_confirm_missing_or_mismatch_raises_and_writes_nothing[None·빈 문자열·다른 이름·앞 공백·뒤 공백·한 글자 다름·대조군 이름] (7건) | 결정 A — 확인값 없음/불일치는 `ConfirmationRequired("person_delete")`, 쓰기 0 | 각 값 → 예외 + `reason == "person_delete"` + `assert_no_writes`(9테이블 값) + 인물 1행 | 통과 · V2-5·V2-11 | 기록 없음 |
| test_person_delete.py::test_confirm_correct_value_deletes_the_person | 맞는 확인값이면 삭제 | 인물 행 0 | 통과 · — | 기록 없음 |
| test_person_delete.py::test_confirm_uses_current_display_name_not_alias | 확인값 = 현재 `display_name`(옛 이름·별칭 불가) | 이름을 "바뀐이름" 으로 바꾼 뒤 옛 이름·"그분" → 예외+쓰기 0, "바뀐이름" → 삭제 | 통과 · V2-5·V2-11 | 기록 없음 |
| test_person_delete.py::test_other_user_person_is_not_found_whatever_the_confirm_is[맞는 값·None·틀린 값] (3건) | 결정 E — 남의 인물은 확인값과 무관하게 `PersonNotFound`(소유 확인이 먼저), 쓰기 0 | 3값 → `PersonNotFound`, `assert_no_writes`, 인물 1행 | 통과 · V2-4 | 기록 없음 |
| test_person_delete.py::test_not_found_for_missing_id_even_with_any_confirm | 없는 id → `PersonNotFound`(확인 맞음·None 모두), 쓰기 0 | id 123456789012 | 통과 · — | 기록 없음 |
| test_person_delete.py::test_not_found_on_second_delete_of_same_id | 같은 id 재삭제 | 두 번째 → `PersonNotFound` | 통과 · — | 기록 없음 |
| test_person_delete.py::test_service_does_not_commit_outer_rollback_restores_everything | 결정 D·P2 결정 2 — commit 하지 않는다 | `begin_nested` 안에서 삭제 → rollback → 인물·6군데 상태·9테이블 스냅샷 복원 | 통과 · V2-8 | 기록 없음 |
| test_person_delete.py::test_traces_same_digits_in_other_roles_are_not_deleted | 같은 숫자의 다른 뜻 — LIKE 만으로 지우면 남의 행이 사라진다 | id 555000111 인물. `EventOut.id`·`ScheduleOut.id`·`considered_event_ids`·`question_id` 에만 같은 숫자인 trace 3행·질문 1행은 남고, input `person_id`·`EventOut.person_id`·`create_person` output 최상위 `id`(규칙 3) trace 3행과 `candidate_ids`·`resume.schedule.person_id` 질문 1행만 삭제(`deleted.agent_traces == 3`, `pending_questions == 1`) | 통과 · V2-6·V2-9 | 기록 없음 |

## 변이 → 잡는 테스트 (U2, `evidence/*-u2-mutation.txt`, 저장소 파일 무수정 — `mutate_plugin.py` 런타임 치환, 변이마다 append)

기준(`MUT=NONE`) 24 passed. 변이 V2-9~V2-11 은 계획 표 밖에서 내가 더한 것이다(계획의 V2-1~V2-8 은 전부 실행).

| 변이 | 실패한 테스트 |
|---|---|
| V2-1 질문 정리 생략 | test_pending_questions_… · test_traces_no_sentinel_text_… · test_summary_counts_… · test_traces_same_digits_… (4 failed) |
| V2-2 trace 정리 생략(2a) | test_traces_no_sentinel_text_… · test_traces_covering_… · test_summary_counts_… · test_traces_same_digits_… (4 failed) |
| V2-2 `input` 만 판정(2b) | 같은 4건 (4 failed) |
| V2-2 `output` 만 판정(2c) | test_traces_no_sentinel_text_… · test_traces_covering_… · test_summary_counts_… (3 failed) |
| V2-3 정리를 `persons` 삭제 뒤로 | **잡히지 않음 — 동치 변이**(24 passed). 이 구현의 정리는 인물 행을 다시 조회하지 않고 미리 구한 id 목록으로 지우므로 순서가 결과를 바꾸지 않는다. 계획의 "인물 없음 → 조회 실패로 건너뜀" 구조가 아니라서다 |
| V2-4 소유 확인에서 `user_id` 무시 | test_other_user_person_is_not_found_whatever_the_confirm_is[3건] (3 failed) |
| V2-5 확인 검사를 정리 뒤로 | test_confirm_missing_or_mismatch_…[7건] · test_confirm_uses_current_display_name_not_alias (8 failed, `assert_no_writes` 행 수) |
| V2-6 정밀 판정 생략(LIKE 후보 전부 삭제) | test_traces_same_digits_in_other_roles_are_not_deleted (1 failed, 6 != 3) |
| V2-7 건수 집계를 삭제 뒤에 | test_summary_counts_equal_seeded_counts (1 failed) |
| V2-8 `session.commit()` 호출 | test_service_does_not_commit_outer_rollback_restores_everything (1 failed, `ResourceClosedError`) |
| V2-9 output 판정에 `tool_name` 을 넘기지 않음(규칙 3 무력화) | test_traces_same_digits_in_other_roles_are_not_deleted (1 failed, 2 != 3) |
| V2-10 미답변 질문만 삭제 | test_pending_questions_… · test_traces_no_sentinel_text_… · test_summary_counts_… (3 failed) |
| V2-11 확인값이 `None` 이 아니면 통과 | test_confirm_missing_or_mismatch_…[6건] · test_confirm_uses_current_display_name_not_alias (7 failed) |

## 센티널 시나리오가 지나간 쓰는 곳 (01-plan 리스크 1 — 사실 3 표 대조)

| 사실 3 표의 쓰는 곳 | 시나리오에서 지나간 경로 | 확인한 테스트 |
|---|---|---|
| `@traced` 툴 trace(`update_person`·`add_event`·`add_schedule`·`get_briefing`·`search_person`) | 센티널 기록 턴 merge + 브리핑 입력 조립 + ER 후보 검색 | test_traces_covering_each_shape_in_the_scenario_are_deleted |
| `tool_error` trace | **지나가지 않음** (오류 경로를 시나리오에 넣지 않았다) | 규칙 1 이 `input.person_id` 로 잡는다는 U1 단위 테스트만 |
| ER 되묻기 payload(`candidate_ids`·`confidence_breakdown`) | identity 되묻기 2건(미답변·답변됨) | test_pending_questions_… · test_traces_covering_… (`ask_user`) |
| 재개 재료 `context.resume` (`schedule.person_id`) | **지나가지 않음** (schedule 질문 없음 — decoy 질문 행의 `resume.schedule.person_id` 로만) | test_traces_same_digits_in_other_roles_are_not_deleted |
| ER 판정(`er_resolve` 의 `candidates[].person_id`) | merge·identity 턴의 ER trace | test_traces_no_sentinel_text_remains_… |
| 루프 trace(`loop_resolve_done.person_ids` 등) | 센티널 기록 턴 | test_traces_covering_… (`loop_resolve_done`) |
| 브리핑(`briefing_compose`) | `run_briefings` 1회 | test_traces_covering_… |
| 푸시(`push_send`) | **지나가지 않음** (`NullNotifier`) | U1 단위 테스트(규칙 1)만 |
| 메모리(`memory_pattern`·`memory_promote`) | 미승격 4+1 이벤트로 승격·패턴 둘 다 | test_traces_covering_… |
