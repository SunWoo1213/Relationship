# review-FIX-027 · 커밋 전 리뷰 — FIX 에 verifier 검증을 절차·커밋 훅으로 강제한다

검토자: verifier (fable) · 2026-10-06 · 기준 HEAD `90f249c` + 작업 트리 미커밋 diff · Refs: FIX-027 L-002 L-004 FIX-008 FIX-022 R-공통-1 R-26-4

**판정: 보류** — [필수] 4건(F-27-1~F-27-4), [권고] 6건(R-27-1~R-27-6). 코드·문서는 고치지 않았다(FIX-027.md 의 `검증:` 줄 한 줄만 갱신).

보류 요지: 훅이 **의도한 다섯 케이스는 막고 통과시킨다**(test-guards 재실행 실패 0, 기존 규칙 1~5 유지 확인). 그러나 (1) 새 템플릿이 `stage-gate.sh` 의 FIX 분기와 **충돌해 활성 패키지가 없을 때 FIX 구현이 불가능**해지고, (2) 판단 불가 경로 하나가 **깨진 JSON 을 내어 fail-closed 주장이 성립하지 않으며**, (3) `git commit -a`·pathspec 으로 **스테이징 없이 제품 코드를 끼워 넣으면 규칙 6 이 침묵**하고, (4) `검증:` 줄 판정이 `통과` 를 보지 않아 **verifier 의 보류 판정으로도 커밋이 열린다**. 넷 다 재현 명령·출력이 `evidence/20261006-1613-review-fix027-bypass.txt` 에 있다.

## 1. 본 것

- diff(`git diff`): `.claude/hooks/commit-guard.sh`(+15, 규칙 6 추가 73~84행) · `.claude/scripts/test-guards.sh`(+65, "FIX-027 제품 코드 verifier 게이트" 절 111~175행) · `.claude/skills/devlog/SKILL.md`(`/devlog fix` 49~56행, 5→7단계) · `CLAUDE.md`(+1, 113행) · `docs/wiki/templates/fix.md`(14~15행 `계획 점검:`/`검증:` 분리). 신규 `.claude/scripts/fix_guard_check.py`(129행).
- 문서: `docs/wiki/fixes/FIX-027.md`(수정안 A~E, 결과 절). 출발점 `review-FIX-018-025.md` 101행(R-공통-1 — "FIX 템플릿의 `검증:` 줄에 `검증자: verifier` 를 요구하도록 … 기계 검사를 FIX 문서에도 적용"), `review-FIX-026.md` 75행(R-26-4 — 활성 패키지 아래 FIX 는 `stage-gate.sh` FIX 분기를 타지 않음 → "제품 코드 FIX 는 커밋 전 verifier 리뷰" 규칙을 `/devlog fix` 에 반영할 때 함께 다룰 것).
- 구현자 증거: `evidence/20261006-1604-fix027-{test-guards,pytest,ruff,mypy}.txt` — 각각 `결과: 실패 0`(6케이스 ok) · `1840 passed, 1 warning` · `All checks passed!` · `[ok] 새 오류 없음 (현재 38건, 기준선 38건)`. 주장과 일치.
- 주변 코드(변경 없음, 정합성 확인용): `.claude/hooks/_py.sh`, `.claude/hooks/stage-gate.sh` 9행·85~90행(FIX 분기), `.claude/scripts/verify-plan.sh` 86행, `.claude/skills/commit/SKILL.md` 67~68행·106행, `.github/workflows/*.yml` 112·147행(ubuntu·windows 에서 `test-guards.sh` 실행, FIX-022), `git log` 의 `(FIX-` 제목 유형(fix 17·test 2·docs 4·harness 2).

## 2. 내가 직접 실행한 것

| 명령 | 결과 | 증거 |
|---|---|---|
| `bash .claude/scripts/test-guards.sh` | `== 결과: 실패 0 ==`, 새 절 6케이스(1·2·2b·3·4·5) 전부 ok | 구현자 파일과 동일 출력(`evidence/20261006-1604-fix027-test-guards.txt` 63~69·138행), 내 재실행은 scratchpad |
| 격리 저장소 우회·fail-closed 시험 46건(제목 15·경로 5·검증 줄 위조 11·fail-closed 11·stage-gate 2·기존 규칙 7) | 기대와 다른 결과 **25건**(아래 §3·§4) | `evidence/20261006-1613-review-fix027-bypass.txt`(출력 + 스크립트 본문) |
| `python fix_guard_check.py <root>` / `… <root> <없는 초안>` | rc=2 / rc=2 | 같은 파일 §D |

## 3. 판정 기준별 결과

### 3.1 의도한 동작 — 통과
훅은 FIX-027.md 수정안 C 의 네 케이스와 추가 2b 를 막고 통과시킨다(§2 첫 행). `alembic/` 만 스테이징해도 DENY(§B 1행). CRLF 초안·CRLF FIX 문서 모두 올바르게 판정(§A 마지막, §C 7행). `fix(FIX-27)` 처럼 번호가 어긋나면 `FIX-27.md` 를 찾다 실패해 DENY — 방향이 맞다.

### 3.2 fail-closed — 부분 통과
- 통과: ROOT 가 git 저장소가 아님 → rc 2 → DENY. 스크립트 파일 부재 → 파이썬 한 줄 오류 → DENY. 인자 부족·초안 없음 rc 2. 파이썬 없음은 `commit-guard.sh:24~28`(FIX-008, 변경 없음)이 그대로 막는다(내 PATH 시험은 bash 자체가 사라져 무효 — evidence §D 표기).
- **실패(F-27-2)**: FIX 문서가 UTF-8 이 아니면 `fix_guard_check.py:48` `read_text(encoding="utf-8")` 가 `UnicodeDecodeError`(`ValueError` 계열, `except OSError` 에 안 걸림)로 **여러 줄 Traceback** 을 stderr 로 내고, `commit-guard.sh:79` 가 `2>&1` 로 그대로 받아 `deny()` 에 넘긴다. `deny()`(37~42행)는 `\`·`"` 만 이스케이프하고 **줄바꿈은 처리하지 않아** stdout 이 유효한 JSON 이 아니다(`json.load` → `Invalid control character at … char 142`, evidence §C 끝). PreToolUse 훅의 stdout 이 JSON 으로 파싱되지 않으면 `permissionDecision` 이 전달되지 않고 도구 호출이 진행된다 — 즉 이 경로는 **deny 를 출력하려 했으나 실제로는 열린다**. FIX-027.md 수정안 B 의 "판단 불가(파일 읽기 실패 등)도 deny(fail-closed)" 와 어긋난다. 같은 이유로 스크립트의 **모든** 예기치 않은 예외가 fail-open 이 된다.
- 기존 규칙 1~5: 마커 없음·`-m`·해시 불일치·`--amend`·`--no-verify`·마커 조작 전부 DENY, 정상 `feat` 커밋 allow(evidence §D).

### 3.3 Mac/Windows 이식성 — 통과(Windows 는 CI 대기)
- `_py.sh` 로 인터프리터 선택, `PYTHONUTF8=1`·`PYTHONIOENCODING=utf-8` 상속, `read_text(encoding="utf-8")`, `splitlines()`·`strip()` 으로 CRLF 처리(시험으로 확인), `replace("\\","/")` 정규화, `pathlib` 경로 결합. `subprocess.run(["git", …])` 리스트 형식은 Windows 에서 `git.exe` 를 PATH 로 찾는다.
- `"$HOOK_PY" "$(dirname "$0")/../scripts/…" "$ROOT" "$DRAFT"` 처럼 파이썬에 경로 인자를 넘기는 선례는 `test-guards.sh:224`(`findings.py <path>`)이고 그 스크립트가 CI Windows(Git Bash) 에서 돌아간다(`.github/workflows` 147행, FIX-022). 로컬 증거는 Mac 만이므로 Windows 는 푸시 후 CI 로 확인해야 한다(R-27-6).

### 3.4 보호 범위 — 의견은 R-27-5

### 3.5 절차 문서·CLAUDE.md 정합성 — 1건 충돌(F-27-1), 나머지 일치
- L-002: SKILL 52행 "`검증:` 줄은 메인 세션이 쓰지 않는다 … L-002 는 FIX 에도 적용" ↔ CLAUDE.md "팀 구성"(점검표·완료 검토는 verifier 만) 일치. CLAUDE.md 113행 ↔ SKILL 54~55행 일치.
- L-004: SKILL 54행(backend-agent 띄우기 전 AskUserQuestion + `--stage backend-agent`) ↔ SKILL 15행·CLAUDE.md 110행 일치. 55행의 verifier 위임에는 같은 문구가 없다(R-27-4).
- **충돌(F-27-1)**: SKILL 53행 "활성 패키지가 … 없으면 `CURRENT.md active: FIX-nnn`" 경로에서 `stage-gate.sh:88` 은 `^검증:[[:space:]]*통과` 를 요구하는데, 새 템플릿(`templates/fix.md:15`)·SKILL 52행은 `검증:` 을 verifier 가 **구현 뒤** 채우는 자리표로 바꿨다. 재현(evidence §E): `active: FIX-999`, FIX 문서에 `계획 점검: 통과`·`검증: (verifier 가 쓴다 …)`·`승인: 사용자` → `app/new.py` 쓰기 **DENY** "수정 계획 검증이 '통과'가 아니다". backend-agent 가 코드를 못 쓰면 verifier 가 볼 코드가 없고 `검증:` 은 영원히 자리표다 — 활성 패키지가 없는 순간부터 FIX 절차가 교착한다. 지금은 `active: P7-push` 라 드러나지 않을 뿐이며, 바로 그 상황(활성 패키지 아래 FIX 가 stage-gate 를 우회)이 FIX-027 증상 3행(R-26-4)이다. `stage-gate.sh:9` 주석도 "검증: 통과" 로 남아 있다.
- 자리표 문구가 SKILL 52행(`검증: (verifier 가 쓴다)`)과 템플릿 15행(`… — 제품 코드를 바꾸면 커밋 전 review-FIX-nnn.md 와 함께`)에서 다르다. 둘 다 `(` 로 시작해 판정에는 영향 없음 — 메모만.

## 4. 소견

### [필수] — 커밋 전에 닫아야 한다

| ID | 내용 | 재현(evidence §) | 권장 조치(구현은 backend-agent) |
|---|---|---|---|
| **F-27-1** | `stage-gate.sh:88` 이 FIX 문서의 `^검증: 통과` 를 요구 → 새 템플릿의 자리표와 충돌, 활성 패키지가 없는 FIX 는 제품 코드 쓰기 불가(교착). 수정안 A 가 B 범위 밖의 훅(`stage-gate.sh`)을 깨뜨렸다. | §E 1행 | stage-gate FIX 분기를 `^계획 점검:[[:space:]]*통과` + `^승인:` 로 바꾸고(코드 쓰기 전 조건), `검증:` 은 commit-guard 규칙 6 이 커밋 시점에 본다는 역할 분담을 `stage-gate.sh:9` 주석·SKILL 53행에 적는다. `test-guards.sh` stage-gate 절에 "새 템플릿 FIX 문서로 app/ 쓰기 allow" 케이스 추가. |
| **F-27-2** | 스크립트의 처리되지 않은 예외(예: FIX 문서 비-UTF-8 → `UnicodeDecodeError`, `fix_guard_check.py:48`)가 여러 줄 Traceback 으로 `deny()` 에 들어가 **유효하지 않은 JSON** 을 출력 → 거부가 전달되지 않는다. "판단 불가도 deny" 주장(수정안 B) 불성립. | §C 마지막 2항 | ① `fix_guard_check.py` `main` 전체를 `except Exception` 으로 감싸 한 줄 메시지 + rc 2. ② `commit-guard.sh` 에서 `fix_guard_out` 의 줄바꿈을 공백으로 접고(`tr '\n' ' '`) 길이를 제한한 뒤 `deny` 에 넘긴다(`deny()` 자체에 줄바꿈 이스케이프를 넣으면 다른 규칙도 함께 안전해진다). ③ test-guards 에 "비-UTF-8 FIX 문서 → 출력이 유효 JSON 이고 deny" 케이스. |
| **F-27-3** | 규칙 6 은 `git diff --cached` 만 본다. `git commit -a -F …`, `git commit -F … app/a.py`(pathspec), `git commit --include app/a.py -F …` 는 **스테이징 없이** `app/` 를 커밋에 넣으므로 staged 목록이 비어 "제품 코드 무변경" 으로 통과한다. `/commit` 스킬 106행은 `-A`·`.` 만 금지한다. | §B 3~5행 | commit-guard 의 `case "$cmd"` 에 ` -a`/`--all`/`--include`/`--only`/`-o`/`-i` 와 `-F <초안>` 뒤 추가 인자(pathspec)를 deny 로 추가("커밋 대상은 `git add` 명시 경로로만"). test-guards 케이스 3개. |
| **F-27-4** | `_verification_line_ok`(41~59행)는 `검증:` 줄에 `verifier` 가 있고 `(` 로 시작하지 않으면 통과 → `검증: 보류 — verifier (fable) … [필수] 2건`, `검증: 통과 — 메인 세션 (verifier 생략)`, `검증: verifier 에게 요청 예정` 이 모두 allow. verifier 의 **보류** 판정이 게이트를 연다. 패키지 흐름은 `결과: 통과`(stage-gate:96)와 `검증자: verifier`(verify-plan:86)를 따로 보는데 FIX 는 한 줄에 둘을 합쳤으니 둘 다 요구해야 등가다. | §C 1~4행 | 정규식을 `^검증:\s*통과\b.*verifier` 로(stage-gate 와 같은 `통과` 술어). 자리표 검사(`(`)는 그대로 두어도 되나 `통과` 요구로 사실상 흡수된다. test-guards 에 "보류 — verifier → DENY" 케이스. |

### [권고] — 커밋을 막지 않음, 다음 작업 단위에서

- **R-27-1 제목 패턴.** `TITLE_RE` 가 대소문자·공백·유형·복수 ID·선행 빈 줄·BOM 에 약하다: `Fix(FIX-999)`, `fix (FIX-999)`, `fix(FIX-999, FIX-998)`, `feat|docs|harness|chore(FIX-999)`, 첫 줄이 빈 줄(git 은 strip 하므로 실제 제목은 2행), UTF-8 BOM, 본문 `Refs: FIX-nnn` 만 있는 경우 — 전부 allow(§A). 이 저장소는 `docs(FIX-nnn)`·`harness(FIX-nnn)` 제목을 실제로 쓴다(`git log`, app/ 변경은 없었음). 권장: 첫 비공백 줄에서 `re.I` 로 `^[a-z]+\s*\(\s*FIX-(\d+)` 를 보고, 더 단순하게는 **초안 어디든**(제목·`Refs:`) `FIX-(\d+)` 가 있으면 그 번호 전부에 대해 검사. 유형 제한(fix/test)은 보호 효과보다 우회 면이 크다.
- **R-27-2 인용 경로.** `core.quotepath` 기본값에서 비-ASCII 파일명은 `"app/\355\225\234.py"` 처럼 따옴표 인용으로 나와 `startswith("app/")` 가 실패한다(§B 2행). `git -c core.quotepath=off diff --cached --name-only -z` 로 받고 `\0` 분리.
- **R-27-3 review 문서 판정.** FIX-027.md 수정안 B 는 "존재(스테이징 또는 HEAD)" 인데 구현(`fix_guard_check.py:26~27, 112`)은 디스크 존재만 본다 — 0바이트 빈 파일, `검토자:` 줄 없는 파일, untracked 파일이 모두 통과(§C 8~10행). 리뷰 문서가 커밋에 함께 실리지 않으면 이력에 증거가 남지 않는다. 권장: `git ls-files --cached --error-unmatch docs/wiki/fixes/review-FIX-nnn.md`(추적 또는 스테이징) + 파일에 `^검토자:.*verifier` 줄 요구. 계획 문장과 구현 중 하나를 맞춘다.
- **R-27-4 절차 문장.** SKILL 55행 verifier 위임에 L-004 문구(AskUserQuestion → `approve-commit.sh --stage verifier`)를 54행처럼 명시. CLAUDE.md 113행·SKILL 54행 "backend-agent 에 위임" 은 평가 산출물(`evaluation/`·`reports/`) FIX 면 eval-agent 가 맞으므로 "구현 에이전트(backend-agent·eval-agent)" 로. 자리표 문구(SKILL 52행 vs 템플릿 15행) 통일. 기획서 정합성 영향 없음.
- **R-27-5 보호 범위(위임 질문 4).** 넣어야 한다고 본다. 근거: ① `stage-gate.sh` 면제 경로(`docs/*|.claude/*|.githooks/*|.github/*|…`) 때문에 훅·CI 변경은 **활성 작업·계획 검증·승인 어느 게이트도 거치지 않는** 저장소에서 가장 느슨한 쓰기다 — 제품 코드보다 느슨하다. ② 이 저장소의 가드 결함 이력이 전부 하네스 자체 변경에서 나왔다: FIX-002(게이트가 재설계 전 패키지를 봄), FIX-003("verifier 가 콜론 하나 때문에 조용히 사라져 있었다"), FIX-008(인터프리터 이름), FIX-013(커밋 후처리 누락), FIX-014 후보(Bash 쓰기 우회). ③ 바로 이 FIX 가 하네스만 바꿨는데 독립 리뷰에서 [필수] 4건이 나왔다. ④ 교착 위험은 없다 — 규칙 6 은 커밋 시점에 문서 두 개만 보므로 깨진 훅을 고치는 작업 자체를 막지 않는다. 권장: 대상 접두사를 `app/ alembic/ .claude/hooks/ .claude/scripts/ .claude/settings.json .github/workflows/` 로 넓히고, 제목 유형 제한을 푼다(R-27-1). 범위 결정은 사용자 몫이므로 별도 FIX 로 올려 승인받을 것.
- **R-27-6 Windows 증거.** 로컬 증거는 Mac 만. CI(`.github/workflows` windows job 147행, FIX-022)가 `test-guards.sh` 를 Git Bash 로 돌리므로 dev2 푸시 후 그 결과를 FIX-027.md 결과 절에 링크로 남길 것. `$(dirname "$0")/../scripts/…` 경로 인자는 `test-guards.sh:224` 선례와 같은 형태라 추가 위험은 보지 않는다.

## 5. 결론

의도한 다섯 케이스와 기존 규칙 1~5 는 증거대로 동작하고, pytest·ruff·mypy 는 구현자 주장과 일치한다. 그러나 F-27-1 은 절차 자체를 교착시키고, F-27-2 는 이 FIX 의 핵심 주장(fail-closed)을 깨며, F-27-3·F-27-4 는 게이트를 한 플래그·한 단어로 지나간다. **보류** — 네 건을 닫고(backend-agent), test-guards 에 해당 케이스를 추가한 뒤 재리뷰를 요청할 것. `FIX-027.md` 의 `검증:` 줄은 `보류 — review-FIX-027.md [필수] 4건` 으로 둔다.

작업 트리 참고: 검토 시작 시 `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md` 가 미커밋 변경 상태였다. 내가 만든 파일은 이 문서와 `evidence/20261006-1613-review-fix027-bypass.txt` 뿐이며 `.env` 는 열지 않았다.

---

# 재리뷰 (재작업분 커밋 전) — 2026-10-08

검토자: verifier (fable) · 2026-10-08 13:21 · 기준 HEAD `1ddab52` + 작업 트리 미커밋 diff(`.claude/hooks/commit-guard.sh` +37 · `stage-gate.sh` +24 · `.claude/scripts/test-guards.sh` +197 · `fix_guard_check.py` 신규 234행 · `SKILL.md` · `CLAUDE.md` · `templates/fix.md` · `FIX-027.md`) · Refs: FIX-027 L-002 L-004 원칙8

**판정: 보류** — [필수] 2건(F-27-5, F-27-6), [권고] 3건(R-27-7~R-27-9), 이월 2건(R-27-2, R-27-6). 첫 리뷰 [필수] 4건 중 **F-27-1·F-27-2 는 닫혔고 F-27-3·F-27-4 는 부분**이다. 채택된 권고 R-27-1·R-27-3·R-27-4·R-27-5 는 합의한 범위 안에서 닫혔다. 코드·훅·계획은 고치지 않았다(이 절과 `FIX-027.md` 의 `검증:` 한 줄, `evidence/20261008-1321-review-fix027-*` 만 썼다).

보류 요지: (1) **F-27-3 의 "pathspec 커밋 우회 → deny" 가 `-F` 뒤 한 자리만 막는다.** 규칙 2 가 허용하는 `--file=`/`--file ` 형태 뒤의 경로, `-F` **앞**에 둔 경로, `--pathspec-from-file=` 은 전부 allow 이고, 격리 저장소에서 실제로 `git commit` 이 미스테이징 `app/a.py` 를 커밋에 넣는 것까지 재현했다. 게다가 `test-guards.sh` 의 F-27-3 세 케이스는 승인 마커가 없는 실제 저장소에서 돌아 **검사를 제거해도 규칙 1 로 DENY** 된다 — 항상 통과하는 테스트다(변이 시험). (2) **F-27-4 의 "통과 + verifier 둘 다" 는 두 단어가 한 줄에 있기만 하면 통과한다.** `검증: 통과 — 메인 세션 (verifier 생략)`(첫 리뷰 F-27-4 의 예시 그대로)·`검증: 통과 — verifier 리뷰 생략(문서만)` 이 allow 다. 구현자의 재시험 증거(`20261006-1700-…-bypass-retest.txt` 41·44·45행)에 이 `!!` 3건이 그대로 찍혀 있는데 FIX-027.md·HANDOFF·journal 어디에도 설명이 없다(grep 0건) — 증거 파일을 열지 않고 "재작업 완료" 로 보고된 셈이다.

## R1. 직접 실행한 것

| 명령 | 결과 | 증거 |
|---|---|---|
| `bash .claude/scripts/test-guards.sh` | `== 결과: 실패 0 ==`, ok 158줄(새 절: F-27-3 3 · verifier 게이트 25 · F-27-1 2 · R-27-5 9) | `evidence/20261008-1321-review-fix027-test-guards.txt` |
| `bash docs/wiki/fixes/evidence/20261006-1700-fix027-rework-bypass-retest.sh`(구현자 스크립트 그대로) | ok 40 · **`!!` 3**(41·44·45행 — 구현자 증거와 동일) | `evidence/20261008-1321-review-fix027-bypass-retest.txt` |
| 새 우회·예외 하네스 72건(A 플래그·인자 14 · A2 실제 커밋 3 · B 제목 12 · C 검증 줄 11 · D fail-closed 5 · E 회귀 10 · F 이 커밋 2 · G stage-gate 12 · H 변이 2) | 기대와 다른 것 **25건**(A 5 · B 9 · C 7 · H 셋업 오류 1, 나머지 메모) | `evidence/20261008-1321-review-fix027-rereview-bypass.{sh,txt}` |
| 변이 시험(복사본에서 F-27-3 두 grep 제거) | 실제 저장소: 세 케이스 여전히 DENY(규칙 1) / 격리 저장소+마커: 셋 다 allow 로 뒤집힘 | `evidence/20261008-1321-review-fix027-mutation.{sh,txt}` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` · `ruff check … .claude/scripts/fix_guard_check.py` · `scripts/mypy_check.py --run` | `1840 passed, 1 warning` · `All checks passed!` · `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` — 구현자 17:00 증거와 일치 | rereview-bypass.txt 끝 3줄 |

## R2. 첫 리뷰 항목별 닫힘 여부

| 항목 | 판정 | 근거(코드 + 내가 돌린 것) |
|---|---|---|
| **F-27-1** stage-gate 교착 | **닫힘** | `stage-gate.sh:103~104` `^계획 점검:\s*통과` 또는 `^검증:\s*통과` + `^승인:`. test-guards "F-27-1" 2케이스 ok(새 템플릿·옛 템플릿). 내 G 절: `active: FIX-999`(계획 점검: 통과 + 승인)로 `.claude/hooks/x.sh` 쓰기 allow — 활성 패키지 없이도 훅 수리 가능, 교착 없음. `stage-gate.sh:9~13` 주석·SKILL 3단계에 역할 분담 명시. |
| **F-27-2** 예외 → 깨진 JSON | **닫힘** | `commit-guard.sh:42~44` `deny()` 가 `json.dumps` 사용(규칙 1~6 공통). `fix_guard_check.py:98~101, 117~122`(`UnicodeDecodeError` 직접 처리) + `main()` 224~229 포괄 처리 rc 2, 한 줄로 접음. 내 D 절 5경로(초안 비-UTF-8 → outer except 경로 · review 비-UTF-8 · review 가 디렉터리 · ROOT 에 따옴표·공백 · git 저장소 아님) 전부 DENY + `json.load` 성공. test-guards "F-27-2" 2줄 ok. |
| **F-27-3** 스테이징 우회 | **부분(→ F-27-5)** | 막힘: `-a`/`--all`/`-i`/`--include`/`-o`/`--only`(`commit-guard.sh:72`), `-F <초안>` 뒤 인자(75행), `-- app/a.py`, `-aF`/`-am`(규칙 2 가 막음), `git -c … commit -a`. **열림**(A 절): `git commit --file=.claude/commit-draft.txt app/a.py` · `--file .claude/commit-draft.txt app/a.py` · `git commit app/a.py -F .claude/commit-draft.txt` · `git commit --pathspec-from-file=paths.txt -F …` — 넷 다 allow, A2 절에서 실제 git 이 `app/a.py | 2 +-` 를 커밋. 원인: 75행 정규식이 `-F` 한 형태의 **뒤**만 보는데 규칙 2(82행)는 `--file=`·`--file ` 도 허용한다. test-guards 세 케이스는 변이 시험 (a) 처럼 검사 없이도 DENY(마커 없음) → 증거 아님. |
| **F-27-4** 보류도 통과 | **부분(→ F-27-6)** | 막힘: `검증: 보류 — verifier …`·`검증: 통과 — 메인 세션`·`검증: verifier 에게 요청 예정`·`통과하지 못함 — verifier`(C 절, test-guards 2케이스). **열림**(C 절 7건): `검증: 통과 — 메인 세션 (verifier 생략)`(첫 리뷰 F-27-4 예시) · `통과(점검표 1~8) — verifier 리뷰는 아직` · `통과 — verifier 리뷰 생략(문서만)` · `통과 — 메인 세션, verifier 는 다음 커밋에서` · `통과 — verifier 아님` · `검증:` 줄 두 개(자리표 + `## 결과` 의 통과) · `보류` 줄 뒤에 옛 `통과` 줄 잔존. 원인: `fix_guard_check.py:102` `^검증:\s*통과\b.*verifier` — `.*` 가 "verifier" 를 어디서든 받고, 103~105행이 **어느 한 줄**만 맞으면 True. (첫 리뷰 F-27-4 권장 정규식을 그대로 쓴 것이고 그 정규식이 느슨했다 — 내 권고의 결함이기도 하다. 그러나 구현자 재시험이 `!!` 로 잡았는데 보고되지 않았다.) |
| **R-27-5** 보호 경로 | **닫힘** | `stage-gate.sh:79~81` — 네 경로를 면제 case 앞에 두어 게이트로 떨어뜨림. test-guards "R-27-5" 9케이스 ok(활성 없음 4 DENY · skills 면제 · 실제 저장소 4 allow). 내 G 절: 실제 저장소(`active: P7-push`, 02-plan-verify 통과·승인)에서 훅·스크립트·settings·workflow 전부 allow, `commit-draft.txt`·`gitlog.md`·skills·agents·CURRENT 도 allow(면제 유지). 02-plan-verify 없는 패키지로는 DENY(실제로 건다). 메모: `frozen: CR-xxx` 중에는 훅 경로도 막힌다(R-27-9). |
| **R-27-1** 제목 유형·정규화 | **닫힘(합의 범위)** | `fix_guard_check.py:45~49, 52~64, 67~84` — 유형 `[a-z]+` 무엇이든·대소문자·괄호 앞뒤 공백·BOM·선행 빈 줄·복수 ID·번호 정규화(`FIX-27`→`FIX-027.md`). test-guards 12케이스 ok, retest A 절 15건 ok. 합의 밖 형태는 R-27-7. |
| **R-27-3** review 문서 기준 | **닫힘** | `fix_guard_check.py:109~141` — `is_file`·`st_size>0`·`^검토자:.*verifier`(대소문자 무시)·`git ls-files --cached --error-unmatch`. test-guards 4케이스 ok(0바이트·검토자 없음·untracked DENY, 스테이징 allow). 내 D 절: 비-UTF-8·디렉터리도 DENY. |
| **R-27-4** 절차 문장 | **닫힘** | SKILL 6단계 "`AskUserQuestion`으로 시작 승인 → `approve-commit.sh --stage verifier`(L-004 …)", 5단계·CLAUDE.md 113행 "구현 에이전트(`backend-agent`·`eval-agent`)", 자리표 문구 SKILL 3단계 = `templates/fix.md:15` 로 통일(`grep` 일치). |
| R-27-2 인용 경로 | 이월(구현자 명시 "이번 라운드 미처리") | retest 32행 `app/한글.py` allow 그대로. |
| R-27-6 Windows 증거 | 이월(CI 대기) | 로컬은 Mac 뿐. `_py.sh`·`json.dumps`·`subprocess` 리스트·`pathlib` 사용은 기존 `findings.py` 선례와 같아 추가 위험은 보지 않음. dev2 푸시 후 CI windows job 결과를 FIX-027.md 결과 절에 링크. |

## R3. 회귀·공통 동작

- 기존 규칙 1~5: 마커 없음·`-m`·해시 불일치·`--amend`·`--no-verify`·마커 조작 DENY, 정상 `feat` allow(retest D 절 7건, 내 E 절). `git log --all`·`git add -i`(commit 아님)에 오탐 없음. `git commit -F … && git push origin dev2` allow(오탐 없음).
- 비-FIX 커밋(`feat(P7-push)`·`docs(readme)` + app/) 규칙 6 미적용 allow. 문서만·훅만 바꾼 `fix(FIX-999)`/`harness(FIX-999)` 는 검증 줄 없어도 allow(E 절).
- stage-gate 정상 흐름: `.claude/*` 면제(hooks·scripts·settings 제외), docs 면제, L-003 대기, 새·옛 FIX 템플릿 호환(test-guards 전부 ok).
- Mac·Windows: 새 코드는 전부 `_py.sh` 경유 `$HOOK_PY`·표준 라이브러리·`replace("\\","/")`·`splitlines()`. Mac 증거만 있음(R-27-6).

## R4. 이 FIX-027 커밋 자체가 받는 요구(위임 질문 3)

- 규칙 6: 스테이징에 `app/`·`alembic/` 없음(현재 0개). 제목이 `harness(FIX-027)` 든 `fix(FIX-027)` 든 `fix_guard_check.py` rc 0(F 절) → 규칙 6 해당 없음. 리뷰 문서·`검증: 통과` 는 **훅이 요구하지 않는다**(절차상 SKILL 6단계 "훅·문서만 바꾸는 FIX … `검증:` 줄은 여전히 verifier 가 쓴다" 만 적용 — 이 절이 그것이다).
- stage-gate(R-27-5): 이 재작업이 쓴 `.claude/hooks/*`·`.claude/scripts/*` 는 `active: P7-push`(02-plan-verify `결과: 통과`·`승인:`)로 allow(G 절 실측). 교착 없음. 활성 패키지가 끝나 `active: none` 이 되면 훅 수정에는 `active: FIX-nnn`(계획 점검: 통과 + 승인) 등록이 필요하다 — SKILL 4단계 그대로.
- 따라서 **F-27-5·F-27-6 을 닫은 뒤** 같은 커밋으로 올릴 수 있다. 규칙 1~5 만 만족하면 통과한다.

## R5. 소견

### [필수]

| ID | 내용 | 재현 | 권장 조치(구현은 backend-agent) |
|---|---|---|---|
| **F-27-5** | F-27-3 미완. `commit-guard.sh:75` 가 `-F <초안>` **뒤** 인자만 막아, 규칙 2 가 허용하는 `--file=<초안>`·`--file <초안>` 뒤 경로, `-F` **앞** 경로, `--pathspec-from-file=`(-F 앞)이 통과한다. 실제 git 이 미스테이징 `app/a.py` 를 커밋에 넣는 것 재현. test-guards 의 F-27-3 세 케이스는 마커 없는 실제 저장소에서 돌아 검사와 무관하게 DENY(변이 시험 (a)) — 증거가 아니다. | rereview-bypass.txt A·A2 절, mutation.txt (a) | 정규식을 "뒤" 가 아니라 **허용 목록**으로: `git commit` 토큰 뒤에 남는 인자가 `-F <초안>`·`--file=<초안>`·`--file <초안>` 뿐이어야 allow, 그 외 토큰(`-` 로 시작하지 않는 경로, `--pathspec-from-file`, `--pathspec-file-nul`)은 deny. 예: `commit` 이후 문자열에서 초안 토큰을 제거한 뒤 `[^-[:space:]]` 로 시작하는 토큰이나 `--pathspec` 이 남으면 deny. test-guards 의 F-27-3 케이스를 **FG_T 절(격리 저장소 + 마커·초안)** 로 옮기고 `--file= app/a.py`·`app/a.py -F`·`--pathspec-from-file` 3케이스 추가. |
| **F-27-6** | F-27-4 미완. `fix_guard_check.py:102~105` — "통과" 와 "verifier" 가 **같은 줄 어디든** 있으면 True, 여러 `검증:` 줄 중 **하나만** 맞아도 True. `검증: 통과 — 메인 세션 (verifier 생략)`(첫 리뷰 F-27-4 예시)·`통과 — verifier 리뷰 생략(문서만)`·자리표 + `## 결과` 의 통과 줄·`보류` 뒤 옛 `통과` 잔존 — 7형태 allow. 구현자 재시험 증거 41·44·45행 `!!` 3건이 미보고. | rereview-bypass.txt C 절, bypass-retest.txt 41·44·45행 | ① 정규식을 `^검증:\s*통과\s*[—–-]+\s*verifier\b` 로 — 구분자 바로 뒤에 verifier(SKILL 6단계 예시 `검증: 통과 — verifier (fable) …` 그대로). ② `^검증:` 줄이 **둘 이상이면 거부**(FIX 문서에는 한 줄만 있어야 한다 — 템플릿도 한 줄)하거나 첫 줄만 본다. ③ test-guards 에 "통과 — 메인 세션 (verifier 생략) → DENY"·"검증: 줄 두 개 → DENY" 추가, retest 스크립트의 기대값과 증거 `!!` 0 확인. ④ FIX-027.md 결과 절에 재작업 증거(17:00)와 이 재리뷰 증거를 적고, 증거에 `!!` 가 남으면 반드시 설명한다(원칙8). |

### [권고]

- **R-27-7 제목 형태.** `TITLE_RE` 는 `<유형>(FIX-nnn[, FIX-mmm])` 만 본다. `fix(FIX-999 재작업)`·`fix(FIX-999/hooks)`·`fix(FIX-999; FIX-998)`·`fix-hooks(FIX-999)`·`fix2(FIX-999)`·`fix[FIX-999]`·`fix: FIX-999 …`·`FIX_999`·`FIX 999` 는 규칙 대상 밖(B 절 9건 allow, app/ 스테이징 상태). 합의한 R-27-1 범위 밖이라 권고로 둔다. 본문 전체 검색이 넓다는 구현자 논리는 타당하니 **제목 줄 한 줄 안에서** `FIX-?\s?(\d+)` 가 있으면 전부 대상으로 하는 중간안을 권한다(제목에 FIX 번호를 적고 app/ 를 바꾸는 커밋은 전부 FIX 커밋이다).
- **R-27-8 환경변수 접두.** `GIT_INDEX_FILE=/tmp/idx git commit -F …` 는 훅의 `git diff --cached` 가 보는 색인과 커밋이 쓰는 색인이 달라 규칙 6 이 빈 목록을 본다(A 절 마지막, allow). 드문 형태지만 `commit-guard.sh` 에서 `git` 앞에 `GIT_[A-Z_]+=` 가 붙으면 deny 하는 한 줄이면 막힌다. safety-guard 와 함께 다룰 것.
- **R-27-9 동결 중 훅 수리.** R-27-5 로 `.claude/hooks/*` 가 면제에서 빠지면서 `frozen: CR-xxx` 동안 훅·스크립트·CI 도 쓸 수 없다(G 절 메모). CR 이행 중 훅 결함이 드러나면 CR 해제 뒤에만 고칠 수 있다. 의도한 결과면 `stage-gate.sh` 주석·`/devlog change` 절차에 한 줄, 아니면 frozen 검사에서 네 경로를 예외로.

## R6. 결론

F-27-1·F-27-2·R-27-1·R-27-3·R-27-4·R-27-5 는 코드와 내가 돌린 시험으로 닫혔다. 그러나 F-27-3 은 `--file=`·pathspec 앞·`--pathspec-from-file` 로, F-27-4 는 "verifier 생략" 한 줄로 열려 있고, 둘 다 구현자 증거 또는 test-guards 가 잡지 못한다(한쪽은 `!!` 미보고, 한쪽은 항상 통과하는 테스트). **보류** — F-27-5·F-27-6 을 닫고 test-guards 에 실효 케이스를 넣은 뒤 재리뷰. `FIX-027.md` 의 `검증:` 줄은 `보류 — verifier 재리뷰 (review-FIX-027.md) [필수] 2건` 으로 둔다.

작업 트리 참고: 내가 만든 파일은 이 절과 `evidence/20261008-1321-review-fix027-{test-guards,bypass-retest,rereview-bypass,mutation}.txt`·`…-{rereview-bypass,mutation}.sh`(스크립트 두 개는 scratchpad 에서 `cp` 로 옮김) 뿐이다. `.env` 는 열지 않았다.

---

# 3차 리뷰 (2차 재작업분, 커밋 전) — 2026-10-08

검토자: verifier (fable) · 2026-10-08 13:50 · 기준 HEAD `1ddab52` + 작업 트리 미커밋 diff(`.claude/hooks/commit-guard.sh` +50 · `stage-gate.sh` +25 · `.claude/scripts/test-guards.sh` +248 · 신규 `commit_args_check.py` 115행 · `fix_guard_check.py` 236행 · `SKILL.md` · `CLAUDE.md` · `templates/fix.md` · `FIX-027.md`) · Refs: FIX-027 L-002 L-004 원칙8

**판정: 통과** — 재리뷰 [필수] F-27-5·F-27-6 모두 닫힘, 채택된 [권고] R-27-7·R-27-8·R-27-9 닫힘. 이번 리뷰에서 새로 연 것은 [권고] 4건(R-27-10~R-27-13)뿐이며 전부 (가) FIX-027 이전부터 있던 앞단 감지 구멍이거나 (나) 정상 절차에서 나오지 않는 형태이거나 (다) fail-closed 오탐이다. 코드·훅·계획은 고치지 않았다(이 절과 `FIX-027.md` 의 `검증:` 한 줄, `evidence/20261008-1350-review3-fix027-*` 9개만 썼다).

범위 기준(위임 지시 3): 이 훅은 LLM 이 실수·편의로 규칙을 지나가는 것을 막는 장치이고 악의적 우회 전부를 막는 보안 경계가 아니다. 따라서 **`/commit` 스킬 절차 안에서 실제로 나올 법한 형태**만 [필수] 후보로 보았다 — 스킬이 쓰는 명령은 `git add <명시 경로> …` → `git commit -F .claude/commit-draft.txt` → 별도 호출 `git push origin dev2` 셋뿐이다(`.claude/skills/commit/SKILL.md` 67~68·80행). 이 셋은 전부 allow 이고(T1 A-허용 절), 그 명령에 플래그·경로를 "덧붙이는" 모든 형태는 DENY 다(T1 A 절 29건·test-guards F-27-5 31건).

## T1. 직접 실행한 것

| 명령 | 결과 | 증거 |
|---|---|---|
| `bash .claude/scripts/test-guards.sh` | `== 결과: 실패 0 ==`, ok 208(F-27-5 31 · R-27-8 2 · F-27-4 3 · F-27-6 9 · F-27-2 2 · R-27-3 4 · R-27-1 12 · R-27-7 10 · stage-gate F-27-1 2 · R-27-5 9) — 구현자 `…-rework2-test-guards.txt` 와 동일 | `evidence/20261008-1350-review3-fix027-test-guards.txt` |
| 재리뷰 스크립트 `20261008-1321-review-fix027-rereview-bypass.sh` 재실행 | ok 61 · `!!` 4(51·52·124·125행) — 구현자 보고와 동일. 판정은 T2 "구현자 설명" | `…-review3-fix027-rereview-rerun.txt` |
| 구현자 변이 시험 `…-rework2-mutation.sh` 재실행 | F-27-5 7/7 · F-27-6 3/3 뒤집힘 — 케이스가 검사를 실제로 본다 | `…-review3-fix027-mutation-rerun.txt` |
| 새 우회·회귀 하네스 103건(A 셸 문법 29 · A-허용 11 · A-전치 10 · A-환경 7 · B 검증 줄 27 · C 제목 8 · D 이 커밋 7 · E stage-gate 8) | ok 69 · `!!` 11 · 메모 23. `!!` 11건의 분류는 T3 | `…-review3-fix027-bypass.{sh,txt}` |
| 보충 3건(HEAD 훅 비교 11행 · `>(cat)` 실제 git · C절 정정) | 앞단 구멍 8형태는 HEAD 훅과 동일 · `>(cat)`/`<(true)` 는 git 이 `outside repository` 로 실패 · 정정 케이스 allow | `…-review3-fix027-extra.{sh,txt}` |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` · `scripts/mypy_check.py --run` · `ruff check .claude/scripts/{commit_args_check,fix_guard_check}.py` | `1840 passed, 1 warning` · `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` · `All checks passed!` | `…-review3-fix027-regression.txt` |

## T2. 재리뷰 항목별 닫힘 여부

| 항목 | 판정 | 근거(코드 + 내가 돌린 것) |
|---|---|---|
| **F-27-5** `--file=`·pathspec 앞·`--pathspec-from-file` 우회, test-guards 케이스 무효 | **닫힘** | `commit_args_check.py:45~101` 허용 목록(`-F <초안>`·`--file=<초안>`·`--file <초안>` 외 토큰은 전부 거부, 전역 옵션 `-c/-C/--git-dir/--work-tree` 건너뜀, 따옴표 불일치·commit 미발견도 거부), `commit-guard.sh:83~88` 호출. test-guards F-27-5 케이스는 **FG_T 격리 저장소 + 마커·초안**에서 돌고(`test-guards.sh:184~201`) 변이 시 7/7 뒤집힘(T1). 내 A 절: 따옴표 3형·이스케이프·`$(…)`·백틱·`\`줄바꿈·서브셸+cd·`env`/`command`/`exec`·공백 없는 `;`/`&&`·전역 옵션 3형·`-n`·`-q`·`-F`붙여쓰기·`--`·리다이렉션 뒤 경로·변수 경로·`$'…'`·파이프 뒤 전부 DENY, deny 출력은 따옴표·역슬래시가 섞여도 유효 JSON. 재리뷰 A·A2 의 네 형태(`--file= 경로`·`--file 경로`·`경로 -F`·`--pathspec-from-file`) 모두 DENY(rereview-rerun A 절). 부수 효과: HEAD 규칙 4 가 문자열 `--no-verify` 만 봐서 열려 있던 단축형 `-n` 도 허용 목록이 막는다. |
| **F-27-6** `검증:` 줄 느슨한 일치·복수 줄·`!!` 미보고 | **닫힘** | `fix_guard_check.py:49~50, 100~108` — `^검증:\s*통과\s*[—–-]+\s*verifier\b`(대소문자 무시) + `^검증:` 줄 정확히 1개 + 부정어 9개. 재리뷰 C 절 7형태(`메인 세션 (verifier 생략)`·`통과(점검표…) — verifier 리뷰는 아직`·`리뷰 생략(문서만)`·`verifier 는 다음 커밋에서`·`verifier 아님`·자리표+결과 줄·보류+옛 통과) 전부 DENY(rereview-rerun C 절·test-guards F-27-6 9건), 변이(옛 정규식) 시 3/3 뒤집힘. 구현자 재시험 재실행 `…-rework2-retest-1700.txt` 는 ok 43 · `!!` 0 이고 FIX-027.md 2차 재작업 절이 지난 `!!` 3건을 실제 우회로 설명했다(원칙8 충족). 내 B 절: 부정어 8형태 DENY, SKILL 6단계 예시 줄·이번 리뷰가 쓸 줄·들여쓴 줄 allow, `**검증:**`·`검증 :`·`·` 구분자·`(verifier…)` 괄호는 DENY(fail-closed). 목록의 한계는 R-27-12. |
| **R-27-7** 제목 형태 | **닫힘(합의 범위)** | `fix_guard_check.py:47` `ID_RE = fix-0*(\d+)` 로 제목 줄 전체 검색. test-guards R-27-7 10건, 내 C 절 `Fix-999`·`fix-0999`·`harness(FIX-999)` DENY, 본문 Refs 만 있는 제목은 allow(extra (3)). `FIX_999`·`FIX 999` 는 사용자 결정(`FIX-\d+` 한정) 범위 밖 — 구현자 설명 타당. 왼쪽 경계 없음 오탐은 R-27-13. |
| **R-27-8** `GIT_*=` 접두 | **닫힘** | `commit-guard.sh:80~82`. test-guards 2건 + 내 A-환경 `export GIT_INDEX_FILE=…;`·`env GIT_INDEX_FILE=…`·`GIT_DIR=… GIT_WORK_TREE=…` DENY, `FOO=1 git commit` 은 allow(오탐 없음). `-c core.hooksPath=` 는 commit-guard allow 이나 safety-guard 가 DENY(역할 분담 확인). |
| **R-27-9** frozen 중 훅 수리 | **닫힘(의도 주석)** | `stage-gate.sh:84` 한 줄 — 사용자 결정대로 주석만. |
| R-27-2 인용 경로 · R-27-6 Windows CI | 이월 | 변경 없음. R-27-6 은 dev2 푸시 후 CI windows job 결과를 FIX-027.md 결과 절에 링크할 것. |

**구현자 설명의 타당성(위임 지시 1)**: 재리뷰 스크립트의 `!!` 4건 중 ① `fix(FIX_999)`·`fix(FIX 999)` 는 합의 범위(`FIX-\d+`) 밖이므로 타당. ② H절 변이 2건은 sed 가 바꾸려는 문구(`pattern = re.compile(r"^검증:…`·`(-a|--all|-i|--include|-o|--only)`)가 현재 코드에 **0건**이라(regression.txt) 변이가 적용되지 않은 채 원본과 같은 판정을 낸 것 — "변이 무효" 설명이 사실이고, 대체한 `rework2-mutation.sh` 는 새 구조(스크립트 교체·정규식 되돌리기)를 실제로 변이해 10/10 뒤집힘을 내가 재실행으로 확인했다.

## T3. 새 우회 시도 결과 — `!!` 11건의 분류

| 분류 | 건 | 형태 | 실제 영향 | 소견 |
|---|---|---|---|---|
| (가) 앞단 감지 구멍 | 8 | `(git …)`·`/usr/bin/git`·`git.exe`·`bash -c "git …"`·`sh -c '…'`·`eval "…"`·`$(git …)`·`git -c alias.ci=commit ci` | `commit-guard.sh:63` grep 이 `git` 앞 글자를 `;&|공백·행머리`만 허용해 이 형태들은 **git commit 으로 인식되지 않고 규칙 1~6 전체가 건너뛰어진다**(마커 없이도 allow). HEAD 훅과 결과가 11행 전부 동일(extra (1)) — FIX-027 이전부터 있던 구멍이고 이 FIX 의 회귀가 아니다. `commit_args_check.py:100` 의 "bash -c 등 감춰진 형태 거부" 는 이 grep 을 통과한 뒤에만 작동하므로 실제로는 닿지 않는다. | **R-27-10** |
| (나) stdin 인자 주입 | 1 | `echo app/a.py \| xargs git commit -F <초안>` | 파서는 글자 그대로의 인자만 보므로 allow, 실제 git 이 `app/a.py` 를 커밋에 넣는다(bypass.txt A-전치 재현). | **R-27-11** |
| (다) 실질 우회 아님 | 1 | `git commit -F <초안> >(cat) app/a.py` | 파서가 `>(` 뒤 두 토큰을 리다이렉션으로 건너뛰어 allow 하지만, git 이 `/dev/fd/63 is outside repository` 로 실패해 커밋되지 않는다(extra (2), `<(true)`·`2>(cat)` 도 실패). | 메모 |
| (라) 검토자 라벨 오류 | 1 | C절 `feat(P7-push): 접두사 처리 (Refs 본문에만 FIX-999)` | 제목 괄호 안에 FIX-999 를 써 놓고 "제목에 없음" 이라 라벨했다 — DENY 가 맞다. 정정 케이스(본문 Refs 에만) allow(extra (3)). | 없음 |

메모(판정에 넣지 않음): ① `-F '<초안>'`(단따옴표)·`-F  <초안>`(이중 공백)은 파서 allow 지만 `commit-guard.sh:93` 규칙 2 case 가 DENY — 불일치지만 fail-closed 이고 스킬 명령은 정확히 한 형태다. ② `'&&' app/a.py` 처럼 인용된 연산자는 파서가 구분자로 보지만 git 이 pathspec 오류로 실패. ③ 부정어 목록 밖 표현 10형태(`미검토`·`리뷰 없이`·`없음`·`스킵`·`(메인 세션 작성)`·`불필요`·`TODO`·`보류`·`(보류, [필수] 2건)`·`추후`)는 allow, 반대로 정상 판정 줄에 `제외`·`예정`·`아직` 이 들어가면 DENY(오탐) — R-27-12. ④ `hotfix-999`·`prefix-3` 가 FIX 번호로 잡힌다 — R-27-13. ⑤ 구현자 ruff 증거의 3건은 전부 `.claude/scripts/findings.py` 기존 오류로 이 FIX 범위 밖(구현자가 보고함).

## T4. 회귀·공통 동작(위임 지시 2)

- 기존 규칙 1~5: 마커 없음·`-m`·`--amend`·`--no-verify`(safety-guard)·마커 조작·해시 불일치 DENY, 정상 `feat`/`docs` + app/ allow(test-guards·rereview-rerun E 절). `git log --all`·`git add -i`·`git status` 오탐 없음.
- 비-FIX 커밋·문서만 바꾼 FIX·훅만 바꾼 `harness(FIX-999)`: 검증 줄 없어도 allow(rereview-rerun E 절).
- stage-gate: 새·옛 FIX 템플릿 호환(F-27-1 2건), R-27-5 보호 경로 9건, L-003 대기 3건 ok. 실제 저장소(`active: P7-push`)에서 이 FIX 가 쓴 훅·스크립트·settings·workflow·app/·docs 경로 전부 allow(bypass.txt E 절).
- Mac·Windows: 새 코드는 `_py.sh` 경유 `$HOOK_PY`·표준 라이브러리(`shlex` posix·`re`·`subprocess` 리스트·`pathlib`)·`json.dumps` 로 훅 출력 항상 유효 JSON(A 절 2건·F-27-2 2건). 로컬 증거는 Mac 뿐(R-27-6 이월). `shlex(posix=True)` 는 Windows 역슬래시 경로(`-F .claude\commit-draft.txt`)를 이스케이프로 읽어 DENY 하지만 스킬은 슬래시 경로만 쓴다 — fail-closed.

## T5. 이 커밋 자체(위임 지시 4)

- 규칙 6: 스테이징 app/·alembic/ 0개 → 제목이 `harness(FIX-027)`·`fix(FIX-027)`·`harness(hooks): FIX-027 …` 어느 것이든 `fix_guard_check.py` rc=0(해당 없음). 규칙 5b: 스킬 명령 `git commit -F .claude/commit-draft.txt` → `commit_args_check.py` rc=0. 실제 저장소(마커 없음)에서 훅 판정은 규칙 1 "승인 마커가 없다" 뿐 — 승인 뒤에는 규칙 1~5 만 만족하면 통과한다.
- 교착 없음: `FIX-027.md` 의 `^검증:` 줄은 1개, `review-FIX-027.md` 에 `검토자: verifier` 줄 존재. 이 두 문서를 격리 저장소에 복사해 **app/ 를 바꾸는 FIX 로 가정**했을 때 — 현재(보류) 줄로는 DENY(맞음), 줄을 `검증: 통과 — verifier 3차 리뷰 (review-FIX-027.md)` 로 바꾼 사본으로는 allow(bypass.txt D 절). 이 절을 쓴 뒤 `FIX-027.md` 의 `검증:` 줄을 그 형태로 갱신했다.
- stage-gate: 위 T4 — 교착 없음.

## T6. 소견

### [필수] — 없음

### [권고] — 커밋을 막지 않음, 별도 FIX 로

- **R-27-10 앞단 감지 정규식(기존 구멍, FIX-027 회귀 아님).** `commit-guard.sh:53, 63` 의 `(^|[;&|[:space:]])git(…)[[:space:]]+commit` 은 `(git`, `"git`, `'git`, `$(git`, `/usr/bin/git`, `git.exe`, 그리고 `-c alias.x=commit x` 를 git commit 으로 보지 않아 **규칙 1(승인 마커)부터 6까지 전부** 건너뛴다(extra (1): HEAD 훅과 동일). 정상 절차에서 나오는 형태가 아니라 [권고] 로 두지만, 영향이 규칙 6 이 아니라 승인 절차 전체라는 점에서 다음 하네스 FIX 의 첫 항목으로 권한다. 권장: 감지도 `commit_args_check.py` 의 토큰 파서로 옮겨(`git`/`git.exe`/`…/git` 토큰 뒤 서브커맨드가 `commit` 또는 `alias.*=commit` 의 별칭이면 감지; `found==0` 은 "commit 아님" 으로 별도 종료 코드) bash grep 은 1차 필터로만 두거나, 최소한 grep 의 앞 글자 클래스에 `("'$/` 와 `git(\.exe)?` 를 더한다. `bash -c`/`sh -c`/`eval` 은 인용 안 문자열까지 shlex 가 풀어 주므로 같은 파서에서 잡힌다. test-guards 케이스 8개.
- **R-27-11 `xargs git commit`.** 파서가 보지 못하는 stdin 주입(`… | xargs git commit -F <초안>`)으로 미스테이징 `app/a.py` 가 실제 커밋된다(bypass.txt A-전치). 정상 절차 밖 형태. 권장: `git` 토큰 **앞** 토큰이 `xargs`(옵션 포함)이면 거부 — 한 줄. test-guards 1건.
- **R-27-12 부정어 목록의 한계와 오탐.** `fix_guard_check.py:50` 은 블랙리스트라 `미검토`·`없음`·`스킵`·`보류`·`추후`·`(메인 세션 작성)` 등은 통과하고(B 절 10형태), 반대로 verifier 의 정상 판정 줄에 `제외`·`예정`·`아직` 같은 평범한 단어가 들어가면 DENY 된다(B 절 오탐 3건). 훅은 정규식 형태를 그대로 베껴 쓴 위조와 진짜 판정을 구별할 수 없으므로 실질 통제는 L-002 절차 + review 문서 `검토자:` + git 추적이다. 목록 확장은 권하지 않는다(끝이 없다). 권장: `templates/fix.md:15` 자리표 또는 SKILL 6단계에 "`검증:` 줄은 `통과 — verifier (fable) <날짜>, review-FIX-nnn.md` 한 형태로만 쓰고 부정·유보 어휘(생략·아직·예정·아님·않·못·미실시·제외·대신)를 넣지 않는다" 한 줄, 그리고 `fix_guard_check.py` 모듈 docstring 에 블랙리스트의 한계를 명시.
- **R-27-13 `ID_RE` 왼쪽 경계.** `fix-0*(\d+)` 에 경계가 없어 `hotfix-999`·`prefix-3`·`suffix-N`·`bugfix-N` 이 FIX 번호로 잡히고, app/ 를 바꾸는 feat 커밋이 존재하지 않는(또는 옛 템플릿의) FIX 문서를 이유로 DENY 된다(C 절 메모 2건, fail-closed 오탐). 권장: `(?<![a-z])fix-0*(\d+)`(re.I). test-guards 1건(`feat(P7-push): hotfix-999 적용` + app/ → allow).

### 이월
R-27-2(인용 경로) · R-27-6(Windows CI 증거 — dev2 푸시 후 링크).

## T7. 결론

F-27-5·F-27-6 은 코드(허용 목록 파서·정규식+단일 줄+부정어)와 내가 돌린 시험(test-guards 208 ok, 재리뷰 스크립트 61 ok, 변이 10/10, 새 하네스 103건)으로 닫혔고, 채택 권고 3건도 닫혔다. 남은 `!!` 는 전부 FIX-027 이전부터 있던 앞단 구멍·정상 절차 밖 형태·실질 우회 아님·검토자 라벨 오류로 분류되며 [필수] 는 없다. **통과** — `FIX-027.md` 의 `검증:` 줄은 `검증: 통과 — verifier 3차 리뷰 (review-FIX-027.md)` 로 쓴다(새 정규식·단일 줄·부정어 규칙을 격리 저장소에서 확인, bypass.txt D 절 + 갱신 후 재확인은 `…-review3-fix027-selfcheck.txt`). 원칙8(3회 재검증) 기준으로 이 FIX 는 여기서 닫히고, R-27-10~13 은 별도 FIX 로 사용자가 정한다.

작업 트리 참고: 내가 만든 파일은 이 절과 `FIX-027.md` 의 `검증:` 한 줄, `evidence/20261008-1350-review3-fix027-{test-guards,rereview-rerun,mutation-rerun,regression,bypass,extra,selfcheck}.txt`·`…-{bypass,extra}.sh`(전부 Write 툴로 저장, Bash 쓰기 없음) 뿐이다. `.env` 는 열지 않았다. 코드·훅·계획·구현자 증거는 손대지 않았다.
