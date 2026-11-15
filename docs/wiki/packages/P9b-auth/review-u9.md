# P9b-auth · U9 커밋 전 코드 리뷰 (review-u9)

검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트
대상: dev2 작업 트리의 U9 미커밋 변경 — 고친 14파일(`app/api/schemas.py` · `app/auth/__init__.py` · `app/auth/routes.py` · `app/db/models.py` · `app/settings.py` · `tests/auth_helpers.py` · `tests/test_api.py` · `tests/test_auth_{api,helpers,origin,required_routes}.py` · `tests/test_migration_0003.py` · `tests/test_schema_{check,models}.py`) + 새 5파일(`alembic/versions/0004_users_nickname.py` · `app/auth/names.py` · `tests/test_auth_{nickname,availability}.py` · `tests/test_migration_0004.py`). 프론트 U10(`web/`, HEAD `8b6946f`)은 범위 밖(계약 대조용으로 읽기만).
작성: 2026-11-16 07:31 · HEAD `8b6946f`(dev2)

결과: 통과

열린 [필수](코드) 0 · [필수·기록] D-1 한 건(코드가 아니라 U9 커밋에 같이 넣을 기록 — 채우면 재리뷰 불필요) · [권고] R-1~R-7.

## 1. 본 것

- 계약: `01-plan.md` U9(281~331행 — 모델·리비전·닫힌 목록 B1~B17·새 시험 3파일·변이 V9-1~13·판정) · "API 계약 — 개정 3"(152~165행) · "닉네임 규칙 — 개정 3"(167~181행) · "4차 검증 권고 반영" R4-1·R4-2·R4-4·R4-5·R4-10(392~401행) · "단위 공통 회귀"(433행~). `decisions/D18-login-user-isolation.md` 결정 11("최종 판정은 DB UNIQUE + 가입 시 409 이고 조회는 참고용이다")·지킬 것 10("가입과 조회는 같은 정규화 함수 하나를 쓰고, DB UNIQUE 는 그 함수가 돌려준 값에 건다"). `security.md` §5 CR-007 줄("닉네임은 계정 표시용으로만 저장한다 … `agent_traces`·툴 입력·`pending_questions.context` 에 넣지 않는다", "접근 로그에 조회 쿼리 값(아이디·닉네임 — 비밀 아님)이 남는다").
- 코드: `git diff -- app alembic` 전부, 새 파일 `0004_users_nickname.py`·`app/auth/names.py` 전문, `app/auth/routes.py` 전문, `git diff -U0 -- tests` 전부, 새 시험 3파일 전문, `tests/conftest.py`(`db_session` 롤백 픽스처)·`tests/test_migration_0003.py`(`_mig_env`·`MIG_DB_NAME`)·`app/auth/origin.py`(`UNSAFE_METHODS`). 프론트 계약: `web/src/api/client.ts:189-198`·`web/src/screens/AuthScreen.tsx:142·168`.
- 구현자 증거(출력만): `evidence/20261116-07*-u9-*.txt`(pytest·upgrade·dev 전후 행 수·mypy 2회·mutations).
- 작업 트리: `git status --short` 에서 `docs/wiki` 밖 변경은 위 19파일뿐(리뷰 전후 같음). `docs/wiki/journal.md` 2줄은 U10 커밋·푸시 훅 기록이다.

## 2. 직접 실행한 명령과 결과

증거는 전부 `docs/wiki/packages/P9b-auth/evidence/`. 탐침·변이 파일은 스크래치패드 `…/scratchpad/review-u9/`(`probe_u9.py`·`u9mut.py`·`db_state.py`)에만 두었고 저장소 파일은 고치지 않았다. 새 DB 를 만들지 않았다. 구현자 스크래치패드(`p9b-u9/repo`)는 열지 않았다.

| 무엇 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q` | **2624 passed** · 실패 0 · skip 0(구현자 값과 같음. U5 시점 2515 + 새 3파일 수집 109) | `20261116-0724-review-u9-pytest-all.txt` |
| ruff(검사만) | `.venv/bin/python -m ruff check app tests scripts evaluation` | All checks passed | `…-0724-review-u9-ruff.txt` |
| mypy | `.venv/bin/python scripts/mypy_check.py --run` | 새 오류 없음(38/38). 구현자 첫 실행 `u9-mypy.txt` 는 새 오류 2건 FAIL → `u9-mypy-fixed.txt` 38/38 — 지금 트리는 38 | `…-0730-review-u9-mypy.txt` |
| alembic check | `POSTGRES_PORT=5433 .venv/bin/python -m alembic check` | `No new upgrade operations detected.` | `…-0724-review-u9-alembic-check.txt` |
| schema_check | `POSTGRES_PORT=5433 .venv/bin/python scripts/schema_check.py` | 전부 PASS · UNIQUE 6(`uq_users_nickname` 포함) missing=[] · `alembic_version -> 0004` | `…-0724-review-u9-schema-check.txt` |
| tools_check | `.venv/bin/python scripts/tools_check.py` | 7/7 | `…-0730-review-u9-tools-check.txt` |
| R4-10 | `grep -rln nickname app --include=*.py` | `app/auth/names.py`·`app/auth/routes.py`·`app/db/models.py`·`app/api/schemas.py` 4개뿐 | `…-0724-review-u9-r4-10-grep.txt` |
| ER·툴·에이전트 무변경 | `git status --short -- app/er evaluation reports data app/agent app/tools app/briefing app/llm` | 빈 출력 | `…-0724-review-u9-er-unchanged.txt` |
| 직접 탐침 155건 | `… pytest … scratchpad/review-u9/probe_u9.py` | 155 passed — §3 | `…-0728-review-u9-probe.txt` |
| 변이 6종 + 대조군 3 | `U9_MUT=<이름> … pytest -p u9mut …` | §5 | `…-0728-review-u9-mutations.txt` |
| DB 4개 상태(변이 뒤, SELECT 만) | `… scratchpad/review-u9/db_state.py` | §6 | `…-0729-review-u9-db-state.txt` |

## 3. 볼 것 1~8 판정

**1. 리비전 0004** — `upgrade` 는 `add_column(nullable=True)` → `UPDATE users SET nickname = username WHERE nickname IS NULL` → `alter_column(nullable=False)` → `create_unique_constraint(op.f("uq_users_nickname"))` 네 문장, 삭제문 0. `downgrade` 는 `drop_constraint` → `drop_column` 둘뿐. 모델(`UniqueConstraint("nickname")`·`nullable=False`·기본값 없음)과 일치(`alembic check` 무변경, DB 의 `nickname (is_nullable, default) = ('NO', None)`). 운영 DB 실패 경로: 기존 아이디는 `[a-z0-9_]{3,20}` 이라 백필 값이 서로 다르고(UNIQUE 안전) 닉네임 규칙(2~20자·소문자)도 만족한다 — 찾지 못했다. 잠금: `ALTER TABLE` 이 `users` 에 ACCESS EXCLUSIVE 를 잡지만 backend 컨테이너가 하나이고 기동 전에 도므로 경쟁 상대가 없다. 트랜잭션 DDL 이라 중간 실패는 0003 으로 되돌아간다(구현자 V9-1 증거에서 다음 실행이 복구됨). 개발 DB 실측: 0003·3행 → 0004·3행·`nickname == username` 3(구현자 전후 증거 + 내 `db-state`).

**2. 가입 판정 순서·경합** — 코드 순서가 ①아이디 → ②비밀번호(길이·UTF-8) → ③닉네임 → ④`_exists(username)` → ⑤`_exists(nickname)` → ⑥`begin_nested` INSERT 로 계획과 같다. `IntegrityError` 는 `err.orig.diag.constraint_name` 을 `_CONSTRAINT_CODES` 로 옮기고 없으면 `raise`(구현자 X-reraise 변이가 잡힘). 탐침 `test_409_issues_no_cookie_and_no_session_row`: 사전 조회 409 3종과 경합 409 3종 모두 `Set-Cookie` 0·`auth_sessions`·`users` 행 수 불변, 409 뒤 `/auth/me` 401, 경합 409 뒤 **같은 DB 세션으로 다음 가입 201**(세이브포인트 롤백 뒤 세션 정상). 둘 다 겹친 경합도 `username_taken` 이 나왔다(PostgreSQL 이 먼저 만든 인덱스부터 검사 — 계약은 사전 조회 ④ 가 보장하므로 여기 순서는 참고).

**3. 정규화** — `normalize_nickname` 은 `NFC → strip → fullmatch → lower` 한 함수이고 호출처는 `routes.py` 의 `signup`·`_availability` 두 곳뿐(grep). 아이디는 두 곳 모두 `normalize_username` + `_USERNAME_RE.fullmatch`. `NICKNAME_PATTERN` 리터럴의 바이트는 `eab080`·`ed9ea3`(NFC 의 가·힣)이다(`xxd`). 허용 집합이 ASCII + 완성형 한글이라 `lower()` 뒤에도 규칙을 만족한다(터키어 `İ`·전각 `ＡＢ`·`ⓐⓑ`·결합 문자 `áb` 는 정규식에서 이미 거부 — 탐침). NFC 는 허용 문자에 대해 길이를 늘리지 않는다: NFD `가`×20 → 201, NFD `가`×21 → 422(탐침). 탐침 `test_{username,nickname}_rule_same_in_signup_and_availability`: 25개 입력에서 조회 `invalid` ⇔ 가입 422, 조회 `available` ⇔ 가입 201 → 다시 조회 `taken`. **프론트 전제**(칸 값을 trim 없이 보냄): 닉네임 `" 민지p "`·`"민지q\n"` 는 서버가 지워 201/`available`. 아이디 `" abc_p1 "` 는 가입 422 `invalid_username`·조회 `invalid` — 결정 A("아이디 규칙 변경 없음") 그대로이고 두 경로가 같다(R-4 관찰).

**4. 500 이 0 인가** — 탐침: 가입 세 필드 × 이상 문자열 29종(NUL·제어문자·ESC·짝 없는 서로게이트 3종·100만 자·한글 30만 자·RLO·BOM·결합 문자·전각·터키어·켈빈 기호·공백 10만 + `ab`·SQL 조각 등) = 87건 전부 201/422, 201 이면 저장 값이 규칙 정규식 안. 타입 오류 9종 × 3필드 27건 전부 422·`input` 되울림 0·행 수 불변. 깨진 본문 8종 400/422. 조회 쿼리 28종(중복 키·빈 값·값 없는 키·`%`·`%zz`·잘린 UTF-8·`%FF%FE`·overlong `%C0%80`·`%00`×2만·`%ED%A0%80`·`+`·`username[]`·대문자 키·6만 자 등) 전부 200/422, 쓰기 0. 500 은 한 건도 없었다.

**5. `GET /auth/availability`** — `current_user` 의존성 없음, 쓰레기 쿠키 2개를 실어도 200·`Set-Cookie` 0(탐침), `Cache-Control: no-store`(200 응답 전부), 두 쿼리가 없으면 422 `missing_query`(`?username[]=`·`?USERNAME=`·`?=x` 포함), 형식 위반은 DB 조회 전 `invalid`(구현자 V9-10 + `_NoDb` 시험), 쓰기 0(4테이블 행 수 불변). `_EXEMPT` 와 열거 기대 두 곳에 `("GET", "/auth/availability")` 가 들어갔고 Origin 미들웨어는 `UNSAFE_METHODS` 만 본다. 422 본문은 `{"detail":{"code":"missing_query"}}` 고정 — 입력 되울림 0. 중복 키는 마지막 값으로 판정한다(`?username=taken&username=` → `invalid`).

**6. 닫힌 목록** — `git diff -U0 -- tests` 의 삭제 줄 전수: `auth_helpers.py`(B17) · `test_api.py:93`(B4) · `test_auth_api.py` 69-70(B9)·83(B10)·213(B11)·551(B12)·607(B13) · `test_auth_helpers.py:105`(B16) · `test_auth_origin.py:103`(B14) · `test_auth_required_routes.py` docstring·주석(B15, 나머지는 추가 줄) · `test_migration_0003.py` 48(B5)·214-219(B6)·233-234·248·259·269(B8)·358(B7) · `test_schema_check.py` 63-65(B3) · `test_schema_models.py` 80(B1)·153-159(B2). 목록 밖 삭제 줄 0. B6: "DB 버전 == 스크립트 head" 는 남고 head 리터럴은 `test_migration_0004 ①`(`head == "0004"`)로 옮겨갔다 — 약해지지 않았다. B8: 두 행의 닉네임이 `dup_a`/`dup_b` 로 달라 `constraint_name == "uq_users_username"` 단언이 그대로 선다. B15: 새 단언 둘 다 DB 에 가지 않는 요청(R4-2).

**7. 구현자가 스스로 판단한 곳** — (가) 6만 자: 타당. `httpx.URL(…100000자)` 는 `InvalidURL URL too long` 을 낸다(직접 확인). 10만 자는 판정 함수 직접 호출로 보탤 수 있다(R-5). (나) 서로게이트 둘로 나눔: R4-4 그대로, 타당. (다) `_me_out`: 응답 3곳이 같은 식이 되고 구현자 V9-11a/b/c 가 각각 잡혔다, 타당. (라) `_exists` monkeypatch: 계획 문장("④⑤ 사전 조회를 '없음' 으로 바꿔 끼운 뒤")의 구현이고 실제 INSERT·실제 제약 이름을 지난다, 타당. (마) ⑤ 삭제 변이 "등가": 동의 — ⑤ 가 없어도 ⑥ 이 같은 `nickname_taken` 을 낸다(내 경합 탐침으로 확인). 겉으로 보이는 차이는 scrypt 해시를 한 번 더 도는 비용뿐이다.

**8. 원칙 7 / R4-10** — `nickname` 이 나오는 `app/` 파일은 허용 4개뿐. 가입이 `persons`·`person_aliases`·`agent_traces` 행을 만들지 않는 시험이 있다. `app/auth/` 에 `logging`·`print` 0(grep) — 탐침의 `caplog`(DEBUG) 레코드 0건, 비밀번호·닉네임 누출 0. 접근 로그에 조회 쿼리 값이 남는 것은 `security.md` §5 가 이미 적어 둔 사실이다.

## 4. 소견

### [필수·기록]

- **D-1 U9 기록이 작업 트리에 없다.** `tests.md` 에 `U9` 가 0번 나오고(U10 절은 408행에 있음) `03-log.md` 에 U9 구현 항목이 없다. 계획 U9 판정은 "통과 수 = U9 시작 전 재측정값 + 새 테스트(03-log 에 수식)"·"`test_migration_0003.py` 의 헬퍼 … import 하거나 같은 방식 — 03-log 에" 를 요구한다. 구현자가 계획과 다르게 한 곳 (가)~(마)와 mypy 첫 실행 FAIL → 수정 경위도 03-log 에 있어야 한다. U9 커밋에 같이 넣는다(코드 변경 아님 — 재리뷰 불필요).

### [권고]

- **R-1 (시험 공백 — 변이 M-Q 생존)** 조회의 아이디 판정에만 `strip()` 을 넣어도 248건이 전부 통과한다. `test_username_statuses` 에 `(" taken_user ", "invalid")`·`("taken_user\n", "invalid")` 를, 가입 쪽에 같은 입력 422 `invalid_username` 을 더하면 "조회의 아이디 판정 = 가입의 아이디 판정"(D18 지킬 것 10)이 고정된다. 프론트가 trim 없이 보내므로 실제로 닿는 입력이다. 지금 코드는 맞다(탐침).
- **R-2 (시험 공백 — 변이 M-L 생존)** `NFC` 를 `NFKC` 로 바꿔도 전부 통과한다(전각 `ＡＢ`·`ⓐⓑ` 가 ASCII 로 접혀 통과하게 되는 변이). 거부 목록에 `"ＡＢ"`·`"ⓐⓑ"`·`"１２"` 를 더한다. 지금 코드는 셋 다 거부한다(탐침).
- **R-3 (시험 공백)** 409 시험이 `Set-Cookie` 없음·`auth_sessions` 행 수 불변을 단언하지 않는다. 지금 코드는 409 여섯 경로 모두 쿠키·세션 0(탐침). 한 시험에 두 단언을 더한다.
- **R-4 (관찰 — U11 브라우저 점검에서 볼 것)** 닉네임은 앞뒤 공백이 지워지고 아이디는 지워지지 않는다. 아이디 칸에 끝 공백이 붙으면(모바일 자동완성) 중복 확인이 `invalid`, 가입이 `invalid_username` 이다. 계획(결정 A 불변)대로이고 두 경로가 같은 답을 주므로 결함은 아니다. 바꾸려면 사용자 결정.
- **R-5** 조회의 10만 자는 `test_raw_lone_surrogate_string_is_invalid_without_touching_db` 의 `_NoDb` 직접 호출에 `"x" * 100_000` 한 줄을 더해 계획 문장("10만 자 → invalid")을 글자대로 채울 수 있다.
- **R-6 (관찰)** 422 `missing_query` 응답에는 `Cache-Control` 이 없다(헤더 설정이 `raise` 뒤). 계약 표는 200 응답의 헤더만 정하므로 위반 아님.
- **R-7 (관찰 — U9 이전부터)** 아이디에 켈빈 기호(U+212A)가 섞이면 `lower()` 가 ASCII `k` 로 바꿔 통과한다(`"Kelvin_p"` → 저장 `kelvin_p`). 저장 값은 규칙 안이고 가입·조회가 같은 답을 준다. U2 의 `normalize_username` 동작이며 U9 가 만든 것이 아니다.

## 5. 변이 표 (verifier 실행 — 런타임 치환, 저장소 무수정)

방식: `u9mut.py` 플러그인이 `pytest_sessionstart`(conftest 가 테스트 DB 로 바꾼 뒤)에서 대상 모듈 소스를 읽어 문자열 하나를 바꾼 사본을 `sys.modules` 에 꽂는다. 실행 시험은 `test_auth_{nickname,availability,api,required_routes,helpers,origin}.py`(248건) — 커밋형 시험 없음. 마이그레이션 변이는 `MIG_DB_NAME` 을 `relationship_test_mig_v15` 로 바꿔 `test_migration_0004.py` 만. V9-12 는 실행하지 않았다. `*` = 구현자가 돌리지 않은 변이.

| 변이 | 기대 | 결과 |
|---|---|---|
| CONTROL | 통과 | 248 passed(접속 DB `relationship_test`) |
| M-A* 가입이 정규화 전 원문 저장(`nickname=body.nickname`) | 잡힘 | **잡힘** — 9 failed(`test_nickname_is_normalized_nfc_strip_lower` 6 · strip 시험 · 대소문자 409 · 조회 case-fold) |
| M-B* 조회의 아이디 판정이 소문자화 누락 | 잡힘 | **잡힘** — 2 failed(`test_username_statuses[TAKEN_USER-taken]`·`[Free_Name-available]`) |
| M-E* `no-store` → `no-cache` | 잡힘 | **잡힘** — 1 failed(`test_response_is_no_store_and_keys_are_exact`) |
| M-L* `NFC` → `NFKC` | 잡힘 | **생존** — 248 passed → R-2 |
| M-Q* 조회의 아이디 판정에만 `strip()` | 잡힘 | **생존** — 248 passed → R-1 |
| CONTROL-MIG-V15 | 통과 | 8 passed |
| M-D* 백필 `SET nickname = id` | 잡힘 | **잡힘** — 3 failed(③ 백필 · ⑥ UNIQUE · ⑧ 왕복), 치환 2회 적용 |
| CONTROL-MIG-V15(변이 뒤) | 통과 | 8 passed(전용 DB 가 스스로 복구) |

구현자 변이 증거(`20261116-0717-u9-mutations.txt`)는 V9-1~11·13 과 추가 8종이 잡혔고, V9-2 첫 실행은 변이 문법 오류로 난 수집 ERROR 였으나 V9-2a/2b 로 다시 돌려 단언 실패로 잡혔다. 생존 1건(X-skip-nick-check)은 §3-7 (마).

한계: M-D 가 실제로 `…_mig_v15` 에서 돌았는지는 출력에 찍히지 않는다(플러그인이 찍는 이름은 세션 DB). 근거는 `_mig_env` 가 `tests.test_migration_0003.MIG_DB_NAME` 전역을 읽는다는 코드뿐이다. 어느 쪽이든 두 전용 DB 의 끝 상태는 §6 에서 정상이다.

## 6. DB 상태 (변이 뒤, 읽기 전용 SELECT)

| DB | alembic | users | `nickname IS NULL` | `nickname = username` | UNIQUE |
|---|---|---|---|---|---|
| `relationship` | 0004 | 3 | 0 | 3 | `uq_users_nickname`·`uq_users_username` |
| `relationship_test` | 0004 | 0 | 0 | 0 | 둘 다 |
| `relationship_test_mig` | 0004 | 2 | 0 | 2 | 둘 다 |
| `relationship_test_mig_v15` | 0004 | 2 | 0 | 2 | 둘 다 |

네 DB 모두 `nickname` 은 NOT NULL·기본값 없음. 구현자 보고(v15 의 UNIQUE 복구 포함)와 같다. 공유 테스트 DB 에 탐침·변이가 남긴 행 0.

## 7. 확인하지 못한 것

- 운영 서버·운영 볼륨(0003, 계정 있음)에서의 실제 `0003 -> 0004` 기동 — U11 의 로컬 Caddy 스모크와 재배포 몫이다. 여기서는 개발 DB 3계정 실측과 전용 DB 시험으로만 봤다.
- 실제 동시 요청 두 개의 경합 — `_exists` 치환으로 INSERT 충돌 경로만 봤다(커밋형 동시성 시험은 돌리지 않음).
- uvicorn·Caddy 를 지나는 실제 HTTP 에서의 긴 쿼리(요청 줄 상한) — TestClient 로만 봤다.
- V9-12(downgrade 가 컬럼을 남김) — 계획대로 실행하지 않고 downgrade 코드 두 줄과 시험 ⑧ 을 읽어 확인했다.
- Windows CI — 계획이 Mac 로컬 판정으로 정했다.
