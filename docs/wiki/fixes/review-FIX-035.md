# review-FIX-035 · identity 거절 → new_person 후속 질문 · 후보 1명 문구 — 커밋 전 리뷰

검토자: verifier (fable) · 2026-10-16 · 기준 HEAD `c4fbd2f` + 작업 트리 미커밋 diff(`app/agent/loop.py` +110/-3 · `app/er/pipeline.py` +5/-1 · `tests/test_api_answers_resume.py` +145 · `tests/test_er_pipeline.py` +21 · registry · P5-loop 03-log) · Refs: FIX-035 P5-loop P8-frontend D1 D10 S3.3 S3.4 원칙1 원칙2 원칙4 원칙9 FIX-033

**결과: 보류 — [필수] 1건(R-35-1), [권고] 5건(R-35-2~6).** 수정안 (가)·(나)의 동작 자체는 코드·테스트·변이로 전부 확인됐다(§3.1) — 거절 뒤 자동 생성·자동 병합은 없고(원칙1·D1), 후속 질문은 S3.4 비동기 모델 그대로이며(§3.2), 내가 돌린 변이 12종 중 11종이 검출됐다(§2 #3). 그러나 **`app/agent/loop.py` 가 `AgentTrace` ORM 과 `flag_modified` 를 직접 쓰게 되어 P5-loop 04-review 가 증거로 닫은 판정 표 23행 부정 grep(`grep -rnE "PendingQuestion|flag_modified|\.context *=" app/agent/` → 0건)이 깨졌고, FIX-035.md 는 이 불변식 변경을 적지 않았다**(R-35-1). 몇 줄짜리 이동(헬퍼를 `app/tools/context.py` 로)으로 닫히거나, 사용자가 불변식 완화를 결정하고 기록하면 닫힌다. 코드·테스트·계획·카드는 고치지 않았고 `FIX-035.md` 의 `검증:` 줄만 보류로 썼다.

## 1. 본 것

- `docs/wiki/fixes/FIX-035.md` 증상·원인·수정안 (가)(나)·회귀 테스트 목록·기획서 정합성·`계획 점검: 통과`·`승인: 사용자 (2026-10-15)`.
- `git diff` 전체(위 6파일 + HANDOFF·journal). `app/agent/loop.py` 신규 `_followup_new_person_turn()`(1169~1253행)·`resume_turn()` identity 분기(1430~1450행)·`_extend_for_ask`/`_extend_new_person_payload`(440~495행)·`_log_resume_entry`(1156~1166행)·`_drop_calls_for_mention`(1315~1320행)·`resume_turn` docstring(1330~1400행). `app/er/pipeline.py` `_build_ask_payload`(165~240행)·`apply_resolution` trace 부분 갱신 절(F-93f063, 420~440행)·모듈 상수(108~109행). `app/tools/questions.py` `ask_user`(184~233행, `_validate_context` 152~177행). `app/tools/persons.py` `create_person` 확인 검사(303~320행). `tests/test_agent_loop.py:225` 금지 토큰 테스트.
- 카드: D1(`create_person` 호출 경로는 반드시 answered pending_question 을 거친다) · D10 · S3.3 17행 · S3.4 7~13행 · P5-loop 01-plan U7(94행)·판정 표 23행(143행)·367행 · 04-review 126·152행 · 03-log U7 항목 (4).
- 구현자 증거 6개 `fixes/evidence/20261015-2031-FIX-035-*.txt`·`20261015-2032-FIX-035-*.txt`. **2031 전체 회귀는 `1 failed, 1950 passed`** — `test_loop_module_source_never_mentions_thresholds_or_confidence_literal` 가 `confidence` 토큰을 잡았고, 2032 재실행에서 1951 passed. 즉 첫 구현은 후속 질문 context 에 `confidence_breakdown` 을 넣었다가 이 테스트 때문에 뺐다(R-35-4).
- `HANDOFF.md`·`journal.md` diff 는 메인 세션 기록이라 판정 대상에서 뺐다.

## 2. 내가 직접 실행한 것 (구현자 수치를 옮기지 않았다 — 전부 `save_evidence.py` 통로, 출력 전문)

| # | 확인 | 결과 | 증거 |
|---|---|---|---|
| 1 | 전체 회귀 `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs -q` | **1951 passed, skip 0**(skip 요약 줄 없음), 26.05s, exit 0 | `fixes/evidence/20261016-1719-verifier-FIX-035-regression.txt` |
| 2 | `.venv/bin/ruff check app tests` | All checks passed, exit 0 | `…-1720-verifier-FIX-035-ruff.txt` |
| 3 | 변이 12종 — 스크래치패드 사본(`app/`·`tests/`·`alembic/` rsync, `loop.__file__` 이 사본을 가리킴 확인) 에서 `mut.py` 가 치환→pytest(두 테스트 파일 36건)→원복. 저장소 무수정 | 대조군 36 passed · **M1~M7·M9~M12 검출(11종)** · **M8 생존**(아래) · 원복 확인 "사본 2파일 원문과 동일" | `…-1722-verifier-FIX-035-mutations.txt` |
| 4 | 작업 트리 무변경 확인: 리뷰 시작·종료 `git diff --stat` | 둘 다 `8 files changed, 284 insertions(+), 8 deletions(-)` 동일. untracked 는 FIX-035.md·구현자 증거 6·내 증거 3 뿐 | 이 문서 §2 (명령 출력은 세션 로그) |
| 5 | 판정 표 23행 부정 grep `grep -rnE "PendingQuestion\|flag_modified\|\.context *=" app/agent/` | **`loop.py:210` `from sqlalchemy.orm.attributes import flag_modified` · `:1229` `flag_modified(row, "output")`** 2건 신규(그 밖은 docstring·`PendingQuestionOut` 뿐으로 전과 같음). `:212` 에 `AgentTrace` ORM import 도 신규 | 세션 로그 (R-35-1) |

변이 표:

| ID | 변이 | 결과 | 잡은 테스트 |
|---|---|---|---|
| M1 | 거절 분기를 옛 drop 으로 | 검출 | `…reject_asks_new_person_followup_fix035` 외 3건 |
| M2 | 후속 kind 를 identity 로 | 검출 | followup·tag·no 3건 |
| M3 | `Resolution.band` 를 identity 로(태그 칩 확장 누락) | 검출 | options 단언 + 태그 답 **422**(`create_person` 긍정 답 검사가 살아 있다, D1) |
| M4 | 후보 1명 문구를 옛 문구로 | 검출 | `test_resolve_identity_single_candidate_question_wording_fix035` |
| M5 | 후보 2명 이상 문구도 "님이" 로 | 검출 | 기존 `…identity_payload` 에 추가된 단언 |
| M6 | `flag_modified` 제거(UPDATE 안 나감) | 검출 | `…writes_trace_fields_fix035` `KeyError` — trace 테스트가 DB 재조회로 영속을 실제로 본다 |
| M7 | `resume_trace_id=None` | 검출 | 같은 테스트 |
| **M8** | **`hints` 를 싣지 않음(hierarchy 힌트 유실)** | **살아남음(36 passed)** | 없음 → R-35-2 |
| M9 | `followup_question_id` 에 엉뚱한 값 | 검출 | 같은 trace 테스트 |
| M10 | 후속 턴 `stop_reason=None` | 검출 | followup 테스트 |
| M11 | 후속 context `utterance` 비움 | 검출 | tag 테스트(`add_event` 0 — `raw_utterance` 검증이 막는다) |
| M12 | 거절 조건 뒤집기 | 검출 | 기존 identity 긍정 경로 2건 + 신규 4건 |

## 3. 판정

### 3.1 수정안 대조

| 항목 | 명세(FIX-035.md 행) | 코드·시험 | 판정 |
|---|---|---|---|
| 거절 시 보류 제안 유지 + 같은 mention 으로 new_person 질문 | 31 | `loop.py:1441~1450` → `_followup_new_person_turn`; `pending_calls` 그대로 전달; 테스트 `resume["pending_calls"] == ["add_event"]` | ✓ (M1·구현자 M6) |
| 질문 문구·칩(태그 5 + "아니요") | 32~33 | `:1192~1196` + `_extend_for_ask` 재사용(`:1206~1212`); 테스트 options 단언 | ✓ (M2·M3) |
| `PendingResume` 에 원래 `pending_calls`·`hints` | 34 | `:1198·1209~1210` — **hints 전달은 테스트가 고정하지 않음** | ✓ 코드 / 시험 공백(R-35-2) |
| 그 자리에서 재개 턴 종료 | 35 | `return _followup_new_person_turn(...)` → `_log_turn`, `stop_reason="ask_user"` | ✓ (M10) |
| ER 재실행 없음 · band 는 new_person | 36 | `resolve()`·`apply_resolution()` 호출 없음, `Resolution(band="new_person", trace_id=None)` 수동 생성 | ✓ |
| 원칙9: `loop_resume` output 에 `identity_rejected`·`followup_question_id` | 37 | `:1224~1230` 두 키만 추가 + `flag_modified` + `flush` | ✓ 동작 (M6·M7·M9) / 구조는 R-35-1 |
| 후속 답 → 기존 경로(태그 → `create_person` + 원래 `add_event`, "아니요" → 0회) | 38~40 | 재개 `new_person` 분기 무변경(`:1452~1480`); 테스트 tag(`persons +1, events +1, relation_tag="직장", raw_utterance` 원문)·no(0·0) | ✓ (M11·M12) |
| 후보 1명 `<이름> 님이 맞으실까요?` · 2명 이상 옛 문구 · options/candidate_ids/affirmative 불변 | 44~46 | `pipeline.py:210~214`; 두 테스트 | ✓ (M4·M5) |
| 전체 회귀 skip 0 · ruff | 56 | §2 #1·#2 | ✓ |

### 3.2 메인 세션이 짚어 둔 점 5개

1. **`apply_resolution` 우회.** 우회가 맞다 — 후속 경로는 `ask_user` 를 루프가 직접 부른다. 선례가 있다: U5 의 `schedule` 질문도 루프가 `ask_user(kind="schedule")` 를 직접 부른다(01-plan U5). 우회로 잃는 것은 `er_resolve` 행의 `decision.pending_question_id` 연결뿐이고, 대신 `loop_resume.output.followup_question_id` 와 `ask_user` 의 `tool_call` 행(`@traced`)이 그 연결을 맡는다. **D1 "승인 시에만 create_person" 은 그대로다**: 후속 경로가 부르는 것은 `ask_user` 하나이고, 생성은 두 번째 답이 `resume_turn` 의 기존 `new_person` 분기(`ctx.confirmed_question_id = question_id` → `create_person` → `persons.py:303~320` 확인 검사)를 탈 때만 일어난다. M3 에서 긍정 답 검사가 422 로 막는 것을 봤다. 원칙1(자동 병합·생성 없음)·원칙2·원칙4(ER 단계·임계치 무변경)도 지켜진다 — 이 경로는 확신도·임계치를 읽지 않는다(금지 토큰 테스트 통과).
2. **기존 `loop_resume` 행 output 사후 수정.** 방식 자체는 저장소의 확립된 선례를 따른다 — `apply_resolution` 이 F-93f063 결정으로 같은 `er_resolve` 행의 `decision` 세 키만 `flag_modified` 로 바꾼다(`pipeline.py` 420~440행 "판정 필드 불변, 전체 재기록 금지"). 여기도 "두 키만 더한다" 고 적었고 M6·M7·M9 가 영속을 증명한다. 원칙9 관점에서 "진입 기록 + 전환 사실" 이 한 행에 있는 것은 읽기에도 낫다. 대안 (i) 새 step 행 — `LOOP_TRACE_STEPS` 6종 고정(결정 F, U1 테스트)이라 어휘 변경이 필요해 FIX 범위를 넘는다. (ii) `loop_turn` output(TurnResult) 에 싣기 — 스키마 변경. **그래서 방식은 타당하나, 그 코드가 `app/agent/` 에 있는 것이 문제다**(R-35-1): P5-loop 가 증거로 닫은 "루프는 ORM 을 직접 만지지 않는다" 를 깬다. `apply_resolution` 과 같은 자리(`app/tools/context.py` 의 `traced` 옆 또는 `app/er/pipeline.py` 의 `_load_trace_row` 와 같은 헬퍼)로 옮기면 선례와 불변식을 둘 다 지킨다.
3. **private 상수 import.** `from app.er.pipeline import _NEW_PERSON_CONFIRM_OPTION, _NEW_PERSON_REJECT_OPTION`(`loop.py:214`). 01-plan U4 의 "ER 원본의 부정 옵션을 그대로 쓴다 — 문자열을 베끼지 않는다" 취지는 지켰고 ruff 도 통과하나 밑줄 이름 결합이다(R-35-5, 권고).
4. **`confidence_breakdown` 제외.** 재개는 `context` 에서 `mention`·`candidate_ids`·`utterance`·`resume` 만 읽으므로(`resume_turn` 1403~1420행) **기능 손실은 없다.** 원칙9 근거는 원래 identity 질문 행(`pending_questions.context`)과 `er_resolve` 행에 그대로 있다. 다만 (a) S3.4 13행은 context 에 "확신도 분해" 를 넣으라 하고 ER 이 만드는 new_person 질문은 넣는데 후속 질문만 빠져 **같은 kind 의 두 질문 모양이 다르다**, (b) 뺀 이유(`test_agent_loop.py:225` 금지 토큰)가 코드에 없다 — 2031 증거의 1 failed 가 그 이유를 보여 준다. 권고(R-35-4).
5. **그 밖에.** 거절→후속→태그→`create_person`+원래 `add_event`(테스트 + M11), "아니요"→0회(테스트), 후보 1명·2명 문구(M4·M5) 전부 확인. **identity 재질문 루프 가능성 없음**: 후속 질문 뒤 태그 답이면 `preresolved[mention]` 로 `resolve()` 를 건너뛰고, "아니요" 면 `_drop_calls_for_mention` 으로 그 언급이 사라진다 — 같은 언급으로 identity 가 다시 나올 길이 없다. 다른 언급이 또 되묻는 것은 U7 규칙 그대로다. 추가로 본 가장자리: `resume_raw` 가 비어 있는 옛 identity 질문(P2 가 직접 만든 행)에 거절해도 `pending_calls=[]` 로 후속 질문이 나가고 태그 답은 인물만 만든다 — 해롭지 않다.

### 3.3 범위·기록

- 제품 코드 변경은 FIX-035 수정안이 지정한 두 파일뿐. 제외 범위(원칙7) 침범 없음. 비밀 문자열 없음(diff 육안 + 증거 통로 비밀 검사 통과).
- `registry.md` 두 행에 FIX-035 추가("해시 pending" — 커밋 때 메인 세션이 채운다). P5-loop 03-log 에 U7 변경 한 줄(03-log U7 (4) "새 인물 질문으로 자동 전환하지 않는다" 와 반대 방향 — 새 줄이 근거를 가리킨다). HANDOFF 갱신 있음.
- `docs/wiki/packages/P8-frontend/tests.md` 에 FIX-035 테스트 5건이 없다(R-35-6).

## 4. 소견

### [필수]
- **R-35-1 · `app/agent/loop.py` 가 ORM(`AgentTrace`)·`flag_modified` 를 직접 써서 P5-loop 판정 표 23행 불변식이 깨졌고, FIX-035.md 가 이를 적지 않았다.** 근거: `loop.py:210` `from sqlalchemy.orm.attributes import flag_modified` · `:212` `from app.db.models import …, AgentTrace` · `:1225~1230` `ctx.session.get(AgentTrace, resume_trace_id)` + `row.output[...] = …` + `flag_modified(row, "output")`; P5-loop 01-plan 143행 "`grep -rnE "PendingQuestion\|flag_modified\|\.context *=" app/agent/` → **0건**" · 367행 "`pending_questions`·`agent_traces` 를 쓰는 유일한 자리가 툴 7종과 `@traced` … (루프는 ORM 을 직접 만지지 않는다 — 판정 표 23행)" · 04-review 126·152행(evidence `20260925-1950-verifier-greps-2.txt` 로 닫음); FIX-035.md 58~64행 기획서 정합성 절은 U7 문구 변경만 적고 이 불변식은 언급 없음. 재현: `grep -rnE "flag_modified|AgentTrace" app/agent/` → 3건. 해결 후보: **(a)** trace 부분 갱신 헬퍼(예: `amend_trace_output(ctx, trace_id, extra: dict) -> None`, "키 추가만, 기존 키 덮어쓰기 금지, `flag_modified` + `flush`")를 `app/tools/context.py` 의 `traced` 옆에 두고 루프는 그것만 부른다 — `apply_resolution` 의 F-93f063 규약과 같은 자리·같은 수단이 되고 grep 은 다시 0건. **(b)** 사용자가 불변식 완화를 결정하면 01-plan 판정 표 23행·04-review 에 FIX-035 각주, FIX-035.md 정합성 절에 한 줄. 어느 쪽이든 재검증은 `grep -rnE "PendingQuestion|flag_modified|\.context *=" app/agent/` 와 `…writes_trace_fields_fix035` + M6 재실행이면 끝난다.

### [권고]
- **R-35-2 · `hints` 전달이 테스트로 고정되지 않았다(변이 M8 생존).** 근거: `…-1722-verifier-FIX-035-mutations.txt` M8 `36 passed`; `loop.py:1198·1209` 는 전달하지만 `_start_identity_question` 에 `create_person` 힌트 제안이 없어 `hints={}` 인 경우만 시험한다. 추가할 테스트 1건: `create_person(person="팀장", relation_tag=…, hierarchy="상")` 힌트 제안을 함께 넣은 identity 질문 → 거절 → "직장으로 기억할게요" → `person.hierarchy == "상"`(힌트 없으면 `_DEFAULT_HIERARCHY="동"` 과 구분된다). FIX-033 (a) "계약 값은 값으로 단언한다".
- **R-35-3 · 낡은 docstring 4곳.** `loop.py:1362~1363` resume_turn "답이 후보 밖(ER 거절 옵션)이면 그 언급에 딸린 보류 제안을 버리고 아무것도 만들지 않는다" · `:1395~1400` "진행할 보류 제안이 없어도 … `loop_resolve_done`/`loop_record` … 각 1행씩 남는다"(후속 경로는 두 행을 남기지 않는다) · `:1316` `_drop_calls_for_mention` "부정 답(identity 거절/…)"(identity 거절은 더 이상 이 함수를 부르지 않는다) · `:1158~1160` `_log_resume_entry` "`resume_input.to_dict()` 가 `input`/`output` 양쪽에 그대로 실린다"(거절 경로에서 output 에 두 키가 더해진다). 재현: `sed -n '1158,1160p;1316p;1362,1363p;1395,1400p' app/agent/loop.py`.
- **R-35-4 · `confidence_breakdown` 생략 이유가 코드에 없고, 같은 kind 의 두 질문 모양이 다르다.** 근거: `loop.py:1185~1190` context 에 키 없음 ↔ `pipeline.py:224~231` new_person context 에 있음; S3.4 13행; 구현자 증거 `20261015-2031-FIX-035-full-regression.txt` 1 failed(`금지 토큰 발견: confidence`) → 2032 통과. 해결 후보: (i) `_followup_new_person_turn` docstring 에 "확신도 분해는 원래 identity 질문 행·`er_resolve` 행에 있고, 이 모듈은 확신도 토큰을 쓰지 않는다(판정 표 6행)" 한 줄, 또는 (ii) 키 이름을 적지 않고 원래 `context` 를 통째로 옮긴다 — `{k: v for k, v in context.items() if k not in ("resume", "candidate_ids", AFFIRMATIVE_KEY)}` 에 `candidate_ids: {}`·`AFFIRMATIVE_KEY` 를 다시 얹으면 손실 없이 금지 토큰도 없다. FIX-035.md 결과 절에 2031→2032 경위 한 줄.
- **R-35-5 · `app.er.pipeline` 의 밑줄 상수 2개를 `app/agent/loop.py` 가 import 한다.** `loop.py:214`. 해결: `app/er/types.py`(또는 `app/er/__init__.py` `__all__`)에 `NEW_PERSON_CONFIRM_OPTION`/`NEW_PERSON_REJECT_OPTION` 으로 공개하고 `pipeline.py` 는 그것을 쓴다(값 불변 — `tests/test_er_pipeline.py` 문자열 단언 그대로). 낮은 우선.
- **R-35-6 · `packages/P8-frontend/tests.md` 에 FIX-035 테스트 5건(`test_api_answers_resume.py` 4 · `test_er_pipeline.py` 1)이 없다.** 사용자 규칙(2026-10-15, 테스트 1건 = 표 1줄, U9부터 의무). P8 활성 중 들어간 테스트이므로 같은 표에 "FIX-035" 절로 5줄(변이 ID 열은 이 문서 §2 표의 M1~M12) — 또는 P5-loop 쪽에 둘지 메인 세션이 정한다.

## 5. 결론

`검증:` 줄은 `검증: 보류 — verifier (fable) 2026-10-16, review-FIX-035.md ([필수] R-35-1)` 로 썼다. R-35-1 은 (a) 헬퍼 이동이면 backend-agent 가 바로 고칠 수 있고, (b) 불변식 완화면 사용자 결정 + 문서 세 곳이다. 재검증: ① `grep -rnE "PendingQuestion|flag_modified|\.context *=" app/agent/` 0건(또는 (b) 의 기록 확인) ② `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q tests/test_api_answers_resume.py tests/test_er_pipeline.py` ③ M6·M7·M9 재실행이 여전히 `…writes_trace_fields_fix035` 를 실패시키는지 ④ R-35-2 테스트를 넣었다면 M8 검출 — 넷으로 끝난다. R-35-3~6 은 이번 커밋에 포함할지 사용자·메인 세션이 정한다.

---

## 재확인 (2026-10-16) — 재작업 1차

검토자: verifier (fable) · 기준 HEAD `c4fbd2f` + 작업 트리 미커밋 diff 13파일(`app/agent/loop.py` +135/-3 · `app/er/__init__.py` +4 · `app/er/pipeline.py` +16/-8 · `app/er/types.py` +6 · `app/tools/context.py` +24 · `tests/test_api_answers_resume.py` +184 · `tests/test_er_pipeline.py` +21 · `tests/test_tools_context.py` +31 · registry · P5-loop 03-log · P8 tests.md · HANDOFF · journal) · 사용자 결정: R-35-1 방식 (a) + R-35-2~6 전부 포함.

**결과: 통과 — [필수] 0, [권고] 2(R-35-7·R-35-8, 모두 문서 정합성).** R-35-1~6 중 R-35-1·2·3·5·6 은 닫혔고 R-35-4 는 코드 쪽은 닫혔으나 FIX-035.md 결과 절의 "2031→2032 경위 한 줄" 이 빠져 있다(R-35-8 에 묶음). 재작업이 범위 밖 변경을 넣지 않았고(`git diff` 전체 §재확인-3), 내가 돌린 변이 12종이 전부 검출됐다. 코드·테스트·계획은 고치지 않았다.

### 재확인-1. 내가 직접 실행한 것 (전부 `save_evidence.py` 통로, 출력 전문)

| # | 확인 | 결과 | 증거 |
|---|---|---|---|
| 1 | 전체 회귀 `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs -q` | **1953 passed, skip 0**(skip 줄 0건), 1 warning(google.genai Deprecation — 전과 같음), 25.35s, exit 0 | `fixes/evidence/20261016-1750-verifier-FIX-035-recheck-regression.txt` |
| 2 | `.venv/bin/ruff check app tests scripts evaluation`(CI 범위) | All checks passed, exit 0 | `…-1750-verifier-FIX-035-recheck-ruff.txt` |
| 3 | R-35-1 재검증 ① 판정 표 23행 부정 grep `grep -rnE --include=*.py 'PendingQuestion\|flag_modified\|\.context *=' app/agent/` + `c4fbd2f` 대조 | **19줄 / 19줄, 파일명·행번호 제외 내용 동일**(전부 docstring·`PendingQuestionOut` DTO). `grep -rnE 'flag_modified\|AgentTrace' app/agent/` → **0건** | `…-1752-verifier-FIX-035-recheck-grep2.txt` (1)~(4) + 덧붙인 정정 대조 "동일: … 19줄 일치". (`…-1751-verifier-FIX-035-recheck-grep.txt` 는 (3) 의 접두 제거가 안 돼 거짓 차이를 보여 grep2 로 대체 — 수치 19/19 와 0건은 같다) |
| 4 | R-35-5 옛 밑줄 상수 잔존 `grep -rnE '_NEW_PERSON_(CONFIRM\|REJECT)_OPTION' app tests scripts evaluation` / 공개 상수 정의·사용 | 잔존 **0건**. 정의 `app/er/types.py:39~40`, 재export `app/er/__init__.py:19~20·42~43`, 사용 `pipeline.py:92~93·230·235~236`·`loop.py:212~213·1200·1205~1206` | 같은 파일 (5)·(6) |
| 5 | R-35-3 docstring 4곳 · R-35-4 생략 이유 한 줄 | `loop.py:1165`(`_log_resume_entry`) · `:1321`(`_drop_calls_for_mention`) · `:1368`(resume_turn identity 항목) · `:1408`(resume_turn "각 1행씩" 예외) · `:1192`("context 에 확신도 분해를 싣지 않는다 -- … 판정 표 6행, 금지 토큰 테스트") | 같은 파일 (9)·(10) |
| 6 | 변이 12종 — 스크래치패드 사본 `fix035v2/`(`app`·`tests`·`alembic`·`alembic.ini`·`pyproject.toml` rsync, 사본 5파일 `cmp` 일치, `loop/context/types.__file__` 이 사본을 가리킴 출력) 에서 `mut.py` 가 치환→pytest(세 파일 48건)→원복 | 대조군 48 passed · **12/12 검출** · 원복 "사본 4파일 원문과 동일" · 저장소 `git diff --stat` 시작·종료 모두 `13 files changed, 427 insertions(+), 24 deletions(-)` | `…-1753-verifier-FIX-035-recheck-mutations.txt` |
| 7 | 범위: `git diff --stat`·`git status --porcelain` untracked | 제품 코드 5파일·테스트 3파일·위키 5파일. untracked 는 FIX-035.md·review·증거 파일뿐 | `…-1752-verifier-FIX-035-recheck-grep2.txt` (7)·(8) |

변이 표(1차 M 번호 유지, V 는 재작업이 새로 만든 것을 겨냥):

| ID | 변이 | 결과 | 잡은 테스트 |
|---|---|---|---|
| M1 | 거절 분기를 옛 drop 으로 | 검출 | fix035 5건(`…followup`·`…writes_trace_fields`·`…then_tag`·`…then_no`·`…keeps_hierarchy_hint`) |
| M2 | 후속 kind 를 identity 로 | 검출 | 4건 |
| M4 | 후보 1명 문구를 옛 문구로 | 검출 | `test_resolve_identity_single_candidate_question_wording_fix035` |
| **M6** | 헬퍼에서 `flag_modified` 제거 | 검출 | **`…writes_trace_fields_fix035` `KeyError`** + 헬퍼 계약 테스트 |
| **M7** | 루프가 `resume_trace_id=None` | 검출 | **`…writes_trace_fields_fix035`** |
| **M8** | `hints` 미전달(R-35-2) | **검출(1차에서는 생존)** | `…keeps_hierarchy_hint_fix035` `KeyError: 'hierarchy'` |
| **M9** | `followup_question_id` 에 엉뚱한 값 | 검출 | **`…writes_trace_fields_fix035`** |
| M12 | 거절 조건 뒤집기 | 검출 | 기존 identity 긍정 2건 + fix035 5건 |
| V1 | 헬퍼에서 `ctx.session.flush()` 제거 | 검출 | 헬퍼 계약 테스트(`expire_all` 뒤 재조회가 `{'a': 1}`) |
| V2 | `ask_user` 반환값을 그대로 쓰지 않고 `status="answered"` 로 다시 만듦 | 검출 | `…followup_fix035` `'answered' == 'pending'` |
| V3 | `_extend_for_ask` 결과 대신 확장 전 payload 로 `ask_user` | 검출 | options 단언 + 태그 답 422 + `KeyError: 'resume'` |
| V4 | 공개 상수 `NEW_PERSON_REJECT_OPTION` 값 변경("아니오") | 검출 | 기존 `…new_person_reject_creates_nothing` + fix035 2건 — 승격 뒤에도 값이 테스트로 고정돼 있다 |

재검증 ③ 의 답: `…writes_trace_fields_fix035` 를 실패시킨 변이 = **M1·M6·M7·M9·M12**(증거 끝줄 "trace 테스트 … 를 실패시킨 변이"). ④ 의 답: M8 검출.

### 재확인-2. 소견별 닫힘 판정

| 소견 | 판정 | 근거 |
|---|---|---|
| **R-35-1** [필수] | **닫힘** | 방식 (a). `app/tools/context.py:244~262` `amend_trace_output(ctx, trace_id, extra) -> bool` — `traced` 바로 아래, `flag_modified` import 도 이 파일로 이동(`:79`). `app/agent/` 에 `flag_modified`·`AgentTrace` 0건, 23행 grep 19줄 = `c4fbd2f`(재확인-1 #3). 루프는 `loop.py:1235` 한 곳에서 헬퍼만 부른다. M6·M7·M9 가 여전히 trace 테스트를 실패시킨다(#6) |
| R-35-2 | 닫힘 | `tests/test_api_answers_resume.py:242~276` `…keeps_hierarchy_hint_fix035` — `create_person(hierarchy="상")` 힌트 제안을 함께 넣고 거절 → 태그 답 → 후속 context `resume.hints.hierarchy == "상"` 과 `person.hierarchy == "상"` 을 값으로 단언(FIX-033 (a)). M8 검출 |
| R-35-3 | 닫힘 | 4곳 전부 고쳐짐(재확인-1 #5). 새 문장이 실제 동작과 맞는지 코드로 대조: `_drop_calls_for_mention` 은 identity 분기에서 더 이상 불리지 않고(`:1443~1459` `return _followup_new_person_turn(...)`), 후속 경로는 `loop_resume`+`ask_user`+`loop_turn` 행만 남긴다(`_followup_new_person_turn` 은 `_log_turn` 만 부른다) |
| R-35-4 | **부분 닫힘** | (i) 채택: `loop.py:1192~1194` docstring 한 줄 있음. 그러나 "FIX-035.md 결과 절에 2031→2032 경위 한 줄" 은 없다(`grep -n "2031\|2032" docs/wiki/fixes/FIX-035.md` → 0건). 코드 쪽은 끝났으므로 [권고] R-35-8 로 묶는다 |
| R-35-5 | 닫힘 | `app/er/types.py:36~40` 공개 상수(값 `"네, 기억해둘게요"`·`"아니요"` 불변), `app/er/__init__.py` `__all__` 에 export, `pipeline.py`·`loop.py` 가 같은 이름을 쓴다. 밑줄 이름 잔존 0건(재확인-1 #4). V4 가 값 고정을 증명 |
| R-35-6 | 닫힘 (단 R-35-7) | `packages/P8-frontend/tests.md:419~431` "FIX-035" 절 7행 — 열 5개가 위 표와 같고, 변이 ID 열이 이 문서 §2·재작업 증거의 ID 를 가리키며, "실패 이력" 열이 M8 생존→보강 경위를 적었다(`…keeps_hierarchy_hint` 행). 7행 = 실제 신규 테스트 7건(`pytest --collect-only`: answers_resume 11→16, er_pipeline 20→21, tools_context 10→11) |

### 재확인-3. 새로 생긴 것 검토

1. **`amend_trace_output` 계약.** 키 추가만·기존 키 덮어쓰기 `ValueError`·행 없음/`None`/`output` 이 dict 아님 → `False`·`to_jsonable` 적용·`flag_modified`+`flush`, commit 없음. `apply_resolution` 의 F-93f063 갱신(`pipeline.py` 420~440행, `decision` 세 키를 **바꾸는** 것)과 충돌하지 않는다 — `apply_resolution` 은 이 헬퍼를 부르지 않고 자기 규약대로 직접 고치며(`grep -rn amend_trace_output app` → 정의 + `loop.py` 1곳뿐), 헬퍼의 "덮어쓰기 거부" 는 루프의 사후 추가에만 걸린다. 루프에서 `ValueError` 가 날 수 있는가: `loop_resume` 행 `output` 은 `ResumeInput.to_dict()`(`kind`·`context`·`answer`)이고 `identity_rejected`·`followup_question_id` 와 겹치지 않는다. 트랜잭션 경계: `ask_user`(`@traced`, flush) → 헬퍼(flush) → `_log_turn` 모두 같은 요청 세션 안, commit 은 호출자(결정2·툴 규약 그대로). 사소한 점: 루프가 반환값 `bool` 을 버리므로 `False`(행 없음) 가 조용히 지나간다 — `resume_trace_id = ctx.last_trace_id`(`:1422`) 는 `_log_resume_entry` 직후라 실제로 `None` 이 될 길이 없고, M7 이 그 경우를 테스트가 잡는 것을 보여 주므로 소견으로 올리지 않는다.
2. **`ask_user` 반환값 재사용.** `questions.py:225~231` 은 저장된 행에서 `question_id`·`status="pending"`·`kind`·`question`·`options` 를 만들어 돌려주고, 기존 경로의 `_pending_question_from_resolve`(`loop.py:1030~1048`)도 같은 5필드를 payload 에서 만든다. 값은 같다 — `ask_user` 의 정규화는 공백·중복 검사뿐이고 payload 에 그런 입력이 없다. 테스트가 `question`·`options`·`status`·`question_id != q1` 을 그대로 단언하고 V2 가 검출됐다. ORM 재조회 없음(23행 유지).
3. **공개 상수 승격.** 옛 이름 잔존 0건(재확인-1 #4). 문서에만 `_NEW_PERSON_*` 이 남는데(`review-FIX-035.md` §3.2 3항·P5-loop 02-plan-verify H-4) 둘 다 역사 기록이라 고칠 것이 아니다.
4. **tests.md 형식·집계.** 형식은 맞다(R-35-6). 그러나 FIX-035 절 머리글 "위 총계·집계에는 넣지 않는다" 와 "실패 이력 집계" 의 **세는 법 명령이 어긋난다** → R-35-7.
5. **범위.** `git diff` 전체를 읽었다. 제품 코드 변경은 R-35-1~5 가 지정한 파일(`loop.py`·`pipeline.py`·`types.py`·`__init__.py`·`context.py`)뿐이고, 수정안 (가)(나) 의 동작(거절→후속 질문·1명 문구)은 1차와 같다(M1·M2·M4·M12 재검출). 삭제된 테스트 없음(diff 에 `-` 테스트 줄 없음, 건수는 전부 증가). 비밀 문자열 없음(증거 통로 비밀 검사 전부 통과). 원칙1·2·4·7·9, D1, S3.3·S3.4 판정은 §3.1~3.2 그대로 — 재작업은 구조(헬퍼 위치·상수 이름)와 테스트만 바꿨다.

### 재확인-4. 새 소견 (전부 [권고] — 커밋을 막지 않는다)

- **R-35-7 · tests.md "실패 이력 집계" 의 세는 법 명령이 FIX-035 절 7행을 함께 세어 표와 어긋난다.** 근거: `tests.md:441` 세는 법 `grep -c "^| .*| 기록 없음" tests.md` → 표는 176 인데 지금 **182**(`+6`), `… \*\*검출 실패 → 보강\*\*` → 표는 17 인데 지금 **18**(`…keeps_hierarchy_hint` 행의 "검출 실패 → 보강"). `c4fbd2f` 의 같은 파일은 176·17 로 표와 일치했다. 해결 후보: (i) FIX-035 7행을 집계에 넣어 203 → 210(백엔드 64 → 71, 총계 표에 FIX-035 행 추가), 또는 (ii) 세는 법에 "FIX-035 절 제외" 명령(예: `sed '/^### FIX-035/,/^### 실패 이력 집계/d' tests.md | grep -c …`)을 적는다. 어느 쪽이든 메인 세션·사용자가 정한다.
- **R-35-8 · 기록 정합성 세 곳.** (a) `registry.md:176` `tests/test_api_answers_resume.py` 행 "+4건 (11 → 15건)" — 실제 **+5, 16건**(`pytest --collect-only -q tests/test_api_answers_resume.py` → 16; R-35-2 테스트가 더해졌다). (b) `registry.md:168` `app/agent/loop.py` 행·`:88` `app/er/pipeline.py` 행·`:81` `app/er/__init__.py` 행에 FIX-035 변경(`_followup_new_person_turn`·resume_turn identity 분기·후보 1명 문구·상수 재export)이 없다 — `grep -c FIX-035 docs/wiki/registry.md` 5건은 전부 `context.py`·`types.py`·테스트 3행이다. 1차 리뷰 §3.3 이 "두 행" 으로 넘긴 것을 내가 좁게 봤다. (c) R-35-4 의 "FIX-035.md 결과 절에 2031→2032 경위 한 줄" 미기재. 셋 다 커밋 때 메인 세션이 "해시 pending" 을 채우며 같이 적을 수 있는 크기다.

### 재확인-5. 결론

`검증:` 줄을 `통과 — verifier (fable) 2026-10-16 재확인` 으로 바꿨다. [필수] 없음. R-35-7·R-35-8 은 문서 정합성이라 이번 커밋에 넣을지(메인 세션이 "해시 pending" 을 채울 때 같이) 사용자·메인 세션이 정한다. 커밋 뒤 남는 확인은 FIX-035.md 가 정한 대로 실서버 U10 사람 점검(identity 거절 → 후속 질문 칩 → 태그 → 인물 카드·사건)뿐이다.
