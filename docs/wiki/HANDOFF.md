# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-21 19:55 (CR-003 문서 이행 끝, `docs(CR-003)` 커밋 승인 대기)

active: **P8-frontend**(U0~U9 완료 · **U10 사람 점검 — 사용자 화면 점검 남음**) | frozen: **none**(CR-003 동결 2026-10-21 걸었다가 문서 이행 뒤 해제) | 브랜치 `dev2` = origin/dev2 **`3bd5025`**(CI 38890656483 success) + **미커밋 문서 11파일(이 커밋)** | origin/dev `f9500fe` · origin/main `f05d017`(사용자 README) | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 10·사건 30 — U10 테스트 행 남김, 원칙8), 테스트 `relationship_test` | 백엔드 **1953 passed skip 0** · 프론트 **137 passed** · E2E 4 (코드는 `3bd5025` 그대로)

## 이 세션(2026-10-21)에 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| 지난 커밋 뒤 남은 해시 기록 | 03-log FIX-035 항목 `735f391`·정렬 항목 `3bd5025` · registry FIX-035 7곳 `735f391`·`PersonCardScreen.tsx` 행 `3bd5025` | `packages/P8-frontend/03-log.md`·`registry.md` |
| **CR-003 문서 이행**(§4 1~3·5) | `frozen: CR-003` → **D15 신설**(`decisions/D15-persons-screen-layout.md` — 그리드·이름/별칭 검색(프론트)·태그 필터 없음·사이드바 최근 5명 `last_contact_at`·상세 가운데 75% **상한 없음**(R-U10C-4)·"코드에서 지켜야 할 것" grep 문장) · 01-plan 결정 N 인용문·U6·체크리스트 19·20 "CR-003·D15 대체" · backlog **P8b-persons-grid** 항목 + **P9 에 배포 유효성 요구(R-U10D-1~4·S1~S15)** · INDEX 47행·패키지 표 · proposal 상단 한 줄 · CR-003 상태 이행완료(동결 창 사유 R-U10C-6 기록) · journal CR 줄 → `frozen: none` | `changes/CR-003.md` |

## 진행 중 (이 턴에서 멈춘 자리)
- **`docs(CR-003)` 커밋 승인 대기** — 포함: `docs/backlog.md` `docs/proposal.md` `docs/wiki/{CURRENT,HANDOFF,INDEX,journal,registry}.md` `docs/wiki/changes/CR-003.md` `docs/wiki/packages/P8-frontend/{01-plan,03-log}.md` 신규 `docs/wiki/decisions/D15-persons-screen-layout.md`. 제품 코드 변경 0 → verifier 리뷰 불필요(문서 커밋). 커밋 뒤 dev2 푸시(메모리 규칙).
- 백그라운드 서버 없음(이 세션은 문서만). 필요하면 백엔드 :8000(`set -a; . ./.env; set +a; POSTGRES_PORT=5433 .venv/bin/uvicorn app.main:create_app --factory --port 8000`)·프론트 :5173(`npm run dev`).

## 바로 다음에 할 것 (순서대로)
1. **P8 닫기**: U10 32행 체크리스트 20항은 **사용자가** 데스크톱·모바일·밝음·어두움으로 본다(수정 반영 횟수: 1 — 증거 파일에 명시; 19·20항은 아직 전원 목록 기준, 5명은 P8b 뒤) · 31행(브리핑·알림)·29행 ⑤/30행 ⑧ 사용자 확인 문장 → verifier **04-review**(L-004 승인 먼저) → `/devlog done`.
2. **P8b-persons-grid** `/devlog start` → architect 01-plan(**D15 "코드에서 지켜야 할 것" 그대로**, 백엔드 변경 0, E2E `card.spec.ts`·`routes.test.tsx` 사이드바 단언 5명, R-U10C-3 목록 폭 단언 보강) → verifier 02-plan-verify → frontend-agent → 04-review. D15 갱신 이력에 완료 해시.
3. 그 뒤 CR 후보(사용자 순서 제안 ③→①): **③ 채팅으로 인물 정보 조회**(trace 368: LLM 이 `search_person` 부르려다 `not_callable_by_llm` 거부) · **① 구글 로그인 + 사용자 격리**(`APP_USER_ID` 고정 `app/settings.py:500`, `pending_questions` user_id 없음 F-fbaaae, `X-Session-Id` 클라이언트 값 — R-U10D-3 과 직결, **P9 착수 조건**) · ④ 음성 입력 **제외 유지**. UI/UX 소단위(2026-10-16 분석: 1-1·1-2·1-4·1-5·3-2·3-3·3-5·5-1·4-2·2-3)는 FIX 또는 P8c 로.
4. 복기자료(`~/Desktop/Portfolio/wiki/interview/relationship/17-개발과정-해설.md`)는 취업 활동 재개 전까지 하지 않는다(메모리 규칙 2026-10-15).

## 사용자가 정한 것 (최근)
- 2026-10-21: 재개 순서 "1→2 이어서 완료"(해시 기록 → CR-003 문서 이행 → docs 커밋).
- 2026-10-16: FIX-035 R-35-1 (a)·권고 전부 · U10 정렬 왼쪽+넓게, 상세 가운데·PC 기준·창 비례 · CR-003 A 수용(5명 기준 마지막 사건 시각·검색 이름+별칭·프론트 처리·타일→기존 상세 경로·P8b·⑥ 지금 U10 에) · "P8 마무리 먼저" · 음성 입력 제외 · 인물 화면은 기존 `#/persons` 수정.

## FIX 후보 (미착수 — 순서는 사용자에게)
- **하네스**: `approve-commit.sh --stage` 마커 덮어쓰기(두 에이전트 연속 승인) · `save_evidence.py` `bash -c` 인자 결합(SQL 따옴표·`cd web &&`) · 03-log U0~U3 머리줄 `pending` 잔존(해시는 registry 에 있음) · FIX-014 후속 R-14-19 · FIX-032 R-32-1·2 · FIX-033 R-33-7·8 · R-27-10~13 · R-30-2 · R-12 · R-29-1·3 · `findings.py` ruff 3건 · "완료 커밋 뒤 CI 확인" SKILL 규칙.
- **제품**: 1-4 자동 병합 표시(오병합 발견 창구) · 응답 문장 1-1·1-2 · R-U10D-5(`.env.example` 죽은 이름 3개) · R-U10D-9(스케줄러 워커 수) · 발송 네트워크(P7) · 잠금 404(결정 K) · `judge.py` docstring · 작업 메모리 미구현(S3.5) · `s_emb=0` 합산 · 인물 분리 없음 · `loop_extract` 토큰 0 · `update_person` 부분 반영 · `memory_promote` `source` 비대칭 · FIX-035 후속: 후보 1명 문구 실서버 확인.

## 사용자 몫 · 주의
- 브랜치: `dev2` 작업 → `dev` 승격(`dev2:dev`, L-003) → `main`. **dev 승격 아직 안 함**(P7·FIX-018~035·P8 전부 dev2 에만). `.claude/.push-approved` 잔존 여부 확인(있으면 삭제 요청). 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`, `cd web && npm ci`.
- 웹푸시 키 `.env` `VAPID_*`·`PUSH_DEV_PAGE_ENABLED=1`. [미확인] Windows 실기기 · main 보호.
- **언어 전부 한국어** · 승인 질문 전 자세한 설명(예시 포함) · 위임 매번 L-004(마커는 답을 받은 뒤, **에이전트 하나당 마커 하나**) · 마커 생성/커밋/푸시 각각 따로 · **파일 변경은 Write/Edit 로만** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음 · 테스트 1건 = tests.md 1줄 · 스크린샷은 세션 임시 폴더라 다음 세션엔 없음.
