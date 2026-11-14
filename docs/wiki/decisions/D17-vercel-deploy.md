# D17 · 배포는 AWS 최소 구성 — EC2 1대에 Docker Compose(Caddy·FastAPI·Postgres/pgvector), 프론트 정적도 Caddy, 기간 한정 공개

상태: 유효 (D7 을 대체한다) | 해결하는 검증: R14(재결정) | 출처: CR-005 (제기 2026-11-13, 승인 2026-11-14, **개정 ② 2026-11-14 오후** — 1차 "Vercel + Neon" 에서 AWS 최소로 바뀜, 사용자)

**결정**
1. **구성**: EC2 **1대**(퍼블릭 서브넷, Elastic IP)에 Docker Compose 서비스 3개 — `caddy`(80/443, 자동 HTTPS, `/api/*` 는 `handle_path` 로 접두를 떼고 `backend` 로 프록시, 그 밖은 프론트 정적 빌드 `file_server`) · `backend`(FastAPI uvicorn, entrypoint 가 `alembic upgrade head` 뒤 기동) · `postgres`(`pgvector/pgvector:pg16`, 볼륨 `pgdata`, 호스트 포트 미노출). **S3·CloudFront·RDS·ALB·NAT·Terraform·SSM·ECR 없음.** 기존 `docker-compose.yml`(로컬 DB 전용)은 그대로 두고 `docker-compose.prod.yml`·`Dockerfile`·`Caddyfile` 을 새로 만든다.
2. **HTTPS**: Caddy 가 Let's Encrypt 로 발급. 호스트명은 보유 도메인이 있으면 그것, 없으면 `sslip.io` 류 IP 기반 무료 호스트명(P9 01-plan 결정). PWA·웹푸시는 HTTPS 필수라 생략 불가.
3. **주기 작업**: 서버 안 1분 루프 그대로(`BRIEFING_SCHEDULER_ENABLED=1`, S3.6 원문). 외부 스케줄·비밀 헤더·`/api` 접두 래퍼는 **만들지 않는다**(제품 코드 변경 0).
4. **비밀**: `.env` 는 사용자가 EC2 에 직접 올린다(security §1). 저장소·이미지에 값 없음.
5. **배포·갱신**: 사용자가 SSH 로 `git pull` → `docker compose -f docker-compose.prod.yml up -d --build`. 이미지 태그 = 커밋 해시(SERVER-CHECKLIST 0-4). GitHub Actions 배포 워크플로는 만들지 않는다(기간이 5일).
6. **공개 기간**: 2026-11-14 ~ **2026-11-19(목)** (졸업평가 11-18 다음 날 종료). 종료 절차(P9 수용 기준): 인스턴스 종료 + EBS 볼륨·EIP 해제 확인 · 보안 그룹 삭제 · 비밀 값 회전(OpenAI·VAPID) · AWS Budgets 알림은 유지. 접근 코드·로그인은 없음(발표용). LLM 비용은 OpenAI 월 지출 한도(사용자). **계정은 신규 가입(사용자 2026-11-14), 비상업·개인 학습 용도.** 2025-07 이후 신규 계정은 크레딧 방식 Free Plan($100 + 활동 최대 $100, 6개월) — 적격 인스턴스(t3.micro·t4g.small 등)도 크레딧에서 차감되므로 **Budgets 알림($10/$30/$50, user-setup 02)을 EC2 생성 전에 켠다.** 5일 공개 비용은 크레딧 안(약 $3 안팎 추정, P9 01-plan 에서 재계산).
7. **백업**: 공개 5일·데모 데이터라 자동 백업 파이프라인은 두지 않는다. 종료 직전 `pg_dump` 1회를 사용자가 내려받는 것으로 갈음(09 가이드 §5 의 "A안 백업 필수" 예외 — 기간 한정 데모).
8. **실제 기동 시점**: 사용자가 따로 지시할 때. P9 계획·파일 작성·로컬 compose 스모크까지는 에이전트, EC2 생성·기동·DNS 는 사용자.

**이유**
- 사용자 선택(CR-005 개정 ②): Vercel 안은 제품 코드 4단위(`/api` 래퍼·브리핑 토큰·DSN 수정·Actions 스케줄)를 요구했고 자동 브리핑이 main 승격 뒤에나 돌았다. AWS 최소는 **제품 코드 변경 0** 으로 지금 로컬 구성을 그대로 올리고 1분 스케줄러도 그대로 돈다. 대신 사용자 콘솔·서버 작업이 늘고 계정 무료 자격에 따라 비용이 생길 수 있다 — 비교표를 보고 사용자가 골랐다.
- 원안 D7(CloudFront·RDS·Terraform·SSM)은 몇 명 규모·5일 공개에 과하다(09 가이드 §6 "하지 않는 것" 과 같은 논리를 더 밀었다).

**파급**
- S3.6: 운용 보충 불필요(원문 그대로 — 1분 루프). CLAUDE.md 기술 스택 3줄(프론트 서빙·인프라·Budgets). backlog P9 항목, review-index R14, INDEX P9 행. user-setup 09(AWS 가이드)는 **부분 유효**(§2 결정 1·2·3·4·8, §5 운영 규칙 일부, §7 확장 신호) — CloudFront·Terraform·SSM·Actions 절은 이번에 쓰지 않음. user-setup 02(Budgets) **다시 필수**. security §5: 저장 암호화는 EBS 기본, 전송 TLS 는 Caddy.
- P9-infra 01-plan 재작성(architect) — 단위: `Dockerfile`·`docker-compose.prod.yml`·`Caddyfile`·entrypoint(backend-agent, 로컬 compose 스모크 포함), 프론트 빌드 산출물 경로 확인(frontend-agent, 변경 0 기대), user-setup 11(EC2 절차)·12(종료 체크리스트)(메인), 첫 기동·스모크(사용자 지시 뒤). 스모크 S1~S15 중 RDS·CloudFront 항목은 compose·Caddy 대응으로 치환.
- 원칙 5·7 무관. security §1(비밀은 `.env` 를 사용자가 서버에 직접)·§4(destroy·`down -v` 금지는 종료 절차에서 사용자만) 유지.

**코드에서 지켜야 할 것**
1. 제품 코드(`app/`·`web/src/`·`alembic/`)는 이 결정으로 바뀌지 않는다 — `git diff --stat <기준>..HEAD -- app web/src alembic` 빈 출력.
2. `Caddyfile` 의 `/api/*` 는 `handle_path`(접두 제거)로 `backend:8000` 에 프록시하고, 나머지는 `web/dist` 정적 `file_server`(SPA fallback `try_files … /index.html`).
3. `docker-compose.prod.yml` 의 `postgres` 는 호스트 포트를 노출하지 않고(`ports` 없음), 볼륨 `pgdata` 를 쓴다. `backend` 의 `DATABASE_URL` 은 compose 네트워크 이름(`postgres:5432`)을 가리킨다.
4. `backend` 컨테이너는 기동 시 `alembic upgrade head` 를 먼저 실행하고 실패하면 죽는다(`docker compose ps` 로 보임).
5. 저장소·이미지·compose 파일에 비밀 값이 없다(`.env` 는 `env_file` 로 참조만). `BRIEFING_SCHEDULER_ENABLED=1` 은 운영 `.env` 에서 켠다(기본값 off 유지).
6. 종료 체크리스트가 `docs/user-setup/` 에 있고 P9 04-review 가 그 존재를 증거로 든다.

**갱신 이력**
- 2026-11-14 신설(CR-005 1차: Vercel Python 함수 + Neon Free + GitHub Actions 5분 스케줄, 공개 ~11-18). 같은 날 **개정 ②**: 사용자 선택으로 AWS 최소 구성(EC2 1대 + Compose, 코드 변경 0, 1분 루프 유지, 공개 ~11-19)으로 전면 교체. Vercel 조사 사실은 CR-005 §2-1 에 기록으로 남김. 구현은 P9-infra 재계획 — 완료 해시는 그때 적는다. 파일명 `D17-vercel-deploy.md` 는 링크 유지를 위해 그대로 둔다.
