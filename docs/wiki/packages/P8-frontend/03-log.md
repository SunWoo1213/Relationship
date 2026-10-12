# P8-frontend · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-10-11 00:40 · docs(P8-frontend): 프론트 3화면 계획을 검증·승인까지 마치고 활성화한다 · ab29daa
- 변경: 01-plan(architect 초안 → 사용자 결정 반영 개정 1 → verifier 소견 반영 개정 2), 02-plan-verify(verifier 1차 보류 [필수] R-1 → 재검증 통과, 사용자 승인 기록), 05-remediation(`F-ce7d18` 해소), 증거 8개(메인 세션 3 · verifier 5), 이 03-log 생성. CURRENT active P8-frontend.
- 이유(기획서·카드 연결): backlog P8 첫 줄 수용 기준 "채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면". 사용자 확정 결정 A~N(A frontend-agent 신설 sonnet · C 같은 출처 + `/api` 접두 · F 원문 조회 API 2개 · L 챗봇형 UI Tailwind+shadcn/ui · M 오프라인 제외 — 기획서 부록 A 385행 · N ChatGPT 식 왼쪽 사이드바).
- 정합성 확인: 원칙 / D / S / 보안 — verifier 점검표 8행 통과(1차부터). 원칙5(화면 3개)·원칙7(경계 문장)·원칙9(조회는 판정 아님) 해석은 02-plan-verify §2-1 판정. 오프라인은 CR 없이 범위에서 제외.
- 승인 조건(사용자, 2026-10-10): ① U1~U9 모든 작업 단위는 커밋 전에 verifier 코드 리뷰 ② 디자인 추가 수정은 추후 요청 시 별도 작업(P8 안에서는 수정 1회 상한). 활성화는 FIX-030(`c37c99a`, CI run 38062960426 세 job success) 뒤 — 활성화하면 test-guards 상태 의존 실패가 가려지기 때문.
- 남은 것 · 다음 단위: U0 하네스 — 메인 세션이 훅 변경 diff 계획(②③ GATED·approve-commit → ① frontend-agent.md → ④ `fix_guard_check.py` 180행 `web/` → ⑤ test-guards 5경우 → ⑥~⑧ CLAUDE.md·SKILL.md·INDEX)을 사용자에게 먼저 보이고 승인, `settings.json` npm/npx allow 여부도 사용자 결정. verifier 권고 N-1~N-3 은 U9·04-review 에서.
- Refs: P8-frontend R12 R19 R8 D1 D7 S3.1 S3.4 S3.6 원칙5 원칙7 원칙9 F-ce7d18

## 2026-10-11 12:50 · harness(P8-frontend): 프론트 담당 에이전트를 만들고 승인·검증 게이트에 넣는다 · pending
- 변경: U0 ①~⑧ — `.claude/agents/frontend-agent.md` 신설(sonnet, 규칙 ①~⑧) · `delegate-guard.sh` GATED·`approve-commit.sh --stage` 에 frontend-agent · `fix_guard_check.py` 182행 `web/`(+22행 docstring·206행 메시지, `commit-guard.sh` 주석 11·100행) · `test-guards.sh` 6줄(케이스 6·7, `web/x.ts` 거부, frontend-agent 위임 거부/허용·마커 소비) · CLAUDE.md·devlog SKILL·INDEX. 사용자 결정으로 `settings.json` allow 에 `npm run`·`npm test`·`npm ci`·`npm install`(npx 제외).
- 이유(기획서·카드 연결): 01-plan U0, 결정 A, 사용자 확정 "FIX 게이트 web/ 까지". 적용 순서 ②③ → ① (R-3, 게이트 구멍 방지).
- 정합성 확인: L-002 · L-004 · 원칙5 · 원칙7 — 위반 없음. **`stage-gate.sh` 는 고치지 않음** — 앞 초안의 "⑨ `web/` 추가" 는 불필요(R-2, 면제 목록 방식), `test-guards` 165행 `web/x.ts (active: none) 거부` 가 실증.
- 검증: `evidence/20261011-1237-u0-harness.txt`(test-guards 실패 0·ok 222) · verifier `review-u0-harness.md` 결과 통과([필수] 0) · 변이 시험 `evidence/20261011-1241-verifier-u0-mutation.txt`(원본 exit 1 / web/ 조건 제거 exit 0). 권고 R-U0-1·2(CLAUDE.md 111행·SKILL 55행 문구)는 이 커밋에서 반영.
- **R-3: test-guards PASS 전에는 frontend-agent 위임 금지** — Mac PASS 확인(위 증거). **Windows 는 대기(R-U0-4)** — 푸시 뒤 CI windows job 결과를 증거 파일 끝에 덧붙인 뒤 "U0 완료(Mac·Windows)" 로 본다.
- 남은 것 · 다음 단위: R-U0-3 — U4 이후 단위별 verifier 리뷰에 `web/package.json` scripts 전부·의존성 변경·`package-lock.json` 동반 여부를 고정 점검 항목으로(npm allow 가 safety-guard 텍스트 매칭을 우회하는 간접 경로라서). security.md 한 줄 추가는 사용자 판단 대기. 다음: U1 인물 목록·카드 조회 API(backend-agent).
- Refs: P8-frontend L-002 L-004 원칙5 원칙7 F-ce7d18

## 2026-10-11 15:05 · feat(P8-frontend): 인물 목록과 인물 카드를 읽는 조회 API 를 더한다 · pending
- (앞 항목 보충) U0 커밋 = `440a0e5`. 그 CI run 38111227562 windows job 이 test-guards session-start 시험에서 멈춤(U0 새 시험은 Windows 에서도 ok) → 사용자 승인으로 취소 → **FIX-031** `6479c1d` 로 고침 → CI run 38116488226 세 job success(windows 3분 32초). **R-U0-4 해소 — U0 Mac·Windows 통과, frontend-agent 위임 가능(R-3).** R-U0-3: 사용자 결정 "security.md 에는 추가하지 않는다" — 단위별 verifier 점검만.
- 변경: `app/api/read.py`(신규 — `list_persons`·`get_person_card`, 이름 확정) · `schemas.py` 응답 모델 7종 · `routes.py` `GET /persons`·`GET /persons/{id}` · `tests/test_api_read_persons.py` 12건.
- 이유(기획서·카드 연결): 01-plan U1. 조회는 판정이 아니므로 DB 쓰기·trace 0(원칙9 해석, 02-plan-verify). 소유 확인은 `app.tools.persons._owned_person` 을 밑줄 이름 그대로 재사용(공개 승격 없음 — 보안 판정을 한 곳에) → 타 사용자·부재 같은 404.
- 정합성 확인: 원칙9 · S3.1(원문 보존 — 응답에 `raw_utterance` 없음, 타임라인 쿼리가 컬럼을 고르지 않음) · S3.5 · 스키마 v2. 확정 값: `TIMELINE_LIMIT=20`(01-plan "U1 에서 확정" — 카드는 최근 흐름, 이력은 facts·patterns 가 요약) · `UPCOMING_SCHEDULES_LIMIT=10`(01-plan 에 없던 값 — **사용자 결정 "10건 유지 + 테스트"**, 카드 응답 크기 상한, 24시간 브리핑 범위와 무관) · 별칭 정렬은 기존 `_person_out` 과 같은 Python `sorted()`(R-U1-4).
- 검증: verifier 1차 **보류** — [필수] R-U1-1 `last_contact_at` max→min 변이를 테스트가 못 잡음 → backend-agent 재작업(값 단언·순서가 뒤집히는 픽스처·상한·경계·별칭 테스트 5건) → 재검토 **통과**(변이 7건 모두 검출, `review-u1-read-persons.md`). 12 passed · 전체 1894 passed skip 0 · ruff · mypy 38/38. 증거 `evidence/20261011-1350-*`·`1420-*`·`verifier-u1-*`.
- **절차 위반 기록(R-U1-2)**: 1차 구현에서 backend-agent 가 `read.py`·`schemas.py`·`routes.py` 를 Bash(heredoc·python 치환)로 썼다(자기 보고) → secret-guard·stage-gate 미경유. verifier·메인 세션 확인 결과 내용은 깨끗(비밀 0·삭제 0·범위 밖 0). 재작업과 FIX-031 은 위임 프롬프트 맨 앞에 "Write/Edit 로만" 을 재명시해 지켜졌다(자기 보고). 근본 대책은 하네스 FIX 후보 **FIX-014**(훅을 Bash 쓰기까지 넓히기)와 연결.
- 남은 것 · 다음 단위: U2 원문 조회 API 2개(`GET /events/{id}/raw`, `GET /persons/{pid}/facts/{fid}/sources`, backend-agent). 위임 프롬프트에 "Write/Edit 로만" 을 계속 맨 앞에.
- Refs: P8-frontend S3.1 S3.5 원칙9 FIX-031 FIX-014

## 2026-10-11 15:45 · feat(P8-frontend): 타임라인·사실의 근거 원문을 펼쳐 보는 조회 API 를 더한다 · pending
- (앞 항목 보충) U1 커밋 = `6c2d0e7`, CI run 38117011109 세 job success.
- 변경: `app/api/read.py` `get_event_raw`·`get_fact_sources`·`FACT_SOURCES_LIMIT` · `schemas.py` `EventRawOut`·`FactBriefOut`·`FactSourceEventOut`·`FactSourcesOut`(`raw_utterance` 가 실리는 유일한 모델 둘) · `routes.py` 두 GET · `tests/test_api_read_raw.py` 18건.
- 이유(기획서·카드 연결): 01-plan U2·결정 F, 부록 A "타임라인 항목을 펼치면 원문 발화가 나옵니다".
- 정합성 확인: S3.1(저장 문자열 그대로 — 특수문자·줄바꿈·이모지·5000자 테스트) · R8 · 원칙9(쓰기·trace 0). 격리: `persons.user_id` 조인 조건 두 곳 + `person_facts.person_id = person_id`, 404 는 계획 4경우 + 3경우 모두 같은 본문. 확정 값(R-U2-1): `FACT_SOURCES_LIMIT=20`(승격 배치 상한 `MEMORY_PROMOTE_MAX_EVENTS`=20 과 맞춤 · 승격 누적·패턴 사실은 20건을 넘을 수 있고 전체 건수는 U1 카드의 `source_count` 로 구분) · 정렬 `occurred_at desc` → 2차 키 `id desc`. **계획 밖 방어 조건** 근거 쿼리 `Event.person_id == person_id` — verifier 가 `fact_sources` 쓰기 경로 셋(promote·patterns·direct_facts)을 읽고 정당하게 다른 인물 이벤트가 연결되는 경로 없음 확인 → 정상 데이터 영향 없음, 사용자 질의 불필요(R-U2-1). 이런 계획 밖 판단은 앞으로 구현 전에 보고하게 한다(FIX-033).
- 검증: verifier `review-u2-read-raw.md` 통과([필수] 0) — 변이 8건(격리 3·정렬 2·상한·strip·방어 조건) 전부 FAIL, U1 변이 2건 여전히 FAIL. 30 passed · 전체 1912 passed skip 0 · ruff · mypy 38/38. 증거 `evidence/20261011-1520-u2-*`·`1529-verifier-u2-*`.
- 남은 것 · 다음 단위: R-U2-2 `read.py` 모듈 docstring 갱신은 U3 위임에 포함(제품 코드라 메인 세션이 직접 고치지 않음) · R-U2-3 판정표 7행(`briefed_at`·`updated_at` 변화 0) 값 테스트는 U3 공통 픽스처에서 · R-U2-4(구현자가 저장소 파일로 변이) → FIX-033. 다음: 사용자 결정 "U2 끝내고 FIX 먼저" → FIX-014 → 032 → 033, 그 뒤 U3.
- Refs: P8-frontend S3.1 R8 원칙9

## 2026-10-12 17:05 · U3 시작 — 대기 질문·브리핑 조회 API · 진행 중
- (앞 항목 보충) U2 커밋 = `2c902f0`, CI 38119853036 success. 그 뒤 FIX-014(`de35242`)·FIX-032(`22a6822`)·FIX-033(`7031a19`) 완료, CI 전부 success.
- 재개 확인: `git status` 미커밋 3개(HANDOFF·FIX-033.md 결과절·journal — 기록 파일만, U3 커밋에 포함) · CURRENT active P8-frontend · Docker `capstone2-postgres-1` healthy. 사용자 결정(AskUserQuestion): "U3 시작". L-004 마커 `--stage backend-agent` 는 승인 **뒤에** 생성(17:04).
- **계획 밖 값 사전 확정(FIX-033 (b) 선반영 — 구현 전 사용자에게 물음)**: 01-plan U3 의 "기간 상수(U3 에서 확정)" + 계획에 없던 정렬·상한. 사용자 확정 2026-10-12: `BRIEFINGS_LOOKBACK_DAYS = 7`(근거: 스케줄러 리드 창 `BRIEFING_LEAD_HOURS=24` 보다 넓어야 지난 브리핑을 돌아볼 수 있고, 데모 DB 에서 화면이 길어지지 않는 값 — 미래 쪽 상한 없음) · 정렬 `scheduled_at desc` → 2차 키 `schedule_id desc`(가까운 미래 일정이 맨 위) · `BRIEFINGS_LIMIT = 20`(`TIMELINE_LIMIT`·`FACT_SOURCES_LIMIT` 와 같은 값, 기간으로 이미 좁혀지므로 안전장치). 01-plan 94행에 반영. 이 밖의 계획 밖 값이 나오면 구현자가 멈추고 보고(규칙 (b)).
- 위임 범위: `GET /questions/pending`(기존 `list_pending` 재사용) · `GET /briefings` · R-U2-2 `read.py` docstring · R-U2-3 `briefed_at`·`updated_at` 값 단언 공통 헬퍼.
- Refs: P8-frontend S3.4 S3.6 D2 R12 원칙9 FIX-033

## 2026-10-12 18:10 · feat(P8-frontend): 대기 질문 목록과 저장된 브리핑을 읽는 조회 API 를 더한다 · pending
- 변경: `app/api/read.py` `list_briefings()`·`BRIEFINGS_LOOKBACK_DAYS=7`·`BRIEFINGS_LIMIT=20`·모듈 docstring(R-U2-2 닫힘) · `schemas.py` `BriefingRecordOut`·`BriefingScheduleOut`·`BriefingPersonOut`(기존 line/suggestion/pattern 모델 재사용, 원문 필드 0) · `routes.py` `GET /questions/pending`(`resolve_session_id`+`build_chat_ctx`+기존 `list_pending`, 응답 `ChatPendingQuestionOut`)·`GET /briefings?schedule_id=` · 신규 `tests/helpers_read_api.py`(`snapshot_db`·`assert_no_writes` — R-U2-3 닫힘: 8테이블 행 수 + `schedules.briefed_at`·`persons.updated_at` **값**) · `tests/test_api_questions_pending.py` 8건 · `tests/test_api_read_briefings.py` 22건 · `registry.md` U3 행 6개 + U1·U2 행 8개(R-U3-4).
- 이유(기획서·카드 연결): 01-plan U3·결정 G(일정마다 최근 브리핑 1건), S3.4(프론트 확인 칩 = 미답변 pending_questions), S3.6, R12. U5 채팅 화면의 대기 칩 복원과 U7 브리핑 화면의 원천.
- 정합성 확인: trace 원천 `tool_name='briefing' AND step='briefing_compose'` 둘 다(상수 import, R-9) · `row_number()` 로 일정별 최신 1행(`created_at desc → id desc` — 동률은 같은 트랜잭션 `now()` 고정 때문에 실제로 생김, verifier 확인) · `output->>'schedule_id'`/`'person_id'` BigInteger 캐스팅 조인 + `persons.user_id` · 원문 0 · 쓰기 0·trace 0 · `get_briefing` 툴 미호출. **계획 밖 판단(FIX-033 (b))**: 사전 확정 3개(17:05 항목) 외에 구현자 보고 3개 — ① 쓰기 0 스냅샷 7→8테이블(`pending_questions` 추가, 판정표 8행 충족) ② `routes.py` `ctx.now = now` 직접 대입(`build_chat_ctx` 가 `now` 를 안 받고 `deps.py` 는 판정표 11행 무변경 — 동작 위험 없음: non-frozen dataclass, 요청마다 새 ctx, 변이 M20 이 고정) ③ `schedules.person_id == persons.id` 일치 검사 생략(`run.py` 195·224~225행이 두 키의 단일 출처 — 정상 데이터 안전). 메인 세션 해석 2개(최신 동률 `id desc` · `schedule_id` 쿼리는 404 규약·기간 미적용)는 verifier 가 25행·결정 G 와 모순 없음 판정.
- 검증: verifier `review-u3-read-questions-briefings.md` **통과**([필수] 0 · [권고] 6). 구현자 변이 24종 전부 검출(저장소 밖 사본) + verifier 독립 변이 8건(런타임 치환 플러그인, 저장소 무수정): 계약을 깨는 6건 전부 검출 — 표에 없던 V5(분할 키 person_id)·V8(응답 모델 kind 누락) 포함, V6·V7 은 동치 변이. U1R·U2R 회귀 변이 여전히 검출. 30 passed · 전체 **1942 passed skip 0** · ruff · mypy 38/38. 증거 `evidence/20261012-1800-u3-*`(5) · `20261012-1733-verifier-u3-*`(6). 메인 세션 재실행으로 30 passed·ruff·mypy 재확인.
- 절차 기록: verifier 1차 실행이 변이 11회를 끝낸 뒤 리뷰 파일 쓰기 직전 10분 무응답으로 하네스 watchdog 에 중단 → 저장소 무수정·떠 있는 pytest 없음 확인 후 같은 에이전트를 SendMessage 로 재개(재실행 없이 산출물만 작성). **증거 (c) 미달 1건(R-U3-3)**: 구현자 변이 증거가 pytest 전체 출력이 아니라 필터된 줄뿐 → 메인 세션이 줄 단위 원본·스크립트를 `evidence/20261012-1800-u3-mutation-raw.txt`·`-mutation-script.py.txt` 로 보존하고 머리에 미달 표기. 다음 위임부터 "변이마다 pytest 출력 전체를 파일로" 를 프롬프트에 고정, 재발 시 [필수].
- 권고 처리(사용자 결정 2026-10-12 "U9 로 미루고 지금 커밋"): **R-U3-1**(`ctx.now = now` → `dataclasses.replace` 관례)·**R-U3-2**(목록 조인 `Person.id == Schedule.person_id` 한 줄 방어) 는 두 줄짜리이고 동작 결함이 아니라(M20 고정·`run.py` 단일 출처) 위임 2회 비용을 피해 **U9 백엔드 몫에 포함**. R-U3-4 registry U1·U2 행은 이 커밋에서 추가, "(U3 미커밋)" 6칸은 다음 커밋에서 해시로 교체. **R-U3-5**(U1·U2 `test_쓰기_0_trace_0` 을 헬퍼로 교체 · `_COUNTED_MODELS` 에 `push_subscriptions` 추가) 는 U9. **R-U3-6** ④ 판정표 9·10행의 "실제 실행으로 만든 trace" 부분은 U9 끝에서 끝 판정으로 · ⑤ **U7 에 넘길 결정**: `#/briefings?schedule_id=N` 강조를 목록+클라이언트 강조로 할지 `GET /briefings?schedule_id=` 호출(7일 창 무시, 푸시 클릭용)로 할지 — U7 위임 전 사용자에게 묻는다.
- 남은 것 · 다음 단위: U4 프론트 골격(frontend-agent, L-004) — 위임 프롬프트에 R-U0-3(verifier 가 `web/package.json` scripts·의존성·lock 점검)·(c) "출력 전체" 고정. 커밋 뒤 CI 세 job 확인 → 03-log 에 해시·run 보충.
- Refs: P8-frontend U3 S3.4 S3.6 D2 R12 원칙9
