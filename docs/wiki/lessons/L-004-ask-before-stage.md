# L-004 · 계획·구현·검증 단계는 자동으로 시작하지 않고 사용자에게 묻고 시작한다

날짜: 2026-09-03 | 어디서(P / FIX / CR): 하네스 (P0-compose U1 을 backend-agent 에 자동 위임한 직후 사용자 지시) | Refs: harness L-004 L-002

## 무슨 일이 있었나
- P0-compose 에서 메인 세션이 계획 승인을 받자마자 architect → verifier → (개정) architect → verifier → backend-agent 를 연달아 스스로 띄웠다. 사용자는 각 단계가 시작되는 시점을 통제하지 못했다.
- 사용자: "계획, 구현, 검증은 자동으로 시작하지 않고 나에게 물어보고 시작해줘."

## 왜 그랬나
- L-002 가 "누가 하는가"(역할·모델)는 정했지만 "언제 시작하는가"는 정하지 않았다. 자율 실행 기본값대로 다음 단계로 넘어갔다.
- 단계마다 토큰 비용이 크고(서브에이전트 4~8만 토큰), 사용자가 중간 결과를 보고 방향을 바꿀 기회가 단계 사이에 있어야 한다.

## 다음부터
규칙으로 바꿀 것이 있으면 어느 파일(CLAUDE.md · 스킬 · 훅)을 고쳤는지 적는다.
- **규칙**: architect / backend-agent / eval-agent / verifier 를 띄우기 전에 매번 `AskUserQuestion`(무엇을 · 누구에게 · 왜)으로 시작 승인을 받는다. 승인 직후 `bash .claude/hooks/approve-commit.sh --stage <에이전트>` 가 1회용 마커 `.claude/.stage-approved`(내용 = 에이전트 이름)를 만들고, `delegate-guard.sh`(PreToolUse Agent)가 마커 없거나 이름이 다르면 거부, 맞으면 소비한다. 재검증·개정 반복도 매번 묻는다. 조사용 에이전트(Explore, claude-code-guide 등)는 게이트 밖이다.
- 고친 파일: `.claude/hooks/delegate-guard.sh`(신설), `.claude/hooks/approve-commit.sh`(`--stage`), `.claude/settings.json`(Agent matcher, 마커 쓰기 deny), `.gitignore`, `.claude/skills/devlog/SKILL.md`(원칙 절), `CLAUDE.md` 개발 프로세스, `.claude/scripts/test-guards.sh`(위임 게이트 사례 4건).
- 이 지시 직전에 시작된 backend-agent U1 은 마치게 두고, 그 이후 위임부터 적용한다.
