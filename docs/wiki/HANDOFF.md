# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-02 12:00 — **dev 승격 완료: origin/dev = `36c288e`(dev2 27커밋 fast-forward, 사용자 승인). L-003 결정 = main 승격 보류 · 다음 작업 계속(사용자, 2026-10-02) — 대기 마커 해제됨.** **main 이 갈라져 있다**: origin/main = `f05d017`(2026-10-02 사용자가 main 에 직접 커밋한 README 개편, 부모 `1e4afb4`). **사용자 의도(2026-10-02): 포트폴리오용 README 수정이라 그대로 둔다** — 되돌리거나 dev 로 끌어오지 않는다. 다만 다음 main 승격 때는 `dev:main` 이 fast-forward 가 아니므로 그 시점에 README 를 어느 쪽으로 둘지 사용자에게 묻는다(dev2 의 `9b2e187` 도 README 를 고쳤다). FIX-016 완료 `36c288e`. 활성 작업 없음. 미커밋은 훅이 적은 journal 줄뿐. **주의**: 승격 준비 중 `approve-commit.sh` 를 잘못 불러 이미 쓴 초안에 대한 커밋 마커(`.claude/.commit-approved`)가 남아 있다 — 훅이 직접 삭제를 막으므로 다음 `/commit` 이 새 초안으로 덮어쓴다(초안 해시가 달라 옛 초안으로는 커밋되지 않는다).

> **2026-10-02 세션**: 재개 질문에 사용자가 FIX-016 을 골랐다. 사실만 저장한 턴이 "새로 기억한 것이 없어요" 라고 답하던 것을 "기억했어요: 사실 N건." 으로 고쳤다 — `build_reply(stored_facts=)` + `RecordOutcome.facts` 속성 + 호출 두 곳. 결정 B(i) "숫자만 입력" 유지, API 스키마 불변. **1627 passed skip 0**(1624+3) · tools_check 7/7 · 수정 전 코드로 새 테스트 3 failed 확인. 상세 `fixes/FIX-016.md`.
>
> **2026-09-30 세션**: ① P6-memory 종료(`94373cc`) ② 사실 키 중복을 FIX-015 로(`6e7b286`) ③ 실 LLM 왕복 확인 + 새 결함 2건 발견(`26dcd22`) — 그중 응답 문구가 FIX-016 이다.

**무엇이 돌아가게 됐나(P6-memory)**: 대화 턴마다 ① 같은 인물의 같은 종류 사건이 기본 365일 안에 3회 이상이면 `pattern:{type}` 사실이 규칙으로 생기고(LLM 0회), ② 미승격 이벤트가 5건 쌓이면 LLM 이 인물 사실로 승격하며, ③ 만들어진 사실은 전부 `fact_sources` 로 근거 원문에 이어진다. 커밋 U1 `7564c5d`·U2 `d67d084`·U3 `51b4d65`·U4 `48e3617`·U5 `b209581`·U6 `8d3967a`·U7 `93c6d3f`·U8 `4916db3`, 종료 `94373cc`. R8·R11 구현완료. 04-review FAIL 0/WARN 0, 전체 1622 passed skip 0. 상세는 `packages/P6-memory/04-review.md`, 이력은 journal 2026-09-29.

**FIX-015 가 고친 것**: `app/agent/propose.py` 의 `PROPOSAL_ARG_SCHEMA.facts.key` 에 `app.memory.FACT_KEYS` 9종 enum(**제품 코드 실질 변경은 상수 한 줄**). 전체 **1624 passed skip 0** · `tools_check` 7/7(= S3.2 무변경의 증거). **실 LLM 왕복도 통과** — 발화 4건에서 제안된 키가 `hobby`·`workplace`·`likes`·`dislikes` 로 `FACT_KEYS` 밖 0건. **결정적 증거는 trace 171**: 발화에 "**소속이** 네이버로 바뀌었어" 가 그대로 있는데도 LLM 이 `소속` 이 아니라 `workplace` 를 골랐다(수정 전 같은 자리에서 나온 것이 `소속`·`직장`·`이직`). 증거 `fixes/evidence/FIX-015/20260930-0100-real-llm-check.txt`. **남는 한계**: 4발화 1회 관측이고 enum 은 유도이지 거부가 아니다 — 어휘 밖 키가 다시 나오면 거부안(`update_person` 어휘 검사)을 별건으로 올린다. 이미 저장된 `소속`·`직장` 행은 지우지 않았다.

**FIX / CR 판단 근거(같은 유형이 또 오면 재사용)**: **어휘·규칙을 정한 카드가 있는가** 로 갈린다. 이번엔 `grep -rln "FACT_KEYS|사실 키|고정 어휘" docs/wiki/decisions/ docs/wiki/specs/ docs/proposal.md CLAUDE.md` 가 **0건**이었고, `S3.2` 는 시그니처만 적어 어휘를 걸어도 `tools_check` 7/7 이 유지됐다 → 원칙·D·S 를 안 바꾸므로 **FIX**. D-5 는 루프를 자유 키로 **정한** 게 아니라 P6-memory 의 **범위를 그은** 것이다.

active: **none** | frozen: none | 브랜치 `dev2`(작업·실험) | main = `1e4afb4` · origin/dev = `e48ac4c` · **origin/dev2 = `26dcd22`(최신, 여기서 작업)** | Docker DB `capstone2-postgres-1`(5433): 개발 DB `relationship`, 테스트 DB `relationship_test` — 5432·5434 는 다른 프로젝트

## 커밋 안 된 변경
- FIX-016 커밋 전이면: `app/agent/respond.py`·`app/agent/loop.py`·`tests/test_agent_loop.py`·`docs/wiki/fixes/FIX-016.md`·`fixes/evidence/FIX-016/`·`CURRENT.md`·`journal.md`·이 파일. 전부 한 커밋으로 묶는다(`/commit`, Refs `FIX-016 P5-loop P6-memory S3.2 원칙7 원칙9`).
- journal 의 COMMIT·PUSH 줄은 훅이 커밋 뒤에 적으므로 늘 한 박자 늦게 다음 커밋에 실린다 — 따로 처리할 일이 아니다.

## 바로 다음에 할 것
**진행 중인 작업이 없다.** FIX-016 커밋 뒤 아래에서 고른다.

1. ~~FIX-016 응답 문구~~ — **완료(2026-10-02)**. ~~dev 승격~~ — 완료(`36c288e`, main 승격은 보류).
0. **P6-briefing 계획 승인 완료(2026-10-02 14:10) — `CURRENT active: P6-briefing`.** 계획 문서 커밋 `688c4a4`(dev2 푸시됨). **U1 골격 완료**(backend-agent, 1643 passed skip 0, 커밋은 journal COMMIT 줄). U1 커밋 `e2155f9`. **U2 대상 선정 완료**(1654 passed skip 0, 잠금 제거 시 동시 실행 테스트 실패 확인, 테스트 DB 잔여 0 — 메인 세션 재확인). U2 커밋 `db3c645`. **U3 브리핑 입력 조립 완료**(1660 passed skip 0, 기존 툴·메모리 코드 무변경 — 메인 세션 재확인). U3 커밋 `cfb55ea`. **U4 문장 생성기·검증기 완료** + 사용자 요청으로 **실 API(OpenAI gpt-4o-mini) 왕복 2회**(`evidence/20261002-1601-u4-real-llm.txt`·`-1604-…-after-fix.txt`). 뜻 반전 방어 동작 확인. 금지 표현 빈틈 2건을 사용자 결정으로 고침(요약 줄에도 검사, `힘들`·`마음을`·`배려` 추가) → **1697 passed skip 0**. 남은 품질(패턴 문장화가 규칙 값 복사·요약 줄 반말)은 U8·P10. U4 커밋 `a2f032d`. **U5 실행 함수 완료** — 실 OpenAI 끝에서 끝까지 확인 통과(개발 DB 사용자 `brief-u5-check`, 행 남김) + 사용자 결정으로 DB 오류도 일정 단위 격리(연결 끊김만 올림) → **1707 passed skip 0**. `run_briefings(ctx, *, composer, notifier, schedule_id, trigger, lead_hours)` — 열린 세션을 받는다(R-5). **다음 = U6 `POST /briefings/run`**(L-004 승인 전 상세 설명, 사용자는 실 API 확인을 원함). 실 API 확인 스크립트는 scratchpad 의 `u4_real_llm.py`(커밋 안 함, 내용은 evidence 머리 참고) — 권고 R-1: `SKIP LOCKED` 동시 실행 테스트는 `db_session` 롤백 픽스처로 재현 불가, U2 03-log 에서 커밋 픽스처 방식 정함. 이하 경과 기록: **P6-briefing 01-plan** — 사용자 착수 승인(2026-10-02, L-004 architect 마커 소비) → architect 초안 완료(`packages/P6-briefing/01-plan.md`, U1~U8, 판정 표 30행). 결정 A~K **사용자 확정 = 전부 권장안**(01-plan "확정" 줄). `verify-plan.sh` FAIL 1(02-plan-verify 없음, 정상)/WARN 0 — `evidence/20261002-1206-verify-plan.txt`. verifier 1차 02-plan-verify = **보류**([필수] H-1 `JudgeTimeout` 없는 이름 · H-2 결정 B 는 S3.6 좁힘). 사용자 승인으로 메인 세션이 문서만 고침(01-plan 21·6·28행, S3.6 카드 보충 줄, resolution-plan §3.6 보충 줄, 05-remediation 해결 단계) → **verifier 2차 재검증 진행 중**. 다음: 통과면 계획 승인 → `CURRENT active` → 계획 문서 커밋. 권고 R-1·R-2·R-4·R-5·R-6 은 U2·U4·U5·U7 03-log 에서. 아직 미커밋.
2. **`dev` 승격 검토** — dev2 의 P6-memory + FIX-015 + FIX-016 커밋을 `git push origin dev2:dev` 로 올린다. **승인 마커(`approve-commit.sh --push`) 가 먼저**이고, 푸시 뒤에는 L-003 대로 멈춰 사용자 결정을 기다린다. 승격 근거는 pytest·게이트다(P9 미착수라 실서버 배포는 아직 없다 — 2026-09-15·09-23 과 같은 판단).
3. ~~`P6-briefing` 착수~~ → 위 0번에서 진행 중. **FIX 후보 추가(결정 G)**: `likes`/`dislikes` 뜻 반전 — 관측 사례(trace 181)의 출처는 승격 추출기가 아니라 **루프 제안기 `app/agent/propose.py`** 다(이전 HANDOFF 가 `build_extract_prompt()` 로 잘못 적었다, architect 확인). 손볼 자리: `propose.py`(와 `extract.py`) 키 설명에 부정 표현 → `dislikes` 지시.
4. 그 밖 FIX 후보 3건(아래 "열린 질문"): `/health` 빈 DB · `update_person` 부분 반영 · `memory_promote` `source` 키 비대칭(코드 한 줄, 문서는 이미 고쳤다).
5. 그 뒤 패키지 순서: P6-briefing → P8 인물 카드 → P9 AWS(Terraform).

## 이 세션에서 배운 것 (다음에 재사용)
- **04-review 를 verifier 에 맡기면 메인 세션 몫이 남는다** — `review-index.md`·`registry.md`·`01-plan` 체크박스·`backlog` 는 verifier 가 고치지 않는다(계획·문서를 고치지 않는 역할이라서). 04-review §4·§5 가 "바꿔야 할 내용" 을 적어 주므로 그대로 옮기면 된다. 그 뒤 `verify-impl.sh` 를 **한 번 더** 돌려야 WARN 이 사라진 것을 증거로 남길 수 있다.
- **verifier 가 넘긴 [권고] 중 "문서가 사실과 다르다" 는 그 자리에서 닫는다.** 이번에 `docs/RUNNING.md` 202행이 그랬다(`memory_promote` 는 `source` 로 갈린다고 적었는데 실제로는 직접 링크 행에만 있다). 코드 수정은 별건이어도 **틀린 문서를 남기는 것은 별건이 아니다**(사실성 규칙).
- **FIX 인지 CR 인지는 "어휘·규칙을 정한 카드가 있는가" 로 갈린다.** grep 한 번이면 끝난다 — 아래 §"FIX / CR 판단 근거" 에 이번 판정을 통째로 남겨 뒀다.
- **`.env` 는 셸에서 올리면 훅이 막지 않는다**(`set -a; . ./.env; set +a`). 다만 명령 문자열에 `.env` 가 들어간 **읽기·존재 확인**(`cat`, `[ -f .env ]`)은 `safety-guard` 가 막는다 — 존재 확인을 건너뛰고 바로 기동하면 된다.

## 다음 패키지가 알아야 할 것 (04-review §7 요약)
- 진입점은 하나: `app.memory.after_record(ctx, person_ids, extractor=None, *, fact_keys_by_person=None, event_ids_by_person=None)` — 루프 `_record()` 뒤 한 자리에서만 부른다.
- `person_facts` 에 **세 출처가 섞여 있다**: `pattern:*`(규칙, confidence 1.0, value `"{n}회 (날짜…)"`) · 승격 사실(`FACT_KEYS` 9키) · 루프 직접 사실(**FIX-015 이후 같은 9키로 유도된다. 다만 유도이지 거부가 아니므로 옛 자유 키 행(`소속`·`직장`·`이직`)이 DB 에 남아 있고 앞으로도 섞일 수 있다**). P8 "원문 펼치기" 는 `fact_sources → events.raw_utterance`(조회 API 는 아직 없다). **이벤트 없이 사실만 쓴 턴은 링크가 없다**(`action: unlinked`, `reason: no_event_this_turn`) — 카드에서 원문을 못 펼치는 사실이 존재한다.
- **미승격 판정은 `agent_traces` 를 상태로 쓴다**(결정 B(ii)) — **trace 를 지우면 승격이 다시 돈다.**
- `memory_promote` 는 세 종류다. 승격 횟수 = `considered_event_ids` 가 비어 있지 않은 행의 수(`docs/RUNNING.md` 202행 표).
- 한계: 새 이벤트 없이 시간만 흐르면 패턴이 낡는다(결정 C-5) → 브리핑 직전 재계산이 필요한 이유.

## 옛 세션에서 끝난 것 (상세는 journal·04-review)
- **P5-loop 완료** → main 승격. **FIX-005** 사용자 시간대(기본 서울) · **FIX-006** pytest 는 항상 테스트 전용 DB `relationship_test` 에만 붙는다. 셋 다 main(`1e4afb4`)에 있다.
- 09-28~29 전반부는 **Windows → Mac 이전으로 조용히 망가진 하네스 복구**였다 — FIX-008(훅이 macOS 에 없는 `python` 을 불러 **차단형 가드 5종이 전부 열려 있었다**) · FIX-010(브랜치 3단계) · FIX-011(**구현 검증이 테스트를 한 건도 안 돌리고 통과했다**) · FIX-012(DB 기본 포트 5433) · FIX-013(커밋+푸시를 묶으면 후처리가 건너뜀).

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
