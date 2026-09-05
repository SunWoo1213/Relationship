# P2-tools · 완료 검토 (04-review)

날짜: 2026-09-05 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트(L-002). 코드·계획·카드는 고치지 않았다. 이 문서·05-remediation(원인 분석·확인 결과·상태 판정)·evidence/ 만 썼다.

검토 대상: 01-plan(개정 1, U1~U9 전부 [x]) · 02-plan-verify(§3 권고 9건) · 03-log 10 항목(착수 7b793ba, U1 f217190, U2 4eca3e9, U3 a9cb254, U4 f318d58, U5 9cb35b6, U6 8162e09, U7 7c94aad, U8 4d5817e, U9 f2e9e05) · 05-remediation 16 소견 · evidence 1535~1921 · 구현 산출물 전부(`app/db/session.py` `app/settings.py` `app/embedding.py` `app/tools/*` `app/api/*` `app/main.py` `scripts/tools_check.py` `tests/*` `requirements.txt` `.env.example` `README.md` `registry.md` `specs/S3.1`). 읽은 카드: INDEX 태그 표 → review-index R6 R7 R10 R18 행 → D01 D02 D06(코드에서 지켜야 할 것) D04 D05 D09 → S3.1 S3.2 S3.4 S3.6 → security.md §1 §5 → CLAUDE.md 툴 7종 표(60~66행)·불변 원칙 1·2·4·6·7·9 → backlog P2 행(27행).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P2-tools > docs/wiki/packages/P2-tools/evidence/<ts>-verify-impl.txt 2>&1` (로컬 컨테이너가 5433 이라 포트를 셸 변수로 넘겼다. 사전 실행 evidence/20260905-1936-verify-impl.txt 는 04-review 부재 WARN 1 → F-14f3ef; 아래는 04-review 작성 후 최종 실행 evidence/20260905-1948-verify-impl.txt)
```
== verify-impl P2-tools  (20260905-1948) ==
........................................................................ [ 69%]
..............................................................           [100%]
206 passed in 3.13s
PASS  pytest 통과 → evidence/20260905-1948-pytest.txt
PASS  compileall 통과 → evidence/20260905-1948-lint.txt
PASS  태그 P2-tools 커밋 11 건 → evidence/20260905-1948-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: D6
PASS  커밋에 태그 존재: R10
PASS  커밋에 태그 존재: R18
PASS  커밋에 태그 존재: R6
PASS  커밋에 태그 존재: R7
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.6
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  시그니처가 CLAUDE.md와 일치  ← evidence/20260905-1936-review-tools-chec
PASS  증거 확인:  `ask_user`가 `pending_questions`에 저장  ← evidence/20260905-1937-review-ask-user-r
PASS  registry 에 P2-tools 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260905-1948-summary.txt ==
exit=0
```
참고 — `verify-impl.sh` 자체는 `POSTGRES_PORT` 를 붙이지 않고 `python -m pytest -q` 를 부른다(`-rs` 도 없다). 이 저장소의 `app/config.py` 기본 포트는 5432 이므로 셸 변수 없이 돌리면 dbtest 가 조용히 skip 될 수 있다(01-plan 리스크 "실 DB 테스트가 조용히 skip 된다"). 그래서 §3 에 5599 포트 실행(skip 사유가 보이는지)과 5433 `-rs` 실행(skip 0)을 별도 증거로 둔다.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시, 존재하는 경로만. 기준 문장은 `docs/backlog.md` 27행 그대로.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 시그니처가 CLAUDE.md와 일치 | evidence/20260905-1936-review-tools-check.txt (구현자 파서 재실행 `RESULT: 7/7 ok` exit=0), evidence/20260905-1937-review-signatures-independent.txt (verifier 자체 스크립트 — `tools_check` 를 import 하지 않고 CLAUDE.md 60~66행 원문과 `inspect.signature` 7개를 직접 대조, `MISMATCH=0`), evidence/20260905-1908-pytest-signatures.txt (15 passed), scripts/tools_check.py, tests/test_tool_signatures.py, f2e9e05 | 통과 |
| `ask_user`가 `pending_questions`에 저장 | evidence/20260905-1937-review-ask-user-row.txt (verifier 독립 실행: `session_scope()` 안에서 `ask_user(kind=new_person)` 1회 → 같은 스코프 `SELECT id, session_id, kind, question, options, context, answered_at FROM pending_questions WHERE id=1092` 1행·`answered_at=None`·`agent_traces` tool_call 1행 → 의도적 rollback → 새 세션에서 0행), evidence/20260905-1908-pytest-questions.txt (35 passed skip 0), evidence/20260905-1939-review-pytest-api-wrongport.txt (HTTP 경로: DB 없으면 skip 사유 노출), app/tools/questions.py, 8162e09 | 통과 |

**`ctx` 첫 인자 편차에 대한 최종 판단 — 수용 기준 훼손 아님(02-plan-verify 와 같은 결론, 조건 하나 추가).** 근거: (1) CLAUDE.md 표는 "제품 속 에이전트(LLM)가 호출하는" 언어 중립 의사 시그니처이고, `ctx`(세션·session_id·user_id·embedder·now·confirmed_question_id)는 LLM 이 채우는 값이 아니라 런타임 실행 맥락이다 — 7개 모두 같은 자리에 같은 이름으로 붙고 그 뒤는 이름·순서·옵션 여부가 글자 그대로 같다(위 evidence 두 파일에서 직접 확인). (2) 01-plan 결정 2 가 이 편차를 유일하게 허용하고 `tools_check` 가 "첫 매개변수가 정확히 `ctx`" 를 기계로 강제한다(`test_tool_signatures.py` (d) 케이스가 `ctx` 아닌 첫 인자를 FAIL 로 잡는다). (3) 반환형 이름(`Person` ↔ `PersonOut`)은 F-107a50 원인 분석대로 판정 대상이 아니다. **조건**: P5-loop 이 LLM 에 노출하는 툴 스키마(JSON schema)는 `ctx` 를 제외한 매개변수만 담아야 하며, 그 스키마 생성기가 `inspect.signature` 에서 첫 매개변수를 떼는 방식이면 `tools_check` 와 같은 출처가 된다 — §7 에 인계.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 verifier 가 이 세션에서 직접 실행했다. 변이는 원본을 scratchpad 에 복사해 두고 sed/치환으로 적용 → 해당 테스트 실행 → 원본 복사본으로 복원 → `git diff --stat` 빈 값 확인 → 전체 206 passed 재확인 순서(`git checkout --` 는 safety-guard 가 막으므로 복사본 복원).

| 케이스 | 명령 | 증거 |
|--------|------|------|
| (a) D1 강제 우회 — `_require_confirmation` 의 `answered_at` 검사 제거 | `sed -i '298s/.../if False and .../' app/tools/persons.py; POSTGRES_PORT=5433 python -m pytest tests/test_tools_persons.py -q -rs -k unanswered_question` | evidence/20260905-1938-review-mutations.txt — `Failed: DID NOT RAISE ConfirmationRequired` 1 failed → 복원 후 `git diff --stat` 빈 값 |
| (b) 원칙1 — `search_person` 이 `hints.hierarchy` 로 후보를 배제하도록 변이 | `-k hints_do_not_exclude` | 같은 파일 — `assert 0 == 1` 1 failed → 복원 |
| (c) 결정 12 — `answer_question` 이 already_answered 를 통과시키도록 변이 | `POSTGRES_PORT=5433 python -m pytest tests/test_api.py -q -rs -k already_answered` | 같은 파일 — `assert 200 == 409` 1 failed → 복원 |
| (d) 미결 3 — `records.py` `_require_aware` naive 검사 무력화 | `-k naive` (tests/test_tools_records.py) | 같은 파일 — `DID NOT RAISE InvalidValue` 2 failed(add_event·add_schedule) → 복원. 복원 뒤 `git status --short -- app tests scripts` 빈 값, 전체 `206 passed` |
| 원칙2·3·4 — 임계치·확신도 계산이 `app/` 에 없다 | `grep -rnE 'T_merge\|T_new\|confidence\s*=\|0\.5\s*\*\|s_llm\|s_emb' app/` (`DEFAULT_FACT_CONFIDENCE` 제외) | evidence/20260905-1939-review-grep-principles.txt — 코드 줄 0건(모듈 docstring 의 "하지 않는다" 문장 3건만) |
| 원칙6 — `pattern:` 생성 없음 | `grep -rnE 'pattern:' app/` | 같은 파일 — docstring 1건("패턴 감지 없음") 외 0 |
| 원칙7 — 브리핑 반환에 문장형 키 없음 | `BriefingOut.to_dict().keys()` 실행 + `grep summary\|suggestion\|advice\|제안` | 같은 파일 — 키 집합 `['aliases','facts','generated_at','person','recent_events','schedule','upcoming_schedules']`, 코드 줄 0건; 회귀 `test_get_briefing_to_dict_key_set_has_no_sentence_fields` |
| LLM·임베딩 공급자 미도입 | `grep -rnE '^(import\|from) (openai\|anthropic)' app/; grep openai\|anthropic requirements.txt` | 같은 파일 — 0건 / requirements 에 없음 |
| D2 — 동기 대기 없음 | `grep -rnE 'time\.sleep\|sleep(\|asyncio\.sleep\|while True' app/` | 같은 파일 — 코드 줄 0건; 회귀 `test_ask_user_never_calls_time_sleep`(monkeypatch 로 sleep 을 폭탄으로) |
| D6 — 별칭 삭제 없음 | `grep -rnE 'session\.delete\|\.delete(\|DELETE FROM' app/` | 같은 파일 — 0건 |
| P5 경계 — 채팅·루프 라우트 없음 | `grep -rnE '@router\.(get\|post\|...)' app/` | 같은 파일 — `GET /health`, `POST /answers/{question_id}` 2개뿐 |
| 원칙9 — trace 부착 범위 | `grep -rnE '@traced("' app/` | 같은 파일 — 8건 = 툴 7종 + `answer_question`. `/health`·`list_pending` 은 미부착(01-plan 25행 규약 "7개 툴 + answer_question", 03-log U6 에 `list_pending` 제외 이유 기록) |
| 잘못된 포트에서 조용히 통과하지 않는다 | `POSTGRES_PORT=5599 python -m pytest tests/test_api.py -q -rs` | evidence/20260905-1939-review-pytest-api-wrongport.txt — `2 passed, 8 skipped`, 8건 모두 사유 "local PostgreSQL not reachable — set POSTGRES_PORT=5433 (... port: 5599 ...)", 비밀번호·접속 URL 0회 |
| 실 DB 전체 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | evidence/20260905-1939-review-pytest-all.txt — `206 passed`, skip 0 |
| 스키마 무변경 | `POSTGRES_PORT=5433 python -m alembic check; alembic current; git log 5dc95bb..HEAD -- alembic/versions alembic/env.py docker/ alembic.ini` | evidence/20260905-1939-review-alembic-check.txt — "No new upgrade operations detected." exit 0, `0001 (head)`, P1 종료 후 마이그레이션·compose 커밋 0건 |
| FastAPI 실기동·종료 | `POSTGRES_PORT=5433 python -m uvicorn app.main:app --port 8791` → curl → kill → `netstat` | evidence/20260905-1940-review-uvicorn-health.txt — `/health` 200 `{"status":"ok","db":"up","alembic_revision":"0001"}`(`alembic current` 와 같음), `POST /answers/999999999` → 404 `{"detail":{"code":"not_found"}}`, 본문 필드 누락 → 422(FastAPI 기본), 종료 후 8791·8792 LISTENING 0, 서버 로그·응답에 비밀 0회. (첫 시도의 400 은 Git Bash 가 '예' 를 비-UTF-8 코드페이지로 보낸 클라이언트 측 문제 — 파일 본문으로 재시도해 404 확인) |
| tool_error 경로가 DB 유래 예외를 어떻게 다루는가(추가 탐침) | 롤백 세션 + 1535차원 가짜 embedder 로 `create_person` | evidence/20260905-1942-review-tool-error-probe.txt — 호출자에게 `PendingRollbackError` 가 올라오고 원래 `DataError('expected 1536 dimensions, not 1535')` 는 `__context__` 에만 남으며 tool_error 행도 없다 → **F-ca12ad**(§6) |
| 정적 | 핀·exit 줄·registry·비밀 패턴 | evidence/20260905-1941-review-static.txt — `fastapi==0.135.1 / starlette==0.52.1 / uvicorn==0.41.0 / httpx==0.28.1 / pydantic==2.12.5` = `pip freeze`; evidence 43개 파일의 `exit=` 줄이 기대값(변이 파일만 1, 나머지 0); registry P2-tools 26행(모듈 10·엔드포인트 5·스크립트 1·테스트 10) 중 경로 행 26개의 커밋 열이 `git log -- <path>` 의 첫/마지막 커밋과 일치(24개) 또는 `pending`(2개 → F-5d554d); 공유 파일 7개(README·db_check·requirements·models·config·conftest·test_config) 행 수 각 1; 저장소 키 패턴(`sk-…`/`AKIA…`/PEM/`ghp_`) 0; `alembic.ini` `sqlalchemy.url =` 공란; `.env.example` P2 추가분은 `APP_USER_ID=local` 이름+예시뿐(`POSTGRES_PASSWORD=pass` 자리표시자는 P0-compose 시점부터 있던 줄, 이번 diff 아님) |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
review-index 갱신은 메인 세션이 한다(verifier 는 카드를 고치지 않는다). 제안 해시:
- **R10** 툴 시그니처 ↔ 스키마 불일치 → 구현완료(**f2e9e05** — `scripts/tools_check.py`·`tests/test_tool_signatures.py`; 함수 본체는 a9cb254 f318d58 9cb35b6 8162e09 7c94aad)
- **R6** 신규 인물 자동등록 vs 확인형 → 구현완료(**f318d58** — `create_person` 의 `_require_confirmation`(answered `new_person` + 긍정 답 규약) / U6 8162e09 의 왕복 테스트 `test_d1_roundtrip_*`). P5-loop 이 "루프가 확인 없이 create 를 부르지 않는다" 를 마저 닫는다(review-index 행의 "P2-tools, P5-loop" 그대로).
- **R7** ask_user 동기 반환 불가 → 구현완료(**8162e09** — `pending_questions` 저장 후 `{question_id, status:"pending"}` 반환, 24h 만료 파생 / HTTP 앞 절반 4d5817e). 재개(턴 N+1 뒤 절반)는 P5-loop.
- **R18** 승진 후 display_name 정책 → 구현완료(**f318d58** — `update_person(display_name=…)` 은 answered identity/new_person 질문 필요, 새 이름 `system` 별칭 누적, 이전 별칭 유지·삭제 경로 없음)

## 5. registry.md 에 올린 산출물
- P2-tools 행 26개(`grep -c '| P2-tools |'` = 26): 모듈 10(`app/db/session.py` `app/settings.py` `app/embedding.py` `app/tools/{__init__,types,context,persons,records,questions,briefing}.py`), 엔드포인트 5(`app/main.py` `app/api/{__init__,deps,routes,schemas}.py`), 스크립트 1(`scripts/tools_check.py`), 테스트 10(`tests/test_{settings,db_session,tools_types,tools_context,tools_persons,tools_records,tools_questions,tools_briefing,api,tool_signatures}.py`).
- 기존 행 비고만 갱신(새 행 없음, 각 1행 유지 확인): `app/config.py`(repr=False) `app/db/models.py`(ALIAS_SOURCES) `requirements.txt`(fastapi·uvicorn·httpx 3줄) `tests/conftest.py`(픽스처) `tests/test_config.py`(repr 검사) `README.md`(P2 행·실행 절) `scripts/embed_pilot.py`(비고 "P3-er 에서 이동").
- 커밋 열 `pending` 2행(63·73행) → F-5d554d, 닫는 커밋에서 f2e9e05 로.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
05-remediation 최종(`findings.py … 20260905-1948-verify-impl.txt --source verify-impl` 동기화 후): **해소 16 / 열림 3(필수 0)**. 열림 3 = F-4d2507(architect 인계), F-ca12ad(신규, P3-er 인계), F-5d554d(신규, 닫는 커밋에서 메인 세션). F-14f3ef(04-review 부재)는 §1 재실행 WARN 0 으로 해소. 열린 것은 모두 [권고]이며 P2 수용 기준을 막지 않는다. verify-plan 출처 registry 소견 6건(F-673d47 F-ca32f5 F-127d01 F-320519 F-0ffff5 F-2c37bd)은 evidence/20260905-1941-review-static.txt(공유 파일 행 수 각 1)로 verifier 가 해소 판정했고, review 출처 7건(F-08b3db F-b97a06 F-4d8d96 F-3c8d4a F-0010e6 F-2418ef F-107a50)은 03-log 권고 처리 표의 각 evidence·코드를 재확인한 뒤 evidence/20260905-1944-verifier-impl-review.txt 동기화로 해소했다(F-fbaaae 는 U6 에서 이미 해소, `grep 'user_id 격리 부재' app/tools/questions.py` 57행 확인).

- **F-4d2507 [권고, 열림 → architect 인계]** security.md §5 "인물 단위 완전 삭제 API(`DELETE /persons/{id}`)" 를 받을 backlog 항목이 여전히 없다(`grep -nE 'DELETE|delete_person|완전 삭제' docs/backlog.md` 0건). P2 제외는 사용자 결정(01-plan 미결 8)이므로 P2 완료를 막지 않지만, `pending_questions.context`·`agent_traces.input/output` JSONB 안의 `person_id` 참조 정리 요건(P1 04-review §7)을 함께 실을 항목을 architect 가 P5-loop 묶음 또는 별도로 세워야 한다.
- **F-ca12ad [권고, 신규 → P3-er 첫 단위 또는 FIX]** `@traced` except 경로가 실패한 flush 뒤 같은 세션에 tool_error 행을 add+flush 하므로 `PendingRollbackError` 가 원래 예외를 대체하고 tool_error 행도 남지 않는다(evidence/20260905-1942-review-tool-error-probe.txt). P2 의 자체 예외는 전부 flush 전 검증 오류라 수용 기준·206 테스트에는 영향이 없지만, P3-er 가 실제 임베딩 공급자를 꽂으면(차원 불일치·NULL·CHECK) 도달한다. 조치 후보는 05 원인 분석에 적었다(`begin_nested()` 세이브포인트 안에서 기록 시도 후 원래 예외를 그대로 올리기, 또는 F-4d8d96 의 별도 커넥션 결정과 묶어 P5). `app/embedding.EmbeddingProvider` 에 D4 가 요구한 `dimension` 이 없어(`embed()` 만 요구) 차원 불일치를 호출 전에 잡을 자리가 없다는 점도 같은 축이다.
- **F-5d554d [권고, 신규 → 닫는 커밋]** registry 63·73행 커밋 열 `pending`(→ f2e9e05), 03-log 10개 제목 `· pending`(→ 7b793ba f217190 4eca3e9 a9cb254 f318d58 9cb35b6 8162e09 7c94aad 4d5817e f2e9e05). P0-compose 7d20a34 와 같은 처리. README 진행 표 P2 행 "구현 완료 · 검증 대기" 도 같은 커밋에서 "완료(04-review)" 로.
- **관찰(소견 아님, 기록만)**:
  - O1 `TRACE_MAX_STRING` 이 01-plan(`app/settings.py`, 4000)과 달리 `app/tools/context.py` 에 2000 으로 있다. 03-log U2 는 값을 적었지만 "계획과 다르게 한 것" 으로 표시하지 않았다. 기능 영향 없음. 설정값 단일 출처 원칙상 P3 에서 `settings.py` 로 옮기는 편이 정합.
  - O2 `GET /health` 응답 키가 01-plan 35행의 `alembic` 이 아니라 `alembic_revision` 이다(README·테스트·evidence 는 구현과 일치). 03-log U8 "계획과 다르게 한 것" 에 없음. P5·P9 헬스체크가 이 이름을 쓰면 된다.
  - O3 03-log U2·U3·U7 의 Refs 에 있는 `원칙9`/`원칙1 원칙2 원칙4`/`원칙7` 태그는 해당 커밋 메시지 Refs 에 없다(verify-impl 은 D/S/R/FIX/CR 만 검사해 통과). `git log --grep 원칙7` 로 추적할 수 없다는 뜻이며, 태그 어휘(INDEX)가 원칙 태그를 커밋 Refs 에 허용하므로 다음 패키지부터 /commit 초안이 03-log 와 같은 Refs 를 쓰게 하면 된다.
  - O4 `verify-impl.sh` 가 `POSTGRES_PORT`·`-rs` 없이 pytest 를 부른다(§1 참고). 하네스 개선 후보(L 카드 또는 스크립트에 `"$@"` 로 `-rs` 기본 추가) — 이 패키지 판정에는 §3 의 5599/5433 두 실행으로 보완했다.
  - O5 `ask_user` 의 `context` 비밀 방어는 최상위 키 이름만 본다(값·중첩 키는 보지 않는다, docstring 에 명시). S3.4 "비밀 저장 금지" 의 실제 보증은 context 를 채우는 P3-er·P5-loop 의 몫이다.

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- **P3-er (임베딩·ER 2~4단계)**
  - `search_person(ctx, query, hints=None) -> list[Candidate]` — `Candidate{person: PersonOut, similarity(인물별 max, 0~1, embedding_skipped 면 0.0), aliases_matched, rule_flags{exact_alias, partial_alias, hierarchy_match, relation_tag_match, hierarchy_adjacent, embedding_skipped}}`. **배제하지 않는다** — 규칙 필터·`s_rule`·`s_emb`·`s_llm`·`T_merge`/`T_new`·`confidence_breakdown` trace 는 전부 P3 몫. `hierarchy_adjacent` 는 상↔동, 동↔하 만 True.
  - 임베딩 공급자: `app/embedding.py` 의 `EmbeddingProvider`(Protocol, `embed(texts)` 만) + `as_provider()`; `OpenAIEmbeddingProvider` 를 `scripts/embed_pilot.py` 에서 `app/` 으로 옮겨 `ctx.embedder` 에 꽂는다. `EMBEDDING_DIM=1536`. **F-ca12ad** 를 첫 단위에서 처리(`@traced` 예외 경로) — 공급자를 꽂는 순간 차원 불일치가 tool_error 를 가리는 경로가 열린다. `dimension` 속성/검증 추가 권장(D4). P2 구간에 embedder 없이 만들어진 `embedding IS NULL` 별칭 백필(01-plan 결정 4 "남는 일").
  - 벡터 인덱스(HNSW/IVFFlat) revision 을 만들 때 `person_aliases.source` CHECK(`ALIAS_SOURCES`, 결정 5) 도 같이 얹을지 결정. `agent_traces.tool_name` NOT NULL 에 툴 아닌 단계(규칙 필터·LLM 판정)를 어떻게 넣을지(01-plan 미결 1).
  - `ask_user(kind=identity|new_person)` 은 `context["affirmative_options"]`(= `app.tools.types.AFFIRMATIVE_KEY`, `options` 의 부분집합) 없이는 `InvalidValue` 다. `create_person`/`update_person(display_name=…)` 은 `ctx.confirmed_question_id` 가 answered·같은 `session_id`·해당 kind·답 ∈ affirmative_options 일 때만 통과한다.
- **P5-loop (루프·채팅·재개)**
  - `ToolContext(session, session_id, user_id=app_user_id(), embedder=None, now=utcnow, confirmed_question_id=None)` 생성 지점을 **한 곳**으로(01-plan 리스크 "D1 강제의 구멍"). 지금 `build_ctx()`(`app/api/deps.py`)는 답할 `pending_questions` 행의 `session_id` 를 쓴다(결정 12). `X-Session-Id` 헤더 규약은 채팅 엔드포인트가 정한다.
  - **확인 질문은 특정 인물·이름에 묶여 있지 않고 소비되지도 않는다**: 같은 세션의 answered `new_person` 질문 하나로 `create_person` 을 여러 번(다른 이름으로) 부를 수 있고, answered `new_person` 질문이 `update_person(display_name=…)` 도 통과시킨다(kinds=("identity","new_person")). P2 는 "answered 질문을 거쳤는가"까지만 보증한다 — 루프가 질문 context 에 대상(후보 id·display_name)을 넣고 재개 시 그 대상에만 쓰도록 하는 것, 또는 1회 소비 규약은 P5 가 정한다.
  - `POST /answers/{question_id}` 는 답 저장까지(200 `{question_id, status:"answered"}` / 404 / 409 `{code: already_answered|expired, question_id}` / 422). 저장된 `context` 로 루프를 재개하는 뒤 절반을 이 라우트에 잇는다. `list_pending(ctx, session_id=None)`(trace 없음)이 있으니 칩 조회 라우트는 이것을 감싼다. `expired`(24h, `settings.QUESTION_TTL`)는 `answered_at` NULL 유지.
  - `pending_questions`·`agent_traces` 에 `user_id` 격리가 없다(F-fbaaae, 해소=명문화) — 세션→사용자 귀속 계층이 필요.
  - tool_error trace 는 호출자 rollback 과 함께 사라진다(F-4d8d96, 문서화로 닫음) + F-ca12ad — 별도 커넥션 기록 여부를 P5 01-plan 에서 결정.
  - `get_session()` 은 정상 종료 시 commit, 예외 시 rollback. 툴은 flush 까지만. 도메인 예외 → HTTP 매핑은 `app/main.py` 한 곳(404/409/422/400/500, `/health` 만 503).
  - LLM 노출용 툴 스키마는 `inspect.signature` 에서 `ctx` 를 뗀 나머지만(§2 조건). `TOOL_NAMES` 순서 = CLAUDE.md 표 순서.
  - `occurred_at`/`scheduled_at` 은 tz-aware 만 받고 UTC 로 정규화해 저장한다 — "어제 저녁" 해석은 P5.
- **P6-memory / P6-briefing**: `add_event` 는 패턴·승격·`fact_sources` 를 건드리지 않는다. `get_briefing(ctx, person_id, schedule_id=None) -> BriefingOut{person, aliases, facts[전부, updated_at DESC], recent_events[5], upcoming_schedules[3], schedule?, generated_at}` — 문장·제안 없음; `schedule_id` 가 있을 때만 그 일정 `briefed_at` 을 `now` 로 덮어쓴다(주기 작업의 "이미 브리핑함" 판단은 이 컬럼). `person_facts` 는 `(person_id, key)` 애플리케이션 upsert(UNIQUE 없음).
- **architect**: F-4d2507(DELETE /persons backlog 항목) + 01-plan 미결 8 의 JSONB 참조 정리 요건.

결과: 완료
승인: 사용자 (2026-09-05)