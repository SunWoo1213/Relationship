# P2-tools · 계획 (01-plan)

상태: 승인(2026-09-05, 개정 1, verifier 통과 FAIL 0/WARN 6) | 담당: architect(계획) / backend-agent(구현) / verifier(검증) — 승인·커밋은 메인 세션 | 작성: 2026-09-05
태그 — 패키지: P2-tools · 닫는 검증: R6 R7 R10 R18 · 기대는 결정: D1 D2 D6 (참조 D4 D5 D9) · 구현하는 명세: S3.2 S3.4 (경계 확인용 S3.1 S3.3 S3.5 S3.6) · 관련 원칙: 원칙1 원칙2 원칙4 원칙6 원칙7 원칙9
의존: P1-schema (완료 — 5dc95bb, 04-review 결과 완료. 9테이블·CHECK 4·`vector(1536)`·FK CASCADE 6), P0-compose (완료 — 819e1ac, 로컬 pgvector 컨테이너 호스트 5433). `docs/backlog.md` P2 행의 의존 문구는 "P1 스키마"이며 충족. P4 게이트 해당 없음(P2 는 P4 이전 패키지 — P4 게이트는 P5 이후에만 적용).

## 목표
`docs/resolution-plan.md` §5 구현 순서 표의 "P2 | 툴 7종 v2 구현 + 단위 테스트 | backend-agent | P1 | 시그니처 일치, ask_user가 pending_questions에 저장" 한 줄을 실현한다. 기획서 4장의 "제품 속 에이전트가 호출하는 도구 집합"을, P1 이 만든 스키마 v2 위에서 **DB 를 읽고 쓰는 순수 파이썬 함수 7개**로 구현하고, 그 위에 P1 04-review §7 이 넘긴 **FastAPI 골격**(앱 팩토리·요청 단위 세션 의존성·`GET /health`·`POST /answers/{question_id}` 답 저장)을 얇게 얹는다(결정 1 — 사용자 결정). 이 패키지가 닫는 검증은 R10(툴 시그니처 ↔ 스키마 불일치 → S3.2 v2 시그니처를 코드가 그대로 갖는다), R6(신규 인물 자동등록 vs 확인형 → `create_person` 이 answered `new_person` 질문 없이는 실패한다, D1), R7(ask_user 동기 반환 불가 → 질문을 `pending_questions` 에 저장하고 `{question_id, status:"pending"}` 을 돌려준 뒤 턴을 끝낸다, D2), R18(승진 후 `display_name` 정책 → 별칭 누적 + 표시 이름 갱신, D6)이다. 이 패키지가 끝나면 P3-er 은 "후보를 어떻게 가져오는가"를 다시 만들 필요 없이 `search_person` 이 돌려주는 `Candidate[]` 위에서 4단계 판정만 얹으면 된다.

## 범위

- 포함:
  - **툴 7종 (S3.2 시그니처 그대로)** — `app/tools/` 패키지의 모듈 함수. 각 함수는 첫 매개변수로 실행 맥락 `ctx: ToolContext`(세션·session_id·user_id·임베딩 공급자·현재 시각)를 받고, **그다음 매개변수는 CLAUDE.md "툴 7종" 표와 이름·순서·옵션 여부가 글자 그대로 같다**(결정 2).
    - `search_person(ctx, query, hints=None) -> list[Candidate]`
    - `create_person(ctx, display_name, aliases, relation_tag, hierarchy) -> PersonOut`
    - `update_person(ctx, person_id, facts=None, new_alias=None, display_name=None) -> PersonOut`
    - `add_event(ctx, person_id, type, content, occurred_at, raw_utterance) -> EventOut`
    - `add_schedule(ctx, person_id, title, scheduled_at) -> ScheduleOut`
    - `get_briefing(ctx, person_id, schedule_id=None) -> BriefingOut`
    - `ask_user(ctx, kind, question, options, context) -> PendingQuestionOut`
  - **툴 밖 보조 함수 2개**(툴 7종에 포함되지 않으며 LLM 에 노출하지 않는다): `answer_question(ctx, question_id, answer)`(답을 `pending_questions.answer`·`answered_at` 에 저장. 답 문자열이 저장된 `options` 안에 있어야 하고, 이미 답했거나 24h 만료된 질문은 거절한다), `question_status(question, now)`(`answered` / `expired` / `pending` 파생 — F-081752, S3.4).
  - **엔진·세션 `app/db/session.py`**: `get_engine()`(`app.config.sqlalchemy_url()` 로 1회 생성, 모듈 캐시), `SessionLocal = sessionmaker(bind=…, expire_on_commit=False)`, `session_scope()` 컨텍스트 매니저(정상 종료 시 commit, 예외 시 rollback). P1 04-review §7 이 "엔진·sessionmaker·요청 단위 세션은 P2 가 만든다"고 넘긴 부분이다.
  - **F-8eeb9b 처리(P1 04-review §6 권고, 첫 단위)**: `app/config.py` 의 `ConnInfo.password` 를 `field(repr=False)` 로 바꾸고 `repr(conn)`·`str(conn)` 에 비밀번호가 없음을 검사하는 테스트 1건을 기존 `tests/test_config.py` 에 추가한다. 엔진·예외 메시지가 생기기 **전에** 처리한다.
  - **실행 맥락 `ToolContext`**(`app/tools/context.py`): `session`, `session_id`, `user_id`, `embedder: EmbeddingProvider | None = None`, `now: Callable[[], datetime]`(기본 `lambda: datetime.now(timezone.utc)`), `confirmed_question_id: int | None = None`. 툴은 이 객체 밖의 전역 상태를 읽지 않는다.
  - **`agent_traces` 기록(원칙9)**: `app/tools/context.py` 의 `@traced("<tool_name>")` 데코레이터 하나로 일원화. 7개 툴 + `answer_question` 에 붙는다. 저장 값 — `session_id = ctx.session_id`, `step = "tool_call"`, `tool_name = 툴 이름`, `input = {ctx 를 뺀 인자의 JSON 표현}`, `output = {반환 dict}`, `tokens_in = tokens_out = 0`(P2 에는 LLM 호출이 없다). 예외가 나면 `step = "tool_error"`, `output = {"error": 예외 클래스명, "message": str(e)}` 를 남기고 예외를 다시 올린다.
  - **`search_person` 의 후보 검색**(결정 3): 별칭 정확 일치 → 부분 일치(`ILIKE`) → 임베딩 유사도(`person_aliases.embedding` top-K, K=10, 인물별 max) 를 합쳐 인물 단위 `Candidate` 로 집계한다. `Candidate = {person, similarity, aliases_matched, rule_flags}`(S3.2 15행 그대로). `hints`(`hierarchy` / `relation_tag`)는 **후보를 배제하지 않고 `rule_flags` 만 채운다**(배제·완화 재검색은 P3-er 의 2단계).
  - **임베딩 인터페이스 `app/embedding.py`**: `EmbeddingProvider` Protocol(`name`, `dimension`, `embed(texts) -> list[list[float]]`) 만 정의한다(D4 "임베딩 호출은 반드시 인터페이스 뒤에"). 별칭이 만들어질 때 `ctx.embedder` 가 있으면 그 자리에서 `person_aliases.embedding` 을 채우고(D5 "새 별칭이 확정되면 즉시 임베딩"), 없으면 NULL 로 둔다. 테스트는 결정적 가짜 공급자(해시 기반 1536차원)를 주입한다.
  - **값 집합 검증**: `type ∈ EVENT_TYPES`, `relation_tag ∈ RELATION_TAGS`, `hierarchy ∈ HIERARCHIES`, `kind ∈ QUESTION_KINDS` 를 `app.db.models` 에서 import 해 툴 진입점에서 검사하고 위반 시 `InvalidValue` 를 올린다(DB CHECK 에 닿기 전에 사람이 읽을 수 있는 오류로). 상수를 재정의하지 않는다(P1 04-review §7).
  - **별칭 출처 값 집합 `ALIAS_SOURCES`**(결정 5): `("user_said", "confirmed", "system")` 를 `app/db/models.py` 에 상수로 추가한다(컬럼·CHECK 변경 없음 → 마이그레이션 없음).
  - **`user_id` 격리(security.md §5)**: 모든 인물 조회에 `persons.user_id = ctx.user_id` 조건. `person_id` 를 인자로 받는 툴도 먼저 이 조건으로 인물을 조회하고 없으면 `PersonNotFound` — 다른 사용자 행에 이벤트·일정·사실이 붙지 않는다.
  - **설정값 모듈 `app/settings.py`**: `app_user_id(env)`(`APP_USER_ID`, 기본 `"local"`), `QUESTION_TTL_HOURS = 24`(S3.4), `SEARCH_TOP_K = 10`(D5/S3.3), `BRIEFING_RECENT_EVENTS = 5`, `BRIEFING_UPCOMING_SCHEDULES = 3`, `DEFAULT_FACT_CONFIDENCE = 1.0`, `TRACE_MAX_STRING = 4000`.
  - **FastAPI 골격 (결정 1 — 사용자 결정 2026-09-05)**: P1 04-review §7 이 "FastAPI 앱은 P2-tools 가 만든다"고 넘긴 부분을 이 패키지에서 받는다. 범위는 **앱 팩토리 + 요청 단위 세션 의존성 + 엔드포인트 2개**로 한정한다.
    - `app/main.py` — `create_app() -> FastAPI` 팩토리와 모듈 수준 `app = create_app()`. 라우터 등록과 도메인 예외 → HTTP 상태 매핑(예외 핸들러)을 이 한 곳에서 한다(결정 11).
    - `app/api/deps.py` 의 `get_session()` — 요청 단위 세션 의존성. `app/db/session.py` 의 `SessionLocal` 로 세션을 만들어 `yield` 하고, 정상 종료 시 commit·예외 시 rollback·항상 close(= `session_scope()` 와 같은 규약을 FastAPI 의존성 형태로). **툴 함수는 여전히 commit 하지 않는다**(결정 2 — 트랜잭션 경계는 호출자).
    - `GET /health` — 세션으로 `SELECT 1` 과 `SELECT version_num FROM alembic_version` 을 실행해 `{"status":"ok","db":"up","alembic":"<rev>"}` 를 돌려준다. 접속 실패 시 503 `{"status":"degraded","db":"down"}` — **접속 문자열·비밀번호·예외 원문을 본문에 넣지 않는다**(security.md §1).
    - `POST /answers/{question_id}` — S3.4 턴 N+1 의 **답 저장까지만**. 본문 `{"answer": "<선택지 문자열>"}`(pydantic 모델 `AnswerIn`, `app/api/schemas.py`), 처리 = `answer_question(ctx, question_id, answer)` 호출, 응답 `{"question_id": <id>, "status": "answered"}`. **저장된 context 로 루프를 재개하거나 후속 툴을 호출하지 않는다** — 그 화살표는 P5-loop 이 이 엔드포인트를 확장해서 잇는다.
    - `ToolContext` 는 요청마다 만든다. `session` = 의존성이 준 세션, `session_id` = **답할 `pending_questions` 행의 `session_id`**(결정 12), `user_id` = `settings.app_user_id()`, `embedder = None`(P2 는 답 저장에서 별칭을 만들지 않는다), `now` 기본값.
  - **테스트**(결정 8): 실 PostgreSQL(로컬 5433) + 트랜잭션 롤백 픽스처. `tests/conftest.py` 에 `db_engine`(세션 스코프, 접속 실패 시 `pytest.skip`), `db_session`(함수 스코프 — 바깥 트랜잭션 열고 끝나면 rollback), `fake_embedder`, `tool_ctx` 픽스처와 `pytest_configure` 의 `dbtest` 마커 등록을 추가한다. DB 없이 도는 테스트(설정·시그니처·JSON 직렬화)는 마커 없이 항상 돈다. HTTP 테스트(`tests/test_api.py`)는 **같은 롤백 픽스처를 `app.dependency_overrides[get_session]` 로 주입**해 재사용한다(결정 13).
  - **의존성 3개 추가**(첫 단위 U1): `fastapi`, `uvicorn[standard]`, `httpx`(Starlette `TestClient` 의 필수 의존성). `requirements.txt` 에 설치본 버전으로 핀 고정하고 `pip freeze` 출력을 evidence 로 남긴다. `pydantic` v2 는 `fastapi` 가 끌어오므로 직접 적지 않는다(결정 10). `anthropic`·`openai` 는 여전히 추가하지 않는다.
  - **수용 기준 기계 검증 `scripts/tools_check.py`**: `CLAUDE.md` 의 "툴 7종" 표를 파싱해 기대 시그니처를 만들고 `inspect.signature` 로 실제 함수와 대조(이름·순서·옵션 여부), 어긋나면 종료 코드 1. `tests/test_tool_signatures.py` 는 같은 파서를 import 해 회귀로 돈다(파서 이중 정의 금지 — `scripts/schema_check.py` 와 같은 방식).
  - **문서 반영**: `docs/wiki/registry.md` 신규 행(session·settings·embedding·tools 6모듈·`app/main.py`·`app/api` 3모듈·tools_check·테스트) + 기존 행 **비고만** 갱신(`app/config.py`, `app/db/models.py`, `tests/conftest.py`, `requirements.txt`(43행 — fastapi/uvicorn/httpx 추가), `README.md`, `scripts/embed_pilot.py`), `README.md` 진행 상태 표 P2 행과 **로컬 API 실행 절**(uvicorn·`curl /health`).
- 이 패키지에서 하지 않는 것:
  - **LLM 호출·프롬프트·구조화 출력** 일체. `anthropic` 의존성을 추가하지 않는다. `tokens_in/out` 이 0 인 이유가 이것이다.
  - **에이전트 루프·툴 라우팅·채팅 엔드포인트**(`POST /messages`, 발화 → 툴 선택 → 저장 → 응답, `POST /answers/{question_id}` 의 **재개 흐름** — 저장된 context 로 루프를 다시 도는 부분) — 전부 **P5-loop**(결정 1). P2 가 만드는 HTTP 표면은 `GET /health` 와 `POST /answers/{question_id}` 의 **답 저장**뿐이다.
  - **인물 카드·브리핑 조회 API**(`GET /persons/{id}`, `GET /briefings/...`, `POST /briefings/run`) — P6-briefing·P8-frontend. 인증·세션 관리·CORS 설정도 이 패키지에서 하지 않는다(로컬 단일 사용자, 결정 9).
  - **ER 4단계·확신도·임계치**(`s_llm`·`s_emb`·`s_rule`·`confidence`·`T_merge`·`T_new`·후보 배제·승진 완화 재검색·`confidence_breakdown` trace) — **P3-er**(S3.3). P2 는 판정하지 않고 후보만 모은다.
  - **OpenAI 임베딩 실제 호출**(`OpenAIEmbeddingProvider` 를 `app/` 으로 옮기는 일, `openai` 의존성 추가, 기존 별칭 백필) — **P3-er**(결정 4). `scripts/embed_pilot.py` 는 손대지 않는다(P0 증거 재현성).
  - **벡터 인덱스(HNSW/IVFFlat) 생성**과 그 마이그레이션 — P3-er(P1 01-plan 결정 5 그대로).
  - **3계층 메모리 승격·반복 패턴 감지(`pattern:{type}`)·`fact_sources` 채우기** — **P6-memory**(S3.5, D9, 원칙6). `add_event` 는 승격·패턴을 트리거하지 않는다.
  - **브리핑 문장화·"한 줄 행동 제안"·주기 작업(1분)·`POST /briefings/run`** — **P6-briefing**(S3.6). `get_briefing` 은 구조화된 자료만 돌려준다(결정 7). 감정·고민 대화는 범위 밖(원칙7).
  - **웹푸시·VAPID·`push_subscriptions` 쓰기** — P7-push.
  - **프론트·확인 칩 렌더링** — P8-frontend.
  - **스키마 변경**: 새 테이블·컬럼·CHECK·인덱스를 만들지 않는다. 새 Alembic revision 을 만들지 않는 것이 목표이며, `alembic check` 가 "변경 없음"인 것을 마지막 단위 증거로 남긴다.
  - **인물–인물(A–B) 관계**, `person_embeddings`, `users` 테이블, `pending_questions.status` 컬럼 — 원칙7·D5·D8·S3.1 그대로 만들지 않는다.
  - **`delete_person` / `DELETE /persons/{id}`** — 툴 7종 밖이고 사각지대 정리 정책이 아직 없다(미결 8).
  - 시드·데모 데이터 삽입(테스트 픽스처 안에서 만드는 행은 제외), 인프라·CI.

## 산출물 (파일 경로)
- app/settings.py — 런타임 설정값(APP_USER_ID·24h·top-K·브리핑 N·기본 confidence·trace 길이 제한)
- app/db/session.py — engine 생성(`app.config.sqlalchemy_url()`)·`SessionLocal`·`session_scope()`
- app/embedding.py — `EmbeddingProvider` Protocol (구현체 없음)
- app/tools/__init__.py — 툴 7종 재export, `TOOL_NAMES`
- app/tools/types.py — `Candidate`·`PersonOut`·`EventOut`·`ScheduleOut`·`BriefingOut`·`PendingQuestionOut`·예외 계층
- app/tools/context.py — `ToolContext`, `@traced` 데코레이터(agent_traces 기록·JSON 변환·문자열 절단)
- app/tools/persons.py — `search_person`·`create_person`·`update_person`(+별칭 추가·사실 upsert 보조)
- app/tools/records.py — `add_event`·`add_schedule`
- app/tools/questions.py — `ask_user`·`answer_question`·`question_status`
- app/tools/briefing.py — `get_briefing`
- app/main.py — `create_app()` 팩토리·라우터 등록·도메인 예외 → HTTP 매핑 핸들러·`app`
- app/api/__init__.py — 라우터 재export (라우터를 나눈다 — 결정 11)
- app/api/deps.py — `get_session()` 요청 단위 세션 의존성, 요청별 `ToolContext` 조립 보조
- app/api/routes.py — `GET /health`, `POST /answers/{question_id}` (P5 가 채팅·재개를 여기에 얹는다)
- app/api/schemas.py — `AnswerIn`(요청 본문)·`AnswerOut`·`HealthOut` pydantic 모델
- requirements.txt — `fastapi`·`uvicorn[standard]`·`httpx` 핀 추가(기존 파일)
- app/db/models.py — `ALIAS_SOURCES` 상수 추가(컬럼·제약 변경 없음, 기존 파일)
- app/config.py — `ConnInfo.password` 를 `field(repr=False)` 로(F-8eeb9b, 기존 파일)
- scripts/tools_check.py — CLAUDE.md 표 파싱 → `inspect.signature` 대조 (rc 0/1)
- tests/conftest.py — `db_engine`·`db_session`·`fake_embedder`·`tool_ctx` 픽스처, `dbtest` 마커 등록(기존 파일)
- tests/test_config.py — `repr(ConnInfo)` 비밀번호 미포함 1건 추가(기존 파일)
- tests/test_settings.py — 설정값 해석(DB 없이)
- tests/test_db_session.py — 엔진 URL 조립·`session_scope` 계약(DB 없이 가능한 범위)
- tests/test_tools_context.py — trace 행 기록·예외 시 `tool_error`·문자열 절단
- tests/test_tools_persons.py — 후보 검색·D1 강제·D6 승진·별칭 누적·사실 upsert
- tests/test_tools_records.py — `add_event`/`add_schedule` 값 집합·`raw_utterance` 필수·타 사용자 차단
- tests/test_tools_questions.py — `ask_user` 저장·`{question_id, status:"pending"}`·24h 만료 파생·`answer_question`
- tests/test_tools_briefing.py — 브리핑 구성·`briefed_at` 기록
- tests/test_tool_signatures.py — CLAUDE.md 표 ↔ 실제 시그니처(DB 없이)
- tests/test_api.py — `TestClient`: `GET /health` 200·`POST /answers` 정상 저장·없는 id 404·이미 답한 질문 409·옵션 밖 답 422
- docs/wiki/packages/P2-tools/evidence/ — pytest(`-rs`)·tools_check·alembic check·DB 행 확인 출력
- docs/wiki/registry.md — 신규 행 + 기존 행 비고 갱신(새 행 금지)
- README.md — 진행 상태 표 P2 행

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)
- [x] U1 기반: `requirements.txt` 에 `fastapi`·`uvicorn[standard]`·`httpx` 를 설치본 버전으로 핀 고정하고 `pip install -r requirements.txt` + `pip freeze` 출력을 evidence 로(결정 10), `app/config.py` 의 `password` 를 `field(repr=False)` 로 고치고 `tests/test_config.py` 에 `repr` 검사 1건 추가(F-8eeb9b), `app/db/session.py`(engine·`SessionLocal`·`session_scope`), `app/settings.py`, `tests/conftest.py` 에 `db_engine`·`db_session`·`fake_embedder` 픽스처와 `dbtest` 마커 등록, `tests/test_settings.py`·`tests/test_db_session.py`. 로컬 5433 에 붙어 픽스처가 롤백으로 깨끗한지 확인한 출력을 evidence 로 / Refs: P2-tools R6 R7 R10 R18 D1 D2 D6 S3.2 S3.4
- [x] U2 툴 공통: `app/tools/types.py`(Candidate·*Out·예외), `app/tools/context.py`(`ToolContext`·`@traced`·JSON 변환·`TRACE_MAX_STRING` 절단), `tests/test_tools_context.py`(성공 시 `step="tool_call"` 행 1개, 예외 시 `tool_error` 행 + 예외 재발생, 긴 문자열 절단, `tokens_in/out = 0`) / Refs: P2-tools R10 S3.2 원칙9
- [ ] U3 `search_person`: `app/embedding.py`(Protocol), `app/tools/persons.py` 의 후보 검색 — 별칭 정확·부분 일치, `ctx.embedder` 가 있을 때 `cosine_distance` top-K(K=10) → 인물별 max, `hints` 로 `rule_flags` 채우기, 결정적 정렬. `tests/test_tools_persons.py` 후보 검색 부분(가짜 임베딩 주입, embedder 없을 때 `embedding_skipped`) / Refs: P2-tools R10 D4 D5 S3.2 S3.3
- [ ] U4 `create_person`·`update_person`: D1 강제(`ctx.confirmed_question_id` 가 answered `new_person` 질문이 아니면 `ConfirmationRequired` — 직접 호출 테스트가 실패해야 한다), D6(별칭 누적·삭제 금지, `display_name` 갱신도 answered 질문 필요), `ALIAS_SOURCES` 추가, 별칭 생성 시 임베딩 채우기, `person_facts` 애플리케이션 upsert. 해당 테스트 / Refs: P2-tools R6 R18 D1 D5 D6 S3.2
- [ ] U5 `add_event`·`add_schedule`: `app/tools/records.py` — `type ∈ EVENT_TYPES` 검사, `raw_utterance` 필수 인자, aware UTC 시각 요구, `user_id` 소유 확인. `tests/test_tools_records.py` / Refs: P2-tools R10 S3.1 S3.2
- [ ] U6 `ask_user`·`answer_question`: `app/tools/questions.py` — `pending_questions` 저장 후 `{question_id, status:"pending"}` 반환(동기 대기·폴링 없음), `question_status` 파생(answered / 24h expired / pending), `answer_question` 이 `answer`·`answered_at` 기록·이미 답한 질문 재답변 거부(`QuestionNotAnswerable`)·만료 질문 거부·저장된 `options` 밖의 답 거부(`InvalidValue`). `tests/test_tools_questions.py`(수용 기준 후반부의 직접 증거 — 행 존재 조회) / Refs: P2-tools R7 D1 D2 S3.4
- [ ] U7 `get_briefing`: `app/tools/briefing.py` — 인물·별칭·`person_facts` 전부·최근 events N건·다가오는 schedules, `schedule_id` 가 주어지면 그 일정에 `briefed_at = now()` 기록. 문장화·제안 없음. `tests/test_tools_briefing.py` / Refs: P2-tools R10 S3.2 S3.6 원칙7
- [ ] U8 FastAPI 골격: `app/main.py`(`create_app()`·예외 핸들러 매핑 — `PersonNotFound`/없는 question_id → 404, `QuestionNotAnswerable` → 409, `InvalidValue` → 422, 본문에 접속 정보·예외 원문 금지), `app/api/deps.py`(`get_session()` 요청 단위 세션·요청별 `ToolContext` 조립), `app/api/routes.py`(`GET /health`, `POST /answers/{question_id}` — `answer_question` 호출까지, 루프 재개 없음), `app/api/schemas.py`(`AnswerIn`·`AnswerOut`·`HealthOut`), `tests/test_api.py`(`TestClient` + `dependency_overrides` 로 U1 롤백 픽스처 재사용: `/health` 200·`db":"up"`·`alembic` 리비전, 정상 답 저장 후 DB 행에 `answer`·`answered_at`, 없는 id 404, 이미 답한 질문 409, 옵션 밖 답 422, 응답 본문에 비밀 문자열 0회). 툴 함수가 모두 자리 잡은 뒤 그 위에 얇은 HTTP 표면만 얹으므로 U7 뒤에 둔다 / Refs: P2-tools R7 D2 S3.4
- [ ] U9 수용 기준 기계 검증 + 문서: `scripts/tools_check.py`(CLAUDE.md 표 파싱 → `inspect.signature` 대조, rc 0/1)와 `tests/test_tool_signatures.py`, 전체 `pytest -q -rs` · `tools_check` · `alembic check`(스키마 무변경 증거) · `uvicorn` 기동 후 `curl /health` 출력을 evidence 로, `docs/wiki/registry.md` 신규 행 + 기존 행 비고 갱신, `README.md` 진행 표 P2 행과 **실행 절**(`python -m uvicorn app.main:app --reload` / 로컬 DB 포트를 셸 변수로 넘기는 예 `POSTGRES_PORT=5433 python -m uvicorn app.main:app --reload` / `curl http://localhost:8000/health` 기대 출력) / Refs: P2-tools R6 R7 R10 R18 D1 D2 D6 S3.2 S3.4

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)
- 시그니처가 CLAUDE.md와 일치, `ask_user`가 `pending_questions`에 저장

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령 — verify-plan 4번은 위 절의 불릿만 backlog 와 대조하므로 별도 절로 둔다)

로컬 컨테이너는 5433 이므로 포트를 셸 변수로 넘긴다(`.env` 는 읽지 않는다, security.md §1).

| 무엇 | 명령 | 기대 출력 |
|------|------|-----------|
| **시그니처가 CLAUDE.md와 일치** | `python scripts/tools_check.py` | 툴 7종 각 행에 `[ok] search_person(query, hints=None)` 형태로 CLAUDE.md 기대값과 실제 `inspect.signature` 가 함께 찍히고 불일치 0, 종료 코드 0 |
| 같은 검사의 회귀 | `python -m pytest tests/test_tool_signatures.py -q` | 7개 툴 각각 1건 통과(DB 불필요) |
| **`ask_user`가 `pending_questions`에 저장** | `POSTGRES_PORT=5433 python -m pytest tests/test_tools_questions.py -q -rs` | `ask_user` 호출 후 같은 트랜잭션에서 `SELECT id, kind, question, options, context FROM pending_questions WHERE id = :id` 가 1행, 반환값이 `{"question_id": <id>, "status": "pending"}`, `answered_at IS NULL` |
| 같은 항목의 skip 여부 확인 | 위 명령의 `-rs` 요약 줄 | `dbtest` 가 skip 되지 않았음(“1 skipped” 이 아니라 실행됨)을 evidence 에 남긴다 |
| trace 기록(원칙9) | `pytest tests/test_tools_context.py tests/test_tools_persons.py -q` | 툴 호출마다 `agent_traces` 1행, `tool_name` = 툴 이름, `tokens_in=tokens_out=0` |
| D1 강제(R6) | `pytest tests/test_tools_persons.py -k confirm -q` | 확인 없는 `create_person` 이 `ConfirmationRequired` 로 실패 |
| 같은 항목의 HTTP 경로 | `POSTGRES_PORT=5433 python -m pytest tests/test_api.py -q -rs` | `POST /answers/{id}` 200 + DB 행에 `answer`·`answered_at` 기록, 없는 id 404, 이미 답한 질문 409, 옵션 밖 답 422 |
| FastAPI 골격이 실제로 뜬다 | `POSTGRES_PORT=5433 python -m uvicorn app.main:app --port 8000` 후 `curl -s -o - -w "%{http_code}" http://localhost:8000/health` | `200` 과 `{"status":"ok","db":"up","alembic":"<rev>"}`. `<rev>` 가 `alembic current` 와 같고 본문에 비밀번호·호스트 문자열이 없다 |
| 스키마 무변경 | `POSTGRES_PORT=5433 python -m alembic check` | `No new upgrade operations detected.` 종료 코드 0 |
| 전체 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 기존 49건 + 신규 전부 통과, 실패 0 |

- 증거 경로: `docs/wiki/packages/P2-tools/evidence/`. Docker Desktop 이 꺼져 있으면 우회하지 않고 사용자에게 실행을 요청하고 멈춘다(security.md §6).

## 리스크 · 미결

- **결정 1 — 범위선: P2 = 툴 함수 7종 + 세션/엔진 + FastAPI 골격(health, answers) / P5 = 루프·채팅 엔드포인트·재개 흐름.** (사용자 결정 2026-09-05, journal DECISION 기록. 초안의 "HTTP 는 전부 P5" 를 개정한 것이다.) 근거: P1-schema 04-review §7 인계 "엔진·sessionmaker·요청 단위 세션·**FastAPI 앱은 P2 가 만든다**" 를 그대로 존중한다 — 앱 팩토리가 없으면 `get_session` 의존성의 형태를 정할 자리가 없고, 세션 경계 결정(결정 2 "툴은 commit 하지 않는다")이 실제 요청에서 검증되지 않은 채 P5 로 넘어간다. 경계는 **동작**으로 긋는다:
  - **P2 가 만든다**: 앱 팩토리, 요청 단위 세션 의존성, `GET /health`(DB 접속 확인), `POST /answers/{question_id}` 의 **답 저장**(= `answer_question` 호출 → `{question_id, status}` 반환). S3.4 다이어그램의 턴 N("pending_questions 저장" — U6)과 턴 N+1 의 **앞 절반**("칩 선택 → POST /answers/{question_id}")까지다.
  - **P5 가 만든다**: 턴 N+1 의 **뒤 절반**("저장된 context 로 루프 재개 → 후속 툴"), `POST /messages` 채팅 엔드포인트, 툴 라우팅, LLM 호출.
  - **backlog 와의 관계**: backlog P5 수용 기준 "발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개" 는 그대로 유효하다 — **P5 는 P2 가 만든 `POST /answers/{question_id}` 를 "재개까지" 확장한다**(새로 만드는 것이 아니라 저장 뒤에 루프 호출을 잇는다). backlog P2 수용 기준 문장은 손대지 않으므로 verify-plan 4번 대조에는 영향이 없고, 골격은 수용 기준을 넘는 부분이 아니라 그것을 실행 가능한 형태로 감싸는 최소 표면이다.
  - 03-log·04-review 에 이 경계를 다시 적고 P5-loop 01-plan 이 "확장" 으로 이어받는다. 기획서 변경이 아니라 패키지 경계 확정이므로 CR 은 열지 않는다.
- **결정 2 — 시그니처는 `ctx` 한 개만 앞에 붙인다.** 수용 기준이 "시그니처가 CLAUDE.md와 일치"이므로 세션·user_id·session_id·임베딩 공급자를 개별 인자로 흩뿌리지 않는다. 대안이던 "`session` 을 첫 인자로"는 session 외에 user_id·session_id·embedder 도 필요해 결국 인자가 4개 붙는다. `ToolContext` 하나로 묶고, `scripts/tools_check.py` 가 **첫 매개변수가 정확히 `ctx` 이고 그 뒤가 CLAUDE.md 표와 이름·순서·옵션까지 같은지**를 검사한다(허용되는 유일한 편차를 기계가 강제한다). 컨텍스트 매니저는 툴 안에 두지 않는다 — **툴은 commit 하지 않고 `flush()` 까지만 하며**, 트랜잭션 경계는 호출자(`session_scope()`, 나중에는 P5 의 요청 경계)가 잡는다. 그래야 롤백 픽스처로 테스트가 서로 오염되지 않는다.
- **결정 3 — `search_person` 은 배제하지 않고 신호만 모은다.** 반환은 인물 단위 `Candidate{person, similarity, aliases_matched, rule_flags}`. `similarity` = 임베딩 코사인 유사도의 인물별 max(0~1), `aliases_matched` = 문자열로 맞은 별칭 목록, `rule_flags` = `{exact_alias, partial_alias, hierarchy_match, relation_tag_match, hierarchy_adjacent, embedding_skipped}`. `hierarchy_adjacent` 를 미리 넣는 이유는 P3-er 의 승진 완화 재검색(S3.3)이 이 신호를 필요로 하기 때문이다. `s_emb`·`s_rule`·`s_llm`·임계치 분기는 전부 P3(원칙2·4 — P2 는 판정 주체가 아니다).
- **결정 4 — 임베딩은 "인터페이스만 P2, 실제 공급자는 P3".** `app/embedding.py` 에 Protocol 만 두고 `OpenAIEmbeddingProvider` 는 옮기지 않는다. 이유: (a) P2 단위 테스트가 네트워크·`OPENAI_API_KEY` 에 묶이면 재현성이 깨진다(원칙8); (b) `openai` 를 `requirements.txt` 에 넣으면 런타임 호출자가 없는 의존성이 생긴다; (c) `scripts/embed_pilot.py` 를 지금 건드리면 P0-embed-pilot 의 실행 증거 재현 경로가 흔들린다. 대신 **쓰기 경로는 P2 에 있다** — `ctx.embedder` 가 주입되면 별칭을 만들 때 그 자리에서 임베딩을 채우므로(D5), P3 는 `OpenAIEmbeddingProvider` 를 `app/embedding.py` 로 옮겨 ctx 에 꽂기만 하면 된다. registry 26행 비고의 "P2/P3 에서 이동"을 U8 에서 "P3-er 에서 이동"으로 좁힌다. **남는 일**: P2 를 embedder 없이 돌린 구간에 생긴 `embedding IS NULL` 별칭의 백필 — P3-er 몫으로 기록.
- **결정 5 — `person_aliases.source` 값 집합 = `user_said` / `confirmed` / `system`.** `user_said`(발화에서 그대로 뽑은 미확정 호칭), `confirmed`(사용자가 답한 질문을 거쳐 확정 — `confirmed_at` 을 함께 채운다), `system`(시스템 생성, 예: `create_person` 의 `display_name` 자동 별칭). `ALIAS_SOURCES` 는 `app/db/models.py` 에 둔다(값 집합 상수의 단일 출처가 이미 그 모듈 — P1 04-review §7). **DB CHECK 는 추가하지 않는다**: 새 revision 을 만들지 않는 것이 이 패키지 목표이고, 값 집합이 P3(별칭 확정 경로)·P6(승격)에서 흔들릴 가능성이 남아 있다. 강제는 애플리케이션 검증으로 하고, 굳어지면 P3-er 의 벡터 인덱스 revision 에 CHECK 를 함께 얹는다. S3.1 카드에는 이 값 집합 한 줄을 U8 에서 추가한다(카드 갱신이지 기획서 변경이 아니므로 CR 아님).
- **결정 6 — `person_facts` 는 `(person_id, key)` 애플리케이션 upsert.** `UNIQUE` 가 없으므로(P1 미결) 조회 후 있으면 `value`·`updated_at` 갱신, 없으면 삽입. 이유: 같은 key 가 여러 행이면 인물 카드·브리핑이 서로 모순되는 값을 동시에 보여준다. `update_person(facts=[{key,value}])` 에는 confidence 인자가 없으므로 사용자 발화에서 직접 온 사실은 `DEFAULT_FACT_CONFIDENCE = 1.0`. 한계: UNIQUE 가 없어 동시 호출 시 중복 행이 생길 수 있다 — 단일 사용자·단일 워커라 수용하고, 읽을 때는 `updated_at DESC` 첫 행을 쓴다. 승격(P6-memory)이 누적/갱신 중 무엇을 택할지는 그 패키지 결정이며, 그때 UNIQUE 를 걸지도 함께 정한다.
- **결정 7 — `get_briefing` 은 자료까지.** 반환 `BriefingOut = {person, aliases, facts[], recent_events[N=5], upcoming_schedules[3], schedule?, generated_at}`. `schedule_id` 가 주어졌을 때만 그 일정에 `briefed_at = ctx.now()` 를 기록한다(어느 일정의 브리핑인지 모르는 채로 표시를 남기지 않는다 — S3.2 "`briefed_at` 기록"의 최소 해석). LLM 문장화·"한 줄 행동 제안"·주기 작업·`POST /briefings/run` 은 P6-briefing, 푸시는 P7-push(S3.6 "적용: P6-briefing, P7-push"). 감정·고민 대화는 어느 패키지에서도 하지 않는다(원칙7).
- **결정 8 — 테스트는 실 PostgreSQL(로컬 5433) + 롤백 픽스처. SQLite 는 불가.** 근거: `JSONB`, `vector(1536)` 과 `cosine_distance`, 부분 인덱스(`WHERE answered_at IS NULL`), `BIGINT GENERATED BY DEFAULT AS IDENTITY`, `ILIKE` — SQLite 에 전부 없거나 다르게 동작해서 "통과하는데 운영에서 깨지는" 테스트가 된다. `db_session` 픽스처는 커넥션에 바깥 트랜잭션을 열고 세션을 그 위에 바인딩한 뒤 테스트가 끝나면 rollback 하므로 DB 에 행이 남지 않는다(`alembic upgrade head` 상태만 요구). 접속 실패 시 `pytest.skip(reason)`.
- **결정 9 — `user_id` 는 설정값.** `app/settings.py` 의 `app_user_id()` 가 `APP_USER_ID`(기본 `"local"`)를 읽고 `ToolContext.user_id` 기본값이 된다. `.env` 는 읽지 않는다. `.env.example` 에 `APP_USER_ID` 이름을 추가할지는 U1 에서 결정하되 값은 넣지 않는다(security.md §1).
- **결정 10 — 의존성은 3개만, U1 에서 핀 고정.** `fastapi`, `uvicorn[standard]`, `httpx` 를 `requirements.txt` 에 설치본 버전으로 못 박는다(기존 SQLAlchemy·alembic·psycopg·pgvector 와 같은 방식). `pydantic` 은 `fastapi` 가 끌어오므로 직접 적지 않는다 — 우리가 고르는 의존성과 전이 의존성을 섞지 않기 위해서다. `httpx` 는 런타임에 쓰지 않지만 Starlette `TestClient` 가 없으면 못 도는 **테스트 필수** 의존성이므로 파일 안에 `# TestClient 용` 주석을 단다. U1 에서 설치하는 이유: U8 에서 처음 설치하면 그 단위 하나가 "의존성 추가 + 앱 + 테스트" 로 커지고, `pip freeze` 증거를 첫 단위 evidence 에 모아 두는 편이 04-review 에서 대조하기 쉽다. 미결 4(pyproject 이전)는 이 추가에도 불구하고 "이전하지 않는다"로 유지한다 — 파일 형식 문제이지 의존성 개수 문제가 아니다.
- **결정 11 — 라우터는 `app/api/` 로 나눈다(단일 `main.py` 아님).** 엔드포인트가 2개뿐이라 단일 파일이 더 짧지만, P5-loop 이 채팅·재개를, P6·P8 이 조회 API 를 같은 자리에 얹을 것이 확정되어 있다. 지금 `app/api/{deps,routes,schemas}.py` 로 나눠 두면 P5 는 `routes.py` 에 라우트를 더하고 `deps.py` 의 `get_session` 을 재사용하면 되고, `main.py` 는 조립만 하는 자리로 남는다. 요청 본문 스키마는 **`app/api/schemas.py`** 에 둔다(`app/tools/types.py` 의 반환 타입과 섞지 않는다 — 툴 타입은 LLM/함수 경계, API 스키마는 HTTP 경계). 도메인 예외 → HTTP 상태 매핑은 `main.py` 의 예외 핸들러 한 곳에서만 한다(라우트마다 try/except 를 흩뿌리지 않는다).
- **결정 12 — 이미 답한 질문은 409, 200 idempotent 가 아니다.** `POST /answers/{question_id}` 상태 코드: 없는 id·다른 사용자 → **404**, 이미 `answered_at` 이 있거나 24h 만료 → **409**(본문 `{"detail": {"code": "already_answered" | "expired", "question_id": id}}`), 저장된 `options` 밖의 답 → **422**, 정상 → 200. 409 를 고른 이유: (a) 원칙1 의 비대칭 비용 — 답이 바뀌면 뒤따르는 병합 판단이 바뀌는데 조용한 덮어쓰기는 "언제 무엇으로 확정됐는지" 를 지운다; (b) 200 idempotent 로 하려면 "같은 답이면 200, 다른 답이면?" 을 또 정해야 하고 결국 분기가 는다; (c) 프론트 중복 클릭은 P8 이 칩 비활성화로 막을 문제이고, 그때도 409 는 "이미 처리됨" 이라는 정확한 신호다. `answer_question` 이 올리는 도메인 예외 하나(`QuestionNotAnswerable`, `reason` 필드로 already_answered/expired 구분)를 핸들러가 409 로 매핑한다. **`ctx.session_id` 는 답할 `pending_questions` 행의 `session_id` 를 그대로 쓴다** — 클라이언트가 헤더로 주장하는 값보다 저장된 행이 권위 있고, trace 가 질문을 만든 턴과 같은 세션에 묶인다. `X-Session-Id` 헤더 규약은 세션을 새로 여는 쪽(P5 의 채팅 엔드포인트)이 정한다.
- **결정 13 — HTTP 테스트도 실 DB + 롤백 픽스처를 재사용한다.** `TestClient(create_app())` 를 쓰되 `app.dependency_overrides[get_session] = lambda: db_session` 으로 U1 의 롤백 세션을 주입한다. 그래야 (a) 테스트가 DB 에 행을 남기지 않고, (b) 테스트 코드가 `answer_question` 이 쓴 행을 **같은 트랜잭션에서** 직접 조회해 "정말 저장됐는가" 를 증거로 만들 수 있다(원칙9·검증 규약). 오버라이드된 `get_session` 은 commit 하지 않는다(롤백해야 하므로) — 대신 툴이 `flush()` 까지 하는 결정 2 덕분에 조회에는 문제가 없다. `GET /health` 테스트만은 오버라이드로 도는 세션을 쓰되, `alembic_version` 조회가 필요하므로 `dbtest` 마커를 붙인다.
- **리스크 — `TestClient` 와 앱 lifespan 이 실 엔진을 만든다.** `create_app()` 이 import·기동 시점에 `get_engine()` 을 부르면 테스트가 `POSTGRES_*` 환경변수에 묶인다(로컬은 5433). 대응: (a) 엔진 생성을 **지연**시킨다 — `get_engine()` 은 모듈 캐시로 최초 호출 시 만들고, `create_app()` 은 엔진을 만들지 않는다(lifespan 에서 접속 확인을 하지 않는다. 접속 확인은 `GET /health` 의 일이다); (b) 그래도 오버라이드되지 않은 경로가 남으면 테스트는 `POSTGRES_PORT=5433` 을 요구하므로, 판정 방법 표의 모든 pytest 명령에 이 변수를 붙이고 `-rs` 로 skip 여부를 evidence 에 남긴다; (c) `.env` 는 읽지 않는다(security.md §1).
- **리스크 — `httpx` 버전과 Starlette `TestClient` 호환.** `httpx` 0.28 에서 `app=` 인자가 제거되는 등 Starlette 의 `TestClient` 구현과 버전이 맞지 않으면 `TypeError` 로 테스트가 통째로 깨진다. 대응: U1 에서 설치 후 **`from fastapi.testclient import TestClient` 가 import 되고 최소 요청 1건이 도는 것을 그 자리에서 확인**해 evidence 에 남기고, 깨지면 우회(직접 ASGI 호출 구현)하지 말고 `httpx` 를 호환 버전으로 내려 핀을 고정하고 그 사실을 03-log 에 적는다. `fastapi`·`starlette`·`httpx` 세 줄을 `pip freeze` 증거에 함께 남긴다.
- **리스크 — 실 DB 테스트가 조용히 skip 된다.** 컨테이너가 꺼진 채로 `pytest` 가 초록으로 끝나면 수용 기준이 검증되지 않은 채 통과한 것처럼 보인다. 대응: (a) 모든 실행을 `-rs` 로 돌려 skip 사유를 evidence 에 남긴다; (b) 04-review 는 "`dbtest` 가 실행됐다"는 줄(skip 0)을 증거로 요구한다; (c) 수용 기준 전반부(시그니처)는 DB 없이 도는 `tools_check` 로 항상 검증되게 분리했다. verify-impl 은 종료 코드만 보므로 이 구분이 필요하다.
- **리스크 — pgvector 0.5.0 의 SQLAlchemy 연산자 API.** 계획은 `Vector` 컬럼의 `cosine_distance()`(코사인 거리, `similarity = 1 - distance`)를 전제한다. 설치본에서 이름·가용성이 다르면 우회하지 말고 `text("embedding <=> :vec")` 바인딩으로 후퇴하고 그 사실을 03-log 에 적는다. 인덱스가 없으므로 순차 스캔이며(행 수가 적어 무해), 인덱스는 P3-er.
- **리스크 — `scripts/tools_check.py` 가 CLAUDE.md 표를 파싱한다.** 표 서식이 바뀌면 검사가 깨진다. 대응: 파서는 "툴 7종" 제목과 다음 제목 사이의 표 행만 읽고, **7행을 못 찾으면 통과가 아니라 실패**(rc 1)로 처리한다. 이것이 "기획서가 바뀌면 코드가 조용히 어긋나는" 상황을 오히려 잡아 준다.
- **리스크 — D1 강제의 구멍.** `ctx.confirmed_question_id` 는 호출자가 채우는 값이므로, 손으로 아무 값이나 넣으면 우회할 수 있다. P2 는 "그 id 가 실제로 존재하고 `kind="new_person"` 이며 `answered_at IS NOT NULL` 이고 같은 `session_id` 인가"까지 DB 로 검사한다. 그 이상(루프가 확인 없이 create 를 부르지 않는가)은 P5-loop 의 책임이며, ctx 생성 지점을 한 곳으로 유지하는 것이 조건이다 — P5 01-plan 에 넘긴다.
- **리스크 — 시간 의존 테스트(24h 만료).** `question_status` 는 `ctx.now()` 를 주입받아 계산하고 `datetime.now()` 를 직접 부르지 않는다. `created_at` 은 서버 기본값이므로 만료 테스트는 행의 `created_at` 을 과거로 명시 지정해 만든다.
- **미결 1 — `agent_traces.tool_name` NOT NULL 과 툴이 아닌 단계.** P2 는 항상 실제 툴 이름을 넣으므로 문제가 없지만, P3-er 의 규칙 필터·LLM 판정 trace 는 툴이 아니다. 자리표시자(`"-"` 또는 단계 이름 재사용)를 P3-er 01-plan 에서 정한다(P1 04-review §7 인계 그대로). P2 는 상수를 미리 만들지 않는다.
- **미결 2 — `pending_questions.context` 에 무엇을 넣는가.** S3.4 는 "재개에 필요한 것만(발화, 후보 id, 확신도 분해). 비밀·전체 대화 이력 저장 금지". P2 의 `ask_user` 는 호출자가 준 dict 를 그대로 저장하되 JSON 직렬화와 문자열 절단(`TRACE_MAX_STRING`)만 적용한다. 실제로 어떤 키를 넣을지는 그 값을 만드는 P3-er·P5-loop 이 정한다.
- **미결 3 — `occurred_at`·`scheduled_at` 의 상대 표현 해석.** "어제 저녁"을 KST 기준 절대 시각으로 바꾸는 책임은 P5-loop 이다. P2 는 tz-aware `datetime` 만 받고, naive 값이면 `InvalidValue` 로 거절한다(조용한 UTC 가정 금지).
- **미결 4 — `pyproject.toml` 이전.** P1 01-plan 결정 3 이 "P2 착수 때 재검토"로 넘겼다. 이번에는 새 도구 설정이 없고(마커는 `conftest.py` 의 `pytest_configure` 로 등록하므로 설정 파일이 필요 없다) ruff 도 미설치이므로 **이전하지 않는다**. `requirements.txt` 는 결정 10 에 따라 `fastapi`·`uvicorn[standard]`·`httpx` 세 줄만 늘어난다(`openai`·`anthropic` 은 여전히 P3·P5 몫). ruff 도입 시점에 다시 본다.
- **미결 5 — `search_person` 의 문자열 매칭 범위.** 정확 일치·`ILIKE '%q%'` 부분 일치까지만 한다. 한국어 호칭 사전·초성·형태소 정규화는 규칙 필터의 일부이며 P3-er(2단계 "호칭 사전 호환")에서 정한다. P2 에서 어설픈 정규화를 넣으면 P3 의 `s_rule` 과 이중 출처가 된다.
- **미결 6 — `update_person(display_name=…)` 의 확인 요건(D6).** D6 은 "사용자 확인(answered question)을 거친 경우에만"이라고 못 박는다. P2 는 `display_name` 이 주어지면 `ctx.confirmed_question_id` 가 answered `identity` 또는 `new_person` 질문일 것을 요구한다. `facts`·`new_alias` 만 바꾸는 호출은 확인을 요구하지 않는다(별칭은 누적일 뿐 지워지지 않으므로 오병합 위험이 아니다 — 원칙1의 비대칭 비용이 걸리는 곳은 "다른 사람으로 합치는" 연결이고 그 판단은 P3 다).
- **미결 7 — 별칭 중복.** 같은 인물에 같은 문자열 별칭이 두 번 들어오면 새 행을 만들지 않고 기존 행의 `source`·`confirmed_at` 만 올린다(격상: `user_said` → `confirmed`). 다른 인물에 같은 별칭이 있는 것은 정상(동명이인) — 막지 않는다.
- **미결 8 — `delete_person` 을 어디에 두는가.** security.md §5 는 "인물 단위 완전 삭제 API"를 요구하지만 이번 수용 기준 밖이고, `pending_questions.context`·`agent_traces.input/output` 의 JSONB 안에 남는 `person_id` 참조(P1 04-review §7 의 사각지대)를 어떻게 정리·익명화할지는 그 JSONB 를 채우는 P3-er·P5-loop 이 정해진 뒤라야 답할 수 있다. **사용자 결정 필요**: P5-loop 의 엔드포인트 묶음에 넣을지, 별도 backlog 항목으로 세울지. P2 가 FastAPI 골격을 갖게 됐어도(결정 1) 이 판단은 바뀌지 않는다 — 막힌 것은 라우터가 없어서가 아니라 **JSONB 안의 참조를 어떻게 정리할지가 정해지지 않아서**이고, 그 값을 채우는 것은 P3·P5 다. P2 는 trace 에 `person_id` 를 넣을 때 이 사각지대를 docstring·registry 비고로 남기는 것까지만 한다.
- **기계 검증에서 예상되는 WARN(FAIL 아님).** `verify-plan.sh` 7번(registry 중복)은 산출물 목록의 `app/config.py`·`app/db/models.py`·`tests/conftest.py`·`tests/test_config.py`·`requirements.txt`(P1-schema 행, registry 43행)와 `README.md`(하네스 행)에 대해 "다른 패키지로 이미 있음" WARN 을 낸다. 여섯 파일 모두 **새 행을 만들지 않고 기존 행의 비고만 갱신**하는 것이 계획이므로 의도된 결과다(P1-schema 와 같은 처리). `app/main.py`·`app/api/*`·`tests/test_api.py` 는 registry 에 없으므로 신규 행이다.
- **보안.** 비밀은 `os.environ` 으로만 읽고 `.env` 는 읽지 않는다(§1). `agent_traces.input/output` 과 `pending_questions.context` 에 키·헤더·전체 대화 이력을 넣지 않는다(§1·§5). 접속 문자열·비밀번호를 로그·예외 메시지에 찍지 않으며 U1 의 `repr=False` 가 그 첫 조치다. 모든 조회에 `user_id` 조건(§5). 셸에서 `DROP`/`TRUNCATE` 를 쓰지 않고, 테스트 정리는 트랜잭션 rollback 으로만 한다(§4). 컨테이너·볼륨을 지우지 않는다.

## 읽은 카드
- `docs/wiki/INDEX.md` 패키지 id 표(P2-tools 행 — 담당 backend-agent, 닫는 R `R6 R7 R10 R18`; 이웃 P3-er `R4 R9`, P5-loop `R6 R7`, P6-memory·P6-briefing·P7-push 행), 상황별 읽기 경로 표, `docs/wiki/CURRENT.md`(active: none, 메모 — 다음 후보 P2-tools)
- `.claude/gitlog.md`(2026-09-05 14:46 스냅샷 — dev `5dc95bb`(P1-schema 완료), main `819e1ac`, 승격 대기 7건, 마지막 커밋 파일 목록, 미커밋 `docs/wiki/journal.md` 1건. P2-tools 태그 커밋 없음 = 착수 전)
- `docs/backlog.md` "구현 순서" P2 절(수용 기준 문장·의존 문구 "P1 스키마"), P1 절 완료 표시, P5·P6·P7 절(엔드포인트가 어느 패키지 수용 기준에 있는지 — 결정 1 의 근거), 리스크 로그
- `docs/resolution-plan.md` §3.2 툴 시그니처 v2 표(147~159행, `Candidate` 정의), §3.3 ER 4단계(161~174행 — P2/P3 경계), §3.4 ask_user 프로토콜(176~184행), §3.5(186~191행)·§3.6(193~196행 — 승격·브리핑 경계), §4 착수 준비 표(207~215행), §5 구현 순서 표 P2 행(227행)
- `docs/wiki/specs/S3.2-tools-v2.md` 전문(시그니처 7종·`Candidate`·"모든 툴 호출은 agent_traces 에 기록"), `docs/wiki/specs/S3.4-ask-user-protocol.md` 전문(턴 N/N+1 다이어그램·24h 만료·확인 칩·context 최소 저장 — "적용: P2-tools, P5-loop"), `docs/wiki/specs/S3.1-schema-v2.md` 전문(컬럼·CHECK·`kind` 3값·CASCADE), `docs/wiki/specs/S3.3-er-pipeline.md` 전문(1단계 후보 검색만 P2 와 접점), `docs/wiki/specs/S3.5-memory-promotion.md` 전문(승격은 P6-memory), `docs/wiki/specs/S3.6-briefing-push.md` 전문(브리핑 문장화·제안은 P6-briefing, 푸시는 P7-push)
- `docs/wiki/decisions/D01-new-person-confirm.md` 전문("직접 호출 테스트는 실패해야 한다"), `D02-ask-user-async.md` 전문(동기 대기 금지·독립 툴 유지), `D06-display-name-policy.md` 전문(최근 호칭·별칭 삭제 금지·확인 필요), `D04-embedding-provider.md` 전문(N=1536, `EmbeddingProvider` 인터페이스 강제), `D05-alias-level-embedding.md` 전문(별칭 단위 top-K→인물별 max, 확정 시 즉시 임베딩), `D09-pattern-rule.md` 전문(패턴은 규칙 기반이며 적용은 P6-memory — `add_event` 는 트리거하지 않는다)
- `docs/wiki/review-index.md` R6·R7 행(14·15행 — D1/D2 → S3.4 → P2-tools, P5-loop), R10 행(18행 — S3.2), R18 행(26행 — D6 → S3.2 → P2-tools)
- `docs/wiki/security.md` §1 비밀(.env·키 문자열·로그와 trace 마스킹), §4(셸 DROP/TRUNCATE 금지), §5 제품 코드가 지킬 것(인물 단위 완전 삭제·context 최소 저장·모든 조회에 `user_id`), §6 예외
- `CLAUDE.md` "툴 7종(제품 속 에이전트가 호출) — 시그니처 v2" 표와 그 아래 4개 불릿(`Candidate`·`ask_user` 독립 유지·비동기 대기 질문 모델), "불변 원칙" 1·2·4·6·7·9, "데이터 모델" 절(스키마 v2·`events.type` 고정 집합·ER trace 규약)
- `docs/wiki/packages/P1-schema/04-review.md` §6 권고(F-8eeb9b `ConnInfo` repr, F-081752 status 파생, 관찰 O2·O3·O5), §7 다음 패키지에 넘기는 것 전체(모델·상수 import 경로, `resolve_connection()`/`sqlalchemy_url()`, 엔진·sessionmaker 부재, NOT NULL 계약, `person_aliases.source` 값 집합 미정, `agent_traces` NOT NULL, 인물 삭제 사각지대, `user_id` 출처, `person_facts` UNIQUE 미설정, requirements→pyproject 재검토)
- `docs/wiki/packages/P1-schema/01-plan.md` 전문(형식·상세도 참고 — 판정 방법 절의 존재 이유, 미결 서술 방식)
- `docs/wiki/registry.md` 전문(grep: `app/tools`·`app/settings.py`·`app/db/session.py`·`app/embedding.py`·`scripts/tools_check.py` → 없음 / `app/config.py` 38행·`app/db/models.py` 40행·`tests/conftest.py` 47행·`README.md` 32행·`scripts/embed_pilot.py` 26행("EmbeddingProvider 는 P2/P3 에서 백엔드 모듈로 이동") 존재 → 비고 갱신 대상)
- `.claude/scripts/verify-plan.sh` 전문(태그→카드 존재, 작업 단위 Refs, 수용 기준 backlog 일치, 의존 04-review 완료, 산출물 registry 중복 WARN 규칙)
- **개정 시 추가로 연 것(2026-09-05, 사용자 결정 반영)**: `docs/wiki/specs/S3.4-ask-user-protocol.md` 재확인(3행 "적용: P2-tools, P5-loop, P8-frontend", 6~7행 턴 N / 턴 N+1 다이어그램 — 결정 1 의 "앞 절반/뒤 절반" 경계 근거, 13행 context 최소 저장), `docs/backlog.md` P5 행 전문(40행 "발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개" — P5 가 P2 의 엔드포인트를 확장한다는 문장의 출처)과 P2 행(27행, 수용 기준 문장 무변경 확인), `docs/wiki/registry.md` 재grep(`app/main.py`·`app/api`·`tests/test_api.py`·`fastapi` → 없음 / `requirements.txt` 43행 P1-schema 존재 → 비고 갱신 대상)
- 코드 현황: `app/config.py` 전문(`ConnInfo` 필드·`safe_summary`·`sqlalchemy_url`·`resolve_connection` — repr 에 password 노출 확인), `app/db/models.py` 전문(9모델·값 집합 상수 4개·NOT NULL 정책 docstring), `tests/conftest.py` 전문(sys.path 등록만), `requirements.txt` 전문(SQLAlchemy 2.0.50·alembic·psycopg·pgvector 0.5.0), `scripts/schema_check.py` 접속·종료 코드 부분(`resolve_connection` → `psycopg.connect(**as_keywords())`, rc 0/1/2), `scripts/embed_pilot.py` 의 `EmbeddingProvider` Protocol·`OpenAIEmbeddingProvider`(57~97행 — 재사용 가능 여부 판단), `app/main.py`·세션 모듈 부재 확인
