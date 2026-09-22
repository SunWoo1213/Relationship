# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-22 (**[재개 2026-09-22 — 사용자 결정: 커밋 → 스모크 08 → U7 순. 실 실행은 사용자가 `!` 접두로 본인 셸에서 직접(.env 는 사용자 셸이 로드, 에이전트는 읽지 않음). ① 스모크 03 완료 rc=0: openai gpt-4o-mini-2024-07-18, in 410/out 48, s_llm 0.9·confidence 0.8384·band merge, 키 유효, 키 문자열 미혼입(`P3-er/evidence/20260921-2011-er-smoke-real.txt` — `reason` 필드는 cp949 이중 인코딩으로 복구 불가, 수치 온전; 커밋 **2ebf061** 등재, 03-log 항목 `pending`→2ebf061 은 다음 커밋에서) ② 스모크 08 완료 rc=0(2026-09-22 13:09, 사용자 `set -a; . ./.env; set +a; PYTHONIOENCODING=utf-8 python scripts/baseline_smoke.py`): openai gpt-4o-mini-2024-07-18 · llm_single identity score 0.7 · llm_error None · tokens 551/57 (`P3-baselines/evidence/20260922-1309-baseline-smoke-real.txt`). **결정 I(i) 03·08 충족 → U7 선행 조건 전부 완료.** 등재 커밋(이번): F-87c597 해소·review-index R4 실호출 확인·04-review 132행·§7 5·13·README 01/03/08·P4 evidence 3파일(smoke03/08 복사 + `20260922-1320-u6-smoke-handover.txt`) ③ **다음 = U7 실 실행**(사용자 셸, 카드 10, Docker 5433 켜야 함, `.env` 로드 접두 `set -a; . ./.env; set +a;` 필수 — `!` 셸은 매번 새로 뜬다). `reports/pilot/` 비어 있음(2026-09-22). 끝나면 traces·raw.gz·metrics 커밋·판정 표·cost_estimate §3·§4] P4-pilot-eval U1~U6 + U7 선행 2단위 완료: 보강 e7f0a9c(er_resolve trace 전량 덤프·재계산 diff 0) · gzip 1a5643b(raw `.jsonl.gz` 결정적 출력·`--rows` .gz 입력·5MB 가드, 스텁 실측 7,404,682 → 161,615 bytes). 전체 1285 passed(skip 0). 01-plan 46·71·80·126·205행 경로 표기 `.gz` 개정(사용자 선택, verify-plan FAIL 0/WARN 3) — docs 커밋 **1c84d35**(03-log 항목 해시 치환 완료). 스모크 03 증거 등재 커밋 = 이번(03-log 마지막 항목 `pending` → 다음 커밋에서 치환). **U7 코드 선행 조건은 모두 충족 — 남은 것은 키가 필요한 실 실행뿐**(스모크 03·08 → U7). **실행 방식 = 사용자가 본인 셸에서 직접 실행(사용자 결정 2026-09-21)** — 메인 세션이 명령 순서를 안내했고, 결과 파일(`reports/pilot/raw-<ts>.jsonl.gz`·`traces-<ts>.jsonl`·`metrics.json` 등과 실행 로그)이 생기면 다음 세션이 이어받아 evidence 이관·판정 표·U8 을 진행한다. 에이전트는 실 실행을 돌리지 않는다. 이 세션에 `OPENAI_API_KEY` 없음. U7 커밋 대상 = `raw-<ts>.jsonl.gz` + `traces-<ts>.jsonl`(평문 raw 는 add 하지 않는다). 실 실행 압축 크기는 `[size]` 줄로 확인(스텁 압축률로 단정 금지). F-95c6a7·F-0ffff5([권고]) 보류 → done 때 verifier.**)
active: **P4-pilot-eval** | frozen: none | 브랜치: dev = **2ebf061**(origin/dev·main = 3c6108d, 미푸시 11 — 마지막 2ebf061, 그 앞 1c84d35, 그 앞 9: b164f36·fb81234·a97521b·ee124b7·a59ecb4·dd6a996·0283ac0·e7f0a9c·1a5643b). 경위: verifier 02-plan-verify 1차(09-17 09:30) 보류 H-1 → 사용자 (a) 지배 기준·R-1~R-4 → 01-plan 개정 → verifier 2차(09:50) **통과**(FAIL 0/WARN 3 의도, 점검표 8/8) → 2026-09-18 사용자 재개 결정·계획 승인 → 02 `승인: 사용자 (2026-09-18)`, CURRENT active, `03-log.md` 생성(pending 항목 1), journal VERIFY×2·DECISION·START. backlog 15행 흡수 표기는 이미 있음. START 커밋 **b164f36**(18파일, 미푸시 — dev 가 origin/dev 보다 1 앞). 03-log START 항목 `pending` → b164f36 은 다음 커밋에 포함.

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 0/3** — F-87c597 열림(P3-er), 사용자 스모크 카드 03·08(`--provider anthropic|openai|gemini`)이 첫 실호출. R4 꼬리표는 P4 가 닫는다.
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(스모크 03), F-46f1eb, F-036185, F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`. 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. (a) 보강 e7f0a9c · (b) gzip 1a5643b · (b') 01-plan `.gz` 표기 개정 — 완료. **(c) 다음 = 사용자가 본인 셸에서 스모크 03·08 → U7 실 실행. 재개 시 먼저 `reports/pilot/` 에 결과가 생겼는지 확인하고, 없으면 실행 여부를 묻는다**: 스모크 03·08(OpenAI 경로) 1회씩 + U7(`docs/user-setup/10-pilot-eval-run.md`) — 키 필요, 실행 방식은 사용자에게 다시 묻는다(본인 셸 직접 / 키 로드한 셸에서 Claude Code 재시작). 비밀 파일은 에이전트가 읽지 않는다. 단가 상수(gpt-4o-mini in 0.15/out 0.60·embed 0.02 per 1M)는 오프라인 기록값 — 실행 전 현재가 확인 후 `--price-*`. dry-run 추정 LLM 282회·$0.0316·상한 $5. (d) U7 뒤: `traces-<ts>.jsonl` 을 `reports/pilot/` 에 raw 와 같은 stamp 로, 스모크 결과 P4 evidence 이관(F-87c597), `reports/cost_estimate.md` §3·§4 실측 채움, 판정 표 99·102·104·106·108행 evidence, 미달이면 재실행 금지 → U8. U6 인계: `curve.py --commit/--run-mode`, `dataset_hash` = `data/scenarios/*.json` 정렬 sha256, rc 0/1/2/3.
2. 09 카드 §2 결정 10개·4.0 항목(Budgets·도메인·SSO 프로필·GitHub prod 환경)은 사용자 몫 — P9 전 아무 때나. P4 통과 전 P5 이후 시작 금지.
3. 보류: 사용자 스모크 03·08 실호출(anthropic·openai·gemini), P0-cost, F-46f1eb·F-036185, 하네스 L-nnn(verify-impl 6번).

## 재개 시 읽을 카드 (이것만)
- `packages/P4-pilot-eval/01-plan.md`(U1~U9 64~72행, 결정 표 ~226행, 278행 R-5·R-6), `02-plan-verify.md` §3·§4, `03-log.md` 마지막 항목, `docs/backlog.md` 61행
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
