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

## U2 — 인증 코어 (backend-agent, 2026-11-15)

새 파일 4개, 새 시험 **117건**(`test_auth_passwords.py` 16 · `test_auth_settings.py` 14 · `test_auth_api.py` 42 · `test_auth_origin.py` 45). `[n]` 은 parametrize 건수. 증거 이름의 시각 접두는 `20261115-2122-`(변이는 `2125-`). 명령 기본형: `POSTGRES_PORT=5433 .venv/bin/python -m pytest <파일> -q`. 비밀번호는 전부 시험용 문자열.

### `tests/test_auth_passwords.py` (DB 불필요)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_hash_differs_from_plaintext_and_has_no_plaintext_substring` — 해시 ≠ 평문, 평문이 해시에 들어 있지 않다 | 위 기본형 | passed | `u2-auth` |
| `test_same_password_hashed_twice_differs_by_salt` — 같은 비밀번호 두 번 해시가 다르고 솔트 필드도 다르다 | 같음 | passed | `u2-auth` |
| `test_format_carries_parameters_and_sizes` — `scrypt$16384$8$1$…`, 솔트 16B·해시 32B 를 값으로 단언(M-20 이 잡음) | 같음 | passed | `u2-auth` · `u2-mutations` |
| `test_parse_hash_returns_components` — `(16384, 8, 1, 솔트 16B, 해시 32B)` | 같음 | passed | `u2-auth` |
| `test_parse_hash_rejects_malformed` [7] — 깨진 형식은 `None`, `verify_password` 는 예외 없이 False | 같음 | passed | `u2-auth` |
| `test_verify_right_and_wrong_password` — 맞는/틀린/빈 비밀번호 | 같음 | passed | `u2-auth` |
| `test_verify_uses_parameters_from_stored_string` — 저장 문자열의 파라미터(n=1024)로 검증 | 같음 | passed | `u2-auth` |
| `test_verify_handles_non_ascii_password` — 한글 비밀번호 | 같음 | passed | `u2-auth` |
| `test_dummy_hash_is_valid_format_and_cached` — 더미 해시는 유효 형식·프로세스당 한 번 | 같음 | passed | `u2-auth` |
| `test_verify_uses_constant_time_compare` — `hmac.compare_digest` 가 정확히 1번 불린다(V2-1 은 기능 테스트로 안 잡혀 호출 여부를 직접 단언) | 같음 | passed(V2-1 변이가 실패시킴) | `u2-mutations` |

### `tests/test_auth_settings.py` (DB 불필요)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_auth_constants_match_the_plan` — 7일·8~128자·`[a-z0-9_]{3,20}`·쿠키 이름 두 개를 값으로 | 같음 | passed | `u2-auth` |
| `test_auth_cookie_secure_values` [6] — 없음/빈값/1/true → 켬, 0/false → 끔 | 같음 | passed | `u2-auth` |
| `test_auth_cookie_secure_rejects_unknown_values` [4] — `yes`·`2`·`False`·`off` 는 `InvalidValue` | 같음 | passed | `u2-auth` |
| `test_auth_cookie_secure_reads_os_environ_when_env_omitted` — `env` 생략 시 `os.environ` | 같음 | passed | `u2-auth` |
| `test_cookie_name_follows_secure_flag` — `__Host-rel_session`/`rel_session`, 설정 따라 바뀜 | 같음 | passed | `u2-auth` |
| `test_hash_token_is_sha256_hex` — `sha256(token)` hex 64자 | 같음 | passed | `u2-auth` |

### `tests/test_auth_api.py` (`dbtest`, 롤백 세션, `https://testserver`)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_signup_201_body_and_cookie_attributes` — 201 `{id, username}`·id 32자 hex·쿠키 `__Host-rel_session`·HttpOnly·SameSite=lax·Path=/·Secure·Max-Age=604800·Domain 없음 | 기본형 | passed(V2-3·V2-4·M-23·M-24·M-25 가 실패시킴) | `u2-auth` · `u2-mutations` |
| `test_cookie_name_secure_on_is_host_prefixed_without_domain` — Secure 켬 이름·Domain 없음(V2-8) | 같음 | passed | `u2-auth` |
| `test_cookie_name_secure_off_is_plain_without_secure_attribute` — `AUTH_COOKIE_SECURE=0`+http: `rel_session`·Secure/Domain 없음·Path=/·http 로도 쿠키가 실려 `/auth/me` 200 | 같음 | passed | `u2-auth` |
| `test_signup_normalizes_username_to_lowercase` — `DemoUser`→`demouser`, `DEMOUSER` 로 로그인(M-16) | 같음 | passed | `u2-auth` |
| `test_signup_duplicate_409_username_taken` — 409 본문, 대소문자만 다른 것도 409, 행 1개(M-26) | 같음 | passed | `u2-auth` |
| `test_signup_invalid_username_422` [8] — `ab`·21자·공백·한글·`-`·`\n` 끝·`.`·빈 값 → `invalid_username` | 같음 | passed | `u2-auth` |
| `test_signup_username_boundaries_accepted` [4] — 3자·20자·밑줄·숫자만 통과(M-19) | 같음 | passed | `u2-auth` |
| `test_signup_invalid_password_422` [3] — 빈 값·7자·129자 → `invalid_password`(M-17·M-18) | 같음 | passed | `u2-auth` |
| `test_signup_password_length_boundaries_accepted` [3] — 8자·128자·한글 통과 | 같음 | passed | `u2-auth` |
| `test_signup_validation_error_body_does_not_echo_password` — 형식 오류 422 본문에 비밀번호 0(M-22) | 같음 | passed | `u2-auth` |
| `test_login_200_sets_cookie` — 200 `{id, username}`+쿠키, 이어서 `/auth/me` 200 | 같음 | passed | `u2-auth` |
| `test_login_failures_share_one_response_for_unknown_user_and_wrong_password` — 없는 아이디·틀린·129자 비밀번호가 같은 401·같은 본문·쿠키 없음(V2-6) | 같음 | passed | `u2-auth` |
| `test_login_runs_a_hash_verification_even_for_unknown_user` — 없는 아이디에도 `verify_password` 1회(M-21) | 같음 | passed | `u2-auth` |
| `test_me_with_cookie_200_without_401` — 쿠키 있으면 200 본문 일치, 없으면 401 `unauthenticated` | 같음 | passed | `u2-auth` |
| `test_me_with_unknown_token_401` — 모르는 토큰 401 | 같음 | passed | `u2-auth` |
| `test_logout_without_cookie_401` — F-3, 쿠키 없이 401(V2-10) | 같음 | passed | `u2-auth` |
| `test_logout_204_no_body_clears_cookie_and_deletes_row` — 204·본문 없음·삭제 쿠키(Max-Age=0·Path=/)·행 −1·같은 쿠키 다시 실으면 401(V2-5·M-27) | 같음 | passed | `u2-auth` |
| `test_logout_without_body_is_accepted` — 본문 없는 로그아웃 204 | 같음 | passed | `u2-auth` |
| `test_logout_removes_only_that_session` — 한 기기 로그아웃이 다른 기기 세션을 끊지 않는다 | 같음 | passed | `u2-auth` |
| `test_session_expiry_boundary_is_exclusive_at_seven_days` — T0+7일−1초 200, T0+7일 401, +1초 401(M-11) | 같음 | passed | `u2-auth` |
| `test_session_expires_at_uses_configured_days` — `expires_at == T0 + 7일`(M-12) | 같음 | passed | `u2-auth` |
| `test_password_hash_has_no_plaintext_substring` — DB 해시에 평문·앞 8자 0, scrypt 형식(판정 #1 `-k plaintext`) | 같음 | passed | `u2-auth` · `u2-hash-grep` |
| `test_token_hash_is_sha256_of_cookie_not_the_cookie` — `token_hash` ≠ 쿠키, `== sha256(쿠키)`(V2-2) | 같음 | passed | `u2-auth` |
| `test_auth_endpoints_write_no_agent_traces` — `/auth/*` 는 `agent_traces` 를 쓰지 않는다 | 같음 | passed | `u2-auth` |
| `test_non_json_content_types_are_rejected_and_write_nothing` [3: `/chat`·`/answers/1`·`/push/subscriptions`] — 쿠키를 가진 채 `text/plain`·폼 → 415/422, `persons`·`events`·`pending_questions`·`push_subscriptions`·`agent_traces` 행 수 불변(V2-9) | 같음 | passed | `u2-auth` · `u2-mutations` |
| `test_answers_route_with_json_content_type_is_reached_control` — 대조군: JSON 콘텐츠 타입이면 라우트에 닿아 404 | 같음 | passed | `u2-auth` |

### `tests/test_auth_origin.py` (앞 표 부분은 DB 불필요, 뒤는 `dbtest`)

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_origin_matches_table` [21] — 같은 호스트·기본 포트 양쪽 제거·비기본 포트·https 에 `:80`·소문자·XFH 우선·쉼표 첫 값·`null`·스킴 없음·알 수 없는 스킴·빈 값·경로 붙은 Origin(M-13·M-14·M-15·M-30) | 기본형 | passed | `u2-origin` |
| `test_unsafe_methods_set_is_exactly_the_four_state_changing_methods` — POST·PUT·PATCH·DELETE 만(M-28·M-29) | 같음 | passed | `u2-origin` |
| `test_evil_origin_post_is_403_bad_origin_and_changes_nothing` [4: `/auth/logout`·`/briefings/run`·`/chat`·`/auth/signup`] — `Origin: https://evil-1-2-3-4.sslip.io` → 403 `bad_origin`, users·auth_sessions·persons·events·pending_questions·push_subscriptions·agent_traces 행 수 불변(V2-7) | 같음 | passed | `u2-origin` · `u2-mutations` |
| `test_evil_origin_logout_keeps_the_session_alive` — 위조 로그아웃 뒤에도 같은 쿠키로 `/auth/me` 200 | 같음 | passed | `u2-origin` |
| `test_every_state_changing_method_is_checked_before_routing` [4: POST·PUT·PATCH·DELETE] — 라우트가 없어 405 일 경로도 Origin 이 먼저 403 | 같음 | passed | `u2-origin` |
| `test_safe_methods_are_not_checked` [3: GET·HEAD·OPTIONS] / `test_get_with_other_origin_is_not_403` — 안전 메서드는 다른 Origin 이어도 403 아님 | 같음 | passed | `u2-origin` |
| `test_same_host_origin_passes` — 같은 호스트 Origin 로그아웃 204 | 같음 | passed | `u2-origin` |
| `test_no_origin_header_passes` / `test_same_origin_without_login_reaches_route_with_401_not_403` — Origin 없음·같은 출처는 라우트에 닿아 401(403 아님) | 같음 | passed | `u2-origin` |
| `test_x_forwarded_host_equal_to_origin_passes` / `test_origin_not_equal_to_host_without_forwarded_host_is_403` — XFH 와 같은 Origin 통과, XFH 없이 Host 와 다르면 403 | 같음 | passed | `u2-origin` |
| `test_default_port_origin_passes` / `test_non_default_port_origin_is_403` — `https://testserver:443`↔`Host: testserver` 통과, `:8443` 은 403 | 같음 | passed | `u2-origin` |
| `test_uppercase_origin_host_passes` — `https://TestServer`↔`testserver` 통과 | 같음 | passed | `u2-origin` |
| `test_x_forwarded_host_uses_first_value_only` — `testserver, evil.example` 통과, `evil.example, testserver` 403 | 같음 | passed | `u2-origin` |
| `test_null_origin_is_403` — `Origin: null` 403 | 같음 | passed | `u2-origin` |

### 전체·회귀·변이

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| U1 리뷰 R-8·R-9 반영 후 `tests/test_migration_0003.py` | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_migration_0003.py -q` | 11 passed(시험 수·검출력 불변) | `u2-migration` |
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2389 passed**(2272 + 117) · 0 failed · skip 0 | `u2-pytest-all` |
| ruff · mypy · tools_check · `alembic check` · `schema_check` | 판정 표 11·공통 회귀 | All checks passed · 새 오류 없음(38/38) · 7/7 · `No new upgrade operations detected.` · PASS(리비전 0003) | `u2-ruff` · `u2-mypy` · `u2-tools-check` · `u2-alembic-check` · `u2-schema-check` |
| ER·평가 무변경 | `git diff --stat 08c1b49..HEAD -- app/er evaluation reports data` | 빈 출력 | `u2-er-unchanged` |
| 변이 31종(저장소 밖 사본) | `bash run_all.sh`(스크래치패드) → `run_mutant.py <id>` 변이마다 `--append` | 31/31 실패(KILLED) · 보조 V2-9b(`strict_content_type=False`)는 이 시점엔 살아남음 — **정정(review-u2 §6)**: 콘텐츠 타입 *없는* 본문은 실제 회귀 경로다. 아래 "리뷰 보완" 의 시험이 잡는다 | `u2-mutations` |

### U2 리뷰 보완 (review-u2 F-1·F-2·R-1·R-2·R-3·R-8, 2026-11-15) — 새 시험 37건

`test_auth_api.py` +36(42→78) · `test_auth_passwords.py` +1(16→17). 아래 표는 함수 단위. 명령 기본형은 위와 같다. 전체 **2426 passed**(2272+154)·0 failed·skip 0.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `test_login_with_malformed_username_is_the_same_401_and_still_runs_one_hash` [9: NUL·NUL 만·서로게이트·21자·10만자·빈 값·한글·공백·`\n` 끝] — **F-1** 같은 401 `invalid_credentials` 본문(없는 아이디와 바이트 동일)·쿠키 없음·`verify_password` 정확히 1회가 더미 해시로(F-1 변이 잡힘) | 기본형 | passed | `u2-fix-auth` · `u2-fix-mutations` |
| `test_signup_with_unencodable_password_is_422_and_creates_no_user` — **F-2** 짝 없는 서로게이트 비밀번호 가입 422 `invalid_password`·`users` 행 수 불변(F-2 변이 잡힘) | 같음 | passed | 같음 |
| `test_login_with_unencodable_password_is_the_same_401` — F-2 로그인도 같은 401 | 같음 | passed | `u2-fix-auth` |
| `test_unencodable_password_is_explicitly_rejected_not_an_accident` — `is_utf8_encodable` 값 단언, `verify_password` 가 `_derive` 호출 전에 False(우연한 `except ValueError` 아님, F-2b 변이 잡힘) | 같음 | passed | `u2-fix-mutations` |
| `test_auth_string_inputs_never_cause_a_server_error` [4: signup/login × username/password] — NUL·섞인 NUL·짝 없는 서로게이트·10만자·빈 값 + 타입 None·123·True·1.5·[]·{}·["a"]·{"a":1} 를 넣어 전부 4xx(401/422)·`Traceback` 없음·`users` 행 수 불변 | 같음 | passed(500 경로 0) | `u2-fix-auth` |
| `test_logout_endpoint_input_never_causes_a_server_error` [14] — 로그아웃 `endpoint` 에 같은 이상 값 → 204 또는 422, 500 없음 | 같음 | passed | 같음 |
| `test_login_with_over_128_chars_password_skips_the_hash` — **R-3** 129자 로그인 `verify_password` 호출 0·같은 401(R-3a 변이 잡힘) | 같음 | passed | `u2-fix-mutations` |
| `test_signup_validation_error_body_does_not_echo_password`(확장) — **R-3** 로그인(누락·타입 오류)·로그아웃 422 에도 비밀번호 되울림 0·`input` 키 없음 | 같음 | passed | `u2-fix-auth` |
| `test_json_shaped_body_without_content_type_is_rejected_and_writes_nothing` [5: `/chat`·`/answers/1`·`/push/subscriptions`·`/auth/signup`·`/auth/login`] — **R-1** 콘텐츠 타입 헤더 없는 JSON 모양 본문 4xx·행 수 불변(V2-9b 변이 잡힘) | 같음 | passed | `u2-fix-mutations` |
| `test_logout_clear_cookie_keeps_secure_and_plain_name_when_off` — **R-2** 삭제 쿠키 켬: `__Host-`·Secure·Path=/·Domain 없음, 끔: `rel_session`·Secure 없음·Max-Age=0(R-2·R-2b 변이 잡힘) | 같음 | passed | `u2-fix-mutations` |
| 전체 pytest · ruff(`alembic` 포함) · mypy | 전체 명령 | 2426 passed · All checks passed · 새 오류 없음(38/38) | `u2-fix-pytest-all` · `u2-fix-ruff` · `u2-fix-mypy` |
| 변이(저장소 밖 사본) | `run_fix.sh` | F-1·F-2·F-2b·R-3a·R-2·R-2b·V2-9b·V2-7a·V2-1 전부 잡힘 | `u2-fix-mutations` |

## U3a — 기존 테스트 이관·로그인 도우미 (backend-agent, 2026-11-15)

> 동작 불변. `app/` diff 0, 기존 단언 변경 0. 새 시험은 도우미 자체 시험 13건뿐. 증거 접두 `20261115-HHMM-u3a-`.

| 확인 항목 | 명령 | 결과 | evidence |
|---|---|---|---|
| `make_user` — `id == "local"` 행 생성, 같은 id 재호출은 같은 객체·행 1개 | `pytest tests/test_auth_helpers.py` | passed | `u3a-pytest-all-final2` |
| `make_user` — 사용자 지정 id·username 값 | 같음 | passed | 같음 |
| `make_user` — `password_hash == NO_LOGIN_HASH` 이고 `verify_password` 가 False(이 사용자로 로그인 불가) | 같음 | passed | 같음 |
| `make_ctx` — `user_id` 기본 `"local"`·`session_id` 기본 `"test-session"`, 인자로 바꾸면 그 값 | 같음 | passed | 같음 |
| `logged_in_client`(세션) — 쿠키 값의 sha256 == `auth_sessions.token_hash`(행 1개)·원문과 다름·`GET /auth/me` == `{"id","username"}` | 같음 | passed | 같음 |
| `logged_in_client` 기본 사용자는 `"local"`(`/auth/me` id) | 같음 | passed | 같음 |
| `logged_in_client` 두 번 호출 — `users` 행 1개·`auth_sessions` 행 2개 | 같음 | passed | 같음 |
| 쿠키 이름이 설정을 따른다 — 켬 `__Host-rel_session`(접두 없는 이름 없음), 끔 `rel_session` + `/auth/me` 200 | 같음 | passed | 같음 |
| 쿠키 제거 뒤 `/auth/me` 401 | 같음 | passed | 같음 |
| `logged_in_client`(세션 팩토리) — 별도 세션에 커밋된 `users`·`auth_sessions` 각 1행(시험이 직접 정리) | 같음 | passed | 같음 |
| `committed_login` — 안에서 커밋 행 보임(username `helper-` 접두), 나오면 사용자·세션 행 0 | 같음 | passed | 같음 |
| `committed_login` — 본문이 예외를 내도 행 0(정리 보장) | 같음 | passed | 같음 |
| `committed_login` 기본값 — 두 번 호출한 `user_id`·`username` 이 서로 다르다 | 같음 | passed | 같음 |
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q` | **2439 passed**(2426 + 13)·실패 0·skip 0(리뷰 F-1 수정 뒤 재실행도 2439 — `u3a-fix-pytest-all`) | `u3a-pytest-all-final2` |
| ruff · mypy · tools_check | 판정 방법 공통 회귀 | All checks passed · 새 오류 없음(38/38) · 7/7 | `u3a-ruff-final` · `u3a-mypy-final` · `u3a-tools-check-final` |
| `app/`·`evaluation`·`reports`·`data`·`scripts` 무변경 | `git diff --stat -- app evaluation reports data scripts` | 빈 출력 | `u3a-er-unchanged` · `u3a-app-diff-final` |
| 테스트 쪽 고정 사용자 언급 목록 | `bash <SCR>/u3a-tests-fixed-user.sh`(`grep -rnE 'app_user_id|APP_USER_ID' tests scripts evaluation --include='*.py'`) | exit 0, 일치 = `test_settings.py`(U5)·`test_commit_boundaries.py:81,181,293`(U3b)·주석 2곳 | `u3a-tests-fixed-user-final` |
| 평가 러너 불변(참고) | `pytest tests/test_eval_runner.py tests/test_run_pilot_eval.py tests/test_baseline_parity.py` | 145 passed | `u3a-eval-runner-tests` |
| **변이 V3a-1**(저장소 밖 사본: `ToolContext.user_id` 기본값·`app_user_id()` 삭제 + 호출자 리터럴 치환, `test_settings`·`test_commit_boundaries`·(사본에 .git 없어 `test_infra_files`) 제외) | `bash <SCR>/run-v3a1.sh` | 이관 전: **30건 실패**(`test_tools_questions.py` `**kwargs` 도우미의 `user_id` 누락) → 고친 뒤 **2393 passed 실패 0** | `u3a-mutation-v3a1-run2`(실패) · `u3a-mutation-v3a1-run3`(통과) · `u3a-mutation-v3a1`(스크립트 정규식 오류로 변이 전 중단, exit 3) |

도우미 변이(저장소 밖 사본의 `tests/auth_helpers.py` 만 치환, `evidence/20261115-2205-u3a-helper-mutations.txt`, 각 변이는 `-x` 로 첫 실패에서 멈춤):

| 변이 | 잡은 시험(실제 결과) |
|---|---|
| H-1 쿠키 이름 `"__Host-rel_session"` 하드코딩 | `test_logged_in_client_cookie_name_follows_setting` — `['__Host-rel_session'] == ['rel_session']` |
| H-2 `make_user` 가 `user_id` 인자를 무시(`"local"` 고정) | `test_make_user_custom_id_and_username` |
| H-4 `committed_login` 기본 id·username 고정 | `test_committed_login_default_ids_differ_per_call` |
| H-5 `make_user` 멱등 제거 | `test_make_user_uses_given_id_and_is_idempotent` — `pk_users` UniqueViolation |
| H-6 쿠키 값을 엉뚱한 문자열로 | `test_logged_in_client_session_row_matches_cookie` — 해시 불일치(토큰 값은 메시지에 없음) |

(번호 H-3 이 빠진 것은 아래 "돌리지 않은 변이"인 `committed_login` 정리 제거 변이의 자리이기 때문이다.)

**돌리지 않은 변이**: `committed_login` 의 `finally` 정리 제거 — 공유 시험 DB 에 커밋 행이 남아 이후 시험을 오염시킬 수 있어 일부러 돌리지 않았다. 그 보장은 `test_committed_login_cleans_up_even_when_body_raises`(예외 경로)·`…commits_then_cleans_up` 이 값(행 0)으로 단언하며, 변이 시험 뒤 시험 DB 잔여 행 0 을 `evidence/20261115-2205-u3a-test-db-leftover.txt` 로 확인했다. 첫 변이 실행(`…-2204-…`)은 사본에 `tests/tests` 중첩 사본이 생겨 변이가 적용되지 않은 채 전부 통과로 나왔으므로 폐기하고 다시 돌렸다.

## U3b — 모든 API 를 로그인 사용자 기준으로 (backend-agent, 2026-11-16)

새 시험 29건(`test_auth_required_routes.py` 11 · `test_user_isolation.py` 18), 전체 **2468 passed**(2439 + 29)·실패 0·skip 0(`evidence/20261116-0009-u3b-pytest-all.txt`). 증거 파일 이름의 접두는 `20261116-00NN-`.

### `tests/test_auth_required_routes.py` (`dbtest` 표식 없음 — DB 접속 없이 돈다, 빈 세션을 끼워 쿼리가 나가면 오류)

| 시험 | 단언 값 |
|---|---|
| 열거 라우트가 알려진 보호 대상 13개를 모두 포함하고 면제 집합이 정확히 7개(`/health`·`/auth/signup`·`/auth/login`·문서 4) | 집합 동일 |
| 면제가 아닌 **모든** 라우트가 쿠키 없이 401 + 본문 `{"detail":{"code":"unauthenticated"}}` (경로 매개변수 `1`) | 상태 401·본문 일치, 검사된 목록이 보호 대상 13개를 포함 |
| `POST /auth/logout` 쿠키 없이 401(F-3 — 예외 아님) | 401·본문 |
| `/auth/signup`·`/auth/login` 은 401 이 아니라 422(공개 유지) | 422 |
| `PUSH_DEV_PAGE_ENABLED=1` 이면 `/push-dev/` 세 경로만 더 생기고 그 밖의 새 면제 없음 | 세 경로 집합 |
| 면제가 아닌 모든 `APIRoute` 의 의존성 트리에 `current_user` 가 있다(구조 검사) | 누락 `[]` |
| `app.auth.deps`·`app.auth.routes`·`app.api.deps`·`app.api.routes`·`app.main` 을 새 인터프리터에서 **맨 먼저** import 해도 순환 오류 없음(5건) | returncode 0 |

### `tests/test_user_isolation.py` (`dbtest`, 롤백 세션 — 계정 A·B·(C), B 의 인물·별칭("민수")·사건·사실·일정·브리핑 trace·질문을 직접 삽입)

| 시험 | 단언 값 |
|---|---|
| `GET /persons` — A 목록 id 가 `[A 인물]` 뿐, "민수" 문자열 0, B 쪽도 대칭 | id 리스트 |
| `GET /persons/{B}` 404 == 없는 id 404(상태·본문 같음), 내 카드 200 | `{"detail":{"code":"not_found"}}` |
| `GET /events/{B}/raw` 404 == 없는 id, B 원문 문자열 응답에 0, 내 원문 200 | 같음 |
| `GET /persons/{B}/facts/{f}/sources` 404 == 없는 id, 내 인물+B 사실 섞어 넣기도 404, 내 근거 200 | 같음 |
| `GET /briefings` 에 B 일정 0(`[A 일정]`), `?schedule_id={B}` 404 == 없는 id | 같음 |
| `POST /briefings/run {schedule_id: B}` 404 == 없는 id, B 일정 `briefed_at` 불변, 행 수 전부 불변, 문장 생성기 호출 0 | 같음 |
| `POST /briefings/run`(본문 없음) — B 일정이 창 안에 있어도 A 의 일정만 브리핑, B `briefed_at` None | `[A 일정]` |
| `POST /push/subscriptions` — 저장 행 `user_id` 가 로그인 계정(`iso-user-a`) | 쌍 일치 |
| `GET /questions/pending` — 내 채팅방 질문만, **세션 이름이 `chat:A` 여도 소유가 B 인 질문은 제외**, B 는 B 질문만 | id 리스트 |
| `POST /answers/{B 질문}` 404 == 없는 id, 질문 행 `answer`·`answered_at` None, **재개 루프 호출 0**, 모든 테이블 행 수 불변 | 호출 수 0 |
| 세션 이름은 `chat:A` 이고 소유가 B 인 질문에 A 가 답하면 404·불변·재개 0 | 같음 |
| 툴 층 — `answer_question(ctx_A, B 질문)` → `QuestionNotFound`·행 불변, B 의 ctx 로는 `answered`(통제) | 예외·상태 |
| 통제+ER 격리 — 빈 계정 C 가 B 와 같은 별칭 "민수" 로 말하면 후보 0(`er_resolve.candidates == []`)·`new_person` 질문, 질문 행 `user_id`=C·`session_id`=`chat:C`, A·B 는 답할 수 없고(재개 0), C 가 답하면 인물이 C 의 id 로 생기고 재개 정확히 1회, 늘어난 것은 인물 +1·사건 +1 뿐 | 값 |
| `POST /chat` 응답 `session_id` == `chat:A`, `X-Session-Id: chat:B` 를 보내도 같고 trace 세션에 `chat:B` 0 | 문자열 |
| 헤더 없는 B 의 `/chat` 도 `chat:B` | 문자열 |
| ER 이 (가정상) B 의 인물을 골라도(`resolve` 결과를 B 로 치환) 200 오류 답·`loop_error` 1행 `PersonNotFound`·B 의 사건·별칭·`chat:B` trace 불변 | 값 |
| A 의 ctx 로 B 인물에 `add_event`·`get_briefing`·`add_schedule`·`update_person` → 각각 `PersonNotFound`, B 일정 `briefed_at` None, 행 수 불변 | 예외·불변 |
| `ToolContext.user_id` 기본값 없음 — `inspect.signature` 의 `default is empty`, `ToolContext(session=…, session_id=…)` 가 `TypeError` | 값 |

### 변이 17종 — 저장소 밖 사본(`…/scratchpad/p9b-u3b/copy`)에서 변이 하나씩, 관련 9개 시험 파일(124건)만(`evidence/20261116-0011-u3b-mutations.txt`)

| 변이 | 잡은 시험(요약) |
|---|---|
| V3b-1 `GET /briefings` 에서 `current_user` 제거(가짜 사용자) | `test_every_non_exempt_route_requires_login`(UnboundExecutionError — 인증 없이 DB 로 감)·`…declares_current_user_dependency`(`[('GET','/briefings')]`)·`test_briefings_list_and_schedule_filter_are_scoped` |
| V3b-2 `build_ctx` 의 소유 조건 제거 | `test_answering_other_users_question_is_404_no_change_no_resume` — 응답은 툴 층 방어로 똑같이 404 지만 그 툴이 `tool_error` trace 행을 한 줄 남겨 **행 수 동일 단언**이 깨진다(운영은 라우트 예외가 롤백해 trace 도 사라지므로 외부 차이는 없는 이중 방어) |
| V3b-2b `answer_question` 의 소유 조건 제거 | `test_answer_question_tool_rejects_other_users_question`(DID NOT RAISE) |
| V3b-2c 두 소유 조건 모두 제거 | 4건 — `/answers` 409(답이 저장됨)·`DID NOT RAISE`·통제 흐름의 `200 == 404` |
| V3b-3 `/chat` 이 `X-Session-Id` 헤더를 다시 받음 | `test_chat_session_id_is_account_session_and_header_is_ignored`(`chat:B` ≠ `chat:A`)·`test_api_chat` 3건 |
| V3b-4 `ToolContext.user_id` 기본값 복원 | `test_tool_context_user_id_has_no_default` (+ 판정 `u3b-ctx-default` grep) |
| V3b-5 `list_persons` 에 고정 문자열 | `test_persons_list_has_only_my_persons` |
| V3b-6 `list_pending` 의 `user_id` 조건 제거 | `test_pending_questions_list_has_only_my_chatroom_questions`(`[A질문, B질문]`) |
| V3b-7 푸시 구독 저장에 고정 문자열 | `test_push_subscription_belongs_to_the_logged_in_user` |
| V3b-8 브리핑 ctx 의 사용자를 고정 문자열로 | `test_briefing_run_without_body_only_briefs_my_schedules` |
| V3b-9 채팅 ctx 의 사용자를 고정 문자열로 | 5건(`test_commit_boundaries` 3건 포함) |
| V3b-10 `chat_session_id` 가 계정과 무관한 상수 | 20건(세션 id 단언 전반) |
| V3b-11 `app.auth.deps` 가 다시 `app.api.deps` 에서 `get_session` import(순환) | 수집 단계에서 9개 파일 전부 ERROR(`import app.main` 부터 깨짐) — 순서 시험은 수집 전에 막혀 돌지 못함 |
| V3b-12 인물 카드 조회를 고정 문자열로 | `test_person_card_of_other_user_is_404_same_as_missing`(내 카드 404) |
| V3b-13 이벤트 원문 조회를 고정 문자열로 | `test_event_raw_of_other_user_is_404_same_as_missing` |
| V3b-14 브리핑 목록 조회를 고정 문자열로 | `test_briefings_list_and_schedule_filter_are_scoped` |
| V3b-15 (시험 쪽) `test_api_read_persons` 의 SELECT 계수기에서 인증 조회 제외 줄 삭제 | `test_목록_SELECT_수는_인물_수와_무관한_상수` — `3 == 2` |

### 바꾼 기존 단언·헬퍼(닫힌 목록 ①②③ 대조) — 03-log "U3b 구현 메모(초안)" 에 파일:줄 전/후 전부

① 422 `invalid_session_id` → "무시되고 200": `test_api_chat.py`(`…invalid_session_id_header_is_ignored_and_returns_200`)·`test_api_questions_pending.py`(`…형식_위반_세션_헤더는_무시되고_계정_목록이_나온다`) ② `session_id` 기대 → `chat:<user_id>`: `test_api_chat.py` 3곳·`test_api_chat_query.py` 1곳 ③ 헤더 없는/다른 세션 헤더 `/questions/pending` 의 빈 목록 기대 → 계정 기준 목록: `test_api_questions_pending.py` 2곳. 단언 변경이 아닌 것: `SID`·trace 조회 조건을 `chat:local` 로(`test_api_answers_resume.py`·`test_api_chat.py` 2곳·`test_api_chat_query.py`·`test_api_questions_pending.py`), `test_commit_boundaries.py` 3곳 `committed_login`. **닫힌 목록 밖 1건**: `test_api_read_persons.py::_count_selects`(인증 SELECT 1건 제외 — 기대값 `== 2` 는 그대로, 보고 참조).

## U4 — 계정당 채팅방 하나: 대화 기록 저장과 `GET /chat/history` (backend-agent, 2026-11-16)

새 시험 20건(`tests/test_chat_history.py`), 전체 **2491 passed**(2471 + 20)·실패 0·skip 0(`evidence/20261116-0045-u4-pytest-final.txt` 계열). 기존 시험 단언은 바꾸지 않았고, 아래 R-10·R-11 시험 보강 2곳만 `test_user_isolation.py` 에서 고쳤다.

### `tests/test_chat_history.py` (`dbtest`, `env` 픽스처 = 운영 `get_session` 과 같은 commit/rollback 규약을 SAVEPOINT 위에 올림. 준비 데이터는 `db_session.commit()` 으로 확정해 요청이 롤백돼도 남는다)

| 시험 | 단언 값 |
|---|---|
| 채팅 2턴 + 답변 1회(신원 거절 흐름) 뒤 6행이 순서대로 | `(role, content, question_id)` 6쌍 — `(user, 발화1, None)·(assistant, 응답1, q1)·(user, "아니요, 다른 사람이에요", q1)·(assistant, 응답2, q2)·(user, 발화2, None)·(assistant, 응답3, None)`, id 단조 증가 |
| 응답 한 줄의 모양이 프론트 `ChatHistoryItemOut` 과 같다 | 키 집합 `{id, role, content, question_id, created_at}`, `id` int, `created_at` 타임존 포함 ISO |
| `limit=2·1·5·200` 은 최근 N 행을 오래된 것부터 | 전체 목록의 끝 N 개와 같다 |
| 기본 50 · 최대 200 | 상수 `(50, 200)`, 줄 60개일 때 기본 = 줄 10~59(50개), `limit=200` = 60개 |
| `limit` 0·201·-1·abc | 422 (4건) |
| 정렬 키 `(created_at, id)` — id 와 시각을 어긋나게 둔 4행(r3·r4 는 시각 동률) | 전체 `[r2,r3,r4,r1]`, `limit=2` → `[r4,r1]`, `limit=1` → `[r1]`, API `limit=3` → `[r3,r4,r1]` |
| 같은 트랜잭션 6행(`created_at` 동률)은 삽입(id) 순서 | `limit=4` → `[t2,t3,t4,t5]` |
| `append` 가 모르는 role 을 거부 | `ValueError`·행 수 불변 |
| 계정 B 의 기록은 A 에 섞이지 않는다(양방향) | A 6행·B 1행(`"B 만의 말 ZXCV"`), 서로의 문자열 0 |
| B 가 `/chat` 하면 B 에만 2행 | B 2·A 0·A 의 기록 `[]` |
| B 가 A 의 질문에 `/answers` → 404 | 어느 쪽도 행 수 불변(A 2·B 0) |
| 쿠키 없이 `GET /chat/history` | 401 (`limit` 있어도 401) |
| `GET /chat/history` 읽기 전용 | 6번 읽은 뒤 `chat_messages`·`agent_traces` 행 수 불변 |
| `/chat` 이 DB 오류로 500 이면 그 요청의 기록 0 (앞선 성공 턴 2행은 남음) | 행 수 2, 발화 문자열 없음 |
| `/answers` 가 DB 오류로 500 이면 그 요청의 기록 0 | 행 수 2, 답 문자열 없음 |
| `/chat` 에서 루프가 오류를 삼켜 200 이면 사용자 행 + 응답 행 저장 | `[(user, 발화, None), (assistant, 오류 한 줄, None)]` |
| `/answers` 에서 루프가 오류를 삼켜 200 이면 답 행(`question_id=q`) + 응답 행(None) 저장 | 4행, 끝 2행 일치 |

### R-10·R-11 (`tests/test_user_isolation.py`)

- R-10: `world` 픽스처가 `answerer_from_env` 를 `_EchoAnswerer`(카드의 이름·사실 값을 한 줄로 되돌림 — 길면 검증이 거부해 서식 답으로 바뀌어 새어 나간 내용이 보이지 않는다)로 바꿔 끼운다. 변이 VR10(`_read_card` 가 소유자 무시) → `[identity_query]` 가 **`assert '등산' not in …` 단언**으로 실패(OpenAIError 아님, 사본에서 `--tb=line` 으로 확인).
- R-11: `status_code in (200, 404)` → `== 200` + `stored == {persons:0, events:0, schedules:0}`.

### 변이 23종 — 저장소 밖 사본(`…/scratchpad/p9b-u4/copy`)에서 하나씩, 관련 6개 시험 파일(85건)만(`evidence/20261116-0042-u4-mutations-final.txt`; 실제 커밋형 시험은 넣지 않음. 앞서 돈 `…-0039-u4-mutations.txt` 는 R-10 보강 전이라 VR10 이 엉뚱한 시험에서 잡힌 시험 중간 산물 — 최종은 `-final`)

| 변이 | 잡는 시험 |
|---|---|
| V4-1a `recent` 의 `reversed` 제거(최근→오래된 순) | 순서·`limit`·정렬 시험 9건 |
| V4-1b 최근 N 고르기의 2차 키 `id.desc()`→`asc()` | 6행 순서·기본 50·정렬 키·동일 트랜잭션 순서 등 8건 |
| V4-1c `created_at` 키 삭제(id 만) | 정렬 키 시험 |
| V4-1d `created_at.desc()`→`asc()` | 정렬 키 시험 |
| V4-2 `recent` 의 `user_id` 조건 삭제 | `test_other_accounts_history_is_never_mixed`(`7 == 6`)·`test_chat_saves_only_to_the_logged_in_account` |
| V4-2b `/chat` 응답 행을 고정 다른 계정으로 저장 | `test_chat_saves_only_…`(`1 == 2`) 외 FK 위반 30건 |
| V4-3 `append` 가 commit(롤백 밖 저장) | `/chat`·`/answers` 실패 시 기록 0 두 시험(`3 == 2`) |
| V4-4a 기본 51 / V4-4b 최대 201 / V4-4c 최대 199 / V4-4d `ge=0` | 상수 시험·`limit=201`·`limit=0` 422 시험 |
| V4-5a `/chat` 응답 행에 `question_id` 안 담음 / V4-5b `/answers` 사용자 행에 안 담음 / V4-5c `/answers` 응답 행에 새 질문 대신 옛 질문 id | 6행 순서 시험(+모양 시험·오류 삼킴 시험) |
| V4-6a·6b 루프 오류 삼킴 경로에서 응답 행 저장 안 함(`/chat`·`/answers` 각각) | 오류 삼킴 시험 각각 |
| V4-7a `/chat` 사용자 행 / V4-7b `/answers` 사용자 행 / V4-7c `/chat` 응답 행 저장 안 함 | 6행 순서·계정 격리·실패 롤백 시험 등 9·3·7건 |
| V4-8 `GET /chat/history` 의 `current_user` 제거 | `test_history_requires_login`(`200 == 401`) + U3b 열거 시험 2건이 새 라우트를 자동으로 잡음 |
| V4-9 `GET /chat/history` 가 읽다가 행을 씀 | 읽기 전용 시험(`12 == 6`) 외 9건 |
| V4-10 `GET /chat/history` 가 고정 다른 계정 기록을 읽음 | `test_other_accounts_history_is_never_mixed` |
| V4-11 응답 스키마에서 `question_id` 삭제 | 6행 순서·모양 시험 등 4건 |
| VR10 `_read_card` 가 소유자를 무시(R-10) | `test_resume_context_pointing_at_other_users_person_changes_nothing[identity_query]` |

변이 뒤 시험 DB 잔여: `chat_messages`·`users`·`persons` 등 전부 0행(`evidence/20261116-0044-u4-residue-after-mutations.txt`). `agent_traces` 234행은 모두 `concurrency-setup-*`·`answer-concurrency-tool-a`(기존 R-7 — 전체 pytest 가 `test_answer_concurrency` 를 돌릴 때마다 쌓이는 것, 변이 실행엔 그 시험이 없다).

## U5 — 스케줄러·푸시 사용자별, 고정 사용자 삭제, 결정 V (backend-agent, 2026-11-16)

전체 pytest **2515 passed**(2491 + 새 시험 26 − `tests/test_settings.py` 2) · 실패 0 · skip 0(`evidence/20261116-0101-u5-pytest-all.txt`).

### `tests/test_briefing_scheduler_users.py` (`dbtest`, 13건, 롤백 세션 + `session_scope` 를 같은 세션으로 바꾼 대역, 시계 `NOW` 주입 — 실제 커밋 0)

| 시험 | 단언(값) |
|---|---|
| `test_one_run_briefs_both_users_schedules` | A·B 창 안 일정 1건씩 → 한 번에 둘 다 `briefed_at == NOW` |
| `test_each_user_gets_own_ctx_and_exactly_one_call` | A 일정 2건·B 1건 → 호출 사용자 `[A, B]`(A 중복 없음), `trigger == "scheduler"` |
| `test_out_of_window_and_already_briefed_schedules_are_not_processed` | 창 밖(+30h)·지난 일정·이미 브리핑 → 호출 사용자 `[""]` 뿐 |
| `test_window_boundaries_…` | `NOW+24h` 포함·`NOW+24h+1분` 제외·`NOW` 정확히 포함 → `[A, C]` |
| `test_window_comes_from_settings_at_call_time_for_both_list_and_run` | `BRIEFING_LEAD_HOURS=2` 로 바꿔 실행 → `NOW+2h` 만 호출, `run_briefings` 의 `lead_hours == 2` |
| `test_default_window_is_24_hours_passed_to_run_briefings` | 기본 `lead_hours == 24` |
| `test_one_users_failure_…[python·db]` | A 에서 부분 쓰기 후 예외(파이썬 / `select 1/0` DB 오류) → 예외가 밖으로 안 나옴, B `briefed_at == NOW`, A `None`, A 의 부분 쓰기 행 0, 로그에 `A` 포함·일정 제목 없음 |
| `test_notifier_sends_only_to_each_users_own_subscriptions` | 일정 있는 A(2구독)·B(1구독)·일정 없는 C(1구독) → 발송 endpoint 정확히 `[a1, a2, b1]`, `push_send` trace 2행 |
| `test_other_users_subscription_is_not_used_for_a_users_schedule` | A 일정·B 구독만 → 발송 0, A `briefed_at == NOW` |
| `test_zero_targets_calls_run_briefings_once_with_empty_marker_user` | 대상 0명 → 호출 1회, `user_id == ""` |
| `test_zero_targets_leave_exactly_one_briefing_run_trace_in_old_format` | `briefing_run` 행 +1, `session_id` 가 `briefing:` 로 시작(`briefing-scheduler:` 아님), 키 집합 ⊇ 기존 형식, `selected == []`, `lead_hours == 24` |
| `test_one_or_more_targets_never_call_the_marker_ctx` | 대상 1명 → 호출 `[A]`, `""` 0 |

### `tests/test_push_endpoint_owner.py` (`dbtest`, 10건, 롤백 세션)

| 시험 | 단언 |
|---|---|
| `test_second_account_subscribing_same_endpoint_takes_it_over` | A 구독 뒤 B 가 같은 EP → `[(B, EP)]`, `created is True` |
| `test_takeover_leaves_other_endpoints_of_the_old_account` | A 의 EP·OTHER 중 B 가 EP 구독 → `[(A, OTHER), (B, EP)]` |
| `test_same_account_resubscribing_keeps_one_row_and_created_false` | 같은 계정 재구독 → 같은 id·`created is False`·1행 |
| `test_other_accounts_schedule_briefing_is_not_pushed_to_taken_over_endpoint` | (U3b R-6) A 일정 브리핑 → `push == "no_subscription"`·발송 0 |
| `test_manual_briefing_notifier_uses_logged_in_account_subscriptions_only` | (U3b R-2) B 로그인 `/briefings/run` → 발송 endpoint `[b-only]`, `push == "sent"` |
| `test_get_notifier_builds_notifier_for_the_given_logged_in_user` / `..._without_keys_is_null_notifier` | `WebPushNotifier.user_id == 로그인 사용자 id` / 키 없음 → `NullNotifier` |
| `test_logout_with_endpoint_deletes_that_users_row_and_keeps_other_endpoints` | 204, `[(A, OTHER)]` |
| `test_logout_does_not_delete_another_accounts_row_with_same_endpoint` | A 로그아웃이 B 의 같은 EP 행을 안 지움 |
| `test_logout_without_endpoint_or_body_keeps_subscriptions` | `{}`·본문 없음 → 구독 그대로 |

### 그 밖
- `tests/test_chat_history.py` +3건 — `test_second_answer_409_leaves_history_rows_unchanged`(U4 R-1: 409 `already_answered`, 기록 4행·내용 그대로) · `test_utterance_of_exactly_2000_chars_is_accepted_and_2001_is_rejected_with_no_side_effects`(결정 V: 2000자 200, 2001자 422 `loc == ["body","utterance"]`·`type == "string_too_long"`, 인식 단계 호출 수 그대로·`chat_messages`·`agent_traces` 행 수 그대로) · `test_existing_chat_validation_unchanged_empty_utterance_still_422`(`string_too_short`).
- 바꾼 기존 단언: ① `tests/test_push_wiring.py:344` `== "local"` → `== ""`(계획 지정) ② `tests/test_push_subscriptions.py` `test_list_subscriptions_same_endpoint_different_users_are_separate_rows` → `test_save_subscription_same_endpoint_different_user_takes_over_the_endpoint`(결정 P 가 대체한 옛 계약 — 계획 목록에 없던 것, 03-log 보고) · 주석 2곳(`test_push_subscriptions.py:90`·`test_api_read_briefings_e2e.py:185`).

### 변이 28종 — 저장소 밖 사본(`…/scratchpad/p9b-u5/copy`)에서 하나씩, 관련 8개 시험 파일(162건)만(`evidence/20261116-0103-u5-mutations.txt`; 실제 커밋형 시험 없음, 변이 28 전부 실패 ≥ 1 로 잡힘)

| 변이 | 잡는 시험 |
|---|---|
| V5-1 사용자 루프를 첫 사용자만 | 두 일정·호출당 1회·경계·실패 격리·발송 6건 |
| V5-2 예외 격리 제거 / V5-2b 세이브포인트 제거 | 실패 격리 `[python]`·`[db]` 2건 |
| V5-3a 다른 사용자 같은 endpoint 삭제 제거 | 인수·R-6·로그아웃 격리·`save_subscription` 인수 5건 |
| V5-3b 삭제가 자기 행도 지움 / V5-3c 다른 endpoint 도 지움 | 재구독 `created False`·`test_create_subscription_same_endpoint_updates_keys_without_new_row` / 인수 시 다른 endpoint 유지 |
| V5-4 로그아웃 endpoint 삭제 제거 | `test_logout_with_endpoint_deletes_that_users_row_…` |
| V5-4b 삭제에 `user_id` 조건 제거 / V5-4c `endpoint` 조건 제거 | 로그아웃이 B 행 안 지움 / 다른 endpoint 유지 |
| V5-4d NUL·서로게이트 방어 제거 | `test_auth_api.py` 로그아웃 이상 값 500 시험 2건 |
| V5-4e 로그아웃 endpoint 유무 조건 제거 | 본문 없음·`None` 등 6건 |
| V5-5 0명일 때 `run_briefings` 안 부름 | 새 0명 시험 3건 + **기존** `test_briefing_scheduler.py::test_manual_endpoint_and_scheduler_call_the_same_run_briefings_object`·`test_push_wiring.py` 스케줄러 2건 |
| V5-5b 0명 표식을 `"local"` | `test_push_wiring.py::test_scheduler_passes_web_push_notifier_…`(`== ""`)·새 표식 시험 2건 |
| V5-5c 표식 ctx 를 항상 호출 | 사용자 루프 시험 6건 |
| V5-6a 목록 창을 24 리터럴 / V5-6b `run_briefings` 의 `lead_hours` 24 리터럴 / V5-6c 상수를 import 시점에 읽음 | `test_window_comes_from_settings_at_call_time_…` |
| V5-7a `>=`→`>` / V5-7b `<=`→`<` | 창 경계 시험 |
| V5-8 `briefed_at IS NULL` 제거 / V5-9 `DISTINCT` 제거 | 창 밖·이미 브리핑 시험 / 호출당 1회 시험 |
| V5-10 알림기 사용자 고정 / V5-11 ctx 에 시계 안 넘김 | 사용자별 발송·기존 `test_push_wiring.py` 2건 / 시계 `NOW` 단언들 |
| V5-R2 `get_notifier` 가 `"local"` 고정(U3b R-2) | `test_push_endpoint_owner.py` 3건 |
| VV-1 상한 2001 / VV-2 1999 / VV-3 상한 제거 / VV-4 최소 길이 제거 | 2000·2001 경계 시험 / 빈 발화 422 시험 |

변이 뒤 시험 DB 잔여: 12개 테이블 모두 0행, `agent_traces` 261행은 전부 `concurrency-*`(`evidence/20261116-0123-u5-residue-after-mutations.txt`, 그 외 접두 0 확인).

## U7 — 배포 전 스모크 2종 (backend-agent, 2026-11-16, HEAD `4be331b`)

코드·테스트 변경 0. 스모크 1건 = 1줄. 증거 파일은 `evidence/20261116-013x-u7-*.txt`.

### ① Caddy 경유 Origin (운영 compose, 로컬 `https://localhost:8443`, `SITE_ADDRESS=localhost`, `-k`)

| 항목 | 기대 | 실제 | 증거 |
|---|---|---|---|
| 0003 적용 | 볼륨(0002)에서 0003 으로 | `Running upgrade 0002 -> 0003` 로그 줄 · Traceback 0 · `/api/health` `alembic_revision":"0003"` | `u7-caddy-origin-up` |
| (a) 같은 Origin 가입 | 201, 쿠키 속성 | 201 · `__Host-rel_session=***; HttpOnly; Max-Age=604800; Path=/; SameSite=lax; Secure` | `u7-caddy-origin-requests` |
| (b) 쿠키로 me·persons·chat/history | 200·`[]`·`[]` | 200 · 200 `[]` · 200 `[]` | 같음 |
| (c) 로그아웃 → 옛 쿠키 | 204 → 401 | 204 → 401 `unauthenticated` | 같음 |
| (d) 다른 Origin 가입·로그인 | 403 `bad_origin`, 행 불변 | 403·403 `bad_origin` · `users` 수 1 → 1 · 같은 아이디 정상 가입 201 → 2 | 같음 |
| (e1) XFH=evil + Origin=evil | 403 | 403 `bad_origin` | 같음 |
| (e2) XFH=evil + Origin=진짜 | 201(Caddy 가 덮어쓰면) | 201 — Caddy 가 클라이언트의 `X-Forwarded-Host` 를 자기 값으로 덮어씀 | 같음 |
| (f) Origin 없음 POST | 통과 | signup 201 · login 200 | 같음 |
| (f) 쿠키 없음 GET 3종·`/` | 401×3·200 | 401·401·401 · `/` 200 | 같음 |
| (g) HTTP 8088 → HTTPS | 308 | 308 `Location: https://localhost/…`(포트 8443 아님 — 로컬 매핑 때문에 따라가면 443) | `u7-caddy-origin-requests`·`g1-redirect` |
| (g) 포트 붙은 Origin(`https://localhost:8443`) | 201 | 201 | 같음 |
| (g) 포트 뺀 Origin(`https://localhost`) + Host `localhost:8443` | 403(로컬 포트 차이) | 403 `bad_origin` | 같음 |
| (g) 운영 모양(Host `localhost`, Origin `https://localhost` / `:443`) | 201 | 201 · 201 | 같음 |
| (g) 308 따라간 뒤 Origin `http://localhost:8088` 유지 | 403(출처 다름) | 403 · Origin `https://localhost` 로 바꾸면 201 | `g1-redirect` |
| 프론트 번들 | 로그인 관문 포함 | `assets/index-DNYl7nPx.js` 에 `/auth/me`·`/auth/signup`·`/chat/history` 각 1행 | `u7-caddy-origin-requests` |
| 로그·종료 | Traceback 0 · down(-v 없음) | backend Traceback 0 · 비밀번호·`rel_session` 문자열 0 · caddy error 0 · down 뒤 `relationship-prod_*` 볼륨 3개 남음 · 개발 컨테이너 불변 | `u7-caddy-origin-logs-down` |

### ② 로컬 통합 (개발 DB 5433, `AUTH_COOKIE_SECURE=0`, `http://localhost:8765`, 실 LLM 1턴)

| 항목 | 기대 | 실제 | 증거 |
|---|---|---|---|
| 가입 A·B | 201·201, 쿠키 `rel_session` | 201·201 · `rel_session=***; HttpOnly; Max-Age=604800; Path=/; SameSite=lax`(Secure 없음) | `u7-local-integration` |
| A `/chat` 1턴 | 200, `session_id == chat:<A id>` | 200(3.2초) · `chat:db5aec5e…` 일치 · `stop_reason=ask_user` · `kind=new_person` 질문 id 22 · `stored` 0·0·0 | 같음 |
| A 상태 | — | `/persons` `[]`(인물 미생성 — 승인 전) · `/questions/pending` 질문 22 1건 | 같음 |
| B 격리 | 인물 0, 질문 0 | `/persons` `[]` · `/questions/pending` `[]` · `/chat/history` `[]` | 같음 |
| B `POST /answers/22` | 404 | 404 `not_found` · A 의 질문은 그대로 | 같음 |
| B `GET /persons/{id}` | 404 | **미실행** — A 인물이 생기지 않았다(질문 단계에서 턴 종료). 단위 시험 `test_user_isolation.py` 가 맡음 | — |
| 다른 Origin 으로 A `/chat` | 403 | 403 `bad_origin` | 같음 |
| A 로그아웃 → 옛 쿠키 | 204 → 401 | 204 · `/auth/me` 401 · `/persons` 401 | 같음 |
| A 재로그인 `/chat/history` | 2행 user→assistant | 2행, `user`(id 1) → `assistant`(id 2, `question_id=22`) | 같음 |
| 2001자 | 422 | 422 `string_too_long` | 같음 |
| 서버 로그 | Traceback 0 · 비밀 0 | Traceback 0 · 비밀번호·`rel_session`·긴 토큰 문자열 0 · 프로세스 종료 확인 | `u7-local-serverlog` |

## U10 — 가입 닉네임 칸·중복 확인·사이드바 닉네임 (frontend-agent, 2026-11-16, CR-007)

실행: `npm --prefix web exec -- vitest run --root web` → 212 passed(기준선 191). 증거 `evidence/20261116-0712-u10-vitest.txt`, verifier 재실행 `evidence/20261116-0717-review-u10-vitest.txt`.

| 시험 (`web/src/__tests__/auth.test.tsx` 새 describe) | 단언 | 결과 |
|---|---|---|
| 가입 화면 칸·버튼·순서 | 닉네임 칸 `autocomplete=nickname`·`required`, "중복 확인" 버튼 2개, 칸 순서 username→nickname→password→password_confirm, `rules` 문구에 닉네임 규칙 | 통과 |
| 로그인 화면 0 | 닉네임 칸·두 버튼 없음 | 통과 |
| 아이디 중복 확인 — available | 요청 URL 정확히 `/api/auth/availability?username=minji_01`, `role=status` 안내, alert 없음 | 통과 |
| 아이디 중복 확인 — taken | 같은 URL, taken 안내 | 통과 |
| 아이디 중복 확인 — invalid | 같은 URL, invalid 안내 | 통과 |
| 닉네임 중복 확인 — available | 요청 URL `?nickname=%EB%AF%BC%EC%A7%80`, 안내 | 통과 |
| 닉네임 중복 확인 — taken | 같은 URL, taken 안내 | 통과 |
| 닉네임 중복 확인 — invalid | 같은 URL, invalid 안내 | 통과 |
| 값 변경 시 결과 사라짐 | 그 칸 결과만 사라지고 다른 칸은 남음 | 통과 |
| 늦은 응답 폐기 | 요청 때 값과 지금 값이 다르면 결과 없음, 버튼 다시 활성 | 통과 |
| 가입↔로그인 전환 시 초기화 | 닉네임 값·두 결과 지움 | 통과 |
| 빈/공백 비활성 | 버튼 `disabled`, 요청 0 | 통과 |
| 조회 실패 — 5xx | `checkFailed` 안내, 가입은 진행(요청 1회) | 통과 |
| 조회 실패 — 네트워크 | `checkFailed` 안내, 가입은 진행 | 통과 |
| 확인 없이 제출 | 가입 요청 1회, 조회 요청 0회(결정 AA) | 통과 |
| 가입 409 `nickname_taken` | 안내 `alert` 한 줄, 가입 화면 유지 | 통과 |
| 가입 422 `invalid_nickname` | 안내 `alert` 한 줄, 가입 화면 유지 | 통과 |
| me 200 사이드바 | `sidebar-nickname` '민지', `sidebar-username` 'minji_01', 민지 · minji_01 · 로그아웃 순서 | 통과 |
| 가입 직후 사이드바 | 201 응답 닉네임 '심사위원' 표시 | 통과 |
| `api.test.ts` checkAvailability URL | 준 키만, 한글·공백 인코딩, `GET`·`same-origin` | 통과 |
| `api.test.ts` checkAvailability 401 | 전역 로그아웃 신호 없음 | 통과 |

기존 시험 갱신(닫힌 목록 F1~F4): 가입 본문 단언 `{username, nickname, password}`, `ME.nickname='민지'`. E2E 5 passed(목 데이터만 갱신, 가입 화면 새 E2E 는 없음).
