# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-29 08:20 — **세션 인계용 정리(사용자 요청).** 지금 자리: **FIX-013 계획 3차본을 막 완성했고, 아직 검증받지 않았다.** 2차까지 모두 verifier 보류였다. 3차에서 바뀐 핵심: 수정 방식이 "`exit` 네 곳 삭제" 에서 **"세 `if` 를 `if/elif/elif` 사슬로 합치기"** 로 바뀌었다 — 지금 갈래의 배타를 만드는 것이 바로 그 `exit` 들이라, 지우기만 하면 한 명령이 여러 갈래를 타서 새 결함이 생긴다(verifier 격리 실험으로 확인). **다음에 할 일: 3차본을 verifier 에 재검증(L-004 승인 먼저) → 통과하면 사용자 승인 → 구현.** 구현 전에 검출력 확인 A·B·C 를 먼저 한다(FIX-013 회귀 표). 커밋은 훅+시험+문서 한 덩어리. (이전: 07:40 — 2차본 재검증 위임.)











active: **P6-memory** | frozen: none | 브랜치 `dev2`(작업·실험) | main = `1e4afb4` · origin/dev = `e48ac4c` · origin/dev2 = `0c46913`(최신, 여기서 작업) | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 이 세션(2026-09-28~29)에서 한 것 — 새 세션이 맥락을 잡는 줄거리

기기를 **Windows → Mac** 으로 옮긴 뒤 하네스가 조용히 망가져 있었고, 그것을 찾아 고치는 데 세션의 절반을 썼다. 순서대로:

1. **FIX-008 `c4285ed`** — 훅 9개가 stdin 을 `python` 으로 파싱하는데 macOS 에는 그 이름이 없었다. **차단형 가드 5종이 전부 조용히 열려 있었다.** `_py.sh` 탐지 신설(`python`→`python3`, 실제 실행해 확인), 못 찾으면 통과가 아니라 **차단**.
2. **FIX-010 `3c0f0d9`** — 브랜치를 사용자 의도대로 3단계로 재편(dev2 실험 → dev 검증 → main 배포). 곁들여 `test-guards.sh` 가 실패 50건이던 것을 0으로(시험 경로가 `C:\Capstone2\` 로 박혀 Mac 에서 검사가 **아무것도 안 하고 통과**하고 있었다).
3. **FIX-011 `217e523` + `cd09a60`** — 사용자가 "계획→계획검증→구현→구현검증 훅이 도는지" 물어 점검했더니 **구현 검증만 망가져 있었다**: 테스트를 한 건도 안 돌리고 WARN 으로 통과, DB 미연결 255건 skip 인데 PASS. 실패 방향을 통과에서 차단으로 뒤집었다. 사각지대였던 `commit-cleanup`·`precompact` 시험 12건도 추가.
4. **FIX-012 `0c46913`** — DB 기본 포트를 5433 으로(두 기기 모두 5433). 이제 환경변수 없이도 `1524 passed skip 0`.
5. **제품**: P6-memory **U1 `7564c5d`**(설정 상수·타입 골격) · **U2 `d67d084`**(패턴 감지 규칙 — LLM 없이 `pattern:{type}` 사실 생성·갱신·삭제).
6. **FIX-013(진행 중)** — 위 4번 커밋을 내가 `commit && push` 로 묶어 실행하다 **커밋 후처리가 통째로 건너뛰는** 새 결함을 발견했다.

## 옛 세션에서 끝난 것 (상세는 journal·04-review)
- **P5-loop 완료** → main 승격(1474 passed, 실서버 왕복 확인). **FIX-005** 사용자 시간대 `APP_TIMEZONE`(기본 서울). **FIX-006** pytest 는 항상 테스트 전용 DB `relationship_test` 에만 붙는다. 셋 다 main 에 올라가 있다(main = `1e4afb4`).

## 바로 다음에 할 것
1. (완료 `7564c5d`) **P6-memory U1**(골격: 설정 상수 6개 중 환경변수 3개 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`, `.env.example` 3줄, `app/memory/{__init__,types}.py`, 상수 테스트) — backend-agent 위임함(2026-09-28 23:10, L-004 마커 생성). **돌아오면 메인 세션이 `POSTGRES_PORT=5433 pytest tests/test_memory_patterns.py -k constants -v`·`python -c "import app.memory"`·`grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example`(3건)을 직접 재실행해 확인한 뒤 `/commit` 승인.** 증거는 `packages/P6-memory/evidence/*-u1-skeleton.txt`.
2. (완료 `c4285ed`) **FIX-008** 훅 인터프리터 탐지. 남은 확인 하나: 다음 세션 시작 로그에서 `(source: unknown)` 이 사라지는지 보고 FIX-008 `## 결과` 검증 4번에 적는다.
3. (완료 `3c0f0d9`, dev2 푸시됨) **브랜치 3단계 전환 FIX-010** — 실험 `git push origin dev2`(마커 없음) → 검증 승격 `git push origin dev2:dev`(승인 마커 + L-003 대기) → 배포 `git push origin dev:main`. `origin dev` 직접 푸시는 거부.
4. (완료 `217e523`·`cd09a60`) **FIX-011 구현 검증 복구 + 훅 시험 12건**. (완료 `0c46913`) **FIX-012 DB 기본 포트 5433**. **사용자 몫: Windows 기기 확인 5가지**(아래 "사용자 몫" 절).
5. **(3차본 검증 대기) FIX-013** — 커밋+푸시 복합 명령에서 커밋 후처리가 건너뛰는 결함(`0c46913` 에서 실제 발생). 계획 `fixes/FIX-013.md` 의 **개정 이력 절부터 읽으면** 1·2차에서 무엇이 틀렸는지 알 수 있다. 3차본 요지: 푸시 갈래 세 개를 `if/elif/elif` 로 합치고 `exit` 를 없애 커밋 처리로 잇는다 · 복합 명령 시험 6건(전제에 ref 재동기화·`.awaiting-decision` 초기화 포함) · 검출력 확인 A·B·C 를 **고치기 전에** 수행 · `SKILL.md` §5~§6 에 "푸시는 별도 Bash 호출" 문장.
6. (완료 `d67d084`) **P6-memory U2 패턴 감지 규칙**. 다음은 **U3**(`pattern:` 접두 키 보호) → U4(추출기) → U5(승격) → U6(루프 연결) → U7(직접 사실 링크) → U8(기계 검증). 단위마다 L-004 위임 승인·`/commit`.
7. 이월: R-10(U6 추출기 지연 생성), R-15(U5 결정 F 스키마 `min_events`). 그다음 `P6-briefing`(패턴 문장화·브리핑 직전 패턴 재계산). 이후 P9 AWS(Terraform).
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
- **커밋과 푸시는 반드시 따로 실행한다**(FIX-013). 한 명령에 묶으면 `commit-cleanup` 이 푸시만 처리하고 끝나 마커가 남고 journal 줄이 빠진다. 푸시·승격은 단독 Bash 호출, 승인 마커 먼저. dev 푸시 뒤 `.awaiting-decision` 이 새 커밋을 막는다 → 사용자 결정 후 `--decision fix` 또는 `--release`.
- `app/` docstring 에 "evaluation" 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지.
