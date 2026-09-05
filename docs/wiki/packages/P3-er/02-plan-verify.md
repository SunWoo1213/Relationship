# P3-er · 계획 검증 (02-plan-verify)

대상: 01-plan.md **개정 1**(architect(opus), 머리말 "개정 1 — verifier 보류 3건·권고 7건 반영(사용자 결정 2026-09-06 00:10)", U1~U9) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 초판 2026-09-05 20:39(결과 보류) → **개정 2026-09-05 22:06(재검증, 다른 verifier 세션)**

개정 이력 — 초판(2026-09-05 20:39, 다른 verifier 세션): 점검표 #2 보류, 필수 소견 3건(F-138665 F-f43a9d F-8c6354)·권고 7건. **이 개정**: 01-plan 개정 1 을 같은 카드(S3.3 S3.7 S3.2 S3.4 / D01 D02 D03 D04 D05 D06 D10 / security §1 §5 / entity-resolution·agent-observability 스킬 / CLAUDE.md 원칙 1~4·8·9 / backlog P3·P4 / P2 04-review §6 §7)와 다시 대조. §1 최종 출력 교체, §2 #2 재판정(통과), §3 보류 3건 닫힘·권고 7건 닫힘·**새 권고 6건**, §4 결과 통과. 초판 본문은 git 이력(`docs/wiki/packages/P3-er/02-plan-verify.md` 첫 커밋 전 미커밋 상태였으므로 evidence `20260905-2038-verify-plan-3.txt`·`20260905-2035-plan-review-findings.txt` 가 초판의 기록이다)에 남는다.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령 이력: `20260905-2029-verify-plan-2.txt`(초판 전, FAIL 1 = 02-plan-verify 부재) → `20260905-2038-verify-plan-3.txt`(초판 후, FAIL 0/WARN 9 — 보류 1 + registry 8) → `20260905-2142-4-verify-plan.txt`(01-plan 개정 1 후, 메인 세션 실행, FAIL 0/WARN 9 — 보류 1 은 이 문서 초판의 표기) → `20260905-2206-verify-plan-5.txt`(이 개정 **전**, FAIL 0/WARN 9 동일) → 이 문서 개정 **후** 재실행: `bash .claude/scripts/verify-plan.sh P3-er > docs/wiki/packages/P3-er/evidence/20260905-2206-verify-plan-6.txt`. 아래는 재실행(최종) 출력 전체.
```
== verify-plan P3-er  (2026-09-05 22:18) ==
PASS  존재: docs/wiki/packages/P3-er/01-plan.md
PASS  존재: docs/wiki/packages/P3-er/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D2
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R4
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 F-ca12ad 수정 + `@traced` 확장: `app/tools/cont
PASS  Refs 있음: - [ ] U2 임베딩 런타임 공급자: `OpenAIEmbeddingProv
PASS  Refs 있음: - [ ] U3 호칭 사전 + 규칙 필터(2단계): `app/er/typ
PASS  Refs 있음: - [ ] U4 확신도·두 임계치(4단계): `app/er/confiden
PASS  Refs 있음: - [ ] U5 후보 검색 어댑터(1단계) + LLM 판정(3단�
PASS  Refs 있음: - [ ] U6 파이프라인 `resolve()`·trace(부수효과 0):
PASS  Refs 있음: - [ ] U7 `apply_resolution()` + 회귀 3종: `app/er/pipelin
PASS  Refs 있음: - [ ] U8 백필·스모크 스크립트: `scripts/backfill_e
PASS  Refs 있음: - [ ] U9 수용 기준 기계 검증 + 문서: 전체 `POSTG
PASS  backlog 일치: 승진 회귀 테스트 통과, trace에 `confidence_breakdo
PASS  의존 완료: P2-tools
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/er/__init__.py
PASS  registry 중복 없음: app/er/types.py
PASS  registry 중복 없음: app/er/dictionary.py
PASS  registry 중복 없음: app/er/candidates.py
PASS  registry 중복 없음: app/er/rules.py
PASS  registry 중복 없음: app/er/judge.py
PASS  registry 중복 없음: app/er/confidence.py
PASS  registry 중복 없음: app/er/pipeline.py
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: app/embedding.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
| 모듈 | 임베딩 Protocol | app/embedding.py | P2-tools | a9cb254 | `Embeddi
WARN  registry 에 다른 패키지로 이미 있음: app/tools/context.py → | 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | �
WARN  registry 에 다른 패키지로 이미 있음: scripts/embed_pilot.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
PASS  registry 중복 없음: app.embed
PASS  registry 중복 없음: scripts/backfill_embeddings.py
PASS  registry 중복 없음: scripts/er_smoke.py
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) | 
WARN  registry 에 다른 패키지로 이미 있음: tests/conftest.py → | 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftes
PASS  registry 중복 없음: tests/test_er_dictionary.py
PASS  registry 중복 없음: tests/test_er_rules.py
PASS  registry 중복 없음: tests/test_er_confidence.py
PASS  registry 중복 없음: tests/test_er_judge.py
PASS  registry 중복 없음: tests/test_er_pipeline.py
PASS  registry 중복 없음: tests/test_embedding_provider.py
PASS  registry 중복 없음: tests/test_backfill_embeddings.py
WARN  registry 에 다른 패키지로 이미 있음: tests/test_tools_context.py → | 테스트 | trace 행 기록·예외 시 tool_error·문자열 절단 | tests/
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=0 WARN=8 ==
```
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. WARN 8 = 기존 registry 행 8(공유 파일 8개 — `app/settings.py`·`app/embedding.py`·`app/tools/context.py`·`scripts/embed_pilot.py`·`requirements.txt`·`tests/conftest.py`·`tests/test_tools_context.py`·`README.md`)에 대한 것으로 01-plan 212행 "여덟 파일 모두 새 행을 만들지 않고 기존 행의 비고만 갱신" 과 05-remediation F-fdb56f 외 7건(조치 없음, **U9** 에서 `grep -c` 행 수 불변 확인 — 개정 1 재매김 반영)으로 처리된다. 초판의 "보류 1 건" WARN(F-033bb1)은 #2 통과로 사라졌다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 행 번호는 01-plan 개정 1 기준.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱" ↔ 01-plan 53행 "인물 간(A–B) 관계 저장, 고민 상담·감정 대화, 음성 입력 — 범위 밖(원칙7). ER 은 사용자–인물 관계만 다룬다". 화면 추가 0(원칙5), 브리핑 문장화·제안 없음(52행). 산출물 목록(57~84행)에 프론트·API 라우트 없음. 경계 P5(47~48행 "`resolve()` 는 `mention` 을 인자로 받는다"·"루프·툴 라우팅·채팅 엔드포인트·`POST /answers` 재개 — P5-loop"), P1/P3-baselines/P4(49행), P6/P7/P8(52행), 스키마 변경 0(51행 "새 Alembic revision 0건"), 벡터 인덱스 연기 근거 169행 "근사 검색은 후보 recall 을 바꿔 P4 게이트가 재는 값을 오염시킨다"(원칙8, journal 2026-09-05 23:45 DECISION 일치). 개정 1 은 범위를 넓히지 않았다 — 머리말 7행 "수용 기준 절과 카드(D3·D10·S3.3)는 변경 없음", 바뀐 것은 결정의 정밀화(3-c·4 갱신 주체·9 픽스처·10 사전 표)와 단위 분할뿐. |
| 2 | 불변 원칙 1~9 위반 없음 | **통과** | **원칙1**: `S3.3-er-pipeline.md` "T_merge 미만 자동 병합 금지(원칙1·2)", `entity-resolution/SKILL.md` "`T_merge` 미만에서 자동 병합이 절대 일어나지 않는가" ↔ 01-plan 28행 "`T_merge` 미만에서 자동 병합·자동 `create_person` 이 절대 일어나지 않는다" + **개정 1 신규** 28·140행 결정 3-c(b) "`matched_person_id=null` … 병합 대상 자체가 없으므로 merge 를 금지하고 `s_llm=0`" (초판 #2 미결 사유 (i) 의 null 경로가 닫힘), 27·139행 결정 3-c(a) "세 신호는 모두 LLM 이 고른 `matched_person_id` 후보 하나에 귀속" (초판 #2 미결 사유 (i) 의 귀속 — "최고 유사도 후보의 s_emb 로 B 를 병합" 하는 오병합 방향 부풀림이 사라짐), 29·131행 "완화로 통과한 위계 검사는 `rule_passed` 에 미통과로 센다(완화가 점수를 올려 주지 않는다)", 199행 리스크 "완화 재검색" 방어 (i)~(iv). **결정 2 배제 규칙 수정의 방향 판단(verifier)**: 엄격 단계가 인접 불일치도 탈락시키므로 완화 경로가 더 자주 발동하지만, 완화는 (i) 엄격 결과 0건일 때만·(ii) 위계 불일치**만**으로 탈락한 후보(29행)·(iii) 인접 1칸(`_is_hierarchy_adjacent`, `app/tools/persons.py` 110행 `== 1`)·(iv) `T_merge` 불변·(v) `s_rule` 에 미통과 계상(−0.2/3 = −0.067) — 완화된 후보는 같은 후보가 엄격 통과했을 때보다 **항상 낮은** confidence 를 받고 `relaxed_retry`·`relaxed_pass` 로 P4 가 따로 집계한다(199행 (iv)). 완화 자체가 merge 가능성을 0 에서 양수로 만드는 것은 S3.3 카드가 명령한 것("인접 위계까지 허용으로 완화한 재검색 1회")이므로 계획의 책임이 아니다 — 통과. 산술(evidence `20260905-2206-plan-review-arith.txt`): LLM 실패 상한 0.5 < 0.8, 힌트 없는 상한 0.8 = `T_merge`(202행 리스크로 P4 인계 — `rule_checked=0` merge 건 별도 집계). **원칙2**: `D10-two-thresholds.md` "임계치 하나로 구현하지 않는다. 두 값 모두 설정값이며 trace decision 에 어느 구간이었는지 남긴다" ↔ 28행, 172행 결정 8 "`0 ≤ T_new ≤ T_merge ≤ 1` 검증", 153~157행 `decision{band, band_by_threshold, T_merge, T_new}`, U4 스윕 테스트. `≥` 경계: 43행 "`≥` 는 merge, `≥ T_new` 는 identity" = D10. 부동소수 규약(28·201행 `round(·,6)` "또는 `isclose(1e-9)`")은 D10 과 충돌하지 않으나 두 갈래 중 `round(·,6)` 은 `T_merge−5e-7` 을 merge 로 넘긴다 — 원칙1 방향의 미세 결함, **권고 F-7fe239**(§3). **원칙3**: `D03-confidence-formula.md` "`s_llm`: LLM이 구조화 출력으로 자기보고한 0~1 (로그 확률 아님)"·"trace `confidence_breakdown{s_llm,s_emb,s_rule,weights,confidence}` 필수" ↔ 27행 "`judge.py` 모듈 docstring·`Judgement` 필드 주석·trace `llm` 객체에 명시", 150~152행 5키 + `matched_person_id`·`rule_checked`·`rule_passed`(D3 5키를 줄이지 않고 더한 것), 판정 방법 표 108행 "5키(D3 필수) + 귀속을 드러내는 `matched_person_id`". 회귀(a) 산술 verifier 재계산: `0.5·0.95 + 0.3·0.85 + 0.2·(2/3) = 0.86333 ≥ 0.8`(179행 "≈ 0.863" 일치, 완화 통과를 **미통과로 계상한 값**임을 `rule_passed=2` 로 확인, 여유 0.063). **원칙4**: `entity-resolution/SKILL.md` "절차(반드시 4단계)" ↔ 16행 "4단계가 각각 별도 모듈", 128행 결정 1, U6 `stages` 테스트; 규칙 통과 후보 0 → LLM 생략(34행)은 1·2단계가 돌고 `llm.skipped=true` 로 기록되므로 단일 호출 대체가 아니다; LLM 입력은 통과 후보뿐(U5 "입력 후보는 규칙 통과 후보만")이라 2단계가 실효한다 — 단 범위 검증 집합 표기가 133행 "후보 id 집합"/34행 "통과 후보 id 집합" 으로 갈려 **권고 F-5a97ef**. **원칙8**: 49~50행 "측정 대상이지 측정자가 아니다"·"테스트를 통과시키려고 임계치를 움직이지 않는다", 173행 `FakeJudge`·`grouped_embedder` 결정적, **개정 1 신규** 174~180행 결정 9 픽스처 확정(초판 #2 미결 사유 (iii) 닫힘 — `hierarchy:"동"` ↔ 유도 `상`, 단언 `decision.relaxed_retry is True` 로 "완화 없이 통과" 불가), 195행 `USER_RANK_ANCHOR` "환경변수·설정으로 노출하지 않는다 — 테스트를 통과시키려고 돌릴 수 있는 손잡이를 만들지 않기 위해서다", 211행 미결 5 "없는 증거를 있는 것처럼 쓰지 않는다". **원칙9**: `CLAUDE.md` "ER 단계의 `agent_traces.output` 에는 `candidates[]`, `confidence_breakdown{}`, `decision` 을 JSON으로" ↔ 144~165행 output 스키마(배제 후보 포함 130행 "배제된 후보도 trace `candidates[]` 에 `passed_rules=false`·`excluded_by` 와 함께"), 31행 "`tokens_in`/`tokens_out` 은 Anthropic 응답 `usage` 의 실제 값"; **개정 1 신규** 143행 갱신 주체(초판 #2 미결 사유 (ii) 닫힘 — `apply_resolution` 이 같은 `er_resolve` 행의 `applied`·`pending_question_id`·`applied_at` 세 필드만 부분 갱신, 판정 필드 불변, `agent-observability` 체크리스트 "`ask_user` 호출에 `pending_question_id` 가 연결되는가" 충족 방식 확정). 검증 방법의 빈틈(identity map 읽기·중복 apply·`llm_failed` 귀속·null 경로 파이프라인 테스트)은 **권고 F-93f063 F-8809f2 F-f3b245 F-1d65ac** — 카드 위반이 아니라 테스트 정밀도 문제라 착수를 막는 사유로 올리지 않는다. 원칙5·6·7 은 #1. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D01-new-person-confirm.md` "create_person 호출 경로는 반드시 answered pending_question 을 거친다" ↔ 26행 `apply_resolution` "identity/new_person 이면 `ask_user(...)`"(`create_person` 호출 없음), 28행. `D02-ask-user-async.md` "동기 대기(sleep/poll) 금지. ask_user 를 다른 툴에 합치지 않는다" ↔ 26·142행(`ask_user` 별도 툴 재사용, 저장 후 종료·재개는 P5 48행). `D04-embedding-provider.md` "EmbeddingProvider 인터페이스 뒤에 둔다(embed(texts), dimension)" ↔ 35행 "Protocol 에 `dimension` 추가", 168행 "호출 없이". `D05-alias-level-embedding.md` "인물당 대표 벡터를 만들지 않는다. 새 별칭이 확정되면 즉시 임베딩" ↔ 19행 "`search_person` 재사용(인물별 max)", 40행 merge 시 `update_person(new_alias=…)`(P2 `_add_alias` 가 즉시 임베딩), 36행 NULL 백필. `D06-display-name-policy.md` "update_person(display_name=…)은 사용자 확인(answered question)을 거친 경우에만. 별칭은 절대 삭제하지 않는다" ↔ 137행 결정 3-b "merge 는 별칭 누적까지만", 54행, 213행 "백필 스크립트는 삭제하지 않고". **개정 1 대조**: D6 서사 "팀장→부장 승진" ↔ 결정 10 표(팀장 rank 2 → `동`, 부장 rank 4 → `상`, 1칸) — 인접 완화 경로와 정합하고 `hierarchy` 값 집합(상/동/하, `app/tools/persons.py` `HIERARCHIES`)을 바꾸지 않으므로 스키마·CHECK 영향 없음. `D10` "trace decision 에 어느 구간" ↔ 153~154행 `band`·`band_by_threshold`(구간을 더 정확히 남김). `D03` 5키 ↔ 150~152행 — 초판이 미정으로 둔 `s_emb` 귀속은 결정 3-c 로 "LLM 이 고른 후보의 값" 으로 확정되어 D3 "`s_emb`: 후보 검색 코사인 유사도" 와 충돌 없음. 충돌 0. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.2-tools-v2.md` "Candidate = {person, similarity, aliases_matched, rule_flags} — 3단계 LLM 판정 입력" ↔ 5행 의존 문장; `update_person (person_id, facts?, new_alias?, display_name?)` ↔ 40행 `new_alias="부장님"`; `ask_user (kind, question, options, context)` ↔ 26행. `S3.3-er-pipeline.md` "3. LLM 판정 … → {matched_person_id \| null, s_llm, reason} (구조화 출력)" ↔ 32행·139행 결정 3-c(a) "S3.3 의 단일 `Judgement` 모델 그대로 — 후보별 점수 배열로 바꾸지 않는다"(초판 선택지 (B) 기각, 카드 갱신 불필요 — 141행 (c)); "승진 케이스: 2단계 위계 제약을 인접 위계까지 허용으로 완화한 재검색 1회. 재검색 여부 trace에 기록" ↔ 29행(1회·`relaxed_retry`·`hierarchy_relaxed_retry`), 200행 "재검색 = 규칙 재평가" 해석(P2 `search_person` 이 hints 로 배제하지 않으므로 결과 동일 — verifier 인정 유지, docstring·03-log 명시 조건); "회귀 테스트 필수: 승진(팀장→부장님) 연결, 팀장↔이모 배제, 동명이인 분리" ↔ 40~42행 (a)(b)(c) 1:1, (c) 는 단일 `Judgement` 모델에 맞게 고쳐짐("둘 중 하나를 `matched_person_id` 로 고르되 `s_llm` 을 중간값으로"). `S3.4-ask-user-protocol.md` "context 에는 재개에 필요한 것만(발화, 후보 id, 확신도 분해). 비밀·전체 대화 이력 저장 금지" ↔ 142행 `context {mention, utterance, candidate_ids, confidence_breakdown}`. `S3.7-eval-spec.md` "곡선: x = T_merge ∈ {0.5,…,0.95}, T_new=0.3 고정"·"calibration(s_llm 구간별 정답률)" ↔ 172행 config 인자 주입, 159행 `llm.s_llm`, 109행 재계산 절대오차 < 1e-9, **개정 1 신규** 163행 "`forced_reason` 이 `null` 인 행만 순수 산식 구간이며, 곡선은 그 행들로 재계산하고 강제 경로는 따로 집계"(초판 권고 F-4d1e21 반영 — S3.7 재계산 정확성 확보), 162행 후보별 `s_emb`·`s_rule` 원자료. 스키마 v2 무변경(117행 `alembic check`); `agent_traces.output` 은 `JSONB`(`app/db/models.py` 256행)라 부분 갱신이 스키마 변경 없이 가능. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `gitlog.sh P3-er S3.3`(2026-09-05 22:06): dev = main = `b676799` "docs(P2-tools): 완료 — verifier 04-review 완료 판정·사용자 승인", `packages/P2-tools/04-review.md` "결과: 완료 / 승인: 사용자 (2026-09-05)"; verify-plan 출력 `PASS 의존 완료: P2-tools`. `docs/backlog.md` P3 "의존: P2". P4 게이트(`backlog.md` "P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다")는 P3 에 적용되지 않으며 01-plan 5행이 이를 명시. P3-er 태그 커밋은 P1·P2 의 인계 문구 5건뿐(`a9cb254` 등 — 착수 커밋 없음), 미커밋 변경은 `HANDOFF.md`·`journal.md`·`packages/P3-er/`(위키 문서만, 제품 코드 0) — `git status` 2026-09-05 22:06. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P3 행 "수용기준: 승진 회귀 테스트 통과, trace에 `confidence_breakdown` 존재" ↔ 01-plan 98행 "- 승진 회귀 테스트 통과, trace에 `confidence_breakdown` 존재"; verify-plan `PASS backlog 일치`. 개정 1 머리말 "수용 기준 절 … 변경 없음". 판정 방법 표(104~122행)가 두 항목을 pytest `-k promotion`(106행 — 기대 단언에 "엄격 필터 탈락 → `decision.relaxed_retry is True` → `band="merge"`·`forced_reason=null`" 까지 명시)과 SQL `output->'confidence_breakdown'`(108행) 로 기계화. 초판이 "픽스처 미정이라 계획 보완 후 성립" 이라 한 조건은 결정 9(174~180행)로 충족 — **이제 기계적으로 판정 가능**. 신규 3행(F-ca12ad 재현 수단 전환·차원 사전 검출·경계 비교)은 모두 pytest `-k` 명령 + 기대 출력이고, "R4 닫힘 표기" 행은 명령이 아니라 04-review 기재 규약이다(기계 판정 항목이 아니라 보고 규약 — 허용). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan 출력 `PASS Refs 있음` U1~U9 9건. 각 Refs 에 `P3-er` + D/S/R/원칙 태그(U1 `S3.3 원칙9`, U2 `R9 D4 D5`, U3 `R4 D3 S3.3 원칙4`, U4 `R4 D3 D10 S3.3 원칙1 원칙2`, U5 `R4 R9 D3 D4 D5 S3.3`, U6 `R4 R9 D3 D10 S3.3 원칙1 원칙4 원칙9`, U7 `R4 R9 D1 D2 D6 D10 S3.3 S3.4 원칙1 원칙8 원칙9`, U8 `D4 D5 R9 원칙8`, U9 `R4 R9 D3 D10 S3.3 S3.7 원칙8 원칙9`). 단위 크기: 초판 권고 F-cab7d6 대로 구 U6 이 U6(`resolve`·trace·stages·no_side_effect·강등) / U7(`apply_resolution`·`grouped_embedder`·회귀 3종·applied 계약) 으로 분할됨 — 각 단위가 커밋 하나 크기. U2 가 가장 크지만(공급자 이동·Protocol·`check_dimension`·테스트 수단 전환·requirements) 한 주제(임베딩 런타임)라 허용. |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다"·"`os.environ[...]` 로 읽는다"·"로그·trace에 키·비밀을 남기지 않는다" ↔ 01-plan 32행 "키는 `os.environ` 으로만 SDK 에 전달하고 프롬프트·trace·예외 메시지 어디에도 넣지 않는다", 136행 결정 3(d), 135행 "trace `llm.error` 에 예외 유형만", 102행 "`.env` 는 읽지 않는다", 36·44행 backfill/er_smoke "키 없으면 종료 코드 2·키 문자열은 출력하지 않는다", **개정 1 신규** 35행·167행 "`_load_dotenv_quietly()` 는 그 스크립트에만 남기고 옮기지 않는다 … `app/embedding.py`·`app/settings.py`·`scripts/backfill_embeddings.py`·`scripts/er_smoke.py` 는 `.env` 를 읽지 않는다"(초판 권고 F-bad87c 반영, 04-review 확인 명령 `grep -n "dotenv" app/ scripts/` 제시). §4 "셸에서 DROP/TRUNCATE 금지" ↔ 213행 "테스트 정리는 rollback 으로만". §5 "context 에는 재개에 필요한 것만"·"모든 조회는 user_id 조건" ↔ 142·213행. 외부 전송은 SDK 호출(OpenAI·Anthropic)뿐. U9 README "환경변수 **이름**만, 값·키 금지". |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
소견 파일: 초판 `evidence/20260905-2035-plan-review-findings.txt`(필수 3·권고 7) → 이 개정 `evidence/20260905-2206-plan-review-findings-2.txt`(**FAIL 0**, WARN 6 신규) 를 `findings.py P3-er … --source review` 로 재투입 → 초판 10건 자동 해소(해결 단계 표에 개정 1 문단 위치를 verifier 가 기입), 신규 6건 등록(원인 분석·권장 해결 단계·완료 판정 명령까지 verifier 기입, 상태 대기(backend-agent)). 산술 evidence: `evidence/20260905-2206-plan-review-arith.txt`.

**초판 보류(필수) 3건 — 전부 닫힘.** 사용자 결정(journal 2026-09-06 00:10 DECISION)과 개정 1 문구 대조:
- **F-138665** 닫힘 — 결정 "LLM 이 고른 인물의 s_emb·s_rule, null 이면 s_llm=0·병합 금지(후보 있으면 identity, 없으면 new_person)" ↔ 01-plan 27행·28행·138~141행 결정 3-c (a)(b)(c) 문구 일치. 선택지 (A) 채택이라 S3.3 `{matched_person_id | null, s_llm, reason}` 그대로, 카드 변경 없음(141행 (c) 가 이를 명시). 회귀(c) 문장이 단일 `Judgement` 모델에 맞게 고쳐짐(42행). U4 "`matched_person_id=null` 이면 `band != "merge"`" 테스트 존재.
- **F-f43a9d** 닫힘 — 결정 "apply_resolution 이 er_resolve 같은 행에 applied·pending_question_id·applied_at 갱신" ↔ 26행·143행·164행, 산출물 `Resolution.trace_id`, U6 초기값 세 필드, U7 "같은 trace 행에서 `pending_question_id` 를 조회할 수 있고 판정 필드는 그대로다"·"행 수는 여전히 판정당 1", 판정 방법 표 `-k applied`. 대안 (B)(C) 기각 근거 143행. 결정 5 "행 1개" 계약 유지.
- **F-8c6354** 닫힘 — 결정 "픽스처 인물 hierarchy=동, 호칭 사전이 부장님→상 유도 → 1칸 차이 완화 경로" ↔ 40행·174~180행 결정 9(`hierarchy:"동"`, `hints=None`, 기대 경로 "엄격 필터 탈락(통과 후보 0) → 완화 재평가 1회 → 통과", `rule_checked=3`·`rule_passed=2`) + 181~196행 결정 10 표(`USER_RANK_ANCHOR=2`; 사원/대리 → 하, 과장/팀장 → 동, 차장 이상 → 상; 팀장 rank 2 → `동`, 부장 rank 4 → `상`). verifier 산술 `0.8633 ≥ 0.8`(완화 통과 미통과 계상 기준, 여유 0.063). `USER_RANK_ANCHOR` 미노출 근거 195행(원칙8), 사전에만 있고 `HIERARCHIES` 3값 불변이라 스키마 영향 없음, 리스크 203행이 기준선 가정의 실패 방향(질문 증가 — 오병합 아님)을 적음.

**초판 권고 7건 — 전부 개정 1 에 반영되어 닫힘**(05-remediation 해결 단계에 문단 위치 기입): F-4d1e21(31·153~155·163행 `band_by_threshold`/`forced_reason` 분리), F-3ca6b5(37행·U1(iii)·U2·판정 방법 표 2행 — U1 시점 1535차원 → U2 이후 NOT NULL 위반으로 재현 수단 전환, 두 테스트 유지), F-acc9b9(29·131행 미통과 계상 + `relaxed_pass`), F-cab7d6(U6/U7 분할, U1~U9), F-5aaf28(판정 방법 표 R4 행·미결 5 "실호출 미검증" 이중 표기), F-bad87c(35·167행 dotenv 비이동), F-05cbf1(34행 "후보 0건 = 2단계 규칙 통과 후보 0건" 정의 문장).

**이 개정에서 새로 발견한 것 — 권고(WARN) 6건, 보류 아님.** 카드 위반이 아니라 개정 1 이 새로 연 경로의 구현 규약·테스트 정밀도 문제이며 구현 단위(U4~U7)에서 03-log 한 줄 + 테스트로 닫을 수 있다. 계획 문구 재개정은 요구하지 않는다.
- **F-7fe239** 임계치 비교 허용오차가 두 갈래(`round(·,6)` / `isclose(1e-9)`). `round(·,6)` 은 `T_merge−5e-7` 을 merge 로 판정해 원칙1 방향과 반대이고 U4 스윕 테스트(원값 `< T_merge` → `band != merge`)와 모순될 수 있다. 실제 필요한 것은 표현 오차만 흡수하는 1e-9 급(`0.5·0.8+0.3·1+0.2·0.5 = 0.7999999999999999` 가 그 사례). 권장: 비교 함수 하나를 `confidence.py` 단일 출처로 두고 두 테스트가 같은 함수를 쓴다.
- **F-93f063** `apply_resolution` 의 JSONB 부분 갱신 테스트가 같은 세션 identity map 으로 읽으면 in-place dict 변경이 flush 되지 않아도 통과한다(`app/db/models.py` 256행 `JSONB`, `MutableDict` 없음). 권장: `jsonb_set`/`||` 또는 `flag_modified`, 테스트는 `expire_all` 후 원시 SQL 재조회.
- **F-8809f2** 같은 `Resolution` 으로 `apply_resolution` 을 두 번 부를 때의 계약이 없다 — merge 는 upsert 라 무해하나 identity/new_person 은 `pending_questions` 2행. 권장: `decision.applied=true` 면 거부, 테스트 1건.
- **F-f3b245** `llm_failed` 경로의 `s_emb`·`s_rule` 귀속 미정(결정 3-c 는 null 경로만 0 으로 정함). band 는 identity 강제라 오병합 위험은 없고 S3.7 재계산 일관성 문제. 권장: null 과 같은 분해(세 신호 0, `matched_person_id=null`).
- **F-5a97ef** 범위 검증 집합 표기가 133행 "후보 id 집합"/34행 "통과 후보 id 집합" 으로 갈림. 권장: 통과 후보 집합으로 통일하고 범위 밖 id 는 `llm.error` 유형으로 API 장애와 구분.
- **F-1d65ac** 결정 3-c(b) null 경로의 파이프라인 테스트가 U6·판정 방법 표에 없다. 또 통과 후보 0 → LLM 미호출이므로 null 은 통과 후보 ≥1 에서만 생겨 "없으면 `new_person`" 가지는 도달 불가 — 테스트한 것으로 세지 말 것. 권장: `-k no_matched` 케이스 1건.

**registry WARN 8건**(F-fdb56f F-b3d90e F-149891 F-ef1fb8 F-2c37bd F-127d01 F-b266cb F-0ffff5)은 기존 행 비고 갱신 계획(212행)으로 의도된 것 — **U9**(개정 1 재매김, 05-remediation 의 "대기(U8)" 표기를 U9 로 정정) 후 `grep -c` 행 수 불변으로 닫는다. F-033bb1("보류 1건")은 이 개정의 #2 통과로 자동 해소.

**확인해 통과로 본 것(사용자 결정 대조)**: journal 2026-09-06 00:10 DECISION 3항목 모두 개정 1 의 결정 3-c·4·9·10 에 문구 그대로 반영. journal 23:45 DECISION 6항목(초판 확인)은 개정 1 에서 바뀌지 않음(26·31·35·51·72·137·211행). 개정 1 이 "하지 않는 것"(46~55행)을 늘렸을 뿐 줄이지 않았다.

## 4. 결정
결과: 통과 — 초판 필수 소견 3건은 사용자 결정대로 개정 1 에 반영되었고 카드 변경·CR 없이 닫힌다(§3). 기계 검증 FAIL 0, 보류 0(§1). 신규 권고 6건은 구현 단위(U4~U7)에서 03-log·테스트로 닫고 04-review 가 완료 판정 명령 출력으로 확인한다 — 착수 조건이 아니다.
승인: 사용자 (2026-09-06)
