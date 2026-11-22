# P9d-sensitive-guard · 계획 검증 (02-plan-verify)

대상: 01-plan.md(개정 2) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-22(1차 검증 · 같은 날 재검증 2회차 · 3회차)

기준 커밋 `6d97217`(dev2 = origin/dev2). 제품 코드는 `cef47d0` 이후 변경 0(`git diff --stat 6d97217 -- app alembic web tests scripts evaluation` 빈 출력). 이 문서는 계획·카드·코드를 고치지 않는다. 법적 판단은 하지 않는다.

**이 문서를 읽는 순서**: 지금 유효한 판정은 1.1절(기계 검증 최신 출력)·2절 맨 위 표(3회차 점검표)·3.A절(3회차 소견)·4절 `결과:` 줄이다. 2회차 내용(2.0.1절 점검표·3.0절 소견·4.0.1절 결정)과 1차 내용("1차(이력)" 표시)은 지우지 않고 남겼다 — 2회차 절이 적은 01-plan 행 번호는 개정 1, 1차 절은 개정 전 계획 기준이다. 3회차 절의 행 번호는 개정 2 기준이다.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

명령: `python3 .claude/scripts/save_evidence.py P9d-sensitive-guard verify-plan -- bash .claude/scripts/verify-plan.sh P9d-sensitive-guard`

### 1.1 재검증(3회차) — 01-plan 개정 2 와 이 문서의 3회차 판정을 쓴 뒤

3회차에서 본 실행(전부 exit 0, `FAIL=0`):

| 파일 | 언제 | 결과 줄 | 비고 |
|------|------|---------|------|
| `evidence/20261122-1721-verify-plan.txt` | 개정 2 직후(메인 세션 실행, 이 문서는 아직 2회차 내용) | `FAIL=0 WARN=58` | 2회차 r2 출력과 `diff` — 시각 2줄, registry WARN 5건 추가(개정 2 가 닫힌 목록에 더한 기존 시험 `tests/test_api.py`·`test_agent_query_gate.py`·`test_agent_query_types.py`·`test_api_read_persons.py`·`test_mcp_tools.py`), 결과 줄. 점검표 줄은 2회차 3행 그대로 |
| **`evidence/20261122-1732-verify-plan.txt`** | 3회차 점검표·결정을 쓴 뒤 — **아래 출력** | `FAIL=0 WARN=57` | 점검표 8행 전부 통과 → `PASS  보류 0건`. WARN 57 = registry 57 |
| `evidence/20261122-1732-verify-plan-r3-confirm.txt` | 아래 출력을 이 절에 붙인 뒤(문서 최종 상태) | `FAIL=0 WARN=57` | 위 파일과 `diff` — 시각 1줄뿐. 붙인 출력과 위 증거 파일은 `diff` 0줄 |

#### 1.1.1 2회차 실행 이력 (01-plan 개정 1)

| 파일 | 언제 | 결과 줄 | 비고 |
|------|------|---------|------|
| `evidence/20261122-1542-verify-plan.txt` | 개정 1 직후(메인 세션 실행, 이 문서는 아직 1차 내용) | `FAIL=0 WARN=53` | 점검표 줄은 1차 3행 |
| `evidence/20261122-1711-verify-plan.txt` | 2회차 점검표를 쓴 직후 | `FAIL=0 WARN=53` | 5행 근거 칸에 backlog 인용문의 낱말이 들어가 스크립트가 한 행을 더 센 것(판정은 통과). 5행 문장을 고쳐 다시 돌렸다 |
| `evidence/20261122-1711-verify-plan-r2.txt` | 그 문장을 고친 뒤 — 2회차 때 이 절에 붙였던 출력 | `FAIL=0 WARN=53` | 점검표 줄 = 2회차 3행(M5). 출력 전문은 그 증거 파일에 있다 — 아래 3회차 출력과의 차이는 시각 2줄·점검표 `보류` 줄·registry WARN 5건·결과 줄뿐이다(`diff` 로 확인) |
| `evidence/20261122-1713-verify-plan-r2-confirm.txt` | 2회차 문서 최종 상태 | `FAIL=0 WARN=53` | r2 와 머리 줄(시각) 밖은 `diff` 0줄 |

#### 1.1.2 3회차 출력 전체

파일: `evidence/20261122-1732-verify-plan.txt` (exit 0)
```
# 명령: bash .claude/scripts/verify-plan.sh P9d-sensitive-guard
# 시각: 2026-11-22T17:32:00+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 6d97217 (dev2)
# exit: 0
# ---
== verify-plan P9d-sensitive-guard  (2026-11-22 17:32) ==
PASS  존재: docs/wiki/packages/P9d-sensitive-guard/01-plan.md
PASS  존재: docs/wiki/packages/P9d-sensitive-guard/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D14
PASS  카드 존재: D16
PASS  카드 존재: D17
PASS  카드 존재: D18
PASS  카드 존재: D19
PASS  카드 존재: D2
PASS  카드 존재: D20
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [x] U0 **[메인 세션 + architect] CR-009 문서 이행 — D20 신설, D2·D14
PASS  Refs 있음: - [ ] U1 **[eval-agent] 민감 가드 시험 세트·라벨 규칙·형식 검사기 — test 는 U2
PASS  Refs 있음: - [ ] U2 **[backend-agent] 규칙 검사 모듈 — `detect`·`mask`·`name_
PASS  Refs 있음: - [ ] U3 **[backend-agent] 리비전 0006 + 모델 — 민감 표시 컬럼·고지 컬럼·`p
PASS  Refs 있음: - [ ] U4 **[backend-agent] 가입 고지·재고지 API·미동의 403·주기 브리핑 건너뜀*
PASS  Refs 있음: - [ ] U5a **[backend-agent] 가림 적용 — 대화 기록·trace·LLM·응답 전부 가린
PASS  Refs 있음: - [ ] U5b **[backend-agent] 사전 동의 질문 — 라우트가 `ask_user` 툴 없이 
PASS  Refs 있음: - [ ] U5c **[backend-agent] 사전 동의 재개·거절·만료 정리·배포 전 대기 질문 — 지
PASS  Refs 있음: - [ ] U6 **[backend-agent] 사후 확인 — 추출 LLM 의 민감 표시, 기록·조회 모두 
PASS  Refs 있음: - [ ] U7a **[backend-agent] 저장 표시 전파·동의 문맥 사슬·사실 표시 단조·승격 입력
PASS  Refs 있음: - [ ] U7b **[backend-agent] 이름 규칙(사용자 결정 15·22) — `_apply_na
PASS  Refs 있음: - [ ] U8 **[backend-agent] 내보내는 경로 제외(fail-closed) — `get_br
PASS  Refs 있음: - [ ] U9a **[frontend-agent] 가입 고지 체크·재고지 모달·403 `notice_req
PASS  Refs 있음: - [ ] U9b **[frontend-agent] 채팅 차단 안내·거절 줄 표시, 인물 카드 민감 배지·기
PASS  Refs 있음: - [ ] U10 **[eval-agent] 평가 실행·실패 분석 — 규칙 단독 수치와 사후 LLM 표시 수
PASS  Refs 있음: - [ ] U11 **[verifier] 완료 검토(로컬) — verify-impl·04-review·변이*
PASS  Refs 있음: - [ ] U12 **[메인 세션 SSH + 사용자] 운영 반영 — 백업 → 0006 → 재배포 → 바깥 확
PASS  backlog 일치: **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)** — 동의 전 LLM·임베딩
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P6-memory
PASS  의존 완료: P7-push
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/sensitive_guard/dev.jsonl
PASS  registry 중복 없음: evaluation/sensitive_guard/test.jsonl
PASS  registry 중복 없음: evaluation/sensitive_guard/README.md
PASS  registry 중복 없음: evaluation/sensitive_guard/run.py
PASS  registry 중복 없음: scripts/validate_sensitive_set.py
PASS  registry 중복 없음: app/guard/__init__.py
PASS  registry 중복 없음: app/guard/rules.py
PASS  registry 중복 없음: app/guard/detect.py
PASS  registry 중복 없음: app/guard/mask.py
PASS  registry 중복 없음: app/guard/names.py
PASS  registry 중복 없음: app/guard/messages.py
PASS  registry 중복 없음: app/guard/consent.py
PASS  registry 중복 없음: alembic/versions/0006_sensitive_guard.py
WARN  registry 에 다른 패키지로 이미 있음: app/db/models.py → | 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema | 4dfaf33 | `Perso
| 모듈 | 계정·세션·대화 기록 모델 `User`·`AuthSession`·`ChatMessage`, `PendingQuestion.user_
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 모듈 | 리비전 0005 — `mcp_tokens`(계정당 1행 — `user_id` UNIQUE·`token_hash` UNIQUE·`us
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
| 설정 | 고정 사용자 폐지 — `app_user_id()`·`DEFAULT_APP_USER_ID`·`APP_USER_ID` 삭제(`tests
| 모듈 | 닉네임 정규화 `normalize_nickname`(NFC → strip → fullmatch → lower, 위반이면 `None`
| 설정 | `MCP_TOKEN_DAYS`·`MCP_LIST_PEOPLE_LIMIT`·`MCP_FIND_PERSON_LIMIT`·`MCP_FIN
WARN  registry 에 다른 패키지로 이미 있음: app/auth/routes.py → | 엔드포인트 | `POST /auth/signup`(201)·`POST /auth/login`(200)·`POST /auth/logout`(2
| 모듈 | 푸시 구독 소유 — `save_subscription` 이 같은 endpoint 의 다른 사용자 행을 지운 뒤 upsert(결정 P
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 엔드포인트 | `POST·GET·DELETE /auth/mcp-token` — 201 `{token,created_at,expires_at}
WARN  registry 에 다른 패키지로 이미 있음: app/auth/deps.py → | 모듈 | 로그인 의존성 `current_user`(없거나 만료면 401 `unauthenticated`) · 시계 `get_auth_now`
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-tools | 4d58
| 엔드포인트 | POST /chat | app/api/routes.py | P5-loop | d5c8ec9 | 발화 1건 → 인식(LLM 1회
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 엔드포인트 | GET /persons · GET /persons/{person_id} (읽기 전용) | app/api/routes.py | 
| 엔드포인트 | GET /events/{event_id}/raw · GET /persons/{person_id}/facts/{fact_id}/
| 엔드포인트 | GET /questions/pending · GET /briefings (읽기 전용) | app/api/routes.py | 
| 모듈 | 계정 대화 세션 `chat_session_id(user)` = `chat:<user_id>` · 전 라우트 로그인 필수(`/heal
| 모듈 | 대화 기록 `append(session, user_id, role, content, question_id=None)`(flush 만
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
WARN  registry 에 다른 패키지로 이미 있음: app/api/read.py → | 모듈 | 읽기 전용 조회 `list_persons()`·`get_person_card()` · 상수 `TIMELINE_LIMIT=20`·`U
| 모듈 | 원문 조회 `get_event_raw()`·`get_fact_sources()` · 상수 `FACT_SOURCES_LIMIT=20`
| 모듈 | 브리핑 조회 `list_briefings()` · 상수 `BRIEFINGS_LOOKBACK_DAYS=7`·`BRIEFINGS_LIM
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools | 4d5817e | `AnswerIn`·`
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 모듈 | 조회 응답 `PersonListItemOut`·`PersonBasicOut`·`PersonFactOut`·`PersonPattern
| 모듈 | 원문 응답 `EventRawOut`·`FactBriefOut`·`FactSourceEventOut`·`FactSourcesOut` 
| 모듈 | 브리핑 조회 응답 `BriefingRecordOut`·`BriefingScheduleOut`·`BriefingPersonOut` |
| API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
| 설정 | 고정 사용자 폐지 — `app_user_id()`·`DEFAULT_APP_USER_ID`·`APP_USER_ID` 삭제(`tests
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 엔드포인트 | `POST·GET·DELETE /auth/mcp-token` — 201 `{token,created_at,expires_at}
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/tools/context.py → | 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | 실행 맥락(`
| 모듈 | 대기 질문 소유 검사 — `answer_question`·`list_pending(ctx)` 가 `user_id == ctx.use
WARN  registry 에 다른 패키지로 이미 있음: app/tools/questions.py → | 모듈 | ask_user·answer_question·question_status | app/tools/questions.py | P2-to
| 모듈 | 대기 질문 소유 검사 — `answer_question`·`list_pending(ctx)` 가 `user_id == ctx.use
WARN  registry 에 다른 패키지로 이미 있음: app/tools/persons.py → | 모듈 | search_person·create_person·update_person | app/tools/persons.py | P2-too
WARN  registry 에 다른 패키지로 이미 있음: app/tools/records.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
WARN  registry 에 다른 패키지로 이미 있음: app/tools/briefing.py → | 모듈 | get_briefing | app/tools/briefing.py | P2-tools | 7c94aad | `person_facts
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/inputs.py → | 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 입력 조립(build_briefing_input) | app/briefing/inputs.py | P6-briefing | 
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/select.py → | 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 대상 선정(select_due_schedules) | app/briefing/select.py | P6-briefing | 
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/scheduler.py → | 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 1분 주기 작업(스케줄러) | app/briefing/scheduler.py | P6-briefing | a67692e | 
| 모듈 | 계정별 브리핑 주기 작업 — `default_run_once(now=None)` 이 창(`BRIEFING_LEAD_HOURS`, 호
WARN  registry 에 다른 패키지로 이미 있음: app/memory/promote.py → | 모듈 | 승격(미승격 이벤트 → person_facts upsert) | app/memory/promote.py | P6-memory | b
WARN  registry 에 다른 패키지로 이미 있음: app/memory/patterns.py → | 모듈 | 반복 패턴 감지(규칙, LLM·임베딩 0) | app/memory/patterns.py | P6-memory | d67d084 | 
WARN  registry 에 다른 패키지로 이미 있음: app/memory/direct_facts.py → | 모듈 | 루프 직접 사실 → 원문 링크(U7, 결정 G(ii)) | app/memory/direct_facts.py | P6-memory |
WARN  registry 에 다른 패키지로 이미 있음: app/memory/extract.py → | 모듈 | 사실 추출기(FactExtractor, 공급자 3종+가짜) | app/memory/extract.py | P6-memory | 48
WARN  registry 에 다른 패키지로 이미 있음: app/mcp_server/tools.py → | 모듈 | MCP 도구 본체 4개 `tool_list_people`·`tool_find_person`·`tool_get_person_card`
PASS  registry 중복 없음: tests/test_guard_rules.py
PASS  registry 중복 없음: tests/test_migration_0006.py
PASS  registry 중복 없음: tests/test_privacy_notice.py
PASS  registry 중복 없음: tests/test_guard_mask.py
PASS  registry 중복 없음: tests/test_guard_messages.py
PASS  registry 중복 없음: tests/test_guard_pre.py
PASS  registry 중복 없음: tests/test_guard_resume.py
PASS  registry 중복 없음: tests/test_guard_posthoc.py
PASS  registry 중복 없음: tests/test_guard_storage.py
PASS  registry 중복 없음: tests/test_guard_names.py
PASS  registry 중복 없음: tests/test_guard_export.py
WARN  registry 에 다른 패키지로 이미 있음: tests/test_schema_models.py → | 테스트 | 스키마 v2 모델 메타데이터(DB 없이) | tests/test_schema_models.py | P1-schema | 4dfaf
WARN  registry 에 다른 패키지로 이미 있음: tests/test_schema_check.py → | 테스트 | 스키마 검사 스크립트 순수 로직(DB 없이) | tests/test_schema_check.py | P1-schema | 03e3
WARN  registry 에 다른 패키지로 이미 있음: tests/test_migration_0003.py → | 테스트 | 리비전 0003 검사 11건 — head·새 테이블 컬럼·UNIQUE·CHECK·NOT NULL·비우기·`alembic check
WARN  registry 에 다른 패키지로 이미 있음: tests/test_migration_0004.py → | 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_migration_0005.py → | 테스트 | MCP 백엔드 시험 — `test_mcp_tokens_api` 18 · `test_mcp_tools` 31 · `test_mcp_
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-tools | 
| 모듈 | FastAPI lifespan — 브리핑 주기 작업 진입점 | app/main.py | P6-briefing | a67692e | 
WARN  registry 에 다른 패키지로 이미 있음: tests/test_agent_query_gate.py → | 테스트 | 조회 턴 게이트 Q 관문(기록 툴 4종 거부·내부 전용 툴 ② 사유 유지·순서·기록 턴 대조군)·프롬프트 문장 3종 | tests
WARN  registry 에 다른 패키지로 이미 있음: tests/test_agent_query_types.py → | 테스트 | 조회 발화 계약 — `intent` 어휘·스키마·`validate_proposal` 규칙·`PendingResume.intent`
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api_read_persons.py → | 테스트 | `GET /persons`·`GET /persons/{id}` | tests/test_api_read_persons.py | P8
WARN  registry 에 다른 패키지로 이미 있음: tests/test_mcp_tools.py → | 테스트 | MCP 백엔드 시험 — `test_mcp_tokens_api` 18 · `test_mcp_tools` 31 · `test_mcp_
WARN  registry 에 다른 패키지로 이미 있음: tests/auth_helpers.py → | 테스트 | 로그인 테스트 도우미 `make_user(session, user_id="local")`·`logged_in_client(app,
| 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_api.py → | 테스트 | 인증 시험 — passwords·settings·api·origin (U2 117건 + 리뷰 보완 37건) | tests/test
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_nickname.py → | 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_availability.py → | 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_origin.py → | 테스트 | 인증 시험 — passwords·settings·api·origin (U2 117건 + 리뷰 보완 37건) | tests/test
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_required_routes.py → | 테스트 | 미로그인 401 계약(라우트 열거) 11건 · 계정 간 격리 21건(남의 id 응답 == 없는 id 응답, 남의 질문 답변 시 행
WARN  registry 에 다른 패키지로 이미 있음: tests/test_briefing_scheduler_users.py → | 모듈 | 계정별 브리핑 주기 작업 — `default_run_once(now=None)` 이 창(`BRIEFING_LEAD_HOURS`, 호
WARN  registry 에 다른 패키지로 이미 있음: tests/test_push_wiring.py → | 테스트 | 수동·주기 두 경로의 알림기 연결(U5) | tests/test_push_wiring.py | P7-push | 55fc0f3 |
PASS  registry 중복 없음: evaluation/recognition/probe.py
WARN  registry 에 다른 패키지로 이미 있음: tests/test_agent_loop.py → | 테스트 | 해석·기록·응답 단계(run_turn, 되묻기 기본 케이스) | tests/test_agent_loop.py | P5-loop |
PASS  registry 중복 없음: web/src/lib/privacyNotice.ts
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/AuthScreen.tsx → | 모듈 | 로그인·가입 화면 `AuthScreen`·`AUTH_NOTICE`·`authFailureNotice`(한 화면 전환, 가입은 확인 
| 모듈 | `AuthScreen` 닉네임 칸·칸마다 "중복 확인"(`role=status`, `username-check`/`nickname-
WARN  registry 에 다른 패키지로 이미 있음: web/src/components/AppShell.tsx → | 앱 틀·라우팅 | `web/src/App.tsx` · `web/src/main.tsx` · `web/src/routes.ts`(`parseH
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
| 브리핑 화면 알림 버튼·인앱 배너 | `BriefingScreen.tsx` `PushSubscribe`(미구독 "알림 받기"/진행 "알림 켜
| 모듈 | 사이드바 계정 줄 `AccountRow`(아이디 · 로그아웃) · `getCurrentPushEndpoint()`(로그아웃 때 이 
| 모듈 | `AuthScreen` 닉네임 칸·칸마다 "중복 확인"(`role=status`, `username-check`/`nickname-
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/api/types.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
| 모듈 | `checkAvailability(q)` — 준 키만 쿼리에 싣는 `GET /auth/availability`, 401 에도 로그아
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/api/client.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 세션 보관·채팅 호출 | `web/src/session.ts`(`getSessionId`·`setSessionId`·`clearSession
| 인물 카드 화면 | `web/src/screens/PersonCardScreen.tsx`(`PersonCardScreen`·`CARD_NOT
| 브리핑 화면 | `web/src/screens/BriefingScreen.tsx`(`BriefingScreen`·`BRIEFING_NOTIC
| 푸시 구독 | `web/src/push.ts`(`subscribeToPush`·`getPushStatus`·`urlBase64ToUint8A
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
| 모듈 | `checkAvailability(q)` — 준 키만 쿼리에 싣는 `GET /auth/availability`, 401 에도 로그아
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/ChatScreen.tsx → | 채팅 화면 | `web/src/screens/ChatScreen.tsx`(`ChatScreen`·`NOTICE` 고정 안내 문장 5개 — 빈
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
| 모듈 | 사이드바 계정 줄 `AccountRow`(아이디 · 로그아웃) · `getCurrentPushEndpoint()`(로그아웃 때 이 
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/PersonCardScreen.tsx → | 인물 카드 화면 | `web/src/screens/PersonCardScreen.tsx`(`PersonCardScreen`·`CARD_NOT
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
PASS  registry 중복 없음: web/src/lib/labels.ts
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/auth.test.tsx → | 테스트 | 프론트 로그인 시험 — `auth.test.tsx` 22건 + `api.test`·`chat.test` 신규 11건(Vitest 
| 테스트 | 가입 닉네임·중복 확인 시험 — `auth.test.tsx` 새 describe + `api.test.ts` 2건(Vitest 1
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/chat.test.tsx → | 테스트 | 채팅 테스트 21건 — 세션 헤더·저장·422 버림·Enter/Shift+Enter·타이핑 점·칩 글자/순서/선택 고정/이어 붙임
| 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/card.test.tsx → | 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
| 테스트 | 브리핑 테스트 16건(`briefing.test.tsx` — 서버 순서·머리줄 3요소·문자열 동일(특수문자·공백)·basis 미표
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
PASS  registry 중복 없음: web/src/__tests__/labels.test.tsx
PASS  registry 중복 없음: web/src/__tests__/notice.test.tsx
PASS  registry 중복 없음: reports/sensitive_guard.md
PASS  registry 중복 없음: reports/sensitive_guard_metrics.json
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
WARN  registry 에 다른 패키지로 이미 있음: docs/user-setup/13-user-todo-deploy.md → | 문서 | EC2 최소 구성 배포 절차(신규 계정 Free Plan·Budgets·키 페어·보안 그룹·t4g.small·EIP·Docker·`
PASS  registry 중복 없음: docs/wiki/packages/P9d-sensitive-guard/03-log.md
WARN  registry 에 다른 패키지로 이미 있음: tests.md → | 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
| 문서 | 테스트 기록 — 프론트 Vitest 135건·E2E 4건을 표 1줄씩(무엇을 확인·입력 → 기대·결과·검출한 변이 ID), 총계와 
| 테스트 | 배포 파일 텍스트 검사 **19건** — compose `name`·서비스 3·postgres/backend `ports` 0·`
WARN  registry 에 다른 패키지로 이미 있음: 04-review.md → | 문서 | P4b 완료 검토와 그 검증 증거(게이트 독립 재계산·부정 케이스 18건·D12/D13 grep·회귀 3종 재확인·경계 확인·ver
PASS  registry 중복 없음: app/guard/messages.py
PASS  registry 중복 없음: tests/test_guard_messages.py
PASS  registry 중복 없음: web/src/lib/privacyNotice.ts
PASS  registry 중복 없음: web/src/__tests__/notice.test.tsx
PASS  registry 중복 없음: test_privacy_notice.py
PASS  registry 중복 없음: notice.test.tsx
== 결과: FAIL=0 WARN=57 ==
```
WARN 57 = 전부 registry 줄이다(점검표 줄은 `PASS  보류 0건`). FAIL 0.

registry 줄은 전부 "registry 에 다른 패키지로 이미 있음" 이다 — 이 계획이 기존 파일을 **고치는** 목록이라 나오는 줄이고, 개정 1 에서 U3·U4·U7b 닫힌 목록에 든 기존 시험 파일 7개, 개정 2 에서 U3·U5a·U6·U8 닫힌 목록에 든 기존 시험 파일 5개(`tests/test_api.py`·`test_agent_query_gate.py`·`test_agent_query_types.py`·`test_api_read_persons.py`·`test_mcp_tools.py`)만큼 늘었다. 새로 만드는 파일은 전부 `PASS  registry 중복 없음` 이다. 중복 구현 소견이 아니다(1차·2회차와 같은 해석).

### 1.2 1차 검증 때의 출력 (이력 — 01-plan 개정 전)

**1차**(이 문서를 쓰기 전, 메인 세션 실행) — `evidence/20261122-1509-verify-plan.txt`, exit 1, `== 결과: FAIL=1 WARN=46 ==`. FAIL 은 `FAIL  없음: docs/wiki/packages/P9d-sensitive-guard/02-plan-verify.md` 1건뿐이다. 나머지 줄은 아래 2차 출력과 같다(2차는 그 FAIL 줄이 PASS 로 바뀌고 6번 검사(점검표) 줄이 더해진다).

**2차**(이 문서를 쓴 뒤) — 파일 이름과 출력 전체는 아래.

파일: `evidence/20261122-1528-verify-plan.txt` (exit 0). 1차와의 차이는 `diff` 로 확인했다 — 시각 줄, 02-plan-verify 존재 줄(FAIL → PASS), 6번 검사 6줄 추가, 결과 줄뿐이다.
```
# 명령: bash .claude/scripts/verify-plan.sh P9d-sensitive-guard
# 시각: 2026-11-22T15:28:21+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 6d97217 (dev2)
# exit: 0
# ---
== verify-plan P9d-sensitive-guard  (2026-11-22 15:28) ==
PASS  존재: docs/wiki/packages/P9d-sensitive-guard/01-plan.md
PASS  존재: docs/wiki/packages/P9d-sensitive-guard/02-plan-verify.md
PASS  카드 존재: D14
PASS  카드 존재: D16
PASS  카드 존재: D17
PASS  카드 존재: D18
PASS  카드 존재: D19
PASS  카드 존재: D2
PASS  카드 존재: D20
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [x] U0 **[메인 세션 + architect] CR-009 문서 이행 — D20 신설, D2·D14
PASS  Refs 있음: - [ ] U1 **[eval-agent] 민감 가드 시험 세트·라벨 규칙·형식 검사기 — test 는 U2
PASS  Refs 있음: - [ ] U2 **[backend-agent] 규칙 검사 모듈 — `detect`·`mask`·`name_
PASS  Refs 있음: - [ ] U3 **[backend-agent] 리비전 0006 + 모델 — 민감 표시 컬럼·고지 컬럼·`p
PASS  Refs 있음: - [ ] U4 **[backend-agent] 가입 고지·재고지 API·미동의 403·주기 브리핑 건너뜀*
PASS  Refs 있음: - [ ] U5a **[backend-agent] 가림 적용 — 대화 기록·trace·LLM·응답 전부 가린
PASS  Refs 있음: - [ ] U5b **[backend-agent] 사전 동의 질문 — 라우트가 `ask_user` 툴 없이 
PASS  Refs 있음: - [ ] U5c **[backend-agent] 사전 동의 재개·거절·만료 정리·배포 전 대기 질문 — 지
PASS  Refs 있음: - [ ] U6 **[backend-agent] 사후 확인 — 추출 LLM 의 민감 표시, 기록·조회 모두 
PASS  Refs 있음: - [ ] U7 **[backend-agent] 저장 표시 전파·동의 문맥 사슬·사실 표시 단조·승격 입력 
PASS  Refs 있음: - [ ] U8 **[backend-agent] 내보내는 경로 제외(fail-closed) — `get_br
PASS  Refs 있음: - [ ] U9a **[frontend-agent] 가입 고지 체크·재고지 모달·403 `notice_req
PASS  Refs 있음: - [ ] U9b **[frontend-agent] 채팅 차단 안내·거절 줄 표시, 인물 카드 민감 배지·기
PASS  Refs 있음: - [ ] U10 **[eval-agent] 평가 실행·실패 분석 — 규칙 단독 수치와 사후 LLM 표시 수
PASS  Refs 있음: - [ ] U11 **[verifier] 완료 검토(로컬) — verify-impl·04-review·변이*
PASS  Refs 있음: - [ ] U12 **[메인 세션 SSH + 사용자] 운영 반영 — 백업 → 0006 → 재배포 → 바깥 확
PASS  backlog 일치: **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)** — 동의 전 LLM·임베딩
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P6-memory
PASS  의존 완료: P7-push
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 1 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/sensitive_guard/dev.jsonl
PASS  registry 중복 없음: evaluation/sensitive_guard/test.jsonl
PASS  registry 중복 없음: evaluation/sensitive_guard/README.md
PASS  registry 중복 없음: evaluation/sensitive_guard/run.py
PASS  registry 중복 없음: scripts/validate_sensitive_set.py
PASS  registry 중복 없음: app/guard/__init__.py
PASS  registry 중복 없음: app/guard/rules.py
PASS  registry 중복 없음: app/guard/detect.py
PASS  registry 중복 없음: app/guard/mask.py
PASS  registry 중복 없음: app/guard/names.py
PASS  registry 중복 없음: app/guard/messages.py
PASS  registry 중복 없음: app/guard/consent.py
PASS  registry 중복 없음: alembic/versions/0006_sensitive_guard.py
WARN  registry 에 다른 패키지로 이미 있음: app/db/models.py → | 모듈 | 스키마 v2 SQLAlchemy 모델 9개 | app/db/models.py | P1-schema | 4dfaf33 | `Perso
| 모듈 | 계정·세션·대화 기록 모델 `User`·`AuthSession`·`ChatMessage`, `PendingQuestion.user_
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 모듈 | 리비전 0005 — `mcp_tokens`(계정당 1행 — `user_id` UNIQUE·`token_hash` UNIQUE·`us
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
| 설정 | 고정 사용자 폐지 — `app_user_id()`·`DEFAULT_APP_USER_ID`·`APP_USER_ID` 삭제(`tests
| 모듈 | 닉네임 정규화 `normalize_nickname`(NFC → strip → fullmatch → lower, 위반이면 `None`
| 설정 | `MCP_TOKEN_DAYS`·`MCP_LIST_PEOPLE_LIMIT`·`MCP_FIND_PERSON_LIMIT`·`MCP_FIN
WARN  registry 에 다른 패키지로 이미 있음: app/auth/routes.py → | 엔드포인트 | `POST /auth/signup`(201)·`POST /auth/login`(200)·`POST /auth/logout`(2
| 모듈 | 푸시 구독 소유 — `save_subscription` 이 같은 endpoint 의 다른 사용자 행을 지운 뒤 upsert(결정 P
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 엔드포인트 | `POST·GET·DELETE /auth/mcp-token` — 201 `{token,created_at,expires_at}
WARN  registry 에 다른 패키지로 이미 있음: app/auth/deps.py → | 모듈 | 로그인 의존성 `current_user`(없거나 만료면 401 `unauthenticated`) · 시계 `get_auth_now`
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-tools | 4d58
| 엔드포인트 | POST /chat | app/api/routes.py | P5-loop | d5c8ec9 | 발화 1건 → 인식(LLM 1회
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 엔드포인트 | GET /persons · GET /persons/{person_id} (읽기 전용) | app/api/routes.py | 
| 엔드포인트 | GET /events/{event_id}/raw · GET /persons/{person_id}/facts/{fact_id}/
| 엔드포인트 | GET /questions/pending · GET /briefings (읽기 전용) | app/api/routes.py | 
| 모듈 | 계정 대화 세션 `chat_session_id(user)` = `chat:<user_id>` · 전 라우트 로그인 필수(`/heal
| 모듈 | 대화 기록 `append(session, user_id, role, content, question_id=None)`(flush 만
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
WARN  registry 에 다른 패키지로 이미 있음: app/api/read.py → | 모듈 | 읽기 전용 조회 `list_persons()`·`get_person_card()` · 상수 `TIMELINE_LIMIT=20`·`U
| 모듈 | 원문 조회 `get_event_raw()`·`get_fact_sources()` · 상수 `FACT_SOURCES_LIMIT=20`
| 모듈 | 브리핑 조회 `list_briefings()` · 상수 `BRIEFINGS_LOOKBACK_DAYS=7`·`BRIEFINGS_LIM
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools | 4d5817e | `AnswerIn`·`
| 엔드포인트 | GET /push/vapid-public-key · POST /push/subscriptions | app/api/routes
| 모듈 | 조회 응답 `PersonListItemOut`·`PersonBasicOut`·`PersonFactOut`·`PersonPattern
| 모듈 | 원문 응답 `EventRawOut`·`FactBriefOut`·`FactSourceEventOut`·`FactSourcesOut` 
| 모듈 | 브리핑 조회 응답 `BriefingRecordOut`·`BriefingScheduleOut`·`BriefingPersonOut` |
| API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 엔드포인트 | `GET /chat/history?limit=N`(1~200, 기본 50) → `ChatHistoryItemOut[]`(`id
| 설정 | 고정 사용자 폐지 — `app_user_id()`·`DEFAULT_APP_USER_ID`·`APP_USER_ID` 삭제(`tests
| 엔드포인트 | `GET /auth/availability`(로그인 불필요·`no-store`) · 가입 계약 `{username,passwo
| 엔드포인트 | `POST·GET·DELETE /auth/mcp-token` — 201 `{token,created_at,expires_at}
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/tools/context.py → | 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | 실행 맥락(`
| 모듈 | 대기 질문 소유 검사 — `answer_question`·`list_pending(ctx)` 가 `user_id == ctx.use
WARN  registry 에 다른 패키지로 이미 있음: app/tools/questions.py → | 모듈 | ask_user·answer_question·question_status | app/tools/questions.py | P2-to
| 모듈 | 대기 질문 소유 검사 — `answer_question`·`list_pending(ctx)` 가 `user_id == ctx.use
WARN  registry 에 다른 패키지로 이미 있음: app/tools/persons.py → | 모듈 | search_person·create_person·update_person | app/tools/persons.py | P2-too
WARN  registry 에 다른 패키지로 이미 있음: app/tools/records.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
WARN  registry 에 다른 패키지로 이미 있음: app/tools/briefing.py → | 모듈 | get_briefing | app/tools/briefing.py | P2-tools | 7c94aad | `person_facts
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/inputs.py → | 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 입력 조립(build_briefing_input) | app/briefing/inputs.py | P6-briefing | 
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/select.py → | 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 대상 선정(select_due_schedules) | app/briefing/select.py | P6-briefing | 
WARN  registry 에 다른 패키지로 이미 있음: app/briefing/scheduler.py → | 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 브리핑 패키지 진입점 재export | app/briefing/__init__.py | P6-briefing | e2155f9 | 
| 모듈 | 브리핑 1분 주기 작업(스케줄러) | app/briefing/scheduler.py | P6-briefing | a67692e | 
| 모듈 | 계정별 브리핑 주기 작업 — `default_run_once(now=None)` 이 창(`BRIEFING_LEAD_HOURS`, 호
WARN  registry 에 다른 패키지로 이미 있음: app/memory/promote.py → | 모듈 | 승격(미승격 이벤트 → person_facts upsert) | app/memory/promote.py | P6-memory | b
WARN  registry 에 다른 패키지로 이미 있음: app/memory/patterns.py → | 모듈 | 반복 패턴 감지(규칙, LLM·임베딩 0) | app/memory/patterns.py | P6-memory | d67d084 | 
WARN  registry 에 다른 패키지로 이미 있음: app/memory/direct_facts.py → | 모듈 | 루프 직접 사실 → 원문 링크(U7, 결정 G(ii)) | app/memory/direct_facts.py | P6-memory |
WARN  registry 에 다른 패키지로 이미 있음: app/memory/extract.py → | 모듈 | 사실 추출기(FactExtractor, 공급자 3종+가짜) | app/memory/extract.py | P6-memory | 48
WARN  registry 에 다른 패키지로 이미 있음: app/mcp_server/tools.py → | 모듈 | MCP 도구 본체 4개 `tool_list_people`·`tool_find_person`·`tool_get_person_card`
PASS  registry 중복 없음: tests/test_guard_rules.py
PASS  registry 중복 없음: tests/test_migration_0006.py
PASS  registry 중복 없음: tests/test_privacy_notice.py
PASS  registry 중복 없음: tests/test_guard_mask.py
PASS  registry 중복 없음: tests/test_guard_messages.py
PASS  registry 중복 없음: tests/test_guard_pre.py
PASS  registry 중복 없음: tests/test_guard_resume.py
PASS  registry 중복 없음: tests/test_guard_posthoc.py
PASS  registry 중복 없음: tests/test_guard_storage.py
PASS  registry 중복 없음: tests/test_guard_export.py
WARN  registry 에 다른 패키지로 이미 있음: tests/auth_helpers.py → | 테스트 | 로그인 테스트 도우미 `make_user(session, user_id="local")`·`logged_in_client(app,
| 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_api.py → | 테스트 | 인증 시험 — passwords·settings·api·origin (U2 117건 + 리뷰 보완 37건) | tests/test
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_nickname.py → | 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_availability.py → | 테스트 | 닉네임 가입 63건 · 중복 조회 38건 · 리비전 0004 8건 · 도우미 `make_user(..., *, nickname=N
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_origin.py → | 테스트 | 인증 시험 — passwords·settings·api·origin (U2 117건 + 리뷰 보완 37건) | tests/test
WARN  registry 에 다른 패키지로 이미 있음: tests/test_auth_required_routes.py → | 테스트 | 미로그인 401 계약(라우트 열거) 11건 · 계정 간 격리 21건(남의 id 응답 == 없는 id 응답, 남의 질문 답변 시 행
WARN  registry 에 다른 패키지로 이미 있음: tests/test_briefing_scheduler.py → | 테스트 | 1분 주기 작업 스위치·내구성·같은 함수 확인(U7) | tests/test_briefing_scheduler.py | P6-br
WARN  registry 에 다른 패키지로 이미 있음: tests/test_briefing_scheduler_users.py → | 모듈 | 계정별 브리핑 주기 작업 — `default_run_once(now=None)` 이 창(`BRIEFING_LEAD_HOURS`, 호
PASS  registry 중복 없음: web/src/lib/privacyNotice.ts
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/AuthScreen.tsx → | 모듈 | 로그인·가입 화면 `AuthScreen`·`AUTH_NOTICE`·`authFailureNotice`(한 화면 전환, 가입은 확인 
| 모듈 | `AuthScreen` 닉네임 칸·칸마다 "중복 확인"(`role=status`, `username-check`/`nickname-
WARN  registry 에 다른 패키지로 이미 있음: web/src/components/AppShell.tsx → | 앱 틀·라우팅 | `web/src/App.tsx` · `web/src/main.tsx` · `web/src/routes.ts`(`parseH
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
| 브리핑 화면 알림 버튼·인앱 배너 | `BriefingScreen.tsx` `PushSubscribe`(미구독 "알림 받기"/진행 "알림 켜
| 모듈 | 사이드바 계정 줄 `AccountRow`(아이디 · 로그아웃) · `getCurrentPushEndpoint()`(로그아웃 때 이 
| 모듈 | `AuthScreen` 닉네임 칸·칸마다 "중복 확인"(`role=status`, `username-check`/`nickname-
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/api/types.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
| 모듈 | `checkAvailability(q)` — 준 키만 쿼리에 싣는 `GET /auth/availability`, 401 에도 로그아
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/api/client.ts → | API 클라이언트·타입 | `web/src/api/client.ts`(`apiFetch`·`ApiError`·`API_BASE='/api'`
| 세션 보관·채팅 호출 | `web/src/session.ts`(`getSessionId`·`setSessionId`·`clearSession
| 인물 카드 화면 | `web/src/screens/PersonCardScreen.tsx`(`PersonCardScreen`·`CARD_NOT
| 브리핑 화면 | `web/src/screens/BriefingScreen.tsx`(`BriefingScreen`·`BRIEFING_NOTIC
| 푸시 구독 | `web/src/push.ts`(`subscribeToPush`·`getPushStatus`·`urlBase64ToUint8A
| 모듈 | 계정 API 클라이언트 `signup`·`login`·`getMe`·`logout(endpoint?)`·`getChatHistory
| 모듈 | `checkAvailability(q)` — 준 키만 쿼리에 싣는 `GET /auth/availability`, 401 에도 로그아
| 모듈 | MCP 토큰 클라이언트 `getMcpToken`·`createMcpToken`·`deleteMcpToken` · 타입 `McpTok
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/ChatScreen.tsx → | 채팅 화면 | `web/src/screens/ChatScreen.tsx`(`ChatScreen`·`NOTICE` 고정 안내 문장 5개 — 빈
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
| 모듈 | 사이드바 계정 줄 `AccountRow`(아이디 · 로그아웃) · `getCurrentPushEndpoint()`(로그아웃 때 이 
WARN  registry 에 다른 패키지로 이미 있음: web/src/screens/PersonCardScreen.tsx → | 인물 카드 화면 | `web/src/screens/PersonCardScreen.tsx`(`PersonCardScreen`·`CARD_NOT
| 인물 목록 단일 조회 | `web/src/components/PersonsProvider.tsx`(`PersonsProvider`·`useP
PASS  registry 중복 없음: web/src/lib/labels.ts
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/auth.test.tsx → | 테스트 | 프론트 로그인 시험 — `auth.test.tsx` 22건 + `api.test`·`chat.test` 신규 11건(Vitest 
| 테스트 | 가입 닉네임·중복 확인 시험 — `auth.test.tsx` 새 describe + `api.test.ts` 2건(Vitest 1
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/chat.test.tsx → | 테스트 | 채팅 테스트 21건 — 세션 헤더·저장·422 버림·Enter/Shift+Enter·타이핑 점·칩 글자/순서/선택 고정/이어 붙임
| 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
WARN  registry 에 다른 패키지로 이미 있음: web/src/__tests__/card.test.tsx → | 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
| 테스트 | 브리핑 테스트 16건(`briefing.test.tsx` — 서버 순서·머리줄 3요소·문자열 동일(특수문자·공백)·basis 미표
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
PASS  registry 중복 없음: web/src/__tests__/labels.test.tsx
PASS  registry 중복 없음: web/src/__tests__/notice.test.tsx
PASS  registry 중복 없음: reports/sensitive_guard.md
PASS  registry 중복 없음: reports/sensitive_guard_metrics.json
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
WARN  registry 에 다른 패키지로 이미 있음: docs/user-setup/13-user-todo-deploy.md → | 문서 | EC2 최소 구성 배포 절차(신규 계정 Free Plan·Budgets·키 페어·보안 그룹·t4g.small·EIP·Docker·`
PASS  registry 중복 없음: docs/wiki/packages/P9d-sensitive-guard/03-log.md
WARN  registry 에 다른 패키지로 이미 있음: tests.md → | 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
| 문서 | 테스트 기록 — 프론트 Vitest 135건·E2E 4건을 표 1줄씩(무엇을 확인·입력 → 기대·결과·검출한 변이 ID), 총계와 
| 테스트 | 배포 파일 텍스트 검사 **19건** — compose `name`·서비스 3·postgres/backend `ports` 0·`
WARN  registry 에 다른 패키지로 이미 있음: 04-review.md → | 문서 | P4b 완료 검토와 그 검증 증거(게이트 독립 재계산·부정 케이스 18건·D12/D13 grep·회귀 3종 재확인·경계 확인·ver
PASS  registry 중복 없음: app/guard/messages.py
PASS  registry 중복 없음: tests/test_guard_messages.py
PASS  registry 중복 없음: web/src/lib/privacyNotice.ts
PASS  registry 중복 없음: web/src/__tests__/notice.test.tsx
PASS  registry 중복 없음: test_privacy_notice.py
PASS  registry 중복 없음: notice.test.tsx
== 결과: FAIL=0 WARN=47 ==
```
2차의 WARN 47 = registry 46 + `보류 1 건`(점검표 3행). FAIL 0 이지만 보류가 있어 결과는 통과가 될 수 없다.

WARN 46건 가운데 registry 줄은 전부 "registry 에 다른 패키지로 이미 있음" 이다 — 이 계획이 기존 파일을 **고치는** 목록(`app/agent/loop.py` 등)이라 나오는 줄이고, 새로 만드는 파일(`app/guard/*`·`tests/test_guard_*`·`evaluation/sensitive_guard/*`·`alembic/versions/0006_sensitive_guard.py`)은 전부 `PASS  registry 중복 없음` 이다. 중복 구현 소견이 아니다(P9b-auth 02-plan-verify 와 같은 해석). 05-remediation 은 만들지 않았다 — 아래 3절 소견은 계획 문서(architect)가 고칠 것이라 여기에 원인과 고칠 자리를 적는다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")

**재검증(3회차) — 01-plan 개정 2 기준. 행 번호는 개정 2 의 것이다. 2회차에서 통과였던 행은 개정 2 가 바꾼 자리만 다시 보고 나머지 근거는 2.0.1절 그대로다.**

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 63~70행 범위 표 제외 칸 "고민 상담 기능 · 인물 간(A–B) 관계 저장 · 관계 태그 필터링 · 상담 페르소나 / 톤 설정 · 음성 입력 · 네이티브 앱". 01-plan 31행 "이 패키지에서 하지 않는 것: … 새 화면(재고지는 기존 화면 위 모달 — 원칙5, G14) · 법적 판단·약관 내용 단정 · … 인물 간 관계·상담(원칙7) · 툴 7종의 개수·시그니처 변경 · `app/er/` 판정 로직 변경 · 계정 삭제 · MCP 도구 추가" — 개정 2 에서 그대로다. 개정 2 가 더한 것은 닫힌 시험 목록·수용 기준 문장·내부 함수(`legacy_resume_blocked`·`_pending_calls_from` 의 `excluded` 인자·`ResolveOutcome.name_rule_dropped`)뿐이고 화면·사용자에게 보이는 문구는 더하지 않았다: U9a 수용 기준(227행) "새 라우트(화면) 0", 채팅 문구는 `D20-sensitive-guard.md` 확정 문구 글자 그대로(63행 "단언 = D20 '확정 문구' 와 글자 일치 + `BRIEFING_FORBIDDEN_EXPRESSIONS` 어느 항목도 포함하지 않음") |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1·2: 2회차 N-R3 이 카드에 들어갔다 — `D20-sensitive-guard.md` R-7 "**단 하나의 판정 뒤 갈래(사용자 결정 D-4)**: 결정 22 로 통과한 언급이 별칭 주인이 아닌 인물로 자동 연결되거나 새 인물(`< T_new`)로 판정되면, `resolve()` 가 확신도를 낸 **뒤** 그 언급을 `ask_user` 없이 버린다 — 병합·생성·질문이 모두 0 이라 오병합(원칙1)이 생기지 않고 미검출 쪽으로만 기운다. 원칙2 의 글자(…)와 다른 이 갈래는 사용자가 고른 동작(D-4 (a))이며, 그 언급의 `er_resolve` trace 는 `applied` 가 거짓으로 남는다" ↔ 01-plan 215행 수용 기준 "trace `dropped_non_owner`, 그 언급의 `er_resolve` trace 는 `applied` 가 거짓으로 남는다 — 조회 턴 1322행과 같은 모양, N-R3". 원칙4: `app/er/` 무수정(209·216행 `u7a-er-unchanged`·`u7b-er-unchanged` 빈 출력) — 개정 2 의 M5 수정이 "임베더 호출은 후보 검색 질의뿐" 으로 바뀌어 `search_person`·`app/er/` 를 고칠 이유가 없어졌다. 원칙5: 227행. 원칙6: `D14-pattern-window-config.md` 15행 "민감 표시된 사건 … 은 패턴 횟수에 세지 않는다" ↔ U7a(206행). 원칙8: 143행 U1 test 동결, 151행 "목록은 backend-agent 가 dev 세트만 보고 귀납(test 파일을 여는 코드·명령 0)", 152행 "U2 시점 러너는 `--split test` 를 거부". 원칙9: 74행 `guard_name_rule` trace(결정값 4종·규칙 id·제안 인덱스, 언급 문자열 0), 179행 `guard_check` trace, 201행 사후 긍정 재개의 `loop_*` step 순서(`loop_gate` 가 재개 턴에 하나 더 남는다 — 판정 근거가 느는 쪽) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | 2회차 M5 가 닫혔다. `D20-sensitive-guard.md` 결정 22 "기존 별칭 자체는 인물 판정 때 OpenAI 로 계속 전송된다(사용자가 알고 고름)" · R-7 "별칭 저장(`_add_alias`)은 같은 글자 행이 있으면 새 행·임베딩을 만들지 않으므로 **새로 저장되는 이름이 없다**" ↔ 01-plan 215행 "**별칭 저장용 임베딩 0**(개정 2 — M5): 임베딩이 있는 기존 별칭 + 가짜 임베더를 붙인 그 턴에서 임베더 호출은 **후보 검색 질의뿐**이고(… `app/tools/persons.py:214`, D20 결정 22 가 받아들인 전송) 호출 횟수가 같은 인물을 민감 낱말 없는 기존 별칭으로 부른 턴과 같으며, `person_aliases` 행 수와 그 행의 `embedding` 값이 그대로". 코드 대조(3.A.1 H3): `app/tools/persons.py:214` `query_vector = provider.embed([q])[0]`(그 사용자에게 임베딩이 있는 별칭이 1개 이상일 때만), 364~372행 `_add_alias` 는 `PersonAlias.person_id == person.id` · `PersonAlias.alias == alias` 행이 없을 때만 `provider.embed([alias])` — 단언은 카드·코드와 맞고 가짜 임베더의 호출 횟수·`person_aliases` 행으로 기계 판정된다. 나머지 D 카드는 2회차 그대로 맞다: `D02-ask-user-async.md` "사전 동의 질문 … 은 라우트가 `ask_user` **툴을 부르지 않고**" ↔ U5b(185행), `D16-query-turn.md` "`get_person_card(include_sensitive=False)`" ↔ U8(220행), `D18-login-user-isolation.md` "`_EXEMPT` 무변경" ↔ U4(173행), `D19-mcp-read-token.md` "`sensitive_category` 키는 빼서 낸다" ↔ U8(221행 — 개정 2 가 `tests/test_mcp_tools.py:293` 비교 대상을 그 키를 뺀 덤프로 바꾼다고 적었다), `D17-vercel-deploy.md` "백업 → 0006 → 재배포 → 바깥 확인 → 기존 가입자 재고지 실제 확인" ↔ U12(249행). 카드 안의 낡은 문장 1건은 권고 P3-R5(3.A.5) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.1-schema-v2.md` 53~57행 "events(+ sensitive_category, + consent_question_id) … person_facts(+ sensitive_category) … schedules(+ sensitive_category) … users(+ privacy_notice_version, + privacy_notice_accepted_at) … pending_questions.kind CHECK … 4종" ↔ 01-plan 159~160행(컬럼 79 → 85 · nullable 이름 집합 7 → 11 · CHECK 5 → 8 · `QUESTION_KINDS` 3 → 4 — 2회차 G6 에서 직접 센 값과 같다). 개정 2 가 더한 U3 줄은 코드와 같다(3.A.1 H1): `tests/test_api.py:93` `assert body["alembic_revision"] == "0005"` ↔ 164행, `tests/test_migration_0004.py:110` `mig["columns_before"] == USERS_COLUMNS - {"nickname"}`·157행 ↔ 163행. `S3.2-tools-v2.md` "툴 7종의 **개수·시그니처는 그대로**(`tools_check` 7/7)" ↔ 207행(표시는 툴이 `ctx.consent` 를 읽는 한 곳), 개정 2 의 `_pending_calls_from(…, excluded=…)`·`legacy_resume_blocked` 는 툴이 아니다. `S3.4-ask-user-protocol.md` "프로토콜(저장 → 턴 종료 → 칩 → 재개)은 그대로" ↔ 193행 — `answer_question` 은 고치지 않고 그 앞에서 읽기만 하는 사전 검사를 둔다(코드 대조 3.A.1 H4: `submit_answer` 는 `build_ctx` → `answer_question` → `load_resume_input` 순서이고 세션·질문 id·사용자·`ctx.now()` 가 `answer_question` 앞 자리에 이미 있다). `S3.5-memory-promotion.md` "`COALESCE(기존, 이번 쓰기의 범주)` 로만" ↔ 206행. `S3.6-briefing-push.md` ④ "사용자 반복 밖 독립 단계" ↔ 192행. `S3.7-eval-spec.md` 크기·역할 ↔ U1·U2·U10. 임계치 `T_merge`·`T_new` 를 건드리는 파일은 없다 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 04-review 의 `결과: 완료` 줄과 닫은 커밋(1차 확인 그대로): P5-loop `f9bfba7` · P5b-query-turn `f67d8e4` · P6-memory `94373cc` · P6-briefing `f9500fe` · P7-push `50fd7fc` · P4 게이트 = P4b-er-redesign `1075dd6`. U0 `6d97217` 은 `gitlog.sh P9d-sensitive-guard CR-009` 두 태그 칸에 있다(3.A.1 H0 — dev2 = origin/dev2, 제품 코드 미커밋 변경 0). 단위 순서 그림(129~135행)과 각 단위 `의존:` 은 개정 2 에서 바뀌지 않았다. 개정 2 가 더한 닫힌 목록은 그 단위가 스스로 깨뜨리는 시험만 담는다(U5a `test_agent_query_gate.py` · U6 `test_agent_query_types.py` · U8 `test_api_read_persons.py`·`test_mcp_tools.py`) — 앞 단위의 산출물을 당겨 쓰지 않는다. verify-plan `PASS  의존 완료` 4줄(1.1.2절) |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P9d 행 `수용기준:` 뒤 문자열과 01-plan 255행을 스크립트로 다시 비교 — 571자, 계획 문자열이 backlog 행 안에 그대로 있다(3.A.1 H9 `571 True`). 개정 2 는 그 줄을 건드리지 않았다. verify-plan `PASS  backlog 일치: **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)**` |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan `PASS  Refs 있음` 17줄(U0·U1·U2·U3·U4·U5a·U5b·U5c·U6·U7a·U7b·U8·U9a·U9b·U10·U11·U12 — 1.1.2절). 2회차 N-R8 반영: 머리 태그 줄(4행) "기대는 결정: D20(신설) · D1 · D2 · …" 에 `D1` 이 들어갔고 verify-plan `PASS  카드 존재: D1` |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` 72행 "(CR-009 · D20, 2026-11-22) **민감 정보 가드레일**: LLM 호출 전 서버 규칙 검사 — … 민감 범주는 칩 동의 전 OpenAI 호출 0. 동의 대기 중 원문은 `pending_questions.context`·`chat_messages` 한 줄에만" ↔ U5b 수용 기준(187행)·U2 `u2-no-log`(153행). 외부 전송: 실 OpenAI 호출은 U6·U10 "사용자 지시 뒤"(202·240행), U10 상한 D-3 확정 $1. U1 "**식별번호 모양 문자열은 전부 지어낸 값** … 우회하지 않고 문장을 바꾼다(`security.md` 6절)"(143행), U12 "백업 복원은 … 데이터 삭제를 동반하므로 **사용자가 직접 실행**한다(`security.md` 6절) … 에이전트는 실행하지 않는다"(250행), 공통 회귀 "증거에 원문 민감 문장을 그대로 남기지 않는다"(278행). 개정 2 가 더한 거절 경로 변이(196·203행 "거절 처리를 `resume_turn` **안**으로 옮기기 → 거절 뒤 trace 전수 `LIKE` FAILED")는 거절한 원문이 trace 에 남지 않음을 지키는 쪽이다 |

### 2.0.1 2회차 점검표 (이력 — 01-plan 개정 1 기준. 행 번호는 개정 1 의 것)

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 2차-1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 63~70행 범위 표 제외 칸 "고민 상담 기능 · 인물 간(A–B) 관계 저장 · 관계 태그 필터링 · 상담 페르소나 / 톤 설정 · 음성 입력 · 네이티브 앱". 01-plan 31행 "이 패키지에서 하지 않는 것: … 새 화면(재고지는 기존 화면 위 모달 — 원칙5, G14) · 법적 판단·약관 내용 단정 · … 인물 간 관계·상담(원칙7) · 툴 7종의 개수·시그니처 변경 · `app/er/` 판정 로직 변경 · 계정 삭제 · MCP 도구 추가" — 개정 1 에서 그대로다. 개정 1 이 더한 화면·문구는 없다: U9a 수용 기준(194행) "새 라우트(화면) 0", 채팅 문구는 `D20-sensitive-guard.md` 확정 문구 ①~⑥·부속("이름 거부 '그 표현은 이름으로 기억하지 않아요. 이름이나 호칭으로 다시 말해 주세요.'") 글자 그대로이고 01-plan 60행이 "`BRIEFING_FORBIDDEN_EXPRESSIONS` 어느 항목도 포함하지 않음" 을 단언으로 둔다. 새 이름 거부 갈래(`dropped_non_owner`·`dropped_no_consent`)도 같은 부속 문구를 쓴다(새 문구 0) |
| 2차-2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1: 개정 1 의 D-4 확정안은 병합을 줄이는 쪽이다 — `D20-sensitive-guard.md` 갱신 이력 "통과한 기존 별칭 표현이 별칭 주인이 아닌 인물·새 인물로 해석되면 기록하지 않고 이름 거부 안내" ↔ 01-plan 71행 "merge·new_person 밴드는 `apply_resolution`·되묻기 **전에**(⑤ 자리) 그 언급을 이름 거부". 원칙2: 확신도 ≥ `T_merge` 인데도 연결하지 않는 것은 "≥ `T_merge` **만** 자동 연결"(CLAUDE.md 원칙2)과 어긋나지 않는다. 다만 ⑤ 자리는 `resolve()` **뒤**라 `D20-sensitive-guard.md` R-7 "이것은 확신도 판정 **이전**의 제외이며 … (판정이 일어나지 않는다)" 문장이 그 갈래에는 맞지 않는다 — 판정은 일어나고 `< T_new` 인데 `ask_user` 없이 버린다. 사용자가 D-4 로 직접 고른 동작이고 병합·생성이 0 이라 위반으로 보지 않되, 카드 문장을 맞춘다(3.0.5 권고 N-R3). 원칙4: `app/er/` 무수정(177·183행 `u7a-er-unchanged`·`u7b-er-unchanged` 빈 출력). 원칙5: 194행. 원칙6: `D14-pattern-window-config.md` 15행 "민감 표시된 사건 … 은 패턴 횟수에 세지 않는다" ↔ U7a `app/memory/patterns.py`(173행). 원칙8: 109행 "test 는 U2 착수 전 동결", 119행 "목록은 backend-agent 가 dev 세트만 보고 귀납(test 파일을 여는 코드·명령 0)", 120행 "U2 시점 러너는 `--split test` 를 거부", 빈자리 ①(83행) "시간 상한 수는 두지 않는다 … 시간 상한은 기기마다 흔들린다". 원칙9: 71행 `guard_name_rule` trace(결정값 4종·규칙 id·제안 인덱스, 언급 문자열 0), 146행 `guard_check` trace, trace 덮어쓰기는 `D20-sensitive-guard.md` R-3 "trace 를 덮어쓰는 **유일한** 자리는 `app/guard/consent.py::redact_declined`" 로 한정. 미동의 건너뜀 trace 0(72행)은 `S3.6-briefing-push.md` 가 계획에 넘긴 자리이고 `CR-009.md` 9절 반영표가 "4.2 U4 의 … 문장은 **이력**이 됐다" 로 맞췄다 |
| 2차-3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 보류 | 1차 M4 는 닫혔다 — `D20-sensitive-guard.md` R-7 "언급이 그 사용자의 이미 저장된 별칭과 **글자까지 같으면**(정규화 없음 — 공백·대소문자만 다른 변형은 이름 거부) 이름 규칙을 통과한다. 별칭 저장(`_add_alias`)은 같은 글자 행이 있으면 새 행·임베딩을 만들지 않으므로 **새로 저장되는 이름이 없다**" ↔ 01-plan 71행·182행, 코드 `app/tools/persons.py:364~372`(`PersonAlias.alias == alias` 로 찾고 없을 때만 `provider.embed([alias])`). **새 충돌 1건**: `D20-sensitive-guard.md` 결정 22 "기존 별칭 자체는 인물 판정 때 OpenAI 로 계속 전송된다(사용자가 알고 고름)" — 통과한 언급은 ER 후보 검색을 탄다(`app/er/candidates.py:41` → `app/tools/persons.py:214` `query_vector = provider.embed([q])[0]`, 그 사용자에게 임베딩이 있는 별칭이 1개라도 있으면 언급 문자열을 임베딩한다). 그런데 01-plan 182행 수용 기준은 "별칭 임베딩 호출 0(**가짜 임베더 호출 인자에 그 문자열 0**)" 이다 — 카드가 받아들인 전송(후보 검색 질의)을 0 으로 단언해, `app/er/`·`search_person` 을 고치지 않고는 성립하지 않는다 → 3.0.4 M5. 나머지 D 카드는 맞음: `D02-ask-user-async.md` "사전 동의 질문 … 은 라우트가 `ask_user` **툴을 부르지 않고**" ↔ U5b(152행), `D16-query-turn.md` "`get_person_card(include_sensitive=False)`" ↔ U8(187행), `D18-login-user-isolation.md` "`_EXEMPT` 무변경" ↔ U4(140행), `D19-mcp-read-token.md` "`sensitive_category` 키는 빼서 낸다" ↔ U8(188행), `D17-vercel-deploy.md` "백업 → 0006 → 재배포 → 바깥 확인 → 기존 가입자 재고지 실제 확인" ↔ U12(216행). D20 ① 표 #6·#7·#10b·#13·#14 의 판정 명령·단위 칸은 개정 1 과 같게 고쳐져 있다(`u7a-chain`·`u7a-monotone`·`u7b-name-rule`·`notice.test.tsx`·`test_migration_0006.py`) |
| 2차-4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.1-schema-v2.md` 53~57행 "events(+ sensitive_category, + consent_question_id) … person_facts(+ sensitive_category) … schedules(+ sensitive_category) … users(+ privacy_notice_version, + privacy_notice_accepted_at) … pending_questions.kind CHECK … 4종" ↔ 01-plan 127~128행. 개정 1 의 새 값을 `tests/test_schema_models.py` 에서 직접 셌다: 총 컬럼 79(164~165행) + 6 = **85** · `NULLABLE_COLUMNS`(88~96행, 이름 집합 7개) + 새 이름 4개 = **11** · CHECK 총 5(223행, 세는 테이블 목록에 `events`·`person_facts`·`schedules` 가 있다) + 3 = **8** · `QUESTION_KINDS` 3(210행) → **4** — 넷 다 계획과 같다. FK 9·인덱스 13·UNIQUE 8 은 0006 이 더하지 않아 그대로(`consent_question_id` 는 "BIGINT NULL(FK 없음)"). `S3.2-tools-v2.md` "툴 7종의 **개수·시그니처는 그대로**(`tools_check` 7/7)", "**툴이 그것을 읽어 기록하는 같은 INSERT/upsert 문에서** `sensitive_category` … 를 채운다" ↔ 173~174행(1차 R-2 닫힘). `S3.4-ask-user-protocol.md` "조회는 언급 해석 단계부터 다시 돈다(… 기존 identity 답 전용 조회 재개 경로를 쓰지 않는다)" ↔ 67행 VR1(`_continue_after_gate` → `_run_query_turn`). `S3.5-memory-promotion.md` "`COALESCE(기존, 이번 쓰기의 범주)` 로만" ↔ 173행. `S3.6-briefing-push.md` ④ "사용자 반복 밖 독립 단계" ↔ 159행. `S3.7-eval-spec.md` 크기·역할 ↔ U1·U2·U10. 임계치 `T_merge`·`T_new` 를 건드리는 파일은 없다. 스키마 고정 단언을 가진 **시험 파일 목록**이 덜 닫힌 것(`tests/test_api.py:93`)은 카드 일치가 아니라 단위 실행 가능성 문제라 3.0.4 M2-잔여로 둔다 |
| 2차-5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 04-review 의 `결과: 완료` 줄과 닫은 커밋(1차 확인 그대로): P5-loop `f9bfba7` · P5b-query-turn `f67d8e4` · P6-memory `94373cc` · P6-briefing `f9500fe` · P7-push `50fd7fc` · P4 게이트 = P4b-er-redesign `1075dd6`. U0 `6d97217` 은 `gitlog.sh P9d-sensitive-guard CR-009` 두 태그 칸에 있다(3.0.1 G1). `docs/backlog.md` P9d 행이 P9b-auth 를 선행 완료 조건에서 뺐다("메인 세션 결정 — 닫지 않고 둔다"). 단위 순서(97~105행): U7b 는 U7a 뒤("U7b 는 U7a 의 `ctx.consent` 복원·표시 전파에 기댄다"), U8 은 U7b 뒤(같은 `loop.py`), U9a 는 U4 뒤, U10 은 U2·U6 뒤 — U10 의 "이름 규칙 오탐 표" 가 쓰는 `name_allowed` 는 U2 산출물이라 U7b 에 기대지 않는다. backlog P9d `단위:` 줄도 U7a·U7b 로 고쳐져 있다. verify-plan `PASS  의존 완료` 4줄(1.1절) |
| 2차-6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P9d 행 `수용기준:` 뒤 문자열과 01-plan 222행을 스크립트로 다시 비교 — `571 571 True`(3.0.1 G9). 개정 1 은 backlog 의 `단위:` 줄과 결정 22 줄만 바꿨고 수용기준 문자열은 그대로다. verify-plan `PASS  backlog 일치: **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)**` |
| 2차-7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan `PASS  Refs 있음` 17줄(U0·U1·U2·U3·U4·U5a·U5b·U5c·U6·**U7a·U7b**·U8·U9a·U9b·U10·U11·U12 — 1.1절). 태그가 가리키는 카드는 `PASS  카드 존재`. U7b Refs 의 `D1` 은 머리 태그 줄(4행 "기대는 결정")에 없으나 카드 `D01-new-person-confirm.md` 는 있다(사소 — 3.0.5 N-R8) |
| 2차-8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` 72행 "(CR-009 · D20, 2026-11-22) **민감 정보 가드레일**: LLM 호출 전 서버 규칙 검사 — … 민감 범주는 칩 동의 전 OpenAI 호출 0. 동의 대기 중 원문은 `pending_questions.context`·`chat_messages` 한 줄에만" ↔ U5b 수용 기준(154행)·U2 `u2-no-log`(121행). 외부 전송: 실 OpenAI 호출은 U6·U10 "사용자 지시 뒤", U10 상한 D-3 확정 $1(207행). 개정 1 이 더한 것: U1 "**식별번호 모양 문자열은 전부 지어낸 값** … Write 단계 `secret-guard`·`save_evidence` 비밀 패턴에 걸리면 우회하지 않고 문장을 바꾼다(`security.md` 6절)"(111행), U12 "백업 복원은 … 데이터 삭제를 동반하므로 **사용자가 직접 실행**한다(`security.md` 6절) … 에이전트는 실행하지 않는다"(217행), 백업 파일은 "서버에만"(216행), 증거는 "값·토큰 0"(218행), 공통 회귀 "증거에 원문 민감 문장을 그대로 남기지 않는다"(245행) |

### 2.1 1차 점검표 (이력 — 01-plan 개정 전 기준. 행 번호는 개정 전 계획의 것)

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1차-1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 63~70행 범위 표 제외 칸 "고민 상담 기능 · 인물 간(A–B) 관계 저장 · 관계 태그 필터링 · 상담 페르소나 / 톤 설정 · 음성 입력 · 네이티브 앱". 01-plan 29행 "이 패키지에서 하지 않는 것: … 새 화면(재고지는 기존 화면 위 모달 — 원칙5, G14) · 법적 판단·약관 내용 단정 · … 인물 간 관계·상담(원칙7) · 툴 7종의 개수·시그니처 변경 · `app/er/` 판정 로직 변경 · 계정 삭제 · MCP 도구 추가". `docs/proposal.md` 23행 상단 안내 "가드레일은 상담이 아니다 — 보낼지·저장할지만 묻는다". 가드 문구는 `D20-sensitive-guard.md` 확정 문구 ①~⑥ 글자 그대로이고 01-plan 56행이 "`BRIEFING_FORBIDDEN_EXPRESSIONS` 어느 항목도 포함하지 않음" 을 단언으로 둔다 |
| 1차-2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1·2·4: `D20-sensitive-guard.md` R-7 "이것은 확신도 판정 **이전**의 제외이며 병합·생성·질문 어느 것도 하지 않는다 — '임계치 미만은 반드시 `ask_user`' 의 예외가 아니다" ↔ 01-plan 64행 VR2(걸린 언급의 제안을 `rejected` 로 옮긴 새 `GateVerdict`, `app/er/` 무수정 — 151행 `u7-er-unchanged`). 원칙3: 확신도·임계치 손대지 않음(산출물 목록에 `app/er/` 0). 원칙5: 01-plan 162행 "새 라우트(화면) 0". 원칙6: `D14-pattern-window-config.md` 15행 "민감 표시된 사건 … 은 패턴 횟수에 세지 않는다" ↔ U7 `app/memory/patterns.py`. 원칙7: 1행 근거. 원칙8: 01-plan 91행 "test 는 U2 착수 전 동결", 101행 "목록은 backend-agent 가 dev 세트만 보고 귀납", 174행 "규칙 수치와 LLM 수치가 같은 표에 없음". 원칙9: 01-plan 67행 `guard_name_rule` trace·121행 `guard_check` trace, trace 덮어쓰기는 `D20-sensitive-guard.md` R-3 "trace 를 덮어쓰는 **유일한** 자리는 `app/guard/consent.py::redact_declined`" 로 한정. 미동의 건너뜀을 trace 없이 두는 것(68행)은 `S3.6-briefing-push.md` 12행 "건너뛰는 자리·trace 빈도는 P9d 01-plan" 이 넘긴 자리다(권고 R-3) |
| 1차-3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 보류 | `D20-sensitive-guard.md` R-7 "언급이 그 사용자의 이미 저장된 별칭과 **정확히 일치**(정규화 = … `name_key` …)하면 이름 규칙을 통과한다 — **새로 저장되는 이름이 없다**". 01-plan 67행·150행은 `name_key` 일치면 통과시키고 ER 로 넘기는데, 별칭 저장은 글자 그대로 비교한다(`app/tools/persons.py::_add_alias` — `PersonAlias.alias == alias`, 없으면 임베딩 호출 뒤 INSERT). 공백·대소문자만 다른 언급("마약쟁이형" ↔ 저장된 "마약쟁이 형")은 통과 → merge → `app/er/pipeline.py` 의 `update_person(new_alias=mention)` 으로 **민감 낱말이 든 새 별칭 행 + 임베딩**이 생긴다. 수용 기준에 "통과 턴의 `person_aliases` 새 행 0" 단언이 없다 → 3절 M4. 나머지 D 카드는 맞음: `D02-ask-user-async.md` 13행 "사전 동의 질문 … 은 라우트가 `ask_user` **툴을 부르지 않고**" ↔ U5b, `D16-query-turn.md` 40행 "`get_person_card(include_sensitive=False)`" ↔ U8, `D18-login-user-isolation.md` 46행 "`_EXEMPT` 무변경" ↔ U4, `D19-mcp-read-token.md` 42행 "`sensitive_category` 키는 빼서 낸다" ↔ U8, `D17-vercel-deploy.md` 37행 "백업 → 0006 → 재배포 → 바깥 확인 → 기존 가입자 재고지 실제 확인" ↔ U12 |
| 1차-4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.1-schema-v2.md` 53~57행(세 표 `sensitive_category`·`events.consent_question_id` FK 없음·`users` 두 컬럼·kind CHECK 4종) ↔ 01-plan 108행 "S3.1 보충 그대로". `S3.2-tools-v2.md` 18행 "툴 7종의 **개수·시그니처는 그대로**(`tools_check` 7/7)" ↔ 01-plan 148행 "시그니처 불변"·판정 표 12행. `S3.4-ask-user-protocol.md` 16행 이하 "프로토콜(저장 → 턴 종료 → 칩 → 재개)은 그대로", "조회는 언급 해석 단계부터 다시 돈다(… 기존 identity 답 전용 조회 재개 경로를 쓰지 않는다)" ↔ 01-plan 63행 VR1(`_run_query_turn`, `_resume_query_turn` 미사용). `S3.5-memory-promotion.md` 10행 "`COALESCE(기존, 이번 쓰기의 범주)` 로만" ↔ U7. `S3.6-briefing-push.md` 12행 ④ "사용자 반복 밖 독립 단계" ↔ U5c. `S3.7-eval-spec.md` 11행 크기·역할 ↔ U1·U2·U10. 임계치 T_merge·T_new 는 건드리는 파일 없음. 표현 차이 1건은 권고 R-2(S3.2 "기록 직후 같은 트랜잭션에서 채운다" ↔ 계획은 툴이 `ctx.consent` 를 읽는다) |
| 1차-5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 04-review 의 `결과: 완료` 줄과 닫은 커밋: P5-loop 196행 `f9bfba7` · P5b-query-turn 244행 `f67d8e4` · P6-memory 152행 `94373cc` · P6-briefing 267행 `f9500fe` · P7-push 185행 `50fd7fc` · P4 게이트 = P4b-er-redesign 144행 `1075dd6`. U0(문서 이행) `6d97217` 은 `gitlog.sh P9d-sensitive-guard D20 CR-009` 태그 검색 세 칸 모두에 있다. P9b-auth·P9-infra 는 아직 닫히지 않았으나 `docs/backlog.md` 110행이 선행 조건에서 뺐다("닫지 않고 둔다"). 단위 순서는 `CR-009.md` 4.2 의존 그림과 같다(01-plan 79~86행). verify-plan `PASS  의존 완료` 4줄 |
| 1차-6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 110행 `수용기준:` 뒤 문자열과 01-plan 189행을 스크립트로 비교 — 둘 다 571자, 같음. verify-plan `PASS  backlog 일치: **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)**` |
| 1차-7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan `PASS  Refs 있음` 16줄(U0·U1·U2·U3·U4·U5a·U5b·U5c·U6·U7·U8·U9a·U9b·U10·U11·U12). 태그가 가리키는 카드 D2·D5·D14·D16·D17·D18·D19·D20 과 검증 항목 R7·R12·R19 는 `PASS  카드 존재`·`PASS  검증 항목 존재` |
| 1차-8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` 5절 CR-009 줄 "가드 모듈은 원문을 로그·예외 메시지에 싣지 않는다" ↔ 01-plan 102~103행(`u2-no-log`). "동의 대기 중 원문은 `pending_questions.context`·`chat_messages` 한 줄에만" ↔ U5b 수용 기준. 외부 전송: 실 OpenAI 호출은 U6·U10 "사용자 지시 뒤", U10 은 상한 $1(01-plan 235행 D-3 확정). 운영 백업 파일은 "파일은 서버에만"(183행), 증거는 "값·토큰 0"(185행), 공통 회귀 "증거에 원문 민감 문장을 그대로 남기지 않는다"(212행). 되돌리기는 downgrade 가 실패하면 "멈추고 사용자에게 묻는다"(184행) — 삭제·복원을 에이전트가 스스로 하지 않는다. 시험 세트의 식별번호 모양 문자열은 권고 R-12 |

## 3. 보류 소견과 조치

### 3.A 재검증(3회차) — 01-plan 개정 2

05-remediation 은 만들지 않았다(verify-plan FAIL 0, 남은 것은 [권고]뿐 — 고칠 자리는 3.A.5 에 적는다). 아래 행 번호는 개정 2 의 01-plan 과 `6d97217` 의 코드 기준이다. 계획·카드·코드는 고치지 않았다.

#### 3.A.1 직접 실행한 확인

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| H0 | `bash .claude/scripts/gitlog.sh P9d-sensitive-guard CR-009` · `git status --short` | 두 태그 모두 `6d97217` 1건. dev2 = origin/dev2. 미커밋은 문서(backlog·CURRENT·HANDOFF·CR-009·D20·journal·S3.2)와 이 패키지 폴더뿐 — 제품 코드·시험 변경 0 |
| H1 | `tests/test_api.py` 88~95행 · `tests/test_migration_0004.py` 36~42·106~112·154~158·166~170행 읽기 · `grep -rnE "['\"]000[3-6]['\"]\|alembic_revision" tests scripts evaluation app web/src web/e2e` | `tests/test_api.py:93` `assert body["alembic_revision"] == "0005"  # P9b-auth U12 -- 0005(CR-008)`. `tests/test_migration_0004.py:110` `assert mig["columns_before"] == USERS_COLUMNS - {"nickname"}`(0003 상태) · 111·169행 head · 157행 0003 상태. 리비전 리터럴은 `test_api.py:93`·`test_migration_0005.py:110·111·196`(head)과 0003·0004 를 **목적지**로 쓰는 줄(`0004.py:66·154·156`·`0005.py:69·189·191`)뿐 — 계획 표와 같다. `web/`·`scripts/`·`evaluation/` 에는 0건 |
| H2 | `grep -rnE "set\(…\) ==\|keys\(\)\) ==" tests`(키 집합 동등 비교 전부) · `grep -rnE "json\(\) == \{" tests/test_auth_*.py` · `tests/test_auth_nickname.py` 60~88행 · `tests/test_auth_helpers.py` 96~106행 · `tests/test_auth_api.py` 86~100행 읽기 | 계획이 든 `test_auth_api.py:96`·`test_auth_nickname.py:70`(`set(body) == {"id", "username", "nickname"}`)은 실재. **계획에 없는 것 3줄**: `tests/test_auth_nickname.py:83` `assert login.json() == {"id": created["id"], "username": "nickuser2", "nickname": "심사위원"}` · `:85` `assert me.json() == {…같은 사전…}` · `tests/test_auth_helpers.py:105` `assert me.json() == {"id": "u-helper-1", "username": "helper-one", "nickname": "helper-one"}` — 셋 다 `MeOut`(`app/auth/routes.py:121~122` `_me_out`, 가입·로그인·`/auth/me` 의 `response_model`)의 사전 동등 비교라 `notice_required` 가 더해지면 실패한다 → P3-R1 |
| H3 | `app/tools/persons.py` 196~216·358~376행 읽기 | 208행 `embedding_ran = provider is not None and embedded_alias_count > 0`, 214행 `query_vector = provider.embed([q])[0]`. `_add_alias` 는 같은 인물·같은 글자 행이 있으면 임베딩·INSERT 를 하지 않는다. 계획 215행의 단언("임베더 호출은 후보 검색 질의뿐", "호출 횟수가 민감 낱말 없는 기존 별칭 턴과 같음", "`person_aliases` 행 수·`embedding` 값 그대로")은 이 코드에서 참이고, 가짜 임베더의 호출 기록과 행 조회로 판정된다 |
| H4 | `app/api/routes.py` 212~302행 · `grep -nE "^def \|PendingQuestion" app/api/deps.py` · `app/agent/loop.py` 793~868·1497~1582행의 context 줄 | `submit_answer`: `ctx = build_ctx(session, question_id, user, …)`(없거나 남의 질문이면 여기서 404) → `answer_question(ctx, question_id, body.answer)` → `load_resume_input`. `answer_question` 앞에 세션·질문 id·`user.id`·`ctx.now()` 가 있어 `legacy_resume_blocked(session, question_id, user_id, now)` 를 그 사이에 부를 수 있다. `PendingQuestion` ORM 을 읽는 곳은 `app/api/deps.py`(147·181행) — 계획이 그 모듈에 함수를 둔 것은 기존 규약(deps 166행 docstring)과 같다. 세 kind 의 질문 context 모두 최상위 `utterance` 키가 있다(ER 질문은 `app/er/pipeline.py`, 일정 질문 `loop.py` `_ask_schedule` 의 `context={"utterance": utterance, "resume": …}`, 후속 새 인물 질문 `"utterance": utterance`) — `detect(context["utterance"])` 가 세 kind 모두에서 성립한다 |
| H5 | `app/agent/loop.py` 295~315·396~432·541~616행 읽기 · `grep -rn "_pending_calls_from\|ResolveOutcome" app tests` | `_pending_calls_from(proposal, verdict, resolved_mentions)` 의 호출 자리는 **599행** 한 곳(계획 214행은 601행이라 적음 — 2행 차이, P3-R4). `verdict.accepted` 를 돌며 `args.get("person")` 으로 언급을 읽으므로 `excluded` 집합으로 그 언급의 제안을 빼는 것은 한 줄 조건으로 된다. `ResolveOutcome`(295행)은 dataclass 이고 `to_dict()` 가 `loop_resolve_done` trace 출력이다 — 새 필드를 기본값과 함께 더하는 것은 기존 생성 자리(618·625행, `tests/test_person_refs.py:126`, `tests/test_memory_loop.py`)를 깨지 않는다 |
| H6 | `tests/test_agent_query_gate.py` 92~104행 · `grep -rn GATE_REJECTION_REASONS app tests` · `app/agent/gate.py` 110~125행 · `tests/test_agent_fix037.py` 165~185행 | 100행 `GATE_REJECTION_REASONS[-1] == REASON_QUERY_TURN_NO_WRITE`, 101·102행 `== 7`. 튜플을 쓰는 곳은 그 시험·`test_agent_gate.py:409`(부분집합)·`test_agent_fix037.py:174`(매개변수)뿐. `fix037` 은 `gate_check` 를 가짜로 바꿔 사유를 강제하고 `result.reply == NOTHING_SENTENCE` 를 본다 — 새 사유가 매개변수에 들어가도 `run_turn` 을 직접 부르는 시험이라 차단 안내(라우트가 붙인다)는 붙지 않는다. 계획 표의 "고치지 않음" 이유와 같다 |
| H7 | `tests/test_agent_query_types.py` 30~50행 · `grep -rnE "PROPOSAL_SCHEMA\|PROPOSAL_ARG_SCHEMA" tests app` · `app/agent/propose.py` 488~500행 | 38행 `set(PROPOSAL_SCHEMA["properties"]) == {"tool_calls", "intent"}` — U6 가 최상위 속성을 더하면 실패한다. 47행·`test_agent_propose.py:90·91`(`required == ["tool_calls"]`·`additionalProperties is False`)은 선택 속성이라 그대로. 공급자 요청 본문 단언(`test_agent_propose.py:417·511·612`)은 `PROPOSAL_SCHEMA` 를 그대로 대입한 값과 비교하므로 따라간다 |
| H8 | `tests/test_api_read_persons.py` 125~200행 · `tests/test_mcp_tools.py` 1~12·125~140·280~300행 · `grep -nE "model_dump" app/mcp_server/tools.py` · `app/api/schemas.py` 334~390행 · `grep -rnE "(card\|facts\|timeline\|patterns\|upcoming_schedules)… == [\[\{]" tests/test_agent_query_*.py tests/test_api_*.py tests/test_mcp_*.py tests/test_tools_briefing.py tests/test_briefing_inputs.py` | `test_api_read_persons.py:189` `set(body["upcoming_schedules"][0]) == {"id", "title", "scheduled_at", "briefed_at"}` — 카드 항목에 키가 늘면 실패. 같은 파일의 사실·패턴·타임라인 단언은 키 하나씩만 읽는다(182~187행) — 깨지지 않는다. 137행(목록 항목 키 집합)은 `PersonListItemOut` 이 그대로라 유지. `test_mcp_tools.py:293` `result == read.get_person_card(…).model_dump(mode="json")` — MCP 가 키를 빼면 실패. 137·138행(목록)·319행(브리핑)은 모양 그대로. 카드 내용을 사전·목록 통째로 비교하는 다른 시험은 0건(마지막 grep 0줄) |
| H9 | backlog P9d 행과 01-plan 255행 비교(python, 읽기 전용) | `571 True` |
| H10 | `tests/test_auth_required_routes.py` 36~60·104~125행 · `web/src/__tests__` 의 가입·`/auth/me` 목 응답 grep · `web/src/__tests__/auth.test.tsx` 262~272행 | `_EXEMPT`(39행)·`_MUST_REQUIRE_LOGIN`(51행) 실재, 111행 `_MUST_REQUIRE_LOGIN <= routes`·113행 면제 등식 — 새 라우트는 보호 목록에만 들어가면 된다. 프론트: 가입 본문 동등 비교는 `auth.test.tsx:272` 한 곳(`toEqual({ username, nickname, password })`), 다른 시험의 `/auth/me` 목 응답(`connect`·`push`·`card`·`routes`)은 `notice_required` 가 없는 객체라 "필드가 `true` 일 때만 모달"(227행)이면 그대로 돈다 |
| H11 | `sed -n '89p' docs/wiki/decisions/D20-sensitive-guard.md`(R-7) | 2회차 N-R3 줄이 들어 있다(점검표 2행 인용). 같은 문단 뒤쪽에 "통과한 언급이 별칭 주인이 아닌 인물로 해석될 때의 동작은 사용자 결정 대기(01-plan D-4)" 가 남아 있다 — 같은 문단 앞쪽·갱신 이력 120행은 "확정 (a)" 라 낡은 문장이다(P3-R5) |
| H12 | `grep -rnE "sensitive_categories\|턴 수준" docs/wiki/decisions/D20-sensitive-guard.md docs/wiki/specs/S3.4-ask-user-protocol.md docs/wiki/changes/CR-009.md` | `CR-009.md:259`(4.2 U6) "`PROPOSAL_ARG_SCHEMA` 에 턴 수준 `sensitive_categories: enum[]`" 1줄뿐 — D20·S3.4 는 자리를 정하지 않았다. 계획 199행은 `PROPOSAL_SCHEMA` 최상위로 정했다(P3-R5) |

#### 3.A.2 2회차 [필수] 판정

| 소견 | 판정 | 근거 |
|------|------|------|
| **M2-잔여** U3 닫힌 목록에 `tests/test_api.py:93`·`tests/test_migration_0004.py:110` | **닫힘** | 01-plan 20행(사실 절 — "`tests/test_api.py:93` `body["alembic_revision"] == "0005"` … 0005 때도 `c85a0e8` 이 이 줄을 고쳤다", "110·157행은 0003 상태")·39행(산출물 U3 목록에 `tests/test_api.py`)·163행("**110행(`mig["columns_before"]`)과 157행**(둘 다 0003 상태)은 `USERS_COLUMNS - {"nickname", "privacy_notice_version", "privacy_notice_accepted_at"}`")·164행(`"0005"` → `"0006"`, 주석도)·168행(`u3-api` 명령, `u3-test-diff` 기대 목록에 `tests/test_api.py`, "목록 밖에서 깨지는 시험이 있으면 멈추고 03-log 에 보고"). 코드 대조 H1 — 두 줄 모두 계획이 적은 그대로다 |
| **M5** U7b 임베딩 단언 | **닫힘** | 01-plan 215행·217행. 단언은 코드와 맞고(H3) D20 결정 22 가 받아들인 전송(후보 검색 질의 임베딩)을 0 으로 단언하지 않는다. 고친 변이 후보(217행 "글자 비교를 정규화 비교(NFC·`casefold`·공백 제거)로")는 공백 변형 "마약쟁이형" 이 통과 판정을 받는 순간 수용 기준 "공백만 다른 변형 1건은 이름 거부(trace `dropped`, 별칭·인물 행 0)" 의 trace 결정값 단언에서 먼저 걸리고, 가짜 judge 가 주인으로 merge 를 내면 `_add_alias` 가 같은 글자 행을 찾지 못해 새 행 + `provider.embed([alias])` 1회가 생겨 "`person_aliases` 행 수 그대로"·"임베더 호출 횟수 같음" 에서도 걸린다 — 어느 쪽이든 검출된다. `casefold` 만으로는 한국어 변형이 생기지 않는다는 주석도 맞다 |

#### 3.A.3 2회차 [권고] N-R1~N-R8 처리

| 소견 | 판정 | 근거(01-plan 개정 2) |
|------|------|------|
| N-R1 ⑤ 갈래에서 버린 언급의 제안 | 닫힘 | 213행(파일 — `_pending_calls_from` 에 제외 언급 인자 · `ResolveOutcome` 에 버린 언급 필드)·214행(방식 — 지역 집합 `dropped`, `excluded=dropped` 새 키워드 인자 "기본 빈 집합이라 기존 호출 동작 불변")·215행(시험 1건 "앞 언급이 `dropped_non_owner` 이고 뒤 언급이 identity 질문으로 끝나면 그 질문 context 의 `pending_calls` 에 앞 언급의 제안 0")·217행(변이 "`excluded` 인자 빼기 → N-R1 시험 FAILED"). 코드로 가능하다(H5). 호출 행 번호만 2행 다르다(P3-R4) |
| N-R2 R-10 사전 검사의 자리 | 닫힘 | 192행(파일 `app/api/deps.py`(`legacy_resume_blocked`))·193행(방식 — `answer_question` 은 고치지 않고 앞에서 잠금 없이 읽는다, 여섯 조건이 모두 참일 때만 409, 하나라도 거짓이면 기존 경로)·194행(시험 "이미 답한 배포 전 모양 질문은 `already_answered`", "남의 배포 전 모양 질문은 404")·196행(변이 "'미답' 조건 빼기"). `submit_answer` 흐름에서 가능하다(H4) — `build_ctx` 가 먼저 남의 질문을 404 로 끊고, 함수 자체도 소유를 조건에 넣어 순서에 기대지 않는다. 막힐 때 쓰기 0 이라 잠금 없는 읽기의 경합은 해가 없다는 설명도 맞다(막히지 않는 쪽은 `answer_question` 의 `with_for_update` 가 그대로 지킨다) |
| N-R3 D20 R-7 의 원칙2 문장 | 닫힘 | D20 R-7 보충 줄(H11, 점검표 2행 인용) + 215행 `er_resolve` `applied` 거짓 시험. 같은 문단의 낡은 한 문장은 P3-R5 |
| N-R4 사실 절의 이유 문장 | 닫힘 | 19행 "`test_briefing_scheduler.py`(5줄 — … 이 시험은 `session_scope` 를 바꾸지 않아 주기 작업이 시험 세션과 **다른 세션**으로 돌고 거기서는 대상이 0명이다 …)" |
| N-R5 사후 긍정 재개의 trace 순서·거절 변이 | 닫힘 | 201행(step 순서 = `loop_resume` → `loop_gate` → 기록 `loop_resolve_done`·`loop_record` / 조회 `loop_query` → `loop_turn`, 재구성 `Proposal.raw` 는 빔)·196·203행(거절 처리를 `resume_turn` 안으로 옮기는 변이). step 이름은 `app/agent/types.py` 50~69행 상수와 같다 |
| N-R6 U9a 닫힌 목록 표현 | 닫힘 | 226행 "**단언 변경은 272행 가입 본문 하나**, 준비 줄은 가입을 제출하는 시험 전부에 고지 체크 클릭 한 줄" |
| N-R7 가입 422 모양 | 닫힘 | 52행(계약 표 — 선택 필드 `bool \| None = None`, 라우트가 판정)·173행. `app/auth/routes.py:102~103` `_invalid` 실재. 검사 순서 한 줄은 P3-R3 |
| N-R8 U7b Refs 의 `D1` | 닫힘 | 4행 머리 태그 줄, verify-plan `PASS  카드 존재: D1` |

#### 3.A.4 "고정 단언 전수 확인" 절(96~123행) 대조

**계획이 새로 찾았다고 한 6곳 — 전부 그 단위에서 실제로 깨지는 단언이다.**

| 계획이 든 자리 | 직접 본 줄 | 그 단위에서 깨지는가 |
|------|------|------|
| `tests/test_auth_api.py:96` (U4) | `assert set(body) == {"id", "username", "nickname"}` | 그렇다 — 가입 응답 `MeOut` 에 `notice_required` |
| `tests/test_auth_nickname.py:70` (U4) | 같은 식 | 그렇다 |
| `tests/test_agent_query_gate.py:101·102` (U5a) | `len(GATE_REJECTION_REASONS) == 7` · `len(set(…)) == 7` | 그렇다. 100행은 새 사유를 마지막 앞에 넣으면 유지(H6) |
| `tests/test_agent_query_types.py:38` (U6) | `set(PROPOSAL_SCHEMA["properties"]) == {"tool_calls", "intent"}` | 그렇다(H7) |
| `tests/test_api_read_persons.py:189` (U8) | `set(body["upcoming_schedules"][0]) == {"id", "title", "scheduled_at", "briefed_at"}` | 그렇다(H8) |
| `tests/test_mcp_tools.py:6·293` (U8) | 6행 docstring "`model_dump(mode="json")` 과 **같다**" · 293행 동등 비교 | 그렇다(H8) |

**"고치지 않는 것" 표본 대조 — 이유가 맞다.** `test_migration_0005.py:191`(`== "0004"` 는 downgrade 목적지) · `test_schema_check.py:24·58·63`·`test_schema_models.py` 144·226~234·289·336(테이블·FK·JSONB·인덱스 수는 0006 이 바꾸지 않는다 — S3.1 보충에 새 테이블·FK·인덱스 0) · `test_tools_questions.py:131~140`(매개변수 3종 성공 — 4종째가 있어도 참) · `test_agent_fix037.py:174`(H6) · `test_auth_required_routes.py:113`(면제 등식 — 새 라우트는 면제가 아니다) · `test_api_read_persons.py:137`·`test_mcp_tools.py:137`(`PersonListItemOut` 불변) · `web/`(H10).

**목록에 없는데 깨질 단언 — 3줄 찾았다(같은 종류: `MeOut` 사전 동등 비교, U4).** H2.
- `tests/test_auth_nickname.py:83`·`:85` — 파일은 U4 닫힌 목록 안이지만 계획 72행은 "**단언 줄 변경 0**(본문·준비만). **예외 3줄**" 로 못 박았고 이 두 줄은 그 셋에 없다.
- `tests/test_auth_helpers.py:105` — **파일이 U4 닫힌 목록에 없다**(43행·72행). 계획이 든 `u4-auth` 명령(174행)이 이 파일을 돌리므로 그 명령이 그대로 FAILED 가 되고, 고치면 `u4-test-diff ⊆ 닫힌 목록` 이 성립하지 않는다.

**종류 판정 — 구현 중 안전하게 드러나는 쪽이다(계획 단계 필수 아님).** ① 세 줄 모두 U4 자신의 판정 명령 `u4-auth` 가 돌리는 파일에 있어 조용히 지나갈 길이 없다(전체 pytest 까지 가기 전에 실패). ② U4 에는 "닫힌 목록 밖에서 깨지는 시험이 있으면 멈추고 03-log 에 보고, 목록을 넓히는 것은 verifier 리뷰에서"(174행)가 있다 — 2회차 M2-잔여를 필수로 본 까닭은 그때 U3 에 이 문장이 없었기 때문이다. ③ 고치는 내용이 하나로 정해진다(기대 사전에 `"notice_required": False` — 도우미·가입 모두 현재 판에 동의한 계정이다). 설계·사용자에게 보이는 동작·다른 단위에 번지지 않는다. 다만 "전수 확인" 이라 이름 붙인 절이 `set(body) ==` 모양만 찾고 `json() == {` 모양을 놓친 것이므로, 활성화 전에 architect 가 세 줄을 넣으면 U4 에서 멈춤·보고 왕복 1회를 아낀다(P3-R1).

그 밖의 패턴은 더 찾지 못했다: 리비전 리터럴(H1) · 컬럼·CHECK·인덱스 수(2회차 G6·G13 — `scripts/schema_check.py` 는 FK `== 9`·인덱스 `>= 10`·CHECK `>= 1` 만 본다) · 응답 키 집합(H2 의 grep 전부 — `test_chat_history.py:155`·`test_api_read_raw.py:89·143·154`·`test_api_read_briefings.py:138·142·143`·`test_mcp_tokens_api.py:95·173`·`test_tools_briefing.py:263`·`test_agent_query_loop.py:723~744`·`test_memory_promote.py:460` 은 이 계획이 모양을 바꾸지 않는 응답·trace) · 거부 사유·스키마 속성 집합(H6·H7) · 카드 `model_dump` 동등 비교(H8) · 질문 context 사전 동등 비교(`test_tools_questions.py:122·281` — `ask_user` 동작 불변, `consent` 키는 동의 턴에만) · `_AFFIRMATIVE_REQUIRED_KINDS`·`ToolContext` 필드·`run_turn` 시그니처를 고정한 시험 0건.

**미리 알 수 없는 것 1종**: U5a·U5b 가 `/chat` 에 규칙 검사를 걸면, 기존 채팅·루프 시험의 발화 가운데 U2 가 귀납할 낱말·정규식에 걸리는 것이 있으면 그 시험이 칩 질문이나 가림으로 끝난다. 목록이 U2 산출물이라 지금은 셀 수 없다(추정 낱말 몇 개로 `tests/` 를 찾아본 범위에서는 채팅 발화 0건). U5a·U5b 에는 U3·U4 같은 "멈추고 보고" 문장이 없다 → P3-R2.

#### 3.A.5 [권고] — 계획을 고칠 때 함께 넣거나 해당 단위 커밋 전 리뷰에서 닫는다 (필수 0건)

- **P3-R1 · U4 — `MeOut` 사전 동등 비교 3줄.** `tests/test_auth_nickname.py:83·85`, `tests/test_auth_helpers.py:105`(3.A.4). **고칠 자리**: 01-plan 72행(VR3 — "예외 3줄" 을 6줄로, 닫힌 목록에 `tests/test_auth_helpers.py`)·43행(산출물 U4 목록)·112행(전수 확인 표의 `MeOut` 행)·172행(U4 파일 "시험 7개"). 넣지 않으면 U4 에서 `u4-auth` 실패 → 멈춤·03-log 보고 → verifier 리뷰에서 목록 확장으로 닫힌다.
- **P3-R2 · "목록 밖에서 깨지면 멈추고 보고" 를 공통 규칙으로.** 지금은 U3(168행)·U4(174행)에만 있다. 278행 "단위 공통 회귀" 에 같은 문장을 한 번 두면 U5a·U5b(기존 발화가 규칙에 걸리는 경우 — 3.A.4)·U6·U7a·U8 에도 걸린다. 10행 "단언은 각 단위의 '닫힌 목록' 안에서만 바꾼다" 와 278행 "실패 0" 이 부딪히면 구현 에이전트는 어차피 멈춰야 하므로 동작은 같고, 적어 두면 임의로 단언을 고치는 길이 막힌다.
- **P3-R3 · U4 가입 검사 순서.** `notice_required` 와 기존 `invalid_username`·`invalid_password`·`invalid_nickname`·`username_taken`·`nickname_taken` 이 함께 걸릴 때 어느 코드가 나가는지가 없다(기존 순서 시험 `tests/test_auth_nickname.py:346~352`). 화면은 체크 없이는 버튼이 비활성이라 사용자에게 보이지 않는다 — U4 에 한 줄(예: 고지 판정을 맨 앞에)과 시험 1건.
- **P3-R4 · 행 번호.** `_pending_calls_from` 호출은 `loop.py` **599행**(계획 214행 "601행", VR2 ⑤ "되묻기(599~607)" 는 맞음).
- **P3-R5 · 카드·CR 의 낡은 문장 2건(메인 세션·architect).** ① `D20-sensitive-guard.md` R-7 뒤쪽 "통과한 언급이 별칭 주인이 아닌 인물로 해석될 때의 동작은 사용자 결정 대기(01-plan D-4)" → 확정 (a) 로(H11). ② `CR-009.md` 4.2 U6 "`PROPOSAL_ARG_SCHEMA` 에 턴 수준 `sensitive_categories`" 는 계획이 `PROPOSAL_SCHEMA` 최상위로 정했으므로(199행 — 제안 인자가 아니라 턴 전체의 표시라 그쪽이 맞다) CR 9절 반영표에 "이력" 한 줄(H12).
- **P3-R6 · `ResolveOutcome.name_rule_dropped` 의 trace 모양(U7b 리뷰).** `ResolveOutcome.to_dict()` 는 `loop_resolve_done` trace 출력이다(H5). 새 필드를 거기에 실을지, 싣는다면 언급 문자열 대신 언급 인덱스로 둘지(74행 `guard_name_rule` 의 "언급 문자열 0" 과 같은 방향)를 U7b 구현 때 정하고 시험에 드러낸다. 근거 자체는 `guard_name_rule` 행에 이미 남는다.
- **P3-R7 · 프론트 `MeOut` 타입(U9a 리뷰).** `web/src/api/types.ts:24` 에 `notice_required` 를 필수로 두면 타입이 붙은 기존 목 객체가 typecheck 에서 걸릴 수 있다 — "기존 목 응답은 고치지 않는다"(227행)를 지키려면 선택 필드다. `u9a-typecheck` 가 드러낸다.

#### 3.A.6 개정 2 가 새로 만든 문제 — 찾은 것

| 본 것 | 판정 | 근거 |
|------|------|------|
| 모순(계획 안·카드와) | 없음(사소 2건은 P3-R4·P3-R5) | VR2 행·U7b·전수 확인 표의 `REASON_NAME_RULE`(게이트 튜플에 넣지 않음)과 U5a 의 `REASON_MASKED_VALUE`(넣음, 마지막 앞)가 서로·`test_agent_gate.py:409`·`test_agent_query_gate.py:100` 과 맞는다. 계약 표(52행)와 U4 수용 기준(173행)의 422 모양이 같다 |
| 코드와 맞지 않는 자리 | 없음(행 번호 2행 차이 P3-R4) | H3~H8 |
| 실행 불가능한 검증 명령 | 없음 | 개정 2 가 더한 `u3-api`·`u5a-test-diff`·`u6-test-diff`·`u7b-test-diff`·`u8-test-diff` 는 `git diff --stat <해시> -- <경로>` 모양이고 가리키는 기존 파일(`tests/test_api.py`·`test_agent_fix037.py`·`test_agent_query_gate.py`·`test_agent_query_types.py`·`test_api_read_persons.py`·`test_mcp_tools.py`)이 있다. `git diff --stat` 은 추적되지 않은 새 파일을 내지 않으나 판정이 "⊆" 라 성립한다. 그 시점에 그대로 실패하는 것은 `u4-auth`(P3-R1) 하나이고 U4 의 멈춤 문장이 받는다 |
| 임의로 정한 사용자에게 보이는 동작 | 없음 | 개정 2 가 정한 것은 내부 자리뿐이다 — `legacy_resume_blocked` 의 응답은 D20 R-10 "409 `expired` 와 같은 응답" 그대로, 가입 422 는 기존 `detail.code` 모양, 새 문구 0. D-1~D-4·결정 22 는 계획 280~312행에 확정값 그대로(D-4 (a) 언제나 이름 거부 — 214·215행, 결정 22 글자 일치 — 74행, U2 낱말 목록 검토는 관문 아님 — 151·310행) |

### 3.0 재검증(2회차) — 01-plan 개정 1 (이력 — 판정은 3.A.2·3.A.3)

05-remediation 은 만들지 않았다(1차와 같은 이유 — 소견은 계획 문서를 architect 가 고칠 것이라 여기에 원인과 고칠 자리를 적는다). 아래 행 번호는 개정 1 의 01-plan 과 `6d97217` 의 코드 기준이다.

#### 3.0.1 직접 실행한 확인

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| G1 | `bash .claude/scripts/gitlog.sh P9d-sensitive-guard CR-009` | 두 태그 모두 `6d97217` 1건. dev2 = origin/dev2. 미커밋: backlog·CURRENT·HANDOFF·CR-009·D20·journal·S3.2(개정 1 과 함께 고친 카드)와 이 패키지 폴더 — 제품 코드 변경 0 |
| G2 | `grep -rcE "default_run_once\|_due_user_ids" tests` · `tests/test_briefing_scheduler.py` 160~205행 읽기 | 4개 파일(`test_push_wiring.py` 8줄 · `test_briefing_scheduler_users.py` 13줄 · `test_briefing_scheduler.py` 5줄 · `test_commit_boundaries.py` 1줄 = 407행 docstring). `test_briefing_scheduler.py:203` 은 `run_briefings` 를 가짜로 바꾼 뒤 `default_run_once()` 를 부르고 `len(calls) == 2` 를 단언한다. 이 시험은 `session_scope` 를 바꾸지 않아 주기 작업이 **실제 세션**으로 돈다 — 대상 0명 → `NO_USER_MARKER` 1회(`app/briefing/scheduler.py:171~172`) → 가짜 1회 + 수동 1회 = 2. `users` 조인을 더해도 대상은 여전히 0명이라 단언이 그대로 성립한다 |
| G3 | `tests/test_push_wiring.py` 108~114·167~176·349~385행 읽기 | `_make_person` 이 `Person(user_id="local")` 을 만들고 픽스처 `scheduler_env` 는 `session_scope` 를 롤백 세션으로 바꿀 뿐 계정 행을 만들지 않는다. 366·385행 `schedule.briefed_at is not None`. 307~337행 세 시험은 인물이 없어 표식 사용자로 돈다(조인과 무관) |
| G4 | `tests/test_briefing_scheduler_users.py` 31~60·111~122·288~327행 읽기 | `_person(db, user_id)` 가 `users` 행 없이 인물을 만든다(`A = "u5sched-a"`·`B = "u5sched-b"`). 대상 0명 시험 2건(288·298행)은 조인 뒤에도 그대로다 |
| G5 | `tests/auth_helpers.py` 58~78행 읽기 · `grep -rnE "\bUser\(" app scripts evaluation tests` | `make_user` 는 있으면 그대로·없으면 flush, 키워드 인자 `nickname` 하나. `User(` 는 `app/auth/routes.py:151`(가입)과 `tests/auth_helpers.py:70` 두 곳뿐 |
| G6 | `tests/test_schema_models.py` 18~96·158~263행 읽기 | 4행 근거 칸의 셈(79·7·5·3 → 85·11·8·4). 176행 `len(checks) == 1` 은 `events` 의 CHECK 전부를 세므로 0006 뒤 2 가 된다(계획 128행이 `type` 만 고르도록 고침). `pending_questions`(208행 `len(checks) == 1`)는 CHECK 를 지우고 다시 만드는 것이라 1 그대로 |
| G7 | `grep -rnE '"000[3-6]"' tests scripts app` · `grep -rn alembic_revision tests app` · `app/api/routes.py` 201~209행 · `tests/db_bootstrap.py:85` · `git show --stat c85a0e8 -- tests scripts` | **`tests/test_api.py:93` `assert body["alembic_revision"] == "0005"  # P9b-auth U12 -- 0005(CR-008)`** — `/health` 는 `alembic_version` 표를 읽고(routes 203행) 시험 DB 는 세션 시작 때 `alembic upgrade head` 가 된다(db_bootstrap 85행 docstring). 0005 때도 이 줄을 고쳤다(`c85a0e8` stat `tests/test_api.py | 2 +-`). 01-plan 에는 `test_api.py` 가 한 번도 나오지 않는다(`grep -n "test_api.py" 01-plan.md` 0줄) → M2-잔여 |
| G8 | `tests/test_migration_0004.py` 58~111·145~171행 · `0005.py` 58~118·180~200행 · `0003.py` 49·226~229·346~373행 읽기 | 0004 픽스처는 `upgrade "0003"` 뒤 `columns_before` 를 잡고(82행) `upgrade "head"` 한다. **110행 `mig["columns_before"] == USERS_COLUMNS - {"nickname"}` 도 0003 상태 단언**이다 — 계획 131행은 157행만 "0003 상태" 로 적었다. 111·169행은 head. 0005 는 110·111·196행 리터럴 `"0005"`. 0003 은 49행 집합을 head 에서 쓴다(228·372행) — 계획과 같다 |
| G9 | backlog P9d 행 `수용기준:` 문자열과 01-plan 222행 비교(python, 읽기 전용) | `571 571 True` |
| G10 | `app/tools/persons.py` 196~214·340~386행 · `app/er/candidates.py:41` · `app/er/pipeline.py` 459~467행 읽기 | `_add_alias`: `PersonAlias.person_id == person.id` 이고 `PersonAlias.alias == alias` 인 행을 찾고(364~368행) 없을 때만 `provider.embed([alias])`(372행) 뒤 INSERT — 계획 21행과 같다. **`search_person` 은 그 사용자에게 임베딩이 있는 별칭이 1개라도 있으면 질의 문자열을 임베딩한다**(214행 `query_vector = provider.embed([q])[0]`). ER 후보 검색은 `search_person` 을 그대로 쓴다(candidates 41행) → M5 |
| G11 | `app/agent/loop.py` 323~342·398~430·541~612·905~930·1087~1187·1286~1322·1641~1648·1808~1890행 · `app/agent/gate.py` 288~330행 · `app/agent/types.py` 174~193행 읽기 | `gate.check(proposal)` 는 세션·LLM 을 건드리지 않는 순수 함수이고 `_gate` 는 그것을 trace 로 감쌀 뿐이다(704~712행) — 재개에서 다시 태울 수 있다. `Proposal` 필드는 `tool_calls`·`raw`·`intent` 셋이고 게이트·해석은 `tool_calls`·`intent` 만 읽는다(`raw` 는 "게이트·해석이 참조하지 않는" 값, types 178행). `run_turn` 1128~1187행은 `proposal`·`verdict`·`now`·주입체만 쓰므로 함수로 뽑을 수 있다. `_ordered_mentions`·`_pending_calls_from`·`_record`(913행)는 모두 `verdict.accepted` 만 읽는다 — 새 `GateVerdict` 에서 뺀 제안은 어디에도 닿지 않는다. `_record` 는 `outcome.person_ids` 에 없는 언급을 건너뛴다(926행). `_resolve_mentions_impl` 601행 `_pending_calls_from(proposal, verdict, set(person_ids))` 는 확정되지 않은 **모든** 언급의 제안을 싣는다(→ N-R1) |
| G12 | `app/api/routes.py` 212~302행 · `app/tools/questions.py` 237~262행 · `app/api/deps.py` 158~186행 · `app/agent/loop.py` 1482~1494행 읽기 | `submit_answer` 는 `build_ctx` → `answer_question`(행 잠금 `with_for_update`, 소유·이미 답함·만료·옵션 검사와 저장이 **한 함수**) → `load_resume_input` → `resume_turn` 순서. `_log_resume_entry` 는 context 전체를 `loop_resume` trace 에 싣는다(→ N-R2·N-R5) |
| G13 | `scripts/schema_check.py` 133~190행 · `git show c85a0e8 -- scripts/schema_check.py` | CHECK 검사는 `len(rows) >= 1` 과 값 포함만 본다. 0005 때 고친 것은 FK 수 8→9 뿐 — 0006 은 FK 를 더하지 않으므로 계획대로 고칠 곳이 없다 |
| G14 | 검증 명령이 가리키는 기존 파일 27개 `[ -e ]` · `grep -rnE "signup\|가입" web/e2e/*.ts` · `grep -cE "가입하기\|signup" web/src/__tests__/*` · `.github/workflows/tests.yml` | 전부 있다(`tests/test_memory_*.py`·`test_tools_*.py`·`test_agent_query_*.py`·`test_briefing_*.py`·`test_mcp_*.py`·`test_api_read_*.py`·`scripts/mypy_check.py` 등). E2E 에는 가입 흐름이 없다(0줄). Vitest 가입 관련 줄은 `auth.test.tsx` 한 파일(13줄) |

#### 3.0.2 1차 [필수] M1~M4 판정

| 소견 | 판정 | 근거 |
|------|------|------|
| **M1** U4 닫힌 목록에 `test_push_wiring.py` 없음 | **닫힘** | 01-plan 19행(사실 절 — 4개 파일 열거)·40행(산출물)·69행(VR3 — `test_push_wiring.py` 픽스처에 `make_user(session, "local")` 1줄, `test_briefing_scheduler_users.py` 계정 준비 줄, `_MUST_REQUIRE_LOGIN` 1줄을 단언 예외로 명시)·141행(`u4-scheduler` 에 네 파일). 코드 대조 G2·G3·G4 — 두 파일만 고치면 되고 `test_briefing_scheduler.py:203` 은 정말 고칠 필요가 없다. 사실 절이 든 이유 문장만 다르다(N-R4) |
| **M2** U3 가 깨뜨리는 기존 시험이 목록에 없음 | **부분 — 1건 남음(M2-잔여)** | 닫힌 부분: 01-plan 20행·39행·127~133행(닫힌 목록과 새 값)·134행("목록 밖 시험 diff 0")·135행(`u3-migration` 이 0003~0006 을 같이, `u3-schema-tests`, `u3-test-diff`). 새 값 넷(85·11·8·4)은 G6 으로 맞다. `scripts/schema_check.py` 무수정도 맞다(G13). **남은 것**: `tests/test_api.py:93`(G7)과 `tests/test_migration_0004.py:110`(G8) |
| **M3** U7 이 커밋 하나 크기가 아님 | **닫힘** | 01-plan 172~177행 U7a(표시 전파·동의 사슬·단조·승격 제외·패턴 제외·민감 일정 문구 — 새 시험 `test_guard_storage.py`)와 179~184행 U7b(이름 규칙·결정 22·근거 trace — 새 시험 `test_guard_names.py`). 판정 표 6·7·10b·12·13 행(232~239행), U8 의존(186행), U11 변이 목록(211행), backlog `단위:` 줄, D20 ① 표 단위 칸이 함께 바뀌었다. U7a 는 여전히 파일 7개 + `loop.py` 후속 질문 네 자리로 크지만 한 계약(동의 문맥이 저장물에 닿는 길)으로 묶이고 판정이 `-k chain`·`-k monotone` 두 개다 — 1차가 예로 든 분할과 같다. U7b 는 `loop.py` 다섯 자리 + 새 함수 하나로 한 계약이다 |
| **M4** 결정 22 통과 경로의 새 별칭 | **닫힘**(같은 자리에 새 소견 M5·N-R1) | 메인 세션 결정 "글자까지 같을 때만 통과" 가 01-plan 22행·71행·181~182행, D20 결정 22·R-7, S3.2, backlog, CR-009 3.2 에 같은 문장으로 들어갔다. `_add_alias` 주장은 코드와 같다(G10). 수용 기준에 "그 턴의 `person_aliases` 행 수 변화 0"·"공백·대소문자만 다른 변형 1건은 이름 거부"·변이 후보 "글자 비교를 `casefold` 로"(184행)가 있다. (가) 비소유 해석은 D-4 확정 (a) 로(71행·247~251행·278행 — 사용자·메인 세션 결정과 같다), (나) 동의 문맥 없는 통과 턴은 `dropped_no_consent` 로 닫았다. 임베딩 단언 문구가 코드와 맞지 않는 것은 M5 |

#### 3.0.3 1차 [권고] R-1~R-13 처리

| 소견 | 판정 | 근거(01-plan 개정 1) |
|------|------|------|
| R-1 이름 규칙 자리 문장·시험 등식 | 닫힘 | 68행 VR2 끝 문장, 41행·180행(`tests/test_agent_loop.py` 426·483·600행 — 실재, 등식 모양 확인). D20 R-7·S3.2 자리 문장이 계획과 같게 고쳐졌다. 기존 시험에는 민감 언급이 없어 등식은 고치지 않아도 성립한다 — 고치는 것은 항을 더해 강화하는 쪽이다 |
| R-2 표시를 채우는 자리 | 닫힘 | 173~174행 + `S3.2-tools-v2.md` 마지막 줄 |
| R-3 미동의 건너뜀 근거 | 닫힘 | 72행·269행 + `CR-009.md` 9절 반영표 |
| R-4 사후 확인(기록) 재개 재료 | 닫힘(잔여 N-R5) | 67행 VR1·166~168행 — `proposal_calls` 전부 + `_gate` 재실행 + `_continue_after_gate`. 코드로 가능하다(G11). 힌트 유지 시험이 수용 기준에 있다(168행) |
| R-5 R-10 순서·중간 상태 | 닫힘(잔여 N-R2) | 105행·160행 |
| R-6 `probe.py`·프론트 목 응답 | 닫힘 | 40행·69행·194행·271행. E2E 에 가입 흐름이 없다(G14) |
| R-7 빈자리 9건 | 닫힘 | 80~91행 — 판정은 3.0.6 |
| R-8 `-k` 이름 | 닫힘 | 175행·182행·판정 표 232~236행 "선택 시험 수 > 0" |
| R-9 test 미열람 판정·검토 관문 | 닫힘 | 119~122행 — 러너 `--split test` 거부 시험과 변이 후보, 낱말 목록 검토는 관문 아님(메인 세션 결정) |
| R-10 U12 절차 | 닫힘 | 215~218행 — 사전 예행 4개, `pg_dump` 전문, 되돌릴 창(⑥~⑦), upgrade 실패 분기, 복원은 사용자 직접, 고지 컬럼 소실, 새로고침 |
| R-11 D20 ① 표 #13 | 닫힘 | 239행 + D20 ① 표 #13(미커밋 diff) |
| R-12 지어낸 식별번호 | 닫힘 | 111·113행 |
| R-13 사소한 것 | 닫힘 | 24행(`P9b-auth/03-log.md:316`)·146행(옵션 밖 답의 `tool_error` trace 는 범위 밖)·247행(D-1~D-3 확정 표기) |

#### 3.0.4 [필수] — 고치기 전에는 통과가 될 수 없다 (2건, 둘 다 한두 줄 수정)

- **M2-잔여 · U3 닫힌 목록에 `tests/test_api.py` 가 없다.** G7. 0006 뒤 시험 DB 의 `alembic_version` 은 `0006` 이라 `tests/test_api.py:93` `assert body["alembic_revision"] == "0005"` 가 실패한다. 01-plan 134행 "**목록 밖 시험 diff 0**" 과 245행 공통 회귀 "전체 pytest 실패 0" 이 U3 에서 같이 성립하지 않는다 — 1차 M2 와 같은 종류이고, 0005 때 이 줄을 고친 선례(`c85a0e8`)가 있어 미리 알 수 있던 자리다. U4 에는 "닫힌 목록 밖에서 깨지는 시험이 있으면 멈추고 03-log 에 보고" 문장(141행)이 있으나 U3 에는 없다. **고칠 자리**: 01-plan 20행(사실 절 — 스키마 고정 단언)·39행(산출물 "시험(닫힌 목록 안에서 고침 — U3)")·127~133행(닫힌 목록에 `tests/test_api.py:93` 리터럴 `"0005"` → `"0006"` 과 주석) 그리고 135행 `u3-test-diff` 의 기대 목록. 함께: 131행의 `tests/test_migration_0004.py` 줄에 **110행**(`mig["columns_before"]` — 0003 상태)도 157행과 같은 식(`USERS_COLUMNS - {"nickname", "privacy_notice_version", "privacy_notice_accepted_at"}`)으로 바꾼다고 적는다(G8 — 같은 파일 안이라 목록은 넓어지지 않지만 지금 문장대로면 110행이 실패한다).
- **M5 · U7b 수용 기준의 임베딩 단언이 코드·D20 결정 22 와 맞지 않는다(점검표 3행).** G10. 01-plan 182행 "그 턴의 `person_aliases` 행 수 변화 0·별칭 임베딩 호출 0(**가짜 임베더 호출 인자에 그 문자열 0**)" — 통과한 언급은 ER 을 타고, ER 후보 검색(`search_person`)은 그 문자열을 질의로 임베딩한다(`app/tools/persons.py:214`). 결정 22 의 장면은 "이미 저장된 별칭이 있는" 사용자이므로 임베더를 붙인 시험에서는 그 문자열이 반드시 임베더 인자에 나온다. 문구대로 시험하려면 `app/er/`·`search_person` 을 고치거나(금지 — 수용 기준 #12) 임베더 없이 돌려 아무것도 검사하지 않는 시험이 된다. D20 결정 22 는 그 전송을 받아들였다("기존 별칭 자체는 인물 판정 때 OpenAI 로 계속 전송된다(사용자가 알고 고름)"). **고칠 자리**: 182행을 "별칭 **저장용** 임베딩 0" 으로 — 예: 임베딩이 있는 기존 별칭 + 가짜 임베더를 붙인 턴에서 임베더 호출이 후보 검색 질의뿐(호출 횟수가 같은 인물을 민감 낱말 없는 기존 별칭으로 부른 턴과 같다)이고 `person_aliases` 행 수·그 행의 `embedding` 값이 그대로. 184행 변이 후보("`casefold` 비교로")가 이 단언으로 검출되는지도 그 문장으로 맞춘다.

#### 3.0.5 [권고] — 해당 단위 커밋 전 리뷰에서 닫을 수 있다

- **N-R1 · VR2 ⑤(비소유 해석 거부)에서 버린 언급의 제안이 뒤 언급의 되묻기 context 에 실린다.** G11. ⑤ 는 `_resolve_mentions_impl` 안이라 `verdict` 를 바꾸지 못하고, 601행 `_pending_calls_from(proposal, verdict, set(person_ids))` 는 확정되지 않은 모든 언급의 제안을 담는다. 버린 언급이 앞, identity·new_person 질문이 나는 언급이 뒤에 있으면 버린 언급의 제안이 그 질문의 `pending_calls` 로 저장되고, 재개 때 그 언급을 다시 `resolve()` 한다(judge 재호출 — 이번엔 주인으로 merge 될 수도 있어 결과가 갈린다). 기록은 `_record` 926행이 건너뛰어 0 이다. U7b 에 방식 한 줄(버린 언급 집합을 그 뒤 `_pending_calls_from` 에서 빼고 `ResolveOutcome` 으로 답 문구에 전달)과 시험 1건(앞 언급 `dropped_non_owner` + 뒤 언급 identity 질문 → 그 질문 context 의 `pending_calls` 에 앞 언급 제안 0)을 더한다. 182행 "걸린 언급의 제안이 다른 언급 되묻기 context 의 `pending_calls` 에 0" 이 ⑤ 갈래도 포함한다고 읽으면 수용 기준은 이미 있다.
- **N-R2 · R-10 사전 검사의 자리(U5c).** G12. 160행은 "소유·상태를 기존과 같은 순서로 본 **뒤**, 답을 저장하기 **전에**" 라 적었는데 그 상태 검사와 저장은 `answer_question` 한 함수 안이고 행 잠금(`with_for_update`, FIX-019)도 거기서 잡는다. 라우트에서 하려면 상태를 한 번 더 읽어야 하고(`PendingQuestion` ORM 을 읽는 곳은 `app/api/deps.py` 뿐이라는 기존 규약 — deps 166행), 함수 안에서 하려면 `app/tools/questions.py` 가 U5c 파일 목록에 있어야 한다. 어느 쪽인지 U5c 에 한 줄, 그리고 "이미 답한 배포 전 질문 → `already_answered`(R-10 응답이 아님)" 시험 1건.
- **N-R3 · D20 R-7 의 원칙2 문장이 ⑤ 갈래를 덮지 못한다(점검표 2행).** "확신도 판정 **이전**의 제외 … (판정이 일어나지 않는다)" 는 `_apply_name_rule`(ER 앞)에만 맞다. D-4 확정안의 새 인물 밴드 거부는 `resolve()` 가 확신도를 낸 **뒤** `< T_new` 인데 `ask_user` 없이 그 언급을 버린다 — CLAUDE.md 원칙2 "그 미만은 반드시 `ask_user`" 의 글자와 다르다. 병합·생성이 0 이고 사용자가 고른 동작이라 계획은 그대로 두되, D20 R-7(과 필요하면 CLAUDE.md 원칙2 옆 주석)에 "결정 22 로 통과한 언급이 주인이 아닌 인물·새 인물로 판정되면 판정 뒤에 버린다 — 병합·생성·질문 0, 사용자 결정 D-4" 한 줄을 메인 세션·architect 가 더한다. 그 `er_resolve` trace 는 `applied` 가 거짓으로 남는다는 것(조회 턴 1322행과 같은 모양)도 U7b 시험에 한 줄.
- **N-R4 · 사실 절 19행의 이유 문장.** `test_briefing_scheduler.py` 는 5줄(계획 "6곳")이고, 203행이 안전한 이유는 "`logged_in_client` 로 `local` 계정을 만든다" 가 아니라 그 시험이 `session_scope` 를 바꾸지 않아 주기 작업이 다른 세션으로 돌고 대상이 0명이기 때문이다(G2). 결론("고칠 필요 없음")은 맞다.
- **N-R5 · 사후 긍정 재개의 trace 순서(U6).** 재개에서 `_gate` 를 다시 태우면 `loop_gate` 행이 재개 턴에 하나 더 생긴다 — `resume_turn` docstring "`loop_extract`/`loop_gate` 행은 남기지 않는다"(loop 1803~1805행)와 달라진다. 다시 만든 `Proposal` 의 `raw` 는 비어 있다(동작 영향 0, G11). U6 수용 기준에 사후 긍정 재개의 step 순서 한 줄. 또 `_log_resume_entry` 가 context 전체를 `loop_resume` 행에 싣으므로(G12) "거절 분기는 `resume_turn` **앞**에서 끝난다"(160행)를 U5c·U6 변이 후보에 더한다(거절 처리를 `resume_turn` 안으로 옮기기 → 거절 뒤 trace 전수 0 FAILED).
- **N-R6 · U9a 닫힌 목록 표현.** `auth.test.tsx` 는 "272행 가입 본문 단언" 만이 아니라 가입을 제출하는 시험마다 체크 클릭 준비 줄이 든다(체크 없이는 버튼이 비활성 — 194행). 같은 파일 안이라 `u9a-test-diff` 는 그대로 성립한다. "단언 변경은 272행 하나, 준비 줄은 가입 제출 시험 전부" 로 적는다.
- **N-R7 · 계약 표의 가입 422 모양**은 기존 `_invalid`(`app/auth/routes.py:102~103`, `HTTPException(422, detail={"code": …})`)와 같다 — 본문 스키마에서 필수 필드로 두면 FastAPI 기본 검증 422(`detail` 이 목록)가 먼저 나가므로 선택 필드로 받고 라우트에서 판정해야 한다는 것을 U4 에 한 줄.
- **N-R8 · U7b Refs 의 `D1`** 을 머리 태그 줄(4행)에 더하거나 Refs 에서 뺀다(카드 `D01-new-person-confirm.md` 는 있다).

#### 3.0.6 개정 1 이 스스로 정한 것 — 카드·코드에서 나오는가

| 정한 것 | 판정 | 근거 |
|------|------|------|
| 통과 턴에 동의 문맥이 없으면 이름 거부(`dropped_no_consent`, 71행) | 계획이 정해도 된다 — 사용자에게 **알린다** | 결정 22 는 "동의 칩은 평소처럼 뜨고 저장물에는 민감 표시" 를 전제로 한 통과다. 동의 문맥이 없으면 표시할 범주가 없어 통과시키는 쪽이 결정 22 문장 밖이고, 거부하는 쪽은 결정 15("저장하지 않고 안내")로 돌아간다. 새 문구 0(부속 "이름 거부" 문구). 이름 규칙과 사전 검사가 같은 목록이라 발화에 그 낱말이 있으면 늘 동의가 먼저 서므로, 이 갈래는 추출 LLM 이 발화에 없는 민감 낱말을 언급으로 낸 때에만 생긴다. D20 R-7 에 같은 문장이 들어가 있다 |
| ① U2 선형 시간 = 구조 단언 | 계획이 정해도 된다 | 원칙8(시간 상한은 기기마다 흔들린다). 사용자에게 보이지 않는다 |
| ② 자리표시만 든 사실 값 → 그 `update_person` 제안 전체 거부 | 계획이 정해도 된다 | `app/agent/gate.py` 288~330행 — 거부는 제안 단위(`RejectedProposal(index, …)`)뿐이다. 같은 제안의 다른 사실도 함께 버려진다는 것은 U5a 시험에 드러나게 한다 |
| ③ 재개 방어에 걸리면 딸린 보류 제안도 버림 + 이름 거부 문구 | 계획이 정해도 된다 | 사용자 결정 15, 기존 `_drop_calls_for_mention`(loop 1641행)의 new_person 부정 답 처리와 같은 모양 |
| ④ 민감 일정 문구 조건(동의 턴에서 일정 1건 이상 저장 시 한 번) | 계획이 정해도 된다 | D20 부속 문구 그대로, 조건은 계획 86행이 든 CR-009 의 G12 문장("알림이 오지 않는다는 것을 칩 응답에 한 줄")에서 나온다 |
| ⑤ `cleanup_expired` 예외 규약 | 계획이 정해도 된다 | `app/briefing/scheduler.py` 174~178행의 사용자 반복 규약과 같다 |
| ⑥ `guard_check` → 구간 시작 id 읽기 → `run_turn` | 계획이 정해도 된다 | D20 R-2 "`guard_check` trace 는 남는다" |
| ⑦ 카드 가림 상태에서 보이는 것(배지·범주 이름·사건 날짜·종류 이름·사실 키 이름) | D-2 확정 범위 안 — 사용자에게 **알린다** | D-2 는 "배지 '민감' + 범주 이름 + 눌러서 보기" 까지 정했다. 날짜·종류·키 이름을 가림 상태에서 보이는 것은 계획이 더한 것이다. 자기 카드 화면(카드 계층)이고 한 번 누르면 전부 보이므로 새 결정으로 올리지는 않되, 사실 키 이름 자체가 내용을 드러낼 수 있다는 점은 U12 화면 확인 때 사용자가 본다 |
| ⑧ U1 조회형 ≥ 1·우회는 범주 셈 밖 | 계획이 정해도 된다 | `CR-009.md` U1 "조회형 민감 문장도 범주별로 섞는다", 사용자 결정 12 크기 그대로 |
| ⑨ 재고지 재호출 204·행 변경 0 | 계획이 정해도 된다 | 처음 동의 시각을 덮지 않는다 |
| 계약 표(49~57행): 가입 422 `notice_required`·`POST /auth/privacy-notice` 204·403 모양·`PRIVACY_NOTICE_VERSION = 1` | 계획이 정해도 된다 | 기존 오류 모양(`detail.code`)과 같다(N-R7). 사용자에게 보이는 글은 D20 확정 문구뿐 |
| D-4 (a) 언제나 이름 거부 | 사용자 결정(2026-11-22)과 같다 | 71행·251행·278행. identity 밴드는 질문을 띄우고 답이 주인일 때만 기록한다 — 메인 세션이 전한 "주인이 아닌 인물·새 인물로 해석되면 언제나 이름 거부" 와 어긋나지 않는다(주인으로 답하면 해석 결과가 주인이다) |

#### 3.0.7 단위별 실행 가능성·크기·변이

- **검증 명령**: 가리키는 기존 파일은 전부 있다(G14). 새 파일(`test_guard_names.py` 등)은 그 단위가 만든다. 그 시점에 실행 불가능하거나 그대로 실패하는 것은 U3 공통 회귀(M2-잔여) 하나다. U7b 의 `-k name_rule`·U7a 의 `-k chain`·`-k monotone` 은 시험 이름 규약과 "선택 수 > 0" 이 붙어 있다.
- **의존 순서**: 97~105행 그림과 각 단위 `의존:` 이 같다. U5c~U6 사이 중간 상태(동의 턴 후속 질문이 R-10 409)는 105행에 적혀 있고 U7a 수용 기준 "사슬에서 R-10 409 가 나지 않음" 이 닫는다. 그 사이 커밋의 전체 pytest 가 깨지는지는 기존 시험에 민감 낱말이 든 발화가 있느냐에 달렸다 — U5c 리뷰에서 실행 결과로 본다(계획 문제가 아니다).
- **커밋 하나 크기**: U7a·U7b 는 3.0.2 M3. 나머지 단위는 1차와 같다.
- **변이 후보**: U1~U10 모두 1개 이상(115·122·136·142·149·156·163·170·177·184·190·196·202·208행). U11 이 U5a·U5b·U5c·U6·U7a·U7b·U8 각 1개 + downgrade 가드 + 러너 `--split test` 거부를 다시 돌린다(211행).

### 3.1 (1차 이력) 직접 실행한 확인

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| E1 | `bash .claude/scripts/gitlog.sh P9d-sensitive-guard D20 CR-009` | 세 태그 모두 `6d97217` 1건. dev2 = origin/dev2. 미커밋: backlog·CURRENT·HANDOFF·CR-009·D20·journal·S3.2(사용자 결정 22 보충)와 이 패키지 폴더 |
| E2 | `grep -n "^def " app/agent/loop.py` + 해당 행 읽기 | 01-plan 13행의 행 번호가 전부 맞다: `_ordered_mentions` 323, `_pending_calls_from` 398, `_apply_resume_byte_limit` 451, `_resolve_mentions_impl` 541(호출 552·`resolve()` 580·`apply_resolution` 583), `_execute_call` 869~897(`facts`·`new_alias` 만), `run_turn` 1087(1124 → 1126 → 1128 → 1139 → 1141, `trace_ids` 1180~1184), `_run_query_turn` 1286(1309 `resolve()`, 1322 주석 "별칭 누적 0"), `_drop_calls_for_mention` 1641, `resume_turn` 1710(1847 별칭 · 1856 `_followup_new_person_turn` · 1877 `create_person`) |
| E3 | `app/api/routes.py` 212~302·305~331·333~416 읽기 | `submit_answer` 의존성은 `judge`·`embedder`·`extractor` 뿐, `chat` 은 389행 `append_chat_message` 가 `run_turn` 앞, `_record_loop_error` 는 `input={"utterance": …}` — 계획 15행과 같다 |
| E4 | `app/tools/questions.py` 90~236 읽기 · `grep -rn "ask_user(" app` | `_AFFIRMATIVE_REQUIRED_KINDS = ("identity", "new_person")` 96행, `@traced("ask_user")` 183행. `ask_user` 호출 자리는 `loop.py:831`·`:1547`·`er/pipeline.py:478` 세 곳. `create_person` 확인 경로는 `persons.py:470`·`:547` 이 kind 를 직접 적는다 — `sensitive` 를 긍정 규약 집합에 더해도 인물 생성 확인으로 쓰이지 않는다 |
| E5 | `app/briefing/scheduler.py` 100~180 읽기 | `_due_user_ids` 는 `Person.user_id` 만 읽는다. 대상 0명이면 `NO_USER_MARKER` 로 한 번 돈다 — 계획 17·68행과 같다 |
| E6 | `grep -rln "default_run_once" tests` → 4개 파일, `tests/test_push_wiring.py` 104~112·349~388행 읽기 | `test_scheduler_end_to_end_sends_and_records`·`test_scheduler_end_to_end_without_keys_keeps_old_behavior` 가 `Person(user_id="local")` + 창 안 일정을 만들고 **`users` 행 없이** `default_run_once()` 를 불러 `schedule.briefed_at is not None` 을 단언한다(픽스처 `scheduler_env` 는 `make_user`·`logged_in_client` 를 부르지 않는다) → M1 |
| E7 | `git show c85a0e8 -- tests/test_schema_models.py tests/test_schema_check.py tests/test_migration_0003.py tests/test_migration_0004.py scripts/schema_check.py` · `grep -n "QUESTION_KINDS\|0005" tests/…` | 0005 때 목록 밖 시험 4개 + 스크립트 1개를 고쳤다("계획 목록 밖 수정, 03-log 보고" 주석). 지금 고정 단언: `tests/test_schema_models.py:210` `len(m.QUESTION_KINDS) == 3` · 같은 파일 "총 컬럼 79"·"nullable 은 정확히 7개" · `tests/test_schema_check.py:44` `len(sc.m.QUESTION_KINDS) == 3` · `tests/test_migration_0005.py:110` `head == "0005"`·`:196` → M2 |
| E8 | `app/tools/persons.py` 340~386 읽기 | 별칭 존재 확인은 `PersonAlias.alias == alias`(글자 그대로), 없으면 `provider.embed([alias])` 뒤 INSERT → M4 |
| E9 | `grep -rln "auth/signup"`(저장소 전체) · `tests/` 개수 | 시험 16곳/5파일(계획 19행과 같음). 그 밖에 `evaluation/recognition/probe.py:110` 이 가입 본문을 `username`·`password`·`nickname` 만으로 보낸다 → R-6 |
| E10 | 검증 명령이 가리키는 파일 46개 존재 확인(`[ -e ]`) · `web/package.json` scripts | 기존 시험·스크립트 전부 있음(`tests/test_auth_helpers.py`·`tests/test_agent_gate.py`·`scripts/schema_check.py`·`scripts/mypy_check.py` 등). `typecheck`·`build`·`lint` 스크립트 있음 |
| E11 | `web/src/screens/ChatScreen.tsx` 88·128·190·317, `web/src/__tests__/auth.test.tsx:272`, `app/mcp_server/tools.py` 37~41, `docs/wiki/fixes/FIX-015.md:84`, `git log -1 6e7b286` | 계획 18·20·21행과 같다 |
| E12 | `docs/user-setup/13-user-todo-deploy.md` 124~144 · `docker/entrypoint.sh:10` · `docker-compose.prod.yml` | I 절 되돌리기 4단계(backend 정지 → `run --rm --entrypoint python backend -m alembic downgrade` → `git checkout` → `up -d --build`)와 기동 시 `alembic upgrade head` 가 실재한다. 백업 선례는 `packages/P9b-auth/03-log.md:316` `~/backup-20261118-pre-demo-fix.sql`(계획 22행은 "HANDOFF 27행" 이라 적었으나 그 줄에는 없다 — R-13) |
| E13 | backlog 110행과 01-plan 189행 문자열 비교(python, 읽기 전용) | `backlog len 571 plan len 571 equal True` |

### 3.2 (1차 이력) [필수] — 판정은 3.0.2

- **M1 · U4 의 닫힌 시험 목록에 `tests/test_push_wiring.py` 가 없다(VR3·VR7 이 덜 닫혔다).** 01-plan 68행은 `_due_user_ids` 에 `users` 를 조인해 "`users` 행이 없는 `persons.user_id` 도 제외" 한다. 그러면 E6 의 두 시험은 대상 사용자가 0명이 되어 `briefed_at` 이 NULL 로 남고 실패한다. 65행 닫힌 목록에는 주기 작업 시험이 `test_briefing_scheduler.py`·`test_briefing_scheduler_users.py` 둘뿐이고, 19행 "주기 작업 시험 중 `users` 행을 만드는 것은 `test_briefing_scheduler_users.py` 뿐" 은 `default_run_once` 를 부르는 파일 4개 중 2개만 본 것이다. 이대로면 U4 수용 기준 "전체 pytest 실패 0" 과 "`git diff --stat <U3 해시> -- tests` 의 파일 목록 ⊆ 닫힌 목록" 이 같이 성립하지 않는다. **고칠 자리**: 01-plan 19행(사실 절)·65행(VR3 닫힌 목록에 `tests/test_push_wiring.py` 준비 줄 추가)·37행(산출물 "시험(닫힌 목록 안에서 고침)")·116행(`u4-scheduler` 명령에 그 파일). 함께: 115행 "새 라우트는 `_MUST_REQUIRE_LOGIN`" 은 `tests/test_auth_required_routes.py` 의 상수 집합에 한 줄을 더하는 것인데 65행은 그 파일에 "단언 줄 변경 0(본문·준비만)" 이라 적었다 — 그 한 줄을 예외로 적는다.
- **M2 · U3 가 깨뜨리는 기존 시험이 파일 목록에 없고, U3 검증 명령 자체가 실패한다.** 107행 파일 목록은 리비전·모델·새 시험 3개뿐인데 E7 의 고정 단언이 0006 으로 전부 달라진다: `QUESTION_KINDS` 4종(→ `test_schema_models.py:210`·`test_schema_check.py:44`), 컬럼 6개 추가(→ "총 컬럼 79"), nullable 컬럼 6개 추가(→ "정확히 7개"), head 가 `0006`(→ `test_migration_0005.py:110`·`:196` — 이 파일은 110행 `u3-migration` 명령에 들어 있어 명령이 그대로 FAILED 가 된다). 10행 "단언은 각 단위의 닫힌 목록 안에서만 바꾼다" 와 212행 "범위 = 그 단위 파일 목록만" 때문에 구현 에이전트는 계획 밖 수정을 하거나 멈춰야 한다(0005 때 같은 일이 있었다 — E7 주석). **고칠 자리**: 01-plan 107행에 U3 닫힌 목록(`tests/test_schema_models.py`·`tests/test_schema_check.py`·`tests/test_migration_0005.py` 의 head 리터럴 두 곳 — 0004 시험이 0005 때 바꾼 방식, 필요하면 `tests/test_migration_0003.py`·`0004.py`·`scripts/schema_check.py`)과 바꿀 단언(개수 3→4, 79→85, 7→13 을 architect 가 S3.1 보충에서 세어 적는다), 37행 산출물, 109행 수용 기준에 "목록 밖 시험 diff 0" 판정 명령(`git diff --stat <기준> -- tests`).
- **M3 · U7 이 커밋 하나 크기가 아니다.** 147~152행 U7 은 서로 독립인 계약 셋을 한 단위에 담았다 — ① 저장 표시 전파·동의 문맥 사슬·바이트 절단(D20 ① 표 #6) ② 사실 표시 단조·승격 입력 제외·패턴 제외(#7, R-5·R-8, D14) ③ 이름 규칙 네 자리 + 재개 거르기 + 근거 trace + 사용자 결정 22(#10b, R-7). 고치는 파일 11개에 `loop.py` 의 `run_turn`·`resume_turn`·후속 질문 네 자리·`_execute_call` 이 모두 들어가고, 판정도 `-k chain`·`-k monotone`·`-k name` 셋으로 이미 갈려 있다. 한 계약의 리뷰 소견이 나머지 둘의 커밋을 붙잡는다 — CR-009 가 구 U4 를 U5a·U5b·U5c 로 나눈 것(검토 M9)과 같은 이유다. **고칠 자리**: U7 을 둘 이상으로 나눈다(예: U7a 표시 전파·사슬·단조·승격·패턴 / U7b 이름 규칙·결정 22·`guard_name_rule` trace — U7b 는 U7a 의 `ctx.consent` 에 기댄다). 01-plan 79~86행 순서 그림·147~152행·판정 표 6·7·10b 행·U8 의존·U11 변이 목록, 그리고 `docs/backlog.md` 110행의 `단위:` 줄(수용기준 문자열은 그대로).
- **M4 · 사용자 결정 22 의 통과 경로에서 민감 낱말이 든 새 별칭이 저장될 수 있다(점검표 3행).** E8. `name_key` 는 공백·대소문자를 접는데 별칭 저장은 글자 그대로 비교하므로, 저장된 별칭과 `name_key` 만 같은 언급은 통과한 뒤 자동 연결에서 **새 별칭 행 + 임베딩 호출**을 만든다. `D20-sensitive-guard.md` R-7 "새로 저장되는 이름이 없다"·`CR-009.md` 8.4 N7 "(나) … 같은 별칭 upsert 라 새 행 0" 과 어긋난다. 같은 뿌리의 둘: (가) 통과한 언급이 그 별칭의 주인이 아닌 인물로 해석되면(identity 답으로 다른 인물을 고르는 경우 포함 — 1847행) 그 인물에 민감 별칭이 새로 붙는다 (나) 통과한 턴에 동의 문맥이 없을 때(언급은 LLM 이 낸 문자열이라 발화의 부분 문자열이 아닐 수 있다) 저장물에 무슨 범주를 붙이는지가 없다 — 67행은 "사전 검사에서 이미 동의를 거쳤으므로" 를 전제로만 적었다. **고칠 자리**: 01-plan 67행(VR6)·150행(U7 수용 기준)에 ① 통과 턴에서 `person_aliases` 행 수 변화 0 과 임베딩 호출 중 별칭 임베딩 0 을 단언으로(공백·대소문자만 다른 변형 1건 포함) ② 그것을 `app/er/` 를 고치지 않고 이루는 방법(예: 루프가 언급을 저장된 별칭 문자열로 바꿔 ER 에 넘긴다 / 글자까지 같은 때만 통과) ③ (가)(나) 의 동작 한 줄씩. "변형 별칭이 새로 저장되는 것을 받아들인다" 를 고르려면 D20 R-7 문장이 바뀌므로 사용자 결정이다(4절 Q1).

### 3.3 (1차 이력) [권고] — 처리는 3.0.3

- **R-1 · 이름 규칙 ① 의 자리 표현이 카드와 다르다.** `D20-sensitive-guard.md` R-7 은 "`_resolve_mentions_impl` 안, `_ordered_mentions` 뒤" 라 적었고 01-plan 64행은 `run_turn` 의 게이트 뒤(새 함수 `_apply_name_rule`)로 정했다. 카드가 "정확한 줄 자리는 01-plan" 이라 넘겼고 재검토 VR2 도 두 자리를 다 들었으므로 충돌은 아니다. 계획이 통과하면 D20 R-7·S3.2 18행 이하의 자리 문장을 계획에 맞춰 한 번 고친다(메인 세션·architect). 함께: 걸린 제안은 `loop_gate` trace(이미 기록됨)에는 `accepted` 로 남고 실행·보류 어디에도 없다 — `tests/test_agent_loop.py` 426·483·600행의 등식(`accepted == executed ∪ failed ∪ pending ∪ hint_only`)에 "이름 규칙으로 버린 인덱스" 항이 더해진다는 것을 U7 에 한 줄 적는다(`guard_name_rule.input.proposal_indices` 가 그 항이다).
- **R-2 · 표시를 채우는 자리.** `S3.2-tools-v2.md` 는 "동의 문맥은 `ToolContext.consent` 로 싣고 기록 직후 같은 트랜잭션에서 `sensitive_category` 를 채운다", `CR-009.md` U7 은 "`_record`·`_execute_call`(툴 호출 뒤 같은 트랜잭션에서 표시)" 인데 01-plan 148행은 툴(`add_event`·`add_schedule`·사실 upsert)이 `ctx.consent` 를 직접 읽는다. 결과는 같고 시그니처도 그대로지만 문장이 다르다 — 어느 쪽인지 한 줄로 고정하고 카드 문장을 맞춘다. 툴 반환 타입에 필드가 늘면 `tools_check` 가 무엇을 보는지도 U7 에 적는다.
- **R-3 · 미동의 건너뜀의 근거(VR7).** `CR-009.md` 4.2 U4 는 "`briefing_run` trace 에 건너뛴 사유 `notice_required` 와 일정 id 만" 이라 적었고 계획은 trace 0 으로 닫았다(68행). S3.6 이 계획에 넘긴 자리라 받아들인다. CR 4.2 의 그 문장은 이력이 되었음을 CR 반영표에 한 줄 남기는 것이 좋다. `users` 행이 없는 `persons.user_id` 를 제외하는 것은 계획이 더한 방어 조건이다(230행에 적혀 있음).
- **R-4 · 사후 확인(기록)의 재개 재료.** 63행은 조회 쪽 context 모양만 적었다. 기록 쪽은 "기존 `PendingResume` + `_synthetic_proposal_and_verdict`" 인데 `PendingResume` 은 언급 하나의 `mention`·`hints` 를 담는 모양이다. 사후 질문은 ER 앞에서 멈추므로 언급이 여럿일 수 있고, `hint_only` 버킷(`create_person` 제안의 관계 태그·위계 힌트)을 싣지 않으면 긍정 재개 뒤 위계가 기본값으로 떨어진다(사전 경로는 처음부터 다시 돌아 힌트가 산다). context 모양(`mention` 을 무엇으로 두는지, 힌트를 싣는지)을 U6 에 적고, "긍정 재개 결과가 표시 없는 턴과 같은 저장 행" 시험을 한 줄 더한다.
- **R-5 · R-10 의 순서와 단위 사이 중간 상태.** `submit_answer` 는 `answer_question`(답 저장)을 먼저 부른다(E3). 배포 전 질문을 409 로 막을 때 답이 저장된 채 409 인지(질문 소비), 저장 전 검사인지(질문이 24시간 동안 계속 떠 있음)를 U5c 에 적는다. 또 U5c 가 R-10 을 넣고 U7 이 `consent` 키를 넣으므로, 그 사이 커밋에서는 동의한 턴의 후속 질문(identity·new_person·schedule)이 R-10 에 걸려 409 가 된다 — 운영 반영이 U12 한 번이라 바깥 영향은 없지만 U5c·U6 리뷰가 이 상태를 결함으로 읽지 않도록 한 줄.
- **R-6 · 닫힌 목록 밖에서 조용히 깨지는 것.** `evaluation/recognition/probe.py:110`·`:190`·`:249` 는 운영 주소에 가입을 보내는 측정 도구다 — U4 뒤 422 가 된다. 고칠지(U4 목록에 추가), 그대로 두고 03-log 에 적을지 정한다. 프론트는 기존 Vitest·E2E 목 응답(`web/e2e/fixtures.ts:45`·`auth.spec.ts:10`)에 `notice_required` 가 없다 — U9a 에 "필드가 `true` 일 때만 모달" 을 적어야 `u9a-test-diff` 가 `auth.test.tsx` + `notice.test.tsx` 로 닫힌다.
- **R-7 · 계획이 비워 둬서 구현 에이전트가 지어내야 하는 값**(후보와 함께 계획에 한 줄씩):
  1. U2 "선형 시간(역추적 폭발 시험 1건)" 의 판정 — (a) 2000자 최악 입력 1회 실행 시간 상한을 수로 (b) 시간 대신 구조 단언(중첩 수량자 없는 정규식 목록 검사). 시간 상한은 기기마다 흔들린다.
  2. U5a "자리표시만으로 된 사실 값 거부" 의 단위와 정의 — (a) 그 `update_person` 제안 전체를 거부 (b) 그 사실 항목만 뺀다(게이트는 제안 단위로 거부한다 — `RejectedProposal(index, …)`). "자리표시만" = 공백을 뺀 값이 자리표시 문자열과 같음 / 자리표시를 포함함.
  3. U7 재개 방어(1847·1877 앞)에 걸렸을 때 — (a) 별칭·인물 저장만 건너뛰고 딸린 기록은 그대로 (b) 딸린 제안도 버리고 이름 거부 문구. `CR-009.md` U7 ⑦ 이 "각각 시험" 을 요구하므로 기대값이 필요하다.
  4. U7 부속 문구 "이 일정은 민감한 내용이라 브리핑과 알림을 보내지 않아요." 를 답에 붙이는 조건(동의 턴에서 일정이 저장됐을 때마다 / 재개 턴 포함)과 그 단언. 148행 파일 목록에 문구는 있으나 수용 기준에 없다.
  5. U5c `cleanup_expired` 가 예외를 내면 브리핑 반복을 막지 않는다는 것(사용자 반복과 같은 try 규약)과 그 시험.
  6. U5a `guard_check`(결정 `masked`) 행을 `turn_trace_range` 의 "직전 최대 id" 를 읽기 **전에** 쓴다는 순서 — R-2 는 `guard_check` trace 가 남는다고 한다.
  7. U9b "채팅 차단 안내·거절 줄 표시" 의 수용 기준(168행에는 칩 DOM·가림·한글 이름만 있다)과, 가린 상태에서 무엇이 보이는지(배지·범주 이름·날짜).
  8. U1 조회형 민감 문장의 개수와, 우회 20·조회형이 "범주·유형별 15~20" 셈에 드는지(검사기가 무엇을 세는지).
  9. `POST /auth/privacy-notice` 를 이미 동의한 계정이 다시 부를 때(204 그대로 / 시각 갱신 여부).
- **R-8 · 판정 명령의 이름 고르기.** `-k chain`·`-k monotone` 은 시험 이름에 그 낱말이 없으면 0건 선택(exit 5)이고 `-k name` 은 `display_name` 등 다른 시험까지 고른다. U7 에 "시험 함수 이름에 `chain`·`monotone`·`name_rule` 을 넣는다" 와 선택된 시험 수 > 0 확인을 적는다(D20 ① 표는 `-k name` 그대로 두어도 된다).
- **R-9 · U2 의 test 미열람 판정이 약하다.** `grep -rn "test.jsonl" app evaluation/sensitive_guard/run.py` 는 러너가 경로를 `f"{split}.jsonl"` 로 만들면 0줄이면서 test 를 열 수 있다. "U2 시점 러너는 `--split test` 를 거부한다(종료 코드 ≠ 0)" 를 시험 1건으로 더한다. 사용자의 낱말 목록 검토(101행·234행)가 다음 단위를 막는 관문인지 아닌지도 적는다(4절 Q2).
- **R-10 · U12 절차.** 문서로는 실행 가능하다(E12 — I 절과 같은 명령 모양, 기동 시 `alembic upgrade head`, 백업 선례). 빈 곳: ① `pg_dump …` 명령 전문과 백업 파일 확인(크기·끝줄)이 J 절에 들어가야 한다 ② **되돌릴 수 있는 창은 ⑥ 과 ⑦ 사이뿐**이다 — ⑦ 에서 사용자가 민감 문장 칩에 답하면 `kind='sensitive'` 행이 생겨 downgrade 가 실패한다. 되돌릴지 판단하는 시점을 ⑥ 뒤로 못 박는다 ③ `alembic upgrade` 자체가 실패해 backend 가 뜨지 않는 경우의 분기(DDL 이 트랜잭션 안이라 0005 로 남는다 → `git checkout <이전>` → `up -d --build`, downgrade 불필요) ④ 백업 복원 명령 순서(삭제를 동반하므로 사용자가 직접 실행 — `security.md` 6절) ⑤ downgrade 가 성공하면 `users.privacy_notice_*` 두 컬럼(고지 동의 기록)이 사라진다는 것 ⑥ "로컬 운영 구성 예행" 의 증거 이름을 U12 수용 기준에 넣는다(민감 행이 있을 때 downgrade 실패 예행 포함) ⑦ 배포 전 열려 있던 탭은 새로고침 전까지 옛 화면이라 403 에 모달이 뜨지 않는다 — ⑦ 사용자 확인 순서에 새로고침.
- **R-11 · D20 ① 표 #13 과 계획의 차이.** 카드의 판정 명령은 `pytest tests/test_guard_messages.py` 하나, 단위 칸은 "U4·U5a·U5b·U6·U7·U8·U9a" 인데 계획은 ④⑤ 를 프론트(`notice.test.tsx`)에 두고 U4 에는 문구가 없으며 U5c 가 문구를 더한다(206행). 계획 통과 뒤 카드 #13 의 판정 명령·단위 칸을 맞춘다. 판 번호와 문구의 묶음이 기계적이지 않다는 한계는 58·226행에 적혀 있다.
- **R-12 · 시험 세트의 식별번호 모양 문자열.** dev·test 에 주민등록번호·계좌번호·카드번호·비밀번호 모양 문장이 들어가 공개 저장소에 올라간다. README 에 "전부 지어낸 값(실재하지 않는 형식·검증 숫자 불일치)" 규칙을 적고 검사기 항목으로 둔다. `secret-guard`·`save_evidence` 의 비밀 패턴이 비밀번호 예문에 걸리면 우회하지 않고 문장을 바꾼다(`security.md` 6절).
- **R-13 · 사소한 것.** 22행 백업 선례 인용은 `packages/P9b-auth/03-log.md:316` 이다. 175행 "(사용자 결정 필요 D-3)"·168행 "(사용자 결정 필요 D-2)"·149행 "아래 '사용자 결정 필요' D-1" 과 214행 절 제목은 235행에서 확정됐으므로 "확정" 으로 고친다. `POST /answers/{id}` 에 옵션 밖 문자열을 보내면 `answer_question` 의 `tool_error` trace 입력에 그 문자열이 남는다(`app/tools/context.py` — 기존 동작, 화면은 칩 문자열만 보낸다) — U5a 전수 `LIKE` 의 범위 밖임을 적거나 한 건 시험한다.

### 3.4 (1차 이력) VR1~VR8 · CR-009 8.6 판정 — 재검증에서 VR3 은 닫힘(M1), VR6 의 결정 22 는 닫힘(M4, 잔여 M5)

| 항목 | 판정 | 근거 |
|------|------|------|
| VR1 사후 조회 재개 | 닫힘 | 63행. `_run_query_turn` 은 `Proposal` 을 받아 `_query_mentions(proposal)` 로 언급을 모으고(E2, 1238·1300행) 게이트 판정과 무관하다 — `query_calls` 로 `Proposal` 을 다시 만들면 된다. `answerer=None` 이면 1412~1416행이 `answerer_from_env()`. 기록 쪽은 R-4 |
| VR2 이름 규칙 자리 | 닫힘(잔여 R-1·R-7-3) | 64행 네 자리. `_ordered_mentions`·`_pending_calls_from` 은 둘 다 `verdict.accepted` 만 읽으므로(323~342·398~430행) 새 `GateVerdict` 에서 뺀 제안은 ER·되묻기 context·기록 어디에도 닿지 않는다. 재개는 `_drop_calls_for_mention`(1641행, `PendingCall` 모양)이 맞다 |
| VR3 U4 시험 파일 | **덜 닫힘 — M1** | 가입 시험 5파일·도우미는 맞다(E9, `User(` 는 `tests/auth_helpers.py:70` 한 곳). 주기 작업 시험 목록이 빠졌다. `git diff --stat <해시> -- …` 모양은 116·151·163·212행 모두 `..` 없이 적혔다 |
| VR5 고지 문구 주인 | 닫힘(잔여 R-11) | 55~58행 — 서버는 채팅 문구, 프론트는 ④⑤, 만드는 단위 U5a·U9a |
| VR6 이름 규칙 근거 trace | 닫힘(결정 22 는 M4) | 67행 — 언급 문자열 0, 인물 id 는 기존 키 `person_id`(R-12) |
| VR7 미동의 건너뜀 자리 | 닫힘(여파 M1, 잔여 R-3) | 68행 — `_due_user_ids` 조인, 건너뛴 계정은 `_run_for_user` 에 들어가지 않아 `briefing_run` trace 가 쌓이지 않는다(E5) |
| VR8 `chat_message_id` | 닫힘 | 69행 — 라우트가 `append_chat_message` 반환 id 를 들고 `attach_turn_refs` 로 덧붙인다. 사후 질문은 `chat` 라우트의 `run_turn` 에서만 생긴다(답 라우트의 `run_turn` 은 동의 문맥이 있어 사후 검사를 건너뛴다) |
| 8.6 행 번호 | 닫힘 | E2 — 전부 일치 |
| 8.6 FIX-015 해시 | 닫힘 | E11 — `6e7b286` |
| 8.6 `loop.py:1322` | 닫힘 | E2 — "결정 I (a) -- apply_resolution() 을 부르지 않는다(별칭 누적 0)" |
| 8.6 `turn_trace_range` 겹침 | 닫힘 | 73행 — `sending` 잠금(E11), 넓게 지우는 쪽 |
| 8.6 R-10 규칙 목록 변경 창 | 닫힘 | 74행 — U12 ③ 기록 |
| 8.6 RR7 나머지 | 닫힘 | 19행 — 계정 행을 직접 만드는 시험 0(E9) |

### 3.5 (1차 이력) 그 밖의 판정

- **사용자 결정 22건 + D-1~D-3**: 계획과 어긋나는 자리는 M4(결정 22) 하나다. D-1(149·218·235행)·D-2(168·219·235행)·D-3(175·220·235행)은 반영됐다. 결정 5·8·9·10·11·12·13·14·15·16·17·21 은 U4·U5c·U1·U5b·U6·U7·U12 수용 기준에 있다.
- **계획이 사용자 결정 없이 정한 값**: 사용자 결정과 부딪히는 것은 찾지 못했다. 계획이 스스로 정한 것은 카드가 계획에 넘긴 것들이다 — `guard_name_rule` trace 모양·`REASON_NAME_RULE`(VR6), 미동의 건너뜀 trace 0·`users` 행 없는 소유자 제외(VR7, R-3), `POST /auth/privacy-notice` 204·본문 없음(42~53행 계약 표), `attach_turn_refs`(VR8). 빈자리는 R-7 의 9건.
- **툴 7종·`app/er/`**: 산출물 목록(31~40행)에 `app/er/` 파일이 없고 U7 판정 `git diff --stat <기준> -- app/er` 가 빈 출력을 요구한다. 툴 4개(`add_event`·`add_schedule`·`update_person`·`get_briefing`)는 본문만 바뀌고 인자가 늘지 않는다 — 수용 기준 #12 와 파일 목록은 양립한다. 단 M4 의 해법이 `app/er/` 를 건드리지 않아야 한다.
- **핵심 계약 변이 후보**: U1~U10 모두 1개 이상 있다(97·104·111·117·124·131·138·145·152·158·164·170·176행). U11 이 U5a·U5b·U5c·U6·U7·U8 각 1개와 downgrade 가드를 다시 돌린다.
- **검증 명령의 실행 가능성**: 기존 파일을 가리키는 이름은 전부 실재한다(E10). 실행되지 않거나 그대로 실패하는 것은 U3 `u3-migration`(M2)과 U4 전체 pytest(M1) 둘이다.

## 4. 결정

결과: 통과

(재검증 3회차 — 01-plan 개정 2 기준)

판정 근거: 2회차 [필수] 둘(M2-잔여·M5)이 닫혔고(3.A.2), 2회차 [권고] N-R1~N-R8 이 전부 반영됐다(3.A.3). 점검표 8행 통과. verify-plan `FAIL=0`, 점검표 `PASS  보류 0건`(`evidence/20261122-1732-verify-plan.txt`). 개정 2 가 새로 만든 모순·코드 불일치·실행 불가능한 명령·임의로 정한 사용자에게 보이는 동작은 찾지 못했다(3.A.6).

남은 것은 [권고] 7건(P3-R1~P3-R7, 3.A.5)이고 전부 해당 단위 커밋 전 리뷰에서 닫을 수 있다. 그중 P3-R1(U4 — `tests/test_auth_nickname.py:83·85`, `tests/test_auth_helpers.py:105` 의 `MeOut` 사전 동등 비교가 닫힌 목록에 없다)은 "고정 단언 전수 확인" 절이 놓친 것이지만, U4 자신의 판정 명령 `u4-auth` 가 그 파일을 돌려 반드시 드러나고 U4 에 "목록 밖에서 깨지면 멈추고 보고" 문장이 있으며 고칠 내용이 하나로 정해지므로 계획 단계 필수로 보지 않았다(3.A.4). 활성화 전에 architect 가 세 줄(과 P3-R2 의 공통 문장)을 넣으면 U4 에서 멈춤·보고 왕복 1회를 아낀다 — 넣어도 이 판정은 그대로 유효하고 재검증은 필요 없다(닫힌 목록을 넓히는 쪽의 수정뿐이다).

사용자에게 물을 것: **없다.** D-1~D-4·결정 22 의 "글자까지 같음"·U2 낱말 목록 검토는 관문 아님 — 모두 계획에 확정값 그대로 있다.

사용자에게 알리기만 하면 되는 것(2회차와 같다 — 새로 생긴 것 없음):
- 결정 22 로 통과하려면 그 턴에 동의가 있어야 한다 — 동의 문맥 없이 기존 민감 별칭과 같은 언급이 나오면(추출 LLM 이 발화에 없는 낱말을 낸 드문 경우) 이름 거부된다.
- D-4 (a) 의 새 인물 갈래는 인물 판정이 끝난 뒤 질문 없이 버린다(병합·생성 0) — D20 R-7 에 한 줄이 들어갔다.
- 인물 카드의 가린 민감 항목에는 배지·범주 이름과 함께 사건 날짜·종류, 사실 키 이름이 보인다(값·내용·일정 제목은 가림). U12 화면 확인 때 본다.
- 미동의 계정 건너뜀은 trace 를 남기지 않는다 · 운영에서 되돌릴 수 있는 것은 사용자가 민감 문장 칩에 답하기 전까지다.

(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)

### 4.0.1 2회차 결정 (이력 — 01-plan 개정 1 기준)

2회차 결과 — 보류.

보류 사유: [필수] 2건 — **M2-잔여**(U3 닫힌 목록에 `tests/test_api.py:93` 없음, 함께 `tests/test_migration_0004.py:110`)와 **M5**(U7b 수용 기준의 임베딩 단언이 `search_person` 질의 임베딩·D20 결정 22 와 맞지 않음). 점검표는 3행이 보류(M5), 나머지 7행 통과. M2-잔여는 점검표 밖(단위의 실행 가능성) 소견이다. 1차 [필수] 넷 중 M1·M3·M4 는 닫혔고 M2 는 한 건이 남았다. 1차 [권고] R-1~R-13 은 전부 반영됐다.

두 건 모두 계획 문장 한두 줄을 고치면 닫힌다(고칠 자리는 3.0.4). 고친 뒤의 재검증은 그 두 자리와 verify-plan 재실행으로 충분하다 — 나머지 판정은 이 문서 그대로 유효하다.

[권고] 8건(N-R1~N-R8, 3.0.5)은 계획을 고칠 때 함께 넣거나 해당 단위(U4·U5c·U6·U7b·U9a) 커밋 전 리뷰에서 닫는다.

사용자에게 물을 것: **없다.** D-1~D-4 와 결정 22 의 "글자까지 같음" 은 계획에 그대로 들어갔고, 개정 1 이 스스로 정한 값은 카드·기존 코드 관례에서 나온다(3.0.6).

사용자에게 알리기만 하면 되는 것:
- 결정 22 로 통과하려면 그 턴에 동의가 있어야 한다 — 동의 문맥 없이 기존 민감 별칭과 같은 언급이 나오면(추출 LLM 이 발화에 없는 낱말을 낸 드문 경우) 이름 거부된다.
- D-4 확정안의 새 인물 밴드 거부는 인물 판정이 끝난 뒤 질문 없이 버리는 갈래다 — 원칙2 문장("미만은 반드시 `ask_user`")의 글자와 다르므로 D20 R-7 에 한 줄을 더한다(N-R3). 병합·생성은 0 이다.
- 인물 카드의 가린 민감 항목에는 배지·범주 이름과 함께 사건 날짜·종류, 사실 키 이름이 보인다(값·내용·일정 제목은 가림). U12 화면 확인 때 본다.
- 1차에서 알린 것은 그대로다: 미동의 계정 건너뜀은 trace 를 남기지 않는다 · 운영에서 되돌릴 수 있는 것은 사용자가 민감 문장 칩에 답하기 전까지다.

(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)

### 4.1 1차 결정 (이력 — 01-plan 개정 전)

1차 결과 — 보류.

보류 사유: [필수] 4건(M1·M2·M3·M4). 점검표는 3행이 보류(M4), 나머지 7행 통과. M1·M2·M3 은 점검표 밖(단위의 실행 가능성·크기) 소견이다.

사용자에게 물을 것(계획을 고칠 때 모아서):
- **Q1(M4)** 저장된 별칭과 공백·대소문자만 다른 언급을 통과시킬 때 — (a) 통과시키되 새 별칭 행·임베딩은 만들지 않는다(D20 문장 그대로, 방법은 architect) (b) 글자까지 같은 언급만 통과, 변형은 이름 거부 (c) 변형 별칭이 새로 저장되는 것을 받아들인다(D20 R-7 문장 수정). (a)·(b) 는 사용자 결정 22 의 문장 안이라 architect 가 고를 수 있고, (c) 만 사용자 결정이다.
- **Q2(R-9)** U2 낱말·정규식 목록 검토를 U5a 착수 전 관문으로 둘지, U12 전 아무 때나 볼지.
- 알리기만 하면 되는 것: 미동의 계정 건너뜀은 trace 를 남기지 않는다(R-3) · 운영에서 되돌릴 수 있는 것은 사용자가 민감 문장 칩에 답하기 전까지다(R-10 ②) · `evaluation/recognition/probe.py` 는 U4 뒤 가입이 막힌다(R-6).

(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)
