# review-FIX-014 · 커밋 전 리뷰 — 프로젝트 안 Bash 파일 쓰기 거부 훅(`bash-write-guard`) + commit-cleanup 텍스트 매칭 수정

검토자: verifier (fable) · 2026-10-11 · 기준 HEAD `d16375e` + 작업 트리 미커밋 diff(신규 `.claude/hooks/bash-write-guard.sh`·`.claude/scripts/bash_write_check.py`, 수정 `.claude/settings.json` +7 · `.claude/hooks/commit-cleanup.sh` +13/-5 · `.claude/scripts/test-guards.sh` +83/-1 · `CLAUDE.md` 120행 · `docs/wiki/security.md` · 에이전트 정의 3개 · `docs/wiki/registry.md` 2행) · Refs: FIX-014 FIX-008 FIX-013 security.md verification.md 원칙8 원칙9

**결과: 완료 · 판정(4차 좁은 재검증 2026-10-11, 새 컨텍스트): 통과** — 3차 보류 사유 **R-14-16 한 건이 닫혔다**: 3차 V14-x 직접 재실행 + 명령 프롬프트 명시 변형(`deno run -A -`·`--allow-write`·`deno eval` stdin·`bun run -`·`bun x -`·`deno x -`·heredoc/here-string·`cat f | deno run -`) 40건 전부 deny, deno/bun 정상 사용 26건 + 작업 흐름 20건 allow(오탐 회귀 0), test-guards 실패 0(ok 328), drive2 `불일치 0`·drive `불일치 14`(번호 동일), node/ruby/perl/php stdin 코드 deny 유지, `(?:Sync)?` 1줄은 필요·무해, fail-closed deny. 유일한 deny 미달 1건(`deno run - <<EOF $(cat f)`)은 3차가 이미 올린 후속 후보 **R-14-18 의 deno 인스턴스**(동적 heredoc 본문 미검사)이고, 새로 찾은 deno/bun 옵션 표 우회(R-14-19)·`deno repl`/`bunx`(R-14-20)는 사용자 결정(2026-10-11 20:35)대로 [필수]가 아니라 후속 후보로 기록만 했다. 자세한 것은 끝의 "## 4차 검증 (2026-10-11)". `FIX-014.md` 의 `검증:` 줄을 통과로 채웠다.

(3차 판정 2026-10-11: 보류 — 지정 3건 중 R-14-12·R-14-13 은 완전히 닫혔고 오탐 회귀 0·test-guards 실패 0·fail-closed 회귀 0 이었으나, R-14-14 가 명령 프롬프트 명시 변형 `deno run -`(및 `deno eval`·`bun run -`)에서 ALLOW 로 뚫려 "지정 건 덜 닫힘"(R-14-16). "## 3차 검증 (2026-10-11)".)
(2차 재검증 판정 2026-10-11: 보류 — 1차 [필수] 4건 해소, 새 [필수] 2건(R-14-12·R-14-13)·[권고] R-14-14. "## 재검증 (2026-10-11)".)
(1차 판정 2026-10-11: 보류 — [필수] 4건(R-14-1~R-14-4), [권고] 7건(R-14-5~R-14-11). 코드·훅·계획·카드는 고치지 않았다.)

보류 요지: 계획(수정안 1~11)에 적힌 것은 전부 들어갔고 전부 동작한다 — 수정안 9 의 거부 8건·허용 6건, 보강 시험, 결함 ②, fail-closed, 검출력 증거 모두 내가 다시 실행해 확인했다(§2). 그러나 **훅이 이미 막는 형태의 "형제" 가 열려 있다**: `bash -c '…'` 는 막는데 같은 코드를 `… | bash`·`bash <<< '…'` 로 넘기면 통과하고(§4 X1·X2·X13), `bash -c "$(…)"` 는 "판정 불가 → 차단" 인데 `python3 -c "$(…)"`·`node -e "$(…)"` 는 통과하며(X3·X4), `xargs sed -i` 는 막는데 `find … -exec sed -i {} +` 는 통과한다(X5). 이들은 수정안 5 가 한계로 둔 "프로그램 실행의 부작용" 이 아니라 훅이 이미 처리하는 셸 문법의 변형이고, X3·X4 는 수정안 4·security.md("검사할 수 없으면 통과가 아니라 차단") 를 직접 어긴다. 또 수정안 11 범위인 하위 에이전트 정의 중 `verifier.md` 가 갱신되지 않아 24·32행이 지금 거부되는 명령(`| tee docs/wiki/…/evidence/…`)을 지시한다(C5 실측). 네 건을 닫고 재검증(§7)하면 통과다.

## 1. 본 것

- 문서: `docs/wiki/fixes/FIX-014.md` — 결정(2026-10-11 "프로젝트 안 Bash 쓰기 거부"), 수정안 1~11, `계획 점검: 통과`, `승인: 사용자`, 결과절(구현 완료·검증 대기·한계).
- 구현 증거: `evidence/20261011-1609-fix014-before.txt`(XX 26) · `-after.txt`(XX 0).
- diff: `git diff HEAD` 의 12 파일(`HANDOFF.md`·`journal.md` 는 대상 아님) + 신규 2 파일 전문. `settings.json` PreToolUse `Bash|PowerShell` 배열 전체(62~89행), `_py.sh`, `commit-cleanup.sh` 1~40행, `test-guards.sh` 의 격리 저장소 절(570~640행)과 보조 함수.
- 구현자 고백: `bash_write_check.py` 가 before 실행 전에 이미 존재했다 → §3.2 에서 판정.
- 열지 않은 것: 제품 코드(`app/`·`tests/`) — 이번 FIX 는 건드리지 않는다고 했고 `git status` 에도 없다.

## 2. 내가 직접 실행한 것 (수치는 전부 다시 쟀다)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `bash .claude/scripts/test-guards.sh`(Mac, 실제 저장소, 출력은 스크래치패드 리터럴 경로로) | 종료 0 · **ok 264 / XX 0 / `== 결과: 실패 0 ==`**. after 증거 본문과 diff **0줄** | `evidence/20261011-verifier-fix014-test-guards.txt`(전체 283행) |
| 2 | before/after 를 diff 하고 FIX-014 절·"No such file"·"결과: 실패" 줄을 제외 | **0줄** — FIX-014 절 밖의 기존 시험은 전부 동일하게 ok. before 의 "No such file" 36줄 = FIX-014 절 호출 수(거부 20 + 허용 15 + 대조 1). XX 26→0, ok 238→264 | `evidence/20261011-verifier-fix014-scope.txt` §4 |
| 3 | 훅을 stdin JSON 으로 직접 호출하는 드라이버 — 침입 86건 + 오탐 60건 | 침입: 수정안 9 8건·verifier 고안 40건(V1~V40) **전부 deny**, 의심 우회 18건(X1~X18) **전부 allow(뚫림)**, 한계 8건(L1~L8) 한계대로 allow. 오탐: 수정안 6 6건·작업 흐름 49건 **전부 allow**, 보수적 거부 3건(C1·C2·C3), 문서 지시 명령 거부 1건(C5) | `evidence/20261011-verifier-fix014-intrusion.txt`(표 전체) · 드라이버 원문 `…-drive-src.txt` |
| 4 | fail-closed 12건 — PATH 비움·깨진 JSON·빈 stdin·판정 스크립트 없음·import 예외·구문 오류·tool_name 없음·`HOOK_PY=`·`CLAUDE_PROJECT_DIR` 미설정·따옴표 불일치·7단 중첩 | **11건 DENY**. 유일한 allow 는 `command` 가 문자열이 아닌 123 인 경우(빈 명령 취급 — Claude Code 는 항상 문자열을 보내므로 실제 경로 아님) | `evidence/20261011-verifier-fix014-fail-closed.txt` |
| 5 | 격리 저장소(스크래치패드 `cc-iso`, `git init`)에서 `commit-cleanup.sh` 직접 호출 — 성공 판정이 우연히 맞는 상태(origin/dev2·origin/dev = HEAD, 초안 제목 = HEAD, 마커 둘) | 인자 속 글자 5건(`python3 -c "print('git push origin dev2')"`·`grep "git commit" …`·`echo "git push origin dev2:dev"`·`printf … 'git commit -F …'`·`sed -n "/git push origin dev2/p"`) → journal·마커·`.awaiting-decision` **전부 무변화**. 실제 조각 4건 → PUSH-dev2 +1·+1, COMMIT +1 + 커밋 마커 소비, PUSH +1 + 푸시 마커 소비 + 잠금 생성 | `evidence/20261011-verifier-fix014-cc-direct.txt` |
| 6 | `--git-fragments` 단독: 깨진 JSON → 출력 없음 rc 0 · `echo hi; git push origin dev2 && python3 -c "print(1)"` → `git push origin dev2` 한 줄만 | 결함 ② 공유 함수가 설계대로 | 같은 파일 끝 |
| 7 | 살아 있는 저장소 `docs/wiki/journal.md` 줄 수·마지막 줄(검증 전후) | 465줄, 마지막 줄 `15:59 PUSH-dev2 d16375e` 그대로 — 내 Bash 명령 문자열에 `git push origin dev2` 글자가 인자로 여러 번 들어갔지만 가짜 줄 없음(결함 ② 의 살아 있는 증거) | `…-scope.txt` §8 |
| 8 | `grep -rn 'tee docs/…'` .claude/·docs/wiki | `verifier.md` 24·32행, `skills/devlog/SKILL.md` 34·42행, `verification.md` 60행이 아직 `| tee docs/wiki/packages/<id>/evidence/…` 지시 → 드라이버 C5 로 거부 실측 | `…-scope.txt` §9 |
| 9 | `grep -n '\$cmd\b\|\$gitcmd' commit-cleanup.sh` | `$gitcmd` 5곳(46·63·69·77·86행), `$cmd` 참조 0곳 — 16~20행의 `cmd=` 계산은 죽은 코드 | R-14-11 |

부수 증거(이 세션의 실제 Bash 호출이 살아 있는 훅에 막힘): `… > "$SP/test-guards.txt"` → bash-write-guard deny(변수 경로) · `cp … "$T/.claude/hooks/"` → bash-write-guard deny(변수 목적지) · `ls .claude/.commit-approved` → safety-guard deny · `env |` → safety-guard deny. 앞의 둘은 수정안 4 가 실제로 집행된다는 증거이자 R-14-7 의 근거다.

## 3. 확인 항목별 판정 (위임 프롬프트 1~8)

### 3.1 범위 — diff ↔ 수정안 1~11: 일치, 안전장치를 약화하는 변경 없음
- 수정안 1: `bash-write-guard.sh`(47행, `_py.sh` 로 인터프리터 탐지 → 없으면 deny → `bash_write_check.py "$ROOT"` 호출 → rc≠0 이면 stdout 을 사유로 deny) + `settings.json` `Bash|PowerShell` PreToolUse 에 **블록 1개(+7행)** 추가, safety-guard·commit-guard 뒤 세 번째. 다른 matcher·deny/allow 목록 무변경(§2 scope §2).
- 수정안 2·3·4: `parse()`(따옴표·`;`·`&&`·`||`·`|`·줄바꿈·heredoc·`$(…)`·백틱·프로세스 치환), `WriteChecker.frag()`(리다이렉트 `>`·`>>`·`>|`·`&>`·`&>>`·`>&`, fd 복제 제외), 명령별 핸들러(tee·sed·perl·awk·cp·mv·ln·install·rsync·touch·truncate·dd·patch·ed/ex·curl·wget·python·node·ruby·vi 스크립트 모드·PowerShell 11종·.NET), `PathJudge`(임시 영역 허용·프로젝트 안 거부·변수/치환 거부·`$TMPDIR` 류 변수 허용). 수정안 2 의 목록을 넘는 핸들러(rsync·wget·patch·ed·vi·ruby·.NET)는 전부 **차단을 넓히는** 방향이다.
- 수정안 5: 한계가 훅 머리말·py docstring·CLAUDE.md·security.md·registry·FIX-014 결과절에 같은 문장으로 적혀 있다. L1~L8 실측과 일치.
- 수정안 6·9: test-guards 에 거부 20·허용 15·대조 1·파이썬 탐지 1·결함 ② 5 시험. 수정안 9 의 8건이 라벨 그대로 들어가 있다.
- 수정안 7: `commit-cleanup.sh` 는 `$cmd` 5곳을 `$gitcmd` 로 바꾼 것과 `gitcmd=` 생성 1곳이 전부. 공유 함수는 `bash_write_check.py --git-fragments`(registry 행이 "공유" 라고 적음 — 중복 구현 없음). 판정을 **좁히는** 변경만 있다.
- 수정안 8·10: before 증거 있음(§3.2). CI windows 는 푸시 뒤(§3.7).
- 수정안 11: CLAUDE.md 120행·security.md(머리말·§4b 신설·§7 가드 목록)·backend/eval/frontend 3개 ✓. **verifier.md 는 미갱신**(R-14-4).
- 범위 밖 변경: 없음. 제품 코드 무변경.

### 3.2 검출력 증거의 유효성 — 유효
before 는 "훅 파일 없음·등록 없음·옛 commit-cleanup" 상태를 실제로 반영한다: 훅 호출 36번 전부 `No such file or directory`, 거부 기대 20건 + 대조 1건 + 파이썬 탐지 1건 XX, 결함 ② 4건 XX(옛 훅이 `echo git push origin dev2` 로 가짜 줄을 남겨 "기대 4, 실제 5"). after 는 그 26건만 ok 로 바뀌고 나머지 238줄은 글자 단위 동일(§2 2). 내가 다시 돌린 결과도 after 와 동일(§2 1).

판정 스크립트가 먼저 존재한 사실은 증거를 무효로 만들지 않는다. 시험 대상은 훅 진입점(`$BW`)과 `commit-cleanup.sh` 이고, 그 둘이 없는/옛 상태는 배포 전 상태와 같다 — 스크립트 파일은 아무도 호출하지 않으면 효과가 0 이다. before 가 답하지 않는 질문("판정 스크립트가 깨졌을 때 시험이 잡는가")은 after 의 대조 시험(같은 명령이 임시 경로면 allow·프로젝트 경로면 deny)과 내 fail-closed F4~F6(스크립트 없음·예외·구문 오류 → 전부 deny)이 대신 답한다. 다만 FIX-013 교훈의 정신("고치기 전에 시험이 실패하는 것을 본다")에 비추면 판정 본체를 before 뒤에 쓰는 것이 깨끗했다 — 기록으로 남기되 소견은 내지 않는다(구현자가 before 파일 5행에 스스로 밝혔다).

### 3.3 침입 시도 — 수정안 9 8건 + verifier 40건 전부 deny; 추가 18건 뚫림
표는 `evidence/20261011-verifier-fix014-intrusion.txt`. 요약:

| 묶음 | 건수 | 결과 |
|---|---|---|
| 수정안 9 (S9-1~8) | 8 | 전부 deny — heredoc·`>`·`sed -i ''`·tee·cp·python open('w')·`"$X"`·PS Set-Content |
| 위임 프롬프트 예시 (V1~V12) | 12 | 전부 deny — `python3 - <<PY`·`bash -c`·`eval`·`cat <<EOF >`·`>> ./`·`"$CLAUDE_PROJECT_DIR/…"`·node writeFileSync·PS Out-File·`env X= sh -c '… $X'`·`dd of=`·install·`$(pwd)/…` |
| verifier 추가 (V13~V40) | 28 | 전부 deny — 절대 경로 리터럴·`: >`·명령 없는 `>`·`1>`·`exec 3>`·`{…} >`·`tee -a`·`sed -i.bak`·truncate·ln·mv·`>|`·`&>`·`sh -c "$(…)"`·`bash <<'EOF'`·`xargs sh -c`·vim -c·patch·rsync·`curl -O`·wget·shutil.copy·PS Copy-Item·PS [IO.File]·`~/x`·python 변수 경로·`open(file=…)`·`2> app/err.log` |
| **뚫림 (X1~X18)** | 18 | 전부 allow — 분류는 §6 |
| 한계 (L1~L8) | 8 | 전부 allow, 수정안 5 대로 — `os.system`·`subprocess`·`git apply`·`bash x.sh`·`python x.py`·`ruff format`·`npm run build`·`alembic revision` |

### 3.4 오탐 — 수정안 6 6건 + 작업 흐름 49건 전부 allow; 보수적 거부 3건 + 문서 지시 1건
위임 프롬프트의 9건(`git commit -F …`·`git push origin dev2`·`POSTGRES_PORT=5433 .venv/bin/python -m pytest … | tail -1`·`bash test-guards.sh > <스크래치패드>/x.txt 2>&1`·`gh run view … --json --jq`·`grep -rn … | head`·`python3 -c "print(1)"`·`curl -o <스크래치패드>/x.json`·`echo "$(date)" >> /tmp/x`) 전부 allow. 추가로 gitlog.sh·approve-commit.sh·findings.py 실행, 읽기 heredoc, `python3 - <<'PY'` 읽기, 따옴표 안 `>`, 프로세스 치환, for/[ ]/`<` 입력, `$TMPDIR`·`${TMPDIR}`·`"$TMPDIR/x"`, `/private/tmp/`, PS Get-Content·`$env:TEMP` 등 allow.
거부된 정상 명령 4건: C1 `cd /tmp && echo x > y`(cd 미추적 → 상대 경로는 프로젝트 안으로 판정; 수정안 3 "상대 경로 → 거부" 대로, 우회 = 절대 경로) · C2 `echo 'print(1)' | python3`(stdin 코드 차단, 우회 = `python3 -c`/`python3 - <<PY`) · C3 `echo x > $SP/x`(변수 → 수정안 4 대로, 우회 = 리터럴 경로) · **C5 `verify-plan.sh … | tee docs/wiki/packages/<id>/evidence/…`** — 우회는 있지만(스크래치패드 → Write) 현행 문서가 이 명령을 지시한다 → R-14-4. C1~C3 은 R-14-7(권고).

### 3.5 fail-closed — 전부 차단
파이썬 없음(PATH 비움) → `[bash-write-guard] 파이썬 인터프리터를 찾지 못해 검사할 수 없다 - FIX-008` deny. 깨진 JSON·빈 stdin → `훅 입력을 해석할 수 없어 … 차단한다` deny(rc 1). 판정 스크립트 파일 없음 → python 의 `can't open file` 이 그대로 사유가 되어 deny. import 예외·구문 오류 → Traceback 이 사유가 되어 deny. 따옴표 불일치 → ParseError deny. 7단 중첩 → MAX_DEPTH deny. `HOOK_PY=` 미리 비움·`CLAUDE_PROJECT_DIR` 미설정·`tool_name` 없음 → 정상 판정(deny). `commit-cleanup` 쪽 `--git-fragments` 는 깨진 입력에 빈 출력 rc 0(기록 누락 방향, 주석과 일치).

### 3.6 결함 ② — 인자 속 글자 무시, 실제 조각은 기존대로
test-guards 결함 ② 절 5건 ok(§2 1) + 격리 저장소 직접 9건(§2 5) + 살아 있는 journal 무변화(§2 7). `echo hi; git push origin dev2` 처럼 다른 명령 뒤에 오는 실제 git 조각도 기록된다.

### 3.7 test-guards 직접 실행 · Windows
실패 0(§2 1). Windows 형태는 코드 읽기로만 봤다: `_base()` 가 `.exe` 를 떼고 `\` 를 `/` 로 통일, PowerShell 모드에서 `os.sep=="/"` 이면 `\`→`/` 변환, `os.name=="nt"` 에서 Git Bash `/c/…` → `C:/…` 변환, `^[A-Za-z]:[\\/]` 를 절대 경로로 인식, `$env:TEMP|TMP|TMPDIR` 허용, test-guards 는 `native_path`(cygpath -m) 로 임시 경로를 만든다. **실검증은 푸시 뒤 CI windows job 의 몫이다**(수정안 10). 참고: Mac 호스트에서 PowerShell 모드로 `C:\…\Temp\x` 리터럴을 주면 `realpath("C:/…")` 가 cwd 에 붙어 오판하지만 Mac 에서 PowerShell 툴은 쓰이지 않는다.

### 3.8 문서 정합
- CLAUDE.md 120행: 허용 목록(`/tmp`·`$TMPDIR`·스크래치패드·`/dev/null`)·판정 불가 차단·한계 문장이 코드와 일치. "증거 파일도 tee 가 아니라 Write 툴로 저장한다" ✓(C5 가 그 이유).
- security.md §4b·§7: 규칙 표·한계·공유 구조 설명이 코드와 일치. §7 의 차단형 가드 목록에 `bash-write-guard` 추가 ✓(F1 실측).
- backend/eval/frontend 정의: "임시 파일은 `/tmp`·스크래치패드에만" — 코드와 일치하되 **"변수가 아니라 리터럴 절대 경로"** 라는 조건이 빠져 있어 R-14-7 의 함정이 그대로 남는다(권고).
- registry 2행: 경로·구성 요소 이름(`iter_cmds`·`WriteChecker`·`PathJudge`·`git_fragments`)이 실제 코드와 일치.
- **verifier.md 24·32행 미갱신 → R-14-4([필수]).** `skills/devlog/SKILL.md` 34·42행·`verification.md` 60행도 같은 명령을 지시한다(수정안 11 범위 밖이지만 함께 고치지 않으면 `/devlog` 절차가 매번 훅에 막힌다).

## 4. 침입·오탐 표
`evidence/20261011-verifier-fix014-intrusion.txt` 에 146행 전체(라벨·툴·기대·실제·판정·사유). 재실행 드라이버는 `…-drive-src.txt`.

## 5. 한계 기록 (수정안 5 — 소견 아님)
프로그램 실행의 부작용은 막지 않는다: L1 `os.system`·L2 `subprocess`·L3 `git apply`·L4 `bash x.sh`·L5 `python x.py`·L6 `ruff format app/`(포매터가 제품 코드를 고침)·L7 `npm run build`·L8 `alembic revision`. X14 `bash -s < /tmp/script.sh`(스크립트 파일을 stdin 으로 읽는 것 = `bash x.sh` 의 변형)도 이 범주로 분류한다. 운용 규칙 + verifier 리뷰가 계속 맡는다 — CLAUDE.md·security.md 에 적힌 대로.

## 6. 소견

### [필수]
- **R-14-1 stdin 으로 코드를 받는 셸이 열려 있다** — `printf 'echo x > app/x.py' | bash`(X1)·`echo '…' | sh`(X13)·`bash <<< 'echo x > app/x.py'`(X2) 전부 allow. 근거: `bash_write_check.py` 398~408행 `_shell_codes()` 는 `-c` 인자나 heredoc 본문만 코드로 보고, 인자가 없으면 빈 목록을 돌려준다; 739~740행 `shell_dynamic()` 은 그 빈 목록으로 아무것도 하지 않는다. `<<<` 는 67행 `_REDIR_RE` 가 토큰으로 잡지만 313행이 `<<`·`<<-` 만 heredoc 으로 모은다. 같은 코드를 `bash -c '…'`(V2)·`bash <<'EOF'`(V27) 로 주면 막히므로 이것은 한계가 아니라 변형이다. 대조: 745행 `cmd_python` 은 같은 상황("stdin 에서 코드를 읽는다")을 **차단**한다(C2) — 셸만 빠졌다. 제안: 셸(_SHELLS·_PS_SHELLS)이 스크립트 파일·`-c`·heredoc 없이 실행되면 `cmd_python` 과 같이 "stdin 코드 판정 불가 → 차단"; `<<<` 는 target.text 를 코드로 재귀 분석. 판정 명령: 드라이버 X1·X2·X13 → deny.
- **R-14-2 인라인 코드가 동적이면 통과한다** — `python3 -c "$(cat /tmp/p.py)"`(X3)·`node -e "$(cat /tmp/x.js)"`(X4) allow. 근거: 872~896행 `cmd_python` 과 898~905행 `_inline` 이 `args[k+1].text`(원문 `$(cat …)`)만 정규식으로 훑고 `args[k+1].dynamic` 을 보지 않는다. 반면 919~923행 `shell_dynamic` 은 `bash -c "$(…)"` 를 "실행할 코드를 판정할 수 없다 → 차단" 한다(V26). 수정안 4·security.md "검사할 수 없으면 통과가 아니라 차단" 위반. 제안: 코드 인자 Word 가 `dynamic` 이면 Deny. 판정 명령: 드라이버 X3·X4 → deny.
- **R-14-3 `find … -exec/-execdir` 로 감싼 쓰기가 통과한다** — `find app -name '*.py' -exec sed -i s/a/b/ {} +`(X5) allow. 근거: 359~395행 `strip_prefix` 가 `xargs` 는 벗기고 `stdin_args=True` 로 표시해 `sed -i` 가 "대상이 stdin 에서 옴 → 차단" 되게 하지만(V28·test-guards "xargs sed -i"), `find` 는 핸들러도 접두 처리도 없다. `find -exec` 는 LLM 에이전트가 일괄 치환에 흔히 쓰는 형태이고 xargs 의 형제다. 제안: `find` 조각에서 `-exec`/`-execdir`/`-ok` 뒤 `;`/`+` 까지를 명령으로 재귀하되 대상이 find 결과임을 `stdin_args=True` 로 표시; `-delete`·`-fprint*` 는 대상 판정 불가로 차단. 판정 명령: 드라이버 X5 → deny.
- **R-14-4 문서가 거부되는 명령을 지시한다** — `.claude/agents/verifier.md` 24행 `bash .claude/scripts/verify-plan.sh <id> | tee docs/wiki/packages/<id>/evidence/<ts>-verify-plan.txt`, 32행 `verify-impl.sh <id> | tee …/evidence/…`; 같은 명령이 `.claude/skills/devlog/SKILL.md` 34·42행, `docs/wiki/verification.md` 60행. 드라이버 C5 로 거부 실측(`tee: 쓰기 대상 'docs/wiki/packages/P8-frontend/evidence/x.txt' 는 프로젝트 안이다`). 수정안 11 "하위 에이전트 정의 하네스 규칙의 해당 줄" 범위에서 verifier.md 가 빠졌고, CLAUDE.md 120행 "증거 파일도 tee 가 아니라 Write 툴로" 와 충돌한다. 제안: 세 문서를 "`… > <스크래치패드 리터럴 경로>/x.txt` 뒤 Write 툴로 evidence 에 저장" 으로 고친다(test-guards.sh 머리말 3~4행이 이미 그 문장이다). 판정 명령: `grep -rn 'tee docs/wiki' .claude docs/wiki/verification.md` → 0건.

### [권고]
- **R-14-5 인터프리터 휴리스틱 사각(수정안 2 목록 밖)** — awk 프로그램 안 출력 리다이렉트 `print "x" > "app/x.py"`(X6, `cmd_awk` 는 `-i inplace` 만 봄), perl 3-인자 `open(my $f, ">", "app/x.py")`(X7, 689행 정규식이 `my $f` 를 못 넘음), `php -r file_put_contents(…)`(X8, 핸들러 없음), `builtins.open('docs/zz.md','w')` 별칭(X11 — 649~658행이 수신자가 `_PY_FUNC_MODULES` 밖이면 메서드 호출로 보고 첫 인자 `'docs/zz.md'` 를 모드로 읽는데, 665행 `set(mode) & set("wax+")` 가 경로 글자에 w/a/x 가 있을 때만 우연히 걸린다), `exec(__import__('base64').b64decode(…))` 난독(X12). 제안: python 인라인에 `exec(`/`compile(`/`__import__(` 가 보이면 보수적 차단; perl·awk·php 는 프로그램 문자열에 `>`·`open(`·`file_put_contents`·`fopen` 이 보이면 "대상 판정 불가 → 차단". 또는 한계 문장에 "python/node/PowerShell 외 인터프리터 인라인 코드" 를 추가해 문서화.
- **R-14-6 PowerShell `Invoke-Expression`/`iex` 문자열(X9)·`cmd /c "…"`(X10) 미재귀** — 파싱은 OS 무관해서 Mac 에서 재현된다. Windows 전용 경로이므로 CI windows 와 함께 보되, 제안: `iex`/`invoke-expression` 의 정적 문자열 인자를 PowerShell 코드로 재귀, `cmd` 를 `_SHELLS` 류로 다루어 `/c` 뒤를 재귀.
- **R-14-7 보수적 거부와 `CLAUDE_SCRATCHPAD`** — C1(`cd /tmp && echo x > y`)·C2(`echo … | python3`)·C3(`echo x > $SP/x`) 은 수정안 3·4 대로의 차단이고 우회(절대 경로·`-c`/heredoc·리터럴)가 있다. 그러나 이 검증 중 verifier 본인이 `$SP/…`·`"$T/…"` 로 두 번 막혔고, **`CLAUDE_SCRATCHPAD` 환경변수가 이 세션에 설정돼 있지 않아**(scope §7) 448~449행 `_TMP_DYN_RE` 의 그 분기는 죽은 코드다 — 스크래치패드 허용은 리터럴 경로(`/private/tmp/` 접두 또는 경로 성분 `scratchpad`)로만 동작한다. 제안: 에이전트 정의 3개·CLAUDE.md 120행에 "임시 경로는 변수(`$SP`)가 아니라 **리터럴 절대 경로**로 쓴다" 한 줄; 또는 `_TMP_DYN_RE` 의 `CLAUDE_SCRATCHPAD` 를 문서에서 약속하지 않는다.
- **R-14-8 디렉터리·삭제·압축 해제** — `tar -xf … -C app`(X15)·`unzip … -d app`(X16)은 cp 와 같은 "파일을 만드는" 명령인데 핸들러가 없다(제안: `-C`/`-d` 목적지 판정, 없으면 cwd → 차단). `mkdir app/newdir`(X17)·`rm app/x.py`(X18)는 "쓰기" 목록 밖이라 범위 밖으로 기록만 한다(단일 파일 삭제는 safety-guard 도 보지 않는다).
- **R-14-9 commit-cleanup 의 새 의존** — `bash_write_check.py` 가 없거나 깨지면 `gitcmd` 가 비어 커밋·푸시 처리가 조용히 빠진다(주석대로 "기록 누락이 안전"). 그러나 소비되지 않은 1회용 승인 마커는 다음 `git commit` 을 commit-guard 에서 통과시킬 수 있다 — 파이썬 없음 때와 같은 기존 성질이지만 의존 파일이 하나 늘었다. 제안: `--git-fragments` 호출 실패(rc≠0 또는 스크립트 없음) 시 stderr 경고 한 줄(`[commit-cleanup] 판정 스크립트 없음 — 마커를 소비하지 못했다`).
- **R-14-10 사소한 메시지** — 431행 MAX_DEPTH Deny 문구에만 `[bash-write-guard]` 접두가 없다(F12). PATH 비움 시 25행 `dirname` 자체를 못 찾아 stderr 한 줄이 섞이지만 deny JSON 은 정상(F1).
- **R-14-11 죽은 코드·시험 스크립트 변수 rm** — `commit-cleanup.sh` 16~20행 `cmd=` 는 더 이상 참조되지 않는다(§2 9). `test-guards.sh` 171행 `rm -rf "$BW_T"` 는 변수 경로 재귀 삭제인데 기존 절(CC_T·FG_T·SG_T)과 같은 패턴이라 이번 FIX 의 신규 문제는 아니다 — 기록만.

### 참고(소견 아님)
- F7: `tool_input.command` 가 문자열이 아니면(123) 빈 명령으로 allow — Claude Code 입력 형식상 발생하지 않는다.
- 판정 본체가 before 전에 존재한 점은 §3.2 에 기록. 다음 FIX 부터는 시험 → before → 구현(판정 본체 포함) 순서를 지키는 것이 FIX-013 교훈에 맞다.

## 7. 재검증 방법 (R-14-1~R-14-4 를 닫은 뒤)
1. `bash .claude/scripts/test-guards.sh > <스크래치패드 리터럴>/tg.txt 2>&1` → 실패 0 (test-guards 에 X1·X2·X13·X3·X4·X5 를 거부 기대로 추가했는지도 본다 — 검출력: 고치기 전 훅에서 XX 여야 한다).
2. `…-drive-src.txt` 를 스크래치패드에 `drive.py` 로 두고 `python3 drive.py <저장소> <스크래치패드>` → X1~X5·X13 deny, C5 는 문서만 고치는 것이므로 그대로 deny(기대를 deny 로 바꿔 읽는다), 나머지 allow/deny 변동 없음.
3. `grep -rn 'tee docs/wiki' .claude docs/wiki/verification.md` → 0건.
4. 통과하면 `FIX-014.md` 의 `검증:` 줄을 `검증: 통과 — verifier (fable) 2026-10-11, review-FIX-014.md (Windows 는 푸시 뒤 CI windows job)` 로(verifier 가 쓴다).

## 재검증 (2026-10-11)

검토자: verifier (fable) · 1차와 **다른 새 컨텍스트** · 기준 HEAD `d16375e` + 작업 트리(1차 구현 + 재작업 R-14-1~4) · 대상 diff: `bash_write_check.py`(신규, 재작업분 `Frag.stdin_dynamic/piped/pipe_src`·`_pipe_literal`·`_stdin_codes`·`_need_static`·`_find_exec_frags`·`_frag_cmds`)·`test-guards.sh`(+23 시험)·`verifier.md`·`devlog/SKILL.md`·`verification.md`·`FIX-014.md` 결과절. 코드·훅·계획은 고치지 않았다. 임시 파일은 스크래치패드 리터럴 절대 경로에만 두고 증거는 Write 툴로 저장했다(고친 문서 3곳의 절차 그대로 — §R3).

**결과: 보류.** 1차 [필수] 4건은 닫혔다(§R1). 그러나 재작업이 열어 둔 같은 종류의 구멍이 5개 남아 있고(§R2) 전부 라이브 훅을 통과시켜 실제 파일을 만드는 것까지 확인했다. 새 [필수] 2건(R-14-12·R-14-13)을 닫고 §R7 로 다시 보면 통과다. 나머지(오탐 회귀·검출력·test-guards·문서·fail-closed·FIX-014.md 정합)는 전부 조건을 충족한다.

### R1. [필수] 4건 해소 — 확인 1
드라이버 1(`…-drive-src.txt` 를 스크래치패드에 복원, C5 기대만 deny 로 갱신) 재실행 → `evidence/20261011-verifier-fix014-recheck-drive.txt`. **불일치 22 → 14.**

| 소견 | 판정 명령 | 결과 |
|---|---|---|
| R-14-1 stdin 셸 | X1 `printf … \| bash` · X2 `bash <<< …` · X13 `echo … \| sh` · X14 `bash -s < file` | 전부 **deny** (X1·X2·X13 은 본문 재귀로 `리다이렉트 '>' app/x.py`, X14 는 `실행할 코드를 판정할 수 없다`) |
| R-14-2 동적 인라인 | X3 `python3 -c "$(cat …)"` · X4 `node -e "$(cat …)"` | 전부 **deny** (`인라인 코드가 변수·명령 치환을 포함`) |
| R-14-3 find -exec | X5 `find app -exec sed -i … {} +` | **deny** (`sed -i: 쓰기 대상 'app'` — `{}` → 시작 경로 치환) |
| R-14-4 문서 | `grep -rn 'tee docs/wiki' .claude docs/wiki/verification.md` | **1건** = `test-guards.sh:191` 거부 기대 시험의 입력 문자열(명령 아님). C5 → **deny**(일치) |

남는 불일치 14 = 침입 11(X6 X7 X8 X11 X12 → R-14-5 · X9 X10 → R-14-6 · X15 X16 → R-14-8 · X17 X18 쓰기 목록 밖) + 오탐 3(C1 C2 C3 → R-14-7 보수적 거부 유지). 구현자 보고(`…-rework-driver.txt` "남는 15 = 11 + 3 + C5")·`FIX-014.md` 103~111행 한계 목록과 **번호별 일치**. 오탐 W1~W49·S6-1~6·C4 **55건 전부 allow**(새 오탐 0).

### R2. 새 우회 시도 — 확인 2 → **5건 뚫림 → [필수]**
드라이버 2(`…-recheck-drive2-src.txt`) 53건 + 경계 12건 → `evidence/20261011-verifier-fix014-recheck-bypass.txt`. 위임 프롬프트의 예시 9건(`cat <<EOF | bash`·`bash -s <<<`·`sh -s -- <<EOF`·`python3 - <<<`·`find -execdir sh -c`·`find -ok mv`·`xargs -I{} sh -c … < list`·`… | tee /tmp/s.sh | bash`·`zsh <<< "$(cat f)"`)은 **전부 deny**. 그 밖 `bash -`·`/bin/bash`·`env bash`·`command sh`·`echo -e`·`printf '%s\n'`·`|&`·그룹·서브셸·base64 파이프·중첩 here-string·연쇄 파이프·`-exec` 안 동적 코드·괄호 뒤 `-exec`·`-okdir cp`·`perl -pi`·`node --eval/-p`·`ruby -e "$X"`·`python3 -Ic`·xargs touch/cp/tee 등 **43건 deny**. 뚫린 것:

| # | 명령 | 실제 | 실증(라이브 훅 통과, 스크래치패드 `proof/app/` 에 파일 생성) |
|---|---|---|---|
| N25 | `bash <<EOF` ␤ `$(cat /tmp/f)` ␤ `EOF` | allow | `app/n25.py` 생성 |
| N26 | `bash <<EOF` ␤ `$CMD` ␤ `EOF` | allow | `app/n26.py` 생성 |
| N27 | `echo 'echo x > app/x.py' \| xargs -I{} bash -c {}` | allow | `app/n27.py` 생성 |
| N28 | `echo '…' \| xargs -I{} sh -c '{}'` | allow | (N27 과 같은 경로) |
| N30 | `printf "open('app/x.py','w')" \| xargs -0 -I{} python3 -c {}` | allow | `app/n30.py` 생성 |
| E1/E2 | `cat <<EOF` ␤ `$(echo x > app/x.py)` ␤ `EOF` (비셸 heredoc 본문의 치환) | allow | `app/e1.py` 생성 |

1차 [필수] 기준("훅이 이미 막는 형태의 형제", "검사할 수 없으면 차단" 위반)을 그대로 적용한다: N25·N26 은 재작업이 막은 `bash <<< "$(cat f)"`(동적 here-string)·`bash -c "$X"` 의 **heredoc 형제**이고, N27·N28·N30 은 재작업이 막은 `… | bash`·`… | xargs bash -c`(N29 deny) 의 **자리표(-I{}) 형제**다. E1 은 1차부터 막아 온 "명령 치환 안의 리다이렉트"(`echo $(cat x > app/y)`, test-guards 거부 기대)의 **heredoc 본문 형제**다. 셋 다 프로그램 부작용(수정안 5)이 아니라 셸 문법이다.

### R3. 오탐 회귀 — 확인 3
드라이버 1 의 1차 허용 60건 중 C1~C3 외 **전부 allow**(변동 0). 재작업이 허용으로 고정한 7건(A1~A7: `printf 'ls' | bash`·`bash <<< 'ls -la'`·`echo 'echo x > /tmp/y' | sh`·`python3 -c "print(1)"`·`find -exec grep -l`·`find -exec wc -l`·`find /tmp -exec sed -i`) **전부 allow**. 대조 13건(`cat <<EOF | bash` 에 쓰기 없는 본문, `bash -s` 읽기, `python3 - <<< 'print(1)'`, `find -exec sh -c 'wc -l "$1"'`, `find -exec cp {} /tmp/`, `xargs -I{} python3 -c {}` 읽기, 그리고 **이 재검증이 실제로 쓴 명령** `test-guards.sh > <스크래치패드 리터럴>/tg.txt 2>&1`·`python3 drive.py … > …`·`git diff HEAD -- …`·`grep -rn 'tee docs/wiki' …`·`diff … | head`) **전부 allow**. 새로 막힌 정상 명령 0.

### R4. 검출력 증거 — 확인 4
`evidence/20261011-verifier-fix014-recheck-scope.txt` §1. `rework-before`(FIX-014 절) ↔ 이번 `tg.txt`(FIX-014 절) diff = **16쌍(XX→ok) + 결과 줄**만. `1609-after` ↔ `rework-before` = **새 16 XX + 새 7 ok 만 추가**, 기존 줄 삭제·변경 0. `1609-after` 전체 ↔ 이번 `tg.txt` 전체 = 머리말 주석 + FIX-014 절 23줄만. → before 는 "시험만 추가하고 코드는 1차 상태" 를 반영하고, 차이는 FIX-014 절에만 있다. 유효.

### R5. test-guards 직접 실행 — 확인 5
`bash .claude/scripts/test-guards.sh` → rc 0 · **ok 287 · XX 0 · skip 1**(active=P8-frontend) · `== 결과: 실패 0 ==`. 전체 306행 → `evidence/20261011-verifier-fix014-recheck-test-guards.txt`(요약 아님, 원문). 구현자 `…-rework-after.txt`(요약본)와 집계 일치.

### R6. 문서 — 확인 6
`grep -rn 'tee docs/wiki' .claude docs/wiki/verification.md` → `test-guards.sh:191` 1건(시험 입력). `verifier.md` 24·32행·`SKILL.md` 34~35·43행·`verification.md` 60~61행의 새 문구("Write 툴로 저장, 긴 출력은 스크래치패드 **리터럴 절대 경로**로 `>` 한 뒤 Read → Write")는 이 재검증이 **그 절차대로 실행해** 확인했다(scope §3): `> /private/tmp/claude-501/…/scratchpad/tg.txt` allow → Read → Write 성공, 드라이버 A14·A15 도 allow. 1차에 verifier 본인이 막혔던 `$SP/…` 형태(C3)는 여전히 deny 이므로 "리터럴" 한정이 맞는 문구다.

### R7. fail-closed — 확인 7
깨진 JSON → `훅 입력을 해석할 수 없어 … 차단한다` deny · PATH 비움 → `파이썬 인터프리터를 찾지 못해 … FIX-008` deny · 빈 stdin → deny (`…-recheck-bypass.txt` F1~F3). 회귀 없음.

### R8. FIX-014.md 결과절 ↔ 드라이버 — 확인 8
102행 "남는 불일치 15건" 과 103~111행 번호(X6 X7 X8 X11 X12 · X9 X10 · X15 X16 · X17 X18 · C1 C2 C3 · C5) → 내 드라이버(C5 기대 갱신 후 14) 와 **일치**. 다만 95행 한계 문장 "heredoc 본문 안의 `$(…)` 치환은 재귀 분석하지 않는다" 는 반만 맞다 — 셸 heredoc 본문은 `iter_cmds` 로 재귀되고(V27·N19 deny) 비셸(`cat`) 본문만 분석하지 않으며(E1·E2 allow), 셸 본문의 `$(…)`·`$VAR` 는 명령으로 재귀되지만 **그 결과가 실행 코드라는 점**은 보지 않는다(N25·N26 allow). 이 문장은 수정안 1~11 의 승인된 한계(수정안 5 "프로그램 실행")가 아니라 구현자가 결과절에 덧붙인 것이므로 R-14-13 으로 소견화한다.

### 소견 (재검증에서 새로 냄)

#### [필수]
- **R-14-12 xargs 자리표로 넘긴 코드가 "정적 코드" 로 취급된다** — `echo '…' | xargs -I{} bash -c {}`(N27)·`… | xargs -I{} sh -c '{}'`(N28)·`printf … | xargs -0 -I{} python3 -c {}`(N30) allow, 실증 `proof/app/n27.py`·`n30.py` 생성. 근거: `strip_prefix()` 384~420행이 `xargs` 를 벗기며 `stdin_args=True` 만 돌려주고, `_shell_codes()` 460~461행과 `cmd_python()` 975~977행·`_inline()` 1008~1010행은 `-c`/`-e` 다음 Word 의 `.dynamic` 만 본다 — `{}` 는 리터럴이라 `dynamic=False`, 코드 "`{}`" 를 재귀 분석해 아무것도 못 찾고 통과한다. 반면 자리표 없이 `… | xargs bash -c`(N29)·`… | xargs python3 -c`(N31) 는 `-c` 다음 인자가 없어 stdin 분기로 떨어져 deny 된다 — 같은 행위의 형제가 자리표 하나로 갈린다. 또 `xargs -I{} sh -c 'echo > {}'`(V28) 처럼 자리표가 **경로** 자리에 오면 거부되는데 **코드** 자리에 오면 통과한다. 제안: `stdin_args=True`(xargs 아래) 인 조각에서 셸·인터프리터의 코드 인자(`-c`/`-e`/`--eval`/`-p`)는 "stdin 에서 온 코드" 로 보고 `_pipe_literal(frag)` 로 내용을 알 수 있으면 그것을 재귀 분석, 아니면 `Deny`(판정 불가). 더 단순하게는 `stdin_args` 이고 코드 인자 텍스트에 `{}`(또는 `-I` 값)가 들어 있으면 `dynamic` 취급. 판정 명령: 드라이버 2 N27·N28·N30 → deny, A13(`echo 'print(1)' | xargs -I{} python3 -c {}`) 은 allow 유지 또는 보수적 deny 둘 다 허용(test-guards 에 거부 기대 3건 추가, 검출력 전/후 증거).
- **R-14-13 heredoc 본문의 치환·변수를 보지 않는다** — (a) 셸: `bash <<EOF` ␤ `$(cat /tmp/f)` ␤ `EOF`(N25)·`$CMD`(N26) allow, 실증 `proof/app/n25.py`·`n26.py`. 따옴표 없는 구분자의 본문은 바깥 셸이 확장한 뒤 bash 가 실행하므로 실행 코드가 동적이다 — 재작업이 막은 `bash <<< "$(cat f)"`(X-동적 here-string, parse 326~328행 `target.dynamic → stdin_dynamic`) 와 같은 상황인데 heredoc 경로(324~325행 `pending`)는 `dynamic` 을 보지 않고 `read_bodies()` 275~290행이 본문을 그대로 `heredocs` 에 넣는다. 그 본문을 `_frag_cmds` 531~533행이 `iter_cmds` 로 재귀하면 `$(cat /tmp/f)` 는 "`cat /tmp/f` 라는 명령" 으로만 보이고 그 출력이 실행된다는 점은 사라진다. (b) 비셸: `cat <<EOF` ␤ `$(echo x > app/x.py)` ␤ `EOF`(E1·E2) allow, 실증 `proof/app/e1.py`. `cat` 에는 핸들러가 없어 본문이 분석되지 않지만 `$(…)` 는 **바깥 셸이 실행**한다 — 1차부터 test-guards 거부 기대인 "명령 치환 안의 리다이렉트"(`echo $(cat x > app/y)`) 와 같은 행위다. `FIX-014.md` 95행이 이것을 한계로 적었지만 수정안 5 의 한계("프로그램 실행의 부작용")가 아니고 수정안 2("heredoc") ·4("판정 불가 → 거부") 범위다. 제안: `parse()` 에서 heredoc 구분자 Word 가 따옴표로 둘러싸였는지(`<<'EOF'`/`<<"EOF"`) 를 기록하고, 따옴표 없는 본문은 **모든 명령**에 대해 `$(…)`·백틱 치환을 `Word.subs` 처럼 `iter_cmds` 로 재귀하며(E1 해결), **셸로 들어가는** 본문에 `$(…)`·백틱·`$VAR`/`${…}` 가 남아 있으면 `stdin_dynamic=True`(N25·N26 해결 — `bash <<< "$(…)"` 와 같은 규칙). 따옴표 구분자(`<<'EOF'`, W13·V27·N20)와 이스케이프(`\$F`, E12 는 이미 deny)는 그대로. 판정 명령: 드라이버 2 N25·N26·E1·E2 → deny, W13·V27·A8·N1 → 변동 없음(test-guards 에 거부 기대 4건·허용 대조 1건 추가, 검출력 전/후 증거). `FIX-014.md` 95행 한계 문장은 삭제하거나 "따옴표 구분자 heredoc 본문은 확장이 없어 분석하지 않는다" 로 바꾼다.

#### [권고]
- **R-14-14 stdin 코드 차단이 python 에만 있다** — `echo "require('fs').writeFileSync('app/x.js','x')" | node`(E4)·`echo 'open(F,">app/x.py")' | perl`(E3)·`echo "File.write(…)" | ruby`(E5) allow. `cmd_python` 987~995행은 코드 인자·heredoc·스크립트 없이 실행되면 stdin 코드로 보고 deny 하는데 `cmd_node`·`cmd_ruby`·`cmd_perl` 에는 그 분기가 없다. `FIX-014.md` 111행이 `node < file` 만 적었다. 제안: 세 핸들러에 `cmd_python` 과 같은 분기(`_stdin_codes` 로 리터럴이면 검사, 아니면 deny). 또는 한계 문장을 "`… | node/perl/ruby`" 까지 넓혀 문서화.
- **R-14-15 그 밖 기록(막지 않음)** — `pwsh -Command -`(E8, stdin 코드 — R-14-6 과 함께) · `. /tmp/s`·`source /tmp/s`(E6·E7, L4 `bash x.sh` 와 같은 범주) · `xargs -a /tmp/list sed -i`(E9, GNU xargs 의 파일 입력 — `-a` 가 `strip_prefix` 417행 값 옵션 목록에 없어 `list` 가 명령으로 오인) · `… | busybox sh`(E10) · `find -delete`(E11, 문서화됨). R-14-5·6·8 과 함께 후속 FIX 후보.
- **R-14-7 잔존** — `backend-agent.md` 71행·`eval-agent.md` 61행·`frontend-agent.md` 53행에 "임시 경로는 변수가 아니라 **리터럴 절대 경로**" 가 없다(verifier.md 에만 있음). C3 `> $SP/x` 는 여전히 deny.
- **FIX-014.md 95행** 한계 문장 정정(R-14-13 과 함께).

### 재검증 방법 (R-14-12·R-14-13 을 닫은 뒤)
1. `bash .claude/scripts/test-guards.sh > <스크래치패드 리터럴>/tg.txt 2>&1` → 실패 0, 새 거부 기대(N25·N26·N27·N28·N30·E1·E2)가 **고치기 전** XX 인 before 증거.
2. `…-recheck-drive2-src.txt` 를 스크래치패드에 `drive2.py` 로 Write → 실행 → 마지막 줄 `불일치 0`, A1~A20 전부 allow, E3~E11 은 기록.
3. `…-drive-src.txt`(C5 deny) 재실행 → `불일치 14` 그대로(회귀 없음).
4. 통과하면 `FIX-014.md` 의 `검증:` 줄을 `검증: 통과 — verifier (fable) <날짜>, review-FIX-014.md (재검증; Windows 는 푸시 뒤 CI windows job)` 로.

증거: `evidence/20261011-verifier-fix014-recheck-{test-guards,drive,bypass,scope,drive2-src}.txt`.

## 3차 검증 (2026-10-11)

검토자: verifier (fable) · 1·2차와 **다른 새 컨텍스트** · 기준 작업 트리(d16375e + 1·2차 재작업 누적) · 코드·훅·계획·문서는 고치지 않았다. 임시 파일은 스크래치패드 리터럴 절대 경로에만. 증거는 Write 툴로 저장.

**판정: 보류.** 판정 규칙(사용자 2026-10-11 19:35 회차 상한)의 통과 조건 중 "지정 3건 해소" 가 **R-14-14 에서 충족되지 않는다**: 명령 프롬프트가 R-14-14 의 가까운 변형으로 **명시한** `deno run -` 이 ALLOW 로 뚫린다(덜 닫힘). 나머지 조건(R-14-12·R-14-13 해소, 오탐 회귀 0, test-guards 실패 0, 검출력, fail-closed, 문서, FIX-014.md 정합)은 **전부 충족**. 새로 찾은 그 밖의 우회(python/node/ruby heredoc 동적 본문 등)는 [필수]가 아니라 후속 FIX 후보로 기록만 한다.

### 3-R1. 지정 3건 — 확인 1 (증거 final-summary §1·1b, final-variants)
- **R-14-12 (해소)**: drive2 N27·N28·N30 deny(`불일치 0`). 명령 프롬프트 명시 변형 `-I%`·`--replace=@`·`-i` 를 포함해 `-i%`·`-0I{}`·띄어쓴 `-I {}`·node/ruby/python 코드 자리까지 V12-1~15 **전부 deny**. 자리표가 인자 자리면 allow 유지(P11·P12). 완전히 닫힘.
- **R-14-13 (해소, 셸 heredoc 범위)**: drive2 N25·N26·E1·E2 deny. 명시 변형 `<<-EOF`·백틱 본문·`${VAR}`·`$VAR`(셸 heredoc) V13-1~10·12 **전부 deny**. 인용 구분자(`<<'EOF'`)·값 치환뿐인 비셸 heredoc·쓰기 없는 heredoc 은 allow 유지(P7·P8·P13·P14). 셸 heredoc 범위에서 닫힘.
- **R-14-14 (덜 닫힘 → 보류)**: `node -`·`nodejs`·`bun`·`php`·`ruby -`·`perl -`·`node < file` 은 deny. 그러나 **`deno run -` → ALLOW**, `deno eval` → ALLOW, `bun run -` → ALLOW. `deno run -` 은 명령 프롬프트 변형 목록에 **명시**됐고, `FIX-014.md` 118행이 "node·nodejs·bun·deno·ruby·perl·php 가 … 파이프·here-string·heredoc·`< 파일` 로 코드를 받으면 … 거부" 라고 **deno·bun 을 명시 범위에 넣었다**. deno·bun 의 표준 stdin 실행형이 그 명시 범위 안에서 열려 있으므로 "지정 건 덜 닫힘" 이다.
  - 원인(추정): `cmd_node`(=`cmd_deno`=`cmd_bun`)의 `_interp_codes` 2차 루프(1174~1186행)에서 서브명령 `run`/`eval` 이 값옵션도 `-`도 아닌 위치인수라 "스크립트 파일 실행" 으로 보고 `list(frag.heredocs)` 를 조기 반환 → stdin 코드 판정(`_stdin_code_list`)에 도달하지 못한다.
  - 판정 명령(닫은 뒤 재검증): drive3 V14-3, 모듈 `deno run -`·`deno eval`·`bun run -` → deny 로 전환, `deno run app/x.ts`(스크립트 실행)·`bun install` 류는 allow 유지(한계). test-guards 에 거부 기대 추가 + 검출력 전/후 증거.

### 3-R2. 지정 건 대조 — drive.py (C5 기대 deny) `불일치 14` 유지, drive2.py `불일치 0`
번호별 X6 X7 X8 X9 X10 X11 X12 X15 X16 X17 X18 + C1 C2 C3 — `FIX-014.md` 120행·2차 재검증 R1 과 동일. 회귀 없음.

### 3-R3. 오탐 회귀 0 — 확인 2
drive3 P1~P20(commit·push·pytest 파이프·gh·grep·인용 구분자 heredoc·`echo 'console.log(1)' | node`·스크래치패드 리터럴 `>`·find 읽기·diff 파이프) **전부 allow**. drive2 A1~A20·drive W/S6/C4 allow. C1·C2·C3 은 1·2차와 같은 문서화된 보수적 거부(새로 막힌 것 아님). **새로 막힌 정상 명령 0.**

### 3-R4. 검출력 — 확인 3
`rework2-before`(FIX-014 절) XX 17 ↔ `after` 0, before↔after diff 는 FIX-014 절 17줄(XX→ok DENY)+결과줄뿐(§확인3). 내 `tg.txt` ↔ 2차 `recheck-test-guards.txt` diff = 머리말 주석 6줄뿐. 차이는 FIX-014 절에만.

### 3-R5. test-guards 직접 실행 — 확인 4
`bash .claude/scripts/test-guards.sh` rc 0 · **ok 316 · XX 0 · skip 1 · "== 결과: 실패 0 =="**. 전체: `evidence/20261011-verifier-fix014-final-test-guards.txt`.

### 3-R6. fail-closed — 확인 5
F1 깨진 JSON deny · F2 PATH 비움 deny(FIX-008) · F3 빈 stdin deny. 회귀 없음.

### 3-R7. 문서·FIX-014.md 정합 — 확인 6·7
`grep -rn 'tee docs/wiki'` → `test-guards.sh:191`(시험 입력) 1건. verifier.md/SKILL.md/verification.md 의 "Write 툴/리터럴 절대경로 `>`" 문구는 이 검증이 그 절차대로 실행해 확인(리터럴 `>` allow·`$SP/x` deny). CLAUDE.md 120행·security.md §4b/§7·에이전트 정의: 최종 동작과 어긋남 없음. `FIX-014.md` 120행 "불일치 14" 번호별 일치, 95행 한계 문장도 동작과 일치. 다만 **118행 "deno" 명시 범위가 실제로는 `deno run -`/`bun run -`/`deno eval` 에서 덜 닫힘**(위 3-R1).

### 3-R8. 새 우회 탐색 — 후속 FIX 후보 표 (기록용, [필수] 아님 — 원칙8)

| # | 재현 명령 | 실제 | 원인 추정 |
|---|---|---|---|
| R-14-16 | `echo '<write>' \| deno run -` · `echo '<write>' \| bun run -` · `deno eval "Deno.writeTextFileSync(...)"` | **allow** | R-14-14 와 같은 뿌리. `_interp_codes` 가 서브명령 `run`/`eval` 을 스크립트 파일로 오인해 조기 반환, stdin 코드 판정 누락. **이번 보류의 직접 사유**(명령 프롬프트 명시 변형). 닫으면 R-14-14 완결. |
| R-14-17 | `python3 <<EOF` ␤ `$(cat /tmp/p.py)` ␤ `EOF` | allow | `cmd_python`(1119~1127행)이 `frag.heredoc_dyn` 을 보지 않고 heredoc 본문을 리터럴 코드로만 검사. 바깥 셸이 `$(…)` 를 먼저 실행해 그 출력을 python 이 실행하는 점을 놓침. 셸 heredoc(`bash <<EOF $(…)`)은 `_stdin_codes` 가 `heredoc_dyn` 을 보므로 deny — python/비셸 경로만 샌다. |
| R-14-18 | `node <<EOF` ␤ `$(cat f)` ␤ `EOF` · `ruby <<EOF` ␤ `$(cat f)` ␤ `EOF` | allow | `_stdin_code_list`(1151~1164행)이 `frag.stdin_dynamic`·`piped` 만 보고 `heredoc_dyn` 을 보지 않음. R-14-17 과 같은 누락. |
| R-14-5 재확인 | `php -r 'file_put_contents(...)'`(Z1) · `awk 'BEGIN{print "x" > "f"}'`(Z2) | allow | 2차 후속 후보 그대로. php `-r` 인라인·awk 프로그램 내 리다이렉트 미처리. |
| R-14-6 재확인 | `echo '...' \| pwsh -Command -`(Z3) | allow | PowerShell stdin 코드 미재귀. |
| R-14-15 재확인 | `xargs -a /tmp/list sed -i`(Z4) · `source /tmp/s`(Z5) · `echo '...' \| busybox sh`(Z6) · `find app -delete`(Z7) · `tar -xf -C app`(Z8) | allow | 2차 후속 후보 그대로(xargs `-a` 파일 입력·source·busybox·find -delete·tar/unzip 목적지). |

→ 닫은 뒤 재검증 방법: drive3 V14-3·R-14-16 모듈 케이스 deny, `deno run app/x.ts` allow 유지, test-guards 거부 기대 추가 + 검출력 전/후. R-14-17·18 은 `cmd_python`/`_stdin_code_list` 에 `heredoc_dyn` 분기를 더하면 닫힌다.

### 보류 사유 (요약)
지정 건 **R-14-14 가 명령 프롬프트 명시 변형 `deno run -`(및 `deno eval`·`bun run -`) 에서 바로 뚫린다**. FIX-014.md 118행이 deno·bun 을 명시 범위에 넣었으므로 이는 새 우회가 아니라 지정 건의 미완결(덜 닫힘)이다. 이 한 건을 닫고 3-R8 재검증을 하면 통과다. 나머지 통과 조건은 모두 충족.

증거: `evidence/20261011-verifier-fix014-final-{summary,variants,test-guards}.txt`.

## 4차 검증 (2026-10-11)

검토자: verifier (fable) · 1·2·3차와 **다른 새 컨텍스트** · 기준 작업 트리(d16375e + 1·2·3차 재작업 누적, 미커밋) · 코드·훅·계획·문서는 고치지 않았다(이 절·머리 판정 줄·`FIX-014.md` `검증:` 줄만 썼다). 임시 파일은 스크래치패드 리터럴 절대 경로에만. 증거는 Write 툴로 저장했고, 사본 ↔ 스크래치패드 원본 출력을 `diff` 로 글자 단위 대조했다.

**판정: 통과.** 판정 규칙(사용자 2026-10-11 20:35, `FIX-014.md` `승인:` 줄 "R-14-16 만 더 닫고 좁은 재검증")의 통과 조건을 전부 충족한다 — ① R-14-16 과 명시 변형 deny ② 오탐 회귀 0 ③ test-guards 실패 0 ④ 3차 통과 항목(R-14-12·13·14 node/ruby/perl/php, drive2 0, drive 14) 무회귀 ⑤ 지시 밖 1줄 `(?:Sync)?` 는 필요·무해. 새로 찾은 우회는 규칙대로 [필수]가 아니라 4-R8 후속 후보 표에만 기록했다.

### 4-R1. R-14-16 직접·변형 — 확인 1 (증거 `r16-variants.txt` "## R-14-16 직접·변형")
- 3차에서 뚫렸던 3건 재실행: `printf W | deno run -`(V14-3) · `printf BW | bun run -` · `printf W | deno eval` → **전부 deny**(사유 "node 파일 쓰기: 쓰기 대상 'app/x.js' 는 프로젝트 안").
- 명령 프롬프트 명시 변형 전부 deny: `deno run -A -` · `--allow-write -` · `--allow-write=app --quiet -` · `-A --unstable -` · `deno eval -` · `deno eval "W"`(정적 인라인) · `deno eval --ext=ts "W"` · `deno eval -p "W"` · `bun x -` · `bun -` · `bun run --silent -` · `deno x -` · `deno -`.
- heredoc/here-string 전부 deny: `deno run - <<EOF W` · `deno run -A - <<'EOF' W`(인용 구분자) · `deno run - <<< W` · `bun run - <<EOF BW` · `bun run - <<< BW` · `deno eval <<< W` · `deno eval <<EOF W`.
- 동적 입력 전부 deny(판정 불가 → 차단): `cat f | deno run -` · `cat f | bun run -` · `cat f | deno eval` · `deno run - < f` · `bun run - < f` · `echo "$(cat f)" | deno run -` · `deno eval "$(cat f)"` · `deno run - <<< "$(cat f)"` · `curl … | deno run -A -`.
- 쓰기 API 변형 deny: async `Deno.writeTextFile` · `Deno.writeFileSync` · `Bun.write` · `fs.writeFileSync`(deno 로) · 절대 경로 `/usr/local/bin/deno run -` · `2>/dev/null` 꼬리 · `cd app && …` · `xargs -I{} deno eval {}`(자리표 코드).
- **41건 중 40 deny, 1건 allow: #32 `deno run - <<EOF` ␤ `$(cat /tmp/f.ts)` ␤ `EOF`.** 이것은 R-14-16(서브명령 뒤 stdin 판정 누락)이 아니라 3차 3-R8 이 이미 올린 **R-14-18**(비셸 인터프리터의 `_stdin_code_list` 가 `frag.heredoc_dyn` 을 보지 않음 — node·ruby 와 같은 뿌리)의 deno 인스턴스다. 같은 heredoc 이 정적 본문이면(#17·#18) deny 이므로 R-14-16 경로는 닫혔고, 동적 본문만 R-14-18 로 샌다. 판정 규칙 "이미 후속 후보인 것 포함 → [필수] 아님" 적용.
- 코드 읽기로 원인 해소 확인: `bash_write_check.py` 1166~1196행 `_interp_codes` 가 `subcmds`(첫 위치인수 `run`/`eval`/`x`/`exec`)를 위치인수로 세지 않고 건너뛰어, 뒤가 `-`·무인자면 1196행 `_stdin_code_list` 에 도달하고, `code_subcmds`(`eval`)면 1194행에서 다음 인자를 인라인 코드로 검사한다. `cmd_deno`(1212)·`cmd_bun`(1215)이 `cmd_node` 별칭에서 분리돼 `_cmd_runtime`(1205)으로 간다. node 경로(1198)는 서브명령 표 없이 그대로.

### 4-R2. 오탐 회귀 0 — 확인 2 (증거 `r16-variants.txt` "## 오탐" · "## 작업 흐름 P1~P20")
`deno run app/x.ts` · `deno run -A app/x.ts` · `--allow-all` · `deno run -A npm:prettier --check .` · `bun run build` · `bun run test` · `bun run app/x.ts` · `bun test` · `bun install` · `bun x prettier --check .` · `deno eval "console.log(1)"` · `deno eval "…readTextFileSync(…)"`(읽기) · `echo 'console.log(1)' | deno run -` · `… | bun run -` · `… | deno eval` · `deno --version` · `bun --version` · `deno -V` · `deno task dev` · `deno fmt --check` · `deno lint app` · `deno test -A` · `deno check app/x.ts` · `deno run - <<< 'console.log(1)'` · `printf writeTextFileSync('/tmp/x.js') | deno run -`(임시 경로) · `echo W | grep -c deno`(실행 아님) — **26건 전부 allow**. 작업 흐름 P1~P20(git status/add+commit -F/push dev2 · pytest|tee 스크래치패드 · gh · grep · `cat <<'EOF'` 인용 구분자 · `echo 'console.log(1)' | node` · 스크래치패드 리터럴 `>` · find 읽기 · diff 파이프 · gitlog.sh · alembic · npm run build · curl -o 스크래치패드 · sed -n · ls · python3 -c print · wc|sort · `>&2`·`2>/dev/null`) **전부 allow**. drive2 A1~A20·drive W1~W49/S6/C4 allow(4-R3). 3차 P1~P20 소스는 증거에 없어 같은 범주로 재구성했다(`r16-drive5-src.txt`). **새로 막힌 정상 명령 0.**

### 4-R3. 회귀 — 확인 3 (증거 `r16-drivers.txt`, `r16-variants.txt` "## (?:Sync)? 회귀")
- drive2.py(2차 verifier 소스 복원) **`불일치 0 (셸 stdin 0 · 동적·find·xargs 0 · 오탐 0)`** — N1~N34·N40~N59 deny, E1~E5·E12 deny, E6~E11 한계(allow, R-14-15 후속 후보 그대로), A1~A20 allow, F1~F3 deny.
- drive.py(1차 verifier 소스 복원, C5 기대 deny) **`불일치 14 (침입 11 · 오탐 3)`** — X6 X7 X8 X9 X10 X11 X12 X15 X16 X17 X18 + C1 C2 C3. 2·3차와 **번호별 동일**, 새 오탐 0, C5 deny 일치.
- node/ruby/perl/php stdin 코드(3차 R-14-14): `echo BW | node` · `echo File.write | ruby` · `echo open(">…") | perl` · `echo file_put_contents | php` · `node < f` deny, `echo 'puts 1' | ruby` · `echo 'console.log(1)' | node` allow — 유지.
- `(?:Sync)?` 가 기존 패턴을 깨지 않음: `fs.writeFileSync`·`writeFile`·`appendFileSync`·`copyFileSync(/tmp→app)` deny, `copyFileSync(app→/tmp)`·`writeFileSync('/tmp/…')` allow, 옛 패턴 `Deno.writeTextFile` deny 유지, `Bun.write` deny, 변수 경로 deny, `console.log('writeFileSync')`(괄호 없음) allow, `readFileSync` allow — 20건 불일치 0.

### 4-R4. 검출력 — 확인 4
`rework3-before.txt`(deno/bun 서브명령 처리를 옛 동작으로 되돌린 상태) R-14-16 거부 기대 7건 **전부 XX**, `== 결과: 실패 7 ==` ↔ `rework3-after.txt` 같은 7줄 `ok DENY`, `실패 0`. 두 파일 `diff` = 머리말 주석 + 그 7줄 + 결과줄뿐(내가 다시 돌림). 허용 기대 5건은 before 에서도 ok(오탐 방향 변화 없음). 내 `tg4.txt` ↔ 2차 전체 출력 `recheck-test-guards.txt` diff = 머리말 7줄 + FIX-014 절에 추가된 R-14-12/13/14/16 시험 줄만, 삭제·변경 0(`r16-fail-closed.txt` §4). 차이는 FIX-014 절에만.

### 4-R5. test-guards 직접 실행 — 확인 5 (증거 `r16-test-guards.txt`, 전체 출력)
`bash .claude/scripts/test-guards.sh` → rc 0 · **ok 328 · XX 0 · skip 1(active=P8-frontend) · `== 결과: 실패 0 ==`**. 3차 316 → 328 = R-14-16 거부 7 + 허용 5(`git diff .claude/scripts/test-guards.sh` 의 `+` R-14-16 줄 expect_deny 7 · expect_allow 5 와 일치).

### 4-R6. fail-closed — 확인 6 (증거 `r16-fail-closed.txt` §1)
깨진 JSON(`{"tool_name":"Bash","tool_input":{"command": "echo hi"` — 닫는 괄호 없음)을 라이브 훅에 직접 → **deny** "훅 입력을 해석할 수 없어 검사하지 못했다(JSONDecodeError) — 차단한다". 대조 정상 JSON `echo hi` → allow. drive5 F1·F3, drive2 F1·F2(PATH 비움)·F3 deny. 덧붙여 이 검증 세션의 내 Bash 호출(`python3 - <<'PY' … open(p,"w")`, 경로가 변수)이 라이브 훅에 실제로 막혔다(§3) — 훅이 살아 있고 설계대로 판정한다는 직접 증거.

### 4-R7. 지시 밖 1줄 `(?:Sync)?` — 필요·무해 → 통과 범위 (증거 `r16-fail-closed.txt` §2)
옛/새 정규식을 같은 코드에 대고 비교: `Deno.writeTextFileSync("app/x","")` old=**False** new=True. 옛 패턴 `Deno\.writeTextFile\s*\(` 은 `Sync` 앞에서 끊겨 R-14-16 의 핵심 쓰기 API 를 잡지 못한다 → 이 1줄 없이는 서브명령 처리를 고쳐도 V14-3 이 allow 로 남으므로 **R-14-16 을 닫는 데 필요**하다. `(?:Sync)?` 는 Deno 두 이름에만 붙고 다른 대안은 글자 그대로, `readTextFileSync` 는 매칭되지 않으며 라이브 20건 회귀 0 → **무해**. 참고(소견 아님): `Deno.writeFileSync` 는 옛 패턴에서도 `writeFileSync` 대안으로 이미 잡혔다(old=True) — `FIX-014.md` 125행 "`Deno.writeTextFileSync`·`Deno.writeFileSync` 를 놓치던 것" 은 앞의 것만 맞다. 동작 영향 없음.

### 4-R8. 후속 후보 표 (기록용, [필수] 아님 — 사용자 결정 2026-10-11 20:35 · 원칙8) (증거 `r16-variants.txt` "## 후속 탐색")

| # | 재현 명령 | 실제 | 원인 추정 · 비고 |
|---|---|---|---|
| R-14-18 (deno 인스턴스, 재확인) | `deno run - <<EOF` ␤ `$(cat /tmp/f.ts)` ␤ `EOF` (#32) · `node <<EOF $(cat f)`(Q12) | allow | `_stdin_code_list`(1151~1164행)가 `frag.heredoc_dyn` 을 보지 않음. 3차 R-14-18 그대로 — deno 도 같은 함수를 타므로 같이 열려 있다. `heredoc_dyn` 이면 Deny 한 줄로 닫힌다(R-14-17 cmd_python 도 동일). |
| **R-14-19 (신규)** deno/bun 고유 옵션이 node 표로 해석됨 | `printf W \| deno run -c deno.json -`(Q1) · `deno run --check -`(Q2) · `deno run --config deno.json -`(Q3) · `deno run --import-map m.json -`(Q4) · `deno eval --ext ts "W"`(Q5) · `bun run -c bunfig.toml -`(Q6) · `bun run --cwd app -`(Q7) | allow | `_interp_codes` 1181행의 "정보 출력·문법 검사" 표 `("-v","--version","-h","--help","-c","--check")` 와 1183행 `value_opts`(node 의 `-r`·`--require`…)가 deno/bun 에도 그대로 쓰인다. deno 의 `-c`=`--config <file>`, `--check`=타입검사 **플래그**라 `-c`/`--check` 를 만나면 1182행에서 heredoc 만 돌려주고 끝난다(Q1·Q2). `--config x`·`--import-map x`·`--cwd x`(띄어쓴 값옵션)는 값옵션 표에 없어 값 `x` 가 "스크립트 파일" 위치인수로 보여 1195행 조기 반환(Q3·Q4·Q7), `deno eval --ext ts "W"` 는 값 `ts` 가 코드로 오인되고 진짜 코드 `"W"` 는 검사되지 않는다(Q5). `=` 붙인 형태(`--ext=ts`·`--allow-write=app`)는 deny(#6·#10). **R-14-16 과 같은 함수의 옵션 표 문제라 비용이 작다 — 후속 FIX 1순위 권고.** 닫는 방향: `_cmd_runtime` 에 deno/bun 전용 `info_flags`·`value_opts` 를 넘기고 1181행 표를 인자로 바꾼다. |
| **R-14-20 (신규)** 서브명령·바이너리 이름 밖 | `printf W \| deno repl`(Q8) · `printf BW \| bunx -`(Q10) | allow | `repl` 이 `subcmds` 에 없어 위치인수(스크립트)로 보고 조기 반환; deno repl 은 파이프 stdin 을 평가한다. `bunx` 는 `cmd_bunx` 핸들러가 없어 일반 명령으로 통과. 시스템에 deno/bun 이 없으면 실해는 없지만 문서 범위(118행 deno·bun)와 어긋난다. |
| 참고(보수 거부, 소견 아님) | `cat /tmp/f \| deno run -r app/x.ts`(Q9) | deny | node 의 `-r <module>` 값옵션 표가 deno 의 `-r`(`--reload`, 플래그)에 적용돼 `app/x.ts` 를 값으로 삼키고 stdin 코드 판정으로 떨어짐 → 파이프 앞이 리터럴이 아니라 거부. 오탐이지만 실제 작업 흐름에 없는 조합이라 기록만. R-14-19 와 같은 표를 고치면 함께 사라진다. |
| R-14-5~8·15·17 | (3차 3-R8 표 그대로) | allow | 변동 없음 — 별도 FIX(사용자 결정). |

### 통과 사유 (요약)
3차 보류 사유 R-14-16(`deno run -`·`bun run -`·`deno eval` stdin 코드)이 직접 3건 + 명시 변형 37건에서 **전부 deny** 로 닫혔고, deno/bun 정상 사용·작업 흐름 46건 **오탐 0**, test-guards **실패 0**, 2·3차 통과 항목 **회귀 0**, 지시 밖 `(?:Sync)?` 1줄은 **필요·무해**, fail-closed **deny**. 남은 allow(동적 heredoc 본문 #32, R-14-19·20)는 판정 규칙상 [필수]가 아니며 후속 후보로 기록했다. `FIX-014.md` `검증:` 줄을 통과로 채웠다. Windows 는 푸시 뒤 CI windows job 이 본다.

증거: `evidence/20261011-verifier-fix014-r16-{variants,drive5-src,drivers,test-guards,fail-closed}.txt`.
