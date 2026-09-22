# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-22 21:05 — **P4b-er-redesign U4 완료·커밋**(해시는 journal 의 COMMIT 줄). 재개 세션이 20:40 중단 지점을 이어받아 사용자 확정 4건을 받고 마감했다: (1) 결정 D 해석 = 구현대로 — 재계산은 기록된 `weights`·`rule_checked` 로 제품 `combine()` 호출을 재현하고 `weights_effective` 는 `_check_weights_effective()` 교차 확인에 쓴다(`weights_effective` 를 config 로 넘기면 마지막 비트가 어긋나 `max_abs_diff == 0.0` 이 깨진다), (2) `METRICS_SCHEMA_VERSION` 2 유지, (3) `report.py` 부분집합 표 3열 유지, (4) P4 기준선 재검증 불가는 **명시적 거부**로 수용 — 하위 호환 분기를 두지 않는다. 전체 pytest **1325 passed / 0 failed**(U1 부터 밀려온 알려진 5건 해소, 새 실패 0), dry-run 사슬 rc=0 · network 0 · `dumped=180 recomputed=180 max_abs_diff=0.0`, `rule_checked==0` 40줄도 0.0(옛 D3 식이면 0.0875). evidence 9: `20260922-1955-u4-*` 1 + `2020-u4-*` 7 + `2035-u4-pytest-all-recheck`. **바로잡은 사실**: 기준선 `reports/metrics.json` 이 거부되는 사유는 스키마 판 번호가 아니라 결정 H(i) 의 meta 두 키(`weights_policy`·`penalized_merge_policy`) 결손이다 — 판 번호를 1 로 되돌려도 호환성은 돌아오지 않는다. 결정 기록은 01-plan `U4 이행 해석 확정` 항목과 03-log U4 `사용자 확정` 줄. **커밋 메시지는 사람이 읽는 문장 형식(사용자 지시 19:40) 계속 적용.**
active: **P4b-er-redesign** | frozen: none | 브랜치: dev — origin/dev = **dbcfca0**, U4 커밋 **1건 미푸시**(사용자 결정: 커밋만, 푸시는 U5 준비까지 묶어서). main = 3c6108d — 승격은 게이트 재판정 뒤(20:05 사용자 '보류', `.awaiting-decision` 마커 해제됨).

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 1/3(openai)** — 스모크 03(2ebf061)·08(750f11b) 완료, F-87c597 해소, R4 "실호출 확인". anthropic·gemini 는 선택(미실행). U7 실 실행 750f11b 기준 완료(결과는 위 갱신 줄).
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-46f1eb, F-036185(F-87c597 은 750f11b 에서 해소), F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`, JSON 읽기 `PYTHONUTF8=1`. 사용자 `!` 실행은 셸이 매번 새로 떠서 `set -a; . ./.env; set +a;` 접두 필요(키). `.env` 의 `DATABASE_URL` 은 사용자가 2026-09-22 에 5433 으로 수정(`app/config.py` 규칙 1: DATABASE_URL 이 POSTGRES_PORT 보다 우선 — U7 1·2차 실패 원인). 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **결정 I 이행 — U5 실 실행 전에 기준선 stamp 사본을 먼저 커밋**: `reports/{metrics.json,calibration.json,curve.csv,eval.md}` → `reports/pilot/<이름>-20260922-042440.*`. 판정: metrics 사본 sha256 이 `25e16dd6…` 로 시작하고 `raw`·`traces` 원본 diff 0줄. 기준선 덮어쓰기 금지.
2. `docs/user-setup/10-pilot-eval-run.md` 갱신 — `.env` 로드 주체·`PYTHONUTF8=1`·산출물 이동 절차.
3. **U5** eval-agent 위임 승인(L-004) → dry-run 준비 → **사용자가 키 있는 셸에서 실 실행 1회**: `set -a; . ./.env; set +a` 접두, 새 stamp, `--commit $(git rev-parse HEAD)`, `--max-cost-usd 5`, evidence 파일명에 `real-run`(R-9), Docker 5433. **U4 → U5 순서 필수** — 순서를 바꾸면 `--recheck-traces` 가 새 trace 를 거부해 rc=1 로 죽고 비용만 나간다.
4. **U6** `reports/failure_cases.md` §13(§1~12 는 손대지 않는다) — 감점 merge 계수는 새 `subsets.penalized_merge`(+`relaxed_pass_merges`·`reasons`)와 원시 JSONL 의 `detail["penalized_by"]` 로 바로 읽는다, 별도 파싱 불필요. → **U7** 문서·`registry.md` 비고 확장(새 행 아님)·`schema_version` 2 한 줄·기계 검증 → verifier 04-review 게이트 재판정(결정 K 그대로, sc-015/sc-007 는 별도 수용 기준, R-6).
5. 보류: dev 푸시(U4 커밋 1건), main 승격(게이트 재판정 뒤), 하네스 L-nnn(R-2 verify-plan 5번 불릿 의존·03-log Refs=커밋 Refs), 러너 `safe_summary` FIX, 09 카드 §2, anthropic·gemini 스모크, F-46f1eb·F-036185, P10 인계.

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
