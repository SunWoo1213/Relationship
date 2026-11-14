# P9-infra · 계획 검증 (02-plan-verify)

대상: 01-plan.md (2026-11-14 AWS 최소 구성 재작성본, 결정 A~P `확정:` 채워진 상태) | 검증자: verifier (fable) — 계획 작성자(architect, opus)와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-14

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P9-infra verify-plan -- bash .claude/scripts/verify-plan.sh P9-infra` → `docs/wiki/packages/P9-infra/evidence/20261114-1411-verify-plan.txt`
```
# 명령: bash .claude/scripts/verify-plan.sh P9-infra
# 시각: 2026-11-14T14:11:47+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 4a4d8cb (dev2)
# exit: 0
# ---
== verify-plan P9-infra  (2026-11-14 14:11) ==
PASS  존재: docs/wiki/packages/P9-infra/01-plan.md
PASS  존재: docs/wiki/packages/P9-infra/02-plan-verify.md
PASS  카드 존재: D17
PASS  카드 존재: D4
PASS  패키지 id 등록됨: P0-compose
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R14
PASS  Refs 있음: - [ ] U1 **[backend-agent] 배포 파일 5종 + 텍스트 검사 테스트 + 로컬 compos
PASS  Refs 있음: - [ ] U1b **[backend-agent] CI 이미지 빌드 + compose 헬스 스모크 job (
PASS  Refs 있음: - [ ] U2 **[frontend-agent] 빌드 산출물·`/api` 규약·PWA 루트 경로 확인 (기
PASS  Refs 있음: - [ ] U3 **[메인 세션] 사용자 문서 11·12 + registry + security·SERVER
PASS  Refs 있음: - [ ] U4 **[사용자 + 메인 세션] 실제 기동·스모크 S1~S17(치환본)·데모 5단계·03-log
PASS  backlog 일치: 배포 URL(HTTPS)에서 데모 시나리오 5단계 재현 + `git diff --stat -- app web
PASS  의존 완료: P8-frontend
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 2 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) | requirements.txt, requirements-dev.txt 
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
WARN  registry 에 다른 패키지로 이미 있음: alembic.ini → | 마이그레이션 | Alembic 도입 + 초기 스키마 v2 | alembic/ (alembic.ini, alembic/env.py, scrip
PASS  registry 중복 없음: docker/entrypoint.sh
PASS  registry 중복 없음: /app/docker/entrypoint.sh
PASS  registry 중복 없음: docker/entrypoint.sh
PASS  registry 중복 없음: app.main
PASS  registry 중복 없음: docker-compose.prod.yml
PASS  registry 중복 없음: /api/openapi.json
WARN  registry 에 다른 패키지로 이미 있음: /index.html → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
WARN  registry 에 다른 패키지로 이미 있음: /sw.js → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| 서비스 워커 | `web/public/sw.js`(범위 `/` 단일 파일 — `push` → `showNotification(title,{b
| 푸시 구독 | `web/src/push.ts`(`subscribeToPush`·`getPushStatus`·`urlBase64ToUint8A
WARN  registry 에 다른 패키지로 이미 있음: /index.html → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
WARN  registry 에 다른 패키지로 이미 있음: /manifest.webma → | PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
WARN  registry 에 다른 패키지로 이미 있음: .github/workflows/tests.yml → | 설정 | GitHub Actions 테스트 워크플로(pgvector 서비스 컨테이너에서 pytest) | .github/workflows/t
| CI | `.github/workflows/tests.yml` 의 `web` job(matrix ubuntu-latest·windows-la
PASS  registry 중복 없음: tests/test_deploy_files.py
PASS  registry 중복 없음: docs/user-setup/11-ec2-minimal-deploy.md
PASS  registry 중복 없음: docs/user-setup/12-shutdown.md
PASS  registry 중복 없음: docs/wiki/packages/P9-infra/tests.md
PASS  registry 중복 없음: 03-log.md
== 결과: FAIL=0 WARN=8 ==
```

### 1-1. WARN 판정
- `WARN 보류 2 건 — 결과는 통과가 될 수 없다` 는 이 문서 3행의 `보류` 판정(과 근거 열의 "보류" 낱말)을 스크립트가 센 것으로, 4절 결정과 일치한다(오탐 아님 — F-P9V-1 이 닫히면 사라진다).
- registry WARN 7건(`requirements.txt` · `alembic.ini` · `/index.html` ×2 · `/sw.js` · `/manifest.webma` · `.github/workflows/tests.yml`)은 전부 **오탐**이다. 근거: 01-plan "산출물" 절의 "새로 만드는 파일" 목록은 `Dockerfile`·`docker/entrypoint.sh`·`docker-compose.prod.yml`·`Caddyfile`·`.dockerignore`·`tests/test_deploy_files.py`·`docs/user-setup/11-…`·`12-…`·`tests.md`·`03-log.md` 이고(전부 `PASS registry 중복 없음`), WARN 이 걸린 7개는 Dockerfile 이 **복사하는 기존 파일**(`requirements.txt`·`alembic.ini`), Caddy 가 **서빙하는 기존 산출물 경로**(`/index.html`·`/sw.js`·`/manifest.webmanifest` — registry 의 P7·P8 행), **고치는 기존 파일** 표에 이미 올린 `tests.yml`(U1b, "새 파일 아님" 이라고 01-plan 64행이 명시)이다. 중복 구현이 아니다.
- 직전 실행(`evidence/20261114-1401-verify-plan.txt`)의 FAIL 1건은 "없음: 02-plan-verify.md" — 이 문서가 그 파일이다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 제외 칸: "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 음성 입력 / 네이티브 앱". 01-plan "하지 않는 것" 은 배포 형태만 다루고(S3·CloudFront·RDS…, Vercel 4단위, 접근 코드·격리, 자동 백업, 관측성, 새 화면, P2b U3~U5, P10·P11) 제품 기능을 더하지 않는다 — "제품 코드(`app/`·`web/src/`·`alembic/`) 변경 — D17 '코드에서 지켜야 할 것' 1". `CR-005.md` §2 "범위(2장) 변동 없음. 바뀌는 것은 배포 형태만이다." 각 제외 줄 끝에 이유가 있다(원칙7 "왜 안 했는가"). |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙5: 01-plan "새 화면·화면 요소 — 원칙5" 제외, 결정 K (i) "확인 페이지는 제품 화면이 아니고(원칙5) 공개 URL 에 둘 이유가 없다(S9 404)". 원칙7: 위 1행. 원칙8: 판정 표가 `save_evidence.py` 출력·해시·경로로만 판정하고 U4 "실패하면 재시도 남발 대신 `findings.py` 소견(원칙8)"; 비용 표 "단가는 기억에 의존한 대략값 … 확인 필요" 로 미확인 수치를 표시. 원칙9: "관측성은 `agent_traces`(원칙9)와 `docker compose logs`", S13 이 `agent_traces.step='briefing_run'` 으로 스케줄러를 판정. 원칙1~4·6 은 ER·임계치·패턴 코드가 바뀌지 않으므로(제품 코드 diff 0, 판정 표 #2) 영향 없음; U4 "승진 호칭 변이 단계에서 확인 없이 자동 병합되면 원칙1 위반 — 승격하지 않는다" 로 운영 경로에서도 원칙1 을 본다. **직접 확인한 사실**: `app/main.py` 147행 `if request.url.path == "/health":` · `web/src/api/client.ts` 23행 `export const API_BASE = '/api'` · `web/vite.config.ts` 27행 `rewrite: stripApiPrefix` — Caddy `handle_path` 접두 제거 뒤 백엔드 경로 = FastAPI 라우트(`/health`·`/persons`·`/chat`·`/briefings/run`, `app/api/routes.py` 309·381·437행) 로 맞다. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 (재검증 14:16 — 1차 판정은 F-P9V-1 로 유보했음, 아래 근거 끝·§5 참고) | `D17-vercel-deploy.md` "코드에서 지켜야 할 것" 1~6 ↔ 01-plan 판정 표: 1 "`git diff --stat <기준>..HEAD -- app web/src alembic` 빈 출력" → #2(전 단위) · 2 "`handle_path`(접두 제거)로 `backend:8000` … `try_files … /index.html`" → S2·테스트 ⑪ · 3 "`postgres` 는 호스트 포트를 노출하지 않고 … 볼륨 `pgdata` … `DATABASE_URL` 은 `postgres:5432`" → #3·⑨·⑩ · 4 "`alembic upgrade head` 를 먼저 실행하고 실패하면 죽는다" → ⑫·entrypoint `set -eu` · 5 "저장소·이미지·compose 파일에 비밀 값이 없다 … `BRIEFING_SCHEDULER_ENABLED=1` 은 운영 `.env` 에서" → #4·⑥⑦·결정 K · 6 "종료 체크리스트가 `docs/user-setup/` 에" → #6. 여섯 항목 모두 판정 표 행이 있다. **사실 2·3 직접 확인**: `app/config.py` 114행 `if database_url:` · 118행 `password=parsed["password"] or postgres["password"]`(비밀번호 없는 URL 이면 `POSTGRES_PASSWORD` 로 채움 — 맞다); `.claude/hooks/secret-guard.sh` 68행 `'postgres(ql)?://[^:/[:space:]]+:[^@[:space:]]{8,}@'` 를 `${DB_USER}:${DB_PW_VALUE}@…` 형태에 적용하면 일치(True), 비밀번호 없는 형태는 불일치(False) — 이 문서를 쓰는 동안 같은 꼴을 담은 스크래치 파일 Write 가 `[secret-guard] 비밀로 보이는 문자열` 로 실제 거부됐다. 결정 O (i) 의 근거 둘 다 맞다. **사실 6 직접 확인**: `docker-compose.yml` 에 `name:` 없음, 서비스 `postgres`·볼륨 `pgdata` — `name: relationship-prod` 필요성 맞다(F-P9V-3 참고). **충돌 1건(F-P9V-1)**: 01-plan 61행 `Caddyfile` 사양을 **실제 Caddy 로 adapt 한 결과**(`evidence/20261114-1406-plan-verify-caddy-order.txt`) 최상위 `respond @apidocs 404` 는 `handle_path /api/*` **뒤** 에 배치된다 — `/api/docs` 요청은 `reverse_proxy` 가 먼저 받아 백엔드 `/docs`(Swagger) 를 그대로 돌려주고 404 는 닿지 않는다. 결정 M (i)·S10·스모크 ⑧ 이 깨지며, 텍스트 테스트 ⑪("`/api/docs`… 404" 문자열 존재)은 이 오류를 잡지 못한다. D17 2 "`/api/*` 는 `handle_path`" 자체는 맞지만 결정 M 의 구현 사양이 틀렸다 → 아래 §3. **재검증(14:16)**: 고친 01-plan 61행 `handle_path /api/* { @docs path /docs* /redoc* /openapi.json ; respond @docs 404 ; reverse_proxy backend:8000 }` 을 같은 방법으로 adapt 한 결과(`evidence/20261114-1416-plan-verify-caddy-order-fixed.txt`) `/api/*` subroute 안 순서가 `rewrite → [/docs* /redoc* /openapi.json] static_response(404) → reverse_proxy` 로 404 가 프록시보다 앞에 온다. 테스트 ⑪(91행) "`respond … 404` 줄이 `handle_path /api/*` 블록 안에 있고 같은 블록의 `reverse_proxy` 줄보다 앞 … 매처는 접두 없는 `/docs*`·`/redoc*`·`/openapi.json`" · V1-14b(92행) "404 `respond` 를 `handle_path` 블록 밖 최상위로 옮김 → ⑪ (+ 스모크 ⑧ `/api/docs` 200 으로 실패)" 가 추가돼 틀린 배치를 테스트와 스모크 둘 다 잡는다. 충돌 해소. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.6-briefing-push.md` 5~6행: "주기 작업(컨테이너 내, 1분)" · "운용(CR-005 · D17 개정 ②): 배포도 EC2 컨테이너 안 lifespan 루프(1분) 그대로 — `BRIEFING_SCHEDULER_ENABLED=1` 을 운영 `.env` 에서 켠다." ↔ 01-plan 목표 "1분 브리핑 스케줄러는 서버 안에서 원문(S3.6) 그대로 돈다(`BRIEFING_SCHEDULER_ENABLED=1`, 운영 `.env`)", `--workers 1`(R-U10D-9). 스키마·툴 시그니처·임계치·ask_user 는 바뀌지 않는다(`CR-005.md` §2 "스키마 S3.1·툴 S3.2·ER S3.3·ask_user S3.4·메모리 S3.5·평가 S3.7 무변경", 제품 코드 diff 0). `app/settings.py` 358~364행 `BRIEFING_SCHEDULER_ENABLED` 는 `'1' or 'true'` 만 허용(사실 5 맞음). `app/briefing/run.py` 6행 "실행 끝에 `briefing_run` trace 1행" — S13 판정 근거 맞음. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 95행 "의존: P8". `P8-frontend/04-review.md` 296행 "결과: 완료 — [필수] 0 · [권고] 10" (2026-10-21). `P4b-er-redesign/04-review.md` 144행 "결과: 완료"(verify-plan `PASS P4 게이트 통과 (P4b-er-redesign)`). `P8b-persons-grid/04-review.md` 30행 `FAIL=0`·backlog "완료 2026-10-28". P2b 일시 중단은 `CR-005.md` 일정 제약 절 "P2b-person-delete 는 **U2 커밋까지만 마치고** … 11-18 뒤 P2b U3~U5 를 재개한다" 와 01-plan 5행 "P2b-person-delete 는 **U2 `3a1bcec` 뒤** …" 가 같은 해시(`3a1bcec`, gitlog 최근 커밋 3번째)를 가리킨다. gitlog(`gitlog.sh P9-infra P9 CR-005 D17`, HEAD `4a4d8cb`): P9·CR-005·D17 태그 커밋은 `53cbefe`·`4a4d8cb` 문서 2건, 코드 커밋 0 — 01-plan 7행 기준 해시 `4a4d8cb` 와 일치. `CURRENT.md` `active: none`·`frozen: none`. 순서 U1∥U2 → U1b → U3 → **[사용자 지시] U4** 는 D17 8 "실제 기동 시점: 사용자가 따로 지시할 때" 와 backlog "실제 EC2 기동은 사용자가 따로 지시할 때" 와 같다. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | verify-plan `PASS backlog 일치`. `docs/backlog.md` 95행 "수용기준: 배포 URL(HTTPS)에서 데모 시나리오 5단계 재현 + `git diff --stat -- app web/src alembic` 빈 출력(제품 코드 무변경) + `postgres` 호스트 포트 미노출 + 저장소·compose 파일에 비밀 값 0 + 로컬에서 `docker compose -f docker-compose.prod.yml up --build` 스모크(`/api/health` 200, 정적 `/` 200) + 종료 체크리스트 문서 존재 + 아래 유효성 점검 중 compose·Caddy 대응 항목(RDS·CloudFront 항목은 치환)." = 01-plan "수용 기준" 절 문장. 7구절이 판정 표 #1~#7 에 하나씩 대응하고, "아래 유효성 점검" 은 `P8-frontend/review-u10-deploy-validity.md` §9 S1~S15 가 치환 표 S1~S15 행과 번호·원안 문구가 1:1 로 맞는다(S8 `pg_stat_ssl` 기대값을 `f` 가 정상으로 바꾼 근거는 security §5 개정 ② "호스트 포트 미노출(compose 네트워크 안에서만)"). 기준 없는 `git diff` 는 "`<기준>..HEAD` 로 한다 — 활성화 때 적는 기준 해시" 로 보정했다(합리적). #1 데모 5단계만 사람 판정, 나머지 기계. |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan `PASS Refs 있음` ×5(U1·U1b·U2·U3·U4). 01-plan 85행 U1 "Refs: P9-infra D17 R14 R-U10D-1 R-U10D-2 R-U10D-4 R-U10D-5 R-U10D-9 원칙8 security" · 94행 U1b "Refs: P9-infra D17 R-U10D-1 원칙8" · 101행 U2 "Refs: P9-infra D17 R-U10D-2 원칙5" · 107행 U3 "Refs: P9-infra D17 security R-U10D-3 R-U10D-5" · 139행 U4 "Refs: P9-infra D17 R14 R-U10D-1~4 R-U10D-8 R-U10D-9 R-U10D-10 원칙8". 변이 표: U1 V1-1~15 · U1b V1b-1~3 · U2 V2-1~2 가 각각 잡는 테스트 번호를 적었다. 단위 크기: U1 이 파일 5종 + 테스트 15항 + 스모크 14단계로 크다(F-P9V-5, 권고). |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 11행 L-007 예외·12행 "배포는 SSM Parameter Store"(U3 가 D17 4 로 고친다 — 01-plan 75행) · §4 44행 "`docker … prune`, `volume rm`, `compose down -v` 금지 — 컨테이너만 내리기(`down`). 볼륨 삭제는 사용자" ↔ 01-plan 스모크 ⑭ "`down`(**`-v` 없음**)", 12 문서 2항 `down`, 14단계 "`DROP`/`TRUNCATE`·`down -v` 없이" · §4 46행 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T`, `scp`) 금지" ↔ 사실 11 "배포 URL `POST /api/chat`(S6)·`pg_dump` 파일 내려받기(scp)는 사용자 몫" · §3 36행 `curl … | sh` 금지 ↔ 11 문서 6단계 "Docker 공식 apt 저장소 방식(`curl … \| sh` 금지 — security §3)" · §5 67행 개정 ② "호스트 포트 미노출 … 전송 TLS 는 Caddy" ↔ #3·S3·S8. `.env`: 사실 12 "에이전트는 `.env` 를 읽지도 쓰지도 않는다 … 스크래치패드의 비밀 없는 변수 파일", `.dockerignore` 에 `.env`·`.env.*`, `postgres` 서비스에 `env_file` 없음. `docker compose config` 는 "항상 `--quiet` 로만" (보간된 비밀이 증거에 찍히지 않게). 09 가이드 §5 "A안 백업 필수" 예외는 `D17-vercel-deploy.md` 7 "종료 직전 `pg_dump` 1회를 사용자가 내려받는 것으로 갈음(09 가이드 §5 의 'A안 백업 필수' 예외 — 기간 한정 데모)" 에 기록됨; `CR-005.md` 에는 `pg_dump`·백업 단어가 0건(F-P9V-6, 권고 — D17 이 결정 카드이므로 통과에 영향 없음). |

### 2-1. 추가로 직접 확인한 사실 주장 (01-plan "코드에서 확인한 사실")
| 사실 | 확인 | 결과 |
|---|---|---|
| 1 `os.environ` 만 읽음 | `app/config.py` 16행 "값은 `os.environ` 에서만 읽는다", `app/settings.py` 4행 "으로만 읽는다. `.env` 파일 자체는 존재 확인도 하지 않는다" | 맞음 |
| 2 `DATABASE_URL` 비밀번호 대체 경로 | `app/config.py` 114·118행(위 3행) | 맞음. 덧붙임: `POSTGRES_PASSWORD` 가 있고 URL 비밀번호가 비면 `warnings` 에 "[warn] POSTGRES_PASSWORD 가 DATABASE_URL 과 다르다" 가 **들어가지만** `alembic/env.py` 53행 `_conn_info, _warnings = resolve_connection()` 은 그 목록을 쓰지 않는다 — 기동에 영향 없음(F-P9V-7 메모) |
| 3 secret-guard 68행 패턴 | 위 3행 — 변수 보간 형태 일치 확인(Python `re`, 같은 패턴 `save_evidence.py` 58행) + 실제 Write 거부 | 맞음 |
| 4 `/health` 503 분기·`API_BASE`·Vite 프록시 | `app/main.py` 147행 · `client.ts` 23행 · `vite.config.ts` 27행 · `vite.config.ts` 에 `base` 없음(grep 0) | 맞음 |
| 5 lifespan 스케줄러·스위치 | `app/main.py` `_lifespan` · `app/settings.py` 358~364행 · `app/briefing/run.py` 6행 | 맞음 |
| 6 compose 프로젝트 이름 충돌 | `docker-compose.yml` `name:` 없음 · `docker compose ls`: 현재 개발 DB 프로젝트 이름은 **`capstone2`**(`capstone2_pgdata`), 그리고 **`relationship_pgdata`** 볼륨도 이미 존재 | 결론(`name: relationship-prod` 필수)은 맞음. 단 "기본 프로젝트 이름(디렉터리명)" 은 현재 개발 환경에서 `.env` 의 `COMPOSE_PROJECT_NAME` 으로 `capstone2` 가 된 것으로 보인다 — `--env-file <스크래치>` 로 띄우는 운영 compose 는 그 값을 받지 않아 이름 없이면 `relationship` 이 되고 **기존 `relationship_pgdata`(옛 데이터)** 와 충돌한다(F-P9V-3) |
| 7 initdb·슈퍼유저 | `docker/initdb/01-vector.sql` 존재 | 맞음 |
| 8 arm64 바이너리·engines·build | `web/package-lock.json` 3059·3423·5841행(`lightningcss-linux-arm64-gnu` 는 5841행 의존 선언, 5949행은 미확인) · `web/package.json` 6~9행 `"node": ">=24"`, `"npm": ">=11"` · 12행 `"build": "tsc -b && vite build"` · `tests.yml` 170행 `node-version: 24` | 맞음 |
| 9 `app/` 이 `evaluation|scripts|data|reports` 를 import 하지 않음 | 접두 grep(`'^\s*(from\|import) (evaluation\|scripts\|data\|reports)'`) 25행은 전부 `from dataclasses import dataclass`(21)·`replace`(4) 가 `data` 접두에 걸린 것. 단어 경계 grep `'^\s*(from\|import) (evaluation\|scripts\|reports\|data)(\.\|\s)' app` → **0행** | 맞음 |
| 10 Python 3.13 | `.python-version` 없음 · `pyproject.toml` 7행 `target-version = "py313"`·24행 `python_version = "3.13"` · `tests.yml` 35행 `["3.13", "3.14"]`, 7행 `branches: [main, dev, dev2]` | 맞음. `requirements.txt` 핀(`psycopg[binary]==3.3.5`·`fastapi==0.135.1`·`uvicorn[standard]==0.41.0` 등)이 CI 3.13 에서 돌고 있으므로 `python:3.13-slim` 전제와 맞다 |
| 11·12 security §4·§1 | 위 8행 | 맞음 |
| 13 `POST /briefings/run` 무보호 | `app/api/routes.py` 381행 `@router.post("/briefings/run", …)` 의존성에 인증 없음, `client.ts` 138행 | 맞음 |
| S5 `/api/questions/pending` 헤더 없음 → `[]` | `routes.py` 471~483행 docstring "헤더가 없으면 … 결과는 항상 빈 목록이다" | 맞음 |
| 비용 표 | t4g.small $0.0208×120h=$2.50 · EBS $0.0912/GB-월×20GB×120/730h≈$0.30 · EIP $0.005×120=$0.60 → $3.40; 단가 "기억에 의존한 대략값 … 확인 필요" 표시 있음 | 계산 일관, 미확인 표시 있음 |
| 결정 B 확정 | "(iii) 새로 구입하는 도메인 … **보조**: … `<EIP>.sslip.io` 로 먼저 띄우고" — 위임 요청문의 사용자 결정과 같다 | 맞음 |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

**[필수]**
- **F-P9V-1 — `Caddyfile` 사양의 결정 M (i) 구현이 동작하지 않는다(01-plan 61행 · 테스트 ⑪ · V1-14).** 증거 `evidence/20261114-1406-plan-verify-caddy-order.txt`: 01-plan 61행 그대로 적은 Caddyfile 을 `caddy:2-alpine` 의 `caddy adapt` 로 변환하면 라우트 순서가 `header ×3 → header/encode → [/api/*] subroute(rewrite, reverse_proxy) → [handle] subroute(vars, try_files, file_server) → [/api/docs* /api/redoc* /api/openapi.json] static_response` 다. `respond` 는 Caddy 지시문 순서에서 `handle_path` 뒤이므로 `/api/docs` 는 `reverse_proxy` 가 먼저 처리해 백엔드 `/docs`(Swagger UI, 200)를 돌려준다 — S10·스모크 ⑧ 이 실패하고, 텍스트 테스트 ⑪ 은 "404 문자열 존재" 만 봐서 잡지 못한다. 위임 프롬프트는 01-plan 원문을 인용해야 하므로(메모리 "위임 프롬프트는 01-plan 원문을 인용") 이 줄을 고치지 않으면 backend-agent 가 틀린 사양을 그대로 구현하고 스모크에서 왕복이 생긴다. **고칠 것(architect 또는 메인, 01-plan 3곳)**: ① 61행 — 404 를 `handle_path /api/*` **블록 안**으로 옮기고 접두가 떼인 경로로 매칭: `handle_path /api/* { @docs path /docs* /redoc* /openapi.json ; respond @docs 404 ; reverse_proxy backend:8000 }` (대안: `handle @apidocs { respond 404 }` 블록을 `handle_path` 와 나란히 — `handle` 계열은 경로 길이로 정렬돼 긴 `/api/docs*` 가 먼저 매칭) ② 테스트 ⑪ 을 "`respond … 404` 가 `handle_path /api/*` 블록 안(또는 `handle` 블록 안)에 있고 `reverse_proxy` 줄보다 앞" 으로 보강 ③ V1-14 에 "404 를 최상위 `respond` 로 옮김 → ⑪ + 스모크 ⑧" 변이를 추가. 고친 뒤 `verify-plan.sh` 재실행 + 이 문서 3행 재판정(verifier).

**[권고]** (통과를 막지 않음 — 위임 전 반영 권고)
- **F-P9V-2 — 판정 표 명령 대부분이 `save_evidence.py` 를 그대로 통과하지 못한다.** `save_evidence.py` 19행 "`--` 뒤 인자를 공백으로 이어 `bash -c` 로 실행" — 셸이 따옴표를 벗긴 뒤 다시 합치므로 `ps --format '{{.Service}} {{.Ports}}'`(두 토큰으로 갈라짐) · `python -c "import urllib.request; print(...)"` · `psql -tAc "SELECT count(*) FROM agent_traces WHERE step='briefing_run'"` · `curl -w '%{http_code} %{content_type}'` · `docker run … sh -c 'ls -a /app'` · **`git grep -nIE '(PASSWORD|SECRET|API_KEY|PRIVATE_KEY)[[:space:]]*[:=]…'`**(따옴표가 벗겨지면 `bash -c` 가 `(`·`|`·`$` 를 서브셸·파이프로 해석 — 문법 오류 또는 `PASSWORD` 를 명령으로 실행 시도) 가 깨진다. 01-plan 147행이 원리("따옴표가 사라지므로 토큰 하나로 쓴다")를 적어 놓고도 표는 그 규칙을 지키지 않았다. 우회(계획에 한 줄로 명시): 안쪽 따옴표를 바깥 따옴표로 한 번 더 감싸 `bash -c` 가 다시 해석하게 하거나(`"'{{.Service}} {{.Ports}}'"`), 스크래치패드에 `<SCR>/u1-<이름>.sh` 를 Write 로 만들고 `save_evidence.py P9-infra <이름> -- bash <SCR>/u1-<이름>.sh` 로 돈다(머리줄 `# 명령:` 에 스크립트 경로만 남으므로 스크립트 본문을 03-log 에 인용). `python3 -m alembic heads` 도 저장소 `.venv` 인터프리터(`.venv/bin/python -m alembic heads` → `0002 (head)`)로 적어야 한다 — 시스템 `python3` 에는 alembic 이 없다.
- **F-P9V-3 — 사실 6 의 기본 프로젝트 이름 서술 보정.** 현재 개발 DB 는 `docker compose ls` 상 프로젝트 `capstone2`(`capstone2_pgdata`)이고 별도로 `relationship_pgdata` 볼륨이 남아 있다. `--env-file <스크래치>` 로 띄우는 운영 compose 는 `.env` 의 `COMPOSE_PROJECT_NAME` 을 받지 않으므로 `name:` 이 없으면 `relationship` 프로젝트가 되어 **옛 `relationship_pgdata`** 를 집어 쓴다(개발 DB `capstone2` 와는 다른 충돌). 결론(`name: relationship-prod` 필수)은 그대로 맞지만, "개발 DB 무영향" 회귀 행에 `docker compose ls` 와 `docker volume ls --format '{{.Name}}'` 전·후 비교를 추가하고, 스모크 ⑭ 뒤 남는 볼륨 이름이 `relationship-prod_pgdata` 임을 그 출력으로 판정하면 된다.
- **F-P9V-4 — U2 의 `web/public/` 수정 허용 범위.** 01-plan 104행 "`web/public/`·`web/vite.config.ts` 처럼 `web/src/` 밖이면 최소 수정 + Vitest 1건까지 허용" — `web/public/sw.js`·`manifest.webmanifest` 는 수용 기준 `git diff -- app web/src alembic` 바깥이지만 사용자가 받는 제품 산출물(서비스 워커·PWA 매니페스트, registry P7·P8 행)이다. 수정이 생기면 03-log 와 04-review 에 "제품 산출물 변경(diff 검사 바깥)" 으로 따로 표시하고 그 이유를 적도록 한 줄 추가를 권한다. 기대 변경 0 이므로 지금은 영향 없다.
- **F-P9V-5 — U1 크기.** 배포 파일 5종 + `.env.example` + 텍스트 테스트 15항 + 로컬 스모크 14단계 + 변이 15종이 커밋 하나다. 리뷰 가능하지만 크다 — 필요하면 "파일 5종 + 테스트"(U1) 와 "로컬 스모크 증거"(U1 두 번째 커밋, 03-log 만) 로 나눠도 수용 기준·Refs 는 그대로다. 강제하지 않는다.
- **F-P9V-6 — 백업 예외 기록 위치.** 09 가이드 §5 "A안 백업 필수" 의 예외(종료 직전 `pg_dump` 1회)는 `D17` 7 에만 있고 `CR-005.md` 개정 ② 본문에는 `pg_dump`·백업 단어가 없다(grep 0). 결정 카드(D17)에 있으므로 충분하지만, CR-005 개정 ② "유지되는 것" 줄에 "백업 = 종료 직전 `pg_dump` 1회(D17 7)" 한 구절을 더하면 추적이 닫힌다(U3 또는 메인, 문서 1줄).
- **F-P9V-7 — 기동 로그 기대값 메모.** 결정 O (i) 구성(`POSTGRES_PASSWORD` 있음 + URL 비밀번호 없음)에서 `resolve_connection` 은 `[warn] POSTGRES_PASSWORD 가 DATABASE_URL 과 다르다` 를 `warnings` 에 넣는다(`app/config.py` 130~133행). 지금 호출자(`alembic/env.py` 53행)는 그 목록을 출력하지 않아 로그에 나오지 않지만, U1 스모크 ⑬ "Traceback 0" 판정에 이 줄이 보여도 오류가 아님을 03-log 에 한 줄 적어 두면 U4 에서 혼동이 없다. 제품 코드 수정 대상이 아니다.

## 4. 결정
1차(14:11): 보류 — [필수] 1(F-P9V-1) · [권고] 6(F-P9V-2~7). 기록으로 유지.

결과: 통과 — 재검증 2026-11-14 14:16. [필수] F-P9V-1 닫힘(§5), [권고] F-P9V-2·3·4·6 반영 확인, F-P9V-5(U1 분할)는 선택 사항으로 미반영, F-P9V-7 은 U1 03-log 메모로 이관(메인 보고). 열린 [필수] 0.
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)

## 5. 재검증 (2026-11-14 14:16 — 메인이 01-plan·CR-005 를 고친 뒤)

### 5-1. 소견별 확인 (01-plan 재읽기, `grep -n "F-P9V-1\|F-P9V-2\|F-P9V-3\|F-P9V-4"` → 18·61·91·92·104·147·179행)
| 소견 | 고친 곳 (인용) | 판정 |
|---|---|---|
| F-P9V-1 [필수] | 01-plan 61행 "`handle_path /api/* { @docs path /docs* /redoc* /openapi.json ; respond @docs 404 ; reverse_proxy backend:8000 }`(결정 M (i) — **404 는 `handle_path` 블록 안**에서 접두가 떼인 경로로 매칭하고 `reverse_proxy` 보다 **앞**에 둔다 …)" · 91행 ⑪ "`respond @docs 404` … 줄이 **`handle_path /api/*` 블록 안**에 있고 같은 블록의 `reverse_proxy` 줄보다 **앞**에 있으며, 매처는 접두 없는 `/docs*`·`/redoc*`·`/openapi.json`" · 92행 "V1-14b 404 `respond` 를 `handle_path` 블록 밖 최상위로 옮김(또는 `reverse_proxy` 뒤로) → ⑪ (+ 스모크 ⑧ `/api/docs` 200 으로 실패 — F-P9V-1 재현)". **직접 재실행**: 고친 사양을 `caddy:2-alpine` `caddy adapt` → `evidence/20261114-1416-plan-verify-caddy-order-fixed.txt` — `/api/*` subroute 안 `rewrite → static_response 404(/docs*,/redoc*,/openapi.json) → reverse_proxy`. | **닫힘** |
| F-P9V-2 [권고] | 147행 "**따옴표·`$`·`|`·`(` 가 든 안쪽 명령(F-P9V-2)** — … 우회 두 가지 중 하나: ① 바깥 따옴표로 한 번 더 감싸기(`"'{{.Service}} {{.Ports}}'"`) ② 안쪽 명령을 스크래치패드 `<SCR>/u1-<이름>.sh` 로 Write 해 두고 `-- bash <SCR>/u1-<이름>.sh`. `alembic heads` 는 `.venv/bin/python -m alembic heads`" | 반영 |
| F-P9V-3 [권고] | 18행 "(보정 F-P9V-3: 현재 개발 DB 컨테이너의 실제 프로젝트는 `capstone2`(볼륨 `capstone2_pgdata`)이고 `relationship_pgdata` 는 따로 남아 있는 옛 볼륨 — 운영 compose 는 `--env-file <스크래치>` 로 띄워 `.env` 의 `COMPOSE_PROJECT_NAME` 을 받지 않으므로 `name:` 이 유일한 방어)" · 179행 "`… u1-compose-ls -- docker compose ls` + `… u1-volume-ls -- docker volume ls` 전·후(F-P9V-3) … 새 볼륨은 `relationship-prod_*` 만" | 반영 |
| F-P9V-4 [권고] | 104행 "단 `web/public/`(sw.js·manifest)은 제품 산출물이므로 수정이 생기면 03-log U2 항목과 04-review 에 '제품 산출물 변경' 으로 따로 표시한다(F-P9V-4)" | 반영 |
| F-P9V-5 [권고] | 미반영(선택 사항) | 열림 — 통과 무관 |
| F-P9V-6 [권고] | `CR-005.md` 46행 "**백업**: 09 가이드 §5 'A안 백업 필수' 는 5일 데모 예외로 **종료 직전 `pg_dump` 1회(사용자 다운로드)** 로 갈음(D17 7, F-P9V-6)" | 반영 |
| F-P9V-7 [권고] | U1 03-log 메모로 이관(메인) | 열림 — 통과 무관 |

### 5-2. 기계 검증 재실행 출력 (그대로)
명령: `python3 .claude/scripts/save_evidence.py P9-infra verify-plan -- bash .claude/scripts/verify-plan.sh P9-infra` → `evidence/20261114-1418-verify-plan.txt` (중간 실행 `…-1415-`(메인)·`…-1417-`(이 문서가 아직 "보류" 낱말을 품은 상태) 도 남아 있음)
```
# 명령: bash .claude/scripts/verify-plan.sh P9-infra
# 시각: 2026-11-14T14:18:21+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 4a4d8cb (dev2)
# exit: 0
# ---
== verify-plan P9-infra  (2026-11-14 14:18) ==
PASS  존재: docs/wiki/packages/P9-infra/01-plan.md
PASS  존재: docs/wiki/packages/P9-infra/02-plan-verify.md
PASS  카드 존재: D17
PASS  카드 존재: D4
PASS  패키지 id 등록됨: P0-compose
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R14
PASS  Refs 있음: - [ ] U1 **[backend-agent] 배포 파일 5종 + 텍스트 검사 테스트 + 로컬 compos
PASS  Refs 있음: - [ ] U1b **[backend-agent] CI 이미지 빌드 + compose 헬스 스모크 job (
PASS  Refs 있음: - [ ] U2 **[frontend-agent] 빌드 산출물·`/api` 규약·PWA 루트 경로 확인 (기
PASS  Refs 있음: - [ ] U3 **[메인 세션] 사용자 문서 11·12 + registry + security·SERVER
PASS  Refs 있음: - [ ] U4 **[사용자 + 메인 세션] 실제 기동·스모크 S1~S17(치환본)·데모 5단계·03-log
PASS  backlog 일치: 배포 URL(HTTPS)에서 데모 시나리오 5단계 재현 + `git diff --stat -- app web
PASS  의존 완료: P8-frontend
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) | requirements.txt, requirements-dev.txt 
| 모듈 | 웹푸시 설정 읽기 | app/settings.py | P2-tools | 85393e0 | **P7-push U1(85393e0)*
WARN  registry 에 다른 패키지로 이미 있음: alembic.ini → | 마이그레이션 | Alembic 도입 + 초기 스키마 v2 | alembic/ (alembic.ini, alembic/env.py, scrip
PASS  registry 중복 없음: docker/entrypoint.sh
PASS  registry 중복 없음: /app/docker/entrypoint.sh
PASS  registry 중복 없음: docker/entrypoint.sh
PASS  registry 중복 없음: app.main
PASS  registry 중복 없음: docker-compose.prod.yml
PASS  registry 중복 없음: /openapi.json
PASS  registry 중복 없음: evidence/20261114-1406-plan-verify-caddy-order.txt
WARN  registry 에 다른 패키지로 이미 있음: /index.html → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
WARN  registry 에 다른 패키지로 이미 있음: /sw.js → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| 서비스 워커 | `web/public/sw.js`(범위 `/` 단일 파일 — `push` → `showNotification(title,{b
| 푸시 구독 | `web/src/push.ts`(`subscribeToPush`·`getPushStatus`·`urlBase64ToUint8A
WARN  registry 에 다른 패키지로 이미 있음: /index.html → | 확인 도구(제품 화면 아님, 스위치 기본 꺼짐) | 웹푸시 구독 확인 페이지 — `/push-dev/`·`/push-dev/sw.js`·`/
| PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
| 테스트 | `sw.test.ts` 14건(가짜 self 로 sw.js 평가 — push 인자·postMessage·잘못된 JSON·click
WARN  registry 에 다른 패키지로 이미 있음: /manifest.webma → | PWA 껍데기 | `web/public/manifest.webmanifest`(이름 `관계 메모리`·`start_url` `/#/chat`·
PASS  registry 중복 없음: tests/test_deploy_files.py
WARN  registry 에 다른 패키지로 이미 있음: .github/workflows/tests.yml → | 설정 | GitHub Actions 테스트 워크플로(pgvector 서비스 컨테이너에서 pytest) | .github/workflows/t
| CI | `.github/workflows/tests.yml` 의 `web` job(matrix ubuntu-latest·windows-la
PASS  registry 중복 없음: docs/user-setup/11-ec2-minimal-deploy.md
PASS  registry 중복 없음: docs/user-setup/12-shutdown.md
PASS  registry 중복 없음: docs/wiki/packages/P9-infra/tests.md
PASS  registry 중복 없음: 03-log.md
== 결과: FAIL=0 WARN=7 ==
```
WARN 7건은 1-1 절과 같은 registry 이름 겹침 오탐(1차 때의 "보류 2 건" 카운터는 `PASS 보류 0건` 으로 바뀜). **FAIL 0 · 보류 0 → 결과: 통과.**
