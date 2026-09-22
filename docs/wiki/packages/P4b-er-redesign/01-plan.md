# P4b-er-redesign · 계획 (01-plan)

상태: 초안 | 담당: backend-agent(`app/`) + eval-agent(`evaluation/`·`scripts/`·`reports/`) + 사용자(실 실행) | 작성: 2026-09-22
태그 — 패키지: P4b-er-redesign · 닫는 검증: R3 R4(재검증) · 기대는 결정: **D12 D13** D10 D4 D5 D11 · 구현하는 명세: **S3.3**(S3.7 불변) · 관련 원칙: 원칙1 원칙2 원칙3 원칙4 원칙8 원칙9 · 변경 요청: **CR-001**
의존:
- **CR-001 이행완료(문서)** — `e4109cc`(`.claude/gitlog.md` 최근 커밋 1행, dev HEAD). D12·D13 카드 신설, D3 대체됨, S3.3 7·9·19행·CLAUDE.md 원칙3·backlog P4b 행·INDEX 71행 갱신. `CURRENT.md frozen: none`(코드 쓰기 차단 해제).
- **P4-pilot-eval 부분완료** — `adf9f1b`(04-review 부분완료·사용자 승인). 그 안의 실 실행 `ef18143`(openai `gpt-4o-mini-2024-07-18` + `text-embedding-3-small` N=1536, 40 시나리오·141 mention·7050행), 실패 케이스 분석 `ea1bbb2`, 기계 검증 `f01ea35`(1285 passed). 이 패키지의 **기준선**이자 비교 대상이다.
- **P3-er 완료**(04-review `완료`) — 고칠 코드의 출처. `docs/wiki/registry.md` 81행 `app/er/rules.py`(`02e6f14`) · 82행 `app/er/confidence.py`(`593c254`) · 85행 `app/er/pipeline.py`(`d6e5949` U6 → `cc5d24f` U7). CR-001 30행이 말한 "P3-er U3 규칙 필터 / U4 확신도 결합 / U6 trace" 가 이 세 커밋이다. `.claude/gitlog.md` 스냅샷은 최근 20건만 담아 P3-er 커밋이 보이지 않는다 — **태그별 이력이 필요하면 메인 세션에 `bash .claude/scripts/gitlog.sh P3-er D3` 실행을 요청한다**(이 문서는 registry 등록 해시를 근거로 썼다, L-001).
- **P1-pilot-dataset 완료** — `data/scenarios/` 40건. 이 패키지는 **데이터를 고치지 않는다**.
- 시작 해시(무변경 diff 의 기준점) = **`e4109cc`**. 스냅샷 시점 `dev` 는 `origin/dev` 보다 2 앞서고 미커밋 변경은 `docs/wiki/journal.md` 1건뿐이다(제품 코드 0).
- **이 패키지가 P5 이후의 게이트다**(backlog 70행 "의존: P3, **P4b 게이트 통과**", INDEX 81행). P4 가 미달이므로 P5·P6·P8 은 이 패키지의 04-review 가 `pass` 를 확인하기 전에는 시작하지 않는다.

## 목표

P4 파일럿 평가가 결정 K (a) 게이트에서 미달했다 — `T_merge=0.8` 에서 베이스라인 `embedding_only`(오병합 0/132·미검출 1/132)가 제안 방식(오병합 1/132·미검출 1/132)을 지배했다(`dominated_by=['embedding_only']`, 04-review §4b). `reports/failure_cases.md` §8 이 그 원인을 S3.3 의 **2단계와 4단계**로 귀속했고 — 2단계 규칙 필터가 골드 후보를 떨어뜨린 mention 6건(`relation_tag_conflict` 2·`hierarchy_conflict` 4)이 오병합 1건(`sc-015` t0 "부장님")과 미검출 1건(`sc-007` t2 "문실장님")의 출발점이며, 4단계가 미측정 `s_rule`(`rule_checked == 0`, 141 중 100)을 0 으로 합산해 확신도 상한을 0.80 에 묶어 보류 79건 중 52건을 `[0.7, 0.8)` 에 몰았다 — 사용자가 CR-001 A 안(①+②)을 수용해 **D12(관측 신호 재정규화 결합)**·**D13(규칙 필터는 배제가 아니라 감점)**이 유효 결정이 됐다. 이 패키지는 그 두 결정을 `app/er/` 에 구현하고, 평가 도구를 새 산식에 맞추고, **같은 데이터·같은 방식·같은 격자로 한 번만 재실행**해, 같은 결정 K (a) 식으로 게이트를 다시 판정받는다. 수치가 또 미달이면 재실행이 아니라 실패 케이스 분석 갱신과 사용자 결정으로 간다(원칙8, backlog 65행 마지막 문장).

## 범위

- 포함:
  - **D12 구현** — `app/er/confidence.py::combine()` 이 관측된 신호만 결합한다(`confidence = Σ w_i·s_i / Σ w_i`). `rule_checked == 0` 이면 `s_rule` 을 분모에서 빼 `0.625·s_llm + 0.375·s_emb`, 세 신호가 모두 관측되면 D3 원식과 **부동소수까지 같은 값**. `_breakdown()` 에 `weights`(설정값)·`weights_effective`(적용된 정규화 가중치)·`rule_checked` 를 모두 기록한다(원칙9).
  - **D13 구현** — `app/er/rules.py` 의 `relation_tag_conflict`·`hierarchy_conflict` 가 후보를 목록에서 빼지 않고 `penalized_by` 로 표시만 하며 `s_rule = rule_passed / rule_checked` 감점으로 반영된다. `dictionary_conflict` 배제와 후보 0명의 `no_candidates` 강제 경로는 종전 그대로. 3단계 LLM 이 감점 후보를 포함한 후보 전체를 본다.
  - **보수 분기**(원칙1) — 감점 후보가 3단계에서 선택되면 `confidence ≥ T_merge` 라도 자동 연결하지 않고 `identity` 로 강등할지를 설정값 하나로 켜고 끈다. trace 에 `forced_reason="penalized_candidate"`. 기본값·이름·예외는 **결정 A·B**.
  - **평가 도구 정합** — `scripts/run_pilot_eval.py`(`--recheck-traces` 재계산을 `weights_effective`·`rule_checked` 로, 설정 불일치 거부는 `weights` 키로), `evaluation/curve.py`(`meta.weights` 유지 + 정책 표기), `evaluation/calibration.py`(placeholder 판정 문장), `evaluation/resolvers/proposed.py`(`detail` 에 `penalized_by` 전달 — 인터페이스 불변), `evaluation/metrics.py`(부분집합 지표에 `penalized merge` 추가).
  - **재실행 1회** — 같은 40건·같은 다섯 방식·같은 `T_merge` 격자 10점·같은 공급자(OpenAI, 결정 A(ii) 유지)·같은 상한. **새 stamp·새 `run_id`·새 `meta.commit`**.
  - **비교 산출물** — P4 기준선 대비 mention 단위 diff(결정 G).
  - **문서** — `docs/wiki/registry.md` 행(수정 파일은 비고 확장), `README.md`·`docs/user-setup/10-pilot-eval-run.md` 실행법 갱신, `.claude/skills/entity-resolution/SKILL.md` 산식·2단계 문장(U0).
- 이 패키지에서 하지 않는 것:
  - **S3.3 4단계 구조·툴 시그니처 v2·스키마 v2 변경 없음**(원칙4). 단계를 합치거나 LLM 단일 호출로 대체하지 않는다. `search_person` 시그니처·`ERConfig.top_k` 주입은 손대지 않는다(결정 H(i), F-bdd6c5 유지).
  - **`data/` 무수정**(원칙8, P1 인계 9). 라벨이 의심되면 고치지 않고 새 검수 기록 + 사용자 결정으로 분리한다. `reports/failure_cases.md` §9 는 "검수 필요 라벨 없음"으로 이미 닫혔다.
  - **P4 기준선 덮어쓰기 금지** — `reports/pilot/raw-20260922-042440.jsonl.gz`·`reports/pilot/traces-20260922-042440.jsonl`·그 실행의 `reports/metrics.json`(sha256 `25e16dd6…`)·`calibration.json`·`curve.csv`·`eval.md` 의 내용은 비교 기준선이다(CR-001 36행). 갱신 경로는 결정 I.
  - **가중치 비율(5:3:2)·`T_merge`/`T_new` 운영값 재설정** — D12 가 비율 불변을 못박았고 40건으로 튜닝하지 않는다(원칙8). 곡선은 다시 그리되 운영값 확정은 P10.
  - **`s_llm` 보정 로직 추가** — failure_cases §8 이 "보정표만 보고 `s_llm` 을 보정하는 변경은 권하지 않는다"(과신 증거 없음).
  - **150건 데이터셋·최종 `eval.md`·이벤트 추출 F1·툴 호출 정확도** — P10.
  - **P5 이후(루프·메모리·브리핑·프론트)** — 게이트 통과 전 금지.
  - **재실행 반복** — 설정을 바꿔 다시 돌리는 것은 게이트 패키지의 가장 흔한 위반이다(원칙8, 카드 10 "같은 설정으로 두 번 돌리지 않는다").

## 산출물 (파일 경로)

- app/er/confidence.py — `combine()` 재정규화, `_breakdown()` `weights_effective`·`rule_checked`, `forced_reason` 어휘 +1
- app/er/rules.py — `penalized_by` 표시, `relation_tag_conflict`·`hierarchy_conflict` 배제 제거, 완화 재평가 트리거 조건(결정 C)
- app/er/pipeline.py — 2→3단계 후보 전달, 보수 분기 적용, trace 필드
- app/er/types.py — `ScoredCandidate.penalized_by`, `ERConfig` 보수 분기 정책 필드(아래 "허용 파일" 각주)
- scripts/er_smoke.py — 109행 `combine()` 호출부 시그니처 정합(U1, 권고 R-3 — `app/` 밖이지만 D12 호출자)
- app/settings.py — 보수 분기 설정 상수·환경변수 파싱(`er_config()`), `ER_WEIGHTS` 비율은 불변
- scripts/run_pilot_eval.py — `--recheck-traces` 재계산 규약(결정 D), `[traces] rule=…` 안내 문장
- evaluation/curve.py — `meta.weights_policy`·`meta.penalized_merge_policy`(결정 H)
- evaluation/metrics.py — 부분집합 지표 `penalized_merge`(D13 파급 "위험 계측")
- evaluation/calibration.py — placeholder 판정 문장·주석의 D3 → D12 정합
- evaluation/resolvers/proposed.py — `detail["penalized_by"]`(어댑터 인터페이스 불변)
- tests/test_er_confidence.py·test_er_rules.py·test_er_pipeline.py·test_run_pilot_eval.py·test_eval_*.py — 기대값 갱신 + 신규 단언
- reports/pilot/raw-\<새 ts\>.jsonl.gz · traces-\<새 ts\>.jsonl — 재실행 원시(결정 E 규약 그대로)
- reports/metrics.json · calibration.json · curve.csv · eval.md — 재실행 결과(결정 I 로 기준선 보존 후 갱신)
- reports/failure_cases.md — P4 기준선 대비 diff 절 추가(결정 G)
- docs/wiki/packages/P4b-er-redesign/evidence/ — pytest·회귀 3종·dry-run·실 실행·recheck·무변경 diff·sha256 출력
- docs/wiki/registry.md · README.md · docs/user-setup/10-pilot-eval-run.md · .claude/skills/entity-resolution/SKILL.md

> **`app/` 허용 파일은 5개다.** CR-001 33행의 목록(`confidence.py`·`rules.py`·`pipeline.py`·`settings.py`)에 **`app/er/types.py`** 를 더한다 — D13 "코드에서 지켜야 할 것"이 요구하는 `penalized_by` 는 `ScoredCandidate`(frozen dataclass, `types.py` 60~89행)의 필드이고, 보수 분기 설정값은 `ERConfig`(같은 파일 287~307행)가 들고 있어야 `er_config()`·`resolve(config=…)` 경로로 주입된다. 다른 `app/` 파일(`candidates.py`·`judge.py`·`dictionary.py`·`tools/*`)은 고치지 않는다. 이 한 줄이 판정 표 "허용 파일" 행의 근거다.

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 `/commit`)

- [ ] U0 **[메인 세션] 스킬 카드 정합 (U1 착수 전 필수)**: `.claude/skills/entity-resolution/SKILL.md` 22행("2. 규칙 필터 … 명백히 다른 후보 **배제**")·36행(`s_rule` 설명)·39행(`confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`)이 **아직 D3·배제 규약 그대로**다. backend-agent 는 이 스킬을 자동 참조하므로(CLAUDE.md "사용법"), 고치지 않은 채 U1 을 시작하면 구현자가 대체된 결정을 읽는다. D12·D13 문장으로 세 줄만 바꾸고 CR-001 참조 한 줄을 단다. 코드·계산 변경 없음 / Refs: CR-001 D12 D13 S3.3 원칙3
- [ ] U1 **[backend-agent] D12 — 관측 신호 재정규화 결합**: `app/er/confidence.py::combine()` 이 `rule_checked`(또는 `s_rule is None`)를 입력으로 받아 미측정이면 `(w_llm·s_llm + w_emb·s_emb) / (w_llm + w_emb)` 를 돌려준다. 세 신호가 모두 관측되면 D3 원식과 **abs diff == 0**(무작위 표본 단언). `_breakdown()` 에 `weights`·`weights_effective`·`rule_checked`·`rule_passed` 를 모두 남긴다. **강제 경로**(`_forced_decision`·`no_candidates`)는 `rule_checked=0` 이므로 `weights_effective` 도 재정규화 값으로 적되 `confidence` 는 종전대로 0.0 이다(모든 신호가 0 이라 산식 결과와 같다 — `--recheck-traces` 가 그대로 통과해야 한다). `rule_checked > 0`·`rule_passed == 0`(검사했는데 전부 충돌)은 **여전히 `s_rule = 0` 으로 합산**한다. 호출부 `scripts/er_smoke.py:109`(힌트 없는 스모크에서 `s_rule=0` 을 넣는다)도 같은 규약으로 고친다. 테스트: `tests/test_er_confidence.py` — (i) 세 신호 관측 시 D3 원식과 동일, (ii) `rule_checked=0` 이면 0.625/0.375, (iii) `rule_checked>0, rule_passed=0` 이면 0 합산, (iv) `weights_effective` 키 존재와 합이 1.0, (v) 293행 기존 기대값 `0.5*0.95+0.3*0.9+0.2*0.8` 이 그대로 통과 / Refs: CR-001 D12 D10 S3.3 원칙3 원칙9 **[권고 R-3 반영]** `scripts/er_smoke.py:109` 의 `combine()` 호출부도 U1 에서 같이 고친다(산출물 목록에 명시, backend-agent 담당 — `app/` 밖 1파일 예외).
- [ ] U2 **[backend-agent] D13 — 규칙 필터는 감점**: `app/er/rules.py` 의 `_evaluate()` 가 모으는 충돌 중 `relation_tag_conflict`·`hierarchy_conflict` 는 **배제가 아니라 감점**이 된다 — 후보는 `penalized_by`(대표 사유 하나 또는 정렬된 목록, `_CONFLICT_PRIORITY` 54행 **어휘 순서 유지**)를 달고 남고, `passed_rules` 는 "배제되지 않았다"(= `dictionary_conflict` 없음)를 뜻하게 되며, `excluded_by` 에는 `dictionary_conflict` 만 등장한다. `s_rule = rule_passed / rule_checked` 는 그대로다(감점이 여기 반영된다). `apply_rules()` 의 완화(`relaxed=True`) 규약과 `relaxed_pass` 계상 규칙(완화가 `rule_passed` 를 올려주지 않는다)은 유지. `run_rule_stage()` 의 완화 재평가 트리거 조건은 **결정 C** 를 따른다. 테스트: `tests/test_er_rules.py` 42·43·71·72·89·93행 기대값 갱신(`excluded_by` → `penalized_by`), 신규 단언 — **3단계에 전달되는 후보 수 == 1단계 후보 수 − `dictionary_conflict` 후보 수**(D13 "코드에서 지켜야 할 것"), `excluded_by` 에 두 사유가 더 이상 나오지 않음 / Refs: CR-001 D13 S3.3 원칙1 원칙9
- [ ] U3 **[backend-agent] 파이프라인·보수 분기·회귀 3종**: `app/er/pipeline.py::_run_pipeline` 이 `run_rule_stage()` 가 돌려준 **감점 포함 후보**를 3단계 LLM 과 `decide()` 에 넘긴다(`all_scored` 는 종전대로 trace `candidates[]`). 감점 후보가 귀속되고 `band == "merge"` 이면 결정 A·B 의 설정값에 따라 `identity` 로 강등하고 `forced_reason="penalized_candidate"`·`band_by_threshold`(순수 산식 밴드)를 함께 남긴다 — 강등은 **판정 기록을 덮어쓰지 않고 별도 필드로** 드러난다(원칙9, `band_by_threshold` 규약 그대로). `ScoredCandidate.penalized_by`·`ERConfig` 정책 필드·`app/settings.py` 상수·`er_config()` 파싱을 같이 넣는다. **회귀 3종(S3.3 18행·D12·D13 필수)**: (a) 승진 연결 `tests/test_er_pipeline.py:410` — `relaxed_retry is True`·`relaxed_pass is True`·`rule_checked 3`·`rule_passed 2`·`s_rule 2/3`·`confidence ≈ 0.863`·`band == "merge"` 가 **그대로** 통과해야 한다(결정 C·A 의 예외가 여기 걸린다), (b) 팀장↔이모 `:481` — 이 픽스처는 별칭 "팀장"이 사전 표제어라 `dictionary_conflict` 가 함께 떠서 D13 이후에도 **배제**가 유지된다. 단언은 `excluded_by == "dictionary_conflict"` + `penalized_by` 에 나머지 두 사유로 바뀌고 결과(`no_candidates` → `new_person` → `ask_user`)는 불변, (c) 동명이인 `:524` — 힌트가 비어 `rule_checked == 0` 이므로 D12 재정규화가 걸린다. `confidence` 가 `0.5·0.55 + 0.3·s_emb ≈ 0.575` 에서 `0.625·0.55 + 0.375·s_emb ≈ 0.72` 로 오르지만 `[T_new, T_merge)` 안이라 `identity` 유지 — 테스트의 `t_new <= confidence < t_merge` 단언이 그대로 성립하는지 실행으로 확인한다. 세 테스트의 **결과(band·action·저장된 질문)는 하나도 바뀌지 않아야 하고**, 바뀌면 그것이 계획 위반 신호다 / Refs: CR-001 D13 D12 D10 S3.3 원칙1 원칙2 원칙9
- [ ] U4 **[eval-agent] 평가 도구 정합 + 전체 회귀**: (i) `scripts/run_pilot_eval.py::recompute_confidence()`(904행) — 재계산은 `weights_effective`·`rule_checked` 로 제품 `combine()` 을 그대로 부르고, **설정 불일치 거부는 `weights` 키를 `app.settings.ER_WEIGHTS` 와 비교**하는 종전 규약을 유지한다(결정 D). `_Weights`(714행) 모양과 `[traces] rule=…`(1035행) 안내 문자열을 새 산식으로. `_TRACE_CANDIDATE_KEYS`(761행)에 `penalized_by` 추가. (ii) `evaluation/curve.py` — `meta.weights`(`_weights_block()`, 531행)는 **설정값 그대로 유지**하고 `meta.weights_policy`·`meta.penalized_merge_policy` 를 더한다(결정 H). `_META_KEYS`(183행) 순서·`--validate` 갱신. (iii) `evaluation/metrics.py` 569행 부분집합 지표에 **`penalized_merge`**(`penalized_by` 가 비어 있지 않은 merge 행 수·그중 오병합 수)를 더한다(D13 파급 "위험 계측"). (iv) `evaluation/resolvers/proposed.py` 185행 곁에 `detail["penalized_by"]` — **이것이 없으면 U6 의 "감점 후보가 merge 된 건수"를 원시 JSONL 에서 셀 수 없다**(그래서 U4 는 U5 실 실행보다 반드시 앞선다). (v) `evaluation/calibration.py` 의 D3 참조 문장을 D12 로, placeholder 판정(`matched_person_id is None`)은 규약 그대로 두되 ② 로 배제가 줄어 placeholder 수가 준다는 것을 주석에 한 줄. (vi) 전체 `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` 통과(기준 1285 passed, `f01ea35`) / Refs: CR-001 D12 D13 S3.7 원칙8 원칙9
- [ ] U5 **[eval-agent 준비 → 사용자 실행] dry-run 사슬 + 실 재실행 1회**: eval-agent 가 `--dry-run --stub`(네트워크 0)으로 runner → metrics → calibration → curve → validate → report 사슬과 `--recheck-traces` 를 먼저 증명하고 예상 호출·비용을 찍는다. 그다음 **사용자**가 키 있는 셸에서 카드 10 절차로 1회 실행한다 — 새 stamp, `--commit $(git rev-parse HEAD)`, `--max-cost-usd`(결정 E). 카드 10 갱신: 사용자가 쓰는 `.env` 로드 접두(`set -a; . ./.env; set +a;` — 스크립트는 `.env` 를 읽지 않는다, 로드 주체는 사용자 셸이다·security §1)와 Windows `PYTHONUTF8=1` 을 절차 3·판정 명령에 명시, 산출물 이동 절차를 결정 I(기준선 보존)에 맞춰 수정. evidence: 실행 명령(키 값 없이)·표준출력 전문·rc·토큰 합계·`meta.provider/model/embedding_model/run_mode/commit` / Refs: CR-001 D4 D11 원칙8 L-004 **[권고 R-9 반영]** 실 실행 로그 파일명은 `evidence/<ts>-u5-real-run.txt`(`*real-run*` 포함 — 판정 표 21행 규약), 실패 시도도 같은 규약으로 남기고 03-log 에 사유(LLM 호출 수·과금)를 적는다.
- [ ] U6 **[eval-agent] P4 기준선 대비 실패 케이스 갱신**: `reports/failure_cases.md` 에 결정 G 형식으로 비교 절을 **이어 붙인다**(기존 절 1~12 의 수치·문장은 고치지 않는다 — 그것이 기준선이다). 담을 것: (a) mention 단위 diff 표 — 조인 키 `(scenario_id, turn, mention, mention_kind)`(04-review §6 이 `mention_index` 의 turn 내 비유일 4건을 지적했다), 열은 기준선 `decision`/`person_id`/`confidence` → 재실행 값과 변화 유형, (b) `sc-015` t0 "부장님"·`sc-007` t2 "문실장님" 두 건의 전후 판정과 후보 목록(정답 후보가 3단계에 도달했는가), (c) 기준선 deferred 79건의 행방(merge / identity 유지 / new_person, 그중 골드 일치 수), (d) **감점 후보가 merge 된 건수와 그중 오병합 수**(D13 위험 계측), (e) `rule_checked == 0` 인 mention 100건의 확신도 분포 이동, (f) 게이트 4수치의 전후 비교와 `dominated_by` 변화. 결론 문장은 "표본 40건이므로 방향과 유형까지"(P1 인계 15). **미달이면 여기까지가 산출물이고 재실행하지 않는다** — S3.3 재설계 후보를 적어 사용자 결정으로 올린다(원칙8) / Refs: CR-001 D12 D13 S3.3 S3.7 원칙1 원칙8
- [ ] U7 **[eval-agent] 수용 기준 기계 검증 + 문서**: 아래 "판정 방법" 표의 모든 명령을 실행해 출력을 evidence 로 남긴다(무변경 diff·sha256·게이트·회귀 3종·`sc-015`/`sc-007` 포함). `docs/wiki/registry.md` — 수정한 기존 행(81·82·85행 `app/er/*`)은 **비고에 D12·D13 한 줄과 새 커밋 해시**를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례), 새로 생긴 산출물(재실행 `raw`·`traces`·비교 절)은 행으로. `README.md` "파일럿 평가 실행법 (P4)" 절에 P4b 재실행 한 문단, 33행 비고에 패키지명. `docs/user-setup/10-pilot-eval-run.md` 는 U5 에서 고친 내용 확정 / Refs: CR-001 S3.7 원칙4 원칙8 원칙9
- [ ] **04-review [verifier] 게이트 재판정**: 결정 K (a) 식 **그대로**, 한 번만. `metrics.json.gate` 인용 + 독립 재계산, `sc-015`/`sc-007` 두 조항, 기준선 불변, `app/`·`data/` 무변경, 회귀 3종, D12·D13 "코드에서 지켜야 할 것" 전 항목 grep, `penalized_by` merge 건수(D13 위험 계측) 보고. 판정은 verifier 만 한다(L-002) / Refs: CR-001 D12 D13 D10 R3 R4 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [ ] [backend-agent + eval-agent] **ER 재설계 후 파일럿 재실행** — D12(관측 신호 재정규화)·D13(규칙 필터 감점) 구현 + 새 stamp 재실행 + 게이트 재판정 / 의존: P4 부분완료(adf9f1b), CR-001 승인 / 수용기준: `app/er/confidence.py`·`rules.py`·`pipeline.py`·`types.py`(+`settings.py` 설정값) 가 D12·D13 "코드에서 지켜야 할 것" 전부 충족(회귀 3종 유지), `--recheck-traces` `max_abs_diff=0.0`(weights_effective), 새 stamp `reports/pilot/raw-<ts>.jsonl.gz`·`reports/metrics.json` 로 결정 K 게이트 `0.8 [] True True`, `sc-015` 오병합·`sc-007` 미검출 아님, P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경. 미달이면 재실행 없이 failure_cases 갱신 + 사용자 결정
  - 01-plan 결정 항목: 감점 후보의 `≥ T_merge` 보수 분기(권장 강등)·설정값 이름 / 완화 재검색 존치 / `weights` vs `weights_effective` 거부 규약 / 재실행 비용 상한

해석(기계 판정 방법, 위 두 줄을 바꾸지 않는다):

  - "**D12·D13 "코드에서 지켜야 할 것" 전부 충족**" → D12 카드 23~27행 4항목과 D13 카드 21~25행 4항목을 각각 grep·테스트로 증명한다. 판정 명령은 아래 표 3·4·5·6·7행. 두 카드가 "리뷰어가 grep 으로 확인할 수 있는 문장으로" 쓴 것을 그대로 쓴다.
  - "**(회귀 3종 유지)**" → `tests/test_er_pipeline.py` 의 승진·이모·동명이인 세 테스트가 통과한다. **결과(band·action·저장된 질문 종류)가 P3-er 때와 같아야** 하고, 바뀐 것은 `excluded_by`/`penalized_by` 표시와 `confidence` 수치뿐이다(U3).
  - "**`--recheck-traces` `max_abs_diff=0.0`(weights_effective)**" → 재실행이 뜬 새 `traces-<ts>.jsonl` 에 대해 `python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-<새 ts>.jsonl` 이 rc=0 이고 `dumped == recomputed`·`max_abs_diff=0.0`. 재계산은 `weights_effective` 로 한다(결정 D).
  - "**새 stamp … 결정 K 게이트 `0.8 [] True True`**" → `PYTHONUTF8=1 python -c "import json;g=json.load(open('reports/metrics.json'))['gate'];print(g['t_merge'],g['dominated_by'],g['d10_direction'],g['pass'])"` 의 출력이 정확히 `0.8 [] True True`. `meta.run_mode == "real"`, `meta.run_id`·`meta.commit`·raw stamp 가 P4 실행과 다르다.
  - "**`sc-015` 오병합·`sc-007` 미검출 아님**" → 새 raw 의 `method="proposed"`·`t_merge=0.8`·`mention_kind="gold"` 행에서 `classify_gold_row()` 가 `sc-015` t0 "부장님"에 `false_merge` 를, `sc-007` t2 "문실장님"에 `miss` 를 돌려주지 않는다(표 12행).
  - "**P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경**" → `git diff --name-only e4109cc..HEAD -- reports/pilot/raw-20260922-042440.jsonl.gz reports/pilot/traces-20260922-042440.jsonl` 이 0줄이고, 두 파일의 sha256 이 P4 종료 시점 값과 같다. `reports/metrics.json` 은 수용 기준이 **새 결과**를 요구하므로 갱신되며, 기준선 사본은 결정 I 로 보존한다(사본의 sha256 = `25e16dd6…`).
  - "**미달이면 재실행 없이 failure_cases 갱신 + 사용자 결정**" → (i) evidence 의 실 실행 파일이 **설정당 1개**다(2개 이상이면 03-log 에 설정 변경 사유가 있어야 한다), (ii) 미달이어도 `reports/failure_cases.md` 비교 절은 존재한다(U6 은 결과와 무관하게 한다), (iii) 미달 시 `T_merge`·가중치·프롬프트를 바꿔 다시 돌린 흔적이 없다(`meta.t_new`·`grid`·`weights`·`model_configured` 가 P4 와 같다).

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

로컬 컨테이너는 5433 이므로 포트를 셸 변수로 넘긴다(`.env` 는 스크립트가 읽지 않는다 — security §1). `open()` 한 줄 명령에는 Windows cp949 대비로 `PYTHONUTF8=1` 을 앞에 둔다(P4 U7 실측).

| # | 무엇 | 명령 | 기대 출력 |
|---|------|------|-----------|
| 1 | 전체 테스트 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 1285(f01ea35 기준) + 신규 전부 통과, 실패 0·skip 0 |
| 2 | 회귀 3종 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -k "promotion or aunt or homonym"` | `3 passed` |
| 3 | D12 grep | `grep -n "weights_effective\|rule_checked" app/er/confidence.py` | `combine()`·`_breakdown()` 양쪽에서 잡힌다(각 1행 이상) |
| 4 | D12 동치 | `pytest tests/test_er_confidence.py -q -k "renormalize or observed"` | 세 신호 관측 시 D3 원식과 `abs diff == 0`, `rule_checked=0` 이면 0.625/0.375 |
| 5 | D13 grep | `grep -n "penalized_by" app/er/rules.py app/er/types.py app/er/pipeline.py` · `grep -n "excluded_by" app/er/rules.py` | `penalized_by` 가 세 파일에 있고, `excluded_by` 대입 경로에 `relation_tag_conflict`·`hierarchy_conflict` 가 없다 |
| 6 | 후보 전달 수 | `pytest tests/test_er_rules.py -q -k "penalt or forwarded"` | 3단계 후보 수 == 1단계 후보 수 − `dictionary_conflict` 수 |
| 7 | 보수 분기 스위치 | `grep -n "ER_PENALIZED_MERGE_POLICY" app/settings.py app/er/types.py` · `pytest tests/test_er_pipeline.py -q -k penalized` | 설정값 하나로 켜고 끌 수 있고 trace 에 `forced_reason="penalized_candidate"` 가 남는다 |
| 8 | dry-run(네트워크 0) | `POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --dry-run --stub --out <tmp>` | rc=0, `network_calls=0`·`run_mode=stub`, 사슬 6단계 |
| 9 | 실 실행 | 카드 10 절차 3(사용자 셸, 새 stamp, `--commit`, `--max-cost-usd`) | rc=0, `run_mode=real`, `[rows] rows=… = mentions × methods=5 × t_merge=10` |
| 10 | trace 재계산 | `python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-<새 ts>.jsonl` | `dumped==recomputed`·`max_abs_diff=0.0`, rc=0 |
| 11 | 게이트 | `PYTHONUTF8=1 python -c "import json;g=json.load(open('reports/metrics.json'))['gate'];print(g['t_merge'],g['dominated_by'],g['d10_direction'],g['pass'])"` | `0.8 [] True True` |
| 12 | 두 시나리오 | `PYTHONUTF8=1 python -c '<failure_cases §11 의 <PRE> 머리글, raw 경로만 새 stamp 로>; print([(r["scenario_id"],r["turn"],classify_gold_row(r)) for r in G("proposed",0.8) if r["scenario_id"] in ("sc-015","sc-007")])'` | `sc-015` 행에 `false_merge` 없음, `sc-007` 행에 `miss` 없음 |
| 13 | 스키마·격자 | `python -m evaluation.metrics --validate reports/metrics.json` · `python -c "import csv;r=list(csv.DictReader(open('reports/curve.csv',encoding='utf-8')));print(sorted({float(x['t_merge']) for x in r}), {x['t_new'] for x in r}, len({x['method'] for x in r}))"` | rc=0 · `[0.5,…,0.95]`(10점)·`{'0.3'}`·`5` |
| 14 | `eval.md` 멱등 | `python -m evaluation.report --metrics reports/metrics.json --out <tmp>/eval.md && diff <tmp>/eval.md reports/eval.md` | 0줄 |
| 15 | 허용 파일 | `git diff --name-only e4109cc..HEAD -- app/` | 출력이 `{app/er/confidence.py, app/er/rules.py, app/er/pipeline.py, app/er/types.py, app/settings.py}` 의 **부분집합**(그 밖의 `app/` 파일이 나오면 미충족) |
| 16 | 데이터 무변경 | `git diff --name-only e4109cc..HEAD -- data/` | **0줄** |
| 17 | 기준선 불변 | `git diff --name-only e4109cc..HEAD -- reports/pilot/raw-20260922-042440.jsonl.gz reports/pilot/traces-20260922-042440.jsonl` · `sha256sum reports/pilot/raw-20260922-042440.jsonl.gz reports/pilot/metrics-20260922-042440.json` | 0줄 · metrics 사본 해시가 `25e16dd6…`(P4 04-review·CR-001 36행 인용값)로 시작 |
| 18 | 라벨 무변경 | `python scripts/validate_scenarios.py --strict --json` | rc=0, `total` 40·5범주 `counts` 그대로 |
| 19 | 스키마·툴 무변경 | `POSTGRES_PORT=5433 python -m alembic check` · `python scripts/tools_check.py` | `No new upgrade operations detected.` · `7/7 ok` |
| 20 | 위험 계측 | `PYTHONUTF8=1 python -c "import json;m=json.load(open('reports/metrics.json'));print(m['proposed']['subsets'])"` | `penalized_merge` 키가 있고 분자/분모가 함께 적혀 있다 |
| 21 | 재실행 1회 | `ls docs/wiki/packages/P4b-er-redesign/evidence/*real-run*` | 실 실행 evidence 가 **1개**(2개 이상이면 03-log 에 설정 변경 사유) |

- 증거 경로: `docs/wiki/packages/P4b-er-redesign/evidence/`. Docker Desktop 이 꺼져 있거나 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security §6).

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| registry 행 | 무엇 | 이 패키지가 어떻게 쓰는가 |
|---|---|---|
| 81 `app/er/rules.py`(02e6f14) | `apply_rules()`·`run_rule_stage()`·`_evaluate()`·`_CONFLICT_PRIORITY` | **수정**(D13). 새 모듈을 만들지 않고 같은 함수 안에서 배제→감점으로 바꾼다. 어휘 3종은 유지 |
| 82 `app/er/confidence.py`(593c254) | `combine()`·`band_for()`·`ge_with_tolerance()`·`decide()` | **수정**(D12). `band_for`·`_ge`·허용오차 단일 출처(F-7fe239)는 **건드리지 않는다** |
| 85 `app/er/pipeline.py`(d6e5949·cc5d24f) | `resolve()`·`apply_resolution()` | **수정**(후보 전달·보수 분기). 4단계 순서·trace 1행·부수효과 0 규약 유지 |
| `app/er/candidates.py`·`judge.py`·`dictionary.py` | 1·3단계 | **무수정**(failure_cases §8: 1·3단계는 원인이 아니다) |
| `scripts/run_pilot_eval.py`·`evaluation/{runner,metrics,calibration,curve,report}.py` | P4 가 만든 평가 사슬 | 그대로 재사용하고 D12·D13 이 바꾼 부분만 고친다. **러너·지표 구조를 새로 만들지 않는다** |
| `evaluation/scenario_state.py`·`evaluation/resolvers/*` | 적재기·다섯 방식 | 무수정(어댑터 `detail` 키 1개만 추가). 방식·인터페이스를 늘리지 않는다 |
| `data/scenarios/`·`scripts/validate_scenarios.py` | 40건·검증기 | 읽기 전용. 무변경 증거 명령의 출처 |
| `docs/user-setup/10-pilot-eval-run.md` | 사용자 실행 카드 | **갱신해 재사용**(새 카드 번호를 만들지 않는다) |
| `README.md` "파일럿 평가 실행법 (P4)" 절(330행) | 실행법 | 절을 새로 만들지 않고 이어 붙인다(F-0ffff5 선례) |

## 리스크 · 미결

**사용자 결정이 필요한 항목 (U1 착수 전. 결정은 메인 세션·사용자가 한다 — L-004)**

- **결정 A — 감점 후보의 `≥ T_merge` 보수 분기 기본값.**
  (i) **`ask`(강등) + `relaxed_pass` 예외 — 권장**: `penalized_by` 가 비어 있지 않은 후보가 귀속되면 `confidence ≥ T_merge` 라도 `band="identity"`(`forced_reason="penalized_candidate"`)로 강등한다. **단 `relaxed_pass == True`(인접 위계 1칸 완화 통과) 후보는 예외**로 자동 연결을 허용한다. 근거: D13 이 권장안으로 강등을 적었고(원칙1 — 후보가 늘어 오병합 기회가 는다는 위험을 40건으로 검증할 수 없다), 예외가 없으면 **S3.3 회귀 1(승진 연결)이 깨진다** — 승진 픽스처의 김민수는 `hierarchy_conflict` 감점 후보이므로 예외 없는 강등은 `tests/test_er_pipeline.py:444` 의 `band == "merge"` 를 `identity` 로 바꾼다. 비용: 예외 규칙 한 줄과 테스트 2개. 위험: 예외 경로가 곧 승진 자동 연결 경로이므로 오병합이 거기서 나면 계측이 필요하다 → U4 의 `penalized_merge` 부분집합에 `relaxed_pass` 를 함께 센다.
  (ii) `merge`(자동 연결 허용): 마찰이 가장 적고 게이트 통과 가능성이 높지만, D13 이 명시한 "후보가 늘어 오병합 기회가 는다"를 아무 장치 없이 받는다. 원칙1 의 비대칭 비용과 반대 방향.
  (iii) 예외 없는 전면 강등: 회귀 1 위반이므로 **채택 불가**(S3.3 18행·D12/D13 "회귀 3종 통과"가 수용 기준이다).
- **결정 B — 설정값 이름·환경변수.** (i) **권장**: 상수 `app/settings.py::ER_PENALIZED_MERGE_POLICY`(D13 24행이 예시로 든 이름 그대로), 환경변수 같은 이름, 값 어휘 `ask` | `merge`, 기본 `ask`, `er_config()` 가 읽어 `ERConfig.penalized_merge_policy` 로 넘기고 trace `decision` 에 적용 여부가 남는다. 근거: 카드가 쓴 이름을 코드가 그대로 쓰면 grep 한 번으로 카드↔코드가 이어진다(원칙9). / (ii) 불리언 `ER_DOWNGRADE_PENALIZED=1`(짧지만 값이 trace 에 남을 때 의미가 덜 분명하고 셋째 정책을 못 늘린다). / (iii) `ERConfig` 필드만 두고 환경변수 없음(실행 중 스위치 불가 — D13 "켜고 끌 수 있다"와 어긋남).
- **결정 C — 완화 재평가(`rules.py` 167행·`run_rule_stage` 190~202행) 존치 여부.**
  (i) **존치 + 트리거 조건 변경 — 권장**: 지금 조건은 "엄격 통과 후보 0"인데, D13 이후 `hierarchy_conflict` 는 배제가 아니므로 그 후보가 이미 "통과"로 잡혀 **완화가 영영 돌지 않는다**. 조건을 "**감점 없는 후보 0**"(`penalized_by` 가 빈 후보가 하나도 없을 때)으로 바꾸면 승진 케이스에서 완화 1회가 그대로 돌아 `relaxed_pass=True`·`relaxed_retry=True`·`s_rule=2/3`·`band=merge` 가 전부 유지된다(회귀 1). 완화가 `rule_passed` 를 올려주지 않는 규약(결정2)도 그대로. / (ii) 제거: `relaxed_retry`·`relaxed_pass` 필드와 S3.3 15행 "재검색 1회" 문장이 죽고, 승진 후보가 상시 감점 후보가 되어 결정 A(i) 의 강등에 걸린다 → 회귀 1 위반. / (iii) 존치·조건 그대로: (ii)와 같은 결과(완화가 사실상 죽는다). **이 결정은 결정 A 와 한 몸이다** — A(i) 의 예외가 성립하려면 C(i) 가 필요하다.
- **결정 D — `--recheck-traces` 규약.** (i) **권장**: 거부 판정은 **`weights`**(설정값) ↔ `app.settings.ER_WEIGHTS` 비교로 **그대로 유지**하고(921~924행), 재계산은 **`weights_effective`·`rule_checked`** 로 제품 `combine()` 을 부른다. 더해 `weights_effective` 가 `weights`·`rule_checked` 에서 산술적으로 도출되는 값과 같은지 교차 확인한다(`rule_checked==0` → `{llm:0.625, emb:0.375, rule:0.0}`). 기준은 `max_abs_diff == 0.0`(허용오차 없음) 유지. 근거: D12 카드 19행이 정확히 이 분업을 지시한다. / (ii) 거부 판정을 `weights_effective` 로 바꾸기: 재정규화 값이 `ER_WEIGHTS` 와 다르므로 `rule_checked==0` 행이 **전건 거부**된다 — 불가. / (iii) 거부 판정 삭제: 원칙3 의 "기록된 산식이 제품 상수와 같다"는 방어가 사라진다 — 비권장.
- **결정 E — 재실행 비용 상한·1회 원칙.** (i) **권장**: `--max-cost-usd 5` 유지(P4 결정 B(i) 그대로), 실행 1회. 참고 수치는 P4 실측 40건 $0.0271(04-review §7 4항)·사전 추정 $0.0316(카드 10 기대 출력). 미달이어도 **재실행하지 않고** U6 갱신 + 사용자 결정으로 간다(backlog 65행 마지막 문장·원칙8). dry-run 은 네트워크 0 이므로 횟수 제한 없음. / (ii) 상한을 낮춘다($1): 실측의 30배 여유라 충분하지만 P4 와 상한이 달라져 재현 조건이 하나 바뀐다. / (iii) 2회 실행(변동성 측정): 비용이 아니라 **원칙8 위반 위험**이 문제다 — 게이트 패키지가 같은 설정으로 두 번 돌리는 것은 카드 10 이 금지한다. 변동성은 P10.
- **결정 F — 게이트 기준.** (i) **권장**: 결정 K (a) 지배 기준을 **글자 그대로** 쓰고 `metrics.json.gate` 판정식(`evaluation/curve.py`)은 **바꾸지 않는다**(S3.7 불변). backlog 가 더한 두 조항(`sc-015` 오병합 아님·`sc-007` 미검출 아님)은 `gate.pass` 안에 넣지 않고 **수용 기준의 별도 항목**으로 04-review 가 표 12행 명령으로 확인한다. 근거: 게이트 식을 이 패키지가 바꾸면 "미달한 쪽이 판정식을 고쳤다"가 되어 원칙8 방어가 무너진다. / (ii) `gate` 안에 두 조항을 넣는다: 04-review 가 한 줄로 판정할 수 있지만 `curve.py` 판정식 변경 = 결정 K 개정(CR 필요). / (iii) 추가 기준 "P4 기준선 대비 오병합 ≤ 1·미검출 ≤ 1"(CR-001 51행 문구)도 수용 기준으로 올린다: **backlog 65행에는 이 문장이 없다** — 넣으려면 backlog 개정이 먼저다(아래 "backlog 개정 제안" 1).
- **결정 G — P4 기준선과의 비교 산출물 형식.** (i) **권장**: `reports/failure_cases.md` 에 `## 13. P4 기준선 대비(P4b 재실행)` 절을 **이어 붙이고** 기존 절 1~12 의 수치·문장은 한 글자도 고치지 않는다(문서 머리글에 "§1~12 는 P4 실행 기준선, §13 이 P4b" 한 줄). 근거: backlog 가 "failure_cases 갱신"이라고 적었고, 한 파일에 전후가 붙어 있어야 04-review 가 대조를 한 번에 한다. 조인 키는 `(scenario_id, turn, mention, mention_kind)`(04-review §6 `mention_index` 비유일 4건). / (ii) 새 파일 `reports/failure_cases_p4b.md`: 기준선 불변이 더 분명하지만 backlog 문장("failure_cases 갱신")과 어긋나고 두 파일 대조 비용이 는다. / (iii) `eval.md` 안에만 비교 표: `eval.md` 는 `metrics.json` 만으로 재생성돼야 하므로(멱등 요구) 기준선 수치를 손으로 넣을 수 없다 — 불가.
- **결정 H — `weights_effective` 정책의 메타 표기.** (i) **권장**: `evaluation/curve.py` 의 `meta.weights` 는 지금처럼 **설정값(`ERConfig` 모듈 기본값)** 을 유지하고, `meta.weights_policy = "observed_renormalized(D12)"` 와 `meta.penalized_merge_policy = "<결정 A·B 의 값>"` 두 키를 더한다. `report.py` 는 실행 메타 표에 그 두 줄을 찍는다(입력은 여전히 `metrics.json` 하나 — 멱등 유지). 근거: 유효 가중치는 mention 마다 다르므로 단일 값으로 적을 수 없고, "정책"과 "설정값"을 나누면 `--recheck-traces` 의 두 키 분업(결정 D)과 어휘가 같아진다. / (ii) `meta.weights` 를 유효 가중치로 교체: mention 별로 다른 값을 하나로 적는 셈이라 거짓이 된다 — 불가. / (iii) 표기 없음: 재실행 산출물만 보고는 어느 산식으로 계산됐는지 알 수 없다(원칙8 재현성) — 비권장.
- **결정 I — P4 기준선 `reports/metrics.json` 보존 방법 (이 계획이 추가한 결정).** CR-001 36행은 "`reports/metrics.json`(sha256 `25e16dd6…`)은 덮어쓰지 않는다"고 적었지만, backlog 수용 기준은 "**새 stamp … `reports/metrics.json` 로 결정 K 게이트** `0.8 [] True True`"를 요구한다 — 같은 경로를 두고 두 요구가 부딪힌다.
  (i) **권장**: U5 실행 **전에** 현재 `reports/metrics.json` 을 `reports/pilot/metrics-20260922-042440.json`(기준선 stamp)으로 **복사해 커밋**하고, 같은 방식으로 `calibration.json`·`curve.csv`·`eval.md` 도 stamp 사본을 남긴 뒤, `reports/` 최상위 4파일을 재실행 결과로 갱신한다. 판정: 사본의 sha256 이 `25e16dd6…`(metrics) 로 시작하고 `raw`·`traces` 원본은 diff 0줄. / (ii) 재실행 결과를 `reports/pilot/` 에만 두고 최상위는 P4 그대로: 수용 기준 문장("`reports/metrics.json` 로 게이트")을 어긴다. / (iii) 기준선을 `git show adf9f1b:reports/metrics.json` 으로만 남긴다(사본 없음): 파일이 저장소에 보이지 않아 04-review 가 경로로 대조할 수 없고, 원칙8 "재현 가능"의 눈에 보이는 증거가 줄어든다.

**리스크(결정이 아니라 지켜볼 것)**

- **② 는 40건으로 검증할 수 없다**(CR-001 20행·failure_cases §8 후보 2). 후보가 늘면 오병합 기회도 는다 — 반사실 계산이 불가능한 유일한 변경이다. 완화: 보수 분기(결정 A)·`penalized_merge` 부분집합 계측(U4)·04-review 의 별도 보고(D13 파급 19행). 그래도 "40건에서 오병합이 안 났다"는 안전의 증명이 아니다 — 이 한계 문장을 U6 결론에 박는다(P1 인계 15).
- **회귀 3종이 이 패키지의 안전벨트다.** 세 테스트의 **결과**가 하나라도 바뀌면 D12·D13 구현이 규약을 넘은 것이다. 특히 (a) 승진은 결정 A·C 의 조합에 직접 걸리고, (c) 동명이인은 D12 로 `confidence` 가 `≈0.575 → ≈0.72` 로 오른다 — `[T_new, T_merge)` 안이지만 여유가 줄었다. `T_merge` 에 더 가까워진 만큼 실행에서 동명이인 계열이 merge 로 넘어가는지 U6 이 확인한다.
- **테스트가 옛 산식·옛 어휘를 문자열로 박아 두고 있다.** `tests/test_er_rules.py` 42·43·71·72·89·93행(`excluded_by` 기대값), `tests/test_er_confidence.py` 293행(원식 수치 — D12 에서도 통과해야 한다), `tests/test_run_pilot_eval.py` 450·590~601·644행(`weights` 키·거부 테스트), `evaluation/calibration.py` 200~208행 설명 문자열(`tests/test_eval_calibration.py:970` 이 `inspect.getsource` 로 본다). 기대값을 바꾸는 것과 **단언을 없애는 것**은 다르다 — 없애면 규약이 사라진다.
- **`--recheck-traces` 가 새 trace 를 거부할 수 있다.** 04-review §7 3항이 경고한 그대로다(66·135·720행). 결정 D(i) 를 U4 에서 먼저 고치지 않고 U5 를 돌리면 실행 rc=1 로 죽고 비용만 나간다. **U4 → U5 순서를 지킨다.**
- **`detail["penalized_by"]` 가 없으면 U6 을 쓸 수 없다.** 원시 JSONL 은 재실행 뒤 다시 만들 수 없다(재실행 금지). 어댑터 키 추가는 U4 안, 즉 실행 전에 끝나야 한다.
- **`T_merge 0.8` 유지 vs 곡선 재확정(D10·R3).** 산식이 바뀌면 같은 0.8 이 다른 뜻이 된다(D12 로 상한이 0.80 → 1.0 으로 풀린다). 이 패키지는 **초기값 0.8 을 그대로 두고** 곡선으로 단조성(R3)만 재확인한다. 운영값 확정은 P10(P4 범위 문장 그대로).
- **`rule_checked == 0` 이 여전히 141 중 100 이라는 사실은 바뀌지 않는다.** D12 는 그 100건의 확신도를 올릴 뿐 힌트를 더 만들지 않는다. merge 가 급증하면(반사실 48 → 97) **오병합 축이 함께 움직이는지**가 게이트의 관건이다.
- **강제 경로의 `weights_effective`.** `_forced_decision`·`no_candidates` 는 `confidence` 를 산식 없이 0.0 으로 둔다. 재정규화 가중치를 적어도 모든 신호가 0 이라 재계산이 0.0 으로 일치하지만, 여기서 `weights` 만 적고 `weights_effective` 를 빠뜨리면 `--recheck-traces` 가 키 부재로 죽는다(U1 단언 대상).
- **Windows 로케일.** 판정 명령 앞에 `PYTHONUTF8=1`(카드 10·P4 01-plan 92행 각주). 재실행 stamp 는 UTC(registry 140행).
- **`.env` 로드 주체.** 사용자가 `set -a; . ./.env; set +a;` 로 셸에 값을 넣는 것과 **스크립트가 `.env` 를 읽는 것**은 다르다 — 후자는 security §1 위반이다. 카드 10 갱신 시 이 구분을 문장으로 남긴다(U5).
- **컨텍스트·단위 경계.** `app/` 3~5파일과 평가 도구 5파일을 한 단위로 묶지 않는다(U1~U4 로 나눈 이유). 단위마다 `/commit`, 각 커밋 `Refs: CR-001 …`.

## 결정 (사용자 확정 2026-09-22 — 권장 조합 그대로)

| 결정 | 확정 | 반영 단위 |
|------|------|-----------|
| A 감점 후보 `≥ T_merge` | **(i)** `ask` 강등(`forced_reason="penalized_candidate"`) + `relaxed_pass == True` 후보는 자동 연결 예외 | U3 |
| B 설정값 | **(i)** `ER_PENALIZED_MERGE_POLICY` = `ask` \| `merge`, 기본 `ask`, `ERConfig.penalized_merge_policy`, trace 에 적용 여부 | U3 |
| C 완화 재평가 | **(i)** 존치 + 트리거 "엄격 통과 후보 0" → **"감점 없는 후보 0"** (A 와 한 몸) | U2·U3 |
| D `--recheck-traces` | **(i)** 거부는 `weights`↔`ER_WEIGHTS` 유지, 재계산은 `weights_effective`·`rule_checked` 로 제품 `combine()` + 도출값 교차 확인 | U4 |
| E 비용·횟수 | **(i)** `--max-cost-usd 5`, 실 실행 1회, 미달 시 재실행 금지 | U5 |
| F 게이트 기준 | **(i)** 결정 K (a) 식·`metrics.json.gate` 판정식 불변; `sc-015`/`sc-007` 은 별도 수용 기준 항목(표 12행) | U7·04-review |
| G 비교 산출물 | **(i)** `failure_cases.md` §13 "P4 기준선 대비" 이어 붙임, §1~12 불변 | U6 |
| H 메타 표기 | **(i)** `meta.weights` 유지 + `meta.weights_policy`·`meta.penalized_merge_policy`, `report.py` 메타 표 2줄 | U4 |
| I 기준선 보존 | **(i)** U5 전에 `reports/{metrics.json,calibration.json,curve.csv,eval.md}` → `reports/pilot/<이름>-20260922-042440.*` 복사·커밋(metrics sha256 `25e16dd6…` 판정), 재실행이 최상위 갱신. CR-001 36행 문구 정정(메인 세션) | U5 |
| backlog 개정 (1) 기준선 대비 ≤ 1 | **거절** — 결정 K 두 축과 중복·완화 소지, `sc-015`/`sc-007` 조항이 더 날카로움 | — |
| backlog 개정 (2) `types.py` | **반영** — backlog 65행·이 계획 수용 기준 줄에 `types.py`(+`settings.py`) 추가(메인 세션) | — |

## backlog 개정 제안 (architect 는 이 위임에서 `docs/backlog.md` 를 고치지 않았다)

1. **"P4 기준선 대비 오병합 ≤ 1·미검출 ≤ 1" 이 backlog 65행에 없다.** CR-001 §4 2항은 P4b 수용 기준을 "재실행 게이트 `0.8 [] True True` + 회귀 3종 + **P4 기준선 대비 오병합 ≤ 1·미검출 ≤ 1**"로 적었지만, 실제로 커밋된 backlog 행에는 그 조항 대신 `sc-015`/`sc-007` 두 시나리오 조항이 들어갔다. 게이트 기준을 넓히려면(결정 F(iii)) **backlog 문장을 먼저 고쳐야** 한다 — 이 계획은 커밋된 backlog 문장만 수용 기준으로 옮겼다.
2. **`app/` 허용 파일 목록에 `app/er/types.py` 가 빠져 있다.** CR-001 33행 파일 목록에는 없지만 `ScoredCandidate.penalized_by`·`ERConfig` 정책 필드가 그 파일에 있어야 D13 을 구현할 수 있다. backlog 문장은 `confidence.py`·`rules.py`·`pipeline.py` 세 파일만 이름으로 들지만 "D12·D13 코드에서 지켜야 할 것 전부 충족"이 상위 조건이므로 충돌은 아니다 — 04-review 가 오해하지 않도록 이 계획의 "허용 파일" 각주와 판정 표 15행에 근거를 남겼다.
3. **P5 행(70행)의 의존 문구는 이미 "P4b 게이트 통과"로 갱신돼 있다**(e4109cc). 추가 개정 필요 없음.

## 읽은 카드

- `.claude/gitlog.md`(2026-09-22 16:28 스냅샷) — 브랜치(`dev = e4109cc`, `origin/dev` 보다 2 앞섬, `main(origin) = 0dbf2c9`, 승격 대기 17), 최근 커밋 20건 중 `e4109cc`·`adf9f1b`·`f01ea35`·`ea1bbb2`·`ef18143`, 마지막 커밋(CR-001)의 파일 목록 14개, 미커밋 `docs/wiki/journal.md` 1건. **P3-er 커밋(U3/U4/U6)은 이 스냅샷(최근 20건)에 없어 registry 81·82·85행의 등록 해시(`02e6f14`·`593c254`·`d6e5949`·`cc5d24f`)를 근거로 썼다 — 태그 이력이 필요하면 메인 세션에 `bash .claude/scripts/gitlog.sh P3-er D3` 실행 요청**(L-001, architect 는 Bash 없음)
- `docs/wiki/INDEX.md` — 47행(D 태그: D3 는 D12 로 대체됨·D13 신설), 70·71행(P4 부분완료·P4b 행), 81행(P4b 게이트 통과가 P5 조건)
- `docs/wiki/CURRENT.md` — `active: none`·`frozen: none`, 메모 15·16행(CR-001 이행완료(문서), 코드는 P4b 패키지, P4 부분완료 경위)
- `docs/backlog.md` — 59~66행(P4 행·**P4b 절 전문**, 수용 기준을 글자 그대로 옮긴 출처), 68~70행(P5 의존), 97~104행 리스크 로그
- `docs/wiki/changes/CR-001.md` — §1 변경 문장 표·근거 수치, §2 영향 분석(R3·R4·D3→D12·D13·S3.3·파일 목록·재실행 규약 36행), §3 선택지 A/B/C 와 "① 만으로는 지배가 풀리지 않는다", §4 이행 순서 4·5항
- `docs/wiki/decisions/D12-observed-signal-renormalization.md` — 결정 5~10행·이유·파급·**코드에서 지켜야 할 것 23~27행**(U1·판정 표 3·4행의 출처)
- `docs/wiki/decisions/D13-rule-filter-penalty.md` — 결정 5~8행(보수 분기를 이 01-plan 결정으로 위임)·이유·파급(위험 계측 19행)·**코드에서 지켜야 할 것 21~25행**(U2·U3·판정 표 5·6·7행)
- `docs/wiki/decisions/D10-two-thresholds.md` — 두 임계치·방향·"임계치 하나로 구현하지 않는다"
- `docs/wiki/specs/S3.3-er-pipeline.md` — 전문(4단계 표 5~13행, 승진 완화 15행, 회귀 3종 18행, CR-001 각주 19행)
- `docs/wiki/specs/S3.7-eval-spec.md` — 전문(지표·곡선 x축·산출물·"미달 시 재시도가 아니라 실패 케이스 분석" — 이 패키지가 바꾸지 않는 것)
- `docs/wiki/packages/P4-pilot-eval/04-review.md` — §4b 게이트 판정 수치, §4c R3·R4·R9 상태, §5 registry, §6 열린 소견 표(`mention_index` 비유일 4건·러너 `safe_summary`·stamp UTC), **§7 CR 절 1~7항**(코드 위치·재실행 규약·회귀 대상 테스트), 결과·승인 줄
- `docs/wiki/packages/P4-pilot-eval/01-plan.md` — 5행 의존 형식, 62~73행 작업 단위 문장, 75~87행 수용 기준+해석, **89~108행 판정 표 형식**(이 문서 판정 표의 본), 192~211행 결정 항목 서술 형식, 213~228행 결정 확정 표(A~L), 230~240행 리스크 절, 261~285행 읽은 카드 형식
- `reports/failure_cases.md` — §8 단계 귀속 표·한 줄 결론·`/devlog change` 후보 3종(반사실 수치 48→97·96·1), §10 한계 6항, §11 재현 `<PRE>` 머리글·R1 게이트 행(판정 표 12행의 본)
- `docs/user-setup/10-pilot-eval-run.md` — 전문(환경변수 이름 표, 절차 1~5, gzip 규약, trace 재계산 출력 형태, 종료 코드 0/1/2/3, "같은 설정으로 두 번 돌리지 않는다")
- `docs/wiki/registry.md` — 81·82·85행(`app/er/rules.py`·`confidence.py`·`pipeline.py` 등록 해시·요약), 33행(README 비고, F-0ffff5), 127~147행(P4 산출물 21행) grep
- `.claude/skills/entity-resolution/SKILL.md` — 22·36·39행 grep(**아직 D3 산식·"배제" 문장** → U0 의 근거)
- `docs/wiki/templates/plan.md` — 이 문서의 형식
- 코드(해당 함수만 Read): `app/er/confidence.py` 전문(`combine` 64행·`_breakdown` 133행·`_forced_decision` 176행·`decide` 223행), `app/er/rules.py` 전문(`_CONFLICT_PRIORITY` 54행·`_evaluate` 74행·`apply_rules` 122행·`_hierarchy_only_adjacent_conflict` 157행·`run_rule_stage` 174행), `app/er/pipeline.py`(`_run_pipeline` 156~235행·`resolve` 238행), `app/er/types.py` grep(`ScoredCandidate` 60~89행·`ERConfig` 287~307행), `app/settings.py` 60~153행(`ER_WEIGHTS` 78행·`er_config()` 110행), `scripts/run_pilot_eval.py` 700~770·900~960·1035행, `evaluation/curve.py` 183~188·528~534·656~662행 grep, `evaluation/calibration.py` 45~59·190~210·343~370행 grep, `evaluation/metrics.py` 569행 grep, `evaluation/resolvers/proposed.py` 109~120·185~188행 grep
- 테스트(위치 확인): `tests/test_er_pipeline.py` 389~568행(**회귀 3종 전문**), `tests/test_er_rules.py` 42~111행 grep, `tests/test_er_confidence.py` 50~101·181~196·293행 grep, `tests/test_run_pilot_eval.py` 450·497~625·644·770행 grep, `tests/test_eval_calibration.py:970` grep
- `CLAUDE.md` — 불변 원칙 1·2·3(D12 반영 문장)·4·8·9, 툴 7종 v2 표, 개발 프로세스(활성 패키지·증거·재실행 금지·L-001~L-004)
