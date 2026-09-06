# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-07 04:10 (U6-3 커밋 — verifier 4차 재검수 위임 예정)
active: **P1-pilot-dataset** | frozen: none | 브랜치: dev (origin/dev 09875aa, main bdf9f70 승격 보류; 로컬 U3~U6-3 미푸시). **U6-3 커밋**(해시 journal). **다음: verifier 4차 재검수**(L-004 승인됨) — #21·#22 닫기, sc-034 t0/t1 별개 사건 판정. 열림 0 → 사용자 검수(3차 절 최종 목록: 함정 sc-002/004/006/008/010/012/013/015/036 + 지나가는 언급 sc-038/039/040) → U7(eval-agent: registry·README·수용 기준 evidence) → /devlog done(verifier 04-review). P10 인계: absolute 0, praise 1·other 5, personal_share 편중, 사용자→인물 favor 1.

## 지금 어디까지
- **P3-er 완료(2026-09-06)** — U1 @traced 세이브포인트(2b82882) → U2 임베딩 런타임 공급자·check_dimension(2c63c60) → U3 호칭 사전·규칙 필터(02e6f14) → U4 확신도·두 임계치·허용오차 1e-9(593c254) → U5 후보 어댑터·**공급자 중립 Judge(Claude·OpenAI, judge_from_env, gemini 예약 — 사용자 결정, 결정 3 개정 2)**(b1f2782) → U6 resolve() 4단계·trace 1행·부수효과 0(d6e5949) → U7 apply_resolution·회귀 3종(cc5d24f) → U8 백필·스모크 스크립트(107ace3) → FIX evidence 게이트 ER_EVIDENCE_STAMP(a807364) → U9 registry 20행·README ER 실행법·기계 검증(b3bcc2d) → verifier(fable) 04-review **완료**(필수 0·권고 6, verify-impl FAIL 0/WARN 0, pytest 398/skip 0, 변이 4종 검출, trace 재계산 오차 0) → 사용자 승인. backlog P3 ER 행 [x], review-index R4·R9 구현완료(**실호출 미검증** 두 줄 표기), README P3 행, CURRENT none.
- 회귀 3종 실측: 승진 s_llm 0.95·s_emb 0.849·s_rule 0.667·confidence 0.863 → merge·relaxed_retry·별칭 "부장님"·display_name 무변경 / 이모 relation_tag_conflict → LLM 생략 → new_person 질문 / 동명이인 0.575 → identity 질문·options 2 이름.
- **열린 권고(P3-er 05-remediation)**: F-87c597 R4 실호출 미검증 — 사용자 스모크 1회 → evidence → R4 표기 갱신. F-46f1eb 테스트 더미 키 `"sk-test-dummy"` → `_FAKE_KEY_MARKER` 규약. F-036185 `validate_judgement` bool id 방어. F-251dc2 trace candidates[].similarity/aliases_matched 가 s_emb·전체 별칭 복제(P4 결정). F-bdd6c5 `ERConfig.top_k` 가 실제 검색 K 에 무효(P4 스윕 금지 명시 또는 FIX). F-d5c11e 03-log 정정(완료).
- 이전 패키지 열린 소견: P2 F-4d2507 `DELETE /persons/{id}` backlog 항목(P5/P8 계획 때 architect), F-4d8d96 tool_error rollback 소실(P5 별도 커넥션 결정), F-c7078e mako Refs(revision 만들 때).
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 0001(head), 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8` + 리다이렉트. verify-impl.sh 내부 pytest 는 포트 없이 돌아 skip 표시(하네스 한계 — 직접 실행이 증거, 개선 후보). 설치: anthropic 1.4.0·openai 2.33.0.

## 바로 다음에 할 것 (순서대로)
0. **(완료) F-7bea05·F-1ba055 해소** — 빈 fixture(`test_empty_dataset_passes_with_zero_scenarios`) + 시점 무관 불변식(`test_repository_dataset_satisfies_time_invariant_properties`), `virtual_names` 단정 완화. 함께 **검사 (12) SURFACE_NOT_IN_UTTERANCE·(13) UTTERANCE_LENGTH/TURN_COUNT** 추가(경계 상수 8~60자·2~6턴, (11)은 U5 예정으로 비워 둠). 저장소 16건 위반 0. → 다음: fix 커밋 → U2 커밋 → U3(pronoun 8 + normal 10, 같은 방식: L-004 승인 → gen-prompt evidence 저장 → 위임) → U4(new_person 6, 하위 유형 각 3건 이상 R-5) → U5(무결성·manifest 배분표·검사 11 파일명↔category 추가·검수 패킷) → 검수(verifier 새 컨텍스트, evidence/<ts>-label-review.md, 사용자는 함정·new_person 건) → U6 → U7.
1. (완료) 완료 커밋 0527ab8 → dev 푸시 → **main 승격(2026-09-06 19:35, 12커밋 b676799..0527ab8, 로컬 검증 근거로 사용자 승인)**.
1-b. (완료) `SERVER-CHECKLIST.md` 루트 커밋 bdf9f70 → dev 푸시 → **main 승격(2026-09-06 20:15, 문서 전용이라 실서버 검증 없이 사용자 승인)**. 다음 승격부터는 이 가이드 §1~§4 증거를 근거로 한다.
2. 사용자 스모크(값은 셸에만): `ANTHROPIC_API_KEY=… python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/<ts>-er-smoke-real.txt` 또는 `LLM_PROVIDER=openai OPENAI_API_KEY=… python scripts/er_smoke.py --provider openai` → F-87c597 닫고 review-index R4 갱신(작은 docs 커밋).
3. 다음 패키지 후보(architect 에게 backlog 분해 요청, L-004 승인 후): **P1-pilot-dataset**(eval-agent, 한국어 대화 150건 — P4 게이트 선행) / **P3 베이스라인 3종**(eval-agent) / **P0-cost**(AWS Budgets) / P4-pilot-eval(P3 완료로 착수 가능, P1 데이터셋 필요). **P4 통과 전 P5 이후 시작 금지.** P4 01-plan 에 F-251dc2·F-bdd6c5 결정 포함.
4. 사소 FIX 후보(별도 작은 커밋, 승인 후): F-46f1eb·F-036185.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `packages/P1-pilot-dataset/01-plan.md`(작업 단위·결정 확정 블록), `02-plan-verify.md` §3 권고 R-4~R-12, `docs/backlog.md` P1 절
- `packages/P3-er/04-review.md` §6~§7(열린 권고·P4/P5 인계), `05-remediation.md` 신규 권고 6, `README.md` "엔티티 해석(ER) 실행법"
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- 스모크 실행 시점(사용자 키 필요, 순서 2). 다음 패키지 선택(P1-pilot-dataset 권장, 순서 3) — L-004 승인 뒤 architect 위임.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. Bash 문자열에 훅 금지 문구(볼륨 삭제, 강제 푸시, DROP, 환경변수 전체 출력 단어) 금지 — 문서 수정은 스크립트 파일(scratchpad) + python 실행 또는 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 실제로 바꾼 커밋만, 기존 파일 행은 비고만.
- 서브에이전트가 만든 pending 해시·상태 줄은 다음 커밋에서 메인 세션이 정리한다. evidence 를 쓰는 테스트는 반드시 환경변수 게이트(`ER_EVIDENCE_STAMP` 규약).
