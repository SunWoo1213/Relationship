# P3-baselines · 완료 검토 (04-review)

날짜: 2026-09-11 | 검토자: verifier (fable) — 구현자(eval-agent, opus)와 다른 모델·새 컨텍스트(L-002). 코드·계획·카드·registry·backlog·CURRENT·README 는 고치지 않았다. 이 문서·`05-remediation.md`(F-445cda 원인 분석·해결 단계·재검증 칸)·`evidence/20260911-1235~1245-review-*` 만 썼다.

검토 대상: HEAD `ad394ba`(dev, U8). 01-plan(U1~U8 전부 `[x]`, 결정 A~J) · 02-plan-verify(통과, 권고 R-1~R-9) · 03-log 9 항목(착수 0e3447a, U1 05d90f0, U2 f212ad6, U3 bcb2fad, U4 8bfd880, U5 0d98e47, U6 e0812f7, U7 7289a63, U8 ad394ba — 03-log 의 U8 항목 해시는 아직 `pending`) · 05-remediation 소견 3(해소 2·열림 1[권고]) · evidence 41 파일(U1~U8) + 이 검토 9 파일 · 코드 `evaluation/`(7 모듈)·`tests/test_baseline_*.py`·`tests/test_scenario_state.py`·`scripts/baseline_smoke.py`·`git diff 0e3447a..HEAD -- app/`. 구현자의 "eval-agent 판단" 51건은 근거가 아니라 확인 대상으로 읽었다(§6).

수치 해석에 대한 주의(01-plan 172행·P1 §7 인계 11): 이 패키지는 **배관**이고 세 밴드의 분포·정답률은 여기서 묻지 않는다. 40건 표본에서 나올 수치는 P4 가 "방향과 실패 유형"으로만 읽고, 운영 임계치 확정은 P10 150건이다.

## 1. 기계 검증 출력 (그대로 붙인다)

### 1a. 초안 실행 (검토자 줄만 있는 04-review 골격으로, 본문 작성 전)
명령: `bash .claude/scripts/verify-impl.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260911-1235-review-verify-impl-draft.txt`
```
== verify-impl P3-baselines  (20260911-1235) ==
sssssssssssssssssssss.ssssssssssssssssssssssssssssssssssss.............. [ 92%]
...................................................................      [100%]
627 passed, 232 skipped in 10.63s
PASS  pytest 통과 → evidence/20260911-1235-pytest.txt
PASS  compileall 통과 → evidence/20260911-1235-lint.txt
PASS  태그 P3-baselines 커밋 9 건 → evidence/20260911-1235-commits.txt
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
FAIL  04-review 수용 기준 표에 행이 없다
PASS  registry 에 P3-baselines 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=1 WARN=0 → evidence/20260911-1235-summary.txt ==
```
- FAIL 1 = 04-review 본문 부재(초안 시점) — `findings.py` 가 **F-445cda** 로 올렸고 verifier 가 원인 분석·해결 단계를 채웠다(05-remediation). 아래 1b 최종 실행으로 해소 여부를 본다.
- pytest `232 skipped` 는 `verify-impl.sh` 가 `POSTGRES_PORT` 없이 pytest 를 돌려 실 DB 테스트(`dbtest`)가 skip 되는 **하네스 한계**(P1 04-review §1a 와 같다). 이 패키지의 DB 테스트를 포함한 전건은 verifier 가 포트를 주고 직접 다시 돌렸다 — `evidence/20260911-1236-review-pytest-all.txt`: `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` → **`859 passed in 21.23s`, skip 0, rc=0**(HEAD ad394ba 머리 줄). U8 의 `evidence/20260911-1215-u8-pytest-all.txt`(859 passed) 와 같은 수치다.
- `evidence/20260911-1235-commits.txt` 9건 = 0e3447a~ad394ba 전부 이 패키지(`gitlog.sh P3-baselines` 와 동일). 03-log Refs 태그(D3·D4·D5·D10·S3.1·S3.3·S3.7)는 모두 커밋 메시지에 있다.

### 1b. 최종 실행 (04-review 본문 작성 후)
명령: `bash .claude/scripts/verify-impl.sh P3-baselines | tee docs/wiki/packages/P3-baselines/evidence/20260911-1245-review-verify-impl-final.txt`
```
== verify-impl P3-baselines  (20260911-1242) ==
sssssssssssssssssssss.ssssssssssssssssssssssssssssssssssss.............. [ 92%]
...................................................................      [100%]
627 passed, 232 skipped in 10.35s
PASS  pytest 통과 → evidence/20260911-1242-pytest.txt
PASS  compileall 통과 → evidence/20260911-1242-lint.txt
PASS  태그 P3-baselines 커밋 9 건 → evidence/20260911-1242-commits.txt
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  베이스라인 3종 (문자열 완전일치·임 ← evidence/20260911-1215-u8-parity.txt, ev
PASS  증거 확인:  해석 1 "베이스라인 3종" → `ALL_METHODS` ← evidence/20260911-1215-u8-methods.txt (`
PASS  증거 확인:  해석 2 "(문자열 완전일치·임베딩 단� ← evidence/20260911-1215-u8-definitions.tx
PASS  증거 확인:  해석 3 "의존: P1 데이터셋" → `tests/tes ← tests/test_baseline_parity.py (103·159~
PASS  증거 확인:  해석 4 "제안 방식과 동일 인터페이스 ← evidence/20260911-1215-u8-parity.txt (46
PASS  registry 에 P3-baselines 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260911-1242-summary.txt ==
```
- **FAIL 0 · WARN 0.** 1a 의 F-445cda 는 이 실행으로 해소(`findings.py … 20260911-1245-review-verify-impl-final.txt --source verify-impl` 재실행 → 해소, 05-remediation 머리 줄). `232 skipped` 는 1a 와 같은 하네스 한계이며 `evidence/20260911-1236-review-pytest-all.txt`(859 passed, skip 0) 가 보완한다. 스크립트 내부 ts 는 12:42(파일명 `-1242-pytest/lint/commits/summary`), tee 파일명은 05-remediation 에 미리 적은 `20260911-1245-…-final.txt` 다.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

수용 기준 문장의 동일성: `sed -n '41p' docs/backlog.md` 와 `sed -n '111p' docs/wiki/packages/P3-baselines/01-plan.md` 를 체크박스·글머리만 떼고 문자열 비교 → `SAME`(verifier 실행, 2026-09-11 12:33). 문장: "[eval-agent] 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능".

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능 — 전체 | evidence/20260911-1215-u8-parity.txt, evidence/20260911-1236-review-pytest-all.txt, 7289a63, ad394ba | 통과 |
| 해석 1 "베이스라인 3종" → `ALL_METHODS` 에 세 방식(결정 C 로 완전일치 2변형) + `proposed` 가 모두 있고 팩토리로 인스턴스가 만들어진다 | evidence/20260911-1215-u8-methods.txt (`('proposed', 'exact_raw', 'exact_norm', 'embedding_only', 'llm_single')`), evidence/20260911-1215-u8-parity.txt (`test_factory_creates_a_resolver_without_keys_or_network[*]` 5 PASSED), evaluation/resolvers/registry.py | 통과 |
| 해석 2 "(문자열 완전일치·임베딩 단독·LLM 단일 프롬프트)" → 세 모듈이 존재하고 방식 정의를 단위 테스트가 단언(완전일치 임베딩·LLM 0회 / 임베딩 단독 LLM 0회 / 단일 프롬프트 LLM 정확히 1회) | evidence/20260911-1215-u8-definitions.txt (183 passed), evidence/20260911-1215-u8-parity.txt (`test_method_definition_call_counters[*]` 10 PASSED), evidence/20260911-1237-review-negative.txt (N7h calls=0·N7i calls=1), evaluation/resolvers/exact_match.py, evaluation/resolvers/embedding_only.py, evaluation/resolvers/llm_single.py | 통과 |
| 해석 3 "의존: P1 데이터셋" → `tests/test_scenario_state.py`·`tests/test_baseline_parity.py` 가 `data/scenarios/` 실물을 읽어 돈다 | tests/test_baseline_parity.py (103·159~162행 `load_scenarios()`·`SCENARIO_IDS=("sc-025","sc-001")`), evidence/20260911-1215-u8-side-effects.txt (sc-025 '엄마'·sc-001 '김팀장' 실물 발화), evidence/20260910-1515-u6-pytest.txt, data/scenarios/manifest.json | 통과 |
| 해석 4 "제안 방식과 동일 인터페이스로 호출 가능" → `POSTGRES_PORT=5433 python -m pytest tests/test_baseline_parity.py -q -rs` 가 같은 테스트 함수에서 `proposed` 포함 전 방식을 같은 인자로 호출해 통과, 본문 분기 0 | evidence/20260911-1215-u8-parity.txt (46 passed, skip 0, `-v` id 에 5방식×sc-025·sc-001), evidence/20260911-1215-u8-no-branch.txt (R-1 grep 0줄 rc=1), tests/test_baseline_parity.py (252~257행 단일 호출 지점·408~448행 계약) | 통과 |

## 2b. 판정 방법 표(01-plan 123~133행) 8행 대조 — verify-impl 의 증거 열 검사 대상은 위 §2 뿐이다

| 01-plan 행 | 기대 출력(계획 문언) | 실측 evidence | 판정 |
|---|---|---|---|
| 125 동일 인터페이스 | parity 전 방식 통과, skip 0, 방식 수 5 | `20260911-1215-u8-parity.txt` 46 passed skip 0; verifier 재실행 `20260911-1236-review-pytest-all.txt` 859 passed 안에 포함 | 일치 |
| 126 방식 목록 | 4 이름 포함 | `20260911-1215-u8-methods.txt` 5종(결정 C 2변형) | 일치 |
| 127 부수효과 0 | 세 테이블 증분 0 **"(제안 방식만 `agent_traces` +1)"** | `20260911-1215-u8-side-effects.txt`: 5방식×2시나리오 모두 `persons`·`person_aliases`·`pending_questions` 증분 0; `agent_traces` 는 **proposed +2, embedding_only +1, 나머지 0**; 롤백 후 4테이블 0. verifier 부정 케이스 N10e'·N10f'·N10h 도 같은 값(`20260911-1237-review-negative.txt` 42·44·46행) | 세 테이블 증분 0 = **일치**. 괄호 문언은 실측과 다름 → 아래 판정 (a) |
| 128 베이스라인 정의 준수 | 완전일치 0/0 · 임베딩 단독 LLM 0 · 단일 프롬프트 LLM 1 | `20260911-1215-u8-definitions.txt` 183 passed; parity 카운터 10 PASSED; 부정 N7h·N7i | 일치 |
| 129 제안 방식 무변경 | `app/` 0줄, 예외 `app/er/judge.py` 1건 이름 승격 | `20260911-1215-u8-isolation.txt`: `git diff --name-only 0e3447a..HEAD -- app/` = `app/er/judge.py` 1줄, diff = `_call_with_error_mapping`→`call_with_error_mapping` 3곳 + 호환 별칭 4줄(+9/-4); verifier 재실행 동일 1줄. 동작 무변경: `POSTGRES_PORT=5433 python -m pytest tests/test_er_judge.py tests/test_er_pipeline.py -q` → 54 passed(verifier 12:33, 두 파일 무수정 — `git log -- tests/test_er_judge.py` 에 이 패키지 커밋 없음), 옛 이름 별칭 `app/er/judge.py:200` 존재 | 일치(결정 J 예외 그대로) |
| 130 데이터셋 무변경 | rc=0, total 40·5범주 | `20260911-1215-u8-data-unchanged.txt` ok:true·total 40·counts 8/8/8/10/6·schema_version 2·rc=0, `git diff 0e3447a..HEAD -- data/` 0줄; verifier 재실행 `git diff --name-only 0e3447a..HEAD -- data/ alembic/ reports/` = 0줄 | 일치 |
| 131 스키마·툴 무변경 | `No new upgrade operations detected.` · `7/7 ok` | `20260911-1215-u8-alembic-check.txt`·`20260911-1215-u8-tools-check.txt` 그대로 | 일치 |
| 132 실 LLM 1회(사용자 실행) | 키 없으면 rc=2 | `20260911-1215-u8-smoke-nokey.txt` rc=2; verifier N9a·N9b(anthropic·openai 둘 다 키 이름 제거 후) rc=2. **실 키 실행은 미수행**(사용자 몫 — `docs/user-setup/08-baseline-smoke.md`) | rc=2 일치 / 실호출 미검증(§7 인계) |
| 133 전체 | 실패 0, skip 0 | `20260911-1215-u8-pytest-all.txt`·`20260911-1236-review-pytest-all.txt` 859 passed skip 0 | 일치 |

**127행(원문 131행 문언) "제안 방식만 `agent_traces` +1" 판정 — (a) 계획 문언 오차, 규약 위반 아님.** 근거: (1) 불변 규약 1 의 정의(01-plan 48행, `evaluation/resolvers/base.py` 11~17행)는 "`persons`·`person_aliases`·`pending_questions` 를 쓰지 않는다 / `ask_user`·`create_person`·`update_person`·`apply_resolution` 을 부르지 않는다"이며 `agent_traces` 는 규약의 대상 테이블이 아니고 `search_person` 은 금지 목록에 없는 **읽기 툴**이다. (2) 초과분 +1 씩은 모두 제품 툴 `search_person` 의 `@traced` 기록(원칙9 — 제품 툴 호출은 trace 를 남긴다)이고, `proposed` 의 `er_resolve` trace 1 은 S3.3/P3-er 결정5 "ER trace 행 1개" 그대로다. 베이스라인이 trace 를 **직접** 쓰는 코드는 없다(`embedding_only.py` 68~73행 docstring, `llm_single.py` 74~78행 "`agent_traces` 도 쓰지 않는다" — 실측 0). (3) 01-plan 171행 리스크 "trace 비대칭"이 이미 "베이스라인은 trace 를 남기지 않고 `MentionDecision` 이 단일 출처"로 정리했으므로 P4 지표 계산에 영향이 없다. 계획 문언은 고치지 않는다(verifier 는 계획을 수정하지 않음) — 권고: (i) `base.py` 16~17행 "제안 방식 어댑터만 `agent_traces` 행 1개" 도 같은 오차이므로 P4 착수 전 docs 커밋에서 실측(proposed 2 = `er_resolve`+`search_person`, embedding_only 1 = `search_person`)으로 정정, (ii) P4 러너가 `agent_traces` 를 세거나 `session_id` 로 trace 를 되찾을 때 이 수를 전제한다(§7 인계 7).

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

verifier 가 직접 실행. 스크립트는 저장소 밖 scratchpad `review_negative.py`(원문은 evidence 파일 끝에 첨부), DB 케이스는 `create_savepoint` 롤백 세션, 네트워크 0, 키 값 출력 0. 출력: `evidence/20260911-1237-review-negative.txt` — **33 케이스 전부 기대와 일치(`MISMATCH=0`, rc=0)**, 검출 33/33.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| N1 `get_resolver("없는이름")` → 등록 목록을 담은 `KeyError`; N1b `register("proposed", …)` 중복 → `ValueError` | `POSTGRES_PORT=5433 python <scratchpad>/review_negative.py` | evidence/20260911-1237-review-negative.txt 4~5행 |
| N2 `MentionDecision(decision="merge", person_id=None)` 거부; N3 `identity`+`person_id=1` 거부; N3b `new_person`+`person_id` 거부; N3c `decision="foo"` 거부; N3d `score=1.5`·N3e `score=NaN` 거부; N3f `identity`+`None` 허용(대조군) | 같음 | 같은 파일 6~12행 (`ValueError … 불변 규약 3` / `score must be in [0, 1]`) |
| N6 `exact_norm` 순수 층: `normalize_dictionary("님")` 은 `'님'`(비지 않음 — U3 판단 (1) 사실 확인), `"님"`·`""` 일치 0 | 같음 | 13~15행 |
| N7 `llm_single` 강등(순수, 스텁 caller): `decision="maybe"` → `identity`+`unknown_decision:maybe`·`person_id=None`; `matched_person_id=9999` → `out_of_range_id`; `merge`+id 없음 → `merge_without_person_id`; `identity`+후보 0 → `identity_without_candidates`; `s_llm=1.7` → `score=1.0`+`score_clamped=True`; `candidate_person_ids=[1,9999,'x']` → kept [1]·`dropped=[9999,'x']`; caller `JudgeUnavailable("timeout")` → `identity`+`forced=timeout`(예외 아님); 빈 mention → LLM `calls=0`+`empty_mention`; 정상 merge 는 `calls=1` | 같음 | 16~26행 |
| N8 `seed_person_specs` 에 `seed_persons` 밖 id `p9` → `ScenarioStateError`; `check_schema_version` 3 → `ScenarioStateError` | 같음 | 27~28행 |
| N9 `scripts/baseline_smoke.py` 키 이름을 환경에서 제거하고 실행(anthropic / `--provider openai`) → rc=2, 안내문에 변수 **이름만** | 같음 (`subprocess`, 키 값 미출력) | 29~30행 |
| N10 DB(롤백 세션, `user_id=review-neg-user`, 동명이인 `김민수` 2건·별칭 `민수`·embedding NULL): N10a `exact_raw "김민수"` → `identity`·`person_id=None`·후보 2건(원칙1 — 하나를 고르지 않음); N10b `exact_norm "김민수님"` → 정규화 `김민수`·`identity` 2건(R-8 양쪽 정규화); N10c `exact_norm "님"` → `new_person`·`forced=None`; N10d `"   "`·N10d' `exact_raw ""` → `empty_after_normalize`; N10e `embedding_only` embedder 없음 → `new_person`+`embedding_skipped`·`top_s_emb=0.0`·`band_by_threshold=new_person`(임계치가 정함, 규약4); N10e' `agent_traces` +1; N10f `proposed`(FakeJudge 0.9, embedder 없음) → `identity`·`score=0.45`·**merge 아님**(T_merge 미만 자동 병합 없음, 원칙1·2); N10f' `agent_traces` +2; N10g 다른 `user_id` 에서 `exact_raw "김민수"` → `new_person`·후보 0(사용자 범위 격리); N10h 7회 호출 뒤 `persons`/`person_aliases`/`pending_questions` 증분 0(`agent_traces` 총 +3) | 같음 | 33~47행 |
| N11 롤백 뒤 새 커넥션에서 `review-neg-user` 인물 0 (저장소·DB 에 흔적 없음) | 같음 | 48행 |

테스트가 실제로 실패 조건을 검사하는지(항상 통과하는 테스트가 아닌지): `tests/test_baseline_base.py` 286·295행 `pytest.raises(KeyError)`, 372~393행 `app/` `.py` 순회 후 `evaluation` import 0 단언(파일 0개면 실패); `tests/test_baseline_llm_single.py` 530~583행 강등 5경로 각각 `forced_reason` 등식, 468·476행 `score_clamped` 유무 양방향; `tests/test_baseline_embedding_only.py` 180행 `TIE`; `tests/test_baseline_exact_match.py` 181~188행 "님" 비지 않음을 **사실로 고정**; `tests/test_baseline_parity.py` 444행 `ALLOWED_TRACE_DELTA[name]` 집합 단언, 372~378행 표가 방식을 빠뜨리면 먼저 깨짐. verifier 의 N 케이스 33건이 같은 조건을 독립 코드로 재현해 같은 값이 나왔다.

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- 없음. INDEX 패키지 표의 이 패키지 "닫는 R" 열은 `—`(01-plan 4행 "닫는 검증: 없음"), `grep -n "P3-baselines" docs/wiki/review-index.md` → 0건(rc=1). R3(두 임계치)·R4 의 구현완료 판정은 P4 곡선 결과로 닫힌다(P1 04-review §4 와 같은 처리).

## 5. registry.md 에 올린 산출물
- `docs/wiki/registry.md` 107~123행 **P3-baselines 17행**(모듈 8 = `evaluation/__init__.py`·`resolvers/{__init__,base,registry,proposed,exact_match,embedding_only,llm_single}.py`·`scenario_state.py` 중 9 경로, 테스트 7, 스크립트 1) — verifier 가 17 경로 전부에 대해 `[ -f ]` 존재와 `git log --oneline --reverse -- <path> | head -1`(파일을 만든 커밋)을 registry 커밋 열과 대조: **17/17 존재·17/17 일치**(05d90f0 ×5, f212ad6 ×2, bcb2fad ×2, 8bfd880 ×2, 0d98e47 ×3, e0812f7 ×2, 7289a63 ×1; verifier 실행 2026-09-11 12:33, 출력은 이 세션 로그 — 재현 명령은 위 그대로). 후속 수정 커밋(`evaluation/__init__.py` e0812f7, `resolvers/__init__.py` f212ad6·bcb2fad·8bfd880·0d98e47, `exact_match.py` 0d98e47, `test_baseline_exact_match.py` 8bfd880·0d98e47, `test_baseline_embedding_only.py` 0d98e47)은 비고 열에 적혀 있고 `git log -- <path>` 와 일치.
- `app/er/judge.py` 행(81행, P3-er) 비고에 "결정 J: 공개 승격(P3-baselines U5 0d98e47) … 옛 이름은 호환 별칭" 기록 — 기존 행은 비고만(01-plan 95행) 준수.
- **README 행(32행, 하네스)**: `grep -c "| README.md |"` = **1**(행 수 불변 — F-0ffff5 해결 단계의 첫 조건 충족). 그러나 그 행 비고에 `P3-baselines U8:` 문구가 **없다**(`grep -o "P3-[a-z]*[^|]*"` → `P3-er U9: …` 만) — U8 이 README 에 "베이스라인 3종 실행법" 절(README 293행~)을 추가했으면서 registry 비고를 덧붙이지 않았다. F-0ffff5 는 [권고] 이므로 완료를 막지 않으나 **열린 채 남는다**(§6 권고 3).
- 커밋 열 표기 방침(U8 판단 (4)): 이 패키지는 "파일을 만든 커밋 1개 + 후속 수정은 비고", P1 행들은 "관련 커밋 여러 개 나열". 둘 다 기계 검증 가능하지만 `verify-impl.sh`/`verify-plan.sh` 는 커밋 열을 읽지 않으므로 어느 쪽도 스크립트를 깨지 않는다. verifier 판단: **이 패키지 방식(생성 커밋 + 비고)이 `git log --reverse | head -1` 한 줄로 대조되어 검증 비용이 낮다.** 통일은 `registry.md` 머리 "규칙" 줄에 한 문장 추가로 끝나는 하네스 문서 작업 → §6 권고 7, 이 패키지 조치 아님.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

### [필수] — 없음
- F-445cda(04-review 표 없음, 초안 시점) — §1b 최종 실행 FAIL 0 으로 **해소**. 그 외 [필수] 소견 없음. 05-remediation 열린 소견은 F-0ffff5([권고], 아래 3) 하나.

### [권고] (패키지 닫기 전제 아님 — 닫는 docs 커밋 또는 P4 계획에서 처리)
1. **131행 문언·`base.py` 16~17행 docstring 정정** — 실측 `agent_traces` 증분(proposed 2·embedding_only 1)으로. 판정 (a), §2b 참조. 계획 본문은 "정정 각주" 형식으로만(원문 보존).
2. **U5 판단 (3) `s_llm` 범위 밖 처리가 제안 방식과 비대칭** — `app/er/judge.py:162` `validate_judgement()` 는 `0 ≤ s_llm ≤ 1` 밖을 `JudgeUnavailable("schema")` 로 **거부**(→ 제안 방식은 `llm_failed` 강등), `evaluation/resolvers/llm_single.py` 247~250·594행은 **접고(clamp) 결정을 유지**(`score_clamped`). `llm_single.py` 239~241행 docstring "`validate_judgement()` 와 같은 어휘·같은 엄격함"은 이 지점에서 부정확하다. 두 공급자 모두 strict 스키마(`minimum 0·maximum 1`, `RESOLUTION_SCHEMA` 121행·`JUDGEMENT_SCHEMA` 75행)를 강제하므로 실호출에서 범위 밖이 올 가능성은 낮고, 발생해도 베이스라인을 **약하게 만드는 방향이 아니라** 유리하게 두는 쪽이라 원칙8(약한 대비군 금지) 위반은 아니다. 다만 "같은 이유로 실패해야 비교가 공정하다"는 구현자 자신의 기준과 어긋나므로: (i) docstring 문장 정정, (ii) P4 지표 정의에서 `score_clamped=True` 건을 보정표(`calibration`)에서 제외하거나 별도 표시(§7 인계 11). FIX 불필요, P4 01-plan 몫.
3. **F-0ffff5 잔여** — registry 32행 README 비고에 `P3-baselines U8: "베이스라인 3종 실행법" 절 추가` 한 줄(§5). 닫는 docs 커밋에서 처리하면 05-remediation 해결 단계 1 이 닫힌다.
4. **`scripts/baseline_smoke.py` 12행 docstring 경로 오기** — "`docs/wiki/user-setup/` 스모크 카드" → 실제 경로는 `docs/user-setup/08-baseline-smoke.md`(`docs/wiki/user-setup` 은 존재하지 않음, `ls` 확인). 문서 문자열 1줄.
5. **03-log U8 항목 해시 `pending`** — 닫는 커밋에서 `ad394ba` 기입(하네스 절차, 03-log 형식 "커밋마다 항목 하나… 해시").
6. **실 키 스모크 미실행(사용자 몫)** — `docs/user-setup/08-baseline-smoke.md`. P4 착수 전 1회. 결과(공급자·모델·`llm_error`)를 P4 evidence 와 이 패키지 evidence 에 남긴다(01-plan P4 인계 5).
7. **registry 커밋 열 표기 방침 통일** — `registry.md` 머리 규칙에 "커밋 열 = 파일을 만든 커밋, 후속 수정은 비고" 한 문장(§5). 하네스 문서 몫.
8. **하네스 한계(P1 과 동일)** — `verify-impl.sh` 가 포트 없이 pytest 를 돌려 `dbtest` 232건이 skip 된다. verifier 가 매번 `POSTGRES_PORT=5433` 재실행으로 보완했다. 스크립트가 `POSTGRES_PORT` 를 환경에서 받아 넘기도록 하는 L-nnn 후보(이 패키지 조치 아님).

### 02-plan-verify §3 권고 R-1~R-9 반영 판정
| # | 판정 | 근거(파일·행·evidence) |
|---|---|---|
| R-1 분기 없음 판정 명령 | 반영 | `tests/test_baseline_parity.py` 7~20행 규칙·329~335행 픽스처 kwargs 표·252~257행 단일 호출 지점; `evidence/20260911-1215-u8-no-branch.txt`·`20260910-1537-u7-no-branch.txt` grep 0줄 rc=1 |
| R-2 역방향 import 0 | 반영 | `evaluation/__init__.py` 12~20행; `tests/test_baseline_base.py` 372~393행; `evidence/20260911-1215-u8-isolation.txt` `grep -rn evaluation app/` rc=1; verifier 재실행 rc=1 |
| R-3 `identity` 후보 목록 | 반영(결정 I) | `llm_single.py` 116~133행 `candidate_person_ids` 필수 필드·533~548행 `_filter_ids`·623~627행 `identity_without_candidates`; `base.py` 23~24행; `evidence/20260911-1215-u8-r3-docstring.txt`; 부정 N7d·N7f |
| R-4 `OPENAI_MODEL` | 반영 | `llm_single.py` 405행 `os.environ.get("OPENAI_MODEL", …)`·36행 docstring; `README.md` 324행(이름만) |
| R-5 private 함수 결정 | 반영(결정 J = 선택지 b) | `evidence/20260911-1215-u8-isolation.txt` diff; `app/er/judge.py:200` 호환 별칭; verifier `test_er_judge.py`+`test_er_pipeline.py` 54 passed(무수정) |
| R-6 `source`·`confirmed_at`·`embedder` 주의 | 반영 | `scenario_state.py` 46~63행(R-6 절)·124행 `ALIAS_SOURCE="confirmed"`·345~347행; `tests/test_scenario_state.py` 364~376행(`confirmed`·`confirmed_at == FIXED_NOW`)·395행(`embedding.is_not(None)` 수); parity 309~312행 주석 |
| R-7 `validate_scenarios` 적재 함수 재사용 | 반영 | `scenario_state.py` 107~112행 `from validate_scenarios import load_dataset …`·198행·210~220행 `check_schema_version`; 부정 N8b |
| R-8 양쪽 정규화·빈 문자열 | 반영(예시 문자열은 사실 정정) | `exact_match.py` 35~40·185~187·353~366행; `tests/test_baseline_exact_match.py` 181~188행("님" 은 `normalize()` 가 비우지 않는다 — `app/er/dictionary.py` 접미 제거 조건, `app/` 무수정); 부정 N6a·N10b·N10c·N10d — R-8 의 **의도**(빈 정규화 결과 → `new_person`+`empty_after_normalize`, 대칭 정규화)는 구현됐고 예시 "님" 만 실물 동작상 빈 문자열이 아니다 |
| R-9 P1 §7 인계 이 패키지 몫·P4 6항 잔존 | 반영 | 2(적재 그대로) `scenario_state.py` 8~28행·`tests/test_scenario_state.py` 바이트 동일 단언; 9(라벨 재해석 금지) `git diff 0e3447a..HEAD -- data/` 0줄; 10(schema_version 2) `SUPPORTED_SCHEMA_VERSION=2`+N8b; 11(40건 방향만) 01-plan 71·172행 + 이 문서 머리; 12(`top_k` 미스윕) `embedding_only.py` 60~66·300행. P4 6항은 01-plan **178~183행**(02-plan-verify 가 적은 171~178행은 "결정 확정 2" 블록 삽입으로 7행 밀린 것)에 그대로 — `evidence/20260911-1215-u8-p4-handover.txt` |

### 03-log "eval-agent 판단" 51건 판정 (U2 4·U3 6·U4 8·U5 10·U6 10·U7 7·U8 6)
| 항목 | 판정 | 근거 |
|---|---|---|
| U5 (3) `s_llm` 범위 밖 clamp | **이의 — [권고] 2** | 위. 제안 방식(`judge.py:162`)은 거부, 베이스라인은 유지. 원칙 위반 아님, 문서·P4 지표 정의로 처리 |
| U5 (4) `forced_reason` 우선순위(호출 실패 > 어휘·id 위반 > 후보 없음) | 이의 없음 | `llm_single.py` 586~627행 분기 순서가 docstring 57~59행과 일치; 한 자리 하나 = P4 범주 집계 전제. 부정 N7a~N7g 각각 단일 사유 |
| U6 (3) `ctx.embedder` 미참조, P4 `embedder=` 명시 필수 | 이의 없음(결정 H(i)) | `scenario_state.py` 61~63·325행 `as_provider(embedder)`; parity 309~312행이 실제로 명시. **P4 러너가 빠뜨리면 두 방식이 `embedding_skipped`** — §7 인계 8 |
| U6 (8) 반복 적재 두 벌·`commit()` 없음 | 이의 없음 | 74~78행 docstring; 초기화는 P1 §7 인계 1 = 01-plan P4 인계 1. §7 인계 9 |
| U7 (1) trace 증분 실측 ≠ 131행 | 판정 (a) 계획 문언 오차 | §2b |
| U7 (4) `hints=None` 전 방식 고정 | 이의 없음, **P4 도 동일하게** | `parity.py` 96~99행; `embedding_only.py` 279~282행(`None` 이면 `derive_hints`). dict 를 주면 유도 경로가 죽어 시나리오 간 의미가 달라진다 — §7 인계 10 |
| U8 (2) SQL 조회 스크립트 저장소 밖 | 이의 없음 | 스크립트 원문이 evidence 끝에 첨부(재현 가능, `verification.md` "명령 재현 출력"); 같은 성질을 `parity.py` 442~444행이 테스트로 고정하므로 registry 대상 아님. verifier 도 같은 방식(§3) |
| U8 (4) registry 커밋 열 방침 | 이 패키지 방식 지지, 통일은 하네스 문서 | §5 |
| U2 (2) 후보별 `score` 는 판정 인물만 `confidence` | 이의 없음 | `proposed.py` 154~160행; P3-er 결정3(후보별 결합 확신도 없음). `signals` 에 원자료 보존 |
| U3 (1) "님" 단독은 빈 문자열이 아님 | 이의 없음(사실) | 부정 N6a; `app/` 무수정 |
| U3 (6) `load_known_persons` 는 `embedding IS NULL` 별칭 포함 | 이의 없음 | 완전일치는 벡터 불필요(`exact_match.py` 50~55행) — 그래서 `embedding_only`·`proposed` 와 별칭 집합이 다를 수 있음은 **방식 정의의 차이**이지 결함이 아니다. P4 가 실 임베딩으로 적재하면 집합이 같아진다 |
| U4 (1) 동점 강등은 `merge` 밴드에서만 | 이의 없음 | 01-plan 103행 "`embedding_skipped` → `new_person`" 과 충돌 없이 원칙1 만 적용. `embedding_only.py` 198~202행 |
| U4 (2) `embedding_skipped` 를 `band_for(0)` 로 | 이의 없음(규약 4) | 부정 N10e `band_by_threshold=new_person` |
| U4 (4) `signals` 에 `s_rule` 미기재 | 이의 없음 | 계산 안 된 값을 0.0 으로 적으면 오독(원칙9 "있는 근거만") |
| U6 (5) `validate_scenarios._dict_items`·`_scenario_id` private import | 이의 없음(선례) | `scripts/`(P1) 의 private 이며 01-plan 67행 규칙은 `app/` 대상. `dump_scenarios.py` 선례. 다만 P1 스크립트를 고치면 깨진다 — registry 비고에 이미 "재사용" 기록 |
| U8 (6) README P1 행 "대기" | 해소됨 | `README.md` 72행 "**완료** … verifier 04-review 완료(5cac9bf)" — ad394ba 에 포함 |
| 나머지 35건(U2 (1)(3)(4), U3 (2)~(5), U4 (3)(5)~(8), U5 (1)(2)(5)~(10), U6 (1)(2)(4)(6)(7)(9)(10), U7 (2)(3)(5)~(7), U8 (1)(3)(5)) | 검토, 이의 없음 | 전부 `detail` 기록 키·순서·재현성·테스트 기법에 관한 것으로 원칙·D·S·security 와 충돌 지점 없음. U8 (5) 스모크 미실행은 [권고] 6 |

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

**P4-pilot-eval 로** — 01-plan 178~183행 6항은 그대로 유효(`evidence/20260911-1215-u8-p4-handover.txt`). 여기에 이 검토에서 생긴 7~15 를 더한다. **P4 01-plan 이 아래를 옮겨 적었는지 P4 02-plan-verify 에서 본다.**

1. 시나리오 사이 **DB 초기화**와 반복 실행 — 적재기는 이 패키지(`evaluation.scenario_state.load_scenario_state`), 초기화·러너는 P4(P1 §7 인계 1).
2. **분모 규칙**: `ambiguous: true` mention 3개 제외, `passing_mentions` 6개 = 오탐 분자, `ask_user` 로 간 mention 은 제3 범주(P1 §7 인계 3·4·6).
3. **지표·곡선·보정표**: 오병합률·미검출률·F1·`ask_user_rate_by_kind`·`calibration`, x축 `T_merge` ∈ {0.5,…,0.95}·`T_new`=0.3 고정(S3.7, D10). `ERConfig(t_merge=…)` 인자 주입으로 다섯 방식 모두 스윕 가능(`resolve_mention(..., config=)`). `top_k` 는 스윕하지 않는다.
4. **`RESOLVERS` 이름 문자열 = `metrics.json` 키** — `proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`(순서 고정, `evidence/20260911-1215-u8-methods.txt`).
5. **판정 모델별 재기록** — 베이스라인 3 을 어느 공급자·모델로 돌렸는지 P4 evidence 에(`MentionDecision.detail["provider"|"model"]` 이 값을 준다).
6. **실 임베딩·실 LLM 특성은 P4 가 처음 본다** — 이 패키지는 스텁까지만(사용자 스모크 08 카드가 실호출 1회, [권고] 6).
7. **`agent_traces` 증분(실측)**: 호출 1회당 `proposed` +2(`er_resolve` 1 + `search_person` 1), `embedding_only` +1(`search_person`), 완전일치 2변형·`llm_single` 0. `MentionDecision` 이 단일 출처이며 trace 로 되짚을 때만 이 수를 전제한다(§2b 판정 (a)).
8. **`load_scenario_state(ctx, scenario, embedder=…)` 의 `embedder=` 를 반드시 명시** — `ctx.embedder` 는 읽지 않는다(결정 H(i)). 빠뜨리면 `person_aliases.embedding` 전부 NULL → `embedding_only`·`proposed` 가 `embedding_skipped`로 떨어져 "방식이 나쁜 것"으로 오독된다(`ScenarioState.embedded_alias_count == alias_count` 를 러너가 단언할 것).
9. **같은 시나리오를 두 번 적재하면 두 벌** — 1 과 같은 사안, 러너가 시나리오마다 트랜잭션 롤백 또는 `user_id` 격리(부정 N10g: `user_id` 범위 밖 인물은 어떤 방식도 보지 않는다).
10. **`hints` 는 다섯 방식에 같은 값**, 기본 `None`(그때 후보 검색 방식만 `derive_hints(mention)` 유도). dict 를 주면 유도 경로가 죽어 시나리오마다 의미가 달라진다(U7 판단 (4)).
11. **`detail["forced_reason"]`·`detail["score_clamped"]` 집계 규칙** — `forced_reason` 은 한 자리 하나(범주 집계), `score_clamped=True` 는 보정표에서 제외 또는 별도 표시([권고] 2). 강등 여부는 `decision` vs `detail["band_by_threshold"]`(proposed·embedding_only) / `detail["raw_decision"]`(llm_single) 차이로 읽는다.
12. **비용**: `llm_single` 프롬프트는 사전 상태 **전체** 인물 목록이라 제안 방식보다 길다(`detail["prompt_chars"]`·`person_count` 가 실측치). 40 시나리오 × mention × (proposed 1 + llm_single 1) LLM 호출 + 별칭·mention 임베딩. `P0-cost` 미착수.
13. **사용자 스모크 08 카드 결과**(공급자·모델·`llm_error`)를 P4 evidence 에 옮겨 적는다(5 와 같은 자리).
14. **`score` 의 의미는 방식마다 다르다**(`base.py` 94~97행: 결합 확신도 / `s_emb` / 일치 여부 1.0·0.0 / `s_llm`) — 같은 축에 놓지 않는다. 완전일치의 `identity` 도 `score` 1.0 이다(U3 판단 (4)).
15. **표본 40건은 방향·실패 유형만**(P1 §7 인계 11) — 운영 임계치 확정은 P10.

**P10-final-eval 로** — P1 04-review §7 P10 인계 1~5 그대로(이 패키지가 더한 것 없음). 다섯 방식 인터페이스는 150건에도 그대로 쓴다.

**하네스로** — [권고] 7(registry 커밋 열 규칙 한 줄)·8(`verify-impl.sh` 포트 전달).

결과: 완료 — §1b `verify-impl.sh` FAIL 0·WARN 0(직접 재실행 pytest 859 passed skip 0), §2 수용 기준 4/4 해석 문장 통과(backlog 41행과 글자 일치 `SAME`), §2b 판정 표 8/8 실측 일치(131행 괄호 문언만 (a) 계획 문언 오차), §3 부정 케이스 33/33 검출, 열린 [필수] 0 · [권고] 8(F-0ffff5 포함, 닫는 docs 커밋·P4 계획·하네스 몫). 실 키 스모크(사용자 몫)·실 임베딩·실 LLM 특성은 P4 가 처음 본다.
승인: 사용자 (2026-09-11)
