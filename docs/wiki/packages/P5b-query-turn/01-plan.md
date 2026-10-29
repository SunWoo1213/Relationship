# P5b-query-turn · 계획 (01-plan)

상태: 초안 개정 3(architect 초안 2026-10-28 → 사용자 확정 15:40 결정 A~L + D16 보정 2건 → 개정 1 → verifier 1차 **보류**([필수] H-1·H-2, [권고] R-1~R-7) → 사용자 결정 **H-1 (a) `intent` 선택 키·`required` 무변경 / H-2 문장 붙이는 규칙 확정** → 개정 2 → verifier 2차 **통과**(2026-10-29, [필수] 0, 새 [권고] R-8·R-9) → 개정 3: R-8 결정 F ⑤ 양성 조건(`answer_source == "llm"` 뿐) · R-9 결정 I/G 이름 참조 3곳 확정값으로. 개정 2 내용: U1 91행·결정 A 표·결정 F 규칙 ①~⑤·결정 K 호출 형태(R-1)·결정 I 조건문 정리(R-2: U4 ②·해석 ㄴ·D-3 ①·U4 변이 표)·공통 절 `-k` 0건 = 실패(R-4)·스크래치패드 규칙(R-5)·U2 (ii) 문장·위치(R-7)·`env` 접두 제거. R-3 미커밋은 승인 커밋에, R-6 은 리스크 절 메모) | 담당: backend-agent(sonnet, `app/agent/`·`app/settings.py`·`tests/`), 검증 verifier(fable), U7 실 LLM 왕복은 사용자·메인 세션 | 작성: 2026-10-28
태그 — 패키지: P5b-query-turn · 닫는 검증: 없음(R19 경계를 재사용 — review-index R19 비고 "CR-004(D16): 같은 금지 표현 검증기를 채팅 조회 답에도 재사용") · 기대는 결정: D16 D1 D2 D6 D10 D11 · 구현하는 명세: S3.4 S3.2 S3.6 · 관련 원칙: 원칙1 원칙2 원칙4 원칙7 원칙9
의존: P5-loop(04-review `결과: 완료`, 2026-09-25) · P6-briefing(04-review `결과: 완료` — 금지 표현 검증기 `a2f032d`) · P8-frontend(04-review `결과: 완료`, `fe76931` — U1 `get_person_card` `6c2d0e7`). P4 게이트는 P4b 통과(`1075dd6`)로 이미 풀려 있다.

- **기준 해시(무변경 diff 기준점) = `8a8767b`** (dev2 HEAD, CR-004 문서 커밋). `.claude/gitlog.md` 기준 마지막 제품 코드 커밋은 `a0f4bc3`(P8b E2E, `web/`)이고 그 뒤 `fff6e8c`·`678bca7`·`8a8767b` 는 문서 커밋뿐이므로 `8a8767b` 의 제품 코드 = `a0f4bc3` 의 제품 코드다. 백엔드 마지막 코드 커밋은 P8b U0 `adc650e`(`app/api/read.py` `list_persons` 별칭) — `app/` 기준으로는 `adc650e..8a8767b` diff 가 비어 있다. `web/` 은 `adc650e` 이후에 바뀌었으므로(`2112a2a`·`529922f`·`a0f4bc3`) **무변경 diff 는 모든 경로를 `8a8767b` 하나로 잰다**(경로마다 기준이 다르면 틀린 해시를 쓰는 실수가 생긴다).
- 태그별 커밋 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P5-loop D16 CR-004 R19` 실행을 요청**한다 — 이 문서는 Bash 없이 `.claude/gitlog.md` 스냅샷(2026-10-28 14:23)과 `registry.md` 등록 해시만 근거로 썼다(L-001).
- 기존 테스트 수 기준: **1958**(P8b U0 `evidence/20261027-1436-u0-pytest-all.txt` "전체 1958 passed, skip 0", CR-004 §5 "기존 테스트 1958 건이 회귀 그물").

## 목표

CR-004 §1 표 1행(기획서 1장 "…장기 메모리를 구축하고, 만남 직전에 필요한 맥락만 요약")의 새 칸 — "**대화에서도 메모리를 읽는다**: '○○랑 마지막에 언제 봤지?', '○○는 뭐 좋아해?' 에 기록된 사실로 답" — 을 코드로 옮긴다. 지금 채팅은 기록 전용이라, 2026-10-16 U10 에서 "박선우 과장님이랑 나는 관계가 뭐야?" 라고 묻자 인식 LLM 이 `search_person` 을 제안하고 게이트가 `not_callable_by_llm` 으로 거부해 "이번 발화에서는 새로 기억한 것이 없어요." 라는 엉뚱한 답이 났다(trace 368). 이 패키지는 P5-loop 루프(인식 → 게이트 → 해석 → 기록 → 응답)를 **바꾸지 않고 분기를 하나 더한다**: 인식 단계가 같은 LLM 1회 구조화 출력에 `intent`("record"/"query")를 함께 내고(D16 결정 1), 게이트가 조회 턴의 기록 툴 제안을 코드로 거부하며(결정 1), 조회 턴은 언급을 **같은 ER 4단계**로 해석한 뒤(결정 2·3) 그 인물의 카드(`get_person_card()`)를 코드로 읽어(결정 4) LLM 이 그 근거만으로 1~3줄 답을 쓰고, R19 금지 표현 검증기를 통과하지 못하면 서버가 만든 템플릿 답으로 대체한다(결정 5). 조회 턴은 저장 0 이고(결정 1·6), 답은 기록된 사실의 재진술로 한정한다(결정 8, CLAUDE.md 원칙7 경계 문장 "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다"). 새 툴·새 API·새 스키마·프론트 변경은 없다(결정 10, S3.1·S3.2 무변경).

## 범위

- 포함:
  - **인식 단계 확장**(`app/agent/propose.py`) — `PROPOSAL_SCHEMA` 최상위에 `intent` enum `["record","query"]` 1필드(결정 A). `PROPOSAL_ARG_SCHEMA`·`tool_calls[]` 원소 스키마는 그대로다(D16 "코드에서 지켜야 할 것" 1). 프롬프트에 의도 분류 지시 · 조회일 때 언급을 어떻게 내는지(결정 B) · "나"·"저" 등 사용자 자신 지칭을 인물로 내지 말라는 지시(D16 결정 7 — 프롬프트 지시뿐, 코드 필터 없음). `validate_proposal()` 이 `intent` 를 읽어 `Proposal.intent` 에 싣는다. `FakeProposer` 가 발화별 `intent` 를 줄 수 있게 선택 필드 하나.
  - **게이트 확장**(`app/agent/gate.py`) — `proposal.intent == "query"` 면 기록 툴 4종(`add_event`·`add_schedule`·`update_person`·`create_person`) 제안을 새 거부 사유 1개로 거부(결정 B). `search_person`·`ask_user`·`get_briefing` 의 `not_callable_by_llm` 은 그대로(D16 "코드에서 지켜야 할 것" 2). `check()` 시그니처·순수 함수 성질은 그대로.
  - **루프 조회 분기**(`app/agent/loop.py`) — `run_turn()` 이 게이트 뒤 `intent == "query"` 면 조회 분기로 간다: 언급마다 `app.er.resolve()`(결정 J 상한까지) → band 별 처리(merge = 그 인물 확정, identity = `apply_resolution()` 으로 되묻기·턴 종료, new_person = 되묻지 않고 "기록이 없어요" — D16 결정 3; merge·new_person 에서는 `apply_resolution()` 을 **부르지 않는다** — 결정 I (a) 확정) → `get_person_card()` 를 **코드로** 1회(결정 L) → 근거 조립(결정 D) → 답 생성(U3) → `loop_query` trace(결정 C) → `loop_turn`. `_record()`·`after_record()`(승격 훅)는 부르지 않는다(저장 0).
  - **재개 확장**(`app/agent/loop.py::resume_turn`·`app/agent/types.py::PendingResume`) — 조회 턴의 identity 질문은 `context["resume"]["intent"] = "query"` 를 싣고(S3.4 끝 줄 "재개 재료(`PendingResume`)에 `intent`("record"/"query") 1필드가 더해져 답 뒤 재개가 조회로 이어진다"), `resume_turn()` 이 그 값을 보면 기록 재개 대신 조회 재개로 간다(결정 G).
  - **응답 확장**(`app/agent/respond.py`) — 조회 답 생성기(LLM, 구조화 출력 1회)·답 검증기(R19 금지 표현 목록 재사용 + 줄 수·길이)·템플릿 답·"기록이 없어요" 문구(결정 E). 기존 `build_reply()` 는 손대지 않는다.
  - **설정 상수**(`app/settings.py`) — `QUERY_TIMELINE_LIMIT` 등(결정 D·E·J). 위임 범위 목록(`app/agent/{propose,gate,loop,respond,types}.py`)에는 없지만 U1 권장 분할이 "settings 상수"를 들었고 P5-loop 상수(`LOOP_MAX_*`)가 이 파일에 있으므로 같은 자리에 둔다 — **상수 추가만**, 기존 상수 무수정. `app/agent/__init__.py` 재export 추가도 포함.
  - **테스트** — 새 파일 5개(산출물 절). **기존 테스트 파일은 고치지 않는다**(기존 1958 건 무수정 통과가 회귀 그물 — 새 테스트를 기존 파일에 끼워 넣지 않으므로 "무수정"이 `git diff` 로 증명된다, 판정 표 R-1행).
  - **문서** — `registry.md` 행(새 테스트 5)·비고 확장(고친 기존 모듈 6), `packages/P5b-query-turn/tests.md`(테스트 1건 = 1줄, 사용자 규칙), `03-log.md`(활성화 뒤), `docs/RUNNING.md` 에 조회 발화 예시 한 줄(기존 절에 이어 붙임).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **`app/er/*` 수정**(ER 4단계·두 임계치·확신도 결합) — D16 결정 2 "확신도·임계치를 조회를 위해 낮추지 않는다". P4b 게이트 수치가 나온 코드이므로 호출자로만 붙는다(P5-loop 와 같은 이유, 원칙8).
  - **`app/tools/*` 수정·새 툴** — D16 "`app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로(`scripts/tools_check.py` 7/7)". 조회는 툴이 아니라 루프가 코드로 부르는 읽기 함수다(S3.2 무변경).
  - **`app/api/*` 수정**(라우트·스키마·deps·`read.py`) — 위임 지시 "`app/api/*`·`alembic/`·`web/`(diff 0)". 답 생성기 주입을 라우트 의존성으로 하지 않는 이유는 결정 K, `get_person_card` 를 옮기지 않는 이유는 결정 L. `ChatOut`/`AnswerOut` 은 기존 `reply`·`stored`·`pending_question` 그대로 쓴다.
  - **`alembic/`·`app/db/*`** — S3.1 무변경(D16 파급 "S3.1 스키마·S3.2 툴 7종 시그니처 무변경"). `intent` 는 새 컬럼이 아니라 `pending_questions.context`(JSONB) 안의 키다.
  - **`web/` 수정** — D16 결정 10 "프론트 변경 0". "인물 카드 보기" 링크가 조회 턴에 붙지 않는 문제는 결정 F 에서 다룬다.
  - **`app/briefing/*` 수정** — 검증기는 import 해서 재사용(수정 0). `validate_briefing()` 은 `BriefingInput`·`ComposedBriefing`(브리핑 전용 모양)을 받으므로 조회 답에 그대로 쓸 수 없고, 금지 표현 검사는 `compose.py` 안에서도 `any(bad in text for bad in BRIEFING_FORBIDDEN_EXPRESSIONS)` 한 줄(589·626행)이라 공용 함수가 없다 — **목록(`app/briefing/types.py::BRIEFING_FORBIDDEN_EXPRESSIONS`)과 사유 상수(`compose.py::REASON_FORBIDDEN_EXPRESSION`)만 import** 하는 것이 결정 E 의 추천이다. 검증기 함수를 공용 모듈로 옮기는 것은 `app/briefing/` 수정이 되므로 결정 E 의 다른 후보로만 둔다.
  - **기존 기록 경로 동작 변경** — `intent` 가 없거나 `"record"` 인 턴은 지금과 한 글자도 다르게 돌지 않는다(`Proposal.intent` 기본값 `"record"`, 게이트 새 검사는 `"query"` 에서만). 근거는 기존 테스트 1958 건 무수정 통과.
  - **혼합 발화의 기록**(D16 결정 6) — `intent == "query"` 면 그 턴은 기록 0. 혼합 발화 기록 누락은 P10 표본으로 관찰 뒤 재결정.
  - **인물 간(A–B) 관계 서술·고민 상담·조언·평가**(원칙7, D16 결정 8) — 조회 답은 한 인물 카드의 재진술뿐(결정 J 가 한 턴 한 인물을 추천하는 이유 중 하나).
  - **작업 메모리(최근 N턴, S3.5)** — CR-004 §1 표 4행 "바꾸지 않는다 — 조회 답의 근거는 영구 메모리(카드)".
  - **의도 오분류율 측정** — D16 파급 "P10 평가 표본에 조회 발화 케이스(의도 오분류율) 추가". 이 패키지는 측정 대상(trace)을 만들 뿐 지표를 내지 않는다.
  - **인식 단계 토큰 기록** — 지금 `Proposer` 3종은 사용량을 돌려주지 않아 `loop_extract` 행의 토큰이 0 이다(기존 동작). 조회 답 생성기의 토큰은 남기지만(`loop_query`, 결정 C), 인식 단계 토큰을 고치는 것은 기존 기록 경로 변경이라 범위 밖(리스크 절).

## 산출물 (파일 경로)

**새로 만드는 파일**

- `tests/test_agent_query_types.py` — U1: `Proposal.intent`·`PendingResume.intent` 직렬화·스키마 enum·상수
- `tests/test_agent_query_gate.py` — U2: 조회 턴 거부 사유·기록 툴 집합·프롬프트 지시 문장
- `tests/test_agent_query_answer.py` — U3: 답 생성기 프롬프트·검증기·템플릿·Fake·공급자 오류 매핑
- `tests/test_agent_query_loop.py` — U4·U5: 조회 분기(run_turn)·재개(resume_turn)·저장 0 단언
- `tests/test_api_chat_query.py` — U6: `POST /chat`·`POST /answers/{id}` 끝에서 끝
- `docs/wiki/packages/P5b-query-turn/tests.md` — 테스트 1건 = 1줄(사용자 규칙, P8b 형식)
- `docs/wiki/packages/P5b-query-turn/evidence/` — 단위별 `*-u<n>-*.txt`

**고치는 기존 파일** (아래 각주가 허용 근거)

- `app/agent/types.py` — `Proposal.intent`·`PendingResume.intent`·`STEP_LOOP_QUERY`·`INTENT_*` 상수
- `app/agent/propose.py` — `PROPOSAL_SCHEMA["properties"]["intent"]`·프롬프트·`validate_proposal`·`FakeProposer.intents`
- `app/agent/gate.py` — `REASON_QUERY_TURN_NO_WRITE`(이름은 결정 B)·`WRITE_TOOLS`·`check()` 안 검사 1개
- `app/agent/loop.py` — 조회 분기(`run_turn` 안 분기 1곳 + 새 비공개 함수)·`resume_turn` 분기 1곳
- `app/agent/respond.py` — 조회 답 생성기 Protocol·공급자·Fake·검증기·템플릿(결정 E·K)
- `app/agent/__init__.py` — 재export
- `app/settings.py` — 조회 상수(추가만)
- `docs/wiki/registry.md` · `docs/RUNNING.md`

> **`app/` 허용 파일은 위 7개뿐이다.** `app/er/`·`app/tools/`·`app/api/`·`app/db/`·`app/briefing/`·`app/memory/`·`app/main.py`·`alembic/`·`web/` 는 `git diff --stat 8a8767b..HEAD -- <경로>` 가 빈 출력이어야 한다(판정 표 R-2행). 근거: D16 "코드에서 지켜야 할 것" 3·7, 위임 지시 "바꾸지 않는 것". `verify-plan.sh` 7번(registry 중복)은 위 기존 파일들이 P5-loop 행으로 등록돼 있어 **WARN 을 낼 것이 예상된다** — 새 구현이 아니라 기존 모듈 확장이므로 registry 는 새 행이 아니라 **비고 확장**으로 처리한다(P5-loop U8 과 같은 선례, F-0ffff5).

## 기존 산출물 재사용 (registry 행 번호 — 중복 구현 금지)

| registry 행 | 무엇 | 이 패키지에서 |
|---|---|---|
| 164 `app/agent/types.py`(P5-loop `3e4db92`) | `Proposal`·`PendingResume`·`TurnResult`·step 어휘 6종(`LOOP_TRACE_STEPS`) | 필드 1개씩 추가. **`LOOP_TRACE_STEPS` 튜플에는 넣지 않는다** — `tests/test_agent_types.py` 56~65행이 "정확히 6종"을 단언한다(기존 테스트 무수정 조건). `STEP_LOOP_ERROR` 와 같이 튜플 밖 상수로 둔다 |
| 165 `app/agent/__init__.py` | 재export | 새 이름 재export 만 |
| 166 `app/agent/propose.py`(`069bdc2`) | `PROPOSAL_SCHEMA`(168~186행, 최상위 `tool_calls` 하나 + `additionalProperties: False`)·`build_propose_prompt()`(223행)·`validate_proposal()`(299행)·공급자 3종 `ClaudeProposer.propose`(373)·`OpenAIProposer.propose`(426)·`GeminiProposer.propose`(501)·`FakeProposer`(559) | 스키마에 키 1개, 프롬프트 문장 추가, 파싱 1곳. 공급자 3종은 `PROPOSAL_SCHEMA` 를 그대로 넘기므로 **코드 무수정**으로 새 필드를 받는다 |
| 167 `app/agent/gate.py`(`8ecf75c`) | `check(proposal, *, config)`(272행)·`REASON_*`(99~104행)·`GATE_REJECTION_REASONS`(107)·`NOT_CALLABLE_BY_LLM`(125)·`GateConfig`(152) | 사유 1개·집합 1개·검사 1줄. `tests/test_agent_gate.py::test_all_rejection_reasons_are_in_vocabulary`(397행)는 `issubset` 과 "그 7개 제안의 사유 집합" 을 보므로 어휘 튜플이 7개가 돼도 깨지지 않는다 |
| 168 `app/agent/loop.py`(`7a2ec5c`…) | `resolve_mentions`(592)·`_propose`(655)·`_gate`(668)·`_record_impl`(862)·`_record`(975)·`run_turn`(1051)·`_log_turn`(1149)·`resume_turn`(1329)·`_extend_identity_payload`(435)·`_extend_for_ask`(468) | `resolve_mentions()` 는 **재사용하지 않는다** — 그 함수는 merge 에서 `apply_resolution()`(별칭 누적 = `update_person` `tool_call`)을, new_person 에서 질문 생성을 하므로 조회 턴의 "저장 0"·③-2 와 맞지 않는다(결정 I). 대신 `app.er.resolve` 를 직접 부르고, identity 경로만 기존 `_extend_identity_payload` 모양을 재사용한다 |
| 169 `app/agent/respond.py`(`1835355`) | `build_reply()`(39행, 기록 턴 템플릿) | 무수정. 조회 답 함수들을 옆에 더한다 |
| 191 `app/briefing/types.py`(P6-briefing `e2155f9`·`a2f032d`) | `BRIEFING_FORBIDDEN_EXPRESSIONS`(242행, 14개) | import 만 |
| 196 `app/briefing/compose.py`(P6-briefing `a2f032d`) | `REASON_FORBIDDEN_EXPRESSION`(428)·`REASON_TOO_LONG`(427)·공급자 구현 관례(`ClaudeBriefingComposer` 707행 — `usage` 에서 토큰 회수)·`template_briefing()` 폴백 관례 | 상수 import, 공급자 구현은 **모양만 따른다**(새 Protocol 이므로 클래스는 새로 쓴다 — 결정 K) |
| 222 `app/api/read.py`(P8 U1 `6c2d0e7`, P8b U0 `adc650e`) | `get_person_card(session, user_id, person_id, now) -> PersonCardOut`(182행) · `TIMELINE_LIMIT=20`(54)·`UPCOMING_SCHEDULES_LIMIT=10`(58) · `@traced` 없음 · `raw_utterance` 컬럼 자체를 고르지 않음(229행) | 루프가 코드로 1회 호출(결정 L). 응답 모양 `PersonCardOut`(`app/api/schemas.py` 359~368행: `person{id,display_name,relation_tag,hierarchy}`·`aliases`·`last_contact_at`·`facts[{id,key,value,updated_at,source_count}]`·`patterns[{id,key,value,source_count}]`·`timeline[{id,type,content,occurred_at}]`·`upcoming_schedules[{id,title,scheduled_at,briefed_at}]`) |
| 70 `scripts/tools_check.py` | 툴 7종 시그니처 대조 | 판정만(`7/7 ok`) |
| 173 `tests/test_agent_gate.py` · 174 `test_agent_loop.py` · 175 `test_api_chat.py` · 176 `test_api_answers_resume.py` | 픽스처·헬퍼 관례 | 새 파일이 같은 관례를 따른다: `tests/conftest.py::db_session`(119행, 롤백 세션)·`fake_embedder`(148행) · `test_agent_gate.py::_spy(monkeypatch, name)`(68행, `app.tools.<name>` 스파이) · `test_agent_loop.py::_ctx(db_session, *, session_id, embedder=None)`(60행) · `test_api_chat.py::app_and_client`(84행, `dependency_overrides[get_session]`·`[get_embedder]`) + `dependency_overrides[get_proposer]` = `FakeProposer(table=…)`·`[get_judge]` = `FakeJudge(table={person_id: s_llm})`(`app/er/judge.py`) |

## 작업 단위 (단위 하나 = 커밋 하나. 끝나면 `/commit`)

공통 — 모든 단위의 판정 명령(단위마다 실행, `save_evidence.py` 로 출력 전체 저장 — FIX-034, Write 로 옮겨 적지 않는다):
`POSTGRES_PORT=5433 python3 .claude/scripts/save_evidence.py P5b-query-turn u<n>-<파일> -- .venv/bin/python -m pytest tests/<그 단위 새 파일> -v`(환경변수는 **wrapper 앞**에 — `env …` 접두는 `safety-guard` 가 막는다, P8b 04-review 메모) · `… u<n>-pytest-all -- .venv/bin/python -m pytest tests/ -q -rs`(기대: 1958 + 그 단위까지의 신규 전부 통과, 실패 0·skip 0) · **`-k` 식으로 돌린 판정은 수집 0건(pytest exit 5)이면 실패로 본다**(R-4 — 테스트 이름이 판정 표의 `-k` 토큰을 포함해야 한다) · **임시 파일·변이 스크립트는 스크래치패드 리터럴 절대 경로**(`/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/<세션>/scratchpad/u<n>/`, FIX-033 (d), R-5) · `… u<n>-ruff -- .venv/bin/ruff check app tests`(기대 `All checks passed!`) · `… u<n>-tools-check -- .venv/bin/python scripts/tools_check.py`(기대 `7/7 ok`). 증거는 `docs/wiki/packages/P5b-query-turn/evidence/<ts>-u<n>-*.txt`. 단위마다 `tests.md` 에 새 테스트 1건 = 1줄을 더한다. 구현 보고에는 아래 각 단위의 "변이 → 잡는 테스트" 표를 실제 실행 결과로 채운다(FIX-033 (a) — 저장소를 고쳐 변이를 돌렸다면 원복 후 `git diff` 로 원복을 보인다). **계획에 없는 상수·정렬·상한·문구·방어 조건이 필요하면 구현하기 전에 멈추고 후보와 이유를 보고한다**(FIX-033 (b)).

모든 단위에 걸리는 구현 제약(P5-loop 판정 표 5a·5b·6·9·15·23행 grep 이 `app/agent/` 전체를 보므로 새 코드도 지켜야 한다 — 판정 표 R-4행):
(1) 소스·주석·docstring 어디에도 `create_person` 이나 `update_person` 바로 뒤에 여는 괄호를 붙인 표기를 새로 쓰지 않는다(5a 는 `create_person(` 정확히 1줄, 5b 는 허용 두 곳뿐). (2) 영어 어휘 `confidence`·`T_merge`·`t_merge`·`T_new`·`t_new` 를 쓰지 않는다 — 설명은 한국어 "확신도"(6행). (3) `time.sleep`·`asyncio.sleep`·`while True` 금지(9행). (4) `PendingQuestion`·`flag_modified`·`.context =` 금지(23행) — 질문 행은 `apply_resolution()` → `ask_user` 로만 생긴다. (5) 프롬프트·trace·응답에 키 문자열 0(15행, security §1).

- [ ] U1 **[backend-agent] 계약 — `intent` 필드·스키마·재개 재료·trace 어휘·상수 (도는 분기는 아직 없다)** / Refs: P5b-query-turn CR-004 D16 S3.4 원칙1 원칙4 원칙7 원칙9 R19
  - `app/agent/types.py`: `INTENT_RECORD = "record"`·`INTENT_QUERY = "query"`·`INTENTS = (INTENT_RECORD, INTENT_QUERY)`. `Proposal.intent: str = INTENT_RECORD`(frozen 필드 추가, `to_dict()` 에 `"intent"` 키를 **항상** 싣는다 — `loop_extract.output` 으로 의도 분류 결과가 남는다, D16 결정 9). `PendingResume.intent: str = INTENT_RECORD`, `to_dict()` 는 **`"query"` 일 때만** `"intent"` 키를 싣는다(기존 관례 "해당 없는 필드는 `to_dict()` 에 싣지 않는다", 83행 — 기존 저장 context·테스트와 호환, 읽는 쪽은 키가 없으면 `"record"`). `PendingResume.version` 은 결정 G. `STEP_LOOP_QUERY`(이름은 결정 C) — `LOOP_TRACE_STEPS` 튜플 밖.
  - `app/agent/propose.py`: `PROPOSAL_SCHEMA["properties"]["intent"] = {"type": "string", "enum": list(INTENTS)}`, `required` 는 **무변경**(`["tool_calls"]` 그대로 — `intent` 는 선택 키, 키 없음/`null` → `"record"`; H-1 사용자 결정 (a) 2026-10-28, `tests/test_agent_propose.py:89-91` 무수정 유지). `PROPOSAL_ARG_SCHEMA`·`tool_calls` 원소 스키마는 한 글자도 바꾸지 않는다. `validate_proposal()` — 결정 A 의 누락/위반 규칙. `FakeProposer` 에 `intents: dict[str, str] = field(default_factory=dict)` — 표에 있는 발화만 `raw["intent"]` 로 넘긴다(기존 `FakeProposer(table=…)` 호출은 그대로 기록 턴).
  - `app/settings.py`: 결정 D·E·J 가 확정한 상수(이름·값은 확정 칸을 그대로). `app/agent/__init__.py` 재export.
  - 테스트(`tests/test_agent_query_types.py`): `INTENTS == ("record","query")` · `PROPOSAL_SCHEMA` 최상위 키 집합 == `{"tool_calls","intent"}` 이고 `intent.enum == ["record","query"]` · `PROPOSAL_SCHEMA["properties"]["tool_calls"]` 가 `PROPOSAL_ARG_SCHEMA` 를 그대로 품는다(동일 객체 또는 동일 값) · `validate_proposal({"tool_calls": []})` → `intent == "record"` · `{"tool_calls": [], "intent": "query"}` → `"query"` · `"intent": "ask"` → 결정 A 규칙 · `Proposal.to_dict()["intent"]` · `PendingResume(intent="query").to_dict()["intent"] == "query"` 이고 기본값이면 키 없음 · `STEP_LOOP_QUERY not in LOOP_TRACE_STEPS` 이고 `loop_` 접두사 · `FakeProposer(table={u: []}, intents={u: "query"}).propose(u, now).intent == "query"` · 상수 값.
  - 변이 → 잡는 테스트: `Proposal.intent` 기본값을 `"query"` 로 → `test_proposal_default_intent_is_record`·`test_proposal_to_dict_always_has_intent` FAIL(**U1 실측 — R-U1-1**: `validate_proposal` 이 intent 를 항상 명시 전달해 `missing_intent` 테스트는 이 변이를 안 잡고, "기존 기록 턴 테스트 다수 FAIL" 은 게이트가 intent 를 읽는 U2 뒤에야 성립 — U2 에서 M1 재실행) / enum 에서 `"query"` 제거 → `test_schema_intent_enum` FAIL / `PendingResume.to_dict()` 가 `intent` 를 항상 싣게 → `test_pending_resume_default_omits_intent` FAIL / `STEP_LOOP_QUERY` 를 `LOOP_TRACE_STEPS` 에 추가 → 기존 `test_agent_types.py` 64행 FAIL.
- [ ] U2 **[backend-agent] 인식 프롬프트 + 게이트 — 조회 턴 기록 제안 거부** / Refs: P5b-query-turn CR-004 D16 S3.2 원칙1 원칙4 원칙7 원칙9 R19
  - `app/agent/gate.py`: `WRITE_TOOLS = frozenset({"add_event","add_schedule","update_person","create_person"})`, 거부 사유 1개(이름은 결정 B)를 `GATE_REJECTION_REASONS` 에 더한다. `check()` 의 제안별 순서를 **①②Q④③⑤** 로 — ① 화이트리스트 ② `not_callable_by_llm` 다음, ④ 앞에 "Q: `proposal.intent == INTENT_QUERY` 이고 `name ∈ WRITE_TOOLS` → 새 사유" 를 둔다(결정 B 근거: `search_person` 제안은 ② 에서 먼저 걸려 `not_callable_by_llm` 그대로 — D16 "코드에서 지켜야 할 것" 2). 모듈 docstring "적용 순서" 절에 Q 를 더한다. 순수 함수·시그니처 그대로.
  - `app/agent/propose.py::build_propose_prompt()`: (i) 의도 분류 지시 — "발화가 이미 기록된 인물 정보를 묻는 질문이면 intent 를 query, 새 사실·사건·일정을 알려주는 말이면 record. 둘이 섞이면 query"(D16 결정 6 조회 우선). (ii) 조회 턴의 언급 표기 — 결정 B-3 (b) 확정: `propose.py` 231~237행의 기존 "search_person … 절대 제안하지 마라" 문장 **바로 뒤**에 다음 두 문장을 글자 그대로 덧붙인다(기존 문장은 지우지 않는다, R-7): "단, intent 가 query 일 때만 예외로, 물어본 인물마다 search_person 을 그 언급(query)으로 하나씩 제안하라. 이 제안은 실행되지 않고 대상 표시로만 쓰인다." (iii) 사용자 자신 지칭 제외 — "'나'·'저'·'내'·'제' 처럼 말하는 사용자 자신을 가리키는 말은 인물로 제안하지 마라"(D16 결정 7, 프롬프트 지시뿐). 기존 문장은 지우지 않는다(`tests/test_agent_propose.py` 126~131행이 `search_person`·`ask_user`·`get_briefing`·"제안" 포함을 본다).
  - 테스트(`tests/test_agent_query_gate.py`, 전부 `_spy` 류로 `app.tools.*` 호출 0 확인): 조회 턴의 `add_event`/`add_schedule`/`update_person`/`create_person` 각각 → 새 사유(4건) · 조회 턴의 `search_person`·`ask_user`·`get_briefing` → `not_callable_by_llm` 그대로(3건) · 조회 턴의 툴 7종 밖 이름 → `unknown_tool` · 조회 턴의 `update_person(person_id=3)` → 새 사유(Q 가 ④ 보다 먼저 — 순서 고정) · 조회 턴 `accepted == []` 항상 · 기록 턴(`intent` 기본값)에서 같은 제안들 → 기존 판정 그대로(`execute`/`hint_only`) · `WRITE_TOOLS == set(TOOL_NAMES) - NOT_CALLABLE_BY_LLM`(새 툴이 생겨 조용히 빠지는 것 방지) · 프롬프트에 (i)(ii)(iii) 문장이 들어 있다.
  - 변이 → 잡는 테스트: Q 검사 제거 → 조회 턴 기록 툴 4건 FAIL / Q 를 ② 앞으로 → `test_query_turn_search_person_stays_not_callable` FAIL / `WRITE_TOOLS` 에서 `create_person` 제거 → `test_query_turn_rejects_create_person`·집합 등식 FAIL / 조건을 `intent != "record"` 로 → 영향 없음(동등 변이 — 보고에 그렇게 적는다).
- [ ] U3 **[backend-agent] 조회 답 생성기·검증기·템플릿 (`respond.py`, DB·루프 무관한 순수 층)** / Refs: P5b-query-turn CR-004 D16 S3.6 D11 원칙7 원칙9 R19
  - `QueryAnswerer` Protocol(`answer(question, evidence, now) -> QueryAnswer`), `QueryAnswer`(frozen: `text`·`tokens_in`·`tokens_out`·`provider`·`model`, `trace_tokens()`), 구조화 출력 스키마(`{answer: string}` — 결정 E), `build_query_answer_prompt(question, evidence, now) -> (system, user_text)`, 공급자 3종(`ClaudeQueryAnswerer`·`OpenAIQueryAnswerer`·`GeminiQueryAnswerer` — `app/er/judge.py` 의 `select_provider`·`call_with_error_mapping`·`call_with_gemini_error_mapping`·`_to_gemini_schema` import, `app/briefing/compose.py` 707~770행 관례 그대로: 모델 env 이름 공유·`ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES` 재사용·`usage` 에서 토큰 회수)·등록표·`answerer_from_env()`·`FakeQueryAnswerer`(표 기반, `fail` 주입, `call_count`)·`validate_query_answer(text) -> str | None`(사유 또는 통과)·`template_query_answer(evidence, now) -> str`·`no_record_reply(mentions) -> str`·`no_mention_reply() -> str`. 문구·상한·사유 어휘·근거 0건 처리는 결정 E 확정안을 **글자 그대로** 쓴다.
  - 프롬프트(결정 E): system 에 CLAUDE.md 원칙7 조회 구절 원문 "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다 — 평가·조언·감정 대화는 하지 않는다" + "아래 인물 카드 자료만 근거로 쓰고, 자료에 없는 것은 '기록이 없어요'라고 답하라" + 줄 수 상한 + "다른 인물과의 관계는 말하지 마라". user_text 에 질문 발화 원문 1건 + `now`(사용자 시간대) + 결정 D 의 근거. **이벤트 원문(`raw_utterance`)·인물 id·환경변수·키는 넣지 않는다**(카드 응답에 원문 필드가 없다 — `app/api/schemas.py` 307~309행).
  - 테스트(`tests/test_agent_query_answer.py`, 네트워크 0): 검증기 — 금지 표현 14개 각각 포함 → `forbidden_expression`(parametrize) · 줄 수 상한 경계(상한 줄 통과·상한+1 거부) · 글자 상한 경계(상한 통과·상한+1 거부) · 빈 문자열/공백 → 결정 E 사유 · 정상 답 통과 · 템플릿 — 근거 있는 카드·근거 0건 카드·`last_contact_at` 없음 각각의 정확한 문자열(값으로 단언) · 템플릿 출력이 검증기를 통과한다(폴백이 다시 걸리지 않음) · `no_record_reply(["김철수"])` 정확한 문자열 · 프롬프트 — 원칙7 구절 포함·질문 원문 포함·근거 값 포함·시드 원문 문자열(예 `절대노출금지`) 미포함·타임라인 6건 입력에서 5건만(결정 D 상한) · 공급자 3종 오류 매핑(가짜 클라이언트가 timeout/rate_limit 예외 → `JudgeUnavailable` 어휘, `tests/test_briefing_compose.py` 류 관례) · `answerer_from_env()` 가 `LLM_PROVIDER` 를 따른다.
  - 변이 → 잡는 테스트: 금지 표현 검사 제거 → parametrize 14건 FAIL / 글자 상한 `>` 를 `>=` 로 → 경계 통과 케이스 FAIL / 줄 상한 3→4 → 상한+1 거부 케이스 FAIL / 프롬프트에 타임라인을 자르지 않고 전부 → 5건 단언 FAIL / 템플릿 날짜를 UTC 로 → `last_contact` 문자열 단언 FAIL(경계 시각 시드).
- [ ] U4 **[backend-agent] 루프 조회 분기 — `run_turn` (해석 재사용 → 카드 조회 → 답 → trace, 저장 0)** / Refs: P5b-query-turn CR-004 D16 S3.4 D1 D2 D10 원칙1 원칙2 원칙4 원칙7 원칙9 R19
  - `run_turn()` 에 `answerer: QueryAnswerer | None = None` 키워드를 더한다(결정 K — 라우트는 넘기지 않으므로 운영은 지연 해소). 게이트 직후 `if proposal.intent == INTENT_QUERY: return _run_query_turn(...)` 1곳 — 그 아래 기존 코드는 손대지 않는다.
  - `_run_query_turn`: ① 언급 목록(결정 B 의 출처 규칙, 순서 = 제안 인덱스 순, 중복 제거, 상한 결정 J) ② 언급마다 `app.er.resolve(ctx, mention, utterance, None, judge=judge, config=config)` — 결과 band 만 본다(루프는 확신도를 읽지 않는다, 원칙1·2·4): **merge** → 그 `matched_person_id` 로 확정하고 다음 언급은 보지 않는다(결정 J), **`apply_resolution()` 을 부르지 않는다**(결정 I (a) 확정 — 별칭 누적 0, `er_resolve.decision.applied=false` 그대로) · **identity** → `_extend_identity_payload` 와 같은 모양으로 `PendingResume(mention=…, intent="query", pending_calls=[])` 를 얹고 `apply_resolution()`(→ `ask_user`) → 그 질문으로 턴 종료(`TurnResult.pending_question`, `stop_reason="ask_user"`) · **new_person** → `apply_resolution()` 을 부르지 않는다(질문 행 0, D16 결정 3·"코드에서 지켜야 할 것" 5) — "기록 없음" 목록에 넣고 다음 언급으로 ③ 확정된 인물이 있으면 `get_person_card(ctx.session, ctx.user_id, person_id, ctx.now())`(결정 L 방식, `PersonNotFound` 면 "기록 없음"으로) → 근거 조립(결정 D) → 근거 0건 규칙(결정 E) 또는 `answerer.answer(...)` → `validate_query_answer` → 실패·공급자 오류(`JudgeUnavailable`)면 템플릿(결정 E — 예외를 라우트로 올리지 않는다) ④ 확정 인물이 없으면 `no_record_reply` / 언급이 없으면 `no_mention_reply` ⑤ `loop_query` trace 1행(결정 C 스키마, `trace_tokens()` 로 답 생성 토큰) ⑥ `_log_turn`. `TurnResult.stored` 는 전부 0, `trace_ids` = `[loop_extract, loop_gate, loop_query]` id(+ identity 면 그 사이 ER·`ask_user` 행은 기존처럼 따로 남는다).
  - **부르지 않는 것**(부정 테스트 대상): `resolve_mentions`·`_record`·`_record_impl`·`after_record`·`app.tools.add_event/add_schedule/update_person/create_person`.
  - 테스트(`tests/test_agent_query_loop.py`, `FakeProposer(intents=…)`·`FakeJudge`·`fake_embedder`·`FakeQueryAnswerer`, 네트워크 0): 공용 헬퍼 `_counts(db_session, user_id) -> dict`(`persons`·`person_aliases`·`events`·`schedules`·`person_facts`·`fact_sources`·`pending_questions` 행 수)와 `assert_no_writes(before, after)` 를 이 파일에 둔다. 케이스 — (a) 시드 인물 merge: 카드 근거로 답, 저장 0(위 7개 테이블 행 수 불변 — `pending_questions` 포함), 기록 툴 `tool_call` 행 0(`SELECT … WHERE step='tool_call' AND tool_name IN (4종)`), `get_person_card` 스파이 1회, answerer 입력의 타임라인 ≤ 5·사실 전부·일정 전부 / (b) 빈 DB: new_person → 질문 행 0·`ask_user` `tool_call` 0·reply == `no_record_reply([...])` / (c) 후보 2명 동점(identity): `pending_questions` +1, 저장된 `context["resume"]["intent"] == "query"`, `options` = ER 원본 / (d) 금지 표현 답(Fake 가 "힘들어 보여요") → reply == 템플릿, `loop_query.output` 의 폴백 사유 `forbidden_expression` / (e) answerer 가 `JudgeUnavailable("timeout")` → reply == 템플릿, 예외가 `run_turn` 밖으로 안 나감, `loop_error` 행 0 / (f) 근거 0건 인물 → 결정 E 규칙(LLM 호출 0 이면 `FakeQueryAnswerer.call_count == 0`) / (g) 혼합 발화(조회 의도 + `add_event` 제안) → `add_event` 실행 0·게이트 사유가 `loop_gate.output.rejected` 에 / (h) trace 368 재현 — 제안 `search_person(query="박선우 과장님")`·`search_person(query="나")` 가 함께 와도(프롬프트 지시가 새는 경우) 결정 B·J 규칙대로 처리되고 저장 0 / (i) 언급 0개 → `no_mention_reply` / (j) 기록 턴(`intent` 기본값)은 `_run_query_turn` 을 타지 않는다(스파이) / (k) `loop_query.output` 스키마 키 집합이 결정 C 와 같다.
  - 변이 → 잡는 테스트: merge 에서 `apply_resolution()` 호출(결정 I (a) 확정 — 부르지 않는다) → (a) `person_aliases` 행 수·`update_person` `tool_call` 단언 FAIL / new_person 에서 `apply_resolution()` 호출 → (b) 질문 행 0 FAIL / 타임라인 슬라이스 5→6 → (a) ≤5 단언 FAIL / 폴백 분기 제거 → (d)(e) FAIL / 조회 분기 뒤에 `_record` 를 부름 → (g) FAIL.
- [ ] U5 **[backend-agent] 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`resume_turn`)** / Refs: P5b-query-turn CR-004 D16 S3.4 D2 원칙1 원칙7 원칙9 R19
  - `resume_turn()` 에 `answerer=None` 키워드. `_log_resume_entry` 직후 `kind == "identity"` 이고 `resume_raw.get("intent", "record") == "query"` 면 `_resume_query_turn(...)` 으로 가고 끝낸다(기존 identity 기록 재개 코드는 그 아래 그대로). 답이 `candidate_ids` 안 → 그 `person_id` 로 U4 ③~⑥ 을 같은 함수로 재사용(질문 = `context["utterance"]` — ER 이 넣은 원 발화 1건, `PendingResume` 에 새로 담지 않는다). 답이 후보 밖(ER 거절 옵션) → FIX-035 의 new_person 후속 질문을 **내지 않고** `no_record_reply([mention])`(③-2 와 같은 취급). 별칭은 누적하지 않는다(결정 G (a) 확정 — 저장 0, `update_person` 호출 없음). trace 행: `loop_resume`·`loop_query`·`loop_turn`(`loop_resolve_done`/`loop_record` 없음).
  - 테스트(`tests/test_agent_query_loop.py` 이어서): 조회 identity 질문 → 후보 답 → 그 인물 카드로 답·저장 0(결정 G (a) 확정 — `person_aliases` 불변·`update_person` `tool_call` 0) / 거절 답 → 새 질문 0·reply == `no_record_reply` / `intent` 키가 없는 기존 identity context(P5-loop 형식) → 기존 기록 재개 경로 그대로(`update_person` 별칭 누적 1회) — 하위 호환 / `new_person`·`schedule` kind 는 `intent` 를 보지 않는다.
  - 변이 → 잡는 테스트: `resume_raw.get("intent")` 분기 제거 → 조회 재개 테스트가 기록 경로(별칭 누적)로 가서 FAIL / 거절 답에 FIX-035 후속 질문 → 새 질문 0 단언 FAIL / 기본값을 `"query"` 로 → 하위 호환 테스트 FAIL.
- [ ] U6 **[backend-agent] API 끝에서 끝 + 회귀 판정 전부 + 문서** / Refs: P5b-query-turn CR-004 D16 S3.4 원칙8 원칙9 R19
  - `tests/test_api_chat_query.py`(`app_and_client` 와 같은 방식 — 새 파일에 같은 픽스처를 둔다, 기존 파일 import 는 하지 않는다): `POST /chat` 조회 발화 1건 → 200·`reply` 비어 있지 않음·`stored == {0,0,0}`·`pending_question is None`·요청 전후 행 수 불변·`agent_traces` 에 `loop_extract`(output `intent == "query"`)·`loop_gate`(새 사유)·`er_resolve`·`loop_query`·`loop_turn` 각 1 / identity 조회 → `POST /answers/{id}` 1요청으로 답 → 재개 응답 `reply` 에 카드 근거·저장 0·두 번째 답 409(기존 결정 J 그대로) / new_person 조회 → `pending_question is None`·`pending_questions` 행 0 / answerer 주입은 결정 K 방식(라우트 무수정). 
  - 판정 표 전 행 실행 → evidence. `registry.md`: 새 테스트 5개 **행**, 고친 기존 모듈 6개(`types.py`·`propose.py`·`gate.py`·`loop.py`·`respond.py`·`__init__.py`)와 `app/settings.py` 는 **비고에 P5b-query-turn 한 줄 + 커밋 해시**(새 행 아님). `tests.md` 완성. `docs/RUNNING.md` 에 조회 발화 예시 한 줄.
  - 변이 → 잡는 테스트: `run_turn` 조회 분기 진입 조건을 `"Query"` 로 오타 → HTTP 조회 테스트 전부(기록 턴으로 처리돼 `loop_query` 0행) FAIL / `stored` 를 근거 건수로 채움 → `stored == 0` 단언 FAIL.
- [ ] U7 **[사용자·메인 세션] 실 LLM 왕복 1회 (사람 점검)** / Refs: P5b-query-turn CR-004 D16 원칙7 원칙8 R19
  - 결정 H 의 발화 목록을 로컬 서버(`uvicorn app.main:app --port 8000`)에 `curl` 로 보내고(실 공급자 키 — 사용자 셸에서 로드, security §1), 각 응답 전문 + 요청 전후 행 수 + 그 세션의 `agent_traces`(`step, tool_name, output`)를 `evidence/<ts>-u7-real-llm.txt` 로 남긴다. 판정은 결정 H. 코드 변경 없음 — 실패하면 고치지 않고 FIX 후보로 기록한다(원칙8).
- [ ] **04-review [verifier] 완료 검토** — 판정 표 전행 대조, 부정 케이스 직접 실행(조회 턴 기록 0 / 기록 툴 `tool_call` 0 / new_person 질문 행 0 / `search_person` 여전히 `not_callable_by_llm` / 금지 표현 답 → 템플릿 / `web/`·`app/er`·`app/tools`·`app/api`·`alembic` 무변경 / 기존 테스트 파일 무변경), 단위마다 핵심 계약 변이 시험 최소 1개(저장소 밖 사본 또는 런타임 치환), `registry.md` 등록, D16 갱신 이력에 적을 완료 해시 제안. 판정은 verifier 만 한다(L-002) / Refs: P5b-query-turn CR-004 D16 R19

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [ ] [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `intent`(record/query) 필드 + 게이트가 조회 턴의 기록 제안 거부 + 같은 ER 4단계로 해석(identity 되묻기 유지, new_person 은 "기록이 없어요") + `get_person_card` 근거(사실 전부·타임라인 최근 5·일정) LLM 답 + R19 금지 표현 검증기(실패 시 템플릿) (CR-004 · D16) / 의존: P5-loop, P6-briefing(검증기), P8 U1(`get_person_card`) / 수용기준: D16 "코드에서 지켜야 할 것" 전부 · 조회 턴 저장 0(`events`·`schedules`·`person_facts`·`persons` 행 수 불변, 기록 툴 `tool_call` 0) · 툴 7종 불변(`tools_check` 7/7) · 프론트 diff 0 · trace 에 의도·해석·조회 근거 건수·답 · pytest 통과 · 실 LLM 왕복 1회(trace 368 류 질문에 카드 근거 답) — 사용자 승인 2026-10-28

해석(기계 판정 방법, 위 한 줄을 바꾸지 않는다):

  - "**D16 '코드에서 지켜야 할 것' 전부**" → 아래 판정 표 D-1~D-7 행. D16 의 일곱 문장을 **그대로** 행으로 옮겼다.
  - "**조회 턴 저장 0(… 행 수 불변, 기록 툴 `tool_call` 0)**" → 판정 표 A-1행. 수용 기준이 든 4개 테이블에 `person_aliases`·`fact_sources`·`pending_questions`(new_person 경로)를 더해 본다 — 결정 I (a) 확정(merge 에서 별칭 누적 안 함)이므로 **`person_aliases` 도 불변**이다(7개 테이블 전부 행 수 불변 + `assert_no_writes` 류 값 단언).
  - "**툴 7종 불변(`tools_check` 7/7)**" → 판정 표 A-2행.
  - "**프론트 diff 0**" → 판정 표 D-7행.
  - "**trace 에 의도·해석·조회 근거 건수·답**" → 판정 표 A-3행: 의도 = `loop_extract.output.intent`, 해석·근거 건수·답 = `loop_query.output`(결정 C 스키마).
  - "**pytest 통과**" → 판정 표 A-4행(전체 `-q`, 1958 + 신규, 실패 0·skip 0) + ruff A-5행.
  - "**실 LLM 왕복 1회(trace 368 류 질문에 카드 근거 답)**" → 판정 표 H-1행(사람 점검, U7).
  - "**의존: P5-loop, P6-briefing(검증기), P8 U1**" → 이 문서 "의존:" 줄의 세 04-review `결과: 완료`(`verify-plan.sh` 5번이 기계 확인).

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

로컬 컨테이너는 5433. 명령은 전부 `python3 .claude/scripts/save_evidence.py P5b-query-turn <이름> -- <명령>` 으로 감싸 출력 전체를 evidence 에 남긴다(아래 표는 안쪽 명령만 적는다). 한글 출력이 섞인 한 줄 python 에는 `PYTHONUTF8=1`.

| # | 무엇 (출처 문장) | 명령 | 기대 출력 |
|---|------|------|-----------|
| D-1 | D16: "`propose.py` 구조화 출력 스키마에 `intent` enum `["record","query"]` 가 있고, 다른 필드·툴 제안 스키마는 그대로다." | ① `PYTHONUTF8=1 .venv/bin/python -c "from app.agent.propose import PROPOSAL_SCHEMA as S, PROPOSAL_ARG_SCHEMA as A; print(sorted(S['properties'])); print(S['properties']['intent']['enum']); print(S['properties']['tool_calls']['items']['properties']['args'] is A)"` ② `git diff 8a8767b..HEAD -- app/agent/propose.py \| grep -E '^[-+]' \| grep -E 'PROPOSAL_ARG_SCHEMA\|"(person\|type\|content\|occurred_at\|title\|scheduled_at\|display_name\|aliases\|relation_tag\|hierarchy\|new_alias\|facts)"'` ③ `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_types.py -q` | ① `['intent', 'tool_calls']` / `['record', 'query']` / `True` ② **0줄**(인자 스키마 줄의 추가·삭제 없음) ③ 통과 |
| D-2 | D16: "`gate.py` 는 `intent == "query"` 턴의 기록 툴 제안을 거부하고 사유를 `loop_gate` trace 에 남긴다. `search_person`·`ask_user`·`get_briefing` 의 `not_callable_by_llm` 은 그대로다." | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_gate.py tests/test_api_chat_query.py -q -k "query_turn or loop_gate or not_callable"` | 통과 — 기록 툴 4종 → 새 사유(결정 B), 그 사유가 `loop_gate.output.rejected[].reason` 에 있음(HTTP 테스트), 조회 턴 `search_person`·`ask_user`·`get_briefing` → `not_callable_by_llm`, `app.tools.*` 스파이 호출 0 |
| D-3 | D16: "`loop.py` 조회 분기는 `app.er.resolve`/`apply_resolution` 을 재사용하고, `get_person_card` 를 **코드로** 부른다. `app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로(`scripts/tools_check.py` 7/7)." | ① `grep -nE "resolve\(\|apply_resolution\(\|get_person_card" app/agent/loop.py` ② `.venv/bin/python scripts/tools_check.py` ③ `git diff --stat 8a8767b..HEAD -- app/tools/` ④ `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_loop.py -q -k "card_called_once"` | ① 조회 분기 함수 안에 `resolve(`·`apply_resolution(`(**identity 경로에서만** — 결정 I (a); merge·new_person 경로에는 없다)·`get_person_card` 호출이 보인다 ② `7/7 ok` ③ **빈 출력** ④ 통과(스파이 1회) |
| D-4 | D16: "조회 턴에 `add_event`·`add_schedule`·`update_person`·`create_person` `tool_call` trace 0, `events`·`schedules`·`person_facts`·`persons` 행 수 변화 0(`assert_no_writes` 류 단언)." | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_loop.py tests/test_api_chat_query.py -q -k "no_writes"` | 통과 — 조회 턴(merge·new_person·identity·혼합·금지 표현 폴백·공급자 오류 폴백·재개) 각각에서 `assert_no_writes` 통과, 기록 툴 4종 `tool_call` 행 0 |
| D-5 | D16: "`new_person` 구간의 조회 턴은 `pending_questions` 행을 만들지 않는다(③-2). `identity` 구간은 만든다." | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_loop.py tests/test_api_chat_query.py -q -k "new_person_no_question or identity_asks"` | 통과 — new_person: `pending_questions` +0·`ask_user` `tool_call` 0·reply == `no_record_reply` 확정 문구 / identity: +1, `context["resume"]["intent"] == "query"` |
| D-6 | D16: "답 생성 프롬프트에 들어가는 근거는 `get_person_card` 응답에서 온 값뿐이고(발화 원문 + 카드), 타임라인은 최근 5건까지. 답은 R19 검증기를 거치고, 실패 시 템플릿 문자열(프론트 고정 문구가 아니라 서버가 만든 `reply`)." | ① `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_answer.py tests/test_agent_query_loop.py -q -k "prompt or timeline_limit or forbidden or fallback"` ② `grep -nE "BRIEFING_FORBIDDEN_EXPRESSIONS\|REASON_FORBIDDEN_EXPRESSION" app/agent/respond.py` ③ `git diff --stat 8a8767b..HEAD -- app/briefing/` | ① 통과 — 프롬프트에 카드 값·질문 원문만(시드 원문 문자열·다른 인물 이름 0), 타임라인 6건 시드 → 프롬프트 5건, 금지 표현 답 → reply == 템플릿 문자열(서버 생성) ② import 줄이 보인다 ③ **빈 출력** |
| D-7 | D16: "프론트(`web/`) diff 0." | `git diff --stat 8a8767b..HEAD -- web/` | **빈 출력** |
| A-1 | 수용 기준 "조회 턴 저장 0" | D-4 와 같은 명령 + `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_chat_query.py -q -k "stored_zero"` | 통과 — HTTP 응답 `stored == {"persons":0,"events":0,"schedules":0}`, 요청 전후 행 수 불변(결정 I 확정에 따라 `person_aliases` 포함) |
| A-2 | 수용 기준 "툴 7종 불변" | `.venv/bin/python scripts/tools_check.py` | `7/7 ok` |
| A-3 | 수용 기준 "trace 에 의도·해석·조회 근거 건수·답" | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_chat_query.py tests/test_agent_query_loop.py -q -k "trace"` | 통과 — `loop_extract.output.intent == "query"`, `loop_query.output` 키 집합 == 결정 C 확정 스키마, 근거 건수가 시드와 일치, `reply` 가 `loop_turn` 과 같음, 답 생성 토큰이 `tokens_in/out` 에(Fake 가 준 값) |
| A-4 | 수용 기준 "pytest 통과" | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/ -q -rs` | `1958 + 신규` passed, 실패 0·skip 0 |
| A-5 | 린트 | `.venv/bin/ruff check app tests` | `All checks passed!` |
| R-1 | 기존 테스트 무수정(회귀 그물) | `git diff --name-only --diff-filter=M 8a8767b..HEAD -- tests/` | **빈 출력**(바뀐 기존 테스트 파일 0 — 새 파일은 `--diff-filter=A` 로만 나온다) |
| R-2 | 허용 파일 / 무변경 경로 | ① `git diff --name-only 8a8767b..HEAD -- app/` ② `git diff --stat 8a8767b..HEAD -- app/er app/tools app/api app/db app/briefing app/memory app/main.py alembic web` | ① `{app/agent/types.py, propose.py, gate.py, loop.py, respond.py, __init__.py, app/settings.py}` 의 부분집합 ② **빈 출력** |
| R-3 | 스키마 무변경 | `POSTGRES_PORT=5433 .venv/bin/python -m alembic check` | `No new upgrade operations detected.` |
| R-4 | P5-loop 불변식 grep 유지(5a·5b·6·9·23) | ① `grep -rnE -B1 "create_person\(" app/agent/` ② `grep -rnE "update_person\(" app/agent/` ③ `grep -rn "T_merge\|t_merge\|T_new\|t_new\|confidence" app/agent/` ④ `grep -rnE "time\.sleep\|asyncio\.sleep\|while True" app/agent/` ⑤ `grep -rnE "PendingQuestion\|flag_modified\|\.context *=" app/agent/` | ① 1줄(기존 재개 경로) ② 기존 허용 두 곳뿐(새 줄 0) ③④ **0건** ⑤ **기준 `8a8767b` 시점과 같다**(R-U1-2 — 기준에서도 `PendingQuestionOut` 타입명·docstring 으로 19건이 나오므로 "0건" 이 아니라 **동일성**으로 판정; 추가 줄(`git diff 8a8767b -- app/agent \| grep '^+'`)에는 0건) — 각 출력이 `8a8767b` 시점과 같다(`git stash` 없이 비교하려면 04-review 가 `git show 8a8767b:app/agent/loop.py \| grep …` 로 대조) |
| R-5 | 기록 턴 회귀(기존 경로 그대로) | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_propose.py tests/test_agent_types.py -q` | 전부 통과(이 파일들은 R-1 로 무수정) |
| R-6 | 네트워크 0 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_types.py tests/test_agent_query_gate.py tests/test_agent_query_answer.py tests/test_agent_query_loop.py tests/test_api_chat_query.py -q` | 전부 통과, 실 LLM·실 임베딩 0(`FakeProposer`·`FakeJudge`·`fake_embedder`·`FakeQueryAnswerer`) |
| R-7 | 순환 import 없음(결정 L) | `PYTHONUTF8=1 .venv/bin/python -c "import app.agent; import app.api; import app.main; print('ok')"` 와 `… -c "import app.api; import app.agent; print('ok')"` | 둘 다 `ok` |
| R-8 | 원칙7 경계 — 상담성 답 없음 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_agent_query_answer.py tests/test_agent_query_loop.py -q -k "forbidden or no_counseling"` | 통과 — 금지 표현 14개 각각 템플릿 대체, 프롬프트에 원칙7 조회 구절 원문 |
| H-1 | 수용 기준 "실 LLM 왕복 1회"(사람 점검, U7) | 결정 H 의 curl 목록 | 결정 H 의 판정 기준 전부 충족을 사용자가 evidence 로 확인 |

- 증거 경로: `docs/wiki/packages/P5b-query-turn/evidence/`. Docker Desktop 이 꺼져 있거나 키가 없으면 우회하지 않고 사용자에게 명령을 보여 주고 멈춘다(security §6).

## 결정 항목 (구현자가 추측할 자리를 남기지 않는다 — FIX-033 (b). 확정 칸은 사용자가 채운다)

### 결정 A · `intent` 의 위치와 누락·위반 처리

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 최상위 1개 — 추천** | `{"intent": "record"\|"query", "tool_calls": [...]}`. **`required` 는 `["tool_calls"]` 그대로 — `intent` 는 선택 키**(H-1 (a), 기존 테스트 `test_proposal_schema_top_level_requires_tool_calls_only` 무수정). 코드: 키 없음/`null` → `"record"`, 값이 enum 밖 → `JudgeUnavailable("schema")` | D16 결정 6 "한 턴 한 의도" 와 모양이 같다. 게이트가 턴 단위로 판정(Q 검사)하므로 턴 단위 필드가 자연스럽다. 누락 → record 는 기존 `FakeProposer(table=…)`·기존 테스트가 `intent` 없이 도는 것을 그대로 살린다(기존 1958 무수정). 위반 → schema 는 기존 "형식 위반은 인식 단계가 schema 로" 규약(`validate_proposal` docstring) 그대로 |
| (b) 제안마다 `intent` | `tool_calls[i].intent` | 한 턴 안에서 의도가 섞일 수 있어 결정 6 과 어긋나고, D16 "툴 제안 스키마는 그대로" 위반 |
| (a') 최상위 + 위반도 record | enum 밖 값 → `"record"` | 실패를 숨긴다(조회 질문이 기록 턴으로 처리돼 trace 368 증상 재현). 비추천 |

확정: **(a)** — 사용자 2026-10-28

### 결정 B · 게이트 거부 사유 어휘·적용 순서, 그리고 조회 턴의 언급은 어디서 얻나

**B-1 사유 어휘** — 추천 `query_turn_no_write`(상수 `REASON_QUERY_TURN_NO_WRITE`). 후보: `query_turn_no_write` / `read_only_turn` / `query_intent`. 근거: 기존 어휘가 "무엇이 안 되는가"를 말하는 snake_case(`not_callable_by_llm`·`person_id_from_llm`)이고, P10 이 `loop_gate.output.rejected[].reason` 으로 셀 때 뜻이 바로 읽힌다.

**B-2 적용 순서** — 추천 ①②**Q**④③⑤(② 다음, ④ 앞). 근거: (i) `search_person` 은 ② 에서 먼저 걸려 `not_callable_by_llm` 그대로(D16 "코드에서 지켜야 할 것" 2), (ii) 조회 턴의 기록 툴 제안은 인자가 맞든 틀리든 "이 턴에는 쓰지 않는다"가 가장 근본 사유이므로 ③④ 보다 먼저 하나로 멈춘다(기존 "제안 하나마다 딱 하나의 사유에서 멈춘다" 규약). 조회 턴에서 `accepted` 는 항상 빈 목록이 된다(툴 7종 = 호출 불가 3 + 기록 4).

**B-3 조회 턴 언급의 출처** — 기록 턴은 `args["person"]` 에서 언급을 얻는데, 조회 턴에는 실행될 기록 제안이 없다.

| 후보 | 내용 | D16 과의 관계 | 근거·위험 |
|---|---|---|---|
| (a) 새 최상위 필드 `mentions: [str]` | `intent == "query"` 일 때 LLM 이 대상 언급을 따로 낸다 | **D16 "다른 필드·툴 제안 스키마는 그대로다" 문장과 어긋난다** — 채택하면 D16 갱신(메인 세션, 사용자 결정) 필요 | 가장 명시적·프롬프트가 깔끔하다. 스키마 필드 2개 추가 |
| **(b) 기존 제안의 인물 인자를 읽는다 — 추천** | 조회 턴의 `tool_calls[]` 를 인덱스 순으로 훑어 `search_person` 은 `args["query"]`, 그 밖의 툴은 `args["person"]` 의 문자열(앞뒤 공백 제거, 빈 값 제외, 첫 등장 순 중복 제거)을 언급으로 쓴다. **실행은 게이트가 전부 거부한다**(②·Q). 프롬프트 지시(U2 (ii)): "intent 가 query 이면 물어본 인물마다 search_person 을 그 언급(query)으로 하나씩 제안하라 — 실행되지 않고 대상 표시로만 쓰인다" | D16 문장 그대로 성립(스키마는 `intent` 하나만 늘어난다). D16 결정 2 "`search_person` 은 여전히 LLM 이 직접 부르지 못한다(게이트 ② 유지)" 도 그대로 — 제안은 하지만 실행은 안 된다 | trace 368 에서 LLM 이 **이미 스스로** `search_person("박선우 과장님")` 을 냈다 — 모델의 자연스러운 행동을 그대로 받는다. 위험: 기존 system 문장 "search_person … 절대 제안하지 마라" 와 지시가 겹친다 → U2 가 그 문장 뒤에 "단, intent 가 query 일 때만 예외로 대상 표시용 search_person 을 낸다" 를 덧붙인다(기존 문장은 지우지 않음). 언급을 하나도 안 내면 `no_mention_reply`(결정 E)로 끝나고 `loop_query` 에 남아 관찰된다 |
| (c) (a)+(b) | 둘 다 읽고 합친다 | (a) 와 같은 D16 문제 | 출처가 둘이 되어 "이중 출처 금지"(P5-loop 01-plan 80행) 정신과 어긋난다 |

확정: **B-1 `query_turn_no_write` · B-2 ①②Q④③⑤ · B-3 (b)** — 사용자 2026-10-28

### 결정 C · trace step 어휘와 `loop_query.output` 스키마, `stop_reason`

- step: 추천 **`loop_query`** 1종(상수 `STEP_LOOP_QUERY`, `tool_name="agent"`) — 접두사 `loop_` 규약, "한 단계 = 한 행". `LOOP_TRACE_STEPS`(6종)에는 넣지 않는다(기존 테스트 `test_agent_types.py` 64행). 후보: `loop_query` / `loop_query`+`loop_query_answer` 2행(해석·조회와 답 생성을 나눔 — 행이 늘고 한 턴 판정이 두 행 조인이 된다, 비추천).
- 조회 턴 한 턴의 루프 행: `loop_extract` → `loop_gate` → (ER 이 남기는 `er_resolve`·`search_person` `tool_call`, identity 면 `ask_user` `tool_call`) → **`loop_query`** → `loop_turn`. `loop_resolve_done`·`loop_record` 는 남기지 않는다(기록 경로의 행이므로 — 남기면 P10 의 "기록 턴" 집계가 오염된다).
- `loop_query.output` 추천 스키마:
  ```
  {intent: "query",
   mentions: [str],                       # 결정 B-3 규칙으로 뽑은 순서 그대로(상한 적용 전)
   mentions_dropped: int,                 # 결정 J 상한으로 해석하지 않은 수
   resolutions: [{mention, band, person_id|null, er_trace_id, applied: bool, question_id|null}],
   person_id: int|null,                   # 답한 인물(없으면 null)
   evidence_counts: {facts, patterns, timeline, schedules},   # 프롬프트에 실제로 넣은 건수(타임라인은 상한 뒤)
   answer_source: "llm"|"template"|"no_record"|"no_mention"|"ask",
   fallback_reason: null|"forbidden_expression"|"too_long"|"too_many_lines"|"empty"|"answerer_error:<오류 어휘>"|"no_evidence",
   rejected_answer: str|null,             # 검증기에 걸린 LLM 답 원문(R19 한계 분석용, P10)
   reply: str}
  ```
  `tokens_in/out` 은 답 생성기 사용량(`QueryAnswer.trace_tokens()`), LLM 을 부르지 않았으면 0. 카드 전체·근거 값은 싣지 않는다(건수만 — 같은 값은 DB 가 원천, 이중 출처 금지).
- `TurnResult.stop_reason`: 추천 **답한 조회 턴은 `None`**, identity 되묻기는 `"ask_user"`(기존 어휘). 근거: `app/api/schemas.py` 113행 docstring 이 `stop_reason ∈ {"ask_user","limit",None}` 이라 적고 있어, 새 값 `"query"` 를 내면 `app/api` 무변경 조건 아래 그 문서가 틀린 채 남는다. 의도는 trace 로 충분히 구별된다. 후보 (ii) `"query"` — 클라이언트가 구별 가능하지만 API 문서 불일치.

확정: **`loop_query` 1종(6종 튜플 밖) · output 스키마 위 그대로 · 답한 조회 턴 `stop_reason=None`** — 사용자 2026-10-28

### 결정 D · 근거 조립 (프롬프트에 무엇을 넣나)

추천: `get_person_card()` 응답에서 —
- `person.display_name`·`relation_tag`·`hierarchy` · `aliases`(전부 — "누구"를 묻는 답에 쓴다) · `last_contact_at`(사용자 시간대 날짜)
- `facts` **전부**(`key=value`, `updated_at` 날짜) + `patterns` **전부**(`value` 그대로 — 패턴도 `person_facts` 행이므로 D16 "사실 전부"에 포함)
- `timeline` 최근 **`QUERY_TIMELINE_LIMIT = 5`**건(`type`·`content`·`occurred_at` 날짜. 카드가 이미 `occurred_at desc → id desc` 로 최대 20건을 주므로 앞에서 5건 자른다 — 정렬을 새로 정하지 않는다)
- `upcoming_schedules` **전부**(`title`·`scheduled_at`. 카드 상한 `UPCOMING_SCHEDULES_LIMIT = 10` 이 곧 "전부"의 실제 상한 — 새 상한을 두지 않는다)
- 넣지 않는 것: 인물 id·사실 id·이벤트 id(답 문장에 필요 없음, 결정 E (ii) 를 고르면 넣는다) · `source_count` · `briefed_at` · 이벤트 원문 `raw_utterance`(카드에 필드 자체가 없다 — 원칙7·비밀, 사실 근거 원문 엔드포인트 `get_fact_sources()` 도 부르지 않는다) · 다른 인물 정보 · 환경변수·키.
- 상수: `app/settings.py` 에 `QUERY_TIMELINE_LIMIT = 5`(D16 결정 4 ⑥ 값). **환경변수 오버라이드는 두지 않는다**(추천) — 같은 파일의 `LOOP_MAX_*`·`BRIEFING_SUGGESTION_MAX_CHARS` 가 전부 평 상수이고, 이 값은 운영 중 바꿀 설정이 아니라 원칙7·비용 경계다. 후보 (ii) `QUERY_TIMELINE_LIMIT` 환경변수 오버라이드(정수 검증 + 테스트 2건 추가).

확정: **추천안 그대로 — `QUERY_TIMELINE_LIMIT = 5` 평 상수(환경변수 없음), 원문·id 는 넣지 않음** — 사용자 2026-10-28

### 결정 E · 답 프롬프트·검증·폴백 문구

- **E-1 구조화 출력**: 추천 (i) `{answer: string}` 하나(도구 이름 `report_query_answer`). 후보 (ii) `{answer, basis: {fact_ids, event_ids, schedule_ids}}` + 입력에 없는 id → `unknown_basis`(P6 브리핑과 같은 근거 검증) — 지어낸 id 는 잡지만 "있는 사실을 잘못 재진술"은 못 잡고, 관계·마지막 접촉 같은 카드 필드 답은 근거 id 가 없어 빈 basis 를 허용해야 한다. D16 결정 5 는 검증을 "R19 금지 표현 검증기"로 한정했으므로 (i) 로 시작하고 (ii) 는 P10 표본에서 근거 밖 답이 관찰되면 다시 연다.
- **E-2 상한**: `QUERY_ANSWER_MAX_LINES = 3`(D16 결정 5 "1~3줄") · `QUERY_ANSWER_MAX_CHARS = 240`(= 3줄 × `BRIEFING_SUGGESTION_MAX_CHARS` 80 — 새 튜닝값이 아니라 기존 한 줄 상한에서 파생). 줄 = `text.strip().splitlines()` 중 공백 아닌 줄. 비교는 `> 상한` 이면 거부(상한 자체는 통과).
- **E-3 검증기 재사용 방식**: 추천 — `app/briefing/types.py::BRIEFING_FORBIDDEN_EXPRESSIONS` 와 `app/briefing/compose.py::REASON_FORBIDDEN_EXPRESSION`·`REASON_TOO_LONG` 을 **import** 하고, `respond.py::validate_query_answer(text)` 가 `any(bad in text for bad in BRIEFING_FORBIDDEN_EXPRESSIONS)`(compose.py 589·626행과 같은 식)로 검사한다. 사유 어휘: `empty`(공백뿐) · `too_many_lines` · `too_long`(재사용) · `forbidden_expression`(재사용), 검사 순서 empty → 줄 수 → 길이 → 금지 표현. 후보 (ii) 금지 표현 검사 한 줄을 `app/briefing/` 의 공용 함수로 뽑아 양쪽이 부른다 — 중복은 없어지지만 `app/briefing/` 수정(위임 지시 "수정 0" 과 충돌, P6 회귀 범위가 늘어남). 후보 (iii) `validate_briefing()` 그대로 — 입력 타입(`BriefingInput`·`ComposedBriefing`)이 맞지 않아 어댑터를 억지로 만들어야 한다, 비추천.
- **E-4 폴백 규칙**: 검증 실패 또는 답 생성기의 `JudgeUnavailable`(오류 어휘 6종) → 템플릿 답으로 대체하고 `loop_query.fallback_reason` 에 사유(`answerer_error:timeout` 처럼). **예외를 `run_turn` 밖으로 올리지 않는다** — 올리면 라우트가 "지금은 기억하지 못했어요"(결정 G, P5-loop) + 세이브포인트 롤백으로 `loop_query` trace 까지 잃는다. 근거: D16 결정 5 "답이 비지 않는다". `SQLAlchemyError` 는 기존 규약대로 삼키지 않는다.
- **E-5 문구**(서버가 만드는 `reply` — 프론트 고정 문구 아님). 날짜는 `user_timezone()` 기준 `M월 D일`(0 패딩 없음). 추천안:
  - 템플릿 답(근거 있음): `"{display_name} — {relation_tag}·{hierarchy}, 마지막 접촉 {M월 D일}, 알고 있는 것 {n}건. 자세한 건 인물 화면에서 볼 수 있어요."` — `n = len(facts) + len(patterns)`, `last_contact_at` 없으면 `"마지막 접촉 기록 없음"`. 예: `"박선우 과장님 — 직장·동, 마지막 접촉 10월 21일, 알고 있는 것 1건. 자세한 건 인물 화면에서 볼 수 있어요."`(위임 예시의 "인물 카드에서" 를 결정 F 때문에 "인물 화면에서"로 — 링크가 목록 화면 `HREF.persons` 로 가므로)
  - 근거 0건(사실·패턴·타임라인·일정 모두 0): **LLM 을 부르지 않고**(비용 0, 지어낼 재료가 없다) `"{display_name} — {relation_tag}·{hierarchy}로 기억하고 있어요. 그 밖의 기록은 아직 없어요."`, `answer_source="template"`·`fallback_reason="no_evidence"`. 근거: 태그·위계만으로 "관계가 뭐야"는 답할 수 있고, 그 이상은 지어낼 위험뿐이다. 후보 (ii) 근거 0건도 LLM 에 넘긴다.
  - ③-2 "기록이 없어요"(확정 인물 0, new_person 만): 언급 1개 `"\"{mention}\"에 대한 기록이 없어요."`, 여러 개 `"\"{a}\", \"{b}\"에 대한 기록이 없어요."`(첫 등장 순).
  - 언급 0개: `"누구에 대해 물어보셨는지 알아듣지 못했어요. 이름을 넣어 다시 물어봐 주세요."`
  - 결정 J 상한으로 해석하지 않은 언급이 있을 때 답 끝에 붙는 한 줄: `"한 번에 한 사람씩 물어봐 주세요."`
- **E-6 프롬프트 문장**(U3): system = `"너는 사용자가 기록해 둔 한 인물의 정보를 묻는 질문에 답하는 보조 도구다. "` + 원칙7 조회 구절 원문 + `" 아래 인물 카드 자료만 근거로 1~3줄 한국어로 답하고, 자료에 없는 것은 '기록이 없어요'라고 답하라. 추측하거나 새 사실을 만들지 마라. 다른 인물과의 관계는 말하지 마라. 위로·조언·감정 표현을 쓰지 마라. report_query_answer 도구로만 답하라."` — 구현자가 표현을 다듬어야 하면 멈추고 보고한다.

확정: **E-1 (i) · E-2 3줄/240자 · E-3 목록·사유 import · E-4 템플릿 폴백(예외 안 올림) · E-5 문구 원안 5종 · E-6 프롬프트 문장 그대로** — 사용자 2026-10-28

### 결정 F · 조회 답에 "인물 카드 보기" 링크를 어떻게 붙이나 (D16 결정 10 과의 충돌)

사실: `web/src/screens/ChatScreen.tsx` 46~48행 `hasStored(stored) = stored.persons > 0 || stored.events > 0` 일 때만 링크(`NOTICE.personsLink`, 목적지 `HREF.persons` = 인물 **목록** 화면)를 붙인다. 조회 턴은 `stored` 가 전부 0 이므로 **프론트 무변경으로는 링크가 붙지 않는다** — D16 결정 10 "'인물 카드 보기' 링크 재사용" 은 현재 코드로 성립하지 않는다.

| 후보 | 내용 | D16 |
|---|---|---|
| **(a) 링크 없이 문장만 — 추천** | 답·템플릿 끝에 "자세한 건 인물 화면에서 볼 수 있어요." 만 둔다. 사이드바(최근 5명)·인물 화면은 그대로 있다. **붙이는 규칙(H-2 확정 2026-10-28)**: ① 코드가 붙인다(`respond.py`, 상수 `QUERY_MORE_HINT = "자세한 건 인물 화면에서 볼 수 있어요."`) ② E-2 검증(3줄/240자)은 **LLM 답 본문에만** 하고 통과한 뒤 붙인다 — 최종 `reply` 는 최대 4줄(본문 3 + 이 문장 1, 결정 J 줄이 있으면 5) ③ 순서 = 본문 → (결정 J "한 번에 한 사람씩" 줄, 해당 시) → 이 문장, 줄바꿈 `\n` 으로 잇는다 ④ `loop_query.rejected_answer` 는 LLM 원문, `reply` 는 붙인 결과 ⑤ **붙이는 답은 `answer_source == "llm"` 뿐**(양성 조건, R-8) — ③-2 "기록이 없어요"·언급 0 "알아듣지 못했어요"·템플릿 답(근거 있음·근거 0건 둘 다, `answer_source` = `template`/`no_record`/`no_mention`)에는 붙이지 않는다(근거 있는 템플릿 문구 안에는 이미 같은 문장이 있어 중복 금지) | 결정 10 의 "프론트 변경 0" 은 지키고 "링크 재사용" 구절만 성립하지 않는다 → **D16 갱신 이력에 "링크는 붙지 않음 — 프론트 0 우선(P5b 01-plan 결정 F)" 한 줄**(메인 세션, CR 아님 — 결정의 핵심 "프론트 0"을 지키는 쪽의 문구 정정) |
| (b) `stored` 를 근거 건수로 채운다 | 링크가 붙는다 | 거짓 값 — "저장 0" 수용 기준·`stored` 의미 위반. 비추천 |
| (c) 응답에 읽기 전용 `queried_person_id` 필드 + 프론트 1줄(그 인물 카드로 바로 링크) | 가장 좋은 경험 | `app/api/schemas.py`·`web/` 변경 → D16 결정 10 "프론트 0" 위반 → **CR-004 보정 또는 새 CR** 필요 |

확정: **(a) 링크 없이 문장만** — 사용자 2026-10-28 (D16 갱신 이력에 보정 기록됨)

### 결정 G · identity 되묻기 뒤 재개 — 재개 재료와 동작

- 재개 재료: 추천 `PendingResume` 에 **`intent` 1필드만**(S3.4 끝 줄 그대로). 질문 원문은 ER 이 이미 넣은 `context["utterance"]`(1건), 대상은 `context["mention"]`·`context["candidate_ids"]` — 더 담을 것이 없다(결정 J 가 한 턴 한 인물이므로 "남은 언급" 재료가 필요 없다). `pending_calls=[]`·`held_drafts=[]`·`hints={}`.
- `PendingResume.version`: 추천 **`"1"` 유지** — `intent` 는 "해당 없으면 싣지 않는" 선택 필드이고 읽는 쪽 기본값이 `"record"` 라 기존 저장 context 와 양방향 호환. 후보 (ii) `"2"` 로 올림 — 의미는 분명하지만 버전으로 분기하는 코드가 없어 숫자만 바뀐다.
- 후보 답(`candidate_ids` 안): 추천 **(a) 저장 0 — 별칭을 누적하지 않고** 그 인물 카드로 답한다. 근거: 이 재개 턴도 조회 턴이다(D16 결정 1 "조회 턴은 저장 0", 수용 기준 "기록 툴 `tool_call` 0"). 비용: 같은 표기로 다시 물으면 또 되묻는다. 후보 (b) 사용자가 확인한 identity 이므로 기존 기록 재개처럼 `update_person(new_alias=mention)` 1회 — 다음부터 merge 로 바로 답한다, 오병합 위험 없음(사용자 확인). 단 그 턴에 `update_person` `tool_call` 1행·`person_aliases` +1 이 생겨 수용 기준 문장과 어긋나므로 **(b) 를 고르면 수용 기준 해석에 "재개 턴의 확인된 별칭 누적은 예외" 를 명시**해야 한다(backlog 문장은 그대로, 해석만).
- 거절 답(ER 거절 옵션): 추천 FIX-035 후속 new_person 질문을 **내지 않고** `"\"{mention}\"에 대한 기록이 없어요."`(③-2 와 같은 취급 — 조회 턴에서 "새로 기억할까요" 를 묻지 않는다, D16 결정 3).
- trace: `loop_resume`(기존) → `loop_query` → `loop_turn`.

확정: **`intent` 1필드 · version "1" 유지 · 후보 답 (a) 저장 0 · 거절 답은 "기록이 없어요"(후속 질문 없음)** — 사용자 2026-10-28

### 결정 H · 실 LLM 왕복(U7) 발화 목록과 판정

사전 조건: 사용자 로컬 DB 에 "박선우 과장님"(trace 368 당시 인물)과 사실·타임라인이 있는 인물 1명이 있어야 한다 — 없으면 U7 시작 전에 기록 발화로 만들고 그 발화도 evidence 에 남긴다. 이름은 사용자 DB 에 맞춰 바꾼다(아래는 형식).

| # | 발화 | 기대 |
|---|---|---|
| 1 | `박선우 과장님이랑 나는 관계가 뭐야?` (trace 368 원문) | `loop_extract.output.intent == "query"`, 언급에 "나" 없음(있으면 관찰로 기록 — 결정 J 규칙상 답은 여전히 박선우 과장님), 답에 저장된 `relation_tag`·`hierarchy`(직장·동 등), 저장 0 |
| 2 | `○○는 뭐 좋아해?` (사실이 있는 인물) | 답이 카드 `facts` 의 값을 재진술, 카드에 없는 정보 0 |
| 3 | `○○랑 마지막에 언제 봤지?` | 답의 날짜 == 카드 `last_contact_at`(사용자 시간대) |
| 4 | `김철수 생일 언제야?` (DB 에 없는 이름) | `pending_question == null`, `pending_questions` +0, reply == 결정 E ③-2 문구 |
| 5 | `어제 ○○랑 밥 먹었는데 ○○ 생일이 언제였지?` (혼합) | intent query 면 `events` +0(D16 결정 6) — record 로 분류되면 오분류 관찰로 기록(실패 아님, P10 표본) |
| 6 | `○○가 요즘 힘들어 보이는데 어떻게 위로하지?` (상담 유도) | 답에 위로·조언 없음 — LLM 답이 금지 표현에 걸리면 템플릿(`fallback_reason`), 통과한 답이면 사람이 원칙7 위반 여부를 판정 |

판정(전 발화 공통): 답에 카드 밖 정보 0(사람이 `GET /persons/{id}` 응답과 대조) · 요청 전후 `persons`·`person_aliases`·`events`·`schedules`·`person_facts`·`pending_questions` 행 수(4번 외 불변, 4번도 불변) · `loop_query` 행 존재·토큰 > 0(LLM 답인 경우). 1~4 가 기대대로면 통과, 5·6 은 관찰 기록(실패해도 FIX 후보로 남기고 이 패키지 완료를 막지 않는다 — 추천. 후보 (ii) 6 도 통과 조건에 포함).

확정: **발화 6개, 1~4 통과 조건·5~6 관찰** — 사용자 2026-10-28

### 결정 I · 조회 턴의 merge 에서 `apply_resolution()` 을 부르는가 (D16 결정 2 와 "코드에서 지켜야 할 것" 4 의 충돌)

사실: `app/er/pipeline.py::apply_resolution()` 은 `band == "merge"` 면 `update_person(ctx, person_id=…, new_alias=mention)` 로 별칭을 누적한다(383·465행) — 이 호출은 `@traced` 툴이라 **`update_person` `tool_call` 행 1개**를 남기고, 언급 표기가 새것이면 `person_aliases` 행 +1 이다. D16 결정 2 는 "`resolve()` → `apply_resolution()` 으로 해석한다", "코드에서 지켜야 할 것" 4 는 "조회 턴에 … `update_person` … `tool_call` trace 0" — 두 문장을 동시에 글자 그대로 지킬 수 없다.

| 후보 | 내용 | 결과 |
|---|---|---|
| **(a) merge·new_person 은 `resolve()` 만, identity 만 `apply_resolution()` — 추천** | merge 는 `Resolution.matched_person_id` 를 그대로 쓰고 쓰지 않는다. `er_resolve` 행의 `decision.applied` 는 `false` 로 남는다(사실 그대로 — 적용하지 않았다). `loop_query.output.resolutions[].applied` 에도 같은 값 | "저장 0"·"기록 툴 `tool_call` 0"·③-2(new_person 질문 0) 전부 성립. D16 "코드에서 지켜야 할 것" 3 "`app.er.resolve`/`apply_resolution` 을 재사용" 도 성립(identity 경로). **D16 결정 2 문장에 갱신 이력 한 줄**("조회 턴의 merge 는 별칭을 누적하지 않는다 — 저장 0 우선, P5b 01-plan 결정 I") 필요(메인 세션, 사용자 확인) |
| (b) merge 도 `apply_resolution()` | 기록 턴과 같은 해석 동작, 별칭이 학습된다 | `update_person` `tool_call` 1·`person_aliases` +1 가능 → D16 "코드에서 지켜야 할 것" 4 와 수용 기준 "기록 툴 `tool_call` 0" 해석을 "LLM 제안이 아닌 ER 내부 행은 제외"(P5-loop 판정 7행 관례)로 좁혀야 한다 |

확정: **(a) merge·new_person 은 `resolve()` 만, identity 만 `apply_resolution()`** — 사용자 2026-10-28 (D16 결정 2 갱신 이력에 보정 기록됨)

### 결정 J · 한 조회 턴에서 해석하는 언급 수와 답하는 인물 수

- 해석 상한: 추천 기존 `LOOP_MAX_MENTIONS = 5` **재사용**(새 상수 없음) — 넘는 언급은 `resolve()` 하지 않고 `mentions_dropped` 로 센다.
- 답하는 인물 수: 추천 **`QUERY_MAX_PERSONS = 1`**(`app/settings.py`). 처리: 언급을 순서대로 `resolve()` — new_person 은 "기록 없음"에 넣고 계속, **identity 가 먼저 나오면 그 자리에서 되묻고 턴 종료**(결정 C(i) "첫 되묻기에서 턴 종료"와 같은 규칙), **merge 가 나오면 그 인물로 확정하고 남은 언급은 해석하지 않는다**(`mentions_dropped` 에 더하고 답 끝에 결정 E "한 번에 한 사람씩" 한 줄). 근거: ① 여러 인물 카드를 한 프롬프트에 넣으면 LLM 이 둘 사이 관계를 서술할 수 있다 — 인물 간(A–B) 관계는 원칙7 제외 범위, ② 재개 재료가 `intent` 1필드로 끝난다(결정 G, S3.4 끝 줄), ③ 답 길이 1~3줄과 맞다. 후보 (ii) `QUERY_MAX_PERSONS = 2`(두 사람 질문 지원 — 재개 재료에 "남은 언급·확정 인물" 이 더 필요해 S3.4 끝 줄 "intent 1필드" 를 넘는다).
- "나" 가 프롬프트 지시를 새어 언급에 들어온 경우: 코드로 거르지 않는다(D16 결정 7 은 프롬프트 지시). 보통 new_person 이 되어 "기록 없음"으로 넘어가고 다음 언급으로 간다 — 다만 사용자 이름이 인물로 등록돼 있으면 merge 될 수 있다(리스크 절).

확정: **`LOOP_MAX_MENTIONS` 재사용 · `QUERY_MAX_PERSONS = 1`** — 사용자 2026-10-28

### 결정 K · 답 생성기를 어떻게 주입하나 (`app/api` 무변경 제약)

사실: `POST /chat`·`POST /answers` 라우트는 `run_turn(ctx, utterance, proposer=…, judge=…, extractor=…)` 만 넘긴다(`app/api/routes.py` 365행). `app/api` diff 0 이면 라우트가 답 생성기를 넘길 수 없다.

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) `run_turn`/`resume_turn` 에 `answerer=None` 키워드 + 조회 분기에서만 지연 해소(`answerer_from_env()`) — 추천** | 운영: 조회 턴에서만 공급자를 만든다(기록 턴·키 없는 테스트에 영향 0 — `extractor` 의 `_LazyFactExtractor` 관례와 같은 이유). 루프 단위 테스트는 인자로 `FakeQueryAnswerer` 주입. HTTP 테스트는 `monkeypatch.setattr("app.agent.respond.answerer_from_env", lambda env=None: FakeQueryAnswerer(...))`(새 테스트 파일에서만) | `app/api` 무변경. `Proposer` Protocol 무변경(기존 테스트 대역 `_FailingProposer`·`_DbErrorProposer` 영향 0). HTTP 테스트가 의존성 오버라이드 대신 monkeypatch 를 쓰는 비대칭이 생긴다 |
| (b) `Proposer` Protocol 에 `answer_query()` 메서드 추가 | 기존 `get_proposer` 의존성으로 HTTP 테스트 주입 가능 | 인식과 답 생성 책임이 한 객체에 섞이고, Protocol 변경으로 기존 대역 클래스가 구조적으로 미충족이 된다 |
| (c) `app/api/deps.py`·`routes.py` 에 `get_query_answerer` 의존성 추가 | 가장 정석적인 주입 | `app/api` 수정 → 위임 지시 "diff 0" 위반, 사용자 확인 필요 |

확정: **(a) `answerer=None` 키워드 + 지연 해소, HTTP 테스트는 monkeypatch** — 사용자 2026-10-28. **호출 형태(R-1)**: `loop.py` 는 최상단 `from app.agent.respond import answerer_from_env` 로 이름을 묶지 않고, 조회 분기 함수 안에서 `from app.agent import respond as _respond` 뒤 `_respond.answerer_from_env()` 로 **모듈 속성 호출**한다 — `monkeypatch.setattr("app.agent.respond.answerer_from_env", …)` 가 효과를 내는 유일한 형태. 판정: `grep -n "answerer_from_env" app/agent/loop.py` 결과가 그 속성 호출 1곳뿐.

### 결정 L · `get_person_card` 를 루프에서 어떻게 부르나 (순환 import)

사실: `app/api/__init__.py` 14행이 `from app.api.routes import router` 를 하고, `routes.py` 113행이 `from app.agent import LoopError, Proposer, resume_turn, run_turn` 를 한다. 따라서 `app/agent/loop.py` **최상단**에서 `from app.api.read import get_person_card` 를 하면 `import app.agent` 가 먼저 일어나는 경로(예: 테스트가 `from app.agent import run_turn` 부터 import)에서 `app.api` 패키지 초기화 → `routes` → 반쯤 초기화된 `app.agent` 를 import → `ImportError` 가 난다.

| 후보 | 내용 | 근거 |
|---|---|---|
| **(a) 조회 분기 함수 안에서 지연 import — 추천** | `_read_card(ctx, person_id)` 안에 `from app.api.read import get_person_card` 한 줄 + 주석(순환 이유) | `app/api` 무변경, 호출 시점에는 두 패키지가 모두 초기화돼 있다. 판정 표 R-7 이 두 import 순서를 모두 확인 |
| (b) 카드 읽기 콜러블을 주입(`card_reader=`) | 의존 방향이 깔끔하다 | 결국 기본값 해소에 (a) 가 필요하다 — 인자만 하나 는다 |
| (c) `get_person_card` 를 중립 모듈(`app/memory/` 등)로 옮김 | 계층이 바르다 | `app/api/read.py` 수정 → diff 0 위반 |

확정: **(a) 조회 분기 함수 안 지연 import** — 사용자 2026-10-28

## 리스크 · 미결

- **(R-6, 02-plan-verify 1차) 조회 턴의 `loop_gate.rejected` 에 `not_callable_by_llm` 이 의도적으로 쌓인다**(결정 B-3 (b) — LLM 이 대상 표시용 `search_person` 을 내고 게이트가 거부). P10 이 게이트 거부율을 집계할 때는 `loop_extract.output.intent` 로 기록 턴/조회 턴을 나눠 세야 한다 — 조회 턴의 `not_callable_by_llm`·`query_turn_no_write` 는 결함이 아니라 설계다. P10 인계 문장으로 04-review §7 에 옮긴다.

- **의도 오분류**: (가) 질문 → record: 지금(trace 368)과 같은 "새로 기억한 것이 없어요" + 게이트 거부 — 관측: `loop_extract.output.intent == "record"` 인데 `loop_gate.output.rejected` 에 `not_callable_by_llm`(`search_person`)만 있는 턴. (나) 기록 → query: **기록 누락**(더 나쁜 쪽) — 관측: `loop_gate.output.rejected[].reason == query_turn_no_write`(결정 B 확정 어휘) 인 턴 = "LLM 이 기록 툴을 냈는데 의도를 query 로 붙인 턴" 이므로 그 수가 오분류 후보의 상한이다. 둘 다 SQL 한 줄로 셀 수 있게 결정 B·C 를 골랐다. 지표화는 P10(D16 파급).
- **검증기 목록 밖 표현 통과(R19 한계)**: 금지 표현은 14개 부분 문자열뿐 — 돌려 말하면 통과한다(P6-briefing 01-plan 결정 E 한계, review-index R19 "목록 밖 표현은 통과 → P10"). 완화: 프롬프트 지시 + `rejected_answer` 를 trace 에 남겨 P10 표본으로. "근거 밖 정보"(카드에 없는 사실)는 코드로 잡지 못한다(결정 E-1 (ii) 를 고르지 않는 한) — U7 사람 점검과 P10.
- **"나" 제외가 프롬프트 지시뿐**(D16 결정 7): 사용자 본인 이름이 인물로 등록돼 있거나 ER 이 "나" 를 어떤 별칭과 merge 하면 엉뚱한 인물로 답할 수 있다 — `loop_query.output.mentions` 로 관찰, 반복되면 FIX(코드 필터)로 올린다.
- **조회 턴 비용**: 인식 1회 + ER 판정(후보가 규칙 필터를 통과한 언급마다 0~1회) + 답 생성 1회 = **LLM 최소 2회**(기록 턴은 1 + ER). 근거 0건·new_person 만·언급 0개면 답 생성 0회(결정 E). 결정 J 가 해석 언급 수를 줄여 ER 호출 상한도 줄인다.
- **인식 단계 토큰 미기록**: 기존 `Proposer` 는 사용량을 돌려주지 않아 `loop_extract` 행 토큰이 0 이다(P5-loop 부터의 상태). D16 결정 9 "토큰"은 조회 답 생성 토큰으로만 채운다 — 인식 토큰 기록은 기록 경로 공용 변경이라 별도 FIX 후보(범위 밖).
- **`PendingResume.version`**: 결정 G 에서 `"1"` 유지 추천 — 버전 분기 코드가 생기면 다시 본다.
- **D16 문구와 다르게 되는 두 곳**(사용자 결정 필요): 결정 F(링크 재사용 불가 — 프론트 0 우선)·결정 I(merge 별칭 누적 안 함 — 저장 0 우선). 추천안대로면 두 줄을 D16 "갱신 이력"에 남긴다(메인 세션). 반대로 고르면 CR 보정(F (c)) 또는 수용 기준 해석 조정(I (b)).
- **혼합 발화 기록 누락**(D16 결정 6 의 의도된 비용): P10 표본으로 관찰 뒤 재결정.
- **verify-plan 7번 WARN 예상**: 산출물 절의 기존 파일(P5-loop·P6-briefing 등록)이 "registry 에 다른 패키지로 이미 있음" WARN 을 낸다 — 기존 모듈 확장이므로 정상(비고 확장).

## 읽은 카드

- `docs/wiki/decisions/D16-query-turn.md` 전문 — 결정 1~10·"코드에서 지켜야 할 것" 7문장(판정 표 D-1~D-7 에 그대로). 인용: "게이트(`app/agent/gate.py`)는 `intent == "query"` 인 턴에서 기록 툴(`add_event`·`add_schedule`·`update_person`·`create_person`) 제안을 **코드로 거부**한다(새 거부 사유 1개 — 어휘는 P5b 01-plan 이 정한다). 조회 턴은 저장 0 이다." · "`new_person` 구간(아예 모르는 사람)은 **되묻지 않고** \"기록이 없어요\" 로 끝낸다" · "프론트 변경 0 — 답은 기존 `reply` 문자열, \"인물 카드 보기\" 링크 재사용."
- `docs/wiki/changes/CR-004.md` 전문 — §1 표, §2 "수정할 파일 목록(안 A 기준)", §3 열린 결정 ①~⑦(사용자 확정 2026-10-28). 인용: "**되돌릴 커밋 없음** — 현재 루프를 바꾸는 게 아니라 분기를 더한다." · "⑥ 근거 상한 … **5** (브리핑 S3.6 의 줄 수 상한과 맞춤 — 01-plan 에서 상수명·환경변수 확정)"
- `docs/backlog.md` 75행 — 수용 기준 원문(위 절에 글자 그대로).
- `docs/wiki/INDEX.md` 73행 — "`P5b-query-turn` | 채팅 조회 발화 — 의도 분류·ER 재사용·카드 근거 답 (CR-004 · D16) — P8b 뒤 | backend-agent | — (R19 검증기 재사용)".
- `CLAUDE.md` 원칙7 경계 문장 — "**채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다** — 평가·조언·감정 대화는 하지 않는다."
- `docs/wiki/specs/S3.4-ask-user-protocol.md` 14행 — "(CR-004 · D16, 2026-10-28) 조회 발화의 `identity` 되묻기는 같은 프로토콜을 쓰고, 재개 재료(`PendingResume`)에 `intent`("record"/"query") 1필드가 더해져 답 뒤 재개가 조회로 이어진다. `new_person` 구간의 조회 발화는 되묻지 않는다(질문 행 생성 0)."
- `docs/wiki/review-index.md` 27행(R19) — "**CR-004(D16)**: 같은 금지 표현 검증기를 채팅 조회 답에도 재사용(P5b-query-turn)".
- `docs/wiki/packages/P5-loop/01-plan.md` — 1~165행(범위 절 게이트 ①~⑤·적용 순서 ①②④③⑤, 작업 단위 U1~U8, 판정 표 1~28행), 225~284행(결정 A·B·C·D·E·F·G·H·I·J·K·L). 인용: "적용 순서는 ①②④③⑤ 다" · "(i) **권장 — 순차 처리, 첫 되묻기에서 턴 종료**" · "output 스키마: `{accepted:[{index,name,bucket}], rejected:[{index,name,reason}], limits:{…}}`" · 판정 표 5a "일치 **1줄** — `app/agent/loop.py` 의 **재개 경로(`new_person` 답 처리)** 한 곳".
- `docs/wiki/packages/P5-loop/04-review.md` §7(185~197행) — "**오류 규약**: `LoopError`·공급자 오류(`JudgeUnavailable`)·`ToolError` 는 200 + `stored` 전부 0 + `trace_ids=[loop_error id]`" (결정 E-4 가 답 생성기 오류를 라우트로 올리지 않는 이유).
- `docs/wiki/packages/P6-briefing/01-plan.md` 결정 D·E(180~195행) — "**(ii) 프롬프트 지시 + 코드 검증기** … 한계: 금지 표현 목록은 완전하지 않다(돌려 말하면 통과한다)" · "(i) LLM 1회 구조화 출력 + 코드 검증 + 실패 시 템플릿 대체".
- `docs/wiki/packages/P8-frontend/01-plan.md` U1 줄은 열지 않았다 — 같은 내용(`get_person_card` 응답 모양)을 코드 `app/api/read.py` 182~260행과 `app/api/schemas.py` 359~368행에서 직접 확인했다.
- `docs/wiki/registry.md` 62·70·164~176·191·196·222행(위 "기존 산출물 재사용" 표).
- `docs/wiki/verification.md` 3행·79~87행 — "\"확인했습니다 / 완료했습니다\"는 검증이 아니다." · "보고: \"변이 → 기대 → 결과(어떤 테스트가 FAIL)\" 표와 대조군. 변이가 통과하면 테스트 공백이다(소견)."
- `docs/wiki/fixes/FIX-033.md` 18~21행 — "(b) **계획에 없는 상수·정렬·상한·추가 방어 조건이 필요하면 구현하기 전에 멈추고 보고한다**".
- `.claude/skills/devlog/SKILL.md` 시작 절 4~8단계(정합성 점검 8항은 verifier 가 02-plan-verify 에서 판정).
- `.claude/scripts/verify-plan.sh` 전문(태그·Refs·수용 기준 일치·의존·registry 검사 규칙 — 이 문서 형식을 맞추려고).
- `docs/wiki/packages/P8b-persons-grid/tests.md` 1~15행(tests.md 형식).
- 코드(확인 범위만): `app/agent/propose.py` 1~99·100~254·299~345·373~580행 · `app/agent/gate.py` 전문 · `app/agent/loop.py` 1~230·435~690·1030~1180·1329~1530행 · `app/agent/respond.py` 전문 · `app/agent/types.py` 40~188·355~472행 · `app/briefing/compose.py` 1~130·195~270·474~493·700~770행, `FORBIDDEN` grep · `app/briefing/types.py` 242~254행 · `app/api/read.py` 40~80·180~260행 · `app/api/schemas.py` 300~368행, `stop_reason` grep · `app/api/__init__.py` 전문 · `app/api/routes.py` 113행·300~380행 · `app/er/pipeline.py` 160~490행 · `app/tools/context.py` 146~235행(`traced` 의 `trace_tokens()` 규약) · `app/settings.py` 180~204행 · `web/src/screens/ChatScreen.tsx` `hasStored`·`personsLink` grep · `tests/test_agent_types.py` 56~71·120~131행 · `tests/test_agent_gate.py` 397~419행 · `tests/test_agent_propose.py` 126~159행 grep · 테스트 픽스처 이름 grep(`conftest.py`·`test_api_chat.py`·`test_agent_loop.py`·`test_agent_gate.py`).
