# P8-frontend · 계획 검증 (02-plan-verify)

대상: 01-plan.md (architect 초안 → 사용자 결정 A~N 반영 개정 1, 2026-10-10 — 1차 §1~§4 · 소견 반영 개정 2 — 재검증 §5) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-10-10

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P8-frontend | tee docs/wiki/packages/P8-frontend/evidence/20261010-2314-verify-plan-verifier.txt` (1차 — 이 문서를 쓰기 전. "02-plan-verify 없음" FAIL 1 은 그 시점에 정상. 같은 파일 아래쪽에 verifier 가 직접 실행한 사실 확인 명령·출력이 있다)
```
== verify-plan P8-frontend  (2026-10-10 23:11) ==
PASS  존재: docs/wiki/packages/P8-frontend/01-plan.md
FAIL  없음: docs/wiki/packages/P8-frontend/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D7
PASS  패키지 id 등록됨: P11-demo
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P8-frontend
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  검증 항목 존재: R8
PASS  Refs 있음: - [ ] U0 하네스 — frontend-agent 신설·위임 게이트·FIX 게이트 `web/` 확대 — 
PASS  Refs 있음: - [ ] U1 인물 목록·카드 조회 API — [backend-agent] `GET /persons` → 
PASS  Refs 있음: - [ ] U2 원문 조회 API(결정 F 확정) — [backend-agent] `GET /events/{
PASS  Refs 있음: - [ ] U3 대기 질문·브리핑 조회 API — [backend-agent] `GET /questions/
PASS  Refs 있음: - [ ] U4 프론트 골격·디자인 토큰·도구·CI — [frontend-agent] 첫 명령 `node -
PASS  Refs 있음: - [ ] U5 채팅 화면 + 확인 칩 — [frontend-agent] 발화 입력·전송(`POST /api
PASS  Refs 있음: - [ ] U6 인물 카드 화면 + 원문 펼치기 — [frontend-agent] `#/persons` 인물
PASS  Refs 있음: - [ ] U7 브리핑 화면 + 수동 브리핑 버튼 — [frontend-agent] `#/briefings`
PASS  Refs 있음: - [ ] U8 PWA·푸시 구독 — [frontend-agent] `manifest.webmanifest`
PASS  Refs 있음: - [ ] U9 E2E·자동 판정 전체·문서 — [frontend-agent: E2E·프론트 행·불변식 gr
PASS  Refs 있음: - [ ] U10 사람 점검 — 실서버·실 LLM·데스크톱 Chrome — [사용자·메인 세션] (에이전트 
PASS  backlog 일치: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P6-memory
PASS  의존 완료: P7-push
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  registry 중복 없음: .claude/agents/frontend-agent.md
PASS  registry 중복 없음: app/api/read.py
PASS  registry 중복 없음: tests/test_api_read_persons.py
PASS  registry 중복 없음: tests/test_api_read_raw.py
PASS  registry 중복 없음: tests/test_api_questions_pending.py
PASS  registry 중복 없음: tests/test_api_read_briefings.py
PASS  registry 중복 없음: web/package.json
PASS  registry 중복 없음: web/package-lock.json
PASS  registry 중복 없음: web/tsconfig.json
PASS  registry 중복 없음: web/vite.config.ts
PASS  registry 중복 없음: web/index.html
PASS  registry 중복 없음: web/tailwind.config.ts
PASS  registry 중복 없음: web/components.json
PASS  registry 중복 없음: web/src/main.tsx
PASS  registry 중복 없음: web/src/App.tsx
PASS  registry 중복 없음: web/src/routes.ts
PASS  registry 중복 없음: web/src/styles/tokens.css
PASS  registry 중복 없음: web/src/api/client.ts
PASS  registry 중복 없음: web/src/api/types.ts
PASS  registry 중복 없음: web/src/session.ts
PASS  registry 중복 없음: web/src/screens/ChatScreen.tsx
PASS  registry 중복 없음: web/src/screens/PersonCardScreen.tsx
PASS  registry 중복 없음: web/src/screens/BriefingScreen.tsx
PASS  registry 중복 없음: web/src/push.ts
PASS  registry 중복 없음: web/public/sw.js
PASS  registry 중복 없음: web/public/manifest.webma
PASS  registry 중복 없음: web/public/icon-192.png
PASS  registry 중복 없음: web/public/icon-512.png
PASS  registry 중복 없음: web/src/__tests__/chat.test.tsx
PASS  registry 중복 없음: web/src/__tests__/card.test.tsx
PASS  registry 중복 없음: web/src/__tests__/briefing.test.tsx
PASS  registry 중복 없음: web/src/__tests__/routes.test.ts
PASS  registry 중복 없음: web/src/__tests__/sw.test.ts
PASS  registry 중복 없음: web/src/__tests__/push.test.ts
PASS  registry 중복 없음: web/playwright.config.ts
PASS  registry 중복 없음: web/e2e/chat.spec.ts
PASS  registry 중복 없음: web/e2e/card.spec.ts
PASS  registry 중복 없음: web/e2e/briefing.spec.ts
PASS  registry 중복 없음: web/e2e/fixtures/api.ts
== 결과: FAIL=1 WARN=0 ==
```
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.
(위 FAIL 1 은 이 문서 자체의 부재이므로 소견으로 올리지 않는다 — P7-push 02-plan-verify 와 같은 처리. 이 문서를 쓴 뒤 2차 실행 결과는 아래 1-2절.)

git 기록(`bash .claude/scripts/gitlog.sh P8`, 2026-10-10 23:11): `dev2` HEAD `50fd7fc`(= 01-plan 8행 "시작 해시") · origin/dev2 와 같음 · dev `f9500fe` · 미커밋 `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md`·`docs/wiki/packages/P8-frontend/`(문서만, 제품 코드 0 — 01-plan 8행과 일치). `git log --grep P8` 5건은 전부 다른 패키지 커밋이 P8 을 인계 문맥으로 언급한 것이고 P8-frontend 단위 커밋은 없다(01-plan 9행과 일치).

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표(56~62행) 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱", 포함 열 "챗봇 UI (텍스트)"·"인물 카드 (사실 · 타임라인 · 마지막 접촉)"·"반응형 웹 + PWA"; 부록 A "되는 것 / 안 되는 것" 표(377~385행) "❌ 음성 입력 / 인물 간(A–B) 관계도 / 감정 상담 / 다중 사용자 운영 / 오프라인 사용". 01-plan "하지 않는 것"(34~48행)이 여섯 항목을 각각 한 줄씩 명시: 39행 "관계 태그 필터링 — 기획서 2장 제외 열 … 걸러 내는 컨트롤을 두지 않는다"(판정 19행 "목록 화면에 필터 컨트롤 0"), 40행 "고민 상담·감정 대화·상담 페르소나·톤 설정, 인물 간(A–B) 관계, 음성 입력, 네이티브 앱(원칙7) — 채팅 응답은 서버 `reply` 를 그대로 보여 줄 뿐 프론트가 문장을 만들지 않는다. 마이크·음성 API 를 쓰지 않는다. 설치는 PWA 로만", 41행 "인증·로그인·다중 사용자 — 단일 사용자 전제", 35행 "오프라인 사용 … 부록 A 385행 '안 되는 것: 오프라인 사용' 그대로". 집행: 불변식 2 `grep -rnE "getUserMedia\|SpeechRecognition\|webkitSpeech" web/src web/public → 0건`, 체크리스트 18항 "상담 페르소나 이름·말투 설정·음성 입력 버튼·'무엇이든 물어보세요' 류 문구가 없다", 판정 17행 "서버 `reply` 그대로(프론트가 문장을 지어내지 않음)". 결정 L 318행 경계 문장 "챗봇 UI 의 형태만 빌린다. 대화 내용은 기록 결과(서버 `reply`)·확인 칩·브리핑의 한 줄 제안으로 한정한다" 가 `CLAUDE.md` 원칙7 경계 문장 "브리핑의 '제안'은 기록된 사실에서 도출되는 한 줄 행동 제안으로 한정" 과 같은 방향이고, 프론트가 서버 문자열을 만들지 않으므로 상담 기능이 프론트에서 생길 경로가 없다. 인물 간 관계: 조회 API 응답 모양(U1~U3)에 인물–인물 필드 없음(S3.1 "인물–인물 관계 테이블 없음 (D8, 원칙7)" 과 일치) |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | `CLAUDE.md` 불변 원칙 절. **원칙1~4·6(ER·임계치·확신도·패턴)**: 이 패키지는 `app/er`·`app/agent`·`app/memory`·`app/tools` 를 고치지 않는다 — 01-plan 43행 "스키마 v2 변경·툴 7종 시그니처 변경·루프·ER·메모리·브리핑 생성 로직 변경 — S3.1·S3.2 가 권위다", 판정 11행 `git diff --stat 50fd7fc -- app/tools app/agent app/er app/memory app/briefing app/push app/db alembic` 빈 출력 + `python scripts/tools_check.py` "RESULT: 7/7 ok". 프론트의 확인 칩은 서버가 낸 `pending_question.options` 를 그대로 보여 주고 `POST /answers` 로 넘길 뿐 판정을 하지 않는다(해석 ㄱ "그 `options` 문자열이 그대로 칩으로 뜨고", 판정 15행 "칩 3개가 … 글자·순서 그대로"). **원칙5** "프론트 화면은 3개로 고정: 채팅 / 인물 카드 / 브리핑. UI에 시간을 쓰지 않는다": 해석 (틀) "라우트는 정확히 3개(`#/chat`·`#/persons`·`#/briefings`)이고, 그 밖의 화면 경로가 없다", 판정 13행 routes.test "경로 키가 정확히 `chat`·`persons`·`briefings` 3개", 37행 "네 번째 화면 — 설정·로그인·구독 관리·trace 보기·인물 추가 폼 화면을 만들지 않는다", 결정 H "(iii) 은 4번째 화면이라 원칙5 위반" 로 구독 버튼을 브리핑 화면 안에, 결정 L 325행 "전환 토글은 두지 않는다(설정 화면·설정 저장이 생기지 않게)", 결정 N 335행 "사이드바 열림/닫힘은 화면이 아니라 레이아웃 상태다. … 접힘 상태를 저장하는 설정 화면·설정 저장은 만들지 않는다". "UI에 시간을 쓰지 않는다" 의 출처는 `docs/proposal.md` 9장 리스크 표 254행 "1인 개발 일정 초과 → 프론트 3화면 고정, 음성·메시지 초안 제외. UI에 시간을 쓰지 않는다" — 일정 리스크 대응 문장이므로 결정 L 313행 "화면 수(3개)는 그대로이고, 기성 부품으로 한 번에 만드는 것은 … 뜻(디자인 작업으로 일정 초과 금지)을 지킨다. 원칙5 문구를 바꾸지 않는다" 해석에 동의한다(사용자 확정 2026-10-10). 단, 이 해석은 **수정 1회 상한(312행·판정 32행)이 지켜질 때만** 성립하므로 04-review 가 반영 횟수를 증거로 받아야 한다(R-10). 판정 13행은 "라우트 3개" 만 잡고 라우트 없는 화면(Dialog/Sheet 패널)은 못 잡는다 — R-4 권고. **원칙7**: 1행. **원칙8**: 판정 표 1~28행이 명령·기대값으로 적혀 있고 29~32행은 "증거 파일이 갖출 항목(전부 있어야 통과)" 을 열거(①~⑫, DB 조회 출력·trace id·사용자 문장), 리스크 9 "안 뜨면 발화를 바꿔 다시 하되 시도마다 증거에 남긴다(원칙8)", 절차 9 "남은 확인 행은 지우지 않는다(원칙8)", 리스크 11 "사람 점검이 있어야 닫힌다". **원칙9** "모든 판정에는 근거를 남긴다": 조회 API 가 trace 를 남기지 않는 것(결정 F 271행 "조회는 판정이 아니다")은 `app/tools/questions.py` 290~295행 `list_pending` docstring "툴 7종 밖이고 판정을 하지 않는 단순 조회라 `@traced` 를 붙이지 않는다 … 매 폴링/렌더링마다 `agent_traces` 행이 쌓이면 원칙9가 지키려는 '판정 근거'의 신호 대 잡음비가 나빠진다"(P5-loop 선례)와 같은 해석이고, S3.2 마지막 줄 "모든 툴 호출은 `agent_traces`에 … 기록(원칙9)" 의 대상은 툴 호출이지 HTTP 조회가 아니다. 판정 7행이 "1·2·5·6·8·9행 요청 전후 `agent_traces` 행 수 … 전부 변화 0" 으로 이를 고정한다. 결정 G(trace 를 제품 조회 원천으로)는 원칙9 와 충돌하지 않는다 — trace 를 읽기만 하고 바꾸지 않으며(판정 7·10행), `docs/wiki/packages/P6-briefing/04-review.md` 199행 "주기 작업이 만든 브리핑은 응답이 없으므로 `agent_traces(tool_name='briefing', step='briefing_compose')` 가 유일한 저장소(결정 H(i)) — `user_id` 열이 없어 `output.person_id → persons.user_id` 조인 필요(R-6)" 가 이미 이 용도를 예정했다. 코드 확인: `app/briefing/run.py` 223~225행 `compose_output = {"schedule_id": schedule.id, "person_id": person_id, …}`, `app/db/models.py` 273행 `output … JSONB` — 조인 키가 있다(R-9) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | 01-plan 4행 "기대는 결정: D1 D2 D7". `docs/wiki/decisions/D01-new-person-confirm.md` "코드에서 지켜야 할 것: `create_person` 호출 경로는 반드시 answered pending_question 을 거친다" — 프론트는 툴을 부르지 않고 `POST /answers/{question_id}` 만 부른다(U5, 판정 15행 "`POST /api/answers/7` 본문 `{"answer":"친구"}` 1회"); 38행 "카드에 편집 폼을 두면 툴 7종을 우회하는 쓰기 경로가 생겨 … 고치는 경로는 대화(채팅 → 루프 → `update_person`)다" 로 우회 쓰기 경로를 막았다. `D02-ask-user-async.md` "코드에서 지켜야 할 것: 동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다", 파급 "프론트 확인 칩 = 미답변 pending_questions 렌더링. 미답변 24h 만료. 답 없이 새 발화가 오면 대기 질문 유지하고 새 발화 우선" — U5 "화면 진입 시 `GET /api/questions/pending` 으로 대기 칩 복원"(진입 1회, 폴링 아님 — 판정 16행 "진입 시 `GET /api/questions/pending` 1건"), 결정 E "대기 중 입력: 막지 않는다 — S3.4 '새 발화 우선'", "409: `already_answered`·`expired` → 그 칩을 지우고 한 줄 안내. 재시도하지 않는다"(판정 17행). `D07-tls-caddy.md` "적용 시점 P9-infra" — 01-plan 46행 "운영 배포(S3 + CloudFront, Caddy TLS, CloudFront 경로 동작 설정) — D7 '적용 시점 P9-infra'", 결정 C(ii) 251행 "D7(Caddy)과 기술 스택(S3 + CloudFront)을 그대로 따른다 … 배포 자체는 P9". 그 밖에 인용한 D 카드 없음. 결정 F 의 "trace 없음" 은 D 카드 "코드에서 지켜야 할 것" 과 무관(2행 참조) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | **S3.1** `docs/wiki/specs/S3.1-schema-v2.md` 9행 "`fact_sources(fact_id, event_id)` -- 시맨틱 사실 → 근거 원문", 10행 "`events(id, person_id, type, content, raw_utterance, occurred_at, created_at)`", 13행 "`agent_traces(id, session_id, step, tool_name, input, output, …)`"(user_id 없음 → 결정 G 조인) — U2 "`fact_sources` → `events` 조인", U1 "`last_contact_at` = 그 인물 `events.occurred_at` 최댓값" 이 열 이름과 맞고, 판정 11행 `alembic check` "No new upgrade operations detected." 로 스키마 무변경을 고정. `events` 에 `user_id` 가 없으므로 결정 F 270행 "두 엔드포인트 모두 `persons.user_id = app_user_id()` 를 조인 조건에 건다" 가 유일한 격리 경로이고 `docs/wiki/security.md` §5 "모든 조회는 `user_id` 조건을 넣는다" 와 일치. **S3.2** `S3.2-tools-v2.md` "적용: P2-tools" — 툴 7종 표이며 HTTP 조회 목록이 아니다(결정 F ③). 새 GET 6개는 툴이 아니고 `tools_check` 7/7(판정 11행)로 시그니처 불변 확인; 불변식 5 "쓰기 라우트를 더하지 않는다". **S3.4** `S3.4-ask-user-protocol.md` "적용: P2-tools, P5-loop, P8-frontend" — 카드가 이미 이 패키지를 적용처로 둔다. "턴 N+1 칩 선택 → POST /answers/{question_id} → 저장된 context로 루프 재개"(해석 ㄱ 그대로), "답 없이 다음 발화가 오면 대기 질문 유지, 새 발화 우선"(결정 E(i), 판정 16행), "미답변 24시간 후 만료(… status=expired)"(판정 8행 "만료(25h 전) 1" 제외·17행 409 `expired`), "프론트 확인 칩 = 미답변 pending_questions"(결정 E "미답변 전부를 질문별로 쌓는다", U3 `list_pending` 재사용 — `app/tools/questions.py` 287행 시그니처 `list_pending(ctx, session_id=None)` 확인). "`context`에는 … 비밀·전체 대화 이력 저장 금지" — U5 "대화 기록은 화면 메모리에만(새로고침하면 지워짐 — 서버에 대화 이력 API 없음)" 으로 프론트도 이력을 서버에 두지 않는다. **S3.6** `S3.6-briefing-push.md` "수동 트리거 `POST /briefings/run` = 같은 함수. 데모 '시간 앞당기기'와 '발표자 수동 버튼' 겸용"(U7 "지금 브리핑" 버튼 = 기존 `POST /briefings/run`), "제안은 사실에서 도출되는 한 줄 행동 제안으로 한정"(U7 "서버 문자열 그대로", 판정 20행), "푸시 구독은 `push_subscriptions`. VAPID 키는 … 코드·저장소에 두지 않는다"(U8 "`GET /api/push/vapid-public-key` 로 받는다", 불변식 7). 브리핑 조회 원천(trace)은 S3.6 에 없는 보충이지만 P6-briefing 결정 H(i) 가 정한 저장소를 읽는 것이라 카드 변경이 아니다. **임계치 2개·ask_user 비동기**: ER·루프 무변경(판정 11행 diff)이라 해당 없음; D2 는 3행 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 88행 "[frontend-agent(신설)] 프론트 3화면 + PWA / 의존: P5, P6 / 수용기준: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면". 04-review `결과: 완료` 줄 직접 확인: `P5-loop/04-review.md` 196행 · `P6-memory/04-review.md` 152행 · `P6-briefing/04-review.md` 267행 · `P7-push/04-review.md` 185행 · `P4b-er-redesign/04-review.md` 144행(기계 검증 "PASS 의존 완료" 4건·"PASS P4 게이트 통과 (P4b-er-redesign)"). `docs/wiki/CURRENT.md` "active: none / frozen: none" — 동결 없음. P7 완료 커밋 `50fd7fc` = 01-plan 8행 시작 해시 = `gitlog.sh` HEAD. 인계 대조: `P5-loop/04-review.md` 187행 "`POST /chat` 계약(P8-frontend 가 그대로 쓴다): … 확인 칩 = `pending_question.options` 그대로" = 01-plan 12행; `P6-briefing/04-review.md` 199행(trace 유일 저장소·`user_id` 조인) = 01-plan 13행·결정 G; 188행 "지정 모드 `schedule_id` 가 잠긴 행이면 404 … P8 버튼이 생기면 혼란" = 결정 K; `P6-briefing/01-plan.md` 29행 "`GET /briefings/...` 는 backlog 수용 기준에 없어 만들지 않는다" = 01-plan 14행(조회 API 가 P8 몫); `P7-push/04-review.md` 178행 "제품 화면에서 `/push-dev/` 를 링크하지 않는다(결정 A 조건 — P8 04-review 에서 재확인) … 구독 해제 API 는 없다" = 01-plan 15·45행·불변식 1·결정 H. 후행: `docs/backlog.md` 93행 P9 "의존: P8" — 01-plan "후행 패키지가 이 패키지에서 기대하는 것" 에 P9 항목 있음. 단위 순서: U0(하네스) → U1~U3(backend-agent) → U4~U8(frontend-agent) → U9 → U10, 85행 "U0 커밋 전에는 frontend-agent 를 띄우지 않는다", 101행 "U9 자동 판정 1~28행이 전부 통과한 뒤에만" — R-1·R-3 참조 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 88행 "수용기준: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면" = 01-plan "## 수용 기준" 절 "- 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면"(기계 검증 "PASS backlog 일치"). 해석 표 ㄱ·ㄴ·ㄷ·(틀) 는 backlog 본문 "프론트 3화면 + PWA" 와 `docs/proposal.md` 316행 "평소처럼 얘기하면 하단에 확인 칩이 뜹니다", 346행 "타임라인 항목을 펼치면 원문 발화가 나옵니다", 287행 "화면은 셋입니다" 를 판정 가능한 문장으로 옮긴 것이고 새 기준을 더하지 않았다(107행 "새 기준을 더하는 것이 아니다"). backlog 89행 둘째 줄 "[미정 — CR 필요] 사용자별 메모리 설정" 은 01-plan 36행이 제외로 명시. 판정 표 덮음: ㄱ = 8·14~17b·24·29행, ㄴ = 1~7·18·19·25·30행, ㄷ = 9·10·20~23·26·31행, (틀) = 12·13·25·32행 — 빠진 구절 없음 |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 "PASS Refs 있음" U0~U10 11줄(메인 세션 1차 FAIL 1건은 U0 Refs 가 하위 줄에만 있던 형식 문제 — `evidence/20261010-2330-verify-plan-2.txt`, 첫 줄 끝에 같은 Refs 를 덧붙여 해소, 내용 무변경). U0 `P8-frontend L-002 L-004 원칙5` · U1 `P8-frontend S3.1 S3.5 원칙9` · U2 `P8-frontend S3.1 R8 원칙9` · U3 `P8-frontend S3.4 S3.6 D2 R12` · U4 `P8-frontend 원칙5 D7` · U5 `P8-frontend S3.4 D1 D2 원칙1 원칙7` · U6 `P8-frontend R8 S3.5 원칙7` · U7 `P8-frontend S3.6 R19 원칙7` · U8 `P8-frontend S3.6 R12 원칙5` · U9 `P8-frontend 원칙5 원칙8 원칙9` · U10 `P8-frontend S3.4 S3.6 원칙8`. `docs/wiki/review-index.md` 16·20·27행 R8·R12·R19 는 모두 "구현완료" 이고 INDEX 76행 P8 "닫는 R —" 와 일치 — 이 패키지가 닫는 R 은 없고 기대는 R 로만 쓴다(SKILL.md 태그 규칙 "기대는 D, 구현하는 S, 속한 P"). 단위 크기: U0~U8 은 각각 커밋 하나로 설명 가능. U9 는 frontend-agent 와 backend-agent 두 담당이 한 단위라 커밋이 2개가 될 가능성이 크다(R-13). 단위마다 담당·판정 명령·증거 파일 이름이 있다 |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | **비밀** — `docs/wiki/security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다": 절차 1 "사용자가 `.env` 에 LLM·임베딩 키 … 를 넣는다. 에이전트·메인 세션은 `.env` 를 읽지 않는다(security §1)", frontend-agent 초안 ⑥ "`.env` 금지". §5 "웹푸시 VAPID 개인키는 환경변수/SSM. 프론트에는 공개키만": U8 "`GET /api/push/vapid-public-key` → `pushManager.subscribe`", 불변식 7 `grep -rnE "VITE_[A-Z_]*(KEY|SECRET|TOKEN)" web/ → 0건`("빌드에 비밀을 넣지 않는다 — VAPID 공개키도 … 로 받는다"). 증거 파일: 29행 ① "키 값 없음", 31행 ⑪ "엔드포인트 호스트만"(P7 관례). **외부 전송** — §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T`, `scp`, `rclone`) 금지": 자동 테스트는 결정 J "실 LLM·실 푸시는 사람 점검에서만", 판정 서문 "가짜 표에 없는 요청은 실패시킨다(실제 네트워크 0)", 결정 L 323행 "웹 글꼴을 내려받지 않는다(외부 요청을 만들지 않는다 — 불변식 9)" + 불변식 9 `fonts.googleapis|fonts.gstatic|cdn.` 0건. 실 푸시·실 LLM 은 U10 "사용자·메인 세션" 만. `npm ci`·`npx shadcn`·`npx playwright install` 은 내려받기(인바운드)이고 §4 가 막는 "전송" 이 아니며 `safety-guard.sh` 에 npm/npx 규칙이 없다(evidence 2314 — 리스크 3 확인, R-8). §3 "다운로드한 스크립트 즉시 실행 금지 — 파일로 저장 → 내용 확인 → 실행" 의 취지상 `npx shadcn` 은 버전 고정 권고(R-8). **삭제** — §3 "재귀 삭제 … scratchpad 밖에서 금지": 01-plan 에 셸 삭제 단계 없음; frontend-agent 초안 ⑦ "`rm -rf` 대신 도구 옵션이나 node 스크립트" — `safety-guard.sh` 60행이 `rimraf` 도 막으므로 npm 스크립트에서 `rimraf` 도 피해야 한다(R-8). 절차 9 "남은 확인 행은 지우지 않는다". §2 git: 푸시는 메인 세션 몫(01-plan 8행), 서브에이전트 커밋 금지(⑥). `.gitignore` 에 `web/node_modules/`·`web/dist/` 추가(33행) + 불변식 8 `git ls-files web | grep -E "node_modules|dist/|…" → 0건` 으로 대용량·생성물 스테이징 방지. 리스크 4 `package-lock.json` 비밀 패턴 오탐은 `.githooks/pre-commit` 35·38행 패턴(`sk-…{24,}`·`ghp_…{36}`)이 표준 base64 integrity 와 겹치지 않아 낮고, 걸리면 "우회하지 않고 메인 세션에 보고" 로 §6 과 일치 |

### 2-1. 메인 세션이 위임한 판정 항목 1~8

1. **결정 F(원문 조회 API 2개, CR·FIX 불필요) — 동의.** 근거는 전부 실재한다: `docs/proposal.md` 119행 "원문은 보존해 근거 추적이 가능하다", 346행 "타임라인 항목을 펼치면 원문 발화가 나옵니다. 요약이 틀렸을 때 근거를 확인하고 고칠 수 있습니다"(기획서가 요구하는 기능 — 확인까지, 고치기는 38행에서 대화 경로로 한정), S3.1 9행 `fact_sources` 주석 "시맨틱 사실 → 근거 원문"(이 조인의 존재 이유), S3.2 "적용: P2-tools" 툴 7종 표(HTTP 조회 목록 아님), 선례 `docs/wiki/registry.md` 208행 `GET /push/vapid-public-key · POST /push/subscriptions`(P7-push U2 `6c98516`, S3.6 아래에서 CR 없이 추가). `/devlog change` 조건(SKILL.md 65행 "기획서가 바뀔 때")에 해당하지 않고 결함 수정도 아니다. **사용자 격리**: `events`·`person_facts`·`fact_sources` 에 `user_id` 가 없으므로(S3.1) `persons.user_id = app_user_id()` 조인이 유일한 격리이며, 두 번째 엔드포인트의 `person_facts.person_id = :person_id AND fact_sources.fact_id = :fact_id` 조건(270행)이 "다른 인물의 사실 id 끼워 넣기" 를 막고 판정 6행이 이를 시험한다. 같은 404 는 `app/main.py` 35행 매핑 `PersonNotFound … 404 {"detail":{"code":"not_found"}}` 재사용(판정 3·5·6행). **trace 미기록**: 2행 원칙9 판정 — `list_pending` 선례와 같은 해석, 판정 7행이 고정. S3.1 카드 "아래:" 줄 보충은 선택(R-7).
2. **결정 L(Tailwind+shadcn/ui 한 번에, 수정 1회 상한) — CR 불필요 해석에 동의, 조건부.** 2행 원칙5 판정 참조: 원칙5 둘째 문장의 출처가 기획서 9장 "1인 개발 일정 초과" 리스크 행이므로 "디자인 작업으로 일정을 초과하지 않는다" 로 읽는 것이 문맥에 맞고, 화면 수·기획서 본문을 바꾸지 않는다. 다만 "한 번에"·"수정 1회" 는 기계 판정이 없다 → U10 증거에 반영 횟수를 적고 04-review 가 ≤ 1 을 확인(R-10). 원칙7 경계: 318행 경계 문장 + 체크리스트 18항 + 판정 17행 "서버 `reply` 그대로" + 불변식 2 — 프론트가 문장을 만들지 않으므로 충분하다. 자리표시 문구 "오늘 있었던 일을 적어 주세요" 는 기록 안내로 한정.
3. **결정 N(모든 폭 왼쪽 사이드바) — 원칙5 와 양립.** 사이드바·서랍은 라우트가 아니고(335행), 사이드바 인물 목록은 `#/persons` 와 같은 컴포넌트·같은 API(U6 "같은 목록 컴포넌트를 … 새 API·새 라우트 없음"). 판정 13행 "라우트 키 정확히 3개" 는 **새 라우트**를 기계로 잡지만, 서랍이 Sheet(Radix Dialog) 라서 같은 부품으로 라우트 없는 네 번째 화면(설정 패널 등)을 만들어도 13행은 통과한다 → 라우트 밖 패널이 서랍 1개뿐임을 증거로 받는 불변식 추가 권고(R-4). 판정 25행(E2E 데스크톱 1280px·모바일 390px)과 체크리스트 1·19·20항이 결정 N 의 동작을 덮는다.
4. **결정 G(`agent_traces` 를 제품 조회 원천으로) — S3.6·원칙9 와 충돌 없음.** S3.6 은 브리핑 저장소를 정하지 않았고 P6-briefing 결정 H(i)·04-review 199행이 trace 를 유일 저장소로 확정했다. 원칙9 는 "기록하라" 이지 "읽지 말라" 가 아니며 조회는 trace 를 바꾸지 않는다(판정 7·10행). 코드: `app/briefing/run.py` 223~225행 `compose_output` 에 `schedule_id`·`person_id`, `models.py` 273행 JSONB — 조인 가능. 주의 두 가지(R-9): 조인 조건에 `tool_name='briefing' AND step='briefing_compose'` 둘 다 걸 것(같은 `tool_name` 의 `briefing_run`·`briefing_error` 행과 섞이지 않게), `TRACE_MAX_STRING = 2000`(`app/tools/context.py` 86행) 절단이 `lines[].text`(80자 상한)에 닿지 않음을 U3 테스트가 고정. 리스크 6(trace 키가 사실상 API 계약)은 계획이 인지했다.
5. **결정 M(오프라인 제외) — 흔적 없음.** 01-plan 에서 "오프라인|offline|IndexedDB|outbox" 는 3·35·109·290·347·349·350·351·359행뿐이고 전부 제외 선언·경과·향후 CR 출발점·불변식 3(캐시 없음) 문맥이다(evidence 2314). 작업 단위 U0~U10·판정 표 1~32행·산출물 목록·"기존 산출물 재사용" 표·registry 예정 파일에 0건(메인 세션 2330 메모 "오프라인 예정 파일 3개 제거 반영" 과 일치). `docs/proposal.md` 385행 "❌ 오프라인 사용" 과 일치. 불변식 3 `addEventListener('fetch'|caches.` 0건이 서비스 워커 쪽을 기계로 막는다.
6. **U0 하네스 — 방향은 L-002·L-004·FIX-027 과 맞으나 파일 지정 오류 1건([필수] R-1).** L-004(`docs/wiki/lessons/L-004-ask-before-stage.md` "계획·구현·검증 단계는 자동으로 시작하지 않고 사용자에게 묻고 시작한다")의 집행부가 `delegate-guard.sh` 15행 `GATED="architect backend-agent eval-agent verifier"`·`approve-commit.sh` 24·27행이고 frontend-agent 가 없다(리스크 1 사실 확인). L-002(역할·모델 분리): 결정 A sonnet — 계획 opus·검증 fable 과 다르고 SKILL.md 98~104행 표와 같은 구조. FIX-027(`docs/wiki/fixes/FIX-027.md` 21행 B "스테이징 파일에 `app/`·`alembic/` 이 있으면 … `review-FIX-nnn.md` 존재를 요구")의 `web/` 확대는 사용자 확정. **그러나 규칙 6 의 경로 판정은 `commit-guard.sh` 가 아니라 `.claude/scripts/fix_guard_check.py` 180행 `touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") …)` 에 있다.** `commit-guard.sh` 의 `app/·alembic/` 은 11·100행 주석뿐이고 106행이 파이썬을 호출한다. 01-plan 77행 표·88행 ④·91행 판정 `grep -n "web/" .claude/hooks/commit-guard.sh` 는 전부 셸 파일만 가리켜, 주석만 고쳐도 판정 grep 이 통과하고 실제 게이트는 열리지 않는다(⑤ test-guards 케이스가 제대로 쓰였을 때만 잡힌다). 훅 변경은 "diff 계획을 먼저 보이고 승인" 대상이므로 계획이 맞는 파일을 가리켜야 한다 → 05-remediation `F-` 소견, 01-plan 77·88·91행에 `fix_guard_check.py` 추가 요구. 순서 (가)~(마)는 안전하다 — 메모 plan-before-editing·FIX-027 "메인 세션은 코드를 직접 고치지 않는다" 는 제품 코드 규칙이고, 하네스 문서·훅은 P4b U0(`83d33dd`, 메인 세션)·FIX-027 선례대로 메인 세션 + verifier diff 리뷰. **게이트 구멍**: 정의 파일 `.claude/agents/frontend-agent.md` 가 없으면 Agent 호출 자체가 불가능하므로 구멍은 ①(정의 파일 생성)과 ②(GATED 추가) 사이에만 있고, `.claude/agents/*` 는 stage-gate 면제(89행)라 P8 활성화 전에도 쓸 수 있다 → ② 를 ① 보다 먼저(또는 같은 묶음에서) 적용하고 test-guards 통과 전 위임 금지를 03-log 에 기록(R-3). `stage-gate.sh` 는 제품 경로 목록이 아니라 면제 목록(89행)이라 `web/` 는 이미 게이트 대상 — ⑨ 불필요, 판정 `grep -n "web/" .claude/hooks/stage-gate.sh` 는 0건이 정상이 되어 판정으로 쓸 수 없다(R-2). Mac·Windows: 판정에 "CI windows job 의 훅 자가 점검 결과 success" 가 있고 `.github/workflows/tests.yml` 147행 windows job 이 `bash .claude/scripts/test-guards.sh` 를 돌린다 — 판정 가능. test-guards.sh 414~424행에 delegate-guard 케이스 틀(`ag` 헬퍼)과 123~199행 FIX-027 격리 저장소 틀이 있어 ⑤ 의 새 케이스를 같은 틀로 쓸 수 있다.
7. **판정 표 — 수용 기준 세 구절을 빠짐없이 덮는다**(6행 매핑). 자동 29행(1~28 + 17b) + 사람 4행. "실 네트워크 0" 은 판정 서문의 규칙이지 행이 아니다 — 가짜 표 밖 `fetch` 가 실패하는 것을 검사하는 테스트 1건과 Playwright 에서 수집한 요청 URL 이 전부 preview 호스트/`/api/` 임을 단언하는 행을 추가해야 "판정 가능" 해진다(R-5). 사람 점검 29~31행은 증거 항목 ①~⑫ 가 DB 조회 출력·trace id·사용자 문장으로 구체적이고 `docs/wiki/verification.md` 의 "인정하는 증거" 와 맞는다; 32행은 20항 각각 통과/수정 표기 + 반영 횟수(R-10). 11행 무변경 diff 경로에 `app/main.py`·`app/settings.py`·`app/api/deps.py` 가 빠져 있다 — 산출물은 `routes.py`·`schemas.py`·새 `read.py` 뿐이므로 그 밖의 `app/` 변경 0 을 판정에 넣어야 한다(R-6).
8. **"확인 필요" 사실 확인 결과**(evidence 2314): (a) `safety-guard.sh` 에 npm/npx/node 규칙 없음 — 규칙 F(116·117행)는 `curl|wget … | sh`·`iex` 만. `npm ci`·`npx shadcn`·`npx playwright install` 은 훅에 걸리지 않는다. 단 57행 `rm -r`·60행 `rimraf` 는 scratchpad 밖에서 차단되므로 npm 스크립트에서 둘 다 피한다. (b) `.claude/settings.json` allow(4~27행)에 npm/npx/node 없음 → 매번 권한 프롬프트. allow 추가는 `.claude/settings.json`(stage-gate 게이트 경로, 88행) 변경이라 사용자 결정 사항 — U0 에 넣을지 묻는다. (c) stage-gate `web/`: 면제 목록에 없어 이미 막힘(⑨ 불필요, R-2). (d) `.githooks/pre-commit` 패턴 35·38행 — 리스크 4 유지, 오탐 가능성 낮음. (e) Caddy `handle_path`·Chrome 설치 조건의 `fetch` 리스너 요구 여부는 이 검증에서 확인하지 않았다(계획대로 P9·U8 03-log).

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

**[필수]** (해소 전에는 `결과: 통과` 가 될 수 없다)
- **R-1 · 05-remediation `F-` 소견(출처 review)** — 01-plan 77행 표·88행 ④·91행 판정이 FIX 게이트 규칙 6 의 경로 확대 대상으로 `.claude/hooks/commit-guard.sh` 만 지목하지만, 실제 판정은 `.claude/scripts/fix_guard_check.py` 180행 `p.startswith("app/") or p.startswith("alembic/")` 이다(`commit-guard.sh` 11·100행은 주석, 106행이 이 파이썬을 호출). 조치: 01-plan 77행 "고치는 기존 파일" 에 `.claude/scripts/fix_guard_check.py`(180·203행과 22행 docstring) 추가, 88행 ④ 에 같은 파일 명시, 91행 판정 grep 에 `.claude/scripts/fix_guard_check.py` 추가. 계획 수정은 architect/메인 세션 몫, 재검증은 `verify-plan.sh` + 이 문서 2-1절 6 항 재확인.

**[권고]** (구현 단위·04-review 에서 반영 — 통과 조건 아님)
- **R-2** U0 판정 `grep -n "web/" .claude/hooks/stage-gate.sh` 삭제 또는 대체. `stage-gate.sh` 87~89행은 면제 목록 방식이라 `web/` 는 이미 게이트 대상(메인 세션 2330 메모와 같은 결론). 대체: `test-guards.sh` 에 "활성 작업 없음 → `web/x.ts` 쓰기 거부 / 활성·승인 뒤 허용" 1~2경우(408행 `gate` 헬퍼 선례). 01-plan 89행 ⑨ 는 "불필요" 로 03-log 에 기록.
- **R-3** U0 적용 순서: ②(`delegate-guard.sh` GATED)·③(`approve-commit.sh`)을 ①(`.claude/agents/frontend-agent.md`)보다 먼저 또는 같은 묶음에서 적용하고, (다) test-guards PASS 전에는 frontend-agent 위임 금지를 03-log U0 에 한 줄로 남긴다. 구멍은 ①~② 사이에만 있다(정의 파일 없이는 Agent 호출 불가).
- **R-4** 불변식 10 추가: 라우트 밖 패널이 결정 N 서랍 1개뿐 — 예: `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx` 결과가 사이드바 컴포넌트 1파일(+ `components/ui/` 기성 부품)뿐. 판정 13행(라우트 3개)이 못 잡는 "라우트 없는 네 번째 화면" 을 막는다.
- **R-5** "실 네트워크 0" 을 판정 행으로: Vitest setup 의 가짜 `fetch` 가 표에 없는 URL 에 throw 하는 것을 검사하는 테스트 1건(예: `fetch('https://example.invalid')` → reject), Playwright 각 spec 에서 `page.on('request')` 로 모은 URL 이 전부 preview 호스트 또는 `/api/` 임을 단언. 27행 불변식 또는 28행에 넣는다.
- **R-6** 판정 11행 무변경 경로에 `app/main.py app/settings.py app/api/deps.py` 추가(또는 `git diff --stat 50fd7fc -- app ':!app/api/routes.py' ':!app/api/schemas.py' ':!app/api/read.py'` 빈 출력). 산출물 표가 `app/` 변경을 세 파일로 한정했으므로 그 밖은 0 이어야 한다.
- **R-7** S3.1 카드 머리줄 "아래: P1-schema" 에 "P8-frontend(조회만, 스키마 무변경)" 한 줄 보충 — 선택. S3.4 는 이미 "적용: P8-frontend". 카드 수정은 메인 세션/architect(verifier 는 카드를 고치지 않는다).
- **R-8** 리스크 3 확인 결과를 U0/U4 03-log 에 기록: safety-guard 는 npm/npx 를 막지 않음(단 `rm -r`·`rimraf` 차단 — npm 스크립트 금지 목록에 `rimraf` 추가), settings.json allow 에 npm 없음(추가 여부는 사용자 결정 — `.claude/settings.json` 은 게이트 경로), `npx shadcn@<버전>`·`npx playwright@<버전>` 처럼 버전 고정, `package-lock.json` 커밋(계획 U4)으로 재현성.
- **R-9** U3 `GET /briefings` 조인 조건에 `tool_name='briefing' AND step='briefing_compose'` 둘 다; `briefing_run`·`briefing_error` 행 혼입 부정 케이스를 판정 10행에 추가. `output->>'schedule_id'`·`output->>'person_id'` 키 존재는 `run.py` 224~225행 확인.
- **R-10** 결정 L "수정 1회 상한" 은 기계 판정이 없으므로 U10 32행 증거 파일에 "수정 반영 횟수: n" 을 명시하고 04-review 가 n ≤ 1 을 확인. 넘으면 리스크 7 대로 CR 여부를 사용자에게.
- **R-11** 판정 8행 "헤더 없음 → `[]`" 에 "DB 쓰기 0(발급된 uuid 세션이 어디에도 저장되지 않음)" 단언 포함 — `resolve_session_id`(`deps.py` 207행)는 헤더가 없으면 uuid4 를 발급하므로 재사용 시 자연히 빈 목록이지만, 7행의 "조회는 쓰지 않는다" 를 8행에도 적용해 둔다.
- **R-12** `verify-plan.sh` registry 검사 출력이 `web/public/manifest.webmanifest` 를 `webma` 로 자른다(1절) — 파일명 파싱 한계, 판정 영향 없음. 하네스 FIX 후보로 기록.
- **R-13** U9 는 frontend-agent(E2E·문서)와 backend-agent(회귀) 두 담당이라 커밋 2개가 자연스럽다 — 03-log 에 해시 2개를 적거나 U9a/U9b 로 나눈다.

- R-1 은 `bash .claude/scripts/findings.sh P8-frontend evidence/20261010-2314-verify-plan-review.txt --source review` 로 05-remediation.md **`F-ce7d18` [필수]** 에 올렸고 verifier 는 원인 분석 칸까지만 채웠다(해결 단계·재검증은 계획 수정 주체 몫).

## 4. 결정
결과: 통과 — 재검증(개정 2, §5, 2026-10-10 23:35~23:40): [필수] R-1(`F-ce7d18`) 해소 확인, 권고 R-2~R-6·R-8~R-11·R-13 반영 확인, R-7 "택하지 않음" 기록 확인, R-12 리스크 12 로 기록. 새 소견은 권고 N-1~N-3 세 건(통과 조건 아님 — 04-review·U9 03-log 에서 반영). (1차 판정 2026-10-10 23:21 은 **보류** — 사유 [필수] R-1 1건: 01-plan 의 FIX 게이트 대상 파일 지정 오류. 점검표 8행은 1차부터 전부 통과였다.)
승인: 사용자 (2026-10-10) — 조건 ① U1~U9 모든 작업 단위는 커밋 전에 verifier 코드 리뷰를 받는다(사용자 선택 "모든 단위 리뷰" — 01-plan 의 단위별 /commit 앞에 끼운다, 04-review 가 단위별 리뷰 문서 존재를 확인) ② 디자인 추가 수정은 추후 사용자가 요청하면 별도 작업(FIX 또는 후속 패키지)으로 한다 — P8 안에서는 결정 L 의 수정 1회 상한 그대로. 활성화는 FIX-030(test-guards 상태 의존 시험, CI run 38052897284 실패 원인) 완료 뒤(사용자 결정 — 활성화하면 실패가 가려진다)

## 1-2. 기계 검증 2차 출력 (이 문서 작성 뒤 — 그대로 붙인다)
명령: `bash .claude/scripts/verify-plan.sh P8-frontend | tee docs/wiki/packages/P8-frontend/evidence/20261010-2321-verify-plan-verifier-2.txt` ("registry 중복 없음" PASS 39줄은 1차와 동일해 evidence 파일에서 한 줄로 줄였다. 기계 검증 "보류 0건" 은 점검표 판정 열만 세는 것이고 §4 결과는 보류다)
```
== verify-plan P8-frontend  (2026-10-10 23:21) ==
PASS  존재: docs/wiki/packages/P8-frontend/01-plan.md
PASS  존재: docs/wiki/packages/P8-frontend/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D7
PASS  패키지 id 등록됨: P11-demo
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P8-frontend
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  검증 항목 존재: R8
PASS  Refs 있음: U0 ~ U10 (11줄, 1차와 동일)
PASS  backlog 일치: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P6-memory
PASS  의존 완료: P7-push
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  registry 중복 없음: (39줄, 1차와 동일)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
== 결과: FAIL=0 WARN=0 ==
```

## 5. 재검증 (개정 2 — 소견 반영 뒤) · verifier (fable) 2026-10-10 23:35~23:40

대상: 01-plan.md 개정 2(3행 "02-plan-verify 소견 반영: [필수] R-1(`F-ce7d18`) + 권고 R-2~R-6·R-8~R-11·R-13, R-7 은 택하지 않음, R-12 는 하네스 FIX 후보 — 사용자 승인 2026-10-10"). 1차 §1~§4 는 지우지 않았다. 새 컨텍스트에서 다시 읽은 것: 01-plan 전문, 05-remediation 전문, `.claude/scripts/fix_guard_check.py` 1~70·110~210행, `.claude/hooks/commit-guard.sh`·`stage-gate.sh`·`delegate-guard.sh`·`approve-commit.sh`·`.claude/scripts/test-guards.sh`·`verify-plan.sh`(grep·부분), `app/briefing/run.py` 218~230행·`types.py` 215~229행, `app/api/deps.py` 201~211행.

### 5-1. 기계 검증 출력 (verifier 직접 실행 — 그대로)
명령: `bash .claude/scripts/verify-plan.sh P8-frontend` → `evidence/20261010-2335-verify-plan-verifier-re.txt`(출력 전체 + 아래 사실 확인 명령·출력). "registry 중복 없음" 40줄은 1차 39줄 + `web/src/__tests__/network.test.ts`(R-5 반영분)이고 전부 PASS 라 여기서는 한 줄로 줄였다.
```
== verify-plan P8-frontend  (2026-10-10 23:35) ==
PASS  존재: docs/wiki/packages/P8-frontend/01-plan.md
PASS  존재: docs/wiki/packages/P8-frontend/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D7
PASS  패키지 id 등록됨: P11-demo / P2-tools / P3-baselines / P5-loop / P6-briefing / P7-push / P8-frontend / P9-infra (8줄)
PASS  검증 항목 존재: R12 / R19 / R8 (3줄)
PASS  Refs 있음: U0 ~ U10 (11줄)
PASS  backlog 일치: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면
PASS  의존 완료: P5-loop / P6-briefing / P6-memory / P7-push (4줄)
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: (40줄 — 1차 39줄 + web/src/__tests__/network.test.ts)
== 결과: FAIL=0 WARN=0 ==
```
git(`gitlog.sh P8-frontend P8`, 23:35): `dev2` HEAD `50fd7fc` = origin/dev2 = 01-plan 8행 시작 해시 · 태그 `P8-frontend` 커밋 0 · 미커밋은 `HANDOFF.md`·`journal.md`·`packages/P8-frontend/` 문서만(제품 코드 0). 메인 세션 기계 검증 `evidence/20261010-2332-verify-plan-3.txt`(FAIL 0 / WARN 0)와 같은 결과다.

### 5-2. [필수] R-1(`F-ce7d18`) 해소 판정 — **해소**
근거(전부 `evidence/20261010-2335-verify-plan-verifier-re.txt`):
- **실제 코드 위치 재확인**: `grep -n -E 'app/|alembic/|web/' .claude/scripts/fix_guard_check.py` → 22행 docstring · 45행 주석 · **180행 `touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") for p in staged)`** · 203행 거부 메시지. `commit-guard.sh` 의 `app/·alembic/` 은 11·71·100행 모두 `#` 주석이고 106행 `fix_guard_out="$("$HOOK_PY" "$(dirname "$0")/../scripts/fix_guard_check.py" …)"` 가 호출부다. 1차 §2-1 6항의 사실과 같다.
- **01-plan 개정 2 가 가리키는 파일**: `grep -n "fix_guard_check.py" 01-plan.md` → 24·77·88·90·91·233·372·414행, `grep -n 'startswith("web/")' 01-plan.md` → 77·88·91행. 77행 표 "고치는 기존 파일" 열에 `.claude/scripts/fix_guard_check.py`(180행 조건 · 203행 메시지 · 22행 docstring)와 "`commit-guard.sh` 는 11·100행 **주석만** 정합(판정 코드 아님 — 106행이 `fix_guard_check.py` 호출)", 88행 ④ "**실제 판정 파일은 `.claude/scripts/fix_guard_check.py`** — 180행 … 에 `or p.startswith("web/")` 추가", 91행 판정 "`grep -n 'startswith("web/")' .claude/scripts/fix_guard_check.py`(180행 경로 조건에 1건 — **주석만 고쳐서는 통과하지 않는 판정**, R-1)" + "⑤ 의 새 5경우 … `fix_guard_check.py` 를 실제로 거쳐야 한다". 24·233·372행(범위·결정 B·리스크 2)·414행(읽은 카드)도 같은 취지. `F-ce7d18` 해결 단계 1행의 기대 출력을 전부 충족한다.
- **"주석만 고쳐도 통과" 가 되는지 — 직접 시험**(scratchpad 격리 git 저장소, 제품 파일 무변경, 초안 첫 줄 `fix(FIX-999): …`, `FIX-999.md` 없음): ① 현재 코드 + `web/x.ts` 스테이징 → exit 0(지금 게이트는 `web/` 를 모른다) ② 현재 코드 + `app/a.py` → exit 1 "[fix-guard] 제품 코드(app/·alembic/)를 바꾸는 FIX-999 커밋은 verifier 검증이 먼저다 …"(판정은 180행 조건) ③ 203행 메시지만 `app/·alembic/·web/` 로 바꾼 복사본 + `web/x.ts` → exit 0(메시지·주석만으로는 열리지 않는다 — 1차가 지적한 "셸 주석만 고치면 판정 grep 통과" 와 같은 함정이 파이썬 쪽 메시지에도 있음을 확인) ④ 180행에 `or p.startswith("web/")` 를 넣은 복사본 + `web/x.ts` → exit 1(계획 88행 ④ 의 수정이 실제로 게이트를 연다). 계획이 고칠 파일·줄과 판정 대상이 실제 코드와 일치한다.
- **판정 명령의 한계 1건(새 소견 N-1, 권고)**: ⑤ 파일 맨 위에 주석 `# TODO: p.startswith("web/")` 한 줄만 더한 복사본 → `grep -c 'startswith("web/")'` = 1 이지만 exit 0. 즉 91행의 grep **단독**은 주석에 속을 수 있다. 91행이 같은 판정에 test-guards ⑤ "`web/` FIX 커밋 거부/허용 2경우(`fix_guard_check.py` 를 실제로 거치는 시험)" 를 함께 요구하므로 R-1 은 해소하되, 04-review 는 둘을 **묶음**으로 요구하고 grep 단독 통과를 증거로 받지 않는다.
- `F-ce7d18` 상태를 "해소" 로 바꾸고 재검증·확인 결과 칸을 채웠다(05-remediation.md — verifier 몫). 머리줄 "열림: 0 (필수 0) | 해소: 1".

### 5-3. 권고 반영 판정 (R-2~R-13 — 소견 취지대로 들어갔는지)
| 소견 | 반영 판정 | 근거(01-plan 개정 2 행 · 인용 · 사실 확인) |
|------|-----------|------------------------------------------|
| R-2 stage-gate 판정 대체 | 반영 | 24행 "`stage-gate.sh` 는 면제 목록 방식이라 `web/` 가 이미 게이트 대상 — 수정 없이 test-guards 1경우로 확인", 77행 "`.claude/hooks/stage-gate.sh` 는 고치지 않는다 — 87~89행이 면제 목록 방식", 88행 ⑤ "활성 작업 없음 → `web/x.ts` 쓰기 거부 1경우(408행 `gate` 헬퍼 틀)", 89행 "⑨ 는 **불필요** … `grep "web/" stage-gate.sh` 는 0건이 정상이라 판정으로 쓰지 않는다", 91행 판정 목록에서 stage-gate grep 삭제됨. 사실: `grep -n "web/" .claude/hooks/stage-gate.sh` 0건, 88~89행 면제 case 는 `docs/*|.claude/*|…` 뿐, test-guards 352행 `gate()`·367행 `sg_gate()` 헬퍼 실재 |
| R-3 적용 순서·위임 금지 기록 | 반영 | 90행 "(나) … **적용 순서는 ②·③(위임 게이트) → ①(정의 파일) → ④~⑧**(R-3 …) → (다) … **(다) PASS 전에는 frontend-agent 위임 금지** 를 03-log U0 에 한 줄로 남긴다", 371행 리스크 1 "②·③ 을 ① 보다 먼저 적용하고 test-guards PASS 전에는 위임하지 않는다". 사실: `delegate-guard.sh` 15행 `GATED="architect backend-agent eval-agent verifier"`, `approve-commit.sh` 24·27행에 frontend-agent 없음(리스크 1 그대로) |
| R-4 불변식 10 | 반영 | 367행 "10. `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v "^web/src/components/ui/"` → 결정 N 사이드바(서랍) 컴포넌트 **1파일뿐**(파일 이름은 U4 에서 정해 03-log 에 기록). 라우트 밖 패널은 그 서랍 1개만 허용", 346행 결정 N "불변식 10(라우트 밖 패널은 이 서랍 1개만, R-4)", 153행 27행 "불변식 … (1~10)". 판정 가능(파일 수·이름). 범위 주의는 N-2 |
| R-5 실 네트워크 0 판정 행 | 반영 | 154행 27b "Vitest — setup 의 가짜 `fetch` 에 표에 없는 URL(`fetch('https://example.invalid')`) / Playwright — 각 spec(24~26행)에서 `page.on('request')` 로 모은 요청 URL 전부 → reject / 전부 preview 호스트의 앱 파일 또는 `/api/` 경로, 그 밖 0건", 69행 `network.test.ts` "가짜 표 밖 요청은 실패 를 검사(판정 27b행, R-5)", 100행 U9 "27b행 요청 URL 단언", 120행 서문·299행 결정 J "이 규칙 자체를 판정 27b행이 시험한다". 두 쪽 다 기대 출력이 명확해 판정 가능 |
| R-6 무변경 diff 경로 | 반영 | 136행 11행 "`git diff --stat 50fd7fc -- app alembic ':!app/api/routes.py' ':!app/api/schemas.py' ':!app/api/read.py'`(… `app/main.py`·`app/settings.py`·`app/api/deps.py` 포함 그 밖은 0, R-6) → 빈 출력". **pathspec 직접 시험**: 그 명령은 지금 빈 출력·exit 0; `git ls-files -- app alembic ':!app/api/routes.py' ':!app/api/schemas.py' ':!app/api/read.py' \| grep '^app/api/'` → `app/api/__init__.py`·`app/api/deps.py`(app/api 4파일 중 routes·schemas 만 빠짐, read.py 는 아직 없음) — 의도한 세 파일만 제외한다. 주의는 N-3 |
| R-7 S3.1 보충(선택) | 택하지 않음 — 기록 확인 | 274행 "verifier 는 선택 권고(R-7)로 냈고, **R-7 은 택하지 않음**(사용자 2026-10-10 — 권고 묶음에서 제외, S3.1 카드 무변경)", 3행에도 "R-7 은 택하지 않음". 카드 무변경이므로 점검표 4행 판정에 영향 없음 |
| R-8 npm·npx·삭제 명령 | 반영 | 95행 U4 "내려받기 명령은 `npx shadcn@<버전>`·`npx playwright@<버전>` 처럼 **버전을 고정**하고 쓴 버전을 03-log 에 남긴다, npm 스크립트에 … 셸 삭제 명령을 쓰지 않는다 — R-8·리스크 3", 227행 초안 ⑦("`safety-guard.sh` 60행이 … 막으므로 … 쓰지 않는다 — R-8")·⑧(버전 고정), 373행 리스크 3 (a)(b)(c) 확인 결과와 "allow 에 추가할지는 … **사용자 결정** — U0 diff 계획을 보일 때 함께 묻는다", 374행 리스크 4. 사실: `.claude/settings.json` 에 npm/npx/node 0건(재확인) |
| R-9 브리핑 조인 조건·혼입 부정 케이스 | 반영 | 94행 U3 "조건은 `tool_name='briefing' AND step='briefing_compose'` **둘 다** … `output->>'schedule_id'`·`output->>'person_id'`(`app/briefing/run.py` 224~225행)", 135행 10행 "일정 1 의 `briefing_compose` 보다 **나중**에 같은 `tool_name='briefing'` 의 `briefing_run`·`briefing_error` 행을 … 추가, 일정 3 은 `briefing_error` 행만 → 일정 1 은 여전히 `briefing_compose` 내용, 일정 3 은 목록에 없음(R-9)". **코드 대조**: `run.py` 223행 `compose_output: dict[str, Any] = {` · **224행 `"schedule_id": schedule.id,` · 225행 `"person_id": person_id,`** — 행 번호·키 일치. `types.py` 215행 `BRIEFING_TRACE_TOOL_NAME = "briefing"`, 219·223·229행 `STEP_BRIEFING_RUN/COMPOSE/ERROR = "briefing_run"/"briefing_compose"/"briefing_error"`, `run.py` 155~156·260~261·322~323행이 세 step 을 같은 tool_name 으로 기록 → 부정 케이스가 실제 데이터 모양과 맞는다 |
| R-10 수정 1회 상한 증거 | 반영 | 164행 32행 "증거 파일에 **"수정 반영 횟수: n"** 줄을 명시하고 04-review 가 n ≤ 1 을 확인한다 — 넘으면 리스크 7 대로 CR 여부를 사용자에게 묻는다(R-10)", 377행 리스크 7 동일 |
| R-11 헤더 없음 → DB 쓰기 0 | 반영 | 133행 8행 "`[]` + **DB 쓰기 0**(요청 전후 `pending_questions`·`agent_traces` 행 수 변화 0 — 서버가 발급한 uuid 세션이 어디에도 저장되지 않음, R-11)". 판정 가능: 행 수 비교. 코드: `app/api/deps.py` 207~208행 `if x_session_id is None: return str(uuid.uuid4())` — 저장 없음 |
| R-12 verify-plan 파일명 절단 | 리스크로 기록 | 382행 리스크 12 "(범위 밖 — 하네스 FIX 후보, R-12) … `webma` 로 자른다 … 이 패키지에서 고치지 않고 메인 세션이 FIX 후보로 올릴지 정한다". 이번 출력에도 `web/public/manifest.webma` 그대로(판정 영향 없음) |
| R-13 U9 커밋 2개 | 반영 | 100행 U9 "담당이 둘이라 **커밋은 2개가 될 수 있다**(U9a frontend-agent 몫 · U9b backend-agent 몫 — 03-log U9 에 해시 2개를 적는다, R-13)" |

### 5-4. 개정으로 생긴 새 문제 찾기 (상호 참조·합계·글자 일치)
- 자동 판정 행 `1~28 + 17b + 27b` = **30**(grep 30), 사람 점검 29~32 = **4**. "자동 30행" 표기는 100·101·120·297·381행 일관. 1차 §2-1 7항의 "자동 29행" 은 이제 30행이다(27b 추가) — 이 문서의 1차 기록은 그대로 두고 여기서 바로잡는다.
- 불변식 1~10, 체크리스트 1~20, 리스크 1~12, 결정 A~N, U0~U10 — 번호 연속·누락 없음. 교차 참조: 69행→27b, 100행→24~26·27b, 153행→불변식 1~10, 164행→리스크 7, 346행→25행·체크리스트 1·19·20·불변식 10, 377행→32행, 381행→30행 — 전부 존재하는 번호를 가리킨다.
- 수용 기준 줄 "- 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면" = `docs/backlog.md` 88행(PASS backlog 일치). 작업 단위 첫 줄 Refs 11/11.
- 원칙5·7 경계 유지: 37행 "네 번째 화면 … 만들지 않는다(원칙5)", 40행 "**경계 문장: 챗봇 UI 의 형태 … 를 빌리더라도 대화 내용은 기록 결과·확인 칩·브리핑의 한 줄 제안으로 한정한다**", 319행 "원칙7 경계 문장", 체크리스트 18항 — 개정 1 과 같다.
- 77·91행의 `.claude/hooks/approve-commit.sh` 경로 실재(`ls`), `.claude/scripts/` 에는 없다 — 계획 표기가 맞다.
- 1차 점검표 8행(§2)의 근거는 개정 2 에서 바뀐 행 번호(77·88~91·100·101·120·133·135·136·154·164·367·372·373)를 포함해도 결론이 바뀌지 않는다: 1행(제외 목록)·3행(D 카드)·4행(S 카드 — R-7 미채택으로 카드 무변경)·6행(수용 기준)·8행(보안 — R-8 반영으로 더 좋아짐) 그대로, 2행(원칙5 — 불변식 10 이 라우트 밖 패널을 잡아 1차의 R-4 유보가 해소)·5행(순서 — R-3 반영)·7행(Refs — U9 커밋 2개 R-13 반영) 보강. 8행 전부 **통과** 유지.

새 소견(전부 **권고** — 통과 조건 아님, FAIL/WARN 아님이라 `findings.sh` 소견은 만들지 않았다):
- **N-1** (U0 판정·04-review) 91행 `grep -n 'startswith("web/")' fix_guard_check.py` 는 주석 한 줄로도 1건이 된다(5-2 시험 ⑤). 04-review 는 이 grep 을 test-guards ⑤ "`web/` FIX 커밋 거부/허용 2경우" PASS 출력과 **묶음**으로만 증거로 받고, 증거에 180행 전후 `sed -n '178,182p'` 를 함께 남긴다.
- **N-2** (U9 불변식 10) `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx` 는 `web/src/__tests__/*.tsx` 와 주석·문자열("Dialog" 등)도 센다. 테스트 파일이 서랍 컴포넌트를 이름으로 import 하면 걸리지 않지만, "Sheet" 글자를 쓰면 2파일이 된다. U4 에서 서랍 컴포넌트 이름을 정할 때 `--exclude-dir=__tests__` 를 붙이거나 예외 파일을 03-log 에 적어 판정이 흔들리지 않게 한다. 취지(라우트 밖 패널 1개)는 그대로다.
- **N-3** (U9 11행) `git diff --stat 50fd7fc -- app alembic …` 은 **추적되지 않은 새 파일**을 보여 주지 않는다. U9 실행 시점에 U1~U3 이 전부 커밋돼 있어야 하고, 증거에 `git status --porcelain app alembic` 빈 출력을 함께 남겨 "커밋 안 된 `app/` 파일 0" 을 닫는다.

### 5-5. 재검증 결정
**통과.** [필수] 1건 해소(`F-ce7d18`), 권고 11건 반영·1건 미채택(R-7, 사용자 결정)·1건 리스크 기록(R-12). 새 소견 N-1~N-3 은 권고. 1차 판정은 §4 의 괄호 안에 남겼다. 승인은 사용자 몫(`승인:` 줄 비움). 이 절을 쓴 뒤 `verify-plan.sh` 를 다시 돌려 줄 형식(검증자 줄·점검표 8행·`결과:` 줄)이 깨지지 않았음을 확인했다 — `evidence/20261010-2342-verify-plan-verifier-re2.txt`(FAIL 0 / WARN 0, 점검표 행 카운트 8).
