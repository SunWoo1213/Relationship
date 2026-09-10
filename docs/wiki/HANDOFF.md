# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-10 (P1-pilot-dataset 완료 승인 — 닫는 docs 커밋 준비 중)
active: **none** | frozen: none | 브랜치: dev = f78e9dc(U7), origin/dev 09875aa(로컬 7커밋 미푸시), main bdf9f70 승격 보류. **진행 중: P1-pilot-dataset 닫는 커밋(`/commit` 초안 → 사용자 승인)** — 04-review `승인: 사용자 (2026-09-10)`·backlog P1 [x]·registry 105/106행 정정·03-log U7 해시·CURRENT none·journal DONE·05-remediation F-14f3ef 해소·evidence 22(2152-* 16 + 20260910-*) 전부 미커밋. `.gitignore`(졸업작품신청서.md 제외)도 같은 커밋에 넣는다(사용자 결정 2026-09-10). 03-log 09:40 항목의 `pending` 은 이 커밋 해시로 다음 커밋에서 채운다.

## 지금 어디까지
- **P1-pilot-dataset 완료(2026-09-10)** — U1 스키마·검증기(1e1320c) → U2 promotion·alias(09875aa) → FIX 시점 무관 테스트(baee71e) → U3 pronoun·normal(aa6ecfc) → U4 new_person(6775463) → U5 schema_version 2·검사 11/14/15·manifest(40c36f8) → U6 라벨 검수 반영 3라운드(76add8a·6906af4·aeed0bd) → U7 registry 12행·README(f78e9dc) → verifier(fable) 04-review **완료**(필수 0, 권고 R-4~R-12 반영 8·R-6 P4 이관, verify-impl FAIL 0/WARN 0, 수용 기준 4/4, 부정 케이스 8/8·대조군 0) → 사용자 승인. 40건·5범주(8/8/8/10/6), 라벨 검수 verifier 40/40·사용자 12/12. 닫는 R 없음(R3·R4 는 P4). **P4 인계 13항·P10 인계 5항 = `packages/P1-pilot-dataset/04-review.md` §7** — P4 01-plan 이 옮겨 적었는지 P4 02-plan-verify 에서 본다.
- **P3-er 완료(2026-09-06)** — U1~U9 + FIX(2b82882..b3bcc2d), verifier 04-review 완료(필수 0·권고 6). R4·R9 구현완료(**실호출 미검증** 표기). 열린 권고: F-87c597 R4 실호출(사용자 스모크), F-46f1eb 더미 키 규약, F-036185 bool id 방어, F-251dc2 trace 복제·F-bdd6c5 top_k 무효(P4 결정).
- 이전 패키지 열린 소견: P2 F-4d2507 `DELETE /persons/{id}` backlog(P5/P8 계획 때 architect), F-4d8d96 tool_error rollback(P5), F-c7078e mako Refs(revision 만들 때).
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 0001(head), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8` + 리다이렉트. verify-impl.sh 내부 pytest 는 포트 없이 돌아 skip 표시(하네스 한계). 설치: anthropic 1.4.0·openai 2.33.0.

## 바로 다음에 할 것 (순서대로)
0. **닫는 커밋** `/commit`(docs: 04-review·05·03-log·backlog·registry·CURRENT·journal·HANDOFF·evidence 22·.gitignore) → dev 푸시(7+1 커밋, 승인) → L-003 승격 판단 대기(`SERVER-CHECKLIST.md` §1~§4 근거; 데이터·문서 위주라 로컬 검증 근거 승격도 가능 — 사용자 결정).
1. 사용자 스모크(값은 셸에만): `ANTHROPIC_API_KEY=… python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/<ts>-er-smoke-real.txt` 또는 `LLM_PROVIDER=openai OPENAI_API_KEY=… python scripts/er_smoke.py --provider openai` → F-87c597 닫고 review-index R4 갱신(작은 docs 커밋).
2. 다음 패키지(architect 에게 backlog 분해, L-004 승인 후): **P3 베이스라인 3종**(eval-agent) / **P4-pilot-eval**(P1·P3 완료로 착수 가능 — 01-plan 에 F-251dc2·F-bdd6c5 결정 + P1 04-review §7 인계 13항 포함) / **P0-cost**(AWS Budgets). **P4 통과 전 P5 이후 시작 금지.**
3. 사소 FIX 후보(별도 작은 커밋, 승인 후): F-46f1eb·F-036185.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `packages/P1-pilot-dataset/04-review.md` §6~§7(권고 처리·P4/P10 인계), `docs/backlog.md` P3·P4 절
- `packages/P3-er/04-review.md` §6~§7(열린 권고·P4/P5 인계), `05-remediation.md` 신규 권고 6, `README.md` "엔티티 해석(ER) 실행법"
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- dev 푸시 뒤 main 승격 여부(순서 0). 스모크 실행 시점(사용자 키 필요, 순서 1). 다음 패키지 선택(P3 베이스라인 또는 P4-pilot-eval, 순서 2) — L-004 승인 뒤 architect 위임.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. Bash 문자열에 훅 금지 문구(볼륨 삭제, 강제 푸시, DROP, 환경변수 전체 출력 단어) 금지 — 문서 수정은 스크립트 파일(scratchpad) + python 실행 또는 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 실제로 바꾼 커밋만, 기존 파일 행은 비고만.
- 서브에이전트가 만든 pending 해시·상태 줄은 다음 커밋에서 메인 세션이 정리한다. evidence 를 쓰는 테스트는 반드시 환경변수 게이트(`ER_EVIDENCE_STAMP` 규약).
