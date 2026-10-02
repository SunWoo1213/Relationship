# P6-briefing · 계획 검증 (02-plan-verify)

대상: 01-plan.md (architect 초안 2026-10-02, 결정 A~K 사용자 확정 = 전부 권장안 — 계획서 150행 "확정" 줄) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-10-02 (1차 13:40~13:50 · 2차 재검증 13:59~, 새 컨텍스트)

읽은 것(위임 프롬프트가 지정한 절만): `specs/S3.6-briefing-push.md`·`S3.5-memory-promotion.md`·`S3.2-tools-v2.md`·`S3.1-schema-v2.md` 전문, `decisions/D14-pattern-window-config.md`·`D11-llm-provider-registry.md` 전문, `CLAUDE.md` 불변 원칙 1~9, `docs/proposal.md` 54~66행(2장 범위 표), `docs/resolution-plan.md` 193~199·233~237행, `docs/backlog.md` 77~89행, `review-index.md` R12·R19 행, `security.md` 전문, `packages/P5-loop/04-review.md`·`P6-memory/04-review.md`·`P4b-er-redesign/04-review.md` 결과 줄 + P6-memory §6·§7, `registry.md` 36~70행 + grep, `.claude/skills/devlog/SKILL.md` 정합성 점검표, `CURRENT.md`, `HANDOFF.md` grep. 코드는 읽기만: `app/main.py` 전문, `app/tools/briefing.py` 전문, `app/api/routes.py` 90~100행, `app/er/types.py` 45~57행, `tests/conftest.py` 120~130행, 그 밖은 grep(evidence `20261002-1340-verifier-fact-checks.txt`, 이하 "fc §n"). git 은 `bash .claude/scripts/gitlog.sh P6-briefing S3.6 R12 R19`(13:40).

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P6-briefing | tee docs/wiki/packages/P6-briefing/evidence/20261002-1340-verify-plan.txt`

### 1차 (이 문서를 쓰기 전 — `02-plan-verify 없음` FAIL 1 은 예고된 정상)
```
== verify-plan P6-briefing  (2026-10-02 13:40) ==
PASS  존재: docs/wiki/packages/P6-briefing/01-plan.md
FAIL  없음: docs/wiki/packages/P6-briefing/02-plan-verify.md
PASS  카드 존재: D11
PASS  카드 존재: D14
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 골격 — [backend-agent] 설정 상수 3개 + `briefing_scheduler
PASS  Refs 있음: - [ ] U2 대상 선정 — [backend-agent] `select_due_schedules(ctx, 
PASS  Refs 있음: - [ ] U3 브리핑 입력 조립 — [backend-agent] `build_briefing_input(c
PASS  Refs 있음: - [ ] U4 문장 생성기 — [backend-agent] `BriefingComposer.compose(
PASS  Refs 있음: - [ ] U5 실행 함수 — [backend-agent] `run_briefings(session_fact
PASS  Refs 있음: - [ ] U6 수동 트리거 — [backend-agent] `POST /briefings/run`. 요청 
PASS  Refs 있음: - [ ] U7 주기 작업 — [backend-agent] `app/briefing/scheduler.py`
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 전 행 실행, 전체
PASS  backlog 일치: `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-memory
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  registry 중복 없음: app/briefing/__init__.py
PASS  registry 중복 없음: app/briefing/types.py
PASS  registry 중복 없음: app/briefing/select.py
PASS  registry 중복 없음: app/briefing/inputs.py
PASS  registry 중복 없음: app/briefing/compose.py
PASS  registry 중복 없음: app/briefing/run.py
PASS  registry 중복 없음: app/briefing/scheduler.py
PASS  registry 중복 없음: tests/test_briefing_select.py
PASS  registry 중복 없음: tests/test_briefing_inputs.py
PASS  registry 중복 없음: tests/test_briefing_compose.py
PASS  registry 중복 없음: tests/test_briefing_run.py
PASS  registry 중복 없음: tests/test_api_briefings.py
PASS  registry 중복 없음: tests/test_briefing_scheduler.py
== 결과: FAIL=1 WARN=0 ==
```
1차 FAIL 1 은 `findings.py --source verify-plan` 으로 `F-ef47d1` 이 됐다(05-remediation). 메인 세션의 이전 실행 `evidence/20261002-1206-verify-plan.txt` 도 같은 FAIL 1 이다.

### 2차 (이 문서를 쓴 뒤 재실행 — `tee docs/wiki/packages/P6-briefing/evidence/20261002-1348-verify-plan-2.txt`)
```
== verify-plan P6-briefing  (2026-10-02 13:48) ==
PASS  존재: docs/wiki/packages/P6-briefing/01-plan.md
PASS  존재: docs/wiki/packages/P6-briefing/02-plan-verify.md
PASS  카드 존재: D11
PASS  카드 존재: D14
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 골격 — [backend-agent] 설정 상수 3개 + `briefing_scheduler
PASS  Refs 있음: - [ ] U2 대상 선정 — [backend-agent] `select_due_schedules(ctx, 
PASS  Refs 있음: - [ ] U3 브리핑 입력 조립 — [backend-agent] `build_briefing_input(c
PASS  Refs 있음: - [ ] U4 문장 생성기 — [backend-agent] `BriefingComposer.compose(
PASS  Refs 있음: - [ ] U5 실행 함수 — [backend-agent] `run_briefings(session_fact
PASS  Refs 있음: - [ ] U6 수동 트리거 — [backend-agent] `POST /briefings/run`. 요청 
PASS  Refs 있음: - [ ] U7 주기 작업 — [backend-agent] `app/briefing/scheduler.py`
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 전 행 실행, 전체
PASS  backlog 일치: `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-memory
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 2 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/briefing/__init__.py
PASS  registry 중복 없음: app/briefing/types.py
PASS  registry 중복 없음: app/briefing/select.py
PASS  registry 중복 없음: app/briefing/inputs.py
PASS  registry 중복 없음: app/briefing/compose.py
PASS  registry 중복 없음: app/briefing/run.py
PASS  registry 중복 없음: app/briefing/scheduler.py
PASS  registry 중복 없음: tests/test_briefing_select.py
PASS  registry 중복 없음: tests/test_briefing_inputs.py
PASS  registry 중복 없음: tests/test_briefing_compose.py
PASS  registry 중복 없음: tests/test_briefing_run.py
PASS  registry 중복 없음: tests/test_api_briefings.py
PASS  registry 중복 없음: tests/test_briefing_scheduler.py
== 결과: FAIL=0 WARN=1 ==
```
2차 FAIL 0 WARN 1. `findings.py --source verify-plan` 재실행으로 `F-ef47d1` 해소, WARN 은 `F-033bb1`(권고 — 행 3·4 의 보류를 센 파생 소견, H-1·H-2 가 닫히면 같이 사라진다). 05-remediation 열림 3(필수 2: `F-256944`·`F-4029df`), 해소 1.

### 3차 (2차 재검증 — 점검표 행 3·4 를 통과로 재판정한 뒤, `tee docs/wiki/packages/P6-briefing/evidence/20261002-1401-verify-plan-3.txt`)
```
== verify-plan P6-briefing  (2026-10-02 14:01) ==
PASS  존재: docs/wiki/packages/P6-briefing/01-plan.md
PASS  존재: docs/wiki/packages/P6-briefing/02-plan-verify.md
PASS  카드 존재: D11
PASS  카드 존재: D14
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 골격 — [backend-agent] 설정 상수 3개 + `briefing_scheduler
PASS  Refs 있음: - [ ] U2 대상 선정 — [backend-agent] `select_due_schedules(ctx, 
PASS  Refs 있음: - [ ] U3 브리핑 입력 조립 — [backend-agent] `build_briefing_input(c
PASS  Refs 있음: - [ ] U4 문장 생성기 — [backend-agent] `BriefingComposer.compose(
PASS  Refs 있음: - [ ] U5 실행 함수 — [backend-agent] `run_briefings(session_fact
PASS  Refs 있음: - [ ] U6 수동 트리거 — [backend-agent] `POST /briefings/run`. 요청 
PASS  Refs 있음: - [ ] U7 주기 작업 — [backend-agent] `app/briefing/scheduler.py`
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 전 행 실행, 전체
PASS  backlog 일치: `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-memory
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/briefing/__init__.py
PASS  registry 중복 없음: app/briefing/types.py
PASS  registry 중복 없음: app/briefing/select.py
PASS  registry 중복 없음: app/briefing/inputs.py
PASS  registry 중복 없음: app/briefing/compose.py
PASS  registry 중복 없음: app/briefing/run.py
PASS  registry 중복 없음: app/briefing/scheduler.py
PASS  registry 중복 없음: tests/test_briefing_select.py
PASS  registry 중복 없음: tests/test_briefing_inputs.py
PASS  registry 중복 없음: tests/test_briefing_compose.py
PASS  registry 중복 없음: tests/test_briefing_run.py
PASS  registry 중복 없음: tests/test_api_briefings.py
PASS  registry 중복 없음: tests/test_briefing_scheduler.py
== 결과: FAIL=0 WARN=0 ==
```
3차 FAIL 0 WARN 0. `bash .claude/scripts/findings.sh P6-briefing evidence/20261002-1401-verify-plan-3.txt --source verify-plan`(14:02) → "새 소견 0, 해소 1(`F-033bb1`), 열림 0 (필수 0)". 05-remediation: 열림 0, 해소 4(`F-ef47d1`·`F-256944`·`F-4029df`·`F-033bb1`). `F-256944`·`F-4029df` 는 source=review 라 findings 가 자동으로 닫지 않으며 verifier 가 재검증 명령 출력(`evidence/20261002-1359-reverify.txt`)을 근거로 직접 해소 처리했다.

FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.

### 이 판정이 만든 evidence
- `evidence/20261002-1340-verify-plan.txt` — 1차 기계 검증.
- `evidence/20261002-1340-verifier-fact-checks.txt` — 01-plan 의 해시·registry 행·함수명·행 번호·기준선 표본 대조 명령과 출력(§1~§17).
- `evidence/20261002-1340-verifier-hold-findings.txt` — 보류 소견 H-1·H-2 의 `findings.py` 입력(→ `F-256944`·`F-4029df`).
- `evidence/20261002-1359-reverify.txt` — 2차 재검증: H-1·H-2 재검증 명령·R-3 대조·새 충돌/CR 검사 명령과 출력(verifier 직접 실행).
- `evidence/20261002-1401-verify-plan-3.txt` — 3차 기계 검증(FAIL 0 WARN 0).

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 56~63행 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱". 01-plan 35행 "하지 않는 것": "**고민 상담·감정 대화·위로 문장, 인물 간(A–B) 관계 서술, 상담 페르소나, 음성, 네이티브 앱**(원칙7) — 제안은 기록된 사실·사건에서 나온 한 줄 행동뿐이다. 결정 E 의 코드 검증기가 이를 강제한다". 결정 E(191행) "인물 간 관계 서술을 막기 위해 제안 근거는 **이 인물 한 명의** 사실·이벤트로만 한정한다(입력 자체가 한 인물 것뿐)". 29행 화면 제외 "브리핑 조회 API·프론트 브리핑 화면(P8-frontend, 원칙5 화면 3개 고정)". 태그 필터: 산출물 표(43~65행)에 relation_tag 조건·필터 인자 없음. 기획서 포함 열 "만남 전 브리핑 생성" 이 이 패키지다. 제외 열 침범 없음 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1~4(ER): 01-plan 32행 "`app/agent/`·`app/memory/`·`app/er/` 수정 — 패턴 재계산은 `detect_patterns` 를 **import 해서 부르기만** 한다", 판정 29행 `git diff --stat 36c288e -- app/tools/briefing.py app/agent app/memory app/er` 빈 출력 — ER 코드·임계치·ask_user 에 손대지 않는다. 원칙5: 29행(행 1). 원칙6 CLAUDE.md "LLM은 패턴 문장화만" ↔ 01-plan 14행 "**패턴 판정은 규칙 그대로**(원칙6)", 73행 U3 "① `detect_patterns(ctx, person_id)`(결정 K — 기존 함수 그대로)", 249행 불변식 "`app/briefing/select.py`·`inputs.py` 는 `app.briefing.compose`·`app.er.judge`·`app.embedding` 을 import 하지 않는다 … `person_facts` 의 `pattern:*` 행을 `app/briefing/` 이 직접 쓰지 않는다", 판정 19행 `count_mismatch` → "패턴 행 value 는 생성기와 무관하게 규칙 값 그대로". D(i)·E(ii) 가 LLM 에 맡기는 것은 패턴 **문장**·요약 줄·제안 한 줄이고 패턴 **판정**이 아니다(S3.5 "LLM은 문장화만", P6-memory 01-plan 181행 결정 E "(ii) **P6-briefing**. 문장화는 … 패턴 **판정**과 분리돼야 한다(원칙6)") — 원칙6 안. 원칙7 경계 문장 CLAUDE.md "브리핑의 '제안'은 기록된 사실에서 도출되는 한 줄 행동 제안으로 한정한다. 감정·고민에 대한 대화는 하지 않는다" ↔ 결정 E(ii) 191행 검증기 4조건(근거 ≥1·입력에 실재·한 줄/상한·금지 표현)과 판정 14~16행(`no_basis`·`forbidden_expression`·`not_one_line`/`too_long`), 20행 프롬프트 경계 문구. 부정 테스트가 경계를 실제로 검사하는지: 14행은 근거 없는 제안을 `null` 로, 15행은 "민수의 기분을 먼저 위로해 주세요"(목록의 `기분`·`위로` 2개 포함)를 거부, 16행은 줄바꿈·상한 초과를 거부 — 세 행 모두 **거부가 안 일어나면 실패하는** 기대 출력이다. 한계는 193행이 스스로 적었다("목록은 완전하지 않다 … 경계 전체를 증명하지 않는다", P10 인계). 원칙8: 69행 "모든 테스트는 **실 키·네트워크 없이** 돈다(가짜 생성기·`NullNotifier`)", 74행 `FakeBriefingComposer`(표 기반·결정적), 결정 D(i) 템플릿 대체로 실패를 숨기지 않음, 리스크 절 263행 "자동 테스트는 전부 가짜 생성기다 … 품질은 U8 사용자 실행 1회로만 본다" 명시. 원칙9: 결정 I(225~228행) `briefing_run`·`briefing_compose`·`briefing_error` output 키 열거, 판정 23행 `tokens_in/out` = 생성기 사용량. 원칙1~3·4 의 임계치·ask_user 는 이 패키지가 건드리지 않는다(행 4) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 (2차 재판정 13:59 — 1차 13:50 판정은 H-1 로 막혀 있었다, 1차 근거 문장은 아래 그대로 둔다) | D14 "패턴 판정에 LLM 을 쓰지 않는다 / 기본값은 `app/settings.py` 한 곳 / 실제 쓴 기간·횟수를 패턴 trace(`memory_pattern`)에 기록" ↔ 01-plan 73행 "기존 함수 그대로, 자기 `memory_pattern` trace 를 남긴다", 32행 `app/memory/` 무수정, 판정 11행 `memory_pattern` `action=deleted` 1행(`app/memory/patterns.py` 148행 `action="deleted"` 실존, fc §4) — D14 충돌 없음. D11 "`JUDGES` 가 하나만 … `caller_from_env()` 는 표·스위치를 `judge.py` 에서 import 한다(자체 표 금지) … 구조화 출력 실패는 기존 오류 어휘 6종(`timeout/rate_limit/api_error/connection/schema/out_of_range_id`)만 쓴다 — 어휘를 늘리지 않는다" ↔ 01-plan 74행 "`select_provider`·`call_with_error_mapping` import(D11 — 자체 선택 로직 금지, 등록표는 `FACT_EXTRACTORS` 와 같은 모양으로 새로 둔다)", 139행 "오류 어휘 `app/er/judge.py` 기존 6종 … 새 오류 클래스를 만들지 않는다". 등록표를 새로 두는 것은 `app/memory/extract.py` 620행 `FACT_EXTRACTORS`(P6-memory 승인 선례, "스키마가 달라 표 자체는 새로 둔다")와 같은 방식이고 선택 로직은 `select_provider`(judge.py 785행) 재사용이라 D11 의 "자체 선택 로직 금지" 안이다. **H-1(`F-256944`)**: 그러나 74행 U4 와 118행 판정 21행이 흉내 낼 오류로 `JudgeTimeout`(기존 오류 어휘)" 을 적었는데 그 클래스는 저장소에 **없다**(fc §5: `grep -rn JudgeTimeout app tests` 0건). 실제 어휘는 `app/er/types.py` 49행 `class JudgeUnavailable(Exception)` 하나에 메시지 문자열 `"timeout"`(`judge.py` 232행 `raise JudgeUnavailable("timeout")`)이다. 글자 그대로 구현하면 139행·D11 "어휘를 늘리지 않는다" 와 모순이고, 판정 21행은 존재하지 않는 이름으로는 기계적으로 실행할 수 없다. 문서 두 곳의 이름을 `JudgeUnavailable("timeout")` 로 고치면 풀린다(§3). **→ 2차 재검증(`evidence/20261002-1359-reverify.txt` "F-256944")**: 01-plan 에 `JudgeTimeout` **0건**, `JudgeUnavailable("timeout")` 1건(118행 판정 21행: "`JudgeUnavailable("timeout")`(기존 오류 어휘 — `app/er/types.py` 49행, `judge.py` 232행. 새 클래스 없음)") — 인용한 행 번호가 현재 코드와 일치(`grep -n "^class Judge" app/er/types.py` → 49행, `grep -n 'JudgeUnavailable("timeout")' app/er/judge.py` → 232·625행). 코드 무변경(`git diff --stat 36c288e -- app tests` 빈 출력). 이제 판정 21행은 D11 "구조화 출력 실패는 기존 오류 어휘 6종만 … 어휘를 늘리지 않는다" 와 01-plan 139행 "새 오류 클래스를 만들지 않는다" 에 맞고, 가짜 생성기가 그 예외를 던지는 테스트로 기계 실행 가능하다. D 카드 충돌 없음 |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 (2차 재판정 13:59 — 1차 13:50 판정은 H-2 로 막혀 있었다, 1차 근거 문장은 아래 그대로 둔다) | S3.1 "`schedules(id, person_id, title, scheduled_at, briefed_at)`" ↔ 01-plan 30행 "스키마 v2 변경·마이그레이션 — S3.1 이 권위다. 브리핑 저장 테이블(결정 H(ii))이나 `schedules` 컬럼 추가를 고르면 … CR 이 먼저다", 결정 H(i) 확정 "응답 + `briefing_compose` trace output 에만 — 스키마 무변경", 판정 29행 `alembic check` → "No new upgrade operations detected." — **H(i) 는 S3.1 을 바꾸지 않는다**. `agent_traces(id, session_id, step, tool_name, input, output, tokens_in, tokens_out, created_at)` 의 기존 열만 쓰고(결정 I), `session_id` NOT NULL(`app/db/models.py` 252행)을 `"briefing:<uuid4>"` 로 채운다. 원칙8·9 와의 관계: 생성 결과가 trace 에 남으므로 "모든 판정에 근거"(원칙9)는 충족되고, 재현성은 LLM 출력 자체가 아니라 입력(`used_facts`·`event_ids`)과 검증기 거부 사유가 남는 것으로 지킨다 — 217행이 한계("trace 를 지우면 브리핑도 사라진다")를 P6-memory 결정 B(ii) 와 같은 리스크로 적었다. S3.2 "`get_briefing` `(person_id, schedule_id?) → Briefing` `briefed_at` 기록" ↔ 31행 "툴 7종 시그니처·동작 변경 — `get_briefing(person_id, schedule_id?)` 는 S3.2 그대로 쓴다(`tools_check` 7/7 유지)", 133행 "**그대로 호출** … 같은 조회·기록을 새로 쓰지 않는다"(`app/tools/briefing.py` 64행 시그니처·148행 `schedule_row.briefed_at = now` 실존, fc §4). 임계치 2개·ask_user 비동기: 이 패키지는 ER·ask_user 를 호출하지 않는다(산출물 표 43~65행에 `app/er`·`app/tools/questions.py` 없음, `app/agent/gate.py` 125행 `NOT_CALLABLE_BY_LLM` 에 `get_briefing` 이 그대로 — 31행). S3.5 "LLM은 문장화만 / 원문은 어떤 경우에도 삭제하지 않는다" ↔ 248행 불변식·판정 27행 `events` 불변. S3.6 2행 "수동 트리거 `POST /briefings/run` = 같은 함수" ↔ 판정 3행 "두 경로 모두 같은 `run_briefings` 객체". S3.6 3행 경계 ↔ 행 2. S3.6 4행 "VAPID 키는 … 코드·저장소에 두지 않는다" ↔ 247행 grep 0건. **H-2(`F-4029df`)**: S3.6 1행·`docs/resolution-plan.md` 197행 "`scheduled_at - now() ≤ 24h AND briefed_at IS NULL`" 은 상한만 있어 지난 일정도 글자 그대로 만족하는데, 결정 B(i) 확정안 `now ≤ scheduled_at ≤ now+24h` 는 하한을 더해 선정 집합을 **줄인다** — 해석이 아니라 명세의 좁힘이다. 결정은 타당하다(CLAUDE.md "만남 직전에 필요한 맥락만 요약", `app/tools/briefing.py` 29~30·124행 `upcoming_schedules` 가 이미 `scheduled_at >= now` 로 과거 제외 — fc §17). 기획서 본문에 공식이 없고(fc §12: `docs/proposal.md` 에 `24h`·`scheduled_at - now` 0건), D 카드 없음, R12·수용 기준 불변이므로 **CR 은 아니고 S3.6 카드 한 줄 + resolution-plan 197행 주석 한 줄 보충**이면 풀린다(§3). 01-plan 170행이 스스로 같은 판단을 요청했다. **→ 2차 재검증(`evidence/20261002-1359-reverify.txt` "F-4029df")**: `S3.6-briefing-push.md` 6행 "보충(2026-10-02, P6-briefing 결정 B(i) 사용자 확정): 창은 `now ≤ scheduled_at ≤ now + 24h` — **이미 지난 일정은 제외**한다 … `get_briefing` 의 `upcoming_schedules`(`scheduled_at >= now`)와 같은 방향", `resolution-plan.md` 198행 "(2026-10-02 보충: 창은 `now ≤ scheduled_at ≤ now + 24h` — 이미 지난 일정은 제외 … 위 공식은 원 결정 기록.)" — `git diff --numstat` 두 파일 모두 추가 1/삭제 0, 원 공식 줄은 그대로. 01-plan 103행(판정 6행) "선정 안 됨(결정 B(i) 확정, S3.6 카드 보충 줄)", 조건문 0건. 보충이 인용한 선례 `app/tools/briefing.py` 124행 `.where(Schedule.scheduled_at >= now)` 실존. 새 충돌 없음: 같은 공식을 적은 다른 S/D 카드 없음(grep — D02 의 "미답변 24h 만료" 는 pending_questions 만료라 무관), S3.6 은 P7-push 에도 적용되는데 P7 은 "같은 함수"(S3.6 7행)를 쓰므로 창이 좁아진 것이 그대로 이어져 어긋남이 없다. CR 재확인: `docs/proposal.md` 공식 0건, 기획서·D 카드·CLAUDE.md·backlog·review-index 무변경(`git diff --stat` 빈 출력) — R12 "브리핑 트리거·푸시 구독 저장소 없음 / 결정완료" 행도 그대로. 이제 결정 B(i) = S3.6 명세이며 S 카드와 일치한다 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 80행 "의존: P5". `packages/P5-loop/04-review.md` 196행 "결과: 완료"(완료 처리 커밋 `f9bfba7` "docs(P5-loop): 완료 검토 결과와 완료 처리" — gitlog 13:40·fc §1). `packages/P6-memory/04-review.md` 152행 "결과: 완료"(`94373cc` "docs(P6-memory): … 완료로 닫는다", fc §1) — 01-plan 10행이 그 §7 인계 4항(`detect_patterns` 재호출·세 출처·unlinked·trace 상태)을 옮겨 적었고 §7 원문 "`detect_patterns(ctx, person_id) -> PatternResult` 는 순수 SQL·LLM 0 — **P6-briefing 이 브리핑 직전에 다시 부른다**" 와 일치. P4 게이트 `packages/P4b-er-redesign/04-review.md` 144행 "결과: 완료"(기계 검증 `PASS  P4 게이트 통과 (P4b-er-redesign)`). 시작 해시 `36c288e` = dev2 HEAD = origin/dev(gitlog "dev 36c288e [origin/dev]") — 01-plan 7행의 "스냅샷 dev 표시 `3c0f0d9` vs HANDOFF 36c288e" 는 HANDOFF 8행 "origin/dev = `36c288e`" 쪽이 지금 상태와 같다. 이 태그 기존 커밋 `7c94aad`(P2-tools U7 get_briefing, gitlog "태그 'P6-briefing' 커밋") 만 코드이고 R12·R19 태그 커밋 0건 — 01-plan 9행 "코드는 없다" 와 일치. `CURRENT.md` 3~4행 `active: none` / `frozen: none`(fc §15). 미커밋 변경은 `HANDOFF.md`·`journal.md`·이 패키지 폴더뿐(gitlog "커밋 안 된 변경") — 8행 "제품 코드는 0" 일치 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 80행 "수용기준: `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록" ↔ 01-plan 82행 "- `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록"(fc §16 두 줄 나란히, 기계 검증 `PASS  backlog 일치`). 해석 표 ㄱ~ㄷ(88~90행)은 새 기준을 더하지 않고 세 구절을 각각 판정 가능한 문장으로 바꾼 것이며 판정 표 1~3행이 그 셋을 직접 덮는다. `docs/resolution-plan.md` 235행 P6 표 행의 수용 기준도 같은 문장 |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 `PASS  Refs 있음` 8건(U1~U8). 각 단위가 패키지 태그 `P6-briefing` + S3.6 을 포함하고, 닫는 검증 R12 는 U1·U2·U5·U6·U7·U8, R19 는 U4·U8, D11 은 U4, D14 는 U3 에 붙어 4행 태그 줄(R12 R19 / D14 D11 / S3.6 S3.2 S3.5 S3.1 / 원칙5~9)과 어긋나는 단위가 없다. 선행 태그 커밋: `7c94aad`(P6-briefing·S3.6 두 태그 모두에 걸림, gitlog) — 01-plan 9행이 같은 해시를 적었다. 단위마다 판정 명령·evidence 파일명이 있어 커밋 하나 크기로 닫힌다(U4 가 가장 크지만 모듈 하나 `compose.py` 에 머문다) |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | security §1 "`.env.example`에 **이름만** 적는다" ↔ 01-plan 64행 "`BRIEFING_SCHEDULER_ENABLED=`(값 비움 … 비밀 없음)"; §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 227행 "프롬프트 전문·키는 기록하지 않는다(security §1)", 결정 I `llm:{provider, model}` 만. §4 "로컬 서버 이외로 데이터 전송 금지" ↔ 결정 J(i) `NullNotifier` "아무것도 보내지 않고 `"not_configured"` 반환", 판정 24행 "외부 전송 0", 28행 "웹푸시 … `pywebpush` 같은 의존성을 추가하지 않고"(`requirements.txt` 에 apscheduler·pywebpush 0건, fc §11). §5 "모든 조회는 `user_id` 조건" ↔ 72행 U2 "`Person.user_id == ctx.user_id`", 137행 `_owned_person` 재사용(`app/tools/persons.py` 371행 실존) "새 소유 검사 함수 금지", 판정 8행 다른 사용자 404. 삭제: 248행 불변식 "원문(`events`) 삭제·수정 금지" grep + 판정 27행, 34행 옛 자유 키 행 "삭제·이름 바꾸기" 하지 않음. 응답에 `raw_utterance` 미포함(76행·252행, `EventOut` 이 원문을 담지 않는 기존 결정 `app/tools/types.py` 71~73행). 위반 없음. 표기 지적 하나는 권고 R-3(28행 "VAPID 문자열을 … `.env.example` 어디에도 쓰지 않는다" — 실제로는 `.env.example` 31~34행에 P7 용 VAPID **이름** 줄이 이미 있다, fc §10; 이름만이라 §1 위반은 아니고 문장이 사실과 다를 뿐) |

### 위임 프롬프트가 따로 판정을 요구한 5항

1. **결정 B(i) — 해석인가 변경인가.** **변경(명세 좁힘)**이다 — 행 4 H-2. 필요한 것은 S3.6 카드 한 줄 보충 + `docs/resolution-plan.md` 197행 주석 한 줄(CR-002 가 §3.5 에 주석을 단 방식). CR 은 필요 없다: 기획서 본문에 공식 없음(fc §12), D 카드 없음, R12 검증 항목·수용 기준·툴 시그니처 불변. 결정 내용 자체는 기획 의도·`get_briefing` 선례와 맞다.
2. **`app/main.py` lifespan 추가 vs "lifespan 두지 않음".** 그 결정의 소재는 세 곳이고 모두 **리스크 A(엔진 미생성)의 따름 문장**이지 lifespan 자체의 금지가 아니다(fc §6): `app/main.py` 10~11행 "접속 확인은 `GET /health` 가 요청이 왔을 때만 한다. lifespan 훅도 두지 않는다(접속 확인은 lifespan 의 일이 아니다)", `app/api/routes.py` 96행 "`create_app()`/lifespan 은 엔진을 만들지도 접속을 확인하지도 않는다", `packages/P2-tools/01-plan.md` 145행 "리스크 — `TestClient` 와 앱 lifespan 이 실 엔진을 만든다 … `create_app()` 은 엔진을 만들지 않는다(lifespan 에서 접속 확인을 하지 않는다)". 01-plan 62행은 스위치 기본 꺼짐으로 "import·기동 시 엔진 생성 없음은 그대로" 를 유지하고 U7 판정에 `tests/test_api.py`(262~274행 `_counting_get_engine` 리스크 A 테스트, fc §7)를 넣어 그 불변식을 회귀로 지킨다. **충돌 없음**. 다만 고칠 문장이 `main.py` 한 곳만 적혀 있는데 `routes.py` 96행도 같은 말을 하므로 함께 손봐야 한다(R-2).
3. **결정 H(i)(trace 에만 저장).** S3.1 무변경(행 4), 원칙9 충족, 원칙8 은 입력·거부 사유 보존으로 지키되 한계(trace 정리 시 소실)를 217·261행이 적었다. 충돌 없음. `agent_traces` 에 `user_id` 가 없어 P8 이 사용자별 브리핑을 읽으려면 `output.person_id → persons.user_id` 조인이 필요하다는 점은 270행 인계에 포함돼 있지 않다(R-6).
4. **결정 D(i)·E(ii) 와 원칙6·7.** 행 2 — 충돌 없음, 판정 14~16·19·20행은 거부가 안 일어나면 실패하는 부정 테스트다. 빠진 부정 케이스 하나: 생성기가 **입력에 없는 패턴**을 지어내는 경우(`pattern_sentences[].key` 가 입력 `pattern:*` 밖) — 19행은 숫자 불일치만 본다(R-4).
5. **사실 주장 표본 대조**(fc §1~§17): 해시 10개(`36c288e`·`f9bfba7`·`94373cc`·`7c94aad`·`d67d084`·`7564c5d`·`6e7b286`·`26dcd22`·`3c0f0d9`·`f05d017`) 전부 실존(§1). registry 행 번호 10곳(38·51·52·53·56·57·58·61·64·177) 전부 일치(§2), registry 중복 grep 0건(§3). 함수·상수 17개 실존(§4: `get_briefing` 64행·`detect_patterns` 92행·`_owned_person` 371행·`select_provider` 785행·`call_with_error_mapping` 221행·`FACT_EXTRACTORS` 620행·`extractor_from_env` 627행(01-plan "614~632행" 안)·`get_fact_extractor` 241행·`session_scope` 79행·`app_user_id` 345행·`user_timezone` 325행·`PATTERN_KEY_PREFIX` 199행·`FACT_KEYS` 356행·`TRACE_MAX_STRING` 86행·`ToolContext` 92행(01-plan "91~106행")·`BriefingOut` 132행(01-plan "132~161행")·`NOT_CALLABLE_BY_LLM` 에 `get_briefing`). `TestClient(` 4파일 9곳(§8: 3+2+3+1) = 258행. 기준선 1627(§9) = 판정 30행. FIX-015 증거 trace 181 `likes=매운 음식`(§14) = 207행. 선행 결과 줄 3개·CURRENT(§15). **불일치 1건**: `JudgeTimeout`(§5) → H-1.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

- **H-1 [필수] `F-256944` — 01-plan 74행(U4)·118행(판정 21행)의 `JudgeTimeout` 은 존재하지 않는 클래스다.** 근거: fc §5(`grep -rn JudgeTimeout app tests` 0건; `app/er/types.py` 49행 `class JudgeUnavailable(Exception)`; `judge.py` 232·625행 `raise JudgeUnavailable("timeout")`). 01-plan 139행 "새 오류 클래스를 만들지 않는다" 및 D11 "어휘를 늘리지 않는다" 와 모순이 되고 판정 21행이 기계적으로 실행 불가. **풀리는 조건**: 두 곳의 이름을 `JudgeUnavailable("timeout")` 로 바꾼다(계획 문서 수정, 코드 무변경). 재검증 명령은 05-remediation `F-256944` "재검증" 에 있다.
- **H-2 [필수] `F-4029df` — 결정 B(i) 는 S3.6 1행·resolution-plan 197행 공식의 해석이 아니라 하한을 더한 명세 좁힘이다.** 근거: 행 4·위 5항-1, fc §12·§17. **풀리는 조건**(메인 세션 — verifier 는 카드를 고치지 않는다): ① `docs/wiki/specs/S3.6-briefing-push.md` 1행 뒤에 한 줄 "창은 `now ≤ scheduled_at ≤ now + 24h`(지난 일정 제외 — P6-briefing 결정 B(i), 2026-10-02 사용자 확정). `get_briefing` 의 `upcoming_schedules` 와 같은 방향". ② `docs/resolution-plan.md` 197행 끝에 같은 뜻의 괄호 주석 한 줄. ③ 01-plan 103행(판정 6행) 기대 출력을 "선정 안 됨" 으로 확정 표기. CR 불필요(§2 행 4 근거). U2 커밋 전이면 되므로 승인 커밋에 함께 넣을 수 있다.
- `F-ef47d1` [필수] "02-plan-verify 없음" — 이 문서 작성으로 해소 예정(2차 기계 검증에서 확인).

### 재검증 이력 (2차, 2026-10-02 13:59 — verifier fable, 새 컨텍스트)

사용자가 보류 조치와 재검증을 승인했고 메인 세션이 **문서만** 고쳤다(05-remediation 해결 단계 표). 그 설명을 믿지 않고 파일을 직접 대조했다 — 명령과 출력 전체는 `evidence/20261002-1359-reverify.txt`.

- **H-1 `F-256944` → 해소.** 01-plan `JudgeTimeout` 0건 / `JudgeUnavailable("timeout")` 1건(118행). 인용한 `types.py` 49행·`judge.py` 232행은 현재 코드와 일치. 코드 무변경. 05-remediation 해결 단계 표의 "74행 은 위치 오기" 주장은 **증거로 확정할 수 없다**(01-plan 미추적 → 이력 없음, 1차 fc §5 가 01-plan 자체의 `grep -n` 을 남기지 않았다 — 1차 verifier 의 기록 누락). 현재 74행에는 `Judge` 문자열이 없고 해소 조건(없는 이름 0건)은 어느 쪽이든 충족되므로 판정에 영향 없음. 점검표 행 3 → 통과.
- **H-2 `F-4029df` → 해소.** S3.6 6행·resolution-plan 198행 보충 줄 각 1건, 둘 다 추가 1/삭제 0(원 공식 보존). 01-plan 103행 "선정 안 됨" 확정, 조건문 0건(R-7 도 함께 닫힘). **새 문제 검사**: ① 같은 공식을 가진 다른 S/D 카드 없음(D02 "미답변 24h 만료" 는 무관). ② S3.6 의 적용 범위 P7-push — "같은 함수" 를 쓰므로 창 좁힘이 그대로 이어지고 P7 쪽에 별도 결정이 필요하지 않다. ③ CR 조건 — 기획서 본문 공식 0건, `docs/proposal.md`·`docs/wiki/decisions`·`CLAUDE.md`·`docs/backlog.md`·`review-index.md` 무변경(`git diff --stat` 빈 출력), R12 행·수용 기준 불변 → **CR 불필요 유지**. ④ 보충이 인용한 선례 `app/tools/briefing.py` 124행 실존. 점검표 행 4 → 통과.
- **R-3 → 닫힘.** 01-plan 28행이 "VAPID 키 값을 코드·문서·`.env.example` 어디에도 쓰지 않으며 `.env.example` 31~34행의 기존 P7 용 빈 이름 줄(`VAPID_PUBLIC_KEY=` 등)은 건드리지 않는다" 로 바뀌어 `.env.example` 31~34행 실제 내용(`VAPID_PUBLIC_KEY=`·`VAPID_PRIVATE_KEY=`·`VAPID_SUBJECT=mailto:you@example.com` — reverify.txt)과 일치. 행 8 판정 변화 없음(원래 통과).
- **남는 표기(판정에 영향 없음, 수정 불요)**: 01-plan 150행 "S3.6 해석 여부는 verifier 판정"·170행 "verifier 가 02-plan-verify 에서 … 판정해야 한다"·262행 리스크 "verifier 판정 필요" 는 이 재검증으로 답이 났다(변경 → 카드 보충 완료). 결정 기록이므로 그대로 둔다. 72행 U2 의 "결정 B 의 창(권장: …)" 도 150행 "권장 = 확정" 에 의해 확정 값이다.
- 기계 검증 3차는 §1 에 붙였다. 1차 판정 문장(행 3·4 근거 열·§3 H-1/H-2·§4 1차 줄)은 지우지 않았다.

### 권고 (착수를 막지 않는다 — 번호 R-1~)

- **R-1 [권고] 판정 9행(동시 실행 `SKIP LOCKED`)은 기존 `db_session` 픽스처로는 쓸 수 없다.** `tests/conftest.py` 120~130행(fc §13): 바깥 트랜잭션 + SAVEPOINT, 끝나면 항상 rollback. 커밋되지 않은 일정 행은 **다른 커넥션의 두 번째 세션에 보이지 않으므로** "세션 두 개가 같은 순간 `select_due_schedules`" 는 같은 행을 두고 경쟁할 수 없다. 조치: U2 03-log 에서 방식을 정한다 — 예: `db_engine` 으로 커밋하는 전용 픽스처(테스트 끝에 그 인물·일정만 명시 삭제) 또는 같은 커넥션 두 세션 대신 두 커넥션 + 커밋. "같은 커넥션 두 세션" 은 잠금을 검사하지 못하므로 증거가 아니다.
- **R-2 [권고] lifespan 문장은 `app/api/routes.py` 96행에도 있다.** 01-plan 62행은 `app/main.py` docstring 만 고친다고 적었다. 같은 커밋(U7)에서 `routes.py` 96행 "`create_app()`/lifespan 은 엔진을 만들지도 접속을 확인하지도 않는다" 를 "스위치가 꺼져 있으면" 조건으로 맞춘다(문서 정합, 원칙8).
- **R-3 [권고] 01-plan 28행 "VAPID 문자열을 … `.env.example` 어디에도 쓰지 않는다" 는 사실과 다르다.** `.env.example` 31~34행에 P7 용 `VAPID_PUBLIC_KEY=`·`VAPID_PRIVATE_KEY=`·`VAPID_SUBJECT=` 이름 줄이 이미 있다(fc §10). 이름만이라 security §1 위반은 아니며 U8 불변식 grep(247행)은 `.env.example` 을 보지 않으므로 판정은 영향 없음. 문장을 "이 패키지가 새로 더하지 않는다" 로 고친다.
- **R-4 [권고] 원칙6 부정 케이스 보강 — 생성기가 입력에 없는 패턴 키를 지어낼 때.** 판정 19행은 숫자 불일치(`count_mismatch`)만 본다. `pattern_sentences[].key` 가 입력 `pattern:*` 집합 밖이면 그 문장을 거부(`unknown_basis` 재사용 가능)하는 케이스 1행을 `test_briefing_compose` 에 더한다. 반대로 입력 패턴을 생성기가 빠뜨리면 템플릿 문장으로 채우는지도 같은 테스트에서 단언한다(74행 "그 패턴만 템플릿 문장으로 대체" 의 누락 쪽).
- **R-5 [권고] U5 `run_briefings(session_factory, …)` 와 U6 `get_session` 의존성이 맞물리는 방식이 비어 있다.** 75행은 실행 함수가 세션 **팩토리**를 받고 141행은 "주기 작업이 실행마다 세션을 연다" 인데, 76행 엔드포인트는 요청 단위 `get_session`(이미 열린 세션)을 의존성으로 받는다. 같은 함수가 세션을 받을지 팩토리를 받을지(그리고 API 경로에서 `FOR UPDATE … SKIP LOCKED` 와 세이브포인트가 어느 트랜잭션에 묶이는지)를 U5 03-log 에서 한 문장으로 정한다. 판정 3행("같은 `run_briefings` 객체")은 어느 쪽이든 성립한다.
- **R-6 [권고] P8 인계에 `agent_traces` 의 사용자 귀속 방법을 적는다.** 270행 인계는 "`briefing_compose` trace" 까지만 적었다. `agent_traces` 에 `user_id` 가 없으므로(S3.1) P8 이 사용자별로 읽으려면 `output.person_id → persons.user_id` 조인 또는 `session_id` 접두 규약이 필요하다 — 다중 사용자 부채(F-fbaaae)와 같은 뿌리임을 한 줄 적는다.
- **R-7 [권고] 판정 표 6행 문구.** 결정 B 확정 뒤에도 "권장안 (i) 이면 … / (ii) 를 고르면 …" 조건문이 남아 있다. H-2 ③ 과 함께 "선정 안 됨" 으로 고정한다(04-review 가 기대값을 추측하지 않게).

## 4. 결정
결과: 통과 — 2차 재검증(2026-10-02 13:59, verifier fable). [필수] H-1 `F-256944`·H-2 `F-4029df` 는 `evidence/20261002-1359-reverify.txt` 로 해소, 점검표 8행 전부 통과. 기계 검증 3차 FAIL 0·WARN 0(§1, `F-033bb1` 해소). 수정은 모두 문서(01-plan 3곳·S3.6 카드·resolution-plan §3.6)이며 코드·범위·스키마·시그니처·수용 기준·R12 는 그대로(reverify.txt `git diff --stat` 빈 출력). CR 불필요. 권고 R-1·R-2·R-4·R-5·R-6 은 착수 조건이 아니며 U2·U7·U4·U5·P8 인계 03-log 에서 처리한다(R-3·R-7 은 이번 수정으로 닫힘). `승인:` 은 사용자 몫 — 비워 둔다.
- 1차 판정(2026-10-02 13:50, 기록 보존): 보류 — [필수] 2건(H-1 `F-256944` 계획 문서의 존재하지 않는 클래스명, H-2 `F-4029df` S3.6 보충 필요). 점검표 8행 중 6행 통과, 행 3·4 는 위 두 소견이 닫히면 통과로 바뀐다(둘 다 문서 수정이며 코드·범위·스키마·시그니처는 그대로). 권고 R-1~R-7 은 착수 조건이 아니다. 기계 검증 1차 FAIL 1(02 부재, 예고됨)·WARN 0 → 2차(`evidence/20261002-1348-verify-plan-2.txt`) FAIL 0·WARN 1(보류 2건 파생). 두 소견이 닫히면 verifier 가 행 3·4 를 재판정해 이 줄을 "통과" 로 바꾼다 — 그때까지 `승인:` 은 비워 둔다.
승인: 사용자 (2026-10-02) — 결정 A~K 전부 권장안, 1차 보류 조치(문서 수정)·2차 재검증 통과 확인 후 계획 승인
