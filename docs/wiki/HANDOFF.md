# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 20:30
active: none | frozen: none | 브랜치: dev (origin/dev = 3abe513, main = b4ddfef, 승격 대기 5커밋)

## 지금 어디까지
- 마지막으로 끝낸 것: P0-embed-pilot **완료·승인·커밋·dev 푸시**(a66f1e2 U2, e4ab0a4 U3+done, 3abe513 verify-impl 수정). 이어서 하네스 L-002(역할별 모델 분리: architect=opus, backend=sonnet, eval=opus, verifier(신설)=fable, verify-plan/impl 이 검증자=verifier 강제) 작성, 자가 점검 68 ok (evidence/20260903-test-guards-L002.txt).
- (이전) P0-embed-pilot U2·U3 완료. 파일럿 실행 결과 두 모델 모두 D4 기준 통과, **확정: OpenAI text-embedding-3-small, N=1536** (`reports/embed_pilot.md`). D04·S3.1·review-index R5·registry·backlog 반영. 04-review 작성, verify-impl FAIL 0 (`evidence/20260903-verify-impl-2.txt`; 1차 FAIL 은 verify-impl.sh 제목 패턴 버그 → 소견 F-445cda 해소, 스크립트 수정).
- 이어서 하네스 L-003(dev 푸시 뒤 멈춤: `.awaiting-decision` 마커, stage-gate·commit-guard 강제, commit 스킬 §6.1) 작성, 자가 점검 72 ok (evidence/20260903-test-guards-L003.txt).
- 진행 중인 것: **하네스 커밋 2건(L-002, L-003) 승인 대기**. 승인 후 커밋 → `git push origin dev` → 훅이 결정 대기 마커 생성 → **사용자에게 승격/수정을 묻고 멈춘다(L-003)**.
- 커밋 안 된 변경: L-002 묶음(agents/verifier.md, backend-agent model, verify-plan/impl 검증자 검사, templates, devlog 스킬, CLAUDE.md, lessons/L-002) + L-003 묶음(stage-gate·commit-guard·approve-commit·commit-cleanup, commit 스킬, security.md, CLAUDE.md, .gitignore, settings.json, test-guards, lessons/L-003) + registry·journal·evidence.

## 바로 다음에 할 것 (순서대로)
1. L-002 커밋 → L-003 커밋 → `git push origin dev` → AskUserQuestion(승격/수정/보류) → 멈춤.
2. 사용자 결정 뒤 `/devlog start P0-compose`(사용자 선택). **새 흐름**: architect(opus)에 01-plan 초안 위임 → verifier(fable)에 02-plan-verify 위임 → 사용자 승인 → backend-agent(sonnet) 구현 → verifier 04-review. 메인 세션은 점검표를 직접 쓰지 않는다.
3. 사용자 직접: AWS Budgets $10/$30/$50. main 승격은 dev 실서버 검증 후 `/commit release`.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P0-embed-pilot/04-review.md` §7(다음 패키지에 넘기는 것), `reports/embed_pilot.md` 결론
- `lessons/L-001-dev-branch.md`, `L-002-role-model-separation.md`, `L-003-stop-after-dev-push.md`

## 열린 질문 · 사용자 결정 대기
- L-002·L-003 커밋 승인. dev 푸시 뒤 승격/수정 결정(실서버 확인 후). 다음 패키지는 P0-compose 로 결정됨.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **푸시는 `git push origin dev` 만**. main 직접 푸시는 훅이 거부. 승격은 `/commit release` → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다. 정리 훅은 PostToolUse.
- **dev 푸시 뒤 `.claude/.awaiting-decision` 이 있으면** 새 작업·커밋이 막힌다. 사용자에게 승격/수정을 물어 `approve-commit.sh --release` 또는 `--decision fix` 로 푼다.
- Bash 도구는 `\` 를 하나로 줄인다. 백슬래시가 든 패치는 Write 로 파일에 쓴 뒤 실행한다(L-003 패치에서 SyntaxError 로 한 번 실패).
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 키는 이제 채워져 있다(사용자 확인 2026-09-03).
- Windows 콘솔: 파이썬 출력은 스크립트에서 UTF-8 로 reconfigure. evidence 에 `cut -c` 로 잘린 한글은 깨져 보일 수 있다(내용 문제 아님).
- 임계치 T_merge/T_new 는 모델별 스케일이 달라 P4 에서 보정한다(reports/embed_pilot.md 관찰).
