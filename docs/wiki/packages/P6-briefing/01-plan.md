# P6-briefing · 계획 (01-plan)

상태: 초안(architect 작성 · 결정 A~K 사용자 확정 2026-10-02 전부 권장안 · 02-plan-verify 는 verifier 몫) | 담당: backend-agent(`app/briefing/` 새 패키지 · `app/api/routes.py`·`deps.py`·`schemas.py` 엔드포인트 한 자리 · `app/main.py` lifespan 한 자리 · `app/settings.py` 상수 · `.env.example` 한 줄) | 작성: 2026-10-02
태그 — 패키지: P6-briefing · 닫는 검증: R12(브리핑 트리거 절반 — 푸시 절반은 P7-push) R19 · 기대는 결정: D14 D11 · 구현하는 명세: S3.6 S3.2 S3.5 S3.1 · 관련 원칙: 원칙5 원칙6 원칙7 원칙8 원칙9
의존: P5-loop(04-review `결과: 완료`, 완료 처리 `f9bfba7`) · P6-memory(04-review `결과: 완료`, 완료 처리 `94373cc`) · 선행 게이트 P4b-er-redesign(04-review `결과: 완료`)

- 근거 해시(`.claude/gitlog.md` 스냅샷 2026-10-02 11:46, Bash 없이 읽음 — L-001): 작업 브랜치 `dev2` HEAD = `36c288e`(FIX-016 "사실만 저장한 턴도 무엇을 기억했는지 답한다"). P6-memory 단위 커밋 U1 `7564c5d` · U2 `d67d084` · U3 `51b4d65` · U4 `48e3617` · U5 `b209581` · U6 `8d3967a` · U7 `93c6d3f` · U8 `4916db3`, 완료 처리 `94373cc`. FIX-015(루프 사실 키를 `FACT_KEYS` 9종으로 유도) `6e7b286`, 실 LLM 확인 문서 `26dcd22`. FIX-016 `36c288e`. 스냅샷의 `dev` 표시는 `3c0f0d9` 이지만 `HANDOFF.md`(2026-10-02 12:00)는 그 뒤 origin/dev = `36c288e` 로 승격됐다고 적었다 — 이 계획의 의존 판단은 dev2 HEAD 기준이므로 어느 쪽이든 영향이 없다. main = `f05d017`(사용자 README 직접 커밋, dev 와 갈라짐 — 이 패키지와 무관, main 승격 때 병합 필요).
- **이 패키지의 시작 해시(무변경 diff 기준점) = `36c288e`.** 스냅샷 시점 미커밋 변경은 `docs/wiki/HANDOFF.md`·`journal.md` 뿐이고 제품 코드는 0이다.
- 이 태그로 이미 있는 커밋: `7c94aad`(P2-tools — `get_briefing` 이 "문장화·제안·주기 작업·`POST /briefings/run` 은 P6-briefing" 이라는 꼬리표를 남긴 커밋). 코드는 없다. 태그별 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P6-briefing S3.6 R12 R19` 실행을 요청**한다.
- P6-memory 04-review §7 인계: ① `detect_patterns(ctx, person_id)` 는 순수 SQL·LLM 0 — **P6-briefing 이 브리핑 직전에 다시 부른다**(결정 C-5 한계: 새 이벤트 없이 시간만 흐르면 패턴이 낡는다). ② `person_facts` 에 세 출처가 섞여 있다 — `pattern:*`(규칙) · 승격 사실(`FACT_KEYS` 9키) · 루프 직접 사실(FIX-015 이후 9키로 유도되지만 옛 자유 키 `소속`·`직장`·`이직` 행이 DB 에 남아 있다). ③ 이벤트 없이 사실만 쓴 턴의 사실은 `fact_sources` 링크가 없다(`action: unlinked`). ④ 미승격 판정은 `agent_traces` 를 상태로 쓴다 — 이 패키지는 `memory_*` trace 를 지우거나 쓰지 않는다(`detect_patterns` 가 스스로 남기는 `memory_pattern` 행은 예외 — 기존 함수 그대로).

## 목표

`docs/resolution-plan.md` §3.6(195~198행)과 S3.6 카드의 앞 세 문장 — "주기 작업(컨테이너 내, 1분): `scheduled_at - now() ≤ 24h AND briefed_at IS NULL` → `get_briefing` → (웹푸시) → `briefed_at`", "수동 트리거 `POST /briefings/run` = 같은 함수", "브리핑 내용: 기록된 사실·패턴·최근 사건. **제안은 사실에서 도출되는 한 줄 행동 제안으로 한정**, 감정·고민 대화 금지" — 를 코드로 옮긴다. 지금은 P2-tools 의 `get_briefing`(`app/tools/briefing.py`)이 **자료만** 모아 돌려줄 뿐(사실 전부·최근 사건 5·다가오는 일정 3, LLM 0), 그 자료를 사람이 읽는 브리핑으로 만드는 단계도, 만남이 다가오면 스스로 도는 주기 작업도, 발표자가 누르는 수동 트리거도 없다. 이 패키지는 세 가지를 만든다. ① **대상 선정**: 24시간 안에 다가왔고 아직 브리핑하지 않은 일정(`briefed_at IS NULL`)을 고른다. ② **브리핑 생성**: 브리핑 직전에 패턴을 다시 계산하고(P6-memory 인계 ①), `get_briefing` 자료에서 LLM 이 패턴 문장과 한 줄 행동 제안을 쓰되, **패턴 판정은 규칙 그대로**(원칙6)이고 **제안은 입력에 있는 사실·사건만 근거로 삼으며 감정·고민 문장은 코드가 버린다**(원칙7·R19). ③ **실행 경로 두 개, 함수 하나**: 1분 주기 작업과 `POST /briefings/run` 이 같은 실행 함수를 부르고, 성공한 일정에 `briefed_at` 을 남긴다. 예: 사용자가 어제 "내일 저녁 7시에 민수랑 저녁 약속" 이라고 말해 두었다면, 오늘 저녁 7시 24시간 전부터 1분 안에 주기 작업이 그 일정을 집어 "민수와 올해 세 번 다퉜어요(2026-03-02, 06-11, 09-20)" · "제안: 매운 음식은 피하고 고수 없는 식당을 고르세요(근거: 싫어하는 것=고수, 원문 '민수 매운 거 못 먹어')" 같은 브리핑을 만들고 그 일정의 `briefed_at` 을 채운다 — 다음 분에는 다시 집지 않는다. **웹푸시 발송은 하지 않는다**(P7-push). 주기 작업에는 "푸시를 보낼 자리"(결정 J)만 남긴다.

## 범위

- 포함:
  - **대상 선정(규칙·SQL)** — `app/briefing/select.py`. `persons.user_id = ctx.user_id` 인 일정 중 결정 B 의 창 안이고 `briefed_at IS NULL` 인 것을 `scheduled_at` 오름차순으로 고른다. 동시에 도는 두 실행(주기 작업과 수동 트리거)이 같은 일정을 두 번 집지 않도록 `FOR UPDATE SKIP LOCKED` 로 행을 잡는다.
  - **브리핑 입력 조립** — `app/briefing/inputs.py`. 일정마다 ① `detect_patterns(ctx, person_id)` 재호출(결정 K) ② `get_briefing(ctx, person_id, schedule_id)` 호출(기존 툴 그대로 — `briefed_at` 기록이 여기서 일어난다) ③ 사실 세 출처 정리(결정 F) ④ 제안 근거로 쓸 수 있는 사실·사건의 연결 원문 조회(결정 G).
  - **브리핑 문장 생성기** — `app/briefing/compose.py`. `BriefingComposer` Protocol · 구조화 출력 스키마 · 프롬프트(경계 지시 포함) · 검증기(결정 E) · 공급자 구현(`app/er/judge.py` 의 `select_provider`·`call_with_error_mapping` 재사용, D11 — `app/memory/extract.py` 와 같은 방식) · `FakeBriefingComposer`(네트워크 0) · **템플릿 대체 생성기**(LLM 0, 결정 D).
  - **실행 함수(주기·수동 공용)** — `app/briefing/run.py::run_briefings(...)`. 일정마다 세이브포인트로 감싸 한 일정의 실패가 다른 일정을 되돌리지 않게 한다. 푸시 자리는 `Notifier` Protocol 과 기본 `NullNotifier`(결정 J).
  - **수동 트리거** — `POST /briefings/run`(`app/api/routes.py`), 요청·응답 스키마(`app/api/schemas.py`), 생성기 의존성 `get_briefing_composer()`(`app/api/deps.py`, 지연 생성 — 키가 없어도 요청이 실패하지 않게, P6-memory R-10 과 같은 규약).
  - **주기 작업(1분)** — `app/briefing/scheduler.py`. 앱 lifespan 안의 비동기 루프가 `BRIEFING_INTERVAL_SECONDS`(60)마다 같은 실행 함수를 스레드에서 부른다. 환경변수 스위치로 켜고 끈다(결정 A).
  - **관측성(원칙9)** — trace 어휘 `tool_name="briefing"`, step `briefing_run`·`briefing_compose`·`briefing_error`(결정 I). 입력으로 쓴 사실·뺀 사실·근거 id·검증기 거부 사유·템플릿 대체 여부·토큰 in/out·푸시 자리 상태를 남긴다.
  - **설정·문서** — `app/settings.py` 상수(`BRIEFING_LEAD_HOURS`=24 · `BRIEFING_INTERVAL_SECONDS`=60 · `BRIEFING_SUGGESTION_MAX_CHARS` · 스위치 읽기 함수 `briefing_scheduler_enabled(env=None)`), `.env.example` 에 스위치 한 줄(값 비움 = 꺼짐, 비밀 없음), `docs/RUNNING.md` "브리핑이 언제·어떻게 도는가" 한 절, `registry.md` 새 행·비고 확장.
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **웹푸시 — 구독 저장(`push_subscriptions`)·VAPID 키·발송·서비스 워커**(P7-push, backlog P7 "구독 저장, VAPID 발송") — 이 패키지는 `Notifier` 자리(결정 J)만 두고 `NullNotifier` 는 아무것도 보내지 않는다. `pywebpush` 같은 의존성을 추가하지 않고 VAPID 키 값을 코드·문서·`.env.example` 어디에도 쓰지 않으며 `.env.example` 31~34행의 기존 P7 용 빈 이름 줄(`VAPID_PUBLIC_KEY=` 등)은 건드리지 않는다(security §1, S3.6 4행).
  - **브리핑 조회 API·프론트 브리핑 화면**(P8-frontend, 원칙5 화면 3개 고정) — 화면이 읽을 자료는 이 패키지가 응답과 trace 로 남긴다(결정 H). `GET /briefings/...` 는 backlog 수용 기준에 없어 만들지 않는다.
  - **스키마 v2 변경·마이그레이션** — S3.1 이 권위다. 브리핑 저장 테이블(결정 H(ii))이나 `schedules` 컬럼 추가를 고르면 이 패키지 밖에서 `/devlog change` CR 이 먼저다.
  - **툴 7종 시그니처·동작 변경** — `get_briefing(person_id, schedule_id?)` 는 S3.2 그대로 쓴다(`tools_check` 7/7 유지). 루프 게이트가 `get_briefing` 을 LLM 호출 불가로 막아 둔 것(`app/agent/gate.py`)도 그대로다 — 브리핑은 대화 턴이 아니라 실행 함수가 부른다.
  - **`app/agent/`·`app/memory/`·`app/er/` 수정** — 패턴 재계산은 `detect_patterns` 를 **import 해서 부르기만** 한다(P6-memory 판정 근거 코드, 원칙8). 공급자 등록표도 import 만 한다.
  - **추출 품질 자체의 개선(프롬프트 키 설명 손질)·추출 정밀도 지표** — 결정 G 에서 (iii) 을 고르지 않는 한 이 패키지 밖이다. 지표는 P10-final-eval. 이 패키지는 소비 쪽 방어(결정 G(ii))만 한다.
  - **이미 저장된 옛 자유 키 사실(`소속`·`직장`·`이직`)의 삭제·이름 바꾸기** — 원문에서 다시 만들 수 없는 사실이고(루프 직접 사실) backlog 어디에도 정리 항목이 없다. 브리핑은 읽을 때 거른다(결정 F).
  - **고민 상담·감정 대화·위로 문장, 인물 간(A–B) 관계 서술, 상담 페르소나, 음성, 네이티브 앱**(원칙7) — 제안은 기록된 사실·사건에서 나온 한 줄 행동뿐이다. 결정 E 의 코드 검증기가 이를 강제한다.
  - **다중 사용자 스케줄링** — 주기 작업은 `app_user_id()` 한 사용자만 본다(P5-loop 결정 I 와 같은 단일 사용자 전제, 다중 사용자 격리 부채 F-fbaaae 는 P9-infra 전).
  - **배포 환경에서 스위치 켜기·컨테이너 구성**(P9-infra) — 이 패키지는 스위치와 실행 설명까지만 둔다.

## 산출물 (파일 경로)

**새로 만드는 파일**

- `app/briefing/__init__.py` — 진입점 재export(`run_briefings`·`select_due_schedules`·생성기 Protocol·가짜·`NullNotifier`·trace 상수)
- `app/briefing/types.py` — 결과 타입(`BriefingInput`·`ComposedBriefing`·`BriefingLine`·`Suggestion`·`BriefingRunResult`), trace 어휘 상수(`BRIEFING_TRACE_TOOL_NAME="briefing"`, step 3종), 금지 표현 목록(결정 E), `Notifier` Protocol·`NullNotifier`(결정 J)
- `app/briefing/select.py` — 대상 일정 선정(SQL, LLM 0)
- `app/briefing/inputs.py` — 패턴 재계산 → `get_briefing` → 사실 정리 → 근거 원문 조회
- `app/briefing/compose.py` — `BriefingComposer` Protocol·`BRIEFING_SCHEMA`·`build_briefing_prompt()`·`validate_briefing()`·공급자 구현·`composer_from_env()`·`FakeBriefingComposer`·`template_briefing()`
- `app/briefing/run.py` — `run_briefings()`(주기·수동 공용 실행 함수)
- `app/briefing/scheduler.py` — 1분 주기 루프·lifespan 진입점
- `tests/test_briefing_select.py` — 창 경계·`briefed_at`·다른 사용자·동시 실행
- `tests/test_briefing_inputs.py` — 패턴 재계산·사실 세 출처 정리·근거 원문
- `tests/test_briefing_compose.py` — 스키마·검증기 부정 케이스(원칙7)·템플릿 대체·프롬프트 경계 문구·네트워크 0
- `tests/test_briefing_run.py` — 실행 함수·멱등·실패 격리·trace
- `tests/test_api_briefings.py` — `POST /briefings/run` 한 흐름
- `tests/test_briefing_scheduler.py` — 스위치 꺼짐/켜짐·주기 호출·예외 후에도 루프 유지·종료

**고치는 기존 파일** (registry 에 다른 패키지 행으로 있다 — 새 행이 아니라 비고 확장)

| 파일 | 고치는 내용 | 원래 패키지 |
|------|------------|------------|
| `app/settings.py` | 상수 `BRIEFING_LEAD_HOURS=24`·`BRIEFING_INTERVAL_SECONDS=60`·`BRIEFING_SUGGESTION_MAX_CHARS`(결정 E), 읽기 함수 `briefing_scheduler_enabled(env=None)`(환경변수 `BRIEFING_SCHEDULER_ENABLED`, 비우면 꺼짐, `1`/`true` 만 켜짐, 그 밖 값은 `InvalidValue`) | P2-tools |
| `app/main.py` | `create_app()` 에 lifespan 한 자리 — 스위치가 켜졌을 때만 주기 루프를 띄운다. 모듈 docstring 의 "lifespan 훅도 두지 않는다" 문장을 "스위치가 꺼져 있으면 lifespan 은 아무것도 하지 않는다(import·기동 시 엔진 생성 없음은 그대로)" 로 고친다(리스크 A 유지) | P2-tools |
| `app/api/routes.py` · `app/api/schemas.py` · `app/api/deps.py` | `POST /briefings/run`, `BriefingRunIn`·`BriefingRunOut`, `get_briefing_composer()` | P2-tools / P5-loop / P6-memory |
| `.env.example` | 한 줄 `BRIEFING_SCHEDULER_ENABLED=`(값 비움, 주석 "비우면 꺼짐, 1 이면 1분마다 브리핑" — 비밀 없음, security §1) | 하네스(registry 38행) |
| `docs/RUNNING.md` · `docs/wiki/registry.md` | 실행 설명 한 절 · 행 추가/비고 확장 | — |

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

각 단위의 완료 판정 명령은 로컬 기준 `POSTGRES_PORT=5433 .venv/bin/python -m pytest …` 이고 테스트 DB 는 `relationship_test`(FIX-006, `tests/conftest.py` 가 스스로 준비)다. 모든 테스트는 **실 키·네트워크 없이** 돈다(가짜 생성기·`NullNotifier`). 시간은 `ToolContext.now` 주입으로 고정한다(기존 `ctx.now()` 패턴 — `get_briefing` 이 이미 호출당 한 번만 읽는다). 출력은 `docs/wiki/packages/P6-briefing/evidence/<YYYYMMDD-HHMM>-<이름>.txt` 로 남긴다. 담당은 전부 **backend-agent**, U8 의 실 공급자 왕복 1회만 사용자 실행 권고.

- [x] U1 골격 — [backend-agent] 설정 상수 3개 + `briefing_scheduler_enabled()`, `.env.example` 한 줄, `app/briefing/__init__.py`·`types.py`(결과 타입·trace 어휘·금지 표현 목록·`Notifier`/`NullNotifier`). 도는 코드 없음. 판정: `pytest tests/test_briefing_select.py -k constants -v`(상수 값·어휘·스위치 기본 꺼짐·`1`/`true` 켜짐·잘못된 값 `InvalidValue`) + `python -c "import app.briefing"` + `grep -n "BRIEFING_SCHEDULER_ENABLED" .env.example`(1건) · 증거 `evidence/*-u1-skeleton.txt` / Refs: P6-briefing S3.6 R12 원칙9
- [ ] U2 대상 선정 — [backend-agent] `select_due_schedules(ctx, *, lead_hours, schedule_id=None) -> list[Schedule]`. `Schedule` ⨝ `Person` 에서 `Person.user_id == ctx.user_id`, 결정 B 의 창(권장: `now ≤ scheduled_at ≤ now + 24h`), `briefed_at IS NULL`, `scheduled_at ASC`, `FOR UPDATE OF schedules SKIP LOCKED`. `schedule_id` 가 주어지면(결정 C) 그 한 건만 소유 확인 후 창·`briefed_at` 과 무관하게 돌려주고, 없거나 다른 사용자 것이면 `ScheduleNotFound`. LLM·임베딩 import 없음. 판정: `pytest tests/test_briefing_select.py -v` · 증거 `evidence/*-u2-select.txt` / Refs: P6-briefing S3.6 S3.1 R12 원칙8
- [ ] U3 브리핑 입력 조립 — [backend-agent] `build_briefing_input(ctx, schedule) -> BriefingInput`. 순서: ① `detect_patterns(ctx, person_id)`(결정 K — 기존 함수 그대로, 자기 `memory_pattern` trace 를 남긴다) ② `get_briefing(ctx, person_id, schedule_id)`(기존 툴 그대로 — 여기서 `briefed_at = ctx.now()` 가 기록된다) ③ 결정 F 의 사실 정리(권장: `pattern:*` + `FACT_KEYS` 만 쓰고 그 밖 키는 `excluded_facts` 로 따로 둔다, 같은 키 여러 행은 `updated_at desc` 첫 행) ④ 결정 G 의 근거 원문(권장: 쓰인 사실마다 `fact_sources → events.raw_utterance` 를 최대 N건 조회해 `suggestion_eligible` 표시 — 링크 없는 사실은 요약 줄에는 쓰되 제안 근거 불가). `events` 는 읽기만 한다. 판정: `pytest tests/test_briefing_inputs.py -v` · 증거 `evidence/*-u3-inputs.txt` / Refs: P6-briefing S3.5 S3.6 D14 원칙6 원칙9
- [ ] U4 문장 생성기 — [backend-agent] `BriefingComposer.compose(briefing_input) -> ComposedBriefing`. 출력 스키마(결정 D 권장안) `{pattern_sentences:[{key, sentence}], lines:[{text, basis:{fact_keys:[], event_ids:[]}}], suggestion:{text, basis:{fact_keys:[], event_ids:[]}} | null}`. 프롬프트에 S3.6 경계 문장을 그대로 넣는다("기록된 사실에서 도출되는 한 줄 행동 제안으로 한정, 감정·고민에 대한 대화는 하지 않는다"). 검증기(결정 E)는 **항목 단위로** 거부하고 사유를 남긴다: 근거 비었음 · 입력에 없는 키/이벤트 id · 제안 근거가 `suggestion_eligible` 아님 · 제안이 두 줄 이상/상한 초과 · 금지 표현 포함 · 패턴 문장의 숫자가 규칙 값의 `n` 과 다름(→ 그 패턴만 템플릿 문장으로 대체). 공급자는 `app/er/judge.py` 의 `select_provider`·`call_with_error_mapping` import(D11 — 자체 선택 로직 금지, 등록표는 `FACT_EXTRACTORS` 와 같은 모양으로 새로 둔다). `FakeBriefingComposer`(표 기반·결정적·호출 횟수 카운트). `template_briefing(input)`(LLM 0, 패턴은 규칙 value 그대로, **제안 없음**). 판정: `pytest tests/test_briefing_compose.py -v` · 증거 `evidence/*-u4-compose.txt` / Refs: P6-briefing S3.6 R19 D11 원칙6 원칙7 원칙8
- [ ] U5 실행 함수 — [backend-agent] `run_briefings(session_factory, *, now, composer, notifier=NullNotifier(), schedule_id=None, trigger: "scheduler"|"manual") -> BriefingRunResult`. 실행 하나에 `session_id = "briefing:<uuid4>"`(결정 I). 대상 선정(U2) 뒤 일정마다 `begin_nested()` 안에서 U3 → U4(생성기 오류면 결정 D 대로 템플릿 대체, `briefed_at` 은 그대로 기록) → `notifier.notify(...)`(`NullNotifier` 는 `"not_configured"` 반환만) → `briefing_compose` trace 1행. 일정 하나에서 생성기 밖 예외(DB 등)가 나면 그 세이브포인트만 되돌려 그 일정의 `briefed_at` 이 남지 않게 하고(다음 실행이 다시 집는다), **롤백이 끝난 뒤** 바깥에서 `briefing_error` 1행을 쓴다(P6-memory U6 의 `memory_error` 와 같은 규약). 실행 끝에 `briefing_run` 1행. `SQLAlchemyError` 의 처리 규약은 P5 와 같다(삼키지 않고 올림 — 단 세이브포인트 단위 격리를 먼저 시도, 03-log 에 정한 방식을 남긴다). 판정: `pytest tests/test_briefing_run.py -v` · 증거 `evidence/*-u5-run.txt` / Refs: P6-briefing S3.6 S3.2 R12 원칙7 원칙9
- [ ] U6 수동 트리거 — [backend-agent] `POST /briefings/run`. 요청 본문 선택 `{"schedule_id": int?}`(결정 C), 응답 `{run_id, generated_at, briefings:[{schedule_id, person_id, composer: "llm"|"template", pattern_sentences, lines, suggestion, push}], skipped:[{schedule_id, reason}]}`. 의존성 `get_session`(기존)·`get_briefing_composer()`(지연 생성). `run_briefings(..., trigger="manual")` 를 부른다 — 주기 작업과 **같은 함수**(S3.6 2행). 응답에 `raw_utterance` 원문을 싣지 않는다(근거는 id·키로만 — `get_briefing` 의 `EventOut` 결정과 같은 이유). 판정: `pytest tests/test_api_briefings.py -v` · 증거 `evidence/*-u6-api.txt` / Refs: P6-briefing S3.6 R12 원칙9
- [ ] U7 주기 작업 — [backend-agent] `app/briefing/scheduler.py` 의 비동기 루프(`asyncio` 태스크, `BRIEFING_INTERVAL_SECONDS` 마다 `run_briefings(..., trigger="scheduler")` 를 스레드 풀에서 실행)와 `app/main.py` lifespan 한 자리(결정 A). 스위치가 꺼져 있으면 태스크를 만들지 않는다. 한 번의 실행이 예외를 내도 루프는 계속 돈다(예외는 trace·로그로 남기고 삼킨다). 앱 종료 시 태스크를 취소하고 기다린다. 테스트는 루프 간격과 실행 함수를 주입해(예: 0.01초, 호출 카운터) 실 시간 1분을 기다리지 않는다. 판정: `pytest tests/test_briefing_scheduler.py -v` + 기존 `tests/test_api.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_memory_loop.py`(lifespan 추가 후에도 `TestClient` 를 쓰는 기존 테스트 통과 — 스위치 기본 꺼짐) · 증거 `evidence/*-u7-scheduler.txt` / Refs: P6-briefing S3.6 R12 원칙8
- [ ] U8 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 전 행 실행, 전체 회귀(`POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs`, skip 0), "지킬 불변식" 절 grep 을 그 절 명령 그대로, `alembic check`(스키마 무변경), `python scripts/tools_check.py` 7/7(시그니처 무변경), `git diff --stat 36c288e -- app/tools/briefing.py app/agent app/memory app/er`(빈 출력 — 무변경), `registry.md`·`docs/RUNNING.md` 갱신. 실 공급자 왕복 1회(`POST /briefings/run`, 개발 DB 의 확인용 인물 하나)는 사용자 실행 권고로 남긴다(P6-memory U8 과 같은 방식). 증거 `evidence/*-u8-*.txt` / Refs: P6-briefing S3.6 R12 R19 원칙7 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록

### 해석 (위 한 줄을 판정 가능한 문장으로 — 새 기준을 더하는 것이 아니다)

| # | 원문 구절 | 이 계획의 해석 |
|---|----------|--------------|
| ㄱ | `POST /briefings/run`으로 | HTTP `POST /briefings/run` 이 200 을 돌려주고, 그 처리 경로가 1분 주기 작업과 **같은 함수**(`run_briefings`)다(S3.6 "수동 트리거 = 같은 함수") |
| ㄴ | 브리핑 생성 | 창 안의 미브리핑 일정마다 응답 `briefings[]` 에 한 건이 생긴다. 그 한 건은 ① 브리핑 직전에 다시 계산한 `pattern:*` 의 문장, ② 사실·최근 사건 요약 줄, ③ 한 줄 행동 제안(없을 수 있음)으로 이뤄지며, **모든 줄과 제안은 입력에 있는 사실 키·이벤트 id 를 근거로 가진다**. 제안은 한 줄이고 감정·고민 표현이 없다(원칙7, R19). 생성 과정은 `briefing_compose` trace 1행에 남는다(원칙9) |
| ㄷ | `briefed_at` 기록 | 브리핑이 생성된 일정의 `schedules.briefed_at` 이 그 실행의 `now` 로 채워지고, 같은 조건으로 다시 실행하면 그 일정은 다시 집히지 않는다(`briefed_at IS NULL` 조건). 실패한 일정은 `briefed_at` 이 비어 있어 다음 실행이 다시 집는다 |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

전부 `POSTGRES_PORT=5433 .venv/bin/python -m pytest <파일>::<테스트> -v` 로 실행하고 출력 파일을 `docs/wiki/packages/P6-briefing/evidence/` 에 남긴다. 테스트 이름은 U 단위에서 확정하되 아래 뜻을 바꾸지 않는다. **"상태" 열**: 모든 행은 **독립**이다 — 행마다 새 인물·일정을 만들고 앞 행의 결과를 이어 쓰지 않는다(P6-memory 04-review §6 권고 반영). 시각은 전부 `ctx.now` 주입으로 고정한다(아래 `T` = 주입한 지금).

| # | 확인할 것 | 상태 | 케이스 | 기대 출력 | 위치 |
|---|----------|------|-------|----------|------|
| 1 | ㄱ·ㄴ·ㄷ 양성(API 한 흐름) | 독립 | 인물 1·일정 `T+3h` 1건·사실 2·이벤트 3, 가짜 생성기 의존성 오버라이드, `TestClient` `POST /briefings/run` | 200, `briefings` 길이 1, 그 일정 `briefed_at == T`, `briefing_run` 1행·`briefing_compose` 1행 | test_api_briefings |
| 2 | ㄷ 재실행 멱등 | 독립 | 1행과 같은 준비 후 `POST` 두 번 | 두 번째 응답 `briefings == []`, 생성기 호출 총 1회, `briefed_at` 값 불변 | 〃 |
| 3 | ㄱ 같은 함수 | 독립 | 엔드포인트와 주기 루프가 부르는 함수를 가짜로 바꿔 끼움 | 두 경로 모두 같은 `run_briefings` 객체를 부름(`trigger` 값만 `manual`/`scheduler`) | test_api_briefings·scheduler |
| 4 | 창 경계 양성 | 독립 | 일정 `T+24h` 정확히 | 선정됨 | test_briefing_select |
| 5 | 창 경계 부정 | 독립 | 일정 `T+24h+1s` | 선정 안 됨 | 〃 |
| 6 | 지난 일정(결정 B) | 독립 | 일정 `T−1s`, `briefed_at` NULL | 선정 안 됨(결정 B(i) 확정, S3.6 카드 보충 줄) | 〃 |
| 7 | 이미 브리핑됨 | 독립 | 일정 `T+3h`, `briefed_at` 채워짐 | 선정 안 됨 | 〃 |
| 8 | 다른 사용자 격리 | 독립 | 다른 `user_id` 인물의 `T+3h` 일정 / `schedule_id` 로 그 일정 지정 | 선정 안 됨 / API 404 `not_found`, `briefed_at` 불변 | test_briefing_select·api |
| 9 | 동시 실행 | 독립 | 세션 두 개가 같은 순간 `select_due_schedules` | 한 일정은 한 세션에만 잡힘(`SKIP LOCKED`) | test_briefing_select |
| 10 | 수동 강제(결정 C) | 독립 | `briefed_at` 이 이미 있는 일정을 `{"schedule_id": id}` 로 | 브리핑 1건 생성, `briefed_at` 이 새 `T` 로 갱신(`get_briefing` 기존 덮어쓰기 동작) | test_api_briefings |
| 11 | 패턴 재계산(결정 K) | 독립 | `conflict` 3건으로 `pattern:conflict` 가 있던 인물, 시계를 옮겨 1건이 창 밖 → 브리핑 | 브리핑 입력·출력에 `pattern:conflict` 없음, `person_facts` 에서도 삭제, `memory_pattern` trace `action=deleted` 1행, 이벤트 3건 그대로 | test_briefing_inputs |
| 12 | 사실 세 출처(결정 F) | 독립 | `pattern:meal`·`workplace=네이버`(9키)·`소속=네이버`(옛 자유 키) | 권장안이면 입력 사실 = `pattern:meal`·`workplace`, `소속` 은 `excluded_facts` 와 trace 에만 | 〃 |
| 13 | 같은 키 여러 행 | 독립 | `likes` 2행(`updated_at` 다름) | 입력에는 최신 1행만 | 〃 |
| 14 | 원칙7 부정 — 근거 없는 제안 | 독립 | 가짜 생성기가 `suggestion.basis` 비움 | 제안 `null`, 거부 사유 `no_basis` trace, 나머지 줄은 유지 | test_briefing_compose |
| 15 | 원칙7 부정 — 감정·고민 표현 | 독립 | 가짜 생성기 제안 "민수의 기분을 먼저 위로해 주세요"(근거 있음) | 제안 `null`, 사유 `forbidden_expression` | 〃 |
| 16 | 원칙7 부정 — 한 줄 위반 | 독립 | 제안에 줄바꿈 / `BRIEFING_SUGGESTION_MAX_CHARS` 초과 | 제안 `null`, 사유 `not_one_line`/`too_long` | 〃 |
| 17 | 근거 위조 | 독립 | 입력에 없는 이벤트 id·사실 키를 근거로 단 줄 | 그 줄만 거부, 사유 `unknown_basis` | 〃 |
| 18 | 근거 자격(결정 G) | 독립 | 제안 근거가 `fact_sources` 링크 없는 사실뿐 | 권장안이면 제안 `null`, 사유 `basis_not_eligible` | 〃 |
| 19 | 패턴 판정은 규칙(원칙6) | 독립 | 가짜 생성기 패턴 문장 "다섯 번 다퉜어요"·규칙 값 `"3회 (…)"` | 그 패턴 문장만 템플릿 문장으로 대체, 사유 `count_mismatch`. 패턴 행 value 는 생성기와 무관하게 규칙 값 그대로 | 〃 |
| 20 | 프롬프트 경계 문구 | 독립 | `build_briefing_prompt(input)` | S3.6 경계 문장 원문 포함, 인물 간 관계 질문·조언 요청 문구 없음 | 〃 |
| 21 | 템플릿 대체(결정 D) | 독립 | 가짜 생성기가 `JudgeUnavailable("timeout")`(기존 오류 어휘 — `app/er/types.py` 49행, `judge.py` 232행. 새 클래스 없음) | 브리핑 `composer="template"`, 제안 `null`, `briefed_at` 기록됨, `briefing_compose` output `fallback_reason` | test_briefing_run |
| 22 | 실패 격리 | 독립 | 일정 2건 중 첫 건 처리 중 DB 예외 주입 | 첫 건 `briefed_at` NULL(되돌림)·`briefing_error` 1행 존재, 둘째 건 정상 생성·`briefed_at` 기록 | 〃 |
| 23 | 근거 기록(원칙9) | 독립 | 1행 실행 후 trace 조회 | `briefing_compose.output` 에 `schedule_id`·`person_id`·`used_facts`·`excluded_facts`·`lines[].basis`·`suggestion.basis`·`rejected[]`·`composer`·`push` 키, `tokens_in/out` = 생성기 사용량(템플릿이면 0/0), `briefing_run.output` 에 `trigger`·`window`·`selected`·`skipped` | 〃 |
| 24 | 푸시 없음(결정 J) | 독립 | 1행 실행 | `push == "not_configured"`, 외부 전송 0(가짜 `Notifier` 로 바꾸면 호출 1회·인자에 `raw_utterance` 없음) | 〃 |
| 25 | 주기 작업 스위치 | 독립 | 스위치 비움 / `1` 로 `TestClient` 컨텍스트 진입, 간격 0.01초·카운터 주입 | 꺼짐: 실행 함수 호출 0 / 켜짐: 호출 ≥ 1, 종료 후 태스크 취소됨 | test_briefing_scheduler |
| 26 | 주기 작업 내구성 | 독립 | 주입한 실행 함수가 첫 호출에서 예외 | 다음 주기에 다시 호출됨(루프 생존) | 〃 |
| 27 | 원문 불변 | 독립 | 1·11행 전후 | `events` 행 수·`raw_utterance`·`content` 동일 | test_briefing_run·inputs |
| 28 | 불변식 grep | — | "지킬 불변식" 절 명령 그대로(표 안에서는 파이프 기호가 칸을 나누므로 명령을 다시 적지 않는다) | 전부 0건 | U8 evidence |
| 29 | 무변경 | — | `alembic check` · `python scripts/tools_check.py` · `git diff --stat 36c288e -- app/tools/briefing.py app/agent app/memory app/er` | "No new upgrade operations detected." · "RESULT: 7/7 ok" · 빈 출력 | U8 evidence |
| 30 | 전체 회귀 | — | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs` | 실패 0·skip 0, 통과 수 ≥ 1627(FIX-016 기준선) | U8 evidence |

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 위치(registry 행) | 어떻게 |
|--------|------------------|-------|
| `get_briefing(ctx, person_id, schedule_id?)` | `app/tools/briefing.py`(P2-tools `7c94aad`, 61행) | **그대로 호출**. 자료 조회(사실 전부·최근 사건 5·다가오는 일정 3)와 `schedule_id` 가 있을 때의 `briefed_at = ctx.now()` 기록을 이 함수가 한다 — 같은 조회·기록을 새로 쓰지 않는다. `@traced("get_briefing")` 가 `tool_call` trace 를 이미 남긴다 |
| `BriefingOut`·`ScheduleOut`·`EventOut`·`ScheduleNotFound` | `app/tools/types.py`(56행) | 입력 조립이 `BriefingOut` 을 받아 쓴다. 새 응답 DTO 는 `app/briefing/types.py` 에 두되 `BriefingOut` 필드를 복제하지 않는다 |
| `detect_patterns(ctx, person_id)` | `app/memory/patterns.py`(P6-memory `d67d084`, 177행) | 브리핑 직전 재호출(결정 K). 수정 없음 |
| `FACT_KEYS`·`PATTERN_KEY_PREFIX` | `app/memory/types.py`·`app/settings.py`(53행) | 결정 F 의 사실 정리 기준 |
| `_owned_person(session, person_id, user_id)` | `app/tools/persons.py`(58행) | `schedule_id` 지정 시 소유 확인(security §5). 새 소유 검사 함수 금지 |
| 공급자 선택·오류 매핑 | `app/er/judge.py`(`select_provider`·`call_with_error_mapping`, D11) | import 만. `app/memory/extract.py`(`FACT_EXTRACTORS`·`extractor_from_env`)가 같은 방식의 선례 |
| 오류 어휘 | `app/er/judge.py` 기존 6종 | 새 오류 클래스를 만들지 않는다 |
| `@traced(tool_name, step=…)`·`trace_tokens()`·세이브포인트 규약 | `app/tools/context.py`(57행), `app/memory/hooks.py`(`begin_nested()` 밖에서 오류 행 기록) | 새 step 3종을 이 데코레이터로, 오류 행은 롤백 뒤 바깥에서 |
| `session_scope()` | `app/db/session.py`(52행) | 주기 작업이 실행마다 세션을 연다 |
| `app_user_id()`·`user_timezone()` | `app/settings.py`(53행, FIX-005) | 주기 작업의 사용자, 브리핑 문장의 날짜 표기(창 계산은 UTC) |
| 지연 생성 의존성 규약 | `app/api/deps.py` `get_fact_extractor()`(64행) | `get_briefing_composer()` 를 같은 모양으로 |
| 테스트 픽스처·마커 | `tests/conftest.py`(51행, `db_session`·`dbtest`, FIX-006) | 그대로 |

registry 를 `app/briefing`·`test_briefing`·`briefings/run`·`scheduler` 로 grep 한 결과 0건 — 새 모듈은 중복이 아니다(`briefing` 으로 걸리는 것은 위 표의 `app/tools/briefing.py`·`tests/test_tools_briefing.py`·`BriefingOut` 뿐이고 셋 다 재사용 대상).

## 결정 항목 (사용자가 고른다 — 각 항목 권장안 표시, 확정 아님)

> **확정(사용자, 2026-10-02) — 전부 권장안**: **A(i)** 앱 lifespan 비동기 루프 + `BRIEFING_SCHEDULER_ENABLED`(기본 꺼짐) · **B(i)** `now ≤ scheduled_at ≤ now+24h`(지난 일정 제외 — S3.6 해석 여부는 verifier 판정) · **C(ii)** 선택 `schedule_id` · **D(i)** LLM 1회 구조화 출력 + 코드 검증 + 실패 시 템플릿 대체(`briefed_at` 기록) · **E(ii)** 프롬프트 + 코드 검증기 · **F(ii)** `pattern:*` + `FACT_KEYS` 만, 그 밖 키는 `excluded_facts`·trace · **G(ii)** 소비 쪽 방어, 프롬프트 수정은 별개 FIX 후보(선행 조건 아님) · **H(i)** 응답 + `briefing_compose` trace 에만(스키마 무변경) · **I** 권장 어휘 그대로 · **J(i)** `Notifier` + `NullNotifier` · **K(i)** 브리핑 대상 인물만 직전 재계산. 아래 각 항목의 "권장" 이 곧 확정안이다.

### 결정 A · 1분 주기 작업을 어떻게 돌리나

| 선택지 | 무엇 | 장점 | 단점 |
|-------|------|------|------|
| **(i) 앱 lifespan 안의 비동기 루프 + 환경변수 스위치(기본 꺼짐)** | uvicorn 프로세스 안에서 `asyncio` 태스크가 60초마다 실행 함수를 스레드에서 부른다 | S3.6 "컨테이너 내" 그대로, 새 의존성 0, 실행 함수를 직접 부르는 테스트로 대부분을 덮고 루프는 간격 주입으로 짧게 확인 | 워커를 여러 개 띄우면 루프도 여러 개 — `SKIP LOCKED`(U2)와 `briefed_at IS NULL` 로 중복 브리핑은 막지만 같은 분에 쿼리가 늘어난다. `main.py` 의 "lifespan 두지 않음" 문장을 고쳐야 한다 |
| (ii) APScheduler 같은 라이브러리 | 스케줄러 객체가 1분 작업을 등록 | 크론식 표현·실패 재시도 기능 | 의존성 추가, 이 패키지에는 "1분마다 한 번" 이상이 필요 없다(과설계) |
| (iii) 별도 프로세스(`python -m app.briefing.worker`) | 웹 서버와 분리된 루프 | 웹 워커 수와 무관하게 하나만 돈다 | 프로세스 하나를 더 띄워야 하고 그 구성은 P9-infra 몫 — 이 패키지에서는 로컬 실행 설명만 늘어난다 |
| (iv) 외부 cron 이 `POST /briefings/run` 호출 | EC2 cron/systemd 타이머 | 앱 코드 0 | 주기 작업이 앱 밖(인프라)으로 빠져 "컨테이너 내"(S3.6)와 다르고 이 패키지에서 확인할 수 없다 |

**권장: (i).** 예: 로컬에서 `BRIEFING_SCHEDULER_ENABLED=1` 로 서버를 켜 두면 1분 안에 내일 약속의 브리핑이 생기고, 스위치를 비워 두면(테스트·평소 개발) 아무 일도 일어나지 않는다. 기본을 꺼 둔 이유: 기존 테스트가 `TestClient` 컨텍스트로 앱을 띄울 때 실제 DB 를 매분 훑는 루프가 돌면 안 된다.

### 결정 B · "24시간 안" 에 이미 지난 일정을 넣나

S3.6 문장 `scheduled_at - now() ≤ 24h AND briefed_at IS NULL` 을 글자 그대로 읽으면 **이미 지난 일정도**(차이가 음수) 조건을 만족한다.

- **(i) `now ≤ scheduled_at ≤ now + 24h`** — 지난 일정은 넣지 않는다. 예: 서버가 사흘 꺼져 있다 켜지면 그 사이 지난 약속 10건의 브리핑이 한꺼번에 생기지 않는다. 만남 **직전** 맥락이라는 기획 의도와 맞다.
- (ii) S3.6 글자 그대로(지난 일정 포함) — 늦게라도 브리핑을 남긴다. 위 예에서 10건이 한 번에 생기고 LLM 도 10회 돈다.

**권장: (i).** 다만 (i) 은 S3.6 문장의 **해석을 좁히는 것**이므로 verifier 가 02-plan-verify 에서 "명세 안의 해석인가, 명세 변경인가" 를 판정해야 한다. 변경으로 판정되면 S3.6 카드에 한 줄 보충(문서 FIX)이 필요하다 — CR 까지는 아니라고 본다(검증 항목·결정을 바꾸지 않는다).

### 결정 C · 수동 트리거가 받는 인자

- (i) 인자 없음 — 주기 작업과 완전히 같다.
- **(ii) 선택 `schedule_id`** — 주면 그 일정 하나를 창·`briefed_at` 과 무관하게 즉시 브리핑(이미 브리핑했어도 다시 — `get_briefing` 이 `briefed_at` 을 최신 시각으로 덮어쓰는 기존 동작 그대로), 안 주면 주기 작업과 같다. 예: 발표자가 "다음 주 금요일 회식" 일정을 지금 바로 브리핑해 보여 준다(S3.6 "시간 앞당기기"·"발표자 수동 버튼").
- (iii) `as_of` 시각 주입 — API 로 "지금" 을 바꾼다. 데모엔 편하지만 운영 API 에 시간 조작 입구가 생긴다(테스트는 이미 `ctx.now` 주입으로 충분).

**권장: (ii).**

### 결정 D · 브리핑 문장을 무엇으로 만드나

- **(i) LLM 1회 구조화 출력 + 코드 검증 + 실패 시 템플릿 대체** — 일정마다 LLM 한 번으로 패턴 문장·요약 줄·제안 한 줄을 받고, 모든 줄에 근거 키·id 를 달게 한다. 공급자 오류·시간 초과면 템플릿(LLM 0)으로 만들고 `briefed_at` 은 그대로 기록한다(매분 재시도로 LLM 비용이 쌓이는 것을 막는다). 원칙6 "LLM 은 문장화만" 과 맞다.
- (ii) 템플릿만(LLM 0) — 재현성은 최고지만 "패턴 문장화는 LLM" 이라는 역할 분담(원칙6·P6-memory 결정 E)이 비고, 제안 한 줄을 규칙으로 만들기 어렵다.
- (iii) LLM 자유 문장(구조화 없음) — 근거를 기계로 확인할 수 없어 원칙7·9 를 지킬 수단이 없다.

**권장: (i).** 예: 공급자가 죽어 있어도 "민수 · 저녁 약속 · 패턴: conflict 3회 (2026-03-02, …) · 최근: 9/20 다툼" 같은 템플릿 브리핑은 나오고, 제안 줄만 빠진다.

### 결정 E · 원칙7 경계(제안 한 줄, 감정·고민 금지)를 무엇으로 지키나

- (i) 프롬프트 지시만.
- **(ii) 프롬프트 지시 + 코드 검증기** — 제안은 ① 근거(사실 키 또는 이벤트 id) ≥ 1 ② 근거가 입력에 실제로 있음 ③ 줄바꿈 없음·`BRIEFING_SUGGESTION_MAX_CHARS`(권장 80자) 이하 ④ 금지 표현 목록에 걸리지 않음. 하나라도 어기면 **제안만 버리고**(브리핑은 유지) 사유를 trace 에 남긴다. 금지 표현 초안(사용자가 고칠 수 있다): `기분`·`감정`·`위로`·`고민`·`상담`·`스트레스`·`마음이`·`힘드`·`우울`·`속상`·`서운`. 인물 간 관계 서술을 막기 위해 제안 근거는 **이 인물 한 명의** 사실·이벤트로만 한정한다(입력 자체가 한 인물 것뿐).

**권장: (ii).** 한계: 금지 표현 목록은 완전하지 않다(돌려 말하면 통과한다) — 판정 표 15·16행은 목록이 동작함을 보일 뿐 경계 전체를 증명하지 않는다. P10-final-eval 에서 제안 문장 표본 점검 항목으로 넘긴다.

### 결정 F · `person_facts` 의 세 출처를 브리핑이 어떻게 다루나

| 선택지 | 무엇 | 문제 |
|-------|------|------|
| (i) 전부 그대로 | `get_briefing` 이 준 사실 전부를 LLM 에 | 옛 자유 키 `소속=네이버` 와 `workplace=네이버` 가 둘 다 들어가 "소속 네이버, 직장 네이버" 처럼 중복 줄이 나온다 |
| **(ii) `pattern:*` + `FACT_KEYS` 9키만 쓰고, 그 밖 키는 `excluded_facts` 로 빼 trace 에만 남긴다. 같은 키가 여러 행이면 `updated_at desc` 첫 행** | 고정 어휘만 브리핑에 | 옛 자유 키에만 있는 정보(예: `이직=다음 달`)는 브리핑에서 빠진다 — trace 에는 남는다 |
| (iii) 옛 키를 9키로 사상(`소속`·`직장`→`workplace`) | 표를 만들어 바꿔 읽기 | 사상표가 추측이다(`이직` 은 `life_event` 인가 `workplace` 인가). 사실을 코드가 재해석하게 된다 |

**권장: (ii).** `get_briefing` 의 `facts`(원자료)는 손대지 않으므로 P8 인물 카드는 여전히 모든 행을 볼 수 있다. 같은 키 여러 행 규칙은 `update_person`(P2-tools 결정 6)과 같은 "`updated_at desc` 첫 행" 이다.

### 결정 G · 추출 품질 리스크(뜻이 뒤집힌 사실)를 이 패키지에서 다루나

사실: 2026-09-30 실 LLM 확인(journal 01:00, `fixes/evidence/FIX-015/20260930-0100-real-llm-check.txt`)에서 "매운 음식을 **못 먹어**" 가 `likes=매운 음식` 으로 저장됐다(같은 호출의 `dislikes=고수` 는 맞음). **이 사실은 승격 추출기가 아니라 루프 직접 사실(`app/agent/propose.py`, trace 181)에서 나왔다** — HANDOFF 의 "`build_extract_prompt()` 키 설명을 볼 값어치" 문장은 손볼 자리를 승격 쪽으로 적었으나 관측된 사례의 출처는 루프 제안기다. 브리핑이 이 사실을 그대로 쓰면 "민수가 좋아하는 매운 음식집을 예약하세요" 같은 **정반대 제안**이 나온다.

- (i) 이 패키지에서 다루지 않는다 — 리스크로만 남기고 P10-final-eval 에서 측정.
- **(ii) 소비 쪽 방어(이 패키지 U3·U4)** — 제안의 근거가 되는 사실에는 `fact_sources` 로 연결된 원문(`raw_utterance`, 사실당 최대 2건)을 LLM 입력에 함께 넣고 "사실과 원문이 어긋나 보이면 그 사실을 제안 근거로 쓰지 말라" 고 지시한다. **링크 없는 사실은 요약 줄에는 쓰되 제안 근거로는 못 쓴다**(검증기 `basis_not_eligible`). 원문은 응답·푸시 자리에 싣지 않고 LLM 입력과 trace 에만 둔다.
- (iii) 선행 FIX — P6-briefing 착수 전에 `propose.py`(와 `extract.py`)의 `likes`/`dislikes` 키 설명에 부정 표현("못 먹어", "싫어해" → `dislikes`) 지시를 더하는 FIX 를 먼저 한다.

**권장: (ii)**, 그리고 (iii) 은 이 패키지와 **별개의 FIX 후보**로 병행 기록(선행 조건으로 걸지 않는다). 근거: 이미 DB 에 저장된 잘못된 사실은 프롬프트를 고쳐도 남아 있으므로, 피해가 실제로 생기는 자리(제안)에서 막는 것이 먼저다. 한계: (ii) 도 LLM 판단에 기대므로 반전을 **줄일 뿐 없애지 못한다** — 측정은 P10-final-eval, 판정 표 18행은 "링크 없는 사실은 제안 근거 불가" 라는 코드 규칙만 확인한다. 비용: 원문 동봉으로 입력 토큰이 늘어난다(사실 8개 × 원문 2건 상한).

### 결정 H · 생성된 브리핑을 어디에 남기나 (스키마 v2 에 브리핑 테이블이 없다)

- **(i) 응답 + `briefing_compose` trace output 에만** — 스키마 무변경. 주기 작업이 만든 브리핑도 trace 에 남으므로 P7-push·P8 이 나중에 읽을 수 있다(조회 API 는 P8 에서 정한다). 로그를 결과 저장소로 쓰는 것은 P6-memory 결정 B(ii) 와 같은 선택이고 같은 한계를 가진다(trace 를 지우면 브리핑도 사라진다).
- (ii) `briefings` 테이블 신설 — 가장 명확하지만 **S3.1 변경**이라 `/devlog change` CR 선행.
- (iii) 저장하지 않음 — 화면이 열릴 때마다 다시 생성(LLM 재호출, 결과가 매번 달라짐 — 원칙8 재현성 약화).

**권장: (i).** (ii) 를 고르면 이 계획은 CR 이행 뒤로 밀린다.

### 결정 I · trace 어휘

- `tool_name = "briefing"`(P5 `"agent"`, P6-memory `"memory"`, ER `"er"` 와 같은 층위). `session_id = "briefing:<uuid4>"` — 실행 하나(주기 한 번 또는 수동 한 번)가 하나의 세션이다(`agent_traces.session_id` 는 NOT NULL).
- `briefing_run`: 실행마다 1행. output `{trigger: scheduler|manual, now, window:{from,to}, lead_hours, schedule_id_arg, selected:[schedule_id], skipped:[{schedule_id, reason}], briefed:[schedule_id], errors: n}`, tokens 0.
- `briefing_compose`: 일정마다 1행. output `{schedule_id, person_id, pattern_trace_id, used_facts:[{key, fact_id, eligible}], excluded_facts:[{key, fact_id, reason}], event_ids, composer: llm|template, fallback_reason?, pattern_sentences, lines:[{text, basis}], suggestion:{text, basis}|null, rejected:[{item, reason}], llm:{provider, model}, push}`, tokens = 생성기 사용량(`trace_tokens()`). 원문(`raw_utterance`)은 trace 문자열 절단 규약(`TRACE_MAX_STRING`)을 따르고 프롬프트 전문·키는 기록하지 않는다(security §1).
- `briefing_error`: 일정 단위 실패 1행 `{schedule_id, person_id, stage: select|patterns|briefing|compose|notify, error}` — 세이브포인트 롤백 **뒤** 바깥에서 쓴다.
- 권장안 그대로면 고를 것은 없고 이름만 확인한다.

### 결정 J · 푸시를 보낼 자리

- **(i) `Notifier` Protocol(`notify(schedule, composed) -> str`) + 기본 `NullNotifier`(아무것도 보내지 않고 `"not_configured"` 반환)** — P7-push 는 이 자리에 `WebPushNotifier` 를 끼우기만 한다. 순서는 S3.6 대로 브리핑 생성 → 푸시 자리 → (같은 세이브포인트 커밋으로) `briefed_at` 확정.
- (ii) 자리를 두지 않는다 — P7 이 실행 함수 본문을 고쳐야 한다.

**권장: (i).** **경계**: 이 패키지에서 `briefed_at` 은 푸시 결과와 무관하게 기록된다(보낼 곳이 없으므로). "푸시가 실패하면 `briefed_at` 을 남길지" 는 P7-push 가 정한다(인계).

### 결정 K · 패턴을 언제 다시 계산하나

- **(i) 브리핑 대상 인물만, 브리핑 직전에 `detect_patterns` 1회** — 브리핑에 쓰이는 패턴만 최신이 된다. 비용은 쿼리 1개 + `memory_pattern` trace 1행.
- (ii) 주기 작업 한 번마다 모든 인물 — 인물 카드(P8)의 낡은 패턴까지 지워지지만 매분 인물 수만큼 쿼리·trace 행이 쌓인다(하루 1,440 × 인물 수).

**권장: (i).** 인물 카드가 낡은 패턴을 보이는 문제는 P8 이 카드 조회 때 같은 함수를 부를지 정한다(인계).

## 지킬 불변식 (수용 기준 밖)

- **푸시 발송 코드 없음.** `grep -rniE "pywebpush|vapid|push_subscriptions|PushSubscription" app/briefing/ app/api/ app/main.py` → 0건.
- **원문(`events`) 삭제·수정 금지.** `grep -rnE "delete\(Event|update\(Event|\.raw_utterance\s*=[^=]|\.content\s*=[^=]" app/briefing/` → 0건. 권위 있는 판정은 판정 표 27행 테스트.
- **패턴 판정에 LLM 없음(원칙6).** `app/briefing/select.py`·`inputs.py` 는 `app.briefing.compose`·`app.er.judge`·`app.embedding` 을 import 하지 않는다(테스트가 모듈 import 목록 단언). `person_facts` 의 `pattern:*` 행을 `app/briefing/` 이 직접 쓰지 않는다: `grep -rnE "PersonFact\(|insert\(PersonFact|update\(PersonFact" app/briefing/` → 0건.
- **기존 코드 무변경.** `git diff --stat 36c288e -- app/tools/briefing.py app/agent app/memory app/er` → 빈 출력.
- `app/briefing/` docstring·주석에 "evaluation" 금지: `grep -rn "evaluation" app/briefing/` → 0건.
- 응답·`Notifier` 인자에 `raw_utterance` 원문을 싣지 않는다(판정 표 24행 테스트).

## 리스크 · 미결

- **추출 품질(결정 G)** — 뜻이 뒤집힌 사실(`likes=매운 음식`)이 이미 DB 에 있다. 권장안 (ii) 는 제안 단계에서 줄일 뿐 없애지 못하고, 요약 줄에는 잘못된 사실이 그대로 보일 수 있다. 측정은 P10-final-eval. 별개 FIX 후보: 루프 제안기(`propose.py`)·승격 추출기(`extract.py`) 의 `likes`/`dislikes` 키 설명에 부정 표현 지시 추가.
- **금지 표현 목록의 한계(결정 E)** — 돌려 말한 감정·상담 문장은 목록을 통과한다. 경계의 1차 방어는 프롬프트와 "근거 필수" 규칙이고 목록은 보조다.
- **lifespan 추가가 기존 테스트에 주는 영향(결정 A)** — 기존 `TestClient` 사용 테스트 4파일(9곳). 스위치 기본 꺼짐으로 무영향이어야 하며 U7 판정에 그 4파일 회귀를 넣었다.
- **여러 워커(결정 A(i))** — `SKIP LOCKED`·`briefed_at IS NULL` 로 중복 브리핑은 막지만, P9-infra 가 워커 수를 늘리면 루프도 늘어난다. 배포 때 "스위치는 한 프로세스에서만 켠다" 를 RUNNING 에 적는다.
- **`get_briefing` 이 `briefed_at` 을 생성기보다 먼저 쓴다** — 같은 세이브포인트 안이므로 생성기 밖 예외면 함께 되돌려지고(판정 22행), 생성기 오류는 템플릿 대체로 브리핑이 생기므로 기록이 맞다(결정 D). 템플릿까지 실패하는 경우는 생성기 밖 예외로 취급한다.
- **로그를 결과 저장소로(결정 H(i))** — trace 정리 정책이 생기면 브리핑 기록도 사라진다. 현재 정리 정책 없음(P6-memory 결정 B(ii) 와 같은 리스크).
- **결정 B(i) 의 명세 해석 여부** — verifier 판정 필요(결정 B 본문).
- **실 공급자 확인** — 자동 테스트는 전부 가짜 생성기다. 한국어 문장 품질·경계 준수는 U8 의 사용자 실행 1회로만 본다.
- **시간대** — 창 계산은 UTC 절대 시간(24시간), 문장 속 날짜만 `user_timezone()`. "내일 저녁" 같은 상대 표현은 쓰지 않고 날짜로 쓴다(프롬프트 지시 + 템플릿).
- **미결(사용자 결정 필요)**: 결정 A~K 전부(권장안만 표시). 그중 범위가 크게 갈리는 것은 **D(LLM 사용 여부)·G(추출 품질 대응)·H(스키마 변경 여부)** 셋이다.

## 후행 패키지가 이 패키지에서 기대하는 것

- **P7-push**: `Notifier` Protocol 자리와 `briefing_compose.output.push` 필드. 푸시 실패 시 `briefed_at` 처리(되돌릴지)를 P7 이 정한다. VAPID 키·구독 저장은 전부 P7.
- **P8-frontend**: 브리핑 화면이 읽을 자료 = `POST /briefings/run` 응답 모양과 `briefing_compose` trace(결정 H(i)). 조회 API 와 "인물 카드 열 때 패턴 재계산" 여부는 P8 이 정한다.
- **P9-infra**: `BRIEFING_SCHEDULER_ENABLED` 를 웹 프로세스 하나에서만 켠다.
- **P10-final-eval**: 제안 문장의 경계 준수 표본 점검, 뜻이 뒤집힌 사실이 제안에 쓰인 비율(`briefing_compose` trace 의 근거 id 로 역추적).

## 읽은 카드

- `docs/wiki/templates/plan.md` 전문(형식)
- `docs/wiki/specs/S3.6-briefing-push.md` 전문, `docs/wiki/specs/S3.5-memory-promotion.md` 전문, `docs/wiki/specs/S3.2-tools-v2.md`(`get_briefing` 행만 grep), `docs/wiki/specs/S3.1-schema-v2.md`(`schedules` 행만 grep)
- `docs/wiki/decisions/D14-pattern-window-config.md` 전문
- `docs/resolution-plan.md` §3.6(195~198행), 235행(P6 표 행)
- `docs/wiki/review-index.md` R12·R19 행(grep), `docs/wiki/INDEX.md` 전문(패키지 표·태그 어휘), `docs/wiki/CURRENT.md` 전문, `docs/backlog.md` P6~P8 절(77~89행)
- `docs/wiki/registry.md` 50~69행 + grep(`briefing`·`schedules`·`ctx.now`·`routes.py`·`deps.py`·`respond`)
- `docs/wiki/packages/P6-memory/01-plan.md` 전문(형식·결정 C-5·E 인계), `docs/wiki/packages/P6-memory/04-review.md` 전문(§6 권고·§7 인계)
- `docs/wiki/HANDOFF.md` 전문("다음 패키지가 알아야 할 것"·"열린 질문"), `docs/wiki/journal.md` 353행(2026-09-30 실 LLM 확인 — grep)
- `.claude/gitlog.md`(2026-10-02 11:46 스냅샷), `.claude/scripts/verify-plan.sh` 1~70행(형식 요건)
- 코드 읽기(쓰지 않음): `app/tools/briefing.py` 전문, `app/tools/types.py` `BriefingOut`(132~161행), `app/tools/context.py` `ToolContext`(91~106행), `app/main.py` 전문(lifespan 없음·리스크 A), `app/api/` 함수 목록(grep), `app/memory/` 정의 목록(grep), `app/memory/extract.py` 614~632행(`FACT_EXTRACTORS`·`extractor_from_env`), `app/db/models.py` `session_id` 줄(grep), `requirements.txt`(스케줄러·푸시 의존성 없음 확인)
- 열지 않은 것: D11 카드(P6-memory 01-plan 이 이미 인용한 "등록표 재사용" 규칙만 따른다), `docs/wiki/security.md`(§1·§5 는 P6-memory 계획 인용을 따랐다 — verifier 가 원문 대조)
