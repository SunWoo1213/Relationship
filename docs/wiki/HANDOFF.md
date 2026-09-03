# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 21:10
active: none | frozen: none | 브랜치: dev (origin/dev = 4df323f, **main = 4df323f** 승격 완료, 승격 대기 0)

## 지금 어디까지
- 마지막으로 끝낸 것: P0-embed-pilot **완료·승인·커밋·dev 푸시**(a66f1e2 U2, e4ab0a4 U3+done, 3abe513 verify-impl 수정). 이어서 하네스 L-002(역할별 모델 분리: architect=opus, backend=sonnet, eval=opus, verifier(신설)=fable, verify-plan/impl 이 검증자=verifier 강제) 작성, 자가 점검 68 ok (evidence/20260903-test-guards-L002.txt).
- (이전) P0-embed-pilot U2·U3 완료. 파일럿 실행 결과 두 모델 모두 D4 기준 통과, **확정: OpenAI text-embedding-3-small, N=1536** (`reports/embed_pilot.md`). D04·S3.1·review-index R5·registry·backlog 반영. 04-review 작성, verify-impl FAIL 0 (`evidence/20260903-verify-impl-2.txt`; 1차 FAIL 은 verify-impl.sh 제목 패턴 버그 → 소견 F-445cda 해소, 스크립트 수정).
- 이어서 하네스 L-003(dev 푸시 뒤 멈춤: `.awaiting-decision` 마커, stage-gate·commit-guard 강제, commit 스킬 §6.1) 작성, 자가 점검 72 ok (evidence/20260903-test-guards-L003.txt).
- L-002(64f92e4)·L-003(4df323f) 커밋 후 dev 푸시 완료. `.claude/.awaiting-decision` 생성됨.
- 사용자가 dev 4df323f 를 **main 으로 승격**(2026-09-03, `git push origin dev:main`, RELEASE 기록). 결정 대기 마커 해제.
- 진행 중인 것: `/devlog start P0-compose` 착수. architect(opus)가 `packages/P0-compose/01-plan.md` 초안 작성 완료(U1 compose+initdb / U2 db_check / U3 registry·README, 미결: 이미지 태그 pg16·드라이버 psycopg·포트 변수화). **verifier(fable)가 02-plan-verify 작성 중(서브에이전트 실행 중, 완료 알림 대기)**. Docker 데몬 실행 확인됨(사용자가 켬).
- 사용자 요청으로 루트 `README.md`(프로젝트 전체 소개) 작성 — **커밋 승인 대기**. 클로드 팀(teammates) 밑작업 질문은 claude-code-guide 에이전트가 조사 중(완료 알림 대기).
- 커밋 안 된 변경: 없음.

## 바로 다음에 할 것 (순서대로)
1. README 커밋(푸시는 P0-compose 계획 커밋과 함께 — L-003 마커가 verifier 작업을 막지 않도록). verifier 완료 알림 → 02-plan-verify 결과(통과/보류) 확인(검증자 줄 verifier 필수) → 사용자 승인 → CURRENT active → 계획 커밋 → backend-agent(sonnet) 구현 → verifier 04-review.
2. 이후 커밋·dev 푸시 뒤에는 다시 멈추고 승격/수정을 묻는다(L-003).(사용자 선택). **새 흐름**: architect(opus)에 01-plan 초안 위임 → verifier(fable)에 02-plan-verify 위임 → 사용자 승인 → backend-agent(sonnet) 구현 → verifier 04-review. 메인 세션은 점검표를 직접 쓰지 않는다.
3. 사용자 직접: AWS Budgets $10/$30/$50. main 승격은 dev 실서버 검증 후 `/commit release`.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P0-embed-pilot/04-review.md` §7(다음 패키지에 넘기는 것), `reports/embed_pilot.md` 결론
- `lessons/L-001-dev-branch.md`, `L-002-role-model-separation.md`, `L-003-stop-after-dev-push.md`

## 열린 질문 · 사용자 결정 대기
- 없음. (다음 패키지 P0-compose 로 결정됨)

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **푸시는 `git push origin dev` 만**. main 직접 푸시는 훅이 거부. 승격은 `/commit release` → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다. 정리 훅은 PostToolUse.
- **dev 푸시 뒤 `.claude/.awaiting-decision` 이 있으면** 새 작업·커밋이 막힌다. 사용자에게 승격/수정을 물어 `approve-commit.sh --release` 또는 `--decision fix` 로 푼다.
- Bash 도구는 `\` 를 하나로 줄인다. 백슬래시가 든 패치는 Write 로 파일에 쓴 뒤 실행한다(L-003 패치에서 SyntaxError 로 한 번 실패).
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 키는 이제 채워져 있다(사용자 확인 2026-09-03).
- Windows 콘솔: 파이썬 출력은 스크립트에서 UTF-8 로 reconfigure. evidence 에 `cut -c` 로 잘린 한글은 깨져 보일 수 있다(내용 문제 아님).
- 임계치 T_merge/T_new 는 모델별 스케일이 달라 P4 에서 보정한다(reports/embed_pilot.md 관찰).
