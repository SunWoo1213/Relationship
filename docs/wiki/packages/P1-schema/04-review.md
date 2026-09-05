# P1-schema · 완료 검토 (04-review)

날짜: 2026-09-05 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·컨텍스트(L-002)

대상 커밋: 9397066(착수) → d7113e9(U1) → 4dfaf33(U2) → 09c2bd1(U3) → 03e3ce3(U4) → ec2fe8c(U5). 로컬 컨테이너 `capstone2-postgres-1`(호스트 5433, PostgreSQL 16.15, vector 0.8.6), DB 상태 `0001 (head)`. 검토 중 DB 스키마를 바꾸지 않았다(downgrade 미실행). 읽은 카드: INDEX 태그 어휘·패키지 표 P1-schema 행, S3.1 전문, S3.2 표, D4·D5·D8·D9 전문, review-index R8·R9 행(16·17행), security.md §1·§4·§5, 원칙7·8·9(CLAUDE.md).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh P1-schema > docs/wiki/packages/P1-schema/evidence/20260905-1439-verify-impl-final.txt 2>&1` (이 문서를 쓴 뒤 실행한 최종본. 사전 실행: `evidence/20260905-1431-verify-impl.txt` FAIL 0 / WARN 1 — 유일한 WARN 은 이 문서의 부재 F-14f3ef)
```
== verify-impl P1-schema  (20260905-1439) ==
.................................................                        [100%]
49 passed in 0.82s
PASS  pytest 통과 → evidence/20260905-1439-pytest.txt
PASS  compileall 통과 → evidence/20260905-1439-lint.txt
PASS  태그 P1-schema 커밋 10 건 → evidence/20260905-1439-commits.txt
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: R9
PASS  커밋에 태그 존재: S3.1
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  9개 테이블 생성  ← evidence/20260905-1433-verifier-independ
PASS  증거 확인:  `events.type` 제약 존재  ← evidence/20260905-1433-verifier-independ
PASS  registry 에 P1-schema 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260905-1439-summary.txt ==
```
FAIL 없음. 사전 실행의 WARN 1(F-14f3ef, 04-review 부재)은 이 문서 작성으로 닫힌다 — 최종 실행 출력을 `findings.py --source verify-impl` 에 다시 넣어 해소 처리(05-remediation 갱신 줄 참조).

## 2. 수용 기준 대조
backlog "구현 순서" P1 행 문장 그대로: **"9개 테이블 생성, `events.type` 제약 존재"**. 증거는 verifier 가 구현자 스크립트를 쓰지 않고 psycopg 로 직접 조회한 출력(`independent-query`)을 1차로, 구현자 evidence 와 커밋을 2차로 둔다.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 9개 테이블 생성 | evidence/20260905-1433-verifier-independent-query.txt ([Q1] `information_schema.tables` 9-set rows=9, [Q1b] public 전체 10 = 9 + `alembic_version`, [Q9] 컬럼 총 56), evidence/20260905-1432-verifier-schema-check-head.txt (exit=0, 구현자 evidence/20260905-1414-roundtrip-5-schema-check-after.txt 와 diff IDENTICAL), 09c2bd1, alembic/versions/0001_schema_v2.py | 통과 |
| `events.type` 제약 존재 | evidence/20260905-1433-verifier-independent-query.txt ([Q2] `ck_events_type_valid` = `CHECK ((type = ANY (ARRAY['conflict','praise','meal','meeting','personal_share','favor','other'])))` 1행, [Q3] CHECK 총 4), evidence/20260905-1435-verifier-mutation-models.txt (M1·M2 — 값 하나 빼면 테스트 FAILED), 4dfaf33 | 통과 |

계획(01-plan "판정 방법" 표)의 나머지 항목도 같은 독립 쿼리로 확인했다 — 모두 기대값과 일치(evidence/20260905-1433-verifier-independent-query.txt):
- 나머지 CHECK 3종: [Q3] `ck_persons_relation_tag_valid`(가족·연인·친구·직장·지인 5값), `ck_persons_hierarchy_valid`(상·동·하 3값), `ck_pending_questions_kind_valid`(identity·new_person·schedule 3값). 한글 값이 UTF-8 로 정상 저장·출력됨.
- 벡터 컬럼(D4 D5 R9): [Q4] `person_aliases.embedding` = `vector(1536)`, `attnotnull=False`(nullable).
- `person_embeddings` 부재(R9): [Q5] 0행. 벡터 인덱스(hnsw/ivfflat) [Q11] 0개(계획 결정 5 — P3-er 로 이연).
- `fact_sources` 실재·복합 PK(R8): [Q6] `pk_fact_sources` = `PRIMARY KEY (fact_id, event_id)`.
- FK CASCADE: [Q7] 6행 전부 `confdeltype='c'` — `events/person_aliases/person_facts/schedules.person_id → persons`, `fact_sources.fact_id → person_facts`, `fact_sources.event_id → events`.
- 인덱스: [Q8] `ix_*` 10개(부분 인덱스 `ix_pending_questions_session_id_unanswered` 포함). 총 19 = ix 10 + pk 9.
- NOT NULL 정책(F-08e812): [Q10] nullable 은 정확히 `answer, answered_at, confirmed_at, embedding, briefed_at` 5개 — S3.2 필수 인자(`add_event` 5개·`add_schedule` 3개·`ask_user` 4개·`create_person` 4개)에 대응하는 컬럼은 전부 NOT NULL.
- `pending_questions.status` 컬럼 없음: [Q12] 0행(01-plan "하지 않는 것").
- 되돌리기 왕복: 구현자 evidence 8개 파일의 `exit=` 줄을 직접 읽어 확인 — roundtrip-1~5·alembic-check 모두 exit=0, badport exit=2, database-url exit=0; roundtrip-2 `Running downgrade 0001 -> `, roundtrip-3 `9 tables absent … PASS` + `alembic_version (empty)`, roundtrip-4 `Running upgrade  -> 0001`(evidence/20260905-1440-verifier-static-checks.txt [S6]).
- 모델↔마이그레이션 일치: evidence/20260905-1437-verifier-alembic-check.txt `No new upgrade operations detected.` exit=0.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 verifier 가 직접 실행. 모든 DB 명령은 `POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8`, 파일 리다이렉트(tee 미사용).

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 모델에서 `EVENT_TYPES` 값 하나(`other`) 제거 → 테스트가 잡는가 | `app/db/models.py` 임시 수정 → `python -m pytest tests/test_schema_models.py tests/test_schema_check.py -q` → 원복 | evidence/20260905-1435-verifier-mutation-models.txt M1: `test_events_type_check_contains_all_seven_event_types` + `test_check_value_constants_are_the_same_object…` FAILED(2 failed, 26 passed) |
| CHECK SQL 리터럴에서만 `'other'` 제거(튜플은 그대로) — 제약 문장 자체가 틀린 경우 | 같은 방식 | 같은 파일 M2: `test_events_type_check_contains_all_seven_event_types` FAILED(1 failed) — 튜플과 리터럴이 이중 출처이지만 테스트가 둘의 어긋남을 잡는다 |
| `schedules.person_id` FK 의 `ondelete="CASCADE"` 제거 | 같은 방식 | 같은 파일 M3: `test_all_six_foreign_keys_have_ondelete_cascade` FAILED |
| `embedding` 을 `Vector(3072), nullable=False` 로 변경(D4 위반) | 같은 방식 | 같은 파일 M4: 차원·nullable·DDL 컴파일 테스트 3건 FAILED |
| 변이 원복 확인 | 각 변이 후 `cp` 원본 복원 → `git diff --stat -- app/db/models.py` | 같은 파일: 매번 `[]`(빈 diff), 최종 `cmp` IDENTICAL, `pytest tests/ -q` 49 passed, `git status --short` 코드 경로 변경 없음 |
| `schema_check.py` 가 실제 DB 어긋남을 잡는가 — head 상태에서 "비어 있어야 한다"고 기대 | `python scripts/schema_check.py --expect-empty` | evidence/20260905-1437-verifier-expect-empty-at-head.txt `[FAIL] 9 tables absent (--expect-empty) -> still present: […9개]`, **exit=1** |
| 잘못된 포트 → 접속 실패 rc=2, 비밀번호 미출력 | `POSTGRES_PORT=5599 python scripts/schema_check.py` | evidence/20260905-1437-verifier-badport-5599.txt `[error] DB 접속 실패: ConnectionTimeout …` **exit=2**; 출력에 `user=app host=localhost port=5599 dbname=relationship` 만. 토큰 검사 `:pass@` 0, 단어 `pass` 0, `postgresql://` 0(`password` 1건은 검사 라벨 줄 자체) |
| 모델과 마이그레이션이 갈라지지 않았는가 | `python -m alembic check` | evidence/20260905-1437-verifier-alembic-check.txt `No new upgrade operations detected.` exit=0 |
| 전체 테스트 | `python -m pytest tests/ -q` | evidence/20260905-1439-pytest.txt 49 passed(= config 5 + models 17 + schema_check 11 + 기존 db_check 6 + embed_pilot 10) |
| `alembic.ini` 에 접속 문자열이 없는가 | `grep -nE '^sqlalchemy\.url' alembic.ini` | evidence/20260905-1440-verifier-static-checks.txt [S1] `93:sqlalchemy.url =`(값 공란), 한글 줄 0(cp949 사유는 03-log U3·커밋 09c2bd1 본문에 기록 [S8]) |
| 키 패턴·비밀번호 하드코딩 | `git grep -nIE 'sk-…|AKIA…|BEGIN … PRIVATE KEY|postgresql://…:…@'`(evidence·패키지 문서 제외) | [S2] 키 패턴 0. `postgresql://…:…@` 히트는 `.env.example:14` 공개 예시값, `app/config.py:72` f-string 템플릿, 테스트의 가짜 값(`pw1`·`pwone`·`pass`)뿐. `DEFAULT_PASSWORD = "pass"` 는 compose 기본값과 같은 예시값(P0-compose F-033bb1 결정 (a)) |
| P0-compose 산출물 불변 | `git log --oneline -- docker/ docker-compose.yml` | [S3] 749bb8e 한 건(P0-compose U1)에서 멈춤, 작업 트리 diff 없음 |
| 범위 밖 산출물 부재 | grep: `app/main.py`, FastAPI import, `relationship(`, `hnsw|ivfflat`, `status` 컬럼, `sessionmaker|create_engine`(app/), `users|person_relations|relationships` 테이블 | [S4] 전부 없음. `person_embeddings` 문자열은 부재 검사·docstring 에만 |
| 셸에서 D-R-O-P 를 실행한 흔적 | 저장소 전체 토큰 위치 집계 + `execute|psql … dr?p` 형태 검색 | [S5] 코드에서는 `alembic/versions/0001_schema_v2.py`(downgrade 19건)뿐, evidence 에서는 autogenerate 원본 복사본 1파일뿐, 셸 실행 형태 0. 나머지는 계획·점검 문서의 금지 서술 |
| 왕복 evidence 의 exit 줄이 모두 기대값인가 | 8개 파일 직접 읽음 | [S6] 위 §2 참조 — 전부 일치 |
| requirements 핀 = 설치 버전 | `pip freeze` evidence 대조 | [S7] SQLAlchemy 2.0.50 / alembic 1.19.2 / psycopg[binary] 3.3.5 / pgvector 0.5.0 / pytest 9.0.3 일치 |
| `ConnInfo` 객체를 그대로 찍으면 비밀번호가 새는가(계획 16행 "비밀번호를 로그·예외 메시지에 찍지 않는다") | 가짜 비밀번호로 `repr(conn)` 검사(os.environ 미사용) | evidence/20260905-1445-verifier-conninfo-repr.txt — **repr/str 에 포함됨(True)**, safe_summary 는 미포함. 현재 호출부는 모두 safe_summary 만 쓰므로 실제 유출은 없음 → 권고 F-8eeb9b(§6) |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- 아직 바꾸지 않았다 — `/devlog done` 에서 메인 세션이 바꾼다. 적을 해시:
  - **R8** "시맨틱→원문 링크 없음" → `구현완료(4dfaf33, 09c2bd1 — fact_sources(fact_id, event_id) 복합 PK·FK CASCADE 2)`. 모델 4dfaf33 + 마이그레이션 09c2bd1. P6-memory 가 실제 링크를 쓴다는 "다음 카드"는 유지.
  - **R9** "인물당 임베딩 1개" → `구현완료(4dfaf33, 09c2bd1 — person_aliases.embedding vector(1536) nullable, person_embeddings 없음)`. P3-er(후보 검색 top-K→인물별 max) 는 유지.
  - 근거: evidence/20260905-1433-verifier-independent-query.txt [Q4][Q5][Q6][Q7].

## 5. registry.md 에 올린 산출물
- P1-schema 소유 신규 행 **10개**(registry 38~47행): `app/config.py`, `app/db/base.py`, `app/db/models.py`, `alembic/`(ini·env·mako·0001), `scripts/schema_check.py`, `requirements.txt, requirements-dev.txt`(1행), `tests/test_config.py`, `tests/test_schema_models.py`, `tests/test_schema_check.py`, `tests/conftest.py`. 03-log U5 의 "11개" 는 파일 수를 센 오기(F-36bed6).
- 기존 행 비고만 갱신, 새 행 없음: `README.md` 행 1개(32행), `scripts/db_check.py` 행 1개(37행) — `grep -c '| README.md |'`=1, `grep -c '| scripts/db_check.py |'`=1 (evidence/20260905-1440-verifier-static-checks.txt [S10]). 계획 단계 권고 F-0ffff5·F-c57789·F-8c9c5b 의 완료 판정 조건 충족.
- 정정 필요(F-36bed6): 38행 커밋 열 `9397066, d7113e9, 4dfaf33, 09c2bd1, 03e3ce3` → 실제 `d7113e9` 만, 39행 `d7113e9, 4dfaf33` → `d7113e9` 만(`git log -- app/config.py app/db/base.py`). 37행 `scripts/db_check.py` 의 커밋 열은 P0-compose 때부터 `pending` 인 채 d7113e9·ec2fe8c 가 수정했으니 이번에 함께 채우는 것이 맞다.
- `alembic/README`(alembic init 이 만든 1줄 보일러플레이트)가 09c2bd1 에 포함됐으나 산출물 목록·registry 에 없다 — 무해, `alembic/` 행이 폴더 단위이므로 추가 행 불필요.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
필수 소견 0. 완료를 막는 항목 없음. 권고 3건은 05-remediation 에 원인 분석까지 채웠고 해결은 P2-tools 착수 단위(backend-agent)/메인 세션 몫이다.

- **F-36bed6 [권고] registry 커밋 열 부정확 + 03-log "11행".** §5 참조. 메인 세션이 `/devlog done` 문서 커밋에서 38·39(·37)행만 고치면 닫힌다.
- **F-8eeb9b [권고] `ConnInfo` dataclass repr 에 password 포함.** evidence/20260905-1445-verifier-conninfo-repr.txt. P0-compose 정의를 그대로 옮긴 기존 결함이며 현재 유출 경로 없음. P2-tools 가 엔진·세션·예외 처리를 넣기 **전에** `field(repr=False)` + `repr(conn)` 테스트 1건.
- **F-c7078e [권고] `alembic/script.py.mako` 에 P1-schema Refs 고정.** 후속 revision 이 P1 태그를 상속하면 `git log --grep` 영향 범위 계산이 오염된다. P3-er 첫 revision(벡터 인덱스) 때 템플릿 자리표시자로 바꾸거나 생성 직후 Refs 를 고쳐 쓰는 절차를 그 패키지 01-plan 에 둔다.
- **02-plan-verify §3 의 "55컬럼" 은 verifier(나)의 집계 오차였다.** 같은 문장의 테이블별 수치 7+6+6+2+7+5+9+5+9 = **56** 이고, 03-log 착수 항목·커밋 9397066 본문의 "S3.1 55컬럼" 도 이를 그대로 옮긴 것이다. 구현자가 U2 에서 S3.1 을 직접 세어 56 으로 정정했고(03-log U2 "위임 프롬프트와 다르게 한 것"), 독립 쿼리 [Q9] 총 56·`test_total_column_count_equals_56…` 이 이를 확인한다. 승인된 02-plan-verify 본문은 고쳐 쓰지 않고 여기 기록으로 남긴다. 교훈: 합계는 손으로 더하지 말고 명령 출력으로 적는다.
- 관찰(조치 불필요):
  - O1. `verify-impl` 의 "태그 P1-schema 커밋 10 건" 중 4건(819e1ac·7397966·749bb8e·23d8700)은 본문에서 P1-schema 를 언급한 P0-compose 커밋이다. 이 패키지의 커밋은 6건.
  - O2. `scripts/schema_check.py` 의 CHECK 값 검사는 `pg_get_constraintdef` 문자열들을 이어붙인 뒤 값이 부분 문자열로 있는지만 본다(persons 의 두 검사가 같은 `all_defs` 를 공유). 컬럼이 뒤바뀐 CHECK 도 통과할 수 있으나, 모델 테스트(`checks` 를 컬럼별로 잡음)와 `alembic check` 가 이중으로 막는다. P2 에서 손댈 필요 없음.
  - O3. 모델의 CHECK 는 SQL 리터럴이고 `EVENT_TYPES` 등 튜플과 이중 출처다. M1·M2 변이가 각각 잡히므로 현재는 안전. P2 가 값 집합을 바꿀 일이 생기면 튜플에서 리터럴을 생성하는 쪽이 낫다.
  - O4. `alembic/env.py` 는 `resolve_connection()` 의 불일치 경고(`_warnings`)를 버린다 — `DATABASE_URL` 과 `POSTGRES_PORT` 가 어긋나도 alembic 은 조용히 `DATABASE_URL` 로 간다(규칙 자체는 db_check 와 동일). 이름만 있는 경고이므로 stderr 로 내보내도 비밀 유출 없음. 선택 사항.
  - O5. `DEFAULT_PASSWORD = "pass"` 등 기본값이 `app/config.py` 에 있어 환경변수가 하나도 없으면 로컬 compose 기본값으로 접속을 시도한다(P0-compose 결정 그대로). P9-infra 에서 운영 환경은 `DATABASE_URL` 필수로 바꿀지 결정.
  - O6. 03-log 각 항목의 hash 는 `pending` 으로 남아 있다(위임 프롬프트가 허용). 실제 해시는 §머리말의 6개.
  - O7. verifier evidence 파일명의 시각(1432~1446)은 손으로 붙인 순번이라 실제 수정 시각(14:32~14:35, `ls --time-style`)보다 최대 10분 앞선다. 실행 순서는 파일명 순과 같고 내용은 그대로다. 기계 검증 파일(1431·1439)은 스크립트가 붙인 실제 시각.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- **모델 import 경로**: `from app.db.models import Person, PersonAlias, PersonFact, FactSource, Event, Schedule, PendingQuestion, PushSubscription, AgentTrace`; `from app.db.base import Base`. 값 집합 상수 `EVENT_TYPES`(7)·`RELATION_TAGS`(5)·`HIERARCHIES`(3)·`QUESTION_KINDS`(3) 는 `app.db.models` 에서만 import 한다(schema_check 도 그렇게 한다 — 재정의 금지, registry 40행).
- **접속**: `app.config.resolve_connection()`(우선순위 `DATABASE_URL` > `POSTGRES_*`+기본값, `POSTGRES_HOST` 선택) → `ConnInfo.sqlalchemy_url()` = `postgresql+psycopg://…`. 로그에는 `safe_summary()` 만. **엔진·`sessionmaker`·요청 단위 세션·FastAPI 앱은 없다** — P2-tools 가 만든다(01-plan 결정 4). 만들 때 F-8eeb9b(`repr=False`)를 먼저 처리.
- **마이그레이션 운용**: `POSTGRES_PORT=5433 alembic upgrade head` / `alembic check`(모델 변경 후 0건이어야 함) / 새 revision 은 `alembic revision --autogenerate -m …` 뒤 손보정 + Refs 줄 교체(F-c7078e). `alembic.ini` 는 영어 주석만(cp949). 스키마 되돌리기는 `alembic downgrade` 만(security.md §4).
- **NOT NULL 계약(F-08e812)**: 툴이 반드시 채워야 하는 컬럼 — `add_event` 는 `type∈EVENT_TYPES, content, raw_utterance, occurred_at`; `add_schedule` 는 `title, scheduled_at`; `ask_user` 는 `kind∈QUESTION_KINDS, question, options(JSONB), context(JSONB)`; `create_person` 은 `display_name, relation_tag∈RELATION_TAGS, hierarchy∈HIERARCHIES` + `user_id`. 비워 둘 수 있는 것은 `embedding, confirmed_at, briefed_at, answer, answered_at` 뿐. `person_aliases.source` 도 NOT NULL 이므로 별칭을 만들 때 출처 문자열을 정해야 한다(값 집합은 S3.1 미정 — P2 결정).
- **`agent_traces` 와 원칙9**: `tool_name`·`tokens_in`·`tokens_out` 이 NOT NULL 이다. ER 4단계 중 툴 호출이 아닌 단계(규칙 필터, LLM 판정)의 trace 에 `tool_name` 을 무엇으로 넣을지(예: step 이름 또는 `"-"`)와 토큰 0 처리를 P3-er 01-plan 에서 정한다. `output` JSONB 에 `candidates[]`·`confidence_breakdown{}`·`decision` 을 넣는 규약은 S3.1 그대로.
- **`pending_questions.status` 파생(F-081752, S3.4)**: 컬럼이 없다. `pending` = `answered_at IS NULL AND created_at >= now() - interval '24 hours'`, `expired` = `answered_at IS NULL AND created_at < …`, `answered` = `answered_at IS NOT NULL`. 부분 인덱스 `ix_pending_questions_session_id_unanswered`(`WHERE answered_at IS NULL`)가 pending+expired 를 함께 덮는다. P2-tools 01-plan 에 이 규칙을 명시.
- **인물 완전 삭제 사각지대(security.md §5)**: `pending_questions`·`agent_traces` 는 person FK 가 없어 `DELETE persons` CASCADE 로 지워지지 않는다. `DELETE /persons/{id}` 구현 시 `context`/`input`/`output` JSONB 안의 person_id 참조를 애플리케이션이 정리하거나 익명화하는 절차가 필요 — P2-tools 이후(01-plan 미결 그대로).
- **`persons.user_id`**: FK 없는 `TEXT NOT NULL`. 단일 사용자 식별자를 어디서 얻을지(설정값) P2 결정. 모든 조회에 `user_id` 조건.
- **`person_facts(person_id, key)` UNIQUE 없음**: 승격이 갱신인지 누적인지는 P6-memory 결정. D9 패턴 `key="pattern:{type}"` 은 TEXT 로 들어간다.
- **벡터 인덱스 없음**: P3-er 이 실제 후보 검색 쿼리(연산자 `<=>` 등)와 함께 별도 revision 으로 추가. 1536 은 HNSW 한도 2000 안(D4).
- **의존성 파일 형식**: `requirements.txt` + `requirements-dev.txt`(`==` 고정). ruff·pytest 설정이 늘면 `pyproject.toml` 이전 여부를 P2-tools 착수 때 재검토(01-plan 결정 3 미결). ruff 는 아직 미설치라 verify-impl 은 `compileall` 만 돈다.
- **서버 버전**: 로컬 PostgreSQL 16.15 / pgvector 0.8.6 위에서 DDL 검증. RDS 메이저·pgvector 가용 버전은 P9-infra 에서 재확인(README 177행·registry 비고).

결과: 완료
승인: 사용자 (2026-09-05)