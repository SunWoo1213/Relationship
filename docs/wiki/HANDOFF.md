# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-15 15:20 (**U4 커밋 중(이 커밋). U1~U4 전부 완료 → 다음은 `/devlog done`(verifier 04-review 위임 승인, L-004)**)
active: **P3-llm-providers** | frozen: none | 브랜치: dev = U4 커밋(origin/dev = 5a1bcbe, 미푸시 6: 701fb8d 025a7c4 c01381d cf01e9f 7b94a69 + U4), main = 0e3447a. **진행 중: 없음**(U1~U4 커밋됨). 미커밋: 없음(이 커밋 뒤 journal COMMIT 줄만). **재개 절차(새 세션)**: `/devlog resume` → AskUserQuestion **verifier 04-review 위임 승인**(L-004) → `bash .claude/hooks/approve-commit.sh --stage verifier` → verifier 1회(verify-impl.sh + 04-review, 아래 '04-review 위임에 넣을 것') → 사용자 완료 승인 → `CURRENT active: none` → journal DONE → `/commit` → `git push origin dev` → L-003 멈춤.

## 지금 어디까지
- **U4 완료(이 커밋)** — README 두 절·user-setup 01(기본/선택 반전 R-9(e), `GEMINI_*` 사용 가능, `LLM_PROVIDERS_ENABLED`)·03·08(`--provider anthropic|gemini` 줄, 결정 7 (i))·D11 갱신 이력·registry 비고 8행(새 행 0, R-8)·R-7(`scripts/er_smoke.py`·`baseline_smoke.py` gemini 키 행+help, `tests/test_er_smoke.py` +1건). `.env.example` 변경 없음(U1 반영 확인). evidence `20260915-1500-u4-*` 8건: **918 passed / 0 / 0 skip**, er 회귀 91, parity 46, tools_check 7/7, app-diff 2줄, registry-r8 8개 모두 1, smoke gemini 키 없음 rc=2. backend-agent 판단 3건(03-log): `.env.example` 무변경 처리, Docker 재기동, exit-2 evidence 는 `unset` 서브셸.
- **U3 완료(7b94a69)** — `GeminiSingleCaller`, `CALLERS` 는 `JUDGES` 키 파생, `caller_from_env` 는 `select_provider` 만. 917 passed. backend-agent 판단 3건 03-log(04-review 확인 대상).
- **U2 완료(cf01e9f)** — `GeminiJudge`·`_to_gemini_schema`·`call_with_gemini_error_mapping`(어휘 6종, timeout·connection 만 1회 재시도). 896 passed. 판단 2건 03-log.
- **U1 완료(c01381d)** — `JUDGES`·`enabled_providers`·`select_provider`·`judge_from_env` 2단계, 기본 openai. 소견 F-7afd7f(해소). 873 passed.
- **계획 승인(2026-09-14)** — verifier 02-plan-verify 통과(FAIL 0/WARN 11 의도), 권고 R-1~R-9. 05-remediation 열림 9(registry 의도된 WARN → 04-review §5 에서 R-8 명령 evidence `u4-registry-r8.txt` 로 닫음), 해소 3.
- **04-review 위임에 넣을 것**: 패키지 id, 읽을 것 = `01-plan.md`(수용 기준·결정 확정 표·U1~U4 행), `02-plan-verify.md` R-1~R-9, `03-log.md` 전체(판단 2+3+3건 확인), `05-remediation.md`, `decisions/D11`, `docs/backlog.md` 51행, evidence 전체(`u1-*`~`u4-*`), `.claude/gitlog.md`. verifier 가 직접 `bash .claude/scripts/verify-impl.sh P3-llm-providers | tee evidence/<ts>-verify-impl.txt`(DB 포트 5433 — `verify-impl.sh` 포트 전달이 안 되면 evidence 에 그 사실 기록, L-nnn 후보), 부정 케이스 직접 실행. §5 registry 는 R-8 명령. §6 에 R-9(b) "실호출로 검증된 공급자 0/3(F-87c597 열림, R4 꼬리표는 P4 가 닫는다)" 그대로. R-9(c) proposal 상단 안내문 갱신 여부는 H 로 올려 사용자 결정. `git diff --name-only 025a7c4..HEAD -- app/ scripts/ tests/ requirements.txt` 를 03-log 선언 목록과 대조(R-7). 검토자 줄 `verifier (fable)`. HANDOFF·journal·코드·계획 수정 금지.
- **P3-baselines·P1-pilot-dataset·P3-er 완료** — P4 인계: `packages/P3-baselines/04-review.md` §7 15항, `packages/P1-pilot-dataset/04-review.md` §7 13항. P4 01-plan 초안 701fb8d — P3-llm-providers 04-review 완료 해시를 P4 01-plan 5행에 채운 뒤 P4 02-plan-verify.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(스모크 03), F-46f1eb, F-036185, F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop — 2026-09-15 backend-agent 가 재기동, 켜짐), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`. 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **`/devlog done`**: AskUserQuestion verifier 04-review 위임 승인(L-004) → `--stage verifier` → verifier 1회(verify-impl + 04-review) → 소견 있으면 루프(FAIL 은 backend-agent 재위임도 L-004) → 사용자 완료 승인 → `CURRENT active: none` → backlog 체크 → journal DONE → `/commit`.
2. `git push origin dev`(사용자 승인) → L-003 멈춤(승격/수정/보류) → P4 01-plan 5행에 04-review 해시 → P4 02-plan-verify(verifier, L-004).
3. 보류: 사용자 스모크 03·08(gemini 포함) 카드 실호출, P0-cost, F-46f1eb·F-036185, 하네스 L-nnn(`verify-impl.sh` 포트).

## 재개 시 읽을 카드 (이것만)
- `packages/P3-llm-providers/03-log.md` 마지막 2항목, `01-plan.md` 수용 기준·결정 확정 표, `02-plan-verify.md` R-7·R-8·R-9, `05-remediation.md`, `decisions/D11-llm-provider-registry.md`
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `docs/backlog.md` 51~56행
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- verifier 04-review 위임 승인(L-004) — 다음 첫 질문.
- R-9(c): `docs/proposal.md` 상단 안내문에 "기본 LLM 공급자 openai(D11)" 한 줄을 넣을지 — 04-review H 로 올라오면 사용자가 정한다(`/devlog change` 여부 포함).
- 하네스 L-nnn 후보: `verify-impl.sh` 포트 전달.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. Docker 가 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. `git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다. Bash 문자열에 마커 파일명·훅 금지 문구·환경변수 전체 출력(`environ` grep·`env -u` 포함) 금지 — 문서 수정은 scratchpad 스크립트 + python 또는 Write. `.env` 존재 확인 금지. `git checkout --` 금지.
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. registry 는 이 패키지에서 새 행 없이 기존 행 비고만(R-8). 기존 테스트를 고쳐 통과시키면 소견으로 기록(F-7afd7f 선례).
- 서브에이전트가 만든 pending 해시(03-log U4)는 다음 커밋(done)에서 메인 세션이 정리. 서브에이전트에게 HANDOFF·journal 금지 명시. `app/` docstring 에 "evaluation" 문자열 금지(`test_app_does_not_mention_evaluation_package_at_all`).
