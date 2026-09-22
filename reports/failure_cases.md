# 실패 케이스 분석 — 파일럿 40건 (P4-pilot-eval U8)

> 이 문서는 **해석만 한다.** 게이트 판정(pass/fail)은 다시 내리지 않고 `reports/metrics.json` 의 `gate` 를 그대로 옮긴다 — `dominated_by: ["embedding_only"]`, `d10_direction: true`, **`pass: false`**(결정 K 개정 (a), 01-plan 227행).
> 수치는 전부 아래 입력 파일에서 센 값이고, 절 11 에 세는 명령이 한 줄씩 있다(원칙8). 평가를 다시 돌리지 않았고 `data/`·`app/`·`evaluation/`·`reports/pilot/` 을 고치지 않았다.
> **§1~12 는 P4 실행(`raw-20260922-042440`) 기준선이고, §13 이 P4b 재실행(`raw-20260922-150931`)이다** — §1~12 의 수치·문장은 P4b 에서 한 글자도 고치지 않았다(P4b-er-redesign 결정 G(i)).

## 0. 메타 — 무엇을 어디서 읽었나

| 항목 | 값 | 출처 |
|---|---|---|
| 실행 id | `run-29621888da00` | `reports/metrics.json` → `meta.run_id` |
| 평가한 커밋 | `750f11b02f13c942c6d2ef8155646d5b7bc03ac6` (`750f11b`) | `meta.commit` (L-001) |
| 판정 공급자·모델 | `openai` · `gpt-4o-mini-2024-07-18` (설정 문자열 `gpt-4o-mini`) | `meta.provider`·`meta.model`·`meta.model_configured` |
| 임베딩 모델 | `text-embedding-3-small` (N=1536, D4) | `meta.embedding_model` |
| 데이터셋 해시 | `sha256:49cd8c4a1079e36ac1f2a7999a79f5ef36149441f8c5f528024f749a72eb899e` | `meta.dataset_hash` |
| 실행 모드 | `real` (스텁 아님) | `meta.run_mode` |
| 시나리오·행 | 40건 · 7050행 (141 mention × 5방식 × 10임계치) | `meta.scenario_count`·`meta.row_count` |
| 채점 분모 | 132 (골드 135 − `ambiguous` 3), `passing` 6 은 오탐 축 별도 | `meta.mention_counts`·`meta.denominator_rule` |
| 임계치 | `T_merge` = 0.8 (게이트 점), `T_new` = 0.3 고정 | `gate`·`meta.t_new` |

읽은 파일: `reports/metrics.json` · `reports/calibration.json` · `reports/pilot/raw-20260922-042440.jsonl.gz`(원시 판정 7050행) · `reports/pilot/traces-20260922-042440.jsonl`(`er_resolve` trace 1410건) · `data/scenarios/*.json`(골드 라벨·함정).
집계 출력 전문: `docs/wiki/packages/P4-pilot-eval/evidence/20260922-1354-u8-failure-cases.txt`.

### 출발점 (`T_merge` = 0.8, 분모 132 — `reports/eval.md` 의 표를 옮김)

| 방식 | 정답 병합 | **오병합** | **미검출** | 제3 범주(identity 보류) | 신규 판정 정답 | f1 |
|---|---|---|---|---|---|---|
| `proposed` | 47 | **1** (0.8%) | **1** (0.8%) | 79 (59.8%) | 4 | 0.566 |
| `exact_raw` | 83 | 0 | 33 (25.0%) | 2 | 14 | 0.826 |
| `exact_norm` | 91 | 4 (3.0%) | 20 (15.2%) | 6 | 11 | 0.854 |
| `embedding_only` | 95 | 0 | 1 (0.8%) | 31 (23.5%) | 5 | 0.892 |
| `llm_single` | 90 | 0 | 10 (7.6%) | 19 | 13 | 0.865 |

제안 방식은 **오병합·미검출 둘 다 1건**이지만, `embedding_only` 가 오병합 0 · 미검출 1 로 두 축 모두 같거나 낮아 **지배**한다(오병합 0 < 1 엄격). 제안 방식이 나머지 44건을 `ask_user(identity)` 로 밀어 넣은 것이 이 결과의 실체다. 아래는 그 44건이 어디서 나왔는지를 단계별로 추적한 것이다.

---

## 1. 오병합 1건 — 전문 (`sc-015` turn 0 `"부장님"`)

| 항목 | 값 |
|---|---|
| 시나리오 · 턴 · mention | `sc-015` · turn 0 · index 1 · `"부장님"` |
| 카테고리 · 함정 | `alias` · `nickname_shared_with_title` |
| 발화 | `"은우 별명이 부장님이야 잔소리 대마왕ㅋ"` |
| 골드 | `p1` = 조은우(DB id **11930**, `친구`/`동`) — 별칭 `은우`·`부장님`·`조은우` |
| 판정 결과 | `merge` → **11931 한지원**(`직장`/`상`, 별칭 `한부장`·`부장님`) = **오병합** |
| `expected_ask_user.allowed` | `["identity","none"]` |
| `trace_id` | 73821 (`reports/pilot/traces-20260922-042440.jsonl`) |

**후보 목록(1단계 결과, 원시 행 `candidates[]`)**

| 후보 | `s_emb` | `exact_alias` | `hierarchy_match` | `relation_tag_match` | `rule_checked`/`rule_passed` | `passed_rules` | `s_rule` |
|---|---|---|---|---|---|---|---|
| 11930 조은우 **(골드)** | 1.0 | 1.0 | 0.0 (`hierarchy_adjacent` 1.0) | **0.0** | 3/1 | **0 (탈락)** | 0.333 |
| 11931 한지원 | 1.0 | 1.0 | 1.0 | 1.0 | 3/3 | 1 | 1.0 |

**2단계 규칙 필터**: `excluded_by = {"11930": "relation_tag_conflict"}` — **정답 후보가 여기서 탈락했다.** 남은 후보는 한지원 하나뿐이다.

**3·4단계 확신도 분해** (`detail.confidence_breakdown`, trace 73821 과 동일)

```
s_llm = 0.9 (자기보고)  s_emb = 1.0  s_rule = 1.0  (rule_checked=3, rule_passed=3)
confidence = 0.5·0.9 + 0.3·1.0 + 0.2·1.0 = 0.95  ≥ T_merge 0.8 → merge
relaxed_retry = false,  forced_reason = null,  llm_error = null
```

**왜 `T_merge` 를 넘었는가**: 세 신호가 전부 "한지원"을 가리켰다. 별칭 `부장님` 이 실제로 한지원에 등록돼 있어 `s_emb` = 1.0, 위계·관계 태그가 모두 맞아 `s_rule` = 1.0, LLM 도 0.9 를 줬다. **정답 후보는 이미 2단계에서 사라져 3·4단계가 볼 수 없었다.** 즉 이 오병합은 "확신도 결합이 헐거워서"가 아니라 **규칙 필터가 정답을 지웠기 때문에 남은 오답이 만장일치로 보인 것**이다.

> ⚠ 제안 방식의 `detail` 에는 LLM `reason` 원문이 남지 않는다(`proposed` 0/141, `llm_single` 141/141 — 절 11 R23). U6 선행 보강이 프롬프트·`reason` 을 trace 덤프에서 제외했기 때문이다(security §1). **LLM 판정 문장 자체는 이 실행의 산출물로 재현할 수 없다** — 있는 그대로 적는다.

**같은 mention 의 다른 방식** (`T_merge` = 0.8)

| 방식 | 결정 | 인물 | 비고 |
|---|---|---|---|
| `proposed` | `merge` | 11931 | **오병합** |
| `exact_raw` | `identity` | – | `부장님` 이 두 인물에 걸려 단독 일치 아님 → 보류 |
| `exact_norm` | `identity` | – | 같음 |
| `embedding_only` | `identity` | – | `forced_reason = tie`(두 후보 `s_emb` 동률) → 보류 |
| `llm_single` | `identity` | – | reason: `"부장님이라는 별명이 두 사람에게 모두 사용될 수 있어 헷갈림."` |

**넷은 모두 "모른다"고 답했고 제안 방식만 확신했다.** 제안 방식만 규칙 필터로 후보를 하나로 줄였기 때문이다 — 동률(tie)이 사라지자 망설일 이유도 사라졌다.

### 다른 방식의 오병합 4건 (모두 `exact_norm`)

| 방식 | 시나리오 | mention | 골드 | 판정 |
|---|---|---|---|---|
| `exact_norm` | `sc-002` t3 | `과장님` | 11895 이서연 | → 11896 박지훈 (`promotion_collides_with_existing_title`) |
| `exact_norm` | `sc-036` t1·t2·t3 | `임대리` ×3 | DB 밖 신규 인물 | → 11946 이대리 (`new_person_resembles_existing`) |

`exact_raw`·`embedding_only`·`llm_single` 은 오병합 0 이다.

---

## 2. 미검출 1건 — 전문 (`sc-007` turn 2 `"문실장님"`)

| 항목 | 값 |
|---|---|
| 시나리오 · 턴 · mention | `sc-007` · turn 2 · index 1 · `"문실장님"` |
| 카테고리 · 함정 | `promotion` · 없음 |
| 발화 | t0 `"오늘 문쌤한테 피티 받았는데 빡셌음"` → t1 `"명찰이 실장으로 바뀌어 있더라"` → t2 `"문실장님 됐다고 커피 쏘심ㅋㅋ"` |
| 골드 | `p1` = 문태현(DB id **11903**, `지인`/`동`) — 별칭 `문쌤`·`태현쌤` |
| 판정 결과 | `new_person`(= `ask_user(kind="new_person")`) → **미검출**(결정 L: `new_person` 은 단정이므로 골드와 대조해 채점) |
| `expected_ask_user.allowed` | `["none"]` |
| `trace_id` | 71871 |

**후보 목록**: 1건 — 11903 문태현, `s_emb` = 0.314, `exact_alias` 0, `rule_checked` 2 / `rule_passed` 0, `passed_rules` **0**.
**2단계**: `excluded_by = {"11903": "relation_tag_conflict"}` → **통과 후보 0**.
**3단계**: `llm_skipped = true`, `llm_attempts = 0` — LLM 을 부르지 못했다.
**4단계**: `forced_reason = "no_candidates"`, 확신도 분해는 전부 0(`s_llm`=`s_emb`=`s_rule`=0, `confidence`=0.0) → `< T_new 0.3` → `new_person`.

**왜 놓쳤는가**: 승진 호칭 변경(`문쌤` → `문실장님`)이라 1단계 임베딩 유사도가 0.314 로 낮았고, 2단계가 관계 태그 충돌로 그 하나를 마저 떨어뜨렸다. **후보가 0 이 되면 확신도가 계산되지 않고 0.0 으로 강제**되어 `T_new` 아래로 떨어진다 — "모르겠으니 물어본다"가 아니라 "새 사람이다"라고 단정하게 된다.

**같은 mention 의 다른 방식**

| 방식 | 결정 | 결과 |
|---|---|---|
| `proposed` | `new_person` | 미검출 |
| `exact_raw` | `new_person` | 미검출 |
| `exact_norm` | `new_person` | 미검출 |
| `embedding_only` | `identity` (`score` 0.314) | 보류 — 미검출 아님 |
| `llm_single` | `merge` → 11903 | **정답** (reason: `"문실장님은 문태현과 같은 인물로 보입니다."`) |

**`embedding_only` 의 미검출 1건은 다른 mention 이다**: `sc-021` turn 2 `"아까 걔"`(pronoun, 골드 11914 표동혁). 후보 3명의 `s_emb` 가 0.299 / 0.288 / 0.248 로 전부 `T_new` 언저리였고 최고값 0.299 < 0.3 → `new_person`. 같은 mention 에서 제안 방식은 `identity` 로 보류했다(LLM 이 `no_matched`). 두 방식의 미검출률이 1/132 로 같은 것은 **우연히 수가 같을 뿐 원인이 다르다.**

---

## 3. 강제 경로 30건 (`forced_reason`, `T_merge` = 0.8, 분모 138)

`metrics.json` 의 분포는 `no_matched` **25** + `no_candidates` **5** + `none` 108 = 138 이다(141행 − `ambiguous` 3행; 제외된 3건 중 `sc-022` t1·`sc-024` t4 가 `no_matched`, `sc-013` t3 은 강제 아님).

| `forced_reason` | 수 | 단계 귀속 | 정의 |
|---|---|---|---|
| `no_matched` | 25 | **3단계 LLM 판정** (회수 실패 13 / 옳은 거절 12 — 아래 3b) | 후보가 있고(25/25 모두 후보 ≥ 1, 전부 규칙 통과 후보 보유) LLM 을 실제로 불렀는데(`llm_attempts` 1, `llm_skipped` false) `matched_person_id: null` 을 돌려줬다 → 확신도 0.0 강제 → `identity` |
| `no_candidates` | 5 | **1단계 후보 검색(3건) / 2단계 규칙 필터(2건)** | 3단계에 넘길 후보가 0 → LLM 건너뜀(`llm_skipped` true 5/5) |

### 3a. `no_candidates` 5건 — 후보 검색이 못 찾았나, 규칙이 떨어뜨렸나

| 시나리오 | mention | 후보 수 | `excluded_by` | 귀속 | 결과 |
|---|---|---|---|---|---|
| `sc-007` t2 | `문실장님` | 1 | `{11903: relation_tag_conflict}` | **2단계** | **미검출**(절 2) |
| `sc-036` t1 | `그 친구` | 1 | `{11946: relation_tag_conflict}` | **2단계** | `new_person_correct`(결과적 정답) |
| `sc-037` t0 | `시우` | 0 | `{}` | **1단계** | `new_person_correct` |
| `sc-037` t1 | `시우형` | 0 | `{}` | **1단계** | `new_person_correct` |
| `sc-037` t2 | `형` | 0 | `{}` | **1단계** | `new_person_correct` |

`sc-037` 3건은 DB 에 아무도 없는 진짜 신규 인물이므로 후보 0 이 정상이다. **문제는 2단계가 만든 2건**이고, 그중 하나가 유일한 미검출이다.

### 3b. `no_matched` 25건 — 카테고리 분포

| 카테고리 | 수 | 대표 mention |
|---|---|---|
| `pronoun` | 9 | `걔`·`쟤`·`얘`·`그 사람`·`아까 걔`·`심팀장` |
| `new_person` | 8 | `장하람`·`하람씨`×2, `남주 배우`·`배달 기사님`·`기사님`·`웬 아저씨`·`그 정치인`(뒤 5건은 `passing` mention) |
| `promotion` | 5 | `김부장님`·`박과장님`×2·`최대리`·`회장님` |
| `alias` | 4 | `영어쌤`×2·`권쌤`×2 |
| `normal` | 1 | `심팀장` |

**25건 전부 후보가 있었고 전부 LLM 을 호출했다** — 후보 검색(1단계)이 놓친 것이 아니다. 3단계가 "이 중에 없다"고 답한 것이다. 25건을 정오로 가르면:

| 구분 | 수 | 판단 |
|---|---:|---|
| `passing` mention (지나가는 언급) | 5 | **옳은 거절** — 제안 방식 오탐 0/6, `exact_raw`·`exact_norm`·`llm_single` 6/6, `embedding_only` 2/6 |
| 골드가 **DB 밖** 신규 인물 (`sc-012` `영어쌤`·`권쌤` 4 · `sc-035` `장하람`·`하람씨` 3) | 7 | **옳은 거절** — 다만 결정이 `identity` 보류라 `new_person` 정답으로는 안 잡힌다 |
| 골드가 **DB 안**이고 **후보 목록에도 있었는데** `null` | **13** | **3단계 회수 실패** — 13/13 모두 후보에 골드 포함(`sc-001`·`sc-002`×2·`sc-003`·`sc-005`·`sc-017`·`sc-018`·`sc-019`·`sc-020`×2·`sc-021`·`sc-024`·`sc-033`) |

즉 `no_matched` 25건 중 **12건은 제대로 거절한 것**이고, **13건만이 3단계의 실패**다. 13건은 오병합이 아니라 `identity` 보류로 갔으므로 안전하지만 마찰이다.

> 강제 경로의 확신도는 전부 `0.0`(`s_llm`=`s_emb`=`s_rule`=0)이다. 이 자리표시 0.0 은 보정표에서 `placeholder_s_llm` 20건으로 제외된다(`calibration.json.excluded`).

---

## 4. `ask_user(identity)` 79건의 구성 — 지배의 원인

`proposed` 의 제3 범주 79/132(59.8%) 대 `embedding_only` 31/132(23.5%). **차이 48건이 어디서 왔는지가 이 절의 질문이다.**

### 4a. 확신도 구간 분포

| 구간 | 수 | 해석 |
|---|---:|---|
| `0.0`(강제 경로) | 20 | `no_matched` — 확신도 계산 자체를 못 했다 |
| `[0.3, 0.5)` | 2 | |
| `[0.5, 0.7)` | 5 | |
| **`[0.7, 0.8)`** | **52** | **임계치 바로 아래** — `0.75` 29건 · `0.775` 15건 · 나머지 8건 |

**79건 중 52건(66%)이 0.7~0.8 구간에 몰려 있다.** 0.75 라는 값이 29번 똑같이 나온 것은 우연이 아니다 — 아래 4c 의 구조적 상한이다.

### 4b. 신호별 분포 (79건, `detail.confidence_breakdown`)

| 신호 | 중앙값 | 평균 | 값 분포 |
|---|---:|---:|---|
| `s_llm` | 0.900 | 0.675 | 0.0 → 20건 · 0.7 → 1 · 0.8 → 5 · **0.9 → 36** · 0.95 → 16 · 1.0 → 1 |
| `s_emb` | 1.000 | 0.670 | 0.0 → 20건 · **1.0 → 44건** · 나머지 15건은 0.285~0.927 산재 |
| **`s_rule`** | **0.000** | **0.072** | **0.0 → 72건** · 0.667 → 4 · 1.0 → 3 |
| `confidence` | 0.750 | 0.553 | 0.0 → 20 · **0.75 → 29** · **0.775 → 15** · 나머지 |

> 사분위: `confidence` q1 0.000 / med 0.750 / q3 0.750, `s_llm` q1 0.000 / med 0.900 / q3 0.900, `s_emb` q1 0.000 / med 1.000 / q3 1.000, `s_rule` q1 0.000 / med 0.000 / q3 0.000.

**`s_rule` 이 79건 중 72건에서 0 이다.** `s_llm`·`s_emb` 는 높은데 `s_rule` 만 바닥이다.

### 4c. 왜 `s_rule` 이 0 인가 — `rule_checked = 0` 연쇄

| 관측 | 수 | 명령 |
|---|---:|---|
| `derive_hints` 가 빈 dict 인 mention (`embedding_only.detail.hints`) | **91/141 (64.5%)** | `meta.empty_derive_hints` 와 같은 값 |
| `proposed` 에서 `rule_checked == 0` | **100/141 (70.9%)** | R12 |
| 교차: (hints 비었음, `rule_checked`=0) | 91 / (hints 있음, `rule_checked`=0) 9 / (hints 있음, `rule_checked`>0) 41 | R12 |
| `s_rule == 0.0` 인 mention 중 `rule_checked == 0` | 100/100 | R12 |

**`rule_checked = 0` 이면 `s_rule = 0` 이고, 그러면 확신도의 구조적 상한은**

```
confidence ≤ 0.5·1.0 + 0.3·1.0 + 0.2·0 = 0.80
```

즉 **규칙을 한 항목도 재지 못한 mention 은 `s_llm`·`s_emb` 가 동시에 만점일 때만 겨우 `T_merge` 에 닿는다.** 실측도 정확히 그렇다 — `rule_checked = 0` 인 mention 의 확신도 최댓값은 **0.800** 이고(그 값이 14건), `rule_checked > 0` 인 mention 의 최댓값은 1.0 이다. LLM 이 0.9 를 주고 임베딩이 1.0 이어도 `0.5·0.9 + 0.3·1.0 = 0.75` 로 **자동으로 ask_user 가 된다.**

### 4d. deferred 79건을 원인별로 나누면

| 원인 | 수 | 단계 귀속 |
|---|---:|---|
| 규칙 신호 미측정(`rule_checked` = 0)이 0.2 를 통째로 깎아 0.8 미만 | **52** | **4단계 확신도 결합 + 2단계가 신호를 못 냄** |
| 강제 경로 `no_matched` — 확신도 계산 자체가 0 | 20 | 3단계 LLM 판정 |
| 규칙은 쟀는데 합산이 0.8 미만 | 7 | 4단계(정상 동작) |

### 4e. "물었지만 사실 맞았을 건"

| 지표 | 값 |
|---|---:|
| deferred 79건 중 골드가 DB 안 인물인 건 | 69 |
| 그중 후보 목록에 골드가 들어 있던 건 | **69/69 (100%)** — 1단계는 놓치지 않았다 |
| `confidence_breakdown.matched_person_id` 가 **골드와 같았던 건** | **61/79 (77.2%)** |
| 귀속 인물이 있는 deferred 59건 기준 | 골드 일치 54 / 불일치 5 |

**79번 물어본 것 중 61번은 시스템이 이미 정답을 알고 있었다.** 원칙1(오병합 ≫ 미검출)에 따르면 물어보는 쪽이 안전하지만, 이 비율은 "안전 마진"이 아니라 **신호 하나가 측정되지 않아 생긴 기계적 감점**이다.

### 4f. 같은 79 mention 을 `embedding_only` 는 어떻게 판정했나

| `embedding_only` 결과 | 수 |
|---|---:|
| `merge_correct` | **52** |
| `deferred` | 24 |
| `new_person_correct` | 2 |
| `miss` | 1 |

**제안 방식이 물어본 79건 중 52건을 `embedding_only` 는 오병합 없이 맞혔다.** 이 52 가 `merge_correct` 95 대 47 의 차이(48)와 제3 범주 79 대 31 의 차이(48)를 거의 그대로 설명한다. **지배의 산술적 원인은 여기다.**

### 4g. 그래도 LLM 판정 자체는 나쁘지 않았다

임계치와 무관하게 "LLM 이 고른 인물이 골드였는가"만 보면 (`matched_person_id` 가 있는 107건):

| `s_llm` 구간 | n | 귀속 정답 | 정확도 |
|---|---:|---:|---:|
| 0.9–1.0 | 101 | 98 | **97.0%** |
| 0.8–0.9 | 5 | 2 | 40.0% |
| 0.7–0.8 | 1 | 1 | 100% |
| 합계 | 107 | 101 | 94.4% |

보정표(`reports/calibration.json`)의 `proposed` 0.9–1.0 칸이 46.5%(47/101)로 낮게 보이는 것은 **정답 정의가 `classify_gold_row ∈ {merge_correct, new_person_correct}` 여서 `deferred` 가 전부 오답으로 계산되기 때문**이다(결정 F(i)). 같은 모델·같은 구간에서 `llm_single` 은 88.0%(103/117)다. 두 수의 차이는 LLM 품질 차이가 아니라 **제안 방식만 확신도 게이트를 통과해야 한다는 조건 차이**다 — 보정표 수치를 "LLM 이 과신한다"로 읽으면 안 된다.

---

## 5. `T_merge` 격자 전체 — 지배가 풀리는 점이 있나

셀 = **오병합 n / 미검출 n / `ask_user(identity)` n** (분모 132). 지배 계산은 결정 K 산식을 격자 전체에 그대로 적용한 **참고값**이다 — 게이트 판정은 `T_merge` = 0.8 한 점에서만 내린다(`metrics.json.gate`).

| `T_merge` | `proposed` | `exact_raw` | `exact_norm` | `embedding_only` | `llm_single` | 참고: `dominated_by` |
|---|---|---|---|---|---|---|
| 0.50 | 6 / 1 / 22 | 0 / 33 / 2 | 4 / 20 / 6 | 6 / 1 / 19 | 0 / 10 / 19 | **[]** |
| 0.55 | 6 / 1 / 22 | 0 / 33 / 2 | 4 / 20 / 6 | 3 / 1 / 22 | 0 / 10 / 19 | [`embedding_only`] |
| 0.60 | 6 / 1 / 22 | 0 / 33 / 2 | 4 / 20 / 6 | 1 / 1 / 25 | 0 / 10 / 19 | [`embedding_only`] |
| 0.65 | 6 / 1 / 23 | 0 / 33 / 2 | 4 / 20 / 6 | 1 / 1 / 27 | 0 / 10 / 19 | [`embedding_only`] |
| 0.70 | 4 / 1 / 27 | 0 / 33 / 2 | 4 / 20 / 6 | 0 / 1 / 29 | 0 / 10 / 19 | [`embedding_only`] |
| 0.75 | 2 / 1 / 33 | 0 / 33 / 2 | 4 / 20 / 6 | 0 / 1 / 30 | 0 / 10 / 19 | [`embedding_only`] |
| **0.80** | **1 / 1 / 79** | 0 / 33 / 2 | 4 / 20 / 6 | **0 / 1 / 31** | 0 / 10 / 19 | **[`embedding_only`]** ← 게이트 |
| 0.85 | 1 / 1 / 96 | 0 / 33 / 2 | 4 / 20 / 6 | 0 / 1 / 31 | 0 / 10 / 19 | [`embedding_only`] |
| 0.90 | 1 / 1 / 105 | 0 / 33 / 2 | 4 / 20 / 6 | 0 / 1 / 38 | 0 / 10 / 19 | [`embedding_only`] |
| 0.95 | 1 / 1 / 114 | 0 / 33 / 2 | 4 / 20 / 6 | 0 / 1 / 43 | 0 / 10 / 19 | [`embedding_only`] |

**지배가 풀리는 점은 `T_merge` = 0.50 하나뿐이고, 그것은 개선이 아니다.** 그 점에서 제안 방식의 오병합은 6/132(4.5%)이고 `embedding_only` 도 6/132 로 **두 축이 동률이라 "미지배"가 된 것**(결정 K: 동률이면 미지배)이지, 제안 방식이 나아진 것이 아니다. 원칙1(오병합 = 신뢰 붕괴)에 비추면 `T_merge` 를 0.5 로 내리는 것은 게이트 통과를 위해 가장 나쁜 축을 6배로 키우는 선택이다 — **임계치 조정만으로는 이 게이트를 통과할 수 없다.**

또 하나: 제안 방식의 `ask_user(identity)` 는 0.75 → 0.8 구간에서 **33 → 79 로 두 배 이상 뛴다.** 4c 의 상한(0.75/0.775 에 52건이 정체) 때문이며, 곡선의 이 한 칸이 게이트 점의 마찰을 만든다. D10 방향(`T_merge`↑ → 오병합 비증가·`ask_user`↑) 자체는 9쌍 전부에서 지켜졌다(`d10_direction: true`).

---

## 6. 함정 12 시나리오 (7종, 55 mention) 에서의 거동

`data/scenarios/*.json` 의 `trap` 이 붙은 시나리오는 12건(`sc-002`·`sc-004`·`sc-006`·`sc-008`·`sc-010`·`sc-012`·`sc-013`·`sc-015`·`sc-036`·`sc-038`·`sc-039`·`sc-040`)이고 그 안의 mention 은 55개다. 아래 표는 **골드 채점 대상 mention 만** 센다(`passing` 6·`ambiguous` 1 제외 → 48).

표기: `ok` 정답 병합 / `fm` 오병합 / `ms` 미검출 / `df` identity 보류 / `np` 신규 판정 정답.

| 함정 종류 | 시나리오 | 채점 mention | `proposed` | `exact_raw` | `exact_norm` | `embedding_only` | `llm_single` |
|---|---:|---:|---|---|---|---|---|
| `same_title_two_persons` | 3 | 14 | ok6 df8 | ok4 ms6 np4 | ok6 ms1 df3 np4 | ok7 df7 | ok7 df3 np4 |
| `promotion_collides_with_existing_title` | 2 | 9 | ok4 df5 | ok4 ms5 | ok7 **fm1** ms1 | ok6 df3 | ok7 ms1 df1 |
| `new_person_resembles_existing` | 1 | 6 | ok2 df3 np1 | ok2 np4 | ok2 **fm3** np1 | ok2 df4 | ok1 df2 np3 |
| `passing_mention` | 3 | 6 | ok3 df3 | ok2 ms4 | ok4 ms2 | ok6 | ok6 |
| `nickname_shared_with_title` | 1 | 5 | ok2 **fm1** df2 | ok2 ms1 df2 | ok2 df3 | ok3 df2 | ok2 df3 |
| `similar_name_two_persons` | 1 | 4 | df4 | ok3 ms1 | ok3 ms1 | ok4 | ok2 df2 |
| `nickname_shared` | 1 | 4 | ok2 df2 | ok4 | ok4 | ok4 | ok2 df2 |

읽을 점 세 가지.

1. **제안 방식은 함정에서 오병합을 거의 내지 않지만(1건), 대신 전부 보류로 간다** — 48건 중 27건이 `df`. `similar_name_two_persons`(`채원씨`/`채영이`)에서는 4건 전부 보류라 정답 병합이 0 이다. `embedding_only` 는 같은 4건을 오병합 없이 전부 맞혔다.
2. **`exact_norm` 의 오병합 4건이 전부 함정에서 나왔다** — 정규화가 `과장님`→박과장, `임대리`→`이대리` 를 같게 만든다. 문자열 정규화의 위험이 정확히 함정 설계대로 드러났다.
3. **`passing_mention`(지나가는 언급)에서 제안 방식만 오탐 0**: `passing` mention 6건을 전부 `identity` 보류로 처리했고(오탐 0/6), `exact_raw`·`exact_norm`·`llm_single` 은 6/6 전부 인물 등록 결정(`new_person`), `embedding_only` 는 2/6. **원칙2 의 "확신도 低에서 자동 `create_person` 금지"가 실제로 작동한 유일한 방식이다.** 이 축은 게이트 산식(오병합·미검출)에 들어가지 않아 지배 판정에 반영되지 않았다 — 있는 그대로 적어 둔다.

---

## 7. 카테고리별 (`T_merge` = 0.8) — 오병합 / 미검출 / identity 보류 / 채점 수

| 카테고리 | `proposed` | `exact_raw` | `exact_norm` | `embedding_only` | `llm_single` |
|---|---|---|---|---|---|
| `promotion` (28) | 0 / **1** / 12 | 0 / 16 / 0 | **1** / 7 / 3 | 0 / 0 / 11 | 0 / 5 / 4 |
| `pronoun` (31) | 0 / 0 / **25** | 0 / 9 / 0 | 0 / 9 / 0 | 0 / **1** / 8 | 0 / 5 / 6 |
| `alias` (33) | **1** / 0 / 21 | 0 / 3 / 2 | 0 / 2 / 3 | 0 / 0 / 7 | 0 / 0 / 7 |
| `normal` (21) | 0 / 0 / 12 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `new_person` (19) | 0 / 0 / 9 | 0 / 5 / 0 | **3** / 2 / 0 | 0 / 0 / 5 | 0 / 0 / 2 |

- **`pronoun` 이 제안 방식의 최대 마찰원**: 31건 중 25건(80.6%)이 보류다. 지시대명사는 표면형에 정보가 없어 `s_emb` 가 낮고 호칭 사전이 걸리지 않아 `rule_checked` 도 0 이 되기 쉽다 — 4c 의 상한에 그대로 걸린다.
- **`normal` 21건에서 제안 방식만 12건을 물었다.** 나머지 네 방식은 `normal` 에서 오류도 보류도 0 이다. 쉬운 케이스에서조차 확신도가 0.8 에 못 미친다는 뜻으로, 4c 가 카테고리를 가리지 않는 구조적 문제임을 보여 준다.
- `promotion` 의 유일한 미검출이 절 2 의 `sc-007` 이고, `alias` 의 유일한 오병합이 절 1 의 `sc-015` 다.

---

## 8. S3.3 단계 귀속 결론

S3.3 의 네 단계(1 후보 검색 → 2 규칙 필터 → 3 LLM 판정 → 4 확신도 결합·분기)에 실패를 귀속하면:

| 단계 | 이 실행에서의 책임 | 근거 |
|---|---|---|
| **1. 후보 검색** | **거의 없음.** deferred 79건 중 골드가 DB 안 인물인 69건 전부(69/69)에서 골드가 후보 목록 안에 있었다. `no_candidates` 5건 중 3건은 DB 에 아무도 없는 정상 케이스. 약점은 승진 호칭(`문쌤`→`문실장님` `s_emb` 0.314)·지시대명사(`아까 걔` 최고 0.299)에서 유사도가 낮아진다는 것뿐이다 | 4e · 3a |
| **2. 규칙 필터** | **오병합 1건·미검출 1건 = 제안 방식의 오류 전부가 여기서 시작됐다.** 골드 인물을 떨어뜨린 mention 6건(`relation_tag_conflict` 2 + `hierarchy_conflict` 4) 중 1건이 오병합(`sc-015`), 1건이 미검출(`sc-007`), 4건이 보류. 전체로는 19/141 mention 에서 제외가 일어났고 사유는 `relation_tag_conflict` 12 · `hierarchy_conflict` 7 | 절 1 · 절 2 · evidence PART 3 |
| **3. LLM 판정** | **정확하지만 회수율이 낮다.** 귀속 인물의 정답률은 `s_llm` ≥ 0.9 에서 97.0%(98/101). `no_matched` 25건 중 12건은 옳은 거절(`passing` 5 + DB 밖 신규 7)이고 **13건이 회수 실패**다 — 골드가 DB 안이고 후보 목록에도 있었는데 `null` 을 돌려줬다. LLM 오류(`llm_error`)는 0 | 4g · 3b |
| **4. 확신도 결합** | **마찰 79건의 주범.** `s_rule` 이 미측정(`rule_checked`=0)일 때도 0 으로 합산되어 확신도 상한이 0.80 으로 고정된다. deferred 79건 중 52건이 이 경로이고, 그중 `embedding_only` 가 오병합 없이 맞힌 것이 52건이다 | 4c · 4d · 4f |

**한 줄 결론: 제안 방식이 `embedding_only` 에 지배된 것은 판정이 틀려서가 아니라, 2단계가 정답 후보를 떨어뜨린 6건과 4단계가 "재지 못한 규칙 신호(`rule_checked`=0, 141 중 100)"를 0 점으로 합산해 확신도 상한을 0.80 에 묶은 52건 — 즉 2·4단계 때문이다.**

### `/devlog change` 후보 (셋 다 **후보**일 뿐, 결정은 사용자)

1. **미측정 신호의 가중치 재정규화 (4단계).** `rule_checked == 0` 이면 `s_rule` 을 0 으로 합산하지 말고 남은 두 신호로 가중치를 재정규화한다(`0.5/0.3` → `0.625/0.375`). **반사실 실측**: `T_merge` 0.8 을 그대로 두고 이 규칙만 적용하면 merge 48 → **97**, 그중 골드 일치 **96**, 오병합은 **1건 그대로**(`sc-015`, 원인이 2단계라 이 변경과 무관). 원칙3 의 3신호 결합 자체는 유지된다(가중치 비율 불변, 분모만 관측된 신호로). 원칙3 의 산식 문장을 바꾸는 변경이므로 CR 대상이다.
2. **2단계를 배제(exclude)에서 감점(penalty)으로 (2단계).** `relation_tag_conflict`·`hierarchy_conflict` 를 후보 제거가 아니라 `s_rule` 감점으로 바꾸면 `sc-015` 에서 조은우가 후보로 남아 LLM 이 두 후보를 비교할 수 있고(넷 중 넷이 `identity` 로 망설인 mention), `sc-007` 은 `no_candidates` 가 아니라 정상 판정 경로를 탄다. 위험: 후보가 늘어 오병합 기회도 는다 — 40건으로는 검증할 수 없다.
3. **`T_merge` 재설정은 단독으로는 답이 아니다.** 절 5 가 보여 주듯 0.8 → 0.75 는 마찰을 79 → 33 으로 줄이지만 오병합을 1 → 2 로 늘리고 지배는 그대로다. 임계치는 1·2 를 적용한 **뒤에** 곡선을 다시 그려 정한다.

절 4g 의 이유로 **보정표만 보고 `s_llm` 을 보정하는 변경은 권하지 않는다** — 이 실행에서 LLM 자기보고는 과신의 증거를 보이지 않았다.

---

## 9. 검수 필요 라벨

**없음.** 다섯 방식 전부가 오답(`false_merge` 또는 `miss`)인 mention 은 **0건**이고, 다섯 방식 전부가 보류인 mention 도 0건이다(evidence PART 1 §12·§I). 라벨이 특정 방식에 유리·불리하게 쏠린 흔적은 찾지 못했다.

한 건만 관찰로 남긴다 — `sc-015` t0 `"부장님"`(골드 `p1` 조은우). 별칭 `부장님` 이 두 인물에 모두 등록돼 있어 표면형만으로는 가를 수 없지만, 발화 `"은우 별명이 부장님이야"` 가 같은 턴 안에서 근거를 준다. **라벨은 타당하며 `trap.reason` 이 의도를 명시한다.** `data/` 는 고치지 않았다(인계 9).

---

## 10. 한계

- **표본 40 시나리오 · 채점 mention 132.** 오병합 1건이 0.76%p 를 움직인다. 카테고리당 19~33 mention, 함정 종류당 4~14 mention 이므로 **종류별 비율은 방향 표시일 뿐 추정치가 아니다.** 신뢰구간은 P10(150건)에서 낸다.
- **공급자 1벌.** `openai` / `gpt-4o-mini-2024-07-18` 한 모델의 결과다. Gemini·Anthropic 경로는 실호출 0 이므로 "LLM 판정이 정확하다"는 이 모델에 한정된다.
- **LLM `reason` 원문이 제안 방식에는 없다.** 절 1 의 "LLM 이 왜 0.9 를 줬는가"는 재현 불가이며, 이 문서는 남은 수치(`s_llm`·후보·`excluded_by`)로만 추론했다.
- **반사실(절 8 후보 1)은 저장된 신호를 다시 합산한 계산**이지 재실행 결과가 아니다. 가중치를 바꾸면 LLM 프롬프트·후보는 그대로이므로 이 계산이 유효하지만, 실제 채택 시에는 U7 과 같은 실행으로 확인해야 한다.
- **`ambiguous` 3건·`passing` 6건은 정확도 축 분모 밖**이다(`meta.denominator_rule`). 절 6 의 `passing` 관찰은 별도 축(`passing.false_positive`)이다.
- **이 문서는 게이트를 다시 판정하지 않는다.** `pass: false` 는 `metrics.json.gate` 의 값이다.

---

## 11. 재현 (같은 입력 → 같은 수치)

전제: 저장소 루트에서, `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 을 앞에 붙인다(Windows cp949 로케일 대비). 네트워크·DB·LLM 을 쓰지 않는다.

공통 머리글(아래 `<PRE>` 로 표기):

```python
import gzip,json,sys;sys.path.insert(0,".");from collections import Counter
from evaluation.metrics import classify_gold_row
R=[json.loads(l) for l in gzip.open("reports/pilot/raw-20260922-042440.jsonl.gz","rt",encoding="utf-8")]
K=lambda r:(r["scenario_id"],r["mention_kind"],r["mention_index"])          # metrics._mention_key 와 동일
G=lambda m,t:[r for r in R if r["method"]==m and r["t_merge"]==t and r["mention_kind"]=="gold" and not r["ambiguous"]]
S0=lambda m:[r for r in R if r["method"]==m and r["sweep_index"]==0]        # mention 당 한 행
```

| # | 무엇을 세나 | 명령 본문 (`python -c '<PRE>; …'`) | 기대 출력 |
|---|---|---|---|
| R1 | 게이트 | `import json;g=json.load(open("reports/metrics.json",encoding="utf-8"))["gate"];print(g["t_merge"],g["dominated_by"],g["d10_direction"],g["pass"])` | `0.8 ['embedding_only'] True False` |
| R2 | 방식별 결과 분포 | `[print(m,dict(Counter(classify_gold_row(r) for r in G(m,0.8)))) for m in ["proposed","exact_raw","exact_norm","embedding_only","llm_single"]]` | 절 0 표 |
| R3 | 오병합 전건 | `[print(m,r["scenario_id"],r["turn"],r["mention"],r["gold_db_person_id"],"->",r["person_id"]) for m in [...] for r in G(m,0.8) if classify_gold_row(r)=="false_merge"]` | 5행 (proposed 1 · exact_norm 4) |
| R4 | 미검출 전건 | `… if classify_gold_row(r)=="miss"` (`proposed`·`embedding_only`) | `sc-007 2 문실장님 no_candidates` / `sc-021 2 아까 걔 None` |
| R5 | 강제 경로 분포 | `print(dict(Counter(r["detail"]["forced_reason"] for r in R if r["method"]=="proposed" and r["t_merge"]==0.8 and not r["ambiguous"])))` | `{None: 108, 'no_matched': 25, 'no_candidates': 5}` |
| R6 | `no_matched` 가 LLM 을 불렀나 | `F=[… forced_reason=="no_matched"];print(len(F),Counter(r["detail"]["llm_attempts"] …),Counter(r["detail"]["llm_skipped"] …),Counter(bool(r["candidates"]) …))` | `25 {1:25} {False:25} {True:25}` |
| R7 | `no_candidates` 5건 | `[print(r["scenario_id"],r["turn"],r["mention"],len(r["candidates"]),r["detail"]["excluded_by"]) for r in R if … forced_reason=="no_candidates"]` | 절 3a 표 |
| R8 | deferred 확신도 구간 | `D=[r for r in G("proposed",0.8) if classify_gold_row(r)=="deferred"];print(len(D), Counter(…))` | `79` / `{'0.0':20,'[0.3,0.5)':2,'[0.5,0.7)':5,'[0.7,0.8)':52}` |
| R9 | deferred 신호 분포 | `D=[r["detail"]["confidence_breakdown"] …];` `s_llm`·`s_emb`·`s_rule`·`confidence` 중앙값·분포 | 절 4b 표 |
| R10 | 물었지만 맞았을 건 | `print(sum(1 for r in D if r["detail"]["confidence_breakdown"]["matched_person_id"]==r["gold_db_person_id"]),"/",len(D))` | `61 / 79` |
| R11 | 같은 79 의 `embedding_only` | `E={K(r):r for r in G("embedding_only",0.8)};print(Counter(classify_gold_row(E[K(r)]) for r in D))` | `{'merge_correct':52,'deferred':24,'new_person_correct':2,'miss':1}` |
| R12 | `rule_checked=0` 연쇄 | `P={K(r):r for r in S0("proposed")};E={K(r):r for r in S0("embedding_only")};` hints 빈 dict 수 · `rule_checked==0` 수 · 교차 | `91/141` · `100/141` · `{(F,F):41,(F,T):9,(T,T):91}` |
| R13 | 확신도 상한 | `C=[r["detail"]["confidence_breakdown"] for r in S0("proposed")];print(max(c["confidence"] for c in C if c["rule_checked"]==0))` | `0.8` (`rule_checked>0` 은 `1.0`) |
| R14 | LLM 귀속 정확도 | `s_llm` 구간 × (`matched_person_id`==골드) 교차 | `('0.9-1.0',True):98, ('0.9-1.0',False):3, …` |
| R15 | 격자별 지배 | `metrics.json` 의 `by_t_merge[*]` 3계열 나열 | 절 5 표 |
| R16 | 함정 규모 | `T=[… trap_kind];print(len(T), len({r["scenario_id"] …}), Counter(r["trap_kind"] …))` | `55 12 {…7종…}` |
| R17 | 카테고리별 | `metrics.json` `by_t_merge["0.8"]["by_category"]` | 절 7 표 |
| R18 | `passing` 오탐 | `metrics.json` `by_t_merge["0.8"]["passing"]` | proposed `0/6`, exact_* · llm_single `6/6`, embedding_only `2/6` |
| R19 | 보정표 | `calibration.json` 의 `groups[*].bins` 중 `n>0` | proposed `0.9-1.0 101/47`, llm_single `0.9-1.0 117/103` |
| R20 | 반사실 재정규화 | `rule_checked==0` 이면 `0.625·s_llm+0.375·s_emb`, 아니면 그대로 → `>=0.8` 집계 | `merge 97 골드일치 96 불일치 1` |
| R21 | 부분집합 | `metrics.json` `by_t_merge["0.8"]["subsets"]` | `merge_rule_unchecked 14/오병합 0`, `merge_relaxed_retry 14/오병합 0` |
| R22 | trace 확신도 재계산 | `traces-…jsonl` 에서 `trace_id==73821` 의 가중합 | `0.95 == 0.95` (abs diff 0, 원칙3·9) |
| R23 | `reason` 보존 여부 | `sum(1 for r in S0(m) if "reason" in r["detail"])` | `proposed 0` / `llm_single 141` |
| R24 | `no_matched` 25 의 정오 분해 | `F=[… forced_reason=="no_matched"];print(Counter(r["mention_kind"] …), sum(1 for r in F if r["gold_db_person_id"] is not None), sum(1 for r in F if r["gold_db_person_id"] is not None and any(c["person_id"]==r["gold_db_person_id"] for c in r["candidates"])))` | `{'gold':20,'passing':5}` · `13` · `13` |

R1~R23 의 **전체 명령 원문과 실행 출력**은 `docs/wiki/packages/P4-pilot-eval/evidence/20260922-1354-u8-failure-cases.txt` PART 4 에 있다.

---

## 12. 결론

- 게이트는 `reports/metrics.json.gate` 대로 **미달**이다 — `T_merge` = 0.8 에서 `embedding_only` 가 제안 방식을 지배한다(오병합 0 < 1, 미검출 동률 1).
- 제안 방식의 오류 2건은 모두 **2단계 규칙 필터가 정답 후보를 배제**한 데서 나왔고, 마찰 79건 중 52건은 **4단계가 재지 못한 규칙 신호를 0 점으로 합산**해 확신도 상한이 0.80 에 묶인 데서 나왔다. 1단계 후보 검색과 3단계 LLM 판정은 이 실행에서 주된 원인이 아니다.
- 임계치만 조정해서는 통과할 수 없다(절 5). 설계 변경 후보 2개를 절 8 에 올린다 — **결정은 사용자, 절차는 `/devlog change`.**
- **표본 40건이므로 이 문서가 말할 수 있는 것은 방향과 실패 유형까지다.** 비율의 정밀도, 변경안의 효과 확인, 신뢰구간은 P10(150건)의 몫이다.

---

## 13. P4 기준선 대비(P4b 재실행)

> 이 절은 **P4b-er-redesign U6** 의 산출물이다. 위 §1~12 는 손대지 않았다(결정 G(i)) — 그것이 비교 기준선이다.
> 이 절도 §0~12 와 같은 규약을 따른다: **해석만 하고 게이트를 다시 판정하지 않는다.** `pass: true` 는 `reports/metrics.json` 의 `gate` 값을 옮긴 것이고, 최종 판정은 04-review(verifier)가 독립 재계산으로 한다.
> 평가를 다시 돌리지 않았다(결정 E — 실 실행 1회). 네트워크·LLM·DB 호출 0으로 이미 만들어진 파일만 읽었다. 기준선 파일 6개는 읽기 전용으로 열었다.

### 13.0 메타 — 무엇과 무엇을 비교했나

| 항목 | **P4 기준선** | **P4b 재실행** |
|---|---|---|
| 실행 id | `run-29621888da00` | `run-35ae97b5e6ed` |
| 평가한 커밋 (L-001) | `750f11b02f13c942c6d2ef8155646d5b7bc03ac6` (`750f11b`) | **`f96d15b401a24d31bc49de86a1d2c2e11e593999`** (`f96d15b`) |
| 원시 판정 | `reports/pilot/raw-20260922-042440.jsonl.gz`<br>sha256 `8d85e4de…` | `reports/pilot/raw-20260922-150931.jsonl.gz`<br>sha256 `7223e1e5…` |
| trace | `reports/pilot/traces-20260922-042440.jsonl`<br>sha256 `41aa3165…` | `reports/pilot/traces-20260922-150931.jsonl`<br>sha256 `4a8a23ad…` |
| 지표 | `reports/pilot/metrics-20260922-042440.json`<br>sha256 `25e16dd6…`(결정 I 사본) | `reports/metrics.json`<br>sha256 `b293ab50…` |
| `meta.schema_version` | 1 | **2** (meta 2키 + `subsets.penalized_merge`) |
| `meta.weights` | `{llm 0.5, emb 0.3, rule 0.2}` (D3) | `{llm 0.5, emb 0.3, rule 0.2}` (비율 불변, D12) |
| `meta.weights_policy` | (키 없음) | **`observed_renormalized(D12)`** |
| `meta.penalized_merge_policy` | (키 없음) | **`ask`** (결정 A(i)·B(i)) |
| 데이터셋 해시 | `sha256:49cd8c4a…` | `sha256:49cd8c4a…` — **같다**(`data/` 무수정) |
| 시나리오·행·격자 | 40건 · 7050행 · `T_merge` 10점 · `T_new` 0.3 | 40건 · 7050행 · 같은 격자 · 같은 `T_new` |
| 공급자·모델 | `openai` · `gpt-4o-mini-2024-07-18` · `text-embedding-3-small` | 같음 |
| 채점 분모 | 골드 135 − `ambiguous` 3 = **132** | 같음 (`mention_counts` 동일) |

**조인 키.** 04-review §6 이 `mention_index` 의 turn 내 비유일을 지적했으므로 **`(scenario_id, turn, mention, mention_kind)`** 로 조인했다. `proposed`·`T_merge` 0.8 의 141행에서 이 키는 양쪽 모두 **141개 전부 유일**이고 교집합도 141(한쪽에만 있는 키 0)이다. (참고: 이 필터에서는 `(scenario_id, mention_kind, mention_index)` 도 우연히 유일했지만, 계획이 지정한 키를 쓴다.)

**`person_id` 는 실행 간 비교 불가.** 평가 러너가 시나리오마다 DB에 인물을 새로 적재하므로 id 대역이 다르다(기준선 `11894~11949`, 재실행 `16213~16268`). 아래 표의 인물 열은 전부 **`display_name`** 이고, 정오 판정은 `person_id == gold_db_person_id` 로 각 실행 안에서 따로 했다.

### 13.1 (a) mention 단위 diff — `proposed`, `T_merge` = 0.8

**변화 유형별 건수 (141 mention 전체)**

| 변화 유형 | 수 |
|---|---:|
| `identity` → `merge` | **49** |
| 완전 동일(결정·인물·확신도 모두) | 45 |
| `merge` 유지 · 확신도만 변동 | 28 |
| `identity` 유지 · 확신도만 변동 | 16 |
| `new_person` → `identity` | 1 (`sc-007` t2) |
| `identity` → `new_person` | 1 (`sc-012` t1) |
| `merge` → `identity` | 1 (`sc-015` t0) |
| **합계** | **141** |

변화가 있는 행 **96** / 그중 결정이 바뀐 행 **52**. 결정이 같은 44행 중 **귀속 인물이 달라진 행은 0건**이다 — 이 재실행에서 "같은 결정으로 다른 사람에게 붙은" 사례는 없었다.

**채점 분류 전이 (골드·non-`ambiguous` 132건)**

| 기준선 → 재실행 | 수 |
|---|---:|
| `deferred` → `merge_correct` | **49** |
| `merge_correct` → `merge_correct` | 47 |
| `deferred` → `deferred` | 29 |
| `new_person_correct` → `new_person_correct` | 4 |
| `deferred` → `new_person_correct` | 1 |
| **`miss` → `deferred`** | **1** (`sc-007` t2 "문실장님") |
| **`false_merge` → `deferred`** | **1** (`sc-015` t0 "부장님") |
| 합계 | 132 |

**오른쪽 아래가 비어 있다는 것이 이 표의 요점이다** — `merge_correct → false_merge`, `deferred → false_merge`, 어떤 칸에서도 `miss` 로 간 행이 0이다. 이번 표본에서 악화된 mention 은 없었다.

**결정이 바뀐 52행 전체** (변화 없는 89행은 싣지 않는다)

| # | mention | 기준선 decision / 인물 / conf | 재실행 decision / 인물 / conf | 변화 유형 | 채점 |
|---|---|---|---|---|---|
| 1 | `sc-002` t4 `"이서연 과장님"` | identity / – / 0.6895 | merge / 이서연 / 0.8619 | identity→merge | deferred → merge_correct |
| 2 | `sc-003` t3 `"유진씨"` | identity / – / 0.7500 | merge / 최유진 / 1.0000 | identity→merge | deferred → merge_correct |
| 3 | `sc-005` t0 `"하윤이"` | identity / – / 0.7500 | merge / 정하윤 / 0.9375 | identity→merge | deferred → merge_correct |
| 4 | `sc-007` t2 `"문실장님"` | new_person / – / 0.0000 | identity / – / 0.5442 | new_person→identity | **miss → deferred** |
| 5 | `sc-009` t1 `"준호"` | identity / – / 0.7500 | merge / 배준호 / 0.9687 | identity→merge | deferred → merge_correct |
| 6 | `sc-010` t1 `"민준이"` | identity / – / 0.7500 | merge / 이민준 / 0.9375 | identity→merge | deferred → merge_correct |
| 7 | `sc-010` t2 `"민준이"` | identity / – / 0.7500 | merge / 이민준 / 0.9375 | identity→merge | deferred → merge_correct |
| 8 | `sc-011` t1 `"최유진"` | identity / – / 0.7500 | merge / 최유진 / 1.0000 | identity→merge | deferred → merge_correct |
| 9 | `sc-012` t0 `"수학쌤"` | identity / – / 0.7500 | merge / 안소미 / 0.9375 | identity→merge | deferred → merge_correct |
| 10 | `sc-012` t1 `"영어쌤"` | identity / – / 0.0000 | new_person / – / 0.2989 | identity→new_person | deferred → new_person_correct |
| 11 | `sc-012` t2 `"안쌤"` | identity / – / 0.7750 | merge / 안소미 / 0.9687 | identity→merge | deferred → merge_correct |
| 12 | `sc-013` t0 `"채원씨"` | identity / – / 0.7750 | merge / 임채원 / 0.9687 | identity→merge | deferred → merge_correct |
| 13 | `sc-013` t1 `"채영이"` | identity / – / 0.7500 | merge / 서채영 / 0.9375 | identity→merge | deferred → merge_correct |
| 14 | `sc-013` t2 `"채영이"` | identity / – / 0.7500 | merge / 서채영 / 0.9375 | identity→merge | deferred → merge_correct |
| 15 | `sc-013` t2 `"채원이"` | identity / – / 0.7280 | merge / 임채원 / 0.9100 | identity→merge | deferred → merge_correct |
| 16 | `sc-014` t2 `"다인이"` | identity / – / 0.7500 | merge / 서다인 / 0.9375 | identity→merge | deferred → merge_correct |
| 17 | `sc-015` t0 `"부장님"` | merge / 한지원 / 0.9500 | identity / – / 0.8167 | merge→identity | **false_merge → deferred** |
| 18 | `sc-015` t0 `"은우"` | identity / – / 0.7500 | merge / 조은우 / 0.9375 | identity→merge | deferred → merge_correct |
| 19 | `sc-015` t2 `"은우"` | identity / – / 0.7500 | merge / 조은우 / 0.9687 | identity→merge | deferred → merge_correct |
| 20 | `sc-016` t0 `"예린이"` | identity / – / 0.7193 | merge / 신예린 / 0.8991 | identity→merge | deferred → merge_correct |
| 21 | `sc-016` t1 `"예리니"` | identity / – / 0.7750 | merge / 신예린 / 0.9375 | identity→merge | deferred → merge_correct |
| 22 | `sc-016` t2 `"린이"` | identity / – / 0.7500 | merge / 신예린 / 0.9687 | identity→merge | deferred → merge_correct |
| 23 | `sc-017` t0 `"규진이"` | identity / – / 0.7750 | merge / 남규진 / 0.9687 | identity→merge | deferred → merge_correct |
| 24 | `sc-017` t1 `"규진이"` | identity / – / 0.7750 | merge / 남규진 / 0.9375 | identity→merge | deferred → merge_correct |
| 25 | `sc-017` t3 `"서윤이"` | identity / – / 0.7500 | merge / 백서윤 / 0.9687 | identity→merge | deferred → merge_correct |
| 26 | `sc-018` t0 `"민서 누나"` | identity / – / 0.7750 | merge / 구민서 / 0.9687 | identity→merge | deferred → merge_correct |
| 27 | `sc-018` t1 `"보라"` | identity / – / 0.7750 | merge / 양보라 / 0.9375 | identity→merge | deferred → merge_correct |
| 28 | `sc-019` t0 `"세호"` | identity / – / 0.7750 | merge / 장세호 / 0.9687 | identity→merge | deferred → merge_correct |
| 29 | `sc-019` t0 `"아름이"` | identity / – / 0.7500 | merge / 노아름 / 0.9375 | identity→merge | deferred → merge_correct |
| 30 | `sc-019` t1 `"세호"` | identity / – / 0.7750 | merge / 장세호 / 0.9375 | identity→merge | deferred → merge_correct |
| 31 | `sc-020` t0 `"가은이"` | identity / – / 0.7500 | merge / 홍가은 / 0.9687 | identity→merge | deferred → merge_correct |
| 32 | `sc-021` t0 `"동혁이"` | identity / – / 0.7500 | merge / 표동혁 / 0.9687 | identity→merge | deferred → merge_correct |
| 33 | `sc-021` t1 `"서윤이"` | identity / – / 0.7500 | merge / 백서윤 / 0.9375 | identity→merge | deferred → merge_correct |
| 34 | `sc-021` t3 `"보라"` | identity / – / 0.7750 | merge / 양보라 / 0.9375 | identity→merge | deferred → merge_correct |
| 35 | `sc-022` t0 `"규진이"` | identity / – / 0.7750 | merge / 남규진 / 0.9375 | identity→merge | deferred → merge_correct |
| 36 | `sc-022` t0 `"세호"` | identity / – / 0.7750 | merge / 장세호 / 0.9375 | identity→merge | deferred → merge_correct |
| 37 | `sc-024` t0 `"동혁이"` | identity / – / 0.7500 | merge / 표동혁 / 0.9687 | identity→merge | deferred → merge_correct |
| 38 | `sc-024` t0 `"보라"` | identity / – / 0.7500 | merge / 양보라 / 0.9687 | identity→merge | deferred → merge_correct |
| 39 | `sc-026` t0 `"아름이"` | identity / – / 0.7500 | merge / 노아름 / 0.9375 | identity→merge | deferred → merge_correct |
| 40 | `sc-026` t2 `"아름이"` | identity / – / 0.7750 | merge / 노아름 / 0.9687 | identity→merge | deferred → merge_correct |
| 41 | `sc-027` t0 `"규진이"` | identity / – / 0.7500 | merge / 남규진 / 1.0000 | identity→merge | deferred → merge_correct |
| 42 | `sc-027` t2 `"규진이"` | identity / – / 0.7500 | merge / 남규진 / 0.9375 | identity→merge | deferred → merge_correct |
| 43 | `sc-029` t0 `"보라쌤"` | identity / – / 0.7750 | merge / 양보라 / 0.9375 | identity→merge | deferred → merge_correct |
| 44 | `sc-030` t0 `"하윤이"` | identity / – / 0.7750 | merge / 정하윤 / 0.9687 | identity→merge | deferred → merge_correct |
| 45 | `sc-030` t3 `"하윤이"` | identity / – / 0.7500 | merge / 정하윤 / 0.9687 | identity→merge | deferred → merge_correct |
| 46 | `sc-031` t0 `"서윤이"` | identity / – / 0.7500 | merge / 백서윤 / 0.9687 | identity→merge | deferred → merge_correct |
| 47 | `sc-031` t2 `"서윤이"` | identity / – / 0.7500 | merge / 백서윤 / 0.9375 | identity→merge | deferred → merge_correct |
| 48 | `sc-032` t0 `"지호형"` | identity / – / 0.7500 | merge / 오지호 / 0.9375 | identity→merge | deferred → merge_correct |
| 49 | `sc-033` t0 `"가은이"` | identity / – / 0.7500 | merge / 홍가은 / 0.9375 | identity→merge | deferred → merge_correct |
| 50 | `sc-038` t2 `"다인이"` | identity / – / 0.7500 | merge / 서다인 / 0.9375 | identity→merge | deferred → merge_correct |
| 51 | `sc-040` t0 `"예린이"` | identity / – / 0.7443 | merge / 신예린 / 0.8991 | identity→merge | deferred → merge_correct |
| 52 | `sc-040` t2 `"예린이"` | identity / – / 0.7193 | merge / 신예린 / 0.8991 | identity→merge | deferred → merge_correct |

49행이 같은 모양이다 — **기준선 확신도가 `0.72~0.78`(§4a 가 "임계치 바로 아래"라고 부른 구간)이던 행이 `0.89~1.00` 으로 올라가 `merge` 가 됐고, 49건 전부 귀속 인물이 골드였다.** 나머지 3행(4·10·17)만 성격이 다르다.

### 13.2 (b) 기준선의 오병합 1건·미검출 1건 — 정답 후보가 3단계에 도달했는가

#### `sc-015` t0 `"부장님"` (기준선의 유일한 오병합)

| 항목 | **P4 기준선** | **P4b 재실행** |
|---|---|---|
| 판정 | `merge` → **한지원**(오답) = **`false_merge`** | `identity`(ask_user) = `deferred` |
| 2단계 | `excluded_by = {조은우: relation_tag_conflict}` — **골드 후보가 여기서 사라짐** | `excluded_by = {}` · `penalized_by = {조은우: ["relation_tag_conflict","hierarchy_conflict"]}` |
| 3단계 후보 수 | **1**(한지원만) | **2**(조은우 + 한지원) — 골드가 3단계에 **도달했다** |
| LLM 귀속 | 한지원 (`s_llm` 0.9) | **조은우 = 골드** (`s_llm` 0.9, `llm_attempts` 1) |
| `rule_checked`/`rule_passed` | 3 / 3 (한지원 기준) | 3 / 1 (조은우 기준) |
| 확신도 분해 | `0.5·0.9 + 0.3·1.0 + 0.2·1.0 = 0.9500` | `0.5·0.9 + 0.3·1.0 + 0.2·0.3333 = 0.8167` (`weights_effective` = 설정값 그대로, `rule_checked`>0) |
| 밴드 | `band_by_threshold = merge` → `merge` | `band_by_threshold = merge` → **`forced_reason = "penalized_candidate"`** → `identity` |

후보별 신호(재실행): 조은우 `s_emb` 1.0 · `exact_alias` 1.0 · `rule_checked` 3 / `rule_passed` 1 · `s_rule` 0.3333 · `relaxed_pass` 0 · `passed_rules` **1**(= 배제되지 않음) / 한지원 `s_emb` 1.0 · `rule_checked` 3 / `rule_passed` 3 · `s_rule` 1.0.

**읽는 법.** ② (D13)가 §8 이 예상한 대로 동작했다 — 골드 후보가 목록에 남아 3단계 LLM 이 두 후보를 **비교**했고, LLM 은 이번에 골드를 골랐다. 확신도 0.8167 은 `T_merge` 0.8 을 넘지만(`band_by_threshold = merge`) 귀속 후보가 감점 후보라서 **결정 A(i) 의 보수 강등이 `identity` 로 내렸다.** 즉 이 mention 은 *오병합이 정답 병합으로* 바뀐 것이 아니라 *오병합이 되묻기로* 바뀌었다. 원칙1(오병합 ≫ 미검출) 기준으로는 개선이고, 마찰 축으로는 1건이 남는다. 다섯 방식 전체로 보면 기준선에서 "제안 방식만 확신했다"(§1)는 상황이 사라져 **다섯 방식이 모두 `identity`** 가 됐다.

#### `sc-007` t2 `"문실장님"` (기준선의 유일한 미검출)

| 항목 | **P4 기준선** | **P4b 재실행** |
|---|---|---|
| 판정 | `new_person`(단정) = **`miss`** | `identity`(ask_user) = `deferred` |
| 2단계 | `excluded_by = {문태현: relation_tag_conflict}` → **통과 후보 0** | `excluded_by = {}` · `penalized_by = {문태현: ["relation_tag_conflict","hierarchy_conflict"]}` |
| 3단계 | `llm_skipped = true`, `llm_attempts = 0` — **LLM 을 부르지 못했다** | `llm_skipped = false`, `llm_attempts = 1` — 골드 후보가 3단계에 **도달했다** |
| LLM 귀속 | – | **문태현 = 골드** (`s_llm` 0.9) |
| `rule_checked`/`rule_passed` | 0 / 0 (강제 경로) | 2 / 0 (검사했으나 전부 충돌) |
| 확신도 분해 | 전 신호 0 → `confidence = 0.0` (`forced_reason = "no_candidates"`) | `0.5·0.9 + 0.3·0.31405 + 0.2·0 = 0.5442`, `forced_reason = null` |
| 밴드 | `< T_new 0.3` → `new_person` | `T_new 0.3 ≤ 0.5442 < T_merge 0.8` → `identity` |

**읽는 법.** `rule_checked = 2 · rule_passed = 0` 이므로 **D12 의 재정규화는 여기 적용되지 않는다**(카드 D12 "검사했는데 전부 충돌이면 여전히 `s_rule = 0` 으로 합산") — `weights_effective` 도 설정값 그대로다. 미검출이 풀린 원인은 전적으로 **② (D13)** 다: 후보가 살아남아 `no_candidates` 강제 경로를 타지 않았고, 그래서 "새 사람이다"라고 단정하는 대신 "모르겠으니 묻는다"가 됐다. 낮은 `s_emb`(0.314, 승진 호칭 변경)는 그대로이므로 **`merge_correct` 까지 가지는 못했다.** `llm_single` 은 두 실행 모두 이 mention 을 맞혔다(`merge` → 문태현).

### 13.3 (c) 기준선 `deferred` 79건의 행방

| 재실행 결정 | 수 | 그중 귀속 인물 == 골드 | 재실행 채점 |
|---|---:|---:|---|
| `merge` | **49** | **49 / 49 (100%)** | `merge_correct` 49 |
| `identity` 유지 | **29** | 0 (귀속 없음) | `deferred` 29 |
| `new_person` | **1** | – (골드가 DB 밖) | `new_person_correct` 1 |
| 합계 | 79 | | |

- **`merge` 49건**은 전부 `rule_checked == 0` 이던 mention 이다(49/49). 기준선 확신도는 `0.6895 ~ 0.7750`(전부 `T_merge` 미만), 재실행 확신도는 `0.8619 ~ 1.0000`. §4d 가 "규칙 신호 미측정이 0.2 를 통째로 깎아 0.8 미만"으로 분류한 52건이 이 49건과 겹친다. **오병합은 0건**이다.
- **`identity` 유지 29건**의 구성: `forced_reason` = `no_matched` 15 · `penalized_candidate` 4 · `null` 10. 확신도는 `0.0` 15건, `[0.3, 0.8)` 14건. 이 29건 중 `confidence_breakdown.matched_person_id` 가 골드와 같았던 것은 **16건**(기준선 같은 지표는 11건) — §4e 가 말한 "물었지만 사실 맞았을 건"이 비율로는 남아 있다.
- **`new_person` 1건**은 `sc-012` t1 `"영어쌤"`(확신도 0.2989 < `T_new` 0.3). 골드가 DB 밖 인물이라 `new_person_correct` 다 — 기준선에서는 확신도 0.0 강제로 `identity` 였다.
- 역방향: **재실행의 `deferred` 31건은 이 29건 + `sc-015` + `sc-007`** 로 정확히 설명된다(`forced_reason`: `no_matched` 15 · `penalized_candidate` 5 · `null` 11).

### 13.4 (d) 감점 후보가 `merge` 된 건수 — D13 위험 계측 (두 경로 교차 확인)

D13 이 명시한 위험은 "**후보가 늘어 오병합 기회도 는다**"이다. 두 경로로 따로 세서 같은 수가 나오는지 확인했다.

| 경로 | 값 |
|---|---|
| **경로 1** `reports/metrics.json` → `proposed.by_t_merge["0.8"].subsets.penalized_merge` | `merges` **14** · `false_merge_rate` **0/14** · `relaxed_pass_merges` **14** · `relaxed_pass_false_merge_rate` 0/14 · `reasons` `{hierarchy_conflict: 14}` |
| **경로 2** 원시 JSONL `detail["penalized_by"]` 직접 집계 | `merge` 이면서 **귀속 인물 자신이 감점 후보**인 행 **14** (채점 분모 안 14) · 그중 `false_merge` **0** · `relaxed_pass = 1.0` **14/14** · 사유 `hierarchy_conflict` **14** |
| 교차 결과 | **일치(14 = 14, 오병합 0 = 0).** |

**정의 차이 한 가지를 밝혀 둔다.** 원시 JSONL 에서 "`merge` 행 중 `penalized_by` 가 비어 있지 않은 것"을 후보 아무나 기준으로 세면 **22건**이다. 그중 **귀속된 인물 자신이 감점 후보**인 것이 14건이고, `metrics.json` 의 `penalized_merge` 는 후자를 센다. 나머지 8건은 "감점된 다른 후보가 목록에 있었지만 정상 후보로 병합한" 경우로, D13 위험(감점 후보를 자동 연결)과는 성격이 다르다. 두 수가 다른 것은 불일치가 아니라 **정의 차이**이며, 04-review 가 `penalized_merge` 를 읽을 때 이 정의를 함께 읽어야 한다.

**감점 후보 merge 14건 전체** (전부 `merge_correct`, 전부 `relaxed_pass`)

| 시나리오 | mention | 확신도 | 사유 |
|---|---|---:|---|
| `sc-001` t0 / t1 | `"김팀장"` | 0.9333 / 0.9333 | `hierarchy_conflict` |
| `sc-002` t0 | `"이대리"` | 0.9083 | `hierarchy_conflict` |
| `sc-004` t0 / t1 | `"강팀장님"` / `"윤팀장님"` | 0.8715 / 0.8676 | `hierarchy_conflict` |
| `sc-009` t0 | `"배대리"` | 0.9333 | `hierarchy_conflict` |
| `sc-010` t0 / t3 | `"김팀장"` / `"팀장님"` | 0.9083 / 0.8833 | `hierarchy_conflict` |
| `sc-023` t0 | `"심팀장"` | 0.9083 | `hierarchy_conflict` |
| `sc-028` t0 / t2 | `"심팀장"` | 0.8833 / 0.8833 | `hierarchy_conflict` |
| `sc-035` t1 | `"박과장님"` | 0.8617 | `hierarchy_conflict` |
| `sc-036` t0 / t2 | `"이대리"` | 0.8833 / 0.8833 | `hierarchy_conflict` |

**14건 전부가 `relaxed_pass == True`(인접 위계 1칸 완화 통과, 승진 계열)다.** 즉 결정 A(i)가 자동 연결을 허용한 **예외 경로가 곧 감점 후보 병합 경로 전부**다. 이번 표본에서 그 경로의 오병합은 0이지만, **예외 경로가 위험 경로라는 구조는 그대로 남아 있다**(01-plan 결정 A(i) 의 위험 문장).

**보수 강등(`forced_reason = "penalized_candidate"`) 5건** — 결정 A(i)가 실제로 작동한 자리다.

| 시나리오 | mention | `band_by_threshold` | 확신도 | 귀속 == 골드 | 결과 |
|---|---|---|---:|---|---|
| `sc-002` t1 / t2 | `"박과장님"` | `merge` | 0.8617 | **예** | `deferred` |
| `sc-020` t0 | `"심팀장"` | `merge` | 0.8833 | **예** | `deferred` |
| `sc-033` t2 | `"심팀장"` | `merge` | 0.8833 | **예** | `deferred` |
| `sc-015` t0 | `"부장님"` | `merge` | 0.8167 | **예** | `deferred` |

**5건 모두 귀속 인물이 골드였다.** 보수 분기가 이번 표본에서 막은 것은 오병합 0건이고, 대신 **정답 5건을 되묻기로 바꿨다** — 마찰 31건 중 5건(16%)이 이 정책의 비용이다. 원칙1의 비대칭 비용을 받아들인 결과이며, `ER_PENALIZED_MERGE_POLICY=merge` 로 끄면 이 5건이 `merge_correct` 가 되고 `deferred` 는 26건이 된다(다만 그때 `sc-015` 는 자동 연결되므로 안전 마진도 함께 사라진다 — 40건으로는 어느 쪽이 옳은지 정할 수 없다).

**배제 → 감점 전환의 규모** (D13 "코드에서 지켜야 할 것" 1항이 실 데이터에서 확인된 자리)

| 항목 | 기준선 | 재실행 |
|---|---:|---:|
| `excluded_by` 가 있는 mention | **19** (`relation_tag_conflict` 12 · `hierarchy_conflict` 7) | **3** (`dictionary_conflict` 3 **만**) |
| `penalized_by` 가 있는 mention | (키 없음) | **34 / 141** (후보 단위 사유 `hierarchy_conflict` 33 · `relation_tag_conflict` 12) |
| `forced_reason = no_candidates` | 5 | 4 |
| `forced_reason = no_matched` | 25 | 20 |

### 13.5 (e) `rule_checked == 0` mention 의 확신도 분포 이동 (D12 재정규화 효과)

**먼저 전제 하나를 정정한다.** "기준선 trace 에는 `rule_checked` 키가 없다"는 전제로 이 항목을 받았으나, 실제로는 **있다** — `traces-20260922-042440.jsonl` 의 `proposed` 141건 전부에 `confidence_breakdown.rule_checked` 가 있고(141/141), 원시 JSONL 의 `detail.confidence_breakdown` 도 같다. 기준선에 **없는 키는 `weights_effective`** 다(0/141, 재실행은 141/141). 따라서 우회(추정·역산)가 필요 없었고, `rule_checked` 는 양쪽에서 **직접 읽어** 비교했다. `weights_effective` 는 재실행에만 있으므로 기준선 쪽은 "설정값 `weights` 가 곧 유효 가중치"로 읽었다(D3 산식이 재정규화를 하지 않았으므로 사실과 같다).

**측정 지점 주의.** §4c 의 `100/141` 은 `sweep_index == 0`(= `T_merge` 0.5)에서 센 값이다. 이 절은 게이트 점 `T_merge` = 0.8 에서 센다(러너가 임계치마다 시나리오 상태를 새로 적재해 돌리므로 sweep 마다 값이 다를 수 있다). 다행히 기준선은 두 지점에서 같은 **100/141** 이다. 재실행은 **96/141**.

| 항목 | 기준선 | 재실행 |
|---|---:|---:|
| `rule_checked == 0` 인 mention | **100 / 141** | **96 / 141** |
| 양쪽 모두 0인 mention | 95 | 95 |
| 기준선만 0 (재실행에서 규칙이 측정됨) | 5 | – |
| 재실행만 0 | – | 1 |

기준선에서만 0이던 5건은 전부 **기준선에서 후보가 배제돼 강제 경로(확신도 0)를 타던 mention** 이다 — `sc-002` t1·t2 `"박과장님"`, `sc-007` t2 `"문실장님"`, `sc-020` t0 `"심팀장"`, `sc-033` t2 `"심팀장"`. D13 로 후보가 살아나자 규칙이 실제로 측정됐다. 재실행에서만 0인 1건은 `sc-036` t2 `"임대리"`(양쪽 모두 `deferred`).

**양쪽 모두 `rule_checked == 0` 인 95 mention 의 확신도 구간**

| 구간 | 기준선 | 재실행 |
|---|---:|---:|
| `0.000` (강제 경로) | 27 | 25 |
| `(0, 0.3)` | 0 | 1 |
| `[0.3, 0.5)` | 2 | 0 |
| `[0.5, 0.7)` | 4 | 5 |
| **`[0.7, 0.8)`** | **48** | **1** |
| `[0.8, 0.9)` | 14 | 4 |
| **`[0.9, 1.0]`** | **0** | **59** |

- 중앙값 `0.7500 → 0.9375`, 평균 `0.5349 → 0.6756`, **`≥ 0.8` 건수 `14 → 63`**.
- **`rule_checked == 0` 일 때의 확신도 상한이 `0.800 → 1.000` 으로 풀렸다** (§4c 가 "구조적 상한 0.80"이라고 부른 것). `rule_checked > 0` 의 상한은 양쪽 다 1.0 으로 그대로다.
- 재실행의 `rule_checked == 0` 96건은 **전부** `weights_effective = {llm 0.625, emb 0.375, rule 0.0}` 이고, 확신도가 0이 아닌 건 전부 `(0.5·s_llm + 0.3·s_emb) / 0.8` 과 **소수점 오차 없이 일치**(불일치 0건)했다.
- **D12 동치 확인(실 데이터)**: 양쪽 모두 `rule_checked > 0` 인 40 mention 중 세 신호(`s_llm`·`s_emb`·`s_rule`)가 완전히 같은 20건은 **확신도 차이가 정확히 0** 이다. 재정규화는 미측정에만 적용됐다.
- 부분집합 지표도 같은 말을 한다: `subsets.merge_rule_unchecked` 가 **`merges 14 · 오병합 0` → `merges 63 · 오병합 0`**.
- **§8 후보 1의 반사실 대비**: 예측은 "`merge` 48 → 97, 골드 일치 96, 오병합 1건 그대로"였다. 실측은 **`merge` 48 → 96, 골드 일치 96, 오병합 0**. 예측 97 대 실측 96 의 1건 차이는 `sc-015`(반사실은 ①만 적용해 오병합이 남는다고 봤고, 실제로는 ②+보수 강등으로 `identity` 가 됐다)로 설명된다. **저장된 신호를 재합산한 반사실이 실 재실행과 거의 같았다**는 것은 ①(D12)의 효과 추정이 견고했다는 뜻이다.

### 13.6 (f) 게이트 4수치 전후

| 수치 | **P4 기준선** | **P4b 재실행** |
|---|---|---|
| 제안 방식 **오병합률** (`T_merge` 0.8) | **1 / 132 = 0.76%** | **0 / 132 = 0.00%** |
| 제안 방식 **미검출률** | **1 / 132 = 0.76%** | **0 / 132 = 0.00%** |
| `gate.dominated_by` | **`["embedding_only"]`** | **`[]`** |
| `gate.d10_direction` | `true` | `true` (위반 0/9쌍) |
| `gate.pass` | **`false`** | **`true`** (`reason: null`) |

**방식별 (`T_merge` = 0.8, 분모 132)** — 베이스라인 열의 변화 없음에 주목.

| 방식 | 오병합 | 미검출 | identity 보류 | f1 |
|---|---|---|---|---|
| `proposed` | **1 → 0** | **1 → 0** | 79 → **31** | 0.566 → **0.897** |
| `exact_raw` | 0 → 0 | 33 → 33 | 2 → 2 | 0.826 → 0.826 |
| `exact_norm` | 4 → 4 | 20 → 20 | 6 → 6 | 0.854 → 0.854 |
| `embedding_only` | 0 → 0 | 1 → 1 | 31 → 31 | 0.892 → 0.892 |
| `llm_single` | 0 → 0 | **10 → 9** | 19 → 20 | 0.865 → 0.865 |

- **지배가 풀린 것은 베이스라인이 나빠져서가 아니다.** `exact_raw`·`exact_norm`·`embedding_only` 는 141 mention 중 **결정이 바뀐 것이 한 건도 없다**(0 / 0 / 0). `embedding_only` 는 여전히 오병합 0 · 미검출 1 이며, 제안 방식이 **두 축 모두에서 그것보다 낮아져**(0 < 1) 지배 조건이 성립하지 않게 됐다. `llm_single` 만 1건 바뀌었고(`sc-002` t3 `"과장님"`, `miss → deferred`) 그것은 LLM 재호출 변동이다.
- **되묻기**: `ask_user_rate_by_kind.identity` **79/132 (59.8%) → 31/132 (23.5%)** — `embedding_only` 와 정확히 같은 수치가 됐다. `new_person` 은 5/132 (3.8%) 로 양쪽 동일, `schedule` 0. `expected_ask_user.allowed` 준수율 **97/132 (73.5%) → 117/132 (88.6%)**. `passing` 오탐 축은 양쪽 모두 **0/6**.
- **`T_merge` 격자 단조성(R3)** — 산식이 바뀌어도 방향은 유지된다.

| `T_merge` | 기준선 오병합 / 미검출 / 보류 | 재실행 오병합 / 미검출 / 보류 |
|---|---|---|
| 0.50 | 6 / 1 / 22 | 4 / 0 / 22 |
| 0.55 | 6 / 1 / 22 | 4 / 0 / 23 |
| 0.60 | 6 / 1 / 22 | 4 / 0 / 23 |
| 0.65 | 6 / 1 / 23 | 3 / 0 / 25 |
| 0.70 | 4 / 1 / 27 | 3 / 0 / 26 |
| 0.75 | 2 / 1 / 33 | 1 / 0 / 29 |
| **0.80** | **1 / 1 / 79** | **0 / 0 / 31** |
| 0.85 | 1 / 1 / 96 | 0 / 0 / 34 |
| 0.90 | 1 / 1 / 105 | 0 / 0 / 46 |
| 0.95 | 1 / 1 / 114 | 0 / 0 / 86 |

기준선은 0.75 → 0.80 에서 보류가 33 → 79 로 튀었다(구조적 상한 0.80 에 47건이 걸려 있었다). 재실행은 그 절벽이 사라져 보류가 완만하게 오른다(29 → 31 → 34 → 46 → 86). **오병합은 `T_merge` 가 오를수록 단조 감소하고 보류는 단조 증가한다 — R3 방향이 양쪽 실행에서 모두 성립한다.** 운영값 확정은 P10(150건)의 몫이고 이 절은 방향만 확인한다.

- **카테고리별** (분모: promotion 28 · pronoun 31 · alias 33 · normal 21 · new_person 19)

| 카테고리 | 오병합 | 미검출 | identity 보류 |
|---|---|---|---|
| `promotion` | 0 → 0 | **1 → 0** | 12 → 10 |
| `pronoun` | 0 → 0 | 0 → 0 | **25 → 9** |
| `alias` | **1 → 0** | 0 → 0 | **21 → 5** |
| `normal` | 0 → 0 | 0 → 0 | **12 → 1** |
| `new_person` | 0 → 0 | 0 → 0 | 9 → 6 |

마찰이 가장 크게 준 곳은 `pronoun`(지시대명사)·`normal`·`alias` 다 — 힌트가 나오지 않아 `rule_checked = 0` 이 되기 쉬운 범주와 일치한다(§4c).

### 13.7 이 비교가 말하지 않는 것 (한계 — §10 에 이어서)

- **표본 40 시나리오 · 채점 mention 132 다. 이 절이 말할 수 있는 것은 방향과 실패 유형까지다**(P1 인계 15, §10 첫 줄과 같은 한계). 오병합 1건이 0.76%p 를 움직이므로 "0/132" 와 "1/132" 의 차이를 비율로 해석하면 안 된다.
- **"40건에서 오병합이 안 났다"는 안전의 증명이 아니다.** D13 은 3단계에 가는 후보를 늘렸고(배제 mention 19 → 3, 감점 mention 34), 그만큼 오병합 기회도 늘었다. 이번 표본에서 그 위험을 감싼 것은 보수 강등 5건과 "감점 후보 merge 14건이 전부 `relaxed_pass` 예외 경로"라는 사실인데, **예외 경로가 곧 위험 경로**이므로 P10(150건)에서 이 부분집합을 다시 계측해야 한다(01-plan 리스크 "② 는 40건으로 검증할 수 없다").
- **두 실행의 차이가 전부 D12·D13 때문은 아니다.** 양쪽에서 LLM 을 실제로 부른 136 mention 중 **60건에서 `s_llm` 자기보고 값이 달랐다**(변화량 대부분 ±0.05·±0.1, 강제 경로가 바뀌며 ±0.7~0.9 로 크게 움직인 6건 포함). `llm_single` 베이스라인도 1건 판정이 바뀌었다 — **같은 모델을 같은 프롬프트로 다시 불러도 자기보고 점수는 흔들린다.** 따라서 mention 단위 diff 는 "D12·D13 효과 + 실행 간 변동"의 합이며, 40건에서 이 둘을 분해할 수 없다. 반사실(§8 후보 1)과 실측이 1건 차이로 맞았다는 것이 D12 기여의 간접 근거일 뿐이다. `s_emb` 이 달라진 5건 중 눈에 띄는 1건(`sc-002` t3 `"과장님"` 0.2849 → 0.4244)은 임베딩 비결정성이 아니라 **앞선 턴의 병합 결과가 달라 별칭 집합이 달라진** 상태 차이다.
- **`sc-015`·`sc-007` 은 "고쳐졌다"기보다 "안전한 쪽으로 옮겨졌다".** 둘 다 `merge_correct` 가 아니라 `deferred`(되묻기)다. 수용 기준은 "오병합·미검출이 아님"을 요구하고 그 조건은 충족하지만, **정확히 맞힌 것은 아니다**.
- **보수 강등 5건은 전부 정답이었다.** 이 정책은 이번 표본에서 오병합 0건을 막았고 정답 5건을 되묻기로 바꿨다. 이득과 비용의 균형은 40건으로 판정할 수 없다.
- **공급자 1벌·`reason` 원문 없음**은 §10 그대로다. 제안 방식 `detail` 에는 여전히 LLM `reason` 이 남지 않으므로(security §1) "LLM 이 왜 `sc-015` 에서 이번에는 조은우를 골랐는가"는 이 산출물로 재현할 수 없다.
- **이 절은 게이트를 판정하지 않는다.** `pass: true` 는 `reports/metrics.json.gate` 의 값이며, 결정 K (a) 식에 따른 판정과 독립 재계산은 04-review(verifier)의 몫이다(결정 F(i)).

### 13.8 결론

- **게이트 4수치는 `0.8 / [] / true / true` 로 바뀌었다**(기준선 `0.8 / ["embedding_only"] / true / false`). 지배가 풀린 이유는 베이스라인이 나빠져서가 아니라 — 세 베이스라인은 결정이 한 건도 바뀌지 않았다 — 제안 방식의 오병합·미검출이 각각 1 → 0 으로 내려갔기 때문이다.
- **§8 이 2단계·4단계로 귀속했던 두 가지가 각각 대응된다.** ② D13(감점)이 `sc-015`(오병합)·`sc-007`(미검출) 두 건에서 **정답 후보를 3단계에 도달시켰고**, ① D12(재정규화)가 `rule_checked = 0` 의 구조적 상한 0.80 을 풀어 **마찰 79 → 31** 을 만들었다(기준선 `deferred` 79 중 49건이 골드로 자동 연결, 오병합 0).
- **그러나 이것은 40건의 결과다.** 방향(오병합↓·마찰↓·미검출↓)과 유형(2단계가 정답을 지우던 실패, 4단계가 임계치 바로 아래에 몰리던 마찰)까지가 말할 수 있는 전부다. 비율의 정밀도·신뢰구간·D13 이 새로 만든 오병합 기회의 크기는 **P10(150건)** 에서 다시 잰다.
- **실패 케이스는 사라지지 않고 모양이 바뀌었다**: 되묻기 31건(그중 정답을 이미 알고 있던 것 16건 + 보수 강등 5건), 감점 후보 자동 연결 14건(전부 승진 완화 예외 경로). 이 세 덩어리가 P10 이 이어받을 관찰 대상이다.

### 13.9 재현 (§11 과 같은 규약)

전제: 저장소 루트, `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`. 네트워크·DB·LLM 0.

```python
import gzip,json,sys;sys.path.insert(0,".");from collections import Counter
from evaluation.metrics import classify_gold_row
L=lambda p:[json.loads(l) for l in gzip.open(p,"rt",encoding="utf-8")]
RB,RN=L("reports/pilot/raw-20260922-042440.jsonl.gz"),L("reports/pilot/raw-20260922-150931.jsonl.gz")
K=lambda r:(r["scenario_id"],r["turn"],r["mention"],r["mention_kind"])        # 결정 G 조인 키
P=lambda R:{K(r):r for r in R if r["method"]=="proposed" and r["t_merge"]==0.8}
PB,PN=P(RB),P(RN)
```

| # | 무엇을 세나 | 기대 출력 |
|---|---|---|
| S1 | 게이트 전후 | `0.8 ['embedding_only'] True False` / `0.8 [] True True` |
| S2 | 변화 유형 | `identity→merge 49`, 완전 동일 45, `merge` 확신도만 28, `identity` 확신도만 16, 나머지 1+1+1 |
| S3 | 채점 전이 | `deferred→merge_correct 49`, `merge_correct→merge_correct 47`, `deferred→deferred 29`, `false_merge→deferred 1`, `miss→deferred 1`, … 합계 132 |
| S4 | 두 시나리오 | `sc-015` t0 = `identity`/`penalized_candidate`, `sc-007` t2 = `identity`/`forced_reason None` |
| S5 | deferred 79 행방 | `{'merge':49,'identity':29,'new_person':1}`, merge 49 전부 귀속==골드 |
| S6 | 감점 merge 교차 | `subsets.penalized_merge.merges = 14` == 원시 집계 14, 오병합 0 == 0 |
| S7 | `rule_checked==0` | base 100/141 · new 96/141, 공통 95건 `≥0.8` 14 → 63, 상한 0.800 → 1.000 |
| S8 | 비결정성 | 양쪽 LLM 호출 136건 중 `s_llm` 상이 60건, 베이스라인 3종 결정 변화 0 |

전체 명령 원문과 실행 출력은 **`docs/wiki/packages/P4b-er-redesign/evidence/20260923-0039-u6-compare.txt`** 에 있다(PART 0 입력 sha256 / PART 1 (a)~(f) / PART 2 세부 / PART 3 게이트 점 재집계·비결정성).
