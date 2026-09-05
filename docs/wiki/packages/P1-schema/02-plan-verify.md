# P1-schema · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자(architect, opus)와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-05

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P1-schema | tee docs/wiki/packages/P1-schema/evidence/20260905-1226-verify-plan-4.txt` (이 문서를 쓴 뒤 실행한 최종본. 이전 실행: `evidence/20260905-1217-verify-plan.txt` FAIL 4/WARN 4 → `20260905-1218-2-verify-plan.txt` FAIL 1/WARN 4 → `20260905-1224-verify-plan-3.txt` FAIL 1/WARN 4 — 남은 FAIL 1 은 이 문서의 부재(F-b3534b))
```
== verify-plan P1-schema  (2026-09-05 12:26) ==
PASS  존재: docs/wiki/packages/P1-schema/01-plan.md
PASS  존재: docs/wiki/packages/P1-schema/02-plan-verify.md
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  카드 존재: D8
PASS  패키지 id 등록됨: P0-compose
PASS  패키지 id 등록됨: P0-embed-pilot
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R8
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 백엔드 골격 최소 + DB 접속 설정: `requir
PASS  Refs 있음: - [ ] U2 모델 9개 + 제약·인덱스: `app/db/models.py`
PASS  Refs 있음: - [ ] U3 Alembic 도입 + 초기 마이그레이션: `alembi
PASS  Refs 있음: - [ ] U4 스키마 검사 스크립트 + 왕복 증거: `scr
PASS  Refs 있음: - [ ] U5 문서·registry 반영 + db_check 서버 버전 �
PASS  backlog 일치: 9개 테이블 생성, `events.type` 제약 존재
PASS  의존 완료: P0-compose
PASS  의존 완료: P0-embed-pilot
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: requirements.txt
PASS  registry 중복 없음: requirements-dev.txt
PASS  registry 중복 없음: app/__init__.py
PASS  registry 중복 없음: app/config.py
PASS  registry 중복 없음: app/db/__init__.py
PASS  registry 중복 없음: app/db/base.py
PASS  registry 중복 없음: app/db/models.py
PASS  registry 중복 없음: alembic.ini
PASS  registry 중복 없음: sqlalchemy.url
PASS  registry 중복 없음: alembic/env.py
PASS  registry 중복 없음: app.confi
PASS  registry 중복 없음: alembic/script.py.mako
PASS  registry 중복 없음: alembic/versions/0001_schema_v2.py
PASS  registry 중복 없음: scripts/schema_check.py
PASS  registry 중복 없음: tests/conftest.py
PASS  registry 중복 없음: sys.path
PASS  registry 중복 없음: tests/test_schema_models.py
PASS  registry 중복 없음: tests/test_config.py
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
WARN  registry 에 다른 패키지로 이미 있음: db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
WARN  registry 에 다른 패키지로 이미 있음: scripts/db_check.py → | 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일�
== 결과: FAIL=0 WARN=4 ==
```
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.

WARN 4 건에 대한 판단: 모두 7번 항목(registry 중복)이며 대상은 `README.md`(2건)·`scripts/db_check.py`(2건, 경로 표기 차이로 중복 검출). 01-plan 27행 "기존 행 비고 갱신(`README.md` 행, `scripts/db_check.py` 행 — **새 행 금지**)"과 U5 "`README.md` 행과 `scripts/db_check.py` 행 **비고만** 갱신(새 행 금지)" 이 명시돼 있으므로 의도된 WARN 이다(P0-compose 04-review §5 와 같은 처리). 완료 검토에서 `grep -c` 로 행 수 불변을 확인한다(05-remediation F-0ffff5·F-c57789·F-8c9c5b 의 완료 판정 명령).

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱". 01-plan 17행 모델 9개는 S3.1 목록 그대로이고 34행 "하지 않는 것"에 "**인물–인물(A–B) 관계 테이블**(원칙7, D8) … 만들지 않는 것이 이 패키지의 산출물이며, 부재를 `scripts/schema_check.py` 가 검사한다". 산출물 목록(42~60행)에 화면·음성·상담 관련 파일 없음. `specs/S3.1-schema-v2.md` "인물–인물 관계 테이블 없음 (D8, 원칙7)" 과 일치 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙7: 위 1행. 원칙8 `CLAUDE.md` "평가 수치는 재현 가능해야 한다" → 01-plan 26행 "`alembic upgrade head` → `schema_check` → `alembic downgrade base` → 테이블 부재 확인 → 재 `upgrade head` 왕복 출력, `pytest` 출력, `pip freeze` 출력을 `tee` 로 남긴다", 109행 결정 5 "데이터 0건 시점에서는 … 인덱스 파라미터를 정당화할 측정치가 없다(원칙8)". 원칙9 `CLAUDE.md` "`agent_traces`에 step·입력·출력·툴·토큰(in/out)·후보·확신도 분해를 기록" → 01-plan 17행 `agent_traces` 포함, 23행 "`agent_traces.input`·`agent_traces.output` 은 **JSONB**; … `tokens_in/tokens_out` 은 `INTEGER`". 원칙2 임계치·원칙3 3신호·원칙4 4단계·원칙1 오병합은 ER 로직(P3-er)이라 이 패키지에 해당 없음 — 01-plan 32행 "ER 로직·후보 검색 쿼리·거리 연산자 사용 — P3-er"로 명시 제외. 원칙5 화면 없음. 원칙6 `person_facts(key="pattern:{type}")` 저장 가능 — 3행 참조 |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D04-embedding-provider.md` "차원 N은 설정값이며 마이그레이션에 하드코딩하되 그 근거를 `reports/embed_pilot.md`에 남긴다" / "확정 … **N = 1536**" → 01-plan 19행 "`person_aliases.embedding` = `vector(1536)` (D4 확정 차원, D5 별칭 단위)". `D05-alias-level-embedding.md` "인물당 대표 벡터를 만들지 않는다" / "`person_embeddings` 테이블 없음" → 01-plan 34행 "`person_embeddings` 테이블(D5, R9). 만들지 않는 것이 이 패키지의 산출물", 25행 schema_check 가 부재 검사. `D08-title-relationship-memory.md` "인물–인물 엣지 테이블·필드를 만들지 않는다. 이름에 graph 를 쓰지 않는다" → 34행 제외, 산출물 경로에 graph 없음. `D09-pattern-rule.md` "`person_facts(key="pattern:{type}", …)` 생성·갱신, 근거 이벤트를 `fact_sources`에 연결" → 01-plan 23행 `key` 는 `TEXT`, 115행 "UNIQUE 를 걸지 않고 인덱스만 둔다" — 저장 가능, 21행 `fact_sources` 복합 PK `(fact_id, event_id)`. `D02-ask-user-async.md` "질문을 `pending_questions`에 저장 … `POST /answers/{question_id}`가 저장된 `context`로 루프를 재개" → 17행 `pending_questions` 포함, 23행 `options`·`context` JSONB. D2 "동기 대기(sleep/poll) 금지"는 스키마와 무관 |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.1-schema-v2.md` 코드 블록 9줄(`persons … agent_traces`)과 01-plan 17행 테이블 9개 이름 일치. 컬럼 대조(아래 §3 "S3.1 대비 차이" 참조): 누락 0, 추가 0 — 01-plan 17행 "컬럼 집합은 S3.1 5~15행과 글자 그대로 대응시키고, 임의의 컬럼을 추가하지 않는다", 38행 "`users` 테이블 신설, `pending_questions.status` 컬럼 신설 등 **S3.1 에 없는 컬럼·테이블 추가**" 를 하지 않는 것으로 명시. S3.1 "`events.type` CHECK 제약: `conflict / praise / meal / meeting / personal_share / favor / other`" / "`relation_tag` ∈ {가족, 연인, 친구, 직장, 지인}, `hierarchy` ∈ {상, 동, 하}" / "`pending_questions.kind` ∈ {identity, new_person, schedule}" → 01-plan 18행 CHECK 4개 값 집합 동일. S3.1 "인물 단위 완전 삭제 … → FK ON DELETE CASCADE" → 20행 FK 6개 CASCADE. S3.1 `embedding vector(1536)` → 19행. `specs/S3.2-tools-v2.md` `add_event(person_id, type, content, occurred_at, raw_utterance)` → `events` 컬럼에 `raw_utterance` 있음; `get_briefing … "`briefed_at` 기록"` → `schedules.briefed_at` 있음; `ask_user(kind, question, options, context)` → `pending_questions` 4컬럼 있음. `status` 컬럼: S3.1 에 없음 → 계획 116행 "`status` 는 `answered_at IS NULL` 에서 파생되는 값이며, 스키마에 컬럼을 추가하지 않는다" 는 권위 스키마(S3.1)와 일치하며 D2 의 `{question_id, status:"pending"}` 는 API 반환값이라 충돌 없음(단 `S3.4` "status=expired" 파생에는 `created_at` 도 필요 — §3 관찰 b). 임계치 2개·ask_user 비동기 동작은 P2/P3 범위 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 22행 "의존: 착수 준비(D4 차원 확정, docker-compose)" → 14행 `[x] 임베딩 공급자 파일럿 (D4)`, 16행 `[x] 로컬 docker-compose (pgvector) … 완료(2026-09-05, 04-review 완료, verify-impl FAIL 0)`. `packages/P0-embed-pilot/04-review.md` 67~68행 "결과: 완료 / 승인: 사용자 (2026-09-03)" — 커밋 `e4ab0a4`(gitlog: "docs(P0-embed-pilot): U3 카드 반영·완료 검토 — D4 확정, S3.1 vector(1536)"). `packages/P0-compose/04-review.md` 90~91행 "결과: 완료 / 승인: 사용자 (2026-09-05)" — 커밋 `819e1ac`(gitlog: "docs(P0-compose): 완료 — verifier 04-review 완료 판정·사용자 승인, 패키지 닫음"). verify-plan 출력 "PASS 의존 완료: P0-compose / P0-embed-pilot". P4 게이트: `CLAUDE.md` "P4 파일럿 평가 전에 P5 이후 시작 금지" — P1 은 P4 이전이라 해당 없음(01-plan 5행). P0-compose 04-review §7 인계 5건 반영: "initdb 에 SQL 을 추가하지 말고 Alembic 으로" → 01-plan 35행 제외; "`CREATE EXTENSION IF NOT EXISTS vector` 를 한 번 더 두어도 무해" → 24행 upgrade 첫 줄; "의존성 선언 파일이 아직 없다 … `psycopg[binary]` 3.3.5" → 13행 requirements; "볼륨 … 삭제는 사용자만 … Alembic downgrade 로" → 36행; 포트 5433(§6 O6) → 74행 "로컬 컨테이너는 5433 에 떠 있으므로 포트를 **셸 변수로 넘긴다**". §6 O1(서버 버전) → 28행 U5 반영 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 22행 "수용기준: 9개 테이블 생성, `events.type` 제약 존재" = 01-plan 70행 "- 9개 테이블 생성, `events.type` 제약 존재". verify-plan 출력 "PASS backlog 일치: 9개 테이블 생성, `events.type` 제약 존재". 기계적 판정 가능성: 01-plan 86~97행 표에 `information_schema.tables` 9행, `pg_constraint` 의 `CHECK (type IN (...))` 한 줄 등 명령·기대 출력이 쌍으로 있음 |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan 63~67행 U1~U5 각 줄 끝 "Refs: P1-schema R8 R9 D4 D5 S3.1" — 속한 P·닫는 R·기대는 D·구현하는 S 모두 포함(SKILL.md 태그 규칙). verify-plan 출력 "PASS Refs 있음" 5건. 같은 태그의 기존 커밋: S3.1/D5 는 `e4ab0a4`·`749bb8e`·`0ee6e25` 등 P0 커밋에만 있고 P1-schema 코드 커밋은 0건(gitlog `## 태그 'R8' 커밋` / `'R9'` 비어 있음) — 착수 전 상태와 일치 |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다" → 01-plan 16행 "`.env` 는 읽지도 쓰지도 않는다(security.md §1). 값은 `os.environ` 에서만 읽고, 반환한 접속 문자열·비밀번호를 로그·예외 메시지에 찍지 않는다"; §1 "코드·문서·커밋에 키 문자열을 넣지 않는다" → 24행 "`alembic.ini`(`sqlalchemy.url` 은 **비워 둔다** — 비밀이 ini 에 들어가면 안 된다)". 판정 방법 78행의 접속 문자열 `postgresql://app:pass@localhost:5433/relationship` 은 `.env.example` 14행 공개 예시값과 동일(포트만 5433). §4 "셸에서 `DROP`/`TRUNCATE` 금지 — 대신: Alembic 마이그레이션 파일로 작성해 검토" → 36행 "스키마를 되돌릴 때는 `alembic downgrade` 만 쓴다. `DROP TABLE` 은 검토 가능한 마이그레이션 파일 안에만 존재한다"; `alembic downgrade base` 는 카드가 지시한 "대신" 경로이며 P0-compose 04-review §7 "스키마 초기화가 필요하면 Alembic downgrade 로" 와 일치. 집행부 `safety-guard.sh` 115행은 셸 명령 문자열의 `drop table` 만 차단하므로 `alembic downgrade` 는 막히지 않는다. §4 "`compose down -v` 금지" → 36행 제외. §3 재귀 삭제 → 66행 U4 "생성 파일은 즉시 삭제"는 단일 파일. §5 "`DELETE /persons/{id}` → CASCADE" → 20행 FK CASCADE; "모든 조회는 `user_id` 조건" → 113행 `user_id TEXT NOT NULL` + 인덱스. 외부 전송 없음 |

계획 품질(절차 4번): "하지 않는 것" 11개 항목(29~39행)이 P1-pilot-dataset·P2-tools·P3-er·P6-memory·P9-infra 로 경계를 명시. 작업 단위 U1~U5 는 각각 파일 묶음 하나(골격+설정 / 모델+테스트 / Alembic+revision / 검사 스크립트+왕복 증거 / 문서) — 커밋 하나 크기. 수용 기준은 SQL·종료 코드로 판정 가능.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
보류(필수) 소견: **없음.**

S3.1 대비 컬럼 대조(verifier 직접 대조, 9테이블 55컬럼): `persons` 7 / `person_aliases` 6 / `person_facts` 6 / `fact_sources` 2 / `events` 7 / `schedules` 5 / `pending_questions` 9 / `push_subscriptions` 5 / `agent_traces` 9 — 계획 17~23행의 모델 명세·타입 정책은 S3.1 컬럼 이름을 하나도 빼거나 더하지 않는다. S3.1 이 정하지 않은 것(타입·NULL 허용·인덱스)을 계획이 정했고(23·113·114·115행) 그중 S3.1 개정이 필요한 항목은 없다(컬럼·테이블 집합이 그대로이므로).

권고 관찰(통과를 막지 않음 — 구현·완료 검토에서 확인. `findings.py --source review` 로 05-remediation 에 [권고] 소견 등록 — 출력 파일 `evidence/20260905-1228-plan-review-observations.txt`. d 는 절차 안내라 소견 없음):
- a. **F-ace4dd · 접속 해석 규칙의 이중 구현.** 01-plan 16행은 `app/config.py` 가 `scripts/db_check.py` 의 `resolve_connection()` 과 "**같은 우선순위·같은 변수 이름**" 으로 동작한다고만 하고, 재사용인지 재구현인지 정하지 않았다. 재구현이면 `CLAUDE.md` "registry.md(무엇이 있는가 — … 중복 구현 금지)" 와 P0-compose 04-review §6 O5 "P1/P2 에서 DB 설정 모듈로 흡수될 때 정리" 에 어긋난다. 권고: U1 에서 `app/config.py` 를 단일 구현으로 두고 U5 의 `db_check.py` 수정 시 그것을 import 하거나(테스트 `tests/test_db_check.py` 는 유지), 둘을 유지하는 이유를 03-log 에 적는다. 완료 검토에서 `grep -n "DATABASE_URL" app/config.py scripts/db_check.py` 로 확인.
- b. **F-081752 · `status` 파생 규칙이 불완전하게 서술됨.** `specs/S3.4-ask-user-protocol.md` "미답변 24시간 후 만료(`answered_at` null 유지, status=expired)" — `pending`/`expired` 구분에는 `answered_at IS NULL` 외에 `created_at` 도 필요하다. 스키마 변경은 필요 없고(S3.1 에 `status` 없음, 계획 38행 제외가 옳다), 부분 인덱스 `WHERE answered_at IS NULL` 도 유효하다. P2-tools 계획에서 파생 규칙(`answered_at IS NULL AND created_at >= now() - 24h` = pending)을 명시하도록 인계 사항으로 남길 것.
- c. **F-08e812 · NULL 허용 정책이 타임스탬프 계열에만 명시됨**(114행). `display_name`·`alias`·`content`·`raw_utterance`·`question`·`endpoint`·`step`·`tool_name` 등의 NOT NULL 여부는 계획에 없다. S3.1 도 정하지 않으므로 계획 결함은 아니나, U2 구현 시 결정을 03-log 에 적고 `tests/test_schema_models.py` 에 포함할 것(S3.2 시그니처의 필수 인자에 대응하는 컬럼은 NOT NULL 이 자연스럽다).
- d. **집행 훅과의 접점.** `safety-guard.sh` 115행은 Bash 명령 문자열에 `drop table` 이 있으면 차단한다. 마이그레이션 파일(`downgrade()` 의 `op.drop_table`)·`schema_check.py` 는 Write 도구로 쓰고, Bash heredoc 으로 SQL 주석에 `DROP TABLE` 문자열을 넣지 말 것. 우회가 아니라 절차 안내(security.md §6).
- e. **F-75c1c1 · `POSTGRES_HOST`(P0-compose O5) 미해결.** 01-plan 16행 "호스트 기본값 `localhost`" 만 있다. `app/config.py` 가 `POSTGRES_HOST` 를 읽으면 `.env.example` 에 이름을 올리고, 읽지 않으면 U5 의 `db_check.py` 수정 때 132행을 정리할지 03-log 에 적을 것.

## 4. 결정
결과: 통과
승인: 사용자 (2026-09-05)
