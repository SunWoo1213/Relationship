# journal — 시간순 로그

> 형식: `- YYYY-MM-DD HH:MM | KIND | 내용 | Refs`
> KIND: START(패키지 착수) · DONE(완료) · COMMIT(훅이 자동 기록) · FIX · DECISION · CR · LESSON · NOTE
> COMMIT 줄은 `commit-cleanup.sh` 가 붙인다. 나머지는 /devlog 절차에서 LLM이 쓴다. 지우거나 고쳐 쓰지 않는다(append-only).

- 2026-09-03 14:20 | NOTE | 하네스 구축 중 세션 중단. 훅·settings.json 까지 작성됨, 스킬·위키 미완 |
- 2026-09-03 15:00 | NOTE | 위키 색인·카드·템플릿, commit/devlog 스킬 작성 재개 |
- 2026-09-03 15:03 | DECISION | D4 갱신: 임베딩은 OpenAI 로 시작, 추후 다른 공급자 API 키로 성능 비교 (사용자 지시) | D4 R5
- 2026-09-03 15:03 | NOTE | 하네스 구축 완료: 위키 카드(R/D/S)·템플릿 9종·훅 9종·스크립트 4종·스킬 commit/devlog·보안 카드·검증 루프. 자가 점검 64 ok (docs/wiki/evidence/20260903-test-guards.txt). 첫 커밋 승인 대기 |
- 2026-09-03 19:00 | COMMIT | e062986 harness(wiki): 개발 프로세스 하네스 구축 — 위키·승인 커밋·보안·핸드오프·검증 루프
- 2026-09-03 19:01 | PUSH | origin e062986
- 2026-09-03 19:10 | START | P0-embed-pilot 착수: 계획 승인(기계 검증 PASS 23/FAIL 0). OpenAI 모델 2개(3-small·3-large)로 호칭 30개 유사도 행렬 → 모델·차원 N 확정 | P0-embed-pilot D4 D5 S3.1 R5
- 2026-09-03 19:09 | COMMIT | b4ddfef docs(P0-embed-pilot): 계획·계획검증 승인, 패키지 착수
- 2026-09-03 19:09 | PUSH | origin b4ddfef
- 2026-09-03 19:20 | DECISION | L-001 브랜치 전략: 작업·푸시는 dev, main 은 실서버 검증 후 /commit release(dev:main)로만 승격. 에이전트 git log 연동(gitlog.sh · .claude/gitlog.md, agents 3종·devlog 단계 추가). 자가 점검 68 ok (docs/wiki/evidence/20260903-test-guards-L001.txt) (사용자 지시) | L-001 security
