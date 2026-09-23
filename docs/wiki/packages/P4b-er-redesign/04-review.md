# P4b-er-redesign · 완료 검토 (04-review)

날짜: 2026-09-23 | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

검토 대상: dev `HEAD = cf5a171`(U7). 무변경 diff 기준점 `e4109cc`(CR-001 문서 이행). 평가 대상 코드는 `85ceda7`(U1)·`08bda7c`(U2)·`dbcfca0`(U3)·`b5b412c`(U4), 재실행 산출물은 `855a26b`(U5, `meta.commit = f96d15b`), 비교 절 `4338eea`(U6). 실행 환경: Docker `capstone2-postgres-1` Up(healthy) 호스트 5433, 네트워크·LLM·임베딩 실호출 **0**, 파일럿 재실행 **0회**(원칙8 — 실 실행은 사용자가 1회만 했다). 이 검토는 코드·계획·카드·`reports/`·`data/` 를 고치지 않았고, 새로 만든 파일은 `evidence/20260923-1242-review-*.txt` 와 이 문서뿐이다. 부정 케이스의 변조 사본은 scratchpad 에만 썼다.

## 1. 기계 검증 출력 (그대로 붙인다)

### 1a. 1차 — 04-review 작성 전
명령: `POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-impl.sh P4b-er-redesign | tee docs/wiki/packages/P4b-er-redesign/evidence/20260923-1242-review-verify-impl.txt`
```
== verify-impl P4b-er-redesign  (20260923-1242) ==
........................................................................ [ 97%]
.............................                                            [100%]
1325 passed in 161.73s (0:02:41)
PASS  pytest 통과 → evidence/20260923-1242-pytest.txt
PASS  compileall 통과 → evidence/20260923-1242-lint.txt
PASS  태그 P4b-er-redesign 커밋 13 건 → evidence/20260923-1242-commits.txt
PASS  커밋에 태그 존재: CR-001
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D12
PASS  커밋에 태그 존재: D13
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: R3
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P4b-er-redesign 행 있음
WARN  미완료 작업 단위 8 개
== 결과: FAIL=0 WARN=2 → evidence/20260923-1242-summary.txt ==
rc=0
```
FAIL 0. WARN 2 = (1) 이 문서 부재(2차에서 소멸해야 한다), (2) `01-plan.md` 의 U0~U7 체크박스가 아직 `[ ]` 다 — 구현 사실과 무관한 문서 표기이며 닫는 커밋에서 메인 세션이 `[x]` 로 바꾼다(§6 V-6). 1차가 만든 `20260923-1242-{pytest,lint,commits,summary}.txt` 는 2차와 중복이다 — 정리 여부는 메인 세션이 정한다. 참고: 4번 검사의 `R8` 은 03-log U3 항목의 `Refs: … R4 R8` 에서 온 것인데, 그 `R8` 은 02-plan-verify 권고 **R-8**(감점 후보 `candidate_ids` 단언)을 뜻하고 review-index 의 검증 항목 R8(`fact_sources`)이 아니다(§6 V-5).

### 1b. 2차 — 04-review 작성 후
(아래 §8 에 붙인다 — 2차 실행은 이 문서를 쓴 뒤에만 가능하다.)

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

backlog 65행 수용 기준 원문(글자 그대로): "`app/er/confidence.py`·`rules.py`·`pipeline.py`·`types.py`(+`settings.py` 설정값) 가 D12·D13 "코드에서 지켜야 할 것" 전부 충족(회귀 3종 유지), `--recheck-traces` `max_abs_diff=0.0`(weights_effective), 새 stamp `reports/pilot/raw-<ts>.jsonl.gz`·`reports/metrics.json` 로 결정 K 게이트 `0.8 [] True True`, `sc-015` 오병합·`sc-007` 미검출 아님, P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경. 미달이면 재실행 없이 failure_cases 갱신 + 사용자 결정". 본 검증 `diff <(sed -n 65,66p docs/backlog.md) <(sed -n 73,74p 01-plan.md)` 는 계획 검증 때와 같은 문장이다(01-plan 71행 "글자 그대로").

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| D12 "코드에서 지켜야 할 것" 1항 — `combine()` 이 `rule_checked` 를 받아 미측정이면 `(w_llm·s_llm + w_emb·s_emb)/(w_llm + w_emb)`, 세 신호 관측 시 D3 원식과 abs diff 0 | evidence/20260923-1242-review-d12-d13-grep.txt (`app/er/confidence.py` 96~129행 `rule_checked: int = 1`·`if rule_checked > 0` 분기·`denom = w_llm + w_emb`), evidence/20260923-1242-review-regression3-recheck.txt (`test_er_confidence.py -k "renormalize or observed or rule_passed or effective"` → 7 passed), evidence/20260923-1242-review-negative-cases.txt (N6: `rule_checked=0` → 0.9 ≠ D3 0.72, `rule_checked=2·rule_passed=0` → 0.72 = D3), 85ceda7 | 통과 |
| D12 2항 — `confidence_breakdown` 에 `weights`·`weights_effective`·`rule_checked` 키 | evidence/20260923-1242-review-d12-d13-grep.txt (`confidence.py` 209·210·212·213행 `"weights"`·`"weights_effective": _effective_weights(...)`·`"rule_checked"`·`"rule_passed"`), evidence/20260923-1242-review-gate-recalc.txt (§G — 재실행 trace 141/141 에 `weights_effective` 존재는 U6 evidence/20260923-0039-u6-compare.txt (e) 141/141), 85ceda7 | 통과 |
| D12 3항 — `rule_checked > 0`·`rule_passed == 0` 은 여전히 `s_rule = 0` 합산(재정규화 아님) | evidence/20260923-1242-review-negative-cases.txt (N6 `combine(0.9,0.9,0.0,cfg,rule_checked=2)` = 0.72 = D3 원식), evidence/20260923-1242-review-regression3-recheck.txt (`test_decide_rule_checked_positive_rule_passed_zero_still_sums_zero_s_rule` 포함 7 passed), 85ceda7 | 통과 |
| D12 4항 · D13 4항 — 회귀 3종(승진 연결·팀장↔이모 배제·동명이인 분리) 통과, **결과(band·action·저장된 질문 종류)가 P3-er 때와 같다** | evidence/20260923-1242-review-regression3-recheck.txt (`pytest tests/test_er_pipeline.py -k "promotion or aunt or homonym"` → `3 passed, 17 deselected`, rc=0). P3-er 시점 단언과의 대조는 본 검증에서 `git show cc5d24f:tests/test_er_pipeline.py` 로 했다: 승진 435~444행 `band=="merge"`·`forced_reason is None`·`applied.action=="merge"`·`pending_question_id is None` = 현재 454~464행 그대로(+`band_by_threshold=="merge"`·`penalized_by==("hierarchy_conflict",)` 단언 추가); 이모 494~512행 `forced_reason=="no_candidates"`·`band=="new_person"`·`rows[0].kind=="new_person"` = 현재 519~537행 그대로(+`excluded_by=="dictionary_conflict"`·`penalized_by` 표시); 동명이인 540~568행 `t_new <= confidence < t_merge`·`band=="identity"`·`ask_payload kind=="identity"`·`rows[0].kind=="identity"` = 현재 565~593행 그대로. 바뀐 것은 표시 필드와 `confidence` 수치(동명이인 0.575→0.71875, 03-log U1)뿐, cc5d24f, dbcfca0 | 통과 |
| D13 1항 — `relation_tag_conflict`·`hierarchy_conflict` 가 후보를 빼지 않고 `penalized_by` 에만 등장, `excluded_by` 는 `dictionary_conflict` 만 | evidence/20260923-1242-review-d12-d13-grep.txt (`rules.py` 138~139·151·155행 두 사유는 `penalizing_conflicts.add` 로, 166행 `dictionary_conflict` 만 `conflicts` 배제 경로, 196행 `excluded_by = _EXCLUSION_ONLY_CONFLICT if … else None` 이 유일한 대입, 197행 `penalized_by = tuple(...)`), evidence/20260923-1242-review-negative-cases.txt (N7: 사전 모순 후보 30 `excluded_by=dictionary_conflict`, 감점 후보 31 `excluded_by=None`·`penalized_by=('relation_tag_conflict','hierarchy_conflict')`·3단계 전달 [31, 32]), 08bda7c | 통과 |
| D13 2항 — 3단계 전달 후보 수 == 1단계 후보 수 − `dictionary_conflict` 수(테스트로 단언) | evidence/20260923-1242-review-regression3-recheck.txt (`test_er_rules.py -k "forwarded or penal or excluded_by_domain"` → 5 passed; `test_candidate_count_forwarded_equals_total_minus_dictionary_excluded` 242행 `len(passed) == len(all_scored) - dictionary_excluded_count`), evidence/20260923-1242-review-d12-d13-grep.txt (테스트 본문 228~245행 인용), 08bda7c | 통과 |
| D13 3항 — 보수 분기를 설정값 하나(`ER_PENALIZED_MERGE_POLICY`)로 켜고 끄고 기본값은 01-plan 결정(`ask`), trace 에 적용 여부 | evidence/20260923-1242-review-d12-d13-grep.txt (`app/settings.py:94 ER_PENALIZED_MERGE_POLICY = "ask"`·166행 `_read_choice(..., ("ask","merge"))`, `types.py:337 penalized_merge_policy: str = "ask"`·350행 어휘 검증, `pipeline.py:116 FORCED_REASON_PENALIZED_CANDIDATE`·142~160행 `_downgrade_penalized_merge` 가 `decision_payload["forced_reason"]` 에 남김), evidence/20260923-1242-review-regression3-recheck.txt (`-k penalized` → 2 passed: 기본 강등·`merge` 오버라이드), evidence/20260923-1242-review-negative-cases.txt (N1·N1b `bogus` 거부, N1c `merge` 통과), evidence/20260923-1242-review-gate-recalc.txt (§F 실 실행 trace `forced_reason=penalized_candidate` 5건), dbcfca0 | 통과 |
| `--recheck-traces` `max_abs_diff=0.0`(weights_effective) — 새 stamp trace | evidence/20260923-1242-review-regression3-recheck.txt (`python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-20260922-150931.jsonl` → `dumped=1410 recomputed=1410 max_abs_diff=0.0`, rc=0 — 본 검증 직접 실행), evidence/20260923-1242-review-negative-cases.txt (N5b~N5e: 확신도 +0.01·`weights_effective` 비도출·`weights` 상수 불일치·키 삭제를 각각 rc=1 로 잡는다 — 판정기가 실제로 실패 조건을 본다), reports/pilot/traces-20260922-150931.jsonl, b5b412c | 통과 |
| 새 stamp `reports/pilot/raw-<ts>.jsonl.gz`·`reports/metrics.json` 로 결정 K 게이트 `0.8 [] True True` — `metrics.json.gate` 인용 + **독립 재계산** | evidence/20260923-1242-review-gate-recalc.txt (§A 방식별 n/d 에서 지배식 재계산 → `dominated_by=[]`; §B `reports/curve.csv` 연속 9쌍 오병합률 비증가·identity 발생률 비감소 위반 0 → `d10_direction=True`; §C 독립 재계산 `0.8 [] True True` == `metrics.json.gate` `0.8 [] True True`, `reason=None`, 일치 True; §D 원시 JSONL 을 `classify_gold_row` 로 다시 세어 5방식 오병합·미검출·분모가 `metrics.json` 과 전부 일치; §G `run_mode=real`·`run_id run-35ae97b5e6ed`·`commit f96d15b` 가 P4(`run-29621888da00`·`750f11b`)와 다름), reports/metrics.json, reports/pilot/raw-20260922-150931.jsonl.gz, 855a26b | 통과 |
| `sc-015` 오병합 아님 · `sc-007` 미검출 아님 — `gate.pass` 밖의 **별도 조항** | evidence/20260923-1242-review-gate-recalc.txt (§E: `sc-015` t0 "부장님" `classify=deferred`·`decision=identity`·`forced_reason=penalized_candidate`·`band_by_threshold=merge`·conf 0.8167·정답 후보가 후보 목록과 3단계에 있음(`gold_in_candidates=True`·`matched==gold=True`); `sc-007` t2 "문실장님" `classify=deferred`·`decision=identity`·conf 0.5442·`rule_checked=2`·정답 16222 가 `penalized_by` 로 남아 3단계 도달; `sc-015` false_merge 행 0·`sc-007` miss 행 0). 두 건은 **정답이 아니라 되묻기(`deferred`)** 로 옮겨졌다 — 문구("오병합·미검출 아님")는 충족, "해결"은 아니다(§6 관찰 1), 855a26b | 통과 |
| P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경 + 사본 sha256 | evidence/20260923-1242-review-boundary.txt (`git diff --name-only e4109cc..HEAD -- reports/pilot/raw-20260922-042440.jsonl.gz reports/pilot/traces-20260922-042440.jsonl` → 0줄; `sha256sum` raw `8d85e4de…` = `git show e4109cc:` blob 해시 동일, traces `41aa3165…`, metrics 사본 `25e16dd67ea7…`; blob id `eea060ae…` 가 `e4109cc:reports/metrics.json` = `adf9f1b:reports/metrics.json` = `HEAD:reports/pilot/metrics-20260922-042440.json` 로 셋이 같다 — 사본이 P4 시점 파일과 바이트 동일), reports/pilot/metrics-20260922-042440.json, a8faa81 | 통과 |
| "미달이면 재실행 없이 failure_cases 갱신 + 사용자 결정" — 해석 (i) 실 실행 evidence 설정당 1개 (ii) 비교 절 존재 (iii) 설정 변경 흔적 없음 | evidence/20260923-1242-review-boundary.txt (`ls evidence/*real-run* | wc -l` → 1), reports/failure_cases.md (§13 422~762행, U6 4338eea), evidence/20260923-1242-review-gate-recalc.txt (§G: `t_new` 0.3·`grid` 10점·`weights` 0.5/0.3/0.2·`model_configured`·`embedding_model`·`dataset_hash` 가 P4 사본과 같음 — `weights.source` 문자열만 D3→D12 문구), 855a26b | 통과 |
| (01-plan 판정 표 1행) 전체 테스트 실패 0·skip 0 | evidence/20260923-1242-pytest.txt (`1325 passed in 161.73s`, verify-impl 1차), evidence/20260923-1214-u7-accept-1.txt (U7 `1325 passed`) | 통과 |
| (판정 표 15·16행) `app/` 변경이 허용 5파일의 부분집합 · `data/` 0줄 | evidence/20260923-1242-review-boundary.txt (`git diff --name-only e4109cc..HEAD -- app/` → `app/er/confidence.py, pipeline.py, rules.py, types.py, app/settings.py` 정확히 5 = 허용 목록; `-- data/` → 0줄) | 통과 |
| (판정 표 13·14·18·19행) 스키마·격자 · `eval.md` 멱등 · 라벨 무변경 · alembic/툴 무변경 | evidence/20260923-1214-u7-accept-2.txt (U7: `--validate OK`·격자 10점·`{'0.3'}`·5방식, report 재생성 diff 0줄, `validate_scenarios --strict --json` total 40·5범주·issue 0, `alembic check` "No new upgrade operations detected."·`tools_check 7/7 ok`), evidence/20260923-1242-review-negative-cases.txt (N4e 본 검증 `--validate reports/metrics.json` → OK rc=0) | 통과 |
| (판정 표 20행 · D13 파급 "위험 계측") `penalized_merge` 건수 보고 — **정의 명시** | evidence/20260923-1242-review-gate-recalc.txt (§F: `proposed@0.8` merge 96 중 **정의 A(귀속 인물 자신이 감점 후보) 14 · 오병합 0** = `metrics.json subsets.penalized_merge {merges 14, n 0/d 14, relaxed_pass_merges 14, reasons {hierarchy_conflict 14}}`; **정의 B(후보 아무나 감점) 22 · 오병합 0**. 보수 강등 5건 전부 귀속==골드). 판정 표 원문 명령 `m['proposed']['subsets']` 는 KeyError 이고 정정 경로는 `m['proposed']['by_t_merge']['0.8']['subsets']` — 계획서 오기(§6 V-1), 산출물 결함 아님, b5b412c | 통과 |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 본 검증이 직접 실행했다(`evidence/20260923-1242-review-negative-cases.txt`, 18건 중 기대대로 18, 저장소 파일 수정 0). 원본 `traces-20260922-150931.jsonl`·`metrics.json` 은 읽기만 하고 변조는 scratchpad 사본에만 했다.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 어휘 밖 정책값을 환경변수로 넣으면 `er_config()` 가 거부한다 | `ER_PENALIZED_MERGE_POLICY=bogus python -c "from app.settings import er_config; er_config()"` → rc=1 `InvalidValue: … must be one of ('ask', 'merge') (got 'bogus')` | evidence/20260923-1242-review-negative-cases.txt N1 |
| 같은 어휘 검증이 `ERConfig` 생성자에도 있다 / 허용값 `merge` 는 통과(대조군) | `ERConfig(penalized_merge_policy='bogus')` → rc=1 · `ER_PENALIZED_MERGE_POLICY=merge` → `policy= merge` rc=0 | evidence/20260923-1242-review-negative-cases.txt N1b·N1c |
| 옛 기준선 trace(D3 산식, `weights_effective` 없음)는 새 재계산을 통과하지 않는다 | `python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-20260922-042440.jsonl` → rc=1 `weights_effective 가 없다 (D12 이전 trace 는 이 재계산 대상이 아니다)` 1410건 | evidence/20260923-1242-review-negative-cases.txt N2 |
| 옛 기준선 metrics 사본(판 1)은 새 `--validate` 가 거부한다 — 사유는 판 번호가 아니라 meta 정책 키 2개 결손 | `python -m evaluation.metrics --validate reports/pilot/metrics-20260922-042440.json` → rc=1 `missing key(s) ['weights_policy', 'penalized_merge_policy']` | evidence/20260923-1242-review-negative-cases.txt N3 |
| `metrics.json` 을 변조하면 `--validate` 가 잡는다: `gate.pass` 뒤집기 / `weights_policy=bogus` / `penalized_merge_policy` 어휘 밖 / `false_merge n=1` 로 rate 불일치 | 사본 4종 → 각각 rc=1(`gate.pass: False disagrees with …`, `must be 'observed_renormalized(D12)'`, `must be one of ['ask','merge']`, `rate: 0.0 != n/d (1/132)`); 원본은 `OK` rc=0 | evidence/20260923-1242-review-negative-cases.txt N4a~N4e |
| 새 trace 사본을 변조하면 `--recheck-traces` 가 잡는다: 확신도 +0.01 / `weights_effective` 비도출값 / `weights` ≠ `ER_WEIGHTS` / `weights_effective` 삭제 | 앞 30줄 사본(`rule_checked==0` 줄 변조) → 각각 rc=1(`abs diff=0.01 != 0`, `도출되는 값 {0.625, 0.375, 0.0} 과 다르다(D12)`, `제품 상수 ER_WEIGHTS 와 다르다(원칙3)`, `weights_effective 가 없다`); 변조 없는 사본은 `max_abs_diff=0.0` rc=0 | evidence/20260923-1242-review-negative-cases.txt N5a~N5e |
| 재정규화가 값을 실제로 바꾸고, 검사했는데 전부 충돌(`rule_checked=2, rule_passed=0`)은 여전히 0 합산 / 범위 밖 `s_llm` 거부 | `combine(0.9,0.9,0.0,cfg,rule_checked=0)` = 0.9 ≠ D3 0.72 · `rule_checked=2` = 0.72 · `combine(1.2,…)` → `InvalidValue` | evidence/20260923-1242-review-negative-cases.txt N6·N6b |
| 규칙 필터: 관계 태그·위계 충돌 후보는 남고(감점), 사전 모순만 배제된다(팀장↔이모) | `run_rule_stage([사전모순 30, 감점만 31, 깨끗 32], derive_hints("이모"))` → 30 `excluded_by=dictionary_conflict`, 31 `excluded_by=None penalized_by=(relation_tag_conflict, hierarchy_conflict)`, 3단계 전달 `[31, 32]` | evidence/20260923-1242-review-negative-cases.txt N7 |
| 감점 후보가 `≥ T_merge` 여도 기본 정책은 자동 병합하지 않는다(DB 필요 → 테스트로) | `pytest tests/test_er_pipeline.py -k penalized` → 2 passed (`…downgrade` 가 `band="identity"`·`forced_reason="penalized_candidate"`·`pending_questions kind="identity"`·`candidate_ids` 에 감점 후보 포함까지 단언, `…merge_override` 가 반대 경로) | evidence/20260923-1242-review-regression3-recheck.txt |
| 허용 밖 `app/` 파일·`data/`·기준선 변경 없음 | `git diff --name-only e4109cc..HEAD -- app/` 5파일뿐 · `data/` 0줄 · 기준선 2파일 0줄 | evidence/20260923-1242-review-boundary.txt |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- **R3**(임계치 방향) — review-index 11행 비고 "**CR-001 뒤 P4b 재실행 곡선으로 재확인**"은 본 검증 §B 로 충족됐다: `reports/curve.csv` 제안 방식 연속 9쌍에서 오병합률 `[0.0303,0.0303,0.0303,0.0227,0.0227,0.0076,0,0,0,0]` 비증가·identity 발생률 `[0.1667 … 0.6515]` 비감소, 위반 0(evidence/20260923-1242-review-gate-recalc.txt). **review-index 비고는 아직 갱신되지 않았다** — 닫는 커밋에서 메인 세션이 "재확인(855a26b, 04-review cf5a171 이후 해시)" 한 줄을 더한다.
- **R4**(자기보고 `s_llm` + 보정표) — CR-001 §2 "산식 분모 변경으로 재검증 필요": 재실행 `reports/calibration.json`(855a26b, `--t-merge 0.8`)이 D12 산식으로 다시 생성됐고 `--recheck-traces` 가 1410건 `abs diff 0`. review-index 12행 비고에 "D12 산식으로 재검증(855a26b)" 한 줄 필요(미갱신).
- R8 은 이 패키지와 무관하다(§1a 참고 — 03-log 의 `R8` 은 권고 R-8).

## 5. registry.md 에 올린 산출물
05-remediation 의 열린 소견 22건([권고] 22, [필수] 0 — verify-plan 이 낸 "registry 에 다른 패키지로 이미 있음")을 U7(`cf5a171`)의 registry 갱신과 1:1 대조했다(본 검증 grep, 각 경로의 registry 행에 `P4b` 비고와 해시가 있는가):

| 소견 | 경로 | registry 행 · P4b 비고 | 판정 |
|---|---|---|---|
| F-ed9327 | app/er/confidence.py | 82행 `P4b-er-redesign U1(85ceda7)` | 닫힘 |
| F-99f745 | app/er/rules.py | 81행 `U2(08bda7c)` | 닫힘 |
| F-ead503 | app/er/pipeline.py | 85행 `U3(dbcfca0)` | 닫힘 |
| F-c4dc23 | app/er/types.py | 79행 `U2(08bda7c)·U3(dbcfca0)` | 닫힘 |
| F-fdb56f | app/settings.py | 53행 `U3(dbcfca0)` | 닫힘 |
| F-3e8c8f | scripts/run_pilot_eval.py | 137행 `U4(b5b412c)` | 닫힘 |
| F-111cde | evaluation/curve.py | 133행 `U4(b5b412c)` | 닫힘 |
| F-c9f2fe | evaluation/metrics.py | 129행 `U4(b5b412c)` | 닫힘 |
| F-63a805 | evaluation/calibration.py | 131행 `U4(b5b412c)` | 닫힘 |
| F-a58eb4 | evaluation/resolvers/proposed.py | 115행 `U4(b5b412c)` | 닫힘 |
| F-2e533b | tests/test_er_confidence.py | 91행 `P4b U1(pending)` — 비고는 있으나 **해시 미확정**(85ceda7 로 바꿔야 한다) | **열림(권고)** |
| F-107c92 | tests/test_er_rules.py | 89행 `P3-er 02e6f14 · 8건` — **P4b 비고 없음**(실제 11건, 08bda7c) | **열림(권고)** |
| F-8439c7 | tests/test_er_pipeline.py | 94행 — **P4b 비고 없음**(20건, 08bda7c·dbcfca0) | **열림(권고)** |
| F-27a843 | tests/test_run_pilot_eval.py | 138행 — **P4b 비고 없음**(+5건, b5b412c) | **열림(권고)** |
| F-5d4642 | reports/metrics.json | 142행 `U5(855a26b)` | 닫힘 |
| F-00846b | reports/failure_cases.md | 146행 `U6(4338eea)` §13 | 닫힘 |
| F-0ffff5 | README.md | 33행 `U7(pending)` — 닫는 커밋 해시로 확정 필요(U7 03-log 가 예고) | 닫힘(해시 확정은 닫는 커밋) |
| F-225938 | docs/user-setup/10-pilot-eval-run.md | 147행 `U5 선행(a8faa81)`·`U7(pending)` | 닫힘(해시 확정은 닫는 커밋) |
| F-fcf0a9 | `.jsonl.gz`(basename 오탐) | 149행 `raw-20260922-150931.jsonl.gz` P4b-er-redesign 855a26b 신규 행 | 닫힘 |
| F-a4bedc | calibration.json(오탐) | 143행 `U5(855a26b)` + 148행 기준선 사본 행 | 닫힘 |
| F-09ad74 | curve.csv(오탐) | 144행 `U5(855a26b)` | 닫힘 |
| F-3f9278 | eval.md(오탐) | 145행 `U5(855a26b)` | 닫힘 |

신규 행 4개(148 기준선 stamp 사본 4파일 a8faa81 · 149 `raw-20260922-150931.jsonl.gz` 855a26b · 150 `traces-20260922-150931.jsonl` 855a26b · 151 U7 evidence 2파일 `pending`)도 확인했다. 새 산출물(`ScoredCandidate.penalized_by`·`meta.weights_policy`·`meta.penalized_merge_policy`·`subsets.penalized_merge`·`ER_PENALIZED_MERGE_POLICY`)은 기존 행 비고에 들어 있다(79·133·129·53행). **닫힘 18 / 열림 4**(전부 [권고], 전부 registry 비고 누락·해시 미확정 — 05-remediation 의 상태 줄은 verifier 가 고치지 않는다; 닫는 커밋에서 메인 세션이 4행을 갱신하고 `findings.py` 재실행으로 해소한다).

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
**게이트·수용 기준을 막는 [필수] 소견: 없음.** 아래는 전부 [권고](문서 정합) 또는 관찰(판정에 반영, 조치는 P10 인계)이다.

새 소견(본 검증):
- **V-1 [권고] 01-plan 판정 표 20행 명령 경로 오기.** `m['proposed']['subsets']` 는 `KeyError`, 실제 경로는 `m['proposed']['by_t_merge']['0.8']['subsets']`(failure_cases §11 R21 과 같은 경로). U7 이 원문 실행 rc=1 을 지우지 않고 남겼고 본 검증도 정정 경로로 판정했다(§2 마지막 행). 사용자 결정으로 계획서는 고치지 않는다 — 이 문서가 정정 경로의 기록이다. 하네스 교훈 후보: 판정 표 명령은 계획 검증(02-plan-verify) 때 한 번 실행해 본다(당시 산출물이 없어 실행 불가였던 행이라 예외).
- **V-2 [권고] 05-remediation 잔여 4건**(§5: F-2e533b 해시 미확정, F-107c92·F-8439c7·F-27a843 registry 비고 없음). 테스트 4파일은 01-plan 산출물 목록(53행)에 있으므로 U7 규약("수정한 기존 행은 비고 확장")의 누락이다. 닫는 커밋: registry 89·91·94·138행 비고에 P4b 단위·건수·해시 한 줄씩.
- **V-3 [권고] 03-log 제목 줄 해시 `pending` 6건** — U2(08bda7c)·U3(dbcfca0)·U5 선행(a8faa81)·U5 실 실행(855a26b)·U6(4338eea)·U7(cf5a171). 03-log 는 "지우거나 고쳐 쓰지 않는다"가 규약이지만 `pending` → 해시 확정은 U0 항목이 선례(13행 "직전 `pending`→83d33dd")다. 닫는 커밋에서 확정.
- **V-4 [권고] registry `pending` 3곳(33·147·151행)과 README 진행 상태 표 P4 행("게이트 미달")** — U7 03-log 가 닫는 커밋 항목으로 이미 적었다. 함께 review-index R3·R4 비고(§4).
- **V-5 [권고] 태그 어휘 충돌** — 03-log U3 `Refs: … R4 R8` 의 `R8` 은 권고 R-8 인데 `verify-impl.sh` 4번·`git log --grep` 이 검증 항목 R8 로 읽는다(§1a). 앞으로 권고는 `R-8` 표기만 쓰고 Refs 에는 넣지 않는다(하네스 L-nnn 후보, 코드 영향 0).
- **V-6 [권고] 01-plan U0~U7 체크박스 `[ ]` 8개**(verify-impl WARN) — 닫는 커밋에서 `[x]`.
- **V-7 관찰(소견 아님) `.env.example` 변경** — `git diff e4109cc..HEAD` 에 01-plan 산출물 목록에 없는 `.env.example`(`ER_PENALIZED_MERGE_POLICY=ask` 5줄)이 있다. 03-log U3 "메인 세션 보완"이 사유(settings.py 22행 2층 규약과의 정합)를 적었고, 제품 코드·테스트가 이 파일을 읽지 않으며(`grep -rln env.example tests/` 0건) "하지 않는 것" 목록 위반이 아니다. 범위 초과로 보지 않는다.

관찰(판정에 반영한 사실 — 구현자의 자기 평가가 아니라 U6·U7 이 낸 수치를 본 검증이 재계산했다):
1. **`sc-015`·`sc-007` 은 `deferred` 다.** 수용 기준 문구("오병합·미검출 아님")는 충족하지만 둘 다 `merge_correct` 가 아니다. `sc-015` 는 순수 산식으로 `merge`(0.8167 ≥ 0.8, 귀속 = 골드)였으나 결정 A(i) 강등으로 되물었고, `sc-007` 은 0.5442 로 `[T_new, T_merge)` 다. "고쳐졌다"가 아니라 "안전한 쪽으로 옮겨졌다"로 기록한다.
2. **`penalized_merge` 정의.** 이 문서와 `metrics.json` 이 보고하는 14건은 **정의 A(귀속 인물 자신이 감점 후보인 merge)** 이고, 원시 JSONL 을 "후보 아무나 감점" 기준으로 세면 22건이다(§2 마지막 행, evidence §F). D13 위험(감점 후보를 자동 연결)은 정의 A 가 맞고, 14건은 전부 `relaxed_pass` 예외(승진 계열)·오병합 0. 정의 B 의 나머지 8건은 감점된 다른 후보를 두고 정상 후보로 병합한 것.
3. **보수 강등 5건은 전부 귀속==골드.** 결정 A(i) 가 이번 표본에서 막은 오병합은 0, 비용은 정답 5건 되묻기(마찰 31건 중 5). 수용 기준 밖이며 40건으로 이득·비용을 정할 수 없다 → §7 인계 1.
4. **실행 간 `s_llm` 자기보고 변동 60/136.** 게이트 개선을 D12·D13 단독 효과로 분해할 수 없다(U6 §13.7). 판정에는 이렇게 반영했다: 결정 K (a) 는 "기록된 한 실행"에 대한 식이고 결정 E(i) 가 1회를 정했으므로 게이트 판정 자체는 성립한다; `exact_raw`·`exact_norm`·`embedding_only` 는 결정 변화 0 이라 지배가 풀린 것이 베이스라인 악화 때문이 아니라는 점, 그리고 D12 반사실(§8 후보 1: merge 97·골드 96·오병합 1)과 실측(merge 96·골드 96·오병합 0)이 1건 차이로 맞는다는 점이 D12 기여의 근거다. 그러나 **"P4b 게이트 통과"는 40건·1회 실행의 결과**이며 변동성 측정은 P10 의 몫이다(§7 인계 2).
5. **실 실행 evidence 에 rc 줄이 없다.** 대체 근거 3가지를 충분하다고 판정한다: (a) `run_pilot_eval.py` 는 어느 단계든 rc≠0 이면 즉시 비0 으로 끝나고 `[ok] 사슬 완료` 는 `return RC_OK` 직전에만 찍힌다(U7 evidence 9행 `sed` 인용), 실 실행 파일에 6단계 `rc=0` + `[ok] 사슬 완료` 가 있다; (b) 실행 직후 `20260923-0021-u5-postrun-verify.txt` 가 산출물 8개·`--validate OK`·`--recheck-traces 0.0`·report diff 0줄; (c) 본 검증이 같은 산출물로 `--recheck-traces`(rc=0)·`--validate`(rc=0)·원시 재집계(§D 일치)를 다시 돌렸다. 재실행은 답이 아니다(원칙8). 카드 10 은 이미 `echo "rc=$?"` 를 절차에 넣어 두었다(56·76행) — 다음 실 실행은 표준출력만이 아니라 그 줄까지 리다이렉트한다(§7 인계 5).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
1. **결정 A(i) 의 비용 계측(P10).** `ER_PENALIZED_MERGE_POLICY=ask` 기본값을 유지하되, 150건에서 보수 강등 건수·그중 귀속==골드 비율·`penalized_merge`(정의 A) 부분집합의 오병합을 다시 잰다. 이번 40건: 강등 5/5 정답, 감점 merge 14/14 정답(전부 `relaxed_pass`). `merge` 로 바꾸면 `sc-015` 가 자동 연결되므로 안전 마진과 함께 사라진다 — 40건으로 정할 수 없다.
2. **변동성(P10).** 같은 프롬프트·모델에서 `s_llm` 이 60/136 흔들렸다. 결정 E(iii)(2회 실행) 를 P10 에서 계획하거나 보정표 `calibration.json` 의 구간별 정답률로 대신 볼지 eval-agent 가 P10 01-plan 에서 결정. `llm_single` 도 1건 바뀌었다(`sc-002` t3).
3. **`T_merge`/`T_new` 운영값 확정(P10).** 초기값 0.8/0.3 유지. 재실행 곡선에서 절벽(0.75→0.80 보류 33→79)이 사라졌고 단조성 유지(R3). 0.75 에서 오병합 1/132 — 운영값을 내리려면 150건 근거가 필요하다.
4. **P5 착수 조건.** backlog 70행 "의존: P3, **P4b 게이트 통과**" — 이 문서 `결과: 완료` + 사용자 승인 뒤. P5 가 읽을 인터페이스: `ERConfig.penalized_merge_policy`(`"ask"|"merge"`, `er_config()` 가 `ER_PENALIZED_MERGE_POLICY` 를 읽음), `ScoredCandidate.penalized_by: tuple[str, ...]`(trace `candidates[].penalized_by` 와 `Resolution.to_dict()` 에 직렬화), `combine(..., rule_checked=)`(생략 시 1 = 측정됨), `confidence_breakdown.weights_effective`(`rule_checked==0` 이면 `{llm 0.625, emb 0.375, rule 0.0}`), `forced_reason` 어휘 +1 `penalized_candidate`(강등은 `band`/`forced_reason`/`action` 3키만 바꾸고 `band_by_threshold`·`confidence`·`matched_person_id` 보존). ask_user 재개(`POST /answers/{question_id}`)는 강등 케이스도 기존 `identity` 경로와 같다(`pending_questions.kind="identity"`, `context.candidate_ids` 에 감점 후보 포함 — R-8).
5. **다음 실 실행 규약.** `… 2>&1 | tee evidence/<ts>-…-real-run.txt; echo "rc=$?" >> 같은 파일`(카드 10 56·76행의 `rc=$?` 줄까지 남긴다). 옛 trace(D12 이전)는 `--recheck-traces` 가 명시적으로 거부하므로 기준선 재검증은 `git show f01ea35:scripts/run_pilot_eval.py` 로.
6. **P4 04-review 220행 대체 기록(R-6).** "`reports/metrics.json` … 덮어쓰지 않는다"는 결정 I(i)(stamp 사본 `reports/pilot/metrics-20260922-042440.json`, CR-001 36행 정정)로 대체됐다. 기준선 = 사본, 최상위 = 재실행 결과.
7. **미커밋 잔여물.** `reports/pilot/metrics-stage.json`·평문 `reports/pilot/raw-20260922-150931.jsonl`(7.7MB, 5MB 한도)은 커밋하지 않는다(U5 03-log). verify-impl 1·2차가 만든 `evidence/<ts>-{pytest,lint,commits,summary}.txt` 중복은 메인 세션이 정리한다.

결과: 완료
승인: 사용자 (2026-09-23)

## 8. 기계 검증 2차 출력 (04-review 작성 후)
명령: `POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-impl.sh P4b-er-redesign | tee docs/wiki/packages/P4b-er-redesign/evidence/20260923-1253-review-verify-impl-2.txt`
```
== verify-impl P4b-er-redesign  (20260923-1253) ==
........................................................................ [ 97%]
.............................                                            [100%]
1325 passed in 158.59s (0:02:38)
PASS  pytest 통과 → evidence/20260923-1253-pytest.txt
PASS  compileall 통과 → evidence/20260923-1253-lint.txt
PASS  태그 P4b-er-redesign 커밋 13 건 → evidence/20260923-1253-commits.txt
PASS  커밋에 태그 존재: CR-001
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D12
PASS  커밋에 태그 존재: D13
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: R3
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  D12 "코드에서 지켜야 할 것" 1항 — `co ← evidence/20260923-1242-review-d12-d13-gr
PASS  증거 확인:  D12 2항 — `confidence_breakdown` 에 `weights` ← evidence/20260923-1242-review-d12-d13-gr
PASS  증거 확인:  D12 3항 — `rule_checked > 0`·`rule_passed ==  ← evidence/20260923-1242-review-negative-c
PASS  증거 확인:  D12 4항 · D13 4항 — 회귀 3종(승진 연� ← evidence/20260923-1242-review-regression
PASS  증거 확인:  D13 1항 — `relation_tag_conflict`·`hierarchy_ ← evidence/20260923-1242-review-d12-d13-gr
PASS  증거 확인:  D13 2항 — 3단계 전달 후보 수 == 1단계 ← evidence/20260923-1242-review-regression
PASS  증거 확인:  D13 3항 — 보수 분기를 설정값 하나(`E ← evidence/20260923-1242-review-d12-d13-gr
PASS  증거 확인:  `--recheck-traces` `max_abs_diff=0.0`(weights_eff ← evidence/20260923-1242-review-regression
PASS  증거 확인:  새 stamp `reports/pilot/raw-<ts>.jsonl.gz`·`rep ← evidence/20260923-1242-review-gate-recal
PASS  증거 확인:  `sc-015` 오병합 아님 · `sc-007` 미검출 � ← evidence/20260923-1242-review-gate-recal
PASS  증거 확인:  P4 기준선(`raw-20260922-042440.jsonl.gz`) 미� ← evidence/20260923-1242-review-boundary.t
PASS  증거 확인:  "미달이면 재실행 없이 failure_cases 갱� ← evidence/20260923-1242-review-boundary.t
PASS  증거 확인:  (01-plan 판정 표 1행) 전체 테스트 실패 ← evidence/20260923-1242-pytest.txt (`1325
PASS  증거 확인:  (판정 표 15·16행) `app/` 변경이 허용 5� ← evidence/20260923-1242-review-boundary.t
PASS  증거 확인:  (판정 표 13·14·18·19행) 스키마·격자  ← evidence/20260923-1214-u7-accept-2.txt (
PASS  증거 확인:  (판정 표 20행 · D13 파급 "위험 계측")  ← evidence/20260923-1242-review-gate-recal
PASS  registry 에 P4b-er-redesign 행 있음
WARN  미완료 작업 단위 8 개
== 결과: FAIL=0 WARN=1 → evidence/20260923-1253-summary.txt ==
rc=0
```
FAIL 0 · WARN 1(01-plan 체크박스, §6 V-6). 1차의 "04-review 없음" WARN 소멸, 검토자 = verifier PASS, 수용 기준 표 16행 증거 전부 실재 PASS. 2차가 만든 `20260923-1253-{pytest,lint,commits,summary}.txt` 는 1차(`1242-*`)와 중복 — 정리는 메인 세션.
