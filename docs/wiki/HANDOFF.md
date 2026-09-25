# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-25 22:25 — **P5-loop 완료(verifier 04-review `완료`, 사용자 승인).** 완료 커밋 `f9bfba7`(README 최신화 포함) → **dev 푸시 완료(`24feebd..f9bfba7`, 12커밋). 사용자 "main 승격" 결정 → main 에 GitHub PR #1 병합 커밋 `7eaf1f6`(2026-09-23 15:56, 내용은 dev 와 동일)이 있어 ff 불가 → 내용 무변경 병합 커밋을 dev 에 만들고 푸시 → `git push origin dev:main`.**

active: **none** | frozen: none | 브랜치 `dev` | Docker DB `capstone2-postgres-1`(5433, pgvector) — 5432 는 다른 프로젝트

## 마지막으로 끝낸 것
- P5-loop U1~U8 커밋(`3e4db92`~`f0d3e26`, 미푸시 11개). 재개 세션에서 끊겼던 verifier 04-review 를 다시 띄워 완료(`04-review.md`, verify-impl FAIL 0/WARN 0 `evidence/20260925-2200-verify-impl.txt`, 1474 passed, 05 열림 0/해소 23).
- 완료 처리: 04-review `승인:` · review-index R6·R7 구현완료 · backlog P5 체크 · CURRENT active none · journal DONE · 01-plan 판정 표 표기 정정(테스트 파일명·`-k`)·user-setup → RUNNING.md 갈음(사용자 결정) · 03-log U8 해시 · 05 머리말 U8 메모 복원 · README(진행 표·테스트 수·실 LLM 미확인 명시).

## 커밋 안 된 변경
- journal 의 COMMIT 줄(훅 자동)과 이 HANDOFF 만 — 다음 커밋에 포함.

## 바로 다음에 할 것
1. main 승격 마무리(`approve-commit.sh --release` → `git push origin dev:main` → `git fetch origin main:main`). 재발 방지: GitHub main 브랜치 보호 규칙(사용자 몫)(승격 전 판정 표 8행 실 공급자 curl 을 사용자가 돌려 보길 권고, `docs/RUNNING.md` 122행).
2. 다음 패키지 후보: P6(메모리 승격·패턴 감지 / 브리핑) — `/devlog start`, architect 위임은 L-004 승인 먼저.

## 열린 질문 · 사용자 결정 대기
- main 승격 시점 · 8행 실 공급자 확인.
- 보류(P5 끝날 때까지였던 것, 이제 꺼낼 차례): R-19(`verify-plan.sh` 7절 정규식) · `test-guards.sh` 옛 경로 · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · 하네스 부채(verify-plan 토큰 스캔 오탐, findings.py 빈 표 중복, verify-impl 이 05 머리말 메모를 지우는 문제).
- P9 착수 전: 09 카드 §2 결정 10개. 다중 사용자 격리 부채(F-fbaaae).

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다.
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 파일·테스트로 재확인.
- 개발 DB 에 `judge-row7-*`·`verifier-row7-*` 확인 행 잔존(지우지 않음). 테스트는 전역 개수 단언 금지.
- 푸시는 `git push origin dev` 단독 Bash 호출. 승인 마커는 커밋 명령과 다른 Bash 호출에서 먼저.
