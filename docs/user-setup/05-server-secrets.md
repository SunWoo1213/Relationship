# 05 · 실서버·배포 비밀 (SSM Parameter Store · VAPID · GitHub Actions) — P7/P9 때

> **부분 대체(CR-005 · D17, 2026-11-14)**: 배포는 AWS 최소 구성(EC2 1대 + Compose)이라 **SSM Parameter Store·GitHub Actions 배포 secrets 절은 해당 없음**. 배포 비밀은 사용자가 서버 `.env`(권한 600)에 직접 쓴다 — 이름 표는 `11-ec2-minimal-deploy.md` §4. 이 문서는 **VAPID 키 생성 절만 유효**(배포용은 새 키 쌍, 결정 N).

## 언제 필요한가
- **P7 웹푸시**: VAPID 키 쌍 생성 → `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `VAPID_SUBJECT`.
- **P9 인프라**: Terraform 실행 자격(AWS 계정), SSM Parameter Store 에 `.env.example` 의 이름 전부(값은 SSM 에만), GitHub Actions secrets(AWS 배포 역할·S3/CloudFront), EC2 의 Caddy 가 Let's Encrypt 를 받을 도메인(D7).

## 왜 사용자 몫인가
AWS 계정·도메인·GitHub 저장소 설정은 사용자 소유이고, 비밀 값은 에이전트가 다루지 않는다. Terraform 코드는 infra-agent(신설 예정)가 쓰되 `terraform apply` 는 사용자가 실행한다(`security.md` §4 — destroy 금지).

## 절차 (P9 착수 시 채운다)
1. `.env.example` 의 이름 목록 ↔ SSM 파라미터 이름 대조(값은 보지 않는다) — `SERVER-CHECKLIST.md` 0-2.
2. VAPID 키 생성 명령은 P7 계획(01-plan)에서 확정한다(py_vapid 또는 web-push CLI). 공개키는 프론트에 들어가고 개인키는 SSM 에만.
3. 도메인·DNS: CloudFront → EC2(Caddy) 경로, ALB 미사용(D7).
4. GitHub → Settings → Secrets and variables → Actions: 배포에 필요한 이름만.
5. 직전 배포 이미지 태그(커밋 해시) 메모 — 되돌리기 기준(SERVER-CHECKLIST 0-4).

## 끝났다는 증거
SERVER-CHECKLIST §0 표 5행 통과 + §1~§4 evidence 파일. 값은 어디에도 없음.
