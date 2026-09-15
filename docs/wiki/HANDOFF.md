# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-15 12:15 (U3 GeminiSingleCaller 구현 완료·검토 완료 — **커밋 승인 대기**. 다음: `/commit` → U4 위임(L-004))
active: **P3-llm-providers** | frozen: none | 브랜치: dev = cf01e9f(origin/dev = 5a1bcbe, 미푸시 4: 701fb8d 025a7c4 c01381d cf01e9f), main = 0e3447a. **진행 중: U3 커밋 대기** — 미커밋: `evaluation/resolvers/llm_single.py`·`tests/test_baseline_llm_single.py`·evidence `20260915-1200-u3-*` 9개 + `20260914-1720-u2-import-module.txt`(U2 누락분)·03-log(U3 항목 + U2 해시)·HANDOFF·journal. **재개 절차**: 미커밋이 남아 있으면 `/devlog resume` → 사용자에게 목록 → `/commit`(초안은 03-log 마지막 항목 그대로) → (1) AskUserQuestion **U4 위임 승인**(L-004) → `bash .claude/hooks/approve-commit.sh --stage backend-agent` → backend-agent 1회(아래 'U4 위임 프롬프트') → 검토 → 03-log U4 → `/commit` → (2) AskUserQuestion **verifier 04-review 위임 승인** → `--stage verifier` → `/devlog done`.

## 지금 어디까지
- **U3 완료(커밋 대기)** — `GeminiSingleCaller`(`GeminiJudge` 규약 동일, `_to_gemini_schema`·`call_with_gemini_error_mapping` 재사용 `is` 테스트), `CALLERS` 는 `JUDGES` 키 순회, `caller_from_env` 는 `select_provider` 만(자체 거부 0, D11 (b)). R-1(c) parametrize 이동. 전체 **917 passed / 0 / 0 skip**, parity 46, er 회귀 91, tools_check 7/7, `app/` 0줄. backend-agent 판단 3건은 03-log 에(04-review 확인 대상).
- **U2 완료(cf01e9f)** — `GeminiJudge`·`_to_gemini_schema`·`call_with_gemini_error_mapping`(어휘 6종, timeout·connection 만 1회 재시도, `retry_options` 미채택 근거 evidence). 896 passed.
- **U1 완료(c01381d)** — `JUDGES`·`enabled_providers`·`select_provider`·`judge_from_env` 2단계, 기본 openai. 소견 F-7afd7f(해소). 873 passed.
- **계획 승인(2026-09-14)** — verifier 02-plan-verify 통과(FAIL 0/WARN 11 의도), 권고 R-1~R-9. D11 카드. 05-remediation 열림 9(registry 의도된 WARN, 04-review §5 에서 닫음), 해소 3.
- **U4 위임 프롬프트에 넣을 것**: 01-plan U4(51행) 그대로 — `.env.example` 주석(이름만), README 두 절, `docs/user-setup/01-env-keys.md` `GEMINI_*` 행·활성 스위치(R-9(e)), 03·08(또는 09, 결정 7) 스모크 카드 `--provider gemini`, D11 카드 갱신 이력 1줄(결정 6), `registry.md` **기존 행 비고만**(R-8, 새 행 금지), R-7 gemini 키 행. evidence `<ts>-u4-*`: 전체 `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs`, `tests/test_er_judge.py tests/test_er_pipeline.py`, `tests/test_baseline_parity.py`(46), `python scripts/tools_check.py` 7/7, `git diff --name-only 701fb8d..HEAD -- app/`(= `app/er/judge.py`·`app/settings.py` 2줄 + `requirements.txt` 는 app 밖). 코드 수정 없음(문서·evidence 만). HANDOFF·journal 금지, registry 는 비고 열만.
- **P3-baselines·P1-pilot-dataset·P3-er 완료** — P4 인계: `packages/P3-baselines/04-review.md` §7 15항, `packages/P1-pilot-dataset/04-review.md` §7 13항. P4 01-plan 초안 701fb8d — P3-llm-providers 04-review 완료 해시를 P4 01-plan 5행에 채운 뒤 P4 02-plan-verify.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(스모크 03), F-46f1eb, F-036185, F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop — 2026-09-15 켜짐), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`. 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **U3 `/commit`**(사용자 승인) — 초안: 03-log 마지막 항목. `git add` 명시 경로: `evaluation/resolvers/llm_single.py tests/test_baseline_llm_single.py docs/wiki/packages/P3-llm-providers/03-log.md docs/wiki/packages/P3-llm-providers/evidence/20260915-1200-u3-*.txt docs/wiki/packages/P3-llm-providers/evidence/20260914-1720-u2-import-module.txt docs/wiki/HANDOFF.md docs/wiki/journal.md`.
2. **U4 위임**(L-004 AskUserQuestion) → backend-agent 1회 → 검토 → 03-log U4 → `/commit`.
3. **`/devlog done`**(L-004 verifier 승인 → `--stage verifier` → verify-impl + 04-review, R-9(b) "실호출 검증 공급자 0/3") → 사용자 완료 승인 → `CURRENT active: none` → `/commit` → `git push origin dev` → L-003 멈춤 → P4 02-plan-verify.
4. 보류: 사용자 스모크 03·08(gemini 포함) 카드, P0-cost, F-46f1eb·F-036185, 하네스 L-nnn(`verify-impl.sh` 포트).

## 재개 시 읽을 카드 (이것만)
- `packages/P3-llm-providers/03-log.md` 마지막 2항목, `01-plan.md` 51행(U4)·결정 확정 표, `02-plan-verify.md` R-7·R-8·R-9, `05-remediation.md`, `decisions/D11-llm-provider-registry.md`
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `docs/backlog.md` 51~56행, `docs/user-setup/README.md`·`01-env-keys.md`
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- U3 커밋 승인 → U4 위임 승인(L-004) → verifier 04-review 위임 승인(L-004).
- 하네스 L-nnn 후보: `verify-impl.sh` 포트 전달.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. Docker 가 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. `git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다. Bash 문자열에 마커 파일명·훅 금지 문구·환경변수 전체 출력(`environ` grep 포함) 금지 — 문서 수정은 scratchpad 스크립트 + python 또는 Write. `.env` 존재 확인 금지. `git checkout --` 금지.
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. registry 는 이 패키지에서 새 행 없이 기존 행 비고만(R-8, U4). 기존 테스트를 고쳐 통과시키면 소견으로 기록(F-7afd7f 선례).
- 서브에이전트가 만든 pending 해시는 다음 커밋에서 메인 세션이 정리. 서브에이전트에게 HANDOFF·journal 금지 명시. `app/` docstring 에 "evaluation" 문자열 금지(`test_app_does_not_mention_evaluation_package_at_all`).
