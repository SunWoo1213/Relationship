# P8-frontend U3 대기 질문·브리핑 조회 API — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — 코드에 요구하는 변경 없음. 01-plan 94행 계약(두 응답 모양·`list_pending` 재사용·헤더 없음 `[]`·422 규칙·trace 원천 두 조건·일정별 최신 1행·error 만 있는 일정 제외·`persons.user_id` 조인·기간 7일·정렬 2차 키·상한 20·원문 필드 0·쓰기 0·trace 0·`get_briefing` 미호출)을 전부 지키고, 내가 고른 변이 8건 중 계약을 실제로 깨는 6건이 전부 새 테스트에 잡혔으며(대조군 60 passed), 나머지 2건은 동치 변이(사전 소유 확인·response_model 이 막음)다. U1·U2 회귀 변이 각 1건도 여전히 검출된다. 전체 회귀 1942 passed·skip 0, ruff·mypy 기준선 유지, 비밀·손상·범위 밖 변경 0. 소견은 [권고] 6건뿐이고 커밋을 막지 않는다.
대상: 작업 트리(기준 HEAD `7031a19`) — `app/api/read.py`(`git diff --numstat` `122 6` — 삭제 6줄은 docstring 1행·import 5줄의 교체, 그 외 U1·U2 본문 무변경) · `app/api/routes.py`(`37 2` — 삭제 2줄은 import 두 줄 확장) · `app/api/schemas.py`(`28 0`) · 신규 `tests/helpers_read_api.py`(73행) · `tests/test_api_questions_pending.py`(133행, 8 테스트) · `tests/test_api_read_briefings.py`(415행, 22 테스트) · `docs/wiki/registry.md`(`6 0`) · 구현 증거 `evidence/20261012-1800-u3-*.txt` 5개. 위임 프롬프트대로 `HANDOFF.md`·`journal.md`·`fixes/FIX-033.md`·`01-plan.md`·`03-log.md` 의 변경은 대상 아님(01-plan 94행·03-log 맨 끝 "U3 시작" 항목만 근거 문서로 읽음).
근거 문서: `01-plan.md` 94행(U3 정의 — 사용자 확정값 3개) · 25행(읽기 전용 공통 규약·공통 404) · 55행(파일 지도) · 판정표 7·8·9·10·11행 · `03-log.md` 2026-10-12 17:05 항목(해석 2개·확정값 근거) · `app/briefing/run.py` 195·224~225행 · `app/briefing/types.py` 215·223행 · `app/tools/questions.py` 287~323행 `list_pending`·109~121행 `question_status` · `app/api/deps.py` 201~211행 `resolve_session_id`·223~242행 `build_chat_ctx`·304~310행 `get_now` · `app/tools/context.py` 91~104행 · `app/db/models.py` 110~115행(`updated_at` `onupdate=func.now()`) · `tests/conftest.py` 119~130행(`db_session` — 바깥 트랜잭션 + SAVEPOINT) · `app/main.py` 111~112·184~186행(공통 404) · CLAUDE.md 원칙9 · `docs/wiki/verification.md` "변이 시험 방법" · `docs/wiki/fixes/FIX-033.md` 규칙 (a)~(c) · `review-u2-read-raw.md` R-U2-2·R-U2-3·R-U2-4 · `docs/wiki/security.md` §1·§5.
내가 남긴 증거(모두 `docs/wiki/packages/P8-frontend/evidence/`): `20261012-1733-verifier-u3-tests.txt`(U3+U1+U2 -v, 60 passed) · `20261012-1733-verifier-u3-full-regression.txt`(1942 passed, skipped 0) · `20261012-1733-verifier-u3-lint.txt`(ruff·mypy 38/38) · `20261012-1733-verifier-u3-mutation.txt`(대조군 + 내 변이 V1~V8 + U1R·U2R 11회 출력 전체 + 원복 `git status`) · `20261012-1733-verifier-u3-mutplug.py.txt`(변이 플러그인 소스) · `20261012-1733-verifier-u3-grep.txt`(쓰기·trace·범위·비밀·손상 grep 전부).

---

## 1. 01-plan 94행 U3 계약 대조

| 계약(01-plan 94행 글자 그대로) | 코드 위치 | 테스트 | 판정 |
|---|---|---|---|
| `GET /questions/pending` → `[{question_id, status, kind, question, options}]` | `routes.py` 470행 `response_model=list[ChatPendingQuestionOut]`(`schemas.py` 85~93행, 5필드) · 483행 `ChatPendingQuestionOut(**q.to_dict())` — `PendingQuestionOut.to_dict()`(`tools/types.py` 121~128행) 키 5개와 동일 | `test_필드_5개_값_일치` — 응답 전체를 dict 동치로 단언 | 일치. **변이 V8**(모델에서 `kind` 누락) → 6 failed |
| 헤더 `X-Session-Id` 의 세션, 기존 `list_pending(ctx, session_id)` 재사용 — 새 조회 로직 금지 | 471행 `Depends(resolve_session_id)` · 483행 `list_pending(ctx, session_id)` · `read.py` 에 대기 질문 쿼리 없음(`grep PendingQuestion app/api/read.py` 0건 — helpers 에만 있음) | `test_다른_세션_질문은_제외` · `test_답변된_질문은_제외` · `test_만료_경계_24시간`(23:59:59 포함·정확히 24h 제외·25h 제외 — `question_status` 의 `<=` 와 일치) · `test_created_at_오름차순` | 일치. 구현자 변이 M21(세션 격리 제거) → 2 failed(구현자 표) |
| 헤더 없으면 빈 목록 | `resolve_session_id` 207~208행이 `uuid4` 를 발급하고 어디에도 저장하지 않음(R-11) → `list_pending` 결과 `[]` | `test_헤더_없으면_빈_목록_이고_쓰기_0` — `[]` + `assert_no_writes`(행 수 8개·`briefed_at`·`updated_at`) | 일치 |
| 형식 위반 422 는 `/chat` 과 같은 규칙 | 같은 의존성 `resolve_session_id`(`/chat` 311행과 동일) → `{"detail":{"code":"invalid_session_id"}}` | `test_형식_위반_세션_헤더는_422` — 5가지 위반값 모두 422 + 본문 동치 | 일치 |
| `GET /briefings`(선택 쿼리 `schedule_id`) → `[{schedule{id,title,scheduled_at}, person{id,display_name}, generated_at, composer, pattern_sentences[], lines[{text,basis}], suggestion\|null, push, trace_id}]` | `schemas.py` `BriefingRecordOut`(9필드)·`BriefingScheduleOut`(3)·`BriefingPersonOut`(2), `lines`·`suggestion`·`pattern_sentences` 는 기존 `BriefingLineOut`·`BriefingSuggestionOut`·`BriefingPatternSentenceOut` 재사용(basis 는 `BriefingBasisOut{fact_keys, event_ids}` 로 고정) · `read.py` 반환 comprehension 이 `output["composer"]`·`["push"]`·`.get("lines")` 등을 매핑 | `test_응답_필드_매핑_전체_값` — 최상위 9키·`schedule` 3키·`person` 2키 집합 동치 + 전 필드 값 동치(`generated_at`=trace `created_at`, `trace_id`=trace `id`) · `test_제안이_있으면_basis_그대로` | 일치. 구현자 M17(`generated_at` 오매핑)·M18(`trace_id` 오매핑)·M19(`push` 고정) 모두 FAIL(구현자 표) |
| 원천은 `briefing_compose` trace, 조건 `tool_name='briefing' AND step='briefing_compose'` **둘 다**(R-9) | `read.py` 306~307행 `.where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME).where(AgentTrace.step == STEP_BRIEFING_COMPOSE)` — 44행에서 `app.briefing.types` 상수 import(문자열 하드코딩 없음) | `test_run_과_error_행은_섞이지_않는다`(더 최근 run·error 행이 있어도 compose 선택) · `test_다른_tool_name_의_compose_step_은_제외` | 일치. **변이 V1**(step 필터 제거) → 3 failed(구현자 M3 과 건수·이름 동일) · 구현자 M4(tool_name 필터 제거) → 1 failed |
| 일정마다 가장 최근 1행 | `row_number() OVER (PARTITION BY output->>'schedule_id' ORDER BY created_at DESC, id DESC)` 서브쿼리 + `.where(ranked.c.rn == 1)` | `test_일정마다_최신_1행만`(삽입 순서 섞음) · `test_동률_created_at_이면_id_큰_행` | 일치. **변이 V4**(`rn == 1` 제거) → 2 failed(M15 와 동일) · **변이 V5**(분할 키를 person_id 로 — 구현자 표에 없음) → 4 failed · 구현자 M1·M2(정렬 방향) 각 1 failed |
| `output->>'schedule_id'`·`output->>'person_id'` 로 `persons.user_id = app_user_id()` 조인 | `trace_output["schedule_id"].astext.cast(BigInteger)` → `.join(Schedule, Schedule.id == ranked.c.sid).join(Person, Person.id == ranked.c.pid).where(Person.user_id == user_id)` · 라우트 495행이 `app_user_id()` 를 넘김 | `test_다른_사용자_일정은_제외`(응답에 남의 이름 0) | 일치. **변이 V2**(격리 제거) → 1 failed(M5 와 동일). 두 키 일치 검사 생략은 §3-③ |
| `briefing_error` 만 있는 일정은 넣지 않는다 | step 필터가 compose 만 남기므로 error 만 있는 일정은 서브쿼리에 행이 없음 | `test_error_만_있는_일정은_제외` · `test_schedule_id_error_만_있어도_빈_목록` | 일치(V1 의 3 failed 중 2건이 이 두 테스트) |
| 대상 일정 `scheduled_at ≥ now − 기간 상수`, `BRIEFINGS_LOOKBACK_DAYS = 7`, 미래 상한 없음 | `read.py` 73행 `BRIEFINGS_LOOKBACK_DAYS = 7`(주석에 사용자 확정 근거) · 목록 모드 `.where(Schedule.scheduled_at >= now - timedelta(days=BRIEFINGS_LOOKBACK_DAYS))`, `now` 는 `get_now()` 의존성 | `test_기간_경계_정확히_7일전_포함_7일_1초전_제외_미래_포함` — `assert BRIEFINGS_LOOKBACK_DAYS == 7` + 경계 3점 | 일치. **변이 V3**(`>=`→`>`) → 1 failed(M6 동일) · 구현자 M7(7→8)·M22(실시계) FAIL |
| 정렬 `scheduled_at` 내림차순 → 2차 키 `schedule_id` 내림차순 | `.order_by(Schedule.scheduled_at.desc(), Schedule.id.desc())` | `test_정렬_scheduled_at_내림차순과_2차키_id_내림차순`(같은 시각 2건 + trace 생성 순서 뒤섞음) | 일치. 구현자 M8(2차 키 asc)·M9(1차 키 asc) FAIL |
| 상한 `BRIEFINGS_LIMIT = 20`, 셋 다 코드 상수·환경변수 아님 | 77행 `BRIEFINGS_LIMIT = 20` · `.limit(BRIEFINGS_LIMIT)` · `grep os.environ app/api/read.py` 0건(설정값 import 는 `PATTERN_KEY_PREFIX` 뿐) | `test_상한_21개_일정이면_20개` — 21건 중 가장 이른 1건이 잘림을 id 리스트로 단언 | 일치. 구현자 M10(20→21)·M11(limit 제거) FAIL |
| 원문 필드 없음 | `BriefingRecordOut` 트리에 `raw_utterance` 필드 없음(`grep raw_utterance app/api/schemas.py` 는 U2 모델 2개·주석뿐) · `basis` 는 `BriefingBasisOut{fact_keys, event_ids}` 타입이라 모르는 키가 버려짐 | `test_응답에_raw_utterance_없음` — 감시 문자열·키 0회, `event_ids` 만 나감(두 모드) | 일치. **변이 V7**(응답 dict 에 `raw_utterance` 주입) → 60 passed = 동치 변이: pydantic 이 모르는 키를 버려 응답에 안 실림. 막는 것은 response_model 이고 `test_응답_필드_매핑_전체_값` 의 9키 집합 단언이 모델 변경을 잡는다 |
| DB 쓰기 0 · trace 0 | `grep -n "insert\|update\|delete\|\.add(\|commit(\|flush(\|traced\|AgentTrace("` → read.py 는 docstring 10행·`PersonFact.updated_at` 읽기(U1 기존)뿐, routes.py 470~495행 범위 0건(grep 증거) · `read.py` 의 `session.*` 호출은 전부 `execute(select…)` | `test_쓰기_0_trace_0_briefed_at_updated_at_불변`(200 두 번·404 한 번, `briefed_at` 값까지) · pending 쪽 `test_쓰기_0_trace_0`(세 경로) | 일치. 구현자 M23(`briefed_at` UPDATE 주입)·M24(`updated_at` UPDATE 주입) 둘 다 helpers 72~73행 단언에서 FAIL |
| `get_briefing` 툴 미호출 | `grep get_briefing\|run_briefings\|build_briefing_input app/api/read.py` → docstring 7행뿐 · `routes.py` U3 라우트는 `list_briefings` 만 호출 | (쓰기 0·`briefed_at` 불변 테스트가 간접 증거 — `get_briefing` 은 `briefed_at` 을 쓴다) | 일치 |
| 판정 `pytest tests/test_api_questions_pending.py tests/test_api_read_briefings.py -v` · 증거 `evidence/*-u3-read-questions-briefings.txt` | 구현 증거 `20261012-1800-u3-read-questions-briefings.txt` 30 passed · 내 재실행 60 passed(U1 12·U2 18 포함) | — | 일치 |

판정표 8행(세션 S 미답변 1·답변됨 1·만료 1, 세션 T 1, 헤더 없음 `[]`+쓰기 0, 형식 위반 422) = `test_쓰기_0_trace_0`+`test_다른_세션_질문은_제외`+`test_형식_위반…` 으로 충족. 9·10행(두 경로 실행·재실행·사용자 범위·원문·다른 step 혼입·error 만) 중 "실제 `POST /briefings/run`·`run_briefings(trigger="scheduler")` 로 만든 trace 를 읽는" 부분은 이 단위 테스트가 trace 행을 직접 넣어 대체했다 — compose `output` 키 모양은 `run.py` 224~250행과 대조해 같고(`_output()` 헬퍼가 그 키를 전부 가짐), 끝에서 끝 실행은 U9 전체 판정 몫이므로 결함 아님(R-U3-6 에 기록 요청).

## 2. 메인 세션 해석 2개(03-log 17:05 항목) — 계획·카드와의 정합

- **(ㄱ) "가장 최근" = `created_at desc, id desc`.** `agent_traces.created_at` 은 `server_default=func.now()`(`models.py` 277행)이고 PostgreSQL `now()` 는 트랜잭션 시작 시각이라, 같은 요청 트랜잭션 안에서 같은 일정의 compose 행이 두 번 생기면 `created_at` 이 동률이다(`run_briefings` 재실행을 한 트랜잭션에서 두 번 하면 가능). 그래서 2차 키 `id desc` 는 "최근" 의 결정적 정의로 필요하며, 결정 G·01-plan 94행 "일정마다 가장 최근 1행" 과 모순 없음. 테스트 `test_동률_created_at_이면_id_큰_행` 이 이 정의를 고정한다.
- **(ㄴ) `schedule_id` 쿼리 — 없음/남의 것 404 `not_found`, 있으나 compose 없음 `[]`, 이때 기간 상수 미적용.** 25행 "다른 사용자 소유·없는 행은 기존 공통 404 `not_found` 규약" 과 일치(`ScheduleNotFound` → `main.py` 186행 핸들러, `test_schedule_id_두_404_응답이_같다` 가 두 경우 본문 동일을 단언). "있으나 compose 없음 → `[]`" 은 일정이 존재하므로 404 규약 대상이 아니고 목록 응답 타입(`list`) 과도 맞다. 기간 미적용은 94행이 "대상 일정은 … 기간 상수" 를 **목록** 조건으로 적었고 `schedule_id` 지정은 특정 행 조회(푸시 클릭 — U8 `notificationclick` → `#/briefings?schedule_id=N`)라 7일 창을 적용하면 지난 일정의 알림 클릭이 빈 화면이 되므로 해석이 타당하다. 모순 없음. 단, U7 계획(01-plan 98행)은 "`GET /api/briefings` 목록 … `#/briefings?schedule_id=N` 이면 그 일정을 맨 위·강조" 라 프론트가 목록+강조로 갈지 `?schedule_id=` 호출로 갈지 정해져 있지 않다 — R-U3-6.

## 3. 구현자의 계획 밖 판단 3개

- **① 스냅샷 테이블 7 → 8(`pending_questions` 추가).** 판정표 8행이 "`pending_questions`·`agent_traces` 행 수 변화 0" 을 요구하므로 추가는 계획을 더 충실히 따른 것이다. 스키마 v2 의 9번째 테이블 `push_subscriptions` 만 빠져 있다(읽기 API 가 건드릴 경로는 없음) — R-U3-5.
- **② `routes.py` 482행 `ctx.now = now`.** `ToolContext` 는 `@dataclass`(frozen 아님, `context.py` 91행)이고 `now` 는 기본값 람다 필드(104행)라 대입이 유효하며, `list_pending` 은 호출 시점에 `ctx.now()` 를 한 번 읽는다(312행) — 캐시하는 경로 없음(`grep "\.now = "` 는 이 한 곳뿐). 요청마다 새 ctx 라 공유 상태 위험도 없다. **동작은 맞고** 구현자 M20(이 줄 제거 → 6 failed)이 테스트가 이 줄을 고정함을 보인다. 코드 품질은 [권고]: 저장소 관례는 `dataclasses.replace(ctx, session_id=…)`(`run.py` 183행)처럼 복사본을 만드는 것이고, 조립 직후 속성을 덮어쓰는 방식은 `build_chat_ctx` 가 `now` 를 받지 않는다는 사실을 라우트에 숨긴다. `build_chat_ctx` 에 `now` 인자를 추가하는 길은 판정표 11행(`app/api/deps.py` 무변경, R-6) 때문에 이 패키지에서 막혀 있으므로, `replace(ctx, now=now)` 또는 라우트에서 `ToolContext(session=…, session_id=…, user_id=app_user_id(), now=now)` 직접 조립이 대안이다 — R-U3-1.
- **③ `schedules.person_id == persons.id` 일치 검사 생략.** `run.py` 195행 `person_id = schedule.person_id` 가 유일한 출처이고 224~225행이 같은 `schedule` 에서 `schedule.id`·`person_id` 를 넣으므로 제품 코드가 쓰는 compose 행에서는 두 키가 항상 같은 일정을 가리킨다(`_record_briefing_error` 147~148행도 같은 값). trace 행을 넣는 외부 API 는 없다. `schedule_id` 모드는 사전 소유 확인(`read.py` 279~285행, `Schedule→Person` 조인)이 일정 쪽 소유를 따로 보장한다. 생략이 실데이터에서 위험하지 않다고 판정한다. 남는 틈은 **목록 모드에서 손으로 조작한 trace**(남의 `schedule_id` + 내 `person_id`)뿐이고, 그때 남의 일정 제목·시각이 내 목록에 섞인다 — 한 줄 방어(`Person.id == Schedule.person_id` 를 조인 조건에 추가)로 막히고 정상 데이터 결과는 변하지 않는다. 코드 변경 의무는 아니고 R-U3-2 로 돌려준다.

## 4. `tests/helpers_read_api.py` (R-U2-3)

- **값 비교 여부**: `snapshot_db` 가 `(id, briefed_at)` 전체와 `(id, updated_at)` 전체를 id 순 튜플로 담고, `assert_no_writes` 가 `counts`·`briefed_at`·`persons_updated_at` 세 가지를 각각 동치 단언한다(72~73행 메시지 "schedules.briefed_at 이 바뀌었다"·"persons.updated_at 이 바뀌었다"). 행 수만이 아니라 **값**이다.
- **"같은 트랜잭션에서 `now()` 고정이라 `updated_at` 을 30일 전으로 둬야 UPDATE 를 잡는다"**: 맞다. `updated_at` 갱신 주체는 SQLAlchemy `onupdate=func.now()`(`models.py` 114행)뿐이고 DB 트리거는 없다(`grep -rln TRIGGER alembic app/db` exit 1). `db_session` 픽스처는 바깥 트랜잭션 하나 + SAVEPOINT(`conftest.py` 122~124행)라 테스트 전체가 한 트랜잭션이고 PostgreSQL `now()` 는 트랜잭션 시작 시각으로 고정된다. 따라서 `server_default=func.now()` 로 만든 직후 행을 UPDATE 하면 `updated_at` 이 같은 값으로 다시 써져 변화가 안 보인다 — `_person()` 이 `updated_at=NOW - 30일` 을 명시한 이유가 정확하다. `briefed_at` 은 테스트가 값을 직접 넣으므로 이 함정과 무관하다.
- **헬퍼 자체 검증**: `test_헬퍼_자체_briefed_at_또는_updated_at_변경은_잡아낸다` 가 `s.briefed_at = NOW` → flush → `AssertionError(match="briefed_at")`, `p.display_name = "개명"` → flush(onupdate 발동) → `match="updated_at"` 두 가지를 `pytest.raises` 로 확인한다. 구현자 M23·M24(조회 함수 안에 UPDATE 주입)도 helpers 72·73행에서 FAIL 했다(구현자 raw 증거). 헬퍼는 실제로 UPDATE 를 잡는다.
- 범위 밖 후속: U1 `test_api_read_persons.py`·U2 `test_api_read_raw.py` 의 `test_쓰기_0_trace_0` 은 여전히 7테이블 행 수만 비교하고 이 헬퍼를 쓰지 않는다 — R-U3-5.

## 5. 변이 시험 — 내가 직접 돌린 것 (`20261012-1733-verifier-u3-mutation.txt`)

방법: 스크래치패드 pytest 플러그인 `mutplug.py`(소스 보존 `…-verifier-u3-mutplug.py.txt`)가 `read.py` 소스 문자열을 한 곳 치환해 모듈 네임스페이스에 다시 exec 하고 `routes` 의 import 이름을 다시 묶는다(런타임 치환, 저장소 무수정 — 끝의 `git status --short`·`git diff --stat` 가 구현자 변경 그대로임을 보인다). 대상 4파일 60 테스트, 대조군 **60 passed**.

| 변이 | 계약 | 결과 | 잡은 테스트 | 구현자 표 대응 |
|---|---|---|---|---|
| V1 `step` 필터 제거 | trace 원천 둘 다 | **3 failed** | `run_과_error_행은_섞이지_않는다` · `error_만_있는_일정은_제외` · `schedule_id_error_만_있어도_빈_목록` | M3 — 건수·이름 동일 |
| V2 목록 쿼리 `Person.user_id` 제거 | 사용자 격리 | **1 failed** | `다른_사용자_일정은_제외` | M5 — 동일 |
| V3 `>=` → `>` | 기간 경계 | **1 failed** | `기간_경계_…` (정확히 7일 전 누락) | M6 — 동일 |
| V4 `rn == 1` 제거 | 일정별 최신 1행 | **2 failed** | `일정마다_최신_1행만` · `동률_created_at_이면_id_큰_행` | M15 — 동일 |
| V5 분할 키 `schedule_id` → `person_id` **(표에 없음)** | 일정별(인물별 아님) | **4 failed** | `기간_경계_…` · `정렬_…` · `상한_…` · `쓰기_0_…`(같은 인물 일정 2건 중 1건만 나옴) | 없음 — 새 변이, 검출됨 |
| V6 `schedule_id` 모드에서만 목록 쿼리 `user_id` 조건 제거(사전 소유 확인 유지) **(표에 없음)** | 격리 | 60 passed | — | 동치 변이: 그 모드의 격리는 279~285행 사전 확인이 이미 보장(M13·M14 가 그 확인을 깨면 2~4 failed). 테스트 공백 아님 |
| V7 응답 dict 에 `raw_utterance="비밀원문XYZ"` 주입 **(표에 없음)** | 원문 필드 0 | 60 passed | — | 동치 변이: `BriefingRecordOut` 에 그 필드가 없어 pydantic 이 버림. 막는 층은 response_model 이고 모델 변경은 `응답_필드_매핑_전체_값` 의 키 집합 단언이 잡는다 |
| V8 `ChatPendingQuestionOut` 에서 `kind` 누락 **(표에 없음)** | 응답 5필드 | **6 failed** | pending 테스트 6건(`ResponseValidationError: Field required kind`) | 없음 — 새 변이, 검출됨 |
| U1R `func.max` → `func.min`(목록·카드 두 곳) | U1 회귀 | **4 failed** | U1 리뷰 때와 같은 4테스트 | — |
| U2R `PersonFact.person_id == person_id` 제거 | U2 회귀 | **4 failed** | U2 리뷰 M1 과 같은 4테스트 | — |

구현자 24종(`20261012-1800-u3-mutation-raw.txt`)과 겹치는 V1~V4 는 실패 건수·테스트 이름이 **전부 일치**한다. 구현자 표에 "통과한 변이" 는 없고(24종 전부 FAIL), 내가 추가한 V5·V8 도 잡혔다. U1R 1차 실행은 플러그인의 "원문 1회" 검사(목록·카드 두 곳)에 걸려 INTERNALERROR 였고 플러그인을 고쳐 재실행했다 — 증거 파일 머리에 적었다.

## 6. 증거 규칙 (c) — 구현자 변이 증거가 출력 전체가 아님

사실: `-mutation.txt` 는 발췌본, `-mutation-raw.txt` 도 스크립트 66행이 `FAILED`·` passed`·` failed`·`error` 줄만 고른 것이라 변이마다의 pytest 전체 출력은 남아 있지 않다. FIX-033 (c) "증거 파일에는 명령 출력 전체를 Write 로 남긴다" 에 **미달**이고, 그 규칙을 박은 커밋(`7031a19`) 바로 다음 단위에서 어긴 것이다.

판정: **[권고]**(R-U3-3), 재작업 요구 안 함. 이유 — ① 남은 줄이 판정에 쓰이는 정보(변이 이름·FAILED 테스트 이름·`N failed, M passed`·AssertionError 위치)를 전부 담고 있어 결과를 숨기지 않는다. ② 스크립트가 보존돼 재현 가능하고, 내가 독립 경로(런타임 치환)로 4종을 재현해 건수·이름이 정확히 일치했으므로 표의 신뢰도는 확인됐다. ③ 메인 세션이 파일 머리에 미달을 명시하고 원본·스크립트를 보존했다. 재실행은 정보를 더하지 않는다. 단, 다음 단위부터는 위임 프롬프트에 "변이마다 pytest 출력을 그대로 파일에 받고(`> 파일`), 요약은 그 아래 따로" 를 적고, 다시 미달이면 그때는 [필수]로 올린다.

## 7. registry.md

- U3 행 6개(219~224행)와 코드 대조: 라우트 이름·`resolve_session_id`·`build_chat_ctx`·`list_pending`·`get_now()` 설명 = `routes.py` 470~495행과 일치. `list_briefings` 행의 조건·`row_number()`·정렬·상한·404 = `read.py` 와 일치. 스키마 행 3모델·기존 3모델 재사용 = `schemas.py` 와 일치. 헬퍼 행 "8테이블 + briefed_at + updated_at" = helpers 와 일치. 테스트 행 8건·22건 = 파일의 테스트 수와 일치(내 -v 출력 8·22). 해시 칸은 "(U3 미커밋)" — 커밋 뒤 교체 필요.
- 구현자 보고 "U1·U2 행이 registry 에 없다" — **사실**: `grep -n "list_persons\|get_person_card\|get_event_raw\|get_fact_sources\|test_api_read_persons\|test_api_read_raw" docs/wiki/registry.md` exit 1(grep 증거). U2 리뷰 §7 은 "U9 가 registry 갱신" 으로 미뤘으나 U3 가 자기 행을 먼저 올려 비대칭이 생겼다 — R-U3-4.

## 8. 보안·범위

| 확인 | 명령(grep 증거) | 결과 |
|---|---|---|
| 비밀·키 문자열 | `grep -nEi "sk-…\|AKIA…\|PRIVATE KEY\|api[_-]?key\s*=\|secret\s*=\|password\s*=\|token\s*="` 6파일 | 0건(exit 1) |
| 삭제 | `git diff HEAD -- app/api/read.py \| grep "^-"` → docstring 1행 + import 5줄(교체) · `routes.py` 2줄(import 확장) | U1·U2 함수 본문 삭제 0 |
| 범위 밖 파일 | `git diff --numstat HEAD -- app tests docs/wiki/registry.md` → `read.py`·`routes.py`·`schemas.py`·`registry.md` + 신규 테스트 3개 | `app/api/deps.py`·`app/main.py`·`app/settings.py`·`alembic/`·`app/briefing/*`·`app/tools/*` 변경 0(판정표 11행 R-6 충족) |
| 쓰기 라우트 불변식 | POST/PUT/PATCH/DELETE 수 HEAD 4 = 트리 4 · GET 6 → 8 | 계획대로 GET 2개만 추가 |
| Write/Edit 로만 변경 | 자기 보고(03-log 위임 범위 "Write/Edit 로만" 재명시, FIX-014 `bash-write-guard` 가 `de35242` 부터 Bash 쓰기를 거부) | 기계 증거 없음 — "자기 보고" 로 적음 |
| 외부 네트워크 호출 | `grep "httpx\|requests\.\|urllib\|socket\|aiohttp"` 4파일 | 0건. 테스트는 `TestClient` + 실 PostgreSQL 만 |
| 인코딩·CRLF·끝 개행·문법 | UTF-8 OK · CRLF 0 · 끝 개행 있음 · `py_compile` 6파일 ok | 정상 |
| security §5 "모든 조회는 `user_id` 조건" | `list_briefings` 두 모드 모두 `Person.user_id == user_id`(목록 쿼리 + 사전 확인) · pending 은 세션 키(`user_id` 컬럼 없음 — `build_chat_ctx` docstring 이 명시한 패키지 범위 밖) | 충족 |

## 9. 소견

**[필수]** 없음.

**[권고]** (커밋을 막지 않음)

- **R-U3-1 · `routes.py` 482행 `ctx.now = now`.** 동작은 맞고 M20 이 테스트로 고정됨을 보였으나, 조립 직후 속성 덮어쓰기는 저장소 관례(`run.py` 183행 `dataclasses.replace`)와 다르다. `ctx = replace(build_chat_ctx(session, session_id, None), now=now)` 또는 라우트에서 `ToolContext(...)` 직접 조립을 권한다. `build_chat_ctx` 시그니처 변경은 판정표 11행(deps.py 무변경) 때문에 이 패키지에서 하지 않는다. U3 커밋에 넣든 U9 에 미루든 03-log 에 적는다.
- **R-U3-2 · 목록 조인에 `Person.id == Schedule.person_id` 방어 조건.** 제품 코드가 쓰는 compose 행은 두 키가 항상 같은 일정(`run.py` 195·224~225행)이라 정상 데이터 결과는 변하지 않고, 조작된 trace 행이 남의 일정 제목·시각을 섞는 틈만 막는다. 한 줄이므로 U3 커밋에 포함하거나, 생략한다면 03-log 에 "run.py 가 단일 출처" 를 이유로 적는다.
- **R-U3-3 · 증거 규칙 (c) 미달(§6).** 이번은 메인 세션의 머리 기록·원본·스크립트 보존으로 받는다. 다음 단위 위임 프롬프트에 "변이마다 pytest 출력 전체를 파일로, 요약은 아래 따로" 를 넣고, 재발 시 [필수].
- **R-U3-4 · registry U1·U2 행 부재.** `list_persons`·`get_person_card`·`get_event_raw`·`get_fact_sources`·테스트 파일 2개 행이 없다(grep exit 1). U3 가 자기 행을 올린 지금 비대칭이므로 U3 커밋(위키 파일이라 메인 세션이 씀)에서 같이 올리고, "(U3 미커밋)" 6칸을 커밋 해시로 바꾼다.
- **R-U3-5 · 헬퍼 후속(범위 밖).** ① U1·U2 `test_쓰기_0_trace_0` 이 helpers 를 쓰지 않아 판정표 7행(`briefed_at`·`updated_at` 값)을 U3 테스트만 본다 — U9 전체 판정 때 두 파일을 헬퍼로 바꾼다. ② `_COUNTED_MODELS` 에 `push_subscriptions` 가 없다(9테이블 중 8) — 같은 때 추가.
- **R-U3-6 · 03-log U3 완료 항목에 적을 것.** ① 확정값 3개와 근거(이미 17:05 항목에 있음 — 완료 항목에서 참조) ② 스냅샷 8테이블·`ctx.now` 대입·`Schedule.person_id` 일치 검사 생략(§3) ③ (c) 미달과 처리 ④ 판정표 9·10행의 "실제 실행으로 만든 trace" 부분은 U9 끝에서 끝 판정으로 넘김 ⑤ U7 에 넘길 결정: `#/briefings?schedule_id=N` 강조를 목록+강조로 할지 `?schedule_id=` 호출(7일 창 무시, 푸시 클릭용)로 할지 ⑥ Refs `P8-frontend U3 S3.4 S3.6 D2 R12 원칙9`.

## 10. 판정

**통과.** 01-plan 94행의 계약 항목 전부가 코드에 있고 각 항목을 값으로 단언하는 테스트가 있으며, 그 테스트들이 "항상 통과" 가 아님을 내 변이 6건(원천 조건·격리·경계·최신 1행·분할 키·응답 필드 — 전부 FAIL)과 구현자 24종(전부 FAIL, 겹치는 4종은 건수·이름까지 일치)으로 확인했다. 동치 변이 2건(V6·V7)은 테스트 공백이 아니라 다른 층(사전 소유 확인·response_model)이 막는 것임을 적었다. 메인 세션 해석 2개는 25행 규약·결정 G 와 모순 없고, 구현자의 계획 밖 판단 3개는 코드를 읽어 동작 위험이 없음을 판정했다(품질 개선은 [권고]). R-U2-3 헬퍼는 값 비교·`onupdate`·트랜잭션 `now()` 설명·자체 검증 모두 맞다. U1·U2 회귀 변이 검출, 전체 회귀 1942 passed·skip 0, ruff·mypy 기준선, 비밀·손상·범위 밖 변경 0. [필수] 0, [권고] 6. 커밋·승인은 메인 세션·사용자 몫이다.
