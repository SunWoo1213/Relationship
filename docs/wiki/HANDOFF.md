# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-03 22:05
active: P0-compose | frozen: none | 브랜치: dev (로컬 dev = ae2076f + 계획 커밋 예정, origin/dev = main = 4df323f)

## 지금 어디까지
- 사용자가 dev 4df323f 를 main 으로 승격(2026-09-03). 그 뒤 README(ae2076f, 로컬, 미푸시) 커밋.
- **P0-compose 계획 승인(2026-09-03)** — L-002 첫 적용: architect(opus) 초안 → verifier(fable) 보류 1건(F-033bb1) → 사용자 결정 (a) → architect 개정 → verifier 재검증 통과(FAIL 0/WARN 1, `packages/P0-compose/evidence/20260903-verify-plan-2-final.txt`). CURRENT active: P0-compose.
- 진행 중인 것: **계획 문서 커밋(커밋만, 사용자 승인됨) 진행 중.** 그 다음 backend-agent(sonnet)에 U1 위임.
- 커밋 안 된 변경: packages/P0-compose/*(01·02·03·05·evidence), CURRENT.md, journal.md, HANDOFF.md.
- 팀 밑작업(L-004, Agent Teams): 사용자 결정 **보류**. 조사 요약은 이 세션 답변에 있음(env CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1, teammateMode, TaskCompleted 훅, 팀메이트별 담당 파일 분할). 필요 시 다시 꺼낸다.

## 바로 다음에 할 것 (순서대로)
1. 계획 문서 `/commit`(커밋만. 푸시는 구현 커밋과 함께 — L-003).
2. U1: backend-agent(sonnet)에 위임 — `.env.example` 이름 4개(POSTGRES_USER/PASSWORD/DB/PORT, 예시값 app/pass/relationship/5432) + `docker-compose.yml`(pgvector/pgvector:pg16, `${VAR:-기본값}`, `${POSTGRES_PORT:-5432}:5432`, 이름 있는 볼륨, healthcheck) + `docker/initdb/01-vector.sql`. Docker 데몬 실행 중. → `/commit`.
3. U2: `scripts/db_check.py`(psycopg 우선, 대안은 compose exec psql — 결정은 03-log) — CREATE EXTENSION + `SELECT '[1,2,3]'::vector`, POSTGRES_* 부재 시 compose 기본값과 비교, 어긋난 변수 이름만 경고. 실행 출력을 `packages/P0-compose/evidence/`에 tee → `/commit`.
4. U3: README "로컬에서 해 보기" 절에 로컬 DB(up/check/down, 볼륨 삭제 금지, 포트 바꾸면 DATABASE_URL 도), registry 기존 README 행 비고 갱신(새 행 금지) + compose·initdb·db_check 행 추가 → `/commit` → verifier 04-review → `/devlog done` → dev 푸시 → L-003 멈춤(승격/수정 질문).

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P0-compose/01-plan.md` 작업 단위·리스크, `02-plan-verify.md` §3 참고사항, `03-log.md` 마지막 2항목
- `lessons/L-001-dev-branch.md`, `L-002-role-model-separation.md`, `L-003-stop-after-dev-push.md`

## 열린 질문 · 사용자 결정 대기
- 없음.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). 메인 세션이 직접 쓰면 verify-plan/impl 이 FAIL.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` 이 생기면 승격/수정을 묻고 멈춘다(L-003). 승격은 `approve-commit.sh --release` → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다. 정리 훅은 PostToolUse.
- Bash 명령 문자열에 훅 금지 문구(예: 볼륨을 지우는 compose 옵션, 강제 푸시 옵션)가 **텍스트로라도** 들어가면 차단된다. 그런 문구가 든 문서는 Write 도구로 쓴다. `\\` 도 하나로 줄어드니 패치는 파일로 써서 실행.
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 스크립트가 키 부재를 스스로 보고하게 한다.
- registry 에 README 행이 이미 있다(하네스 소유). P0-compose U3 는 새 행을 만들지 말고 비고만 갱신한다.
