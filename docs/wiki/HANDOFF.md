# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-23 17:20 (**세션 중단** — P5-loop 계획이 2차 보류인 상태에서 사용자가 중단을 결정했다. 재개하면 아래 1번부터.)

**이번 세션에 끝난 것**: P4b-er-redesign 종료(게이트 통과, `1075dd6`) → FIX-001 main 병합·승격(`e2f0569`, 네 갈래 동기화) → FIX-001 마무리(`1227026`) → FIX-002 게이트 검사(`cf82868`).

**P5-loop 계획 경과**: architect 01-plan 초안(U1~U7) → **사용자 결정 12건 확정** → backlog 개정 3건 → 기계 검증 `FAIL=12` → 형식 2건 수정 + FIX-002 → `FAIL=1` → **verifier 1차 보류**(H-1·H-2·H-3) → **결정 L 을 (i)→(iii) 하이브리드로 변경** → architect 개정(U1~U8, 판정 표 27행) → **사용자 확정 M-1(d)·M-2(i)** + backlog 리스크 로그 → `FAIL=0` → **verifier 2차 보류**. 상세는 `journal.md` 17:20 줄과 `02-plan-verify.md`.

**확정된 설계(다시 열지 말 것)** — A 추출 개수 상한(언급 5·이벤트 5·일정 3) · B 응답은 템플릿 · C 순차 처리·첫 되묻기에서 턴 종료 · D 되묻기로 끝나도 되돌리지 않는다 · E 재개는 해석 단계부터 · F `tool_name="agent"`+`loop_` 6종(`loop_gate` 포함) · G 한 줄 안내+저장 0 · H 예외를 삼켜 200 으로 같은 트랜잭션 커밋 · I 세션 id 서버 발급·격리는 명시만 · J 소비 1회는 409·대상은 `context["mention"]` · K 이벤트는 `now`·일정은 되묻기 · **L(iii) LLM 이 `tool_calls` 를 제안하고 코드가 게이트를 친다**(화이트리스트·인자 스키마·**`person_id` 직접 지정 금지**·상한, LLM 은 턴당 1회) · M-0 `apply_resolution` 호출 **전에** `dataclasses.replace` 로 `context` 에 `"resume"` 한 키 · M-1(d) 확인 질문 하나로 태그까지 · M-2(i) 후보 시각 2~3개+모르겠어요.

**2차 보류 3건**(원칙·카드 위반 아님. 전부 01-plan 문장 수정으로 닫힌다):
- **H-1(잔존)** 판정 표 7·22행 기대 출력이 **구조상 거짓**. 메인 세션이 코드로 확인: `search_person`·`update_person`·`ask_user` 가 전부 `@traced` 이고 ER 이 내부에서 부른다(`candidates.py:112`·`pipeline.py:461`·`:474`) → `tool_call` 행에 **게이트가 거부할 툴이 반드시 섞이므로** "`accepted` 집합 = `tool_call` 행 집합" 은 성립 불가. 빈 DB 예시는 되묻기로 끝나 `loop_record` 가 없고, 시드 DB 면 `judge=FakeJudge` 미주입이라 실 공급자를 부른다.
- **H-4(신규)** 확정 M-1(d)·M-2(i) 가 본문 5곳 미반영 — U1 `PendingResume` 스키마 · U4 `replace` 식 · U7 문장 · **M-0 ③ 이 M-1(d)와 모순**("`AFFIRMATIVE_KEY` 를 고치지 않는다") · 힌트 있을 때도 태그를 묻는지 미정.
- **H-5(신규)** 판정 표 5행 grep 기대 출력이 U5 의 `update_person(facts/new_alias)` 호출과 모순.
- 권고 **R-9~R-19**. R-19 는 하네스(P5 밖): `verify-plan.sh` 7절 정규식 `[.][a-z]{1,5}` 가 `inspect.signature` 를 잘라 가짜 경로 토큰을 만든다(메인 세션 확인).

**루프 비용 경고**: 1차 보류 3건 → 개정 → 2차 보류 3건(2건 신규). 계획이 커지며(판정 표 18→27행) 결함이 계속 나온다. 원칙8 "재시도 남발 금지"를 의식할 지점 — 3차는 **범위를 묶어서**.

**메인 세션이 이번에 틀렸던 것(같은 실수 반복 금지)**: ① 결정 L 을 설명할 때 원칙1·4 와 CLAUDE.md 만 보고 **`docs/proposal.md` 72행을 확인하지 않았다** — 권위 문서는 침묵했어도 기획서를 직접 열었어야 했다. ② `FIX-002.md` 에 evidence 파일명을 손으로 적어 틀렸다(1518 → 실제 1526, 정정 완료). ③ stage-gate 훅은 거절할 때도 **exit 0** 이고 판정이 출력 JSON 에 있다 — 종료 코드로 읽어 "가드가 안 막는다"고 잘못 봤다가 정정했다.

**커밋 메시지는 사람이 읽는 문장 형식(사용자 지시) 계속 적용.**
active: **none**(P5-loop 은 아직 활성화 전 — 02-plan-verify 통과 + 사용자 승인 뒤에 `active: P5-loop`) | frozen: none | P4b-er-redesign **완료** · FIX-001 **완료** · FIX-002 **완료** | 브랜치: dev — **로컬이 `origin/dev`(e2f0569) 보다 2커밋 앞선다**: `1227026`(FIX-001 마무리) · `cf82868`(FIX-002). `main` = `origin/main` = `e2f0569`. **푸시하지 않았다** — 푸시하면 L-003 마커가 서서 verifier 다음 단계를 바로 못 잇기 때문이고, P5 계획 승인까지 마친 뒤 한 번에 올린다. Docker `capstone2-postgres-1` 5433. 미추적 2파일(`reports/pilot/raw-20260922-150931.jsonl` 평문 7.7MB·`metrics-stage.json`)은 **의도적으로 커밋하지 않는 것**이니 지우지 않는다.

## 지금 어디까지
- **완료**: P1·P2·P3(er·baselines·llm-providers)·P4(부분완료, 게이트 미달)·**P4b(게이트 통과)**·FIX-001(main 병합·승격)·FIX-002(게이트 검사). 전부 04-review `결과: 완료` 또는 FIX `## 상태: 완료`.
- **P5-loop 은 계획 단계에서 멈춰 있다** — 01-plan 개정본(U1~U8) + 02-plan-verify `결과: 보류`(2차) + 05-remediation(열림 8 = 필수 1 + 권고 7) + evidence 7개. `CURRENT active: none` 이므로 **제품 코드를 쓸 수 없다**(stage-gate 가 막는다).
- **실호출로 검증된 LLM 공급자 1/3(openai)**. anthropic·gemini 는 미실행(선택). 첫 실서버 검증은 P9 배포 뒤 `SERVER-CHECKLIST.md` — 지금까지의 승격은 전부 pytest·게이트 근거다.
- **이전 패키지 열린 소견**: P3-er F-46f1eb·F-036185, P2 F-4d2507(→ backlog `DELETE /persons/{id}` 항목으로 신설됨)·F-4d8d96·F-c7078e, P4 F-251dc2·F-bdd6c5.
- **로컬 환경**: Docker `capstone2-postgres-1` 호스트 5433. 명령 앞 `POSTGRES_PORT=5433`, 한글 출력 `PYTHONIOENCODING=utf-8`, JSON 한 줄 명령 `PYTHONUTF8=1`. `.env` 의 `DATABASE_URL` 이 `POSTGRES_PORT` 보다 우선한다(`app/config.py`). evidence 를 python 으로 읽을 때 `errors="replace"`(cp949 혼입). 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **[재개 첫 질문] 2차 보류를 어떻게 풀지 사용자에게 먼저 묻는다.** 네 안을 그대로 다시 보인다 — (a) **3차 개정, 범위를 묶어서**(architect 에 H-1·H-4·H-5 + R-9~R-17 **만** 고치게 하고 새 단위·새 판정 행 추가 금지) / (b) **판정 표를 줄인다**(27행은 과하다. 수용 기준 직결 행만 남기고 나머지는 구현 중) / (c) **보류를 [권고]로 내리고 승인**(빠르지만 틀린 판정 방법으로 착수하게 된다) / (d) 메인 세션이 직접 고친다(L-002 이탈). **(a) 를 권했다.** 원칙8 "재시도 남발 금지" 를 의식할 지점이다 — 1차 3건 → 2차 3건(2건 신규), 계획이 커지며 결함이 계속 나온다.
2. 정하면 그 뒤는 **L-004 승인 → `--stage <에이전트>` 마커 → Agent 1회** 순서. 3차도 보류면 멈추고 다시 의논한다.
3. 통과 뒤: 사용자 계획 승인 → `02-plan-verify.md` `승인: 사용자 (날짜)` → `CURRENT.md active: P5-loop` → `03-log.md` 생성 → `journal.md` START → 계획 문서 커밋 → **U1 착수**(backend-agent, L-004 매번).
4. **미푸시 3커밋**: `1227026`(FIX-001 마무리) · `cf82868`(FIX-002) · 이번 계획 기록 커밋. `origin/dev` = `e2f0569`. 푸시하면 L-003 마커가 서므로 재개 시 승격/보류를 묻게 된다.
5. 남은 [권고]: R-19 `verify-plan.sh` 7절 정규식(하네스, P5 밖) · `test-guards.sh` 옛 경로 13곳 · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · registry 133행 `U6(pending)` · `verify-impl.sh` 6번 완화 · 러너 `safe_summary` FIX · 09 카드 §2 결정 10개 · anthropic·gemini 스모크 · F-46f1eb·F-036185.
6. **P10 인계**(P4b 04-review §7): 결정 A(i) 비용 재측정 · `s_llm` 60/136 변동 때문에 2회 실행 여부 · `T_merge`/`T_new` 운영값 · 다음 실 실행은 `2>&1 | tee` + `echo "rc=$?"` 까지.
2. **사용자 계획 승인**(AskUserQuestion) → `02-plan-verify.md` 에 `승인: 사용자 (날짜)` → `CURRENT.md` `active: P5-loop` → `03-log.md` 생성 → `journal.md` `START` → **계획 문서 커밋**.
3. **미커밋 잔여 정리 + dev 푸시** — 계획 승인 커밋까지 묶어 `1227026`·`cf82868` 과 함께 한 번에 올린다. 푸시 뒤 L-003 결정을 묻고 멈춘다.
4. **U1 착수** — backend-agent 위임(L-004 매번). 단위는 U1~U7, 각 단위 끝에 `/commit`. **U1 은 확정 12건을 전제로 한다.**
5. 남은 [권고]: `test-guards.sh` 옛 경로 13곳(별도 단위) · P4b 01-plan 111행 판정 표 20행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · registry 133행 `U6(pending)` 은 P4-pilot-eval 소속 · `verify-impl.sh` 6번 완화 여부 · 러너 `safe_summary` FIX · 09 카드 §2 결정 10개 · anthropic·gemini 스모크 · F-46f1eb·F-036185.
6. **P10 인계**(P4b 04-review §7): 결정 A(i) 비용 재측정 · 실행 변동성(`s_llm` 60/136) 때문에 2회 실행 여부 · `T_merge`/`T_new` 운영값 확정 · 다음 실 실행은 `2>&1 | tee` + `echo "rc=$?"` 까지 남긴다.

## 재개 시 읽을 카드 (이것만)
- `packages/P5-loop/01-plan.md`(작업 단위 U1~U7, **리스크·미결 절 머리의 확정 12건**, 판정 방법 표), `02-plan-verify.md` §2·권고, `05-remediation.md`(열린 8건 = 필수 1 + 권고 7)
- `decisions/D01`·`D02`(코드에서 지켜야 할 것), `specs/S3.4`·`S3.2`·`S3.3`, `docs/backlog.md` "P5" 절
- `docs/wiki/fixes/FIX-002.md`(게이트 검사 수정 근거), `docs/wiki/CURRENT.md`, `.claude/gitlog.md`
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- **[최우선] P5-loop 2차 보류를 어떻게 풀 것인가** — 네 안(3차 개정 범위 묶기 / 판정 표 축소 / 보류를 권고로 내리고 승인 / 메인 세션이 직접 수정). 재개 시 첫 질문이다. ~~main 갈라짐~~ 은 FIX-001 로 해소됐다(네 갈래 모두 `e2f0569`).
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
