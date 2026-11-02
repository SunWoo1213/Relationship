# P5b-query-turn U3 조회 답 생성기·검증기·템플릿 (`respond.py` 확장, 순수 층) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 — [필수] 0 · [권고] 5(R-U3-1 `절대노출금지` 미포함 단언은 이 층에서 공허(구조적 보장이 진짜 근거), R-U3-2 `no_record_reply([])` 퇴화 문자열 — U4 가 언급 0 을 먼저 걸러야, R-U3-3 재export 범위가 `propose.py` 관례(`PROPOSERS`·`PROPOSAL_SCHEMA`·공급자 클래스)보다 좁음, R-U3-4 E-6 조립 결과에 원칙7 구절 뒤 문장 경계가 없음("…하지 않는다 아래 인물 카드…" — 계획 글자 그대로라 위반 아님, 다듬으려면 계획 결정), R-U3-5 03-log U3 항목·registry 해시 pending 3곳). 코드 결함은 찾지 못했다. 계약 값 직접 확인 174 PASS / 0 FAIL, 변이 25건(계획 표 5 재현 + 계획 변형 1 + 내 변이 19) 전부 검출·생존 0·동등 0, U3 파일 71 passed, 전체 2081 passed(2010 + 71)·skip 0, ruff 통과, `tools_check` 7/7, 범위 밖 diff 0, 기존 테스트 파일 수정 0, 기존 `respond.py` 줄 제거 0.
대상: 작업 트리(HEAD `06b7bb5` = U2, 무변경 기준 `8a8767b`) — `git diff HEAD -- app`(`--numstat` `__init__.py 27 1` · `respond.py 465 0`, 합 +492/−1) · 신규 `tests/test_agent_query_answer.py`(594줄, 수집 71 = 함수 48 + parametrize 23) · `docs/wiki/registry.md` 비고 2곳(`__init__.py`·`respond.py` 행) + 새 행 1(`tests/test_agent_query_answer.py`) · `docs/wiki/packages/P5b-query-turn/tests.md` U3 절 · 구현 증거 `evidence/20261102-0856-u3-{answer,pytest-all}.txt`·`20261102-0857-u3-{diff-filter,mutation,ruff,scope,tools-check}.txt`(7). `HANDOFF.md`·`journal.md`·`03-log.md` 의 문서 diff 는 위임대로 리뷰 대상 아님(03-log 에 U3 항목이 아직 없다는 사실만 §7 에 적는다).
근거 문서: `01-plan.md` 100~104행(U3 계약·프롬프트·테스트 목록·변이 표 5건) · 86~87행(구현 제약 (1)~(5)) · 218~228행(결정 D 근거 항목·넣지 않는 것·`QUERY_TIMELINE_LIMIT = 5` 평 상수) · 230~244행(결정 E — E-1 `{answer}`·`report_query_answer`, E-2 3줄/240자 `>` 거부·줄 = strip 뒤 공백 아닌 줄, E-3 import 재사용·사유 `empty`/`too_many_lines`/`too_long`/`forbidden_expression`·순서 empty → 줄 → 길이 → 금지, E-5 문구 5종, E-6 system 문장) · 250행 결정 F ①(`QUERY_MORE_HINT = "자세한 건 인물 화면에서 볼 수 있어요."`, respond.py 상수) · `docs/wiki/decisions/D16-query-turn.md` 결정 4("사실 전부 + 타임라인 최근 5건 + 다가오는 일정 전부 + `relation_tag`·`hierarchy`·`last_contact_at`")·5("R19 금지 표현 검증기 … 통과하지 못하면 템플릿 답")·7·10, "코드에서 지켜야 할 것" 6("프롬프트에 들어가는 근거는 `get_person_card` 응답에서 온 값뿐 … 타임라인은 최근 5건까지") · `CLAUDE.md` 44행 원칙7 경계 구절 · `docs/wiki/verification.md` 79~87행(변이 규칙) · `docs/wiki/security.md` §1 · 사용자가 수용한 구현자 판단 5건(①`TYPE_CHECKING` import ②`now` ISO·일정 `M월 D일` ③user_text 배치·빈 절 `- 없음` ④`JudgeUnavailable(fail)` 위치 인자 ⑤`template_query_answer` 의 `now` 미사용) + evidence 타입 `app.api.schemas.PersonCardOut`.
내가 남긴 증거(모두 `docs/wiki/packages/P5b-query-turn/evidence/`): `20261102-0908-verifier-u3-tests.txt`(U3 파일 -v) · `20261102-0908-verifier-u3-full-regression.txt`(전체 `-q -rs`) · `20261102-0908-verifier-u3-lint.txt`(ruff) · `20261102-0908-verifier-u3-tools-check.txt`(7/7) · `20261102-0913-verifier-u3-scope.txt`(범위 diff·`-` 줄 전수·HEAD 줄 보존·순환 import·수집·tests.md 대조·registry·`git status`) · `20261102-0913-verifier-u3-contract-values.txt`(계약 값 Python 직접 확인 — 2회 append, 1회는 스크래치패드 스크립트가 저장소 루트를 `sys.path` 에 안 넣어 `ModuleNotFoundError` exit 1, 2회차 exit 0 · 174 PASS 가 판정 근거) · `20261102-0914-verifier-u3-grep-constraints.txt`(구현 제약 (1)~(5)·비밀·R-4 집계) · `20261102-0914-verifier-u3-mutation.txt`(변이 25 + 대조군). 스크립트는 스크래치패드 `verifier-p5b-u3/{scope.sh,contract.py,constraints.sh,mutate.py}`.

---

## 1. 본 것 — 01-plan 100~104행·결정 D·E·F 계약 대조

| 계약(01-plan·결정 글자 그대로) | 코드 위치(`app/agent/respond.py`) | 직접 확인(contract-values 2회차) | 테스트 | 판정 |
|---|---|---|---|---|
| `QueryAnswerer` Protocol(`answer(question, evidence, now) -> QueryAnswer`) | 184~185행 | `inspect.signature` 매개변수 `['self','question','evidence','now']` | Fake·공급자 3종이 같은 시그니처 | 일치 |
| `QueryAnswer`(frozen: `text`·`tokens_in`·`tokens_out`·`provider`·`model`, `trace_tokens()`) | 166~180행 | `FrozenInstanceError` 발생, 필드 순서 5종 그대로, `trace_tokens() == ComposedBriefing(tokens_in=3,tokens_out=4).trace_tokens() == (3, 4)` tuple | `test_query_answer_trace_tokens_shape` | 일치. V12 검출 |
| E-1 구조화 출력 `{answer: string}`, 도구 `report_query_answer` | 143~148행·135행 | 스키마 dict 동치(`required ["answer"]`·`additionalProperties False`), 이름 일치 | `test_schema_and_tool_name_exact_values` | 일치. V23 검출 |
| `build_query_answer_prompt(question, evidence, now) -> (system, user_text)` | 213~254행 | 반환 튜플 2 | 프롬프트 테스트 5건 | 일치 |
| E-6 system 문장 그대로 + 원칙7 구절 원문 | 150~158행 | `system == "너는 … 보조 도구다. " + 원칙7 구절 + " 아래 인물 카드 자료만 근거로 1~3줄 … report_query_answer 도구로만 답하라."` → True(255자). `CLAUDE.md` 44행에서 `**` 를 뗀 구절 "채팅의 조회 답(CR-004 · D16)도 기록된 사실의 재진술로 한정한다 — 평가·조언·감정 대화는 하지 않는다" 가 system 에 포함 True. "다른 인물과의 관계는 말하지 마라"·"1~3줄"·"report_query_answer 도구로만 답하라" 포함 | `test_prompt_system_exact_sentences` | 일치. V10·V20·M3a 검출. §4b 메모(문장 경계) |
| 결정 D 근거: 이름·태그·위계·별칭 전부·`last_contact_at`(사용자 시간대 날짜)·사실 전부(`key=value`, 날짜)·패턴 전부(`value`)·타임라인 앞 5건(`type`·`content`·날짜)·일정 전부(`title`·날짜) | 222~253행 | 내 카드(사실 2·패턴 2·타임라인 6·일정 3): 질문 1회·`2026-10-25T12:00:00+09:00`·`마지막 접촉: 10월 21일`(UTC 10-20 16:30 시드)·`hobby=등산 (10월 21일)`·`team=플랫폼팀 (10월 19일)`·패턴 2 값·`- [meal] 타임라인검증1 (10월 19일)`~5 있고 6 없음·`일정검증1~3 (11월 3일)` 전부 — user_text 전문은 증거 파일에 출력 | `test_prompt_user_text_has_question_now_and_evidence_values`·`…timeline_limit_keeps_only_first_five`·`…last_contact_date_in_user_timezone_not_utc` | 일치. M4·M5·V14·V17 검출 |
| 결정 D 넣지 않는 것: 인물 id·사실 id·이벤트 id·`source_count`·`briefed_at`·`raw_utterance`·환경변수·키 | — | 내 카드의 id(424242·535353·535354·646464·646465·757501·757505·868601)·`source_count`·`briefed_at`·`raw_utterance`·`ANTHROPIC`·`OPENAI`·`GEMINI`·`LLM_PROVIDER`·`API_KEY`·`environ`·`sk-`·`.env`·`SECRET`·`TOKEN` 전부 system+user 에 없음(21건 PASS). `PersonCardOut`/`TimelineEventOut` 필드 집합에 `raw_utterance` 없음(구조적) | `test_prompt_excludes_raw_ids_and_secrets` | 일치. §7 R-U3-1 |
| 빈 카드 표기(수용 판단 ③) | 228~253행 | `- 없음` 4회·`별칭: 없음`·`마지막 접촉: 기록 없음` | — | 일치 |
| 공급자 3종 — `select_provider`·`call_with_error_mapping`·`call_with_gemini_error_mapping`·`_to_gemini_schema` import, compose.py 707~770행 관례(모델 env 공유·`ER_JUDGE_TIMEOUT`/`ER_JUDGE_MAX_RETRIES`·`usage` 토큰) | 54~62행 import, 313~508행 | 같은 예외 → `ClaudeQueryAnswerer` 와 `ClaudeBriefingComposer` 의 `str(JudgeUnavailable)` 동일: timeout·rate_limit·api_error·connection 4종 × Claude/OpenAI/Gemini = 12건 전부 `answerer == composer == 기대`. `provider` 문자열 `anthropic`/`openai`/`gemini` 가 compose.py 소스의 `provider="…"` 와 같음. `max_tokens=1024` 동일. `tool_use` 없음·`choices` 빈 목록·`tool_calls None`·arguments JSON 아님·`text` 없음·JSON 아님·`answer` 비문자열(숫자·None·dict 아님) → 전부 `"schema"`. usage 회수 `(11,22)`·`(3,4)`·`(5,6)`, usage None → `(0,0)`. Gemini config: `system_instruction`·`temperature 0`·`application/json`·`response_schema == _to_gemini_schema(QUERY_ANSWER_SCHEMA)`. `GEMINI_MODEL` 없음 → `InvalidValue` | 공급자 테스트 16함수 19건 | 일치. V16·V18·V21·V24 검출 |
| 등록표·`answerer_from_env()` | 511~521행 | `set(QUERY_ANSWERERS) == set(BRIEFING_COMPOSERS) == {anthropic, openai, gemini}`, Fake 는 표 밖, 본문 `return QUERY_ANSWERERS[select_provider(env)]()` 가 `composer_from_env` 본문과 이름만 다름(D11 2단계 패턴), `LLM_PROVIDER` 3종 각각 그 클래스, 활성 집합 밖·미지 이름 → `InvalidValue` | `test_query_answerers_registry_has_three_providers`·`test_answerer_from_env_*` 4건 | 일치. V11·V15 검출 |
| `FakeQueryAnswerer`(표 기반, `fail` 주입, `call_count`) | 524~540행 | 표 키 → 답, 없으면 `""`, `provider "fake"`, `call_count` 2; `fail="api_error"` → `JudgeUnavailable`, `str(e) == "api_error"`, `call_count` 1. `JudgeUnavailable.__init__ is Exception.__init__` 이라 위치 인자(수용 판단 ④)와 compose.py 의 `error=` 키워드가 같은 `str(e)` | `test_fake_answerer_*` 2건 | 일치. V22 검출 |
| `validate_query_answer(text) -> str \| None`, E-2 3줄/240자 `>` 거부·줄 = strip 뒤 공백 아닌 줄, E-3 import 재사용·순서 empty → 줄 → 길이 → 금지 | 262~276행 | `""`·`"  \n "` → `empty`; 3줄 None·4줄 `too_many_lines`; 공백 줄 불산입; 240 None·241 `too_long`; strip 뒤 240 None; 금지 14개 각각 `forbidden_expression`; 4줄+금지 → `too_many_lines`; 241+금지 → `too_long`; 3줄·238자+금지 → `forbidden_expression`. `REASON_TOO_LONG is compose.REASON_TOO_LONG`·`REASON_FORBIDDEN_EXPRESSION is …`·금지 목록 `is` 같은 객체 | 검증기 테스트 9함수 26건 | 일치. M1·M2·M3a·M3b·V6·V13 검출 |
| E-5 템플릿(근거 있음) `"{display_name} — {relation_tag}·{hierarchy}, 마지막 접촉 {M월 D일}, 알고 있는 것 {n}건. 자세한 건 인물 화면에서 볼 수 있어요."`, `n = len(facts)+len(patterns)`, 없으면 `"마지막 접촉 기록 없음"`, 0 패딩 없음 | 279~294행 | 사실 1·LC 10-20T16:30Z → `"박선우 과장님 — 직장·동, 마지막 접촉 10월 21일, 알고 있는 것 1건. 자세한 건 인물 화면에서 볼 수 있어요."` 글자 그대로; LC None → `"…마지막 접촉 기록 없음, 알고 있는 것 0건. …"`; 사실 2+패턴 2+타임라인 6+일정 3 → `4건`; 1월 5일 UTC 15:00 → `1월 6일,`(패딩 없음) | `test_template_with_evidence_exact_string_and_last_contact_in_user_timezone`·`…without_last_contact_exact_string`·`…count_is_facts_plus_patterns` | 일치. M5·V9·V19 검출 |
| E-5 근거 0건(사실·패턴·타임라인·일정 모두 0) `"{display_name} — {relation_tag}·{hierarchy}로 기억하고 있어요. 그 밖의 기록은 아직 없어요."` | 286~287행·`has_evidence` 200~205행 | LC 있어도·별칭 있어도 근거 0 → 그 문자열; `has_evidence` 는 facts/patterns/timeline/schedules 각 1건만으로 True, 모두 0 이면 False | `test_template_no_evidence_exact_string_even_with_last_contact`·`test_has_evidence_true_for_each_source[4]` | 일치. V8 검출 |
| E-5 ③-2 `no_record_reply` 1개 `"\"{mention}\"에 대한 기록이 없어요."`, 여러 개 `"\"{a}\", \"{b}\"…"`(첫 등장 순) · 언급 0 `"누구에 대해 물어보셨는지 알아듣지 못했어요. 이름을 넣어 다시 물어봐 주세요."` | 297~305행 | 세 값 글자 그대로, 순서 유지 | `test_no_record_reply_*`·`test_no_mention_reply_exact_string` | 일치. V7 검출. §7 R-U3-2(`[]`) |
| 결정 F ① `QUERY_MORE_HINT` · 결정 J `QUERY_ONE_AT_A_TIME_HINT` (respond.py 상수, 붙이는 것은 U4) | 128~130행 | 값 일치, `app.settings` 에 `QUERY_MORE_HINT` 없음 | `test_hint_constants_exact_values` | 일치 |
| 템플릿 출력이 검증기를 통과(폴백이 다시 걸리지 않음) | — | 템플릿 4종(근거 있음·0건·LC None·가득) + 고정 응답 3종 전부 `None`, 근거 있음 템플릿 1줄·≤240자 | `test_template_outputs_pass_validator` | 일치 |
| `app/agent/__init__.py` 재export 12종 | import 12 + `__all__` 12 | 12종 전부 `app.agent.X is respond.X` 이고 `__all__` 포함, `build_reply` 유지, `__all__` 중복 없음 | 테스트 파일이 `app.agent` 에서 12종 import | 일치. §7 R-U3-3 |
| `PersonCardOut` 은 `TYPE_CHECKING` import(수용 판단 ①) | 73~74행 | 런타임 모듈 전역에 `PersonCardOut` 없음, `app.api` 런타임 import 없음, `import app.agent.respond` 단독·`import app.agent`·`import app.api; import app.agent`·`import app.main`·`import app.briefing.compose; import app.agent.respond` 전부 ok | — | 일치 |
| 테스트 목록(01-plan 103행 14항목) | — | 금지 14 parametrize / 줄 경계 / 글자 경계 / 빈·공백 / 정상 / 템플릿 3종 정확 문자열 / 템플릿 통과 / `no_record_reply` / 프롬프트 원칙7·질문·근거·시드 원문·5건 / 공급자 3종 오류 매핑 / `answerer_from_env` — 48함수가 전부 덮는다(§5) | — | 일치 |

## 2. 직접 실행한 검증 명령과 출력

| 명령 | 출력 | 증거 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_agent_query_answer.py -v` | 71 passed in 1.03s, exit 0 | `…-0908-verifier-u3-tests.txt` |
| `… pytest tests/ -q -rs` | 2081 passed, 1 warning in 23.47s — `skip` 문자열 0줄. 기준 2010 + 71 | `…-0908-verifier-u3-full-regression.txt` |
| `.venv/bin/ruff check app tests` | `All checks passed!` exit 0 | `…-0908-verifier-u3-lint.txt` |
| `.venv/bin/python scripts/tools_check.py` | `RESULT: 7/7 ok` exit 0 | `…-0908-verifier-u3-tools-check.txt` |
| `git diff --diff-filter=M --stat 8a8767b -- tests` | 빈 출력(0줄) — 기존 테스트 파일 수정 0 | `…-0913-verifier-u3-scope.txt` (A) |
| `git diff --stat HEAD -- app/briefing app/er app/api app/agent/loop.py app/agent/gate.py app/agent/propose.py app/agent/types.py app/settings.py alembic web` + `app/tools app/db app/memory app/main.py scripts` | 둘 다 빈 출력(0줄) | 같은 파일 (B)(B2) |
| `git diff --name-only HEAD -- app` / `--numstat` | `app/agent/__init__.py`(27/1)·`app/agent/respond.py`(465/0) 2개 — 01-plan 100행이 지정한 `respond.py` + 재export | 같은 파일 (C)(D) |
| `git diff HEAD -- app/agent/respond.py` 의 `-` 줄 전수 | 0줄. `diff <(git show HEAD:app/agent/respond.py) app/agent/respond.py` 의 `<` 줄 0 — HEAD 의 모든 줄(기존 `build_reply`·docstring 포함)이 그대로 남음. `def build_reply(` 39행 → 80행(위에 docstring 절·import 가 더해져 내려감). HEAD ↔ `8a8767b` 의 `respond.py` 는 동일(U1·U2 가 손대지 않음) | 같은 파일 (E)(G)(G2)(G3) |
| `git diff HEAD -- app/agent/__init__.py` 의 `-` 줄 전수 | `-from app.agent.respond import build_reply` 1줄 — 괄호 import 로 바뀌며 `build_reply` 는 `+` 줄에 남음(유실 0) | 같은 파일 (F) |
| 순환 import 5가지 순서 | 전부 ok(§1 표) | 같은 파일 (H) |
| `pytest --collect-only -q` ↔ `tests.md` | 수집 71, 함수 48(parametrize: 금지 14·empty 3·has_evidence 4·non_string 4·from_env 3 = 28 → 48 + 28 − 5 = 71). `tests.md` 표 48행 이름 `diff` → `SAME`. 머리글 "신규 71건 = 함수 48개" 맞음. 표의 `(n건)` 합 28 | 같은 파일 (I)(J)(J2)(J3) |
| 계약 값 Python(174 항목) | 174 PASS / 0 FAIL, exit 0(2회차) | `…-0913-verifier-u3-contract-values.txt` |
| 구현 제약 (1)~(5) + 비밀 패턴 — app 추가 줄 401·신규 테스트 594줄 대상 `grep -nE` | (1) `create_person\(\|update_person\(` 0 / (2) 확신도 영어 어휘 0 / (3) `sleep`·`while True` 0 / (4) `PendingQuestion`(Out 제외 및 전체)·`flag_modified`·`.context =` 0 / (5) 키 패턴 0 — app 추가 줄·신규 테스트 모두 exit 1(0건). 환경변수 이름이 있는 app 추가 줄 6개는 `os.environ.get("ANTHROPIC_MODEL"/"OPENAI_MODEL"/"GEMINI_MODEL")` 3줄 + Gemini docstring·`InvalidValue` 메시지 3줄(compose.py 325~338행 관례와 같은 문장, 프롬프트·trace 아님) — 프롬프트 문자열 자체에는 0(contract §5 21건). 기준 `8a8767b` `respond.py` 18행 `update_person(facts=…)` 는 기존 docstring(예외 기록). R-4 집계 현재 ↔ 기준: `create_person\(` 1 = 1, `update_person\(` 5 = 5 | `…-0914-verifier-u3-grep-constraints.txt` |
| 저장소 무수정 | 변이 뒤 `git status --short` = 리뷰 전과 같음(제품 2 + 문서 5 + 구현 증거 7 + 내 증거 + 신규 테스트 1) | `…-0914-verifier-u3-mutation.txt` 끝·`…-scope.txt` (L) |

## 3. 변이 시험 — 내가 직접 (`20261102-0914-verifier-u3-mutation.txt`)

방법: 스크래치패드 `verifier-p5b-u3/mutate.py` 가 변이마다 새 하위 디렉터리(`mut/<id>/`)에 `app`·`tests`·`pyproject.toml`·`alembic.ini` 를 복사(`__pycache__` 제외)하고 문자열 치환(정확히 1곳 — 아니면 중단)을 적용한 뒤 `APP_TIMEZONE=Asia/Seoul` 로 `pytest tests/test_agent_query_answer.py -q -p no:cacheprovider`(71건, DB·네트워크 0)를 돈다. 저장소 무수정. 구현자의 `p5b-u3/mutate.py`(M1~M7) 와 독립이다.

| 변이 | 치환 | 결과 | 검출 테스트 |
|---|---|---|---|
| C0 대조군 | 없음 | 71 passed | — |
| M1 금지 표현 검사 제거(계획 표 1) | `if any(bad in text …): return REASON_FORBIDDEN_EXPRESSION` 삭제 | FAIL 14 | `test_validate_rejects_each_forbidden_expression[14]` |
| M2 글자 상한 `>` → `>=`(계획 표 2) | 비교식 | FAIL 2 | `…char_limit_boundary_240_pass_241_rejected`·`…char_count_uses_stripped_text` |
| M3a 줄 상한 3 → 4(계획 표 3, `settings.py` 상수) | `QUERY_ANSWER_MAX_LINES = 4` | FAIL 3 | `…line_limit_boundary…`·`…order_lines_before_length_before_forbidden`·`test_prompt_system_exact_sentences`(system 의 "1~3줄" 이 상수에서 옴) |
| M3b 상수는 3, 비교만 `+ 1`(내 변형 — 상수 단언을 우회) | `> QUERY_ANSWER_MAX_LINES + 1` | FAIL 2 | `…line_limit_boundary…`·`…order_lines…` |
| M4 타임라인 자르지 않음(계획 표 4) | `evidence.timeline[:QUERY_TIMELINE_LIMIT]` → `evidence.timeline` | FAIL 1 | `test_prompt_timeline_limit_keeps_only_first_five` |
| M5 날짜를 UTC(계획 표 5) | `value.astimezone(user_timezone())` → `value` | FAIL 3 | `…template_with_evidence_exact_string…`·`…user_text_has_question_now_and_evidence_values`·`…last_contact_date_in_user_timezone_not_utc` |
| V6 검사 순서 금지 표현 먼저 | 블록 재배열 | FAIL 1 | `…order_lines_before_length_before_forbidden` |
| V7 `no_record_reply` 구분자 `", "` → `","` | 문자열 | FAIL 2 | `test_no_record_reply_exact_strings`·`…keeps_input_order` |
| V8 근거 0건 판별에서 일정 제외 | `has_evidence` 식 | FAIL 1 | `test_has_evidence_true_for_each_source[card3]` |
| V9 템플릿 `n` 에서 패턴 제외 | `len(evidence.facts)` | FAIL 1 | `test_template_count_is_facts_plus_patterns` |
| V10 E-6 "다른 인물과의 관계는 말하지 마라. " 삭제 | system 문자열 | FAIL 1 | `test_prompt_system_exact_sentences` |
| V11 `QUERY_ANSWERERS` 에서 gemini 제거 | dict 원소 | FAIL 2 | `…registry_has_three_providers`·`…from_env_follows_llm_provider[gemini]` |
| V12 `trace_tokens` 가 `(0, 0)` | 반환식 | FAIL 4 | `…trace_tokens_shape` + 공급자 파싱 3건 |
| V13 empty 검사 제거 | `if not stripped: return REASON_EMPTY` 삭제 | FAIL 4 | `…empty_or_blank_is_empty[3]`·`…claude_answerer_empty_string_answer_passes_through_for_validator` |
| V14 프롬프트 `now` 를 UTC 그대로 | `now.isoformat()` | FAIL 1 | `…user_text_has_question_now_and_evidence_values`(`+09:00` 단언) |
| V15 `answerer_from_env` 가 `select_provider` 우회 | `env.get("LLM_PROVIDER")` 직접 | FAIL 1 | `…from_env_unknown_and_disabled_rejected`(활성 집합 규칙) |
| V16 Claude 토큰 in/out 뒤바뀜 | getattr 교환 | FAIL 1 | `…claude_answerer_parses_text_and_usage` |
| V17 프롬프트에서 별칭 누락 | `"별칭: 없음"` 고정 | FAIL 1 | `…user_text_has_question_now_and_evidence_values` |
| V18 Gemini `response_schema` 변환 없이 원 스키마 | `_to_gemini_schema` 제거 | FAIL 1 | `…gemini_answerer_request_uses_schema_and_parses` |
| V19 템플릿 끝 문장 "인물 카드에서"(결정 F 이전 문구) | f-string | FAIL 2 | 템플릿 정확 문자열 2건 |
| V20 원칙7 구절 뒤 마침표 추가 | system 조각 | FAIL 1 | `test_prompt_system_exact_sentences` |
| V21 Claude `provider="claude"` | 문자열 | FAIL 1 | `…claude_answerer_parses_text_and_usage` |
| V22 Fake `call_count` 미증가 | 줄 삭제 | FAIL 2 | `test_fake_answerer_*` 2건 |
| V23 스키마 `additionalProperties: True` | dict 값 | FAIL 1 | `test_schema_and_tool_name_exact_values` |
| V24 `_parse_answer` 가 비문자열을 `str()` 로 수용 | isinstance 검사 완화 | FAIL 3 | Claude `[bad_output0]`·OpenAI·Gemini 비문자열 3건 |

검출 25 / 생존 0 / 동등 0. 계획 표 5건(M1·M2·M3a·M4·M5)은 계획이 적은 테스트가 그대로 잡는다. 구현자 증거 `…-0857-u3-mutation.txt` 의 M1~M7(M6 패턴 제외 = 내 V9, M7 비문자열 = 내 V24)과 결과가 맞다. 테스트가 "통과한다" 가 아니라 글자 그대로의 값(정확한 문자열·사유 어휘·토큰 쌍·provider 이름·스키마 dict)을 단언하므로 변이마다 다른 부분집합이 FAIL 한다 — 항상 통과하는 테스트는 없다(R-U3-1 의 단언 1개만 예외, §4a).

## 4. 계획 불일치·메모 판정

### 4a. `절대노출금지` 미포함 단언은 이 층에서 공허하다(계획이 그렇게 요구했고, 구조적 보장이 진짜 근거)

01-plan 103행 "시드 원문 문자열(예 `절대노출금지`) 미포함" 을 `test_prompt_excludes_raw_ids_and_secrets` 가 `"절대노출금지" not in text` 로 옮겼는데, 이 테스트의 카드 어디에도 그 문자열이 **들어가지 않는다**(`PersonCardOut`·`TimelineEventOut` 에 `raw_utterance` 필드가 없다 — `app/api/schemas.py` 307~309행 주석, contract §5 [참고]). 어떤 구현이라도 이 단언은 통과한다. 실제 보장은 ① 타입에 원문 필드가 없다 ② `build_query_answer_prompt` 가 카드 값만 읽는다(§1) 이고, "DB 의 `raw_utterance` 시드가 `reply`/프롬프트에 안 나온다" 는 카드가 `get_person_card()` 에서 오는 U4(루프)에서 DB 시드로 검사해야 의미가 있다. 코드 결함 아님. 같은 테스트의 다른 단언(id 3종·`source_count`·`briefed_at`·환경변수 5종)은 실질적이다 — id 는 카드에 실제로 7777/8888/9001 이 들어 있고 프롬프트에 없음을 본다.

### 4b. E-6 조립 결과에 원칙7 구절 뒤 문장 경계가 없다 — 계획 글자 그대로

01-plan 243행은 `"…보조 도구다. "` + 원칙7 구절 원문 + `" 아래 인물 카드 자료만 …"` 로 이어 붙이라고 했고 구절 원문은 마침표 없이 "…하지 않는다" 로 끝난다. 그래서 system 은 "…평가·조언·감정 대화는 하지 않는다 아래 인물 카드 자료만 근거로…" 가 된다(contract §5 전문). 구현은 계획과 글자 그대로 같고(True, 255자), 계획 자체가 "구현자가 표현을 다듬어야 하면 멈추고 보고한다" 고 했으므로 구현자가 손대지 않은 것이 맞다. LLM 이 읽는 데 지장은 없어 보이지만 마침표 하나는 메인 세션/사용자가 결정할 일이다 — 넣으면 `test_prompt_system_exact_sentences` 의 기대 문자열도 같이 바뀐다(V20 이 그 변이). 위반 아님.

### 4c. 수용된 구현자 판단 5건 — 코드와 일치

① `TYPE_CHECKING` import(73~74행, 런타임 `app.api` 미참조, 5가지 import 순서 ok) ② `현재 시각: 2026-10-25T12:00:00+09:00`(ISO), 일정 `일정검증1 (11월 3일)` ③ user_text 배치 `질문:` → `현재 시각:` → `[인물 카드]` 이름·관계·별칭·마지막 접촉·알고 있는 사실·반복 패턴·최근 타임라인(최대 5건)·예정된 일정, 빈 절 `- 없음` ④ `JudgeUnavailable(self.fail)` ⑤ `template_query_answer(evidence, now)` 가 `now` 를 안 쓴다(docstring 에 명시). evidence 타입은 `app.api.schemas.PersonCardOut` 그대로(테스트·contract 둘 다 그 타입으로 호출).

### 4d. 계획에 없는 것이 들어갔는가

새 상수·새 환경변수 없음: `respond.py` 의 `os.environ` 사용은 `ANTHROPIC_MODEL`·`OPENAI_MODEL`·`GEMINI_MODEL` 3곳(compose.py 와 같은 이름, grep (9)). `_QUERY_ANSWER_TOOL_DESCRIPTION`(도구 설명 1문장)·`_NO_LAST_CONTACT`·`_NO_MENTION_REPLY`·`REASON_EMPTY`·`REASON_TOO_MANY_LINES`·`has_evidence()` 는 결정 E-1/E-3/E-5 의 값을 담는 이름이지 새 문구·새 규칙이 아니다(값은 §1 에서 글자 그대로 확인). 폴백 분기·`QUERY_MORE_HINT` 붙이기·`loop_query` trace 는 없다(U4 몫, 모듈 docstring 30~34행이 그렇게 적음) — `loop.py` diff 0.

## 5. `tests.md`·`registry.md`·테스트가 실패 조건을 검사하는가

- `tests.md` U3 절 표 48행 ↔ `--collect-only` 함수 48: 이름 집합 `diff` → `SAME`. 머리글 "신규 71건 = 함수 48개, 파라미터 포함" 맞음(71 = 48 + 28 − 5). "71 passed"·"2081 passed, skip 0"·검출 변이 `U3-M1~M7`·"첫 실행에서 전부 통과(실패 이력 없음)" 는 구현 증거 `…-0856-u3-answer.txt`(71 passed)·`…-0856-u3-pytest-all.txt`(2081 passed)·`…-0857-u3-mutation.txt` 와 내 재실행에 맞다. 표의 "입력 → 기대" 칸이 §1 의 직접 확인 값과 같다.
- 01-plan 103행 테스트 목록 14항목 ↔ 48함수: 전부 덮인다(§1 마지막 행). 계획에 없는 추가 테스트(`test_forbidden_expression_list_has_fourteen`·`…blank_lines_do_not_count`·`…char_count_uses_stripped_text`·`…order_…`·`…template_count_is_facts_plus_patterns`·`…template_no_evidence…`·`…has_evidence…[4]`·`…no_record_reply_keeps_input_order`·`…hint_constants…`·`…trace_tokens_shape`·Fake 2·스키마·Claude 요청 본문·빈 문자열 통과·기본 모델 env·OpenAI/Gemini 구조 위반·등록표·거부)는 결정 E-2/E-3/E-5/F/J·compose.py 관례의 직접 번역이라 범위 초과가 아니다.
- 테스트가 실제로 실패 조건을 검사하는가: §3 25변이 전부 검출. 공급자 테스트는 "예외가 난다" 가 아니라 `str(excinfo.value) == "timeout"/"rate_limit"/"schema"` 어휘까지 단언하고, 요청 본문(`tool_choice`·`tools`·`parameters`·`response_schema`)과 토큰 쌍·`provider` 값을 단언한다. 공허한 단언은 R-U3-1 의 `"절대노출금지"` 1개뿐.
- `registry.md`: `__init__.py` 행 "P5b U3(해시 pending): respond.py 의 조회 답 12종 재export"(12종 이름 = 내 확인 12종) / `respond.py` 행 "P5b U3(해시 pending)" 비고(Protocol·`QueryAnswer`·스키마·도구 이름·프롬프트·검증기 순서·템플릿·`has_evidence`·고정 응답·힌트 2·공급자 3·등록표·`answerer_from_env`·Fake·`TYPE_CHECKING`) 가 코드와 맞다 / 새 행 `tests/test_agent_query_answer.py` 71건(U3)·pending·"경계 시각 시드(UTC 10-20 16:30 → 서울 10월 21일)". 커밋 뒤 해시 치환 3곳은 메인 세션 몫.

## 6. 범위·원칙

- 범위: `app/` 변경 2파일이 01-plan 100행이 지정한 `respond.py` + 재export. `app/briefing`·`app/er`·`app/api`·`app/tools`·`app/db`·`app/memory`·`app/main.py`·`loop.py`·`gate.py`·`propose.py`·`types.py`·`settings.py`·`alembic`·`web`·`scripts` diff 0. 기존 테스트 파일 수정 0. 기존 `respond.py` 줄 제거 0(`build_reply`·docstring 보존). "하지 않는 것" — 폴백 분기·루프·trace·`QUERY_MORE_HINT` 붙이기·`get_person_card` 호출·`app/briefing/` 수정(E-3 후보 (ii) 기각)·`{answer, basis}` 스키마(E-1 후보 (ii) 기각)·환경변수 오버라이드(결정 D) 전부 없음.
- 원칙1·2·4: 확신도·임계치·ER 단계 무관 — 추가 줄에 `confidence`/`T_merge`/`T_new` 0, `app/er` diff 0(judge.py 의 헬퍼를 import 만 한다).
- 원칙7: system 에 CLAUDE.md 44행 구절 원문 + "위로·조언·감정 표현을 쓰지 마라" + "다른 인물과의 관계는 말하지 마라"(A–B 관계 제외 범위), 검증기가 R19 금지 표현 14개를 compose.py 와 같은 목록으로 거부, 템플릿·고정 응답 7종이 전부 검증기를 통과(사실 재진술뿐 — 평가·조언·감정 문장 0).
- 원칙9: `QueryAnswer.trace_tokens()` 가 `ComposedBriefing.trace_tokens()` 와 같은 `(in, out)` 모양, `provider`·`model` 보존 — U4 의 `loop_query` trace 재료. 검증 사유 4종이 문자열 어휘로 고정돼 `fallback_reason` 에 실을 수 있다.
- 툴 시그니처 v2·스키마 v2 무변경(`tools_check` 7/7, `alembic` diff 0, 새 툴·새 API 없음 — D16 "코드에서 지켜야 할 것" 3).
- security §1: 추가 줄에 키 패턴 0, 프롬프트 문자열(system·user)에 환경변수 이름·키·`.env` 0(contract §5), 요청 본문에도 0. Gemini `InvalidValue` 메시지의 ".env 의 GEMINI_MODEL" 은 compose.py 338행과 같은 운영 안내 문장이고 프롬프트·trace 가 아니다. `.env` 미독. 증거 파일은 전부 `save_evidence.py`(비밀 검사 통과). 변이는 스크래치패드 사본에서만.
- 동결·활성: 활성 패키지 P5b-query-turn(`fe4a99e`), U1 `1dccb95`·U2 `06b7bb5` 위의 세 번째 단위.

## 7. 소견

[필수] 없음.

[권고] (커밋을 막지 않음)

- R-U3-1 · `tests/test_agent_query_answer.py::test_prompt_excludes_raw_ids_and_secrets` 의 `"절대노출금지" not in text` 단언은 이 층에서 공허하다 — 카드에 그 문자열이 들어가지 않으므로 어떤 구현도 통과한다(§4a). 계획 103행을 글자 그대로 옮긴 것이라 구현자 잘못이 아니고, 실질 보장은 `PersonCardOut` 에 원문 필드가 없다는 구조다. U4 계획/리뷰에서 "DB 에 `raw_utterance="절대노출금지"` 시드를 넣고 `run_turn` 의 `reply`·`loop_query` trace·답 생성기에 넘어간 user_text 에 없음" 을 검사해야 이 단언이 의미를 갖는다(메인 세션 메모).
- R-U3-2 · `no_record_reply([])` 는 `'에 대한 기록이 없어요.'` 를 돌려준다(contract §3 참고 줄). 계획 E-5 는 1개/여러 개만 정의했고 언급 0 은 `no_mention_reply()` 몫이므로 이 층의 결함은 아니다. U4 가 "확정 인물 0 이고 언급도 0" 을 `no_mention_reply()` 로 먼저 보내야 한다(결정 E-5 언급 0 문구) — U4 리뷰에서 그 분기 순서를 본다. 방어 조건을 `no_record_reply` 안에 넣는 것은 계획에 없는 방어(FIX-033 (b))라 지금 권하지 않는다.
- R-U3-3 · `app/agent/__init__.py` 재export 12종에 `QUERY_ANSWERERS`·`QUERY_ANSWER_SCHEMA`·`QUERY_ANSWER_TOOL_NAME`·`ClaudeQueryAnswerer`/`OpenAIQueryAnswerer`/`GeminiQueryAnswerer`·`REASON_EMPTY`·`REASON_TOO_MANY_LINES` 가 없다. 같은 파일이 `propose.py` 쪽은 `PROPOSERS`·`PROPOSAL_SCHEMA`·`PROPOSAL_TOOL_NAME`·공급자 3 클래스를 재export 한다(관례 불일치). 테스트는 `app.agent.respond` 에서 직접 import 하고, 01-plan 101행은 재export 범위를 지정하지 않았으므로 계약 위반은 아니다. registry 비고 "12종" 은 코드와 맞다. U4 가 `REASON_*` 를 쓰게 되면 그때 같이 맞추는 것으로 충분(메인 세션 판단).
- R-U3-4 · E-6 조립 결과 system 에 원칙7 구절 뒤 문장 경계가 없다("…하지 않는다 아래 인물 카드…", §4b). 계획 243행 글자 그대로이고 구현자가 다듬지 않은 것이 규칙에 맞다. 마침표를 넣을지는 사용자/메인 세션 결정 — 넣으면 01-plan 243행·`test_prompt_system_exact_sentences` 기대 문자열을 함께 바꾼다. 지금 커밋에는 영향 없음.
- R-U3-5 · 03-log U3 항목(메인 세션). 03-log 에 아직 U3 항목이 없다(grep (10): "남은 것 · 다음 단위: U3" 까지만). 적을 것: ① 내 재실행 71·2081(2010 + 71)·skip 0·ruff·7/7·범위 diff 0·기존 테스트 수정 0·`respond.py` 제거 줄 0 ② 계약 값 174 PASS(contract-values 2회차; 1회차는 내 스크립트의 `sys.path` 누락으로 exit 1) ③ 변이 25 검출·생존 0·동등 0(구현자 M1~M7 과 정합) ④ R-U3-1~4 ⑤ `registry.md` 해시 pending 3곳 치환. Refs `P5b-query-turn CR-004 D16 S3.6 D11 원칙7 원칙9 R19`.

## 8. 판정

통과. U3 의 계약 전부 — `QueryAnswerer`/`QueryAnswer`(frozen, `trace_tokens()` 모양 = `ComposedBriefing`)·E-1 `{answer}`/`report_query_answer`·E-6 system 글자 그대로(원칙7 구절 원문 포함)·결정 D 근거(별칭·사실·패턴 전부, 타임라인 5건, 일정 전부, 사용자 시간대 날짜)와 넣지 않는 것(id·`source_count`·`briefed_at`·원문·환경변수·키 0)·E-2/E-3 검증기(3줄/240자 `>` 거부, 사유 4종 import 재사용, 순서 empty → 줄 → 길이 → 금지, 금지 14개)·E-5 문구 5종 글자 그대로·근거 0건 판별·F ①/J 힌트 상수·공급자 3종(compose.py 와 같은 오류 어휘 12/12·provider 문자열·`max_tokens`·`usage` 회수·`_to_gemini_schema`)·등록표 키 = `BRIEFING_COMPOSERS`·`answerer_from_env` = `select_provider` 2단계·Fake(표·`fail`·`call_count`)·재export 12종·`TYPE_CHECKING` 순환 회피 — 가 01-plan 100~104행·결정 D·E·F·J 확정 칸·D16 결정 4·5·"코드에서 지켜야 할 것" 6·사용자 수용 판단 5건과 맞고, 내 재실행에서 71 passed·전체 2081 passed(2010 + 71)·skip 0·ruff 통과·`tools_check` 7/7 이다. 변이 25건 전부 검출(생존 0). 범위 밖 diff 0, 기존 테스트 수정 0, 구현 제약 (1)~(5) 추가 줄 0건, 프롬프트에 비밀·환경변수 이름 0. 커밋을 막는 소견 없음.
