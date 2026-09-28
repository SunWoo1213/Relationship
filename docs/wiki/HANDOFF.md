# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-29 03:00 — **브랜치를 세 단계로 다시 짰다(FIX-010, 커밋 대기).** 사용자가 원한 구조는 `dev2`=실험(아무때나 푸시) → `dev`=검증 통과분(승인 필요) → `main`=배포였고, FIX-009 가 만든 `dev→dev2` 복사는 방향이 반대였다. 훅·스킬·문서 10개를 고쳤고 `origin dev` 직접 푸시는 이제 거부된다. **곁들여 `test-guards.sh` 가 이 기기에서 실패 50건이던 것을 0건으로 만들었다** — `python` 이름(FIX-008 과 같은 뿌리)과 `C:\Capstone2\` 로 박힌 시험 경로 때문에 stage-gate 케이스들이 조용히 통과하고 있었다. 제품 회귀 1511 passed. **다음: 이 변경 커밋 → 로컬 dev2 로 이주 → `git push origin dev2`.** (이전: 01:50 — FIX-009 커밋 `2e293c8`, dev2 푸시 성공.)




active: **P6-memory** | frozen: none | 브랜치 `dev2`(작업·실험) | main = `1e4afb4` · origin/dev = `e48ac4c` · origin/dev2 = `2e293c8`(최신, 여기서 작업) | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 이번 세션에서 끝난 것
- P5-loop 완료(verifier 04-review, 1474 passed) → README 최신화 → 실서버·실 AI 왕복 확인(판정 표 8행 통과) → main 승격. main 에 GitHub PR #1 병합 커밋이 있어 내용 무변경 병합 `36766c1` 로 맞췄다.
- FIX-005 `1f07429`·`16b19a5`: 사용자 시간대 `APP_TIMEZONE`(기본 Asia/Seoul). 실서버에서 "어제 저녁" → KST 24일 19:00. main 승격함.
- FIX-006 `1e4afb4`(main 승격함): pytest 는 항상 `relationship_test` 에 붙는다(`tests/conftest.py`·`tests/db_bootstrap.py`, 없으면 만들고 마이그레이션, 개발 DB 이름과 같으면 거부). CI 의 개발 DB 마이그레이션 단계 제거. 1486 passed, 격리 증명 통과.

## 바로 다음에 할 것
1. (완료 `7564c5d`) **P6-memory U1**(골격: 설정 상수 6개 중 환경변수 3개 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`, `.env.example` 3줄, `app/memory/{__init__,types}.py`, 상수 테스트) — backend-agent 위임함(2026-09-28 23:10, L-004 마커 생성). **돌아오면 메인 세션이 `POSTGRES_PORT=5433 pytest tests/test_memory_patterns.py -k constants -v`·`python -c "import app.memory"`·`grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example`(3건)을 직접 재실행해 확인한 뒤 `/commit` 승인.** 증거는 `packages/P6-memory/evidence/*-u1-skeleton.txt`.
2. (완료 `c4285ed`) **FIX-008** 훅 인터프리터 탐지. 남은 확인 하나: 다음 세션 시작 로그에서 `(source: unknown)` 이 사라지는지 보고 FIX-008 `## 결과` 검증 4번에 적는다.
3. (구현·검증 끝·커밋 대기) **브랜치 3단계 전환 FIX-010** — 실험 `git push origin dev2`(마커 없음) → 검증 승격 `git push origin dev2:dev`(승인 마커 + L-003 대기) → 배포 `git push origin dev:main`. `origin dev` 직접 푸시는 거부. 커밋 뒤 `git checkout dev2 && git merge --ff-only dev` 로 이주하고 `git push origin dev2`.
4. 해소됨: 보류였던 `test-guards.sh` 옛 경로 문제를 FIX-010 에서 닫았다(실패 50 → 0). 남은 곁가지: `safety-guard` 가 `git config --get-all` 같은 읽기 전용 조회까지 막는다.
5. 이후 P6-memory U2(패턴 규칙) → U3(`pattern:` 키 보호) → U4(추출기) → U5(승격) → U6(루프 연결) → U7(직접 사실 링크) → U8(기계 검증). 단위마다 위임 승인·`/commit`.
6. 이월: R-10(U6 추출기 지연 생성), R-15(U5 결정 F 스키마 `min_events`). 그다음 `P6-briefing`(패턴 문장화·브리핑 직전 패턴 재계산). 이후 P9 AWS(Terraform).
- 발견: 지금 루프가 `pattern:` 키 사실을 막지 않는다 → U3 가 막는다.

## 사용자 몫 (알려 둔 것)
- **브랜치 역할(2026-09-29 확정, FIX-010)**: `dev2` = 작업·실험(아무때나 `git push origin dev2`) → `dev` = 검증을 통과한 것(`/commit` 승인 뒤 `git push origin dev2:dev`, 그 뒤 L-003 대기) → `main` = 배포(`/commit release`). `origin dev` 직접 푸시는 훅이 막는다. **다른 기기에서는 `origin/dev2` 를 받아 그 위에서 바로 작업한다**(`git checkout dev2 && git pull --ff-only`). 이 맥의 GitHub 로그인은 사용자가 `gh auth login` + `gh auth setup-git` 으로 끝냈다(`SunWoo1213`) — **새 기기마다 이 두 명령이 필요하다.** 주의: GitHub Desktop 에서 브랜치를 바꾸면 커밋 안 된 변경이 stash(`!!GitHub_Desktop<dev>`)로 들어간다 — 사라진 것처럼 보이면 `git stash list`.
- 환경 파일 15행에 공백이 섞인 값이 있다(`2.5: command not found`). `LLM_PROVIDER=openai`(하나만)·`LLM_PROVIDERS_ENABLED=`(비우면 셋 다 허용)·`OPENAI_MODEL=gpt-4o-mini` 로 정리하라고 안내했다. `DATABASE_URL` 이 5432(다른 프로젝트)를 가리켜 서버 기동 때 `unset DATABASE_URL` 이 필요했다.
- 빈 DB `relationship_test_fix006_evidence` 정리(훅이 셸의 DB 삭제를 막음). GitHub main 브랜치 보호 규칙. 테스트 서버(8000)가 켜져 있으면 종료.

## 열린 질문 · 보류
- 보류 목록: R-19(`verify-plan.sh` 7절 정규식) · ~~`test-guards.sh` 옛 경로~~(FIX-010 에서 해소) · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · 하네스 부채(verify-plan 토큰 스캔 오탐, findings.py 빈 표 중복, verify-impl 이 05 머리말 메모를 지우는 문제).
- P9 전: 다중 사용자 격리 부채(F-fbaaae). 개발 DB 에 확인용 행(`judge-row7-*`·`verifier-row7-*`·`row8-check-23175`·`fix005-recheck`)이 남아 있다. 지우지 않는다.

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다.
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인.
- 실서버 확인은 사용자가 `!` 로 기동한다(환경 파일은 훅이 막음). 이 세션에서 쓴 명령: `set -a; . ./.env; set +a; unset DATABASE_URL; APP_USER_ID=<확인용 이름> POSTGRES_PORT=5433 nohup python -m uvicorn app.main:app --port 8000 > <scratchpad>/uvicorn.log 2>&1 &`. 한국어 본문은 UTF-8 파일로 `--data-binary @file` 전송(인자로 주면 400).
- 푸시·승격은 단독 Bash 호출, 승인 마커 먼저. dev 푸시 뒤 `.awaiting-decision` 이 새 커밋을 막는다 → 사용자 결정 후 `--decision fix` 또는 `--release`.
- `app/` docstring 에 "evaluation" 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지.
