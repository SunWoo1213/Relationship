# P5b-query-turn U5 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`resume_turn` `answerer=None` + `_resume_query_turn`, U4 ③~⑥ → `_query_finish` 공용 꼬리) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 3(R-U5-1 생존 변이 V7 = 재개 후보 답 카드 `PersonNotFound`(사용자 수용 판단 ①) 테스트 공백 — 코드는 맞고 내 (v-e) 직접 확인이 덮는다, U6 에서 테스트 1건 권고 / R-U5-2 `resume_turn` docstring 이 조회 재개 분기를 설명하지 않음(identity 절은 `update_person` 경로만, trace 절은 FIX-035 만 예외로 적음) / R-U5-3 구현자 변이 러너의 스크래치패드 저장소 사본(`p5b-u5/repo`)에 `.env` 가 들어 있음 — journal 2026-11-02 에 이미 기록·사용자에게 삭제 명령 전달됨, 커밋 전 삭제 확인 권고). 코드 결함은 찾지 못했다. 공용 헬퍼 분리 동일성: U4 커밋 `18219ba` 의 `_run_query_turn` 꼬리(③~⑥) 와 현재 `_query_finish` 본문이 이동한 1줄(`dropped = …`) 외 문장 단위 동일, `_run_query_turn` 머리 동일, `resume_turn` 본문 `-` 0줄·`+` 12줄(시그니처 1 + 분기 11). 계약 값 직접 확인 95 PASS / 0 FAIL(2회차; 1회차 3 FAIL 은 내 스크립트 오류 — `PersonCardOut` 속성명 2, D1 게이트가 거부한 합성 new_person 행 1), 변이 22건 적용(계획 표 3 + 내 변이 19) 중 검출 21·생존 1·동등 0, U4+U5 파일 33 passed(U4 23건 무수정), 회귀 9파일 283 passed, 전체 2114 passed(2104 + 10)·skip 0, ruff 통과, `tools_check` 7/7, 범위 밖 diff 0, 기존 테스트 파일 수정 0, `loop.py` 의 `-` 줄 1(이동).
대상: 작업 트리(HEAD `18219ba` = U4, 무변경 기준 `8a8767b`) — `git diff HEAD -- app`(`--numstat` `app/agent/loop.py 108 1`, 1파일) · `tests/test_agent_query_loop.py`(`git diff --numstat 18219ba` `322 0`, 수집 23 → 33 = 함수 8 추가, 그중 2개 parametrize 2건) · `docs/wiki/registry.md` 비고 2곳(`loop.py` 행 "P5b U5(해시 pending)" 추가 · 테스트 행 23 → 33건) · `docs/wiki/packages/P5b-query-turn/tests.md` U5 절(8행) · 구현 증거 `evidence/20261102-1327-u5-mutation.txt`·`20261102-1328-u5-{diff-filter,loop,pytest-all,regression,ruff,scope,tools-check,u4-tests-untouched}.txt`(9). `HANDOFF.md`·`journal.md`·`03-log.md` 의 문서 diff 는 위임대로 리뷰 대상 아님(03-log 에 U5 항목이 아직 없고 U4 항목에 커밋 해시 한 줄만 추가된 사실을 §7 에 적는다). 구현자의 자기 평가(`tests.md` 의 "M1~M15 전부 검출"·구현 변이 증거)는 판정 근거로 쓰지 않았다 — 아래 수치는 전부 내 실행이다.
근거 문서: `01-plan.md` 111~114행(U5 계약·테스트 4·변이 3) · 86~87행(구현 제약 (1)~(5)) · 결정 G(257~266행 — 재개 재료 `intent` 1필드·version "1"·후보 답 (a) 저장 0·거절 답 "기록이 없어요" 후속 질문 없음·trace `loop_resume → loop_query → loop_turn`) · 결정 I (a) · 결정 C(`loop_query.output` 10키·`resolutions[]` 6키·답한 턴 `stop_reason=None`·`loop_resolve_done`/`loop_record` 없음) · 결정 F(힌트 순서·`QUERY_MORE_HINT` 는 llm 뿐) · 결정 K(R-1 모듈 속성 호출) · `D16-query-turn.md` 결정 2·3·9·"코드에서 지켜야 할 것" 3~5 · `S3.4-ask-user-protocol.md` 끝 줄(`PendingResume.intent` 1필드, 답 뒤 재개가 조회로 이어짐) · `FIX-035.md`(identity 거절 → new_person 후속 — `loop_resume.output` 의 `identity_rejected`·`followup_question_id` 는 그 경로만의 키) · `verification.md` · `security.md` · 메인 세션 위임문(③~⑥ 공용 헬퍼 분리 + U4 23건 무수정, `resolutions` 모양, `trace_ids=[loop_resume, loop_query]`, 하위 호환, R-U4-2 4건, 사용자 수용 판단 ① 재개 후보 답 카드 `PersonNotFound` → `no_record`).
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`): `20261102-1334-verifier-u5-tests.txt`(U4+U5 파일 -v) · `20261102-1334-verifier-u5-regression9.txt`(회귀 9파일) · `20261102-1334-verifier-u5-full-regression.txt`(전체 `-q -rs`) · `20261102-1336-verifier-u5-lint.txt`(ruff) · `20261102-1336-verifier-u5-tools-check.txt`(7/7) · `20261102-1336-verifier-u5-scope.txt`(범위 diff·`-` 줄 전수·hunk·`resume_turn` 본문 대조·`answerer_from_env`/`from app.api` 출현·순환 import 3순서·확신도 grep 기준 대조·수집 ↔ tests.md·registry·03-log·구현 증거 목록·`git status`) · `20261102-1337-verifier-u5-grep-constraints.txt`(구현 제약 (1)~(5)·금지 호출·키 패턴·R-4 집계·docstring grep) · `20261102-1344-verifier-u5-contract-values.txt`(1회차, 내 스크립트 오류 3) · `20261102-1345-verifier-u5-contract-values.txt`(2회차, 95 PASS / 0 FAIL) · `20261102-1344-verifier-u5-mutation.txt`(변이 22). 스크립트는 스크래치패드 `verifier-p5b-u5/`(`contract.py`·`mutate.py`)·`u5/`(`compare_tail.py`·`compare_resume.py`·`scope.sh`·`constraints.sh`). `.env` 는 읽지도 복사하지도 않았다(변이 사본 최상위 = `alembic`·`alembic.ini`·`app`·`pyproject.toml`·`tests`, 증거 7행).

---

## 1. 본 것 — 01-plan 111~114행·결정 C·F·G·I·K·D16·S3.4·FIX-035·위임문 계약 대조

| 계약(01-plan·결정·위임문 글자 그대로) | 코드 위치(`app/agent/loop.py`, 작업 트리 행) | 직접 확인(contract-values 2회차) | 테스트 | 판정 |
|---|---|---|---|---|
| `resume_turn()` 에 `answerer: QueryAnswerer \| None = None` 키워드. `_log_resume_entry` 직후 `kind == "identity"` 이고 `resume_raw.get("intent", "record") == "query"` 면 `_resume_query_turn(...)` 으로 가고 끝낸다(기존 identity 기록 재개 코드는 그 아래 그대로) | 1705행 키워드 · 1793~1802행 분기(`INTENT_RECORD`/`INTENT_QUERY` 상수, 기본값 `INTENT_RECORD`) | scope (D4): `18219ba` 의 `resume_turn` 본문 vs 현재 — `-` 0줄, `+` 12줄 = 시그니처 1 + 분기 블록 11. 분기 위치는 `_log_resume_entry(ctx, resume_input)` / `resume_trace_id = ctx.last_trace_id` 바로 아래, `pending_calls` 조립 위 | (t)(u)(v)(w) | 일치. P1·P3·V12 검출 |
| 답이 `candidate_ids` 안 → 그 `person_id` 로 U4 ③~⑥ 을 같은 함수로 재사용(질문 = `context["utterance"]` — ER 이 넣은 원 발화, `PendingResume` 에 새로 담지 않는다) | `_resume_query_turn` 1637~1694행: `utterance = context.get("utterance", "")`, `if answer in candidate_ids:` → `_read_card(ctx, chosen)` → `_query_finish(...)` | (i)[A]/(i)[B] `answerer.questions == [원 발화]`, `evidence.person.display_name == 고른 인물`, 다른 인물 이름 없음 · (vii) 저장 `context.resume` 키 == `{version, mention, hints, pending_calls, held_drafts, dropped, intent}`(발화 중복 없음), `version "1"` · (vii-b) `context["utterance"]` 를 바꾼 사본으로 직접 재개하면 그 값이 question(출처 확인) | (t) `seen[0]` 에 고른 이름만 | 일치. V8 검출 |
| 답이 후보 밖(ER 거절 옵션) → FIX-035 의 new_person 후속 질문을 내지 않고 `no_record_reply([mention])`(③-2 와 같은 취급) | 1680~1681행 `else: unrecorded.append(mention)` → `_query_finish(card=None, …)` | (ii) 옵션 `['김민수','김민호','아니요, 다른 사람이에요']` 의 거절 답 → 7개 테이블 불변(`pending_questions` +0) · `_followup_new_person_turn`·`ask_user`·`apply_resolution`·`resolve`·`update_person` 호출 0 · `reply == '"팀장"에 대한 기록이 없어요.'` · answerer 0 · `answer_source no_record`·`person_id None`·`evidence_counts` 전부 0·MORE 없음 · `loop_resume.output` 키 == `['answer','context','kind']`(`identity_rejected`·`followup_question_id` 없음) · (ii-대조) 같은 DB 에서 기록 턴 identity 거절은 그 두 키 + new_person 후속 질문을 남긴다 → 키 어휘는 FIX-035 전용임을 확인 · (ii-직접) 저장 옵션 밖 임의 답을 `ResumeInput` 으로 직접 넣어도 거절과 같은 취급 | (u) | 일치. P2·V13·V14 검출 |
| 별칭은 누적하지 않는다(결정 G (a) 확정 — 저장 0, `update_person` 호출 없음). D16 "코드에서 지켜야 할 것" 4 | 1637~1694행에 `app_tools.` 호출 0(grep-constraints (6) 추가 99줄에 `app_tools.`·`update_person`·`apply_resolution(`·`resolve(`·`resolve_mentions(`·`_record(`·`after_record(`·`_followup_new_person_turn(` 0) | (i)[A]/(i)[B] 7개 테이블 불변(`person_aliases` 2 → 2) · 재개 뒤 기록 툴 `tool_call` 0 · 재개 뒤 `tool_call` 행 전체 0(`ask_user` 포함) · 금지 호출 스파이 7종 전부 0 | (t) `_write_tool_rows == 0`·`calls == {0,0,0,0}` | 일치. V1 검출 |
| trace 행: `loop_resume`·`loop_query`·`loop_turn`(`loop_resolve_done`/`loop_record` 없음). 위임문 `trace_ids = [loop_resume, loop_query]` 행 id | `_resume_query_turn` 이 `trace_ids=[resume_trace_id]` 를 넘기고 `_query_finish` 가 `query_trace_id` 를 뒤에 붙인다(1440행) | (i)(ii) 재개 뒤 `loop_resume 1 · loop_query 1 · loop_turn 1`, `loop_resolve_done`/`loop_record`/`er_resolve`/`loop_extract`/`loop_gate`/`loop_error` 0 · `result.trace_ids == [loop_resume.id, loop_query.id]`(예 `[417470, 417471]`) · `loop_query.tool_name == "agent"` · `loop_turn.output.reply == loop_query.output.reply == result.reply` | (t)(u) | 일치. V2·V18·V15 검출 |
| 위임문 `loop_query.resolutions` = `[{mention, band:"identity", person_id, er_trace_id:None, applied, question_id:<재개한 질문 id>}]`(후보 답 `person_id`=후보·`applied=True`, 거절 `None`·`False`), `mentions=[mention]`, `mentions_dropped=0`, `stop_reason=None`, `stored` 0, `loop_turn` 1행 | 1663~1675행 `entry` · 1685~1693행 `mentions=[mention]`, `dropped=0`, `pending_question=None` | (i)[A] `[{"band":"identity","applied":true,"mention":"팀장","person_id":47898,"er_trace_id":null,"question_id":11128}]` 정확히 · (ii) `[{…,"person_id":null,"applied":false,"question_id":11133}]` 정확히 · `output` 키 집합 == 10개 정확히 · `intent query`·`mentions ["팀장"]`·`mentions_dropped 0` · `stop_reason None`·`pending_question None`·`stored {0,0,0}` | (t)(u) 전체 값 단언 | 일치. V3·V6·V9·V10·V11·V5 검출 |
| 하위 호환(위임문): `intent` 키 없음 → 기록 경로; `new_person`·`schedule` kind 는 `intent` 무시 | 1793행 `resume_raw.get("intent", INTENT_RECORD)` + `kind == "identity"` 조건 | (iii) 기록 턴(P5-loop 경로, `add_event(person="팀장")`+판정 실패)이 만든 identity 행의 `context.resume` 키 == `['dropped','held_drafts','hints','mention','pending_calls','version']`(intent 없음) → 재개: `_resume_query_turn` 스파이 0 · `update_person` `tool_call` 1 · `person_aliases` 1 → 2 · `events` 0 → 1 · `stored.events 1` · `loop_query 0`·`loop_record 1`·`loop_resolve_done 1` · (iii-b) `intent="record"` 명시해도 기록 경로 · (iv) `new_person`·`schedule` 에 `resume.intent="query"` 사본 → `_resume_query_turn` 0·`loop_query 0`·`loop_record 1`·`loop_resolve_done 1` | (v)(w) | 일치. P3·V12 검출 |
| 사용자 수용 판단 ① — 재개 후보 답의 카드 `PersonNotFound` → `no_record` 취급(U4 ⑤ 와 동일) | 1670~1676행 `card = _read_card(ctx, chosen)` / `if card is None: unrecorded.append(mention)` (`_read_card` 1251~1261행이 `PersonNotFound` → `None`) | (v-e) `get_person_card` 가 `PersonNotFound` → `reply == no_record_reply(["팀장"])`·answerer 0·`person_id None`·`answer_source no_record`·`resolutions[0] == {…person_id: 후보 id, applied: true…}`·저장 0·예외 없음 · (v-f) 다른 user 소유 후보 id 를 context 에 넣어도 카드 None → no_record·answerer 0 | 없음 — (y) 는 merge 경로만 | 일치. V7 생존(§3, R-U5-1) · V7b 는 (y) 가 검출 |
| 결정 K (a)+R-1 — `answerer is None` 이면 근거 있을 때만 `_respond.answerer_from_env()` 모듈 속성 호출(재개도 같은 꼬리) | `_query_finish` 1403행 1곳(scope (E) `grep -c` 1) · `resume_turn` 이 `answerer=answerer` 를 그대로 넘김(1800행) | — | (t) 주입 answerer 로 llm 답 | 일치. V17 검출(None 으로 바꾸면 (t) FAIL) |
| 결정 L (a) — `from app.api` 는 `_read_card` 안 지연 import 1곳, 순환 import 없음 | 1256행 1곳, 1~260행 0 | scope (G) `agent-first ok`·`api-first ok`·`loop-only ok` | — | 일치 |
| 결정 E — 재개 경로의 폴백도 같은 꼬리: `JudgeUnavailable` 만 템플릿, `SQLAlchemyError` 는 삼키지 않음, 검증 실패는 템플릿 + `rejected_answer` 원문 | `_query_finish` 1395~1413행(U4 와 동일 문장) | (xv) `FakeQueryAnswerer(fail="timeout")` → 템플릿·`answerer_error:timeout`·예외 없음·`loop_error 0` · (xvi) 금지 표현 앞뒤 공백 → `template`·`forbidden_expression`·`rejected_answer == '  요즘 많이 힘들어 보여요  \n'` 원문 · (i-t) 빈 답 → 템플릿·`empty`·`rejected ''`, 템플릿 reply 에 MORE 1회 · (v-h) 답 생성기 `SQLAlchemyError` → `resume_turn` 밖 전파 · (v-i) `get_person_card` `SQLAlchemyError` → `resume_turn` 밖 전파 | (aa) 는 `run_turn` 만 | 일치. V19 검출 |
| R-U4-2 닫기 4건(위임문 x·y·z·aa) | — | (v-a) 앞뒤 공백 유효 답 → 본문 strip + MORE·`rejected None`·`llm` · (v-b) 금지 표현 앞뒤 공백 → `rejected_answer` 원문 · (v-c) merge 턴 `resolutions[0].person_id == person.id`·`band merge` · (v-d) merge 카드 `PersonNotFound` → no_record·answerer 0·`resolutions[0].person_id == merge id` · (v-g) 답 생성기 `SQLAlchemyError` → `run_turn` 밖 전파 | (x)(y)(z)(aa) | 일치. 생존이던 U4 V10·V11·V12·V13·V20 에 해당하는 내 변이 V7b(= U4 V12)·V16 이 이제 검출 |
| 원칙9 — 재개 턴도 trace 에 해석(resolutions)·조회 입력(person_id·근거 건수)·답·토큰 | `_QueryTrace` 그대로 | (i) `evidence_counts == {facts 3, patterns 0, timeline 5, schedules 2}` · `tokens_in/out == (7,3)`(`QueryAnswer.trace_tokens()` 그대로) · 원문(`raw_utterance`) 이 reply·`loop_query`·`loop_turn` 에 0 | (k) 스키마(U4) | 일치 |
| 원칙1·2·4 — 루프는 band 만 본다, 확신도 어휘 없음 | 추가 99줄에 `confidence`/`T_merge`/`T_new`/`threshold`/`breakdown`/`s_llm`/`s_emb`/`s_rule` 0 · `loop.py` 전체 기준 `8a8767b` 0 == 현재 0 | — | — | 일치 |
| (vi) 두 번째 답 제출 409 는 라우트 몫(U6) | — | (vi) `answer_question` 재호출 → `QuestionNotAnswerable("already_answered")`(기존 동작) · (i) 재개 뒤 질문 행은 `answer == pick`·`answered_at not null` 그대로(재개가 행을 건드리지 않음) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_agent_query_loop.py -v` | 33 passed in 0.92s, exit 0 — U5 10건(t×2·u·v·w×2·x·y·z·aa) PASSED | `…-1334-verifier-u5-tests.txt` |
| `… pytest tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_propose.py tests/test_agent_types.py tests/test_agent_query_types.py tests/test_agent_query_gate.py tests/test_agent_query_answer.py -q` | 283 passed, exit 0 | `…-1334-verifier-u5-regression9.txt` |
| `… pytest tests/ -q -rs` | 2114 passed, 1 warning in 25.77s — skip 0줄. 기준 2104 + 10 | `…-1334-verifier-u5-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-1336-verifier-u5-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-1336-verifier-u5-tools-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` | 빈 출력 — 기존 테스트 파일 수정 0 | `…-1336-verifier-u5-scope.txt` (A) |
| `git diff 18219ba -- tests/test_agent_query_loop.py \| grep "^-[^-]"` / `--numstat` | `-` 줄 0 / `322 0` — U4 테스트 23건 무수정(상단 import 7줄 + U5 블록 추가만) | (A2) |
| `git diff --stat HEAD -- app/api app/er app/tools app/briefing app/memory app/db app/main.py app/agent/respond.py app/agent/gate.py app/agent/propose.py app/agent/types.py app/agent/__init__.py app/settings.py alembic web scripts` | 빈 출력 | (B) |
| `git diff --numstat HEAD -- app` | `108 1 app/agent/loop.py` 1파일 | (C) |
| `git diff HEAD -- app/agent/loop.py` 의 `-` 줄 전수 | 1줄 — `    dropped = len(mentions) - resolved`(`_query_finish` 호출 인자 `dropped=len(mentions) - resolved` 로 이동). hunk 5개: import(`INTENT_RECORD` +1)·`_run_query_turn` 꼬리 → `_query_finish` 호출 + 새 함수 머리·`_resume_query_turn` 새 함수·`resume_turn` 시그니처 +1·`resume_turn` 분기 +11 | (D)(D2) |
| `18219ba` 의 `resume_turn` 본문 vs 현재(`compare_resume.py`, AST 함수 범위) | `-` 0 · `+` 12(시그니처 1 + 분기 11) — 기존 identity/new_person/schedule 본문 무변경 | (D4) |
| 공용 헬퍼 분리 동일성(`compare_tail.py`, AST 함수 범위) | `18219ba` `_run_query_turn`(1273~1411행) 의 `dropped = …` 부터 끝(72줄) vs 현재 `_query_finish`(1357~1446행) docstring 뒤 본문(72줄): unified diff 는 `-    dropped = len(mentions) - resolved` / `+` 빈 줄 1쌍뿐 — 이동한 1줄을 빼면 빈 줄 1개 차이, 빈 줄·주석 제외 정규화 후 IDENTICAL. `_run_query_turn` 머리(`dropped = …` 앞 67줄) vs 현재 머리(`return _query_finish(` 앞): IDENTICAL. 힌트 순서·`source` 조건·`_QueryTrace` 10필드·`TurnResult` 필드·`_log_turn` 전부 같은 문장 | §3 V4·V5·V15·V16·V19 가 U4 테스트로 검출됨이 방증 |
| `grep -n "answerer_from_env" app/agent/loop.py` / `grep -n "from app.api\|import app.api"` / 1~260행 `app.api` | `1403: answerer = _respond.answerer_from_env()` 1곳 / `1256: from app.api.read import get_person_card` 1곳 / 0 | (E)(F)(F2) |
| 순환 import 3순서 | `agent-first ok`·`api-first ok`·`loop-only ok` | (G) |
| 확신도·임계치 grep 기준 대조(`loop.py` 전체) | `8a8767b` 0 == 현재 0 | (H) |
| `pytest --collect-only -q` ↔ `tests.md` U5 절 | 수집 33(함수 31, 파라미터 포함) 중 U5 함수 8·파라미터 포함 10 / `tests.md` U5 절 8행, 이름 `diff` → `SAME` | (I) |
| registry·03-log·구현 증거 목록·`git status` | `loop.py` 행 비고 "P5b U5(해시 pending)" 1곳 + 테스트 행 "33건(U4 23 + U5 10 …)" / 03-log 는 U4 항목 끝에 "커밋 뒤(2026-11-02): `18219ba`, dev2 푸시" 1줄 추가, U5 항목 없음 / 구현 증거 u5 9개 / status 는 제품 1 + 테스트 1 + 문서 5 + 증거 | (J)(K)(L)(M) |
| 구현 제약 (1)~(5) — `git diff HEAD -- app` 추가 줄 99 대상 | (1) `create_person\(\|update_person\(` 0 / (2) 확신도 영어 어휘 0 / (3) `sleep`·`while True` 0 / (4) `PendingQuestion`(Out 제외) 0·`flag_modified`·`.context =` 0 / (5) 키 패턴 0 / (6) 금지 호출 `resolve_mentions(`·`_record(`·`_record_impl(`·`after_record(`·`_followup_new_person_turn(`·`apply_resolution(`·`resolve(`·`app_tools.`·기록 툴 4종·`ask_user` 0 / (7) `os.environ`·`getenv` 0 / R-4 집계: `create_person\(` app/agent 1 = 기준 1, `update_person\(` 5 = 기준 5, `PendingQuestion\|flag_modified\|.context =` loop.py 13 = HEAD 12 + `PendingQuestionOut` 타입 1(`_query_finish` 시그니처) / 신규 테스트 269줄: 키 패턴 0, 실 공급자·네트워크 import 0 / (10) `resume_turn` docstring 에 `INTENT_QUERY`·`_resume_query_turn`·"조회 턴"·"조회 재개"·"P5b"·"U5" 0(R-U5-2) | `…-1337-verifier-u5-grep-constraints.txt` |
| 계약 값 Python 95 항목(§1 의 (i)~(vii) + 템플릿·폴백·격리·원문 비노출) | 95 PASS / 0 FAIL, exit 0(2회차). 1회차(`…-1344-…`) 는 37 PASS / 3 FAIL — 전부 내 스크립트 오류(`PersonCardOut.display_name` → `.person.display_name` 2건, 합성 new_person 행을 D1 게이트 `ConfirmationRequired('not_affirmative')` 가 거부한 추가 케이스 1건 — 기존 경로의 정상 동작이라 뺐다) | `…-1345-verifier-u5-contract-values.txt` |
| 저장소 무수정 | 변이 뒤 `git status --short` = 리뷰 전과 같음(제품 1·테스트 1·문서 5·증거), 사본 `loop.py` ↔ 저장소 `SAME`, 사본에 비밀 파일 없음 True | `…-1344-verifier-u5-mutation.txt` 끝 |

## 3. 변이 시험 — 내가 직접 (`20261102-1344-verifier-u5-mutation.txt`)

사본 `verifier-p5b-u5/repo`(최상위 `alembic`·`alembic.ini`·`app`·`pyproject.toml`·`tests` — `.env` 없음) 에서 `loop.py` 만 바꿔 `tests/test_agent_query_loop.py`(33) 를 돌렸다. 대조군 C0 33 passed. 22건 적용 / 검출 21 / 생존 1 / 동등(패턴 불일치) 0.

| id | 변이 | 결과 | 잡은 테스트 |
|---|---|---|---|
| P1 | 계획1 `resume_raw.get("intent")` 분기 제거(`if False:`) | 검출 3 | (t)×2 별칭 누적·`update_person` 1 · (u) |
| P2 | 계획2 거절 답에 FIX-035 `_followup_new_person_turn` 후속 질문 | 검출 1 | (u) `followup == []`·행 수 |
| P3 | 계획3 기본값을 `INTENT_QUERY` 로 | 검출 1 | (v) 하위 호환 |
| V1 | 재개 후보 답에서 `app_tools.update_person(ctx, chosen, new_alias=mention)`(결정 G (b) 로 되돌림) | 검출 2 | (t)×2 |
| V2 | `trace_ids=[]`(loop_resume 누락) | 검출 3 | (t)×2 (u) |
| V3 | `resolutions[].question_id` None | 검출 3 | (t)×2 (u) |
| V4 | `_query_finish` 힌트 순서 뒤집기(MORE 먼저) | 검출 2 | U4 (h)(o) — 공용 꼬리를 U4 테스트가 지킨다 |
| V5 | `_query_finish` `stop_reason="ask_user"` 항상 | 검출 4 | U4 (q) + (t)×2 (u) |
| V6 | `_resume_query_turn` `dropped=1` | 검출 3 | (t)×2 (u) |
| V7 | 재개 후보 답 카드 None 처리 제거(`person_id = chosen` 무조건) | 생존 | 없음 — R-U5-1 |
| V7b | `_read_card` 가 `PersonNotFound` 를 흡수하지 않음(= U4 V12) | 검출 1 | (y) — U4 생존 변이가 닫힘 |
| V8 | 재개 question 을 `mention` 으로 | 검출 2 | (t)×2 |
| V9 | 재개 `entry.applied` 를 올리지 않음 | 검출 2 | (t)×2 |
| V10 | 재개 `entry.person_id` None | 검출 2 | (t)×2 |
| V11 | 재개 `entry.band` "merge" | 검출 3 | (t)×2 (u) |
| V12 | `kind == "identity"` 조건 제거 | 검출 2 | (w)×2 |
| V13 | 답이 후보 밖이어도 첫 후보로 답 | 검출 1 | (u) |
| V14 | 거절 답을 `unrecorded` 에 넣지 않음 | 검출 1 | (u) |
| V15 | `_query_finish` 가 `_log_turn` 생략 | 검출 3 | U4 (a) + (t)×2 |
| V16 | MORE 힌트를 llm 외에도(`source != _SRC_ASK`) | 검출 12 | U4 (b)(d)(e)(f)(i)(n)(p)(r)·격리 + (u)(x)(y) — U4 생존 V10/V11 류가 (x) 로 닫힘 |
| V17 | `resume_turn` 이 `answerer=None` 을 넘김(지연 해소) | 검출 2 | (t)×2 |
| V18 | `trace_ids=[None]` | 검출 3 | (t)×2 (u) |
| V19 | 근거 0건 판정 제거 | 검출 2 | U4 (f)(r) |

판정: 01-plan 114행 변이 표 3건은 적힌 테스트가 그대로 잡는다(P1 → 조회 재개 테스트 (t) 가 별칭 누적으로 FAIL, P2 → (u) 새 질문 0 단언, P3 → (v)). 공용 꼬리 `_query_finish` 에 넣은 변이(V4·V5·V15·V16·V19) 를 U4 테스트가 전부 잡으므로 "U4 테스트 23건 무수정 통과" 가 분리 동일성의 살아 있는 증거다. 생존 V7 은 §6 R-U5-1.

## 4. 계획 불일치·메모 판정

### 4a. 사용자가 수용한 구현자 판단 ① — 코드와 일치
재개 후보 답의 카드 `PersonNotFound` → `no_record` 취급: `_resume_query_turn` 1670~1676행이 `_read_card`(U4 ⑤ 와 같은 함수) 의 `None` 을 `unrecorded` 로 넘긴다. (v-e) 로 직접 확인(위 §1). `resolutions[0].person_id` 는 후보 id 로 남고(사용자가 고른 사실), `output.person_id` 는 None(답한 인물 없음) — U4 merge 경로 (v-d) 와 같은 비대칭이고 결정 C 의 두 필드 정의("해석 결과" vs "답한 인물")와 맞는다.

### 4b. 계획에 없는 것이 들어갔는가
`git diff HEAD -- app` 추가 99줄은 import 1·`_query_finish` 호출 13·`_query_finish` 머리(시그니처·docstring) 21·`_resume_query_turn` 58·`resume_turn` 시그니처 1·분기 11 뿐. 새 상수·새 툴·새 trace step·`app/api`·`web` 변경 0. `_query_finish` 는 위임문이 지시한 "③~⑥ 공용 헬퍼 분리" 이고 01-plan 113행 "U4 ③~⑥ 을 같은 함수로 재사용" 과 같은 뜻이다. `INTENT_RECORD` import 는 기본값 상수화(01-plan 은 문자열 `"record"` 로 적음 — 같은 값, `app/agent/types.py` 의 어휘를 쓰는 쪽이 맞다).

### 4c. `resume_turn` docstring(메모 → R-U5-2)
1707~1780행 docstring 의 "답 종류별 동작 — identity: `context["candidate_ids"][answer]` 가 가리키는 그 인물에만 `update_person` 을 … 부른다" 와 "`agent_traces` … 단 identity 거절 → 후속 질문 경로(FIX-035)는 두 행을 남기지 않고" 는 U5 뒤 조회 재개(`resume.intent == "query"` — `update_person` 0, `loop_resolve_done`/`loop_record` 0) 를 설명하지 않는다. 분기 자리의 한 줄 주석("P5b U5 -- 조회 턴이 낸 identity 질문의 답: 별칭 누적 없이 카드로 답한다") 과 `_resume_query_turn` docstring 은 정확하다. 동작 결함 아님.

## 5. `tests.md`·`registry.md`·테스트가 실패 조건을 검사하는가

- `tests.md` U5 절 8행 ↔ `--collect-only` U5 함수 8(파라미터 포함 10) 이름 `SAME`. 표의 "결과 · 검출 변이" 열은 구현자 번호(U5-M*)라 내 판정 근거로 쓰지 않았다.
- `registry.md`: `loop.py` 행 비고의 "`_run_query_turn` 의 ③~⑥ 을 공용 `_query_finish` 로 떼어냈다(동작·trace 비트 단위 동일)"·`resolutions[0]` 모양·trace 행 3종·"기존 재개 코드 무변경" 은 §2 분리 동일성·(D4)·§1 과 일치. 테스트 행 33건(U4 23 + U5 10) 일치. 해시 pending 2곳(메인 세션이 커밋 뒤).
- 테스트는 실패 조건을 검사한다: §3 의 P1~P3·V1~V3·V6·V8~V14·V17·V18 이 (t)(u)(v)(w) 로만 잡힌다(U4 테스트로는 안 잡힘). (t) 는 실제 조회 턴이 저장한 질문 행 → `answer_question` → `load_resume_input` → `resume_turn` 경로를 타고, 7개 테이블·금지 호출 4종 스파이·`resolutions` 전체 값·`trace_ids` 행 id 를 본다. (y) 는 `app.api.read.get_person_card` 를 바꿔 끼워 실제 `PersonNotFound` 경로를 탄다(V7b 검출). (aa) 는 `pytest.raises(SQLAlchemyError)` 두 경로.
- 테스트 파일 메모(소견 아님): 추가 import 7줄이 기존 `from app.tools.context import ToolContext` 뒤에 `from sqlalchemy.exc …` / `from app.agent.loop import resume_turn`(기존 `from app.agent.loop import run_turn` 과 분리) 순으로 붙어 isort 관례와 다르다. `pyproject.toml` ruff `select = ["F","B","DTZ"]` 에 I 규칙이 없어 lint 는 통과한다. U6 에서 파일을 다시 열 때 한 줄로 합쳐도 되는 정도.

## 6. 범위·원칙

- 원칙7(제외 범위): 재개 턴 답도 카드 사실 재진술(LLM 답 또는 템플릿)·"기록이 없어요" 뿐. 거절 답에 "새로 기억할까요" 를 묻지 않는다(D16 결정 3, (ii)).
- 원칙1·2·4: 재개 분기는 ER 을 다시 돌리지 않고(`resolve` 0, `er_resolve` 0) 사용자가 고른 `candidate_ids[answer]` 만 쓴다 — 오병합 위험 0(사용자 확인). 확신도 어휘 0.
- 원칙9: §1 trace 행·`resolutions`·근거 건수·토큰.
- D16 "코드에서 지켜야 할 것" 3(`apply_resolution` 재사용은 identity 되묻기 때 U4 가, 재개는 저장 0 이라 호출 없음 — 결정 G (a))·4(기록 툴 `tool_call` 0, 7개 테이블 불변)·5(`pending_questions` +0, (ii)) 성립. `web/` diff 0.
- security §1: 추가 줄·신규 테스트에 키 패턴 0, `os.environ` 0, trace·reply 에 원문(`raw_utterance`) 0((i)). `.env` 미독·미복사(내 변이 사본 최상위 5항목). 증거는 전부 `save_evidence.py`(비밀 검사 통과). 저장소 무수정. 단 구현자 변이 러너의 사본에는 `.env` 가 있다 — R-U5-3.
- 계획 범위(01-plan U5 줄) 안. "하지 않는 것"(`PendingResume` 에 발화 추가·별칭 누적·FIX-035 후속·새 trace step) 전부 안 했다.

## 7. 소견

- [권고] R-U5-1 — 생존 변이 V7(재개 후보 답 카드 `PersonNotFound` 처리 제거 → `person_id` 가 후보 id 로 남고 `no_record_reply([])` 빈 목록 답). 사용자 수용 판단 ① 의 경로를 지키는 테스트가 없다((y) 는 merge 경로만). 코드는 맞고 내 (v-e)·(v-f) 가 덮는다. U6 에서 `tests/test_agent_query_loop.py` 또는 `tests/test_api_chat_query.py` 에 재개 경로 `PersonNotFound` 1건(`reply == no_record_reply(["팀장"])`·`person_id None`·answerer 0) 추가 권고.
- [권고] R-U5-2 — `resume_turn` docstring(1707~1780행) 이 조회 재개 분기를 설명하지 않는다(§4c). 동작 결함 아님. U6 문서 단위에서 identity 절에 "조회 턴이 낸 질문(`resume.intent == "query"`)은 `_resume_query_turn` — 별칭 누적 0, `loop_query`" 한 줄, trace 절의 예외 목록에 조회 재개 추가 권고. 코드 수정이 필요하므로 메인 세션이 아니라 구현 에이전트 몫.
- [권고] R-U5-3 — 구현자 변이 러너 사본 `scratchpad/p5b-u5/repo` 최상위에 `.env` 가 있다(이름만 확인, 내용 미독). journal 2026-11-02 DECISION 줄에 "변이 러너가 스크래치패드에 복사한 `.env` 사본 삭제는 훅이 막아 사용자에게 명령 전달" 로 이미 기록됨. 커밋 전 사용자가 삭제했는지 확인 권고. 이 패키지의 변이 러너 관례(U4·U5 verifier: `app`·`tests`·`alembic`·`pyproject.toml`·`alembic.ini` 만 복사)를 구현자 위임문에 명시하면 재발을 막는다.
- 03-log 에 적을 내용(메인 세션): U5 항목 — 변경(`resume_turn(..., answerer=None)`·분기 1곳·`_resume_query_turn`·`_query_finish` 분리, `loop.py` +108/−1, 테스트 +10 = 33, U4 23건 무수정) · 이유(01-plan U5 줄·결정 G (a)·D16 결정 3·S3.4 끝 줄) · 계획과 다른 점(사용자 수용 판단 ① 재개 카드 `PersonNotFound` → `no_record`; `INTENT_RECORD` 상수 기본값) · 검증(구현 증거 9 + verifier: 33·283·2114 skip 0·ruff·7/7·분리 동일성 IDENTICAL·`resume_turn` `-` 0·계약 값 95/0·변이 22 적용/21 검출/1 생존) · 소견 R-U5-1~3 · 남은 것 U6(API 끝에서 끝 + 회귀 판정 + 문서, R-U5-1·R-U5-2 포함) · registry 해시 pending 2곳.

## 8. 판정

결과: 통과 — [필수] 0. 커밋 가능. [권고] R-U5-1(테스트 공백 1, U6)·R-U5-2(docstring, U6)·R-U5-3(스크래치패드 `.env` 사본 삭제 확인, 사용자) 는 이 커밋을 막지 않는다.
