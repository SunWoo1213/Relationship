# review-FIX-031 · 커밋 전 리뷰 — Windows CI 의 훅 자가 시험이 session-start 시험에서 멈추는 것

검토자: verifier (fable) · 2026-10-11 · 기준 HEAD `440a0e5` + 작업 트리 미커밋 diff(`.claude/scripts/test-guards.sh` +4/-1, `.github/workflows/tests.yml` +4/-0) · Refs: FIX-031 FIX-022 P8-frontend L-001

**판정: 통과** — [필수] 0건, [권고] 3건(R-31-1~R-31-3). 코드·훅·워크플로는 고치지 않았다(FIX-031.md 의 `검증:` 줄 한 줄만 갱신). 단, **Windows 에서 멈춤이 실제로 해소되는지는 이 리뷰로 판정할 수 없다** — Mac 에서는 옛 코드도 멈추지 않았으므로 로컬 통과는 "회귀 없음" 의 증거이지 "원인 해소" 의 증거가 아니다. 그 판정은 수정안 3 대로 푸시 뒤 CI windows job 으로만 한다.

통과 요지: (1) diff 가 수정안 1·2 와 글자 단위로 일치하고 범위 밖 변경이 없다(§3.1). (2) "훅 출력을 파이프로 바로 head 에 넘기는 곳은 489행 하나" 라는 구현 보고가 맞다 — 나머지 `| head -c` 9곳은 이미 변수에 담긴 문자열을 자르는 것이다(§3.2). (3) 새 판정 로직은 옛 로직과 의미가 같다 — 가짜 훅 4종(정상 / 둘째 줄에만 '세션 재개' / 빈 출력 / 다른 헤더)에서 옛·새 로직이 모두 같은 ok/XX 를 내고, 실제 `session-start.sh` 첫 줄도 동일하다(§2 2~3). (4) `bash .claude/scripts/test-guards.sh` 실패 0(§2 1). (5) `timeout-minutes: 20` 은 두 job 모두 `jobs.<id>` 직속 키로 파싱된다(§2 4). (6) 문서가 "근본 원인 미확정 — 가설" 을 제목·본문·코드 주석에 모두 남기고, 수정 뒤 CI 결과로 가설을 판정하는 절차를 적어 두었다(§3.5).

## 1. 본 것

- 문서: `docs/wiki/fixes/FIX-031.md`(증상 — run 38111227562 windows job 이 `== session-start 출력 존재 ==` 뒤 33분 무출력 · 원인 가설 — `head -n 1` 이 파이프를 닫은 뒤 MSYS 에서 쓰는 쪽이 SIGPIPE 를 못 받아 막힘 · 수정안 1~3 · `계획 점검: 통과` · `승인: 사용자 (2026-10-11 …)`).
- diff: `git diff .claude/scripts/test-guards.sh .github/workflows/tests.yml` — test-guards 489행 `out="$(… | bash "$H/session-start.sh" | head -n 1)"` 1줄 삭제 → 주석 2줄 + `full="$(… | bash "$H/session-start.sh")"` + `out="$(printf '%s\n' "$full" | head -n 1)"` 4줄 추가. 493행 판정(`grep -q '세션 재개'`)은 무변경. tests.yml 은 `pytest`(28행)·`windows`(126행) job 에 주석 1줄 + `timeout-minutes: 20` 1줄씩.
- 구현 증거: `evidence/20261011-fix031-test-guards.txt`(exit 0 · XX 0 · yaml ok — 요약본, 원문은 스크래치패드라 남아 있지 않음 → R-31-3).
- 작업 트리의 다른 변경(`app/api/routes.py`·`schemas.py`·`read.py`·`tests/test_api_read_persons.py`·P8 evidence)은 U1 재작업이며 이 리뷰 대상이 아니다. 열지 않았다.
- `.claude/scripts/fix_guard_check.py` 49~50행(`VERDICT_RE`·`NEGATION_RE`), 108행.

## 2. 내가 직접 실행한 것 (수치는 보고서에서 옮기지 않고 전부 다시 쟀다)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `bash .claude/scripts/test-guards.sh`(Mac, 실제 저장소 `active: P8-frontend`) | 종료 0 · **ok 222 / XX 0 / `== 결과: 실패 0 ==`**(240행). 202~203행 `== session-start 출력 존재 ==` → `ok   session-start prints header` | `evidence/20261011-verifier-fix031-test-guards.txt`(전체 원문 240행) |
| 2 | 가짜 훅 4종에 대해 새 로직(491~493행 사본 `judge.sh`)과 옛 로직(489행 사본 `judge-old.sh`)을 각각 실행 | `fake-ok`(첫 줄에 '세션 재개') → 둘 다 ok · `fake-bad-2ndline`(둘째 줄에만) → 둘 다 `XX session-start: 다른 헤더` · `fake-empty`(출력 없음) → 둘 다 `XX session-start: ` · `fake-bad-string`('세션 시작') → 둘 다 XX. **4/4 동일 판정** — 새 로직은 첫 줄만 보는 성질과 실패 조건을 그대로 유지한다 | `evidence/20261011-verifier-fix031-negative.txt` 1~29행 |
| 3 | 실제 `.claude/hooks/session-start.sh` 출력에 옛/새 로직 적용, 첫 줄 비교 | `SAME first line`(`=== 세션 재개 컨텍스트 (source: resume) — …`), 전체 출력 13,878바이트(문서의 12,417바이트보다 커졌다 — HANDOFF·journal 이 자람. 파이프 버퍼 가설과 모순 없음) | 같은 파일 31~35행 |
| 4 | `python3 -c "yaml.safe_load(...)"` 로 job 키 위치 출력 | `pytest runs-on=ubuntu-latest timeout-minutes=20` · `windows runs-on=windows-latest timeout-minutes=20` — 두 job 의 `jobs.<id>.timeout-minutes` 로 파싱됨(GitHub Actions 스키마의 job 레벨 키). `grep -n timeout-minutes` 28·126행 2건 | 같은 파일 40~43행 |
| 5 | `grep -n 'bash "\$H/[a-z-]*\.sh" \| head' .claude/scripts/test-guards.sh`(변경 후) | 0건 — 훅 프로세스 출력을 head 에 직접 넘기는 곳 없음 | 같은 파일 37~38행 |
| 6 | `git diff --stat` 2파일 | `2 files changed, 8 insertions(+), 1 deletion(-)` | 같은 파일 45~48행 |

## 3. 확인 항목별 판정

### 3.1 diff ↔ 수정안 1~3 — 일치, 범위 밖 변경 없음
- 수정안 1: `full="$(echo '{"source":"resume"}' | bash "$H/session-start.sh")"; out="$(printf '%s\n' "$full" | head -n 1)"` 가 491~492행에 글자 그대로 들어갔고 판정 문자열 `세션 재개` 는 493행에 그대로다. test-guards 의 다른 절은 diff 에 없다(hunk 1개).
- 수정안 2: `pytest`(리눅스)·`windows` 두 job 에 `timeout-minutes: 20` — 문서의 "windows job(및 리눅스 job)" 과 일치. step 레벨이 아니라 job 레벨이라 그 job 의 모든 step 을 합쳐 20분이다(§2 4). 직전 정상 소요 2분 49초 대비 7배 여유.
- 수정안 3(회귀 판정): 로컬 실패 0 은 §2 1 로 닫혔다. CI windows job success 는 푸시 뒤 — 미실행이 맞다.
- 범위: `git status --short` 에서 `docs/wiki` 외 변경은 FIX-031 2파일 + U1 재작업 4파일(`app/api/*` 3 · `tests/test_api_read_persons.py`)뿐이고, 후자는 별도 커밋 대상이다. 훅(`.claude/hooks/`) 무변경.

### 3.2 "`| head` 는 489행 하나" 보고 — 맞다
`grep -n '| head'` 결과 10건(변경 후 기준 38·153·155·279·285·376·399·403·431·492행). 이 중 492행은 이번에 넣은 `printf '%s\n' "$full" | head -n 1`(변수를 넘김), 376행은 `grep … CURRENT.md | head -n1`(파일 읽기, 훅 아님), 나머지 8건은 전부 `$(printf '%s' "$out"|"$3"|"$fg_out" | head -c N)` 로 **이미 캡처된 문자열**을 XX 메시지용으로 자르는 것이다. 즉 "훅 프로세스 stdout 을 파이프로 바로 head 에 넘기는" 형태는 옛 489행 하나였고 변경 후 0건이다(§2 5). 구현 보고와 일치.

### 3.3 의미 동등성 — 유지
- 옛 로직: 훅 stdout → `head -n 1` → `out`. 새 로직: 훅 stdout 전체 → `full` → `printf '%s\n'` → `head -n 1` → `out`. 차이는 (a) 훅이 끝까지 돈 뒤 첫 줄을 고른다는 점, (b) `$(…)` 가 꼬리 개행을 제거하고 `printf '%s\n'` 이 한 줄 보장을 위해 되살린다는 점이다. 빈 출력이면 `full=""` → `printf` 가 빈 줄 하나 → `out=""` → XX. 옛 로직도 `out=""` → XX. 동일(§2 2 `fake-empty`).
- 4종 가짜 훅 모두 옛·새 판정 일치, 실제 훅 첫 줄 동일(§2 2~3). 공허 통과가 아니다 — 첫 줄에 '세션 재개' 가 없으면 XX 가 난다는 것을 두 음성 케이스가 직접 보여 준다.
- 부수 효과: 새 로직은 session-start 가 끝날 때까지 기다리므로 시험 시간이 늘 수 있다. Mac 실측에서는 전체 실행이 눈에 띄게 느려지지 않았다(240행 출력, 수 초 내). session-start 안의 `gitlog.sh --write` 등 하위 프로세스는 옛 로직에서도 SIGPIPE 로 중단되지 않았을 가능성이 있어(쓰기 대상이 stdout 이 아니면 SIGPIPE 를 받지 않음) 실질적 차이는 거의 없다.

### 3.4 로컬 실행 — 실패 0
§2 1. ok 222 는 FIX-030 리뷰 당시 215 보다 7 많다 — U0(`440a0e5`)에서 frontend-agent 시험 등이 추가된 결과로 보이며 이번 FIX 의 ok 수는 변하지 않는다(시험 1건을 1건으로 바꿈). `stage-gate` 절은 `active: P8-frontend` 라 "product code with active: none" 1건이 skip 됐다(FIX-030 R-30-1 에 적힌 기존 성질, 이번 범위 밖).

### 3.5 한계와 문서의 정직성 — 적절
- 문서 17행 제목이 "원인 (근본 원인 미확정 — 가설)" 이고, 23행이 "확인 안 됨", "같은 커밋 재실행으로 재현되는지도 보지 않았다(간헐일 수 있음)" 을 명시한다. 31행이 "수정 뒤 windows job 이 정상 시간에 끝나면 가설과 일치, 또 멈추면(20분 실패) 가설이 틀린 것 → 다시 사용자에게 보고" 로 판정 절차를 둔다. 코드 주석(489~490행)에도 "(근본 원인 미확정)" 이 남아 있다. 사실성 규칙(확인되지 않은 원인은 미확정으로)과 맞다.
- 내가 덧붙이는 한계: **Mac 실패 0 은 Windows 해소의 증거가 아니다.** 옛 코드도 Mac·리눅스에서는 멈추지 않았다. 또 `timeout-minutes` 는 재발 시 "6시간 → 20분 실패" 로 드러나게 하는 안전망이지 멈춤 자체를 고치는 것이 아니다. 따라서 이 FIX 의 결과절은 CI run id 와 windows job 소요 시간이 들어가야 닫힌다(R-31-1).

### 3.6 `검증:` 줄 형식
`검증: 통과 — verifier (fable) 2026-10-11, review-FIX-031.md (Windows 해소는 푸시 뒤 CI windows job 으로 확인)` — `VERDICT_RE` 일치 · `NEGATION_RE` 비포함(python 으로 확인, §2 보조) · FIX-031.md 안에서 줄 첫머리 `검증:` 은 이 한 줄뿐(37행 자리표를 교체). 제품 코드(`app/`·`alembic/`) 무변경이라 commit-guard 규칙 6 비대상이지만 L-002 절차(다른 모델·새 컨텍스트, 직접 재실행, 음성 케이스)는 지켰다.

## 4. 소견

### [필수] — 없음

### [권고] — 커밋을 막지 않음

- **R-31-1 결과절 마무리(메인 세션).** 커밋 → dev2 푸시 뒤 `gh run view <id> --json jobs` 로 세 job success 와 **windows job 소요 시간**(직전 정상 2분 49초 수준이면 가설과 일치)을 FIX-031.md 결과절에 적는다. 가능하면 같은 커밋을 `gh run rerun` 으로 한 번 더 돌려 간헐성을 배제한다(문서 23행이 스스로 "재현 여부 미확인" 이라 했으므로 1회 success 만으로는 가설 확정이 아니다). 이 run 이 U0 의 R-U0-4(Windows 확인)도 겸한다는 문서 31행의 연결을 결과절에 그대로 남긴다.
- **R-31-2 재발 시 진단 정보.** 또 20분 타임아웃이 나면 로그에 남는 것은 `== session-start 출력 존재 ==` 한 줄뿐이다. 다음에 이 절을 손볼 때 `full` 의 바이트 수를 `ok` 줄에 함께 찍으면(예: `ok   session-start prints header (bytes=N)`) 출력 크기와 멈춤의 상관을 CI 로그에서 바로 볼 수 있다. 이번 범위 밖.
- **R-31-3 구현 증거 원문.** `evidence/20261011-fix031-test-guards.txt` 는 요약본이고 원문은 스크래치패드(`tg.txt`)에 있어 저장소에 남지 않았다. 이번에는 내가 다시 돌린 전체 원문(`20261011-verifier-fix031-test-guards.txt`)이 대신하므로 막지 않지만, 다음부터는 구현 쪽도 `tee` 로 전체를 evidence 에 남기는 것이 `docs/wiki/verification.md` 취지에 맞다.

## 5. 결론

`검증: 통과 — verifier (fable) 2026-10-11, review-FIX-031.md (Windows 해소는 푸시 뒤 CI windows job 으로 확인)` 을 FIX-031.md 에 기록한다. 커밋(U1 과 별도) → dev2 푸시 → R-31-1 대로 CI windows job 결과를 결과절에 적으면 수정안 3 이 닫힌다. 20분 실패가 나면 가설이 틀린 것이므로 FIX-031 을 다시 열고 사용자에게 보고한다.
