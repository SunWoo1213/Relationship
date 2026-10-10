# review-FIX-030 · 커밋 전 리뷰 — test-guards 의 "활성 작업 있으면 allow" 시험이 실제 저장소 CURRENT.md 에 묶여 CI 가 깨진 것

검토자: verifier (fable) · 2026-10-11 · 기준 HEAD `50fd7fc` + 작업 트리 미커밋 diff(`.claude/scripts/test-guards.sh` +20/-3, 그 외 코드 파일 변경 없음) · Refs: FIX-030 FIX-027 FIX-028 R-27-5

**판정: 통과** — [필수] 0건, [권고] 4건(R-30-1~R-30-4). 코드·훅은 고치지 않았다(FIX-030.md 의 `검증:` 줄 한 줄만 갱신).

통과 요지: (1) 원인이 코드와 CI 로그에서 그대로 확인된다 — HEAD 398~401행이 `$ROOT`(실제 저장소)로 stage-gate 를 불렀고, `active: none` 복제본에서 HEAD 스크립트를 돌리면 CI 와 같은 4줄 XX·`실패 4` 가 난다(§2 [전]). (2) 수정 후 스크립트는 같은 복제본에서 `실패 0`, 실제 저장소(`active: FIX-030`)에서도 `실패 0` — 저장소 상태와 무관해졌다(수정안 C). (3) 새 시험은 공허하지 않다 — FIX-998 의 `승인:` 줄을 빼거나 `계획 점검:` 을 보류로 바꾸면 allow 4줄이 XX 가 되고, stage-gate 를 항상 allow 로 바꾸면 대조 4줄이 XX 가 된다(§2 M1~M3). (4) diff 는 계획 표 A·B 와 일치하고 훅 무변경, Windows 처리 방식은 FIX-028 과 같은 관용구다(§3).

## 1. 본 것

- 문서: `docs/wiki/fixes/FIX-030.md`(증상·원인·수정안 A~D·`계획 점검: 통과`·`승인: 사용자 2026-10-10`·결과절). 구현 증거 `evidence/20261010-2355-fix030-test-guards.txt`.
- diff: `git diff .claude/scripts/test-guards.sh` — 399~401행(`$ROOT` 4경로 `expect_allow` 루프) 삭제, 400~419행 추가(`SG_T` sg3 격리 저장소 + `CURRENT.md active: FIX-998` + `fixes/FIX-998.md` 새 템플릿 → 4경로 allow 4줄 → `active: none` 으로 바꿔 같은 4경로 DENY 대조 4줄 → `rm -rf "$SG_T"`). `git status --short` 에서 코드 파일 변경은 `test-guards.sh` 하나뿐(나머지는 docs/wiki 문서·증거·P8-frontend 폴더). `git status --short .claude/hooks` 빈 출력 — 훅 무변경.
- 훅 쪽 근거(변경 없음): `stage-gate.sh` 89행(면제 경로 — `.claude/hooks·scripts·settings.json·.github/workflows` 는 R-27-5 로 면제 목록에서 빠져 있음), 93~102행(`CURRENT.md` 없음·frozen·`active: none` → deny), 104~114행(FIX 활성 시 `fixes/<id>.md` 의 `^계획 점검:\s*통과` 또는 `^검증:\s*통과` + `^승인:\s*\S` 요구), 73행(`$ROOT/.claude/.awaiting-decision`), `delegate-guard.sh` 14행(`$ROOT/.claude/.stage-approved`).
- CI 원본: `gh run view 38052897284 --json conclusion,headSha,jobs` → `failure`, headSha `50fd7fc…`, 세 job(pytest 3.13 · 3.14 · windows) 전부 failure. `--log-failed` 에서 세 job 모두 `XX should ALLOW but denied: R-27-5 활성 작업 있으면 allow: <실제 저장소 경로>/.claude/hooks/_py.sh …` 4줄 + `== 결과: 실패 4 ==`(증거 2/2 머리).
- 같은 파일의 다른 `$ROOT`·실제 저장소 상태 의존 시험(`grep -n '\$ROOT\|CURRENT.md\|awaiting-decision\|stage-approved\|_selftest'`) — §3.3·R-30-1.
- 형식 참고: `review-FIX-028.md`. `fix_guard_check.py` 47~50행(`VERDICT_RE`·`NEGATION_RE`), 100~101행(`검증:` 줄 정확히 하나).

## 2. 내가 직접 실행한 것 (수치는 보고서에서 옮기지 않고 전부 다시 쟀다)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `bash .claude/scripts/test-guards.sh` — 실제 저장소(`active: FIX-030`) | **ok 215 / XX 0 / `== 결과: 실패 0 ==`**, 종료 0. allow 4줄(`격리 저장소, active: FIX-998`) + `FIX-030 대조` DENY 4줄 모두 ok. 실행 후 `git status` 변화 없음, 마커·`_selftest` 잔여 없음 | `evidence/20261011-0005-review-fix030-test-guards.txt`(전체 원문) |
| 2 [전] | `CLAUDE_PROJECT_DIR=<clone-none> bash <git show HEAD:…test-guards.sh>` — scratchpad 복제본(`.claude`·`.github` 복사 + `CURRENT.md active: none`), **수정 전** 스크립트 | **ok 208 / XX 4 / `실패 4`** — XX 4줄이 CI 와 같은 메시지·같은 4경로(`.claude/hooks/_py.sh`·`.claude/scripts/test-guards.sh`·`.claude/settings.json`·`.github/workflows/tests.yml`) | `evidence/20261011-0005-review-fix030-repro-mutation.txt` [전] |
| 3 [후] | 같은 복제본, **수정 후** 스크립트(작업 트리 사본, md5 동일 확인) | **ok 216 / XX 0 / `실패 0`** (`active: none` 이라 `product code with active: none` 1건이 추가 실행돼 실제 저장소보다 1 많음) | 같은 파일 [후] |
| 4 M1 | 수정 후 스크립트 사본에서 FIX-998 printf 의 `승인: 사용자 (2026-10-10)` 줄 제거(diff 1줄) | **XX 4 / `실패 4`** — allow 4줄이 `R-27-5 활성 작업 있는데 거부됨 … "FIX-998 에 사용자 승인 기록이 없…"` 로 바뀜. 대조 4줄은 여전히 ok | 같은 파일 M1 |
| 5 M2 | 사본에서 `계획 점검: 통과` → `계획 점검: 보류` | **XX 4 / `실패 4`** — allow 4줄이 `… "FIX-998 의 계획 점검이 '통과'가 …"` 로 거부. 대조 4줄 ok | 같은 파일 M2 |
| 6 M3 | 두 번째 복제본 clone-allow 의 `.claude/hooks/stage-gate.sh` 만 `exit 0`(항상 allow) 로 교체, 수정 후 스크립트 원본 | **XX 12 / `실패 12`**(전부 stage-gate 절) — 그중 `FIX-030 대조 실패: … active: none 인데 allow 됐다` 4줄. allow 4줄은 ok(항상 allow 이므로 당연). 실제 `.claude/hooks` 는 `git status` 무변경 | 같은 파일 M3 |

보고된 수치와의 대조: 구현 증거의 "수정 전 211(실제 저장소 FIX-030) / 수정 후 215 / 복제본 216 / 재현 실패 4" 는 내 측정(실제 215 · 복제본 후 216 · 복제본 전 208·실패 4)과 일치한다. 211 과 208 의 차이는 측정 상태가 다른 것(활성 작업 유무 → `product code with active: none` 1건 ±, R-27-5 4건 ±)으로 설명되며 모순이 아니다(R-30-4).

## 3. 확인 항목별 판정

### 3.1 diff ↔ 계획 표 A·B — 일치
- A: 같은 절의 `native_path "$(mktemp -d …)"` 로 `SG_T` 생성(403행) · `CURRENT.md active: FIX-998`(405행) · `fixes/FIX-998.md` 에 `계획 점검: 통과` + `승인: 사용자 (…)`(406~407행) · 4경로가 계획 문구 그대로(`.claude/hooks/x.sh`·`.claude/scripts/x.py`·`.claude/settings.json`·`.github/workflows/x.yml`) · `CLAUDE_PROJECT_DIR="$SG_T"` 로 호출(409행) · 훅 무변경.
- B: 같은 `SG_T` 를 `active: none` 으로 덮어쓰고(414행) 같은 4경로 DENY 단언(415~418행). M3 가 이 대조의 검출력을 보여준다.
- C: 실제 저장소(`active: FIX-030`)와 복제본(`active: none`) 두 상태 모두 `실패 0`(§2 1·3). "FIX 완료 뒤 실제 `active: none` 재실행" 은 메인 세션 몫(R-30-3).
- D(CI 세 job): 커밋·dev2 푸시 뒤에만 확인 가능 — 미실행이 맞고, 계획대로 FIX-030.md 결과절에 run id 를 적으면 닫힌다.
- 계획 8번 "`rm -rf "$SG_T"` 가 safety-guard 대상인지 구현 시 확인": 스크립트 내부 `rm -rf` 는 훅이 보는 Bash 명령 문자열(`bash .claude/scripts/test-guards.sh`)이 아니므로 걸리지 않는다 — 실제로 §2 1 이 막히지 않고 돌았고, 383·398행의 기존 `rm -rf "$SG_T"` 와 같은 패턴이다.

### 3.2 새 시험의 검출력 — 공허 통과 아님
- allow 4줄은 FIX 문서의 두 조건(`계획 점검: 통과`·`승인:`)에 각각 민감하다(M1·M2). 둘 다 stage-gate 112~114행이 실제로 읽는 줄이므로 "활성 FIX 게이트를 타고 allow 됐다" 를 증명한다.
- 대조 4줄은 훅이 allow 만 내면 XX 가 된다(M3). 따라서 allow 4줄 ok 가 "프로젝트 밖 인식(FIX-028 증상)" 으로 공허하게 나온 것이 아님을 같은 저장소 안에서 분리해 보인다.
- `FIX-998` 번호는 같은 파일의 다른 `SG_T` 가 쓰는 `FIX-999` 와 다르고 디렉터리도 별개라 간섭이 없다. 각 `SG_T` 는 절 끝에서 삭제된다(잔여물 없음 확인).

### 3.3 같은 파일에 남은 실제 저장소 상태 의존 시험 — 있음(모두 skip 형, CI 를 빨갛게 하진 않음) → R-30-1
`grep` 결과(수정 후 행 번호):
- 353~354행 `gate "$ROOT/docs/wiki/x.md"`·`"$ROOT/.claude/skills/x/SKILL.md"`: 면제 경로(89행)는 `CURRENT.md` 를 읽기 전에 allow 되므로 **상태 무관**. 문제 없음.
- 357~362행 `product code with active: none`: 실제 `CURRENT.md` 를 읽어 `active != none` 이면 `skip`(이번 실행에서 `skip active=FIX-030`). 결과는 바뀌지 않지만 **검사 범위가 저장소 상태에 따라 달라진다.** 같은 내용은 격리 `SG_T` 의 FIX-028 대조(372·391행)가 이미 검사한다.
- 421~429행(L-003): 실제 저장소에 `.claude/.awaiting-decision` 를 만들었다가 지우고 `gate "$ROOT/docs/wiki/packages/x/01-plan.md"`·`"$ROOT/docs/wiki/HANDOFF.md"` 로 시험. 실제 마커가 있으면 `skip`. 스크립트가 426~428행 사이에서 죽으면 **실제 저장소가 L-003 대기 상태로 남는다**(stage-gate 73행·commit-guard 52행이 그 마커를 읽는다).
- 431~441행(L-004): 실제 저장소에 `.claude/.stage-approved`(내용 `architect`) 를 만들고 delegate-guard 가 소비하는지 시험. 실제 마커가 있으면 `skip`. 중간에 죽으면 가짜 승인 마커가 남아 architect 위임이 승인 없이 통과된다.
- 444~453행(findings.py): 실제 `docs/wiki/packages/_selftest` 를 만들고 지움. 상태 의존은 아니나 실제 저장소에 쓴다.
- 469행 `hook_python_with yaml "$ROOT"`: 환경(패키지 유무) 의존, 상태 의존 아님.
이번 FIX 의 범위(CI 를 깨는 4건)는 닫혔다. 위 항목은 범위 밖이라 [권고]로만 남긴다.

### 3.4 Windows(Git Bash) 처리 — FIX-028 방식과 동일
- 403행 `SG_T="$(native_path "$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/tg-sg3-$$")")"` 는 386행(sg2)·365행(sg)·126행·495행과 같은 관용구(접미사만 `tg-sg3`). `printf '…\n' > "$SG_T/…"`·`CLAUDE_PROJECT_DIR="$SG_T" bash "$H/stage-gate.sh"`·`rm -rf "$SG_T"` 도 386~398행과 같다. `mktemp` 사용은 5곳 전부 `native_path` 로 감싸져 있다(`grep -n mktemp`).
- 같은 구조의 sg2 절이 직전 success run(38049456285, `e555142`) windows job 에서 돌았으므로 sg3 절도 같은 경로 표기로 동작할 것으로 본다. 실측은 수정안 D(CI)로 닫는다.
- Mac 에서의 부수 문제 1건(R-30-2): XX 메시지의 `head -c 150` 이 바이트 단위라 한글 중간에서 잘려 깨진 UTF-8 이 나올 수 있다(M2 에서 실제 발생 — Mac `grep` 이 UTF-8 로케일에서 그 파일을 거부해 집계를 python 으로 했다). 기존 378·382행과 같은 패턴이고 **XX 가 났을 때만** 영향이라 통과를 막지 않는다.

### 3.5 `검증:` 줄 형식
`검증: 통과 — verifier (fable) 2026-10-11, review-FIX-030.md` — `VERDICT_RE`(`^검증:\s*통과\s*[—–-]+\s*verifier\b`) 일치, `NEGATION_RE`(생략|아직|예정|아님|않|못|미실시|제외|대신) 비포함, FIX-030.md 안에서 줄 첫머리 `검증:` 은 이 한 줄뿐(39행 "`검증:` 줄은 verifier 가 쓴다" 는 줄 중간이라 제외). 본 리뷰 문서 첫머리에 `검토자: verifier (fable)`.

## 4. 소견

### [필수] — 없음

### [권고] — 커밋을 막지 않음

- **R-30-1 남은 실제 저장소 의존 시험(§3.3).** 357~362행은 격리 대조(372·391행)와 중복이므로 삭제하거나 `SG_T` 로 옮긴다. 421~441행(L-003·L-004)은 실제 `.claude/` 에 마커를 썼다 지우는 구조라 (a) 실제 마커가 있으면 조용히 `skip` 돼 범위가 상태에 따라 달라지고 (b) 중간 중단 시 실제 저장소에 가짜 마커가 남는다. CC_T 절(495행~)처럼 임시 저장소에 `.claude/` 를 꾸며 `CLAUDE_PROJECT_DIR` 로 돌리면 둘 다 없어진다. 444~453행 `_selftest` 도 같은 방식으로 옮길 수 있다. 별도 FIX 후보.
- **R-30-2 `head -c 150` 바이트 절단(410행, 기존 378·382행 동일).** 실패 메시지가 한글 중간에서 잘려 깨진 UTF-8 을 내고, Mac `grep` 이 UTF-8 로케일에서 그 출력 파일을 거부한다(M2 에서 실제 발생). `"$HOOK_PY" -c` 로 글자 단위 절단하거나 `cut -c1-150`(로케일 의존) 로 바꾸면 된다. 다음에 이 파일을 손볼 때 함께.
- **R-30-3 수정안 C·D 마무리(메인 세션).** FIX 완료로 실제 `CURRENT.md` 가 `active: none` 이 된 뒤 `bash .claude/scripts/test-guards.sh` 를 한 번 더 돌려 `실패 0` 을 결과절에 적고, dev2 푸시 뒤 `gh run view <id> --json jobs` 로 세 job success 와 windows job 로그의 `FIX-030 대조` DENY 4줄을 인용한다(FIX-028 R-28-3 과 같은 이유 — "실패 0" 만으로는 대조가 돌았는지 안 보인다).
- **R-30-4 결과절 수치 표기.** "수정 전 211" 은 실제 저장소(`active: FIX-030`) 기준이고 `active: none` 복제본에서는 208(실패 4)이다. 결과절에 상태별로 나눠 적으면(전: 211/FIX-030 · 208/none, 후: 215/FIX-030 · 216/none) 사실성 규칙에 더 맞는다. 오류는 아니다.

## 5. 결론

`검증: 통과 — verifier (fable) 2026-10-11, review-FIX-030.md` 를 FIX-030.md 에 기록한다. 제품 코드(`app/`·`alembic/`) 무변경이라 commit-guard 규칙 6 비대상이지만 L-002 절차(다른 모델·새 컨텍스트의 독립 검증, 직접 재실행, 변이로 검출력 확인)는 지켰다. 커밋 → dev2 푸시 → R-30-3 대로 기록하면 수정안 C·D 가 닫힌다.
