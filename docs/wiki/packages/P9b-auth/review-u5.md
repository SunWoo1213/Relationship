# P9b-auth U5 커밋 전 리뷰 — 스케줄러·푸시 사용자별, 로그아웃 시 구독 떼기, 고정 사용자 삭제, 발화 길이 상한

검토자: verifier (fable)
일시: 2026-11-16 (HEAD `a25123b` + 미커밋 작업 트리, dev2). Mac 로컬만 판정(Windows CI 는 확인하지 않음).
범위: `git diff HEAD` 의 `app/briefing/scheduler.py`·`app/push/subscriptions.py`·`app/auth/routes.py`·`app/api/schemas.py`·`app/settings.py`·`.env.example`·`.github/workflows/tests.yml`·`tests/test_{api_read_briefings_e2e,chat_history,push_subscriptions,push_wiring}.py` · 새 `tests/test_briefing_scheduler_users.py`·`tests/test_push_endpoint_owner.py` · 삭제 `tests/test_settings.py` · `03-log.md` "U5 구현 메모(초안)" · `tests.md` U5 절. 읽기만: `app/briefing/{select,run}.py`, `app/db/session.py`, `app/api/deps.py`(`get_notifier`), `docker/` 진입점, `web/src/api/client.ts`·`screens/ChatScreen.tsx`, `01-plan.md` U5·결정 J·P·U·V·판정 #4·#6·#12, `S3.6-briefing-push.md` CR-006 보충, `D18` 결정 6·7·지킬 것 5·8, `review-u3b.md` R-2·R-6, `review-u4.md` R-1.

판정: 통과

열린 [필수] 0 · [권고] R-1~R-7(모두 커밋을 막지 않음).

## 1. 직접 실행한 명령과 결과

증거는 모두 `docs/wiki/packages/P9b-auth/evidence/`(`save_evidence.py` 저장). `<SCR>` = `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad`. 시험용 DB 를 새로 만들지 않았고 pytest 를 동시에 돌리지 않았으며, 저장소에는 이 문서와 evidence 밖에 쓰지 않았다.

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2515 passed**, 실패 0, skip 0, exit 0 | `20261116-0126-verifier-u5-pytest-all.txt` |
| 새 시험 2파일 + 기존 스케줄러 시험 | `… -m pytest tests/test_briefing_scheduler_users.py tests/test_push_endpoint_owner.py tests/test_briefing_scheduler.py -q -rs` | 28 passed | `20261116-0129-verifier-u5-pytest-new.txt` |
| ruff·mypy·tools_check·alembic check·고정 사용자 grep·범위·단언 변경 전수 | `bash <SCR>/vu5/static.sh` | ruff(`app tests scripts evaluation alembic`, `--fix` 없음) All checks passed · mypy 새 오류 없음(38/38) · tools 7/7 · `No new upgrade operations detected` · 판정 #4 grep(`app`, `--include='*.py'`) **exit 1** · `tests scripts evaluation .github` grep(`--exclude-dir=__pycache__`) **exit 1** · 대조군: 같은 패턴이 `HEAD` 에서는 7파일 23줄 일치(패턴이 살아 있다) · `git diff HEAD --stat -- app/er app/tools app/agent app/db alembic evaluation reports data web` 빈 출력 · `tests.yml` 0추가 1삭제, `.env.example` 0추가 3삭제 · `tests/test_briefing_scheduler.py` 변경 0 | `20261116-0129-verifier-u5-static.txt` |
| 탐침(변이 없음) + 변이 8종 | `bash <SCR>/vu5/run-mut.sh`(저장소 밖 사본 `<SCR>/vu5/copy`, 롤백형 시험 6파일 + 탐침 `<SCR>/vu5/test_vprobe_u5.py`, 공급자 키 환경변수 제거, 커밋형 시험 제외) | 기준선 142 passed. 변이 8종 **전부 저장소 시험이 잡음** — 3절 | `20261116-0129-verifier-u5-mutations.txt` |
| NUL endpoint 구독 저장 탐침 | `bash <SCR>/vu5/run-nul.sh`(사본) | U5 사본·U5 이전 동작 사본 **둘 다** `DataError`(= 500) → R-4 | `20261116-0131-verifier-u5-probe-nul-subscribe.txt` |
| 시험 DB 잔여 | `.venv/bin/python <SCR>/p9b-u4/residue.py`(읽기만) — 변이 전·후·끝 | 12개 테이블 중 `agent_traces` 밖 전부 0, `agent_traces` 270 → 270 → 270(변이·탐침이 더한 행 0. 270 은 기존 U3b R-7 누적) | `…-0129-…-residue-before.txt` · `…-0130-…-residue-after.txt` · `…-0131-…-residue-final.txt` |

증거 읽는 법 두 가지. ① `…-mutations.txt` 의 "저장소 시험 실패 N건" 숫자는 내 스크립트가 `-s` 로 흘러나온 로그 줄(`ERROR [app.briefing.scheduler] …`)까지 세어 부풀려져 있다(BASE 의 "3건" 은 전부 로그 줄, `pytest exit=0`·142 passed). 판정은 `FAILED tests/…` 줄과 요약 줄로 읽는다. ② `…-static.txt` 의 "그 밖 최상위(참고)" 절 `exit=2` 는 없는 경로를 인자로 준 내 스크립트 탓이다. 같은 grep 을 있는 경로(`.env.example docker-compose*.yml Dockerfile Caddyfile docker infra SERVER-CHECKLIST.md README.md`)로 다시 돌려 exit 1(0줄)을 봤으나 증거 파일로는 남기지 않았다.

**실행하지 않은 것**: 실제 `session_scope()`(사용자마다 커밋)로 도는 운영 경로와 동시 구독 경합은 커밋형 실행이 필요해 돌리지 않았다 — 2절의 해당 판정은 코드 읽기 근거다. Windows CI 미확인.

**검토 도중 작업 트리 변화**: 시작 때 없던 `SERVER-CHECKLIST.md`·`docs/RUNNING.md`·`docs/reliability.md`·`docs/user-setup/11·13`·`docs/wiki/HANDOFF.md` 변경이 검토 중에 나타났다. 내가 쓴 것이 아니고 이 리뷰의 대상도 아니다(읽지 않았다).

## 2. 판정 근거

**1. 확인받을 것 ① — `test_push_subscriptions.py` 단언 변경: 타당(결정 P 의 필연).**
옛 단언 `list_subscriptions(db_session, "user-a") == [first.id]` 는 "같은 endpoint 를 B 가 구독한 뒤에도 A 의 행이 남는다" 이고, S3.6 CR-006 보충 "같은 endpoint 는 마지막으로 구독한 계정 하나에만 묶이고(다른 계정의 같은 endpoint 행은 구독 저장 때 지운다)" 와 양립할 수 없다. 바뀐 시험은 `first.id != second.id`·`user-b == [second.id]` 를 그대로 두고 `second.created is True`·`user-a == []` 를 더했다 — 느슨해진 단언 없음. 격리 자체("남의 구독은 안 나온다")는 바로 위 `test_list_subscriptions_only_returns_own_user` 가 그대로 본다. 다만 계획 문장 "U5 가 고치는 기존 단언은 `tests/test_push_wiring.py:344` 하나" 와는 어긋나므로 03-log 커밋 항목에 이 1건을 남길 것(초안 메모에는 이미 있다).

**2. 확인받을 것 ② — `delete_subscription` 의 NUL·서로게이트 방어: 타당, 범위도 맞다.**
방어를 빼면 `test_logout_endpoint_input_never_causes_a_server_error[\x00]`·`[a\x00b]` 가 500(VM-7). 걸러내는 두 종류는 드라이버가 DB 로 보낼 수 없는 값 그대로다(NUL → `psycopg.DataError`, 짝 없는 서로게이트 → `UnicodeEncodeError`). 더 넓히는 안(로그아웃 본문을 구독 저장 검증처럼 422 로)은 U2 계약 "문자열이면 204" 를 깨므로 맞지 않다. 탐침으로 NUL·10만 자·`not-a-url`·한글 endpoint 다섯 값 모두 204, 세션 행 1개 삭제, 그 뒤 `/auth/me` 401, 구독 행 불변을 확인했다. docstring 의 근거 문장만 사실과 다르다 → R-4.

**3. 스케줄러.**
- **사용자 목록 = 계획 문장과 일치.** `_due_user_ids` 는 `Person ⨝ Schedule` 에 `scheduled_at >= now`·`<= now + lead_hours`·`briefed_at IS NULL`·`DISTINCT` — `select_due_schedules` 기본 모드와 같은 세 조건이다. 모든 사용자를 매분 도는 구현이 아니다(구현자 보고 "`persons.user_id` DISTINCT" 는 출처 테이블을 말한 것). 조인 조건을 항상 참으로(VM-3)·위쪽 끝 제거(VM-5)·목록만 실제 시계(VM-4) 모두 잡힌다.
- **창 상수**: `settings_module.BRIEFING_LEAD_HOURS` 를 `default_run_once` 본문에서 읽어 목록 질의와 `run_briefings(lead_hours=…)` 에 같은 값을 넘긴다(R2-3).
- **실패 격리·롤백**: 사용자마다 `session_scope()` 를 따로 연다 — 예외면 그 세션만 rollback·close 되고 다음 사용자는 새 세션이다. `finally: session.close()` 라 커넥션·`FOR UPDATE` 잠금이 남지 않는다. `begin_nested()` 한 겹은 운영에서 성공 시 세이브포인트 해제, 실패 시 세이브포인트 롤백 뒤 바깥 rollback 이라 결과가 같다(부작용 없음). `run_briefings` 안쪽의 일정별 세이브포인트와 중첩될 뿐이다. 시험은 파이썬 예외·DB 오류 둘 다에서 B 브리핑·A 미브리핑·부분 쓰기 0 을 값으로 본다. DB 오류만 격리에서 빼도(VM-2) 잡힌다. 방향성 한계 → R-1.
- **대상 0명**: 탐침으로 표식 실행이 `agent_traces` 를 **정확히 1행**(`briefing_run`) 늘리고 구독·`briefed_at` 불변임을, 사용자 2명일 때는 `briefing_run` 2행이며 선택 0건짜리 표식 행이 없음을 확인. 기존 `tests/test_briefing_scheduler.py` 는 diff 0 이고 통과 — P9 판정 근거("일정이 없어도 매분 `briefing_run` 1행")가 유지된다.
- **로그**: 사용자 단위 실패는 `logger.exception("… user_id=%s")` 로 남기고 삼킨다. 목록 질의 실패는 여전히 `run_scheduler_loop` 의 루프 수준 로그로 올라간다 — P6 결정과 충돌하지 않는다. 메시지에는 사용자 id 뿐이나 traceback 은 별개 → R-2. 운영에서 alembic 은 별도 프로세스(`docker/` 진입점 `python -m alembic upgrade head` 뒤 `exec … uvicorn`)라 구현자가 본 "로거 꺼짐" 은 시험 환경 한정이 맞다.
- **`default_run_once(now=None)`**: 인자 없이 부를 수 있어 `RunOnce = Callable[[], None]` 과 `start_scheduler_task` 호출이 그대로다(mypy 새 오류 0).

**4. 푸시.**
- 인수 삭제와 upsert 는 같은 세션의 연속 문장이고 커밋은 `get_session` 이 요청 끝에 한 번 — 한 트랜잭션이다. 경합 → R-3.
- A 의 일정 브리핑이 인수된 endpoint 로 가지 않는다(`test_other_accounts_schedule_briefing_is_not_pushed_to_taken_over_endpoint` — `push == "no_subscription"`, 발송 0).
- 로그아웃은 `user_id == 로그인 계정 AND endpoint == 값` 행만 지운다(다른 계정의 같은 endpoint·자기 다른 endpoint 불변 — 저장소 시험 3건). 미로그인 + endpoint 는 401 이고 삭제 0(탐침). 구독을 떼고 세션 삭제를 건너뛰는 변이(VM-6)도 잡힌다.
- `get_notifier` 는 `notifier_from_env(session, user.id, now)` — 시험 2건이 직접 본다(review-u3b R-2·R-6 닫힘). review-u4 R-1(두 번째 답 409 뒤 기록 불변)도 시험이 더해져 닫혔다.

**5. 고정 사용자 제거.** `app` 0줄(exit 1)·`tests scripts evaluation .github` 0줄(exit 1, 허용 주석 2곳도 문구를 바꿔 0). `.env.example` 은 주석+값+빈 줄 3줄 삭제, `tests.yml` 은 한 줄 삭제뿐. `git show HEAD:tests/test_settings.py` 는 `app_user_id` 시험 2건이 전부다 — 다른 설정 시험이 함께 사라지지 않았다. 2515 = 2491 + 26 − 2 로 판정 #12 와 맞는다.

**6. 결정 V.** `ChatIn.utterance` `max_length=2000`. 저장소 시험이 2000 통과·2001 은 422(`loc ["body","utterance"]`, `string_too_long`)·인식 호출 수·`chat_messages`·`agent_traces` 불변을 본다. 422 본문은 기존 빈 발화 422 와 같은 pydantic 목록이다. 프론트는 `client.ts` 가 규약 밖 본문을 `ApiError(422, null)` 로 던지고 `ChatScreen.send()` 의 `catch` 가 `NOTICE.failed` 한 줄을 띄운다 — 깨지지 않는다 → R-5.

**7. 단언 변경 전수.** `git diff HEAD -U0 -- tests` 의 삭제 줄은 주석 2줄 · `test_push_wiring.py:344`(계획 지정) · 위 1번 시험(이름·docstring·단언 1줄) · `test_settings.py` 전체뿐이다. 툴 7종·ER·마이그레이션·프론트 변경 0.

## 3. 변이 (구현자 표 V5-*·VV-* 에 없는 것)

| 변이 | 잡은 저장소 시험 |
|---|---|
| VM-1 첫 실패 뒤 루프 중단(`break`) | 실패 격리 `[python]`·`[db]` — 단 방향 의존, R-1 |
| VM-2 `RuntimeError` 만 격리 | 실패 격리 `[db]` |
| VM-3 목록 질의 조인 조건 항상 참 | 창 경계 · 호출 시점 상수 |
| VM-4 목록 질의만 실제 시계 | 사용자 루프 시험 9건 |
| VM-5 창 위쪽 끝 조건 제거 | 창 밖 · 창 경계 · 호출 시점 상수 |
| VM-6 endpoint 가 있으면 세션 삭제 생략 | `test_auth_api.py::test_logout_204_no_body_clears_cookie_and_deletes_row` |
| VM-7 NUL 방어만 제거 | `test_logout_endpoint_input_never_causes_a_server_error` 2건 |
| VM-8 ctx 사용자를 표식 `""` 로(알림기만 사용자별) | 사용자 루프 9건 + 기존 `test_push_wiring.py::test_scheduler_end_to_end_sends_and_records` |

## 4. 소견

[필수] 없음.

- **R-1 [권고] 실패 격리 시험이 목록 순서에 기대 있다.** `_due_user_ids` 는 정렬이 없는데 시험은 "A 실패 → B 브리핑" 한 방향뿐이다. VM-1(첫 실패 뒤 `break`)에서 내 탐침의 반대 방향(`B` 실패 → `A`)은 **통과**했다 — DB 가 A 를 먼저 돌려줬기 때문에 저장소 시험이 잡은 것이다. 실패 사용자를 `[A, B]` 로 매개변수화하면 순서와 무관해진다.
- **R-2 [권고] 실패 로그의 traceback 에 DB 매개변수 값이 실린다.** 탐침: 메시지에는 없음(`False`), `logger.exception` 이 붙이는 traceback 에는 SQL 매개변수 값이 있음(`True`). HEAD 도 같은 예외를 루프 수준 `logger.exception` 으로 찍었으므로 U5 가 새로 연 노출은 아니고, 계획도 `logger.exception` 을 지정했다. `run_briefings` 가 일정별 오류를 유형 이름으로만 남기므로 여기까지 오는 것은 주로 연결 오류다. 후속으로 엔진 `hide_parameters=True` 를 검토할 것.
- **R-3 [권고] 결정 P 는 동시 요청에 대해 보장되지 않는다(코드 읽기, 미실행).** UNIQUE 는 `(user_id, endpoint)` 뿐이라 A·B 가 같은 endpoint 를 동시에 구독하면 서로의 미커밋 행을 못 보고 두 행이 남을 수 있다(제약 위반은 없다). 한 브라우저는 쿠키가 하나라 실제로는 드물고 다음 구독 저장 때 정리된다. 닫으려면 `endpoint` 단독 유니크(마이그레이션)가 필요해 이 단위 범위 밖이다.
- **R-4 [권고] `delete_subscription` docstring 근거 문장이 사실과 다르고, 그 뒤에 기존 결함이 있다.** "구독 저장 검증 통과 불가" 라고 썼지만 `PushSubscriptionIn` 은 `https://` 접두와 길이만 본다. `https://x.test/\x00` 는 검증을 통과해 DB 에서 `DataError`(500)가 난다 — U5 이전 동작 사본에서도 같다(P7 기존 결함, 로그인 사용자만 도달). 방어의 결론(저장된 행과 일치할 수 없다)은 여전히 맞으므로 문구만 "DB 가 저장을 거부하는 값" 으로 고치고, 구독 저장 500 은 FIX 후보로 올릴 것.
- **R-5 [권고] 2000자 초과 안내.** 계획대로 일반 실패 안내 한 줄이다. 입력창에 길이 제한이 없어 보낸 말풍선은 화면에 남고 새로 고치면 사라진다. 시연 영향 없음.
- **R-6 [권고] `app/auth/routes.py` import 줄 위치.** `from app.push.subscriptions import delete_subscription` 이 `app.db.models` 와 `app.db.session` 사이에 있다(ruff 는 통과 — 정렬 규칙 미적용). 정리만.
- **R-7 [권고] 계획 문장과 다른 단언 변경 1건을 03-log 커밋 항목에 남길 것**(2절 1번).
