# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-29 06:30 — **미커밋 세 묶음, 커밋 대기.** ① 훅 시험 12건 추가(`commit-cleanup`·`precompact` 사각지대 제거, 결함 주입으로 검출력 확인) ② **FIX-012 DB 기본 포트 5433** — 두 기기 모두 5433 이라 기본값을 맞췄다. 이제 **환경변수 없이도 `1524 passed skip 0`**(고치기 전 `1215 passed 309 skipped`). ③ `.env.example` 포트(사용자 수정). **환경 파일을 코드가 읽게 할 것인가는 A안 유지로 결정**했고 근거·검토 과정을 FIX-012 와 CANDIDATES C-8 에 남겼다 — 테스트 3개가 `app.main` 을 import 해서 진입점 분리 없이는 "테스트는 안 읽는다" 가 성립하지 않는다는 점이 결정적이었다. P9 에서 재검토. (이전: 06:10 — 미커밋 세 묶음 정리.)









active: **P6-memory** | frozen: none | 브랜치 `dev2`(작업·실험) | main = `1e4afb4` · origin/dev = `e48ac4c` · origin/dev2 = `d67d084`(최신, 여기서 작업) | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 이번 세션에서 끝난 것
- P5-loop 완료(verifier 04-review, 1474 passed) → README 최신화 → 실서버·실 AI 왕복 확인(판정 표 8행 통과) → main 승격. main 에 GitHub PR #1 병합 커밋이 있어 내용 무변경 병합 `36766c1` 로 맞췄다.
- FIX-005 `1f07429`·`16b19a5`: 사용자 시간대 `APP_TIMEZONE`(기본 Asia/Seoul). 실서버에서 "어제 저녁" → KST 24일 19:00. main 승격함.
- FIX-006 `1e4afb4`(main 승격함): pytest 는 항상 `relationship_test` 에 붙는다(`tests/conftest.py`·`tests/db_bootstrap.py`, 없으면 만들고 마이그레이션, 개발 DB 이름과 같으면 거부). CI 의 개발 DB 마이그레이션 단계 제거. 1486 passed, 격리 증명 통과.

## 바로 다음에 할 것
1. (완료 `7564c5d`) **P6-memory U1**(골격: 설정 상수 6개 중 환경변수 3개 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`, `.env.example` 3줄, `app/memory/{__init__,types}.py`, 상수 테스트) — backend-agent 위임함(2026-09-28 23:10, L-004 마커 생성). **돌아오면 메인 세션이 `POSTGRES_PORT=5433 pytest tests/test_memory_patterns.py -k constants -v`·`python -c "import app.memory"`·`grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example`(3건)을 직접 재실행해 확인한 뒤 `/commit` 승인.** 증거는 `packages/P6-memory/evidence/*-u1-skeleton.txt`.
2. (완료 `c4285ed`) **FIX-008** 훅 인터프리터 탐지. 남은 확인 하나: 다음 세션 시작 로그에서 `(source: unknown)` 이 사라지는지 보고 FIX-008 `## 결과` 검증 4번에 적는다.
3. (완료 `3c0f0d9`, dev2 푸시됨) **브랜치 3단계 전환 FIX-010** — 실험 `git push origin dev2`(마커 없음) → 검증 승격 `git push origin dev2:dev`(승인 마커 + L-003 대기) → 배포 `git push origin dev:main`. `origin dev` 직접 푸시는 거부.
4. (완료 `217e523`) **FIX-011 구현 검증 복구** + 후속으로 `commit-cleanup`·`precompact` 자동 시험 12건 추가(**커밋 대기**). 이제 등록된 훅 9개가 모두 `test-guards.sh` 범위 안이다. **사용자 몫: Windows 기기 확인 5가지**(아래 "사용자 몫" 절).
5. (완료 `d67d084`) **P6-memory U2 패턴 감지 규칙**. 다음은 **U3**(`pattern:` 접두 키 보호 — 루프의 LLM 이 패턴 사실을 위조하지 못하게 `app/tools/persons.py` 에 조건 한 줄) → U4(추출기) → U5(승격) → U6(루프 연결) → U7(직접 사실 링크) → U8(기계 검증). 단위마다 L-004 위임 승인·`/commit`.
6. 이월: R-10(U6 추출기 지연 생성), R-15(U5 결정 F 스키마 `min_events`). 그다음 `P6-briefing`(패턴 문장화·브리핑 직전 패턴 재계산). 이후 P9 AWS(Terraform).
- 발견: 지금 루프가 `pattern:` 키 사실을 막지 않는다 → U3 가 막는다.

## 사용자 몫 (알려 둔 것)
- **브랜치 역할(2026-09-29 확정, FIX-010)**: `dev2` = 작업·실험(아무때나 `git push origin dev2`) → `dev` = 검증을 통과한 것(`/commit` 승인 뒤 `git push origin dev2:dev`, 그 뒤 L-003 대기) → `main` = 배포(`/commit release`). `origin dev` 직접 푸시는 훅이 막는다. **다른 기기에서는 `origin/dev2` 를 받아 그 위에서 바로 작업한다**(`git checkout dev2 && git pull --ff-only`). 이 맥의 GitHub 로그인은 사용자가 `gh auth login` + `gh auth setup-git` 으로 끝냈다(`SunWoo1213`) — **새 기기마다 이 두 명령이 필요하다.** 주의: GitHub Desktop 에서 브랜치를 바꾸면 커밋 안 된 변경이 stash(`!!GitHub_Desktop<dev>`)로 들어간다 — 사라진 것처럼 보이면 `git stash list`.
- **[미확인] Windows 기기에서 훅·검증 스크립트를 한 번 돌려 봐야 한다** (FIX-008·FIX-010·FIX-011 은 전부 Mac 에서만 확인했다). 확인할 것: ① `bash .claude/scripts/test-guards.sh` → 실패 0 ② `set -a; . ./.env; set +a` 뒤 `bash .claude/scripts/verify-impl.sh P6-memory` → `PASS pytest 통과` ③ 훅이 `python`(Windows 표준 이름)을 골랐는지 — `bash -c '. .claude/hooks/_py.sh; echo $HOOK_PY'` ④ venv 경로가 `.venv/Scripts/python.exe` 로 잡히는지 ⑤ 커밋 한 번 해 보고 승인 마커가 자동으로 지워지는지. 하나라도 어긋나면 그 출력을 알려 주면 FIX 로 잇는다.
- 환경 파일 15행에 공백이 섞인 값이 있다(`2.5: command not found`). `LLM_PROVIDER=openai`(하나만)·`LLM_PROVIDERS_ENABLED=`(비우면 셋 다 허용)·`OPENAI_MODEL=gpt-4o-mini` 로 정리하라고 안내했다. `DATABASE_URL` 이 5432(다른 프로젝트)를 가리켜 서버 기동 때 `unset DATABASE_URL` 이 필요했다.
- 빈 DB `relationship_test_fix006_evidence` 정리(훅이 셸의 DB 삭제를 막음). GitHub main 브랜치 보호 규칙. 테스트 서버(8000)가 켜져 있으면 종료.

## 열린 질문 · 보류
- **[결정됨 2026-09-29] 환경 파일은 코드가 읽지 않는다 — A안 유지**(셸에서 `set -a; . ./.env; set +a`). 코드가 `load_dotenv` 로 읽는 안을 검토했으나, 테스트 3개가 `app.main` 을 import 해서 "앱 시작할 때만 읽는다" 가 성립하지 않는다(진입점 `app/run.py` 분리가 필요). 오늘 문제의 실제 원인은 기본값 어긋남이었고 FIX-012 로 닫혔다. **P9(AWS 배포)에서 진입점을 정리할 때 재검토** — `lessons/CANDIDATES.md` C-8, 근거는 `fixes/FIX-012.md` "검토하고 보류한 것" 절.
- 보류 목록: R-19(`verify-plan.sh` 7절 정규식) · ~~`test-guards.sh` 옛 경로~~(FIX-010 에서 해소) · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · 하네스 부채(verify-plan 토큰 스캔 오탐, findings.py 빈 표 중복, verify-impl 이 05 머리말 메모를 지우는 문제).
- P9 전: 다중 사용자 격리 부채(F-fbaaae). 개발 DB 에 확인용 행(`judge-row7-*`·`verifier-row7-*`·`row8-check-23175`·`fix005-recheck`)이 남아 있다. 지우지 않는다.

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다.
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인.
- 실서버 확인은 사용자가 `!` 로 기동한다(환경 파일은 훅이 막음). 이 세션에서 쓴 명령: `set -a; . ./.env; set +a; unset DATABASE_URL; APP_USER_ID=<확인용 이름> POSTGRES_PORT=5433 nohup python -m uvicorn app.main:app --port 8000 > <scratchpad>/uvicorn.log 2>&1 &`. 한국어 본문은 UTF-8 파일로 `--data-binary @file` 전송(인자로 주면 400).
- **환경 파일은 셸에 올려 쓴다**(A안, FIX-011·FIX-012): `set -a; . ./.env; set +a`. 값은 출력하지 않는다. DB 포트는 이제 기본값이 5433 이라 포트만 필요하면 안 올려도 되지만(FIX-012), `DATABASE_URL`·API 키가 필요한 실행은 올려야 한다. DB 에 못 붙어 건너뛴 테스트가 있으면 `verify-impl.sh` 가 FAIL 한다.
- 푸시·승격은 단독 Bash 호출, 승인 마커 먼저. dev 푸시 뒤 `.awaiting-decision` 이 새 커밋을 막는다 → 사용자 결정 후 `--decision fix` 또는 `--release`.
- `app/` docstring 에 "evaluation" 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지.
