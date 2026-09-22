# 10 · 파일럿 평가 실 실행 (P4-pilot-eval U7)

## 언제 필요한가
P4 파일럿 평가는 `data/scenarios/` 40건에 다섯 방식(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`)을 돌려 `reports/metrics.json`·`calibration.json`·`curve.csv`·`eval.md` 를 만든다. 이 한 번의 실행만 **실 LLM·실 임베딩**을 쓴다(그 밖의 테스트는 전부 네트워크 0). 키는 사용자만 다루므로(`security.md` §6) 이 카드의 명령은 사용자가 직접 돌린다.

**선행**: 03(ER 스모크)·08(베이스라인 스모크)을 먼저 1회씩 돌려 키·공급자·모델이 살아 있는지 확인한다(결정 I). 40건 × 5방식을 돌리다 키 문제로 중간에 죽으면 비용만 나간다.

## 왜 사용자 몫인가
자동 테스트는 실 LLM 을 부르지 않는다(원칙8 — 재현 불가능한 수치를 만들지 않는다). 스크립트는 `.env` 를 읽지 않고 환경변수를 통째로 출력하지도 않는다. 필요한 값은 **사용자 셸에만** 둔다.

## 필요한 환경변수 (이름만 — 값은 여기에 적지 않는다)

| 이름 | 필수 | 쓰임 |
|------|------|------|
| `OPENAI_API_KEY` | 필수 | 판정(`LLM_PROVIDER=openai`, 결정 A(ii))과 임베딩(`text-embedding-3-small`, D4)이 같은 키를 쓴다 |
| `OPENAI_MODEL` | 선택 | 없으면 `gpt-4o-mini`. 값은 `meta.model_configured` 에 남는다 |
| `POSTGRES_PORT` | 선택 | 로컬 컨테이너는 `5433`. 기본값과 다르면 반드시 준다 |

스크립트는 위 이름 외의 환경변수를 읽지 않는다. 키가 없으면 **rc=2** 로 멈추고 **이름만** 안내한다.

## 절차

1. 먼저 **비용 추정만** 본다(네트워크·DB 0):
   ```bash
   # Git Bash
   PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --dry-run --stub --estimate-only
   ```
   ```powershell
   # PowerShell
   $env:PYTHONIOENCODING="utf-8"; python scripts/run_pilot_eval.py --dry-run --stub --estimate-only
   ```
   `[estimate] cost_usd total=…` 와 `[estimate] price_source=…` 가 찍힌다. **단가는 저장소에 적어 둔 오프라인 상수**이므로 공급자 가격표에서 현재가를 확인하고, 다르면 다음 단계 명령에 `--price-in`/`--price-out`/`--price-embed` 를 붙여 실제 단가로 다시 계산한다.

2. (선택) 네트워크 0 으로 사슬 전체를 한 번 돌려 본다 — 키가 없어도 된다. 산출물은 임시 디렉터리에 둔다(`reports/` 아래는 스크립트가 거부한다).
   ```bash
   POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --dry-run --stub --out /tmp/pilot-dry
   ```

3. 실 실행. 키를 넣은 셸에서(01 카드 5번), 저장소 루트에서:
   ```bash
   # Git Bash
   ts=$(date +%Y%m%d-%H%M)
   POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 \
     python scripts/run_pilot_eval.py \
       --out reports/pilot \
       --commit "$(git rev-parse HEAD)" \
       --max-cost-usd 5 \
     > docs/wiki/packages/P4-pilot-eval/evidence/$ts-u7-real-run.txt 2>&1
   echo "rc=$?"
   ```
   ```powershell
   # PowerShell
   $ts = Get-Date -Format yyyyMMdd-HHmm
   $env:POSTGRES_PORT="5433"; $env:PYTHONIOENCODING="utf-8"
   python scripts/run_pilot_eval.py --out reports/pilot --commit (git rev-parse HEAD) --max-cost-usd 5 `
     > docs/wiki/packages/P4-pilot-eval/evidence/$ts-u7-real-run.txt 2>&1
   ```
   - `--commit` 은 **평가한 커밋 해시**다(L-001). `metrics.json` 의 `meta.commit` 과 `eval.md` 메타 표에 그대로 실린다.
   - Docker Desktop 이 켜져 있어야 한다(로컬 PostgreSQL 5433). 평가는 **아무것도 커밋하지 않는다** — 시나리오마다 트랜잭션을 되돌린다(결정 D(i)).

4. 저장한 파일을 **한 번 읽는다**. 프롬프트 원문·키는 출력에 나가지 않도록 되어 있지만, 저장 전 확인은 사용자 몫이다.

5. 결과 파일을 `reports/` 자리로 옮긴다(에이전트가 해도 된다): `reports/pilot/metrics.json` → `reports/metrics.json` 등. 원시 `reports/pilot/raw-<ts>.jsonl.gz` 와 **같은 stamp 의 `reports/pilot/traces-<ts>.jsonl`** 은 그대로 둔다(결정 E — 원시 응답이 있어야 지표를 다시 계산할 수 있다).

## 커밋되는 원시 판정은 `raw-<ts>.jsonl.gz` 다

`.githooks/pre-commit` 이 5MB 초과 파일을 막는데 전량 실행의 원시 JSONL 은 그보다 크다(스텁 실측 7.4MB). **gzip 으로 커밋한다**(사용자 결정 2026-09-21 — 결정 E 유지, 훅은 바꾸지 않는다).

- 실행은 평문 `raw-<ts>.jsonl` 을 먼저 쓰고(중단돼도 거기까지 남는다), 끝난 뒤 `raw-<ts>.jsonl.gz` 로 압축한 다음 **압축본을 metrics·calibration·curve 에 넘긴다**. 출력에 이 두 줄이 찍힌다.
  ```
  [gzip] reports/pilot/raw-<ts>.jsonl.gz 1234567 bytes (평문 7404682 bytes, level=9, mtime=0·파일명 미기록)
  [gzip] roundtrip_sha256=<64자> ok plain=보존 -- 이후 단계 입력은 압축본이다
  [size] reports/pilot/raw-<ts>.jsonl.gz 1234567 bytes limit=5242880 ok
  ```
- 커밋하는 것은 `.gz` 하나다. 평문은 기본 보존이므로 `git add` 에 넣지 않는다(지우고 싶으면 `--drop-raw-plain` — 왕복 sha256 검증을 통과한 뒤에만 지운다).
- `[size] … OVER` 와 `[warn] 커밋 한도 초과:` 가 나오면 그 파일은 커밋할 수 없다(rc 는 0 그대로다 — 수치가 틀린 게 아니라 파일이 큰 것이다). 그대로 보고한다.
- **커밋된 파일 하나로 지표를 다시 계산한다**(원칙8) — `--rows` 는 `.jsonl` 과 `.jsonl.gz` 를 똑같이 받고 결과 바이트가 같다.
  ```bash
  python -m evaluation.metrics --rows reports/pilot/raw-<ts>.jsonl.gz --out /tmp/metrics-recheck.json
  python -m evaluation.curve   --rows reports/pilot/raw-<ts>.jsonl.gz --out /tmp/metrics.json --curve /tmp/curve.csv
  ```
- `traces-<ts>.jsonl`(~1.7MB)은 한도 안이라 **평문 그대로** 커밋한다.

## 확신도 재계산 증거 (`traces-<ts>.jsonl`)

결정 D(i) 로 시나리오마다 트랜잭션을 되돌리므로 `agent_traces` 는 **실행이 끝나면 사라진다**. 그래서 실행 중에 제안 방식의 `step='er_resolve' AND tool_name='er'` 행을 `raw-<ts>.jsonl` 과 **같은 stamp** 의 `traces-<ts>.jsonl` 로 덤프하고, 사슬 끝에서 전 줄의 `confidence` 를 `0.5·s_llm + 0.3·s_emb + 0.2·s_rule` 로 다시 계산해 기록값과 비교한다(원칙3·원칙9, 01-plan 106행 판정 표).

```
[traces] dumped=1410 recomputed=1410 max_abs_diff=0.0 path=reports/pilot/traces-<ts>.jsonl
[traces] rule=0.5·s_llm+0.3·s_emb+0.2·s_rule (app.er.confidence.combine, weights={'llm': 0.5, 'emb': 0.3, 'rule': 0.2}, 기준 abs diff == 0)
```

- `max_abs_diff` 가 `0.0` 이 아니거나 `[fail] traces:` 줄이 있으면 rc=1 이다(어느 trace 인지 함께 찍힌다). 그 출력을 지우지 않고 그대로 보고한다.
- 덤프에는 프롬프트 원문·`llm.reason` 자유 서술·키가 들어가지 않는다(security §1).
- 파일만 들고 나중에 다시 확인할 수 있다(DB·네트워크·키 0):
  ```bash
  python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-<ts>.jsonl
  ```
- 파일이 너무 커지면 `--traces-per-scenario N` 으로 시나리오당 N 줄만 덤프한다(기본은 전량 — 표본을 고르면 판정을 유리하게 만들 여지가 생긴다, 원칙8).

## 종료 코드

| rc | 뜻 | 할 일 |
|----|----|-------|
| 0 | 사슬 완료(runner → metrics → calibration → curve → validate → report) | 산출물 5종과 `[ok]` 줄 확인 |
| 1 | 단계 실패·단언 위반(임베딩 수 불일치, 행 수 불일치, 스키마 검증 실패, **trace 재계산 abs diff ≠ 0** 등) | 출력의 `[fail]` 줄을 그대로 에이전트에게 보여 준다. **실패도 결과다** — 출력을 지우지 않는다 |
| 2 | 필요한 키 환경변수가 없다 | 안내된 **이름**을 셸에 넣고 다시 돌린다(값은 이 저장소에 쓰지 않는다) |
| 3 | 예상 비용이 `--max-cost-usd` 를 넘었다 | 단가를 확인하고, 필요하면 상한을 올리거나 `--limit` 로 범위를 줄인다. **이 경우 한 줄도 실행되지 않았다**(과금 0) |

## 기대 출력 (형태)

```
[estimate] run_mode=real scenarios=40 mentions=141
[estimate] llm_calls total=282 proposed=141 llm_single=141 (결정 C(i): …)
[estimate] cost_usd total=0.0316 (in=… out=… embed=…)
[estimate] max_cost_usd=5.0
[run] run_mode=real run_id=run-…  / dataset_hash=sha256:… / commit=…
[scenario] sc-001 aliases=2 embedded=2 rows=200 traces=40 ok   ← 40줄(시나리오마다 1줄)
[traces] dumped=1410 recomputed=1410 max_abs_diff=0.0 path=reports/pilot/traces-<ts>.jsonl
[rows] rows=7050 = mentions=141 × methods=5 × t_merge=10 (expected=7050)
[gzip] …/raw-<ts>.jsonl.gz … bytes (평문 … bytes, level=9, mtime=0·파일명 미기록)
[gzip] roundtrip_sha256=… ok plain=보존 -- 이후 단계 입력은 압축본이다
[run] run_mode=real network_calls=… 
[run] tokens_in=… tokens_out=… (실행 실측 합계, llm_fresh_call 행만)
[stage] metrics: rc=0 … [stage] report: rc=0
[ok] 사슬 완료
```

- 시나리오 줄이 `MISMATCH` 로 끝나면 별칭 임베딩이 비었다는 뜻이고 rc≠0 이다(그 상태의 수치는 방식 품질이 아니다).
- `[run] tokens_in/out` 이 이 실행의 **실측 토큰**이다 — `reports/cost_estimate.md` §3·§4 의 "U7 직후 채움" 칸에 이 값을 옮긴다.

## 끝났다는 증거

- `docs/wiki/packages/P4-pilot-eval/evidence/<ts>-u7-real-run.txt` 가 존재하고 비어 있지 않다.
- 판정 명령:
  ```bash
  PYTHONUTF8=1 python -c "import json;m=json.load(open('reports/metrics.json'))['meta'];print(m['provider'],m['model'],m['embedding_model'],m['run_mode'],m['commit'])"
  ```
  (`PYTHONUTF8=1` 은 Windows cp949 로케일에서 `open()` 이 UTF-8 JSON 을 읽다 `UnicodeDecodeError` 를 내는 것을 막는다 — 2026-09-22 실측.)
  → `run_mode` 가 `real` 이고 `provider`/`model` 이 `stub`·`fake` 가 아니어야 한다.
- 같은 설정으로 **두 번 돌리지 않는다**. 수치가 마음에 들지 않아 다시 돌리는 것이 게이트 패키지의 가장 흔한 위반이다(원칙8) — 미달이면 재실행이 아니라 `reports/failure_cases.md`(U8)로 간다.

## 끝난 뒤 에이전트에게

"파일럿 평가 돌렸어, 파일 `<경로>`, rc=`<코드>`" → 에이전트가 산출물을 `reports/` 로 정리하고, `reports/cost_estimate.md` 의 실측 칸을 채우고, 실패 케이스 분석(U8)과 완료 검토(04-review)로 넘어간다.
