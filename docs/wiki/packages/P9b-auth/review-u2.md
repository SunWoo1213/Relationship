# P9b-auth · U2 커밋 전 코드 리뷰 (review-u2)

검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트
대상: dev2 작업 트리의 U2 미커밋 변경(`app/auth/*.py` 6파일 · `app/api/schemas.py` · `app/main.py` · `app/settings.py` · `.env.example` · `tests/test_auth_{api,origin,passwords,settings}.py` · `tests/test_migration_0003.py` · `03-log.md` U2 메모 · `tests.md` U2 절 · `evidence/20261115-212*-u2-*.txt`). 프론트 U6(`web/`)은 범위 밖.
작성: 2026-11-15 21:40

판정: **통과** (재검토 2026-11-15 21:50 — 1차 `보류` 의 [필수] F-1·F-2 해소, §10). 열린 [필수] 0 · 열린 [권고] R-4·R-5·R-6·R-7·R-9·R-10(R-1·R-2·R-3·R-8 은 닫힘).

> 아래 §1~§9 는 1차 검토(21:40, 판정 보류) 기록 그대로다. 재검토 결과는 §10.

> 리뷰 도중 HEAD 가 `0f9223e` → `6ecf635`(U6 프론트 커밋)로 움직였다. U2 파일 10개는 계속 미커밋이고(`git status --short -- app tests .env.example` 10줄, 리뷰 전후 같음) 내가 본 내용은 바뀌지 않았다. 증거 파일 머리의 HEAD 가 둘로 갈리는 이유다. 계획의 순서("U6 은 U2 커밋 뒤")와 실제 커밋 순서가 다른 점은 메인 세션 몫으로 적어만 둔다.

## 1. 본 것

- 계약: `01-plan.md` "API 계약" 표(공통 Origin 행) · U2 항목(128~141행) · "고치는 기존 파일" U2 행 · 결정 A~H·T(266~285행) · 판정 표 #1·#13 · 사실 10·12·13·14 · "3차 검증 권고 반영". `decisions/D18-login-user-isolation.md` 지킬 것 1~4. `security.md` §1(CR-006 행). `review-u1.md` R-8·R-9.
- 코드: `git diff -- app tests .env.example` 전부, 새 파일 `app/auth/{__init__,passwords,sessions,deps,origin,routes}.py`, 시험 4파일 전부, `app/main.py` 예외 핸들러, `app/api/deps.py:120-130`(`get_session`), `app/db/session.py:44`(엔진), `Caddyfile`, `web/vite.config.ts:26-29`, `web/src/api/client.ts:71-74`, FastAPI `routing.py:407-418`(콘텐츠 타입 분기, 설치본 0.135.1 · Starlette 1.7.0 · pydantic 2.13.5).
- 구현자 기록: `03-log.md` U2 메모(판단 1~6·변이 방식), `tests.md` U2 절, `evidence/20261115-2125-u2-mutations.txt`.

## 2. 직접 실행한 명령과 결과

증거는 전부 `docs/wiki/packages/P9b-auth/evidence/`. 탐침·변이는 저장소 밖 사본(`…/scratchpad/vu2/copy`)에서만 돌렸고 저장소 파일은 고치지 않았다. 시험용 DB 는 새로 만들지 않았다(기존 `relationship_test`·`relationship_test_mig` 재사용).

| 무엇 | 명령 | 결과 | 증거 |
|---|---|---|---|
| 전체 pytest | `.venv/bin/python -m pytest -q -rs` | **2389 passed** · 실패 0 · skip 0 | `20261115-2131-verifier-u2-pytest-all.txt` |
| 인증 4파일 + 0003 | `… pytest tests/test_auth_*.py tests/test_migration_0003.py -q -rs` | 128 passed(117 + 11) | `20261115-2131-verifier-u2-auth.txt` |
| alembic | `.venv/bin/python -m alembic check` | `No new upgrade operations detected.` | `…-2131-verifier-u2-alembic-check.txt` |
| ruff | `… -m ruff check app tests scripts evaluation alembic` | All checks passed(구현자 증거는 `alembic` 디렉터리를 빼고 돌렸다 — 여기서 포함해 통과) | `…-2132-verifier-u2-ruff.txt` |
| mypy | `… scripts/mypy_check.py --run` | 새 오류 없음(38/38) | `…-2132-verifier-u2-mypy.txt` |
| tools_check | `… scripts/tools_check.py` | 7/7 | `…-2132-verifier-u2-tools-check.txt` |
| 범위 | `git status --short -- app/er app/tools app/api/routes.py app/api/deps.py app/agent evaluation reports data` | 빈 출력 | `…-2132-verifier-u2-er-unchanged.txt` |
| 탐침 15종(이상 입력·쿠키·Origin·타이밍) | `vrun.py probe` | 아래 §3·§4 | `20261115-2135-verifier-u2-probe.txt`(`2134` 는 출력 필터가 깨진 첫 실행 — 대체됨) |
| 보충 시험 5건 기준선 + 예외 문자열 카나리아 | `vrun.py probe test_vu2_extra.py` | 5 passed | `…-2135-verifier-u2-extra-baseline.txt` |
| 변이 13종(구현자 시험만) | `vrun.py mutall` + `mut VM-4`·`mut VM-12` 추가 | §6 | `…-2135-verifier-u2-mutations.txt`(첫 실행의 VM-4 `[ERROR]`·VM-12 "잡힘" 은 변이 정의 오류 — 파일 끝에 붙인 두 줄이 맞는 결과) |
| 같은 변이 + 보충 시험 | `vrun.py mutall-extra` | §6 | `…-2137-verifier-u2-mutations-extra.txt` |
| R-8·R-9(`-vv -l` 강제 실패) | `vrun.py showlocals` | 환경 사본 0회 | `…-2137-verifier-u2-showlocals2.txt`(`2136` 은 URL 수 세는 식이 거칠었던 첫 실행) |
| 증거 속 비밀 | `grep -lE 'rel_session=[A-Za-z0-9_-]{20,}\|scrypt\$16384\$8\$1\$[A-Za-z0-9+/]{10,}' *u2*.txt` | 일치 0(exit 1) | 이 표 |

## 3. [필수] 소견

### F-1 `POST /auth/login` — 아이디에 NUL 문자가 있으면 500

- 재현(`verifier-u2-probe` p01): `{"username": "ab\u0000cd", "password": …}` → **500 `{"detail":{"code":"internal_error"}}`**. 예외는 `sqlalchemy.exc.DataError`(PostgreSQL 은 문자열에 NUL 을 못 받는다, `extra-baseline` p16).
- 원인: `app/auth/routes.py:124-125` — 로그인은 `normalize_username()` 만 하고 결정 A 의 형식 검사 없이 곧바로 `select(User).where(User.username == username)` 를 보낸다. 가입(96행)은 `_USERNAME_RE.fullmatch` 로 막지만 로그인에는 그 문이 없다.
- 왜 필수인가: ① 계약 위반 — "API 계약" 표의 로그인 실패는 `401 invalid_credentials` 하나다("없는 아이디·틀린 비밀번호 같은 응답"). NUL 이 든 아이디는 "없는 아이디" 인데 다른 상태·다른 본문이 나간다. ② 로그인 없이 누구나 보낼 수 있다. ③ 요청마다 서버 로그에 트레이스백이 남고, 그 문구에 SQL 과 `[parameters: …]`(여기서는 아이디)가 실린다(`extra-baseline` p16 `mentions parameters: True`). 비밀번호는 실리지 않는다(`canary in traceback text: False`).
- 닫는 조건: 형식에 맞지 않는 아이디(NUL·짝 없는 서로게이트·길이 초과 등)의 로그인이 **401 `invalid_credentials` 같은 본문**이고, 그때도 해시 검증이 한 번 돈다(더미 해시 — 시간 차 유지). 그 입력을 단언하는 시험 1건.

### F-2 `POST /auth/signup` — 비밀번호에 짝 없는 서로게이트가 있으면 500

- 재현(`verifier-u2-probe` p02): 본문 `{"username": "surro1", "password": "\ud800aaaaaaaaaa"}` → **500 `internal_error`**. 예외는 `UnicodeEncodeError`(`extra-baseline` p16).
- 원인: `app/auth/passwords.py:40` `password.encode("utf-8")` 가 `hash_password` 경로에서 보호 없이 불린다. `verify_password`(83~86행)는 `except ValueError` 가 우연히 `UnicodeEncodeError`(그 하위 클래스)를 삼켜 로그인은 401 로 끝나지만(같은 탐침 `/auth/login -> 401`), 가입은 길이 검사(`routes.py:98`)를 통과한 뒤 해시에서 터진다.
- 왜 필수인가: 계약상 가입 실패는 422(`invalid_username`/`invalid_password`)·409 뿐이다. 로그인 없이 보낼 수 있는 입력에 500 이 나간다. DB 변화는 없다(INSERT 전에 터진다). 예외 문구에는 문제 문자 하나와 위치만 있고 비밀번호 전체는 없다(카나리아 0회).
- 닫는 조건: UTF-8 로 못 바꾸는 비밀번호의 가입이 계약 안의 4xx(`invalid_password` 가 자연스럽다)이고 `users` 행 수 불변. 시험 1건. `verify_password` 가 그 입력을 False 로 돌리는 것도 우연이 아니라 의도로 드러나게(주석이든 명시적 분기든).

두 소견 모두 정보 유출·인증 우회는 아니다. 고치는 범위는 `routes.py`·`passwords.py` 몇 줄과 시험 2건으로 보인다.

## 4. 줄 단위 판정 — 맞다고 본 것과 근거

**해시(`passwords.py`)**
- 파라미터·형식이 결정 C 그대로: `SCRYPT_N = 2**14`·`r=8`·`p=1`·`dklen=32`·`secrets.token_bytes(16)`, 형식 `scrypt$16384$8$1$<salt>$<hash>`(`test_format_carries_parameters_and_sizes` 가 값으로 단언, 구현자 M-20 잡힘).
- 비교는 `hmac.compare_digest`(87행, D18 지킬 것 1). 구현자 V2-1 을 호출 여부 시험으로 잡았다 — 계획이 "기능 테스트로는 안 잡힘" 이라 한 한계를 넘었다.
- 길이 상한이 해시 앞: 가입 `routes.py:98` → `101`, 탐침 p14 "2MB 비밀번호 가입 → 422 `invalid_password`". 변이 VM-9(상한 제거) 잡힘.
- 형식 파싱: 깨진 문자열은 `None`/False(시험 7건). `n` 상한은 없다 — 저장 문자열은 `hash_password` 가 만든 DB 값뿐이라 공격자 입력이 아니다(R-6 권고).
- 더미 해시 타이밍: 탐침 p12 중앙값 — 없는 아이디 20.9 ms · 틀린 비밀번호 20.8 ms · 성공 22.2 ms. 평준화가 실제로 된다. 128자 초과는 아는/모르는 아이디 모두 1.3 ms 로 같아 아이디 존재를 드러내지 않는다.

**세션·쿠키(`sessions.py`·`deps.py`)**
- 토큰 `secrets.token_urlsafe(32)`(256비트, 탐침 p08 길이 43). DB 에는 `sha256` hex 만(`test_token_hash_is_sha256_of_cookie_not_the_cookie`, 구현자 V2-2 잡힘).
- 만료 `expires_at > now`(79행). 변이 **VM-1(만료 조건 삭제) 잡힘**, VM-8(주입 시계 대신 실제 시계) 잡힘.
- 로그아웃은 그 토큰 행만: 변이 **VM-2(그 사용자의 모든 세션 삭제) 잡힘**(`test_logout_removes_only_that_session`).
- 세션 고정 없음: 로그인은 항상 새 토큰을 만든다. 탐침 p08 — 공격자가 미리 심은 쿠키 값으로 로그인해도 발급 토큰이 그 값이 아니다(`False`). 재로그인하면 행이 2개가 되고 옛 토큰도 만료까지 유효하다(기기별 세션 — 계획대로, R-9 참고).
- `__Host-` 조건: 설정 쿠키 `Secure`·`Path=/`·`Domain` 없음(시험). **삭제 쿠키도 같은 속성**(탐침 p07: `__Host-rel_session=""; … HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure`, 끔 상태는 `rel_session=""` 에 `Secure` 없음). 다만 이 둘을 단언하는 시험이 없다(R-2).
- 켬 상태에서 접두 없는 `rel_session` 쿠키로는 인증되지 않는다(p08 → 401). 변이 VM-7 잡힘.

**Origin 미들웨어(`origin.py`)**
- 규칙이 결정 T·R2-1 ① 그대로(소문자·스킴 기본 포트 양쪽 제거·XFH 첫 값·`null` 다름). 변이 VM-10(XFH 무시)·VM-11(XFH·Host 어느 쪽이든) 잡힘.
- 이상 입력(탐침 p05·p06): userinfo(`https://testserver@evil.example`·`https://evil.example@testserver`)·끝 점·역슬래시·쉼표나 공백으로 이은 두 값·깨진 IPv6·빈 `Origin` 헤더 → 전부 다름(403). IPv6 리터럴은 같은 것끼리 통과, 다른 것은 다름. 경로·쿼리·프래그먼트가 붙어도 호스트만 본다.
- 관찰만(조치 불요): ① `Origin: http://<같은 호스트>` 는 https 사이트에서도 통과한다(p06 → 401, 즉 라우트에 닿음) — 결정 T 가 "호스트(:포트)" 비교라 계획대로다. 같은 호스트의 http 페이지를 공격자가 내놓으려면 망 중간자여야 한다. ② `Host` 가 빈 요청에 `Origin: https://:443` 이면 같다고 본다 — 브라우저가 만들 수 없는 값이고 Caddy 를 지나면 `Host` 가 빈 요청이 없다. ③ `Origin` 헤더가 둘이면 첫 값만 본다(위조 값이 첫째면 403, 둘째면 통과) — 브라우저는 하나만 보낸다. 변이 VM-6(마지막 값 사용)은 살아남는다(R-5).
- 등록: `create_app()` 의 `add_middleware` 한 곳. 순수 ASGI 라 라우팅·의존성·DB 세션보다 앞에서 끊는다 — 403 때 DB 변화 0(`test_evil_origin_post_is_403_bad_origin_and_changes_nothing` 4경로가 `users`·`auth_sessions` 포함 7테이블 행 수 단언). GET·HEAD·OPTIONS 통과(시험 3건, 구현자 M-28 잡힘).
- **Caddy 뒤 같은 출처 POST(코드 추론, 확정은 U7 스모크)**: `Caddyfile` 의 `handle_path /api/* { … reverse_proxy backend:8000 }` 에 `header_up Host` 가 없다 → Caddy 기본대로 `Host` 는 원래 값이고 `X-Forwarded-Host` 도 원래 호스트다. 브라우저 `Origin: https://54-79-202-221.sslip.io` ↔ 둘 중 어느 쪽과 비교해도 같다 → 막지 않는다. 로컬 스모크(`SITE_ADDRESS=:80`)도 `Origin` 과 `Host` 의 포트가 같아 통과. Vite 개발 프록시는 `web/vite.config.ts:29` `xfwd: true` 가 이미 있다.

**응답·로그·예외**
- `/auth/*` 422 본문에 `input`·`ctx` 없음: 탐침 p04 — 가입·로그인 × 7가지(필드 누락·타입 오류·배열 본문·문자열 본문·깨진 JSON·`text/plain`·콘텐츠 타입 없음) 전부 키가 `['loc','msg','type']` 뿐이고 카나리아 0회.
- `/auth` 밖 422 모양 불변: `/chat` 422 는 여전히 `['input','loc','msg','type']`(p04). 프론트 `web/src/api/client.ts:71-74` 는 `detail` 이 객체이고 `code` 가 있을 때만 읽으므로 배열 모양 422 와 충돌하지 않는다.
- `app/auth/` 에 `print`·`logging` 호출 0(grep). `/auth/*` 는 `agent_traces` 를 쓰지 않는다(시험).
- 증거 파일 13개에 토큰·해시 문자열 0(§2 마지막 줄).

**가입 경합·아이디 정규화**
- `begin_nested()` + `IntegrityError` → 409(구현자 M-26 잡힘). 운영 `get_session` 에서도 세이브포인트만 되돌아가 뒤 응답이 정상이다.
- 유니코드 접힘 — **계정 혼동 없음**(구현자 판단에 동의). 탐침 p09: `K`(켈빈 기호)`im_01` 가입 → `kim_01` 로 저장, 이어 ASCII `kim_01` 가입 → 409. 즉 켈빈 `K` 는 대문자 `K` 와 똑같이 "같은 아이디의 다른 표기" 로 접힐 뿐, 서로 다른 두 계정이 한 이름으로 보이거나 남의 계정에 들어가는 길이 없다(로그인도 같은 접힘 + 비밀번호 필요). ASCII 로 접히지 않는 문자(`İ`·전각 `ＡＢＣ`·`ſ`·`ǅ`·`Å`·결합 문자·폭 없는 공백·`ı`)는 전부 422.

**non-JSON 본문(F-7 ②)**
- `text/plain`·폼 → 4xx·행 수 불변(구현자 시험 3경로 + 대조군). 콘텐츠 타입이 **없는** 본문도 지금은 422·DB 불변이다(탐침 p13, 4경로).

## 5. 계획에 없던 방어 2건

| 방어 | 판정 | 근거 |
|---|---|---|
| ① `/auth` 라우터에만 `_NoInputEchoRoute`(422 에서 `input`·`ctx` 제거) | **타당, 계획·D18 과 충돌 없음** | D18 지킬 것 3 "응답 본문에 비밀번호 0" 의 직접 적용. 기본 422 는 필드 누락 때 본문 전체를 되돌린다(구현자 M-22 가 시험으로 잡힘). 범위가 `/auth` 라우터 하나라 다른 라우트 모양 불변(p04). 사용자 결정 사항 없음. 빈틈: 시험이 가입만 본다 — 로그인만 기본 라우트로 빠지는 변이 VM-12 가 살아남는다(R-3) |
| ② 로그인 비밀번호 128자 초과면 해시 없이 같은 401 | **타당, 계획·D18 과 충돌 없음** | 결정 B 의 상한(표 근거 "상한 128 은 해시 입력 상한")을 그대로 쓴다 — 새 상수 0. 응답 본문·상태가 다른 실패와 같고(`test_login_failures_share_one_response…`), 시간 차는 아이디 존재와 무관하다(p12). 사용자 결정 사항 없음. 빈틈: "해시를 돌리지 않는다" 를 단언하는 시험이 없어 방어를 지워도(VM-5) 전부 통과한다(R-3) |

그 밖 구현자 판단: ASGI 미들웨어(계획 "미들웨어 또는 공통 의존성" 안) · `get_auth_now` 분리(기존 `get_now` 시험과 격리 — 타당) · 순환 import 메모(U3b 인계, 지금은 `app.main` 이 `app.api` 를 먼저 불러 문제없음 — 전체 pytest 통과가 근거) — 이의 없음.

## 6. 변이 시험 (verifier, 구현자가 돌리지 않은 것)

| 변이 | 구현자 시험만 | 보충 시험 포함 |
|---|---|---|
| VM-1 `find_user_by_token` 만료 조건 삭제 | **잡힘** — `test_session_expiry_boundary_is_exclusive_at_seven_days` | — |
| VM-2 로그아웃이 그 사용자의 모든 세션 삭제 | **잡힘** — `test_logout_removes_only_that_session` | — |
| VM-7 `current_user` 가 항상 `rel_session` 이름 | **잡힘**(9건) | — |
| VM-8 만료를 실제 시계로 계산 | **잡힘** | — |
| VM-9 가입 비밀번호 상한 제거 | **잡힘** | — |
| VM-10 XFH 무시 · VM-11 XFH·Host 어느 쪽이든 통과 | **잡힘** | — |
| VM-3 쿠키 삭제가 이름 분기 누락(항상 `__Host-`) | 살아남음 | 잡힘(`test_logout_secure_off_clears_plain_name`) |
| VM-4 쿠키 삭제에서 `Secure` 빠짐 | 살아남음 | 잡힘(`test_logout_clear_cookie_keeps_host_prefix_attributes`) |
| VM-5 로그인 128자 초과 방어 제거 | 살아남음 | 잡힘(`test_too_long_login_skips_hash`) |
| VM-13 `strict_content_type=False`(= 구현자 V2-9b) | 살아남음 | 잡힘(`test_noctype_json_shaped_body_is_rejected_and_writes_nothing`) |
| VM-12 로그인만 422 되울림 방어 밖 | 살아남음 | 살아남음(보충 시험에 넣지 않음) |
| VM-6 `Origin` 헤더 여럿이면 마지막 값 | 살아남음 | 살아남음 |

핵심 계약(만료·한 세션만 로그아웃·쿠키 이름으로 인증·Origin 비교)은 잡힌다. 살아남은 것은 전부 "지금 코드는 맞지만 시험이 그 성질을 붙들지 않는" 자리다(R-1~R-5). 보충 시험 원문은 `…/scratchpad/vu2/test_vu2_extra.py`(저장소에 넣지 않았다).

### 구현자 V2-9b 설명 — 절반만 맞다

- 맞는 부분: FastAPI 0.135.1 `routing.py:409-418` — 콘텐츠 타입이 있으면 `application/json`·`+json` 일 때만 JSON 으로 읽고, `strict_content_type` 은 **헤더가 아예 없을 때만** 영향을 준다. 그래서 `text/plain`·폼 시험으로는 그 변이가 안 잡힌다.
- 틀린 부분: "실제 회귀 경로가 아니다". 콘텐츠 타입 없는 POST 는 다른 사이트 페이지가 프리플라이트 없이 보낼 수 있는 요청이고(본문을 타입 없는 Blob·바이트로 주면 헤더가 붙지 않는다), 그 옵션이 지키는 것이 바로 그 경로다. 옵션을 끄면 `/push/subscriptions`·`/auth/signup` 이 그 본문을 JSON 으로 받아 쓴다(VM-13 + 보충 시험이 실패로 보임). 지금은 기본값이 켜져 있어 안전하고(p13) Origin 검사가 한 겹 더 있지만, 시험은 그 경로를 비워 두었다 → R-1.

## 7. 범위

- 기존 라우트·툴·ER·평가 무변경: `git status --short -- app/er app/tools app/api/routes.py app/api/deps.py app/agent evaluation reports data` 빈 출력. `app/` 에서 바뀐 기존 파일은 계획 표의 U2 행 3개(`main.py` +5 · `settings.py` +45 · `schemas.py` +38)뿐이고 전부 추가다.
- 뒤 단위 앞당김 없음: `app_user_id()`·`APP_USER_ID` 줄 그대로(`.env.example:53`, `settings.py` 의 함수 — diff 문맥에서 확인). 로그아웃 `endpoint` 는 받기만 한다(`routes.py:146`).
- 기존 시험 변경은 `tests/test_migration_0003.py` 하나(R-8·R-9). 전체 2389 = 2272 + 117.
- **R-8·R-9 닫힘**: `mig` 픽스처를 일부러 실패시키고 `-vv -l` 로 돌렸을 때 카나리아 환경변수 값 0회·키 이름 0회, 찍힌 지역변수는 `conn`·`db_engine`·`engine`·`overrides` 뿐(`env` 없음), 접속 URL 모양 3회는 전부 비밀번호 자리가 `***`(`showlocals2`). `_EnvOverrides` docstring 에 `==` 비교 금지 경고가 들어갔다. 헬퍼 `_mig_env` 안의 지역변수 `env` 는 남지만 그 함수 안에서 예외가 날 때만 보인다 — 구현자 메모대로 R-8 범위 밖.

## 8. [권고] 소견 (커밋을 막지 않는다)

- **R-1 콘텐츠 타입 없는 본문 시험.** F-7 ② 시험에 "헤더 없이 JSON 모양 본문 → 4xx·행 수 불변" 을 더하면 V2-9b 가 잡힌다. `03-log`·`tests.md` 의 "실제 회귀 경로가 아니다" 문장은 §6 대로 고쳐 적는다.
- **R-2 쿠키 삭제 속성 시험.** 로그아웃 응답의 `Set-Cookie` 에 `Secure` 가 있는지(켬), 끔 상태에서 이름이 `rel_session` 인지 단언이 없다(VM-3·VM-4 생존). `__Host-` 쿠키는 `Secure` 없는 `Set-Cookie` 를 브라우저가 버리므로, 이 속성이 빠지면 로그아웃해도 브라우저에 쿠키가 남는다(서버 행은 지워져 인증은 안 되지만).
- **R-3 계획 밖 방어 2건의 시험.** ① 422 되울림 시험에 `/auth/login` 을 더한다(VM-12). ② 128자 초과 로그인에서 `verify_password` 호출 0 을 단언한다(VM-5). 지금은 두 방어 모두 지워도 통과하는 구간이 있다.
- **R-4 `AUTH_COOKIE_SECURE` 오타는 기동 때 잡는다.** 지금은 요청마다 읽어 값이 틀리면 `/auth/*` 가 전부 `422 invalid_value` 이고 `/health` 는 200 이다(p11) — 배포 스모크가 `/health` 만 보면 놓친다. `BRIEFING_SCHEDULER_ENABLED` 처럼 lifespan 에서 한 번 읽어 기동을 실패시키는 편이 같은 관례다. U7 스모크에 로그인 한 번이 들어가면 그것으로도 잡힌다.
- **R-5 `Origin` 헤더가 둘인 요청.** 하나만 허용하고 둘 이상이면 다름으로 보는 편이 닫힌 쪽이다(지금은 첫 값). 브라우저 경로가 아니라 우선순위 낮음.
- **R-6 저장 해시의 `n` 상한.** `parse_hash` 는 `n ≥ 2` 만 본다. DB 값이 오염되면 큰 `n` 으로 메모리를 잡으려 든다. 공격자 입력이 아니라 낮음 — 형식을 올릴 때 함께.
- **R-7 500 로그의 SQL 파라미터.** 엔진(`app/db/session.py:44`)에 `hide_parameters` 가 없어, 가입 INSERT 가 UNIQUE 가 아닌 이유로 실패하면 로그의 예외 문구에 `password_hash` 가, 세션 INSERT 면 `token_hash` 가 실린다. 평문·토큰 원문은 아니라 D18 지킬 것 3 위반은 아니다. 엔진은 U2 범위 밖이라 별도 FIX 후보.
- **R-8 낡은 문장 2곳.** `tests/test_auth_api.py:180` docstring 의 "(`hide_input_in_errors` …)" — 실제 수단은 `_NoInputEchoRoute` 다(03-log 는 그 옵션이 안 먹었다고 적었다). `app/api/schemas.py` 주석은 맞다.
- **R-9 기록.** ① `registry.md` 에 `app/auth/*`·`auth_cookie_secure()`·`OriginCheckMiddleware` 행이 아직 없다(grep 0) — U1 처럼 커밋 때 올린다. ② 재로그인마다 세션 행이 쌓이고 정리 작업이 없다(계획 리스크 절에 있는 수용 사항 — 공개 4일). ③ 응답이 나간 뒤 `get_session` 이 커밋한다(FastAPI 0.135 요청 범위 의존성) — 가입 201 직후의 다음 요청이 아주 드물게 커밋보다 먼저 닿을 수 있다. 기존 모든 라우트와 같은 구조라 U2 문제가 아니다. U7 스모크에서 가입 → `/auth/me` 를 연달아 볼 때 염두에 둔다.

## 9. 판정

**보류**(1차). 닫을 것은 F-1·F-2 둘이다(구현 에이전트). 고친 뒤 재검토는 그 두 입력의 탐침 재실행(`vrun.py probe`)과 인증 시험·전체 pytest 로 충분하다. R-1~R-3 은 같은 파일을 여는 김에 함께 넣으면 변이 5개가 닫힌다.

## 10. 재검토 (2026-11-15 21:50) — 판정: 통과

구현자 수정: `app/auth/routes.py`(로그인 형식 문 130~134행 · 가입 UTF-8 검사 100~102행) · `app/auth/passwords.py`(`is_utf8_encodable` 44~50행 · `verify_password` 명시적 False 92~93행) · `tests/test_auth_api.py`·`tests/test_auth_passwords.py`(시험 117 → 154건) · `tests.md`·`03-log.md`. 구현자 보고는 근거로 쓰지 않고 아래를 직접 돌렸다. 증거는 같은 `evidence/` 의 `20261115-214*-verifier-u2-recheck-*.txt`.

### 10.1 직접 실행

| 무엇 | 결과 | 증거 |
|---|---|---|
| 전체 pytest `-q -rs` | **2426 passed** · 실패 0 · skip 0(2389 + 37) | `…-2146-verifier-u2-recheck-pytest-all.txt` |
| 인증 4파일 + 0003 | 165 passed(154 + 11) | `…-2146-verifier-u2-recheck-auth.txt` |
| ruff(`alembic` 포함) · mypy | All checks passed · 새 오류 없음(38/38) | `…-recheck-static.txt` · `…-recheck-mypy.txt` |
| 탐침 17종 재실행(1차 15 + p17 타이밍 · p18 퍼즈) | 아래 | `…-2145-verifier-u2-recheck-probe.txt` |
| 퍼즈에서 로그인 200 이 난 조합 식별 | 아래 R-10 | `…-2148-verifier-u2-recheck-who200.txt` |
| 변이 18종(1차 13 + 수정 되돌림 RM-1~RM-5), **구현자 시험만** | 17 잡힘 · VM-6 만 생존 | `…-2146-verifier-u2-recheck-mutations.txt` |
| 증거 속 비밀(`*u2*.txt` 전체, 구현자 `u2-fix-*` 5개 포함) | 토큰·해시 문자열 일치 0(exit 1) | §2 와 같은 grep |
| 범위 | `git status --short -- app tests .env.example` 10줄 그대로 · `app/api`·`main.py`·`settings.py` diff 는 1차와 같은 88줄 추가 | 이 표 |

### 10.2 닫는 조건별 판정

- **F-1 닫힘.** p01: NUL 아이디 로그인 → `401 {"detail":{"code":"invalid_credentials"}}`. 시험 `test_login_with_malformed_username_is_the_same_401_and_still_runs_one_hash`[9]가 본문이 없는 아이디 응답과 바이트 단위로 같고(`resp.content == unknown.content`) `verify_password` 가 정확히 1회, 그 대상이 `dummy_hash()` 임을 값으로 단언한다. **타이밍 평준화 유지**(p17 중앙값): 없는 아이디 21.0 ms · NUL 아이디 19.3 · 서로게이트 아이디 19.3 · 길이 초과 아이디 19.3 · 틀린 비밀번호 20.7. 형식 위반 쪽이 약 1.7 ms 짧은 것은 DB 조회 한 번이 빠진 차이다 — 형식 위반 아이디는 가입될 수 없어 공격자가 그 차이로 알아낼 계정이 없다.
- **F-2 닫힘.** p02: 서로게이트 비밀번호 가입 → `422 invalid_password`, 시험이 `users` 행 수 불변을 단언. 로그인 쪽은 `verify_password` 가 `_derive` 를 부르지 않고 False(`test_unencodable_password_is_explicitly_rejected_not_an_accident` 가 호출 0 단언). 서로게이트 비밀번호 로그인은 아는/모르는 아이디 모두 1.3~1.5 ms 로 같아 아이디 존재를 드러내지 않는다.
- **500 전수.** p18: 아이디·비밀번호에 36가지 값(NUL·짝 없는 서로게이트 앞/뒤/쌍·BOM·켈빈 기호·제어 문자·SQL 조각·30만 자·빈 값·`None`·숫자·불리언·배열·객체)을 36×36 으로 가입·로그인 양쪽에 넣었다(2592 요청) → **5xx 0**. 상태는 가입 201·409·422, 로그인 200·401·422 뿐. 본문 자체가 이상한 경우(빈 본문·`null`·배열·깨진 JSON·잘못된 UTF-8·10만 바이트 숫자) × 3경로도 401·422 뿐. 쿠키 값 이상 입력의 `/auth/me`·`/auth/logout` 은 전부 401.
- **계획 밖 추가 없음.** 새 상수 0, 새 응답 코드 0. F-1 은 결정 A 의 정규식을 로그인에도 적용한 것이고 F-2 는 계약 표의 `invalid_password` 를 쓴다. API 계약 표와 어긋난 곳 없음. `is_utf8_encodable` 은 `passwords.py` 안 도우미 하나.
- **새 시험이 값을 단언한다.** 수정을 되돌리는 변이 5종이 전부 구현자 시험으로 잡힌다: RM-1(로그인 형식 문 제거) · RM-2(가입 UTF-8 검사 제거) · RM-3(형식 위반 아이디는 더미 해시 건너뜀) · RM-4(`verify_password` 명시적 분기 제거) · RM-5(실패 코드를 `invalid_username` 으로). 1차에 살아남았던 VM-3·VM-4·VM-5·VM-12·VM-13 도 이제 구현자 시험으로 잡힌다(R-1·R-2·R-3 닫힘). R-8(낡은 docstring)도 고쳐졌고, `tests.md` 124행이 V2-9b 설명을 정정했다.

### 10.3 남은 [권고]

- **R-4**(`AUTH_COOKIE_SECURE` 오타를 기동 때 잡기) · **R-5**(`Origin` 헤더 둘 — VM-6 생존) · **R-6**(저장 해시 `n` 상한) · **R-7**(500 로그의 SQL 파라미터, U2 밖 FIX 후보) · **R-9**(registry 행 · 세션 행 누적 · 응답 뒤 커밋) — 1차 그대로 열려 있다. 커밋을 막지 않는다.
- **R-10(새로 관찰) 비밀번호 끝의 NUL 은 구별되지 않는다.** 퍼즈에서 비밀번호 `fuzzreal` 로 만든 계정에 `fuzzreal\x00` 로 로그인이 됐다(`recheck-who200`). 구현 결함이 아니라 scrypt(안쪽 PBKDF2-HMAC)의 성질이다 — HMAC 은 블록(64바이트)보다 짧은 키를 0 으로 채우므로 끝에 NUL 을 붙인 비밀번호가 같은 해시를 낸다(`hashlib.scrypt` 로 직접 확인: 끝 NUL 1·2개는 같음, 앞·가운데 NUL 은 다름). 공격자가 얻는 것은 없다(원래 비밀번호를 알아야 한다). 비밀번호의 NUL 을 거부하는 규칙은 결정 B 밖의 새 정책이라 여기서 권하지 않고 기록만 한다.

### 10.4 판정

**통과.** 열린 [필수] 0. U2 를 커밋해도 된다. 커밋 때 R-9 ①(registry 행)을 함께 올리면 된다.
