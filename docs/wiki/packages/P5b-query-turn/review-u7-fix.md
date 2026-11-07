# P5b-query-turn · U7 결함 수정 커밋 전 리뷰

검토자: verifier (fable)
일시: 2026-11-07
대상: 작업 트리 미커밋 변경(HEAD `be67c76`, 브랜치 `dev2`) — `app/agent/loop.py` · `app/agent/propose.py` · `tests/test_agent_query_loop.py` · `tests/test_agent_propose.py` · `tests/test_agent_query_gate.py` · `docs/wiki/packages/P5b-query-turn/tests.md` "## U7 결함 수정(2026-11-07)" 절
결과: **통과** (재리뷰 2026-11-07 15:10, §6) — 1차 판정은 **보류**([필수] 2건: 테스트 h3 입력 3줄 + D16 카드·01-plan 보정 문구)였고, 두 건이 닫힌 것을 직접 재실행으로 확인해 통과로 바꿨다. 1차 본문(§1~§5)은 기록으로 그대로 둔다.

---

## 1. 본 것(파일·줄)

| 파일 | 줄 | 본 내용 |
|---|---|---|
| `app/agent/loop.py` | 1236~1262 | `_query_mentions()` — `value = call.args.get("person")` 뒤 `search_person` 이면 `query` 가 비지 않은 문자열일 때만 `value` 를 덮어쓴다. 문자열 아님·공백은 기존처럼 제외. "나" 코드 필터 없음(docstring 에 결정 J 명시). 그 밖의 줄 변경 없음 |
| `app/agent/loop.py` | 1284~1330, 1395~1445 | `_run_query_turn()` — `mentions[:LOOP_MAX_MENTIONS]` 로 상한 재사용, merge 에서 `break`(답 인물 1명), `dropped = len(mentions) - resolved`, `dropped > 0` 이면 `QUERY_ONE_AT_A_TIME_HINT` 를 붙인다. **이 함수는 이번 diff 에 없다**(변경 0) — 수정의 파급을 보기 위해 읽었다 |
| `app/agent/propose.py` | 136~162 | `PROPOSAL_ARG_SCHEMA.properties` 에 `"query": {"type": "string"}` 1줄 추가(`person` 바로 뒤). 스키마는 원래 `additionalProperties: True`(162행) — `query` 는 추가 전에도 **금지되지 않았고 열거되지 않았을 뿐**이다 |
| `app/agent/propose.py` | 240~250 | 조회 예외 문장 "… search_person 을 하나씩 제안하고 그 언급을 query 필드에 써라(person 필드에 써도 받아들인다). …" 로 교체. 직전 문장 "절대 제안하지 마라." 와 248~249행 "'나'·'저'·'내'·'제' … 인물로 제안하지 마라." 는 그대로 |
| `tests/test_agent_query_loop.py` | 582~593 | h3 입력 9건·기대 `["가","나","읽힘","다","라"]` — `person` 폴백 1건, `query` 우선 1건, `person` 공백·정수 제외 2건 추가 |
| `tests/test_agent_query_loop.py` | 596~622 | `test_u7_real_llm_person_arg_shape` — u7r-1 과 같은 제안 모양(`person` 2건), `assert_no_writes`·`_write_tool_rows == 0`·`mentions == [...]`·`answer_source != "no_mention"`·`person_id == person.id` |
| `tests/test_agent_propose.py` | 134~147 | 스키마 `query` 속성 1건 · 프롬프트 문장 3구절 1건 |
| `tests/test_agent_query_gate.py` | 262~268 | `exception` 문자열을 새 문장으로 교체, "절대 제안하지 마라." 뒤 순서 단언 유지 |
| `docs/wiki/packages/P5b-query-turn/tests.md` | 182~203 | U7 절 — 표 4행 + 변이 3행 + 게이트 테스트 1행 + 이력 문단 |
| `docs/wiki/packages/P5b-query-turn/03-log.md` | 74~82 | U7 항목(pending) — 원인 서술 "스키마에 `query` 가 없었음" 포함 |
| 카드 | `docs/wiki/decisions/D16-query-turn.md` 결정 2·7·"코드에서 지켜야 할 것" 1~3 · `01-plan.md` 186~200(결정 B-3)·296~304(결정 J)·274(판정 표 1행)·리스크 "나" 항 | 아래 §3 대조 |
| evidence | `20261104-2110-u7r-{1..7}-*.txt` · `20261107-1455-u7fix-mutation.txt` · `20261107-1456-u7fix-pytest-all-2.txt` · `20261107-1455-u7fix-ruff.txt` | 7/7 `{"person": …}`·6/7 `no_mention` 확인(u7r-3 만 `get_briefing(person=…)` 덧붙음으로 통과) · 구현자 변이 3/3 검출 · 2125 passed · `-ruff.txt` 는 도움말만(잘못된 산출물, 03-log 79행도 인정) |

## 2. 직접 실행한 명령 · evidence · 결과

모두 `python3 .claude/scripts/save_evidence.py P5b-query-turn verifier-u7fix-<이름> -- <명령>` 으로 저장(`docs/wiki/packages/P5b-query-turn/evidence/`). DB 는 `POSTGRES_PORT=5433`.

| # | 명령 | evidence | 결과 | 기대 대비 |
|---|---|---|---|---|
| 1 | `pytest tests/test_agent_query_loop.py tests/test_agent_propose.py tests/test_agent_query_types.py tests/test_api_chat_query.py tests/test_agent_query_gate.py -q` | `20261107-1459-verifier-u7fix-pytest-target.txt` | **158 passed** | = 158 |
| 2 | `pytest tests/ -q -rs` | `20261107-1459-verifier-u7fix-pytest-all.txt` | **2125 passed**, skip 0(`-rs` 출력에 SKIPPED 없음) | = 2125 |
| 3a | `ruff check app tests` | `20261107-1500-verifier-u7fix-ruff.txt` | All checks passed, exit 0 | 통과 |
| 3b | `scripts/mypy_check.py --run` | `20261107-1500-verifier-u7fix-mypy.txt` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` | = 38=38 |
| 3c | `scripts/tools_check.py` | `20261107-1500-verifier-u7fix-tools.txt` | `RESULT: 7/7 ok` | = 7/7 |
| 4 | `git diff --name-only` | `20261107-1500-verifier-u7fix-diff-names.txt` | 9파일 = 코드 2 + 테스트 3 + `tests.md`·`03-log.md`·`journal.md`·`HANDOFF.md`. `app/api/`·`web/`·`app/settings.py` **0** | 범위 안 |
| 5 | 변이 4회(런타임 치환 플러그인, 스크래치패드 `mut-u7fix/vmut_*.py`, 저장소 무수정) — 대상 4파일 134건 | `20261107-1501-verifier-u7fix-mutation.txt`(4회 append) | 아래 표 | **2/3 검출 — 생존 2** |
| 6 | 탐침: u7 재현 입력에서 "나" 가 언급으로 들어온 뒤 실제 `reply`·`mentions_dropped` | `20261107-1503-verifier-u7fix-probe-self-mention.txt` | `mentions=['박선우 과장님','나']` · `mentions_dropped=1` · `resolutions=[('박선우 과장님','merge')]` · `answer_source=llm` · **`reply` 에 "한 번에 한 사람씩 물어봐 주세요." 가 붙음** | §4 R-U7F-3 |

변이 결과(대조군 → 변이):

| 변이 | 내용 | 기대 | 결과 |
|---|---|---|---|
| 대조군 `vmut_control` | 치환 없음 | 134 passed | 134 passed |
| V3 `vmut_nofallback` | `person` 폴백 제거(수정 전 코드) | h3·u7 FAIL | **2 failed**(h3, u7) — 구현자 M1 재현 |
| V1 `vmut_anytool_query` | 툴 이름 분기 제거 — 모든 툴에서 `query` 우선 | h3 FAIL | **134 passed — 생존** |
| V2 `vmut_blank_query_wins` | `search_person` 의 `query` 가 공백이어도 `person` 으로 폴백하지 않음(`strip()` 조건 제거) | h3 FAIL | **134 passed — 생존** |

생존 이유: h3 의 9개 입력에 ① `search_person` 아닌 툴이 `query` 키를 가진 경우, ② `search_person` 에 `query` 공백·`person` 유효가 **함께** 있는 경우, ③ `search_person` 에 `query` 비문자열·`person` 유효가 함께 있는 경우가 없다. 위임문 (A) "`query` 우선, **문자열이 아니거나 비면** `person` 폴백" 의 뒤 절과 결정 B-3 (b) "그 밖의 툴은 `person`" 절이 테스트에 고정되지 않았다.

## 3. 판정 근거(원칙·카드 대조)

| 항목 | 근거 | 판정 |
|---|---|---|
| 원칙1·2·4 — ER 4단계 재사용, 확신도·임계치 접근 없음 | diff 는 `_query_mentions`(언급 문자열 수집)와 스키마·프롬프트 문장뿐. `resolve()` 호출·band 분기·`T_merge`/`T_new` 어디에도 손대지 않았다(`loop.py` 1284~1330 변경 0). `tools_check` 7/7 | 지킴 |
| 원칙7 — 경계 | 답 생성·검증기·템플릿 무변경. 프롬프트 변경은 인식 단계 문장 1개 | 지킴 |
| 원칙9 — trace | `loop_query.output.mentions` 에 폴백으로 읽은 언급도 그대로 남는다(탐침 evidence) | 지킴 |
| D16 결정 2 "`search_person` 은 여전히 LLM 이 직접 부르지 못한다(게이트 ② 유지)" | 게이트 무변경. u7r 7건 모두 `not_callable_by_llm` 로 거부되고 실행 0 | 지킴 |
| D16 결정 7 "'나'·'저' 등은 **프롬프트 지시로** 언급에서 제외" · 결정 J "'나' 가 새어 들어온 경우 코드로 거르지 않는다" · 01-plan 274행 "언급에 '나' 없음(있으면 관찰로 기록 — 결정 J 규칙상 답은 여전히 박선우 과장님)" | 코드 필터 없음(docstring·구현 일치). 프롬프트 248~249행 지시 유지. 폴백으로 "나" 가 **이제 실제 경로에서도** 언급으로 들어온다(수정 전에는 `person` 인자가 통째로 버려져 "나" 도 안 들어왔다). 결정 J 대로 첫 언급 merge 로 답하고 "나" 는 해석하지 않는다(탐침 `resolutions` 1건) — **답 인물은 맞다.** 다만 `mentions_dropped=1` 이 되어 "한 번에 한 사람씩 물어봐 주세요." 가 붙는다(탐침 reply). 이는 결정 J 의 기존 규칙이 새로 도달 가능해진 것이며 카드와 **어긋나지 않는다**. 사용자에게 보이는 부작용은 R-U7F-3 으로 관찰 대상 | 어긋나지 않음 · 관찰 필요 |
| D16 "코드에서 지켜야 할 것" 1 "`propose.py` … `intent` enum 이 있고, **다른 필드·툴 제안 스키마는 그대로다**" · 01-plan B-3 (b) 행 "D16 문장 그대로 성립(**스키마는 `intent` 하나만 늘어난다**)" | `PROPOSAL_ARG_SCHEMA.properties.query` 1개가 늘었다 — 카드 문장과 **글자 그대로 어긋난다**. 04-review 는 이 규칙을 grep 으로 확인한다. 완화 사실: `additionalProperties: True` 라 금지가 풀린 것이 아니라 열거(유도)만 추가됐고, 위임문 (B) 가 명시한 범위다. 그러나 카드·계획 문구를 두지 않으면 04-review 에서 같은 지적이 다시 난다 | **R-U7F-1 [필수]** — 문구 보정 |
| 결정 B-3 (b) 문구 vs 코드 | 계획: "`search_person` 은 `args["query"]`, 그 밖의 툴은 `args["person"]`". 코드: `search_person` 은 `query` 우선, 비문자열·공백이면 `person` 폴백. 차이는 폴백 절 하나. 적는 법은 §4 R-U7F-1 에 문구로 제시 | 보정 문구 필요 |
| 결정 J 상한 `LOOP_MAX_MENTIONS` 재사용 · 답 인물 1명 | `mentions[:LOOP_MAX_MENTIONS]`·merge `break` 무변경 | 지킴 |
| 범위 — 위임문 (A)(B)(C) 밖 변경 | diff 9파일 중 코드 2·테스트 3 은 (A)(B)(C) 그대로. `03-log`·`journal`·`HANDOFF`·`tests.md` 는 기록. `app/api/`·`web/`·`app/settings.py` 0 | 지킴 |
| 테스트가 실패 조건을 검사하는가 | `test_u7_real_llm_person_arg_shape`: 저장 0 은 7테이블 전후 행 수 동등(`_counts`), 기록 툴 trace 0 은 SQL count, `person_id == person.id` 는 실제 id, `mentions` 는 정확 목록 — V3 변이에서 `mentions [] != [...]` 로 실패함(실제 값 단언 확인). 약한 곳: `answer_source != "no_mention"` 는 부정 단언 — 탐침으로 실제 값 `llm` 확인(R-U7F-3 에 보강 권고). h3: V3·구현자 M2 를 잡지만 V1·V2 생존 | u7 재현 유효 · **h3 공백 2 → R-U7F-2 [필수]** |
| 03-log 원인 서술 | 76행 "스키마에 `query` 가 없었음" — 정확히는 `additionalProperties: True` 라 **허용은 됐고 열거되지 않았을 뿐**. 원인 서술의 정확성(원칙8) | R-U7F-4 [권고] |
| evidence 위생 | `20261107-1455-u7fix-ruff.txt` 는 `sh -c` 인용 손실로 도움말만 찍힌 파일(exit 1). 03-log 79행·HANDOFF 가 "무시·삭제 대상" 으로 적었으나 아직 있다 | R-U7F-5 [권고] |

## 4. 소견

### [필수] — 커밋 전(코드 수정 없음)

- **R-U7F-1 D16 카드·01-plan B-3 (b) 보정 문구(메인 세션, 문서만).** 코드 규칙 1 과 B-3 (b) 근거 문장이 현재 코드와 글자 그대로 어긋나고, 04-review 가 grep 으로 확인하는 항목이다. 선례: D16 갱신 이력 2026-10-28 보정 2건. 제안 문구 —
  - `D16-query-turn.md` 갱신 이력에 1줄: "2026-11-07 **보정 ③(P5b U7, 실 LLM 왕복 `evidence/20261104-2110-u7r-*`)**: 코드 규칙 1 '다른 필드·툴 제안 스키마는 그대로다' 에 예외 1개 — `PROPOSAL_ARG_SCHEMA.properties.query`(string, 조회 턴 대상 표시용 `search_person(query=…)` 유도; 스키마는 `additionalProperties: True` 라 금지가 풀린 것이 아니라 열거만 추가). 루프는 `search_person` 의 `query` 를 우선 읽고 비문자열·공백이면 `person` 으로 폴백한다(gpt-4o-mini 7/7 `person`). 결정 7(코드 필터 없음)·결정 2(게이트 ② 유지)는 그대로."
  - `01-plan.md` B-3 (b) 행 끝 또는 확정 줄 아래에 1줄: "**보정(U7, 2026-11-07)**: `search_person` 은 `query` **우선**, 문자열이 아니거나 비면 `person` 폴백(그 밖의 툴은 `person` 그대로). 스키마에 `query` 속성 1개가 늘어 '스키마는 `intent` 하나만 늘어난다' 는 더 이상 성립하지 않는다 → D16 갱신 이력 보정 ③."
- **R-U7F-2 h3 에 입력 3건 추가(backend-agent, 테스트만) — 변이 V1·V2 생존 닫기.** `test_h3_mention_source_rule` 의 `tool_calls` 에 다음을 더하고 기대 목록을 맞춘다: ① `ToolCallProposal(name="add_event", args={"person": "바", "query": "사"})` → "바"(그 밖의 툴은 `query` 를 읽지 않는다 — V1), ② `ToolCallProposal(name="search_person", args={"query": "  ", "person": "아"})` → "아"(공백 `query` 는 `person` 폴백 — V2), ③ `ToolCallProposal(name="search_person", args={"query": 1, "person": "자"})` → "자"(비문자열 `query` 는 `person` 폴백). 추가 뒤 `vmut_anytool_query`·`vmut_blank_query_wins` 를 다시 돌려 각 1 FAIL 을 evidence 로 남기고 `tests.md` 변이 표에 U7-M4·M5 로 적는다. 플러그인은 스크래치패드 `mut-u7fix/` 에 있다(세션 종료 시 사라지므로 본 문서 §2 표의 내용으로 재작성 가능).

### [권고] — 다음 단위(U7 재실행·04-review)

- **R-U7F-3 "나" 폴백의 가시적 부작용 관찰.** 탐침 evidence: u7r-1 모양에서 `reply` 끝에 "한 번에 한 사람씩 물어봐 주세요." 가 붙는다(한 사람을 물었는데). 원인은 결정 J 의 `mentions_dropped` 규칙이 "나" 에도 적용되는 것 — 카드와 어긋나지 않으나 사용자에게 보인다. 조치는 **사용자 결정**(D16 결정 7 을 코드 필터로 바꾸는 것은 CR/FIX): (i) U7 재실행 ① 발화의 `reply` 에 이 문장이 붙는지 기록 → 01-plan 리스크 "'나' 제외가 프롬프트 지시뿐" 항의 "반복되면 FIX(코드 필터)" 판단 재료. (ii) `test_u7_real_llm_person_arg_shape` 에 `out["mentions_dropped"] == 1`·`answer_source == "llm"`·`QUERY_ONE_AT_A_TIME_HINT in result.reply` 를 **현재 동작의 기록**으로 단언해 두면 나중 FIX 가 바꿀 때 테스트가 알려 준다(지금은 부정 단언 `!= "no_mention"` 하나).
- **R-U7F-4 03-log 76행 원인 서술 정정.** "스키마에 `query` 가 없었음" → "스키마에 `query` 가 열거되지 않았음(`additionalProperties: True` 라 금지는 아니었음)". 수정의 성격이 "강제" 가 아니라 "유도 + 폴백" 임이 드러나게.
- **R-U7F-5 잘못된 evidence 삭제.** `evidence/20261107-1455-u7fix-ruff.txt`(도움말만, exit 1) 는 03-log·HANDOFF 가 삭제 대상으로 적었다 — 커밋에 들어가기 전에 지운다(메인 세션; `rm` 1파일). `-ruff-check.txt`·`-ruff-format.txt` 가 유효본.
- **R-U7F-6 프롬프트 문장의 양가성.** "query 필드에 써라(person 필드에 써도 받아들인다)" 는 모델에게 두 길을 다 열어 준다 — 유도 효과가 약해질 수 있다. 폴백이 있으니 결과에는 영향이 없다. U7 재실행에서 `loop_extract.output.tool_calls[].args` 키가 `query` 로 바뀌었는지 7건 세어 03-log 에 남기면 "스키마 열거 + 문장" 의 효과를 알 수 있다(P10 인계 재료).

## 5. 판정

**결과: 보류.**
근거: 코드는 위임 범위 (A)(B)(C) 안이고 원칙1·2·4·7·9 와 D16 결정 2·7·결정 J 를 지키며, 158/2125 passed·ruff·mypy 38=38·7/7·범위 밖 변경 0 을 직접 확인했다. 그러나 ① D16 "코드에서 지켜야 할 것" 1 과 01-plan B-3 (b) 근거 문장이 코드와 글자 그대로 어긋나 04-review 가 grep 으로 잡게 되고(R-U7F-1, 문서 보정만), ② 새 계약의 두 절("그 밖의 툴은 `person`"·"비면 `person` 폴백")이 테스트에 고정되지 않아 변이 2건이 살아남았다(R-U7F-2, h3 입력 3줄). 둘을 닫으면(코드 변경 없음, 재실행은 h3 1건 + 변이 2회) **통과** 로 바꾼다.

한 줄(1차): 코드는 맞고 범위 안이나, 카드 문구 1곳과 h3 입력 3건이 비어 있어 커밋 전 보류 — 제품 코드 수정 0.

---

## 6. 재리뷰 (2026-11-07 15:10) — [필수] 2건 닫힘 확인

### 6.1 본 것

| 항목 | 확인 |
|---|---|
| 제품 코드 무변경 | `git diff --stat -- app/agent/loop.py app/agent/propose.py` = 1차와 같은 `12 ++++++++++--` / `5 +++--`(+13/−4). §1 에 적은 `_query_mentions` 본문·스키마 `query`·프롬프트 문장 그대로 |
| `tests/test_agent_query_loop.py` h3 (574~597행) | 입력 3건 추가 — `add_event {person:"바", query:"사"}` · `search_person {query:"  ", person:"아"}` · `search_person {query:1, person:"자"}`, 기대 `["가","나","읽힘","다","라","바","아","자"]`. docstring 에 "V1·V2 변이 검출용(R-U7F-2)" |
| 같은 파일 `test_u7_real_llm_person_arg_shape` (600~631행) | R-U7F-3 반영 — `answer_source == "llm"`(부정 단언 → 실제 값), `mentions_dropped == 1`, `result.reply.splitlines()[-2] == QUERY_ONE_AT_A_TIME_HINT`(상수는 24행에서 import, 다른 테스트 540·571행과 같은 상수). §2 탐침 evidence 의 실제 값과 일치 |
| `docs/wiki/decisions/D16-query-turn.md` 38행 | "2026-11-07 보정 ③ … 코드 규칙 1 … 예외 1개 — `PROPOSAL_ARG_SCHEMA.properties.query`(string …; `additionalProperties: True` 라 금지가 풀린 것이 아니라 열거만 추가). 루프는 `search_person` 의 `query` 를 우선 읽고 문자열이 아니거나 비면 `person` 으로 폴백 … 결정 7·결정 2·결정 J 는 그대로" — 코드(`loop.py` 1248~1252행 `isinstance(primary, str) and primary.strip()`)와 일치 |
| `01-plan.md` 195행 | "보정(U7, 2026-11-07, R-U7F-1): `search_person` 은 `query` 우선, 문자열이 아니거나 비면 `person` 폴백(그 밖의 툴은 `person` 그대로) … `query` 속성 1개가 늘어 '스키마는 `intent` 하나만 늘어난다' 는 더 이상 성립하지 않는다 → D16 보정 ③. 프롬프트 (ii) 문장은 … 로 바뀌었다" — 코드·프롬프트 243~245행과 일치. 확정 줄(194행)은 그대로 |
| `03-log.md` 76행 (R-U7F-4) | "스키마에 `query` 가 열거되지 않았음 — `additionalProperties: True` 라 금지는 아니었음, R-U7F-4" 로 정정됨 |
| `tests.md` 188·198~199행 | h3 행에 추가 입력 3건, 변이 표 U7-M4(툴 이름 분기 제거)·U7-M5(공백 query 폴백 제거) 각 1 FAIL(h3) + evidence 경로 |
| 구현자 evidence `20261107-1508-u7fix2-mutation.txt` | 4구간 중 앞 2구간은 `2 failed`(u7 까지 실패 — 보고대로 `-k` 인용·`[-1]` 오단언 시점의 무효 실행), **뒤 2구간** `mut_v1_allquery`·`mut_v2_nostrip` 각 `1 failed, 1 passed`(h3 FAIL·u7 PASS) — 보고와 일치 |
| 변경 파일 목록 | 11파일 = 1차 9 + `D16-query-turn.md` + `01-plan.md`(둘 다 R-U7F-1 문서 보정). `app/api/`·`web/`·`app/settings.py` 여전히 0 |

### 6.2 직접 실행 (evidence `docs/wiki/packages/P5b-query-turn/evidence/`)

| # | 명령 | evidence | 결과 |
|---|---|---|---|
| 1 | 대상 5파일 pytest | `20261107-1510-verifier-u7fix2-pytest-target.txt` | **158 passed** |
| 2 | `pytest tests/ -q -rs`(테스트 파일 1개만 바뀌었지만 25초라 다시 돌렸다) | `20261107-1510-verifier-u7fix2-pytest-all.txt` | **2125 passed**, SKIPPED 0 |
| 3 | `ruff check app tests` | `20261107-1510-verifier-u7fix2-ruff.txt` | All checks passed |
| 4 | `scripts/mypy_check.py --run` | `20261107-1510-verifier-u7fix2-mypy.txt` | `[ok] 38=38` |
| 5 | 변이 4회(1차와 같은 플러그인 `vmut_*`, 대상 4파일 134건) | `20261107-1510-verifier-u7fix2-mutation.txt` | 아래 표 |

| 변이 | 1차 결과 | 재리뷰 결과 |
|---|---|---|
| 대조군 | 134 passed | 134 passed |
| V1 툴 이름 분기 제거 | **생존** | **1 failed**(h3: `'사'` 가 `'바'` 자리에 들어옴) — 검출 |
| V2 공백 `query` 채택 | **생존** | **1 failed**(h3: `'아'` 누락) — 검출 |
| V3 `person` 폴백 제거 | 2 failed | 2 failed(h3·u7) — 유지 |

### 6.3 소견 상태

| 소견 | 상태 |
|---|---|
| R-U7F-1 [필수] 카드·계획 문구 | **닫힘** — D16 38행·01-plan 195행, 코드와 일치 |
| R-U7F-2 [필수] h3 입력 3건 | **닫힘** — V1·V2 각 1 FAIL 직접 재현, tests.md U7-M4·M5 |
| R-U7F-3 [권고] "나" 부작용 기록 | 테스트 단언으로 **현재 동작 기록 완료**. U7 재실행 ① 에서 `reply` 관찰·코드 필터 여부는 여전히 사용자 결정(D16 결정 7) — 04-review §7 인계 |
| R-U7F-4 [권고] 03-log 원인 서술 | **닫힘** |
| R-U7F-5 [권고] `evidence/20261107-1455-u7fix-ruff.txt` 삭제 | **열림** — 파일이 아직 있다(`ls` 확인). 커밋 전 1파일 삭제 권고 유지 |
| R-U7F-6 [권고] U7 재실행에서 `query` 키 사용 7건 집계 | 열림(다음 단위) |

### 6.4 판정

**결과: 통과.** [필수] 2건은 제품 코드 변경 없이 닫혔고(코드 diff 는 1차와 동일), 닫힌 것을 158/2125 passed·ruff·mypy 38=38·변이 V1·V2 검출로 직접 확인했다. 카드(D16 보정 ③)·계획(B-3 (b) 보정)·코드·프롬프트 네 곳의 문장이 같은 규칙("`query` 우선, 비문자열·공백이면 `person`, 그 밖의 툴은 `person`")을 말한다. 열린 [권고]는 R-U7F-5(evidence 1파일 삭제)·R-U7F-6(U7 재실행 관찰)·R-U7F-3 후속(사용자 결정) — 커밋을 막지 않는다.

한 줄: h3 가 새 계약의 두 절을 고정하고(변이 V1·V2 검출) 카드·계획 문구가 코드와 맞아 통과 — 제품 코드 변경 0, 남은 것은 evidence 1파일 삭제와 U7 재실행 관찰.
