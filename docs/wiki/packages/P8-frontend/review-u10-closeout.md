# P8-frontend U10 마감 — 커밋 전 리뷰 (정렬 수정 1회 · FIX-035 실서버 확인 기록 · CR-003 문서 · 커밋 포함 범위)

검토자: verifier (fable)
요청: 메인 세션 2026-10-16 — 미커밋 변경 전부(`git status --short` 7 수정 + untracked 21)의 커밋 전 리뷰. 코드·테스트·계획 무수정(변이는 저장소 안에서 Edit → 실행 → Edit 원복, 아래 §3 원복 증거).
HEAD: `735f391` (dev2). 기준 문서: `01-plan.md` 161~164행(판정표 29~32행)·178~203행(화면 점검 체크리스트)·305~313행(결정 L) · `02-plan-verify.md` 126행(R-10) · `.claude/skills/devlog/SKILL.md` 66~71행(`/devlog change`)·92행(태그 규칙) · `docs/proposal.md` 60행(2장 표 "관계 태그 필터링" 제외) · `docs/wiki/changes/CR-003.md`.

**판정: 통과 (2026-10-16 19:49 재확인) — 1차 판정은 보류([필수] 2건, 둘 다 위키 문서 사실 오류·누락)였고, 메인 세션이 문서로 해소한 것을 verifier 가 재확인했다.** 코드 변경(`PersonCardScreen.tsx`·`card.test.tsx`)은 재실행·변이·원복까지 통과. [권고] 8건은 열린 채 커밋 가능(R-U10C-6·7 조건은 §3 참조).

재확인 증거 `evidence/20261016-1949-verifier-u10-closeout-recheck.txt`:
- R-U10C-1 해소: `03-log.md` 205~214행 — 항목 `## 2026-10-16 · fix(P8-frontend): 인물 화면 정렬을 고친다 — U10 32행 "수정 필요" 1회 · pending`, 207행 **"수정 반영 횟수: 1 (에이전트 작업 2회 — … CR-003 §3 ⑥(a) 사용자 결정으로 같은 1회로 본다 …)"**, 1차 `-1918-…`·2차 `-1933/1934-…` 증거 경로, 214행 `Refs: P8-frontend U10 CR-003 원칙5 원칙7 결정L 결정N`.
- R-U10C-2 해소: `tests.md` 454·455행 실패 이력 칸 `없음 (집계 제외)`(455행은 M4 생존·R-U10C-3 메모 포함) → 세는 법 grep `"^| .*| 기록 없음"` = **182**, 실제 실패 5 · 검출 실패→보강 18 · 보류·재작업 4 · 동작 틈→보강 1 — 표(182/210)와 일치.
- R-U10C-9 해소: HANDOFF 재작성, `grep -c "182 유지"` = 0.
- 제품 코드 무변경: `git status --short web/` 2파일 그대로, `git diff PersonCardScreen.tsx | shasum` = `ddfa457a…`(§2 원복 값과 동일).

---

## 0. 결론 한 문단

정렬 수정 diff(2파일, `5 +++--`·`+23`)는 typecheck 0 · Vitest 137/137 · build 0 · E2E 4/4 로 재현됐고, 변이 4종 중 계약 변이 3종(M1·M2·M3)은 전부 검출, 공백 탐침 M4(목록을 감싼 안쪽 div 에 폭 상한)는 **생존** — 테스트가 `section` 한 요소의 classList 만 보기 때문이다(R-U10C-3). 원복 뒤 diff 해시가 사전 값과 같다. "두 번의 에이전트 작업을 수정 1회로 본다"는 판정은 기계적으로는 2회이지만, 01-plan 164행·리스크 7 이 정한 출구("넘으면 CR 여부를 사용자에게")가 실제로 실행돼 CR-003 ⑥(a) 로 사용자가 결정했으므로 절차상 유효하다 — 단 그 사실(에이전트 작업 2회)을 03-log 에 숨기지 말고 "수정 반영 횟수: 1" 과 함께 적어야 하는데 **03-log 에 U10 정렬 항목 자체가 없다**(R-U10C-1). FIX-035 실서버 기록의 id·수치는 DB 재조회와 전부 일치하고 SQL 은 SELECT 만이다. 다만 `tests.md` 의 "세는 법" grep 이 새 정렬 행 2개를 세어 집계 표(182/210)와 어긋난다(R-U10C-2). CR-003 영향 분석은 확인한 범위에서 맞고, §4 0단계가 SKILL.md "승인 즉시 frozen" 과 어긋나지만 그 창 안의 제품 코드 변경이 CR 이 명시한 2파일뿐임을 확인했으므로 사유 기록으로 족하다(R-U10C-6).

## 1. 재실행 수치 (verifier 직접 실행, `save_evidence.py` 통로)

| 항목 | 명령 | 결과 | 증거 |
|---|---|---|---|
| typecheck | `npm --prefix web run typecheck` | exit 0 | `evidence/20261016-1941-verifier-u10-closeout-typecheck.txt` |
| Vitest 전체 | `npm --prefix web run test -- --run` | **9 files · 137 passed (137)**, exit 0 | `evidence/20261016-1941-verifier-u10-closeout-vitest.txt` |
| build | `npm --prefix web run build` | exit 0 (`index-*.css 44.47 kB`·`index-*.js 361.04 kB`, 구현자 증거와 동일) | `evidence/20261016-1942-verifier-u10-closeout-build.txt` |
| E2E | `npm --prefix web run e2e` | **4 passed (4.3s)**, exit 0 — card 데스크톱/모바일·chat·briefing | `evidence/20261016-1942-verifier-u10-closeout-e2e.txt` |
| 개발 DB 재조회(읽기만) | `docker exec capstone2-postgres-1 psql … -c "select …"` 6건 | persons **10** · events **30** · pending_questions max id **15** · trace 374 `identity_rejected=true, followup=13` · 396 `true, 15` · er_resolve 407 confidence **0.8653779689735086** matched **10** · events 29/30 `raw_utterance` 기록과 동일 | 이 문서 §4 (출력 인용) |

구현자 증거 `evidence/20261016-1933/1934-u10-fix-card-align2-*.txt` 와 수치 동일(137·4·exit 0).

## 2. 변이 시험 (저장소 안 Edit → 실행 → Edit 원복; `git checkout` 은 미커밋 변경을 지우므로 쓰지 않음)

증거: `evidence/20261016-1942-verifier-u10-closeout-mutation.txt`(4회 `--append`, 머리줄 `# 메모:` 에 변이 내용).

| # | 변이 | 기대 | 결과 | 판정 |
|---|---|---|---|---|
| M1 | `section` 에 `className="mx-auto"` 추가 | 목록·상세 테스트 2건 실패 | `2 failed \| 29 passed (31)` | 검출 |
| M2 | 래퍼 `card-wrap` 에서 `mx-auto` 제거 | 상세 1건 실패 | `1 failed \| 30 passed (31)` | 검출 |
| M3 (verifier) | 래퍼 비율 `md:w-3/4` → `md:w-1/2` | 상세 1건 실패 | `1 failed \| 30 passed (31)` | 검출 |
| M4 (verifier, 공백 탐침) | 목록을 감싼 안쪽 `<div className="mt-4">` 에 `mx-auto max-w-3xl` | 목록 테스트가 잡아야 "본문 폭 전체" 규칙이 보호됨 | **`31 passed (31)` — 생존** | 공백 → R-U10C-3 |

원복 확인 `evidence/20261016-1943-verifier-u10-closeout-revert-check.txt`: `git diff --stat` = `card.test.tsx 23 +`·`PersonCardScreen.tsx 5 +++--`(구현자 `-1934-…-revert-check.txt` 와 동일), `git diff PersonCardScreen.tsx | shasum` = `ddfa457a70d3dd2b35fe9946bc3ddfd8cfe9a788`(변이 전 §0 에서 잰 값과 동일), 원복 뒤 `31 passed (31)`.

## 3. 소견

### [필수]

**R-U10C-1 — 03-log 에 U10 정렬 수정 항목이 없다 (Refs·"수정 반영 횟수" 기록 누락).**
- 근거: `grep -n "정렬\|align" docs/wiki/packages/P8-frontend/03-log.md` → U10 관련 0건(27·45행은 U1·U3 의 정렬 키). 03-log 마지막 항목(203행)은 FIX-035 "커밋 뒤" 줄뿐. 반면 `tests.md` 448~455행·`registry.md` 246행·HANDOFF 에는 정렬 수정이 있다.
- 왜 필수인가: 01-plan 164행 32행 "증거 파일에 **"수정 반영 횟수: n"** 줄을 명시하고 04-review 가 n ≤ 1 을 확인" · `02-plan-verify.md` 126행 R-10 · SKILL.md 92행 "`Refs:` 에 … 해소한 F-id/FIX/CR 을 모두 적는다" — 이 커밋의 코드 변경을 역추적할 03-log 항목과 Refs 가 없다. 또 "1회" 판정의 근거(에이전트 작업 2회를 CR-003 ⑥(a) 사용자 결정으로 같은 1회로 본다)는 CR-003 머리글·HANDOFF 에만 있고 패키지 기록에 없다.
- 요구(메인 세션, 문서만): 03-log 에 U10 항목 — ① 1차(`-1918-…` 증거, `max-w-4xl` 왼쪽 정렬, 사용자가 본 뒤 추가 지시) ② 2차(`-1933/1934-…`, section 클래스 제거 + `card-wrap mx-auto w-full md:w-3/4`) ③ **"수정 반영 횟수: 1 (에이전트 작업 2회 — 2차는 커밋 전 사용자 추가 지시, CR-003 ⑥(a) 로 같은 1회로 결정)"** 줄 ④ verifier 이 문서 ⑤ `Refs: P8-frontend CR-003 원칙5 원칙7`. 32행 최종 증거 파일(`*-u10-check-screens.txt`, 01-plan 101행)에도 같은 줄을 옮긴다.

**R-U10C-2 — `tests.md` 집계 표와 "세는 법" grep 이 어긋난다 (182 ↔ 184).**
- 근거: `tests.md` 467행 세는 법 `grep -c "^| .*| 기록 없음" tests.md` 를 실행하면 **184**(HEAD 기준 182). 새 "U10 화면 점검 수정 1회" 절의 행 2개(453·454행)가 `| 기록 없음 |` 로 끝나 세어진다(`git diff … | grep "^+|" | grep -c "| 기록 없음 |$"` → 2). 그런데 448행 절 제목은 "위 총계·집계에 넣지 않는다" 이고 462행 표는 `기록 없음 182`·합계 `210` 그대로. FIX-035 수동 6건은 `없음 (수동 점검)` 이라 세어지지 않는다(의도대로).
- 왜 필수인가: 이 집계는 R-35-7 로 한 번 고친 사실 수치이고 HANDOFF 가 "`기록 없음` grep 182 유지" 라고 단언한다 — 지금 커밋하면 문서가 스스로 틀린다.
- 요구(둘 중 하나): (a) 정렬 행 2개의 실패 이력 칸을 `없음 (집계 제외)` 류로 바꿔 grep 밖으로 내보내거나 (b) 정렬 2건을 집계에 넣어 `기록 없음 184`·합계 `212`·합계식("프론트 135 + 2 …")·HANDOFF 문장을 함께 고친다. 어느 쪽이든 세는 법 grep 과 표가 같은 수여야 한다.

### [권고]

**R-U10C-3 — 변이 M4 생존: "목록은 본문 폭 전체" 규칙이 `section` 한 요소에만 고정돼 있다.** `card.test.tsx` 117~125행은 `[data-screen="persons"]` 의 classList 만 보고, 실제로 목록을 감싸는 `<div className="mt-4">`(`PersonCardScreen.tsx` 335행)·`PersonList` 조상은 보지 않는다. 자식에 `max-w-*`/`mx-auto` 를 걸면 규칙이 깨져도 통과한다. E2E `card.spec.ts` 에도 폭 단언이 없다(`grep max-w|boundingBox` 0). 이번 커밋을 막을 정도는 아니다(사용자가 Chrome 1556px 에서 시각 확인, HANDOFF) — **P8b-persons-grid 에서** `person-list` 의 조상 전부에 폭 상한 클래스가 없음을 단언하거나 E2E `boundingBox()` 로 목록 폭 ≈ `main` 폭을 재는 테스트로 보강할 것.

**R-U10C-4 — 체크리스트 2항 "줄 폭이 너무 넓지 않다(본문 최대 폭 안)" 과 새 규칙의 관계.** 목록: 행마다 이름·태그·날짜 한 줄(`PersonList.tsx` 36~46행)이라 전체 폭이어도 "줄 폭" 문제가 아니다 — 충돌 아님. 상세: `md:w-3/4` 는 상한이 없어 넓은 창(예: 2560px, 사이드바 256px 제외 → 약 1700px)에서 타임라인 원문(`white-space: pre-wrap`)의 줄이 길어진다. 사용자 결정("창 크기에 따라 비율", CR-003 §1 표)이 01-plan 체크리스트 2항보다 뒤에 나온 상위 결정이므로 코드는 결정대로가 맞다. 다만 2항은 32행 점검에서 **사용자가 자기 화면으로 판정**하고, D15 를 쓸 때 "상세 75% 에 상한을 두지 않는다" 는 문장을 명시해 2항과의 관계를 닫을 것. 참고: 브리핑 화면은 이미 폭 상한이 없다(`BriefingScreen.tsx` 241행 `flex flex-col gap-4`) — 이번 변경이 새로 만든 불일치는 아니다.

**R-U10C-5 — 판정표 29·30행 증거 요건 충족도 (이 기록은 보조 증거, 29·30행은 여전히 사용자 몫).** `-1915-…fix035.txt` 와 `-1911-…db.txt` 로 ① 기동 명령·주소(키 값 없음, 0절) ② 발화 원문(A-1·B-1·C-1) ③ `pending_questions` id·kind·options(1911 §1) ④ answer·answered_at(같은 곳) ⑥ 인물 id 10·타임라인 항목 id 29 ⑦ `raw_utterance`(1911 §4) 는 충족. **미충족**: ⑤ "사용자 확인 문장(무엇이 보였는지·누른 칩·Chrome 버전)" — Chrome 154.0.8037.99 는 있으나 문장은 메인 세션의 것 · ⑥ "펼친 사실 id" — 사실 "근거 보기"를 펼치지 않았다(A-6 는 타임라인 원문만) · ⑧ 사용자 확인 문장 없음. 04-review 는 29·30행을 이 기록만으로 닫을 수 없고, 사용자 절차(01-plan 168~170행 3~5단계) 결과가 따로 필요하다는 한계를 적을 것. 증거 파일명도 01-plan 101행 관례(`*-u10-check-chat.txt`·`*-u10-check-card.txt`)와 다른 보조 이름이다 — 그대로 두되 04-review 에서 매핑.

**R-U10C-6 — CR-003 §4 0단계 ↔ SKILL.md 70행 "승인 즉시 `frozen: CR-nnn`".** 어긋난다. 사유는 CR-003 머리글에 있다("⑥을 지금 U10 수정에 로 정했으므로 그 수정이 끝날 때까지 제품 코드 쓰기를 열어 둔다"). 동결의 목적(결정이 흔들리는 동안 제품 코드가 계획과 어긋나지 않게)은 창 안의 제품 코드 변경이 CR 이 명시한 범위뿐이면 지켜진다 — `git status --short web/` = `card.test.tsx`·`PersonCardScreen.tsx` 2파일뿐, CR-003 ⑥(a) "클래스 2개 변경" 범위 안. **사유 기록으로 족하다.** 조건: 이 커밋 직후 `frozen: CR-003`(CR §4 1단계)을 걸고, journal 의 CR 줄에 "승인 2026-10-16 → 동결은 P8 커밋 `<해시>` 뒤" 를 남겨 창이 있었음을 추적 가능하게 할 것.

**R-U10C-7 — 루트 `test-results/.last-run.json`(19:17, `{"status":"failed","failedTests":[]}`).** `web/.gitignore` 13행에는 `test-results/` 가 있으나 루트 `.gitignore` 에는 없다(`git check-ignore` 무응답). `npm --prefix web run e2e` 는 `web/test-results/` 에만 쓴다(이번 재실행으로 확인 — 루트 파일 mtime 19:17 불변). 19:17 에 저장소 루트에서 Playwright 를 직접 실행한 흔적(설정 파일이 없어 실패)이다. **커밋 제외.** 삭제하거나 루트 `.gitignore` 에 `test-results/` 를 더할지는 하네스 변경이라 사용자 결정(FIX-014 가드 범위 밖의 프로그램 산출물).

**R-U10C-8 — `-1910-u10-check-chat-fix035-db.txt`(저장 실패본, 9줄) 포함 여부: 포함 권고.** 비밀 문자열 0(`grep` §5), 내용은 bash 문법 오류 한 줄뿐. 세 곳이 참조한다(`-1915-…` 4~6행 주석, `03-log.md` 203행 "1910 파일은 저장 실패본", HANDOFF "삭제 후보") — 제외하면 세 참조를 고쳐야 하고, 남기면 실패 경위가 추적된다(원칙8·9). 부수 소견: `save_evidence.py` 가 `--` 뒤 인자를 공백으로 이어 `bash -c` 에 넘겨 SQL 따옴표가 깨진 것은 사용법 한계(docstring 34행 "`--` 뒤 인자를 공백으로 이어 `bash -c` 로 실행") — 긴 SQL 은 1911 처럼 파일 리다이렉트가 맞다. L/FIX 후보로만 기록.

**R-U10C-9 — HANDOFF 사실 문장 1개가 낡았다.** "`tests.md` … (수동 6건, 집계 제외 — `기록 없음` grep 182 유지)" 는 FIX-035 수동 절만 있을 때 참이었고, 정렬 절(453·454행) 추가 뒤 184 다(R-U10C-2). R-U10C-2 를 어느 쪽으로 닫든 이 문장을 같이 고칠 것. 그 밖 HANDOFF·journal(735f391 두 줄)·registry(246행 "해시 pending")·03-log 203행의 사실(해시·CI run·수치)은 확인한 범위에서 맞다.

**R-U10C-10 — `data-testid="card-wrap"` 추가는 범위 안.** 결정 L/원칙7 의 금지 대상(서버 문자열 가공·새 화면·새 라우트·맞춤 디자인 반복)이 아니고, 같은 파일이 이미 `person-card`·`person-list` 를 쓴다(테스트 훅 관례). 래퍼 `div` 자체가 비율 폭을 거는 데 필요한 요소라 "테스트를 위한 제품 코드" 도 아니다. 소견 없음 — 기록만.

## 4. 사실 대조 — FIX-035 실서버 확인 기록 ↔ DB 원본 ↔ 재조회

| 기록(`tests.md` U10-F35-*, `-1915-…`) | DB 원본 `-1911-…db.txt` | verifier 재조회(19:43) |
|---|---|---|
| persons 10 · events 29(A)·30(C) | §5 `10 / 30`, §4 id 29·30 person_id 10 | `10` · `30` · 29/30 `raw_utterance` 동일 |
| pending_questions 12 identity → 13 new_person → 14 identity → 15 new_person, answer 값 | §1 4행 동일(answered_at 10:07:37 / 10:08:25 / 10:09:30 / 10:09:45 UTC) | max id 15 |
| trace 374 `identity_rejected=true`·`followup_question_id=13`, 396 → 15 | §7 동일 | `374\|true\|13`, `396\|true\|15` |
| er_resolve 407 merge 0.8654 → person 10 | §9 `merge 0.8653779689735086 10` | 동일 |
| A-5 응답 "기억했어요: 이벤트 1건." | §8 386 `stored {events 1, persons 1}` reply 동일 | — |
| B 생성 0 | §8 403 stored 전부 0, §5 persons 10 유지 | persons 10 |

쓰기 0 확인: 1911 의 SQL(스크래치패드 `u10_fix035.sql`, 20개 `select`/`\echo`)에 `update/insert/delete/alter/drop/truncate/create` 0건, 출력에 `UPDATE n`·`INSERT n` 태그 0건. 테스트 데이터(인물 10·사건 29·30·질문 12~15)는 개발 DB 에 남겼다(01-plan 174행 9단계, 원칙8) — 기록과 일치.

## 5. 커밋 포함 / 제외 판정

| 파일 | 판정 | 근거 |
|---|---|---|
| `web/src/screens/PersonCardScreen.tsx` · `web/src/__tests__/card.test.tsx` | **포함** | §1·§2 통과, 원복 해시 일치 |
| `docs/wiki/packages/P8-frontend/03-log.md` | **포함** — R-U10C-1 해소 확인(205~214행) | `-1949-…-recheck.txt` [1] |
| `docs/wiki/packages/P8-frontend/tests.md` | **포함** — R-U10C-2 해소 확인(grep 182) | `-1949-…-recheck.txt` [2] |
| `docs/wiki/HANDOFF.md` · `journal.md` · `registry.md` | **포함** — R-U10C-9 해소 확인("182 유지" 0건) | `-1949-…-recheck.txt` [3] |
| `docs/wiki/changes/CR-003.md` | **포함** | §6 영향 분석 확인, 비밀·절대 경로 0 |
| `docs/wiki/packages/P8-frontend/review-u10-deploy-validity.md` | **포함** | `grep -nE "/Users/\|/private/\|@gmail\|sk-…\|AKIA…\|-----BEGIN"` → 0건. 148행의 `ANTHROPIC_API_KEY`·`GEMINI_API_KEY` 는 환경변수 **이름**(값 없음) |
| `evidence/20261016-1910-…db.txt` | 포함(권고, R-U10C-8) | 비밀 0, 세 곳이 참조 |
| `evidence/20261016-1911-…db.txt` · `-1915-…fix035.txt` | **포함** | §4 일치. 1911 머리줄의 스크래치패드 절대 경로는 `save_evidence` 머리줄 관례(기존 evidence 144 파일에 같은 형태) |
| `evidence/20261016-1918-u10-fix-card-align-*.txt`(5) · `-1933/1934-…align2-*.txt`(6) | **포함** | 1차·2차 작업 증거 모두 CR-003 §1 표·registry 가 참조 |
| `evidence/20261016-1920/1925-verifier-u10-deploy-validity-*.txt`(5) | **포함** | survey 18·24·32행의 `OPENAI_API_KEY`·`POSTGRES_PASSWORD` 는 이름·참조 위치만(값 없음) |
| `evidence/20261016-194*-verifier-u10-closeout-*.txt`(6) · 이 문서 | 포함 | 이번 리뷰 증거 |
| `test-results/`(루트) | **제외** | R-U10C-7 |

## 6. CR-003 영향 분석 확인

| 주장 | 확인 | 결과 |
|---|---|---|
| R 해당 없음 | `grep -n "화면\|UI\|배치" docs/wiki/review-index.md` → R9(임베딩) 1건뿐 | 맞음 |
| 기존 D 무관 · D15 신설 | `docs/wiki/decisions/` D01~D14 제목 — 화면 배치 카드 없음(D07 TLS·D08 제목 등) | 맞음. D15 파일은 아직 없음(CR §4 2단계, 예정대로) |
| S 무변경 | 결정 ③(가) 프론트 필터 → API·스키마 손대지 않음 | 맞음 |
| 원칙5·7 유지 | 화면 3개·라우트 `#/persons/:id` 재사용, 태그 필터 제외 | 맞음 |
| 되돌릴 커밋 없음 | `git log --oneline -- web/src/components/PersonList.tsx web/src/components/AppShell.tsx` → `819cb2a 46532e7 761cced 977f2ee 975a8e5`, CR 인용과 동일 | 맞음 |
| 기획서 2장 표 "관계 태그 필터링" 제외 유지 | `docs/proposal.md` 60행 `\| 인물 카드 (사실 · 타임라인 · 마지막 접촉) \| 관계 태그 필터링 \|` — CR §1 "검색은 이름·별칭 문자열만" | 맞음. SKILL.md 81행 점검표 1 "태그 필터 침범 없음" 과도 일치 |
| §1 표 "이전: U10 수정 1회(미커밋) `max-w-4xl`" | `-1918-…mutation.txt` 테스트 이름 "폭 상한은 max-w-4xl" | 맞음(1차 작업 상태를 정확히 적음) |
| §4 0단계 | SKILL.md 70행과 어긋남 → R-U10C-6 | 사유 기록으로 족함(조건부) |
| `docs/wiki/INDEX.md` 에 CR-003 | 0건 | 아직 안 올림 — CR §4 2단계에서(지금은 결함 아님) |

## 7. 리뷰 범위 밖 · 기록

- 1차 정렬 작업(`-1918-…`, `max-w-4xl`)의 변이 1종 검출·136 passed 는 증거 파일로만 확인했고 재실행하지 않았다(현재 코드가 아님).
- `review-u10-deploy-validity.md` 내용은 재판정하지 않았다(요청 범위: 포함 가부만).
- `verify-impl.sh` 는 돌리지 않았다(완료 검토 단계가 아님 — `/devlog done` 에서).
