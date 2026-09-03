# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 19:12
active: P0-embed-pilot | frozen: none

## 지금 어디까지
- 마지막으로 끝낸 것: 하네스 첫 커밋 `e062986` 커밋+푸시(origin/main). P0-embed-pilot 계획(01-plan)·계획검증(02-plan-verify, 기계 검증 PASS 23/FAIL 0) 작성, 사용자 승인(2026-09-03). CURRENT active 등록, 03-log 생성, journal START.
- 진행 중인 것: **계획 문서 커밋 승인 대기** (초안 `.claude/commit-draft.txt`, 사용자는 이미 "승인 + 커밋+푸시"를 택했으므로 마커 생성 후 커밋·푸시). 그 다음 U1.
- 커밋 안 된 변경: docs/wiki/packages/P0-embed-pilot/{01-plan,02-plan-verify,03-log}.md, evidence/20260903-verify-plan.txt, CURRENT.md, journal.md, HANDOFF.md.

## 바로 다음에 할 것 (순서대로)
1. 계획 문서 `/commit`(커밋+푸시).
2. U1: `scripts/embed_pilot.py`(호칭 30개, `EmbeddingProvider` 인터페이스 + `OpenAIEmbeddingProvider`, 코사인 행렬, 판정 팀장↔부장님 > 팀장↔이모, `reports/embed_pilot/<model>.json` 저장, 키 없으면 명확히 종료) + `tests/test_embed_pilot.py`(가짜 공급자, 네트워크 없음). pytest 통과 → `/commit`.
3. U2: `.env`의 `OPENAI_API_KEY`로 모델 2개(`text-embedding-3-small`, `text-embedding-3-large`) 실행, 출력을 `packages/P0-embed-pilot/evidence/`에, `reports/embed_pilot.md`(행렬 2종 요약·판정·선택 근거 1문단·확정 N) → `/commit`.
4. U3: D04 카드 갱신 이력(모델·N), S3.1 `vector(N)` 주석, review-index R5 상태, registry 행 → `/commit` → `/devlog done`.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`
- `packages/P0-embed-pilot/01-plan.md` 작업 단위, `03-log.md` 마지막 2항목
- `decisions/D04-embedding-provider.md` "코드에서 지켜야 할 것"

## 열린 질문 · 사용자 결정 대기
- `.env`에 `OPENAI_API_KEY`가 있는지(에이전트는 확인 불가). U2 실행 실패 시 사용자에게 작성 요청.
- 사용자 직접 항목: AWS Budgets $10/$30/$50 (backlog 착수 준비).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- 제품 코드(`scripts/`, `tests/`)는 CURRENT active=P0-embed-pilot 이고 02-plan-verify 에 `결과: 통과`·`승인:` 이 있어야 쓸 수 있다(훅). 지금은 조건 충족.
- 커밋은 `/commit` 절차로만. `git add -A`/`.` 금지. 푸시도 승인 마커 필요. 마커 정리 훅은 PostToolUse라 같은 명령 안에서 `ls`로 확인하면 아직 남아 있는 것처럼 보인다.
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 스크립트가 키 부재를 스스로 보고하게 한다.
- 행렬 "2종"은 OpenAI 모델 2개로 해석(01-plan 범위 절). 타 공급자 비교는 별도 작업.
