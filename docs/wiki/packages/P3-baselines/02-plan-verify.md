# P3-baselines · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-10

선행 확인(`bash .claude/scripts/gitlog.sh P3-baselines`, 10:33): dev = `8fdc5b5`(origin/dev ahead 2, main `4f73b07`). 선행 패키지 완료 커밋 — P1-pilot-dataset 닫는 커밋 `5cac9bf`(U7 `f78e9dc`), P3-er 닫는 커밋 `0527ab8`(U9 `b3bcc2d`) — 01-plan 5행이 적은 네 해시가 모두 최근 커밋 20건에 있다. 태그 `P3-baselines` 커밋 0건(신규 패키지). 미커밋 변경: `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md`(추적) + `packages/P3-baselines/`·`packages/P1-pilot-dataset/evidence/`(미추적) — 제품 코드·카드 변경 없음. `evaluation/` 디렉터리는 아직 없다(`ls evaluation` → 없음), 저장소 루트에 `pyproject.toml`·`pytest.ini`·`setup.cfg` 없음(01-plan 169행 리스크와 일치).

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

### 1a. 1차 — 메인 세션 실행(02-plan-verify 작성 전)
명령: `bash .claude/scripts/verify-plan.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260910-1029-verify-plan.txt`
```
== verify-plan P3-baselines  (2026-09-10 10:29) ==
PASS  존재: docs/wiki/packages/P3-baselines/01-plan.md
FAIL  없음: docs/wiki/packages/P3-baselines/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  Refs 있음: - [ ] U1 공통 인터페이스·방식 표: `evaluation/__i
PASS  Refs 있음: - [ ] U2 제안 방식 어댑터: `evaluation/resolvers/prop
PASS  Refs 있음: - [ ] U3 베이스라인 1(문자열 완전일치): `evaluat
PASS  Refs 있음: - [ ] U4 베이스라인 2(임베딩 단독): `evaluation/re
PASS  Refs 있음: - [ ] U5 베이스라인 3(LLM 단일 프롬프트): `evalua
PASS  Refs 있음: - [ ] U6 시나리오 사전 상태 적재기: `evaluation/s
PASS  Refs 있음: - [ ] U7 **동일 인터페이스 계약 테스트**(수용 
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증 + 문서: 전체 `POSTG
PASS  backlog 일치: [eval-agent] 베이스라인 3종 (문자열 완전일치·�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-er
PASS  registry 중복 없음: evaluation/__init__.py
PASS  registry 중복 없음: evaluation/resolvers/__init__.py
PASS  registry 중복 없음: evaluation/resolvers/base.py
PASS  registry 중복 없음: evaluation/resolvers/registry.py
PASS  registry 중복 없음: evaluation/resolvers/proposed.py
PASS  registry 중복 없음: app.er.resol
PASS  registry 중복 없음: evaluation/resolvers/exact_match.py
PASS  registry 중복 없음: evaluation/resolvers/embedding_only.py
PASS  registry 중복 없음: evaluation/resolvers/llm_single.py
PASS  registry 중복 없음: evaluation/scenario_state.py
PASS  registry 중복 없음: persons.id
PASS  registry 중복 없음: scripts/baseline_smoke.py
PASS  registry 중복 없음: tests/test_baseline_base.py
PASS  registry 중복 없음: tests/test_baseline_proposed.py
PASS  registry 중복 없음: tests/test_baseline_exact_match.py
PASS  registry 중복 없음: tests/test_baseline_embedding_only.py
PASS  registry 중복 없음: tests/test_baseline_llm_single.py
PASS  registry 중복 없음: tests/test_scenario_state.py
PASS  registry 중복 없음: tests/test_baseline_parity.py
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=1 WARN=1 ==
```
FAIL 1 = 이 문서(02-plan-verify.md)가 아직 없었기 때문 → F-cf1510. WARN 1 = README.md 가 하네스 행(registry.md 32행)으로 이미 있음 → F-0ffff5. 두 소견의 원인·조치는 §3 과 05-remediation.md.

### 1b. 최종 — verifier 실행(이 문서 작성 후)
명령: `bash .claude/scripts/verify-plan.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260910-1036-verify-plan-final.txt`
```
== verify-plan P3-baselines  (2026-09-10 10:39) ==
PASS  존재: docs/wiki/packages/P3-baselines/01-plan.md
PASS  존재: docs/wiki/packages/P3-baselines/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  Refs 있음: - [ ] U1 공통 인터페이스·방식 표: `evaluation/__i
PASS  Refs 있음: - [ ] U2 제안 방식 어댑터: `evaluation/resolvers/prop
PASS  Refs 있음: - [ ] U3 베이스라인 1(문자열 완전일치): `evaluat
PASS  Refs 있음: - [ ] U4 베이스라인 2(임베딩 단독): `evaluation/re
PASS  Refs 있음: - [ ] U5 베이스라인 3(LLM 단일 프롬프트): `evalua
PASS  Refs 있음: - [ ] U6 시나리오 사전 상태 적재기: `evaluation/s
PASS  Refs 있음: - [ ] U7 **동일 인터페이스 계약 테스트**(수용 
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증 + 문서: 전체 `POSTG
PASS  backlog 일치: [eval-agent] 베이스라인 3종 (문자열 완전일치·�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-er
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/__init__.py
PASS  registry 중복 없음: evaluation/resolvers/__init__.py
PASS  registry 중복 없음: evaluation/resolvers/base.py
PASS  registry 중복 없음: evaluation/resolvers/registry.py
PASS  registry 중복 없음: evaluation/resolvers/proposed.py
PASS  registry 중복 없음: app.er.resol
PASS  registry 중복 없음: evaluation/resolvers/exact_match.py
PASS  registry 중복 없음: evaluation/resolvers/embedding_only.py
PASS  registry 중복 없음: evaluation/resolvers/llm_single.py
PASS  registry 중복 없음: evaluation/scenario_state.py
PASS  registry 중복 없음: persons.id
PASS  registry 중복 없음: scripts/baseline_smoke.py
PASS  registry 중복 없음: tests/test_baseline_base.py
PASS  registry 중복 없음: tests/test_baseline_proposed.py
PASS  registry 중복 없음: tests/test_baseline_exact_match.py
PASS  registry 중복 없음: tests/test_baseline_embedding_only.py
PASS  registry 중복 없음: tests/test_baseline_llm_single.py
PASS  registry 중복 없음: tests/test_scenario_state.py
PASS  registry 중복 없음: tests/test_baseline_parity.py
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=0 WARN=1 ==
```
FAIL 0 / WARN 1. WARN 은 F-0ffff5(의도된 WARN, §3). `findings.py P3-baselines evidence/20260910-1036-verify-plan-final.txt --source verify-plan` 실행(10:39, verifier) → 출력 `05-remediation.md 갱신: 새 소견 0, 해소 1, 열림 1 (필수 0)` / `✓ F-cf1510  해소`. 05-remediation.md 머리 줄 `열림: 1 (필수 0) | 해소: 1`.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | CLAUDE.md 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱" ↔ 01-plan 70행 "하지 않는 것: **인물 간(A–B) 관계·감정 대화·상담**(원칙7), **일정 라벨 평가**(P10-final-eval, 결정 C)". 산출물 표(77~96행)는 전부 `evaluation/`·`scripts/baseline_smoke.py`·`tests/test_baseline_*.py`·문서 2건이며 화면·관계 테이블·음성 경로가 없다. `S3.1-schema-v2.md` "인물–인물 관계 테이블 없음 (D8, 원칙7)" — 적재기(U6, 105행)는 "`seed_persons` 에 있는 인물만, `persons[].aliases` 를 그대로 … `events`·`schedules`·`pending_questions` 는 만들지 않는다" 이므로 `persons`·`person_aliases` 두 테이블만 쓴다. 베이스라인 3 프롬프트 입력은 57행 "사전 상태 인물 목록(표시 이름·별칭·관계 태그·위계)과 발화 맥락" — 사용자–인물 관계뿐이다. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | **원칙4 vs 베이스라인 3** — CLAUDE.md 원칙4 "엔티티 해석은 LLM 단일 호출로 하지 않는다"는 제품 속 에이전트의 해석 경로에 대한 금지이고, `S3.7-eval-spec.md` "베이스라인 3종 + 제안 방식, 동일 데이터·동일 지표" 와 `.claude/skills/eval-harness/SKILL.md` §3 표 "LLM 단일 프롬프트 \| 베이스라인 3" 이 그 대비군을 **명세로 요구**한다. 01-plan 은 결정 A(i) 152행 "`app/` 은 제품 런타임만, 평가 장치(러너·지표 계산기 포함)는 전부 `evaluation/`" · 67행 "`app/` 수정 — … 고치지 않는다" · 판정 표 129행 "`git diff --name-only <U1 직전 해시>..HEAD -- app/` → 출력 0줄" 로 제품 코드와 분리했다. `S3.3-er-pipeline.md` "**LLM 단일 호출로 대체 금지**(원칙4)" 의 대상인 `app/er/pipeline.resolve()` 는 어댑터(54행)가 호출만 하고 "`app/er/` 는 한 줄도 고치지 않는다". 역방향 import 금지 명령은 없다 → R-2. **원칙1·2** — 48행 "부수효과 0 — … 어떤 방식도 `ask_user`·`create_person`·`update_person`·`apply_resolution` 을 부르지 않는다", 50행 "`person_id` 는 `merge` 에서만 — `identity` 는 '사람에게 묻는다'이므로 후보 목록이 답이고 단일 인물을 고르지 않는다(원칙1·2)", 결정 B(i) 153행 "완전일치의 동명이인 2건 이상은 `identity`(임의 선택 금지, 원칙1·원칙8)". 어떤 방식도 자동 병합을 **실행**하지 않고 결정만 내므로 오병합 실행 경로가 없다. **원칙3** — 어댑터는 `confidence`·`s_emb`·`s_rule` 을 옮길 뿐(54행) 산식을 재구현하지 않는다; 임베딩 단독이 `s_emb` 만 쓰는 것은 그 방식의 정의(56행 "규칙 필터·LLM 판정 없음")이고 제품 산식이 아니다. **원칙8** — 베이스라인을 약하게 만들지 않는 장치가 세 결정에 문장으로 있다: 결정 C(iii) 154행 "`exact_raw`·`exact_norm` … P4 가 둘 다 보고", 결정 D(i) 155행 "`T_merge`/`T_new` 를 `s_emb` 에 그대로 적용", 결정 E(ii) 156행 "결정까지 LLM 이 내는 새 프롬프트 … 인물 목록 전체 제공 … 공급자·모델은 제안 방식과 같은 환경변수"; 49행 "예외 비대칭 금지 — … 한 방식만 예외로 죽으면 분모가 달라져 비교가 깨진다"; 66행 "골드 라벨 수정·재해석 … 데이터를 손대지 않는다"; 130행 판정 표 "`validate_scenarios.py --strict --json` rc=0 … 라벨을 고치지 않았다". 반대 위험도 163행 "베이스라인이 제안 방식과 비슷하게 나오는 것도 **결과**". **원칙9** — 166행 "제안 방식만 `agent_traces` 행을 남기고 베이스라인은 남기지 않는다 … `MentionDecision` 반환값이 방식별 원자료의 단일 출처" — 원칙9 의 대상은 CLAUDE.md "제품 속 에이전트가 호출"하는 판정이며, 베이스라인 결정의 근거는 `candidates`·`score`·`signals`·`detail.forced_reason`(22~36행)으로 반환값에 남는다. **원칙5·6** — 화면·패턴 감지 무관(산출물 표에 없음). **원칙7** — 1행. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D10-two-thresholds.md` "임계치 하나로 구현하지 않는다. 두 값 모두 설정값이며 trace `decision`에 어느 구간이었는지 남긴다" ↔ 01-plan 52행 "`config` 는 `ERConfig` 를 그대로 재사용(D10) — `t_merge`/`t_new` 를 P4 가 한 프로세스 안에서 스윕", 결정 D(i) 155행 "`band_for()` 재사용. 전용 τ 스윕 없음", 16행 `DECISIONS = ("merge", "identity", "new_person")  # D10 밴드 어휘와 같은 낱말`. 완전일치·LLM 단일은 임계치를 "하나로" 쓰는 것이 아니라 정의상 쓰지 않으며(52행 "각 방식이 두 값을 어떻게 쓰는지(또는 쓰지 않는지)는 모듈 docstring 에 한 줄") 제품 경로(`app/er/confidence.py band_for()`, 실재 확인 82행)는 무수정. `D03-confidence-formula.md` "trace `confidence_breakdown{…}` 필수(원칙9)" — 어댑터는 `resolve()` 가 이미 쓴 trace 를 `trace_id` 로 가리키고(33행) 산식 무수정. `D04-embedding-provider.md` "임베딩 호출은 반드시 `EmbeddingProvider` 인터페이스 뒤에 둔다" ↔ 결정 H 159행 "적재기는 `embedder` 인자를 받는다" + `app/tools/context.py` 103행 `embedder: EmbeddingProvider | EmbedderCallable | None` 재사용; D4 "파일럿 검증 기준은 동일: '팀장↔부장님' 유사도 > '팀장↔이모'" ↔ U4 103행 "`grouped_embedder` 로 통제한 유사도에서 '팀장↔부장님 > 팀장↔이모'(D4 검증 기준)가 밴드에 반영되는지". `D05-alias-level-embedding.md` "인물당 대표 벡터를 만들지 않는다" ↔ 56행 "`search_candidates()` 를 재사용해(중복 구현 금지, D5 별칭 top-K → 인물별 max)", U6 105행 별칭 단위 적재. `D01-…md` "`create_person` 호출 경로는 반드시 answered pending_question 을 거친다" ↔ 48행 어떤 방식도 `create_person` 을 부르지 않음. 재사용 심볼 실재: `app/er/candidates.py:91 search_candidates(ctx, mention, hints=None, *, top_k)`, `app/er/confidence.py:82 band_for(confidence, config)`, `app/er/dictionary.py:154 normalize(mention)`, `app/er/types.py:287 ERConfig(t_merge, t_new, …)`·`:175 Resolution(trace_id, mention, candidates, relaxed_retry, matched_person_id, confidence, band, forced_reason, decision, llm, …)`, `app/er/pipeline.py:238 resolve(ctx, mention, utterance, hints=None, *, judge=None, config=None)`, `app/tools/context.py:92 ToolContext(session, session_id, user_id, embedder, …)` — 01-plan 54·101행의 필드 매핑이 실제 필드명과 일치. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.2-tools-v2.md` 툴 7종 표 — 01-plan 은 툴을 추가·변경하지 않고 판정 표 131행 "`python scripts/tools_check.py` → `7/7 ok`" 로 무변경을 증거화; 어댑터는 `resolve()` 만 부른다(54행). `S3.1-schema-v2.md` `persons(id, user_id, display_name, relation_tag, hierarchy, …)`·`person_aliases(id, person_id, alias, source, embedding vector(1536), confirmed_at)` — 적재기가 쓰는 두 테이블뿐이고 새 테이블·컬럼 없음(산출물 표에 `alembic/` 없음, 131행 "`alembic check` → `No new upgrade operations detected.`"). `data/scenarios/promotion.json` sc-001 실물의 `persons[]` 키 `display_name·relation_tag·hierarchy·aliases` 가 `persons` NOT NULL 컬럼(`app/db/models.py` 102~105행)과 1:1 대응. `S3.3-er-pipeline.md` "≥ T_merge → 연결 / [T_new, T_merge) → identity / < T_new → new_person" ↔ 결정 D(i)·`band_for` 재사용(임계치 2개). `S3.7-eval-spec.md` "곡선: x = T_merge ∈ {0.5,…,0.95}, T_new=0.3 고정" ↔ 175행 "`ERConfig(t_merge=…)` 인자 주입으로 네 방식 모두 스윕 가능하다는 것이 이 패키지의 인터페이스 약속". `S3.4`·ask_user 비동기 — 어떤 방식도 `ask_user` 를 부르지 않으므로(48행) 프로토콜 무관; `identity`/`new_person` 은 `pending_questions.kind` 와 같은 어휘(D1 "`ask_user.kind` ∈ {identity, new_person, schedule}")를 결정 낱말로만 쓴다. 불일치 하나: 57행 환경변수 "`LLM_PROVIDER`·`ANTHROPIC_MODEL`" 에 OpenAI 경로의 `OPENAI_MODEL`(`.env.example` 9행, `app/er/judge.py:305`)이 빠짐 → R-4(문서 누락, S 카드 충돌 아님). |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 41행 "의존: P1 데이터셋" — `packages/P1-pilot-dataset/04-review.md` 179~180행 "결과: 완료 … 승인: 사용자 (2026-09-10)", 닫는 커밋 `5cac9bf`(gitlog). 비교 대상 P3-er — `packages/P3-er/04-review.md` 166~167행 "결과: 완료 / 승인: 사용자 승인 2026-09-06", 닫는 커밋 `0527ab8`. 1a 출력 "PASS 의존 완료: P1-pilot-dataset / P3-er". **P4 게이트** — `docs/wiki/INDEX.md` 패키지 표 아래 "**P4 이전에 P5 이후를 시작하지 않는다.**", `docs/backlog.md` 43행 "### P4 — 게이트"(P3 절 41행은 게이트 앞), `.claude/scripts/verify-plan.sh` 68~72행 `num ≥ 5` 일 때만 P4 04-review 를 검사 → 01-plan 5행 "P4 게이트는 이 패키지에 해당하지 않는다(게이트는 P5 이후에만 적용) — 오히려 이 패키지가 그 게이트의 입력을 만든다" 는 backlog·INDEX·스크립트 셋과 맞는다. P3-er §7 인계 "**`ERConfig.top_k` 는 스윕하지 말 것**(F-bdd6c5)" ↔ 69행 "`ERConfig.top_k` 스윕(P1 §7 인계 12 — F-bdd6c5 로 무효)" 하지 않음. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 41행 `- [ ] [eval-agent] 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능` ↔ 01-plan 111행 같은 문장(체크박스 제외). verifier 대조: `a=$(sed -n 41p docs/backlog.md \| sed 's/^- \[ \] //'); b=$(sed -n 111p …/01-plan.md \| sed 's/^- //'); [ "$a" = "$b" ]` → `SAME`; 1a "PASS backlog 일치". 해석 4문장(114~117행)은 각각 명령·기대 출력을 가진다 — "3종" = `ALL_METHODS` 포함 여부(126행 명령), "정의" = 스텁 호출 카운터 0/0/1(128행), "P1 데이터셋" = 실물 `data/scenarios/` 읽기, "동일 인터페이스" = `pytest tests/test_baseline_parity.py -q -rs` 통과 + parametrize 목록에 `proposed` 포함. 넷째 문장의 "방식별 분기 `if name == …` 가 테스트 본문에 없다" 는 판정 명령이 표(123~133행)에 없다 → R-1 에 구체 명령을 적는다(수용 기준 통과 자체는 pytest 출력으로 기계 판정된다). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan 100~107행 U1~U8 각 줄 끝 `/ Refs: P3-baselines …` — U1 `S3.7 D10 원칙2 원칙8`, U2 `S3.3 D3 D10 원칙1 원칙9`, U3 `S3.7 원칙1 원칙8`, U4 `S3.7 D4 D5 D10 원칙2`, U5 `S3.7 D3 원칙4 원칙8`, U6 `P1-pilot-dataset D5 원칙8`, U7 `S3.7 S3.3 D10 원칙8`, U8 `S3.7 원칙8 원칙9`. 1a 출력 "PASS Refs 있음" 8건. 태그가 가리키는 카드 D1·D3·D4·D5·D10 실재(1a "PASS 카드 존재" 5건), S3.3·S3.7 은 `docs/wiki/specs/` 에 실재(`ls` 확인). 단위 크기: 각 단위가 모듈 1개 + 테스트 1개(U5 는 + 스모크 스크립트, U8 은 evidence + 문서 2건)로 P3-er U5·U8 과 같은 크기 — 커밋 하나 규모. |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다" ↔ 01-plan 121행 "포트를 셸 변수로 넘긴다(`.env` 는 읽지 않는다, security.md §1)"; §1 "코드·문서·커밋에 키 문자열을 넣지 않는다 … `os.environ[…]` 로 읽는다" ↔ 57행 "키는 `os.environ` 으로만 전달하고 프롬프트·로그·예외 메시지에 넣지 않는다(security.md §1)", 62행 README "환경변수 **이름**만"; §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 61행 스모크 "키·프롬프트 원문은 남기지 않는다", U5 104행 테스트 "키 미노출(네트워크 0)"; §6 "우회하지 않고 사용자에게 명령을 그대로 보여주고 직접 실행을 요청" ↔ 135행 "Docker Desktop 이 꺼져 있거나 API 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security.md §6)", 132행 실호출은 "사용자 실행". §3·§4 — 산출물·판정 표에 삭제·prune·DROP·외부 전송 명령 없음(부수효과 0 조회는 `SELECT count(*)`). §5 "전체 대화 이력 저장 금지" — 베이스라인은 DB 에 쓰지 않고 프롬프트 입력은 `utterance` 한 턴(44행 시그니처). |

## 3. 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

### 기계 검증 소견
- **F-cf1510 [필수]** `02-plan-verify.md 없음` — 원인은 이 문서가 아직 없었던 것(검증 순서상 정상). 이 문서 작성 후 §1b 재실행으로 사라진다. 05-remediation.md 에 원인·해결 단계·재검증을 채웠다.
- **F-0ffff5 [권고]** `README.md 가 registry 에 하네스 행으로 이미 있음` — **의도된 WARN.** `registry.md` 32행 `| 문서 | 프로젝트 README(…) | README.md | 하네스 | pending | … P3-er U9: 진행 표 P3 행 … "엔티티 해석(ER) 실행법" 절 추가 …` 처럼 README 는 패키지마다 **기존 행 비고만** 덧붙이는 파일이다. 01-plan 95행 "`docs/wiki/registry.md` — 신규 행 추가(기존 행은 비고만)"·96행 "`README.md` — 베이스라인 실행법 절" 이 같은 규칙이고, 같은 F-id 가 P3-er 에서도 같은 판정으로 닫혔다(`packages/P3-er/05-remediation.md` 244~266행 "조치 없음 — … 기존 행 비고 갱신, 새 행 금지 … 판정: 닫힘 … 행 수 1 유지"). 스크립트는 "기존 파일 확장"과 "재작성"을 구분하지 못하므로 WARN 은 U8 뒤 `grep -c "| README.md |" docs/wiki/registry.md` = 1(행 수 불변)로 04-review 에서 닫는다. 계획 승인을 막지 않는다.

### 보류 항목 (H-n)
- 없음.

### 권고 (R-n · 승인 조건 아님 — 실행 시 반영하고 04-review 에서 본다)

| # | 내용 | 근거 | 반영 단위 |
|---|------|------|-----------|
| R-1 | 수용 기준 넷째 문장의 "방식별 분기 없음"을 **판정 명령**으로 고정: `grep -nE "if name ==\|if name in\|match name\|name !=" tests/test_baseline_parity.py` → 출력 0줄을 판정 표(123~133행)와 U8 evidence 에 넣는다. 단, `proposed` 에는 `FakeJudge`, `llm_single` 에는 스텁 클라이언트를 주입해야 하므로 **픽스처가 이름→팩토리 kwargs 표**를 갖는 것은 허용하고, 금지 범위는 "테스트 함수 본문의 단언·호출 분기"로 명시한다. 그렇지 않으면 구현자가 "분기 없음"을 자의적으로 해석한다. | 01-plan 117행 "(방식별 분기 `if name == …` 가 테스트 본문에 없다는 것도 함께 확인)" 에 명령이 없음; `verification.md` "출력 없이 붙인 명령"은 증거가 아님 | U7·U8 |
| R-2 | 원칙4 분리를 역방향으로도 증거화: `grep -rn "evaluation" app/ --include=*.py` → 0줄(제품 코드가 평가 패키지를 import 하지 않는다)을 U8 판정 표에 추가. 129행의 `git diff -- app/` 0줄은 "수정 없음"만 보이고 "의존 없음"은 보이지 않는다. | CLAUDE.md 원칙4; 01-plan 152행 결정 A "`app/` 은 제품 런타임만" | U8 |
| R-3 | **`identity` 일 때 `llm_single` 의 `candidates` 가 비어 있게 될 위험.** 50행 규약 "`identity` 는 … 후보 목록(`candidates`)이 답" 인데 57행 응답 스키마 `{decision, matched_person_id, s_llm, reason}` 에는 후보 목록이 없다. 구조화 출력에 `candidate_person_ids: int[]`(identity 일 때 헷갈린 인물 id 들, 사전 상태 밖 id 는 강등 규칙과 같이 처리)를 추가하거나, 없으면 `candidates=[]` 로 두고 `detail.forced_reason="no_candidate_list"` 를 남기는 쪽을 **U5 착수 전에 하나로 정해 모듈 docstring 에 적는다**. 정하지 않으면 P4 의 identity 품질 비교(골드가 후보 안에 있었는가)가 방식마다 다른 의미가 된다(원칙8 동일 지표). 결정 E(ii)의 스키마에 필드를 더하는 것이지 형태를 바꾸는 것이 아니다. | 01-plan 50행 vs 57행·156행; `S3.7` "동일 데이터·동일 지표" | U5 (U1 base.py docstring 에도 한 줄) |
| R-4 | 57행·156행 환경변수 목록에 `OPENAI_MODEL` 을 추가한다(`.env.example` 9행, `app/er/judge.py:305` 가 이미 읽는 이름). 공급자 중립을 말하면서 Claude 모델 변수만 적으면 OpenAI 경로가 기본값 `gpt-4o-mini` 로 조용히 떨어져 "제안 방식과 같은 모델" 보장이 깨질 수 있다. README 절에도 이름만. | 01-plan 57행 "제안 방식과 **같은 환경변수**(`LLM_PROVIDER`·`ANTHROPIC_MODEL`)"; `security.md` §1 이름만 | U5·U8 |
| R-5 | **private 함수 재사용 결정을 U5 전에 미리 내린다.** 결정 E(ii) "공급자 호출부는 같은 형태로 새 모듈에 둔다" 는 `app/er/judge.py:178 _call_with_error_mapping()`(timeout/rate_limit/api_error/connection 매핑)과 같은 로직을 필요로 한다. 165행 규칙("private 함수가 필요해지면 복제하지 말고 멈춰 사용자 결정")대로면 U5 는 거의 확실히 멈춘다. 선택지: (a) `from app.er.judge import _call_with_error_mapping` 을 **읽기 import 로 허용**(app/ 무수정 유지, 결합은 registry 비고에 기록) / (b) `judge.py` 에서 공개 이름으로 승격(= `app/` 1줄 수정, 67행 "하지 않는 것" 위반이므로 사용자 결정 필요) / (c) SDK 예외를 `llm_single.py` 가 직접 잡고 `detail.forced_reason` 어휘를 P3-er `llm.error` 어휘(`timeout/rate_limit/api_error/connection/schema/out_of_range_id`)와 같게 맞춘다. 메인 세션이 U5 시작 승인 때 하나를 고르면 왕복이 준다. | 01-plan 165행; `app/er/judge.py` 21행 "둘 다 `_call_with_error_mapping()`"; P3-er 04-review §7 "`llm.error` 어휘" | U5 착수 승인 시 |
| R-6 | 적재기의 `person_aliases.source` 값과 `confirmed_at` 을 명시한다(`S3.1` "`source` ∈ {user_said, confirmed, system}", 앱 검증 있음). 사전 상태 = "대화 전 알려진 별칭"(P1 결정 I)이므로 `confirmed` + `confirmed_at=ctx.now()` 가 의미에 맞고, `search_person` 이 `embedding IS NOT NULL` 별칭만 검색한다는 사실(`app/tools/persons.py:192,205`)을 docstring 과 `tests/test_scenario_state.py` 에 적는다 — `embedder` 를 주면 별칭 수 = `embedding IS NOT NULL` 수, 주지 않으면 전부 NULL(임베딩 단독·제안 방식이 `embedding_skipped` 로 떨어짐)을 단언해 P4 가 실 임베딩 없이 돌리는 사고를 막는다. | 01-plan 105행·159행 결정 H(i); `S3.1-schema-v2.md`; `D05` "새 별칭이 확정(`confirmed_at`)되면 즉시 임베딩한다" | U6 |
| R-7 | 시나리오 JSON 적재는 `scripts/validate_scenarios.py` 의 적재 함수를 재사용한다(P1 `dump_scenarios.py` 가 이미 그렇게 함 — registry 101행 "`validate_scenarios` 의 적재 함수만 재사용"). `schema_version` 2 확인도 그 경로에서 온다(P1 04-review §7 인계 10 "스키마 계약: `schema_version` 2"). 새 JSON 파서를 쓰면 중복 구현이다. | `registry.md` 100~101행; P1 §7 인계 10; CLAUDE.md "중복 구현 금지" | U6 |
| R-8 | `exact_norm` 은 `normalize()` 를 **mention 과 별칭 양쪽**에 적용한 뒤 비교하고, `normalize()` 가 빈 문자열을 돌려주는 입력(예: "님" 단독)은 `new_person` + `detail.forced_reason="empty_after_normalize"` 로 처리한다는 것을 U3 테스트에 넣는다. 한쪽만 정규화하면 "김팀장"↔"팀장" 같은 비대칭이 방식 정의를 흐린다. | 01-plan 102행·154행 결정 C(iii); `app/er/dictionary.py:154` "공백 제거 → 존칭 접미 제거(최대 1개) → 성씨 1글자 접두 제거" | U3 |
| R-9 | P1 04-review §7 인계 중 이 패키지 몫의 반영 확인 — 2(적재 = `seed_persons`+`aliases` 그대로) 58·105행 반영, 9(라벨 재해석 금지) 66행 반영, 10(schema_version 2) → R-7, 11(표본 40건은 방향만) 71·167행 반영, 12(`top_k` 미스윕) 69행 반영; 1·3·4·5·6·7·8·13 은 P4 몫으로 171~178행 인계에 옮겨 적음. 빠진 것은 10 하나이며 R-7 로 닫는다. 04-review 에서 P4 인계 6항(171~178행)이 그대로 남아 있는지 본다. | `packages/P1-pilot-dataset/04-review.md` 156~168행 | U6·U8 |

## 4. 결정
결과: 통과 — 점검표 8행 모두 통과. 원칙4 대비군(베이스라인 3)은 S3.7·eval-harness 가 요구하는 명세이고 `evaluation/` 로 제품 코드와 분리됐다(2행). 두 임계치·`identity` 어휘는 `band_for`·`ERConfig` 재사용으로 D10 과 일치하고 어떤 방식도 병합·질문을 실행하지 않는다(2·3행). 수용 기준은 backlog 41행과 글자 그대로 같고 4문장 해석이 명령·기대 출력을 가진다(6행). 권고 R-1~R-9 는 승인 조건이 아니며(R-3·R-5 는 U5 착수 전에 정하면 왕복이 준다) 04-review 에서 본다. §1b 최종 기계 검증 FAIL 0 이 이 판정의 기계 근거다(WARN 1 = F-0ffff5 의도된 WARN).
승인: 사용자 (2026-09-10)
