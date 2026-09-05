# P0-compose · 완료 검토 (04-review)

날짜: 2026-09-05 | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

읽은 것: `01-plan.md`(범위·"하지 않는 것"·U1~U3·수용 기준·리스크·미결), `02-plan-verify.md` §3, `03-log.md` 항목 4개, `05-remediation.md`(F-033bb1 5~7단계·F-0ffff5 4~5단계 "대기"), `evidence/20260903-*`·`20260904-*`, `docs/wiki/INDEX.md` 패키지 표(P0-compose 닫는 R `—`), `decisions/D04-embedding-provider.md`(확정 N=1536, "코드에서 지켜야 할 것"), `decisions/D05-alias-level-embedding.md`("`person_embeddings` 테이블 없음 … `person_aliases.embedding`"), `specs/S3.1-schema-v2.md` 7행(`embedding vector(1536)`, 아래: P1-schema), `security.md` §1·§4, CLAUDE.md 원칙7·8. 구현 파일 전문: `docker-compose.yml`, `docker/initdb/01-vector.sql`, `.env.example`, `scripts/db_check.py`, `tests/test_db_check.py`, `README.md` 119~146행, `registry.md` 32·35~37행. 커밋: `bash .claude/scripts/gitlog.sh P0-compose`(태그 커밋 6건, 미커밋 `docs/wiki/journal.md` 1건).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh P0-compose | tee docs/wiki/packages/P0-compose/evidence/20260905-1127-verify-impl.txt` (04-review 작성 뒤 최종 실행. 사전 실행은 `evidence/20260904-verify-impl-pre.txt` PASS 8 / WARN 1 "04-review 없음")
```
== verify-impl P0-compose  (20260905-1127) ==
................                                                         [100%]
16 passed in 0.11s
PASS  pytest 통과 → evidence/20260905-1127-pytest.txt
PASS  compileall 통과 → evidence/20260905-1127-lint.txt
PASS  태그 P0-compose 커밋 6 건 → evidence/20260905-1127-commits.txt
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: S3.1
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  `SELECT '[1,2,3]'::vector` 성공  ← evidence/20260904-db-check.txt (구현�
PASS  registry 에 P0-compose 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260905-1127-summary.txt ==
exit=0
```
FAIL 0 → `findings.py --source verify-impl` 소견 없음. 05-remediation 의 구현 단계 대기 항목(F-033bb1 5~7, F-0ffff5 4~5)은 아래 §3 정적 검사 출력(`evidence/20260905-1121-review-static.txt`)으로 판정했다 — 05-remediation 의 "확인 결과" 칸은 이 파일을 가리키도록 갱신한다.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| `SELECT '[1,2,3]'::vector` 성공 | evidence/20260904-db-check.txt (구현자 실행, `[ok] SELECT '[1,2,3]'::vector -> [1,2,3]`, `exit code: 0`) ; evidence/20260905-1121-review-db-check.txt (verifier 재현 2회: `POSTGRES_PORT=5433` 경로와 `DATABASE_URL` 경로 모두 `-> [1,2,3]`, `exit=0`, extversion 0.8.6) ; 0ee6e25 | 통과 |

보조 근거(수용 기준은 아니지만 01-plan 범위 항목의 실재):
- compose 기동·healthy: `evidence/20260904-compose-up.txt`, `evidence/20260904-compose-ps.txt`(`Up 7 seconds (healthy)`, `0.0.0.0:5433->5432/tcp`), verifier 시점 `evidence/20260905-1121-review-compose.txt`(`docker compose config --quiet` exit 0, `ps` healthy).
- 확장 생성 initdb: `docker/initdb/01-vector.sql`, `evidence/20260903-vector-ext.txt`(extversion 0.8.6). 커밋 749bb8e.
- `.env.example` 이름 4개·compose `${VAR:-기본값}` 4개: `evidence/20260905-1121-review-static.txt`(`grep -c 'POSTGRES_' .env.example` → 4, `grep -n 'POSTGRES_.*:-' docker-compose.yml` → 8·9·10·12행 + healthcheck 17행). 기본값 `app`/`pass`/`relationship`/`5432` = `.env.example` 16~19행 예시값과 동일.
- 단위 테스트: `evidence/20260905-1121-review-pytest.txt`(6 passed, exit 0).
- README 로컬 DB 절·registry: `README.md` 121~144행, `docs/wiki/registry.md` 32·35·36·37행. 커밋 7397966.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
모두 verifier 가 2026-09-05 직접 실행. 컨테이너 `capstone2-postgres-1`(pg16, 5433 매핑)이 떠 있어 실접속 재현이 가능했다. `.env` 는 읽지도 존재 확인도 하지 않았다.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 테스트가 실패 조건을 실제로 검사하는가 — 변이 1: 경고 문장에 비밀번호 값을 덧붙인 `db_check.py` 복사본(scratchpad, 원본 미수정) | `pytest tests/test_db_check.py -q` (복사본 대상) | evidence/20260905-1121-review-mutation.txt — `test_mismatch_warns_variable_name_only_no_secret_value` FAILED (`assert 'pwtwo' not in …`), 1 failed 5 passed |
| 같은 것 — 변이 2: `POSTGRES_PORT` 불일치 비교를 항상 거짓으로 | 위와 같음 | 같은 파일 — 같은 테스트 FAILED (`assert 'POSTGRES_PORT' in …`), 1 failed 5 passed. 결론: 테스트 6건 중 핵심 1건이 "이름만 경고·비밀번호 값 부재" 두 요건을 실제로 잡는다. 항상 통과하는 테스트가 아니다 |
| 없는 포트로 접속 → 비정상 종료, 비밀번호 미출력 | `POSTGRES_PORT=5599 python scripts/db_check.py` | evidence/20260905-1121-review-db-check.txt — `ConnectionTimeout`, `exit=1`; 파일 전체에 토큰 `pass` 0회(`grep -c -w pass` → 0) |
| 없는 DB → 비정상 종료 | `POSTGRES_PORT=5433 POSTGRES_DB=nonexistent_db python scripts/db_check.py` | 같은 파일 — `FATAL: database "nonexistent_db" does not exist`, `exit=1` |
| `DATABASE_URL` ↔ `POSTGRES_PORT` 불일치 → 변수 이름만 경고, 접속은 `DATABASE_URL` 우선 | `DATABASE_URL=<.env.example 14행 예시값> POSTGRES_PORT=5433 python scripts/db_check.py` | 같은 파일 — 1행 `[warn] POSTGRES_PORT 가 DATABASE_URL 과 다르다`(값 없음), `source=DATABASE_URL port=5432`. 5432 는 무관 컨테이너라 인증 실패 `exit=1` — 03-log U2 발견과 일치하는 기대된 결과 |
| compose 파일 유효성·비밀값·볼륨 삭제 옵션 부재 | `docker compose config --quiet` ; `docker compose config \| grep -v -i password` ; `grep -n -E 'down +-v\|volume +rm\|prune\|--force\|DROP \|TRUNCATE' docker-compose.yml docker/initdb/01-vector.sql scripts/db_check.py` | evidence/20260905-1121-review-compose.txt(exit 0, 서비스 1개·볼륨 `capstone2_pgdata`·initdb 읽기전용 bind), evidence/20260905-1121-review-static.txt(실행 파일 매치는 `docker-compose.yml:2` 주석 경고문 1건뿐) |
| 키 문자열·실제 비밀번호 부재 | `grep -n -E 'sk-…\|AKIA…\|-----BEGIN\|api[_-]?key…' .env.example docker-compose.yml docker/initdb/01-vector.sql scripts/db_check.py tests/test_db_check.py README.md` ; `grep -n -i password …` | evidence/20260905-1121-review-static.txt — 키 패턴 0건(exit 1); `password` 등장 줄은 `.env.example:17 POSTGRES_PASSWORD=pass`(공개 예시값), compose 9행 `${POSTGRES_PASSWORD:-pass}`, db_check 의 필드명·`DEFAULT_PASSWORD = "pass"`·주석뿐 |
| 범위 침범 — 테이블 생성·Alembic·Dockerfile 없음("하지 않는 것" 1·2·4) | `grep -n -i -E 'CREATE TABLE\|ALTER TABLE\|alembic' docker/initdb/*.sql scripts/db_check.py docker-compose.yml` ; `ls docker/initdb alembic* Dockerfile` | 같은 파일 — 0건(exit 1); `docker/initdb` 에 `01-vector.sql` 하나, `alembic*`·`Dockerfile` 없음. 커밋 749bb8e·0ee6e25·7397966 의 파일 목록(§1 gitlog)에도 범위 밖 경로 없음 |
| 03-log Refs ↔ 커밋 본문 Refs 일치 | `git log -1 --format=%b <h> \| grep '^Refs:'` × 4 vs `grep -n '^- Refs:' 03-log.md` | 같은 파일 — 23d8700 `P0-compose D4 D5 S3.1 F-033bb1 F-0ffff5 (L-002)`, 749bb8e·0ee6e25 `… F-033bb1`, 7397966 `… F-0ffff5` — 03-log 11·18·27·34행과 태그 일치 |
| registry: README 새 행 금지(F-0ffff5 4단계) / 신규 행 3개 | `grep -c '\| README.md \|' docs/wiki/registry.md` ; `grep -n P0-compose docs/wiki/registry.md` | 같은 파일 — README 행 1(32행, 소유 `하네스`, 비고에 "P0-compose: 로컬 DB 절 추가(2026-09-04), pg16 태그는 P9-infra 에서 재확인"); 35·36·37행 compose·initdb·db_check 신규, 소유 P0-compose |
| README 에 U2 발견(5432 충돌 → 두 값 동시 변경)·미결 1(pg16) 반영 | `grep -n 'docker compose up -d' README.md` + 142·143행 직접 확인 | `README.md` 127행(F-0ffff5 5단계), 142행 "`.env`의 `POSTGRES_PORT`와 `DATABASE_URL`의 포트를 **같이** 다른 값(예: 5433)으로 바꾼다", 143행 "`pgvector/pgvector:pg16`으로 시작한다. … P9-infra에서 이 태그를 재확인", 144행 P1-schema 선행 조건 메모, 141행 볼륨 삭제 금지(옵션 문자열 없이 풀어 씀) |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- 해당 없음. INDEX.md 패키지 표 63행 `| P0-compose | 로컬 docker-compose pgvector | backend-agent | — |` — 닫는 R 없음(01-plan 미결 3). review-index.md 변경 불필요.

## 5. registry.md 에 올린 산출물
- 35행 `docker-compose.yml` (스크립트, P0-compose, 비고: pg16·P9-infra 재확인)
- 36행 `docker/initdb/01-vector.sql` (스크립트, P0-compose)
- 37행 `scripts/db_check.py` (스크립트, P0-compose, 비고: 테스트 `tests/test_db_check.py`)
- 32행 `README.md` — 새 행 아님, 기존 행(소유 `하네스`) 비고만 갱신. `| README.md |` 행 수 1 유지.
- 커밋 열은 이 파일의 관행대로 `pending`(P0-embed-pilot 26~28행도 같음) — `/devlog done` 에서 메인 세션이 확정.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
필수(완료를 막는 것): **없음.** verify-impl FAIL 0, 수용 기준 통과, 05-remediation 대기 단계 모두 기대값 충족(F-033bb1 5: 4 / 6: 4+1 / 7: 경고·README 확인, F-0ffff5 4: 1 / 5: 127행).

기록만 하는 편차·관찰(조치는 메인 세션·다음 패키지 판단):
- O1 **db_check 가 서버 버전을 찍지 않는다.** 01-plan 15행 "서버 버전·확장 버전·쿼리 결과를 표준출력에 찍고" 중 서버 버전(`SELECT version()`)이 빠졌다(`scripts/db_check.py` 154~165행은 확장 생성·extversion·캐스트 3개만). 수용 기준·보안과 무관하고 extversion(0.8.6)과 `compose ps` 의 이미지 태그로 버전 추적은 가능하다. 미결 1(pg16 ↔ RDS 메이저) 확인 때 서버 버전 출력이 있으면 편하므로 P1-schema 에서 DB 모듈을 만들 때 넣기를 권고. FIX 불필요.
- O2 **구현자 evidence 는 `POSTGRES_*` 경로로만 성공을 보였다.** `evidence/20260904-db-check.txt` 의 `source=POSTGRES_*` — 에이전트가 `.env` 를 로드하지 않으므로 정상(security.md §1). `DATABASE_URL` 경로의 성공은 verifier 가 `evidence/20260905-1121-review-db-check.txt` 마지막 블록에서 보강했다(`source=DATABASE_URL port=5433`, exit 0).
- O3 `tests/test_db_check.py` 는 01-plan 산출물 목록에 없던 파일이고 registry 에 독립 행이 없다(37행 비고에만). P0-embed-pilot 은 테스트에 행(27행)을 두었다 — 관행을 하나로 맞출지 메인 세션 판단. 범위 침범은 아니다(범위 안 스크립트의 테스트).
- O4 `evidence/20260903-compose-config.txt`(U1, 커밋 749bb8e)에 해석된 환경값이 들어 있다. 02-plan-verify §3 은 "config 출력은 evidence 에 넣지 않는다"고 했다. 값은 `pass` 등 공개 예시값이라 유출은 아니지만, 앞으로 `config` 출력을 남길 때는 `--quiet` 또는 password 줄 제외로 할 것(이번 verifier evidence 는 그렇게 했다).
- O5 `scripts/db_check.py` 132행이 `POSTGRES_HOST` 를 읽는다 — `.env.example` 에 없는 이름. 기본값 `localhost` 라 동작에 영향 없음. 이름을 쓸 거면 `.env.example` 에 올리고, 아니면 제거 — P1/P2 에서 DB 설정 모듈로 흡수될 때 정리.
- O6 로컬 환경 상태: 5432 는 무관 컨테이너가 점유, 이 프로젝트 컨테이너는 셸 변수로 5433 매핑(`evidence/20260905-1121-review-compose.txt`). 영구 해결은 사용자 몫(README 142행) — `.env` 의 `POSTGRES_PORT` 와 `DATABASE_URL` 포트를 같이 바꾸거나 무관 컨테이너 정리. verifier 는 `.env` 상태를 모른다.
- O7 위키 정리 남음(메인 세션): `README.md` 69행 진행 상태 "구현 완료 · 검증 대기" → 갱신, `docs/wiki/journal.md` 미커밋 변경 1건, `CURRENT.md` active 해제는 `/devlog done`.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- 로컬 DB 접속: 이름 4개 `POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB / POSTGRES_PORT`(+`DATABASE_URL`, 같은 값 유지). compose 기본값 = `.env.example` 예시값(`app`/`pass`/`relationship`/`5432`). 호스트 `localhost`.
- 확장: `vector` 0.8.6, 이미지 `pgvector/pgvector:pg16`(PostgreSQL 16). P1-schema 의 `person_aliases.embedding vector(1536)`(S3.1 7행, D4 확정) 컬럼은 이 확장이 이미 있는 DB 위에 만든다 — 마이그레이션에서 `CREATE EXTENSION IF NOT EXISTS vector` 를 한 번 더 두어도 무해(멱등).
- P1-schema 는 initdb 에 SQL 을 추가하지 말고 Alembic 으로 테이블을 만든다(01-plan "하지 않는 것" 1·2 — 이 패키지의 initdb 는 확장까지만).
- 재현 명령: `docker compose up -d` → `docker compose ps`(healthy) → `python scripts/db_check.py`(rc 0). 포트 충돌 시 `POSTGRES_PORT` 와 `DATABASE_URL` 포트 동시 변경(README 142행).
- 볼륨 `capstone2_pgdata` 삭제는 사용자만(security.md §4). 스키마 초기화가 필요하면 Alembic downgrade 로.
- 미결 1(pg16 ↔ RDS 메이저 버전)은 P9-infra 착수 시 재확인 — `registry.md` 32·35행 비고와 README 143행에 메모됨.
- 의존성 선언 파일이 아직 없다(03-log U2: "requirements 파일은 P1/P2 백엔드 골격에서 추가"). `psycopg[binary]` 3.3.5 가 첫 항목.

결과: 완료
승인: 사용자 (2026-09-05)