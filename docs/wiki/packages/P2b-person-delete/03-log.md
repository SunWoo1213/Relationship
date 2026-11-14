# P2b-person-delete · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-11-09 16:35 · docs(P2b-person-delete): 인물 완전 삭제 계획을 검증까지 마치고 활성화한다 · pending
- 변경: `01-plan.md`(architect) · 결정 A~K 확정 · `02-plan-verify.md`(verifier `통과`) · evidence `20261109-1619/1626-verify-plan.txt`(2차 FAIL 0 / WARN 2 오탐) · `INDEX.md` 패키지 표에 id 추가 · `CURRENT.md active` · 이 로그.
- 이유(기획서·카드 연결): security.md §5 "인물 단위 완전 삭제 API" · 기획서 9장 제3자 개인정보 · F-4d2507(P2 04-review 인계). 사용자 2026-11-09 "다음 일들 쭉 진행, 배포는 하지 않음" — 배포 없이 할 수 있는 다음 항목.
- 정합성 확인: 점검표 8/8(02-plan-verify §2). 원칙5 — 카드 안 인라인 확인(새 화면·Dialog 없음). 원칙9 — 참조 trace 행 통째 삭제는 사용자가 비용을 알고 고름(결정 C). 원칙8 — 평가 trace 는 롤백되어 운영 trace 삭제가 `evaluation/`·`reports/` 에 닿지 않음(verifier 확인). 툴 7종 불변(결정 I).
- verifier [권고] 처리: R-1 판정 명령 따옴표 요령(`save_evidence.py` 가 `" ".join` → `bash -c` 라 `-k "a or b"` 가 깨짐, BSD grep `\|`) → 위임 프롬프트에 넣는다. **R-2 보정**: 01-plan 32행 "trace 를 읽는 평가 스크립트는 `run_pilot_eval.py` 하나" → `evaluation/runner.py`(370행)도 읽는다 — U1 ① 원칙8 확인 범위를 `scripts/run_pilot_eval.py` + `evaluation/` 로 넓힌다(결론 불변). R-3 registry 236행 "8테이블" → "9테이블" 은 U5. R-4 ① 01-plan 상태 줄 갱신(이 커밋) · ② U3 HTTP 테스트는 `client.request("DELETE", url, json=…)` — 위임 프롬프트에.
- 남은 것 · 다음 단위: U1 [backend-agent] 판별 순수 함수 `references_person` + `PERSON_REF_RULES` + 전수 조사.
- Refs: P2b-person-delete F-4d2507 security 원칙5 원칙8 원칙9

## 2026-11-09 16:45 · feat(P2b-person-delete): 기록 속에서 지울 인물을 가리키는 항목을 판별하는 규칙을 더한다 · pending (U1, backend-agent)
- 변경: 새 `app/api/delete.py`(규칙 상수 5종·`PERSON_REF_RULES` 1~5·`references_person(obj, person_id, *, tool_name=None)`, docstring 에 전수 조사 표) · 새 `tests/test_person_refs.py` 41건(실제 직렬화 코드로 픽스처) · `tests.md` 신설. 기존 파일 무수정.
- 결과: 41 passed · 전체 2177(2136+41) skip 0 · ruff · tools 7/7 · mypy 38=38 · 변이 V1-1~V1-9 전부 검출(런타임 치환). 메인 재확인 41 passed·ruff·새 파일 2개뿐.
- 전수 조사: `agent_traces` 쓰는 곳 7곳(`tools/context.py` 2·`memory/hooks.py`·`push/notifier.py`·`briefing/run.py` 3·`api/routes.py` loop_error), `pending_questions` 는 `ask_user` 1곳. 계획 표 밖 모양 없음. **계획과 다른 점**: `person_ids` 는 `PendingResume` 이 아니라 `ResolveOutcome.to_dict()`(`loop_resolve_done` output) · `candidate_person_ids` 는 스키마 설명에만(규칙 5 방어 유지) · `briefing_run` 은 일정 id 만. 원칙8(R-2): `run_pilot_eval.py`·`evaluation/runner.py` 만 trace 를 읽고 둘 다 세이브포인트 롤백 안 — 결론 불변. `fact_sources` 교차 연결 없음(6곳 확인).
- 하네스 메모: `bash-write-guard` 가 `.venv/bin/python --version` 을 stdin 코드로 오탐(기존 L 후보와 같음).
- verifier 커밋 전 리뷰(`review-u1-person-refs.md`): 1차 **보류**([필수] 1 · [권고] 4). 직접 재실행 41 passed·2177 skip 0·ruff·mypy 38=38, 다른 변이 RA 검출·RB 생존(→ R-U1-3), JSONB 왕복 형 보존 직접 확인, 전수 조사 재실행(쓰기 **8곳** — 위 "7곳" 은 오기, R-U1-2). [필수] R-U1-1 01-plan·02-plan-verify 의 `resume.person_ids` 오기 → 메인이 보정 2줄. [권고] R-U1-2 docstring 7→8곳·R-U1-3 규칙 2 `tool_name` 없이 고정 테스트 → U2 위임문 · R-U1-4 남는 행 목록 보완 → U5/security §5.
- verifier 재리뷰(§6) **통과** — 보정 2줄·코드 무변경 확인.
- 남은 것 · 다음 단위: U2 삭제 서비스(위임문에 R-U1-2·R-U1-3).
- Refs: P2b-person-delete F-4d2507 security 원칙8 원칙9 결정C 결정G

## 2026-11-14 · feat(P2b-person-delete): 인물을 지우면 별칭·사실·사건·일정과 그 인물을 가리키는 질문·판단 기록까지 함께 지우는 서비스를 더한다 · pending (U2, backend-agent)
- 변경: `app/api/delete.py` — `delete_person(session, user_id, person_id, confirm) -> PersonDeleteSummary`, `_referencing_question_ids`·`_referencing_trace_ids`, `CONFIRM_REASON="person_delete"`, docstring 7곳→**8곳**(R-U1-2 닫힘). 순서 소유 확인 → 확인값(`ConfirmationRequired`, 쓰기 0) → 집계 → 질문 삭제(답변 여부 무관, 결정 C-1) → trace 삭제(행 통째, C-2) → `DELETE persons` 한 문장(CASCADE, D) → commit 없음·trace 없음(H). `tests/test_person_refs.py` +1(R-U1-3 닫힘) · 새 `tests/test_person_delete.py` 24건(센티널 987654321, 실제 경로 world) · `tests.md` U2 절.
- 결과: 66 passed(두 파일) · 전체 **2202**(2177+25) skip 0 · ruff · tools 7/7 · mypy 38=38 · `alembic check` 무변경 · 기존 테스트 무수정. 변이 V2-1~V2-11 중 **V2-3(정리를 persons 삭제 뒤로) 는 동치 변이로 생존** — id 목록을 먼저 구해 지우고 `pending_questions`·`agent_traces` 에 persons FK 가 없어 순서가 결과를 바꾸지 않는다(verifier 재실행으로 확인; 계획 전제 "순서가 중요" 는 해당 없음). 메인 재확인 66 passed·ruff·3파일.
- verifier 커밋 전 리뷰(`review-u2-delete-service.md`) **통과**([필수] 0 · [권고] 5). 직접 재실행 2202 passed(28초)·다른 변이 RA(trace 사전 거름 input 만)·RB(확인값 strip) 검출. **R-U2-4 기록**: ① 결정 K "전 세션, `user_id` 한정" 의 실제 메커니즘 — JSONB 질의에 `user_id` 조건은 없고, `_owned_person` 이 `user_id` 로 소유를 확인한 뒤 전역 IDENTITY 인 `persons.id` 로 찾는다. 인물 id 를 JSONB 에 쓰는 경로 6곳이 모두 `user_id` 로 걸러진 조회에서 나오므로 다른 사용자의 기록이 같은 id 를 가질 수 없다(남는 사각 = 기존 F-fbaaae 단일 사용자 전제). ② V2-3 동치(위). ③ 구현자가 보고한 "전체 pytest 약 20분" 은 재현되지 않았고(28초, 다른 연결·락 0) 원인 미확정 — 이 단위 테스트가 원인이라는 증거 없음. ④ 센티널이 지나지 않는 3곳(`tool_error`·`push_send`·`resume.schedule.person_id`)은 쓰는 코드가 `person_id` 를 int 로 쓰고 규칙 1 이 깊이 무관 + decoy 왕복으로 덮음 — `tool_error` 경로 보강은 R-U2-2(U5 전).
- [권고] 처리: R-U2-1 docstring 232행 "V2-3 이 지킨다" 문구 → U3 에서 backend-agent · R-U2-2 `tool_error` world 추가 → U5 전 · R-U2-3 registry 행 3개(모듈·테스트 2) **이 커밋** · R-U2-5 tests.md 한 줄 → U5.
- **보류(CR-005, 2026-11-14)**: 사용자가 배포(Vercel)를 11-18 졸업평가 전에 요구 → 이 패키지는 **U2 커밋에서 멈추고 P9-infra 를 먼저 한다.** `delete_person` 은 호출자(라우트)가 없어 배포본에 노출되지 않는다. 재개는 U3(라우트)부터, 11-18 뒤.
- Refs: P2b-person-delete F-4d2507 security 원칙8 원칙9 결정A 결정C 결정D 결정E 결정H 결정K R-U1-2 R-U1-3 CR-005
