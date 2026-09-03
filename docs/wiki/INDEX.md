# docs/wiki — 참고자료 색인

> 이 위키는 **필요할 때 꺼내 보는 참고자료**다. 전문을 읽지 않는다.
> 검증(R) → 결정(D) → 명세(S) → 패키지(P) → 커밋(Refs) 이 한 사슬로 이어져 있고, 카드마다 "위/아래/이웃" 링크가 있어 흐름을 따라가면 된다.

## 한 장 흐름

```
기획서 docs/proposal.md (원본, 본문 불변)
   │ 검증
   ▼
R1~R20  review-index.md ── 한 줄 + 상태 + "다음 카드"
   │ 결정
   ▼
D1~D10  decisions/ ── 결정·이유·파급·"코드에서 지켜야 할 것"
   │ 명세
   ▼
S3.1~S3.7  specs/ ── 스키마·툴·ER·ask_user·메모리·브리핑·평가
   │ 구현 (docs/backlog.md 순서, P4 게이트)
   ▼
P0~P11  packages/<id>/ ── 01-plan → 02-plan-verify(+승인) → 03-log(커밋마다) → 04-review(+증거) 
   │ 커밋 (Refs: P D S R)                      ↑ evidence/ 파일이 증거
   ▼
journal.md (시간순) · registry.md (무엇이 있는가) · HANDOFF.md (지금 어디, 다음 무엇)

기획서가 바뀌면: changes/CR-nnn ── 이 사슬을 거꾸로 타고(R→D→S→P→git log --grep) 영향 범위를 구한다
```

## 상황별 읽기 경로 (이 순서로, 이것만)

| 상황 | 읽는 것 | 그다음 하는 것 |
|------|---------|----------------|
| 세션 시작·재개·압축 후 | `HANDOFF.md`(자동 주입) → `CURRENT.md` | **중단된 작업·커밋 안 된 변경이 있으면 다른 일보다 먼저** 사용자에게 목록을 보이고 우선순위를 묻는다(`/devlog resume`) |
| 새 패키지 착수 | `docs/backlog.md` 해당 항목 → `review-index.md`의 R 행 → 그 행의 D·S 카드 → `registry.md`(이미 있는지) | `/devlog start <id>` (계획 → 기계 검증 → 승인) |
| 코드 쓰는 중 | 활성 패키지 `01-plan.md` 작업 단위 · 해당 S 카드 · D 카드 "코드에서 지켜야 할 것" · `security.md` | 단위 끝나면 `/commit` |
| 커밋 | `03-log.md` 마지막 항목 · `verification.md` 증거 규칙 | `/commit` (초안 → 승인 → 커밋) |
| 버그·문서 불일치 | `templates/fix.md` | `/devlog fix` |
| 패키지 완료 | `04-review` 템플릿 · `verification.md` | `bash .claude/scripts/verify-impl.sh <id>` → `/devlog done` |
| 기획서 변경 | `templates/change-request.md` · 관련 R 행 | `/devlog change` (동결 → 영향 분석 → 이행) |
| 컨텍스트가 길어짐 | — | `/devlog handoff` (HANDOFF 갱신) |

## 태그 어휘 (커밋 `Refs:` · 계획서 · 로그 · 코드 docstring 공통)

| 태그 | 뜻 | 카드 위치 |
|------|----|-----------|
| `P0`~`P11` | 작업 패키지 (P0 = 착수 준비) | `packages/<id>/` |
| `D1`~`D10`, `D11+` | 설계 결정 | `decisions/Dnn-*.md` |
| `R1`~`R20` | 기획서 검증 항목 | `review-index.md` → 원문 `docs/proposal-review.md` |
| `S3.1`~`S3.7` | 설계 명세 | `specs/S3.x-*.md` |
| `원칙1`~`원칙9` | 불변 원칙 | `CLAUDE.md` |
| `FIX-nnn` | 수정 기록 | `fixes/` |
| `CR-nnn` | 기획서 변경 요청 (출구 절차) | `changes/` |
| `L-nnn` | 교훈 | `lessons/` |

`git log --oneline --grep 'D5'` → 어떤 커밋이 어떤 결정에 기대는지. 기획서 변경 시 영향 범위를 구하는 방법이다.

## 패키지 id (폴더 이름 = 커밋 scope)

| id | 내용 | 담당 | 닫는 R |
|----|------|------|--------|
| `P0-embed-pilot` | 임베딩 공급자 파일럿 — OpenAI 로 시작 (D4) | backend-agent | R5 |
| `P0-cost` | LLM 비용 실측 | eval-agent | R13 |
| `P0-compose` | 로컬 docker-compose pgvector | backend-agent | — |
| `P1-schema` | 스키마 v2 마이그레이션 | backend-agent | R8 R9 |
| `P1-pilot-dataset` | 파일럿 데이터셋 30~50건 | eval-agent | — |
| `P2-tools` | 툴 7종 v2 | backend-agent | R6 R7 R10 R18 |
| `P3-er` | ER 4단계 + 확신도 + trace | backend-agent | R4 R9 |
| `P3-baselines` | 베이스라인 3종 | eval-agent | — |
| `P4-pilot-eval` | **게이트** 파일럿 평가 · 보정표 · 곡선 | eval-agent | R3 R4 |
| `P5-loop` | 에이전트 루프 + ask_user 재개 | backend-agent | R6 R7 |
| `P6-memory` | 승격 + 패턴 + fact_sources | backend-agent | R8 R11 |
| `P6-briefing` | 브리핑 + 주기 작업 + 수동 트리거 | backend-agent | R12 R19 |
| `P7-push` | 웹푸시 | backend-agent | R12 |
| `P8-frontend` | 프론트 3화면 + PWA | frontend-agent(신설) | — |
| `P9-infra` | Terraform + Actions + Caddy | infra-agent(신설) | R14 |
| `P10-final-eval` | 150건 + 최종 평가 | eval-agent | — |
| `P11-demo` | 데모 리허설 | 사용자 | R15 |

의존·수용기준은 `docs/backlog.md`가 권위. **P4 이전에 P5 이후를 시작하지 않는다.** 한 번에 활성 패키지는 하나.

## 파일 지도

| 경로 | 무엇 | 언제 |
|------|------|------|
| `HANDOFF.md` | 지금 어디까지 · 바로 다음 · 주의 (60줄) | 세션 시작 시 자동 주입 · 작업 단위마다 갱신 |
| `CURRENT.md` | `active:` 활성 작업 · `frozen:` 열린 CR | 훅이 읽는다 |
| `journal.md` | 시간순 한 줄 로그 (append-only) | 최근 맥락 `tail` |
| `registry.md` | 구현 목록 — 모듈·엔드포인트·툴·테이블·테스트 | 단위 시작 전 grep, 커밋마다 추가 |
| `review-index.md` | R1~R20 | R 태그 |
| `decisions/` | D 카드 | D 태그 |
| `specs/` | S 카드 | 구현 시 |
| `packages/<id>/` | 01-plan · 02-plan-verify · 03-log · 04-review · 05-remediation(검증 소견→조치 계획) · evidence/ | 패키지 생애 |
| `fixes/` `changes/` `lessons/` | FIX · CR · L | 해당 시 |
| `verification.md` | 증거 규칙 · 기계 검증 사용법 | 검증할 때 |
| `security.md` | 금지 명령·비밀 취급 · 대안 | 훅이 막았을 때 |
| `templates/` | 위 문서 8종 템플릿 | 새로 만들 때 |

## 절차와 집행

| 절차 | 스킬 | 집행 훅·스크립트 |
|------|------|-----------------|
| 착수·완료·수정·기획서 변경·핸드오프·재개 | `/devlog` | `stage-gate.sh` (active/frozen), `verify-plan.sh`, `verify-impl.sh` |
| 검증 결과 → 조치 계획 → 재검증 루프 | `/devlog` (verification.md "루프") | `findings.py` → `packages/<id>/05-remediation.md` |
| 커밋·푸시 (매 작업 단위, 사용자 승인) | `/commit` | `commit-guard.sh`, `approve-commit.sh`, `commit-cleanup.sh`, `.githooks/pre-commit` |
| 보안 | — | `safety-guard.sh`, `secret-guard.sh`, `settings.json` deny |
| 컨텍스트 소진 대비 | `/devlog handoff` | `handoff-check.sh`(Stop), `session-start.sh`, `precompact.sh` |
