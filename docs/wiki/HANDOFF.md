# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-26 01:20 — **세션 종료 지점. P5-loop 완료·main 승격, FIX-005(시간대)·FIX-006(테스트 전용 DB) 완료.** FIX-006 커밋 승인 대기(이 문서가 그 커밋에 포함). 새 작업은 없다.

active: **none** | frozen: none | 브랜치 `dev` | main = dev = `16b19a5`(FIX-006 커밋 전) | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 이번 세션에서 끝난 것
- P5-loop 완료(verifier 04-review, 1474 passed) → README 최신화 → 실서버·실 AI 왕복 확인(판정 표 8행 통과) → main 승격. main 에 GitHub PR #1 병합 커밋이 있어 내용 무변경 병합 `36766c1` 로 맞췄다.
- FIX-005 `1f07429`·`16b19a5`: 사용자 시간대 `APP_TIMEZONE`(기본 Asia/Seoul). 실서버에서 "어제 저녁" → KST 24일 19:00. main 승격함.
- FIX-006(커밋 대기): pytest 는 항상 `relationship_test` 에 붙는다(`tests/conftest.py`·`tests/db_bootstrap.py`, 없으면 만들고 마이그레이션, 개발 DB 이름과 같으면 거부). CI 의 개발 DB 마이그레이션 단계 제거. 1486 passed, 격리 증명 통과.

## 바로 다음에 할 것
1. (커밋 승인 뒤) FIX-006 푸시 여부 → L-003 승격 결정.
2. 다음 패키지 **P6**(메모리 승격·패턴 감지 90일 3회 / 브리핑 생성·주기 작업) — `/devlog start`, architect 위임은 L-004 승인 먼저. backlog P6 두 항목.
3. **사용자 요청(2026-09-26): AWS 배포는 Terraform 으로.** backlog P9-infra(Terraform + GitHub Actions + Caddy, 의존 P8, infra-agent 신설)와 일치한다. P9 착수 전 `docs/user-setup/09-aws-deploy.md` §2 결정 10개. RDS 계정 CREATEDB 권한(FIX-006 테스트 경로)도 확인한다.

## 사용자 몫 (알려 둔 것)
- 환경 파일 15행에 공백이 섞인 값이 있다(`2.5: command not found`). `LLM_PROVIDER=openai`(하나만)·`LLM_PROVIDERS_ENABLED=`(비우면 셋 다 허용)·`OPENAI_MODEL=gpt-4o-mini` 로 정리하라고 안내했다. `DATABASE_URL` 이 5432(다른 프로젝트)를 가리켜 서버 기동 때 `unset DATABASE_URL` 이 필요했다.
- 빈 DB `relationship_test_fix006_evidence` 정리(훅이 셸의 DB 삭제를 막음). GitHub main 브랜치 보호 규칙. 테스트 서버(8000)가 켜져 있으면 종료.

## 열린 질문 · 보류
- 보류 목록: R-19(`verify-plan.sh` 7절 정규식) · `test-guards.sh` 옛 경로 · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · 하네스 부채(verify-plan 토큰 스캔 오탐, findings.py 빈 표 중복, verify-impl 이 05 머리말 메모를 지우는 문제).
- P9 전: 다중 사용자 격리 부채(F-fbaaae). 개발 DB 에 확인용 행(`judge-row7-*`·`verifier-row7-*`·`row8-check-23175`·`fix005-recheck`)이 남아 있다. 지우지 않는다.

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다.
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인.
- 실서버 확인은 사용자가 `!` 로 기동한다(환경 파일은 훅이 막음). 이 세션에서 쓴 명령: `set -a; . ./.env; set +a; unset DATABASE_URL; APP_USER_ID=<확인용 이름> POSTGRES_PORT=5433 nohup python -m uvicorn app.main:app --port 8000 > <scratchpad>/uvicorn.log 2>&1 &`. 한국어 본문은 UTF-8 파일로 `--data-binary @file` 전송(인자로 주면 400).
- 푸시·승격은 단독 Bash 호출, 승인 마커 먼저. dev 푸시 뒤 `.awaiting-decision` 이 새 커밋을 막는다 → 사용자 결정 후 `--decision fix` 또는 `--release`.
- `app/` docstring 에 "evaluation" 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지.
