# D17 · 배포는 Vercel(프론트 정적 + FastAPI Python 함수) + Neon(PostgreSQL/pgvector), 기간 한정 공개

상태: 유효 (D7 을 대체한다) | 해결하는 검증: R14(재결정) | 출처: CR-005 (제기 2026-11-13, 승인 2026-11-14, 사용자)

**결정**
1. **플랫폼**: Vercel Hobby 프로젝트 1개. `web/` Vite 빌드는 정적 호스팅, FastAPI(`app.main:create_app`)는 **Python 서버리스 함수 1개**(Fluid compute, 최대 300초). `vercel.json` `rewrites` 로 `/api/*` → 함수(FastAPI 쪽은 `/api` 접두 제거 — 프론트 `API_BASE='/api'`·Vite 프록시 `stripApiPrefix` 와 같은 규약). Terraform·Dockerfile·Caddy·CloudFront·EC2·SSM 은 쓰지 않는다. 비밀은 Vercel 환경변수.
2. **DB**: **Neon Free**(PostgreSQL + pgvector, Vercel Marketplace 연동으로 `DATABASE_URL` 주입, `sslmode=require`). 스키마 v2·Alembic 그대로. `alembic upgrade head` 는 사용자 로컬 또는 GitHub Actions 수동 워크플로에서 Neon 을 향해 실행(실행 주체 = 사용자, R-U10D-4 대응). 5분 유휴 자동 중지·접속 시 자동 재개는 수용.
3. **주기 작업**: `BRIEFING_SCHEDULER_ENABLED` 는 배포에서 **끈다**(서버리스에 상주 루프 없음). 대신 **GitHub Actions `schedule`(5분, 공개 저장소 무료)** 이 비밀 헤더 `X-Briefing-Token`(이름은 P9 01-plan 결정)으로 `POST /api/briefings/run` 을 부른다. 그 엔드포인트는 헤더가 없거나 다르면 404/401(P9 결정). Vercel cron(Hobby 하루 1회)은 쓰지 않는다 — 브리핑 "만남 직전(≤24h)" 의미 유지, 지연 ≤ 5분(+Actions 지연).
4. **공개 보호**: 접근 코드·로그인 **없음**. **공개 기간 2026-11-14 ~ 2026-11-18(수, 졸업평가)**. 종료 절차(P9 수용 기준): Vercel 배포 삭제 또는 프로젝트 비공개 · GitHub Actions 스케줄 비활성 · Neon 프로젝트 삭제 · 비밀 값(OpenAI 키·VAPID·브리핑 토큰) 회전. 공개 중 LLM 비용은 OpenAI 월 지출 한도(사용자 몫)로 막는다. 사용자 격리(구글 로그인, F-fbaaae)는 여전히 미결 — 단일 사용자 `APP_USER_ID` 데모.
5. **웹푸시**: `pywebpush` 발송은 함수 안에서 그대로(상태 없음). VAPID 키는 Vercel 환경변수. 구독 저장은 Neon.

**이유**
- 사용자 지시(CR-005): Vercel, 무료 티어, 졸업평가(11-18)까지만 공개. AWS 구성(D7)은 비용·준비 시간이 발표 일정에 맞지 않고 IaC 작성 분량이 크다.
- Neon 은 Supabase 와 달리 7일 무요청 일시중지가 없어(자동 재개) 드물게 열리는 데모가 죽어 있지 않다.
- Vercel Hobby cron 은 하루 1회라 S3.6 의 "≤24h 전 브리핑" 을 분 단위로 지키지 못한다. GitHub Actions 스케줄은 공개 저장소에서 무료고 기존 수동 트리거 엔드포인트를 그대로 쓴다(코드 변경 = 보호 헤더 1개).

**파급**
- S3.6 운용 절 보충(주기 작업의 실행 주체가 컨테이너 루프 → 외부 스케줄 호출). S3.1~S3.5·S3.7 무변경.
- P9-infra 01-plan 재작성(infra-agent 신설 불필요 — backend-agent: `vercel.json`·함수 진입점·`/briefings/run` 헤더·`BRIEFING_SCHEDULER_ENABLED` 기본 off 확인 · frontend-agent: 빌드 출력·`/api` 규약 확인 · 사용자: Vercel/Neon 콘솔·환경변수·`alembic upgrade head`·OpenAI 한도·종료). 스모크 S1~S15(review-u10-deploy-validity) 중 Dockerfile·RDS·CloudFront 항목은 Vercel·Neon 대응 항목으로 치환.
- CLAUDE.md 기술 스택 2줄, backlog P9, review-index R14, INDEX P9 행, user-setup 09(AWS 가이드)·02(AWS Budgets) 상단 "대체됨", security §5 "RDS 프라이빗 서브넷" → "Neon TLS 접속".
- 원칙 5·7 무관. 보안 카드 §1(비밀은 Vercel 환경변수에만)·§5 유지.

**코드에서 지켜야 할 것**
1. `vercel.json` 의 `rewrites` 는 `/api/(.*)` 한 줄로 FastAPI 함수를 가리키고, FastAPI 라우트에는 `/api` 접두가 없다(기존 `app/api/routes.py` 경로 그대로).
2. `POST /briefings/run` 은 비밀 헤더 검사 없이 실행되지 않는다(테스트: 헤더 없음 → 실행 0·응답 404 또는 401, 맞는 헤더 → 기존 동작). 토큰 값은 코드·문서에 없다(`.env.example` 에 이름만).
3. 배포 설정에서 `BRIEFING_SCHEDULER_ENABLED` 는 비어 있거나 `0`(lifespan 루프 없음).
4. `.github/workflows/` 의 스케줄 워크플로는 `secrets.*` 로만 토큰·URL 을 읽고, 저장소 파일에 값이 없다.
5. 종료 절차 체크리스트가 `docs/user-setup/` 에 있고 P9 04-review 가 그 존재를 증거로 든다.

**갱신 이력**
- 2026-11-14 신설(CR-005). 구현은 P9-infra 재계획 — 완료 해시는 그때 적는다.
