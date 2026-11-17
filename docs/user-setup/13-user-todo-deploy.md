# 13 · 사용자가 할 일 — 배포(P9) 전후 (2026-11-14 작성, 졸업평가 11-18 · 종료 11-19 18:00)

> Refs: P9-infra CR-005 D17 · `11-ec2-minimal-deploy.md`(상세 절차) · `12-shutdown.md`(종료) · `02-aws-budgets.md`
> 사용자 지시(2026-11-14): "내가 해야할 일을 문서로 작성해서 놔둬". 에이전트가 할 수 없는 것(계정·결제·비밀 값·콘솔·도메인)만 모았다. 끝나면 체크하고 날짜를 적는다. **값(키·비밀번호·계정 ID)은 이 문서에 쓰지 않는다.**

## A. 지금 ~ 11-16(월) — 기동 전에 미리 (에이전트 작업과 무관하게 할 수 있음)

- [ ] **A-1 AWS 신규 계정 가입** (Free Plan, 비상업·개인 학습). 가입 화면 aws.amazon.com/free 에서 메모: 크레딧 $___ · 기간 ___개월 · t4g.small 적격 ☐. 계정 검증에 하루까지 걸릴 수 있다 — 그래서 먼저.
- [ ] **A-2 루트 MFA** 켜기 → **관리자 IAM 사용자**(또는 Identity Center) + MFA → 이후 루트 미사용.
- [x] **A-3 Budgets 알림 $10 / $30 / $50**(`02-aws-budgets.md`) — **끝(2026-11-15, 에이전트가 Chrome 에서 생성)**: `capstone2-10`·`-30`·`-50`, 각각 Actual 100% 메일, **크레딧 제외 필터 적용**. 크레딧 잔액 $120. 아래는 원래 안내. 고급 옵션에서 **크레딧을 비용에 포함**하는지 확인(크레딧이 상쇄하면 알림이 늦게 울린다). **EC2 를 만들기 전에.**
- [x] **A-4 OpenAI 월 지출 한도** 설정(대시보드 Limits). 공개 중 LLM 비용 상한. — **끝(2026-11-15, 사용자 지시로 에이전트가 Chrome 에서 설정)**: 조직 월 한도 $10 + **Enforce a hard limit 켬**("Limit enforced" 확인). 알림 80%($8)·100%($10)는 기존 그대로. 주의: 한도에 닿으면 조직 전체 요청이 429 로 거부된다(로컬 개발 포함, 강제는 즉시가 아니라 약간 넘을 수 있음).
- [x] **A-5 도메인** — **(2026-11-17 갱신) `relmemo.com` 을 사서 적용했다. 옛 주소 `54-79-202-221.sslip.io` 도 함께 열린다 — `14-domain.md` 맨 위 "적용 결과".** 종료 때 E-5 의 레코드 삭제가 다시 해당한다. 아래는 이전 결정(이력): **사지 않는다(사용자 결정 2026-11-15): `<EIP>.sslip.io` 로 진행.** B-2(DNS A 레코드)·E-5 의 레코드 삭제는 해당 없음. 아래는 원래 안내(이력). ~~도메인 구입~~ + 등록기관 DNS 관리 화면 접근 확인. 구입하면 **도메인 이름을 메인 세션에 알린다**(11·12 문서의 `<도메인>` 자리표를 채운다 — Terraform 은 DNS 를 다루지 않으므로 변수가 없고, A 레코드는 등록기관에서 B-2 로 직접). 늦으면 `<EIP>.sslip.io` 로 먼저 띄운다.
- [x] **A-6 Terraform 설치** — **끝(2026-11-14, 사용자 지시로 에이전트가 `brew install hashicorp/tap/terraform` → v1.17.2 arm64)**. `fmt -check`·`init`(aws provider 5.100.0, lock 파일 커밋)·`validate` 통과, `ssh_cidr` 자리표·`0.0.0.0/0` 거부 확인. 정상 값 plan 은 B-1 때.
- [ ] **A-7 에이전트에게 줄 AWS 권한(Terraform 용)** — 사용자가 "aws 권한을 주면 terraform 으로" 하기로 했다(2026-11-14). 준비:
  0. **진행(2026-11-15)**: 1·2번의 사용자 생성과 권한 연결은 에이전트가 Chrome 에서 끝냄 — IAM 사용자 `relationship-terraform`(콘솔 접속 없음, `AmazonEC2FullAccess` 직접 연결). **남은 것은 사용자 몫: 액세스 키 발급(1번 뒷부분)과 3번 `aws configure`.**
  1. IAM 사용자 하나를 **Terraform 전용**으로 만들고 액세스 키 1개 발급(루트·관리자 키는 쓰지 않는다).
  2. 권한은 이 배포에 필요한 것만: EC2(인스턴스·보안 그룹·키 페어·EIP·AMI 조회), VPC 읽기(기본 VPC·서브넷 조회). 간단히 가려면 `AmazonEC2FullAccess` 하나. S3·RDS·IAM 쓰기는 주지 않는다.
  3. 키 값은 **사용자 PC 의 `~/.aws/credentials` 에 프로필 이름(예 `relationship-deploy`)으로** 넣는다(`aws configure --profile relationship-deploy` 또는 파일 직접 편집). 에이전트는 그 파일을 읽지 않고(훅이 막음) `AWS_PROFILE=relationship-deploy` 이름만 받아 Terraform 이 SDK 로 읽게 한다. 값은 대화에 붙이지 않는다.
  4. 종료(11-19) 뒤 이 키를 **비활성·삭제**한다(12 문서 8번과 함께).
- [ ] **A-8 SSH 공개키 준비**: Terraform 이 키 페어를 만들 때 쓸 ed25519 공개키 — `ssh-keygen -t ed25519 -f ~/.ssh/relationship-deploy`(비밀번호 설정 권장). **공개키 경로**(`~/.ssh/relationship-deploy.pub`)만 에이전트에 알린다. 개인키는 PC 에만.
- [ ] **A-9 내 공인 IP 확인**(SSH 22 허용용): 발표 장소 와이파이에서도 바뀌니 기동 당일 다시 확인. `curl -s https://checkip.amazonaws.com`.
- [x] **A-10 VAPID 키** — **새로 만들지 않는다(사용자 결정 2026-11-15): 로컬 `.env` 의 기존 쌍을 서버 `.env` 에 그대로 넣는다.** 그래서 종료(E-4) 때 "배포용 VAPID 폐기" 는 **로컬 VAPID 쌍을 새로 만들어 교체**하는 것으로 바뀐다(서버에 올라갔던 키이므로). 아래는 원래 안내. ~~배포용 VAPID 키 쌍 생성~~(로컬과 다른 새 쌍): `docs/RUNNING.md` "① VAPID 키는 사용자가 직접 만든다" 명령을 터미널에서 한 번. 두 줄은 서버 `.env` 에만 넣는다(아래 C-2).
- [x] **A-11 OpenAI 키** — **새로 발급하지 않는다(사용자 결정 2026-11-15): 로컬 `.env` 의 기존 키를 서버 `.env` 에 그대로 넣는다.** 종료(E-4) 때는 **그 키를 폐기하고 로컬용 키를 새로 발급**해 로컬 `.env` 를 바꾼다. 원래 안내: ~~배포용 OpenAI 키 새로 발급(종료 때 폐기하기 쉽게)~~. 값은 `.env` 에만.

## B. 기동 지시 — 사용자가 "띄워 달라" 고 말할 때 (11-17 화 권장)

> **실제 진행(2026-11-15 저녁) — B-1~B-4 끝.** 달라진 점 세 가지:
> 1. **리전은 시드니(`ap-southeast-2`)다.** 간편 가입 계정은 연락처 국가에 따라 리전이 하나로 고정되고(한국 → 시드니) 조직 정책이 다른 리전의 EC2 호출을 거부한다. 서울을 쓰려면 계정 "고급 기능 활성화"(되돌릴 수 없음)가 필요해 시드니로 갔다.
> 2. **`infra/terraform.tfvars` 는 만들지 않았다**(에이전트 쓰기 차단). 값은 명령줄 `-var` 로 넘긴다 — apply·destroy 모두 **`-var 'ssh_cidr=<내 IP>/32' -var 'ssh_public_key_path=~/.ssh/relationship-deploy.pub' -var 'region=ap-southeast-2'`** 세 개를 붙인다(`-var-file` 대신). 프로필은 `AWS_PROFILE=relationship-deploy`.
> 3. 호스트명 `54-79-202-221.sslip.io`(EIP `54.79.202.221`), 배포 커밋 `843e6e7`. 서버 `.env` 는 PC 에서 만들어 ssh 로 보냈다(OpenAI·VAPID 는 로컬 값 재사용, 줄 수 16 — 로컬 `.env` 에 같은 이름이 두 번 적힌 것 2개, 뒤 값이 쓰인다). 바깥 스모크 S1·S2·S3·S4·S10 통과(evidence `20261115-1950-u4-smoke-public.txt`). **남은 것: B-5 사람 점검, B-6.**

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
- [ ] **D-3** 빈 기억이 필요하면 화면에서 새 계정을 가입한다(CR-006 뒤 — 계정마다 기억이 따로, `.env` 수정 없음).
- [ ] **D-4** 서버가 죽으면 로컬 실행(`docs/RUNNING.md`)으로 발표.

## E. 종료 11-19(목) 18:00 — `12-shutdown.md` 그대로
- [ ] **E-1** 백업 `pg_dump` → PC 로 내려받기(저장소에 넣지 않는다).
- [ ] **E-2** 에이전트에게 "종료해 달라" → 에이전트가 12 문서 순서와 명령을 보여 준다 → 사용자가 **`cd /Users/sunwoo/Desktop/Portfolio/Relationship && AWS_PROFILE=relationship-deploy terraform -chdir=infra destroy -var 'ssh_cidr=<apply 때 넣은 IP>/32' -var 'ssh_public_key_path=~/.ssh/relationship-deploy.pub' -var 'region=ap-southeast-2'`** 를 **직접** 실행(실제 진행에 맞춘 명령 — `-var-file` 이 아니다. 콘솔로 확인할 때도 리전을 시드니로; `destroy` 는 훅이 막아 에이전트가 못 한다; 인스턴스·EIP·보안 그룹·키 페어가 한 번에 사라진다). Terraform 이 안 되면 콘솔에서 인스턴스 종료·EIP 해제·보안 그룹·키 페어 삭제.
- [ ] **E-3** EBS `available` 볼륨 0·스냅샷 0·EIP 0 확인.
- [ ] **E-4** 비밀 회전: OpenAI 키는 기존 것을 재사용했으므로(A-11) **그 키를 폐기하고 새 키를 발급해 로컬 `.env` 교체** · VAPID 는 기존 쌍을 재사용했으므로(A-10) **로컬 VAPID 쌍을 새로 만들어 교체** · **A-7 의 Terraform 액세스 키 비활성·삭제** · PC 의 `.pem`/개인키 정리.
- [ ] **E-5** 도메인 A 레코드 삭제(쓴 경우). 다음 날 Billing 에서 EC2·EBS·IPv4 사용량 증가 0 확인.
- [ ] **E-6** 완성 확인 질문(P9 04-review)에 답한다 → 승격 → P2b(인물 삭제) 재개.

## G. 로그인 버전 반영 (P9b-auth U7 — 에이전트가 "반영해 달라" 고 해시를 알려 준 뒤, 11-16~11-17)

> **이 반영은 운영 서버의 기존 데이터(인물·사건·일정·질문·푸시 구독·판단 기록)를 한 번 비운다**(사용자 결정 2026-11-15 "모두 비운다"). **반영 뒤에는 옛 버전으로 되돌릴 수 없다** — 문제가 생기면 에이전트가 고친 새 해시를 다시 올린다. 서버 `.env` 는 고치지 않는다(새 값 없음).

- [ ] **G-1** (선택) 반영 전 DB 백업 1회 — `12-shutdown.md` 1항의 `pg_dump` 명령. 비우기로 했으므로 필수 아님.
- [ ] **G-2** 서버 접속: `ssh -i ~/.ssh/relationship-deploy ubuntu@54.79.202.221`
- [ ] **G-3** 코드 받기: `cd ~/Relationship && git fetch origin && git checkout 4be331b` (2026-11-16 기준 — 로컬 운영 구성 스모크를 통과한 해시. 그 뒤 수정이 생기면 에이전트가 새 해시를 알려 준다)
- [ ] **G-4** 기동(옛 backend 가 내려가고 새 backend 가 올라오면서 리비전 0003 이 돈다 — 따로 `alembic` 을 치지 않는다): `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`
- [ ] **G-5** 상태: `docker compose -f docker-compose.prod.yml ps` → 세 서비스 running, postgres·backend healthy. 출력을 에이전트에 붙인다.
- [ ] **G-6** 로그: `docker compose -f docker-compose.prod.yml logs --tail=200 backend | grep -c Traceback` (기대 0) 와 `docker compose -f docker-compose.prod.yml logs backend | grep "Running upgrade"` (기대: `0002 -> 0003` 한 줄). 두 출력을 에이전트에 붙인다.
- [ ] **G-7** 브라우저(탭 하나)로 `https://54-79-202-221.sslip.io` → 로그인 화면이 뜨는지 → **시연 계정 가입**(아이디·비밀번호는 직접 정하고 저장소·채팅에 적지 않는다. 아이디 3~20자 영문 소문자·숫자·밑줄, 비밀번호 8자 이상) → 채팅 한 줄 → 로그아웃 → 다시 로그인하면 방금 대화가 보이는지.
- [ ] **G-8** 발화 목록 13개(`docs/wiki/packages/P9b-auth/u8-demo-script.md`)를 시연 계정 채팅에 넣어 데이터를 쌓는다. 확인 칩이 뜨면 직접 판단해 누른다.
- [ ] **G-9** 리허설: (가) 로그아웃 → 새 계정 가입 → 인물 화면이 비어 있음, 채팅 기록 없음 (나) 로그아웃 → 시연 계정 로그인 → 인물 카드·브리핑·지난 대화가 그대로. **로그아웃은 채팅 화면에서**(인물 상세 화면에서 로그아웃하면 다음 계정의 첫 화면이 "인물을 찾을 수 없어요" 로 뜬다 — 정보 노출은 아님), **탭은 하나만**.
- [ ] **G-10** OpenAI 사용량 확인 — 11-17 저녁과 11-18 아침. 누구나 가입할 수 있어 월 한도 $10 이 평가 전에 소진될 수 있다. 소진됐으면 한도를 올리거나 키를 바꾼다(사용자만 가능).
- [ ] **G-11** (푸시를 시연에 쓸 때) 시연 계정으로 로그인한 브라우저에서 브리핑 화면 "알림 받기" → 권한 허용 → 알림을 눌러 그 브리핑이 열리는지.

## H. 닉네임·중복검사 버전 반영 (P9b-auth U11, CR-007 — 2026-11-16, 해시 `bd0e061`)

> 가입 화면에 닉네임 칸과 아이디·닉네임 "중복 확인" 이 생긴다. **이번 반영은 데이터를 지우지 않는다** — 계정 표에 닉네임 칸만 더하고, 이미 있는 계정은 닉네임이 아이디와 같은 값으로 채워진다(닉네임을 나중에 바꾸는 기능은 없다). 서버 `.env` 는 고치지 않는다(새 값 없음).
> 로컬에서 운영과 같은 구성으로 먼저 확인했다(계정이 있는 0003 DB → 0004, 계정 수 그대로, `evidence/20261116-0735~0737-u11-*.txt`).
> **시연 계정은 이 반영이 끝난 뒤에 가입한다** — 먼저 만든 계정은 닉네임이 아이디로 고정된다.

- [ ] **H-1** 서버 접속: `ssh -i ~/.ssh/relationship-deploy ubuntu@54.79.202.221`
- [ ] **H-2** 코드 받기: `cd ~/Relationship && git fetch origin && git checkout bd0e061`
- [ ] **H-3** 기동(새 backend 가 올라오면서 리비전 0004 가 돈다 — 따로 `alembic` 을 치지 않는다): `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`
- [ ] **H-4** 상태: `docker compose -f docker-compose.prod.yml ps` → 세 서비스 running, postgres·backend healthy. 출력을 에이전트에 붙인다.
- [ ] **H-5** 로그: `docker compose -f docker-compose.prod.yml logs --tail=200 backend | grep -c Traceback` (기대 `0`) 와 `docker compose -f docker-compose.prod.yml logs backend | grep "Running upgrade"` (기대: `0003 -> 0004` 가 있는 줄). 두 출력을 에이전트에 붙인다.
- [ ] **H-6** 에이전트에 "반영했어" 라고 알린다 → 에이전트가 바깥 확인(본문 없는 조회)을 한다: `/api/health` 의 `alembic_revision` 이 `0004`, `/api/auth/availability?username=test` 가 `taken`.
- [ ] **H-7** 브라우저(열려 있던 탭은 **새로고침**) → 기존 `test` 계정은 사이드바 아래에 `test · test · 로그아웃` 으로 보인다(닉네임 = 아이디) → 로그아웃 → "계정 만들기" → 아이디·닉네임을 넣고 칸마다 "중복 확인" → 가입 → 사이드바에 `닉네임 · 아이디 · 로그아웃`.
  - 닉네임 규칙: 한글(완성형)·영문·숫자·밑줄 2~20자, 가운데 공백 불가. 영문은 소문자로 저장·표시된다(`Demo` → `demo`).
  - "중복 확인" 을 누르지 않아도 가입은 된다. 겹치면 가입할 때 화면에 이유가 나온다.
  - 아이디 앞뒤에 공백이 들어가면 "형식이 맞지 않는다" 로 나온다(닉네임은 앞뒤 공백을 알아서 뗀다).
- [ ] **H-8** 이어서 G-8(시연 계정에 발화 13개) · G-9(리허설) · G-10(OpenAI 사용량) · G-11(푸시).

### 미리 만든 계정 지우기 (사용자 요청 2026-11-16 "테스트 계정을 미리 만들었던걸 삭제하고 진행")

앱에는 계정 삭제 기능이 없다. 서버에서 아래를 한 번에 붙여 넣는다(`'test'` 자리에 지울 아이디). 그 계정의 인물·사건·일정·질문·알림 구독·판단 기록·대화·로그인 세션이 함께 지워지고 **되돌릴 수 없다**. 다른 계정은 건드리지 않는다. 같은 문장을 로컬 개발 DB 에서 되돌리는 트랜잭션으로 실행해 문법과 동작을 확인했다(운영 서버에서는 에이전트가 실행하지 않았다).

```
cd ~/Relationship
docker compose -f docker-compose.prod.yml exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
BEGIN;
CREATE TEMP TABLE _t ON COMMIT DROP AS SELECT id FROM users WHERE username = 'test';
SELECT count(*) AS accounts_to_delete FROM _t;
DELETE FROM agent_traces WHERE session_id IN (SELECT 'chat:' || id FROM _t);
DELETE FROM pending_questions WHERE user_id IN (SELECT id FROM _t);
DELETE FROM push_subscriptions WHERE user_id IN (SELECT id FROM _t);
DELETE FROM persons WHERE user_id IN (SELECT id FROM _t);
DELETE FROM users WHERE id IN (SELECT id FROM _t);
COMMIT;
SELECT username, nickname FROM users ORDER BY created_at;
SQL
```

기대 출력: `accounts_to_delete` 가 `1`, 이어서 `DELETE n` 다섯 줄(마지막이 `DELETE 1`), `COMMIT`, 남은 계정 목록. `accounts_to_delete` 가 `0` 이면 아이디가 틀린 것이다(아무것도 지워지지 않는다). 지운 뒤 그 계정으로 로그인돼 있던 브라우저는 새로고침하면 로그인 화면으로 돌아간다.

### H 가 잘못됐을 때

- **먼저**: H-4·H-5 출력을 에이전트에 붙인다. 고친 새 해시를 받아 H-2·H-3 을 다시 한다(권장).
- **급하게 로그인 버전(`4be331b`, 닉네임 없음)으로 되돌려야 할 때** — 로컬에서 예행해 동작을 확인한 순서다(`evidence/20261116-0737-u11-rollback.txt`). 계정과 기억 데이터는 그대로 남고 **닉네임 값만 사라진다**. 순서를 바꾸지 않는다(옛 버전은 0004 상태의 DB 에서 뜨지 않는다).
  1. `docker compose -f docker-compose.prod.yml stop backend`
  2. `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml run --rm --entrypoint python backend -m alembic downgrade 0003` → `Running downgrade 0004 -> 0003` 한 줄
  3. `git checkout 4be331b`
  4. `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`
  - 1~4 사이에는 사이트가 잠깐 열리지 않는다(502). 되돌린 뒤 나중에 다시 닉네임 버전을 올리면 **모든 계정의 닉네임이 아이디 값으로 다시 채워진다**(그 전에 정한 닉네임은 남지 않는다).
  - 에이전트는 이 명령을 운영 서버에서 실행해 보지 않았다(로컬 운영 구성에서만 확인).

## I. MCP 버전 반영 (P9b-auth U14, CR-008 — 2026-11-17 밤, 해시 `c85a0e8`) — **에이전트가 SSH 로 반영함**

> 로그인한 화면에 "AI 연결" 이 생기고, `https://relmemo.com/mcp` 에 읽기 전용 도구 4개가 열린다. **데이터를 지우지 않는다** — 토큰 표(`mcp_tokens`) 하나만 더한다(리비전 0005). 서버 `.env` 는 고치지 않았다(compose 가 MCP 를 기본으로 켠다).
> 반영 전후 운영 DB 행 수가 같다: 계정 1 · 인물 7 · 사건 100 · 대화 278 · 일정 2 (`evidence/20261117-2359-u14-deploy-c85a0e8-output.txt`). 바깥 확인: `/api/health` `0005`, `/mcp` 는 토큰 없이 401(`evidence/20261117-2359-u14-public-get.txt`).

- [ ] **I-1 (사용자)** 열려 있던 탭을 **새로고침** → 사이드바에 "AI 연결" 이 보이는지, 채팅·인물 카드·브리핑이 평소대로인지.
- [ ] **I-2 (사용자)** 토큰 만들기와 Claude Code 연결 — `15-mcp-connect.md` 2·3절. 토큰 값은 에이전트에게 주지 않는다.
- [ ] **I-3 (사용자)** 결과를 **토큰 없이** 말로 알려 준다("연결됨, 인물 7명 나옴" 정도).

### MCP 만 급히 끌 때

서버에서 `.env` 에 `MCP_ENABLED=0` 한 줄을 넣고 `docker compose -f docker-compose.prod.yml up -d`. `/mcp` 만 404 가 되고 나머지는 그대로다. 다시 켜려면 그 줄을 지우고 같은 명령. 로컬 운영 구성에서 예행했다(`evidence/20261117-2349-u14-caddy-off-drill.txt`).

### I 가 잘못됐을 때 — 이전 버전(`935aa4a`)으로 되돌리기

**`git checkout 935aa4a` 만 하면 backend 가 뜨지 않는다**(옛 코드는 리비전 `0005` 를 모른다). 아래 순서를 바꾸지 않는다. 계정·기억 데이터는 그대로 남고 **연결 토큰만 사라진다**. 로컬 운영 구성에서 예행한 순서다(①~④ 9초, `evidence/20261118-0000-u14-rollback-drill.txt`) — 운영 서버에서는 실행해 보지 않았다.

1. `docker compose -f docker-compose.prod.yml stop backend`
2. `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml run --rm --entrypoint python backend -m alembic downgrade 0004` → `Running downgrade 0005 -> 0004` 한 줄
3. `git checkout 935aa4a`
4. `GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build`

## F. 로컬 정리 (언제든, 에이전트는 못 함)
- [ ] 로컬 Postgres 의 시험용 DB 2개(P9b-auth U1 이 만든 빈 DB, 지워도 다음 테스트 때 하나는 다시 생긴다): `relationship_test_mig`, `relationship_test_mig_v15` — 원하면 `dropdb` 로 직접.
- [ ] 로컬 Docker 의 스모크 볼륨 3개: `docker volume rm relationship-prod_pgdata relationship-prod_caddy_data relationship-prod_caddy_config`
- [ ] 무효 evidence 4개(마지막은 U3b 변이 이름 파일의 불완전 사본 — `…-u3b-names-v11-v29.txt` 가 완전본): `rm /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P9-infra/evidence/20261114-1512-u3b-mutations-names.txt` 와 `rm /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261107-1455-u7fix-ruff.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/fixes/evidence/20261108-2000-L-007-test-guards.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261108-2009-u7fix3-review-baseline.txt`
