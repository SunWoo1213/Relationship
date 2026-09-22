# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-22 23:45 — **U4 b5b412c · U5 선행 a8faa81 · U5 준비 4/4 완료(커밋 대기) → 다음은 사용자 실 실행 1회**. 재개 세션이 20:40 중단 지점을 이어받아 사용자 확정 4건으로 U4 를 마감했다: (1) 결정 D 해석 = 구현대로(재계산은 기록된 `weights`·`rule_checked` 로 제품 `combine()` 재현, `weights_effective` 는 교차 확인), (2) `METRICS_SCHEMA_VERSION` 2 유지, (3) `report.py` 부분집합 3열 유지, (4) P4 기준선 재검증 불가는 **명시적 거부**로 수용. U4 검증 전체 **1325 passed / 0 failed**. **바로잡은 사실**: 기준선 `metrics.json` 거부 사유는 판 번호가 아니라 결정 H(i) meta 두 키 결손 — 판을 1 로 되돌려도 호환성은 안 돌아온다. a8faa81 = 기준선 stamp 사본 4개(sha256 네 쌍 일치, metrics `25e16dd6…`) + 카드 10 P4b 갱신. **U5 준비(eval-agent 2회 위임, L-004 승인 23:22·23:33)**: 1/4 비용추정 rc=0(`llm_calls=282`·`tokens_in=120100/out=22560`·`cost_usd total=0.0316`·상한 $5) · 2/4 스텁 사슬 6단계 **rc=0**(`network_calls=0`·`rows=7050`·gzip·size ok·`[ok] 사슬 완료`) · 3/4 `--recheck-traces` **rc=0**(`dumped=1410 recomputed=1410 max_abs_diff=0.0`, `rule_checked==0` 930/1410 줄의 `weights_effective` 가 전부 `{0.625,0.375,0.0}`, `matched_candidate` dict 1370줄 전부에 `penalized_by` 키, 비지 않은 줄 260 중 강등 15) · 4/4 실행 직전 점검(카드 10 블록 인자·경로 무오타, 기준선 6파일 sha256, `validate_scenarios --strict` rc=0 total 40). 첫 시도 때 Docker 데몬이 꺼져 2/4·3/4 가 막혔고(스텁도 세이브포인트 때문에 DB 필요) 우회하지 않고 멈춰 사용자 기동 뒤 이어서 끝냈다. **스텁 수치는 게이트 판정에 쓰지 않는다.** 미커밋: evidence 4개 + 03-log U5 준비 항목(`pending`) + journal. **커밋 메시지는 사람이 읽는 문장 형식(사용자 지시 19:40) 계속 적용.**
active: **P4b-er-redesign** | frozen: none | 브랜치: dev — origin/dev = **dbcfca0**, 미푸시 **2**(b5b412c·a8faa81) + U5 준비 커밋 예정. main = 3c6108d — 승격은 게이트 재판정 뒤(20:05 사용자 '보류'). Docker `capstone2-postgres-1` Up/healthy 5433.

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 1/3(openai)** — 스모크 03(2ebf061)·08(750f11b) 완료, F-87c597 해소, R4 "실호출 확인". anthropic·gemini 는 선택(미실행). U7 실 실행 750f11b 기준 완료(결과는 위 갱신 줄).
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-46f1eb, F-036185(F-87c597 은 750f11b 에서 해소), F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`, JSON 읽기 `PYTHONUTF8=1`. 사용자 `!` 실행은 셸이 매번 새로 떠서 `set -a; . ./.env; set +a;` 접두 필요(키). `.env` 의 `DATABASE_URL` 은 사용자가 2026-09-22 에 5433 으로 수정(`app/config.py` 규칙 1: DATABASE_URL 이 POSTGRES_PORT 보다 우선 — U7 1·2차 실패 원인). 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **U5 준비 /commit**(대기 중): evidence 4개(`20260922-2314-u5-{dryrun-estimate,preflight}.txt`·`20260922-2338-u5-{dryrun-chain,recheck-traces}.txt`) + 03-log 항목. 코드·`reports/`·`data/` 0줄.
2. **U5 실 실행 — 사용자 몫**(에이전트가 대신 돌리지 않는다, security §6). 카드 10 "P4b U5 재실행" 블록 그대로:
   `ts=$(date +%Y%m%d-%H%M); set -a; . ./.env; set +a; POSTGRES_PORT=5433 PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --out reports/pilot --commit "$(git rev-parse HEAD)" --max-cost-usd 5 > docs/wiki/packages/P4b-er-redesign/evidence/$ts-u5-real-run.txt 2>&1; echo "rc=$?"`
   실행 전 확인: `.env` 의 `DATABASE_URL` 포트 5433(`app/config.py` 규칙 1 — P4 U7 2회 실패 원인), `OPENAI_API_KEY`(없으면 rc=2·과금 0), 현재 단가(다르면 `--price-*`). 예상 $0.0316. **같은 설정으로 두 번 돌리지 않는다**(결정 E(i)·원칙8) — 미달이어도 재실행이 아니라 U6. rc=1 이어도 출력을 지우지 않는다.
3. 실행 뒤: 산출물을 `reports/` 로 옮기고(stamp 사본이 있어 안전) `reports/cost_estimate.md` 실측 칸을 채운다. 새 `metrics.json` 은 `schema_version` 2 이고 `meta.weights_policy`·`meta.penalized_merge_policy` 가 있어야 한다.
4. **U6** `reports/failure_cases.md` §13(§1~12 무수정) — 감점 merge 는 `subsets.penalized_merge`(+`relaxed_pass_merges`·`reasons`)와 원시 JSONL 의 `detail["penalized_by"]` 로 바로 읽는다. → **U7** 문서·`registry.md` 비고 확장(U4 수정 5파일 + stamp 사본 4개 + `schema_version` 2)·기계 검증 → **04-review** verifier 게이트 재판정(결정 K 그대로, sc-015/sc-007 별도, R-6).
5. 보류: dev 푸시(2건+), main 승격(게이트 재판정 뒤), 하네스 L-nnn, 러너 `safe_summary` FIX, 09 카드 §2, anthropic·gemini 스모크, F-46f1eb·F-036185, P10 인계.

## 재개 시 읽을 카드 (이것만)
- `packages/P4b-er-redesign/01-plan.md`(작업 단위 58~69행, 결정 표, 판정 표), `02-plan-verify.md` §2·권고 R-1~R-9, `03-log.md` 마지막 항목, `decisions/D12*.md`·`D13*.md`(코드에서 지켜야 할 것), `changes/CR-001.md` §2, `docs/backlog.md` "P4b" 절
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `decisions/D11-llm-provider-registry.md`
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- 09 카드 §2 결정 10개(리전·DB A/B·인스턴스·도메인·443 제한·Session Manager·수동 dispatch·EC2 빌드·프론트·백업) — P9 착수 전 사용자 확정. DB A안(compose) 선택 시 D12 카드 필요.
- 하네스 L-nnn: `verify-impl.sh` 6번 완화 여부(다음 확장 전용 패키지 때 결정).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. Docker 가 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003).
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. `git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다. Bash 문자열에 마커 파일명·훅 금지 문구·환경변수 전체 출력(`environ` grep·`env -u` 포함) 금지 — 문서 수정은 scratchpad 스크립트 + python 또는 Write. `.env` 존재 확인 금지. `git checkout --` 금지. evidence 파일은 cp949 혼입이 있을 수 있어 python 읽기는 `errors="replace"`.
- **푸시 명령은 Bash 호출 하나에 단독으로**(뒤에 `grep` 등 실패할 수 있는 명령을 붙이면 종료 코드가 0 이 아니어서 cleanup 훅이 돌지 않는다 — 2026-09-15 실측, 같은 push 재실행으로 복구).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. verify-impl 재실행마다 `<ts>-pytest/lint/commits/summary.txt` 4개가 생기므로 중복 실행분은 지우고 커밋한다.
- 서브에이전트에게 HANDOFF·journal 금지 명시. `app/` docstring 에 "evaluation" 문자열 금지(`test_app_does_not_mention_evaluation_package_at_all`).
