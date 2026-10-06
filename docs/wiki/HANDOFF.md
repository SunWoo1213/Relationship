# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-05 20:20 — **세션 종료 지점(사용자 "다른 세션에서 이어서" 지시).** 진행 중인 작업 없음. 마지막 커밋 `4912865`(FIX-019, dev2 푸시됨 — 그 CI run `37301747971` 은 종료 시점에 in_progress, **다음 세션 첫 확인**).

active: **P7-push**(U1~U4 완료, U5~U8 남음) | frozen: none | 브랜치 `dev2` | origin/dev = `f9500fe` · origin/main = `f05d017`(사용자 포트폴리오 README — 그대로) | DB `capstone2-postgres-1`(5433): 개발 `relationship`, 테스트 `relationship_test` | 전체 **1804 passed skip 0**

> **2026-10-05 세션 한 일**: P7 계획 승인 `a69af80` → U1 `85393e0`(pywebpush·VAPID 설정) · U2 `6c98516`(구독 저장 API) · U3 `f256259`(알림 본문, 원문 미포함) · U4 `8e9af9e`(발송기·알림기, R-6 assert→명시적 if) · FIX 후보 기록 `47adb1e` · **FIX-018** `7bc2e60`(dev2 에도 CI — dev2 첫 CI success) · **FIX-019** `4912865`(answer_question 행 잠금, 수정 전 재현 FAILED 확인). 저장소 밖: 복기·면접 자료 01~16 + PDF.

## 커밋 안 된 변경
- 없음 — 세션 종료 기록 커밋에 `fixes/FIX-020.md`(계획·승인, 구현 전)·이 HANDOFF·journal 을 넣었다(다른 기기에서도 이어가도록).

## 바로 다음에 할 것 (순서대로)
0. ~~FIX-019 CI 확인~~ — **완료: run 37301747971 `success`(1m9s)**, 동시성 테스트가 Linux 에서도 통과. 세션 종료 기록 커밋 `b89c936`(dev2 푸시됨). 커밋 안 된 것은 이 줄과 journal 자동 줄뿐.
1. **FIX-021 ruff·mypy·커버리지 완료 `b124c8e` + 보완(mypy `python_version = "3.13"` 고정 — CI 3.13 과 로컬 3.14 의 typeshed 문구 차이로 CI 에서만 실패했던 것)** — ruff 0 · mypy 기준선 37(새 오류만 실패, `scripts/mypy_check.py --run`) · 커버리지 95.27%(하한 90) · 1809 passed. 커밋 후 dev2 CI 확인. 로컬 확인 명령: `.venv/bin/ruff check app tests scripts evaluation` · `.venv/bin/python scripts/mypy_check.py --run`. **다른 기기는 `pip install -r requirements-dev.txt` 필요.** FIX-021 CI success(run 37397662883). **[진행 중] FIX-022(점검 ⑤ — Linux 3.13+3.14 matrix · Windows job · test-guards CI · dbtest 표시 9개, 계획·승인 `fixes/FIX-022.md`)** backend-agent 실행 중, 미커밋. 끝나면 재확인 → 커밋·푸시 → Windows job 결과 확인(실패하면 사용자에게 "바로 수정 / continue-on-error" 결정 받기). **FIX-020 완료 `7459925`(CI success)** — 1808 passed skip 0. **이 기기 개발 DB 는 0002 로 올림(2026-10-06 사용자 실행, UNIQUE 3개 확인)** — 다른 기기는 각각 `alembic upgrade head` 필요. 확인: `docker exec capstone2-postgres-1 psql -U app -d relationship -tAc "select version_num from alembic_version"` → `0002`. (아래는 계획 기록) **FIX-020 · UNIQUE 제약 3개 + ON CONFLICT**(계획 **승인됨** — `fixes/FIX-020.md`, 사용자가 CR 아닌 FIX 로 판단). 대상: `person_facts(person_id,key)` · `person_aliases(person_id,alias)` · `push_subscriptions(user_id,endpoint)`. 순서: 재현 테스트(수정 전 FAILED) → models + Alembic `0002`(중복 있으면 멈춤, down/up 왕복) → 세 upsert 를 `INSERT … ON CONFLICT` → S3.1 카드 보충 한 줄. backend-agent 위임 전 **L-004 승인 질문**. 개발 DB 중복 0건 확인됨(2026-10-05). 끝나면 **사용자에게 개발 DB `alembic upgrade head` 요청**.
2. **테스트 점검 나머지(사용자 "차례대로" 지시, 항목마다 계획→승인)**: ③ ruff(+`DTZ`)·커버리지 리포트(기존 위반은 기준선, 새 위반만 막기) → ⑤ CI Python 3.13↔로컬 3.14 정렬·Windows job·`test-guards.sh` CI → ⑦ 커밋 경계 통합 테스트(`/chat`·브리핑 실제 커밋) → ⑧ 마이그레이션 down/up(FIX-020 에서 일부) → ⑨ 순수 함수 속성 기반 테스트 → ④ live 스모크(`@pytest.mark.live`, 기본 꺼짐)·프롬프트 회귀 세트(P10 과 함께).
3. **P7-push U5~U8**: U5 두 경로 연결(`deps.get_notifier`·`scheduler.default_run_once` → `notifier_from_env`, R-1 같은 세션) → U6 `/push-dev/` 확인 페이지 → U7 판정 1~25행·RUNNING.md·registry → U8 Chrome 실발송(사용자: VAPID 키 생성 `.env`, macOS 알림 권한). 그 뒤 verifier 04-review. **P7 완료 시 복기 자료 `08-웹푸시.md` 갱신 필수.**
4. 사용자 질문에 답한 의견(결정 아님): Langfuse·Jaeger 지금 미도입 — 대신 `loop_extract` 토큰 0 수정·trace `latency_ms`·`prompt_version`·비용 집계(FIX 후보). 원하면 D 카드로.

## FIX 후보 (복기 자료 작성·점검 중 코드로 확인, 미착수)
- `app/er/judge.py` 4행 docstring 과일반화(OpenAI 는 logprobs 있음 → "Claude API 기준") · 작업 메모리("최근 N턴") 미구현 — S3.5 와 불일치(FIX/CR 판단) · 임베딩 건너뛰면 `s_emb=0` 이 관측값처럼 합산(D12 와 비대칭) · `search_person` 질의 임베딩 예외 경로 미확인 · `.env.example` 의 `EMBEDDING_PROVIDER`·`EMBEDDING_MODEL`·`APP_ENV` 읽는 코드 없음 · 인물 분리(오병합 되돌리기) 기능 없음 · `loop_extract` trace 토큰 0(미실측) · 지난 일정 제외로 서버 꺼진 동안 지난 약속은 브리핑 안 됨 · `temperature=0` 은 Gemini 경로 4곳뿐(OpenAI·Claude 기본값).
- 하네스: `session-start.sh` 53행 "dev 에서만 작업" 낡은 문구(지금 dev2) · commit SKILL "첫 커밋" 절 같은 문구.
- 이전부터: `/health` 빈 DB 를 ok · `update_person` 부분 반영 · `memory_promote` `source` 키 비대칭 · 주기 작업 루프 수준 실패가 로그로만 · 루프가 잠근 일정 수동 지정 시 404.

## 저장소 밖 — 복기·면접 자료(커밋 금지)
- `~/Desktop/Portfolio/wiki/interview/relationship/` 01~16 + `Relationship-복기자료.pdf`(311쪽). 규칙: Portfolio `CLAUDE.md` 6절 — 패키지·FIX 가 끝나면 영향 파일 갱신 → 그 README "갱신 기록" 한 줄 → Portfolio 에서 `python3 양식/도구/interview_pdf.py relationship`. FIX-018·019·U3·U4 는 **아직 자료에 반영 안 함**(다음 갱신 때 `08`·`11`·`13`·`14`·`16`).

## 사용자 몫
- 브랜치: `dev2` 작업 → `dev` 검증(`dev2:dev`, L-003) → `main`. 다른 기기: `git checkout dev2 && git pull --ff-only`. **워크플로 파일을 바꾸는 푸시는 gh 토큰 `workflow` scope 필요(2026-10-05 추가함).**
- [미확인] Windows 에서 훅·검증 스크립트 확인 · 환경 파일 15행 공백 · 빈 DB `relationship_test_fix006_evidence` 정리 · GitHub main 브랜치 보호.

## 주의
- **언어: 전부 한국어.** 위임·커밋 승인 질문 전에 **예시·요청/응답·이유를 담은 자세한 설명**을 먼저 준다(사용자가 요약만 보고 "자세하게" 되물은 적 있음).
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인(이번 세션: U4 `assert` 문제를 이렇게 잡음). 동시성 테스트는 여러 번 돌려 본다.
- 하네스·훅 변경은 계획 먼저 보이고 승인(L-004·사용자 지시). **커밋과 푸시는 따로 실행**(FIX-013). **파일 변경은 Write/Edit 툴로만.** `app/` docstring 에 "evaluation" 금지, `app/push/sender.py` 외에 발송 라이브러리 이름 문자열 금지(불변식 grep).
- 실서버: `set -a; . ./.env; set +a; export POSTGRES_PORT=5433 APP_USER_ID=<확인용>; .venv/bin/uvicorn app.main:create_app --factory --port 8765` — 끝나면 `pkill -f "uvicorn app.main:create_app --factory --port 8765"`. 키 값 출력 금지.
