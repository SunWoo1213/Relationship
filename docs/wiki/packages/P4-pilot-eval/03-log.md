# P4-pilot-eval · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-18 · docs(P4-pilot-eval): 계획검증 통과·계획 승인 — 결정 K 지배 기준, 패키지 착수 · b164f36
- 변경: `01-plan.md` 개정(의존 59c67cc·P3-llm-providers 추가 의존, 수용 기준 backlog 61행 문구, 결정 K (i)→(a) 지배 기준 226행·U4 `gate` 67행·판정 표 107행, R-1 U6 비용 문장 인용, R-2 행 번호 정정, R-3·R-4), `02-plan-verify.md`(verifier fable — 1차 09:30 보류 H-1 → 2차 09:50 통과, §1 verify-plan 0922·0930·0943·0954 FAIL 0/WARN 3 의도, 점검표 8/8, `승인: 사용자 (2026-09-18)`), `05-remediation.md`(F-0e133a 필수 해소, F-95c6a7·F-0ffff5 권고 열림 = registry 기존 행 확장 의도), `evidence/` 10파일(verify-plan 6·plan-refs 2·plan-signatures·validate-scenarios), `P3-llm-providers/04-review.md` 결과 줄 형식 1줄(verify-plan 의존 검사 regex), `CURRENT.md active: P4-pilot-eval`, journal, HANDOFF, 이 로그
- 이유(기획서·카드 연결): backlog 61행 "파일럿 평가(오병합률·미검출률·보정표·곡선 초안)" — S3.7 §5 P4 행, R3(D10 두 임계치 방향)·R4(자기보고 s_llm 보정) 를 닫는다. 결정 K 개정은 `exact_match.py:264~276` 의 오병합 0 가능성 때문에 단일 부등식이 방식 품질과 무관하게 미달을 낼 수 있어서(원칙8)
- 정합성 확인: 원칙 1·2·3·8·9 / D3 D4 D5 D10 D11 / S3.7 S3.3 / 보안 — 위반 없음(02-plan-verify 점검표 8/8). 코드 변경 0
- 남은 것 · 다음 단위: U1 러너 골격·격리·적재(eval-agent, L-004 승인 후). 결정 I: U6 전에 사용자 스모크 03·08(OpenAI) 1회. R-5~R-7 구현 시 반영
- Refs: P4-pilot-eval D3 D4 D5 D10 D11 S3.7 S3.3 R3 R4 F-0e133a L-002 L-004

## 2026-09-18 · feat(P4-pilot-eval): U1 러너 골격·격리·적재 — 세이브포인트 롤백·적재기 재사용·LLM mention 당 1회·hints None · pending
- 변경: `evaluation/runner.py` 신규(`run_pilot`·`RunSummary`·`RunnerError`·`build_runner_env`·`T_MERGE_GRID`·`T_NEW`·`ROW_EXTRA_KEYS`), `tests/test_eval_runner.py` 신규 29건, `docs/wiki/registry.md` 2행, `evidence/20260918-1239-u1-pytest.txt`·`20260918-1239-u1-pytest-all.txt`, 이 로그. `app/`·`data/` 변경 0
- 이유(기획서·카드 연결): 01-plan U1(64행) (i)~(v). 결정 D(i) 시나리오별 세이브포인트 롤백, 결정 C(i) LLM 1회 → 임계치 10벌, 결정 A(ii)·P3-llm-providers 인계 1(러너 매핑에 `LLM_PROVIDER=openai` 명시·`LLM_PROVIDERS_ENABLED` 제거), 인계 8(`embedder` 필수·임베딩 수 단언), 인계 9(두 벌 방지), 원칙9(`trace_id` 보존). 계획과 다르게 구현한 점: (1) 결정 C(i) 를 "confidence 에 `band_for` 재적용"이 아니라 "임계치마다 `resolve_mention()` 재호출 + LLM·임베딩 기억 래퍼"로 구현 — 러너가 밴드 규칙을 옮겨 적지 않아 `embedding_only` 동점 강등(R-5)·강제 강등이 방식 코드 그대로 유지되고, 제안 방식 행마다 자기 `er_resolve` trace 가 생긴다. LLM 호출 수는 계획과 같다(mention × 방식 1회, 테스트 단언). (2) 시그니처에 키워드 인자 4개 추가(`resolver_kwargs`·`env`·`before_rollback`·`overwrite`, 모두 기본값) — 스텁 주입·U7 실행 중 trace 덤프·원시 결과 덮어쓰기 방지. (3) JSONL 에 필수 4키 외 10키 추가 — U2 가 JSONL 만으로 분모 규칙(`passing_mentions`·`ambiguous`·`expected_ask_user.allowed`)을 적용하도록
- 정합성 확인: 원칙1·2(방식 판정 무개입, `ERConfig(t_merge, t_new=0.3)` 만 주입) / 원칙8(격자 고정, 기존 JSONL 덮어쓰기 거부) / 원칙9(`trace_id`·`llm_fresh_call`) / D5(별칭·mention 임베딩이 같은 기억 객체) / D10 / 보안(키·프롬프트 원문 미기록, summary 에 공급자 변수 두 값만)
- 검증: `POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 python -m pytest tests/test_eval_runner.py -q -rs` → 29 passed rc=0 (evidence/20260918-1239-u1-pytest.txt); 전체 `tests/` → 947 passed rc=0(기준 918 + 29, skip 0) (evidence/20260918-1239-u1-pytest-all.txt); `git diff --name-only -- app/ data/` 0줄
- 남은 것 · 다음 단위: U2 지표 계산기(JSONL 입력, 토큰 합산은 `llm_fresh_call` 행만). U7 은 `before_rollback` 으로 trace 표본 덤프. 실 공급자 경로(`judge_from_env`/`caller_from_env` 실 생성)는 U6 dry-run·U7 에서 처음 돈다
- Refs: P4-pilot-eval S3.7 D5 D10 원칙8 원칙9
