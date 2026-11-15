# P9b-auth · 계획 검증 (02-plan-verify)

대상: 01-plan.md (개정 3 — CR-007 가입 닉네임·아이디·닉네임 중복검사) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-16 (4차)

**이 문서의 현재 판정은 4차(아래 1~4절)다.** 3차(개정 2 대상, 2026-11-15, 통과) 기록은 지우지 않고 4절 뒤 "3차 기록" 에 그대로 두었다 — `verify-plan.sh` 가 점검표 행을 `| 1 |`~`| 8 |` 로 세므로 3차 표의 행 번호에만 "3차-" 를 붙였고, 3차의 결과 줄은 "3차 결과:" 로 바꿨다(내용 불변).

4차 기준: HEAD `bfbcdb1`(dev2, `cr(CR-007)` 문서 커밋). `git diff --stat 4be331b..HEAD -- app alembic web tests` 빈 출력 — 운영 반영 해시 뒤로 제품 코드 변경 0. `CURRENT.md` `active: P9b-auth` · `frozen: CR-007`.

4차에서 본 것 — `01-plan.md` 3·4행, 32~47행(사실 15~22·개정 3 목표), 60·72~76행, 120~136행, 152~181행(API 계약 개정 3·닉네임 규칙), 275~362행(U9·U10·U11), 380~388행, 411~417·430~437행, 467~482행(결정 W~AH), 492~494행, 514~521행, 534~546행, 606~623행 · `changes/CR-007.md` 전문 · `decisions/D18-login-user-isolation.md` 결정 3·10·11, 지킬 것 4·10·11 · `specs/S3.1-schema-v2.md` 36~42행 · `security.md` §4·§5 69행 · `CLAUDE.md` 55·87행 · `docs/backlog.md` 99·100·105·122·123행 · 코드 대조: `app/auth/routes.py` 전문, `app/auth/deps.py`, `app/auth/origin.py`, `app/db/models.py` 298~315, `app/db/base.py` naming_convention, `alembic/versions/0003_auth_users.py`, `alembic/env.py`, `app/api/schemas.py` 436~467, `tests/auth_helpers.py` 50~100, `tests/test_auth_helpers.py` 55~110, `tests/test_auth_api.py` 60~90·440~640, `tests/test_auth_required_routes.py` 1~145, `tests/test_migration_0003.py` 100~125·195~236·339~358, `tests/conftest.py`(시험 DB 준비), `web/src/screens/AuthScreen.tsx` 전문, `web/src/auth.tsx`, `web/src/components/AppShell.tsx` 25~58, `web/src/api/client.ts` 40~110·183~197, `web/src/__tests__/auth.test.tsx` 74~108·205~272, `web/e2e/auth.spec.ts` 전문, `web/e2e/fixtures.ts` 30~110, `Caddyfile`, `docker/entrypoint.sh`, `docker-compose.prod.yml`, `Dockerfile` 28~47 · 전수 검색(확장자 지정)은 3절 "닫힌 목록 대조" 에 명령과 결과.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P9b-auth verify-plan-r3-v4 -- bash .claude/scripts/verify-plan.sh P9b-auth`
저장: `evidence/20261116-0702-verify-plan-r3-v4.txt`(HEAD `bfbcdb1`, exit 0 — 이 문서를 4차로 고치기 **전** 실행). architect 실행분: `evidence/20261116-0656-verify-plan-r3.txt`(HEAD `10872b7`, 같은 PASS 줄). 4차로 고친 **뒤** 다시 실행한 것은 이 절 끝에 파일 이름을 적는다.
```
== verify-plan P9b-auth  (2026-11-16 07:02) ==
PASS  존재: docs/wiki/packages/P9b-auth/01-plan.md
PASS  존재: docs/wiki/packages/P9b-auth/02-plan-verify.md
PASS  카드 존재: D16
PASS  카드 존재: D17
PASS  카드 존재: D18
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R14
PASS  Refs 있음: - [x] U1 **[backend-agent] 스키마·리비전 0003 — `users`·`auth_sess
PASS  Refs 있음: - [x] U2 **[backend-agent] 인증 코어 — 비밀번호 해시·세션 토큰·쿠키 이름 규칙·`c
PASS  Refs 있음: - [x] U3a **[backend-agent] 기존 테스트 이관(동작 불변) — `ToolContext(
PASS  Refs 있음: - [x] U3b **[backend-agent] 모든 API 를 로그인 사용자 기준으로 — 401·남의 자
PASS  Refs 있음: - [x] U4 **[backend-agent] 계정당 채팅방 하나 — 대화 기록 저장과 `GET /chat
PASS  Refs 있음: - [x] U5 **[backend-agent] 스케줄러·푸시 사용자별 — 사용자마다 브리핑 루프(0명이면 
PASS  Refs 있음: - [x] U6 **[frontend-agent] 로그인·가입 화면(관문), 로그아웃, 대화 기록 불러오기,
PASS  Refs 있음: - [ ] U7 **[메인 세션 + 사용자] 문서·로컬 통합 스모크·배포 반영·바깥 스모크** / Refs:
PASS  Refs 있음: - [ ] U8 **[사용자 + 메인 세션] 시연 계정 데이터 쌓기와 시연 두 갈래 리허설(배포 URL)**
PASS  Refs 있음: - [ ] U9 **[backend-agent] 닉네임·중복검사 백엔드 — 리비전 0004 `users.ni
PASS  Refs 있음: - [ ] U10 **[frontend-agent] 가입 화면 닉네임 칸·아이디·닉네임 "중복 확인"·`ni
PASS  Refs 있음: - [ ] U11 **[메인 세션 + 사용자] 0004 재배포 — 문서·로컬 Caddy 경유 스모크(0003
PASS  backlog 일치: 가입·로그인·로그아웃·내 정보 API 가 동작하고 비밀번호는 해시로만 저장된다 + `/health`·`/au
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: alembic/versions/0003_auth_users.py
PASS  registry 중복 없음: app/auth/__init__.py
PASS  registry 중복 없음: app/auth/passwords.py
PASS  registry 중복 없음: app/auth/sessions.py
PASS  registry 중복 없음: app/auth/deps.py
PASS  registry 중복 없음: app/auth/routes.py
PASS  registry 중복 없음: app/auth/origin.py
PASS  registry 중복 없음: app/chat/history.py
PASS  registry 중복 없음: tests/test_migration_0003.py
PASS  registry 중복 없음: tests/test_auth_passwords.py
PASS  registry 중복 없음: tests/test_auth_api.py
PASS  registry 중복 없음: tests/test_auth_origin.py
PASS  registry 중복 없음: tests/auth_helpers.py
PASS  registry 중복 없음: tests/test_auth_required_routes.py
PASS  registry 중복 없음: tests/test_user_isolation.py
PASS  registry 중복 없음: tests/test_chat_history.py
PASS  registry 중복 없음: tests/test_briefing_scheduler_users.py
PASS  registry 중복 없음: tests/test_push_endpoint_owner.py
PASS  registry 중복 없음: web/src/screens/AuthScreen.tsx
PASS  registry 중복 없음: web/src/auth.ts
PASS  registry 중복 없음: web/src/__tests__/auth.test.tsx
PASS  registry 중복 없음: docs/wiki/packages/P9b-auth/tests.md
PASS  registry 중복 없음: 03-log.md
PASS  registry 중복 없음: alembic/versions/0004_users_nickname.py
PASS  registry 중복 없음: app/auth/names.py
PASS  registry 중복 없음: tests/test_migration_0004.py
PASS  registry 중복 없음: tests/test_auth_nickname.py
PASS  registry 중복 없음: tests/test_auth_availability.py
PASS  registry 중복 없음: users.usern
PASS  registry 중복 없음: users.nickn
PASS  registry 중복 없음: err.orig.diag.const
PASS  registry 중복 없음: app/auth/names.py
== 결과: FAIL=0 WARN=0 ==
```
기계 검증이 **보지 못한 것**(R-12, 그대로 열려 있음): "의존 완료" 줄이 `P8-frontend` 하나뿐이고 P4 게이트 줄이 없다(`verify-plan.sh` 62·68행이 `P5b-`·`P9b-` 형 id 를 못 읽는다). 손 확인 — `packages/P8-frontend/04-review.md:296`·`packages/P5b-query-turn/04-review.md:244`·`packages/P4b-er-redesign/04-review.md:144` 가 각각 "결과: 완료". 이 출력의 "PASS 검증자 / 점검표 / 결과" 6줄은 실행 시점의 3차 표를 읽은 것이다 — 4차 표로 고친 뒤 재실행: (아래 한 줄)
- 4차 갱신 뒤 재실행: `evidence/20261116-0707-verify-plan-r3-v4-after.txt`(exit 0, FAIL=0 WARN=0 — PASS 줄이 위 출력과 한 줄도 다르지 않다. 4차 점검표 8행·`결과:` 줄을 읽은 결과다)

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표") — 4차, 개정 3 대상
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 아래 행 번호(275행 등)는 `bfbcdb1` 의 `01-plan.md` 기준이다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `changes/CR-007.md` 15행 "제외 칸 변동 없음 — 닉네임은 **사람(인물)이 아니라 계정의 표시 이름**이라 인물 간(A–B) 관계·고민 상담과 무관하다" ↔ 01-plan 73행 "**제품 속 에이전트가 답·브리핑에서 닉네임으로 사용자를 부르기** — 원칙7 경계 … 밖", 76행 "닉네임을 다른 사용자에게 보이는 곳(공개 프로필·계정 목록) — 범위 밖", 72행 닉네임 변경 없음, 74행 닉네임 로그인 없음, 75행 시도 제한 없음. `CLAUDE.md` 원칙7 "채팅방 목록(여러 대화방) — 계정마다 채팅방은 하나다" ↔ 339행 "채팅방 목록은 여전히 없다(원칙7)". 하지 않는 것 5줄이 명시돼 있다. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙7 경계 — `CLAUDE.md` "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다" ↔ 결정 AE(479행) "`/auth/*` 응답과 사이드바뿐 — 에이전트 답·브리핑·툴 입력에 쓰지 않음". 실물: `app/` 에서 `username` 을 읽는 곳은 `app/auth/*`·`app/api/schemas.py`·`app/db/models.py`·`app/settings.py` 뿐이고 `Depends(current_user)` 15곳은 `user.id` 만 넘긴다(3절 명령 ⑥) → U9 범위 판정(315행 `u9-scope` "산출물 표의 U9 행과 닫힌 목록 파일만")이 지켜지면 닉네임이 프롬프트·툴로 갈 길이 없다. 원칙5 — `CLAUDE.md` "화면 수를 고정하지 않는다 … UI에 시간을 쓰지 않는다" ↔ 493행 "새 화면 없음 — 관문 화면에 칸·버튼을 더할 뿐". 원칙9 — 494행 "조회 API·가입은 판정이 아니라 trace 0", 312행 시험 "가입이 `persons`·`person_aliases`·`agent_traces` 행을 만들지 않는다", 313행 "쓰기 0". 원칙1~4·8 — 494행 `git diff --stat <기준>..HEAD -- app/er evaluation reports data` 빈 출력(공통 회귀 427행). |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `decisions/D18-login-user-isolation.md` 지킬 것 4 "**(CR-007 보충)** 예외에 `GET /auth/availability` 하나를 더한다 — 계약 테스트(`tests/test_auth_required_routes.py`)의 면제 목록도 이름으로 함께 고친다" ↔ B15(306행) "`("GET", "/auth/availability")` 를 **두 곳 모두**에 추가 → 8"; 실물 `tests/test_auth_required_routes.py:34-42`(`_EXEMPT`)·`103-111`(등식) 두 곳이 맞다. 지킬 것 10 "가입과 조회는 같은 정규화 함수 하나를 쓰고, DB UNIQUE 는 그 함수가 돌려준 값에 건다" ↔ 285행 `normalize_nickname(raw) -> str \| None` "가입·조회가 이 함수 하나만 쓴다", 179행 "앱 정규화 값 = DB 비교 대상(함수 인덱스 없음)". 지킬 것 10 "형식 위반(NUL·제어문자·짝 없는 서로게이트 포함)은 **DB 에 묻기 전에** 422" ↔ 162행 "①~③ 은 **DB 조회 0**"; 실측 `evidence/20261116-0704-planverify4-nickname-probe.txt` — NUL·짝 없는 서로게이트·10만 자 모두 예외 없이 `None`(단 앞뒤의 공백류 제어문자는 정규화가 지운다 — R4-1). 지킬 것 11 "중복 조회 API 는 읽기 전용이다(쓰기·`agent_traces`·LLM 호출 0). 로그인 응답(…같은 401)은 바꾸지 않는다" ↔ 163행·157행 "401 `invalid_credentials` — 변경 없음". 결정 11 "둘 다 겹치면 `username_taken`" ↔ 162행 ④→⑤ 순서, 변이 V9-7. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.1-schema-v2.md` 38행 "users(+ nickname) -- Text NOT NULL, UNIQUE uq_users_nickname(정규화한 값: NFC·앞뒤 공백 제거·영문 소문자)" ↔ 282행 `mapped_column(Text, nullable=False)`·`UniqueConstraint("nickname")`; 이름은 실물 `app/db/base.py` naming_convention `uq_%(table_name)s_%(column_0_N_name)s` → `uq_users_nickname`. 42행 "① `nickname` 을 nullable 로 추가 ② 기존 행을 `nickname = username` 으로 채움 … ③ NOT NULL ④ UNIQUE. **데이터를 지우지 않는다**" ↔ 283행 upgrade ①~④ 같은 순서·"`DELETE`·`TRUNCATE`·`DROP` 0", downgrade "계정 행은 남고 닉네임 값만 사라진다". 41행 "DB CHECK 는 두지 않는다" ↔ 282행. 툴 7종·임계치·`ask_user` 는 건드리지 않는다(`CR-007.md` 26행 "S3.2 … S3.7 **무변경**", 판정 #11 `tools_check` 7/7). |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 01-plan 5행 "의존: P8-frontend(완료 …) — 충족 · P5b-query-turn(완료 2026-11-09, `f67d8e4`) — 충족 · P4 게이트(P4b 통과 2026-09-23) — 충족" — 세 `04-review.md` "결과: 완료"(1절 손 확인). U9 의존(281행) "U5 커밋(`ca539a1` — 충족)" — `git cat-file -t ca539a1` = commit, `4be331b`(운영 반영)·`f93e7e6`(바깥 스모크)도 존재하고 `4be331b` 는 HEAD 의 조상. 단위 순서 277행 "U9 ∥ U10 → U11 → U8" — U9(`app/`·`alembic/`·`tests/`)와 U10(`web/`)은 파일이 겹치지 않고(120~136행 표), 279행 ①~④ 가 커밋 시점마다 전체 시험이 서는지를 따졌다(3절 "U9 ∥ U10" 에서 대조). U11 의존(356행) "U9·U10 각 verifier 리뷰 통과 + 반영할 해시 … 에서의 전체 pytest·Vitest 증거". |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 99행 "수용기준: 가입·로그인·로그아웃·내 정보 API 가 동작하고 … + (CR-007) 리비전 0004 가 기존 계정을 지우지 않고 닉네임을 아이디 값으로 채우며 `alembic upgrade head`·`alembic check` 통과, 배포 URL 에서 반영 전 계정이 그대로 로그인되고 닉네임이 보인다" ↔ 01-plan 435행 — 두 문자열을 스크립트로 비교해 `True`(각 1092자, 3절 명령 ⑦). `verify-plan` "PASS backlog 일치". 앞 구절 "`/health`·`/auth/signup`·`/auth/login` 밖의 모든 API 가 로그인 없이 401" 과 뒤 구절 "이 조회는 … 함께 로그인 없이 열린 예외다" 는 437행 주("판정 #2 는 #16 과 함께 읽는다")와 판정 #16(413행 "면제 8 = 공개 4 + 문서 4, 그 밖 전부 401")으로 한 판정이 된다. 판정 #14~#20 은 전부 명령·기대값이 있다(411~417행). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 281행 U9 "/ Refs: P9b-auth CR-007 D18 S3.1 security 원칙7 원칙9" · 333행 U10 "/ Refs: P9b-auth CR-007 D18 원칙5 원칙7" · 356행 U11 "/ Refs: P9b-auth CR-007 D18 D17 security"(`verify-plan` "PASS Refs 있음" 12줄 — U1~U11). |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | §5 69행 "닉네임은 계정 표시용으로만 저장한다 — 다른 계정에 보이는 곳 0, `agent_traces`·툴 입력·`pending_questions.context` 에 넣지 않는다 … 가입 409 가 이미 같은 정보를 주므로 새로 드러나는 정보는 없지만 묻는 비용이 낮아진다" ↔ 164행 "계정 열거와의 관계(사실)" — 실물 `app/auth/routes.py:108-114` 가 지금도 409 `username_taken` 을 낸다(형식·비밀번호 검사 뒤라 유효한 비밀번호가 필요하고, 안 쓰이는 아이디면 계정이 만들어진다 — "비용만 낮춘다" 는 서술과 맞다). §4 "셸에서 `DROP`/`TRUNCATE` 금지 → Alembic 마이그레이션 파일로" ↔ 283행(리비전 안에서도 삭제문 0), 314행 "`DROP DATABASE` 0", 358행 "볼륨 삭제·`down -v` 0". §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T` …) 금지" ↔ 361행 "바깥 스모크(메인, 본문 없는 GET 만 — security §4)", 가입 POST 는 로컬 Caddy 스모크(358행)로만. §1 ↔ 358행 "비밀번호는 스크래치패드 파일로만, 증거에는 `***`", 429행 "증거에 비밀번호·쿠키 값 0". 422 본문 되울림 — 287행 "같은 `router` — `_NoInputEchoRoute` 가 쿼리 422 에도 적용"(실물 `routes.py:51-75`). |

## 3. 소견과 조치 — 4차

증거 파일: `evidence/20261116-0702-verify-plan-r3-v4.txt`(기계 검증) · `evidence/20261116-0704-planverify4-nickname-probe.txt`(닉네임 규칙 실측 — 저장소 무수정, DB·네트워크 접근 0). 그 밖의 근거는 코드·테스트 파일:줄과 아래 명령.

### 직접 실행한 명령(읽기 전용)
① `bash .claude/scripts/gitlog.sh P9b-auth CR-007 D18` ② `grep -rnE '/auth/signup|signup\(' --include='*.py' app tests scripts evaluation alembic` ③ `grep -rniE 'password_hash\s*=|into\s+users|users\s*\(' --include='*.py' --include='*.sh' --include='*.sql' --include='*.yml' --include='*.md' app tests scripts evaluation alembic infra .github` + `grep -rnE 'INSERT INTO users|\bUser\(' --include='*.py' …` ④ `grep -rn 'make_user\b' --include='*.py' .` ⑤ `grep -rnE "signup|username|auth/me|auth/login|MeOut|Credentials" web/src web/e2e --include='*.ts' --include='*.tsx'` ⑥ `grep -rnE "\.username|username" --include='*.py' app`(인증 4파일 밖 결과: `app/config.py:84` URL 파싱 1줄뿐) ⑦ 수용 기준 문자열 비교(파이썬 한 줄, 결과 `True 1092 1092`) ⑧ `grep -rnE '"0003"|0003\b|downgrade' --include='*.py' tests scripts app` ⑨ `.venv/bin/python` 으로 `psycopg 3.3.5`·`sqlalchemy 2.0.50`·`fastapi 0.135.1`·`starlette 1.7.0`, `hasattr(psycopg.Error, 'diag')` = True ⑩ 닉네임 규칙 실측(증거 파일) ⑪ `git diff --stat 4be331b..HEAD -- app alembic web tests`(빈 출력).

### 따져 본 10가지

1. **닫힌 목록의 완전성(B1~B17·F1~F4) — 목록 밖에서 깨질 곳을 찾지 못했다.**
   - 가입을 부르는 시험: `tests/test_auth_api.py` 38곳(`_signup` 69-70 경유 + 직접 본문 551·607 + 183·184·461 은 본문 오류라 여전히 4xx) · `tests/test_auth_origin.py:103`(B14)·`117` · `tests/test_auth_required_routes.py:138`(빈 본문 422). 계획 사실 18 과 같다. `scripts/`·`evaluation/`·`alembic/` 에는 없다.
   - `users` 행을 만드는 곳: `app/auth/routes.py:105`, `tests/auth_helpers.py:65`(`make_user` — B17), 원시 SQL 은 `tests/test_migration_0003.py:233·234·248·259·269` 5문장(B8)뿐. `make_user` 를 부르는 `tests/test_user_isolation.py`·`tests/test_push_endpoint_owner.py`·`tests/test_auth_helpers.py` 는 기본 닉네임 = 그 행의 아이디라 손댈 곳이 없다(아이디가 이미 UNIQUE).
   - `_signup` 기본 닉네임 = 아이디 인자(B9)로 기존 시험이 서는지: 아이디 규칙 `[a-z0-9_]{3,20}` ⊂ 닉네임 규칙이고 검사 순서가 아이디 → 비밀번호 → 닉네임이라, 아이디 위반 시험은 여전히 `invalid_username`, 비밀번호 위반 시험은 `invalid_password`, 같은 아이디 재가입은 "둘 다 겹침 → `username_taken`" 으로 지금 단언과 같다.
   - 리비전 문자열: `tests/test_api.py:93`(B4), `tests/test_migration_0003.py:218·219·358`(B6·B7)뿐. 시험 DB 는 세션마다 `alembic upgrade head`(`tests/conftest.py` 19~21행)라 0004 로 올라간다. 병렬 실행 설정(xdist)은 없다 — `test_migration_0003.py`·`test_migration_0004.py` 가 같은 전용 DB 를 차례로 쓴다.
   - 프론트: `web/e2e/` 에 가입 흐름은 없다(`auth.spec.ts` 는 로그인·로그아웃만, `fixtures.ts:45` 는 `/auth/me` 기본 응답). 가입 본문 단언은 `auth.test.tsx:270` 하나(F3). `sidebar-username` 단언 5곳은 글자가 아이디 그대로라 유지된다. 목 응답에 `nickname` 이 없어도 타입 검사는 통과한다(JSON 리터럴) — "바꿔도 되는 목 데이터" 분류가 맞다. 라우트 수·OpenAPI·`AUTH_NOTICE` 키 수를 세는 시험은 없다.
2. **리비전 0004 — 순서·백필·UNIQUE·downgrade 모두 맞다.** nullable 추가 → 백필 → NOT NULL → UNIQUE(283행). 백필 값: 실측에서 아이디 규칙 표본 200000개 전부 `norm(username) == username`(증거 파일) — 아이디는 ASCII 소문자·숫자·밑줄 3~20자라 NFC·strip·lower 가 값을 바꾸지 않고 닉네임 정규식 안이다. `username` 이 UNIQUE(`uq_users_username`, 0003)라 백필 뒤 닉네임도 서로 다르다. `alembic/env.py:118` `context.begin_transaction()` — 실패하면 0003 에 남는다. downgrade 는 제약·컬럼만 지운다. 시험 DB 의 `helper-…` 아이디(하이픈)는 DB CHECK 가 없어 백필을 막지 않는다(계획 사실 21 과 같다).
3. **가입 판정 순서와 경합 — 드라이버에서 제약 이름이 읽힌다.** `requirements.txt:4` `psycopg[binary]==3.3.5`(asyncpg 아님). `err.orig.diag.constraint_name` 은 이미 `tests/test_migration_0003.py:236` 이 `== "uq_users_username"` 으로 단언하고 있고 그 시험은 기준선(2515 passed)에 들어 있다. ①~③ DB 조회 0 → ④⑤ 사전 조회 → ⑥ 세이브포인트 INSERT 는 지금 코드(`routes.py:108-114` `begin_nested`)의 확장이다. "그 밖의 제약이면 다시 올린다" 도 맞다(다른 결함을 409 로 숨기지 않음).
4. **`GET /auth/availability` — 글자·시험 수준에서 모순 없이 정리됐다.** D18 결정 3·지킬 것 4, `CLAUDE.md` 55행("네 번째 예외"), backlog 99행, 01-plan 435·437행이 모두 "원래 문장 + CR-007 보충" 꼴로 같은 네 경로를 말한다. 시험은 B15 가 두 곳을 이름으로 고친다. Caddy: `Caddyfile` `handle_path /api/*` 가 접두를 떼므로 백엔드 경로는 `/auth/availability` — 맞다(`@docs` 매처에 걸리지 않는다). GET 이라 `OriginCheckMiddleware`(`origin.py:29` `UNSAFE_METHODS`) 대상이 아니다. 계정 열거 서술은 사실과 맞다(점검표 8행). 남는 문장 어긋남은 R4-9.
5. **닉네임 정규화 — 500 경로를 찾지 못했다. 한 가지 서술이 실제와 다르다(R4-1).** `unicodedata.normalize("NFC", …)` 는 짝 없는 서로게이트에 예외를 내지 않는다(Python 3.14.7 실측, 10만 자 포함). NUL·제로폭·BOM·자모·옛한글·한자·이모지·전각 영문은 정규식에서 걸린다. 계획 521행의 미확인 항목은 이 실측으로 닫힌다. 다만 `str.strip()` 은 U+001C~001F·U+000B·U+000C·U+0085·U+2028 도 공백으로 보고 지운다 → `"\x1f민지"` 는 422 가 아니라 **`민지` 로 통과**한다. 규칙 표 177행 "제어문자 … → 가입 422" 는 "가운데 있거나 공백류가 아닌 제어문자" 에만 참이다. 저장 값에는 제어문자가 남지 않으므로 결함은 아니고, 시험 값이 정해져 있지 않은 것이 문제다.
6. **U9 ∥ U10 — 파일이 겹치지 않고 계약 표는 닫힌 값이다.** 경로·쿼리 키·응답 모양·상태값 3개·오류 코드·문구(338행)·testid·`role`·버튼 이름이 모두 값으로 있다. U9 만 커밋된 구간에서 프론트 시험은 목 응답이라 그대로 서고, U10 만 커밋된 구간에서 pytest 는 무관하다(279행 ①②). 배포는 둘 다 든 해시만(③). 겹치는 것은 위키 파일뿐이다(R4-7). 화면 상태 두 가지가 비어 있다(R4-6).
7. **U11 — 스모크는 실제 0003 볼륨에서 `0003 -> 0004` 를 본다. 비상 되돌리기 명령은 계획에 없다(R4-3).** 358행이 볼륨 재사용·적용 줄·행 수 불변(9)·`nickname = username` 수·기존 계정 로그인·조회·가입 201·409·403·health `0004` 를 요구하고 "실패하면 재배포하지 않는다" 로 끝난다. 재배포 명령(360행)은 `docker/entrypoint.sh` 의 `python -m alembic upgrade head` 와 맞다(따로 alembic 을 치지 않는다). 비상 경로는 357행이 "정확한 명령 형태는 메인이 … 대조해 적는다" 로 미뤄 대조할 명령이 없다.
8. **원칙 7 경계 — 막혀 있다. 전용 판정 명령은 없고 범위 판정이 대신한다(R4-10).** 점검표 2행.
9. **일정 — 축소 경로의 분류가 맞다.** 조회 API 를 빼는 축소 3 은 "사용자 결정 — 메인이 묻기 전에는 적용하지 않는다"(386행), `4be331b` 로 평가하는 것은 사용자 할 일 11(b)(536행)에 있다. "재배포하지 않는다" 는 되돌릴 것이 없는 쪽이라 기본값으로 두어도 안전하다. 달력(P9c)·시연 계정 가입 시점은 사용자 할 일 10·9 로 분류돼 있으나 **묻는 시점이 계획에 없다** — 아래 "사용자에게 올릴 것".
10. 점검표 8행 — 2절.

### [필수]
없음.

### [권고] — R4-1·R4-2·R4-3 은 위임 프롬프트(또는 01-plan 에 메인이 덧붙이는 줄)에 한 줄씩 넣기를 권한다. 판정에 영향이 없어 재검증 없이 해도 된다

- **R4-1 (U9 새 시험의 "제어문자" 값 고정 — 177행·312행)** 실측(`evidence/20261116-0704-planverify4-nickname-probe.txt`): `"\x1f민지"`·`"민지\x1c"`·`"\x0b민지"`·`"민지\x85"`·`"민지 "` → `'민지'`(통과), `"\x01민지"`·`"민\x01지"`·`"민지\x7f"`·`"​민지"`·`"﻿민지"` → 위반. 시험 작성자가 앞뒤 공백류 제어문자를 고르면 201 이 나와 규칙 표 177행과 175행이 서로 다른 답을 주고 "멈추고 보고" 가 걸린다. → 312행 "NUL·제어문자·…" 를 "NUL(`"\x00"`·`"a\x00b"`)·공백류가 아닌 제어문자(`"민\x01지"`·`"민지\x7f"`)·제로폭(`"​민지"`)" 로, 177행에 "앞뒤의 공백류 제어문자(U+0009~000D·U+001C~001F·U+0085·U+2028 등)는 175행대로 제거된다 — `"\x1f민지"` → `민지`" 한 문장을 더한다. D18 지킬 것 10 의 "제어문자" 도 같은 뜻(정규화 뒤 남은 것)으로 읽는다.
- **R4-2 (B15 의 새 단언 — 306행)** `tests/test_auth_required_routes.py` 의 `bare_client`(83~95행)는 엔진에 묶이지 않은 `Session()` 을 끼운다. 조회 API 를 **유효한 값**으로 부르면 DB 조회에서 오류(500)가 난다. → `test_public_routes_stay_open` 에 더하는 단언은 쿼리 없음(422 `missing_query`)이나 `?username=`(200 `"invalid"`)처럼 **DB 에 가지 않는 요청**으로만 쓴다. 계획의 "(200/422)" 를 이 두 요청으로 못박는다.
- **R4-3 (U11 비상 되돌리기 명령 — 357행·결정 AH)** 명령이 없고 예행 단계도 없다. 읽어서 확인한 사실: `docker-compose.prod.yml:43` backend `restart: unless-stopped`, `docker/entrypoint.sh:10` 이 기동마다 `alembic upgrade head`, 이미지 태그는 `relationship-backend:${GIT_SHA:-local}`(42행). 따라서 떠 있는 새 backend 에 `exec` 로 downgrade 하면 ① 그 사이 새 코드가 0003 스키마에서 돈다 ② 컨테이너가 재시작하면 entrypoint 가 다시 0004 로 올린다. 맞는 순서로 보이는 것(**실행해 보지 않았다**): 새 해시 체크아웃 상태에서 `docker compose -f docker-compose.prod.yml stop backend` → `GIT_SHA=<새 해시> docker compose -f docker-compose.prod.yml run --rm --entrypoint python backend -m alembic downgrade 0003` → `git checkout 4be331b` → `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`. → U11 로컬 Caddy 스모크 끝에 이 순서를 로컬 볼륨에서 한 번 돌려(되돌린 뒤 `users` 행 수 그대로 → 다시 새 해시로 올려 `0003 -> 0004`) 증거를 남긴 다음에만 13 문서에 적는다. 예행하지 않으면 문서에 "검증되지 않은 명령" 이라고 적거나 결정 AH 를 (ii) "앞으로만" 으로 둔다.
- **R4-4 (조회 API 의 서로게이트·긴 값 시험 — 313행)** 쿼리 문자열로는 짝 없는 서로게이트가 서버에 닿지 않는다 — `%ED%A0%80` 은 U+FFFD 3개로 풀린다(증거 파일 `parse_qsl` 줄). httpx 의 `params=` 에 서로게이트 문자열을 주면 클라이언트 쪽에서 인코딩 오류가 난다. → 시험은 원시 경로 `"/auth/availability?nickname=%ED%A0%80"` 로 쓰고 기대는 `"invalid"`. NUL 은 `%00` 으로 실제로 닿는다(U+0000) — V9-10 은 유효하다. 10만 자 쿼리는 TestClient 에서만 앱에 닿는다(실서버에서 uvicorn·Caddy 가 먼저 거르는지는 확인하지 않았다 — 어느 쪽이든 500 은 아니다).
- **R4-5 (U9 파일 목록 밖 문장 1곳)** `app/auth/__init__.py:7` "`routes` -- `/auth/signup`·`/auth/login`·`/auth/logout`·`/auth/me`" 가 낡는다. 고치면 `u9-scope` 판정(315행)에 걸리므로 산출물 표 U9 행에 더하거나 "그대로 둔다" 를 정한다.
- **R4-6 (U10 화면 상태 두 가지)** ① "중복 확인" 응답이 오기 전에 값을 바꾸면 늦게 온 응답이 바뀐 값 아래에 옛 결과를 그린다 — 337행 "값이 바뀌면 그 칸의 결과를 지운다" 만으로는 막히지 않는다(요청 때 값과 지금 값이 다르면 버린다 — `web/src/auth.tsx:39` `latest` 와 같은 방식). ② 가입 ↔ 로그인 전환(`AuthScreen.tsx:61-66` `switchMode`) 때 닉네임 값·확인 결과를 지우는지 정해져 있지 않다. ③ 가입 화면 E2E 를 쓰게 되면 `page.getByLabel('아이디')` 는 부분 일치라 `aria-label="아이디 중복 확인"` 버튼까지 잡는다 → `{ exact: true }`.
- **R4-7 (U9 ∥ U10 의 위키 파일)** 두 에이전트가 `packages/P9b-auth/03-log.md`·`tests.md` 를 같이 고친다 — 제품 파일은 겹치지 않지만 이 둘은 겹친다. 메인이 차례로 받거나 절을 나눠 준다(U2 ∥ U6 때와 같다).
- **R4-8 (U11 스모크의 기존 계정 로그인)** 358행 "기존 스모크 계정으로 `POST /api/auth/login` 200" 은 U7 때 스크래치패드에 둔 비밀번호 파일에 기댄다. 지금은 `…/scratchpad/p9b-u7/` 가 있다(파일 이름만 확인, 내용은 읽지 않았다). 재부팅으로 사라지면 0003 시절 계정으로 로그인할 수 없다 → 그때는 새 이미지를 빌드하기 **전에** `relationship-*:4be331b` 이미지로 한 번 띄워 계정 하나를 가입해 두고 시작한다.
- **R4-9 (문장 어긋남 3곳 — 판정에는 영향 없음)** ① 판정 #2(399행) 괄호 "예외는 이 3개 + 문서 경로뿐" 이 #16 "면제 8" 과 글자로 다르다(437행 주가 잇는다) — 04-review 에서 구절 2 는 #16 과 함께 판정한다 ② `docs/backlog.md:100` "세분화는 … (U1·U2·U3a·U3b·U4~U8)" 에 U9~U11 이 없다(`CR-007.md` 39행은 "세분화 줄" 을 고친다고 적었다) ③ `security.md` 69행·`CR-007.md` 33행 "접근 로그(uvicorn·Caddy)" — `Caddyfile` 에 `log` 지시문이 없어 Caddy 접근 로그는 남지 않는다(uvicorn 쪽만).
- **R4-10 (원칙7 전용 판정 한 줄)** 지금은 범위 판정(`u9-scope`)과 "행을 만들지 않는다" 시험이 간접으로 막는다. `grep -rln nickname app --include='*.py'` 의 결과가 `app/db/models.py`·`app/settings.py`·`app/api/schemas.py`·`app/auth/routes.py`·`app/auth/names.py` 뿐임을 U9 판정에 더하면 "닉네임이 에이전트·브리핑·툴 코드에 없다" 가 한 줄로 보인다(스크립트로, exit 0 + 목록 대조).
- **R4-11 (결정 Y — 화면 표기가 바뀐다)** 영문 닉네임은 소문자로 저장·표시된다(`Demo` → `demo`, 실측). 권장안 채택 범위 안이지만 사용자가 시연에서 직접 보게 되는 동작이라 아래 질문 묶음에 한 줄로 알린다.
- **R-12 (1차, 하네스)** `verify-plan.sh` 62·68행 — 이 패키지 밖, 그대로 열려 있다.

### 사용자에게 올릴 것 — **U9 위임 전에** 한 번에
계획은 아래를 "사용자만 할 수 있는 일" 9~11(534~536행)로 옳게 분류했다. 권장안으로 넘긴 것은 없다. 다만 **묻는 시점이 적혀 있지 않고**, 9·10 은 U9 를 시작하면 사실상 정해지므로 위임 전에 물어야 한다.
1. **달력(P9c)을 평가 전에 넣지 않게 되는 것**(할 일 10). 사용자는 11-15 에 달력 보기를, 11-16 에 닉네임을 요청했다. 닉네임을 먼저 하면 P9c 포기 시점(11-17 12:00)을 넘긴다(514행). "닉네임 먼저" 는 메인 지시(382행)이고 사용자 답 기록은 `HANDOFF.md`·`journal.md` 에 없다.
2. **시연 계정을 언제 만들지**(할 일 9). 닉네임 변경 기능이 없어(결정 AG) U11 반영 전에 만든 계정은 닉네임이 아이디로 굳는다. 사용자가 오늘 배포본에서 시연 데이터를 쌓기 시작하면 그 계정이 그렇게 된다 — 지금 알려야 한다.
3. 영문 닉네임은 소문자로 보인다(R4-11) · 운영의 `test` 계정 닉네임은 `test` 가 된다.
4. 일정이 밀릴 때의 두 기준(할 일 11 — 11-17 10:00 축소, 18:00 까지 재배포 못 하면 `4be331b` 로 평가)을 그대로 쓸지.

### 검증하지 못한 것
- 전체 pytest·Vitest 를 돌리지 않았다 — 닫힌 목록은 전수 검색과 파일 대조로 판정했다. 검색 패턴 밖의 방식으로 `users` 컬럼·가입 본문에 기대는 시험이 있으면 계획의 "목록 밖 테스트가 깨지면 멈추고 보고"(288행)가 받는다.
- DB 에 접속하지 않았다 — 변이용 전용 DB `relationship_test_mig_v15` 가 "이미 있음"(316행), 로컬 운영 볼륨 계정 9개·개발 DB 계정 3개(사실 21)는 03-log 기록으로만 보았다.
- 비상 되돌리기 순서(R4-3)와 U11 스모크는 실행하지 않았다(계획 검증 단계).
- jsdom 이 `required` 빈 칸에서 제출을 막는지는 실행해 보지 않았다 — F2 가 네 시험 모두에 닉네임을 넣으므로 어느 쪽이든 선다.
- 배포 서버에는 요청을 보내지 않았다.

## 4. 결정
결과: 통과
사유: 점검표 8행 통과, [필수] 0건. 개정 3(U9·U10·U11)이 3차까지 통과한 기존 부분과 부딪히는 곳을 찾지 못했다 — 닫힌 목록 B1~B17·F1~F4 는 전수 검색에서 빠진 곳이 없고, 리비전 0004 의 순서·백필 값·UNIQUE·downgrade 가 S3.1 보충과 같으며, 제약 이름은 이 프로젝트의 드라이버(psycopg 3)에서 이미 시험으로 읽히고 있고, 닉네임 정규화는 NUL·짝 없는 서로게이트·10만 자에서 예외 없이 위반으로 끝난다(실측 증거). 남은 것은 [권고] R4-1~R4-11 과 하네스 R-12 이며, R4-1(제어문자 시험 값)·R4-2(`bare_client` 에서 조회 API 를 부르는 방식)·R4-3(비상 되돌리기 명령과 예행)은 위임·U11 전에 한 줄씩 더하기를 권한다. 사용자에게 올릴 것 1·2 는 U9 위임 전에 묻는다.
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다 — 이번에는 `frozen: none` 으로 동결을 푼다.)

---

# 3차 기록 (2026-11-15, 개정 2 대상 — 결과 통과. 아래는 그때의 문서 그대로이며 절 머리와 표 행 번호에만 "3차-" 를 붙였다)

3차 기준: HEAD `08c1b49`(dev2). **3차 검증**이다.
- 1차(HEAD `5c0f26d`) 결과 보류 — [필수] F-1~F-7 · [권고] R-1~R-13 → 개정 1.
- 2차(HEAD `08c1b49`) 결과 보류 — [필수] N-1~N-4 · [권고] R2-1~R2-4 → 개정 2.
- 3차(이 문서) — 개정 2 를 architect 의 "반영했다" 보고가 아니라 계획 본문과 코드·테스트로 다시 대조했다.

3차에서 본 것 — `01-plan.md` 1~30행·60~100행·101~180행·193~200행·220~246행·278행·289~293행·341~381행(개정된 곳 전부) · 2차에서 읽은 카드(`decisions/D18-login-user-isolation.md`, `specs/S3.1`·`S3.4`·`S3.6`, `security.md`)는 그 뒤 바뀌지 않았다(`git status --short` 에 카드 변경 없음) · 전수 검색: 스키마·리비전 단언(`tests/test_schema_models.py` 150~320행 전부, `tests/test_schema_check.py`, `scripts/schema_check.py` 숫자 비교 줄, 저장소 전체 `0002|alembic_revision`), `app_user_id|APP_USER_ID`(위키 밖 저장소 전체), `X-Session-Id`·`invalid_session_id`·`session_id` 단언(`tests/` 전체), `PendingQuestion(`(`app`·`scripts`·`evaluation`·`tests`), 한 테스트 안에서 세션 id 를 둘 이상 쓰는 곳(구문 분석 스크립트, 0건), `app/api/deps.py` 조립 함수를 직접 부르는 테스트 · N-4 대조: `app/briefing/run.py` 168~335, `app/briefing/scheduler.py` 전문, `app/push/notifier.py:252-270`, `tests/test_push_wiring.py` 159~174·296~400, `tests/test_briefing_scheduler.py` 153~206.

## 3차-1. 기계 검증 출력 (2026-11-15, 개정 2 대상)
명령: `python3 .claude/scripts/save_evidence.py P9b-auth verify-plan -- bash .claude/scripts/verify-plan.sh P9b-auth`
저장: `evidence/20261115-2051-verify-plan.txt` (이 문서를 3차 판정으로 갱신한 뒤 실행, exit 0). 이전 실행: 1차 `evidence/20261115-2021-verify-plan.txt` · 2차 `evidence/20261115-2039-verify-plan.txt`.
```
== verify-plan P9b-auth  (2026-11-15 20:51) ==
PASS  존재: docs/wiki/packages/P9b-auth/01-plan.md
PASS  존재: docs/wiki/packages/P9b-auth/02-plan-verify.md
PASS  카드 존재: D16
PASS  카드 존재: D18
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R14
PASS  Refs 있음: - [ ] U1 **[backend-agent] 스키마·리비전 0003 — `users`·`auth_sess
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인증 코어 — 비밀번호 해시·세션 토큰·쿠키 이름 규칙·`c
PASS  Refs 있음: - [ ] U3a **[backend-agent] 기존 테스트 이관(동작 불변) — `ToolContext(
PASS  Refs 있음: - [ ] U3b **[backend-agent] 모든 API 를 로그인 사용자 기준으로 — 401·남의 자
PASS  Refs 있음: - [ ] U4 **[backend-agent] 계정당 채팅방 하나 — 대화 기록 저장과 `GET /chat
PASS  Refs 있음: - [ ] U5 **[backend-agent] 스케줄러·푸시 사용자별 — 사용자마다 브리핑 루프(0명이면 
PASS  Refs 있음: - [ ] U6 **[frontend-agent] 로그인·가입 화면(관문), 로그아웃, 대화 기록 불러오기,
PASS  Refs 있음: - [ ] U7 **[메인 세션 + 사용자] 문서·로컬 통합 스모크·배포 반영·바깥 스모크** / Refs:
PASS  Refs 있음: - [ ] U8 **[사용자 + 메인 세션] 시연 계정 데이터 쌓기와 시연 두 갈래 리허설(배포 URL)**
PASS  backlog 일치: 가입·로그인·로그아웃·내 정보 API 가 동작하고 비밀번호는 해시로만 저장된다 + `/health`·`/au
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: alembic/versions/0003_auth_users.py
PASS  registry 중복 없음: app/auth/__init__.py
PASS  registry 중복 없음: app/auth/passwords.py
PASS  registry 중복 없음: app/auth/sessions.py
PASS  registry 중복 없음: app/auth/deps.py
PASS  registry 중복 없음: app/auth/routes.py
PASS  registry 중복 없음: app/auth/origin.py
PASS  registry 중복 없음: app/chat/history.py
PASS  registry 중복 없음: tests/test_migration_0003.py
PASS  registry 중복 없음: tests/test_auth_passwords.py
PASS  registry 중복 없음: tests/test_auth_api.py
PASS  registry 중복 없음: tests/test_auth_origin.py
PASS  registry 중복 없음: tests/auth_helpers.py
PASS  registry 중복 없음: tests/test_auth_required_routes.py
PASS  registry 중복 없음: tests/test_user_isolation.py
PASS  registry 중복 없음: tests/test_chat_history.py
PASS  registry 중복 없음: tests/test_briefing_scheduler_users.py
PASS  registry 중복 없음: tests/test_push_endpoint_owner.py
PASS  registry 중복 없음: web/src/screens/AuthScreen.tsx
PASS  registry 중복 없음: web/src/auth.ts
PASS  registry 중복 없음: web/src/__tests__/auth.test.tsx
PASS  registry 중복 없음: docs/wiki/packages/P9b-auth/tests.md
PASS  registry 중복 없음: 03-log.md
== 결과: FAIL=0 WARN=0 ==
```
기계 검증이 **보지 못한 것**(1차 R-12, 그대로 열려 있음): `verify-plan.sh` 62행 정규식이 `P5b-query-turn` 을 잡지 못해 "의존 완료" 줄이 `P8-frontend` 하나뿐이고, 68행 `sed` 가 `P9b-auth` 에서 숫자를 뽑지 못해 P4 게이트 줄이 출력에 없다. 손 확인 — `packages/P5b-query-turn/04-review.md`·`packages/P4b-er-redesign/04-review.md`·`packages/P8-frontend/04-review.md` 모두 "결과: 완료".

## 3차-2. 정합성 점검표 (2026-11-15, 개정 2 대상 — 행 번호 앞에 "3차-" 를 붙여 4차 점검표와 구분한다. 내용은 그대로)
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 3차-1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, **채팅방 목록(여러 대화방)** — 계정마다 채팅방은 하나다." ↔ 01-plan 50행 "**채팅방 목록(여러 대화방)** — CR-006 · 원칙7 제외", 185행 `AppShell` 은 "<아이디> · 로그아웃" 한 줄뿐, 283행 "계정은 사용자 단위이며 인물 간 관계를 저장하지 않는다". 53행 "**CSRF 토큰** — 같은 출처 JSON API + Origin 검사(결정 T)로 갈음". 개정 2 가 더한 것(결정 U 표식 `user_id`, 기존 테스트 닫힌 목록)은 범위를 넓히지 않는다. |
| 3차-2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙5 — `CLAUDE.md` "화면 수를 고정하지 않는다 — 필요한 화면(로그인·가입 등)은 계획에서 근거와 함께 더한다" ↔ 182행 관문 1개 + 이유. 원칙1~4 — 55행 "툴 7종·ER 4단계·임계치·확신도·평가 산출물 변경 — 원칙1~4·8. 값의 출처만 바뀐다", 공통 회귀 244행 `git diff --stat <기준>..HEAD -- app/er evaluation reports data` 빈 출력. 원칙8 — 145행 `scripts/run_pilot_eval.py` 는 같은 값 명시뿐, 125행 "이 값들은 S3.1 보충(카드)에서 나오므로 단언 의미 변경이 아니라 카드 반영이다". 원칙9 — 135행 "`/auth/*` 는 `agent_traces` 를 쓰지 않는다(판정이 아님)", 175행 대상 0명이어도 `run_briefings` 가 `briefing_run` 1행을 기존 형식으로 남긴다(실물 `app/briefing/run.py:319-331`). |
| 3차-3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `decisions/D18-login-user-isolation.md` 지킬 것 4 "`/health`·`/auth/signup`·`/auth/login` 밖의 모든 라우트가 로그인 의존성을 갖는다" ↔ 107행 "**미로그인 401 `unauthenticated`**(… 예외는 … 3개뿐)", 159행 "**`/auth/logout` 은 예외가 아니다**". 지킬 것 5 "요청 경로에서 `app_user_id()`·`APP_USER_ID` 참조 0, `ToolContext.user_id` 기본값 0(`grep` 판정)" ↔ 161행 `grep -rnE … app/api app/tools app/auth`(기대 exit 1), 판정 #4(225행). 지킬 것 8 "주기 작업은 사용자마다 별도 `ToolContext(user_id=…)` 로 돌고, 한 사용자의 실패가 다른 사용자의 브리핑을 막지 않는다" ↔ 174행 "**사용자 단위 예외 격리**"; 대상 0명일 때의 표식 `""` 실행(175행)은 어느 계정의 일정도 고르지 않으므로(`app/briefing/select.py:76` `Person.user_id == ctx.user_id`) 이 항목과 부딪히지 않는다. 지킬 것 1·2·3·6·7·9 는 2차와 같은 문장(129·130·131·135·153·160행, 판정 #11). |
| 3차-4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.1-schema-v2.md` 27~29행 "users(id, username, password_hash, created_at) … auth_sessions(id, user_id, token_hash, created_at, expires_at) … chat_messages(id, user_id, role, content, question_id, created_at)" ↔ 120행 컬럼 집합 동일. 32행 "기존 테이블의 … `user_id` 는 `users.id` 값을 담되 **FK 는 두지 않는다**" ↔ 120행, 125행 `EXPECTED_FKS` 6→8(새 테이블 2개만). 34행 "0003 은 기존 사용자 데이터(…)를 **비운다**" ↔ 122행. `S3.4-ask-user-protocol.md` 14행 "로그인 사용자와 `user_id` 가 같을 때만 받고, 아니면 404(행·`answer` 변화 0)" ↔ 154행. `S3.6-briefing-push.md` 8행 "대상은 창 안에 미브리핑 일정이 있는 사용자" · 12행 "같은 endpoint 는 마지막으로 구독한 계정 하나에만" ↔ 174·176행. 툴 시그니처·임계치·`ask_user` 비동기는 건드리지 않는다(55행). |
| 3차-5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 99행 "의존: P9-infra U4(배포본 기동 `7830f6c`, 04-review 는 P9b 반영 뒤 함께) · P8 · P5b" ↔ 01-plan 5·6행. `packages/P8-frontend/04-review.md`·`P5b-query-turn/04-review.md`·`P4b-er-redesign/04-review.md` "결과: 완료". `CURRENT.md` 3행 "active: none". 단위 순서(117행 "U1 → U2 → U3a → U3b → (U4 ∥ U5)")는 §3 "단위별 통과 가능성" 에서 커밋 시점마다 따졌다. |
| 3차-6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 99행 "수용기준: 가입·로그인·로그아웃·내 정보 API 가 동작하고 … + pytest 전체 통과 skip 0" ↔ 01-plan 250행(`verify-plan` "PASS backlog 일치"). 판정 #12(233행)가 "통과 수 = 기준선 2261 + 새 테스트 − (U5 이후) `tests/test_settings.py` 2건" 으로 고쳐져 수 변화가 설명된다. 계획 안 grep 판정 5개는 모두 `-rnE`·스크립트 방식이고 "exit 2 는 실패" 가 붙었다(161·148·177행, 판정 #4). |
| 3차-7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan 119·128·143·151·164·172·181·193·201행 U1·U2·U3a·U3b·U4~U8 아홉 단위 모두 "/ Refs: P9b-auth D18 …"(`verify-plan` "PASS Refs 있음" 9줄). |
| 3차-8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | §4 "셸에서 `DROP`/`TRUNCATE` 금지 → Alembic 마이그레이션 파일로 작성해 검토" ↔ 122행(리비전 안 `DELETE` 4문), 123행(전용 DB 는 만들기만 하고 지우지 않는다). §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T` …) 금지" ↔ 195행 Caddy 스모크는 로컬 compose, 198행 "바깥 스모크(메인, 본문 없는 GET 만 — security §4)". §1 "(CR-006 · D18) 사용자 비밀번호·세션 토큰·쿠키 값은 로그·`agent_traces`·응답 본문·예외 메시지·증거 파일에 남기지 않는다" ↔ 135·196·246행. §5 "대화 기록은 … `chat_messages` 에만 **계정 소유로** 저장하고(다른 계정·로그·trace 로 복사 금지)" ↔ 168행. 263행이 `SameSite=Lax` 를 "보조 방어일 뿐" 으로 적고 주 방어를 JSON 본문 요구 + Origin 검사로 둔다. |

## 3차-3. 소견과 조치 (2026-11-15, 개정 2 대상)

증거 파일: `evidence/20261115-2036-planverify2-u3b-grep-probe.txt`(2차 N-3) · `evidence/20261115-2019-planverify-cmd4-probe.txt`(1차 F-4). 그 밖의 근거는 코드·테스트 파일:줄.

### 이력 — 1차 F-1~F-7, 2차 N-1~N-4 의 3차 판정

| 소견 | 3차 | 근거 |
|---|---|---|
| F-1 U1↔U3 순서 | 해소(2차) | 121행, 변이 V1-3b. |
| F-2 U3↔U5 순서 | 해소 | `app/` 쪽은 2차에 해소, 테스트 쪽(N-2)은 아래. |
| F-3 로그아웃 미로그인 | 해소(2차) | 점검표 3행. |
| F-4 판정 #4 명령 | 해소(2차) | 225행. |
| F-5 U3 단언 닫힌 목록 | 해소 | 157행 — 2차 R2-2 ① 까지 반영. |
| F-6 대상 0명 | 해소 | N-4 아래. |
| F-7 CSRF 근거 | 해소(2차) | 2차 "새로 들어온 것" 대조 그대로 유효. |
| **N-1** U1 스키마 단언 | **해소**(한 줄 누락 → R3-1) | 125행 닫힌 목록 ①~④, 파일 표 78·79행, 124행 판정에 `scripts/schema_check.py` 전부 PASS. architect 가 더했다는 항목을 실물로 확인: `tests/test_schema_models.py` `NULLABLE_COLUMNS` 는 **컬럼 이름 집합**을 전 테이블에서 모아 비교하므로(232~239행) 새 nullable `question_id` 가 깨뜨린다 — 맞다. `EXPECTED_INDEXES`·309행 `total == 10` 은 기대 항목만 세므로 깨지지는 않고 반영 대상 — 계획 서술과 같다. 194~201행 CHECK 총수는 9테이블 고정 목록이라 깨지지 않는다 — 계획 서술과 같다. 212행 `len(found) == 6` 은 `EXPECTED_FKS` 와 함께 깨진다 — 사실 9(23행)에 있다. `scripts/schema_check.py` 의 숫자 비교는 237행(`== 6`)·286행(`>= 10`)·356행(`== 0`)뿐 — 계획과 같다. **목록에 없는 것 1건**: `tests/test_api.py:91`. |
| **N-2** `app_user_id` 테스트 참조 | **해소** | 146행(U3a 리터럴화)·148행 판정·149행 V3a-1·177행(U5 삭제·−2)·9행·233행. 위키 밖 저장소 전체 검색 결과가 사실 9(25행)의 목록과 같다 — `tests/` 6파일, `.github/workflows/tests.yml:176`, `docs/user-setup/11…:58,105`·`13…:41,46`. 계획에 없는 문서 1곳은 R3-3. |
| **N-3** U3b grep | **해소** | 161행 `grep -rnE … app/api app/tools app/auth` + "기대 exit 1, exit 2 는 실패". 재귀 검색에 캐시 파일이 섞이는 점은 R3-2. |
| **N-4** 대상 0명 방법 | **해소** | 아래 "N-4 확정안 대조". |

### N-4 확정안 대조 (175행, 결정 U 278행) — 실물·기존 테스트와 맞다
- `ToolContext` 는 `user_id` 값을 검증하지 않는다(`app/tools/context.py:93-109` — `__post_init__` 없음). `notifier_from_env(session, user_id, now)` 도 값을 그대로 넘길 뿐이다(`app/push/notifier.py:252-270`) → `""` 로 불러도 예외가 없다.
- `run_briefings` 는 `select_due_schedules` 로 `Person.user_id == ctx.user_id` 인 일정만 고른다(`app/briefing/select.py:76`). `persons.user_id` 는 로그인 계정의 `users.id`(uuid4 hex)나 테스트의 `"local"` 류 값이므로 `""` 로는 0건이 선택되고, 실행 끝의 `briefing_run` 행 1개만 남는다(`run.py:319-331`, `session_id` 는 `run.py:183` 이 붙이는 `briefing:<uuid>`) — 계획 174·175행 서술과 같다.
- 기존 테스트 4건: `tests/test_briefing_scheduler.py:202-206` 은 실제 `session_scope()` 로 돌지만 다른 테스트의 데이터는 바깥 트랜잭션에 갇혀 보이지 않으므로 대상 0명 → 가짜 `run_briefings` 1회 → `len(calls) == 2` 가 선다. `tests/test_push_wiring.py:308-345` 3건은 `scheduler_env`(172행 — `session_scope` 를 롤백 세션 하나를 내주는 대역으로 바꿈)에서 일정 없이 돌므로 `""` ctx 로 1회 불리고, 344행은 `== ""` 로 바뀐다(계획이 U5 단언으로 적음). 같은 파일의 끝까지 가는 2건(347~384행)은 `"local"` 인물의 `now+3h` 일정을 넣으므로 사용자 목록에 `"local"` 이 잡혀 지금처럼 돈다 — 계획 174행 "`users` 테이블이 아니라 `persons.user_id` 에서 구하므로" 가 이것을 보장한다.
- 구현 때 지킬 점 하나(계획 174행 "세션을 사용자마다 따로 여는 방식 권장" 과 관련): `scheduler_env` 는 `session_scope()` 를 몇 번 불러도 같은 세션을 내주므로 어느 방식이든 테스트는 선다. 03-log 로 흡수된다.

### 단위별 통과 가능성 (커밋 시점마다 전체 pytest)
- **U1** — 닫힌 목록(125행)으로 스키마 단언·`PendingQuestion(` 6파일이 덮인다(`PendingQuestion(` 은 `app` 1곳 + 테스트 6파일 9곳이 전부, 원시 SQL 삽입 0). **남는 1건: `tests/test_api.py:91`**(R3-1).
- **U2** — 기존 테스트에 닿는 변경 없음(라우트 수·OpenAPI 를 단언하는 테스트 없음, `Origin` 을 보내는 테스트 없음).
- **U3a** — `app/` diff 0. 리터럴화 대상 2파일이 146행에 줄 번호로 있다.
- **U3b** — `X-Session-Id` 를 쓰는 곳 19곳·세션 단언 7곳(`tests/test_api_chat.py:148,210,222,225`, `tests/test_api_chat_query.py:437,440`, `tests/test_api_questions_pending.py:75`)이 모두 닫힌 목록 ①②③(157행) 안이다. 한 테스트 안에서 세션 id 둘로 격리를 가르는 테스트는 0건. `resolve_session_id`·`build_ctx`·`build_chat_ctx`·`get_notifier` 를 직접 부르는 테스트 0건(`load_resume_input` 2곳은 시그니처 불변). `app/` 의 `ToolContext(` 4곳은 모두 `user_id=` 명시.
- **U4** — `chat_messages.user_id` FK 는 U3a 의 로그인 도우미가 만든 `users` 행으로 충족.
- **U5** — N-2·N-4 반영으로 고칠 기존 테스트가 줄 번호까지 있다(`tests/test_settings.py` 삭제, `tests/test_push_wiring.py:344`).
- **U6~U8** — 2차와 같다(순서 결함 없음).

### [필수]
없음.

### [권고] — 구현 중 보고·03-log 로 흡수된다. R3-1 만은 활성화 전에 한 줄 더하기를 권한다

- **R3-1 (U1 닫힌 목록에 1줄)** `tests/test_api.py:91` `assert body["alembic_revision"] == "0002"  # FIX-020 -- 0002 리비전 추가`. 테스트 DB 가 0003 이 되면 **U1 에서 반드시 실패**하고 125행 닫힌 목록에 없어 "목록 밖 테스트가 깨지면 멈추고 보고" 가 걸린다(저장소 전체 `0002|alembic_revision` 검색에서 리비전 문자열을 단언하는 곳은 이 한 줄뿐). 고칠 값이 `"0003"` 하나로 정해져 있어 잘못된 구현으로 이끌지는 않지만, 알고 있는 왕복 1회다 → 125행 ② 뒤에 "`tests/test_api.py:91` `"0002"` → `"0003"`(리비전 반영)" 을 더하거나 U1 위임 프롬프트에 같은 문장을 넣는다. 이 한 줄을 더하는 것은 판정에 영향이 없으므로 재검증 없이 해도 된다.
- **R3-2 (재귀 grep 4개에 캐시 제외)** 시스템 grep 의 `-r` 은 `__pycache__/*.pyc` 도 읽는다. 지금 코드에서 `grep -rnE 'app_user_id|APP_USER_ID' tests scripts evaluation` 은 "Binary file tests/__pycache__/test_settings.cpython-314.pyc matches" 같은 줄을 낸다. U5 에서 `tests/test_settings.py` 를 지워도 그 `.pyc` 는 남으므로 `u5-outside-app.sh`(177행)가 "주석 2곳만" 이 아닌 줄을 내고, `u3b-request-path.sh`(161행)·`u5-no-fixed-user.sh`(225행)도 pytest 를 돌리기 전에 실행하면 옛 `.pyc` 때문에 exit 0 이 된다. 헛통과가 아니라 **헛실패** 쪽이다 → 148·161·177·225행의 재귀 grep 에 `--include='*.py'`(`.github` 를 함께 보는 177행은 `--exclude-dir=__pycache__`)를 붙인다.
- **R3-3 (U7 문서 목록에 1곳)** `docs/reliability.md:101` "이 프로젝트에는 **인증이 없다.** 서버 환경변수 `APP_USER_ID` 한 사람을 전제로 하며 …" 가 이 패키지 뒤 사실과 달라진다. 194행 문서 목록에 더한다(제품 코드·테스트와 무관).
- **R3-4 (U3a 판정 문장)** 148행 "일치 줄이 … 뿐" 목록에 `tests/test_answer_concurrency.py` 가 없는 것은 146행이 그 파일의 docstring 언급(71·73·127행)까지 고치기로 했기 때문이다 — 맞다. 다만 docstring 을 남기면 판정이 어긋나므로 03-log 에 "docstring 3곳 포함" 을 적게 한다.
- **R-12 (1차, 하네스)** `verify-plan.sh` 62·68행 — 이 패키지 밖, 그대로 열려 있다.

### 사용자에게 알릴 것 · 사용자만 정할 수 있는 것
2차와 같고 계획에 모두 들어갔다: ① OpenAI 월 한도 소진 가능성(사용자 할 일 6) ② 배포 반영 기동이 운영 데이터를 비우고 **0003 적용 뒤에는 옛 해시로 되돌릴 수 없다**(197행·리스크 291행 — 2차 R2-1 ③ 반영) ③ U1 에서 로컬 개발 DB 인물이 지워진다(124행). 사용자만 정할 수 있는 것: 범위 축소 3 을 쓸 경우의 수용 기준 6번 변경. 3차에서 새로 생긴 항목은 없다.

### 검증하지 못한 것
- 전체 pytest 를 돌리지 않았다 — 위 "단위별 통과 가능성" 은 코드·테스트 파일 대조와 전수 검색으로 판정했다. 검색 패턴 밖의 방식으로 스키마·세션·고정 사용자에 기대는 테스트가 있으면 계획의 "목록 밖이 깨지면 멈추고 보고" 가 받는다.
- Caddy 가 `Host` 를 그대로 넘기고 클라이언트의 `X-Forwarded-Host` 를 덮어쓰는지는 이 저장소에 증거가 없다 — U7 Caddy 스모크(195행)가 배포 반영 전 관문이다.

## 3차-4. 결정 (2026-11-15, 개정 2 대상)
3차 결과: 통과
사유: 점검표 8행 통과, [필수] 0건. 2차 [필수] N-1~N-4 가 계획 본문에서 닫힌 것을 코드·기존 테스트와 대조해 확인했다(스키마 단언·`app_user_id` 참조·세션 단언·`PendingQuestion(` 직접 생성은 전수 검색). 남은 것은 [권고] R3-1~R3-4 와 하네스 R-12 이며, R3-1(`tests/test_api.py:91`)은 U1 에서 반드시 만나는 한 줄이라 활성화 전에 125행이나 위임 프롬프트에 더하기를 권한다.
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)
