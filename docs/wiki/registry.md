# registry — 구현 목록 (무엇이 이미 있는가)

> 목적: **이미 만든 것을 다시 만들거나, 만들었다고 착각하는 것**을 막는다.
> 규칙: 작업 단위를 시작하기 전에 이 표를 `grep` 한다. `/commit` 마다 새 산출물을 한 줄씩 추가하고, `/devlog done` 에서 패키지 행을 확정한다. `verify-plan.sh`(중복 경고)·`verify-impl.sh`(등록 확인)가 이 파일을 읽는다.
> 종류: 모듈 · 엔드포인트 · 툴 · 테이블 · 마이그레이션 · 테스트 · 스크립트 · 데이터셋 · 리포트 · 문서 · 훅 · 스킬

| 종류 | 이름 | 경로 | 패키지 | 커밋 | 비고 |
|------|------|------|--------|------|------|
| 문서 | 기획서 원본 | docs/proposal.md | 하네스 | pending | 본문 수정 금지 |
| 문서 | 검증 20항목 | docs/proposal-review.md | 하네스 | pending | 색인은 wiki/review-index.md |
| 문서 | 해결 계획서 D1~D10·S3.1~3.7·P1~P11 | docs/resolution-plan.md | 하네스 | pending | 카드는 wiki/decisions, specs |
| 문서 | backlog | docs/backlog.md | 하네스 | pending | 수용 기준의 권위 |
| 훅 | 단계 게이트 | .claude/hooks/stage-gate.sh | 하네스 | pending | CURRENT active/frozen |
| 훅 | 커밋 승인 가드·정리·승인 | .claude/hooks/commit-guard.sh, commit-cleanup.sh, approve-commit.sh | 하네스 | pending | |
| 훅 | 보안 가드(명령)·비밀 가드(쓰기) | .claude/hooks/safety-guard.sh, secret-guard.sh | 하네스 | pending | security.md |
| 훅 | 세션 재개·압축·핸드오프 검사 | .claude/hooks/session-start.sh, precompact.sh, handoff-check.sh | 하네스 | pending | HANDOFF.md |
| 훅 | git pre-commit 비밀 검사 | .githooks/pre-commit | 하네스 | pending | core.hooksPath |
| 스크립트 | 계획·구현 기계 검증 | .claude/scripts/verify-plan.sh, verify-impl.sh | 하네스 | pending | verification.md |
| 스크립트 | 검증 출력 → 조치 계획(소견) 동기화 | .claude/scripts/findings.py | 하네스 | pending | packages/<id>/05-remediation.md |
| 스크립트 | 훅 자가 점검 | .claude/scripts/test-guards.sh | 하네스 | pending | 증거: docs/wiki/evidence/ |
| 스킬 | commit · devlog | .claude/skills/commit, .claude/skills/devlog | 하네스 | pending | |
| 스킬 | entity-resolution · eval-harness · agent-observability | .claude/skills/* | 하네스 | pending | 제품 작업법 |
| 에이전트 | architect · backend-agent · eval-agent | .claude/agents/*.md | 하네스 | pending | |
| 스크립트 | git log 요약(에이전트용) · .claude/gitlog.md 스냅샷 | .claude/scripts/gitlog.sh | 하네스 | pending | L-001. session-start·commit-cleanup 훅이 --write 로 갱신 |
| 문서 | 교훈 L-001 브랜치 전략·git log 연동 | docs/wiki/lessons/L-001-dev-branch.md | 하네스 | pending | dev→실서버 검증→main 승격 |
| 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenAIEmbeddingProvider·코사인 행렬·D4 판정 | scripts/embed_pilot.py | P0-embed-pilot | pending | EmbeddingProvider 는 P2/P3 에서 백엔드 모듈로 이동 |
| 테스트 | 임베딩 파일럿 순수 로직(가짜 공급자, 네트워크 없음) | tests/test_embed_pilot.py | P0-embed-pilot | pending | pytest 10 passed |
| 리포트 | 임베딩 파일럿 결과(행렬 2종·선택 근거·N=1536) | reports/embed_pilot.md, reports/embed_pilot/*.json | P0-embed-pilot | pending | 실행 출력 evidence/20260903-embed-pilot-run.txt |
