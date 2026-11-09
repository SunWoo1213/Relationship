# P2b-person-delete · 계획 (01-plan)

상태: **활성(2026-11-09)** — architect 초안 → 결정 A~K 확정(사용자 2026-11-09, 4건 선택·7건 추천안 위임) → verifier 02-plan-verify `통과`([필수] 0 · [권고] R-1~R-4) | 담당: backend-agent(sonnet, U1~U3) · frontend-agent(sonnet, U4 — 결정 B 가 "포함"일 때만) · 검증 verifier(fable) · 메인 세션(03-log·사람 점검 진행) | 작성: 2026-11-09
태그 — 패키지: P2b-person-delete · 닫는 검증: 없음(INDEX 67행 패키지 표 "—") · 기대는 결정: 없음(새 D 카드 없음 — 결정 항목은 이 계획 안에서 확정) · 구현하는 명세: 없음(근거는 `docs/wiki/security.md` §5 "인물 단위 완전 삭제 API (`DELETE /persons/{id}` → CASCADE)" · 기획서 9장 제3자 개인정보) · 관련 원칙: 원칙5 원칙8 원칙9 (+ CLAUDE.md "툴 7종" 표 불변) · 이어받는 소견: F-4d2507(P1 04-review §7 → P2 04-review 90행 인계)
의존: P2-tools(04-review `결과: 완료`, 2026-09-05 — backlog 36행) — **충족**. 이 패키지는 P5 이후 단계가 아니라 P2 의 보충이지만, 실제로 정리할 JSONB 모양은 P3-er·P5-loop·P5b·P6·P7 이 쓴 것이라 그 패키지들이 전부 완료된 지금(HEAD `f67d8e4`)을 기준으로 한다. P4 게이트는 P4b 통과로 이미 풀려 있다.

- **기준 해시(무변경 diff 기준점) = `f67d8e4`** (dev2 = dev = main, P5b 완료 문서 커밋). `.claude/gitlog.md` 스냅샷(2026-11-09 09:14) 기준 마지막 제품 코드 커밋은 `cf26dce`(P5b fix, `app/agent/`)이고 `fb8841a`·`f67d8e4` 는 문서 커밋뿐이므로 `f67d8e4` 의 제품 코드 = `cf26dce` 의 제품 코드다. 모든 경로의 무변경 diff 를 `f67d8e4` 하나로 잰다.
- 태그 `P2b-person-delete` 커밋은 아직 없다. 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P2-tools F-4d2507` 실행 요청**(이 문서는 Bash 없이 스냅샷과 registry 해시만 근거로 썼다, L-001).
- 기준선: pytest **2136 passed, skip 0**(위임 지시 — P5b 04-review 재실행 값) · mypy `scripts/mypy_check.py --run` **38건**(P5b 04-review 119행 `[ok] 새 오류 없음 (현재 38건, 기준선 38건)`) · Vitest 는 U4 시작 전 같은 명령으로 재어 03-log 에 적는다.

### 코드에서 확인한 사실 (계획의 전제)

1. **FK CASCADE 는 이미 전부 걸려 있다.** `app/db/models.py` — `person_aliases.person_id`(133행)·`person_facts.person_id`(152행)·`events.person_id`(195행)·`schedules.person_id`(212행) → `persons.id ondelete="CASCADE"`, `fact_sources.fact_id`(175행) → `person_facts.id`·`fact_sources.event_id`(178행) → `events.id` 둘 다 CASCADE. 마이그레이션 `alembic/versions/0001_schema_v2.py` 24행 "All 6 foreign keys keep `ondelete="CASCADE"`" · 180~263행 6곳. 메타데이터 테스트 `tests/test_schema_models.py`(registry 52행 "FK 6개 `ondelete=CASCADE`")가 이미 지킨다. → **새 마이그레이션이 필요 없다**(결정 D).
2. `push_subscriptions` 는 `user_id` 단위이고 `persons` 로 가는 FK 가 없다(models.py 247~261행) — 인물 삭제와 무관.
3. **`pending_questions`·`agent_traces` 에는 `person_id` 컬럼도 `user_id` 컬럼도 없다.** 인물 참조는 JSONB 안에만 있고, 그 모양이 한 가지가 아니다(아래 표). 그래서 "`person_id` 키를 지운다" 한 줄로는 정리가 끝나지 않는다 — 이 패키지의 실질 난이도가 여기 있다.

   | 쓰는 곳 | JSONB 위치 | 인물 id 가 들어가는 모양 |
   |---|---|---|
   | `@traced` 툴 trace (`app/tools/context.py` 224~232행) | `agent_traces.input` | 툴 인자 그대로 — `update_person`/`add_event`/`add_schedule`/`get_briefing` 의 `person_id` |
   | 같은 곳 | `agent_traces.output` | `to_jsonable(result)` — `PersonOut.to_dict()` 는 **`"id"`** 키(types.py 43행, `create_person`/`update_person` 반환 최상위), `Candidate.to_dict()` 는 `"person": {"id": …}`(61~63행, `search_person` 반환 배열), `BriefingOut` 도 `"person": {…}`(152~154행), `EventOut`/`ScheduleOut` 은 `"id"`=이벤트/일정 id + `"person_id"`(84~106행) |
   | `tool_error` trace (context.py 196~210행) | `input` | 실패한 툴의 인자(`person_id`) |
   | ER 되묻기 payload (`app/er/pipeline.py` 197~238행) | `pending_questions.context` 및 `ask_user` trace input | `candidate_ids` = **이름→id 사전**(200행), `confidence_breakdown`(안에 `matched_person_id` — 192행) |
   | 재개 재료 (`app/agent/loop.py` 476·490행, 303·310행) | `pending_questions.context["resume"]` | `person_ids` = **언급→id 사전**, `pending_calls` 인자 |
   | ER 판정 (`app/er/judge.py` 142행·523행) | ER trace output | `candidates[].person_id`, `candidate_person_ids` 배열 |
   | 루프 trace (`app/agent/loop.py` 287·1227·1312행 등) | `loop_*` output | `person_id`(merge 가 아니면 `None`) |
   | 브리핑 (`app/briefing/run.py` 148·157·225·262·296행) | `briefing_run`/`briefing_compose`/`briefing_error` | `person_id` + 브리핑 문장(제3자 정보) |
   | 푸시 (`app/push/notifier.py` 241행) | `push_send` output | `person_id` |
   | 메모리 (`app/memory/hooks.py` 131~137행, `types.py` 103·235·311행) | `memory_promote`/`memory_pattern`/`memory_error` | `person_id` |

   - 같은 숫자가 다른 뜻으로도 쓰인다: `EventOut.id`·`schedule_id`·`question_id`·`considered_event_ids` 는 인물 id 와 **값이 겹칠 수 있다**(서로 다른 IDENTITY 시퀀스). 그래서 "텍스트에 그 숫자가 있으면 지운다"는 남의 행까지 지우는 과잉 삭제가 된다(결정 C-3).
   - trace 를 읽는 제품 코드가 두 곳 있다: `app/memory/promote.py` 136행(`output["person_id"]` 로 이전 승격 조회)·`app/api/read.py` 302행(`briefing_compose` 의 `person_id`). 둘 다 **그 인물 자신의** 행만 읽으므로, 인물이 사라진 뒤 그 행이 지워져도 다른 인물의 동작은 바뀌지 않는다.
   - 평가 스크립트 중 trace 를 읽는 것은 `scripts/run_pilot_eval.py` 하나다. 평가 데이터셋(`data/scenarios/*`)과 평가 실행 DB 는 사용자의 운영 데이터와 분리돼 있고, 삭제 API 를 부르지 않는다 — U1 에서 확인해 03-log 에 적는다(원칙8 영향 확인).
4. 소유 확인 helper `app.tools.persons._owned_person(session, person_id, user_id)`(persons.py 417~429행)가 있고, 없음·남의 것 모두 `PersonNotFound` → `app/main.py` 111·184행 공통 404 `{"detail":{"code":"not_found"}}`. `GET /persons/{id}`(routes.py 444~453행)가 이 관례를 쓴다(`get_person_card` → `_owned_person`, registry 227행).
5. 확인 요구용 예외 `ConfirmationRequired(reason)`(types.py 196~209행)와 그 핸들러가 이미 있다 — **422** `{"detail":{"code":"confirmation_required","reason": …}}`(main.py 38·133~139행). `app/main.py` 를 고치지 않고 재사용할 수 있다.
6. 프론트: `web/src/api/client.ts` 45행 `method?: 'GET' | 'POST'` — `DELETE` 가 아직 없다. 인물 카드 화면은 `web/src/screens/PersonCardScreen.tsx`(`CardView` 223행). shadcn `ui/` 에 `dialog`·`alert-dialog` 가 없다(button·card·badge·collapsible·skeleton·tabs·sonner·sheet 8개). **P8b 판정 12행 불변식**: `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx | grep -v "^web/src/components/ui/"` → `AppShell.tsx` **1파일뿐**(라우트 밖 패널 1개, 원칙5). 삭제 확인을 대화상자로 만들면 이 불변식이 깨진다(결정 A·B).
7. HTTP 엔드포인트 중 툴이 아닌 것(`/push/subscriptions`·읽기 API)은 `agent_traces` 를 남기지 않는 선례가 있다(registry 216·225행).

## 목표

기획서 9장 "제3자 개인정보" 대응으로 `docs/wiki/security.md` §5 첫 줄 "인물 단위 완전 삭제 API (`DELETE /persons/{id}` → CASCADE)" 를 구현한다. 이 제품은 사용자가 아닌 제3자(가족·동료·친구)에 대한 기록을 쌓으므로, 사용자가 한 인물을 잊게 하고 싶을 때 그 인물에 대한 별칭·사실·이벤트(원문 포함)·일정이 **한 번에, 남김없이** 지워져야 한다. 테이블 행은 이미 걸린 FK CASCADE 로 지우고, CASCADE 가 닿지 않는 JSONB(`pending_questions.context`, `agent_traces.input/output`) 안의 그 인물 참조를 같은 트랜잭션에서 정리한다. 실수로 지우지 않도록 삭제 전 확인을 요구하고, 남의 인물은 지울 수 없게 한다(존재 여부도 흘리지 않는다). 예: 사용자가 "민수" 카드에서 삭제를 누르고 확인하면 민수의 별칭 3개·사실 4개·이벤트 12건·일정 1건이 사라지고, 민수를 후보로 들고 있던 미답변 질문 "민수/민준 중 한 분이 맞으실까요?" 와 민수 id 가 들어 있던 trace 행이 함께 정리된다. 다른 인물 "민준" 의 데이터는 1바이트도 바뀌지 않는다.

## 범위

- 포함:
  - `DELETE /persons/{person_id}` HTTP 엔드포인트 — 소유 확인(결정 E), 삭제 전 확인(결정 A), 반환(결정 F).
  - 인물 참조 판별 규칙(결정 C-3)과 JSONB 정리(결정 C-1·C-2) — `pending_questions`·`agent_traces`.
  - 테이블 삭제는 기존 FK CASCADE 로(결정 D) — 마이그레이션 0.
  - 테스트: 순수 판별 함수 단위 테스트 · DB 테스트(CASCADE 5종+`fact_sources`·JSONB 정리·다른 인물 불변·과잉 삭제 없음) · HTTP 테스트.
  - (결정 B 가 "포함"일 때) 인물 카드 화면 안의 삭제 버튼 + 같은 화면 안의 인라인 확인 + 삭제 뒤 `#/persons` 이동·인물 목록 재조회.
  - 문서: 이 패키지 `tests.md`(테스트 1건 = 1줄) · `registry.md` 행 · `security.md` §5 구현 표시 한 줄(메인 세션).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **삭제를 툴(8번째)로 만들거나 대화("민수 지워줘")로 삭제** — CLAUDE.md "툴 7종" 표는 고정이고(`scripts/tools_check.py` 7/7), LLM 이 되돌릴 수 없는 삭제를 판단하게 하면 원칙1(오병합 비대칭)과 같은 비대칭이 삭제에도 생긴다. 삭제는 사람이 버튼·API 로만 한다(결정 I).
  - **새 마이그레이션** — FK CASCADE 6개가 이미 있다(사실 1).
  - **인물 간(A–B) 관계 정리** — 저장 자체를 안 한다(원칙7).
  - **사용자(계정) 단위 전체 삭제·`push_subscriptions` 정리** — backlog 항목은 인물 단위다. 구독은 사용자 단위라 무관(사실 2).
  - **삭제 되돌리기(휴지통·소프트 삭제)** — "완전 삭제" 요구와 반대. 확인 단계(결정 A)로 실수를 막는다.
  - **새 화면·새 라우트·대화상자(`Dialog`/`Sheet`/`Drawer`)** — 원칙5, P8b 판정 12행 불변식(사실 6). 확인은 카드 화면 안 인라인으로(결정 A·B).
  - **이름 문자열만 있고 id 가 없는 trace 의 정리**(결정 G 가 (i)일 때) — backlog 수용 기준은 "`person_id` 참조" 다. 남는 것은 리스크 절과 03-log 에 숨기지 않고 적는다.
  - **배포 환경(RDS·CloudFront) 판정** — 사용자 지시 2026-11-09 "배포는 하지 않을게요". DELETE 본문 전달 여부 같은 배포 쪽 확인은 P9 로 넘긴다(리스크 4).
  - **다중 사용자 격리 검증** — security §5 "멀티테넌시 미검증(부록 A)". 인물 소유 확인은 `user_id` 조건으로 하지만, `user_id` 컬럼이 없는 JSONB 테이블은 인물 id(전역 유일 IDENTITY)로만 정리한다.

## 산출물 (파일 경로)

**새로 만드는 파일** (U1 시작 전 `registry.md` grep 으로 이름 중복 없음 확인 — 이 계획 작성 시 `delete`·`person_refs` 행 없음)

- `app/api/delete.py` — 인물 참조 판별 순수 함수(`references_person`, 규칙 상수 `PERSON_REF_RULES`)와 삭제 서비스 `delete_person(session, user_id, person_id, confirm) -> PersonDeleteSummary`(결정 J 추천 위치).
- `tests/test_person_refs.py` — 판별 순수 함수 단위 테스트(DB 없음, U1).
- `tests/test_person_delete.py` — DB 테스트(실 PostgreSQL 롤백, U2).
- `tests/test_api_person_delete.py` — HTTP 테스트(`TestClient` + `dependency_overrides[get_session]`, U3).
- `docs/wiki/packages/P2b-person-delete/tests.md` — 테스트 1건 = 1줄(P8 `tests.md` 표 모양 + 변경 구분 열).
- `docs/wiki/packages/P2b-person-delete/evidence/*.txt` — `save_evidence.py` 산출물.

**고치는 기존 파일**

| 파일 | 고치는 내용 | registry 행 |
|---|---|---|
| `app/api/routes.py` | `DELETE /persons/{person_id}` 라우트 1개(읽기 라우트 444~453행 옆) | 225행 |
| `app/api/schemas.py` | 확인 입력 모델(결정 A-2)·반환 모델 `PersonDeleteOut`(결정 F) | 225행 |
| (B 포함 시) `web/src/api/client.ts` | `method` 타입에 `'DELETE'`, `deletePerson(personId, confirm)` | 246행 |
| (B 포함 시) `web/src/api/types.ts` | `PersonDeleteOut` 타입(U3 응답과 1:1) | 246행 |
| (B 포함 시) `web/src/screens/PersonCardScreen.tsx` | `CardView` 안 삭제 버튼 + 인라인 확인 블록, 성공 시 `notifyPersonsChanged()` + `#/persons` | 246행 |
| (B 포함 시) `web/src/__tests__/card.test.tsx` · `web/e2e/card.spec.ts` | 삭제 흐름 테스트 추가(기존 단언 무수정) | 247·256행 |
| `docs/wiki/registry.md` | 새 행(모듈·엔드포인트·테스트 3) + 위 행 비고 | — |

`app/main.py`·`app/db/models.py`·`alembic/`·`app/tools/`·`app/agent/`·`app/er/`·`app/memory/`·`app/briefing/`·`app/push/` 는 **무변경**.

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 경로 | registry 근거 | 이 패키지에서 |
|---|---|---|---|
| 스키마 v2 모델·FK CASCADE 6 | `app/db/models.py` | 47행 | 그대로. `Person` 한 행 삭제로 5개 테이블+`fact_sources` 가 따라 지워진다 |
| 메타데이터 테스트(FK `ondelete=CASCADE`) | `tests/test_schema_models.py` | 52행 | 판정 J-1 에서 그대로 실행(무수정) |
| 소유 확인 `_owned_person` · `PersonNotFound` | `app/tools/persons.py` 417행 · `app/tools/types.py` 169행 | 59·61행 | 소유 확인을 새로 짜지 않는다 |
| `ConfirmationRequired` + 422 핸들러 | `app/tools/types.py` 196행 · `app/main.py` 133행 | 59행 | 확인 없음·불일치를 이 예외로(결정 A) — `main.py` 무수정 |
| 요청 세션 `get_session`(commit/rollback) · `app_user_id()` | `app/api/deps.py` 120행 · `app/settings.py` | 225행 | 한 요청 = 한 트랜잭션. 중간 실패 시 정리·삭제 전부 되돌아간다 |
| 공통 404 매핑 | `app/main.py` 111·184행 | 79행 | 남의 인물·없는 인물 같은 본문 |
| "쓰기 0" 헬퍼 `snapshot_db`·`assert_no_writes`(9테이블) | `tests/helpers_read_api.py` | 236행 | 확인 없음·남의 인물 요청이 아무것도 바꾸지 않음을 값으로 단언 |
| `TestClient`+`dependency_overrides` 관례 · `app_and_client` | `tests/test_api.py` · `tests/test_api_chat_query.py` | 79·176행 | HTTP 테스트 골격 |
| 실제 trace·질문을 만드는 경로(가짜 공급자) | `run_turn`·`resume_turn`(`FakeProposer`·`FakeJudge`·`fake_embedder`), `run_briefings`(`FakeBriefingComposer`), `after_record`(`FakeFactExtractor`) | 170·179·175행 등 | U2 의 "센티널 id" 테스트가 손으로 만든 JSON 이 아니라 **실제 쓰는 코드**가 남긴 JSONB 를 정리 대상으로 삼게 한다 |
| (B) `PersonsProvider`·`notifyPersonsChanged` | `web/src/components/PersonsProvider.tsx` | 249·255행 | 삭제 뒤 사이드바·그리드 재조회 |
| (B) shadcn `Button`·`Collapsible` | `web/src/components/ui/` | 235행 | 인라인 확인 블록. 새 shadcn 부품 내려받지 않음 |
| (B) E2E `installFakeApi`·`expectNoStrayRequests` | `web/e2e/fixtures.ts` | 256행 | 삭제 흐름 E2E |

## 작업 단위 (단위 하나 = 커밋 하나. 끝나면 `/commit`)

공통: 판정 명령은 저장소 루트에서, 출력은 전부 `python3 .claude/scripts/save_evidence.py P2b-person-delete <이름> -- <명령>`(Windows 는 `python`)으로 `evidence/<ts>-<이름>.txt`. DB 명령은 `POSTGRES_PORT=5433` 를 **wrapper 앞**에 붙인다(`env …` 금지). 위임 프롬프트에 FIX-033 네 규칙을 넣는다: (a) 계약 값(삭제 건수·상태 코드·본문·남는 행)은 값으로 단언하고 "변이 → 잡는 테스트" 표를 보고에 넣는다(아래 표가 최소) (b) **이 계획에 없는 상수·규칙·방어 조건이 필요하면 구현 전에 멈추고 보고**(후보와 이유) (c) 증거는 `save_evidence.py` 출력 전체 (d) 임시 파일·변이 스크립트는 스크래치패드 리터럴 절대 경로. 테스트 1건 = `tests.md` 1줄(단위 커밋에 같이). 각 단위 시작 전 `registry.md` grep, 끝나면 `pytest tests/ -q -rs` 전체 1회로 회귀 0 확인. 위임 프롬프트는 이 계획 원문을 인용하고 임의 제한을 덧붙이지 않는다.

- [ ] U1 인물 참조 판별 규칙(순수 함수) + 쓰는 곳 전수 목록 — [backend-agent] `app/api/delete.py` 에 `PERSON_REF_RULES`(결정 C-3 확정 규칙)와 `references_person(obj, person_id, *, tool_name=None) -> bool`(재귀, DB 없음). **규칙 목록은 이 계획 "사실 3" 표를 출발점으로 하되, 구현자가 `grep -rn "AgentTrace(\|ask_payload\|to_jsonable(" app/` 로 모든 쓰는 곳을 다시 훑어 표에 없는 모양이 나오면 구현 전에 멈추고 보고**(FIX-033 (b)). 전수 목록(쓰는 곳 → JSONB 경로 → 규칙 번호)은 모듈 docstring 과 U1 보고에 남긴다. 함께 확인해 보고할 것: ① `scripts/run_pilot_eval.py` 가 운영 DB 의 trace 를 재료로 쓰지 않는다(원칙8) ② `fact_sources` 가 다른 인물의 사실과 이 인물의 이벤트를 잇는 경로가 있는가(`app/memory/promote.py`·`direct_facts.py`·`patterns.py` 의 `FactSource(` 6곳). 판정: `.venv/bin/python -m pytest tests/test_person_refs.py -v` · 증거 `*-u1-person-refs.txt` · 변이 `*-u1-mutation.txt` / Refs: P2b-person-delete F-4d2507 security§5 원칙9
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트 |
    |---|---|
    | V1-1 `candidate_ids` 사전의 **값** 검사 제거 | identity 질문 context 픽스처(pipeline.py 202행 모양) → True |
    | V1-2 `resume.person_ids` 사전 값 검사 제거 | 재개 재료 픽스처(loop.py 303행 모양) → True |
    | V1-3 `"person": {"id": …}` 경로 제거 | `search_person` 출력 배열·`BriefingOut` 픽스처 → True |
    | V1-4 `create_person`/`update_person` 최상위 `"id"` 규칙 제거 | `PersonOut` 출력 픽스처 + `tool_name="create_person"` → True |
    | V1-5 최상위 `"id"` 를 툴 이름과 무관하게 인물 id 로 봄 | `add_event` 출력(`EventOut.id` == 인물 id 와 같은 숫자, `person_id` 는 다른 인물) → **False**(과잉 판정 금지) |
    | V1-6 텍스트 정규식(`str(obj)` 에 숫자 포함)으로 바꿈 | `considered_event_ids`·`schedule_id`·`question_id` 에만 같은 숫자 → **False** |
    | V1-7 `matched_person_id`·`candidate_person_ids` 검사 제거 | ER breakdown·judge 출력 픽스처 → True |
    | V1-8 `bool`(`True == 1`) 을 정수로 취급 | `{"person_id": True}` 와 인물 id 1 → False |
    | V1-9 문자열 `"12"` 를 12 로 취급 | 결정 C-3 확정대로(추천: 정수만) |
- [ ] U2 삭제 서비스 `delete_person` — [backend-agent] `app/api/delete.py`: ① `_owned_person` 으로 소유 확인(없음·남의 것 `PersonNotFound`) ② 확인 검사(결정 A-2, 불일치 `ConfirmationRequired(reason="person_delete")`, **이 시점까지 쓰기 0**) ③ 삭제 건수 집계(결정 F) ④ `pending_questions` 정리(결정 C-1) ⑤ `agent_traces` 정리(결정 C-2 — 결정 C-3 의 SQL 사전 거름 + U1 함수로 정밀 판정) ⑥ `DELETE FROM persons WHERE id = :pid AND user_id = :uid`(결정 D — FK CASCADE) ⑦ commit 하지 않는다(트랜잭션 경계는 `get_session`, P2 결정 2). trace 를 남기지 않는다(결정 H). DB 테스트(`tests/test_person_delete.py`): **센티널 시나리오** — `persons.id = 987654321`(IDENTITY BY DEFAULT 라 명시 id 삽입 가능)·이름 "삭제대상센티널" 인물과 대조군 인물(id 작은 값)을 만들고, 가짜 공급자로 **실제 경로**를 돌려 JSONB 를 쌓는다: 기록 턴 merge(`add_event`·`add_schedule`), identity 되묻기(두 인물이 후보, 미답변으로 둠) 1건 + 답변된 질문 1건, `update_person` 사실, `run_briefings` 1회, 메모리 승격 1회, 대조군만 나오는 턴 1회. 삭제 뒤 단언: CASCADE 5테이블 + `fact_sources` 의 센티널 행 0 · `pending_questions.context::text`·`agent_traces.input::text`·`output::text` 어디에도 `987654321` 없음(**결정 C-3 이 놓친 모양을 잡는 그물** — 다른 시퀀스가 이 값에 닿지 않으므로 텍스트 검색이 안전하다) · 대조군 인물의 5테이블 행·값 전후 동일, 대조군만 참조하는 trace·질문 행 전후 동일(과잉 삭제 없음) · 결정 C 확정에 따른 남는 행 모양. 판정: `POSTGRES_PORT=5433 … pytest tests/test_person_delete.py -v` · 증거 `*-u2-person-delete.txt` · 변이 `*-u2-mutation.txt` / Refs: P2b-person-delete F-4d2507 security§5 원칙8 원칙9
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트 |
    |---|---|
    | V2-1 `pending_questions` 정리 생략 | 센티널 텍스트 0 (pending_questions) |
    | V2-2 `agent_traces` 정리 생략 / `input` 만 정리 | 센티널 텍스트 0 (traces input·output 각각) |
    | V2-3 정리를 `persons` 삭제 **뒤**로(인물 없음 → 조회 실패로 건너뜀) | 같은 테스트 |
    | V2-4 `user_id` 조건 제거 | 남의 인물 → `PersonNotFound` + `assert_no_writes` |
    | V2-5 확인 검사를 정리 뒤로 | 확인 불일치 → `assert_no_writes`(9테이블 값) |
    | V2-6 JSONB 정리를 텍스트 `LIKE` 결과로 바로 삭제(정밀 판정 생략) | 대조군 trace 중 `EventOut.id`/`schedule_id` 가 987654321 이 아닌 작은 값으로 대조군 인물 id 와 같도록 꾸민 행 — 대조군 삭제 시나리오 쪽에서 과잉 삭제 검출(테스트에 대조군 삭제 케이스 1건 포함) |
    | V2-7 건수 집계를 삭제 뒤에 | 반환 건수 == 시드 건수 |
    | V2-8 `session.commit()` 호출 | 서비스 호출 뒤 바깥 트랜잭션 rollback 시 인물이 되살아남 |
- [ ] U3 HTTP `DELETE /persons/{person_id}` — [backend-agent] `routes.py` 에 라우트 1개(`app_user_id()`·`get_session`), `schemas.py` 에 확인 입력(결정 A-2)·`PersonDeleteOut`(결정 F). `app/main.py` 무수정(404·422 핸들러 재사용). HTTP 테스트(`tests/test_api_person_delete.py`): 확인 없음·불일치 → 422 `{"detail":{"code":"confirmation_required","reason":"person_delete"}}` + `assert_no_writes` · 없는 id 와 남의 인물 → **같은** 404 본문 + `assert_no_writes` · 정상 → 결정 F 모양·값 · 같은 id 재삭제 → 404 · 삭제 뒤 `GET /persons/{id}` 404, `GET /persons` 에 없음 · 응답·로그에 이름·원문 미포함(결정 A-2 가 본문/헤더일 때 쿼리 문자열에 이름이 없음). 판정: `POSTGRES_PORT=5433 … pytest tests/test_api_person_delete.py -v` · 증거 `*-u3-api-person-delete.txt` · 변이 `*-u3-mutation.txt` / Refs: P2b-person-delete F-4d2507 security§5
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트 |
    |---|---|
    | V3-1 남의 인물에 403 | 404 본문 동일성 |
    | V3-2 확인 검사 제거 | 422 + 쓰기 0 |
    | V3-3 반환을 204 로(결정 F 가 200 일 때) | 응답 값 단언 |
    | V3-4 라우트가 `user_id` 대신 헤더 값 사용 | 남의 인물 404 |
- [ ] U4 (결정 B 가 "포함"일 때만) 인물 카드 삭제 버튼 + 인라인 확인 — [frontend-agent, `web/` 만] `client.ts` `deletePerson`·`method` 에 `'DELETE'` · `types.ts` `PersonDeleteOut` · `PersonCardScreen.tsx` `CardView` 끝에 "이 인물 삭제" 버튼 → 누르면 **같은 카드 안에** 확인 블록(결정 A-3 문구, [삭제]/[취소]) → [삭제] 시 `deletePerson(id, 확인값)` → 성공: `notifyPersonsChanged()` + `location.hash = '#/persons'` / 422·404·네트워크 오류: 블록 안에 고정 문구 1줄, 카드 유지. `Dialog`/`Sheet`/`Drawer`/`window.confirm` 금지(사실 6, 원칙5). Vitest(`card.test.tsx`): 버튼만 누르면 DELETE 요청 0 · 확인 후 정확히 1회(메서드·경로·확인값) · 취소 시 0 · 성공 후 해시·목록 재조회 1회 · 실패 문구. E2E(`card.spec.ts`): 카드 → 삭제 → 확인 → 그리드에서 사라짐, `expectNoStrayRequests`. 판정: `npm --prefix web run typecheck` · `npm --prefix web test -- --run` · `npm --prefix web run build` · `npm --prefix web run e2e` · 불변식 grep · 증거 `*-u4-front.txt`·`*-u4-mutation.txt`·`*-u4-invariants.txt` / Refs: P2b-person-delete security§5 원칙5
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트 |
    |---|---|
    | V4-1 버튼 클릭 즉시 DELETE(확인 생략) | "버튼만 누르면 요청 0" |
    | V4-2 취소해도 DELETE | "취소 시 0" |
    | V4-3 성공 후 `notifyPersonsChanged` 누락 | 목록 재조회 1회 |
    | V4-4 확인을 `Sheet` 로 | 불변식 grep(AppShell 1파일) |
    | V4-5 확인값 누락(서버가 422) | 요청 본문/헤더 단언 |
- [ ] U5 자동 판정 전체 + 문서 — [backend-agent: 판정 실행·`tests.md`·`registry.md`] + [메인 세션: `03-log.md`·`security.md` §5 "구현: P2b-person-delete `<해시>`" 한 줄] 아래 판정 표 전부 실행, `tests.md` 행 수 = 이 패키지가 더한 테스트 수. 증거 `*-u5-final-judge.txt` / Refs: P2b-person-delete F-4d2507 security§5 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- `DELETE /persons/{id}` — 인물 단위 완전 삭제 / 의존: P2 / 수용기준: 인물·별칭·사실·이벤트·일정이 FK CASCADE 로 함께 지워지고, `pending_questions.context`·`agent_traces.input/output` JSONB 안의 `person_id` 참조도 정리된다. 삭제 전 확인을 요구하고, 남의 인물은 지울 수 없다 / Refs: F-4d2507 security§5 (P1 04-review §7)

(backlog 38행과 글자 그대로 같다. 39행 부연 — "security.md §5 가 요구하는데 backlog 어느 항목에도 없었다(F-4d2507, P2 04-review 90행이 architect 에게 인계). … **P5 에 끼우지 않는다**" — 에 따라 루프 패키지와 섞지 않고 독립 패키지로 둔다.)

## 해석 — 수용 기준 (새 기준을 더하는 것이 아니다)

| # | 원문 구절 | 이 계획의 해석 → 판정 행 |
|---|---|---|
| ㄱ | 인물·별칭·사실·이벤트·일정이 FK CASCADE 로 함께 지워지고 | `persons` 1행 삭제로 `person_aliases`·`person_facts`·`events`·`schedules` + 그 자식 `fact_sources` 가 DB CASCADE 로 0행. 애플리케이션이 자식 테이블을 따로 지우지 않는다(결정 D) → J-1 |
| ㄴ | `pending_questions.context` … JSONB 안의 `person_id` 참조도 정리된다 | "`person_id` 참조" = 키 이름이 `person_id` 인 것만이 아니라 **그 인물 id 를 가리키는 모든 JSONB 위치**(사실 3 표 — `candidate_ids` 값·`resume.person_ids` 값·`matched_person_id` 등). 정리 방식은 결정 C-1 → J-2 |
| ㄷ | `agent_traces.input/output` JSONB 안의 `person_id` 참조도 정리된다 | 같은 정의, `input`·`output` 둘 다. 정리 방식 결정 C-2, 판별 규칙 결정 C-3 → J-3 |
| ㄹ | 삭제 전 확인을 요구하고 | 서버가 확인 없는 삭제를 거부(결정 A) + (B 포함 시) 화면 확인 → J-4 (+ J-13) |
| ㅁ | 남의 인물은 지울 수 없다 | `persons.user_id = app_user_id()` 조건, 남의 것·없는 것 같은 응답(결정 E), 아무것도 바뀌지 않음 → J-5 |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

아래 "명령" 은 안쪽 명령만 적는다. 실제 실행은 `POSTGRES_PORT=5433 python3 .claude/scripts/save_evidence.py P2b-person-delete <증거 이름> -- <명령>` (DB 를 쓰지 않는 명령은 `POSTGRES_PORT=5433` 생략). 한글 출력이 섞인 한 줄 python 에는 `PYTHONUTF8=1`. Docker Desktop 이 꺼져 있으면 우회하지 않고 사용자에게 명령을 보여 주고 멈춘다(security §6).

| # | 무엇 (출처) | 명령 | 기대 출력 | 증거 이름 |
|---|---|---|---|---|
| J-1 | ㄱ CASCADE 5종 + `fact_sources` | ① `.venv/bin/python -m pytest tests/test_schema_models.py -q -k "cascade or fk"` ② `.venv/bin/python -m pytest tests/test_person_delete.py -q -k cascade` ③ `grep -nE "delete\((PersonAlias\|PersonFact\|Event\|Schedule\|FactSource)\)" app/api/delete.py` | ① 통과(FK 6개 CASCADE, 무수정 테스트) ② 통과 — 센티널 인물의 `persons`·`person_aliases`·`person_facts`·`events`·`schedules`·`fact_sources` 행 0, 대조군 행 수·값 전후 동일 ③ **0줄**(자식 테이블을 앱이 직접 지우지 않음, 결정 D 추천 기준) | `j1-cascade` |
| J-2 | ㄴ `pending_questions.context` 정리 | `.venv/bin/python -m pytest tests/test_person_delete.py -q -k pending_questions` | 통과 — 삭제 뒤 `SELECT count(*) FROM pending_questions WHERE context::text LIKE '%987654321%'` = 0, 결정 C-1 확정대로 남는/지워진 행 수, 대조군만 참조하는 질문 행 전후 동일 | `j2-pending-questions` |
| J-3 | ㄷ `agent_traces.input/output` 정리 | ① `.venv/bin/python -m pytest tests/test_person_delete.py -q -k traces` ② `.venv/bin/python -m pytest tests/test_person_refs.py -q` | ① 통과 — 삭제 뒤 `input::text`·`output::text` 에 `987654321` 0건(실제 경로가 쓴 trace 대상), 결정 C-2 확정대로의 남는 행 모양, 대조군 전용 trace 행 전후 동일(과잉 삭제 0) ② 통과(V1-1~V1-9 표의 양성·음성 픽스처) | `j3-traces` |
| J-4 | ㄹ 삭제 전 확인 | `.venv/bin/python -m pytest tests/test_api_person_delete.py tests/test_person_delete.py -q -k confirm` | 통과 — 확인 없음·불일치 → 422 `{"detail":{"code":"confirmation_required","reason":"person_delete"}}`, `assert_no_writes` 통과(9테이블 값), 맞는 확인 → 삭제 | `j4-confirm` |
| J-5 | ㅁ 남의 인물 | `.venv/bin/python -m pytest tests/test_api_person_delete.py tests/test_person_delete.py -q -k "other_user or not_found"` | 통과 — 남의 인물·없는 id 응답 상태·본문 바이트 동일(결정 E), `assert_no_writes` 통과, 재삭제 404 | `j5-other-user` |
| J-6 | 툴 7종 불변(결정 I) | ① `.venv/bin/python scripts/tools_check.py` ② `git diff --stat f67d8e4..HEAD -- app/tools/ app/agent/` ③ `grep -rn "delete_person" app/agent app/tools app/er` | ① `7/7 ok` ② **빈 출력** ③ **0줄** | `j6-tools` |
| J-7 | 스키마 무변경(결정 D) | ① `.venv/bin/python -m alembic check` ② `git diff --stat f67d8e4..HEAD -- alembic/ app/db/` | ① `No new upgrade operations detected.` ② **빈 출력** | `j7-alembic` |
| J-8 | 전체 회귀 | `.venv/bin/python -m pytest tests/ -q -rs` | `2136 + 신규` passed, 실패 0·**skip 0** | `j8-pytest-all` |
| J-9 | 린트 | `.venv/bin/ruff check app tests` | `All checks passed!` | `j9-ruff` |
| J-10 | 타입 기준선 | `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음` (기준선 38건) | `j10-mypy` |
| J-11 | 허용 파일 / 무변경 경로 | ① `git diff --name-only f67d8e4..HEAD -- app/` ② `git diff --stat f67d8e4..HEAD -- app/main.py app/db app/tools app/agent app/er app/memory app/briefing app/push alembic` | ① `{app/api/delete.py, app/api/routes.py, app/api/schemas.py}` 의 부분집합(`app/api/__init__.py` 가 필요하면 구현 전 보고) ② **빈 출력** | `j11-scope` |
| J-12 | 기존 테스트 무수정 | `git diff --name-only --diff-filter=M f67d8e4..HEAD -- tests/` | **빈 출력**(새 파일은 `--diff-filter=A` 로만). 기존 테스트를 고쳐야 하면 구현 전 보고 | `j12-tests-unmodified` |
| J-13 | (B 포함 시) 프론트 | ① `npm --prefix web run typecheck` ② `npm --prefix web test -- --run --reporter=verbose` ③ `npm --prefix web run build` ④ `npm --prefix web run e2e` ⑤ `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v "^web/src/components/ui/"` ⑥ `grep -rn "window.confirm\|confirm(" web/src --include=*.tsx` ⑦ `git diff --stat f67d8e4..HEAD -- web/src/routes.ts web/src/screens/ChatScreen.tsx web/src/screens/BriefingScreen.tsx` | ① ③ 종료 0 ② 실패 0, 총 건수 = U4 시작 전 기준선 + 신규 ④ 실패 0, `expectNoStrayRequests` 통과 ⑤ `web/src/components/AppShell.tsx` **1파일뿐** ⑥ 0줄 ⑦ **빈 출력** | `j13-front` |
| J-14 | (B 제외 시) 프론트 무변경 | `git diff --stat f67d8e4..HEAD -- web/` | **빈 출력** | `j14-web-unchanged` |
| J-15 | `tests.md` 행 수 | `tests.md` 표 행 수(절별) = U1~U4 신규 테스트 수, 이름이 `pytest -v`/Vitest verbose 출력과 1:1 | 일치 | `u5-tests-md-check` |

### 사람 점검 (B 포함 시, 자동 J-1~J-13 통과 뒤)

| # | 무엇 | 체크리스트 | 증거가 갖출 항목 |
|---|---|---|---|
| H-1 | 실서버에서 삭제 흐름 1회(로컬, 배포 아님) | ① 테스트용 인물 하나를 채팅으로 만든다 ② 카드에서 삭제 → 확인 블록이 같은 카드 안에 뜬다(새 창·패널 없음) ③ 취소 → 그대로 ④ 삭제 → 그리드·사이드바에서 사라짐 ⑤ 그 인물 이름으로 채팅에서 물어보면 "기록이 없어요" 계열 답(P5b) | 항목마다 통과/수정 필요 + 사용자 한 줄 의견, **"수정 반영 횟수: n" — n ≤ 1**(P8 결정 L) |

## 결정 항목 (구현자가 추측할 자리를 남기지 않는다 — FIX-033 (b). 확정 칸은 사용자가 채운다)

### 결정 A · "삭제 전 확인" 을 어떻게 요구하나

**A-1 확인 방식**

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 서버 2단계(같은 엔드포인트) + 화면 확인 — 추천** | 확인값 없이 `DELETE` 하면 422 `confirmation_required`(기존 `ConfirmationRequired`·핸들러 재사용, `reason="person_delete"`), 쓰기 0. 맞는 확인값과 함께 다시 `DELETE` 하면 삭제. 화면은 카드 안 인라인 확인 뒤 확인값을 붙여 부른다(B 포함 시) | 수용 기준 "확인을 요구" 를 **서버가** 보장한다 — curl·버그 난 프론트·잘못된 id 로도 한 번에 지워지지 않는다. 새 라우트·새 예외·`main.py` 변경 0. 비용: 클라이언트가 확인값을 알아야 한다(A-2) |
| (b) (a) + 미리보기 `GET /persons/{id}/delete-preview` | 지워질 건수(별칭·사실·이벤트·일정·질문·trace)를 먼저 보여 준다 | 확인 문구가 구체적("이벤트 12건이 함께 지워집니다")이 된다. 비용: 라우트 1개·테스트 추가, 카드 응답에 이미 타임라인·일정이 보여 효용이 작다 |
| (c) 화면 확인 대화상자만 | 서버는 `DELETE` 즉시 삭제 | 가장 단순. 그러나 "확인을 요구" 를 서버가 지키지 않아 API 수준에서 수용 기준을 증명할 수 없고, B 를 제외하면 확인 자체가 사라진다. 비추천 |
| (d) 서버 발급 일회용 토큰 | 미리보기에서 토큰 발급 → `DELETE ?token=` | 강하지만 토큰 저장소(새 테이블 또는 서명 키)가 필요 — 스키마 v2 에 없다. 과함 |

원칙5 와의 관계: 확인은 **인물 카드 화면 안의 인라인 블록**이라 새 화면·새 라우트가 아니다. `Dialog`/`Sheet` 를 쓰면 P8b 판정 12행 불변식(라우트 밖 패널 = `AppShell` 1개)이 깨지므로 쓰지 않는다.

**A-2 확인값과 전달 위치**

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(i) 현재 `display_name` 을 JSON 본문 `{"confirm": "<표시 이름>"}` 로 — 추천** | 서버가 `persons.display_name` 과 정확히 같은지 비교(공백·대소문자 가공 없음) | 상태 없이 "잘못된 id"·"그 사이 이름이 바뀐 인물" 을 막는다(GitHub 저장소 삭제의 이름 입력과 같은 발상). 본문이라 접근 로그에 제3자 이름이 남지 않는다. 비용: DELETE 본문은 일부 프록시가 버린다 — 로컬은 문제없고 배포(P9) 때 CloudFront 전달을 확인해야 한다(리스크 4) |
| (ii) 같은 값을 헤더 `X-Confirm-Delete` 로 | 비교 방식 동일 | 로그·프록시 문제 없음. 비용: 한글 헤더 값은 인코딩 규칙이 따로 필요(RFC 상 ASCII) — percent-encoding 약속을 하나 더 만든다 |
| (iii) 쿼리 `?confirm=<표시 이름>` | 동일 | 가장 단순하지만 제3자 이름이 URL·접근 로그에 남는다(security §5 저장 최소화와 어긋남). 비추천 |
| (iv) 쿼리 `?confirm=true` 상수 | 값 비교 없음 | 실수 방지 효과가 거의 없다(잘못된 id 도 그대로 지움) |

**A-3 화면 확인 문구(B 포함 시, 프론트 고정 문장)** — 추천: 「"{display_name}" 님의 별칭·사실·기록·일정이 모두 지워지고 되돌릴 수 없습니다.」 버튼 [삭제] / [취소]. 실패 문구: 「삭제하지 못했어요. 다시 시도해 주세요.」 (이름은 서버 값 그대로 끼워 넣는다 — 원칙7 가공 금지)

확정: **A-1 (a) 서버 2단계 + 화면 확인 · A-2 (i) 본문 `{"confirm": 현재 display_name}` · A-3 추천 문구 그대로** — 사용자 2026-11-09

### 결정 B · 프론트를 이 패키지에 넣나

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 포함 — 추천** | U4: 인물 카드 화면에 삭제 버튼 + 같은 카드 안 인라인 확인(frontend-agent) | 사용자가 실제로 쓸 수 있는 유일한 입구다(제품에 curl 사용자는 없다). 화면 수는 그대로 3개(원칙5). 비용: 단위 1개(Vitest·E2E·사람 점검 H-1), frontend-agent 위임 1회 |
| (b) API 만 | U4 없음, J-14 로 `web/` 무변경 판정 | 범위가 가장 작다. 그러나 화면에 입구가 없어 security §5 의 "사용자가 지울 수 있다" 가 문서상으로만 성립하고, 나중에 프론트 패키지를 또 열어야 한다 |

확정: **(a) 포함 — 인물 카드 안 삭제 버튼 + 인라인 확인(새 화면 없음), U4 frontend-agent** — 사용자 2026-11-09

### 결정 C · JSONB 정리 정책

**C-1 `pending_questions`**

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 그 인물을 참조하는 행은 답변 여부와 관계없이 행 삭제 — 추천** | 판별(C-3)이 참인 질문 행을 지운다 | 미답변 질문을 남기면 사용자가 칩을 눌렀을 때 재개가 없는 인물을 `update_person` 하려다 `PersonNotFound` → `loop_error` 로 끝난다(쓸모없는 질문). 질문 문장·`options` 에도 그 인물 이름이 들어 있다(pipeline.py 212~214행) — 키만 지우면 이름이 남는다. 답변된 질문은 재개에 다시 쓰이지 않는 이력이라 지워도 동작 영향 0. 비용: "민수/민준 중 누구?" 처럼 **다른 인물도 후보였던 미답변 질문**이 함께 사라진다 — 사용자가 그 말을 다시 하면 새로 묻는다 |
| (b) 미답변만 삭제, 답변된 것은 키 마스킹 | 답변된 행의 인물 id 를 `null` 로 | 이력 행은 남지만 질문 문장 속 이름이 그대로 남는다. 판별·마스킹 코드가 둘로 갈린다 |
| (c) 후보 목록에서만 그 인물을 빼고 질문 유지 | `candidate_ids`·`options`·`affirmative_options` 에서 제거 | 다른 후보에 대한 질문은 살린다. 그러나 질문 문장을 다시 써야 하고(이름이 문장 속에 있음), 후보가 1명만 남으면 질문 성격이 바뀐다(FIX-035 문구 분기). 복잡도 대비 이득이 작다 |
| (d) 만료 처리 | `answered_at` 을 채워 대기 목록에서 빼기만 | 이름·id 가 그대로 남아 "정리" 가 아니다. 비추천 |

**C-2 `agent_traces`**

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 그 인물을 참조하는 행 삭제 — 추천** | 판별(C-3)이 `input` 또는 `output` 에서 참인 행을 지운다 | 같은 행 안에 이름·발화 조각·브리핑 문장·후보 표시 이름이 함께 있어(예: `ask_user` input 의 질문 문장, `briefing_compose` output 의 문장), id 만 지우면 제3자 정보가 남는다. 행 삭제는 "남는 것 0" 을 센티널 텍스트 검색으로 기계 증명할 수 있다. 원칙8 비용: 평가는 운영 trace 를 쓰지 않는다(사실 3 — U1 확인). **원칙9 비용**: 그 인물이 "후보로만" 끼었던 ER 판정 행(다른 인물로 merge 된 판정)의 근거도 함께 사라진다 — 남은 인물의 그 판정에 대한 trace 근거가 빈다. 그 인물의 이벤트 원문(`events.raw_utterance`)은 남아 기록 자체의 근거는 유지된다 |
| (a') 혼합 — "주체" 행은 삭제, "후보로만" 끼인 행은 그 후보 항목만 제거 | 툴 trace·브리핑·메모리·푸시처럼 그 인물이 주체인 행은 삭제, ER 행은 `candidates[]`·`candidate_ids` 에서 그 항목만 빼고 유지 | 원칙9 를 더 지킨다. 비용: 단계(step)별로 "주체" 정의와 부분 삭제 코드가 필요하고, 후보 항목 밖(발화·breakdown)에 남은 이름 조각은 지우지 못한다. 테스트 표면이 2배 |
| (b) 값 마스킹 | 인물 id 위치를 `null` 로, 행 유지 | 원칙9 행 수는 보존. 그러나 이름·문장이 남아 "완전 삭제" 가 아니고, `null` 이 된 행이 `promote.py`·`read.py` 의 trace 조회 의미를 바꿀 수 있다. 비추천 |
| (c) 키 제거 | `person_id` 등 키를 통째로 삭제 | (b) 와 같은 문제 + 행 스키마가 깨져 trace 를 읽는 코드가 `KeyError` 를 낼 수 있다 |

**C-3 판별 규칙(무엇을 "그 인물 참조" 로 보나)과 구현 방식**

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 구조 규칙(경로 목록) + SQL 사전 거름 — 추천** | 규칙: ① 어느 깊이든 키 `person_id`·`matched_person_id` 의 **정수** 값 ② 키 `person` 아래 사전의 `id` ③ 툴 이름이 `create_person`·`update_person` 인 trace `output` 최상위 `id` ④ 키 `candidate_ids`·`person_ids` 아래 사전의 **값** ⑤ 키 `candidate_person_ids` 배열 원소 — U1 전수 조사에서 더 나오면 구현 전 보고. `bool` 은 정수로 보지 않고 문자열 숫자도 보지 않는다. SQL 로 `input::text LIKE '%<id>%' OR output::text LIKE …` 인 행만 가져와(과잉 포함·누락 0) Python 에서 규칙으로 정밀 판정 | 이벤트·일정·질문 id 와 값이 겹쳐도 남의 행을 지우지 않는다(V1-5·V1-6). 규칙은 한 곳(`PERSON_REF_RULES`)에 있다. 누락은 U2 센티널 텍스트 검색이 그물로 잡는다. 비용: 앞으로 trace 모양을 새로 만드는 패키지가 규칙을 갱신해야 한다(리스크 2) |
| (b) 텍스트 정규식만 | `::text ~ '\m<id>\M'` 이면 참조 | 단순하지만 다른 시퀀스의 같은 숫자에 걸려 **다른 인물의 trace·질문을 지운다**. 비추천 |
| (c) `jsonb_path_exists` 만(SQL) | 규칙 ①~⑤ 를 jsonpath 로 | DB 한 번에 끝나지만 ③(툴 이름 조건)·④(사전 값) 표현이 길고 단위 테스트를 DB 없이 못 한다 |

확정: **C-1 (a) 참조 질문 행 삭제(답변 여부 무관) · C-2 (a) 참조 trace 행 통째 삭제(원칙9 비용 수용) · C-3 (a) 구조 규칙 + LIKE 사전 거름 + Python 정밀 판정** — 사용자 2026-11-09 (C-1·C-2 사용자 선택, C-3 추천안)

### 결정 D · FK CASCADE 를 어떻게 쓰나

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 기존 DB CASCADE 그대로 — 추천** | `DELETE FROM persons WHERE id=:pid AND user_id=:uid` 한 문장. 자식 5테이블·`fact_sources` 는 DB 가 지운다. 마이그레이션 0 | FK 6개가 이미 CASCADE(사실 1, `0001` 24행·메타데이터 테스트). 수용 기준 문장 "FK CASCADE 로 함께 지워지고" 를 글자 그대로 지킨다. ORM 관계(relationship)가 정의돼 있지 않아 `session.delete()` 도 결국 같은 SQL 이지만, 코어 `delete()` 가 의도를 더 분명히 한다 |
| (b) 애플리케이션에서 순서대로 삭제 | `fact_sources` → `events`/`person_facts` → `person_aliases`/`schedules` → `persons` | DB 제약이 이미 하는 일을 중복. 순서 실수 위험만 늘고 수용 기준 "FK CASCADE 로" 와 어긋난다 |
| (c) 새 마이그레이션으로 CASCADE 재선언 | — | 이미 걸려 있어 `alembic check` 가 변경 없음을 보인다. 불필요 |

`push_subscriptions` 는 `persons` 로 가는 FK 가 없는 사용자 단위 테이블이라 무관(사실 2) — J-1 대조군 단언에 구독 행 수 불변을 함께 넣는다.

확정: **(a) 기존 DB CASCADE, `DELETE persons` 한 문장(마이그레이션 없음)** — 추천안, 사용자 2026-11-09 위임

### 결정 E · 남의 인물·없는 인물 응답

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 404 `{"detail":{"code":"not_found"}}`(존재 숨김) — 추천** | `_owned_person` → `PersonNotFound` → 공통 404 | `GET /persons/{id}`·`/events/{id}/raw` 등 기존 관례(사실 4, main.py 43~45행 "존재 여부를 흘리지 않는다") 그대로. 코드 추가 0 |
| (b) 403 | 남의 것이면 403, 없으면 404 | 남의 인물 id 가 **존재한다**는 사실을 흘린다. 기존 관례와 어긋남 |

확인 검사와의 순서: **소유 확인이 먼저**(남의 인물이면 확인값이 맞든 틀리든 404) — 그래야 확인 422 가 존재 여부를 흘리지 않는다.

확정: **(a) 404(기존 GET 관례), 소유 확인을 확인값 검사보다 먼저** — 추천안, 사용자 2026-11-09 위임

### 결정 F · 성공 응답 모양

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 200 + 삭제 건수 요약 — 추천** | `{"person_id": <id>, "deleted": {"persons": 1, "person_aliases": n, "person_facts": n, "fact_sources": n, "events": n, "schedules": n, "pending_questions": n, "agent_traces": n}}` — 이름·원문 없음 | 테스트가 값으로 단언할 수 있고(FIX-033 (a)), 증거 파일에 무엇이 지워졌는지 남는다(원칙9 를 응답으로 보완 — 결정 H). 비용: 응답 스키마 1개, 삭제 전 `count` 질의 6번(인물 1명 단위라 작다) |
| (b) 204 No Content | 본문 없음 | REST 관례에 가장 맞고 단순. 그러나 정리 범위를 HTTP 테스트에서 직접 볼 수 없어 DB 질의로만 판정해야 한다 |

확정: **(a) 200 + 테이블별 삭제 건수 JSON** — 추천안, 사용자 2026-11-09 위임

### 결정 G · id 없이 이름·발화만 남은 trace (코드를 읽다 발견한 열린 범위)

`loop_extract` 의 `input`(사용자 발화 원문, 예: "민수랑 어제 싸웠어"), `loop_turn`·`loop_query` 의 `reply` 문장 등은 인물 id 없이 이름·원문을 담는다. 결정 C 만으로는 이 행이 남는다.

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(i) 이 패키지는 id 참조만 정리하고, 남는 것을 문서로 밝힌다 — 추천** | 리스크 절·03-log·`security.md` §5 구현 줄에 "id 없는 발화 trace 는 남는다" 를 적는다 | backlog 수용 기준이 "`person_id` 참조" 로 범위를 정했다(확정되지 않은 범위를 넣지 않는다). 비용: "완전 삭제" 라는 이름과 실제 사이에 틈이 남는다 — 사용자가 이를 받아들일지 정해야 한다 |
| (ii) 같은 턴의 trace 전부 삭제 | id 참조 행이 속한 턴(세션 안에서 `loop_extract` ~ `loop_turn`/`loop_resume` 사이, id 순)을 통째로 지운다 | 원문 발화까지 지워 가장 "완전" 하다. 비용: 턴 경계를 trace 순서로 추정해야 하고(턴 id 컬럼 없음), 같은 턴의 다른 인물 근거까지 지운다. 판별 테스트가 크게 는다. backlog 문장 변경(범위 확대)이 필요할 수 있다 |
| (iii) 이름·별칭 문자열 검색으로 삭제 | `::text LIKE '%민수%'` | "엄마"·"팀장님" 처럼 흔한 호칭은 다른 인물 행까지 지운다. 비추천 |

확정: **(i) id 참조만 정리하고, 이름·발화만 남는 trace 는 한계로 security.md §5 에 밝힌다** — 사용자 2026-11-09

### 결정 H · 삭제 자체를 trace 로 남기나

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(i) 남기지 않는다 — 추천** | 다른 비-툴 HTTP 엔드포인트(`/push/subscriptions`·읽기 API, registry 216·225행)와 같다. 무엇이 지워졌는지는 응답(결정 F)으로 돌려준다 | 원칙9 는 "판정" 의 근거다 — 삭제는 에이전트 판정이 아니라 사용자 명령이다. 삭제 기록에 인물 id 를 남기면 방금 지운 참조를 다시 만드는 셈이다 |
| (ii) 건수만 담은 trace 1행(`step="person_delete"`, id·이름 없음) | 감사 흔적 | id 가 없으면 무엇을 지웠는지 알 수 없어 감사 가치가 낮고, `session_id` 를 새로 지어야 한다 |

확정: **(i) 남기지 않음(비-툴 엔드포인트 선례)** — 추천안, 사용자 2026-11-09 위임

### 결정 I · 툴이 아니라 HTTP 엔드포인트인가

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) HTTP 엔드포인트만 — 추천** | `app/tools/` 무변경, `tools_check.py` 7/7(J-6) | CLAUDE.md 툴 표(7종)는 고정 계약이다. 대화로 삭제를 시키면 LLM 이 되돌릴 수 없는 일을 판단하게 된다 — 오병합을 피하려고 확신도 미달 시 묻는 이 제품의 태도(원칙1·2)와 반대 방향 |
| (b) 8번째 툴 `delete_person` | 대화 "민수 지워줘" 로 삭제 | 툴 표 변경 = 기획서 변경(CR) 필요. 비추천 |

확정: **(a) HTTP 엔드포인트만, 툴 7종 불변(tools_check 7/7)** — 추천안, 사용자 2026-11-09 위임

### 결정 J · 삭제 로직을 둘 모듈

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 새 모듈 `app/api/delete.py` — 추천** | 판별 순수 함수 + `delete_person` 서비스. 읽기 쪽 `app/api/read.py`(registry 227행)와 나란히 | HTTP 전용 기능이 `app/api/` 안에 머문다. `app/tools/`(툴 모듈, `tools_check` 대상)·`app/agent/`(루프)와 섞이지 않아 J-6·J-11 판정이 단순해진다 |
| (b) `app/tools/persons.py` 에 추가 | `_owned_person` 옆 | 툴이 아닌 함수가 툴 모듈에 들어가 "툴 7종" 경계가 흐려진다 |
| (c) `app/api/read.py` 에 추가 | — | "읽기 전용" 모듈 이름·docstring(쓰기 0)과 모순 |

확정: **(a) 새 `app/api/delete.py`** — 추천안, 사용자 2026-11-09 위임

### 결정 K · 정리 대상 trace 를 찾을 때 세션 범위

| 후보 | 내용 | 근거·비용 |
|---|---|---|
| **(a) 전 세션(전역) — 추천** | `pending_questions`·`agent_traces` 전체에서 판별 | 두 테이블에 `user_id` 가 없고(사실 3) 인물 id 는 전역 유일 IDENTITY 라, 다른 사용자의 행이 같은 인물 id 를 참조할 수 없다(인물 검색이 `user_id` 로 걸러짐). 브리핑·메모리 trace 는 채팅 세션과 다른 `session_id`(`briefing:<uuid>` 등)를 쓰므로 세션 한정이면 빠진다 |
| (b) 요청 헤더 `X-Session-Id` 의 세션만 | — | 다른 세션·브리핑 trace 가 남는다. 수용 기준 미달 |

확정: **(a) 전 세션(브리핑·메모리 trace 포함), 사용자 범위는 `user_id` 로 한정** — 추천안, 사용자 2026-11-09 위임

## 리스크 · 미결

1. **판별 규칙 누락(가장 큰 리스크)** — JSONB 모양이 여러 패키지에 흩어져 있다(사실 3). 대응: U1 전수 조사 + U2 센티널 id(987654321) 텍스트 검색이 실제 쓰는 코드가 만든 JSONB 에 대해 "남는 것 0" 을 증명한다. 센티널이 없는 경로(시나리오에 안 넣은 step)는 잡지 못하므로, U2 시나리오가 사실 3 표의 쓰는 곳을 전부 한 번씩 지나가는지 U2 보고에 표로 대조한다.
2. **이후 패키지의 규칙 갱신 의무** — 새 trace 모양(새 키 이름으로 인물 id 저장)을 만드는 패키지는 `PERSON_REF_RULES` 를 함께 갱신해야 한다. 이 의무를 `registry.md` 의 `app/api/delete.py` 행 비고와 모듈 docstring 에 적는다. 규칙 미갱신은 U2 센티널 테스트가 그 새 경로를 지나가지 않으면 잡히지 않는다 — 이 한계를 03-log 에 적는다.
3. **결정 G (i) 를 고르면 남는 것** — id 없는 발화·답 문장 trace. "완전 삭제" 표현과의 틈을 security §5 구현 줄에 밝힌다.
4. **DELETE 본문(결정 A-2 (i))과 배포** — 로컬 uvicorn·FastAPI·`fetch` 는 DELETE 본문을 그대로 전달한다. CloudFront → Caddy → FastAPI 경로의 전달 여부는 배포(P9)에서 확인할 항목으로 P9 계획에 넘긴다(이 패키지는 배포하지 않는다).
5. **동시성** — 삭제와 같은 인물에 대한 채팅 턴이 겹치면, 턴 쪽 `add_event` 가 FK 위반(`IntegrityError`)으로 실패하고 `SQLAlchemyError` 는 루프가 삼키지 않아 500 이 된다(registry 170행 R-3 규약). 단일 사용자·사람이 누르는 버튼이라 빈도가 낮아 이 패키지에서는 막지 않고 기록만 한다.
6. **`fact_sources` 교차 연결** — 다른 인물의 사실이 이 인물의 이벤트를 근거로 잇고 있다면 링크만 사라지고 사실은 남는다(근거 원문 수 감소). U1 에서 `FactSource(` 6곳이 같은 인물 이벤트만 잇는지 확인해 보고한다. 교차가 가능하면 구현 전 멈추고 보고.
7. **결정 C-1 (a) 의 부수 효과** — 다른 인물도 후보였던 미답변 질문이 사라진다. 프론트 채팅 화면은 `GET /questions/pending` 을 다시 불러 사라진 칩을 지운다(P8 U3) — B 포함 시 Vitest 로 확인할지 U4 위임 때 결정(추가 상수 아님, 테스트 범위).
8. **기존 테스트 수정 가능성** — 라우트 목록을 스냅샷으로 단언하는 기존 테스트가 있으면 J-12 가 깨진다. 발견 시 구현 전 보고.

## 읽은 카드

- `docs/backlog.md` 30~44행(P2 절 — 38·39행 수용 기준과 부연)
- `docs/wiki/security.md` §3·§4·§5 (grep 으로 해당 줄 전후)
- `docs/wiki/INDEX.md` 67·74행(패키지 표)
- `docs/wiki/registry.md` — grep(`persons`·`routes.py`·`models.py`·`alembic`·`helpers_read_api`·`assert_no_writes`·`_owned_person`·`PersonNotFound`·`delete`) 결과 행 45~255
- `docs/wiki/templates/plan.md` 전문
- `docs/wiki/packages/P5b-query-turn/01-plan.md` 1~12행, 138~179행(판정 표·결정 A 형식), 절 목차(grep)
- `docs/wiki/packages/P5b-query-turn/04-review.md` 119행(mypy 기준선)
- `docs/wiki/packages/P8b-persons-grid/01-plan.md` 1~170행(혼합 패키지 형식·판정 12행 불변식)
- `.claude/gitlog.md` 스냅샷 2026-11-09 09:14
- 코드: `app/db/models.py` 전문 · `alembic/versions/` 목록과 `ondelete` grep · `app/api/routes.py` 380~498행 · `app/api/deps.py` 전문 · `app/main.py` 28~187행 · `app/tools/context.py` 170~249행 · `app/tools/types.py` 169~209행·`to_dict` grep · `app/tools/persons.py` 417~429행 · `app/er/pipeline.py` 170~239행 · `app/agent/loop.py` 455~514행·`context`/`person_id` grep · `app/memory/promote.py` 120~149행 · `app/api/read.py` 280~319행 · `app/agent/types.py`·`briefing/types.py`·`memory/types.py`·`push/types.py` STEP 상수 grep · `scripts/` `AgentTrace` grep · `app/memory/` `FactSource(` grep · `web/src/api/client.ts`·`web/src/screens/PersonCardScreen.tsx` grep · `web/src/components/ui/` 목록
