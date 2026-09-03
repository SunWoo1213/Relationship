# P0-compose · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-03 20:11 (verifier 재검증) | 출처: verify-plan | 열림: 2 (필수 0) — 둘 다 계획 단계 해소, 구현 단계(대기)는 04-review 에서 판정 | 해소: 0 (완전 해소는 구현 단계 판정 후)

## F-033bb1 · [권고] 보류 1 건 — 결과는 통과가 될 수 없다
상태: 해소(계획 단계) — 구현 단계는 04-review 에서 판정 | 발견: 2026-09-03 (verify-plan) | 해소: 계획 단계 2026-09-03 20:11 (verifier 재검증, 1~4 완료 / 5~7 대기)

### 증상 (검증 출력 인용)
```
WARN  보류 1 건 — 결과는 통과가 될 수 없다
```

### 원인 분석
- 가설: (verifier 작성, 02-plan-verify.md 점검표 8행 보류) 01-plan 이 compose 환경변수 `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_PORT` 를 `.env` 에서 읽는다고 했지만(12행·42행), 그 이름을 적을 유일한 자리인 `.env.example`(security.md §1 "에이전트는 `.env.example`에 이름만 적는다")에 해당 이름이 없고 01-plan 산출물·U1 에 `.env.example` 갱신이 없다. 그래서 DB 비밀번호·포트의 출처가 `DATABASE_URL`(db_check)과 `POSTGRES_*`(compose) 둘로 갈린다.
- 확인 방법(명령): `grep -n "POSTGRES_" .env.example` (이름이 있는지) / `grep -n "\.env\.example" docs/wiki/packages/P0-compose/01-plan.md` (산출물·U1 에 갱신이 있는지)
- 확인 결과: `grep -n "POSTGRES_" .env.example` → 출력 없음(종료 1). `.env.example` 의 DB 관련 줄은 "DATABASE_URL=postgresql://app:pass@localhost:5432/relationship" 한 줄뿐. 01-plan 에서 `.env.example` 은 12·33·42·43·57행에 "대조"·"동일한 예시값" 용도로만 등장하고 산출물 절(24~30행)에는 없다. 조치 선택지(architect): (a) 산출물·U1 에 `.env.example` 이름 4개 추가를 명시, 또는 (b) compose 는 고정 기본값만 쓰고 `DATABASE_URL` 단일 출처로 하며 42행 "`.env`에서 바꿀 수 있게" 삭제. 해결은 계획 작성자 몫이므로 아래 해결 단계는 비워 둔다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
사용자 결정(2026-09-03): **선택지 (a)** — `.env.example`에 이름 4개를 두고 compose 가 `${VAR:-기본값}`으로 읽으며, `DATABASE_URL`과 값이 같아야 함을 README 안내와 db_check 경고로 알린다. (b)는 채택하지 않는다.
1~4는 계획 문서 수정(architect, 지금), 5~7은 구현 단위 U1·U2·U3 에서 backend-agent 가 수행한다.

| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan.md 산출물 절에 `.env.example` 행 추가(이름 4개 `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_PORT`, 예시값 app/pass/relationship/5432, "`DATABASE_URL`과 같은 값 유지·실제 비밀번호는 `.env`에만" 주석) | `grep -n "^- .env.example" docs/wiki/packages/P0-compose/01-plan.md` | 산출물 절에 `.env.example` 로 시작하는 행 1줄 | 완료 (verifier 실행 20:08 → 26행 1건. `evidence/20260903-remediation-check-2.txt`) |
| 2 | 01-plan.md U1 제목·본문에 `.env.example` 갱신을 첫 작업으로 명시 | `grep -n "U1 .*\.env\.example" docs/wiki/packages/P0-compose/01-plan.md` | U1 줄 1건 매치 | 완료 (verifier 실행 20:08 → 35행 1건, exit 0. 같은 evidence) |
| 3 | 01-plan.md 리스크 절 포트 항목을 결정 (a)로 고쳐 씀 — `.env.example` 이름 4개 + compose `${VAR:-기본값}` + README 안내 + db_check 불일치 경고(비밀번호 값 출력 금지) | `grep -n "POSTGRES_PORT:-5432" docs/wiki/packages/P0-compose/01-plan.md` | 범위·리스크에서 2건 이상 매치 | 완료 (verifier 실행 20:08 → 13·35·44행 3건. 같은 evidence) |
| 4 | 01-plan.md 범위·산출물·U2 에 db_check 불일치 경고 요건 추가(어긋난 **변수 이름만** 출력, 비밀번호 값 금지, 종료 코드 불변) | `grep -c "불일치" docs/wiki/packages/P0-compose/01-plan.md` | 2 이상 | 완료 (verifier 실행 20:08 → 5. 같은 evidence) |
| 5 | (구현 U1) `.env.example` DB 절에 이름 4개 추가 — `.env` 는 건드리지 않는다 | `grep -c "POSTGRES_" .env.example` | `4` (이름 4줄. 주석 문장에는 `POSTGRES_` 문자열을 쓰지 않는다) | 대기 (verifier 확인 20:08 → 현재 0, exit 1 — U1 전이므로 정상) |
| 6 | (구현 U1) `docker-compose.yml` 이 네 변수를 `${VAR:-기본값}`으로만 읽고 기본값이 `.env.example` 예시값과 같음 | `grep -c "POSTGRES_.*:-" docker-compose.yml` | 4 (USER/PASSWORD/DB/PORT 각 1) | 대기 (verifier 확인 20:08 → `docker-compose.yml` 없음 — U1 전이므로 정상) |
| 7 | (구현 U2·U3) `scripts/db_check.py` 에 `DATABASE_URL`↔`POSTGRES_*` 불일치 경고(이름만) 구현, README 로컬 DB 절에 "두 값을 같게 유지" 안내 | `python scripts/db_check.py` 출력과 `grep -n "DATABASE_URL" README.md` | 불일치 시 변수 이름만 담긴 `WARN` 줄(비밀번호 값 없음), README 로컬 DB 절에 안내 문장 | 대기 (verifier 확인 20:08 → `scripts/db_check.*` 없음, README 에 `docker compose up -d` 없음 — U2·U3 전이므로 정상. 참고: `POSTGRES_*` 가 환경에 없을 때는 compose 기본값과 비교해야 거짓 경고가 없다, 02-plan-verify §3) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P0-compose` (계획 단계. 구현 뒤에는 `verify-impl.sh P0-compose`)
- 결과 파일(evidence/): `evidence/20260903-verify-plan-2-final.txt` (2026-09-03 20:11, FAIL=0 WARN=1 — "보류 0건" PASS. 남은 WARN 은 F-0ffff5 의 README 행) + 단계 판정 명령 출력 `evidence/20260903-remediation-check-2.txt`. 재검증 1회차. 구현 뒤 `verify-impl.sh` 출력은 04-review 에서 적는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — security.md §1(`.env.example`에 이름만)·§4는 그대로 지킨다. D4/D5/S3.1 은 컬럼·차원 이야기라 접속 변수와 무관.
- FIX/CR 로 올려야 하는가: 아니오 (결정·명세 변경 없음. 계획 문서 수정으로 닫힌다)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 해소(계획 단계) — 구현 단계는 04-review 에서 판정 | 발견: 2026-09-03 (verify-plan) | 해소: 계획 단계 2026-09-03 20:11 (verifier 재검증, 1~3 완료 / 4~5 대기. WARN 자체는 U3 뒤에도 남는 것이 정상)

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: (verifier 작성) 중복 구현이 아니라 소유 표기 문제다. 계획 검증 도중(2026-09-03 19:57) 메인 세션이 `README.md`(미커밋, 9076 바이트)를 새로 만들고 `docs/wiki/registry.md` 32행에 "| 문서 | 프로젝트 README(…) | README.md | 하네스 | pending |" 로 등록했다. 01-plan 산출물의 "README.md '로컬 DB' 절"은 그 파일에 절 하나를 보태는 것이며 README.md 121행이 이미 "로컬 DB(docker-compose + pgvector)와 백엔드 서버 실행 방법은 해당 패키지가 완료되면 이 절에 추가한다"로 자리를 예약해 두었다.
- 확인 방법(명령): `grep -n "README" docs/wiki/registry.md` / `grep -n -i "docker\|compose\|로컬 DB" README.md` / `git status --short README.md docs/wiki/registry.md`
- 확인 결과: registry 32행 소유 `하네스`, 상태 `pending`. README.md 69행 "| P0 | 로컬 docker-compose (pgvector) | 계획 검증 중 |", 121행 위 인용문. `git status` → `?? README.md`, ` M docs/wiki/registry.md`(둘 다 미커밋). 조치 선택지(architect·메인 세션): U3 에서 registry 의 README 행을 새로 만들지 말고 기존 32행의 비고에 "P0-compose: 로컬 DB 절" 을 덧붙이거나, 01-plan 산출물 30행 "docs/wiki/registry.md — compose·initdb·db_check 행 추가" 옆에 "README 는 기존 행 갱신" 을 명시. 파일 소유는 그대로 하네스.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
결정: `README.md` 소유는 `하네스` 그대로 두고 registry 에 **새 README 행을 만들지 않는다**. P0-compose 는 기존 32행 비고에 "P0-compose: 로컬 DB 절"을 덧붙인다. WARN 자체는 registry 에 README 행이 하나뿐인 한 verify-plan 이 계속 출력할 수 있으므로(다른 패키지 소유 파일에 절을 더하는 정상 상황), 이 소견은 "중복 신설 금지"를 계획에 못 박는 것으로 닫는다.

| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan.md 범위 절의 "README … 또는 … registry 행 추가"를 "README 로컬 DB 절 + registry 기존 README 행 비고 갱신(새 행 금지)"으로 교체 | `grep -n "새 행 금지" docs/wiki/packages/P0-compose/01-plan.md` | 범위·산출물·U3 를 포함해 3건 이상 매치 | 완료 (verifier 실행 20:08 → 17·32·37·65행 4건. `evidence/20260903-remediation-check-2.txt`) |
| 2 | 01-plan.md 산출물 절 registry 행을 "compose·initdb·db_check 행 추가, README 는 기존 32행 비고 갱신"으로 수정 | `grep -n "기존 32행\|기존 README 행" docs/wiki/packages/P0-compose/01-plan.md` | 2건 이상 매치 | 완료 (verifier 실행 20:08 → 17·32·37·47·65행 5건. 같은 evidence) |
| 3 | 01-plan.md U3 를 같은 문구로 수정하고 README 절 위치(“로컬에서 해 보기” 121행 예약 자리)를 명시 | `grep -n "U3 .*비고 갱신" docs/wiki/packages/P0-compose/01-plan.md` | U3 줄 1건 매치 | 완료 (verifier 실행 20:08 → 37행 1건, exit 0. 같은 evidence) |
| 4 | (구현 U3) `docs/wiki/registry.md` 32행 비고에 "P0-compose: 로컬 DB 절" 추가 — 새 README 행을 만들지 않는다 | `grep -c "| README.md |" docs/wiki/registry.md` | `1` (여전히 한 행) | 대기 (verifier 확인 20:08 → 현재 1. U3 뒤에도 1 이어야 한다) |
| 5 | (구현 U3) `README.md` 121행 예약 문장을 실제 로컬 DB 절로 교체 | `grep -n "docker compose up -d" README.md` | "로컬에서 해 보기" 절 안에서 1건 이상 | 대기 (verifier 확인 20:08 → 0건, exit 1 — U3 전이므로 정상. README 121행 예약 문장 그대로) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P0-compose` (계획 단계. 구현 뒤에는 `verify-impl.sh P0-compose`)
- 결과 파일(evidence/): `evidence/20260903-verify-plan-2-final.txt` (2026-09-03 20:11, FAIL=0 WARN=1 — 이 소견의 WARN 이 그 1건. 02-plan-verify §3 에 보류 사유가 아닌 이유를 적었다) + `evidence/20260903-remediation-check-2.txt`. 재검증 1회차.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — 파일 소유(하네스)와 registry "무엇이 있는가" 원칙 그대로. 중복 구현 아님(README 121행이 자리를 예약).
- FIX/CR 로 올려야 하는가: 아니오 (문서 소유·표기 문제)

