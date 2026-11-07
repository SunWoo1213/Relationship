---
name: devlog
description: 개발 위키(docs/wiki) 운영 절차. 세션 재개(HANDOFF 의 "바로 다음"대로 바로 이어감), 패키지·수정 작업의 시작(계획→기계 검증→verifier 정합성 점검→활성화, 승인 없음), 검증 결과→조치 계획 루프(findings), 완료(증거 기반 수용기준 검토 → 사용자 완성 확인 1회 → 승격), 기획서 변경 요청(CR, 출구 절차), 체크포인트(HANDOFF) 갱신을 수행한다. "이어서", "시작해", "착수", "패키지 열어", "FIX 기록", "기획서 바뀌었어", "상태 확인", "핸드오프" 요청에 쓴다. 제품 코드를 쓰기 전에는 반드시 이 절차로 활성 작업을 등록해야 한다(stage-gate 훅이 강제).
---

# devlog — 위키 운영 절차

## 원칙

- 위키는 **꺼내 보는 참고자료**다. 시작 시 `docs/wiki/INDEX.md`와 `CURRENT.md`(재개면 `HANDOFF.md`)만 읽고, 태그가 가리키는 카드만 연다.
- 모든 문서는 `docs/wiki/templates/`의 형식을 그대로 쓴다. 항목을 빼지 않는다(비어 있으면 "없음").
- 기획서 정합성은 **계획 단계에서** 검증한다. 코드가 생긴 뒤 검증하면 늦다.
- **검증은 증거로만** (`verification.md`). 기계 검증 스크립트 출력을 그대로 붙이고, FAIL/WARN 은 `findings.py`로 소견을 만들어 조치 계획을 쓴다. "확인했습니다"는 빈 칸으로 간주한다.
- **사용자 승인 관문은 없다(L-006, 2026-11-07).** 계획 승인·단계 시작 승인(옛 L-004)·커밋 승인·dev 푸시 뒤 대기(옛 L-003)는 폐지됐다. 요청을 받으면 계획 → 계획 검증 → 구현 → 테스트 → 완료 검토 → 커밋·dev2 푸시까지 **묻지 않고** 진행한다. 훅은 verifier 의 `결과: 통과`(stage-gate)·`검증: 통과 — verifier`(commit-guard)만 본다.
- **사람이 보는 지점은 하나다.** 완료 검토(04-review)가 `결과: 완료` 가 되면 `AskUserQuestion` 으로 "완성됐다. 확인해 달라"를 한 번 묻는다(`/devlog done` 4단계). 확인이면 dev·main 승격까지 이어서 하고, 수정 필요면 FIX 로 계속한다.
- **결정은 여전히 묻는다.** 계획이 비워 둔 상수·범위·정렬·상한(사용자 결정 A~N 류), 기획서 변경(CR 수용/거절), 되돌리기(폐기)처럼 **사용자만 정할 수 있는 것**은 승인이 아니라 결정이므로 `AskUserQuestion` 으로 묻고 진행한다. 계획 단계에서 한 번에 모아 묻는다(위임 뒤 왕복 방지).
- 에이전트는 절차가 가리키는 자리에서 바로 띄운다(architect → verifier → 구현 에이전트 → verifier). 역할·모델 분리(L-002)는 그대로다.
- 계획·검증·구현은 모두 위키에 남긴다. 만들기 전에 `registry.md`를 grep 한다(중복 방지). 날짜·마일스톤은 쓰지 않는다.

## 하위 명령

### `/devlog resume`   ← 세션 시작·재개·압축 후 첫 행동
1. `HANDOFF.md`(자동 주입됨)의 "진행 중"·"바로 다음", `CURRENT.md` active/frozen, `git status --short`, 열린 소견(`packages/*/05-remediation.md` 의 `상태: 열림`)을 모아 **중단된 작업 목록**을 만든다.
2. 목록이 비어 있지 않으면 사용자에게 한두 줄로 알리고 **HANDOFF 의 "바로 다음"대로 바로 이어간다**(L-006 — 우선순위를 묻지 않는다). 사용자가 새 요청을 같이 보냈으면 그 요청을 먼저 받고, 중단 작업은 HANDOFF 에 남겨 둔다. 폐기(변경 되돌리기)는 사용자가 말했을 때만 한다 — `git revert`·파일 단위 복구만, `checkout -- .` 금지.
3. 진행 중 상태가 HANDOFF 와 다르면 "바로 다음"을 다시 쓰고 첫 항목부터 시작한다.

### `/devlog status`
`CURRENT.md`, `HANDOFF.md` 요약, `journal.md` 마지막 5줄, 활성 패키지 `01-plan.md` 작업 단위 체크 상태, 열린 소견 수를 보여준다.

### `/devlog start <패키지 id>`   (id는 INDEX.md "패키지 id" 표의 것만)
1. 선행 조건: `CURRENT.md active`가 none(한 번에 하나), `frozen`이 none.
2. `docs/backlog.md`에서 해당 항목(의존·수용기준)을 읽는다. 선행 패키지 `04-review.md` `결과: 완료` 확인. **P5 이후는 `P4-pilot-eval` 완료 없이 시작하지 않는다.**
3. `review-index.md`에서 이 패키지가 닫는 R → "다음 카드"(D, S)를 연다. 원문은 카드가 지시하는 절만. `registry.md`를 grep 해 이미 있는 산출물을 확인한다. **git log 를 본다(L-001)**: `bash .claude/scripts/gitlog.sh <id> <D/S 태그>` — 선행 패키지 완료 커밋, 같은 태그의 기존 커밋, 미커밋 변경을 확인하고 02-plan-verify 점검표 5·7 의 근거에 커밋 해시를 적는다. 현재 브랜치가 `dev2`(작업·실험 브랜치, L-001 개정 2026-09-29)인지 확인한다.
4. `packages/<id>/01-plan.md`를 `templates/plan.md`로 작성(architect 에 위임, 바로 띄운다). 작업 단위(U1, U2 …)마다 `Refs:`. 수용 기준은 backlog와 **글자 그대로**. 계획이 비워 둔 상수·범위·상한이 있으면 **이 시점에 한 번에** `AskUserQuestion` 으로 후보와 권장안을 보여 확정받는다(결정, 승인 아님).
5. **기계 검증**: `mkdir -p packages/<id>/evidence` 후
   `python3 .claude/scripts/save_evidence.py <id> verify-plan -- bash .claude/scripts/verify-plan.sh <id>` 를 실행해 `docs/wiki/packages/<id>/evidence/<ts>-verify-plan.txt` 에 출력 전체를 저장한다
   (FIX-034 — `tee`·`>` 는 프로젝트 안 쓰기라 bash-write-guard 가 거부하고, Write 로 옮겨 적지 않는다).
   FAIL/WARN 이 있으면 `bash .claude/scripts/findings.sh <id> <그 파일> --source verify-plan` → `05-remediation.md` 소견을 채우고 계획을 고친 뒤 다시 실행(FAIL 0 까지, 3회 한도).
6. **`verifier` 에이전트에 위임**(L-002: 계획을 쓴 쪽이 점검표를 채우지 않는다)하여 `02-plan-verify.md`를 `templates/plan-verify.md`로 작성: `검증자: verifier (fable)`, 1절에 기계 검증 출력 전체, 2절 점검표 8행은 각각 **카드 파일명 + 인용 문장**을 근거로 판정. 위임 프롬프트에는 패키지 id·읽을 카드 목록·evidence 경로를 적는다. `verify-plan.sh`는 검증자 줄에 `verifier`가 없으면 FAIL 한다. 보류가 있으면 [필수] 소견을 계획에 반영해 다시 verifier 에 보낸다(3회 한도, 그 뒤에는 사용자에게 보고). 보류 사유가 **사용자 결정**을 요구하면 그것만 묻는다.
7. `결과: 통과` 면 승인 없이 바로 활성화한다(L-006): `CURRENT.md`에 `active: <id>`, `03-log.md`를 템플릿으로 생성, `journal.md`에 `START` 줄, `HANDOFF.md` 갱신, `/commit`(계획 문서 커밋). 계획 요약(목표·작업 단위·수용 기준·검증 결과)은 사용자에게 **보고**만 한다.
8. 이 시점부터 제품 코드를 쓸 수 있다. 구현 에이전트를 바로 띄우고, 작업 단위 하나가 끝날 때마다 verifier 커밋 전 리뷰 → `/commit` → dev2 푸시. 새 산출물은 `registry.md`에 행 추가. 모든 단위가 끝나면 `/devlog done`.

### 검증 → 조치 루프 (구현 중 문제가 나왔을 때, `verification.md` "루프")
1. `python3 .claude/scripts/save_evidence.py <id> verify-impl -- bash .claude/scripts/verify-impl.sh <id>` 로 `docs/wiki/packages/<id>/evidence/<ts>-verify-impl.txt` 에 출력 전체 저장 (pytest 출력도 같은 방식 `save_evidence.py <id> pytest -- …`. Write 로 옮겨 적지 않는다, FIX-034)
2. `bash .claude/scripts/findings.sh <id> <그 파일> --source verify-impl` → `05-remediation.md`에 소견 블록.
3. 소견마다 채운다: 원인 가설 → 확인 명령 실행·출력 인용 → **해결 단계 표**(단계 = 파일·방법 + 완료 판정 명령 + 기대 출력). 명령 없는 단계는 쓰지 않는다.
4. 단계를 순서대로 실행하고 완료 판정 명령을 실제로 실행해 상태를 완료로. 결정·명세(D/S/원칙)를 바꿔야만 풀리는 소견은 멈추고 `/devlog fix` 또는 `/devlog change`로 올려 사용자에게 보고.
5. 1의 같은 명령 재실행 → 2 재실행 → 사라진 소견은 자동 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 재시도하지 않고 사용자에게 보고(원칙8).
6. 소견 해소도 작업 단위 → `/commit` (Refs 에 F-id).

### `/devlog fix <한 줄 제목>`   (FIX-027: 계획 점검과 검증을 분리 — 메인 세션은 FIX 코드를 직접 고치지 않는다)
1. 다음 번호 `FIX-nnn`으로 `fixes/FIX-nnn.md`를 `templates/fix.md`로 작성. 증상은 검증 출력·테스트 출력 인용, 원인, 수정안, 회귀 테스트(명령).
2. **기획서 정합성**: 수정이 원칙·D·S를 바꾸면 FIX가 아니다 → D 카드 갱신 또는 `/devlog change`.
3. 정합성 점검표 적용 → **메인 세션이** `계획 점검: 통과`(점검표 1~8, 근거 요약)를 쓴다(승인 없음, L-006). **`검증:` 줄은 메인 세션이 쓰지 않는다** — 빈 칸(`검증: (verifier 가 쓴다 — 제품 코드를 바꾸면 커밋 전 review-FIX-nnn.md 와 함께)`)으로 둔다. L-002 는 패키지뿐 아니라 FIX 에도 적용된다. `stage-gate.sh` 는 코드를 쓰기 전 이 `계획 점검:` 줄만 본다(F-27-1) — `검증:` 줄의 실제 판정은 6단계에서 커밋 시점에 본다. 수정안이 사용자 결정(값·범위)을 요구하면 그것만 묻는다.
4. 활성 패키지가 있으면 그대로 두고 FIX를 진행한다. 없으면 `CURRENT.md active: FIX-nnn`.
5. **구현은 구현 에이전트(`backend-agent`·`eval-agent`·`frontend-agent` — 평가 산출물 `evaluation/`·`reports/` 를 바꾸는 FIX 는 eval-agent, 프론트 `web/` 을 바꾸는 FIX 는 frontend-agent)에 바로 위임한다(L-006 — 시작 승인 없음)**. 메인 세션은 코드를 직접 고치지 않는다(조율·커밋만, CLAUDE.md "팀 구성"). **위임 프롬프트에 FIX-033 의 네 규칙을 넣는다**: (a) 계약 값은 값으로 단언하고 "변이→잡는 테스트" 표를 보고 · (b) 계획에 없는 상수·정렬·상한·방어 조건은 구현하기 전에 멈추고 보고 · (c) 증거는 `save_evidence.py <패키지|fixes> <이름> -- <명령>` 으로 명령 출력 전체(Write 로 옮겨 적지 않는다, FIX-034) · (d) 임시 파일은 스크래치패드 리터럴 절대 경로.
6. **제품 코드(`app/`·`alembic/`·`web/`)를 바꾼 FIX/test 커밋은 verifier 리뷰가 먼저다.** 구현 에이전트 작업이 끝나면 바로 `verifier`에게 커밋 전 코드 리뷰를 맡겨 `fixes/review-FIX-nnn.md`(`검토자: verifier (fable)`, 본 것·직접 실행한 검증 명령·판정 근거·소견)를 쓰게 한다. **단위마다 핵심 계약 변이 시험을 최소 1개 돌리게 고정한다**(저장소 밖 사본 또는 런타임 치환, 저장소 무수정 — 방법은 `verification.md` "변이 시험 방법"). 통과하면 verifier 가 `FIX-nnn.md`의 `검증:` 줄을 채운다(예: `검증: 통과 — verifier (fable) 2026-10-06, review-FIX-nnn.md`). `commit-guard.sh`가 이 두 가지(검증 줄에 `통과` 와 `verifier` 둘 다 + review 문서 존재·추적 여부)를 커밋 시점에 확인해, 없으면 거부한다(FIX-027). 훅·문서만 바꾸는 FIX(제품 코드 무변경)는 review 문서를 생략할 수 있지만 `검증:` 줄은 여전히 verifier 가 쓴다.
7. 리뷰 통과 뒤 **사용자가 요청한 FIX 라면** 커밋 전에 `AskUserQuestion` 으로 "수정이 끝났다(테스트·리뷰 결과 요약). 확인해 달라"를 한 번 묻는다(L-006 의 완성 확인 — 선택지: 확인 / 수정 필요). 패키지 진행 중 내부에서 발생한 FIX 는 묻지 않고 패키지 완료 확인에 포함한다. 그 뒤 `/commit` (`Refs: FIX-nnn`) → dev2 푸시. `## 결과`에 해시·테스트 출력 경로, `journal.md`에 `FIX` 줄, active를 원래 값으로.

### `/devlog done`
1. `bash .claude/scripts/verify-impl.sh <id>` 를 `python3 .claude/scripts/save_evidence.py <id> verify-impl -- bash .claude/scripts/verify-impl.sh <id>` 로 실행해 `docs/wiki/packages/<id>/evidence/<ts>-verify-impl.txt` 에 전체 저장(FIX-034; `tee`·`>` 는 bash-write-guard 가 거부한다) → FAIL 은 루프로. 열린 [필수] 소견이 있으면 완료가 아니다.
2. **`verifier` 에이전트에 위임**(L-002: 구현한 쪽이 완료 검토를 쓰지 않는다)하여 `04-review.md`를 `templates/package-review.md`로 작성: `검토자: verifier (fable)`, 1절 기계 검증 출력 전체, 2절 수용 기준마다 증거(evidence 파일·해시·경로 — 문장 금지), 3절 부정 케이스(verifier 가 직접 실행), 5절 registry 등록 목록. `verify-impl.sh`는 검토자 줄에 `verifier`가 없으면 FAIL 한다. 1단계의 verify-impl 실행도 verifier 가 한다. 3절에는 단위마다 핵심 계약 변이 시험 최소 1개(저장소 밖 사본 또는 런타임 치환, 저장소 무수정)를 포함한다.
3. 닫힌 R의 `review-index.md` 상태를 "구현완료(해시)"로. `docs/backlog.md` 체크박스. 열린 문제는 FIX/L 로 이관.
4. **유일한 사용자 확인 지점(L-006).** `결과: 완료` 면 `AskUserQuestion` 으로 "완성됐다. 확인해 달라"를 묻는다 — 보여 줄 것: 무엇이 생겼나(기능 한 줄), 수용 기준 통과 수, 테스트 수치, 열린 [권고] 소견, 확인하는 방법(실행 명령·화면). 선택지: **확인** / **수정 필요(내용)**. 확인 → `04-review.md` `확인: 사용자 (날짜)` → `CURRENT.md active: none` → `journal.md` `DONE` → `HANDOFF.md` → `/commit` → `git push origin dev2` → `git push origin dev2:dev` → `git push origin dev:main`(`/commit` §5). 수정 필요 → 내용을 FIX 로 만들어 `/devlog fix` 로 계속하고 완료 확인을 다시 묻는다.
5. P4-pilot-eval 미달이면 "부분완료 + 실패 케이스 분석 산출물"로 기록하고 `S3.3` 재설계를 `/devlog change` 또는 새 D 카드로 올린다(원칙8).

### `/devlog change <기획서 변경 한 줄>`   ← 기획서가 바뀔 때의 출구 절차
1. 다음 번호 `CR-nnn`으로 `changes/CR-nnn.md`를 `templates/change-request.md`로 작성.
2. **영향 분석은 태그로**: 바뀌는 기획서 절 → `review-index.md`의 R → 그 행의 D·S → INDEX 패키지 표의 P → `git log --oneline --grep '<태그>'` 영향 커밋. 결과를 CR 2절에 붙인다(출력 인용).
3. 선택지(수용/부분/거절)·비용·위험 표 → `AskUserQuestion`으로 사용자 결정.
4. 승인 즉시 `CURRENT.md frozen: CR-nnn`(제품 코드 쓰기 동결). 이행은 CR 4절 순서: 새 D 카드(옛 D는 `대체됨(→Dnn)`) → S 카드 → `CLAUDE.md` → `docs/backlog.md` → `review-index.md` → `docs/proposal.md` 상단 "원본 이후 확정된 사항" 한 줄(본문은 원본 유지) → 영향 코드 `git revert` 목록 또는 FIX → `frozen: none` → `journal.md` `CR`. 문서 갱신 한 커밋, 코드 되돌리기·수정은 별도 커밋(각 `Refs: CR-nnn`).
5. 거절이면 사유를 남기고 상태를 거절로. 기획서는 그대로.

### `/devlog handoff`   ← 체크포인트
1. `HANDOFF.md`를 현재 상태로 다시 쓴다: 갱신 시각, active/frozen, 마지막으로 끝낸 것, 진행 중(파일·함수·어디까지), 커밋 안 된 변경(`git status --short` 요약), 바로 다음 1~3개, 재개 시 읽을 카드, 열린 질문, 주의. 60줄 이내.
2. **언제**: 작업 단위 종료마다(`/commit`에 포함), 큰 파일·여러 파일 읽기 직전, 대화가 길어졌다고 느낄 때(도구 호출 수십 회, 큰 출력 여러 번), 턴 종료 전(Stop 훅 `handoff-check.sh`가 검사). 남은 토큰·컨텍스트 표시가 **20% 미만이면 새 작업 단위를 시작하지 않고** 마무리·HANDOFF·`/commit`만 한다.

## 정합성 점검표 (plan-verify · fix · commit 공용)

| # | 항목 | 어디를 보나 (근거 열에 파일명 + 인용) |
|---|------|-------------|
| 1 | 범위 — 기획서 2장 제외(상담·A–B 관계·페르소나·음성·네이티브·태그 필터) 침범 없음 | `docs/proposal.md` 2장 표, CLAUDE.md 원칙7 |
| 2 | 불변 원칙 1~9 위반 없음 | CLAUDE.md "불변 원칙" |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | `decisions/D*.md` |
| 4 | S 카드와 일치 — 스키마 v2·시그니처 v2·임계치 2개·ask_user 비동기 | `specs/S3.*.md` |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | `docs/backlog.md`, `packages/*/04-review.md` |
| 6 | 수용 기준이 backlog와 동일 | `docs/backlog.md` |
| 7 | 작업 단위마다 Refs 태그 | 계획서 자체 |
| 8 | 보안 카드 위반 없음 — 비밀·외부 전송·삭제 | `security.md` |

## 태그 규칙

- `Refs:`에는 **닫는 R**, **기대는 D**, **구현하는 S**, **속한 P**, 해소한 **F-id/FIX/CR** 을 모두 적는다. 예: `Refs: P3-er D3 D10 S3.3 R4 F-1a2b3c`
- 커밋 메시지·계획서·로그·코드 주석(모듈 docstring 첫 줄)에 같은 표기. `git log --grep`, `grep -r`로 역추적하기 위해서다.

## 서브에이전트에게 위임할 때

### 역할별 모델 분리 (L-002 — 같은 컨텍스트·같은 모델의 자기 평가는 후하다)

| 단계 | 에이전트 | 모델 | 쓰는 문서 | 하지 않는 것 |
|------|---------|------|-----------|-------------|
| 계획 | `architect` | opus | 01-plan 초안, backlog | 점검표 판정, 코드 |
| 구현 | `backend-agent` | sonnet | 코드·테스트, 03-log 초안, 05 해결 단계 | 02-plan-verify·04-review 판정 |
| 구현(프론트) | `frontend-agent` | sonnet | `web/` 코드·테스트, 03-log 초안 | 02-plan-verify·04-review 판정, `app/`·`alembic/` |
| 평가 데이터·지표 | `eval-agent` | opus | 데이터셋·metrics·리포트 | 자기 데이터셋의 완료 검토 |
| 검증 | `verifier` | fable | 02-plan-verify 점검표, 04-review, 05 원인 분석, 코드 리뷰 | 코드·계획·카드 수정 |
| 조율 | 메인 세션 | (현재 모델) | 위임, 사용자 결정·완성 확인 질문, /commit, HANDOFF | 점검표·완료 검토를 직접 채우기 |

- 한 패키지에서 같은 에이전트가 두 단계 이상을 맡지 않는다. 메인 세션이 급하다고 점검표를 직접 쓰면 `verify-plan.sh`/`verify-impl.sh`가 `검증자:`/`검토자:` 줄로 잡는다.
- verifier 는 새 컨텍스트로 띄운다(이전 대화를 잇지 않는다). 위임 프롬프트에 구현자의 자기 평가("잘 됐다")를 넣지 않고 파일 경로만 준다.
- 모델을 바꾸려면 `.claude/agents/<name>.md` 의 `model:` 과 이 표·CLAUDE.md 팀 표를 같은 커밋에서 고친다.

- architect/backend-agent/eval-agent/frontend-agent/verifier 는 `AskUserQuestion`이 없다. **사용자 결정·완성 확인은 메인 세션이 한다.** 서브에이전트는 계획 초안·검증표·코드·증거 파일을 만들고 돌아온다.
- 위임 프롬프트에는 패키지 id, 읽을 카드 목록(전문 금지), 작업 단위 번호, 증거를 남길 경로(`packages/<id>/evidence/`)를 명시한다.
