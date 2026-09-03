---
name: devlog
description: 개발 위키(docs/wiki) 운영 절차. 세션 재개(중단 작업 최우선, 사용자에게 우선순위 확인), 패키지·수정 작업의 시작(계획→기계 검증→정합성 점검→사용자 승인→활성화), 검증 결과→조치 계획 루프(findings), 완료(증거 기반 수용기준 검토), 기획서 변경 요청(CR, 출구 절차), 체크포인트(HANDOFF) 갱신을 수행한다. "이어서", "시작해", "착수", "패키지 열어", "FIX 기록", "기획서 바뀌었어", "상태 확인", "핸드오프" 요청에 쓴다. 제품 코드를 쓰기 전에는 반드시 이 절차로 활성 작업을 등록해야 한다(stage-gate 훅이 강제).
---

# devlog — 위키 운영 절차

## 원칙

- 위키는 **꺼내 보는 참고자료**다. 시작 시 `docs/wiki/INDEX.md`와 `CURRENT.md`(재개면 `HANDOFF.md`)만 읽고, 태그가 가리키는 카드만 연다.
- 모든 문서는 `docs/wiki/templates/`의 형식을 그대로 쓴다. 항목을 빼지 않는다(비어 있으면 "없음").
- 기획서 정합성은 **계획 단계에서** 검증한다. 코드가 생긴 뒤 검증하면 늦다.
- **검증은 증거로만** (`verification.md`). 기계 검증 스크립트 출력을 그대로 붙이고, FAIL/WARN 은 `findings.py`로 소견을 만들어 조치 계획을 쓴다. "확인했습니다"는 빈 칸으로 간주한다.
- 승인은 `AskUserQuestion`으로 받고, 문서의 `승인:` 줄에 "사용자 (YYYY-MM-DD)"를 적는다. 훅은 이 줄이 있어야 코드 쓰기를 허용한다.
- 계획·검증·구현은 모두 위키에 남긴다. 만들기 전에 `registry.md`를 grep 한다(중복 방지). 날짜·마일스톤은 쓰지 않는다.

## 하위 명령

### `/devlog resume`   ← 세션 시작·재개·압축 후 첫 행동
1. `HANDOFF.md`(자동 주입됨)의 "진행 중"·"바로 다음", `CURRENT.md` active/frozen, `git status --short`, 열린 소견(`packages/*/05-remediation.md` 의 `상태: 열림`)을 모아 **중단된 작업 목록**을 만든다.
2. 목록이 비어 있지 않으면 **다른 어떤 일보다 먼저** `AskUserQuestion`으로 보여주고 항목별 우선순위를 정한다. 선택지: 이어서 완료(권장) / 보류 / 폐기(변경을 되돌린다 — 되돌리기는 `git revert`·파일 단위 복구만, `checkout -- .` 금지).
3. 결정대로 `HANDOFF.md` "바로 다음"을 다시 쓰고, 첫 항목부터 시작한다. 새 요청이 있어도 중단 작업을 먼저 정리한 뒤 받는다(사용자가 명시적으로 순서를 바꾸면 그대로).

### `/devlog status`
`CURRENT.md`, `HANDOFF.md` 요약, `journal.md` 마지막 5줄, 활성 패키지 `01-plan.md` 작업 단위 체크 상태, 열린 소견 수를 보여준다.

### `/devlog start <패키지 id>`   (id는 INDEX.md "패키지 id" 표의 것만)
1. 선행 조건: `CURRENT.md active`가 none(한 번에 하나), `frozen`이 none.
2. `docs/backlog.md`에서 해당 항목(의존·수용기준)을 읽는다. 선행 패키지 `04-review.md` `결과: 완료` 확인. **P5 이후는 `P4-pilot-eval` 완료 없이 시작하지 않는다.**
3. `review-index.md`에서 이 패키지가 닫는 R → "다음 카드"(D, S)를 연다. 원문은 카드가 지시하는 절만. `registry.md`를 grep 해 이미 있는 산출물을 확인한다. **git log 를 본다(L-001)**: `bash .claude/scripts/gitlog.sh <id> <D/S 태그>` — 선행 패키지 완료 커밋, 같은 태그의 기존 커밋, 미커밋 변경을 확인하고 02-plan-verify 점검표 5·7 의 근거에 커밋 해시를 적는다. 현재 브랜치가 `dev` 인지 확인한다.
4. `packages/<id>/01-plan.md`를 `templates/plan.md`로 작성. 작업 단위(U1, U2 …)마다 `Refs:`. 수용 기준은 backlog와 **글자 그대로**.
5. **기계 검증**: `mkdir -p packages/<id>/evidence` 후
   `bash .claude/scripts/verify-plan.sh <id> | tee docs/wiki/packages/<id>/evidence/<ts>-verify-plan.txt`
   FAIL/WARN 이 있으면 `python .claude/scripts/findings.py <id> <그 파일> --source verify-plan` → `05-remediation.md` 소견을 채우고 계획을 고친 뒤 다시 실행(FAIL 0 까지, 3회 한도).
6. **`verifier` 에이전트에 위임**(L-002: 계획을 쓴 쪽이 점검표를 채우지 않는다)하여 `02-plan-verify.md`를 `templates/plan-verify.md`로 작성: `검증자: verifier (fable)`, 1절에 기계 검증 출력 전체, 2절 점검표 8행은 각각 **카드 파일명 + 인용 문장**을 근거로 판정. 위임 프롬프트에는 패키지 id·읽을 카드 목록·evidence 경로를 적는다. `verify-plan.sh`는 검증자 줄에 `verifier`가 없으면 FAIL 한다. 보류가 하나라도 있으면 `결과: 보류`로 두고 사용자에게 보고하고 멈춘다.
7. 통과면 `AskUserQuestion`으로 계획 요약(목표·작업 단위·수용 기준·기계 검증 결과·읽은 카드)을 보여주고 승인을 받는다. 선택지: 승인 / 수정 요청 / 보류.
8. 승인되면 `02-plan-verify.md`에 `승인: 사용자 (날짜)`, `CURRENT.md`에 `active: <id>`, `03-log.md`를 템플릿으로 생성, `journal.md`에 `START` 줄, `HANDOFF.md` 갱신, `/commit`(계획 문서 커밋).
9. 이 시점부터 제품 코드를 쓸 수 있다. 작업 단위 하나가 끝날 때마다 `/commit`. 새 산출물은 `registry.md`에 행 추가.

### 검증 → 조치 루프 (구현 중 문제가 나왔을 때, `verification.md` "루프")
1. `bash .claude/scripts/verify-impl.sh <id> | tee docs/wiki/packages/<id>/evidence/<ts>-verify-impl.txt` (pytest 출력도 같은 방식으로 파일에)
2. `python .claude/scripts/findings.py <id> <그 파일> --source verify-impl` → `05-remediation.md`에 소견 블록.
3. 소견마다 채운다: 원인 가설 → 확인 명령 실행·출력 인용 → **해결 단계 표**(단계 = 파일·방법 + 완료 판정 명령 + 기대 출력). 명령 없는 단계는 쓰지 않는다.
4. 단계를 순서대로 실행하고 완료 판정 명령을 실제로 실행해 상태를 완료로. 결정·명세(D/S/원칙)를 바꿔야만 풀리는 소견은 멈추고 `/devlog fix` 또는 `/devlog change`로 올려 사용자에게 보고.
5. 1의 같은 명령 재실행 → 2 재실행 → 사라진 소견은 자동 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 재시도하지 않고 사용자에게 보고(원칙8).
6. 소견 해소도 작업 단위 → `/commit` (Refs 에 F-id).

### `/devlog fix <한 줄 제목>`
1. 다음 번호 `FIX-nnn`으로 `fixes/FIX-nnn.md`를 `templates/fix.md`로 작성. 증상은 검증 출력·테스트 출력 인용, 원인, 수정안, 회귀 테스트(명령).
2. **기획서 정합성**: 수정이 원칙·D·S를 바꾸면 FIX가 아니다 → D 카드 갱신 또는 `/devlog change`.
3. 정합성 점검표 적용 → `검증: 통과`, `AskUserQuestion` 승인 → `승인:` 기록.
4. 활성 패키지가 있으면 그대로 두고 FIX를 진행한다. 없으면 `CURRENT.md active: FIX-nnn`.
5. 수정 후 `/commit` (`Refs: FIX-nnn`). `## 결과`에 해시·테스트 출력 경로, `journal.md`에 `FIX` 줄, active를 원래 값으로.

### `/devlog done`
1. `bash .claude/scripts/verify-impl.sh <id> | tee …/evidence/<ts>-verify-impl.txt` → FAIL 은 루프로. 열린 [필수] 소견이 있으면 완료가 아니다.
2. **`verifier` 에이전트에 위임**(L-002: 구현한 쪽이 완료 검토를 쓰지 않는다)하여 `04-review.md`를 `templates/package-review.md`로 작성: `검토자: verifier (fable)`, 1절 기계 검증 출력 전체, 2절 수용 기준마다 증거(evidence 파일·해시·경로 — 문장 금지), 3절 부정 케이스(verifier 가 직접 실행), 5절 registry 등록 목록. `verify-impl.sh`는 검토자 줄에 `verifier`가 없으면 FAIL 한다. 1단계의 verify-impl 실행도 verifier 가 한다.
3. 닫힌 R의 `review-index.md` 상태를 "구현완료(해시)"로. `docs/backlog.md` 체크박스. 열린 문제는 FIX/L 로 이관.
4. `AskUserQuestion` 완료 승인 → `승인:` → `CURRENT.md active: none` → `journal.md` `DONE` → `HANDOFF.md` → `/commit`.
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
| 평가 데이터·지표 | `eval-agent` | opus | 데이터셋·metrics·리포트 | 자기 데이터셋의 완료 검토 |
| 검증 | `verifier` | fable | 02-plan-verify 점검표, 04-review, 05 원인 분석, 코드 리뷰 | 코드·계획·카드 수정 |
| 조율 | 메인 세션 | (현재 모델) | 위임, AskUserQuestion 승인, /commit, HANDOFF | 점검표·완료 검토를 직접 채우기 |

- 한 패키지에서 같은 에이전트가 두 단계 이상을 맡지 않는다. 메인 세션이 급하다고 점검표를 직접 쓰면 `verify-plan.sh`/`verify-impl.sh`가 `검증자:`/`검토자:` 줄로 잡는다.
- verifier 는 새 컨텍스트로 띄운다(이전 대화를 잇지 않는다). 위임 프롬프트에 구현자의 자기 평가("잘 됐다")를 넣지 않고 파일 경로만 준다.
- 모델을 바꾸려면 `.claude/agents/<name>.md` 의 `model:` 과 이 표·CLAUDE.md 팀 표를 같은 커밋에서 고친다.

- architect/backend-agent/eval-agent/verifier 는 `AskUserQuestion`이 없다. **승인·우선순위 결정 단계는 메인 세션이 한다.** 서브에이전트는 계획 초안·검증표·코드·증거 파일을 만들고 돌아온다.
- 위임 프롬프트에는 패키지 id, 읽을 카드 목록(전문 금지), 작업 단위 번호, 증거를 남길 경로(`packages/<id>/evidence/`)를 명시한다.
