# P5b-query-turn · U7 수정 3(관계 질문 답 프롬프트 보강) 커밋 전 리뷰

검토자: verifier (fable)
일시: 2026-11-08
대상: 작업 트리 미커밋 변경(HEAD `e49f78d`, 브랜치 `dev2`) — `app/agent/respond.py` · `tests/test_agent_query_answer.py` · `docs/wiki/packages/P5b-query-turn/tests.md` "## U7 3차 — 관계 질문 답 프롬프트 보강(2026-11-07)" 절. 그 밖의 미커밋 변경(L-007 하네스·HANDOFF·03-log·journal)은 대상 밖.
결과: **통과** (재리뷰 2026-11-08 20:19, §6) — 1차 판정은 **보류**([필수] R-U7F3-1 문서 보정 1건)였고, R-U7F3-1·R-U7F3-2 가 닫힌 것을 직접 재실행으로 확인해 통과로 바꿨다. 1차 본문(§1~§5)은 기록으로 그대로 둔다. 열린 [권고]: R-U7F3-3(04-review §7 인계)·R-U7F3-4(evidence 1파일 삭제) — 커밋을 막지 않는다.

---

## 1. 본 것

| 파일 | 줄 | 본 내용 |
|---|---|---|
| `app/agent/respond.py` | 150~153 | `_RELATION_DESC`(5항목, `직장`→`직장 관계` 만 바뀌고 나머지 4개는 항등) · `_HIERARCHY_DESC`(`상(윗사람)`·`동(같은 급)`·`하(아랫사람)`). 주석 "어휘는 `app/db/models.py` 의 RELATION_TAGS·HIERARCHIES … 사전 밖 값은 원문 그대로". `models.py` 72~73행 `RELATION_TAGS`·`HIERARCHIES` 와 키 집합 동일(눈으로 대조 — 테스트로는 고정되지 않음, R-U7F3-2) |
| `app/agent/respond.py` | 155~164 | `_QUERY_SYSTEM_PROMPT` — "…1~3줄 한국어로 답하고, " 뒤에 "관계나 위계를 물으면 [인물 카드]의 '관계' 줄을 그대로 답하라 — 그것도 기록된 사실이다. " 1문장, "자료에 없는 것은…" 앞. 다른 문장 무변경 |
| `app/agent/respond.py` | 234~235 | 카드 줄 `관계: {_RELATION_DESC.get(tag, tag)}, 위계 {_HIERARCHY_DESC.get(h, h)}` — `.get(k, k)` 로 사전 밖 값 통과. user_text 머리 `[인물 카드]` 는 그대로(새 문장이 가리키는 이름과 일치) |
| `app/agent/respond.py` | 269~283 · 286~300 | `validate_query_answer`(empty → 줄 수 → 240자 → `BRIEFING_FORBIDDEN_EXPRESSIONS`) · `template_query_answer`(`{display_name} — {relation_tag}·{hierarchy}` 원안) — **둘 다 diff 에 없다(변경 0)**. 템플릿은 01-plan E-5 사용자 확정 문구라 그대로 둔 것이 맞다(어휘 불일치는 R-U7F3-3) |
| `app/briefing/types.py` | 242~257 | 금지 표현 14개(`기분`·`감정`·`위로`·`고민`·`상담`·`스트레스`·`마음이`·`마음을`·`배려`·`힘드`·`힘들`·`우울`·`속상`·`서운`). 새 어휘 `직장 관계`·`윗사람`·`같은 급`·`아랫사람`·`위계` 는 어느 것도 부분 문자열로 포함하지 않는다 — 카드 줄을 그대로 답해도 검증기에 걸리지 않음 |
| `app/api/schemas.py` | 323~327 | `PersonBasicOut.relation_tag: str`·`hierarchy: str`(Optional 아님). `models.py` 93~97행 `nullable=False` + CHECK 제약 → 운영 경로에서 `None`·사전 밖 값은 도달하지 않는다. passthrough 는 방어선일 뿐 |
| `tests/test_agent_query_answer.py` | 230~238 | `test_prompt_system_exact_sentences` — 시스템 프롬프트 **전체 문자열 정확 일치**(새 문장 위치까지 고정) |
| 같은 파일 | 253 · 264~275 | user_text 단언 `관계: 직장 관계, 위계 동(같은 급)` · 신규 `..._is_descriptive`(`\n관계: 직장 관계, 위계 동(같은 급)\n` 한 줄 단위) · `..._unknown_values_passthrough`(`기타`/`?` → `관계: 기타, 위계 ?`; pydantic 인스턴스 속성 대입은 `validate_assignment` 없음이라 유효) |
| `tests.md` | 207~222 | 표 4행 + 변이 2행(M1 빈 dict → 2 FAIL, M2 문장 제거 → 1 FAIL) + 수치(115 · 2127 · 38=38) |
| 구현자 evidence | `20261107-1538-u7fix3-{answer-tests,ruff,mypy,pytest-all}.txt` · `20261107-1539-u7fix3-{diff,mutation}.txt` | 115 passed(exit 0) · All checks passed · 38=38 · **2127 passed** · `--stat` 2파일 +28/−4(HANDOFF·journal 포함) · 변이 M1 `2 failed, 71 passed`·M2 `1 failed, 72 passed` — tests.md 주장과 일치 |
| 실 LLM evidence | `20261108-2002-u7t-1-relation.txt` vs `20261107-1534-u7s-1-relation.txt` · `20261108-2002-u7t-card-9-before.txt` | 아래 §2 |
| 카드·계획 | `D16-query-turn.md` 결정 4·5·8 · "코드에서 지켜야 할 것" 6 · 갱신 이력(보정 ①~③) · `01-plan.md` 219~245행(결정 D·E-2·E-3·E-5·E-6, 확정 줄 245행) | 아래 §2 |

## 2. 수용 기준 · 카드 대조

| 항목 | 근거(인용) | 판정 |
|---|---|---|
| 수용 기준 원문 질문 ① "박선우 과장님이랑 나는 관계가 뭐야?" | 카드 기준 `u7t-card-9-before.txt`: `"relation_tag":"직장","hierarchy":"동"`. 3차 `u7s-1` trace 529 `loop_query.reply` = **"기록이 없어요."**(answer_source=llm, 411/10). 4차 `u7t-1` trace 572 `reply` = **"직장 관계, 위계 동(같은 급)\n자세한 건 인물 화면에서 볼 수 있어요."**, `answer_source: "llm"`, `fallback_reason: null`, `rejected_answer: null`, tokens 448/16, `evidence_counts {facts 1, timeline 3}`, `mentions_dropped 0`. counts before/after `12\|15\|33\|6\|24\|36\|20` 동일(저장 0) | 닫힘 — 답이 카드 사실의 재진술이고 검증기(R19·3줄·240자)를 실제로 통과했다 |
| D16 결정 8 / 원칙7 경계 "조회 답은 기록된 사실의 재진술로 한정 … 감정·조언·고민·평가를 하지 않는다" | 새 문장은 "[인물 카드]의 '관계' 줄을 **그대로** 답하라 — 그것도 기록된 사실이다": 재진술 지시이고 평가·조언 어휘 0. 4차 ⑥(상담 유도) 답 "기록이 없어요." 유지(03-log 4차 표) | 지킴 |
| D16 결정 4 "근거 = … `relation_tag`·`hierarchy`…" · 코드 규칙 6 "프롬프트에 들어가는 근거는 `get_person_card` 응답에서 온 값뿐" | 카드 줄은 여전히 `relation_tag`·`hierarchy` 두 값에서만 나온다. 다만 `(윗사람)`·`(같은 급)`·`관계` 는 카드 응답에 없는 **풀어쓰기 문자열**(결정적 사전 5+3 항목)이다 — 새 사실이 아니라 표기 변환이지만, 규칙 6 을 글자 그대로 읽으면 설명이 필요하다 | 어긋나지 않음 · 보정 문구에 한 줄(R-U7F3-1 에 포함) |
| 01-plan 결정 E-6(243행) "system = … `' 아래 인물 카드 자료만 근거로 1~3줄 한국어로 답하고, 자료에 없는 것은 …'` — **구현자가 표현을 다듬어야 하면 멈추고 보고한다**" · 245행 "확정: … **E-6 프롬프트 문장 그대로** — 사용자 2026-10-28" | 코드 159~160행은 확정 문장 사이에 1문장을 끼웠다 — **사용자 확정 문구와 글자 그대로 어긋난다.** 멈추고 보고는 됐다(03-log 85~ 3차 "열림 1" → 메인이 위임). 그러나 01-plan E-6·D16 갱신 이력 어디에도 보정 기록이 없다(`grep "수정 3\|보정 ④\|관계 줄\|서술형\|같은 급"` 01-plan·D16 → 0건). 선례 R-U7F-1(review-u7-fix §3·§6.1)과 같은 성격 | **R-U7F3-1 [필수]** |
| 01-plan 결정 D(219~226행) 근거 조립 | 넣는 것·넣지 않는 것(id·`source_count`·`raw_utterance`·환경변수) 무변경. `test_prompt_excludes_raw_ids_and_secrets` 그대로 통과(§3 #1) | 지킴 |
| 01-plan E-2·E-3 검증기 | 코드 269~283 무변경. 실 LLM 답 16자·1줄 | 충돌 없음 |
| 01-plan E-5 템플릿 "`{relation_tag}·{hierarchy}`" 원안 확정 | `template_query_answer` 무변경(`EXACT_ONE_FACT_TEMPLATE` 단언 그대로 통과). 프롬프트 카드 줄만 서술형이 되어 템플릿 답과 어휘가 갈린다 | 계획대로 · 불일치는 R-U7F3-3 |
| 범위 | `git diff --stat -- app tests` = `respond.py` +9/−1 · `test_agent_query_answer.py` +19/−2 만(`evidence/20261108-2010-u7fix3-review-mutation-before.txt`). `app/api/`·`web/`·`app/settings.py`·`app/briefing/` 0 | 지킴 |
| 원칙1·2·4·9 | ER·임계치·trace 스키마에 손대지 않음(`loop_query.output` 키 집합 4차 trace 572 = 3차 529) | 지킴 |

## 3. 직접 재실행(evidence `docs/wiki/packages/P5b-query-turn/evidence/`, 전부 `save_evidence.py`)

| # | 명령 | evidence | 결과 | 대비 |
|---|---|---|---|---|
| 1 | `pytest -q tests/test_agent_query_answer.py tests/test_agent_query_loop.py tests/test_api_chat_query.py` | `20261108-2009-u7fix3-review-pytest-target.txt` | **115 passed**, exit 0 | = 구현자 115 |
| 2 | `ruff check app/agent/respond.py tests/test_agent_query_answer.py` | `20261108-2009-u7fix3-review-ruff.txt` | All checks passed, exit 0 | 통과 |
| 3a | `mypy app/agent/respond.py` | `20261108-2009-u7fix3-review-mypy.txt` | exit 1, "Found 34 errors in 14 files (checked 1 source file)" — **`respond.py` 자체 오류 0**(출력에 `respond.py` 줄 없음), 34건 전부 import 따라 들어온 기존 파일(`loop.py`·`pipeline.py`·`routes.py` 등) | 기준선 소음 — 3b 로 판정 |
| 3b | `scripts/mypy_check.py --run` | `20261108-2009-u7fix3-review-mypy-baseline.txt` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` | = 38=38 |
| 4 | `pytest -q -rs tests/` | `20261108-2011-u7fix3-review-pytest-all.txt` | **2127 passed**, SKIPPED 0, exit 0 | = 구현자 2127(기준선 2125 + 신규 2) |
| 5a | 변이 전 기준 — `respond.py` blob·`--stat` | `20261108-2010-u7fix3-review-mutation-before.txt` | blob `4752e815cf9b…`(= diff 헤더 `index 5974785..4752e81`), 153행 `"동": "동(같은 급)"`, `--stat` 2파일 +25/−3 | 기준 |
| 5b | **변이 실제 삽입**(Edit 로 153행 `"동": "동(같은 급)"` → `"동": "동"`) 후 `pytest -q tests/test_agent_query_answer.py` | `20261108-2011-u7fix3-review-mutation-run.txt` | **2 failed, 71 passed**, exit 1 — `test_prompt_user_text_has_question_now_and_evidence_values`(AssertionError `관계: 직장 관계, 위계 동(같은 급)`) · `test_prompt_relation_line_is_descriptive` | 검출 |
| 5c | 원복(Edit) 후 같은 스크립트 | `20261108-2011-u7fix3-review-mutation-after.txt` | blob **`4752e815cf9b…` 동일**, 153행 원문 복귀, `--stat` 5a 와 동일 | 원복 확인 |
| — | (무효) `sh -c 'git hash-object …; git diff --stat …'` | `20261108-2009-u7fix3-review-baseline.txt` | `sh -c` 인용 손실로 앞부분이 `git` 도움말 — `--stat` 부분만 유효. 5a 가 대체본. 삭제는 메인 세션 몫(검토자는 파일을 지우지 않는다) | 참고 |

구현자 변이 M1(빈 dict)·내 변이(`동` 1항목 원복)는 같은 두 테스트가 잡는다. M2(문장 제거)는 정확 일치 테스트가 잡는다(구현자 evidence 확인). **살아남는 변이**: `상`·`하`·`가족`~`지인` 항목만 바꾸는 변이 — 테스트가 `직장`/`동` 조합만 쓴다(R-U7F3-2).

## 4. 소견

### [필수]

- **R-U7F3-1 01-plan E-6 확정 문장과 코드가 어긋남 — 보정 기록(문서만, 메인 세션).** 245행 확정 줄은 "E-6 프롬프트 문장 **그대로** — 사용자 2026-10-28" 인데 코드는 문장 1개를 끼웠고, 보정 기록이 01-plan·D16 어디에도 없다. 04-review 가 E-6 을 grep 으로 대조하면 같은 지적이 난다(R-U7F-1 선례). 제안 문구 —
  - `01-plan.md` 245행 확정 줄 아래 1줄: "**보정(U7 수정 3, 2026-11-08, review-u7-fix3 R-U7F3-1)**: 실 LLM 3차(`evidence/20261107-1534-u7s-1-relation.txt`)에서 수용 기준 ① 에 '기록이 없어요' → E-6 문장 '…1~3줄 한국어로 답하고, ' 뒤에 **'관계나 위계를 물으면 [인물 카드]의 '관계' 줄을 그대로 답하라 — 그것도 기록된 사실이다. '** 1문장 추가, 카드 줄은 `관계: {relation_tag}·{hierarchy}` → `관계: {서술형}, 위계 {서술형}`(`_RELATION_DESC`·`_HIERARCHY_DESC`, 사전 밖은 원문). 4차(`u7t-1`) 답 '직장 관계, 위계 동(같은 급)'. E-5 템플릿 문구는 그대로."
  - `D16-query-turn.md` 갱신 이력에 1줄(보정 ④): "코드 규칙 6 '근거는 `get_person_card` 응답에서 온 값뿐' — 프롬프트 카드의 관계·위계 줄은 그 두 값의 **결정적 풀어쓰기**(`respond.py` 사전 5+3 항목, 사전 밖 원문)로 쓴다. 새 사실·다른 출처 없음. 결정 4·5·8 그대로."
  - 사용자 확정 문구를 바꾼 것이므로 완성 확인(L-006) 때 "E-6 에 문장 1개 더함" 을 한 줄로 알리는 것을 권한다(결정을 다시 묻는 것은 아니다).

### [권고]

- **R-U7F3-2 사전과 어휘 출처를 테스트로 묶기(backend-agent, 테스트만).** 주석은 "어휘는 `models.py` 의 RELATION_TAGS·HIERARCHIES" 라 하지만 고정하는 테스트가 없다 — `set(_RELATION_DESC) == set(RELATION_TAGS)`·`set(_HIERARCHY_DESC) == set(HIERARCHIES)` 1건, 그리고 `상`·`하`·`가족`~`지인` 각각의 출력 문자열 parametrize 1건. 지금은 `직장`/`동` 조합만 단언해 다른 6개 항목의 변이가 살아남는다(§3). 다음 단위(04-review 전)에서.
- **R-U7F3-3 템플릿(E-5)과 프롬프트 카드 줄의 어휘 불일치 기록.** 폴백 답은 "박선우 과장님 — 직장·동, …", LLM 답은 "직장 관계, 위계 동(같은 급)". 같은 질문에 폴백 여부로 표기가 달라진다. E-5 는 사용자 확정 문구라 바꾸는 것은 사용자 결정 — 04-review §7·P10 인계로 적어 두고, 바꾸려면 그때 묻는다. 지금 코드를 고치지 않은 것이 계획에 맞다.
- **R-U7F3-4 evidence 위생.** 내 `20261108-2009-u7fix3-review-baseline.txt` 는 앞부분 무효(§3 비고). 커밋에 넣지 않거나 메인 세션이 지운다(`rm` 1파일). 선례 R-U7F-5(`20261107-1455-u7fix-ruff.txt`)와 같은 종류.

## 5. 판정

**결과: 보류.**
근거: 코드는 위임 범위 안(2파일 +28/−3)이고, 새 지시 문장은 재진술 범위(D16 결정 8)를 넘지 않으며, 카드 줄 변경은 R19 검증기(금지 14개·3줄·240자)와 충돌하지 않음을 실 LLM 4차 trace 572(`answer_source=llm`, `fallback_reason=null`)로 확인했다. 115/2127 passed·ruff·mypy 38=38 을 직접 재실행했고, 변이 1건을 실제로 넣어 2 FAIL 로 잡히는 것과 원복(blob 동일)을 evidence 로 남겼다. 그러나 **사용자 확정 E-6 문장("그대로")과 코드가 어긋난 채 보정 기록이 없다**(R-U7F3-1) — 선례 R-U7F-1 과 같은 문서 보정 2줄이면 닫히고, 그러면 **통과** 로 바꾼다. 제품 코드 수정 0.

한 줄: 코드·테스트·실 LLM 증거는 전부 맞고 변이도 잡히나, 사용자 확정 프롬프트 문장(E-6)을 바꾼 보정 기록이 01-plan·D16 에 없어 보류 — 문서 2줄, 코드 변경 0.

---

## 6. 재리뷰(2026-11-08 20:19) — R-U7F3-1·R-U7F3-2 닫힘 확인

### 6.1 본 것

| 항목 | 확인 |
|---|---|
| 제품 코드 무변경 | `respond.py` blob **`4752e815cf9b…`** — 1차 리뷰 때와 동일(`evidence/20261108-2018-u7fix3-review2-mutation-before.txt`). `git diff --stat -- app` = `respond.py` +8/−1 만. 수정 3 의 코드는 1차 §1 그대로 |
| R-U7F3-1 `01-plan.md` 247행 | "**보정(U7 수정 3, 2026-11-08, review-u7-fix3 R-U7F3-1)**: 실 LLM 3차(`evidence/20261107-1534-u7s-1-relation.txt`)에서 … E-6 문장 '…1~3줄 한국어로 답하고, ' 뒤에 '관계나 위계를 물으면 [인물 카드]의 '관계' 줄을 그대로 답하라 — 그것도 기록된 사실이다. ' 1문장 추가, 카드 줄은 `관계: {relation_tag}·{hierarchy}` → `관계: {서술형}, 위계 {서술형}`(… 사전 밖 값은 원문 그대로). 4차(`…u7t-1-relation.txt`) 답 '직장 관계, 위계 동(같은 급)'. E-5 템플릿 문구는 그대로(… R-U7F3-3). 완성 확인 때 사용자에게 한 줄로 알린다." — 확정 줄(245행) 바로 아래, 코드 159~160·234~235행과 문장·형식 일치. 소견이 요구한 네 요소(문장 원문·카드 줄 변경·evidence 경로·E-5 그대로) + 완성 확인 고지 모두 있음 |
| R-U7F3-1 `D16-query-turn.md` 39행 | "2026-11-08 **보정 ④(P5b U7 수정 3, … R-U7F3-1)**: 코드 규칙 6 '근거는 `get_person_card` 응답에서 온 값뿐' — 프롬프트 카드의 관계·위계 줄은 그 두 값의 **결정적 풀어쓰기**(`respond.py` 사전 5+3 항목, 사전 밖은 원문)로 쓰고, 시스템 문장에 … 1문장을 더했다. 새 사실·다른 출처 없음. 결정 4·5·8 그대로." — 규칙 6 과 코드의 관계를 소견 취지대로 설명. 결정 4·5·8 무변경 선언은 1차 §2 대조와 일치 |
| R-U7F3-2 `tests/test_agent_query_answer.py` 신규 2건(diff +47/−2) | `test_relation_desc_vocab_matches_models` — `set(_RELATION_DESC) == set(RELATION_TAGS)`·`set(_HIERARCHY_DESC) == set(HIERARCHIES)`(`app.db.models` 에서 import; 첫 실행 `app.models` 오타 → 1 failed 가 `evidence/20261108-2016-u7fix3-r2-pytest.txt` 에 남아 있고 `-pytest-rerun.txt` 82 passed). `test_prompt_relation_and_hierarchy_each_value_is_descriptive` — parametrize 8건, 기대값은 **문자열 리터럴**(`"관계: 가족, "` … `", 위계 하(아랫사람)\n"`), `setattr(card.person, field, value)` 로 한 값씩 바꿔 user_text 포함 단언. 사전을 테스트 안에서 다시 계산하지 않으므로 사전 값 변이를 잡는다 |
| 구현자 변이 M3 | `evidence/20261108-2016-u7fix3-r2-mutation.txt`: `_HIERARCHY_DESC["상"]`→`"상"` 에서 `hierarchy-상` 1 FAIL / 81 passed, `-revert-diffstat.txt` 로 원복(+8/−1) — 보고와 일치 |
| `tests.md` 219~224행 | 신규 2행(첫 실행 FAIL 이력 포함) + 변이 M3 행 |
| 변경 파일 범위 | 1차 대비 늘어난 것은 `01-plan.md`·`D16-query-turn.md`(문서 보정)·테스트 1파일. `app/api/`·`web/`·`app/settings.py`·`app/briefing/` 여전히 0 |

### 6.2 직접 실행(evidence `docs/wiki/packages/P5b-query-turn/evidence/`)

| # | 명령 | evidence | 결과 |
|---|---|---|---|
| 1 | `pytest -q tests/test_agent_query_answer.py` | `20261108-2018-u7fix3-review2-pytest-target.txt` | **82 passed**(1차 73 + 신규 9) |
| 2 | `ruff check app/agent/respond.py tests/test_agent_query_answer.py` | `20261108-2018-u7fix3-review2-ruff.txt` | All checks passed |
| 3 | `pytest -q -rs tests/` | `20261108-2019-u7fix3-review2-pytest-all.txt` | **2136 passed**, SKIPPED 0(= 2127 + 9, 예상과 일치) |
| 4a | 변이 전 기준 | `20261108-2018-u7fix3-review2-mutation-before.txt` | blob `4752e815…`, `--stat` 2파일 +55/−3 |
| 4b | **변이 실제 삽입** — 구현자 M3 과 다른 값: 152행 `_RELATION_DESC["가족"]` `"가족"`→`"가족 관계"`(키 집합은 유지 → 어휘 테스트는 통과해야 하고 parametrize 만 잡아야 함) 후 #1 재실행 | `20261108-2018-u7fix3-review2-mutation-run.txt` | **1 failed, 81 passed** — 실패한 것은 정확히 `…each_value_is_descriptive[relation_tag-가족-관계: 가족, ]`(AssertionError `'관계: 가족, ' in '…관계: 가족 관계, 위계 동(같은 급)…'`). `test_relation_desc_vocab_matches_models` 는 통과(키 집합 불변이므로 설계대로) |
| 4c | 원복(Edit) 후 같은 스크립트 + `git diff --stat -- app` | `20261108-2019-u7fix3-review2-mutation-after.txt` | blob **`4752e815…` 동일**, 152~153행 원문, `git diff --stat -- app` = `respond.py` +8/−1 |

### 6.3 소견 상태

| 소견 | 상태 |
|---|---|
| R-U7F3-1 [필수] 01-plan E-6·D16 보정 기록 | **닫힘** — 247행·39행, 코드와 일치, 완성 확인 고지 문장 포함 |
| R-U7F3-2 [권고] 사전 어휘·8값 테스트 | **닫힘** — 키 집합 + 8값 리터럴, 변이 `가족`(검토자)·`상`(구현자) 각 1 FAIL |
| R-U7F3-3 [권고] 템플릿(E-5)·프롬프트 어휘 불일치 | 열림(설계대로) — 01-plan 247행이 "04-review §7·P10 인계" 로 적었다. 사용자 결정 사항 |
| R-U7F3-4 [권고] 무효 evidence `20261108-2009-u7fix3-review-baseline.txt` 삭제 | 열림 — 파일이 아직 있다. 커밋 전 1파일 삭제는 메인 세션 몫 |

### 6.4 판정

**결과: 통과.** [필수] 1건은 제품 코드 변경 없이 문서 2줄로 닫혔고(코드 blob 1차와 동일), 닫힌 것을 82/2136 passed·ruff·변이 1건 검출·원복으로 직접 확인했다. 계획(01-plan 보정)·카드(D16 보정 ④)·코드(159~160·234~235행)·테스트(정확 일치 + 8값 리터럴 + 키 집합) 네 곳이 같은 규칙을 말한다. 열린 [권고] R-U7F3-3·R-U7F3-4 는 커밋을 막지 않는다.

한 줄: E-6 보정 2줄이 들어가고 사전 8값·키 집합이 테스트에 고정돼(변이 `가족`·`상` 각 1 FAIL) 통과 — 제품 코드 변경 0, 남은 것은 무효 evidence 1파일 삭제와 템플릿 어휘 인계.
