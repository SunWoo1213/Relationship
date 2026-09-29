# P6-memory · 완료 검토 (04-review)

날짜: 2026-09-29 | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

> 판정 입력: `docs/backlog.md` P6 첫 항목(권위 문장) · `01-plan.md` 해석 절 ㄱ~ㄹ·판정 표 21행·"지킬 불변식"·"이 패키지에서 하지 않는 것" · `02-plan-verify.md` 승인 줄(232행)과 이월 R-10·R-14·R-15·F-bbf7fa 3단계 · `03-log.md` U1~U8(U8 끝 "메인 세션 독립 재확인·보완" 두 줄 포함) · `evidence/` U1~U8 파일 · `registry.md` · `docs/RUNNING.md` 181~203행 · `review-index.md` R8·R11 행 · `journal.md` 2026-09-29 17:00·17:30·19:50 · `HANDOFF.md` "열린 질문·보류" 절.
> 보고된 수치는 옮기지 않고 **직접 재실행**했다(`evidence/20260929-2024-verifier-recheck.txt`, 이하 "recheck §X"). HEAD = `4916db3`, 미커밋 제품 코드 0(recheck §A).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh P6-memory 2>&1 | tee docs/wiki/packages/P6-memory/evidence/<ts>-verify-impl.txt` — 04-review 작성 **전**(1차)과 **후**(2차) 두 번.

### 1차 — `evidence/20260929-2021-verify-impl.txt` (04-review 없음 → 증거 열 검사는 아직 미수행)
```
== verify-impl P6-memory  (20260929-2021) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1622 passed, 1 warning in 13.78s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20260929-2021-pytest.txt
PASS  compileall 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20260929-2021-lint.txt
PASS  태그 P6-memory 커밋 26 건 → evidence/20260929-2021-commits.txt
PASS  커밋에 태그 존재: CR-002
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D14
PASS  커밋에 태그 존재: D9
PASS  커밋에 태그 존재: R11
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.5
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P6-memory 행 있음
WARN  미완료 작업 단위 6 개
== 결과: FAIL=0 WARN=2 → evidence/20260929-2021-summary.txt ==
```
- WARN 1 "04-review.md 없음" — 이 문서를 쓰기 전이라 정상. 2차에서 사라져야 한다.
- WARN 2 "미완료 작업 단위 6 개" — `01-plan.md` U3~U8 의 체크박스가 `- [ ]` 로 남아 있다(U1·U2 만 `[x]`). 커밋 `51b4d65`·`48e3617`·`b209581`·`8d3967a`·`93c6d3f`·`4916db3` 로 여섯 단위가 실제로 끝났으므로 코드 문제가 아니라 계획 문서의 체크 표시 누락이다. **메인 세션이 01-plan U3~U8 을 `[x]` 로 바꾸면 사라진다**(verifier 는 01-plan 을 고치지 않는다). FAIL 0 이므로 `findings.py` 는 돌리지 않았다.

### 2차 — 04-review 작성 후, `evidence/20260929-2029-verify-impl-2.txt` (증거 열 검사 실제 수행)
```
== verify-impl P6-memory  (20260929-2029) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1622 passed, 1 warning in 12.93s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20260929-2029-pytest.txt
PASS  compileall 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20260929-2029-lint.txt
PASS  태그 P6-memory 커밋 26 건 → evidence/20260929-2029-commits.txt
PASS  커밋에 태그 존재: CR-002
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D14
PASS  커밋에 태그 존재: D9
PASS  커밋에 태그 존재: R11
PASS  커밋에 태그 존재: R8
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.5
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pat ← evidence/20260929-2024-verifier-recheck.
PASS  증거 확인:  ㄱ "승격 후" = 같은 인물의 미승격 이벤트가 5건 이상일 때 승격이 한 번 돈 뒤 ( ← evidence/20260929-1457-u5-promote.txt (판
PASS  증거 확인:  ㄴ "사실→원문 링크 존재" = 승격이 만들거나 갱신한 `person_facts` 행 전 ← evidence/20260929-1457-u5-promote.txt (1
PASS  증거 확인:  ㄷ "설정된 기간·횟수 규칙(기본 365일 3회)" = 같은 인물·같은 type·`occ ← evidence/20260929-0116-u2-patterns.txt (
PASS  증거 확인:  ㄹ "`pattern:{type}` 사실 생성" = `key="pattern:<type> ← evidence/20260929-0116-u2-patterns.txt (
PASS  증거 확인:  (계획 내 보조 기준) 판정 표 19·20·21행 — 불변식 grep·`alembic c ← evidence/20260929-2001-u8-invariants.txt
PASS  증거 확인:  (02-plan-verify 이월) F-bbf7fa 3단계 `.env.example` 설 ← evidence/20260929-2024-verifier-recheck.
PASS  registry 에 P6-memory 행 있음
WARN  미완료 작업 단위 6 개
== 결과: FAIL=0 WARN=1 → evidence/20260929-2029-summary.txt ==
```
- 1차 WARN "04-review.md 없음" 은 사라졌고 §2 증거 7행 전부 `PASS 증거 확인`. 남은 WARN 1 은 1차와 같은 01-plan 체크박스 표기(§6 [권고])다. FAIL 0 → `findings.py` 미실행, 새 소견 없음.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

backlog 문장(권위): **"승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pattern:{type}` 사실 생성"** — 01-plan 76행과 글자 그대로 같다(02-plan-verify 점검표 6행 통과). 아래 ㄱ~ㄹ 은 01-plan "해석" 절(80~87행)의 네 조각을 그대로 옮긴 것이고, 각 행의 정의를 계획에서 읽어 그 정의가 충족됨을 증거로 보였다.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pattern:{type}` 사실 생성 (전체 문장) | evidence/20260929-2024-verifier-recheck.txt §B·§H 1622 passed skip 0, evidence/20260929-2001-u8-acceptance.txt 21행 분류표, 커밋 7564c5d d67d084 51b4d65 48e3617 b209581 8d3967a 93c6d3f 4916db3 | 통과 |
| ㄱ "승격 후" = 같은 인물의 미승격 이벤트가 5건 이상일 때 승격이 한 번 돈 뒤 (01-plan 83행) | evidence/20260929-1457-u5-promote.txt (판정 10·11·12행: `test_promote_person_five_unpromoted_events_creates_facts_with_source_links` 5건→추출기 1회, `..._four_unpromoted_events_does_not_trigger` 4건→0회, `..._does_not_recount_already_considered_events` 재승격 0회), evidence/20260929-2024-verifier-recheck.txt §C·§D-2 (`MEMORY_PROMOTE_MIN_EVENTS=4` 로 바꾸면 4건-미트리거 테스트가 실제로 FAILED — 테스트가 임계치를 검사한다는 증거), app/memory/promote.py, 커밋 b209581 | 통과 |
| ㄴ "사실→원문 링크 존재" = 승격이 만들거나 갱신한 `person_facts` 행 전부가 `fact_sources` 로 ≥1 `events` 행에 이어지고 그 이벤트는 같은 인물의 것이며 `raw_utterance` 가 그대로 (01-plan 84행) | evidence/20260929-1457-u5-promote.txt (10행 테스트: `_linked_event_ids(hobby)=={ids[0],ids[1]}`·`job=={ids[2]}` — 링크 = 추출기가 가리킨 id, `after == before` 로 content·raw_utterance 불변; D-6 두 갈래 `..._upsert_same_value_only_adds_link`·`..._different_value_overwrites_and_replaces_links`), evidence/20260929-1928-u7-direct-facts.txt (결정 G(ii) 루프 직접 사실도 같은 턴 이벤트에 링크), evidence/20260929-2024-verifier-recheck.txt §E grep 1 = 0건 (Event 삭제·수정 코드 없음), 커밋 b209581 93c6d3f | 통과 |
| ㄷ "설정된 기간·횟수 규칙(기본 365일 3회)" = 같은 인물·같은 type·`occurred_at ∈ [now−PATTERN_WINDOW_DAYS일, now]` 이벤트가 `PATTERN_MIN_COUNT` 건 이상(기본 365·3), 실제 쓴 값을 `memory_pattern` output `window_days`·`min_count` 에 기록, 판정은 코드 규칙·LLM 0회 (01-plan 85행) | evidence/20260929-0116-u2-patterns.txt (판정 1~8행), evidence/20260929-2024-verifier-recheck.txt §C (`..._window_boundary_exclusive_one_second_early`·`..._excludes_future_occurred_at`·`..._does_not_mix_persons`·`..._does_not_mix_types`·`test_patterns_module_does_not_import_llm_or_embedding_modules` 전부 PASSED) ·§D-1 (`PATTERN_MIN_COUNT=2` 면 2건-무패턴 테스트가 FAILED) ·§D-3 (`PATTERN_WINDOW_DAYS=400` 이면 창 경계 테스트가 FAILED — 창·횟수를 실제로 검사) ·§E grep 3종 (0건·기준선 1건·0건), evidence/20260929-1622-u6-loop.txt (판정 9행 `memory_pattern` tokens 0/0·추출기 0회), app/settings.py, 커밋 7564c5d d67d084 | 통과 |
| ㄹ "`pattern:{type}` 사실 생성" = `key="pattern:<type>"`·`value="{n}회 (날짜 목록)"`·`confidence=1.0` 행이 생기고 창 안 이벤트 n건 전부가 `fact_sources` 로 이어짐 (01-plan 86행) | evidence/20260929-0116-u2-patterns.txt (1행 `test_detect_patterns_three_events_creates_pattern_fact` 1행·1.0·"3회 (…)"·링크 3, 7행 같은 id 로 "4회"·링크 4, 8행 미달 시 삭제·CASCADE·이벤트 보존·previous_value), evidence/20260929-1622-u6-loop.txt (17행 재개 경로·18행 `POST /chat` 3회 뒤 `pattern:conflict` + 링크 3), evidence/20260929-1404-u3-key-guard.txt 와 evidence/20260929-2024-verifier-recheck.txt §B (`update_person` 이 `pattern:` 접두 키를 11종 변형 전부 `InvalidValue` — 계획 15행 예시 `" Pattern:meal "` 포함), app/memory/patterns.py, 커밋 d67d084 51b4d65 | 통과 |
| (계획 내 보조 기준) 판정 표 19·20·21행 — 불변식 grep·`alembic check`·`tools_check` 7/7·전체 회귀 skip 0 | evidence/20260929-2001-u8-invariants.txt, evidence/20260929-2001-u8-regression.txt, evidence/20260929-2024-verifier-recheck.txt §E·§F·§H ("No new upgrade operations detected." / "RESULT: 7/7 ok" / 1622 passed skip 0), evidence/20260929-2021-pytest.txt | 통과 |
| (02-plan-verify 이월) F-bbf7fa 3단계 `.env.example` 설정 줄 3건 · R-10 추출기 지연 해소 · R-14/R-15 `min_events` 를 trace 와 결정 F 에 기록 | evidence/20260929-2024-verifier-recheck.txt §G (58·59·61행 3건, 값 비어 있음) ·§C (`test_after_record_does_not_resolve_extractor_from_env_when_trigger_not_met` PASSED = R-10), evidence/20260929-1457-u5-promote.txt (`..._trace_records_min_events_from_env_override` = R-14), docs/wiki/packages/P6-memory/01-plan.md (186행 결정 F output 에 `min_events` = R-15), 커밋 7564c5d 8d3967a b209581 | 통과 |

### 판정 표 8행 "이벤트 4건 그대로" — 독립 판정 (메인 세션이 남긴 미해결 1건)

- **원문**(recheck §J): 01-plan 101행 `| 7 | 갱신 | 3건 → 4번째 추가 | 같은 행(id 불변) value "4회 …", 링크 4 |`, 102행 `| 8 | 미달 처리 | 시계를 옮겨 창 안 2건 | 결정 C-5 대로(권장: 행 삭제·링크 CASCADE·이벤트 4건 그대로) + trace 에 이전 value |`. 결정 C-5(165행) `(i) 패턴 사실 행 삭제(링크는 FK CASCADE, 이벤트는 그대로), trace 에 이전 value 를 남긴다`.
- **테스트**(`tests/test_memory_patterns.py::test_detect_patterns_deletes_fact_when_count_falls_below_threshold`, 488~538행, 직접 읽음): 이벤트 3건(now−350일·−200일·−50일) → 패턴 생성 → 시계를 +20일 옮겨 가장 오래된 1건이 창 밖 → 단언 4개: `_pattern_fact(...) is None`(행 삭제), `FactSource` 집합 `== set()`(CASCADE), trace `changes[]` 에 `action=="deleted"`·`previous_value == 이전 value`·`fact_id` 일치, `Event.id in remaining_ids` 집합 보존(이벤트 그대로).
- **판정: 계획 표 문구의 표기 문제이지 미달이 아니다.** 근거 ① 8행의 "4건" 은 7행(3건→4번째 추가) 상태를 이어 쓴 숫자이고, 8행 케이스 열 자체는 "시계를 옮겨 창 안 2건" 만 요구한다 — 테스트는 시계를 옮겨 창 안 2건을 만든다(케이스 열 충족). ② 기대 열의 권위는 "결정 C-5 대로 + trace 이전 value" 이고, C-5(i) 원문은 이벤트 개수를 정하지 않는다("이벤트는 그대로"). ③ 해석 절 ㄷ·ㄹ 어디에도 4건 요구가 없다. ④ 검증되는 네 성질(삭제·CASCADE·원문 보존·이전 value)은 이벤트 총수 3이든 4든 같은 코드 경로를 지난다 — 4건이면 "창 밖으로 2건이 나가는" 경우가 되지만 C-5 는 "기준 횟수 미만으로 떨어지면" 이라는 조건만 두므로 1건이 나가 2건이 남는 것도 같은 조건이다. ⑤ 메인 세션이 4건 시나리오를 덧붙이지 않고 그대로 둔 것은 02-plan-verify 가 승인한 계획을 사후에 고치지 않는다는 규칙에도 맞다. 따라서 메인 세션의 "오기" 판단에 동의한다. 남기는 것: [권고] 다음 패키지 계획부터 판정 표의 케이스 열이 앞 행 상태를 잇는지 독립인지 적는다(§6).

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
전부 verifier 가 직접 실행 — `evidence/20260929-2024-verifier-recheck.txt`. §D 세 건은 **테스트가 항상 통과하는 테스트가 아님**을 보이기 위해 설정을 일부러 어긋나게 주어 FAILED 가 나는 것을 확인한 것이다(원칙8 — 실패 조건을 실제로 검사한다는 증거).

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 2건이면 패턴이 생기지 않는다(판정 2행) | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -v tests/test_memory_patterns.py::test_detect_patterns_two_events_no_pattern` | recheck §C PASSED · §D-1 `PATTERN_MIN_COUNT=2` 로 같은 테스트 → `AssertionError: assert <PersonFact> is None`, 1 failed(테스트가 횟수 임계를 실제로 본다) |
| `now−365일−1초` 는 창 밖(3행) · 미래 `occurred_at` 제외(4행) | `… ::test_detect_patterns_window_boundary_exclusive_one_second_early` · `… ::test_detect_patterns_excludes_future_occurred_at` | recheck §C PASSED · §D-3 `PATTERN_WINDOW_DAYS=400` 로 → `assert 3 == 2` 1 failed(창 길이를 실제로 본다) |
| 인물·type 을 섞어 세지 않는다(5·6행) | `… ::test_detect_patterns_does_not_mix_persons` · `… ::test_detect_patterns_does_not_mix_types` | recheck §C PASSED |
| 다른 `user_id` 의 인물 id → `PersonNotFound`, 패턴 0·추출기 0회(security §5) | `… ::test_detect_patterns_other_users_person_raises_person_not_found` · `tests/test_memory_promote.py::test_promote_person_other_users_person_raises_person_not_found_without_calling_extractor` | recheck §C PASSED |
| 미승격 4건이면 추출기를 부르지 않는다(11행) · 이미 본 이벤트를 다시 승격하지 않는다(12행) · 미달 호출이 이벤트를 영구 미승격으로 만들지 않는다(U5 ★3) · 다른 `session_id` 의 승격 기록도 본다 | `tests/test_memory_promote.py::test_promote_person_four_unpromoted_events_does_not_trigger` · `…_does_not_recount_already_considered_events` · `…_unpromoted_events_are_not_lost_when_trigger_not_yet_met` · `…_ignores_session_id_when_counting_considered_events` | recheck §C PASSED · §D-2 `MEMORY_PROMOTE_MIN_EVENTS=4` 로 4건 테스트 → `assert PromotionResult(... min_events=4, considered_event_ids=[4개] ...) is None` 1 failed(임계치를 실제로 본다) |
| 추출기가 `pattern:meal`·어휘 밖 키·입력에 없는 이벤트 id·빈 값을 내면 그 사실만 거부(14행) | `tests/test_memory_promote.py::test_promote_person_rejects_invalid_facts_but_keeps_valid_ones` + `tests/test_memory_extract.py -k "rejects_"` | recheck §C PASSED · evidence/20260929-2001-u8-acceptance.txt (extract 쪽 10 passed) |
| `update_person(facts=[{"key":" Pattern:meal "}])` → `InvalidValue`, 행 0, 같이 넣은 정상 키도 저장되지 않음(15행) | `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_tools_persons.py -k pattern -v` | recheck §B 11 passed(`[ Pattern:meal ]` 파라미터 포함 — 메인 세션 보완분 `4916db3`) |
| 추출기 `timeout` 이면 턴 200·이벤트 5건 보존·`memory_error` 1행·사실 0·안쪽 `memory_pattern`/`memory_promote` 행 없음(16행) | `tests/test_memory_loop.py::test_extractor_failure_is_isolated_event_survives_and_memory_error_is_recorded` | recheck §C PASSED · 테스트 본문 직접 읽음(`error_rows[0].output == {person_id, stage:"promote", error:"JudgeUnavailable"}`, 롤백된 중간 trace 0행 단언) · `app/memory/hooks.py` 185~205행 `begin_nested()` 밖에서 `_record_memory_error` 호출 확인 |
| 트리거 미달 턴은 `extractor_from_env()` 를 아예 부르지 않는다(R-10) · 패턴만 생기는 턴은 추출기 0회·tokens 0/0(9행) | `tests/test_memory_loop.py::test_after_record_does_not_resolve_extractor_from_env_when_trigger_not_met` · `…::test_pattern_only_turn_never_calls_extractor_and_has_zero_tokens` | recheck §C PASSED · evidence/20260929-1622-u6-loop.txt(회귀 4파일 36건이 API 키 없이 통과) |
| U7 직접 링크가 승격의 미승격 판정을 오염시키지 않는다 · 실패한 `update_person` 의 키는 수집되지 않는다 | `tests/test_memory_loop.py::test_direct_fact_link_does_not_disturb_promotion_links_in_same_turn` · `…::test_direct_fact_failed_update_person_call_is_not_collected` | recheck §C PASSED · `app/memory/promote.py` 110~128행 `_considered_event_ids` 가 `output.get("considered_event_ids") or []` 로 읽고 `DirectFactLinkResult.to_dict()`(`app/memory/types.py` 309~312행)는 그 키를 내지 않음(직접 읽음) |
| 원문(`events`) 삭제·수정 코드 없음 · `app/agent/` 금지 리터럴 기준선 · "evaluation" 0건(19행) | 01-plan "지킬 불변식" 절 grep 3종 그대로 | recheck §E: 0건(exit 1) · `app/agent/loop.py:1352` 1건(기준선 `evidence/20260928-1350-verifier-fact-checks.txt` §6 의 같은 `create_person(` 호출) · 0건(exit 1) |
| 스키마·툴 시그니처 무변경(20행) | `.venv/bin/python -m alembic check` · `.venv/bin/python scripts/tools_check.py` | recheck §F "No new upgrade operations detected." · "RESULT: 7/7 ok" |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- **아직 바꾸지 않았다**(review-index 는 메인 세션 몫). 현재 상태(직접 grep): R8 행 16 `구현완료(4dfaf33, 09c2bd1 — fact_sources … P6-memory 가 승격 시 채움)`, R11 행 19 `결정완료(CR-002: D9→D14, 기본 365일·3회 설정값)`.
- 바꿔야 할 내용:
  - **R8** → `구현완료(4dfaf33, 09c2bd1 테이블 · b209581 승격이 fact_sources 채움 · 93c6d3f 루프 직접 사실도 링크 · d67d084 패턴 링크)`. 근거: §2 ㄴ 행, `evidence/20260929-1457-u5-promote.txt`, `evidence/20260929-1928-u7-direct-facts.txt`.
  - **R11** → `구현완료(d67d084 규칙 감지 · 8d3967a 턴마다 자동 실행 · CR-002/D14 기본 365일·3회 설정값)`. 근거: §2 ㄷ·ㄹ 행, `evidence/20260929-0116-u2-patterns.txt`, `evidence/20260929-1622-u6-loop.txt`.
- 관련 카드 상태: D14 "적용은 P6-memory" → 적용 완료 표시 대상. S3.5 네 문장 전부 코드로 옮겨짐(승격 트리거·승격 동작·패턴·원문 불변). D9 는 D14 로 대체된 상태 그대로.

## 5. registry.md 에 올린 산출물
- **올라간 것**(직접 grep, 커밋 `4916db3`): 새 모듈 6행 — 176 `app/memory/types.py`(7564c5d) · 177 `patterns.py`(d67d084) · 178 `extract.py`(48e3617) · 179 `promote.py`(b209581) · 180 `hooks.py`(8d3967a) · 181 `direct_facts.py`(93c6d3f); 테스트 4행 — 182 `test_memory_patterns.py` · 183 `test_memory_extract.py` · 184 `test_memory_promote.py` · 185 `test_memory_loop.py`; 59행 `app/tools/records.py` 비고에 "트리거 없음은 더 이상 사실이 아니다" 확장. `verify-impl.sh` `PASS registry 에 P6-memory 행 있음`.
- **빠진 것 — 메인 세션이 보탤 것**(01-plan 산출물 표 "고치는 기존 파일 … 새 행이 아니라 비고 확장" 에 해당하는데 해당 행 53·58·64·65·72·165 어디에도 `P6` 문자열이 없다, 직접 grep 0건):
  - 53 `app/settings.py` — `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`MEMORY_PROMOTE_MIN_EVENTS`(환경변수)·`PATTERN_KEY_PREFIX`·`MEMORY_PROMOTE_MAX_EVENTS`·`MEMORY_MAX_FACTS`(코드 상수)·`pattern_config()`·`promote_min_events()` (7564c5d)
  - 58 `app/tools/persons.py` — `update_person` 이 `pattern:` 접두 키(공백·대소문자 변형 포함)를 `InvalidValue` 로 거부, 검증 뒤 upsert 두 단계(부분 반영 금지) (51b4d65)
  - 165 `app/agent/loop.py` — `RecordOutcome.event_person_ids`·`event_ids_by_person`·`fact_keys_by_person`, `_record()` 가 `loop_record` 뒤 `after_record()` 호출, `run_turn`/`resume_turn` `extractor=None` 키워드 (8d3967a, 93c6d3f)
  - 64 `app/api/deps.py` — `get_fact_extractor()` (8d3967a) · 65/167 `app/api/routes.py` — `/chat`·`/answers/{id}` 가 `extractor` 주입 (8d3967a)
  - 72 `tests/test_tools_persons.py` — `-k pattern` 11건 (51b4d65, 4916db3)
  - `.env.example` 행(38행, 하네스 소유) — 설정 이름 3줄 추가 (7564c5d)
- 계획 대비 파일 구성 차이(문제 아님, 기록만): 01-plan 은 `after_record()` 를 `promote.py` 에 두기로 했으나 구현은 `hooks.py`(U6)·`direct_facts.py`(U7) 두 파일을 더 만들었다. 03-log U6·U7 과 registry 180·181행에 근거가 있고 진입점은 여전히 하나(`after_record`)다.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
`05-remediation.md` 열린 소견 0(필수 0, 해소 6). `verify-impl.sh` FAIL 0. **[필수] 소견 없음.** 아래는 전부 [권고] 이거나 범위 밖 별건이며, 수용 기준 미달로 분류한 것은 없다.

- **[권고] 01-plan U3~U8 체크박스** — `- [ ]` 6개가 남아 `verify-impl.sh` WARN 1건. 메인 세션이 `[x]` 로(문서만).
- **[권고] registry 비고 확장 누락** — §5 "빠진 것" 6곳. 새 모듈·테스트는 등록됐으므로 FAIL 은 아니나, 01-plan 이 스스로 정한 "비고 확장" 이 안 됐고 다음 패키지가 `settings.py`·`loop.py` 를 grep 할 때 P6 변경을 못 본다.
- **[권고] 판정 표 8행 문구** — §2 하단 판정대로 미달 아님. 다음 계획부터 판정 표 케이스 열이 앞 행 상태를 잇는지 독립인지 적는다(architect 몫, L-후보).
- **[권고] `memory_promote` 세 종류의 구분 키가 비대칭이다** — (메인 세션 질문 5) 판정: **결정 F 와 어긋남은 사실이나 정당하고 기록돼 있다.** 결정 F 원문 "트리거가 걸렸을 때만 1행" 은 같은 결정 F 의 "미달 이유는 `memory_pattern` 에" 와 함께 U2 커밋 시점에 이미 모순이었다(패턴 모듈은 승격 이력을 모르며 `test_patterns_module_does_not_import_llm_or_embedding_modules` 가 원칙6 격리를 강제). U5 가 "호출마다 1행 + 미달 행은 `considered_event_ids=[]`" 로 푼 것은 원칙9(왜 승격하지 않았나 남김)에 맞고, 취소선·※ 로 01-plan 186행에, ★ 세 판단으로 03-log U5 에, `test_promote_person_non_trigger_trace_records_reason_and_empty_considered` 로 테스트에 남았다. U7 이 `memory_promote` step 을 재사용한 것도 01-plan 73행("`memory_*` trace 에 `unlinked`", 새 step 없음) 안이다. 실 데이터(journal 17:30·19:50)에서 미달 행이 이벤트를 소실시키지 않고 직접 링크 행이 미승격 판정을 오염시키지 않음이 확인됐다. **남는 문제 하나**: `docs/RUNNING.md` 200행이 "`output.source` 를 봐야 한다" 고 적었지만 실제로 `source` 키는 직접 링크 행(`"direct"`)에만 있고(recheck §L — `types.py` 312행 한 곳), LLM 승격 행과 미달 행은 `source` 가 없어 `considered_event_ids` 가 비었는지 또는 `llm`/`facts` 키로 구분해야 한다. 운영자가 `source` 로 필터하면 승격 행과 미달 행을 못 가른다. 조치 후보(코드 한 줄·FIX 후보): `PromotionResult.to_dict()` 에 `source: "llm"`(트리거) / `"skipped"`(미달) 를 넣어 세 종류가 같은 키로 갈리게 한다. 이 패키지 수용 기준 밖이므로 [권고].

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
**인터페이스·설정값**
- `app.memory.after_record(ctx, person_ids, extractor=None, *, fact_keys_by_person=None, event_ids_by_person=None)` — 루프 `_record()` 뒤 한 자리에서만 부른다. `detect_patterns(ctx, person_id) -> PatternResult` 는 순수 SQL·LLM 0 — **P6-briefing 이 브리핑 직전에 다시 부른다**(결정 C-5 한계: 새 이벤트 없이 시간만 흐르면 패턴이 낡는다).
- `person_facts` 에는 세 출처의 사실이 섞여 있다: `pattern:*`(규칙, confidence 1.0, value `"{n}회 (날짜…)"`) · 승격 사실(`FACT_KEYS` 9키, confidence `DEFAULT_FACT_CONFIDENCE`) · 루프 직접 사실(자유 키). **P8 인물 카드의 "원문 펼치기" 는 `fact_sources → events.raw_utterance`** 로 조회한다(조회 API 는 이 패키지가 만들지 않았다).
- 환경변수 3개 `PATTERN_WINDOW_DAYS`(365)·`PATTERN_MIN_COUNT`(3)·`MEMORY_PROMOTE_MIN_EVENTS`(5), 코드 상수 3개 `MEMORY_PROMOTE_MAX_EVENTS`(20)·`MEMORY_MAX_FACTS`(8)·`PATTERN_KEY_PREFIX`. 앱 안 사용자별 선택은 backlog P8 CR 항목.
- trace: `tool_name="memory"`, step `memory_pattern`(tokens 0)·`memory_promote`(세 종류 — §6 권고)·`memory_error`(`{person_id, stage ∈ pattern/promote/direct_fact, error}`). 미승격 판정은 `agent_traces` 를 상태로 쓴다(결정 B(ii)) — **trace 를 지우면 승격이 다시 돈다.**

**메인 세션이 물은 5개 항목의 분류 (미달 / 범위 밖)**
1. **사실 키 중복**(`소속`·`직장`·`workplace` = 네이버) — **범위 밖 별건, 미달 아님.** 결정 D-5(01-plan 174행)는 "한계: P5 루프의 `update_person` 직접 사실은 여전히 자유 키다 — 이 패키지에서 바꾸지 않고 리스크에 남긴다", 리스크 절 212행 "루프 제안 스키마에 같은 enum 을 거는 것은 P5 행동 변경이라 이 패키지에서 하지 않는다" 로 **D-5 는 승격만 구속한다**고 계획이 명시했고 사용자가 그 계획을 승인했다(02-plan-verify 232행). 수용 기준 ㄴ 은 "승격이 만든 사실" 의 링크를 묻는다. 그러나 **제품 결함으로서는 실재**하고(journal 19:50) 브리핑·카드가 중복을 그대로 보여준다 → **P6-briefing·P8 착수 전에 FIX 또는 CR 로 사용자 결정 필요**. 손볼 자리는 `app/agent/propose.py` 145행 `facts.key`(enum 없음, `type`·`relation_tag`·`hierarchy` 는 이미 enum) 또는 게이트/`update_person` 의 어휘 검사 — 어느 쪽이든 P5-loop 행동 변경.
2. **루프가 쓴 사실의 어휘 미통제** — 1과 같은 뿌리, **범위 밖**(계획대로 U3 는 `pattern:` 만 막는다, 01-plan 21행). 1의 FIX/CR 에 합친다.
3. **추출 품질**(회사명이 `job` 에) — **범위 밖**, 01-plan 206행 "추출 품질은 측정되지 않는다 … P10-final-eval 로 인계" 와 "하지 않는 것" 절 "추출 품질 지표 … (P10-final-eval)". `build_extract_prompt()` 의 키 설명 손질은 P10 측정 뒤.
4. **`/health` 가 테이블 없는 DB 를 `status: ok`·`db: up` 으로 보고** — **범위 밖**, 이 패키지가 만든 결함이 아니다(`app/api/routes.py` `/health` 는 P2-tools `4d5817e`, registry 65행). 실서버 확인(journal 17:00)에서 드러난 기존 결함 → **FIX 후보**(`alembic_version` 이 비었으면 `db: "no_schema"` 등으로 503 또는 경고).
5. **`memory_promote` 세 종류** — **범위 안·미달 아님·정당함**, 남는 것은 §6 [권고]("`source` 키 비대칭") 하나.

**추가로 넘기는 기존 결함(HANDOFF "열린 질문·보류" 에 이미 있음, 이 패키지 밖)**
- `update_person` 의 인자 간 부분 반영 — `display_name`·`new_alias` 가 `facts` 검증보다 앞에서 적용돼 `InvalidValue` 실패 호출이 이름 변경을 남긴다(`app/tools/persons.py`, U3 발견). FIX 후보.
- 동시 요청 시 `person_facts(person_id, key)` 유일 제약 없음(01-plan 리스크) — 단일 사용자 전제, 스키마 변경은 CR.

결과: 완료
승인: 사용자 (2026-09-29)

### 승인 뒤 메인 세션이 처리한 것 (§6 [권고] 4건)
- **[권고] 01-plan U3~U8 체크박스** — `[x]` 로 바꿨다. `verify-impl.sh` WARN "미완료 작업 단위 6 개" 해소.
- **[권고] registry 비고 확장 6곳** — §5 "빠진 것" 을 전부 채웠다: 38행 `.env.example`(설정 3줄) · 53행 `app/settings.py`(설정 6개·읽는 함수 2개) · 58행 `app/tools/persons.py`(`pattern:` 거부·부분 반영 금지) · 64행 `app/api/deps.py`(`get_fact_extractor()`) · 65행 `app/api/routes.py`(extractor 주입 + `/health` 결함 메모) · 72행 `tests/test_tools_persons.py`(`-k pattern` 11건) · 165행 `app/agent/loop.py`(`RecordOutcome` 3필드·`after_record` 호출 자리).
- **[권고] `memory_promote` 의 `source` 키 비대칭** — 코드는 그대로 두고(별건 FIX 후보), **사실과 달랐던 `docs/RUNNING.md` 202행을 고쳤다**: "`source` 를 봐야 한다" → 세 종류 구분 표 + "승격 횟수 = `considered_event_ids` 가 비어 있지 않은 행의 수". 문서가 틀린 채로 남는 것은 원칙8·사실성 규칙에 어긋나므로 이 패키지 안에서 닫았다.
- **[권고] 판정 표 8행 문구** — 계획을 사후에 고치지 않는다는 규칙대로 01-plan 은 손대지 않았다. "판정 표 케이스 열이 앞 행 상태를 잇는지 독립인지 적는다" 는 다음 계획부터의 architect 몫(L-후보)으로 §7 에 남긴다.

### 승인 뒤 남기는 것
- `review-index.md` R8 → `구현완료(… b209581 · 93c6d3f · d67d084)`, R11 → `구현완료(d67d084 · 8d3967a)` 로 바꿨다.
- `docs/backlog.md` P6 첫 항목 체크박스 `[x]`.
- **다음 작업(사용자 결정, 2026-09-29)**: 사실 키 중복(§7-1·§7-2) 을 FIX 로 할지 CR 로 할지 정하는 것부터 한다.
