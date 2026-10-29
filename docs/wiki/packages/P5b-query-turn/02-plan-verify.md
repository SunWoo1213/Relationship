# P5b-query-turn · 계획 검증 (02-plan-verify)

대상: 01-plan.md(초안 개정 1 — 결정 A~L 사용자 확정 2026-10-28) | 검증자: verifier (fable) — 계획 작성자(architect, opus)·메인 세션과 다른 모델·컨텍스트(L-002) | 날짜: 2026-10-28

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P5b-query-turn verifier-verify-plan -- bash .claude/scripts/verify-plan.sh P5b-query-turn` (FIX-034 — `tee` 대신 save_evidence)

### 1-1. 작성 전 1회 — `evidence/20261028-1512-verifier-verify-plan.txt`
```
# 명령: bash .claude/scripts/verify-plan.sh P5b-query-turn
# 시각: 2026-10-28T15:12:10+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 8a8767b (dev2)
# exit: 1
# ---
== verify-plan P5b-query-turn  (2026-10-28 15:12) ==
PASS  존재: docs/wiki/packages/P5b-query-turn/01-plan.md
FAIL  없음: docs/wiki/packages/P5b-query-turn/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D16
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 **[backend-agent] 계약 — `intent` 필드·스키마·재개 재료·trace 
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 프롬프트 + 게이트 — 조회 턴 기록 제안 거부** /
PASS  Refs 있음: - [ ] U3 **[backend-agent] 조회 답 생성기·검증기·템플릿 (`respond.py`, D
PASS  Refs 있음: - [ ] U4 **[backend-agent] 루프 조회 분기 — `run_turn` (해석 재사용 → 카
PASS  Refs 있음: - [ ] U5 **[backend-agent] 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`re
PASS  Refs 있음: - [ ] U6 **[backend-agent] API 끝에서 끝 + 회귀 판정 전부 + 문서** / Ref
PASS  Refs 있음: - [ ] U7 **[사용자·메인 세션] 실 LLM 왕복 1회 (사람 점검)** / Refs: P5b-que
PASS  backlog 일치: [ ] [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `in
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P8-frontend
PASS  registry 중복 없음: tests/test_agent_query_types.py
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
PASS  registry 중복 없음: tests/test_agent_query_gate.py
PASS  registry 중복 없음: tests/test_agent_query_answer.py
PASS  registry 중복 없음: tests/test_agent_query_loop.py
PASS  registry 중복 없음: tests/test_api_chat_query.py
PASS  registry 중복 없음: docs/wiki/packages/P5b-query-turn/tests.md
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
PASS  registry 중복 없음: FakeProposer.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/agent/__init__.py → | 모듈 | 루프 패키지 재export 진입점 | app/agent/__init__.py | P5-loop | 3e4db92 | `run_tur
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
== 결과: FAIL=1 WARN=8 ==
```

- FAIL 1 = 이 문서(02-plan-verify) 부재 — 작성 뒤 재실행(1-2)으로 닫는다.
- WARN 8 = 전부 "registry 에 다른 패키지로 이미 있음"(`app/agent/{types,propose,gate,loop,respond,__init__}.py`·`app/settings.py`·`docs/RUNNING.md`). 01-plan 63행이 미리 적은 대로("`verify-plan.sh` 7번(registry 중복)은 위 기존 파일들이 P5-loop 행으로 등록돼 있어 **WARN 을 낼 것이 예상된다** — 새 구현이 아니라 기존 모듈 확장이므로 registry 는 새 행이 아니라 **비고 확장**으로 처리한다") 기존 모듈 확장이고, "기존 산출물 재사용" 표(69~79행)가 registry 164~169·56 행을 행 번호로 인용한다 — 내가 `grep -n` 으로 대조한 결과 164(`types.py`)·165(`__init__.py`)·166(`propose.py`)·167(`gate.py`)·168(`loop.py`)·169(`respond.py`)·191(`briefing/types.py`)·196(`briefing/compose.py`)·222(`api/read.py`)·70(`tools_check.py`)·173~176(테스트 4) 행 번호가 전부 맞다. 소견으로 올리지 않는다(의도된 WARN).

### 1-2. 작성 뒤 1회 — `evidence/20261028-1518-verifier-verify-plan.txt`
```
# 명령: bash .claude/scripts/verify-plan.sh P5b-query-turn
# 시각: 2026-10-28T15:18:51+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 8a8767b (dev2)
# exit: 0
# ---
== verify-plan P5b-query-turn  (2026-10-28 15:18) ==
PASS  존재: docs/wiki/packages/P5b-query-turn/01-plan.md
PASS  존재: docs/wiki/packages/P5b-query-turn/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D16
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 **[backend-agent] 계약 — `intent` 필드·스키마·재개 재료·trace 
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 프롬프트 + 게이트 — 조회 턴 기록 제안 거부** /
PASS  Refs 있음: - [ ] U3 **[backend-agent] 조회 답 생성기·검증기·템플릿 (`respond.py`, D
PASS  Refs 있음: - [ ] U4 **[backend-agent] 루프 조회 분기 — `run_turn` (해석 재사용 → 카
PASS  Refs 있음: - [ ] U5 **[backend-agent] 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`re
PASS  Refs 있음: - [ ] U6 **[backend-agent] API 끝에서 끝 + 회귀 판정 전부 + 문서** / Ref
PASS  Refs 있음: - [ ] U7 **[사용자·메인 세션] 실 LLM 왕복 1회 (사람 점검)** / Refs: P5b-que
PASS  backlog 일치: [ ] [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `in
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: tests/test_agent_query_types.py
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
PASS  registry 중복 없음: tests/test_agent_query_gate.py
PASS  registry 중복 없음: tests/test_agent_query_answer.py
PASS  registry 중복 없음: tests/test_agent_query_loop.py
PASS  registry 중복 없음: tests/test_api_chat_query.py
PASS  registry 중복 없음: docs/wiki/packages/P5b-query-turn/tests.md
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
PASS  registry 중복 없음: FakeProposer.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/agent/__init__.py → | 모듈 | 루프 패키지 재export 진입점 | app/agent/__init__.py | P5-loop | 3e4db92 | `run_tur
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
== 결과: FAIL=0 WARN=8 ==
```

- FAIL 0 · WARN 8(1-1 과 같은 의도된 WARN). 스크립트의 "보류 0건" 은 점검표 8행 기준이다 — 이 문서의 보류는 점검표가 아니라 §3 [필수] H-1·H-2(기존 테스트 충돌·구현자 추측 자리)에서 나오며, 그래서 §4 결과는 보류다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 58~65행 범위 표 — 제외 "고민 상담 기능"·"인물 간(A–B) 관계 저장"·"관계 태그 필터링"·"상담 페르소나 / 톤 설정"·"음성 입력"·"네이티브 앱"; 18행 상단 안내 "답은 기록된 사실의 재진술로 한정(2장 제외 칸 "고민 상담" 그대로)". `docs/wiki/changes/CR-004.md` §1 표 "포함 칸 **"챗봇 UI"** 안의 확장(새 칸 없음). 제외 칸은 **그대로**". 01-plan 35행 "하지 않는 것: **인물 간(A–B) 관계 서술·고민 상담·조언·평가**(원칙7, D16 결정 8) — 조회 답은 한 인물 카드의 재진술뿐", 결정 J "`QUERY_MAX_PERSONS = 1` … 여러 인물 카드를 한 프롬프트에 넣으면 LLM 이 둘 사이 관계를 서술할 수 있다 — 인물 간(A–B) 관계는 원칙7 제외 범위", 결정 E-6 프롬프트 "다른 인물과의 관계는 말하지 마라. 위로·조언·감정 표현을 쓰지 마라" + 검증기(`app/briefing/types.py` 242행 `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개 — "기분"·"감정"·"위로"·"고민"·"상담"… 코드에서 확인) 실패 시 템플릿(결정 E-4). 프론트 0(D-7)·화면 3개 그대로. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | CLAUDE.md 원칙1·2·4 ↔ 01-plan 27행 "**`app/er/*` 수정** … 하지 않는다 — D16 결정 2 "확신도·임계치를 조회를 위해 낮추지 않는다"", U4 ② "결과 band 만 본다(루프는 확신도를 읽지 않는다, 원칙1·2·4)", R-2 ② `app/er` diff 빈 출력 — `app/er/pipeline.py` 325행 `resolve(ctx, mention, utterance, hints=None, *, judge=None, config=None)` 시그니처에 맞춰 호출(U4 ②). 원칙4 "LLM 단일 호출로 하지 않는다" ↔ 조회 턴 해석도 `resolve()`(4단계) 경유, `search_person` 제안은 게이트 ② 거부 유지(D16 "코드에서 지켜야 할 것" 2, `app/agent/gate.py` 125행 `NOT_CALLABLE_BY_LLM`). 원칙5 ↔ `web/` diff 0(D-7). 원칙7 ↔ 1행. 원칙8 ↔ U7 "실패하면 고치지 않고 FIX 후보로 기록한다(원칙8)", 결정 H "5·6 은 관찰 기록". 원칙9 ↔ 결정 C `loop_query.output` 스키마(mentions·resolutions·evidence_counts·answer_source·fallback_reason·rejected_answer·reply) + `tokens_in/out`, D16 결정 9 "조회 턴도 `agent_traces` 에 의도 분류 결과·해석·조회 입력(인물 id·근거 건수)·답·토큰". 원칙3·6 은 이 패키지가 건드리지 않는다(`app/er`·`app/memory` 무변경, R-2). |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `docs/wiki/decisions/D16-query-turn.md` "코드에서 지켜야 할 것" 7문장과 01-plan 판정 표 D-1~D-7 "출처 문장" 열을 글자 단위로 대조 — 7행 전부 동일(예: D-4 "조회 턴에 `add_event`·`add_schedule`·`update_person`·`create_person` `tool_call` trace 0, `events`·`schedules`·`person_facts`·`persons` 행 수 변화 0(`assert_no_writes` 류 단언)"). D16 갱신 이력 보정 ① "조회 턴은 **`resolve()` 만** 부르고 `apply_resolution()` 은 `identity` 되묻기 때만 부른다" ↔ 01-plan 결정 I 확정 "(a) merge·new_person 은 `resolve()` 만, identity 만 `apply_resolution()`"·U4 ② merge "그 `matched_person_id` 로 확정" / identity "`apply_resolution()`(→ `ask_user`)" / new_person "`apply_resolution()` 을 부르지 않는다" — 일치. 보정 ② "답 끝에 "자세한 건 인물 화면에서 볼 수 있어요." 문장만 둔다" ↔ 결정 F 확정 "(a) 링크 없이 문장만" — 일치(단 LLM 답에 붙이는 시점은 미정, §3 H-2). 사실 대조: `app/er/pipeline.py` 383행 `apply_resolution`·391~395행 docstring "`band == "merge"`: `update_person(ctx, person_id=…, new_alias=resolution.mention)` 로 **별칭만 누적**" — 결정 I 의 전제가 코드와 맞다. D16 문장 3 "`app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로" ↔ A-2 `tools_check` 7/7·R-2 ② `app/tools` diff 0. 충돌 1건은 D 카드가 아니라 기존 **테스트**와의 충돌(§3 H-1). D1·D2·D10 — ER 경로 무수정이므로 그대로. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `docs/wiki/specs/S3.4-ask-user-protocol.md` 마지막 줄 "(CR-004 · D16, 2026-10-28) 조회 발화의 `identity` 되묻기는 같은 프로토콜을 쓰고, 재개 재료(`PendingResume`)에 `intent`("record"/"query") 1필드가 더해져 답 뒤 재개가 조회로 이어진다. `new_person` 구간의 조회 발화는 되묻지 않는다(질문 행 생성 0)." ↔ 01-plan 결정 G "`PendingResume` 에 **`intent` 1필드만**"·U1 "`PendingResume.intent: str = INTENT_RECORD`, `to_dict()` 는 **`"query"` 일 때만**"·D-5 "new_person: `pending_questions` +0". 코드: `app/agent/types.py` 376~384행 `PendingResume` 필드(`version`…`schedule_options`) + `to_dict()` 의 "해당 없으면 싣지 않는" 관례(`tag_by_answer`·`schedule`) — `intent` 선택 키 설계가 같은 관례. S3.2 툴 7종 불변 ↔ 01-plan 28행 "조회는 툴이 아니라 루프가 코드로 부르는 읽기 함수", A-2. S3.1 ↔ R-3 `alembic check`, 30행 "`intent` 는 새 컬럼이 아니라 `pending_questions.context`(JSONB) 안의 키". 임계치 2개 ↔ `app/er` 무변경(R-2). ask_user 비동기 ↔ identity 조회 턴 "그 질문으로 턴 종료(`TurnResult.pending_question`, `stop_reason="ask_user"`)" + `POST /answers/{id}` 재개(U5). `stop_reason=None` ↔ `app/api/schemas.py` 113~114행 docstring "`stop_reason` ∈ `{"ask_user","limit",None}`" — 새 값 없음. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/wiki/packages/P5-loop/04-review.md` 196행 `결과: 완료`(승인 2026-09-25) · `P6-briefing/04-review.md` 267행 `결과: 완료` · `P8-frontend/04-review.md` 296행 `결과: 완료 — [필수] 0 · [권고] 10(…)`. P4 게이트 ↔ `P5-loop/01-plan.md` 12행 "**P4b 게이트 통과** — `1075dd6`(`/devlog done`, verifier 04-review `결과: 완료`, 사용자 승인)". 01-plan 5행이 든 해시 `1075dd6`·`a2f032d`·`6c2d0e7`·`fe76931`·`adc650e` 전부 `git cat-file -t` = commit. 기준 해시 주장 검증: `git diff --stat 8a8767b -- app alembic web` **빈 출력**(exit 0), `git diff --stat adc650e..8a8767b -- app` **빈 출력** — 7행 "`app/` 기준으로는 `adc650e..8a8767b` diff 가 비어 있다" 사실. `gitlog.sh P5b-query-turn P5b` — 태그 커밋 `8a8767b` 1건(CR-004 문서), 미커밋 변경 `HANDOFF.md`·`D16-query-turn.md`·`journal.md`(§3 R-3). |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `diff <(sed -n 75p docs/backlog.md) <(sed -n 125p docs/wiki/packages/P5b-query-turn/01-plan.md)` → 차이 0(IDENTICAL). verify-plan "PASS  backlog 일치". 해석 절(127~136행)은 한 줄을 바꾸지 않고 판정 표 행으로만 매핑(D-1~D-7·A-1~A-4·H-1). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan "PASS  Refs 있음" U1~U7 7건 + 04-review 줄에도 "Refs: P5b-query-turn CR-004 D16 R19". 모든 단위에 `P5b-query-turn CR-004 D16` 공통, 단위별로 S3.4/S3.2/S3.6·D1·D2·D10·D11·원칙 태그가 그 단위 내용과 맞다(예: U3 `S3.6 D11 원칙7 R19` — 답 생성 공급자 3종·금지 표현). |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `docs/wiki/security.md` §1 "로그·trace에 키·비밀을 남기지 않는다", "`.env` … 에이전트가 읽지도 쓰지도 않는다" ↔ 01-plan U3 "**이벤트 원문(`raw_utterance`)·인물 id·환경변수·키는 넣지 않는다**(카드 응답에 원문 필드가 없다 — `app/api/schemas.py` 307~309행)" — 코드 확인: `schemas.py` 307~309행 주석 "이 응답 모델 어디에도 `raw_utterance` 필드가 없다"; 결정 C "카드 전체·근거 값은 싣지 않는다(건수만)"; 공통 제약 (5) "프롬프트·trace·응답에 키 문자열 0(15행, security §1)". U7 "실 공급자 키 — 사용자 셸에서 로드, security §1" + `curl` 대상이 `127.0.0.1:8000` 로컬(§4 "로컬 서버 이외로 데이터 전송 금지" 안). 삭제·강제 푸시·`DROP` 없음. 증거 저장은 `save_evidence.py`(§4b). |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

**[필수] — 승인 전에 01-plan 을 고쳐야 한다(architect 또는 메인 세션, 사용자 결정)**

- **H-1 · U1 "`required` 에 `"intent"` 추가" 가 기존 테스트를 깨뜨려 "기존 테스트 무수정" 과 모순.** 01-plan 91행 "`PROPOSAL_SCHEMA["properties"]["intent"] = …`, `required` 에 `"intent"` 추가(결정 A)" 와 결정 A 표 "(a) … `required: ["tool_calls","intent"]`" — 그런데 `tests/test_agent_propose.py` 89~91행:
  ```
  def test_proposal_schema_top_level_requires_tool_calls_only():
      assert PROPOSAL_SCHEMA["required"] == ["tool_calls"]
      assert PROPOSAL_SCHEMA["additionalProperties"] is False
  ```
  이 테스트는 그대로 두면 FAIL 이고, 고치면 01-plan 24행 "**기존 테스트 파일은 고치지 않는다**", 33행 "근거는 기존 테스트 1958 건 무수정 통과", 판정 표 R-1 "`git diff --name-only --diff-filter=M 8a8767b..HEAD -- tests/` **빈 출력**", A-4 "1958 + 신규 passed, 실패 0" 네 곳과 어긋난다. 01-plan 은 `test_agent_propose.py` 126~131행만 보고(97행) 89~91행은 보지 못했다. 둘 중 하나를 사용자가 정해야 한다 — **(a) `required` 는 `["tool_calls"]` 그대로**(`intent` 는 enum 유도만 있는 선택 키. 결정 A 의 "키 없음/`null` → `"record"`" 규칙이 이미 누락을 받으므로 모양이 더 자연스럽고, `app/agent/propose.py` 공급자 3종은 `strict` 모드를 쓰지 않아(`grep -n strict app/agent/propose.py` 0건 — `app/er/judge.py` 291·373행만 `"strict": True`) 선택 키가 공급자 쪽에서 막히지 않는다; 모델이 `intent` 를 생략하면 record 로 흐르는 것은 의도 오분류 (가) 와 같은 관측 항목) / **(b) 기존 테스트 1건 수정 허용** — 그러면 24·33행 문장, R-1 기대값(`tests/test_agent_propose.py` 1건만 허용 목록으로), A-4 기대값(1958 그대로이되 1건 내용 변경)을 함께 고쳐야 한다. 어느 쪽이든 결정 A 표·U1 본문·U1 테스트 목록(`PROPOSAL_SCHEMA` 단언)·D-1 ① 기대 출력이 같이 바뀐다.
- **H-2 · 결정 F(a) "답·템플릿 끝에 '자세한 건 인물 화면에서 볼 수 있어요.' 만 둔다" — LLM 답에 그 문장을 누가·언제 붙이는지가 없다(FIX-033 (b) 자리).** 템플릿(E-5)에는 문장이 본문 안에 들어 있지만, LLM 답은 E-6 프롬프트가 그 문장을 시키지 않으므로 코드가 덧붙여야 한다. 그러면 (i) `validate_query_answer`(E-2 3줄/240자)를 LLM 원문에 거는지 덧붙인 뒤 문자열에 거는지, (ii) 결정 J 의 "한 번에 한 사람씩 물어봐 주세요." 한 줄과의 순서, (iii) `loop_query.output.reply`·`rejected_answer` 에 어느 문자열을 싣는지, (iv) `no_record_reply`/`no_mention_reply` 에는 붙이지 않는지 — 네 가지가 구현자 추측으로 남는다(D16 결정 5 "1~3줄" 이 덧붙인 뒤 5줄이 될 수 있다). 한 줄로 확정하면 된다. 후보: "검증은 LLM 원문에만 건다 → 통과한 원문 뒤에 코드가 `\n자세한 건 인물 화면에서 볼 수 있어요.` → (상한 초과 언급이 있으면) `\n한 번에 한 사람씩 물어봐 주세요.` 순으로 붙인다(상한 계산에서 제외) · `rejected_answer` 는 LLM 원문, `reply` 는 최종 문자열 · `no_record_reply`/`no_mention_reply` 에는 붙이지 않는다" — 또는 "LLM 답에는 붙이지 않고 템플릿에만 둔다"(그러면 결정 F 문장을 "템플릿 끝에" 로 정정).

**[권고] — 승인을 막지 않지만 위임 프롬프트 또는 01-plan 에 반영하면 재작업을 줄인다**

- **R-1 · 결정 K(a) monkeypatch 대상과 호출 형태.** U6/결정 K "`monkeypatch.setattr("app.agent.respond.answerer_from_env", …)`" 가 효과를 내려면 `app/agent/loop.py` 가 그 이름을 모듈 최상단 `from app.agent.respond import answerer_from_env` 로 묶어 두면 안 된다(그러면 `loop` 모듈의 바인딩은 치환되지 않아 HTTP 테스트가 실 공급자를 만들려다 키 없음으로 실패한다). 계획에 "조회 분기 안에서 `respond.answerer_from_env()`(모듈 속성 호출) 또는 함수 안 지연 import 로 해소한다" 한 줄을 적거나, monkeypatch 대상을 `app.agent.loop.answerer_from_env` 로 바꾼다. `extractor` 의 `_LazyFactExtractor` 선례(`app/memory/hooks.py` 103행)는 별도 클래스로 감쌌으므로 같은 모양이면 이 문제가 없다 — 어느 모양인지 고정.
- **R-2 · 결정 I 확정 뒤에도 남은 조건문 정리.** D-3 ① "`apply_resolution(`(identity 경로 — 결정 I 에 따라 merge 경로 포함 여부)", U4 ② "`apply_resolution()` 호출 여부는 **결정 I**", 수용 기준 해석 A-1 "결정 I 가 … 확정되면 … 확정이 반대면 이 줄은 4개 테이블로 줄인다", U4 변이 "(결정 I 가 "부르지 않음"으로 확정된 경우)" — 확정 (a) 값으로 바꿔 적으면 구현자가 결정 절을 오가지 않는다. 판정 기대값은 이미 (a) 와 모순 없음(`person_aliases` 불변 포함).
- **R-3 · D16 보정 2건이 미커밋.** `git status` — `docs/wiki/decisions/D16-query-turn.md`·`HANDOFF.md`·`journal.md` 가 작업 트리에만 있다(`git diff -- docs/wiki/decisions/D16-query-turn.md` 가 갱신 이력 1줄 추가). 점검표 3 의 근거가 커밋에 있으려면 이 02-plan-verify·승인과 같은 커밋에 넣는다.
- **R-4 · 판정 표 `-k` 토큰이 테스트 이름 제약인데 U 단위 테스트 목록에 일부만 적혀 있다.** `no_writes`·`stored_zero`·`card_called_once`·`new_person_no_question`·`identity_asks`·`timeline_limit`·`fallback`·`trace`·`no_counseling` — 이름이 다르면 `-k` 가 0건을 고르고 pytest 가 exit 5("no tests ran")로 끝나 "통과" 로 오독될 수 있다. 위임 프롬프트에 "판정 표 `-k` 토큰은 테스트 함수 이름에 반드시 포함, 0건 수집은 실패" 를 넣는다.
- **R-5 · FIX-033 (d) 가 01-plan 공통 절에 없다.** "스크래치패드" 0건(`grep -c`). 위임 프롬프트에 "임시 파일은 스크래치패드 리터럴 절대 경로" 를 넣는다(SKILL 5단계 네 규칙 중 (a)(b)(c) 는 84행에 있다).
- **R-6 · 결정 B-3 (b) 의 P10 집계 파급.** 조회 턴마다 `search_person` 제안이 `loop_gate.output.rejected[]` 에 `not_callable_by_llm` 로 **의도적으로** 쌓인다. `P5-loop/04-review.md` §7 "P10-final-eval: … 거부율 = `loop_gate.output.rejected[]` 사유별" 집계는 `loop_extract.output.intent` 로 기록/조회 턴을 나눠 세야 한다 — 01-plan 리스크 절 또는 D16 파급 "P10 평가 표본" 줄에 한 문장. 설계 자체는 D16 결정 2 "`search_person` 은 여전히 LLM 이 직접 부르지 못한다(게이트 ② 유지)"·"코드에서 지켜야 할 것" 2 와 어긋나지 않는다(제안은 하되 실행 0, `accepted == []`).
- **R-7 · U2 (ii) 프롬프트 문장 두 개를 한 자리에 모은다.** 결정 B-3 (b) 표에 지시 "intent 가 query 이면 물어본 인물마다 search_person 을 그 언급(query)으로 하나씩 제안하라 — 실행되지 않고 대상 표시로만 쓰인다" 와 예외 "단, intent 가 query 일 때만 예외로 대상 표시용 search_person 을 낸다"(기존 "절대 제안하지 마라" 문장 **바로 뒤**)가 셀 두 곳에 흩어져 있고 U2 (ii) 는 "결정 B 확정안의 문장" 으로만 가리킨다. 두 문장과 위치(`app/agent/propose.py` 231~237행 system 의 `"절대 제안하지 마라. "` 바로 뒤 / user_text)를 U2 에 글자 그대로 적으면 구현자 추측 0. 기존 `tests/test_agent_propose.py` 126~131행(`search_person`·`ask_user`·`get_briefing`·"제안" 포함)은 두 문장을 더해도 통과한다.

**검토했지만 소견이 아닌 것(위임 프롬프트 "특히 볼 것" 1~8 대응)**
1. 결정 I·F ↔ D16 갱신 이력 보정: 일치(점검표 3). "조회 턴 저장 0·`update_person` tool_call 0" 행(A-1/D-4)은 U4 테스트 (a) `_counts`/`assert_no_writes`(7 테이블) + `SELECT … WHERE step='tool_call' AND tool_name IN (4종)` 로 검증 가능하고, 결정 I(a) 아래 `person_aliases` 불변이 포함된다.
2. B-3 (b): 위 R-6·R-7. 원칙1·4 위반 아님 — 해석은 `resolve()` 안에서만, 제안은 `accepted == []`.
3. K(a): `run_turn`/`resume_turn` 에 `answerer=None` 키워드만 추가 → `app/api/routes.py` 365행 호출(`run_turn(ctx, body.utterance, proposer=…, judge=…, extractor=…)`) 무변경으로 성립, `Proposer` Protocol 무변경이라 `_FailingProposer`·`_DbErrorProposer` 영향 0. 남는 것은 R-1 의 호출 형태뿐.
4. L(a): R-7 행이 `import app.agent; import app.api; import app.main` 과 `import app.api; import app.agent` 두 순서를 **별도 프로세스**(`-c` 2회)로 본다 — 타당. `app/api/__init__.py` 14행 `from app.api.routes import router`·`routes.py` 113행 `from app.agent import …` 사실 확인.
5. C: `loop_query` 를 `LOOP_TRACE_STEPS` 밖에 두는 설계 ↔ `tests/test_agent_types.py` 56~71행(튜플 6종 고정·`STEP_LOOP_ERROR not in LOOP_TRACE_STEPS`·`loop_` 접두사) 과 충돌 없음, `STEP_LOOP_ERROR` 선례(`types.py` 63~65행 주석 "아래 `LOOP_TRACE_STEPS`(6종) 에는 포함하지 않는다"). `LOOP_TRACE_STEPS` 를 집계에 쓰는 코드 없음(`grep -rn` — `app/agent/__init__.py`·`types.py`·`routes.py` 의 `STEP_LOOP_ERROR` 뿐). `stop_reason=None` ↔ `schemas.py` 113행 일치.
6. E: 상한 3줄/240자·검사 순서(empty → 줄 수 → 길이 → 금지 표현)·비교(`> 상한` 거부)·문구 5종·프롬프트 문장 전부 값으로 적혀 있다. 금지 표현 import ↔ "app/briefing 수정 0": `app/briefing/types.py` 242행 튜플·`compose.py` 427~428행 상수 import 만, 589·626행이 `any(bad in … for bad in BRIEFING_FORBIDDEN_EXPRESSIONS)` 한 줄(공용 함수 없음) — 01-plan 32행 설명이 코드와 맞다. 남는 것은 H-2(덧붙이는 문장의 시점).
7. Refs·판정 명령·증거 경로·변이 표: U1~U6 각각 "변이 → 잡는 테스트" 표 있음(U2 는 동등 변이까지 명시). 새 테스트를 새 파일 5개에만 두고 `--diff-filter=M` 으로 무수정을 재는 설계는 타당하나 H-1 때문에 지금 문장대로는 성립하지 않는다. 픽스처 행 번호(`conftest.py::db_session` 120행 — 계획은 119행, 1행 차이; `fake_embedder` 148·`_spy` 68·`_ctx` 60·`app_and_client` 84) 확인.
8. 리스크 절 미결 4건(의도 오분류 관측·"나" 프롬프트 지시·호출 2회·`loop_extract` 토큰 0)은 전부 관측/P10/별도 FIX 로 넘기는 것이고 구현을 막지 않는다.

조치: H-1·H-2 는 `05-remediation.md` 소견이 아니라 01-plan 수정 사항이므로 F-id 를 만들지 않는다(기계 검증 FAIL/WARN 아님). 반영 뒤 verifier 재판정(이 문서 갱신) → 사용자 승인.

## 4. 결정
결과: 통과
승인: 사용자 (2026-10-29) — AskUserQuestion "승인". 1차 보류 [필수] H-1(`intent` 선택 키·`required` 무변경)·H-2(안내 문장 규칙 ①~⑤)는 사용자 결정으로 해소, [권고] R-1~R-9 는 01-plan 개정 2·3 에 반영(R-3 은 이 승인 커밋). 메인 세션 재실행 verify-plan FAIL 0/WARN 8(`evidence/20261029-1048-verify-plan-4.txt`). U1 부터 L-004 매번, 단위마다 verifier 커밋 전 리뷰.

## 재검토(2차) — 01-plan 개정 2 (H-1 (a)·H-2 규칙 확정 반영) · verifier (fable) · 2026-10-29

대상: 01-plan.md 상태 줄 "초안 개정 2 … 개정 2: U1 91행·결정 A 표·결정 F 규칙 ①~⑤·결정 K 호출 형태(R-1)·결정 I 조건문 정리(R-2)·공통 절 `-k` 0건 = 실패(R-4)·스크래치패드 규칙(R-5)·U2 (ii) 문장·위치(R-7)·`env` 접두 제거. R-3 미커밋은 승인 커밋에, R-6 은 리스크 절 메모". 1차 본문(§1~§3)은 이력으로 남긴다. `gitlog.sh P5b-query-turn P5b` — 태그 커밋 `8a8767b` 1건 그대로, 미커밋 `HANDOFF.md`·`D16-query-turn.md`·`journal.md` + 미추적 `packages/P5b-query-turn/`(HEAD `8a8767b`, 1차와 같다).

### 재-1. 기계 검증 (개정 2 대상, 재검토 절 작성 전) — `evidence/20261029-1042-verifier-verify-plan-3.txt`
명령: `python3 .claude/scripts/save_evidence.py P5b-query-turn verifier-verify-plan-3 -- bash .claude/scripts/verify-plan.sh P5b-query-turn`
```
# 명령: bash .claude/scripts/verify-plan.sh P5b-query-turn
# 시각: 2026-10-29T10:42:34+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 8a8767b (dev2)
# exit: 0
# ---
== verify-plan P5b-query-turn  (2026-10-29 10:42) ==
PASS  존재: docs/wiki/packages/P5b-query-turn/01-plan.md
PASS  존재: docs/wiki/packages/P5b-query-turn/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D16
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 **[backend-agent] 계약 — `intent` 필드·스키마·재개 재료·trace 
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 프롬프트 + 게이트 — 조회 턴 기록 제안 거부** /
PASS  Refs 있음: - [ ] U3 **[backend-agent] 조회 답 생성기·검증기·템플릿 (`respond.py`, D
PASS  Refs 있음: - [ ] U4 **[backend-agent] 루프 조회 분기 — `run_turn` (해석 재사용 → 카
PASS  Refs 있음: - [ ] U5 **[backend-agent] 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`re
PASS  Refs 있음: - [ ] U6 **[backend-agent] API 끝에서 끝 + 회귀 판정 전부 + 문서** / Ref
PASS  Refs 있음: - [ ] U7 **[사용자·메인 세션] 실 LLM 왕복 1회 (사람 점검)** / Refs: P5b-que
PASS  backlog 일치: [ ] [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `in
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: tests/test_agent_query_types.py
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
PASS  registry 중복 없음: tests/test_agent_query_gate.py
PASS  registry 중복 없음: tests/test_agent_query_answer.py
PASS  registry 중복 없음: tests/test_agent_query_loop.py
PASS  registry 중복 없음: tests/test_api_chat_query.py
PASS  registry 중복 없음: docs/wiki/packages/P5b-query-turn/tests.md
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
PASS  registry 중복 없음: FakeProposer.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/agent/__init__.py → | 모듈 | 루프 패키지 재export 진입점 | app/agent/__init__.py | P5-loop | 3e4db92 | `run_tur
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
== 결과: FAIL=0 WARN=8 ==
```
FAIL 0 · WARN 8 — 1차 §1-2 와 같은 의도된 WARN(기존 모듈 확장, 01-plan 63행·340행). 소견 없음.

### 재-2. [필수] 해소 여부

| id | 1차 소견 | 개정 2 의 문장(01-plan 행) | 검증(내가 직접 확인한 것) | 판정 |
|---|---|---|---|---|
| H-1 | `required` 에 `intent` 추가가 `tests/test_agent_propose.py:89-91` 을 깨뜨려 "기존 테스트 무수정" 과 모순 | 91행 "`required` 는 **무변경**(`["tool_calls"]` 그대로 — `intent` 는 선택 키, 키 없음/`null` → `"record"`; H-1 사용자 결정 (a) 2026-10-28, `tests/test_agent_propose.py:89-91` 무수정 유지)" · 결정 A (a) 행 174행 "**`required` 는 `["tool_calls"]` 그대로 — `intent` 는 선택 키**(H-1 (a), 기존 테스트 `test_proposal_schema_top_level_requires_tool_calls_only` 무수정)" · 판정 표 D-1 ① 기대 `['intent', 'tool_calls']`(properties 키) | `sed -n 85,95p tests/test_agent_propose.py` — 89~91행 `assert PROPOSAL_SCHEMA["required"] == ["tool_calls"]` / `assert PROPOSAL_SCHEMA["additionalProperties"] is False`: `required` 무변경이면 그대로 통과하고, `additionalProperties: False` 는 `properties` 에 선언된 `intent` 를 막지 않는다. 기존 테스트가 최상위 `properties` 키 집합을 단언하는 곳: `grep -rn 'PROPOSAL_SCHEMA\["properties"\]' tests/` → `test_agent_propose.py:56` 1건뿐이고 `["tool_calls"]["items"]…["name"]` 하위 경로라 영향 0. U1 "`Proposal.to_dict()` 에 `"intent"` 키를 **항상**" — 기존 테스트에 `loop_extract` output 정확 단언 없음(`grep -rn loop_extract tests/ \| grep output` 0건), `to_dict() ==` 단언은 `test_agent_propose.py:263·270`(두 Proposal 끼리 비교)뿐. `grep -n strict app/agent/propose.py` 0건(1차와 같음 — 선택 키가 공급자 strict 모드에 막히지 않음). 따라서 24행 "기존 테스트 파일은 고치지 않는다"·33행 "기존 테스트 1958 건 무수정 통과"·판정 R-1(`--diff-filter=M` 빈 출력)·A-4(1958 + 신규) 네 곳이 그대로 성립한다 | **해소** |
| H-2 | 결정 F(a) 문장을 LLM 답에 누가·언제 붙이는지 없음 | 252행 "**붙이는 규칙(H-2 확정 2026-10-28)**: ① 코드가 붙인다(`respond.py`, 상수 `QUERY_MORE_HINT = "자세한 건 인물 화면에서 볼 수 있어요."`) ② E-2 검증(3줄/240자)은 **LLM 답 본문에만** 하고 통과한 뒤 붙인다 — 최종 `reply` 는 최대 4줄(본문 3 + 이 문장 1, 결정 J 줄이 있으면 5) ③ 순서 = 본문 → (결정 J "한 번에 한 사람씩" 줄, 해당 시) → 이 문장, 줄바꿈 `\n` 으로 잇는다 ④ `loop_query.rejected_answer` 는 LLM 원문, `reply` 는 붙인 결과 ⑤ **붙이지 않는 답**: ③-2 "기록이 없어요"·언급 0 "알아듣지 못했어요"·템플릿 답(문구 안에 이미 같은 문장이 있어 중복 금지)" | 1차가 든 네 가지 추측 자리 (i)검증 시점 (ii)결정 J 줄 순서 (iii)`reply`/`rejected_answer` (iv)안 붙이는 답이 ②③④⑤ 로 각각 닫혔다. D16 결정 5 "1~3줄"(`D16-query-turn.md` 10행 "LLM 이 위 근거만으로 1~3줄 자연어 답을 만든다")과의 관계: "1~3줄" 은 LLM 본문 상한(E-2 233행 `QUERY_ANSWER_MAX_LINES = 3`(D16 결정 5 "1~3줄")) 이고 ② 가 "본문 3 + 이 문장 1" 로 최종 줄 수를 따로 적었다 — D16 문장과 충돌 없음(LLM 답은 여전히 1~3줄). 미커밋 D16 갱신 이력 ② "답 끝에 "자세한 건 인물 화면에서 볼 수 있어요." 문장만 둔다"(`git diff -- docs/wiki/decisions/D16-query-turn.md`) 와 일치. E-5 중복: `grep -n "인물 화면에서 볼 수 있어요" 01-plan.md` → 237행(템플릿 답 문구 안)·252행(규칙) 2곳뿐이고 ⑤ 가 템플릿 답에는 붙이지 않으므로 같은 문장이 두 번 나오지 않는다. 판정 표 충돌: D-6 "금지 표현 답 → reply == 템플릿 문자열" (⑤ 템플릿 무부착과 일치) · R-8 "금지 표현 14개 각각 템플릿 대체" (본문 검증 → 템플릿, ② 와 일치) · A-3 "`reply` 가 `loop_turn` 과 같음" (④ `reply` = 붙인 결과, 한 값) · U4 (d) "reply == 템플릿" · U3 "템플릿 출력이 검증기를 통과한다"(템플릿은 1줄) — 충돌 없음 | **해소** |

### 재-3. [권고] 처리 상태

| id | 1차 권고 | 개정 2 반영 위치 | 확인 | 상태 |
|---|---|---|---|---|
| R-1 | 결정 K monkeypatch 대상과 호출 형태 | 314행 "**호출 형태(R-1)**: `loop.py` 는 최상단 `from app.agent.respond import answerer_from_env` 로 이름을 묶지 않고, 조회 분기 함수 안에서 `from app.agent import respond as _respond` 뒤 `_respond.answerer_from_env()` 로 **모듈 속성 호출**한다 … 판정: `grep -n "answerer_from_env" app/agent/loop.py` 결과가 그 속성 호출 1곳뿐" | `monkeypatch.setattr("app.agent.respond.answerer_from_env", …)` 는 모듈 객체 `app.agent.respond` 의 속성을 바꾸고, `_respond.answerer_from_env()` 는 호출 시점에 그 속성을 읽으므로 효과가 난다(최상단 `from … import` 바인딩은 치환되지 않는 반면). 지금 `app/agent/loop.py` 185행 `from app.agent.respond import build_reply` 는 다른 이름이라 무관. `app.agent.respond` 모듈은 185행 때문에 이미 로드돼 있어 함수 안 `from app.agent import respond` 가 순환을 만들지 않는다 | 반영 |
| R-2 | 결정 I 확정 뒤 남은 조건문 정리 | U4 ② 107행 "**`apply_resolution()` 을 부르지 않는다**(결정 I (a) 확정 — 별칭 누적 0 …)" · 해석 ㄴ 130행 "결정 I (a) 확정(merge 에서 별칭 누적 안 함)이므로 **`person_aliases` 도 불변**" · D-3 ① 146행 "(**identity 경로에서만** — 결정 I (a); merge·new_person 경로에는 없다)" · U4 변이 표 110행 "merge 에서 `apply_resolution()` 호출(결정 I (a) 확정 — 부르지 않는다) → (a) `person_aliases` 행 수·`update_person` `tool_call` 단언 FAIL" | `grep -n "결정 I 가 \|결정 I 에 따라" 01-plan.md` → 0건(exit 1). 네 곳 전부 확정값으로 바뀜. 남은 포인터는 R-9 | 반영 |
| R-3 | D16 보정 2건·HANDOFF·journal 미커밋 | — | `git status` 2026-10-29: `M docs/wiki/HANDOFF.md`·`M docs/wiki/decisions/D16-query-turn.md`·`M docs/wiki/journal.md`·`?? docs/wiki/packages/P5b-query-turn/` 그대로. 점검표 3 의 근거(D16 갱신 이력 보정 ①②)가 커밋에 있으려면 이 02-plan-verify 와 같은 커밋이어야 한다 | **승인 커밋에 포함**(메인 세션 `/commit` 몫 — 여기서 닫는다) |
| R-4 | `-k` 0건 수집 = 실패 | 공통 절 84행 "**`-k` 식으로 돌린 판정은 수집 0건(pytest exit 5)이면 실패로 본다**(R-4 — 테스트 이름이 판정 표의 `-k` 토큰을 포함해야 한다)" | 문장 존재 확인(`grep -n "수집 0건" 01-plan.md` → 84행) | 반영 |
| R-5 | 스크래치패드 리터럴 절대 경로(FIX-033 (d)) | 84행 "**임시 파일·변이 스크립트는 스크래치패드 리터럴 절대 경로**(`/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/<세션>/scratchpad/u<n>/`, FIX-033 (d), R-5)" | `grep -n "스크래치패드" 01-plan.md` → 84행 1건(1차 0건). `<세션>` 자리는 구현 세션이 채우는 값이라 자리표시로 둔 것이 맞다 | 반영 |
| (R-4·R-5 묶음) `env` 접두 제거 | — | 84행 "(환경변수는 **wrapper 앞**에 — `env …` 접두는 `safety-guard` 가 막는다, P8b 04-review 메모)" | 01-plan 안에서 `env` 접두로 시작하는 명령 0건(`grep -nE` 백틱·`--` 뒤 `env ` 패턴 → 84행의 `POSTGRES_PORT=5433 python3 …` 형태만 걸림). 판정 표 D-1·D-2·D-3 ④·D-4·D-5·D-6 ①·A-1·A-3·A-4·R-3·R-5·R-6·R-8 의 `POSTGRES_PORT=5433 .venv/bin/python …` 도 wrapper 앞 형태 | 반영 |
| R-6 | 결정 B-3 (b) 의 P10 집계 파급 | 리스크 절 첫 항목 330행 "**(R-6, 02-plan-verify 1차) 조회 턴의 `loop_gate.rejected` 에 `not_callable_by_llm` 이 의도적으로 쌓인다** … P10 이 게이트 거부율을 집계할 때는 `loop_extract.output.intent` 로 기록 턴/조회 턴을 나눠 세야 한다 … P10 인계 문장으로 04-review §7 에 옮긴다" | 문장 존재·내용이 1차 권고와 같다. 04-review §7 인계는 완료 검토 때 내가 확인한다 | 반영 |
| R-7 | U2 (ii) 프롬프트 두 문장·위치 | 97행 "`propose.py` 231~237행의 기존 "search_person … 절대 제안하지 마라" 문장 **바로 뒤**에 다음 두 문장을 글자 그대로 덧붙인다(기존 문장은 지우지 않는다, R-7): "단, intent 가 query 일 때만 예외로, 물어본 인물마다 search_person 을 그 언급(query)으로 하나씩 제안하라. 이 제안은 실행되지 않고 대상 표시로만 쓰인다."" | `sed -n 225,240p app/agent/propose.py` — `system = (` 231행 … 236행 `f"절대 제안하지 마라. {PROPOSAL_TOOL_NAME} 도구로만 답하라."` … 238행 `)`: 계획이 가리킨 자리가 실제 코드와 맞다(문장은 236행, system 문자열은 231~238행 — 계획의 "231~237행" 과 1행 차이는 닫는 괄호뿐). 기존 테스트 `test_build_propose_prompt_marks_not_callable_tools`(126~131행: `search_person`·`ask_user`·`get_briefing`·"제안" 포함)·`test_build_propose_prompt_has_no_secrets_or_env_names`(141~148행: `ANTHROPIC`·`OPENAI`·`GEMINI`·`os.environ`·`api_key` 미포함)·`…no_literal_parenthesis_call_forms_in_source`(151~157행: user_text 에 `create_person(`·`update_person(` 없음) 은 두 문장을 더해도 통과한다(두 문장에 그 문자열이 없다) | 반영 |

### 재-4. 점검표 재확인 (개정 2 로 바뀐 행 3·6·7 — 나머지 1·2·4·5·8 은 1차 통과 유지)

| # | 항목 | 결과 | 근거 |
|---|---|---|---|
| 3번 | D 카드 "코드에서 지켜야 할 것" 충돌 없음 | 통과 | `D16-query-turn.md` 27~33행 7문장을 다시 읽어 판정 표 D-1~D-7 "출처 문장" 열과 대조 — 개정 2 에서 바뀐 것은 D-3 "기대 출력" 열의 괄호("identity 경로에서만 — 결정 I (a)")뿐이고 출처 문장은 그대로. D16 문장 3 "`app.er.resolve`/`apply_resolution` 을 재사용" 은 identity 경로의 `apply_resolution()` 으로 성립(미커밋 갱신 이력 보정 ① 과 같은 해석). 결정 F 규칙 ①~⑤ ↔ 갱신 이력 보정 ② "프론트 0 을 지키고 답 끝에 "자세한 건 인물 화면에서 볼 수 있어요." 문장만 둔다" — 일치(재-2 H-2). 결정 A (a) ↔ D16 문장 1 "`intent` enum `["record","query"]` 가 있고, 다른 필드·툴 제안 스키마는 그대로다" — `required` 무변경은 "그대로" 쪽에 더 가깝다 |
| 6번 | 수용 기준 = backlog 글자 그대로 | 통과 | `diff <(sed -n 75p docs/backlog.md) <(sed -n 125p docs/wiki/packages/P5b-query-turn/01-plan.md)` → 차이 0, `IDENTICAL`(2026-10-29 재실행). verify-plan "PASS  backlog 일치". 해석 절(127~136행)은 ㄴ 줄의 괄호만 확정값으로 바뀌었고 수용 기준 한 줄은 무수정 |
| 7번 | 단위마다 Refs | 통과 | 재-1 "PASS  Refs 있음" U1~U7 7건. 개정 2 는 U1·U2·U4 본문만 고치고 Refs 줄은 바꾸지 않았다(1차 §2-7 과 같음) |

### 재-5. 새 [권고] (승인을 막지 않는다 — 위임 프롬프트에 한 줄씩)

- **R-8 · 결정 F 규칙 ⑤ "템플릿 답" 의 범위를 양성 조건으로.** E-5 에는 템플릿이 두 가지다 — "근거 있음" 템플릿(237행, 문장을 이미 품음)과 "근거 0건" 템플릿(238행 `"… 그 밖의 기록은 아직 없어요."`, `answer_source="template"`·`fallback_reason="no_evidence"`, 문장 없음). ⑤ 의 괄호 "문구 안에 이미 같은 문장이 있어" 는 앞의 것에만 맞아, 구현자가 근거 0건 템플릿에는 붙여야 하나 망설일 수 있다. "붙이는 답은 `answer_source == "llm"` 뿐(그 밖 `template`·`no_record`·`no_mention`·`ask` 는 붙이지 않는다)" 한 줄로 쓰면 결정 C 의 `answer_source` 어휘와 1:1 이 되어 테스트(U3·U4 (d)(f))도 그 값으로 단언할 수 있다. 어느 쪽이든 수용 기준·D16 과 무관.
- **R-9 · 확정된 결정을 아직 "결정 X" 로만 가리키는 잔존 3곳.** 20행 "merge 에서 `apply_resolution()` 을 부르는가는 **결정 I**" · 112행 "별칭 누적 여부는 결정 G" · 113행 "결정 G (a) 확정 시 `person_aliases` 불변". 결정 I·G 가 모두 (a) 로 확정돼 있어 뜻은 통하지만, R-2 와 같은 이유로 "부르지 않는다(결정 I (a))"·"누적하지 않는다(결정 G (a))" 로 바꾸면 구현자가 결정 절을 오가지 않는다. 판정 표·테스트 기대값에는 영향 없음.

### 재-6. 기계 검증 (재검토 절 작성 뒤) — `evidence/20261029-1046-verifier-verify-plan-3b.txt`

중간 1회(`evidence/20261029-1046-verifier-verify-plan-3.txt`, exit 1)는 `FAIL  점검표 행 수 11 (8 필요)` — 원인은 계획이 아니라 **이 문서의 재-4 표**가 `| 3 |`·`| 6 |`·`| 7 |` 로 시작해 스크립트(`verify-plan.sh` 88행, 패턴 `^\| [1-8] \|`)가 1차 점검표 행으로 함께 센 것. 번호 셀을 `3번`·`6번`·`7번` 으로 바꿔(내용 무변경) 재실행한 것이 아래다. 같은 분에 저장돼 이름을 `-3b` 로 했다(save_evidence 는 덮어쓰지 않는다).

명령: `python3 .claude/scripts/save_evidence.py P5b-query-turn verifier-verify-plan-3b -- bash .claude/scripts/verify-plan.sh P5b-query-turn`
```
# 명령: bash .claude/scripts/verify-plan.sh P5b-query-turn
# 시각: 2026-10-29T10:46:54+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 8a8767b (dev2)
# exit: 0
# ---
== verify-plan P5b-query-turn  (2026-10-29 10:46) ==
PASS  존재: docs/wiki/packages/P5b-query-turn/01-plan.md
PASS  존재: docs/wiki/packages/P5b-query-turn/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D16
PASS  카드 존재: D2
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 **[backend-agent] 계약 — `intent` 필드·스키마·재개 재료·trace 
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 프롬프트 + 게이트 — 조회 턴 기록 제안 거부** /
PASS  Refs 있음: - [ ] U3 **[backend-agent] 조회 답 생성기·검증기·템플릿 (`respond.py`, D
PASS  Refs 있음: - [ ] U4 **[backend-agent] 루프 조회 분기 — `run_turn` (해석 재사용 → 카
PASS  Refs 있음: - [ ] U5 **[backend-agent] 재개 — 조회 턴 identity 되묻기 뒤 답하기 (`re
PASS  Refs 있음: - [ ] U6 **[backend-agent] API 끝에서 끝 + 회귀 판정 전부 + 문서** / Ref
PASS  Refs 있음: - [ ] U7 **[사용자·메인 세션] 실 LLM 왕복 1회 (사람 점검)** / Refs: P5b-que
PASS  backlog 일치: [ ] [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `in
PASS  의존 완료: P5-loop
PASS  의존 완료: P6-briefing
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: tests/test_agent_query_types.py
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
PASS  registry 중복 없음: tests/test_agent_query_gate.py
PASS  registry 중복 없음: tests/test_agent_query_answer.py
PASS  registry 중복 없음: tests/test_agent_query_loop.py
PASS  registry 중복 없음: tests/test_api_chat_query.py
PASS  registry 중복 없음: docs/wiki/packages/P5b-query-turn/tests.md
WARN  registry 에 다른 패키지로 이미 있음: app/agent/types.py → | 모듈 | 루프 계약 타입·trace 어휘(GateVerdict·PendingResume·LoopError 등) | app/agent/type
PASS  registry 중복 없음: Proposal.inten
PASS  registry 중복 없음: PendingResume.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/propose.py → | 모듈 | 인식 단계 — 발화 → tool_calls 제안(LLM 1회) | app/agent/propose.py | P5-loop | 069
PASS  registry 중복 없음: FakeProposer.inten
WARN  registry 에 다른 패키지로 이미 있음: app/agent/gate.py → | 모듈 | 게이트 — LLM 제안을 코드가 거른다(L(iii)) | app/agent/gate.py | P5-loop | 8ecf75c | `
WARN  registry 에 다른 패키지로 이미 있음: app/agent/loop.py → | 모듈 | add_event·add_schedule | app/tools/records.py | P2-tools | 9cb35b6 | `EVE
| 모듈 | 에이전트 루프 오케스트레이션(해석·기록·응답, run_turn/resume_turn) | app/agent/loop.py | P5-
| 모듈 | 루프-메모리 연결(after_record) | app/memory/hooks.py | P6-memory | 8d3967a | `af
WARN  registry 에 다른 패키지로 이미 있음: app/agent/respond.py → | 모듈 | 응답 단계 — 결정적 템플릿 응답 문장 | app/agent/respond.py | P5-loop | 1835355 | `build
WARN  registry 에 다른 패키지로 이미 있음: app/agent/__init__.py → | 모듈 | 루프 패키지 재export 진입점 | app/agent/__init__.py | P5-loop | 3e4db92 | `run_tur
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_user_id()`(`APP_USE
| 엔드포인트 | FastAPI 앱 팩토리·예외 매핑 | app/main.py | P2-tools | 4d5817e | `create_app()
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: docs/RUNNING.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·실행법) | README.md | 하네스 | pending | 패키지 완료마
| 문서 | `docs/RUNNING.md` "프론트 실행 (P8-frontend)" 절 — 백엔드 기동 → `cd web` → `npm ci`
== 결과: FAIL=0 WARN=8 ==
```
FAIL 0 · WARN 8(의도된 WARN, 재-1 과 같음).

### 재-7. 결정(2차)
[필수] 0 — H-1·H-2 해소. [권고] 잔여 R-8·R-9(승인을 막지 않음, 위임 프롬프트에 한 줄씩). R-3 은 승인 커밋에 포함. 따라서 §4 `결과:` 를 **통과** 로 바꿨다(위). 승인은 사용자 몫 — `승인:` 줄은 메인 세션이 쓴다.
