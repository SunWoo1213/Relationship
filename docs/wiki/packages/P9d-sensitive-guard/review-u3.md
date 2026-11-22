# P9d-sensitive-guard · U3 커밋 전 코드 리뷰 (review-u3)

검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트
대상: dev2 작업 트리의 U3 미커밋 변경(기준 커밋 `947c12c`) — 새 파일 `alembic/versions/0006_sensitive_guard.py` · `tests/test_migration_0006.py`, 고친 파일 `app/db/models.py` · `tests/test_schema_models.py` · `tests/test_schema_check.py` · `tests/test_migration_0003.py` · `tests/test_migration_0004.py` · `tests/test_migration_0005.py` · `tests/test_api.py`
작성: 2026-11-22 17:52

결과: 통과

열린 [필수] 0 · [권고] 4(R-1~R-4) · [참고] 5. 통과 판정은 코드·시험에 대한 것이다. 커밋에 같이 들어가야 하는 문서(R-1)는 아래에 따로 적었다.

## 1. 본 것

- 계획: `01-plan.md` U3 항목(157~169행) · 산출물 U3 닫힌 목록(39행) · "고정 단언 전수 확인" 표(96~124행) · 범위의 "하지 않는 것"(31행 — 기존 데이터 소급 없음).
- 카드: `specs/S3.1-schema-v2.md` 51~62행(0006 보충) · `decisions/D20-sensitive-guard.md` ① 표 #14(77행)·R-5(87행)·95행(downgrade 규칙) · `security.md` §4 · `verification.md` "변이 시험 방법" · CLAUDE.md 데이터 모델·원칙 8.
- 코드: `git diff 947c12c -- app tests scripts alembic` 전부, 새 파일 2개 전부, `tests/test_migration_0003.py` 도우미(`_mig_env`·`_constraint_violated`), `alembic/env.py`(트랜잭션 — `context.begin_transaction()` 하나), `app/db/base.py` 명명 규약.
- 구현자 증거: `evidence/20261122-17{37,40,43,44}-u3-*.txt` 12개(참고만 하고 핵심은 §2 에서 다시 실행).

## 2. 직접 실행한 명령과 결과

증거는 전부 `docs/wiki/packages/P9d-sensitive-guard/evidence/`. 저장소 파일은 고치지 않았다(변이는 스크래치패드 pytest 플러그인으로 런타임 치환). 로컬 DB 는 `capstone2-postgres-1`(5433, healthy) — `docker compose ps` 는 이 셸에서 빈 목록이라 `docker ps` 와 포트 열림으로 확인했다.

| 무엇 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 마이그레이션 시험 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_migration_0006.py …0005.py …0004.py …0003.py -q -rs` | **46 passed**, skip 0 | `20261122-1747-verifier-u3-migration.txt` |
| 스키마 + API 시험 | `… pytest tests/test_schema_models.py tests/test_schema_check.py tests/test_api.py -q -rs` | **39 passed** | `…-1747-verifier-u3-schema-tests.txt` |
| alembic check | `… -m alembic check` | `No new upgrade operations detected.` | `…-1747-verifier-u3-alembic-check.txt` |
| schema_check | `… scripts/schema_check.py` | 전부 `[PASS]`, `alembic_version -> 0006`, exit 0 | `…-1747-verifier-u3-schema-check.txt` |
| tools_check | `… scripts/tools_check.py` | `RESULT: 7/7 ok` | `…-1747-verifier-u3-tools-check.txt` |
| 범위 | `git diff --stat 947c12c -- tests scripts app alembic evaluation web` | 추적 파일 7개(`app/db/models.py` + 닫힌 목록 6개) — 목록 밖 0 | `…-1747-verifier-u3-test-diff.txt` |
| ruff | `… -m ruff check app tests scripts alembic` | All checks passed | `…-1747-verifier-u3-ruff.txt` |
| **전체 pytest** | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2778 passed · 실패 0 · skip 0**(기준선 2759 + 새 시험 19) | `…-1747-verifier-u3-full-pytest.txt` |
| 변이 대조군 + 12종 | `VU3_MUT=<이름> PYTHONPATH=<스크래치패드>/vu3 … pytest -p vu3_mut tests/test_migration_0006.py -q -rfEs` | §3 | `…-1749-verifier-u3-mutations-names.txt`(실패 시험 이름 포함). `…-1749-verifier-u3-mutations.txt` 는 `-rs` 로 돌려 이름이 빠진 첫 실행 — 개수는 같다 |
| 시험 전용 DB 복구 확인 | 0003~0006 시험 재실행 + 상태 조회 + 개발 DB 행 수 + `git status --short` | 46 passed · `relationship_test_mig` version 0006·민감 행 0·CHECK 4개 원문 그대로 · 개발 DB 행 수 불변 | `…-1750-verifier-u3-restore.txt`(변이 전 상태는 `…-1749-verifier-u3-mig-state-before.txt`) |
| 개발 DB 전후 | 구현자 `…-1737-u3-dev-before-counts.txt` ↔ `…-1740-u3-dev-after-counts.txt` 대조 + 내가 다시 센 값 | 13개 테이블 행 수 전부 같음(persons 4 · person_aliases 5 · person_facts 2 · fact_sources 1 · events 10 · schedules 1 · pending_questions 638 · agent_traces 6903 · users 12 · auth_sessions 17 · chat_messages 1864 · 나머지 0), 버전만 0005 → 0006 | `…-1749-verifier-u3-dev-counts-pre.txt`(`…-dev-counts-before.txt` 는 `PYTHONPATH` 를 빠뜨려 `ModuleNotFoundError` 로 끝난 첫 실행 — 대체됨) |
| 개발 DB 소급 없음 | 새 컬럼 6개의 `IS NOT NULL` 행 수, `kind='sensitive'` 행 수(읽기 전용) | **전부 0**, 타입·nullable 은 S3.1 과 같음 | `…-1751-verifier-u3-dev-nulls.txt` |

개발 DB 는 읽기만 했다. 변이가 건드린 것은 `relationship_test_mig` 하나다.

## 3. 변이 시험 (저장소 무수정 — 런타임 치환)

방법: 스크래치패드 플러그인이 `alembic.script.base.Script._from_path` 를 감싸 리비전 0006 모듈이 로딩될 때 `_count`·`_CATEGORIES_SQL`·`upgrade`·`downgrade` 를 치환한다. 대조군(`control`) 19 passed.

| 변이 | 기대 | 결과 |
|---|---|---|
| `skip_fact` — downgrade 가드가 `person_facts` 표시 행을 0 으로 셈 | `fact_marked` 가 의도한 단언으로 실패 | **잡힘** — `[fact_marked] Failed: DID NOT RAISE RuntimeError`(구현자 M3 의 `KeyError` 가 아니라 가드 단언). 뒤따르는 3건은 DB 가 0005 로 내려가 생긴 연쇄 |
| `skip_event` — `events.sensitive_category` 를 세지 않음 | `event_marked` 실패 | **잡힘** — `[event_marked] DID NOT RAISE` |
| `skip_schedule` | `schedule_marked` 실패 | **잡힘** — `[schedule_marked] DID NOT RAISE` |
| `skip_consent` — `consent_question_id` 를 세지 않음 | `consent_ref_only` 실패 | **잡힘** — `[consent_ref_only] DID NOT RAISE` |
| `skip_kind` — `kind='sensitive'` 질문을 세지 않음 | `kind_sensitive_question` 실패 | **잡힘** — 다만 `RuntimeError` 가 아니라 PostgreSQL 의 CHECK 재생성 실패(`IntegrityError`)로. 가드가 없어도 DB 가 막고 버전은 0006 그대로다(§5 [참고] N-2) |
| `category_value` — 마이그레이션의 `finance` → `financial` | CHECK 문장·수용 시험 실패 | **잡힘** — `test_check_sentences_are_the_contract_values` + `accepts_five_categories…[3표]` |
| `category_extra` — 범주 6번째 값 추가 | CHECK 문장 실패 | **잡힘** — `test_check_sentences_are_the_contract_values` |
| `upgrade_touch_briefed` — upgrade 뒤 `UPDATE schedules SET briefed_at = now()` | 기존 행 불변 실패 | **잡힘** — `test_upgrade_changes_no_existing_data` |
| `upgrade_touch_updated_at` — upgrade 뒤 `UPDATE person_facts SET updated_at = …` | 기존 행 불변 실패 | **통과(시험 공백)** — 19 passed → R-2 |
| `upgrade_touch_created_at` — upgrade 뒤 `UPDATE events SET created_at = …` | 같음 | **통과(시험 공백)** — 19 passed → R-2 |
| `message_leaks_raw` — 거부 메시지에 질문·내용·값·제목 원문을 덧붙임 | 다섯 경우 전부 실패 | **잡힘** — 5건 모두 `assert '<원문>' not in message` |
| `guard_deletes_then_raises` — 가드 앞에서 별도 연결로 표시 행을 지움 | 행 불변 실패 | **잡힘**(`fact_marked`) — 다만 지운 탓에 가드가 통과해 `DID NOT RAISE` 로 잡혔다. "지운 뒤 실패" 를 따로 떼어 본 변이는 아니다 |

요청받은 확인: **`fact_marked` 는 `person_facts` 개수 검사를 독립적으로 막는다.** 구현자 기록의 `KeyError` 는 변이를 "사전에서 키를 빼는" 식으로 만들어서 생긴 것이고, 개수만 0 으로 만들면 그 경우 하나가 가드 단언으로 실패한다. 다섯 판정 조건 각각에 그 조건만 켜진 경우가 하나씩 있다.

## 4. 판정 근거 — 줄 단위

**리비전 `0006_sensitive_guard.py`**
- upgrade 는 `op.add_column` 6번 · `op.create_check_constraint` 4번 · `op.drop_constraint` 1번뿐이다(45~64행). `UPDATE`·`DELETE`·`TRUNCATE`·`DROP TABLE` 0 — S3.1 60행 "0006 upgrade 는 컬럼 추가·CHECK 교체뿐 — **기존 데이터 변경 0**" 과 `security.md` §4("셸에서 `DROP`/`TRUNCATE` 금지 → Alembic 마이그레이션 파일로 작성해 검토")에 맞다. downgrade 의 `drop_column`·`drop_constraint` 는 마이그레이션 파일 안이고 테이블을 지우지 않는다.
- 컬럼 타입·nullable: `sa.String()`(길이 없음 → `character varying`)·`BigInteger`·`Integer`·`DateTime(timezone=True)`, 전부 `nullable=True`·기본값 없음·FK 없음 — S3.1 53~56행("VARCHAR NULL … BIGINT NULL(FK 없음)", "INTEGER NULL · TIMESTAMPTZ NULL")과 글자가 같다. 실물은 `…-1751-verifier-u3-dev-nulls.txt`.
- downgrade 가드(73~88행): 다섯 개수를 센 뒤 하나라도 0 이 아니면 DDL 전에 `RuntimeError`. D20 95행 "`kind='sensitive'` 행·민감 표시 행·`consent_question_id` 가 하나라도 있으면 아무것도 지우지 않고 실패" 의 세 조건(표시 행은 세 표)을 모두 센다. 메시지는 f-string 에 정수 다섯 개만 넣는다 — 원문·값·id 0(S3.1 61행 "개수만 담은 메시지, 원문 0"). `message_leaks_raw` 변이가 5건 모두 잡힌다.
- 실패 시 불변: 가드가 DDL 보다 앞이고, `alembic/env.py` 가 리비전을 한 트랜잭션(`context.begin_transaction()`)으로 돌려 예외면 통째로 롤백된다. 시험이 실패 뒤 `alembic_version == "0006"` · 새 컬럼 6개 · 행 수 · 행 값 · CHECK 4개 문장을 각각 단언한다(476~480행).
- 범주 순서·값: `_CATEGORIES_SQL` 이 `crime`·`health`·`sex`·`politics_religion`·`finance` 순서로 글자 그대로. 모델 상수를 import 하지 않은 것은 옳다(리비전은 시점 고정).
- downgrade 순서: `kind` CHECK 를 3종으로 되돌리는 것이 컬럼 삭제보다 앞이지만 같은 트랜잭션이라 순서는 결과에 영향이 없다.

**모델 `app/db/models.py`**
- CHECK 이름 `name="sensitive_category_valid"` → 명명 규약으로 `ck_<표>_sensitive_category_valid`. 기존 `kind_valid`·`type_valid` 와 같은 모양이고 리비전의 `op.f(...)` 이름과 일치한다.
- `alembic check` 는 CHECK 제약을 비교하지 않는다. 그래서 모델 ↔ DB 의 CHECK 일치는 `alembic check` 가 아니라 `test_migration_0006.py` ③(DB 문장 리터럴)·⑥-b(모델 문장 리터럴)가 고정한다 — 구현자 M5·M10·M13·M14 와 내 `category_value`·`category_extra` 가 잡힌다.
- `QUESTION_KINDS` 4종 · `kind_valid` 문장 4종 — S3.1 57~58행.

**고친 기존 단언이 계약을 느슨하게 만들었는가**
- `tests/test_migration_0005.py` ①·196행: `head == "0005"` 리터럴 → `"0005" in history` + `DB 버전 == head`. head 리터럴 `"0006"` 과 `down_revision == "0005"` 는 새 `test_migration_0006.py` ①이 값으로 단언하므로 사슬 전체로는 약해지지 않았다. 계획 166행이 지정한 모양 그대로다.
- `tests/test_schema_models.py` events CHECK 시험의 필터 `"type" in str(c.sqltext)`: `sensitive_category IN (…)` 문장에 `type` 이 없어 1개만 남는다. "events 에 CHECK 가 하나뿐" 이라는 옛 단언은 사라졌지만, CHECK 총수 8(`test_exactly_eight…`)과 0006 시험 ⑥-b("표마다 `sensitive_category` CHECK 정확히 1개, 문장 일치")가 대신 고정한다. 계획 161행 지시와 같다.
- `USERS_COLUMNS_AT_0003` 뺄셈 · `NULLABLE_COLUMNS` 11 · 컬럼 85 · CHECK 8 · `TIMESTAMP_COLUMNS` 추가 · `test_api.py` `"0006"` · `test_schema_check.py` 4 — 계획 161~165행과 값이 같다. 테이블 13·FK 9·JSONB 5·인덱스 13·UNIQUE 8 단언은 건드리지 않았다(diff 에 없음).
- `NULLABLE_COLUMNS` 는 이름 집합이라 "세 표 중 하나만 NOT NULL" 을 못 잡지만 0006 시험 ②(DB `is_nullable == "YES"` 6개)·⑥-b(모델 `nullable is True` 6개)가 컬럼 단위로 잡는다.

**구현자가 계획에 없이 정한 것**
- `sa.String()`: S3.1 문언 "VARCHAR" 를 글자 그대로 옮긴 것이라 타당하다. 기존 문자열 컬럼은 `Text` 라 CHECK 정의에 `::character varying` 캐스트가 붙는 차이만 있다.
- CHECK 이름·문장 형태(`IN (…)`, NULL 은 CHECK 의 3값 논리로 통과): 기존 `kind_valid` 와 같은 형태. NULL 통과는 시험 ⑤가 표마다 확인한다.
- `SENSITIVE_CATEGORIES` 를 `app/db/models.py` 에 둔 것: 계획 151행은 같은 이름의 상수를 U2 `app/guard/rules.py` 에 둔다고 적었다. U3 자체는 계획 위반이 아니지만 U2 가 그대로 따로 정의하면 출처가 둘이 된다 → R-3.

## 5. 소견

### [필수]
없음.

### [권고]

- **R-1 `tests.md` · `03-log.md` 에 U3 기록이 없다(커밋에 같이).** `docs/wiki/packages/P9d-sensitive-guard/` 에 `tests.md` 가 아직 없다(`ls` — `01-plan.md`·`02-plan-verify.md`·`03-log.md`·`evidence` 뿐). 계획 47행 산출물에 `tests.md` 가 있고 "테스트 1건 = 표 1줄" 은 사용자 규칙이다. 새 시험 19건(`tests/test_migration_0006.py` — 매개변수 포함)과 고친 단언 6파일을 U3 절로 적고, `03-log.md` U3 항목에 "계획에 없이 정한 것 3가지(String · CHECK 이름 · 상수 위치)" 를 남긴다. 코드 판정과 무관해 [필수] 로 올리지 않았지만 U3 커밋에 함께 들어가야 한다.
- **R-2 "기존 행 변경 0" 스냅샷에 시각 컬럼이 없다(시험 공백, 변이 2종 통과).** `tests/test_migration_0006.py:70~80` `_SNAPSHOT_SQL` 이 `events.created_at` · `person_facts.updated_at` · `persons.created_at`/`updated_at` · `pending_questions.created_at`/`answered_at` · `users.created_at` 를 뽑지 않는다. upgrade 가 이 컬럼을 바꿔도 19 passed(`upgrade_touch_updated_at`·`upgrade_touch_created_at`). 지금 리비전에는 `UPDATE` 가 없어 결함은 아니다. 고칠 자리: `_SNAPSHOT_SQL` 여섯 문장을 `SELECT *` 대신 0005 시점 컬럼 전부(시각 포함)로 넓힌다 — 값이 DB 에 고정돼 있어 흔들리지 않는다.
- **R-3 범주 상수의 출처를 U2 에서 하나로 묶는다.** `app/db/models.py:85~87` 주석은 "가드 모듈(U2)도 이 값을 그대로 따른다" 인데 계획 151행은 `rules.py` 에 `SENSITIVE_CATEGORIES` 를 둔다. U2 위임 때 둘 중 하나를 정한다: `rules.py` 가 `app.db.models.SENSITIVE_CATEGORIES` 를 다시 내보내거나(같은 객체), 따로 정의하되 `tests/test_guard_rules.py` 가 `rules.SENSITIVE_CATEGORIES == models.SENSITIVE_CATEGORIES` 를 단언한다. 어긋나면 가드가 낸 범주가 DB CHECK 에서 500 으로 터진다. U3 에서 고칠 것은 없다.
- **R-4 downgrade 가드의 "세고 나서 지우기" 사이 틈.** 73~79행의 개수 조회와 90행 이후 DDL 사이에 다른 연결이 표시 행을 커밋하면(백엔드가 떠 있는 채 되돌릴 때) `sensitive_category` 컬럼이 값과 함께 사라져 민감 행이 일반 행으로 보이게 된다(`kind='sensitive'` 쪽은 CHECK 재생성이 막는다 — `skip_kind`). 고칠 자리는 둘 중 하나: 가드 앞에 `LOCK TABLE events, person_facts, schedules, pending_questions IN SHARE ROW EXCLUSIVE MODE` 한 줄, 또는 코드는 두고 U12 문서(`docs/user-setup/13-user-todo-deploy.md` J 절 "되돌리기")에 "백엔드를 내린 뒤 downgrade" 를 적는다. 운영 되돌리기는 백업 뒤 수동 절차라 [권고] 로 둔다.

### [참고]

- N-1 작업 트리에 U1(eval-agent) 산출물이 미추적으로 같이 있다 — `evaluation/sensitive_guard/`(`dev.jsonl`), 리뷰 도중 `scripts/validate_sensitive_set.py` 가 새로 생겼다. U3 것이 아니다. U3 커밋은 대상 9개 경로만 `git add` 한다(`git diff --stat` 는 미추적 파일을 보여 주지 않으므로 `u3-test-diff` 로는 드러나지 않는다).
- N-2 `kind='sensitive'` 개수 검사는 안전망이 둘이다(가드 + PostgreSQL CHECK 재생성). 가드를 빼도 데이터는 지워지지 않고 메시지만 `IntegrityError` 로 바뀐다. 시험은 `RuntimeError` 를 요구해 가드 쪽을 고정한다.
- N-3 downgrade 시험이 중간에 실패하면 DB 가 0005 에 남아 같은 실행의 뒤 시험이 연쇄 실패한다(변이 실행에서 1건 원인에 3~5건 실패). 다음 실행의 fixture 가 `downgrade base` 부터 다시 만들어 스스로 회복한다(`…-1750-verifier-u3-restore.txt` 로 확인) — 실패 원인을 읽을 때 첫 `DID NOT RAISE` 줄을 본다.
- N-4 `tests/test_migration_0004.py:122` 주석 "users 컬럼 집합 = S3.1 0004 보충(5)" 는 이제 head 기준 7이다. 단언은 맞고 주석만 옛 숫자다.
- N-5 구현자 변이 증거(`…-1743-u3-mutations.txt`)의 M1~M3 는 모두 `consent_ref_only` 한 경우에서만 실패가 보고됐다(첫 실패에서 멈춘 실행으로 보인다). 조건별 독립성은 그 증거가 아니라 §3 의 `skip_*` 다섯 줄이 근거다.

## 6. 결론

결과: 통과

- 수용 기준(계획 168행) 일곱 항목 — 빈 상태 왕복 · `kind='sensitive'` 가 있을 때 실패·불변 · 표시 행만 있을 때도 같음 · 0005 에서 CHECK 위반/0006 뒤 성공 · 기존 행 변경 0 · `alembic check` 무변경 · 목록 밖 시험 diff 0 — 을 §2 의 직접 실행으로 확인했다.
- D20 #14 판정 명령 `pytest tests/test_migration_0006.py -q` 19 passed, 전체 2778 passed · skip 0.
- 개발 DB 는 행 수 불변·새 컬럼 전부 NULL(소급 없음, 사용자 결정 9).
- 커밋 전: R-1(문서)을 같이 넣고, `git add` 는 U3 경로만(N-1). R-2 는 이 커밋이나 다음 단위에서, R-3 은 U2 위임 프롬프트에, R-4 는 U12 문서 또는 한 줄 잠금으로.
