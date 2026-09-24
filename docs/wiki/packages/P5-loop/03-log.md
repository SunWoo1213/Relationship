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

## 2026-09-24 22:10 · feat(P5-loop): U2 인식 단계 — 발화 한 건에서 툴 호출 제안을 받는다 · 069bdc2
- 변경: `app/agent/propose.py` 신규(Proposer 프로토콜·PROPOSAL_SCHEMA·build_propose_prompt·validate_proposal·공급자 3종·PROPOSERS·proposer_from_env·FakeProposer), `__init__.py` 재export, `tests/test_agent_propose.py` 59개. 01-plan U2 [x]. evidence `20260924-2133-U2-pytest.txt`.
- 이유(기획서·카드 연결): 01-plan U2, 확정 L(iii) — LLM 이 제안하고 게이트(U3)가 거른다. 공급자 호출은 `app/er/judge.py` 를 수정 없이 import 해 재사용.
- 정합성 확인: 원칙 1·2·4(임계치·확신도 참조 0건)·9 / D1 D2 / S3.4 / 보안(키·환경변수·대화 이력을 프롬프트에 넣지 않음, 테스트로 확인) — 위반 없음. 전체 1406 passed.
- 남은 것 · 다음 단위: U2 에서 정한 것 — **R-22 (ㄴ) 채택**(툴 설명을 `inspect.signature` 로 런타임 생성, 소스에 `create_person(`·`update_person(` 리터럴 없음 → 5a·5b grep 0건), 제안 단계 타임아웃·재시도·모델은 ER 판정 설정(`ER_JUDGE_TIMEOUT`·`ER_JUDGE_MAX_RETRIES`·`*_MODEL`) 공유, `PROPOSAL_ARG_SCHEMA` 는 `type`·`relation_tag`·`hierarchy` 만 enum 으로 묶고 툴별 인자 검증은 게이트 단일 출처(R-12), 시각 확정 판단(결정 K)은 U3·U5 로 넘김. 다음 = U3 게이트(backend-agent, L-004). R-23 은 U3 에서 정한다.
- Refs: P5-loop S3.4 D1 D2 원칙9

## 2026-09-24 22:40 · feat(P5-loop): U3 게이트 — LLM 제안을 코드가 거르고 사유를 남긴다 · 8ecf75c
- 변경: `app/agent/gate.py` 신규(`check`·`GateConfig`·거부 사유 6종·`NOT_CALLABLE_BY_LLM`·`INJECTED_ARGS`), `__init__.py` 재export, `tests/test_agent_gate.py` 32개. 01-plan U3 [x]. evidence `20260924-2151-U3-pytest.txt`·`U3-checks.txt`.
- 이유(기획서·카드 연결): 01-plan U3, 확정 L(iii)·A(i)·K(i). 관문 순서 ①②④③⑤(④ person_id 금지를 ③ 인자 스키마보다 먼저 — 사유가 따로 남도록). 인자 검증은 `inspect.signature(app.tools.*)` 런타임 대조(U2 가 넘긴 단일 출처).
- 정합성 확인: 원칙 1·4(LLM 은 person_id 를 줄 수 없고 ask_user·search_person 을 부를 수 없다)·2(임계치·확신도 참조 0건)·9(거부 사유가 GateVerdict 에 남음) / D1(create_person → hint_only)·D2 / S3.4 / 보안 — 위반 없음. 전체 1438 passed, 게이트가 app.tools 를 부르지 않음(스파이 7종).
- 남은 것 · 다음 단위: U3 에서 정한 것 — **R-23**: `occurred_at`·`scheduled_at` 은 None·누락이면 "미확정"으로 통과(U5 가 결정 K(i) 로 되묻기), 값이 있는데 datetime 이 아니면 `bad_args`. 상한은 ①②④③ 통과 후보에만 적용(이미 거부된 것은 세지 않음), 언급 수는 `args.person` 서로 다른 값(create_person 제외). `GateLimits` 는 그 턴의 실제 개수가 아니라 적용된 설정값. `NOT_CALLABLE_BY_LLM` 은 propose.py 의 안내용 목록과 별도(강제용). **R-25 (ㄱ) 힌트↔언급 매칭 규칙은 U4 로 넘김.** 다음 = U4 해석 단계(backend-agent, L-004). U4 전에 R-25 (ㄴ) `held_drafts` 규칙도 정한다.
- Refs: P5-loop S3.4 D1 D2 원칙1 원칙4 원칙9

## 2026-09-24 23:10 · feat(P5-loop): U4 해석 단계 — 언급을 인물에 잇고, 애매하면 되묻고 멈춘다 · 7a2ec5c
- 변경: `app/agent/loop.py` 신규(해석 구간 — `resolve_mentions`, 되묻기 전 context 확장 두 갈래, 재개 데이터 크기 상한, `loop_resolve_done` trace). `run_turn`·`resume_turn` 은 U5 자리로 비움. `tests/test_agent_loop.py` 10개. 01-plan U4 [x]. evidence `20260924-2216-U4-pytest.txt`.
- 이유(기획서·카드 연결): 01-plan U4, 결정 C·D·E·M-0·M-1(d)·M-3 안 A, D2(비동기 대기 질문으로 턴 종료).
- 정합성 확인: 원칙 1·2·4(ER 의 band 문자열로만 분기, 확신도·임계치 참조 0건) / D1 D2 D12 D13 / S3.3 S3.4 / 보안 — 위반 없음. 루프가 pending_questions 를 직접 쓰지 않음. 전체 1448 passed.
- 남은 것 · 다음 단위: U4 에서 정한 것 — **R-25 (ㄱ)** `create_person` 힌트는 `display_name`·`aliases` 가 언급 문자열과 완전히 같을 때만 붙는다(아니면 버림 — M-3 안 A 로 태그는 답에서 오므로 저장 결과 불변, 힌트는 hierarchy 에만). **R-25 (ㄴ)** `pending_calls` 는 재개 재실행 근거라 버리지 않고, `held_drafts` 는 사람이 읽는 미리보기(앞 200자)라 `LOOP_MAX_RESUME_BYTES` 초과 시 비운다. 크기 계산은 `app.tools.context.to_jsonable` 적용 후(실제 저장과 같게). `MentionDecision.to_dict()` 는 er_resolve trace_id 만 담는다(중복 저장 방지). `app/agent/__init__.py` 재export 는 U5 에서 run_turn 과 함께. 다음 = U5 기록 + 응답(backend-agent, L-004). R-24 는 U5 에서 정한다.
- Refs: P5-loop D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4

## 2026-09-25 00:10 · feat(P5-loop): U5 기록·응답 단계 — 확인된 사람의 기록만 저장하고 사실만 답한다 · 1835355
- 변경: `app/agent/loop.py` 에 `run_turn()`·기록 구간(`_record_impl`·`_execute_call`·`_ask_schedule`·`_needs_schedule_question`)·trace 래퍼 추가, `app/agent/respond.py` 신규(`build_reply`), `types.py` `SCHEDULE_UNKNOWN_OPTION`, `__init__.py` 재export, `tests/test_agent_loop.py` U5 6개(총 16). 01-plan U5 [x]. evidence `20260924-2245-U5-pytest.txt`(7행 (가)(나)·22행 포함)·`20260924-2312-U5-fix-pytest.txt`.
- 이유(기획서·카드 연결): 01-plan U5, 결정 B(i)·C(i)·D·E·K(i)·M-2(i). 원칙7 경계 문장.
- 정합성 확인: 원칙 1·2·4·7·9 / D1 D2 / S3.2 S3.4 / 보안 — 위반 없음. 7행 (가)(나)·22행 기대 일치. 전체 1453 passed / 1 failed(test_er_pipeline 782행 — FIX-004).
- 남은 것 · 다음 단위: U5 에서 정한 것 — **R-24**: 기록 단계가 제안마다 `ToolError` 를 잡아 `failed[]` 에 담고 계속한다(run_turn 밖 예외 — 공급자·LoopError·SQLAlchemyError — 는 U6 몫). **후보 시각 규칙**: `ctx.now()` 기준 내일·모레 저녁 7시 + "모르겠어요"(발화 속 상대 날짜를 다시 파싱하지 않음). 한 턴에 질문 하나 — schedule 질문이 나면 그 뒤 execute 제안은 전부 pending_calls 로. **사용자 결정(2026-09-24)**: ER 되묻기로 멈춘 턴에서 merge 된 언급의 시각 없는 add_schedule 은 failed 가 아니라 그 질문의 resume.pending_calls 로(재개 때 U7 이 시각을 묻는다). `TurnResult.stop_reason` = 질문 있으면 "ask_user", 아니면 게이트 값("limit"/None). `TurnResult.trace_ids` = loop_extract·loop_gate·loop_resolve_done·loop_record 4행(loop_turn 자신 제외). `PendingQuestionOut` 은 ORM 재조회 없이 ask_payload 에서 재구성. **U6·U7·U8 에서 재확인**: stop_reason·trace_ids 값 집합. **7행 명령은 개발 DB 에 행을 남긴다** — 다시 돌리면 FIX-004 전 테스트가 또 깨진다. 다음 = FIX-004 → U6.
- Refs: P5-loop D1 D2 S3.2 S3.4 원칙1 원칙7 원칙9 FIX-004

## 2026-09-25 00:50 · fix(FIX-004): 인물 해석 테스트가 DB 전체 질문 수 대신 해석 전후를 비교한다 · pending
- 변경: `tests/test_er_pipeline.py` 한 테스트의 단언을 전후 비교로. `docs/wiki/fixes/FIX-004.md` 신규. evidence `20260924-2325-FIX-004-er-pipeline-pytest.txt`·`20260924-2319-FIX-004-full-suite-pytest.txt`. HANDOFF 재작성(세션 마무리).
- 이유(기획서·카드 연결): 판정 표 7행 명령이 개발 DB 에 남긴 확인 행 때문에 DB 전체 개수 0 단언이 깨졌다. 검사 대상(결정4 — resolve() 는 부수효과 없음)에 단언을 맞춘다.
- 정합성 확인: 원칙·D·S 변경 없음, 원칙8(남은 행 삭제 안 함), 제품 코드 무변경 — 위반 없음. 전체 1454 passed, 실패 0 · 스킵 0.
- 남은 것 · 다음 단위: 다음 세션 = 푸시 여부 확인 → U6 `POST /chat`(backend-agent, L-004). 판정 표 7행 명령은 U8 전까지 다시 돌리지 않는다.
- Refs: FIX-004 P5-loop P3-er D2 원칙8
