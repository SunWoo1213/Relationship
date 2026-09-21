# LLM 비용 실측·추정 (P4-pilot-eval U6 / backlog 15행 P0-cost 흡수)

> backlog 수용 기준(문장 그대로): **"시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정"**
>
> 이 문서의 표는 **5방식**(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`) 기준이다 — P3-baselines 에서 완전일치가 `exact_raw`/`exact_norm` 두 변형으로 등록되어 방식이 4개가 아니라 5개다. 비용이 드는 방식은 그중 LLM 을 부르는 둘(`proposed`·`llm_single`)뿐이고 나머지 셋은 LLM 호출 0 이다(임베딩만 쓴다).

- 산출 도구: `scripts/run_pilot_eval.py`(U6). 이 문서의 수치는 `--dry-run --stub --estimate-only` / `--dry-run --stub` 출력에서 그대로 옮긴 것이다.
- 평가한 커밋: `dd6a996`(U5까지) + 이 문서를 만든 U6 작업 트리. **U6 커밋 해시는 커밋 후 이 줄에 적는다**(L-001, 원칙8).
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
| 1건당 입력 토큰(실측) | — | **U7 직후 채움** |
| 1건당 출력 토큰(실측) | — | **U7 직후 채움** |
| 40건 실행 총 토큰(실측) | — | **U7 직후 채움** |
| 40건 실행 총액(실측, USD) | — | **U7 직후 채움** |
| 공급자·모델 | — | **U7 직후 채움**(`meta.provider`·`meta.model`) |

채우는 방법(값을 지어내지 않는다 — 원칙8):

1. U7 실 실행(`python scripts/run_pilot_eval.py --out reports/pilot/ …`)의 표준출력 `[run] tokens_in=… tokens_out=…` 를 그대로 옮긴다. 이 합계는 `llm_fresh_call == true` 행만 더한 값이다(임계치 사본 9행은 같은 응답이라 세지 않는다).
2. 1건당 = 합계 ÷ 40(시나리오 수). `reports/pilot/raw-<ts>.jsonl` 로 재계산할 수 있다.
3. 총액 = 실측 토큰 × 그날 확인한 단가(명령줄에 넣은 `--price-*` 값을 함께 적는다).

## 4. 150건 외삽 총액 (5방식 × 10임계치) — U7 직후 채움

| 항목 | 값 | 상태 |
|------|----|------|
| 150건 입력 토큰(외삽) | — | **U7 직후 채움** |
| 150건 출력 토큰(외삽) | — | **U7 직후 채움** |
| 150건 × 5방식 × 10임계치 총액(외삽, USD) | — | **U7 직후 채움** |

외삽 방법(고정):

- 40건 실측 토큰 × (150 ÷ 40) = 3.75배. mention 밀도가 40건 표본과 같다고 가정하며, **이 가정을 결과와 함께 적는다**.
- "× 10임계치"는 곱하지 않는다 — 결정 C(i) 로 임계치는 같은 응답을 재사용한다. 방식 축도 이미 호출 수 안에 들어 있다(LLM 을 부르는 방식은 5 중 2).
- 임베딩은 별칭 + mention 표면형 수에 비례하며 같은 3.75배를 쓴다.

현재 추정(가정 토큰)으로만 보면 40건 $0.0316 × 3.75 ≈ **$0.12** 수준이지만, 이 값은 실측이 아니라 §2 의 가정 위에 있는 수이므로 **결정 근거로 쓰지 않는다**. 실측이 나오면 이 문단을 실측 기반 수치로 교체한다.

## 5. 한계

- §2 의 토큰은 가정(`chars_per_token`·`output_tokens_per_call`) 위에 있다. 공급자의 토크나이저는 한국어를 다르게 쪼갤 수 있다.
- 단가는 오프라인 상수다(네트워크 미조회). 실행 전 확인은 사용자 몫이며 `docs/user-setup/10-pilot-eval-run.md` 가 그 절차를 담는다.
- `llm_error`(타임아웃·레이트리밋)로 재시도가 붙으면 실제 호출 수가 상한을 넘을 수 있다 — `app/er/judge.py` 의 재시도는 1회로 제한돼 있다.
