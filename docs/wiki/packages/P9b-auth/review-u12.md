# P9b-auth U12 커밋 전 코드 리뷰 — MCP 백엔드(리비전 0005 `mcp_tokens` · `/auth/mcp-token` 3개 · `/mcp` Bearer 인증 · 읽기 전용 도구 4개 · `MCP_ENABLED` · Caddy·compose) (CR-008 축소안 · D19)

검토자: verifier (fable) | 일시: 2026-11-17 23:53 | 대상: dev2 HEAD `1be2cf4` + 미커밋 작업 트리 중 U12 파일(새 파일 10 · 고친 파일 20)
결과: 통과
판정: **통과**. 열린 [필수] 0 · 열린 [권고] R-1~R-8.
범위 밖(보지도 판정하지도 않음): `web/`(U13 — `review-u13.md`) · 리뷰 도중 작업 트리에 새로 나타난 `docs/RUNNING.md`·`docs/user-setup/15-mcp-connect.md`·`u8-demo-script.md`(U14 문서) · `.env.example` 본문(열지 않았다 — `tests/test_deploy_files.py` ⑲ 의 두 단언으로만 판단) · Docker 이미지 빌드·Caddy 실물 동작·실제 Claude Code 연결(U14).

## 1. 본 것

- 계약: `01-plan.md` 개정 4 — "API 계약 — 개정 4"(231~243행) · "도구 계약 — 개정 4"(245~264행) · U12(528~587행, 닫힌 목록 M1~M11 · 변이 V12-1~20) · 고치는 파일 표(173~182행) · 결정 AI~BB(737~760행). `decisions/D19-mcp-read-token.md` 전문("코드에서 지켜야 할 것" 1~8). `specs/S3.1` 0005 보충(43~50행). `security.md` 17·71행. `02-plan-verify.md` R6-1(200행 — `list_briefings` 는 `trace_id` 를 뺀 것으로 읽었다).
- 변경: 새 제품 파일 6개 전문(`alembic/versions/0005_mcp_tokens.py` 50행 · `app/auth/mcp_tokens.py` 82행 · `app/mcp_server/{__init__,tools,auth,server}.py` 13·99·101·187행) · `git diff -- app/ scripts/ Caddyfile docker-compose.prod.yml requirements.txt` 전부 · `git diff -- tests/` 전부(삭제 줄 포함) · 새 시험 `tests/test_mcp_server.py` 전문(597행), `test_mcp_tokens_api.py`·`test_mcp_tools.py`·`test_migration_0005.py` 는 함수 목록 전부와 해시·격리·재발급·로그·원문 표식·import 금지 시험 본문.
- 주변: `app/db/session.py` `get_session`(78~95행 — 정상 종료 시 commit) · `app/api/read.py` import 줄(44~48행)과 `list_briefings` 의 `trace_id` · `app/api/schemas.py` `BriefingRecordOut` · `scripts/schema_check.py` `EXPECTED_TABLES`(47행 — `Base.metadata` 에서 파생) · `tests/test_migration_0003.py` 292~312행 · `tests/test_briefing_scheduler.py` 의 lifespan 시험 위치.
- 구현자 증거(출력만): `evidence/20261117-23{22..40}-u12-*.txt` 22개 — `pytest-before`(2651) · `pytest-all`(2759) · `mutations`(35건 전부 "잡힘") · `live-client` · `pip-freeze-before/final` · `mypy-final` · `ruff-final` · `check` · `schema-check` · `tools-check` · `forbidden-imports` · `scope`.

## 2. 직접 실행한 명령과 결과

| 명령(접두 `python3 .claude/scripts/save_evidence.py P9b-auth <이름> --`, DB 가 필요한 것은 `POSTGRES_PORT=5433`) | 결과 | evidence |
|---|---|---|
| `.venv/bin/python -m pytest -q` | **2759 passed** · 실패 0 · skip 0 (구현자 증거와 같다. 시작 전 2651 + 새 108) | `20261117-2346-u12-review-pytest-all.txt` |
| `.venv/bin/python -m ruff check app tests scripts evaluation` | `All checks passed!` | `20261117-2347-u12-review-ruff.txt` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` | `20261117-2347-u12-review-mypy.txt` |
| `.venv/bin/python -m alembic check` | `No new upgrade operations detected.` | `20261117-2347-u12-review-alembic-check.txt` |
| `.venv/bin/python scripts/schema_check.py` | 전부 PASS · `alembic_version -> 0005` | `20261117-2347-u12-review-schema-check.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` (툴 7종 불변) | `20261117-2347-u12-review-tools-check.txt` |
| 변이 대조군 + 변이 10건(`…/u12-review/mutate.py`) | 대조군 114/114 · 검출 4 · **생존 6** (아래 표) | `20261117-2348-u12-review-mutations.txt` |
| 탐침 6건을 무변이 구현과 생존 변이 6건에 실행(`…/u12-review/probe.py`) | 무변이 6/6 통과 — 구현은 여섯 경우 모두 옳게 동작. 생존 변이 중 R2·R3·R5·R7·R10 은 탐침이 검출, R16 은 탐침 뒤에도 생존 | `20261117-2351-u12-review-probes.txt` |

변이·탐침은 스크래치패드 사본 `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/u12-review/copy/` 에서만 했다(`app`·`tests`·`alembic`·`scripts` + 설정 5파일, `.env*` 제외 패턴으로 복사, 실행 뒤 사본 삭제). 실행기 `…/u12-review/mutate.py`, 탐침 `…/u12-review/test_probe_verifier.py`·`probe.py`. 실행마다 `import app` 위치가 사본임을 출력으로 확인했다. 대상 시험은 `test_mcp_tokens_api`·`test_mcp_tools`·`test_mcp_server`·`test_auth_required_routes`·`test_briefing_scheduler`(롤백 픽스처 — 시험 DB 에 행이 남지 않는다). 서버를 띄우지 않았고(:8000 의 사용자 백엔드 PID 31961·65209 는 리뷰 전후 그대로), 배포 서버에 요청을 보내지 않았다. 리뷰 뒤 `git status --short` 에서 내가 더한 것은 `evidence/…u12-review-*.txt` 8개와 이 문서뿐이다. 탐침·변이에 쓰인 토큰은 시험 안에서 만들어져 롤백됐고 어느 출력에도 실리지 않았다.

### 변이 표 (구현자가 돌리지 않은 것만 골랐다)

| # | 변이 | 결과 | 잡은 시험 / 비고 |
|---|---|---|---|
| R1 | `user_id_for_mcp_token` 이 해시를 비교하지 않음(아무 Bearer 값이나 통과) | 검출 — 6 failed | `test_unknown_token_is_401` 외 5 |
| R2 | `mcp_token_status` 가 계정으로 거르지 않음(id 가 가장 작은 행) | **생존** → 탐침 P1 이 검출 | 시험 ⑧ 은 A 가 먼저 발급한 뒤 A 의 화면만 본다 — "가장 먼저 만든 행" 을 돌려주는 변이와 구별되지 않는다 → R-1 |
| R3 | 도구가 사용자 id 를 못 읽으면 고정 계정으로 내려감(R5-1 위반) | **생존** → 탐침 P3 이 검출 | `_read_user_id` 단위 시험만 있고 `_invoke` 의 "조회하지 않고 `internal_error`" 갈래를 지나는 시험이 없다 → R-2 |
| R5 | 재발급 upsert 가 `expires_at` 을 새로 쓰지 않음 | **생존** → 탐침 P2 가 검출 | 시험 ④ 는 응답의 `expires_at` 만 본다(행 값이 아니다) → R-1 |
| R6 | `revoke_mcp_token` 이 계정으로 거르지 않음(전부 삭제) | 검출 — 1 failed | `test_delete_and_get_are_scoped_to_the_logged_in_account` |
| R7 | 세션 관리자가 있으면 브리핑 스케줄러를 시작하지 않음 | **생존** → 탐침 P4 가 검출 | 두 스위치가 함께 켜진 lifespan 시험이 없다(운영 compose 는 둘 다 켠다) → R-3 |
| R10 | 래퍼가 `last_used_at` 갱신을 commit 하지 않음 | **생존** → 탐침 P5 가 검출 | 시험은 같은 세션을 공유해 flush 만으로 보인다. 실 서버 왕복(구현자 `u12-live-client` 의 `last_used_at set= True`)이 유일한 증거 → R-2 |
| R15 | `GET /auth/mcp-token` 에 `no-store` 없음 | 검출 — 2 failed | ⑤ 두 시험 |
| R16 | 래퍼가 다른 헤더(`x-mcp-token`)도 자격으로 받음 | **생존**(탐침 P6 뒤에도 — P6 은 다른 헤더 이름 넷을 본다) | 임의 헤더 이름을 전수로 막는 시험은 만들 수 없다. `auth.py:48` 한 곳이 `b"authorization"` 만 읽는 것을 코드로 확인 — 소견 아님 |
| R17 | 브리핑 결과에 계획에 없는 키를 덧붙임 | 검출 — 1 failed | `test_list_briefings_equals_read_dump_without_trace_id` |

구현자 변이 35건(V12-1~18·20 + 추가 15)은 증거 `20261117-2338-u12-mutations.txt` 에서 전부 실패 ≥ 1. V12-19(downgrade 가 테이블을 남김)는 계획대로 실행하지 않았고 코드로 확인했다(3절 6항).

## 3. 판정 근거 (요청 항목 순서)

1. **API 계약·토큰 저장**
   - `POST /auth/mcp-token`(`app/auth/routes.py:271~282`): `Depends(current_user)` · `status_code=201` · `issue_mcp_token` → `session.commit()` → `Cache-Control: no-store` → `{token, created_at, expires_at}`. 계획 241행의 순서 ①~⑥ 그대로. `expires_at = now + timedelta(days=MCP_TOKEN_DAYS)`(`mcp_tokens.py:28`), `MCP_TOKEN_DAYS = 7`.
   - `GET`(285~293행): 키 4개 모델(`McpTokenStatusOut` — `token` 필드 자체가 없다) · `no-store` · 행 없음 → null 셋 · `active = expires_at > now`. `DELETE`(296~302행): 204, 행이 없어도 204. `DELETE` 는 라우트에서 commit 하지 않지만 `get_session`(`app/db/session.py:90`)이 정상 종료 시 commit 한다 — 로그아웃 등 기존 라우트와 같은 방식.
   - 해시만: `token_hash=hash_token(token)`(`mcp_tokens.py:31`), 모델·리비전에 원문 컬럼 0. 시험 ③ 이 행의 여섯 컬럼 값 어디에도 원문이 없음을 본다. 계정당 1개: `UniqueConstraint("user_id")` + `ON CONFLICT ON CONSTRAINT uq_mcp_tokens_user_id DO UPDATE`(36~44행 — `token_hash`·`created_at`·`expires_at`·`last_used_at=None` 넷 다 덮어쓴다, 탐침 P2).
   - 만료 경계: 조회 `McpToken.expires_at > now`(55행) · 상태 `row.expires_at > now`(72행). 같은 순간은 만료 — `test_expired_token_is_401_but_one_second_before_is_ok`·`test_get_expiry_boundary_…` 가 양쪽을 박는다.
   - `/mcp` 401(`app/mcp_server/auth.py:36~41`): 본문 `{"detail":{"code":"unauthenticated"}}` + `WWW-Authenticate: Bearer`, 이유 구별 없음. 인증 순서 ①~⑥ 이 44~56·88~101행과 글자 그대로(첫 `authorization` 값 · `partition(" ")` · `scheme.lower() != "bearer"` 또는 빈 값 → DB 0 · `hash_token(value.strip())`). `auth.py` 에 `cookie`·`query_string` 을 읽는 코드 0. 유효 토큰을 쿠키 값·`X-MCP-Token`·`X-Api-Key`·`Proxy-Authorization` 에 실어도 401, `HEAD /mcp` 401(탐침 P6).
   - 정확 경로: `Route("/mcp", endpoint=<BearerAuthApp 인스턴스>, methods=[GET, POST, DELETE])`(`app/main.py:142`) — `POST /mcp` 200, `Location` 없음(시험 ④). 기존 라우트는 Bearer 를 자격으로 받지 않는다(`test_bearer_header_is_not_a_credential_for_other_routes`).
2. **도구 4개**
   - 읽기 전용·LLM 0: `tools.py` 는 `read.list_persons`·`read.get_person_card`·`read.list_briefings` 셋만 부른다(새 SQL 0, commit 0). `server.py:123~128` 은 세션을 열고 읽고 닫는다. 행 수 불변 시험이 `tools`·`server` 양쪽에 있다(11개 표).
   - `raw_utterance`·닉네임 0: 읽는 모델에 그 필드가 없고 `test_no_tool_result_contains_raw_utterance_or_nickname` 이 표식 문자열로 본다(구현자 V12-9 검출). `trace_id` 0: `tools.py:96` 이 키를 뺀다(R5-7 · R6-1 해석과 같다. 구현자 V12-22·내 R17 이 양쪽 방향을 검출).
   - 격리: 사용자 id 는 `scope["state"]` 에서만 온다(`auth.py:100` → `server.py:85~92`). 도구 입력 스키마에 `user_id`·`username` 0(시험 ⑤). 두 토큰을 세 번 번갈아 부르는 시험과 남의 `person_id`·`schedule_id` → `not_found` 시험이 있다. 사용자 id 를 못 읽으면 `server.py:119~121` 이 세션을 열기 전에 `internal_error` 를 돌려준다 — 탐침 P3 에서 네 도구 모두 세션 팩토리 호출 0 회.
   - import: `app/mcp_server/*.py` 에 `app.tools`·`app.agent`·`app.er`·`app.briefing`·`app.embedding`·LLM SDK import 0(`test_mcp_server_modules_do_not_import_…`, 구현자 `u12-forbidden-imports` exit 1). `tools_check` 7/7.
   - 표시·문구: `readOnlyHint=true`·`destructiveHint=false`·`idempotentHint=true`·`openWorldHint=false`, 제목 넷·설명 넷이 계획 249~261행과 글자 그대로(`server.py:50~69`, 시험 ⑤ 가 값으로 단언).
3. **`mcp_enabled()`** — `app/settings.py:570~595`: 없음·빈 값·`"0"`·`"false"` → `False`, `"1"`·`"true"` → `True`, 그 밖(`yes`·`TRUE`·`on`·`2`·` 1`) → `InvalidValue`. `_register_mcp`(`main.py:134~137`)가 꺼져 있으면 바로 돌아가고 SDK import 는 그 뒤 지연 import 한 줄뿐. 새 인터프리터에서 `import app.main` 뒤 `sys.modules` 에 `mcp*` 0(시험 ①). 꺼진 앱은 `app.state.mcp_session_manager` 가 없어 `_lifespan` 이 빈 `AsyncExitStack` 을 지난다.
4. **`_lifespan`(AsyncExitStack)** — `main.py:198~213`. 관리자가 없으면 스택에 아무것도 넣지 않으므로 이전 코드와 같은 순서(작업 시작 → `yield` → 취소·대기)다. `test_briefing_scheduler.py` 의 기존 lifespan 시험이 2759 안에서 그대로 통과한다. 두 스위치가 함께 켜진 경우는 탐침 P4 로 확인했다 — 순서가 `manager-open → scheduler-start → scheduler-cancelled → manager-close` 이고 작업은 lifespan 동안 살아 있다가 취소된다(계획 539행 "세션 관리자 열기 → 브리핑 작업 시작, 종료는 역순"). 이 조합을 고정하는 시험은 저장소에 없다(R-3).
5. **토큰이 남는 곳** — `app/` 에서 토큰 원문이 지나는 곳은 `issue_mcp_token` 의 반환값, 201 응답 본문, `_bearer_token` 의 반환값, `hash_token` 인자뿐이다. 로그 호출은 `server.py` 의 `mcp_tool name= user= items=` 네 곳뿐이고 인자 값·토큰이 들어가지 않는다(시험 ⑧ · ⑩, 구현자 V12-14a/b 검출). 예외 메시지에 토큰 0. 구현자 증거 22개에서 43자 URL-safe 문자열이 든 줄은 6줄이고 전부 시험 함수 이름이다(`…::test_initialize_reports_server_name_relmemo` 등). `Bearer <값>` 꼴 0줄. `u12-live-client` 는 `token: set (len 43 )` 과 `토큰 값이 출력에 나온 횟수: 0` 만 남겼다.
6. **리비전 0005** — upgrade 는 `op.create_table` 하나(두 UNIQUE·FK CASCADE·PK), `DELETE`·`UPDATE`·`TRUNCATE` 0, 별도 인덱스 0. downgrade 는 `op.drop_table("mcp_tokens")` 한 줄. `test_migration_0005` ③(행 수 불변)·⑦(0004 로 내린 뒤 테이블 없음·`users` 그대로·다시 올리면 빈 테이블)이 2759 안에서 통과. 구현자 `dev-before/after-counts` 가 개발 DB 행 수 불변을 남겼다. `alembic check` 무변경.
7. **닫힌 목록 밖 시험 수정 1건(`tests/test_migration_0003.py:301~302`) — 받아들인다.**
   - 단언은 "head 까지 올린 DB 에서 `users` 를 가리키는 FK 전체" 를 **정확 일치**(`==` 목록)로 본다. 0005 가 `mcp_tokens → users` FK 를 더하면 이 목록은 반드시 한 줄 늘어야 한다. 더한 줄은 테이블·제약 이름·`confdeltype='c'` 를 모두 박는다 — 느슨해진 것이 아니라 한 줄 더 조인 것이다. 같은 함수의 뒷부분(`persons`·`push_subscriptions`·`pending_questions` 에는 `users` FK 0 — 결정 O)은 바뀌지 않았다.
   - 근거 카드: `specs/S3.1` 50행 "`users` FK 는 `auth_sessions`·`chat_messages`·`mcp_tokens` 세 곳(FK 총 9)". M3·M8 과 같은 종류의 카드 반영이다.
   - 계획의 잘못: 557행이 `tests/test_migration_0003.py` 를 "깨지지 않음을 확인한 것" 에 넣었다 — grep 패턴이 이 단언(FK 이름 목록)을 잡지 못했다. 절차상으로는 541행 "목록 밖 시험이 깨지면 멈추고 보고" 에 해당했고, 구현자는 시험 주석에 "계획 목록 밖 수정, 03-log 보고" 라고 적었으나 `03-log.md` 에 U12 절이 아직 없다(R-4).
8. **`read.PersonNotFound`·`read.ScheduleNotFound`** — D19 지킬 것 5 의 문장은 "`app.tools`… 를 import 하지 않는다(조회는 `app.api.read` 를 통해서만 — `grep -rnE` 판정)" 이고, 계획 536행은 `tools.py` 가 `PersonNotFound`·`ScheduleNotFound` 를 잡으라고 이름으로 지정한다. 두 요구를 함께 채우는 길은 `app.api.read` 가 이미 들고 있는 같은 클래스 객체를 쓰는 것이다(`read.py:48`). 규칙의 뜻(툴 7종·에이전트 루프를 MCP 에서 부르지 않는다)에 어긋나지 않는다 — 맞다. 다만 `read.py` 가 그 import 를 정리하면 `AttributeError` 가 되고, 이는 `except` 절에서 터져 `internal_error` 로 가려진다(R-5).
9. **계획에 없는 것** — 새 상수는 계획의 다섯(`MCP_TOKEN_DAYS`·상한 셋·`mcp_enabled`)뿐. 정렬·상한·필터 추가 0(`tools.py` 는 `list_persons` 순서 그대로 자른다). 계획에 글자로 없는 것은 넷이고 모두 동작을 넓히지 않는다: ① `auth.py:89` `scope["type"] != "http"` 조기 반환(닿지 않는 방어) ② `server.py:120` 사용자 id 가 없을 때의 로그 `user=-`(계획은 `<user_id>` 만 적었다) ③ `structured_output=False` + 도구가 직접 `CallToolResult` 를 만드는 방식(SDK 가 `ToolError` 문구를 감싸서 — "텍스트는 코드 문자열 하나뿐" 을 지키려는 것) ④ `main.py:138~139` 시계가 `app.dependency_overrides` 를 요청 시점에 읽는 것(계획 242행 "시험이 덮어쓸 수 있게 래퍼에 주입"). ②③④ 는 03-log 에 적을 것(R-4).
10. **배포 파일** — `Caddyfile`: `handle /mcp { reverse_proxy backend:8000 }` 가 `handle_path /api/*` 뒤·정적 `handle {` 앞, 와일드카드·`handle_path` 0(`test_deploy_files` ⑱, 구현자 V12-13 검출). `docker-compose.prod.yml`: `backend.environment` 에 `MCP_ENABLED: ${MCP_ENABLED:-1}` 한 줄 + 주석, 서비스·포트·볼륨 diff 0(⑲). `requirements.txt`: 주석 3줄 + `mcp==2.3.0` 한 줄, 기존 줄 변경 0. `pip freeze` 전후 차이는 추가 6줄(`mcp`·`mcp-types`·`opentelemetry-api`·`PyJWT`·`python-multipart`·`sse-starlette`)뿐이고 기존 고정 버전이 바뀐 줄 0 — 계획 529행 "기존 고정 줄을 바꿔야만 설치되면 멈추고 보고" 에 걸리지 않는다.

## 4. 소견

[필수] 없음.

[권고] (전부 커밋·배포를 막지 않는다. R-4 는 커밋과 같은 때에, 나머지는 평가 뒤 정리해도 된다.)

- **R-1 토큰 API 시험이 놓치는 두 변이** — `tests/test_mcp_tokens_api.py:249~266`(⑧)은 A 가 먼저 발급한 상태에서 A 의 화면만 봐서, 상태 조회가 계정으로 거르지 않고 "가장 먼저 만든 행" 을 돌려주는 변이(R2)가 살아남는다. 같은 파일 125~138행(④)은 응답의 `expires_at` 만 봐서, 재발급이 행의 `expires_at` 을 새로 쓰지 않는 변이(R5)가 살아남는다. 탐침 P1(B 만 토큰이 있을 때 A 의 `GET` 은 null 셋 · 둘 다 있을 때 각자 자기 시각)·P2(재발급 뒤 행의 `created_at`·`expires_at`)에 해당하는 단언을 더하면 닫힌다. 현재 구현은 두 탐침을 통과한다.
- **R-2 `/mcp` 쪽 시험이 놓치는 두 변이** — ① `app/mcp_server/server.py:119~121`(사용자 id 가 없으면 조회하지 않고 `internal_error`, R5-1)을 지나는 시험이 없다 — `tests/test_mcp_server.py:501` 은 `_read_user_id` 만 본다(R3 생존). 탐침 P3(인증 래퍼 없이 안쪽 앱을 직접 불러 네 도구 모두 `internal_error`·세션 팩토리 호출 0)에 해당하는 시험을 더하면 닫힌다. ② `app/mcp_server/auth.py:80` 의 commit 을 빼도 통과한다(R10 생존) — 시험이 한 세션을 공유해서다. 탐침 P5(commit 횟수를 세는 세션)에 해당하는 시험을 더하면 닫힌다. 지금 이 줄을 실제 DB 로 본 증거는 구현자 `u12-live-client` 의 `last_used_at set= True` 한 줄이다.
- **R-3 두 스위치가 함께 켜진 lifespan 시험 없음** — `app/main.py:198~213`. 운영 compose 는 `MCP_ENABLED`·`BRIEFING_SCHEDULER_ENABLED` 를 함께 켜는데, 저장소 시험은 한쪽씩만 켠다. "MCP 가 켜지면 스케줄러가 시작되지 않는" 변이(R7)가 살아남는다. 탐침 P4 로 현재 구현의 순서(열기 → 시작 → 취소 → 닫기)가 맞음을 확인했다. 같은 시험을 `tests/test_briefing_scheduler.py` 또는 `test_mcp_server.py` 에 더하면 닫힌다. U14 로컬 Caddy 스모크에서 `mcp_tool` 줄과 브리핑 루프 로그가 함께 보이는지도 한 번 본다.
- **R-4 03-log 에 U12 기록 없음** — `grep -n "U12" 03-log.md` 는 276행 "구현 중" 한 줄뿐이다. 계획 529·538·564행이 03-log 에 적으라고 한 것: SDK 버전·확인 날짜·라이선스(`mcp==2.3.0`·MIT), 설치한 소스의 파일:줄(서버 클래스·무상태 옵션·호스트 검사 끄기 — `server.py` docstring 이 "03-log 에 파일:줄" 이라고 가리키는데 대상이 없다), 통과 수 수식(2651 + 108 = 2759), 결정 AT 로 `scope["state"]` 를 고른 근거. 여기에 **닫힌 목록 밖 수정 1건(`test_migration_0003.py:301~302`, 3절 7항)** 과 3절 9항 ②③④ 를 함께 적는다. 01-plan 541·557행의 목록은 다음 개정 때 M12 로 바로잡는다(architect 몫).
- **R-5 예외 클래스를 `read` 의 속성으로 받는 것은 깨지기 쉽다** — `app/mcp_server/tools.py:81·91`. `app/api/read.py` 가 `PersonNotFound`·`ScheduleNotFound` import 를 정리하면 `except read.PersonNotFound` 평가에서 `AttributeError` 가 나고 `server.py:135` 가 이를 `internal_error` 로 삼킨다. `test_mcp_tools` ③·④ 가 `not_found` 를 값으로 단언하므로 그 경우 시험은 깨진다 — 조용히 넘어가지는 않는다. 다음 단계(P12-mcp)에서 예외 클래스를 `app.tools` 밖 공용 모듈로 옮기는 것을 검토한다.
- **R-6 구현자 증거 `20261117-2336-u12-live-server-log.txt` 가 비어 있다** — 본문이 `/bin/bash: /mcp: No such file or directory`·`manager: command not found` 두 줄이다(`grep -E mcp_tool|/mcp|manager` 의 `|` 가 셸에 먹혔다). 실제 uvicorn 처리기로 `mcp_tool name=` 줄이 나가는지(결정 AW — `uvicorn.error.mcp` 자식 로거)는 이 파일로 증명되지 않는다. pytest ⑧ 은 `caplog` 로 로거 이름·메시지만 본다. U14 로컬 Caddy 스모크의 `docker compose logs backend` 발췌(수용 기준 #27 의 증거이기도 하다)로 메운다 — 패턴은 따옴표로 감싼다.
- **R-7 `DELETE /auth/mcp-token` 의 commit 은 의존성 종료 때 일어난다** — `app/auth/routes.py:296~302` 는 `POST` 와 달리 라우트 안에서 commit 하지 않는다(`get_session` 이 한다). 계획은 `DELETE` 의 순서를 정하지 않았고 기존 라우트와 같은 방식이라 계약 위반이 아니다. "폐기 즉시 무효"(D19 결정 2)를 응답 전에 확정하려면 `POST` 처럼 `session.commit()` 한 줄을 두는 편이 읽기 쉽다.
- **R-8 `/mcp/`(끝 슬래시)** — 탐침 P6 에서 `POST /mcp/` 는 SDK 로 처리되지 않는다(307 또는 404 중 하나 — 어느 쪽인지는 단언하지 않았다). Caddy 가 정확 경로 `/mcp` 만 백엔드로 넘기므로 운영에서는 닿지 않는다. 계약(238행)은 `/mcp` → `/mcp/` 리디렉트만 금지하므로 범위 안이다.

## 5. 이 리뷰가 보증하지 않는 것

- Docker 이미지에서 `mcp==2.3.0` 이 설치·기동되는지, Caddy 를 거친 `/mcp` 왕복, 0004 데이터에서 `0004 → 0005` 올리기(U14 로컬 Caddy 스모크).
- 실제 Claude Code 가 이 서버에 붙는지, CLI 가 `Origin` 을 보내 기존 미들웨어의 403 에 걸리는지(계획 804행 리스크 — U14 사용자 연결이 판정). 구현자의 SDK 클라이언트 왕복(`u12-live-client`)은 출력만 읽었고 다시 돌리지 않았다.
- `.env.example` 의 실제 글자(열지 않았다 — 시험 ⑲ 의 "주석 줄 `# MCP_ENABLED=1` 있음 · 값이 박힌 `MCP_ENABLED=` 줄 없음" 두 단언이 통과한다는 것까지).
- SDK(`mcp` 2.3.0) 내부 동작 — 형 오류 때의 SDK 문구, 무상태 모드의 요청 간 격리는 저장소 시험(두 토큰 교차 호출)이 본 범위까지다.
- 부하·남용: `/mcp` 는 틀린 Bearer 값마다 DB 조회 1회를 하고 요청 수 제한이 없다(계획에 없다 — 공개 기간이 11-19 까지인 점과 함께 다음 단계 판단).
