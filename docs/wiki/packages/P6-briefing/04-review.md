# P6-briefing · 완료 검토 (04-review)

날짜: 2026-10-02 | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

읽은 것: `01-plan.md` 전문(수용 기준·해석 ㄱ~ㄷ·판정 표 30행·지킬 불변식·결정 A~K 확정 줄·결정 E "구현 중 변경" 줄·후행 기대), `02-plan-verify.md` 전문(권고 R-1~R-7), `03-log.md` 전문(U1~U8 + 메인 세션 추가 기록 6건), `05-remediation.md`, `docs/wiki/specs/S3.6-briefing-push.md`, `review-index.md` R12·R19 행, `docs/backlog.md` 77~84행, `registry.md` 38·53·62·64~66·187~200행, `docs/RUNNING.md` 212~262행, `CURRENT.md`. 코드는 **읽기만**: `app/briefing/` 7파일 전문(`compose.py` 는 정의 목록 + `build_briefing_prompt`·`validate_briefing`·`template_briefing`·`FakeBriefingComposer`), `git diff 36c288e -- app/main.py app/api/*.py app/settings.py .env.example` 전문, 테스트 6파일의 부정 케이스 본문, `tests/conftest.py` 60~135행. 증거 파일은 `evidence/*-real-*.txt` 5개·`*-negative.txt` 7개·`*-u8-acceptance.txt` 를 읽었다. git 은 `bash .claude/scripts/gitlog.sh P6-briefing S3.6 R12 R19`(20:16). 코드·계획·카드·테스트는 고치지 않았다.

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P6-briefing | tee docs/wiki/packages/P6-briefing/evidence/20261002-2016-verify-impl.txt`

### 1차 (04-review 작성 전 — `04-review.md 없음` WARN 1 은 예고된 정상)
```
== verify-impl P6-briefing  (20261002-2016) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1721 passed, 1 warning in 15.60s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261002-2016-pytest.txt
PASS  compileall 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261002-2016-lint.txt
PASS  태그 P6-briefing 커밋 12 건 → evidence/20261002-2016-commits.txt
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D14
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.5
PASS  커밋에 태그 존재: S3.6
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P6-briefing 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=1 → evidence/20261002-2016-summary.txt ==
```
1차 FAIL 0 / WARN 1. FAIL 이 없으므로 `findings.sh` 로 올릴 소견은 없다(WARN 은 이 문서 작성으로 사라지는 것 — 2차에서 확인). `evidence/20261002-2016-pytest.txt` 31행 "1721 passed, 1 warning" — **skipped 0**(`SKIPPED` 줄 없음, DB `capstone2-postgres-1` 5433 접속). 린트는 ruff 미설치라 `compileall` 경로(스크립트 2번 분기).

### 2차 (이 문서를 쓴 뒤 재실행 — `tee …/evidence/20261002-2024-verify-impl-2.txt`) — **FAIL 6, 전부 파서 문제**
`verify-impl.sh` 5번 검사는 `## 2.` 부터 **다음 `## ` 헤딩**까지의 모든 표 행을 수용 기준 행으로 읽는다. 1차 초안에서 "계획과 달라진 점" 표를 `### 2-1` 하위 절로 두었더니 그 표의 6행(`#`·(a)·(c)·(d)·(e)·(f) — (b) 는 우연히 경로 토큰이 있어 PASS)이 증거 열 검사에 걸렸다. 수용 기준 34행은 전부 PASS 였다. 조치: 하위 절 `### 2-1/2-2/2-3` 을 최상위 `## 2-1/2-2/2-3` 으로 바꿔 표 영역을 닫았다(내용 변경 없음) → 3차.
```
== verify-impl P6-briefing  (20261002-2024) ==
(…수용 기준 34행 PASS 생략 — 3차 출력과 동일, 파일에 전문…)
FAIL  증거가 파일·커밋·경로가 아니다:  #  ← 달라진 것
FAIL  증거가 파일·커밋·경로가 아니다:  (a)  ← U4 금지 표현 검사를 제안→**제안+요약 줄**로 확대, 목록 11→*
PASS  증거 확인:  (b)  ← U5 `run_briefings` 시그니처 — 계획 `(session_f
FAIL  증거가 파일·커밋·경로가 아니다:  (c)  ← U5 `SQLAlchemyError` — 처음엔 `after_record
FAIL  증거가 파일·커밋·경로가 아니다:  (d)  ← U6 `BriefingRunResult.session_id` 추가(응답 
FAIL  증거가 파일·커밋·경로가 아니다:  (e)  ← U7 주기 루프 수준 예외를 **trace 없이 로그만**(01-plan
FAIL  증거가 파일·커밋·경로가 아니다:  (f)  ← `briefing_error.stage` 5종(`select
PASS  registry 에 P6-briefing 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=6 WARN=0 → evidence/20261002-2024-summary.txt ==
```
이 FAIL 6 은 구현·증거의 결함이 아니라 04-review 문서 구조의 문제이므로 `findings.sh` 로 소견을 만들지 않았다(같은 문서를 고쳐 3차에서 0 이 됨 — §8). 하네스 부채로 한 줄: `verify-impl.sh` 5번이 `###` 하위 절을 구분하지 못한다(L-nnn/FIX 후보, §6-11).

### 3차 (헤딩 수정 뒤 — `tee …/evidence/20261002-2025-verify-impl-3.txt`) — **FAIL 0 / WARN 0**
전문은 §8.

### 4차 (§1·§6 문장 보충 뒤 최종 확인 — `tee …/evidence/20261002-2026-verify-impl-4.txt`) — **FAIL 0 / WARN 0**, 증거 행 34 PASS, 1721 passed. 3차와 결과 동일(전문은 파일).

### 이 검토가 만든 evidence
- `evidence/20261002-2016-verify-impl.txt` · `-pytest.txt` · `-lint.txt` · `-commits.txt` · `-summary.txt` — 1차 기계 검증.
- `evidence/20261002-2016-verifier-rerun.txt` — 판정 표 28~30행·무변경을 verifier 가 **직접 재실행**한 명령·출력(alembic · tools_check · `git diff --stat 36c288e …` · 불변식 grep 6종 · `.env.example` VAPID 줄 불변).
- `evidence/20261002-2016-verifier-negative.txt` — §3 부정 케이스 34건 node id 실행 + 어긋남 실험 4종(코드 무변경, 설정·입력만).
- `evidence/20261002-2024-verify-impl-2.txt`(+ `-pytest`·`-lint`·`-commits`·`-summary`) — 2차(파서 FAIL 6). `evidence/20261002-2025-verify-impl-3.txt`(+ 같은 4종) — 3차 FAIL 0/WARN 0(§8).
- 스크래치(커밋하지 않음, 내용은 `-verifier-negative.txt` 머리·각 절에 요약): `verifier_neg_db.py`(창 경계·지난 일정·다른 사용자, 테스트 DB 롤백) · `verifier_neg_validate.py`(검증기 입력 5종) · `test_verifier_neg_scheduler.py`(스위치 `1` 복제본).

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

보고된 수치를 옮기지 않고 verifier 가 다시 돌린 값: 전체 회귀 **1721 passed, 0 failed, 0 skipped**(1차 verify-impl, `-rs`), `alembic check` → "No new upgrade operations detected.", `tools_check.py` → "RESULT: 7/7 ok", `git diff --stat 36c288e -- app/tools/briefing.py app/agent app/memory app/er` → 0줄, 불변식 grep 6종 전부 0건(`-verifier-rerun.txt`).

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록 | 8589e37, evidence/20261002-2016-pytest.txt, evidence/20261002-1854-u6-real-curl.txt | 통과 |
| 해석 ㄱ — HTTP `POST /briefings/run` 200, 처리 경로가 주기 작업과 같은 함수 `run_briefings` | evidence/20261002-2016-verifier-negative.txt (A절 `test_manual_endpoint_and_scheduler_call_the_same_run_briefings_object`), app/api/routes.py, app/briefing/scheduler.py | 통과 |
| 해석 ㄴ — 창 안 미브리핑 일정마다 `briefings[]` 1건(패턴 문장·요약 줄·한 줄 제안, 모두 입력 근거), `briefing_compose` trace 1행 | evidence/20261002-1950-u8-rows-1to10.txt, evidence/20261002-1641-u5-real-e2e.txt, evidence/20261002-2016-verifier-negative.txt | 통과 |
| 해석 ㄷ — `briefed_at == now`, 재실행 시 재선정 없음, 실패 일정은 NULL | evidence/20261002-1950-u8-rows-1to10.txt, evidence/20261002-1940-u7-real-scheduler.txt, evidence/20261002-2016-verifier-negative.txt | 통과 |
| 판정 1 ㄱ·ㄴ·ㄷ 양성(API 한 흐름) | evidence/20261002-1950-u8-rows-1to10.txt (tests/test_api_briefings.py::test_run_briefings_creates_briefing_and_marks_briefed), evidence/20261002-2016-pytest.txt | 통과 |
| 판정 2 ㄷ 재실행 멱등 | evidence/20261002-1950-u8-rows-1to10.txt (::test_run_briefings_second_call_finds_nothing), evidence/20261002-1854-u6-real-curl.txt (①) | 통과 |
| 판정 3 ㄱ 같은 함수 | evidence/20261002-2016-verifier-negative.txt (A절), evidence/20261002-1950-u8-rows-1to10.txt | 통과 |
| 판정 4 창 경계 양성 `T+24h` | evidence/20261002-2016-verifier-negative.txt (A절 + D절 `lead_hours=24 -> ['T+0','T+24h']`) | 통과 |
| 판정 5 창 경계 부정 `T+24h+1s` | evidence/20261002-2016-verifier-negative.txt (A절 + D절 `24+1s` 면 포함됨 — 경계가 민감함) | 통과 |
| 판정 6 지난 일정 `T−1s` 선정 안 됨(결정 B(i), S3.6 보충 줄) | evidence/20261002-2016-verifier-negative.txt (A절 `test_select_due_schedules_excludes_past_schedule` + D절), docs/wiki/specs/S3.6-briefing-push.md | 통과 |
| 판정 7 이미 브리핑됨 | evidence/20261002-2016-verifier-negative.txt (A절 + D절 `T+3h briefed` 미포함) | 통과 |
| 판정 8 다른 사용자 격리 / API 404 `not_found`, `briefed_at` 불변 | evidence/20261002-2016-verifier-negative.txt (A절 4건 + B절 `APP_USER_ID=other-user` 면 `assert 200 == 404` FAIL), evidence/20261002-1854-u6-real-curl.txt (④⑥) | 통과 |
| 판정 9 동시 실행 `SKIP LOCKED` | evidence/20261002-2016-verifier-negative.txt (A절 `test_select_due_schedules_concurrent_sessions_skip_locked`), evidence/20261002-1500-u2-lock-negative.txt | 통과 |
| 판정 10 수동 강제(결정 C) | evidence/20261002-1950-u8-rows-1to10.txt (::test_run_briefings_schedule_id_forces_regeneration), evidence/20261002-1854-u6-real-curl.txt (②③⑤) | 통과 |
| 판정 11 패턴 재계산(결정 K) | evidence/20261002-1950-u8-rows-11to20.txt, evidence/20261002-2016-verifier-negative.txt (A절 `…recomputes_pattern_and_deletes_when_window_shrinks` — U8 에서 원문 값 비교 추가본) | 통과 |
| 판정 12 사실 세 출처(결정 F) | evidence/20261002-1950-u8-rows-11to20.txt, evidence/20261002-1641-u5-real-e2e.txt (`excluded_facts: 소속 not_fact_key`) | 통과 |
| 판정 13 같은 키 여러 행 | evidence/20261002-1950-u8-rows-11to20.txt (::test_build_briefing_input_keeps_only_latest_row_for_same_key) | 통과 |
| 판정 14 원칙7 부정 — 근거 없는 제안 `no_basis` | evidence/20261002-2016-verifier-negative.txt (A절), evidence/20261002-1604-u4-real-llm-after-fix.txt (케이스 C `no_basis` 실 LLM) | 통과 |
| 판정 15 원칙7 부정 — 감정·고민 표현 `forbidden_expression` | evidence/20261002-2016-verifier-negative.txt (A절 4건 + E절 목록 안 3건 거부·**목록 밖 1건 통과**), evidence/20261002-1600-u4-negative.txt | 통과(한계 §6-1) |
| 판정 16 원칙7 부정 — 한 줄 위반 `not_one_line`/`too_long` | evidence/20261002-2016-verifier-negative.txt (A절 + E절 80자 통과/81자 거부) | 통과 |
| 판정 17 근거 위조 `unknown_basis` 그 줄만 | evidence/20261002-2016-verifier-negative.txt (A절 `…rejects_only_the_line_with_fabricated_basis`), evidence/20261002-1600-u4-negative.txt | 통과 |
| 판정 18 근거 자격(결정 G) `basis_not_eligible` | evidence/20261002-2016-verifier-negative.txt (A절 + E절 eligible False 거부/True 통과) | 통과 |
| 판정 19 패턴 판정은 규칙(원칙6) `count_mismatch` → 템플릿 | evidence/20261002-2016-verifier-negative.txt (A절 2건, R-4 `…rejects_fabricated_pattern_key` 포함), evidence/20261002-1600-u4-negative.txt | 통과 |
| 판정 20 프롬프트 경계 문구 | evidence/20261002-2016-verifier-negative.txt (A절 `test_build_briefing_prompt_includes_boundary_sentence_and_no_relation_request`), app/briefing/compose.py | 통과 |
| 판정 21 템플릿 대체(결정 D) `JudgeUnavailable("timeout")` | evidence/20261002-2016-verifier-negative.txt (A절 + E절 ⑤), evidence/20261002-1700-u5-negative.txt (a) | 통과 |
| 판정 22 실패 격리(일정 2건 중 첫 건 DB 예외) | evidence/20261002-2016-verifier-negative.txt (A절 `…isolates_real_db_error…` `SELECT 1/0` DataError + `…isolates_failure…` RuntimeError), evidence/20261002-1650-u5-dberror-negative.txt, evidence/20261002-1700-u5-negative.txt (b) | 통과 |
| 판정 23 근거 기록(원칙9) trace 키·tokens | evidence/20261002-1950-u8-rows-21to27.txt (::test_run_briefings_records_full_trace_fields_with_generator_tokens), evidence/20261002-1641-u5-real-e2e.txt (keys 13종, tokens 739/95) | 통과 |
| 판정 24 푸시 없음(결정 J) `not_configured`, `Notifier` 인자 원문 없음 | evidence/20261002-2016-verifier-negative.txt (A절 `…calls_fake_notifier_once_without_raw_utterance` · `…response_never_contains_raw_utterance`), evidence/20261002-1950-u8-rows-21to27.txt | 통과 |
| 판정 25 주기 작업 스위치 꺼짐 0회 / 켜짐 ≥1·종료 취소 | evidence/20261002-2016-verifier-negative.txt (A절 + C절 스위치 `1` 복제본 FAIL `[1,1,1,…] == []`), evidence/20261002-1930-u7-negative.txt (b) | 통과 |
| 판정 26 주기 작업 내구성 | evidence/20261002-2016-verifier-negative.txt (A절 `test_scheduler_keeps_running_after_run_once_raises`), evidence/20261002-1930-u7-negative.txt (a) | 통과 |
| 판정 27 원문 불변(1·11행 전후) | evidence/20261002-2016-verifier-negative.txt (A절 `test_run_briefings_does_not_mutate_events` + `…recomputes_pattern…`), evidence/20261002-2000-u8-added-tests-negative.txt | 통과 |
| 판정 28 불변식 grep 전부 0건 | evidence/20261002-2016-verifier-rerun.txt ([1][2][3a][3b][5][6] 재실행), evidence/20261002-2016-verifier-negative.txt (A절 `test_selection_and_inputs_do_not_import_llm_or_embedding`) | 통과 |
| 판정 29 무변경 — alembic · tools_check 7/7 · diff 빈 출력 | evidence/20261002-2016-verifier-rerun.txt, evidence/20261002-1950-u8-alembic-check.txt, evidence/20261002-1950-u8-tools-check.txt | 통과 |
| 판정 30 전체 회귀 실패 0·skip 0·≥1627 | evidence/20261002-2016-pytest.txt (1721 passed, skipped 0), evidence/20261002-2000-u8-final-regression.txt | 통과 |

판정 표 30행 전부 통과. 01-plan 127행의 "≥1627" 은 FIX-016 기준선이고 실제 1721(U1~U8 +94)이다.

## 2-1. 계획과 달라진 점 판정 (위임 4항)
(`verify-impl.sh` 가 `## 2.` 다음 `## ` 까지를 수용 기준 표로 읽으므로 이 절은 최상위 절로 둔다 — 2차 FAIL 6 의 원인, §8)

| # | 달라진 것 | 원칙·D·S·수용 기준을 바꾸는가 | 근거·사용자 결정 | 판정 |
|---|----------|------------------------------|-----------------|------|
| (a) | U4 금지 표현 검사를 제안→**제안+요약 줄**로 확대, 목록 11→**14개**(`힘들`·`마음을`·`배려`) | 원칙7 경계를 **좁히는** 방향(더 많이 거부). S3.6 3행·R19 문장 불변. 수용 기준 불변 | 01-plan 결정 E 아래 "구현 중 변경(U4, 사용자 결정 2026-10-02)" 줄, 03-log U4 "④ 조치(사용자 결정 … '①만 지금 고치고 커밋')"·"조치 2(사용자 결정 … '마음을'·'배려' 추가 후 커밋')", `evidence/20261002-1601-u4-real-llm.txt`(케이스 D 요약 줄 "힘들어 보입니다" 통과) → `-1604-…-after-fix.txt`(같은 줄 `forbidden_expression` 거부, 새 제안 "마음을 이해하고 배려하는" 통과 관측) → 테스트 3건 추가(`…rejects_line_with_forbidden_expression_keeps_others`·`…about_their_feelings`·`…conjugated_himdeul`). 코드 `app/briefing/types.py` 목록 14개 주석에 사례 기록 | **인정**. 거부 범위가 커졌을 뿐 경계 정의는 그대로. 요약 줄 거부로 "기록된 사실의 재진술" 이 빠질 수 있다는 부작용(03-log U4 ④ 가 스스로 적음)은 제안이 아니라 줄 단위이므로 브리핑은 유지된다 |
| (b) | U5 `run_briefings` 시그니처 — 계획 `(session_factory, *, now, …)` → 구현 `(ctx, *, composer, notifier, schedule_id, trigger, lead_hours)` | S3.6 "수동 트리거 = 같은 함수" 는 판정 3행으로 그대로 성립. S3.2 툴 시그니처 무관(`run_briefings` 는 툴 7종 밖). D 카드 무관 | 02-plan-verify R-5 가 "U5 03-log 에서 한 문장으로 정한다" 고 요청, 03-log U5 "시그니처를 01-plan 75행과 다르게 한 점(R-5 처리, 위임 프롬프트가 지시한 결정)" 이유 3개(커밋은 호출자 몫·`SKIP LOCKED` 와 세이브포인트가 같은 트랜잭션·`after_record(ctx, …)` 와 같은 모양). `app/briefing/run.py` 모듈 docstring 에 같은 내용. `docs/RUNNING.md` 215행이 구현 시그니처를 적음 | **인정**. 01-plan 75행 원문은 그대로 남아 있어(계획 문서는 고치지 않는 관례) 읽는 사람이 03-log 를 봐야 한다 — §5 [권고] |
| (c) | U5 `SQLAlchemyError` — 처음엔 `after_record` 처럼 올림 → **일정 단위 격리**(연결 끊김·세션 비활성만 올림) | 01-plan 75행 "삼키지 않고 올림 — **단 세이브포인트 단위 격리를 먼저 시도**, 03-log 에 정한 방식을 남긴다" 의 허용 범위 안. 판정 22행 "DB 예외 주입" 과 오히려 더 맞음. S·D 무관 | 03-log U5 "SQLAlchemyError 격리로 변경(사용자 결정 2026-10-02, 메인 세션 구현)" — 1분 주기에서 한 일정의 반복 DB 오류가 나머지를 영원히 막는 위험. 테스트 `test_run_briefings_isolates_real_db_error_other_schedule_still_briefed`(`SELECT 1/0` → `DataError`) + 옛 동작으로 되돌리면 FAIL(`evidence/20261002-1650-u5-dberror-negative.txt`). verifier 재실행 A절 통과 | **인정**. `registry.md` 195·196행은 아직 "삼키지 않고 올린다" 로 적혀 있어 사실과 다름 — §5 [권고] |
| (d) | U6 `BriefingRunResult.session_id` 추가(응답 `run_id`) | 스키마 v2 무관(DB 열 아님, `alembic check` 무변경). 원칙9 를 **돕는** 방향(응답에서 trace 로 역추적) | 03-log U6 "`run_id` 를 그 실행의 `session_id` 와 연결하는 방법" — (a) 최신 trace 재조회 vs (b) 결과에 싣기 중 (b) 선택 이유. `BriefingRunResult(` 생성처가 `run.py` 한 곳임을 grep 으로 확인했다고 적음. 사용자 결정 줄은 없으나 위임 프롬프트가 "어떻게 얻을지 판단해 03-log" 로 위임 | **인정**(추가 필드, 기존 호출부 무영향 — U5 테스트 9건 그대로 통과) |
| (e) | U7 주기 루프 수준 예외를 **trace 없이 로그만**(01-plan 77행 "trace·로그로 남기고 삼킨다") | 원칙9 는 "판정"의 근거 기록 — 루프 수준 실패는 판정이 아니라 실행 실패. 일정 단위 실패는 `briefing_error` 로 이미 남는다. S3.6 은 trace 를 말하지 않는다 | 03-log U7 "01-plan 77행 … 'trace' 처리" — 이 catch 에 오는 것은 `run_briefings()` 격리를 뚫고 올라온 것(연결 끊김·`select_due_schedules` 실패·`session_scope()` 진입 실패)뿐이고, 그때는 세션이 이미 rollback·close 됐으며 DB 자체가 원인일 수 있어 새 세션으로 trace 를 쓰는 것도 실패할 수 있다. **사용자 결정 줄은 없다**(위임 프롬프트 지시). 03-log U8 인계 "운영" 항에 FIX 후보로 명시 | **조건부 인정** — 계획 문장과 다르지만 근거가 타당하고 범위를 좁히는 쪽. 완료 승인 때 사용자가 이 항을 봤다는 기록(승인 줄)이 있으면 닫힌다. P9-infra 전 "스케줄러 수준 실패 경량 trace" FIX 후보로 §6 |
| (f) | `briefing_error.stage` 5종(`select|patterns|briefing|compose|notify`) 중 **3종**(`briefing|compose|notify`) | 결정 I 어휘의 부분집합. 원칙9 충족(실패 일정·단계·예외명 기록). S·D 무관 | 03-log U5 "`briefing_error.output.stage` 어휘 범위" — `build_briefing_input()`(U3)을 수정하지 않고 한 번에 부르므로 `patterns`/`briefing` 을 바깥에서 구분할 수 없음(01-plan 32행 "기존 코드 import 만" 과 일관). `select` 는 일정별 루프 밖이라 격리 대상 일정이 없음. `app/briefing/run.py` 상수 3개 | **인정**. 단 `docs/RUNNING.md` 252행이 "`select`\|`compose`\|`notify` 3종" 이라고 **잘못** 적었다(코드는 `briefing`) — §5 [권고] |

## 2-2. 계획 범위·"하지 않는 것" 침범 여부 (위임 3항)

- 웹푸시 코드 없음: 불변식 [1] grep 0건(`-verifier-rerun.txt`), `requirements.txt` 변경 없음(`git diff --stat 36c288e -- . ':!docs'` 19파일 목록에 없음), `.env.example` 31~34행 VAPID 이름 줄 diff 0(R-3).
- `GET /briefings/...`·프론트 화면 없음: `git diff 36c288e -- app/api/routes.py` 에 `@router.post("/briefings/run")` 하나뿐.
- 스키마·툴 시그니처 무변경: `alembic check` 무변경, `tools_check` 7/7, `app/agent/gate.py` 의 `get_briefing` LLM 호출 불가는 `app/agent` diff 0 으로 그대로.
- `app/agent/`·`app/memory/`·`app/er/`·`app/tools/briefing.py` 무수정: diff 0줄. `inputs.py` 는 `detect_patterns`·`get_briefing` 을 import 해서 부르기만 한다(62·65행).
- 옛 자유 키 삭제·개명 없음: `inputs.py` 는 `PersonFact` 를 `select` 만 한다(불변식 [3b] 0건), 실 e2e 에서 `소속` 이 `excluded_facts(not_fact_key)` 로만 나타남.
- 다중 사용자·배포 구성 없음: `scheduler.py::default_run_once` 가 `app_user_id()` 한 사용자, `docs/RUNNING.md` 가 "스위치는 한 프로세스에서만" 을 적음.
- 고민 상담·A–B 관계: 프롬프트가 "이 인물 한 사람에 관한 내용만 … 다른 인물과의 관계는 언급하지 마라"(판정 20행), 입력 자체가 한 인물 것뿐(`build_briefing_input(ctx, schedule)`).

구현이 범위를 넘은 곳 없음. 03-log Refs 태그 8종(D11 D14 R12 R19 S3.1 S3.2 S3.5 S3.6)이 커밋에 전부 있음(§1 PASS 8건). 02-plan-verify 권고 처리: R-1 U2 03-log(커밋 전용 `db_engine` 픽스처, 잠금 제거 시 FAIL 확인 `-u2-lock-negative.txt`) · R-2 U7(`routes.py` `GET /health` docstring 보충, diff 에서 확인) · R-3 계획 수정으로 닫힘 · R-4 U4(`…rejects_fabricated_pattern_key`·`…fills_missing_pattern_with_template_sentence`) · R-5 (b) · R-6 U8 03-log 인계(`output.person_id → persons.user_id` 조인) · R-7 계획 수정으로 닫힘 — 7건 전부 처리됨.

## 2-3. 테스트가 실제로 실패 조건을 검사하는가 (원칙8)

구현 측이 남긴 "일부러 어긴 코드에서 FAIL" 증거 7건(`-u2-lock-negative`·`-u4-negative`·`-u5-negative`·`-u5-dberror-negative`·`-u6-negative`·`-u7-negative`·`-u8-added-tests-negative`)을 믿지 않고, verifier 가 **코드를 건드리지 않는 방법**으로 표본 4종을 다시 어긋나게 주었다(`-verifier-negative.txt` B~E절): 환경변수·스위치·설정값·입력을 바꾸면 해당 단언이 FAIL 하거나 결과가 뒤집히는 것을 확인했다(§3). 항상 통과하는 테스트는 표본에서 발견되지 않았다.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 verifier 가 직접 실행. 코드 무변경(실험 전후 `git diff --stat HEAD -- app tests` 빈 출력, 테스트 DB 잔여 행 0 — `-verifier-negative.txt` 끝).

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 금지 표현 — 제안 "기분·위로"·"힘들 거예요"·요약 줄 "스트레스" 거부, 다른 줄 유지 | `pytest tests/test_briefing_compose.py::…forbidden_expression ::…keeps_others ::…about_their_feelings ::…conjugated_himdeul` + 스크래치 `verifier_neg_validate.py` ① | `evidence/20261002-2016-verifier-negative.txt` A·E절 — 3건 `['forbidden_expression']` |
| 금지 표현 — **목록 밖** "슬퍼하는 민수를 다독여 주세요" | 같은 스크립트 ② | E절 `kept=True reasons=[]` — 통과한다(결정 E 한계 실증, §6-1) |
| 제안 길이 경계 80/81자 | 같은 스크립트 ③ | E절 `[len 80] kept=True / [len 81] ['too_long']` |
| 근거 자격 — eligible=False 사실뿐 | 같은 스크립트 ④ | E절 `['basis_not_eligible']` / True 면 통과 |
| 지난 일정 `T−1s`·`T+24h+1s`·이미 브리핑 제외, `T+0`·`T+24h` 포함, 오름차순 | 스크래치 `verifier_neg_db.py`(테스트 DB, 롤백) | D절 `lead_hours=24 -> ['T+0','T+24h']` |
| 창 경계가 민감한가 — `lead_hours` 23.9999 / 24+1s | 같은 스크립트 | D절 `23.9999 -> ['T+0']`, `24+1s -> [… 'T+24h+1s']` |
| 다른 사용자 — 기본 모드 0건 / 지정 모드 404 / `briefed_at` 불변 | A절 4건 + D절 `other user -> []` | A절 34 passed; 실서버 `evidence/20261002-1854-u6-real-curl.txt` ④⑥ |
| 404 테스트가 소유를 실제로 검사하는가 | `APP_USER_ID=other-user pytest tests/test_api_briefings.py::test_run_briefings_other_user_schedule_id_returns_404` | B절 `assert 200 == 404` **1 failed**(기대대로) |
| 템플릿 대체 — `JudgeUnavailable("timeout")` → `composer="template"`, 제안 null, `briefed_at` 유지, `fallback_reason` | A절 `test_run_briefings_falls_back_to_template_on_judge_unavailable` + E절 ⑤ | A절 통과; E절 `[template] suggestion=None tokens=(0, 0)` |
| DB 오류 일정 단위 격리 — `SELECT 1/0`(DataError) 첫 건만 되돌림, 둘째 건 브리핑, `briefing_error` 1행 | A절 `…isolates_real_db_error…`·`…isolates_failure…` | A절 통과; 옛 동작으로 되돌리면 FAIL `evidence/20261002-1650-u5-dberror-negative.txt` |
| 스위치 꺼짐 → 루프 미기동(호출 0) / 잘못된 값 → 기동 실패 | A절 `test_scheduler_disabled_by_default…`·`test_invalid_switch_value_fails_app_startup` | A절 통과 |
| "꺼짐" 단언이 스위치에 민감한가 | 스크래치 `test_verifier_neg_scheduler.py`(같은 본문, 스위치 `1`) | C절 `assert [1, 1, 1, …] == []` **FAILED**(기대대로) |
| 응답·`Notifier` 인자에 `raw_utterance` 없음 | A절 `…response_never_contains_raw_utterance`·`…calls_fake_notifier_once_without_raw_utterance` | A절 통과; `-verifier-rerun.txt` [6] grep 3건 전부 docstring |
| `select.py`·`inputs.py` LLM·임베딩 미import(원칙6) | A절 `test_selection_and_inputs_do_not_import_llm_or_embedding` + `-verifier-rerun.txt` [3a] | 통과; 일부러 import 하면 FAIL `evidence/20261002-2000-u8-added-tests-negative.txt` |
| 동시 실행 `SKIP LOCKED` | A절 `test_select_due_schedules_concurrent_sessions_skip_locked` | 통과; 잠금 제거 시 `lock_timeout` FAIL `evidence/20261002-1500-u2-lock-negative.txt` |
| 실 LLM(verifier 는 부르지 않음 — evidence 판독) | — | `-1601-u4-real-llm.txt`: 케이스 C `no_basis` 거부, 케이스 D 요약 줄 "힘들어 보입니다" **통과**(빈틈) → `-1604-…-after-fix.txt`: 같은 줄 거부, 제안 "마음을 이해하고 배려하는" 통과 → 목록 추가. `-1641-u5-real-e2e.txt`: 2건 생성·+30h 미선정·2회차 0건·trace 키 13종. `-1854-u6-real-curl.txt`: 6경로. `-1940-u7-real-scheduler.txt`: 요청 없이 60초 뒤 `trigger=scheduler` 1건, 이후 두 주기 0건, 종료 깨끗 |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
아직 바꾸지 않았다(verifier 는 카드를 고치지 않는다). 메인 세션이 완료 승인 뒤 다음과 같이 바꾼다:

- **R12** `review-index.md` 20행 "결정완료" → **"구현완료(절반 — 브리핑 트리거 e2155f9…e2cca80: 1분 주기 작업 `app/briefing/scheduler.py`·수동 `POST /briefings/run`·같은 함수 `run_briefings`, `briefed_at` 기록; 푸시 구독 저장소는 P7-push 대기)"**. 01-plan 4행이 "R12(브리핑 트리거 절반 — 푸시 절반은 P7-push)" 로 정의했으므로 R12 전체를 "구현완료" 로 닫지 않는다.
- **R19** 27행 "해소(문서)" → **"구현완료(a2f032d — 프롬프트 경계 문장 + 코드 검증기 `validate_briefing`: 근거 필수·입력 실재·한 줄/80자·금지 표현 14개(요약 줄 포함); 한계: 목록 밖 표현은 통과 — P10 표본 점검)"**.
- 다음 카드 열은 그대로("S3.6 → P6-briefing, P7-push" / "원칙7 → S3.6").

## 5. registry.md 에 올린 산출물
U8(e2cca80)이 올렸고 verifier 가 행 존재·해시를 확인했다(§1 PASS "registry 에 P6-briefing 행 있음", `grep -n P6-briefing registry.md`):

- 새 행 11개(187~200행): `app/briefing/__init__.py`(e2155f9) · `types.py`(e2155f9) · `select.py`(db3c645) · `tests/test_briefing_select.py`(db3c645) · `inputs.py`(cfb55ea) · `tests/test_briefing_inputs.py`(cfb55ea) · `compose.py`(a2f032d) · `tests/test_briefing_compose.py`(a2f032d) · `run.py`(e037728) · `tests/test_briefing_run.py`(e037728) · `tests/test_api_briefings.py`(8589e37) · `scheduler.py`(a67692e) · `app/main.py` lifespan 행(a67692e) · `tests/test_briefing_scheduler.py`(a67692e).
- 비고 확장 6행: 38(`.env.example`) · 53(`app/settings.py`) · 62(`app/main.py`) · 64(`deps.py`) · 65(`routes.py`) · 66(`schemas.py`).

**메인 세션이 고칠 문서(verifier 미수정)** — 전부 [권고], 코드 무관:
1. `registry.md` 195행(`run.py`): "`SQLAlchemyError` 는 삼키지 않고 올린다 … `after_record` 와 같은 규약" → 사실과 다름(현재는 연결 끊김·세션 비활성만 올리고 나머지는 일정 단위 격리, 03-log U5 "SQLAlchemyError 격리로 변경"). 196행(`test_briefing_run.py`) "22행(… `RuntimeError`, `SQLAlchemyError` 아님)" 에 `…isolates_real_db_error…`(DataError) 추가 반영, 건수 9→10.
2. `registry.md` 188행(`types.py`)·190행(`test_briefing_select.py`) "금지 표현 11개" → 14개(U4 a2f032d 에 이미 포함).
3. `docs/RUNNING.md` 252행 "`stage`는 `select`\|`compose`\|`notify` 3종" → **`briefing`\|`compose`\|`notify`**(`app/briefing/run.py` `_STAGE_BRIEFING = "briefing"`). 같은 절 `skipped[]` 설명 "대상에서 빠지거나 실패한 일정" → 실제로는 **실패해 격리된 일정만** 들어간다(창 밖 일정은 `skipped` 에 없다 — `run.py` 는 예외 분기에서만 `skipped.append`).
4. `01-plan.md` 3행 "상태: 초안" · 75행 U5 시그니처 · 127행 "≥ 1627" — 계획 문서는 고치지 않는 관례라면 03-log 가 이미 대체 기록을 남겼으니 그대로 둬도 된다. 바꾼다면 75행 끝에 "(→ 03-log U5, `run_briefings(ctx, …)`)" 한 마디.
5. `docs/backlog.md` 80행 체크박스 `- [ ]` → `- [x]`(수용 기준 문장은 그대로).
6. `review-index.md` R12·R19(§4).
7. `CURRENT.md` `active: P6-briefing` → `none`, HANDOFF·journal DONE.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
05-remediation 열린 소견 0(해소 4, 전부 계획 단계). 이번 검토에서 **[필수] 소견 없음**. 아래는 전부 [권고] 또는 인계.

1. **[P10] 금지 표현 목록은 보조 방어** — 목록 밖 "슬퍼하는 … 다독여 주세요" 가 통과한다(§3 E절, verifier 실증). 실 LLM 4건 중 1건(케이스 D)이 두 번 연속 경계 근처 문장을 냈다. 1차 방어는 프롬프트·"근거 필수" 규칙. P10-final-eval 제안 문장 표본 점검(01-plan 결정 E 한계·03-log U8 인계 (c)).
2. **[P10] 패턴 "문장화"가 규칙 값 복사에 그침** — 실 LLM 5회 관측 중 4회(`-u4-real-llm`·`-after-fix`·`-u6-real-curl` ②·`-u7-real-scheduler`)가 `"3회 (날짜…)"` 그대로, 1회(`-u5-real-e2e`)만 문장. 원칙6 위반은 아니다(판정은 규칙, 숫자 일치) — 역할 분담이 빈 품질 문제. 프롬프트 손질은 별도 FIX 후보.
3. **[P7-push] 요약 줄이 `raw_utterance` 원문을 글자 그대로 옮긴다** — "민수는 고수를 진짜 싫어하더라"(U6·U7 실서버). 응답 스키마에 원문 필드는 없지만(불변식 충족) LLM 출력을 거쳐 나온다. 푸시 본문에 실리기 전에 P7 이 "원문 인용 금지" 를 프롬프트·검증 어디서 다룰지 정한다(03-log U6 관찰·U8 인계).
4. **[FIX 후보] `likes`/`dislikes` 뜻 반전 사실** — `likes=매운 음식`(원문 "못 먹어")이 DB 에 남아 있고 브리핑 근거 키에 `likes` 가 그대로 달린다(`-u5-real-e2e` 일정 2). 결정 G(ii) 소비 쪽 방어로 정반대 제안은 안 나왔으나(5회 관측 전부) 라벨 자체는 미해결. 손볼 자리 `app/agent/propose.py`·`app/memory/extract.py` 키 설명(01-plan 결정 G(iii), HANDOFF).
5. **[FIX 후보, P9 전] 스케줄러 수준 실패는 로그만** — §2-1 (e). 운영에서 자주 보이면 세이브포인트 없이 새 세션으로 `briefing_error` 한 줄을 쓰는 경량 trace(03-log U7 인계).
6. **[FIX 후보, 낮음] 지정 모드 `schedule_id` 가 잠긴 행이면 404** — `select.py` 지정 모드가 `with_for_update(skip_locked=True)` 를 쓰므로 주기 작업이 같은 행을 잡고 있는 1분 안에 `POST /briefings/run {"schedule_id": id}` 를 보내면 `one_or_none()` 이 None → `ScheduleNotFound` → 404 `not_found`. 존재하는 자기 일정인데 "없음" 으로 답한다. 수용 기준 밖·단일 사용자 전제라 지금은 문제가 드러나지 않지만 P8 버튼이 생기면 혼란. 대안: 지정 모드만 `skip_locked=False`(대기) 또는 409. 03-log 에 언급 없음.
7. **[인계] `briefing_error.stage` 3종**·`_MAX_FACT_SOURCES=2` 모듈 상수(`inputs.py`, 설정값 아님)·`BRIEFING_*` 3개는 코드 상수(환경변수 아님) — P8·P9 가 값을 바꾸려면 코드 수정.
8. **[인계] 개발 DB 확인용 행 잔존** — 사용자 `brief-u5-check`(인물 2·이벤트 5·사실 4·일정 4, `briefed_at` 채워짐) 가 개발 DB `relationship` 에 남아 있다(FIX-015 관례, 03-log U5). P8 화면 확인 때 재사용 가능.
9. **[문서] RUNNING.md `stage` 어휘 오기·`skipped[]` 설명, registry 195·196·188·190행** — §5.
10. **[P9-infra] 스위치는 한 프로세스에서만** — 워커 수만큼 루프가 늘어난다(`SKIP LOCKED` 로 중복 브리핑은 막음). `docs/RUNNING.md` 에 적혀 있음.
11. **[하네스 부채, L-nnn/FIX 후보] `verify-impl.sh` 5번 검사가 `###` 하위 절을 구분하지 못한다** — `## 2.` 뒤 첫 `## ` 까지의 모든 `|` 행을 수용 기준 행으로 읽어, 하위 절의 다른 표까지 증거 열 검사를 받는다(§1 2차 FAIL 6). 04-review 를 쓰는 쪽이 하위 절을 최상위로 올려 피했다. 스크립트의 awk 종료 조건을 `^##+ ` 로 넓히면 풀린다(수정은 사용자 승인 후 메인 세션, 양 OS 동작 확인).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
03-log U8 인계(P8 R-6·P7·P10·운영 4항)를 검토했고, 아래에 빠진 것을 보충한다.

- **공용 실행 함수** `app.briefing.run.run_briefings(ctx: ToolContext, *, composer: BriefingComposer, notifier: Notifier = NullNotifier(), schedule_id: int | None = None, trigger: "scheduler"|"manual", lead_hours: float = BRIEFING_LEAD_HOURS) -> BriefingRunResult`. **커밋은 호출자 몫**(함수는 `flush()` 까지). `ctx.session_id` 는 내부에서 `"briefing:<uuid4>"` 로 바꾼 파생 ctx 를 쓴다 — 호출자 ctx 는 수정되지 않는다. `ScheduleNotFound` 는 일정별 루프 밖에서 그대로 올라온다(호출자가 404).
- **응답/trace 모양**(P8 브리핑 화면이 읽을 것): `BriefingRunOut{run_id, generated_at, briefings[{schedule_id, person_id, composer:"llm"|"template", pattern_sentences[{key,sentence}], lines[{text, basis{fact_keys,event_ids}}], suggestion{text,basis}|null, push}], skipped[{schedule_id, reason}]}`. `run_id` == `agent_traces.session_id`. 주기 작업이 만든 브리핑은 응답이 없으므로 **`agent_traces(tool_name='briefing', step='briefing_compose')` 가 유일한 저장소**(결정 H(i)) — `user_id` 열이 없어 `output.person_id → persons.user_id` 조인 필요(R-6, 03-log U8). trace `output.used_facts[]` 는 `{key, fact_id, eligible}` 만 — `sources`(원문)는 trace 에 싣지 않았다(LLM 입력에만). 템플릿 대체 줄 형식은 `"{key}: {value}"` / `"{occurred_at} {type}: {content}"`(`template_briefing`).
- **의존성**(P8 테스트·P7 재사용): `app.api.deps.get_briefing_composer()`(지연 생성) · `get_now()`(고정 시계 오버라이드 — `app.dependency_overrides[get_now] = lambda: (lambda: NOW)`) · `build_briefing_ctx(session, now)`. `FakeBriefingComposer(table={schedule_id: raw dict}, fail=None)` 의 표 키는 **`schedule_id`**.
- **푸시 자리**(P7): `Notifier.notify(schedule: app.db.models.Schedule, composed: ComposedBriefing) -> str`. 호출 순서 입력 조립 → 생성/검증 → `notify` → `briefing_compose` trace, 전부 **같은 세이브포인트** 안 — `notify` 가 예외를 내면 그 일정의 `briefed_at` 도 되돌려진다(`stage="notify"`). 반환 문자열이 `push` 필드에 그대로 실린다. `briefed_at` 을 푸시 실패 시 남길지는 P7 결정(01-plan 결정 J 경계). 요약 줄 원문 인용 문제(§6-3).
- **설정값**: `BRIEFING_LEAD_HOURS=24`·`BRIEFING_INTERVAL_SECONDS=60`·`BRIEFING_SUGGESTION_MAX_CHARS=80` 코드 상수, `BRIEFING_SCHEDULER_ENABLED`(환경변수, 비움=꺼짐, `1`/`true` 만 켜짐, 그 밖 값은 **기동 실패**). `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개 코드 상수. `_MAX_FACT_SOURCES=2`.
- **주기 작업**(P9): `app/main.py::_lifespan` → `start_scheduler_task()`; 실행마다 `session_scope()` + `composer_from_env()`(키 없으면 그 주기만 `JudgeUnavailable` → 템플릿 대체, 서버는 안 죽음). 사용자는 `app_user_id()` 하나. 성공 시 uvicorn 로그는 조용하다 — 확인은 `schedules.briefed_at`·`agent_traces` 로. 종료 시 태스크 취소·대기(실서버 확인 `-u7-real-scheduler.txt`).
- **검증기 거부 사유 어휘**(P10 역추적용): `no_basis`·`unknown_basis`·`basis_not_eligible`·`not_one_line`·`too_long`·`forbidden_expression`·`count_mismatch`·`missing_pattern`(R-4 보강 — 거부가 아니라 템플릿 채움도 `rejected[]` 에 남김). `trace.output.rejected[].item.kind` = `pattern|line|suggestion`.
- **S3.6 창 공식**은 보충 줄(`now ≤ scheduled_at ≤ now + 24h`)이 권위 — P7 도 같은 함수를 쓰므로 창이 그대로 이어진다.
- **지정 모드 잠금 시 404**(§6-6) — P8 이 "지금 브리핑" 버튼을 만들면 1분 주기와 겹칠 때 404 를 볼 수 있다.

## 8. 기계 검증 3차 출력 (최종 — 그대로 붙인다)
명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P6-briefing | tee docs/wiki/packages/P6-briefing/evidence/20261002-2025-verify-impl-3.txt`
```
== verify-impl P6-briefing  (20261002-2025) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1721 passed, 1 warning in 15.42s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261002-2025-pytest.txt
PASS  compileall 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261002-2025-lint.txt
PASS  태그 P6-briefing 커밋 12 건 → evidence/20261002-2025-commits.txt
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D14
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.5
PASS  커밋에 태그 존재: S3.6
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록  ← 8589e37, evidence/20261002-2016-pytest.t
PASS  증거 확인:  해석 ㄱ — HTTP `POST /briefings/run` 200, 처리 경로가 주기  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  해석 ㄴ — 창 안 미브리핑 일정마다 `briefings[]` 1건(패턴 문장·요약 줄· ← evidence/20261002-1950-u8-rows-1to10.txt
PASS  증거 확인:  해석 ㄷ — `briefed_at == now`, 재실행 시 재선정 없음, 실패 일정은  ← evidence/20261002-1950-u8-rows-1to10.txt
PASS  증거 확인:  판정 1 ㄱ·ㄴ·ㄷ 양성(API 한 흐름)  ← evidence/20261002-1950-u8-rows-1to10.txt
PASS  증거 확인:  판정 2 ㄷ 재실행 멱등  ← evidence/20261002-1950-u8-rows-1to10.txt
PASS  증거 확인:  판정 3 ㄱ 같은 함수  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 4 창 경계 양성 `T+24h`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 5 창 경계 부정 `T+24h+1s`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 6 지난 일정 `T−1s` 선정 안 됨(결정 B(i), S3.6 보충 줄)  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 7 이미 브리핑됨  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 8 다른 사용자 격리 / API 404 `not_found`, `briefed_at ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 9 동시 실행 `SKIP LOCKED`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 10 수동 강제(결정 C)  ← evidence/20261002-1950-u8-rows-1to10.txt
PASS  증거 확인:  판정 11 패턴 재계산(결정 K)  ← evidence/20261002-1950-u8-rows-11to20.tx
PASS  증거 확인:  판정 12 사실 세 출처(결정 F)  ← evidence/20261002-1950-u8-rows-11to20.tx
PASS  증거 확인:  판정 13 같은 키 여러 행  ← evidence/20261002-1950-u8-rows-11to20.tx
PASS  증거 확인:  판정 14 원칙7 부정 — 근거 없는 제안 `no_basis`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 15 원칙7 부정 — 감정·고민 표현 `forbidden_expression`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 16 원칙7 부정 — 한 줄 위반 `not_one_line`/`too_long`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 17 근거 위조 `unknown_basis` 그 줄만  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 18 근거 자격(결정 G) `basis_not_eligible`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 19 패턴 판정은 규칙(원칙6) `count_mismatch` → 템플릿  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 20 프롬프트 경계 문구  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 21 템플릿 대체(결정 D) `JudgeUnavailable("timeout")`  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 22 실패 격리(일정 2건 중 첫 건 DB 예외)  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 23 근거 기록(원칙9) trace 키·tokens  ← evidence/20261002-1950-u8-rows-21to27.tx
PASS  증거 확인:  판정 24 푸시 없음(결정 J) `not_configured`, `Notifier` 인자 ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 25 주기 작업 스위치 꺼짐 0회 / 켜짐 ≥1·종료 취소  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 26 주기 작업 내구성  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 27 원문 불변(1·11행 전후)  ← evidence/20261002-2016-verifier-negative
PASS  증거 확인:  판정 28 불변식 grep 전부 0건  ← evidence/20261002-2016-verifier-rerun.tx
PASS  증거 확인:  판정 29 무변경 — alembic · tools_check 7/7 · diff 빈 출력 ← evidence/20261002-2016-verifier-rerun.tx
PASS  증거 확인:  판정 30 전체 회귀 실패 0·skip 0·≥1627  ← evidence/20261002-2016-pytest.txt (1721 
PASS  registry 에 P6-briefing 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20261002-2025-summary.txt ==
```
3차 pytest `evidence/20261002-2025-pytest.txt`: 1721 passed, **skipped 0**(`skipped|SKIPPED` 0건). 세 번(2016·2024·2025) 모두 같은 수.

결과: 완료
승인: 사용자 (2026-10-02) — §2-1 (e) "주기 작업 루프 수준 실패는 서버 로그에만 남는다(trace 없음)" 를 보고 수용, P9 배포 전 FIX 후보로 둔다
