# P9d-sensitive-guard · 계획 (01-plan)

상태: **개정 2(2026-11-22, architect — 02-plan-verify 2회차 보류 [필수] M2-잔여·M5·[권고] N-R1~N-R8 반영 + 고정 단언 전수 확인. 개정 1 은 1차 보류 M1~M4·R-1~R-13 반영. 처리표는 맨 끝 "개정 이력")** → verify-plan → verifier 02-plan-verify 재검증 → `active: P9d-sensitive-guard` | 담당: backend-agent(sonnet — U2·U3·U4·U5a·U5b·U5c·U6·U7a·U7b·U8) · frontend-agent(sonnet — U9a·U9b) · eval-agent(opus — U1·U10) · verifier(fable — 02-plan-verify·단위 커밋 전 리뷰·U1 라벨 검수 판정·U11 04-review) · 메인 세션(U0 완료·U12 운영 반영 SSH·증거 저장) · 사용자(낱말 목록 검토·U12 화면 확인·완성 확인) | 작성: 2026-11-22
태그 — 패키지: P9d-sensitive-guard · 닫는 검증: (직접 R 없음 — 간접 R7 R10 R12 R19) · 기대는 결정: D20(신설) · D1 · D2 · D14 · D16 · D17 · D18 · D19 · D5 · 구현하는 명세: S3.1(보충 0006) · S3.2 · S3.4 · S3.5 · S3.6 · S3.7 · 관련 원칙: 원칙1 원칙2 원칙4 원칙5 원칙6 원칙7 원칙8 원칙9 · 출처 CR: CR-009(개정 3 + 사용자 결정 22)
의존: P5-loop · P5b-query-turn · P6-memory · P6-briefing · P7-push(모두 04-review `결과: 완료`) · P4 게이트(P4b-er-redesign 통과)
관련(선행 완료 조건이 아님): CR-009 문서 이행 커밋 `6d97217`(D20·카드 보충·CLAUDE.md·backlog) — 충족. P9b-auth 는 **보류**(메인 세션 결정, 04-review 열림 — 이 패키지는 P9b 산출물 위에 더하고 P9b 를 닫는 조건으로 삼지 않는다). P9-infra 04-review 도 열림(영향 없음). P9c-briefing-calendar 는 이 패키지 뒤(사용자 "가드레일 본작업 먼저").

- **기준 해시** `<기준>` = **`6d97217`**(CR-009 문서 이행). 코드 행 번호는 `cef47d0` 이후 제품 코드 변경이 없어 아래 "코드에서 확인한 사실" 이 그대로 맞다(architect 가 2026-11-22 직접 열어 확인).
- **기준선**: U1 시작 전 메인 세션이 재측정해 03-log 에 — `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q`(실패 0·skip 0, 통과 수 기록) · `npm --prefix web exec -- vitest run --root web`(FIX-039 뒤 246) · `tools_check` 7/7 · mypy 기준선. 판정 명령의 `python3 -m pytest`·`python3 scripts/…` 는 `.venv/bin/python` 으로 읽는다(이 기기의 anaconda `python3` 은 `pgvector` 가 없다 — P9b 01-plan 과 같은 규칙).
- **판정 규칙(P9b 01-plan "판정 방법" 그대로)**: 증거는 `python3 .claude/scripts/save_evidence.py P9d-sensitive-guard <이름> -- <명령>`. 따옴표·`$`·`|` 가 든 명령은 스크래치패드 `<SCR>/<이름>.sh` 로 Write 해 `-- bash <SCR>/<이름>.sh`. `alembic` 은 `.venv/bin/python -m alembic`. **`git diff --stat` 은 커밋 전 작업 트리를 보려고 `git diff --stat <해시> -- <경로>`(`..` 없이) 모양으로 쓴다**(재검토 VR3 ③). `ruff --fix` 금지. 단언은 각 단위의 "닫힌 목록" 안에서만 바꾼다.

### 코드에서 확인한 사실 (계획의 전제 — `6d97217` = 제품 코드 `cef47d0`)
- 루프 `app/agent/loop.py`: `_ordered_mentions` 323~342(호출은 `_resolve_mentions_impl` 552행 한 곳) · `_pending_calls_from` 398~430(게이트 통과 `execute` 버킷 중 미확정 언급의 제안을 되묻기 context 에 담는다 — 인자는 `Proposal`·`GateVerdict`) · `_apply_resume_byte_limit` 451(`PendingResume` 의 `held_drafts` 만 비운다) · `_extend_identity_payload` 471 · `_extend_new_person_payload` 481 · `_extend_for_ask` 504 · `_resolve_mentions_impl` 541(`resolve()` 580행, merge 면 `apply_resolution` 583행) · `_propose` 691 · `_gate` 704 · `_ask_schedule` 793 · `_execute_call` 869~897(`update_person` 은 `facts`·`new_alias` 만, `display_name` 0, `create_person` 호출 0) · `run_turn` 1087(`_propose` 1124 → `_gate` 1126 → `if proposal.intent == INTENT_QUERY: return _run_query_turn(…)` 1128 → `resolve_mentions` 1139 → `_record` 1141, `TurnResult.trace_ids` 4개 1180~1184) · `_query_mentions` 1238 · `_read_card` 1263 · `_run_query_turn` 1286(언급마다 `resolve()` 1309, merge 면 **`apply_resolution` 을 부르지 않는다 — 1322행 주석 "별칭 누적 0"** 직접 확인) · `_followup_new_person_turn` 1497 · `_synthetic_proposal_and_verdict` 1583 · `_drop_calls_for_mention` 1641(인자 `list[PendingCall]`) · `_resume_query_turn` 1650(identity 답 전용 — `candidate_ids[answer]`) · `resume_turn` 1710(identity 답 별칭 1847 · identity 거절 → `_followup_new_person_turn` 1856~1863 · new_person 답 `create_person(display_name=mention, aliases=[mention])` 1877~1883).
- 질문 context: ER 되묻기 context 는 `app/er/pipeline.py` 가 만들고 `context["utterance"]` 를 1건 넣는다. 루프는 `_extend_for_ask` 에서 `context["resume"]`(= `PendingResume.to_dict()`, `app/agent/types.py` 370~417)을 더한다. `ResumeInput.__post_init__`(`types.py:434`)가 `QUESTION_KINDS` 를 검사한다. `ask_user` 는 `@traced`(`app/tools/questions.py:183`), `_AFFIRMATIVE_REQUIRED_KINDS` 96행, 긍정 규약 164~178행, `answer_question` 237행(`@traced`, 입력은 질문 id·답).
- 라우트 `app/api/routes.py`: `submit_answer` 212~302(의존성 `judge`·`embedder`·`extractor` 뿐) · `_record_loop_error` 305(`input={"utterance": …}`) · `chat` 333~416(389행 `append_chat_message` 가 루프 **앞**) · 읽기 라우트 491·500·513·522·533·549 · `POST /briefings/run` 433. `answerer` 를 라우트가 넘기지 않는다 — `None` 이면 `_query_finish` 1412~1416 이 `answerer_from_env()`.
- 대화 세션 id: 대화 ctx `chat:<user_id>`(`deps.py:120`·`:218`), 답 ctx 는 질문 행의 `session_id`(`:152`), 브리핑 주기 작업 `briefing-scheduler:<uuid4>`(`scheduler.py:141`), 수동 브리핑 `briefing:<uuid4>`(`run.py:183`) — 대화 세션 구간에 섞이지 않는다.
- 주기 작업 `app/briefing/scheduler.py`: `_due_user_ids` 107~122(`persons.user_id` 에서, `users` 를 읽지 않음) → `default_run_once` 158~178 → 사용자마다 `_run_for_user` 125~155 → `run_briefings`(`briefing_run` trace 는 `run.py:321`).
- 프론트: 칩 `QuestionChips`(`web/src/screens/ChatScreen.tsx:88~124`)는 `kind` 를 보지 않는다(`kind` 는 `web/src/api/types.ts:68` 에만). 전송 잠금 `sending`(`ChatScreen.tsx:128`·`190`·`317`) — 한 탭에서 동시 전송 0. 가입 본문 단언 `web/src/__tests__/auth.test.tsx:272`.
- 시험 도우미: `tests/auth_helpers.py::make_user`(58행 — 계정 행을 만드는 유일한 도우미, `User(` 는 이 파일에만)·`logged_in_client`(108행, `make_user` 를 부른다). `tests/conftest.py` 에는 계정 픽스처가 없다. 가입을 직접 보내는 시험: `test_auth_api.py`·`test_auth_nickname.py`·`test_auth_availability.py`·`test_auth_origin.py`·`test_auth_required_routes.py`(grep `auth/signup` 16곳/5파일). 저장소의 그 밖 가입 호출: `evaluation/recognition/probe.py:110·190·249`(운영 주소 측정 도구). **(개정 1 — M1) `default_run_once` 를 부르는 시험은 grep `default_run_once|_due_user_ids` 로 4개 파일**: `test_briefing_scheduler_users.py`(13곳 — 인물을 `users` 행 없이 만든다) · `test_push_wiring.py`(8곳 — 픽스처 `scheduler_env` 가 `Person(user_id="local")` 을 `users` 행 없이 만들고 `briefed_at is not None` 을 단언, 349·372행) · `test_briefing_scheduler.py`(5줄 — 203행은 `run_briefings` 를 가짜로 바꾼 뒤 `default_run_once()` 를 부르는데, 이 시험은 `session_scope` 를 바꾸지 않아 주기 작업이 시험 세션과 **다른 세션**으로 돌고 거기서는 대상이 0명이다 → `NO_USER_MARKER` 로 1회(`scheduler.py:171~172`) + 수동 1회 = `len(calls) == 2`. `users` 조인을 더해도 대상은 여전히 0명이라 그대로 성립 — 고칠 필요 없음, U4 가 실행으로 확인. 개정 2 — 02-plan-verify N-R4 로 이유 문장 정정) · `test_commit_boundaries.py`(1곳 — 407행 docstring 언급뿐, 호출 0).
- 스키마 고정 단언(개정 1 — M2, 직접 읽음): `tests/test_schema_models.py` — `S3_1_TABLE_COLUMNS`(18~86행, 테이블별 컬럼 이름 집합) · 총 컬럼 `== 79`(158~165행) · `events` CHECK `len(checks) == 1`(176행) · `QUESTION_KINDS` `== 3`(205~210행) · CHECK 총 `== 5`(215~223행) · `NULLABLE_COLUMNS`(88~96행, **컬럼 이름 집합** — 같은 이름은 한 번만 센다)와 254~263행. `tests/test_schema_check.py:44` `len(sc.m.QUESTION_KINDS) == 3`(인덱스 13·UNIQUE 8 은 0006 이 인덱스·UNIQUE 를 더하지 않아 그대로). `tests/test_migration_0003.py:49` head 기준 `users` 컬럼 집합. `tests/test_migration_0004.py` `USERS_COLUMNS`(39행 정의, 111·169행은 head, **110·157행은 0003 상태** — 110행 `mig["columns_before"]`). `tests/test_migration_0005.py:110·111·196` head 리터럴 `"0005"`. **`tests/test_api.py:93` `body["alembic_revision"] == "0005"`**(`/health` 는 `alembic_version` 표를 읽고 시험 DB 는 세션 시작 때 `upgrade head` — 0005 때도 `c85a0e8` 이 이 줄을 고쳤다). `scripts/schema_check.py` 는 값 집합을 모델에서 읽어(`m.QUESTION_KINDS` 185행) 고칠 곳이 없다. 다른 단위가 깨뜨리는 고정 단언은 아래 "고정 단언 전수 확인" 절.
- 별칭 저장(개정 1 — M4, `app/tools/persons.py` 340~386 직접 읽음): `_add_alias` 는 `PersonAlias.alias == alias`(**글자 그대로**)로 있는지 보고, 없을 때만 `provider.embed([alias])` 뒤 INSERT 한다. 자동 연결은 `app/er/pipeline.py:465` `update_person(new_alias=resolution.mention)`, identity 답은 `loop.py:1847`, new_person 답은 `loop.py:1877`.
- ~~이름 정규화: `app/mcp_server/tools.py::name_key`~~ — (개정 1 — M4, 메인 세션 결정) 사용자 결정 22 의 "정확히 일치" 는 **글자까지 같음**(정규화 없음). `name_key` 는 쓰지 않는다.
- FIX-015 해시: `6e7b286`(`docs/wiki/fixes/FIX-015.md:84`). 태그 검색의 `36c288e`·`d79381a` 는 FIX-015 를 언급한 다른 커밋이다(검토 C1).
- 운영 재배포 절차: `docs/user-setup/13-user-todo-deploy.md` I 절(0005, `c85a0e8`) — SSH `git pull` → `compose -f docker-compose.prod.yml up -d --build`, 되돌리기는 backend 정지 → `alembic downgrade` → `git checkout <이전>` → `up -d --build`. 운영 DB 백업 선례: 서버 홈 `~/backup-20261118-pre-demo-fix.sql`(`pg_dump`, `docs/wiki/packages/P9b-auth/03-log.md:316`). 기동 시 `alembic upgrade head` 는 `docker/entrypoint.sh:10`.

## 목표
기획서 9장 리스크 표 "제3자 개인정보" 행(`docs/proposal.md:264`)의 대응을 실제 동작으로 만든다 — 사용자 원문 1 "누군가가 마약을 했다 이런식으로 해버리면 그냥 들어가네" 와 원문 3 "법적으로 문제가 되는 내용을 차단하고 싶은거야 혹은 사용자가 동의를 하면 들어갈 수 있게 … ChatGPT로 넘어간다는 알림이 있어야" 를 CR-009 · D20 대로 구현한다: LLM 호출 전 서버 규칙 검사, 식별·인증 정보 6종 가림, 민감 범주 5종 칩 동의(사전)와 규칙이 놓친 문장의 저장 전 확인(사후, 기록·조회 모두), 동의 기록과 거절·만료 시 원문 지우기, 민감 항목은 인물 카드에서만, 가입·재고지 OpenAI API 전송 고지, 리비전 0006, 시험 세트 평가, 운영 반영. 완화이며 기록 대상(제3자) 동의 문제는 풀지 않는다. 법적 판단을 하지 않는다.

## 범위
- 포함: CR-009 4.2 의 U1~U12(아래 작업 단위) — D20 결정 1~7·R-1~R-12·사용자 결정 1~22.
- 이 패키지에서 하지 않는 것: 기존 데이터 소급(사용자 결정 9 — 배포 전 데이터·저장 브리핑·식별 원문은 그대로, CR-009 W14) · 새 화면(재고지는 기존 화면 위 모달 — 원칙5, G14) · 법적 판단·약관 내용 단정 · 낱말 목록의 설정값화(코드 상수 한 파일) · 감지율 목표치(G21) · 인물 간 관계·상담(원칙7) · 툴 7종의 개수·시그니처 변경 · `app/er/` 판정 로직 변경 · 계정 삭제 · MCP 도구 추가.

## 산출물 (파일 경로)
- 평가 세트·도구(새): `evaluation/sensitive_guard/dev.jsonl` · `evaluation/sensitive_guard/test.jsonl` · `evaluation/sensitive_guard/README.md` · `evaluation/sensitive_guard/run.py` · `scripts/validate_sensitive_set.py`
- 가드 모듈(새): `app/guard/__init__.py` · `app/guard/rules.py` · `app/guard/detect.py` · `app/guard/mask.py` · `app/guard/names.py` · `app/guard/messages.py` · `app/guard/consent.py`
- 리비전: `alembic/versions/0006_sensitive_guard.py`
- 고친 백엔드: `app/db/models.py` · `app/settings.py` · `app/auth/routes.py` · `app/auth/deps.py` · `app/api/routes.py` · `app/api/read.py` · `app/api/schemas.py` · `app/agent/loop.py` · `app/agent/types.py` · `app/agent/propose.py` · `app/agent/gate.py` · `app/agent/respond.py` · `app/tools/context.py` · `app/tools/questions.py` · `app/tools/persons.py` · `app/tools/records.py` · `app/tools/briefing.py` · `app/briefing/inputs.py` · `app/briefing/select.py` · `app/briefing/scheduler.py` · `app/memory/promote.py` · `app/memory/patterns.py` · `app/memory/direct_facts.py` · `app/memory/extract.py` · `app/mcp_server/tools.py`
- 시험(새): `tests/test_guard_rules.py` · `tests/test_migration_0006.py` · `tests/test_privacy_notice.py` · `tests/test_guard_mask.py` · `tests/test_guard_messages.py` · `tests/test_guard_pre.py` · `tests/test_guard_resume.py` · `tests/test_guard_posthoc.py` · `tests/test_guard_storage.py` · `tests/test_guard_names.py` · `tests/test_guard_export.py`
- 시험(닫힌 목록 안에서 고침 — U3): `tests/test_schema_models.py` · `tests/test_schema_check.py` · `tests/test_migration_0003.py` · `tests/test_migration_0004.py` · `tests/test_migration_0005.py` · `tests/test_api.py`
- 시험(닫힌 목록 안에서 고침 — U5a): `tests/test_agent_query_gate.py`(101·102행 거부 사유 수 7 → 8)
- 시험(닫힌 목록 안에서 고침 — U6): `tests/test_agent_query_types.py`(38행 `PROPOSAL_SCHEMA` 최상위 속성 집합)
- 시험(닫힌 목록 안에서 고침 — U8): `tests/test_api_read_persons.py`(189행 다가오는 일정 항목 키 집합) · `tests/test_mcp_tools.py`(6행 docstring·293행 카드 동등 비교)
- 시험·도구(닫힌 목록 안에서 고침 — U4): `tests/auth_helpers.py` · `tests/test_auth_helpers.py`(105행 `MeOut` 사전 동등 비교 — P3-R1) · `tests/test_auth_api.py` · `tests/test_auth_nickname.py` · `tests/test_auth_availability.py` · `tests/test_auth_origin.py` · `tests/test_auth_required_routes.py` · `tests/test_briefing_scheduler_users.py` · `tests/test_push_wiring.py` · `evaluation/recognition/probe.py`
- 시험(닫힌 목록 안에서 고침 — U7b): `tests/test_agent_loop.py`(426·483·600행의 제안 인덱스 등식에 "이름 규칙으로 버린 인덱스" 항 — R-1)
- 프론트: `web/src/lib/privacyNotice.ts`(새) · `web/src/screens/AuthScreen.tsx` · `web/src/components/AppShell.tsx` · `web/src/api/types.ts` · `web/src/api/client.ts` · `web/src/screens/ChatScreen.tsx` · `web/src/screens/PersonCardScreen.tsx` · `web/src/lib/labels.ts` · `web/src/__tests__/auth.test.tsx` · `web/src/__tests__/chat.test.tsx` · `web/src/__tests__/card.test.tsx` · `web/src/__tests__/labels.test.tsx` · `web/src/__tests__/notice.test.tsx`(새)
- 보고서: `reports/sensitive_guard.md` · `reports/sensitive_guard_metrics.json`
- 문서: `docs/RUNNING.md`(만료 정리·스위치 한 줄) · `docs/user-setup/13-user-todo-deploy.md`(J 절 — 0006 반영·되돌리기) · `docs/wiki/packages/P9d-sensitive-guard/03-log.md`·`tests.md`·`04-review.md`·`evidence/`

### 값으로 고정하는 계약 (U4·U5·U6 백엔드 ↔ U9a·U9b 프론트 — 프론트가 백엔드 커밋 전에 목 응답으로 시작할 수 있게)
| 계약 | 값 |
|---|---|
| 가입 본문 | `{username, password, nickname, privacy_notice_accepted: true}` — 없거나 `false` 면 422 `{"detail":{"code":"notice_required"}}`, `users` 행 0. **본문 스키마에서는 선택 필드(`bool \| None = None`)로 받고 라우트가 판정한다** — 필수 필드로 두면 FastAPI 기본 검증 422(`detail` 이 목록)가 먼저 나가므로, 기존 `_invalid`(`app/auth/routes.py:102~103`, `HTTPException(422, detail={"code": …})`)와 같은 모양으로 낸다(N-R7) |
| `/auth/me`·로그인·가입 응답 `MeOut` | 기존 필드 + `notice_required: bool` |
| 재고지 동의 | `POST /auth/privacy-notice`(본문 없음, 로그인 필수) → 204. 판 번호가 현재보다 낮거나 NULL 이면 `users.privacy_notice_version = PRIVACY_NOTICE_VERSION`, `privacy_notice_accepted_at = now`. **이미 현재 판에 동의한 계정이 다시 부르면 204 이고 행 변경 0**(처음 동의 시각을 동의 기록으로 남긴다 — R-7 ⑨) |
| 미동의 403 | `POST /chat`·`POST /answers/{id}`·`POST /briefings/run` → 403 `{"detail":{"code":"notice_required"}}`(LLM·임베딩 0) |
| 사전·사후 칩 | 기존 `ChatPendingQuestionOut{question_id,status,kind,question,options}` 그대로, `kind="sensitive"` |
| 차단 안내 | `reply` 끝에 D20 확정 문구 ③ 한 줄(새 응답 필드 없음) |
| 거절 뒤 | 응답 `reply` = "기억하지 않았어요.", `GET /chat/history` 의 그 사용자 줄 `content` = "(기억하지 않은 민감한 내용)" |
| 카드 항목 | `PersonCardOut` 의 사실·패턴·타임라인·다가오는 일정 항목에 `sensitive_category: str \| null`(카드 라우트만 값이 있음. MCP 는 키 제거) |
| 판 번호 | `PRIVACY_NOTICE_VERSION = 1`(`app/settings.py`) |

### 가드 문구 상수의 주인 (재검토 VR5 닫음)
- **서버(`app/guard/messages.py`)**: 채팅에 나가는 문구 — ① 사전 동의 칩(U5b) · ② 사후 확인 칩·⑥ 사후 조회 칩(U6) · ③ 차단 안내(U5a) · 부속 거절 뒤 답·대체 줄(U5c) · 민감 일정(U7a) · 이름 거부(U7b) · 조회 안내(U8). **파일과 `tests/test_guard_messages.py` 는 U5a 가 만들고**, 뒤 단위가 자기 문구 상수와 단언을 더한다. 단언 = D20 "확정 문구" 와 글자 일치 + `BRIEFING_FORBIDDEN_EXPRESSIONS` 어느 항목도 포함하지 않음(목록은 검사 도구로만 import, 합치지 않음).
- **프론트(`web/src/lib/privacyNotice.ts`)**: ④ 가입 고지 문단·체크 문구 · ⑤ 재고지 모달 제목·문단·안내·버튼. 서버는 문구를 갖지 않고 판 번호만 갖는다. **U9a 가 만든다.** 단언 = `web/src/__tests__/notice.test.tsx` 가 D20 문장과 글자 일치.
- **판 번호와 문구 묶기**: 문구 ④⑤ 를 바꾸는 커밋은 `PRIVACY_NOTICE_VERSION` 을 같은 커밋에서 올린다. 판정: U4 `test_privacy_notice.py` 가 `PRIVACY_NOTICE_VERSION == 1` 을, U9a `notice.test.tsx` 가 문구 전문을 단언 — 둘 중 하나만 바꾸면 다른 쪽이 그대로라 리뷰에서 드러난다(기계적 묶기는 아니다 — 한계로 리스크 절에).

### 재검토 VR1~VR8 · CR-009 8.6 닫기 (이 계획이 정한 것)
| 항목 | 닫은 방법 |
|---|---|
| **VR1** 사후 조회 재개 (+ 개정 1 — R-4 기록 쪽) | 사후 질문 context 에 **기록·조회 공통으로** `intent`·`utterance`·`proposal_calls`(제안의 `tool_calls` **전부** — `{index, name, args}` 목록, `create_person` 힌트 제안 포함)·`categories`(제안의 `sensitive_categories`) 를 싣는다(`PendingResume` 은 쓰지 않는다 — 언급 하나 모양이라 사후 질문의 여러 언급·`hint_only` 힌트를 담지 못한다). 긍정 재개는 `resume_turn` 의 `kind=="sensitive"`·`phase=="post"` 분기에서 `Proposal` 을 다시 만들고 **`_gate` 를 다시 돌린 뒤**(결정적, LLM 0) `run_turn` 1128~1187행을 새 함수 `_continue_after_gate(ctx, utterance, proposal, verdict, …)` 로 뽑아 그대로 탄다 — 조회면 `_run_query_turn`(언급 해석부터, `answerer=None` → `answerer_from_env()`), 기록이면 `resolve_mentions` → `_record`. 인식 LLM 재호출 0. `_resume_query_turn`(identity 답 전용)·`_synthetic_proposal_and_verdict` 는 쓰지 않는다. `run_turn` 도 같은 함수를 부르게 바꿔 경로가 하나다(표시 없는 턴의 동작은 그대로 — U6 ③). (U6) |
| **VR2** 이름 규칙 자리 | ① **첫 턴**: `run_turn` 에서 게이트(1126) 뒤·사후 검사 뒤, `_continue_after_gate` 의 기록 갈래 맨 앞(= `resolve_mentions` 앞, 사후 긍정 재개도 같은 자리를 지난다)에 새 함수 `_apply_name_rule(ctx, proposal, verdict) -> (verdict', dropped)` — 기록 의도일 때만 돈다. 걸린 언급(`person` 인자 기준)의 `accepted` 항목을 `rejected`(사유 `REASON_NAME_RULE = "name_rule"`, `app/guard/names.py` 상수 — 게이트가 내는 사유가 아니라 `GATE_REJECTION_REASONS` 에 넣지 않는다)로 옮긴 **새 `GateVerdict`** 를 만든다. 그래서 그 제안은 `_ordered_mentions`·`_pending_calls_from`·`_record` 어디에도 닿지 않고 다른 언급의 되묻기 context 로도 실리지 않는다(재개용 `_drop_calls_for_mention` 은 쓰지 않는다 — 모양이 `PendingCall` 목록이다). ② **재개**: `resume_turn` 이 `resolve_mentions` 를 다시 부르기 전, 남은 `pending_calls` 의 언급을 같은 판정으로 걸러 `_drop_calls_for_mention` 으로 버린다(여기는 `PendingCall` 모양이라 맞다). ③ **방어**: 1847(identity 답 별칭)·1877(new_person 답 표시 이름·별칭) 바로 앞, 그리고 identity 거절 → `_followup_new_person_turn`(1856) **앞**(배포 전 identity 질문이 "새로운 사람인가요?" 를 한 번 더 띄우지 않게 — 결정 15 의 "질문 전에 멈춘다"). ④ `_execute_call` 의 `update_person.new_alias`(`display_name` 은 그 자리에 오지 않는다 — 게이트 `gate.py:49·264` 가 먼저 거부). ⑤ (개정 1 — M4) `_resolve_mentions_impl` 의 `resolve()`(580) 뒤·`apply_resolution`(583)·되묻기(599~607) 앞 — 결정 22 로 통과한 언급의 해석 결과 검사(VR6 행). 걸린 제안은 `loop_gate` trace 에는 `accepted` 로 남으므로 `tests/test_agent_loop.py` 426·483·600행의 등식 `accepted == executed ∪ failed ∪ pending ∪ hint_only` 에 "이름 규칙으로 버린 인덱스"(`guard_name_rule.input.proposal_indices`) 항이 더해진다(U7b 닫힌 목록 — R-1). (U7b) |
| **VR3** U4 시험 파일 (개정 1 — M1) | 닫힌 목록: `tests/auth_helpers.py`(`make_user` 에 `notice_accepted: bool = True` — 기본으로 현재 판 번호·시각을 채움. 기존 호출 시그니처 불변) · 가입 본문 `privacy_notice_accepted: true` 추가 — `test_auth_api.py`(`_signup` 도우미)·`test_auth_nickname.py`(`_signup` 도우미)·`test_auth_availability.py`·`test_auth_origin.py`·`test_auth_required_routes.py`(가입 본문이 있는 곳) · **주기 작업 시험의 계정 준비 줄** — `test_briefing_scheduler_users.py`(인물 소유 계정마다 `make_user` 1줄)·`test_push_wiring.py`(픽스처 `scheduler_env` 에 `make_user(session, "local")` 1줄 — 349·372행 단언 유지) · `evaluation/recognition/probe.py`(가입 본문 3곳 — R-6, 시험이 아니라 측정 도구). `test_briefing_scheduler.py`·`test_commit_boundaries.py` 는 고치지 않는다(위 사실 절). **단언 줄 변경 0**(본문·준비만). **예외 7줄**(개정 2 — 전수 확인, 3회차 권고 P3-R1 로 4줄 추가): ① `tests/test_auth_required_routes.py` 의 `_MUST_REQUIRE_LOGIN`(51행) 집합에 새 라우트 `POST /auth/privacy-notice` 를 그 상수의 기존 항목 모양대로 1개 더하는 것(로그인 필수 라우트 목록을 단언하는 상수라 새 라우트는 여기에 들어가야 한다) ② `tests/test_auth_api.py:96`·③ `tests/test_auth_nickname.py:70` 의 `set(body) == {"id", "username", "nickname"}` 에 `"notice_required"`(`MeOut` 필드 추가) ④ `tests/test_auth_api.py:226`·⑤ `tests/test_auth_nickname.py:83`·⑥ `:85`·⑦ `tests/test_auth_helpers.py:105` 의 `MeOut` 사전 동등 비교(`json() == {"id": …, "username": …, "nickname": …}`)에 `"notice_required": <그 계정의 기대값>` — 동의 계정(`make_user` 기본)은 `False`, 가입 직후는 `False`(가입이 고지 동의를 함께 기록). Grep `json\(\) == \{` 로 `tests/` 전부를 다시 확인했고 `MeOut` 모양은 이 4줄뿐이다(나머지는 오류 본문·중복 조회·카드 등 모양이 바뀌지 않는 응답). 판정: `git diff --stat <U3 해시> -- tests evaluation` 의 파일 목록 ⊆ 이 목록 + 새 시험 파일. (U4) |
| **VR5** 고지 문구 주인 | 위 "가드 문구 상수의 주인" 절 |
| **VR6** 이름 규칙 근거 trace + 사용자 결정 22 (개정 1 — M4) | 걸러진 언급·통과한 기존 별칭마다 trace 1행: `step="guard_name_rule"`, `tool_name="guard"`, `input={"mention_index": i, "proposal_indices": [...]}`(언급 문자열 0), `output={"decision": "dropped" \| "passed_existing_alias" \| "dropped_non_owner" \| "dropped_no_consent", "rule_ids": [...], "person_id": <통과·비소유 판정 때 별칭 주인 인물 id>}`(인물 id 는 기존 키 `person_id` — R-12). **결정 22 의 통과 조건(메인 세션 결정 (b))**: 그 사용자 인물들의 `person_aliases.alias` 중 언급과 **글자까지 같은** 행이 있음(`app/guard/names.py::existing_alias_owner_ids(session, user_id, mention) -> set[int]`, 정규화 없음). 공백·대소문자만 다른 변형은 이름 거부. 통과한 언급은 자동 연결 때 `_add_alias` 가 같은 글자 행을 찾아 **새 행·임베딩 0** 이다 → D20 R-7 "새로 저장되는 이름이 없다" 가 `app/er/` 를 고치지 않고 성립. **코드로 확인한 두 경우**: (가) 통과한 언급이 별칭 주인이 **아닌** 인물로 해석되는 경우는 생긴다 — ER 이 다른 인물로 merge(580행 결과의 `matched_person_id` ∉ 주인 집합), identity 질문에서 사용자가 다른 후보를 고름(1847), new_person 밴드·identity 거절(1856·1877). 그대로 두면 그 인물에 민감 별칭이 새로 붙거나 민감 표시 이름의 인물이 생긴다. 동작은 사용자 결정 필요 **D-4**(아래)이고 이 계획의 기본 설계는 권장안 (a) — merge·new_person 밴드는 `apply_resolution`·되묻기 **전에**(⑤ 자리) 그 언급을 이름 거부(`dropped_non_owner`), identity 밴드는 질문을 띄우되 1847 답이 주인이 아니면 별칭 저장 없이 이름 거부, identity 거절은 1856 앞에서 이름 거부. (나) 통과한 턴에 동의 문맥이 없는 경우도 생긴다 — 언급은 추출 LLM 이 낸 문자열이라 발화의 부분 문자열이라는 보장이 없어(`loop.py:323~342` 는 제안 인자를 그대로 읽는다) "같은 낱말 목록이니 통과 턴은 항상 사전 검사에 걸려 동의가 있다" 는 주장은 **성립하지 않는다**. 동작: `ctx.consent` 가 없으면 통과시키지 않고 이름 거부(`dropped_no_consent`) — 결정 22 의 전제("동의 칩은 평소처럼 뜨고") 밖이라 실패를 닫는 쪽으로 둔다(범주를 지어내지 않는다). 그래서 통과 턴의 표시는 언제나 G5 턴 단위(`ctx.consent` 의 범주, D-1 규칙). 가림 자리표시(`[주민등록번호]` 등)가 든 이름은 거부. (U7b) |
| **VR7** 미동의 건너뜀 자리 | `_due_user_ids`(107~122) 질의에 `users` 를 조인해 `users.privacy_notice_version >= PRIVACY_NOTICE_VERSION` 인 계정만 고른다(`users` 행이 없는 `persons.user_id` 도 제외 — 실패는 닫는 쪽). 건너뛴 계정은 `_run_for_user` 에 들어가지 않으므로 **`briefing_run` trace 0 — 1분마다 쌓이지 않는다**. 건너뜀은 DB 상태로 결정되고 재현 가능하므로 별도 trace·로그를 두지 않는다(원칙9 — 판정이 아니라 대상 선정). 수동 `POST /briefings/run` 은 라우트 의존성 403. (U4) |
| **VR8** `chat_message_id` | 라우트가 싣는다: `chat` 이 `append_chat_message`(이미 루프 앞, 389행) 반환 행의 id 를 들고 있다가, 턴이 `kind="sensitive"` 질문으로 끝나면 `app/guard/consent.py::attach_turn_refs(session, question_id, chat_message_id, trace_range)` 로 그 질문 context 에 `chat_message_id`·`turn_trace_range` 를 같은 트랜잭션에서 덧붙인다(`flag_modified`). 사전 질문은 라우트가 만들 때 바로 넣는다. 루프·`ToolContext` 는 이 값을 모른다. (U5b·U6) |
| 8.6 행 번호 재확인 | 위 "코드에서 확인한 사실" — 2026-11-22 직접 확인(`resolve()` 는 580행, 재검토가 적은 581 은 1행 차이) |
| 8.6 FIX-015 해시 | `6e7b286`(위) |
| 8.6 `loop.py:1322` | 직접 읽음 — 조회 턴 merge 는 `apply_resolution` 0, 별칭 누적 0. 그래서 이름 규칙은 기록 의도에만 건다 |
| 8.6 `turn_trace_range` 겹침 | 한 탭은 `sending` 잠금으로 동시 전송 0. 같은 계정의 여러 탭·기기가 동시에 보내면 구간에 다른 턴의 행이 섞일 수 있다 — 더 넓게 지우는 쪽(원문이 남는 쪽이 아님)의 오류로 받아들인다. 브리핑 trace 는 다른 `session_id` 라 섞이지 않는다 |
| 8.6 R-10 규칙 목록 변경 창 | 재배포로 낱말 목록이 바뀌면 배포 전 24시간 안 대기 질문 중 새 목록에 걸리는 것은 409 가 된다. U12 ③ 에서 미답·미만료 대기 질문 수를 기록하고, 더 다루지 않는다(창이 `QUESTION_TTL` 24시간) |

### 빈자리 9건 — 계획이 정한 값 (개정 1 — 02-plan-verify R-7. 근거가 카드·기존 코드에 있는 것만 여기서 정하고, 사용자에게 보이는 것은 아래 "사용자 결정" 절)
| # | 무엇 | 정한 값 | 근거 |
|---|---|---|---|
| ① | U2 "선형 시간" 판정 | **구조 단언**: `rules.py` 의 모든 정규식 문자열에 중첩 수량자(`(...+)+`·`(...*)*`·`(...+)*` 모양)가 없음을 시험이 검사 + 2000자 최악 입력(같은 숫자·낱말 반복) 1회가 예외 없이 끝남. **시간 상한 수는 두지 않는다** | 시간 상한은 기기마다 흔들린다(원칙8 재현성). 역추적 폭발의 원인은 중첩 수량자다 |
| ② | U5a "자리표시만 든 사실 값" | 정의 = 사실 값에서 자리표시 문자열(6종)을 지우고 공백을 지우면 빈 문자열. 단위 = **그 `update_person` 제안 전체를 게이트가 거부**(사유 `REASON_MASKED_VALUE = "masked_value"`) | 게이트는 제안 단위로만 거부한다(`RejectedProposal(index, …)`, `gate.py` 288~). 제안 안의 인자를 고치는 게이트 경로가 없다 |
| ③ | U7b 재개 방어(1847·1877·1856 앞)에 걸렸을 때 | 그 언급의 별칭·인물 저장 0 + **그 언급에 딸린 보류 제안도 버림**(`_drop_calls_for_mention`) + 답에 이름 거부 문구. 다른 언급의 기록은 그대로 | 사용자 결정 15 "저장하지 않고 안내" — 이름 없이 그 언급의 기록만 남으면 어느 인물인지 정할 수 없다 |
| ④ | 민감 일정 문구를 붙이는 조건 | 동의 문맥이 있는 턴(재개 턴 포함)에서 `add_schedule` 이 1건 이상 저장되면 답 끝에 한 번(여러 건이어도 한 번). U7a 시험이 단언 | D20 확정 부속 문구, G12 "알림이 오지 않는다는 것을 칩 응답에 한 줄" |
| ⑤ | U5c `cleanup_expired` 예외 | `default_run_once` 안에서 사용자 반복과 같은 규약으로 `try/except Exception` → `logger.exception`(원문 0) 뒤 사용자 반복을 계속한다. 시험 1건 | `scheduler.py:174~178` 의 "한 사용자의 실패가 다른 사용자를 막지 않게" 규약 |
| ⑥ | `guard_check` 와 `turn_trace_range` 의 순서 | 라우트는 ① `guard_check`(가림) 행을 쓴 **뒤** ② 그 세션 최대 trace id(구간 시작)를 읽고 ③ `run_turn`. 그래서 `guard_check` 는 구간 밖이고 거절·만료 뒤에도 남는다 | D20 R-2 "`guard_check` trace 는 남는다" |
| ⑦ | U9b 채팅·카드 표시 | 채팅: 차단 안내는 서버 `reply` 문자열 그대로(새 컴포넌트 0), `content` 가 대체 줄과 같은 사용자 줄은 흐린 글씨(`text-muted-foreground`)로. 카드 가림 상태: 배지 "민감" + 범주 이름 + (사건) 날짜·종류 이름 / (사실) 키 이름이 보이고 **값·사건 내용·일정 제목은 가림**, "눌러서 보기" 로 펼침 | D-2 확정 (a) · G20 (a) "배지 + 기본 가림". 날짜·키 이름은 카드 계층 안의 메타데이터 |
| ⑧ | U1 조회형 문장 수·셈 | 범주마다 **조회형 1건 이상**(`form: "query"` 필드), 범주·유형별 15~20 셈에 **든다**. 우회 20 은 `group: "evasion"` 으로 범주 셈에 **들지 않는다**. 검사기는 `group=="sensitive"` 만 범주·유형별로 센다 | CR-009 U1 "조회형 민감 문장도 범주별로 섞는다" — 존재만 요구하므로 최소 1. 사용자 결정 12 의 크기는 그대로 |
| ⑨ | `POST /auth/privacy-notice` 재호출 | 위 계약 표 — 204·행 변경 0 | 동의 기록(처음 동의 시각)을 덮지 않는다(사용자 결정 8 의 "동의 기록은 남는다" 와 같은 방향) |

### 고정 단언 전수 확인 (개정 2 — 02-plan-verify M2-잔여. architect 가 2026-11-22 Grep 으로 `tests/`·`scripts/`·`evaluation/`·`web/src`·`web/e2e`·`alembic/` 전부를 찾았다)
찾은 패턴: 리비전 리터럴(`"0005"`·`'0005'`·`0005_`·`"0006"`·`alembic_revision`·`get_current_head`) · 테이블·컬럼·CHECK·인덱스 수(`== 13`·`== 79`·`len(…columns)`·`tables.keys`·`EXPECTED_TABLES`) · `QUESTION_KINDS`·kind 3종 나열(`identity.*new_person.*schedule`, `_AFFIRMATIVE_REQUIRED_KINDS`, `kind="…"`) · `users` 컬럼 집합(`"password_hash"`) · 응답 키 집합(`set(body) ==`·`keys()) ==`·`set(item…) ==`) · 거부 사유·trace step 어휘(`GATE_REJECTION_REASONS`·`LOOP_TRACE_STEPS`·`STEP_*`) · 제안 스키마(`PROPOSAL_SCHEMA[…]`·`"required"`·`additionalProperties`) · `_MUST_REQUIRE_LOGIN`·`_EXEMPT`.

| 찾은 단언(파일:행) | 바뀌는 까닭 | 처리 |
|---|---|---|
| `tests/test_api.py:93` `alembic_revision == "0005"` | 시험 DB head 가 0006 | **U3 닫힌 목록** — `"0006"` 과 주석 `# P9d U3 -- 0006(CR-009)` |
| `tests/test_migration_0005.py:110·111·196` | head 리터럴 | **U3** — head 이력 모양으로 |
| `tests/test_migration_0005.py:191` `== "0004"` | downgrade 목적지 리터럴 | 고치지 않음 — 0004 로 내린 뒤의 버전이라 그대로 맞다(0006 → 0005 → 0004 를 거치는데 그 DB 에는 민감 행이 없다) |
| `tests/test_migration_0004.py:39·110·111·157·169` | `users` 에 두 컬럼 | **U3** — 39 정의(head)에 두 컬럼, 110·157(0003 상태)은 세 이름을 뺀다 |
| `tests/test_migration_0003.py:49` | head 기준 `users` 집합 | **U3** |
| `tests/test_migration_0003.py:219·369`·`0004.py:102·167` `get_current_head()` | 리터럴이 아님 | 고치지 않음 |
| `tests/test_schema_models.py:54·81`(컬럼 집합)·88~96·144(테이블 13)·158~165·176·205~212·215~223·226~234(FK 9)·254~263·289(JSONB 5)·295~300·303~336(인덱스 13) | 컬럼 +6, CHECK +3 | **U3** — 54·81·88·158~165·176·205~212·215~223·`TIMESTAMP_COLUMNS` 를 고친다. 144·226~234·289·336 은 고치지 않음(테이블·FK·JSONB·인덱스 수가 그대로) |
| `tests/test_schema_check.py:24·58·63`·`:44` | — / `QUESTION_KINDS` 4 | **U3** 44행만. 24(테이블 13)·58(인덱스 13)·63(UNIQUE 8)은 그대로 |
| `tests/test_tools_questions.py:131~140` "kind 3종 성공" 매개변수 | 3종 성공을 보는 시험이라 4종째가 없어도 참 | 고치지 않음(`sensitive` 성공·긍정 규약은 새 `tests/test_guard_pre.py`·`test_guard_posthoc.py` 가 본다). 158행 `"unknown_kind"`·`test_agent_types.py:273` `"not_a_kind"` 도 그대로 |
| `tests/test_validate_scenarios.py:559~562` | `"schedule" in QUESTION_KINDS`·`"none" not in` — 포함 단언 | 고치지 않음 |
| `evaluation/metrics.py:131·139·143`·`evaluation/resolvers/base.py:60`·`tests/test_eval_metrics.py:117·118`·`tests/test_baseline_*.py` | ER 평가의 판정·되묻기 **라벨** 어휘(DB `kind` 값 집합이 아니다) | 고치지 않음 |
| `tests/test_auth_api.py:96`·`tests/test_auth_nickname.py:70` `set(body) == {"id","username","nickname"}` | `MeOut` 에 `notice_required` | **U4 단언 예외 2줄**(VR3 행 ②③) — 키 집합에 `notice_required` |
| `tests/test_auth_api.py:226`·`tests/test_auth_nickname.py:83·85`·`tests/test_auth_helpers.py:105` `json() == {"id": …, "username": …, "nickname": …}` | `MeOut` 사전 동등 비교 | **U4 단언 예외 4줄**(VR3 행 ④~⑦ — 3회차 P3-R1 이 든 3줄 + 다시 Grep 해 찾은 `test_auth_api.py:226`) |
| `tests/test_auth_required_routes.py:51·111·136·151·202`(`_MUST_REQUIRE_LOGIN <= …`)·`:113`(면제 등식) | 새 라우트는 보호 목록에만 | **U4 단언 예외 1줄**(51행 집합에 1개). 113행 면제 등식은 그대로 |
| `tests/test_agent_query_gate.py:100~102` `GATE_REJECTION_REASONS[-1] == REASON_QUERY_TURN_NO_WRITE`·`len == 7` | U5a 의 `REASON_MASKED_VALUE` 는 `gate.check` 가 내는 사유라 그 튜플에 든다 | **U5a 닫힌 목록** — 새 사유를 `REASON_QUERY_TURN_NO_WRITE` **앞**에 넣어 100행은 그대로, 101·102행 7 → 8. `REASON_NAME_RULE` 은 `gate.check` 가 내지 않는(루프가 만드는 새 판정의) 사유라 `GATE_REJECTION_REASONS` 에 **넣지 않는다**(`test_agent_gate.py:409` 의 "게이트 출력 ⊆ 그 튜플" 과 맞음) — `app/guard/names.py` 상수 |
| `tests/test_agent_fix037.py:174` 거부 사유 전부 매개변수 | `masked_value` 가 매개변수에 든다 | 고치지 않음 — 강제 거부만 넣는 시험이라 답이 기존 "새로 기억한 것 없음" 문장 그대로(가림이 없으면 차단 안내도 붙지 않는다) |
| `tests/test_agent_types.py:56~65` `LOOP_TRACE_STEPS` 6개 | 가드 trace 는 `tool_name="guard"`·step `guard_check`·`guard_name_rule` 로 `app/guard/` 상수 | 고치지 않음(루프 step 어휘에 넣지 않는다) |
| `tests/test_agent_query_types.py:38` `set(PROPOSAL_SCHEMA["properties"]) == {"tool_calls","intent"}` | U6 의 턴 수준 `sensitive_categories` 는 `PROPOSAL_SCHEMA` 최상위 선택 속성 | **U6 닫힌 목록** — 집합에 하나. 47행 `required == ["tool_calls"]`·`test_agent_propose.py:90·91` 은 선택 속성이라 그대로 |
| `tests/test_api_read_persons.py:189` 다가오는 일정 키 집합 | 카드 라우트 항목에 `sensitive_category` | **U8 닫힌 목록** |
| `tests/test_mcp_tools.py:6·293` 카드 = `read.get_person_card(...).model_dump()` | MCP 는 `sensitive_category` 키를 뺀다 | **U8 닫힌 목록** — 비교 대상을 "그 키를 뺀 덤프" 로. 137행(인물 목록)은 `PersonListItemOut` 이 바뀌지 않아 그대로 |
| `tests/test_tools_briefing.py:257~263` `get_briefing` 키 집합 | 반환 모양 그대로(거른 항목만) | 고치지 않음 |
| `tests/test_chat_history.py:155`·`test_api_read_raw.py:89·143`·`test_api_read_briefings.py:142·143`·`test_mcp_tokens_api.py:95·173` | 모양 그대로 | 고치지 않음 |
| `web/src`·`web/e2e` | `kind` 는 `string`(`types.ts:68`), 리비전·kind 집합 리터럴 0. 가입 본문 단언 `auth.test.tsx:272` | **U9a** — 272행 단언 + 가입 제출 시험의 체크 클릭 준비 줄(N-R6). E2E 는 가입 흐름 0(고치지 않음) |
| `scripts/schema_check.py`·`scripts/tools_check.py` | 값 집합을 모델에서 읽음·시그니처만 봄 | 고치지 않음 |

## 작업 단위 (단위 하나 = 커밋 하나. 끝나면 /commit. 단위마다 verifier 커밋 전 리뷰 + 핵심 계약 변이 시험 최소 1개)

순서·병렬:
```
U0(완료 6d97217) ─┬─ U1 ─(test 동결 해시)─ U2 ─┐
                  └─ U3 ─ U4 ──────────────────┴─ U5a ─ U5b ─ U5c ─ U6 ─ U7a ─ U7b ─ U8 ─┐
                           └─ U9a(U4 커밋 뒤, U5a~U8 과 동시 — web/ 만)                     │
                                     U5b·U5c·U6·U8 ─ U9b ────────────────────────────────┤
                                     U2·U6 ─ U10 ─────────────────────────────────────────┤
                                                                         전부 ─ U11 ─ U12 ─ 사용자 화면 확인·완성 확인
```
U2 와 U3 은 파일이 겹치지 않아 동시 가능(둘 다 backend-agent 라 실제로는 차례로). U10 은 U6 뒤 eval-agent 가 U7a·U7b·U8 과 동시 가능. U7b 는 U7a 의 `ctx.consent` 복원·표시 전파에 기댄다(결정 22 의 통과 턴 표시). U8 은 U7a 의 표시 컬럼 값에 기대고, U7b 와 파일이 겹치므로(`loop.py`) U7b 뒤.
**중간 상태(개정 1 — R-5)**: U5c 가 R-10(동의 문맥 없는 재개 재검사)을 넣고 U7a 가 후속 질문의 `consent` 키를 넣으므로, U5c~U6 커밋 사이에서는 동의한 턴의 후속 질문(identity·new_person·schedule)에 답하면 R-10 에 걸려 409 가 된다. 운영 반영은 U12 한 번이라 바깥 영향이 없다 — U5c·U6 리뷰는 이 상태를 결함으로 읽지 않는다(U7a 수용 기준 ② 가 닫는다).

- [x] U0 **[메인 세션 + architect] CR-009 문서 이행 — D20 신설, D2·D14·D16·D17·D18·D19, S3.1·S3.2·S3.4·S3.5·S3.6·S3.7 보충, CLAUDE.md, backlog P9d 행, review-index, security §5, INDEX, proposal 상단** / Refs: P9d-sensitive-guard CR-009 D20 D2 D14 D16 D17 D18 D19 S3.1 S3.2 S3.4 S3.5 S3.6 S3.7 원칙6 원칙7 원칙9 / 완료 `6d97217`(사용자 결정 22 보충은 이 계획과 같은 문서 커밋)

- [ ] U1 **[eval-agent] 민감 가드 시험 세트·라벨 규칙·형식 검사기 — test 는 U2 착수 전 동결** / Refs: P9d-sensitive-guard D20 S3.7 CR-009 원칙8 / 의존: U0
  - 파일: `evaluation/sensitive_guard/dev.jsonl`·`test.jsonl`·`README.md` · `scripts/validate_sensitive_set.py`(저장소 루트를 `sys.path` 에 넣는 `scripts/tools_check.py:43` 방식).
  - 방식: 한 줄 `{id, text, label: "none"|"block:<type>"|"consent:<category>", group: "sensitive"|"plain"|"trap"|"evasion", trap?, note}`. 차단 유형 6(`rrn`·`passport`·`driver_license`·`account`·`card`·`password`), 범주 5(`crime`·`health`·`sex`·`politics_religion`·`finance`). 크기(사용자 결정 12, **dev·test 각각**): 11개 범주·유형마다 15~20 + 평범 100 + 함정 30(호칭형 이름 "교회 오빠"·"정신과 선생님" 포함, "감기 걸렸대"·전화번호·주소는 `none`) + 우회 20. 조회형 민감 문장을 범주마다 1건 이상(`form: "query"`, 범주 셈에 든다 — 빈자리 ⑧). 우회 20 은 범주 셈 밖. README 에 범주 정의(프로젝트 정의, "법령상 분류가 아니다"), dev 를 본 작성자가 test 도 쓴다는 누출 경로, test 동결 커밋 해시·sha256. **식별번호 모양 문자열은 전부 지어낸 값**(개정 1 — R-12): 주민등록번호 모양은 끝 검증 숫자가 맞지 않게, 카드번호 모양은 공개된 결제 시험용 번호만(Luhn 은 맞으므로 규칙이 잡을 수 있다), 계좌번호는 은행 형식이 아닌 숫자열, 비밀번호 예문은 뜻 없는 낱말. 검사기가 주민등록번호 검증 숫자 불일치와 카드번호의 공개 시험 번호 목록 소속을 확인한다. Write 단계 `secret-guard`·`save_evidence` 비밀 패턴에 걸리면 우회하지 않고 문장을 바꾼다(`security.md` 6절).
  - 역할: 라벨을 만들고 고치는 것은 eval-agent 뿐. verifier 는 `review-u1.md` 에 검수 판정만 쓰고 소견은 `findings.py` 로(라벨을 고치지 않는다).
  - 수용 기준: 검사기 출력에 범주·유형별 개수(`group=="sensitive"`) 15~20 · 범주마다 조회형 ≥ 1 · 평범 100·함정 30·우회 20 · dev/test 문장 중복 0 · 형식 오류 0 · 주민등록번호 모양 검증 숫자 불일치·카드번호 모양 공개 시험 번호 · `review-u1.md` `결과: 통과`.
  - 검증: `… u1-validate -- .venv/bin/python -I scripts/validate_sensitive_set.py evaluation/sensitive_guard/` · `… u1-freeze -- shasum -a 256 evaluation/sensitive_guard/test.jsonl`.
  - 변이 후보: dev 와 test 에 같은 문장 1줄 넣기 → 검사기 FAIL(중복 0 단언).

- [ ] U2 **[backend-agent] 규칙 검사 모듈 — `detect`·`mask`·`name_allowed`, LLM 0·네트워크 0, 러너 규칙 모드(dev 만)** / Refs: P9d-sensitive-guard D20 S3.7 원칙8 원칙9 / 의존: U1 test 동결 커밋
  - 파일: `app/guard/__init__.py`·`rules.py`(정규식·낱말·허용 목록, `SENSITIVE_CATEGORIES`(위 순서 고정)·`BLOCK_TYPES`·규칙 id `^[a-z_]+\.\d{3}$`)·`detect.py`(`detect(text) -> GuardResult{block_spans, consent_categories, rule_ids}`)·`mask.py`(유형별 자리표시 `[주민등록번호]`·`[여권번호]`·`[운전면허번호]`·`[계좌번호]`·`[카드번호]`·`[비밀번호]`)·`names.py`(`name_allowed(text)` = `detect` 에 차단·동의 0 이고 자리표시 0 — **사전 검사와 같은 목록 하나**. `existing_alias_owner_ids` 는 U7b 에서 더한다) · `evaluation/sensitive_guard/run.py`(`--split dev --rules-only` 만 — U10 이 넓힌다) · `tests/test_guard_rules.py`.
  - 방식: NFC·공백 정리 뒤 정규식 + 범주 낱말 + 허용 목록(함정 해소). **목록은 backend-agent 가 dev 세트만 보고 귀납**(test 파일을 여는 코드·명령 0). **사용자 검토는 관문이 아니다**(메인 세션 결정, 02-plan-verify Q2): U2 가 끝나면 메인 세션이 목록을 사용자에게 보고하고, 수정 요청이 오면 U12 전 아무 때나 반영한다(dev 로만 다듬고 test 는 열지 않는다 — 반영 뒤 U10 을 다시 돌린다).
  - 수용 기준: `detect`·`mask` 가 원문을 로그·예외에 싣지 않음 · 2000자(`CHAT_UTTERANCE_MAX_LENGTH`, `app/api/schemas.py:69`) 처리는 빈자리 ① 의 구조 단언(중첩 수량자 0 + 최악 입력 1회 완료) · 규칙 id 정규식 일치 · dev 감지율·오탐률 출력 · **U2 시점 러너는 `--split test` 를 거부(종료 코드 ≠ 0, test 파일을 열지 않음)**(R-9).
  - 검증: `… u2-rules -- .venv/bin/python -m pytest tests/test_guard_rules.py -q`(러너 `--split test` 거부 시험 포함) · `… u2-dev -- .venv/bin/python -I evaluation/sensitive_guard/run.py --split dev --rules-only` · `… u2-no-log -- bash <SCR>/u2-no-log.sh`(안: `grep -rnE "logger\.|print\(" app/guard`, 기대 0줄 = exit 1).
  - 변이 후보: 범주 낱말 하나 지우기 → 그 낱말 시험 FAILED · 허용 목록에서 "마약김밥" 지우기 → 함정 시험 FAILED · 러너의 `--split test` 거부 빼기 → 거부 시험 FAILED.

- [x] U3 **[backend-agent] 리비전 0006 + 모델 — 민감 표시 컬럼·고지 컬럼·`pending_questions.kind` CHECK 4종·downgrade 가드** / Refs: P9d-sensitive-guard D20 S3.1 / 의존: U0
  - 파일: `alembic/versions/0006_sensitive_guard.py` · `app/db/models.py`(`QUESTION_KINDS` 82행, CHECK 228~236행, 새 컬럼) · `tests/test_migration_0006.py`(`tests.test_migration_0003` 도우미·`relationship_test_mig` 재사용 — 0004·0005 관례).
  - 방식: S3.1 보충 그대로. downgrade 는 먼저 민감 질문 행·표시 행·`consent_question_id` 행 수를 세어 하나라도 있으면 개수만 담은 예외(원문 0, 삭제 0). `app/agent/types.py:434` 는 `QUESTION_KINDS` 를 그대로 읽으므로 수정 불필요(시험으로 확인). `relationship_test_mig` 는 0003~0006 시험이 나눠 쓰므로, 민감 행을 넣는 0006 시험은 끝에 그 행을 지워 다음 시험의 downgrade 를 막지 않는다.
  - **닫힌 목록(개정 1 — M2, 0005 선례 `c85a0e8` 과 같은 방식. 바꿀 값은 S3.1 보충 0006 의 컬럼 목록 — `events`(+`sensitive_category`, +`consent_question_id`)·`person_facts`(+`sensitive_category`)·`schedules`(+`sensitive_category`)·`users`(+`privacy_notice_version`, +`privacy_notice_accepted_at`) = 새 컬럼 6개, 새 CHECK 3개(세 표의 `sensitive_category`), 인덱스·UNIQUE·FK·테이블 0 — 에서 architect 가 다시 셌다)**:
    - `tests/test_schema_models.py`: `S3_1_TABLE_COLUMNS` 에 위 6개 컬럼 · 총 컬럼 **79 → 85**(함수 이름·docstring 의 79 포함) · `NULLABLE_COLUMNS` 는 **컬럼 이름 집합**이라 새 이름 4개(`sensitive_category`·`consent_question_id`·`privacy_notice_version`·`privacy_notice_accepted_at` — `sensitive_category` 는 세 표에 있어도 한 번) → **7 → 11**(함수 이름 "seven"·docstring 포함. 검증자 메모의 13 은 컬럼 수로 센 값이다) · `events` CHECK 시험(176행 `len(checks) == 1`)은 `type` 컬럼 CHECK 만 고르도록 거른다(`persons` 시험 186·197행과 같은 방식) · `QUESTION_KINDS` **3 → 4**(205~210행, 함수 이름 "three" 포함) · CHECK 총 **5 → 8**(215~223행 — 그 함수가 세는 테이블 목록에 `person_facts`·`schedules` 가 이미 있다) · `TIMESTAMP_COLUMNS` 에 `("users", "privacy_notice_accepted_at")` 를 더한다(시간대 단언을 새 타임스탬프에도).
    - `tests/test_schema_check.py:44` `len(sc.m.QUESTION_KINDS)` **3 → 4**. 24·58행(테이블 13·인덱스 13)·63행(UNIQUE 8)은 그대로.
    - `tests/test_migration_0003.py:49` head 기준 `users` 집합에 두 컬럼.
    - `tests/test_migration_0004.py`: `USERS_COLUMNS`(39행, head 기준 — 111·169행이 쓴다)에 두 컬럼, **110행(`mig["columns_before"]`)과 157행**(둘 다 0003 상태)은 `USERS_COLUMNS - {"nickname", "privacy_notice_version", "privacy_notice_accepted_at"}`.
    - `tests/test_api.py:93` `body["alembic_revision"] == "0005"` → `"0006"`(주석도 — 0005 선례 `c85a0e8`).
    - `tests/test_migration_0005.py`: 110·111·196행의 리터럴 `"0005"` 를 0004 시험(97~105·168행)과 같은 "head 이력에 0005 가 있고 DB 버전 == head" 모양으로. 리터럴 `"0006"` 은 새 `test_migration_0006.py` 가 본다.
    - `scripts/schema_check.py` 는 값 집합을 모델에서 읽어(185행) 고치지 않는다.
  - 수용 기준: 빈 상태 `upgrade → downgrade -1 → upgrade` · `kind='sensitive'` 행이 있을 때 downgrade 실패하고 행·컬럼·CHECK 그대로 · 표시 행만 있을 때도 같음 · 0005 에서 `kind='sensitive'` INSERT 는 CHECK 위반, 0006 뒤 성공 · 기존 행 변경 0 · `alembic check` 무변경 · **목록 밖 시험 diff 0**.
  - 검증: `POSTGRES_PORT=5433 … u3-migration -- .venv/bin/python -m pytest tests/test_migration_0006.py tests/test_migration_0005.py tests/test_migration_0004.py tests/test_migration_0003.py -q` · `… u3-schema-tests -- .venv/bin/python -m pytest tests/test_schema_models.py tests/test_schema_check.py -q` · `… u3-upgrade -- .venv/bin/python -m alembic upgrade head` · `… u3-check -- .venv/bin/python -m alembic check` · `… u3-schema-check -- .venv/bin/python scripts/schema_check.py` · 개발 DB 전후 행 수(`u3-dev-before-counts`/`u3-dev-after-counts`, P9b U12 와 같은 스크립트 모양) · `… u3-api -- .venv/bin/python -m pytest tests/test_api.py -q` · `… u3-test-diff -- git diff --stat <U3 직전 해시> -- tests scripts`(파일 목록 ⊆ {`tests/test_schema_models.py`·`tests/test_schema_check.py`·`tests/test_migration_0003.py`·`tests/test_migration_0004.py`·`tests/test_migration_0005.py`·`tests/test_api.py`·`tests/test_migration_0006.py`(새)}) · 전체 pytest(실패 0 — 목록 밖에서 깨지는 시험이 있으면 멈추고 03-log 에 보고, 목록을 넓히는 것은 verifier 리뷰에서).
  - 변이 후보: downgrade 의 개수 검사 빼기 → "민감 행 있을 때 실패" 시험 FAILED.

- [ ] U4 **[backend-agent] 가입 고지·재고지 API·미동의 403·주기 브리핑 건너뜀** / Refs: P9d-sensitive-guard D20 D18 S3.1 S3.6 원칙9 / 의존: U3
  - 파일: `app/auth/routes.py`(가입 본문·`MeOut.notice_required`·`POST /auth/privacy-notice`) · `app/auth/deps.py`(`require_notice`) · `app/api/routes.py`(`chat`·`submit_answer`·`run_briefings_endpoint` 에 `require_notice`) · `app/briefing/scheduler.py`(`_due_user_ids` 에 `users` 조인 — VR7) · `app/settings.py`(`PRIVACY_NOTICE_VERSION = 1`) · `tests/test_privacy_notice.py` · VR3 닫힌 목록(도우미 `tests/auth_helpers.py` + 시험 8개 — 3회차 P3-R1 로 `tests/test_auth_helpers.py` 추가 — + `evaluation/recognition/probe.py`).
  - **가입 검사 순서(3회차 P3-R3)**: 기존 `signup`(`app/auth/routes.py:126~149`, 모듈 머리 7행 표)의 관례 "422 형식 위반을 `invalid_username` → `invalid_password` → `invalid_nickname` 순으로 첫 위반만, 그 뒤 409 `username_taken` → `nickname_taken`" 을 따라 **`notice_required` 는 세 형식 검사 뒤·409 사전 조회 앞**에 둔다(422 끼리는 형식 → 동의 순, 422 가 409 보다 먼저). 모듈 머리 표에 그 순서를 한 줄 더한다. 시험 1건: 아이디 형식이 틀리고 동의도 없으면 `invalid_username`, 형식은 맞고 동의 없음 + 이미 있는 아이디면 `notice_required`(409 아님).
  - 수용 기준: `_EXEMPT`(`tests/test_auth_required_routes.py:39`) 무변경, 새 라우트는 `_MUST_REQUIRE_LOGIN`(`:51`)에 1개(VR3 의 단언 예외 ①) · 가입 본문의 `privacy_notice_accepted` 는 선택 필드로 받아 라우트가 판정하고, 없음·`false` 모두 422 `{"detail":{"code":"notice_required"}}`(목록 모양 `detail` 0 — N-R7) · 이미 현재 판에 동의한 계정의 `POST /auth/privacy-notice` 재호출 204·행 변경 0 · 기존 계정(NULL) `notice_required: true` → 동의 뒤 `false` → 판 번호를 올리면 다시 `true` · 미동의 `/chat`·`/answers/{id}`·`/briefings/run` 403, 가짜 주입체 호출 0 · 미동의 계정에 창 안 일정이 있어도 `default_run_once` 1회 뒤 작성기 호출 0·발송 0·`briefed_at` NULL·그 계정 `briefing_run` trace 0 · 동의 뒤 떠 있던 미만료 칩 답 200 · 가입 422 시 `users` 행 0 · VR3 판정.
  - 검증: `POSTGRES_PORT=5433 … u4-notice -- .venv/bin/python -m pytest tests/test_privacy_notice.py tests/test_auth_required_routes.py -q` · `… u4-auth -- .venv/bin/python -m pytest tests/test_auth_api.py tests/test_auth_nickname.py tests/test_auth_availability.py tests/test_auth_origin.py tests/test_auth_helpers.py -q` · `… u4-scheduler -- .venv/bin/python -m pytest tests/test_briefing_scheduler.py tests/test_briefing_scheduler_users.py tests/test_push_wiring.py tests/test_commit_boundaries.py -q` · `… u4-test-diff -- git diff --stat <U3 해시> -- tests evaluation`(⊆ VR3 닫힌 목록 + `tests/test_privacy_notice.py`) · 전체 pytest(실패 0 — 닫힌 목록 밖에서 깨지는 시험이 있으면 멈추고 03-log 에 보고, 목록을 넓히는 것은 verifier 리뷰에서).
  - 변이 후보: `run_briefings_endpoint` 에서 `require_notice` 빼기 → 403 시험 FAILED · `_due_user_ids` 의 조인 빼기 → 건너뜀 시험 FAILED.

- [ ] U5a **[backend-agent] 가림 적용 — 대화 기록·trace·LLM·응답 전부 가린 문장, 자리표시만 든 사실 버리기, 가드 문구 파일 신설** / Refs: P9d-sensitive-guard D20 S3.4 원칙9 / 의존: U2·U4
  - 파일: `app/api/routes.py::chat`(`append_chat_message` **앞**에서 `detect`→`mask`, `_record_loop_error` 에도 가린 문장) · `app/agent/gate.py`(빈자리 ② — `REASON_MASKED_VALUE`, 그 `update_person` 제안 전체 거부. `GATE_REJECTION_REASONS` 에서 `REASON_QUERY_TURN_NO_WRITE` **앞**에 넣는다) · `app/guard/messages.py`(③) · `tests/test_guard_mask.py` · `tests/test_guard_messages.py` · 닫힌 목록 `tests/test_agent_query_gate.py`(101·102행 `len == 7` → `8`, 100행 그대로 — 전수 확인 절).
  - 방식: `guard_check` trace 1행(`tool_name="guard"`, `input={}`, `output={"decision":"masked","types":[...],"rule_ids":[...]}` — 원문·가린 문장 0). 라우트 순서는 빈자리 ⑥(`guard_check` → 구간 시작 id 읽기 → `run_turn`). 범위 밖(기존 동작): `POST /answers/{id}` 에 옵션 밖 문자열을 보내면 `answer_question` 의 `tool_error` trace 입력에 그 문자열이 남는다 — 화면은 칩 문자열만 보내므로 전수 `LIKE` 대상이 아니다(R-13).
  - 수용 기준: 차단 유형 6종 원문이 `chat_messages`·`agent_traces`·`pending_questions`·`events`·`person_facts`·`schedules`·`person_aliases` 텍스트 컬럼과 응답 본문에 0(전수 `LIKE`) · 루프 예외 턴의 `loop_error` 행에도 0 · `caplog` 에 0 · `"[계좌번호]"` 같은 값의 사실 저장 0 · 문구 ③ 글자 일치·금지 표현 0.
  - 검증: `POSTGRES_PORT=5433 … u5a-mask -- .venv/bin/python -m pytest tests/test_guard_mask.py tests/test_guard_messages.py tests/test_agent_gate.py tests/test_agent_query_gate.py tests/test_agent_fix037.py -q` · `… u5a-tools-check -- .venv/bin/python scripts/tools_check.py` · `… u5a-test-diff -- git diff --stat <U5a 직전 해시> -- tests`(⊆ `test_guard_mask.py`·`test_guard_messages.py`(새)·`test_agent_query_gate.py`).
  - 변이 후보: `mask` 를 `append_chat_message` 뒤로 옮기기 → 전수 `LIKE` FAILED.

- [ ] U5b **[backend-agent] 사전 동의 질문 — 라우트가 `ask_user` 툴 없이 저장소에 직접, LLM 호출 0** / Refs: P9d-sensitive-guard D20 D2 S3.4 원칙9 / 의존: U5a
  - 파일: `app/tools/questions.py`(검증·INSERT 를 내부 헬퍼 `_store_question(session, *, session_id, user_id, kind, question, options, context)` 로 분리 — `ask_user` 는 그 헬퍼를 부르고 동작·`@traced` 그대로 · `_AFFIRMATIVE_REQUIRED_KINDS` 에 `sensitive`) · `app/guard/consent.py`(`create_pre_consent_question` — 헬퍼 사용) · `app/api/routes.py::chat` · `app/guard/messages.py`(①) · `tests/test_guard_pre.py`.
  - 방식: CR-009 U5b ①~④. context = `{"phase":"pre","utterance":<가린 문장>,"categories":[...],"rule_ids":[...],"chat_message_id":<id>, AFFIRMATIVE_KEY:["진행해요"]}`. 조회형 문장도 같은 경로.
  - 수용 기준: 동의 범주 문장에서 `proposer`·`judge`·`embedder`·`extractor` 호출 0 · 원문은 `pending_questions.context` 와 `chat_messages` 한 줄에만, `agent_traces` 0 · `ask_user` 기존 시험 무수정 통과 · `GET /questions/pending` 문구에 원문 조각 0 · 문구 ① 글자 일치.
  - 검증: `POSTGRES_PORT=5433 … u5b-pre -- .venv/bin/python -m pytest tests/test_guard_pre.py tests/test_tools_questions.py tests/test_guard_messages.py -q`.
  - 변이 후보: 라우트가 헬퍼 대신 `ask_user` 툴을 부르게 바꾸기 → "trace 원문 0" FAILED.

- [ ] U5c **[backend-agent] 사전 동의 재개·거절·만료 정리·배포 전 대기 질문 — 지우기 함수 하나** / Refs: P9d-sensitive-guard D20 D2 D18 S3.4 S3.6 원칙9 / 의존: U5b
  - 파일: `app/api/routes.py::submit_answer`(`proposer: Proposer | None = Depends(get_proposer)` 추가 — `answerer` 는 `chat` 처럼 넘기지 않는다) · `app/api/deps.py`(`legacy_resume_blocked` — R-10 사전 검사) · `app/agent/loop.py`(`run_turn(…, consent: Consent | None = None)` → `ctx.consent` 설정, `resume_turn` 의 `sensitive` 분기 진입점) · `app/tools/context.py`(`ToolContext.consent: Consent | None = None`) · `app/guard/consent.py`(`Consent(categories, question_id)` · `redact_declined(session, question)` — R-2·R-3 의 유일한 지우기 자리, 남기는 키 상수 `KEEP_KEYS` · `cleanup_expired(session, now)`) · `app/briefing/scheduler.py`(`default_run_once` 맨 앞, 사용자 반복 **밖**에서 `cleanup_expired` 1회) · `app/guard/messages.py`(거절 뒤 답·대체 줄) · `docs/RUNNING.md`(스위치가 꺼지면 만료 원문이 정리되지 않는다 한 줄) · `tests/test_guard_resume.py`.
  - 방식: 긍정 → `run_turn(ctx, context["utterance"], consent=…)` 처음부터. 부정 → `resume_turn` 을 부르기 전에 끝내고 `redact_declined`. 만료 → 주기 정리(멱등 표지 `redacted: true`, 예외 처리는 빈자리 ⑤). R-10: `kind` 가 `identity`·`new_person`·`schedule` 이고 동의 문맥(`consent` 키) 없는 재개는 `context["utterance"]` 를 `detect` 해 걸리면(`sensitive` 질문은 답 자체가 동의 여부라 대상이 아니다) 409 `expired` 와 같은 응답(LLM 0) — **검사는 `answer_question`(답 저장) 앞**(개정 1 — R-5): 상태 검사·저장·행 잠금은 `answer_question` 한 함수 안(`app/tools/questions.py` 237~284, `with_for_update` — FIX-019)이므로 그 함수는 **고치지 않고**, `PendingQuestion` ORM 을 읽는 기존 자리인 `app/api/deps.py` 에 `legacy_resume_blocked(session, question_id, user_id, now) -> bool` 을 더해 `submit_answer` 가 `answer_question` **앞**에서 부른다(개정 2 — N-R2). 이 함수는 잠금 없이 행을 읽어 "그 사용자 소유 · 미답 · 미만료 · `kind` 3종 · `consent` 키 없음 · `detect(context["utterance"])` 에 걸림" 이 **모두** 참일 때만 참이고, 참이면 라우트가 쓰기 0 으로 409 `expired` 와 같은 응답(질문은 소비되지 않고 24시간 TTL 뒤 만료 — 같은 질문을 다시 눌러도 같은 409). 하나라도 거짓이면 기존 경로 그대로라 남의 질문은 404, 이미 답한 질문은 `already_answered`, 만료는 `expired`(모두 `answer_question` 이 낸다). 잠금 없는 읽기라 동시 요청이 와도 막힐 때는 둘 다 쓰기 0 이라 해가 없다. 위 "중간 상태" 문단대로 U7a 전까지는 동의 턴의 후속 질문도 여기에 걸린다.
  - 수용 기준: 거절 뒤 원문이 DB 전 텍스트 컬럼에 0, 대체 줄, 질문 행·답·시각·범주·규칙 id 남음, context 키 ⊆ `KEEP_KEYS` · 만료 뒤(창 안 일정이 없는 사용자 포함, `default_run_once` 1회) 같은 단언 · 긍정 재개에서 추출 LLM 정확히 1회 · 남의 질문 404·1회 소비 409 · 배포 전 모양(동의 문맥 없음·민감 원문) 재개 409, judge 0, `answered_at` NULL 그대로(시험 이름에 `legacy`) · **이미 답한 배포 전 모양 질문은 `already_answered`(R-10 응답이 아님 — `legacy` 시험 1건)** · 남의 배포 전 모양 질문은 404 · 정리 2회째 변경 0 · `cleanup_expired` 가 예외를 내도 같은 `default_run_once` 의 사용자 반복은 돈다.
  - 검증: `POSTGRES_PORT=5433 … u5c-resume -- .venv/bin/python -m pytest tests/test_guard_resume.py tests/test_auth_required_routes.py tests/test_agent_loop.py tests/test_briefing_scheduler.py -q` · tools_check · 전체 pytest.
  - 변이 후보: `redact_declined` 의 `KEEP_KEYS` 를 "utterance 만 지움" 으로 바꾸기 → 키 집합 단언 FAILED · 거절 처리를 `resume_turn` **안**으로 옮기기(그러면 `_log_resume_entry` 가 context 전체를 `loop_resume` 행에 싣는다) → 거절 뒤 trace 전수 `LIKE` FAILED(N-R5) · `legacy_resume_blocked` 의 "미답" 조건 빼기 → "이미 답한 질문은 `already_answered`" 시험 FAILED.

- [ ] U6 **[backend-agent] 사후 확인 — 추출 LLM 의 민감 표시, 기록·조회 모두 해석 전에 멈춤** / Refs: P9d-sensitive-guard D20 D16 S3.4 원칙8 원칙9 / 의존: U5c
  - 파일: `app/agent/propose.py`(턴 수준 `sensitive_categories: enum[]` 을 **`PROPOSAL_SCHEMA` 최상위 선택 속성**으로 — `required` 는 `["tool_calls"]` 그대로, 범주 뜻 한 곳. 제안 인자 스키마 `PROPOSAL_ARG_SCHEMA` 에는 넣지 않는다) · `app/agent/types.py`(`Proposal.sensitive_categories`) · 닫힌 목록 `tests/test_agent_query_types.py`(38행 집합에 `"sensitive_categories"` — 전수 확인 절) · `app/agent/loop.py`(`run_turn` 1126 뒤·1128 앞, 동의 문맥 없을 때만 / 1128~1187행을 `_continue_after_gate` 로 뽑기 / `resume_turn` 의 `phase=="post"` 분기 — 기록·조회 모두 VR1 행: `proposal_calls` 로 `Proposal` 재구성 → `_gate` → `_continue_after_gate`) · `app/api/routes.py::chat`(`run_turn` 직전·직후 그 세션 최대 trace id → `attach_turn_refs` — VR8) · `app/guard/messages.py`(②·⑥) · `tests/test_guard_posthoc.py`.
  - 방식: CR-009 U6. 사후 질문 context = `{"phase":"post","intent":…,"utterance":…,"proposal_calls":[…],"categories":[<제안의 sensitive_categories>],"rule_ids":[], AFFIRMATIVE_KEY:[칩]}` + 라우트가 덧붙이는 `chat_message_id`·`turn_trace_range`(VR8). `KEEP_KEYS` 는 `phase`·`intent`·`categories`·`rule_ids`(사후는 빈 목록)·`chat_message_id`·`turn_trace_range`·`AFFIRMATIVE_KEY`·`redacted` — `utterance`·`proposal_calls` 는 거절·만료 때 지워진다. 그 턴 trace 는 `turn_trace_range` 구간으로 모아 `redact_declined` 가 지운다.
  - 수용 기준: 가짜 제안기 민감 표시 — 기록: 저장 0·질문 1·judge·embedder 0 / 조회: 질문 1·judge·embedder·answerer 0 · 거절·만료 뒤 발화·제안 인자 값 DB 전수 0(그 턴 `ask_user`·`loop_turn` 행 포함, 행 수·step·tool_name·토큰 그대로), 키 ⊆ `KEEP_KEYS` · 조회 긍정 재개는 `_run_query_turn` 경로로 답하고 인식 LLM 0 · **기록 긍정 재개의 저장 행(인물·별칭·사건·사실·일정, 표시 컬럼 제외)이 같은 제안을 표시 없이 돌린 턴과 같음**(언급 둘 이상 + `create_person` 힌트가 든 제안으로 — 위계·관계 태그가 기본값으로 떨어지지 않는다, R-4) · 표시가 없으면 저장 행과 `reply` 가 변경 전과 같음(기존 루프 시험 무수정) · 문구 ②⑥ 글자 일치 · 같은 문장을 규칙이 잡은 경우와 거절 뒤 남는 것이 같은 모양 · **사후 긍정 재개 턴의 trace 중 `loop_*` step 만 본 순서 = `loop_resume` → `loop_gate`(재구성한 제안을 다시 판정 — 재개 턴에 하나 더) → 기록이면 `loop_resolve_done`·`loop_record`, 조회면 `loop_query` → `loop_turn`**(기존 재개의 "`loop_extract`/`loop_gate` 행은 남기지 않는다"(`loop.py` 1803~1805 docstring)와 달라지는 것은 사후 확인 재개뿐이고, 재구성 `Proposal.raw` 는 비어 있다 — 게이트·해석이 읽지 않는다, N-R5) · 닫힌 목록 밖 시험 diff 0(`… u6-test-diff -- git diff --stat <U6 직전 해시> -- tests` ⊆ `test_guard_posthoc.py`(새)·`test_guard_messages.py`·`test_agent_query_types.py`).
  - 검증: `POSTGRES_PORT=5433 … u6-posthoc -- .venv/bin/python -m pytest tests/test_guard_posthoc.py tests/test_agent_loop.py tests/test_agent_query_loop.py tests/test_agent_query_answer.py tests/test_agent_query_types.py tests/test_memory_loop.py tests/test_agent_propose.py tests/test_guard_messages.py -q` · 실 LLM 왕복(시연 발화 13개)은 사용자 지시 때.
  - 변이 후보: 사후 검사를 의도 분기(1128) 뒤로 옮기기 → 조회 "judge 0" FAILED · `attach_turn_refs` 의 구간 시작을 `TurnResult.trace_ids` 로 바꾸기 → `ask_user` 행 원문 FAILED · 사후 긍정 재개에서 `_gate` 재실행을 빼고 저장된 제안을 그대로 실행하기 → step 순서 단언과 "힌트 유지" 저장 행 시험 FAILED · 사후 거절 처리를 `resume_turn` 안으로 옮기기 → 거절 뒤 trace 전수 `LIKE` FAILED(N-R5).

- [ ] U7a **[backend-agent] 저장 표시 전파·동의 문맥 사슬·사실 표시 단조·승격 입력 제외·패턴 제외·민감 일정 문구** / Refs: P9d-sensitive-guard D20 D14 S3.2 S3.4 S3.5 원칙1 원칙6 원칙9 / 의존: U6 (개정 1 — M3 으로 옛 U7 의 앞 절반)
  - 파일: `app/tools/records.py`(`add_event`·`add_schedule` 이 `ctx.consent` 를 읽어 **같은 INSERT 문에서** `sensitive_category`·`consent_question_id` 를 채운다 — 시그니처·반환 타입 불변) · `app/tools/persons.py`(사실 upsert `set_` 에 `COALESCE(person_facts.sensitive_category, EXCLUDED.sensitive_category)`, 값은 `ctx.consent`) · `app/memory/direct_facts.py` · `app/memory/promote.py`(`_upsert_fact` 147 단조, 입력·최소 사건 수에서 민감 제외) · `app/memory/extract.py`(입력 제외) · `app/memory/patterns.py`(민감 사건 제외) · `app/agent/loop.py`(후속 질문 자리 `_extend_for_ask`·`_extend_identity_payload`·`_ask_schedule`·`_followup_new_person_turn` 에 context 최상위 `consent` 키, 재개 때 `ctx.consent` 복원, 민감 일정 문구 — 빈자리 ④) · `app/guard/messages.py`(민감 일정) · `tests/test_guard_storage.py`.
  - 방식: **표시를 채우는 자리는 툴이 `ctx.consent` 를 읽는 한 곳**(개정 1 — R-2, S3.2 문장도 이것으로 맞춘다). `tools_check` 는 툴 7종의 이름·인자(시그니처)를 보며 반환 타입 필드는 늘지 않는다. `consent` 는 `PendingResume` 밖 최상위 키라 `_apply_resume_byte_limit`(held_drafts 만 비움)에 닿지 않는다. 범주 하나만 저장하는 컬럼에는 D-1 확정 규칙(고정 순서의 첫 범주).
  - 수용 기준: CR-009 U7 ①~⑥ · 민감 일정 문구가 동의 턴에서 일정 저장 시 답 끝에 한 번 · 사전 동의 → identity → new_person → schedule 사슬에서 R-10 409 가 나지 않음(위 "중간 상태" 를 닫음) · `tools_check` 7/7. **시험 함수 이름에 `chain`·`monotone` 을 넣고, 선택된 시험 수 > 0 을 증거로**(R-8 — `-k` 가 0건이면 pytest 종료 코드 5).
  - 검증: `POSTGRES_PORT=5433 … u7a-storage -- .venv/bin/python -m pytest tests/test_guard_storage.py tests/test_memory_promote.py tests/test_memory_patterns.py tests/test_memory_extract.py tests/test_memory_loop.py tests/test_tools_persons.py tests/test_tools_records.py tests/test_agent_loop.py tests/test_guard_resume.py tests/test_guard_messages.py -q` · `… u7a-chain -- .venv/bin/python -m pytest tests/test_guard_storage.py -q -k chain` · `… u7a-monotone -- .venv/bin/python -m pytest tests/test_guard_storage.py -q -k monotone` · tools_check · `… u7a-er-unchanged -- git diff --stat <기준> -- app/er`(빈 출력).
  - 변이 후보: 후속 질문 하나(`_ask_schedule`)에서 `consent` 빼기 → 사슬 시험 FAILED · upsert 의 `COALESCE` 를 덮어쓰기로 → 단조 시험 FAILED.

- [ ] U7b **[backend-agent] 이름 규칙(사용자 결정 15·22) — `_apply_name_rule`·재개 거르기·방어·결정 22 의 글자 일치 통과·비소유 해석·근거 trace** / Refs: P9d-sensitive-guard D20 D5 D1 S3.2 원칙1 원칙2 원칙4 원칙9 / 의존: U7a (개정 1 — M3 으로 옛 U7 의 뒤 절반)
  - 파일: `app/agent/loop.py`(VR2 ①~⑤ — `_apply_name_rule`·재개 `pending_calls` 거르기·방어 1847·1856·1877 앞·`_execute_call` `new_alias`·`_resolve_mentions_impl` 580 뒤 비소유 검사 · `_pending_calls_from` 에 제외 언급 인자 · `ResolveOutcome` 에 버린 언급 필드) · `app/guard/names.py`(`existing_alias_owner_ids` · `REASON_NAME_RULE` — 게이트가 내는 사유가 아니라 `GATE_REJECTION_REASONS` 에 넣지 않는다, 전수 확인 절) · `app/guard/messages.py`(이름 거부) · `tests/test_guard_names.py`(새) · `tests/test_agent_loop.py`(닫힌 목록 — 426·483·600행 등식에 버린 인덱스 항, R-1).
  - 방식: VR2·VR6 행 그대로. 결정 22 = 글자까지 같은 별칭이 있을 때만 통과, 통과에는 `ctx.consent` 필요(없으면 `dropped_no_consent`), 별칭 주인이 아닌 인물로 해석되면 D-4 확정안 (a)(언제나 이름 거부). 빈자리 ③(방어에 걸리면 딸린 제안도 버림). **⑤ 갈래에서 버린 언급의 제안(개정 2 — N-R1)**: ⑤ 는 `_resolve_mentions_impl` 안이라 `verdict` 를 바꾸지 못한다 → 그 함수가 지역 집합 `dropped` 에 언급을 넣고, 뒤 언급의 되묻기에서 부르는 `_pending_calls_from(proposal, verdict, set(person_ids), excluded=dropped)`(599행 — 새 키워드 인자, 기본 빈 집합이라 기존 호출 동작 불변)가 그 언급의 제안을 빼며, `ResolveOutcome.name_rule_dropped` 로 답 문구(이름 거부)에 전달한다. **`name_rule_dropped` 에는 언급 문자열이 아니라 언급 인덱스(`first_index` 의 값) 목록을 싣는다**(3회차 P3-R6) — `ResolveOutcome.to_dict()` 가 `loop_resolve_done` trace 출력이 되므로 거부된 민감 표현이 trace 에 남지 않게(D20 R-3·원칙9, `guard_name_rule` trace 의 "언급 문자열 0" 과 같은 규칙). 시험: 그 trace 출력에 거부된 언급 문자열 0. 기록은 `_record`(926행)가 `person_ids` 에 없는 언급을 건너뛰어 원래 0.
  - 수용 기준: CR-009 U7 ⑦⑧ · 걸린 언급의 제안이 다른 언급 되묻기 context 의 `pending_calls` 에 0 · 배포 전 identity 질문 거절 시 "새로운 사람인가요?" 질문 0 · 자리표시 든 이름 저장 0 · **결정 22**: 저장된 별칭과 글자까지 같은 민감 표현(동의 턴)은 통과해 별칭 주인 인물에 기록되고 저장물 민감 표시·trace `passed_existing_alias`, **별칭 저장용 임베딩 0**(개정 2 — M5): 임베딩이 있는 기존 별칭 + 가짜 임베더를 붙인 그 턴에서 임베더 호출은 **후보 검색 질의뿐**이고(통과한 언급은 ER 후보 검색 `search_person` 이 질의로 임베딩한다 — `app/tools/persons.py:214`, D20 결정 22 가 받아들인 전송) 호출 횟수가 같은 인물을 민감 낱말 없는 기존 별칭으로 부른 턴과 같으며, `person_aliases` 행 수와 그 행의 `embedding` 값이 그대로 · 공백만 다른 변형 1건(예: 저장된 "마약쟁이 형" ↔ 언급 "마약쟁이형")은 이름 거부(trace `dropped`, 별칭·인물 행 0, 별칭 저장용 임베딩 0) · 동의 문맥 없는 턴의 일치 언급은 `dropped_no_consent` · 별칭 주인이 아닌 인물로 merge·new_person·identity 답이 나오면 D-4 (a)(별칭·인물 행 0, trace `dropped_non_owner`, 그 언급의 `er_resolve` trace 는 `applied` 가 거짓으로 남는다 — 조회 턴 1322행과 같은 모양, N-R3) · **앞 언급이 `dropped_non_owner` 이고 뒤 언급이 identity 질문으로 끝나면 그 질문 context 의 `pending_calls` 에 앞 언급의 제안 0**(N-R1 시험 1건) · `guard_name_rule` trace 에 언급 문자열 0 · `app/er/` diff 0. 시험 함수 이름에 `name_rule` 을 넣는다(R-8).
  - 검증: `POSTGRES_PORT=5433 … u7b-names -- .venv/bin/python -m pytest tests/test_guard_names.py tests/test_agent_loop.py tests/test_agent_query_loop.py tests/test_tools_persons.py tests/test_guard_messages.py -q` · `… u7b-name-rule -- .venv/bin/python -m pytest tests/test_guard_names.py -q -k name_rule` · tools_check · `… u7b-er-unchanged -- git diff --stat <기준> -- app/er`(빈 출력) · `… u7b-test-diff -- git diff --stat <U7a 해시> -- tests`(⊆ `tests/test_guard_names.py`·`tests/test_agent_loop.py`·`tests/test_guard_messages.py`).
  - 변이 후보: `_apply_name_rule` 을 `_pending_calls_from` 뒤로 → 되묻기 context 시험 FAILED · 결정 22 의 글자 비교를 정규화 비교(NFC·`casefold`·공백 제거 — 철회한 `name_key` 방식)로 바꾸기 → 공백 변형이 통과해 자동 연결에서 새 별칭 행 + 별칭 저장용 임베딩 1회가 생겨 "변형 거부"·"`person_aliases` 행 수 그대로"·"임베더 호출 횟수 같음" 시험 FAILED(한국어 낱말은 대소문자가 없어 `casefold` 만으로는 변형이 생기지 않으므로 공백 변형으로 검출한다) · 580 뒤 비소유 검사 빼기 → `dropped_non_owner` 시험 FAILED · `_pending_calls_from` 의 `excluded` 인자 빼기 → N-R1 시험 FAILED.

- [ ] U8 **[backend-agent] 내보내는 경로 제외(fail-closed) — `get_briefing`·브리핑 입력·일정 선정·카드 기본값·인물 목록·조회 답·MCP** / Refs: P9d-sensitive-guard D20 D16 D19 S3.2 S3.6 R12 R19 원칙7 / 의존: U7a(표시 컬럼 값)·U7b(같은 `loop.py` — 차례로)
  - 파일: `app/tools/briefing.py::get_briefing` · `app/briefing/inputs.py`(97~105·152~171) · `app/briefing/select.py`(기본·수동 55~69) · `app/api/read.py`(`list_persons` 149·`get_person_card(include_sensitive=False)` 183) · `app/api/routes.py`(카드 라우트만 `True`) · `app/api/schemas.py` · `app/agent/loop.py::_read_card` · `app/agent/respond.py`(조회 안내 — 민감 존재 여부는 별도 개수 조회) · `app/mcp_server/tools.py`(`sensitive_category` 키 제거) · `app/guard/messages.py`(조회 안내) · `tests/test_guard_export.py`.
  - 수용 기준: D20 R-6 "제외" 행 열거 계약 시험(상수 목록 — 새 경로가 빠지면 실패) · MCP 카드에 `sensitive_category` 키 0 · 민감 일정 수동 지정 skip 사유 `sensitive_schedule`(404 아님) · 최근 사건 상한은 거른 뒤 · 카드 계층 4경로에만 민감 항목 · **닫힌 목록**(전수 확인 절): `tests/test_api_read_persons.py:189` 다가오는 일정 키 집합에 `"sensitive_category"` · `tests/test_mcp_tools.py:293`(과 6행 docstring)은 비교 대상을 `read.get_person_card(...).model_dump(mode="json")` 에서 항목의 `sensitive_category` 키를 뺀 것으로 — 그 밖 시험 diff 0(`… u8-test-diff -- git diff --stat <U8 직전 해시> -- tests` ⊆ `test_guard_export.py`(새)·`test_guard_messages.py`·`test_api_read_persons.py`·`test_mcp_tools.py`).
  - 검증: `POSTGRES_PORT=5433 … u8-export -- .venv/bin/python -m pytest tests/test_guard_export.py tests/test_tools_briefing.py tests/test_briefing_inputs.py tests/test_briefing_select.py tests/test_briefing_run.py tests/test_briefing_compose.py tests/test_push_payload.py tests/test_mcp_tools.py tests/test_mcp_server.py tests/test_api_read_persons.py tests/test_api_read_raw.py tests/test_api_read_briefings.py tests/test_agent_query_answer.py tests/test_guard_messages.py -q` · tools_check.
  - 변이 후보: `get_person_card` 기본값을 `True` 로 → 열거 계약 FAILED · `get_briefing` 의 사건 필터 빼기 → 브리핑 프롬프트 0 FAILED.

- [ ] U9a **[frontend-agent] 가입 고지 체크·재고지 모달·403 `notice_required` 처리(`web/` 만)** / Refs: P9d-sensitive-guard D20 D18 원칙5 원칙7 / 의존: U4 커밋(계약 확정) — U5a~U8 과 동시
  - 파일: `web/src/lib/privacyNotice.ts`(④⑤ — 단일 출처) · `web/src/screens/AuthScreen.tsx` · `web/src/components/AppShell.tsx` · `web/src/api/types.ts`(`MeOut.notice_required?: boolean` — **선택 필드**로 둔다, 3회차 P3-R7: 기존 목 응답 `ME`·E2E 픽스처가 그 키 없이도 타입이 맞고 "`true` 일 때만 모달" 과 같은 뜻)·`client.ts`(가입 본문 `SignupIn` 에 `privacy_notice_accepted: boolean`) · `web/src/__tests__/notice.test.tsx`(새) · `web/src/__tests__/auth.test.tsx`(닫힌 목록 F1 — **단언 변경은 272행 가입 본문 하나**, 준비 줄은 가입을 제출하는 시험 전부에 고지 체크 클릭 한 줄(체크 없이는 버튼이 비활성이므로), 개정 2 — N-R6).
  - 수용 기준: 체크 없이 가입 버튼 비활성 · 모달 동의 전 `POST /chat` 호출 0 · 로그인 상태에서 `notice_required: true` 면 바로 모달 · **`notice_required` 가 `true` 일 때만 모달**(필드가 없거나 `false` 면 모달 0 — 기존 Vitest·E2E 목 응답 `web/e2e/fixtures.ts:45`·`auth.spec.ts:10` 은 고치지 않는다, R-6) · `/briefings/run`·`/answers` 403 도 같은 모달 · 새 라우트(화면) 0 · 문구 ④⑤ 글자 일치 · `u9a-test-diff` 파일 목록 ⊆ `auth.test.tsx`·`notice.test.tsx`.
  - 검증: `… u9a-vitest -- npm --prefix web exec -- vitest run --root web` · `… u9a-typecheck -- npm --prefix web run typecheck` · `… u9a-build -- npm --prefix web run build` · `… u9a-lint -- npm --prefix web run lint` · `… u9a-test-diff -- git diff --stat <U4 해시> -- web/src/__tests__`.
  - 변이 후보: 모달의 전송 잠금 빼기 → "동의 전 호출 0" FAILED.

- [ ] U9b **[frontend-agent] 채팅 차단 안내·거절 줄 표시, 인물 카드 민감 배지·기본 가림, 범주 한글 이름** / Refs: P9d-sensitive-guard D20 원칙5 원칙7 / 의존: U5b·U5c·U6·U8 커밋
  - 파일: `web/src/screens/ChatScreen.tsx`(칩 컴포넌트 무변경) · `web/src/screens/PersonCardScreen.tsx` · `web/src/lib/labels.ts` · `web/src/__tests__/chat.test.tsx`·`card.test.tsx`·`labels.test.tsx`.
  - 수용 기준: `kind="sensitive"` 칩이 기존 칩과 같은 DOM · 차단 안내는 `reply` 문자열 그대로 보임 · `content` 가 "(기억하지 않은 민감한 내용)" 인 사용자 줄은 흐린 글씨 · 민감 항목 기본 가림 — 가린 상태에서 배지 "민감"·범주 이름·(사건) 날짜·종류 이름·(사실) 키 이름만 보이고 값·사건 내용·일정 제목은 0, "눌러서 보기" 로 펼침(빈자리 ⑦) · 범주 키 한글 이름(D-2 확정 (a): "범죄·불법"·"건강"·"성"·"정치·종교"·"금융") · Vitest·typecheck·build·lint 통과.
  - 검증: 위 U9a 와 같은 4개 명령(`u9b-*`).
  - 변이 후보: 가림 기본값을 `false` 로 → 카드 시험 FAILED.

- [ ] U10 **[eval-agent] 평가 실행·실패 분석 — 규칙 단독 수치와 사후 LLM 표시 수치 분리** / Refs: P9d-sensitive-guard D20 S3.7 원칙8 / 의존: U2(규칙)·U6(LLM 표시)
  - 파일: `evaluation/sensitive_guard/run.py`(test 분할·LLM 표·이름 규칙 오탐 표 추가) · `reports/sensitive_guard.md` · `reports/sensitive_guard_metrics.json`.
  - 수용 기준: test 동결 해시 = 실행 입력 해시 · 놓친 문장·오탐 문장 전부 사례 표 · 규칙 수치와 LLM 수치가 같은 표에 없음 · LLM 표는 "1회 실행"·모델명·날짜·비용 · 재실행 명령 1줄 · verifier 가 원시 결과에서 재계산해 일치.
  - 검증: `… u10-test -- .venv/bin/python -I evaluation/sensitive_guard/run.py --split test` · LLM 표는 실행 비용 상한(D-3 확정 $1 — 넘으면 멈추고 보고) 안에서 사용자 지시 뒤.
  - 변이 후보: 러너가 test 해시 검사를 건너뛰게 → 해시 불일치 시험 FAILED.

- [ ] U11 **[verifier] 완료 검토(로컬) — verify-impl·04-review·변이** / Refs: P9d-sensitive-guard D20 CR-009 원칙8 / 의존: U1~U10 각 리뷰 통과 + 마지막 해시 전체 pytest·Vitest 증거
  - 내용: `bash .claude/scripts/verify-impl.sh P9d-sensitive-guard` · 아래 수용 기준 판정 표 대조 · 변이(U5a·U5b·U5c·U6·U7a·U7b·U8 후보 중 각 1개 재실행 + downgrade 가드 빼기 + 러너 `--split test` 거부 빼기).

- [ ] U12 **[메인 세션 SSH + 사용자] 운영 반영 — 백업 → 0006 → 재배포 → 바깥 확인 → 기존 가입자 재고지 실제 확인** / Refs: P9d-sensitive-guard D17 D18 D20 / 의존: U11 `결과: 완료`
  - 파일: `docs/user-setup/13-user-todo-deploy.md` J 절(I 절 형식 인용).
  - **사전 예행(로컬 운영 구성 — 운영 반영 전, P9b U14 와 같은 모양)**: 0005 데이터 볼륨 → `0005 -> 0006`(행 수 같음) · 민감 행이 없을 때 downgrade 0005 성공 · **민감 질문 행 1개를 만든 뒤 downgrade 가 실패하고 데이터 불변** · `upgrade` 실패 분기(DDL 이 트랜잭션 안이라 0005 그대로) 확인. 증거 이름: `u12-local-upgrade`·`u12-local-downgrade-ok`·`u12-local-downgrade-blocked`·`u12-local-smoke`.
  - 절차(R-10 반영): ① 백업 — `docker compose -f docker-compose.prod.yml exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > ~/backup-<시각>-pre-0006.sql`(서버 홈, 파일은 서버에만 — 11-18 선례 `P9b-auth/03-log.md:316` 과 같은 방식). 확인: `ls -l ~/backup-<시각>-pre-0006.sql`(0바이트 아님) · `tail -n 3 …`(`PostgreSQL database dump complete` 줄) ② 전 행 수(계정·인물·사건·사실·일정·대화·대기 질문·별칭) ③ 미답·미만료 대기 질문 수 ④ `git pull` → `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`(`docker/entrypoint.sh:10` 이 `alembic upgrade head` → `Running upgrade 0005 -> 0006`) ⑤ 후 행 수 = 전 · `/api/health` `alembic_revision` `0006` · backend 로그 Traceback 0 ⑥ 바깥 GET: `/` 200 · `/api/persons`·`/api/auth/me` 401 · `/mcp` 401 JSON → **되돌릴지 판단하는 시점은 여기(⑥ 뒤·⑦ 앞)** ⑦ 사용자: 열려 있던 탭 **새로고침**(옛 화면은 403 에 모달이 없다) → 기존 계정 접속 → 모달 → 동의 전 전송 막힘 → 동의 뒤 전송 → 민감 문장 칩 확인.
  - 되돌리기(J 절에 적는다): (가) ④ 에서 `alembic upgrade` 자체가 실패해 backend 가 뜨지 않으면 — DB 는 0005 그대로(트랜잭션 롤백) → `git checkout <이전 해시>` → `up -d --build`, downgrade 불필요. (나) ⑥ 뒤·⑦ 전(민감 행 0)이면 I 절과 같은 순서 — `stop backend` → `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml run --rm --entrypoint python backend -m alembic downgrade 0005` → `git checkout <이전 해시>` → `up -d --build`. 이때 `users.privacy_notice_*` 두 컬럼(고지 동의 기록)도 사라진다. (다) ⑦ 에서 사용자가 민감 칩에 답한 뒤에는 `kind='sensitive'` 행이 생겨 **downgrade 가 설계대로 실패**한다 — 멈추고 사용자에게 묻는다. 백업 복원은 마지막 수단이고 그 뒤 입력이 사라지며 데이터 삭제를 동반하므로 **사용자가 직접 실행**한다(`security.md` 6절): `stop backend` → DB 비우고 다시 만들기 → `docker compose … exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < ~/backup-<시각>-pre-0006.sql` → `git checkout <이전 해시>` → `up -d --build`(명령 전문은 J 절에, 에이전트는 실행하지 않는다).
  - 수용 기준: 사전 예행 증거 4개 · ①~⑦ 증거(`evidence/<시각>-u12-*.txt`, 값·토큰 0) · verifier 가 04-review 부록에서 대조 · 사용자 화면 확인.

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- **D20 "코드에서 지켜야 할 것" ① 표 1~17(= CR-009 4.3)** — 동의 전 LLM·임베딩 0 · 식별 원문 DB·응답·로그 0 · 검사가 대화 기록·루프보다 앞 · 거절·만료 뒤 원문 DB 전수 0(질문 context 는 남기는 키만, 동의 기록은 남음) · 사후 표시 턴은 기록·조회 모두 ER·임베딩·조회 답 LLM 전에 멈춤 · 동의 턴 저장물 전부 표시(후속 질문 사슬 끝까지) · 사실 표시 단조 · 민감 항목 카드 계층에서만(열거 계약 시험) · 카드 읽기 기본 제외 · 고지 필수·미동의 `/chat`·`/answers`·`/briefings/run` 403·주기 브리핑·푸시 0 · 이름 규칙(질문 전 멈춤) · 로그인 예외 경로 변화 0 · 툴 7종 7/7·`app/er/` 무변경 · 문구 문자열 일치·금지 표현 0 · kind CHECK 4종·downgrade 가드 · 배포 전 대기 질문 재개 막음 · 감지율·오탐률 재현(규칙·LLM 분리) · **완료 = 운영 반영 + 평가 보고서 + verifier 완료 검토 + 사용자 화면 확인**(사용자 결정 11, 서버 종료일은 그때)

### 판정 표 (D20 ① 표의 행 → 이 계획의 판정 명령)
| D20 # | 판정 명령(위 단위의 증거 이름) | 단위 |
|---|---|---|
| 1 | `u5b-pre` | U5b |
| 2 | `u5a-mask` · `u2-no-log` | U5a·U2 |
| 3 | `u5a-mask`·`u5b-pre` + U11 변이(검사를 `append_chat_message` 뒤로) | U5a·U5b |
| 4 | `u5c-resume` · `u6-posthoc` | U5c·U6 |
| 5 | `u6-posthoc` | U6 |
| 6 | `u7a-storage` · `u7a-chain`(선택 시험 수 > 0) | U7a |
| 7 | `u7a-monotone`(선택 시험 수 > 0) | U7a |
| 8·9 | `u8-export` + U11 변이(기본값 `True`) | U8 |
| 10 | `u4-notice` · `u4-scheduler` | U4 |
| 10b | `u7b-names` · `u7b-name-rule`(선택 시험 수 > 0) | U7b |
| 11 | `u4-notice`(`test_auth_required_routes.py`) | U4 |
| 12 | `u<N>-tools-check` 7/7 · `u7a-er-unchanged`·`u7b-er-unchanged`(빈 출력) | 전 단위 |
| 13 | `test_guard_messages.py`(U5a·U5b·U5c·U6·U7a·U7b·U8) · `notice.test.tsx`(U9a) | U5a·U5b·U5c·U6·U7a·U7b·U8·U9a |
| 14 | `u3-migration` | U3 |
| 15 | `u5c-resume`(`-k legacy`) | U5c |
| 16 | `u10-test` | U1·U10 |
| 17 | U12 증거 · `reports/sensitive_guard.md` · 04-review `결과: 완료` · 사용자 화면 확인 | U10·U11·U12 |

단위 공통 회귀(단위마다, 리뷰 전): 전체 `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q`(실패 0·skip 0) · `.venv/bin/python -m ruff check app tests scripts evaluation` · `.venv/bin/python scripts/mypy_check.py --run`(새 오류 없음) · tools_check 7/7 · `git diff --stat <기준> -- app/er reports data`(U10 의 `reports/sensitive_guard*` 만 예외) · 범위 = 그 단위 파일 목록만 · 증거에 원문 민감 문장을 그대로 남기지 않는다(시험용 문장만) · **모든 단위 공통(3회차 P3-R2)**: 전체 pytest·Vitest 에서 그 단위의 닫힌 목록 밖 시험이 깨지면 고치지 말고 **멈추고 03-log 에 보고**한다 — 목록을 넓힐지는 verifier 커밋 전 리뷰에서 정한다(단위 본문의 같은 문장은 이 규칙의 반복이다).

## 사용자 결정 (D-1~D-3 은 **확정** — 사용자 2026-11-22. D-4 는 개정 1 에서 새로 드러남 — **확정 (a) 언제나 이름 거부, 사용자 2026-11-22**(표의 "답 대기" 는 이력). 이미 확정된 22건은 다시 묻지 않는다)

| # | 무엇 | 후보 | 권장 | 이유 |
|---|---|---|---|---|
| **D-4** (답 대기 — U7b 착수 전에 필요) | 사용자 결정 22 로 통과한 기존 별칭 표현이 **별칭 주인이 아닌 인물**로 해석될 때(ER 이 다른 인물로 자동 연결 / identity 질문에서 다른 후보를 고름 / 새 인물로 판정·identity 거절) — VR6 (가) | (a) **언제나 이름 거부** — 자동 연결·새 인물 밴드는 질문 전에 그 언급을 거부하고, identity 답이 다른 인물이면 별칭 저장 없이 거부, identity 거절도 "새로운 사람인가요?" 전에 거부. 그 언급의 기록은 남지 않는다 (b) **별칭 없이 그 인물에 연결** — 자동 연결·identity 답이면 별칭을 저장하지 않고 그 인물에 기록(민감 표시), 새 인물 밴드·identity 거절은 (a) 처럼 거부. ER 적용(`apply_resolution`)을 건너뛰는 자리가 생겨 `er_resolve` trace 의 `applied` 가 거짓으로 남는다(조회 턴 1322행과 같은 모양) | **(a)** | 결정 22 의 문장은 "그 인물(별칭 주인)에 계속 기록한다" 이다. (a) 는 그 밖의 경우를 모두 결정 15("저장하지 않고 안내")로 돌려 경로가 하나이고 trace 의미가 바뀌지 않는다. (b) 는 사용자가 고른 인물에 기록이 남지만 ER 적용을 건너뛰는 새 경로가 생긴다 |

**확정된 D-1~D-3(이력 — 아래 표는 결정 근거)**

| # | 무엇 | 후보 | 권장 | 이유 |
|---|---|---|---|---|
| **D-1** | 한 턴에 동의 범주가 **둘 이상**일 때(예: 범죄 + 건강) 저장 컬럼 `sensitive_category`(값 하나)에 무엇을 넣나 — 카드 배지에 보이는 범주 | (a) 고정 순서(`crime`·`health`·`sex`·`politics_religion`·`finance`)의 첫 범주 하나 (b) 리비전 0006 의 컬럼을 범주 목록(배열)로 바꿔 전부 저장 (c) 범주와 상관없는 표시값 `sensitive` 하나만 | **(a)** | 제외·가림 동작은 "NULL 이 아님" 만 보므로 어느 안이든 같다. (b) 는 S3.1 보충(문자열 + CHECK)과 D20 문장을 바꾼다. (c) 는 카드에서 무슨 범주인지 안 보인다 |
| **D-2** | 인물 카드 배지·범주 표시 문구(사용자에게 보이는 글) | (a) 배지 "민감" + 범주 이름 "범죄·불법"·"건강"·"성"·"정치·종교"·"금융", 가림 상태 "눌러서 보기" (b) 범주 이름 없이 "민감한 기록 · 눌러서 보기" 만 | **(a)** | CR-009 범주 이름 그대로라 새 용어가 없다. (b) 는 D-1 과 상관없이 단순하지만 사용자가 무엇이 가려졌는지 모른다 |
| **D-3** | U10 사후 LLM 표시 측정(실 OpenAI 1회)의 비용 상한 | (a) $1 (b) $2 (c) 상한 없이 사용자 지시 때 1회 | **(a)** | 대상은 규칙이 놓친 test 문장뿐(수십 건)이고 기존 추출 모델 1회라 $1 안으로 추정. P4b 의 "$5/1회" 같은 상한 관례를 따른다. 넘으면 멈추고 보고 |

## 리스크 · 미결
- 낱말 규칙 오탐이 대화 마찰을 만든다(W4) — U10 오탐률을 보고, 크면 재시도가 아니라 실패 분석 뒤 범주 축소를 다시 묻는다(원칙8).
- 추출 스키마 필드 증가로 추출 품질 흔들림(W7) — U6 실 LLM 대조는 사용자 지시 때. P10 전.
- LLM 사후 표시의 재현성 낮음(W8) — U10 LLM 표는 "1회 실행".
- 문구 ④⑤ 와 판 번호의 묶기는 기계적이지 않다(위 "주인" 절) — 리뷰 항목으로.
- `turn_trace_range` 의 여러 탭 동시 요청(위 VR 표) — 넓게 지우는 쪽.
- R-10 규칙 목록 변경 창 — U12 ③ 기록.
- 기존 데이터 무표시 송출·저장 브리핑·식별 원문 잔존(W14), 기존 민감 별칭의 ER 재전송(사용자 결정 22) — 받아들인 위험, 완화책을 더하지 않는다.
- U4 의 주기 작업 조인은 `users` 행이 없는 `persons.user_id` 를 제외한다 — 운영에서는 모든 인물이 로그인 계정 소유라 영향 없음, 시험 준비 줄만 바뀐다(VR3 닫힌 목록 — `test_briefing_scheduler_users.py`·`test_push_wiring.py`). 미동의 계정 건너뜀은 trace 를 남기지 않는다(VR7 — 사용자에게 알릴 것).
- 운영에서 되돌릴 수 있는 창은 U12 ⑥ 뒤·⑦ 앞뿐이다(사용자가 민감 칩에 답하면 downgrade 가 막힌다 — 사용자에게 알릴 것).
- `evaluation/recognition/probe.py` 는 U4 에서 가입 본문을 고친다(고치지 않으면 운영 가입이 422).
- 결정 22 의 통과 조건은 글자 일치라 저장된 별칭과 공백·대소문자만 다르게 부르면 이름 거부된다(메인 세션 결정 — 결정 22 의 "정확히 일치" 안). 언급은 LLM 이 낸 문자열이라 흔들릴 수 있다 — U10 이름 규칙 오탐 표에서 본다.
- U5c~U6 커밋 사이 중간 상태(동의 턴 후속 질문이 R-10 409) — 위 순서 절, U7a 가 닫는다.
- `get_briefing` 동작 변경(툴 7종 시그니처 불변) — 호출자는 브리핑 입력 하나.

## 사용자만 할 수 있는 일 · 에이전트가 검증할 수 없는 것
- U2 산출물 낱말·정규식 목록 검토(G2) — **관문 아님**(메인 세션 결정): U2 뒤 보고, 수정 요청은 U12 전 아무 때나 반영.
- D-4 답 — **확정(사용자 2026-11-22, AskUserQuestion)**: **(a) 언제나 이름 거부.** 결정 22 로 통과한 기존 별칭 표현이 별칭 주인이 아닌 인물로 해석되면(다른 인물로 자동 연결 · identity 답이 다른 후보 · 새 인물 밴드 · identity 거절) 기록하지 않고 이름 거부 안내로 답한다. 위 표 D-4 행과 U7b 의 "D-4 확정안" 은 이 (a) 를 가리킨다.
- 위 D-1~D-3 답 — **확정(사용자 2026-11-22, AskUserQuestion)**: D-1 = (a) 고정 순서(`crime`·`health`·`sex`·`politics_religion`·`finance`)의 첫 범주 하나 · D-2 = (a) 배지 "민감" + 범주 이름 + "눌러서 보기" · D-3 = (a) $1(넘으면 멈추고 보고).
- U6 실 LLM 대조·U10 실 LLM 측정 실행 지시(OpenAI 비용).
- U12: 운영 화면에서 기존 계정 재고지 모달·민감 문장 칩 확인, 완성 확인 뒤 서버 종료일 결정(사용자 결정 11).
- 고지 문구의 법적 충분성·OpenAI 약관 확인(이 계획은 판단하지 않는다).

## 읽은 카드
- `docs/wiki/changes/CR-009.md` 전문(개정 3 — 4.2·4.3·4.4·8절) · `docs/wiki/changes/review-CR-009.md` 재검토(개정 2) 절(VR1~VR8·V-8)
- `docs/wiki/decisions/D20-sensitive-guard.md` 전문 · D2·D14·D16·D17·D18·D19 의 CR-009 보충 줄
- `docs/wiki/specs/S3.1`(0006 보충)·`S3.2`·`S3.4`·`S3.5`·`S3.6`·`S3.7`
- `docs/backlog.md` P9d 행 · `docs/wiki/templates/plan.md` · `docs/wiki/packages/P9b-auth/01-plan.md`(머리·판정 방법·수용 기준 절 — 표기 관례) · `.claude/scripts/verify-plan.sh` · `docs/wiki/registry.md`(grep `guard|sensitive|privacy|consent|auth_helpers|make_user` — 겹치는 산출물은 `tests/auth_helpers.py` 1건, P9b-auth 산출물을 확장) · `.claude/gitlog.md`
- 코드: `app/agent/loop.py`(395~434·536~645·1087~1190·1238~1360·1830~1890, 함수 목록) · `app/agent/types.py` 370~440 · `app/er/pipeline.py` 420~474 · `app/briefing/scheduler.py` 100~219 · `tests/auth_helpers.py` 50~139 · `app/api/routes.py` 196~560 · `app/api/delete.py` · `app/er/judge.py` 118~170 · `app/tools/questions.py` 88~325 · `app/mcp_server/tools.py` · `app/briefing/inputs.py` 80~172 · `app/api/read.py` 145~330 · `docs/user-setup/13-user-todo-deploy.md` I 절 · `docs/wiki/fixes/FIX-015.md` 결과 절
- (개정 1) `docs/wiki/packages/P9d-sensitive-guard/02-plan-verify.md` 2·3절 전문 · `tests/test_schema_models.py` 1~300 · `tests/test_schema_check.py` 전문 · `tests/test_migration_0003.py` 40~65·222~331 · `tests/test_migration_0004.py`·`0005.py`(grep `_columns|"000[45]"`) · `tests/test_briefing_scheduler.py` 160~208 · `tests/test_push_wiring.py`·`tests/test_briefing_scheduler_users.py`·`tests/test_commit_boundaries.py`(grep `default_run_once|make_user|Person\(`) · `scripts/schema_check.py`(grep) · `app/briefing/scheduler.py` 100~219

## 개정 이력

### 개정 1 (2026-11-22, architect — 02-plan-verify 1차 보류 반영)
| 소견 | 고친 자리 | 한 줄 |
|---|---|---|
| **M1** | 사실 절(시험 도우미)·산출물(U4 닫힌 목록)·VR3 행·U4 파일·수용 기준·검증 | grep `default_run_once\|_due_user_ids` 4파일을 직접 확인 — `test_push_wiring.py`·`test_briefing_scheduler_users.py` 준비 줄을 닫힌 목록에, `test_briefing_scheduler.py`·`test_commit_boundaries.py` 는 고칠 필요 없음(근거 적음). `_MUST_REQUIRE_LOGIN` 1줄을 단언 예외로 명시. `u4-scheduler` 에 두 파일 추가 |
| **M2** | 사실 절(스키마 고정 단언)·산출물(U3 닫힌 목록)·U3 | S3.1 보충 0006 에서 다시 셈: 컬럼 **79 → 85**(+6), nullable **이름 집합 7 → 11**(+4 — 검증자 메모의 13 은 컬럼 수), `QUESTION_KINDS` **3 → 4**, CHECK **5 → 8**(+3), `events` CHECK 시험은 `type` 만 거름, 테이블 13·FK 9·인덱스 13·UNIQUE 8 그대로. `test_migration_0003/0004/0005` 의 head 기준 집합·리터럴. `scripts/schema_check.py` 무수정. `u3-migration` 이 통과하도록 0003~0006 을 같이 돌리고 `u3-test-diff` 추가. 선례 `c85a0e8` |
| **M3** | 순서 그림·U7 → U7a·U7b·판정 표 6·7·10b·12·13·U8 의존·U11 변이·담당 줄·backlog P9d `단위:` 줄 | 옛 U7 을 표시 전파·사슬·단조·승격·패턴(U7a)과 이름 규칙·결정 22·근거 trace(U7b)로. U7b 는 새 시험 파일 `tests/test_guard_names.py` |
| **M4** | 사실 절·VR2 ⑤·VR6 행·U7b·사용자 결정 D-4·CR-009·D20·S3.2 | 메인 세션 결정 (b): 글자까지 같은 별칭만 통과, 변형은 거부(`name_key` 철회). `_add_alias` 가 같은 글자 행을 찾아 새 행·임베딩 0 → `app/er/` 무수정. 수용 기준에 별칭 행 변화 0·별칭 임베딩 0·변형 거부 시험. (가) 비소유 해석은 실제로 생긴다 → D-4(권장 (a) 언제나 거부). (나) 동의 문맥 없는 통과 턴도 생긴다(언급이 발화의 부분 문자열이라는 보장 없음 — "같은 목록이니 늘 동의가 있다" 는 성립하지 않음) → `dropped_no_consent` 로 거부 |
| R-1 | VR2 행·U7b·D20 R-7·S3.2 | 이름 규칙 자리 문장을 계획(`_continue_after_gate` 기록 갈래 앞 `_apply_name_rule`)에 맞춤. `test_agent_loop.py` 등식에 버린 인덱스 항 |
| R-2 | U7a 방식·S3.2 | 표시는 툴이 `ctx.consent` 를 읽어 같은 INSERT/upsert 문에서. `tools_check` 는 시그니처만, 반환 타입 불변 |
| R-3 | VR7 행·리스크·CR-009 9절 | 미동의 건너뜀 trace 0 은 계획이 정함 — CR 4.2 U4 의 "`briefing_run` trace 에 사유" 문장은 이력 |
| R-4 | VR1 행·U6 | 사후 질문 context = `proposal_calls` 전부 → 재개 때 `Proposal` 재구성 → `_gate` → `_continue_after_gate`. `PendingResume`·`_synthetic_proposal_and_verdict` 미사용. 힌트 유지 시험 |
| R-5 | 순서 절·U5c | R-10 검사는 소유·상태 확인 뒤·답 저장 앞(쓰기 0, 질문 소비 안 함). U5c~U6 중간 상태 한 줄 |
| R-6 | VR3 행·U4·U9a | `probe.py` 를 U4 닫힌 목록에. 프론트는 `notice_required === true` 일 때만 모달 |
| R-7 | "빈자리 9건" 절 | ①~⑨ 를 근거와 함께 정함. 사용자에게 보이는 것은 D-2 확정 범위 안이라 새 결정 없음 |
| R-8 | U7a·U7b·판정 표 | 시험 이름에 `chain`·`monotone`·`name_rule`, 선택 수 > 0 |
| R-9 | U2·사용자만 할 수 있는 일 | 목록 검토는 관문 아님(메인 세션 결정). 러너 `--split test` 거부 시험 |
| R-10 | U12 | 사전 예행 4개·`pg_dump` 전문·백업 확인·되돌릴 창(⑥~⑦)·upgrade 실패 분기·복원은 사용자 직접·고지 컬럼 소실·새로고침 |
| R-11 | 판정 표 13·D20 ① 표 #13 | 판정 명령에 `notice.test.tsx`, 단위 칸 U5a·U5b·U5c·U6·U7a·U7b·U8·U9a |
| R-12 | U1 | 지어낸 식별번호 규칙과 검사기 항목 |
| R-13 | 사실 절·사용자 결정 절·U9b·U10·U5a | 백업 인용 `P9b-auth/03-log.md:316`, D-1~D-3 "확정" 표기, 옵션 밖 답의 `tool_error` trace 는 범위 밖 |

### 개정 2 (2026-11-22, architect — 02-plan-verify 2회차 보류 반영)
| 소견 | 고친 자리 | 한 줄 |
|---|---|---|
| **M2-잔여** | 사실 절(스키마 고정 단언)·산출물(U3)·U3 닫힌 목록·`u3-api`·`u3-test-diff` 기대 목록·전수 확인 절 | `tests/test_api.py:93` `"0005"` → `"0006"`, `tests/test_migration_0004.py:110`(0003 상태 `columns_before`)도 157행과 같은 식. U3 에도 "목록 밖에서 깨지면 멈추고 보고" |
| **전수 확인**(메인 지시) | 새 절 "고정 단언 전수 확인" · 산출물 · U4·U5a·U6·U8 닫힌 목록 | 같은 종류로 더 찾은 것 — U4 `MeOut` 키 집합 `test_auth_api.py:96`·`test_auth_nickname.py:70`(단언 예외 3줄로) · U5a `test_agent_query_gate.py:101·102`(거부 사유 7 → 8, 새 사유를 마지막 앞에) · U6 `test_agent_query_types.py:38`(`PROPOSAL_SCHEMA` 최상위 속성 — 턴 수준 필드를 거기에 두도록 U6 파일 문장도 정정) · U8 `test_api_read_persons.py:189`·`test_mcp_tools.py:6·293`. 고치지 않는 것과 이유도 표로 |
| **M5** | U7b 수용 기준·변이 후보 | "별칭 임베딩 호출 0" → "별칭 **저장용** 임베딩 0 — 임베더 호출은 후보 검색 질의뿐(호출 횟수가 민감 낱말 없는 기존 별칭 턴과 같음), `person_aliases` 행 수·`embedding` 값 그대로". 변이는 정규화 비교(공백 제거 포함)로 — 공백 변형이 통과해 새 별칭 행·임베딩이 생겨 검출 |
| N-R1 | U7b 방식·수용 기준·변이 | `_pending_calls_from(…, excluded=dropped)` + `ResolveOutcome.name_rule_dropped`, 시험 1건 |
| N-R2 | U5c 방식·파일·수용 기준·변이 | `answer_question` 은 고치지 않고 `app/api/deps.py::legacy_resume_blocked` 를 앞에서 — 이미 답한 질문은 `already_answered` 시험 |
| N-R3 | U7b 수용 기준 · D20 R-7 | 판정 뒤 버리는 갈래(D-4 (a))와 원칙1·2 관계 한 줄, `er_resolve` `applied` 거짓 시험 |
| N-R4 | 사실 절 19행 | `test_briefing_scheduler.py` 5줄, 안전한 이유 = 다른 세션·대상 0명 |
| N-R5 | U6 수용 기준·변이 · U5c 변이 | 사후 긍정 재개의 `loop_*` step 순서(`loop_gate` 하나 더), 거절을 `resume_turn` 안으로 옮기는 변이 |
| N-R6 | U9a 파일 | 단언 변경은 272행 하나, 가입 제출 시험마다 체크 클릭 준비 줄 |
| N-R7 | 계약 표·U4 수용 기준 | 가입 필드는 선택값으로 받아 라우트가 판정 — 422 `{"detail":{"code":"notice_required"}}` |
| N-R8 | 머리 태그 줄 | `D1` 을 기대는 결정에 더함(U7b Refs 와 맞춤) |
| (정리) | VR2 행·U7b 파일 | `REASON_NAME_RULE` 은 `app/guard/names.py` 상수, `GATE_REJECTION_REASONS` 에 넣지 않음(게이트 출력 아님 — `test_agent_gate.py:409` 와 맞음) |

### 3회차 통과 뒤 권고 반영 (2026-11-22, architect — P3-R1~P3-R7. 단위 줄·수용 기준 문자열·Refs 무변경)
| 권고 | 고친 자리 | 한 줄 |
|---|---|---|
| P3-R1 | 산출물(U4)·VR3 행(예외 3 → 7줄)·전수 확인 표·U4 파일 | `MeOut` 사전 동등 비교 `test_auth_nickname.py:83·85`·`test_auth_helpers.py:105` + Grep `json\(\) == \{` 로 다시 찾은 `test_auth_api.py:226` |
| P3-R2 | 단위 공통 회귀 | "목록 밖에서 깨지면 멈추고 03-log 보고" 를 모든 단위 공통 규칙으로 |
| P3-R3 | U4 | `notice_required` 는 세 형식 검사 뒤·409 사전 조회 앞(기존 `signup` 순서 관례), 시험 1건 |
| P3-R4 | U7b 방식 | `_pending_calls_from` 호출 행 599 |
| P3-R5 | D20 R-7 · CR-009 4.2 U6·9절 | D-4 를 확정 (a) 로 · `PROPOSAL_SCHEMA` 최상위 선택 속성 |
| P3-R6 | U7b 방식 | `name_rule_dropped` 는 언급 인덱스(문자열 0), 시험 1건 |
| P3-R7 | U9a 파일 | `MeOut.notice_required` 는 선택 필드 |
