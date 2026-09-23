# P5-loop · 계획 (01-plan)

상태: 초안(02-plan-verify `결과: 보류` 반영 개정 1차) | 담당: backend-agent(`app/agent/`·`app/api/`·`app/settings.py`) | 작성: 2026-09-23

> **개정 이력.** verifier 02-plan-verify 가 보류 3건(H-1·H-2·H-3)·권고 8건(R-1~R-8)을 냈고, 그중 H-3 에서 **사용자가 결정 L 을 (i) 에서 (iii) 하이브리드로 바꿨다**. 이 문서는 그 개정본이다. 바뀐 곳: 목표·범위(인식 단계 = `tool_calls` 제안 + 게이트) · 산출물(`app/agent/propose.py`·`gate.py`) · 작업 단위 U1~U8(초안은 U1~U7) · 판정 표(7행 실행 가능화, 부정 4행 신설) · 결정 F(step 6종) · 결정 L 본문 · 새 미결 2건(M-1·M-2). **확정 11건(A·B·C·D·E·F·G·H·I·J·K)은 그대로다** — 툴을 누가 고르느냐만 바뀌었다. 다음 단계는 **미결 M-1·M-2 사용자 결정 → verifier 재판정(02-plan-verify)** 이며, 이 개정본은 코드·테스트를 한 줄도 쓰지 않았다(`app/` 은 읽기만 했다).
> **backlog 를 줄 번호로 가리키지 않는다(R-5).** 항목이 하나 삽입되면 번호가 밀려 문서가 조용히 틀린다(실제로 P5 줄이 70→73 으로 밀렸다). 이 문서는 backlog 를 **인용문**으로만 가리킨다.
태그 — 패키지: P5-loop · 닫는 검증: **R6 R7** · 기대는 결정: **D1 D2** D12 D13 D6 D10 D11 · 구현하는 명세: **S3.4** S3.2 S3.3 · 관련 원칙: 원칙1 원칙2 원칙4 원칙7 원칙9
의존:

- **P4b 게이트 통과** — `1075dd6`(`/devlog done`, verifier 04-review `결과: 완료`, 사용자 승인). 실 재실행 `855a26b`, 기준선 대비 `4338eea`, 수용 기준 기계 검증 `cf5a171`. 게이트 수치 `0.8 [] True True`(`T_merge=0.8` 에서 제안 방식 오병합 0/132·미검출 0/132, 베이스라인 4종 모두 미지배, F1 0.8972, 되묻기 31건 23.5%). backlog 의 P5 항목("**의존: P3, P4b 게이트 통과**(P4 는 부분완료·미달, CR-001)")이 착수 조건으로 건 "**P4b 게이트 통과**"가 이 해시로 풀렸다. `CURRENT.md` 15·16행이 "**P5 착수 가능**"·"**다음은 P5**"로 같은 사실을 적는다.
- **P4-pilot-eval 부분완료** — `adf9f1b`. 미달 자체는 P4b 가 받았으므로 P5 의 착수 조건은 P4 가 아니라 P4b 다(backlog P5 항목의 "P4 는 부분완료·미달, CR-001").
- **P2-tools 완료**(04-review `결과: 완료`) — 이 패키지가 호출자로 붙을 툴 7종. `app/tools/persons.py`(`a9cb254`·`f318d58`)·`records.py`(`9cb35b6`)·`questions.py`(`8162e09`)·`briefing.py`(`7c94aad`)·`context.py`(`4eca3e9`), HTTP 골격 `app/api/{routes,schemas,deps}.py`(`4d5817e`).
- **P3-er 완료**(04-review `결과: 완료`) — 루프가 부를 ER 진입점 `app/er/pipeline.py`(`d6e5949` U6 `resolve` → `cc5d24f` U7 `apply_resolution`), P4b 에서 `dbcfca0`(보수 강등)까지 확장됨.
- **FIX-001 완료** — `1227026`(dev = origin/dev = main = origin/main 네 갈래 동일). **이 패키지의 시작 해시(무변경 diff 기준점) = `1227026`.** 스냅샷 시점 미커밋 변경은 `docs/wiki/journal.md` 1건과 `reports/pilot/` 미추적 2건뿐이고 제품 코드는 0이다(`.claude/gitlog.md` 74~79행).
- 태그별 커밋 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P5-loop D1 D2 R6 R7` 실행을 요청**한다 — 이 문서는 Bash 없이 `.claude/gitlog.md` 스냅샷과 `registry.md` 등록 해시만 근거로 썼다(L-001).
- 이 패키지가 끝나야 **P6-memory·P6-briefing·P8-frontend** 가 시작할 수 있다(backlog 의 그 세 항목이 단 "의존: P5").

## 목표

`docs/backlog.md` P5 절의 한 줄 — "**에이전트 루프(인식→해석→기록→응답) + ask_user 재개**" — 을 실현한다. 지금 저장소에는 툴 7종(P2)과 ER 4단계(P3·P4b)가 각각 따로 서 있고 **그 둘을 이어 하나의 턴으로 돌리는 주체가 없다**: `app/agent/` 는 존재하지 않고, HTTP 라우트는 `GET /health` 와 `POST /answers/{question_id}` 둘뿐이며 후자는 "답 저장"까지만 한다(`app/api/routes.py` 59~62행이 스스로 "그 화살표는 **P5-loop** 이 이 라우트를 확장해서 잇는다"고 적어 두었다). 이 패키지는 사용자의 한 발화를 받아 **인식**(LLM 이 구조화 출력 **1회**로 `tool_calls` 목록을 제안하고, 코드가 화이트리스트·인자 스키마·`person_id` 금지·개수 상한 **게이트**로 거른다 — 결정 L(iii)) → **해석**(제안이 가리키는 인물 언급마다 `resolve`/`apply_resolution` 으로 기존 인물에 연결하거나 확신도 미달이면 `ask_user` 로 되묻고) → **기록**(확정된 `person_id` 로 인자를 채워 통과한 제안만 `add_event`/`add_schedule`/`update_person` 으로 실행하고) → **응답**(무엇을 기억했는지와 되물을 것이 있으면 선택지를 돌려주는) 한 흐름을 `POST /chat` 요청 하나 안에서 돌리고, 되묻기로 끝난 턴을 `POST /answers/{question_id}` 요청 하나로 **저장된 `context` 에서 이어받아** 마저 끝낸다. 이로써 review-index 14·15행이 `P2-tools, P5-loop` 두 패키지에 걸쳐 두고 "재개 흐름은 P5-loop" 라는 꼬리를 남긴 **R6**(신규 인물 자동등록 vs 확인형 — "루프가 확인 없이 `create_person` 을 부르지 않는다")과 **R7**(ask_user 동기 반환 불가 — S3.4 턴 N+1 의 **뒤 절반**)을 닫는다. 새 결정·새 명세를 만들지 않는다 — D1·D2·S3.4 가 이미 적어 둔 것을 코드로 옮길 뿐이다. **이 문장이 사실인 근거**: 초안의 결정 L(i)("툴 선택은 코드가 한다")는 `docs/proposal.md` 3.1 절 "툴 정의 (Function Calling)" 72행 "**파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다**" 와 어긋나 CR 또는 새 D 카드가 필요했다(02-plan-verify H-3). 사용자가 L 을 **(iii) 하이브리드**로 바꾸면서 "LLM 이 툴을 선택·호출"이 그대로 성립하므로 **기획서 이탈이 사라졌고, 따라서 CR·새 D 카드를 만들지 않는다.**

## 범위

- 포함:
  - **인식 단계(제안)** — 발화 1건 → LLM **1회** 구조화 출력(`app/er/judge.py` 의 공급자 등록표·`select_provider`·오류 어휘를 그대로 재사용)으로 `{tool_calls: [{name, args}, …]}` 를 받는다. 인물은 `person_id` 가 아니라 **언급 문자열**(`args.person`)로 지칭한다. `add_event` 의 `type` 은 CLAUDE.md 고정 집합 7종 밖 값을 받지 않는다(`app/db/models.py::EVENT_TYPES` 재사용). **다회 왕복이 아니다** — 툴 결과를 LLM 에 다시 넣지 않는다(비용·재현성: 턴당 LLM 1회 고정, 원칙8).
  - **게이트 단계(코드)** — 제안을 그대로 실행하지 않는다. ① **화이트리스트**: `name ∉ app.tools.TOOL_NAMES` → 거부(`unknown_tool`). ② **호출 가능 집합**: `search_person`·`ask_user`·`get_briefing` 제안은 거부(`not_callable_by_llm`) — 앞의 둘은 ER 4단계 안에서만 불려야 오병합 방어가 유지되고(원칙1·4), `get_briefing` 은 P6-briefing 몫이다. ③ **인자 스키마**: `inspect.signature(app.tools.<name>)`(`scripts/tools_check.py` 와 같은 출처)과 대조해 필수 누락·미지 인자·타입 위반 거부(`bad_args`). ④ **`person_id` 금지**: LLM 이 `person_id` 를 직접 준 제안은 무조건 거부(`person_id_from_llm`) — `person_id` 는 오직 `resolve()` → `apply_resolution()` 을 거쳐서만 얻는다. ⑤ **개수 상한**: 결정 A(i)(언급 5·이벤트 5·일정 3)를 제안 목록에 적용, 초과분 거부(`limit`). 통과분만 실행하고, **거부한 제안은 사유와 함께 trace 에 남긴다**(`loop_gate`, 결정 F).
  - **해석 단계** — 통과한 제안이 가리키는 언급마다 `app.er.resolve()` → `app.er.apply_resolution()`. `merge` 는 별칭 누적까지 ER 이 하고, `identity`/`new_person` 은 ER 이 `pending_questions` 행을 만들고 그 `question_id` 를 돌려준다. **루프는 확신도를 다시 계산하지도, 임계치를 다시 비교하지도 않는다**(원칙1·2·4 — 판정은 ER 하나의 자리).
  - **기록 단계** — 게이트를 통과하고 `person_id` 가 **확정된** 제안만 실행한다: `args.person`(언급) 자리를 해석 단계가 얻은 `person_id` 로 **코드가** 치환해 `add_event(person_id, type, content, occurred_at, raw_utterance)`·`add_schedule`·`update_person` 을 호출한다. `raw_utterance` 는 LLM 제안에서 받지 않고 사용자가 친 원문 그대로 루프가 주입한다(S3.2 비고 "런타임이 raw_utterance 자동 주입").
  - **`pending_questions.context` 확장(재개 재료)** — 되묻기로 턴이 끝날 때, 아직 실행하지 않은 통과 제안·보류 draft·`hints` 를 `PendingResume` 로 만들어 `apply_resolution` **호출 전에** `dataclasses.replace(resolution, ask_payload=…)` 로 `context` 에 얹는다(결정 C·D·E·J 가 전제하는 재료를 만드는 유일한 경로 — 아래 "결정 M" 절).
  - **응답 단계** — 무엇을 기억했는지 + 되물을 것(`question_id`·`options`)을 담은 결정적 응답(결정 B).
  - **`POST /chat`** — 발화 입력, 세션 귀속(`X-Session-Id` 규약, 결정 I), 응답 스키마. 프론트(P8)가 바로 쓰는 계약이다.
  - **`POST /answers/{question_id}` 확장(재개)** — 답 저장(P2 가 이미 함) **뒤에** 저장된 `context` 로 루프를 이어받아 후속 툴을 호출하고 그 결과를 응답에 담는다. S3.4 8행 "턴 N+1 … 저장된 context 로 루프 재개 → 후속 툴" 의 뒷부분.
  - **D1 확인 질문의 대상 바인딩·1회 소비**(R6 의 꼬리, P2 04-review 108행) — answered `new_person` 질문 하나로 임의의 이름을 `create_person` 할 수 있는 지금의 구멍을, **재개 경로가 `context` 에 적힌 대상(`mention`·`candidate_ids`)에만 쓰도록** 막는다. 소비 1회는 `answer_question` 의 `already_answered`(409)로 강제한다(결정 J).
  - **관측성** — 루프 고유 `agent_traces` 행(step 어휘는 결정 F). 툴 7종·ER 의 trace 는 기존 `@traced` 가 이미 남기므로 **덧붙이기만 하고 기존 규약은 건드리지 않는다**(원칙9). **제안된 툴(`loop_extract`)과 게이트 판정(`loop_gate`: 통과·거부·사유)을 실행된 `tool_call` 행과 함께 볼 수 있어야** P10 이 `docs/proposal.md` 176행 "툴 호출 정확도 | 올바른 툴을 선택한 비율"과 거부율을 잴 수 있다.
  - **문서** — `registry.md` 행(새 모듈)·비고 확장(고친 기존 파일), `README.md` 실행법 한 절, `docs/user-setup/` 의 로컬 재현 절차(기존 카드 갱신, 새 카드 신설 금지).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **3계층 메모리 승격·`fact_sources` 채우기**(S3.5·P6-memory) — 승격은 이벤트가 **쌓인 뒤** 도는 일이고, 이 패키지는 그 이벤트를 **만드는** 쪽이다. `add_event` 는 승격을 건드리지 않는다(registry 59행이 이미 못박았다).
  - **반복 패턴 감지(D9, 90일 3회 → `pattern:{type}`)** — 같은 이유로 P6-memory. 규칙이 보려면 같은 인물의 같은 `type` 이 3건 쌓여 있어야 하는데 이 패키지는 첫 건을 만드는 단계다.
  - **브리핑 생성·주기 작업(1분)·수동 트리거·웹푸시**(S3.6·P6-briefing·P7-push) — `get_briefing` 은 조회만 하는 툴이고(registry 61행 "문장화·제안·LLM 호출 없음"), 문장화·트리거·발송은 별도 수용 기준을 가진 다른 backlog 항목이다. 루프가 미리 부르면 두 패키지의 경계가 흐려진다.
  - **프론트 3화면·PWA·확인 칩 UI**(P8-frontend) — 화면은 3개로 고정(원칙5)이고 이 패키지는 그 화면이 호출할 **계약(요청/응답 스키마)** 만 낸다. UI 를 여기서 만들면 계약이 바뀔 때마다 두 곳을 고친다.
  - **`app/er/` 내부 수정** — P4b 게이트 수치(`0.8 [] True True`)는 `1075dd6` 시점의 ER 코드에서 나온 값이다. 루프를 붙이면서 ER 을 손대면 그 수치의 근거가 사라진다(원칙8). 루프는 **호출자로만** 붙는다.
  - **스키마 v2 변경·마이그레이션·툴 시그니처 v2 변경** — S3.1·S3.2·R10 이 확정한 것이고, `scripts/tools_check.py` 7/7 과 `alembic check` 이 이 패키지의 무변경 증거다. 보류된 기록 항목은 새 컬럼이 아니라 `pending_questions.context`(JSONB)에 둔다.
  - **150건 데이터셋·최종 평가·툴 호출 정확도·이벤트 추출 F1**(P10-final-eval) — P4 04-review 214행·P4 01-plan 254행이 "추출 주체인 P5-loop 이 생긴 뒤 P10 이 잰다"고 이미 인계했다. 이 패키지는 **측정 대상을 만들 뿐 지표를 내지 않는다**.
  - **고민 상담·감정 대화**(원칙7) — 응답은 "무엇을 기억했는가"와 되묻기뿐이다. 브리핑의 "제안"조차 기록된 사실에서 나오는 한 줄로 한정돼 있는데(원칙7 경계 문장), 루프의 응답이 그 선을 넘으면 제품이 상담 봇이 된다.
  - **인물 간(A–B) 관계 저장**(원칙7) — 저장되는 것은 사용자–인물 관계뿐이다(D8). 인식 단계가 "민수와 지훈이 싸웠다"에서 뽑는 것은 **두 사람 각각의 이벤트**이지 둘 사이의 간선이 아니다.
  - **상담 페르소나·음성 입력·네이티브 앱**(원칙7) — 범위 통제의 근거 자체다. 입력은 텍스트 한 줄, 응답은 결정적 문장이다.
  - **다중 사용자 격리**(F-fbaaae) — `pending_questions`·`agent_traces` 에 `user_id` 컬럼이 없어 스키마를 바꿔야 풀린다. 이 패키지는 `user_id = app_user_id()` 단일 사용자 전제를 **문서로 명시**하고 넘어간다(결정 I).
  - **`DELETE /persons/{id}`**(security §5·F-4d2507) — backlog 어느 항목에도 없다. 여기에 끼워 넣으면 수용 기준 없는 코드가 된다. 아래 "backlog 개정 제안" 1 로 올린다.
  - **전체 대화 이력 저장·스트리밍 응답** — S3.4 13행 "`context` 에는 재개에 필요한 것만 … 전체 대화 이력 저장 금지".

## 산출물 (파일 경로)

**새로 만드는 파일**

- `app/agent/__init__.py` — 루프 진입점 재export(`run_turn`·`resume_turn`·타입·상수)
- `app/agent/types.py` — `ToolCallProposal`·`Proposal`(제안 목록 + 원문)·`GateVerdict`(`accepted[]`·`rejected[{index,name,reason}]`)·`EventDraft`·`ScheduleDraft`·`TurnResult`·`PendingResume`·`ResumeInput`·루프 trace 상수(step 어휘·`tool_name`)·`LoopError` 계층
- `app/agent/propose.py` — 인식 단계(초안의 `extract.py` 를 대체한다 — 뽑는 것이 `mentions/events/schedules` 가 아니라 `tool_calls` 이므로 이름도 바꾼다). `Proposer` Protocol + 공급자 구현(`app/er/judge.py` 의 `select_provider`·`enabled_providers`·`call_with_error_mapping` 재사용) + `FakeProposer`(결정적, 네트워크 0) + `PROPOSAL_SCHEMA`·`build_propose_prompt()`
- `app/agent/gate.py` — 게이트. `check(proposal) -> GateVerdict`. 화이트리스트(`app.tools.TOOL_NAMES` import)·호출 가능 집합·`inspect.signature` 인자 대조·`person_id` 금지·상한(결정 A). **거부 사유 어휘는 이 모듈이 단일 출처**(`unknown_tool`·`not_callable_by_llm`·`bad_args`·`person_id_from_llm`·`limit`)
- `app/agent/loop.py` — 오케스트레이션. `run_turn(ctx, utterance, *, proposer=None, judge=None, config=None) -> TurnResult`, `resume_turn(ctx, resume_input) -> TurnResult`, 단계별 trace 기록, `PendingResume` 를 `dataclasses.replace` 로 `ask_payload` 에 얹는 자리
- `app/agent/respond.py` — 응답 단계(결정 B(i) 템플릿 표)
- `tests/test_agent_propose.py` · `tests/test_agent_gate.py` · `tests/test_agent_loop.py` · `tests/test_agent_resume.py` · `tests/test_api_chat.py`
- `docs/wiki/packages/P5-loop/evidence/` — pytest·grep·curl 왕복·trace 조회·무변경 diff 출력

**고치는 기존 파일** (아래 "허용 파일" 각주가 근거)

- `app/api/routes.py` — `POST /chat` 추가, `POST /answers/{question_id}` 에 재개 뒤 절반 연결
- `app/api/schemas.py` — `ChatIn`·`ChatOut`·`AnswerOut` 확장(재개 결과 필드)
- `app/api/deps.py` — 채팅용 `ToolContext` 조립(세션 헤더 규약, 결정 I) + **재개 입력 조립** `load_resume_input(session, question_id) -> ResumeInput{kind, context, session_id}`. `build_ctx()` 의 기존 규약(답할 행의 `session_id` 사용, 결정 12)은 **그대로 두고** 옆에 새 조립 함수를 둔다. 두 가지를 여기서 고친다: (1) `PendingQuestion` ORM 을 읽는 것은 **이 모듈뿐**이고 `app/agent/` 는 값(dict)만 받는다(H-2 의 (b) 경로 차단), (2) `build_ctx` 는 `embedder=None` 이었는데(주석: "답 저장은 별칭을 만들지 않는다") **재개는 `create_person`/`update_person(new_alias)` 로 별칭을 만든다** — 재개·채팅 ctx 는 실제 임베더를 받아야 새 인물이 이후 후보 검색에 보인다(아래 리스크)
- `app/settings.py` — 루프 설정 상수(상한·추출 모델·타임아웃, 결정 A·G)
- `tests/test_api.py` — `AnswerOut` 확장에 따른 기존 단언 갱신(단언을 **없애지 않는다**)
- `docs/wiki/registry.md` · `README.md` · `docs/user-setup/`(해당 카드 갱신)

> **`app/` 허용 파일은 `app/agent/*`(신규 6)과 기존 4개뿐이다** — `app/api/routes.py`·`app/api/schemas.py`·`app/api/deps.py`·`app/settings.py`. 근거: (1) `app/er/*` 는 P4b 게이트 수치가 나온 코드이므로 무수정이어야 그 수치가 이 패키지 뒤에도 유효하다(원칙8), (2) `app/tools/*` 는 시그니처 v2 가 R10 으로 확정돼 `scripts/tools_check.py` 7/7 이 고정 증거다 — 루프는 **호출자**이지 툴의 공저자가 아니다, (3) `app/db/*` 를 고치면 스키마 v2 변경이 되어 S3.1·마이그레이션 이야기가 따라붙는다(`alembic check` 이 무변경 증거). 이 한 줄이 판정 표 "허용 파일" 행의 근거다. `app/main.py` 도 무수정이다 — 루프 오류는 예외로 올리지 않고 잡아서 정상 응답으로 내리기 때문이다(결정 G·H).

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 `/commit`)

- [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어휘 (코드가 도는 건 아직 없다)**: `app/agent/types.py`·`app/agent/__init__.py` 신설. `ToolCallProposal`(`name`·`args`)·`Proposal`(`tool_calls[]`·`raw`)·`GateVerdict`(`accepted[]`·`rejected[{index,name,reason}]`·`stop_reason`)·`EventDraft`·`ScheduleDraft`·`TurnResult`(`reply`·`session_id`·`stored{persons,events,schedules}`·`pending_question`·`stop_reason`·`trace_ids`)·`PendingResume`(재개 context 의 스키마: `version`·`mention`·`hints{relation_tag?,hierarchy?}`·`pending_calls[]`·`held_drafts[]`·`dropped:int`)·`ResumeInput`(`kind`·`context`·`answer`)를 frozen dataclass + `to_dict()` 로 정의한다(`app/tools/types.py`·`app/er/types.py` 와 같은 모양 — 새 직렬화 방식을 만들지 않는다). 루프 trace 상수(`LOOP_TRACE_TOOL_NAME`·step 어휘 6종, 결정 F)와 `app/settings.py` 루프 상수(결정 A·G + `LOOP_MAX_RESUME_BYTES`)를 같이 넣는다. 테스트: `to_dict()` 왕복·step 어휘 고정·`EventDraft.type` 이 `app.db.models.EVENT_TYPES` 부분집합·`PendingResume.to_dict()` 가 발화 원문을 담지 않음(S3.4 13행) / Refs: P5-loop S3.2 S3.4 원칙9
- [ ] U2 **[backend-agent] 인식 단계 — 발화 → `tool_calls` 제안 (LLM 1회)**: `app/agent/propose.py`. `Proposer` Protocol(`propose(utterance, now) -> Proposal`), 공급자 구현은 **`app/er/judge.py` 의 등록표·`select_provider(env)`·`enabled_providers(env)`·`call_with_error_mapping` 을 그대로 재사용**한다(`judge.py` 를 고치지 않는다 — import 만 한다, D11). `PROPOSAL_SCHEMA` 로 `{tool_calls:[{name,args}]}` 구조화 출력을 강제한다 — **여기서는 형식만 본다**(의미 검증·거부는 U3 게이트의 일이다: 두 자리에서 같은 검사를 하지 않는다). 프롬프트는 툴 7종의 이름·용도·인자를 설명하되 **인물은 `person`(언급 문자열)으로 지칭하라고 지시**하고 `person_id` 를 쓰지 말라고 명시한다(강제는 프롬프트가 아니라 U3 게이트가 한다 — 프롬프트 의존 금지, 원칙1). 상대 시간("어제 저녁")은 프롬프트에 `now` 를 주어 **절대 시각으로 받고**, 확정 불가는 결정 K 규약으로 처리한다(P2 04-review 114행이 "'어제 저녁' 해석은 P5" 로 넘긴 항목). `FakeProposer`(표 기반 결정적)로 모든 루프 테스트가 **네트워크 0**으로 돈다. 프롬프트에 키·환경변수·전체 대화 이력을 넣지 않는다(S3.4 13행·security §1). 테스트: 스키마 강제·오류 어휘 6종 매핑·JSON 파싱 실패 처리·키 미노출 / Refs: P5-loop D11 S3.4 원칙7 원칙9
- [ ] U3 **[backend-agent] 게이트 — 제안을 코드가 거른다 (L(iii) 의 안전장치)**: `app/agent/gate.py`. `check(proposal, *, config) -> GateVerdict` 가 ①화이트리스트(`app.tools.TOOL_NAMES` import — 이름 7종을 베껴 쓰지 않는다) ②호출 가능 집합(`search_person`·`ask_user`·`get_briefing` 거부) ③`inspect.signature` 인자 대조 ④`person_id` 금지 ⑤상한(결정 A)을 순서대로 적용하고, 거부는 **실행하지 않고** 사유 어휘와 함께 돌려준다. 루프는 `loop_gate` trace 행에 `{accepted:[{index,name}], rejected:[{index,name,reason}], limits}` 를 남긴다 — 제안 원문은 `loop_extract` output 에만 두고 인덱스로 잇는다(이중 출처 금지). 게이트는 DB·LLM 을 건드리지 않는 **순수 함수**다(테스트가 세션 없이 돈다). 테스트(전부 부정 케이스): `update_person(person_id=3)` 제안 → `person_id_from_llm` 거부·실행 0회 / 툴 7종 밖 이름 → `unknown_tool` / `ask_user`·`search_person`·`get_briefing` → `not_callable_by_llm` / 필수 인자 누락·미지 인자·타입 위반 → `bad_args` / 상한 초과분 → `limit` + `stop_reason="limit"` / 거부 사유가 `loop_gate` output 에 남는다 / Refs: P5-loop S3.2 원칙1 원칙4 원칙9
- [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되묻기 중단·`context` 확장**: `app/agent/loop.py` 의 해석 구간. 통과 제안이 가리키는 언급마다 `app.er.resolve(ctx, mention, utterance, hints)` → `app.er.apply_resolution(ctx, resolution)`. `merge` 면 `person_id` 를 확정 목록에 넣고, `identity`/`new_person` 이면 ER 이 만든 `pending_question_id` 를 받아 **그 턴을 끝낸다**(D2 — sleep/poll 금지). **되묻기 경로에서는 `apply_resolution` 을 부르기 전에** `dataclasses.replace(resolution, ask_payload={**ask_payload, "context": {**ask_payload["context"], "resume": PendingResume(...).to_dict()}})` 로 재개 재료를 얹는다(결정 M-0, 아래 절). `app/er/` 는 고치지 않는다 — `Resolution` 이 frozen dataclass 이므로 `replace` 로 충분하고, `apply_resolution` 은 `kind/question/options/context` 네 키만 뽑아 `ask_user` 에 넘기므로 확장된 `context` 가 `ask_user` 검증을 그대로 지난다. **루프는 `confidence`·`T_merge`·`T_new` 를 읽지도 비교하지도 않는다**(원칙1·2·4). P4b 가 늘린 강등 경로(`forced_reason="penalized_candidate"`, 파일럿 40건에서 되묻기 31건 23.5%)는 **예외가 아니라 정상 경로**이므로 되묻기로 끝나는 턴이 테스트의 기본 케이스다. 테스트: merge 연결·identity 되묻기·new_person 되묻기·`AlreadyApplied` 재적용 거부·루프가 `T_merge` 를 참조하지 않음·확장된 `context["resume"]` 가 저장된 행에서 읽힌다·`LOOP_MAX_RESUME_BYTES` 초과 시 `held_drafts` 를 버리고 `dropped` 수만 남긴다 / Refs: P5-loop D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4
- [ ] U5 **[backend-agent] 기록 + 응답 단계**: 게이트를 통과하고 `person_id` 가 확정된 제안만 실행한다 — `args.person` 을 코드가 `person_id` 로 치환해 `add_event`(`raw_utterance` = 발화 원문 그대로 루프가 주입)·`add_schedule`·`update_person` 을 호출한다. 되묻기로 보류된 언급에 딸린 제안·draft 는 **저장하지 않고** `context["resume"]` 로 넘긴다(결정 D·E). `app/agent/respond.py` 가 결과를 문장으로 만든다(결정 B(i) 템플릿). 응답은 기록된 사실의 요약과 되묻기 선택지뿐이며 **감정·고민에 답하지 않는다**(원칙7 경계 문장 — 부정 테스트 대상). 루프 trace 행(`loop_record`·`loop_turn`)을 남긴다. 테스트: 원문 그대로 저장·확정되지 않은 언급에는 `add_event` 0회·보류 제안이 `resume` 에 실림·응답에 상담성 문장 없음 / Refs: P5-loop S3.2 S3.4 원칙7 원칙9
- [ ] U6 **[backend-agent] `POST /chat` — API 한 흐름**: `app/api/routes.py`·`schemas.py`·`deps.py`. 요청 1건 = 발화 1건 = 턴 1회. 세션 귀속은 결정 I(`X-Session-Id` 없으면 서버가 발급해 응답에 담는다). `get_session()`(요청 단위 commit/rollback)을 **그대로 재사용**하고 툴은 여전히 flush 까지만 한다(P2 결정 2). 루프 예외는 라우트 밖으로 올리지 않고 잡아서 결정 G 의 응답으로 내린다 — 그래야 `loop_error` trace 가 rollback 과 함께 사라지지 않는다(F-4d8d96·F-ca12ad 가 P5 로 넘긴 결정, 결정 H). **삼키는 예외의 범위를 코드와 테스트로 못박는다(R-3)**: 삼키는 것은 `LoopError` 계층·공급자 오류(`judge.py` 오류 어휘 6종)·`ToolError` 계층뿐이고, **`SQLAlchemyError` 는 삼키지 않고 그대로 올린다** — 삼키면 세션이 rollback 필요 상태가 되어 `get_session()` 의 `commit()` 이 `PendingRollbackError` 로 실패하고 trace 까지 잃는다. 테스트: `tests/test_api_chat.py` — `TestClient` + `dependency_overrides[get_session]`(P2 결정 13 과 같은 방식), 한 요청 안에서 저장·응답·`question_id` 반환 / 공급자 오류 → 200 + 저장 0 + `loop_error` 1행 / DB 예외 → 200 이 아니라 그대로 올라간다 / **미답변 질문이 있는 세션에 `/chat` → 200 이고 기존 행의 `answered_at` 이 NULL 로 유지된다(D2 파급 "답 없이 새 발화가 오면 대기 질문 유지, 새 발화 우선", R-4)** / Refs: P5-loop R7 D2 S3.4 원칙9
- [ ] U7 **[backend-agent] 재개 — `POST /answers/{question_id}` 뒤 절반 (R6·R7 을 닫는 단위)**: 답 저장(`answer_question`, 무수정 재사용) **뒤에** 저장된 `context` 로 `resume_turn()` 을 돌린다. `context`·`kind` 는 `app/api/deps.py::load_resume_input` 이 읽어 **값으로** 넘긴다 — `app/agent/` 는 `PendingQuestion` 을 import 하지 않는다(판정 표 부정 grep). 재개 시작 지점은 결정 E(해석 단계부터, 인식 LLM 재호출 없음). `identity` 답 → `context.candidate_ids` 가 가리키는 **그 인물에만** 연결하고 보류 제안을 실행한다. `new_person` 긍정 답 → `ctx.confirmed_question_id` 를 세운 채 `create_person` 을 부르되 **`context.mention` 이 가리키는 대상에만** 쓰고, `relation_tag`·`hierarchy` 는 `context["resume"]["hints"]` 에서 가져온다(미추론 시 처리는 **결정 M-1** — 사용자 결정 대기). `kind="schedule"` 답 → **결정 M-2** 의 변환 규칙으로 `scheduled_at` 을 복원해 `add_schedule`. 부정 답 → 아무것도 만들지 않고 그 사실을 응답·trace(`loop_resume`)에 남긴다(F-b97a06 긍정 답 규약을 루프가 우회하지 않는다). 소비 1회는 결정 J. 테스트: 왕복 2요청 end-to-end(발화 → `question_id` → 답 → 저장·응답), 같은 `question_id` 두 번째 재개 거부(409), `context` 밖 이름으로는 `create_person` 이 일어나지 않음, 만료(24h) 답 거부, 재개로 만든 인물의 별칭에 임베딩이 채워진다(임베더가 설정된 경우) / Refs: P5-loop **R6 R7** D1 D2 S3.4 원칙1
- [ ] U8 **[backend-agent] 수용 기준 기계 검증 + 문서·registry**: **이 단위를 시작하기 전에** `05-remediation.md` 의 [권고] 소견 7건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`)의 원인 분석 칸을 P4b 형식(가설 → 확인 명령 → 확인 결과)으로 채운다(R-2). 그다음 아래 "판정 방법" 표의 모든 명령을 실행해 출력을 `evidence/` 로 남긴다(전체 pytest·허용 파일 diff·`alembic check`·`tools_check.py` 7/7·ER 회귀 3종·curl 왕복·trace 조회·게이트 부정 4행 포함). `docs/wiki/registry.md` — 새 모듈 6·엔드포인트 1·테스트 5는 **행**으로, 고친 기존 파일(`app/api/routes.py`·`schemas.py`·`deps.py`·`app/settings.py`)은 **비고에 P5-loop 한 줄과 커밋 해시를 더한다**(새 행을 만들지 않는다 — F-0ffff5·F-95c6a7 선례). `README.md` 진행 표 P5 행 + 로컬 실행법 한 절(절을 새로 만들지 않고 기존 절에 이어 붙인다). `docs/user-setup/` 은 해당 카드를 갱신한다 / Refs: P5-loop R6 R7 원칙8 원칙9
- [ ] **04-review [verifier] 완료 검토** — 수용 기준 문장·해석·판정 표 전행 대조, 부정 케이스(**LLM 이 준 `person_id` 가 실행되지 않음 / 툴 7종 밖 이름·인자 스키마 위반이 거부됨 / 거부 사유가 trace 에 남음** / 루프가 ER 없이 `create_person` 을 부르지 않음 / `T_merge` 미만 자동 병합 없음 / 동기 대기 없음 / 상담성 응답 없음 / `app/agent/` 가 `PendingQuestion` 을 직접 다루지 않음 / `app/er`·`app/tools`·`app/db` 무변경), `registry.md` 등록, R6·R7 을 닫을 커밋 해시 제안. 판정은 verifier 만 한다(L-002) / Refs: P5-loop R6 R7 D1 D2

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개

해석(기계 판정 방법, 위 한 줄을 바꾸지 않는다):

  - "**에이전트 루프(인식→해석→기록→응답)**" → `app/agent/loop.py` 의 `run_turn()` 이 네 단계를 순서대로 돌고, 한 턴의 `agent_traces` 행에 **네 단계가 모두** 나타난다 — 인식은 `loop_extract`(LLM 제안) + `loop_gate`(코드 게이트) 두 행으로 나뉜다(결정 F 의 step 어휘 6종). 판정: 표 3·7행.
  - "**발화 →**" → 입력은 `POST /chat` 요청 본문의 발화 문자열 **하나**다. 여러 요청으로 나눠 넣지 않는다. 판정: 표 3행(HTTP 테스트)·8행(curl).
  - "**툴 선택**" → **LLM 이 고르고 코드가 거른다**(결정 L(iii), `docs/proposal.md` 72행). 그 턴의 `agent_traces` 에 (a) LLM 이 제안한 `tool_calls` 가 `loop_extract` output 에, (b) 게이트의 통과·거부와 사유가 `loop_gate` output 에, (c) 실제 실행이 `tool_name` ∈ 툴 7종인 `tool_call` 행으로 **1건 이상** 남고, (c) 의 집합이 (b) 의 `accepted` 집합과 일치한다(원칙9). 판정: 표 7행(제안·거부·실행을 한 조회로 본다).
  - "**저장**" → 같은 요청 안에서 `events`(또는 `schedules`·`person_aliases`) 행이 실제로 늘어난다 — 응답 문자열만 바뀌는 것은 저장이 아니다. 판정: 표 3·8행(요청 전후 행 수 조회).
  - "**응답**" → `ChatOut.reply` 가 비어 있지 않고, 되묻기로 끝난 턴이면 `question_id` 와 `options` 가 함께 온다. 판정: 표 3·4행.
  - "**API 한 흐름으로 동작**" → 위 넷이 **HTTP 요청 1건** 안에서 끝난다(중간에 클라이언트 왕복이 없다). 되묻기는 예외가 아니라 정의상 그 턴의 끝이다(D2). 판정: 표 8행의 curl 1회.
  - "**`POST /answers/{question_id}`로 루프 재개**" → 그 요청 **하나**로 (a) 답이 저장되고, (b) 저장된 `context` 로 해석·기록이 이어지고, (c) 그 결과가 응답에 담긴다. 답만 저장되고 아무것도 기록되지 않으면 미충족이다(그것이 P2 의 상태다). 판정: 표 4·8행.
  - "**의존: … P4b 게이트 통과**" → `docs/wiki/packages/P4b-er-redesign/04-review.md` 의 `결과: 완료` 와 `1075dd6`. 판정: 표 17행.
  - 덧붙여, 이 패키지가 **닫는다고 선언한 R6·R7**(review-index 14·15행의 "P2-tools, **P5-loop**")은 04-review 가 별도 항목으로 확인한다 — R6 은 "루프가 확인 없이 `create_person` 을 부르지 않는다"(표 5·6행), R7 은 "턴 N+1 뒤 절반"(표 4행).

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

로컬 컨테이너는 5433 이므로 포트를 셸 변수로 넘긴다(`.env` 는 스크립트가 읽지 않는다 — security §1, 로드 주체는 사용자 셸이다). `open()`·한글 출력이 섞인 한 줄 명령에는 Windows cp949 대비로 `PYTHONUTF8=1` 을 앞에 둔다(P4 U7·P4b 실측).

| # | 무엇 | 명령 | 기대 출력 |
|---|------|------|-----------|
| 1 | 전체 테스트 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 1325(`1227026` 기준) + 신규 전부 통과, 실패 0·skip 0 |
| 2 | 네트워크 0 | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_propose.py tests/test_agent_gate.py tests/test_agent_loop.py tests/test_agent_resume.py tests/test_api_chat.py -q` | 전부 통과. 실 LLM·실 임베딩 호출 0(`FakeProposer`·`FakeJudge`·스텁 임베더) |
| 3 | 한 흐름 | `POSTGRES_PORT=5433 python -m pytest tests/test_api_chat.py -q -k "one_flow or end_to_end"` | 통과 — 요청 1건 안에서 `events` 행 +1 이상, `ChatOut.reply` 비어 있지 않음 |
| 4 | 재개 | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_resume.py -q -k "resume"` | 통과 — `POST /answers/{id}` 요청 1건 뒤 `persons`/`events` 행 증가, 두 번째 재개는 409 |
| 5 | 부정: ER 없는 인물 생성 | `grep -rn "create_person\|update_person" app/agent/` | `app/agent/loop.py` 의 **재개 경로 1곳**에서만 호출되고 그 앞줄에 `ctx.confirmed_question_id` 대입이 있다. 인식·기록 단계에는 0건 |
| 6 | 부정: 임계치 재판정 없음 | `grep -rn "T_merge\|t_merge\|T_new\|t_new\|confidence" app/agent/` | **0건**(루프는 확신도·임계치를 읽지도 쓰지도 않는다 — 원칙1·2·4). 주석·docstring 도 포함이다: 설명이 필요하면 한국어 "확신도"로 쓴다. `context` 안의 `confidence_breakdown` 은 ER 이 만든 dict 를 **키 이름을 적지 않고** 통째로 넘기므로 걸리지 않는다. 잡히면 미충족 |
| 7 | trace: 제안·게이트·실행 | `PYTHONUTF8=1 POSTGRES_PORT=5433 python -c "import json; from app.db.session import SessionLocal; from app.tools.context import ToolContext; from app.agent import run_turn; from app.agent.propose import FakeProposer; from sqlalchemy import text; s=SessionLocal(); ctx=ToolContext(session=s, session_id='judge-row7', user_id='local'); r=run_turn(ctx, '어제 민수랑 저녁 먹었어', proposer=FakeProposer()); s.commit(); rows=s.execute(text('SELECT step, tool_name, output FROM agent_traces WHERE session_id=:s ORDER BY id'), {'s': r.session_id}).all(); print([(a,b) for a,b,_ in rows]); print(json.dumps([c for a,b,c in rows if a in ('loop_extract','loop_gate')], ensure_ascii=False))"` | 첫 줄: `loop_extract`·`loop_gate`·`loop_resolve_done`·`loop_record`·`loop_turn` 이 모두 있고, `tool_name` 이 툴 7종 중 하나인 `tool_call` 행 1건 이상, ER 행(`er`/`er_resolve`) 1건 이상. 둘째 줄: `loop_extract.output.tool_calls[]`(LLM 이 **제안**한 툴)과 `loop_gate.output.{accepted,rejected}`(코드가 **거른** 결과 + 사유)가 보이고, `accepted` 의 툴 이름 집합 = 첫 줄 `tool_call` 행의 `tool_name` 집합 |
| 8 | 수동 왕복(사용자) | `uvicorn app.main:app --port 8000` 뒤 ① `curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"utterance":"..."}'` ② `curl -X POST http://127.0.0.1:8000/answers/<id> -H "Content-Type: application/json" -d '{"answer":"<옵션>"}'` | ①에서 `question_id`·`options`·`session_id` 수신, ②에서 저장 결과가 응답에 포함. 두 응답 전문을 evidence 로. **②에 `X-Session-Id` 를 넣지 않는다** — `build_ctx` 가 답할 행의 `session_id` 를 권위로 쓴다(P2 결정 12). `-H` 를 빼면 FastAPI 가 422 를 낸다(R-1) |
| 9 | 동기 대기 없음(D2) | `grep -rnE "time\.sleep\|asyncio\.sleep\|while True" app/agent/ app/api/` | **0건** |
| 10 | 허용 파일 | `git diff --name-only 1227026..HEAD -- app/` | `app/agent/*` + `{app/api/routes.py, app/api/schemas.py, app/api/deps.py, app/settings.py}` 의 **부분집합**. `app/er/`·`app/tools/`·`app/db/`·`app/main.py` 가 나오면 미충족 |
| 11 | 스키마 무변경 | `POSTGRES_PORT=5433 python -m alembic check` | `No new upgrade operations detected.` |
| 12 | 툴 시그니처 무변경 | `python scripts/tools_check.py` | `7/7 ok` |
| 13 | ER 회귀 3종 유지 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -k "promotion or aunt or homonym"` | `3 passed` |
| 14 | 데이터·평가 산출물 무변경 | `git diff --name-only 1227026..HEAD -- data/ reports/` | **0줄** |
| 15 | 비밀 미노출 | `grep -rniE "api_key\|secret\|password\|OPENAI_\|ANTHROPIC_\|GEMINI_" app/agent/` | 환경변수 **이름**을 값과 함께 찍는 코드 0건. 프롬프트·`context`·응답·trace 에 키 문자열 0건 |
| 16 | registry 등록 | `grep -n "app/agent/" docs/wiki/registry.md` | 새 모듈 행이 전부 있고, 고친 기존 파일은 **비고 확장**(새 행 아님) |
| 17 | 의존 게이트 | `grep -n "^결과:" docs/wiki/packages/P4b-er-redesign/04-review.md` | `결과: 완료` |
| 18 | 부정: 상담성 응답 없음(원칙7) | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_loop.py -q -k "no_counseling or scope"` | 통과 — 감정·고민 발화에 공감·조언 문장을 만들지 않고 기록 요약만 돌려준다 |
| 19 | **부정: LLM 이 준 `person_id` 는 실행되지 않는다**(L(iii) 의 핵심 방어) | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_gate.py -q -k "person_id_from_llm"` | 통과 — `update_person(person_id=3)` 제안이 `GateVerdict.rejected` 로 가고 `app.tools.update_person` 호출 **0회**(spy), `reason == "person_id_from_llm"` |
| 20 | **부정: 화이트리스트** | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_gate.py -q -k "unknown_tool or not_callable"` | 통과 — 툴 7종 밖 이름은 `unknown_tool`, `ask_user`·`search_person`·`get_briefing` 제안은 `not_callable_by_llm` 으로 거부(실행 0회) |
| 21 | **부정: 인자 스키마** | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_gate.py -q -k "bad_args"` | 통과 — 필수 인자 누락·미지 인자·타입 위반·`add_event.type` 고정 집합 위반이 모두 `bad_args` 로 거부 |
| 22 | **거부 사유가 trace 에 남는다** | `PYTHONUTF8=1 POSTGRES_PORT=5433 python -c "<표 7행과 같은 방식으로 거부 섞인 제안 1턴 실행 후> SELECT output FROM agent_traces WHERE session_id=:s AND step='loop_gate'"` | `rejected[]` 에 `{index, name, reason}` 이 거부 수만큼 있고, 같은 턴의 `tool_call` 행 수 = `accepted` 수 |
| 23 | 부정: 루프가 `pending_questions` 를 직접 쓰지 않는다 | `grep -rnE "PendingQuestion\|flag_modified\|\.context *=" app/agent/` | **0건** — `context` 확장 경로는 `dataclasses.replace(resolution, …)` → `apply_resolution` → `ask_user` 하나뿐이다(S3.2 16행 "모든 툴 호출은 agent_traces 에 기록"을 우회하지 않는다) |
| 24 | `context` 크기 상한(S3.4 13행) | `POSTGRES_PORT=5433 python -m pytest tests/test_agent_loop.py -q -k "resume_size"` | 통과 — `LOOP_MAX_RESUME_BYTES` 를 넘으면 `held_drafts` 를 버리고 `dropped` 수만 남기며, 저장된 `context` 에 전체 대화 이력이 없다(발화 원문은 ER 이 넣은 `utterance` 1건뿐) |
| 25 | 대기 질문 유지(D2 파급, R-4) | `POSTGRES_PORT=5433 python -m pytest tests/test_api_chat.py -q -k "pending_survives"` | 통과 — 미답변 질문이 있는 세션에 `/chat` → 200, 기존 행 `answered_at` NULL·status `pending` 유지 |
| 26 | DB 예외는 삼키지 않는다(R-3) | `POSTGRES_PORT=5433 python -m pytest tests/test_api_chat.py -q -k "db_error"` | 통과 — `SQLAlchemyError` 는 200 으로 내리지 않고 그대로 올라간다(`get_session` 의 `commit()` 이 `PendingRollbackError` 로 실패하는 것을 막는다) |
| 27 | 재개로 만든 인물의 별칭 임베딩 | `PYTHONUTF8=1 POSTGRES_PORT=5433 python -c "<재개 1회 실행 후> SELECT alias, (embedding IS NOT NULL) FROM person_aliases WHERE person_id=:p"` | 임베더가 설정된 환경에서 **전부 `True`** — `build_ctx` 의 `embedder=None` 을 재개 경로가 그대로 쓰면 새 인물이 이후 후보 검색에서 보이지 않는다 |

- 증거 경로: `docs/wiki/packages/P5-loop/evidence/`. Docker Desktop 이 꺼져 있거나 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security §6).
- 7·22·27행의 한 줄 명령은 조회 대상이 이미 고정돼 있어 지금 적을 수 있다 — `agent_traces(session_id, step, tool_name, output)` 은 `S3.1` 로, 세션 id 는 결정 I(i) 의 `ChatOut.session_id` 로 확정됐다(02-plan-verify H-1). 구현 시점에 달라지는 것은 `<…>` 로 표시한 **입력 발화와 인물 id 뿐**이며, 실제로 친 명령과 출력을 03-log·`evidence/` 에 그대로 남긴다.

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| registry 행 | 무엇 | 이 패키지가 어떻게 쓰는가 |
|---|---|---|
| 55~61 `app/tools/*` (툴 7종, `4eca3e9`~`7c94aad`) | `search_person`·`create_person`·`update_person`·`add_event`·`add_schedule`·`get_briefing`·`ask_user` | **무수정 호출**. 루프는 호출자다. `get_briefing` 은 이 패키지에서 부르지 않는다(P6-briefing) |
| 60 `app/tools/questions.py` | `answer_question`·`list_pending`·`question_status` | **무수정 호출**. 재개는 `answer_question` 앞에 끼어들지 않고 **뒤에** 붙는다. 1회 소비는 이 함수의 `already_answered` 가 강제한다(결정 J) |
| 85 `app/er/pipeline.py` (`d6e5949`·`cc5d24f`·`dbcfca0`) | `resolve()`·`apply_resolution()` | **무수정 호출**. 이것이 루프의 유일한 인물 해석 진입점이다. `AlreadyApplied`·`Resolution.trace_id` 규약을 그대로 따른다 |
| 78~85 `app/er/*` 나머지 | 후보검색·규칙·확신도·판정 | **무수정**(P4b 게이트 수치 보호, 원칙8). 루프는 import 조차 최소로 한다 |
| 84 `app/er/judge.py` (`c01381d`·`cf01e9f`) | `select_provider`·`enabled_providers`·`call_with_error_mapping`·`JUDGES` | **무수정 재사용**(import). 인식 단계의 공급자 선택·오류 어휘를 새로 만들지 않는다(D11) |
| 55 `app/tools/__init__.py` | `TOOL_NAMES`(툴 7종 이름) | **무수정 import**. 게이트 화이트리스트의 **단일 출처** — 이름 7개를 `gate.py` 에 베껴 쓰지 않는다 |
| `scripts/tools_check.py` (`P2-tools`, R10) | CLAUDE.md 표 ↔ `inspect.signature` 대조 | 게이트의 인자 검증이 **같은 출처**(`inspect.signature(app.tools.<name>)`)를 쓴다. 시그니처가 바뀌면 이 스크립트와 게이트가 **함께** 깨져야 정상이다 |
| 83 `app/er/types.py` | `Resolution`(`@dataclass(frozen=True)`, 193행) | **무수정**. `dataclasses.replace` 로 `ask_payload` 만 바꾼 **새 객체**를 만들어 `apply_resolution` 에 넘긴다 — ER 코드를 고치지 않고 `context` 를 확장하는 유일한 길(H-2) |
| 57 `app/tools/context.py` (`4eca3e9`) | `ToolContext`·`traced(tool_name, step=...)`·`to_jsonable` | **무수정 재사용**. `step` 인자가 이미 있어 루프 step 어휘를 그대로 얹을 수 있다(P3-er 가 `er_resolve` 로 연 길) |
| 65 `app/api/routes.py` (`4d5817e`) | `GET /health` · `POST /answers/{question_id}` | **갱신해 재사용**. `/chat` 을 같은 라우터에 더하고 `/answers` 는 **확장**한다 — 재개용 라우트를 새로 만들지 않는다(그러면 S3.4 8행과 어긋난다) |
| 64 `app/api/deps.py` (`4d5817e`) | `get_session()`·`build_ctx()` | **갱신해 재사용**. `build_ctx` 의 결정 12 규약(답할 행의 `session_id` 권위)은 **그대로 두고** 채팅용 조립만 옆에 둔다 |
| 66 `app/api/schemas.py` (`4d5817e`) | `AnswerIn`·`AnswerOut`·`HealthOut` | **갱신해 재사용**(`AnswerOut` 확장 + `ChatIn`/`ChatOut` 추가). `app/tools/types.py` 의 `*Out` dataclass 와 섞지 않는다(P2 결정 11) |
| 44 `app/db/models.py` | `EVENT_TYPES`·`QUESTION_KINDS`·`AgentTrace`·`PendingQuestion` | **무수정 재사용**. 어휘를 루프에 베껴 쓰지 않고 import 한다 |
| 76 `tests/test_api.py` (`4d5817e`) | `TestClient` + `dependency_overrides` 패턴 | 같은 패턴으로 `tests/test_api_chat.py` 를 쓴다. 기존 파일은 `AnswerOut` 확장분만 갱신 |
| `data/scenarios/` 40건 | 파일럿 데이터셋 | **읽기 전용·이번 범위 밖**. 루프를 이 데이터로 재는 것은 P10 |
| `README.md` 진행 표·실행법 절 | 문서 | 절을 새로 만들지 않고 이어 붙인다(F-0ffff5 선례) |

## 리스크 · 미결

**사용자 결정 — 12건 확정. 그중 L 은 02-plan-verify(H-3) 뒤 `(i)` → `(iii)` 로 바뀌었다. U1 은 이 확정을 전제로 착수한다. 아래 미결 M-1 은 U7(재개), M-2 는 U5(질문 생성)·U7(답 변환)에서 필요하다 — U1~U4 는 막지 않지만 그 전에는 정해져야 한다.**

> 확정: **A(i)** 추출 개수 상한(언급 5·이벤트 5·일정 3, 초과분은 알린다) · **B(i)** 응답은 템플릿 · **C(i)** 순차 처리, 첫 되묻기에서 턴 종료 · **D(i)** 되묻기로 끝나도 되돌리지 않는다 · **E(i)** 재개는 해석 단계부터(인식 LLM 재호출 없음) · **F(i)** `tool_name="agent"` + `loop_` 접두사 **6종**(초안 5종 + `loop_gate`, 아래 결정 F 보강) · **G(i)** 한 줄 안내 + 저장 0 + `loop_error` · **H(i)** 예외를 삼켜 200 으로 끝내 같은 트랜잭션에 커밋(별도 커넥션 없음) · **I(i)** 헤더 없으면 서버가 `uuid4` 발급, 격리 부재는 명시만 · **J(i)** 소비 1회는 `answer_question` 의 409 에 맡기고 대상은 `context["mention"]` 으로 바인딩 · **K(i)** 이벤트는 `now`, 일정은 `ask_user(kind="schedule")` · **L(iii) 하이브리드 — LLM 이 `tool_calls` 를 제안하고 코드가 게이트로 강제한다(구조화 출력 1회, 다회 왕복 아님).**
>
> **L 을 (i) 에서 (iii) 으로 바꾼 이유(사용자 결정).** `docs/proposal.md` 3.1 절 제목이 "툴 정의 (**Function Calling**)" 이고 72행이 "**파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다**", 176행이 지표로 "**툴 호출 정확도 | 올바른 툴을 선택한 비율**" 을 든다. (i) 코드 매핑은 그 72행이 말하는 "파이프라인 하드코딩" 에 해당하고, 176행의 지표는 **잴 대상(선택 행위)을 잃는다**. (iii) 은 기획서를 지키면서 오병합 방어를 프롬프트가 아니라 **코드(게이트)** 에 남긴다 — `person_id` 는 여전히 `resolve()` → `apply_resolution()` 을 거쳐서만 얻는다(원칙1·4). LLM 호출은 여전히 **턴당 1회**(구조화 출력 한 번에 목록을 받는다)이므로 (i) 의 비용·재현성 논거(원칙8)가 그대로 유지된다.
>
> **E 는 사용자가 상세 설명을 요구해 근거를 확인한 뒤 확정했다.** E 의 근거: 재개 때 인식을 다시 부르면 사용자가 답한 질문과 실제로 저장되는 것이 어긋날 수 있다 — P4b 04-review 가 실행 간 `s_llm` 자기보고 136 중 60건 불일치를 기록했다. H 의 근거: 커넥션을 둘로 나누면 "저장은 롤백됐는데 trace 엔 성공이 남는" 불일치가 생긴다. J 의 근거: `_require_confirmation` 의 6검사(`app/tools/persons.py` 266~310행)는 질문의 실재·kind·answered·세션·긍정만 보고 **무엇을 만드는지는 보지 않으며**, 통과한 질문에 소비 표시도 남기지 않는다 — 대상 바인딩은 `context` 가, 소비 1회는 409 가 닫는다.
>
> **backlog 개정 3건도 사용자가 승인했다**(아래 "backlog 개정 제안" 절 1·2·3 전부) — 메인 세션이 반영한다.

**결정 항목 원문 (근거·대안 비교는 그대로 남긴다)**

- **[확정 (i)] 결정 A — 한 턴의 상한과 초과 시 동작.**
  (i) **권장 — 인식 단계가 뽑을 수 있는 수에 상한을 두고, 초과분은 조용히 버리지 않고 알린다**: `LOOP_MAX_MENTIONS = 5` · `LOOP_MAX_EVENTS = 5` · `LOOP_MAX_SCHEDULES = 3`(`app/settings.py` 상수 + 환경변수 오버라이드). 상한을 넘으면 앞에서부터 상한까지만 처리하고 `TurnResult.stop_reason="limit"` 와 trace 에 버린 수를 남기며 응답에 "일부만 기억했다"는 한 줄을 붙인다. **툴 호출 횟수 자체는 상한을 두지 않는다** — 이 설계에서는 호출 수가 `1(인식) + 언급 수(ER) + 기록 수` 로 상한에서 파생되므로 별도 예산을 두면 같은 것을 두 번 세게 된다. 근거: 비용·무한 루프 방지는 필요하지만, 상한을 "툴 호출 n회"로 걸면 어느 단계가 잘렸는지 사용자·trace 가 알 수 없다.
  **[L(iii) 반영 — 결정을 바꾸지 않는다]** 상한의 **적용 지점**만 옮겨 적는다: 이제 5·5·3 은 게이트가 **LLM 제안 목록**에 적용한다(언급 = 서로 다른 `args.person` 값의 수, 이벤트 = `add_event` 제안 수, 일정 = `add_schedule` 제안 수). 초과분은 `limit` 사유로 거부되고 `stop_reason="limit"` + 응답 한 줄은 그대로다. 별도 툴 호출 예산을 두지 않는 근거도 그대로다 — **다회 왕복이 아니므로**(LLM 1회) 호출 수가 제안 수 상한에서 파생된다.
  (ii) 툴 호출 예산제(`LOOP_MAX_TOOL_CALLS=12`, 초과 시 즉시 중단): LLM 이 툴 결과를 받아 다시 호출하는 **다회 왕복**(결정 L(ii))이라면 필수지만, 제안 1회 + 게이트 상한으로는 같은 것을 두 번 세게 된다.
  (iii) 상한 없음: 발화 하나가 인물 30명을 말하면 LLM·DB 호출이 폭발한다. 비권장.
- **[확정 (i)] 결정 B — 응답 문장을 LLM 이 쓰는가, 템플릿인가.**
  (i) **권장 — 템플릿(결정적 문자열 조립)**: 저장된 것(인물명·이벤트 종류·일정)과 되묻기 선택지를 정해진 틀에 끼운다. 근거: ① 원칙7 경계(상담 아님)를 **구조적으로** 보장한다 — 템플릿은 공감·조언을 만들 수 없다, ② LLM 호출이 턴당 1회(인식)로 유지돼 비용·지연이 예측 가능하다, ③ 평가(P10)가 응답을 문자열로 대조할 수 있다(원칙8 재현성), ④ 되묻기 질문 문장은 이미 `app/er/pipeline.py::_build_ask_payload` 가 만들고 있어 루프가 또 만들면 두 자리가 된다.
  (ii) LLM 문장화(턴당 2회 호출): 자연스럽지만 비용 2배, 비결정적, 그리고 **원칙7 경계를 프롬프트로만 지키게 된다** — 감정 발화에 공감 문장이 새어 나오는 것을 테스트로 막기 어렵다.
  (iii) 하이브리드(템플릿 + 선택적 LLM 다듬기): 두 경로를 다 테스트해야 하고 플래그가 하나 는다. 데모 품질이 문제가 되면 P8·P10 에서 다시 꺼낸다.
- **[확정 (i)] 결정 C — 한 발화에 인물·사건이 여럿일 때.**
  (i) **권장 — 순차 처리, 첫 되묻기에서 턴 종료**: 언급을 인식 순서대로 처리하다 되묻기가 나오면 그 자리에서 턴을 끝내고, **아직 처리하지 않은 언급·draft 를 `pending_questions.context` 에 실어** 재개 때 이어서 한다. 근거: D2 가 "ask_user 는 그 턴을 종료한다"고 못박았고, 한 턴에 질문 여러 개를 띄우면 프론트 칩이 어느 질문에 대한 답인지 사용자에게 모호해진다(S3.4 "확인 칩 = 미답변 pending_questions").
  (ii) 전부 처리하고 되묻기를 여러 개 쌓는다: 왕복 수가 줄지만 `context` 마다 부분 상태가 생겨 재개 순서·중복 저장 관리가 급격히 어려워진다. 되묻기가 23.5%(P4b 실측)인 이 제품에서는 한 턴에 질문 2개 이상이 흔해진다.
  (iii) 되묻기 대상만 건너뛰고 나머지는 계속: (ii)의 절반짜리 변형으로, "건너뛴 언급의 이벤트를 누구에게 붙이나"가 그대로 남는다.
- **[확정 (i)] 결정 D — 되묻기로 턴이 끝났을 때 이미 한 저장을 되돌리는가.**
  (i) **권장 — 되돌리지 않는다(커밋)**: 이미 `merge` 로 확정된 언급의 별칭 누적과 그 인물에 붙는 이벤트는 그대로 저장하고, **미확정 언급에 딸린 draft 만 저장을 보류**해 `context` 로 넘긴다. 근거: ① 되돌리면 `ask_user` 가 만든 `pending_questions` 행 자체가 같은 트랜잭션에서 사라져 **질문이 없어진다**(치명), ② 확정된 판정을 무르는 것은 원칙9 의 기록 보존과 반대 방향, ③ 롤백하면 `agent_traces` 도 함께 사라진다(F-4d8d96).
  (ii) 턴 전체 롤백 후 재개 때 처음부터: 일관성은 단순해지지만 (i)의 ①이 설계상 불가능하게 만든다(질문을 저장하려면 커밋해야 한다).
  (iii) 확정분도 보류했다가 재개 때 한꺼번에: `context` 가 커지고(S3.4 "재개에 필요한 것만") 재개가 실패하면 확정분까지 잃는다.
- **[확정 (i)] 결정 E — 재개 시 어디부터 다시 하는가.**
  (i) **권장 — 해석 단계부터. 인식 LLM 을 다시 부르지 않는다**: `context` 에 실린 `mention`·`candidate_ids`·`confidence_breakdown`·보류 draft 로 해석·기록·응답만 돌린다. 근거: ① 같은 발화를 두 번 추출하면 비용이 2배이고 **결과가 달라질 수 있다**(P4b 04-review 가 실행 간 `s_llm` 자기보고가 136 mention 중 60건 달랐다고 기록했다 — LLM 재호출은 재현성의 적이다), ② S3.4 13행이 `context` 에 "재개에 필요한 것"을 넣으라고 이미 지시한다.
  (ii) 인식부터 다시: 발화 원문만 저장하면 되어 `context` 가 작아지지만 ①의 비결정성을 그대로 받는다.
  (iii) 기록 단계부터(해석도 건너뛰기): `identity` 답은 사용자가 후보를 고른 것이므로 해석이 남아 있지 않다고 볼 수도 있으나, `new_person` 답은 `create_person` 이라는 해석 행위가 남아 있어 단계를 건너뛸 수 없다.
- **[확정 (i)] 결정 F — `agent_traces.step` 어휘와 `tool_name`.**
  (i) **권장 — `tool_name="agent"`, step 5종**: `loop_extract`(인식 결과) · `loop_resolve_done`(해석 요약: 언급별 결정) · `loop_record`(기록: 어떤 draft 를 어느 툴로) · `loop_turn`(턴 요약: 발화·응답·`stop_reason`) · `loop_resume`(재개 진입). 오류는 기존 `tool_error` 를 쓰지 않고 `loop_error` 로 따로 둔다(결정 G·H).
  **[L(iii) 반영 — 결정을 뒤집지 않고 한 종을 더한다: step 6종]** `loop_gate` 를 더한다. **이름 5종은 그대로 두고**(F 를 다시 열지 않는다) `loop_extract` 의 output 이 담는 것만 "추출 결과"에서 "**LLM 이 제안한 `tool_calls[]` 원문**"으로 바뀐다. 새 step 을 더한 근거: ① 기존 step 의 output 에 거부를 끼워 넣으면 P10 이 "툴 호출 정확도"·거부율을 재려고 **JSON 안쪽을 파고들어야** 하지만, 별도 step 이면 `SELECT output FROM agent_traces WHERE step='loop_gate'` 한 줄로 분모(제안 수)와 분자(통과 수)가 나온다(`docs/proposal.md` 176행). ② **거부는 오류가 아니라 정상 단계**다 — `loop_error`(결정 G·H)에 섞으면 "실패한 턴"과 "LLM 이 잘못 제안했지만 코드가 막아 정상 종료한 턴"을 구별할 수 없다. ③ 접두사 `loop_` 규약과 "한 단계 = 한 행"이라는 (i) 의 원칙을 그대로 지킨다 — (iii) 이 버린 "네 단계를 지났음을 증명할 수 없다"는 문제로 돌아가지 않는다. output 스키마: `{accepted:[{index,name}], rejected:[{index,name,reason}], limits:{mentions,events,schedules}}`. 제안 **인자 값**은 `loop_extract` 에만 두고 여기서는 인덱스로 가리킨다(이중 출처 금지, 원칙9 의 "근거는 한 곳에"). 근거: P3-er 가 `tool_name="er"`·`step="er_resolve"` 로 **툴 아닌 단계**를 `agent_traces` 에 넣는 선례를 이미 만들었고(`agent_traces.tool_name` 은 NOT NULL 이라 값이 필요하다 — P2 01-plan 미결 1), 접두사 `loop_` 하나로 `git`·SQL 양쪽에서 루프 행만 뽑을 수 있다.
  (ii) 기존 `tool_call`/`tool_error` 어휘에 합치기: 행이 섞여 "툴이 실제로 불린 것"과 "루프가 단계를 지난 것"을 구별할 수 없다 — 수용 기준 해석의 "툴 선택" 판정이 불가능해진다.
  (iii) step 을 단계당 1종(`loop`)으로 줄이기: 행은 줄지만 네 단계를 모두 지났다는 것을 증명할 수 없다(표 7행).
- **[확정 (i)] 결정 G — 실패·타임아웃 시 사용자에게 무엇을 보이는가.**
  (i) **권장 — 200 + "지금은 기억하지 못했어요" 한 줄 + 저장 0 + `loop_error` trace**: 인식 LLM 이 `timeout`/`rate_limit`/`api_error`/`schema`(judge.py 오류 어휘 6종 그대로)로 실패하면 발화는 버리지 않고 **아무것도 저장하지 않은 채** 실패를 알린다. 예외 코드·공급자명·프롬프트는 응답에 담지 않고 trace 에만 어휘(`timeout` 등)로 남긴다(security §1). HTTP 상태는 **200**이다 — 결정 H 참고.
  (ii) 5xx 로 올린다: HTTP 의미로는 정직하지만 `get_session()` 이 rollback 해 `loop_error` trace 까지 사라진다(F-4d8d96) — 원칙9 와 정면 충돌.
  (iii) 부분 저장 후 실패 알림: 인식이 실패하면 저장할 draft 자체가 없으므로 해당 없음. 해석·기록 중간 실패는 결정 D(i) 가 이미 답한다(확정분 유지).
- **[확정 (i)] 결정 H — 오류 trace 를 별도 커넥션으로 남길 것인가 (P2 가 P5 에 명문 인계한 결정, F-4d8d96·F-ca12ad).**
  (i) **권장 — 별도 커넥션을 쓰지 않는다. 대신 루프가 예외를 삼켜 정상 종료한다**: 라우트가 200 으로 끝나면 `get_session()` 이 commit 하므로 `loop_error` 행이 그대로 남는다. 근거: 별도 커넥션·자동 커밋은 트랜잭션 경계가 두 개가 되어 "저장은 롤백됐는데 trace 는 성공으로 남는" 더 나쁜 불일치를 만든다. `app/tools/context.py` 29~31행이 "이 한계를 지금 여기서 우회로 고치지 않는다 — P5-loop 01-plan 이 결정한다"고 적어 둔 그 결정이다.
  (ii) 별도 커넥션으로 오류 trace 즉시 커밋: 어떤 경우에도 기록이 남지만 커넥션 관리·테스트 픽스처가 복잡해지고 위 불일치가 생긴다.
  (iii) 현행 유지(아무것도 하지 않음): 운영에서 오류 trace 가 사라지는 상태가 그대로 간다 — 원칙9 위반 상태를 P5 가 넘기면 닫을 패키지가 없다.
- **[확정 (i)] 결정 I — 세션 귀속(`X-Session-Id`)과 사용자 격리(F-fbaaae).**
  (i) **권장 — 헤더가 있으면 그 값, 없으면 서버가 `uuid4` 로 발급해 `ChatOut.session_id` 로 돌려준다. `user_id` 는 `app_user_id()` 고정**: 형식 검증(길이·문자 집합)을 하고 어긋나면 422. 다중 사용자 격리는 **하지 않고** `pending_questions`·`agent_traces` 에 `user_id` 컬럼이 없다는 사실을 모듈 docstring·README 에 명시한다(스키마 변경은 이 패키지 범위 밖). 근거: P2 04-review 107행이 "`X-Session-Id` 헤더 규약은 채팅 엔드포인트가 정한다"고 P5 에 넘겼고, 110행은 격리 부재를 "세션→사용자 귀속 계층이 필요"로 남겼다 — 단일 사용자 제품(로컬 `app_user_id()`)에서는 명시가 곧 조치다.
  (ii) 스키마에 `user_id` 컬럼을 더해 진짜 격리: 마이그레이션 + `alembic check` 무변경 증거 포기 + S3.1 변경. 범위 이탈.
  (iii) 세션 개념 없이 전역 단일 세션: trace·질문이 전부 한 세션에 섞여 P10 의 세션 단위 분석이 불가능해진다.
- **[확정 (i)] 결정 J — 확인 질문의 1회 소비와 대상 바인딩 (R6 의 꼬리).**
  (i) **권장 — 소비 1회는 `answer_question` 의 `already_answered`(409)에 맡기고, 대상 바인딩은 `context` 로 강제한다**: 재개 경로는 `pending_questions.context["mention"]`·`["candidate_ids"]` 가 가리키는 대상에만 `create_person`/`update_person` 을 호출하고, 그 밖의 이름으로는 호출하지 않는다(부정 테스트). 같은 `question_id` 로 두 번째 `POST /answers` 가 오면 409 이므로 **재개도 자동으로 1회**다. 근거: ER 이 이미 `context` 에 `mention`·`candidate_ids` 를 넣어 두었고(`_build_ask_payload` 186행이 "P5 가 메울 재료"라고 적었다), 새 컬럼 없이 P2 04-review 108행의 구멍을 닫을 수 있다.
  (ii) `pending_questions` 에 `consumed_at` 컬럼 추가: 뜻은 분명해지지만 스키마 변경(범위 밖)이고 `answered_at` 과 사실상 중복이다.
  (iii) 루프 메모리에 소비 여부 보관: 재시작에 사라진다 — D2 가 인메모리 대기를 버린 이유와 같다.
- **[확정 (i)] 결정 K — 시각 확정 실패와 `ask_user(kind="schedule")`.**
  (i) **권장 — 이벤트는 `occurred_at` 을 확정 못 하면 `now` 로 두고 그 사실을 trace 에 남기고, 일정은 `scheduled_at` 이 확정되지 않으면 `add_schedule` 을 부르지 않고 `ask_user(kind="schedule")` 로 되묻는다**: 근거: ① 이벤트는 "언제"가 틀려도 사실 자체는 남기는 편이 낫다(미검출이 오병합보다 낫다는 원칙1 의 방향과 같다), ② 일정은 시각이 틀리면 **브리핑이 틀린 때 뜬다** — 되묻는 편이 싸다, ③ `QUESTION_KINDS` 에 `schedule` 이 이미 있고 P4 04-review 214행이 "`ask_user(kind=schedule)` 은 P5 루프가 만든 뒤 P10 이 잰다"고 명시했다 — 이 패키지가 만들지 않으면 그 kind 는 영영 n=0 이다.
  (ii) 일정도 `now` 기준 추정으로 저장: 되묻기가 줄지만 틀린 일정이 조용히 쌓인다.
  (iii) `schedule` 되묻기를 P6-briefing 으로 미룸: 브리핑 패키지가 일정 입력까지 떠안게 되어 경계가 흐려진다.
- **[확정 (iii) — 초안의 (i) 을 사용자가 뒤집었다] 결정 L — "툴 선택"의 주체: 구조화 추출 + 결정적 매핑인가, LLM 함수 호출 루프인가.** (**가장 큰 갈림길 — 다른 결정들이 여기에 딸려 있다**)

  **확정안 (iii) 의 모양**:
  ```
  발화 → LLM 1회 (구조화 출력으로 tool_calls 목록을 받는다. 다회 왕복이 아니다)
    { tool_calls: [ {name, args}, ... ] }
    ↓ 코드가 게이트를 친다
    · 화이트리스트 — 툴 7종 이름이 아니면 거부
    · 인자 스키마 검증 — 시그니처 v2 에 맞지 않으면 거부
    · ★ person_id 강제 — LLM 이 person_id 를 직접 준 호출은 거부한다.
      인물은 반드시 resolve() → apply_resolution() 을 거쳐서만 얻는다
    · 개수 상한 — 결정 A(i) 를 그대로 적용
    ↓ 통과한 것만 실행. 거부한 것은 사유와 함께 trace 에 남긴다
  ```
  **(iii) 을 고른 근거**: `docs/proposal.md` 3.1 절 제목("툴 정의 (Function Calling)")·72행("파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다")·176행("툴 호출 정확도 | 올바른 툴을 선택한 비율")이 **LLM 의 툴 선택을 명시**한다. (i) 은 그 문장과 어긋나 CR·새 D 카드가 필요했고(02-plan-verify H-3), 지표가 잴 대상을 잃었다. (iii) 은 기획서를 지키면서 (i) 의 안전장치를 **프롬프트가 아니라 코드**로 남긴다. 비용·재현성: LLM 호출은 여전히 턴당 1회이고, 같은 입력·같은 `FakeProposer` 에 같은 실행이 나온다(원칙8). 구현량이 는 자리는 게이트 하나(`app/agent/gate.py`, U3)이며 그 대신 **부정 테스트 4종이 생겨 방어가 눈에 보인다**(판정 표 19~22행).
  **(iii) 에서도 바뀌지 않는 것**: `person_id` 의 유일한 출처는 `apply_resolution()` 이다. `ask_user`·`search_person` 은 LLM 이 부를 수 없다 — 확신도 판정은 ER 안에서만 일어난다(원칙1·2·4). `create_person` 은 재개 경로에서만, answered `new_person` 질문과 함께만 실행된다(D1).
  **(초안의 근거 기록 — 지우지 않는다)**
  (i) LLM 은 "무엇을 뽑을지"를 구조화 출력으로 정하고, "어느 툴을 부를지"는 코드가 정한다: `mentions→resolve/apply_resolution`, `events→add_event`, `schedules→add_schedule`, 확신도 미달→ER 이 `ask_user`. 근거: ① 원칙4 와 같은 정신 — "LLM 단일 호출로 하지 않는다"는 판정을 단계로 쪼갠 것이고, 툴 선택도 같은 이유로 코드가 보증해야 오병합 경로가 닫힌다(원칙1), ② `create_person` 이 `_require_confirmation` 으로 막혀 있으므로 LLM 이 임의로 부를 수 없는데, 그 실패를 LLM 이 "다시 시도"로 받으면 루프가 돈다, ③ 재현 가능(원칙8) — P10 이 "툴 호출 정확도"를 재려면 같은 입력에 같은 호출이 나와야 한다, ④ 비용·지연이 턴당 LLM 1회로 고정된다.
  (ii) 진짜 function calling 루프(LLM 이 `tool_calls` 를 내고 결과를 다시 넣는 다회 왕복): "에이전트가 스스로 툴을 호출한다"는 서사에 가장 가깝고 포트폴리오 설명력이 있다. 대신 비결정적이고, 호출 수 상한(결정 A(ii))·화이트리스트·인자 검증·`ask_user` 강제 게이트를 전부 직접 만들어야 하며, 오병합 금지가 프롬프트 의존이 된다.
  (iii) 하이브리드 — LLM 이 툴 호출을 **제안**하고 코드가 화이트리스트·인자 스키마·ER 경유를 강제해 통과시킨다: (ii)의 서사에 (i)의 안전장치를 붙인 것. 구현량이 가장 크고 테스트 경우의 수가 는다. 초안은 이 점을 이유로 "P10 이후의 확장으로 남기고 지금은 (i)로 간다"를 권했다. → **사용자가 뒤집어 이것이 확정안이 됐다**: 구현량보다 기획서 3.1·5.2 와의 정합이 앞서고, (i) 로 가면 CR 또는 새 D 카드로 이탈을 기록해야 하는데 (iii) 은 그 부채 자체를 없앤다. 다회 왕복을 쓰지 않으므로 (ii) 의 비결정성·비용 폭증도 피한다.

- **[확정 M-0 — H-2 를 닫는 경로. 새 결정이 아니라 C·D·E·J 가 전제한 것을 실행 가능하게 적은 것이다] `pending_questions.context` 를 누가 어떻게 확장하는가.**
  채택: **`apply_resolution()` 을 부르기 전에 `dataclasses.replace(resolution, ask_payload=…)` 로 `context` 를 확장한다.** 근거: ① `Resolution` 은 `@dataclass(frozen=True)`(`app/er/types.py` 193행)이므로 `replace` 가 새 객체를 만들고 **`app/er/` 를 한 줄도 고치지 않는다**(P4b 게이트 수치 보호, 원칙8). ② `apply_resolution`(`app/er/pipeline.py` 474~480행)은 `kind`/`question`/`options`/`context` 네 키만 뽑아 `ask_user` 에 넘기므로, 확장된 `context` 가 `ask_user` 의 검증(비밀 최상위 키·`AFFIRMATIVE_KEY`)을 **그대로 통과**한다 — 툴 밖 쓰기가 아니다(S3.2 16행 "모든 툴 호출은 `agent_traces` 에 기록"). ③ ER 이 이미 넣은 키(`mention`·`utterance`·`candidate_ids`·`confidence_breakdown`·`AFFIRMATIVE_KEY`)는 **읽지도 고치지도 않고** 최상위에 `"resume"` 한 키만 더한다.
  **버린 길 (b)**: `apply_resolution` 뒤에 `PendingQuestion.context` 를 ORM 으로 직접 고친다 — `ask_user` 검증을 우회하고 `agent_traces` 에 남지 않는다. 판정 표 23행이 이 길을 부정 grep 으로 막는다.
  **크기 통제(S3.4 13행 "재개에 필요한 것만, 전체 대화 이력 저장 금지")**: `resume` 에 싣는 것은 ㉮ 아직 실행하지 않은 **게이트 통과 제안**, ㉯ 보류 draft, ㉰ `hints{relation_tag?, hierarchy?}` 세 가지뿐이다. 발화 원문은 ER 이 이미 `context["utterance"]` 로 **1건** 넣었고 루프는 더 넣지 않는다(이전 턴·대화 이력 0). 결정 A(i) 의 상한 5·5·3 이 그대로 **`resume` 의 항목 수 상한**이 되므로 `context` 는 발화 하나의 제안 목록보다 커질 수 없다. 이중 안전장치로 직렬화 바이트 상한 `LOOP_MAX_RESUME_BYTES` 를 두고, 넘으면 보류 draft 를 버리고 `dropped` 수만 남긴다(판정 표 24행). 중첩 값에 비밀이 없게 하는 것은 루프의 몫이다(P2 04-review 98행 O5 — `ask_user` 의 비밀 검사는 최상위 키 이름만 본다).

**미결 — 없음. 2건 모두 사용자가 확정했다 (2026-09-23).**

> **확정 M-1 = (d)** 확인 질문 하나로 태그까지 같이 받는다. 근거(코드로 확인): `create_person(display_name, aliases, relation_tag, hierarchy)` 는 넷 다 필수이고(`app/tools/persons.py`), **`update_person(person_id, facts?, new_alias?, display_name?)` 에는 `relation_tag`·`hierarchy` 인자가 없다** — 한 번 틀리면 되돌릴 툴이 없고 화면도 3개로 고정이라 고칠 길이 없다. (a) 기본값 저장은 그래서 배제했고, (b) 추가 질문은 되묻기가 이미 23.5%(P4b 실측)인데 왕복을 3턴으로 늘리며, (c) 생성 포기는 사용자가 방금 "예"라고 답한 것을 버리는 미검출이다. (d)는 **어차피 물어야 하는 질문 하나**에 태그를 얹으므로 왕복이 늘지 않는다.
>
> **확정 M-2 = (i)** 후보 시각 2~3개 + "모르겠어요". 근거(코드로 확인): `answer_question` 이 `answer not in question.options` 면 `InvalidValue` 를 던진다(`app/tools/questions.py`) — **자유 입력이 구조적으로 불가능**하다. 답→ISO 시각 매핑을 `resume["schedule_options"]` 에 미리 실어 재개 때 **사전 조회로 복원**한다(문자열 재파싱은 로케일·비결정성 문제가 크다). (ii) 날짜만 묻고 기본 시각을 쓰는 안은 결정 K(i) 가 "브리핑이 틀린 때 뜨는 것을 막자"고 되묻기를 택한 취지와 모순이라 배제했다.

**아래는 두 미결의 원문(선택지·비용 비교)이다. 확정 뒤에도 근거 기록으로 남긴다.**

- **[미결 M-1] `new_person` 재개 때 `relation_tag`·`hierarchy` 를 LLM 이 추론하지 못했으면 어떻게 하는가.**
  사실관계: `create_person(display_name, aliases, relation_tag, hierarchy)` 는 넷 다 **필수**이고 `RELATION_TAGS`/`HIERARCHIES` 밖 값은 `InvalidValue` 다(`app/tools/persons.py` 430~433행). ER 이 만드는 `context` 에는 이 힌트가 없다(`_build_ask_payload` 는 `mention`·`utterance`·`candidate_ids`·`confidence_breakdown`·`affirmative_options` 만 채운다). **L(iii) 에서는 1차 출처가 생긴다** — LLM 이 `create_person` 을 제안할 때 `relation_tag`·`hierarchy` 를 함께 주며(CLAUDE.md "사용자가 고르지 않고 대화에서 자동 추론한다"), 게이트를 통과하면 `resume.hints` 로 실린다. 남는 것은 **제안이 없거나 값이 고정 집합 밖일 때**다. 그리고 한번 정해지면 **되돌릴 툴이 없다** — 시그니처 v2 의 `update_person` 에는 `relation_tag` 인자가 없고 화면도 3개로 고정이라 수정 UI 가 없다.
  (a) 기본값으로 저장(예: `지인`/`동`) — 비용: 틀린 태그가 조용히 영구 저장되고 브리핑·인물 카드가 그 값을 쓴다. 갱신 경로가 없어 되돌릴 수 없다.
  (b) `ask_user` 로 한 번 더 묻는다 — 비용: 왕복이 3턴이 되고(`발화 → 새 인물 확인 → 태그 확인`) 재개 상태가 2단계가 된다. `kind` 는 3종 고정이라 이 질문도 `new_person` kind 로 내야 한다.
  (c) 그 인물을 만들지 않고 턴을 끝낸다 — 비용: 사용자가 방금 "기억해줘"에 **예**라고 답한 것을 버린다. 미검출이고 UX 가 나쁘다.
  (d) **권장 — 확인 질문 하나로 태그까지 같이 받는다**: M-0 의 `dataclasses.replace` 로 `new_person` 질문의 `options`/`affirmative_options` 를 "가족으로 기억할게요 / 친구로 … / 직장으로 … / 아니요" 처럼 태그별 긍정 옵션으로 확장하고, 답 문자열 → `relation_tag` 매핑을 `resume` 에 실어 재개가 결정적으로 변환한다. `hierarchy` 는 LLM 힌트가 있으면 그 값, 없으면 `동`(위계는 브리핑 영향이 작고 3종뿐이다). 비용: ER 이 만든 질문 문구를 루프가 **확장하는 유일한 자리**가 생기고 칩이 최대 6개가 된다(P8 이 렌더링해야 한다). 이득: 왕복은 그대로 2턴이고, D1 확인형을 지키며, 추론 실패가 조용한 오기록이 되지 않는다.
- **[미결 M-2] `ask_user(kind="schedule")` 의 `options` 형식과 답 → `scheduled_at` 변환 규칙**(결정 K(i) 가 만들 질문. R-7).
  사실관계: `options` 는 비어 있지 않은 문자열 목록이어야 하고(`app/tools/questions.py` `_validate_options`), `answer` 는 **저장된 `options` 중 하나**여야 한다(`answer_question` 263행). 자유 입력은 지금 구조에서 불가능하다.
  (i) **권장 — 후보 시각 2~3개 + "모르겠어요"**: 옵션은 사람이 읽는 문자열("10월 2일 저녁 7시")로 내고, 답 문자열 → ISO 시각 매핑을 `resume["schedule_options"]` 에 함께 실어 재개가 **문자열을 다시 파싱하지 않고** 사전 조회로 복원한다(파싱은 비결정적이고 로케일을 탄다). "모르겠어요"면 `add_schedule` 을 부르지 않고 그 사실을 응답·trace 에 남긴다. 비용: 후보를 만드는 규칙(예: 발화의 날짜 + 09시/19시)을 U5 에서 정해야 한다.
  (ii) 날짜만 묻고 시각은 기본값(09:00) — 옵션이 짧아지지만 브리핑이 틀린 때 뜬다(결정 K 가 되묻기를 고른 이유와 모순).
  (iii) 이번 패키지에서는 `schedule` 되묻기를 만들지 않는다 — 결정 K(i) 를 되무는 것이고, 그러면 그 `kind` 는 P10 에서 영영 n=0 이다.

**backlog 개정 제안 (architect → 사용자 승인 후 메인 세션이 반영. 이 패키지는 backlog 를 고치지 않는다)**

1. **`DELETE /persons/{id}` 항목 신설** — security §5 가 요구하는 "인물 단위 완전 삭제 API" 가 backlog 어느 항목에도 없다(F-4d2507, P2 04-review 90행이 architect 에게 인계). P1 04-review §7 의 "`pending_questions.context`·`agent_traces.input/output` JSONB 안의 `person_id` 참조 정리" 요건을 같은 항목에 싣는다. **P5 가 아니라 별도 항목**으로 두기를 권한다 — 루프의 수용 기준과 성격이 다르다.
2. **P5 행에 세분화 줄 추가** — P1·P3-baselines·P3-llm-providers·P4b 행이 그랬듯 `- 세분화는 docs/wiki/packages/P5-loop/01-plan.md (U1~U8)` 한 줄과 결정 항목 요약 한 줄. **P5 항목의 문장·수용 기준은 한 글자도 바꾸지 않는다.** 이미 반영된 세분화 줄이 "(U1~U7)" 로 되어 있으면 "(U1~U8)" 로 고치고, 그 줄이 backlog 를 **줄 번호**로 가리키고 있으면 인용문으로 바꾼다(R-5 — 항목이 삽입될 때마다 번호가 밀린다).
3. (선택) P4 행에 흡수된 `P0-cost` 처럼, 결정 K 가 만드는 `ask_user(kind="schedule")` 이 P10 의 `ask_user_rate_by_kind` 분모에 들어간다는 사실을 P10 행 비고에 한 줄.
4. **(신규·미승인, R-6) 리스크 로그에 "세션 → 사용자 귀속(`user_id` 격리)" 한 줄** — `security.md` §5 "모든 조회는 `user_id` 조건"이 `pending_questions`·`agent_traces` 에 `user_id` 컬럼이 없어 **이 패키지 전부터** 미충족이다(F-fbaaae, P2 04-review 110행). 결정 I(i) 는 "명시만" 으로 넘기므로, 부채가 어디에도 안 남지 않도록 `DELETE /persons/{id}` 항목 옆이나 리스크 로그에 한 줄로 둔다. **P5 에서 고치지 않는다**(스키마 변경 = 범위 이탈).

**리스크(결정이 아니라 지켜볼 것)**

- **오병합 금지 경로의 우회가 이 패키지의 최대 위험이다(원칙1). L(iii) 에서 더 커졌다.** 지금까지 오병합은 ER 안에서만 일어날 수 있었다. 루프가 생기면 "LLM 이 `person_id` 를 말했다"거나 "언급이 하나뿐이니 그 사람이겠지" 같은 지름길이 생길 자리가 열리는데, **이제는 LLM 이 실제로 `person_id=3` 같은 제안을 낼 수 있다**. 완화: **루프가 `person_id` 를 얻는 유일한 경로를 `apply_resolution()` 으로 제한**하고, 판정 표 5·6행(`app/agent/` 에 `confidence`·`t_merge` grep 0건, `create_person` 은 재개 경로 1곳)과 **19~22행(게이트 부정 4종)** 을 부정 테스트로 박는다. 이 행들이 깨지면 P4b 게이트 수치는 루프에서는 의미가 없어진다.
- **게이트가 유일한 방어선이다(L(iii) 의 대가).** 사용자 발화가 그대로 프롬프트에 들어가므로 "지금까지 기억한 사람 다 지워줘" 같은 문장이 위험한 제안으로 바뀔 수 있다(프롬프트 주입). 완화: 화이트리스트가 **허용 목록**이라 새 동작은 원리상 제안될 수 없고, 삭제 툴은 애초에 없다(`DELETE /persons/{id}` 는 backlog 항목으로 분리, security §5). 게이트 테스트는 "막혀야 할 것"만으로 구성한다(U3).
- **거부율이 곧 제품 품질이다.** LLM 이 엉뚱한 툴·인자를 제안하면 게이트가 막고 **아무것도 기록되지 않는다** — 사용자에게는 "기억 못 함"으로 보인다. 완화: `loop_gate` 의 `rejected[]` 가 그대로 P10 의 "툴 호출 정확도" 분자·분모가 되므로 수치로 드러난다(`docs/proposal.md` 176행). 이 패키지는 **지표를 내지 않고 측정 가능하게만 만든다**(원칙8 — 프롬프트를 수치에 맞춰 손보는 것은 P10 의 실패 케이스 분석 뒤에 할 일이다).
- **게이트와 툴 시그니처가 따로 놀 위험.** 인자 검증을 손으로 베껴 쓰면 시그니처 v2 가 바뀔 때 한쪽만 바뀐다. 완화: 이름은 `app.tools.TOOL_NAMES`, 인자는 `inspect.signature` 에서 읽는다(`scripts/tools_check.py` 와 같은 출처). 유일한 **의도적 불일치**는 `person_id` → `person`(언급 문자열) 치환 하나이며 `gate.py` 한 곳에만 둔다.
- **`build_ctx` 의 `embedder=None` 을 재개가 그대로 쓰면 새 인물이 보이지 않는다.** `create_person`/`update_person(new_alias=…)` 은 `ctx.embedder` 로 별칭 임베딩을 만드는데(`app/tools/persons.py` 451·460행), 지금 `build_ctx` 는 "답 저장은 별칭을 만들지 않는다"는 전제로 `None` 을 넣는다. 재개는 별칭을 **만든다** — 임베딩이 NULL 이면 그 인물은 이후 후보 검색(별칭 top-K)에서 빠져 미검출이 된다. 완화: 채팅·재개 ctx 조립에서 임베더를 채우고 판정 표 27행으로 확인한다. 이 함정도 루프가 처음 밟는다.
- **`user_id` 격리 부채(F-fbaaae)를 이 패키지가 늘린다.** `pending_questions`·`agent_traces` 에 `user_id` 컬럼이 없는데 루프가 두 테이블에 행을 **많이** 만든다. 결정 I(i) 는 단일 사용자 전제를 명시만 하고 넘긴다 — 스키마 변경은 범위 밖이다. 완화: 모듈 docstring·README 명시 + backlog 개정 제안 4(R-6)로 부채를 남긴다. 후행 패키지(P9 또는 별도 항목)가 닫는다.
- **되묻기가 정상 경로다(23.5%, P4b 실측 40건 중 31건).** "행복 경로 = 한 턴에 끝남"으로 설계하면 실제 사용의 4분의 1이 예외 처리로 빠진다. 완화: U4·U7 의 테스트 기본 케이스를 **되묻기로 끝나는 턴**으로 잡는다.
- **부분 저장의 일관성.** 결정 D(i)는 "확정분은 남기고 보류분은 context 로"인데, 재개가 영영 오지 않으면(24h 만료) 보류 draft 는 사라진다 — 이벤트 미검출이다. 완화: 만료된 질문의 보류 draft 수를 `loop_turn` trace 에 남겨 P10 이 셀 수 있게 한다. 되살리는 로직은 만들지 않는다(범위).
- **`ToolContext.last_trace_id` 는 `@traced` 성공 경로가 매번 덮어쓴다**(P3-er 04-review 161행) — 여러 툴을 연달아 부르는 루프에서는 마지막 값만 남는다. `resolve()` **직후에만** 읽어야 한다. 이 함정은 루프가 처음 밟는다.
- **`pending_questions.context` 가 커진다.** 보류 draft·미실행 제안을 실으면 S3.4 13행("재개에 필요한 것만")과 긴장이 생긴다. 완화는 **결정 M-0 의 "크기 통제"** 절에 적었다: 상한(결정 A)이 곧 항목 수 상한, 발화 원문은 ER 이 넣은 1건뿐, 이중 안전장치로 `LOOP_MAX_RESUME_BYTES`(판정 표 24행). `ask_user` 의 비밀 방어는 최상위 키 이름만 본다(P2 04-review 98행 O5) — **중첩된 값에 비밀이 없게 하는 것은 루프의 몫**이다.
- **원칙7 경계는 코드로 지켜야 한다.** "오늘 힘들었어" 같은 발화가 들어온다. 완화: 결정 B(i) 템플릿 + 판정 표 18행 부정 테스트. LLM 문장화를 택하면 이 방어가 프롬프트로 내려간다.
- **LLM 비용·지연.** 제안 1회 + 언급당 ER 판정 1회 = 턴당 최대 1+5회 — **L(iii) 로 바뀌어도 그대로다**(다회 왕복이 아니므로). P4b 실측(40 시나리오 $0.0274)에 비추면 데모 규모에서는 작지만, 테스트가 실 호출을 하면 이야기가 다르다. 완화: 모든 테스트는 `FakeProposer`·`FakeJudge`(판정 표 2행 네트워크 0).
- **`AnswerOut` 확장은 기존 테스트를 건드린다.** `tests/test_api.py` 의 200 응답 단언이 바뀐다 — **기대값을 바꾸는 것과 단언을 없애는 것은 다르다**(P4b 가 남긴 교훈). 404/409/422 단언은 그대로 유지한다.
- **Windows 로케일·포트.** 판정 명령 앞에 `PYTHONUTF8=1`, 로컬 DB 는 `POSTGRES_PORT=5433`. `.env` 는 스크립트가 읽지 않는다 — 값을 셸에 넣는 것은 사용자다(security §1).
- **L-003.** dev 푸시 뒤에는 멈춘다. 승격은 사용자 결정이다. **L-002.** 이 계획은 architect 가 썼고, 점검표(02-plan-verify)는 verifier 가, 코드는 backend-agent 가 쓴다.
- **단위 경계.** `app/agent/` 6파일과 `app/api/` 3파일을 한 단위로 묶지 않는다(U1~U8 로 나눈 이유 — L(iii) 로 게이트가 생기면서 U3 이 독립 단위가 됐다). 한 단위가 커밋 하나를 넘지 않는다. 단위마다 `/commit`, 각 커밋 `Refs: P5-loop …`.

## 후행 패키지가 이 패키지에서 기대하는 것

- **P6-memory**(의존: P5) — 루프의 기록 단계가 만든 `events` 행과 `raw_utterance` 가 승격의 입력이다. 승격 훅을 **기록 단계 뒤**에 걸 수 있도록 `loop_record` 지점을 한 곳으로 모아 둔다.
- **P6-briefing**(의존: P5) — `get_briefing` 은 이 패키지가 부르지 않는다. 주기 작업·수동 트리거가 붙을 자리가 루프 밖(별도 엔드포인트)이라는 것만 확정된다.
- **P7-push**(의존: P6) — 되묻기 발생 시점(`pending_questions` 생성)이 알림 트리거 후보다. 루프가 그 시점을 trace 로 남긴다.
- **P8-frontend**(의존: P5, P6) — `POST /chat` 요청/응답 스키마·`X-Session-Id` 규약·`question_id`+`options`(확인 칩)가 **프론트 계약 그 자체**다. 칩 목록 조회는 `list_pending` 을 감싸는 얇은 라우트로 P8 이 요구하면 추가한다(이 패키지에서는 만들지 않는다).
- **P10-final-eval**(의존: P4, P9) — 이벤트 추출 F1(클래스별)·**툴 호출 정확도**·`ask_user_rate_by_kind`(특히 `schedule`, 결정 K)를 이 루프가 만든 `agent_traces` 로 잰다. **L(iii) 덕분에 "툴 호출 정확도"(`docs/proposal.md` 176행 "올바른 툴을 선택한 비율")가 실제로 잴 수 있는 지표가 된다** — 분모는 `loop_extract.output.tool_calls` 의 제안 수, 분자는 라벨과 일치하는 제안 수, 그리고 `loop_gate.output.rejected[]` 가 사유별 거부율을 준다. 그래서 step 어휘(결정 F 의 6종)와 `loop_extract`/`loop_gate`/`tool_call` 세 층이 **평가 가능성의 전제**다. 초안에서는 (결정 L(i) 의 결정적 매핑 때문에) 이 지표가 사실상 추출 정확도와 같아져 정의를 다시 써야 했는데, 그 부채가 사라졌다.
- **P9·보안 부채**(F-fbaaae, R-6) — `user_id` 격리는 이 패키지가 열어 두고 간다. 후행 패키지가 스키마에 `user_id` 를 더할 때 `pending_questions`·`agent_traces` 를 쓰는 유일한 자리가 툴 7종과 `@traced` 라는 점이 그 작업을 작게 만든다(루프는 ORM 을 직접 만지지 않는다 — 판정 표 23행).

## 읽은 카드

- `docs/backlog.md` — "P4 파일럿 평가 전에 P5 이후 시작 금지" 원칙 줄, **P5 절 전문(수용 기준을 글자 그대로 옮긴 출처 — 줄 번호로 가리키지 않는다, R-5)**, P4·P4b 절, P6~P11 의 "의존: P5" 줄, 리스크 로그
- `docs/proposal.md` — **3.1 "툴 정의 (Function Calling)" 68~84행**(72행 "파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다"), **3.2 에이전트 루프 86~108행**(108행 "각 단계에서 툴 선택이 일어난다는 점이 에이전트 구조의 근거"), **5.2 지표 168~179행**(176행 "툴 호출 정확도 | 올바른 툴을 선택한 비율") — 결정 L 을 (iii) 로 바꾼 근거
- `docs/wiki/packages/P5-loop/02-plan-verify.md` — verifier 판정 전문(H-1·H-2·H-3, R-1~R-8). 이 개정본이 응답하는 문서다
- `docs/wiki/review-index.md` — **14행 R6**(`D1 → S3.4 → P2-tools, P5-loop`), **15행 R7**(`D2 → S3.4 → P2-tools, P5-loop`), 30행(닫는 법)
- `docs/wiki/decisions/D01-new-person-confirm.md` — 전문. 특히 11행 "코드에서 지켜야 할 것: `create_person` 호출 경로는 반드시 answered pending_question 을 거친다"
- `docs/wiki/decisions/D02-ask-user-async.md` — 전문. 5행(턴 종료), 9행(답 없이 새 발화가 오면 대기 질문 유지·새 발화 우선), 11행 "동기 대기(sleep/poll) 금지"
- `docs/wiki/specs/S3.4-ask-user-protocol.md` — 전문(6~8행 턴 N/N+1 그림, 10~13행 만료·칩·context 규약)
- `docs/wiki/specs/S3.2-tools-v2.md` — 표 전체, 10행 "런타임이 raw_utterance 자동 주입", 16행 "모든 툴 호출은 agent_traces 에 기록"
- `docs/wiki/specs/S3.3-er-pipeline.md` — 진입점 계약만(9~13행 분기, 17행 "T_merge 미만 자동 병합 금지", 19행 CR-001)
- `CLAUDE.md` — 원칙1~9, 툴 7종 시그니처 v2, 데이터 모델 v2, `events.type` 고정 집합, 개발 프로세스
- `docs/wiki/registry.md` — 43~95행(`app/db`·`app/tools`·`app/api`·`app/er` 행 전부 grep). **`app/agent/` 0건 — 루프 모듈은 아직 없다**
- `docs/wiki/verification.md` — 6~18행(증거로 인정하는 것), 20~27행(계획 검증 기법), 28~35행(구현 검증)
- `.claude/gitlog.md` — 브랜치(`dev = 1227026`, `main = e2f0569` … 스냅샷 이후 FIX-001 로 네 갈래 동일), 최근 20건, 미커밋 변경 3건
- `docs/wiki/CURRENT.md` — 15·16행(FIX-001 완료·"다음은 P5", P4b 게이트 `0.8 [] True True`·되묻기 31건 23.5%·한계 문장)
- `docs/wiki/INDEX.md` — 44~55행(태그 어휘), 59~81행(패키지 표 72행 `P5-loop … R6 R7`, 81행 게이트)
- `docs/wiki/packages/P2-tools/04-review.md` — **§7 "P5-loop (루프·채팅·재개)" 106~114행 전부**(ToolContext 단일 생성 지점 / 확인 질문 대상 바인딩·1회 소비 / `/answers` 뒤 절반 / `user_id` 격리 부재 / tool_error 별도 커넥션 결정 / `get_session` 경계 / "어제 저녁" 해석), §3 66행(P5 경계 — 라우트 2개), §6 98행 O5
- `docs/wiki/packages/P3-er/04-review.md` — §7 "P5-loop" 157~162행(트랜잭션 경계·`AlreadyApplied`·`last_trace_id` 덮어쓰기·hints 우선)
- `docs/wiki/packages/P4-pilot-eval/04-review.md` — 214행(P5 가 받을 것: 러너 env 규약, `ask_user(kind=schedule)` n=0)
- `docs/wiki/packages/P4b-er-redesign/01-plan.md` — 형식 선례(허용 파일 각주 57행·판정 방법 표·재사용 표·결정 항목)
- `docs/wiki/templates/plan.md` — 이 문서의 형식
- `docs/wiki/lessons/L-001`~`L-004` — 제목·요지(브랜치·gitlog / 역할별 모델 분리 / dev 푸시 뒤 정지 / 단계 시작 전 승인)
- 코드(계약 확인 목적으로 연 것): `app/api/routes.py`(10~11·59~62행이 P5 를 지목), `app/api/schemas.py`(27~29행), `app/api/deps.py`(13~19행 `X-Session-Id` 인계), `app/tools/context.py`(모듈 docstring 16~31행 F-4d8d96 인계·`traced(step=...)`·`ToolContext` 필드), `app/tools/questions.py`(184~276행 `ask_user`·`answer_question`·248~251행 격리 부재), `app/tools/persons.py`(266~309행 `_require_confirmation`·411~424행 `create_person`), `app/er/pipeline.py`(165~235행 `_build_ask_payload`·321~357행 `resolve`·379~484행 `apply_resolution` — 469~480행이 `ask_user` 에 넘기는 네 키), `app/main.py`(예외 매핑 55~111행), `app/settings.py`(상수 목록)
- 개정 때 추가로 연 것: `app/er/types.py` 193행(`Resolution` 이 `@dataclass(frozen=True)` — `dataclasses.replace` 가 가능한 근거, M-0), `app/tools/types.py` 113~128행(`PendingQuestionOut` 에 **`context` 필드가 없다** — 재개가 `context` 를 툴 반환값으로 받을 수 없어 `deps.py` 가 읽어 넘기는 근거, U7), `app/tools/persons.py` 404~464행(`create_person` 의 `relation_tag`/`hierarchy` 필수·`ctx.embedder` 사용 — M-1 과 임베더 리스크), `app/tools/questions.py` 255~276행(`answer_question` 이 `options` 안의 답만 받는다 — M-2), `app/api/deps.py` 전문(`build_ctx` 가 `embedder=None`·`PendingQuestion` 을 읽는 유일한 자리), `scripts/tools_check.py` 1~55행(`inspect.signature` 대조 방식 — 게이트가 같은 출처를 쓴다)
