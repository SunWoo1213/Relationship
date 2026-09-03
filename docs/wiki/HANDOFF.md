# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 (하네스 구축 완료 시점)
active: none | frozen: none

## 지금 어디까지
- 마지막으로 끝낸 것: 개발 프로세스 하네스 전체. 위키 카드(R1~R20 색인, D01~D10, S3.1~S3.7), 템플릿 9종, 훅 9종, 스크립트 4종(verify-plan, verify-impl, findings.py, test-guards), 스킬 commit/devlog, 보안·검증 카드. 자가 점검 64 ok (`docs/wiki/evidence/20260903-test-guards.txt`).
- 진행 중인 것: **첫 커밋 승인 대기.** 초안은 `.claude/commit-draft.txt`. origin = github.com/SunWoo1213/Relationship.git, `core.hooksPath=.githooks` 설정됨.
- 커밋 안 된 변경: 전부 (커밋 0건).

## 바로 다음에 할 것 (순서대로)
1. 사용자가 첫 커밋(+푸시) 승인 → `bash .claude/hooks/approve-commit.sh [--push]` → 명시 경로 `git add` → `git commit -F .claude/commit-draft.txt` → (`git push -u origin main`).
2. 사용자가 직접: AWS Budgets $10/$30/$50, `.env` 작성(OPENAI_API_KEY, ANTHROPIC_API_KEY).
3. `/devlog start P0-embed-pilot` (D4: OpenAI 임베딩으로 시작 — 카드 `decisions/D04-embedding-provider.md`). 이어서 P0-cost, P0-compose.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`
- 활성 패키지가 생기면 `packages/<id>/01-plan.md` 작업 단위와 `03-log.md` 마지막 2항목

## 열린 질문 · 사용자 결정 대기
- 첫 커밋 승인 여부(커밋만 / 커밋+푸시 / 초안 수정).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- 제품 코드는 `CURRENT.md active` 등록 후에만 쓸 수 있다(훅). 문서·하네스는 면제.
- 커밋은 `/commit` 절차로만. `git add -A`/`.` 금지. 푸시도 승인 마커 필요.
- Bash 도구 명령 문자열에서 이중 백슬래시가 하나로 줄어든다. 백슬래시·마커 문자열(`.commit-approved`)이 들어가는 파일은 Write/Edit 도구로 쓴다.
- 훅은 명령 텍스트를 검사한다. 테스트용 금지 문자열도 걸리므로 시험은 `.claude/scripts/test-guards.sh`로.
