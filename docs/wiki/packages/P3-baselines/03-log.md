# P3-baselines · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-10 10:45 · docs(P3-baselines): 계획·계획검증 승인, 패키지 착수 — 베이스라인 3종 + 공통 Resolver 인터페이스 · pending
- 변경: `01-plan.md`(architect 초안 + 결정 확정 A~H·I·J), `02-plan-verify.md`(verifier 통과, 권고 R-1~R-9, `승인: 사용자 (2026-09-10)`), `05-remediation.md`(F-cf1510 해소·F-0ffff5 의도된 WARN 열림), `evidence/20260910-1029-verify-plan.txt`·`20260910-1036-verify-plan-final.txt`, `CURRENT.md active: P3-baselines`, `docs/backlog.md` 41행 세분화 줄 U1~U8, 이 로그
- 이유(기획서·카드 연결): backlog 41행 "베이스라인 3종 … 제안 방식과 동일 인터페이스로 호출 가능". S3.7·eval-harness §3 "동일 데이터·동일 지표" 의 배관. P4 게이트의 입력을 만든다
- 정합성 확인: 원칙4(대비군은 `evaluation/` 격리, `app/` 변경은 결정 J 1건 예외) / 원칙8(베이스라인 약화 금지 장치: 결정 B·C·E) / 원칙1·2·D10(`identity` 어휘·`band_for`·`ERConfig` 재사용) / S3.1·S3.2 무변경 / security(키·프롬프트 미출력, 실호출 사용자 실행) — 위반 없음
- 남은 것 · 다음 단위: **U1 공통 인터페이스** eval-agent(L-004 승인 후). U5 전에 결정 I·J 반영. 권고 R-1·R-2(U7·U8), R-4(U5·U8), R-6·R-7(U6), R-8(U3) 을 각 단위 위임 프롬프트에 넣는다
- Refs: P3-baselines S3.7 S3.3 D3 D4 D5 D10 원칙4 원칙8 L-002 L-004
