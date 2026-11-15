# P9b-auth U3a 커밋 전 리뷰 — 기존 테스트 이관(동작 불변)

검토자: verifier (fable)
일시: 2026-11-15 (HEAD `1cf67cd` + 미커밋, dev2). Mac 로컬만 판정(Windows CI 미확인 — 사용자 지시).
범위: `tests/`(22개 수정 + 새 파일 2개), `03-log.md` "U3a 구현 메모(초안)", `tests.md` U3a 절, `evidence/*u3a*`. `web/` 는 범위 밖.

판정: 보류

보류 사유는 [필수] F-1 하나다(한 줄 이관 누락 + 03-log 의 사실과 다른 문장). 나머지 확인 항목은 전부 구현자 보고와 일치했다.

## 1. 직접 실행한 명령과 결과

증거는 모두 `docs/wiki/packages/P9b-auth/evidence/` (`save_evidence.py` 저장).

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2439 passed**, 실패 0, skip 0, exit 0 (U2 기준 2426 + 도우미 시험 13) | `20261115-2209-verifier-u3a-pytest-all.txt` |
| ruff | `.venv/bin/python -m ruff check app tests scripts evaluation alembic` | All checks passed | `20261115-2210-verifier-u3a-ruff.txt` |
| mypy | `.venv/bin/python scripts/mypy_check.py --run` | 새 오류 없음(38/38) | `20261115-2210-verifier-u3a-mypy.txt` |
| tools_check | `.venv/bin/python scripts/tools_check.py` | 7/7 ok | `20261115-2210-verifier-u3a-tools-check.txt` |
| 동작 불변 | `git diff --stat -- app evaluation reports data scripts alembic` · `git diff --stat 1cf67cd -- app evaluation reports data scripts` | 둘 다 빈 출력 | `20261115-2210-verifier-u3a-app-diff.txt` · `…-app-diff-u2.txt` |
| 테스트 쪽 고정 사용자 | `bash <SCR>/p9b-u3a/u3a-tests-fixed-user.sh`(`--include='*.py'`, R3-2 반영) | exit 0, 일치 10줄 = `test_settings.py` 5줄 · `test_commit_boundaries.py:81,181,293` · 주석 2곳(`test_push_subscriptions.py:90`·`test_api_read_briefings_e2e.py:185`) — 계획 허용 목록과 일치 | `20261115-2210-verifier-u3a-fixed-user.txt` |
| 변이 V3a-1 독립 재현 | 저장소 밖 사본 `<SCR>/vu3a/mut` — `bash <SCR>/vu3a/run.sh` | 기본값 제거(`102: user_id: str`)·함수 정의 0·사본 모듈 경로 확인 뒤 **2393 passed**, 실패 0, skip 0 (구현자 run3 과 같은 수) | `20261115-2212-verifier-u3a-mutation-v3a1.txt` |
| 실패 출력의 토큰 노출 | 사본 도우미 시험 9곳을 일부러 틀리게 — `<SCR>/vu3a/leak_probe.py` | `-vv`: 8 failed, 토큰 모양 문자열 0 · `-vv -l`: 지역변수 `token = '…'` 2회 노출(R-2) | `20261115-2213-verifier-u3a-leak-probe.txt`(값은 가려 저장) |
| 시험 DB 잔여 행 | `<SCR>/p9b-u3a/leftover.py` (전체 pytest 전·후, 변이·실패 시험 뒤) | 세 번 모두 `users 0 · auth_sessions 0 · persons 0` | `…-2209-…-leftover-before` · `…-2210-…-leftover-after` · `…-2352-…-leftover-final` |

`<SCR>` = `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad`. 시험용 DB 를 새로 만들지 않았고 pytest 를 동시에 돌리지 않았다.

## 2. 위임 항목별 판정 근거

1. **동작 불변 — 확인.** 위 diff 2건 빈 출력. `scripts/run_pilot_eval.py:1378-1382` 는 이미 `user_id=f"pilot-eval-{run_id}"` 를 명시한다(이 파일의 마지막 커밋은 `b124c8e` FIX-021 — U3a 이전). 구현자 보고가 사실이고, 계획 문장("같은 값을 명시")은 계획 쪽 사실 오류다(사실 9 가 "기본값에 기대는 1곳"으로 셌다). 03-log 의 "계획 보정" 문단으로 충분하며, 커밋 메시지 정합성 란에 "계획의 `scripts/run_pilot_eval.py` 수정은 이미 명시돼 있어 변경 없음" 한 줄을 넣으면 된다. 계획서 본문은 고치지 않아도 된다(개정 이력 대상 아님 — 범위 축소가 아니라 무변경).
2. **단언 불변 — 확인.** `git diff -U0 -- tests` 를 전수로 읽었다. 22개 파일의 변경은 (가) `ToolContext(` 에 `user_id="local"`(+ 줄바꿈 재배치), (나) `TestClient(app…)` → `logged_in_client(app, db_session…)`·`committed_login`, (다) `app_user_id()` → `"local"`(데이터 준비 4곳 + `test_push_wiring.py:344` 단언 우변 1곳 + docstring 3곳), (라) 그에 따른 import 줄뿐이다. 단언 줄이 바뀐 곳은 `test_push_wiring.py:344` 하나이고 값이 같다(계획 "고치는 기존 파일" 표 U3a 행이 지정한 리터럴화). `"local"` 이 기존 기본값과 같은지: `app/settings.py:107` `DEFAULT_APP_USER_ID = "local"`, `:563` `env.get("APP_USER_ID", DEFAULT_APP_USER_ID)`, 이 셸에서 `app_user_id()` 실행 결과 `'local'`. `APP_USER_ID` 를 설정하는 경로는 `tests/conftest.py`·`pyproject.toml` 에 없고 `.github/workflows/tests.yml:176` 은 스모크용 변수 파일(pytest 작업 아님)이다. AST 스캔(`<SCR>/ctx_scan.py`)으로 `tests scripts evaluation app` 의 `ToolContext(` 69곳 중 `user_id` 누락 0.
   - 부수 변화 1건(단언 아님): `logged_in_client` 기본 `base_url` 이 `https://testserver` 라 13개 파일의 요청 스킴이 http → https 로 바뀐다. 전체 통과로 영향 없음이 확인되지만 03-log 에 없다(R-1).
3. **사고 복구 — 완전.** import 줄 변경은 `TestClient` 삭제 13 · `tests.auth_helpers` 추가 14 · `ExitStack` 추가 1 · `app_user_id` 삭제 2 뿐이다. `git status --short -- tests` 는 수정 22 + 새 파일 2 로 03-log 목록과 같다. 구현자의 되돌림 패치(`<SCR>/p9b-u3a/isort-untouched.patch`, 22개 파일)의 대상 중 지금 diff 가 남은 것은 `tests/test_tools_questions.py` 하나이고 그 diff 는 U3a 의 `user_id="local"` 1줄(+1/-0)뿐이다. `git diff --check -- tests` 통과. (03-log 는 "21개" 라고 적었고 패치는 22개 — 그 1개가 나중에 U3a 가 건드린 `test_tools_questions.py` 라 실질 차이는 없다.)
4. **증거 파일 — 깨끗함.** 남은 `evidence/*u3a*` 에서 쿠키 값·`Set-Cookie`·토큰 모양(40자 이상) 문자열·키 문자열 0(유일한 `API_KEY` 일치는 테스트 매개변수 이름 `…secret_like_key_raises[API_KEY]`). 기본 실행(`-vv`)의 실패 출력에는 토큰이 찍히지 않는다. `-l` 을 붙이면 찍힌다 → R-2.
5. **도우미 — 확인.** `tests/auth_helpers.py:42` 가 `app.auth.sessions.cookie_name`·`create_session` 을 그대로 쓴다(쿠키 이름 하드코딩 없음, 변이 H-1 이 잡음). `/auth/me` 200 으로 실제 로그인 의존성이 그 쿠키를 받아들임을 시험이 본다. `NO_LOGIN_HASH = "!helper-no-login"` 은 `app/auth/passwords.py:88-90`(`parse_hash` 실패 → False)로 `app/auth/routes.py:139-141` 에서 항상 401. `committed_login` 의 정리는 `finally`(157-160행)이고 예외 경로 시험이 행 0 을 값으로 단언한다. 전체 pytest·변이·실패 시험 뒤 `users`·`auth_sessions` 0행.
6. **V3a-1 — 재현됨, 단 보이는 범위가 한정된다.** 2393 passed 는 "`ToolContext` 기본값·`app_user_id()` 에 기대는 테스트가 없다" 를 보인다. **"쿠키 없는 클라이언트가 남지 않았다" 는 보이지 못한다**(라우트가 아직 쿠키를 보지 않으므로). 그 빈칸에서 F-1 이 나왔다.
7. 위 표.
8. U3b 인계 — 아래 4절.

## 3. 소견

### [필수] F-1 — `tests/test_briefing_scheduler.py:197` 이 이관에서 빠졌고, 03-log 의 이유 문장이 사실과 다르다

- 사실: 197행 `client = TestClient(app)` 뒤 199행 `resp = client.post("/briefings/run")`, 200행 `assert resp.status_code == 200`. `/briefings/run` 은 U3b 에서 로그인 필수가 되는 11개 라우트 중 하나다.
- 03-log "로그인 도우미를 쓰지 않은 곳(이유)" 는 이 파일을 "lifespan 시험 — 라우트 호출 없음, `/health` 뿐" 이라고 적었다. 73·94·129·149행은 맞지만 197행은 틀리다. 구현자 증거 `20261115-2157-u3a-testclient-remaining.txt` 목록을 줄 단위로 대조하지 않은 것으로 보인다.
- 계약: 01-plan U3a "API 테스트의 `TestClient` 생성을 `logged_in_client` 로 바꾼다". 이 시험은 `app.dependency_overrides[get_session] = lambda: db_session` 을 쓰는 롤백 픽스처형이라 `logged_in_client(app, db_session)` 한 줄로 끝난다(단언 변경 없음).
- 영향: 지금은 통과하지만 U3b 에서 401 로 깨진다. U3b 계획이 "쿠키 없는 클라이언트로 남은 테스트에 `logged_in_client` 를 쓰는 것은 단언 변경이 아니다" 로 흡수할 수는 있으나, U3a 를 뗀 목적(R-9 — 이관과 계약 변경을 리뷰에서 가르기)과 03-log 의 정확성 때문에 이 단위에서 닫는다.
- 요구: (a) 197행을 `logged_in_client(app, db_session)` 로 바꾸고 전체 pytest 2439 유지 확인, (b) 03-log 그 문장을 "73·94·129·149행은 lifespan 만, 197행은 이관" 으로 고치고 바꾼 파일 수를 23으로, (c) tests.md U3a 절에 반영. 재검증은 `git diff -U0 -- tests/test_briefing_scheduler.py` 와 pytest 한 번이면 된다.

### [권고]

- **R-1** `logged_in_client` 기본 `base_url="https://testserver"` 로 13개 파일의 요청 스킴이 바뀐 것을 03-log 에 한 줄 적는다(동작 불변 주장의 유일한 부수 변화. `Secure` 쿠키가 실리려면 필요하므로 설계는 타당).
- **R-2** `pytest -l`(showlocals)로 `tests/test_auth_helpers.py` 가 실패하면 지역변수 `token` 원문이 출력된다(71행 시험·189행 시험). 저장소 설정·CI 는 `-l` 을 쓰지 않고 토큰은 롤백·정리되는 가짜 세션 것이라 실해는 없다. 구현자가 지운 증거 파일이 이 경로였을 것이다. "도우미 시험 출력은 `-l` 없이 저장" 을 03-log 에 남기거나, 지역변수에 원문을 두지 않게(해시 비교를 도우미 함수 안으로) 바꾸면 닫힌다.
- **R-3** tests.md U3a 표의 증거 이름이 `u3a-pytest-all-final`·`u3a-ruff-final` 인데 03-log 가 말하는 최종은 `…-2205-…-final2`·`…-2206-…-final2` 다. 맞춘다. 도우미 변이 번호가 H-2 → H-4 로 건너뛴다(H-3 을 뺀 이유 한 줄).
- **R-4** `logged_in_client` 의 세션 팩토리 분기는 커밋하고 정리를 호출자에게 맡긴다. 지금 쓰는 곳은 도우미 자체 시험 하나뿐이다. U3b 에서 커밋형은 `committed_login` 만 쓰도록 하고, 쓰이지 않으면 분기를 없애는 편이 잔여 행 위험이 작다.
- **R-5** `tests/test_answer_concurrency.py` 의 `committed_login(…, user_id="local")` 은 공유 시험 DB 에 `users.id="local"` 을 잠깐 커밋한다. 같은 DB 에 동시에 도는 다른 pytest 가 `make_user("local")` 을 flush 하면 PK 충돌이 난다. 지금은 직렬 실행이라 문제없다(잔여 0 확인). 병렬 실행(xdist)을 들일 때 다시 볼 것.

## 4. U3b 인계 4항목 타당성

1. `test_commit_boundaries.py` 3곳을 `with committed_login(app, lambda: Session(bind=db_engine), user_id=user_id)` 로 — 타당. 도우미 서명과 맞고 `Person(user_id=user_id)` 와 로그인 사용자가 일치한다(계획 N-2 ③ 그대로).
2. `db_session.rollback()`·`expunge` 뒤 `users` 행 소실 주의 — 타당하나 현재 해당 없음: `tests/test_api*.py`·`test_memory_loop.py`·`test_push_*.py` 에 그런 호출 0(grep). 예방 문구로 남기면 된다.
3. `test_api_chat.py` DB 오류 시험이 쿠키 조회 뒤에 오류가 나는 구조인지 — 타당. `current_user` 가 같은 `db_session` 으로 세션 행을 읽으므로 U3b 에서 401 이 아닌 기존 기대 상태가 나오는지 실제로 봐야 한다.
4. `X-Session-Id` 를 보내는 6개 파일의 데이터 준비 `session_id` → `chat:<user_id>` — 타당. grep 결과가 정확히 그 6개(`test_memory_loop`·`test_api_chat`·`test_api_answers_resume`·`test_commit_boundaries`·`test_api_chat_query`·`test_api_questions_pending`)이고 계획 닫힌 목록 ②③ 과 맞는다.

추가로 넘길 것: F-1 을 이 단위에서 닫지 않으면 `test_briefing_scheduler.py:197` 이 5번째 항목이 된다. `test_push_devpage.py`(`/push-dev/`)·`test_api.py:117`(`/health`)은 인증 밖이라 그대로 둔 것이 맞다.

## 5. 고치지 않은 것

코드·계획·카드를 수정하지 않았고 커밋하지 않았다. 내가 쓴 것은 이 파일과 `evidence/*verifier-u3a-*`(1차 12개 + 재검토 5개), 저장소 밖 스크래치(`<SCR>/vu3a/`, `<SCR>/ctx_scan.py`)뿐이다.

## 6. 재검토 (F-1 수정 뒤, 2026-11-15 23:56~)

| 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|
| ① F-1 | `git diff -U0 -- tests/test_briefing_scheduler.py` | import 1줄 추가 + 198행 `TestClient(app)` → `logged_in_client(app, db_session)`. 그 밖의 변경 없음(단언 불변) | (diff 직접 확인) |
| ① 추가 누락 | `grep -rn 'TestClient(' tests`(인증 시험·도우미 제외) + `ASGITransport`·`httpx` 클라이언트 grep | 남은 곳: `test_briefing_scheduler.py` 74·95·130·150(lifespan — 이 파일의 `client.get/post` 호출은 199행→이관된 곳 하나뿐) · `test_push_devpage.py:29`(`/push-dev/`) · `test_api.py:117`(`/health`) · `test_commit_boundaries.py:120,239,311`(U3b). 다른 종류의 클라이언트 0. **추가 누락 0** | (grep 직접 확인) |
| ② 도우미 시험 검출력 | 사본 `<SCR>/vu3a/mut2` — `<SCR>/vu3a/recheck.py` | 대조 13 passed · VR-1(쿠키 값을 엉뚱한 문자열로) 4 failed(`…session_row_matches_cookie` 포함) · VR-2(세션 행에 토큰 원문 저장) 5 failed → 고친 `_compare_cookie_with_row`·`_session_row_for_cookie` 가 해시 일치·원문 미저장을 여전히 값으로 잡는다 | `20261115-2357-verifier-u3a-recheck-helper-mutation.txt` |
| ② R-2 | 같은 스크립트 — 토큰을 다루는 시험 3건을 일부러 실패 | `-vv` 토큰 모양 0 · **`-vv -l` 도 0**(1차에는 2회) | 같음 |
| ③ 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | 2439 passed, 실패 0, skip 0 | `20261115-2356-verifier-u3a-recheck-pytest-all.txt` |
| ③ ruff | `.venv/bin/python -m ruff check app tests scripts evaluation alembic` | All checks passed | `20261115-2357-verifier-u3a-recheck-ruff.txt` |
| ④ 동작 불변 | `git diff --stat -- app scripts evaluation reports data alembic` | 빈 출력 | `20261115-2357-verifier-u3a-recheck-app-diff.txt` |
| 시험 DB 잔여 | `<SCR>/p9b-u3a/leftover.py` | `users`·`auth_sessions`·`persons` 0 | `20261115-2357-verifier-u3a-recheck-leftover.txt` |

- `git status --short -- tests` 는 수정 23 + 새 파일 2 로 03-log(80행 "22 → 23개")와 맞는다. 03-log 67행의 이유 문장도 197행을 따로 적도록 고쳐졌다.
- **닫힘**: F-1, R-2.
- **남은 소견(전부 [권고], 커밋을 막지 않음)**: R-1(`base_url` https 전환을 03-log 에 한 줄 — 미확인), R-3(tests.md 증거 이름 `final` → `final2`·H-3 설명 — 미확인), R-4(세션 팩토리 분기는 U3b 에서 `committed_login` 으로 일원화), R-5(`users.id="local"` 커밋은 병렬 실행 도입 때 재검토). 03-log 67·80행의 lifespan 줄 번호(73·94·129·149)는 import 1줄이 늘어 지금은 74·95·130·150 이다(사소).
