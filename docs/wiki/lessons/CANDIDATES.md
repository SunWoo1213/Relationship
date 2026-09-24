# L-nnn 후보 — 아직 교훈 카드로 올리지 않은 것

> 여러 문서에 "L-nnn 후보" 로 흩어져 있던 것을 한 곳에 모았다(2026-09-24, 사용자 점검 요청). **결정은 아직 없다.** 카드(L-nnn)로 올리거나 기각하면 이 표의 상태를 바꾸고 줄은 지우지 않는다.
> 새 후보가 생기면 원 문서에 "L-nnn 후보" 라고 쓰는 것과 **함께** 여기에 한 줄 추가한다.

| # | 후보 | 출처 (원문 위치) | 강제 장치 후보 | 상태 |
|---|------|------------------|----------------|------|
| C-1 | `main` 직접 커밋·병합을 막는 장치가 없다 — 훅은 이 세션의 dev 푸시만 강제한다. FIX-001(main 6커밋 갈라짐)·PR #1(웹 UI 병합)이 모두 이 경로 | `fixes/FIX-001.md` 60행, HANDOFF 보류 목록 | GitHub 브랜치 보호 규칙(저장소 설정 — 사용자 몫) | 보류(P5 끝까지) |
| C-2 | `verify-impl.sh` 6번("registry 에 패키지 열 행 필수")이 "기존 파일만 확장한 패키지"를 표현할 수 없다 | `packages/P3-llm-providers/04-review.md` 113·118·127행 (F-4ef1a3) | 6번 완화: 기존 행 비고에 패키지 id 가 있으면 통과 | 보류(다음 하네스 확장 패키지) |
| C-3 | 권고 id `R-8` 을 Refs 에 `R8` 로 쓰면 검증 항목 R8 과 충돌한다(`verify-impl.sh` 4번·`git log --grep`) | `packages/P4b-er-redesign/04-review.md` 124행 (V-5) | 권고는 `R-n` 표기만, Refs 에 넣지 않는다 — devlog SKILL 태그 규칙에 한 줄 | 보류(P5 끝까지) |
| C-4 | 03-log 의 Refs 와 커밋 Refs 를 같게 쓴다 | `packages/P4-pilot-eval/04-review.md` 230행 | 03-log 템플릿 주석 | 보류 |
| C-5 | 실패한 Agent 호출(`not found`)도 1회용 단계 승인 마커를 소모한다 → 사용자 재승인이 필요 | `fixes/FIX-003.md` 증상, journal 2026-09-24 19:45 | `delegate-guard.sh` 는 PreToolUse 라 호출 성공 여부를 모른다. PostToolUse 에서 실패 시 마커 복원, 또는 그대로 두고 재승인(현 동작) | 신규 |
| C-6 | journal 기록을 강제하는 장치가 없다 — HANDOFF 는 Stop 훅이 강제하지만 journal 은 COMMIT 줄만 자동. 2026-09-24 하루치가 HANDOFF 에만 남았다 | `lessons/L-005-main-session-verify-first-hand.md` 4 | `handoff-check.sh` 에 "오늘 날짜 journal 줄 0 이면 경고" | 신규 |
| C-7 | `verify-plan.sh` 7절 정규식 `[.][a-z]{1,5}` 가 `inspect.signature` 를 잘라 가짜 경로 토큰(`inspect.signa`)을 만든다 | P5-loop `02-plan-verify.md` R-19, evidence `20260924-1943-verify-plan-3.txt` WARN | 정규식 수정 → FIX | 보류(P5 끝까지) |
