# P7-push · 완료 검토 (04-review)

날짜: 2026-10-10 | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

대상: `01-plan.md`(판정 표 1~26행 · "지킬 불변식" · "수동 확인 절차") · `03-log.md`(U1~U8) · `evidence/` · 커밋 `608694b..6428180`. 검토 시점 HEAD = `6428180`(dev2 = origin/dev2), 미커밋 변경은 `docs/wiki/journal.md`·`docs/wiki/HANDOFF.md`(문서) 뿐 — 제품 코드 미커밋 변경 0(`git status --short -- app tests alembic` 빈 출력).

**24행 기준 해석(사용자 결정 2026-10-10)**: "`git diff --stat 608694b -- <P6 판정 근거 경로>` 가 빈 출력" 을 **"P7-push 단위 커밋이 그 경로를 바꾼 것이 0건이면 통과"** 로 읽는다. verifier 가 커밋별 분해를 직접 재실행해 확인했다(§2 24행, `evidence/20261010-2005-review-row24-decomposition.txt`).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P7-push | tee docs/wiki/packages/P7-push/evidence/20261010-2010-verify-impl.txt` (1차 — 이 문서를 쓰기 전. 스크립트 내부 타임스탬프는 `1959` 라 산출 파일은 `evidence/20261010-1959-{pytest,lint,commits,summary}.txt` 다)
```
== verify-impl P7-push  (20261010-1959) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1873 passed, 1 warning in 21.70s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261010-1959-pytest.txt
WARN  ruff 경고/오류 → evidence/20261010-1959-lint.txt
PASS  태그 P7-push 커밋 15 건 → evidence/20261010-1959-commits.txt
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.6
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P7-push 행 있음
WARN  미완료 작업 단위 4 개
== 결과: FAIL=0 WARN=3 → evidence/20261010-1959-summary.txt ==
```
- 1차 WARN 3 의 뜻: ① ruff — `ruff check .` 가 `.claude/scripts/findings.py` 의 기존 3건(DTZ005 ×2, F541)을 보고한다(`evidence/20261010-1959-lint.txt`). CI 범위 `ruff check app tests scripts evaluation` 은 "All checks passed!"(verifier 재실행, `evidence/20261010-2005-review-negative-cases.txt` B-[10]) — 이 패키지 변경이 아니다. ② 04-review 부재 — 이 문서로 해소. ③ 01-plan U1~U4 체크박스가 `[ ]` 로 남아 있다(U5~U8 만 `[x]`) — 커밋 `85393e0`·`6c98516`·`f256259`·`8e9af9e` 가 있으므로 문서 누락이다(§6-6).
- pytest: **1873 passed, skip 0**(`-rs` 에 SKIPPED 줄 0, `evidence/20261010-1959-pytest.txt`). 01-plan 25행 기준선 1724 이상. U7 evidence(`20261008-1536-u7-regression.txt`)의 1873 과 같은 수.
- 커밋 15건 중 P7 단위·문서 커밋은 13건(`fa5802d` `a69af80` `85393e0` `6c98516` `47adb1e` `f256259` `8e9af9e` `b89c936` `55fc0f3` `572045a` `b73aaf0` `6428180` + `b89c936` 은 HANDOFF 문서). `7c94aad`(P2-tools)·`7459925`(FIX-020)·`32db187`(README)은 본문에 "P7-push" 문자열이 있어 grep 에 걸린 것이고 P7 단위가 아니다(U1 03-log 16행·U7 evidence 가 같은 설명).

FAIL 은 `findings.py … --source verify-impl` 로 05-remediation.md 에 올리고 조치·재검증한다. 열린 [필수] 소견이 있으면 결과는 완료가 될 수 없다. → 1차 FAIL 0. 2차 출력은 §1-2.

### 1-2. 기계 검증 2차 출력 (이 문서를 쓴 뒤 — 증거 열 검사 포함)
명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P7-push | tee docs/wiki/packages/P7-push/evidence/20261010-2015-verify-impl-2.txt` (스크립트 내부 타임스탬프 `2010` — 산출 `evidence/20261010-2010-{pytest,lint,commits,summary}.txt`)
```
== verify-impl P7-push  (20261010-2010) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1873 passed, 1 warning in 22.99s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261010-2010-pytest.txt
WARN  ruff 경고/오류 → evidence/20261010-2010-lint.txt
PASS  태그 P7-push 커밋 15 건 → evidence/20261010-2010-commits.txt
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.6
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  데스크톱 Chrome에서 알림 수신 (`docs/backlog.md` 84행 그대로)  ← evidence/20261010-1950-u8-chrome-manual.
PASS  증거 확인:  해석 ㄱ 구독 저장 — `POST /push/subscriptions` → `push_s ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  해석 ㄴ VAPID 발송 — 수동·주기 경로 모두 `WebPushNotifier`, 결과 ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  해석 ㄷ 알림이 사람 눈에 보임, 본문은 결정 B 규칙·원문 없음  ← evidence/20261010-1950-u8-chrome-manual.
PASS  증거 확인:  1행 ㄱ 구독 저장 양성  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  2행 ㄱ 같은 엔드포인트 → 행 1·같은 id·created false·keys 갱신  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  3행 ㄱ 잘못된 본문 422·행 0  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  4행 ㄱ 공개키 API 200/404/404  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  5행 ㄱ 사용자 격리  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  6행 ㄴ 발송 양성(수동 경로 한 흐름)  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  7행 ㄴ 주기 경로도 같은 알림기  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  8행 ㄴ 키 없을 때 기존 동작  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  9행 ㄴ 반쪽 설정 → misconfigured, 발송 0, briefed_at  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  10행 ㄷ 본문 규칙(결정 B)  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  11행 ㄷ 제안 없음 꼬리  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  12행 ㄷ 원문 미포함(페이로드 JSON)  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  13행 ㄷ 길이·TTL  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  14행 구독 0건 → no_subscription  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  15행 만료 410+201 → partial·행 삭제·removed  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  16행 만료 404 단독 → failed·행 삭제  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  17행 일시 오류 → failed, briefing_error 0, 재선정 0  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  18행 발송기 예외 매핑 5종  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  19행 근거 기록(push_send trace 모양, tokens 0/0)  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  20행 비밀 미기록  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  21행 네트워크 0  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  22행 확인 페이지 스위치  ← evidence/20261008-1536-u7-judgment-table
PASS  증거 확인:  23행 불변식 grep 8종  ← evidence/20261008-1536-u7-invariants-noc
PASS  증거 확인:  24행 무변경(alembic check · tools_check · P6 경로 diff) ← evidence/20261008-1536-u7-invariants-noc
PASS  증거 확인:  25행 전체 회귀 ≥1724·skip 0  ← evidence/20261008-1536-u7-regression.txt
PASS  증거 확인:  26행 ㄷ 사람 확인 — Chrome 알림 수신(③⑤⑥⑦⑧ 한 파일)  ← evidence/20261010-1950-u8-chrome-manual.
PASS  registry 에 P7-push 행 있음
WARN  미완료 작업 단위 4 개
== 결과: FAIL=0 WARN=2 → evidence/20261010-2010-summary.txt ==
```
2차: **FAIL 0 / WARN 2**(ruff 기존 3건 · 01-plan U1~U4 체크박스), 수용 기준 표 30행 증거 전부 실재 확인, pytest 두 번째도 1873 passed skip 0. 2차 출력을 `python .claude/scripts/findings.py P7-push evidence/20261010-2015-verify-impl-2.txt --source verify-impl` 로 올려 `05-remediation.md` 에 [권고] 소견 2건(`F-8aebe7` ruff · `F-2f0840` 체크박스)이 생겼고, verifier 는 원인 분석 칸까지 채웠다(해결은 메인 세션·구현 에이전트). 그 밖에 §6-1 순환 import 를 출처 `review` 소견으로 같은 파일에 추가했다. 열린 [필수] 0.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 데스크톱 Chrome에서 알림 수신 (`docs/backlog.md` 84행 그대로) | evidence/20261010-1950-u8-chrome-manual.txt, 6428180, evidence/20261010-2005-review-negative-cases.txt | 통과 — 26행 다섯 항목 ③⑤⑥⑦⑧ 한 파일 안에 있음(§C-[d]), 비밀 0(§C-[a][b][c]) |
| 해석 ㄱ 구독 저장 — `POST /push/subscriptions` → `push_subscriptions(user_id, endpoint, keys)` 한 행 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-1950-u8-chrome-manual.txt, 6c98516, app/push/subscriptions.py | 통과 — 1~5행 + U8 ③ 구독 1행(user_id local, host fcm.googleapis.com) |
| 해석 ㄴ VAPID 발송 — 수동·주기 경로 모두 `WebPushNotifier`, 결과가 응답 `push`·trace 에 남음 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-1950-u8-chrome-manual.txt, 8e9af9e, 55fc0f3 | 통과 — 6~9·14~21행 + U8 ⑤ `push=="sent"`·⑥ trace 232 status_code 201 |
| 해석 ㄷ 알림이 사람 눈에 보임, 본문은 결정 B 규칙·원문 없음 | evidence/20261010-1950-u8-chrome-manual.txt, evidence/20261010-2005-review-mutation.txt | 통과 — ⑦ 수신 기록·⑧ 사용자 문장, 본문 "10/11 19:00 · 브리핑이 준비됐어요"(요약 줄·원문 없음) |
| 1행 ㄱ 구독 저장 양성 | evidence/20261008-1536-u7-judgment-table.txt, tests/test_push_subscriptions.py | 통과 (2 passed) |
| 2행 ㄱ 같은 엔드포인트 → 행 1·같은 id·created false·keys 갱신 | evidence/20261008-1536-u7-judgment-table.txt, tests/test_push_subscriptions.py | 통과 — FIX-020 이후 ON CONFLICT upsert 로 구현(§6-4) |
| 3행 ㄱ 잘못된 본문 422·행 0 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — 6 케이스, verifier 재실행 PASSED |
| 4행 ㄱ 공개키 API 200/404/404 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — 404 두 경우 verifier 재실행 PASSED, 200 응답에 개인키 값 없음 단언(테스트 182행) |
| 5행 ㄱ 사용자 격리 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-mutation.txt | 통과 — 변이 M2(user_id 조건 제거)에서 FAILED 확인 |
| 6행 ㄴ 발송 양성(수동 경로 한 흐름) | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261008-1510-u5-wiring.txt, tests/test_push_wiring.py | 통과 — 발송 2회·briefed_at==T·trace 1행·같은 세션(R-1) |
| 7행 ㄴ 주기 경로도 같은 알림기 | evidence/20261008-1536-u7-judgment-table.txt, app/briefing/scheduler.py, 55fc0f3 | 통과 — `scheduler.py` 102행 `notifier_from_env(session, ctx.user_id, ctx.now)` |
| 8행 ㄴ 키 없을 때 기존 동작 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — `not_configured`, P6 회귀 6파일 95 passed, verifier 재실행 PASSED |
| 9행 ㄴ 반쪽 설정 → misconfigured, 발송 0, briefed_at | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 |
| 10행 ㄷ 본문 규칙(결정 B) | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-mutation.txt | 통과 — 변이 M1(요약 줄 덧붙임)에서 FAILED 확인 |
| 11행 ㄷ 제안 없음 꼬리 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-1950-u8-chrome-manual.txt | 통과 — U8 실발송 본문이 이 경로("브리핑이 준비됐어요") |
| 12행 ㄷ 원문 미포함(페이로드 JSON) | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-mutation.txt | 통과 — 변이 M1 에서 FAILED 확인 |
| 13행 ㄷ 길이·TTL | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261005-1920-u3-payload.txt | 통과 (5 passed) |
| 14행 구독 0건 → no_subscription | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261005-1934-u4-notifier.txt | 통과 |
| 15행 만료 410+201 → partial·행 삭제·removed | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — verifier 재실행 PASSED |
| 16행 만료 404 단독 → failed·행 삭제 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 |
| 17행 일시 오류 → failed, briefing_error 0, 재선정 0 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — 결정 C(i) 가 `run.py` 무변경으로 성립 |
| 18행 발송기 예외 매핑 5종 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-mutation.txt, app/push/sender.py | 통과 — 변이 M4(gone 코드 제거)에서 FAILED 확인 |
| 19행 근거 기록(push_send trace 모양, tokens 0/0) | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-1950-u8-chrome-manual.txt | 통과 — U8 trace 232 가 같은 모양(+`reason` 키, §7) |
| 20행 비밀 미기록 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — R-8 감시 문자열 2건 verifier 재실행 PASSED |
| 21행 네트워크 0 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — R-2 양성·부정 확인 PASSED |
| 22행 확인 페이지 스위치 | evidence/20261008-1536-u7-judgment-table.txt, evidence/20261010-2005-review-mutation.txt | 통과 — 꺼짐 404 ×6·잘못된 값 4·경로 탐색 6 PASSED, 변이 M3(항상 켜짐)에서 FAILED 확인 |
| 23행 불변식 grep 8종 | evidence/20261008-1536-u7-invariants-nochange.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — verifier 재실행 [1]~[7] 기대값(§6-9 `__pycache__` 비고) |
| 24행 무변경(alembic check · tools_check · P6 경로 diff) | evidence/20261008-1536-u7-invariants-nochange.txt, evidence/20261010-2005-review-row24-decomposition.txt | 통과(사용자 해석) — "No new upgrade operations detected." · "RESULT: 7/7 ok" · 경로를 바꾼 커밋은 FIX-019 4912865·FIX-020 7459925·FIX-021 b124c8e·FIX-025 3cd378c·FIX-026 90f249c 뿐, P7 커밋 전부 0, `90f249c..HEAD` 빈 출력 |
| 25행 전체 회귀 ≥1724·skip 0 | evidence/20261008-1536-u7-regression.txt, evidence/20261010-1959-pytest.txt | 통과 — 1873 passed, skip 0 (U7·verifier 두 번) |
| 26행 ㄷ 사람 확인 — Chrome 알림 수신(③⑤⑥⑦⑧ 한 파일) | evidence/20261010-1950-u8-chrome-manual.txt, evidence/20261010-2005-review-negative-cases.txt | 통과 — ③ 구독 1행(호스트만) · ⑤ `"push": "sent"` · ⑥ trace 232 `status_code 201` · ⑦ `2026-10-10T10:49:55.624Z schedule_id=5 tag=schedule-5` · ⑧ 사용자 원문 "브리핑이 준비됐다고 떴어, 수신기록 줄이 생겼어" (§6-7 형식 비고) |

### 2-1. 비고 (표에 못 넣는 설명)
- **결정 A 최종 판정(02-plan-verify 2행에서 04-review 로 넘긴 것) — 양립, CR 불필요.** 조건 ①②③ 이 코드로 유지되는지 증거: ① 제품 자료 미조회 — `grep -nE "/chat|/briefings|/persons|/answers" app/push/devpage/*` 0건(§B-[5]), `tests/test_push_devpage.py::test_invariant_no_product_data_endpoints_in_devpage`·`test_invariant_page_does_not_draw_title_or_body` PASSED(§A), `sw.js` 가 페이지에 넘기는 것은 `{received_at, schedule_id, tag}` 뿐(파일 12~16행), `index.html` 본문 "제품 화면이 아니라 … 도구입니다". ② 기본 꺼짐 — `test_off_by_default_three_paths_404` ×6 PASSED, 변이 M3 으로 "항상 켜짐" 이면 FAILED 가 됨을 확인(`evidence/20261010-2005-review-mutation.txt`), `app/main.py` 92행 `if not push_dev_page_enabled(): return`(경로 자체 미등록). ③ 운영 미사용·P8 인계 — `docs/RUNNING.md` 314행 "운영에서는 켜지 않는다", `registry.md` 201행 유형 "확인 도구(제품 화면 아님, 스위치 기본 꺼짐)" + "제품 화면에서 링크하지 않는다(P8 인계)", 03-log U6 69행. 제품 프론트(P8)는 아직 없으므로 "링크하지 않는다" 는 P8 04-review 에서 다시 확인해야 한다(§7).
- **U8 ⑧ 과 ⑥⑦ 대조(R-9)**: ⑤ 응답 `schedule_id 5` = ⑥ trace input `schedule_id 5` = ⑦ `schedule_id=5 tag=schedule-5`. ⑥ payload body "10/11 19:00 · 브리핑이 준비됐어요" ↔ ⑧ "브리핑이 준비됐다고 떴어". 발송 10:49:53.93Z → 서비스 워커 수신 10:49:55.62Z → `briefed_at` 10:49:53.94Z. 끊긴 지점 없음.
- U8 에서 메인 세션이 쓴 명령은 로컬 서버(`localhost:8765`)·DB 조회뿐이고 키 생성·`.env` 읽기는 하지 않았다고 증거 파일 3~4행이 밝힌다. verifier 는 대화 밖 증거를 갖지 않으므로 그 진술 자체는 검증하지 않고, **결과물에 비밀이 없음**만 grep 으로 확인했다(§3).

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
| 케이스 | 명령 | 증거 |
|--------|------|------|
| 스위치 꺼짐·빈 값이면 `/push-dev/` 세 경로 404 (×6) | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -v tests/test_push_devpage.py::test_off_by_default_three_paths_404` | evidence/20261010-2005-review-negative-cases.txt (A) |
| 잘못된 스위치 값 4종 → `InvalidValue` 로 앱 생성 실패(조용히 꺼지지 않음) | `… tests/test_push_devpage.py::test_invalid_switch_value_raises_invalid_value` | evidence/20261010-2005-review-negative-cases.txt (A) |
| 켜져 있어도 세 파일 외 경로·`..` 탐색 6종 404/307 | `… tests/test_push_devpage.py::test_other_paths_not_served` | evidence/20261010-2005-review-negative-cases.txt (A) |
| 잘못된 구독 본문 6종 → 422·행 0 | `… tests/test_push_subscriptions.py::test_create_subscription_invalid_body_returns_422_and_no_row` | evidence/20261010-2005-review-negative-cases.txt (A) |
| VAPID 전무·반쪽 → 공개키 404 `push_not_configured` | `… tests/test_push_subscriptions.py::test_vapid_public_key_returns_404_when_*` | evidence/20261010-2005-review-negative-cases.txt (A) |
| 원문·요약 줄이 발송 페이로드에 없음 / 만료 410·404 행 삭제 / 일시 오류에 briefing_error 0·재선정 0 / 예외 메시지 속 감시 문자열이 trace·SendResult 에 없음 / 소유자 불일치 fail-closed / R-2 픽스처 양성·부정 / 키 없음·반쪽 경로 | `… tests/test_push_notifier.py::<8건> tests/test_push_wiring.py::<3건>` (39 passed) | evidence/20261010-2005-review-negative-cases.txt (A) |
| **변이 M1** 요약 줄을 본문에 덧붙이면 10·12행 테스트가 FAILED | `MUT=payload_leaks_lines PYTHONPATH=<scratchpad> … pytest -p mutations …` | evidence/20261010-2005-review-mutation.txt |
| **변이 M2** `list_subscriptions` 가 user_id 조건을 빼면 5행 FAILED | `MUT=subscriptions_ignore_user …` | evidence/20261010-2005-review-mutation.txt |
| **변이 M3** 스위치 무시하고 항상 등록하면 22행 ×6 FAILED | `MUT=devpage_always_on …` | evidence/20261010-2005-review-mutation.txt |
| **변이 M4** 404/410 을 gone 으로 안 보면 18행 FAILED | `MUT=sender_no_gone …` | evidence/20261010-2005-review-mutation.txt |
| 불변식 grep 8종 재실행 + `alembic check` + `tools_check` 7/7 + ruff(CI 범위) + `pywebpush==2.5.0` 설치본 일치 | 01-plan "지킬 불변식" 절 명령 그대로(bash -c) | evidence/20261010-2005-review-negative-cases.txt (B) |
| U8 증거 파일에 키 형태(43자+ base64url)·엔드포인트 경로·p256dh/auth·PRIVATE KEY 0건, ③⑤⑥⑦⑧ 머리줄 5개 | `grep -nE "[A-Za-z0-9_-]{43,}" …` 등 4개 | evidence/20261010-2005-review-negative-cases.txt (C) |
| P7 문서·증거 전체(01~03·evidence·RUNNING·HANDOFF·journal)와 추적 코드에 VAPID 값 형태 0건 | `grep -rnoE "[A-Za-z0-9_-]{43,}" …` / `git grep -nE "VAPID_(PRIVATE|PUBLIC)_KEY *= *…" -- docs app tests scripts alembic .github` | §1-2 아래 "3-1" (출력 인용) |
| **부정 결과(결함 발견)** `python -c "import app.push"` 가 HEAD 에서 순환 import 로 실패 — 01-plan U1 판정 명령의 회귀 | `.venv/bin/python -c "import app.push"` 등 8개 모듈 | evidence/20261010-2005-review-import-cycle.txt (§6-1) |

### 3-1. 문서·코드 비밀 grep 출력 (verifier 직접 실행, 2026-10-10 20:08 — `.env` 는 열지 않았다)
```
$ grep -rnoE "[A-Za-z0-9_-]{43,}" docs/wiki/packages/P7-push/ docs/RUNNING.md docs/wiki/HANDOFF.md docs/wiki/journal.md | grep -vE "test_[a-z0-9_]+|_{3,}|-{3,}|={3,}"
(출력 없음) rc=1   ← 키 형태(43자 이상 base64url 연속) 문자열 0 — 긴 테스트 이름·구분선만 제외했다
$ grep -rnE "BEGIN (EC )?PRIVATE|fcm\.googleapis\.com/[A-Za-z]" docs/wiki/packages/P7-push/ docs/RUNNING.md docs/wiki/HANDOFF.md docs/wiki/journal.md
docs/wiki/packages/P7-push/03-log.md:59: … security §1(`grep BEGIN PRIVATE KEY` 0건, …)   ← grep 명령을 설명한 문장 1건뿐, 키 블록·엔드포인트 경로 없음
$ git grep -nE "VAPID_(PRIVATE|PUBLIC)_KEY *= *[A-Za-z0-9_-]{20,}" -- docs app tests scripts alembic .github
(출력 없음) rc=1
```
(처음 시도한 명령은 pathspec 에 `.env` 글자가 들어 `safety-guard` 가 막았다 — 우회하지 않고 `.env` 를 언급하지 않는 범위로 바꿔 다시 실행했다.)

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- **R12** — 현재 `docs/wiki/review-index.md` 20행: "구현완료(절반 — 브리핑 트리거: P6-briefing e2155f9…e2cca80 … 푸시 구독 저장·발송은 P7-push)". 아직 "절반" 이다. 이 검토로 푸시 절반이 닫혔으므로 메인 세션이 `/devlog done` 3단계에서 **"구현완료(P6-briefing e2155f9…e2cca80 + P7-push 85393e0…6428180: 구독 저장 6c98516·발송 8e9af9e·연결 55fc0f3·Chrome 실수신 6428180)"** 로 바꾼다(verifier 는 review-index 를 고치지 않는다). `docs/backlog.md` 84행 P7 체크박스도 같은 단계.
- 근거 커밋: `git log --grep R12` 에 P7 커밋 `85393e0 6c98516 8e9af9e 55fc0f3 b73aaf0 6428180` 이 들어 있음(verify-impl "PASS 커밋에 태그 존재: R12").

## 5. registry.md 에 올린 산출물
`grep -n "P7-push" docs/wiki/registry.md` (검토 시점):
- 새 행(패키지 열 `P7-push`): 201 `app/push/devpage/index.html · sw.js · devpage.js`(유형 "확인 도구(제품 화면 아님, 스위치 기본 꺼짐)", `572045a`) · 202 `app/main.py` 확인 페이지 등록(`572045a`) · 203 `tests/test_push_devpage.py`(`572045a`) · 204 `app/push/types.py, app/push/__init__.py`(`85393e0`) · 206 `tests/test_push_settings.py`(`85393e0`) · 207 `app/push/subscriptions.py`(`6c98516`) · 209 `tests/test_push_subscriptions.py`(`6c98516`) · 210 `app/push/payload.py`(`f256259`) · 211 `tests/test_push_payload.py`(`f256259`) · 212 `app/push/sender.py`(`8e9af9e`) · 213 `app/push/notifier.py`(`8e9af9e`) · 214 `tests/test_push_notifier.py`(`8e9af9e`) · 216 `tests/test_push_wiring.py`(`55fc0f3`).
- 기존 행 비고 확장: 64 `app/api/deps.py`(`get_notifier`, `55fc0f3`) · 65 `app/api/routes.py`(`run_briefings_endpoint` notifier, `55fc0f3`) · 198 `app/briefing/scheduler.py`(`default_run_once` 알림기, `55fc0f3`) · 205 `app/settings.py`(`vapid_config`·`push_dev_page_enabled`·상수 3, `85393e0` — `.env.example`·`requirements.txt` 도 이 비고) · 208 `app/api/routes.py, app/api/schemas.py`(`/push/*` 두 엔드포인트, `6c98516`) · 215 `app/api/deps.py`(`get_notifier`, `55fc0f3`).
- 01-plan 산출물 절의 파일 15개(모듈 6·정적 3·테스트 6) + 기존 파일 7개 전부 등록돼 있다. 비고 중 사실과 다른 곳 1: 207행 "유일 제약이 없어 동시 요청의 중복 행은 막지 못한다(결정 F(i))" — FIX-020 `7459925` 가 `UNIQUE(user_id, endpoint)`(alembic 0002)와 ON CONFLICT upsert 로 바꿨다(§6-4).

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
[필수] 0건. 아래는 전부 [권고]·FIX/L 후보이며 05-remediation 에 같은 번호로 올렸다(출처 verify-impl 또는 review). 코드·계획·카드는 verifier 가 고치지 않았다.

1. **[권고 — FIX 후보] `app.push` 단독 import 가 순환 import 로 실패한다.** `python -c "import app.push"`(01-plan U1 판정 명령) → `ImportError: cannot import name 'notifier_from_env' from partially initialized module 'app.push.notifier'`. 경로: `app/push/__init__.py:38` → `app/push/notifier.py:65`(`app.briefing.types`) → `app/briefing/__init__.py:27`(scheduler) → `app/briefing/scheduler.py:79` `from app.push.notifier import notifier_from_env`. 도입 커밋 U5 `55fc0f3`(U4 `8e9af9e` 시점 scheduler 에 `app.push` 없음). `app.main`/`app.briefing` 을 먼저 올리는 제품 진입점·테스트·U8 실서버에는 영향이 없어 수용 기준은 통과하지만, U1 판정 명령이 HEAD 에서 깨진 회귀이고 `app.push` 를 먼저 import 하는 스크립트가 생기는 순간 터진다. 증거 `evidence/20261010-2005-review-import-cycle.txt`. 해결 방향(구현 에이전트 몫): `scheduler.py` 의 import 를 `default_run_once()` 안으로 내리거나(지연 import — `composer_from_env` 와 같은 "호출 시점" 규약), `notifier.py` 가 `app.briefing.types` 대신 패키지 `__init__` 를 거치지 않도록 `app/briefing/__init__.py` 의 scheduler 재export 를 지연시킨다. 사용자가 이 항목을 [필수] 로 올리면 완료 승인 전에 FIX 가 먼저다.
2. **[권고] `docs/RUNNING.md` 웹푸시 절 ③·④·⑥ 예시 포트 8000 vs U8 실행 8765.** RUNNING 안에서는 셋 다 8000 으로 일관되고(287·290·297행), 8765 는 HANDOFF 41행이 정한 시험 포트다. 문서 결함이 아니라 "포트는 임의, 세 곳을 같게" 한 줄이 없을 뿐 → RUNNING ③ 에 한 문장 추가 권고. 수용 기준과 무관.
3. **[권고 — L 후보] U7 절차: 에이전트가 VAPID 키 생성 코드를 실행했다.** 03-log U7 81행 "에이전트는 값을 출력하지 않고 길이·`Vapid.from_string` 왕복 일치만 확인". 01-plan "하지 않는 것" 은 "VAPID 키 생성·`.env` 기록을 에이전트가 하는 것 … 키 값이 출력되는 명령도 에이전트가 실행하지 않는다" 다. 판정: **보안 결과 위반 없음**(출력·저장·증거 어디에도 키 값 0 — §3 grep, 일회용 키는 테스트 픽스처가 매번 만드는 것과 같은 성질), **계획 문구 위반 있음**(생성 자체를 하지 말라고 적혀 있었다). 절차 교훈으로 남길 것: 계획이 "검증용 일회용 생성은 허용(값 미출력 조건)" 인지 "생성 금지" 인지를 애초에 구분해 적고, 구현자는 문구가 금지면 문서 명령의 동작 확인을 사용자에게 넘긴다. FIX 불필요.
4. **[권고] FIX-020 이후 문서 표류.** `7459925` 가 P7 범위 안의 `app/push/subscriptions.py` 를 ON CONFLICT upsert 로 바꾸고 `push_subscriptions(user_id, endpoint)` UNIQUE 를 걸었다(S3.1 25행 보충 줄·`alembic/versions/0002`·`app/db/models.py` 252행). 01-plan 결정 F(i)·리스크 "같은 엔드포인트 경쟁 … 유일 제약이 없어" 와 registry 207행 비고는 그 전 사실이다. 판정 2행 테스트는 새 구현에서도 통과한다. 조치: registry 207행 비고 한 줄 갱신(01-plan 은 작성 당시 사실이므로 그대로 두되 03-log 나 이 절이 설명). FIX-020 자체의 검증(`검증: 통과 — 사용자가 FIX 로 판단`, verifier 리뷰 파일 없음 — FIX-027 규칙 이전)은 P7 범위 밖.
5. **[권고] 03-log U8 항목 머리줄 해시 `pending`** → 실제 `6428180`. 다음 커밋에서 채운다(U5·U7 때와 같은 관례).
6. **[권고] 01-plan U1~U4 체크박스 `[ ]`**(verify-impl WARN "미완료 작업 단위 4 개"). 커밋 `85393e0`·`6c98516`·`f256259`·`8e9af9e` 와 03-log 항목이 있으므로 `[x]` 로. 완료 승인 뒤 메인 세션이 고치면 2차 WARN 이 해소된다(P6-memory 때와 같음).
7. **[권고] U8 ⑧ 사용자 확인 문장이 계획 형식(시각·Chrome 버전·OS 버전·제목)을 갖추지 않았다.** 사용자 원문 "브리핑이 준비됐다고 떴어, 수신기록 줄이 생겼어" — 표시 사실·본문 내용·수신 기록은 담고 있어 26행 "⑧ 사용자 확인 문장" 조건은 충족으로 본다(⑥⑦ 기계 증거가 함께 있다). Chrome 버전·OS 버전은 재현성 메모이므로 사용자가 원하면 한 줄 추가(없는 값을 메인 세션이 지어 넣지 않는다).
8. **[권고] ruff WARN** — `.claude/scripts/findings.py` DTZ005 ×2·F541(CI 범위 밖 하네스 스크립트). 이 패키지와 무관, 하네스 정리 때 함께.
9. **[비고] 불변식 [1] `grep -rln "pywebpush" app/` 이 `app/push/__pycache__/sender.cpython-314.pyc` 도 잡는다.** 소스는 `sender.py` 하나로 불변식 충족. 다음 계획에서 같은 불변식을 쓸 때 `--include=*.py` 를 붙이면 캐시 상태에 따라 결과가 달라지지 않는다.
10. **[비고] `push_send.output` 에 `reason` 키가 있다**(판정 19행 모양 `{schedule_id, status, results, removed, payload, ttl}` + R-6 보완으로 더한 `reason`, 정상 경로 `null`). U8 trace 232 에서도 `"reason": null`. 19행 테스트는 통과하고 어휘가 넓어진 것뿐 — P8·P10 이 trace 를 읽을 때 알아야 할 사항(§7).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- **P8-frontend**: `GET /push/vapid-public-key` → `{public_key}`(404 `push_not_configured`), `POST /push/subscriptions` ← `PushSubscription.toJSON()` 모양(`endpoint` https·≤2048, `keys.p256dh/auth` base64url, `expirationTime` 무시) → `{id, created}`. 같은 `(user_id, endpoint)` 는 UNIQUE + upsert(FIX-020). PWA 서비스 워커의 `push` 처리는 `app/push/devpage/sw.js`(제목·본문·`tag="schedule-{id}"`·`schedule_id`) 를 옮겨 쓰고 알림 클릭 → 브리핑 화면을 더한다. **제품 화면에서 `/push-dev/` 를 링크하지 않는다**(결정 A 조건 — P8 04-review 에서 재확인). 응답 `briefings[].push` 어휘 6종 `sent·partial·failed·no_subscription·not_configured·misconfigured`. 구독 해제 API 는 없다.
- **P9-infra**: `VAPID_PUBLIC_KEY`·`VAPID_PRIVATE_KEY`·`VAPID_SUBJECT` 를 SSM → 환경변수로(코드는 `.env` 를 읽지 않는다), `PUSH_DEV_PAGE_ENABLED` 는 비움, HTTPS(D7). 반쪽 설정은 기동을 막지 않고 `push=="misconfigured"` 로만 드러나므로 배포 점검 항목에 `GET /push/vapid-public-key` 200 확인을 넣는다.
- **P10-final-eval**: `push_send.output.payload.body` 에 원문 조각이 섞인 비율 표본 점검(결정 B 한계 — 제안 문장은 검증기가 원문 인용을 거르지 않는다). trace `output.reason`(`owner_mismatch`|null) 키 존재.
- **FIX 후보**: §6-1 순환 import(`55fc0f3`). 발송이 일정 행 잠금(SKIP LOCKED)·세이브포인트 안에서 네트워크를 타는 구조(01-plan 리스크, `PUSH_TIMEOUT_SECONDS=10`×구독 수)는 그대로다.
- 상수(코드 고정, 환경변수 아님): `PUSH_TIMEOUT_SECONDS=10.0` · `PUSH_TTL_MAX_SECONDS=86400` · `PUSH_BODY_MAX_CHARS=120`(`app/settings.py`).
- 개발 DB 에 U8 확인용 구독 행 id=1(user `local`, host fcm)·일정 id=5·인물 id=7·trace 232 가 남아 있다(01-plan ⑩ "남겨도 된다").

결과: 완료
승인: 사용자 2026-10-10 — §6-1 순환 import 는 사용자 결정으로 [필수] 취급해 FIX-029 `e555142` 로 먼저 닫은 뒤 완료 승인(CI run 38049456285 세 job success). 24행은 사용자 해석 "P7 단위 커밋의 그 경로 변경 0건" 으로 통과. 권고 처리: 03-log U8 해시 · 01-plan U1~U4 `[x]` · registry 구독 행 비고(FIX-020 유일 제약) · RUNNING.md 포트 안내 한 줄 · review-index R12 · backlog P7. U7 키 생성 절차 소견은 L 카드 후보로 남김
