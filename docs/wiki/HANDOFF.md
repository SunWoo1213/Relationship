# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-29 23:50 — **P6-memory 가 끝났다. 활성 패키지가 없다(`active: none`). 커밋 `94373cc` · origin/dev2 = 여기.**

verifier 04-review `결과: 완료` → 사용자 승인(2026-09-29). 승인 뒤 메인 세션이 [권고] 3건을 닫고 `verify-impl.sh P6-memory` 를 다시 돌려 **FAIL 0 / WARN 0** 을 받았다(`evidence/20260929-2337-*`, 이전 WARN 이던 "미완료 작업 단위 6개" 가 `PASS 작업 단위 모두 완료 표시` 로 바뀜).

**그 뒤 FIX-015 도 끝냈다(2026-09-30, 커밋 `6e7b286` · origin/dev2 = 여기).** 사실 키 중복을 사용자가 **FIX + "스키마 enum 으로 유도"** 로 정했고, `app/agent/propose.py` 의 `PROPOSAL_ARG_SCHEMA.facts.key` 에 `app.memory.FACT_KEYS` 9종 enum 을 걸었다 — **제품 코드 실질 변경은 상수 한 줄**이다. 판정 표 5행 전부 충족(전체 **1624 passed skip 0** = 기준선 1622+2 · `tools_check` **7/7** = S3.2 무변경의 증거 · 회귀 4파일 121 · 기존 테스트 수정 0건). **실 LLM 왕복 확인도 통과했다(2026-09-30 01:00, 커밋 대기)** — 발화 4건에서 루프가 제안한 키가 `hobby`·`workplace`·`likes`·`dislikes` 로 **`FACT_KEYS` 밖 0건**, `memory_error` 0행(증거 `fixes/evidence/FIX-015/20260930-0100-real-llm-check.txt`). **결정적 증거는 trace 171** — 발화에 "**소속이** 네이버로 바뀌었어" 라는 말이 그대로 있는데도 LLM 이 `소속` 이 아니라 `workplace` 를 골랐다(수정 전 같은 자리에서 나온 것이 `소속`·`직장`·`이직`). **남는 한계**: 4발화 1회 관측이고, enum 은 여전히 유도이지 거부가 아니다 — 어휘 밖 키가 다시 관측되면 거부안((나) `update_person` 어휘 검사)을 별건으로 올린다. 이미 저장된 `소속`·`직장` 행은 지우지 않았다.

**FIX / CR 판단 근거(다음에 같은 유형이 오면 재사용)** — 조사 결과(read-only, 2026-09-29 23:50): **사실 키 어휘를 정한 D 카드·S 카드·기획서 문장이 없다** — `S3.2` 는 `facts?: {key,value}[]` 시그니처만 적고(키에 어휘 제약을 걸어도 시그니처는 그대로라 `tools_check` 7/7 유지), `S3.5` 는 어휘를 말하지 않으며, `grep -rln "FACT_KEYS|사실 키|고정 어휘" docs/wiki/decisions/ docs/wiki/specs/ docs/proposal.md CLAUDE.md` 가 **0건**이다. D-5 는 P6-memory **패키지 안의 결정**이고 거기서도 루프의 자유 키는 "한계·리스크"로만 적혀 있다. → **원칙·D·S 를 바꾸지 않으므로 FIX 가 맞다**(devlog 규칙 "수정이 원칙·D·S를 바꾸면 FIX가 아니다" 의 반대). 선례도 있다: `app/agent/propose.py` 125~131행 docstring 이 "`type`/`relation_tag`/`hierarchy` 만 enum 으로 **유도**하고, 7종 밖 값의 거부는 게이트가 한다" 고 이미 정해 뒀다 — `facts.key` 에 `FACT_KEYS` enum 을 더하는 것은 그 설계를 따르는 것이다.

**무엇이 돌아가게 됐나(한 줄)**: 대화 턴마다 ① 같은 인물의 같은 종류 사건이 기본 365일 안에 3회 이상이면 `pattern:{type}` 사실이 규칙으로 생기고(LLM 0회), ② 미승격 이벤트가 5건 쌓이면 LLM 이 인물 사실로 승격하며, ③ 만들어진 사실은 전부 `fact_sources` 로 근거 원문에 이어진다. 실 LLM 왕복으로도 확인했다(journal 17:30·19:50).

**커밋 U1 `7564c5d` · U2 `d67d084` · U3 `51b4d65` · U4 `48e3617` · U5 `b209581` · U6 `8d3967a` · U7 `93c6d3f` · U8 `4916db3`.** R8·R11 구현완료. 전체 회귀 **1622 passed skip 0** · `alembic check` 무변경 · `tools_check` 7/7.

**verifier 가 독립 판정한 6가지는 전부 "미달 아님"으로 갈렸다** — 판정 표 8행은 계획 표기 문제, 사실 키 중복·루프 어휘·추출 품질·`/health` 는 **범위 밖 별건**(04-review §7). verifier 는 보고 수치를 옮기지 않고 재실행했고, `PATTERN_MIN_COUNT=2`·`MEMORY_PROMOTE_MIN_EVENTS=4`·`PATTERN_WINDOW_DAYS=400` 로 **일부러 어긋나게 주어 FAILED 가 나는 것까지** 확인했다(항상 통과하는 테스트가 아님, 원칙8).

active: **none** | frozen: none | 브랜치 `dev2`(작업·실험) | main = `1e4afb4` · origin/dev = `e48ac4c` · origin/dev2 = `4916db3` | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 커밋 안 된 변경 (이 세션이 만든 것)
- `packages/P6-memory/04-review.md`(신규, verifier 작성 + 승인 줄·승인 뒤 처리 기록) · `evidence/` 17개(신규) · `05-remediation.md`(F-bbf7fa 3단계 닫음)
- `01-plan.md`(U3~U8 체크박스) · `registry.md`(비고 6곳) · `review-index.md`(R8·R11) · `docs/backlog.md`(P6 첫 항목) · `docs/RUNNING.md`(202행 `memory_promote` 세 종류) · `CURRENT.md`(active 해제) · `journal.md`(DONE) · 이 파일

## 바로 다음에 할 것
1. **커밋 안 된 잔여 3줄을 다음 커밋에 싣는다** — `journal.md` 의 COMMIT·PUSH 줄(훅이 자동 기록), `fixes/FIX-015.md` 결과 절의 해시 `6e7b286`, 이 파일. 이 저장소의 기존 관례다(해시는 커밋 뒤에야 알 수 있으므로 늘 한 박자 늦게 실린다).
2. **새로 드러난 FIX 후보 2건을 어떻게 할지 정한다**(아래 "열린 질문" 참고). ① **응답 문구** — 사실만 저장된 턴이 "새로 기억한 것이 없어요" 라고 답한다(`respond.py::build_reply` 가 사실 건수를 안 받는다). 사용자에게 거짓말을 하는 셈이라 **가장 눈에 띄는 결함**이고 고치기는 작다. ② **추출 품질** — "매운 음식을 못 먹어" 를 `likes` 에 넣었다. P10-final-eval 몫이지만 `likes`/`dislikes` 혼동은 브리핑이 정반대 제안을 내게 하므로 P6-briefing 전에 한 번 볼 값어치가 있다.
3. `dev` 승격 검토 — dev2 의 P6-memory 26커밋을 `git push origin dev2:dev`(승인 마커 먼저, 푸시 뒤 L-003 대기).
4. FIX 후보 3건(아래 "열린 질문"): `/health` 빈 DB · `update_person` 부분 반영 · `memory_promote` `source` 키 비대칭(코드 한 줄, 문서는 이미 고침).
5. 그다음 패키지: **`P6-briefing`**(패턴 문장화 · 브리핑 직전 패턴 재계산 — `detect_patterns` 는 순수 SQL 이라 다시 불러도 된다). 이후 P8 인물 카드, P9 AWS(Terraform).

## 다음 패키지가 알아야 할 것 (04-review §7 요약)
- 진입점은 하나: `app.memory.after_record(ctx, person_ids, extractor=None, *, fact_keys_by_person=None, event_ids_by_person=None)` — 루프 `_record()` 뒤 한 자리에서만 부른다.
- `person_facts` 에 **세 출처가 섞여 있다**: `pattern:*`(규칙, confidence 1.0, value `"{n}회 (날짜…)"`) · 승격 사실(`FACT_KEYS` 9키) · 루프 직접 사실(**자유 키** — 위 2번이 여기서 나온다). P8 "원문 펼치기" 는 `fact_sources → events.raw_utterance`(조회 API 는 아직 없다).
- **미승격 판정은 `agent_traces` 를 상태로 쓴다**(결정 B(ii)) — **trace 를 지우면 승격이 다시 돈다.**
- `memory_promote` 는 세 종류다. 승격 횟수 = `considered_event_ids` 가 비어 있지 않은 행의 수(`docs/RUNNING.md` 202행 표).
- 한계: 새 이벤트 없이 시간만 흐르면 패턴이 낡는다(결정 C-5) → 브리핑 직전 재계산이 필요한 이유.

## 옛 세션에서 끝난 것 (상세는 journal·04-review)
- **P5-loop 완료** → main 승격(1474 passed, 실서버 왕복 확인). **FIX-005** 사용자 시간대 `APP_TIMEZONE`(기본 서울). **FIX-006** pytest 는 항상 테스트 전용 DB `relationship_test` 에만 붙는다. 셋 다 main 에 있다(main = `1e4afb4`).
- 이 세션(09-28~29) 전반부는 **Windows → Mac 이전으로 조용히 망가진 하네스를 고치는 데** 썼다: FIX-008 `c4285ed`(훅 9개가 macOS 에 없는 `python` 을 불러 **차단형 가드 5종이 전부 열려 있었다**) · FIX-010 `3c0f0d9`(브랜치 3단계 + `test-guards.sh` 실패 50→0) · FIX-011 `217e523`·`cd09a60`(**구현 검증이 테스트를 한 건도 안 돌리고 통과하고 있었다**) · FIX-012 `0c46913`(DB 기본 포트 5433) · FIX-013 `e1ca8da`(커밋+푸시를 묶으면 후처리가 통째로 건너뜀).

## 사용자 몫 (알려 둔 것)
- **브랜치 역할(2026-09-29 확정, FIX-010)**: `dev2` = 작업·실험(아무때나 `git push origin dev2`) → `dev` = 검증을 통과한 것(`/commit` 승인 뒤 `git push origin dev2:dev`, 그 뒤 L-003 대기) → `main` = 배포(`/commit release`). `origin dev` 직접 푸시는 훅이 막는다. **다른 기기에서는 `origin/dev2` 를 받아 그 위에서 바로 작업한다**(`git checkout dev2 && git pull --ff-only`). 새 기기마다 `gh auth login` + `gh auth setup-git` 이 필요하다. 주의: GitHub Desktop 에서 브랜치를 바꾸면 커밋 안 된 변경이 stash(`!!GitHub_Desktop<dev>`)로 들어간다 — 사라진 것처럼 보이면 `git stash list`.
- **[미확인] Windows 기기에서 훅·검증 스크립트를 한 번 돌려 봐야 한다** (FIX-008·FIX-010·FIX-011 은 전부 Mac 에서만 확인했다). 확인할 것: ① `bash .claude/scripts/test-guards.sh` → 실패 0 ② `set -a; . ./.env; set +a` 뒤 `bash .claude/scripts/verify-impl.sh P6-memory` → `PASS pytest 통과` ③ `bash -c '. .claude/hooks/_py.sh; echo $HOOK_PY'` 가 `python`(Windows 표준 이름)을 골랐는지 ④ venv 경로가 `.venv/Scripts/python.exe` 로 잡히는지 ⑤ 커밋 한 번 해 보고 승인 마커가 자동으로 지워지는지. 하나라도 어긋나면 그 출력을 알려 주면 FIX 로 잇는다.
- 환경 파일 15행에 공백이 섞인 값이 있다(`2.5: command not found`). `LLM_PROVIDER=openai`(하나만)·`LLM_PROVIDERS_ENABLED=`(비우면 셋 다 허용)·`OPENAI_MODEL=gpt-4o-mini` 로 정리하라고 안내했다. `DATABASE_URL` 이 5432(다른 프로젝트)를 가리켜 서버 기동 때 `unset DATABASE_URL` 이 필요했다.
- 빈 DB `relationship_test_fix006_evidence` 정리(훅이 셸의 DB 삭제를 막음). GitHub main 브랜치 보호 규칙. 테스트 서버(8000)가 켜져 있으면 종료.

## 열린 질문 · 보류
- **[FIX-015 로 1차 처리함, 실 확인 대기] 같은 사실이 키 3개로 중복 저장된다** — 실 LLM 에서 `소속=네이버`·`직장=네이버`(루프가 씀) + `workplace=네이버`(승격이 씀) 세 행이 한 인물에 동시에 있었다. 원인은 `app/agent/propose.py::PROPOSAL_ARG_SCHEMA` 의 `facts.key`(145행)가 **enum 없는 자유 문자열**이고 `_PROPOSAL_TOOL_DESCRIPTION`(120행)에도 어휘 지시가 없어 LLM 이 발화마다 다른 한국어 키를 만드는 것(관측: `이직`·`소속`·`직장`). 브리핑(P6-briefing)·인물 카드(P8)가 중복을 그대로 보여준다. verifier 판정: **P6-memory 범위 밖 별건이 맞다**(01-plan D-5·리스크 절이 "루프의 자유 키는 이 패키지에서 바꾸지 않는다" 고 명시했고 사용자가 그 계획을 승인했다) — **그러나 제품 결함으로는 실재한다.** 곁들여: 사실 제안 자체가 드물다(발화 7건 중 2건) — 시맨틱 사실의 주 공급원은 승격이고 루프는 보조다.
- **[FIX 후보] `/health` 가 테이블이 없어도 `db: up`·`status: ok` 를 반환한다.** 이번에 개발 DB 가 빈 것을 `/health` 로는 알 수 없었고 단서는 `alembic_revision: null` 뿐이었다. 마이그레이션 안 된 DB 를 "정상" 으로 보고하면 배포(P9) 뒤 같은 상황을 알아채기 어렵다. 이 패키지가 만든 결함이 아니다(`/health` 는 P2-tools `4d5817e`).
- **[FIX 후보] `update_person` 의 인자 간 부분 반영** — `display_name`·`new_alias` 가 `facts` 검증보다 **앞에서** 적용된다(`app/tools/persons.py` 498~520행). 그래서 검증에 실패한 호출이 이름 변경을 남긴다. 고치는 법: `facts` 검증을 함수 맨 앞으로(테스트 2~3건).
- **[FIX 후보] `memory_promote` 의 `source` 키 비대칭** — 세 종류 중 직접 링크 행에만 `source` 가 있다. `PromotionResult.to_dict()` 에 `source: "llm"`/`"skipped"` 를 더하면 한 키로 갈린다. **문서(`docs/RUNNING.md` 202행)는 이미 사실대로 고쳤다.**
- **[FIX 후보, 새로 발견 2026-09-30] 사실만 저장된 턴이 "새로 기억한 것이 없어요" 라고 답한다.** FIX-015 실 확인에서 세 턴이 `person_facts` 를 실제로 쓰고도(fact_id 13~16) `_NOTHING_STORED` 문장을 돌려줬다. 원인은 `app/agent/respond.py::build_reply` 가 `stored_events`·`stored_schedules` 두 숫자만 받고 **사실 건수를 아예 받지 않는** 것이다(P5-loop 결정 B(i)). 사용자에게 "기억 안 했다" 고 해 놓고 인물 카드에는 사실이 쌓이므로 신뢰를 깎는다. 고치려면 `RecordOutcome` 에서 사실 건수를 세어(U7 이 이미 `fact_keys_by_person` 을 모은다) `build_reply` 에 넘기고 "사실 N건" 을 문장에 더한다 — 결정 B(i)의 "숫자·불리언만 입력" 규약은 그대로 지켜진다.
- **[추출 품질] 어휘는 맞는데 값의 의미가 뒤집힌다** — 회사명(카카오)이 `workplace` 가 아니라 `job` 에 들어갔고(2026-09-29), "매운 음식을 **못 먹어**" 가 `dislikes` 가 아니라 `likes` 에 들어갔다(2026-09-30, 같은 호출의 `dislikes=고수` 는 맞았다). **FIX-015 는 "어느 서랍에 넣는가" 를 고쳤을 뿐 "무엇을 넣는가" 는 고치지 않는다.** 01-plan 이 추출 품질 지표를 **P10-final-eval** 몫으로 명시했다. 다만 `likes`/`dislikes` 혼동은 브리핑이 정반대 제안을 내게 하므로(예: 매운 음식점 추천) P6-briefing 전에 프롬프트 키 설명을 한 번 볼 값어치가 있다.
- **[결정됨 2026-09-29] 환경 파일은 코드가 읽지 않는다 — A안 유지**(셸에서 `set -a; . ./.env; set +a`). `load_dotenv` 안은 테스트 3개가 `app.main` 을 import 해서 "앱 시작할 때만 읽는다" 가 성립하지 않아 보류. **P9 에서 진입점을 정리할 때 재검토** — `lessons/CANDIDATES.md` C-8, 근거 `fixes/FIX-012.md`.
- **FIX-014(후보, 미착수)** — 훅의 판정 입력이 실제 행위와 어긋난다. ① Bash 편집(`sed -i`·heredoc·`>`)은 `stage-gate`·`secret-guard` 를 통째로 지나간다 ② `commit-cleanup` 은 명령 **문자열**만 보므로 실행되지 않은 푸시를 기록할 수 있다. 당장은 운용 규칙으로 막아 뒀다(CLAUDE.md "파일 변경은 Write/Edit 툴로만").
- 보류 목록: R-19(`verify-plan.sh` 7절 정규식) · P4b 01-plan 111행 경로 오기 · 03-log `Refs: R8` 어휘 충돌 · 하네스 부채(verify-plan 토큰 스캔 오탐, findings.py 빈 표 중복, verify-impl 이 05 머리말 메모를 지우는 문제) · **L-후보: 판정 표의 케이스 열이 앞 행 상태를 잇는지 독립인지 계획에 적는다**(04-review §6).
- P9 전: 다중 사용자 격리 부채(F-fbaaae). 개발 DB 에 확인용 행(`judge-row7-*`·`verifier-row7-*`·`row8-check-23175`·`fix005-recheck`·`u6-server-check`·`llm-check`·`u7-check`·`fix015-check`)이 남아 있다. 지우지 않는다.

## 주의
- **언어: 전부 한국어.** 결과는 예시와 쉬운 말로 먼저 설명하고 승인을 묻는다.
- 위임은 묻고 시작(L-004). 서브에이전트 보고는 테스트 재실행·grep 으로 재확인.
- 실서버 확인 명령: `set -a; . ./.env; set +a; unset DATABASE_URL; APP_USER_ID=<확인용 이름> POSTGRES_PORT=5433 nohup .venv/bin/python -m uvicorn app.main:app --port 8000 > <scratchpad>/uvicorn.log 2>&1 &`. 값은 출력하지 않는다. 한국어 본문은 UTF-8 파일로 `--data-binary @file` 전송(인자로 주면 400).
- **커밋과 푸시는 반드시 따로 실행한다**(FIX-013). 한 명령에 묶으면 `commit-cleanup` 이 푸시만 처리하고 끝나 마커가 남고 journal 줄이 빠진다. dev 푸시 뒤 `.awaiting-decision` 이 새 커밋을 막는다 → 사용자 결정 후 `--decision fix` 또는 `--release`.
- **파일 변경은 Write/Edit 툴로만.** Bash(`sed -i`·heredoc·`>`)로 쓰면 `stage-gate`·`secret-guard` 가 입력 필드가 없어 통째로 통과한다 — 활성 작업 게이트·frozen·L-003 잠금·비밀 검사가 동시에 열린다. 읽기·검색은 Bash 로 해도 된다.
- `app/` docstring 에 "evaluation" 금지. `app/agent/` 에 `T_merge|T_new|confidence`·`create_person(` 리터럴 금지(기준선 1건: `loop.py`).
