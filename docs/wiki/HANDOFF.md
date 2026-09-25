# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-25 (재개) — **재개 세션. 사용자 결정: 기록 정리 커밋 → 푸시는 P5-loop 완료 뒤 한 번에(지금은 안 올림) → U6 시작.**

active: **P5-loop** | frozen: none | 브랜치 `dev` | Docker DB `capstone2-postgres-1`(5433, pgvector) — 5432 `finance_postgres` 는 다른 프로젝트라 무관(사용자가 종료함)

## 이 세션에서 끝난 것 (커밋, 전부 dev · **미푸시**)
- `24feebd` 계획 승인·활성화(푸시됨) → `3e4db92` U1 계약 타입 → `a3ebc36` 한국어 규칙(커밋 스킬·에이전트 4종) → `069bdc2` U2 인식(LLM 제안) → `8ecf75c` U3 게이트 → `7a2ec5c` U4 해석 → `1835355` U5 기록·응답
- **미푸시 7개**(`3e4db92`~`1835355` + FIX-004 `1be4a56` — `git log --oneline origin/dev..dev`). 커밋 안 된 것: journal 의 COMMIT 줄(훅 자동)·이 HANDOFF 의 해시 반영 — 다음 첫 커밋에 포함. 푸시는 사용자 승인 뒤 `git push origin dev` → L-003 결정 대기.
- 단위별로 정한 것(R-22~R-25, 후보 시각 규칙, 사용자 결정)은 `packages/P5-loop/03-log.md` 각 항목 "남은 것" 칸에 있다. 다시 정하지 않는다.

## 지금 진행 중
- **U6 `POST /chat` 완료·커밋**(사용자 승인 2026-09-25): chat 9 passed(메인 세션이 재실행), 전체 1463 passed. 해시는 journal 참고, 03-log `pending` 은 다음 커밋에서 채운다.
- 예시 설정 파일에 들어가 있던 실제 형식 키는, 키가 이미 비밀 파일에 있다는 사용자 확인을 받은 뒤 `git restore` 로 되돌렸다(커밋·푸시된 적 없음).
- 다음: U7(재개) — 시작 전에 L-004 승인을 받는다.

## 바로 다음에 할 것 (순서대로)
1. (완료, 커밋 대기) **U6 `POST /chat` — API 한 흐름**(01-plan 93행): `app/api/routes.py`·`schemas.py`·`deps.py`, 세션 id 서버 발급(결정 I), `get_session()` 재사용, 루프 예외는 삼켜 200(결정 G·H) — 단 `SQLAlchemyError` 는 올린다(R-3), 미답변 질문 유지(R-4), 테스트 `tests/test_api_chat.py`. backend-agent, L-004 승인 받음(2026-09-25).
2. U7 재개 `POST /answers/{question_id}` 뒤 절반(R6·R7 을 닫는 단위) → U8 수용 기준 기계 검증·registry·README → `/devlog done`(verifier 04-review).
3. 푸시: 사용자 결정(2026-09-25) — P5-loop 완료 뒤 한 번에. 그 전에는 묻지 않는다.

## U6·U7·U8 에서 재확인할 것 (U5 가 남김)
- `TurnResult.stop_reason` 값 집합("ask_user" / 게이트 "limit" / None)과 `trace_ids`(loop_turn 자신 제외 4행)가 U6 응답 스키마·U8 판정 표와 맞는가.
- 01-plan 70행 `load_resume_input(...) -> ResumeInput{kind, context, session_id}` 표기와 U1 구현(`kind·context·answer`)의 불일치 — U7 에서 한 줄 정리.
- `LOOP_MAX_RESUME_BYTES = 8192` 는 초기 추정치 — U8 에서 재확인.
- U7 재개: 멈춘 턴에서 넘어온 시각 없는 `add_schedule`(pending_calls)은 재개 때 `schedule` 질문으로 이어 묻는다(사용자 결정 2026-09-24, R-14 흐름).
- U8 착수 전 05-remediation [권고] 7건 원인 분석 칸 채우기(R-2).

## 재개 시 읽을 카드 (이것만)
- `packages/P5-loop/01-plan.md` U6~U8 항목·판정 표, `03-log.md` 마지막 두 항목, `02-plan-verify.md` §3 권고 R-20~R-27
- `specs/S3.4`·`S3.2`, `decisions/D01`·`D02`, `docs/wiki/fixes/FIX-004.md`, `.claude/gitlog.md`

## 열린 질문 · 사용자 결정 대기
- 미푸시 커밋 푸시 시점.
- 보류(P5 끝날 때까지, 사용자 결정 2026-09-24): R-19(`verify-plan.sh` 7절 정규식) · `test-guards.sh` 옛 경로 · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌.
- P9 착수 전: 09 카드 §2 결정 10개.

## 주의 (다음 세션이 실수하기 쉬운 것)
- **언어: 답변·커밋·위키 기록·주석·서브에이전트 산출물 모두 한국어**(사용자 요청, 커밋 스킬·에이전트 정의에 반영). 결과 보고는 식별자 나열이 아니라 **예시와 쉬운 말**로 먼저 설명하고 승인을 묻는다(사용자 요청 "설명을 제대로 해주세요").
- 재개 시 커밋 안 된 변경이 있으면 먼저 목록을 보이고 우선순위를 묻는다(`/devlog resume`).
- 위임은 묻고 시작(L-004): 승인 → `approve-commit.sh --stage <이름>` → Agent 1회. 서브에이전트 보고는 믿지 말고 테스트 재실행·grep 으로 확인한다.
- **판정 표 7행 명령은 개발 DB 에 행을 남긴다** — U8 전까지 다시 돌리지 않는다. 테스트는 전역 개수 단언을 쓰지 않는다.
- 전체 회귀는 한 번에 하나만 돌린다(같은 DB 를 공유하는 에이전트 둘이 동시에 돌리지 않는다).
- 푸시는 `git push origin dev` 단독 Bash 호출. 승인 마커는 커밋 명령과 다른 Bash 호출에서 먼저.
- `app/` docstring 에 "evaluation" 문자열 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지(판정 표 5a·6행).
