# P9-infra · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-11-14 · docs(P9-infra): AWS 최소 구성 배포 계획을 검증까지 마치고 활성화한다 · pending
- 변경: `01-plan.md`(architect — 1차 Vercel 안을 같은 날 폐기하고 AWS 최소 안으로 재작성; 결정 A~P 확정) · `02-plan-verify.md`(verifier — 1차 보류 F-P9V-1 → 보정 → 재검증) · evidence `verify-plan`(1359 FAIL 2 → 1401 FAIL 1 → 1415 FAIL 0/WARN 8 오탐) · `CURRENT.md active` · 이 로그 · journal START.
- 이유(기획서·카드 연결): CR-005 개정 ② · D17. 사용자 결정(2026-11-14): A t4g.small + gp3 20GB · B 새로 구입하는 도메인(준비 전 `<EIP>.sslip.io`) · D SSH 22 내 IP · J 종료 11-19 18:00 KST; C 서울 · E 다단계 Dockerfile · F python:3.13-slim/node:24-slim/caddy:2-alpine/pgvector:pg16 · G 루트 파일 + `docker/entrypoint.sh` + `name: relationship-prod` · H CI 스모크 추가 · I $10/$30/$50 · K 운영 .env 스위치(OpenAI 만, `APP_USER_ID=demo`, 확인 페이지 off) · L 로그 10m×3 · M `/api/docs` 류 404 · N VAPID 새 키 · O 비밀번호 없는 `DATABASE_URL` + `POSTGRES_PASSWORD` · P 스모크 S1~S17 그대로 — 추천안 위임.
- verifier 1차 **보류** [필수] F-P9V-1: 계획 61행 Caddyfile 사양이 404 `respond` 를 최상위에 두어 `handle_path` 뒤에 평가됨 → `/api/docs` 가 백엔드 Swagger 200 으로 새어 나감(`caddy adapt` 로 라우트 순서 확인, evidence `20261114-1406-plan-verify-caddy-order.txt`). 보정: 404 를 `handle_path /api/*` 블록 안·`reverse_proxy` 앞·접두 없는 매처로, 테스트 ⑪ 보강, 변이 V1-14b. [권고] F-P9V-2 `save_evidence.py` 따옴표 우회(바깥 따옴표 또는 스크래치패드 .sh) · F-P9V-3 사실 6 보정(개발 프로젝트는 `capstone2`, 옛 `relationship_pgdata` 존재 → `name:` 필수) + 개발 DB 무영향 행에 `compose ls`·`volume ls` · F-P9V-4 U2 `web/public/` 변경 시 표시 · F-P9V-5 U1 분할은 선택(그대로) · F-P9V-6 CR-005 에 pg_dump 1회 구절 · F-P9V-7 `resolve_connection` 경고 미출력은 U1 메모.
- 정합성 확인: 점검표 8/8(02-plan-verify §2). 원칙 5·7 무관 · 원칙 8(제품 코드 0, 같은 커밋으로 프론트·백엔드 빌드) · 원칙 9 무관 · security §1·§4·§5 · D17 "코드에서 지켜야 할 것" 1~6 → 판정 표 대응.
- 남은 것 · 다음 단위: U1 [backend-agent] 배포 파일 5종 + `tests/test_deploy_files.py` + 로컬 compose 스모크 와 U2 [frontend-agent] 빌드 확인 **동시** → U1b CI 스모크 → U3 [메인] user-setup 11·12 → **U4 는 사용자 "띄워 달라" 뒤**.
- Refs: P9-infra CR-005 D17 R14 security 원칙8 F-P9V-1 F-P9V-2 F-P9V-3
