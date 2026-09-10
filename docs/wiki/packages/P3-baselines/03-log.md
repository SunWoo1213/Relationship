# P3-baselines · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-10 10:45 · docs(P3-baselines): 계획·계획검증 승인, 패키지 착수 — 베이스라인 3종 + 공통 Resolver 인터페이스 · pending
- 변경: `01-plan.md`(architect 초안 + 결정 확정 A~H·I·J), `02-plan-verify.md`(verifier 통과, 권고 R-1~R-9, `승인: 사용자 (2026-09-10)`), `05-remediation.md`(F-cf1510 해소·F-0ffff5 의도된 WARN 열림), `evidence/20260910-1029-verify-plan.txt`·`20260910-1036-verify-plan-final.txt`, `CURRENT.md active: P3-baselines`, `docs/backlog.md` 41행 세분화 줄 U1~U8, 이 로그
- 이유(기획서·카드 연결): backlog 41행 "베이스라인 3종 … 제안 방식과 동일 인터페이스로 호출 가능". S3.7·eval-harness §3 "동일 데이터·동일 지표" 의 배관. P4 게이트의 입력을 만든다
- 정합성 확인: 원칙4(대비군은 `evaluation/` 격리, `app/` 변경은 결정 J 1건 예외) / 원칙8(베이스라인 약화 금지 장치: 결정 B·C·E) / 원칙1·2·D10(`identity` 어휘·`band_for`·`ERConfig` 재사용) / S3.1·S3.2 무변경 / security(키·프롬프트 미출력, 실호출 사용자 실행) — 위반 없음
- 남은 것 · 다음 단위: **U1 공통 인터페이스** eval-agent(L-004 승인 후). U5 전에 결정 I·J 반영. 권고 R-1·R-2(U7·U8), R-4(U5·U8), R-6·R-7(U6), R-8(U3) 을 각 단위 위임 프롬프트에 넣는다
- Refs: P3-baselines S3.7 S3.3 D3 D4 D5 D10 원칙4 원칙8 L-002 L-004

## 2026-09-10 13:58 · feat(P3-baselines): U1 공통 Resolver 인터페이스·방식 표 — evaluation/ 패키지 신설, 불변 규약 4개, 계약 테스트 39건 · pending
- 변경: `evaluation/__init__.py`(패키지·의존 방향 R-2 명문화), `evaluation/resolvers/base.py`(`DECISIONS`·`ResolverCandidate`·`MentionDecision`·`Resolver` Protocol, 불변 규약 4개 docstring), `evaluation/resolvers/registry.py`(`RESOLVERS`·`register`·`get_resolver`·`ALL_METHODS` 동적, 예약 이름 5개), `evaluation/resolvers/__init__.py`(공개 진입점, U2~U5 import 자리), `tests/test_baseline_base.py`(39건), `registry.md` 5행, evidence `20260910-1358-u1-pytest.txt`(39 passed)·`20260910-1358-u1-isolation.txt`(`app/` 변경 0줄·`grep evaluation app/` 0줄·U1 `ALL_METHODS` 빈 튜플), journal(PUSH·RELEASE 줄), HANDOFF, 이 로그
- 이유(기획서·카드 연결): 01-plan U1 "공통 인터페이스·방식 표" — S3.7·eval-harness §3 "동일 데이터·동일 지표" 는 **동일 호출**이 먼저 성립해야 한다. 결정 A(i) `evaluation/` 최상위, 결정 B(i) `supported_decisions`, D10 `band_for` 어휘·`ERConfig` 재사용
- 정합성 확인: 원칙1·2(`person_id` 는 `merge` 에서만 — `__post_init__` 강제) / 원칙4(`app/` diff 0줄, 역방향 import 0줄 = R-2 를 U1 에서 선반영) / 원칙8(빈 표에 자리표시자 없음, 예외 비대칭 금지 규약) / security(키·네트워크·DB 없음) — 위반 없음
- 남은 것 · 다음 단위: **U2 제안 방식 어댑터**(`evaluation/resolvers/proposed.py`, `app.er.resolve` 호출만, `app/er/` 무수정) eval-agent(L-004 승인 후). U1 시점 `ALL_METHODS` 는 빈 튜플이며 U2 가 첫 등록. R-1(U7·U8)·R-4(U5·U8)·R-6·R-7(U6)·R-8(U3) 유지
- Refs: P3-baselines S3.7 D10 원칙1 원칙2 원칙4 원칙8 R-2 L-002 L-004
