# L-003 · dev 푸시 뒤에는 사용자가 승격/수정을 정할 때까지 멈춘다

날짜: 2026-09-03 | 어디서(P / FIX / CR): 하네스 (P0-embed-pilot 완료 커밋을 dev 에 푸시한 직후 사용자 지시) | Refs: harness L-003 L-001 security

## 무슨 일이 있었나
- dev 에 3abe513 을 푸시한 뒤 에이전트가 곧바로 다음 하네스 작업(L-002)을 시작했다.
- 사용자: "dev 에 푸시를 하면 내가 그것을 main 에 푸시를 할지 고쳐야 할지 정하기 전엔 그 다음 작업을 진행하지 마세요."

## 왜 그랬나
- L-001 이 "dev → 실서버 검증 → main" 순서는 정했지만, **검증하는 동안 에이전트가 무엇을 하는가**는 정하지 않았다. 에이전트는 자율 실행 기본값대로 다음 작업으로 넘어갔다.
- 실서버 검증 결과 "수정"이 나오면 그 사이 쌓인 다음 작업 커밋이 수정과 섞인다. 검증 단위(푸시 1회)와 결정 단위를 맞춰야 한다.

## 다음부터
규칙으로 바꿀 것이 있으면 어느 파일(CLAUDE.md · 스킬 · 훅)을 고쳤는지 적는다.
- **규칙**: `origin dev` 푸시가 성공하면 cleanup 훅이 `.claude/.awaiting-decision`(푸시 해시)을 만든다. 마커가 있는 동안 `stage-gate.sh` 는 HANDOFF·journal·커밋 초안·gitlog 외 모든 쓰기를, `commit-guard.sh` 는 새 커밋을 거부한다. 에이전트는 푸시 직후 HANDOFF 를 갱신하고 `AskUserQuestion`(승격 / 수정 / 보류)을 한 뒤 턴을 끝낸다.
- **해제**: 승격 → `approve-commit.sh --release`(마커 제거 + 승격 마커) → `git push origin dev:main`. 수정 → `approve-commit.sh --decision fix`(마커 제거) 후 FIX/작업 계속. 보류 → 마커 유지, 다음 세션 재개 시 다시 묻는다.
- 고친 파일: `.claude/hooks/commit-cleanup.sh`(마커 생성·승격 시 제거), `stage-gate.sh`, `commit-guard.sh`, `approve-commit.sh`(`--decision fix`), `.claude/skills/commit/SKILL.md` §6.1, `docs/wiki/security.md` §2, `CLAUDE.md`, `.gitignore`·`settings.json`(마커), `.claude/scripts/test-guards.sh`(대기 게이트 사례 3건).
- 이번 세션의 L-002·L-003 작업은 이 규칙 이전에 시작된 것이라 커밋·푸시까지 마치고 멈춘다. 그 다음부터 규칙이 적용된다.
