# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-14 16:05 (**P3-llm-providers 착수.** 사용자 재개 결정 '이어서 완료' → 계획 승인 → U1 backend-agent 위임 승인(L-004). 계획 커밋 진행 중)
active: **P3-llm-providers** | frozen: none | 브랜치: dev = 701fb8d(origin/dev = 5a1bcbe, 미푸시 1 + 이번 계획 커밋), main = 0e3447a. **진행 중**: (1) 계획 커밋(`.claude/commit-draft.txt`, 승인 대기 → 마커 → `git add` 명시 경로 → `git commit -F`) → (2) `approve-commit.sh --stage backend-agent` → backend-agent U1 1회 위임 → 결과 검토 → `/commit`(U1) → U2(R-6 실측 3건 먼저)·U3·U4 각각 L-004 승인·커밋 → verifier 04-review.

## 지금 어디까지
- **P3-llm-providers 계획 승인(2026-09-14)** — verifier(fable) 02-plan-verify 통과(FAIL 0/WARN 11 의도 = registry 기존 행 소견 9건, 점검표 8/8, 보류 0, 권고 R-1~R-9). `승인: 사용자 (2026-09-14)`, CURRENT active, 03-log 첫 항목(pending), journal START. D11 카드 신설(등록표 `JUDGES`·`LLM_PROVIDERS_ENABLED`·기본 `LLM_PROVIDER=openai`·`FakeJudge` 표 밖·`GEMINI_MODEL` 기본 없음·오류 어휘 6종), D03 파급에 D11 상호참조. 05-remediation 열림 9(전부 의도된 WARN, 04-review §5 에서 닫음).
- **U1 위임 프롬프트에 넣을 것**: 01-plan U1(48행)·판정 표(65~78행)·D11 "코드에서 지켜야 할 것" 5문장·R-1(바뀌는 기존 테스트 4건만: `test_judge_from_env_defaults_to_anthropic`→openai 등, 그 밖 기존 테스트 diff 0)·R-3(스위치·공급자 같은 `env` 매핑)·R-4(파싱: 쉼표 분리→strip().lower()→빈 항목 제거, 미설정/공백만=전체 켬)·R-5(`grep -c "^JUDGES" app/er/judge.py`=1, `_KNOWN_PROVIDERS` 0)·R-7(`scripts/er_smoke.py`·`baseline_smoke.py` `_REQUIRED_KEY_BY_PROVIDER` gemini 행, `tests/test_er_smoke.py` — U1 또는 U4)·R-9(Refs·커밋에 D11). `app/` 수정은 `judge.py`·`settings.py` 2파일뿐. `FakeJudge` 표 밖. evidence `packages/P3-llm-providers/evidence/<ts>-u1-*.txt`. HANDOFF·journal 손대지 말 것.
- **P3-baselines 완료(2026-09-11)**, **P1-pilot-dataset 완료(2026-09-10)**, **P3-er 완료(2026-09-06)** — P4 인계: `packages/P3-baselines/04-review.md` §7 15항, `packages/P1-pilot-dataset/04-review.md` §7 13항. P4-pilot-eval 01-plan 초안은 701fb8d(결정 A~K 확정, 실행 OpenAI 1벌) — P3-llm-providers 04-review 완료 해시를 P4 01-plan 5행에 채운 뒤 P4 02-plan-verify.
- 이전 패키지 열린 소견: P3-er F-87c597 R4 실호출(사용자 스모크 03 카드), F-46f1eb 더미 키 규약, F-036185 bool id 방어, F-251dc2·F-bdd6c5(P4 결정). P2 F-4d2507 `DELETE /persons/{id}`(P5/P8), F-4d8d96 tool_error rollback(P5), F-c7078e mako Refs.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 필요), 스키마 0001(head), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8` + 리다이렉트. 설치: anthropic 1.4.0·openai 2.33.0, `google-genai` 미설치(U2 첫 단계 설치·실측 R-6).

## 바로 다음에 할 것 (순서대로)
1. **계획 커밋**(초안 `.claude/commit-draft.txt`) — AskUserQuestion 승인 → `approve-commit.sh` → `git add` 명시 경로(D11·D03·02-plan-verify·05-remediation·evidence 3·03-log·CURRENT·HANDOFF·journal) → `git commit -F`. 커밋 뒤 03-log `pending` 은 다음 커밋에서 해시로.
2. **U1 위임**: `bash .claude/hooks/approve-commit.sh --stage backend-agent` → backend-agent 1회(위 프롬프트 항목). 돌아오면 evidence·diff 검토(`git diff --name-only -- app/` = 2줄) → `/commit`(`feat(P3-llm-providers): U1 …`, Refs 에 D11).
3. U2(R-2·R-6 실측 evidence 3건 → `GeminiJudge`·`requirements.txt` 핀·스텁 테스트) → U3(`GeminiSingleCaller`, 등록표 import) → U4(문서·evidence·registry 비고 R-8) → `/devlog done`(verifier 04-review, R-9(b) "실호출 검증 공급자 0/3" 명기). 그 다음 `git push origin dev` → L-003 멈춤 → P4-pilot-eval 02-plan-verify.
4. 보류: 사용자 스모크 03·08(·09 gemini) 카드(키 필요, 사용자 몫), P0-cost(AWS Budgets), F-46f1eb·F-036185 소FIX, 하네스 L-nnn(`verify-impl.sh` 포트 전달).

## 재개 시 읽을 카드 (이것만)
- `packages/P3-llm-providers/01-plan.md`(U 줄 48~51·판정 표 65~78·결정 확정 표), `02-plan-verify.md` §3 권고 R-1~R-9, `decisions/D11-llm-provider-registry.md`, `03-log.md` 마지막 항목
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `docs/backlog.md` 51~56행, `docs/user-setup/README.md`(사용자 몫)
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- 계획 커밋 승인(진행 중). 이후 U 단위마다 커밋 승인·위임 승인(L-004). 푸시는 패키지 완료 후 한 번(사용자 결정).
- 하네스 L-nnn 후보: `verify-impl.sh` 포트 전달(권고 8, 두 번 반복된 한계).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번. Docker Desktop 이 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. **`git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다**. Bash 문자열에 마커 파일명·훅 금지 문구(볼륨 삭제, 강제 푸시, DROP, 환경변수 전체 출력 단어) 금지 — 문서 수정은 scratchpad 스크립트 + python 실행 또는 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 만든 커밋 하나, 후속 수정은 비고(R-8: 이 패키지는 새 행 없이 기존 행 비고만).
- 서브에이전트가 만든 pending 해시·상태 줄은 다음 커밋에서 메인 세션이 정리한다. 서브에이전트에게 HANDOFF·journal 은 건드리지 말라고 명시한다. evidence 를 쓰는 테스트는 반드시 환경변수 게이트(`ER_EVIDENCE_STAMP` 규약). 기존 테스트를 고쳐 통과시키면 그 자체가 findings(01-plan 127행) — R-1 의 4건만 예외.
- 계획서 행 번호는 "결정 확정" 블록 삽입으로 밀릴 수 있다. 카드 인용은 문장으로도 대조한다.
