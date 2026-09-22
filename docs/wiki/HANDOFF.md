# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-22 19:05 (**[P4b-er-redesign 계획 승인 — START 커밋 승인 대기]** verifier 02-plan-verify `결과: 통과`(verify-plan FAIL 0/WARN 22 의도, 점검표 8/8, 사실 주장 (a)~(f) 6/6 코드 확인, 회귀 3종 baseline 3 passed, 권고 R-1~R-9, 보류 0). 사용자 계획 승인 19:00 + R-3·R-9 01-plan 반영 → 02 `승인: 사용자 (2026-09-22)`, CURRENT `active: P4b-er-redesign`, `03-log.md` 생성(START 항목 `pending`), journal VERIFY·START. 미커밋: `packages/P4b-er-redesign/`(01·02·03·05·evidence 7) + backlog 65행(types.py) + CR-001 36행(결정 I) + journal·HANDOFF. **다음 = START 커밋(초안 작성됨) → U0(메인 세션: SKILL.md 22·36·39행 D12·D13 정합 + "권위는 S3.3·D12·D13" 한 줄, CR-001 §2 파일 목록 갱신 이력, 하네스 문서 커밋) → U1 backend-agent 위임 승인(L-004).** 결정: A(i) ask 강등+relaxed_pass 예외·B `ER_PENALIZED_MERGE_POLICY`·C 완화 트리거 "감점 없는 후보 0"·D recheck weights_effective·E $5/1회·F 결정 K 불변·G failure_cases §13·H meta 2키·I stamp 사본. **U4→U5 순서 필수**(recheck 가 새 trace 거부 → 유료 실행 rc=1). 기준선 `raw-20260922-042440.jsonl.gz`·`metrics.json`(25e16dd6…) 덮어쓰기 금지 — U5 전에 stamp 사본 커밋.)
active: **P4b-er-redesign**(계획 승인 2026-09-22) | frozen: none | 브랜치: dev = **f01ea35**(dev = e4109cc; origin/dev = f01ea35, 미푸시 2 · main = 3c6108d, 승격 대기 17 — 마지막 e4109cc·adf9f1b·f01ea35, 그 앞 ea1bbb2·ef18143·750f11b·2ebf061·1c84d35, 그 앞 9: b164f36·fb81234·a97521b·ee124b7·a59ecb4·dd6a996·0283ac0·e7f0a9c·1a5643b). 경위: verifier 02-plan-verify 1차(09-17 09:30) 보류 H-1 → 사용자 (a) 지배 기준·R-1~R-4 → 01-plan 개정 → verifier 2차(09:50) **통과**(FAIL 0/WARN 3 의도, 점검표 8/8) → 2026-09-18 사용자 재개 결정·계획 승인 → 02 `승인: 사용자 (2026-09-18)`, CURRENT active, `03-log.md` 생성(pending 항목 1), journal VERIFY×2·DECISION·START. backlog 15행 흡수 표기는 이미 있음. START 커밋 **b164f36**(18파일, 미푸시 — dev 가 origin/dev 보다 1 앞). 03-log START 항목 `pending` → b164f36 은 다음 커밋에 포함.

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 1/3(openai)** — 스모크 03(2ebf061)·08(750f11b) 완료, F-87c597 해소, R4 "실호출 확인". anthropic·gemini 는 선택(미실행). U7 실 실행 750f11b 기준 완료(결과는 위 갱신 줄).
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-46f1eb, F-036185(F-87c597 은 750f11b 에서 해소), F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`, JSON 읽기 `PYTHONUTF8=1`. 사용자 `!` 실행은 셸이 매번 새로 떠서 `set -a; . ./.env; set +a;` 접두 필요(키). `.env` 의 `DATABASE_URL` 은 사용자가 2026-09-22 에 5433 으로 수정(`app/config.py` 규칙 1: DATABASE_URL 이 POSTGRES_PORT 보다 우선 — U7 1·2차 실패 원인). 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **START 커밋**(초안 `.claude/commit-draft.txt`, 사용자 승인 대기): `packages/P4b-er-redesign/{01-plan,02-plan-verify,03-log,05-remediation}.md` + `evidence/`(7) + `docs/backlog.md` + `docs/wiki/changes/CR-001.md` + `CURRENT.md` + journal + HANDOFF. 커밋 뒤 03-log START 항목 `pending` → 해시는 다음 커밋에서.
2. **U0**(메인 세션, 활성 패키지 안 — 하네스 문서 정합, R-7): `.claude/skills/entity-resolution/SKILL.md` 22행(배제→감점 D13)·36행(`s_rule` 미측정 규약)·39행(산식 D12) + "권위는 S3.3·D12·D13, 이 카드는 절차 미러" 한 줄; `changes/CR-001.md` §2 파일 목록에 `types.py`·`er_smoke.py`·SKILL.md 갱신 이력 한 줄 → /commit(Refs CR-001 D12 D13 S3.3).
3. **U1** backend-agent 위임 승인(L-004) → `combine()` 재정규화·`_breakdown` weights_effective/rule_checked·강제 경로·`er_smoke.py:109` + 테스트(`test_er_confidence.py` 293행 원식 수치 유지) → /commit. 이어 U2(rules.py 감점, R-4 확정)·U3(pipeline 보수 분기·ER_PENALIZED_MERGE_POLICY·회귀 3종, R-8) 단위마다 승인·커밋.
4. U4 eval-agent(recheck weights_effective·curve/calibration meta·proposed.detail penalized_by·전체 pytest, R-5) → **U5 전 기준선 stamp 사본 커밋(결정 I)** → U5 dry-run + 사용자 실 실행 1회(`evidence/<ts>-u5-real-run.txt`, `.env` 로드 접두, Docker 5433) → U6 failure_cases §13 → U7 기계 검증·registry(기존 행 비고 확장)·README·카드 10 → verifier 04-review 게이트(결정 K 그대로, sc-015/sc-007 별도, R-6). 통과 시 P5.
5. 보류: dev 푸시(미푸시 3+ — 승격은 사용자, L-003), 하네스 L-nnn(R-2 verify-plan 5번 불릿 의존·03-log Refs=커밋 Refs), 러너 `safe_summary` FIX(U4 에 흡수 가능), 09 카드 §2, anthropic·gemini 스모크, F-46f1eb·F-036185, P10 인계.

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
