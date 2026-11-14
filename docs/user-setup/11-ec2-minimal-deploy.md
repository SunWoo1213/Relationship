# 11 · EC2 최소 구성 배포 — 신규 AWS 계정, 한 대, Docker Compose (P9-infra U3)

> Refs: P9-infra CR-005 D17 security §1 §3 §4 §5 · `02-aws-budgets.md` · `09-aws-deploy.md`(원안, 부분 유효) · `12-shutdown.md` · `SERVER-CHECKLIST.md`
> **실제 EC2 생성·기동은 사용자가 "띄워 달라" 고 지시한 뒤에만 한다**(CR-005 개정 ②). 이 문서는 그때 위에서부터 그대로 따라가는 절차다. 단계마다 "끝났다는 증거" 는 이름·상태만 적고 **계정 ID·키 값·비밀번호는 어디에도 적지 않는다**(security §1).
> 사용자 결정(2026-11-14): 인스턴스 **t4g.small(ARM, 2GB) + gp3 20GB** · 리전 **서울 `ap-northeast-2`** · 접속 **SSH 키 페어, 22 는 내 IP 만** · 호스트명 **새로 구입한 도메인**(준비 전엔 `<EIP>.sslip.io`) · 종료 **11-19(목) 18:00 KST**(12 문서).

## 0. 미리(가능하면 11-16 월까지) — 콘솔 작업, "띄우기" 가 아니다
| # | 할 것 | 끝났다는 증거 |
|---|------|------------|
| 0-1 | **AWS 신규 계정 가입**(Free Plan — 가입 화면 aws.amazon.com/free 에서 크레딧 금액·기간·적격 인스턴스 목록을 확인해 아래 표에 메모). 용도: **비상업·개인 학습(졸업평가 데모)** | 계정 활성 메일. 메모: 크레딧 $___ / 기간 ___개월 / t4g.small 적격 ☐ |
| 0-2 | 루트 **MFA** → 관리자 IAM 사용자(또는 IAM Identity Center) 생성 + MFA → 이후 루트는 쓰지 않는다 | IAM 사용자 이름(값 아님) |
| 0-3 | **Budgets 알림 $10 / $30 / $50**(`02-aws-budgets.md` 그대로). 고급 옵션에서 **크레딧을 비용에 포함**하는지 확인 — 크레딧이 상쇄하면 "실제 비용" 알림이 늦게 울린다 | 예산 3개 `활성` |
| 0-4 | **OpenAI 대시보드 월 지출 한도** 설정(공개 중 LLM 비용 상한) | 한도 금액(값 아님) 설정됨 |
| 0-5 | **도메인 구입**(결정 B) — 등록기관의 DNS 관리 화면에 들어갈 수 있는지 확인. 구입이 늦으면 9단계에서 sslip.io 로 먼저 띄운다 | 도메인 이름 `<도메인>` (메인 세션에 알려 11·12 문서 자리표를 채운다) |

## 1. 리전·키 페어·보안 그룹
| # | 할 것 | 끝났다는 증거 |
|---|------|------------|
| 1-1 | 콘솔 우상단 리전 **아시아 태평양(서울) ap-northeast-2** | 리전 표시 |
| 1-2 | EC2 → 키 페어 → **ed25519**, `.pem` 다운로드 → 사용자 PC 에만 `chmod 600` | 키 페어 이름(값 아님), 로컬 파일 권한 `-rw-------` |
| 1-3 | EC2 → 보안 그룹 생성: 인바운드 **80 TCP `0.0.0.0/0`·`::/0`** · **443 TCP `0.0.0.0/0`·`::/0`** · **22 TCP "내 IP"/32** 만. **5432·8000 규칙 없음.** 아웃바운드 기본(전체) | 규칙 3개(80·443·22) |

> 발표 장소에서 공인 IP 가 바뀌면 22 규칙의 "내 IP" 를 콘솔에서 고친다(SSH 만 영향, 사이트는 영향 없음).

## 2. EC2 생성 · Elastic IP
| # | 할 것 | 끝났다는 증거 |
|---|------|------------|
| 2-1 | 인스턴스 시작: **Ubuntu Server 24.04 LTS (arm64)** AMI · **t4g.small** · 위 키 페어 · 위 보안 그룹 · 기본 VPC 퍼블릭 서브넷 · 퍼블릭 IP 자동 할당 켜기 · 스토리지 **gp3 20GiB**, "종료 시 삭제" 체크 유지 | 인스턴스 `running`, 상태 검사 2/2 |
| 2-2 | **Elastic IP** 할당 → 인스턴스에 연결(호스트명이 IP 에 묶이므로 필수) | EIP 연결됨. 메모: EIP `___.___.___.___`(IP 는 비밀이 아니다) |

## 3. 서버 준비 (SSH)
```
ssh -i <키.pem> ubuntu@<EIP>
```
| # | 할 것 | 끝났다는 증거 |
|---|------|------------|
| 3-1 | `sudo apt-get update && sudo apt-get upgrade -y` | 오류 없음 |
| 3-2 | **Docker 공식 apt 저장소 방식**으로 설치(`curl … \| sh` 금지 — security §3): Docker 문서 "Install using the apt repository" 의 명령을 그대로 — `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` | `docker --version`, `docker compose version` 출력 |
| 3-3 | `sudo usermod -aG docker ubuntu` → 재접속 → `docker ps` 가 sudo 없이 됨 · `systemctl is-enabled docker` = `enabled` | 두 출력 |
| 3-4 | `git clone https://github.com/SunWoo1213/Relationship.git && cd Relationship` → **배포 커밋으로** `git checkout <해시>`(메인 세션이 알려 준다 — P9 04-review 대상 커밋) | `git rev-parse --short HEAD` = 그 해시 |

## 4. `.env` 작성 (서버에서 사용자가 직접, 값은 이 파일에만)
```
nano .env && chmod 600 .env
```
이름만 적는다. **값은 어디에도 복사하지 않는다.**

| 이름 | 값을 어디서 | 비고 |
|------|-----------|------|
| `POSTGRES_USER` | 임의(예: `app`) | compose 가 DB 컨테이너와 백엔드 둘에 준다 |
| `POSTGRES_PASSWORD` | 서버에서 `openssl rand -hex 24` 로 생성 | URL 에 넣지 않는다 — 백엔드는 이 변수로 비밀번호를 채운다(결정 O). **첫 기동 뒤에는 바꾸지 않는다** — Postgres 컨테이너는 볼륨이 초기화된 뒤의 값 변경을 무시하므로 backend 만 접속에 실패한다 |
| `POSTGRES_DB` | `relationship` | |
| `SITE_ADDRESS` | 9단계 호스트명(예: `demo.<도메인>` 또는 `3-35-10-20.sslip.io`) | Caddy 가 이 이름으로 인증서를 받는다. 포트·`https://` 없이 이름만 |
| `OPENAI_API_KEY` | OpenAI 대시보드(**배포용 새 키** 권장 — 종료 때 폐기) | LLM 판정·임베딩(D4·D11). **없으면 브리핑 1분 루프가 매분 Traceback 만 남기고 `briefing_run` 기록이 안 생긴다**(U1 스모크 발견) — 기동 전에 꼭 넣는다 |
| `OPENAI_MODEL` | 로컬 `.env` 와 같은 값 | |
| `LLM_PROVIDER` / `LLM_PROVIDERS_ENABLED` | `openai` / `openai` | 결정 K — 공급자 하나만 |
| `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `VAPID_SUBJECT` | **배포용 새 키 쌍**(결정 N): 사용자 PC 터미널에서 `docs/RUNNING.md` "① VAPID 키는 사용자가 직접 만든다"(273행 근처)의 명령을 **그대로 한 번** 실행해 나온 두 줄을 쓴다(에이전트는 실행하지 않는다 — 값이 대화 기록에 남는다) · `VAPID_SUBJECT=mailto:<내 메일>` | 값은 화면과 이 파일에만. 로컬 `.env` 의 키와 다른 쌍이어야 종료 때 로컬 구독이 살아남는다 |
| `APP_USER_ID` | `demo` | 로컬 `local` 과 구분. 평가 직전 기억 초기화는 14단계 |
| `APP_TIMEZONE` | 비움(기본 Asia/Seoul) | |
| `BRIEFING_SCHEDULER_ENABLED` | `1` | 컨테이너 안 1분 브리핑 루프(D17 3) |

**넣지 않는 것**: `DATABASE_URL`(compose 가 덮어쓴다 — 넣어도 무시되지만 혼동 방지) · `PUSH_DEV_PAGE_ENABLED`(결정 K — 확인 페이지는 공개 URL 에 두지 않는다) · `POSTGRES_PORT`·`POSTGRES_HOST` · Anthropic·Gemini 키.
끝났다는 증거: `ls -l .env` 권한 `-rw-------`, `grep -c '^[A-Z_]*=' .env` 가 **14**(표의 이름 수 — `APP_TIMEZONE=` 처럼 값이 빈 줄도 센다).

## 5. 호스트명 (결정 B)
| 경우 | 할 것 | 끝났다는 증거 |
|------|------|------------|
| 도메인 준비됨 | 등록기관 DNS 에 **A 레코드** `demo`(또는 `@`) → EIP, TTL 300 | `dig +short <호스트명>` = EIP |
| 아직이면 | `SITE_ADDRESS=<EIP 를 대시로>.sslip.io`(예 `3-35-10-20.sslip.io`) 로 먼저 띄운다. 도메인이 준비되면 `.env` 의 `SITE_ADDRESS` 만 바꾸고 6단계 명령 재실행 | `dig +short <호스트명>` = EIP |

> sslip.io 는 인증서 발급 한도를 다른 사용자와 나눠 써서 Let's Encrypt 가 거절할 수 있다. 거절되면 `logs caddy` 에 발급 오류가 찍힌다 → `nip.io` 로 같은 방식으로 바꾼다. (Caddy 의 ZeroSSL 대체 발급은 **이메일을 설정했을 때만** 기본 활성이라 지금 Caddyfile 로는 자동으로 돌지 않는다 — 필요하면 Caddyfile 전역 옵션 `email` 추가를 기동 전에 정한다, R-U1-5.)

## 6. 기동
```
cd ~/Relationship
GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100 caddy
docker compose -f docker-compose.prod.yml logs --tail=200 backend
```
끝났다는 증거: `ps` 에 `caddy`·`backend`·`postgres` 셋이 `running`(backend·postgres `healthy`) · caddy 로그에 인증서 발급 성공(`certificate obtained successfully` 류) · backend 로그에 `alembic` 마이그레이션 줄 뒤 `Application startup complete`, `Traceback` 0.
첫 빌드는 프론트 `npm ci` 포함 수 분 걸린다(t4g.small). 실패하면 `logs` 를 메인 세션에 붙여 준다(비밀 값이 찍히지 않는지 먼저 본다).

## 7. 스모크 (판정 표 U4 행 — 에이전트가 돌리는 GET 과 사용자가 돌리는 것)
| # | 명령 | 기대 |
|---|------|------|
| S1 | `curl -sS https://<호스트명>/api/health` | `status ok`, `db up`, `alembic_revision` 가 최신 리비전 |
| S2 | `curl -sSI https://<호스트명>/` | `200`, `text/html` |
| S4 | `curl -sSI https://<호스트명>/sw.js` · `/manifest.webmanifest` | `Cache-Control: no-cache` · `application/manifest+json` |
| S10 | `curl -s -o /dev/null -w '%{http_code}' https://<호스트명>/api/docs` · `/api/openapi.json` · `/api/redoc` | 전부 `404` |
| S3 | `curl -sSI http://<호스트명>/` | `308` → https(HTTP→HTTPS 리다이렉트) |
| 사용자 | 브라우저로 `https://<호스트명>/` → 채팅 1문장 입력(`POST /chat` 은 본문이 있어 사용자 몫) → 인물 카드 → 브리핑 화면 "알림 받기" → 푸시 수신 | 데모 5단계 통과 |

## 8. 데모 5단계 (발표 직전 한 번 열어 데운다)
`README.md` "데모 시나리오 (3분)" · `SERVER-CHECKLIST.md` §5 그대로. 화면 주소는 해시 라우팅(`https://<호스트명>/#/chat` · `#/persons` · `#/briefings`, PWA `start_url` 도 `/#/chat`)이라 서버는 `/` 하나만 받는다 — Caddy 의 SPA fallback 은 보험(U2 확인). 첫 요청은 Postgres 커넥션·LLM 첫 호출로 느릴 수 있으니 발표 10분 전에 한 번 돈다.

## 9. 갱신 · 되돌리기
```
git fetch && git checkout <새 해시>
GIT_SHA=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d --build
```
마이그레이션은 entrypoint 가 자동으로 돈다. 되돌리기 = 직전 해시로 같은 명령(SERVER-CHECKLIST 0-4·§6).

## 10. 평가 직전 기억 초기화가 필요하면
`.env` 의 `APP_USER_ID` 를 새 값(예 `demo2`)으로 바꾸고 `up -d` — 빈 기억으로 시작한다. `DROP`·`TRUNCATE`·`down -v` 는 쓰지 않는다(security §4). 주의: 모든 방문자가 같은 기억을 공유한다(F-fbaaae, 단일 사용자 데모).

## 11. 로그 · 비상시
- 로그는 `docker compose -f docker-compose.prod.yml logs --tail=200 <서비스>` 만(결정 L — 서비스당 10MB×3 상한, 외부 전송 없음).
- 서버가 응답하지 않으면 발표는 **로컬 실행**(`docs/RUNNING.md`)으로 한다. 발표 전날 저녁 7단계 S1·S2 를 한 번 더 돈다.

## 끝났다는 증거 (04-review 가 본다)
`https://<호스트명>/api/health` 200 · S10 404 ×3 · 데모 5단계 사용자 확인 · `docker compose ps` 세 서비스 healthy · `.env` 권한 600 · 보안 그룹 규칙 3개 · Budgets 3개 — 전부 **이름·상태만** 03-log 에 적는다.
