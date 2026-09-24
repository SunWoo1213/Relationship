# P5-loop · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-24 21:15 · docs(P5-loop): 3차 검증 통과·계획 승인 — 패키지 착수 · 24feebd
- 변경: 02-plan-verify 3차 판정(통과, 8/8, [필수] 0, R-20~R-27) + 승인 줄(F 6종·A 게이트 적용·총 제안 상한 13). evidence `20260924-2051-verify-plan-4.txt`(FAIL 0/WARN 8). 05-remediation F-b38c2c 원인 칸. 01-plan M-3 안 B 잔존 문장 정리(R-21). backlog P5 세분화 줄 U1~U8·L(iii) 결정 요약(R-9). CURRENT active: P5-loop.
- 이유(기획서·카드 연결): devlog start 7~8단계. 02-plan-verify §4 가 R-9·R-21 을 승인 커밋에서 반영하라고 적었다. backlog 수용 기준 문장은 바꾸지 않았다.
- 정합성 확인: 원칙 1·2·4·7·9 / D1 D2 D12 D13 / S3.4 / 보안 — 위반 없음(코드 변경 없음). 편집 후 verify-plan 재실행 FAIL=0 WARN=8.
- 남은 것 · 다음 단위: dev 푸시 뒤 사용자 결정(L-003) → U1(backend-agent, L-004 승인). R-22·R-23·R-24 는 U2·U3·U5 에서.
- Refs: P5-loop R6 R7 D1 D2 S3.4 L-002 L-004

## 2026-09-24 21:45 · feat(P5-loop): U1 루프 계약 타입과 trace 어휘 — 도는 코드는 아직 없다 · 3e4db92
- 변경: `app/agent/types.py`·`__init__.py` 신규(계약 타입·trace 상수·LoopError 계층), `app/settings.py` 루프 상수 추가(5·5·3·13·8192), `tests/test_agent_types.py` 22개. 01-plan U1 [x]. evidence `20260924-2111-U1-pytest.txt`.
- 이유(기획서·카드 연결): 01-plan U1. 결정 F·A·M-1(d)·M-2(i)·M-3 안 A 의 계약 고정. S3.4 — 재개 context 에 발화 원문 없음.
- 정합성 확인: 원칙 1·2·4(app/agent/ 임계치·확신도 참조 0건)·9 / D1 D2 / S3.4 / 보안 — 위반 없음. 전체 1347 passed, alembic check 무변경, tools_check 7/7.
- 남은 것 · 다음 단위: U1 에서 정한 것 — `Proposal.raw` = LLM 원문 dict(실행 경로 미사용), `GateVerdict.rejected.reason` 어휘는 U3 gate.py 단일 출처, `LOOP_MAX_RESUME_BYTES = 8192` 초기 추정치(U8 재확인), 결정 G 설정은 U2 가 judge.py 기존 설정 재사용. 열린 것 — `ResumeInput` 필드: U1 문장(`kind·context·answer`) 채택, 산출물 절 70행 `session_id` 표기와 불일치(01-plan 정리 필요), R-25(ㄴ) `held_drafts` 채움 규칙은 U4 착수 전 결정. 다음 = U2 propose(backend-agent, L-004).
- Refs: P5-loop S3.4 D1 D2 원칙9

## 2026-09-24 22:10 · feat(P5-loop): U2 인식 단계 — 발화 한 건에서 툴 호출 제안을 받는다 · pending
- 변경: `app/agent/propose.py` 신규(Proposer 프로토콜·PROPOSAL_SCHEMA·build_propose_prompt·validate_proposal·공급자 3종·PROPOSERS·proposer_from_env·FakeProposer), `__init__.py` 재export, `tests/test_agent_propose.py` 59개. 01-plan U2 [x]. evidence `20260924-2133-U2-pytest.txt`.
- 이유(기획서·카드 연결): 01-plan U2, 확정 L(iii) — LLM 이 제안하고 게이트(U3)가 거른다. 공급자 호출은 `app/er/judge.py` 를 수정 없이 import 해 재사용.
- 정합성 확인: 원칙 1·2·4(임계치·확신도 참조 0건)·9 / D1 D2 / S3.4 / 보안(키·환경변수·대화 이력을 프롬프트에 넣지 않음, 테스트로 확인) — 위반 없음. 전체 1406 passed.
- 남은 것 · 다음 단위: U2 에서 정한 것 — **R-22 (ㄴ) 채택**(툴 설명을 `inspect.signature` 로 런타임 생성, 소스에 `create_person(`·`update_person(` 리터럴 없음 → 5a·5b grep 0건), 제안 단계 타임아웃·재시도·모델은 ER 판정 설정(`ER_JUDGE_TIMEOUT`·`ER_JUDGE_MAX_RETRIES`·`*_MODEL`) 공유, `PROPOSAL_ARG_SCHEMA` 는 `type`·`relation_tag`·`hierarchy` 만 enum 으로 묶고 툴별 인자 검증은 게이트 단일 출처(R-12), 시각 확정 판단(결정 K)은 U3·U5 로 넘김. 다음 = U3 게이트(backend-agent, L-004). R-23 은 U3 에서 정한다.
- Refs: P5-loop S3.4 D1 D2 원칙9
