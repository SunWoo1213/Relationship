# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-10 14:20 (U2 어댑터 완료 — eval-agent 산출물·evidence 확인, /commit 승인 대기)
active: **P3-baselines** | frozen: none | 브랜치: dev = **05d90f0**(U1), origin dev = main = 0e3447a(미푸시 1, U2 커밋 후 2). **U1 완료(05d90f0)**. **U2 완료(커밋 대기)**: `evaluation/resolvers/proposed.py`(`"proposed"` 등록)·`resolvers/__init__.py` import·`tests/test_baseline_proposed.py` 20건, evidence `20260910-1411-u2-{pytest(59),regression(54),isolation,pytest-all(526)}.txt` 모두 skip 0·`app/` 0줄. eval-agent 판단 4건은 03-log 14:20 항목 → verifier 04-review 확인 대상. **다음**: /commit(사용자 승인) → **U3 완전일치 2변형**(`exact_raw`·`exact_norm`, 결정 C(iii)·R-8, 01-plan U3 행) eval-agent(L-004) → U4 → U5(결정 I·J, R-4) → U6(R-6·R-7) → U7(R-1) → U8(R-1·R-2) → verifier. DB 5433 UP(Docker Desktop 켜짐). 결정 A~J = 01-plan "결정 확정" 2블록, 권고 R-1~R-9 = 02-plan-verify §3.

## 지금 어디까지
- **P1-pilot-dataset 완료(2026-09-10)** — U1 스키마·검증기(1e1320c) → U2 promotion·alias(09875aa) → FIX 시점 무관 테스트(baee71e) → U3 pronoun·normal(aa6ecfc) → U4 new_person(6775463) → U5 schema_version 2·검사 11/14/15·manifest(40c36f8) → U6 라벨 검수 반영 3라운드(76add8a·6906af4·aeed0bd) → U7 registry 12행·README(f78e9dc) → verifier(fable) 04-review **완료**(필수 0, 권고 R-4~R-12 반영 8·R-6 P4 이관, verify-impl FAIL 0/WARN 0, 수용 기준 4/4, 부정 케이스 8/8·대조군 0) → 사용자 승인. 40건·5범주(8/8/8/10/6), 라벨 검수 verifier 40/40·사용자 12/12. 닫는 R 없음(R3·R4 는 P4). **P4 인계 13항·P10 인계 5항 = `packages/P1-pilot-dataset/04-review.md` §7** — P4 01-plan 이 옮겨 적었는지 P4 02-plan-verify 에서 본다.
- **P3-er 완료(2026-09-06)** — U1~U9 + FIX(2b82882..b3bcc2d), verifier 04-review 완료(필수 0·권고 6). R4·R9 구현완료(**실호출 미검증** 표기). 열린 권고: F-87c597 R4 실호출(사용자 스모크), F-46f1eb 더미 키 규약, F-036185 bool id 방어, F-251dc2 trace 복제·F-bdd6c5 top_k 무효(P4 결정).
- 이전 패키지 열린 소견: P2 F-4d2507 `DELETE /persons/{id}` backlog(P5/P8 계획 때 architect), F-4d8d96 tool_error rollback(P5), F-c7078e mako Refs(revision 만들 때).
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 0001(head), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8` + 리다이렉트. verify-impl.sh 내부 pytest 는 포트 없이 돌아 skip 표시(하네스 한계). 설치: anthropic 1.4.0·openai 2.33.0.

## 바로 다음에 할 것 (순서대로)
0. **P3-baselines 구현**: 계획 커밋 → U1(인터페이스, R-1 분기 금지 명령 명시) → U2(어댑터) → U3(완전일치, R-8) → U4(임베딩 단독) → U5(LLM 단일, 결정 I·J, R-4 OPENAI_MODEL) → U6(적재기, R-6·R-7 validate_scenarios 적재 함수 재사용) → U7(parity) → U8(evidence·registry·README, R-2 역방향 import 0) → verifier 04-review. 단위마다 L-004 승인 → eval-agent → /commit. DB 5433 필요(Docker Desktop).
1. 사용자 스모크(값은 셸에만): `ANTHROPIC_API_KEY=… python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/<ts>-er-smoke-real.txt` 또는 `LLM_PROVIDER=openai OPENAI_API_KEY=… python scripts/er_smoke.py --provider openai` → F-87c597 닫고 review-index R4 갱신(작은 docs 커밋).
2. 다음 패키지(architect 에게 backlog 분해, L-004 승인 후): **P3 베이스라인 3종**(eval-agent) / **P4-pilot-eval**(P1·P3 완료로 착수 가능 — 01-plan 에 F-251dc2·F-bdd6c5 결정 + P1 04-review §7 인계 13항 포함) / **P0-cost**(AWS Budgets). **P4 통과 전 P5 이후 시작 금지.**
3. 사소 FIX 후보(별도 작은 커밋, 승인 후): F-46f1eb·F-036185.

## 재개 시 읽을 카드 (이것만)
- 사용자가 직접 할 일(키·Budgets·스모크·배포 비밀): `docs/user-setup/README.md` — 사용자 요청(2026-09-10)으로 신설. 사용자 몫 항목은 여기에만 추가한다.
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `packages/P3-baselines/01-plan.md`(범위·작업 단위·결정 확정 2블록), `02-plan-verify.md` §3 권고 R-1~R-9, `03-log.md` 마지막 항목, `docs/backlog.md` P3 절
- `packages/P3-er/04-review.md` §6~§7(열린 권고·P4/P5 인계), `05-remediation.md` 신규 권고 6, `README.md` "엔티티 해석(ER) 실행법"
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- 스모크 실행 시점(사용자 키 필요, 순서 1). 다음 패키지 선택(P3 베이스라인 또는 P4-pilot-eval, 순서 2) — L-004 승인 뒤 architect 위임.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. **`git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다** — cleanup 훅이 push 분기에서 끝나 commit 마커·COMMIT journal 줄이 남는다(2026-09-10 실측: journal 은 손으로 보정, 마커는 safety-guard 가 삭제를 막아 그대로 둠). Bash 문자열에 마커 파일명을 쓰는 것도 막힌다. Bash 문자열에 훅 금지 문구(볼륨 삭제, 강제 푸시, DROP, 환경변수 전체 출력 단어) 금지 — 문서 수정은 스크립트 파일(scratchpad) + python 실행 또는 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 실제로 바꾼 커밋만, 기존 파일 행은 비고만.
- 서브에이전트가 만든 pending 해시·상태 줄은 다음 커밋에서 메인 세션이 정리한다. evidence 를 쓰는 테스트는 반드시 환경변수 게이트(`ER_EVIDENCE_STAMP` 규약).
