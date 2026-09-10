# P3-baselines · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-10 10:45 · docs(P3-baselines): 계획·계획검증 승인, 패키지 착수 — 베이스라인 3종 + 공통 Resolver 인터페이스 · pending
- 변경: `01-plan.md`(architect 초안 + 결정 확정 A~H·I·J), `02-plan-verify.md`(verifier 통과, 권고 R-1~R-9, `승인: 사용자 (2026-09-10)`), `05-remediation.md`(F-cf1510 해소·F-0ffff5 의도된 WARN 열림), `evidence/20260910-1029-verify-plan.txt`·`20260910-1036-verify-plan-final.txt`, `CURRENT.md active: P3-baselines`, `docs/backlog.md` 41행 세분화 줄 U1~U8, 이 로그
- 이유(기획서·카드 연결): backlog 41행 "베이스라인 3종 … 제안 방식과 동일 인터페이스로 호출 가능". S3.7·eval-harness §3 "동일 데이터·동일 지표" 의 배관. P4 게이트의 입력을 만든다
- 정합성 확인: 원칙4(대비군은 `evaluation/` 격리, `app/` 변경은 결정 J 1건 예외) / 원칙8(베이스라인 약화 금지 장치: 결정 B·C·E) / 원칙1·2·D10(`identity` 어휘·`band_for`·`ERConfig` 재사용) / S3.1·S3.2 무변경 / security(키·프롬프트 미출력, 실호출 사용자 실행) — 위반 없음
- 남은 것 · 다음 단위: **U1 공통 인터페이스** eval-agent(L-004 승인 후). U5 전에 결정 I·J 반영. 권고 R-1·R-2(U7·U8), R-4(U5·U8), R-6·R-7(U6), R-8(U3) 을 각 단위 위임 프롬프트에 넣는다
- Refs: P3-baselines S3.7 S3.3 D3 D4 D5 D10 원칙4 원칙8 L-002 L-004

## 2026-09-10 13:58 · feat(P3-baselines): U1 공통 Resolver 인터페이스·방식 표 — evaluation/ 패키지 신설, 불변 규약 4개, 계약 테스트 39건 · 05d90f0
- 변경: `evaluation/__init__.py`(패키지·의존 방향 R-2 명문화), `evaluation/resolvers/base.py`(`DECISIONS`·`ResolverCandidate`·`MentionDecision`·`Resolver` Protocol, 불변 규약 4개 docstring), `evaluation/resolvers/registry.py`(`RESOLVERS`·`register`·`get_resolver`·`ALL_METHODS` 동적, 예약 이름 5개), `evaluation/resolvers/__init__.py`(공개 진입점, U2~U5 import 자리), `tests/test_baseline_base.py`(39건), `registry.md` 5행, evidence `20260910-1358-u1-pytest.txt`(39 passed)·`20260910-1358-u1-isolation.txt`(`app/` 변경 0줄·`grep evaluation app/` 0줄·U1 `ALL_METHODS` 빈 튜플), journal(PUSH·RELEASE 줄), HANDOFF, 이 로그
- 이유(기획서·카드 연결): 01-plan U1 "공통 인터페이스·방식 표" — S3.7·eval-harness §3 "동일 데이터·동일 지표" 는 **동일 호출**이 먼저 성립해야 한다. 결정 A(i) `evaluation/` 최상위, 결정 B(i) `supported_decisions`, D10 `band_for` 어휘·`ERConfig` 재사용
- 정합성 확인: 원칙1·2(`person_id` 는 `merge` 에서만 — `__post_init__` 강제) / 원칙4(`app/` diff 0줄, 역방향 import 0줄 = R-2 를 U1 에서 선반영) / 원칙8(빈 표에 자리표시자 없음, 예외 비대칭 금지 규약) / security(키·네트워크·DB 없음) — 위반 없음
- 남은 것 · 다음 단위: **U2 제안 방식 어댑터**(`evaluation/resolvers/proposed.py`, `app.er.resolve` 호출만, `app/er/` 무수정) eval-agent(L-004 승인 후). U1 시점 `ALL_METHODS` 는 빈 튜플이며 U2 가 첫 등록. R-1(U7·U8)·R-4(U5·U8)·R-6·R-7(U6)·R-8(U3) 유지
- Refs: P3-baselines S3.7 D10 원칙1 원칙2 원칙4 원칙8 R-2 L-002 L-004

## 2026-09-10 14:20 · feat(P3-baselines): U2 제안 방식 어댑터 — app.er.resolve → MentionDecision 변환, "proposed" 등록, 테스트 20건 · f212ad6
- 변경: `evaluation/resolvers/proposed.py`(`ProposedResolver` + 순수 변환 `to_mention_decision`, `register("proposed")`, `judge`·`config` 팩토리 인자), `evaluation/resolvers/__init__.py`(U2 import 자리 → 실제 import, `ALL_METHODS == ('proposed',)`), `tests/test_baseline_proposed.py`(20건: 세 밴드 변환·부수효과 0(`person_aliases`·`pending_questions` 행 수 불변)·`get_resolver` 경로·규약·도달 불가 조합 강등 4건), `registry.md` 2행, evidence `20260910-1411-u2-pytest.txt`(59 passed, skip 0)·`-u2-regression.txt`(er_pipeline·er_judge 54 passed)·`-u2-isolation.txt`(`app/` 0줄·역방향 import 0줄·`ALL_METHODS`)·`-u2-pytest-all.txt`(전체 526 passed), 이 로그(U1 항목 해시 05d90f0), journal(U1 COMMIT 줄), HANDOFF
- 이유(기획서·카드 연결): 01-plan 54행·101행 U2 "제안 방식 어댑터 … `app/er/` 는 한 줄도 고치지 않는다". S3.3 4단계 결과를 S3.7 "동일 인터페이스" 로 옮긴다(결정 G). D10 `ERConfig` 그대로 전달
- 정합성 확인: 원칙1·2(`person_id` 는 `merge` 에서만, `apply_resolution` 미호출 — 테스트가 행 수 단언) / 원칙4(`app/` diff 0줄·역방향 import 0줄) / 원칙9(`trace_id`·`confidence_breakdown`·`excluded_by` 를 `detail` 에 보존) / 원칙8(도달 불가 조합은 예외 대신 강등 + `adapter_forced_reason`, 규약 2) — 위반 없음
- eval-agent 판단 4건(verifier 04-review 확인 대상): (1) `trace_id` 를 전용 필드와 `detail` 양쪽에(출처 하나, 테스트가 동일성 단언) (2) 후보별 `score` 는 판정된 인물만 `confidence`, 나머지 0.0(제안 방식은 후보별 결합 확신도를 내지 않음, P3-er 결정3) (3) 문자열 `excluded_by` 는 `signals`(float) 대신 `detail`, bool `rule_flags` 6개는 1.0/0.0 (4) 계획에 없던 `detail` 키 추가 `band_by_threshold`·`confidence_breakdown`·`ask_kind`·`llm_skipped/attempts/error` — 판정을 바꾸지 않고 `Resolution` 값을 옮기기만 함
- 남은 것 · 다음 단위: **U3 완전일치 2변형**(`exact_raw`·`exact_norm`, 결정 C(iii), R-8) eval-agent(L-004). 이후 U4 임베딩 단독 → U5 LLM 단일(결정 I·J) → U6 적재기 → U7 parity → U8 evidence·README → verifier 04-review
- Refs: P3-baselines S3.3 S3.7 D3 D10 원칙1 원칙4 원칙8 원칙9 R-2 L-002 L-004

## 2026-09-10 14:35 · feat(P3-baselines): U3 문자열 완전일치 베이스라인 2변형 — exact_raw·exact_norm 등록, 순수 함수 분리, 테스트 61건 · pending
- 변경: `evaluation/resolvers/exact_match.py`(순수 `match_exact(mention, persons, *, normalizer)` + DB 조회 `load_known_persons(ctx)` 분리, `to_mention_decision`, `ExactRawResolver`(`exact_raw`, strip+casefold)·`ExactNormResolver`(`exact_norm`, `app.er.dictionary.normalize()`+casefold 를 mention·별칭·표시 이름 양쪽에, R-8), 1→`merge`(1.0)/2+→`identity`(`person_id` None)/0→`new_person`, 빈 문자열→`forced_reason="empty_after_normalize"`), `evaluation/resolvers/__init__.py`(U3 import, `ALL_METHODS == ('proposed','exact_raw','exact_norm')`), `tests/test_baseline_exact_match.py`(61건: 순수 함수 1/2/0건·공백 대소문자·"김팀장"↔"팀장" raw 불일치/norm 일치·대칭성·상위집합·DB 동명이인→identity·승진 호칭→new_person·부수효과 0·`ctx.embedder=None` 에서도 완전 판정), `registry.md` 2행, evidence `20260910-1423-u3-pytest.txt`(120 passed, skip 0)·`-u3-isolation.txt`(`app/` 0줄·역방향 import 0줄·`ALL_METHODS`), 이 로그(U2 항목 해시 f212ad6), journal(U2 COMMIT 줄), HANDOFF
- 이유(기획서·카드 연결): 01-plan 55행·102행 U3, 결정 C(iii) "두 변형 모두 등록 … P4 가 둘 다 보고" — 약한 베이스라인만 보고하지 않는다(원칙8). 동명이인은 임의 선택 없이 `identity`(원칙1). R-8 양쪽 정규화
- 정합성 확인: 원칙1(동명이인 2건 `identity`, `person_id` None — 테스트 단언) / 원칙4(`app/` 0줄·역방향 import 0줄) / 원칙8(강한 변형 `exact_norm` 함께 등록, 예외 비대칭 금지 공통 경로) / S3.7(임베딩·LLM·규칙·임계치 미사용, `uses_*` 전부 False) — 위반 없음
- eval-agent 판단 6건(verifier 04-review 확인 대상): (1) **R-8 의 예시 "님" 단독은 `normalize()` 가 빈 문자열을 내지 않는다**(`dictionary.py:154` 접미 제거 조건 `len > len(suffix)`) → 일치 0건 분기로 감. 빈 문자열은 `""`·공백뿐·None 뿐. 테스트로 사실을 고정, `app/` 미수정 (2) 빈 문자열 규칙을 `exact_raw` 에도 동일 적용(공통 경로, 분모 불변) (3) `normalize_dictionary` 에 `casefold()` 추가 → `exact_norm` ⊇ `exact_raw` 테스트로 단언 (4) `identity` 의 `score` 1.0 = "문자열은 맞았으나 특정 못 함", 확신도 아님 — docstring 에 P4 축 분리 명시 (5) `new_person` 의 `candidates` 빈 목록, 기록용 `detail` 키(`variant`·`normalized_mention`·`match_count`·`matched_person_ids`·`matched_names`·`ask_kind`·`uses_*`) (6) `load_known_persons` 는 `embedding IS NULL` 별칭도 포함(`search_person` 과 다름)
- 남은 것 · 다음 단위: **U4 임베딩 단독**(`embedding_only`, `search_candidates` + `band_for`, 결정 D(i) `s_emb` 에 `T_merge`/`T_new` 그대로) eval-agent(L-004). 이후 U5(결정 I·J, R-4) → U6 → U7 → U8 → verifier
- Refs: P3-baselines S3.7 원칙1 원칙4 원칙8 R-8 R-2 L-002 L-004
