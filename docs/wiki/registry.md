# registry — 구현 목록 (무엇이 이미 있는가)

> 목적: **이미 만든 것을 다시 만들거나, 만들었다고 착각하는 것**을 막는다.
> 규칙: 작업 단위를 시작하기 전에 이 표를 `grep` 한다. `/commit` 마다 새 산출물을 한 줄씩 추가하고, `/devlog done` 에서 패키지 행을 확정한다. `verify-plan.sh`(중복 경고)·`verify-impl.sh`(등록 확인)가 이 파일을 읽는다.
> 종류: 모듈 · 엔드포인트 · 툴 · 테이블 · 마이그레이션 · 테스트 · 스크립트 · 데이터셋 · 리포트 · 문서 · 훅 · 스킬

| 종류 | 이름 | 경로 | 패키지 | 커밋 | 비고 |
|------|------|------|--------|------|------|
| 문서 | 기획서 원본 | docs/proposal.md | 하네스 | pending | 본문 수정 금지 |
| 문서 | 검증 20항목 | docs/proposal-review.md | 하네스 | pending | 색인은 wiki/review-index.md |
| 문서 | 해결 계획서 D1~D10·S3.1~3.7·P1~P11 | docs/resolution-plan.md | 하네스 | pending | 카드는 wiki/decisions, specs |
| 문서 | backlog | docs/backlog.md | 하네스 | pending | 수용 기준의 권위 |
| 훅 | 단계 게이트 | .claude/hooks/stage-gate.sh | 하네스 | pending | CURRENT active/frozen |
| 훅 | 커밋 승인 가드·정리·승인 | .claude/hooks/commit-guard.sh, commit-cleanup.sh, approve-commit.sh | 하네스 | pending | |
| 훅 | 보안 가드(명령)·비밀 가드(쓰기) | .claude/hooks/safety-guard.sh, secret-guard.sh | 하네스 | pending | security.md |
| 훅 | 세션 재개·압축·핸드오프 검사 | .claude/hooks/session-start.sh, precompact.sh, handoff-check.sh | 하네스 | pending | HANDOFF.md |
| 훅 | git pre-commit 비밀 검사 | .githooks/pre-commit | 하네스 | pending | core.hooksPath |
| 스크립트 | 계획·구현 기계 검증 | .claude/scripts/verify-plan.sh, verify-impl.sh | 하네스 | pending | verification.md |
| 스크립트 | 검증 출력 → 조치 계획(소견) 동기화 | .claude/scripts/findings.py | 하네스 | pending | packages/<id>/05-remediation.md |
| 스크립트 | 훅 자가 점검 | .claude/scripts/test-guards.sh | 하네스 | pending | 증거: docs/wiki/evidence/ |
| 스킬 | commit · devlog | .claude/skills/commit, .claude/skills/devlog | 하네스 | pending | |
| 스킬 | entity-resolution · eval-harness · agent-observability | .claude/skills/* | 하네스 | pending | 제품 작업법 |
| 에이전트 | architect · backend-agent · eval-agent | .claude/agents/*.md | 하네스 | pending | |
| 스크립트 | git log 요약(에이전트용) · .claude/gitlog.md 스냅샷 | .claude/scripts/gitlog.sh | 하네스 | pending | L-001. session-start·commit-cleanup 훅이 --write 로 갱신 |
| 문서 | 교훈 L-001 브랜치 전략·git log 연동 | docs/wiki/lessons/L-001-dev-branch.md | 하네스 | pending | dev→실서버 검증→main 승격 |
| 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenAIEmbeddingProvider·코사인 행렬·D4 판정 | scripts/embed_pilot.py | P0-embed-pilot | pending | EmbeddingProvider 는 P3-er 에서 백엔드 모듈로 이동(P2-tools 결정4 — `app/embedding.py` 는 Protocol 만 두고 `OpenAIEmbeddingProvider`는 옮기지 않음, U9 에서 좁힘) |
| 테스트 | 임베딩 파일럿 순수 로직(가짜 공급자, 네트워크 없음) | tests/test_embed_pilot.py | P0-embed-pilot | pending | pytest 10 passed |
| 리포트 | 임베딩 파일럿 결과(행렬 2종·선택 근거·N=1536) | reports/embed_pilot.md, reports/embed_pilot/*.json | P0-embed-pilot | pending | 실행 출력 evidence/20260903-embed-pilot-run.txt |
| 에이전트 | verifier — 계획 검증·완료 검토·코드 리뷰 전담(fable, 구현자와 다른 모델) | .claude/agents/verifier.md | 하네스 | pending | L-002 |
| 문서 | 교훈 L-002 역할별 모델 분리(계획 opus · 구현 sonnet · 검증 fable) | docs/wiki/lessons/L-002-role-model-separation.md | 하네스 | pending | verify-plan/impl 이 검증자=verifier 강제 |
| 문서 | 교훈 L-003 dev 푸시 뒤 사용자 결정까지 멈춤 | docs/wiki/lessons/L-003-stop-after-dev-push.md | 하네스 | pending | .awaiting-decision 마커 |
| 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마다 진행 상태 표 갱신. P0-compose: 로컬 DB 절 추가(2026-09-04), pg16 태그는 P9-infra 에서 재확인. P1-schema: 진행 표 P1 행·마이그레이션 절 추가(U5 커밋은 pending). P2-tools U9: 진행 표 P2 행(구현 완료·검증 대기)·"백엔드 실행(FastAPI)" 절 추가(uvicorn·curl /health·POST /answers 예) |
| 훅 | 단계 위임 게이트(Agent 호출 전 사용자 승인 마커) | .claude/hooks/delegate-guard.sh | 하네스 | pending | L-004 |
| 문서 | 교훈 L-004 단계는 묻고 시작 | docs/wiki/lessons/L-004-ask-before-stage.md | 하네스 | pending | |
| 스크립트 | 로컬 pgvector compose(postgres 서비스, `${VAR:-기본값}` 4개, healthcheck) | docker-compose.yml | P0-compose | pending | pgvector/pgvector:pg16, P9-infra 에서 RDS 메이저 버전과 재확인 |
| 스크립트 | pgvector 확장 최초 기동 초기화 | docker/initdb/01-vector.sql | P0-compose | pending | CREATE EXTENSION IF NOT EXISTS vector |
| 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일치 경고) | scripts/db_check.py | P0-compose | pending | 테스트 tests/test_db_check.py. P1-schema U1: 접속 조립을 app.config 로 이동·re-export; U5: SELECT version() 출력 추가 |
| 모듈 | 백엔드 패키지 골격(DB 접속 설정) | app/config.py | P1-schema | d7113e9 | `DATABASE_URL` 우선·없으면 `POSTGRES_*` 조립·`sqlalchemy_url()` — 접속 설정 단일 출처(`scripts/db_check.py`·`scripts/schema_check.py`·`alembic/env.py` 가 여기서 import). 앱·라우터는 P2-tools. P2-tools U1: `ConnInfo.password` 를 `field(repr=False)` 로(F-8eeb9b, 비밀 미노출) |
| 모듈 | SQLAlchemy Base + 명명 규칙 | app/db/base.py | P1-schema | d7113e9 | `DeclarativeBase` + `MetaData(naming_convention=...)`(pk/fk/ix/uq/ck) — 제약 이름이 alembic autogenerate·schema_check 기대값의 근거 |
| 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema | 4dfaf33 | `Person/PersonAlias/PersonFact/FactSource/Event/Schedule/PendingQuestion/PushSubscription/AgentTrace`. 값 집합 상수 `EVENT_TYPES`·`RELATION_TAGS`·`HIERARCHIES`·`QUESTION_KINDS`, CHECK 4·FK CASCADE 6·`fact_sources` 복합 PK·`person_aliases.embedding=Vector(1536)`·인덱스 10(부분 인덱스 1). `person_embeddings` 없음(D5 R9). P2-tools U2: `ALIAS_SOURCES = ("user_said","confirmed","system")` 상수 추가(결정5, 컬럼·CHECK 변경 없음) |
| 마이그레이션 | Alembic 도입 + 초기 스키마 v2 | alembic/ (alembic.ini, alembic/env.py, script.py.mako, versions/0001_schema_v2.py) | P1-schema | 09c2bd1 | `env.py` 가 `app.config` 로 접속 주입 + `render_item` 훅으로 `pgvector.sqlalchemy.Vector` 렌더. `0001` upgrade 첫 줄 `CREATE EXTENSION IF NOT EXISTS vector`, downgrade 는 역순 drop(확장 미삭제). `alembic.ini` 의 `sqlalchemy.url` 공란 |
| 스크립트 | 스키마 v2 실물 검사(9테이블·CHECK 4·vector(1536)·FK CASCADE·인덱스·`person_embeddings` 부재, upgrade/downgrade 왕복용) | scripts/schema_check.py | P1-schema | 03e3ce3 | `--expect-empty` 옵션. 기대값은 `app.db.models`/`app.db.base` 에서 가져옴(중복 정의 없음). exit 0/1(FAIL)/2(접속 실패) |
| 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) | requirements.txt, requirements-dev.txt | P1-schema | d7113e9 | SQLAlchemy 2.0.50 / alembic 1.19.2 / psycopg[binary] 3.3.5 / pgvector 0.5.0 / (dev) pytest 9.0.3. P2-tools U1: `fastapi==0.135.1`·`uvicorn[standard]==0.41.0`·`httpx==0.28.1`(TestClient 용) 3줄 추가(결정10) |
| 테스트 | 접속 설정 해석(DB 없이) | tests/test_config.py | P1-schema | d7113e9 | 5건 — `DATABASE_URL` 우선순위, 부분 지정 시 기본값, 비밀번호 미노출. P2-tools U1: `repr(ConnInfo)`/`str` 비밀번호 미포함 1건 추가(총 6건, F-8eeb9b) |
| 테스트 | 스키마 v2 모델 메타데이터(DB 없이) | tests/test_schema_models.py | P1-schema | 4dfaf33 | 17건 — 테이블 9개·`person_embeddings` 부재, CHECK 4종 값 전수, FK 6개 `ondelete=CASCADE`, `fact_sources` 복합 PK, `embedding` 차원 1536, 인덱스 이름 |
| 테스트 | 스키마 검사 스크립트 순수 로직(DB 없이) | tests/test_schema_check.py | P1-schema | 03e3ce3 | 11건 — 기대 테이블/값 집합이 `app.db.models`·`Base.metadata` 와 동일 객체, `compute_exit_code`, `--expect-empty` 파싱, 출력 포맷 |
| 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftest.py | P1-schema | d7113e9 | `app` 패키지 임포트를 위한 `sys.path.insert` — `tests/test_db_check.py` 기존 방식은 그대로 유지. P2-tools U1: `db_engine`·`db_session`(실 PostgreSQL + 롤백, 결정8)·`fake_embedder` 픽스처, `dbtest` 마커 등록 추가 |
| 모듈 | 엔진·세션(session_scope) | app/db/session.py | P2-tools | f217190 | `get_engine()`(지연 생성·모듈 캐시)·`SessionLocal`(지연 프록시)·`session_scope()`(정상 종료 commit·예외 rollback) |
| 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USER_ID` 기본 `"local"`)·`QUESTION_TTL`(24h)·`SEARCH_TOP_K`(10)·브리핑 N(최근 5/다가오는 3)·`DEFAULT_FACT_CONFIDENCE`(1.0) |
| 모듈 | 임베딩 Protocol | app/embedding.py | P2-tools | a9cb254 | `EmbeddingProvider` Protocol·`EmbedderCallable`·`as_provider()` — 구현체 없음(D4, 결정4: 실 공급자는 P3-er) |
| 모듈 | 툴 재export·TOOL_NAMES | app/tools/__init__.py | P2-tools | 4eca3e9 | 툴 7종 + 툴 밖 보조(`answer_question`/`question_status`/`list_pending`) re-export, `TOOL_NAMES` 튜플(CLAUDE.md 표 순서) |
| 모듈 | 툴 반환 DTO·예외 계층 | app/tools/types.py | P2-tools | 4eca3e9 | `Candidate`·`PersonOut`·`EventOut`·`ScheduleOut`·`PendingQuestionOut`·`BriefingOut`(각 `to_dict()`), `ToolError` 계층(`PersonNotFound`/`ScheduleNotFound`/`QuestionNotFound`/`QuestionNotAnswerable`/`ConfirmationRequired`/`InvalidValue`), `AFFIRMATIVE_KEY` |
| 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | 실행 맥락(`session`/`session_id`/`user_id`/`embedder`/`now`/`confirmed_question_id`), `agent_traces` 기록 데코레이터(원칙9, `step=tool_call`/`tool_error`), `to_jsonable()`·`TRACE_MAX_STRING` 절단 |
| 모듈 | search_person·create_person·update_person | app/tools/persons.py | P2-tools | a9cb254 | 별칭 정확/부분 일치 ∪ 임베딩 top-K 인물별 max(배제 없음, 결정3), D1/D6 확인 강제(`_require_confirmation`, 긍정 답 규약 F-b97a06), 별칭 격상(미결7), `person_facts` upsert(결정6) |
| 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVENT_TYPES` 검사, aware datetime 강제(미결3, naive 거절), `raw_utterance` 원문 그대로 저장, 패턴 감지·승격 트리거 없음(원칙6·D9 는 P6-memory) |
| 모듈 | ask_user·answer_question·question_status | app/tools/questions.py | P2-tools | 8162e09 | `pending_questions` 저장·`{question_id,status:"pending"}` 반환(D2, 동기 대기 없음), 24h 만료 파생(F-081752), 긍정 답 규약(`AFFIRMATIVE_KEY`) 강제 |
| 모듈 | get_briefing | app/tools/briefing.py | P2-tools | 7c94aad | `person_facts` 전부·최근 events 5·다가오는 schedules 3 조회, `schedule_id` 주어질 때만 `briefed_at` 기록, 문장화·제안·LLM 호출 없음(결정7, 원칙7) |
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()`(라우터 등록 + 도메인 예외→HTTP 매핑 8종, import·기동 시 엔진 생성 없음), 모듈 레벨 `app` |
| 엔드포인트 | 라우터 재export | app/api/__init__.py | P2-tools | 4d5817e | `router` 재export(`app/main.py` 조립용) |
| 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py | P2-tools | 4d5817e | `get_session()`(요청 단위 세션, commit/rollback/close), `build_ctx()`(답할 `pending_questions` 행의 `session_id` 사용, 결정12) |
| 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-tools | 4d5817e | `/health`: SELECT 1 + `alembic_version`, 실패 시 `main.py` 캐치올이 503; `/answers/{id}`: `answer_question` 호출까지(재개는 P5-loop, R7·D2) |
| 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools | 4d5817e | `AnswerIn`·`AnswerOut`·`HealthOut`(pydantic v2, 접속 정보·비밀 필드 없음) |
| 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-tools | f2e9e05 | CLAUDE.md "툴 7종" 표 파싱 → `inspect.signature` 대조(ctx 포함 실제 시그니처 출력, F-107a50), rc 0/1, `--claude-md` 옵션(테스트용 가짜 표 주입) |
| 테스트 | 설정값 해석(DB 없이) | tests/test_settings.py | P2-tools | f217190 | `app_user_id()` 기본값·환경변수 |
| 테스트 | 엔진 URL 조립·session_scope 계약(DB 없이 가능한 범위) | tests/test_db_session.py | P2-tools | f217190 | 4건 |
| 테스트 | 툴 반환 DTO·예외(DB 없이) | tests/test_tools_types.py | P2-tools | 4eca3e9 | `to_dict()` 직렬화, 예외 속성(`reason`/`code`) |
| 테스트 | trace 행 기록·예외 시 tool_error·문자열 절단 | tests/test_tools_context.py | P2-tools | 4eca3e9 | `step=tool_call`/`tool_error`, `tokens_in=tokens_out=0` |
| 테스트 | 후보 검색·D1 강제·D6 승진·별칭 누적·사실 upsert | tests/test_tools_persons.py | P2-tools | a9cb254 | |
| 테스트 | add_event/add_schedule 값 집합·raw_utterance 필수·타 사용자 차단 | tests/test_tools_records.py | P2-tools | 9cb35b6 | |
| 테스트 | ask_user 저장·`{question_id,status:"pending"}`·24h 만료·answer_question | tests/test_tools_questions.py | P2-tools | 8162e09 | |
| 테스트 | 브리핑 구성·briefed_at 기록 | tests/test_tools_briefing.py | P2-tools | 7c94aad | |
| 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-tools | 4d5817e | `TestClient` + `dependency_overrides[get_session]`(결정13) |
| 테스트 | CLAUDE.md 툴 표 ↔ 실제 시그니처(DB 없이) | tests/test_tool_signatures.py | P2-tools | f2e9e05 | 15건 — (a) 7툴 parametrize (b) 실제 파일 7행 파싱 (c) 부정 케이스(이름 변경/옵션 제거/6행/절 없음) (d) ctx 아닌 첫 인자 |
