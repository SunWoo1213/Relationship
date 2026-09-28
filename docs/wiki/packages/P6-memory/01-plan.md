# P6-memory · 계획 (01-plan)

상태: 1차 개정본(architect 작성 — 결정 A~G 사용자 확정, 02-plan-verify 재검증은 verifier 몫) | 담당: backend-agent(`app/memory/`·`app/agent/loop.py` 연결 한 자리·`app/tools/persons.py` 키 보호 한 자리·`app/api/deps.py`·`app/settings.py`·`.env.example`) | 작성: 2026-09-28
개정 이력: 1차(2026-09-28) — 02-plan-verify 보류 H-1~H-3·권고 R-1~R-9 반영 / 승인 전 추가(2026-09-28, 사용자 결정): `MEMORY_PROMOTE_MIN_EVENTS` 도 환경변수로 덮을 수 있게(기본 5 불변), 앱 안 사용자별 선택은 범위 밖 — backlog 신규 항목
태그 — 패키지: P6-memory · 닫는 검증: R8 R11 · 기대는 결정: D14(D9 대체, CR-002) D11 D6 · 구현하는 명세: S3.5 S3.1 S3.2 · 관련 원칙: 원칙6 원칙7 원칙8 원칙9
의존: P5-loop(04-review `결과: 완료`, 완료 처리 커밋 f9bfba7) · 선행 게이트 P4b-er-redesign(04-review `결과: 완료`)

- 근거 해시(`.claude/gitlog.md` 스냅샷 2026-09-28 13:40, Bash 없이 읽음 — L-001): dev = `2de7416`(CR-002 문서 커밋, origin/dev 보다 ahead 1) · main = origin/main = `1e4afb4`(FIX-006). `2de7416` 의 변경 파일 14개는 전부 문서·하네스(`docs/`·`.claude/`·`CLAUDE.md`)이고 `app/` 은 무변경이다. P5-loop 단위 커밋 U1 `3e4db92` ~ U8 `f0d3e26`, 완료 처리 `f9bfba7`, 실서버 왕복 증거 `ad4f30f`. FIX-005(사용자 시간대) `1f07429`, FIX-006(테스트 전용 DB) `1e4afb4`. **이 패키지의 시작 해시(무변경 diff 기준점) = `2de7416`(코드 기준으로는 `1e4afb4` 와 동일).** 스냅샷 시점 미커밋 변경은 `docs/wiki/journal.md`·`HANDOFF.md` 와 이 패키지 폴더뿐이고 제품 코드는 0이다.
- 이 태그로 이미 있는 커밋: `9cb35b6`(P2-tools U5 — `add_event` 에 "패턴 감지·승격 트리거 없음" 을 명시한 커밋), `5dc95bb`(P1-schema 완료 — `fact_sources` 테이블 생성). 둘 다 "P6-memory 가 채운다" 는 꼬리표이고 코드는 없다. 태그별 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P6-memory D9 D14 R8 R11` 실행을 요청**한다.
- P5-loop 04-review §7 인계: "승격 훅은 `app/agent/loop.py` 의 `_record_impl`(기록 단계, `loop_record` 한 행) 뒤에 건다. `add_event` 는 `raw_utterance` 를 발화 원문 그대로 받는다(루프 주입)."

## 목표

`docs/resolution-plan.md` §3.5(187~192행)와 S3.5 카드의 네 문장을 코드로 옮긴다. 지금은 대화에서 나온 일이 `events`(에피소드 계층, 원문 보존)에 한 줄씩 쌓이기만 하고, **"이 사람은 어떤 사람인가"(시맨틱 계층 `person_facts`)로 올라가는 길이 없다**. `fact_sources` 테이블은 P1-schema 가 만들어 두었지만 아무도 채우지 않으며(review-index R8 행 "P6-memory 가 승격 시 채움"), 반복 패턴 감지(R11, D9)는 결정만 있고 구현이 없다. 이 패키지는 두 가지를 만든다. ① **승격**: 같은 인물의 아직 승격되지 않은 이벤트가 5건 이상 쌓이면 LLM 이 그 이벤트들에서 사실 후보를 뽑고, 코드가 `person_facts` 에 upsert 하며 사실마다 근거 이벤트를 `fact_sources` 로 잇는다 — 브리핑·인물 카드가 "이 사실은 어느 대화에서 나왔나" 를 원문까지 거슬러 보여 줄 수 있게 된다(R8). ② **패턴**: 같은 인물의 같은 `events.type` 이 90일 안에 3번 이상이면 **규칙(코드)** 이 `person_facts(key="pattern:{type}", value="{n}회 (날짜 목록)", confidence=1.0)` 를 만들고 근거 이벤트를 잇는다 — 판정에 LLM 을 쓰지 않으므로 같은 데이터에서 언제나 같은 결과가 나온다(원칙6·8, D9). 예: 사용자가 석 달 동안 "민수랑 또 싸웠어" 를 세 번 말하면 민수 카드에 `pattern:conflict = "3회 (2026-07-02, 2026-08-11, 2026-09-20)"` 가 생기고, 그 세 날짜의 원문 세 줄이 연결된다. **원문(`events`)은 어떤 경우에도 지우지 않는다**(S3.5). 새 D 카드·새 명세를 만들지 않는다 — S3.5·D9 가 이미 적어 둔 것을 옮길 뿐이며, 명세가 비워 둔 "미승격을 어떻게 표시하나" 는 아래 결정 B 에서 **스키마를 바꾸지 않는 선택지**를 권장안으로 둔다(스키마를 바꾸는 선택지는 S3.1 변경이라 `/devlog change` 가 필요하다고 표시).

## 범위

- 포함:
  - **패턴 감지(규칙)** — `app/memory/patterns.py`. 한 인물의 이벤트를 `type` 별로 세어 설정된 창(`PATTERN_WINDOW_DAYS`, 기본 365일) 안 설정된 횟수(`PATTERN_MIN_COUNT`, 기본 3회) 이상이면 `pattern:{type}` 사실을 만들거나 갱신하고, 창 안 이벤트 전부를 `fact_sources` 로 잇는다. SQL 과 파이썬만 쓰고 LLM·임베딩을 부르지 않는다(원칙6). 기간·횟수·접두 `pattern:` 은 `app/settings.py` 설정값(D14 — CR-002. 원 D9 "90일·3회는 설정값").
  - **승격(LLM 추출 + 코드 upsert)** — `app/memory/extract.py`(사실 추출기: 공급자 등록표 재사용, 구조화 출력 스키마, 검증기, 가짜 구현) + `app/memory/promote.py`(미승격 이벤트 조회, 5건 트리거, upsert, `fact_sources` 연결).
  - **`pattern:` 접두 키 보호** — LLM(루프의 `update_person` 제안이든 승격 추출기든)이 `pattern:` 로 시작하는 키를 만들지 못하게 막는다. 지금 P5 루프의 인식 단계는 `update_person(facts=[{key, value}])` 를 **자유 키**로 제안할 수 있고(`app/agent/propose.py` `PROPOSAL_ARG_SCHEMA.facts.key` 가 enum 없는 문자열, `app/agent/gate.py` 231~239행은 모양만 본다), `app/tools/persons.py` `update_person`(534~555행)도 키를 거르지 않는다 — 즉 **현재 코드에서 LLM 이 `pattern:conflict` 를 직접 써 넣을 수 있는 구멍이 실제로 있다**. 이 구멍을 툴 자리 한 곳에서 막는다(결정 D-7).
  - **루프 연결 한 자리** — `app/agent/loop.py::_record()` 의 기록 단계 trace 가 끝난 **뒤** 한 줄로 `app.memory` 진입점을 부른다(P5-loop 04-review §7 인계). `run_turn`·`resume_turn` 이 모두 `_record()` 를 지나므로(loop.py 962행·1286행) 두 경로가 한 자리에서 덮인다. 승격·패턴 실패는 세이브포인트로 그 부분만 되돌리고 턴은 그대로 성공시킨다(이벤트 저장을 잃지 않는다).
  - **HTTP 의존성 주입** — `app/api/deps.py` 에 추출기 공급 함수 1개(`get_fact_extractor`, 기존 `get_proposer`·`get_judge` 와 같은 모양). 새 엔드포인트는 만들지 않는다(결정 A 권장안 기준).
  - **관측성** — 새 trace 어휘 `memory_pattern`·`memory_promote`·`memory_error`(결정 F). 판정마다 입력·출력·근거 이벤트 id·토큰 in/out 을 남긴다(원칙9).
  - **문서·설정 예시** — `registry.md` 새 행·비고 확장, `docs/RUNNING.md` 에 "승격·패턴이 언제 도는가" 한 절(설정 상수 6개 중 환경변수로 덮을 수 있는 것은 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS` 3개), `.env.example` 에 그 3개의 기본값 줄(이름과 "비우면 기본 365/3/5" 설명만 — 비밀 없음, D14·CR-002, security §1).
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **브리핑 생성·패턴 문장화(LLM)·주기 작업(1분)·수동 트리거 `POST /briefings/run`**(S3.6·P6-briefing) — 문장화는 브리핑 화면에서 쓰이는 표현이고, 이 패키지의 `value` 는 이미 사람이 읽을 수 있는 규칙 문자열이다. 여기서 LLM 문장화까지 하면 LLM 호출 자리가 두 곳으로 늘고 P6-briefing 수용 기준("`POST /briefings/run`으로 브리핑 생성")과 경계가 흐려진다(결정 E 권장안).
  - **웹푸시**(P7-push) · **프론트 3화면·인물 카드 원문 펼치기 UI**(P8-frontend, 원칙5) — 이 패키지는 카드가 읽을 **데이터(사실 + 근거 링크)** 만 만든다.
  - **스키마 v2 변경·마이그레이션** — S3.1 이 권위다. 결정 B 에서 컬럼 추가(B(iii))를 고르면 이 패키지 밖에서 `/devlog change` CR 로 먼저 처리해야 한다(아래 리스크).
  - **툴 7종 시그니처 변경** — S3.2·R10 이 확정했다. `update_person` 은 시그니처를 그대로 두고 **값 검사 한 줄**(`pattern:` 접두 거부)만 더한다.
  - **`app/er/` 수정** — P4b 게이트 수치(`0.8 [] True True`)의 근거 코드다(원칙8). 공급자 등록표는 **import 해서 쓰기만** 한다.
  - **새 API 엔드포인트**(예: `POST /memory/promote`) — backlog 수용 기준에 없다. 필요해지면 P6-briefing 의 수동 트리거와 함께 검토한다.
  - **추출 품질 지표(사실 추출 정밀도 등)·150건 평가**(P10-final-eval) — 이 패키지는 측정 대상을 만들 뿐 지표를 내지 않는다.
  - **고민 상담·감정 대화, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성, 네이티브 앱**(원칙7) — 추출기가 뽑는 사실은 **그 한 인물**에 관한 기록된 사실뿐이다. "민수와 지훈이 사이가 안 좋다" 같은 두 인물 사이의 관계는 사실 키 어휘에 자리가 없고(결정 D-5), 감정 해석·조언 문장도 만들지 않는다. 검증기는 스키마 밖 키를 거부한다.
  - **이미 저장된 사실의 삭제·병합 정리 도구, 다중 사용자 격리** — backlog 어느 항목에도 없다(P5-loop 결정 I 와 같은 단일 사용자 전제).

## 산출물 (파일 경로)

**새로 만드는 파일**

- `app/memory/__init__.py` — 진입점 재export(`after_record`·`detect_patterns`·`promote_person`·추출기 Protocol·가짜·trace 상수)
- `app/memory/types.py` — 결과 타입(`PatternResult`·`PromotionResult`·`ExtractedFact`·`Extraction`), trace 어휘 상수(`MEMORY_TRACE_TOOL_NAME = "memory"`, step 3종), 사실 키 어휘 `FACT_KEYS`(결정 D-5)
- `app/memory/patterns.py` — 규칙 기반 패턴 감지(LLM 미사용)
- `app/memory/extract.py` — `FactExtractor` Protocol·`FACTS_SCHEMA`·`build_extract_prompt()`·`validate_extraction()`·공급자 구현(등록표 재사용)·`extractor_from_env()`·`FakeFactExtractor`
- `app/memory/promote.py` — 미승격 이벤트 조회·트리거·upsert·`fact_sources` 연결, `after_record()`(루프가 부르는 한 진입점)
- `tests/test_memory_patterns.py` — 패턴 규칙(경계값·창·인물 분리·갱신·미달 처리·근거 링크)
- `tests/test_memory_extract.py` — 추출 스키마·검증기·오류 매핑·가짜(네트워크 0)
- `tests/test_memory_promote.py` — 트리거·upsert·링크·원문 불변·미승격 판정
- `tests/test_memory_loop.py` — 루프 연결(`run_turn`·`resume_turn`)·실패 격리·`POST /chat` 한 흐름

**고치는 기존 파일** (registry 에 다른 패키지 행으로 있다 — 새 행이 아니라 비고 확장)

| 파일 | 고치는 내용 | 원래 패키지 |
|------|------------|------------|
| `app/settings.py` | 상수 추가: `PATTERN_WINDOW_DAYS=365`·`PATTERN_MIN_COUNT=3`(D14 — 환경변수 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT` 로 덮어씀, 양의 정수만·아니면 `InvalidValue`·비우면 기본값; `MEMORY_PROMOTE_MIN_EVENTS=5` 도 환경변수 `MEMORY_PROMOTE_MIN_EVENTS` 로 덮어씀(같은 규칙, 기본 5 = S3.5 — 사용자 결정 2026-09-28 승인 전 추가, 읽기 함수 `promote_min_events(env=None)`); 읽기 함수 `pattern_config(env=None)`)·`PATTERN_KEY_PREFIX="pattern:"`·`MEMORY_PROMOTE_MAX_EVENTS`·`MEMORY_MAX_FACTS`(결정 D-4) | P2-tools |
| `app/tools/persons.py` | `update_person` 의 `facts` 검사에 `PATTERN_KEY_PREFIX` 접두 거부(`InvalidValue`) 한 조건. 시그니처 불변 | P2-tools |
| `app/agent/loop.py` | `_record()` 끝에서 `app.memory.after_record(...)` 호출 한 자리 + `run_turn`/`resume_turn` 에 `extractor` 키워드 인자(기본 `None` → `extractor_from_env()`). `loop_record` output 의 기존 키는 불변 | P5-loop |
| `app/api/deps.py` · `app/api/routes.py` | `get_fact_extractor()` 추가, `POST /chat`·`POST /answers/{id}` 가 주입받아 넘긴다 | P2-tools / P5-loop |
| `tests/test_tools_persons.py` | `pattern:` 키 거부 케이스 추가(기존 단언 삭제 없음) | P2-tools |
| `.env.example` | 세 줄 추가: `PATTERN_WINDOW_DAYS=`·`PATTERN_MIN_COUNT=`·`MEMORY_PROMOTE_MIN_EVENTS=`(값은 비워 두고 주석으로 "비우면 기본 365일 / 3회 / 5건, 양의 정수만" 설명만 — 비밀 없음, security §1). D14 11행·CR-002 16행 요구(U1) | 하네스(registry 38행) |
| `docs/RUNNING.md` · `docs/wiki/registry.md` | 실행 설명 한 절 · 행 추가/비고 확장 | — |

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

각 단위의 완료 판정 명령은 로컬 기준 `POSTGRES_PORT=5433 pytest …` 이고 테스트 DB 는 `relationship_test`(FIX-006, `tests/conftest.py` 가 스스로 준비)다. 모든 테스트는 **실 키·네트워크 없이** 돈다(가짜 추출기·스텁 임베더). 출력은 `docs/wiki/packages/P6-memory/evidence/<YYYYMMDD-HHMM>-<이름>.txt` 로 남긴다.

- [ ] U1 골격 — 설정 상수 6개(그중 환경변수로 덮는 것은 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS` 3개), `.env.example` 에 그 3개의 기본값 줄(이름 + "비우면 기본 365/3/5" 설명 주석만, 비밀 없음 — D14·CR-002), `app/memory/__init__.py`·`types.py`(결과 타입·trace 어휘·`FACT_KEYS`), 도는 코드 없음. 판정: `pytest tests/test_memory_patterns.py -k constants`(상수 값·어휘 단언, `pattern_config()` 기본 365/3·`promote_min_events()` 기본 5·환경변수 덮어쓰기·0/음수/문자 거부) + `python -c "import app.memory"` + `grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example`(3건) · 증거 `evidence/*-u1-*.txt` / Refs: P6-memory D14 CR-002 S3.5 원칙9
- [ ] U2 패턴 감지 규칙 — `detect_patterns(ctx, person_id) -> PatternResult`. 첫 줄에서 `app/tools/persons.py` 의 `_owned_person(ctx.session, person_id, ctx.user_id)` 를 재사용해 소유를 확인한다(security §5 — 새 소유 검사 함수를 만들지 않는다). 창 = `[now − PATTERN_WINDOW_DAYS일, now]`(결정 C-2, 기본 365일 — D14), `occurred_at` 기준, 인물·`type` 별 개수 ≥ `PATTERN_MIN_COUNT`(기본 3) → `pattern:{type}` upsert(`confidence=1.0`, value 형식 결정 C-3), `fact_sources` 를 창 안 이벤트 집합으로 맞춘다(추가·빠진 링크 제거, 이벤트 행은 불변), 기준 미만으로 떨어진 기존 패턴은 결정 C-5 대로. `memory_pattern` trace 1행(tokens 0) — **이번 판정에 실제로 쓴 기간·횟수를 output 의 `window_days`·`min_count` 에 기록한다(D14, 결정 F)**. LLM·임베딩 import 없음. 테스트에 다른 `user_id` 의 인물 id 로 호출 → `PersonNotFound`·패턴 행 0 한 건. 판정: `pytest tests/test_memory_patterns.py -v` · 증거 `evidence/*-u2-patterns.txt` / Refs: P6-memory D14 D9 S3.5 R11 원칙6 원칙8 원칙9
- [ ] U3 `pattern:` 접두 키 보호 — `update_person(facts=[{key:"pattern:…"}])` → `InvalidValue`(키 앞뒤 공백·대소문자 변형 포함). 패턴 모듈은 `update_person` 을 거치지 않고 ORM 으로 직접 쓴다(fact id 가 필요하고 `confidence=1.0` 고정이므로). 판정: `pytest tests/test_tools_persons.py -k pattern -v` + 기존 `tests/test_tools_persons.py` 전체 통과 · 증거 `evidence/*-u3-key-guard.txt` / Refs: P6-memory D14 D9 S3.2 원칙6
- [ ] U4 사실 추출기 — `FactExtractor.extract(person, existing_facts, events) -> Extraction`. 입력은 인물 표시 이름·기존 비패턴 사실·이벤트 `{id, type, content, raw_utterance, occurred_at}` 목록. 출력 스키마 `{facts: [{key ∈ FACT_KEYS, value, source_event_ids: int[≥1]}]}`. 검증기는 키 어휘 밖·`pattern:` 접두·빈 값·입력에 없는 이벤트 id·상한 초과를 **개별 사실 단위로 거부**하고 사유를 남긴다. 공급자는 `app/er/judge.py` 의 `select_provider`·`call_with_error_mapping`(+Gemini 매핑)을 import(`app/agent/propose.py` 와 같은 방식, D11 — 자체 등록표 금지). 오류 어휘는 기존 6종만. `FakeFactExtractor`(표 기반·결정적·네트워크 0). 판정: `pytest tests/test_memory_extract.py -v` · 증거 `evidence/*-u4-extract.txt` / Refs: P6-memory S3.5 D11 R8 원칙8
- [ ] U5 승격 — `promote_person(ctx, person_id, extractor) -> PromotionResult | None`. 첫 줄에서 `_owned_person(ctx.session, person_id, ctx.user_id)` 재사용(security §5, U2 와 같음). 미승격 판정(결정 B(ii))은 `agent_traces` 를 **`session_id` 와 무관하게** `step='memory_promote' AND output->>'person_id' = :id` 로 세션을 넘어 누적 조회해 `considered_event_ids` 합집합에 없는 그 인물의 이벤트를 센다. 미승격 이벤트 ≥ `promote_min_events()`(기본 5, 환경변수로 덮음) 일 때만 추출기 1회 호출, 오래된 순 최대 `MEMORY_PROMOTE_MAX_EVENTS` 건. 사실마다 `(person_id, key)` upsert(결정 D-6) → `fact_sources(fact_id, event_id)` 연결. `memory_promote` trace 1행(tokens 는 추출기 사용량, 이번 판정에 실제로 쓴 `min_events`(R-14), `considered_event_ids`·사실별 `action`·이전 값·거부 사유). `events` 행은 읽기만 한다. 테스트에 다른 `user_id` 인물 id 로 호출 → `PersonNotFound`·추출기 호출 0 한 건, 다른 `session_id` 로 앞서 승격된 이벤트를 미승격으로 세지 않는 케이스 한 건. 판정: `pytest tests/test_memory_promote.py -v` · 증거 `evidence/*-u5-promote.txt` / Refs: P6-memory S3.5 S3.1 R8 원칙8 원칙9
- [ ] U6 루프 연결 — `after_record(ctx, person_ids, extractor)`: 이번 턴에 `add_event` 가 **실제로 실행된** 인물마다 ① `detect_patterns` ② `promote_person` 순서(결정 C-1). 인물 id 는 `_record_impl` 이 돌려주는 `RecordOutcome` 에 **`event_person_ids: list[int]`**(실행 성공한 `add_event` 의 `person_id`, 중복 제거·첫 등장 순) 필드를 추가해 얻는다 — 지금 `RecordOutcome(executed, failed, events, schedules, schedule_question)` 에는 인물 id 가 없다. `loop_record.output` 의 기존 키는 바꾸지 않으며, output 에 새 키를 더하면 U6 03-log 에 적는다(P5 U1 스키마 규약). 전체를 `ctx.session.begin_nested()` 로 감싸 실패 시 그 부분만 되돌린다 — 이 롤백으로 안쪽의 `memory_pattern`·`memory_promote`·`tool_error` 행도 함께 사라지므로(결정 B(ii) 의 "실패하면 다음에 재시도" 가 성립하는 이유), **`memory_error` 행은 세이브포인트 롤백이 끝난 뒤 바깥 트랜잭션에서 기록한다**(그래야 판정 16행의 `memory_error` 가 남는다). 턴 응답은 그대로(`SQLAlchemyError` 는 P5 규약대로 올린다). `run_turn`·`resume_turn`·`POST /chat`·`POST /answers/{id}` 에 추출기 주입. 응답 문장(`respond.py`)은 바꾸지 않는다. 판정: `pytest tests/test_memory_loop.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py -v` · 증거 `evidence/*-u6-loop.txt` / Refs: P6-memory S3.5 R8 R11 원칙9
- [ ] U7 (결정 G 가 (ii) 일 때만) 루프 직접 사실의 원문 연결 — 같은 턴에 같은 인물로 `update_person(facts)` 와 `add_event` 가 함께 실행되면, 그 사실들을 그 턴의 이벤트에 `fact_sources` 로 잇는다. `update_person` 은 fact id 를 돌려주지 않으므로 id 는 이렇게 얻는다: `_record_impl` 이 실행에 성공한 `update_person` 호출의 `person_id` 와 `call.args["facts"][].key`(툴이 저장한 것과 같게 앞뒤 공백 제거)를 U6 의 `event_person_ids` 와 같은 자리에서 모아 `RecordOutcome` 에 `fact_keys_by_person: dict[int, list[str]]` 로 넘기고(`executed[]` 항목에는 인자가 없다 — loop.py 862행), 그 키로 `(person_id, key)` 를 조회해 `updated_at desc` 첫 행을 쓴다(기존 upsert 관례, "기존 산출물 재사용" 표 2행). 같은 턴에 같은 키가 두 번 실행되면 upsert 결과 행이 하나뿐이므로 그 행 하나에 한 번만 잇는다(`fact_sources` 복합 PK 가 중복을 막는다). 이벤트가 없는 턴의 사실은 연결 없이 두고 `memory_*` trace 에 `unlinked` 로 적는다. 결정 G 가 (i) 이면 이 단위는 없애고 리스크에 남긴다. 판정: `pytest tests/test_memory_loop.py -k direct_fact -v` · 증거 `evidence/*-u7-direct-facts.txt` / Refs: P6-memory R8 S3.5 원칙9
- [ ] U8 수용 기준 기계 검증·문서 — 아래 판정 표 전 행 실행, 전체 회귀(`POSTGRES_PORT=5433 pytest -rs`, skip 0), 금지 문자열 grep(판정 표 19행 — 명령은 "지킬 불변식" 절에 적은 것 그대로), `alembic check`(스키마 무변경), `scripts/tools_check.py` 7/7(시그니처 무변경), `registry.md`·`docs/RUNNING.md` 갱신(RUNNING 절에 "설정 상수 6개 중 환경변수 3개" 로 적는다). 증거 `evidence/*-u8-*.txt` / Refs: P6-memory R8 R11 D14 S3.5 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pattern:{type}` 사실 생성

### 해석 (위 한 줄을 판정 가능한 문장으로 — 새 기준을 더하는 것이 아니다)

| # | 원문 구절 | 이 계획의 해석 |
|---|----------|--------------|
| ㄱ | 승격 후 | 같은 인물의 미승격 이벤트가 5건 이상일 때 승격이 한 번 돈 뒤 |
| ㄴ | 사실→원문 링크 존재 | 승격이 새로 만들거나 갱신한 `person_facts` 행 **전부**가 `fact_sources` 로 ≥ 1개의 `events` 행에 이어져 있고, 그 이벤트는 같은 인물의 것이며 `raw_utterance` 가 저장 당시 그대로다 |
| ㄷ | 설정된 기간·횟수 규칙(기본 365일 3회) | 같은 인물·같은 `type`·`occurred_at` 이 `[now − PATTERN_WINDOW_DAYS일, now]` 안인 이벤트가 `PATTERN_MIN_COUNT` 건 이상(기본 365일·3건). 실제 쓴 기간·횟수를 `memory_pattern` trace output 의 `window_days`·`min_count` 에 기록(D14, 결정 F). 판정은 코드 규칙, LLM 호출 0회 |
| ㄹ | `pattern:{type}` 사실 생성 | `key="pattern:<type>"`, `value="{n}회 (날짜 목록)"`, `confidence=1.0` 인 행이 생기고, 창 안 이벤트 n건 전부가 `fact_sources` 로 이어져 있다 |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

전부 `POSTGRES_PORT=5433 pytest <경로>::<테스트> -v` 로 실행하고 출력 파일을 `docs/wiki/packages/P6-memory/evidence/` 에 남긴다. 테스트 이름은 U 단위에서 확정하되 아래 뜻을 바꾸지 않는다.

| # | 확인할 것 | 케이스 | 기대 | 위치 |
|---|----------|-------|------|------|
| 1 | ㄷ·ㄹ 양성 | 한 인물 `conflict` 3건(창 안) | `pattern:conflict` 1행, `confidence=1.0`, value `"3회 (…3개 날짜…)"`, 링크 3 | test_memory_patterns |
| 2 | ㄷ 경계(부정) | 2건 | 패턴 행 없음 | 〃 |
| 3 | ㄷ 창 경계 | 기본 설정에서 3건 중 1건이 `now − 365일 − 1초` | 패턴 없음. 정확히 `now − 365일` 은 포함. 환경변수로 `PATTERN_WINDOW_DAYS=90`·`PATTERN_MIN_COUNT=2` 를 주면 같은 경계가 90일·2건으로 옮겨 가고 `memory_pattern` output 에 `window_days=90`·`min_count=2` 가 기록된다(기본 설정 케이스는 365·3) | 〃 |
| 4 | ㄷ 미래 제외 | 3건 중 1건 `occurred_at > now` | 패턴 없음 | 〃 |
| 5 | 인물 분리(부정) | 민수 2건 + 지훈 1건 같은 type | 둘 다 패턴 없음 | 〃 |
| 6 | type 분리(부정) | `meal` 2 + `meeting` 1 | 패턴 없음 | 〃 |
| 7 | 갱신 | 3건 → 4번째 추가 | 같은 행(id 불변) value `"4회 …"`, 링크 4 | 〃 |
| 8 | 미달 처리 | 시계를 옮겨 창 안 2건 | 결정 C-5 대로(권장: 행 삭제·링크 CASCADE·이벤트 4건 그대로) + trace 에 이전 value | 〃 |
| 9 | 규칙에 LLM 없음 | 패턴만 생기는 턴 | 추출기 호출 0회, `memory_pattern` trace `tokens_in=tokens_out=0` | test_memory_loop |
| 10 | ㄱ·ㄴ 양성 | 미승격 5건 + 가짜 추출기가 사실 2개 반환 | 사실 2행, 각자 링크 ≥ 1, 링크 이벤트 = 추출기가 준 id, `raw_utterance` 불변 | test_memory_promote |
| 11 | ㄱ 트리거 경계(부정) | 미승격 4건 | 추출기 호출 0회, 사실 0행 | 〃 |
| 12 | 재승격 방지 | 5건 승격 후 1건 추가(미승격 1) | 추출기 호출 0회(결정 B 판정이 앞 5건을 승격됨으로 본다) | 〃 |
| 13 | 원문 불변 | 승격·패턴 전후 | `events` 행 수·`raw_utterance`·`content` 동일(삭제·수정 0) | 〃·patterns |
| 14 | 추출기 거부 | 가짜가 `pattern:meal` 키 / 어휘 밖 키 / 입력에 없는 이벤트 id / 빈 값 반환 | 해당 사실만 거부·사유 trace, 나머지는 저장 | test_memory_extract·promote |
| 15 | 툴 키 보호 | `update_person(facts=[{"key":" Pattern:meal ", …}])` | `InvalidValue`, 행 0 | test_tools_persons |
| 16 | 실패 격리 | 가짜 추출기가 `timeout` 오류 | 턴 응답 200·이벤트 저장됨·`memory_error` trace·사실 0 | test_memory_loop |
| 17 | 재개 경로 | identity 되묻기 → 답 → 재개에서 이벤트 저장, 누적 3건 | 재개 응답 후 `pattern:*` 생성 | 〃 |
| 18 | API 한 흐름 | `TestClient` `POST /chat` 3회(가짜 제안기·판정기·추출기) | 세 번째 뒤 `pattern:{type}` + 링크 3 | 〃 |
| 19 | 금지 문자열·원문 불변 grep | "지킬 불변식" 절의 grep 3개를 **그 절에 적힌 명령 그대로** 실행(표 안에서는 파이프 기호가 칸을 나누므로 명령을 여기 다시 적지 않는다) | `app/agent/` 금지 리터럴은 기준선(`evidence/20260928-1350-verifier-fact-checks.txt` §6: `create_person(` 1건 = loop.py 기존 줄, 나머지 0건)과 같음 · `evaluation` 0건 · `Event` 삭제·수정 0건 | U8 evidence |
| 20 | 무변경 | `alembic check`, `python scripts/tools_check.py` | 차이 없음, 7/7 | U8 evidence |
| 21 | 전체 회귀 | `POSTGRES_PORT=5433 pytest -rs` | 실패 0·skip 0 | U8 evidence |

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 위치(registry 행) | 어떻게 |
|--------|------------------|-------|
| `PersonFact`·`FactSource`·`Event`·`EVENT_TYPES` | `app/db/models.py`(P1-schema `4dfaf33`) | 그대로. `fact_sources` 복합 PK·FK CASCADE 가 이미 있다 — 링크 중복은 PK 가 막는다 |
| `(person_id, key)` 애플리케이션 upsert 관례 | `app/tools/persons.py` `update_person`(결정 6) | 같은 조회 규칙(`updated_at desc` 첫 행)을 따른다. 단 승격·패턴은 fact id 가 필요해 ORM 으로 직접 쓴다(툴을 부르지 않는다 — 툴은 id 를 돌려주지 않고 확신도를 `DEFAULT_FACT_CONFIDENCE` 로 덮는다) |
| `DEFAULT_FACT_CONFIDENCE` | `app/settings.py` | 승격 사실의 확신도(결정 D-8 권장안) |
| 공급자 등록표·활성 스위치·오류 매핑 | `app/er/judge.py`(`select_provider`·`enabled_providers`·`call_with_error_mapping`·Gemini 매핑, D11) | import 만. `app/agent/propose.py`(P5-loop `069bdc2`)가 같은 방식의 선례 |
| `@traced(tool_name, step=…)`·`trace_tokens()` 규약·`ctx.last_trace_id` | `app/tools/context.py` | 새 step 3종을 이 데코레이터로 남긴다 |
| `user_timezone()` | `app/settings.py`(FIX-005) | value 의 날짜 표기만 사용자 시간대로(창 계산은 UTC 절대 시간) |
| 세이브포인트 규약 | `app/agent/loop.py`·`app/api/routes.py`(P5-loop U6·U7) | 승격 실패도 같은 `begin_nested()` 규약 |
| 테스트 픽스처·마커 | `tests/conftest.py`(픽스처 `db_session`·`fake_embedder`, 마커 `dbtest`, FIX-006 테스트 DB) | 그대로 |
| 소유 검사 `_owned_person(session, person_id, user_id)` | `app/tools/persons.py`(P2-tools, security §5) | `detect_patterns`·`promote_person` 첫 줄에서 import 해 재사용(U2·U5). 새 소유 검사 함수 금지 |

registry 를 `app/memory`·`test_memory`·`memory_` 로 grep 한 결과 0건 — 새 모듈은 중복이 아니다.

## 결정 항목 (사용자가 고른다 — 각 항목 권장안 표시)

> **사용자 확정(2026-09-28, AskUserQuestion)**: 결정 A~G 전부 **권장안**.
> A (ii) 루프 기록 단계 끝·같은 요청 안 / B (ii) `memory_promote` trace 의 "본 이벤트" id 로 미승격 판정(스키마 무변경 — 사용자가 (iii) CR 안을 검토한 뒤 (ii) 로 확정) / C-1 이벤트 저장 턴마다 그 인물 재계산 · C-2 `occurred_at` 기준 창(CR-002 로 기본 365일·3회 설정값 — D14)(UTC, 미래 제외, 표기만 사용자 시간대) · C-3 `"{n}회 (날짜 목록)"` · C-4 confidence 1.0 · C-5 (i) 3회 미만이면 패턴 행 삭제·이전 값은 trace 에 보존 / D-1~D-3·D-7 권장 확인 · D-4 이벤트 20·사실 8 · D-5 고정 어휘 9키 · D-6 같은 값이면 링크 추가, 다르면 덮어쓰고 링크를 이번 근거로 교체·이전 값 trace 보존 · D-8 기본값 1.0 / E P6-briefing 으로 미룸 / F 확인 / G (ii) 같은 턴·같은 인물 이벤트에 연결(U7 수행).

### 결정 A · 승격·패턴을 언제 돌리나

| 선택지 | 무엇 | 장점 | 단점 |
|-------|------|------|------|
| (i) `add_event` 안에서 동기 호출 | 툴이 저장 직후 승격 | 모든 호출자에 자동 | 툴에 LLM 호출이 들어간다 — registry 59행 "승격 트리거 없음" 과 S3.2 툴 책임을 깨고, 한 턴에 이벤트 3건이면 세 번 돈다 |
| **(ii) 루프 기록 단계 끝(`_record()` 뒤), 같은 요청·세이브포인트** | 턴마다 이벤트가 저장된 인물만 한 번씩 | P5 04-review 인계 자리 그대로, `run_turn`·`resume_turn` 한 자리로 덮임, 테스트 쉬움 | 트리거가 걸린 턴은 LLM 1회만큼 응답이 느려진다(5건마다 한 번) |
| (iii) 별도 엔드포인트·주기 작업 | 모아서 나중에 | 채팅 응답 지연 0 | 주기 작업 틀은 P6-briefing 몫이라 아직 없다. 패턴이 늦게 보인다 |
| (iv) 응답 후 `BackgroundTasks` | 응답 보낸 뒤 같은 프로세스에서 | 지연 0 | 별도 세션·트랜잭션이 필요하고 실패가 사용자에게 안 보인다, 테스트 복잡 |

**권장: (ii).** 예: 사용자가 다섯 번째로 민수 이야기를 한 그 턴의 응답이 LLM 한 번만큼(수 초) 늦어지고, 그 대신 곧바로 민수 카드에 사실이 생긴다.

### 결정 B · "미승격" 을 어떻게 표시하나 (스키마 v2 에 승격 여부 컬럼이 없다)

| 선택지 | 판정 방법 | 문제 |
|-------|----------|------|
| (i) `fact_sources` 에 연결 안 된 이벤트 | 링크 없으면 미승격 | LLM 이 사실을 하나도 뽑지 못한 이벤트(예: "민수랑 점심 먹음")는 **영원히 미승격**으로 남아 매 턴 다시 LLM 에 들어간다(비용·같은 결과 반복). 패턴 링크도 "승격됨" 으로 잘못 세지 않게 `pattern:` 사실 링크는 빼야 한다 |
| **(ii) `agent_traces` 의 `memory_promote` 행이 적은 `considered_event_ids` 에 없는 이벤트** | "승격기가 이미 본 이벤트" = 승격 기록에 id 가 있다 | 로그를 상태로 쓴다. 대신 그 기록이 원칙9 근거 기록 자체이고, 승격이 실패해 롤백되면 기록도 함께 사라져 다음에 자연스럽게 재시도된다. `output->>'person_id'` JSONB 조회(인덱스 없음 — 단일 사용자 규모에서 문제 없음, 리스크에 기록) |
| (iii) `events.promoted_at` 컬럼 추가 | 컬럼 NULL = 미승격 | 가장 명확하지만 **S3.1 스키마 v2 변경**이다 — CLAUDE.md 데이터 모델·S3.1 카드·마이그레이션이 바뀌므로 이 패키지 착수 전에 `/devlog change` CR(동결 → 영향 분석 → 이행)이 필요하다 |

**권장: (ii).** 스키마를 건드리지 않고, 사실이 안 나온 이벤트도 "봤음" 으로 처리돼 같은 이벤트를 두 번 LLM 에 보내지 않는다. (iii) 을 고르면 이 계획은 CR 이행 뒤로 밀린다.

### 결정 C · 패턴 감지 시점과 규칙 세부

- **C-1 시점** — (i) **이벤트가 저장된 턴마다, 그 인물에 대해**(순수 SQL, LLM 0) / (ii) 승격 때만. (ii) 는 "3회" 가 되어도 미승격 5건이 찰 때까지 패턴이 안 보여 수용 기준 ㄷ 의 뜻과 어긋난다. **권장 (i)**, 순서는 패턴 → 승격.
- **C-2 창 기준 시각**(창 길이는 CR-002·D14 로 설정값, 기본 365일) — (i) **`occurred_at`**(일이 일어난 때) / (ii) `created_at`(말한 때). 사용자가 "지난달에 싸웠어" 라고 오늘 말하면 (i) 은 지난달로 센다. **권장 (i)**. 창은 `[ctx.now() − PATTERN_WINDOW_DAYS일, ctx.now()]` 의 **UTC 절대 시간**(일수 × 24시간)이며 미래 `occurred_at` 은 뺀다. 시간대는 창 계산에 영향이 없고(절대 길이), value 의 날짜 표기만 `user_timezone()`(FIX-005, 기본 서울)로 한다 — 예: UTC `2026-09-19T16:00Z` 는 서울 날짜 `2026-09-20` 으로 적는다.
- **C-3 value 형식** — `"{n}회 (YYYY-MM-DD, YYYY-MM-DD, …)"`, 날짜 오름차순, 같은 날 두 건이면 두 번 적는다. 예: `"3회 (2026-07-02, 2026-08-11, 2026-09-20)"`. (D9 문구를 구체화한 것 — 선택지 없음, 확인만.)
- **C-4 confidence** — `1.0` 고정(D9→D14 불변). 선택지 없음.
- **C-5 기준 횟수 미만으로 떨어지면**(시간이 지나 창 밖으로 밀림) — (i) **패턴 사실 행 삭제**(링크는 FK CASCADE, 이벤트는 그대로), trace 에 이전 value 를 남긴다 / (ii) 그대로 둔다(브리핑에 "3회" 가 계속 뜬다 — 사실과 다름) / (iii) 남기되 value 를 "최근 {기간}일 {n}회 — 기준 미달" 로 바꾼다. **권장 (i)** — 패턴은 원문이 아니라 원문에서 **다시 계산할 수 있는 요약**이므로 지워도 "원문 삭제 금지" 에 걸리지 않고, 근거는 trace 에 남는다. 한계: 새 이벤트가 없으면 재계산이 안 돈다(시간만 흐른 경우) — P6-briefing 이 브리핑 직전에 같은 `detect_patterns()` 를 부르도록 인계한다.
- **C-6 재계산 범위** — 그 인물의 **모든 type**(7종)을 한 번에 다시 센다(이번에 저장된 type 만이 아니라). 비용은 쿼리 1개.

### 결정 D · LLM 사실 추출

- **D-1 공급자** — `app/er/judge.py` 등록표·`LLM_PROVIDER`·`LLM_PROVIDERS_ENABLED` 재사용(D11). 자체 표 금지. 모델명은 기존 환경변수를 그대로 쓴다. (선택지 없음, 확인만.)
- **D-2 구조화 출력 스키마** — `{facts: [{key: enum(FACT_KEYS), value: string, source_event_ids: [int, ≥1]}]}`. 사실마다 근거 이벤트 id 를 **LLM 이 직접 가리키게** 한다(링크를 코드가 추측하지 않는다). 코드는 그 id 가 입력 목록 안에 있는지만 검증한다.
- **D-3 테스트용 가짜** — `FakeFactExtractor(table)`: 입력 이벤트 id 집합 → 미리 정한 출력. 네트워크 0, 호출 횟수를 센다(판정 표 9·11·12행). 등록표 밖(D11 의 `FakeJudge` 와 같은 규약).
- **D-4 상한** — 한 번 승격에 이벤트 최대 `MEMORY_PROMOTE_MAX_EVENTS = 20`(오래된 순), 사실 최대 `MEMORY_MAX_FACTS = 8`. 넘는 사실은 거부·사유 trace. 값은 권장이며 사용자가 바꿀 수 있다.
- **D-5 사실 키 어휘** — (i) 자유 문자열 / (ii) **고정 집합** / (iii) 권장 어휘 + 자유 허용. 자유 키면 "취미" 와 "관심사" 가 따로 쌓여 upsert 가 의미를 잃는다. **권장 (ii)**, 초안: `job`(직업·직급), `workplace`(소속), `family`(가족 사항), `hobby`(취미·관심사), `likes`(좋아하는 것), `dislikes`(싫어하는 것·피할 것), `health`(건강·식이), `life_event`(이사·결혼·출산 같은 근황), `contact_note`(연락·만남 습관). 인물 간 관계 키는 두지 않는다(원칙7). 한계: P5 루프의 `update_person` 직접 사실은 여전히 자유 키다 — 이 패키지에서 바꾸지 않고 리스크에 남긴다.
- **D-6 기존 사실과 충돌 시 upsert 규칙** — 같은 `(person_id, key)` 가 있으면: 값이 같으면 **링크만 추가**, 값이 다르면 **값을 덮어쓰고 링크를 이번 근거로 교체**, 이전 값은 `memory_promote` trace 에 남긴다(원문 이벤트는 그대로이므로 옛 값의 근거는 언제든 다시 찾을 수 있다). 여러 값이 쌓여야 하는 키(`likes` 등)는 프롬프트에 기존 사실을 함께 넣어 LLM 이 **합친 값**을 내게 한다. 예: 기존 `likes="삼겹살"` + 새 이벤트 "민수가 등산 좋아한대" → LLM 출력 `likes="삼겹살, 등산"`, 링크는 이번 근거 이벤트로 교체(옛 근거는 trace 에). 대안: 링크를 교체하지 않고 누적 — 옛 근거가 새 값과 안 맞을 수 있다.
- **D-7 `pattern:` 접두 차단** — 세 겹: ① 스키마 enum 에 없다 ② 검증기가 거부 ③ `update_person` 이 거부(U3 — 루프 경로의 기존 구멍까지 막는다). 게이트(`app/agent/gate.py`)는 바꾸지 않는다 — 툴이 `InvalidValue` 를 던지면 루프가 이미 `loop_record.output.failed[]` 로 남긴다(P5 R-24 규약).
- **D-8 승격 사실의 confidence** — (i) **`DEFAULT_FACT_CONFIDENCE`(1.0)** — `update_person` 과 같은 뜻 / (ii) LLM 자기보고 0~1 저장 — 보정표가 없어 숫자가 정밀해 보이기만 한다(원칙3 은 ER 한정이지만 같은 우려). **권장 (i)**. 근거의 확실함은 숫자가 아니라 링크된 원문으로 보여 준다.

### 결정 E · 패턴 문장화(LLM)를 어디서 하나

(i) 이 패키지 / (ii) **P6-briefing**. 문장화는 브리핑 화면에 보이는 한 줄("민수와 최근 석 달 새 세 번 다퉜어요")이고 패턴 **판정**과 분리돼야 한다(원칙6). **권장 (ii)** — 이 패키지는 규칙 value 까지만 만든다.

### 결정 F · `agent_traces` 어휘

- `tool_name = "memory"`(P5 의 `"agent"`, ER 의 `"er"` 와 같은 층위).
- step 3종 — `memory_pattern`: 이벤트 저장 인물마다 1행. output `{person_id, window:{from,to}, window_days, min_count, counts:{type:n}, changes:[{type, action: created|updated|deleted|unchanged, fact_id, event_ids, previous_value}]}`, tokens 0. `window_days`·`min_count` 는 **이번 판정에 실제로 적용한** `pattern_config()` 값이다(D14 13행 "실제 쓴 기간·횟수를 패턴 trace 에 기록" — 설정을 바꾼 뒤에도 과거 판정을 재현할 수 있게, 원칙8·9). `memory_promote`: 트리거가 걸렸을 때만 1행. output `{person_id, unpromoted_count, considered_event_ids, facts:[{fact_id, key, action: created|updated|same, source_event_ids, previous_value}], rejected:[{index, key, reason}], llm:{provider, model}}`, tokens in/out = 추출기 사용량(`trace_tokens()`). `memory_error`: 승격·패턴 중 삼킨 예외 1행 `{person_id, stage, error}` — 프롬프트·키 원문 미기록(security §1). 세이브포인트 롤백 **뒤** 바깥 트랜잭션에서 쓴다(안에서 쓰면 롤백과 함께 사라진다 — U6).
- 트리거 미달(미승격 4건 이하)은 `memory_pattern` 행에 `unpromoted_count` 를 함께 적어 "왜 승격하지 않았나" 가 남게 한다.
- 권장안 그대로면 선택할 것은 없고, 어휘 이름만 확인하면 된다.

### 결정 G · P5 루프가 직접 쓴 사실(`update_person(facts)`)의 원문 링크

지금 루프는 LLM 제안으로 `update_person(facts)` 를 실행해 **근거 링크 없는 사실**을 만든다. R8 행은 "P6-memory 가 승격 시 채움" 이라 수용 기준은 승격 사실만 요구한다.
(i) 그대로 둔다 — 승격 사실만 링크, 루프 사실은 리스크로 기록 / (ii) **같은 턴·같은 인물의 이벤트에 잇는다**(U7) — 이벤트 없는 턴은 연결 없음으로 trace / (iii) 루프에서 `facts` 제안을 막고 사실은 승격으로만 만든다 — P5 게이트·테스트 변경, 범위가 커진다.
**권장 (ii)** — 비용이 작고 인물 카드(P8)에서 "링크 없는 사실" 이 크게 준다. 예: "민수 요즘 필라테스 다닌대" 한 턴이 `personal_share` 이벤트 + `hobby=필라테스` 사실을 함께 만들면 그 사실이 그 발화에 이어진다. 범위를 최소로 하려면 (i).

## 지킬 불변식 (수용 기준 밖)

- **원문(`events`) 삭제·수정 금지.** 권위 있는 판정은 판정 표 13행 테스트(승격·패턴 전후 `events` 행 수·`raw_utterance`·`content` 동일)다. 보조 grep 은 **`Event` 대상만** 본다: `grep -rnE "delete\(Event|update\(Event|\.raw_utterance\s*=[^=]|\.content\s*=[^=]" app/memory/` → 0건(`[^=]` 는 비교 `==` 를 빼기 위함). 파생 요약인 `PersonFact`(C-5(i) 패턴 행 삭제)·`FactSource`(D-6 링크 교체, U2 빠진 링크 제거)의 삭제는 이 불변식의 대상이 아니며 허용된다 — `PersonFact`·`FactSource` 에는 `content`·`raw_utterance` 열이 없어 위 grep 에 걸리지 않는다. 구현은 `Event` 를 `session.delete()` 에 넘기지 않는다(테스트 13행이 잡는다).
- `app/memory/patterns.py` 는 `app.memory.extract`·`app.er.judge`·`app.embedding` 을 import 하지 않는다(규칙에 LLM 없음 — 원칙6, 테스트가 모듈 import 목록 단언).
- `app/agent/` 에 확신도·인물 생성 리터럴을 새로 쓰지 않는다 — 확신도 값을 다루는 코드는 전부 `app/memory/` 에 둔다. 명령(U8·판정 19행이 이 표기 그대로 실행): `grep -rnE "T_merge|T_new|confidence|create_person\(" app/agent/` → 기준선(fact-checks §6: `create_person(` 1건 = loop.py 기존 줄, 나머지 0건)과 같음.
- `app/memory/` docstring·주석에 "evaluation" 금지. 명령: `grep -rn "evaluation" app/memory/` → 0건.

## 리스크 · 미결

- **추출 품질은 측정되지 않는다.** 이 패키지의 테스트는 가짜 추출기로 배선만 확인한다. 실제 LLM 이 엉뚱한 사실을 뽑아도(예: 농담을 사실로) 막을 지표가 없다 — P10-final-eval 로 인계하고, 검증 가능성은 링크된 원문으로만 보장한다. 실 공급자 왕복 1회(`POST /chat` 5회로 승격 유도)는 U8 에서 사용자 실행 권고로 남긴다(P5 판정 표 8행과 같은 방식).
- **결정 B(ii) 의 "로그를 상태로 쓰기"** — `agent_traces` 를 정리·보관 정책으로 지우면 이미 본 이벤트가 다시 미승격이 된다(중복 사실은 upsert 로 흡수되나 LLM 비용 발생). 현재 trace 삭제 정책은 없다. `output->>'person_id'` 에 인덱스가 없어 trace 가 수십만 행이 되면 느려질 수 있다 — 단일 사용자 데모 규모에서는 문제 없음. 커지면 (iii) CR 로 옮긴다.
- **결정 B(iii) 을 고르면** S3.1·CLAUDE.md 데이터 모델 변경 → `/devlog change` CR 선행, 이 계획의 U5 판정·결정 B 절 개정 필요.
- **승격 실패가 반복되면**(공급자 장애) 그 인물의 턴마다 LLM 호출이 재시도된다. 1차는 `memory_error` 로 보이게만 하고 백오프는 넣지 않는다(과설계 회피). 필요하면 FIX 로.
- **동시 요청**: `person_facts(person_id, key)` 에 유일 제약이 없어(S3.1) 두 요청이 동시에 같은 패턴을 만들면 두 행이 생길 수 있다. 단일 사용자·순차 채팅 전제에서 수용하고, 조회는 `update_person` 과 같은 "`updated_at desc` 첫 행" 규칙을 따른다. 유일 제약 추가는 스키마 변경이라 이 패키지 밖.
- **시간만 흐른 경우 패턴이 낡는다**(결정 C-5 한계) — 새 이벤트가 없으면 재계산이 안 돈다. P6-briefing 이 브리핑 직전 `detect_patterns()` 호출(인계).
- **키 어휘 불일치**(결정 D-5) — 승격은 고정 어휘, P5 루프 직접 사실은 자유 키. 같은 뜻의 사실이 두 키로 갈릴 수 있다. 루프 제안 스키마에 같은 enum 을 거는 것은 P5 행동 변경이라 이 패키지에서 하지 않고 후속 후보로 남긴다.
- **`loop_record` output 모양** — U6 은 이벤트가 실행된 인물 id 를 얻기 위해 `RecordOutcome` 에 `event_person_ids` 필드를(U7 은 `fact_keys_by_person` 을) 더한다. `RecordOutcome.to_dict()` 는 `executed`/`failed` 두 키만 내므로 `loop_record.output` 의 **기존 키는 바뀌지 않으며**, output 에 키를 추가해야 하면 U6 03-log 에 적는다(P5 U1 스키마 규약).
- **응답 지연**(결정 A(ii)) — 트리거 턴은 LLM 1회만큼 느리다. 추출기 타임아웃은 기존 `ER_JUDGE_TIMEOUT` 과 같은 값을 쓰되 별도 상수로 둘지는 U4 에서 정해 03-log 에 남긴다.
- **미결(사용자 결정 필요)**: 없음 — 결정 A~G 전부 권장안으로 사용자 확정(2026-09-28, 결정 항목 절 머리 인용).

## 후행 패키지가 이 패키지에서 기대하는 것

- **P6-briefing**: `person_facts` 에 `pattern:*` 와 승격 사실이 근거 링크와 함께 있다. 패턴 문장화(LLM, 결정 E)와 브리핑 직전 `detect_patterns()` 재호출은 P6-briefing 몫.
- **P8-frontend**: 인물 카드의 "원문 펼치기" 는 `fact_sources → events.raw_utterance` 로 조회한다. 조회 API 는 이 패키지가 만들지 않는다.
- **P10-final-eval**: 사실 추출 품질 측정 대상(`memory_promote` trace 의 입력·출력·근거 id).

## 읽은 카드

- `docs/wiki/templates/plan.md` 전문(형식)
- `docs/wiki/decisions/D09-pattern-rule.md` 전문(CR-002 로 대체됨), `docs/wiki/decisions/D14-pattern-window-config.md` 전문(메인 세션이 CR-002 이행 때 반영), `docs/wiki/decisions/D11-llm-provider-registry.md` 전문
- `docs/wiki/specs/S3.5-memory-promotion.md` 전문, `docs/wiki/specs/S3.1-schema-v2.md`(person_facts·fact_sources·events·type 제약 줄만 grep), `docs/wiki/specs/S3.2-tools-v2.md`(update_person 행만 grep)
- `docs/resolution-plan.md` §3.5(187~192행)
- `docs/wiki/review-index.md` R8·R11 행, `docs/wiki/INDEX.md` 전문(패키지 표·태그 어휘), `docs/wiki/CURRENT.md` 전문, `docs/backlog.md` P6 절
- `docs/wiki/registry.md` grep(`app/db/models.py`·`app/tools/persons.py`·`app/tools/records.py`·`app/settings.py`·`app/er/judge.py`·`app/agent/*`·`tests/conftest.py`·`app/memory` 0건)
- `docs/wiki/packages/P5-loop/01-plan.md` 1~60행(형식·결정 쓰는 법), `docs/wiki/packages/P5-loop/04-review.md` P6 인계 줄(190행)
- 코드 읽기(쓰지 않음): `app/tools/persons.py` 466~559행(`update_person`), `app/db/models.py` 134~191행, `app/agent/loop.py` 760~1000행(`_execute_call`·`_record_impl`·`_record`·`run_turn`), `app/agent/gate.py` 225~241행, `app/agent/propose.py` 120~158행, `app/tools/context.py` 100~219행(`to_jsonable`·`traced`), `app/er/judge.py` 정의 목록
- `.claude/gitlog.md`(2026-09-28 13:14 스냅샷, 1차 개정 때 13:40 스냅샷), `.claude/scripts/verify-plan.sh`(형식 요건 확인)
- 1차 개정 때 추가로 읽음: `02-plan-verify.md` §3(H-1~H-3·R-1~R-9), `05-remediation.md`, `docs/wiki/registry.md` `.env.example` 행(38행, 소유 = 하네스), `app/tools/persons.py` 371~383행(`_owned_person`), `app/agent/loop.py` 830~874행(`_record_impl` 실행·`RecordOutcome` 반환)
- D06 은 열지 않았다 — 이 패키지는 `display_name` 을 다루지 않는다(태그는 `update_person` 이 D6 규칙을 가진 툴이라는 참조로만 둔다).
