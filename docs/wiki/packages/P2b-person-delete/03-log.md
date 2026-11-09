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
