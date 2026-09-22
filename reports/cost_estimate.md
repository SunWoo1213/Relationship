# LLM 비용 실측·추정 (P4-pilot-eval U6 / backlog 15행 P0-cost 흡수)

> backlog 수용 기준(문장 그대로): **"시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정"**
>
> 이 문서의 표는 **5방식**(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`) 기준이다 — P3-baselines 에서 완전일치가 `exact_raw`/`exact_norm` 두 변형으로 등록되어 방식이 4개가 아니라 5개다. 비용이 드는 방식은 그중 LLM 을 부르는 둘(`proposed`·`llm_single`)뿐이고 나머지 셋은 LLM 호출 0 이다(임베딩만 쓴다).

- 산출 도구: `scripts/run_pilot_eval.py`(U6). 이 문서의 수치는 `--dry-run --stub --estimate-only` / `--dry-run --stub` 출력에서 그대로 옮긴 것이다.
- 평가한 커밋: `dd6a996`(U5까지) + 이 문서를 만든 U6 = `0283ac0`. **U7 실 실행 커밋(`meta.commit`) = `750f11b`**(L-001, 원칙8).
- 데이터셋 지문(`dataset_hash`): `sha256:49cd8c4a1079e36ac1f2a7999a79f5ef36149441f8c5f528024f749a72eb899e` (`data/scenarios/*.json` 전부, 파일명+내용 sha256).
- 재현 명령:
  ```bash
  POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --dry-run --stub --estimate-only
  ```

## 1. 호출 수 (파일럿 40건, 확정)

결정 C(i) 때문에 **LLM 은 mention 당 방식별 1회**다 — 임계치 10점은 같은 응답을 재사용한다(그래서 "× 10임계치"가 비용을 10배로 만들지 않는다).

| 항목 | 값 | 출처 |
|------|----|------|
| 시나리오 | 40 | `data/scenarios/manifest.json` |
| mention(골드 + `passing_mentions`) | 141 | dry-run `[estimate] mentions=141` |
| LLM 호출 상한 (`proposed` 141 + `llm_single` 141) | 282 | `[estimate] llm_calls total=282` |
| LLM 호출 실제(스텁 실행 실측) | 277 | 전량 dry-run `[run] stub_llm_calls=277` — 통과 후보가 0인 mention 5건은 `proposed` 가 LLM 을 건너뛴다(`llm.skipped`) |
| 임베딩 텍스트(중복 제거 후) | 125 | `[estimate] embed_texts=125` — 별칭 + mention 표면형, 러너의 기억 래퍼가 문자열 단위로 중복을 없앤다 |
| 임베딩 배치 호출(스텁 실행 실측) | 62 | `[run] stub_embed_calls=62` |
| 행 수(= mention × 5방식 × 10임계치) | 7050 | 전량 dry-run `[rows] rows=7050` |

## 2. 토큰·비용 추정 (40건, **추정 — 실측 아님**)

프롬프트 문자 수는 지어낸 상수가 아니라 실제 프롬프트 빌더(`evaluation.resolvers.llm_single.build_prompt`, `app.er.judge.build_prompt`)를 라벨 사전 상태로 호출해 센 값이다. 문자→토큰과 출력 토큰은 **가정값**이다.

| 항목 | 값 |
|------|----|
| 입력 토큰(추정) | 120,100 |
| 출력 토큰(추정) | 22,560 |
| 임베딩 토큰(추정) | 244 |
| 비용(추정) | **$0.0316** (in $0.0180 + out $0.0135 + embed $0.0000) |
| 가정 | `chars_per_token = 1.5`, `output_tokens_per_call = 80` |
| 단가 | in $0.15 / out $0.60 / embed $0.02 (per 1M) |
| 단가 출처 | OpenAI 공개 가격표의 `gpt-4o-mini`·`text-embedding-3-small` 기록값 — **저장소에 적어 둔 오프라인 상수**이며 이 실행은 가격표를 조회하지 않았다. 실행자가 현재가를 확인해 `--price-in`/`--price-out`/`--price-embed` 로 덮어쓴다 |
| 비용 상한 가드 | `--max-cost-usd` 기본 **$5**(결정 B — AWS Budgets $10 알림의 절반). 넘으면 한 줄도 실행하지 않고 rc=3 |

`proposed` 는 후보(≤ `top_k`)만, `llm_single` 은 사전 상태 **전 인물**을 프롬프트에 넣으므로 같은 mention 이라도 `llm_single` 쪽 프롬프트가 길다(P3-baselines 인계 12).

## 3. 시나리오 1건당 토큰 **실측** — U7 직후 채움

| 항목 | 값 | 상태 |
|------|----|------|
| 1건당 입력 토큰(실측) | **3,256** (= 130,240 ÷ 40) | 실측 2026-09-22 |
| 1건당 출력 토큰(실측) | **315.4** (= 12,617 ÷ 40) | 실측 2026-09-22 |
| 40건 실행 총 토큰(실측) | 입력 **130,240** · 출력 **12,617** (`[run] tokens_in=130240 tokens_out=12617`, `llm_fresh_call` 행만). 방식별: `proposed` 136회 60,266/5,656 · `llm_single` 141회 69,974/6,961 (`metrics.json` `<method>.llm`). 임베딩 배치 호출 62회(= `network_calls` 339 − LLM 277); 임베딩 토큰은 사용량 API 미조회로 **실측 없음** | 실측 2026-09-22 |
| 40건 실행 총액(실측 토큰 × 단가 상수, USD) | **$0.0271** (in 130,240 × $0.15/1M = $0.0195 + out 12,617 × $0.60/1M = $0.0076; 임베딩 제외). 단가는 §2 의 오프라인 상수 그대로 — 실행자가 `--price-*` 를 넘기지 않았다(추정 $0.0316 대비 −14%: 입력 +8%, 출력 −44%) | 실측 2026-09-22 |
| 공급자·모델 | `openai` · `gpt-4o-mini-2024-07-18` · 임베딩 `text-embedding-3-small` · `run_mode=real` · `commit=750f11b` (`meta.provider`·`meta.model`·`meta.embedding_model`) | 실측 2026-09-22 |

출처: `docs/wiki/packages/P4-pilot-eval/evidence/20260922-1324-u7-real-run.txt`(실행 표준출력), `reports/metrics.json`. LLM 오류 0건(`error_calls=0` 양쪽), 재시도 없음 → 호출 수 = 상한 282 − `proposed` 건너뜀 5 = 277.

채우는 방법(값을 지어내지 않는다 — 원칙8):

1. U7 실 실행(`python scripts/run_pilot_eval.py --out reports/pilot/ …`)의 표준출력 `[run] tokens_in=… tokens_out=…` 를 그대로 옮긴다. 이 합계는 `llm_fresh_call == true` 행만 더한 값이다(임계치 사본 9행은 같은 응답이라 세지 않는다).
2. 1건당 = 합계 ÷ 40(시나리오 수). `reports/pilot/raw-<ts>.jsonl` 로 재계산할 수 있다.
3. 총액 = 실측 토큰 × 그날 확인한 단가(명령줄에 넣은 `--price-*` 값을 함께 적는다).

## 4. 150건 외삽 총액 (5방식 × 10임계치) — U7 직후 채움

| 항목 | 값 | 상태 |
|------|----|------|
| 150건 입력 토큰(외삽) | **488,400** (= 130,240 × 3.75) | 외삽 2026-09-22 |
| 150건 출력 토큰(외삽) | **47,314** (= 12,617 × 3.75) | 외삽 2026-09-22 |
| 150건 × 5방식 × 10임계치 총액(외삽, USD) | **≈ $0.10** (= $0.0271 × 3.75 = $0.1016, 단가 상수 기준, 임베딩 제외 — 임베딩은 40건에서 $0.0000 자리) | 외삽 2026-09-22 |

외삽 방법(고정):

- 40건 실측 토큰 × (150 ÷ 40) = 3.75배. mention 밀도가 40건 표본과 같다고 가정하며, **이 가정을 결과와 함께 적는다**.
- "× 10임계치"는 곱하지 않는다 — 결정 C(i) 로 임계치는 같은 응답을 재사용한다. 방식 축도 이미 호출 수 안에 들어 있다(LLM 을 부르는 방식은 5 중 2).
- 임베딩은 별칭 + mention 표면형 수에 비례하며 같은 3.75배를 쓴다.

실측 기반: 40건 $0.0271 × 3.75 ≈ **$0.10**(위 표). §2 의 가정 기반 추정($0.0316 × 3.75 ≈ $0.12)은 실측보다 14% 높았다 — 출력 토큰 가정(80/호출)이 실측(약 45.5/호출)보다 컸기 때문이다. 가정: 150건의 mention 밀도·프롬프트 길이가 40건 표본과 같다. P10 이 150건을 돌리면 이 표를 실측으로 교체한다.

## 5. 한계

- §2 의 토큰은 가정(`chars_per_token`·`output_tokens_per_call`) 위에 있다. 공급자의 토크나이저는 한국어를 다르게 쪼갤 수 있다.
- 단가는 오프라인 상수다(네트워크 미조회). 실행 전 확인은 사용자 몫이며 `docs/user-setup/10-pilot-eval-run.md` 가 그 절차를 담는다.
- `llm_error`(타임아웃·레이트리밋)로 재시도가 붙으면 실제 호출 수가 상한을 넘을 수 있다 — `app/er/judge.py` 의 재시도는 1회로 제한돼 있다.

## 5. P4b 재실행 실측 (2026-09-23, `commit=f96d15b`) — §3·§4 는 P4 기준선이며 고치지 않는다

> P4b-er-redesign U5 가 D12·D13 이후 같은 40건을 **한 번 더** 돌린 결과다. 방식·모델·단가 상수는
> P4 와 같고 바뀐 것은 확신도 결합 산식(D12)과 규칙 필터의 감점 전환(D13)뿐이다. 두 실행을 나란히
> 두려고 §3·§4 의 P4 수치는 한 글자도 고치지 않았다(원칙8 — 기준선은 덮지 않는다).

| 항목 | P4b 재실행(실측) | P4 기준선(§3) | 차이 |
|---|---|---|---|
| 40건 총 입력 토큰 | **132,017** | 130,240 | +1,777 (+1.4%) |
| 40건 총 출력 토큰 | **12,681** | 12,617 | +64 (+0.5%) |
| 1건당 입력 토큰 | **3,300.4** | 3,256.0 | +44.4 |
| 1건당 출력 토큰 | **317.0** | 315.4 | +1.6 |
| 40건 총액(실측 토큰 × 같은 단가 상수) | **$0.0274** (in $0.0198 + out $0.0076) | $0.0271 | +$0.0003 |
| 150건 외삽(× 3.75) | **$0.103** | $0.102 | +$0.001 |
| LLM 호출(네트워크) | `proposed` 137 + `llm_single` 141 = **278** | 277 | +1 |
| 임베딩 배치 호출 | **62** (= `network_calls` 340 − 278) | 62 | 0 |
| 건너뛴 mention | `proposed` **4** (통과 후보 0) | 5 | −1 |
| 오류 호출 | **0** (`errors: {}`) | 0 | 0 |

출처: 실행 표준출력 `[run] tokens_in=132017 tokens_out=12681`(`llm_fresh_call` 행만)·
`[run] network_calls=340`, `reports/metrics.json` 의 `<method>.llm`, evidence
`docs/wiki/packages/P4b-er-redesign/evidence/20260923-0009-u5-real-run.txt`.
단가는 §2 의 오프라인 상수 그대로이며 실행자가 `--price-*` 를 넘기지 않았다. 상한은 `--max-cost-usd 5`.

**읽는 법**: 비용은 사실상 그대로다(+1%). D13 이 규칙 필터에서 후보를 배제하지 않게 되면서 3단계
LLM 판정까지 가는 mention 이 하나 늘었고(건너뛴 mention 5 → 4), 후보가 늘어 프롬프트가 조금 길어졌다.
**D12·D13 의 대가는 비용이 아니라 후보 증가에 따른 오병합 위험**이며 그것은 `metrics.json` 의
`subsets.penalized_merge` 가 센다(이 실행에서는 감점 후보 merge 14건·전부 완화 통과 예외·오병합 0).
