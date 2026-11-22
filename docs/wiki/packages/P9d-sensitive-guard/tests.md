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
