# P9d-sensitive-guard · U4 커밋 전 코드 리뷰 (review-u4)

검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트
대상: dev2 작업 트리의 U4 미커밋 변경(기준 커밋 `61a5241`) — 제품 코드 `app/settings.py` · `app/api/schemas.py` · `app/auth/deps.py` · `app/auth/routes.py` · `app/api/routes.py` · `app/briefing/scheduler.py`, 새 시험 `tests/test_privacy_notice.py`, 고친 시험·도구 `tests/auth_helpers.py` · `tests/test_auth_api.py` · `tests/test_auth_nickname.py` · `tests/test_auth_availability.py` · `tests/test_auth_origin.py` · `tests/test_auth_helpers.py` · `tests/test_auth_required_routes.py` · `tests/test_briefing_scheduler_users.py` · `tests/test_push_wiring.py` · `tests/test_migration_0006.py` · `evaluation/recognition/probe.py`
작성: 2026-11-22 19:00

결과: 통과

열린 [필수] 0 · [권고] 4(R-1~R-4) · [참고] 8. 통과 판정은 코드·시험에 대한 것이다. 커밋에 같이 들어가야 하는 문서(R-1)는 아래에 따로 적었다.

## 1. 본 것

- 계획: `01-plan.md` U4 항목(172~177행) · 산출물 U4 닫힌 목록(43행) · "값으로 고정하는 계약" 표(49~61행) · VR3 행(72행, 단언 예외 7줄) · VR7 행(75행) · "고정 단언 전수 확인" 표(112~114행) · 판정 표 10·11행 · 단위 공통 회귀(280행) · 리스크 304·306행.
- 카드: `decisions/D20-sensitive-guard.md` 결정 17·21(32·36행)·지킬 것 6(47행)·① 표 #10(72행) · `decisions/D18-login-user-isolation.md` 46행(CR-009 보충)·13행(리비전 0003 이 기존 데이터를 비움) · `specs/S3.6-briefing-push.md` 12행 ① · `specs/S3.4-ask-user-protocol.md` 16행 · CLAUDE.md 인증 단락.
- 코드: `git diff 61a5241 -- app evaluation tests` 전부, `tests/test_privacy_notice.py` 전부(504행), `app/briefing/scheduler.py` 전부, `app/auth/routes.py` 가입·로그인·재고지 함수, `app/db/session.py::get_session`(요청 끝 commit), `app/auth/sessions.py::find_user_by_token`(읽기만), `app/api/deps.py::get_notifier`, `app/auth/origin.py`(메서드 기준 미들웨어), `alembic/versions/0003_*.py` upgrade ①.
- 구현자 증거: `evidence/20261122-18{00,01,02}-u4-*.txt` 11개(참고만 — 핵심은 §2·§3 에서 다시 실행). `…-1759-u4-migration-snapshot-mutations.txt` 는 구현자가 무효라고 밝힌 첫 실행이라 보지 않았다.

## 2. 직접 실행한 명령과 결과

증거는 전부 `docs/wiki/packages/P9d-sensitive-guard/evidence/`. 저장소 파일은 고치지 않았다. 로컬 DB 는 `docker ps` 로 `capstone2-postgres-1`(5433, healthy) 확인.

| 무엇 | 명령 | 결과 | 증거 |
|---|---|---|---|
| **전체 pytest** | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2798 passed · 실패 0 · skip 0**(기준선 2778 + 새 시험 20 — 구현자 수치와 같음) | `20261122-1852-verifier-u4-full-pytest.txt` |
| U4 판정 `u4-notice` | `… pytest tests/test_privacy_notice.py tests/test_auth_required_routes.py -q -rs` | **32 passed** | `…-1853-verifier-u4-notice.txt` |
| U4 판정 `u4-auth` | `… pytest tests/test_auth_api.py tests/test_auth_nickname.py tests/test_auth_availability.py tests/test_auth_origin.py tests/test_auth_helpers.py -q -rs` | **237 passed** | `…-1853-verifier-u4-auth.txt` |
| U4 판정 `u4-scheduler` | `… pytest tests/test_briefing_scheduler.py tests/test_briefing_scheduler_users.py tests/test_push_wiring.py tests/test_commit_boundaries.py -q -rs` | **31 passed** | `…-1853-verifier-u4-scheduler.txt` |
| 범위(시험·도구) | `git diff --stat 61a5241 -- tests scripts evaluation` | 추적 파일 11개 = VR3 닫힌 목록 10개 + `tests/test_migration_0006.py`(N-1). `scripts/` 변경 0 | `…-1853-verifier-u4-test-diff.txt` |
| 범위(그 밖) | `git diff --stat 61a5241 -- app/er reports data alembic web` | 출력 없음(변경 0) | `…-1853-verifier-u4-diff-other.txt` |
| ruff | `.venv/bin/python -m ruff check app tests scripts evaluation` | All checks passed | `…-1853-verifier-u4-ruff.txt` |
| tools_check | `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` | `…-1853-verifier-u4-tools-check.txt` |
| mypy | `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)`, exit 0. `scripts/mypy_baseline.txt` 는 diff 에 없음. U4 가 고친 6파일에서 나는 오류는 `app/api/routes.py:471`(`_VapidPartial` — U4 가 건드리지 않은 `get_vapid_public_key`) 1건뿐(N-7) | `…-1854-verifier-u4-mypy.txt` |
| **변이 19종 + 대조군** | `python3 <스크래치패드>/vu4/run_vu4.py`(저장소 사본에서만 치환) | §3 — 17 잡힘 · 2 통과(R-3) | `…-1855-verifier-u4-mutations.txt` |
| **U3 R-2 변이 재실행** | `bash <스크래치패드>/vu3/run_muts.sh control upgrade_touch_updated_at upgrade_touch_created_at upgrade_touch_briefed` | §3 — U3 때 통과하던 2종이 이제 실패 | `…-1859-verifier-u4-r2-mutations.txt` |
| 시험 전용 DB 복구 | 0003~0006 시험 재실행 + 상태 조회 | **46 passed** · `relationship_test_mig` version 0006·새 컬럼 6·민감 행 0·CHECK 4개 문장 그대로 | `…-1859-verifier-u4-restore-migtests.txt` · `…-1859-verifier-u4-restore-state.txt`(변이 전: `…-1859-verifier-u4-mig-state-before.txt`) |
| 개발 DB(읽기 전용) | `users` 행이 없는 `persons.user_id` 개수 등 | `persons` 4 · 계정 없는 인물 **0** · 계정 없는 푸시 구독 0 · `users` 12 · 고지 NULL 12 | `…-1858-verifier-u4-dev-orphans.txt` |
| 가입 동의 값 처리 | `SignupIn.model_validate_json` 에 15가지 값(DB·네트워크 0) | §4 표 → R-2 | `…-1858-verifier-u4-coerce.txt` |

개발 DB 는 읽기만 했다(행 수는 U3 리뷰 때와 같다 — persons 4 · users 12). 변이가 건드린 DB 는 `relationship_test_mig` 하나이고(R-2 재실행), U4 변이 19종은 롤백 세션 시험만 돌려 DB 에 남는 것이 없다. 복구 뒤 행 수(0)와 변이 전 행 수(1)가 다른 것은 마지막에 돈 시험이 달라서다 — 이 DB 는 매 실행 fixture 가 `downgrade base` 부터 다시 만든다(review-u3 N-3).

## 3. 변이 시험 (저장소 무수정)

**U4 계약 — 저장소 밖 사본(`<스크래치패드>/vu4/repo`)에서 소스 한 곳씩 치환.** 대조군 213 passed, 끝에 사본 복원 213 passed · 사본 `app/` 과 저장소 `app/` 차이 없음.

| 변이 | 결과 |
|---|---|
| V1 `chat` 의 `require_notice` → `current_user` | **잡힘** — `test_unconsented_chat_is_403_and_touches_no_llm_no_rows` |
| V2 `submit_answer` 같은 치환 | **잡힘** — `test_unconsented_answers_is_403_then_200_after_notice_accepted` |
| V3 `run_briefings_endpoint` 같은 치환 | **잡힘** — `test_unconsented_briefings_run_is_403_and_composes_nothing` |
| V4 `chat` 에서 고지 의존성을 제안기·판정기·임베더 **뒤로** 옮김(403 은 그대로 나감) | **잡힘** — 같은 시험의 `resolved == []` |
| V5 `/briefings/run` 에서 고지 의존성을 생성기 뒤로 | **잡힘** — 위 시험 + `test_auth_required_routes.py` 2건 |
| V6 `_due_user_ids` 판 번호 조건 제거(조인 유지) | **잡힘** — `notice-null`·`notice-lower-version`·혼합 실행 3건 |
| V7 outer join(계정 없는 인물 포함) | **잡힘** — `[no-users-row]` |
| V8 판 번호 조건을 `IS NOT NULL` 로(낮은 판 통과) | **잡힘** — `[notice-lower-version]` |
| V9 주기 작업 `>=` → `==`(현재보다 높은 판 제외) | **통과(시험 공백)** — 213 passed → R-3 |
| V10 `notice_required` 의 `<` → `!=`(현재보다 높은 판을 미동의로) | **통과(시험 공백)** — 213 passed → R-3 |
| V11 가입 동의 검사를 409 사전 조회 **뒤로** | **잡힘** — `test_signup_check_order_format_then_notice_then_conflict` |
| V12 가입 동의 검사를 닉네임 형식 검사 **앞으로** | **잡힘** — 같은 시험 + `test_422_order_username_then_password_then_nickname` |
| V13 가입 동의 시각을 주입 시계가 아닌 실제 시계로 | **잡힘** — `…records_version_and_time…`(`== T0`) |
| V14 재고지가 현재 판 계정의 시각을 덮어씀 | **잡힘** — `test_reaccept_on_current_version_is_204_and_changes_no_row` |
| V15 재고지 라우트가 `require_notice` 를 요구(미동의는 동의도 못 함) | **잡힘** — 재고지 흐름 3건 |
| V16 스키마를 필수 `bool` 로 | **잡힘** — `[value0]`·`[None]` + 닉네임 시험 2건 |
| V17 스키마를 `bool = False` 로(null 이면 목록 422) | **잡힘** — `[None]` |
| V18 로그인 응답만 `notice_required` 를 False 로 고정 | **잡힘** — `test_login_response_carries_notice_required` |
| V19 `require_notice` 가 403 을 내지 않음 | **잡힘** — 세 라우트 시험 3건 |

**U3 리뷰 R-2 가 닫혔는가 — 런타임 치환(내 U3 플러그인 그대로).** `upgrade_touch_updated_at`(upgrade 뒤 `person_facts.updated_at` 갱신)·`upgrade_touch_created_at`(`events.created_at` 갱신)은 U3 리뷰에서 19 passed 로 통과하던 변이다. 지금은 둘 다 **2 failed, 17 passed** — `test_upgrade_changes_no_existing_data` 가 잡는다(같이 실패하는 `test_downgrade_when_no_sensitive_rows…` 도 같은 스냅샷을 쓴다). 대조군 19 passed, `upgrade_touch_briefed` 는 전처럼 잡힌다. **R-2 는 닫혔다.**

## 4. 판정 근거 — 줄 단위

**미동의 403 의 자리와 순서(`app/auth/deps.py:62~68`, `app/api/routes.py:216·336·436`)**
- `require_notice` 는 `current_user` 를 하위 의존성으로 둔다 — 미로그인이면 `current_user` 가 401 `unauthenticated` 를 먼저 낸다(`test_auth_required_routes.py` 가 세 라우트 포함 전 라우트를 열거해 단언, 32 passed). 로그인했고 미동의면 403 `{"detail":{"code":"notice_required"}}` — 계획 계약 표 "미동의 403" 과 글자가 같다.
- 세 라우트 모두 `user` 가 본문 다음 첫 의존성이라 FastAPI 가 제안기·판정기·임베더·추출기·생성기·알림기보다 먼저 푼다. 시험이 가짜 의존성 생성 자체를 세고(`resolved == []`), 순서를 뒤집은 V4·V5 가 잡힌다. `current_user` → `find_user_by_token` 은 조회만 한다(쓰기 0). 시험이 `agent_traces`·`chat_messages` 행 수 불변, `briefed_at` NULL, 대기 질문 `answer`/`answered_at` NULL 을 단언한다 — D20 #10 "403·LLM 0".
- 세 라우트 밖에 LLM·푸시로 가는 길이 있는지: `run_turn`·`resume_turn` 호출자는 `chat`·`submit_answer` 뿐, `run_briefings` 호출자는 `run_briefings_endpoint` 와 `scheduler._run_for_user` 뿐, `Depends(get_proposer|get_judge|get_embedder|get_fact_extractor|get_briefing_composer|get_notifier)` 는 이 세 라우트에만 있다(`grep -rnE` — §1 코드 목록). 나머지 라우트(`/persons*`·`/events/*/raw`·`/questions/pending`·`/chat/history`·`/briefings`·`/push/*`·`/auth/*`)와 MCP 도구 4개는 읽기·구독 저장뿐이라 OpenAI 전송·푸시 발송이 없다. D20 지킬 것 6("`POST /chat`·`POST /answers/{id}`·`POST /briefings/run` 403 `notice_required`, 주기 브리핑·푸시 건너뜀")의 범위가 빠짐없이 덮였다 → 범위 안 누락 0(N-4).

**가입(`app/auth/routes.py:155~158·166~175`, `app/api/schemas.py:452`)**
- 선택 필드 `bool | None = None` + 라우트 `is not True` 판정 — 계획 계약 표("본문 스키마에서는 선택 필드(`bool | None = None`)로 받고 라우트가 판정한다")와 같다. 없음·`false`·`null` 세 경우 모두 dict 모양 422·`users` 행 수 불변(매개변수 3종).
- 순서: 형식 3종 뒤·409 사전 조회 앞(P3-R3). 모듈 머리 표 7행에 순서가 한 줄로 들어갔다. V11·V12 가 잡힌다.
- `true` 가 아닌 값: 아래 표(증거 `…-verifier-u4-coerce.txt`). pydantic 기본(느슨한) bool 이라 `"true"`·`"yes"`·`"on"`·`"1"`·`1`·`1.0` 이 **동의로 기록**되고, `"abc"`·`2`·`[]`·`{}` 는 FastAPI 기본 422(`detail` 목록)가 나간다. 계획이 고정한 것은 "없거나 `false`" 뿐이라 위반은 아니다 → R-2.

| 본문 값 | 스키마 결과 | 응답 |
|---|---|---|
| `true` | `True` | 201 |
| 없음 · `false` · `null` · `"false"` · `0` | `None`/`False` | 422 `notice_required`(dict) |
| `"true"` · `"yes"` · `"on"` · `"1"` · `1` · `1.0` | `True` | **201 — 동의로 기록** |
| `"abc"` · `2` · `[]` · `{}` | 검증 오류 | 422(`detail` 목록) |

**재고지(`app/auth/routes.py:245~258`)** — `current_user` 만 요구(미동의 계정이 불러야 하므로 옳다, V15), 낮거나 NULL 일 때만 판 번호·시각 기록, 현재 판이면 204·행 무변경(V14). `get_session` 이 요청 끝에 commit 한다. POST 라 Origin 미들웨어(메서드 기준)가 그대로 걸린다. `_EXEMPT` 무변경, `_MUST_REQUIRE_LOGIN` 에 1개(단언 예외 ①).

**주기 작업(`app/briefing/scheduler.py:117~127`)** — inner join + `privacy_notice_version >= PRIVACY_NOTICE_VERSION`. NULL 은 SQL 비교에서 걸러진다(V8 로 낮은 판, V6 로 NULL, V7 로 계정 없는 인물을 각각 확인). VR7 "건너뛴 계정은 `_run_for_user` 에 들어가지 않으므로 `briefing_run` trace 0" — 시험이 생성기 호출 0·발송 0·`briefed_at` NULL 과 함께, 남는 trace 가 표식 실행 1행(`selected == []`)뿐임을 단언한다(N-5). 혼합 실행 시험은 동의 계정만 생성 1·발송 1·trace 1.
- 계정 없는 인물을 건너뛰는 영향: 개발 DB 는 계정 없는 인물 0(§2). 운영은 리비전 0003 이 `DELETE FROM persons` 로 비웠고(D18 13행) 그 뒤 인물은 로그인 라우트로만 만들어지며 계정 삭제 라우트가 없다 — 계획 304행의 전제와 맞다. 운영 DB 를 직접 세어 본 것은 아니다(N-6). 기존 시험은 준비 줄 2곳만 바뀌고 단언은 그대로다.

**고친 기존 단언 = 계획의 7줄뿐인가** — `git diff 61a5241 -- tests` 에서 `assert` 가 바뀐 줄: `test_auth_required_routes.py` `_MUST_REQUIRE_LOGIN` +1(①) · `test_auth_api.py` 키 집합(②)·로그인 사전 비교(④) · `test_auth_nickname.py` 키 집합(③)·로그인(⑤)·me(⑥) · `test_auth_helpers.py` me(⑦). **7줄, VR3 행과 같다.** 나머지는 가입 본문(`privacy_notice_accepted: True`)·계정 준비 줄·import 다. `test_briefing_scheduler.py`·`test_commit_boundaries.py` 는 diff 에 없다.

**`make_user` 기본값 "동의함"(`tests/auth_helpers.py:65`)** — 계획 VR3("`notice_accepted: bool = True` — 기본으로 현재 판 번호·시각을 채움")그대로다. 기본을 False 로 두면 로그인 계정으로 채팅·답·브리핑을 치는 기존 시험이 전부 403 이 되므로, True 가 "로그인한 계정은 쓸 수 있다" 는 기존 시험의 뜻을 보존한다. 미동의 경로는 `test_privacy_notice.py` 가 `notice_accepted=False` 를 명시해 따로 덮고, `test_consented_user_still_passes_the_notice_gate` 가 같은 호출이 동의 계정에서 200 임을 대조한다. 가려지는 의미는 찾지 못했다(주의점 하나는 N-3).

**구현자가 계획에 없이 정한 2가지**
- (a) 동의 시각에 `get_auth_now`: `signup` 은 이미 세션 만료 계산용으로 이 시계를 받고 있고(같은 함수의 `create_session(..., now())`), 운영 값은 UTC `datetime.now(timezone.utc)` 다. 새 의존성을 만들지 않고 시험이 시각을 값으로(`== T0`) 단언할 수 있게 한다(V13). 타당하다.
- (b) `test_briefing_scheduler_users.py` 의 계정 준비를 `_person` 도우미 안 한 줄로: `make_user` 가 멱등이라 계획의 "인물 소유 계정마다 `make_user` 1줄" 과 결과가 같고, 그 파일의 단언은 한 줄도 바뀌지 않았다(diff +2줄 — import·준비). 타당하다.

## 5. 소견

### [필수]
없음.

### [권고]

- **R-1 `tests.md` · `03-log.md` · `registry.md` 에 U4 기록이 없다(커밋에 같이).** `grep -n "U4"` — `tests.md` 0건, `03-log.md` 는 U3 항목의 "다음 단위" 언급뿐, `registry.md` 에 `POST /auth/privacy-notice`·`require_notice`·`PRIVACY_NOTICE_VERSION`·`tests/test_privacy_notice.py` 행 없음. 새 시험 20건(함수 16 — 매개변수 포함 20)과 고친 단언 7줄, 계획에 없이 정한 2가지(§4), `test_migration_0006.py` 스냅샷 확장(U3 R-2 닫음)을 적는다. U3 때(R-1)와 같은 이유로 [필수] 로 올리지 않았지만 U4 커밋에 함께 들어가야 한다.
- **R-2 가입 동의 값이 느슨하게 해석된다(`app/api/schemas.py:452`).** `"true"`·`"yes"`·`"on"`·`"1"`·`1`·`1.0` 이 동의로 기록되고 `"abc"`·`2` 등은 `detail` 이 목록인 422 가 나간다(§4 표). 프론트는 `true` 만 보내므로 지금 깨지는 것은 없지만, 동의 기록의 근거가 "JSON `true`" 하나로 고정돼 있지 않고 이 동작을 붙드는 시험도 없다. 고칠 자리는 둘 중 하나: ① `privacy_notice_accepted: StrictBool | None = None` — 불리언이 아닌 값은 전부 FastAPI 422 로 떨어지고 동의는 `true` 뿐 ② 타입은 두고 `tests/test_privacy_notice.py` 에 지금 동작을 값으로 고정하는 매개변수(`"true"`·`1`·`"abc"`)를 더한다. 어느 쪽이든 U9a 계약(`true` 전송)에는 영향이 없다.
- **R-3 "현재보다 높은 판" 경우의 시험이 없다(변이 V9·V10 통과).** `app/auth/deps.py:59` `version < PRIVACY_NOTICE_VERSION` 과 `app/briefing/scheduler.py:121` `>=` 는 "높은 판 = 동의함" 으로 서로 맞지만, 각각 `!=`·`==` 로 바꿔도 213 passed 다. 판 번호를 올린 배포를 되돌렸을 때만 생기는 상태라 결함은 아니다. 고칠 자리: `tests/test_privacy_notice.py` 에 `privacy_notice_version = PRIVACY_NOTICE_VERSION + 1` 계정 1건 — `/auth/me` `notice_required: false` · `/chat` 200 · 주기 작업이 그 계정 일정을 브리핑.
- **R-4 낡은 설명 3곳(코드 동작과 어긋남).** ① `app/briefing/scheduler.py:22~23` 모듈 docstring "사용자 id 를 `persons.user_id` 에서 구하고(`users` 테이블이 아니다)" — 이제 `users` 를 조인한다(함수 docstring 111~114행은 고쳐졌다). ② `app/api/routes.py` 모듈 docstring 에 세 라우트의 403 `notice_required` 가 없다(`grep -n notice app/api/routes.py` 는 import 와 의존성 4줄뿐). ③ `app/auth/__init__.py:8` 의 `routes` 라우트 나열에 `POST /auth/privacy-notice` 가 없다(이 파일은 U4 파일 목록 밖 — 고치면 범위 판정에 한 줄 메모). ①②는 U4 가 이미 고치는 파일이다.

### [참고]

- N-1 `tests/test_migration_0006.py` 는 VR3 닫힌 목록에 없다. `review-u3.md` R-2 가 "이 커밋이나 다음 단위에서" 로 넘긴 것이고 바뀐 것은 `_SNAPSHOT_SQL` 여섯 문장의 컬럼 목록뿐이다(단언 줄 변경 0). `u4-test-diff` 판정은 "VR3 목록 + 새 시험 + 이 파일" 로 읽는다 — 03-log 에 그 사유를 남긴다(R-1).
- N-2 계획 72행은 `probe.py` "가입 본문 3곳" 이라 적었지만 실제 본문은 `signup()` 함수 한 곳(106~121행)이고 199·258행은 그 함수의 호출이다. 한 곳만 고친 것이 맞다.
- N-3 `make_user` 는 행이 이미 있으면 `notice_accepted` 를 무시하고 기존 행을 돌려준다(`tests/auth_helpers.py:71~73`). `logged_in_client(...)` 를 먼저 부른 뒤 `make_user(..., notice_accepted=False)` 를 부르면 조용히 동의 계정이 된다. 지금 시험은 모두 `make_user` 를 먼저 부르고 상태를 응답으로 다시 확인한다 — 뒤 단위 시험을 쓸 때 순서만 지키면 된다.
- N-4 미동의 계정에 여전히 열려 있는 것: 읽기 라우트 전부 · `GET /questions/pending` · `POST /push/subscriptions`(구독 저장만, 발송은 주기 작업이 건너뜀) · MCP 토큰 발급과 MCP 읽기 도구 4개. 모두 LLM 0·푸시 0 이라 D20 지킬 것 6 의 범위 밖이다. 재고지 모달이 떠 있는 동안 화면이 기록을 읽을 수 있어야 하므로 의도와도 맞다.
- N-5 창 안 일정이 미동의 계정 것뿐이면 대상 0명이 되어 표식 실행(`user_id=""`)의 `briefing_run` trace 1행은 전처럼 1분마다 남는다(P9b 결정 U — 주기 작업 생존 신호). VR7 의 "trace 0" 은 **그 계정의** trace 이고 시험도 그렇게 단언한다.
- N-6 "운영에서는 모든 인물이 로그인 계정 소유"(계획 304행)는 리비전 0003 과 라우트 구조로 뒷받침되지만 운영 DB 를 세어 확인한 것은 아니다. U12 운영 반영 점검에 `SELECT count(*) FROM persons p WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = p.user_id)` 가 0 인지 한 줄 넣으면 닫힌다. 개발 DB 는 `users` 12행이 모두 고지 NULL 이라 이 커밋 뒤 로컬 주기 작업은 재고지 동의 전까지 전 계정을 건너뛴다(기대 동작).
- N-7 mypy 수치: 구현자 증거는 mypy 원출력 `Found 34 errors`, 기준선 도구는 `현재 38건, 기준선 38건` 이다(도구가 세는 범위·방식이 달라 숫자가 다르다). 판정은 도구의 "새 오류 없음"·exit 0 이고 기준선 파일은 바뀌지 않았다.
- N-8 커밋 대상: `tests/test_privacy_notice.py` 는 미추적이라 `git diff --stat` 에 나오지 않는다 — 명시 경로로 `git add` 한다. 작업 트리에 U1 산출물(`evaluation/sensitive_guard/`·`scripts/validate_sensitive_set.py`·`review-u1.md`·`evidence/*-u1-*`)과 메인 세션 문서(`HANDOFF.md`·`journal.md`)가 같이 있다. 이 커밋 뒤 U9a 전까지 로컬 프론트의 가입은 422 `notice_required` 가 된다(`web/src/api/client.ts` 가 세 필드만 보냄) — 운영 반영은 끝난 뒤 한 번(사용자 결정 10)이라 운영 영향은 없다.

## 6. 결론

결과: 통과

- U4 수용 기준(계획 175행) — `_EXEMPT` 무변경·`_MUST_REQUIRE_LOGIN` +1 · 가입 선택 필드와 dict 모양 422·`users` 행 0 · 재고지 재호출 204·행 변경 0 · NULL → `true` → 동의 뒤 `false` → 판 올림 뒤 `true` · 미동의 세 라우트 403·가짜 주입체 생성 0 · 주기 작업 생성 0·발송 0·`briefed_at` NULL·그 계정 trace 0 · 동의 뒤 미만료 칩 답 200 · VR3 — 을 §2 의 직접 실행과 §3 의 변이 17종으로 확인했다.
- D20 ① 표 #10·#11 의 판정 명령(`u4-notice`·`u4-scheduler`) 통과, 전체 2798 passed · skip 0 · ruff · tools_check 7/7 · mypy 새 오류 0.
- U3 리뷰 R-2 는 닫혔다(통과하던 변이 2종이 실패).
- 커밋 전: R-1(문서)·R-4 ①②(같은 파일의 설명)를 같이 넣는다. R-2·R-3 은 이 커밋이나 U5a 앞에서 — 시험 몇 줄이다. `git add` 는 U4 경로만(N-8).
