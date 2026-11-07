# L-006 · 요청 → 완성까지는 자동으로 진행하고, 완성됐다고 판단될 때 한 번만 묻는다

날짜: 2026-11-07 | 어디서(P / FIX / CR): 하네스 (3차 발표 뒤 사용자 지시) | Refs: harness L-006 L-002 L-003 L-004 security

## 무슨 일이 있었나
- 사용자: "hook을 수정하고 싶어요. 이제 사용자의 승인을 받아야 넘어갈 수 있는 단계를 삭제하고 싶습니다. 작업을 자동화해서 인계가 되도록 하고싶습니다."
- 이어서: "내가 어떤 기능 구현을 원하면 그걸 테스트까지 진행한 다음 완성됐다고 판단이 들면 나에게 물어보는 정도로 하고싶어."
- 결정(AskUserQuestion 2문): main 승격까지 **전부 자동** · verifier 자동 검증 게이트(L-002)는 **유지**.

## 왜 그랬나
- L-003·L-004 와 커밋·푸시 승인 마커는 2026-09 초에 "단계마다 사용자가 방향을 볼 기회"를 만들기 위해 넣었다. 두 달 동안 패키지 11개·FIX 35건을 돌리며 절차가 안정됐고, 승인 질문이 위임·커밋·푸시·완료마다 4~6번 반복돼 작업의 흐름을 끊는 비용이 더 커졌다.
- 신뢰성은 사람 승인이 아니라 **다른 모델의 자동 검증**(verifier 계획 검증·완료 검토·FIX 커밋 전 리뷰, L-002)이 지키고 있었다. 그 게이트는 그대로 두고 사람 승인만 뺀다.

## 다음부터
- **규칙**: 요청 → 계획(architect) → 계획 검증(verifier) → 구현(구현 에이전트) → 테스트 → 완료 검토(verifier) → 커밋·dev2 푸시까지 **묻지 않고** 진행한다. 완료 검토가 `결과: 완료` 면 **그때 한 번** `AskUserQuestion` 으로 "완성됐다. 확인해 달라"를 묻는다(선택지: 확인 / 수정 필요). 확인이면 `dev2:dev` → `dev:main` 승격까지 이어서 한다. 수정이면 FIX 로 계속한다.
- 중간에 **사용자 결정이 필요한 것**(계획이 비워 둔 상수·범위·기획서 변경 CR)은 여전히 묻는다 — 그것은 승인이 아니라 결정이다. 세션 재개는 HANDOFF 의 "바로 다음"대로 바로 이어간다.
- **폐지**: `delegate-guard.sh`·`approve-commit.sh` 삭제, 마커 5종(`.commit-approved`·`.push-approved`·`.release-approved`·`.awaiting-decision`·`.stage-approved`) 폐지, `commit-guard.sh` 승인 마커·해시 비교·L-003 검사 삭제, `safety-guard.sh` 승격 푸시 마커 요구 삭제, `commit-cleanup.sh` 마커 생성·소비 삭제, `stage-gate.sh` L-003 블록·`승인:` 줄 검사 삭제, `settings.json` Agent 매처·마커 deny 삭제.
- **유지**: 보안 가드(삭제·비밀·강제 푸시·origin 외 푸시), Bash 쓰기 가드(FIX-014), 활성 작업 게이트(stage-gate `결과: 통과`·`계획 점검: 통과`), FIX 커밋의 verifier 게이트(FIX-027), HANDOFF Stop 훅, 커밋 메시지 초안 파일(`-F`)과 journal 자동 기록.
- 고친 파일: 위 훅·스크립트, `.claude/scripts/test-guards.sh`(L-003·L-004 절 → L-006 회귀 절), `.claude/skills/commit/SKILL.md`, `.claude/skills/devlog/SKILL.md`, `CLAUDE.md` 개발 프로세스, `docs/wiki/security.md` §2, `INDEX.md`, `verification.md`, 템플릿(`plan-verify.md`·`fix.md` 의 `승인:` 줄 제거), 에이전트 정의 5개, `.githooks/pre-commit`, L-003·L-004 카드 상단 "폐지" 표기.
