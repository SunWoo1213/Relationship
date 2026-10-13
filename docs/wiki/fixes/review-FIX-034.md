# review-FIX-034 · 증거 저장 전용 통로 `save_evidence.py` 커밋 전 리뷰

검토자: verifier (fable) · 2026-10-13 · 기준 HEAD `977f2ee` + 작업 트리 미커밋 diff(신규 `.claude/scripts/save_evidence.py` + 대상 9파일) · Refs: FIX-034 FIX-014 FIX-032 FIX-033 FIX-008 R-U3-3 R-U5-3 L-002 원칙8

**결과: 통과 (재검증 2차 2026-10-13 — 아래 "재검증(2차)" 절. [필수] 0, 열린 [권고] 4: R-34-7⑤·R-34-8·R-34-10·R-34-11).**

**결과(1차): 보류 — [필수] 3건(R-34-1·2·3), [권고] 6건(R-34-4~9).** 수정안 1~5 의 명세는 거의 전부 코드·시험·문서로 충족됐고(§3.1), PATTERNS 9개는 `secret-guard.sh` 와 정규화 뒤 문자 단위로 동일하며(§2 #2), test-guards 전체 PASS·저장소 무접촉이고(§2 #1), 구현자 변이 m1~m3 는 재현됐다(§2 #5). 그러나 **이 통로는 `--` 뒤 명령을 따옴표로 묶는 통상 사용법에서 `bash -c` 래퍼가 되며 `bash-write-guard` 는 그 안을 보지 않는다** — `python3 .claude/scripts/save_evidence.py fixes x -- 'echo x > app/y.py'` 는 가드 allow 이고, 가짜 저장소 사본에서 실제로 `app/y.py` 가 생겼다(§2 #4, R-34-1). `security.md` §4b 가 이번 FIX 로 적은 "쓰기 범위는 `docs/wiki/**/evidence/` 로 한정" 은 `--root` 로도 깨진다(`--root <저장소> app` → `app/evidence/…`, R-34-3). 그리고 `--append` 의 glob `*-<이름>.txt` 가 다른 이름의 접미사와 겹쳐 **다른 단위의 기존 증거 파일(추적 파일)에 덧붙인다**(R-34-2). 셋 다 코드 몇 줄로 닫히지만, 통로의 전제("가드가 막지 않는 유일한 의도된 쓰기, 범위 한정, 증거 무결성")에 직접 닿는 것이라 [필수]다. 코드·훅·계획·카드는 고치지 않았고 `FIX-034.md` 의 `검증:` 줄만 보류로 썼다.

## 1. 본 것

- `docs/wiki/fixes/FIX-034.md` 증상·원인·수정안 1~5·기획서 정합성·`계획 점검: 통과`·`승인:` 줄(근거 문서).
- 신규 `.claude/scripts/save_evidence.py` 전체(207행). `git diff -- .claude/scripts/test-guards.sh .claude/hooks/secret-guard.sh .claude/agents/ .claude/skills/devlog/SKILL.md docs/wiki/security.md docs/wiki/verification.md` 전체.
- 구현자 증거 8개 `fixes/evidence/20261013-144*-fix034-*.txt`(전부 새 통로 형식, 머리줄 5개). 구현자 변이 자료 스크래치패드 `mut/`(control.py·m1~m3·section.sh·body.sh).
- 배경: `review-u5-chat.md` §6(R-U5-3 대책 (라)), `bash_write_check.py` 모듈 docstring·`cmd_python`(1102~1117행)·`_shell_codes`(576행), `bash-write-guard.sh`, `secret-guard.sh` PATTERNS, `security.md` §1·§3·§4b, `verification.md`, `test-guards.sh` 1~45행·930~992행, `.github/workflows/tests.yml` 110~151행(windows job 의 test-guards 단계), `registry.md`(하네스 스크립트 행 존재 여부).
- `HANDOFF.md`·`journal.md`·`registry.md` diff 는 메인 세션 기록이라 판정 대상에서 뺐다(registry 에 save_evidence 행이 없는 것만 확인).

## 2. 내가 직접 실행한 것 (전부 새 통로 `python3 .claude/scripts/save_evidence.py fixes verifier-fix034-<이름> -- bash <스크래치패드>/v034/<이름>.sh`, 수치는 구현자 보고에서 옮기지 않았다)

| # | 확인 | 결과 | 증거 |
|---|---|---|---|
| 1 | `bash .claude/scripts/test-guards.sh` 전체 + 실행 전후 `git status --short` 대조 | 종료 0 · `== 결과: 실패 0 ==` · save_evidence 절 ①~⑥ 전부 ok · **git status 실행 전후 동일** · `$TMPDIR` 에 `fixes/evidence` 잔여 없음 | `fixes/evidence/20261013-1451-verifier-fix034-judge.txt`(415행, 381~388행 절, 413행 판정) |
| 2 | PATTERNS 대조: `secret-guard.sh` 9개를 `[[:space:]]`→`\s` 로만 정규화한 목록 vs `import save_evidence` 의 `SECRET_PATTERNS` | **diff rc=0, 9 vs 9** — 방언 차이 외 문자 단위 동일. `secret-guard.sh` diff 는 주석 1줄뿐 | `…-1502-verifier-fix034-diff.txt` §A·§B |
| 3 | 범위: `git diff --quiet -- bash_write_check.py app alembic web tests` · `git diff --stat` · 문서 7곳 `grep -c save_evidence.py` · ruff(`.venv/bin/ruff` 와 `python3 -m ruff` 둘 다) · 구현자 `mut/body.sh` vs test-guards 930~992행 · 구현자 두 test-guards 증거 본문 대조 | 가드 본체·제품 코드 무변경(rc 0) · 7파일 모두 ≥1(1·1·1·2·4·1·1) · ruff 두 방식 모두 통과 · body.sh 는 `SE=` 한 줄만 다름(구현자 변이는 저장소 절 그대로) · 구현자 증거 2벌은 `session-start` 바이트 수(8545/8867) 한 줄만 다름 · **registry.md 에 save_evidence 행 없음(grep rc=1)** · **verification.md 63·86행에 옛 "Read → Write" 지시 잔존** | 같은 파일 §B-1·§C·§D·§D-1·§E·§F·§G·§J |
| 4 | 가드 관계: PreToolUse JSON 을 `bash-write-guard.sh` 에 직접 입력 11건 + 가짜 저장소 사본(스크래치패드 `v034/fakerepo`, `REPO_ROOT` 가 사본을 가리키도록 스크립트를 복사)에서 실제 실행 | 정상 호출 3건 allow · `-- echo x > app/y.py`(따옴표 없음) **deny** · `-- printf x \| tee app/y.py` deny · **따옴표로 묶은 안쪽 명령 4건(`'echo x > app/y.py'`·`"printf x \| tee app/y.py"`·`'sed -i …'`·`'cp /tmp/x app/x.py'`) 전부 allow** · 대조 `bash -c 'echo x > app/y.py'` deny·`xargs -I{} bash -c {}` deny · 사본 실행: `… -- 'echo x > app/y.py'` rc=0, **`fakerepo/app/y.py` 생성(내용 `x`)** | `…-1502-verifier-fix034-guard.txt` §A~§D |
| 5 | 변이 6종(스크래치패드 사본, test-guards 절 930~992행을 떼어 `SE_UNDER_TEST` 로 지정, 저장소 무수정) | control 실패 0 · **ma** 이름 검사 제거 → ④ XX(검출) · **mb** `stderr=PIPE` → **실패 0(살아남음)**, 추가 확인에서 `err` 줄 소실 · **mc** exit 2→0 → ③ XX(검출) · **md** 머리줄만 검사 → **살아남음**, 추가 확인에서 본문 비밀 통과(rc 0·파일 1) · **me** 본문만 검사 → **살아남음** · **mf** 본문 100바이트로 자르기 → **살아남음** | `…-1502-verifier-fix034-mutation.txt` |
| 6 | 우회 시도 ①~⑥ + 추가 ⑦~⑬ (`--root <스크래치패드>/v034/root`, 가짜 비밀은 전부 실행 시점 조합·값 미출력) | 아래 §3.2 표 | `…-1502-verifier-fix034-bypass.txt` |

부수 관찰: 새 통로로 5개 증거를 남기는 동안 Write 로 옮겨 적은 것은 0 이고 bash-write-guard 에 한 번도 막히지 않았다 — FIX-034 가 없애려던 수작업·요약 압력은 실제로 사라진다. (#1 의 증거 파일명 시각 `1451` 은 명령 시작 시각이고 저장은 15:01 — 내 judge.sh 의 `find $TMPDIR` 가 느렸던 탓, 스크립트 결함 아님.)

## 3. 판정

### 3.1 수정안 1~5 대조 (위임 프롬프트 1)

| 항목 | 명세(FIX-034.md 행) | 코드·시험·문서 | 판정 |
|---|---|---|---|
| 인자 `<대상> <이름> [--append] [--note] -- <명령…>` | 17 | `main()` 114~125행, `--` 앞뒤 분리 | ✓ (+`--root`) |
| 대상 검증: 패키지 id 디렉터리 존재 또는 `fixes`, 그 밖 exit 3 | 18 | `_evidence_dir` 88~96행; ⑥ `P99-nope` rc 3·파일 0 | ✓ — 단 `.` 이 통과(§3.2 ⑤-h, R-34-3 에 포함) |
| 이름 `[A-Za-z0-9._-]+`·`..` 거부 exit 3 | 19 | `NAME_RE` 60행·`_valid_token` 84행; ⑤-a~e 전부 rc 3 | ✓ |
| 파일명 `<ts>-<이름>.txt` · `--append` 는 같은 이름 최신 파일 끝에 구분선 | 20 | 185~199행; test ⑤ 구분선 2개 | 형식 ✓ · **glob `*-{name}.txt` 접미사 겹침 — R-34-2** |
| `bash -c`, cwd 저장소 루트, env 3개, `stderr=STDOUT` | 21 | 149~160행; ⑨ `out1/err1/out2` 순서 보존 | ✓ — stderr 수집은 **시험 없음**(mb 생존, R-34-4) |
| 머리줄 5개 + `# ---` + 전체, ANSI 정규식 그대로, 자르지 않음, 8 MB 머리줄 | 22·25 | 59·164~176행; ⑪ 9,000,000 bytes 그대로 + `# 크기:` · ⑫ 빈 출력도 6줄 파일 | ✓ — "자르지 않음" **시험 없음**(mf 생존, R-34-4) |
| 비밀 검사 9개, 걸리면 파일 미생성·줄 번호·패턴 이름만·exit 2 | 23 | 47~57·99~106·178~183행; ①②③④-a rc 2·파일 0·stderr 에 값 없음 | ✓ — 머리줄은 ANSI 미제거(R-34-5) |
| 종료 코드 = 명령 exit, 2/3 구분, stderr 에 저장 경로 | 24 | 161·201~202행; test ② rc 7, ⑩ SIGTERM → 143 | ✓ |
| `--root` 테스트용, `<root>/<대상>` 존재 검사 | 26 | 90~92행; test-guards 가 `mktemp -d` 아래서 돌림 | 명세대로 ✓ — **범위 한정과 모순, R-34-3** |
| test-guards 5경우(+⑥) | 27 | 930~992행, 전부 PASS, 저장소 무접촉(#1) | ✓ |
| 문서 7곳 | 28 | #3 grep 7/7 | ✓ — 잔존 문구·`python3` 고정은 R-34-7 |
| 판정 명령 4개 | 29 | test-guards 실패 0 · selftest 파일 `# exit: 0`/`FIX-034-ok` · grep 7/7 · ruff 통과 — CI windows job 은 커밋 뒤 첫 실행 | ✓ (CI 미실행) |
| `bash_write_check.py` 무변경·제품 코드 무변경·PostToolUse 없음·기존 증거 형식 유지 | 30 | #3 `git diff --quiet` rc 0; `.claude/hooks/` 변경은 secret-guard 주석 1줄 | ✓ |

### 3.2 보안 — 우회 시도 (위임 프롬프트 2, `…-bypass.txt`)

| # | 시도 | 기대 | 실측 | 판정 |
|---|---|---|---|---|
| ① | 비밀이 `# 명령:` 줄에만(`-- "true # <sk-proj-30자>"`, 본문 없음) | rc 2·파일 0 | rc 2·파일 0·`줄 1: openai-anthropic-key` | ✓ 구현자 판단 ⑥ 작동 |
| ② | `--note <비밀>` | rc 2·파일 0 | rc 2·파일 0·`줄 6` | ✓ |
| ③ | 경계: `sk-proj-` 뒤 18/19/23/24자를 **명령 안에서 조합**(머리줄엔 `sk-proj-%s` 만) | 위임 프롬프트는 "23자 미검출·24자 검출" 을 기대했으나 정규식 `sk-(proj-|ant-)?[A-Za-z0-9_-]{24,}` 은 `proj-` 가 클래스 문자라 선택 그룹을 건너뛰어도 맞는다 → 실제 경계는 **`sk-` 뒤 24자 = `sk-proj-` 뒤 19자** | 18자 rc 0·파일 1 / 19·23·24자 rc 2. 같은 문자열 `grep -E`(secret-guard 패턴): 18 rc1 / 19·23·24 rc0. `secret-guard.sh` JSON 입력: 18 allow / 19·23·24 deny | ✓ 세 구현(python·grep -E·훅) 경계 일치 |
| ④-a | 본문에 `sk-\033[0mproj-<30자>` | rc 2(ANSI 제거 뒤 검사) | rc 2·파일 0 | ✓ |
| ④-b | `--note` 에 ANSI 로 쪼갠 비밀 | rc 2 | **rc 0·파일 생성, ESC 1바이트·`proj-` 줄 포함** | ✗ R-34-5 |
| ④-c | 명령 문자열(주석)에 ANSI 로 쪼갠 비밀, 본문 없음 | rc 2 | **rc 0·파일 생성** | ✗ R-34-5 |
| ⑤-a~e | 이름 `../x`·`/private/tmp/x`·`a/b`·`..`·`a..b` | rc 3·파일 0 | 전부 rc 3·파일 0 | ✓ |
| ⑤-f·g | 대상 `../fixes`·절대 경로 | rc 3 | rc 3 | ✓ |
| ⑤-h | 대상 `.` (`--root` 와) | rc 3 | **rc 0 → `<root>/evidence/…` 생성** (pathlib 가 `.` 을 접음; `--root` 없이도 `docs/wiki/packages/evidence/` 가 됨) | ✗ R-34-3 |
| ⑤-i | 대상이 심볼릭 링크(`<root>/link → …/elsewhere`) | — | 링크를 따라 `elsewhere/evidence/` 에 씀 | 관찰(저장소 안 링크는 에이전트가 만들 수 없음 — `ln` 은 가드가 거부) |
| ⑤-j·k | `--root <저장소> app` · `--root . app`(가짜 저장소 사본) | 거부되어야 §4b 와 맞음 | **rc 0 → `app/evidence/<ts>-x.txt` 생성**(두 방식 모두) | ✗ R-34-3 |
| ⑥ | `--root` 없이 `P99-nope` | rc 3·디렉터리 미생성 | rc 3·`docs/wiki/packages/P99-nope` 없음·`git status -- docs/wiki/packages` 빈 출력 | ✓ |
| ⑦ | `20260101-0000-u5-mutation.txt` 가 있을 때 `fixes mutation --append` | 새 파일 `<ts>-mutation.txt` | **u5 파일에 덧붙임(파일 1개, `appended` 포함)**. 실제 P8-frontend evidence 에서 `*-mutation.txt` 정렬 마지막 = `20261013-1354-verifier-u5-mutation.txt`(추적 파일) | ✗ R-34-2 |
| ⑧ | 같은 분 같은 이름 2회 | 2회째 rc 3(구현자 판단 ②) | rc 3 — **2회째 명령은 이미 실행됐고 그 출력은 어디에도 없음** | R-34-6 |
| ⑨~⑫ | stderr 순서 · SIGTERM · 8 MB · 빈 출력 | §3.1 | 전부 명세대로 | ✓ |
| ⑬ | `-- printf '%s|' 'a b' c`(따옴표 없이) | 공백 결합 명세대로 따옴표 소실 | `# 명령: printf %s| a b c`, rc 127 | 명세대로 — 문서에 "한 덩어리로 따옴표" 안내 필요(R-34-7) |

### 3.3 가드와의 관계 (위임 프롬프트 3, `…-guard.txt`)

- 통과 근거(코드): `bash_write_check.py` `frag()` 963행 `re.fullmatch(r"python[\d.]*|py|pypy[\d.]*", name)` → `cmd_python()` 1102행. 첫 인자 `.claude/scripts/save_evidence.py` 가 `-` 로 시작하지 않으므로 1115~1117행 `script = True; break` → `codes` 비어 있고 `script` 참이라 검사 없이 반환. **`--` 뒤 인자는 어디서도 읽지 않는다.** 이것이 docstring 의 "프로그램 실행(`python x.py`)은 막지 않는다" 분기다.
- 따옴표 없는 `-- echo x > app/y.py` 는 셸 문법상 `>` 가 python3 프로세스의 리다이렉트라 `frag.redirs` 에서 잡힌다(B-1 deny). 그러나 통상 사용법은 명세(21행 "`cd web && npm test -- --run` 같은 한 줄")대로 **따옴표로 묶는 것**이고, 그러면 C-1~C-4 전부 allow 다. 같은 코드를 `bash -c '…'` 로 쓰면 `_shell_codes()` 가 리터럴을 재귀 분석해 deny(C-ref), `xargs -I{} bash -c {}` 도 deny(R-14-12) — 즉 가드는 "호출 자리의 셸 코드" 를 보도록 여러 차례 보강됐는데(R-14-1·3·12·13) `save_evidence.py` 가 같은 모양의 구멍을 다시 연다. 가짜 저장소 사본 실행에서 `app/y.py` 가 실제로 생겼다(§2 #4 D).
- 수정안 5 "가드 규칙 무변경 — 이 스크립트는 '프로그램이 쓰는 것' 범주라 이미 통과한다" 는 사실이지만, 그 범주의 다른 것들(pytest·`bash x.sh`)은 **저장소 안 정적 파일**(Write 툴·stage-gate 를 거쳐야 생김)을 실행하는 반면 이 통로는 **호출 자리에서 임의 셸 문자열**을 받는다. 그래서 R-34-1.

### 3.4 구현자 계획 밖 판단 8개 (위임 프롬프트 4)

| # | 판단 | 계획·보안 카드와 모순? | 비고 |
|---|---|---|---|
| ① | test-guards ⑥ ANSI 시험 추가 | 없음 — 명세 22행의 정규식을 시험으로 고정. 구현자 m2 를 이 시험이 잡음 | 기록으로 충분 |
| ② | 같은 분 같은 이름 덮어쓰기 거부 exit 3 | 없음 — 증거 보존 방향. 단 검사 시점이 명령 실행 뒤라 출력 소실(⑧) | R-34-6 |
| ③ | `--append` 첫 호출도 구분선 | 없음 — 파일이 빈 줄 + `# ===== append` 로 시작(구현자 `-mutation.txt` 1~2행). `verification.md` 18행 "머리줄 5개가 있는 파일" 은 여전히 참 | 기록으로 충분 |
| ④ | `--note` 를 `# 메모:` 머리줄로 | 없음 — 6번째 선택 머리줄. 비밀 검사 대상에 포함(②) | 기록으로 충분. 단 ANSI 미제거(R-34-5) |
| ⑤ | verifier.md 는 (c) 줄 대신 verify-plan/verify-impl 문구 변경 | 없음 — verifier.md 에는 (c) 줄이 애초에 없었다(R-33-8). 24·32행이 새 통로를 지시 | 기록으로 충분 |
| ⑥ | 비밀 검사를 머리줄에도 | 없음 — §1 "로그에 키를 남기지 않는다" 강화(①·② 실측) | **시험 없음**(me 생존) — R-34-4 |
| ⑦ | 시그널 종료 128+n | 없음 — ⑩ SIGTERM → 143 | 기록으로 충분 |
| ⑧ | 테스트 ③ 가짜 비밀을 실행 시점에 조합 | 없음 — test-guards 6행 관례 그대로 | 단 조합한 값이 **명령 문자열에 들어가** ③ 이 본문 검사가 아니라 머리줄 검사를 시험하게 됐다(md 생존) — R-34-4 |

### 3.5 변이 (위임 프롬프트 5, `…-mutation.txt`)

| 변이 | 기대 | 결과 | 판정 |
|---|---|---|---|
| ma `if not _valid_token(a.name)` → `if False` | ④ 실패 | ④ XX(rc 1, `…/20261013-1502-../x.txt` 열기 실패) | 검출 |
| mb `stderr=STDOUT` → `PIPE` | 어떤 시험이든 실패 | **실패 0** — 추가 확인: 본문 `out` 만, `err` 소실 | 테스트 공백 |
| mc `return 2` → `return 0` | ③ 실패 | ③ XX | 검출 |
| md 머리줄만 검사 | ③ 실패 | **실패 0** — 본문 비밀 rc 0·파일 1 | 테스트 공백 |
| me 본문만 검사 | ③ 또는 머리줄 시험 실패 | **실패 0** | 테스트 공백(구현자 판단 ⑥ 미시험) |
| mf 본문 `[:100]` 자르기 | 실패 | **실패 0** | 테스트 공백 — FIX 의 핵심 명세 "자르지 않음" 이 시험되지 않음 |
| (구현자) m1 패턴 비움 / m2 ANSI 미제거 / m3 exit 미전달 | ③ / ⑥ / ② 실패 | 구현자 보고와 동일(③ XX / ⑥ XX / ② XX) — §2 #3 에서 변이 본문이 저장소 절과 같음을 확인 | 검출 |

### 3.6 Mac·Windows (위임 프롬프트 6)

- `_shell()` 110행 `shutil.which("bash") or shutil.which("sh")`: Claude Code Bash 툴(Git Bash) 안에서는 Git 의 `usr/bin` 이 PATH 앞이라 Git Bash 로 풀린다. PowerShell·cmd 에서 직접 부르면 `C:\Windows\System32\bash.exe`(WSL 런처)가 먼저일 수 있다 — 구현자 보고대로. WSL 이면 cwd 가 `/mnt/c/…` 로 바뀌고 안쪽 python 이 리눅스 것이 된다. 방어(권고): `BASH`/`EXEPATH` 환경변수나 `Git/bin/bash.exe` 후보를 먼저 보고 `System32\bash.exe` 는 제외(R-34-8).
- CRLF: 본문은 bytes 그대로(`wb`), 머리줄은 `\n` — Windows 명령의 `\r\n` 은 보존된다. 비밀 검사는 `\n` 분할이라 `\r` 이 줄 끝에 남아도 `\s` 가 흡수. `pathlib`·`subprocess` 모두 양쪽 공용.
- 인터프리터 이름: test-guards 는 `$HOOK_PY`(Windows 는 `python`) 로 부르지만 **문서 7곳과 test-guards 3행은 `python3` 고정** — FIX-008 이 적은 대로 Windows 의 `python3` 는 Store 스텁일 수 있다(R-34-7).
- CI windows job(`tests.yml` 151행 `bash .claude/scripts/test-guards.sh`, Git Bash 고정)으로 확인할 것: ① save_evidence 절 ①~⑥ ok ② (권고 반영 시) `_shell()` 이 고른 경로가 Git Bash 인지 한 줄 출력. 이 리뷰는 Mac 에서만 실측했다.

### 3.7 test-guards 저장소 무접촉 (위임 프롬프트 7)
§2 #1 — `git status --short` 실행 전후 동일(413행), `--root` 임시 디렉터리는 `rm -rf "$SE_T"` 로 정리되어 `$TMPDIR` 잔여 없음. FIX-032 관례 준수.

## 4. 소견

### [필수]
- **R-34-1 · 따옴표로 묶은 안쪽 명령이 가드 검사 없이 `bash -c` 로 실행된다 — 통로가 Bash 쓰기 우회로가 된다.** 근거: `…-guard.txt` C-1~C-4 allow(`'echo x > app/y.py'`·`"printf x | tee app/y.py"`·`'sed -i …'`·`'cp /tmp/x app/x.py'`), 대조 `bash -c '…'` deny, 가짜 저장소 사본에서 `app/y.py` 생성(§2 #4 D); `bash_write_check.py` 1115~1117행(스크립트 인자 → 검사 없음); `security.md` §4b 새 문장 "유일한 의도된 Bash 경유 쓰기이며, 쓰기 범위는 `docs/wiki/**/evidence/` 로 한정". 해결 방향(구현 에이전트 몫 — 둘 중 하나, 선택은 사용자): (a) **가드 무변경(수정안 5 유지)** — `save_evidence.py` 가 명령을 실행하기 전에 `bash_write_check.py` 를 같은 입력 형식(`{"tool_input":{"command": <결합한 명령>}}`)으로 서브프로세스 호출해 rc≠0 이면 exit 3 으로 거부(사유를 stderr 에 그대로). 임시 영역·프로그램 실행 허용 규칙이 그대로 적용되므로 `pytest`·`npm test`·`bash test-guards.sh` 는 계속 통과한다. (b) `bash_write_check.py` 의 `cmd_python` 에서 스크립트가 `save_evidence.py` 면 `--` 뒤 인자를 `_shell_codes` 와 같은 급의 셸 코드로 재귀 분석 — 수정안 5 를 바꾸므로 FIX-034.md 갱신 필요. 완료 판정: test-guards 에 ⑦ `… fixes t7 --root "$SE_T" -- 'echo x > app/y.py'` → rc 3·`app/y.py` 미생성·evidence 파일 0, 그리고 (b) 라면 bash-write-guard 절에 `mk "python3 .claude/scripts/save_evidence.py fixes x -- 'echo x > app/y.py'"` deny 1건. 재검증은 `…-guard.txt` 의 11건을 같은 입력으로 다시 돌려 C-1~C-4 가 deny(또는 실행 거부)인지 본다.
- **R-34-2 · `--append` 가 다른 이름의 접미사와 겹쳐 다른 단위의 기존 증거(추적 파일)에 덧붙인다.** 근거: 188행 `ev_dir.glob(f"*-{a.name}.txt")`; `…-bypass.txt` ⑦ — `20260101-0000-u5-mutation.txt` 가 있을 때 `fixes mutation --append` 가 새 파일을 만들지 않고 그 파일에 `appended` 를 덧붙임; 실제 `P8-frontend/evidence` 에서 같은 glob 의 정렬 마지막은 `20261013-1354-verifier-u5-mutation.txt`(커밋된 verifier 증거). 짧은 이름(`mutation`·`test`·`judge`)은 에이전트 정의가 권하는 바로 그 사용법이다. 해결: 후보를 `re.fullmatch(r"\d{8}-\d{4}-" + re.escape(a.name) + r"\.txt", f.name)` 로 거르고 정렬. 완료 판정: test-guards 에 ⑧ 기존 `…-u5-t8.txt` 를 만든 뒤 `t8 --append` → 파일 2개·u5 파일 바이트 불변.
- **R-34-3 · `--root` 와 대상 `.` 이 "쓰기 범위 `docs/wiki/**/evidence/` 한정" 을 깨뜨린다.** 근거: `…-bypass.txt` ⑤-j·k — `--root <저장소> app`·`--root . app`(사본) 으로 `app/evidence/<ts>-x.txt` 생성, ⑤-h — 대상 `.` 으로 `<root>/evidence/` 생성(`--root` 없이는 `docs/wiki/packages/evidence/`); `security.md` §4b 58행·`FIX-034.md` 33행 "쓰기 범위는 `docs/wiki/**/evidence/` 로 한정". `--root` 는 명세(26행)가 허용한 것이지만 명세 자신이 33행과 모순이다. 해결: `--root` 는 `Path(a.root).resolve()` 가 저장소 루트 밖이고 임시 영역(`tempfile.gettempdir()`·`$TMPDIR`·`/tmp`·스크래치패드) 아래일 때만 허용, 아니면 exit 3; 대상은 `.`·`..` 를 거부(`_valid_token` 에 `s in (".", "..")` 추가). test-guards 의 `SE_T` 는 `mktemp -d` 라 그대로 통과한다. 완료 판정: test-guards 에 ⑨ `--root "$ROOT" app` → rc 3·`app/evidence` 미생성, ⑩ 대상 `.` → rc 3. (심볼릭 링크 ⑤-i 는 저장소 안에서 에이전트가 만들 수 없어 소견 아님.)

### [권고]
- **R-34-4 · 테스트 공백 4건(변이 mb·md·me·mf 생존).** `…-mutation.txt`. 추가할 시험: (가) `-- 'echo out; echo err >&2'` → 본문에 `err` 포함(stderr 수집) (나) ③ 의 비밀을 `-- "printf 'sk-proj-%s\n' \"\$(printf 'b%.0s' \$(seq 1 30))\""` 처럼 **명령 안에서 조합**해 본문에만 나타나게(본문 검사) + 머리줄만 비밀인 경우(`-- "true # $SE_FAKE"`) 하나 더(머리줄 검사, 구현자 판단 ⑥ 고정) (다) `-- 'seq 1 2000'` → 본문 2000줄·마지막 줄 `2000`(자르지 않음 — FIX 의 핵심 명세). 네 줄이면 mb·md·me·mf 가 모두 잡힌다.
- **R-34-5 · 머리줄(명령 문자열·`--note`)은 ANSI 를 지우지 않아 ANSI 로 쪼갠 문자열이 검사를 지나 파일에 ESC 와 함께 들어간다.** `…-bypass.txt` ④-b·④-c(rc 0, ESC 1바이트). 162행은 본문만 `ANSI_RE.sub`. 해결: `head_bytes` 도 같은 정규식으로 지우거나(간단), 인자에 `\x1b` 가 있으면 exit 3. 고의 회피 시나리오라 권고.
- **R-34-6 · 같은 분 같은 이름 충돌 검사가 명령 실행 뒤라 두 번째 명령의 출력이 사라진다.** `…-bypass.txt` ⑧(`second-output-lost` 를 담은 파일 0). `stamp` 는 `started` 에서 나오므로 194~197행의 존재 검사를 152행 `subprocess.run` 앞으로 옮기면 된다(긴 테스트를 돌린 뒤 거부당하는 일이 없어진다).
- **R-34-7 · 문서.** ① `verification.md` 63행(루프 1단계 "출력을 Write 툴로 … Read → Write")·86행(변이 시험 방법 "출력은 `>` 로 스크래치패드에 받은 뒤 Read → Write 로 evidence 에 전체를 옮긴다")이 같은 문서 18행의 새 규칙("Write 로 옮겨 적지 않는다")과 모순 — `…-diff.txt` §D-1. ② 7곳 모두 `python3` 고정(§D-2) — FIX-008 대로 Windows 는 `python` 이 표준이고 `python3` 는 Store 스텁일 수 있다. `python3`(Mac)·`python`(Windows) 또는 "훅과 같은 `_py.sh` 탐지" 한 구절. ③ `registry.md` 에 save_evidence 행 없음(§J; test-guards·bash_write_check 등은 등록돼 있음 — 메인 세션 몫). ④ `FIX-034.md` 수정안 2 "4경우 … 추가 ⑤" ↔ 실제 6경우, 결과절 비어 있음(커밋 시 메인 세션). ⑤ 공백 결합(⑬)으로 따옴표가 사라지므로 에이전트 정의의 사용법 줄에 "명령은 한 덩어리로 따옴표로 묶는다" 를 적는 편이 안전하다.
- **R-34-8 · Windows 에서 `shutil.which("bash")` 가 WSL 런처를 고를 수 있다**(§3.6, 구현자 보고와 같음). 후보 순서를 `os.environ.get("BASH")` → Git Bash 경로(`EXEPATH`/`C:\Program Files\Git\bin\bash.exe`) → PATH 로 두고 `System32\bash.exe` 는 제외. CI windows job 첫 실행 결과로 현재 동작을 확인한다.
- **R-34-9 · 구현자 변이 증거 형식.** `20261013-1441-fix034-mutation.txt` 는 전부 `--append` 라 첫 줄이 빈 줄·구분선으로 시작한다(판단 ③). 규칙 위반은 아니나 "첫 호출은 머리줄로 시작, 2회째부터 구분선" 이 읽기 쉽다 — 선택.

## 5. 결론

`검증:` 줄은 `검증: 보류 — verifier (fable) 2026-10-13, review-FIX-034.md ([필수] R-34-1·2·3)` 로 썼다. R-34-1 은 사용자 결정(가드 무변경 (a) vs 가드 보강 (b))이 먼저 필요하고, R-34-2·3 은 구현 에이전트가 바로 고칠 수 있다. 재검증은 ① `…-guard.txt` 11건 재입력(C-1~C-4 deny 또는 실행 거부) ② `…-bypass.txt` ⑤-h·⑤-j·⑤-k·⑦ 재실행(전부 rc 3 또는 새 파일 생성·기존 파일 불변) ③ `bash .claude/scripts/test-guards.sh` 실패 0(새 경우 ⑦~⑩ 포함) ④ 변이 mb·md·me·mf 재실행이 각각 XX 로 끝나는지(R-34-4 반영 시) — 넷으로 끝난다. R-34-5~9 는 사용자·메인 세션이 이번 커밋에 포함할지 정한다.

---

## 재검증(2차) (2026-10-13)

검토자: verifier (fable) · 기준 HEAD `977f2ee` + 재작업 1차 작업 트리(`save_evidence.py` 285행, test-guards 절 ①~⑬, 문서 7곳 + registry) · Refs: FIX-034 FIX-014 FIX-032 R-34-1 R-34-2 R-34-3 R-34-4 R-34-5 R-34-6 R-34-7

**재검증 결과: 통과.** 1차 [필수] R-34-1·2·3 이 전부 해소됐고(§R.3), 1차 §5 가 정한 재검증 ①~④ 를 모두 직접 실행해 통과했다(§R.2). [권고] R-34-4·5·6·7(①~④) 도 반영됐다. 새 [권고] 2건(R-34-10·11), 열린 [권고] R-34-7⑤·R-34-8. 코드·훅·계획·카드는 고치지 않았고 `FIX-034.md` 의 `검증:` 줄만 통과로 썼다.

### R.1 본 것
- `save_evidence.py` 재작업본 전체: `_valid_token` 86~88행(`.` 거부) · `_checked_root` 99~111행(절대 경로 + `resolve()` + 저장소 밖 + 임시 영역) · `_guard_denial` 114~137행(`sys.executable bash_write_check.py <REPO_ROOT>`, JSON stdin, rc≠0 거부, 예외·timeout 거부) · 209~216행(`command` 결합 → 가드 → 같은 문자열을 `bash -c`) · 218~226행(충돌 검사가 실행 앞) · 254행(머리줄 ANSI 제거) · 266~270행(`\d{8}-\d{4}-<이름>\.txt` fullmatch).
- test-guards diff(930~1062행 ①~⑬; ⑦ 실패 분기 `rm -f "$ROOT/app/y.py"`, ⑩ 실패 분기 `se_pre` 가드 뒤 `rm -rf "$ROOT/app/evidence"`), `security.md` §4b·`verification.md` 18·62~63·86행·registry 22행·`FIX-034.md` "재작업 1차" 절.
- 구현자 재작업 증거 `fixes/evidence/20261013-155*-fix034-rework-*.txt`(첫 test-guards 실행 1555 는 ⑦ XX → 1557·1558-final 실패 0; 변이 mb·md·me·mf·mg·mh·mi·mj 전부 XX) · 메인 세션 `20261013-1559-fix034-main-recheck2.txt`(실패 0).

### R.2 내가 직접 실행한 것 (전부 새 통로 `save_evidence.py fixes verifier-fix034-recheck-<이름> -- bash <스크래치패드>/v034/re-<이름>.sh`)

| # | 확인 | 결과 | 증거 |
|---|---|---|---|
| 1 | test-guards 전체 + 실행 전후 `git status --short` + `app/y.py`·`app/evidence` 전후 존재 | 종료 0 · `== 결과: 실패 0 ==` · 절 ①~⑬ 전부 ok(⑦ "가드 거부·실행 안 됨·종료 3", ⑬ 204960 bytes) · **git status 전후 동일** · `app/y.py`·`app/evidence` 전후 모두 없음 | `fixes/evidence/20261013-1612-verifier-fix034-recheck-judge.txt` 398~412·451~454행 |
| 2 | 1차 guard 11건을 바깥 훅에 재입력 | 1차와 동일(C-1~C-4 는 바깥 훅 allow — 바깥 훅은 무변경이므로 정상; 안쪽 가드가 담당) | `…-1612-verifier-fix034-recheck-guard.txt` §A |
| 3 | 안쪽 가드 vs 훅: 같은 안쪽 명령 9건을 (1) 훅에 직접 (2) `save_evidence --root <스크래치패드>` 로 | **훅 deny 7건(`>`·tee·`sed -i`·cp·치환 안 `>`·`"$X"` 판정 불가·python open) ↔ 전부 rc 3·파일 0·가드 메시지 그대로** · 훅 allow 2건(스크래치패드 `>`·`python3 -c "print(1)"`) ↔ 실행됨(`ran.txt` 생성)·파일 1 · `app/y.py` 미생성 | 같은 파일 §B |
| 4 | 글자 그대로 전달 — 공백 결합 변형 6건(`echo x '>' app/y.py`·`\>`·`"echo x" ">" "app/y.py"`·`'|' tee`·`'echo x >' app/y.py`·`'echo x' '; echo y > app/y.py'`) | **전부 rc 3·파일 0**, 사유 "리다이렉트 '>'/tee … 프로젝트 안". 209·212·230행이 같은 변수 `command` 를 쓰므로 가드 입력 = `bash -c` 입력 | 같은 파일 §C·§C-2 |
| 5 | 가드 실패 시 거부(가짜 저장소 사본): checker 없음 / `raise` / `sleep 60`(timeout 30) / rc 1·메시지 없음 | rc 3 ×4, stderr 에 각각 "can't open file"·Traceback·"가드를 실행하지 못해 거부한다(TimeoutExpired)"·"알 수 없는 이유로 거부했다(rc=1)" · evidence 0. 종료 코드 해석은 `bash-write-guard.sh` 41~46행(rc≠0 → deny, 빈 메시지면 대체 문구)과 동일 | 같은 파일 §D·§D-5 |
| 6 | R-34-3: 대상 `.`·`..`·`a/b` / `--root <가짜 저장소>`·`--root .` / 실제 저장소 `--root <저장소>/app` + `TMPDIR=<저장소>/app` / **심볼릭 링크 `<스크래치패드>/replink → 저장소`** / 링크가 임시 영역을 가리킴 / 상대 경로 / `$HOME/.cache`(임시 영역 아님) / 스크래치패드(정상) | 거부 rc 3: `.`·`..`·`a/b`·가짜 저장소·`.`·저장소/app(TMPDIR 무관)·**replink(`resolve()` 로 저장소 안 판정)**·상대·`$HOME` — 파일 0, `app/evidence` 없음 · 허용: 임시 영역 링크·스크래치패드 | `…-1613-verifier-fix034-recheck-bypass.txt` ⑤-h~⑤-o |
| 7 | R-34-2: `…-u5-mutation.txt` 가 있을 때 `mutation --append` / 정확히 같은 이름의 옛 파일 | 새 파일 `<ts>-mutation.txt` 생성, u5 파일 `ORIG` 불변 / 같은 이름 옛 파일에는 덧붙임(의도) | 같은 파일 ⑦·⑦-2 |
| 8 | R-34-5·6: `--note`·명령 문자열의 ANSI 쪼갠 비밀 / `--note` 의 무해한 색 코드 / 같은 분 충돌 2회째(`touch` 부작용으로 실행 여부 확인) | rc 2·파일 0 ×2 / 저장 파일 ESC 0·`# 메모: red` / **2회째 rc 3·명령 미실행**(`ran-dup.txt` 없음) | 같은 파일 ④·⑧ |
| 9 | 변이 12종(변이마다 가짜 저장소 사본 `<V>/repo-<m>/.claude/scripts/{save_evidence.py,bash_write_check.py}` + `app/`, 절 ①~⑬ 을 `ROOT=<사본>` 으로) | control 실패 0 · **mb→⑫ XX · md→⑪ XX · me→⑪ XX · mf→⑬ XX**(1차 공백 4건 전부 닫힘) · mg(가드 호출 제거)→⑦ XX · mh(glob 접미사)→⑨ XX · mi(`--root` 검사 제거)→⑩ XX · mj(`.` 허용)→⑩ XX · ml(가드 rc 무시)→⑦ XX · **mk(머리줄 ANSI 유지)→실패 0** · **mm(충돌 검사 제거)→실패 0**(직접 확인: 2회째 실행되고 덮어씀) · 모든 사본 `app/` 잔여 없음(⑦·⑩ 실패 분기 정리 작동) | `…-1613-verifier-fix034-recheck-mutation.txt` |
| 10 | 범위 | `git status --short -- app .claude/scripts/bash_write_check.py` 빈 출력(§E) · `app/evidence`·`docs/wiki/packages` 무변경 | `…-recheck-guard.txt` §E · `…-recheck-bypass.txt` 정리 |

### R.3 소견 상태

| 소견 | 1차 | 재검증 | 근거 |
|---|---|---|---|
| R-34-1 안쪽 명령 가드 미검사 | 필수 | **해소** | R.2 #3·#4·#5 — 훅과 같은 판정·같은 문자열·실패 시 거부; test-guards ⑦·⑧; 변이 mg·ml 검출 |
| R-34-2 `--append` 접미사 겹침 | 필수 | **해소** | R.2 #7; test-guards ⑨; 변이 mh 검출 |
| R-34-3 `--root`·대상 `.` 범위 | 필수 | **해소** | R.2 #6(심볼릭 링크·TMDIR 저장소 안 포함); test-guards ⑩; 변이 mi·mj 검출 |
| R-34-4 시험 공백 4건 | 권고 | **해소** | R.2 #9 mb·md·me·mf 전부 XX(⑪·⑫·⑬) |
| R-34-5 머리줄 ANSI | 권고 | **해소(코드)** | R.2 #8 — 시험은 없음 → R-34-10 |
| R-34-6 충돌 검사 시점 | 권고 | **해소(코드)** | R.2 #8 — 시험은 없음 → R-34-10 |
| R-34-7 문서 ①~④ | 권고 | **해소** | verification.md 62~63·86행 새 통로 문구, 18·63행 "(Windows 는 `python`)", registry 22행, FIX-034.md 수정안 2 "13경우" |
| R-34-7 ⑤ "명령은 따옴표 한 덩어리" 안내 | 권고 | **열림(선택)** | 구현자가 범위 밖으로 둠. R.2 #4 가 보이듯 결합 뒤 문자열이 가드·`bash -c` 에 똑같이 가므로 **보안에는 영향 없음** — 사용성(⑬ 따옴표 소실)만. 에이전트 정의 사용법 줄 또는 docstring 19행에 한 구절이면 닫힌다 |
| R-34-8 Windows `bash` 탐색 | 권고 | 열림(CI) | 무변경. CI windows job 첫 실행으로 확인 |
| R-34-9 변이 증거 첫 줄 | 선택 | 열림(선택) | 생략 결정 |
| **R-34-10 (신규, 권고)** R-34-5·R-34-6 을 잡는 시험 없음 | — | 열림 | 변이 mk·mm 생존(R.2 #9). 두 줄: ⑭ `--note "$(printf 'sk-\033[0mproj-%s' …30자)" -- echo hi` → rc 2·파일 0 ⑮ 같은 분 같은 이름 2회째 `-- "touch $SE_T/ran"` → rc 3·`ran` 미생성·1회째 파일 불변 |
| **R-34-11 (신규, 권고)** docstring 미갱신 | — | 열림 | `save_evidence.py` 19~21행이 가드 검사·`--root` 임시 영역 제한을 말하지 않는다(코드는 바뀜). 12·21행에 한 구절씩 |

### R.4 Mac·Windows
`_checked_root` 의 임시 영역 후보에 `tempfile.gettempdir()`·`$TMPDIR` 이 있어 Git Bash 의 `mktemp -d`(→ `native_path` C:/…/Temp) 가 통과하는 구조이고, `sys.executable` 로 가드를 부르므로 `python`/`python3` 이름 문제가 없다. Mac 에서만 실측했다 — CI windows job 의 test-guards 단계(①~⑬)로 확인한다.

### R.5 결론
1차 §5 재검증 ①~④ 를 전부 직접 실행해 통과했다(R.2 #2·#3 / #6·#7 / #1 / #9). `FIX-034.md` 의 `검증:` 줄을 `검증: 통과 — verifier (fable) 2026-10-13, review-FIX-034.md (재검증 2차)` 로 썼다. 열린 R-34-7⑤·R-34-10·R-34-11(권고)·R-34-8(CI)은 메인 세션·사용자가 이번 커밋에 포함할지 정한다.
