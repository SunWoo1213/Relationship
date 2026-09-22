# P4-pilot-eval · 완료 검토 (04-review)

날짜: | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002). 새 컨텍스트에서 파일·evidence·커밋만 보고 판정했다. 구현자·메인 세션의 자기 평가는 입력에 없다.

검토 대상: HEAD `f01ea35` (START `b164f36` … U9 `f01ea35`, 태그 커밋 17건 — `evidence/20260922-1533-commits.txt`). 기준 문서: `01-plan.md` 64~108행(U1~U9·수용 기준·해석 6항·판정 표 13행)·205~228행(결정 A~L), `02-plan-verify.md` §3·§4(R-5~R-7·O-4~O-6), `03-log.md` 11항목, `05-remediation.md`, `docs/backlog.md` 61행, `docs/wiki/verification.md`.

verifier 가 새로 만든 evidence(전부 `docs/wiki/packages/P4-pilot-eval/evidence/`):
- `20260922-1533-review-verify-impl.txt` — `verify-impl.sh` 1차 출력(§1). 스크립트가 함께 만든 `20260922-1533-pytest.txt`(1285 passed)·`-lint.txt`·`-commits.txt`·`-summary.txt`
- `20260922-1535-review-negative.txt` — 부정 케이스 N1~N36 실행 출력(§3). 임시 파일은 `C:/Users/swsj1/AppData/Local/Temp/p4review/` 에만 썼다(`reports/`·`data/` 쓰기 0, 실 LLM 호출 0, `.env` 미독)
- `20260922-1549-review-verify-impl-2.txt` — 04-review 작성 후 재검증(§1b, FAIL 0 / WARN 1). 스크립트가 함께 만든 `20260922-1549-pytest.txt`(1285 passed)·`-lint.txt`·`-commits.txt`·`-summary.txt`

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-impl.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260922-1533-review-verify-impl.txt` (verifier 직접 실행, 04-review 작성 **전**)
```
== verify-impl P4-pilot-eval  (20260922-1533) ==
(pytest 진행 점 … 생략 — 원문은 evidence 파일)
1285 passed in 202.42s (0:03:22)
PASS  pytest 통과 → evidence/20260922-1533-pytest.txt
PASS  compileall 통과 → evidence/20260922-1533-lint.txt
PASS  태그 P4-pilot-eval 커밋 17 건 → evidence/20260922-1533-commits.txt
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: R3
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: R9
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P4-pilot-eval 행 있음
WARN  미완료 작업 단위 9 개
== 결과: FAIL=0 WARN=2 → evidence/20260922-1533-summary.txt ==
```
FAIL 0 / WARN 2. `findings.py … --source verify-impl` → `05-remediation.md` 에 F-14f3ef(04-review 없음 — 이 문서 작성으로 해소, 아래 2차 실행)·F-2f0840(01-plan `- [ ] U1~U9` 9개 미체크 — [권고], §6) 생성, 원인 분석 채움. pytest `SKIPPED` 0(`grep -c SKIPPED` → 0, N36).

### 1b. 2차 실행 (04-review 작성 후 — 증거 열 실재 검사 포함)
명령: `POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-impl.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260922-1549-review-verify-impl-2.txt`
```
== verify-impl P4-pilot-eval  (20260922-1549) ==
PASS  pytest 통과 → evidence/20260922-1549-pytest.txt
PASS  compileall 통과 → evidence/20260922-1549-lint.txt
PASS  태그 P4-pilot-eval 커밋 17 건 → evidence/20260922-1549-commits.txt
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: R3
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: R9
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  [backlog 61행 전문] `reports/metrics.json`, `r ← reports/metrics.json, reports/calibratio
PASS  증거 확인:  [backlog 61행 전문] 미달이면 재시도가  ← reports/failure_cases.md, ea1bbb2, evide
PASS  증거 확인:  해석(i) "파일럿 평가" = `data/scenarios/`  ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(ii) 다섯 방식 키마다 `false_merge_r ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(iii) 보정표 `s_llm` 10칸 × provider· ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(iv) `curve.csv` x 10점 `{0.5…0.95}`, `t ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(v) 두 파일이 실 공급자 실행으� ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(vi)-(i) `failure_cases.md` 가 결과와 � ← reports/failure_cases.md, ea1bbb2
PASS  증거 확인:  해석(vi)-(ii) 통과/미달은 결정 K 로 04- ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  해석(vi)-(iii) 미달이면 같은 설정 재� ← evidence/20260922-1318-u7-real-run.txt, 
PASS  증거 확인:  해석(vi)-(iv) 미달 시 S3.3 카드·`app/er/` ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 1 전체 테스트 `pytest tests/ -q -r ← evidence/20260922-1533-pytest.txt, evide
PASS  증거 확인:  판정표 2·3 dry-run rc=0·`network_calls=0`·` ← evidence/20260922-1430-u9-dry-run.txt, e
PASS  증거 확인:  판정표 4 실 실행 rc=0·`run_mode=real`·토 ← evidence/20260922-1324-u7-real-run.txt, 
PASS  증거 확인:  판정표 5 `metrics.json` 스키마 `--validate` ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 6 보정표 `10 <정수>`  ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 7 곡선 `[0.5…0.95] {'0.3'} 5`  ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 8 `eval.md` 재생성 diff 0줄  ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 9 `git diff --name-only b164f36..HEAD - ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 10 라벨 무변경 `validate_scenarios ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 11 `alembic check`·`tools_check.py` � ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 12 확신도 재계산(표본) abs diff ← evidence/20260922-1535-review-negative.t
PASS  증거 확인:  판정표 13 비용 실측·외삽 `grep -nE "1� ← 150건" reports/cost_estimate.md`
PASS  증거 확인:  판정표 14 게이트(결정 K) `0.8 [] True Tru ← evidence/20260922-1535-review-negative.t
PASS  registry 에 P4-pilot-eval 행 있음
WARN  미완료 작업 단위 9 개
== 결과: FAIL=0 WARN=1 → evidence/20260922-1549-summary.txt ==
```
2차: FAIL 0 / WARN 1(F-2f0840 — 01-plan 체크박스, §6). 증거 확인 24/24 PASS. F-14f3ef 는 이 실행으로 해소(`findings.py` 재실행).

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로만. 판정 셀의 수치는 전부 그 증거 파일 안의 출력이다.

**backlog 61행 원문**(글자 그대로 옮김, 01-plan 76행과 대조 = **SAME** — 차이는 backlog 의 `- [ ] ` 체크박스 접두뿐):
> `[eval-agent] **파일럿 평가** (오병합률·미검출률·보정표·곡선 초안) / 의존: P3, P3-llm-providers / 수용기준: `reports/metrics.json`, `reports/calibration.json` 생성. **미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다**`

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| [backlog 61행 전문] `reports/metrics.json`, `reports/calibration.json` 생성 | reports/metrics.json, reports/calibration.json, ef18143, evidence/20260922-1324-u7-real-run.txt | 통과 — 두 파일이 실 실행(rc=0, `run_mode=real`)으로 생겼고 ef18143 에 커밋됨 |
| [backlog 61행 전문] 미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다 | reports/failure_cases.md, ea1bbb2, evidence/20260922-1354-u8-failure-cases.txt, evidence/20260922-1535-review-negative.txt | 통과(조건절 이행) — 게이트 미달(§4 판정) → 재실행 0(N18: rc=0 실 실행 파일 1개, 커밋 raw stamp 1개) → `failure_cases.md` 존재(ea1bbb2) → `app/`·`data/`·`docs/resolution-plan.md` 변경 0줄(N14). 재설계 자체는 이 패키지 밖(`/devlog change`, 사용자 결정 2026-09-22 — §7) |
| 해석(i) "파일럿 평가" = `data/scenarios/` 실물 40건 전부 × 다섯 방식 | evidence/20260922-1535-review-negative.txt, reports/pilot/raw-20260922-042440.jsonl.gz, evidence/20260922-1324-u7-real-run.txt | 통과 — N1 `40 ['embedding_only','exact_norm','exact_raw','llm_single','proposed'] 7050`; 실행 로그 `[scenario]` 40줄 전부 `ok`, `[rows] 7050 = 141 × 5 × 10` |
| 해석(ii) 다섯 방식 키마다 `false_merge_rate`·`miss_rate` 분리 + `meta.denominator_rule` | evidence/20260922-1535-review-negative.txt, reports/metrics.json | 통과 — N10 `--validate` → `OK`, rc=0; N23 방식 키 순서 `['proposed','exact_raw','exact_norm','embedding_only','llm_single']`, `denominator_rule` 9키(`ambiguous`·`passing_mentions`·`third_category` 포함), N8 표에 방식마다 fm·miss 두 값 |
| 해석(iii) 보정표 `s_llm` 10칸 × provider·model·method + `excluded_clamped` | evidence/20260922-1535-review-negative.txt, reports/calibration.json | 통과 — N11 `10 0`; 그룹 `(proposed, openai, gpt-4o-mini-2024-07-18, n=107)`·`(llm_single, openai, gpt-4o-mini-2024-07-18, n=132)`; `model_configured {'openai':'gpt-4o-mini'}`(R-6: 응답 모델명 ≠ 설정 문자열, 둘 다 기록) |
| 해석(iv) `curve.csv` x 10점 `{0.5…0.95}`, `t_new` 0.3, 3계열 × 5방식 | evidence/20260922-1535-review-negative.txt, reports/curve.csv | 통과 — N12 `[0.5, 0.55, …, 0.95] {'0.3'} 5 150` |
| 해석(v) 두 파일이 실 공급자 실행으로 생김, `meta.provider/model/embedding_model` 이 stub/fake 아님, `run_mode == "real"` | evidence/20260922-1535-review-negative.txt, evidence/20260922-1340-u7-judgment.txt | 통과 — N2 `openai gpt-4o-mini-2024-07-18 text-embedding-3-small real`, `commit 750f11b…`, `run_id run-29621888da00`, `top_k_swept False`; 실행 로그 `network_calls=339 stub_llm_calls=0 stub_embed_calls=0` |
| 해석(vi)-(i) `failure_cases.md` 가 결과와 무관하게 존재 | reports/failure_cases.md, ea1bbb2 | 통과 — 절 12개(§0 메타 … §12 결론), 생성 커밋 ea1bbb2(N19 `first_add=ea1bbb2 MATCH`) |
| 해석(vi)-(ii) 통과/미달은 결정 K 로 04-review 가 한 번만 | evidence/20260922-1535-review-negative.txt, reports/metrics.json | **미달** — N7 `0.8 ['embedding_only'] True False`; N8 독립 재계산 `MATCH: True`(§4 게이트 판정) |
| 해석(vi)-(iii) 미달이면 같은 설정 재실행 evidence 가 없어야 한다 | evidence/20260922-1318-u7-real-run.txt, evidence/20260922-1320-u7-real-run.txt, evidence/20260922-1324-u7-real-run.txt, evidence/20260922-1535-review-negative.txt | 통과 — N18: 1318·1320 은 `[scenario]` 0줄·`network_calls` 줄 없음·`[fail] OperationalError … port 5432` 1줄(두 파일 diff 0줄 = 같은 DB 접속 실패), 1324 만 `[scenario]` 40줄·`[ok]`. 03-log 111~113행이 원인(`.env` `DATABASE_URL` 5432 → `POSTGRES_PORT` 덮음)과 "LLM 0회·과금 0" 을 설명. 커밋된 raw stamp 1개(`git ls-files reports/pilot/` 2파일) |
| 해석(vi)-(iv) 미달 시 S3.3 카드·`app/er/` 를 고치지 않는다(`git diff -- app/` 0줄) | evidence/20260922-1535-review-negative.txt | 통과 — N14 `git diff --name-only b164f36..HEAD -- app/ data/` 0줄, `app/er/` 0줄, 작업 트리 `app/ data/` 0줄, `docs/resolution-plan.md` 0줄, docs/wiki 내 S3.3 파일 0줄 |
| 판정표 1 전체 테스트 `pytest tests/ -q -rs` 실패 0·skip 0 | evidence/20260922-1533-pytest.txt, evidence/20260922-1450-u9-pytest-all.txt | 통과 — verifier 실행 `1285 passed in 202.42s`, `SKIPPED` 0(N36); U9 evidence 도 1285 passed(1차 `2 failed, 1283 passed` → 수정 후, §4 3) |
| 판정표 2·3 dry-run rc=0·`network_calls=0`·`run_mode=stub`·시나리오마다 `embedded == aliases` | evidence/20260922-1430-u9-dry-run.txt, evidence/20260922-1533-pytest.txt | 통과 — U9 evidence `[ok] 사슬 완료`, `network_calls=0 stub_llm_calls=277 stub_embed_calls=62`, `[rows] 7050`(verifier 는 재실행하지 않았다 — 같은 HEAD 의 pytest 1285 에 사슬 층 테스트(`test_run_pilot_eval.py` 사슬 5+2+11건, DB 사용)가 포함돼 돌았다) |
| 판정표 4 실 실행 rc=0·`run_mode=real`·토큰 합계 | evidence/20260922-1324-u7-real-run.txt, ef18143 | 통과 — `[run] run_mode=real network_calls=339`, `tokens_in=130240 tokens_out=12617`, 사슬 6단계 `rc=0`, `[traces] dumped=1410 recomputed=1410 max_abs_diff=0.0`, `[gzip] roundtrip … ok`, `[size] … ok` 2줄 |
| 판정표 5 `metrics.json` 스키마 `--validate` rc=0 | evidence/20260922-1535-review-negative.txt | 통과 — N10 `OK reports/metrics.json` rc=0 |
| 판정표 6 보정표 `10 <정수>` | evidence/20260922-1535-review-negative.txt | 통과 — N11 `10 0` |
| 판정표 7 곡선 `[0.5…0.95] {'0.3'} 5` | evidence/20260922-1535-review-negative.txt | 통과 — N12 |
| 판정표 8 `eval.md` 재생성 diff 0줄 | evidence/20260922-1535-review-negative.txt | 통과 — N9 `report rc=0`, `diff rc=0`, `reports/eval.md == reports/pilot/eval.md` |
| 판정표 9 `git diff --name-only b164f36..HEAD -- app/ data/` 0줄 | evidence/20260922-1535-review-negative.txt | 통과 — N14 `lines=0` |
| 판정표 10 라벨 무변경 `validate_scenarios --strict --json` rc=0·`total` 40 | evidence/20260922-1535-review-negative.txt | 통과 — N13 재실행 `total 40 ok True issue_count 0 {'alias':8,'new_person':6,'normal':10,'promotion':8,'pronoun':8} ambiguous 3 traps 12` (N13 1차의 python 읽기 오류는 verifier 의 POSIX 경로 표기 실수, validate 자체는 rc=0) |
| 판정표 11 `alembic check`·`tools_check.py` 무변경 | evidence/20260922-1535-review-negative.txt, evidence/20260922-1340-u7-judgment.txt | 통과 — N35 `No new upgrade operations detected.` rc=0 · `RESULT: 7/7 ok` rc=0 |
| 판정표 12 확신도 재계산(표본) abs diff 0, 실행 로그와 같은 ts | evidence/20260922-1535-review-negative.txt, reports/pilot/traces-20260922-042440.jsonl, evidence/20260922-1324-u7-real-run.txt | 통과 — N6 `--recheck-traces` → `dumped=1410 recomputed=1410 max_abs_diff=0.0`(전량, 표본 아님); stamp `042440`(UTC) = raw 와 동일, 실행 로그 13:24 KST 와 대응(N25 ef18143 `13:39 +0900` 커밋) |
| 판정표 13 비용 실측·외삽 `grep -nE "1건당|150건" reports/cost_estimate.md` | reports/cost_estimate.md, 0283ac0, ef18143 | 통과 — 50·51행 1건당 3,256 / 315.4 토큰(실측), 70행 150건 × 5방식 × 10임계치 ≈ $0.10(외삽), 64행 제목에 5방식 기준. 임베딩 토큰은 "실측 없음" 으로 정직하게 적음 |
| 판정표 14 게이트(결정 K) `0.8 [] True True` 면 통과 | evidence/20260922-1535-review-negative.txt, reports/metrics.json, reports/eval.md | **미달** — N7 `0.8 ['embedding_only'] True False`. §4 참조 |

수용 기준 대조 요약: 문장 2조항 + 해석 6항(vi 는 4소항) + 판정 표 14행 — 전부 증거로 확인됐고, 그중 게이트 2행이 **미달**이다. 미달은 수용 기준의 조건절("미달이면 …")이 정의한 결과이며, 조건절의 이행(실패 케이스 분석·재실행 0·`app/` 무수정)은 통과다.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 verifier 가 직접 실행. 출력 전문: `evidence/20260922-1535-review-negative.txt`(N 번호). 임시 출력은 `C:/Users/swsj1/AppData/Local/Temp/p4review/` 에만.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 커밋본 `.gz` 하나로 U2 지표가 같은 바이트로 다시 나오는가(원칙8) | `python -m evaluation.metrics --rows reports/pilot/raw-20260922-042440.jsonl.gz --out <tmp>/metrics-recheck.json` → `cmp` 사슬 `metrics-stage.json`; 5 방식 블록을 `reports/metrics.json` 의 최상위 5키와 `==` 비교, `meta` 는 공통 9키만 비교(`caller_supplied` 6키 `embedding_model/dataset_hash/run_id/model_configured/commit/run_mode` 는 curve 단계 호출자 인자라 U2 산출물에 없음) | N3 — `cmp metrics-stage.json: 바이트 동일`, `method blocks equal … count 5 diff []`, `meta common diff keys: []` |
| 커밋본 `.gz` + 사슬과 같은 인자로 U4 `metrics.json`·`curve.csv` 가 **바이트 동일**하게 재생성되는가 | `python -m evaluation.curve --rows ….gz --out <tmp>/metrics.json --curve <tmp>/curve.csv --dataset-hash sha256:49cd8c… --run-id run-29621888da00 --embedding-model text-embedding-3-small --model-configured openai=gpt-4o-mini --run-mode real --commit 750f11b…` → `cmp` | N4 — `cmp reports/metrics.json: 바이트 동일`, `cmp reports/curve.csv: 바이트 동일`, sha256 `25e16dd6…` 3파일 동일(tmp·`reports/`·`reports/pilot/`) |
| 커밋본 `.gz` 로 U3 보정표 바이트 동일 | `python -m evaluation.calibration --rows ….gz --out <tmp>/calibration.json --t-merge 0.8 --model-configured openai=gpt-4o-mini` → `cmp` | N5 — `cmp reports/calibration.json: 바이트 동일` |
| trace 전량 재계산 abs diff 0 (DB·네트워크 0) | `python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-20260922-042440.jsonl` | N6 — `dumped=1410 recomputed=1410 max_abs_diff=0.0`, rc=0 |
| 게이트 명령(01-plan 108행) | `python -c "import json;g=json.load(open('reports/metrics.json'))['gate'];print(g['t_merge'],g['dominated_by'],g['d10_direction'],g['pass'])"` (`PYTHONUTF8=1`) | N7 — `0.8 ['embedding_only'] True False` |
| 게이트 **독립 재계산**(O-4 — U4 코드의 자기 보고를 믿지 않는다) | verifier 스크립트 `gate_recheck.py`: 5방식 `by_t_merge["0.8"]` 의 `{n,d,rate}` 로 지배식(≤,≤, 하나는 <)과 D10 연속 쌍 단조를 직접 계산 | N8 — `embedding_only fm=0.0000(0/132) miss=0.0076(1/132) dominates=True`, 나머지 3 False; 제안 곡선 fm `[0.0455,…,0.0076]` 비증가·ask(identity) `[0.1667,…,0.8636]` 비감소 → `INDEPENDENT: dominated_by=['embedding_only'] d10=True pass=False` = 파일 값, `MATCH: True` |
| `eval.md` 멱등 | `python -m evaluation.report --metrics reports/metrics.json --out <tmp>/eval.md && diff <tmp>/eval.md reports/eval.md` | N9 — diff 0줄(rc=0) |
| `--validate` / 보정표 / 곡선 / 라벨 / alembic·tools | 01-plan 99·100·101·104·105행 명령 | N10 `OK` · N11 `10 0` · N12 `… {'0.3'} 5 150` · N13 `total 40 … issue_count 0` · N35 `No new upgrade operations detected.` `7/7 ok` |
| 제품 코드·데이터·S3.3 무변경 | `git diff --name-only b164f36..HEAD -- app/ data/`; `-- app/er/`; `-- docs/resolution-plan.md`; docs/wiki S3.3 grep | N14 — 전부 0줄 |
| 패키지 범위 밖 파일 변경(01-plan "하지 않는 것" 침범) | `git diff --name-only b164f36..HEAD \| grep -v packages/P4-pilot-eval/` | N15 — 31파일: `evaluation/*.py` 5·`scripts/run_pilot_eval.py`·`tests/test_eval_*.py`·`test_run_pilot_eval.py`·`reports/*` 8·README·`docs/user-setup/10`·`README`·registry·review-index·HANDOFF·journal·P3-baselines 04-review/evidence·P3-er 05-remediation/evidence — 모두 01-plan 산출물 목록(38~59행)·인계 13 이관·F-87c597 해소 범위. `app/`·`data/`·프론트·루프 파일 0 |
| 키 문자열 혼입 | `grep -c 'sk-'` (gz 는 `gzip -dc \|`) 산출물 8 + evidence 7 | N16 — 전부 0 |
| 실 실행 로그·덤프에 프롬프트 원문·키 없음 | `grep -ciE 'api_key\|Bearer \|prompt:\|messages'` 1324 로그; `grep -n OPENAI_API_KEY`; traces `"prompt"`·`"reason"` 키 수; raw `"prompt"` | N17 — 0 / (없음) / `0 / 0` (1410줄) / 0 |
| 같은 설정 재실행 없음(수용 기준 (iii)) | 1318·1320·1324 의 `[scenario]` 줄 수·`network_calls`·`[fail]`/`[ok]`; `git ls-files reports/pilot/` | N18 — `0 / (없음) / fail 1 / ok 0` × 2, 1324 `40 / 339 / 0 / 1`; 커밋 raw 1개·traces 1개 |
| 평문 raw(7.5MB)가 커밋되지 않았는가(훅 5MB·결정 E gzip) | `git ls-files reports/pilot/raw-20260922-042440.jsonl \| wc -l` | N22 — `0`. 작업 트리에 untracked 6개(평문 raw·`metrics-stage.json`·pilot 사본 4) 잔존 — §6 [권고] |
| registry 21행 경로 실재·생성 커밋 일치·`pending` 0 | `git log --diff-filter=A --format=%h -- <경로> \| tail -1` 21회, `grep -c 'P4-pilot-eval \| pending'` | N19 — 21행 전부 `exists=Y … MATCH`, `pending: 0`, `\| reports/metrics.json \|` 행 1 |
| f01ea35 테스트 수정이 실패 조건을 여전히 검사하는가(항상 통과 테스트 아님) | `git show f01ea35 -- tests/test_run_pilot_eval.py` | N21 — `test_stub_output_cannot_land_in_reports`: `rc == RC_ERROR` + `"reports/" in out` + `_reports_snapshot() == before`(크기·mtime_ns 전 파일) / `test_dry_run_leaves_no_rows_and_no_reports_files`: `persons` 증분 0 + 스냅샷 동일. "부재" 단언을 "불변" 단언으로 바꿨을 뿐 거부·무기록 조건은 그대로 검사한다 |
| U8 핵심 수치 독립 재계산(raw.gz 직접) | verifier 스크립트 `u8_recheck.py`·`u8_recheck2.py`·`u8_recheck3.py` | N31·N33·N34 — 오병합 1 `('sc-015',0,'부장님',11931,gold 11930)`, 미검출 1 `('sc-007',2,'문실장님')`, deferred 79, `s_llm≥0.9 & matched: 98/101 = 0.970`, `rule_checked==0` 최대 confidence `0.8000`, forced `{no_matched 25, no_candidates 5}`, deferred 분해 20(강제)+52(`rule_checked`=0)+7(=3) = 79, `[0.7,0.8)` 52, `embedding_only` on deferred-79 = `merge_correct 52 / identity 24 / new_person_correct 2 / miss 1` — failure_cases §1·§2·§3·§4a·§4d·§4f·§4g 와 **전부 일치** |
| 보정표 0.9-1.0 칸 vs failure_cases §4g 97.0% | `calibration.json groups[*].bins` 출력 | N28 — `proposed 0.9-1.0: n=101 correct=47 acc=0.465`, `llm_single 0.9-1.0: 117/103 0.880`; `excluded {placeholder_s_llm 20, llm_skipped 5, passing 12, ambiguous 6}`. 두 수치는 정답 정의가 다르다(결정 F(i) vs 귀속 일치) — failure_cases 257행이 이를 명시. §6 [권고] |

부정 케이스 20건 중 20건 통과(게이트 명령은 "미달을 정확히 보고하는가" 로 통과). 재실행하지 않은 것: `--dry-run --stub` 전량(U9 evidence 인용, 사슬 층은 pytest 로 커버).

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)

### 4a. 판단 검토(03-log 의 판단이 카드·원칙과 맞는가)

| 판단 | 카드·원칙 | 확인 |
|---|---|---|
| 결정 A(ii) OpenAI 1벌 | 01-plan 213행 | N2 `provider openai`, `models_observed` 단일 — 정합 |
| 결정 B(i) `--max-cost-usd` $5, cost_estimate 채움 | 214행·backlog 15행 | 1324 로그 `max_cost_usd=5.0`; `cost_estimate.md` §3·§4 실측·외삽(판정표 13) — 정합. 실측 $0.0271(단가 상수, 임베딩 제외) |
| 결정 C(i) LLM mention 당 1회 → 밴드 10벌 | 215행 | N23 `proposed calls 136 = 141 − skipped 5`, `llm_single 141`; N31 `llm_fresh_call` 행 기준 집계 — 정합 |
| 결정 D(i) 시나리오별 롤백, trace 는 실행 중 덤프 | 216행, R-4 | 1324 로그 `[scenario] … ok` 40줄(누수면 `RunnerError`), traces stamp = raw stamp, N6 — 정합 |
| 결정 E 원시 커밋 → gzip 이행(사용자 2026-09-21) | 205행 개정 주석, 1a5643b·1c84d35 | N22 `.gz` 커밋·평문 미커밋, N3·N4 `.gz` 단독 재계산 바이트 동일 — 정합. 결정 E 의 결론(원시 전부 커밋)·훅 무변경 유지 |
| 결정 F(i) 정답 = decision+person_id 골드 일치 | 218행 | N28 `correct_definition` 문자열 — 정합. 부작용은 §6 [권고] |
| 결정 G F-251dc2 불필요 명시·`app/` 무수정 | 194·207행 | 01-plan 194행 문장 존재, N14 `app/` 0줄 — 정합(§6) |
| 결정 H `top_k` 미스윕 | 195·208행 | N2 `top_k_swept False` — 정합 |
| 결정 I 스모크 03·08 선행 | 209행 | `evidence/20260921-2011-smoke03-er-real.txt`(09-21 20:11)·`20260922-1309-smoke08-baseline-real.txt`(09-22 13:09) 모두 U7(13:24) 전, `20260922-1320-u6-smoke-handover.txt` — 정합. U6 시점 이관 생략은 03-log 57행 (6) 에 사용자 결정으로 기록 |
| 결정 J `curve.csv` + Markdown 표, PNG 없음 | 210행 | N32 `reports/*.png` 0, `eval.md` 'png' 0 — 정합 |
| 결정 K 지배 기준 → 아래 4b | 227행 | N7·N8 |
| 결정 L 제3 범주 = `identity` 만 | 228행·65행 해석 | N23 `denominator_rule.third_category`, `eval.md` 한계 절 인용 — 정합 |
| 테스트 전제 결함 2건 수정(f01ea35, 메인 세션) | 03-log 134행, 원칙8 | N21 — 검사 의도 유지(§3). 수정 범위 `tests/` 1파일 +18/−2, `app/`·`evaluation/`·`scripts/` 0. "메인은 조율만" 의 예외를 사용자 결정으로 기록 — 절차 정합 |
| U8 S3.3 단계 귀속(2단계 규칙 필터 = 오류 2건, 4단계 확신도 상한 = 마찰 52건) | S3.3, 원칙1·3·8 | N31·N33·N34 재계산이 §1·§2·§4 수치와 일치. 귀속 논리: 오병합 sc-015 는 `excluded_by` 로 골드(11930) 제외 후 단독 후보 11931 에 `s_llm 0.9·s_emb 1.0·s_rule 1.0 → 0.95`(trace 73821, U8 evidence 137행) — 2단계 귀속 타당. 미검출 sc-007 은 `no_candidates`(cands=1, 제외 후 0) — 2단계 귀속 타당. deferred 52건은 `rule_checked=0 → s_rule=0 → 상한 0.80`(N31 max 0.8000) — 4단계 귀속 타당. 반사실(0.625/0.375)은 재실행이 아니라고 §10 이 명시 — 원칙8 정합. 결론 문장 "표본 40건이므로 방향과 유형까지"(§12) — 인계 15 정합 |
| U8 결정 K 판정을 다시 내리지 않음 | 해석 (ii) | failure_cases §0·§12 "`metrics.json.gate` 대로" — 정합 |

### 4b. 게이트 판정 (결정 K 개정 (a), 여기서 한 번만)

`reports/metrics.json.gate`(인용, N7·N8):
```
t_merge=0.8  proposed: false_merge_rate 1/132 (0.00758) · miss_rate 1/132 (0.00758)
embedding_only: 0/132 · 1/132 → dominates_proposed=true   (오병합 0 < 1 엄격, 미검출 동률)
exact_raw 0/132 · 33/132 false · exact_norm 4/132 · 20/132 false · llm_single 0/132 · 10/132 false
dominated_by=['embedding_only']  undetermined=[]  d10_direction=true  reason=None  pass=false
```
독립 재계산(N8) 동일. **판정: 미달.** 근거는 결정 K (a) 의 문장 그대로 — `T_merge=0.8` 에서 베이스라인 `embedding_only` 가 제안 방식을 지배한다(오병합률 0 ≤ 0.0076 이고 미검출률 0.0076 ≤ 0.0076, 오병합 축이 엄격히 작다). D10 방향은 9쌍 위반 0 으로 충족. 따라서 01-plan 수용 기준 해석 (ii)·결정 K 마지막 문장에 따라 결과는 **부분완료 + 실패 케이스 분석**이며 P5 는 착수하지 않는다. 오병합률 순위(O-5, `eval.md` 88~98행): `exact_raw`·`embedding_only`·`llm_single` 0/132, `proposed` 1/132, `exact_norm` 4/132 — 원칙1 축에서도 제안 방식이 우위가 아니다.

### 4c. R 상태
- R3(D10 두 임계치 방향): `d10_direction=true`(N8 곡선 값) — 구현완료 상태 유지(P3-er 에서 닫힘). review-index 갱신 대상 아님.
- R4(자기보고 `s_llm` 보정): `reports/calibration.json`(ef18143) 실물 존재, 실호출 확인(750f11b). review-index 12행 갱신 **제안**(파일은 메인 세션이 고친다):
  > `R4 | H | … | 구현완료(b1f2782 …; 실호출 확인(2026-09-21 사용자 스모크 03 …); **보정표 실물**(2026-09-22 P4 U7 ef18143 `reports/calibration.json` — openai gpt-4o-mini-2024-07-18, 10구간, excluded_clamped 0, 정답 정의 결정 F(i); `proposed` 0.9-1.0 칸 47/101(F(i), deferred 오답 처리)·귀속 일치 98/101 = 97.0%(failure_cases §4g) — 두 정의 병기는 P10 결정 F(iii) 후보) — F-87c597 해소)`
- R9(인물당 임베딩 1개 → 별칭 단위): review-index 17행 "**실 공급자 호출 미검증**, P4 에서 실측" → 갱신 **제안**:
  > `구현완료(4dfaf33, 09c2bd1, a9cb254, 2c63c60 — 별칭 단위 임베딩·top-K 인물별 max·OpenAIEmbeddingProvider 런타임; **실 공급자 호출 확인**(2026-09-22 P4 U7 ef18143 — text-embedding-3-small N=1536, 40 시나리오 별칭 임베딩 `embedded == aliases` 40/40, 임베딩 배치 62회, `evidence/20260922-1324-u7-real-run.txt`; `embedding_only` 베이스라인 오병합 0/132 — 별칭 max 집계가 실 임베딩에서 동작))`

## 5. registry.md 에 올린 산출물
- P4-pilot-eval 행 **21개**(127~147행), `pending` 0(N19). 경로 21개 전부 실재하고 등록 커밋 = `git log --diff-filter=A` 첫 커밋(`MATCH` 21/21): runner·test_eval_runner `fb81234` / metrics·test_eval_metrics `a97521b` / calibration·test `ee124b7` / curve·test `a59ecb4` / report·test `dd6a996` / run_pilot_eval·test·cost_estimate·카드 10 `0283ac0` / raw.gz·traces·metrics.json·calibration.json·curve.csv·eval.md `ef18143` / failure_cases.md `ea1bbb2`.
- `| reports/metrics.json |` 행 1개 → F-95c6a7 해소 조건 충족(§6).
- **미달**: registry 33행(README, 패키지 "하네스") 비고에 `P4-pilot-eval` 언급 0(N19·N29 `grep -c` → 0). README 자체에는 `### 파일럿 평가 실행법 (P4)` 절(330행)이 있다. → F-0ffff5 유지(§6).

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

| id | 분류 | 판정 | 근거(명령·출력) | 다음 조치(누가) |
|---|---|---|---|---|
| F-251dc2 (P3-er) | [권고] | **P4 측 해소 조건 충족** — 해결 단계 (b) "P4 01-plan 문장" 이행 | 01-plan 194행 "결정 G: (b) 불필요를 명시한다"(N27 grep), `git diff b164f36..HEAD -- app/` 0줄. U8 은 `matched_names=None` 으로 그 한계를 안고 분석(evidence 140행) | P3-er `05-remediation.md` 상태 줄 `열림→해소` 는 메인 세션(verifier 파일 아님). 두 필드 보존은 P5 이전 사소 FIX 후보로 남음 |
| F-bdd6c5 (P3-er) | [권고] | **P4 측 해소 조건 충족** — "`top_k` 스윕 금지 명시" 이행 | N2 `top_k_swept False`, `eval.md` 실행 메타 행 "결정 H(i)·F-bdd6c5" | 같은 방식으로 메인 세션이 상태 갱신. `search_person` 내부 주입 FIX 는 P5 이전 후보(유지) |
| F-95c6a7 | [권고] | **해소** | 완료 판정 명령 `grep -c "\| reports/metrics.json" docs/wiki/registry.md` → `1`(N19) | 05-remediation 상태 갱신(verifier, 이 검토에서) |
| F-0ffff5 | [권고] | **유지(열림)** | 완료 판정 명령 `sed -n 33p docs/wiki/registry.md \| grep -c P4-pilot-eval` → `0`(N19·N29). README 절은 있음(330행) | 종료 커밋에서 registry 33행 비고에 `P4-pilot-eval U9: "파일럿 평가 실행법" 절 추가(f01ea35)` 한 줄(메인 세션) |
| F-14f3ef | [권고] | 04-review 작성으로 해소 — §1b 2차 실행 | verify-impl 2차 출력 | verifier(이 검토) |
| F-2f0840 | [권고] | **유지** — 01-plan `- [ ] U1~U9` 9개 미체크 | `grep -cE '^- \[ \] U[0-9]' 01-plan.md` → 9 (N29) | 종료 커밋에서 U1~U9 를 `- [x]` 로(메인 세션). 코드·결과 결함 아님 |
| 03-log U7 결함 (1) 카드 10·01-plan 판정 명령 encoding | [권고] → 닫힘 | f01ea35 가 `PYTHONUTF8=1` 각주로 처리(카드 10·01-plan 92행), 명령 본문 불변 | — |
| 03-log U7 결함 (2) 러너가 DB 접속 전 `resolve_connection().safe_summary()` 를 찍지 않아 1318·1320 실패 원인을 로그만으로 알 수 없음 | **[권고] FIX 후보(코드, 미수정)** | 1318 로그에 `port 5432` 는 psycopg 오류문에만 있고 `[warn] POSTGRES_PORT 가 DATABASE_URL 과 다르다` 경고가 없음(N18). 비밀 없는 1줄 출력이므로 `scripts/run_pilot_eval.py` 사소 FIX. 실 실행 산출물 무관 | P5 이전 사소 FIX(사용자 승인), `app/` 아님 |
| 03-log U7 결함 (3) raw/traces stamp UTC | [권고] | registry 140행에 "stamp 는 UTC" 기록됨. 카드 10 에는 미기재 | 카드 10 한 줄(문서) — 선택 |
| 03-log Refs ↔ 커밋 Refs 불일치 | [권고] 하네스 관찰 | N20: fb81234 커밋 `D11` 은 03-log U1 Refs 에 없음; 0283ac0 커밋 `S3.7 원칙2` ↔ 03-log U6 `D5`; ef18143·ea1bbb2·f01ea35 커밋 Refs 에 03-log 의 `원칙n`·`L-nnn` 태그 일부 없음. verify-impl 4번은 D/S/R/FIX/CR 태그만 검사해 PASS | L-nnn 후보(하네스): `/commit` 이 03-log Refs 와 커밋 Refs 를 같은 문자열로 쓰게 |
| `reports/pilot/` untracked 6파일(평문 raw 7,545,838 B·`metrics-stage.json`·pilot 사본 4) | [권고] | N22 `git status --porcelain reports/` — 커밋되지 않았고 훅이 막는다. verifier 는 삭제하지 않는다(재귀 삭제 금지) | 사용자 결정: 삭제 또는 `.gitignore reports/pilot/*.jsonl` |
| 보정표 정답 정의 F(i) 의 부작용 | [권고] R4 해석 | N28: `proposed 0.9-1.0` 47/101(46.5%) 은 deferred 79 가 전부 "오답" 으로 잡힌 결과 — LLM 자기보고의 신뢰도가 아니라 `T_merge` 게이트 통과 여부를 잰다. 같은 구간 귀속 일치는 98/101(N31). failure_cases 257행이 명시 | P10: 결정 F(iii) "둘 다 보고" 로 보정표에 두 정의 병기 검토(CR 아님, P10 계획) |
| `mention_index` 가 turn 안에서 mention_kind 간 비유일 | [권고] P10 인계 | N34: `(sid,turn,mention_index)` 충돌 4건(sc-038 t2 m1·sc-039 t2 m1·sc-040 t0 m0·sc-040 t2 m1 — passing 과 gold 가 같은 index). `(sid,turn,mention)` 또는 `+mention_kind` 로는 141 유일 | P10 JSONL 조인 키 규약에 `mention_kind` 포함 |

열린 [필수] 소견 0. 열린 [권고] 중 P4 종료 커밋에서 닫을 수 있는 것: F-0ffff5(비고 1줄)·F-2f0840(체크박스 9개).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

**P5(에이전트 루프) — 착수 금지 상태.** 결정 K 미달(4b). `/devlog change` 와 사용자 결정 이후에만. P5 가 그때 받을 것: 러너 env 규약 `LLM_PROVIDER=openai` 명시·`LLM_PROVIDERS_ENABLED` 미설정(`evaluation/runner.py::build_runner_env`), `ask_user(kind=schedule)` 은 mention 해석이 만들지 않아 P4 에서 언제나 n=0(`denominator_rule.ask_user`) — P5 루프가 만든 뒤 P10 이 잰다.

**CR(사용자 결정 2026-09-22: ① 4단계 미측정 신호 가중치 재정규화 + ② 2단계 규칙 필터 배제→감점) — 영향 범위에 필요한 사실만:**
1. 원칙 문장: `CLAUDE.md` 38행 원칙3 `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule` — ① 은 이 산식의 분모(관측 신호만)를 바꾼다. D3 카드·S3.3 카드가 같은 산식을 가진다(카드 파일은 `docs/wiki/INDEX.md` 태그로).
2. 코드 단일 출처: `app/er/confidence.py::combine()`(64행)·`_breakdown()`(133행, `rule_checked` 기록 151행); 배제 규칙 `app/er/rules.py` `_CONFLICT_PRIORITY`(54행)·`relation_tag_conflict`(96행)·`hierarchy_conflict`(108행)·완화 재검색 조건(167행). 가중치 상수 `app/settings.py:78 ER_WEIGHTS`(환경변수 `W_LLM/W_EMB/W_RULE` 140~142행).
3. P4 도구가 ① 에 걸리는 곳: `scripts/run_pilot_eval.py` 재계산이 trace `confidence_breakdown.weights` 가 `ER_WEIGHTS` 와 다르면 **거부**(66·135·720행, 테스트 "weights 가 ER_WEIGHTS 와 다르면 거부") — 재정규화된 유효 가중치를 trace 에 적으면 `--recheck-traces` 가 rc=1 이 된다. `evaluation/curve.py` `meta.weights` 는 `ERConfig()` 기본값을 읽는다. `evaluation/calibration.py` placeholder 판정은 `matched_person_id is None`(② 로 후보 배제가 줄면 placeholder 20 → 감소).
4. 재실행 규약: 새 실행은 새 stamp(`raw-<ts>.jsonl.gz`)·새 `run_id`·새 `meta.commit` 으로 남기고 `reports/pilot/raw-20260922-042440.jsonl.gz`·`traces-…`·현재 `metrics.json`(sha256 `25e16dd6…`)은 **덮어쓰지 않는다**(원칙8 — 비교 기준선). 비용 기준 40건 $0.0271(단가 상수).
5. 기대 효과의 기준선(재실행 아님, failure_cases §8 반사실): ① 만 적용 시 `T_merge 0.8` merge 48→97·골드 일치 96·오병합 1 유지. ② 는 반사실 계산 불가(후보 집합이 바뀜) — 40건으로 검증 불가하다고 §8 이 적음. 오병합 1건(sc-015)은 ② 의 대상, 미검출 1건(sc-007)도 ② 의 대상.
6. 회귀 대상 테스트: `tests/test_er_*`(P3-er), `tests/test_eval_*`·`tests/test_run_pilot_eval.py`(P4 — 특히 `combine()` 소스 문자열 단언·가중치 거부 테스트는 CR 후 기대값 갱신 필요).
7. 게이트 재판정은 같은 결정 K (a) 식으로 04-review 가 한 번만(재설계 후 P4 재실행 패키지 또는 P10).

**P10(150건 최종 평가):**
- 결정 F(iii) 검토(§6), `mention_index` 조인 키(§6), 임베딩 토큰 실측(사용량 API 미조회 — `cost_estimate.md` 52행), 신뢰구간, `exact_*`·`llm_single` 평탄 곡선 해석(R-5), 이벤트 추출 F1·툴 호출 정확도(P4 범위 밖, 01-plan 35행), PNG 곡선(결정 J(iii)).
- 판정 명령은 `PYTHONUTF8=1` 접두(Windows cp949) — 카드 10·01-plan 92행 각주.
- Gemini·Anthropic 실호출 0(failure_cases §10) — "LLM 판정이 정확하다" 는 gpt-4o-mini-2024-07-18 한정.

**하네스:** F-2f0840(체크박스)·F-0ffff5(registry 비고) 종료 커밋 처리; 03-log Refs = 커밋 Refs 규칙(L-nnn 후보); `verify-plan.sh` 5번 basename 오탐(F-95c6a7 계열) 관찰 유지; 러너 `safe_summary` 사소 FIX 후보.

결과: 부분완료 — 근거: 수용 기준 문장 2조항·해석 6항·판정 표 14행이 전부 증거로 확인됐고(§2), 부정 케이스 20/20(§3), verify-impl FAIL 0(§1), 열린 [필수] 소견 0(§6). 그러나 결정 K (a) 게이트가 **미달**(`dominated_by=['embedding_only']`, 4b — 독립 재계산 일치)이므로 01-plan 수용 기준 해석 (ii)·결정 K 마지막 문장·원칙8 에 따라 "부분완료 + 실패 케이스 분석(`reports/failure_cases.md`, ea1bbb2)" 이다. P5 미착수. 다음은 `/devlog change`(CR ①+②, 사용자 결정 완료).
승인: 사용자 (2026-09-22) — 부분완료(게이트 미달 + 실패 케이스 분석). 다음: /devlog change(CR ①+②)
