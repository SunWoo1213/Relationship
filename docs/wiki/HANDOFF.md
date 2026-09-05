# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-05 11:35 (P0-compose 완료 처리, 커밋 직전)
active: none | frozen: none | 브랜치: dev (origin/dev = main = 0ee6e25. 로컬 dev 는 7397966·7d20a34 + 이번 완료 커밋 = 3개 앞섬, **미푸시**)

## 지금 어디까지
- **P0-compose 완료(2026-09-05)** — verifier(fable) 04-review `결과: 완료`, 사용자 승인. verify-impl PASS 10/WARN 0/FAIL 0 (`evidence/20260905-1127-verify-impl.txt`). 부정 케이스 5종을 verifier 가 직접 실행(`evidence/20260905-1121-review-{compose,db-check,mutation,pytest,static}.txt`). 소견 F-033bb1·F-0ffff5 해소, 열린 소견 0. 닫는 R 없음.
- 이번 세션 커밋: 7d20a34(위키 정리: HANDOFF·journal, 03-log pending→해시). 완료 커밋은 이 HANDOFF 와 함께 `/commit` 중.
- 04-review §6 관찰 O1~O7 은 조치 없이 기록(P1-schema 인계): db_check.py 서버 버전 미출력(`SELECT version()` 권고), `POSTGRES_HOST` 이름이 .env.example 에 없음, tests/test_db_check.py registry 독립 행 없음, evidence 에 compose config 해석값(예시값) 포함 → 앞으로 `--quiet`, 5432 영구 해결은 사용자 몫.
- **P1-schema 인계(04-review §7)**: 이름 4개 + `DATABASE_URL` 동일값, compose 기본값 = `.env.example` 예시값; `vector` 0.8.6 / `pgvector/pgvector:pg16`; `person_aliases.embedding vector(1536)` 은 Alembic 으로(initdb 에 SQL 추가 금지); 볼륨 삭제는 사용자만; pg16↔RDS 메이저는 P9-infra 재확인; 의존성 선언 파일 없음(`psycopg[binary]` 3.3.5 가 첫 항목).
- .env.example 은 추적 유지 확정(2026-09-04). 다시 꺼내지 않는다.
- Docker: 컨테이너 capstone2-postgres-1 은 **호스트 5433**(5432 는 무관한 finance_postgres). 셸 변수 없이 `docker compose up -d` 하면 충돌 — README 로컬 DB 절 안내대로 .env 포트를 바꾸거나 무관 컨테이너 정리(사용자 몫).
- 팀 밑작업(Agent Teams): 사용자 결정 **보류**.

## 바로 다음에 할 것 (순서대로)
1. 완료 커밋 `/commit`(진행 중) → **dev 푸시**(7397966·7d20a34·완료 커밋) → L-003: `.claude/.awaiting-decision` 생기면 승격/수정/보류를 묻고 멈춘다.
2. 승격이면 `approve-commit.sh --release` → `git push origin dev:main` → HANDOFF "main = <hash>".
3. 다음 패키지는 사용자 선택: **P0-cost**(eval-agent, LLM 비용 실측, R13) 또는 **P1-schema**(backend-agent, 스키마 v2 Alembic, 의존: D4 차원·compose 모두 충족). `/devlog start <id>` — architect 위임 전 AskUserQuestion + `--stage architect`(L-004).

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P0-compose/04-review.md` §6·§7(다음 패키지 인계), `docs/backlog.md` P0/P1 절
- `lessons/L-001-dev-branch.md`, `L-002-role-model-separation.md`, `L-003-stop-after-dev-push.md`, `L-004`(위임 게이트)

## 열린 질문 · 사용자 결정 대기
- dev 푸시 뒤 승격 여부(L-003).
- 다음 패키지 선택(P0-cost / P1-schema).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). 메인 세션이 직접 쓰면 verify-plan/impl 이 FAIL.
- **위임은 묻고 시작**(L-004): architect/backend-agent/eval-agent/verifier 는 AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 마커 없으면 delegate-guard 가 거부.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` 이 생기면 승격/수정을 묻고 멈춘다(L-003). 승격은 `approve-commit.sh --release` → `git push origin dev:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다. 정리 훅은 PostToolUse.
- Bash 명령 문자열에 훅 금지 문구(볼륨을 지우는 compose 옵션, 강제 푸시 옵션, DROP)가 **텍스트로라도** 들어가면 차단된다. 그런 문구가 든 문서는 Write 도구로 쓴다.
- `.env` 존재 확인(`test -f .env`)도 safety-guard 가 막는다. 스크립트가 키 부재를 스스로 보고하게 한다.
- registry 에 README 행이 이미 있다(하네스 소유). 새 행을 만들지 말고 비고만 갱신한다.
