# P2b-person-delete · U1(인물 참조 판별 규칙) 커밋 전 리뷰

검토자: verifier (fable)
일시: 2026-11-09
대상: 작업 트리 미추적 새 파일(HEAD `2ff0efb`, 브랜치 `dev2`) — `app/api/delete.py` · `tests/test_person_refs.py` · `docs/wiki/packages/P2b-person-delete/tests.md`. 그 밖의 미커밋 변경(`journal.md`·P5b evidence 2파일·L-007 evidence)은 대상 밖. `delete_person` 은 U2 몫이라 이 파일에 없다(계획대로).
결과: **통과** (재리뷰 2026-11-09, §6) — 1차 판정은 **보류**([필수] R-U1-1 문서 보정 1건)였고, 보정 2줄이 들어간 것과 코드 무변경을 직접 확인해 통과로 바꿨다. 1차 본문(§1~§5)은 기록으로 그대로 둔다. 열린 [권고] R-U1-2·3(U2 위임문)·R-U1-4(U5/security §5)는 커밋을 막지 않는다.
1차 결과(기록): **보류** — [필수] 1건(**문서만**, 코드 변경 0): 01-plan "사실 3" 표·V1-2·해석 ㄴ 와 02-plan-verify 사실 검증 표가 `pending_questions.context["resume"].person_ids` 라고 적었는데 코드에 그 경로가 없다(`person_ids` 는 `ResolveOutcome.to_dict()` = `loop_resolve_done.output`). 구현자가 보고한 "계획과 다른 점" 3건은 전부 코드로 맞음을 확인했고, 41/2177 passed·ruff·mypy 38=38 을 직접 재실행했으며, 변이 1건(구현자와 다른 것)을 런타임 치환으로 넣어 4 FAIL 로 잡히는 것을 확인했다. 보정 줄이 들어가면 **통과** 로 바꾼다(재리뷰는 §4 R-U1-1 의 세 줄 grep 확인으로 충분). [권고] 4건은 커밋을 막지 않는다.

---

## 1. 본 것

| 파일 | 줄 | 본 내용 |
|---|---|---|
| `app/api/delete.py` | 82~99 | 상수 5종 `PERSON_ID_KEYS=("person_id","matched_person_id")` · `PERSON_OBJECT_KEYS=("person",)` · `TOP_LEVEL_ID_TOOLS={create_person, update_person}` · `ID_MAP_KEYS=("candidate_ids","person_ids")` · `ID_LIST_KEYS=("candidate_person_ids",)` · `PERSON_REF_RULES` 1~5 — 01-plan 결정 C-3 확정 ①~⑤ 와 1:1 |
| 같은 파일 | 102~105 | `_is_id`: `type(value) is int and value == person_id` — `bool`(`type(True) is bool`)·`str`·`float` 전부 거짓. 결정 C-3 "`bool` 은 정수로 보지 않고 문자열 숫자도 보지 않는다" 그대로 |
| 같은 파일 | 108~130 | `_walk`: dict 는 키마다 규칙 1·2·4·5 를 보고 **그 뒤 값으로 재귀**(특수 키 아래도 내려감), list/tuple 은 원소 재귀, 스칼라 False. 깊이 무관 |
| 같은 파일 | 133~148 | `references_person`: 규칙 3 은 `isinstance(obj, dict) and tool_name in TOP_LEVEL_ID_TOOLS` 일 때 **최상위** `obj["id"]` 만. 입력 불변(읽기만) |
| 같은 파일 | 1~64 docstring | 규칙 5개 · 쓰는 곳 전수 표 15행 · "계획 표와 다른 점" · "남는 행"(결정 G (i)) · "새 trace 모양 패키지의 의무"(리스크 2). 25행 "`agent_traces` 를 쓰는 곳은 7곳(`context.py` 2·`hooks.py`·`notifier.py`·`run.py` 3·`routes.py`)" — 열거는 **8곳**인데 숫자는 7(R-U1-2) |
| `tests/test_person_refs.py` | 전체 | 함수 30개(`grep -c "^def test_"` = 30) + parametrize(`tool` 2 · `value` 11) = **41건**. 픽스처는 `to_jsonable`·`PersonOut/Candidate/EventOut/ScheduleOut/BriefingOut.to_dict`·`_build_ask_payload`·`Resolution.to_dict`·`PendingResume.to_dict`·`ResolveOutcome.to_dict`·`MentionDecision.to_dict` 로 만든 **실제 직렬화 모양**. 양성은 "그 규칙 하나만 참"(예: identity context 는 `matched_person_id=None` 으로 규칙 1 배제), 음성은 같은 숫자가 `considered_event_ids`·`schedule_id`·`question_id`·`EventOut.id`·`ScheduleOut.id` 에만 있는 구조 — 항상 통과하는 테스트가 아니다(§3 변이) |
| `tests.md` | 전체 | 표 30행(parametrize 는 1행에 건수 표기) + 변이 표 V1-1~V1-9 — `pytest -v` 이름과 1:1, 변이 실패 테스트 목록이 evidence `20261109-1633-u1-mutation.txt` 9회 append 와 일치(3·3·3·3·3·15·5·1·1 failed) |
| 구현자 evidence | `20261109-1633-u1-person-refs.txt`(41 PASSED, exit 0) · `-ruff.txt` · `-mutation.txt`(9회, 전부 exit 1) · `20261109-1634-u1-mypy.txt`(`[ok] 38=38`) · `-pytest-all.txt`(**2177 passed**, skip 없음) · `-tests-unmodified.txt`(`--diff-filter=M -- tests/` 빈 출력) · `-tools-check.txt`(`RESULT: 7/7 ok`) | 보고와 일치 |
| 계획·검증 문서 | `01-plan.md` 11~36행(사실 3 표)·108~121행(U1·V1 표)·167행(해석 ㄴ)·257~265행(결정 C-3 확정)·결정 G·J·K·리스크 1·2·6 · `02-plan-verify.md` 74행(사실 3 검증 행) · `03-log.md` U1 항목 | §2 |

## 2. 계획·카드 대조

| 항목 | 근거(코드 직접 확인) | 판정 |
|---|---|---|
| 결정 C-3 확정 규칙 ①~⑤ = 코드 상수 | 상수 5종(§1) + `test_rule_constants_are_fixed_values` 가 값으로 고정 | 일치 |
| 결정 C-3 "`bool`·문자열 숫자 아님" | `_is_id` `type(value) is int` · `test_bool_is_not_integer_id`(7개 위치) · `test_string_digits_are_not_integer_id`(6개 위치 + `float`) | 일치 |
| 결정 J "새 모듈 `app/api/delete.py`" · J-11 허용 파일 | `git status --short -- app tests web` → `?? app/api/delete.py` `?? tests/test_person_refs.py` 뿐, `--diff-filter=M -- app/ tests/` 빈 출력(`evidence/20261109-1642-u1-review-status.txt`). `app/tools/`·`app/agent/`·`app/er/` 등 무변경 | 일치 |
| 범위 "하지 않는 것" — 툴 8번째·마이그레이션·텍스트 삭제 | `delete.py` 에 DB·세션·SQL 없음(순수 함수), `app/tools/` 무변경, `tools_check 7/7` | 일치 |
| U1 "`grep -rn "AgentTrace(\|ask_payload\|to_jsonable(" app/` 전수 조사" — 표에 없는 모양이 있는가 | 내가 다시 돈 grep: `AgentTrace(` 쓰기 **8곳** — `tools/context.py` 198(tool_error)·224(@traced) · `memory/hooks.py` 133(memory_error) · `push/notifier.py` 235(push_send) · `briefing/run.py` 153(briefing_error)·258(briefing_compose)·320(briefing_run) · `api/routes.py` 295(loop_error). `ask_payload` 생성 4곳 — `er/pipeline.py` 215(identity: `context.candidate_ids` 이름→id, `confidence_breakdown.matched_person_id`)·232(new_person: `candidate_ids={}`) · `agent/loop.py` 1521(FIX-035 후속 new_person, `candidate_ids={}`)·`_ask_schedule`(`resume.schedule.person_id`, `ScheduleResumeRef.to_dict` types.py 361~366). `to_jsonable(` 저장 경로 2곳 — `context.py` 190/229/261(@traced input·output·`amend_trace_output`) · `questions.py` 211(`pending_questions.context`). `amend_trace_output` 가 더하는 키는 `decision.applied/pending_question_id/applied_at`(pipeline.py 10행)·`identity_rejected/followup_question_id`(loop.py 1554~1557) — 질문 id 이므로 규칙에 **안 들어가는 것이 맞다**(값이 인물 id 와 겹쳐도 지우지 않음). 각 trace output 의 to_dict 를 열어 본 결과: `MentionDecision`(`person_id`,1) · `ResolveOutcome`(`person_ids` 사전,4 + `decisions[]`,1) · `RecordOutcome`(`executed[]={index,name,trace_id}`,`failed[]` — 인물 id **없음**) · `_QueryTrace`(`person_id`,`resolutions[].person_id`,1) · `TurnResult`(`pending_question`=`PendingQuestionOut{question_id,status,kind,question,options}` — id 없음, 질문 **문장**에 이름) · `ResumeInput`(`context` 통째 — 4·1) · `Proposal`/`GateVerdict`(언급 문자열·인덱스만) · `Resolution`(`candidates[].person_id`·`confidence_breakdown.matched_person_id`·`decision.matched_person_id`,1; input 은 `mention,utterance,hints,config(ERConfig 임계치)` — id 없음) · `AppliedResolution`(`person_id`,1) · memory 3종(`person_id`,1) · push(input `person_id`,1; output `schedule_id`·`removed`·`payload.title/body`) · briefing 3종(`briefing_run` 은 `selected/briefed/skipped[].schedule_id` **일정 id 만**) | **표 밖 모양 없음** — 구현자 전수 표와 결론 같음 |
| 구현자 "계획과 다른 점" ① `person_ids` 는 `PendingResume` 이 아니라 `ResolveOutcome` | `app/agent/types.py` 370~417 `PendingResume.to_dict()` 키 = `version,mention,hints,pending_calls,held_drafts,dropped[,tag_by_answer,schedule,schedule_options,intent]` — **`person_ids` 없음**. `app/agent/loop.py` 294~313 `ResolveOutcome.person_ids: dict[str,int]` → `to_dict()["person_ids"]`, `_traced_resolve_mentions` 661행 `step=STEP_LOOP_RESOLVE_DONE` 의 output. 01-plan 23행이 가리킨 "loop.py 303·310행" 이 바로 `ResolveOutcome` 이다(계획이 클래스를 잘못 적음) | **구현자 주장 맞음** → R-U1-1 |
| ② `candidate_person_ids` 는 `judge.py` 523행 스키마 설명에만 | `grep -n candidate_person_ids app/` → `er/judge.py` 523행(변환기 docstring 예시) 1곳. 판정 스키마(112~116행)는 `matched_person_id/s_llm/reason` 뿐. 저장되는 곳 없음. 규칙 5 를 남긴 것은 과잉 삭제를 만들지 않는다(키가 있을 때만, 정수 원소만) | 맞음 — 방어적 유지 수용 |
| ③ `briefing_run` 은 일정 id 만 | `briefing/run.py` 313~324 output `{schedule_id_arg, selected, skipped[{schedule_id,reason}], briefed}` · input `{trigger, schedule_id, lead_hours}` | 맞음 — 01-plan 26행 "`briefing_run` … `person_id`" 는 부정확(R-U1-1 에 포함) |
| U1 보고 의무 ① 원칙8 — 평가가 운영 trace 를 쓰지 않는다 | `scripts/run_pilot_eval.py` 1268~1282 `_session`: 바깥 트랜잭션 + `create_savepoint`, "아무것도 커밋하지 않는다" · `evaluation/runner.py` 530·566~567 세이브포인트 rollback. 둘 다 실행 중 자기 세션의 trace 만 읽음 | 03-log 주장 맞음(R-2 범위 포함) |
| U1 보고 의무 ② `fact_sources` 교차 연결 | `FactSource(` 6곳: `promote.py` 222·235·260 — 이벤트 원천 284행 `select(Event).where(Event.person_id == person.id)` · `patterns.py` 244·266 — 135행 `Event.person_id == person.id` · `direct_facts.py` 114 — `event_ids_by_person[person_id]`(loop.py 967행, 그 인물 `add_event` 결과만). 전부 같은 인물 | 03-log "교차 없음" 맞음 |
| 핵심 위험 (거짓 양성) 같은 숫자의 다른 뜻 | `EventOut.id`·`ScheduleOut.id`(툴 이름으로 거름) · `question_id`·`pending_question_id`·`followup_question_id`·`trace_id`·`schedule_id`·`considered_event_ids`·`event_ids`·`subscription_ids`·`selected`·`briefed` — 어느 키도 규칙 키가 아니고, 문자열 안 숫자도 안 봄. 테스트 `test_same_number_other_meanings_is_not_reference`·`test_event_out_id_equal_to_person_id_is_not_reference` 등 | 지킴 |
| 핵심 위험 (거짓 음성) `type(v) is int` 가 JSONB 왕복 뒤에도 맞는가 | **직접 확인**(`evidence/20261109-1642-u1-review-jsonb-roundtrip.txt`, 테스트 DB `relationship_test` 세이브포인트 세션, rollback): `agent_traces.output`·`pending_questions.context` 에 `{person_id: 987654321, flag: True, as_str: "987654321", as_float: 987654321.0, candidate_ids{…}, person{id}, candidate_person_ids[…], nested[…]}` 저장 → 재조회 형 `int / bool / str / float` 전부 보존, `jsonb_typeof` = `number boolean string number`, `references_person(obj, 987654321)=True`·`(obj, 1)=False`(`True` 가 1 로 안 잡힘)·`(obj, 7)=True`, `output::text LIKE '%987654321%'` = True(U2 사전 거름 전제) | 지킴 |
| 원칙9 | trace 스키마·쓰는 코드 무변경(읽기 전용 판별 함수) | 영향 0 |
| 원칙1·2·4 | ER·임계치 코드 무변경 | 영향 0 |

## 3. 직접 재실행(evidence `docs/wiki/packages/P2b-person-delete/evidence/`, 전부 `save_evidence.py`)

| # | 명령 | evidence | 결과 | 대비 |
|---|---|---|---|---|
| 1 | `pytest tests/test_person_refs.py -q` | `20261109-1637-u1-review-pytest-target.txt` | **41 passed**, exit 0 | = 구현자 41 |
| 2 | `ruff check app tests` | `20261109-1637-u1-review-ruff.txt` | All checks passed!, exit 0 | 통과 |
| 3 | `pytest tests/ -q -rs` | `20261109-1637-u1-review-pytest-all.txt` | **2177 passed**, SKIPPED 줄 없음, exit 0 | = 2136 + 41 |
| 4 | `scripts/mypy_check.py --run` | `20261109-1643-u1-review-mypy-baseline.txt` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` | = 38 |
| 5a | **변이 RA**(구현자 V1-1~9 와 다름) — 런타임 치환 플러그인(`scratchpad/p2b-u1-review/mutplug_review.py`, `MUTANT=RA`): `_walk` 가 dict 값 중 **dict 만** 내려가고 list 는 안 내려감(재귀 워커의 흔한 실수) | `20261109-1641-u1-review-mutation-RA.txt` | **4 failed, 37 passed**, exit 1 — `test_person_ids_map_in_stored_context_literal` · `test_event_out_and_schedule_out_person_id`(`BriefingOut.recent_events[].person_id`) · `test_er_resolution_candidates_person_id`(`candidates[].person_id`) · `test_deep_nesting_and_top_level_list` | 검출 |
| 5b | **변이 RB** — 규칙 2(`person.id`)를 `tool_name` 이 있을 때만 적용 | `20261109-1641-u1-review-mutation-RB.txt` | **41 passed**, exit 0 — **살아남음** | R-U1-3 |
| 5c | 변이 뒤 저장소 상태 | `20261109-1642-u1-review-status.txt` | `?? app/api/delete.py` `?? tests/test_person_refs.py` 만, 추적 파일 변경 0(런타임 치환이라 원복 불필요) | 확인 |
| 6 | JSONB 왕복 형 보존(§2) | `20261109-1642-u1-review-jsonb-roundtrip.txt` | int/bool/str/float 보존, rollback | 확인 |

RB 가 살아남는 이유: 규칙 2 양성 테스트 두 개(`search_person`·`get_briefing` 픽스처)가 모두 `tool_name` 을 넘긴다. 현재 저장 모양에서 `person: {id}` 는 툴 output 에만 있어 **지금은 결함이 아니지만**, docstring 136~138행 "`tool_name` 은 규칙 3 에만 쓴다" 라는 계약을 테스트가 고정하지 않는다.

## 4. 소견

### [필수]

- **R-U1-1 01-plan·02-plan-verify 의 `resume.person_ids` 문구 보정(문서만, 메인 세션).** 코드에 `pending_questions.context["resume"].person_ids` 경로는 없다(§2 ①). 그런데 01-plan 23행(사실 3 표 "재개 재료 … `person_ids` = 언급→id 사전")·114행(V1-2 "`resume.person_ids` … 재개 재료 픽스처")·167행(해석 ㄴ "`resume.person_ids` 값")·26행(`briefing_run` 에 `person_id`)과, **내가 쓴** 02-plan-verify 74행("`resume.person_ids`(loop.py 303·310행 `PendingResume.person_ids: dict[str,int]`…) **일치**")이 그렇게 적혀 있다 — 303·310행은 `ResolveOutcome` 이다. U2 가 "사실 3 표의 쓰는 곳을 전부 한 번씩 지나가는지 대조"(리스크 1)할 때 표가 틀리면 `loop_resolve_done` 행을 빠뜨릴 수 있다. 제안 문구 —
  - `01-plan.md` 36행 뒤(사실 7 아래) 1줄: "**보정(U1, 2026-11-09, review-u1-person-refs R-U1-1)**: 23행 `person_ids` 는 `pending_questions.context["resume"]` 가 아니라 `ResolveOutcome.to_dict()` = `agent_traces` `loop_resolve_done.output`(loop.py 294~313행)에 있다(`PendingResume.to_dict()` 에는 없다, types.py 400~417행) — V1-2·해석 ㄴ 의 `resume.person_ids` 도 `loop_resolve_done.output.person_ids` 로 읽는다. 24행 `candidate_person_ids` 는 judge.py 523행 변환기 설명에만 있고 저장되지 않는다(규칙 5 는 방어적으로 유지). 26행 `briefing_run` output 은 일정 id(`selected/briefed/skipped[].schedule_id`)만 담고 `person_id` 는 `briefing_compose`·`briefing_error` 에만 있다. 규칙 ①~⑤ 는 그대로."
  - `02-plan-verify.md` 사실 검증 표 74행 끝에 덧붙임(또는 표 아래 1줄): "**보정(U1 리뷰 2026-11-09)**: `resume.person_ids` 는 오기 — loop.py 303·310행은 `ResolveOutcome.person_ids`(`loop_resolve_done.output`)이고 `PendingResume.to_dict()` 에 `person_ids` 는 없다. 모양 자체(언급→id 사전, 규칙 4)는 맞다."
  - 닫힘 확인: `grep -n "R-U1-1" docs/wiki/packages/P2b-person-delete/01-plan.md docs/wiki/packages/P2b-person-delete/02-plan-verify.md` 각 1건 이상.

### [권고]

- **R-U1-2 docstring "7곳" → "8곳"(backend-agent, U2 에서 같은 파일을 열 때).** `delete.py` 25행의 열거(2+1+1+3+1)는 8곳이고 내 grep 도 8곳이다(§2). `03-log.md` U1 항목 "7곳" 도 같은 숫자다 — 03-log 는 고쳐 쓰지 않는 로그이므로 U2 항목에 "U1 의 7곳은 8곳의 오기" 한 줄로 바로잡는다.
- **R-U1-3 규칙 2 를 `tool_name` 없이 고정하는 테스트 1건(backend-agent, 테스트만, U2 커밋에 포함 가능).** §3 5b 변이 RB 가 살아남는다. `references_person({"person": {"id": PID}}, PID) is True` 와 `to_jsonable([Candidate(...)])` 를 `tool_name` 없이 True 로 단언하는 1건(이름 예 `test_person_object_id_does_not_need_tool_name`)이면 닫힌다. U2 가 `input`·`pending_questions.context` 판정에 `tool_name` 을 넘기지 않으므로 이 계약은 U2 가 기대는 것이다.
- **R-U1-4 "남는 행" 목록 보완(docstring 53~57행 + security §5 구현 줄, U5/메인).** 결정 G (i) 한계로 남는 것 중 docstring 이 적지 않은 것: `loop_turn` input/output 의 `pending_question.question/options`(후보 **이름**이 든 질문 문장, id 없음) · `loop_extract.output.tool_calls[].args.person`(언급 문자열) · `loop_record.output.executed[]`(인덱스·trace_id 만) · `push_send.output.payload.title/body`(이름이 들 수 있으나 같은 행 input 에 `person_id` 가 있어 **행 자체는 지워짐** — 남지 않음, 참고). 처음 둘은 이름이 남는 사례라 security §5 "완전 삭제" 한계 문장에 들어가야 한다(리스크 3).
- **R-U1-5 `tests.md` 상단 "함수 30개, 파라미터 포함 41건" 은 맞다** — 참고로만 적는다(`grep -c "^def test_"` = 30, 2 + 11 parametrize). 수정 없음.

## 5. 판정

**결과: 보류.**
근거: 코드는 결정 C-3 확정 규칙 ①~⑤ 와 상수·테스트 수준에서 1:1 이고, 위임 범위 안(새 파일 2개, 추적 파일 변경 0)이며, 거짓 양성(같은 숫자의 다른 뜻)·거짓 음성(JSONB 왕복 뒤 `int` 보존)을 각각 테스트와 실 DB 왕복 evidence 로 확인했다. 전수 조사를 내가 다시 돌려(쓰기 8곳 + `ask_payload` 4곳 + `to_jsonable` 저장 2곳, to_dict 14종) 표 밖 모양이 없음을 확인했고, 구현자가 보고한 "계획과 다른 점" 3건은 모두 코드가 맞다. 41/2177 passed·ruff·mypy 38=38 직접 재실행, 변이 RA 1건 검출(4 FAIL). 그러나 **계획(01-plan 사실 3 표·V1-2·해석 ㄴ)과 내 02-plan-verify 가 코드에 없는 경로(`resume.person_ids`)를 사실로 적고 있어** 문서 보정 2줄(R-U1-1)이 들어가야 통과다 — 제품 코드 수정 0, 재리뷰는 grep 확인만.

한 줄: 코드·테스트·전수 조사·JSONB 왕복 전부 맞고 변이도 잡히나, 계획과 계획 검증 문서가 코드에 없는 `resume.person_ids` 경로를 사실로 적어 보류 — 문서 2줄(01-plan·02-plan-verify), 코드 변경 0. [필수] 1 · [권고] 4.
