# P9b-auth 테스트 기록 — 무엇을 어떻게 시험했나

> 확인 1건 = 표 1줄. 열: 확인 항목 | 명령 | 결과 | evidence. 단위별로 절을 덧붙인다. 증거는 `evidence/` 아래(이름의 `20261115-HHMM-` 접두는 시각).

## U1 — 스키마·리비전 0003 (backend-agent, 2026-11-15)

새 파일 `tests/test_migration_0003.py`(전부 `dbtest`, 전용 DB `relationship_test_mig`) 11건. 명령은 모두 `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_migration_0003.py -q`.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| ① `test_head_revision_is_0003_and_db_is_at_head` — 스크립트 head 와 전용 DB `alembic_version` 이 `0003` | 위 명령 | passed | `u1-mutations-v2`(변이 실패 확인) · 전체 `u1-pytest-all` |
| ② `test_new_tables_have_exactly_the_s3_1_columns` — 새 테이블 3개 컬럼 집합이 S3.1 보충과 같고 `pending_questions.user_id` 존재 | 위 명령 | passed | 같음 |
| ③ `test_users_username_is_unique` — 중복 INSERT 가 제약 이름 `uq_users_username` 의 IntegrityError | 위 명령 | passed(V1-2 변이가 실패시킴) | `u1-mutations-v2` |
| ③ `test_auth_sessions_token_hash_is_unique` — `uq_auth_sessions_token_hash` | 위 명령 | passed | 같음 |
| ③ `test_chat_messages_role_check_rejects_other_values` — `role='system'` 이 `ck_chat_messages_role_valid` 위반(V1-4 변이가 실패시킴) | 위 명령 | passed | 같음 |
| ③ `test_chat_messages_role_check_accepts_user_and_assistant` — `user`·`assistant` 는 통과 | 위 명령 | passed | 같음 |
| FK `test_only_new_tables_have_users_foreign_key_with_cascade` — users FK 는 정확히 `auth_sessions`·`chat_messages` 두 곳(`confdeltype='c'`), `persons`·`push_subscriptions`·`pending_questions` 에는 없음(결정 O). V1-6 변이가 실패시킴 | 위 명령 | passed | 같음 |
| ④ `test_pending_questions_user_id_is_not_null` — `is_nullable='NO'` + `user_id` 없는 INSERT 가 `column_name='user_id'` 의 IntegrityError(V1-3 변이가 실패시킴) | 위 명령 | passed | 같음 |
| ⑤ `test_upgrade_clears_all_user_data` — 0002 상태에 원시 SQL 로 9개 테이블 행 1개씩 넣고(시작값 `{t:1}` 단언) head 뒤 전부 0(V1-1·V1-1b 변이가 실패시킴) | 위 명령 | passed | 같음 |
| ⑥ `test_alembic_check_reports_no_new_operations` — `command.check` 무변경(V1-8 변이가 실패시킴) | 위 명령 + `u1-check` | passed · `No new upgrade operations detected.` | `u1-check` |
| ⑦ `test_downgrade_to_0002_removes_new_objects_and_upgrade_restores` — downgrade 0002 뒤 새 테이블·컬럼·인덱스 0, 다시 head 로 복원 | 위 명령 | passed | 같음 |

기존 테스트 갱신(닫힌 목록 ①~④·R3-1, S3.1 보충 반영) — 값: 테이블 12·컬럼 합 72(56+4+5+6+1)·FK 8·인덱스 13·CHECK 5·nullable 에 `question_id`·`/health` 리비전 `0003`·`PendingQuestion(` 6파일 `user_id`.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| 전체 pytest(첫 실행, 대체됨) | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | 1 failed(`test_schema_check.py` UNIQUE 기대 집합 — 닫힌 목록 밖이었다가 메인 승인 2026-11-15 로 목록 ②에 추가) · 2271 passed | `u1-pytest-all` |
| UNIQUE 기대 집합 5개로 수정 후 전체 pytest | 같은 명령 | **2272 passed · 0 failed · skip 0**(ruff·`schema_check` 라벨 "12 tables") | `u1-pytest-all-final` · `u1-ruff-final` · `u1-schema-check-final` |
| 변이 10종(정본, 사본·전용 DB) | `bash run_mutants.sh V1-*` | 10/10 실패(V1-5 는 ⑦ 단언이 아니라 **픽스처 setup 의 `DuplicateTable`** 로 걸린다 — 11건 전체 error). `u1-mutations` 는 V1-5 오염으로 superseded | `u1-mutations-v2` |
| F-1 수정 — fixture 가 전체 환경 사본을 내주지 않음(바뀐 키만, repr 은 키 이름만) | 단독 `tests/test_migration_0003.py` | 11 passed | `u1-fix-standalone` |
| F-1 — 일부러 실패시킨 출력(V1-1, DB `relationship_test_mig_v15`)에 환경변수 값이 없다 | `bash run_mutants.sh V1-1` | `'env': <_EnvOverrides keys=…>` 로만 나오고 값·비밀번호 없음(접속 URL 은 `***`) | `u1-fix-forced-failure` |
| F-1 수정 후 전체 pytest · ruff | 전체 명령 | 2272 passed · 0 failed · skip 0 · All checks passed | `u1-fix-pytest-all` · `u1-fix-ruff` |
| 개발 DB 비우기 | `.venv/bin/python -m alembic upgrade head`(전 `u1-dev-before-counts` 인물 12 → 후 `u1-dev-after-counts` 전부 0) | `Running upgrade 0002 -> 0003` | `u1-dev-before-counts` · `u1-upgrade` · `u1-dev-after-counts` |
| `schema_check.py` | `.venv/bin/python scripts/schema_check.py` | 전부 PASS(FK 8·인덱스 13) | `u1-schema-check` |
| ruff · mypy · tools_check | 판정 표 11·공통 회귀 명령 | All checks passed · 새 오류 없음(38/38) · 7/7 | `u1-ruff` · `u1-mypy` · `u1-tools-check` |
