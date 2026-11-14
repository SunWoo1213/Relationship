# 13 · 사용자가 할 일 — 배포(P9) 전후 (2026-11-14 작성, 졸업평가 11-18 · 종료 11-19 18:00)

> Refs: P9-infra CR-005 D17 · `11-ec2-minimal-deploy.md`(상세 절차) · `12-shutdown.md`(종료) · `02-aws-budgets.md`
> 사용자 지시(2026-11-14): "내가 해야할 일을 문서로 작성해서 놔둬". 에이전트가 할 수 없는 것(계정·결제·비밀 값·콘솔·도메인)만 모았다. 끝나면 체크하고 날짜를 적는다. **값(키·비밀번호·계정 ID)은 이 문서에 쓰지 않는다.**

## A. 지금 ~ 11-16(월) — 기동 전에 미리 (에이전트 작업과 무관하게 할 수 있음)

- [ ] **A-1 AWS 신규 계정 가입** (Free Plan, 비상업·개인 학습). 가입 화면 aws.amazon.com/free 에서 메모: 크레딧 $___ · 기간 ___개월 · t4g.small 적격 ☐. 계정 검증에 하루까지 걸릴 수 있다 — 그래서 먼저.
- [ ] **A-2 루트 MFA** 켜기 → **관리자 IAM 사용자**(또는 Identity Center) + MFA → 이후 루트 미사용.
- [ ] **A-3 Budgets 알림 $10 / $30 / $50**(`02-aws-budgets.md`). 고급 옵션에서 **크레딧을 비용에 포함**하는지 확인(크레딧이 상쇄하면 알림이 늦게 울린다). **EC2 를 만들기 전에.**
- [ ] **A-4 OpenAI 월 지출 한도** 설정(대시보드 Limits). 공개 중 LLM 비용 상한.
- [ ] **A-5 도메인 구입** + 등록기관 DNS 관리 화면 접근 확인. 구입하면 **도메인 이름을 메인 세션에 알린다**(11·12 문서의 `<도메인>` 자리표를 채운다 — Terraform 은 DNS 를 다루지 않으므로 변수가 없고, A 레코드는 등록기관에서 B-2 로 직접). 늦으면 `<EIP>.sslip.io` 로 먼저 띄운다.
- [x] **A-6 Terraform 설치** — **끝(2026-11-14, 사용자 지시로 에이전트가 `brew install hashicorp/tap/terraform` → v1.17.2 arm64)**. `fmt -check`·`init`(aws provider 5.100.0, lock 파일 커밋)·`validate` 통과, `ssh_cidr` 자리표·`0.0.0.0/0` 거부 확인. 정상 값 plan 은 B-1 때.
- [ ] **A-7 에이전트에게 줄 AWS 권한(Terraform 용)** — 사용자가 "aws 권한을 주면 terraform 으로" 하기로 했다(2026-11-14). 준비:
  1. IAM 사용자 하나를 **Terraform 전용**으로 만들고 액세스 키 1개 발급(루트·관리자 키는 쓰지 않는다).
  2. 권한은 이 배포에 필요한 것만: EC2(인스턴스·보안 그룹·키 페어·EIP·AMI 조회), VPC 읽기(기본 VPC·서브넷 조회). 간단히 가려면 `AmazonEC2FullAccess` 하나. S3·RDS·IAM 쓰기는 주지 않는다.
  3. 키 값은 **사용자 PC 의 `~/.aws/credentials` 에 프로필 이름(예 `relationship-deploy`)으로** 넣는다(`aws configure --profile relationship-deploy` 또는 파일 직접 편집). 에이전트는 그 파일을 읽지 않고(훅이 막음) `AWS_PROFILE=relationship-deploy` 이름만 받아 Terraform 이 SDK 로 읽게 한다. 값은 대화에 붙이지 않는다.
  4. 종료(11-19) 뒤 이 키를 **비활성·삭제**한다(12 문서 8번과 함께).
- [ ] **A-8 SSH 공개키 준비**: Terraform 이 키 페어를 만들 때 쓸 ed25519 공개키 — `ssh-keygen -t ed25519 -f ~/.ssh/relationship-deploy`(비밀번호 설정 권장). **공개키 경로**(`~/.ssh/relationship-deploy.pub`)만 에이전트에 알린다. 개인키는 PC 에만.
- [ ] **A-9 내 공인 IP 확인**(SSH 22 허용용): 발표 장소 와이파이에서도 바뀌니 기동 당일 다시 확인. `curl -s https://checkip.amazonaws.com`.
- [ ] **A-10 배포용 VAPID 키 쌍 생성**(로컬과 다른 새 쌍): `docs/RUNNING.md` "① VAPID 키는 사용자가 직접 만든다" 명령을 터미널에서 한 번. 두 줄은 서버 `.env` 에만 넣는다(아래 C-2).
- [ ] **A-11 배포용 OpenAI 키** 새로 발급(종료 때 폐기하기 쉽게). 값은 서버 `.env` 에만.

## B. 기동 지시 — 사용자가 "띄워 달라" 고 말할 때 (11-17 화 권장)

- [ ] **B-1** "띄워 달라" + 알릴 것 세 가지: `AWS_PROFILE` 이름 · 공개키 경로 · 도메인(또는 "sslip.io 로"). 그 전에 `infra/terraform.tfvars.example` 을 복사해 `infra/terraform.tfvars` 를 만들고 `ssh_cidr`(A-9 의 내 IP `/32`)·`ssh_public_key_path`(A-8)를 채운다(이 파일은 git 이 무시한다). 에이전트는 `init`·`validate`·`plan` 을 돌려 plan 출력(자원 5개: 보안 그룹·키 페어·EC2·EIP·연결)을 보여 준다.
- [ ] **B-1b `terraform apply` 는 사용자가 직접 실행**한다(보안 카드 §4 — 에이전트는 `apply`·`destroy` 를 하지 않는다): `cd /Users/sunwoo/Desktop/Portfolio/Relationship && AWS_PROFILE=<이름> terraform -chdir=infra apply -var-file=terraform.tfvars` → plan 을 한 번 더 보고 `yes`. 끝나면 `terraform -chdir=infra output` 의 `public_ip`·`sslip_hostname` 을 에이전트에 알린다. (에이전트가 apply 까지 하길 원하면 보안 카드 예외(L-007 과 같은 절차)를 따로 정해야 한다 — 그때 말해 주면 된다.)
- [ ] **B-2 DNS A 레코드**: 도메인 쓰면 등록기관에서 `<호스트명>` → EIP(TTL 300). `dig +short <호스트명>` 이 EIP 가 되면 알린다.
- [ ] **B-3 서버 `.env` 작성**(아래 C). Terraform 은 `.env` 를 만들지 않는다 — 비밀은 사용자 손으로만.
- [ ] **B-4 기동**: 11 문서 §6 명령(`git checkout <해시>` 는 에이전트가 알려 준 커밋) → `ps`·`logs` 결과를 에이전트에 알린다(비밀 값이 찍히지 않았는지 먼저 본다).
- [ ] **B-5 사람 점검**: 브라우저로 `https://<호스트명>/` 데모 5단계(채팅 → 인물 카드 → 브리핑 알림 받기 → 푸시 수신). `POST /chat` 은 본문이 있어 **사용자만** 보낸다(security §3).
- [ ] **B-6 완성 확인 질문**에 답한다(04-review 뒤 한 번).

## C. 서버 `.env` 에 넣는 값 (B-3 때, 서버에서 `nano .env && chmod 600 .env`)
이름만 — 표는 `11-ec2-minimal-deploy.md` §4. 14줄: `POSTGRES_USER`·`POSTGRES_PASSWORD`(서버에서 `openssl rand -hex 24`, **첫 기동 뒤 바꾸지 않는다**)·`POSTGRES_DB`·`SITE_ADDRESS`(호스트명만)·`OPENAI_API_KEY`(A-11)·`OPENAI_MODEL`·`LLM_PROVIDER=openai`·`LLM_PROVIDERS_ENABLED=openai`·`VAPID_PUBLIC_KEY`·`VAPID_PRIVATE_KEY`·`VAPID_SUBJECT=mailto:…`(A-10)·`APP_USER_ID=demo`·`APP_TIMEZONE=`(비움)·`BRIEFING_SCHEDULER_ENABLED=1`. **넣지 않는 것**: `DATABASE_URL`·`PUSH_DEV_PAGE_ENABLED`·`POSTGRES_PORT`·`POSTGRES_HOST`·Anthropic/Gemini 키.

## D. 발표 11-18(수)
- [ ] **D-1** 전날 저녁·당일 10분 전 `https://<호스트명>/api/health` 와 `/` 한 번씩(첫 요청 데우기).
- [ ] **D-2** 발표 장소에서 SSH 가 필요하면 보안 그룹 22 규칙의 "내 IP" 를 바꾼다: `infra/terraform.tfvars` 의 `ssh_cidr` 을 새 IP`/32` 로 고치고 **사용자가** `AWS_PROFILE=<이름> terraform -chdir=infra apply -var-file=terraform.tfvars`(규칙 1개만 바뀌는 plan 확인 뒤 `yes`) — 또는 콘솔에서 규칙 수정. 사이트 자체는 영향 없음.
- [ ] **D-3** 기억 초기화가 필요하면 11 문서 §10(`APP_USER_ID` 바꾸고 `up -d`).
- [ ] **D-4** 서버가 죽으면 로컬 실행(`docs/RUNNING.md`)으로 발표.

## E. 종료 11-19(목) 18:00 — `12-shutdown.md` 그대로
- [ ] **E-1** 백업 `pg_dump` → PC 로 내려받기(저장소에 넣지 않는다).
- [ ] **E-2** 에이전트에게 "종료해 달라" → 에이전트가 12 문서 순서와 명령을 보여 준다 → 사용자가 `AWS_PROFILE=<이름> terraform -chdir=infra destroy -var-file=terraform.tfvars` 를 **직접** 실행(`destroy` 는 훅이 막아 에이전트가 못 한다; 인스턴스·EIP·보안 그룹·키 페어가 한 번에 사라진다). Terraform 이 안 되면 콘솔에서 인스턴스 종료·EIP 해제·보안 그룹·키 페어 삭제.
- [ ] **E-3** EBS `available` 볼륨 0·스냅샷 0·EIP 0 확인.
- [ ] **E-4** 비밀 회전: OpenAI 배포용 키 폐기 · 배포용 VAPID 폐기 · **A-7 의 Terraform 액세스 키 비활성·삭제** · PC 의 `.pem`/개인키 정리.
- [ ] **E-5** 도메인 A 레코드 삭제(쓴 경우). 다음 날 Billing 에서 EC2·EBS·IPv4 사용량 증가 0 확인.
- [ ] **E-6** 완성 확인 질문(P9 04-review)에 답한다 → 승격 → P2b(인물 삭제) 재개.

## F. 로컬 정리 (언제든, 에이전트는 못 함)
- [ ] 로컬 Docker 의 스모크 볼륨 3개: `docker volume rm relationship-prod_pgdata relationship-prod_caddy_data relationship-prod_caddy_config`
- [ ] 무효 evidence 4개(마지막은 U3b 변이 이름 파일의 불완전 사본 — `…-u3b-names-v11-v29.txt` 가 완전본): `rm /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P9-infra/evidence/20261114-1512-u3b-mutations-names.txt` 와 `rm /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261107-1455-u7fix-ruff.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/fixes/evidence/20261108-2000-L-007-test-guards.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261108-2009-u7fix3-review-baseline.txt`
