# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-28 11:40 (U3 verifier 리뷰 **통과**([필수] 0 · [권고] R-U3-1~3 기록) — `test(P8b-persons-grid)` U3 커밋 승인 대기: `web/e2e/card.spec.ts` + registry·tests.md·03-log·review-u3·증거 9 + HANDOFF·journal. 커밋·푸시 뒤 **CI E2E 초록 확인** → U4(frontend-agent: 판정 13행 전체·tests.md 대조·registry 해시). **배포 순서 메모(R-U1-2): main 승격 시 백엔드 U0 먼저**)

active: **P8b-persons-grid**(U0 `adc650e` · U1 `2112a2a` · U2 `529922f` 완료, U3~U5 남음) | frozen: none | 브랜치 `dev2` = origin/dev2 **`529922f`**(U2; CI E2E 는 U3 까지 빨강 예정 — U1 `2112a2a` 의 **CI 40602788831 실패 — `web (ubuntu)` E2E `card.spec.ts` 72·102행 `[data-screen="persons"]` 미표시 — **원인: E2E 픽스처 `PERSONS`(8~11행)에 `aliases` 가 없어 `PersonGrid.tsx` 20행 `.filter` 가 TypeError(verifier U1 탐침 X7 그대로)** → U3 에서 픽스처에 `aliases` 추가 + 사이드바 단언 갱신으로 닫는다(U3 위임문 첫 줄에). 계획상 E2E 갱신은 U3 몫이라 예정된 빨강이지만, 단위 판정에 E2E 가 없어도 CI 는 돌린다 → U3 까지 dev2 CI 빨강 유지, 하네스 L 후보 "단위 커밋 전 `npm --prefix web run e2e` 도 돌린다". 다른 4 job success) | origin/dev `f9500fe` · origin/main `f05d017` | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 11·일정 6 — U10 확인 행), 테스트 `relationship_test` | 기준선(HEAD `529922f`): 백엔드 **1958 passed** · 프론트 **156 passed** · typecheck 0 · E2E 4(U3 전까지 CI 빨강)

## 최근 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| P8-frontend 완료(2026-10-21) | verifier 04-review `완료`([필수] 0 · [권고] 10, R-U10R-1·2 면제) → 커밋 `fe76931` | `packages/P8-frontend/04-review.md` |
| P8b `/devlog start` 1~7단계(2026-10-21~27) | architect 01-plan → **D15 전제 오류 발견**(목록 응답에 별칭 없음) → 사용자 **결정 K (나)** `GET /persons` 응답에 `aliases` 1필드 + A~J 추천안 전부 → D15·CR-003 §2·backlog 89행·INDEX 77행 보정(새 CR 아님) → verify-plan FAIL 0/WARN 3 → verifier 02-plan-verify **통과**(1차 10-22 Fable 한도 429 로 중단 → 10-27 재시도; [권고] R-1~R-9 반영 = 개정 2) → **사용자 승인** → `CURRENT active: P8b-persons-grid` · 03-log · journal START | `packages/P8b-persons-grid/01-plan.md`·`02-plan-verify.md`·`03-log.md` |

## 진행 중 (이 턴에서 멈춘 자리)
- **계획 커밋 `0973858`** → **U0 커밋 `adc650e`**(19파일: `read.py`·`schemas.py`·`test_api_read_persons.py` + registry·tests.md·03-log·01-plan·02-plan-verify·review-u0·증거 8, 사용자 승인 "커밋 + 실험 푸시") → `origin dev2` 끝. 03-log U0 항목 `pending` → `adc650e` 은 다음 커밋에. 기준선 이제 백엔드 **1958 passed**. 미커밋은 journal 자동 줄·이 HANDOFF 뿐.
- **U1 커밋 `2112a2a`**(24파일, verifier 통과 [필수] 0 · [권고] R-U1-1~5, 사용자 승인 "커밋 + 실험 푸시") → `origin dev2` 끝. Vitest 기준선 이제 **149**. 03-log U1 항목 `pending` → `2112a2a` 은 다음 커밋에.
- **U2 커밋 `529922f`**(20파일, verifier 통과 [필수] 0 · [권고] R-U2-1~4, 사용자 승인 "커밋 + 실험 푸시"). Vitest 기준선 **156**. 03-log U2 항목 `pending` → `529922f` 은 다음 커밋에.
- **U3 frontend-agent 진행 중(10:50)** — 위임문: 01-plan U3 줄 원문 + **첫 줄 = 픽스처 `PERSONS`(card.spec 8~11행)에 `aliases` 추가(CI 빨강 원인)** · 6명+ 픽스처 · 76행 `3 + PERSONS.length` → `3 + 5 + 1`(R-U2-2) · 53·108행 클릭 인물은 앞 5명 안 · `sidebar-see-all` → 그리드 → 검색 → 타일 → 카드·원문(기존 단언 유지) · `boundingBox` 폭(허용치 2px 실측 03-log) · 모바일 1열 · `expectNoStrayRequests` · 변이 V3-1~3. 로컬 Playwright 1.64.0·Chromium 설치돼 있음(`npm --prefix web run e2e` 가 build+preview 4173 자동).
- (기록) U2 위임문에 01-plan U2 줄 원문 + 결정 E·F 값 + 변이 V2-1~5 + **R-U1-1**(실패 상태 `person-search` null 단언 1줄, card.test 353행 근처) + **R-U1-5**(`PersonList.tsx` 1~2행 머리 주석 "사이드바 전용") + FIX-033 (b) "구현 전 멈춤" 재강조. (아래 U0 경과는 기록용) U0 backend-agent 경과(1차 13:45 는 `stage-gate.sh` 가 `결과: **통과**` 굵게 표기를 못 읽어 코드 쓰기 거부·변경 0 → 02-plan-verify 120행 표기만 고치고(판정 무변경, 하네스 FIX 후보) 14:00 마커 재생성·재시도; 사전 결정: 137행 키 집합 단언에 `"aliases"` 추가 1줄 허용. 2차는 코드·테스트 5건 작성 뒤 **Docker 데몬 꺼짐**으로 pytest 전부 skip → 메인 세션이 `open -a Docker` + `docker start capstone2-postgres-1` 로 DB 복구(14:40), skip 증거 삭제, 같은 에이전트에 SendMessage 로 미실행 항목(pytest·전체 회귀·변이 2·registry·tests.md) 이어서)** — 바꿀 수 있는 파일 `app/api/read.py`·`schemas.py`·`tests/test_api_read_persons.py` 셋뿐(판정 8행). 끝나면 보고 수치 재실행 → verifier 리뷰(L-004) → `/commit`(feat(P8b-persons-grid) U0).
- 백그라운드 서버: 백엔드 :8000·프론트 :5173 이 10-21 세션에서 띄운 채 아직 떠 있음(세션 종료 시 꺼짐). U0 pytest 는 `relationship_test` DB 라 무관.

## 바로 다음에 할 것 (순서대로)
1. 위 커밋(`/commit`) → dev2 푸시.
2. **U0** `GET /persons` 응답에 `aliases: list[str]` — backend-agent(L-004 승인 → `--stage backend-agent`). 위임문에 01-plan U0 줄 **원문 인용**(별칭 정렬 = `read.py` 177행 `sorted()` 코드포인트 순 · N+1 금지 판정은 질의 횟수 단언 또는 verifier 리뷰 명시 · `_person_out` 재사용 여부 registry 61행 보고 · 원문 필드 없음·쓰기 0 단언 유지) + FIX-033 (a)~(d). 판정 `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v`, 증거 `evidence/*-u0-read-persons-aliases.txt`. **제품 코드 커밋 전 verifier 리뷰**(P8 승인 조건과 같음 — 단위마다). `types.ts` 동기화는 U1.
3. U1 그리드+검색(frontend-agent — 위임문에 01-plan U1 줄 원문: testid `person-grid`·`person-tile`·`person-search`·`person-grid-empty`, 결정 A~D·G~I 값, 리스크 4 (a), 변이 V1-1~V1-11 표) → U2 사이드바 5명(`SIDEBAR_RECENT_LIMIT` AppShell export, V2-1~5) → U3 E2E(픽스처 6명+, `boundingBox` 허용치 2px 실측 03-log) → U4 자동 판정 13행·tests.md·registry → U5 사람 점검(메인 세션 Chrome — **이 Mac 의 "Browser 2" 선택** 필요할 수 있음, 수정 반영 1회 상한, 밝은 모드는 사용자) → verifier 04-review → done. 완료 해시를 D15 갱신 이력에.
4. 그 뒤 후보(사용자 순서 ③→①): ③ 채팅으로 인물 정보 조회(CR) · ① 구글 로그인 + 사용자 격리(CR, P9 착수 조건 R-U10D-3) · ④ 음성 입력 제외 유지. FIX/CR 후보 R-U10R-4 호칭 별칭("과장님") 단독 언급 자동 병합(원칙1) · UI 후보 R-U10R-5(저장된 브리핑 0 이면 "지금 브리핑" 없음) · 1-4 자동 병합 표시 · 응답 문장 1-1·1-2.
5. 복기자료(`~/Desktop/Portfolio/wiki/interview/relationship/`)는 취업 활동 재개 전까지 하지 않는다(메모리 규칙 2026-10-15).

## 사용자가 정한 것 (최근)
- 2026-10-27: P8b 계획 승인 · verifier 재시도는 "계속 진행해줘" 로.
- 2026-10-21: 결정 K (나) · A~J 추천안 전부 · P8 완료 승인(R-U10R-1·2 면제) · "P8 먼저 닫고 P8b" · U10 "너가 직접 해줘".
- 2026-10-16: CR-003 A 수용 · "P8 마무리 먼저" · 음성 입력 제외 · 인물 화면은 기존 `#/persons` 수정.

## FIX 후보 (미착수 — 순서는 사용자에게)
- **하네스**: `stage-gate.sh` 121행 정규식 `^결과:[[:space:]]*통과` 가 verifier 의 `결과: **통과**`(굵게) 를 못 읽음 → 정규식에 `\*{0,2}` 허용 또는 plan-verify 템플릿에 "굵게 금지" 명시 · 서브에이전트가 API 한도(429)로 중단되면 L-004 마커만 소비되고 산출물 없음 — 재시도 규칙(마커 재생성 근거)을 SKILL/훅에 · `save_evidence.py` psql `-f`(컨테이너 경로)·`cd web &&`·같은 분 이름 충돌 · `approve-commit.sh --stage` 마커 덮어쓰기 · 03-log U0~U3 머리줄 `pending` 잔존(P8) · ruff 하네스 4건(R-U10R-8) · FIX-014 후속 R-14-19 · FIX-032 R-32-1·2 · FIX-033 R-33-7·8 · R-27-10~13 · R-30-2 · R-12 · R-29-1·3 · "완료 커밋 뒤 CI 확인" SKILL 규칙.
- **제품**: R-U10R-4 · R-U10R-5 · 1-4 자동 병합 표시 · 응답 문장 1-1·1-2 · R-U10D-5(`.env.example` 죽은 이름 3개) · R-U10D-9(스케줄러 워커 수) · 발송 네트워크(P7) · 잠금 404(결정 K/P6) · `judge.py` docstring · 작업 메모리 미구현(S3.5) · `s_emb=0` 합산 · 인물 분리 없음 · `loop_extract` 토큰 0 · `update_person` 부분 반영 · `memory_promote` `source` 비대칭 · FIX-035 후속: 후보 1명 문구 실서버 확인 · P8 tests.md 갱신 여부(P8b 리스크 8, 사용자 결정).

## 사용자 몫 · 주의
- 브랜치: `dev2` 작업 → `dev` 승격(`dev2:dev`, L-003) → `main`. **dev 승격 아직 안 함**(P7·FIX-018~035·P8 전부 dev2 에만). `.claude/.push-approved` 잔존 여부 확인. 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`, `cd web && npm ci`.
- 웹푸시 키 `.env` `VAPID_*`·`PUSH_DEV_PAGE_ENABLED=1`. [미확인] Windows 실기기 · main 보호 · 밝은 모드 · OS 알림 클릭(면제).
- **언어 전부 한국어** · 승인 질문 전 자세한 설명(예시 포함) · 위임 매번 L-004(마커는 답을 받은 뒤, **에이전트 하나당 마커 하나**) · 위임문은 01-plan 원문 인용·임의 제한 금지 · 마커 생성/커밋/푸시 각각 따로 · **파일 변경은 Write/Edit 로만** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음 · 테스트 1건 = tests.md 1줄 · Claude in Chrome 은 Windows 쪽 Chrome 에 먼저 붙을 수 있음(`select_browser` 로 Mac).
