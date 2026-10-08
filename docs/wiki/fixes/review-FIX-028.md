# review-FIX-028 · 커밋 전 리뷰 — Windows CI 의 test-guards 격리 저장소 stage-gate 시험이 경로 표기 차이로 실패·공허 통과

검토자: verifier (fable) · 2026-10-08 · 기준 HEAD `2264d56` + 작업 트리 미커밋 diff(`.claude/hooks/stage-gate.sh` +8, `.claude/scripts/test-guards.sh` +23/-4) · Refs: FIX-028 FIX-027 FIX-022 R-27-5 R-27-6 F-27-2

**판정: 통과** — [필수] 0건, [권고] 4건(R-28-1~R-28-4). 코드·훅은 고치지 않았다(FIX-028.md 의 `검증:` 줄 한 줄만 갱신).

통과 요지: (1) 원인 가설의 **기전**(네이티브 python 인자만 경로 변환, 환경변수는 그대로 → `stage-gate.sh` 가 "프로젝트 밖"으로 보고 allow)을 Mac 에서 python 스텁으로 재현하면 CI 와 **같은 4건·같은 메시지**가 나온다(§2 S1). (2) 새 대조 케이스는 경로 인식이 깨지면 실제로 XX 를 낸다(S2·S0 — 옛 훅/cygpath 없음에서 2건 XX). (3) A 단독·B 단독 모두 시험을 실패 0 으로 되돌린다(S4·S5). (4) Mac 에서 test-guards 실패 0 · pytest 1840 passed · 훅 출력 유효 JSON. Windows 실제 동작은 CI 로만 확인 가능하므로 커밋·dev2 푸시가 타당하다(§5). 단, **B(훅 보강)는 A 가 있으면 CI 가 그 효과를 구분하지 못한다**(S6·S7) — R-28-1.

## 1. 본 것

- 문서: `docs/wiki/fixes/FIX-028.md`(증상·원인 가설·수정안 A~D·결과). 증거 `evidence/20261008-1420-fix028-ci-windows-fail.txt`(CI windows job: R-27-5 절 4건 XX, 실제 저장소 경로 `/d/a/Relationship/Relationship/...` 4건 ok, `== 결과: 실패 4 ==`), `evidence/20261008-1426-fix028-{test-guards,simulation,pytest}.txt`(실패 0 · 스텁 시뮬레이션 · 1840 passed).
- diff: `stage-gate.sh` 48~55행(cygpath 보강) · `test-guards.sh` 24~30행(`native_path`), 126·365·386·478행(`mktemp -d` 4곳 전부 적용 — `grep -n mktemp` 로 확인, 다른 `mktemp`·`TMPDIR` 사용 없음), 136~140행(`fg_ctl`), 369~372행·389~391행(SG_T 대조 2건).
- 주변(변경 없음): `stage-gate.sh` 56~70행 기존 정규화(`\U` sed · `/c/`↔`C:/` · 소문자 보정 · 프로젝트 밖 `exit 0`), `_py.sh`(인터프리터 `python` 우선 → Windows CI 의 setup-python 네이티브 python 이 선택됨), `.github/workflows/tests.yml` windows job(`shell: bash` = Git Bash, `bash .claude/scripts/test-guards.sh`), `commit-guard.sh`·`commit-cleanup.sh`·`precompact.sh`(`ROOT` 를 파일 읽기·`git -C` 에만 씀, 경로 비교 없음 — `grep -n 'ROOT\|PWD\|toplevel'`), `fix_guard_check.py` 49~50·100~108행(`검증:` 줄 규칙).

## 2. 내가 직접 실행한 것

| 명령 | 결과 | 증거 |
|---|---|---|
| `bash .claude/scripts/test-guards.sh` (Mac) | `== 결과: 실패 0 ==`, FIX-028 대조 3건 모두 `ok DENY` | `evidence/20261008-1441-review-fix028-test-guards.txt` |
| `.venv/bin/python -m pytest -q` | `1840 passed, 1 warning in 20.00s` | `evidence/20261008-1441-review-fix028-pytest.txt` |
| 변이 시험 `scratchpad/sim-fix028.sh`(본문은 증거 파일 끝에 첨부) — python 스텁(인자 `/var/…`→`/private/var/…`, MSYS 변환 흉내) × cygpath 스텁(없음 / `--` 수용 / `--` 거부) × test-guards(HEAD/작업 트리) × stage-gate(HEAD/작업 트리) 8조합으로 **test-guards.sh 전체**를 실행 | 아래 표 | `evidence/20261008-1443-review-fix028-mutation.txt` |

| 시나리오 | test-guards | stage-gate | cygpath | 결과 | 뜻 |
|---|---|---|---|---|---|
| S1 | HEAD | HEAD | 없음 | **실패 4** — CI 와 같은 4줄(`.claude/hooks/x.sh … allow 됐다(R-27-5 회귀)` 등) | 가설의 기전이 CI 증상을 그대로 재현한다 |
| S2 | 새 | HEAD | 없음 | 실패 6 = SG_T 대조 2 XX + R-27-5 4 XX (FG_T 대조는 ok) | 대조 케이스가 경로 미인식을 잡는다(공허 통과 아님) |
| S0 | 새 | 새 | 없음 | 실패 6(S2 와 동일) | 대조는 훅 버전이 아니라 경로 인식 자체를 본다 |
| S3 | 새 | 새 | 수용 | **실패 0** | A+B+C 정상 |
| S4 | 새 | HEAD | 수용 | 실패 0 | A(+C) 단독으로 시험은 충분 |
| S5 | HEAD | 새 | 수용 | 실패 0 | B 단독으로도 불일치를 해소한다 |
| S6 | HEAD | 새 | `--` 거부 | 실패 4 | cygpath 가 `--` 를 못 받으면 B 는 조용히 무효(원값 유지 → allow) |
| S7 | 새 | 새 | `--` 거부 | 실패 0 | **A 가 B 의 무효를 가린다** — CI 실패 0 은 B 의 증거가 아니다 |
| JSON | 새 훅 + 스텁, ROOT=`/var/…` · fp=`/private/var/…` | | | `app/x.py` deny · `.claude/hooks/x.sh` deny · `docs/wiki/x.md` allow(빈 출력), 모두 `json.load` 통과 | F-27-2(유효 JSON) 유지 |

실행 후 `git status` 에 시험 잔여물 없음(`.claude/.awaiting-decision`·`.stage-approved`·`packages/_selftest` 없음).

## 3. 확인 항목별 판정

### 3.1 원인 가설 — 코드·CI 로그와 일치(기전은 Mac 재현, Windows 실측은 CI 대기)
- 코드 근거: HEAD `stage-gate.sh` 의 정규화는 `\`→`/`(46~47행), `^/([a-zA-Z])/`→`X:/`(`\U` sed, 57행), 소문자 보정(64~67행)뿐이다. `ROOT=/tmp/tmp.X`(MSYS 표기)와 `fp=C:/Users/…/Temp/tmp.X/…`(네이티브)는 어느 분기에도 맞지 않아 70행 `exit 0`(allow). 반면 실제 저장소 `/d/a/…` 는 57행이 `D:/a/…` 로 바꿔 맞는다 — CI 로그에서 실패 4건(모두 `SG_T` 임시 저장소)과 ok 4건(실제 저장소 경로)이 정확히 그렇게 갈린다.
- CI 환경 근거: `tests.yml` windows job 은 `actions/setup-python` 의 **네이티브** python 을 두고 `shell: bash`(Git Bash) 로 돈다. `_py.sh` 는 `python` 을 먼저 고르므로 `gate()` 의 인자가 MSYS 변환 대상이 된다. `CLAUDE_PROJECT_DIR="$SG_T" bash …` 는 bash(MSYS 프로그램) 에 주는 환경변수라 변환되지 않는다.
- 실제 저장소 경로가 "프로젝트 안"으로 인식됐다는 **독립 증거**: L-003 절(`gate "$ROOT/docs/wiki/packages/x/01-plan.md"` → DENY 기대, 404~409행)이 CI 에서 실제 저장소 경로로 돌아 XX 가 없었다(실패 총 4 = R-27-5 4건). 따라서 "R-27-5 활성 작업 있으면 allow" 4건은 공허 통과가 아니다.
- 다른 설명 검토: ① `mktemp -d` 실패 → `${TMPDIR:-/tmp}/tg-sg2-$$` 폴백 — 같은 MSYS 표기라 결과 동일, 구분 불필요. ② `\U` 는 GNU sed 확장 — Git for Windows·ubuntu 는 GNU sed 라 동작하고, Mac BSD sed 는 `/d/a/x` → `Ud:/a/x` 를 낸다(직접 확인). Mac 에서는 루트가 `/Users/…`(한 글자 디렉터리 아님)라 패턴이 걸리지 않아 무해하고, CI 증상(`/d/a` 4건 ok)과도 무관하다. ③ `/tmp` 가 Git for Windows 에서 `%TEMP%` 로 마운트되므로 `mktemp -d` 가 `/tmp/tmp.X` 를 주는 것 자체는 정상이고, 문제는 두 표기의 불일치뿐이다.
- 한계(문서가 이미 명시): MSYS 변환 결과(`C:\…` 백슬래시 형인지 `C:/` 형인지)는 Mac 에서 확정 못 한다. 어느 쪽이든 46행 `\`→`/` 뒤 `C:/…` 가 되므로 판정은 같다.

### 3.2 `stage-gate.sh` 보강(B) — 논리 정확, Windows 실측은 R-28-1
- `cygpath -m -- "$fp"` 의 `--`: cygpath(cygwin `winsup/utils/cygpath.cc`, Git for Windows 는 msys2-runtime 의 같은 소스)는 옵션을 `getopt_long(argc, argv, options, long_options, …)` 로 파싱하고 남은 `argv[optind…]` 를 변환 대상으로 쓴다. `getopt_long` 은 POSIX Utility Syntax Guideline 10 대로 `--` 를 옵션 끝으로 처리한다. **근거는 소스·규약이고 실행 증거는 아니다** — S6·S7 이 보여주듯 `--` 가 거부되면 B 는 조용히 무효가 되고 A 가 가린다. 변환 대상이 항상 `/` 로 시작하므로 `--` 없이도 안전하다(선택지는 R-28-1).
- `/` 로 시작하는 경로만 변환: 맞다. Windows 실사용에서 Claude Code 가 `C:\…` 로 주면 46~47행 뒤 `C:/…` 가 되어 cygpath 를 타지 않는다(기존 경로 그대로). `/c/…`·`/tmp/…`·`/d/a/…` 만 변환 → 같은 위치는 같은 `X:/…` 가 된다. 부수 효과로 HEAD 에서 allow 였던 "ROOT=`C:/…`, fp=`/c/…`" 조합도 이제 맞춰진다(거부 방향으로의 정정, 과차단 아님).
- 실패 시 원값 유지: `_c="$(cygpath …)" && [ -n "$_c" ] && fp="$_c"` — 비영 종료·빈 출력 모두 건너뛴다(S6 에서 실제로 원값 유지 → HEAD 와 같은 결과). `set -u` 만 있고 `set -e` 없음.
- Mac·Linux 무영향: `command -v cygpath` 실패 → 블록 통째로 건너뜀(Mac 에 cygpath 없음 확인). test-guards 실패 0 · S0.
- 거부/허용 규칙 불변: 56행 이후 코드는 diff 에 없다. 프로젝트 밖(`/elsewhere/…`, `C:\Capstone2\…`)·상대경로·면제 경로는 구현자 시뮬레이션과 내 JSON 검사에서 allow. 과차단 없음.
- 유효 JSON: 위 표 JSON 행.

### 3.3 `test-guards.sh`(A·C) — 적용 범위·검출력 확인
- `native_path()` 적용: `mktemp -d` 4곳(FG_T 126·SG_T 365·SG_T 386·CC_T 478행) 전부. 다른 임시 경로 생성 없음(`grep -n 'mktemp\|TMPDIR'` — 나머지는 safety 시험용 문자열).
- 대조 3건의 검출력: S2·S0 에서 SG_T 대조 2건이 XX(경로 미인식 시 실패) → "경로가 프로젝트 안으로 인식됨"을 실제로 증명한다. **FG_T 대조(`fg_ctl`)는 성격이 다르다**: `commit-guard.sh` 는 경로 비교를 하지 않으므로 표기 불일치 상태(S2)에서도 ok 다. 이 대조가 증명하는 것은 "훅이 FG_T 를 ROOT 로 삼아 그 안의 마커 부재를 본다"이지 "표기가 일치한다"가 아니다 — 메시지 "(저장소 인식)" 은 그 범위로 읽어야 한다(R-28-2).
- 남은 공허 통과 위험: stage-gate 를 임시 저장소로 시험하는 곳은 SG_T 두 절뿐이고 둘 다 대조가 붙었다. FG_T(commit-guard)·CC_T(commit-cleanup·precompact)는 경로 비교가 없어 표기 차이로 공허해질 구조가 아니다. 실제 저장소 경로의 allow 시험은 L-003 DENY 가 뒷받침한다(3.1).

### 3.4 직접 실행 — §2
### 3.5 커밋·CI 확인의 타당성 — 타당
Windows 기기가 없고 Git Bash 의 MSYS 변환·cygpath 실물은 CI(windows-latest) 에서만 돈다. Mac 에서 할 수 있는 검증(기전 재현·대조 검출력·A/B 각각의 효과·JSON·회귀)은 다 했고 전부 기대대로다. 커밋 → dev2 푸시 → `gh run view <id> --json jobs` 로 3 job success 를 FIX-028.md 결과절에 적는 것이 수정안 D 그대로다. 단 CI 실패 0 이 증명하는 것은 **A+C** 이고 B 는 아니다(S7) — FIX-028.md 결과절의 "어떤 표기든 cygpath 로 맞추므로 견고해졌을 것으로 보임"은 R-28-1 전까지 "미검증"으로 읽어야 한다.

## 4. 소견

### [필수] — 없음

### [권고] — 커밋을 막지 않음

- **R-28-1 B 의 Windows 증거.** A 가 있는 한 CI 는 B(훅의 cygpath 정규화)가 작동하는지 — `--` 수용 포함 — 를 구분하지 못한다(S7). Windows 에서만 도는 케이스 하나를 test-guards R-27-5 절에 추가하면 닫힌다: `command -v cygpath` 가 있을 때 `CLAUDE_PROJECT_DIR="$(cygpath -u "$SG_T")"`(MSYS 표기) + `gate "$SG_T/app/x.py"`(네이티브 표기) → DENY 기대, 없으면 `skip` 출력. 또는 더 단순하게 훅에서 `--` 를 빼도 된다(대상이 항상 `/` 로 시작해 옵션으로 오인될 수 없다). 그 전까지 FIX-028.md 결과절의 "견고해졌을 것으로 보임"은 "B 는 Windows 미검증(Mac 스텁 S5 만)"으로 적는 것이 사실성 규칙에 맞다.
- **R-28-2 `fg_ctl` 메시지.** "저장소 인식" 이 SG_T 대조와 같은 뜻(표기 일치)으로 읽히지만 commit-guard 는 경로를 비교하지 않아 불일치에서도 ok 다(S2). "ROOT 를 FG_T 로 삼아 마커 부재를 봄" 정도로 바꾸거나 주석에 그 한계를 적는다.
- **R-28-3 수정안 D 기록.** CI run id·3 job 결과를 FIX-028.md 결과절에 적고(R-27-6 의 Windows 증거 이월 항목도 함께 닫는다), windows job 로그에서 FIX-028 대조 3줄이 `ok DENY` 인지까지 인용한다 — "실패 0" 만으로는 대조가 돌았는지 안 보인다.
- **R-28-4 `\U` sed(기존 코드, 57행).** BSD sed(Mac) 에서는 `Ud:/a/x` 처럼 깨진다. 지금은 Mac 루트가 패턴에 걸리지 않아 무해하고, B 가 있는 Windows 에서는 cygpath 가 먼저 `X:/` 로 바꿔 이 줄이 사실상 쓰이지 않는다. 다음에 이 훅을 손볼 때 `tr`/파라미터 치환으로 바꾸면 이식성 요구(Mac·Windows)에 맞는다. 이번 FIX 범위 밖.

## 5. 결론

`검증: 통과 — verifier 리뷰 (review-FIX-028.md)` 를 FIX-028.md 에 기록한다. 제품 코드(`app/`·`alembic/`) 무변경이라 commit-guard 규칙 6 비대상이지만 L-002 절차는 지켰다. 커밋 후 dev2 CI 에서 R-28-3 대로 기록하면 수정안 D 가 닫힌다.
