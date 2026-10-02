# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-02 21:30 — **세션 종료 지점. 활성 작업 없음(`active: none`).** P6-briefing 완료(`f9500fe`, dev 승격됨) · FIX-017 완료(`608694b`). **P7-push 는 계획까지 끝나고 사용자 계획 승인만 남았다** — 사용자가 승인 질문에 "다음 세션에서 이어갈 수 있게 기록" 을 택했으므로 **승인되지 않았다**. 다음 세션 첫 행동은 아래 "바로 다음에 할 것" 0번.

> **2026-10-02 세션 한 일**: ① FIX-016 응답 문구(`36c288e`) ② dev 승격(`36c288e`, main 은 보류) ③ **P6-briefing 전체** — 계획 `688c4a4` → U1 `e2155f9` · U2 `db3c645` · U3 `cfb55ea` · U4 `a2f032d` · U5 `e037728` · U6 `8589e37` · U7 `a67692e` · U8 `e2cca80` → 완료. 전체 **1721 passed skip 0**, R12(절반)·R19 구현완료.

**무엇이 돌아가게 됐나(P6-briefing)**: 서버를 `BRIEFING_SCHEDULER_ENABLED=1` 로 띄우면 1분마다 24시간 안·미브리핑 일정을 골라(지난 일정 제외) 패턴을 다시 계산하고, LLM 이 패턴 문장·요약 줄·한 줄 제안을 쓰고, 코드 검증기가 근거 없는 줄·감정/상담 표현·틀린 패턴 횟수를 버린 뒤 `briefed_at` 을 남긴다. LLM 이 실패하면 제안 없는 템플릿. `POST /briefings/run` 은 같은 함수(본문 없음 = 주기 작업과 동일, `schedule_id` = 그 일정 즉시 재생성). 사용법 `docs/RUNNING.md` "브리핑" 절. **U4~U7 은 단위마다 실 OpenAI·실서버로도 확인했다**(사용자 요청 — evidence `*-real-*.txt`).

active: **none** | frozen: none | 브랜치 `dev2` | origin/dev = `f9500fe` · **origin/main = `f05d017`(사용자가 직접 올린 포트폴리오용 README — 그대로 둔다)** | Docker DB `capstone2-postgres-1`(5433): 개발 `relationship`, 테스트 `relationship_test`

## 커밋 안 된 변경
- P7-push 계획 문서(`packages/P7-push/01-plan.md`·`02-plan-verify.md`·`evidence/`)와 이 파일·journal 을 "계획 검증 통과, 승인 대기" 기록 커밋으로 남긴다(사용자 승인 시). 그 커밋이 없으면 `git status` 에 `?? docs/wiki/packages/P7-push/` 로 보인다 — 지우지 말 것.

## 바로 다음에 할 것
0. **[최우선] P7-push 계획 승인 질문을 다시 한다**(AskUserQuestion: 승인 / 수정 요청 / 보류). 상태:
   - 01-plan: architect 초안, U1~U8, 판정 표 26행(1~25 자동, 26 = 사용자가 Chrome 에서 알림 수신 — 증거 5종 `evidence/*-u8-chrome-manual.txt`). 결정 A~G **사용자 확정 = 전부 권장안**(01-plan "확정" 줄): A 확인 전용 `/push-dev/` 정적 페이지(`PUSH_DEV_PAGE_ENABLED` 기본 꺼짐) · B 알림 = 인물 이름·일정 제목 + 시각·제안 한 줄(요약 줄·패턴 제외 — 원문 노출 차단) · C 발송 실패는 상태 문자열만, `briefed_at` 항상 기록 · D `pywebpush` 하나 버전 고정, VAPID 키는 사용자가 만들어 `.env`(값 출력 금지), 키 없으면 `NullNotifier` · E 404/410 구독 행 ORM 삭제 + trace 에 id 만 · F `GET /push/vapid-public-key`·`POST /push/subscriptions`, trace `tool_name="push"` step `push_send` · G 테스트는 `FakePushSender` 만.
   - 02-plan-verify: verifier(fable) **`결과: 통과`**, 점검표 8/8, [필수] 0, verify-plan 2차 **FAIL 0 / WARN 0**(`evidence/20261002-2123-verify-plan-2.txt`). 원칙5 와 확인 페이지는 양립(해석, CR 불필요 — 단 "제품 자료 미조회·기본 꺼짐·운영 미사용" 세 조건을 04-review 에서 증거로). 권고 **R-1~R-10** 은 구현 단위에서 반영(02-plan-verify §3 — 특히 R-2 `pywebpush` import 시점, R-6 일정 소유 단언, R-8 예외 메시지에 endpoint 섞임 방지).
   - 승인되면: 02-plan-verify `승인:` 줄 → `CURRENT active: P7-push` → `03-log.md` 생성 → journal START → `/commit`(계획 문서) → U1 위임은 L-004 로 따로 묻고 **단위마다 무엇을 하는지 자세히 설명한 뒤** 승인받는다.
   - U8 전 사용자 몫: VAPID 키 생성해 `.env` 에 넣기, macOS 알림 권한·집중 모드 확인, Chrome 에서 `/push-dev/` 로 구독.
1. ~~dev 승격~~(`f9500fe`) · ~~FIX-017 likes/dislikes~~(완료 — `fixes/FIX-017.md`; 교훈: 프롬프트 금지형 "절대 넣지 않는다" 는 사실 자체를 버리게 한다, 안내형으로). main 승격은 README 갈라짐 때문에 할 때 사용자에게 README 를 어느 쪽으로 둘지 묻는다.
3. P8(인물 카드·프론트 3화면) — frontend-agent 가 아직 없다. `/push-dev/` 의 구독 처리를 PWA 로 옮기는 일이 P8 몫.
4. 그 밖 FIX 후보: `/health` 빈 DB 를 ok · `update_person` 부분 반영 · `memory_promote` `source` 키 비대칭 · 주기 작업 루프 수준 실패가 trace 없이 로그로만(P9 전) · 루프가 잠근 일정을 수동 지정하면 404(낮음).

## 다음 패키지가 알아야 할 것 (P6-briefing 04-review §6·§7)
- **P7-push**: `Notifier` 자리에 `WebPushNotifier` 를 끼운다(`app/briefing/types.py`, 호출 자리 `app/briefing/run.py` 217~218행). 원문 노출·실패 시 `briefed_at` 은 위 0번의 결정 B·C 로 정해졌다(아직 승인 전).
- **P8**: 브리핑 조회는 `briefing_compose` trace 에서(스키마에 브리핑 테이블 없음, 결정 H). 사용자 귀속은 `output.person_id → persons.user_id`. 응답 `run_id` = trace `session_id`.
- **P10**: 패턴 "문장화" 가 규칙 값 복사("3회 (날짜…)")에 그침(실 LLM 5회 중 4회), 요약 줄 반말. 금지 표현 목록(14개)은 보조 방어 — 목록 밖 "슬퍼하… 다독여" 는 통과(verifier 실증).
- 운영: 스위치는 프로세스 하나에서만 켠다(워커 여럿이면 루프도 여럿 — `SKIP LOCKED` 로 중복 브리핑은 막힘). 서버를 켜 둔 채 두면 매분 돈다(대상 없으면 LLM 0회).
- P6-memory 인계는 그대로 유효: `person_facts` 세 출처(브리핑은 `pattern:*`+9키만 쓰고 옛 자유 키는 제외), trace 를 지우면 승격이 다시 돈다.

## 사용자 몫 (알려 둔 것)
- 브랜치: `dev2` 작업 → `dev` 검증(`dev2:dev`, L-003 대기) → `main` 배포. 다른 기기는 `git checkout dev2 && git pull --ff-only`.
- **[미확인] Windows 기기에서 훅·검증 스크립트 확인**(`test-guards.sh` 실패 0, `verify-impl.sh` pytest 통과, `_py.sh` 가 `python` 선택, venv `.venv/Scripts/python.exe`, 커밋 마커 자동 삭제).
- 환경 파일 15행 공백 값 정리 · 빈 DB `relationship_test_fix006_evidence` 정리 · GitHub main 브랜치 보호 규칙.

## 열린 질문 · 보류
- 환경 파일은 코드가 읽지 않는다(셸 `set -a; . ./.env; set +a`) — P9 에서 재검토(C-8).
- FIX-014(후보): Bash 편집은 `stage-gate`·`secret-guard` 를 지나간다 — 운용 규칙(Write/Edit 만)으로 막아 둠.
- 하네스 부채: `verify-impl.sh` 5번이 `## 2.` 아래 `###` 하위 절 표까지 수용 기준으로 읽음(awk 종료 조건 `^##+ `, 04-review §6-11) · verify-plan 토큰 스캔 오탐 · findings.py 빈 표 중복.
- P9 전: 다중 사용자 격리 부채(F-fbaaae). 개발 DB 확인용 행(`brief-u5-check` 인물 2·일정 4 포함)은 지우지 않는다. `.claude/.commit-approved` 에 옛 마커가 남아 있었으나 이후 커밋이 덮어써 소비됨.

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다. **사용자는 단위마다 무엇을 하는지 자세한 설명을 듣고 승인하길 원한다.**
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인(이번 세션에서 U5 DB 오류 처리·U8 빠진 테스트를 이렇게 잡았다).
- 실서버: `set -a; . ./.env; set +a; export POSTGRES_PORT=5433 APP_USER_ID=<확인용>; .venv/bin/uvicorn app.main:create_app --factory --port 8765` — 끝나면 반드시 `pkill -f "uvicorn app.main:create_app --factory --port 8765"`. 키 값 출력 금지.
- **커밋과 푸시는 따로 실행**(FIX-013). **파일 변경은 Write/Edit 툴로만.** `app/` docstring 에 "evaluation" 금지.
