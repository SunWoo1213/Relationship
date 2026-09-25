# P5-loop · 완료 검토 (04-review)

날짜: 2026-09-25 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·다른 컨텍스트(L-002)

> 이 검토는 두 세션에 걸쳐 이루어졌다. 첫 세션(2026-09-25 19:36~19:44)이 증거 `20260925-1936-*`·`1939-*`·`1940-verify-impl.txt`·`1945-verifier-*`·`1950-verifier-*`·`2000-verifier-*`·`2005-verifier-registry.txt` 를 만든 뒤 이 문서를 쓰기 전에 끊겼고, 두 번째 세션(21:40~)이 그 증거를 다시 읽고 부족한 것만 추가 실행(`2145-verifier-remediation-closure.txt`·`2155-verify-impl.txt`)해 판정을 썼다. 판정 표 7행 명령은 개발 DB 에 행을 남기므로 다시 돌리지 않았다(첫 세션의 `2000-verifier-row7*`·`tmerge-below` 를 그대로 쓴다). 실제 LLM·임베딩 API 는 한 번도 부르지 않았다.

## 1. 기계 검증 출력 (그대로 붙인다)

명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/<ts>-verify-impl.txt` (이 문서를 쓴 뒤 실행 — 출력은 §1b). 첫 실행 `evidence/20260925-2155-verify-impl.txt` 는 FAIL 2(§2b 머리말 참조 — 04-review 표 형식), 문서 형식을 고친 뒤 재실행이 `evidence/20260925-2200-verify-impl.txt` 다.

### 1a. 이 문서를 쓰기 전 (첫 세션, `evidence/20260925-1945-verify-impl-port5433.txt` — FAIL 0 / WARN 1, WARN 은 이 문서 자체의 부재)

```
== verify-impl P5-loop  (20260925-1939) ==
........................................................................ [ 97%]
..................................                                       [100%]
1474 passed in 199.23s (0:03:19)
PASS  pytest 통과 → evidence/20260925-1939-pytest.txt
PASS  compileall 통과 → evidence/20260925-1939-lint.txt
PASS  태그 P5-loop 커밋 18 건 → evidence/20260925-1939-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D12
PASS  커밋에 태그 존재: D13
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: FIX-004
PASS  커밋에 태그 존재: R6
PASS  커밋에 태그 존재: R7
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P5-loop 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=1 → evidence/20260925-1939-summary.txt ==
EXIT:0
```

첫 실행(`evidence/20260925-1940-verify-impl.txt`, 19:36)은 포트를 넘기지 않아 5432(다른 프로젝트 DB)에 붙었고 DB 테스트 292건이 skip 됐다(`1182 passed, 292 skipped`, WARN 2). 그 결과는 증거로 쓰지 않는다 — 위 5433 재실행이 유효한 출력이다(skip 0).

### 1b. 이 문서를 쓴 뒤 — 재실행 (`evidence/20260925-2200-verify-impl.txt`)

```
== verify-impl P5-loop  (20260925-2153) ==
........................................................................ [ 97%]
..................................                                       [100%]
1474 passed in 209.00s (0:03:29)
PASS  pytest 통과 → evidence/20260925-2153-pytest.txt
PASS  compileall 통과 → evidence/20260925-2153-lint.txt
PASS  태그 P5-loop 커밋 18 건 → evidence/20260925-2153-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D12
PASS  커밋에 태그 존재: D13
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: FIX-004
PASS  커밋에 태그 존재: R6
PASS  커밋에 태그 존재: R7
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  에이전트 루프(인식→해석→기록→� ← evidence/20260925-2000-verifier-row7a-se
PASS  증거 확인:  발화 → — 입력은 `POST /chat` 본문의 � ← evidence/20260925-2000-verifier-chat-pyt
PASS  증거 확인:  툴 선택 — LLM 이 제안(`loop_extract`)하� ← evidence/20260925-2000-verifier-row22-se
PASS  증거 확인:  저장 — 같은 요청 안에서 `events`(또� ← evidence/20260925-2000-verifier-chat-pyt
PASS  증거 확인:  응답 — `ChatOut.reply` 가 비어 있지 않� ← evidence/20260925-2000-verifier-chat-pyt
PASS  증거 확인:  API 한 흐름으로 동작 — 위 넷이 HTTP � ← evidence/20260925-2000-verifier-chat-pyt
PASS  증거 확인:  `POST /answers/{question_id}`로 루프 재개 � ← evidence/20260925-2000-verifier-resume-p
PASS  증거 확인:  의존: P4b 게이트 통과  ← evidence/20260925-1852-U8-row17-dependen
PASS  증거 확인:  R6 (이 패키지가 닫는다고 선언) — 루 ← evidence/20260925-1945-verifier-greps.tx
PASS  증거 확인:  R7 (이 패키지가 닫는다고 선언) — ask ← evidence/20260925-2000-verifier-tmerge-b
PASS  registry 에 P5-loop 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260925-2153-summary.txt ==
EXIT:0
```

(스크립트 내부 타임스탬프는 `2153` — 그 실행이 만든 `2153-pytest.txt`·`2153-lint.txt`·`2153-commits.txt`·`2153-summary.txt` 가 tee 파일 `2200-verify-impl.txt` 와 같은 실행이다. 이 세션에서 전체 회귀는 두 번 돌았고(2148·2153) 둘 다 `1474 passed`, skip 0.) FAIL 0 이므로 `findings.py` 로 올릴 소견은 없다. 05-remediation 의 `F-14f3ef`(04-review 부재 WARN)는 이 출력으로 해소했다 — 열린 소견 0.

## 2. 수용 기준 대조

backlog P5 항목 한 줄(글자 그대로): "**에이전트 루프(인식→해석→기록→응답) + ask_user 재개** / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개". 01-plan "수용 기준 → 해석" 절의 여덟 조각으로 나눠 판정한다. 증거 열은 evidence 파일·커밋 해시·경로뿐이다.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 에이전트 루프(인식→해석→기록→응답) — `run_turn()` 한 턴의 `agent_traces` 에 `loop_extract`·`loop_gate`·`er_resolve`·`loop_record`·`loop_turn` 이 전부 나타난다 | evidence/20260925-2000-verifier-row7a-seed0.txt, evidence/20260925-1852-U8-row7b-seed1.txt, evidence/20260925-2000-verifier-row22-seed1-rejects1.txt | 통과 — 세 실행 모두 줄 1 에 루프 step 5종 + `er_resolve` + `tool_call` 행이 순서대로 있다 |
| 발화 → — 입력은 `POST /chat` 본문의 발화 문자열 하나 | evidence/20260925-2000-verifier-chat-pytest.txt, app/api/schemas.py | 통과 — `ChatIn` 은 `utterance: str` 한 필드, `test_chat_stores_event_and_replies_in_one_request` 가 요청 1건으로 끝난다 |
| 툴 선택 — LLM 이 제안(`loop_extract`)하고 코드가 거른다(`loop_gate` 통과·거부·사유), 실행은 `loop_record.executed[].trace_id` 로 `tool_call` 행에 이어지고 U1 등식이 성립한다 | evidence/20260925-2000-verifier-row22-seed1-rejects1.txt, evidence/20260925-2000-verifier-row7a-seed0.txt, evidence/20260925-1950-verifier-gate-pytest.txt | 통과 — 22행: `rejected` 4종(`person_id_from_llm`·`not_callable_by_llm`·`unknown_tool`·`bad_args`)이 trace 에 남고 `executed[].trace_id` 가 가리키는 행 = `[('tool_call','add_event')]` 1건, 등식 `True`. 7행(가): `hint_only` 1·`pending_calls` 1·`executed` 0, 등식 `True` |
| 저장 — 같은 요청 안에서 `events`(또는 `schedules`·`person_aliases`) 행이 실제로 는다 | evidence/20260925-2000-verifier-chat-pytest.txt, evidence/20260925-1852-U8-row7b-seed1.txt, evidence/20260925-2000-verifier-row22-seed1-rejects1.txt | 통과 — 시드 인물 merge 턴에서 `events_of_seed_person= 1`, `executed=[{0,add_event,trace_id}]`; HTTP 테스트가 요청 전후 행 수를 비교한다 |
| 응답 — `ChatOut.reply` 가 비어 있지 않고, 되묻기 턴이면 `question_id`·`options` 가 함께 온다 | evidence/20260925-2000-verifier-chat-pytest.txt, evidence/20260925-2000-verifier-row7a-seed0.txt | 통과 — `test_chat_new_person_returns_pending_question_id` 통과, 7행(가) 질문 `["new_person", [태그 5 + "아니요"]]` |
| API 한 흐름으로 동작 — 위 넷이 HTTP 요청 1건 안에서 끝난다(중간 클라이언트 왕복 없음) | evidence/20260925-2000-verifier-chat-pytest.txt, evidence/20260925-1852-U8-row9-no_sync_wait.txt, d5c8ec9 | 통과(TestClient 기준) — 9건 통과, `time.sleep`/`asyncio.sleep`/`while True` 0건. **판정 표 8행(uvicorn + curl, 실 공급자)은 미실행** — 01-plan 이 "수동 왕복(사용자)"로 지정했고 실제 LLM 키가 필요하다. §6-1 |
| `POST /answers/{question_id}`로 루프 재개 — 요청 하나로 답 저장 + 저장된 `context` 로 해석·기록 + 결과가 응답에 담긴다 | evidence/20260925-2000-verifier-resume-pytest.txt, evidence/20260925-1852-U8-row4-resume.txt, 7df3ada | 통과 — 11건 통과: 왕복 end-to-end 로 `persons`·`events` 증가, 두 번째 재개 409, 만료 409, identity 답 뒤 `schedule` 질문, `schedule` 답 → 사전 조회 시각 저장, "모르겠어요" → 0회 |
| 의존: P4b 게이트 통과 | evidence/20260925-1852-U8-row17-dependency-gate.txt, docs/wiki/packages/P4b-er-redesign/04-review.md | 통과 — `144:결과: 완료` |
| R6 (이 패키지가 닫는다고 선언) — 루프가 확인 없이 `create_person` 을 부르지 않는다 | evidence/20260925-1945-verifier-greps.txt, evidence/20260925-2000-verifier-row7a-seed0.txt, evidence/20260925-2000-verifier-resume-pytest.txt, app/agent/loop.py | 통과 — `create_person(` 호출은 `app/agent/loop.py:1207` 한 곳(재개 `new_person` 답 처리, 앞줄 `ctx.confirmed_question_id = question_id`), 빈 DB 턴에서 `persons_with_tag= 0`, `new_person_reject_creates_nothing`·`create_person_only_targets_context_mention` 통과 |
| R7 (이 패키지가 닫는다고 선언) — ask_user 는 `{question_id, status:"pending"}` 을 돌려주고 턴을 끝내며, 턴 N+1 은 저장된 context 로 재개된다 | evidence/20260925-2000-verifier-tmerge-below-no-automerge.txt, evidence/20260925-2000-verifier-resume-pytest.txt, evidence/20260925-1852-U8-row25-pending_survives.txt | 통과 — 되묻기 턴 `stop_reason= ask_user`·`executed=[]`·`pending_calls` 저장; 미답변 질문이 있는 세션에 새 발화 → 200 + 기존 질문 pending 유지(D2 9행) |

## 2b. 판정 표 28행 전수 대조 (U8 요약 `evidence/20260925-1852-U8-summary.md` 를 verifier 가 재실행·재확인한 결과)

> 2단계 제목으로 둔 이유: `verify-impl.sh` 가 "## 2. 수용 기준 대조" 절의 표만 증거 열 검사 대상으로 삼는다. 이 표는 수용 기준이 아니라 판정 표 행별 대조라 절을 분리했다(첫 실행 `evidence/20260925-2155-verify-impl.txt` 가 이 표의 머리행을 증거로 읽어 FAIL 2 를 냈다 — 문서 형식 문제, 코드·계획 문제 아님).

| 판정 표 행 | verifier 증거 | 판정 |
|---|---|---|
| 1 전체 테스트 1474 passed·skip 0 | evidence/20260925-1939-pytest.txt | 일치 |
| 2 네트워크 0 서브셋 | evidence/20260925-2000-verifier-chat-pytest.txt, evidence/20260925-2000-verifier-loop-pytest.txt, evidence/20260925-2000-verifier-resume-pytest.txt, evidence/20260925-1950-verifier-gate-pytest.txt | 일치(파일명 표기 차이 — 계획 `test_agent_resume.py`, 실제 `tests/test_api_answers_resume.py`, §6-3) |
| 3 한 흐름 `-k "one_flow or end_to_end"` | evidence/20260925-2000-verifier-chat-pytest.txt | 기능 통과, `-k` 문자열 불일치(실제 이름 `test_chat_stores_event_and_replies_in_one_request`, §6-3) |
| 4 재개 | evidence/20260925-2000-verifier-resume-pytest.txt | 일치(파일명 표기 차이) |
| 5a `create_person(` 1줄 + 앞줄 `confirmed_question_id` | evidence/20260925-1945-verifier-greps.txt | 일치 |
| 5b `update_person(` 뒤 `display_name` 0건, 호출 2곳(`loop.py:771`, `loop.py:1188`) | evidence/20260925-1945-verifier-greps.txt | 일치 |
| 6 `T_merge`/`T_new`/`confidence` 0건 | evidence/20260925-1945-verifier-greps.txt, evidence/20260925-2000-verifier-loop-pytest.txt | 일치(소스 스캔 테스트 `test_loop_module_source_never_mentions_thresholds_or_confidence_literal` 도 통과) |
| 7(가) 빈 DB | evidence/20260925-2000-verifier-row7a-seed0.txt | 줄 1~4 전부 기대와 일치, `persons_with_tag= 0` |
| 7(나) 시드 DB | evidence/20260925-1852-U8-row7b-seed1.txt, evidence/20260925-2000-verifier-row22-seed1-rejects1.txt | 일치(`aliases_of_seed_person= 1`·`events_of_seed_person= 1`, `stop_reason= None`) |
| 8 수동 curl(사용자) | docs/wiki/packages/P5-loop/01-plan.md (8행 명령 정의 — 실행 증거 없음) | **미실행**(§6-1, 사용자 몫·실 LLM 키 필요) |
| 9 동기 대기 0건 | evidence/20260925-1945-verifier-greps.txt | 일치 |
| 10 허용 파일 | evidence/20260925-1945-verifier-greps.txt | 일치 — `app/agent/*` 6 + `app/api/{deps,routes,schemas}.py` + `app/settings.py`, `app/er`·`app/tools`·`app/db`·`app/main.py` 무변경 |
| 11 `alembic check` | evidence/20260925-2000-verifier-alembic-check.txt | 일치 |
| 12 `tools_check.py` 7/7 | evidence/20260925-1945-verifier-greps.txt | 일치 |
| 13 ER 회귀 3종 | evidence/20260925-2000-verifier-er-regression.txt | 일치 |
| 14 data/·reports/ 무변경 | evidence/20260925-1945-verifier-greps.txt | 일치 |
| 15 비밀 미노출 | evidence/20260925-1945-verifier-greps.txt | 일치 — 매치는 전부 `*_MODEL` 이름·docstring, 값과 함께 찍는 코드 0건 |
| 16 registry | evidence/20260925-2005-verifier-registry.txt, evidence/20260925-2145-verifier-remediation-closure.txt | 일치 — 새 행 13(모듈 6·엔드포인트 1·테스트 6), 기존 6행 비고 확장 |
| 17 P4b 완료 | evidence/20260925-1852-U8-row17-dependency-gate.txt | 일치 |
| 18 상담성 응답 없음 | evidence/20260925-2000-verifier-loop-pytest.txt | 통과(테스트의 한계는 §3·§6-5) |
| 19 `person_id_from_llm` | evidence/20260925-1950-verifier-gate-pytest.txt | 일치 — 스파이 `calls == []` 단언 확인 |
| 20 화이트리스트 | evidence/20260925-1950-verifier-gate-pytest.txt | 일치 |
| 21 `bad_args` 3케이스 + R-23 `None` 통과 | evidence/20260925-1950-verifier-gate-pytest.txt | 일치 |
| 22 거부 사유 trace | evidence/20260925-2000-verifier-row22-seed1-rejects1.txt | 일치 |
| 23 `PendingQuestion` 직접 사용 0건 | evidence/20260925-1950-verifier-greps-2.txt | 일치 — `-w` 단어 단위 매치는 docstring 5줄뿐, ORM import 0건, `.context =` 0건 |
| 24 `resume_size` | evidence/20260925-2000-verifier-loop-pytest.txt | 기능 통과, `-k` 문자열 불일치(실제 `resume_byte_limit`·`resume_within_byte_limit`, §6-3) |
| 25 대기 질문 유지 | evidence/20260925-2000-verifier-chat-pytest.txt | 일치 |
| 26 DB 예외 미삼킴 | evidence/20260925-2000-verifier-chat-pytest.txt | 일치 — `status_code != 200` 과 예외 문구 미노출 단언 확인 |
| 27 재개 별칭 임베딩 | evidence/20260925-2000-verifier-resume-pytest.txt | 일치 |
| 28 `new_person` 부정 답 → `create_person` 0회 | evidence/20260925-2000-verifier-resume-pytest.txt | 일치 — `persons` 행 수 불변·`stored.persons == 0` 단언 |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

| 케이스 | 명령 | 증거 |
|--------|------|------|
| **`T_merge` 미만이면 자동 병합하지 않는다(원칙1·2)** — 시드 인물 있음 + LLM 자기보고 0.5 → 확신도 미달 | `SEED=1 REJECTS=0 JUDGE_SCORE=0.5 python row7.py` (7행 명령 원문 + verifier 변수 하나) | evidence/20260925-2000-verifier-tmerge-below-no-automerge.txt — `identity` 질문(`["김민수", "아니요, 다른 사람이에요"]`), `executed=[]`, `aliases_of_seed_person= 1`(별칭 누적 없음), `events_of_seed_person= 0`, `stop_reason= ask_user` |
| 확신도 이상이면 merge 되고 `add_event` 가 실행된다(대조군) | `SEED=1 REJECTS=1` | evidence/20260925-2000-verifier-row22-seed1-rejects1.txt — `judge_score= 0.95`, `events_of_seed_person= 1` |
| 빈 DB 에서는 `new_person` 되묻기로 끝나고 `create_person` 0회 | `SEED=0 REJECTS=0` | evidence/20260925-2000-verifier-row7a-seed0.txt — `persons_with_tag= 0`, `hint_only` 버킷만 |
| LLM 이 준 `person_id` 는 실행되지 않는다(L(iii) 핵심 방어) | `pytest tests/test_agent_gate.py -k person_id_from_llm` | evidence/20260925-1950-verifier-gate-pytest.txt — 2 passed, 스파이 `calls == []` |
| 툴 7종 밖 이름·`ask_user`/`search_person`/`get_briefing` 제안 거부 | `-k "unknown_tool or not_callable"` | evidence/20260925-1950-verifier-gate-pytest.txt — 4 passed |
| 인자 스키마 위반(필수 누락·미지 키·타입·`raw_utterance` 제안) 거부, `display_name` → `needs_confirmation`, `create_person` → `hint_only`·호출 0회 | `-k "bad_args or needs_confirmation or hint_only"` | evidence/20260925-1950-verifier-gate-pytest.txt — 18 passed |
| 게이트는 판정과 무관하게 어떤 툴도 부르지 않는다 | `-k never_calls` | evidence/20260925-1950-verifier-gate-pytest.txt — `test_gate_never_calls_any_tool_regardless_of_verdict` 통과 |
| 거부 사유가 `loop_gate` trace 에 남는다 | 22행 | evidence/20260925-2000-verifier-row22-seed1-rejects1.txt |
| 루프가 ER 없이 `create_person` 을 부르지 않는다(D1) | `grep -B1 "create_person("` | evidence/20260925-1945-verifier-greps.txt — 1줄, `loop.py:1207`, 앞줄 `ctx.confirmed_question_id = question_id` |
| `create_person` 은 `context.mention` 에만 쓰인다(R6 대상 바인딩) | `-k only_targets_context_mention` | evidence/20260925-2000-verifier-resume-pytest.txt — 스파이 kwargs `display_name == "민수"`·`aliases == ["민수"]` |
| `new_person` 부정 답 → `create_person` 0회 | `-k new_person_reject` | evidence/20260925-2000-verifier-resume-pytest.txt |
| 같은 `question_id` 두 번째 재개 409, 만료 답 409(1회 소비, 결정 J) | `-k "second_submission or expired"` | evidence/20260925-2000-verifier-resume-pytest.txt |
| 루프가 임계치·확신도를 읽지 않는다(원칙2·4) | `grep T_merge\|t_merge\|T_new\|t_new\|confidence app/agent/` | evidence/20260925-1945-verifier-greps.txt — 0건 |
| 동기 대기 없음(D2) | `grep time.sleep\|asyncio.sleep\|while True` | evidence/20260925-1945-verifier-greps.txt — 0건 |
| 상담성 응답 없음(원칙7) | `-k no_counseling` | evidence/20260925-2000-verifier-loop-pytest.txt — 감정 발화에 "새로 기억한 것이 없어요" 템플릿만. `app/agent/respond.py` 는 `PendingQuestionOut` 만 import 하고 LLM 호출 경로가 없다(구조적 보장) |
| `app/agent/` 가 `PendingQuestion` ORM 을 직접 다루지 않는다 | `grep -rnw PendingQuestion\|flag_modified` + `grep "\.context *="` | evidence/20260925-1950-verifier-greps-2.txt — import 0건, 대입 0건 |
| `app/er`·`app/tools`·`app/db`·`app/main.py`·`data/`·`reports/` 무변경 | `git diff --stat 1227026..HEAD -- app/er app/tools app/db app/main.py`, `-- data/ reports/` | evidence/20260925-1945-verifier-greps.txt — 둘 다 빈 출력. `app/er/judge.py` 는 P5-loop 커밋에 없다(evidence/20260925-2145-verifier-remediation-closure.txt) |
| DB 예외는 200 으로 내리지 않고 상세를 응답에 싣지 않는다 | `-k db_error` | evidence/20260925-2000-verifier-chat-pytest.txt — `status_code != 200`·`"simulated-db-failure-detail" not in resp.text` |
| 언급 2 중 둘째 해석이 실패하면 첫째 merge 의 별칭까지 되돌린다(결정 G "저장 0") | `-k partial_rollback` | evidence/20260925-2000-verifier-chat-pytest.txt |
| 재개 데이터 크기 상한 초과 시 `held_drafts` 만 버리고 `pending_calls` 는 유지 | `-k byte_limit` | evidence/20260925-2000-verifier-loop-pytest.txt — 2 passed |
| 미커밋 제품 코드 없음 | `git status --porcelain -- app tests scripts alembic` | 빈 출력(이 세션 21:42 실행). 미커밋은 위키·evidence 뿐(HANDOFF·journal·05-remediation·evidence/*) |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)

- **아직 바꾸지 않았다** — review-index 14·15행은 P2 시점 문구("재개 흐름은 P5-loop")가 그대로다. 메인 세션이 완료 승인 뒤 다음 해시로 갱신하라(verifier 는 카드를 고치지 않는다):
  - **R6** 신규 인물 자동등록 vs 확인형 → `구현완료(f318d58, 8162e09, 8ecf75c, 7df3ada)` — `8ecf75c`(U3): LLM 의 `create_person` 제안은 `hint_only` 버킷으로만 통과하고 실행되지 않는다. `7df3ada`(U7): `create_person` 호출 경로는 answered `new_person` 질문 + 태그 옵션(긍정) 답 + `ctx.confirmed_question_id` 세팅 뒤 `context.mention` 하나에만, 부정 답이면 0회. 판정 표 5a·28행, §3.
  - **R7** ask_user 동기 반환 불가 → `구현완료(8162e09, 4d5817e, d5c8ec9, 7df3ada)` — `d5c8ec9`(U6): `POST /chat` 은 되묻기가 나면 `pending_question{question_id,status:"pending",kind,question,options}` 를 담아 그 턴을 끝낸다(sleep/poll 0건). `7df3ada`(U7): `POST /answers/{id}` 가 답 저장 뒤 저장된 `context["resume"]` 로 해석·기록을 이어 간다(S3.4 턴 N+1 뒤 절반).

## 5. registry.md 에 올린 산출물

- 새 행 13(evidence/20260925-2005-verifier-registry.txt 161~173행): 모듈 6(`app/agent/types.py`·`__init__.py`·`propose.py`·`gate.py`·`loop.py`·`respond.py`), 엔드포인트 1(`POST /chat`, `d5c8ec9`), 테스트 6(`tests/test_agent_types.py`·`test_agent_propose.py`·`test_agent_gate.py`·`test_agent_loop.py`·`test_api_chat.py`·`test_api_answers_resume.py`). 계획(U8)은 "테스트 5" 였고 실제는 6 — `test_agent_types.py` 가 더해진 것으로 누락이 아니라 초과 등록이다.
- 기존 행 비고 확장 6(새 행 아님, evidence/20260925-2145-verifier-remediation-closure.txt): `app/api/routes.py`(65행)·`schemas.py`(66행)·`deps.py`(64행)·`app/settings.py`(53행)·`tests/test_api.py`(76행)·`README.md`(33행). 각 비고에 `P5-loop` 와 U 커밋 해시가 있고, 경로당 행 수는 1(`routes.py` 만 2 — 기존 행 + 계획된 `POST /chat` 엔드포인트 행).
- `app/er/judge.py` 는 P3-er 행 1개 그대로이고 P5-loop 소속 행·비고가 생기지 않았다(F-e93529 닫힘 조건). `inspect.signa` 를 경로로 가진 행은 0(F-b38c2c 닫힘 조건).
- 05-remediation 의 [권고] 8건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`·`F-b38c2c`)은 위 증거로 이 검토에서 **해소** 처리했다. `F-14f3ef`(04-review 부재)는 §1b 재실행이 WARN 을 내지 않으면 해소.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

열린 [필수] 소견은 없다. 아래는 완료 판정을 막지 않지만 사용자가 알고 결정해야 하는 것들이다.

1. **판정 표 8행(실 공급자 curl 왕복) 미실행 — 사용자 몫.** 이 검토의 "API 한 흐름" 판정은 `TestClient`(프로세스 내 ASGI) + `FakeProposer`·`FakeJudge`·스텁 임베더 기준이다. 실제 uvicorn + 실제 LLM(`proposer_from_env()`) + 실제 임베딩 경로는 한 번도 돌지 않았다. 01-plan 8행 명령대로 사용자가 실행하고 두 응답 전문을 `evidence/` 에 남겨야 dev→main 승격(L-001 "실서버에서 검증한 뒤")의 근거가 된다. `②` 요청에 `X-Session-Id` 를 넣지 않는다(P2 결정 12).
2. **계획한 산출물 하나가 빠졌다 — `docs/user-setup/` 카드 갱신.** 01-plan 범위 37행·산출물 73행·U8 95행이 "`docs/user-setup/` 의 로컬 재현 절차(기존 카드 갱신)" 를 지시했지만 패키지 커밋(`24feebd..f0d3e26`)에 `docs/user-setup/` 변경이 없고 카드 어디에도 `/chat`·`P5-loop` 언급이 0건이다(이 세션 grep). 재현 절차 자체는 `docs/RUNNING.md` 122행에 있으므로 기능 결손은 아니다. **사용자 결정**: (a) RUNNING.md 로 갈음하고 01-plan 표기를 정정, 또는 (b) 완료 커밋에 `docs/user-setup/03-er-smoke.md`(또는 `04-local-db.md`)에 `/chat`·`/answers` 스모크 한 절을 이어 붙인다(새 카드 신설 금지).
3. **01-plan 판정 표의 표기 오류(코드 결함 아님, 문서 정정).** 2·4·27·28행 `tests/test_agent_resume.py` → 실제 `tests/test_api_answers_resume.py`; 3행 `-k "one_flow or end_to_end"` → 실제 `test_chat_stores_event_and_replies_in_one_request`; 24행 `-k "resume_size"` → 실제 `resume_byte_limit`·`resume_within_byte_limit`. 그대로 두면 판정 표 명령이 `exit 5`(0건 선택)로 끝나 재현이 깨진다. 완료 커밋에서 01-plan 을 정정하거나 03-log 에 "표기 차이" 로 남긴다(U7 03-log 가 파일명 차이는 이미 적었다).
4. **03-log U8 항목 해시가 `pending`** (03-log 69행) → `f0d3e26`. 완료 커밋에서 채운다.
5. **상담성 응답 테스트의 범위가 좁다(원칙7).** `test_run_turn_no_counseling_reply_for_emotional_utterance` 는 제안이 0건인 감정 발화만 검사한다(응답 = "새로 기억한 것이 없어요"). 감정 발화 + 이벤트 제안이 함께 있는 케이스는 없다. 다만 `app/agent/respond.py` 는 템플릿 조립만 하고 LLM 을 부르지 않으므로(import 는 `PendingQuestionOut` 뿐) 상담 문장이 생길 경로가 코드에 없다 — 위험은 낮고, P10 이 실 발화 trace 로 잴 때 `reply` 를 함께 보면 된다.
6. **하네스 부채(이 패키지 밖)**: `verify-plan.sh` 산출물 토큰 스캔 오탐(F-e93529·F-b38c2c 계열, 02-plan-verify R-19) — 하네스 FIX 후보. `findings.py` 가 만든 소견 6건에 빈 "해결 단계" 표가 **한 번 더** 붙어 있다(05-remediation F-8e3e74 등, 채운 표 아래 빈 표) — 문서 잡음이며 판정에 영향 없음.
7. **개발 DB 에 남은 확인 행.** 판정 표 7·22행·부정 케이스 실행이 `judge-row7-*`·`verifier-row7-*` 태그의 `persons`·`person_aliases`·`events`·`pending_questions`·`agent_traces` 행을 로컬 DB(5433)에 남겼다. 원칙8·security 에 따라 지우지 않았다. FIX-004 이후 테스트는 전역 개수 단언을 쓰지 않으므로 회귀에는 영향이 없다(1474 passed 가 그 뒤 실행이다).
8. **다중 사용자 격리 부재(F-fbaaae)** — 계획대로 문서 명시만 했다. P9 배포 전 부채(backlog 리스크 로그).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

- **`POST /chat` 계약(P8-frontend 가 그대로 쓴다)**: 요청 `ChatIn{utterance: str(min 1)}` + 헤더 `X-Session-Id`(선택, `^[A-Za-z0-9._-]{1,128}$`, 없으면 서버가 uuid4 발급, 위반 422). 응답 `ChatOut{reply, session_id, stored{persons,events,schedules}, pending_question{question_id,status,kind,question,options}|null, stop_reason|null, trace_ids[]}`. `POST /answers/{question_id}` 응답 `AnswerOut{question_id, status, reply, stored, pending_question|null, stop_reason, trace_ids}` — 재개 중 새 질문이 나면 `pending_question` 에 **새** `question_id` 가 온다(첫 질문은 answered 유지). 확인 칩 = `pending_question.options` 그대로(`new_person` 은 태그 5 + "아니요", `identity` 는 ER 원본, `schedule` 은 후보 시각 2~3 + "모르겠어요").
- **오류 규약**: `LoopError`·공급자 오류(`JudgeUnavailable`)·`ToolError` 는 200 + `stored` 전부 0 + `trace_ids=[loop_error id]` + `stop_reason=None`; `SQLAlchemyError` 는 그대로 5xx. 프론트는 200 이어도 `stored` 와 `pending_question` 을 봐야 한다.
- **설정값(`app/settings.py`)**: `LOOP_MAX_MENTIONS=5`·`LOOP_MAX_EVENTS=5`·`LOOP_MAX_SCHEDULES=3`·`LOOP_MAX_PROPOSALS=13`(합)·`LOOP_MAX_RESUME_BYTES=8192`(U1 초기 추정치, 실측 없음). 제안 단계 타임아웃·재시도·모델은 ER 판정 설정(`ER_JUDGE_TIMEOUT`·`ER_JUDGE_MAX_RETRIES`·`*_MODEL`)을 공유한다.
- **P6-memory**: 승격 훅은 `app/agent/loop.py` 의 `_record_impl`(기록 단계, `loop_record` 한 행) 뒤에 건다. `add_event` 는 `raw_utterance` 를 발화 원문 그대로 받는다(LLM 값이 아니라 루프 주입).
- **P6-briefing**: 루프는 `get_briefing` 을 부르지 않는다. 트리거 자리는 루프 밖 별도 엔드포인트다.
- **P7-push**: 알림 트리거 후보 = `pending_questions` 행 생성 시점(ER 의 `ask_user` `tool_call` 행 + 루프의 `loop_turn` `stop_reason="ask_user"`).
- **P10-final-eval**: 툴 호출 정확도 분모 = `loop_extract.output.tool_calls` 수, 분자 = 라벨 일치 제안 수, 거부율 = `loop_gate.output.rejected[]` 사유별. `ask_user_rate_by_kind` 의 `schedule` 분모가 이제 생긴다(결정 K). 위 6-5 의 `reply` 검사도 같은 trace 로 한다.
- **주의(R-15)**: 임베딩 키가 없는 환경에서 `build_chat_ctx`/`build_ctx` 는 `embedder=None` 이고 ER 은 `embedding_skipped` 로 돈다 — 그때 새 별칭의 `embedding` 이 NULL 로 남아 이후 다른 표기 검색에서 조용히 미검출된다. 실서버 스모크(§6-1) 때 `person_aliases.embedding IS NOT NULL` 을 한 번 확인하라.

결과: 완료
승인: 사용자 (2026-09-25) — 완료 승인. §6-2 `docs/user-setup/` 갱신은 `docs/RUNNING.md` 로 갈음(사용자 결정), 01-plan 표기 정정. 판정 표 8행(실 공급자 curl)은 main 승격 전 사용자 실행 권고로 남긴다.
