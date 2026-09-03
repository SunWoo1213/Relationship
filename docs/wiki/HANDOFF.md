# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 19:25
active: P0-embed-pilot | frozen: none | 브랜치: dev (main = b4ddfef, 승격 대기 커밋은 gitlog.sh 참조)

## 지금 어디까지
- 마지막으로 끝낸 것: (1) 하네스 L-001 — 브랜치 전략(dev 작업·푸시, main 은 `/commit release` 로 승격)과 에이전트 git log 연동(`gitlog.sh`, `.claude/gitlog.md`, agents 3종·devlog 단계). 자가 점검 68 ok (`docs/wiki/evidence/20260903-test-guards-L001.txt`). (2) P0-embed-pilot U1 — `scripts/embed_pilot.py` + `tests/test_embed_pilot.py`, pytest 10 passed (`packages/P0-embed-pilot/evidence/20260903-pytest-U1.txt`).
- 진행 중인 것: **커밋 2건 승인 대기** — (a) `harness(L-001)` 하네스 변경, (b) `feat(P0-embed-pilot)` U1. 승인되면 순서대로 커밋 후 `git push -u origin dev`(첫 dev 푸시).
- 커밋 안 된 변경: 위 두 묶음 전부(`git status --short`).

## 바로 다음에 할 것 (순서대로)
1. 커밋 (a) 하네스 L-001 → 커밋 (b) U1 → `git push -u origin dev`.
2. U2: `python scripts/embed_pilot.py` (모델 2개, `.env`의 `OPENAI_API_KEY` 필요 — 없으면 rc=2 로 멈추므로 사용자에게 작성 요청). 출력을 `packages/P0-embed-pilot/evidence/<ts>-embed-pilot-run.txt`에 tee, `reports/embed_pilot/*.json` 생성, `reports/embed_pilot.md`(행렬 2종 요약·판정·선택 근거 1문단·확정 N) → `/commit`.
3. U3: D04 카드 갱신 이력(모델·N), S3.1 `vector(N)` 주석, review-index R5 상태, registry 행 → `/commit` → `/devlog done`.
4. main 승격은 사용자가 dev 를 실서버에서 검증했다고 말한 뒤 `/commit release`.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P0-embed-pilot/01-plan.md` 작업 단위, `03-log.md` 마지막 2항목
- `decisions/D04-embedding-provider.md` "코드에서 지켜야 할 것", `lessons/L-001-dev-branch.md`

## 열린 질문 · 사용자 결정 대기
- 커밋 (a)(b) 승인. `.env`에 `OPENAI_API_KEY` 존재 여부(에이전트는 확인 불가).
- 사용자 직접 항목: AWS Budgets $10/$30/$50 (backlog 착수 준비).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **푸시는 `git push -u origin dev` 만** 허용된다. `origin main` 직접 푸시는 훅이 거부한다. main 승격은 `/commit release`(승격 마커 `--release`) → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다(commit-guard 는 PreToolUse 시점에 마커를 본다). 정리 훅은 PostToolUse 라 같은 명령 안에서 `ls` 로 보면 마커가 남아 있는 것처럼 보인다.
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 스크립트가 키 부재를 스스로 보고하게 한다.
- 행렬 "2종"은 OpenAI 모델 2개로 해석(01-plan 범위 절). 타 공급자 비교는 별도 작업.
