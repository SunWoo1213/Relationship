# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-22 13:50 (**[U7 실 실행 완료 — 게이트 미달, 커밋 대기] 사용자 셸 3차 실행 rc=0(1·2차는 `.env` DATABASE_URL 5432 → DB 접속 실패·LLM 0회·과금 0; 사용자가 `.env` 를 5433 으로 수정해 근본 해결). 실측: openai gpt-4o-mini-2024-07-18 · text-embedding-3-small · 40/40 · 7050행 · 호출 339 · tokens 130,240/12,617 · $0.0271 · traces 재계산 diff 0 · raw gz 177,043 B. **게이트 `0.8 ['embedding_only'] True False` = 미달**: proposed 오병합 1/132·미검출 1/132·ask(identity) 79/132(59.8%) vs embedding_only 0·1·31(23.5%) → 지배됨(오병합 0<1, 미검출 동률). D10 방향 9쌍 위반 0. 판정 표 나머지 전부 ✔(evidence `20260922-1340-u7-judgment.txt`). **재실행 금지(원칙8) → U8 실패 케이스 분석 + `/devlog change` 후보, P5 미착수(결정 K 개정 (a)).** 이번 커밋 대상: raw `.jsonl.gz`+traces(reports/pilot/), reports/metrics.json·calibration.json·curve.csv·eval.md, cost_estimate §3·§4 실측, registry +6, evidence 4(실패 2·성공 1·판정 1), 03-log·HANDOFF·journal. **add 금지**: 평문 `reports/pilot/raw-….jsonl`(7.5MB)·`metrics-stage.json`. 결함 기록(코드 미수정): 카드 10 판정 명령 encoding 미지정(cp949 UnicodeDecodeError → `PYTHONUTF8=1`), 러너가 접속 전 `safe_summary` 미출력(FIX 후보), stamp UTC.]
active: **P4-pilot-eval** | frozen: none | 브랜치: dev = **750f11b**(origin/dev·main = 3c6108d, 미푸시 12 — 마지막 750f11b, 그 앞 2ebf061·1c84d35, 그 앞 9: b164f36·fb81234·a97521b·ee124b7·a59ecb4·dd6a996·0283ac0·e7f0a9c·1a5643b). 경위: verifier 02-plan-verify 1차(09-17 09:30) 보류 H-1 → 사용자 (a) 지배 기준·R-1~R-4 → 01-plan 개정 → verifier 2차(09:50) **통과**(FAIL 0/WARN 3 의도, 점검표 8/8) → 2026-09-18 사용자 재개 결정·계획 승인 → 02 `승인: 사용자 (2026-09-18)`, CURRENT active, `03-log.md` 생성(pending 항목 1), journal VERIFY×2·DECISION·START. backlog 15행 흡수 표기는 이미 있음. START 커밋 **b164f36**(18파일, 미푸시 — dev 가 origin/dev 보다 1 앞). 03-log START 항목 `pending` → b164f36 은 다음 커밋에 포함.

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 1/3(openai)** — 스모크 03(2ebf061)·08(750f11b) 완료, F-87c597 해소, R4 "실호출 확인". anthropic·gemini 는 선택(미실행). U7 실 실행 750f11b 기준 완료(결과는 위 갱신 줄).
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(스모크 03), F-46f1eb, F-036185, F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`. 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **U7 결과 커밋**(초안 작성됨 — 사용자 승인 대기). 커밋 후 03-log 마지막 항목 `pending` → 해시는 다음 커밋에서.
2. **U8 실패 케이스 분석** — `reports/failure_cases.md`. eval-agent 위임은 AskUserQuestion 승인 → `approve-commit.sh --stage eval-agent` → Agent 1회(L-004). 입력: `reports/metrics.json`·`reports/pilot/raw-20260922-042440.jsonl.gz`·`traces-20260922-042440.jsonl`·`data/scenarios/*.json`. 내용(01-plan U8 72행): 오병합 1건 전문·미검출 1건·`no_matched` 25/`no_candidates` 5 유형·ask_user(identity) 59.8% 구성·함정 12건 거동·카테고리별·**embedding_only 가 지배한 이유 = S3.3 어느 단계인가**(LLM 판정 s_llm 이 확신도를 깎는가? 규칙 필터?) → `/devlog change` 후보. `data/` 수정 금지, 라벨 의심은 별도 검수 기록. 결론은 "방향·유형까지"(40건).
3. U8 뒤: 카드 10·01-plan 판정 명령 encoding 문구 수정(docs), 러너 `safe_summary` 출력 FIX 후보(사용자 결정), U9 registry 해시 확정 → `/devlog done`(verifier 04-review, 결과는 "부분완료 + 실패 케이스 분석" 원칙8) → `/devlog change`(S3.3 재설계) 사용자 결정. P5 이후 시작 금지.
4. 보류: 09 카드 §2 결정 10개(P9 전), anthropic·gemini 스모크(선택), P0-cost, F-46f1eb·F-036185, 하네스 L-nnn(verify-impl 6번), `.gitignore` 에 `reports/pilot/*.jsonl`·`metrics-stage.json` 추가 여부.

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
