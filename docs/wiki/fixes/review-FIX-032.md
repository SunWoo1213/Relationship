# review-FIX-032 · 하네스 잔결함 정리(test-guards 저장소 의존 격리 · session-start 바이트 표시 · 낡은 dev 문구 · 서명 고정값)

검토자: verifier (fable)
검토일: 2026-10-11
대상: 미커밋 변경 5 파일 (기준 HEAD `de35242`) — `.claude/scripts/test-guards.sh` · `.claude/hooks/session-start.sh` · `.claude/agents/backend-agent.md` · `.claude/agents/eval-agent.md` · `.claude/skills/commit/SKILL.md`
결과: 통과 (Windows 는 푸시 뒤 CI windows job 으로 확인)

증거(전체 출력):
- `docs/wiki/fixes/evidence/20261011-2143-verifier-fix032-test-guards.txt` — verifier 직접 실행, 실행 전후 상태 포함
- `docs/wiki/fixes/evidence/20261011-2143-verifier-fix032-checks.txt` — grep·diff·문자/바이트 비교 등 보조 점검
- 구현자: `evidence/20261011-2133-fix032-test-guards.txt`(수정 후 전체) · `evidence/20261011-2133-fix032-before.txt`(옛 훅 + 새 시험, diff)
- 메인 세션: `evidence/20261011-2215-fix032-marker-present.txt`(실제 `.stage-approved` 있는 상태)

## 1. 범위 — diff 와 수정안 1~5 의 대응

| 수정안 | 변경 위치(diff) | 판정 |
|---|---|---|
| 1-a stage-gate "제품 코드 거부" 격리 + `active: FIX-998` 대조 | `test-guards.sh` 497~511행: 실제 `CURRENT.md` grep·`skip` 분기 삭제, `SG_T` 에 `active: none` → DENY, 같은 저장소 `active: FIX-998` → allow | 일치 |
| 1-b L-003 대기·delegate-guard 마커 시험 격리 + FIX-028 C 대조 | 572~609행: `AW="$SG_T/.claude/.awaiting-decision"`, `SA="$SG_T/.claude/.stage-approved"`, 모든 훅 호출에 `CLAUDE_PROJECT_DIR="$SG_T"`. 대조: L-003 절 "마커 없음 → 계획 문서 allow" 1줄, delegate 절 "격리 마커 소비됨 = SG_T 인식" 1줄 | 일치 |
| 1-c findings.py 왕복 격리 | 611~627행: `CLAUDE_PROJECT_DIR="$FD_T"` 로 실행. `findings.py:27` 이 `CLAUDE_PROJECT_DIR` 을 ROOT 로 읽음(checks §2b) — "경로 인자를 받는지 확인" 조건 충족 | 일치 |
| 1-d session-start ok 줄에 출력 크기 | 642행 `(full=${#full} bytes)` | 일치(라벨은 [권고] R-32-1) |
| 2 session-start 53행 dev2 기준 | `[ "$cur" = "dev2" ] \|\| echo "… 작업·실험 푸시는 dev2 · dev 는 dev2:dev 승격으로만 (L-001, git checkout dev2) …"` + 격리 저장소 dev2/other 시험 644~659행 | 일치 |
| 3 에이전트 정의 2 + commit SKILL 첫 커밋 절 | `backend-agent.md:73`, `eval-agent.md:63`, `SKILL.md:115` 모두 dev2 + "dev 는 dev2:dev 승격으로만" | 일치 |
| 4 commit SKILL 서명 고정값 제거 | `SKILL.md:40` 자리표 문장, 43행 규칙 추가. `grep Fable\|Opus\|Sonnet` 매치 없음(checks §5) | 일치 |
| 5 Mac·Windows CI | 코드 변경 없음(CI windows job 존재 `.github/workflows` 116·124행) | 대상 확인 |

- 훅 로직 변경은 `git diff --name-only de35242 -- .claude/hooks` → `session-start.sh` 한 파일, 그 안에서 53행 한 줄뿐(checks §1b). 다른 훅 무변경.
- 범위 밖 변경 없음: `git diff --stat` 8 파일 중 5 가 FIX-032, 나머지 3(HANDOFF·FIX-014·journal)은 지시대로 대상 외.
- 안전장치 약화 여부: 삭제된 것은 (a) 실제 `CURRENT.md` 를 읽는 조건부 시험, (b) 실제 마커를 만들고 지우는 시험, (c) 실제 `docs/wiki/packages/_selftest` 쓰기 — 셋 다 격리 저장소에서 **같은 단언을 유지한 채** 다시 돈다. 삭제된 단언 없음(L-003 3건 → 4건, delegate 8건 → 8건, stage-gate 1건(조건부) → 2건(무조건)).
- 시험 공허화 여부: 각 격리 절에 같은 격리 저장소 안의 반대 결과가 있다 — stage-gate `none` DENY / `FIX-998` allow, L-003 마커 없음 allow / 있음 DENY, delegate 마커 없음 DENY / 일치 allow + 소비 확인. "항상 deny" 또는 "항상 allow" 인 훅은 어느 쪽이든 XX 가 된다. 격리 저장소가 프로젝트 밖으로 인식되면 stage-gate 는 allow(→ `none` 시험 XX), delegate 는 실제 마커를 봐 격리 마커가 소비되지 않음(→ "consumed" 시험 XX). 공허하지 않다.

## 2. 저장소 의존 제거

명령: `grep -n "skip\|CURRENT.md\|\.stage-approved\|\.awaiting-decision\|_selftest" .claude/scripts/test-guards.sh` (checks §2, 전체 출력)

- 매치 32줄 전부 `$SG_T`·`$FD_T`·`$CC_T`(격리 디렉터리) 아래 경로 또는 주석이다.
- 남은 `skip` 은 667행 PyYAML 부재 분기 하나 — 환경 의존이며 저장소 상태 의존이 아니다(이번 실행에서는 skip 0).
- 실제 `$ROOT` 의 `CURRENT.md`·마커·`_selftest` 를 읽거나 쓰는 줄: **없음**.
- 정적 근거(checks §2b): `stage-gate.sh:20,21,73` · `delegate-guard.sh:13,14` · `commit-guard.sh:19,52` · `findings.py:27` 모두 `ROOT = CLAUDE_PROJECT_DIR 우선` 이고 마커·CURRENT 경로가 `$ROOT` 기준이다. 따라서 `CLAUDE_PROJECT_DIR=$SG_T` 로 돌린 시험 결과는 실제 저장소 마커 유무에 영향받을 수 없다.

## 3. 직접 실행

명령: `bash .claude/scripts/test-guards.sh` (실제 저장소, 2026-10-11 21:43:34 → 21:43:58) — 증거 `20261011-2143-verifier-fix032-test-guards.txt`

- `== 결과: 실패 0 ==`, `rc=0`, `ok` 333줄, `XX` 0, `skip` 0.
- 실행 전/후 `git status --short` 10줄 동일(M 8 + ?? 2), `.claude/.stage-approved`·`.awaiting-decision` 전후 모두 "No such file", `docs/wiki/packages/_selftest` 전후 모두 없음.
- 마커가 **있는** 상태(수정안 1 판정 조건의 다른 반쪽): 메인 세션 증거 `20261011-2215-fix032-marker-present.txt` — 머리말에 실행 전 `cat .claude/.stage-approved → verifier`, 실행 후 동일, `.awaiting-decision` 미생성, 변경 파일 수 8 동일, 본문 전체 출력 `ok` 333 · `== 결과: 실패 0 ==`(checks §6). verifier 가 뜰 때 그 마커가 소비되어 재현은 불가하므로 이 파일을 판정에 썼다. 전후 상태 줄은 메인 세션의 기록(명령 출력 원문이 아님)이라는 점은 §6 [권고] R-32-2 로 남긴다 — 다만 §2 의 정적 근거가 같은 결론을 독립적으로 뒷받침한다.

## 4. session-start

- 53행 문구(checks §4): "작업·실험 푸시는 dev2 · dev 는 dev2:dev 승격으로만 (L-001, git checkout dev2)" — CLAUDE.md L-001(dev2 = 작업·실험, dev = `dev2:dev` 승격으로만) 과 일치. 기준 비교 대상 `"dev2"`.
- 격리 시험(644~659행)은 `CLAUDE_PROJECT_DIR="$SS_T" bash "$H/session-start.sh"` 로 **실제 훅 파일**을 실행한다(가짜 훅 아님). `--- git (` 블록이 없으면 XX 로 떨어지는 가드가 있어, gitlog.sh 복사 실패 등으로 git 블록이 빠졌을 때 "경고 없음" 이 거짓 통과가 되지 않는다.
- 출력: `ok   session-start: 브랜치 dev2 → 경고 없음 (격리 저장소)` / `ok   session-start: 브랜치 other → 경고 (격리 저장소)` / `ok   session-start prints header (full=14131 bytes)` — ok 줄에 크기가 찍힌다(구현자 13659, 메인 세션 실행과 내 실행은 HANDOFF 길이 차이로 수치가 다름 — 정상).

## 5. 문구

- `grep -rn 'checkout dev)\|dev 에서 \|dev 에서만\|dev 브랜치에서\|브랜치 \`dev\`' .claude | grep -v dev2` → `safety-guard.sh:74` 한 줄만. 내용은 "dev:main : dev 에서 끝난 것을 배포 브랜치로" — dev→main 승격 설명으로 L-001 과 맞는 문장. 낡은 지시문 잔존 **없음**.
- `grep -n 'dev 에서만\|dev 브랜치에서만' docs/wiki/*.md` → `HANDOFF.md:42` 후보 목록(R-30-1 기록)만. 지시문 아님.
- commit SKILL: `Fable|Opus|Sonnet` 매치 0. 40행 자리표 + 43행 규칙("세션이 알려 주는 Co-Authored-By 줄을 한 글자도 바꾸지 않고… Claude-Session: 은 안내에 있을 때만"). "첫 커밋" 절 115행 dev2 기준 + 승격 규칙. 수정안 3·4 충족.

## 6. 검출력

- 구현자 before(`20261011-2133-fix032-before.txt`): 옛 `session-start.sh`(53행 `dev` 기준) + 새 시험 → `XX   session-start: dev2 인데 브랜치 경고가 나왔다`, `== 결과: 실패 1 ==`. diff 가 그 2줄 + 결과 줄만 다름을 보인다. 훅 로직 변경이 53행 하나뿐이므로 before 가 실패 1 인 것이 정확히 기대값이다 — 유효.
- 격리 절(stage-gate·L-003·delegate·findings)은 훅을 바꾸지 않았으니 전/후 모두 ok 가 정상이다. 그 절의 가치는 (a) §1 의 대조 쌍으로 시험이 공허하지 않음, (b) §3 의 전후 불변으로 실제 저장소를 건드리지 않음 — 구현자 주장 타당. 옛 시험으로는 P8 활성 상태에서 `skip active=P8-frontend` 가 나왔고(FIX-032 증상 1), 새 시험은 같은 조건에서 DENY/allow 둘 다 실제로 돌았다(내 실행 264~265행).

## 7. Mac·Windows

새로 들어간 구문: `${#full}`(bash 내장, Git Bash 동일) · `git -C … init -q` / `checkout -q -b dev2`(커밋 없는 unborn 브랜치에서도 동작, git 2.x) · `CLAUDE_PROJECT_DIR=… bash …`(환경변수 접두, POSIX) · `mktemp -d` + `native_path`(기존 11곳과 같은 관용구) · `cp`. 셸 전용·OS 전용 구문 없음. 실검증은 CI windows job(`.github/workflows` 116·124행) — 푸시 뒤 확인 필요.

## 소견

[필수] 없음.

[권고]
- **R-32-1** `test-guards.sh:642` `full=${#full} bytes` — `${#var}` 는 UTF-8 로케일에서 **문자 수**다(checks §4b: `'한글'` → chars=2 bytes=6; 실제 세션 출력 `${#full}=14323` vs `wc -c=20800`). 라벨이 틀리고, 로케일이 C 인 환경에서는 바이트가 찍혀 OS 간 수치 비교가 어긋난다. R-31-2 목적(Windows 멈춤 원인 좁히기)에는 `printf '%s' "$full" | wc -c` 가 맞다. 안전장치가 아니라 진단 라벨이므로 [권고].
- **R-32-2** "마커 있는 상태" 증거(`…-2215-fix032-marker-present.txt`)의 전후 상태는 머리말의 메인 세션 기록이다. 다음부터는 test-guards 가 시작·종료 시 실제 `$ROOT/.claude/.stage-approved`·`.awaiting-decision` 존재 여부와 `git status --short | wc -l` 을 스스로 찍고 달라지면 XX 로 떨어지게 하면, 어느 상태에서 돌려도 불변이 **출력 안에** 남는다.
- **R-32-3** `FIX-032.md` "결과(커밋 해시 · 테스트)" 절이 비어 있다 — 커밋 뒤 메인 세션이 해시·`ok 333/실패 0` 을 채울 것.
