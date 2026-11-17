# D19 · MCP 읽기 전용 서버 — 계정별 개인 접근 토큰으로 `https://relmemo.com/mcp` 에 연결, 도구 4개, 원문 미노출

상태: 유효 | 해결하는 검증: (직접 R 없음 — 기획서에 MCP 문장 없음) | 출처: CR-008 (제기 2026-11-17, 수용 2026-11-17 밤 "토큰 방식 축소안", 사용자)

**결정**
1. **무엇을 여나**: 이 서비스를 **읽기 전용 원격 MCP 서버**로 연다. 주소는 `https://<배포 호스트>/mcp`(운영 `https://relmemo.com/mcp`). 외부 MCP 클라이언트는 로그인한 계정 자신의 기록만 조회한다. 쓰기(발화 기록·답변·인물 생성)·브리핑 생성·채팅 조회 턴·원문 조회는 열지 않는다.
2. **자격 = 계정별 개인 접근 토큰**: 로그인한 사용자가 웹에서 만든다(`POST /auth/mcp-token`, 로그인 필수). 무작위 불투명 값이고 **DB 에는 해시만**(`mcp_tokens.token_hash`, `auth_sessions` 와 같은 `hash_token`) 저장한다. **계정당 유효 토큰 1개** — 다시 만들면 이전 토큰은 즉시 무효. **만료 = 발급 뒤 7일**. 폐기(`DELETE /auth/mcp-token`) 즉시 무효. 토큰 원문은 발급 응답 한 번에만 실리고 다시 볼 수 없다(`GET` 은 있는지·만료·마지막 사용만).
3. **`/mcp` 인증**: `Authorization: Bearer <토큰>` **헤더로만** 받는다. 쿼리 문자열의 토큰·로그인 쿠키는 자격이 아니다. 토큰 없음·틀림·만료·폐기 → **401** `{"detail":{"code":"unauthenticated"}}`(+ `WWW-Authenticate: Bearer`). 사용자 = 토큰 행의 `user_id` — 도구 입력에 사용자 id 인자가 없다.
4. **도구 4개(모두 읽기 전용 표시, LLM·임베딩 호출 0)**: `list_people`(인물 목록) · `find_person`(이름·별칭 포함 일치 — **일치하는 인물을 전부** 돌려주고 하나로 고르지 않는다) · `get_person_card`(사실·반복 패턴·최근 사건·다가오는 일정) · `list_briefings`(저장된 브리핑). 모두 기존 조회 함수(`app/api/read.py` 의 `list_persons`·`get_person_card`·`list_briefings`)를 감싼다. 결과에 원문(`raw_utterance`)·닉네임·대기 질문·대화 기록·`agent_traces` 가 없다. 결과 크기 상한을 둔다(값은 P9b 01-plan 개정 4).
5. **배치**: 같은 FastAPI 앱 안, 정확 경로 `/mcp`, 공식 MCP Python SDK 의 Streamable HTTP(무상태·JSON 응답). compose 서비스 3개 그대로(D17 결정 1). Caddy 에 `/mcp` 를 접두를 떼지 않고 백엔드로 넘기는 블록을 더한다(D17 보충).
6. **스위치 `MCP_ENABLED`**: 코드 기본은 **꺼짐**(로컬·시험에서 `/mcp` 가 없고 SDK 를 import 하지 않는다). 운영 compose 가 `MCP_ENABLED: ${MCP_ENABLED:-1}` 로 켠다 — 서버 `.env` 수정 없이 켜지고, 끄려면 사용자가 서버 `.env` 에 `MCP_ENABLED=0` 을 넣고 재기동한다. 꺼지면 `/mcp` 는 404. 토큰 발급 API(`/auth/mcp-token`)는 스위치와 무관하게 있다(꺼져 있어도 토큰은 쓸 곳이 없다).
7. **근거 기록(원칙9)**: MCP 도구 호출은 에이전트 판정이 아니다 → `agent_traces` 에 남기지 않는다(기존 읽기 API 규약 — 읽기·쓰기 trace 0. `agent_traces` 는 세션 단위 판정 흐름 재생용이고, `list_briefings` 가 그 표를 원천으로 읽으므로 섞지 않는다). 대신 ① `mcp_tokens.last_used_at`(인증 성공한 요청마다) ② 서버 로그 한 줄(도구 이름·`user_id`·결과 개수 — 인자 값·토큰 0) ③ uvicorn 접근 로그의 `POST /mcp` 줄.
8. **로그아웃과의 관계**: 로그아웃은 웹 세션만 끝낸다 — MCP 토큰은 별개 자격이라 폐기하지 않는다(사용자가 "AI 연결" 화면에서 폐기).
9. **이번에 하지 않는 것(다음 단계 — CR-008 4.3·11장 설계 기록)**: OAuth 로그인 연결(인가 서버·DCR·동의 화면·PKCE·갱신 토큰), Claude 앱·ChatGPT·Gemini 앱 연결, 쓰기 도구, 공개 기간 연장(11-19 종료 유지).

**이유**
- 사용자 목적: "Mcp는 당장 내일 시연을 위해서 필요한거라서" — 평가 전날 밤에 OAuth 인가 서버(엔드포인트 5개·동의 화면·보안 변이 시험)까지 끝낼 수 없다(CR-008 9.2). 정적 Bearer 헤더는 Claude Code·Codex CLI 가 문서로 지원한다(CR-008 7.2 [B1][D1]).
- 계정별 토큰은 로그인한 세션에서만 발급되므로 D18 "사용자 id 는 로그인 계정에서만 온다" 와 맞는다. 고정 시험 토큰(환경변수)을 제품에 두지 않는다.
- 해시 저장·불투명 토큰은 `auth_sessions` 방식을 그대로 재사용해 새 서버 비밀 값이 0 이다(서명 키·JWT 없음) — 배포에 서버 `.env` 수정이 필요 없다.
- 계정당 1개·7일: 시연(11-18)부터 종료(11-19)까지 덮고, 유출 시 피해 기간을 짧게 한다. 1개로 두면 "어느 토큰이 살아 있나" 를 화면 한 줄로 보인다.
- 읽기 전용·기존 조회 함수 재사용: 원칙1~4 경로가 없고 툴 7종·ER·임계치가 그대로다. LLM 비용 0.

**파급**
- S3.1 보충(리비전 0005 `mcp_tokens`). S3.2 툴 7종 **무변경**(MCP 도구는 어댑터 — 툴 7종 등록표에 섞지 않는다, `tools_check` 7/7).
- D18 보충(결정 3 의 로그인 없이 열린 예외 목록과 `/mcp` 자격 문장, 지킬 것 2·3·4). D17 보충(Caddy `/mcp` 블록·compose 스위치 — 결정 1 서비스 3개·공개 기간 무변경).
- CLAUDE.md 기술 스택(MCP 한 줄)·데이터 모델(`mcp_tokens`). security §1(MCP 토큰은 비밀)·§5(외부 공급자 전송). 기획서 상단 한 줄.
- 패키지: P9b-auth 01-plan 개정 4(U12 백엔드 · U13 프론트 "AI 연결" 화면 · U14 재배포·실제 연결). 다음 단계 OAuth 는 `P12-mcp`(CR-008 11장).
- 제3자 개인정보: 조회한 카드 내용이 연결한 클라이언트의 LLM 공급자(Anthropic 등)로 전송된다 — "AI 연결" 화면과 사용자 문서에 고지한다. 원문은 내보내지 않는다.

**코드에서 지켜야 할 것**
1. `mcp_tokens` 에 토큰 원문 컬럼 0 — `token_hash` 만(`app.auth.sessions.hash_token`). 원문은 `POST /auth/mcp-token` 201 응답 본문 한 번에만 있고 `GET` 응답 키에 `token` 이 없다. 두 응답 모두 `Cache-Control: no-store`.
2. 계정당 행 1개 — `mcp_tokens.user_id` UNIQUE, 발급은 그 사용자 행의 upsert(이전 해시를 덮어써 이전 토큰이 즉시 무효). 유효 조건은 `expires_at > now`(같은 순간은 만료 — `auth_sessions` 와 같은 규약).
3. `/mcp` 는 `Authorization` 헤더의 `Bearer` 값만 읽는다 — 쿼리 문자열·쿠키를 읽는 코드 0. 헤더가 없으면 **DB 에 묻기 전에** 401. 401 본문은 `{"detail":{"code":"unauthenticated"}}`(이유를 구별하지 않는다).
4. 도구 핸들러는 사용자 id 를 인증 단계가 넘긴 값에서만 얻는다 — 도구 입력 스키마에 `user_id`·`username` 인자 0. 남의 `person_id`·`schedule_id` 는 "없음"(`not_found`)과 같은 결과.
5. 등록된 MCP 도구는 정확히 `list_people`·`find_person`·`get_person_card`·`list_briefings` 4개이고 모두 `readOnlyHint=true`·`destructiveHint=false`·`openWorldHint=false`. MCP 모듈(`app/mcp_server/`)은 `app.tools`(툴 7종)·`app.agent`·`app.er`·`app.briefing`·`app.embedding`·LLM 공급자 SDK 를 import 하지 않는다(조회는 `app.api.read` 를 통해서만 — `grep -rnE` 판정).
6. 도구 결과 어디에도 `raw_utterance` 키·값, 닉네임, 토큰이 없다. 오류 결과는 고정 코드(`not_found`·`invalid_name`·`internal_error`)뿐 — 예외 원문을 싣지 않는다.
7. 토큰은 로그·`agent_traces`·예외 메시지·증거 파일에 남기지 않는다. 도구 호출 로그 줄에는 도구 이름·`user_id`·결과 개수만(도구 인자 값 0 — 인물 이름은 제3자 정보).
8. `MCP_ENABLED` 가 꺼져 있으면 `/mcp` 라우트가 없고(404) MCP SDK 를 import 하지 않는다(`import app.main` 이 SDK 없이도 된다). 잘못된 값은 `InvalidValue` 로 앱 시작 실패(`push_dev_page_enabled()` 와 같은 관례).

**갱신 이력**
- 2026-11-17 밤 신설(CR-008 3차 — 사용자 "토큰 방식 축소안"). 구현은 P9b-auth U12~U14(01-plan 개정 4) — 완료 해시는 그때 적는다. 파일명은 `D19-mcp-read-token.md`(CR-008 10장의 가칭 `D19-mcp-read-only.md` 대신 — 이번 결정의 핵심이 토큰 방식이라).
