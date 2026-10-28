# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-28 13:55 (P8b-persons-grid 완료 승인 — 완료 커밋 승인 대기)

active: **none**(P8b-persons-grid 완료 2026-10-28) | frozen: none | 브랜치 `dev2` = origin/dev2 **`fff6e8c`**(U4, CI 40615729630 success) + **미커밋: P8b 완료 묶음(아래)** | origin/dev `f9500fe` · origin/main `f05d017` | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 12 — U10·U5 확인 행, 원칙8), 테스트 `relationship_test` | 기준선(코드 `a0f4bc3`): 백엔드 **1958 passed skip 0** · 프론트 **156 passed** · typecheck 0 · E2E 4

## 최근 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| P8-frontend 완료(10-21) | 04-review `완료`, 커밋 `fe76931` | `packages/P8-frontend/04-review.md` |
| **P8b-persons-grid 완료(10-28)** | 계획 `0973858` → U0 `adc650e`(`GET /persons` `aliases`) → U1 `2112a2a`(`PersonGrid` 그리드+검색) → U2 `529922f`(사이드바 5명+전체 보기) → U3 `a0f4bc3`(E2E, CI 복구) → U4 `fff6e8c`(판정 13행) → U5 사람 점검(메인 세션 Chrome+Playwright, 8항 통과, 수정 0) → verifier 04-review `완료`([필수] 0 · [권고] R-U5R-1~11) → **사용자 승인(R-U5R-2 면제)** → `CURRENT active: none` | `packages/P8b-persons-grid/04-review.md`·`03-log.md`·`tests.md` |

## 진행 중 (이 턴에서 멈춘 자리)
- **`docs(P8b-persons-grid)` 완료 커밋 승인 대기** — 포함: `04-review.md`(신규) · verifier 증거 15 + verify-impl 부속 + U5 증거(untracked) · `03-log.md`·`tests.md`·`01-plan.md`(체크박스) · `decisions/D15`(갱신 이력) · `docs/backlog.md`(P8b `[x]`) · `CURRENT.md` · `journal.md` · 이 HANDOFF. 제품 코드 변경 0.
- 백그라운드 서버: 백엔드 :8000(10-28 재시작, U0 코드) · 프론트 :5173. 세션 끝나면 꺼진다.
- Claude in Chrome: 이 세션은 Mac Chrome 만 연결돼 있었음. 창 폭 조절은 전체 화면 창에서 무시됨 → 모바일은 Playwright 스크립트(스크래치패드)로.

## 바로 다음에 할 것 (순서대로)
1. 위 커밋(`/commit`) → dev2 푸시 → CI 확인.
2. **dev 승격 검토**: P8·P8b 가 닫혔으니 `dev2:dev` 승격 후보 시점(L-003 — 승격 뒤 멈추고 실서버 확인). **배포 순서: 백엔드(U0 `aliases`) 먼저, 프론트 나중**(R-U5R-10 — `aliases` 없는 응답이면 `PersonGrid.tsx` 20행 TypeError).
3. 다음 후보(사용자 순서 ③→①): **③ 채팅으로 인물 정보 조회**(CR — trace 368 `not_callable_by_llm`) · **① 구글 로그인 + 사용자 격리**(CR, P9 착수 조건 R-U10D-3·F-fbaaae) · P9-infra(R-U10D-1~4·S1~S15, backlog 93행). FIX 후보: R-U5R-1 상세 `card-wrap` 폭 상한 Vitest 공백 · R-U5R-3 E2E 픽스처 별칭 순서 · R-U5R-4 별칭 질의 `user_id` `rowcount` 단언 · R-U10R-4 호칭 별칭("과장님") 단독 언급 자동 병합(원칙1) · R-U10R-5 저장된 브리핑 0 이면 "지금 브리핑" 없음 · 1-4 자동 병합 표시 · 응답 문장 1-1·1-2.
4. 하네스 L/FIX 후보: `stage-gate.sh`·`verify-impl.sh` 정규식이 `결과: **통과**` 굵게를 못 읽음(이번에 2회 걸림) · 프론트 단위 커밋 전 E2E 도 돌린다(R-U5R-11, U1·U2 CI 빨강) · FIX-033 (b) "구현 전 멈춤" 재강조(R-U5R-6) · 서브에이전트 API 한도(429) 중단 시 마커만 소비 · `save_evidence.py` psql `-f`·`cd web &&`·같은 분 이름 충돌 · 04-review 2.2 표 열 순서(`| # | 무엇 | 증거 | 결과 |` 는 verify-impl 이 못 읽음 — 템플릿 메모) · 03-log P8 U0~U3 머리줄 `pending` 잔존 · ruff 하네스 4건(R-U10R-8).
5. P10 인계: 발화 "윤서랑 처음 인사했어" 추출 0(R-U5R-9) · 호칭 단독 언급·FIX-035 거절→후속·`지수` 되묻기 케이스.
6. 복기자료(`~/Desktop/Portfolio/wiki/interview/relationship/`)는 취업 활동 재개 전까지 하지 않는다(메모리 규칙 2026-10-15).

## 사용자가 정한 것 (최근)
- 2026-10-28: U1 해석 6가지 수용 · U2 리뷰 먼저(단위=커밋 유지) · U5 "제가 Chrome 직접 조작" · **P8b 완료 승인, R-U5R-2 면제** · 커밋마다 "커밋 + 실험 푸시".
- 2026-10-27: 결정 K (나)·A~J 추천안 · N+1 판정 (i) 질의 횟수 단언 · P8b 계획 승인 · verifier 재시도는 "계속 진행해줘".
- 2026-10-21: P8 완료 승인(R-U10R-1·2 면제) · "P8 먼저 닫고 P8b" · U10 "너가 직접 해줘".

## 사용자 몫 · 주의
- 브랜치: `dev2` 작업 → `dev` 승격(`dev2:dev`, L-003) → `main`. **dev 승격 아직 안 함**(P7·FIX-018~035·P8·P8b 전부 dev2 에만). `.claude/.push-approved` 잔존 여부 확인. 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`, `cd web && npm ci`.
- 웹푸시 키 `.env` `VAPID_*`·`PUSH_DEV_PAGE_ENABLED=1`. [미확인] Windows 실기기 · main 보호 · OS 어두운 모드(P8b 는 에뮬레이션) · OS 알림 클릭(면제).
- **언어 전부 한국어** · 승인 질문 전 자세한 설명(예시 포함) · 위임 매번 L-004(마커는 답을 받은 뒤, **에이전트 하나당 마커 하나**) · 위임문은 01-plan 원문 인용·임의 제한 금지·열린 상수는 위임 전 확정 · 마커 생성/커밋/푸시 각각 따로 · **파일 변경은 Write/Edit 로만** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음 · 테스트 1건 = tests.md 1줄 · Claude in Chrome 은 Windows 쪽 Chrome 에 먼저 붙을 수 있음(`select_browser`).
