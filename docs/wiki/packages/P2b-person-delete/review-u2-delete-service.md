# P2b-person-delete · U2(삭제 서비스 `delete_person`) 커밋 전 리뷰

검토자: verifier (fable)
일시: 2026-11-13 (작성 마무리 2026-11-14)
대상: 작업 트리 미커밋 변경(HEAD `a4b44b1`, 브랜치 `dev2`) — `app/api/delete.py`(수정, blob `4823f967…`) · `tests/test_person_refs.py`(수정, blob `761e5055…`, R-U1-3 1건) · `tests/test_person_delete.py`(신규, blob `4ade6e27…`) · `docs/wiki/packages/P2b-person-delete/tests.md`(U2 절·변이 표·사실 3 대조 표). 그 밖의 미커밋 변경(`HANDOFF.md`·`journal.md`·`review-u1-person-refs.md` §6·P5b/L-007 evidence)은 대상 밖. `git status --short -- app tests` = 위 3파일뿐(`evidence/20261113-2051-u2-review-status.txt`).
결과: **통과** — [필수] 0 · [권고] 5. 코드는 01-plan U2 ①~⑦ 순서·결정 A·C·D·E·F·H·K 와 1:1 이고, 거짓 양성(같은 숫자의 다른 뜻·다른 사용자 행)·거짓 음성(센티널 텍스트 0)·쓰기 0·트랜잭션 경계를 테스트와 직접 실행으로 확인했다. 66/2202 passed(skip 0)·ruff·mypy 38=38·`alembic check` 무변경을 직접 재실행했고, 구현자와 **다른** 변이 2건(RA·RB)이 각각 4 FAIL·2 FAIL 로 잡혔다. 구현자의 "V2-3 동치" 주장은 코드 구조(FK 없음·id 목록 선계산)로도, 재실행(24 passed)으로도 맞다. 전체 pytest 20분 지연은 재현되지 않았다(벽시계 28초).

---

## 1. 본 것

| 파일 | 줄 | 본 내용 |
|---|---|---|
| `app/api/delete.py` | 1~2·25 | docstring Refs 에 `U2` 추가, "7곳"→"**8곳**"(R-U1-2 닫힘 — 열거 2+1+1+3+1 = 8 과 일치) |
| 같은 파일 | 71~88 | `sqlalchemy` `Text, cast, delete, func, or_, select` · 모델 8종 · `_owned_person`(`app/tools/persons.py` 417행 재사용, 중복 구현 없음) · `ConfirmationRequired` · `CONFIRM_REASON = "person_delete"` |
| 같은 파일 | 175~183 | `PersonDeleteSummary{person_id, deleted}` frozen dataclass, `to_dict()` 는 `deleted` 를 복사 — 결정 F 의 키 8개와 순서(persons·person_aliases·person_facts·fact_sources·events·schedules·pending_questions·agent_traces) 일치, 이름·원문 없음 |
| 같은 파일 | 190~201 | `_referencing_question_ids`: `cast(context, Text).like('%<id>%')` 사전 거름 → `references_person(row.context, person_id)` (`tool_name` 없음) → `id` 목록. `order_by(id)` |
| 같은 파일 | 204~224 | `_referencing_trace_ids`: `input::text LIKE OR output::text LIKE` → `references_person(output, tool_name=row.tool_name) or references_person(input)` — U1 계약(output 만 `tool_name`) 그대로. **세션·user 조건 없음**(결정 K (a) 전 세션) |
| 같은 파일 | 227~270 | `delete_person`: ① `_owned_person`(없음·남의 것 → `PersonNotFound`) ② `confirm is None or confirm != person.display_name` → `ConfirmationRequired("person_delete")` — 가공(strip·casefold) 없음, 결정 A-2 "정확히 같은지" ③ 건수 집계(질문·trace id 목록 먼저, `_count` 6회, `fact_sources` 는 `fact_id IN(그 인물 facts) OR event_id IN(그 인물 events)` — CASCADE 두 경로 모두) ④ `delete(PendingQuestion).where(id.in_(…))` ⑤ `delete(AgentTrace).where(id.in_(…))` ⑥ `delete(Person).where(id == pid).where(user_id == user_id)` 한 문장 ⑦ `commit`·`AgentTrace(` 없음. `person_id` 는 `int` 라 LIKE 패턴에 외부 문자열이 들어가지 않는다 |
| `tests/test_person_refs.py` | 167~174 | `test_person_object_id_does_not_need_tool_name` — `{"person":{"id":PID}}` 와 `to_jsonable([Candidate(...)])` 를 `tool_name` 없이 True, OTHER 는 False. U1 리뷰 변이 RB(규칙 2 를 `tool_name` 있을 때만)를 이제 잡는다 → R-U1-3 닫힘 |
| `tests/test_person_delete.py` | 전체(약 830줄) | 함수 16개 + parametrize 7·3 = **24건**. 픽스처 `world` 는 손으로 만든 JSON 이 아니라 `run_turn`(merge 1·identity 되묻기 2(미답변·`answer_question` 답변)·대조군 merge 1·다른 사용자 되묻기 1)·`run_briefings`(`FakeBriefingComposer`)·`after_record` 승격(`_AllEventsExtractor`)+패턴(conflict 5건) 이 남긴 JSONB. 센티널 `persons.id=987654321` 명시 삽입(`Identity(always=False)`, models.py 85행). decoy 테스트(`test_traces_same_digits_in_other_roles_are_not_deleted`)만 `AgentTrace(`·`PendingQuestion(` 을 직접 만든다 — 같은 숫자가 `EventOut.id`·`ScheduleOut.id`·`considered_event_ids`·`schedule_id`·`question_id`·`event_ids` 역할인 행 3+1 은 남고, `input.person_id`·`EventOut.person_id`·`create_person` output 최상위 `id`·`candidate_ids`·`resume.schedule.person_id` 인 행 3+1 만 지워진다(`deleted.agent_traces == 3`, `pending_questions == 1`) |
| 같은 파일 | 전제 테스트 | `test_world_sentinel_is_planted_…` 가 삭제 **전** 센티널이 질문 2·trace input/output >0·이벤트 5·일정 1·별칭 2·사실 키 `{likes, pattern:conflict, 취미}`·근거 링크 >0 임을 단언 — "삭제 뒤 0" 이 공허하지 않음을 보장(항상 통과하는 테스트가 아니다) |
| `tests.md` | U2 절 | 표 16행(parametrize 는 1행) — `pytest -v` 이름과 1:1(`evidence/20261109-1700-u2-person-delete.txt`). 변이 표 V2-1~V2-11(V2-3 동치 생존 명시). 사실 3 대조 표 9행 — 미통과 3곳(`tool_error`·`resume.schedule.person_id`·`push_send`)을 숨기지 않고 적음 |
| 구현자 evidence | `20261109-1657-u2-mutation.txt`(기준 24 passed + 변이 11회 append, V2-3 만 24 passed) · `20261109-1700-u2-person-delete.txt`(66 passed) · `-j1~j5-*.txt`(J-1 ③ `grep-exit=1` = 자식 테이블 직접 삭제 0줄) · `-pytest-all.txt`(2202 passed, 1 warning in 31.83s, **명령 시각 17:00:50**) · `20261109-1722-u2-{alembic-check,mypy,ruff,scope,tools-check}.txt`(17:22:22) | 보고와 일치. 단 pytest-all 의 pytest 내부 시간 31.83초와 다음 증거 시각 사이 **약 21분** 간격 — §3 #9 |
| 계획 | `01-plan.md` 124~136행(U2·V2 표)·결정 A·C·D·E·F·G·H·J·K(204~349행)·리스크 1~8·판정 J-1~J-5·J-7·J-10~J-12 · `review-u1-person-refs.md` R-U1-2·3 | §2 |

## 2. 계획·카드 대조 (위임문 "특히 볼 것" 1~6 포함)

| 항목 | 근거(코드 직접 확인) | 판정 |
|---|---|---|
| **1. 소유 확인 → 확인값 검사 순서, 남의·없는 인물에서 쓰기 0**(결정 E·A) | `delete.py` 243행 `_owned_person` 이 244행 비교보다 먼저. `_owned_person` 은 `select(Person).where(id).where(user_id)` 읽기만(persons.py 424~428). 테스트 `test_other_user_person_is_not_found_whatever_the_confirm_is[맞는 값·None·틀린 값]` 3건 — 확인값이 **맞아도** `PersonNotFound` + `assert_no_writes`(9테이블 행 수·`briefed_at`·`updated_at`) · `test_not_found_for_missing_id_even_with_any_confirm` · 변이 V2-4(`user_id` 무시) 3 FAIL | 일치 |
| **2. 거짓 양성 — 다른 인물·다른 사용자의 질문·trace 를 지우는 경로**(결정 K) | JSONB 두 질의(196~200·209~218행)에는 `user_id`·`session_id` 조건이 **없다**. 결정 K "사용자 범위는 `user_id` 로 한정" 은 질의가 아니라 **① `_owned_person`(그 id 가 요청 사용자 것일 때만 진행) + ② `persons.id` 가 전역 단일 IDENTITY(models.py 83~85, 0001 60행)라 "같은 인물 id 가 다른 사용자의 인물을 가리키는" 행이 존재할 수 없다** 로 성립한다. 다른 사용자의 trace 가 이 인물 id 를 담는 경로가 있는지 — 인물 id 를 JSONB 에 넣는 쓰기 코드는 모두 `user_id` 로 걸러진 조회에서 나온다: `search_person`(persons.py 178·204·219 `Person.user_id == ctx.user_id`) · ER 후보(`er/candidates.py` 70) · `update_person`/`add_event`/`add_schedule`/`get_briefing`/승격(`_owned_person`, persons.py 540·promote.py 279) · 브리핑 일정 선택(`briefing/select.py` 61·76 `join(Person).where(Person.user_id)`) · 푸시(`push_send.input.person_id` 는 그 선택된 일정의 인물). 남는 단일 사각은 `pending_questions` 의 `user_id` 격리 부재(F-fbaaae, questions.py 57~62·248~251 — **기존 열린 소견**, 현재 단일 사용자 `app_user_id()` 고정)인데, 그 경우에도 재개 ctx 는 질문 행의 `session_id` 와 `app_user_id()` 로 만들어져(deps.py 136~155) 인물 id 는 여전히 그 인물 소유자의 것이다. 따라서 "참조하는 모든 행 = 그 인물에 관한 행" 이며, 지우는 것은 소유자가 명령한 그 인물의 흔적이다. 같은 숫자의 **다른 뜻**은 decoy 테스트가, 숫자가 없는 행의 값 불변은 `test_traces_control_only_and_unrelated_rows_are_unchanged`(`_unrelated_jsonb_rows` 전후 `==`, 다른 사용자 질문 포함)가 지킨다. 변이 V2-6(LIKE 결과 전부 삭제) 1 FAIL(6 != 3) | 성립 — 단, "`user_id` 한정" 의 실제 메커니즘은 03-log 에 위와 같이 적어야 한다(R-U2-4) |
| **3. 거짓 음성 — 사실 3 표에서 센티널이 지나가지 않은 3곳** | `tool_error`: `tools/context.py` 187~190 `input_payload = to_jsonable(bound.arguments)` → `person_id` 인자(int)가 키 `person_id` 로 깊이 1 → 규칙 1. `push_send`: `push/notifier.py` 239~243 `input={"schedule_id","person_id","subscription_ids"}` → 규칙 1. schedule 질문 `resume.schedule.person_id`: `ScheduleResumeRef.to_dict`(types.py 361~366, U1 리뷰 확인) → 규칙 1 깊이 3. 규칙 1 은 깊이 무관(`_walk` 재귀, U1 `test_deep_nesting_and_top_level_list`)이고 decoy 질문 행이 `resume.schedule.person_id` 리터럴 모양을 실제 DB 왕복으로 덮는다. **이 커밋을 막을 근거는 아니다.** 그러나 세 쓰는 곳의 실제 호출 경로가 바뀌어도(예: 인자 이름 변경) U2 그물이 모르는 상태라, `tool_error` 만이라도 world 에 넣는 것이 싸다(센티널에 `add_event(type="없는값")` 1회 → `tool_error` trace) | 충분(커밋 기준) · R-U2-2 권고 |
| **4. V2-3 동치 주장** | 정리 단계는 `question_ids`·`trace_ids` 를 ③ 에서 **미리** 구해 `id IN (…)` 으로 지운다 — 인물 행을 다시 조회하지 않는다(252~268행). `pending_questions`·`agent_traces` 에는 `persons` 로 가는 FK 가 없다(`grep ForeignKey models.py` → 133·152·175·178·195·212 여섯 곳만, evidence `u2-review-status.txt`) → CASCADE 가 두 테이블에 닿지 않는다. 그러므로 "정리를 `persons` 삭제 뒤로" 는 결과가 같다. **직접 재실행**: 구현자 플러그인 `MUT=V2-3` → 24 passed(`evidence/20261113-2051-u2-review-v2-3-equivalence.txt`). 계획 V2-3 의 전제 "(인물 없음 → 조회 실패로 건너뜀)" 은 이 구현 구조에 해당하지 않는다 — 구현자 설명이 맞다. 다만 `delete.py` 232행 docstring 은 "변이 V2-3·V2-5·V2-7 이 지킨다" 라고 적어 V2-3 이 잡히는 것처럼 읽힌다 | 주장 맞음 · R-U2-1(docstring) |
| **5. 트랜잭션** | 서비스에 `commit()`·`rollback()`·`begin()` 없음. 호출자 계약: `app/api/deps.py` 120~130 `get_session` — "정상 종료 시 commit, 예외 시 rollback, 항상 close". 세 DELETE 가 한 트랜잭션 안이므로 중간 예외(예: ⑤ 에서 DB 오류) 시 ④ 가 되돌려져 부분 삭제 없음. `ConfirmationRequired`·`PersonNotFound` 는 쓰기 전 발생(`assert_no_writes` 10건). `test_service_does_not_commit_outer_rollback_restores_everything` 가 SAVEPOINT 안 삭제 → rollback → 6군데 상태·9테이블 스냅샷 복원을 단언, 변이 V2-8(`commit()` 호출) 1 FAIL(`ResourceClosedError`). 01-plan U2 ⑦ "트랜잭션 경계는 `get_session`, P2 결정 2" 와 일치. U3 는 `Depends(get_session)` 으로 서비스를 호출하고 결과를 그대로 돌려주면 된다(라우트가 commit 을 따로 부르지 않는다) | 일치 |
| **6. 전체 pytest 시간** | §3 #9 — 벽시계 **28초**(20:47:30 → 20:47:58), pytest 내부 26.84초. 두 새 파일 2.82초, 가장 느린 setup 0.27초(`world`). 실행 직후 `pg_stat_activity`: `relationship%` DB 다른 연결 **0**, `pg_locks` 미승인 **0**(`ps` 에 고아 pytest 없음). 구현자 증거는 pytest 내부 31.83초였고 명령 시각 17:00:50 → 다음 증거 17:22:22 — 간격이 **pytest 타이머 밖**(세션 시작 전 import 또는 종료 후 프로세스 정리)에 있어 테스트 본문·락 대기(락 대기였다면 fixture setup 시간으로 타이머 **안**에 잡힌다)로는 설명되지 않는다. 이 단위의 테스트가 원인이라는 증거 없음(같은 테스트가 포함된 내 전체 실행이 28초) | 재현 안 됨 — 원인 미확정으로 03-log 에 기록(R-U2-4) |
| 결정 A-2 "공백·대소문자 가공 없음" | 244행 원문 비교. `test_confirm_missing_or_mismatch_…` 7건(None·""·다른 이름·앞 공백·뒤 공백·한 글자 다름·대조군 이름) + `test_confirm_uses_current_display_name_not_alias`(이름 변경 뒤 옛 이름·별칭 거부). 내 변이 RB(`strip()` 정규화) 2 FAIL | 일치 |
| 결정 C-1 답변 여부 무관 | `_referencing_question_ids` 에 `answered_at` 조건 없음. `test_pending_questions_referencing_person_are_deleted_answered_or_not`(미답변 1·답변 1 삭제, `deleted.pending_questions == 2`, 다른 사용자 질문 5필드 동일). 변이 V2-10 3 FAIL | 일치 |
| 결정 C-2·C-3 행 통째 삭제 + LIKE 사전 거름 + 정밀 판정 | 209~224행. `test_traces_no_sentinel_text_remains_in_input_or_output`(3종 텍스트 0) · `test_traces_covering_each_shape_in_the_scenario_are_deleted`(삭제 전 step/tool 9쌍 존재 → 삭제 뒤 ∅). 내 변이 RA(사전 거름이 `input` 만) 4 FAIL — `assert 9 == 0`·`er_resolve/search_person` 잔존·건수 불일치·decoy `1 != 3` | 일치 |
| 결정 D CASCADE 한 문장, 앱이 자식 삭제 안 함 | 269행 `delete(Person)` 한 문장. J-1 ③ grep `delete\((PersonAlias\|PersonFact\|Event\|Schedule\|FactSource)\)` → **0줄**(`grep-exit=1`, evidence `u2-review-status.txt`). `test_cascade_removes_every_row_…` 6군데 `[]` + 대조군·다른 사용자 인물 상태 동일 + `push_subscriptions` 수 불변. `alembic check` "No new upgrade operations detected."(`u2-review-alembic-check.txt`) | 일치 |
| 결정 F 건수 = 시드 | `test_summary_counts_equal_seeded_counts` — `to_dict()` 전체를 값으로 비교(aliases 2·facts 3·events 5·schedules 1·questions 2, `fact_sources ≥ 3`, `agent_traces ≥ 10`). `expected_traces` 는 테스트가 LIKE 로 독립 집계(정밀 판정이 LIKE 집합과 같다는 전제 — 센티널 숫자는 다른 시퀀스가 닿지 않으므로 이 world 에서 성립). 변이 V2-7 1 FAIL | 일치 |
| 결정 H trace 없음 | `delete.py` 에 `AgentTrace(` 생성 없음, `@traced` 아님. `test_traces_delete_writes_no_trace_row`(전체 trace 수 = 전 − 삭제 건수) | 일치 |
| 결정 I·J 범위 / J-11·J-12 | `app/` 변경 = `app/api/delete.py` 만, `app/tools`·`agent`·`er`·`memory`·`briefing`·`push`·`db`·`alembic` 무변경(`20261109-1722-u2-scope.txt`), `git diff --diff-filter=M f67d8e4 -- tests/` 빈 출력(`u2-review-status.txt` — `test_person_refs.py` 는 f67d8e4 기준 **A**). `tools_check 7/7` | 일치 |
| 원칙8 | 테스트는 `Fake*` 공급자만(네트워크 0), 삭제는 `reports/`·평가 재료를 건드리지 않음 | 영향 0 |
| 원칙9 (C-2 비용 수용) | 그 인물이 후보로만 끼인 ER 행도 지워진다 — 사용자가 C-2 (a) 를 선택했고 01-plan 에 비용이 적혀 있다 | 계획대로 |
| R-U1-2·R-U1-3 (U1 권고) | 25행 "8곳" · `test_person_object_id_does_not_need_tool_name` | 둘 다 닫힘 |

## 3. 직접 재실행 (evidence `docs/wiki/packages/P2b-person-delete/evidence/`, 전부 `save_evidence.py`, `POSTGRES_PORT=5433`)

| # | 명령 | evidence | 결과 | 대비 |
|---|---|---|---|---|
| 1 | `pytest tests/test_person_delete.py tests/test_person_refs.py -q --durations=8` | `20261113-2047-u2-review-pytest-target.txt` | **66 passed** in 2.82s, 가장 느린 항목 setup 0.27s, exit 0 | = 구현자 66 · 메인 3.3s |
| 2 | `ruff check app tests` | `20261113-2047-u2-review-ruff.txt` | All checks passed!, exit 0 | 통과 |
| 3 | `scripts/mypy_check.py --run` | `20261113-2047-u2-review-mypy.txt` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` | = 38 |
| 4 | `date; pytest tests/ -q -rs; date` | `20261113-2047-u2-review-pytest-all.txt` | **2202 passed**, 1 warning in 26.84s, SKIPPED 줄 없음, `pytest-exit=0`, **start 20:47:30 / end 20:47:58**(벽시계 28초) | = 2177 + 25 |
| 5 | **변이 RA**(구현자 V2-1~11 과 다름) — `_referencing_trace_ids` 의 SQL 사전 거름이 `input` LIKE 만(판정은 원본 그대로; "판정만 input" 인 V2-2b 와 다른 단계) | `20261113-2050-u2-review-mutation-RA.txt` | **4 failed, 62 passed**, exit 1 — `test_traces_no_sentinel_text_…`(`assert 9 == 0`) · `test_traces_covering_…`(`er_resolve`/`search_person` 잔존) · `test_summary_counts_…` · `test_traces_same_digits_…`(`1 != 3`) | 검출 |
| 6 | **변이 RB** — 확인값 비교를 `confirm.strip() != display_name.strip()` 으로(V2-11 과 다름) | `20261113-2050-u2-review-mutation-RB.txt` | **2 failed, 64 passed**, exit 1 — `test_confirm_missing_or_mismatch_…[앞 공백]`·`[뒤 공백]` DID NOT RAISE | 검출 |
| 7 | 구현자 V2-3 재실행(`MUT=V2-3`, 구현자 플러그인) | `20261113-2051-u2-review-v2-3-equivalence.txt` | **24 passed** — 동치 변이 확인 | 구현자 주장 맞음 |
| 8 | `alembic check` | `20261113-2051-u2-review-alembic-check.txt` | `No new upgrade operations detected.` | J-7 선행 확인 |
| 9 | DB 상태(`pg_stat_activity`·`pg_locks`, 전체 실행 직후, 읽기 전용) · `ps aux \| grep pytest` | 본문 기록(출력: `connections: 0` · `ungranted locks: 0` · 고아 프로세스 없음) | 락 대기·세션 누수 흔적 없음 | §2 6행 |
| 10 | 변이 뒤 저장소 상태·blob·J-1 grep·FK 목록 | `20261113-2051-u2-review-status.txt` | ` M app/api/delete.py` ` M tests/test_person_refs.py` `?? tests/test_person_delete.py` 만, `--diff-filter=M f67d8e4 -- tests/` 빈 출력, HEAD `a4b44b1` dev2(런타임 치환이라 원복 불필요) | 확인 |

변이 플러그인: `scratchpad/p2b-u2-review/mutplug_review.py`(저장소 밖, `pytest -p mutplug_review`, `MUTANT=RA|RB`). RA 가 잡히는 이유는 world 에 `input` 에는 센티널이 없고 `output` 에만 있는 행(`search_person`·`er_resolve` 후보, `create_person` 류)이 실제로 쌓이기 때문이다 — 전제 테스트가 `AgentTrace.output` 히트 >0 을 먼저 단언한다.

## 4. 소견

### [필수]

없음.

### [권고]

- **R-U2-1 `delete.py` 232행 docstring "변이 V2-3·V2-5·V2-7 이 지킨다" → V2-3 제외(backend-agent, docstring 한 줄, 이 커밋 또는 U3 에서).** V2-3 은 동치 변이라 어떤 테스트도 잡지 않는다(§3 #7, `tests.md` 변이 표도 그렇게 적음). "순서가 계약" 인 것은 ①②(쓰기 0)와 ③(집계가 삭제 전)이며, ④⑤ 와 ⑥ 의 순서는 결과에 영향이 없다 — docstring 이 그 사실과 어긋난다. 제안: "변이 V2-5·V2-7 이 지킨다. ④⑤ 와 ⑥ 의 순서는 결과를 바꾸지 않는다(id 목록을 미리 구하고, 두 테이블에 `persons` FK 가 없다 — V2-3 동치)".
- **R-U2-2 사실 3 대조 미통과 3곳 중 `tool_error` 를 world 에 넣기(backend-agent, 테스트만, U5 전까지).** 센티널 인물에 `add_event(type="없는값")` 같은 실패 호출 1회면 `tool_error` trace(`input.person_id`)가 실제 경로로 쌓이고 `test_traces_covering_…` 의 쌍 목록에 `("tool_error", "add_event")` 를 더할 수 있다. `push_send`(가짜 sender 필요)·schedule 질문(`_ask_schedule` 경로)은 비용이 커서 U1 단위 테스트 + decoy 로 두는 것을 수용한다 — 03-log 에 "리스크 1 한계" 로 적는다.
- **R-U2-3 `registry.md` 에 `app/api/delete.py` 행(메인, U2 커밋 또는 U5).** `grep -n "P2b\|delete.py" docs/wiki/registry.md` → 0건. 01-plan 리스크 2 가 "이 의무를 `registry.md` 의 `app/api/delete.py` 행 비고와 모듈 docstring 에 적는다" 고 했는데 docstring(59~63행)만 있다. 비고에 "인물 id 를 새 키 이름으로 JSONB 에 넣는 패키지는 `PERSON_REF_RULES` 갱신" 과 `references_person`·`delete_person`·`PersonDeleteSummary` 를 올린다.
- **R-U2-4 03-log U2 항목에 기록할 사실 4가지(메인).** ① 결정 K "`user_id` 한정" 의 실제 메커니즘 = `_owned_person` + 전역 IDENTITY(JSONB 질의 자체에는 사용자 조건이 없다, §2 2행) ② V2-3 은 동치 변이(계획 V2-3 전제 "인물 없음 → 조회 실패로 건너뜀" 은 이 구현 구조에 해당 없음) ③ 전체 pytest 약 20분 지연은 verifier 재실행에서 재현되지 않음(벽시계 28초, 락·연결 잔존 0) — 구현자 증거의 간격은 pytest 타이머 밖, 원인 미확정 ④ 사실 3 대조 미통과 3곳(`tool_error`·`push_send`·schedule 질문)과 그 근거(규칙 1, 쓰는 코드 줄).
- **R-U2-5 `test_summary_counts_equal_seeded_counts` 의 `expected_traces` 는 LIKE 집계다(참고, 수정 없음).** 정밀 판정 결과와 LIKE 집합이 같다는 전제는 센티널 world 에서만 성립한다(다른 시퀀스가 987654321 에 닿지 않음). 이 전제가 깨지는 경우(같은 숫자의 다른 뜻)는 decoy 테스트가 값 3·1 로 따로 고정하므로 결함이 아니다 — 두 테스트가 한 쌍이라는 것만 `tests.md` 행에 한 줄 덧붙이면 좋다.

## 5. 판정

**결과: 통과.**
근거: `delete_person` 은 01-plan U2 ①~⑦ 과 결정 A(원문 비교)·C-1/C-2/C-3(행 삭제·LIKE 사전 거름·`references_person` 정밀 판정, output 만 `tool_name`)·D(CASCADE 한 문장, 자식 직접 삭제 0줄)·E(소유 확인 먼저, `PersonNotFound`)·F(건수 8키)·H(trace 없음)·K(전 세션)와 코드 줄 단위로 1:1 이고, 쓰기 0 과 트랜잭션 경계(`get_session` commit/rollback)가 테스트·변이로 고정돼 있다. 거짓 양성은 전역 IDENTITY + `_owned_person` 으로 성립함을 쓰는 코드 6곳의 `user_id` 조건으로 확인했고 decoy·불변 테스트가 지킨다. 거짓 음성은 실제 경로가 쌓은 JSONB 에서 센티널 텍스트 0 으로 증명되며, 미통과 3곳은 규칙 1(깊이 무관)과 쓰는 코드 줄로 덮인다. 66/2202 passed(skip 0)·ruff·mypy 38=38·`alembic check` 를 직접 재실행했고, 구현자와 다른 변이 RA·RB 가 각 4·2 FAIL 로 잡혔다. V2-3 동치 주장은 구조와 재실행 모두 맞다. 20분 지연은 재현되지 않았고 이 단위의 테스트가 원인이라는 증거가 없다. [필수] 0 이므로 커밋을 막을 근거가 없다 — [권고] 5건은 docstring 한 줄·테스트 보강·registry·03-log 기록이며 코드 동작 변경이 아니다.

한 줄: 순서·쓰기 0·CASCADE·JSONB 정리·트랜잭션 전부 계획과 일치, 66/2202 passed·변이 RA·RB 검출·V2-3 동치 확인·20분 지연 재현 안 됨 — **통과**. [필수] 0 · [권고] 5(R-U2-1 docstring V2-3 문구 · R-U2-2 `tool_error` 경로 · R-U2-3 registry 행 · R-U2-4 03-log 기록 4건 · R-U2-5 참고).
