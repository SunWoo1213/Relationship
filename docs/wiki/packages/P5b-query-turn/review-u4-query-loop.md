# P5b-query-turn U4 루프 조회 분기 (`run_turn` `answerer=None` + `_run_query_turn`, 저장 0) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 4(R-U4-1 01-plan 110행 변이 표 3·5번 문구가 실제 검출 경로와 다름(수정안 §4a·§4b), R-U4-2 생존 변이 5건 = 테스트 공백(③ strip/원문·⑤ `PersonNotFound` 흡수·`resolutions[].person_id`·E-4 예외 범위 — 코드는 맞고 내 계약 값 확인이 덮는다, U5/U6 에서 테스트 추가 권고), R-U4-3 `loop_query.input` 에 `record` 전체가 output 과 같은 내용으로 중복 실림(`loop_turn` 관례와 같아 위반 아님, P10 메모), R-U4-4 03-log U4 항목·registry 해시 pending 2곳(메인 세션)). 코드 결함은 찾지 못했다. 계약 값 직접 확인 99 PASS / 0 FAIL(3회차; 1·2회차는 내 스크립트 오류), 변이 31건 적용(계획 표 5건을 7개 변이로 재현 + 내 변이 24) 중 검출 26·생존 5·동등 0, U4 파일 23 passed, 회귀 9파일 283 passed, 전체 2104 passed(2081 + 23)·skip 0, ruff 통과, `tools_check` 7/7, 범위 밖 diff 0, 기존 테스트 파일 수정 0, `loop.py` 의 `-` 줄은 import 3줄뿐(기존 함수 본문 무변경).
대상: 작업 트리(HEAD `a002706` = U3, 무변경 기준 `8a8767b`) — `git diff HEAD -- app`(`--numstat` `app/agent/loop.py 276 3`, 1파일) · 신규 `tests/test_agent_query_loop.py`(923줄, 수집 23 = 함수 23, parametrize 0) · `docs/wiki/registry.md` 비고 1곳(`loop.py` 행 "P5b U4(해시 pending)") + 새 행 1(`tests/test_agent_query_loop.py`) · `docs/wiki/packages/P5b-query-turn/tests.md` U4 절(23행) · 구현 증거 `evidence/20261102-1231-u4-{diff-filter,loop,pytest-all,regression,ruff,scope,tools-check}.txt`·`20261102-1232-u4-grep-k.txt`(`--append` 2회)·`20261102-1233-u4-mutation.txt`(9). `HANDOFF.md`·`journal.md`·`03-log.md` 의 문서 diff 는 위임대로 리뷰 대상 아님(03-log 에 U4 항목이 아직 없다는 사실만 §7 에 적는다).
근거 문서: `01-plan.md` 105~110행(U4 계약·"부르지 않는 것"·테스트 (a)~(k)·변이 표 5건) · 86~87행(구현 제약 (1)~(5)) · 결정 B-3 (b)(언급 출처: `search_person` 은 `query`, 그 밖은 `person`, strip·빈 값 제외·첫 등장 순 중복 제거) · 결정 C(196~216행 — `loop_query` 1종·output 10키·`resolutions[]` 6키·답한 턴 `stop_reason=None`·`loop_resolve_done`/`loop_record` 없음) · 결정 D(근거 건수 — 타임라인은 상한 뒤) · 결정 E-4/E-5(폴백 — `JudgeUnavailable` 만 템플릿, `SQLAlchemyError` 는 삼키지 않음; 문구 5종) · 결정 F ①~⑤(`QUERY_MORE_HINT` 는 `answer_source=="llm"` 뿐, 순서 본문 → 한 사람씩 → 더보기) · 결정 G(`PendingResume` `intent` 1필드, version "1") · 결정 I (a)(merge·new_person 은 `resolve()` 만, identity 만 `apply_resolution()`) · 결정 J(`LOOP_MAX_MENTIONS` 재사용, 인물 1, merge 뒤 남은 언급 해석 안 함 + 안내 한 줄) · 결정 K (a)+R-1(`_respond.answerer_from_env()` 모듈 속성 호출 1곳, 근거 0건이면 해소 안 함) · 결정 L (a)(함수 안 지연 import) · 판정 표 150~168행 D-3·D-4·D-5·R-1·R-2·R-4·R-5·R-7 · `docs/wiki/decisions/D16-query-turn.md` 결정 1~10·"코드에서 지켜야 할 것" 3·4·5·갱신 이력 보정 ①② · `CLAUDE.md` 원칙1·2·4(루프는 `band` 만 본다)·원칙7·원칙9 · `docs/wiki/specs/S3.4-ask-user-protocol.md` 끝 줄 · `docs/wiki/verification.md` 변이 규칙 · `docs/wiki/security.md` §1 · 사용자가 수용한 구현자 판단 7건(2026-11-02 — ① `_QueryTrace` frozen dataclass ② 카드 안 읽은 턴의 `evidence_counts` 전부 0 dict ③ LLM 본문 `strip()`·`rejected_answer` 원문 ④ `mentions_dropped = len(mentions) − resolve 호출 수` ⑤ merge 카드 `PersonNotFound` → "기록 없음" ⑥ identity `PendingQuestionOut` 인라인 조립 ⑦ `QUERY_MAX_PERSONS` 미import).
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`): `20261102-1258-verifier-u4-tests.txt`(U4 파일 -v) · `20261102-1258-verifier-u4-regression9.txt`(회귀 9파일) · `20261102-1258-verifier-u4-full-regression.txt`(전체 `-q -rs`) · `20261102-1259-verifier-u4-lint.txt`(ruff) · `20261102-1259-verifier-u4-tools-check.txt`(7/7) · `20261102-1259-verifier-u4-scope.txt`(범위 diff·`-` 줄 전수·hunk 위치·`answerer_from_env`/`from app.api` 출현·순환 import 3순서·확신도 grep 기준 대조·수집 ↔ tests.md·registry·03-log·`git status`) · `20261102-1259-verifier-u4-grep-constraints.txt`(구현 제약 (1)~(5)·금지 호출·키 패턴·R-4 집계) · `20261102-1305-verifier-u4-contract-values.txt`(계약 값 Python 직접 확인 — 3회 append: 1회차 exit 1 은 내 스크립트가 `tests/conftest.py` 를 import 해 FIX-006 DB 이름 충돌 가드에 걸림, 2회차 exit 1 은 내 시나리오 오류 8건(ER 은 후보가 있으면 new_person 을 내지 않는다는 사실·기록 턴 대조군의 `held_drafts`·identity 가 정당하게 `apply_resolution` 을 부르는 케이스에 스파이를 건 것), 3회차 exit 0 · 99 PASS 가 판정 근거) · `20261102-1306-verifier-u4-mutation.txt`(변이 31 + 대조군, `--append` 1회 = V1 재실행). 스크립트는 스크래치패드 `verifier-p5b-u4/{scope.sh,constraints.sh,contract.py,mutate.py}`, 변이 사본은 `verifier-p5b-u4/repo/`(저장소 무수정 — 끝에 `git status --short` 와 사본 ↔ 저장소 `SAME`).

---

## 1. 본 것 — 01-plan 105~110행·결정 B·C·D·E·F·G·I·J·K·L 계약 대조

| 계약(01-plan·결정 글자 그대로) | 코드 위치(`app/agent/loop.py`, 작업 트리 행) | 직접 확인(contract-values 3회차) | 테스트 | 판정 |
|---|---|---|---|---|
| `run_turn()` 에 `answerer: QueryAnswerer \| None = None` 키워드, 게이트 직후 `if proposal.intent == INTENT_QUERY: return _run_query_turn(...)` 1곳, 그 아래 기존 코드 무변경 | 1091행 키워드 · 1124~1134행 분기 | hunk `@@ -1058,0 +1091 @@`(1줄)·`@@ -1090,0 +1124,11 @@`(11줄) 만 — `run_turn` 본문의 `-` 줄 0. `-` 줄 전수 3개는 모두 import(`build_reply`·`settings`·`tools.types` 를 괄호 import 로 바꾸며 기존 이름 유지) | (j) `_run_query_turn` 스파이 0회 | 일치 |
| 결정 B-3 (b) 언급 출처 — 인덱스 순, `search_person` 은 `args["query"]`, 그 밖은 `args["person"]`, strip·빈 값 제외·첫 등장 순 중복 제거, "나" 를 코드로 거르지 않음 | `_query_mentions` 1233~1248행 | (iv) 공백뿐·비문자열(`12`) 언급 → `mentions == []` · (g) `search_person("팀장")`+`add_event(person="팀장")` → `["팀장"]` 1개 | (h3) `["가","나","다"]` · (h) `["박선우 과장님","나"]` | 일치. V7·V8·V23 검출 |
| 결정 J — `mentions[:LOOP_MAX_MENTIONS]`, merge 면 그 인물로 확정하고 남은 언급은 보지 않음(`break`), 상한·merge 뒤 남은 수 = `mentions_dropped`(수용 판단 ④) | 1297행 슬라이스 · 1310~1318행 merge `break` · 1340행 `dropped = len(mentions) - resolved` | (viii) 2개 merge 가능 → `resolve` 1회 `["팀장"]`·dropped 1·resolutions 1 · (ix) 6개(빈 DB) → `resolve` 정확히 앞 5·dropped 1·`er_resolve` 5행 · (ix) new_person·new_person·identity·4번째 → `resolve` 3회·dropped 1·resolutions band `[new_person,new_person,identity]` | (h)(o)(p)(h2) | 일치. V16·V22 검출 |
| 결정 I (a) — merge·new_person 은 `resolve()` 만(`apply_resolution` 0), identity 만 `apply_resolution()` | 1310~1324행 merge/new_person 경로에 `apply_resolution(` 없음 · 1326행 identity 만 | (i) `er_resolve.decision.applied == False`·`person_aliases` 불변·`update_person` tool_call 0 · (iii) `applied False`·`ask_user` 0 · (ii) `applied True`·`pending_question_id == 행 id` | (a)(b)(c)·스파이 | 일치. P1·P2·V1 검출 |
| 결정 G — identity 재개 재료 `PendingResume(mention, intent="query", pending_calls=[])`, `_extend_identity_payload` 와 같은 모양, version "1" | 1324~1325행 | (ii) `context["resume"] == {"version":"1","mention":"팀장","hints":{},"pending_calls":[],"held_drafts":[],"dropped":0,"intent":"query"}` 정확히 · 기존 identity 기록 턴(P5-loop 경로, 같은 DB·같은 judge) 의 resume 키 = 조회 키 − `{intent}`, `hints`/`held_drafts`/`dropped`/`version` 타입 동일, context 최상위 키 6개 `['affirmative_options','candidate_ids','confidence_breakdown','mention','resume','utterance']` 동일 · `options`·`question` == ER 원본 `ask_payload` | (c) | 일치. V17·V18 검출 |
| D16 "코드에서 지켜야 할 것" 5 — new_person 은 `pending_questions` 행 0, identity 는 1 | 1320~1322행 `continue` | (iii) 7개 테이블(`pending_questions` 포함) 불변 · (ii) `pending_questions` +1, 나머지 6개 불변 | (b)(c) | 일치. P2 검출 |
| 결정 L (a) — `_read_card` 안 지연 import, `PersonNotFound` → `None`(수용 판단 ⑤), 다른 사용자 소유 안 보임 | 1251~1260행 | `from app.api` 출현 1255행 1곳(최상단 1~260행 0), `import app.agent`→`app.api`→`app.main` / `app.api`→`app.agent` / `app.agent.loop` 단독 전부 ok · (xv)⑤ `get_person_card` 가 `PersonNotFound` → `reply == no_record_reply(["팀장"])`·`answer_source no_record`·`person_id None`·`resolutions[0].person_id == merge id`·answerer 0 · (xvi) `_read_card(ctx(local), other.id) is None`, 다른 user 의 같은 별칭은 ER 후보에도 없음(`candidates` id 에 없음) | (a) 스파이 1회·격리 테스트 | 일치. V12 생존(§3, R-U4-2) |
| 결정 D·E — 근거 조립은 카드, 근거 0건이면 LLM 0(`has_evidence`), `answerer.answer()` → `validate_query_answer` → 실패·`JudgeUnavailable` 이면 템플릿, 예외를 올리지 않음, `SQLAlchemyError` 는 삼키지 않음 | 1350~1377행 | (vii) 근거 0건 → `call_count 0`·`fallback no_evidence`·`template`·tokens (0,0)·`QUERY_MORE_HINT` 없음 · (v) 금지 표현 → 템플릿·`forbidden_expression`·`rejected_answer` 원문(앞뒤 공백 포함) · 241자 → `too_long` · 빈 답 → `empty`·`rejected_answer ""` · (vi) `fail="timeout"` → 템플릿·`answerer_error:timeout`·`rejected None`·예외 없음·`loop_error`/`tool_error` 0 · `rate_limit` → `answerer_error:rate_limit` · (xv) `get_person_card` 의 `SQLAlchemyError` 와 답 생성기의 `SQLAlchemyError` 둘 다 `run_turn` 밖으로 그대로 | (d)(e)(f) | 일치. P4a·P4b·V3·V21·V24 검출, V20 생존(§3) |
| 수용 판단 ③ — LLM 본문은 `answer.text.strip()`, `rejected_answer` 는 원문 | 1372~1375행 | (v) `"  요즘 많이 힘들어 보여요  \n"` → `rejected_answer` 그 원문 · `"  <본문>\n"` 유효 답 → `reply == 본문 + "\n" + QUERY_MORE_HINT` | — | 일치. V10·V11 생존(§3) |
| 결정 F ①~⑤ — `QUERY_MORE_HINT` 는 `answer_source=="llm"` 뿐, 결정 J 안내는 ask 제외 `dropped>0` 일 때, 순서 본문 → 한 사람씩 → 더보기, `\n` 으로 잇기 | 1379~1382행 | (i) `reply == 본문\nMORE` · (viii) `reply.splitlines() == [본문, ONE_AT_A_TIME, MORE]` · (ix) new_person 5 + dropped → `no_record_reply(앞5)\nONE_AT_A_TIME`, MORE 없음 · identity+dropped → 안내 없음·reply == 질문 · (v)(vii) 템플릿은 자기 문구 안의 MORE 1회뿐(루프가 더 붙이지 않음) · (iii) no_record 에 MORE 없음 | (h)(h2)(n)(o)(p) | 일치. V4 검출, 구현자 M6·M13·M14 와 정합 |
| 결정 C — `loop_query` 1행(`tool_name="agent"`), output 10키 정확히, `resolutions[]` 6키, `answer_source` 5어휘, `tokens_in/out` = `QueryAnswer.trace_tokens()`(LLM 안 부르면 0), `loop_resolve_done`/`loop_record` 없음, 답한 턴 `stop_reason=None`, identity 는 `"ask_user"` | `_QueryTrace` 1199~1230행 · `_log_query` 1263~1270행 · 1384~1409행 | (i) 키 집합 == 10개 정확히·`resolutions[0]` 6키·값 `{"mention":"팀장","band":"merge","person_id":p,"er_trace_id":er행id,"applied":false,"question_id":null}`·`loop_query` 1·`loop_turn` 1·`loop_resolve_done` 0·`loop_record` 0·`tool_name agent`·`stop_reason None`·`stored {0,0,0}` · (ii) `evidence_counts` 전부 0 dict(수용 판단 ②)·`stop_reason "ask_user"`·`answer_source "ask"`·`person_id None`·`reply == 질문` · 토큰: 유효 답 (11,7) → 컬럼 (11,7), 검증 실패 답도 (11,7) 기록(LLM 을 불렀으므로 — 원칙9 비용 관측) · output 에 `tokens` 키 없음, `trace_tokens()` 가 `(in,out)` tuple | (k)(k2)(q)(c) | 일치. V6·V13(생존)·V14·V15·V19 검출/생존 |
| `TurnResult.trace_ids = [loop_extract, loop_gate, loop_query]` id · `_log_turn` | 1403~1409행 | (i)(ii) `trace_ids == [extract, gate, query]` 행 id, identity 에서도 3개(ER·`ask_user` 행은 따로) · `loop_turn.output.reply == loop_query.output.reply == result.reply` | (a) | 일치. V2·V5 검출 |
| 결정 K (a)+R-1 — `answerer is None` 이고 근거 있을 때만 `from app.agent import respond as _respond` 뒤 `_respond.answerer_from_env()` 모듈 속성 호출 | 1364~1368행 | `grep -n answerer_from_env` 1368행 1곳(속성 호출), `loop` 모듈 전역에 그 이름 없음 · (x) `app.agent.respond.answerer_from_env` 치환 → 1회 호출·llm 답 · (xi) 근거 0건·new_person·언급 0 에서 0회(키 없는 운영에서 조회가 터지지 않음) | (r)(s) | 일치 |
| 수용 판단 ⑦ — `QUERY_MAX_PERSONS` 미import, 값 1 은 코드 구조로 보장 | 1318행 `break`(주석만) | (viii)⑦ band 만 가진 가짜 `resolve`(new_person → merge → …) 로 `resolve` 2회·dropped 1·`person_id` == 첫 merge 인물·resolutions 2·답 본문 = 그 인물 카드 LLM 답 — merge 뒤 둘째 인물로 가는 경로가 없다(`card`·`person_id` 는 merge 에서 한 번만 대입되고 바로 `break`) · `QUERY_MAX_PERSONS == 1`·`loop` 모듈에 이름 없음 | (o)(h) | 일치. V22(break 제거) 15 FAIL |
| 원칙1·2·4 — 루프는 `band` 만 본다 | 전체 | 추가 276줄에 `confidence`/`band_by_threshold`/`T_merge`/`T_new`/`s_llm`/`s_emb`/`s_rule`/`breakdown`/`.score` 0 · `resolution.` 속성 접근 집합 == `{band, matched_person_id, trace_id, ask_payload}` · `config.`/`judge.` 접근 0(통과만) · 기준 `8a8767b` 와 현재의 grep 결과 동일(`band_by_threshold="new_person"` 기존 1줄만, 행 번호 1214 → 1487) | (h2) docstring | 일치 |
| 혼합 발화 (g) — `intent query` 면 기록 0, 게이트 사유 `query_turn_no_write` 가 `loop_gate.output.rejected` 에 | (게이트는 U2) | (g) 저장 0·`add_event` tool_call 0·`{"index":1,"name":"add_event","reason":"query_turn_no_write"} ∈ rejected`·`accepted == []`·언급 1개 | (g) | 일치 |
| R-U3-1 — DB `raw_utterance` 시드가 `reply`·`loop_query` JSON·답 생성기 user_text 에 없음 | — | (xiii) `events.raw_utterance="절대노출금지원문"` 8행 시드(DB 에 실제로 있음 확인) → `reply`·`loop_query.output` JSON·user_text·세션 `agent_traces` 전체(input+output, 7행) 어디에도 없음 | (l) | 일치 — U3 R-U3-1 닫힘 |
| 테스트 목록 (a)~(k) + 공용 헬퍼 `_counts`·`assert_no_writes` | — | 23함수가 (a)~(k) 11항목 + (h2)(h3)(k2)(l)(n)(o)(p)(q)(r)(s)·스파이·격리를 덮는다(§5) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_agent_query_loop.py -v` | 23 passed in 0.73s, exit 0 | `…-1258-verifier-u4-tests.txt` |
| `… pytest tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_propose.py tests/test_agent_types.py tests/test_agent_query_types.py tests/test_agent_query_gate.py tests/test_agent_query_answer.py -q` | 283 passed, exit 0 | `…-1258-verifier-u4-regression9.txt` |
| `… pytest tests/ -q -rs` | 2104 passed, 1 warning in 24.58s — `skip` 문자열 0줄. 기준 2081 + 23 | `…-1258-verifier-u4-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-1259-verifier-u4-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-1259-verifier-u4-tools-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` | 빈 출력 — 기존 테스트 파일 수정 0(신규 1개는 untracked) | `…-1259-verifier-u4-scope.txt` (A) |
| `git diff --stat HEAD -- app/api app/er app/tools app/briefing app/memory app/db app/main.py app/agent/respond.py app/agent/gate.py app/agent/propose.py app/agent/types.py app/agent/__init__.py app/settings.py alembic web scripts` | 빈 출력 | 같은 파일 (B) |
| `git diff --numstat HEAD -- app` | `276 3 app/agent/loop.py` 1파일 | (C) |
| `git diff HEAD -- app/agent/loop.py` 의 `-` 줄 전수 | 3줄 — `from app.agent.respond import build_reply` / `from app.settings import LOOP_MAX_RESUME_BYTES, PATTERN_KEY_PREFIX, user_timezone` / `from app.tools.types import AFFIRMATIVE_KEY, PendingQuestionOut, ToolError`(전부 괄호 import 로 확장, 이름 유실 0). `diff <(git show HEAD:…) …` 의 `<` 줄도 같은 3줄. hunk 9개 중 `run_turn` 안은 `+1`(키워드)·`+11`(분기) 뿐, 나머지는 docstring 절·import·새 함수 블록(`+229`) | (D)(D2)(D3)(D4) |
| `grep -n "answerer_from_env" app/agent/loop.py` / `grep -n "from app.api\|import app.api"` / 1~260행 `app.api` | `1368: answerer = _respond.answerer_from_env()` 1곳 / `1255: from app.api.read import get_person_card` 1곳 / 0 | (E)(F)(F2) |
| 순환 import 3순서 | `agent-first ok`·`api-first ok`·`loop-only ok` | (G) |
| 확신도·임계치 grep 기준 대조 | 8a8767b 1줄 == 현재 1줄(기존 `band_by_threshold="new_person"`), 추가 줄 0 | (H) |
| `pytest --collect-only -q` ↔ `tests.md` U4 절 | 수집 23 / 표 23, 이름 `diff` → `SAME` | (I) |
| registry·03-log·구현 증거 목록·`git status` | `loop.py` 행 비고 "P5b U4(해시 pending)" 1곳 + 새 행 `tests/test_agent_query_loop.py` 23건(U4) pending / 03-log 는 "남은 것 · 다음 단위: U4" 까지(U4 항목 없음) / 구현 증거 9 / status 는 제품 1 + 문서 5 + 신규 테스트 1 + 증거 | (J)(K)(L)(M) |
| 구현 제약 (1)~(5) — `git diff HEAD -- app` 추가 줄 276 대상 | (1) `create_person\(\|update_person\(` 0 / (2) 확신도 영어 어휘 0 / (3) `sleep`·`while True` 0 / (4) `PendingQuestion`(Out 제외)·`flag_modified`·`.context =` 0(Out 포함 출현 3 = import·타입·생성자) / (5) 키 패턴 0 / 금지 호출 `resolve_mentions(`·`_record(`·`_record_impl(`·`after_record(` 0(이름 출현 3건은 docstring 2 + `_SRC_NO_RECORD` 상수) / `app_tools.` 기록 툴 0 / `os.environ`·`getenv` 0. R-4 집계: `create_person\(` app/agent 1 = 기준 1, `update_person\(` 5 = 기준 5(`--include='*.py'`; `__pycache__` 바이너리 제외), `PendingQuestion\|flag_modified\|.context =` loop.py 12 = HEAD 10 + `PendingQuestionOut` 2. 신규 테스트 파일: 키 패턴 0, 실 공급자·네트워크 import 0 | `…-1259-verifier-u4-grep-constraints.txt` |
| 계약 값 Python 99 항목(§1 의 (i)~(xvi) + 토큰·혼합 발화) | 99 PASS / 0 FAIL, exit 0(3회차) | `…-1305-verifier-u4-contract-values.txt` |
| 저장소 무수정 | 변이 뒤 `git status --short` = 리뷰 전과 같음, 사본 `loop.py`/`respond.py` ↔ 저장소 `SAME` | `…-1306-verifier-u4-mutation.txt` 끝 |

## 3. 변이 시험 — 내가 직접 (`20261102-1306-verifier-u4-mutation.txt`)

방법: 스크래치패드 `verifier-p5b-u4/mutate.py` 가 `app`·`tests`·`alembic`·`pyproject.toml`·`alembic.ini` 를 `verifier-p5b-u4/repo/` 에 한 번 복사하고, 변이마다 `loop.py`/`respond.py` 를 저장소 원본으로 되돌린 뒤 문자열 치환(정확히 1곳 — 아니면 중단)을 적용해 `POSTGRES_PORT=5433 pytest tests/test_agent_query_loop.py -q -p no:cacheprovider`(23건, 테스트 DB 롤백)를 돈다. 구현자의 `p5b-u4/mutate.py`(M1~M14)와 독립.

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군 | 없음 | 23 passed | — |
| P1 계획1 merge 에서 `apply_resolution()` | merge 분기에 호출 추가 | FAIL 3 | (a)·(g)·`test_forbidden_callees_are_never_called` |
| P2 계획2 new_person 에서 `apply_resolution()` | new_person 분기에 호출 추가 | FAIL 2 | (b)·(p) |
| P3a 계획3 변형 — `evidence_counts.timeline` 의 `min` 제거 | `len(card.timeline)` | FAIL 1 | (a) `evidence_counts == {3,0,5,2}` |
| P3b 계획3 — U3 프롬프트 슬라이스 5→6(`respond.py` 사본) | `[:QUERY_TIMELINE_LIMIT + 1]` | FAIL 1 | (a) user_text `- [meal]` 줄 == 5 |
| P4a 계획4 폴백 제거 — 공급자 오류 전파 | `except JudgeUnavailable` → `except ZeroDivisionError` | FAIL 2 | (e)·(n) |
| P4b 계획4 폴백 제거 — 검증 실패해도 원문 채택 | `if invalid is None` → `if True` | FAIL 1 | (d) |
| P5 계획5 조회 분기 뒤 기록 경로 — `return` 제거(폴스루) | `return _run_query_turn(` → `_run_query_turn(` | FAIL 16 | (a)(b)(c)(d)(e)(f)(h)(h2)(i)(n)(o)(p)(r)(s)·스파이·격리 — (g) 는 통과(§4b) |
| V1 identity 에서도 `apply_resolution` 생략 | `applied = SimpleNamespace(pending_question_id=0)` | FAIL 2 | (c)·(h2) |
| V2 `trace_ids` 에서 gate 누락 | `[extract_trace_id]` | FAIL 1 | (a) |
| V3 `fallback_reason` 접두 `answerer_error:` 누락 | `f"{exc}"` | FAIL 1 | (e) |
| V4 `QUERY_ONE_AT_A_TIME_HINT` 를 ask 에도 | `if dropped > 0:` | FAIL 1 | (h2) |
| V5 `_log_turn` 생략 | `return turn` | FAIL 1 | (a) `loop_turn` 1행 |
| V6 `stop_reason="ask_user"` 를 답한 턴에도 | 상수화 | FAIL 1 | (q) |
| V7 `_query_mentions` 중복 제거 제거 | `if text:` | FAIL 1 | (h3) |
| V8 `_query_mentions` strip 제거 | `text = value` | FAIL 1 | (h3) |
| V9 new_person 을 "기록 없음" 목록에 안 넣음 | `unrecorded.append` 삭제 | FAIL 3 | (b)·(p)·격리 |
| V10 `rejected_answer` 를 strip 본문으로(③) | `answer.text.strip()` | 생존 23 passed | — (R-U4-2) |
| V11 LLM 본문 strip 생략(③) | `answer.text` | 생존 | — (R-U4-2) |
| V12 `_read_card` 가 `PersonNotFound` 를 흡수하지 않음(⑤) | `except ZeroDivisionError` | 생존 | — (R-U4-2) |
| V13 `resolutions[].person_id` 항상 `None` | 상수화 | 생존 | — (R-U4-2) |
| V14 `resolutions[].er_trace_id` 를 `None` | 상수화 | FAIL 1 | (a) |
| V15 `evidence_counts` facts↔patterns | 바꿈 | FAIL 1 | (a) |
| V16 언급 상한 +1 | `[:LOOP_MAX_MENTIONS + 1]` | FAIL 1 | (p) |
| V17 identity `PendingQuestionOut.options` 빈 목록 | `options=[]` | FAIL 1 | (c) |
| V18 identity `entry["applied"]` 안 올림 | 줄 삭제 | FAIL 1 | (c) |
| V19 `loop_query.output.intent` 를 `"record"` | 상수 | FAIL 1 | (k) |
| V20 답 생성기 예외를 `Exception` 전부 삼킴(E-4 위반) | `except Exception` | 생존 | — (R-U4-2) |
| V21 근거 0건이어도 LLM 호출 | `if False:` | FAIL 2 | (f)·(r) |
| V22 merge 뒤 `break` 제거 | `pass` | FAIL 15 | (a)(d)(e)(f)(g)(h)(k)(k2)(l)(n)(o)(q)(r)(s)·스파이 |
| V23 `search_person` 언급을 `person` 키에서 읽음(B-3 위반) | `args.get("person")` | FAIL 19 | 거의 전부 |
| V24 검증 실패 시 빈 reply | `reply = ""` | FAIL 1 | (d) |

적용 31 / 검출 26 / 생존 5 / 동등 0. 계획 표 5건은 P1·P2·P3a+P3b·P4a+P4b·P5 로 전부 검출되지만 3번·5번은 계획이 적은 테스트와 검출 경로가 다르다(§4a·§4b). 생존 5건은 전부 코드가 맞게 돼 있고 테스트가 그 값을 고정하지 않은 공백이다 — 내 contract-values 3회차가 그 값을 직접 확인했다((v) ③·(xv)⑤·(i)(xv) `resolutions[].person_id`·(xv) `SQLAlchemyError` 전파). 구현자 증거 `…-1233-u4-mutation.txt` 의 M1~M14(16건 검출)와 내 P/V 결과가 겹치는 자리(M1=P1, M2=P2, M3a=P3a, M3b=P3b, M4a=P4a, M4b=P4b, M6/M13/M14=결정 F, M8=V6, M10=V22, M11, M12)에서 결과가 맞다.

## 4. 계획 불일치·메모 판정

### 4a. 변이 표 3번 "타임라인 슬라이스 5→6 → (a) ≤5 단언 FAIL" — `loop.py` 에는 슬라이스가 없다

슬라이스는 U3 `respond.py::build_query_answer_prompt` 의 `evidence.timeline[:QUERY_TIMELINE_LIMIT]` 에 있고, 루프는 카드를 통째로(타임라인 8건 — (i) `seen_timeline_len == [8]`) `answerer.answer(utterance, card, now)` 에 넘긴다(U3 계약 `evidence: PersonCardOut` 그대로). 루프가 가진 것은 trace 건수 `evidence_counts.timeline = min(len, QUERY_TIMELINE_LIMIT)`(결정 C "타임라인은 상한 뒤") 뿐이다. 구현자가 한 두 변이는 서로 다른 코드 경로이고 동등이 아니다: P3a(`min` 제거)는 trace 건수만 틀리게 하고 프롬프트는 그대로이며, P3b(`respond.py` 슬라이스)는 프롬프트만 바꾸고 trace 건수는 그대로다. (a) 는 두 단언(`evidence_counts == {…,"timeline":5,…}` 와 `_RecordingAnswerer` 가 U3 프롬프트 층을 호출해 센 `- [meal]` 줄 == 5)을 다 가지고 있어 둘 다 잡는다. 코드 결함 없음. 계획 문구 수정안(R-U4-1): "`evidence_counts.timeline` 의 `min` 제거 → (a) `evidence_counts` 단언 FAIL; 프롬프트 타임라인 슬라이스(U3 `respond.py`)는 (a) 의 user_text ≤ 5 단언이 U3 층을 거쳐 잡는다(`loop.py` 에는 슬라이스 없음 — 사본 변이로 확인)".

### 4b. 변이 표 5번 "`_record` 호출 → (g) FAIL" — (g) 는 잡지 못한다

P5(`return` 제거로 조회 뒤 기존 기록 경로가 돈다)에서 16개가 FAIL 하지만 (g) `test_g_mixed_utterance_does_not_execute_write` 는 통과한다(변이 증거 P5 FAILED 목록에 없음). 이유: 조회 턴에서는 게이트 Q 관문(U2)이 기록 툴 제안을 전부 거부하므로 `resolve_mentions` 가 받는 `verdict.accepted` 가 `[]` 이고 `_record` 가 쓰는 행이 0 이다 — (g) 의 단언(저장 0·`add_event` tool_call 0·`loop_gate.rejected`·`stored.events == 0`)은 전부 그대로 참이다. 실제로 잡는 것은 `test_forbidden_callees_are_never_called`(스파이)와 (a) 의 `loop_record == []`·reply 단언이다. 구현자 보고가 맞다. 코드 결함 없음. 계획 문구 수정안(R-U4-1): "조회 분기 뒤 기록 경로가 돌게(`return` 제거 또는 `_record` 호출) → `test_forbidden_callees_are_never_called`(금지 호출 스파이)·(a) `loop_record` 0행·reply 단언 FAIL — (g) 는 게이트가 조회 턴의 기록 제안을 이미 전부 거부해 쓰기 0 이므로 이 변이를 잡지 못한다".

### 4c. 사용자가 수용한 구현자 판단 7건 — 코드와 일치

① `_QueryTrace` frozen dataclass(1199~1230행) — `to_dict()` 10키, `trace_tokens()` tuple, `tokens` 는 `repr=False` 이고 output 에 없음((i)) ② 카드 안 읽은 턴 `evidence_counts` 전부 0 dict — (ii)(iii)(iv) ③ `reply = answer.text.strip()`, `rejected_answer = answer.text` — (v) ④ `dropped = len(mentions) - resolved` — (viii)(ix) 상한·merge 뒤·identity 뒤 모두 맞음 ⑤ `PersonNotFound` → `None` → "기록 없음" — (xv)⑤ ⑥ identity `PendingQuestionOut` 인라인 조립(1329~1335행)이 기존 `_pending_question_from_resolve`(1074~1080행)와 같은 5필드·`status="pending"`·`list(payload["options"])` ⑦ `QUERY_MAX_PERSONS` 미import — 값 1 은 구조로 보장된다: `card`/`person_id` 는 merge 분기에서만 대입되고 그 자리에서 `break` 하므로 둘째 인물로 답하는 경로가 존재하지 않는다((viii)⑦ new_person → merge → 중단 확인, V22 `break` 제거 시 15 FAIL). 상수가 코드에서 안 읽히므로 `QUERY_MAX_PERSONS = 2` 로 바꿔도 동작이 안 바뀐다는 점은 U1 리뷰·결정 J 확정 범위 안의 사실(값을 바꾸려면 코드 변경이 필요)이고 결함이 아니다.

### 4d. 계획에 없는 것이 들어갔는가

새 상수·환경변수·문구·방어 조건 없음: `_SRC_*` 5개는 결정 C 어휘의 이름, `_QueryTrace`/`_query_mentions`/`_read_card`/`_log_query` 는 계획 ①~⑥ 을 담는 비공개 함수. `assert resolution.matched_person_id is not None`·`assert payload is not None` 은 기존 `_pending_question_from_resolve`·`_extend_identity_payload` 와 같은 관례. `_read_card` 의 `ctx.now()`(UTC) 는 `app/api/routes.py` 453행이 `get_person_card` 에 넘기는 것과 같은 종류이고, 답·템플릿의 `now` 는 `run_turn` 이 이미 사용자 시간대로 바꾼 값(FIX-005) — 일관. `resume_turn`·`app/api`·`web` 무변경(U5·U6 몫).

### 4e. `loop_query.input` 관례(메모)

`_log_query(ctx, utterance, record)` 를 `@traced` 로 감싸므로 `input` 이 `{"utterance", "record"}` 가 되고 `record` 는 `to_dict()` 결과(= output 과 같은 내용)다((i) 확인). `_log_turn` 의 `{"utterance","turn"}` 과 같은 관례라 위반이 아니지만, P10 이 `loop_query` 를 집계할 때 `output` 만 읽으면 된다는 메모(R-U4-3).

## 5. `tests.md`·`registry.md`·테스트가 실패 조건을 검사하는가

- `tests.md` U4 절 표 23행 ↔ `--collect-only` 23: `diff` → `SAME`. 머리글 "23 passed"·"2104 passed, skip 0; 2081 → +23"·"M1~M14 16건 검출" 은 구현 증거 `…-1231-u4-loop.txt`(23 passed)·`…-1231-u4-pytest-all.txt`(2104 passed)·`…-1233-u4-mutation.txt` 와 내 재실행에 맞다. (h2)(j) 의 "첫 실행 실패 → 테스트 쪽 가정 오류 수정" 실패 이력이 적혀 있다(record-every-test 규칙). (g) 행의 "※ `_record` 호출 변이는 이 케이스가 아니라 스파이가 잡는다" 메모는 §4b 와 일치.
- 01-plan 108행 테스트 (a)~(k) 11항목 ↔ 23함수: 전부 덮인다. 계획에 없는 추가 12개((h2)(h3)(k2)(l)(n)(o)(p)(q)(r)(s)·스파이·격리)는 결정 B-3/F/J/K·R-U3-1·"부르지 않는 것" 의 직접 번역이라 범위 초과가 아니다. 공용 헬퍼 `_counts`(7개 테이블)·`assert_no_writes` 가 계획대로 이 파일에 있다.
- 테스트가 실제로 실패 조건을 검사하는가: §3 에서 26 변이가 서로 다른 부분집합으로 FAIL 한다. 값으로 단언하는 곳이 많다(reply 정확 문자열·`evidence_counts` dict·`resolutions[0]` 키 집합·`er_trace_id == 행 id`·`trace_ids == [id,id,id]`·`context["resume"]["intent"]`·`options == ER 원본`·토큰 (11,7)). 공백은 생존 5건(R-U4-2) — 이 중 `test_other_user_person_is_not_visible` 은 "다른 사용자 인물" 이 ER 후보에서 걸러져 new_person 이 되므로 `_read_card` 의 `PersonNotFound` 분기를 지나가지 않는다(V12 생존 이유).
- `registry.md`: `loop.py` 행 "P5b U4(해시 pending)" 비고(키워드·분기 1곳·비공개 함수 4+1·merge/new_person `resolve()` 만·identity 만 되묻기·저장 0·지연 해소·"기존 함수 본문 무변경(import 3줄만 교체)")가 코드·(D) 와 맞다 / 새 행 `tests/test_agent_query_loop.py` 23건(U4)·pending·`_counts`·`assert_no_writes`. 커밋 뒤 해시 치환 2곳은 메인 세션 몫.

## 6. 범위·원칙

- 범위: `app/` 변경 1파일 = 01-plan 105행이 지정한 `loop.py`. `app/api`·`app/er`·`app/tools`·`app/briefing`·`app/memory`·`app/db`·`app/main.py`·`respond.py`·`gate.py`·`propose.py`·`types.py`·`__init__.py`·`settings.py`·`alembic`·`web`·`scripts` diff 0. 기존 테스트 파일 수정 0. 기존 `loop.py` 줄 제거 0(import 3줄 확장만). "하지 않는 것" — `resolve_mentions`·`_record`·`_record_impl`·`after_record`·기록 툴 4종을 조회 분기가 부르지 않음(grep 0 + 스파이 (xii) 3경로), `resume_turn` 무변경(U5), `app/api` 무변경(결정 K (a)·L (a)), 새 툴·새 API 없음(7/7).
- 원칙1·2·4: 루프는 `band` 만 읽는다 — 추가 줄에 확신도·임계치·신호 이름 0, `resolution.` 속성 4종만((xiv)). 확신도 판정은 ER 안(`er_resolve` 행이 그대로 남고 `decision.applied` 는 적용 여부를 사실대로).
- 원칙7: 답은 U3 검증기를 거치고 실패·오류·근거 0건이면 템플릿((v)(vi)(vii)); 한 턴 한 인물(결정 J — 인물 간 관계 서술 재료가 프롬프트에 안 들어감, (viii)⑦); `reply` 에 상담성 문장 생성 지점 없음(문구는 전부 U3 상수·템플릿·ER 질문).
- 원칙9: `loop_query` 1행에 의도·언급·해석(band·er_trace_id·applied·question_id)·근거 건수·답·폴백 사유·거절 원문·토큰(컬럼) — 결정 C 전부((i)(ii)). `loop_turn` 은 기존대로.
- 툴 시그니처 v2·스키마 v2 무변경(`tools_check` 7/7, `alembic`·`app/db` diff 0). S3.4 끝 줄(`intent` 1필드·new_person 질문 0) — (ii)(iii).
- security §1: 추가 줄·신규 테스트에 키 패턴 0, `os.environ` 0, trace·reply 에 원문(`raw_utterance`) 0((xiii)). `.env` 미독. 증거는 전부 `save_evidence.py`(비밀 검사 통과). 변이는 스크래치패드 사본에서만, 저장소 무수정.
- 동결·활성: 활성 패키지 P5b-query-turn(`fe4a99e`), U1 `1dccb95`·U2 `06b7bb5`·U3 `a002706` 위의 네 번째 단위.

## 7. 소견

[필수] 없음.

[권고] (커밋을 막지 않음)

- R-U4-1 · 01-plan 110행 변이 표의 3번·5번 문구가 실제 검출 경로와 다르다(§4a·§4b). 수정안 — 3번: "`evidence_counts.timeline` 의 `min` 제거 → (a) `evidence_counts` 단언 FAIL; 프롬프트 타임라인 슬라이스(U3 `respond.py`)는 (a) 의 user_text ≤ 5 단언이 U3 층을 거쳐 잡는다(`loop.py` 에는 슬라이스 없음)". 5번: "조회 분기 뒤 기록 경로가 돌게(`return` 제거 또는 `_record` 호출) → `test_forbidden_callees_are_never_called`(스파이)·(a) `loop_record` 0행·reply 단언 FAIL — (g) 는 게이트가 조회 턴의 기록 제안을 이미 전부 거부해 쓰기 0 이므로 잡지 못한다". 계획 문서 수정은 메인 세션(03-log 에 "U4 실측" 으로 적는 방식이면 U1 R-U1-1 과 같은 형식).
- R-U4-2 · 생존 변이 5건 = 테스트 공백(코드는 계약대로 — 내 contract-values 가 값으로 확인). (가) V10·V11 수용 판단 ③(LLM 본문 `strip()`·`rejected_answer` 원문)을 고정하는 테스트 없음 — Fake 답에 앞뒤 공백을 넣은 케이스 1개면 둘 다 잡힌다. (나) V12 수용 판단 ⑤(`_read_card` 의 `PersonNotFound` → "기록 없음")를 지나는 테스트 없음 — `app.api.read.get_person_card` 를 `PersonNotFound` 로 monkeypatch 한 케이스 1개. (다) V13 `resolutions[].person_id` 를 아무 테스트도 값으로 안 봄 — (a) 에 `out["resolutions"][0]["person_id"] == person.id` 한 줄. (라) V20 답 생성기 `except` 범위 — E-4 "`SQLAlchemyError` 는 삼키지 않는다" 를 고정하는 테스트 없음(답 생성기가 `SQLAlchemyError` 를 내면 `run_turn` 밖으로 나가야 함; `except Exception` 으로 넓혀도 23건 통과). U5 가 ③~⑥ 을 같은 함수로 재사용하므로 U5 테스트에 넣는 것이 자연스럽다(메인 세션 판단, 지금 커밋 영향 없음).
- R-U4-3 · `loop_query.input` 에 `record`(= output 과 같은 dict)가 함께 저장된다(§4e). `loop_turn` 의 `{utterance, turn}` 관례와 같아 위반이 아니고 저장량도 작지만, P10 집계·04-review §7 P10 인계에 "`loop_query` 는 `output` 만 읽는다" 한 줄.
- R-U4-4 · 03-log U4 항목(메인 세션) + `registry.md` 해시 pending 2곳(`loop.py` 비고·새 행). 적을 것: ① 내 재실행 23·283·2104(2081 + 23)·skip 0·ruff·7/7·범위 diff 0·기존 테스트 수정 0·`loop.py` `-` 줄 3(import) ② 계약 값 99 PASS(3회차; 1회차 conftest import 로 FIX-006 가드, 2회차 내 시나리오 오류 8 — 둘 다 내 스크립트 문제) ③ 변이 31 적용·26 검출·5 생존(테스트 공백)·동등 0(구현자 M1~M14 16건 검출과 정합) ④ 계획 불일치 2건 판정(§4a 동등 아님·둘 다 필요, §4b (g) 가 못 잡는 것이 맞음) + 수용 판단 7건 일치(⑦ 구조 보장) ⑤ R-U4-1~4. Refs `P5b-query-turn U4 CR-004 D16 S3.4 D1 D2 D10 원칙1 원칙2 원칙4 원칙7 원칙9 R19`.

## 8. 판정

통과. U4 의 계약 전부 — `run_turn(answerer=None)` 키워드와 게이트 직후 분기 1곳(기존 본문 무변경, `-` 줄은 import 3) · 결정 B-3 (b) 언급 출처 규칙 · 결정 J(상한 `LOOP_MAX_MENTIONS`, merge 에서 `break`, `mentions_dropped`, 안내 한 줄) · 결정 I (a)(merge·new_person 은 `resolve()` 만 — `er_resolve.decision.applied false`·별칭 0·`update_person` 0, identity 만 `apply_resolution`) · 결정 G(`PendingResume(intent="query")` 직렬화가 기존 identity 기록 턴 context 와 같은 모양 + `intent` 키) · D16 5(new_person 질문 0) · 결정 L (a)(지연 import 1곳, 순환 3순서 ok, `PersonNotFound` → 기록 없음, user 격리) · 결정 D·E(근거 0건 LLM 0, 검증 실패·`JudgeUnavailable` → 템플릿·사유 어휘, `SQLAlchemyError` 전파) · 결정 F(`QUERY_MORE_HINT` 는 llm 뿐, 순서) · 결정 C(`loop_query` 10키·6키·`stop_reason`·토큰·`loop_resolve_done`/`loop_record` 0) · 결정 K R-1(모듈 속성 호출 1곳, 근거 0건이면 해소 안 함) · 원칙1·2·4(`band` 만) · R-U3-1(원문 비노출 DB 시드로 확인) — 가 01-plan 105~110행·결정 확정 칸·D16 결정 2(보정 ①)·3·4·9·"코드에서 지켜야 할 것" 3·4·5·사용자 수용 판단 7건과 맞고, 내 재실행에서 23 passed·회귀 283·전체 2104 passed(2081 + 23)·skip 0·ruff 통과·`tools_check` 7/7 이다. 변이 31건 중 26 검출, 생존 5 는 테스트 공백(코드 결함 아님, 계약 값 99 PASS 로 덮음). 범위 밖 diff 0, 기존 테스트 수정 0, 구현 제약 (1)~(5) 추가 줄 0건, 금지 호출 0(grep + 스파이), trace·reply 에 비밀·원문 0. 커밋을 막는 소견 없음.
