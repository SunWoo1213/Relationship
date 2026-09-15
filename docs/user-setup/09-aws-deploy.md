# 09 · AWS 배포 가이드라인 — 처음 규모: 사용자 몇 명 (P9 착수 전 기준 문서)

> Refs: P9 D7 D4 D11 S3.1 security §1 §4 · `SERVER-CHECKLIST.md` · `05-server-secrets.md` · `02-aws-budgets.md`
> 이 카드는 **"어떤 모양으로, 얼마에, 어떤 순서로"** 를 정하는 가이드라인이다. Terraform·GitHub Actions 코드는 P9 에서 infra-agent 가 쓰고, `terraform apply`·콘솔 조작·비밀 값 입력은 전부 사용자 몫이다.
> 규모 전제: **동시 사용자 1~5명, 하루 대화 수백 건 이하, 데이터 수 MB.** 이 전제를 넘는 신호는 §7 에 적었다 — 그 전에는 아래 구성을 키우지 않는다.

## 언제 필요한가
- P8(프론트 3화면)까지 끝나고 P9 를 시작할 때 이 문서의 §2 결정을 먼저 확정한다(01-plan 결정 표에 그대로 옮긴다).
- 그 전이라도 §1·§4 의 "지금 해 둘 것"(Budgets, 도메인, 리전 결정)은 미리 해 둔다.

## 왜 사용자 몫인가
AWS 계정·결제·도메인·DNS·GitHub 저장소 설정은 사용자 소유다. 에이전트는 콘솔에 들어가지 않고 비밀 값을 다루지 않는다(`security.md` §1·§4). 에이전트가 만드는 것은 Terraform·워크플로·compose 파일과 이 문서의 명령이며, 실행과 증거 저장은 사용자가 한다.

---

## 1. 목표 구성 (D7 확정 + 소규모 축소)

```
사용자 브라우저(PWA)
   │ HTTPS
   ▼
CloudFront (배포 1개, ACM us-east-1)
   ├─ /            → S3 (React 정적 빌드, OAC 로 비공개 버킷)
   └─ /api/*       → EC2 1대 (퍼블릭 서브넷, Elastic IP)
                      └─ Caddy (Let's Encrypt 자동 HTTPS) → FastAPI(uvicorn, Docker)
                                                              └─ PostgreSQL + pgvector
                                                                 ┌ A안: 같은 EC2 의 docker compose (시작)
                                                                 └ B안: RDS db.t4g.micro 프라이빗 서브넷 (확정 스택)
비밀: SSM Parameter Store (SecureString) → EC2 인스턴스 역할로 읽어 .env 생성
배포: GitHub Actions (OIDC 역할, 장기 키 없음) → SSM Run Command 로 EC2 에서 pull·compose up
비용 알림: AWS Budgets $10 / $30 / $50 (02 카드)
```

- **D7 그대로**: ALB 없음, NAT 없음, EC2 만 퍼블릭, CloudFront 오리진은 HTTPS(Caddy).
- **소규모 축소(이 문서가 추가한 것)**: 인스턴스 1대·단일 AZ·오토스케일링 없음·Multi-AZ 없음·CloudWatch 에이전트 없음. 모니터링은 EC2 상태 검사 알람 1개 + Budgets 만.
- **DB 는 A/B 중 하나를 §2 에서 결정한다.** CLAUDE.md 기술 스택은 "PostgreSQL + pgvector (RDS)" 이므로 A안(compose)을 택하면 **결정 카드(D12 후보) 로 남긴다** — 코드는 `DATABASE_URL` 하나만 보므로(`app/config.py`) A→B 이전 시 앱 수정은 없다.

## 2. P9 착수 전에 확정할 결정 (01-plan 결정 표로 옮긴다)

| # | 결정 | 선택지 | 권장(몇 명 규모) | 근거 |
|---|------|--------|-----------------|------|
| 1 | 리전 | `ap-northeast-2`(서울) / `us-east-1` | **서울** | 사용자가 한국. CloudFront 인증서만 us-east-1(D7) |
| 2 | DB 위치 | **A** compose(EC2 안) / **B** RDS db.t4g.micro | **A 로 시작, B 는 §7 신호 때** | A 는 추가 비용 0, 단 백업을 §5 대로 직접 해야 한다. B 는 월 $15 안팎이 더 든다 |
| 3 | 인스턴스 | t4g.micro(1GB) / **t4g.small(2GB)** / t3.small | **t4g.small** | uvicorn + Postgres + Caddy 를 한 대에 두면 1GB 는 빠듯. ARM 이 x86 보다 싸다 — 이미지가 arm64 를 지원하는지 P9 U1 에서 확인(`pgvector/pgvector:pg16` 은 지원) |
| 4 | 도메인 | 보유 도메인 + Route 53 / 무료 DDNS(DuckDNS 등) | **보유 도메인(연 1~2만 원)** | Caddy 의 Let's Encrypt 는 도메인이 있어야 한다. DDNS 는 인증서 발급 한도를 남과 공유해 실패할 수 있다 |
| 5 | 443 접근 제한 | CloudFront 관리형 prefix list 만 / 전체 개방 | **80 은 전체(인증서 발급·리다이렉트), 443 은 CloudFront prefix list 만** | 오리진 직접 호출 차단. `com.amazonaws.global.cloudfront.origin-facing` |
| 6 | 서버 접속 | SSM Session Manager / SSH 22 | **Session Manager, 22 닫음** | 키 파일 관리 불필요, 보안 그룹에 22 없음 |
| 7 | 배포 트리거 | `main` 푸시 자동 / 수동 `workflow_dispatch` | **수동 dispatch(입력: 커밋 해시)** | L-001·L-003 과 일치 — 승격은 사람이 결정한다. 롤백 = 이전 해시로 다시 dispatch |
| 8 | 이미지 | ECR / EC2 에서 직접 빌드 | **EC2 에서 `git pull` 후 `docker compose build`** | 몇 명 규모에 ECR 은 과하다. 빌드 30초~1분. 태그 = 커밋 해시(SERVER-CHECKLIST 0-4) |
| 9 | 프론트 배포 | Actions 에서 `npm run build` → `aws s3 sync` → CloudFront invalidation | 그대로 | 정적 파일이라 서버와 독립. `/index.html` 만 무효화 |
| 10 | 백업 | A안: 매일 `pg_dump` → S3(수명 30일) / B안: RDS 자동 백업 7일 | A 를 택했으면 **필수** | §5. 백업 없는 A안은 허용하지 않는다 |

## 3. 월 비용 추정 (서울, 온디맨드, 2026-09 기준 **대략** — Pricing Calculator 로 확정)

| 항목 | A안(compose) | B안(RDS) | 메모 |
|------|-------------|---------|------|
| EC2 t4g.small 1대 | ~$15 | ~$15 | 1년 약정(Savings Plan)이면 ~40% 절감. 처음엔 약정 안 한다 |
| EBS gp3 20GB | ~$2 | ~$2 | DB 까지 두면 30GB(~$3) |
| 퍼블릭 IPv4(EIP 1개) | ~$4 | ~$4 | 2024-02 부터 유료 |
| RDS db.t4g.micro + 20GB | — | ~$15~18 | 단일 AZ, 자동 백업 7일 포함 |
| S3 + CloudFront | <$1 | <$1 | 트래픽 수 GB 이하. CloudFront 무료 구간 안 |
| Route 53 호스팅 존 | $0.5 | $0.5 | 도메인 등록비는 연 단위 별도 |
| SSM Parameter Store(Standard) | $0 | $0 | Advanced 는 쓰지 않는다 |
| CloudWatch 알람 1~2개 | $0~0.2 | $0~0.2 | 기본 지표만 |
| **합계** | **~$22/월** | **~$38/월** | LLM·임베딩 API 비용은 별도(P0-cost) |

- 신규 계정 프리 티어(크레딧 방식)가 적용되면 첫 몇 달은 대부분 상쇄된다. `02 카드` 의 Budgets $10 알림이 먼저 울리면 정상이다 — $30 이 울리면 §7 을 본다.
- 가장 큰 변동비는 **LLM 호출**이다. 몇 명 규모에서도 사용자당 일일 발화 상한(예: 200회)을 앱 설정으로 두는 것을 P5 에 넘긴다.

## 4. 순서 (P9 U1~U6 의 골격 — 사용자 단계는 **[사용자]**)

### 4.0 지금 해 둘 것 (P9 전)
1. **[사용자]** Budgets 3개(02 카드). 이것 없이는 아래를 시작하지 않는다.
2. **[사용자]** 도메인 1개 확보, Route 53 호스팅 존 생성, 등록기관 NS 를 Route 53 으로.
3. **[사용자]** AWS 계정에 IAM Identity Center(또는 관리자 IAM 사용자 + MFA). 루트 계정은 쓰지 않는다. 로컬에 `aws configure sso` 로 프로필 1개.
4. **[사용자]** GitHub 저장소 → Settings → Environments 에 `prod` 환경 생성(승인자 = 본인). 배포 워크플로는 이 환경에서만 돈다.

### 4.1 Terraform (infra-agent, `infra/` 디렉터리 — 사용자가 apply)
- 상태 파일: S3 버킷 + DynamoDB 잠금(둘 다 Terraform 밖에서 사용자가 먼저 만든다. 콘솔 5분).
- 모듈 없이 단일 루트, 파일 6개: `network.tf`(VPC, 퍼블릭 서브넷 1, A안이면 프라이빗 서브넷 불필요·B안이면 프라이빗 2), `ec2.tf`(t4g.small, EIP, 인스턴스 역할: SSM 읽기 + Session Manager + S3 백업 쓰기), `sg.tf`(80 전체, 443 CloudFront prefix list, 22 없음), `cdn.tf`(S3 OAC 버킷, CloudFront 오리진 2개, ACM us-east-1, Route 53 레코드), `ssm.tf`(파라미터 **이름**만 선언, 값은 `lifecycle { ignore_changes = [value] }` 로 사용자가 콘솔에서 넣는다), `github-oidc.tf`(OIDC 공급자 + 배포 역할: SSM SendCommand, S3 sync, CloudFront invalidation 만).
- `terraform plan` 출력은 evidence 로 저장(`docs/wiki/packages/P9-infra/evidence/`), `apply` 는 **[사용자]** 가 실행하고 출력 요약만 붙인다(계정 ID·ARN 은 마스킹).

### 4.2 EC2 초기화 (user-data 스크립트, infra-agent 작성)
1. Docker + compose 플러그인 설치, `git clone` (읽기 전용 배포 키 대신 **public 저장소면 https**, private 이면 GitHub 배포 키를 SSM 에 넣고 user-data 가 읽는다).
2. `/opt/app/fetch-env.sh`: `aws ssm get-parameters-by-path --path /relationship/prod --with-decryption` → `.env` 생성(권한 600). **값은 로그에 남기지 않는다**(`set +x`).
3. `docker compose -f docker-compose.prod.yml up -d --build` — 서비스 3개: `caddy`, `backend`, A안이면 `postgres`(볼륨 `pgdata`, 호스트 포트 노출 없음).
4. `backend` 는 기동 시 `alembic upgrade head` 를 먼저 실행하는 entrypoint. 실패하면 컨테이너가 죽고 `docker compose ps` 에서 보인다(SERVER-CHECKLIST 1-1).

### 4.3 Caddy (`Caddyfile`, infra-agent 작성)
```
api.<도메인> {
    reverse_proxy backend:8000
    encode gzip
    header -Server
}
```
- 인증서는 Caddy 가 80/443 으로 자동 발급·갱신. CloudFront 오리진 = `api.<도메인>`, 프로토콜 HTTPS only, 오리진 사용자 정의 헤더 `X-Origin-Secret`(값은 SSM) 을 붙이고 Caddy 에서 그 헤더가 없으면 403 — 443 prefix list 제한과 이중 방어.

### 4.4 GitHub Actions (`.github/workflows/deploy.yml`, infra-agent 작성)
- 트리거 `workflow_dispatch`, 입력 `ref`(커밋 해시, 기본 `main`). 환경 `prod`(승인 필요).
- 단계: OIDC 로 역할 assume → (프론트) `npm ci && npm run build` → `aws s3 sync build/ s3://<버킷> --delete` → invalidation `/index.html` → (백엔드) `aws ssm send-command --document-name AWS-RunShellScript` 로 `cd /opt/app && git fetch && git checkout <ref> && ./fetch-env.sh && docker compose -f docker-compose.prod.yml up -d --build && docker image prune -f` → `curl -sf https://api.<도메인>/health` 로 확인, 실패 시 워크플로 실패.
- 롤백 = 직전 해시로 같은 워크플로 재실행(SERVER-CHECKLIST 0-4 의 메모가 입력값).

### 4.5 첫 배포 뒤 점검 **[사용자]**
`SERVER-CHECKLIST.md` §1~§4 를 순서대로 실행하고 evidence 를 저장한다. §1-4 의 `/health` 는 P5 에서 만든다(아직 없으면 P9 U1 에서 최소 헬스 엔드포인트를 먼저 넣는다 — 본문에 접속 정보 금지).

## 5. 운영 최소 규칙 (몇 명 규모에서도 생략하지 않는 것)

| 항목 | 방법 | 주기 |
|------|------|------|
| DB 백업(A안) | cron: `docker compose exec -T postgres pg_dump -Fc -U $POSTGRES_USER $POSTGRES_DB \| aws s3 cp - s3://<백업버킷>/$(date +%F).dump` · 버킷 수명 규칙 30일 · **복원 리허설 1회**(새 볼륨에 `pg_restore` 후 `scripts/db_check.py`) | 매일 03:00 KST, 리허설은 첫 배포 주 |
| DB 백업(B안) | RDS 자동 백업 7일 + 수동 스냅샷 1개(첫 배포 직후) | 자동 |
| 되돌리기 | 직전 커밋 해시로 워크플로 재실행. 마이그레이션이 있으면 `alembic downgrade -1` 을 먼저(SERVER-CHECKLIST 0-3) | 필요 시 |
| 로그 | `docker compose logs --tail=200` 만. Traceback·키 문자열 0 확인(SERVER-CHECKLIST 1-2). 로그를 외부로 보내지 않는다 | 배포 직후·주 1회 |
| 알람 | CloudWatch: EC2 `StatusCheckFailed` ≥1 → 이메일. Budgets 3개 | 상시 |
| OS 패치 | 월 1회 `dnf upgrade` 후 재부팅(user-data 가 다시 compose up) | 월 1회 |
| 비밀 교체 | SSM 값 갱신 → 워크플로 재실행(fetch-env 가 다시 읽는다). 값은 어디에도 복사하지 않는다 | 노출 의심 시 즉시 |
| 개인정보 | 기획서 9장·`security.md` §5: 대화 원문은 DB 에만, 백업 버킷은 비공개 + SSE-S3, 로그에 발화 원문 금지 | 상시 |

## 6. 하지 않는 것 (범위 통제 — 왜 안 했는가)
- **ALB·오토스케일링·Multi-AZ·NAT·ECS/EKS**: 몇 명 규모에 월 $20~50 을 더 쓰는 항목. 단일 EC2 장애는 재시작(수 분)으로 감수한다.
- **ECR·컨테이너 레지스트리**: EC2 빌드가 1분이면 충분.
- **CloudWatch 에이전트·중앙 로그·APM**: `agent_traces` 테이블(원칙9)이 제품의 관측성이다. 인프라 로그는 compose 로그로 족하다.
- **WAF**: CloudFront prefix list + 오리진 헤더 + Caddy 만. 공개 서비스가 되면(§7) 그때 검토.
- **별도 벡터 DB**: CLAUDE.md 확정 — pgvector 를 같은 DB 에.

## 7. 규모를 키우는 신호 (이 중 하나가 2주 이상 지속되면 B안·상위 인스턴스로)
| 신호 | 측정 | 조치 |
|------|------|------|
| 동시 사용자 10명 이상 또는 일 발화 2,000건 이상 | `agent_traces` 일별 집계 | t4g.medium + RDS(B안) |
| EC2 메모리 85% 이상 지속 | `free -m`, `docker stats` | 인스턴스 승격 또는 DB 분리 |
| DB 5GB 이상 또는 백업 30분 초과 | `pg_database_size`, cron 로그 | RDS(B안) |
| Budgets $30 알림 | 이메일 | 원인 분리(LLM vs 인프라) 후 P0-cost 갱신 |
| 외부 공개(초대 아닌 가입) | 제품 결정 | WAF·Cognito 검토 = 새 결정 카드 |

## 끝났다는 증거
- §2 결정 10개가 P9 `01-plan.md` 결정 표에 옮겨져 사용자 승인됨.
- 4.0 의 4항목 완료 메모(Budgets 이름 3개, 도메인 이름, 프로필 이름, GitHub 환경 이름 — 값·ID 없이).
- 첫 배포 후 `SERVER-CHECKLIST.md` §1~§4 evidence 파일 경로.
- A안이면 복원 리허설 evidence(`db_check.py` 출력) 1개.

## 끝난 뒤 에이전트에게
"09 카드 §2 결정 1~10 은 각각 ○○로 정했어. 도메인은 `<이름>`, 리전 서울" → 에이전트가 P9 01-plan 결정 표 초안과 D12(DB 위치) 카드 초안을 올린다. 값·계정 ID·ARN 은 말하지 않는다.
