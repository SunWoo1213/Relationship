# P9d-sensitive-guard · U4 보강 커밋 전 코드 리뷰 (review-u4b)

검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트
대상: dev2 작업 트리의 U4 보강 미커밋 변경(기준 커밋 `5fc2b79`) — `app/api/schemas.py`(실행 코드) · `app/briefing/scheduler.py` · `app/api/routes.py` · `app/auth/__init__.py`(모듈 docstring 만) · `tests/test_privacy_notice.py`. 같은 작업 트리의 `web/`(U9a) · `evaluation/sensitive_guard/` · `scripts/validate_sensitive_set.py`(U1 재작업)는 대상이 아니다.
작성: 2026-11-22 19:55

결과: 통과

열린 [필수] 0 · [권고] 2(R-1·R-2) · [참고] 5. review-u4 의 R-2·R-3·R-4 는 닫혔다.

## 1. 본 것

- 기준: `review-u4.md` R-2·R-3·R-4(109~111행) · `01-plan.md` U4 항목(172~177행 — 174행 "가입 검사 순서", 175행 "없음·`false` 모두 422 `{"detail":{"code":"notice_required"}}`(목록 모양 `detail` 0 — N-R7)") · `decisions/D20-sensitive-guard.md` 42행(③ 가입 고지·필수 동의, 판 번호)·47행(지킬 것 6)·72행(① 표 #10).
- 코드: `git diff 5fc2b79 -- app tests` 전부 · `app/auth/routes.py` 136~175행(가입) · `app/auth/deps.py` 55~68행 · `app/briefing/scheduler.py` 106~127행 · `tests/test_privacy_notice.py` 1~175행과 바뀐 헝크 · `tests/conftest.py` 119~130행(`db_session` 은 바깥 트랜잭션 rollback).
- 구현자 증거: `evidence/20261122-194{6,7}-u4b-*.txt` 9개(참고만). `…-1947-u4b-tools-check.txt` 는 구현자가 무효라고 밝힌 실행(`python3` 로 돌려 import 오류, exit 1)이라 판정에 쓰지 않았다.

## 2. 직접 실행한 명령과 결과

증거는 전부 `docs/wiki/packages/P9d-sensitive-guard/evidence/`. **저장소 파일은 고치지 않았다** — 변이는 import 시점 소스 치환(스크래치패드 `vu4b/mutplug.py`, `.pyc` 를 읽지도 쓰지도 않음), 값 확인 시험은 스크래치패드의 시험 파일을 `-p tests.conftest` 로 돌렸다. 로컬 DB 는 `docker ps` 로 `capstone2-postgres-1`(5433, healthy) 확인.

| 무엇 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 저장소 잔재(내 실행 **전**) | `git diff 5fc2b79 -- app/auth/deps.py app/auth/routes.py app/settings.py \| wc -l` · 주석 밖 바뀐 줄 · docstring 을 뺀 AST 비교(6파일) | §4 — 잔재 0 | `20261122-1950-verifier-u4b-residue.txt` |
| **가입 동의 값 18종 실제 요청** | `MUT=control … pytest <스크래치패드>/vu4b/test_probe_values.py -p mutplug -p tests.conftest`(JSON 원문을 그대로 보냄, 롤백 세션) | §3 표 — `true` 만 201, 나머지 17종 전부 dict 422·`users` 증가 0 | `…-1950-verifier-u4b-values.txt` |
| `StrictBool` 이었다면 | 같은 시험, `MUT=schema_strict_bool` | 불리언 아닌 14종이 `detail` **목록** 422, 순서 3건도 목록 422 | `…-1951-verifier-u4b-strictbool.txt` |
| **변이 6종 + 대조군 2회** | `bash <스크래치패드>/vu4b/run_muts.sh control sched_ge_to_eq deps_lt_to_ne route_truthy route_eq_true schema_loose_bool schema_strict_bool control` | §5 — 6/6 잡힘, 대조군 183 passed 두 번, 끝난 뒤 `git diff --stat` 그대로·`deps.py`/`routes.py` diff 0줄 | `…-1951-verifier-u4b-mutations.txt` |
| **전체 pytest** | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs -p no:cacheprovider` | **2807 passed · 실패 0 · skip 0**(= 2798 + 매개변수 7 + 새 시험 2, 구현자 수치와 같음) | `…-1952-verifier-u4b-full-pytest.txt` |
| 단독 | `… pytest tests/test_privacy_notice.py -q -rs -p no:cacheprovider` | **29 passed**(20 + 9) | `…-1952-verifier-u4b-notice.txt` |
| ruff | `.venv/bin/python -m ruff check app tests scripts evaluation` | All checks passed | `…-1952-verifier-u4b-ruff.txt` |
| tools_check | `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` | `…-1952-verifier-u4b-tools-check.txt` |
| mypy | `python3 scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 33건, 기준선 38건)`, exit 0 | `…-1952-verifier-u4b-mypy.txt` |

`tests/test_validate_sensitive_set.py` 는 지금 작업 트리에 **없다**(`ls` — No such file, `tests/` 의 `test_*` 103개가 전부 추적 파일). 그래서 "그 파일을 뺀 수치" 도 2807 로 같다. 개발 DB 는 건드리지 않았고, 내 시험·변이는 모두 롤백 세션 시험(`relationship_test`)이라 DB 에 남는 것이 없다 — 되돌릴 것이 없다.

## 3. R-2 방식 판정 — `Any = None` + 라우트 `is not True`

**판정: 타당하다. 메인 세션이 요청한 `StrictBool | None` 보다 계획에 맞는다.**

실제 요청 결과(증거 `…-verifier-u4b-values.txt`):

| 본문 값(JSON 원문) | 응답 | `users` 증가 |
|---|---|---|
| `true` | 201, `privacy_notice_version = 1` | 1 |
| 없음 · `false` · `null` | 422 `{"detail":{"code":"notice_required"}}` | 0 |
| `"true"` · `"yes"` · `"on"` · `"1"` · `"True"` · `"false"` · `"abc"` | 같은 422(dict) | 0 |
| `1` · `1.0` · `2` · `0` | 같은 422(dict) | 0 |
| `[]` · `[true]` · `{}` | 같은 422(dict) | 0 |
| 아이디 형식 위반 + `"abc"` | 422 `invalid_username` | — |
| 비밀번호 형식 위반 + `[]` | 422 `invalid_password` | — |
| 이미 있는 아이디 + `1` | 422 `notice_required`(409 아님) | — |

- 동의로 기록되는 값은 JSON 불리언 `true` **하나**다. `is not True` 는 동일성 비교라 `1`·`1.0`(파이썬에서 `== True`)도 거절한다 — `!= True` 로 바꾼 변이가 `int-1`·`float-1` 에서 잡힌다(§5).
- 구현자의 이유를 직접 확인했다(증거 `…-verifier-u4b-strictbool.txt`). `StrictBool | None` 이면 불리언이 아닌 14종이 전부 `{"detail":[{"type":"bool_type","loc":["body","privacy_notice_accepted"],…}]}` 로 나가고, **아이디 형식이 틀린 요청도 `invalid_username` 이 아니라 그 목록 422 가 먼저** 나간다. 이것은 계획 175행 "목록 모양 `detail` 0 — N-R7" 과 174행 "422 끼리는 형식 → 동의 순" 에 어긋난다. `Any` 는 두 문장을 모두 지킨다.
- `username`·`password`·`nickname` 은 여전히 `str` 이라 그 필드에 문자열이 아닌 값을 보내면 FastAPI 목록 422 가 나간다 — U4 이전부터의 동작이고 이 보강의 범위가 아니다(N-3).
- `Any` 의 부작용: ① OpenAPI 의 `SignupIn.privacy_notice_accepted` 가 `{"title": "Privacy Notice Accepted"}` 로 **타입 없이** 나온다(이전: `boolean | null`). 운영은 `Caddyfile` 13~14행이 `/openapi.json`·`/docs*`·`/redoc*` 에 404 를 내고, 저장소에 OpenAPI 로 타입을 만드는 도구가 없다(`grep -rn openapi web/package.json web/src scripts` 0건) → 영향 없음(N-1). ② `SignupIn` 의 사용처는 `app/auth/routes.py:138` 한 곳, `body.privacy_notice_accepted` 를 읽는 곳도 157행 한 곳이고 값은 저장되지 않는다(저장되는 것은 상수 `PRIVACY_NOTICE_VERSION` 과 주입 시계). 임의 크기의 JSON 값이 본문에 실려 올 수 있지만 다른 필드와 같은 본문 크기 한도 안이다. ③ mypy 새 오류 0.

## 4. 저장소 잔재 확인 (구현자가 저장소 파일을 고쳤다 되돌린 변이)

내 변이를 돌리기 **전**에 확인했다(증거 `…-1950-verifier-u4b-residue.txt`). **잔재 없음.**

- `git diff 5fc2b79 -- app/auth/deps.py app/auth/routes.py app/settings.py` → **0줄**.
- `app/briefing/scheduler.py:122` `.where(User.privacy_notice_version >= PRIVACY_NOTICE_VERSION)` · `app/auth/deps.py:59` `version < PRIVACY_NOTICE_VERSION` · `app/auth/routes.py:157` `is not True` — 그대로.
- docstring 을 비운 AST 를 기준 커밋과 비교: `scheduler.py`·`api/routes.py`·`auth/__init__.py`·`auth/deps.py`·`auth/routes.py` **AST 같음**, `api/schemas.py` 만 다름.
- `app/` diff 에서 주석이 아닌 바뀐 줄은 `schemas.py` 의 `from typing import Any, Literal` 과 `privacy_notice_accepted: Any = None` 두 쌍 + 모듈 docstring 줄뿐이다. docstring 헝크(`scheduler.py` 23행 · `api/routes.py` 14~17행 · `auth/__init__.py` 8행)는 각 파일 모듈 docstring 범위(끝 줄 76 · 104 · 14) 안이다.
- `app/`·`tests/`·`alembic/` 의 변경 파일은 대상 5개뿐이고 `*.orig`·`*.bak`·`*.rej` 없음. `git status --short -- app tests alembic` 에 목록 밖 파일 없음.

방식 자체에 대한 소견은 R-2.

## 5. 변이 시험 (저장소 무수정 — 런타임 치환)

대상 시험: `tests/test_privacy_notice.py` + `test_briefing_scheduler_users.py` + `test_auth_api.py` + `test_auth_nickname.py`. 대조군 183 passed(앞·뒤 두 번).

| 변이 | 결과 |
|---|---|
| `sched_ge_to_eq` — `app/briefing/scheduler.py` `>=` → `==`(review-u4 V9, 그때 통과) | **잡힘** — `test_scheduler_briefs_higher_notice_version_account`(`briefed_at` None) |
| `deps_lt_to_ne` — `app/auth/deps.py` `<` → `!=`(review-u4 V10, 그때 통과) | **잡힘** — `test_higher_notice_version_account_is_not_required_and_chat_passes`(`notice_required` True) |
| `route_truthy` — `is not True` → `not body.privacy_notice_accepted` | **잡힘** — `str-true`·`str-yes`·`int-1`·`float-1`·`str-abc`·`int-2` 6건 |
| `route_eq_true` — `is not True` → `!= True` | **잡힘** — `int-1`·`float-1` 2건 |
| `schema_loose_bool` — 스키마를 보강 전 `bool \| None` 으로 | **잡힘** — 7건(4건은 201, 3건은 목록 422) |
| `schema_strict_bool` — 스키마를 `StrictBool \| None` 으로 | **잡힘** — 7건(목록 422) |

R-3 의 두 변이는 각각 **그 변이를 겨냥한 시험 하나만** 실패한다(1 failed, 182 passed) — 시험이 다른 이유로 깨지는 것이 아니다.

## 6. R-4 — docstring 3곳

- ① `app/briefing/scheduler.py` 22~24행: "`persons.user_id` 에서 구하되 `users` 를 조인해 현재 판의 전송 고지에 동의한 계정만 고르고(미동의 계정과 `users` 행이 없는 인물은 건너뛴다)" — 117~127행의 inner join + `>=` 조건과 맞다.
- ② `app/api/routes.py` 14~16행: 세 라우트 403 `{"detail":{"code":"notice_required"}}`, `require_notice` 의존성 — review-u4 §4 에서 확인한 동작(세 라우트의 첫 의존성)과 맞다.
- ③ `app/auth/__init__.py` 8행: `POST /auth/privacy-notice` 추가 — 라우트가 있다(`app/auth/routes.py` 245행 근처, review-u4 §4).
- 동작 변경 없음: §4 의 AST 비교. 실행 코드 변경은 `schemas.py` 한 곳뿐이다.

## 7. 소견

### [필수]
없음.

### [권고]

- **R-1 `tests.md` · `03-log.md` 에 U4 보강 기록이 없다(커밋에 같이).** `tests.md` 80행은 아직 "**공백**: '현재보다 높은 판' 계정 시험 없음", 103행은 "`"true"`·`1` 등이 동의로 기록됨(review-u4 R-2, 열림)" 이고, `03-log.md` 26행은 U4 보강을 "남은 것" 으로만 적고 있다. 적을 것: 매개변수 3 → 10(7행), 새 시험 2건, 메인 세션 요청(`StrictBool`)과 다르게 `Any` 를 고른 이유(§3), 구현자 변이를 저장소 안에서 돌린 사실(R-2)과 무효 실행 1건.
- **R-2 구현자가 변이를 저장소 파일을 고쳤다 되돌리는 방식으로 돌렸다("저장소 무수정" 이탈).** 잔재는 없다(§4). 다만 그 사이 같은 작업 트리에서 frontend-agent·eval-agent 가 일하고 있었고, 되돌리기 전에 중단되면 `>=` → `==` 같은 한 글자 변이가 남는다 — 이번 것은 내 R-3 시험이 잡지만 일반적으로는 보장되지 않는다. 복사가 권한 거부될 때의 대안은 이번에 쓴 **import 시점 치환**이다(`-p` 플러그인이 `sys.meta_path` 에 로더를 끼워 대상 모듈 소스를 메모리에서만 바꾼다, 저장소·`.pyc` 무접촉 — 스크래치패드 `vu4b/mutplug.py`). 뒤 단위 위임 프롬프트에 "복사가 안 되면 런타임 치환, 저장소 파일 수정 금지" 한 줄을 넣는다. 구현자 증거 `…-1946-u4b-mutations.txt` 는 그 방식으로 만든 것이므로 이 리뷰의 판정 근거는 §5 의 내 실행이다.

### [참고]

- N-1 OpenAPI 스키마에서 `privacy_notice_accepted` 의 타입이 사라졌다(§3 ①). 운영에서 문서 경로는 404 이고 타입 생성 도구도 없어 영향이 없다. 타입을 문서에 남기고 싶다면 `Field(default=None, json_schema_extra={"type": "boolean"})` 로 검증 동작을 바꾸지 않고 적을 수 있다 — 필요해질 때.
- N-2 `{}`·`"on"`·`"1"`·`0`·`"false"` 와 "형식 위반 + 불리언 아닌 값" 순서는 저장소 시험의 매개변수에 없다(내 값 확인 시험에서만 봤다). 스키마 타입을 다시 좁히는 변이는 지금 매개변수로 전부 잡히고(§5 `schema_*`), 라우트 판정을 느슨하게 하는 변이도 잡히므로 공백은 아니다.
- N-3 `app/auth/routes.py` 155~156행 주석("없음·false 모두 같은 422")과 모듈 머리 표 7행은 그대로다 — 틀리지는 않지만 "true 가 아닌 모든 값" 이라는 지금 계약은 `schemas.py` 449~453행 주석에만 있다. 이 파일은 이번 diff 에 없으므로(그리고 없어야 §4 가 성립하므로) 다음에 그 파일을 고칠 때 한 줄.
- N-4 mypy 도구 수치가 review-u4 의 "현재 38건" 에서 "현재 33건" 으로 달라졌다(기준선 38 그대로, 구현자 증거도 33). review-u4 는 `.venv/bin/python` 으로, 이번은 지시대로 `python3` 로 돌렸다 — 판정은 둘 다 "새 오류 없음"·exit 0 이다. 수치 차이의 원인은 따로 확인하지 않았다.
- N-5 커밋 대상은 `app/` 4파일 + `tests/test_privacy_notice.py` + 문서(R-1)·이 리뷰·증거다. `web/`·`evaluation/sensitive_guard/`·`scripts/validate_sensitive_set.py` 는 다른 단위이니 `git add` 는 명시 경로로.

## 8. 결론

결과: 통과

- review-u4 **R-2 닫힘** — 동의는 JSON `true` 하나, 그 밖 17종은 dict 422·`users` 행 0, 검사 순서(형식 → 동의 → 409) 유지. `Any` + `is not True` 는 계획 174·175행을 지키는 쪽이고 `StrictBool` 은 어긴다(직접 확인).
- **R-3 닫힘** — review-u4 에서 통과하던 변이 2종이 각각 새 시험 1건에 잡힌다.
- **R-4 닫힘** — docstring 3곳이 동작과 맞고, 실행 코드 변경은 `schemas.py` 한 곳뿐(AST 비교).
- 저장소 잔재 0. 전체 2807 passed · skip 0 · ruff · tools_check 7/7 · mypy 새 오류 0.
- 커밋 전: R-1(문서)을 같이 넣는다. R-2 는 뒤 단위 위임 문구.
