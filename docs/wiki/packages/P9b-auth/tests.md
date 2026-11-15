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
