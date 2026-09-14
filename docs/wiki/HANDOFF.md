# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-14 16:58 (**P3-llm-providers U1 구현 완료·커밋 승인됨 — 커밋 실행 중.** 전건 DB 재실행 873 passed/skip 0. 다음 U2 위임 승인됨(L-004))
active: **P3-llm-providers** | frozen: none | 브랜치: dev = 025a7c4(origin/dev = 5a1bcbe, 미푸시 2), main = 0e3447a. **진행 중**: U1 커밋(`.claude/commit-draft.txt` 초안 있음 — 승인 → `approve-commit.sh` → `git add` 명시 경로: `app/er/judge.py app/settings.py .env.example tests/test_er_judge.py tests/test_er_smoke.py scripts/er_smoke.py scripts/baseline_smoke.py` + evidence `20260914-1620-u1-*.txt` 11개 + `20260914-1655-u1-pytest-full-db.txt` + `03-log.md` `05-remediation.md` HANDOFF journal → `git commit -F`). 커밋 뒤 03-log U1 항목 `pending` 은 다음 커밋에서 해시로.

## 지금 어디까지
- **U1 완료(미커밋)** — `JUDGES` 단일 표(anthropic·openai·gemini 자리표시 `_gemini_reserved`)·`enabled_providers(env)`(R-4)·`select_provider(env)`(유일한 거부 자리, U3 가 import)·`judge_from_env` 2단계, `LLM_PROVIDER="openai"`·`LLM_PROVIDERS_ENABLED_DEFAULT` 단일 출처, `.env.example` 이름만, 테스트 신규 11 + R-1(a)(d) 개명 2. **계획 밖**: `tests/test_er_smoke.py` 기존 2건 setenv 키 이름(같은 원인) → 소견 F-7afd7f(해소, 04-review 대조 목록 포함). evidence 11개: `app/` diff 2줄, tools_check 7/7, 전체 DB 미연결 641/232 skip → 사용자 Docker 기동 후 재실행 **873 passed / 0 failed / 0 skipped**(`20260914-1655-u1-pytest-full-db.txt`).
- **계획 승인(2026-09-14)** — verifier 02-plan-verify 통과(FAIL 0/WARN 11 의도), 권고 R-1~R-9. D11 카드(등록표·스위치·기본 openai). 05-remediation 열림 9(registry 의도된 WARN, 04-review §5), 해소 3(F-81e3e5·F-11fbee·F-7afd7f).
- **U2 위임 프롬프트에 넣을 것**: 01-plan U2(49행)·82~96행(오류 매핑 표)·124행(변환 불가 시 멈춤)·결정 3(`GEMINI_MODEL` 기본 없음→`InvalidValue`)·4(어휘 6종 재사용)·5(`requirements.txt` 핀 `google-genai==<pip show 실측>`), D11 (d)(e), **R-6 실측 evidence 3건 먼저**(`pip show google-genai`, `google.genai.errors` 대문자 이름, `types.Schema.model_fields`; nullable integer·`s_llm` 0~1 표현 불가면 멈추고 보고), R-2(`GEMINI_API_KEY` 미설정 `genai.Client()` 예외 클래스명 evidence, 더미 키 규약), R-1(b) `test_judge_from_env_gemini_is_reserved_not_implemented` 삭제·대체(gemini 양성 + `GEMINI_MODEL` 미설정 `InvalidValue`), `_gemini_reserved` → `GeminiJudge`, 스텁으로 호출 횟수·재시도 단언, `RESOLUTION_SCHEMA` 도 같은 변환기(U3 가 재사용). `app/` 수정은 `judge.py`(+`requirements.txt`)뿐. HANDOFF·journal·registry 손대지 말 것.
- **P3-baselines·P1-pilot-dataset·P3-er 완료** — P4 인계: `packages/P3-baselines/04-review.md` §7 15항, `packages/P1-pilot-dataset/04-review.md` §7 13항. P4 01-plan 초안 701fb8d — P3-llm-providers 04-review 완료 해시를 P4 01-plan 5행에 채운 뒤 P4 02-plan-verify.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(스모크 03), F-46f1eb, F-036185, F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 필요 — 2026-09-14 16:55 켜짐), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`. 설치: anthropic 1.4.0·openai 2.33.0, `google-genai` 미설치(U2 R-6).

## 바로 다음에 할 것 (순서대로)
1. **U1 커밋**(승인됨) → 마커 → 명시 경로 add → `git commit -F`.
2. **U2 위임**(L-004 승인됨 2026-09-14) → `approve-commit.sh --stage backend-agent` → backend-agent 1회(위 항목) → 검토 → `/commit`(Refs D11).
3. U3(`GeminiSingleCaller`, `select_provider`·`JUDGES` import, `CALLERS` 키 = `JUDGES` 키 단언, R-1(c) parametrize) → U4(문서·R-7 gemini 키 행·R-8 registry 비고·R-9(e) user-setup 01·전건 evidence) → `/devlog done`(verifier 04-review, R-9(b) "실호출 검증 공급자 0/3"). 그 다음 `git push origin dev` → L-003 → P4 02-plan-verify.
4. 보류: 사용자 스모크 03·08(gemini 포함) 카드, P0-cost, F-46f1eb·F-036185, 하네스 L-nnn(`verify-impl.sh` 포트).

## 재개 시 읽을 카드 (이것만)
- `packages/P3-llm-providers/03-log.md` 마지막 2항목, `01-plan.md` 49~51행·82~96행·결정 확정 표, `02-plan-verify.md` R-1~R-9, `05-remediation.md` F-7afd7f, `decisions/D11-llm-provider-registry.md`
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `docs/backlog.md` 51~56행, `docs/user-setup/README.md`
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- 없음(U1 커밋·U2 위임 승인됨). Docker Desktop 현재 켜짐.
- 하네스 L-nnn 후보: `verify-impl.sh` 포트 전달.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. Docker 가 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. `git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다. Bash 문자열에 마커 파일명·훅 금지 문구 금지 — 문서 수정은 scratchpad 스크립트 + python 또는 Write. `.env` 존재 확인 금지. `git checkout --` 금지.
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. registry 는 이 패키지에서 새 행 없이 기존 행 비고만(R-8, U4). 기존 테스트를 고쳐 통과시키면 소견으로 기록(F-7afd7f 선례).
- 서브에이전트가 만든 pending 해시는 다음 커밋에서 메인 세션이 정리. 서브에이전트에게 HANDOFF·journal 금지 명시. `app/` docstring 에 "evaluation" 문자열 금지(`test_app_does_not_mention_evaluation_package_at_all`).
