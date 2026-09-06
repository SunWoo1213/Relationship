# P3-er · 완료 검토 (04-review)

날짜: 2026-09-06 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트(L-002). 코드·계획·카드·registry·backlog·CURRENT·review-index 는 고치지 않았다. 이 문서·05-remediation(상태 판정·신규 소견 원인 분석)·evidence/`20260906-1439-review-*` 만 썼다. 실 LLM·임베딩 API 는 호출하지 않았고 `.env` 는 열지 않았다.

검토 대상: 01-plan(개정 2, U1~U9 전부 [x]) · 02-plan-verify · 03-log 11 항목(착수 bb1abfe, U1 2b82882, U2 2c63c60, U3 02e6f14, U4 593c254, U5 b1f2782, U6 d6e5949, U7 cc5d24f, U8 107ace3, FIX a807364, U9 b3bcc2d) · 05-remediation 소견 26 → 32 · evidence 77 파일 · 코드 `app/er/*`(8) `app/embedding.py` `app/settings.py` `app/tools/context.py` `app/tools/persons.py` `scripts/backfill_embeddings.py` `scripts/er_smoke.py` 테스트 12 · 카드 D3·D5·D10·S3.3·S3.7 · CLAUDE.md 원칙 1~4·8·9.

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh P3-er | tee docs/wiki/packages/P3-er/evidence/20260906-1439-review-verify-impl.txt`
```
== verify-impl P3-er  (20260906-1439) ==
ss...ssssssssssssssssssssssssssssssssssssssssssssssssssssssss.ssssssssss [ 90%]
ssssssssssssssssssssssssss............                                   [100%]
248 passed, 150 skipped in 6.60s
PASS  pytest 통과 → evidence/20260906-1439-pytest.txt
PASS  compileall 통과 → evidence/20260906-1439-lint.txt
PASS  태그 P3-er 커밋 16 건 → evidence/20260906-1439-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: D6
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: R9
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.7
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P3-er 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=1 → evidence/20260906-1439-summary.txt ==
```
- WARN 1 = 이 문서 부재(작성 전 실행). FAIL 0.
- **하네스 한계 확인(03-log U9 관찰이 사실인지)**: `verify-impl.sh` 33행은 `python -m pytest -q "$@"` 로 `POSTGRES_PORT`·`-rs` 없이 부른다(스크립트 직접 읽음). 그래서 실 DB 테스트 150건이 조용히 skip 된다(위 출력 `150 skipped`). 이 skip 은 P2 04-review 관찰 O4·01-plan 리스크 "실 DB 테스트가 조용히 skip 된다" 와 같은 원인이며, **수용 기준의 실제 증거는 아래 직접 실행**이다.
- 직접 실행: `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` → **398 passed, skip 0, exit=0** (`evidence/20260906-1439-review-pytest-all.txt`). 03-log U9 의 398 과 일치.
- 이 문서 작성 후 최종 재실행: `bash .claude/scripts/verify-impl.sh P3-er` → `PASS 검토자 = verifier (L-002)` · `PASS 증거 확인` 2행 · **FAIL=0 WARN=0** (`evidence/20260906-1452-review-verify-impl-final.txt`, 스크립트 내부 ts 20260906-1455 → `evidence/20260906-1455-{pytest,lint,commits,summary}.txt`).

## 2. 수용 기준 대조
backlog P3 행 문장: "승진 회귀 테스트 통과, trace에 `confidence_breakdown` 존재" (docs/backlog.md 31행 = 01-plan 98행, 글자 그대로 일치 확인).

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 승진 회귀 테스트 통과 | evidence/20260906-1439-review-pytest-k-promotion.txt (1 passed), evidence/20260906-1439-review-pytest-k-promotion_or_aunt_or_homonym.txt (3 passed), evidence/20260906-1439-review-mutation.txt (변이 C 에서 이 테스트가 실패 = 완화 경로를 실제로 검사), tests/test_er_pipeline.py, cc5d24f | 통과 |
| trace에 `confidence_breakdown` 존재 | evidence/20260906-1439-review-promotion-trace-sql.txt (판정 방법 표 SQL 1행), evidence/20260906-1439-review-trace-full-recompute.txt (verifier 자체 원시 SQL — output 전체·재계산 abs diff 0.000e+00), evidence/20260906-1439-review-pytest-k-applied.txt, d6e5949 | 통과 |

## 2b. 수용 기준 세부 대조 (단언·SQL — verify-impl 의 증거 열 검사 대상 표는 위 §2 뿐이다)

### (a) 승진 회귀 — 테스트 코드에 실제로 단언된 것 (tests/test_er_pipeline.py 410~478행 직접 읽음)
결정 9 픽스처 항목별 단언 여부:

| 결정 9 항목 | 테스트 코드 | 판정 |
|---|---|---|
| 저장 인물 `{"김민수", 직장, hierarchy="동"}`, 별칭 팀장·김팀장 | 422~424행 `_make_person(..., relation_tag="직장", hierarchy="동")`, `_add_alias` 2회 | 픽스처 일치 |
| `mention="부장님"`, `hints=None` | 429행 `resolve(ctx, "부장님", "...", judge=judge, config=ERConfig())` — hints 미전달 | 일치 (유도 hints = `{'relation_tag':'직장','hierarchy':'상'}` 를 verifier probe 가 확인) |
| 엄격 필터 탈락 → 완화 1회 | 433행 `result.decision["relaxed_retry"] is True`, 435행 `candidate.relaxed_pass is True` | 단언됨. `run_rule_stage` 는 `strict_passed` 가 비어 있을 때만 `True` 를 돌려주므로(app/er/rules.py 177~193행) 이 단언이 곧 "엄격 탈락" 의 증거. verifier probe: 엄격 단계 단독 실행 결과 `passed_rules=False, excluded_by='hierarchy_conflict'` |
| `rule_checked=3`·`rule_passed=2`·`s_rule≈0.667` | 436~438행 `== 3`, `== 2`, `abs(s_rule - 2/3) < 1e-9` | 단언됨 |
| `s_emb ≈ 0.85` | 439행 `candidate.s_emb >= 0.8` | **하한만 단언**(≈0.85 는 미단언). 실측 0.8494 (trace SQL evidence) |
| `s_llm=0.95` | 442행 `== 0.95` | 단언됨 |
| `confidence ≈ 0.863 ≥ T_merge` | 443~444행 `>= 0.8`, `abs(confidence - 0.863) < 0.01` | 단언됨. 실측 0.8631408499792709 |
| `band="merge"`·`forced_reason=null` | 445~446행 | 단언됨 |
| 별칭 "부장님" 추가 | 458~462행 `"부장님" in aliases` (SELECT 재조회) | 단언됨 |
| `display_name` 무변경 | 464~466행 `expire_all()` 후 `== "김민수"` | 단언됨 (+ `-k display_name_unchanged` 별도 1건) |
| `hierarchy=동` 이 아니면 항상 통과하는 테스트(F-8c6354) | 변이 C: `rules._evaluate` 엄격 단계에서도 인접 위계를 통과로 바꾸자 이 테스트가 **실패**(relaxed_retry False) → 완화 경로를 실제로 탄다 | 확인 |

미단언 항목은 `s_emb ≈ 0.85` 의 근사값뿐이며(하한 0.8 만), confidence ≈0.863 단언이 그 값을 간접 고정한다. 판정 방법 표(01-plan 106행)의 단언 목록은 전부 코드에 있다.

### (b) trace `confidence_breakdown` — 원시 SQL 대조
- 판정 방법 표 SQL(`SELECT step, tool_name, output->'confidence_breakdown', output->'decision', tokens_in, tokens_out … WHERE step='er_resolve' AND session_id=:sid`) 1행: `step='er_resolve'`, `tool_name='er'`, `confidence_breakdown` = `{s_llm:0.95, s_emb:0.8493583888197921, s_rule:0.6666666666666666, weights:{llm:0.5,emb:0.3,rule:0.2}, confidence:0.8631408499792709, matched_person_id, rule_checked:3, rule_passed:2}` — D3 필수 5키 + `matched_person_id` + `rule_checked/rule_passed` 전부 존재. `decision` 에 `band="merge"`·`band_by_threshold="merge"`·`forced_reason=null`·`relaxed_retry=true`·`hierarchy_relaxed_retry=true`·`applied=true`·`pending_question_id=null`·`applied_at` (evidence/20260906-1439-review-promotion-trace-sql.txt).
- 판정 방법 표 SQL 은 `llm` 객체를 선택하지 않으므로 verifier 가 `SELECT … output` 전체를 별도 조회: `llm = {provider:"fake", model:null, self_reported:true, s_llm:0.95, reason:"fake", tokens_in:0, tokens_out:0, attempts:1, skipped:false, error:null}` — `provider`/`model`/`self_reported` 존재 (evidence/20260906-1439-review-trace-full-recompute.txt). `model=null` 은 FakeJudge 규약(실 공급자는 응답 `model` 을 넣는다, judge.py 274·363행).
- **재계산(S3.7)**: trace 값만으로 `0.5·0.95 + 0.3·0.8493583888197921 + 0.2·0.6666666666666666 = 0.8631408499792709`, trace `confidence = 0.8631408499792709`, **abs diff = 0.000e+00 (< 1e-9)**. 가중치 합 1.0. `-k recompute` 테스트도 1 passed (evidence/20260906-1439-review-pytest-k-recompute.txt).
- `-k stages` 1 passed(4단계 산출물 키 전부 존재), `-k applied` 2 passed(원시 SQL 로 세 필드만 변경·판정 필드 JSON 동일·행 수 1).

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
| 케이스 | 명령 | 증거 |
|--------|------|------|
| (i) `T_merge` 미만 자동 병합 경로 없음 | `python -m pytest tests/test_er_confidence.py -q -k threshold`; 코드 읽기 `app/er/confidence.py` `band_for`(86~90행: `ge_with_tolerance` 두 번 → merge/identity/new_person), `_forced_decision`(176~223행: `band = "identity" if passed else "new_person"` — merge 리터럴 없음), `decide`(255~340행) | 4 passed(2000조합×3 스윕) evidence/20260906-1439-review-pytest-k-threshold.txt. `"merge"` 문자열을 만드는 코드 지점은 confidence.py 87행(band_for) 하나뿐 evidence/20260906-1439-review-grep-principles.txt. 변이 B(_forced_decision identity→merge) 7건 실패 evidence/20260906-1439-review-mutation.txt |
| (ii) `matched_person_id is None` 인데 merge | `decide` 295~296행 null → `_forced_decision("no_matched")`, 284~290행 `judgement is None`+`llm_failed=False` → `InvalidValue`; `apply_resolution` 374~377행 merge 인데 `matched_person_id is None` → `InvalidValue` | `-k null_path` 1 passed evidence/20260906-1439-review-pytest-k-null_path.txt. 변이 D(null 분기를 첫 후보 귀속으로 우회) 3건 실패 evidence/20260906-1439-review-mutation.txt |
| (iii) `round(` 기반 임계치 비교 없음(F-7fe239) | `grep -n "round(" app/er/*.py app/settings.py` | 매치 6건 전부 docstring/주석(호출 코드 0), 비교 지점은 `ge_with_tolerance` 55행 `a >= b or math.isclose(a, b, abs_tol=1e-9)` 하나. confidence.py 밖(`pipeline/rules/candidates/judge`)에 `t_merge/t_new` 참조 0건 = 이중 출처 없음 evidence/20260906-1439-review-grep-principles.txt. 변이 A(`>` 로 교체) 3건 실패 |
| (iv) 4단계 생략·LLM 단일 호출 경로 없음(원칙4) | `app/er/pipeline.py _run_pipeline` 158~236행: `search_candidates` → `run_rule_stage` → (`passed` 있을 때만) `judge.judge` → `decide` 순서 고정, `grep -nE "def (decide\|combine\|band_for\|apply_rules\|run_rule_stage\|validate_judgement)" app/er/pipeline.py` | 재구현 0건 evidence/20260906-1439-review-grep-principles.txt. LLM 생략은 통과 후보 0 일 때만(179·182행, `llm.skipped=true` — 계획된 예외) `-k no_candidates` 1 passed evidence/20260906-1439-review-pytest-k-no_candidates.txt. `-k stages` 1 passed |
| (v) `resolve()` 가 persons/person_aliases/pending_questions 를 쓰지 않음 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k no_side_effect`; `grep -nE "ask_user\(\|update_person\(\|create_person\(\|session\.add\(\|\.delete\(\|\.commit\("` app/er 5모듈 | 1 passed evidence/20260906-1439-review-pytest-k-no_side_effect.txt. 쓰기 호출은 `pipeline.py` 378행(`update_person`)·391행(`ask_user`) 두 곳뿐이며 둘 다 `apply_resolution` 안 evidence/20260906-1439-review-grep-principles.txt |
| (vi) merge 구간 `display_name` 무변경(결정 3-b) | `-k display_name_unchanged`; `grep -n display_name app/er/pipeline.py` | 1 passed evidence/20260906-1439-review-pytest-k-display_name_unchanged.txt. `update_person` 호출(378~382행)에 `display_name` 인자 없음, `suggested_display_name` 으로만 인계. verifier probe: merge 후 `display_name='김민수'`, aliases `['팀장','김팀장','부장님']` evidence/20260906-1439-review-trace-full-recompute.txt |
| (vii) 키·`.env` | `grep -rn dotenv app/ scripts/backfill_embeddings.py scripts/er_smoke.py` → 0; `os.environ[…API_KEY]` 값 읽기 — `app/embedding.py:153`·`scripts/backfill_embeddings.py:124` 는 `if not os.environ.get("OPENAI_API_KEY")` **존재 검사만**(값을 변수·출력으로 옮기지 않음), 그 외 0; evidence·README·app·scripts·tests 에 실제 키 형식 문자열(`sk-…{10,}`/`AKIA…`) 0건 — 단 `tests/test_er_judge.py:505·526` 의 더미 `"sk-test-dummy"` 는 형식 미달 더미(→ F-46f1eb 권고) | evidence/20260906-1439-review-grep-principles.txt. 키 없이 `er_smoke.py` → rc=2 안내(anthropic·openai 둘 다), 키·프롬프트 미출력 evidence/20260906-1439-review-tools-alembic-scripts.txt |
| (viii) `apply_resolution` 중복 호출 거부·trace 부분 갱신이 판정 필드를 바꾸지 않음 | `-k applied`, `-k double_apply` | 2 passed / 1 passed evidence/20260906-1439-review-pytest-k-applied.txt, evidence/20260906-1439-review-pytest-k-double_apply.txt. 구현 `pipeline.py` 362~366행 `AlreadyApplied` 즉시 raise. 보조 관찰: `validate_judgement` 가 bool 형 id 를 통과시킴(`True` 반환 확인, → F-036185 권고) |
| (ix) 툴 7종 시그니처·스키마 무변경 | `python scripts/tools_check.py`; `POSTGRES_PORT=5433 python -m alembic check`; `git diff --stat bb1abfe..b3bcc2d -- alembic/ app/db/models.py` | `RESULT: 7/7 ok` exit 0; `No new upgrade operations detected.` exit 0; diff 빈 출력(스키마 파일 무변경, 마지막 revision 커밋은 P1 09c2bd1) evidence/20260906-1439-review-tools-alembic-scripts.txt |
| 백필 dry-run 쓰기 0 | `POSTGRES_PORT=5433 python scripts/backfill_embeddings.py --dry-run` | `대상 별칭 0건 … 쓰기 0건` exit 0 evidence/20260906-1439-review-tools-alembic-scripts.txt |
| LLM 실패 강등 | `-k llm_failed` | 1 passed(`forced_reason=llm_failed`, `band=identity`) evidence/20260906-1439-review-pytest-k-llm_failed.txt |

**변이 검사 4종 요약**(evidence/20260906-1439-review-mutation.txt — 원본을 scratchpad 에 복사해 두고 각 변이 후 `cp` 원복, sha256 `77f7d08f…`/`0479901a…` 원복 확인, `git status --short app/er/` 빈 출력):

| 변이 | 죽인 테스트 |
|---|---|
| A `band_for`: `ge_with_tolerance(confidence, t_merge)` → `confidence > t_merge` | 3 failed — `test_boundary_exactly_t_merge_is_merge`, `test_boundary_t_merge_minus_5e10_is_merge_within_tolerance`, `test_threshold_sweep_uses_same_comparison_function_as_boundary` |
| B `_forced_decision`: `"identity" if passed` → `"merge" if passed` | 7 failed — 스윕 null·llm_failed 2, `decide` null/llm_failed/out_of_range 3, 파이프라인 `llm_failed`·`null_path` 2 |
| C `rules._evaluate`: 엄격 단계에서도 인접 위계 통과 | 3 failed — `test_promotion_fixture_relaxes_and_merges_with_conservative_scoring`, `test_relaxation_attempts_at_most_once`, **`test_apply_resolution_promotion_connects_via_relaxed_retry_promotion`** |
| D `decide`: null 분기 제거(첫 통과 후보로 귀속) | 3 failed — `test_threshold_sweep_null_matched_person_id_never_merges`, `test_decide_null_matched_person_id_with_passed_candidates_is_identity`, `test_resolve_null_matched_person_id_forces_identity_not_new_person_null_path` |

네 변이 모두 잡혔다 — 원칙 1·2·4 를 지키는 테스트가 "항상 통과하는 테스트" 가 아님을 확인.

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
review-index.md 는 이 검토에서 바꾸지 않았다(메인 세션이 `/devlog done` 에서). 현재 상태: R4 `해소(문서)`, R9 `구현완료(4dfaf33, 09c2bd1 …)`. F-5aaf28 규약대로 두 줄로 나눠 적는다.

- **R4** ("LLM 출력 확률"은 Claude API 에 없음 → 자기보고 `s_llm` 구조화 출력, D3)
  - (i) **구조화 출력 스키마·파싱·범위 검증 = 검증 완료(스텁)**: `app/er/judge.py` — `JUDGEMENT_SCHEMA{matched_person_id:int|null, s_llm:0~1, reason}` 단일 출처, Claude 강제 `tool_choice={"type":"tool"}`·OpenAI `tool_choice={"type":"function"}`·`strict`, `validate_judgement` 공유(범위·타입·`out_of_range_id`), `Judgement.s_llm` 주석·모듈 docstring·trace `llm.self_reported=true` 세 곳에 "자기보고, 로그 확률 아님" 명시. 증거: `tests/test_er_judge.py` 36건(요청 본문·파싱·`schema`/`out_of_range_id`·4종 예외 매핑×2 공급자·키 미노출) — 전체 실행 evidence/20260906-1439-review-pytest-all.txt 에 포함; trace `llm.self_reported=true` evidence/20260906-1439-review-trace-full-recompute.txt. 커밋 b1f2782.
  - (ii) **실 API 호출 = 실호출 미검증**: evidence 디렉터리에 `*er-smoke-real*` 파일 없음(사용자가 실행하지 않음). 설치본 SDK 타입(anthropic 1.4.0 `ToolParam.strict`, openai 2.33.0 `FunctionDefinition.strict`)까지만 정적 확인 evidence/20260906-1439-review-sdk-shape.txt. 모델 id `claude-sonnet-5`·`gpt-4o-mini`, Anthropic 도구 `strict: True` 수락, `usage` 필드명은 **실호출로만 확인된다**. → F-87c597(권고).
  - review-index 문구 제안: `R4 | … | 구현완료(b1f2782 — 구조화 출력 자기보고 s_llm, judge.py·test_er_judge.py 36건 스텁 검증; **실호출 미검증** — er_smoke 사용자 실행 후 evidence 경로 추가) | D3 → S3.3 → P3-er`
- **R9** (인물당 임베딩 1개 → 별칭 단위 top-K → 인물별 max, D5)
  - (i) **별칭 단위 top-K → 인물별 max 구조 = 검증 완료**: P1 스키마(`person_aliases.embedding`, `person_embeddings` 없음)·P2 `search_person`(별칭 top-K 인물별 max) 위에 P3 `candidates.py` 가 `s_emb` 로 그대로 소비하고, U2 가 `OpenAIEmbeddingProvider`(런타임 단일 출처, `dimension`, `check_dimension` flush 전 검증)를 추가. 증거: `-k dimension` 7 passed(evidence/20260906-1418-u9-pytest-dimension.txt, 재실행은 전체 398 에 포함), `tests/test_embedding_provider.py` 14건, 승진 trace `candidates[].aliases_matched=["김팀장","팀장"]`·`s_emb=0.8494`(별칭 2개 중 max) evidence/20260906-1439-review-trace-full-recompute.txt. 커밋 2c63c60.
  - (ii) **실 임베딩 공급자 호출 = 실호출 미검증**: `backfill_embeddings.py --apply`·`OpenAIEmbeddingProvider.embed()` 를 실제 키로 돌린 evidence 없음(dry-run 만, 대상 0건). 실 임베딩 특성은 01-plan 결정 9 대로 P4 가 실제 공급자로 본다.
  - review-index 문구 제안: `R9 | … | 구현완료(4dfaf33, 09c2bd1, a9cb254, 2c63c60 — 별칭 단위 임베딩·top-K 인물별 max·OpenAIEmbeddingProvider 런타임; **실 공급자 호출 미검증**, P4 에서 실측) | D5 → S3.1 → P1-schema, P2-tools, P3-er`

## 5. registry.md 에 올린 산출물
- P3-er 행 20건(모듈 8 · 스크립트 2 · 테스트 10, registry.md 75~94행) — `grep -c '| P3-er |'` = 20.
- 커밋 열 표본 대조 15건(`git log --oneline -1 -- <path>`): `app/er/__init__.py`·`types.py`·`pipeline.py` cc5d24f, `confidence.py` 593c254, `judge.py`·`candidates.py` b1f2782, `rules.py` 02e6f14, `scripts/er_smoke.py` 107ace3, `tests/test_er_pipeline.py` a807364, `tests/test_er_types.py` d6e5949, `tests/test_embedding_provider.py`·`app/embedding.py`·`app/tools/persons.py` 2c63c60, `tests/conftest.py` cc5d24f → **14건 최신 커밋과 일치**. `.env.example` 은 기존 행 규약(생성 커밋 e062986 + 비고에 b1f2782 추적)이라 최신(b1f2782) 이 아님이 정상 evidence/20260906-1439-review-registry-check.txt.
- 기존 행 9개 비고만 갱신, 행 수 1 유지(`requirements.txt` 는 합행) — 05-remediation registry WARN 8건(F-fdb56f F-b3d90e F-149891 F-ef1fb8 F-2c37bd F-127d01 F-b266cb F-0ffff5) **닫힘** 처리.
- `.env.example` 행(35행)은 b3bcc2d 가 신설 — 03-log U9 본문("만들지 않았다")과 어긋남 → F-d5c11e(문서 정합성, 권고).
- README P3 행 "구현 완료 · 검증 대기" + "엔티티 해석(ER) 실행법" 절(217~250행): 명령·변수 **이름**만, 값·키 0건 확인.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
### 권고 6건(계획 재검증 시 발견) — 판정
| 소견 | 해결 단계·판정 명령·재검증 | verifier 판정 |
|---|---|---|
| F-7fe239 허용오차 단일화 | 채워짐. `-k boundary` 7 / `-k threshold` 4 passed, `round(` 호출 0, 변이 A 3건 실패 | **닫힘**(b3bcc2d) |
| F-93f063 JSONB 부분 갱신 원시 SQL 검증 | 채워짐. 테스트 본문이 원시 `SELECT output` + `expire_all()` 재조회(580~622행 직접 확인), 구현 `flag_modified`. `-k applied` 2 passed | **닫힘**(cc5d24f) |
| F-8809f2 apply 중복 거부 | 채워짐. `AlreadyApplied` 즉시 raise, `-k double_apply` 1 passed(판정 명령의 `-k "applied and twice"` 는 이름 불일치 — `double_apply` 로 읽음) | **닫힘**(cc5d24f) |
| F-f3b245 llm_failed 귀속 | 채워짐. `_forced_decision` 공유 구조, `-k llm_failed` 1 passed, 변이 B 7건 실패 | **닫힘**(593c254·d6e5949) |
| F-5a97ef out_of_range_id 이중 방어 | 채워짐. `decide()` 계층 + `validate_judgement` 를 Claude·OpenAI·Fake 셋이 공유(호출부 268·357·419행 확인) — **U5 Judge 조기 차단까지 완료**. 잔여 bool 구멍은 F-036185 로 분리 | **닫힘**(593c254·b1f2782) |
| F-1d65ac null 경로 파이프라인 테스트 | 채워짐. `-k null_path` 1 passed(판정 명령 `-k no_matched` 는 이름 불일치), 도달 불가 가지 docstring 명시, 변이 D 3건 실패 | **닫힘**(d6e5949) |

### 03-log "계획과 다른 점" 판정
| 항목 | 판정 | 근거 |
|---|---|---|
| U2 `embed_pilot.py` 미이동(결정 6-a 예외 발동) | **수용** | 01-plan 168행이 정확히 이 조항("충돌하면 파일럿을 그대로 두고 `app/embedding.py` 를 런타임 단일 출처로 선언") — 충돌 3가지(dimension·name·usage) 근거 있음, `test_embed_pilot.py` 10건 무변경 통과(evidence/20260906-1130-u2-pytest-embed-pilot.txt), registry 26행 확정 문구 |
| U5 공급자 중립(Claude·OpenAI·Gemini 예약·`judge_from_env`) | **수용** | 01-plan 개정 2(사용자 결정 2026-09-06 14:20) 에 반영됨. 원칙 3(자기보고, 로그 확률 없음)·결정 3(a)~(d)가 공급자 무관하게 유지되는지 코드로 확인(`JUDGEMENT_SCHEMA`·`validate_judgement`·`_call_with_error_mapping` 공유). 카드 D3·S3.3 문장 무변경. trace `llm.provider` 존재 |
| U6 `candidates[].similarity`/`aliases_matched` 근사 | **소견(권고) F-251dc2** | 스키마 키는 있으나 값이 `s_emb`·전체 별칭의 복제 — P4 가 "실제 일치 별칭" 을 trace 로 못 본다. 재계산(S3.7)에는 영향 없음 |
| U7 `ask_user` 4키만 전달(`affirmative_options` 최상위 키 제외) | **수용** | `ask_user` 시그니처 v2 `(kind, question, options, context)` 를 지키는 유일한 방법이며 `context[AFFIRMATIVE_KEY]` 로 긍정 답 규약은 유지. 값 가공 없음(pipeline.py 391~397행) |
| U8 `session_scope()` 재사용·`er_config(env)` 사용 | **수용** | 이미 있는 것을 import 해 조립(중복 구현 금지), 결정 8 세 층 규약과 일치. `.env` 미독 grep 0 |
| U9 `.env.example` registry 행 | **소견(권고) F-d5c11e** | 03-log 본문은 "새 행을 만들지 않았다", 커밋 b3bcc2d 는 신설 — 문서 정합성 |

### 신규 소견(전부 [권고], 패키지 닫기 전제 아님)
- F-87c597 R4 실호출 미검증 — 사용자 스모크 1회 실행·evidence 저장 후 review-index 갱신.
- F-46f1eb `tests/test_er_judge.py` 더미 키 `"sk-test-dummy"` → `_FAKE_KEY_MARKER` 규약으로 통일.
- F-251dc2 trace `candidates[].similarity/aliases_matched` 근사 — P4 01-plan 결정(보존 FIX 또는 불필요 명시).
- F-bdd6c5 `ERConfig.top_k` 가 실제 검색 K 에 무효(trace `input.config.top_k` 와 어긋날 수 있음) — P4 스윕 금지 명시 또는 P5 이전 FIX.
- F-036185 `validate_judgement` bool 형 id 통과 — 한 줄 방어 + 테스트 1건.
- F-d5c11e 03-log U9 항목과 b3bcc2d 내용 불일치 — 후속 한 줄.

**필수 소견 0건.** 05-remediation 열림 6(전부 권고) / 해소 26.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- **P4-pilot-eval**
  - 재계산 입력 계약: `agent_traces WHERE step='er_resolve' AND tool_name='er'` 행 1개 = 판정 1개. `output.confidence_breakdown{matched_person_id, s_llm, s_emb, s_rule, weights{llm,emb,rule}, confidence, rule_checked, rule_passed}` 로 `w·s` 재계산 가능(abs diff 0 확인). 후보별 원자료는 `candidates[]`(`s_emb`·`s_rule`·`rule_checked`·`rule_passed`·`relaxed_pass`·`passed_rules`·`excluded_by`) — 귀속 규칙·분모 규칙·완화 계상을 바꿔 재계산할 수 있다.
  - 공급자별 보정표: `llm.provider`/`llm.model`/`llm.s_llm`(self_reported) 로 나눈다. `llm.error` 어휘 `timeout/rate_limit/api_error/connection/schema/out_of_range_id`, `llm.skipped=true` 는 통과 후보 0.
  - 곡선: `resolve(config=ERConfig(t_merge=…))` 인자 주입으로 한 프로세스 안에서 `T_merge` 스윕(결정 8). **`ERConfig.top_k` 는 스윕하지 말 것**(F-bdd6c5 — 무효). `band_by_threshold` 만 순수 산식 구간이고 `forced_reason != null` 행(`llm_failed/no_matched/no_candidates`)은 따로 집계.
  - 리스크 계측: `rule_checked=0` 인 merge 건(힌트 없는 발화 상한 0.8 = T_merge, 01-plan 203행)·`relaxed_retry=true` 인 merge 건의 오병합률을 따로 본다. 호칭 사전 누락(`derive_hints` 가 빈 dict 를 주는 mention 비율)을 측정한다.
  - 실 임베딩·실 LLM 특성은 P4 가 처음 본다(R4·R9 (ii) 실호출 미검증).
- **P5-loop**
  - 트랜잭션 경계: `resolve()` 는 trace 1행 flush, `apply_resolution()` 은 `update_person`/`ask_user` + trace 부분 갱신 후 `flush()` 까지 — commit 은 호출자(`session_scope()`/`get_session()`). 답 대기 사이에 세션이 끊기면 `Resolution.trace_id` 로 행을 다시 찾는다. 같은 `Resolution` 재적용은 `AlreadyApplied`(F-8809f2) — 재개 경로는 trace `decision.pending_question_id` 를 재사용.
  - `Resolution.suggested_display_name`(merge 구간, 결정 3-b)·`ask_payload.context.candidate_ids{이름→id}`(identity 질문 ↔ 인물 바인딩, P2 §7 구멍)·`ask_payload.affirmative_options`(최상위 키는 `ask_user` 에 넘기지 않는다 — 4키만).
  - `JudgeUnavailable` 은 메시지 문자열 하나(`.error` 속성 없음) — `str(exc)` 가 `llm.error` 값.
  - `ToolContext.last_trace_id` 는 `@traced` 성공 경로가 매번 덮어쓴다 — 여러 툴을 연달아 부르면 마지막 값만 남으므로 `resolve()` 직후에만 읽을 것.
  - `hints` 를 주면 사전 유도보다 우선(결정 10) — 사용자 프로필(직급)을 hints 로 넘기는 경로는 P5 검토 사항.
- **실 스모크 명령(값 없이, 사용자 실행)**: `ANTHROPIC_API_KEY=<키> python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/<ts>-er-smoke-real.txt` 또는 `LLM_PROVIDER=openai OPENAI_API_KEY=<키> python scripts/er_smoke.py --provider openai > …`. 종료 코드 0(9키 JSON) / 2(키 없음) / 3(`{"error": …}`). 어느 결과든 evidence 로 남긴다(원칙 8).
- 사소 수정 후보(별도 커밋, P5 전): F-46f1eb 더미 키 마커, F-036185 bool id 방어.

결과: 완료
승인: 사용자 승인 2026-09-06 19:20 (실호출 미검증은 권고 F-87c597 로 남김)
