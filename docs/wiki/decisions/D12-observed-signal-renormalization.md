# D12 · 확신도 결합은 관측된 신호만 재정규화한다 (D3 대체)

상태: 유효 | 대체하는 결정: D3 | 해결하는 검증: R4(재검증), P4 게이트 미달(결정 K) | 출처: CR-001(사용자 A 수용 2026-09-22) ← `reports/failure_cases.md` §4·§8, P4 04-review §4b·§7

**결정**
- `confidence = Σ_i w_i·s_i / Σ_i w_i`, i ∈ **관측된 신호**. 기본 가중치는 D3 그대로 `w_llm=0.5 · w_emb=0.3 · w_rule=0.2`.
- 세 신호가 모두 관측되면 분모가 1.0 이라 **D3 원식과 동일**: `0.5·s_llm + 0.3·s_emb + 0.2·s_rule`.
- `s_rule` 이 **미측정**(`rule_checked == 0` — hints 가 비어 규칙을 하나도 검사하지 못함)이면 `s_rule` 을 0 으로 넣지 않고 분모에서 뺀다: `(0.5·s_llm + 0.3·s_emb) / 0.8 = 0.625·s_llm + 0.375·s_emb`.
- `s_llm`·`s_emb` 는 항상 관측된다(LLM 오류 시 강등 경로는 별도 — `forced_reason`·`llm_error` 규약 유지). 즉 재정규화가 일어나는 경우는 현재 `s_rule` 미측정 하나뿐이다.
- trace `confidence_breakdown` 에 **`weights`(설정값)와 `weights_effective`(실제 적용된 정규화 가중치)·`rule_checked`** 를 모두 기록한다(원칙9). 재계산 검증(`--recheck-traces`)은 `weights_effective` 로 한다.

**이유**
- P4 실 실행(ef18143, 40건·141 mention): `rule_checked == 0` 이 141 중 100. D3 원식은 이때 `s_rule = 0` 을 합산해 확신도 **상한이 0.80** 에 묶였고(실측 최대 0.800), 사람에게 미룬 79건 중 52건이 `[0.7, 0.8)` 에 몰렸다. 그 52건을 `embedding_only` 베이스라인은 오병합 없이 맞혔다 → 결정 K 게이트 미달의 산술적 원인(`failure_cases.md` §4c·§4f).
- 미측정과 "검사했는데 0점"은 다른 정보다. 검사하지 못한 신호를 0점으로 합산하는 것은 근거 없는 감점이며, 원칙1(오병합 방지)에도 기여하지 않는다 — 감점된 것은 규칙 충돌 후보가 아니라 **힌트가 없는 발화 전부**였다.
- 반사실(저장 신호 재합산, 재실행 아님): `T_merge 0.8` 에서 merge 48 → 97, 골드 일치 96, 오병합 1건 그대로(그 1건은 2단계 원인 → D13). 가중치 비율(5:3:2)은 바꾸지 않는다 — 파일럿 표본 40건으로 비율을 다시 정하지 않는다(원칙8).

**파급** (갱신할 S 카드 · 영향 P 패키지 · CLAUDE.md 원칙)
- S3.3 4단계 산식 줄, `CLAUDE.md` 원칙3 문장, `docs/resolution-plan.md` §3.3(원문 유지 + CR-001 한 줄).
- 구현은 **P4b-er-redesign** 패키지: `app/er/confidence.py::combine()`(관측 신호 재정규화)·`_breakdown()`(`weights_effective`), `app/settings.py ER_WEIGHTS`(비율 유지), `scripts/run_pilot_eval.py --recheck-traces`(`weights_effective` 로 재계산, 설정 `ER_WEIGHTS` 와의 불일치 거부는 `weights` 키로), `evaluation/curve.py meta.weights`, `tests/test_er_*`·`tests/test_run_pilot_eval.py` 기대값.
- P4 기준선(`reports/pilot/raw-20260922-042440.jsonl.gz`·`reports/metrics.json`)은 D3 산식 결과로 **보존**한다. 재실행은 새 stamp.
- D10 유지(`T_merge 0.8`·`T_new 0.3` — 재실행 곡선으로 재확정). R3 방향(`T_merge`↑ → 오병합↓·질문↑)은 산식이 바뀌어도 단조성이 유지되어야 하며 재실행 곡선으로 재확인.

**코드에서 지켜야 할 것** (리뷰어가 grep 으로 확인할 수 있는 문장으로)
- `combine()` 은 `rule_checked` (또는 `s_rule is None`) 을 입력으로 받아 미측정이면 `(w_llm·s_llm + w_emb·s_emb) / (w_llm + w_emb)` 를 돌려준다. 세 신호가 모두 있으면 D3 원식과 **부동소수 오차 없이 같은 값**(테스트: 임의 표본에서 `abs diff == 0` 또는 `isclose`).
- `confidence_breakdown` 에 `weights`·`weights_effective`·`rule_checked` 키가 모두 있다(`grep -n weights_effective app/er/confidence.py`).
- `rule_checked > 0` 이고 `rule_passed == 0` 인 후보(검사했는데 전부 충돌)는 여전히 `s_rule = 0` 으로 **합산**된다 — 재정규화는 미측정에만 적용된다.
- 회귀 3종(승진 연결·팀장↔이모 배제·동명이인 분리, S3.3)이 그대로 통과한다.

**갱신 이력**
- 2026-09-22 신설 — CR-001 A 수용(사용자). 카드는 메인 세션이 기록, 구현은 P4b-er-redesign.
