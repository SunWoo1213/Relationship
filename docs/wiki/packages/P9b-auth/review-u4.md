# P9b-auth U4 커밋 전 리뷰 — 계정당 채팅방 하나: 대화 기록 저장과 `GET /chat/history`

검토자: verifier (fable)
일시: 2026-11-16 (HEAD `75845d1` + 미커밋 작업 트리, dev2). Mac 로컬만 판정.
범위: `app/api/routes.py`·`app/api/schemas.py`(diff) · 새 `app/chat/__init__.py`·`app/chat/history.py` · `tests/test_user_isolation.py`(diff, R-10·R-11) · 새 `tests/test_chat_history.py` · `03-log.md` "U4 구현 메모(초안)" · `tests.md` U4 절 · `evidence/20261116-00*-u4-*`. 읽기만: `web/src/api/types.ts`·`client.ts`·`screens/ChatScreen.tsx`, `app/db/models.py`(`ChatMessage`), `app/db/session.py`(`get_session`), `app/tools/questions.py`(`answer_question`), `app/api/deps.py`(`build_ctx`·`load_resume_input`).

판정: 통과

열린 [필수] 0 · [권고] R-1~R-5(모두 커밋을 막지 않음).

## 1. 직접 실행한 명령과 결과

증거는 모두 `docs/wiki/packages/P9b-auth/evidence/`(`save_evidence.py` 저장). `<SCR>` = `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad`. 시험용 DB 를 새로 만들지 않았고 pytest 를 동시에 돌리지 않았으며, 저장소에는 이 문서와 evidence 밖에 쓰지 않았다.

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2491 passed**, 실패 0, skip 0, exit 0 | `20261116-0049-verifier-u4-pytest-all.txt` |
| 새 시험 + 열거 401 | `… -m pytest tests/test_chat_history.py tests/test_auth_required_routes.py -q -rs` | 31 passed | `20261116-0049-verifier-u4-pytest-history.txt` |
| ruff(CI 범위, `--fix` 없음) | `.venv/bin/python -m ruff check app tests scripts evaluation` | All checks passed | `20261116-0052-verifier-u4-ruff.txt` |
| mypy · tools_check · alembic check · 범위 · 호출처 | `bash <SCR>/vu4/static.sh` | mypy 새 오류 없음(38/38) · tools 7/7 · `No new upgrade operations detected` · 제품·시험 변경 = `app/api/{routes,schemas}.py`·`tests/test_user_isolation.py`·새 `app/chat/`·`tests/test_chat_history.py` 뿐 · `git diff --stat -- app/er app/tools app/agent evaluation reports data alembic web` 빈 출력 · `append`/`recent` 호출처는 `app/api/routes.py` 7곳뿐 | `20261116-0049-verifier-u4-static.txt` |
| 탐침(변이 없음) + 변이 11종 | `bash <SCR>/vu4/run-mut.sh`(저장소 밖 사본 `<SCR>/vu4/copy`, 롤백형 시험 6파일 + 탐침 `<SCR>/vu4/test_vprobe_u4.py`, 공급자 키 환경변수 제거) | 기준선 102 passed(저장소 시험 85 + 탐침 17). 변이 11종 **전부 저장소 시험이 잡음** — 3절 | `20261116-0052-verifier-u4-mutations.txt` |
| 시험 DB 잔여 | `.venv/bin/python <SCR>/p9b-u4/residue.py`(읽기만) — 내 실행 전·후 | 12개 테이블 중 `agent_traces` 밖 전부 0. `agent_traces` 243 → 252(+9 는 전체 pytest 1회의 `test_answer_concurrency` 누적 — 기존 U3b R-7, 변이 실행은 0 추가) | `20261116-0049-verifier-u4-residue-before.txt` · `20261116-0053-verifier-u4-residue-after.txt` |

`…-verifier-u4-static.txt` 의 **exit 1 은 내 스크립트 탓이다** — 첫 두 단계를 CI 보다 넓게 걸었다: `ruff check .` 이 범위 밖 `.claude/scripts/{bash_write_check,findings}.py` 의 기존 4건(B007·DTZ005×2·F541)을 잡았고, 이 저장소가 쓰지 않는 `ruff format --check` 가 차이를 냈다. 둘 다 U4 와 무관하며 판정에 쓰지 않는다. CI 와 같은 범위의 ruff 는 위 `…-ruff.txt`(통과)다. 그 파일의 mypy·tools·alembic·범위 절은 각 `exit=0` 으로 유효하다.

## 2. 판정 근거 (요청 항목 1~7)

**1. 계정 격리 — 문제 없음.**
- 저장 7곳·조회 1곳이 전부 `user.id`(= `Depends(current_user)`)를 넘긴다(`routes.py:258,267,291-301,389,397,407-415,429`). `app/chat/history.py` 의 두 함수는 `user_id` 가 필수 인자이고 `recent` 는 `.where(ChatMessage.user_id == user_id)` 하나로만 고른다.
- `/answers` 는 `build_ctx` 가 `question.user_id != user.id` 면 `QuestionNotFound` 를 던진 **뒤에** 기록한다(`deps.py:148-149` → `routes.py:252-258`) — 남의 질문에 답하면 어느 쪽에도 행이 남지 않는다(`test_answering_other_users_question_is_404_and_saves_nothing_for_either`, 변이 VV-6 이 `(2, 1) == (2, 0)` 으로 깨짐).
- 스케줄러·브리핑·푸시 경로에는 `append` 호출이 없다(`static.txt` "append/recent 호출처" — `routes.py` 밖 0줄).
- 변이: 구현자 V4-2·V4-2b·V4-10 + 내 VV-8(`/answers` 사용자 행을 다른 계정으로) → `test_other_accounts_history_is_never_mixed` `5 == 6`.

**2. 트랜잭션 — 사용자 행을 `run_turn`·`resume_turn` 앞에서 저장한 판단은 맞다.**
- 계획 문구 "라우트의 기존 트랜잭션 안에서 저장(요청이 실패해 롤백되면 기록도 없다). 루프가 오류를 200 답으로 삼키는 경우도 그 답을 저장한다"(01-plan 166행)를 둘 다 만족하는 위치는 **세이브포인트 밖·루프 앞**뿐이다. 세이브포인트 안(VV-3·VV-4)이나 성공 경로 끝(VV-5)으로 옮기면 삼킨 오류에서 사용자 행이 사라지고, 세 변이 모두 `test_*_loop_error_swallowed_as_200_still_saves_both_rows` 가 잡는다.
- 500: `SQLAlchemyError` 는 라우트가 잡지 않아 `get_session` 의 `rollback()` 을 탄다(`app/db/session.py:87-93`). 시험 픽스처 `env` 가 같은 commit/rollback 규약을 SAVEPOINT 위에 올려 실제로 행이 지워지는지 본다(`test_failed_chat_request_…`·`test_failed_answer_request_…` — 앞선 성공 턴 2행은 남고 그 요청 행만 0).
- `/answers` 404·409: `build_ctx`(404)·`answer_question`(409 `already_answered`·`expired`, 선택지 밖 답)이 **기록 앞에서** 예외를 던지므로 `append` 가 불리지 않는다. 저장소 시험은 404 만 직접 보므로 탐침으로 409 두 종류·선택지 밖 답·없는 질문을 직접 확인했다 — 넷 다 기록 불변(`test_probe_second_answer_409_…`·`…_expired_answer_409_…`·`…_answer_not_in_options_…`·`…_missing_question_404_…`, 기준선 통과). → R-1.
- 삼킴 → 실패 → 삼킴을 이은 탐침(`test_probe_append_then_request_rollback_removes_only_request_rows`)도 통과: 세이브포인트 롤백은 사용자 행을 지우지 않고, 요청 롤백은 그 요청의 행만 지운다.
- **동시 요청**: `created_at` 은 `server_default=func.now()`(`models.py:355-357`)이고 Postgres `now()` 는 트랜잭션 시작 시각이라, 한 요청의 사용자 행·응답 행은 시각이 같고 다른 요청의 행은 시각이 다르다. 정렬 키가 `(created_at, id)` 이므로 **두 요청의 쌍이 서로 끼어들지 않는다**(id 만으로 정렬했다면 A 사용자 → B 사용자 → B 응답 → A 응답으로 섞였을 것이다). 남는 영향은 하나 — 쌍의 순서가 "끝난 순"이 아니라 "시작한 순"이라, 느린 요청이 늦게 끝나면 재로그인 뒤 화면 순서가 그때 본 순서와 다를 수 있다. 데이터 손상·계정 섞임은 없다. → R-2(기록).

**3. 프론트와의 계약 — 깨지는 조합 없음.** `ChatScreen.tsx:59-72,148-165` 의 붙이기 로직을 파이썬으로 옮겨 실제 서버 응답에 돌렸다(탐침 `_attach`).
- 모양: 키 집합 `{id, role, content, question_id, created_at}` 이 `web/src/api/types.ts:28-34` 와 같다(`test_history_item_shape_matches_frontend_type`, 구현자 V4-11). `created_at` 은 프론트가 읽지 않는다.
- (a) 미답변 질문: 질문을 낸 assistant 줄(인덱스 1)에 칩이 붙고 맨 앞 복원 0 — `attached == {1: q1}`, `restored == []`. **U6 R-6 닫힘.**
- (b) 답한 뒤: `q1` 은 `/questions/pending` 에서 빠져 칩이 다시 뜨지 않고, 답은 `(user, "아니요, 다른 사람이에요")` 줄로 보인다. user 줄의 `question_id` 는 프론트가 건너뛴다(`item.role === 'user'` 조기 반환).
- (c) 답변의 응답이 새 질문: 새 질문 `q2` 의 칩이 답변의 응답 줄(인덱스 3)에 붙는다. 그 뒤 답하지 않고 새 발화를 보내도 칩은 그 줄에 남는다.
- (d) 질문 줄이 50개 밖: 기록에 그 `question_id` 가 없고 미답변 목록에는 남아 맨 앞 복원 경로로 간다(`restored == [q1]`) — 답할 수는 있지만 질문 말풍선이 옛 기록 맨 위에 뜬다. 어색하지만 동작. → R-3. 요청마다 2행이라 창의 첫 줄은 user 줄이다(쌍이 갈라지지 않음).
- 삼킨 오류 응답 줄의 `question_id` 는 None(VV-7 이 잡음) — 답한 질문에 칩이 되살아날 근거가 없다.
- 실시간 화면과의 차이 하나: 칩을 누른 직후에는 눌린 칩으로, 재로그인 뒤에는 user 말풍선으로 보인다. 결정 R (i) "칩 답은 user 행으로 답 문자열" 그대로이므로 소견 아님.

**4. `GET /chat/history` — 문제 없음.**
- `limit`: 1·200 → 200, 0·201·-1·`abc`·`1.5`·빈 값·`2e1` → 422(저장소 시험 4건 + 탐침 `test_probe_limit_boundaries`). 기본 50·최대 200 은 결정 I(01-plan 274행) 값 그대로.
- 읽기 전용: 6번 읽은 뒤 `chat_messages`·`agent_traces` 행 수 불변(구현자 V4-9 가 잡음).
- 401: `tests/test_auth_required_routes.py` 는 `app.routes` 를 열거하므로 새 라우트를 수정 없이 잡는다(31 passed, 구현자 V4-8 에서 열거 시험 2건 실패).
- 응답 누출: `response_model=list[ChatHistoryItemOut]` 이 5개 키로 거른다 — 응답 본문에 `user_id`·계정 id 문자열 없음(탐침).

**5. security §5 — 위반 없음, 상한은 권고.**
- "다른 계정·로그·trace 로 복사 금지"(security.md 66행): U4 diff 는 `AgentTrace`·`PendingQuestion.context`·로깅에 닿지 않는다. `_record_loop_error` 가 trace 에 `utterance[:2000]` 를 넣는 것은 P5 부터의 기존 동작이고 U4 가 바꾸지 않았다. 탐침에서 응답 문장이 어느 `pending_questions.context` 에도 없음을 확인.
- `content` 상한 없음: `ChatIn.utterance` 는 `min_length=1` 뿐이고 `Caddyfile`·앱 어디에도 요청 본문 상한이 없다(grep 0줄). 다만 같은 발화가 이미 `events.raw_utterance` 로 상한 없이 저장돼 왔으므로 U4 가 새로 연 구멍은 아니다. `/answers` 쪽은 저장된 선택지 중 하나여야 통과하므로 길이가 묶인다. → R-4.

**6. R-10·R-11 — 닫힘.**
- R-10: `world` 픽스처가 `app.agent.respond.answerer_from_env` 를 `_EchoAnswerer` 로 바꾼다. 호출처가 `_respond.answerer_from_env()`(모듈 속성 조회, `app/agent/loop.py:1414`)라 바꿔 끼우기가 실제로 먹는다. 구현자와 다른 방식의 변이 VVR10(카드 조회가 인물의 실제 소유자를 쓰게)에서 `[identity_query]` 가 **`assert '등산' not in '{"question_…'` 단언**(`test_user_isolation.py:692`)으로 실패했다 — `OpenAIError` 가 아니다. 공급자 키 환경변수를 지운 채 돌렸다.
- R-11: `status_code in (200, 404)` → `== 200` + `stored == {persons:0, events:0, schedules:0}`(diff 확인).

**7. 불변 — 확인.** 기존 시험 변경은 `tests/test_user_isolation.py` 의 R-10·R-11 두 곳뿐(단언을 좁힌 것). `ChatOut`·`AnswerOut` 은 diff 에 없다(`schemas.py` 는 `ChatHistoryItemOut` 추가만, `routes.py` 는 반환값을 변수에 담았다가 그대로 반환). 툴 7종 7/7, `app/er`·`app/tools`·`app/agent`·`alembic`·`web`·`evaluation`·`reports`·`data` diff 0. 범위(01-plan "고치는 기존 파일" U4 행 `app/api/schemas.py` + U4 항목) 밖 변경 0. 계획에 없는 상수·정렬·상한 0.

## 3. 변이 (저장소 밖 사본, 저장소 무수정)

구현자 표 23종(`20261116-0042-u4-mutations-final.txt`)에 없는 것만 골랐다. 모두 **탐침이 아니라 저장소 시험**이 최소 1건 실패한다.

| 변이 | 잡은 저장소 시험 |
|---|---|
| VV-1 `/chat` 저장 순서를 응답 → 사용자로 | 6행 순서 · 모양 · 500 뒤 기록 · 삼킨 오류 (4건) |
| VV-2 `/answers` 저장 순서를 응답 → 사용자로 | 6행 순서 · 삼킨 오류 (2건) |
| VV-3 `/chat` 사용자 행을 세이브포인트 안에서 | `test_chat_loop_error_swallowed_as_200_still_saves_both_rows` |
| VV-4 `/answers` 사용자 행을 세이브포인트 안에서 | `test_answer_loop_error_swallowed_as_200_still_saves_both_rows` |
| VV-5 `/chat` 사용자 행을 성공 경로 끝에서만 | 같은 시험(chat) |
| VV-6 `/answers` 가 답 저장 전에 기록하고 커밋(404·409 에서도 남김) | `test_answering_other_users_question_is_404_…` `(2, 1) == (2, 0)` · `test_failed_answer_request_…` `3 == 2` |
| VV-7 `/answers` 삼킨 오류 응답 행에 옛 `question_id` | `test_answer_loop_error_swallowed_…` |
| VV-8 `/answers` 사용자 행을 다른 계정으로 | 6행 순서 · `test_other_accounts_history_is_never_mixed` `5 == 6` 외 |
| VV-9 `recent` 가 `limit` 무시 | `limit`·기본 50·정렬 시험 4건 |
| VV-10 `/chat` 응답 행 `content` 를 발화로 | 6행 순서 |
| VVR10 카드 조회가 실제 소유자 사용 | `[identity_query]` 단언 실패(위 6번) |

생존 변이 0. 변이 실행 뒤 시험 DB 잔여 0(1절).

## 4. 소견

[필수] 없음.

- **[권고] R-1 `/answers` 409 뒤 기록 0 을 저장소 시험이 직접 보지 않는다.** 404·500 은 시험이 있고 409(이미 답함·만료)·선택지 밖 답은 없다. 지금 코드는 넷 다 같은 구조(기록 앞에서 예외)라 탐침으로 통과를 확인했고 VV-6 도 404 시험이 잡지만, 나중에 `answer_question` 앞으로 저장이 옮겨지면서 409 만 따로 처리되는 회귀는 저장소 시험이 못 잡는다. `tests/test_chat_history.py` 에 "두 번째 답 409 → 4행 그대로" 한 건을 더하면 된다(탐침 원문: `<SCR>/vu4/test_vprobe_u4.py::test_probe_second_answer_409_leaves_no_rows`).
- **[권고] R-2 동시 요청 시 순서는 "요청 시작 순"이다(기록).** 한 계정이 겹치는 요청을 보내면(두 탭, 또는 `/chat` 대기 중 칩 누르기) 쌍은 끼어들지 않지만 재로그인 뒤 순서가 응답이 도착한 순서와 다를 수 있다. 시연은 탭 하나(U6 R-2)라 영향 없음. 03-log 의 "정렬 판단" 에 한 줄 남길 것.
- **[권고] R-3 (d) 질문 줄이 최근 50개 밖이면 질문이 기록 맨 위에 따로 뜬다.** U6 R-6 에서 예고된 ⑥ 경로이며 답은 가능하다. 미답변 질문은 24시간 뒤 만료되고 시연 계정은 약 30행(결정 I 근거)이라 실제로 만날 가능성은 낮다. 고치려면 프론트 몫(복원 위치)이지 U4 가 아니다.
- **[권고] R-4 `content` 길이 상한 없음.** `POST /chat` 발화에 상한이 없고 요청 본문 상한도 없다(Caddy·앱). U4 이전부터 `events.raw_utterance` 가 같은 상태였고, 계획이 상수를 비워 두었으므로 구현자가 임의로 넣지 않은 것은 맞다(FIX-033 (b)). 공개 기간(~11-19) 중 로그인한 사용자가 큰 본문을 반복해 보낼 수 있으니, `ChatIn.utterance` `max_length` 또는 Caddy `request_body` 상한을 **사용자 결정으로** 정할지 U7(배포 반영) 전에 한 번 물을 것.
- **[권고] R-5 registry·03-log 마무리(메인 몫).** `registry.md` 에 `app/chat/history.py`(`append`·`recent`·`HISTORY_*`)·`ChatHistoryItemOut`·`GET /chat/history` 행이 아직 없다(구현자 메모의 "registry 새 행 후보"). 커밋 때 함께 올릴 것. 03-log "U4 구현 메모(초안)" 는 커밋 항목으로 옮길 것.

범위 밖 참고(하네스): `.claude/scripts/bash_write_check.py:1228`(B007)·`findings.py:129,130,163`(DTZ005·F541)은 CI ruff 범위 밖의 기존 경고다. U4 와 무관.

## 5. 결론

판정: **통과**. 계정 격리·트랜잭션·프론트 계약·읽기 전용·401·security §5 에서 계약 위반을 찾지 못했고, 구현자 변이 23종에 더해 내 변이 11종이 전부 저장소 시험에 잡혔다. U3b R-10·R-11 과 U6 R-6 은 이 단위에서 닫혔다. 커밋 가능.
