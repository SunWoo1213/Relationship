# P2b-person-delete · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-11-09

읽은 것: `01-plan.md` 전문(결정 A~K `확정:` 줄 포함) · `docs/backlog.md` 36~39행 · `.claude/skills/devlog/SKILL.md` "정합성 점검표" · `docs/proposal.md` 2장 표(58~66행)·9장 260행 · `docs/wiki/security.md` §4·§5 · `docs/wiki/specs/S3.1-schema-v2.md` 12~24행 · `S3.2-tools-v2.md` 13행 · `decisions/D02`·`D15`·`D16` "코드에서 지켜야 할 것" · `docs/wiki/packages/P2-tools/04-review.md` 88~118행 · `packages/P8b-persons-grid/01-plan.md` 147행 · `docs/wiki/INDEX.md` 67~74행 · `registry.md` 52·59·61·79·170·216·225·227·236·246~256행 · `bash .claude/scripts/gitlog.sh P2b-person-delete P2-tools`(태그 `P2b-person-delete` 커밋 0건, HEAD `f67d8e4` = dev = main) · 코드 직접 확인: `app/db/models.py`·`alembic/versions/0001_schema_v2.py`·`app/main.py`·`app/tools/types.py`·`app/tools/persons.py`·`app/tools/context.py`·`app/er/pipeline.py`·`app/er/judge.py`·`app/agent/loop.py`·`app/api/routes.py`·`app/api/read.py`·`app/memory/promote.py`·`scripts/run_pilot_eval.py`·`evaluation/runner.py`·`tests/test_schema_models.py`·`tests/helpers_read_api.py`·`web/src/api/client.ts`·`web/src/components/ui/`·`.claude/scripts/save_evidence.py`·`.claude/scripts/verify-plan.sh`.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `python3 .claude/scripts/save_evidence.py P2b-person-delete verify-plan -- bash .claude/scripts/verify-plan.sh P2b-person-delete` → `evidence/20261109-1626-verify-plan.txt`

1차(메인 세션, 이 문서 작성 전): `evidence/20261109-1619-verify-plan.txt` — `FAIL=1`(02-plan-verify 없음) `WARN=2`. 2차(이 문서 작성 후, verifier 실행, 파일 전체):

```
# 명령: bash .claude/scripts/verify-plan.sh P2b-person-delete
# 시각: 2026-11-09T16:26:34+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: f67d8e4 (dev2)
# exit: 0
# ---
== verify-plan P2b-person-delete  (2026-11-09 16:26) ==
PASS  존재: docs/wiki/packages/P2b-person-delete/01-plan.md
PASS  존재: docs/wiki/packages/P2b-person-delete/02-plan-verify.md
PASS  패키지 id 등록됨: P2-tools
PASS  Refs 있음: - [ ] U1 인물 참조 판별 규칙(순수 함수) + 쓰는 곳 전수 목록 — [backend-agent] `
PASS  Refs 있음: - [ ] U2 삭제 서비스 `delete_person` — [backend-agent] `app/api/d
PASS  Refs 있음: - [ ] U3 HTTP `DELETE /persons/{person_id}` — [backend-agent
PASS  Refs 있음: - [ ] U4 (결정 B 가 "포함"일 때만) 인물 카드 삭제 버튼 + 인라인 확인 — [frontend-
PASS  Refs 있음: - [ ] U5 자동 판정 전체 + 문서 — [backend-agent: 판정 실행·`tests.md`·`r
PASS  backlog 일치: `DELETE /persons/{id}` — 인물 단위 완전 삭제 / 의존: P2 / 수용기준: 인물·별칭·
PASS  의존 완료: P2-tools
PASS  의존 완료: P3-er
PASS  의존 완료: P5-loop
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/api/delete.py
PASS  registry 중복 없음: tests/test_person_refs.py
PASS  registry 중복 없음: tests/test_person_delete.py
PASS  registry 중복 없음: tests/test_api_person_delete.py
PASS  registry 중복 없음: docs/wiki/packages/P2b-person-delete/tests.md
WARN  registry 에 다른 패키지로 이미 있음: tests.md → | 테스트 | 카드 테스트 22건(`card.test.tsx` — 목록 서버 순서/4필드/빈·실패/해시, 사이드바 동일 목록·같은 컴포넌트 im
| 문서 | 테스트 기록 — 프론트 Vitest 135건·E2E 4건을 표 1줄씩(무엇을 확인·입력 → 기대·결과·검출한 변이 ID), 총계와 
WARN  registry 에 다른 패키지로 이미 있음: save_evidence.py → | 스크립트 | 증거 저장 전용 통로 — 명령을 가드 검사 후 실행해 출력 전체·머리줄 5개·exit 를 evidence 에 직접 저장(비밀 검
== 결과: FAIL=0 WARN=2 ==
```

### WARN 2건 판정 — 둘 다 오탐(소견 없음)
- `WARN registry 에 다른 패키지로 이미 있음: tests.md` — `verify-plan.sh` 99행은 "## 산출물" 절의 `- ` 글머리 줄에서 `[A-Za-z0-9_./-]+[.][a-z]{1,5}` 토큰을 뽑아 `registry.md` 에 `grep -F` 한다. 01-plan 70행 글머리 `docs/wiki/packages/P2b-person-delete/tests.md — 테스트 1건 = 1줄(P8 `tests.md` 표 모양 …)` 에서 전체 경로는 `PASS registry 중복 없음` 으로 통과했고, 같은 줄 설명문의 bare 토큰 `tests.md` 가 registry 의 P8-frontend `docs/wiki/packages/P8-frontend/tests.md` 행에 걸린 것이다. 파일 경로가 다르므로 중복 구현이 아니다.
- `WARN … save_evidence.py` — 01-plan 71행 `docs/wiki/packages/P2b-person-delete/evidence/*.txt — save_evidence.py 산출물` 의 설명문에서 도구 이름 `save_evidence.py` 가 토큰으로 뽑힌 것. 이 패키지는 `.claude/scripts/save_evidence.py` 를 만들지 않고 쓰기만 한다(registry 그 행은 도구 등록). 오탐.

FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다. — 2차 FAIL 0, WARN 2 는 위 오탐 판정으로 소견을 만들지 않는다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 58~66행 2장 표 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나·톤 설정 / 음성 입력 / 네이티브 앱" — 01-plan 51~60행 "하지 않는 것" 에 "인물 간(A–B) 관계 정리 — 저장 자체를 안 한다(원칙7)", "새 화면·새 라우트·대화상자 — 원칙5" 가 있고, 포함 범위(44~50행)는 `DELETE /persons/{person_id}`·JSONB 정리·카드 안 인라인 확인·테스트·문서뿐이다. 삭제 자체는 제외 항목이 아니라 포함 근거가 있다: `docs/proposal.md` 260행 9장 리스크 표 "제3자 개인정보 \| 별칭 저장, **인물 단위 완전 삭제**, 최소 수집, 암호화" · `docs/wiki/security.md` §5 첫 줄 "인물 단위 완전 삭제 API (`DELETE /persons/{id}` → CASCADE)". 결정 G (i) 가 "이름·발화만 남는 trace" 를 범위 밖으로 두는 것도 backlog 38행 "`person_id` 참조" 글자 안이다(이름 문자열 삭제는 결정 G (iii) 에서 비추천으로 기각) |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | CLAUDE.md 원칙5 "프론트 화면은 3개로 고정" — 01-plan 213행 "확인은 **인물 카드 화면 안의 인라인 블록**이라 새 화면·새 라우트가 아니다. `Dialog`/`Sheet` 를 쓰면 P8b 판정 12행 불변식이 깨지므로 쓰지 않는다", J-13 ⑤ 기대 "`web/src/components/AppShell.tsx` **1파일뿐**" ⑦ `routes.ts`·`ChatScreen`·`BriefingScreen` diff 빈 출력; `packages/P8b-persons-grid/01-plan.md` 147행 판정 12행 "불변식 — 화면 3개·라우트 밖 패널 1개(원칙5…) `grep -rlE "Sheet\|Dialog\|Drawer" web/src --include=*.tsx \| grep -v ui/` → `AppShell.tsx` 1파일뿐" — 내가 지금 실행한 같은 grep 결과도 `web/src/components/AppShell.tsx` 1줄(기준점 f67d8e4). `web/src/components/ui/` 목록 `badge button card collapsible sheet skeleton sonner tabs` — 01-plan 사실 6 "dialog·alert-dialog 가 없다 … 8개" 와 일치. 원칙7 경계 — A-3 문구는 고정 문장 2개(삭제 안내·실패)이고 상담·조언 문장이 없다. 원칙8 — 01-plan 252행 C-2 (a) "평가는 운영 trace 를 쓰지 않는다(사실 3 — U1 확인)"; 코드 근거 `scripts/run_pilot_eval.py` 58행 "결정 D(i)(시나리오별 트랜잭션 롤백) 때문에 `agent_traces` 는 **실행 중에만** 조회된다", `evaluation/runner.py` 6·17행 "격리 경계 열기 — `ctx.session.begin_nested()` 세이브포인트 … 경계 되돌리기 — 세이브포인트 rollback" — 평가 trace 는 커밋되지 않으므로 운영 DB 의 trace 행 삭제가 평가 산출물(`evaluation/`·`reports/`)에 닿을 경로가 없다. 다만 01-plan 32행 "평가 스크립트 중 trace 를 읽는 것은 `scripts/run_pilot_eval.py` 하나다" 는 부정확 — `evaluation/runner.py` 370행 `select(func.count()).select_from(AgentTrace).where(AgentTrace.session_id == ctx.session_id)` 도 읽는다(결론은 같다 → §3 R-2 [권고]). 원칙9 — C-2 (a) 가 "그 인물이 후보로만 끼었던 ER 판정 행의 근거도 함께 사라진다" 는 비용을 명시하고, 265행 확정 줄 "C-2 (a) 참조 trace 행 통째 삭제(**원칙9 비용 수용**) — 사용자 2026-11-09 (C-1·C-2 사용자 선택)" 으로 사용자가 비용을 알고 골랐다. 결정 H (i) 삭제 trace 미기록은 registry 216·225행 선례(`/push/subscriptions`·읽기 API 가 trace 를 남기지 않음)와 같고 원칙9 의 "판정" 이 아니다. 원칙1~4·6 은 ER·임계치·패턴 코드(`app/er/`·`app/agent/`·`app/memory/`)를 건드리지 않아 해당 없음(J-6 ②·J-11 ② 무변경 diff 로 기계 판정). 원칙7 "툴 7종" 표 — 결정 I (a) + J-6 ① `tools_check.py` `7/7 ok` |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | 01-plan 4행 "기대는 결정: 없음(새 D 카드 없음)" — 인용 D 카드가 없으므로 영향받을 수 있는 카드 3개를 내가 열어 대조했다. `decisions/D02-ask-user-async.md` 11행 "동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다" — 이 계획은 `ask_user` 코드를 바꾸지 않고 `pending_questions` 행만 지운다(결정 C-1), `app/tools/` 무변경(J-6 ②). `decisions/D16-query-turn.md` 29행 "`app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로(`scripts/tools_check.py` 7/7)" — 결정 I (a)·J-6 ① 과 같은 판정. `decisions/D15-persons-screen-layout.md` 25행 "라우트는 여전히 3경로(`#/chat`·`#/persons`·`#/briefings`)" — J-13 ⑦ `routes.ts` diff 빈 출력; 27행 "상세 모드는 `data-testid="card-wrap"` 가 `mx-auto w-full md:w-3/4`" — U4 는 `CardView`(`PersonCardScreen.tsx` 223행 `function CardView`) 안에 버튼·블록을 더할 뿐 폭 클래스를 바꾸는 지시가 없다(기존 `card.test.tsx` 단언 무수정, 01-plan 82행) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.1-schema-v2.md` 24행 "인물 단위 완전 삭제가 가능해야 함(기획서 9장 개인정보) → FK ON DELETE CASCADE" — 결정 D (a) "기존 DB CASCADE 그대로 … 마이그레이션 0" 과 J-7 `alembic check` → `No new upgrade operations detected.`. 사실 1 "FK CASCADE 는 이미 전부 걸려 있다" 를 직접 확인: `app/db/models.py` `grep -n ondelete` → **133·152·175·178·195·212행** 6곳 모두 `ondelete="CASCADE"`(계획 행 번호와 정확히 일치), `alembic/versions/0001_schema_v2.py` 24행 "(e) All 6 foreign keys keep `ondelete="CASCADE"` -- already correct." · 184·203·226·244·257·263행 6곳, `tests/test_schema_models.py` 204행 `test_all_six_foreign_keys_have_ondelete_cascade`·312행 `…on_delete_cascade_in_postgresql_dialect`(J-1 ① `-k "cascade or fk"` 가 실제로 2건을 고른다). S3.1 12·14행 `pending_questions(… context …)`·`agent_traces(… input, output …)` 에 `person_id`·`user_id` 컬럼이 없다 — 사실 3 과 일치. `specs/S3.2-tools-v2.md` 13행 `ask_user … → PendingQuestion` 등 7행 — 결정 I (a) "HTTP 엔드포인트만, 툴 7종 불변" 으로 시그니처 v2 무변경, J-6 ① `7/7 ok`. 사실 5 직접 확인: `app/tools/types.py` 196행 `class ConfirmationRequired(ToolError)`, `app/main.py` 38행 "`ConfirmationRequired` \| 422 \| `{"detail":{"code":"confirmation_required","reason": e.reason}}`" · 133~138행 핸들러 · 189행 등록 — `main.py` 무변경 재사용 가능. 사실 4: `app/tools/persons.py` 417~429행 `_owned_person` "없거나 다른 `user_id` 소유면 `PersonNotFound`", `app/main.py` 111행 `_not_found_handler` → `{"detail": {"code": "not_found"}}`, 184행 `add_exception_handler(PersonNotFound, _not_found_handler)`. 임계치·확신도 코드(`app/er/`)는 J-6 ② 무변경 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `packages/P2-tools/04-review.md` 118행 `결과: 완료`, 닫는 커밋 `b676799`(gitlog.sh 태그 P2-tools: "docs(P2-tools): 완료 — verifier 04-review 완료 판정·사용자 승인, R6 R7 R10 R18 구현완료, 패키지 닫음"). 이어받는 소견 F-4d2507 은 `P2-tools/04-review.md` 90행 "**F-4d2507 [권고, 열림 → architect 인계]** security.md §5 '인물 단위 완전 삭제 API' 를 받을 backlog 항목이 여전히 없다" → `docs/backlog.md` 38~39행으로 신설됨. verify-plan 2차 `PASS 의존 완료: P2-tools / P3-er / P5-loop`(01-plan 5행이 P3·P5 를 JSONB 모양의 출처로 들었기 때문). P4 게이트: 패키지 번호가 2 라 스크립트 게이트 대상이 아니고, 실제 trace 모양 기준점 HEAD `f67d8e4` 는 P5b 완료 커밋(gitlog.sh "dev2 f67d8e4 = dev = main"). `CURRENT.md` `active: none`·`frozen: none` — 활성 패키지 충돌 없음. 태그 `P2b-person-delete` 커밋 0건(gitlog.sh) — 선행 작업 없음 확인 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 38행 "`DELETE /persons/{id}` — 인물 단위 완전 삭제 / 의존: P2 / 수용기준: 인물·별칭·사실·이벤트·일정이 FK CASCADE 로 함께 지워지고, `pending_questions.context`·`agent_traces.input/output` JSONB 안의 `person_id` 참조도 정리된다. 삭제 전 확인을 요구하고, 남의 인물은 지울 수 없다 / Refs: F-4d2507 security§5 (P1 04-review §7)" = 01-plan 158행(접두 `- [ ] [backend-agent]` 만 다름, `[backend-agent]` 는 담당 표기). verify-plan 2차 `PASS backlog 일치`. 해석 표(164~170행 ㄱ~ㅁ)가 구절 5개를 J-1~J-5 로 1:1 대응시키고 새 기준을 더하지 않는다 |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan U1(108행) "Refs: P2b-person-delete F-4d2507 security§5 원칙9" · U2(122행) "… 원칙8 원칙9" · U3(135행) "Refs: P2b-person-delete F-4d2507 security§5" · U4(144행) "… security§5 원칙5" · U5(154행) "… F-4d2507 security§5 원칙8". verify-plan 2차 `PASS Refs 있음` 5줄. 단위마다 담당 에이전트·판정 명령·증거 이름·변이 표(V1-1~9·V2-1~8·V3-1~4·V4-1~5)가 있다 |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §5 "모든 조회는 `user_id` 조건을 넣는다" — 결정 E "`_owned_person` → `PersonNotFound`", U2 ⑥ "`DELETE FROM persons WHERE id = :pid AND user_id = :uid`", V2-4 "`user_id` 조건 제거 → 남의 인물 `PersonNotFound` + `assert_no_writes`". §5 "저장 최소화" — 결정 A-2 (i) "본문이라 접근 로그에 제3자 이름이 남지 않는다", (iii) 쿼리 문자열 안은 "제3자 이름이 URL·접근 로그에 남는다 … 비추천" 으로 기각, 결정 F 응답 "이름·원문 없음", U3 테스트 "응답·로그에 이름·원문 미포함". §4 "셸에서 `DROP`/`TRUNCATE` 금지" — 계획의 삭제는 제품 코드의 행 단위 `DELETE`(FK CASCADE)이고 셸·마이그레이션의 DROP 이 아니다(J-7 `alembic/` 무변경). §4 "외부 전송 금지" — 외부 호출 추가 없음. 비밀 — `.env`·키 문자열 언급 없음(`save_evidence.py` 비밀 검사 자동). 한계 명시: 01-plan 60행 "`user_id` 컬럼이 없는 JSONB 테이블은 인물 id(전역 유일 IDENTITY)로만 정리한다" — `app/db/models.py` 85행 `Identity(always=False)` 로 센티널 명시 삽입이 가능하고 인물 id 는 단일 시퀀스라 다른 사용자 행이 같은 id 를 가리킬 수 없다(결정 K 근거). 남는 것(이름·발화만 있는 trace)은 결정 G (i) 확정 줄대로 "security.md §5 에 한계로" 밝힌다 |

### 사실 주장 직접 검증 결과 (계획 "코드에서 확인한 사실" 1~7)
| 주장 | 확인 | 결과 |
|---|---|---|
| 사실 1 FK CASCADE 6개 `models.py` 133·152·175·178·195·212 · `0001_schema_v2.py` 24행 | `grep -n ondelete` 두 파일 | **일치**(행 번호까지) |
| 사실 2 `push_subscriptions` 는 `user_id` 단위, `persons` FK 없음 | `models.py` 247~261행 `ForeignKey` 0건, `user_id` 컬럼·`UniqueConstraint("user_id","endpoint")` | **일치** |
| 사실 3 JSONB 참조 모양 6종 — `id`(`PersonOut.to_dict` 43행) · `person.id`(`Candidate.to_dict` 61~63행, `BriefingOut` 152~154행) · `candidate_ids`(pipeline.py 200행 `{c.display_name: c.person_id}`) · `resume.person_ids`(loop.py 303·310행 `PendingResume.person_ids: dict[str,int]`, 476·490행 `"resume": resume.to_dict()`) · `matched_person_id`(pipeline.py 192행) · `candidate_person_ids`(judge.py 523행) · `candidates[].person_id`(judge.py 142행) · `EventOut`/`ScheduleOut` 의 `id`+`person_id`(types.py 84~106행) | 각 파일 해당 행 Read/grep | **일치**. `@traced` 쓰기 자리 `context.py` 196~232행(`tool_error` 행 `input=input_payload`, 성공 행 `output=to_jsonable(result)`) 일치 |
| ↑ **보정(U1 리뷰 2026-11-09, R-U1-1)** | — | `resume.person_ids` 는 오기 — loop.py 303·310행은 `ResolveOutcome.person_ids`(`loop_resolve_done.output`)이고 `PendingResume.to_dict()` 에 `person_ids` 는 없다. 모양 자체(언급→id 사전, 규칙 4)는 맞다. |
| 사실 3 "trace 를 읽는 제품 코드 두 곳" `promote.py` 136행 `output["person_id"]`, `read.py` 302행 | Read | **일치** |
| 사실 3 "평가 스크립트 중 trace 를 읽는 것은 `run_pilot_eval.py` 하나" | `grep -rln AgentTrace scripts/ evaluation/` | **부정확** — `evaluation/runner.py` 370행도 `AgentTrace` 를 집계한다(세션 한정 count). 다만 `runner.py` 6·17행 세이브포인트 rollback 과 `run_pilot_eval.py` 58행 "실행 중에만 조회" 로 결론(평가는 운영 trace 를 쓰지 않는다)은 유지 → R-2 |
| 사실 4 `_owned_person` 417~429행, 공통 404 `main.py` 111·184행, `routes.py` 444~453행 `read_person_card` | Read | **일치** |
| 사실 5 `ConfirmationRequired` types.py 196행, 핸들러 main.py 38·133~139행 | grep | **일치**(등록은 189행) |
| 사실 6 `client.ts` 45행 `method?: 'GET' \| 'POST'`, `ui/` 8개, 불변식 grep → `AppShell.tsx` 1파일 | grep·ls·같은 grep 실행 | **일치** |
| 사실 7 비-툴 엔드포인트 trace 미기록 선례 registry 216·225행 | registry Read | **일치**(216행 `/push/vapid-public-key`·`/push/subscriptions`, 225행 `GET /persons` 읽기 전용) |
| 재사용 표 — `snapshot_db`·`assert_no_writes` "9테이블"(`tests/helpers_read_api.py` 56·72행), `scripts/tools_check.py`·`scripts/mypy_check.py` 존재, `alembic check` 부명령 존재 | ls·grep·`alembic --help`·`helpers_read_api.py` 36~46행 `_COUNTED_MODELS` Read | **일치** — `_COUNTED_MODELS` 는 `AgentTrace, Person, PersonAlias, PersonFact, FactSource, Event, Schedule, PendingQuestion, PushSubscription` 9개(`agent_traces`·`pending_questions` 포함 → V2-5 가 JSONB 정리 누출도 행 수로 잡는다). registry 236행 "8테이블" 쪽이 오래됐다 → R-3 |

### 판정 표 J-1~J-15 덮음 확인
- ㄱ CASCADE 5종(`persons`·`person_aliases`·`person_facts`·`events`·`schedules`)+`fact_sources` → J-1 ①②③(③ `grep … delete\((PersonAlias|…)\) app/api/delete.py` 0줄로 "앱이 직접 지우지 않음" 까지 기계 판정). ㄴ `pending_questions.context` → J-2. ㄷ `agent_traces.input/output` → J-3 ①②(V1-5·V1-6 과잉 판정 금지 음성 픽스처 포함). ㄹ 삭제 전 확인 → J-4(+J-13 화면). ㅁ 남의 인물 → J-5(상태·본문 바이트 동일 + `assert_no_writes` + 재삭제 404). 범위 통제 → J-6·J-7·J-11·J-12·J-13 ⑤⑥⑦/J-14. 회귀·품질 → J-8·J-9·J-10. 문서 → J-15. 빠진 구절 없음.
- 모든 판정이 명령 + 기대 출력 + 증거 이름을 갖고, 수용 기준 구절마다 **실패 조건**(센티널 `987654321` 텍스트 0건, 대조군 전후 동일, 쓰기 0, 404 본문 동일)이 값으로 정해져 있어 기계 판정 가능. 센티널 id 는 `models.py` 85행 `Identity(always=False)`(BY DEFAULT) 라 명시 삽입 가능 — 계획 122행 주장 확인.
- 실행 가능성 문제 2건은 §3 R-1 [권고](따옴표 쪼개짐·표 안 `\|` 이스케이프) — 결과를 바꾸지 않는 실행 요령이라 통과를 막지 않는다.

### 계획 품질 — "하지 않는 것"·단위 크기·기계 판정
- 하지 않는 것 10줄(51~60행) 각각 "왜" 가 붙어 있다(툴 8번째·마이그레이션·A–B·계정 삭제·되돌리기·대화상자·이름만 있는 trace·배포·멀티테넌시).
- U1(순수 함수+테스트) · U2(서비스+DB 테스트) · U3(라우트+스키마+HTTP 테스트) · U4(프론트) · U5(판정·문서) — 각각 커밋 하나 크기. U1 에 FIX-033 (b) 멈춤 지점 2개(새 JSONB 모양·`fact_sources` 교차)가 명시돼 구현자가 추측할 자리가 없다.
- 결정 A~K 의 `확정:` 줄 11개가 모두 채워져 있다(226·235·265·277·287·297·309·318·327·337·346행, 사용자 2026-11-09). 상수: `T` 류 신규 상수 없음, 센티널 `987654321`·`reason="person_delete"`·응답 키 8개(결정 F)·A-3 문구가 계획에 고정.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
[필수] 0건. [권고] 4건 — 통과를 막지 않으며, 구현 위임 프롬프트·03-log 에서 반영하면 된다. 05-remediation 소견으로 올리지 않는다(verify-plan FAIL/WARN 아님).

- **R-1 [권고] 판정 명령 실행 요령 2가지** — ① `save_evidence.py` 209행은 `--` 뒤 인자를 `" ".join(cmd_parts)` 로 이어 `bash -c` 에 넘기므로 셸이 벗긴 따옴표가 사라진다. J-1 ① `-k "cascade or fk"` · J-5 `-k "other_user or not_found"` 를 그대로 치면 pytest 가 `or`·`not_found` 를 파일 경로로 받아 실패한다(P5b 04-review 에서 겪은 문제). 우회: 따옴표를 한 겹 더 싸서 글자로 넘긴다 — zsh 예 `… -- .venv/bin/python -m pytest tests/test_api_person_delete.py tests/test_person_delete.py -q -k \"other_user or not_found\"` 또는 `'-k "other_user or not_found"'` 처럼 안쪽 큰따옴표가 인자 문자열에 남게 한다. ② J-13 ⑤ 의 `"Sheet\|Dialog\|Drawer"` 와 `\| grep -v` 는 마크다운 표 셀의 `|` 이스케이프다(사실 6·P8b 147행은 `"Sheet|Dialog|Drawer"`). 실행할 때 `\|` → `|` 로 되돌려야 한다 — BSD grep(macOS) 의 `-E` 에서 `\|` 는 리터럴 `|` 라 0줄이 나와 "불변식 통과" 로 오판할 수 있다. 메인 세션/구현자가 U5 위임 프롬프트에 이 두 요령을 적어 두면 된다.
- **R-2 [권고] 01-plan 32행 사실 보정** — "평가 스크립트 중 trace 를 읽는 것은 `scripts/run_pilot_eval.py` 하나다" → `evaluation/runner.py` 370행(`select_from(AgentTrace).where(session_id == ctx.session_id)` 건수 집계)도 읽는다. 둘 다 세이브포인트 rollback 안에서만 읽고(`runner.py` 6·17행, `run_pilot_eval.py` 58행) 삭제 API 를 부르지 않으므로 원칙8 결론은 그대로다. U1 ① 확인 범위를 "`scripts/run_pilot_eval.py` + `evaluation/`" 로 넓혀 03-log 에 적으면 된다(코드 변경 없음).
- **R-3 [권고] registry 236행 비고 갱신** — 01-plan 97·122·181행 "9테이블" 이 코드(`tests/helpers_read_api.py` 36~46행 `_COUNTED_MODELS` 9개)와 맞고, registry 236행 "8테이블 행 수 + …" 이 오래됐다(P7 이후 `PushSubscription` 추가분 미반영으로 보임). U5 의 registry 갱신 때 236행 비고를 "9테이블" 로 고친다 — 계획·코드 변경 없음.
- **R-4 [권고] 문서 정합 2건** — ① 01-plan 3행 상태 줄 "결정 A~K `확정:` 칸 비어 있음(메인 세션이 사용자에게 한 번에 묻는다)" 은 이제 사실과 다르다(11개 전부 확정). 활성화 커밋에서 "확정(사용자 2026-11-09) → verifier 통과" 로 갱신. ② U3 HTTP 테스트에서 DELETE 에 JSON 본문을 보내려면 `TestClient.delete()` 가 `json=` 을 받지 않으므로 `client.request("DELETE", url, json={"confirm": …})` 을 써야 한다 — 계획에 없는 결정이 아니라 httpx 의 제약이므로 위임 프롬프트에 한 줄 적어 두면 (b) 멈춤을 피한다.

## 4. 결정
결과: 통과
(L-006: 사용자 승인 줄은 쓰지 않는다. `결과: 통과` 면 메인 세션이 바로 활성화한다.)

근거 요약: 기계 검증 2차 FAIL 0(WARN 2 는 §1 오탐 판정) · 점검표 8/8 통과 · 계획이 주장한 코드 사실 7개 중 6개 정확, 1개(평가 trace 읽는 곳) 부정확하나 결론 불변(R-2) · 수용 기준 5구절이 J-1~J-5 로 전부 기계 판정되고 실패 조건이 값으로 고정 · 결정 11개 확정 · 원칙5·8·9 비용이 사용자 확정 줄에 명시.
