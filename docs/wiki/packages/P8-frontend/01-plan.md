# P8-frontend · 계획 (01-plan)

상태: 초안 개정 2(architect — 02-plan-verify 소견 반영: [필수] R-1(`F-ce7d18`) + 권고 R-2~R-6·R-8~R-11·R-13, R-7 은 택하지 않음, R-12 는 하네스 FIX 후보 — 사용자 승인 2026-10-10 "R-1 + 권고 전부") · 개정 1(architect 작성 · 사용자 결정 2026-10-10 반영 — 결정 A~N 전부 확정: A 신설·sonnet · B·D·E·G·H·K·L 권장안 · C (ii) · N 모든 폭 왼쪽 사이드바(모바일 서랍형) · F 원문 조회 API · I 캐시 없음 · J 자동→사람 · M 오프라인 제외 · U0 `web/` 까지 FIX 게이트 확대 · 02-plan-verify 는 verifier 몫) | 담당: frontend-agent(신설 — `web/` 전부) + backend-agent(읽기 전용 조회 API — `app/api/` 와 새 조회 모듈) + 메인 세션(U0 하네스 · U10 사람 점검 진행) | 작성: 2026-10-10
태그 — 패키지: P8-frontend · 닫는 검증: 없음(INDEX 패키지 표 "닫는 R —") · 기대는 결정: D1 D2 D7 · 구현하는 명세: S3.4 S3.6 (읽기만: S3.1 S3.2 S3.5 — 스키마·툴 시그니처 무변경) · 관련 원칙: 원칙1 원칙5 원칙7 원칙8 원칙9
의존: P5-loop(04-review `결과: 완료`) · P6-memory(04-review `결과: 완료`) · P6-briefing(04-review `결과: 완료`) · P7-push(04-review `결과: 완료`) · 선행 게이트 P4b-er-redesign(04-review `결과: 완료`)

- 근거 해시(`.claude/gitlog.md` 스냅샷 2026-10-10 21:41, Bash 없이 읽음 — L-001): 작업 브랜치 `dev2` HEAD = `50fd7fc`(P7-push 완료 처리), 그 앞 FIX-029 `e555142`(푸시 모듈 순환 import). origin/dev = `f9500fe`, main(origin) = `0e943eb`. P7-push 단위 커밋 U1 `85393e0` · U2 `6c98516` · U3 `f256259` · U4 `8e9af9e` · U5 `55fc0f3` · U6 `572045a` · U7 `b73aaf0` · U8 `6428180`.
- **이 패키지의 시작 해시(무변경 diff 기준점) = `50fd7fc`.** 스냅샷 시점 미커밋 변경은 `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md` 두 개(문서)이고 제품 코드는 0이다. `dev2` 는 origin 보다 1커밋 앞서 있다(푸시는 메인 세션 몫).
- 태그 `P8-frontend` 로 이미 있는 커밋은 스냅샷에서 확인되지 않는다. 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P8-frontend S3.4 S3.6` 실행을 요청**한다.
- 저장소에 프론트 소스가 아직 없다(`web/`·`frontend/`·`package.json` Glob 0건, 이 계획 작성 시 확인).
- 선행 패키지가 넘긴 인계(이 계획이 기대는 것):
  - P5-loop 04-review §7: `POST /chat` 요청 `ChatIn{utterance}` + 헤더 `X-Session-Id`(선택, `^[A-Za-z0-9._-]{1,128}$`, 없으면 서버가 uuid4 발급). 응답 `ChatOut{reply, session_id, stored{persons,events,schedules}, pending_question{question_id,status,kind,question,options}|null, stop_reason|null, trace_ids[]}`. `POST /answers/{question_id}` 응답은 같은 다섯 필드 + `question_id`·`status`, 재개 중 새 질문이 나면 **새** `question_id`. **확인 칩 = `pending_question.options` 그대로.** 오류 규약: 공급자 오류·`ToolError` 는 200 + `stored` 전부 0 + `stop_reason=None` — 프론트는 200 이어도 `stored`·`pending_question` 을 봐야 한다. `SQLAlchemyError` 는 5xx.
  - P6-briefing 04-review §7: `BriefingRunOut{run_id, generated_at, briefings[{schedule_id, person_id, composer, pattern_sentences[{key,sentence}], lines[{text, basis}], suggestion{text,basis}|null, push}], skipped[]}`. 주기 작업이 만든 브리핑은 응답이 없으므로 **`agent_traces(tool_name='briefing', step='briefing_compose')` 가 유일한 저장소**(P6 결정 H(i)), `user_id` 열이 없어 `output.person_id → persons.user_id` 조인 필요. §6-6: 지정 모드 `schedule_id` 가 주기 작업에 잠긴 행이면 404 `not_found`.
  - P6-briefing 01-plan 범위 29행: "**브리핑 조회 API·프론트 브리핑 화면**(P8-frontend, 원칙5 화면 3개 고정) — … `GET /briefings/...` 는 backlog 수용 기준에 없어 만들지 않는다." → 조회 API 는 이 패키지 몫으로 넘어왔다.
  - P7-push 04-review §2-1 결정 A·§7: `/push-dev/` 는 제품 화면이 아니며 **제품 화면에서 링크하지 않는다**(P8 04-review 에서 재확인). `GET /push/vapid-public-key` → `{public_key}`(404 `push_not_configured`), `POST /push/subscriptions` ← `PushSubscription.toJSON()` → `{id, created}`. PWA 서비스 워커의 `push` 처리는 `app/push/devpage/sw.js` 를 옮겨 쓰고 **알림 클릭 → 브리핑 화면**을 더한다. **구독 해제 API 는 없다.** `briefings[].push` 어휘 6종.

## 목표

기획서 부록 A "화면은 셋입니다"(① 채팅 — 데이터가 들어가는 곳 / ② 인물 카드 — 쌓인 것이 보이는 곳 / ③ 브리핑 — 앱을 여는 이유)와 2장 범위 표의 "챗봇 UI (텍스트)"·"인물 카드 (사실 · 타임라인 · 마지막 접촉)"·"반응형 웹 + PWA", 그리고 부록 A 의 문장 — "평소처럼 얘기하면 하단에 확인 칩이 뜹니다", "타임라인 항목을 펼치면 원문 발화가 나옵니다. 요약이 틀렸을 때 근거를 확인하고 고칠 수 있습니다"(이 패키지는 **확인**까지, 고치기 폼은 없음 — 범위 참고), 8장 데모 "몇 턴 대화 → 인물 카드가 실시간으로 채워지는 화면"·"시간 앞당기기 → 브리핑"·"푸시 3중 안전장치: 웹푸시 / 인앱 배너 / 발표자 수동 트리거 버튼" — 을 실현한다. 지금까지 만든 백엔드(P5 루프·P6 메모리·브리핑·P7 푸시)는 `curl` 로만 볼 수 있다. 이 패키지는 그 위에 **화면 세 개와 PWA 껍데기**를 얹고, 화면이 읽어야 하지만 아직 없는 **읽기 전용 조회 API**(인물 목록·카드·원문·대기 질문·브리핑)를 백엔드에 더한다. 예: 사용자가 채팅에 "오늘 김팀장이랑 또 부딪혔어" 라고 쓰면 하단에 "김팀장을 기억해둘까요?" 와 서버가 준 선택지 칩이 뜨고, 칩을 누르면 `POST /answers/{id}` 로 이어진다. 사이드바의 인물 목록에서 김팀장 카드를 열어 타임라인 "09/03 회의에서 보고서 공개 지적" 을 펼치면 그때 사용자가 쓴 문장 그대로가 나온다. 브리핑 화면에는 다가오는 일정의 브리핑이 보이고, 데스크톱 알림을 누르면 그 일정의 브리핑으로 열린다. 화면은 **기성 컴포넌트·디자인 토큰으로 한 번에 정돈된 초안 수준**으로 만들고 맞춤 디자인 반복은 하지 않는다(결정 L — 사용자 요청 "실리콘밸리 대기업 화면들처럼 초안으로" 와 원칙5 "UI에 시간을 쓰지 않는다" 의 조정안).

## 범위

- 포함:
  - **하네스 준비(U0, 결정 A 확정)** — `frontend-agent` 정의 파일, L-004 위임 게이트(`delegate-guard.sh` 의 `GATED`·`approve-commit.sh` 의 `--stage` 목록)에 `frontend-agent` 추가, 규칙 6(제품 코드를 바꾸는 FIX/test 커밋은 verifier 리뷰 필수)의 대상 경로를 `web/` 까지 확대(사용자 확정 2026-10-10 — **경로 판정은 `.claude/scripts/fix_guard_check.py` 180행 `touches_product_code`** 이고 `commit-guard.sh` 는 106행에서 그 파이썬을 부를 뿐이라 주석 11·100행만 맞춘다, R-1), `test-guards.sh` 에 그 경우들 추가(`stage-gate.sh` 는 면제 목록 방식이라 `web/` 가 이미 게이트 대상 — 수정 없이 test-guards 1경우로 확인, R-2), `CLAUDE.md` 팀 표·`.claude/skills/devlog/SKILL.md` 역할표(L-002 표)·위임 문장·`docs/wiki/INDEX.md` 표기 갱신.
  - **읽기 전용 조회 API(백엔드, backend-agent)** — 인물 목록 `GET /persons`, 인물 카드 `GET /persons/{person_id}`, **원문 조회(결정 F 확정)** `GET /events/{event_id}/raw`·`GET /persons/{person_id}/facts/{fact_id}/sources`, 대기 질문 목록 `GET /questions/pending`(S3.4 "프론트 확인 칩 = 미답변 pending_questions", 기존 `list_pending()` 재사용), 브리핑 조회 `GET /briefings`(결정 G). 전부 `app_user_id()` 소유 확인(`persons.user_id` 조건), 다른 사용자 소유·없는 행은 기존 공통 404 `not_found` 규약. **조회는 DB 에 아무것도 쓰지 않는다**(`agent_traces` 행 0 — 결정 F "trace" 항목). `get_briefing` 툴은 부르지 않는다(이벤트 5건 상한·원문 미포함·`@traced`·`schedule_id` 시 `briefed_at` 쓰기 — 카드 조회 용도와 맞지 않음).
  - **프론트 소스 `web/`(frontend-agent, 결정 B·L)** — React + TypeScript + Vite, Tailwind CSS + shadcn/ui(결정 L 확정), 해시 라우팅 3경로(결정 C), API 클라이언트(응답 타입은 `app/api/schemas.py` 를 손으로 옮긴 TS 타입), 개발 서버 프록시.
  - **채팅 화면 + 확인 칩**(결정 D·E) — 발화 전송, `session_id` 보관·재전송, `pending_question` 칩, 앱을 다시 열었을 때 대기 질문 복원, 409(`already_answered`/`expired`) 처리, P5 오류 규약(200 이어도 실패 안내).
  - **인물 카드 화면 + 원문 펼치기**(결정 F) — 인물 목록 → 카드(관계 태그·위계·별칭·마지막 접촉·알고 있는 것·반복 패턴·타임라인·다가오는 일정), 타임라인 항목 펼치기 → 원문, 사실·패턴의 "근거 보기" → 근거 원문.
  - **브리핑 화면 + 수동 브리핑 버튼 + 푸시 구독 버튼**(결정 G·H) — 데모 "발표자 수동 트리거 버튼" = 기존 `POST /briefings/run {schedule_id}`. 푸시 구독 버튼은 이 화면 안에 둔다(새 화면 금지, 원칙5).
  - **PWA 껍데기**(결정 I) — `manifest.webmanifest`, 범위 `/` 서비스 워커(`push` → 알림, `notificationclick` → 브리핑 화면, 열린 창에 인앱 배너 메시지). 캐시는 하지 않는다(결정 I).
  - **자동 테스트 → 사람 점검(결정 J 확정)** — Vitest 컴포넌트 테스트 + Playwright E2E(가짜 API), 그 뒤 사람 점검 체크리스트.
  - **CI**(결정 B) — `.github/workflows/tests.yml` 에 프론트 job.
  - **문서** — `docs/RUNNING.md` "프론트 실행" 한 절, `registry.md` 새 행·비고 확장, `.gitignore`(`web/node_modules/`·`web/dist/`·Playwright 산출물).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **오프라인 사용(발화 대기열·앱 셸 캐시)** — 사용자 확정 2026-10-10 "오프라인 빼기"(결정 M). 기획서 부록 A 385행 "안 되는 것: 오프라인 사용" 그대로다. 다시 넣으려면 `/devlog change` CR 이 필요하다.
  - **backlog P8 두 번째 줄 "사용자별 메모리 설정을 앱 안에서 선택(패턴 기간·횟수, 카드 정리 기준)"** — backlog 그 줄 스스로 "[미정 — CR 필요]" 이고 "사용자별 저장은 스키마 v2 변경(설정 테이블), 선택 UI 는 기존 3화면 안(원칙5)이라 CR 선행" 이라고 적혀 있다. 이 패키지의 수용 기준은 첫 줄뿐이다. 설정 UI 는 만들지 않고, 설정은 지금처럼 서버 환경변수(`PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`)로만 고른다.
  - **네 번째 화면** — 설정·로그인·구독 관리·trace 보기·인물 추가 폼 화면을 만들지 않는다(원칙5). 인물 목록은 카드 화면의 일부, 푸시 구독 버튼은 브리핑 화면의 일부다. 기획서 3.5 "에이전트가 어떻게 판단했는지를 보여주는 화면" 은 화면을 늘리는 문장이라 이 패키지에서 다루지 않는다(리스크 참고).
  - **카드에서 사실·요약을 고치는 기능**(부록 A "근거를 확인하고 고칠 수 있습니다" 의 "고치기") — 고치는 경로는 대화(채팅 → 루프 → `update_person`)다. 카드에 편집 폼을 두면 툴 7종을 우회하는 쓰기 경로가 생겨 원칙9(모든 판정에 근거)가 깨진다.
  - **관계 태그 필터링** — 기획서 2장 제외 열 "관계 태그 필터링". 인물 목록은 태그를 보여 주기만 하고 걸러 내는 컨트롤을 두지 않는다.
  - **고민 상담·감정 대화·상담 페르소나·톤 설정, 인물 간(A–B) 관계, 음성 입력, 네이티브 앱**(원칙7) — 채팅 응답은 서버 `reply` 를 그대로 보여 줄 뿐 프론트가 문장을 만들지 않는다. 마이크·음성 API 를 쓰지 않는다. 설치는 PWA 로만. **경계 문장: 챗봇 UI 의 형태(메신저형 대화 화면)를 빌리더라도 대화 내용은 기록 결과·확인 칩·브리핑의 한 줄 제안으로 한정한다**(결정 L).
  - **인증·로그인·다중 사용자** — 단일 사용자 전제(`app_user_id()`, P5-loop 결정 I). 다중 사용자 격리 부채(F-fbaaae)는 backlog 리스크 로그대로 P9-infra 전 과제다(결정 D).
  - **구독 해제 API·해제 버튼** — 수용 기준에 없다(결정 H).
  - **스키마 v2 변경·툴 7종 시그니처 변경·루프·ER·메모리·브리핑 생성 로직 변경** — S3.1·S3.2 가 권위다. 조회 API 는 기존 테이블을 읽기만 한다.
  - **P6 §6-6 지정 모드 잠금 404 의 백엔드 수정** — 프론트가 안내하는 데까지(결정 K). 백엔드 수정은 FIX 후보.
  - **`app/push/devpage/` 수정·제품 화면에서 `/push-dev/` 링크** — P7 결정 A 조건. 제품 서비스 워커는 그 파일을 **복사해** 쓰고 원본은 건드리지 않는다.
  - **운영 배포(S3 + CloudFront, Caddy TLS, CloudFront 경로 동작 설정)** — D7 "적용 시점 P9-infra". 이 패키지는 `vite build` 산출물과 P9 가 옮겨 쓸 프록시 규칙 문서까지다(결정 C).
  - **실제 LLM·실제 푸시 서비스를 자동 테스트에서 쓰는 것** — 결정 J. 실 LLM·실 푸시는 U10 사람 점검에서 사용자·메인 세션만.
  - **맞춤 디자인 반복**(브랜딩·일러스트·커스텀 애니메이션·디자인 시안 여러 벌·시각 회귀 테스트·Storybook·다국어·접근성 감사) — 결정 L 의 시간 상한 밖.

## 산출물 (파일 경로)

**새로 만드는 파일** (프론트 경로는 결정 B·C·I·L 확정안 기준)

- `.claude/agents/frontend-agent.md` — 프론트 구현 에이전트 정의(결정 A, U0)
- `app/api/read.py` — 읽기 전용 조회 함수(인물 목록·카드·원문·근거·브리핑 조회 — DB 를 읽기만, trace 없음). 이름은 U1 에서 registry grep 후 확정
- `tests/test_api_read_persons.py` — `GET /persons`·`GET /persons/{id}`
- `tests/test_api_read_raw.py` — `GET /events/{id}/raw`·`GET /persons/{id}/facts/{fact_id}/sources` 원문·근거·소유 확인
- `tests/test_api_questions_pending.py` — `GET /questions/pending`
- `tests/test_api_read_briefings.py` — `GET /briefings`
- `web/package.json` · `web/package-lock.json` · `web/tsconfig.json` · `web/vite.config.ts` · `web/index.html` · `web/tailwind.config.ts` · `web/components.json` — 빌드·디자인 토큰 골격(결정 B·L)
- `web/src/main.tsx` · `web/src/App.tsx` · `web/src/routes.ts` — 진입점·해시 라우팅 3경로(결정 C)
- `web/src/styles/tokens.css` — 색·간격·글꼴 토큰(밝은/어두운 두 벌, 결정 L)
- `web/src/components/ui/` — shadcn/ui 에서 가져온 기성 컴포넌트(Button·Card·Badge·Collapsible·Toast·Skeleton·Tabs 등, 결정 L)
- `web/src/api/client.ts` · `web/src/api/types.ts` — API 호출·응답 타입
- `web/src/session.ts` — `session_id` 보관(결정 D)
- `web/src/screens/ChatScreen.tsx` · `web/src/screens/PersonCardScreen.tsx` · `web/src/screens/BriefingScreen.tsx` — 화면 3개
- `web/src/push.ts` — 서비스 워커 등록·푸시 구독(결정 H)
- `web/public/sw.js` · `web/public/manifest.webmanifest` · `web/public/icon-192.png` · `web/public/icon-512.png` — PWA(결정 I)
- `web/src/__tests__/chat.test.tsx` · `web/src/__tests__/card.test.tsx` · `web/src/__tests__/briefing.test.tsx` · `web/src/__tests__/routes.test.ts` · `web/src/__tests__/sw.test.ts` · `web/src/__tests__/push.test.ts` · `web/src/__tests__/network.test.ts` — 컴포넌트·서비스 워커 단위 테스트(결정 J), 마지막 것은 "가짜 표 밖 요청은 실패" 를 검사(판정 27b행, R-5)
- `web/playwright.config.ts` · `web/e2e/chat.spec.ts` · `web/e2e/card.spec.ts` · `web/e2e/briefing.spec.ts` · `web/e2e/fixtures/api.ts` — E2E(가짜 API, 결정 J)

**고치는 기존 파일** (registry 에 다른 패키지 행으로 있다 — 새 행이 아니라 비고 확장)

| 파일 | 고치는 내용 | 원래 패키지 |
|------|------------|------------|
| `app/api/routes.py` · `app/api/schemas.py` | 조회 라우트 6개와 응답 스키마(원문 필드는 원문 조회 두 응답에만) | P2-tools / P5-loop / P6-briefing |
| `.claude/hooks/delegate-guard.sh` · `.claude/hooks/approve-commit.sh` · `.claude/scripts/fix_guard_check.py` · `.claude/hooks/commit-guard.sh` · `.claude/scripts/test-guards.sh` | `frontend-agent` 를 위임 게이트 대상(`delegate-guard.sh` 15행 `GATED`)·`--stage` 선택지(`approve-commit.sh` 24·27행)에 추가 · **규칙 6 경로 판정 확대는 `.claude/scripts/fix_guard_check.py`** — 180행 `touches_product_code` 조건에 `p.startswith("web/")` 추가, 203행 거부 메시지 "제품 코드(app/·alembic/)" 와 22행 docstring 에 `web/` (R-1) · `commit-guard.sh` 는 11·100행 **주석만** 정합(판정 코드 아님 — 106행이 `fix_guard_check.py` 호출) · `test-guards.sh` 자가 점검 경우 추가(U0). `.claude/hooks/stage-gate.sh` 는 고치지 않는다 — 87~89행이 면제 목록 방식이라 `web/` 는 이미 게이트 대상(R-2, test-guards 1경우로 확인) | 하네스(FIX-027 규칙 6) |
| `CLAUDE.md` · `.claude/skills/devlog/SKILL.md` · `docs/wiki/INDEX.md` | 팀 구성 표에 `frontend-agent` 행, "아직 만들지 않았다" 문장에서 `frontend-agent` 제거, SKILL.md L-002 역할표 행·"구현(backend-agent, eval-agent)" 위임 문장들에 frontend-agent, INDEX P8 행 담당 | 하네스 |
| `.github/workflows/tests.yml` | 프론트 job(결정 B) | 하네스(FIX-022) |
| `.gitignore` | `web/node_modules/`·`web/dist/`·`web/test-results/`·`web/playwright-report/` | 하네스 |
| `docs/RUNNING.md` · `docs/wiki/registry.md` | "프론트 실행" 한 절 · 행 추가/비고 확장 | — |

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

백엔드 단위의 완료 판정 명령은 로컬 기준 `POSTGRES_PORT=5433 .venv/bin/python -m pytest …` 이고 테스트 DB 는 `relationship_test`(FIX-006)다. 프론트 단위의 완료 판정 명령은 `web/` 에서 `npm run typecheck` · `npm test -- --run` · `npm run e2e` · `npm run build`(스크립트 이름은 U4 에서 `package.json` 에 확정)이다. **자동 테스트는 실제 LLM·실제 푸시 서비스로 아무것도 보내지 않는다**(결정 J). 시간은 백엔드 `get_now()` 오버라이드·프론트 가짜 시계로 고정한다. 출력은 `docs/wiki/packages/P8-frontend/evidence/<YYYYMMDD-HHMM>-<이름>.txt`. 위임은 단위마다 L-004(AskUserQuestion → `approve-commit.sh --stage <에이전트>`). **U0 커밋 전에는 frontend-agent 를 띄우지 않는다**(게이트 구멍 — 리스크 1).

- [ ] U0 하네스 — frontend-agent 신설·위임 게이트·FIX 게이트 `web/` 확대 — [메인 세션, 사용자 승인 뒤] (결정 A 확정 · FIX 게이트 확대는 사용자 확정 2026-10-10 "web/ 까지 넓힌다". 제품 코드 아님. `.claude/agents/*` 는 stage-gate 면제지만 `.claude/hooks/*`·`.claude/scripts/*` 는 활성 작업을 요구하므로 P8 활성화 뒤 첫 단위.) / Refs: P8-frontend L-002 L-004 원칙5
      - 바꾸는 것: ① `.claude/agents/frontend-agent.md`(결정 A "초안 내용", `model: sonnet`) ② `delegate-guard.sh` `GATED` 에 `frontend-agent` ③ `approve-commit.sh` `--stage` case·usage 에 `frontend-agent` ④ 규칙 6 — 제품 코드를 바꾸는 FIX/test 커밋의 verifier 리뷰 필수 대상 경로를 `app/`·`alembic/` 에서 `app/`·`alembic/`·`web/` 로 확대. **실제 판정 파일은 `.claude/scripts/fix_guard_check.py`** — 180행 `touches_product_code = any(p.startswith("app/") or p.startswith("alembic/") …)` 에 `or p.startswith("web/")` 추가, 203행 거부 메시지 "제품 코드(app/·alembic/)" 와 22행 docstring 에 `web/` 추가. `commit-guard.sh` 는 11·100행 주석만 같은 문구로 맞춘다(R-1, `F-ce7d18`) ⑤ `test-guards.sh` 에 경우 추가 — "frontend-agent 위임은 마커 없으면 거부 / 마커 있으면 허용" 2경우 + "`web/` 를 바꾸는 FIX 커밋은 `검증:` 줄·`review-FIX-nnn.md` 없으면 거부 / 있으면 허용" 2경우(123~199행 FIX-027 격리 저장소 틀 — `fix_guard_check.py` 를 실제로 거치는 시험) + "활성 작업 없음 → `web/x.ts` 쓰기 거부" 1경우(408행 `gate` 헬퍼 틀, R-2) — 모두 5경우 ⑥ `CLAUDE.md` 팀 표 1행·"아직 만들지 않았다" 문장·FIX 검증 분리 문장의 경로(`app/`·`alembic/` → `web/` 포함) ⑦ `SKILL.md` L-002 역할표 1행·위임 문장 ⑧ `INDEX.md` P8 행.
      - `stage-gate.sh` 는 고치지 않는다(R-2 — verifier 확인: 87~89행이 면제 목록 방식이라 `web/` 는 이미 활성 작업을 요구한다). 앞 초안의 확인 항목 "⑨ `web/` 추가" 는 **불필요**로 정리하고 03-log U0 에 한 줄로 남긴다. 대신 ⑤ 의 "활성 작업 없음 → `web/` 쓰기 거부" 1경우가 이것을 실제로 시험한다(`grep "web/" stage-gate.sh` 는 0건이 정상이라 판정으로 쓰지 않는다).
      - 순서(사용자 지시 "고치기 전에 계획을 먼저 보이고 승인" — 훅·안전장치): (가) 메인 세션이 ②~⑤의 **훅·스크립트 변경 diff 계획**(`fix_guard_check.py` 포함)을 사용자에게 먼저 보이고 AskUserQuestion 으로 승인 → (나) 승인된 diff 만 메인 세션이 Write/Edit 로 적용하되 **적용 순서는 ②·③(위임 게이트) → ①(정의 파일) → ④~⑧**(R-3 — 게이트 구멍은 정의 파일이 생긴 뒤 GATED 에 이름이 들어가기 전 사이에만 있으므로, 이름을 먼저 게이트에 넣는다) → (다) `test-guards.sh` 실행·증거. **(다) PASS 전에는 frontend-agent 위임 금지** 를 03-log U0 에 한 줄로 남긴다(R-3) → (라) verifier 가 커밋 전 훅 diff 를 리뷰 → (마) `/commit`.
      - 판정: `bash .claude/scripts/test-guards.sh`(Mac 전부 PASS, ⑤ 의 새 5경우 포함 — 특히 "`web/` FIX 커밋 리뷰 없으면 거부 / 있으면 허용" 2경우가 `fix_guard_check.py` 를 실제로 거쳐야 한다) + `grep -n 'startswith("web/")' .claude/scripts/fix_guard_check.py`(180행 경로 조건에 1건 — **주석만 고쳐서는 통과하지 않는 판정**, R-1) + `grep -n "web/" .claude/scripts/fix_guard_check.py`(22행 docstring·203행 메시지 포함) + `grep -n "frontend-agent" .claude/hooks/delegate-guard.sh .claude/hooks/approve-commit.sh CLAUDE.md .claude/skills/devlog/SKILL.md` + (주석 정합만) `grep -n "web/" .claude/hooks/commit-guard.sh` · **Mac·Windows 양쪽 동작**(사용자 요구 — 하네스 훅·스크립트): Windows 는 CI windows job 의 훅 자가 점검 결과(FIX-022 가 넣은 단계, 메인 세션 `gh run view <id>`)가 success · 증거 `evidence/*-u0-harness.txt` / Refs: P8-frontend L-002 L-004 원칙5
- [ ] U1 인물 목록·카드 조회 API — [backend-agent] `GET /persons` → `[{id, display_name, relation_tag, hierarchy, last_contact_at|null}]`(정렬: `last_contact_at` 내림차순·없으면 뒤, 필터 인자 없음), `GET /persons/{person_id}` → `{person{id, display_name, relation_tag, hierarchy}, aliases[], last_contact_at, facts[{id, key, value, updated_at, source_count}](`pattern:` 접두 제외), patterns[{id, key, value, source_count}](`pattern:` 접두만), timeline[{id, type, content, occurred_at}](최근 순, 상한은 코드 상수 — U1 에서 값 확정), upcoming_schedules[{id, title, scheduled_at, briefed_at}]}`. `last_contact_at` = 그 인물 `events.occurred_at` 최댓값. 응답 어디에도 `raw_utterance` 없음. DB 쓰기 0·trace 0. 판정: `pytest tests/test_api_read_persons.py -v` · 증거 `evidence/*-u1-read-persons.txt` / Refs: P8-frontend S3.1 S3.5 원칙9
- [ ] U2 원문 조회 API(결정 F 확정) — [backend-agent] `GET /events/{event_id}/raw` → `{event_id, person_id, type, content, occurred_at, raw_utterance}`(저장된 문자열 그대로), `GET /persons/{person_id}/facts/{fact_id}/sources` → `{fact{id, key, value}, sources[{event_id, type, content, occurred_at, raw_utterance}]}`(`fact_sources` → `events` 조인, `occurred_at` 내림차순, 상한 코드 상수). 사용자 격리: 두 엔드포인트 모두 `persons.user_id = app_user_id()` 를 조인 조건으로 걸고, 두 번째는 `person_facts.person_id = person_id` 도 건다(다른 인물의 사실 id 로 넘겨짚기 차단). 없는 것·남의 것은 같은 404. DB 쓰기 0·trace 0. 판정: `pytest tests/test_api_read_raw.py -v` · 증거 `evidence/*-u2-read-raw.txt` / Refs: P8-frontend S3.1 R8 원칙9
- [ ] U3 대기 질문·브리핑 조회 API — [backend-agent] `GET /questions/pending` → `[{question_id, status, kind, question, options}]`(헤더 `X-Session-Id` 의 세션, 기존 `app.tools.questions.list_pending(ctx, session_id)` 재사용 — 새 조회 로직 금지, 헤더 없으면 빈 목록, 형식 위반 422 는 `/chat` 과 같은 규칙). `GET /briefings`(선택 쿼리 `schedule_id`) → `[{schedule{id, title, scheduled_at}, person{id, display_name}, generated_at, composer, pattern_sentences[], lines[{text, basis}], suggestion|null, push, trace_id}]` — 원천은 `briefing_compose` trace 중 **일정마다 가장 최근 1행**(결정 G) — 조건은 `tool_name='briefing' AND step='briefing_compose'` **둘 다**(같은 `tool_name` 의 `briefing_run`·`briefing_error` 행이 섞이지 않게, R-9), `output->>'schedule_id'`·`output->>'person_id'`(`app/briefing/run.py` 224~225행) 로 `persons.user_id = app_user_id()` 조인. 대상 일정은 `scheduled_at ≥ now − 기간 상수`(값은 U3 에서 확정). `briefing_error` 만 있는 일정은 넣지 않는다. 원문 필드 없음. DB 쓰기 0·trace 0. 판정: `pytest tests/test_api_questions_pending.py tests/test_api_read_briefings.py -v` · 증거 `evidence/*-u3-read-questions-briefings.txt` / Refs: P8-frontend S3.4 S3.6 D2 R12
- [ ] U4 프론트 골격·디자인 토큰·도구·CI — [frontend-agent] 첫 명령 `node --version`·`npm --version`(Mac 은 `node v24.21.0`·`npm 11.19.0` 확인됨 — 메인 세션 2026-10-10, 출력이 다르면 멈추고 보고. Windows 는 CI windows job 으로 확인). `web/` 생성(Vite + React + TypeScript, 결정 B), Tailwind + shadcn/ui 초기화와 토큰(결정 L — 내려받기 명령은 `npx shadcn@<버전>`·`npx playwright@<버전>` 처럼 **버전을 고정**하고 쓴 버전을 03-log 에 남긴다, npm 스크립트에 `rimraf`·`rm -r` 를 쓰지 않는다 — R-8·리스크 3), 앱 틀(결정 N 확정 — 모든 폭에서 왼쪽 사이드바: 위 3개 항목 + 아래 인물 목록 + 본문. 데스크톱(≥ 1024px)은 항상 보임, 모바일·중간 폭은 왼쪽 위 메뉴 버튼으로 여닫는 서랍형이고 항목을 고르면 닫힘. 하단 탭바 없음. 열림/닫힘은 레이아웃 상태일 뿐 라우트·저장 설정 아님), 해시 라우팅 3경로 `#/chat`·`#/persons`(`#/persons/:id`)·`#/briefings`(결정 C), API 클라이언트·타입, Vite 개발 서버 프록시(결정 C 확정 (ii) — `/api` 접두를 벗겨 `http://localhost:8000` 으로, 포트는 설정), 빈 화면 3개, Vitest + Testing Library + jsdom, Playwright 설정, `package-lock.json` 커밋, `engines` 기록, `.gitignore`, `.github/workflows/tests.yml` 프론트 job(결정 B). 판정: `cd web && npm ci && npm run typecheck && npm test -- --run && npm run build`(출력 전부) · 증거 `evidence/*-u4-skeleton.txt` / Refs: P8-frontend 원칙5 D7
- [ ] U5 채팅 화면 + 확인 칩 — [frontend-agent] 발화 입력·전송(`POST /api/chat`), 응답 `session_id` 를 `localStorage` 에 보관하고 다음 요청 헤더로 재전송(결정 D), 대화 기록은 화면 메모리에만(새로고침하면 지워짐 — 서버에 대화 이력 API 없음), 챗봇형 대화 UI(결정 L 사용자 방향 — 꽉 찬 대화 영역·하단 고정 자동 높이 입력창·오른쪽 사용자 말풍선/왼쪽 본문형 응답·타이핑 점·자동 스크롤), `pending_question` 이 있으면 그 응답 바로 아래에 `options` 칩 한 줄(문자열·순서 그대로), 칩 클릭 → `POST /api/answers/{question_id} {answer}` → 누른 칩은 선택 상태로 고정·나머지 비활성 → `reply` 이어 붙임·새 `pending_question` 이면 그 아래 새 칩, 화면 진입 시 `GET /api/questions/pending` 으로 대기 칩 복원, 대기 중에도 입력 가능(결정 E), 409 `already_answered`/`expired` → 그 질문 칩 비활성·한 줄 안내, P5 오류 규약·5xx → 한 줄 안내. 판정: `npm test -- --run src/__tests__/chat.test.tsx` · 증거 `evidence/*-u5-chat.txt` / Refs: P8-frontend S3.4 D1 D2 원칙1 원칙7
- [ ] U6 인물 카드 화면 + 원문 펼치기 — [frontend-agent] `#/persons` 인물 목록(이름·태그·위계·마지막 접촉, 필터 컨트롤 없음 — 같은 목록 컴포넌트를 결정 N 사이드바 아래쪽에도 그린다, 새 API·새 라우트 없음) → `#/persons/:id` 카드(부록 A ② 순서), 타임라인 항목 펼치기 → `GET /api/events/{id}/raw` 1회 → 원문 표시(다시 펼치면 재요청 없음), 사실·패턴 "근거 보기" → `GET /api/persons/{id}/facts/{fact_id}/sources`, 접기, 조회 실패 시 그 항목에만 안내. 채팅 응답 `stored.persons/events > 0` 이면 카드 화면으로 가는 링크 한 줄. 판정: `npm test -- --run src/__tests__/card.test.tsx` · 증거 `evidence/*-u6-card.txt` / Refs: P8-frontend R8 S3.5 원칙7
- [ ] U7 브리핑 화면 + 수동 브리핑 버튼 — [frontend-agent] `#/briefings` 에 `GET /api/briefings` 목록(머리줄 "일정 시각 · 이름 · 일정 제목", 패턴 문장·요약 줄·제안 한 줄 — 서버 문자열 그대로), `#/briefings?schedule_id=N` 이면 그 일정을 맨 위·강조, 일정마다 "지금 브리핑" 버튼 → `POST /api/briefings/run {schedule_id}` → 목록 다시 읽기(결정 K: 404 → "잠시 뒤 다시 시도"), 빈 상태 문구. 판정: `npm test -- --run src/__tests__/briefing.test.tsx` · 증거 `evidence/*-u7-briefing.txt` / Refs: P8-frontend S3.6 R19 원칙7
- [ ] U8 PWA·푸시 구독 — [frontend-agent] `manifest.webmanifest`(이름·아이콘 2종·`start_url` `/#/chat`·`display: standalone`), `web/public/sw.js`(범위 `/`: `push` → `showNotification(title, {body, tag, data:{schedule_id}})` — `app/push/devpage/sw.js` 의 페이로드 해석을 **복사**, `notificationclick` → 열린 창 포커스 후 `#/briefings?schedule_id=N`·없으면 `clients.openWindow`, 열린 창에 `postMessage({type:"briefing", schedule_id})` → 인앱 배너, 캐시 없음·`fetch` 리스너 없음 — 결정 I), `web/src/push.ts`(브리핑 화면 "알림 받기": 권한 → `register('/sw.js')` → `GET /api/push/vapid-public-key` → `pushManager.subscribe({userVisibleOnly:true, applicationServerKey})` → `POST /api/push/subscriptions`, 404 `push_not_configured` → 안내 한 줄, 이미 구독돼 있으면 "알림 켜짐"). 판정: `npm test -- --run src/__tests__/sw.test.ts src/__tests__/push.test.ts` · 증거 `evidence/*-u8-pwa-push.txt` / Refs: P8-frontend S3.6 R12 원칙5
- [ ] U9 E2E·자동 판정 전체·문서 — [frontend-agent: E2E·프론트 행·불변식 grep·RUNNING] + [backend-agent: 백엔드 행·전체 회귀] Playwright E2E 3편(가짜 API, 판정 24~26행·27b행 요청 URL 단언), 아래 자동 판정 1~28행(17b·27b 포함 30행) 실행, 전체 회귀(`POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs`, skip 0), `alembic check`, `python scripts/tools_check.py` 7/7, 무변경 diff, "지킬 불변식" 절 grep, `docs/RUNNING.md` "프론트 실행" 절(백엔드 기동 → `cd web && npm ci && npm run dev` → 주소, 프록시 규칙, VAPID 는 P7 절 참조, 포트 일치 안내, Mac·Windows 명령), `registry.md` 갱신. 담당이 둘이라 **커밋은 2개가 될 수 있다**(U9a frontend-agent 몫 · U9b backend-agent 몫 — 03-log U9 에 해시 2개를 적는다, R-13). 증거 `evidence/*-u9-*.txt` / Refs: P8-frontend 원칙5 원칙8 원칙9
- [ ] U10 사람 점검 — 실서버·실 LLM·데스크톱 Chrome — [사용자·메인 세션] (에이전트 아님 — 실 LLM 비용·실 푸시 외부 전송·사람 눈.) **U9 자동 판정 1~28행(17b·27b 포함 30행)이 전부 통과한 뒤에만**(결정 J 확정 순서). 아래 "사람 점검 절차" 그대로. 판정 표 29~32행. 증거 `evidence/*-u10-check-chat.txt` · `*-u10-check-card.txt` · `*-u10-check-briefing.txt` · `*-u10-check-screens.txt` / Refs: P8-frontend S3.4 S3.6 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면

## 해석 — 수용 기준 (위 한 줄을 판정 가능한 문장으로 — 새 기준을 더하는 것이 아니다)

backlog 항목 본문 "프론트 3화면 + PWA" 가 이 수용 기준의 틀을 정한다. 세 구절을 각각 화면 하나의 핵심 행동으로 읽는다. (오프라인은 이 수용 기준에 없고 범위에서 제외했다 — 결정 M.)

| # | 원문 구절 | 이 계획의 해석 |
|---|----------|--------------|
| ㄱ | 채팅 확인 칩 | 채팅 화면에서 발화를 보내 `POST /chat` 응답에 `pending_question` 이 오면, 그 `options` 문자열이 **그대로** 칩으로 뜨고, 칩을 누르면 `POST /answers/{question_id}` 로 그 문자열이 답으로 가서 재개된 턴의 `reply` 가 보인다. 재개 중 새 질문이 나면 새 칩이 뜬다. 앱을 다시 열어도 미답변·미만료 질문은 칩으로 복원된다(S3.4 "프론트 확인 칩 = 미답변 pending_questions"). 칩이 떠 있어도 새 발화를 보낼 수 있다(S3.4 "새 발화 우선") |
| ㄴ | 카드 원문 펼치기 | 인물 카드 화면의 타임라인 항목을 펼치면 그 이벤트의 `events.raw_utterance` 가 **저장된 글자 그대로** 보인다(부록 A "타임라인 항목을 펼치면 원문 발화가 나옵니다"). 사실·패턴은 "근거 보기" 로 `fact_sources` 가 가리키는 원문을 보인다(S3.1 "fact_sources(fact_id, event_id) -- 시맨틱 사실 → 근거 원문"). 원문은 펼칠 때만 읽고, 목록·카드 응답에는 싣지 않는다(결정 F) |
| ㄷ | 브리핑 화면 | 브리핑 화면이 수동 실행(`POST /briefings/run`)과 1분 주기 작업이 만든 브리핑을 **둘 다** 보여 준다(결정 G). 각 브리핑은 일정 머리줄·패턴 문장·요약 줄·한 줄 제안을 서버 문자열 그대로 보여 주고, 화면에서 그 일정의 수동 브리핑을 다시 돌릴 수 있다(데모 "발표자 수동 트리거 버튼"). 데스크톱 알림을 누르면 이 화면의 그 일정으로 열린다(P7 인계) |
| (틀) | 프론트 3화면 + PWA | 라우트는 정확히 3개(`#/chat`·`#/persons`·`#/briefings`)이고, 그 밖의 화면 경로가 없다(원칙5). PWA 는 manifest + 범위 `/` 서비스 워커(푸시·알림 클릭)까지 |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

**순서(결정 J 확정): 자동 판정 1~28행이 전부 통과해야 사람 점검 29~32행을 시작한다.** "1~28행" 은 번호 사이에 끼운 17b·27b 를 포함해 **자동 30행**이고, 사람 점검은 **4행**(29~32)이다. 1~11행은 `POSTGRES_PORT=5433 .venv/bin/python -m pytest <파일>::<테스트> -v`, 12~23행은 `web/` 에서 Vitest, 24~26행은 Playwright E2E(`npm run e2e` — `vite preview` 빌드에 `page.route` 가짜 API, 실제 Chromium), 27행은 불변식 grep, 27b행은 실 네트워크 0(Vitest 1건 + Playwright 요청 URL 단언, R-5), 28행은 회귀·CI. 테스트 이름은 U 단위에서 확정하되 아래 뜻을 바꾸지 않는다. 백엔드 행은 **독립**(행마다 새 사용자·인물·이벤트·일정·질문을 만든다). 프론트 행은 `fetch`·`navigator.serviceWorker`·`PushManager`·`Notification` 을 가짜로 바꿔 끼우고, 가짜 표에 없는 요청은 실패시킨다(실제 네트워크 0).

### 자동 판정 (실제 LLM·실제 푸시 없음)

| # | 확인할 것 | 케이스 | 기대 출력 | 위치 |
|---|----------|-------|----------|------|
| 1 | ㄴ 인물 목록 | 사용자 A 인물 2·사용자 B 인물 1, `APP_USER_ID=A` 로 `GET /persons` | 200, 2건만, 각 `{id, display_name, relation_tag, hierarchy, last_contact_at}`, 이벤트 없는 인물 `last_contact_at == null`·뒤쪽 | test_api_read_persons |
| 2 | ㄴ 카드 모양 | 인물 1·별칭 2·사실 2·`pattern:` 사실 1·이벤트 3·`fact_sources` 2·미래 일정 1·과거 일정 1 | `facts` 2(패턴 제외, `source_count` 맞음)·`patterns` 1·`timeline` 3(최근 순)·`upcoming_schedules` 1(과거 제외)·`last_contact_at` = 최신 `occurred_at` | 〃 |
| 3 | ㄴ 카드 소유 | 다른 사용자 인물 id / 없는 id | 둘 다 404 `{"detail":{"code":"not_found"}}` | 〃 |
| 4 | ㄴ 목록·카드에 원문 없음 | 이벤트 `raw_utterance` 에 감시 문자열을 넣고 1·2행 요청 | 응답 JSON 에 감시 문자열 0회, 키 `raw_utterance` 0회 | 〃 |
| 5 | ㄴ 이벤트 원문 | `GET /events/{id}/raw`(원문에 공백·이모지·줄바꿈) / 다른 사용자 이벤트 / 없는 id | 200 `raw_utterance` 가 DB 값과 바이트 일치 / 404 / 404 | test_api_read_raw |
| 6 | ㄴ 사실 근거 원문 | 사실 1 에 `fact_sources` 2 / 다른 인물의 `fact_id` 를 내 `person_id` 로 / 다른 사용자 인물 | `sources` 2건·원문 바이트 일치·최근 순 / 404 / 404 | 〃 |
| 7 | 조회는 쓰지 않는다 | 1·2·5·6·8·9행 요청 전후 `agent_traces` 행 수·`schedules.briefed_at`·`persons.updated_at` | 전부 변화 0 | test_api_read_raw (공통 픽스처) |
| 8 | ㄱ 대기 질문 목록 | 세션 S 에 미답변 1·답변됨 1·만료(25h 전) 1, 세션 T 에 미답변 1, 헤더 `X-Session-Id: S` / 헤더 없음 / 형식 위반 | S 의 미답변 1건만 / `[]` + **DB 쓰기 0**(요청 전후 `pending_questions`·`agent_traces` 행 수 변화 0 — 서버가 발급한 uuid 세션이 어디에도 저장되지 않음, R-11) / 422 | test_api_questions_pending |
| 9 | ㄷ 브리핑 조회 — 두 경로 | 일정 1 은 `POST /briefings/run`, 일정 2 는 `run_briefings(trigger="scheduler")`, `FakeBriefingComposer` | 2건, 각 `lines`·`suggestion`·`pattern_sentences` 가 그 실행의 `briefing_compose.output` 과 같음, `schedule.title`·`person.display_name` 채워짐 | test_api_read_briefings |
| 10 | ㄷ 재실행·사용자 범위·원문·다른 step 혼입 | 일정 1 지정 실행 2회(생성기 응답 다르게) / 사용자 B 브리핑 trace 1 / 원문 감시 문자열 / 일정 1 의 `briefing_compose` 보다 **나중**에 같은 `tool_name='briefing'` 의 `briefing_run`·`briefing_error` 행을 `output` 에 같은 `schedule_id`·`person_id` 를 넣어 추가, 일정 3 은 `briefing_error` 행만 | 1건·두 번째 내용 / 내 것만 / 감시 문자열 0회 / 일정 1 은 여전히 `briefing_compose` 내용, 일정 3 은 목록에 없음(R-9) | 〃 |
| 11 | 무변경 | `alembic check` · `python scripts/tools_check.py` · `git diff --stat 50fd7fc -- app alembic ':!app/api/routes.py' ':!app/api/schemas.py' ':!app/api/read.py'`(산출물 표가 `app/` 변경을 이 세 파일로 한정 — `app/main.py`·`app/settings.py`·`app/api/deps.py` 포함 그 밖은 0, R-6) | "No new upgrade operations detected." · "RESULT: 7/7 ok" · 빈 출력 | U9 evidence |
| 12 | 빌드·타입 | `cd web && npm ci && npm run typecheck && npm run build` | 종료 코드 0, 타입 오류 0, `web/dist/index.html`·`web/dist/sw.js`·`web/dist/manifest.webmanifest` 존재 | U9 evidence |
| 13 | (틀) 화면 3개 | `routes.test.ts` — 라우트 표 | 경로 키가 정확히 `chat`·`persons`·`briefings` 3개, 알 수 없는 해시는 `#/chat` | routes.test |
| 14 | ㄱ 전송·세션 | 첫 전송(헤더 없음) → 응답 `session_id: "s-1"` → 두 번째 전송 | 첫 요청에 `X-Session-Id` 없음, 두 번째 `X-Session-Id: s-1`, `localStorage` 에 `s-1` | chat.test |
| 15 | ㄱ 칩 왕복 | 응답 `pending_question{question_id:7, options:["직장","친구","아니요"]}` → "친구" 클릭 → 응답에 새 `pending_question{question_id:8,…}` | 칩 3개가 질문을 낸 응답 바로 아래에 글자·순서 그대로, `POST /api/answers/7` 본문 `{"answer":"친구"}` 1회, "친구" 칩은 선택 상태(`aria-pressed=true`)로 남고 나머지 둘은 비활성·다시 눌러도 요청 0, 재개 `reply` 와 8 의 칩이 그 아래에 이어 붙음 | 〃 |
| 16 | ㄱ 복원·새 발화 우선 | 진입 시 `GET /api/questions/pending` 1건 / 칩이 떠 있는 상태에서 새 발화 | 칩 1개 복원 / 입력창 활성·`POST /api/chat` 1회·기존 칩 유지 | 〃 |
| 17 | ㄱ 오류 | 칩 클릭 → 409 `{"code":"expired"}` / `POST /api/chat` 500 / P5 오류 규약 응답(200·`stored` 0·`pending_question` null) | 그 질문의 칩 전부 비활성 + 안내 1줄 / 타이핑 점 사라지고 안내 1줄·입력 유지 / 서버 `reply` 그대로(프론트가 문장을 지어내지 않음) | 〃 |
| 17b | ㄱ 챗봇형 입력·스크롤 | 입력창에 Shift+Enter 로 3줄 → Enter / 응답 대기 / 응답 도착(맨 아래에 있을 때·위로 올려 둔 때) | 줄바꿈 3줄 유지 후 전송 1회·입력창 비워짐 / 타이핑 점 표시 / 맨 아래로 스크롤 · 스크롤 위치 유지 + "새 메시지" 표시 | 〃 |
| 18 | ㄴ 원문 펼치기 | 타임라인 2건 → 첫 항목 펼치기 → 접기 → 다시 펼치기 | `GET /api/events/{첫 id}/raw` **1회만**, 원문이 응답 문자열 그대로, 접으면 숨김 | card.test |
| 19 | ㄴ 근거 보기·항목·필터 없음 | 2행 모양 응답 + 사실 "근거 보기" 클릭 | 알고 있는 것 2·반복 패턴 1·타임라인 3·다가오는 일정 1 렌더, `GET /api/persons/{id}/facts/{fact_id}/sources` 1회·원문 2건 표시, 목록 화면에 필터 컨트롤 0 | 〃 |
| 20 | ㄷ 브리핑 렌더 | `GET /api/briefings` 2건(하나는 `suggestion: null`) / 0건 | 머리줄·패턴 문장·요약 줄·제안이 응답 문자열 그대로, `null` 이면 제안 칸 없음 / 빈 상태 문구 | briefing.test |
| 21 | ㄷ 수동 브리핑·잠금 404 | "지금 브리핑" 클릭 → 200 / → 404 `not_found` | 본문 `{"schedule_id":N}` 뒤 `GET /api/briefings` 재호출 / 안내 1줄, 목록 유지 | 〃 |
| 22 | ㄷ 알림 → 브리핑 화면 | `sw.test.ts` — 가짜 `self`: `push`(P7 페이로드 모양) / `notificationclick`(창 있음·없음) | `showNotification(title,{body,tag,data:{schedule_id}})` 1회 + 열린 창 `postMessage` / 창 있음: `focus`+이동 `…#/briefings?schedule_id=N`, 없음: `openWindow(…#/briefings?schedule_id=N)` | sw.test |
| 23 | ㄷ 푸시 구독 버튼 | 가짜 `PushManager` — 공개키 200 / 404 `push_not_configured` | `POST /api/push/subscriptions` 본문 = 가짜 구독 `toJSON()` / 안내 1줄·구독 호출 0 | push.test |
| 24 | ㄱ E2E 채팅 칩 | Playwright, 가짜 API: 발화 → 칩 → 클릭 → 재개 응답 → 새로고침 | 칩 표시·클릭 후 `reply`, 새로고침 뒤 `GET /api/questions/pending` 으로 복원 | e2e/chat.spec |
| 25 | ㄴ E2E 카드 원문·사이드바 | 데스크톱 폭(1280px): 사이드바 인물 목록에서 인물 클릭 → 타임라인 펼치기 / 모바일 폭(390px): 메뉴 버튼 → 서랍에서 "인물" → 인물 → 카드 | 데스크톱: 본문에 그 인물 카드·원문 표시, 사이드바 3개 항목으로 화면 3개 전환 모두 동작 / 모바일: 처음엔 서랍 닫힘·하단 탭바 없음, 메뉴 버튼으로 열림, 항목을 고르면 서랍 닫히고 그 화면 표시, 라우트는 3경로 그대로 | e2e/card.spec |
| 26 | ㄷ E2E 브리핑 | `#/briefings?schedule_id=N` 직접 열기 → "지금 브리핑" | 그 일정 맨 위·강조, 실행 후 목록 갱신 | e2e/briefing.spec |
| 27 | 불변식 grep | "지킬 불변식" 절 명령 그대로(1~10) | 절에 적은 기대값 | U9 evidence |
| 27b | 실 네트워크 0(R-5) | Vitest — setup 의 가짜 `fetch` 에 표에 없는 URL(`fetch('https://example.invalid')`) / Playwright — 각 spec(24~26행)에서 `page.on('request')` 로 모은 요청 URL 전부 | reject(가짜 표 밖 요청은 실패) / 전부 preview 호스트의 앱 파일 또는 `/api/` 경로, 그 밖 0건 | network.test · e2e/*.spec |
| 28 | 전체 회귀·CI | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs` · `npm test -- --run` · `npm run e2e` · CI run(메인 세션 `gh run view <id>`) | pytest skip 0·passed ≥ 1882(P7 완료 시점)+U1~U3 신규 · vitest·e2e 실패 0 · CI 기존 job + 프론트 job 전부 success | U9 evidence |

### 사람 점검 (자동 판정 통과 뒤 — 화면을 보고 확인하는 체크리스트)

| # | 확인할 것 | 체크리스트 | 증거 파일이 갖출 항목(전부 있어야 통과) | 위치 |
|---|----------|-----------|--------------------------------------|------|
| 29 | **ㄱ 실서버 채팅 확인 칩** | 절차 ①~⑤ | ① 서버·프론트 기동 명령과 주소(키 값 없음) ② 보낸 발화 원문 ③ `pending_questions` 최근 행의 `id`·`kind`·`options`(DB 조회 출력) ④ 칩을 누른 뒤 그 행 `answer`·`answered_at`(DB 조회 출력) ⑤ 사용자 확인 문장(무엇이 보였는지·누른 칩·Chrome 버전) | U10 evidence |
| 30 | **ㄴ 카드 원문 펼치기** | ⑥~⑧ | ⑥ 카드에 보인 인물 id·펼친 타임라인 항목 id·펼친 사실 id ⑦ 그 이벤트 `raw_utterance` DB 조회 출력 ⑧ 사용자 확인 문장(펼친 원문이 ⑦ 과 같았는지) | U10 evidence |
| 31 | **ㄷ 브리핑 화면·알림 클릭** | ⑨~⑫ | ⑨ 브리핑의 `briefing_compose` trace id ⑩ 화면 머리줄·제안이 그 trace `output` 과 같다는 대조 ⑪ (VAPID 설정 시) 제품 화면 "알림 받기" 로 만든 구독 행(엔드포인트 **호스트만**)·`push "sent"` ⑫ 사용자 확인 문장(알림을 눌러 그 일정이 열렸는지). VAPID 미설정이면 ⑪ 대신 안내 1줄을 본 사실을 ⑫ 에 적고, 알림 클릭은 22행 자동 테스트로만 닫혔다는 한계를 04-review 에 적는다 | U10 evidence |
| 32 | **화면 점검(결정 L·N — 챗봇형 UI 요건 포함)** | 아래 "화면 점검 체크리스트" 20항(1~10 공통 · 11~20 챗봇형 UI 요건 — 19·20 은 결정 N 사이드바) | 항목마다 통과/수정 필요 표기 + 사용자 한 줄 의견, 데스크톱 폭·모바일 폭(개발자 도구 기기 모드) 각 1회, 밝은/어두운 각 1회. "수정 필요" 는 **한 번만** 반영하고 다시 점검(결정 L 시간 상한). 증거 파일에 **"수정 반영 횟수: n"** 줄을 명시하고 04-review 가 n ≤ 1 을 확인한다 — 넘으면 리스크 7 대로 CR 여부를 사용자에게 묻는다(R-10) | U10 evidence |

### 사람 점검 절차 (사용자·메인 세션, 에이전트는 실 LLM·실발송하지 않는다)

1. 사용자가 `.env` 에 LLM·임베딩 키(필요하면 P7 의 VAPID 세 이름)를 넣는다. 에이전트·메인 세션은 `.env` 를 읽지 않는다(security §1).
2. 메인 세션: 백엔드 `uvicorn` 기동(포트는 `docs/RUNNING.md` 대로), `cd web && npm run dev`. 기동 명령과 주소만 증거에 남긴다(①).
3. 사용자: 데스크톱 Chrome 으로 프론트 주소를 열고 채팅에 새 인물이 나오는 발화를 보낸다(②). 칩이 뜨면 하나를 누른다.
4. 메인 세션: `pending_questions` 최근 행을 조회해 남긴다(③④). 사용자 문장을 그대로 붙인다(⑤).
5. 사용자: 사이드바 인물 목록에서 그 인물 카드를 열고 타임라인 항목과 사실 "근거 보기" 를 펼친다. 메인 세션이 그 이벤트 행의 `raw_utterance` 를 조회해 남기고(⑥⑦), 사용자 문장을 붙인다(⑧).
6. 사용자: 그 인물과 24시간 안의 일정이 생기는 발화를 보낸다(기존 개발 DB 확인 행은 다른 사용자·과거일 수 있어 새로 만든다). 사이드바 "브리핑" 항목에서 "지금 브리핑" 을 누르거나 주기 작업 스위치를 켠다. 메인 세션이 `briefing_compose` trace 를 조회해 화면과 대조한다(⑨⑩).
7. (VAPID 설정 시) 사용자: "알림 받기" → 권한 허용. 메인 세션이 구독 행(호스트만)을 남기고 수동 브리핑을 한 번 더 실행해 `push` 값을 남긴다(⑪). 사용자가 알림을 눌러 그 일정이 열리는지 확인하고 문장을 준다(⑫).
8. 사용자: "화면 점검 체크리스트" 를 데스크톱·모바일 폭, 밝은·어두운 모드로 본다(32행).
9. 남은 확인 행은 지우지 않는다(원칙8, P7 관례 — 개발 DB `relationship`).

### 화면 점검 체크리스트 (32행)

1. 세 화면 모두 같은 앱 틀(결정 N — 모든 폭 왼쪽 사이드바: 데스크톱은 항상 보임 / 모바일은 메뉴 버튼으로 여닫는 서랍형 사이드바)이고, 사이드바에 지금 화면이 표시된다. 하단 탭바가 없다.
2. 본문 글자가 읽기 편한 크기(본문 16px 안팎)이고 줄 폭이 너무 넓지 않다(본문 최대 폭 안).
3. 여백이 일정하다(카드·목록 사이 간격이 화면마다 들쭉날쭉하지 않다).
4. 확인 칩이 그 질문을 낸 에이전트 응답 바로 아래 버튼 한 줄로 보이고, 누른 칩이 선택 상태로 남는다(나머지 비활성).
5. 카드의 섹션(알고 있는 것·반복 패턴·타임라인·다가오는 일정)이 제목으로 구분되고, 펼치기/접기 표시가 보인다.
6. 브리핑의 제안 한 줄이 요약 줄과 시각적으로 구분된다.
7. 로딩 중(스켈레톤)·빈 상태·오류 안내가 각 화면에서 빈 화면으로 남지 않는다.
8. OS 가 어두운 모드면 앱도 어둡고, 글자 대비가 충분해 보인다.
9. 키보드 Tab 으로 칩·버튼에 이동할 때 포커스 테두리가 보인다.
10. 모바일 폭(390px 안팎)에서 가로 스크롤이 생기지 않는다(칩 줄의 가로 스크롤은 예외).

챗봇형 UI 요건(결정 L 사용자 방향 — 비슷한 사용 경험인지 본다):

11. 대화 영역이 헤더(모바일은 메뉴 버튼 줄)를 뺀 화면 높이를 꽉 채운다.
12. 입력창이 하단에 고정돼 있고, 여러 줄을 쓰면 높이가 늘어나며(상한 뒤 내부 스크롤), Enter 전송·Shift+Enter 줄바꿈·전송 버튼이 동작한다. 모바일에서 키보드가 올라와도 입력창이 가려지지 않는다.
13. 사용자 발화는 오른쪽 말풍선, 에이전트 응답은 왼쪽(본문형 또는 말풍선 — 결정 L)으로 구분된다.
14. 응답을 기다리는 동안 타이핑 점이 보이고, 응답이 오면 사라진다.
15. 새 메시지가 오면 맨 아래로 자동 스크롤된다. 위로 올려 읽는 중에는 끌려 내려가지 않고 "새 메시지" 표시만 뜬다.
16. 인물 카드·브리핑 화면이 채팅과 같은 디자인 언어(글꼴·색·여백·모서리)로 보인다.
17. 특정 회사 로고·상표·고유 그림이 쓰이지 않았다.
18. 상담 페르소나 이름·말투 설정·음성 입력 버튼·"무엇이든 물어보세요" 류 문구가 없다(원칙7 경계 문장).
19. (결정 N) 모바일 폭에서 왼쪽 위 메뉴 버튼으로 서랍형 사이드바가 열리고, 항목(채팅·인물·브리핑 또는 인물 이름)을 고르면 서랍이 닫히며 그 화면이 보인다. 하단 탭바가 없다.
20. (결정 N) 데스크톱 폭에서 사이드바가 항상 보이고, 사이드바 인물 목록에서 인물을 누르면 본문에 그 인물 카드가 열린다.

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 경로 | registry 근거 | 이 패키지에서 |
|---------|------|--------------|-------------|
| `POST /chat`·`POST /answers/{id}` | `app/api/routes.py` | 65·167행 | 그대로 호출만. 계약 변경 없음 |
| `list_pending(ctx, session_id)` | `app/tools/questions.py` | 60행 비고·코드 287행 | `GET /questions/pending` 이 그대로 부른다 |
| `_owned_person`·`_person_out` | `app/tools/persons.py` | 58행 | 카드·원문 조회의 소유 확인·별칭 정렬에 재사용 후보(밑줄 이름이라 공개 승격이 필요하면 U1 03-log 에 이유, P3-baselines 결정 J 선례) |
| `POST /briefings/run` | `app/api/routes.py` | 65행 비고(P6-briefing U6) | "지금 브리핑" 버튼이 그대로 호출 |
| `briefing_compose` trace 모양 | `app/briefing/run.py` | 195행 | `GET /briefings` 의 원천(P6 결정 I 필드) |
| `GET /push/vapid-public-key`·`POST /push/subscriptions` | `app/api/routes.py` | 208행 | "알림 받기" 버튼이 그대로 호출 |
| 확인 페이지 서비스 워커 | `app/push/devpage/sw.js` | 201행 | 페이로드 해석만 복사. 원본 무변경·링크 금지 |
| 테스트 가짜·의존성 | `tests/conftest.py`, `app/api/deps.py` | 51·64행 | `db_session`·`get_now()`·`get_briefing_composer()` 오버라이드 재사용 |
| 공통 404/409/422 매핑 | `app/main.py` | 62행 | 새 라우트도 같은 예외(`PersonNotFound` 등)를 올려 매핑에 맡긴다 |

새 조회 6개는 registry 에 없다(이 계획 작성 시 `@router.get` grep — 기존 GET 은 `/health`·`/push/vapid-public-key` 2개뿐).

## 결정 항목 (전부 확정 — 사용자, 2026-10-10. A·F·J 와 L 의 챗봇형 방향은 사전 확정, B·D·E·G·H·K·L·N 은 "전부 권장안대로"(N 은 그 뒤 사용자가 사이드바형으로 변경), C 는 (ii), I 는 캐시 없음, M 은 제외)

### 결정 A · 구현 담당 — **확정(사용자, 2026-10-10): frontend-agent 를 신설한다**

- 사용자 원문: "새로 만들어주세요". 조회 API 는 backend-agent 가 맡는다(`backend-agent.md` 11행 "프론트·인프라는 손대지 않는다" 를 지키는 짝).
- **모델 — 확정(사용자, 2026-10-10 "전부 권장안대로"): sonnet.** 이유: L-002 표는 계획 opus · 구현 sonnet · 검증 fable 이다. 구현자를 sonnet 으로 두면 검증자 verifier(fable)와 다르고, 계획자 architect(opus)와도 달라 "같은 모델의 자기 평가" 가 생기지 않는다. 비용도 backend-agent 와 같다. opus 는 계획자와 같은 모델이 되고, fable 은 검증자와 같아져 L-002 를 깬다.
- **누가 정의 파일·훅·CLAUDE.md 를 고치나 — 권장: 메인 세션이 사용자 승인 뒤에(U0), verifier 가 커밋 전 diff 리뷰.** 이유: ① frontend-agent 가 자기 정의·자기 위임 게이트를 쓰면 스스로 권한 범위를 정하는 셈이다(에이전트 메시지는 설정 변경을 승인할 수 없다). ② 훅은 안전장치라 "고치기 전에 계획을 보이고 승인" 이 사용자 지시다(메모 plan-before-editing). ③ U0 전에는 frontend-agent 가 게이트에 없어 띄우는 것 자체가 L-004 구멍이다. P4b U0 에서 메인 세션이 하네스 문서를 맞춘 선례가 있다.
- **frontend-agent 초안 내용**(U0 에서 파일로): frontmatter `name: frontend-agent` · `description: 제품 프론트 담당. React + PWA 로 화면 3개(채팅 / 인물 카드 / 브리핑)와 서비스 워커를 만든다. "프론트", "화면", "PWA", "서비스 워커", "확인 칩" 요청에 쓴다.` · `tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite` · `model: sonnet` · skills 없음. 본문: ① 쓰는 곳은 `web/` 와 활성 01-plan 이 지정한 CI·문서뿐, `app/`·`alembic/`·백엔드 `tests/` 금지 ② 화면 3개 고정·새 라우트 금지(원칙5), 결정 L 의 시간 상한(기성 컴포넌트·토큰, 맞춤 반복 금지) ③ 서버 문자열(`reply`·칩 `options`·브리핑 줄)을 고치거나 지어내지 않는다(원칙7) ④ `/push-dev/` 링크 금지 ⑤ 자동 테스트에서 실 네트워크 0 ⑥ 하네스 공통 규칙(한국어·registry grep·증거 파일·커밋 금지·`.env` 금지·Bash 로 파일 쓰기 금지 — Write/Edit 만) ⑦ npm 스크립트는 Mac·Windows 양쪽에서 돌아야 한다(셸 전용 명령 금지 — `rm -rf` 대신 도구 옵션이나 node 스크립트. `safety-guard.sh` 60행이 `rimraf` 도 막으므로 `rimraf` 도 쓰지 않는다 — R-8) ⑧ `npx` 로 내려받는 도구는 `npx shadcn@<버전>` 처럼 버전을 고정한다(security §3 취지 — R-8).

### 결정 B · 빌드 도구·언어·위치·CI — **확정(사용자, 2026-10-10): Vite + React + TypeScript, `web/`, CI 두 OS·E2E ubuntu**

- 빌드: (i) **Vite + React** · (ii) Create React App(유지보수 중단) · (iii) 번들러 없이 ES 모듈. 권장 (i) — 개발 서버 프록시 내장(결정 C), `vite build` 산출물이 S3 에 그대로 올라간다.
- 언어: (i) **TypeScript** · (ii) JavaScript. 권장 (i) — P5·P6·P7 응답 모양을 타입으로 옮기면 `npm run typecheck` 가 계약 어긋남을 잡는다.
- 위치: (i) **`web/`** · (ii) `frontend/`. 권장 (i). 규칙 6(FIX 커밋 verifier 게이트 — 경로 판정은 `.claude/scripts/fix_guard_check.py` 180행, `commit-guard.sh` 는 호출부)은 지금 `app/`·`alembic/` 만 보므로 U0 에서 `web/` 까지 넓힌다(사용자 확정 — 리스크 2).
- CI: (i) **프론트 job: 타입·Vitest·빌드는 ubuntu·windows 두 OS, Playwright E2E 는 ubuntu 만** · (ii) 전부 ubuntu 만 · (iii) 전부 두 OS · (iv) CI 에 넣지 않음. 권장 (i) — 사용자 요구 "Mac·Windows 양쪽에서 동작" 의 연장으로 npm 스크립트가 Windows 에서 깨지는지 바로 드러난다(FIX-022 windows job 선례). Playwright 브라우저 내려받기·실행 시간은 Windows 에서 크고, E2E 가 보는 것은 브라우저 동작이라 OS 차이가 작다.

### 결정 C · 서빙·출처 — **확정(사용자, 2026-10-10): (ii) 같은 출처 + `/api` 접두를 프록시가 벗긴다** (방안 비교는 사용자 요청 "방안들을 제시해주세요")

공통 전제: 화면 라우팅은 **해시**(`/#/chat` 등)로 한다 — API `POST /chat` 과 화면 `/chat` 이 같은 출처에서 경로가 겹치는 것을 피하고, S3 에 "404 → index.html" 대체 규칙이 필요 없다. 아래 네 방안은 "프론트가 API 를 어떤 주소로 부르나" 의 차이다.

| | (i) 같은 출처 · API 경로 그대로 | (ii) 같은 출처 · `/api` 접두를 프록시가 벗긴다 | (iii) 별도 출처 + CORS | (iv) FastAPI 가 빌드 산출물도 서빙 |
|---|---|---|---|---|
| 개발 시 구성 | 브라우저 → Vite(5173) → 프록시가 `/chat`·`/answers`·`/persons`·`/events`·`/questions`·`/briefings`·`/push` 7개 접두를 → uvicorn(8000) | 브라우저 → Vite(5173) → `/api/*` 한 규칙만 → 접두를 벗겨 uvicorn(8000) | 브라우저 → Vite(5173) 화면 / 브라우저 → uvicorn(8000) API 직접 | `vite build --watch` → `web/dist` 를 uvicorn(8000)이 정적 서빙(또는 개발만 (ii) 와 병행) |
| 운영 시 구성 | CloudFront: 기본 → S3, 경로 동작 7개 → EC2 오리진(Caddy → uvicorn) | CloudFront: 기본 → S3, `/api/*` 동작 1개 → EC2(Caddy `handle_path /api/*` 로 접두 제거 → uvicorn) | CloudFront → S3(화면), `api.도메인` → EC2(Caddy 자체 인증서) | CloudFront → EC2 전체(Caddy → uvicorn), S3 미사용 |
| CORS | 불필요 | 불필요 | **필요**(`app/main.py` 에 CORS 미들웨어·허용 출처 설정, 사전 요청) | 불필요 |
| 백엔드 변경 | 없음 | 없음 | CORS 미들웨어 + 허용 출처 환경변수 | 정적 서빙 라우트(P7 확인 페이지처럼) |
| P9-infra 연결(S3+CloudFront, D7 Caddy) | 기술 스택·D7 그대로. 경로 동작 7개 — **새 API 접두가 생길 때마다 CloudFront 도 고쳐야 한다** | 기술 스택·D7 그대로. 동작 1개 + Caddy 한 줄. 새 API 가 늘어도 인프라 무변경 | 화면은 스택 그대로, API 는 도메인·인증서가 하나 더(Caddy 가 Let's Encrypt 로 처리 가능). D7 의 "CloudFront 오리진 HTTPS" 구조와 달라진다 | CLAUDE.md 기술 스택 "React + PWA (S3 + CloudFront)"·기획서 6장 "CloudFront ──> S3" 와 다르다 → D 카드 변경 또는 CR |
| 서비스 워커·푸시 | 같은 출처라 단순 | 같은 출처라 단순 | 서비스 워커는 화면 출처, 구독 등록 API 는 다른 출처 — 동작은 하지만 CORS 대상 | 같은 출처 |
| Mac/Windows 개발 편의 | 터미널 2개(`uvicorn`·`npm run dev`), 차이 없음 | 같음 | 같음 + 허용 출처 값을 OS 별 `.env` 에 맞춰야 함 | 터미널 1개처럼 쓰지만 `--watch` 재빌드가 느리고 HMR 없음 |
| 기존 계약·문서 영향 | 없음 | 프론트 코드만 `/api` 를 붙인다. `curl` 예·P7 확인 페이지·테스트는 그대로 | 없음(백엔드에 미들웨어 추가) | 없음 |
| 단점 | 접두 목록이 프록시·CloudFront 두 곳에 중복 | "프론트가 부르는 주소 ≠ 백엔드 실제 경로" 라 로그를 볼 때 `/api` 를 머릿속으로 빼야 한다 | 운영 설정 실수(허용 출처)가 곧 장애, 사전 요청 지연 | 기획서 구조 변경 |

- **확정: (ii).** 사용자는 기획서 구조를 빼고 봐도 (ii) 가 낫다는 설명 — 업계 표준 모양, 배포 방식이 바뀌어도 코드 무변경, CORS 없음 — 을 듣고 골랐다. **운영에서 정적 파일을 S3+CloudFront(기획서·기술 스택)로 낼지 EC2 Caddy 가 `web/dist` 를 직접 낼지는 P9-infra 에서 정한다 — (ii) 는 프론트가 `/api` 만 부르므로 어느 쪽이든 프론트·백엔드 코드 무변경.** 이유(기록): CORS 코드가 없고 백엔드·기존 계약을 건드리지 않으며(11행 무변경 유지), 운영에서 CloudFront 경로 동작이 1개로 고정돼 이후 API 가 늘어도 P9 설정이 바뀌지 않는다. D7(Caddy)과 기술 스택(S3 + CloudFront)을 그대로 따른다. 이 패키지는 `vite.config.ts` 프록시 규칙과 `docs/RUNNING.md` 에 "운영 규칙: CloudFront `/api/*` → EC2, Caddy `handle_path /api/*`" 를 적어 P9 가 옮겨 쓰게 한다(배포 자체는 P9). Caddy `handle_path` 동작은 P9 에서 실제로 확인한다(이 계획은 Caddy 문서를 열지 않았다 — **확인 필요**).
- 택하지 않은 차선 (i): 접두가 7개로 고정이라면 충분하지만, P8 에서만 6개가 새로 생기는 것처럼 앞으로도 늘어날 수 있다.

### 결정 D · 세션·사용자 식별 — **확정(사용자, 2026-10-10): `localStorage` session_id, 인증 범위 밖**

- (i) **서버가 준 `session_id` 를 `localStorage` 에 보관·재전송** · (ii) 탭마다 새 세션(`sessionStorage`) · (iii) 프론트가 uuid 를 만들어 첫 요청부터 보냄. 권장 (i) — P5 결정 I "헤더 없으면 서버가 발급", 대기 질문이 세션에 묶여 있어 새로고침·재방문 뒤 칩 복원에 같은 세션이 필요하다.
- `APP_USER_ID` 는 서버 환경변수다. 프론트는 사용자 id 를 보내지도 알지도 않는다. **인증·로그인은 범위 밖**(단일 사용자 전제, F-fbaaae 는 P9-infra 전 과제) — RUNNING 에 "인증 없음, 로컬·데모 전용" 을 명시한다.

### 결정 E · 확인 칩 동작 — **확정(사용자, 2026-10-10): 입력 막지 않음 · 미답변 전부 · 409 안내**

- 표시: 칩 글자 = `options` 문자열 그대로(기획서 부록 A 의 "[네] [다른 사람이에요]" 같은 문구로 바꾸지 않는다 — 답은 `options` 안의 문자열이어야 `answer_question` 이 받는다).
- 대기 중 입력: (i) **막지 않는다** · (ii) 답할 때까지 잠금. 권장 (i) — S3.4 "답 없이 다음 발화가 오면 대기 질문 유지, 새 발화 우선".
- 여러 대기 질문: (i) **미답변 전부를 질문별로 쌓는다** · (ii) 최근 1개만. 권장 (i) — S3.4 "프론트 확인 칩 = 미답변 pending_questions"(복수).
- 409: `already_answered`·`expired` → 그 칩을 지우고 한 줄 안내. 재시도하지 않는다.

### 결정 F · 원문 펼치기 — **확정(사용자, 2026-10-10): 백엔드에 원문 조회 API 를 새로 만든다**

- 사용자 원문: "원문 펼치기를 새로 만들어주세요". 기존 API 로는 안 된다 — `get_briefing` 은 이벤트 5건 상한·`raw_utterance` 미포함(모듈 docstring "브리핑 자료 자체에 원문 전체를 싣지 않는다는 명시적 결정")·`@traced` 라 카드 조회에 쓸 수 없다.
- **엔드포인트 모양 — 권장: (i) 두 개.** `GET /events/{event_id}/raw`(타임라인 펼치기)와 `GET /persons/{person_id}/facts/{fact_id}/sources`(사실·패턴 "근거 보기" — `fact_sources` → `events.raw_utterance`). 대안 (ii) 카드 응답 타임라인에 원문을 함께 실음 — 요청은 줄지만 카드를 열 때마다 모든 원문이 오가고 "응답에 원문 필드 없음" 불변식(`schemas.py` docstring, P6·P7 판정)이 카드 응답에서 깨진다. 대안 (iii) 인물 단위로 원문 전부 `GET /persons/{id}/raw` — 펼치지 않은 원문까지 나간다. (i) 은 원문이 나가는 자리를 두 엔드포인트로 좁혀 판정 4~6행처럼 시험하기 쉽다.
- **사용자 격리**: 두 엔드포인트 모두 `persons.user_id = app_user_id()` 를 조인 조건에 건다. 두 번째는 `person_facts.person_id = :person_id` 와 `fact_sources.fact_id = :fact_id` 를 함께 걸어, 다른 인물의 사실 id 를 경로에 끼워도 404 다. 없는 것·남의 것은 같은 404(`app/main.py` 규약 "존재하지 않음과 다른 사용자 소유를 같은 404 로 다뤄 존재 여부를 숨긴다").
- **trace — 권장: 남기지 않는다.** 이유: 원칙9 는 "모든 **판정**에는 근거를 남긴다" 이고 조회는 판정이 아니다. `list_pending()` 도 같은 이유로 `@traced` 를 붙이지 않았다(코드 docstring "매 폴링/렌더링마다 `agent_traces` 행이 쌓이면 원칙9가 …"). 원문 열람 감사 기록이 필요하다면 다중 사용자 운영(범위 밖) 때의 일이다.
- **담당**: backend-agent 단위 U2 로 분리(U1 카드 조회와 별도 커밋 — 원문이 나가는 코드만 따로 리뷰받게).
- **S 카드 영향·CR 필요 여부 — 판단: CR 불필요, FIX 도 아님, 카드 보충은 선택.** 근거: ① 기획서가 이미 이 기능을 요구한다 — `docs/proposal.md` 119행 "원문은 보존해 근거 추적이 가능하다", 346행 "타임라인 항목을 펼치면 원문 발화가 나옵니다". ② S3.1 9행 "`fact_sources(fact_id, event_id)` -- 시맨틱 사실 → 근거 원문" 이 이 조인을 위한 테이블이다. ③ S3.2 는 **툴 7종**(LLM 이 부르는 것)의 시그니처이고 HTTP 조회 API 목록이 아니다 — 툴을 늘리지 않으므로 `tools_check` 7/7 유지. ④ S3.4 와는 겹치지 않는다(대기 질문 조회는 S3.4 "프론트 확인 칩 = 미답변 pending_questions" 를 구현할 뿐). ⑤ 선례: P7-push 가 `/push/*` 두 엔드포인트를 S3.6 "푸시 구독은 `push_subscriptions`" 아래에서 CR 없이 더했다. 기획서·D·S 문장을 바꾸지 않으므로 `/devlog change` 대상이 아니고, 기존 동작의 결함 수정이 아니므로 FIX 도 아니다. S3.1 카드 "적용" 줄에 "P8-frontend(조회)" 한 줄을 보충할지는 verifier 가 02-plan-verify 에서 판단한다. → verifier 는 선택 권고(R-7)로 냈고, **R-7 은 택하지 않음**(사용자 2026-10-10 — 권고 묶음에서 제외, S3.1 카드 무변경).

### 결정 G · 브리핑 화면의 데이터 원천 — **확정(사용자, 2026-10-10): `GET /briefings` — trace 최신 1행**

- (i) **`GET /briefings` — `briefing_compose` trace 에서 일정마다 최신 1행** · (ii) 화면은 `POST /briefings/run` 응답만 · (iii) 브리핑 저장 테이블 신설. 권장 (i).
  - 이유: P6 결정 H(i) "주기 작업이 만든 브리핑은 trace 가 유일한 저장소". (ii) 면 1분 주기 작업이 만든 브리핑과 알림을 눌러 들어온 경우 화면이 비어 수용 기준 ㄷ·P7 인계를 못 채운다. (iii) 은 스키마 v2 변경이라 CR 이 먼저다.
  - 주의: 관측 기록을 제품 조회에 쓰는 구조다. `agent_traces` 에 `user_id` 가 없어 `output.person_id → persons.user_id` 조인으로 범위를 건다(P6 R-6). trace 문자열은 `TRACE_MAX_STRING = 2000`(`app/tools/context.py` 86행)으로 잘리지만 줄·제안은 80자 상한이라 영향이 없다고 보며, U3 테스트로 확인한다.

### 결정 H · 푸시 구독 UI·알림 클릭·해제 — **확정(사용자, 2026-10-10): 브리핑 화면 "알림 받기" · 알림 클릭 → 그 일정 · 인앱 배너 · 구독 해제 없음**

- 구독 버튼 위치: (i) **브리핑 화면 상단 "알림 받기" 한 줄** · (ii) 채팅 화면 · (iii) 별도 설정 화면. 권장 (i). (iii) 은 4번째 화면이라 원칙5 위반.
- 알림 클릭: (i) **그 일정(`#/briefings?schedule_id=N`)으로, 열린 창이 있으면 그 창을 포커스** · (ii) 앱 첫 화면으로. 권장 (i) — P7 인계 문장 그대로.
- 인앱 배너(기획서 8장 "푸시 3중 안전장치" 두 번째): (i) **서비스 워커가 `push` 를 받으면 열린 창에 `postMessage` → 현재 화면 상단 한 줄(누르면 브리핑 화면)** · (ii) 만들지 않음. 권장 (i) — 서비스 워커 몇 줄이고 새 화면이 아니다.
- 구독 해제: (i) **만들지 않는다** · (ii) `DELETE /push/subscriptions` + 해제 버튼. 권장 (i) — 수용 기준 밖, P7 이 "구독 해제 API 는 없다" 로 넘겼다. 브라우저에서 알림을 끄면 다음 발송의 404/410 으로 P7 만료 정리가 행을 지운다.

### 결정 I · PWA 서비스 워커 캐시 범위·`/push-dev/sw.js` 와의 관계 — **확정(사용자, 2026-10-10): 캐시 없음**

- 캐시: **P8 에서는 캐시를 하지 않는다(푸시·알림 클릭·배너만). API 응답은 어떤 경우에도 캐시하지 않는다.** 결정 M(오프라인 제외)으로 앱 셸 캐시가 필요한 이유가 없어졌다. 택하지 않은 안: `vite-plugin-pwa`(Workbox 사전 캐시) — 쓸 곳이 없는 캐시 계층이 생긴다 / manifest 만(서비스 워커 없음) — 푸시를 받을 수 없다. API 응답(인물·원문)을 캐시하면 기기에 남는 개인정보가 늘고(기획서 9장 "제3자 개인정보 … 최소 수집") 서버와 어긋난 화면이 보인다.
- 설치 가능(홈 화면 추가)은 **수용 기준이 아니다**. Chrome 설치 조건이 `fetch` 리스너를 요구하는지는 **확인 필요**(U8 에서 개발자 도구 Application → Manifest 표시를 03-log 에 기록).
- `/push-dev/sw.js` 와의 관계: 제품 워커는 범위 `/`, 확인 페이지 워커는 범위 `/push-dev/`(더 구체적인 범위가 그 페이지를 맡는다). **서로 다른 등록이라 구독도 따로**다 — 개발 중 둘 다 구독하면 `push_subscriptions` 에 행이 둘, 알림이 두 번 올 수 있다(운영은 `PUSH_DEV_PAGE_ENABLED` 비움). 원본은 고치지 않고 페이로드 해석만 복사한다(차이는 03-log U8 에 diff 로).

### 결정 J · 테스트 방식 — **확정(사용자, 2026-10-10): 자동화 테스트를 먼저 돌리고, 그 뒤 사람이 점검한다**

- 사용자 원문: "테스트는 일단은 자동화하고 사람에게 점검받는 형식으로 할게요". 판정 표를 자동 1~28행(17b·27b 포함 30행) / 사람 29~32행(4행)으로 나눴고, U10 은 자동 30행 전부 통과 뒤에만 시작한다.
- **도구 — 권장: Vitest + Testing Library(컴포넌트) + Playwright(E2E, `page.route` 가짜 API, 실제 Chromium).** 대안: Vitest 만(E2E 없음) — 빠르지만 화면 전환·새로고침 복원·해시 이동 같은 실제 브라우저 동작이 사람 점검에 몰린다. 사용자가 "자동화" 를 먼저 원했으므로 E2E 를 포함한다.
- 자동 테스트의 실 네트워크 0: 프론트는 전역 `fetch` 를 "가짜 표에 없는 요청이면 실패" 로 바꿔 끼우고(P7 의 "`pywebpush.webpush` 가 불리면 실패" 와 같은 발상), Playwright 는 `page.route('**/api/**')` 로 전부 가로채고 가로채지 못한 요청은 실패시킨다. 이 규칙 자체를 판정 27b행이 시험한다(R-5). 백엔드는 기존 가짜(`FakeProposer`·`FakeJudge`·`FakeBriefingComposer`·`FakePushSender`). 실 LLM·실 푸시는 사람 점검에서만(P7 결정 G 와 같은 취지).

### 결정 K · 수동 브리핑 버튼의 잠금 404 (P6 §6-6) — **확정(사용자, 2026-10-10): 프론트 404 안내만, 백엔드는 FIX 후보**

- (i) **프론트에서 404 를 "잠시 뒤 다시 시도" 로 안내만** · (ii) 이 패키지에서 `select.py` 지정 모드를 `skip_locked=False` 로 · (iii) 별도 FIX 로 409. 권장 (i) — (ii) 는 P6-briefing 판정 근거 코드를 바꿔 11행 무변경을 깬다. 백엔드 수정은 FIX 후보((iii)).

### 결정 L · 화면 완성도 — **확정(사용자, 2026-10-10): (i) Tailwind + shadcn/ui, 사람 점검 뒤 수정 1회 상한, CR 불필요 해석 포함** (사용자 요청 "실리콘밸리 대기업 화면들처럼 초안으로" 와 원칙5 "UI에 시간을 쓰지 않는다")

- 긴장: 원칙5 는 "프론트 화면은 3개로 고정 … UI에 시간을 쓰지 않는다" 이고, 이 문장은 기획서 9장 리스크 표 "1인 개발 일정 초과 → 프론트 3화면 고정, … UI에 시간을 쓰지 않는다" 에서 왔다. 즉 **화면 수를 늘리지 않고 디자인 작업에 일정을 빼앗기지 않는 것**이 원래 뜻(일정 리스크 대응)이다. 사용자 요청은 "초안" 수준의 정돈된 모양이다.
- 선택지:
  - (i) **기성 컴포넌트·디자인 토큰으로 한 번에 — Tailwind CSS + shadcn/ui(Radix 기반, 코드를 저장소에 복사하는 방식) + lucide 아이콘.** 장점: 대형 제품들이 쓰는 정돈된 기본값(간격 척도·타이포 단계·포커스 링·어두운 모드 변수)을 설정 없이 얻고, 접근성(키보드·스크린리더 속성)은 Radix 가 기본 제공한다. 컴포넌트가 저장소 안 코드라 런타임 라이브러리 잠금이 없다. 단점: 초기화 명령(`npx shadcn …`)이 레지스트리에서 코드를 내려받는다(리스크 3), Tailwind 설정 파일이 늘어난다.
  - (ii) 완성형 컴포넌트 라이브러리(MUI·Chakra 등). 장점: 컴포넌트 수가 많다. 단점: 번들이 크고 "특정 라이브러리 느낌" 이 강하며 테마 조정에 시간이 든다.
  - (iii) 최소 CSS(기본 HTML 요소). 장점: 원칙5 문구에 가장 가깝다. 단점: 사용자 요청을 채우지 못한다.
  - (iv) 맞춤 디자인(시안 → 반복). 장점: 완성도. 단점: 원칙5 의 뜻(일정 리스크)과 정면으로 충돌 — 하려면 CR 로 원칙5 문구를 바꿔야 한다.
- **확정: (i), 시간 상한을 둔다.** 화면마다 한 번 구현 + 사람 점검(32행) 뒤 "수정 필요" 를 **한 번만** 반영. 맞춤 일러스트·브랜딩·애니메이션(기본 전환 외)·디자인 시안 여러 벌·시각 회귀 테스트는 하지 않는다.
- **CR 필요 여부 — 판단: (i) 이면 CR 불필요.** 근거: 화면 수(3개)는 그대로이고, 기성 부품으로 한 번에 만드는 것은 "UI에 시간을 쓰지 않는다" 의 뜻(디자인 작업으로 일정 초과 금지)을 지킨다. 원칙5 문구를 바꾸지 않는다. (iv) 를 고르면 CR 이 필요하다. 이 해석은 사용자가 확정했다(2026-10-10).
- **사용자 방향(확정, 2026-10-10)** — 사용자 원문: "인스타 디엠이나 ChatGPT, Gemini, Claude 같은 챗봇 UI를 원해". 특정 회사의 로고·상표·고유 디자인을 복제하지 않고 **비슷한 사용 경험**으로 만든다.
  - **채팅 화면 — 메신저·챗봇형 대화 UI**: 화면을 꽉 채우는 대화 영역(헤더·탭을 뺀 나머지 높이 전부), 하단 고정 입력창(여러 줄 자동 높이 — 상한 몇 줄 뒤 내부 스크롤, Enter 전송·Shift+Enter 줄바꿈, 전송 버튼, 전송 중 비활성), 사용자 말풍선은 오른쪽 · 에이전트 응답은 왼쪽 본문형(배경 없는 텍스트 — 권장. 말풍선형은 대안으로 토큰 한 줄 차이), 응답 대기 중 타이핑 점 3개, 새 메시지가 오면 맨 아래로 자동 스크롤(사용자가 위로 올려 읽는 중이면 "새 메시지" 버튼만 보이고 끌어내리지 않는다), 모바일 우선 반응형, 어두운 모드(OS 설정 따름).
  - **ask_user 확인 칩**: 그 질문을 낸 **에이전트 응답 바로 아래**에 버튼 칩 한 줄(넘치면 가로 스크롤 또는 줄바꿈 — 빠른 답장·추천 질문과 비슷한 형태). 칩을 누르면 `POST /answers/{question_id}` 를 부르고, **답한 칩은 선택 상태로 고정**(나머지 칩은 비활성 — 같은 질문에 두 번 답하지 않음), 재개 응답은 그 아래에 이어 붙는다. 앱을 다시 열어 복원한 대기 질문은 질문 문장을 에이전트 응답처럼 한 덩이로 보이고 그 아래 칩을 단다.
  - **인물 카드·브리핑**: 같은 디자인 언어(같은 토큰·글꼴·여백·카드 모양)를 쓴다. 화면 이동 방식은 결정 N(모든 폭 왼쪽 사이드바, 모바일 서랍형).
  - **원칙7 경계 문장**: 챗봇 UI 의 **형태**만 빌린다. 대화 **내용**은 기록 결과(서버 `reply`)·확인 칩·브리핑의 한 줄 제안으로 한정한다 — 상담 페르소나·말투 설정·감정 대화·음성 입력·"무엇이든 물어보세요" 식 자유 질의 안내 문구를 두지 않는다. 입력창 자리표시 문구도 "오늘 있었던 일을 적어 주세요" 처럼 기록을 안내한다.
  - 범위 한정: 위 형태를 기성 컴포넌트·토큰으로 **한 번에** 구현한다. 맞춤 애니메이션(타이핑 점·기본 전환 외)·픽셀 단위 반복 다듬기는 하지 않는다. 확인은 사람 점검 체크리스트 11~20항(챗봇형 UI 요건).
- **참고할 디자인 특성(범위 한정)**:
  - 레이아웃: 결정 N 확정 — 데스크톱(≥ 1024px) 항상 보이는 왼쪽 사이드바(위 3개 항목 + 아래 인물 목록) + 본문(채팅은 대화 열 최대 폭 약 720px 가운데) / 모바일·중간 폭(< 1024px) 한 열 본문 + 모바일 서랍형 사이드바(왼쪽 위 메뉴 버튼으로 열고 닫음, 항목을 고르면 닫힘). 하단 탭바 없음.
  - 여백: 4px 배수 척도(4·8·12·16·24·32)만 쓴다.
  - 타이포: 시스템 글꼴 묶음(`-apple-system`, `"Apple SD Gothic Neo"`, `"Malgun Gothic"`, `"Segoe UI"`, sans-serif) — 웹 글꼴을 내려받지 않는다(외부 요청을 만들지 않는다 — 불변식 9). 크기 단계 4개(제목·소제목·본문·보조).
  - 색: 중립 회색 단계 + 강조색 1개 + 경고색 1개(반복 패턴 표시). 토큰은 밝은/어두운 두 벌.
  - 어두운 모드: OS 설정(`prefers-color-scheme`)을 따른다. **전환 토글은 두지 않는다**(설정 화면·설정 저장이 생기지 않게).
  - 상태 표현: 로딩 스켈레톤·빈 상태 문구·오류 토스트 한 줄. 채팅은 말풍선 2색, 칩은 둥근 버튼, 카드 섹션은 제목 + 접기.
  - 접근성: Radix 기본 + 포커스 테두리 보이기 + 버튼에 이름. 대비 AA 를 목표로 하되 감사 도구 측정은 하지 않는다(사람 점검 8·9항으로 대신).

### 결정 N · 화면 이동 방식 — **확정(사용자, 2026-10-10): 모든 폭에서 ChatGPT 와 비슷한 왼쪽 사이드바** (화면 3개 안에서 이동만 — 새 화면 금지, 원칙5)

- 사용자 원문: "화면 이동은 ChatGPT처럼 왼쪽 사이드바로 해주세요". 앞 초안의 권장안 (i) 에서 "모바일 하단 탭바" 를 뺀 것이 확정안 (i') 이다. 특정 회사의 로고·상표·고유 디자인은 복제하지 않고 비슷한 사용 경험으로 만든다(결정 L).
- **확정 내용**:
  - 데스크톱(≥ 1024px): 사이드바가 **항상 보인다**. 위에 3개 항목(채팅·인물·브리핑), 아래에 인물 목록(`GET /persons` 결과 그대로). 인물을 누르면 본문에 그 인물 카드(`#/persons/:id`)가 열린다.
  - 모바일·중간 폭(< 1024px): 사이드바가 **기본으로 접혀 있고**, 왼쪽 위 메뉴 버튼(햄버거)으로 여는 **서랍(drawer)** 이다. 항목(3개 항목 또는 인물)을 고르면 서랍이 닫히고 그 화면이 보인다. 서랍 바깥을 누르거나 Esc 로도 닫힌다. **하단 탭바는 두지 않는다.**
  - 사이드바 열림/닫힘은 **화면이 아니라 레이아웃 상태**다. 새 라우트·새 화면이 아니므로 원칙5(화면 3개)와 판정 13행(라우트 3개)은 그대로다. 접힘 상태를 저장하는 설정 화면·설정 저장은 만들지 않는다(새로고침하면 폭에 따른 기본값).

| | **(i') 모든 폭 왼쪽 사이드바 — 모바일은 서랍형 (확정)** | (i) 모바일 하단 탭바 + 데스크톱 왼쪽 사이드바(앞 초안 권장안) | (ii) 채팅 전면 + 상단 아이콘 2개(카드·브리핑) | (iii) 상단 탭 3개(모든 폭 공통) |
|---|---|---|---|---|
| 모바일 | 메뉴 버튼 → 서랍형 사이드바(3개 항목 + 인물 목록), 고르면 닫힘 | 하단 탭바 3개(채팅·인물·브리핑). 인물 탭 = 목록 → 카드 | 채팅이 기본, 상단 아이콘으로 카드·브리핑 진입, 뒤로가기로 복귀 | 상단 탭 3개 |
| 데스크톱 | 항상 보이는 왼쪽 사이드바: 위 3개 항목, 아래 인물 목록. 인물을 누르면 본문에 카드 | 같음 | 같음(넓은 폭에서도 아이콘) | 상단 탭 3개, 인물 목록은 인물 탭 본문 |
| 장점 | 사용자가 고른 챗봇 앱 경험과 같고, 폭이 달라도 내비 구조가 하나(사이드바 내용 공유 — 표시 방식만 분기). 모바일 본문을 탭바 높이만큼 더 넓게 쓴다 | 엄지 닿는 하단 탭 | 채팅 몰입감 최대, 구현이 가장 작다 | 구현 단순 |
| 단점 | 모바일에서 화면 이동에 탭 한 번이 더 든다(메뉴 → 항목) | 폭에 따라 내비 구조가 둘, 사용자 요청과 다름 | 카드·브리핑이 숨겨져 데모에서 찾기 어렵다 | 챗봇형 경험과 거리가 있다 |
| 화면 수 | 3(사이드바·서랍은 레이아웃, 인물 목록은 인물 카드 화면의 목록을 옆에 띄운 것) | 3 | 3 | 3 |

- 이유(기록): 사용자 방향(챗봇형)과 같은 경험이고, 데스크톱에서 대화 중에도 인물 목록이 보여 데모 1~2단계(채팅 → 카드 채워짐)를 한 화면 폭에서 보여 줄 수 있다. 서랍은 shadcn/ui 의 Sheet(Radix Dialog 기반) 같은 기성 컴포넌트로 만든다(결정 L 시간 상한 — 맞춤 애니메이션 없음). 판정: 25행(E2E 사이드바·서랍) · 체크리스트 1·19·20항 · 불변식 10(라우트 밖 패널은 이 서랍 1개만, R-4).

### 결정 M · 오프라인 — **확정(사용자, 2026-10-10): 제외**

- **확정 내용: 제외** — 기획서 부록 A 385행 "안 되는 것: 오프라인 사용" 그대로. 사용자 답 "오프라인 빼기". 다시 넣으려면 `/devlog change` CR 이 필요하다. 이 패키지에는 오프라인 작업 단위·판정 행·예정 파일이 없고, 서비스 워커는 캐시를 하지 않는다(결정 I).
- 경과: 사용자 원문 "오프라인에서는 원본들을 저장하고 정리본을 서버에 저장할게요" → "오프라인은 첫 번째 해석이 맞아요". **해석은 첫 번째로 확인했으나 범위에서 제외**했다. 첫 번째 해석: 오프라인일 때 사용자가 입력한 원문 발화를 브라우저(IndexedDB)에 보관하고, 온라인이 되면 서버로 보내 지금처럼 에이전트 루프로 정리한 결과를 저장한다(서버의 `events.raw_utterance` 원문 보존은 그대로). 두 번째 해석(원문은 기기에만, 서버에는 정리본만)은 S3.1 `events.raw_utterance`·S3.2 `add_event(…, raw_utterance)`·기획서 116·119행 원문 보존·원칙9·결정 F 와 충돌해 택하지 않았다.
- **향후 CR 의 출발점(이 계획이 정리한 설계 요소 — 이 패키지에서 구현하지 않는다)**: ① 대기열 — IndexedDB `outbox`(`client_message_id`·원문·기기 시각·상태), 표시는 채팅 화면 안 한 줄. ② 중복 전송 방지 — `Idempotency-Key` 헤더 + 서버 멱등 키 테이블(예: `client_messages(user_id, client_message_id UNIQUE, …)`, S3.1 변경). 같은 발화가 두 번 처리되면 반복 패턴(원칙6)이 부풀려진다. ③ 발화 시각 — `ChatIn.said_at` 을 상대 시각 해석 기준으로(P5-loop·FIX-005 기준점 변경). ④ 순서 — 한 번에 하나, 실패 시 대기열 정지. ⑤ ask_user 상호작용 — 전송 중 `pending_question` 이 오면 대기열을 멈추고 칩을 보인다(원칙1, S3.4 "새 발화 우선" 과의 관계는 CR 에서 verifier 확인). ⑥ 앱 셸 캐시 — 결정 I 를 다시 연다(API 응답 캐시는 여전히 금지).

## 지킬 불변식 (수용 기준 밖)

U9 에서 아래 명령을 그대로 실행해 출력 전체를 증거로 남긴다(판정 표 27행).

1. `grep -rn "push-dev" web/src web/public web/index.html` → 0건(P7 결정 A 조건).
2. `grep -rnE "getUserMedia|SpeechRecognition|webkitSpeech" web/src web/public` → 0건(원칙7 음성 입력 제외).
3. `grep -rnE "addEventListener\(['\"]fetch|caches\." web/public/sw.js` → 0건(결정 I — 캐시 없음, 결정 M 오프라인 제외).
4. `grep -rn "raw_utterance" web/src` → 원문 조회 두 응답 타입과 원문 표시 컴포넌트 외 0건.
5. `grep -cE "@router\.(post|put|patch|delete)" app/api/routes.py` 가 `git show 50fd7fc:app/api/routes.py | grep -cE "@router\.(post|put|patch|delete)"` 와 같다(쓰기 라우트를 더하지 않는다 — U1~U10).
6. `git diff --stat 50fd7fc -- app/push/devpage` → 빈 출력.
7. `grep -rnE "VITE_[A-Z_]*(KEY|SECRET|TOKEN)" web/` → 0건(빌드에 비밀을 넣지 않는다 — VAPID 공개키도 `GET /api/push/vapid-public-key` 로 받는다).
8. `git ls-files web | grep -E "node_modules|dist/|test-results|playwright-report"` → 0건.
9. `grep -rnE "fonts\.googleapis|fonts\.gstatic|cdn\." web/src web/index.html` → 0건(결정 L — 외부 글꼴·CDN 요청 없음).
10. `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx | grep -v "^web/src/components/ui/"` → 결정 N 사이드바(서랍) 컴포넌트 **1파일뿐**(파일 이름은 U4 에서 정해 03-log 에 기록). 라우트 밖 패널은 그 서랍 1개만 허용한다 — 판정 13행(라우트 3개)이 못 잡는 "라우트 없는 네 번째 화면"(설정 패널 등)을 막는다(원칙5, R-4).

## 리스크 · 미결

- **1. 하네스 게이트 구멍(결정 A)** — U0 전에 frontend-agent 를 띄우면 `delegate-guard.sh` 가 이름을 몰라(`GATED="architect backend-agent eval-agent verifier"`) 승인 마커 없이 통과하고, `approve-commit.sh --stage frontend-agent` 는 usage 오류다. U0 커밋 전에는 frontend-agent 위임을 하지 않는다. U0 안에서도 ②·③ 을 ① 보다 먼저 적용하고 test-guards PASS 전에는 위임하지 않는다(R-3).
- **2. 규칙 6 의 범위 — U0 에서 해소(사용자 확정 2026-10-10 "web/ 까지 넓힌다")** — 지금은 FIX 커밋의 verifier 게이트가 `app/`·`alembic/` 만 본다. 판정 코드는 `.claude/scripts/fix_guard_check.py` 180행이고 `commit-guard.sh` 11·100행은 주석이다(R-1, `F-ce7d18` — 앞 초안이 셸 파일만 지목했던 오류). U0 ④ 가 `fix_guard_check.py` 에 `web/` 를 넣고 `test-guards.sh` 의 거부·허용 실제 시험으로 확인한다. U0 커밋 전에는 `web/` 에 FIX 커밋을 하지 않는다(어차피 U4 전에는 `web/` 가 없다). `stage-gate.sh` 는 면제 목록 방식이라 `web/` 가 이미 게이트 대상 — 수정 불필요(R-2, verifier 확인).
- **3. Node·npm·외부 내려받기 — 확인 결과 반영(R-8, verifier evidence `20261010-2314-verify-plan-verifier.txt`)** — Node: Mac 은 확인됨(`node v24.21.0`(nvm)·`npm 11.19.0`, 메인 세션 2026-10-10), Windows 는 CI windows job 으로 확인(로컬 Windows 는 미확인). `engines` 범위는 U4 에서 이 버전과 CI 버전을 함께 덮게 정한다. `npm install`·`npx shadcn`·`npx playwright install` 은 레지스트리·브라우저 바이너리를 내려받는 인바운드 통신이다. 확인된 것: (a) `safety-guard.sh` 에는 npm/npx/node 규칙이 **없다**(규칙 F 116·117행은 `curl|wget … | sh`·`iex` 만) — 단 57행 `rm -r`·60행 `rimraf` 는 scratchpad 밖에서 차단되므로 npm 스크립트에서 **`rimraf` 를 쓰지 않는다**(frontend-agent 초안 ⑦). (b) `.claude/settings.json` Bash `allow`(4~27행)에 npm/npx/node 가 **없어 매번 권한 프롬프트**가 뜬다. allow 에 추가할지는 `.claude/settings.json`(게이트 경로) 변경이라 **사용자 결정** — U0 diff 계획을 보일 때 함께 묻는다. (c) 내려받기 명령은 `npx shadcn@<버전>`·`npx playwright@<버전>` 으로 **버전을 고정**하고(security §3 "파일로 저장 → 내용 확인 → 실행" 취지), `package-lock.json` 을 커밋해 재현성을 둔다(U4). 결과는 U0·U4 03-log 에 기록한다.
- **4. `package-lock.json` 과 비밀 검사** — `.githooks/pre-commit` 35·38행 패턴(`sk-…{24,}`·`ghp_…{36}`)은 표준 base64 integrity 와 겹치지 않아 **오탐 가능성은 낮다**(verifier 확인, R-8). 0 은 아니므로 걸리면 우회하지 않고 메인 세션에 보고한다(security.md).
- **5. 운영 출처(P9 로 넘김)** — 결정 C(ii) 는 운영에서 `/api/*` → EC2 + Caddy 접두 제거로 성립한다. 정적 파일을 S3+CloudFront 로 낼지 EC2 Caddy 가 `web/dist` 를 직접 낼지는 P9-infra 에서 정한다(어느 쪽이든 프론트·백엔드 코드 무변경). Caddy `handle_path` 동작 확인은 P9. 서비스 워커·푸시는 HTTPS 가 필요하다(로컬 `localhost` 는 예외).
- **6. 브리핑 조회가 trace 에 기대는 구조(결정 G)** — P6 `briefing_compose.output` 키가 사실상 API 계약이 된다. U3 테스트가 그 키를 고정한다. 장기적으로 저장 테이블이 필요하면 CR.
- **7. 화면 완성도의 끝(결정 L)** — "실리콘밸리 대기업 화면처럼" 은 기준이 주관적이라 반복이 늘기 쉽다. 사람 점검 32행의 "수정 필요" 1회 반영 상한을 지키고(증거에 "수정 반영 횟수: n" — 04-review 가 n ≤ 1 확인, R-10), 넘으면 사용자에게 CR(원칙5) 여부를 묻는다.
- **8. 기획서 3.5 "판단 과정을 보여주는 화면"** — 화면 3개 고정과 문장상 긴장이 있다. 이 패키지는 다루지 않는다. P11-demo 전에 사용자가 정한다.
- **9. 실 LLM 응답 문장** — 29행은 실 LLM 판정에 따라 칩이 안 뜰 수도 있다. 안 뜨면 발화를 바꿔 다시 하되 시도마다 증거에 남긴다(원칙8).
- **10. 개발 DB 확인 행** — 기존 확인 행(P5 `judge-row7-*`, P6 `brief-u5-check`, P7 일정 id=5 등)이 사용자 `local` 화면에 섞여 보일 수 있다. 지우지 않는다(원칙8). 사람 점검은 새로 만든 행으로 판정한다.
- **11. 사람 점검이 있어야 닫힌다** — U10 은 사용자 시간이 필요하다. 그 전까지 "자동 판정 30행(1~28·17b·27b) 통과·사람 점검 대기" 상태로 04-review 에 올라갈 수 없다.
- **12. (범위 밖 — 하네스 FIX 후보, R-12)** `verify-plan.sh` 의 registry 중복 검사 출력이 `web/public/manifest.webmanifest` 를 `webma` 로 자른다(02-plan-verify 1절). 파일명 파싱 한계이고 판정에는 영향이 없다. 이 패키지에서 고치지 않고 메인 세션이 FIX 후보로 올릴지 정한다.

## 후행 패키지가 이 패키지에서 기대하는 것

- **P9-infra**: `web/dist` 경로·빌드 명령, 정적 파일 서빙 방식 결정(S3+CloudFront 또는 EC2 Caddy 가 `web/dist` 직접 — 결정 C), `/api/*` → EC2 + Caddy 접두 제거 규칙(결정 C), `/sw.js` 를 캐시하지 않는 헤더 권고, `PUSH_DEV_PAGE_ENABLED` 비움, HTTPS(D7), 인증 없음 전제(F-fbaaae).
- **P10-final-eval**: 화면·조회 API 는 trace 를 남기지 않으므로 평가 원천은 그대로.
- **P11-demo**: 데모 5단계와 화면 대응(1 채팅 칩 · 2 카드 · 3 채팅 일정 칩 · 4 채팅 identity 칩 · 5 브리핑 "지금 브리핑" 버튼 + 알림/인앱 배너).

## 읽은 카드

(이 계획을 쓰며 실제로 연 카드만. 전문을 읽었으면 어느 절인지)

- `CLAUDE.md`(세션 주입) — 불변 원칙 1·5·6·7·9, 데이터 모델, 기술 스택, 팀 구성 표·"frontend-agent 는 아직 만들지 않았다" 문장, 개발 프로세스
- `docs/wiki/INDEX.md` 전문 — 패키지 표 P8-frontend 행
- `docs/wiki/CURRENT.md` 전문 — `active: none`, P7-push 완료 메모
- `.claude/gitlog.md` 전문 — HEAD `50fd7fc`, 브랜치·미커밋 변경
- `docs/backlog.md` — P8 절 두 줄, 리스크 로그(F-fbaaae) — grep 범위
- `docs/wiki/review-index.md` 전문
- `docs/wiki/registry.md` — 1~66행, 167행, 195~217행(엔드포인트·브리핑·푸시 행)
- `docs/wiki/specs/S3.4-ask-user-protocol.md` 전문 · `S3.6-briefing-push.md` 전문 · `S3.2-tools-v2.md` 전문 · `S3.1-schema-v2.md`(grep: 9·10행)
- `docs/wiki/decisions/D07-tls-caddy.md` 전문
- `docs/wiki/templates/plan.md` 전문
- `docs/wiki/packages/P5-loop/04-review.md` 175~198행(§6·§7 인계)
- `docs/wiki/packages/P6-briefing/04-review.md` 180~207행(§6·§7 인계) · `P6-briefing/01-plan.md` 결정 I(225~231행)·범위 25~37행(grep)
- `docs/wiki/packages/P7-push/04-review.md` 112~186행(결정 A 판정·§6·§7 인계) · `P7-push/01-plan.md` 1~110행(형식 참고·판정 표 26행 형식)
- `docs/proposal.md` — 2장 범위 표(54~65행), 3.3 메모리 표(116~119행, grep), 3.5 관측성(134~138행), 8장 데모(235~246행), 9장 리스크(250~258행), 부록 A 화면 셋·되는 것/안 되는 것(285~385행)
- `docs/resolution-plan.md` — grep(186행 확인 칩 문장, 238행 P8 행)
- `.claude/skills/devlog/SKILL.md` 1~99행(`/devlog start`·`/devlog change` 절차, L-002 역할표 머리)
- `.claude/agents/backend-agent.md` 1~12행(범위 문장)
- `.claude/scripts/verify-plan.sh` 30~104행(검사 항목)
- `.claude/hooks/delegate-guard.sh`·`approve-commit.sh`·`stage-gate.sh`·`commit-guard.sh`·`safety-guard.sh`·`.githooks/pre-commit` — grep 만(에이전트 이름 고정·면제 경로·FIX 게이트 범위·비밀 패턴)
- 코드(사실 확인용 grep·부분 읽기): `app/api/routes.py`(`@router` 6개), `app/api/schemas.py` 40~124행, `app/tools/briefing.py` 1~66행, `app/tools/questions.py`(`list_pending` 시그니처·docstring), `app/main.py`(예외 매핑), `app/tools/context.py`(`TRACE_MAX_STRING`), `.github/workflows/tests.yml`(job 이름)
- (개정 2) `docs/wiki/packages/P8-frontend/02-plan-verify.md` 전문(§2-1·§3 소견 R-1~R-13) · `05-remediation.md` 전문(`F-ce7d18`) · `.claude/scripts/fix_guard_check.py` — grep `app/|alembic/`(22·45·180·203행)
