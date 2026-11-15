# P9b-auth · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-11-15 21:10 · docs(P9b-auth): 로그인·계정별 격리 계획을 검증까지 마치고 활성화한다 · d9c5a5f
- 변경: `01-plan.md`(architect 초안 → 개정 1 → 개정 2 + 메인 반영: 기준 해시 `08c1b49`, 기준선 2261 passed, U7 Caddy 경유 Origin 스모크, 3차 권고 R3-1~R3-4), `02-plan-verify.md`(verifier 1차 보류 F-1~F-7 → 2차 보류 N-1~N-4 → 3차 **통과**, 점검표 8/8, [필수] 0), verify-plan 증거(마지막 `evidence/20261115-2052-verify-plan.txt` FAIL 0/WARN 0), 기준선 pytest 증거, `P9c-briefing-calendar/01-plan.md` 초안(달력, P9b 완료 뒤), backlog 100행 세분화 표기, `CURRENT active: P9b-auth`.
- 이유(기획서·카드 연결): CR-006 · D18 — 졸업평가(11-18) 시연에서 새 계정 가입(빈 상태)과 데이터가 쌓인 계정 로그인 두 갈래를 보이기 위해 아이디·비밀번호 로그인과 계정별 격리를 넣는다. 결정 A~U 는 사용자 지시("계획·실행·독립 검토까지 진행")에 따라 권장안 채택.
- 정합성 확인: 원칙 1~4·8·9 무변경, 원칙5·7 은 CR-006 개정 문장 / D18 지킬 것 1~9 · D17 결정 6 / S3.1·S3.4·S3.6 보충 / security §1·§4·§5 — 위반 없음(verifier 3차 점검표 8행 통과).
- 남은 것 · 다음 단위: U1(backend-agent — 스키마·리비전 0003, 개발 DB 인물 12명 삭제됨) → U2 → U3a → U3b → (U4 ∥ U5), U6 은 U2 커밋 뒤 동시, U7 배포 반영(사용자 SSH — 0003 적용 뒤에는 옛 해시로 되돌릴 수 없음), U8 시연 계정. 축소 판단 시점: 11-16 밤까지 U3b 미커밋이면 축소 1·4. 열린 [권고]: R-12(verify-plan.sh 가 `P5b-`·`P9b-` id 를 못 읽음, 하네스 FIX 후보).
- Refs: P9b-auth CR-006 D18 D17 S3.1 S3.4 S3.6 F-fbaaae R-U10D-3 R12 R14 security

## 2026-11-15 21:50 · feat(P9b-auth): 계정·로그인 세션·대화 기록 테이블을 더하고 기존 데이터를 비우는 리비전 0003 을 넣는다 · pending
- 변경: `alembic/versions/0003_auth_users.py`(새 테이블 3 + `pending_questions.user_id` + 기존 사용자 데이터 `DELETE`), `app/db/models.py`(모델 3·컬럼 1·인덱스 3), `app/tools/questions.py`(`ask_user` 가 `user_id` 를 넣는 한 줄), `scripts/schema_check.py`(FK 6→8, 라벨 동적화), 새 `tests/test_migration_0003.py` 11건, 닫힌 목록의 기존 테스트 9파일(스키마 수치·`PendingQuestion(` 인자·리비전 문자열), `tests.md`, registry 행 3개, `review-u1.md`.
- 이유(기획서·카드 연결): CR-006 · D18 결정 1·4·5·8 · S3.1 보충 — 계정별 격리의 바탕 스키마. 기존 데이터는 사용자 결정대로 비운다(개발 DB 인물 12명 삭제됨, 행 수 증거 `u1-dev-before/after-counts`).
- 정합성 확인: 원칙1~4·9 무관(ER·툴 시그니처 불변, `tools_check` 7/7) / D18 지킬 것 9 / S3.1 보충과 컬럼·제약 일치(`alembic check` 무변경) / security §4(비우기는 리비전 파일의 DELETE 로만, TRUNCATE·DROP DATABASE 없음) — 위반 없음. 변이 시험 중 전용 시험 DB 의 찌꺼기 테이블을 임시 `drop_table` 로 치운 일은 verifier 가 "커밋을 막는 위반 아님, 선례 아님"(R-3)으로 판정.
- 남은 것 · 다음 단위: U2(인증 코어) — 시작 때 R-8·R-9(`tests/test_migration_0003.py`) 함께. R-6 CI dbtest 결과 확인. 서버에 시험 DB `relationship_test_mig`·`relationship_test_mig_v15`(빈 상태) 남음 — 삭제는 사용자 몫.
- Refs: P9b-auth D18 S3.1 CR-006 F-fbaaae security 원칙8

## U1 구현 메모 (backend-agent, 2026-11-15 — /commit 전 초안, 커밋 항목이 아니다)
- **개발 DB 인물 12명 삭제됨**(사용자 결정 4 "모두 비운다"). 실행 전 행 수 `evidence/20261115-2056-u1-dev-before-counts.txt`: persons 12 · person_aliases 15 · person_facts 24 · events 33 · fact_sources 36 · schedules 6 · pending_questions 21 · push_subscriptions 2 · agent_traces 605. `alembic upgrade head`(0002→0003) 뒤 `…-2057-u1-dev-after-counts.txt` 전부 0, `alembic_version` 0003. 비우기는 리비전 파일의 `DELETE`(security §4) 로만 했다.
- 판단(계획이 맡긴 것): ① `pending_questions` 인덱스 — **단순 `(user_id, answered_at)`**(`ix_pending_questions_user_id_answered_at`). 부분 인덱스(`answered_at IS NULL`)는 답이 끝난 질문을 user_id 로 조회하는 U3b 의 소유 검사에 안 맞고, 기존 `session_id` 부분 인덱스와 중복이라 단순형을 골랐다. ② 인덱스 이름은 모델·리비전 모두 `ix_auth_sessions_user_id`·`ix_chat_messages_user_id_created_at`. 제약 이름은 naming_convention 그대로(`uq_users_username`·`uq_auth_sessions_token_hash`·`ck_chat_messages_role_valid`·`fk_*_user_id_users`). ③ `users.id` 는 Text PK 이고 모델에 기본값을 두지 않았다 — 값(uuid4 hex)은 U2 가 정한다.
- **전용 시험 DB `relationship_test_mig`**: `tests/db_bootstrap.ensure_test_database_ready` 가 `relationship_test` 를 만드는 방식 그대로(없으면 `CREATE DATABASE`·`vector` 확장·`upgrade head`, 있으면 재사용) — 훅에 막히지 않았고 `DROP DATABASE` 는 쓰지 않았다. 환경은 `apply_test_database_env` 에 `TEST_POSTGRES_DB=relationship_test_mig` 를 준 복사본을 `patch.dict(os.environ)` 로 모듈 안에서만 쓴다. alembic 은 `Config()`(ini 없이)로 불러 env.py 의 `fileConfig` 가 다른 테스트 로거를 끄지 못하게 했다.
- 변이 시험 부작용: V1-5(downgrade 가 `users` 를 남김)를 처음 공유 전용 DB 에서 돌리자 `users` 가 남아 이후 변이가 `DuplicateTable` 로 오염됐다. 전용 DB 의 변이 찌꺼기 `users` 한 테이블을 Alembic `Operations.drop_table` 로 치워(스크래치 스크립트, 대상은 내가 만든 `relationship_test_mig` 뿐 — 개발·공유 테스트 DB 아님) 복구했고, 변이 전체를 `u1-mutations-v2` 로 다시 돌렸다(V1-5 는 별도 DB `relationship_test_mig_v15` — 서버에 시험 DB 가 하나 더 남았다). 첫 증거 `u1-mutations` 의 V1-5·V1-6·V1-8 구간은 그 오염으로 신뢰할 수 없다(superseded).
- **닫힌 목록 추가(메인 승인 2026-11-15)**: `tests/test_schema_check.py::test_model_unique_constraint_expectations…` 기대 집합에 새 UNIQUE 2개(`uq_users_username`·`uq_auth_sessions_token_hash`)를 더하고 이름을 `…three_plus_0003_two` 로(S3.1 보충 반영, 단언 의미 변경 아님). `scripts/schema_check.py` 라벨 "9 tables …" 두 곳은 `len(EXPECTED_TABLES)` 로 동적화.
- 변이 사고 경위: V1-5 가 전용 시험 DB `relationship_test_mig` 에 `users` 를 남겨 오염 → Alembic `Operations.drop_table("users")`(스크래치 스크립트, 그 DB 한정)로 치움. 이후 V1-5 는 별도 DB `relationship_test_mig_v15` 를 써서 그 DB 가 서버에 남았다(추가 변이는 이 DB 재사용, 더 만들지 않음).
- **리뷰 반영(review-u1)**: F-1 `mig` 픽스처가 `dict(os.environ)` 전체를 내주던 것을 `os.environ` 과 달라진 키만 담은 `_EnvOverrides`(repr 은 키 이름만)로 바꿨다. 일부러 실패시킨 출력에 환경변수 값 없음(`u1-fix-forced-failure`, DB `relationship_test_mig_v15`). R-2 **V1-5 는 ⑦ 단언이 아니라 픽스처 setup 의 `DuplicateTable` 로 걸린다**(downgrade 가 남긴 객체가 다음 upgrade 를 막으므로). R-4 시험 docstring 을 "직접 부르는 alembic 명령은 ini 를 읽지 않는다(fixture 의 `ensure_test_database_ready` 는 읽는다)" 로 좁혔다.
- (U1 리뷰 뒤, 메인 기록): verifier `review-u1.md` 1차 보류(F-1 시험 픽스처가 환경변수 전체를 인자로 내줌) → `_EnvOverrides` 로 수정 → 재검토 **통과**. 열린 권고 R-8(`mig` 픽스처 지역변수 `env` 가 여전히 전체 환경 사본 — `-l` 에서만 찍힘)·R-9(`_EnvOverrides` 비교 단언 경고 docstring)는 U2 에서 함께 고친다. R-6(CI dbtest 결과)은 푸시 뒤 여기에 적는다.
- (이전 보고 시점의 멈춘 곳, 위 승인으로 해소): 전체 pytest 에서 닫힌 목록 밖 `tests/test_schema_check.py::test_model_unique_constraint_expectations_returns_fix_020_three` 가 실패(새 UNIQUE 2개 `uq_users_username`·`uq_auth_sessions_token_hash` 가 모델 메타데이터에서 나와 기대 집합 3 → 5). 고치지 않고 보고한다.
