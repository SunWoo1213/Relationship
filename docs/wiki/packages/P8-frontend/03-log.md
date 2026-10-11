# P8-frontend · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-10-11 00:40 · docs(P8-frontend): 프론트 3화면 계획을 검증·승인까지 마치고 활성화한다 · ab29daa
- 변경: 01-plan(architect 초안 → 사용자 결정 반영 개정 1 → verifier 소견 반영 개정 2), 02-plan-verify(verifier 1차 보류 [필수] R-1 → 재검증 통과, 사용자 승인 기록), 05-remediation(`F-ce7d18` 해소), 증거 8개(메인 세션 3 · verifier 5), 이 03-log 생성. CURRENT active P8-frontend.
- 이유(기획서·카드 연결): backlog P8 첫 줄 수용 기준 "채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면". 사용자 확정 결정 A~N(A frontend-agent 신설 sonnet · C 같은 출처 + `/api` 접두 · F 원문 조회 API 2개 · L 챗봇형 UI Tailwind+shadcn/ui · M 오프라인 제외 — 기획서 부록 A 385행 · N ChatGPT 식 왼쪽 사이드바).
- 정합성 확인: 원칙 / D / S / 보안 — verifier 점검표 8행 통과(1차부터). 원칙5(화면 3개)·원칙7(경계 문장)·원칙9(조회는 판정 아님) 해석은 02-plan-verify §2-1 판정. 오프라인은 CR 없이 범위에서 제외.
- 승인 조건(사용자, 2026-10-10): ① U1~U9 모든 작업 단위는 커밋 전에 verifier 코드 리뷰 ② 디자인 추가 수정은 추후 요청 시 별도 작업(P8 안에서는 수정 1회 상한). 활성화는 FIX-030(`c37c99a`, CI run 38062960426 세 job success) 뒤 — 활성화하면 test-guards 상태 의존 실패가 가려지기 때문.
- 남은 것 · 다음 단위: U0 하네스 — 메인 세션이 훅 변경 diff 계획(②③ GATED·approve-commit → ① frontend-agent.md → ④ `fix_guard_check.py` 180행 `web/` → ⑤ test-guards 5경우 → ⑥~⑧ CLAUDE.md·SKILL.md·INDEX)을 사용자에게 먼저 보이고 승인, `settings.json` npm/npx allow 여부도 사용자 결정. verifier 권고 N-1~N-3 은 U9·04-review 에서.
- Refs: P8-frontend R12 R19 R8 D1 D7 S3.1 S3.4 S3.6 원칙5 원칙7 원칙9 F-ce7d18

## 2026-10-11 12:50 · harness(P8-frontend): 프론트 담당 에이전트를 만들고 승인·검증 게이트에 넣는다 · pending
- 변경: U0 ①~⑧ — `.claude/agents/frontend-agent.md` 신설(sonnet, 규칙 ①~⑧) · `delegate-guard.sh` GATED·`approve-commit.sh --stage` 에 frontend-agent · `fix_guard_check.py` 182행 `web/`(+22행 docstring·206행 메시지, `commit-guard.sh` 주석 11·100행) · `test-guards.sh` 6줄(케이스 6·7, `web/x.ts` 거부, frontend-agent 위임 거부/허용·마커 소비) · CLAUDE.md·devlog SKILL·INDEX. 사용자 결정으로 `settings.json` allow 에 `npm run`·`npm test`·`npm ci`·`npm install`(npx 제외).
- 이유(기획서·카드 연결): 01-plan U0, 결정 A, 사용자 확정 "FIX 게이트 web/ 까지". 적용 순서 ②③ → ① (R-3, 게이트 구멍 방지).
- 정합성 확인: L-002 · L-004 · 원칙5 · 원칙7 — 위반 없음. **`stage-gate.sh` 는 고치지 않음** — 앞 초안의 "⑨ `web/` 추가" 는 불필요(R-2, 면제 목록 방식), `test-guards` 165행 `web/x.ts (active: none) 거부` 가 실증.
- 검증: `evidence/20261011-1237-u0-harness.txt`(test-guards 실패 0·ok 222) · verifier `review-u0-harness.md` 결과 통과([필수] 0) · 변이 시험 `evidence/20261011-1241-verifier-u0-mutation.txt`(원본 exit 1 / web/ 조건 제거 exit 0). 권고 R-U0-1·2(CLAUDE.md 111행·SKILL 55행 문구)는 이 커밋에서 반영.
- **R-3: test-guards PASS 전에는 frontend-agent 위임 금지** — Mac PASS 확인(위 증거). **Windows 는 대기(R-U0-4)** — 푸시 뒤 CI windows job 결과를 증거 파일 끝에 덧붙인 뒤 "U0 완료(Mac·Windows)" 로 본다.
- 남은 것 · 다음 단위: R-U0-3 — U4 이후 단위별 verifier 리뷰에 `web/package.json` scripts 전부·의존성 변경·`package-lock.json` 동반 여부를 고정 점검 항목으로(npm allow 가 safety-guard 텍스트 매칭을 우회하는 간접 경로라서). security.md 한 줄 추가는 사용자 판단 대기. 다음: U1 인물 목록·카드 조회 API(backend-agent).
- Refs: P8-frontend L-002 L-004 원칙5 원칙7 F-ce7d18

## 2026-10-11 15:05 · feat(P8-frontend): 인물 목록과 인물 카드를 읽는 조회 API 를 더한다 · pending
- (앞 항목 보충) U0 커밋 = `440a0e5`. 그 CI run 38111227562 windows job 이 test-guards session-start 시험에서 멈춤(U0 새 시험은 Windows 에서도 ok) → 사용자 승인으로 취소 → **FIX-031** `6479c1d` 로 고침 → CI run 38116488226 세 job success(windows 3분 32초). **R-U0-4 해소 — U0 Mac·Windows 통과, frontend-agent 위임 가능(R-3).** R-U0-3: 사용자 결정 "security.md 에는 추가하지 않는다" — 단위별 verifier 점검만.
- 변경: `app/api/read.py`(신규 — `list_persons`·`get_person_card`, 이름 확정) · `schemas.py` 응답 모델 7종 · `routes.py` `GET /persons`·`GET /persons/{id}` · `tests/test_api_read_persons.py` 12건.
- 이유(기획서·카드 연결): 01-plan U1. 조회는 판정이 아니므로 DB 쓰기·trace 0(원칙9 해석, 02-plan-verify). 소유 확인은 `app.tools.persons._owned_person` 을 밑줄 이름 그대로 재사용(공개 승격 없음 — 보안 판정을 한 곳에) → 타 사용자·부재 같은 404.
- 정합성 확인: 원칙9 · S3.1(원문 보존 — 응답에 `raw_utterance` 없음, 타임라인 쿼리가 컬럼을 고르지 않음) · S3.5 · 스키마 v2. 확정 값: `TIMELINE_LIMIT=20`(01-plan "U1 에서 확정" — 카드는 최근 흐름, 이력은 facts·patterns 가 요약) · `UPCOMING_SCHEDULES_LIMIT=10`(01-plan 에 없던 값 — **사용자 결정 "10건 유지 + 테스트"**, 카드 응답 크기 상한, 24시간 브리핑 범위와 무관) · 별칭 정렬은 기존 `_person_out` 과 같은 Python `sorted()`(R-U1-4).
- 검증: verifier 1차 **보류** — [필수] R-U1-1 `last_contact_at` max→min 변이를 테스트가 못 잡음 → backend-agent 재작업(값 단언·순서가 뒤집히는 픽스처·상한·경계·별칭 테스트 5건) → 재검토 **통과**(변이 7건 모두 검출, `review-u1-read-persons.md`). 12 passed · 전체 1894 passed skip 0 · ruff · mypy 38/38. 증거 `evidence/20261011-1350-*`·`1420-*`·`verifier-u1-*`.
- **절차 위반 기록(R-U1-2)**: 1차 구현에서 backend-agent 가 `read.py`·`schemas.py`·`routes.py` 를 Bash(heredoc·python 치환)로 썼다(자기 보고) → secret-guard·stage-gate 미경유. verifier·메인 세션 확인 결과 내용은 깨끗(비밀 0·삭제 0·범위 밖 0). 재작업과 FIX-031 은 위임 프롬프트 맨 앞에 "Write/Edit 로만" 을 재명시해 지켜졌다(자기 보고). 근본 대책은 하네스 FIX 후보 **FIX-014**(훅을 Bash 쓰기까지 넓히기)와 연결.
- 남은 것 · 다음 단위: U2 원문 조회 API 2개(`GET /events/{id}/raw`, `GET /persons/{pid}/facts/{fid}/sources`, backend-agent). 위임 프롬프트에 "Write/Edit 로만" 을 계속 맨 앞에.
- Refs: P8-frontend S3.1 S3.5 원칙9 FIX-031 FIX-014
