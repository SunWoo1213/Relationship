# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-28 18:10 — **브랜치 점검**: dev2 pull 오류 원인 = 로컬 dev2 추적 설정 없음 → 설정함, 로컬 dev2 를 `80c2842` 로 맞춤. 다음 = 이 커밋 뒤 사용자가 dev2 로 공유 푸시, 그다음 P6-memory U1 위임 승인. (이전: 17:45 — **사용자 요청으로 멈춤.** FIX-007 커밋 `80c2842`. 다음 세션 첫 일 = P6-memory U1 위임 승인. 커밋 안 된 것은 HANDOFF·journal 자동 줄뿐(다음 커밋에 포함). 사용자 몫 추가: backend-agent 가 5439 에 띄웠다 내린 임시 테스트 DB 의 도커 볼륨이 남아 있다(필요 없으면 직접 정리). (이전: 15:20 — **세션 재개(`/devlog resume`). 사용자 결정: 옛 열린 소견부터 정리 → 그다음 U1.** 옛 소견 11건 중 8건은 이미 반영돼 있어 상태만 '해소'(근거 `fixes/evidence/20260928-1510-old-findings-recheck.txt`), 남은 3건(F-46f1eb·F-036185·F-c7078e)은 FIX-007 로 묶어 승인받음. P6-memory 는 active 그대로, U1 미착수.

active: **P6-memory** (FIX-007 병행) | frozen: none | 브랜치 `dev` | main = `1e4afb4`, dev = `80c2842`(origin/dev 와 같음) · dev2 = `80c2842`(로컬이 origin/dev2 추적) | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 이번 세션에서 끝난 것
- P5-loop 완료(verifier 04-review, 1474 passed) → README 최신화 → 실서버·실 AI 왕복 확인(판정 표 8행 통과) → main 승격. main 에 GitHub PR #1 병합 커밋이 있어 내용 무변경 병합 `36766c1` 로 맞췄다.
- FIX-005 `1f07429`·`16b19a5`: 사용자 시간대 `APP_TIMEZONE`(기본 Asia/Seoul). 실서버에서 "어제 저녁" → KST 24일 19:00. main 승격함.
- FIX-006 `1e4afb4`(main 승격함): pytest 는 항상 `relationship_test` 에 붙는다(`tests/conftest.py`·`tests/db_bootstrap.py`, 없으면 만들고 마이그레이션, 개발 DB 이름과 같으면 거부). CI 의 개발 DB 마이그레이션 단계 제거. 1486 passed, 격리 증명 통과.

## 바로 다음에 할 것
1. (완료) 옛 소견 정리 `aa91f34` · FIX-007 `80c2842`(1488 passed skip 0) — 열린 소견 0.
2. **P6-memory U1**(골격: 설정 상수 6개 중 환경변수 3개 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`, `.env.example` 3줄, `app/memory/{__init__,types}.py`) → backend-agent(L-004 승인 먼저). 이후 U2~U8, 단위마다 `/commit`.
3. 이월: R-10(U6 추출기 지연 생성), R-15(U5 결정 F 스키마 `min_events`). 그다음 `P6-briefing`(패턴 문장화·브리핑 직전 패턴 재계산). 이후 P9 AWS(Terraform).
- 발견: 지금 루프가 `pattern:` 키 사실을 막지 않는다 → U3 가 막는다.

## 사용자 몫 (알려 둔 것)
- **브랜치 역할(2026-09-28, 사용자 결정)**: main = 최종 완성, dev = 백업(작업·승인 푸시는 여전히 dev, L-001·L-003 그대로), dev2 = 다른 기기끼리 현재 상태 공유. 훅은 고치지 않았다 — dev2 푸시는 사용자가 `!git push origin dev:dev2` 로 직접. 로컬 dev2 는 origin/dev2 추적 설정함(`git pull` 가능). 주의: GitHub Desktop 에서 브랜치를 바꾸면 커밋 안 된 변경이 stash(`!!GitHub_Desktop<dev>`)로 들어간다 — 사라진 것처럼 보이면 `git stash list`.
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
