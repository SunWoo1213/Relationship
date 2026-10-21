# P8-frontend · 완료 검토 (04-review)

날짜: 2026-10-21 | 검토자: verifier (fable) — 구현자(backend-agent·frontend-agent)·메인 세션과 다른 모델·새 컨텍스트(L-002). 코드·계획·카드·03-log·tests.md 는 고치지 않았다. 커밋하지 않았다. `.env` 는 읽지 않았다.

기준 문서: `01-plan.md`(수용 기준 23~32행 · 판정 표 1~32행 125~164행 · 사람 점검 절차 166~175행 · 화면 점검 체크리스트 178~202행 · 지킬 불변식 356~367행) · `docs/backlog.md` 88행(수용 기준 원문) · `02-plan-verify.md` 134~135행(결과·승인 조건 ①②, N-1~N-3) · `03-log.md`(U0~U10·FIX-035·정렬·CR-003 항목) · `tests.md`(총계 203 + FIX-035 7 = 210, U10 절 3개) · `05-remediation.md`(열림 0 / 해소 1) · 단위 리뷰 `review-u0-harness.md` … `review-u9b-backend.md` · `review-u10-closeout.md` · `review-u10-deploy-validity.md` · `docs/wiki/fixes/review-FIX-035.md` · 카드 D01·D02·D07·D15·S3.4·S3.6 · `docs/wiki/verification.md`. HEAD `75cb4ad`(dev2, 제품 코드는 `3bd5025` 와 같음). 미커밋: `HANDOFF.md`·`journal.md`·`03-log.md`·`tests.md`(문서) + U10 증거 8개(untracked). `app/`·`alembic/`·`web/` 미커밋 변경 0(`git status --porcelain app alembic` 빈 출력 — N-3, `evidence/20261021-2135-verifier-04-mutation-be.txt` 끝 `git status --short app tests alembic` 빈 출력).

## 1. 기계 검증 출력 (그대로 붙인다)

명령(1차, 04-review 작성 전): `python3 .claude/scripts/save_evidence.py P8-frontend verifier-04-verify-impl-pre -- POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P8-frontend` → `evidence/20261021-2131-verifier-04-verify-impl-pre.txt`
```
# 명령: POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P8-frontend
# 시각: 2026-10-21T21:31:45+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 75cb4ad (dev2)
# exit: 0
# ---
== verify-impl P8-frontend  (20261021-2131) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1953 passed, 1 warning in 26.28s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261021-2131-pytest.txt
WARN  ruff 경고/오류 → evidence/20261021-2131-lint.txt
PASS  태그 P8-frontend 커밋 22 건 → evidence/20261021-2131-commits.txt
PASS  커밋에 태그 존재: CR-003
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D15
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: D7
PASS  커밋에 태그 존재: FIX-014
PASS  커밋에 태그 존재: FIX-031
PASS  커밋에 태그 존재: FIX-033
PASS  커밋에 태그 존재: FIX-034
PASS  커밋에 태그 존재: FIX-035
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.5
PASS  커밋에 태그 존재: S3.6
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P8-frontend 행 있음
WARN  미완료 작업 단위 11 개
== 결과: FAIL=0 WARN=3 → evidence/20261021-2131-summary.txt ==
```
WARN 3 의 뜻: ① ruff — `evidence/20261021-2131-lint.txt` 의 4건은 전부 하네스 스크립트(`.claude/scripts/bash_write_check.py:1228` B007 · `.claude/scripts/findings.py:129·130` DTZ005 · `:163` F541)이고 제품 코드(`app/`·`web/`) 0건 — P7-push 04-review 와 같은 처리(이관, R-U10R-8). ② 04-review 부재 — 이 문서로 해소(2차 출력 아래). ③ "미완료 작업 단위 11 개" — `01-plan.md` 87~101행 U0~U10 체크박스가 `- [ ]` 그대로(P6-memory 선례: 승인 뒤 메인 세션이 닫는다, R-U10R-7). **FAIL 0 → 소견(`findings.sh`) 생성 대상 없음.**

### 1-1. 2차 실행 (이 문서를 쓴 뒤)

명령: `python3 .claude/scripts/save_evidence.py P8-frontend verifier-04-verify-impl-post2 -- POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P8-frontend` → `evidence/20261021-2145-verifier-04-verify-impl-post2.txt`
```
# 명령: POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P8-frontend
# 시각: 2026-10-21T21:45:09+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: 75cb4ad (dev2)
# exit: 0
# ---
== verify-impl P8-frontend  (20261021-2145) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1953 passed, 1 warning in 23.55s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261021-2145-pytest.txt
WARN  ruff 경고/오류 → evidence/20261021-2145-lint.txt
PASS  태그 P8-frontend 커밋 22 건 → evidence/20261021-2145-commits.txt
PASS  커밋에 태그 존재: CR-003
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D15
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: D7
PASS  커밋에 태그 존재: FIX-014
PASS  커밋에 태그 존재: FIX-031
PASS  커밋에 태그 존재: FIX-033
PASS  커밋에 태그 존재: FIX-034
PASS  커밋에 태그 존재: FIX-035
PASS  커밋에 태그 존재: R12
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.5
PASS  커밋에 태그 존재: S3.6
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  채팅 확인 칩  ← evidence/20261021-2040-u10-check-chat.tx
PASS  증거 확인:  카드 원문 펼치기  ← evidence/20261021-2040-u10-check-card.tx
PASS  증거 확인:  브리핑 화면  ← evidence/20261021-2028-u10-check-briefin
PASS  증거 확인:  1 ㄴ 인물 목록 — 사용자 격리 2건만·필드 5개·`last_contact_at` nu ← evidence/20261021-2135-verifier-04-mutat
PASS  증거 확인:  2 ㄴ 카드 모양 — facts/patterns 분리·timeline 3·upcoming ← evidence/20261015-1521-u9-be-rows-1-4-pe
PASS  증거 확인:  3 ㄴ 카드 소유 — 남의 것/없는 것 404 동일 본문  ← evidence/20261021-2137-verifier-04-negat
PASS  증거 확인:  4 ㄴ 목록·카드에 원문 없음  ← evidence/20261021-2137-verifier-04-negat
PASS  증거 확인:  5 ㄴ 이벤트 원문 — 바이트 일치/404/404  ← evidence/20261021-2135-verifier-04-mutat
PASS  증거 확인:  6 ㄴ 사실 근거 원문 — 2건·최근 순/404/404  ← evidence/20261021-2135-verifier-04-mutat
PASS  증거 확인:  7 조회는 쓰지 않는다 — trace·`briefed_at`·`updated_at` 변화 ← evidence/20261021-2137-verifier-04-negat
PASS  증거 확인:  8 ㄱ 대기 질문 목록 — 세션 S 1건/헤더 없음 `[]`+쓰기 0/422  ← evidence/20261021-2137-verifier-04-negat
PASS  증거 확인:  9 ㄷ 브리핑 조회 두 경로 — run/scheduler 2건, 내용 = compose  ← evidence/20261015-1522-u9-be-rows-9-10-b
PASS  증거 확인:  10 ㄷ 재실행·사용자 범위·원문·다른 step 혼입  ← evidence/20261021-2135-verifier-04-mutat
PASS  증거 확인:  11 무변경 — `alembic check`·`tools_check` 7/7·`git d ← evidence/20261021-2132-verifier-04-invar
PASS  증거 확인:  12 빌드·타입 — exit 0·dist 3파일  ← evidence/20261021-2131-verifier-04-web-t
PASS  증거 확인:  13 (틀) 화면 3개 — 라우트 키 정확히 3·알 수 없는 해시 → `#/chat`  ← evidence/20261021-2132-verifier-04-invar
PASS  증거 확인:  14 ㄱ 전송·세션  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  15 ㄱ 칩 왕복 — 글자·순서 그대로, `aria-pressed=true` 고정, 나머 ← evidence/20261021-2136-verifier-04-mutat
PASS  증거 확인:  16 ㄱ 복원·새 발화 우선  ← evidence/20261021-2131-verifier-04-web-e
PASS  증거 확인:  17 ㄱ 오류 — 409 두 코드·5xx·P5 규약  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  17b ㄱ 챗봇형 입력·스크롤  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  18 ㄴ 원문 펼치기 — raw 1회만·그대로·접으면 숨김  ← evidence/20261021-2136-verifier-04-mutat
PASS  증거 확인:  19 ㄴ 근거 보기·항목·필터 없음  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  20 ㄷ 브리핑 렌더  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  21 ㄷ 수동 브리핑·잠금 404  ← evidence/20261021-2131-verifier-04-web-e
PASS  증거 확인:  22 ㄷ 알림 → 브리핑 화면 (`sw.test.ts`)  ← evidence/20261021-2136-verifier-04-mutat
PASS  증거 확인:  23 ㄷ 푸시 구독 버튼  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  24 ㄱ E2E 채팅 칩  ← evidence/20261021-2131-verifier-04-web-e
PASS  증거 확인:  25 ㄴ E2E 카드 원문·사이드바 — 1280/390  ← evidence/20261021-2131-verifier-04-web-e
PASS  증거 확인:  26 ㄷ E2E 브리핑  ← evidence/20261021-2131-verifier-04-web-e
PASS  증거 확인:  27 불변식 grep 1~10  ← evidence/20261021-2132-verifier-04-invar
PASS  증거 확인:  27b 실 네트워크 0 (R-5)  ← evidence/20261021-2131-verifier-04-web-v
PASS  증거 확인:  28 전체 회귀·CI  ← evidence/20261021-2132-verifier-04-pytes
PASS  증거 확인:  29 ㄱ 실서버 채팅 확인 칩 — ①~⑤  ← evidence/20261021-2040-u10-check-chat.tx
PASS  증거 확인:  30 ㄴ 카드 원문 펼치기 — ⑥~⑧  ← evidence/20261021-2040-u10-check-card.tx
PASS  증거 확인:  31 ㄷ 브리핑 화면·알림 클릭 — ⑨~⑫  ← evidence/20261021-2029-u10-check-briefin
PASS  증거 확인:  32 화면 점검 20항 — 데스크톱·모바일 폭 각 1회, 밝은·어두운 각 1회, "수정  ← evidence/20261021-2040-u10-check-screens
PASS  registry 에 P8-frontend 행 있음
WARN  미완료 작업 단위 11 개
== 결과: FAIL=0 WARN=2 → evidence/20261021-2145-summary.txt ==
```
2차: **FAIL 0 / WARN 2**(ruff 하네스 4건 — R-U10R-8 · 01-plan 체크박스 11개 — R-U10R-7). 1차의 "04-review.md 없음" WARN 은 사라졌고, 수용 기준 표 35행(backlog 3 + 판정 32)의 증거 열이 전부 실재로 확인됐다. (같은 분에 잘못 만든 빈 증거 `…-verifier-04-verify-impl-post.txt`(명령 `true`)는 verifier 가 바로 지웠다 — 그래서 이름이 `post2` 다.)

### 1-2. verifier 직접 재실행 수치 (보고 수치를 옮기지 않았다 — 전부 `save_evidence.py` 통로, `evidence/`)

| 항목 | 명령 | 내 결과 | 증거 |
|---|---|---|---|
| 백엔드 전체 회귀 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **1953 passed, skip 0**, 1 warning, exit 0 | `evidence/20261021-2132-verifier-04-pytest.txt` (verify-impl 자체 실행분 `evidence/20261021-2131-pytest.txt` 도 1953 passed) |
| 프론트 타입 | `npm --prefix web run typecheck` | exit 0, 오류 0 | `evidence/20261021-2131-verifier-04-web-typecheck.txt` |
| 프론트 Vitest | `npm --prefix web test -- --run` | **9 files · 137 passed (137)**, exit 0 | `evidence/20261021-2131-verifier-04-web-vitest.txt` |
| 프론트 빌드 | `npm --prefix web run build` | exit 0, `web/dist/index.html`·`web/dist/sw.js`·`web/dist/manifest.webmanifest` 생성(21:31) | `evidence/20261021-2131-verifier-04-web-build.txt` |
| E2E | `npm --prefix web run e2e` | **4 passed (4.3s)** — chat 1 · card 데스크톱 1280 1 · card 모바일 390 1 · briefing 1 | `evidence/20261021-2131-verifier-04-web-e2e.txt` |
| 불변식 1~10 + 11행·13행 | 01-plan 356~367행 명령 그대로 | 1·2·3·7·8·9 → 0건(rc=1) · 4 → `PersonCardScreen.tsx` 주석 2·표시 2 + `types.ts` 2(원문 응답 타입·표시 컴포넌트뿐) · 5 → 4 = 4 · 6 → 빈 출력 · 10 → `web/src/components/AppShell.tsx` 1파일 · 13 → 라우트 이름 `chat`·`persons`·`briefings` 3 | `evidence/20261021-2132-verifier-04-invariants.txt` |
| 개발 DB 재조회(SELECT 만) | U10 행(인물 9·10·11, 별칭, 사건 27·28·31·32, 일정 6, 질문 16·17, trace 427·428·432·449·453, 사실 24 근거) | U10 증거 4개의 id·값과 전부 일치(§2 29~31행) | `evidence/20261021-2132-verifier-04-u10-db-recheck.txt` |
| 실서버 부정 케이스 | §3 표 | 404 ×6 · 422 · `[]` · 원문 키 0 ×2 · 조회 전후 DB 변화 0 · 프록시 바이트 동일 | `evidence/20261021-2137-verifier-04-negative-live.txt` |
| 변이(백엔드, 런타임 치환) | §3 표 | 대조 64 passed → BM1 1 failed · BM2 3 failed · BM3 1 failed, 저장소 무수정 | `evidence/20261021-2135-verifier-04-mutation-be.txt` |
| 변이(프론트, 저장소 밖 사본) | §3 표 | 대조 137 passed → FM1 2 failed · FM2 2 failed · FM3 3 failed, 저장소 무수정·사본 원복 diff 0 | `evidence/20261021-2136-verifier-04-mutation-web.txt` |
| CI | `gh run view 39587449611`(HEAD `75cb4ad`) | completed · success — `pytest (3.13)`·`pytest (3.14)`·`windows`·`web (ubuntu-latest)`·`web (windows-latest)` 5 job 전부 success | `evidence/20261021-2144-verifier-04-extra.txt` |

## 2. 수용 기준 대조

증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

### 2-1. backlog 88행 수용 기준 (글자 그대로)

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 채팅 확인 칩 | evidence/20261021-2040-u10-check-chat.txt(29행 서술: 발화 (c) → q16 identity 칩 3개 → 거절 → q17 new_person 칩 6개 → 지인 → 인물 11·사건 32) · evidence/20261021-2033-u10-check-chat-db.txt(q16·q17 `answer`·`answered_at`, trace 449 `identity_rejected=true followup=17`) · evidence/20261021-2132-verifier-04-u10-db-recheck.txt(내 재조회 동일) · evidence/20261021-2136-verifier-04-mutation-web.txt(FM2 `aria-pressed` 고정 → chat.test 2 failed) · evidence/20261021-2131-verifier-04-web-e2e.txt(chat.spec: 칩 → 재개 reply → 새로고침 복원) · 977f2ee · 07ec09a | 통과 — 칩 글자 = `pending_questions.options` 그대로(DB 행과 서술 일치), 누른 칩이 `answer` 로 저장, 재개 중 새 질문(FIX-035 후속)이 새 칩으로 |
| 카드 원문 펼치기 | evidence/20261021-2040-u10-check-card.txt(30행: 인물 9 · 사건 28 `⌄` → `GET /api/events/28/raw` 1회 · 사실 24 근거 2건 28·27) · evidence/20261021-2029-u10-check-card-db.txt(⑦ `raw_utterance`) · evidence/20261021-2137-verifier-04-negative-live.txt([9] API 응답 `raw_utterance` = DB 값 글자 단위 동일, [7][8] 목록·카드에 원문 키 0) · evidence/20261021-2135-verifier-04-mutation-be.txt(BM1 strip → 1 failed, BM2 근거 순서 → 3 failed) · evidence/20261021-2136-verifier-04-mutation-web.txt(FM3 trim → card.test 3 failed) · 761cced · 2c902f0 | 통과 — 원문은 펼칠 때만 두 응답으로, 저장 글자 그대로(결정 F·원칙7) |
| 브리핑 화면 | evidence/20261021-2028-u10-check-briefing-run.txt(`POST /briefings/run` → 일정 6, lines·suggestion, push "sent") · evidence/20261021-2029-u10-check-briefing-db.txt(trace 427 compose · 428 run manual · 구독 2행 호스트만) · evidence/20261021-2040-u10-check-briefing.txt(⑩ 화면 머리줄·사실 줄·제안 = trace, 불일치 0 · 배너 "브리핑 보기" → `#/briefings?schedule_id=6` 강조) · evidence/20261021-2137-verifier-04-negative-live.txt([10] `GET /briefings?schedule_id=6` 응답 = trace 427 글자 그대로, `trace_id:427`) · evidence/20261021-2131-verifier-04-web-e2e.txt(briefing.spec: 맨 위 강조 → 지금 브리핑 → 재조회) · evidence/20261021-2136-verifier-04-mutation-web.txt(FM1 알림 클릭 주소 → sw.test 2 failed) · 46532e7 · 819cb2a | 통과 — 수동·주기 두 경로(판정 9행 자동 + 수동 실서버), 서버 문자열 그대로, 알림 클릭 경로는 22행 자동 + 앱 안 배너 실서버(OS 알림 실클릭만 미확인 → 31행·R-U10R-1) |

### 2-2. 판정 표 1~32행 (01-plan 125~164행)

| 기준 (판정 표 행) | 증거 | 결과 |
|------------------------------|------|------|
| 1 ㄴ 인물 목록 — 사용자 격리 2건만·필드 5개·`last_contact_at` null 뒤 | evidence/20261021-2135-verifier-04-mutation-be.txt(대조군 5파일 64 passed, persons 12 포함) · evidence/20261015-1521-u9-be-rows-1-4-persons.txt · evidence/20261011-verifier-u1-recheck-mutation.txt(`func.max→min` 4 failed, R-U1-1 해소) · evidence/20261021-2137-verifier-04-negative-live.txt([3c] 남의 인물 404) · 6c2d0e7 | 통과 |
| 2 ㄴ 카드 모양 — facts/patterns 분리·timeline 3·upcoming 1·`last_contact_at` 최신 | evidence/20261015-1521-u9-be-rows-1-4-persons.txt · evidence/20261011-verifier-u1-recheck-mutation.txt · tests/test_api_read_persons.py · 6c2d0e7 | 통과 |
| 3 ㄴ 카드 소유 — 남의 것/없는 것 404 동일 본문 | evidence/20261021-2137-verifier-04-negative-live.txt([1] 999999 · [3c] 인물 5(brief-u5-check) → `{"detail":{"code":"not_found"}}` 404) · evidence/20261015-1521-u9-be-rows-1-4-persons.txt | 통과 |
| 4 ㄴ 목록·카드에 원문 없음 | evidence/20261021-2137-verifier-04-negative-live.txt([7] `GET /persons` 0 · [8] `GET /persons/9` 0) · evidence/20261015-1521-u9-be-rows-1-4-persons.txt | 통과 |
| 5 ㄴ 이벤트 원문 — 바이트 일치/404/404 | evidence/20261021-2135-verifier-04-mutation-be.txt(BM1 `strip()` → `test_이벤트_원문_응답_전체_값` 1 failed: `TRICKY_RAW` 앞뒤 공백 검출) · evidence/20261021-2137-verifier-04-negative-live.txt([2] 404 · [9] 사건 28 동일) · evidence/20261015-1522-u9-be-rows-5-6-raw.txt · 2c902f0 | 통과 |
| 6 ㄴ 사실 근거 원문 — 2건·최근 순/404/404 | evidence/20261021-2135-verifier-04-mutation-be.txt(BM2 순서 반전 → 3 failed: 내림차순·동률 id·상한) · evidence/20261021-2137-verifier-04-negative-live.txt([3] [3b] 404) · evidence/20261011-1529-verifier-u2-mutation.txt · 2c902f0 | 통과 |
| 7 조회는 쓰지 않는다 — trace·`briefed_at`·`updated_at` 변화 0 | evidence/20261021-2137-verifier-04-negative-live.txt(before/after `459\|17\|11\|32\|max_updated_at\|max_briefed_at` 동일 — 실서버 GET 12회 뒤) · evidence/20261015-1522-u9-be-row-7-write-zero.txt · evidence/20261015-1523-u9-be-mutation.txt(M4a~M4e 쓰기 주입 5종 검출) · tests/helpers_read_api.py | 통과 |
| 8 ㄱ 대기 질문 목록 — 세션 S 1건/헤더 없음 `[]`+쓰기 0/422 | evidence/20261021-2137-verifier-04-negative-live.txt([5] `bad session!` → 422 `invalid_session_id` · [6] 헤더 없음 → `[]` 200, 전후 `pending_questions` 17 그대로) · evidence/20261015-1522-u9-be-row-8-pending.txt · evidence/20261012-1733-verifier-u3-mutation.txt · 95ca2c0 | 통과 |
| 9 ㄷ 브리핑 조회 두 경로 — run/scheduler 2건, 내용 = compose output | evidence/20261015-1522-u9-be-rows-9-10-briefings.txt · tests/test_api_read_briefings_e2e.py · evidence/20261021-2137-verifier-04-negative-live.txt([10] 실서버 run 경로 = trace 427) · 0b24bb6 | 통과 |
| 10 ㄷ 재실행·사용자 범위·원문·다른 step 혼입 | evidence/20261021-2135-verifier-04-mutation-be.txt(BM3 기간 6일 → `test_기간_경계_…` 1 failed) · evidence/20261015-1627-verifier-u9b-mutation.txt · evidence/20261015-1927-u9b-rework1-v2-mutation.txt(R-U9b-1 조작 trace V2 검출) · evidence/20261021-2137-verifier-04-negative-live.txt([4] 999999 → 404) | 통과 |
| 11 무변경 — `alembic check`·`tools_check` 7/7·`git diff --stat 50fd7fc -- app alembic ':!routes.py' ':!schemas.py' ':!read.py'` 빈 출력 | evidence/20261021-2132-verifier-04-invariants.txt([11] 지금은 5파일 `app/agent/loop.py`·`app/er/__init__.py`·`app/er/pipeline.py`·`app/er/types.py`·`app/tools/context.py`) · evidence/20261021-2144-verifier-04-extra.txt(`50fd7fc..735f391^` 빈 출력 · `735f391..HEAD` 빈 출력 · `alembic check` · `tools_check`) · evidence/20261015-1522-u9-be-row-11-nochange.txt(U9b 시점 빈 출력) · 735f391 · docs/wiki/fixes/review-FIX-035.md | 통과 — 5파일 전부 FIX-035 커밋 `735f391` 한 건의 변경이고 그 FIX 는 FIX 게이트(`review-FIX-035.md` 통과, 1953 passed, 변이 12/12)를 거쳤다. P8 단위 커밋(U1~U10)의 `app/` 변경은 계획대로 세 파일뿐(R-U10R-10 기록) |
| 12 빌드·타입 — exit 0·dist 3파일 | evidence/20261021-2131-verifier-04-web-typecheck.txt · evidence/20261021-2131-verifier-04-web-build.txt · web/dist/index.html · web/dist/sw.js · web/dist/manifest.webmanifest | 통과 |
| 13 (틀) 화면 3개 — 라우트 키 정확히 3·알 수 없는 해시 → `#/chat` | evidence/20261021-2132-verifier-04-invariants.txt([13] `routes.ts` 이름 3·`HREF` 3·`DEFAULT_HASH = HREF.chat` · [10] 라우트 밖 패널 `AppShell.tsx` 1파일) · evidence/20261021-2131-verifier-04-web-vitest.txt(routes.test 포함 137) · 975a8e5 | 통과 |
| 14 ㄱ 전송·세션 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261013-1354-verifier-u5-mutation.txt · evidence/20261021-2131-verifier-04-web-e2e.txt(chat.spec `X-Session-Id`) · 977f2ee | 통과 |
| 15 ㄱ 칩 왕복 — 글자·순서 그대로, `aria-pressed=true` 고정, 나머지 비활성 | evidence/20261021-2136-verifier-04-mutation-web.txt(FM2 → `칩을 누르면 POST /api/answers/{id} … 선택 고정·나머지 비활성`·`답 응답의 reply 가 이어 붙고 …` 2 failed) · evidence/20261013-1354-verifier-u5-mutation.txt · evidence/20261021-2040-u10-check-chat.txt(⑤ 실서버 선택 상태) | 통과 |
| 16 ㄱ 복원·새 발화 우선 | evidence/20261021-2131-verifier-04-web-e2e.txt(chat.spec 새로고침 복원) · evidence/20261013-1354-verifier-u5-mutation.txt · evidence/20261016-1915-u10-check-chat-fix035.txt(A4 F5 복원 실서버) | 통과 |
| 17 ㄱ 오류 — 409 두 코드·5xx·P5 규약 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261013-1354-verifier-u5-mutation.txt · evidence/20261016-1915-u10-check-chat-fix035.txt(A3 동시 답 → 409 실서버) | 통과 |
| 17b ㄱ 챗봇형 입력·스크롤 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261021-2040-u10-check-screens.txt(12항 3줄 입력·Enter/Shift+Enter, 14항 타이핑 점) · evidence/20261013-1354-verifier-u5-mutation.txt | 통과 — "새 메시지" 표시는 자동 테스트로만(32행 15항 부분) |
| 18 ㄴ 원문 펼치기 — raw 1회만·그대로·접으면 숨김 | evidence/20261021-2136-verifier-04-mutation-web.txt(FM3 → `첫 펼침에 GET /events/{id}/raw 1회, 원문은 글자 그대로 …` 등 3 failed) · evidence/20261013-1847-verifier-u6-mutation.txt · evidence/20261021-2040-u10-check-card.txt(실서버 1회·재요청 0) · 761cced | 통과 |
| 19 ㄴ 근거 보기·항목·필터 없음 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261013-1847-verifier-u6-mutation.txt · evidence/20261021-2040-u10-check-card.txt(사실 24 근거 2건) · web/src/components/PersonList.tsx(필터·검색 코드 0 — §3) | 통과 |
| 20 ㄷ 브리핑 렌더 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261014-1946-verifier-u7-mutation.txt · evidence/20261021-2040-u10-check-briefing.txt(⑩ 문자열 그대로) · 46532e7 | 통과 |
| 21 ㄷ 수동 브리핑·잠금 404 | evidence/20261021-2131-verifier-04-web-e2e.txt(briefing.spec) · evidence/20261014-1946-verifier-u7-mutation.txt · evidence/20261021-2137-verifier-04-negative-live.txt([4] 404 본문) | 통과 |
| 22 ㄷ 알림 → 브리핑 화면 (`sw.test.ts`) | evidence/20261021-2136-verifier-04-mutation-web.txt(FM1 `targetHashFor` → `/#/chat` 로 바꾸면 `notificationclick … openWindow("/#/briefings?schedule_id=N")` 2 failed — 테스트가 주소를 값으로 고정) · evidence/20261014-2024-verifier-u8-mutation.txt · evidence/20261015-1444-verifier-u9a-rework-x16-recheck.txt · 819cb2a | 통과(자동) — 실 OS 알림 클릭은 31행 ⑫ |
| 23 ㄷ 푸시 구독 버튼 | evidence/20261021-2131-verifier-04-web-vitest.txt · evidence/20261014-2024-verifier-u8-mutation.txt · evidence/20261021-2029-u10-check-briefing-db.txt(구독 1·3, 호스트만) · evidence/20261021-2040-u10-check-briefing.txt("알림 켜짐" 상태) | 통과 |
| 24 ㄱ E2E 채팅 칩 | evidence/20261021-2131-verifier-04-web-e2e.txt(`e2e/chat.spec.ts:8` passed) · evidence/20261015-1443-verifier-u9a-rework-v2-mutation.txt · 07ec09a | 통과 |
| 25 ㄴ E2E 카드 원문·사이드바 — 1280/390 | evidence/20261021-2131-verifier-04-web-e2e.txt(`card.spec.ts:43` 데스크톱 · `:85` 모바일 390 passed) · evidence/20261015-1443-verifier-u9a-rework-v2-mutation.txt(V2 원문 줄바꿈 E2E 검출) | 통과 |
| 26 ㄷ E2E 브리핑 | evidence/20261021-2131-verifier-04-web-e2e.txt(`briefing.spec.ts:20` passed) | 통과 |
| 27 불변식 grep 1~10 | evidence/20261021-2132-verifier-04-invariants.txt(내 재실행 — 1·2·3·7·8·9 0건, 4 제품 코드 4곳+타입 2, 5 4=4, 6 빈, 10 `AppShell.tsx` 1파일) · evidence/20261015-1428-verifier-u9a-invariants.txt | 통과 |
| 27b 실 네트워크 0 (R-5) | evidence/20261021-2131-verifier-04-web-vitest.txt(network.test 2 포함) · evidence/20261015-1444-verifier-u9a-rework-x16-recheck.txt(표 밖 `/api/` 요청 → 4 failed) · web/e2e/fixtures.ts | 통과 |
| 28 전체 회귀·CI | evidence/20261021-2132-verifier-04-pytest.txt(1953 passed skip 0 ≥ 1882+신규) · evidence/20261021-2131-verifier-04-web-vitest.txt(137) · evidence/20261021-2131-verifier-04-web-e2e.txt(4) · evidence/20261021-2144-verifier-04-extra.txt(CI 39587449611 5 job success, HEAD 75cb4ad) · 75cb4ad | 통과 |
| 29 ㄱ 실서버 채팅 확인 칩 — ①~⑤ | evidence/20261021-2040-u10-check-chat.txt(① 기동 명령·주소, 키 값 없음 ② 발화 3건 ③ q16 id·kind·options ④ 칩 뒤 `answer`·`answered_at` ⑤ 메인 세션 확인 문장 + Chrome 156.0.0.0) · evidence/20261021-2033-u10-check-chat-db.txt · evidence/20261021-2132-verifier-04-u10-db-recheck.txt(q16 `아니요, 다른 사람이에요` 11:33:05 · q17 `지인으로 기억할게요` 11:33:18 · 인물 11 · 사건 32 · trace 449 — 서술과 동일) | 통과(조건부) — ①~④ 는 내가 DB 로 재확인. ⑤ "사용자 확인 문장" 은 사용자 지시(2026-10-21 "너가 직접 해줘", 03-log U10 항목·증거 머리글)로 메인 세션 문장이 대신함 — 판정 근거는 §6 R-U10R-1 앞 단락 |
| 30 ㄴ 카드 원문 펼치기 — ⑥~⑧ | evidence/20261021-2040-u10-check-card.txt(⑥ 인물 9·사건 28·사실 24 ⑦ raw ⑧ 메인 세션 문장) · evidence/20261021-2029-u10-check-card-db.txt · evidence/20261021-2137-verifier-04-negative-live.txt([9] API = DB 동일) · evidence/20261021-2132-verifier-04-u10-db-recheck.txt(사실 24 → 27·28) | 통과(조건부) — ⑥⑦ 재확인(R-U10C-5 의 "펼친 사실 id" 공백은 이번 증거로 닫힘). ⑧ 은 29행 ⑤ 와 같은 대체 |
| 31 ㄷ 브리핑 화면·알림 클릭 — ⑨~⑫ | evidence/20261021-2029-u10-check-briefing-db.txt(⑨ trace 427 ⑪ 구독 1·3 호스트 `https://fcm.googleapis.com`, push "sent") · evidence/20261021-2028-u10-check-briefing-run.txt · evidence/20261021-2040-u10-check-briefing.txt(⑩ 대조 불일치 0, 앱 안 배너 수신 · ⑫ **미확인** 명시) · evidence/20261021-2137-verifier-04-negative-live.txt([10]) · evidence/20261021-2136-verifier-04-mutation-web.txt(FM1) | **통과(조건부 — ⑫ 미충족)** — ⑨⑩⑪ 은 내가 API·DB 로 재확인. ⑫ OS 알림 클릭 → 그 일정 열림은 **아무도 하지 않았다**(확장이 OS 알림을 누를 수 없음). 자동 22행(가짜 self, FM1 로 계약 고정 확인) + 앱 안 배너 경로 실서버 + P7 U8 실클릭(다른 워커 `app/push/devpage/sw.js`)만 있다. 판정은 [권고] R-U10R-1 + 사용자 확인 조건 — 근거 §6 |
| 32 화면 점검 20항 — 데스크톱·모바일 폭 각 1회, 밝은·어두운 각 1회, "수정 반영 횟수: n ≤ 1" | evidence/20261021-2040-u10-check-screens.txt(20항 표: 통과 17 · 부분 3(7·12·15) · 수정 필요 0 · 머리글 **"수정 반영 횟수: 1"**(2026-10-16 정렬 `3bd5025`) · 데스크톱 1710×862 dark · 모바일 500×667 dark · **밝은 모드 미확인**) · evidence/20261016-1942-verifier-u10-closeout-mutation.txt(정렬 수정 변이 M1~M3 검출·M4 생존) · 3bd5025 · docs/wiki/changes/CR-003.md | **통과(조건부)** — n = 1 ≤ 1 확인(에이전트 작업 2회를 CR-003 ⑥(a) 사용자 결정으로 1회로 본 경위는 03-log 정렬 항목·`review-u10-closeout.md` §0). 미충족 2: 밝은 모드 1회(R-U10R-2) · 모바일 폭 390(500 으로 대신, E2E 390 이 10항·19항을 덮음, R-U10R-3). "사용자 한 줄 의견" 은 메인 세션 의견 |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

실서버(떠 있는 :8000·:5173, 개발 DB `relationship`)에는 **읽기 요청만** 보냈다. 변이는 저장소 파일을 고치지 않았다(백엔드: 스크래치패드 플러그인 `PYTHONPATH=… -p mutplug` 런타임 치환 · 프론트: 스크래치패드 사본 + `node_modules` 심링크). 각 증거 끝에 `git status --short` 빈 출력.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 없는 인물·남의 인물 카드 → 404 `not_found` 같은 본문 | `curl /persons/999999` · `curl /persons/5`(소유 `brief-u5-check`) | evidence/20261021-2137-verifier-04-negative-live.txt [1][3c] |
| 없는 이벤트 원문 → 404 | `curl /events/999999/raw` | 같은 파일 [2] |
| 없는 사실 · 남의 인물 경로에 내 사실 끼움 → 404 | `curl /persons/9/facts/999999/sources` · `curl /persons/5/facts/24/sources` | 같은 파일 [3][3b] |
| 없는 일정 지정 브리핑 → 404 | `curl "/briefings?schedule_id=999999"` | 같은 파일 [4] |
| `X-Session-Id` 형식 위반 → 422 `invalid_session_id` / 헤더 없음 → `[]` + 저장 0 | `curl -H "X-Session-Id: bad session!" /questions/pending` · 헤더 없이 | 같은 파일 [5][6] + before/after `pending_questions` 17 = 17 |
| 목록·카드 응답에 원문 키 없음(결정 F) | `curl /persons` · `/persons/9` → `grep -c raw_utterance` 0 | 같은 파일 [7][8] |
| 조회 12회 뒤 DB 쓰기 0(판정 7행 실서버) | `agent_traces`·`pending_questions`·`persons`·`events` 수 · `max(updated_at)` · `max(briefed_at)` before = after | 같은 파일 [before][after] `459\|17\|11\|32\|…` 동일 |
| 개발 프록시가 응답을 바꾸지 않음 | `curl :5173/api/persons` vs `curl :8000/persons` → `cmp` 동일 | 같은 파일 [12] `proxy_same_bytes=yes` |
| 쓰기 라우트 추가 없음(불변식 5) · 개발 페이지 무변경(6) · 비밀 없음(7) · 산출물 미커밋(8) · 외부 글꼴/CDN 없음(9) | 01-plan 356~367행 명령 그대로 | evidence/20261021-2132-verifier-04-invariants.txt [5] 4=4 · [6] 빈 · [7][8][9] 0건 |
| 제품 화면에서 `/push-dev/` 링크 없음(P7 결정 A, 불변식 1) · 음성 API 없음(원칙7, 2) · sw 캐시/fetch 없음(결정 I·M, 3) | 같은 명령 | 같은 파일 [1][2][3] 0건(rc=1) |
| 라우트 밖 패널은 서랍 1개(원칙5, 불변식 10) · 라우트 3개(13행) | `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v ui/` · `routes.ts` | 같은 파일 [10] `AppShell.tsx` 1파일 · [13] 3 |
| 인물 목록에 태그 필터·검색 컨트롤 없음(기획서 2장 제외 · D15 는 P8b) | `grep -n "slice\|<input\|filter\|search" web/src/components/PersonList.tsx web/src/components/AppShell.tsx` → 0건(이 세션 직접 실행; 사이드바가 보인 "5명" 은 사용자 `local` 의 인물이 정확히 5명이기 때문 — evidence/20261021-2132-verifier-04-u10-db-recheck.txt 인물 7~11) | web/src/components/PersonList.tsx |
| `app/` 변경이 FIX-035 밖에 없음(계획 범위 — 11행) | `git diff --stat 50fd7fc 735f391^ -- app alembic ':!…3파일'` 빈 · `git diff --stat 735f391 -- …` 빈 · `git status --porcelain app alembic` 빈(N-3) | evidence/20261021-2144-verifier-04-extra.txt · evidence/20261021-2135-verifier-04-mutation-be.txt 끝 |
| FIX 게이트가 `web/` 를 실제로 판정(U0, N-1 묶음) | `fix_guard_check.py` 180행 `startswith("web/")` + test-guards 케이스 6·7(`web/x.ts` 거부/허용) + 변이(조건 제거 → 판정 뒤집힘) | docs/wiki/packages/P8-frontend/review-u0-harness.md §2·§3 · evidence/20261011-1241-verifier-u0-mutation.txt |
| 가짜 표 밖 요청은 실패(27b) | X16 재실행(표 밖 `/api/` 요청) 4 failed · network.test 2 | evidence/20261015-1444-verifier-u9a-rework-x16-recheck.txt |

### 3-1. 변이 시험 — 단위마다 최소 1개 (단위 리뷰의 verifier 변이 인용 + 이번에 내가 새로 돌린 6개)

| 단위 | 단위 리뷰에서 verifier 가 돌린 변이(인용) | 이번 04-review 에서 새로 돌린 변이 → 결과 |
|---|---|---|
| U0 하네스 | `web/` 조건 제거 → test-guards 케이스 6 판정 뒤집힘 — `review-u0-harness.md` §3, evidence/20261011-1241-verifier-u0-mutation.txt | — |
| U1 인물 조회 | V1~V7(`func.max→min` 4 failed 등) — evidence/20261011-verifier-u1-recheck-mutation.txt | (U9b 대조군에 포함) |
| U2 원문 조회 | M1~M8 전부 검출 — evidence/20261011-1529-verifier-u2-mutation.txt | **BM1** `routes.get_event_raw` 응답 `raw_utterance.strip()` → `test_이벤트_원문_응답_전체_값` **1 failed** · **BM2** `routes.get_fact_sources` `sources` 역순 → 내림차순·동률 id·상한 **3 failed** — evidence/20261021-2135-verifier-04-mutation-be.txt |
| U3 대기 질문·브리핑 조회 | V1~V8(계약 변이 6/6 검출, 2 동치) — evidence/20261012-1733-verifier-u3-mutation.txt | **BM3** `read.BRIEFINGS_LOOKBACK_DAYS` 7→6 → `test_기간_경계_정확히_7일전_포함_7일_1초전_제외_미래_포함` **1 failed**(`assert 6 == 7`) — 같은 파일 |
| U4 골격 | V1~V5 + 재검증 M3·M7·V4 — evidence/20261012-2040-verifier-u4-mutation-1.txt · evidence/20261012-2336-verifier-u4-recheck-mutation.txt | — |
| U5 채팅 | V1~V5(V1 공백 → R-U5-1 → U6 에서 M9 검출) — evidence/20261013-1354-verifier-u5-mutation.txt | **FM2** `ChatScreen.tsx` 칩 `aria-pressed={false}` 고정 → chat.test `칩을 누르면 … 선택 고정·나머지 비활성`·`답 응답의 reply …` **2 failed** — evidence/20261021-2136-verifier-04-mutation-web.txt |
| U6 카드 | V2~V5 + 탐침 P1~P3 — evidence/20261013-1847-verifier-u6-mutation.txt | **FM3** `PersonCardScreen.tsx` 타임라인 원문 `.trim()` → card.test 원문 펼치기 **3 failed**(`RAW_A` 앞뒤 공백·줄바꿈 검출) — 같은 파일 |
| U7 브리핑 | V1~V5(V3·V4 틈 → R-U7-2 → U8 M24~M26 검출) — evidence/20261014-1946-verifier-u7-mutation.txt | — |
| U8 PWA·푸시 | V1~V5(V4 틈 → R-U8-1 → U9a 검출) — evidence/20261014-2024-verifier-u8-mutation.txt | **FM1** `sw.js` `targetHashFor` 가 `/#/chat` 반환 → sw.test `notificationclick … openWindow("/#/briefings?schedule_id=N")` **2 failed** — 같은 파일 |
| U9a E2E | V1~V5c(V2 → R-U9a-1 → 재작업 후 E2E 검출) — evidence/20261015-1443-verifier-u9a-rework-v2-mutation.txt | — |
| U9b 백엔드 판정 | V1~V3(V2 생존 → R-U9b-1 → 재작업 검출) — evidence/20261015-1627-verifier-u9b-mutation.txt · evidence/20261015-1927-u9b-rework1-v2-mutation.txt | BM1~BM3 는 U9b 가 손본 5파일 대조군(64 passed) 위에서 돌렸다 |
| FIX-035 | M1~M12 전부 검출(M8 재작업 후) — docs/wiki/fixes/review-FIX-035.md §2·재확인 | — (전체 회귀 1953 에 포함) |
| 정렬 수정(U10) | M1~M3 검출 · **M4 생존**(R-U10C-3 → P8b) — evidence/20261016-1942-verifier-u10-closeout-mutation.txt | — |

대조군: 백엔드 5파일 `64 passed` · 프론트 `137 passed`. 새 변이 6종 **전부 검출**, 통과한 변이 0. 저장소 무수정: 두 증거 파일 끝 `git status --short` 빈 출력(`status_rc=0`), 프론트 사본 원복 뒤 `diff -rq web/src <사본>/src`·`sw.js` 차이 0(`diff_rc=0`).

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)

- 이 패키지가 닫는 R: **없음** — `docs/wiki/INDEX.md` 76행 패키지 표 "닫는 R —", 01-plan 4행 "닫는 검증: 없음". `review-index.md` 는 바꾸지 않았다.
- 기대는 R(읽기만): **R8**(시맨틱→원문 링크) — `review-index.md` 16행 "구현완료(4dfaf33, 09c2bd1 … P6-memory …)" 그대로. 이 패키지는 `fact_sources` 를 **읽는 쪽**(`GET /persons/{id}/facts/{fact_id}/sources`, 카드 "근거 보기")을 만들었고 U10 에서 사실 24 → 사건 27·28 로 실제 링크를 화면에서 확인했다(§2 30행). **R12**(브리핑 트리거·푸시 구독 저장소) — 20행 "구현완료(P6-briefing … P7-push …)" 그대로. 이 패키지는 그 위의 화면(`GET /briefings`, "지금 브리핑", "알림 받기")만 더했고, U10 에서 제품 화면 구독(id 3)으로 `push "sent"` 수신을 확인했다(§2 31행 ⑪). 상태 변경 없음 — 맞다.

## 5. registry.md 에 올린 산출물

- `grep -c "| P8-frontend |" docs/wiki/registry.md` → **42행**(220~261행). 경로 열의 토큰 46개를 전부 `[ -e ]` 로 대조 — **전부 실재**(이 세션 직접 실행; `.github/workflows/tests.yml` · `app/api/{read,routes,schemas}.py` · `tests/{helpers_read_api,test_api_read_persons,test_api_read_raw,test_api_questions_pending,test_api_read_briefings,test_api_read_briefings_e2e}.py` · `web/` 아래 29개 · `docs/RUNNING.md` · `docs/reliability.md` · `docs/wiki/packages/P8-frontend/tests.md`).
- 단위 ↔ 해시: U1 `6c2d0e7` · U2 `2c902f0` · U3 `95ca2c0` · U4 `975a8e5` · U5 `977f2ee` · U6 `761cced` · U7 `46532e7` · U8 `819cb2a` · U9a `07ec09a` · FIX-035 `735f391` · 정렬 `3bd5025` — 전부 `evidence/20261021-2131-commits.txt`(태그 커밋 22건)에 있다. 03-log 항목의 해시 칸과도 일치(U0 는 `440a0e5`, 03-log 14행 "pending" 은 그 뒤 기록에서 채워짐).
- **해시 `pending` 잔존 2행**: 259행(`tests/test_api_read_briefings_e2e.py`, U9b)·260행(`docs/reliability.md`, U9b) — U9b 커밋 `0b24bb6` 으로 채워야 한다(R-U10R-9, 문서).
- 03-log 의 CR-003 항목(216행)·U10 항목(224행) 해시 `pending` — CR-003 은 `75cb4ad` 로 커밋됐고(222행 "커밋 뒤" 줄에 기록됨), U10 항목은 이 04-review 와 한 묶음으로 커밋될 것(메인 세션 몫).

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

`05-remediation.md`: 열림 0(필수 0) / 해소 1(`F-ce7d18`, 계획 단계). 이번 `verify-impl` FAIL 0 → 새 소견 없음. 아래는 이 검토의 소견이다. **[필수] 0 · [권고] 10.**

**미확인 2건을 [필수] 로 보지 않는 근거(판정 표 29~32행 "조건부 통과")**
1. 수용 기준(backlog 88행 세 구절)의 **증거는 전부 있다** — 각 구절이 자동 테스트(판정 1~28행, 내가 재실행·변이로 공허하지 않음을 확인)와 실서버 DB·API 원본(내가 SELECT·curl 로 재확인)으로 닫혔다. 미확인 2건은 **같은 동작을 사람 눈으로 한 번 더 보는 층**(29~32행)의 일부이지, 증거가 없는 기준이 아니다. 원칙 1~9·"하지 않는 것"·D/S 카드 위반과 무관하다.
2. 01-plan 31행 끝 문장이 스스로 "알림 클릭은 22행 자동 테스트로만 닫혔다는 한계를 04-review 에 적는다" 는 닫는 방식을 정해 두었다(VAPID 미설정 경우를 위한 문장이지만, 계획 작성자가 "실클릭 없이 자동 테스트 + 한계 기록" 을 통과 형식으로 인정했다는 뜻이다). 이번에는 VAPID 가 설정돼 ⑪ 까지 실서버로 확인됐고 빠진 것은 ⑫ 하나다.
3. "사용자 확인 문장" → "메인 세션 확인 문장" 대체는 사용자 지시("너가 직접 해줘", 2026-10-21)로 사용자가 절차의 자기 역할을 메인 세션에 넘긴 것이고, 증거 머리글·03-log 에 그 사실이 숨김 없이 적혀 있다. 메인 세션이 적은 객관 항목(id·시각·문자열)은 내가 전부 DB·API 로 대조해 어긋남 0 이었다(§2). 주관 항목(무엇이 보였나)은 대체된 주체의 문장이라는 한계를 29·30·32행에 그대로 적었다.
4. 그래서 [권고] + **사용자 확인 조건**으로 둔다. 조건은 사용자가 1~2분이면 닫을 수 있고(아래 R-U10R-1·2), `승인:` 줄에서 사용자가 조건을 수행했는지·면제하는지를 적으면 된다. 반대로 [필수] 로 두면 에이전트가 할 수 없는 일 때문에 패키지가 영구 보류가 된다 — 그것은 L-004(사용자가 단계를 정한다)의 취지와도 어긋난다.

**[권고] (사용자 확인 조건 2 + 인계·문서 8)**
- **R-U10R-1 — 31행 ⑫ OS 알림 클릭 → 그 일정 열림, 실브라우저 미확인.** 근거: `evidence/20261021-2040-u10-check-briefing.txt` ⑫ "미확인(에이전트 한계)"; P8 의 `web/public/sw.js` 54~72행 `notificationclick`(앱 창 고르기 → `focus` + `postMessage({type:"open-briefing"})` / 없으면 `openWindow("/#/briefings?schedule_id=N")`)은 가짜 `self` 로만 실행됐다(sw.test, FM1 로 계약 고정 확인). P7 U8 의 실클릭(2026-10-10)은 다른 워커(`app/push/devpage/sw.js`)다. 조건(사용자, 1분): 브리핑 화면 일정 6 카드의 "지금 브리핑" → OS 알림 클릭 → 주소가 `#/briefings?schedule_id=6` 이고 그 카드가 강조되는지 → `승인:` 줄에 한 줄. 안 되면 FIX(P8 범위, `web/public/sw.js`).
- **R-U10R-2 — 32행 밝은 모드 1회 미확인.** 근거: 같은 screens 증거 머리글 "밝은 모드는 미확인". 보완 사실: `web/src/styles/tokens.css` 70행 `:root`(밝은 팔레트 기본) · 108행 `@media (prefers-color-scheme: dark)`; Playwright E2E 4건은 `colorScheme` 미지정 = 기본 light 로 세 화면을 렌더링해 통과했다(`web/playwright.config.ts` 에 `colorScheme` 없음) — 밝은 모드에서 깨지지 않는다는 자동 근거는 있다. 조건(사용자, 1분): OS 를 밝게 바꿔 세 화면을 한 번 보고 체크리스트 8항 반대 경우(밝을 때 글자 대비)를 `승인:` 줄에 한 줄.
- **R-U10R-3 — 모바일 폭 390 은 500 으로 대신(Chrome 창 최소 폭).** E2E `card.spec.ts:83` 390×844 가 10항(가로 스크롤 — 서랍·탭바 없음)을 덮는다. 기록만. 실기기 소프트 키보드(12항)·"새 메시지" 표시(15항)·로딩/오류 안내(7항)는 자동 테스트로만 — 사용자가 원하면 P8b 32행 재점검 때 같이.
- **R-U10R-4 — [FIX/CR 후보, P8 범위 밖, 원칙1] 일반 호칭 별칭의 단독 언급이 자동 병합된다.** 근거: `evidence/20261021-2132-verifier-04-u10-db-recheck.txt` — 인물 9 별칭 `과장님`(id 11, `user_said`) · 인물 10 `박선영 과장님`·`선영 과장님`; trace 432 `s_llm 0.9·s_emb 1.0·s_rule 1.0 → 0.95 merge`(LLM reason "'과장님'이라는 별명이 박선우 과장님과 정확히 일치"). 설계대로(확정 별칭 정확 일치)지만 같은 사용자에 `과장님` 이 둘 이상이면 2단계 규칙(D13)이 감점할 재료가 없다. 같은 DB 에 인물 7 `민수` 의 별칭 `박지훈 과장님`(id 7, P8 이전 세션의 것)도 있어 호칭 별칭이 이미 섞여 있다. 처리: ER 쪽 CR/FIX(S3.3 — 호칭만인 별칭은 `s_rule` 감점 또는 저장 시 확인) — P10 평가 데이터에 "호칭 단독 언급" 케이스를 넣어 측정부터(§7).
- **R-U10R-5 — [UI/UX 후보] 저장된 브리핑이 0 이면 화면에 "지금 브리핑" 버튼이 없어 첫 브리핑은 API/주기 작업으로만 만들 수 있다.** 근거: `web/src/screens/BriefingScreen.tsx` 138행(버튼은 카드 안) · 262행(빈 상태 문구만); `evidence/20261021-2040-u10-check-briefing.txt` "첫 브리핑은 RUNNING.md 220행 수동 경로로". 01-plan 해석 ㄷ "그 일정의 수동 브리핑을 **다시** 돌릴 수 있다" 와 결정 H 대로라 결함은 아니다. 데모(기획서 8장 "발표자 수동 트리거 버튼")에서 첫 브리핑을 화면에서 만들고 싶으면 P8c/FIX(빈 상태에 "다가오는 일정 브리핑 만들기" 한 버튼 = `POST /briefings/run` 본문 없음, 새 화면·라우트 없음).
- **R-U10R-6 — 열어 둔 브리핑 화면은 자동 갱신되지 않는다(결정 I 캐시 없음·주기 조회 없음).** 기록만. 알림 배너 "브리핑 보기" 가 재조회 경로다(실서버 확인).
- **R-U10R-7 — 01-plan 87~101행 U0~U10 체크박스 11개가 `- [ ]` 그대로(verify-impl WARN "미완료 작업 단위 11 개").** P6-memory·P4b 선례대로 승인 뒤 메인 세션이 `- [x]` 로 닫고 2차 verify-impl 에서 WARN 이 사라지는지 본다.
- **R-U10R-8 — ruff WARN 4건은 전부 하네스(`.claude/scripts/`), 제품 코드 0.** P7-push 04-review 와 같이 이관(FIX 후보 `findings.py` DTZ005·F541, `bash_write_check.py` B007).
- **R-U10R-9 — registry 259·260행 해시 `pending` → `0b24bb6`.** 문서만.
- **R-U10R-10 — 판정 표 11행의 명령은 FIX-035 뒤로는 글자 그대로 "빈 출력" 이 될 수 없다.** 5파일은 전부 `735f391` 한 커밋이고 FIX 게이트를 거쳤다(§2 11행). 다음 패키지 계획이 "무변경 diff" 를 쓸 때는 기준 해시를 **마지막 FIX 커밋 뒤**로 두거나 FIX 커밋을 제외하는 식(`git diff --stat <fix>..HEAD`)으로 적도록 — architect 메모(L 후보 아님, 계획 문구 습관).

**단위 리뷰에서 넘어온 [권고] 상태**: R-U10C-3(M4 생존) → backlog P8b 수용 기준에 "목록 폭 단언 보강" 으로 들어가 있음(열림, P8b) · R-U10C-4 → D15 "상한 없음" 명시로 닫힘 · R-U10C-5(29·30행 사용자 확인·펼친 사실 id) → 이번 U10 증거로 ⑥ 사실 24 는 닫힘, ⑤⑧ 은 위 대체 판정 · R-U10C-6 → `changes/CR-003.md` 3행 동결 창 사유 기록으로 닫힘 · R-U10C-7 → 루트 `.gitignore` 59행 `test-results/` 로 닫힘(`git check-ignore` 확인) · R-U10C-8 포함됨 · R-U10C-9 닫힘 · R-U10C-10 기록. **R-U10D-1~4([필수], 배포 유효성)** → `docs/backlog.md` 93행 P9 수용 기준에 글자 그대로 들어가 있음(이 패키지의 열린 [필수] 아님 — P9 착수 조건). R-U10D-5~10 → 같은 행 ④.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

**P8b-persons-grid (frontend-agent, `web/` 만, 백엔드 diff 0 — D15)**
- D15 "코드에서 지켜야 할 것" 6줄 그대로가 수용 기준(backlog 89행). 지금 코드 상태: `getPersons()` 인자 없음(`client.ts:107`), `PersonList.tsx`·`AppShell.tsx` 에 `slice`·`<input>`·filter 0(§3) — 사이드바는 전원 목록이다(사용자 `local` 이 5명이라 화면엔 5명으로 보였을 뿐).
- R-U10C-3: `card.test.tsx` 목록 폭 단언을 `[data-screen="persons"]` 조상·자손 전부(또는 E2E `boundingBox()`) 로 보강. 사이드바 5명 + "전체 보기" 는 `routes.test.tsx`·`card.test.tsx`·`e2e/card.spec.ts:43` 사이드바 단언을 함께 갱신. 상세 `card-wrap mx-auto w-full md:w-3/4` 는 `3bd5025` 유지.
- 32행 체크리스트 19·20항은 P8b 뒤 "5명 기준" 으로 다시 본다(01-plan 200~201행 메모). 그때 R-U10R-2(밝은 모드)·R-U10R-3 도 같이 닫으면 된다.

**P9 (infra, backlog 93행)**
- 착수 조건 [필수] R-U10D-1~4 + 스모크 S1~S15(`review-u10-deploy-validity.md` §9) — backlog 에 이미 글자 그대로. 특히 `/api` 접두: 프론트는 `API_BASE='/api'` 고정(`client.ts`)이고 개발 프록시가 접두를 벗긴다(`proxy.ts stripApiPrefix`, §3 프록시 동일 바이트) — 운영 Caddy `handle_path /api/*` 가 같은 일을 해야 한다(R-U10D-2). 정적 산출물 `web/dist/`(`index.html`·`sw.js` 범위 `/`·`manifest.webmanifest`·`icon-*.svg`), `sw.js` 는 `Service-Worker-Allowed` 없이 루트에 있어야 범위 `/` 가 된다. 빌드에 비밀 0(불변식 7) · VAPID 공개키는 런타임 `GET /api/push/vapid-public-key`.
- R-U10D-10: U10 은 전부 Vite 5173 → uvicorn 8000 경로였다. 운영 URL 에서 데모 5단계(채팅 → 칩 → 카드 원문 → 브리핑 → 알림) 재현이 P9 수용 기준.
- 스케줄러 워커 수(R-U10D-9): `BRIEFING_SCHEDULER_ENABLED` 는 U10 에서 꺼져 있었다(수동 run 만). 운영에서 켤 때 `--workers 1`.

**P10 (eval-agent)**
- 평가 데이터에 넣을 실서버 관찰: ① 호칭 단독 언급(`과장님`)이 같은 사용자의 두 `과장님` 인물 중 하나에 0.95 로 자동 병합(R-U10R-4, trace 432) ② identity 거절 → new_person 후속(FIX-035, trace 449·453) ③ 처음 보는 이름 `지수` 에 임베딩 유사 후보(박수·박선영 과장님)로 identity 질문이 먼저 나온 것(원칙2 구간) — 되묻기 비율 측정 케이스.
- 브리핑 본문 표본: trace 427(`lines` 1·`suggestion` 1·금지 표현 0) — P6-briefing 인계 "원문 조각 표본 점검" 에 추가.

**설정값·주의(공통)**
- 조회 상한: `TIMELINE_LIMIT=20`·`FACT_SOURCES_LIMIT=20`·`BRIEFINGS_LIMIT=20`·`BRIEFINGS_LOOKBACK_DAYS=7`(`app/api/read.py` 54~77행) — 테스트가 값으로 고정(BM3).
- 개발 DB `relationship` 의 U10 확인 행은 남긴다(원칙8): 인물 7~11(`local`), 사건 27~32, 일정 6, 질문 12~17, 구독 1·3, trace ~459. 테스트는 `relationship_test`.
- `tests.md` 총계 203(+FIX-035 7 = 210) 과 "세는 법" grep 182 가 일치함을 이번에도 확인했다(이 세션 직접 실행). U10 수동 3절(FIX-035 6 · 정렬 2 · 29~32행 8)은 집계 제외 표기 그대로.

결과: 완료 — [필수] 0 · [권고] 10(사용자 확인 조건 2: R-U10R-1 OS 알림 클릭 · R-U10R-2 밝은 모드). 근거: 기계 검증 FAIL 0(WARN 3 은 하네스 ruff·04-review 부재·체크박스), 내가 직접 재실행한 백엔드 1953 passed skip 0 · 프론트 typecheck 0 · Vitest 137 · build · E2E 4 · 불변식 1~10 전부 기대값 · 실서버 부정 케이스 12건 전부 기대값 · 새 변이 6종 전부 검출(저장소 무수정) · backlog 수용 기준 3구절과 판정 표 1~28행 전부 증거로 통과 · 29~32행은 객관 항목을 DB·API 로 재확인해 일치했고, 빠진 것은 사용자 지시로 메인 세션이 대신한 "사용자 문장" 2곳과 에이전트가 할 수 없는 OS 알림 클릭·OS 밝은 모드 2곳뿐이며 이 둘은 수용 기준의 증거가 아니라 사람 점검 층의 일부라 [권고]+사용자 확인 조건으로 둔다(근거 §6 앞 단락). 승인 전 사용자가 R-U10R-1·2 를 1~2분에 수행하거나 면제를 `승인:` 줄에 적으면 된다. P8b 는 이 문서 뒤 시작 가능(backlog 89행 "의존: P8-frontend 04-review 완료").
승인: 사용자 (2026-10-21) — AskUserQuestion "승인 — 확인 2건은 면제": R-U10R-1(OS 알림 클릭)·R-U10R-2(밝은 모드)는 수행하지 않고 면제한다. 갈음 근거: 알림 클릭은 U9 22행 자동 테스트(`sw.js` notificationclick)와 P7 U8 사용자 실클릭(2026-10-10), 밝은 모드는 `tokens.css` 의 light/dark 토큰 쌍과 U4 토큰 테스트. 메인 세션 재확인: verify-impl FAIL 0/WARN 2 · Vitest 137 · typecheck 0(2026-10-21 21:47).
