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
| 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenAIEmbeddingProvider·코사인 행렬·D4 판정 | scripts/embed_pilot.py | P0-embed-pilot | pending | EmbeddingProvider 는 P2/P3 에서 백엔드 모듈로 이동 |
| 테스트 | 임베딩 파일럿 순수 로직(가짜 공급자, 네트워크 없음) | tests/test_embed_pilot.py | P0-embed-pilot | pending | pytest 10 passed |
| 리포트 | 임베딩 파일럿 결과(행렬 2종·선택 근거·N=1536) | reports/embed_pilot.md, reports/embed_pilot/*.json | P0-embed-pilot | pending | 실행 출력 evidence/20260903-embed-pilot-run.txt |
| 에이전트 | verifier — 계획 검증·완료 검토·코드 리뷰 전담(fable, 구현자와 다른 모델) | .claude/agents/verifier.md | 하네스 | pending | L-002 |
| 문서 | 교훈 L-002 역할별 모델 분리(계획 opus · 구현 sonnet · 검증 fable) | docs/wiki/lessons/L-002-role-model-separation.md | 하네스 | pending | verify-plan/impl 이 검증자=verifier 강제 |
| 문서 | 교훈 L-003 dev 푸시 뒤 사용자 결정까지 멈춤 | docs/wiki/lessons/L-003-stop-after-dev-push.md | 하네스 | pending | .awaiting-decision 마커 |
| 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마다 진행 상태 표 갱신. P0-compose: 로컬 DB 절 추가(2026-09-04), pg16 태그는 P9-infra 에서 재확인. P1-schema: 진행 표 P1 행·마이그레이션 절 추가(U5 커밋은 pending) |
| 훅 | 단계 위임 게이트(Agent 호출 전 사용자 승인 마커) | .claude/hooks/delegate-guard.sh | 하네스 | pending | L-004 |
| 문서 | 교훈 L-004 단계는 묻고 시작 | docs/wiki/lessons/L-004-ask-before-stage.md | 하네스 | pending | |
| 스크립트 | 로컬 pgvector compose(postgres 서비스, `${VAR:-기본값}` 4개, healthcheck) | docker-compose.yml | P0-compose | pending | pgvector/pgvector:pg16, P9-infra 에서 RDS 메이저 버전과 재확인 |
| 스크립트 | pgvector 확장 최초 기동 초기화 | docker/initdb/01-vector.sql | P0-compose | pending | CREATE EXTENSION IF NOT EXISTS vector |
| 스크립트 | DB 접속 검사(psycopg, `POSTGRES_*`↔`DATABASE_URL` 불일치 경고) | scripts/db_check.py | P0-compose | pending | 테스트 tests/test_db_check.py. P1-schema U1: 접속 조립을 app.config 로 이동·re-export; U5: SELECT version() 출력 추가 |
| 모듈 | 백엔드 패키지 골격(DB 접속 설정) | app/config.py | P1-schema | d7113e9 | `DATABASE_URL` 우선·없으면 `POSTGRES_*` 조립·`sqlalchemy_url()` — 접속 설정 단일 출처(`scripts/db_check.py`·`scripts/schema_check.py`·`alembic/env.py` 가 여기서 import). 앱·라우터는 P2-tools |
| 모듈 | SQLAlchemy Base + 명명 규칙 | app/db/base.py | P1-schema | d7113e9 | `DeclarativeBase` + `MetaData(naming_convention=...)`(pk/fk/ix/uq/ck) — 제약 이름이 alembic autogenerate·schema_check 기대값의 근거 |
| 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema | 4dfaf33 | `Person/PersonAlias/PersonFact/FactSource/Event/Schedule/PendingQuestion/PushSubscription/AgentTrace`. 값 집합 상수 `EVENT_TYPES`·`RELATION_TAGS`·`HIERARCHIES`·`QUESTION_KINDS`, CHECK 4·FK CASCADE 6·`fact_sources` 복합 PK·`person_aliases.embedding=Vector(1536)`·인덱스 10(부분 인덱스 1). `person_embeddings` 없음(D5 R9) |
| 마이그레이션 | Alembic 도입 + 초기 스키마 v2 | alembic/ (alembic.ini, alembic/env.py, script.py.mako, versions/0001_schema_v2.py) | P1-schema | 09c2bd1 | `env.py` 가 `app.config` 로 접속 주입 + `render_item` 훅으로 `pgvector.sqlalchemy.Vector` 렌더. `0001` upgrade 첫 줄 `CREATE EXTENSION IF NOT EXISTS vector`, downgrade 는 역순 drop(확장 미삭제). `alembic.ini` 의 `sqlalchemy.url` 공란 |
| 스크립트 | 스키마 v2 실물 검사(9테이블·CHECK 4·vector(1536)·FK CASCADE·인덱스·`person_embeddings` 부재, upgrade/downgrade 왕복용) | scripts/schema_check.py | P1-schema | 03e3ce3 | `--expect-empty` 옵션. 기대값은 `app.db.models`/`app.db.base` 에서 가져옴(중복 정의 없음). exit 0/1(FAIL)/2(접속 실패) |
| 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) | requirements.txt, requirements-dev.txt | P1-schema | d7113e9 | SQLAlchemy 2.0.50 / alembic 1.19.2 / psycopg[binary] 3.3.5 / pgvector 0.5.0 / (dev) pytest 9.0.3 |
| 테스트 | 접속 설정 해석(DB 없이) | tests/test_config.py | P1-schema | d7113e9 | 5건 — `DATABASE_URL` 우선순위, 부분 지정 시 기본값, 비밀번호 미노출 |
| 테스트 | 스키마 v2 모델 메타데이터(DB 없이) | tests/test_schema_models.py | P1-schema | 4dfaf33 | 17건 — 테이블 9개·`person_embeddings` 부재, CHECK 4종 값 전수, FK 6개 `ondelete=CASCADE`, `fact_sources` 복합 PK, `embedding` 차원 1536, 인덱스 이름 |
| 테스트 | 스키마 검사 스크립트 순수 로직(DB 없이) | tests/test_schema_check.py | P1-schema | 03e3ce3 | 11건 — 기대 테이블/값 집합이 `app.db.models`·`Base.metadata` 와 동일 객체, `compute_exit_code`, `--expect-empty` 파싱, 출력 포맷 |
| 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftest.py | P1-schema | d7113e9 | `app` 패키지 임포트를 위한 `sys.path.insert` — `tests/test_db_check.py` 기존 방식은 그대로 유지 |
