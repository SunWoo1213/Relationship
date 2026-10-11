# review-FIX-033 · 위임·검증 절차 보강(문서만) 커밋 전 리뷰

검토자: verifier (fable) · 2026-10-11 · 기준 HEAD `22a6822` + 작업 트리 미커밋 diff(대상 5파일 +25/-3) · Refs: FIX-033 FIX-014 FIX-032 L-002 L-004 원칙8 R-U1-1 R-U1-3 R-31-3 R-14-7

**결과: 통과 (재검증 2026-10-11 — 1차 판정: 보류)** — 1차: [필수] 1건(R-33-1), [권고] 7건(R-33-2~8). 재검증(아래 "재검증 (2026-10-11)" 절)에서 R-33-1·2·3·4·6 해소 확인, R-33-5·7·8 은 선택/후속으로 열어 둠, 새 권고 R-33-9 1건. 아래 1차 본문은 그대로 보존한다. (1차 원문) 문서만 바꾸는 FIX 라 review 문서를 생략할 수 있지만(`SKILL.md` 56행), 판정 근거를 남기기 위해 쓴다. 코드·훅·계획·카드는 고치지 않았고 `FIX-033.md` 의 `검증:` 줄도 비워 두었다(보류이므로).

보류 요지: 새 규칙 (a)~(d) 와 devlog SKILL 문구는 실제 사고 4건(R-U1-1·R-U1-3·R-31-3·R-14-7)에 각각 대응하고 기존 규칙과 충돌하지 않는다(§3·§4). 범위는 `.md` 5파일로 깨끗하고 test-guards 실패 0 이다(§2). 그러나 `verification.md` 의 새 절 "변이 시험 방법" 1번째 항목이 지시하는 `mktemp -d` 는 이 Mac 에서 `/var/folders/…/T/tmp.XXXX`(= `$TMPDIR`) 를 만든다 — **스크래치패드가 아니다.** 같은 절 4번째 항목 "스크래치패드 밖으로 Bash 쓰기를 하지 않는다" 와 모순이고, 1번째 항목의 근거 "(스크래치패드가 세션과 함께 사라진다)" 는 그 경로에 해당하지 않으며, 그 리터럴 경로의 `rm -rf` 는 safety-guard 가 "scratchpad 밖" 으로 거부한다(§2 표 4, `evidence/20261011-verifier-fix033-hookclaims.txt`). 증상 4 가 고치려던 것이 "다음에 같은 시행착오를 반복하지 않을 방법" 인데, 절차가 자기 안에서 어긋나면 그 목적을 다 채우지 못한다. 한 항목의 문구 수정으로 닫힌다.

## 1. 본 것

- `docs/wiki/fixes/FIX-033.md` — 증상 1~4, 원인, 수정안 1~4(문서만), 기획서 정합성, `계획 점검: 통과`(29행), `검증:` 자리표(30행), `승인: 사용자 (2026-10-11 …)`(31행), 결과절(35~36행: 5파일 +25/-3, (d) R-14-7 추가, 증거 2개).
- diff: `git diff 22a6822 -- .claude/agents/backend-agent.md .claude/agents/eval-agent.md .claude/agents/frontend-agent.md .claude/skills/devlog/SKILL.md docs/wiki/verification.md` 전체(`evidence/20261011-verifier-fix033-scope.txt` 38~122행).
- 구현자 증거: `evidence/20261011-2157-fix033-grep.txt`(SKILL.md 37·55·61행을 `cut -c1-260` + "(이하 생략)" 으로 줄인 발췌본 — 머리말에 스스로 표시), `evidence/20261011-2157-fix033-test-guards.txt`(전체, 실패 0).
- 사고 원문: `docs/wiki/packages/P8-frontend/review-u1-read-persons.md` 37행·56행·59~70행(§5)·97행(R-U1-1)·102행(R-U1-3)·122~131행(재검토 1), `docs/wiki/fixes/review-FIX-031.md` 13행·62행(R-31-3), `docs/wiki/fixes/review-FIX-014.md` 35행·67행·81행·102행(R-14-7).
- 대조 규칙: `CLAUDE.md` 31행("메인 세션은 조율·승인·커밋만 한다")·111행(L-004)·120행(FIX-014 Bash 쓰기 규칙), `.claude/agents/verifier.md` 3·17·24·32·39행, `.claude/scripts/bash_write_check.py` 673~738행(임시 경로 판정), `.claude/hooks/safety-guard.sh`·`bash-write-guard.sh`(직접 입력 시험).
- 작업 트리의 다른 변경(`HANDOFF.md`·`journal.md`·`FIX-032.md`·`FIX-033.md`)은 위임 범위 밖이라 diff 를 읽지 않았다(`FIX-033.md` 는 본문만 읽음).

## 2. 내가 직접 실행한 것 (수치는 보고서에서 옮기지 않고 전부 다시 쟀다)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `git diff --name-only 22a6822` · `git status --porcelain` · `… \| grep -v '\.md$'` | 변경 9파일 전부 `.md`, 비-`.md` 0(rc=1). 대상 5파일 `+25/-3`. 삭제 3줄은 SKILL.md 5·6단계와 `/devlog done` 2단계의 **같은 줄을 늘려 다시 쓴 것**(원문이 `+` 줄 앞부분에 그대로 포함) — 기존 규칙 삭제 없음 | `evidence/20261011-verifier-fix033-scope.txt` 3~36행·124~127행 |
| 2 | 수정안 4 의 grep 을 **글자 그대로**: `grep -n "값으로 단언\|구현하기 전에 멈추고\|출력 전체" .claude/agents/*.md .claude/skills/devlog/SKILL.md docs/wiki/verification.md` | backend 72·73·74 / eval 62·63·64 / frontend 55·56·57 / SKILL 37·55·61 / verifier 25(기존) / **architect 0 · verification.md 0** | `evidence/20261011-verifier-fix033-grep.txt` §A·§A-1 |
| 3 | 구현자 변형(4문구·"멈추" 축약): `grep -n "값으로 단언\|구현하기 전에 멈추\|출력 전체\|리터럴 절대 경로" <5파일>` | backend 4 · eval 4 · frontend 4 · SKILL 5(35·37·43 기존 + 55·61 신규) · verification.md 2(61 기존 + **84 신규**). 새 절(77~85행)만 보면 4문구 중 "리터럴 절대 경로" 1건만 걸림 | 같은 파일 §B·§B-1·§C |
| 4 | 훅에 PreToolUse JSON 직접 입력(실행 없음): safety-guard 4건 · bash-write-guard 8건 | `rm -rf "$R"`·`rm -rf $T` **deny**(scratchpad 밖) · `rm -rf <스크래치패드 리터럴>` allow · **`rm -rf <mktemp -d 리터럴 /var/folders/…>` deny(scratchpad 밖)** · `> $SP/…`·`> "$(mktemp -d)/…"` deny(판정 불가) · `> /var/folders/…/T/tmp.FU6V9WSid0/out.txt`·`cp -R app <같은 경로>` allow(`$TMPDIR` 접두) · 다른 기기의 `/var/folders/zz/…` deny · 스크래치패드 리터럴 `>`·`PYTHONPATH=… pytest -p …` allow · 임시 저장소 `git add app/x.py` allow | `evidence/20261011-verifier-fix033-hookclaims.txt` |
| 5 | `bash .claude/scripts/test-guards.sh` | 종료 0 · `== 결과: 실패 0 ==` · 에이전트 frontmatter 5건 ok(architect·backend·eval·frontend·verifier) | `evidence/20261011-verifier-fix033-test-guards.txt`(354행 전체) |
| 6 | `grep -n -o "통과하면 통과하면" .claude/skills/devlog/SKILL.md` | 56행 1건 — 이번 diff 가 넣은 중복(원문 "쓰게 하고, 통과하면 verifier 가" → "쓰게 한다. **…** 통과하면 통과하면 verifier 가") | `…-grep.txt` §D, `…-scope.txt` 92행 |
| 7 | `grep -n "| tee" .claude/skills/devlog/SKILL.md docs/wiki/verification.md .claude/agents/verifier.md` | SKILL.md 60행(`/devlog done` 1단계) `verify-impl.sh <id> \| tee …/evidence/…` 잔존 — bash-write-guard 가 거부하는 형태(FIX-014 C5·R-14-4) | `…-grep.txt` §F |
| 8 | `mktemp -d` · `python3 -c 'import tempfile;print(tempfile.gettempdir())'` | `/var/folders/bs/dry3bl8532q22pr3sd98m_p40000gn/T/tmp.FU6V9WSid0` · `/var/folders/bs/…/T` — 스크래치패드(`/private/tmp/claude-501/…/scratchpad`) 와 다른 트리 | `…-hookclaims.txt` 3행 |
| 9 | 참조 경로 `ls -la` | `review-u1-read-persons.md`(29209B)·`evidence/20261011-verifier-u1-mutation.txt`(2336B, 1행 "pytest -p 플러그인(스크래치패드)으로 런타임 치환") 존재 | `…-scope.txt` 129~134행 |

부수 증거(살아 있는 훅에 verifier 본인이 막힘): 이 검증의 첫 Bash 호출 두 건이 `… > "$SP/fix033-grep.txt"` 형태였고 bash-write-guard 가 "쓰기 대상 경로 '$SP/fix033-grep.txt' 를 판정할 수 없다(변수·명령 치환·계산된 경로)" 로 거부했다. R-14-7 의 함정이 그대로이며 새 규칙 (d) 가 필요한 이유의 실증이다. 또 시험 명령 문자열에 `git commit` 글자가 들어가자 commit-guard 가 그 호출을 거부해(2회) "임시 저장소의 커밋도 막힌다" 는 주장은 test-guards 62·168행으로 대신 확인했다(`…-hookclaims.txt` 참고 1).

## 3. 확인 항목별 판정 (위임 프롬프트 1~7)

### 3.1 범위 — `.md` 만, 수정안 1~4 + R-14-7 1건과 1:1, 삭제는 재작성
- 비-`.md` 변경 0(§2 1). 코드·훅·시험 스크립트 무변경.
- 수정안 1 ↔ 에이전트 정의 3개에 각 4줄: (a) 값으로 단언 · (b) 구현 전 멈춤 · (c) 출력 전체 · (d) 리터럴 절대 경로. 수정안은 "세 줄" 이라 했고 (d) 는 결과절(35행)이 R-14-7 로 설명한다 — 위임 프롬프트의 "수정안 1~4 + R-14-7 문구 1건" 과 일치. 단 FIX-033.md 수정안 1·Refs 줄은 갱신되지 않았다(R-33-4).
- 수정안 2 ↔ SKILL.md 55행(위임 프롬프트에 (a)~(d) 한 문장)·56행(verifier 변이 시험 ≥1, 저장소 무수정, `verification.md` 참조)·61행(`/devlog done` 2단계 3절에 같은 문구). 일치.
- 수정안 3 ↔ verification.md 77~85행 새 절: 고유 새 디렉터리(`mktemp -d`)·`rm -rf` 변수 경로 금지·스테이징만·런타임 치환 예시 경로·FIX-014 이후 Bash 쓰기 범위·보고 표. 항목은 전부 있다. 내용의 정확성은 §3.4.
- 삭제 3줄은 전부 같은 줄의 확장(§2 1). 정당.

### 3.2 내용 정합 — 기존 규칙과 충돌·중복 없음, L-002·L-004 와 맞음
- (a)·(c)·(d) 는 바로 위 줄들(FIX-014 "Write/Edit 로만", "증거는 파일로", "커밋 금지")을 **구체화**한다. (c) "Write 로 남긴다" 는 FIX-014 줄의 "Bash 로 파일을 쓰지 않는다" 와 같은 방향. (d) 는 FIX-014 줄의 "임시 파일은 `/tmp`·스크래치패드에만" 에 "리터럴로" 를 더한 것 — R-14-7 이 지적한 빠진 조건 그대로(review-FIX-014.md 81행 "**변수가 아니라 리터럴 절대 경로** 라는 조건이 빠져 있어"). 중복이 아니라 보완.
- (a) 의 "불가피하게 고쳤다면 원복 후 `git diff`" 는 Edit 툴로 제품 코드를 고치는 경우를 말하므로 stage-gate(활성 작업)·FIX-014 와 충돌 없음.
- (b) "구현하기 전에 멈추고 보고 → 메인 세션이 사용자에게 묻고 01-plan/03-log 에 기록" 은 CLAUDE.md 31행 "메인 세션은 조율·승인·커밋만" 과 111행 L-004(자동 시작 금지·AskUserQuestion) 의 역할 분담과 일치한다. R-U1-3 의 실제 처리(사용자 결정 "10건 유지 + 테스트" → 03-log 기록, review-u1 116·173행)가 바로 이 흐름이다. 참고: 승인된 01-plan 을 사후에 고치면 02-plan-verify 와 어긋날 수 있으니 실무상 03-log 쪽 기록이 안전하다(소견 아님).
- SKILL.md 56·61행의 verifier 문구 "저장소 밖 사본 또는 런타임 치환, 저장소 무수정" 은 verifier.md 17행 "코드·계획·카드를 수정하지 않는다"·39행 "고치지 않는다" 와 일치하고, L-002(구현자와 다른 모델이 검증) 를 바꾸지 않는다. 변이 시험 의무는 verifier.md 에는 들어가지 않았고 위임 프롬프트로 전달된다(R-33-8, 선택).
- FIX-032 의 "dev2" 줄(각 정의의 마지막 "git log 를 본다" 줄)은 건드리지 않았다(`…-scope.txt` 52·66·80행 컨텍스트).

### 3.3 실제 사고 대조 — 4건 모두 대응 줄 있음
| 사고 | 원문 | 새 규칙이 있었다면 막았을 줄 |
|---|---|---|
| R-U1-1 `func.max→func.min` 변이에 7건 통과 | review-u1 70·97행 ("`is not None` 만 단언", "아무 테스트도 보호하지 않는다") | backend-agent.md 72행 (a) "그 코드를 바꾸면(예: `max→min` …) 실패할 테스트가 있어야 한다 … '어떤 변이를 어떤 테스트가 잡는가' 표" — 구현자가 표를 만들려면 변이 4 를 직접 돌려야 했고 7 passed 가 보고 단계에서 드러난다. 2차 방어: SKILL.md 56행 verifier 변이 ≥1 |
| R-U1-3 `UPCOMING_SCHEDULES_LIMIT = 10` 계획 밖·테스트 없음·주석 근거 오류 | review-u1 56·102행 | backend-agent.md 73행 (b) — 예시가 그대로 "목록 상한 `LIMIT = 10`". frontend 56행도 "목록 표시 개수 상한" |
| R-31-3 구현 증거가 요약본 | review-FIX-031.md 13·62행 | backend-agent.md 74행 (c) "명령 출력 전체를 Write 로 … 요약·발췌는 그 아래 따로". SKILL.md 55행 (c) 가 위임 프롬프트에 강제 |
| R-14-7 변수 경로(`$SP/…`·`"$T/…"`) 거부로 두 번 막힘 | review-FIX-014.md 35·102행 | backend/eval/frontend 75/65/58행 (d) + verification.md 84행 + SKILL.md 55행 (d). 이 검증 중 verifier 도 같은 함정에 걸렸다(§2 부수 증거) — 규칙이 있어도 사람이 읽어야 막히지만, 적어도 "왜 막혔나" 를 즉시 알 수 있다 |
| (증상 4) `rm -rf "$R"`·임시 저장소 커밋 | FIX-033.md 10행 | verification.md 81~82행(1·2번째 항목). 다만 1번째 항목 내용이 부정확 — R-33-1 |

대응 없는 사고: 없음. U2 "`Event.person_id` 추가 방어선"(증상 2 후반)은 (b) 의 "추가 방어 조건" 이 덮는다.

### 3.4 verification.md 새 절 — 참조는 맞고 훅과도 맞지만, 1번째 항목이 절 안에서 모순
- 참조 경로 2개 존재(§2 9). `review-u1-read-persons.md` §5(59~70행)는 실제로 "스크래치패드의 pytest 플러그인(`-p <모듈>`, `PYTHONPATH` 로 주입)" 방식을 기록하고, 변이 증거 1행도 같다. "대조군 7 passed → 변이 4건" 수치는 §5 61행·66~68행과 일치.
- `rm -rf "$VAR"` 거부: 실측 deny(§2 4). `$(mktemp -d)/…` 거부: 실측 deny. `PYTHONPATH=<스크래치패드 리터럴> pytest -p …`: 실측 allow. 임시 저장소 `git add <경로>`: 실측 allow. "commit-guard 가 임시 저장소의 커밋까지" : test-guards 62·168행.
- **모순(R-33-1)**: 1번째 항목은 `mktemp -d` 출력 경로에서 작업하라 하고, 정리 불필요의 이유를 "스크래치패드가 세션과 함께 사라진다" 로 든다. 그러나 `mktemp -d` 는 `$TMPDIR`(이 Mac: `/var/folders/bs/…/T/`) 아래를 만들며 스크래치패드(`/private/tmp/claude-501/…/scratchpad`)가 아니다(§2 8). 그 경로로의 Bash 쓰기는 훅이 허용하지만(§2 4, `$TMPDIR` 접두) 4번째 항목 "스크래치패드 밖으로 Bash 쓰기를 하지 않는다" 와 글자 그대로 어긋나고, safety-guard 는 그 경로의 `rm -rf` 를 "scratchpad 밖" 으로 거부한다. Windows(Git Bash) 에서도 `mktemp -d` 는 `/tmp` → `%TEMP%` 라 마찬가지로 스크래치패드가 아니다. 즉 이 절을 그대로 따르는 다음 에이전트는 "어느 디렉터리가 맞나" 를 또 시행착오로 알게 된다 — 증상 4 미해결.

### 3.5 판정 grep 과 test-guards (수정안 4)
- 글자 그대로의 수정안 4 명령은 `verification.md` 에서 **0건**, `architect.md` 에서 0건(§2 2). 수정안 4 가 "각 파일에서 걸리고" 라 했으므로 문구 기준으로는 미충족. 구현자는 패턴을 바꿔(4번째 문구 추가·"멈추고"→"멈추") 5파일 적중을 보였고 그 사실을 증거 머리말에 적었다. 새 절의 내용(§3.4)은 있으므로 **내용 기준 통과, 판정 기준 기록 불일치** → R-33-3(권고). 위임 프롬프트의 질문 "verification.md 는 '리터럴 절대 경로' 만 걸려도 되는가" 에 대한 답: 그 문구는 61행(기존)에도 있어 새 절의 존재 증명이 되지 못한다 — 새 절은 제목 `## 변이 시험 방법` 또는 "`mktemp -d`"·"스테이징" 같은 고유 문구로 판정해야 한다. FIX-033.md 결과절에 실제 판정 명령을 적어 두면 닫힌다.
- test-guards: 실패 0, frontmatter 5건 ok(§2 5). 구현자 결과와 같다.

### 3.6 구현자 증거의 전체본 대체
구현자 `…-2157-fix033-grep.txt` 는 `cut -c1-260` 과 "(이하 생략 — 기존 줄)" 로 SKILL.md 37·55·61행을 줄였다. 이 FIX 가 넣는 (c) "증거 파일에는 명령 출력 전체 … 요약·발췌는 그 아래 따로" 에 비추면 발췌가 전체를 **대신**했으므로 규칙과 어긋난다(R-33-5). 내 `…-verifier-fix033-grep.txt` 가 잘라내기 없는 전체본이다.

### 3.7 Mac·Windows
문서만 바꾼다 — 해당 없음. 단 R-33-1 의 `mktemp -d` 경로 문제는 Windows 에서도 같은 방향(스크래치패드 아님)이라 수정 문구는 OS 를 가리지 않게 쓰는 것이 좋다.

## 4. 소견

### [필수]
- **R-33-1 · `verification.md` 81행(새 절 1번째 항목)의 `mktemp -d` 지시가 같은 절 84행과 모순이고 괄호 근거가 틀렸다.** 근거: `mktemp -d` 실측 `/var/folders/bs/…/T/tmp.FU6V9WSid0`(스크래치패드 아님, §2 8); 그 경로 `rm -rf` → safety-guard deny "scratchpad 밖"(§2 4); 84행 "스크래치패드 밖으로 Bash 쓰기를 하지 않는다"; 81행 "(스크래치패드가 세션과 함께 사라진다)" 는 `$TMPDIR` 디렉터리에 해당 없음. 해결 방향(구현 에이전트 몫, 내가 고치지 않음): ① `mktemp -d <스크래치패드 리터럴 절대 경로>/mut.XXXXXX` 처럼 **스크래치패드 안에** 만들게 하고 "출력된 경로를 리터럴로 확인" 은 유지(치환 경로 금지는 실측대로 맞음), 또는 ② "스크래치패드 아래 새 하위 디렉터리를 Write/`mkdir` 로 만든다" 로 바꾸고 `mktemp -d` 언급을 뺀다. 어느 쪽이든 84행과 같은 영역을 가리키게 하고, 괄호 근거를 "스크래치패드는 세션과 함께 사라지며 그 안의 `rm -rf` 리터럴 경로는 safety-guard 가 허용한다" 로 맞춘다. 완료 판정: 새 절에서 작업 디렉터리를 가리키는 모든 문구가 스크래치패드(또는 그 하위)로 통일 + `rm -rf <그 리터럴 경로>` 를 safety-guard 에 직접 입력해 allow(`…-hookclaims.txt` 3번째 케이스가 기대 출력).

### [권고]
- **R-33-2 · `SKILL.md` 56행 "통과하면 통과하면" 중복** — 이번 diff 가 넣었다(`…-scope.txt` 90행 원문 "쓰게 하고, 통과하면" ↔ 92행 "쓰게 한다. … 통과하면 통과하면"). 의미는 바뀌지 않지만 R-33-1 수정 시 함께 고치면 된다.
- **R-33-3 · 수정안 4 의 판정 grep 이 `verification.md`·`architect.md` 에서 0건** — 글자 그대로는 "각 파일에서 걸리고" 를 충족하지 못한다(§3.5). FIX-033.md 결과절에 실제 쓴 판정(4문구 변형)을 적거나, `verification.md` 는 `grep -n "^## 변이 시험 방법" docs/wiki/verification.md` 로 따로 판정한다고 적는다. `architect.md` 는 Bash·구현이 없어 대상 밖이라는 한 줄도.
- **R-33-4 · FIX-033.md 수정안 1 "세 줄" ↔ 실제 4줄, Refs 에 R-14-7 없음** — 결과절(35행)만 (d)·R-14-7 을 설명한다. 3행 Refs 에 `R-14-7`, 수정안 1 에 (d) 한 줄을 더하면 추적성이 맞는다.
- **R-33-5 · 구현자 grep 증거가 발췌본** — `…-2157-fix033-grep.txt` 의 `cut -c1-260`·"(이하 생략)" 은 이 FIX 의 (c) 와 어긋난다(§3.6). 내 전체본이 대신하므로 막지 않는다. 다음부터는 전체를 남기고 발췌는 그 아래에.
- **R-33-6 · `SKILL.md` 60행 `verify-impl.sh <id> | tee …/evidence/…` 잔존(R-14-4 잔여)** — bash-write-guard 가 거부하는 형태인데 이번 diff 가 바로 다음 줄(61행)을 고치면서 그대로 두었다. 새 절 84행 "스크래치패드 밖으로 Bash 쓰기 금지" 와 같은 문서 체계 안에서 어긋난다. 범위 밖이라 권고 — 43행과 같은 문구("출력을 Write 툴로 … 긴 출력은 스크래치패드 리터럴 절대 경로로 `>` 한 뒤 Read → Write")로 바꾸면 된다.
- **R-33-7 · R-14-7 이 제안한 `CLAUDE.md` 120행 미반영** — 120행은 "대상 경로를 판정할 수 없으면(변수·명령 치환) 차단한다" 까지만 있고 "임시 경로는 리터럴 절대 경로로 쓴다" 지시는 없다(§1 대조). 에이전트 정의 3개에 들어갔으므로 실효는 있다. 선택 — CLAUDE.md 는 메인 세션도 읽으므로 한 구절 추가가 메인 세션의 U0 재발(증상 4)을 막는 데 직접 닿는다.
- **R-33-8 · `verifier.md` 에 변이 시험 의무·`verification.md` 절 참조 없음** — 현재는 SKILL.md 56·61행이 위임 프롬프트로 전달하도록 한다. verifier.md 완료 검토 3번("항상 통과하는 테스트는 증거가 아니다")이 원칙은 담고 있어 선택 사항. 넣는다면 "커밋 전 코드 리뷰" 절에 "단위마다 핵심 계약 변이 1개 이상 — 방법은 `verification.md` '변이 시험 방법'" 한 줄.

## 5. 결론

`검증:` 줄은 비워 둔다(보류). R-33-1 한 항목(그리고 같은 손길로 R-33-2)을 구현 에이전트가 고친 뒤, 재검증은 다음 셋으로 끝난다: ① `sed -n '77,86p' docs/wiki/verification.md` 로 작업 디렉터리 문구가 스크래치패드로 통일됐는지 읽기, ② `rm -rf <새 절이 가리키는 리터럴 경로>` 를 `safety-guard.sh` 에 직접 입력해 allow, ③ `bash .claude/scripts/test-guards.sh` 실패 0 재확인. 통과하면 `검증: 통과 — verifier (fable) 2026-10-11, review-FIX-033.md (문서만 — Windows 해당 없음)` 을 쓴다. R-33-3~8 은 메인 세션·사용자가 이번 커밋에 포함할지 정한다(이번 FIX 범위 밖인 6·7·8 은 별도 FIX 로 미뤄도 된다).

---

## 재검증 (2026-10-11)

검토자: verifier (fable) · 1차 리뷰와 다른 새 컨텍스트 · 기준 HEAD `22a6822` + 작업 트리 미커밋 diff(대상 6파일 +32/-7, FIX-033.md 포함) · Refs: FIX-033 FIX-014 L-002 L-004 R-33-1 R-33-2 R-33-3 R-33-4 R-33-6 R-14-7

**재검증 결과: 통과.** 1차 [필수] R-33-1 과 같은 손길의 [권고] R-33-2·3·4·6 이 전부 해소됐고, 재작업이 1차에서 통과한 것(에이전트 정의 3개·사고 4건 대응·L-002/L-004 정합)을 건드리지 않았다. 코드·훅·계획·카드는 고치지 않았다. `FIX-033.md` 의 `검증:` 줄만 썼다(아래 §R.5). 재작업 중 메인 세션이 `FIX-033.md`(R-33-3·4)를 직접 고친 것은 문서(FIX 카드 자체)이므로 "메인 세션은 제품 코드를 직접 고치지 않는다" 와 충돌하지 않는다.

### R.1 본 것
- `review-FIX-033.md` 1차 본문 전체(R-33-1~8, §5 재검증 방법 ①②③).
- `git diff 22a6822 -- docs/wiki/verification.md .claude/skills/devlog/SKILL.md docs/wiki/fixes/FIX-033.md .claude/agents/backend-agent.md .claude/agents/eval-agent.md .claude/agents/frontend-agent.md` 전체.
- 재작업 증거 `evidence/20261011-2200-fix033-rework.txt`(판정 1~4 전체)·`20261011-2200-fix033-rework-test-guards.txt`(353행, 실패 0).
- 1차 증거 `…-verifier-fix033-scope.txt`(39~80행, 에이전트 정의 diff 원본)·`…-verifier-fix033-hookclaims.txt`(3번째 케이스 = R-33-1 기대 출력).
- `HANDOFF.md`·`journal.md`·`FIX-032.md` 는 위임 범위 밖 — 읽지 않았다.

### R.2 내가 직접 실행한 것 (전부 다시 쟀다 — 수치를 보고서에서 옮기지 않음)

| # | 확인 | 명령 | 결과 | 증거 |
|---|---|---|---|---|
| 1 | R-33-1 문구 | `sed -n '77,86p' docs/wiki/verification.md` | 81행: 작업 디렉터리 = "스크래치패드 … 아래 고유한 새 하위 디렉터리", `mktemp -d` 는 "`mktemp -d <스크래치패드 리터럴>/mut.XXXXXX`" 로 스크래치패드 안 지정, "`$TMPDIR`·`/tmp` 의 `mktemp -d` 기본값은 쓰지 않는다", 괄호 근거 "(스크래치패드가 세션과 함께 사라진다)" 가 이제 그 경로에 맞음. 83·84행도 스크래치패드. 작업 디렉터리를 가리키는 문구 전부 스크래치패드(하위)로 통일 — 84행과 모순 없음 | `evidence/20261011-verifier-fix033-recheck-scope.txt` §B |
| 2 | R-33-1 훅 실측 | 81행 두 예시를 **실제로 만들고**(`mkdir -p <스크래치패드>/mut-fix033-recheck-20261011`, `mktemp -d <스크래치패드 리터럴>/mut.XXXXXX` → `…/scratchpad/mut.GspWFG`, 접두 일치) 그 리터럴로 `rm -rf` 를 `safety-guard.sh` 에 stdin JSON 으로 입력 | **A·B allow**(출력 없음, rc=0). 대조: `mktemp -d` 기본값 리터럴 `/var/folders/bs/…/T/tmp.Y1jGEB38s2` **deny**, `/tmp/tmp.…` deny, `rm -rf "$VAR"` deny, `rm -rf "$(mktemp -d)"` deny — 81행이 "쓰지 않는다"·"훅이 거부한다" 고 한 주장과 전부 일치. bash-write-guard: `> <스크래치패드 하위 리터럴>/out.txt` allow · `mktemp -d <스크래치패드 리터럴>/mut.XXXXXX` allow · `PYTHONPATH=<리터럴> pytest -p …` allow · `> "$(mktemp -d)/…"` deny · `verify-impl.sh … \| tee docs/…` deny(R-33-6 옛 60행 형태). 기대 ↔ 결과 11/11 | `evidence/20261011-verifier-fix033-recheck-hookclaims.txt` |
| 3 | R-33-2 | `grep -c "통과하면 통과하면" .claude/skills/devlog/SKILL.md` | **0**(rc=1). 56행 "쓰게 한다. **단위마다 …**. 통과하면 verifier 가" — 1회 | `…-recheck-scope.txt` §C |
| 4 | R-33-6 | `grep -n "\| tee" .claude/skills/devlog/SKILL.md` / `grep -n "tee"` | 명령 형태 **0건**. `tee` 언급 2건(35·60행)은 모두 "`tee`·`>` 는 … 거부한다" 설명. 60행 새 문구 = "스크래치패드 리터럴 절대 경로로 `>` 받은 뒤 Read → Write 로 … 전체 저장" — 34~35행(start 5단계)·43행(루프 1단계)과 같은 취지(Write 저장·tee/> 거부·긴 출력은 스크래치패드 경유) | 같은 파일 §C |
| 5 | R-33-3 판정 명령 글자 그대로 | `grep -c "값으로 단언\|구현하기 전에 멈추\|출력 전체\|리터럴 절대 경로" .claude/agents/backend-agent.md .claude/agents/eval-agent.md .claude/agents/frontend-agent.md .claude/skills/devlog/SKILL.md` / `grep -n "^## 변이 시험 방법" docs/wiki/verification.md` | eval **4** · backend **4** · frontend **4** · SKILL **6**(35·37·43·55·60·61행 — 60행 재작성으로 1차 5→6) — 네 파일 모두 ≥1 / `77:## 변이 시험 방법 (메인 세션·verifier, FIX-033)` **1건**. FIX-033.md 20행이 원안이 왜 판정 불가였는지(architect.md·verification.md 0건, "리터럴 절대 경로" 는 61행 기존 문구) 적어 둠 | 같은 파일 §D |
| 6 | R-33-4 | `sed -n '3p;18p' docs/wiki/fixes/FIX-033.md` · `grep -n "R-14-7"` | 3행 Refs 끝에 `R-14-7` 추가. 18행 수정안 1 "세 줄"→"**네 줄**((a)~(c) + FIX-014 검증 R-14-7 의 (d) … — 사용자 2026-10-11 FIX-033 위임 승인 때 포함)". R-14-7 3곳(3·18·35행) | 같은 파일 §D |
| 7 | 1차 통과분 보존 | `git diff 22a6822 -- <에이전트 3개>` ↔ 1차 `…-verifier-fix033-scope.txt` 39~80행 을 `diff`·`shasum` | **바이트 동일**(diff rc=0, sha256 `e5145194…eab2812` 둘 다). blob index 3개(`0987a61..efb19e1`·`1813d4c..fd2161a`·`dbb2f6f..8e74b79`) 1차와 같음. mtime 21:57(에이전트 3개) < 22:17(1차 리뷰) < 22:22(재작업 SKILL·verification·FIX-033). 즉 사고 4건 대응 줄(1차 §3.3)·L-002/L-004 정합(§3.2)은 그대로 | 같은 파일 §E |
| 8 | test-guards | `bash .claude/scripts/test-guards.sh` | 종료 0 · `== 결과: 실패 0 ==` · ok 333 · XX 0 · 에이전트 frontmatter 5건 ok | `evidence/20261011-verifier-fix033-recheck-test-guards.txt`(351행 전체) |
| 9 | 범위 | `git diff --name-only 22a6822` · `git status --porcelain` | 추적 변경 9파일 전부 `.md`. 비-`.md` 는 untracked `evidence/*.txt` 8개(증거)만. 대상 6파일 `+32/-7`(에이전트 +4×3 · SKILL +4/-4 · verification +10 · FIX-033 +6/-3). 코드·훅·스크립트 무변경 | `…-recheck-scope.txt` §A |
| 10 | R-33-5·7·8 상태 | `git diff --quiet 22a6822 -- CLAUDE.md .claude/agents/verifier.md` · grep | CLAUDE.md 무변경("리터럴 절대 경로" 0건) · verifier.md 무변경("변이"/"verification.md" 0건) · 1차 구현 grep 증거는 발췌본 그대로(수정 대상 아님), 재작업 증거는 전체본 | 같은 파일 §F |

부수 관찰: 이번 재검증에서 verifier 는 스크래치패드 **리터럴** 하위 디렉터리(`…/scratchpad/fix033-recheck/`)로만 `>` 했고 훅에 한 번도 막히지 않았다 — 1차 §2 "부수 증거"(변수 경로로 두 번 거부)와 대조되는, 새 절 84행·규칙 (d) 가 지시하는 그대로의 작업 경로다.

### R.3 소견 상태

| 소견 | 1차 등급 | 재검증 | 근거 |
|---|---|---|---|
| R-33-1 `mktemp -d` 가 스크래치패드 밖 / 84행과 모순 | 필수 | **해소** | R.2 #1·#2 — 문구 통일 + 두 예시 경로의 `rm -rf` 리터럴 allow, `$TMPDIR` 대조 deny |
| R-33-2 "통과하면 통과하면" | 권고 | **해소** | R.2 #3 — 0건 |
| R-33-3 판정 grep 이 글자 그대로 안 돌아감 | 권고 | **해소** | R.2 #5 — 정정된 명령이 글자 그대로 통과(4·4·4·6 + 1건) |
| R-33-4 "세 줄"·Refs R-14-7 | 권고 | **해소** | R.2 #6 |
| R-33-5 구현자 1차 grep 증거가 발췌본 | 권고 | **열림(후속 관행)** | 1차 파일은 그대로(수정 대상 아님). 재작업 증거는 전체본으로 남겨 (c) 를 지킴. 1차 verifier 전체본이 대신 — 막지 않음 |
| R-33-6 SKILL.md 60행 `\| tee` | 권고 | **해소** | R.2 #4 — 명령 형태 0건, 새 문구가 34·43행과 같은 취지, 옛 형태는 훅이 실제 deny(hookclaims K) |
| R-33-7 CLAUDE.md 120행 미반영 | 선택 | **열림(선택)** | R.2 #10 — CLAUDE.md 무변경. 에이전트 정의 3개 (d) 로 실효 있음 |
| R-33-8 verifier.md 에 변이 의무 없음 | 선택 | **열림(선택)** | R.2 #10 — verifier.md 무변경. SKILL.md 56·61행이 위임 프롬프트로 전달 |
| **R-33-9 (신규, 권고)** `FIX-033.md` 36행 결과절 "합계 5파일 +25/-3" 은 1차 시점 수치 — 재작업(SKILL.md 60행 재작성 +1/-1) 뒤 대상 5파일은 `+26/-4` 이고 결과절에 재작업(R-33-1·2·6 반영, 증거 `20261011-2200-fix033-rework*.txt`) 언급이 없다 | — | 열림(권고) | R.2 #9 `git diff --stat`. 메인 세션이 `/commit` 때 해시를 적으면서 한 줄 보태면 닫힌다. 판정에 영향 없음 |

### R.4 Mac·Windows
문서만 — 해당 없음. 새 81행 문구는 "세션 안내에 적힌 리터럴 절대 경로" 기준이라 OS 를 가리지 않는다(1차 §3.7 권고 반영).

### R.5 결론
1차 §5 가 정한 재검증 ①②③ 을 모두 직접 실행해 통과했고(R.2 #1·#2·#8), 보강 확인(R-33-2·3·4·6 해소, 1차 통과분 무변경, 범위 `.md` 만)도 통과했다. `FIX-033.md` 30행을 `검증: 통과 — verifier (fable) 2026-10-11, review-FIX-033.md (재검증; 문서만 — Windows 해당 없음)` 으로 썼다. 열린 R-33-5·7·8(선택/후속)·R-33-9(권고)는 메인 세션·사용자가 이번 커밋에 포함할지 정한다.
