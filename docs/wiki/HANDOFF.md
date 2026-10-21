# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-21 21:55 (P8-frontend 완료 승인 — `docs(P8-frontend)` 완료 커밋 승인 대기)

active: **none**(P8-frontend 완료 2026-10-21) | frozen: none | 브랜치 `dev2` = origin/dev2 **`75cb4ad`**(CR-003 문서; CI 39587449611 5 job success — verifier 확인) + **미커밋: P8 완료 묶음(아래)** | origin/dev `f9500fe` · origin/main `f05d017`(사용자 README) | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 11·일정 6·질문 17 — U10 확인 행 남김, 원칙8), 테스트 `relationship_test` | 백엔드 **1953 passed skip 0** · 프론트 **137 passed** · typecheck 0 · E2E 4 (verifier 재실행 2026-10-21 21:3x, 코드 `3bd5025`)

## 이 세션(2026-10-21)에 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| CR-003 문서 이행 | D15 신설 · 01-plan 결정 N/U6/19·20 · backlog P8b + P9 배포 요구 · INDEX · proposal 상단 · 해시 기록 → **커밋 `75cb4ad`** dev2 | `changes/CR-003.md`·`decisions/D15-persons-screen-layout.md` |
| U10 29~32행 마무리(사용자 "너가 직접 해줘") | 메인 세션이 이 Mac 의 Chrome(156)을 직접 조작 — 칩 왕복(q16→거절→q17→지인, 인물 11 지수) · 카드 원문 = DB · 일정 6 → `POST /briefings/run` → trace 427 = 화면, push sent · 20항 통과 17/부분 3 · 수정 반영 횟수 1 | `evidence/20261021-20{28,29,33,40}-u10-check-*` · `tests.md` U10 절 · 03-log |
| **verifier 04-review → `완료`** | [필수] 0 · [권고] R-U10R-1~10. verifier 직접 재실행 pytest 1953 · Vitest 137 · build · E2E 4 · 변이 6/6 검출 · 실서버 부정 12건. 메인 재확인 verify-impl FAIL 0/WARN 2 · Vitest 137 · typecheck 0 | `packages/P8-frontend/04-review.md` · `evidence/20261021-21*-verifier-04-*`(25개) |
| **사용자 승인 — P8 완료** | R-U10R-1(OS 알림 클릭)·-2(밝은 모드) **면제**(승인 줄에 갈음 근거). `CURRENT active: none` · backlog P8 `[x]` · journal DONE · R-U10R-7 01-plan 체크박스 11개 `[x]` · R-U10R-9 registry 259·260행 `0b24bb6` | 이 커밋 |

## 진행 중 (이 턴에서 멈춘 자리)
- **`docs(P8-frontend)` 완료 커밋 승인 대기** — 포함: `04-review.md`(신규) · U10 증거 8 + verifier 증거 25(untracked) · `tests.md` · `03-log.md`(U10 항목 + CR-003 항목 해시) · `01-plan.md`(체크박스) · `registry.md`(259·260) · `docs/backlog.md`(P8 `[x]`) · `CURRENT.md` · `journal.md` · 이 HANDOFF. 제품 코드 변경 0.
- 백그라운드 서버 켜짐: 백엔드 :8000(bash id bfadxxdvl)·프론트 :5173(b05bdijfl, `[::1]` 만 듣는다). 세션 끝나면 꺼진다.
- Chrome: Claude in Chrome 이 **Windows 쪽 Chrome("Browser 1")에 먼저 연결**돼 localhost 가 오류였다 → `list_connected_browsers` → `select_browser`(macOS "Browser 2"). 다음 세션도 같은 일이 생기면 같은 순서. 이 Mac 의 Chrome 창 최소 폭 500 → 모바일 390 은 E2E 로만.

## 바로 다음에 할 것 (순서대로)
1. 위 커밋(`/commit`, 사용자 승인) → dev2 푸시.
2. **P8b-persons-grid `/devlog start`**(active none 확인됨) → architect 01-plan(L-004): **D15 "코드에서 지켜야 할 것" 그대로**, 백엔드 변경 0, `card.test.tsx`·`routes.test.tsx`·E2E `card.spec.ts` 사이드바 단언 → 최근 5명 + "전체 보기", R-U10C-3 목록 폭 단언 보강(조상 전부 또는 `boundingBox()`), 02-plan-verify "무변경 diff" 기준 해시 = `3bd5025`(R-U10R-10) → verifier 02-plan-verify → 승인 → frontend-agent → 04-review. D15 갱신 이력에 완료 해시.
3. 그 뒤 후보(사용자 순서 ③→①): **③ 채팅으로 인물 정보 조회**(trace 368 `not_callable_by_llm`) · **① 구글 로그인 + 사용자 격리**(F-fbaaae, `APP_USER_ID` 고정, `X-Session-Id` — P9 착수 조건 R-U10D-3) · ④ 음성 입력 **제외 유지**. FIX/CR 후보 **R-U10R-4 호칭 별칭("과장님") 단독 언급 자동 병합**(er_resolve 432, 0.95 — 인물 10 `박선영 과장님`·인물 7 별칭 `박지훈 과장님` 공존, 원칙1) · UI 후보 R-U10R-5(저장된 브리핑 0 이면 "지금 브리핑" 없음) · 1-4 자동 병합 표시 · 응답 문장 1-1·1-2.
4. P9 착수 전 사용자 결정 R-U10D-3(공개 배포 정책) · 첫 단위 Dockerfile+S1(backlog 93행).
5. 복기자료(`~/Desktop/Portfolio/wiki/interview/relationship/`)는 취업 활동 재개 전까지 하지 않는다(메모리 규칙 2026-10-15).

## 사용자가 정한 것 (최근)
- 2026-10-21: 재개 "1→2 이어서 완료" · "P8 먼저 닫고 P8b" · U10 은 "이 컴퓨터에서 다시 해봐" → "너가 직접 해줘"(사용자 문장을 메인 세션 문장으로 대신) · verifier 04-review 시작 승인 · **P8 완료 승인, R-U10R-1·2 면제**.
- 2026-10-16: CR-003 A 수용(5명 기준 마지막 사건 시각·검색 이름+별칭·프론트 처리·타일→기존 상세 경로·P8b·⑥ 지금 U10 에) · "P8 마무리 먼저" · 음성 입력 제외 · 인물 화면은 기존 `#/persons` 수정.

## FIX 후보 (미착수 — 순서는 사용자에게)
- **하네스**: `save_evidence.py` 가 psql `-f`(컨테이너 경로)·`cd web &&`·SQL 따옴표를 깨뜨림(해결책: `'<'` 리다이렉션·`--prefix`) · 같은 분 이름 충돌 시 "이미 있다" · `approve-commit.sh --stage` 마커 덮어쓰기 · 03-log U0~U3 머리줄 `pending` 잔존 · ruff 하네스 4건(R-U10R-8, `.claude/scripts/`) · FIX-014 후속 R-14-19 · FIX-032 R-32-1·2 · FIX-033 R-33-7·8 · R-27-10~13 · R-30-2 · R-12 · R-29-1·3 · "완료 커밋 뒤 CI 확인" SKILL 규칙.
- **제품**: R-U10R-4(위) · R-U10R-5(위) · 1-4 자동 병합 표시 · 응답 문장 1-1·1-2 · R-U10D-5(`.env.example` 죽은 이름 3개) · R-U10D-9(스케줄러 워커 수) · 발송 네트워크(P7) · 잠금 404(결정 K) · `judge.py` docstring · 작업 메모리 미구현(S3.5) · `s_emb=0` 합산 · 인물 분리 없음 · `loop_extract` 토큰 0 · `update_person` 부분 반영 · `memory_promote` `source` 비대칭 · FIX-035 후속: 후보 1명 문구 실서버 확인.

## 사용자 몫 · 주의
- 브랜치: `dev2` 작업 → `dev` 승격(`dev2:dev`, L-003) → `main`. **dev 승격 아직 안 함**(P7·FIX-018~035·P8 전부 dev2 에만 — P8 완료가 승격 후보 시점). `.claude/.push-approved` 잔존 여부 확인(있으면 삭제 요청). 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`, `cd web && npm ci`.
- 웹푸시 키 `.env` `VAPID_*`·`PUSH_DEV_PAGE_ENABLED=1`. [미확인] Windows 실기기 · main 보호 · 밝은 모드 · OS 알림 클릭(면제).
- **언어 전부 한국어** · 승인 질문 전 자세한 설명(예시 포함) · 위임 매번 L-004(마커는 답을 받은 뒤, **에이전트 하나당 마커 하나**) · 마커 생성/커밋/푸시 각각 따로 · **파일 변경은 Write/Edit 로만** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음 · 테스트 1건 = tests.md 1줄 · 스크린샷은 세션 임시 폴더라 다음 세션엔 없음.
