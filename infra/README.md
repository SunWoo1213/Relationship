# infra/ — Terraform 로 EC2 한 대 띄우기 (P9-infra U3b)

> Refs: P9-infra D17 R14 CR-005 · `docs/user-setup/11-ec2-minimal-deploy.md`(콘솔 절차 — 이 폴더가 §1~§2 를 대신한다) · `12-shutdown.md`(종료) · `13-user-todo-deploy.md`(사용자 할 일) · `docs/wiki/security.md` §1·§4
> 사용자 지시(2026-11-14): "내가 나중에 너에게 aws 권한을 주면 terraform 으로 수행하도록 세팅만 해줘". **이 폴더는 선언만 담는다. 지금까지 `apply` 한 적 없다.**

## 만드는 것

보안 그룹 1 · 키 페어 1 · EC2 1(Ubuntu 24.04 arm64 `t4g.small`, gp3 20GB, 종료 시 삭제) · Elastic IP 1(+연결) — 5개 자원. 기본 VPC 를 조회만 한다.
첫 부팅 때 `user_data.sh` 가 Docker(공식 apt 저장소 방식)·compose 플러그인을 깔고 `ubuntu` 를 docker 그룹에 넣고 저장소를 `/home/ubuntu/Relationship` 에 clone 한다.

**만들지 않는 것**: `.env`(비밀은 사용자가 서버에서 직접 — 11 문서 §4) · DNS 레코드(도메인은 등록기관, 도메인 전엔 `sslip_hostname` 출력) · IAM · S3 백엔드 · 모듈. 보안 그룹 인바운드는 80·443(전체)과 22(`ssh_cidr` 하나)뿐이고 5432·8000 규칙은 없다.

## 전제 (13 문서 A-6 ~ A-9 — 사용자 몫)

| 항목 | 내용 |
|---|---|
| A-6 | `terraform` 설치(`terraform -version`, 1.5 이상) |
| A-7 | Terraform 전용 IAM 사용자 + 액세스 키를 사용자 PC 의 `~/.aws/credentials` 프로필(예 `relationship-deploy`)로. 키 값은 대화·코드·tfvars 에 넣지 않는다 |
| A-8 | ed25519 공개키 파일(예 `~/.ssh/relationship-deploy.pub`) — 경로만 쓴다. 개인키는 PC 에만 |
| A-9 | 내 공인 IP(`curl -s https://checkip.amazonaws.com`) — 22 허용용, 기동 당일 다시 확인 |

자격 증명은 코드에 없다. `provider "aws"` 에는 `access_key`·`secret_key`·`profile` 이 없고, Terraform 이 **환경변수 `AWS_PROFILE`** 로 `~/.aws/credentials` 를 읽는다. 에이전트는 그 파일을 읽지 않는다(훅).

## 실행 순서 (저장소 루트에서)

```
cp infra/terraform.tfvars.example infra/terraform.tfvars     # 사용자가 값을 채운다 (ssh_cidr · ssh_public_key_path). 커밋 금지(.gitignore)

AWS_PROFILE=<프로필 이름> terraform -chdir=infra init
terraform -chdir=infra fmt -check
AWS_PROFILE=<프로필 이름> terraform -chdir=infra validate
AWS_PROFILE=<프로필 이름> terraform -chdir=infra plan -var-file=terraform.tfvars
```

1. `init` — provider 를 받는다. 처음 한 번 `infra/.terraform.lock.hcl` 이 생기면 **커밋한다**(버전 잠금, 비밀 아님).
2. `plan` — 자원 5개 생성(`Plan: 5 to add`)·인스턴스 유형 `t4g.small`·22 의 cidr 이 `/32` 인지 눈으로 확인한다. 출력은 `evidence/` 로 남긴다.
3. `apply` — **사용자가 직접 실행한다**(에이전트는 `plan` 까지 — security §4 "apply/destroy 는 사용자"). 사용자가 "띄워 달라" 고 한 뒤 1회, 사용자 터미널에서 `AWS_PROFILE=<프로필 이름> terraform -chdir=infra apply -var-file=terraform.tfvars` 를 치고 plan 을 한 번 더 본 뒤 `yes` 를 입력한다. 에이전트는 명령을 보여 주고 결과 출력을 evidence 로 받는다. (`apply -auto-approve` 는 safety-guard 가 막는다.)
4. `output` — `AWS_PROFILE=<프로필 이름> terraform -chdir=infra output` 으로 `public_ip`·`ssh_command`·`sslip_hostname`·`instance_id` 를 본다.
5. 이후는 사람 몫 — 첫 부팅이 끝났는지 `ssh -i <개인키> ubuntu@<public_ip>` 로 들어가 `cloud-init status --wait` · `docker compose version` 으로 확인한 뒤 **11 문서 §3-4(배포 커밋 checkout)부터** — `.env` 작성(§4) · 호스트명(§5) · 기동(§6) · 스모크(§7).

## 바꿔 적용하기

- 발표 장소에서 IP 가 바뀌면(13 문서 D-2) `ssh_cidr` 만 고쳐 `plan` → `apply` 한다. `lifecycle.ignore_changes` 가 AMI 최신화·user-data 수정으로 인스턴스가 교체(= DB 볼륨 소실)되는 것을 막는다. 보안 그룹 규칙 하나만 바뀐다.
- `instance_type` 을 x86(`t3.*`)으로 바꾸면 `ami_architecture = "amd64"` 도 함께 바꾼다.

## 끝내기 (12 문서)

**`terraform destroy` 는 safety-guard 가 막으므로 에이전트가 못 한다 — 사용자가 직접 실행한다**(security §4):

```
AWS_PROFILE=<프로필 이름> terraform -chdir=infra destroy -var-file=terraform.tfvars
```

먼저 12 문서 1번(서버에서 `pg_dump` → PC 로 내려받기)을 마친 뒤. 인스턴스(루트 볼륨 `delete_on_termination=true`)·Elastic IP·보안 그룹·키 페어가 함께 사라진다. 그 뒤 12 문서 4번(`available` 볼륨 0·스냅샷 0·EIP 0 확인) · 8번(Terraform 액세스 키 비활성·삭제)을 이어서 한다. 콘솔에서 지우는 길도 12 문서에 그대로 있다.

## 상태 파일

로컬 `infra/terraform.tfstate`(+ `.backup`)에 쌓인다. **커밋 금지**(`.gitignore`, safety-guard 도 스테이징을 막는다). 상태 파일에는 인스턴스 id·IP 가 들어 있고 비밀은 없지만, 습관상 저장소에 넣지 않는다. 잃어버리면 Terraform 이 자원을 잊으므로 종료 전까지 PC 에 둔다. 원격 백엔드(S3)는 쓰지 않는다.
