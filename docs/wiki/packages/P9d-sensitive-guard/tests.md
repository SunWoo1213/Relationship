# P9d-sensitive-guard 테스트 기록 — 무엇을 어떻게 시험했나

> 확인 1건 = 표 1줄. 열: 확인 항목 | 명령 | 결과 | evidence. 단위별로 절을 덧붙인다. 증거는 `evidence/` 아래(이름의 `20261122-HHMM-` 접두는 시각).
> 기준선: 전체 pytest **2759 passed · skip 0**(`evidence/20261122-1735-baseline-pytest.txt`, 기준 커밋 `947c12c`). 같은 날 17:33 의 첫 기준선(1786 passed · 973 skipped)은 로컬 DB 가 꺼져 있던 것이라 쓰지 않는다.

## U3 — 리비전 0006 + 모델 (backend-agent, 2026-11-22)

새 파일 `tests/test_migration_0006.py`(전부 `dbtest`, 전용 DB `relationship_test_mig`) 19건. 명령은 모두 `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_migration_0006.py -q`. 증거: 구현자 `u3-migration`(0003~0006 합쳐 46 passed), verifier 재실행 `verifier-u3-migration`.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| ① `test_head_is_0006_and_db_is_at_0006` — head 리터럴 `0006`, down_revision `0005`, 전용 DB 버전 | 위 명령 | passed | `u3-migration` · 변이 `u3-mutations` |
| ② `test_new_columns_match_s3_1_by_value` — 새 컬럼 6개의 이름·타입·nullable·기본값 없음·길이 없음, 0005 상태에는 없음 | 위 명령 | passed | 같음 (변이 M6·M7) |
| ③ `test_check_sentences_are_the_contract_values` — 세 표의 범주 CHECK 문장, kind CHECK 4종 문장(전은 3종), 새 CHECK 정확히 3개 증가 | 위 명령 | passed | 같음 (변이 M4·M5·M10, verifier `category_value`·`category_extra`) |
| ④ `test_kind_sensitive_violates_at_0005_and_succeeds_at_0006` — 0005 에서 `kind='sensitive'` 는 제약 이름으로 위반, 0006 에서 성공, 모르는 kind 는 위반 | 위 명령 | passed | 같음 |
| ⑤ `test_sensitive_category_accepts_five_categories_and_null_only[events]` — 범주 5종·NULL 통과, `drugs` 는 제약 이름으로 위반 | 위 명령 | passed | 같음 |
| ⑥ `…[person_facts]` — 위와 같음 | 위 명령 | passed | 같음 |
| ⑦ `…[schedules]` — 위와 같음 | 위 명령 | passed | 같음 |
| ⑧ `test_upgrade_changes_no_existing_data` — upgrade 전후 행 수·값 불변, 새 컬럼 전부 NULL(소급 0) | 위 명령 | passed | 같음 (변이 M8, verifier `upgrade_touch_briefed`). **공백**: 스냅샷이 시각 컬럼을 보지 않는다 — verifier 변이 `upgrade_touch_updated_at`·`upgrade_touch_created_at` 통과(R-2, 열림) |
| ⑨ `test_model_carries_the_same_contract_values` — 모델의 범주 5종·CHECK 문장·kind 4종·컬럼 타입·nullable·타임존 | 위 명령 | passed | 같음 (변이 M13 — 이 시험을 더한 뒤 잡힘) |
| ⑩ `test_resume_input_accepts_sensitive_kind_without_code_change` — `ResumeInput` 이 코드 수정 없이 `sensitive` 를 받음 | 위 명령 | passed | 같음 |
| ⑪ `test_no_table_index_unique_or_fk_is_added` — 테이블·인덱스·PK/UNIQUE/FK 이름 집합이 전후 같음 | 위 명령 | passed | 같음 |
| ⑫ `test_alembic_check_reports_no_new_operations` — 모델과 DB 가 같음 | 위 명령 | passed | 같음 (변이 M12) |
| ⑬ `test_downgrade_when_no_sensitive_rows_removes_columns_and_restores_three_kinds` — 민감 행이 없으면 downgrade 가 컬럼·CHECK 를 되돌리고 행을 보존, 다시 upgrade | 위 명령 | passed | 같음 (변이 M9) |
| ⑭ `test_downgrade_refuses_and_keeps_everything_when_sensitive_rows_exist[kind_sensitive_question]` — 민감 동의 질문 행이 있으면 실패, 메시지에 개수만, 버전·컬럼·행·CHECK 불변 | 위 명령 | passed | 같음 (verifier `skip_kind` — PostgreSQL CHECK 재생성 실패로도 막힘) |
| ⑮ `…[event_marked]` — 사건 표시 행 | 위 명령 | passed | verifier `skip_event` |
| ⑯ `…[fact_marked]` — 사실 표시 행 | 위 명령 | passed | verifier `skip_fact`(`DID NOT RAISE` 로 독립 검출) |
| ⑰ `…[schedule_marked]` — 일정 표시 행 | 위 명령 | passed | verifier `skip_schedule` |
| ⑱ `…[consent_ref_only]` — 동의 질문 참조만 있는 행 | 위 명령 | passed | 변이 M1·M2, verifier `skip_consent`·`message_leaks_raw` |
| ⑲ `test_notice_columns_alone_do_not_block_downgrade` — 고지 동의 값만 있으면 downgrade 가 막히지 않음 | 위 명령 | passed | 같음 |

### 고친 기존 단언 (닫힌 목록 6파일 — 목록 밖 시험 diff 0, `u3-test-diff`·`verifier-u3-test-diff`)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `tests/test_api.py:93` — `/health` 의 `alembic_revision` `"0005"` → `"0006"` | `pytest tests/test_api.py -q` | passed (10) | `u3-api` |
| `tests/test_migration_0005.py:110·111·196` — head 리터럴 → "이력에 0005 가 있고 DB 버전 == head" | `pytest tests/test_migration_0005.py -q` | passed | `u3-migration` |
| `tests/test_migration_0004.py:39·110·157` — `USERS_COLUMNS` 5 → 7, 0003 상태는 `USERS_COLUMNS_AT_0003` | `pytest tests/test_migration_0004.py -q` | passed | 같음 |
| `tests/test_migration_0003.py:49` — head 기준 `users` 집합에 두 컬럼 | `pytest tests/test_migration_0003.py -q` | passed | 같음 |
| `tests/test_schema_models.py` — 총 컬럼 79 → 85, nullable 이름 7 → 11, CHECK 5 → 8, kind 3 → 4, 타임스탬프 컬럼 +1, events type CHECK 필터 | `pytest tests/test_schema_models.py tests/test_schema_check.py -q` | passed (29) | `u3-schema-tests` |
| `tests/test_schema_check.py:44` — `len(QUESTION_KINDS)` 3 → 4 | 위 명령 | passed | 같음 |

### 단위 공통

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| 전체 회귀 | `.venv/bin/python -m pytest -q` | **2778 passed · skip 0** (2759 + 19) | `u3-full-pytest` · verifier `verifier-u3-full-pytest` |
| 모델 ↔ DB | `alembic check` | `No new upgrade operations detected.` | `u3-check` |
| 스키마 점검 | `python3 scripts/schema_check.py` | PASS(13개 테이블, kind 4종, `alembic_version -> 0006`) | `u3-schema-check` |
| 툴 7종 시그니처 | `python3 scripts/tools_check.py` | 7/7 ok | `u3-tools-check` |
| 개발 DB 행 수 불변(0005 → 0006) | 전후 행 수 세기 | 13개 테이블 전후 같음 | `u3-dev-before-counts` · `u3-dev-after-counts` · verifier `verifier-u3-dev-nulls`(새 컬럼 NOT NULL 행 0) |
| 변이 | 저장소 밖 사본(구현자 14건) · 런타임 치환(verifier 12건) | 구현자 14/14 잡힘 · verifier 10 잡힘 / 2 통과(시각 컬럼 — R-2) | `u3-mutations` · `verifier-u3-mutations-names` |
| 시험 전용 DB 복구 | 변이 뒤 0003~0006 재실행 | version 0006 · 민감 행 0 · CHECK 4개 원문 | `verifier-u3-restore` |

## U4 — 가입 고지·재고지 API·미동의 403·주기 브리핑 건너뜀 (backend-agent, 2026-11-22)

새 파일 `tests/test_privacy_notice.py` 20건. 명령은 모두 `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_privacy_notice.py -q`. 증거: 구현자 `u4-notice`(required_routes 포함 32 passed), verifier 재실행 `verifier-u4-*`.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| ① `test_notice_version_is_one` — `PRIVACY_NOTICE_VERSION == 1` | 위 명령 | passed | `u4-notice` · 변이 M18 |
| ② `test_signup_without_acceptance_is_422_notice_required_and_writes_no_user[없음]` — 422 `{"detail":{"code":"notice_required"}}`, `users` 행 0 | 위 명령 | passed | 변이 M10·M11·M21 |
| ③ `…[false]` — 위와 같음 | 위 명령 | passed | 같음 |
| ④ `…[null]` — 위와 같음 | 위 명령 | passed | 같음 |
| ⑤ `test_signup_with_acceptance_records_version_and_time_and_not_required` — 가입 201, `notice_required` false, 판 1·시각 기록 | 위 명령 | passed | 변이 M9·M12·M13 |
| ⑥ `test_signup_check_order_format_then_notice_then_conflict` — 형식 3종 → 동의 → 409 순서 | 위 명령 | passed | 변이 M22·M23 (`u4-mutations-order`) |
| ⑦ `test_me_notice_required_is_true_for_null_and_lower_version_false_for_current` — NULL·낮은 판 true, 현재 판 false | 위 명령 | passed | 변이 M8·M17 |
| ⑧ `test_login_response_carries_notice_required` — 로그인 응답에 `notice_required` | 위 명령 | passed | verifier 변이(로그인 응답만 False 고정) |
| ⑨ `test_reaccept_null_account_flow_null_then_false_then_true_after_version_bump` — NULL → 204 → false → 판 올림 → true | 위 명령 | passed | 변이 M15·M16 |
| ⑩ `test_reaccept_lower_version_overwrites_version_and_time` — 낮은 판은 판 번호·시각을 덮어씀 | 위 명령 | passed | 같음 |
| ⑪ `test_reaccept_on_current_version_is_204_and_changes_no_row` — 재호출 204, 처음 시각 유지 | 위 명령 | passed | 변이 M14 |
| ⑫ `test_privacy_notice_without_login_is_401` — 비로그인 401 | 위 명령 | passed | `u4-notice` |
| ⑬ `test_unconsented_chat_is_403_and_touches_no_llm_no_rows` — `/chat` 403, LLM·임베딩 의존성 0, trace·대화 행 불변 | 위 명령 | passed | 변이 M2·M19·M20, verifier(의존성 순서 변이) |
| ⑭ `test_unconsented_briefings_run_is_403_and_composes_nothing` — `/briefings/run` 403, 생성기 0, `briefed_at` NULL | 위 명령 | passed | 변이 M1 |
| ⑮ `test_unconsented_answers_is_403_then_200_after_notice_accepted` — `/answers` 403(질문 그대로) → 동의 뒤 200 | 위 명령 | passed | 변이 M3 |
| ⑯ `test_consented_user_still_passes_the_notice_gate` — 동의 계정은 통과(대조) | 위 명령 | passed | `u4-notice` |
| ⑰ `test_scheduler_skips_unconsented_account_entirely[notice-null]` — 생성기 0 · 발송 0 · `briefed_at` NULL · 그 계정 trace 0 | 위 명령 | passed | 변이 M4·M5 |
| ⑱ `…[낮은 판]` — 위와 같음 | 위 명령 | passed | 같음 |
| ⑲ `…[no-users-row]` — `users` 행이 없는 인물도 건너뜀 | 위 명령 | passed | 변이 M7 |
| ⑳ `test_scheduler_briefs_only_consented_account_in_a_mixed_run` — 섞인 실행에서 동의 계정만 브리핑 | 위 명령 | passed | 변이 M6. **공백**: "현재보다 높은 판" 계정 시험 없음 — verifier 변이 2종(`>=`→`==`, `<`→`!=`) 통과(review-u4 R-3, 열림) |

### 고친 기존 단언 (계획 VR3 예외 7줄 — 나머지는 가입 본문·계정 준비 줄, `u4-test-diff`)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `tests/test_auth_required_routes.py:65` — 로그인 필수 집합에 `("POST", "/auth/privacy-notice")` 추가(면제 집합은 그대로) | `pytest tests/test_auth_required_routes.py -q` | passed | `u4-notice` |
| `tests/test_auth_api.py:97` — 가입 응답 키 집합에 `notice_required` | `pytest tests/test_auth_api.py -q` | passed | `u4-auth`(237 passed) |
| `tests/test_auth_api.py:226` — 로그인 응답에 `"notice_required": False` | 위 명령 | passed | 같음 |
| `tests/test_auth_nickname.py:78` — 키 집합에 `notice_required` | `pytest tests/test_auth_nickname.py -q` | passed | 같음 |
| `tests/test_auth_nickname.py:~95` — 로그인 응답에 `"notice_required": False` | 위 명령 | passed | 같음 |
| `tests/test_auth_nickname.py:~102` — me 응답에 `"notice_required": False` | 위 명령 | passed | 같음 |
| `tests/test_auth_helpers.py:~109` — me 응답에 `"notice_required": False` | `pytest tests/test_auth_helpers.py -q` | passed | 같음 |
| `tests/test_migration_0006.py` 스냅샷에 시각 컬럼 추가(단언 줄 변경 0 — review-u3 R-2) | `pytest tests/test_migration_0006.py -q` | passed (19) · 시각 컬럼 변이 7종 잡힘 | `u4-migration0006` · `u4-migration-snapshot-mutations`(1800 판) · verifier `verifier-u4-r2-mutations` |

### 단위 공통

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| 전체 회귀 | `.venv/bin/python -m pytest -q` | **2798 passed · skip 0** (2778 + 20) | `u4-pytest-full` · verifier `verifier-u4-full-pytest` |
| 주기 브리핑 시험 | `pytest tests/test_briefing_scheduler*.py tests/test_push_wiring.py -q` | 31 passed (기존 단언 그대로) | `u4-scheduler` |
| ruff · 툴 7종 · mypy | `ruff check` · `tools_check.py` · `mypy_check.py --run` | 통과 · 7/7 · 새 오류 없음(38 = 기준선 38) | `u4-ruff` · `u4-tools-check` · `u4-mypy` |
| 변이 | 저장소 밖 사본(구현자 23 + 순서 2) · verifier 19종 | 구현자 전부 잡힘 · verifier 17 잡힘 / 2 통과(R-3) | `u4-mutations` · `u4-mutations-order` · `verifier-u4-mutations` |
| 가입 동의 값 해석 | 문자열·숫자 본문으로 가입 | `"true"`·`1` 등이 동의로 기록됨(review-u4 R-2, 열림) | `verifier-u4-coerce` |

## U4 보강 — 동의 값 좁히기·높은 판 계정 시험 (backend-agent, 2026-11-22)

review-u4 의 R-2·R-3·R-4 를 닫는다. 위 U4 절의 "공백"(⑳)과 "R-2 열림"은 이 절에서 닫혔다. 명령은 모두 `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_privacy_notice.py -q`(29 passed).

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_signup_without_acceptance_is_422_notice_required_and_writes_no_user[str-true]` — 문자열 `"true"` 는 동의가 아님: 422 `notice_required`(detail dict), `users` 행 0 | 위 명령 | passed | `u4b-notice-pytest` · 변이(`is not True` → `not x`, 스키마 `bool \| None`) |
| `…[str-yes]` — `"yes"` | 위 명령 | passed | 같음 |
| `…[int-1]` — 숫자 `1` | 위 명령 | passed | 같음 (verifier 변이 `!= True`) |
| `…[float-1]` — `1.0` | 위 명령 | passed | 같음 |
| `…[str-abc]` — `"abc"` | 위 명령 | passed | 같음 |
| `…[int-2]` — `2` | 위 명령 | passed | 같음 |
| `…[list]` — `[]` | 위 명령 | passed | 변이(스키마 `bool \| None`·`StrictBool \| None`) |
| `test_higher_notice_version_account_is_not_required_and_chat_passes` — 판 번호가 현재+1 인 계정: me `notice_required` false, `/chat` 200 | 위 명령 | passed | 변이 `deps.py` `<` → `!=` (review-u4 에서 통과하던 것) |
| `test_scheduler_briefs_higher_notice_version_account` — 같은 계정의 일정이 브리핑됨(생성기 1회, 푸시 발송) | 위 명령 | passed | 변이 `scheduler.py` `>=` → `==` (review-u4 에서 통과하던 것) |
| 실제 요청 18종(JSON 원문) — `true` 만 201, 나머지 17종 422 `notice_required` dict · 형식 위반이 함께 오면 `invalid_*` 가 먼저 · 이미 있는 아이디 + `1` 은 `notice_required` | verifier 스크래치패드 시험 | 전부 기대대로 | `verifier-u4b-values` |
| `StrictBool` 로 바꾸면 계획과 어긋남(detail 목록 422, 검사 순서 깨짐) | 런타임 치환 | 14종이 목록 422 | `verifier-u4b-strictbool` |
| 전체 회귀 | `.venv/bin/python -m pytest -q` | **2807 passed · skip 0** (2798 + 9) | `u4b-pytest-full` · `verifier-u4b-full-pytest` |
| 저장소 잔재 없음(구현자가 저장소 파일을 고쳤다 되돌리는 방식으로 변이를 돌림 — 규칙 밖) | `git diff 5fc2b79 -- app/auth/deps.py app/auth/routes.py app/settings.py` · docstring 을 비운 AST 비교 | 0줄 · `schemas.py` 만 다름 | `verifier-u4b-residue` · `u4b-revert-diff` |
| ruff · 툴 7종 · mypy | 단위 공통 | 통과 · 7/7 · 새 오류 없음(33, 기준선 38) | `verifier-u4b-ruff` · `verifier-u4b-tools-check` · `verifier-u4b-mypy` |
