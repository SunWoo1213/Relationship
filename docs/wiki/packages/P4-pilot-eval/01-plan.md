# P4-pilot-eval · 계획 (01-plan)

상태: 초안 | 담당: eval-agent | 작성: 2026-09-11 | 개정: 2026-09-17(verifier 02-plan-verify H-1 → 결정 K 지배 기준, R-1~R-4 반영)
태그 — 패키지: P4-pilot-eval · 닫는 검증: R3 R4 · 기대는 결정: D3 D4 D5 D10 · 구현하는 명세: S3.7 S3.3 · 관련 원칙: 원칙1 원칙2 원칙3 원칙8 원칙9
의존: **P1-pilot-dataset 완료**(`packages/P1-pilot-dataset/04-review.md` `결과: 완료`·승인 2026-09-10, U7 `f78e9dc` / 닫는 커밋 `5cac9bf` — 입력은 `data/scenarios/` 40건·5범주와 `scripts/validate_scenarios.py --strict --json` 의 `counts`·`ambiguous_mention_count`·`trap_count`). **P3-er 완료**(`packages/P3-er/04-review.md` `결과: 완료`·승인 2026-09-06, U9 `b3bcc2d` / 닫는 커밋 `0527ab8` — 평가 대상인 제안 방식 `app.er.resolve()`·`ERConfig`·`agent_traces step='er_resolve'`). **P3-baselines 완료**(`packages/P3-baselines/04-review.md` `결과: 완료`·승인 2026-09-11, U8 `ad394ba` / 닫는 커밋 `5a1bcbe` — 다섯 방식 `RESOLVERS` 와 적재기 `evaluation.scenario_state`). `.claude/gitlog.md`(2026-09-15 16:15) 기준 `dev = main(origin) = 3c6108d`, 승격 대기 0, **`P4-pilot-eval` 태그 커밋 1건**(701fb8d 계획 초안 — 코드 0, 미착수 정상). `docs/backlog.md` 59~61행 P4 행의 의존 문구는 "P3" 이며 충족. **P3-llm-providers 완료**(추가 의존, 사용자 결정 A 2026-09-11 — LLM 공급자 등록표·활성 스위치·Gemini 구현. `packages/P3-llm-providers/04-review.md` `결과: 완료`·승인 2026-09-15, U1 `c01381d`·U2 `cf01e9f`·U3 `7b94a69`·U4 `10a66c3` / 닫는 커밋 `59c67cc` — `JUDGES`·`select_provider`·`judge_from_env`·`caller_from_env` 가 `LLM_PROVIDER=openai` 기본, D11. 실호출 검증 공급자 0/3 은 이 패키지 U6·U7 이 처음 닫는다).
**이 패키지가 P5 이후의 게이트다**(CLAUDE.md·`docs/backlog.md` 7행·INDEX 80행 "P4 이전에 P5 이후를 시작하지 않는다"). 따라서 이 계획의 의존 줄에는 "P4 통과 여부"가 없고, 반대로 P5-loop·P6·P8 의 01-plan 이 이 패키지의 04-review 를 인용하게 된다.

## 목표

S3.7 카드(`docs/resolution-plan.md` §3.7 원문, §5 P4 행)가 요구하는 한 문장 — "**오병합률·미검출률·보정표·곡선 초안**을 내고, 미달이면 재시도가 아니라 실패 케이스 분석 후 §3.3 재설계" — 를 실제 수치로 만든다. P1 이 데이터(40건 골드 라벨)를, P3-er 이 제안 방식을, P3-baselines 가 다섯 방식을 같은 인터페이스로 호출하는 배관을 놓았고, **아무도 아직 재지 않았다**. 이 패키지가 처음으로 (a) 실 임베딩(OpenAI `text-embedding-3-small`, D4 N=1536)·실 LLM 으로 40건 × mention × 5방식 × `T_merge` 스윕을 돌리고, (b) 오병합률과 미검출률을 **분리**해(원칙1 의 비대칭 비용) 계산하고, (c) `s_llm` 자기보고 점수의 구간별 실제 정답률을 `reports/calibration.json` 에 적어 D3 의 "로그확률 없이 자기보고를 쓴다"는 선택을 방어하고(R4), (d) x축 `T_merge` ∈ {0.5,…,0.95}·`T_new` 0.3 고정 곡선으로 D10 의 두 임계치 방향(높이면 오병합↓ 질문↑)을 데이터로 확인한다(R3). 기획서 9장의 방어선("그냥 GPT 부른 거 아니냐")은 여기서 나오는 표 하나로만 성립한다. 동시에 이 패키지는 **게이트**다 — 수치가 나쁘면 그것도 결과이며(원칙8), 데이터·라벨·구현을 손보는 대신 `reports/failure_cases.md` 를 남기고 S3.3 재설계 여부를 사용자 결정으로 올린다.

## 범위

- 포함:
  - **평가 러너 `evaluation/runner.py`** — 시나리오 40건 × 각 시나리오의 mention × 다섯 방식(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`) × `T_merge` 스윕. 시나리오마다 사전 상태를 적재하고 **끝나면 되돌린다**(격리 방식은 결정 D). 호출은 P3-baselines 가 고정한 한 줄뿐이다:
    ```python
    get_resolver(name, **kwargs).resolve_mention(ctx, mention, utterance, hints=None, *, config=ERConfig(t_merge=…))
    ```
    `hints` 는 다섯 방식 모두 `None` 고정(P3-baselines §7 인계 10 — dict 를 주면 `derive_hints` 유도 경로가 죽어 시나리오마다 의미가 달라진다). 적재는 반드시 `evaluation.scenario_state.load_scenario_state(ctx, scenario, embedder=…)` 이고 **`embedder=` 를 명시**하며 `ScenarioState.embedded_alias_count == alias_count` 를 러너가 단언한다(인계 8 — 빠뜨리면 `embedding_only`·`proposed` 가 `embedding_skipped` 로 떨어져 "방식이 나쁜 것"으로 오독된다).
  - **원시 결과 JSONL** — `MentionDecision.to_dict()` 한 줄 = 판정 하나(`method`·`scenario_id`·`turn`·`mention`·`t_merge`·`decision`·`person_id`·`score`·`detail`·`trace_id`·`tokens_*`). **`MentionDecision` 이 단일 출처**이고(P3-baselines 01-plan 171행) `agent_traces` 는 제안 방식의 검증·재계산용 보조다. LLM 응답을 다시 사겠다고 재실행하지 않도록 원시 JSONL 을 먼저 저장하고 지표는 그 파일에서만 계산한다(S3.7 "metrics.json 재사용", 비용).
  - **지표 계산기 `evaluation/metrics.py`** — 오병합률·미검출률·Precision/Recall/F1·`ask_user_rate_by_kind`·강제 사유 분포. 분모 규칙은 P1 이 넘긴 계약 그대로(아래 "인계 항목 대장" 2·3·4·5·6).
  - **보정표 `evaluation/calibration.py` → `reports/calibration.json`** — 자기보고 `s_llm` 0.1 구간(10칸)별 실제 정답률. **공급자·모델별로 나눈다**(P3-er §7: `llm.provider`/`llm.model`/`llm.s_llm`). `detail["score_clamped"] == True` 건은 보정표에서 제외하고 제외 수를 함께 적는다(P3-baselines §6 [권고] 2·§7 인계 11).
  - **트레이드오프 곡선 `evaluation/curve.py`** — x = `T_merge` ∈ {0.5, 0.55, …, 0.95}(10점), `T_new` = 0.3 **고정**, y = 오병합률 · `ask_user(identity)` 발생률 · 미검출률. 다섯 방식 전부 같은 x축(임베딩 단독도 `band_for` 로 같은 두 임계치를 쓴다 — P3-baselines 결정 D(i)). `ERConfig.top_k` 는 **스윕하지 않는다**(결정 H).
  - **리포트 생성기 `evaluation/report.py` → `reports/eval.md` 초안** — 입력은 `reports/metrics.json` **하나뿐**이어야 한다(S3.7·품질체크 "metrics.json 으로 리포트 재생성"). 이것이 P10 수용 기준("`metrics.json`만으로 `eval.md` 재생성")의 선행 구현이다.
  - **실 공급자 1회 실행** — 임베딩 OpenAI `text-embedding-3-small`(D4 확정, N=1536), LLM 은 결정 A. 키는 사용자 셸 환경변수로만 들어가고 저장소·프롬프트·로그·예외에 남지 않는다(security.md §1·§6). 실행 주체는 결정 G.
  - **실패 케이스 분석 `reports/failure_cases.md`** — 오병합·미검출·강제 강등(`forced_reason`)·`llm.error` 건을 유형별로 묶고 각 유형에 원문 mention·후보·`confidence_breakdown` 을 붙인다. **미달이든 아니든 만든다**(원칙8 — 미달일 때만 쓰면 성공 보고서가 된다).
  - **게이트 판정 문단** — 수용 기준 아래 "해석(기계 판정 방법)" 과 결정 K 의 통과 기준으로, 04-review 가 기계적으로 판정할 수 있게 한다.
  - **문서 반영** — `docs/wiki/registry.md` 신규 행, `README.md` 평가 실행법 절, `docs/user-setup/10-pilot-eval-run.md`(사용자가 키 있는 셸에서 실행하는 카드).
- 이 패키지에서 하지 않는 것:
  - **150건 데이터셋·최종 평가·`eval.md` 확정본** — P10-final-eval. 여기서 만드는 `eval.md` 는 **초안**(backlog 54행 "곡선 초안")이다.
  - **운영 임계치 확정** — 40건은 카테고리당 6~10건이라 "방향과 실패 유형"만 본다(P1 §7 인계 11, P3-baselines §7 인계 15). `T_merge`·`T_new`·가중치의 **운영값 확정은 P10**. 이 패키지는 곡선과 "이 방향으로 움직인다"까지.
  - **`app/` 수정** — `app/er/*`·`app/tools/*`·`app/embedding.py` 를 고치지 않는다(원칙4 경계·P3-baselines 선례). 필요해지면 멈춰 사용자 결정으로 올린다. 유일한 후보는 F-251dc2 이며 이 계획은 **고치지 않는 쪽**을 택한다(아래 "05-remediation 소견 — 이 계획의 결정" 과 결정 G).
  - **골드 라벨 수정·재해석** — 수치가 나쁘게 나와도 `data/` 를 손대지 않는다(P1 §7 인계 9·13, 원칙8). 라벨 의심은 FIX 가 아니라 새 검수 기록 + 사용자 결정.
  - **이벤트·일정 추출 F1, 툴 호출 정확도** — 발화에서 이벤트를 뽑는 주체는 에이전트 루프(P5)다. P4 는 **mention 단위 인물 해석만** 잰다. P1 §7 인계 7(클래스별 이벤트 F1 보고)은 **범위 밖**으로 명시하고 P10 으로 그대로 넘긴다(아래 인계 대장 P1 §7 의 7항).
  - **`ERConfig.top_k` 스윕**(F-bdd6c5 — 무효), **가중치(0.5/0.3/0.2) 스윕**(D3 는 설정값이라 했으나 40건으로 튜닝하면 과적합. P10 몫).
  - **프론트·루프·메모리 승격·브리핑**(P5 이후, 게이트 통과 전 금지), **고민 상담·인물 간 관계·감정 대화**(원칙7).

## 산출물 (파일 경로)

- evaluation/runner.py — 시나리오 순회·격리·적재·다섯 방식 × `T_merge` 스윕·JSONL 기록
- evaluation/metrics.py — 분모 규칙·오병합률·미검출률·P/R/F1·`ask_user_rate_by_kind`·강제 사유 집계
- evaluation/calibration.py — `s_llm` 0.1 구간 × 공급자·모델별 정답률(`score_clamped` 제외)
- evaluation/curve.py — `T_merge` 스윕 집계, 곡선 좌표(방식 × x 10점 × y 3계열)
- evaluation/report.py — `reports/metrics.json` 한 파일만 읽어 `reports/eval.md` 생성(멱등)
- scripts/run_pilot_eval.py — CLI 진입점(`--dry-run`/`--stub`·`--methods`·`--t-merge`·`--out`·`--limit`). 키 없으면 종료 코드 2(이름만 안내, `.env` 미독)
- reports/pilot/raw-<ts>.jsonl — 원시 판정(재계산·재현의 입력)
- reports/metrics.json — 원수치(다섯 방식 키 = `RESOLVERS` 이름)
- reports/calibration.json — 보정표
- reports/curve.csv — 곡선 좌표(그림 형식은 결정 J)
- reports/eval.md — 초안(metrics.json 에서 생성)
- reports/failure_cases.md — 실패 유형·표본·원인 가설(원칙8)
- reports/cost_estimate.md — 40건 실측(시나리오 1건당 토큰·방식별 호출 수·실비용) → 150건 × 5방식 × 10임계치 총액 외삽(결정 B(i), backlog 15행 P0-cost 흡수. 본문에 "4방식 → 5방식(`exact_raw`/`exact_norm` 분리)" 한 줄)
- tests/test_eval_runner.py — 격리·적재 단언·`hints=None`·스윕 격자·JSONL 스키마(스텁, 네트워크 0)
- tests/test_eval_metrics.py — 분모 규칙(ambiguous 제외·`passing_mentions` 오탐·ask_user 제3 범주) 전수
- tests/test_eval_calibration.py — 구간 경계·공급자 분할·`score_clamped` 제외
- tests/test_eval_curve.py — x 10점·`T_new` 고정·단조 방향 단언은 하지 않음(데이터가 정한다)
- tests/test_eval_report.py — 같은 metrics.json → 같은 바이트(재생성 멱등)
- docs/user-setup/10-pilot-eval-run.md — 사용자 실행 카드(키·비용 상한·명령·증거 저장 위치)
- docs/wiki/packages/P4-pilot-eval/evidence/ — pytest·dry-run·실 실행·스키마 검증·무변경 diff 출력
- docs/wiki/registry.md — 신규 행(기존 행은 비고만), README.md — 평가 실행법 절

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

- [ ] U1 **러너 골격·격리·적재**: `evaluation/runner.py` — `run_pilot(ctx_factory, scenarios, methods, t_merge_grid, *, embedder, judge=None, out_path) -> RunSummary`. 시나리오마다 (i) 격리 경계 열기(결정 D), (ii) `load_scenario_state(ctx, scenario, embedder=…)` **재사용**(적재기를 다시 만들지 않는다 — registry 124행), (iii) `assert state.embedded_alias_count == state.alias_count`, (iv) mention 순회 × 방식 × `T_merge`, (v) 경계 되돌리기. `hints=None` 고정. 러너가 만드는 env 에 `LLM_PROVIDER=openai` 를 **명시**로 넣고 `LLM_PROVIDERS_ENABLED` 는 넣지 않는다(P3-llm-providers §7 인계 1 — 기본값이 바뀌어도 재현). 결과는 `MentionDecision.to_dict()` + `scenario_id`·`turn`·`t_merge`·`gold_person_id` 를 더한 JSONL 한 줄. `trace_id` 를 그대로 보존해 제안 방식 판정을 `agent_traces WHERE step='er_resolve'` 로 되짚을 수 있게 한다(P3-er §7 재계산 입력 계약 — 결정 D(i) 롤백에서는 **실행 중에 한함**: U7 이 표본을 실행 중에 덤프하고 04-review 는 그 evidence 를 실행 로그와 같은 ts 로 요구한다). `tests/test_eval_runner.py` — 같은 시나리오 2회 실행 후 `persons`/`person_aliases` 행 수 증분 0(두 벌 방지, 인계 9), `hints` 인자가 전 방식에서 `None`(호출 스파이), 스윕 격자 길이 = 10, `embedder=None` 이면 **즉시 실패**(경고가 아니라 오류 — 인계 8) / Refs: P4-pilot-eval S3.7 D5 D10 원칙8 원칙9
- [ ] U2 **지표 계산기**: `evaluation/metrics.py` — 입력은 U1 의 JSONL 만. 분모 규칙: `ambiguous: true` mention 3개(sc-022 t1·sc-024 t4·sc-013 t3) **제외**, `passing_mentions` 6개(sc-038·039·040)는 `create_person`/`ask_user(kind=new_person)` 이 나오면 **오탐 분자**, `ask_user` 로 간 mention 은 오병합에도 미검출에도 넣지 않는 **제3 범주**로 따로 집계. `expected_ask_user.allowed` 는 **허용 집합**으로 채점(단일 정답 아님). 산출: 방식별 `false_merge_rate`·`miss_rate`·`precision`/`recall`/`f1`·`ask_user_rate_by_kind{identity,new_person,schedule}`·`forced_reason` 분포(한 자리 하나)·`llm_error` 분포·부분집합 지표(`rule_checked==0` 인 merge 의 오병합률, `relaxed_retry==true` 인 merge 의 오병합률, `derive_hints` 가 빈 dict 인 mention 비율 — P3-er §7 리스크 계측). `score` 는 방식마다 의미가 다르므로 **같은 축에 놓지 않는다**(인계 14). `tests/test_eval_metrics.py` — 손으로 만든 소형 입력으로 세 분모 규칙·제3 범주·허용 집합 채점을 전수 단언 / Refs: P4-pilot-eval S3.7 D10 원칙1 원칙2 원칙8
  - **해석(결정 L, 사용자 2026-09-18 — 위 문장은 바꾸지 않는다)**: "ask_user 로 간 mention" 의 제3 범주는 `decision=="identity"`(판단을 사람에게 미룸)에 한한다. `new_person`(아는 누구도 아니라는 단정)은 골드와 대조해 `miss`/`new_person_correct` 로 채점한다 — 같은 사람을 새 인물로 잘못 보는 경우가 전부 `new_person` 으로 나가므로 이를 제외하면 미검출률이 구조적으로 0 이 되어 결정 K 의 한 축이 죽는다. 마찰 축 `ask_user_rate_by_kind` 는 `identity`·`new_person` 둘 다 센다(정확도 축과 배타적이지 않음, `meta.denominator_rule.ask_user`). `llm_error` 행은 기본 분모에 남기고(`base.py` 규약 2 — 한 방식만 분모가 줄면 비교가 깨진다) `point.excluding_llm_error` 를 함께 낸다. verifier 04-review 확인 대상.
- [ ] U3 **보정표**: `evaluation/calibration.py` → `reports/calibration.json` — `s_llm` 0.1 구간 10칸 × (`provider`,`model`) 별 `{bin, n, correct, accuracy}`. 대상은 `s_llm` 을 실제로 내는 방식(`proposed`·`llm_single`)뿐이며 방식도 키로 나눈다. 그룹 키 `model` 은 판정이 돌려준 값(`Judgement.model` / `detail["model"]`)을 그대로 쓰고 설정 문자열(`OPENAI_MODEL`)은 `meta.model_configured` 에 따로 적는다(P3-llm-providers §7 인계 4 — Gemini 는 `model_version` 이 설정과 다를 수 있다). `detail["score_clamped"] == True` 는 제외하고 `excluded_clamped` 수를 같은 파일에 적는다([권고] 2). `llm.skipped == true`(통과 후보 0)와 `llm.error`(`timeout/rate_limit/api_error/connection/schema/out_of_range_id`)는 분모에서 빼고 별도 카운트. "정답"의 정의는 그 판정의 `decision`·`person_id` 가 골드와 일치하는가로 한 줄 명시. `tests/test_eval_calibration.py` — 경계값(0.1·0.8·1.0)이 어느 칸인지, 공급자 두 개 섞인 입력이 분리되는지, clamp 제외 / Refs: P4-pilot-eval R4 D3 원칙3 원칙9
- [ ] U4 **곡선·metrics.json 조립**: `evaluation/curve.py` + `metrics.json` 작성기 — x = `T_merge` {0.5,0.55,…,0.95} 10점, `T_new` = 0.3 고정(스윕하지 않는다), y 3계열(오병합률·`ask_user(identity)` 발생률·미검출률) × 다섯 방식. `metrics.json` 최상위 키는 **`RESOLVERS` 이름 문자열 그대로**(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`, 순서 고정 — 인계 4) + `meta{provider, model, embedding_model, dataset_hash, schema_version, run_id, t_new, grid}`. `band_by_threshold` 만 순수 산식 구간이고 `forced_reason != null` 행은 곡선 계열과 별도 집계(P3-er §7). `reports/curve.csv` 동시 출력. **`metrics.json` 최상위 `gate{t_merge:0.8, proposed:{false_merge_rate,miss_rate}, baselines:{name:{false_merge_rate,miss_rate}}, dominated_by:[name…], d10_direction:bool, pass:bool}`** 를 결정 K(지배 기준)로 계산해 넣는다 — `dominated_by` 는 `T_merge=0.8` 에서 오병합률 ≤ 제안 방식 **그리고** 미검출률 ≤ 제안 방식이며 둘 중 하나는 엄격히 < 인 베이스라인 목록, `d10_direction` 은 제안 방식 곡선에서 `T_merge` 최저→최고 사이 오병합률이 증가하지 않고 `ask_user(identity)` 발생률이 감소하지 않음, `pass = (dominated_by == []) and d10_direction`. `tests/test_eval_curve.py` — 격자 10점·`T_new` 불변·방식 키 5개와 순서·`gate` 판정식(동률 4조합·지배 1건·D10 역방향 1건 손 입력) / Refs: P4-pilot-eval R3 D10 S3.7 원칙1 원칙2
- [ ] U5 **리포트 생성기**: `evaluation/report.py` — `python -m evaluation.report --metrics reports/metrics.json --out reports/eval.md`. 입력은 `metrics.json` **하나뿐**(JSONL·DB·네트워크를 읽지 않는다). 표(방식 × 지표), 곡선 표/그림 링크, 운영 최적점 **후보** 한 문단(40건이므로 "방향"이라는 단서를 문장에 박는다), 한계 절. `tests/test_eval_report.py` — 고정 `metrics.json` 픽스처로 두 번 생성해 **바이트 동일**, 입력에 없는 수치를 본문에 쓰지 않는다(템플릿이 키를 참조하지 않으면 실패) / Refs: P4-pilot-eval S3.7 원칙8
- [ ] U6 **실행 CLI·dry-run·비용 가드**: `scripts/run_pilot_eval.py` — `--dry-run --stub`(스텁 판정기·결정적 가짜 임베딩, **네트워크 0**)으로 전 파이프라인을 한 번 돌려 JSONL→metrics→calibration→curve→eval.md 가 이어지는지 증명한다. 실행 전 **예상 호출 수·토큰·비용 추정을 표준출력에 먼저 찍고**(40 시나리오 × mention × (`proposed` 1 + `llm_single` 1) LLM 호출 + 별칭·mention 임베딩; `detail["prompt_chars"]`·`person_count` 가 실측 입력 — 인계 12), `--max-cost-usd` 상한을 넘으면 실행하지 않고 종료(결정 B). 키 없으면 종료 코드 2(이름만 안내, `.env` 미독 — security §1). 사용자 스모크 03(`docs/user-setup/03-er-smoke.md`)·08(`docs/user-setup/08-baseline-smoke.md`) 결과(공급자·모델·`llm_error`)를 이 패키지 evidence 로 옮겨 적는다(인계 13, [권고] 6). **`reports/cost_estimate.md`**(결정 B(i), backlog 15행 "시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정" — 문장은 그대로, 본문에 5방식 기준임을 한 줄): dry-run 의 호출 수 추정과 U7 실측 토큰으로 1건당 토큰·150건 외삽 총액(USD) 두 수치를 적는다(실측 수치는 U7 직후 채움). `docs/user-setup/10-pilot-eval-run.md` 작성 / Refs: P4-pilot-eval D4 원칙8 L-004
- [ ] U7 **실 공급자 1회 실행**: 임베딩 OpenAI `text-embedding-3-small`(N=1536, D4), LLM 결정 A. 산출 `reports/pilot/raw-<ts>.jsonl`·`reports/metrics.json`·`reports/calibration.json`·`reports/curve.csv`·`reports/eval.md`. evidence 에 실행 명령(키 값 없이)·표준출력·소요·실제 토큰 합계·`provider`/`model`/`embedding_model` 을 남긴다(인계 5·13, P1 §7 인계 8 — 판정 모델별 재기록). 제안 방식 표본 일부를 `agent_traces` 로 되짚어 `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule` 재계산 abs diff 0 을 확인(R4·원칙3·원칙9). 실패·오류도 그대로 남긴다(어느 결과든 evidence, 원칙8) / Refs: P4-pilot-eval R4 R9 D3 D4 D5 원칙3 원칙8 원칙9
- [ ] U8 **실패 케이스 분석**: `reports/failure_cases.md` — 오병합 전건(있으면 전부), 미검출 상위 유형, `forced_reason`·`llm_error` 유형, 함정 12건(`by_trap_kind` 7종)에서의 거동, 카테고리별(promotion·pronoun·alias·normal·new_person) 실패 분포. 각 건에 시나리오 id·turn·mention·후보·`confidence_breakdown`·왜 그렇게 판정했는지 한 줄. **결론 문장은 "표본 40건이므로 방향과 유형까지"**(인계 15). 수치가 결정 K 기준에 미달이면 재실행·재시도 대신 여기에 S3.3 재설계 후보(어느 단계가 원인인가)를 적고 `/devlog change` 후보로 사용자에게 올린다. 라벨이 틀렸다고 보이면 `data/` 를 고치지 않고 P1 형식의 새 검수 기록 + 사용자 결정으로 분리한다(인계 9) / Refs: P4-pilot-eval S3.3 S3.7 원칙1 원칙8
- [ ] U9 **수용 기준 기계 검증 + 문서**: 전체 `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs`, dry-run 재실행, `metrics.json`·`calibration.json` 스키마 검증, 곡선 격자 확인, `eval.md` 재생성 멱등 diff 0줄, `git diff --name-only <U1 직전 해시>..HEAD -- app/ data/` **0줄**, `python scripts/validate_scenarios.py --strict --json` rc=0(`total` 40 그대로), `POSTGRES_PORT=5433 python -m alembic check`·`python scripts/tools_check.py` 무변경을 evidence 로 남긴다. `docs/wiki/registry.md` 신규 행(모듈 5·스크립트 1·테스트 5·리포트 산출물), `README.md` "파일럿 평가 실행법" 절(환경변수 **이름**만) / Refs: P4-pilot-eval S3.7 원칙4 원칙8 원칙9

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [eval-agent] **파일럿 평가** (오병합률·미검출률·보정표·곡선 초안) / 의존: P3, P3-llm-providers / 수용기준: `reports/metrics.json`, `reports/calibration.json` 생성. **미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다**

  해석(기계 판정 방법, 위 문장을 바꾸지 않는다):
  - "**파일럿 평가**" → `data/scenarios/` **실물 40건 전부**에 대해 다섯 방식이 돌았다. 판정: `python -c "import json,collections;rows=[json.loads(l) for l in open('reports/pilot/raw-<ts>.jsonl',encoding='utf-8')];print(len({r['scenario_id'] for r in rows}), sorted({r['method'] for r in rows}))"` → `40 ['embedding_only','exact_norm','exact_raw','llm_single','proposed']`. 픽스처·부분 표본이 아니다.
  - "(오병합률·미검출률·…)" → `reports/metrics.json` 의 다섯 방식 키 각각에 `false_merge_rate`·`miss_rate` 가 **분리된 두 값**으로 존재하고 분모 규칙(ambiguous 3건 제외·`passing_mentions` 6건 오탐·ask_user 제3 범주)이 `meta.denominator_rule` 에 기록돼 있다. 판정: U9 스키마 검증 스크립트 rc=0.
  - "(…보정표…)" → `reports/calibration.json` 에 `s_llm` 0.1 구간 **10칸**이 `provider`·`model`·`method` 별로 있고 `excluded_clamped` 수가 적혀 있다. 판정: `python -c "import json;d=json.load(open('reports/calibration.json'));print(sorted({b['bin'] for g in d['groups'] for b in g['bins']}))"` → 10개 구간.
  - "(…곡선 초안)" → `reports/curve.csv` 의 x 값 집합이 `{0.5,0.55,…,0.95}` 10점, 모든 행의 `t_new` 가 `0.3`, y 계열 3개 × 방식 5개. 판정: U9 곡선 격자 확인 명령 출력.
  - "`reports/metrics.json`, `reports/calibration.json` 생성" → 두 파일이 **실 공급자 실행**으로 생겼고 `meta.provider`·`meta.model`·`meta.embedding_model` 이 스텁이 아니다(`stub`/`fake` 문자열 아님). 판정: `python -c "import json;m=json.load(open('reports/metrics.json'))['meta'];print(m['provider'],m['model'],m['embedding_model'],m['run_mode'])"` → `run_mode == "real"`.
  - "**미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다**" → (i) `reports/failure_cases.md` 가 **결과와 무관하게** 존재한다(U8). (ii) 통과/미달 판정은 결정 K 의 기준으로 04-review 가 한 번만 내린다. (iii) 미달이면 같은 설정으로 재실행한 evidence 가 **없어야 한다** — 판정: evidence 디렉터리의 실 실행 파일이 설정(공급자·모델·격자)당 1개이거나, 2개 이상이면 03-log 에 설정 변경 사유가 적혀 있다. (iv) 미달 시 산출물은 `failure_cases.md` + S3.3 재설계 후보 목록이며, S3.3 카드·`app/er/` 를 이 패키지 안에서 고치지 않는다(`git diff -- app/` 0줄). 재설계 착수는 `/devlog change` 와 사용자 결정 이후다.

  **기획서·S3.7 에는 절대 목표 수치가 없다.** `docs/proposal.md` 11행이 부록 A 의 "F1 0.87, 오병합률 3%" 를 **예시이며 측정 결과가 아니라고** 명시했고, S3.7·`resolution-plan.md` §3.7·§5 P4 행에도 임계 수치가 없다(grep 확인). 따라서 "미달"의 기준은 이 계획이 지어내지 않고 **결정 K 로 사용자에게 올린다**(권장안은 절대 수치가 아니라 베이스라인 대비 상대 기준 + 원칙1 방향 — 아래).

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

로컬 컨테이너는 5433 이므로 포트를 셸 변수로 넘긴다(`.env` 는 읽지 않는다, security.md §1).

| 무엇 | 명령 | 기대 출력 |
|------|------|-----------|
| 전체 테스트 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 기존 918(P3-llm-providers done 시점) + 신규 전부 통과, 실패 0·skip 0 |
| dry-run(네트워크 0) | `POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --dry-run --stub --out <tmp>` | rc=0. 5방식 × 10임계치 × mention 행 수 출력, `network_calls=0`·`run_mode=stub` |
| 적재 임베딩 단언 | dry-run 로그 | 시나리오마다 `embedded_alias_count == alias_count`(인계 8). 불일치면 rc≠0 |
| 실 실행 | `LLM_PROVIDER=openai OPENAI_API_KEY=… POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --out reports/pilot/` (결정 A(ii) OpenAI 1벌, 키 값은 사용자 셸에만) | rc=0, `run_mode=real`, 토큰·비용 합계 출력. 키 없으면 rc=2 |
| `metrics.json` 스키마 | `python -m evaluation.metrics --validate reports/metrics.json` | rc=0. 방식 키 5개·순서 고정·`meta.denominator_rule` 존재 |
| 보정표 구간 수 | `python -c "import json;d=json.load(open('reports/calibration.json'));print(len({b['bin'] for g in d['groups'] for b in g['bins']}), d['excluded_clamped'])"` | `10 <정수>` |
| 곡선 파일 | `python -c "import csv;r=list(csv.DictReader(open('reports/curve.csv',encoding='utf-8')));print(sorted({float(x['t_merge']) for x in r}), {x['t_new'] for x in r}, len({x['method'] for x in r}))"` | `[0.5,…,0.95]`(10점) · `{'0.3'}` · `5` |
| `eval.md` 재생성 | `python -m evaluation.report --metrics reports/metrics.json --out <tmp>/eval.md && diff <tmp>/eval.md reports/eval.md` | 출력 0줄(멱등 — P10 수용 기준의 선행 증명) |
| 제품 코드·데이터 무변경 | `git diff --name-only <U1 직전 해시>..HEAD -- app/ data/` | **0줄**(원칙4·원칙8. 0줄이 아니면 이 패키지는 미충족) |
| 라벨 무변경 | `python scripts/validate_scenarios.py --strict --json` | rc=0, `total` 40·5범주 `counts` 그대로 |
| 스키마·툴 무변경 | `POSTGRES_PORT=5433 python -m alembic check` · `python scripts/tools_check.py` | `No new upgrade operations detected.` · `7/7 ok` |
| 확신도 재계산(표본) | U7 evidence 의 `agent_traces step='er_resolve'` 재계산 스크립트(결정 D(i) 롤백이므로 **실행 중 덤프**, 실행 로그와 같은 ts) | `0.5·s_llm+0.3·s_emb+0.2·s_rule` 과 기록 `confidence` 의 abs diff 0 |
| 비용 실측·외삽(P0-cost 흡수, 결정 B) | `grep -nE "1건당|150건" reports/cost_estimate.md` | 시나리오 1건당 토큰 실측 수치와 150건 외삽 총액(USD) 두 수치가 있고 5방식 기준이 명시돼 있다 |
| 게이트(결정 K 지배 기준) | `python -c "import json;g=json.load(open('reports/metrics.json'))['gate'];print(g['t_merge'],g['dominated_by'],g['d10_direction'],g['pass'])"` | `0.8 [] True True` 면 통과. `dominated_by` 가 비어 있지 않거나 `d10_direction` 이 False 면 미달(→ U8 + `/devlog change`) |

- 증거 경로: `docs/wiki/packages/P4-pilot-eval/evidence/`. Docker Desktop 이 꺼져 있거나 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security.md §6).

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| registry 행 | 무엇 | 이 패키지가 어떻게 쓰는가 |
|---|---|---|
| 110~113 `evaluation/__init__.py`·`resolvers/{base,registry,__init__}.py`(05d90f0) | `MentionDecision`·`Resolver`·`RESOLVERS`·`get_resolver`·`ALL_METHODS` | 러너가 `from evaluation.resolvers import ALL_METHODS, get_resolver` 한 줄로 돈다. 새 방식·새 인터페이스를 만들지 않는다. 다섯 이름 = `metrics.json` 키 |
| 115·117·119·121 `proposed.py`·`exact_match.py`·`embedding_only.py`·`llm_single.py` | 다섯 방식 구현 | 그대로 호출만 한다. 수정 0(고칠 일이 생기면 멈춘다) |
| 124 `evaluation/scenario_state.py`(e0812f7) | `load_scenario_state(ctx, scenario, *, embedder=None)` | 사전 상태 적재 **전용 경로**. 새 적재기를 만들지 않는다. `embedder=` 명시 필수 |
| 106 `scripts/validate_scenarios.py`(1e1320c baee71e 40c36f8) | 적재·`--strict --json` 의 `counts`·`ambiguous_mention_count`·`trap_count` | 분모 계약의 출처이자 "라벨 무변경" 증거 명령. `scenario_state` 가 이미 얇게 감쌌으므로 러너는 그 래퍼를 쓴다 |
| 107 `scripts/dump_scenarios.py`(40c36f8…) | 검수 패킷 Markdown 덤프 | 실패 케이스 분석(U8)에서 시나리오 원문을 사람이 읽는 형태로 인용할 때 재사용 |
| 87 `scripts/er_smoke.py`(107ace3) · 123 `scripts/baseline_smoke.py`(0d98e47) | 실 LLM 1회 스모크(사용자 실행) | U6·U7 **전에** 1회 실행해 키·공급자·모델을 확인(결정 I). 결과를 이 패키지 evidence 로 옮긴다 |
| 78~85 `app/er/*`(02e6f14·b1f2782·593c254·d6e5949·cc5d24f) | `resolve`·`ERConfig`·`band_for`·`combine`·`judge_from_env`·trace 상수 | **읽기 전용 재사용**. `ERConfig(t_merge=…)` 주입으로 스윕, `ER_TRACE_STEP` 으로 trace 조회. `app/` 무수정 |
| 29 `reports/embed_pilot.md`(P0-embed-pilot) | D4 근거·모델·N=1536 | 실 임베딩 공급자·모델을 여기서 인용(새로 고르지 않는다) |
| README.md "베이스라인 3종 실행법"·"평가 데이터셋(파일럿 40건)" 절 | 실행법 문서 | 새 절을 만들지 않고 **"파일럿 평가 실행법"을 이어 붙인다**(F-0ffff5 선례 — registry 비고에 한 줄) |

신규(registry 행 예정): `evaluation/runner.py`·`metrics.py`·`calibration.py`·`curve.py`·`report.py`, `scripts/run_pilot_eval.py`, `tests/test_eval_{runner,metrics,calibration,curve,report}.py`, `reports/metrics.json`·`calibration.json`·`curve.csv`·`eval.md`·`failure_cases.md`·`cost_estimate.md`·`pilot/raw-<ts>.jsonl`, `docs/user-setup/10-pilot-eval-run.md`.

## 인계 항목 대장 (앞 패키지가 넘긴 것 — U 번호·처리 방식. P4 02-plan-verify 점검 대상)

**P3-baselines 04-review §7 (15항)**

| # | 인계 내용 | 처리 |
|---|---|---|
| 1 | 시나리오 사이 DB 초기화·반복 실행 | **U1** — 결정 D 로 격리 방식 확정 후 구현 |
| 2 | 분모 규칙(ambiguous 3 제외·`passing_mentions` 6 오탐·ask_user 제3 범주) | **U2** — `meta.denominator_rule` 에 기록, 테스트 전수 |
| 3 | 지표·곡선·보정표, `ERConfig(t_merge=…)` 스윕, `top_k` 미스윕 | **U2·U3·U4** + 결정 H(`top_k` 금지 명시) |
| 4 | `RESOLVERS` 이름 = `metrics.json` 키(순서 고정) | **U4** 작성·**U9** 검증 |
| 5 | 판정 모델별 재기록(`detail["provider"|"model"]`) | **U3**(보정표 그룹 키)·**U7**(evidence `meta`) |
| 6 | 실 임베딩·실 LLM 특성은 P4 가 처음 본다 | **U6**(dry-run·비용 가드)·**U7**(실 실행) |
| 7 | `agent_traces` 증분 실측(proposed +2·embedding_only +1·나머지 0) | **U1** — `MentionDecision` 이 단일 출처, trace 는 보조. **U7** 에서 trace 재계산 표본 검증 시 이 수를 전제 |
| 8 | `load_scenario_state(…, embedder=…)` 명시 + `embedded_alias_count == alias_count` 단언 | **U1** — `embedder=None` 이면 오류로 즉시 실패 |
| 9 | 두 번 적재하면 두 벌 → 롤백/`user_id` 격리 | **U1** + 결정 D |
| 10 | `hints` 는 다섯 방식 같은 값, 기본 `None` | **U1** — 호출 스파이 테스트 |
| 11 | `forced_reason`(한 자리 하나)·`score_clamped` 집계 규칙, 강등 판독(`band_by_threshold`/`raw_decision`) | **U2**(forced_reason 분포)·**U3**(clamp 보정표 제외) |
| 12 | 비용(`llm_single` 프롬프트가 더 길다, `prompt_chars`·`person_count`) | **U6**(사전 추정·상한) + 결정 B |
| 13 | 사용자 스모크 08 결과를 P4 evidence 로 | **U6** + 결정 I |
| 14 | `score` 의미가 방식마다 다르다 — 같은 축 금지 | **U2·U4** — `score` 비교 표를 만들지 않는다. 보정표는 `s_llm` 내는 두 방식만 |
| 15 | 표본 40건은 방향·실패 유형만 | **U8** + 범위 "하지 않는 것"(운영 임계치 확정은 P10) |

**P3-baselines 04-review §6 [권고]**: 2(`score_clamped` 보정표 제외/별도 표시) → **U3**. 6(사용자 스모크 08 실행, P4 착수 전 1회) → **결정 I** + **U6**.

**P1-pilot-dataset 04-review §7 (13항)**

| # | 인계 내용 | 처리 |
|---|---|---|
| 1 | 시나리오 사이 DB 초기화(가상 성명 재등장 오염) | **U1** |
| 2 | 사전 상태 = `seed_persons` + `aliases` 그대로(대화 중 호칭 없음) | **U1** — `scenario_state` 재사용, 적재 로직 재구현 금지 |
| 3 | `ambiguous: true` 3건 분모 제외 | **U2** |
| 4 | `passing_mentions` 6개 = 오탐 분자 | **U2** |
| 5 | `expected_ask_user.allowed` 는 허용 집합(단일 정답 채점 금지) | **U2** |
| 6 | ask_user mention 은 제3 범주 + `ask_user_rate_by_kind` | **U2** |
| 7 | 이벤트 F1 을 클래스별로 보고(분포 76건, praise 1·absolute 0) | **범위 밖 — 빠짐(의도)**. 추출은 P5-loop 이 하므로 P4 에서 잴 대상이 없다. 그대로 **P10 으로 재인계**(아래 §P10) |
| 8 | `manifest.generator` 는 생성 시점 기록 — 판정 모델별로 P4 evidence 에 다시 적는다(P1 값 무수정) | **U7** evidence(`meta`) |
| 9 | 라벨 재해석 금지 | **U8**(라벨 의심은 새 검수 기록+사용자 결정) · **U9**(`git diff -- data/` 0줄·`--strict` rc=0) |
| 10 | `schema_version` 2 계약, 더 필요하면 v3 + manifest 갱신 | **U1** — `check_schema_version()` 재사용. mention 단위 추가 정보가 필요하면 FIX 가 아니라 미결로 올린다(아래 리스크) |
| 11 | 40건은 방향·실패 유형만, 운영 임계치는 P10 | **U8** + 범위 |
| 12 | F-251dc2·F-bdd6c5 는 P4 01-plan 이 결정 | **결정 G·H**(이 문서가 결정 문장으로 확정) |
| 13 | 함정 12건은 수치가 나빠도 되돌리지 않는다 | **U8**(`by_trap_kind` 거동 보고) |

**P3-er 04-review §7 P4 절**

| 인계 내용 | 처리 |
|---|---|
| 재계산 입력 계약: `agent_traces WHERE step='er_resolve' AND tool_name='er'` 1행 = 판정 1개, `output.confidence_breakdown{…}`·`candidates[]` 로 재계산 | **U1**(`trace_id` 보존) · **U7**(표본 재계산 abs diff 0) · **U9**(판정 표 마지막 행) |
| 공급자별 보정표(`llm.provider`/`llm.model`/`llm.s_llm`), `llm.error` 어휘 6종, `llm.skipped` | **U3** |
| 곡선은 `config=ERConfig(t_merge=…)` 주입, `band_by_threshold` 만 순수 산식, `forced_reason != null` 별도 집계 | **U2·U4** |
| 리스크 계측: `rule_checked==0` merge·`relaxed_retry==true` merge 의 오병합률, `derive_hints` 빈 dict 비율 | **U2**(부분집합 지표) · **U8**(해석) |
| 실 임베딩·실 LLM 은 P4 가 처음 본다(R4·R9 실호출 미검증) | **U7** — 이 실행이 R4·R9 의 "실호출 미검증" 꼬리표를 닫는 증거다 |

**P3-llm-providers 04-review §7 (7항, 2026-09-15)**

| # | 인계 내용 | 처리 |
|---|---|---|
| 1 | 공급자 선택·결정 A 정합 — `LLM_PROVIDER=openai` 명시, `LLM_PROVIDERS_ENABLED` 미설정, `meta.provider`·`meta.model` 은 `select_provider(env)`·`Judgement.model`/`detail["model"]` 출처(단일 출처 `JUDGES`) | **U1**(env 명시)·**U4**(`meta` 조립)·**U7**(evidence) |
| 2 | Gemini 실호출 미검증 0/3 — P4 는 기본 안 돈다(결정 A (ii)). 돌리려면 스모크 03·08 `--provider gemini` 먼저 | **결정 A 그대로(OpenAI 1벌)**. Gemini 벌은 P10 후보(§P10 9). 사용자가 03·08 gemini 스모크를 실행했으면 결과만 **U6** evidence 로 옮긴다 |
| 3 | 재시도 비대칭(Gemini timeout·connection 만 1회 / Claude·OpenAI SDK `max_retries=1` 은 429·5xx 도) | **U2** — `llm_error` 분포 표 각주 1줄(이번 실행은 OpenAI 1벌이므로 비교 없음, 각주만) |
| 4 | `Judgement.model`(Gemini) 은 `response.model_version` 우선 — 설정 문자열과 다를 수 있음 | **U3** — 그룹 키 `model` = 판정이 돌려준 값, 설정값은 `meta.model_configured` |
| 5 | 토큰 필드(Gemini `usage_metadata`, thinking 토큰 별도) | **U6** — 비용 추정은 `tokens_in`/`tokens_out` 실측 합계로, OpenAI 만 대상. Gemini 주의는 `cost_estimate.md` 각주 |
| 6 | 스키마 실 API 거부 시 `api_error`(400) 강등 — 모든 mention 에 `api_error` 면 공급자 층 문제 | **U7** — 리스크 절 "오류율 5%" 규칙과 결합: 전 mention `api_error` 면 게이트 판정에 쓰지 않고 evidence + 사용자 보고(재시도 금지) |
| 7 | 닫는 커밋 해시를 P4 01-plan 5행에 | **완료** — 이 문서 5행 `59c67cc`(2026-09-15) |

**05-remediation 소견 — 이 계획의 결정**

- **F-251dc2**(trace `candidates[].similarity`·`aliases_matched` 가 `s_emb`·전체 별칭의 복제) → **결정 G: (b) 불필요를 명시한다.** 근거: (i) 이 패키지의 지표·보정표·곡선은 전부 `MentionDecision`(JSONL)에서 계산하며 trace 는 재계산 **검증용 보조**다. (ii) 소견 자체가 "`s_emb` 는 이미 `[0,1]` 안이라 재계산 정확성(S3.7)에는 영향 없음"이라고 확인했다. (iii) "실제 일치 별칭"은 U8 실패 케이스 분석에서 알고 싶은 정보지만, `exact_raw`/`exact_norm` 두 방식의 결과가 같은 mention에 대해 문자열 일치 여부를 **이미 알려 준다**(다섯 방식을 같은 입력에 돌리는 설계의 부수 이득). (iv) 반대쪽(a)을 택하면 `app/er/candidates.py` 수정 = 원칙4 경계의 `app/` 변경이고, **게이트 패키지가 평가 대상 코드를 만지는 것**은 원칙8 관점에서 최악의 순서다. → `app/` 수정 요구 **없음**. 사용자 결정 항목으로도 올린다(결정 G).
- **F-bdd6c5**(`ERConfig.top_k` 가 실제로 전달되지 않음) → **결정 H: `top_k` 는 스윕하지 않는다.** 이 계획은 `ERConfig(t_merge=…)` 만 바꾸고 `top_k` 는 기본값 그대로 둔다. `metrics.json` `meta` 에 `top_k_swept: false` 와 사유(F-bdd6c5)를 적어 04-review·P10 이 오해하지 않게 한다. `search_person` 확장은 P5 이전 사소 FIX 후보로 남긴다(이 패키지 아님).

## 리스크 · 미결

**사용자 결정이 필요한 항목 (U1 착수 전. 결정은 메인 세션·사용자가 한다 — L-004)**

- **결정 A — 실 LLM 공급자·모델.** (i) `LLM_PROVIDER=anthropic` + `ANTHROPIC_MODEL` 소형 모델(**권장** — 제안 방식 `judge_from_env()` 와 `llm_single` 이 **같은 환경변수·같은 모델**을 읽으므로 모델 차이가 방식 차이로 둔갑하지 않는다, 원칙8. 제품이 Claude 기반이라는 기획서 전제와도 맞는다) / (ii) `LLM_PROVIDER=openai` + `OPENAI_MODEL`(임베딩과 키 하나로 끝나 운영은 단순하나, 제품 전제와 어긋나고 P10 비교 축이 하나 늘어난다) / (iii) 둘 다 돌려 공급자 2벌 보정표(가장 방어력이 높지만 **비용·시간 2배**). 어느 쪽이든 `meta.provider`·`meta.model` 에 기록하고 보정표를 그 키로 나눈다.
- **결정 B — 비용 상한과 `reports/cost_estimate.md` 흡수 여부.** backlog 15행 `[eval-agent] LLM 비용 실측 — reports/cost_estimate.md`(P0-cost, 미착수)는 "150건 × 4방식 × 10임계치 총액 추정"이 수용 기준이다. (i) **이 패키지 U6 이 40건 실측을 내고, 그 실측으로 150건을 외삽해 `cost_estimate.md` 를 채워 P0-cost 를 닫는다**(**권장** — 실측 없이 추정하는 것보다 정확하고, 어차피 U6 이 같은 계산을 한다. backlog 15행은 architect 가 "P4 U6 로 흡수" 로 갱신) / (ii) P0-cost 를 별도 패키지로 남기고 P4 는 자기 실행 비용만 본다(범위는 깨끗하나 같은 계산을 두 번) / (iii) P10 으로 미룬다(게이트 실행 전에 비용을 모르는 상태가 된다 — 비권장). **상한값도 함께 정한다**: `--max-cost-usd` 기본값 제안 **$5**(AWS Budgets $10 알림의 절반, CLAUDE.md 첫날 필수 항목과 정합). 초과 예상이면 실행하지 않고 멈춘다.
- **결정 C — 스윕 격자와 반복 횟수(LLM 비결정성).** `T_merge` 목록은 S3.7·D10 이 {0.5,0.55,…,0.95} 10점으로 **고정**했으므로 변경 대상이 아니다. 결정할 것은 **LLM 호출 횟수**다. (i) **LLM 판정은 임계치와 무관하므로 mention 당 1회만 호출하고 그 응답(`s_llm`·`matched_person_id`)을 10개 임계치에 재사용**(**권장** — 비용이 1/10 이고, `band_for` 는 순수 함수라 결과가 동일하다. 제안 방식도 `resolve()` 를 1회 돌린 뒤 `confidence` 에 밴드만 다시 매기면 되므로 U1 이 "판정 1회 → 밴드 10벌" 구조를 쓴다) / (ii) 임계치마다 다시 호출(10배 비용, 비결정성이 곡선에 섞여 해석 불가) / (iii) 1회 호출 + **반복 3회 재실행으로 분산 측정**(재현성 근거는 강해지나 3배 비용). **재실행 정책**: temperature 0 이라도 동일 응답이 보장되지 않으므로, 원시 JSONL 을 커밋해 "이 수치는 이 응답에서 나왔다"를 고정한다(결정 F 와 연동). (i) 채택 시 U1 의 러너 구조가 "resolve 1회 → 밴드 재계산"이 되고, 이는 `MentionDecision.detail["band_by_threshold"]`·`confidence` 가 이미 주는 정보로 가능하다.
- **결정 D — 러너 격리 방식.** (i) **시나리오마다 트랜잭션을 열고 끝나면 롤백**(**권장** — P2·P3-er·P3-baselines 테스트가 이미 쓰는 롤백 픽스처와 같은 방식이라 새 코드가 거의 없고, 남는 행이 0 이라 "두 벌" 사고가 구조적으로 불가능하다. 단점: 같은 세션 안에서 돌아야 하고 `agent_traces` 도 함께 롤백돼 trace 재계산은 실행 중에만 가능 → U7 은 trace 표본을 **실행 중에** 덤프해 evidence 로 남긴다) / (ii) 시나리오마다 다른 `user_id`(trace 가 남아 사후 조회가 쉽고 `search_person` 이 `user_id` 범위를 지키므로 격리도 성립. 단점: 40 시나리오 × 방식 × 회차만큼 행이 누적되고 DB 초기화 책임이 다시 생긴다) / (iii) 둘 다(시나리오마다 새 `user_id` + 전체를 하나의 롤백 경계로 — 격리 이중화, 구현이 조금 는다). 결정에 따라 U1 의 단언 문장이 달라진다.
- **결정 E — `reports/` 산출물 커밋 범위.** (i) **`metrics.json`·`calibration.json`·`curve.csv`·`eval.md`·`failure_cases.md` + 원시 `pilot/raw-<ts>.jsonl` 을 전부 커밋한다**(**권장** — 원칙8 "평가 수치는 재현 가능해야 한다". 원시 JSONL 이 없으면 지표를 다시 계산할 방법이 LLM 재호출뿐이다. 크기는 40 × mention × 5 × (결정 C-i 이면 1벌) 수준으로 작다) / (ii) 집계본만 커밋하고 원시는 로컬 보관(저장소는 가볍지만 재계산 불가) / (iii) 전부 `.gitignore`(재현성 포기 — 비권장). **어느 쪽이든 프롬프트 원문·키·응답 원문 중 개인정보·비밀은 넣지 않는다**(security §1; 시나리오는 가상 성명이라 본문 자체는 안전).
- **결정 F — `s_llm` 정답률의 "정답" 정의.** (i) **판정의 `decision` + `person_id` 가 골드와 일치**(**권장** — 사용자가 체감하는 옳음과 같고 오병합률 정의와 분모가 맞는다) / (ii) `matched_person_id` 만 일치(밴드 무관 — LLM 자체의 식별 능력을 보지만 `identity`/`new_person` 이 정의되지 않는다) / (iii) 둘 다 보고. 보정표의 신뢰도 주장(R4)이 이 정의 위에 서므로 04-review 전에 고정해야 한다.
- **결정 G — F-251dc2 처리.** (i) **P4 는 두 필드가 불필요함을 명시하고 `app/` 을 고치지 않는다**(**권장** — 위 "05-remediation 소견" 의 (i)~(iv). 이 계획의 기본안) / (ii) `app/er/candidates.py::_to_scored` 를 확장해 `similarity_raw`·`aliases_matched` 부분집합을 보존한다 — **원칙4 경계의 `app/` 수정이므로 사용자 승인이 필요**하고, 게이트 패키지가 평가 대상 코드를 만지는 순서가 된다. 채택 시 U0 선행 단위 + P3-er 회귀 테스트 재실행이 붙는다.
- **결정 H — F-bdd6c5 처리.** (i) **`ERConfig.top_k` 스윕 금지를 명시하고 `meta.top_k_swept: false` 로 기록한다**(**권장** — 인계 3·12 가 이미 같은 방향. `search_person` 시그니처(S3.2)는 변경 금지 대상이다) / (ii) P5 이전 사소 FIX 로 `search_person` 내부 주입을 열고 P4 가 `top_k` 도 스윕한다(비교 축이 하나 늘고 `app/` 수정 + 비용 증가).
- **결정 I — 판정기 실호출 전 사용자 스모크 03·08 선행 여부.** (i) **U6 전에 `docs/user-setup/03-er-smoke.md`(제안 방식)와 `08-baseline-smoke.md`(베이스라인 3)를 사용자가 1회씩 실행하고 결과를 evidence 로 남긴 뒤 U7 을 돈다**(**권장** — 40건 × 5방식을 돌리다가 키·모델명·권한 문제로 중간에 죽으면 비용만 나간다. P3-baselines [권고] 6·P3-er F-87c597 이 요구한 실호출 검증도 같이 닫힌다) / (ii) U7 실행 자체가 스모크를 겸한다(단계는 줄지만 실패 시 손실이 크다).
- **결정 J — 곡선 산출 형식.** (i) **`curve.csv` + `eval.md` 안의 Markdown 표만**(**권장** — 의존성 0, 재현 쉬움, `metrics.json` 만으로 재생성 가능이라는 요구와 정합. 발표용 그림은 P10 에서) / (ii) matplotlib PNG 를 함께 생성(발표 자료에 바로 쓰이지만 새 의존성·바이너리 커밋·재생성 멱등 판정이 까다로워진다) / (iii) PNG 는 P10 에서만.
- **결정 K — 게이트 통과 기준("미달"의 정의).** 기획서·S3.7 에 절대 수치가 없다(위 수용 기준 절의 grep 근거). (i) **상대 기준: 제안 방식의 오병합률이 `T_merge=0.8`(D10 초기값)에서 베이스라인 3종의 최저 오병합률보다 낮고, 동시에 미검출률이 베이스라인 최고치보다 나쁘지 않다. 곡선이 D10 방향(`T_merge`↑ → 오병합↓·`ask_user(identity)`↑)을 따른다**(**권장** — 40건 표본에서 절대 수치를 게이트로 삼으면 표본 오차로 프로젝트가 좌우된다. 원칙1 의 비대칭 비용을 그대로 판정식으로 옮긴 형태이고, 기획서가 약속한 것도 "베이스라인 대비 우위"다) / (ii) 절대 수치(예: 오병합률 ≤ 5%)를 지금 정한다(명료하지만 근거가 없다 — 부록 A 수치는 예시라고 기획서가 못박았다) / (iii) 게이트를 수치로 걸지 않고 04-review 가 서술로 판정(원칙8 의 "재현 가능"과 어긋난다). **(i) 채택 시에도 미달이면 P5 를 시작하지 않고 U8 산출물 + `/devlog change` 로 간다.**

**결정 확정 (사용자, 2026-09-11 — 메인 세션 기록. K 는 2026-09-17 개정. 계획 본문의 선택지 문단은 원문 보존)**

| 결정 | 확정 | 계획에 미치는 것 |
|------|------|------------------|
| A 실 LLM 공급자·모델 | **(ii) OpenAI** — P4 U7 은 `LLM_PROVIDER=openai` + `OPENAI_MODEL` 로만 돈다(임베딩과 키 하나). **단, 사용자 요구: 판정기는 Claude·OpenAI·Gemini 를 모두 바꿔 끼울 수 있어야 하고 개발자가 원할 때 켜고 끌 수 있어야 한다.** Gemini 는 현재 `judge.py`·`llm_single.py` 에 이름만 예약·미구현이므로 **P4 착수 전 별도 소패키지**(architect 가 backlog·INDEX 에 추가, backend-agent 구현: `GeminiJudge`·`GeminiSingleCaller`·`google-genai` 의존성·공급자 켜기/끄기 스위치·회귀)로 처리한다. P4 의 의존 줄에 그 패키지 완료를 추가한다. | U7 실행 = OpenAI 1벌. `meta.provider="openai"`·`meta.model=OPENAI_MODEL`. 보정표는 공급자·모델 키로 나누되 이번 실행은 1벌. 다른 공급자는 스모크 1회로 동작만 확인(결정 I) |
| B 비용 상한·P0-cost 흡수 | **(i)** U6 이 40건 실측으로 150건을 외삽해 `reports/cost_estimate.md` 를 채워 P0-cost 를 닫는다. `--max-cost-usd` 기본 **$5** | backlog 15행 "P4 U6 로 흡수" 표기(착수 승인 후 메인 세션) |
| C 스윕·반복 | **(i)** LLM 판정 mention 당 1회 → 밴드 10벌 재계산 | U1 러너 구조 "resolve 1회 → 밴드 재계산" |
| D 격리 | **(i)** 시나리오별 트랜잭션 롤백 | U1 단언 = 2회 실행 증분 0; U7 trace 표본은 실행 중 덤프 |
| E `reports/` 커밋 | **(i)** 원시 JSONL 포함 전부 커밋 | 원칙8 |
| F `s_llm` 정답 | **(i)** `decision`+`person_id` 골드 일치 | U3 보정표 |
| G F-251dc2 | **(i)** 불필요 명시, `app/` 무수정 | 05-remediation 절 그대로 |
| H F-bdd6c5 | **(i)** `top_k` 스윕 금지, `meta.top_k_swept:false` | U4 |
| I 스모크 선행 | **(i)** U6 전 03·08 카드 사용자 1회씩(OpenAI 경로 포함) | U6 evidence 이관 |
| J 곡선 형식 | **(i)** `curve.csv` + Markdown 표, PNG 는 P10 | U4·U5 |
| K 게이트 기준 | **(i) → 개정 (a) 지배 기준(사용자 2026-09-17, verifier 02-plan-verify H-1)**: `T_merge=0.8` 에서 **어떤 베이스라인도 제안 방식을 지배하지 않는다**(지배 = 그 베이스라인의 오병합률 ≤ 제안 방식 **그리고** 미검출률 ≤ 제안 방식, 둘 중 하나는 엄격히 <) **그리고** 곡선이 D10 방향(`T_merge`↑ → 오병합↓·`ask_user(identity)`↑). 개정 사유: `exact_raw`/`exact_norm` 은 단독 일치 1명일 때만 merge(`evaluation/resolvers/exact_match.py` 264~276행)라 40건에서 오병합 0 이 되기 쉬워, 원안 "제안 방식 오병합률 < 베이스라인 최저" 는 제안 방식이 오병합 0 이어도 `0 < 0` 거짓 → 방식 품질과 무관하게 미달. 지배 기준은 원칙1 의 두 축을 유지하면서 0 동률 함정을 피한다. 미달 시 P5 미착수 + U8 + `/devlog change` | 수용 기준 해석 (ii)·04-review 판정식 = U4 `metrics.json.gate`(판정 표 "게이트" 행) |
| L 제3 범주 정의 | **(i)** `identity` 만 제3 범주, `new_person` 은 미검출 채점(사용자 2026-09-18, U2 구현 판단 → 확정. 65행 해석 줄) | U2·U4·U5·U8 |

**리스크(결정이 아니라 지켜볼 것)**

- **실 LLM 비용·소요 시간.** 40 시나리오 × mention × 2방식(`proposed`·`llm_single`) LLM 호출 + 별칭 112개·mention 임베딩. `llm_single` 은 사전 상태 **전 인물**을 프롬프트에 넣어 제안 방식보다 길다(인계 12). 완화: 결정 C(i) 로 임계치당 재호출 금지, 결정 B 의 `--max-cost-usd` 가드, U6 dry-run 으로 호출 수를 먼저 확정.
- **표본 40건의 통계적 한계.** 카테고리당 6~10건이라 오병합 1건이 비율을 크게 흔든다. 완화: 모든 비율에 **분자/분모를 함께** 적고(`"false_merge": {"n": 2, "d": 57, "rate": 0.035}` 형태), `eval.md`·`failure_cases.md` 의 결론 문장을 "방향과 실패 유형"으로 제한(인계 15). 신뢰구간을 쓰더라도 해석은 P10.
- **`embedding_skipped` 사고.** `embedder=` 를 빠뜨리면 `person_aliases.embedding` 이 전부 NULL 이 되고 `embedding_only`·`proposed` 가 무너져 "방식이 나쁘다"로 오독된다(인계 8). 완화: U1 이 `embedded_alias_count == alias_count` 를 단언하고 불일치 시 **경고가 아니라 실행 중단**.
- **공급자 장애·레이트 리밋.** `llm.error` 어휘 6종(`timeout/rate_limit/api_error/connection/schema/out_of_range_id`)이 분모에 섞이면 지표가 왜곡된다. 완화: U2 가 오류 건을 **별도 범주**로 집계하고 분모에서 뺀 수를 `meta` 에 남긴다. 오류율이 5%를 넘으면 그 실행은 evidence 로 남기되 게이트 판정에 쓰지 않고 사용자에게 보고(재시도 남발 금지, 원칙8).
- **`agent_traces` 증가량.** 제안 방식 호출 1회당 +2행(`er_resolve`+`search_person`), `embedding_only` +1(인계 7). 40 × mention × 회차면 수천 행이다. 결정 D(i) 롤백이면 남지 않지만 **실행 중에만 조회 가능**하므로 U7 이 표본 덤프를 실행 중에 뜬다. (ii) `user_id` 격리면 누적 행의 정리 책임이 생긴다.
- **재실행 시 초기화 누락.** 같은 시나리오를 두 번 적재하면 인물·별칭이 두 벌이 되어 동명이인이 인위적으로 생기고 오병합률이 부풀려진다(인계 9). 완화: 결정 D 의 격리 + U1 테스트(2회 실행 후 증분 0).
- **`schema_version` 2 계약의 한계.** mention 단위 추가 정보(함정 대상·선행사 턴 등)가 실패 케이스 분석에 필요해질 수 있다. 그때 FIX 로 데이터를 고치지 않고 `schema_version` 3 + `manifest.json` 갱신 + 사용자 결정으로 간다(P1 §7 인계 10). 이 패키지 기본 입장: **추가 없이 있는 필드로 분석한다**.
- **게이트 패키지의 자기검증 유혹**(원칙8·L-002). 구현(eval-agent)과 판정(verifier)이 다른 모델이어야 하고, 수치가 나쁠 때 **설정을 바꿔 다시 돌리는 것**이 가장 흔한 위반 형태다. 방어: 판정 표의 "실 실행 evidence 는 설정당 1개" 항목과 03-log 의 설정 변경 사유 기록.
- **`reports/` 는 활성 패키지 없이도 쓸 수 있는 경로**(`stage-gate.sh` 예외). 그래도 이 패키지 코드는 `evaluation/`·`scripts/`·`tests/` 에 들어가므로 **`CURRENT.md active: P4-pilot-eval` 등록 후에만** U1 을 시작한다.

## P10-final-eval 로 넘길 것

P1 04-review §7 "P10-final-eval 로" 1~5 를 그대로 승계한다.

1. `occurred_at_kind: absolute` **0건** — 과거 절대 날짜 발화 보충 필요(결정 N 의 결과).
2. `praise` 1·`other` 5 표본 부족, `personal_share` 25/76 편중, `favor` 사용자→인물 방향 1건 편중.
3. 위계 `하` 6/60, 발화 10~26자, 턴 3~5, 한 턴 지칭 1개 편중 — 실사용보다 쉬운 **과대평가 방향** 편향.
4. **일정(schedule) 골드 라벨**(결정 C) 과 정밀 `occurred_at` 정규화 평가(결정 B).
5. `schema_version` 승격 규칙(v3 + manifest 갱신 + 사용자 결정).

이 계획이 더하는 것:

6. **이벤트·일정 추출 F1(클래스별)·툴 호출 정확도** — P1 §7 인계 7. P4 는 mention 해석만 재므로 범위 밖이고, 추출 주체인 P5-loop 이 생긴 뒤 P10 이 잰다. 클래스별 보고(praise 1·absolute 0 이 매크로 평균에 묻히지 않게)라는 요구는 그대로 유효.
7. **운영 임계치 확정** — `T_merge`·`T_new` 의 운영값과 D3 가중치 조정은 150건에서. P4 곡선은 방향과 후보 구간만 제시한다.
8. **`metrics.json` → `eval.md` 재생성**은 U5 가 이미 구현하므로 P10 은 데이터만 바꿔 그대로 쓴다(P10 수용 기준과 같은 명령).
9. **공급자 비교**(D4 "추후 다른 공급자와 성능 비교") — P4 는 OpenAI `text-embedding-3-small` 1종만. 보정표·metrics 의 그룹 키가 이미 공급자별이므로 P10 이 키만 늘리면 된다.
10. **`ERConfig.top_k` 스윕**(결정 H 로 이번엔 금지) 과 F-bdd6c5 의 사소 FIX 여부.
11. **비용 실측의 150건 외삽 검증** — 결정 B(i) 채택 시 P4 실측 → `cost_estimate.md` 추정치가 P10 실행에서 맞았는지 확인.

## 읽은 카드

- `.claude/gitlog.md`(2026-09-15 16:15 스냅샷, `bash .claude/scripts/gitlog.sh P4-pilot-eval`) — 브랜치(dev = main = 3c6108d / 승격 대기 0), `P4-pilot-eval` 태그 커밋 1건(701fb8d 계획 초안), P3-llm-providers 커밋 6건(025a7c4·c01381d·cf01e9f·7b94a69·10a66c3·59c67cc). 초안 시점(2026-09-11 12:57) 스냅샷은 dev 5a1bcbe / main 0e3447a / 승격 대기 10 이었다(L-001)
- `docs/wiki/packages/P3-llm-providers/04-review.md` — §6(열린 문제: 실호출 검증 공급자 0/3, H-1 proposal 안내문 → 사용자 (a) 확정)·§7 P4 인계 7항(위 인계 대장에 옮김)
- `docs/wiki/decisions/D11-llm-provider-registry.md` — 결정(기본 `openai`, 등록표 3종, 활성 스위치)·"코드에서 지켜야 할 것" (a)~(e)·파급(P4 결정 A 정합)
- `docs/user-setup/09-aws-deploy.md`(3c6108d) — 카드 번호 09 가 이미 쓰여 이 패키지의 사용자 카드는 **10** 번
- `docs/wiki/INDEX.md` — 패키지 표 60~80행(70행 `P4-pilot-eval | 게이트 파일럿 평가·보정표·곡선 | eval-agent | R3 R4`, 80행 "P4 이전에 P5 이후를 시작하지 않는다")
- `docs/wiki/CURRENT.md` — `active: none`·`frozen: none`, 메모(P3-baselines 완료·다음 후보 P4)
- `docs/backlog.md` — 10~17행 착수 준비(15행 `cost_estimate.md` 미완), 59~61행 P4 절(수용 기준 원문), 85~93행 리스크 로그(P4 시점 점검 2건: ER 성능 미달·`s_llm` 신뢰성)
- `docs/wiki/review-index.md` — R3(해소(문서), D10) · R4(구현완료 b1f2782, **실호출 미검증**) · R9(구현완료, **실 공급자 호출 미검증, P4 에서 실측**) 행
- `docs/wiki/specs/S3.7-eval-spec.md` — 전문(지표·곡선 x축·베이스라인·산출물·미달 시 절차)
- `docs/wiki/specs/S3.3-er-pipeline.md` — 4단계·확신도·두 임계치 밴드 절(1~18행)
- `docs/wiki/decisions/D10-two-thresholds.md`·`D03-confidence-formula.md`·`D04-embedding-provider.md`(N=1536 확정 절)·`D05-alias-level-embedding.md` — 각 "코드에서 지켜야 할 것"
- `CLAUDE.md` — 불변 원칙 1·2·3·8·9, 툴 7종 v2 표, 개발 프로세스
- `.claude/skills/eval-harness/SKILL.md` — 전문(1 데이터셋 스키마 · 2 지표 표 · 3 베이스라인 · 4 곡선 · 5 재현성/비용 · 산출물 · 품질 체크)
- `docs/wiki/packages/P3-baselines/04-review.md` — §6 [권고] 2·6(122~135행), §7 인계 15항(171~191행), 51건 판정 표 중 P4 관련 행
- `docs/wiki/packages/P1-pilot-dataset/04-review.md` — §7(151~177행) P4 인계 13항·P10 인계 5항·공통 주의
- `docs/wiki/packages/P3-er/04-review.md` — §7(150~163행) P4 절·실 스모크 명령
- `docs/wiki/packages/P3-er/05-remediation.md` — F-251dc2(806~830행)·F-bdd6c5(832~849행)
- `docs/wiki/packages/P4-pilot-eval/02-plan-verify.md`(verifier, 2026-09-17) — H-1(결정 K 판정식 0 동률)·R-1~R-4 → 이 개정의 근거. R-5(재밴드 시 `embedding_only` 동점 강등 재적용 테스트)·R-6(`meta.model` 은 응답 모델명)은 U1·U3 구현 시 참고
- `docs/wiki/registry.md` — 29·78~87·106~107·110~125행(`evaluation/`·`scripts/`·`app/er/`·`reports/` 행 grep)
- `docs/wiki/packages/P3-baselines/01-plan.md` — 형식 참고(작업 단위 문장·결정 확정 블록·판정 방법 표·P4 인계 절 176~183행), 리스크 절
- `docs/resolution-plan.md` — §3.7 곡선 문장(90·202행)·§5 P4 행(230행) grep. `docs/proposal.md` 11·170~177·392·400행 grep(**목표 수치는 예시이며 측정 결과가 아님** 확인)
- `docs/wiki/templates/plan.md` — 이 문서의 형식
