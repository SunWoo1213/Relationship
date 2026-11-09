# P5b-query-turn · 완료 검토 (04-review)

날짜: 2026-11-08 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)·메인 세션과 다른 모델·컨텍스트(L-002)

대상: 브랜치 `dev2` HEAD `cf26dce`. 기준 해시(패키지 시작 전) `8a8767b`. 단위 커밋 U1 `1dccb95` · U2 `06b7bb5` · U3 `a002706` · U4 `18219ba` · U5 `49c1c67` · U6 `a004cdd` · U7 결함 수정 `e49f78d` · U7 수정 3 `cf26dce`(사이의 `be67c76`·`9eb9d2e` 는 하네스 커밋, 제품 코드 무관 — `evidence/20261108-2026-commits.txt`). 읽은 것: `01-plan.md`(수용 기준·판정 표 D-1~D-7/A-1~A-5/R-1~R-8/H-1·결정 A~L·보정 2건) · `docs/backlog.md` 75행 · `02-plan-verify.md`(결과 통과) · `03-log.md` 전문 · `tests.md` · `review-u1~u6-*.md`·`review-u7-fix.md`·`review-u7-fix3.md` · `docs/wiki/decisions/D16-query-turn.md`(결정 1~10·코드 규칙 7문장·보정 ①~④) · `docs/wiki/review-index.md` 27행(R19) · `docs/wiki/registry.md` 56·164~177행 · `app/er/confidence.py` 286~306행(결정3-c(b) 규약) · 코드 `app/agent/loop.py` 1236~1460행·`app/agent/respond.py` 150~320행·`app/agent/gate.py` Q 관문. 판정 명령은 전부 **내가 직접 실행**해 `save_evidence.py` 로 `evidence/20261108-20xx-verifier-04-*.txt` 에 남겼다(래퍼가 공백 포함 인자를 쪼개 1회차가 `exit 4 no tests ran`·`command not found`·`No module named 'app'` 로 깨진 행은 스크래치패드 스크립트로 재실행 — `*-rerun.txt`·`*-greps.txt` 가 유효본, 깨진 1회차 파일은 이력으로 남긴다).

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `python3 .claude/scripts/save_evidence.py P5b-query-turn verifier-04-verify-impl -- POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P5b-query-turn` (FIX-034 — `tee` 대신 save_evidence)

### 1-1. 작성 전 1회 — `evidence/20261108-2026-verifier-04-verify-impl.txt`
```
# 명령: POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P5b-query-turn
# 시각: 2026-11-08T20:26:22+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: cf26dce (dev2)
# exit: 0
# ---
== verify-impl P5b-query-turn  (20261108-2026) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2136 passed, 1 warning in 24.37s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261108-2026-pytest.txt
WARN  ruff 경고/오류 → evidence/20261108-2026-lint.txt
PASS  태그 P5b-query-turn 커밋 11 건 → evidence/20261108-2026-commits.txt
PASS  커밋에 태그 존재: CR-004
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D16
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: FIX-021
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.6
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P5b-query-turn 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=2 → evidence/20261108-2026-summary.txt ==
```
- WARN 1 `ruff` — `ruff check .`(저장소 전체) 가 `.claude/scripts/bash_write_check.py:1228 B007`·`.claude/scripts/findings.py:129·130 DTZ005` 를 낸다(`evidence/20261108-2026-lint.txt`). 전부 하네스 스크립트의 기존 경고이고 이 패키지 diff 와 무관하다(판정 A-5 `ruff check app tests` 는 `All checks passed!` — `evidence/20261108-2029-verifier-04-A-5-ruff.txt`). P7-push 04-review 와 같은 종류의 이관 WARN.
- WARN 2 는 이 문서가 없을 때의 정상 경고. 아래 1-2 가 이 문서를 쓴 뒤의 재실행.

### 1-2. 작성 뒤 재실행(최종) — `evidence/20261109-0051-verifier-04-verify-impl-final2.txt`
(1회차 재실행 `evidence/20261108-2040-verifier-04-verify-impl-final.txt` 는 §2 안에 둔 H-1 발화별 표 7행을 스크립트가 수용 기준 행으로 세어 FAIL 8 — 표를 §2-1 로 옮긴 뒤 다시 돌린 것이 아래다. 코드·evidence 변경 없음.)
```
# 명령: POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P5b-query-turn
# 시각: 2026-11-09T00:51:27+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: cf26dce (dev2)
# exit: 0
# ---
== verify-impl P5b-query-turn  (20261109-0051) ==

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2136 passed, 1 warning in 24.15s
PASS  pytest 통과(/Users/sunwoo/Desktop/Portfolio/Relationship/.venv/bin/python) → evidence/20261109-0051-pytest.txt
WARN  ruff 경고/오류 → evidence/20261109-0051-lint.txt
PASS  태그 P5b-query-turn 커밋 11 건 → evidence/20261109-0051-commits.txt
PASS  커밋에 태그 존재: CR-004
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D16
PASS  커밋에 태그 존재: D2
PASS  커밋에 태그 존재: FIX-021
PASS  커밋에 태그 존재: R19
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.4
PASS  커밋에 태그 존재: S3.6
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 ← evidence/20261108-2026-verifier-04-verif
PASS  증거 확인:  D-1 · D16 "`propose.py` 구조화 출력 스키마에 `intent` enum ← evidence/20261108-2031-verifier-04-D-1a-
PASS  증거 확인:  D-2 · D16 "`gate.py` 는 `intent == "query"` 턴의 기록  ← evidence/20261108-2033-verifier-04-D-2-r
PASS  증거 확인:  D-3 · D16 "`loop.py` 조회 분기는 `app.er.resolve`/`app ← evidence/20261108-2031-verifier-04-D-3a-
PASS  증거 확인:  D-4 · D16 "조회 턴에 `add_event`·`add_schedule`·`upda ← evidence/20261108-2030-verifier-04-D-4.t
PASS  증거 확인:  D-5 · D16 "`new_person` 구간의 조회 턴은 `pending_questi ← evidence/20261108-2033-verifier-04-D-5-r
PASS  증거 확인:  D-6 · D16 "답 생성 프롬프트에 들어가는 근거는 `get_person_card`  ← evidence/20261108-2033-verifier-04-D-6a-
PASS  증거 확인:  D-7 · D16 "프론트(`web/`) diff 0."  ← evidence/20261108-2029-verifier-04-D-7.t
PASS  증거 확인:  A-1 · "조회 턴 저장 0(`events`·`schedules`·`person_fac ← evidence/20261108-2030-verifier-04-A-1.t
PASS  증거 확인:  A-2 · "툴 7종 불변(`tools_check` 7/7)"  ← evidence/20261108-2029-verifier-04-D-3b-
PASS  증거 확인:  A-3 · "trace 에 의도·해석·조회 근거 건수·답"  ← evidence/20261108-2030-verifier-04-A-3.t
PASS  증거 확인:  A-4 · "pytest 통과"  ← evidence/20261108-2027-verifier-04-A-4-p
PASS  증거 확인:  A-5 · 린트  ← evidence/20261108-2029-verifier-04-A-5-r
PASS  증거 확인:  R-1 · 기존 테스트 무수정(회귀 그물) `git diff --name-only --d ← evidence/20261108-2029-verifier-04-R-1.t
PASS  증거 확인:  R-2 · 허용 파일 / 무변경 경로 ①②  ← evidence/20261108-2029-verifier-04-R-2a.
PASS  증거 확인:  R-3 · 스키마 무변경 `alembic check`  ← evidence/20261108-2030-verifier-04-R-3-a
PASS  증거 확인:  R-4 · P5-loop 불변식 grep ①~⑤(⑤ 는 `grep -E` 로 `8a876 ← evidence/20261108-2029-verifier-04-R-4.t
PASS  증거 확인:  R-5 · 기록 턴 회귀(기존 6파일)  ← evidence/20261108-2030-verifier-04-R-5.t
PASS  증거 확인:  R-6 · 네트워크 0(신규 5파일)  ← evidence/20261108-2030-verifier-04-R-6.t
PASS  증거 확인:  R-7 · 순환 import 없음(결정 L)  ← evidence/20261108-2031-verifier-04-R-7a-
PASS  증거 확인:  R-8 · 원칙7 경계 — 상담성 답 없음  ← evidence/20261108-2033-verifier-04-R-8-r
PASS  증거 확인:  H-1 · "실 LLM 왕복 1회(trace 368 류 질문에 카드 근거 답)" — 결정 ← evidence/20261108-2002-u7t-1-relation.tx
PASS  registry 에 P5b-query-turn 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=1 → evidence/20261109-0051-summary.txt ==
```
WARN 1 은 1-1 과 같은 하네스 ruff 경고(`.claude/scripts/`, 이 패키지 diff 무관).

FAIL 0 이므로 `findings.py --source verify-impl` 소견은 만들지 않았다. 열린 [필수] 소견 없음(§6).

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로만. 첫 열은 `docs/backlog.md` 75행의 문장을 글자 그대로 둔 뒤, 01-plan "해석" 절대로 판정 표 행(D-1~D-7 · A-1~A-5 · R-1~R-8 · H-1)으로 쪼갰다. 각 행의 명령은 01-plan 판정 표의 안쪽 명령 그대로이고, 내가 2026-11-08 20:26~20:33 에 직접 실행했다.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| [backend-agent] **P5b-query-turn** — 채팅 조회 발화: 인식 단계 `intent`(record/query) 필드 + 게이트가 조회 턴의 기록 제안 거부 + 같은 ER 4단계로 해석(identity 되묻기 유지, new_person 은 "기록이 없어요") + `get_person_card` 근거(사실 전부·타임라인 최근 5·일정) LLM 답 + R19 금지 표현 검증기(실패 시 템플릿) (CR-004 · D16) / 의존: P5-loop, P6-briefing(검증기), P8 U1(`get_person_card`) / 수용기준: D16 "코드에서 지켜야 할 것" 전부 · 조회 턴 저장 0(`events`·`schedules`·`person_facts`·`persons` 행 수 불변, 기록 툴 `tool_call` 0) · 툴 7종 불변(`tools_check` 7/7) · 프론트 diff 0 · trace 에 의도·해석·조회 근거 건수·답 · pytest 통과 · 실 LLM 왕복 1회(trace 368 류 질문에 카드 근거 답) — 사용자 승인 2026-10-28 | evidence/20261108-2026-verifier-04-verify-impl.txt, evidence/20261108-2027-verifier-04-A-4-pytest-all.txt, cf26dce | 통과 — 아래 20행(D-1~D-7·A-1~A-5·R-1~R-8)+H-1 중 통과 20 · 미달(문구) 1(R-1, 회귀 그물 자체는 유지 — §3·§6 R-04-1) |
| D-1 · D16 "`propose.py` 구조화 출력 스키마에 `intent` enum `["record","query"]` 가 있고, 다른 필드·툴 제안 스키마는 그대로다." ① 스키마 값 ② 인자 스키마 줄 diff ③ U1 테스트 | evidence/20261108-2031-verifier-04-D-1a-rerun.txt, evidence/20261108-2029-verifier-04-D-1b.txt, evidence/20261108-2030-verifier-04-D-1c.txt | 통과 — ① `['intent', 'tool_calls']` / `['record', 'query']` / `True`, `required: ['tool_calls']` ② 01-plan 목록 키(person·type·…·facts)의 추가·삭제 줄 0; 출력 2줄은 `+ "query": {"type": "string"}`(D16 보정 ③ `e49f78d` — `PROPOSAL_ARG_SCHEMA` 에 `query` 속성 1개가 늘어난 것, 카드 갱신 이력에 기록됨)과 `+ "intent"` 최상위 속성 ③ 24 passed |
| D-2 · D16 "`gate.py` 는 `intent == "query"` 턴의 기록 툴 제안을 거부하고 사유를 `loop_gate` trace 에 남긴다. `search_person`·`ask_user`·`get_briefing` 의 `not_callable_by_llm` 은 그대로다." | evidence/20261108-2033-verifier-04-D-2-rerun.txt, evidence/20261108-2002-u7t-5-mixed.txt, evidence/20261108-2002-u7t-1-relation.txt | 통과 — `-k "query_turn or loop_gate or not_callable"` 19 passed(1회차 `…-2030-…-D-2.txt` 는 래퍼 인자 분리로 exit 4, 무효). 실 LLM: u7t-5 `loop_gate.rejected` = `search_person not_callable_by_llm` + `add_event query_turn_no_write`, u7t-1 trace 569 `search_person not_callable_by_llm` |
| D-3 · D16 "`loop.py` 조회 분기는 `app.er.resolve`/`apply_resolution` 을 재사용하고, `get_person_card` 를 **코드로** 부른다. `app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로(`scripts/tools_check.py` 7/7)." ①~④ | evidence/20261108-2031-verifier-04-D-3a-D-6b-greps.txt, evidence/20261108-2029-verifier-04-D-3b-A-2-tools-check.txt, evidence/20261108-2029-verifier-04-D-3c.txt, evidence/20261108-2030-verifier-04-D-3d.txt | 통과 — ① `_run_query_turn`(1284~) 안 `resolve(` 1307 · `apply_resolution(` 1337(identity 경로만, 1320 주석 "결정 I (a) -- apply_resolution() 을 부르지 않는다") · `_read_card` 1266 지연 import·1269 호출 ② `RESULT: 7/7 ok` ③ 빈 출력 ④ `-k merge_answers_from_card` 1 passed |
| D-4 · D16 "조회 턴에 `add_event`·`add_schedule`·`update_person`·`create_person` `tool_call` trace 0, `events`·`schedules`·`person_facts`·`persons` 행 수 변화 0(`assert_no_writes` 류 단언)." | evidence/20261108-2030-verifier-04-D-4.txt, evidence/20261108-2033-verifier-04-mut-u4.txt | 통과 — `-k no_writes` 4 passed. 변이 U4(merge 에서 `apply_resolution` 호출)로 (a)·(g)·u7·스파이 5 FAIL → 단언이 살아 있다 |
| D-5 · D16 "`new_person` 구간의 조회 턴은 `pending_questions` 행을 만들지 않는다(③-2). `identity` 구간은 만든다." | evidence/20261108-2033-verifier-04-D-5-rerun.txt, evidence/20261108-2002-u7t-4-unknown.txt | 통과 — `-k "new_person_no_question or identity_asks"` 3 passed. 실 LLM ④ 는 identity(+1, id 21) — ER 가 `band=identity` 를 돌려준 경우라 D16 결정 3 "identity 구간은 되묻기" 그대로(H-1 행) |
| D-6 · D16 "답 생성 프롬프트에 들어가는 근거는 `get_person_card` 응답에서 온 값뿐이고(발화 원문 + 카드), 타임라인은 최근 5건까지. 답은 R19 검증기를 거치고, 실패 시 템플릿 문자열(프론트 고정 문구가 아니라 서버가 만든 `reply`)." ①~③ | evidence/20261108-2033-verifier-04-D-6a-rerun.txt, evidence/20261108-2031-verifier-04-D-3a-D-6b-greps.txt, evidence/20261108-2029-verifier-04-D-6c.txt, evidence/20261108-2033-verifier-04-mut-u3.txt | 통과 — ① 33 passed ② `respond.py` 54·55행 import, 281·282행 검사 ③ `app/briefing/` diff 빈 출력. 보정 ④(`cf26dce`): 관계·위계 줄은 카드 두 값의 결정적 풀어쓰기(`_RELATION_DESC`·`_HIERARCHY_DESC`, 사전 밖은 원문) — D16 갱신 이력 2026-11-08 보정 ④ 인용 "새 사실·다른 출처 없음". 변이 U3(금지 표현 목록 비움) 16 FAIL |
| D-7 · D16 "프론트(`web/`) diff 0." | evidence/20261108-2029-verifier-04-D-7.txt | 통과 — 빈 출력 |
| A-1 · "조회 턴 저장 0(`events`·`schedules`·`person_facts`·`persons` 행 수 불변, 기록 툴 `tool_call` 0)" | evidence/20261108-2030-verifier-04-A-1.txt, evidence/20261108-2030-verifier-04-D-4.txt, evidence/20261108-2002-u7t-1-relation.txt, evidence/20261108-2002-u7t-7-identity.txt | 통과 — `-k stored_zero` 3 passed(`stored == {0,0,0}`, 7개 테이블 불변 — 결정 I (a) 로 `person_aliases` 포함). 실 LLM 7건 전후 행 수 `12|15|33|6|24|36|20→20`(①~③), `…|21→21`(⑤~⑦); ④ 만 `pending_questions` 20→21 |
| A-2 · "툴 7종 불변(`tools_check` 7/7)" | evidence/20261108-2029-verifier-04-D-3b-A-2-tools-check.txt | 통과 — `RESULT: 7/7 ok` |
| A-3 · "trace 에 의도·해석·조회 근거 건수·답" | evidence/20261108-2030-verifier-04-A-3.txt, evidence/20261108-2030-verifier-04-R-6.txt, evidence/20261108-2002-u7t-1-relation.txt | 통과 — `-k trace` 2 passed(`loop_extract.output.intent`·`loop_query` 5 step). 결정 C 스키마 키 집합 테스트(`test_k_loop_query_output_schema`)는 이름에 `trace` 가 없어 R-6(176 passed)에서 돌았다. 실 LLM trace 572: `intent query`·`resolutions[{band merge, person_id 9, er_trace_id 571}]`·`evidence_counts {1,0,3,0}`·`answer_source llm`·`reply`·토큰 448/16 |
| A-4 · "pytest 통과" | evidence/20261108-2027-verifier-04-A-4-pytest-all.txt, evidence/20261108-2026-pytest.txt | 통과 — `pytest tests/ -q -rs` **2136 passed, skip 0**(기준 1958 + 신규 178: 새 파일 5개 176 + `test_agent_propose.py` 2) |
| A-5 · 린트 | evidence/20261108-2029-verifier-04-A-5-ruff.txt, evidence/20261108-2029-verifier-04-mypy.txt | 통과 — `ruff check app tests` `All checks passed!` · `mypy_check.py --run` `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` |
| R-1 · 기존 테스트 무수정(회귀 그물) `git diff --name-only --diff-filter=M 8a8767b..HEAD -- tests/` | evidence/20261108-2029-verifier-04-R-1.txt, evidence/20261108-2031-verifier-04-R-1-propose-diff.txt, e49f78d | **미달(문구)** — 기대 "빈 출력" 인데 `tests/test_agent_propose.py` 1건. U7 결함 수정 `e49f78d` 가 그 파일 끝에 테스트 2개(`test_proposal_arg_schema_has_query_property`·`test_build_propose_prompt_tells_query_field_and_accepts_person`)를 **추가만** 했다(`+15/−0`, 삭제 줄 0 — 기존 59건 본문 무변경, 회귀 그물 유지). 03-log U7 항목·review-u7-fix §1 표에 파일이 적혀 있으나 01-plan 24행 "기존 테스트 파일은 고치지 않는다"·R-1 행에 보정 기록이 없다 → §6 R-04-1 [권고] |
| R-2 · 허용 파일 / 무변경 경로 ①② | evidence/20261108-2029-verifier-04-R-2a.txt, evidence/20261108-2029-verifier-04-R-2b.txt, evidence/20261108-2029-verifier-04-scope-diffstat.txt | 통과 — ① 정확히 허용 7개(`app/agent/{__init__,gate,loop,propose,respond,types}.py`·`app/settings.py`) ② `app/er app/tools app/api app/db app/briefing app/memory app/main.py alembic web` 빈 출력 |
| R-3 · 스키마 무변경 `alembic check` | evidence/20261108-2030-verifier-04-R-3-alembic.txt | 통과 — `No new upgrade operations detected.` |
| R-4 · P5-loop 불변식 grep ①~⑤(⑤ 는 `grep -E` 로 `8a8767b` 와 동일성, 01-plan 159행 메모 R-U1-2·R-U6-3) | evidence/20261108-2029-verifier-04-R-4.txt | 통과 — ① `create_person\(` `loop.py` 1 = 기준 1 ② `update_person\(` `loop.py` 4 + `respond.py` 1 = 기준 ③ 0건 ④ 0건 ⑤ 파일별 건수 `types.py 2·loop.py 3·그 외 0` = 기준 `8a8767b` 와 동일, `git diff 8a8767b..HEAD -- app/agent` 추가 줄 매치 0 |
| R-5 · 기록 턴 회귀(기존 6파일) | evidence/20261108-2030-verifier-04-R-5.txt | 통과 — 162 passed(`test_agent_propose.py` 는 U7 추가 2건 포함) |
| R-6 · 네트워크 0(신규 5파일) | evidence/20261108-2030-verifier-04-R-6.txt, evidence/20261108-2033-verifier-04-collect-counts.txt | 통과 — 176 passed(types 24 · gate 28 · answer 82 · loop 34 · api 8), Fake 4종만 |
| R-7 · 순환 import 없음(결정 L) | evidence/20261108-2031-verifier-04-R-7a-rerun.txt, evidence/20261108-2031-verifier-04-R-7b-rerun.txt | 통과 — 두 순서 모두 `ok`(1회차 `…-2029-…-R-7a/b.txt` 는 `PYTHONPATH` 누락으로 `No module named 'app'`, 무효) |
| R-8 · 원칙7 경계 — 상담성 답 없음 | evidence/20261108-2033-verifier-04-R-8-rerun.txt, evidence/20261108-2002-u7t-6-counsel.txt | 통과 — `-k "forbidden or no_counseling"` 18 passed. 실 LLM ⑥ "힘들어 보이는데 어떻게 위로하지?" → `"기록이 없어요."`, 위로·조언 0, `fallback_reason null`(검증기 통과한 답을 사람이 원칙7 로 판정 — 위반 없음) |
| H-1 · "실 LLM 왕복 1회(trace 368 류 질문에 카드 근거 답)" — 결정 H 발화 6 + "박 과장님"(4차 `cf26dce` 코드, 3차 `e49f78d`, 11-04 `a004cdd`) | evidence/20261108-2002-u7t-1-relation.txt, evidence/20261108-2002-u7t-2-facts.txt, evidence/20261108-2002-u7t-3-last-contact.txt, evidence/20261108-2002-u7t-4-unknown.txt, evidence/20261108-2002-u7t-5-mixed.txt, evidence/20261108-2002-u7t-6-counsel.txt, evidence/20261108-2002-u7t-7-identity.txt, evidence/20261108-2002-u7t-card-9-before.txt, evidence/20261108-2002-u7t-card-7-before.txt, evidence/20261107-1534-u7s-1-relation.txt, evidence/20261104-2110-u7r-1-relation.txt | 통과(결정 H 판정 기준 1~4 충족, 5~6 관찰) — 상세는 아래 "H-1 대조" |

## 2-1. H-1 대조 (결정 H 표 ↔ 4차 evidence `u7t-*`, 코드 = `cf26dce`)
(§2 표의 H-1 행을 발화별로 푼 것. `verify-impl.sh` 5번이 §2 의 `|` 행을 전부 수용 기준으로 세므로 별도 절로 뺐다 — 1회차 재실행 `evidence/20261108-2040-verifier-04-verify-impl-final.txt` 에서 이 표의 7행이 "증거가 파일·커밋·경로가 아니다" FAIL 8 로 잡힌 이력.)

4차 evidence 머리의 `HEAD: e49f78d` 는 실행 시점에 수정 3 이 미커밋 작업 트리였기 때문이고, 그 작업 트리의 `app/` 변경은 `respond.py` 1파일 = `git diff e49f78d cf26dce -- app/`(`respond.py +9/−1`) 와 같다(review-u7-fix3 §6 blob 대조). 서버는 `--reload` 로 기동돼 그 파일을 읽었다.

| # | 결정 H 기대 | 4차 실제 | 판정 |
|---|---|---|---|
| 1 | `intent == "query"`, 언급에 "나" 없음, 답에 `relation_tag`·`hierarchy`, 저장 0 | trace 568 `intent query`·`search_person(query="박선우 과장님")` 1건(제안에 "나" 없음) · merge 9(conf 1.0) · reply **"직장 관계, 위계 동(같은 급)"** = 카드 9 `직장`/`동` · `evidence_counts {facts 1, timeline 3}` · 토큰 448/16 · 행 수 `12|15|33|6|24|36|20` 불변 | 충족(3차 `u7s-1` "기록이 없어요" ✗ → 수정 3 으로 닫힘; 11-04 `u7r-1` 은 `no_mention` ✗ → `e49f78d` 로 닫힘) |
| 2 | 답이 카드 `facts` 의 값을 재진술, 카드에 없는 정보 0 | "민수는 뭐 좋아해?" → "기록이 없어요" · 카드 7 facts = `job=과장`·`workplace=회사`·`life_event=이사 간다`(좋아하는 것 없음) · 저장 0 | 카드 밖 정보 0 충족. **facts 값의 양성 재진술은 미시연** — 질문이 카드에 없는 사실을 물어 '기록이 없어요' 가 맞는 답이었다(E-6 "자료에 없는 것은 '기록이 없어요'"). 양성 표본은 ①(관계·위계)·③(마지막 접촉)만 — §6 R-04-3·§7 P10 인계 |
| 3 | 답의 날짜 == 카드 `last_contact_at`(사용자 시간대) | "…10월 21일입니다." · 카드 9 `last_contact_at 2026-10-21T06:00:00Z` = 서울 10월 21일 15:00 · 저장 0 | 충족 |
| 4 | `pending_question == null`, `pending_questions` +0, reply == ③-2 문구 | ER `er_resolve` 589: 통과 후보 6(박수·민수·김윤서·…), 판정 `matched_person_id null` → `band identity`·`forced_reason no_matched`·`band_by_threshold new_person` → `ask_user` id 21 · `pending_questions` 20→21 · 그 외 테이블 불변 · `persons` +0 | **통과(허용 판정)** — 루프는 `band` 만 읽는다(01-plan U4 ② "결과 band 만 본다", 원칙1·2·4)이고 ER 는 `app/er/confidence.py` 290~303행 규약 "**null**(결정3-c(b)): `judgement.matched_person_id is None` → llm_failed 와 같은 귀속, `forced_reason="no_matched"`" + "통과 후보 유무로 `band` 가 `identity`/`new_person` 로 갈린다" 대로 identity 를 돌려줬다. D16 결정 3 "identity 구간(후보가 있을 때)은 … 되묻고 … new_person 구간(아예 모르는 사람)은 되묻지 않고" 와 일치 — 결정 H #4 의 "new_person·+0" 문구는 통과 후보 0 을 전제한 것이므로 "저장 0·인물 생성 0·되묻기 1행 허용" 으로 읽는 메인 제안에 **동의**. 단 01-plan 결정 H 표에 그 보정 1줄이 없다 → §6 R-04-2 [권고] |
| 5 | intent query 면 `events` +0 (record 면 오분류 관찰) | `intent query` · 제안 `search_person(query=민수)` + `add_event(meal …)` → 게이트 `query_turn_no_write` 거부 · `events` 33→33 · 답 "기록이 없어요" | 관찰 — D16 결정 6 대로 기록 0(혼합 발화 기록 누락은 설계된 비용, P10) |
| 6 | 답에 위로·조언 없음 | "기록이 없어요." · `fallback_reason null`(검증기 통과) · 위로·조언·감정 표현 0 | 관찰 — 원칙7 위반 없음 |
| 7(추가) | "박 과장님" → identity 되묻기 기대(메인) | merge 9(conf 0.838 = 0.5·0.9 + 0.3·0.627 + 0.2·1.0; `s_llm 0.9` "박선우 과장님을 지칭할 가능성이 높기 때문") — 후보 7(민수, 별칭 "박 과장", `s_emb 0.93`·`s_rule 0.67`)·9·10 중 9 로 자동 병합 · 조회 턴이라 별칭 누적 0·저장 0 | **오병합 위험 표본**(원칙1) — 조회 턴에서는 결정 I (a) 로 피해 0 이지만 기록 턴이었다면 자동 병합. 코드 결함이 아니라 ER 판정 품질(R-U10R-4 계열) → §7 (가) |

공통 판정: 7건 전부 `intent query`·`search_person` 인자 키 `query`(R-U7F-6 닫힘)·`mentions_dropped 0`("나" 폴백 부작용 R-U7F-3 미관찰)·`loop_query` 행 존재·LLM 답인 경우 토큰 > 0(448/16·448/9·449/24·460/9·454/10·443/10) · 저장 0(④ 는 `pending_questions` 만 +1).

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
01-plan "04-review" 줄의 목록을 전부 **내가 직접 실행**했다. 변이 시험은 `docs/wiki/verification.md` "변이 시험 방법" 의 **런타임 치환**(스크래치패드 `scratchpad/v04/mut_u<n>.py` pytest 플러그인, `-p mut_u<n>`) — 저장소 작업 트리는 한 글자도 고치지 않았다(`evidence/20261108-2033-verifier-04-git-status-after-mutation.txt`: `git status --short -- app tests alembic` 빈 출력; 각 변이 evidence 끝에도 같은 명령의 빈 출력).

| 케이스 | 명령 | 증거 |
|--------|------|------|
| 조회 턴 기록 0(7개 테이블 행 수 불변) | `pytest tests/test_agent_query_loop.py tests/test_api_chat_query.py -q -k no_writes` · `pytest tests/test_api_chat_query.py -q -k stored_zero` · 실 LLM 7건의 요청 전후 `SELECT count(*)` 7개 | `evidence/20261108-2030-verifier-04-D-4.txt`(4 passed) · `evidence/20261108-2030-verifier-04-A-1.txt`(3 passed) · `evidence/20261108-2002-u7t-{1..7}-*.txt` counts before == after(④ 만 `pending_questions` +1) |
| 기록 툴 `tool_call` 0(`add_event`·`add_schedule`·`update_person`·`create_person`) | 같은 `-k no_writes`(테스트 안 `SELECT … WHERE step='tool_call' AND tool_name IN (4종)` 단언) · 실 LLM trace 목록 | `evidence/20261108-2030-verifier-04-D-4.txt` · `evidence/20261108-2002-u7t-5-mixed.txt`(`add_event` 제안이 `query_turn_no_write` 로 거부되고 `tool_call` 행은 `search_person` 만) · 변이 U4 가 `update_person` tool_call 을 만들자 `assert 1 == 0` 으로 3 FAIL(`evidence/20261108-2033-verifier-04-mut-u4.txt`) |
| new_person 질문 행 0 | `pytest … -k "new_person_no_question or identity_asks"` | `evidence/20261108-2033-verifier-04-D-5-rerun.txt`(3 passed: 루프 (b)·HTTP new_person·identity 대조). 실 LLM 표본에는 new_person 밴드가 없었다(④ 가 identity) — 코드 경로는 테스트로만 확인 |
| `search_person` 여전히 `not_callable_by_llm` | `pytest … -k "query_turn or loop_gate or not_callable"` · 실 LLM `loop_gate` | `evidence/20261108-2033-verifier-04-D-2-rerun.txt`(19 passed) · `evidence/20261108-2002-u7t-1-relation.txt` trace 569 `{"name": "search_person", "reason": "not_callable_by_llm"}` — 7건 전부 같은 사유 |
| 금지 표현 답 → 템플릿(서버가 만든 `reply`) | `pytest … -k "prompt or timeline_limit or forbidden or fallback"` · `-k "forbidden or no_counseling"` · 변이 U3 | `evidence/20261108-2033-verifier-04-D-6a-rerun.txt`(33 passed) · `evidence/20261108-2033-verifier-04-R-8-rerun.txt`(18 passed) · `evidence/20261108-2033-verifier-04-mut-u3.txt`(금지 목록을 비우면 14 parametrize + 루프 (d)·(x) = 16 FAIL — 검사가 실제로 답을 바꾼다) |
| `web/`·`app/er`·`app/tools`·`app/api`·`alembic` diff 0 | `git diff --stat 8a8767b..HEAD -- app/er app/tools app/api app/db app/briefing app/memory app/main.py alembic web` · `-- web/` · `-- app/tools/` · `-- app/briefing/` | `evidence/20261108-2029-verifier-04-R-2b.txt`·`-D-7.txt`·`-D-3c.txt`·`-D-6c.txt` 전부 빈 출력 · 허용 7파일만 바뀜(`-R-2a.txt`) |
| 기존 테스트 파일 무변경 | `git diff --name-only --diff-filter=M 8a8767b..HEAD -- tests/` | `evidence/20261108-2029-verifier-04-R-1.txt` → **`tests/test_agent_propose.py` 1건**(기대 빈 출력). `evidence/20261108-2031-verifier-04-R-1-propose-diff.txt` `+15/−0` — 삭제 0, 기존 테스트 본문 무변경(추가 2함수, `e49f78d`). 회귀 그물은 유지되나 계획 문구와 어긋남 → §6 R-04-1 |
| 기존 기록 경로 그대로(`intent` 없는 턴) | `pytest tests/test_agent_gate.py tests/test_agent_loop.py tests/test_api_chat.py tests/test_api_answers_resume.py tests/test_agent_propose.py tests/test_agent_types.py -q` | `evidence/20261108-2030-verifier-04-R-5.txt` 162 passed |
| 변이 **U1** — `validate_proposal` 의 `intent` 누락/`null` 기본값을 `record` → `query` 로(결정 A) | `PYTHONPATH=<scratchpad>/v04 pytest tests/test_agent_query_types.py -p mut_u1` (대조군 24 passed) | `evidence/20261108-2033-verifier-04-mut-u1.txt` — **2 failed / 22 passed**(`test_fake_proposer_intents_table`·`test_fake_proposer_without_intents_is_record`, `'query' == 'record'`). 메모: `test_validate_proposal_missing_intent_is_record` 는 `app.agent` 재export 로 **원본 함수 객체**를 import 하므로 런타임 치환이 닿지 않아 통과했다 — 치환 방법의 한계(FakeProposer 경로가 같은 계약을 잡음). 테스트 공백 아님 |
| 변이 **U2** — 게이트 Q 관문 무력화(`WRITE_TOOLS = frozenset()`) | `… pytest tests/test_agent_query_gate.py -p mut_u2` (대조군 28 passed) | `evidence/20261108-2033-verifier-04-mut-u2.txt` — **10 failed / 18 passed**(기록 툴 4종 거부·`create_person`·`person_id` 순서·`accepted == []`·상한·FakeProposer 경유·집합 등식) |
| 변이 **U3** — 검증기의 금지 표현 검사 제거(`BRIEFING_FORBIDDEN_EXPRESSIONS = ()`) | `… pytest tests/test_agent_query_answer.py tests/test_agent_query_loop.py -p mut_u3` (대조군 116 passed) | `evidence/20261108-2033-verifier-04-mut-u3.txt` — **16 failed / 100 passed**(parametrize 14 + 루프 (d) 템플릿 폴백 + (x) `answer_source`) |
| 변이 **U4** — merge 에서 `apply_resolution()` 호출(결정 I (a) 위반, `loop.resolve` 래핑) | `… pytest tests/test_agent_query_loop.py -p mut_u4` (대조군 34 passed) | `evidence/20261108-2033-verifier-04-mut-u4.txt` — **5 failed / 29 passed**((a) `update_person` tool_call `1 == 0`·(g)·`test_u7_real_llm_person_arg_shape`·`test_forbidden_callees_are_never_called` "조회 턴이 부르면 안 되는 함수"·(j) `AlreadyApplied` — 기록 턴 대조군까지 깨짐) |
| 변이 **U5** — 재개 `intent` 기본값 `record` → `query`(01-plan 114행 변이 표 3번, `loop.INTENT_RECORD = "query"`) | `… pytest tests/test_agent_query_loop.py -p mut_u5` (대조군 34 passed) | `evidence/20261108-2033-verifier-04-mut-u5.txt` — **1 failed / 33 passed**(`test_v_resume_without_intent_key_keeps_record_path` `assert 0 == 1` — 옛 identity context 가 조회 재개로 가서 별칭 누적 0) — 정확히 계획이 적은 테스트 |
| 변이 **U6** — `run_turn` 조회 분기 진입 조건 오타(01-plan 118행 변이 표 1번, `loop.INTENT_QUERY = "Query"`) | `… pytest tests/test_api_chat_query.py -p mut_u6` (대조군 8 passed) | `evidence/20261108-2033-verifier-04-mut-u6.txt` — **6 failed / 2 passed**(조회 발화가 기록 턴으로 처리돼 reply `"이번 발화에서는 새로 기억한 것이 없어요."`·identity 질문 없음·`loop_query` 0; 통과 2 는 기록 턴 대조군·혼합 발화(게이트가 전부 거부해 쓰기 0) — 계획 118행 "HTTP 조회 테스트 전부 FAIL" 은 6/8 이 정확) |
| 변이 **U7 수정 3**(보너스) — `_HIERARCHY_DESC["동"] = "동"` | `… pytest tests/test_agent_query_answer.py -p mut_u7` (대조군 82 passed) | `evidence/20261108-2033-verifier-04-mut-u7.txt` — **3 failed / 79 passed**(8값 parametrize `[hierarchy-동]`·관계 줄 서술형·user_text 값) |

변이 7건 전부 검출(생존 0·동등 0). 변이마다 evidence 끝 `git status --short -- app tests` 빈 출력(저장소 무수정).

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- 이 패키지가 **새로 닫는 R 은 없다**(01-plan 4행 "닫는 검증: 없음(R19 경계를 재사용)"). `review-index.md` 27행 R19 는 이미 "구현완료(a2f032d — …)" 이고 비고에 "**CR-004(D16)**: 같은 금지 표현 검증기를 채팅 조회 답에도 재사용(P5b-query-turn)" 이 있다 — 상태 변경 불필요.
- **권고(메인)**: R19 비고의 "(P5b-query-turn)" 뒤에 완료 해시를 덧붙인다 — 예 "(P5b-query-turn `cf26dce` — `respond.py::validate_query_answer` 가 `BRIEFING_FORBIDDEN_EXPRESSIONS`·`REASON_FORBIDDEN_EXPRESSION` 을 import, 금지 표현 답은 템플릿 대체)". 근거: `evidence/20261108-2031-verifier-04-D-3a-D-6b-greps.txt` 54·55·281·282행.
- D16 갱신 이력 2026-10-28 줄 "구현은 P5b-query-turn — 완료 해시는 그때 적는다" → **완료 해시 `cf26dce`**(U1 `1dccb95` ~ U7 수정 3 `cf26dce`) 제안.

## 5. registry.md 에 올린 산출물
`verify-impl` 6번 PASS(`| P5b-query-turn |` 행 존재). 172~176행(새 테스트 5)·비고 확장(`settings.py` 56행, `types.py` 164, `__init__.py` 165, `propose.py` 166, `gate.py` 167, `loop.py` 168, `respond.py` 169)을 커밋 해시·건수와 대조했다(`evidence/20261108-2033-verifier-04-collect-counts.txt`: types 24 · gate 28 · answer **82** · loop **34** · api 8 · `test_agent_propose.py` 64). **메인이 고칠 것**:
- 176행 `tests/test_api_chat_query.py` 해시 `pending` → **`a004cdd`**.
- 168행 `loop.py` 비고 "P5b U6(해시 pending)" → **`a004cdd`**; 비고에 **U7 `e49f78d`** 추가 — `_query_mentions()` 가 `search_person` 의 `query` 우선·문자열 아님/빈 값이면 `person` 폴백(결정 B-3 (b) 보정).
- 166행 `propose.py` 비고에 **U7 `e49f78d`** 추가 — `PROPOSAL_ARG_SCHEMA.properties.query`(D16 보정 ③)·조회 예외 문장 "그 언급을 query 필드에 써라(person 필드에 써도 받아들인다)".
- 169행 `respond.py` 비고에 **U7 수정 3 `cf26dce`** 추가 — `_RELATION_DESC`(5)·`_HIERARCHY_DESC`(3) 결정적 풀어쓰기, 시스템 문장 "관계나 위계를 물으면 …" 1문장(D16 보정 ④).
- 174행 `tests/test_agent_query_answer.py` "71건(U3)" → **82건**(U3 71 + 수정 3 `cf26dce` 11: 카드 줄 기대값·서술형·사전 밖·사전 키 집합 1·8값 parametrize), 해시에 `cf26dce` 병기.
- 175행 `tests/test_agent_query_loop.py` "33건" → **34건**(`e49f78d` h3 입력 3건 개정 + `test_u7_real_llm_person_arg_shape` 신규), 해시에 `e49f78d` 병기.
- 173행 `tests/test_agent_query_gate.py` 비고에 `e49f78d` 문장 교체(+2/−2) 메모.
- 177행 `tests/test_agent_propose.py`(P5-loop, "59건") 비고에 **P5b U7 `e49f78d` 2건 추가**(스키마 `query` 속성·프롬프트 문장) — 현재 수집 64건.
- `tests.md` 5행 머리글 "U6 완성 … 164건 … 2122 passed" → U7 반영: 새 파일 5개 **176건** + `test_agent_propose.py` 2 = 178, 전체 **2136 passed skip 0**(`evidence/20261108-2027-verifier-04-A-4-pytest-all.txt`). U7 절(182·207행)은 이미 있다.
- `03-log.md` 2026-11-08 20:02 항목(수정 3)에 "커밋 뒤: `cf26dce`, dev2 푸시" 줄이 없다(다른 항목은 전부 있음) — 추가.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
`verify-impl` FAIL 0 → `05-remediation.md` 소견 없음. 열린 **[필수] 0**. 아래는 [권고]·사용자 결정·인계.

**이 검토에서 새로 낸 소견**
- **R-04-1 [권고] R-1 미달(문구)** — `tests/test_agent_propose.py` 가 `e49f78d` 에서 +15/−0 수정됨(§2 R-1·§3). 기존 59건 본문 무변경·삭제 0 이라 회귀 그물은 유지되지만, 01-plan 24행 "기존 테스트 파일은 고치지 않는다"·R-1 행 기대 "빈 출력" 과 어긋나고 보정 기록이 없다. 조치(메인, 문서만): 01-plan R-1 행 또는 24행 아래 "보정(U7 `e49f78d`, R-04-1): `tests/test_agent_propose.py` 끝에 U7 테스트 2건 추가(삭제 0) — `--diff-filter=M` 1건은 이 파일뿐" 1줄. 코드 변경 없음.
- **R-04-2 [권고] 결정 H #4 문구 보정** — 기대 "new_person·`pending_questions` +0" 은 통과 후보 0 을 전제. 실제(3차·4차)는 ER 결정3-c(b)(`app/er/confidence.py` 302~303행)로 identity 되묻기(+1). 조치(메인, 문서만): 01-plan 결정 H 표 아래 "보정(04-review R-04-2): 후보가 있고 판정 null 이면 identity 되묻기 1행 허용(저장 0·인물 생성 0) — D16 결정 3 그대로" 1줄.
- **R-04-3 [관찰] 결정 H #2 양성 표본 부재** — "뭐 좋아해?" 가 카드에 없는 사실을 물어 '기록이 없어요' 가 정답이었고, facts 값을 **재진술하는** 실 LLM 답은 ①(관계·위계)·③(마지막 접촉)뿐이다. 코드 결함 아님. P10 평가셋에 "카드 facts 와 맞는 질문"(예 `job`·`workplace` 를 묻는 발화) 표본 추가 권고(§7).
- **R-04-4 [메모] verify-impl WARN(ruff)** — `.claude/scripts/findings.py` DTZ005 2건·`bash_write_check.py` B007 1건, 하네스 기존 경고(이 패키지 diff 와 무관). 하네스 FIX 후보로 이관.

**사용자 결정이 필요한 것**
- **R-U7F3-3** — E-5 템플릿 "박선우 과장님 — 직장·동, …" 과 LLM 답 "직장 관계, 위계 동(같은 급)" 의 표기 차(폴백 여부에 따라 같은 질문의 표기가 달라짐). E-5 는 사용자 확정 문구라 코드 무변경이 맞다. 통일할지는 사용자 결정 → 완성 확인 때 함께 묻기(E-6 1문장 추가 고지와 같은 자리).
- **무효 evidence 삭제(훅이 `rm` 차단, 사용자 몫)** — `docs/wiki/packages/P5b-query-turn/evidence/20261107-1455-u7fix-ruff.txt`(R-U7F-5) · `…/20261108-2009-u7fix3-review-baseline.txt`(R-U7F3-4). 둘 다 미추적 파일(`git status` `??`) — 커밋에 넣지 않으면 된다. HANDOFF 가 적은 `docs/wiki/fixes/evidence/20261108-2000-L-007-test-guards.txt` 도 같은 종류.
- **R-U3-4(잔존)** — E-6 조립 system 에서 원칙7 구절 뒤 문장 경계가 없다(`respond.py` 157~158행 "…평가·조언·감정 대화는 하지 않는다 아래 인물 카드 자료만…"). 수정 3 이 문장 1개를 더했지만 이 자리는 그대로다. 사용자 결정 "그대로 두고 U7 에서 판단" → U7 4차 답은 정상이었으므로 바꿀 이유는 없다. 바꾸려면 01-plan E-6·`test_prompt_system_exact_sentences` 를 함께.

**단위 리뷰 [권고] 추적(review-u1~u6·u7-fix·u7-fix3 ↔ 03-log)**
| 소견 | 상태 | 근거 |
|---|---|---|
| R-U1-1 변이 표 M1 문구 | 닫힘 | 01-plan 94행 "U2 뒤 재실행 42 FAIL … 닫힘", `evidence/20261102-0821-verifier-u2-mutation.txt` |
| R-U1-2 R-4 ⑤ 동일성 판정 | 닫힘 | 01-plan 159행 메모, 이 문서 R-4 가 동일성으로 판정 |
| R-U1-3 · R-U2-5 · R-U3-5 · R-U4-4 03-log 항목 | 닫힘 | 03-log U1~U4 항목 존재 |
| R-U2-1 동등 변이 문구 | 닫힘 | 01-plan 99행 수정 |
| R-U2-2 `gate.py` 284·293행 주석 | 닫힘 | 03-log U2 "2줄만 `①②Q④③⑤` 로 고침" |
| R-U2-3 조회 턴 5함수 스파이 없음 | 열림(수용) | 실질 공백 아님(`check()` 순수 함수) — 조치 없음, 기록만 |
| R-U2-4 tests.md "함수 17" | 닫힘 | tests.md 32행 "함수 18개" |
| R-U3-1 원문 비노출 공허 단언 | 닫힘 | U4 (l) `raw_utterance` DB 시드, review-u4 §1 |
| R-U3-2 `no_record_reply([])` | 닫힘 | U4 (i)(m) `no_mention_reply()` 선행 |
| R-U3-3 재export 범위 | 열림(선택) | 계약 위반 아님, 조치 없음 |
| R-U3-4 E-6 문장 경계 | 열림(사용자 결정) | 위 |
| R-U4-1 변이 표 3·5번 문구 | 닫힘 | 01-plan 110행 "U4 실측" |
| R-U4-2 생존 변이 5건 | 닫힘 | U5 (x)(y)(z)(aa), review-u5 §1 |
| R-U4-3 `loop_query.input` 중복 | 닫힘(인계) | §7 (사) |
| R-U5-1 재개 카드 `PersonNotFound` 테스트 | 닫힘 | U6 `test_chat_query_resume_person_deleted…`, review-u6 V4 검출 |
| R-U5-2 `resume_turn` docstring | 닫힘 | `a004cdd` docstring 절, review-u6 §1 |
| R-U5-3 / R-U6-1 구현자 사본의 비밀 파일(스크래치패드 `p5b-u5/repo`) | 확인 불가 | 다른 세션의 스크래치패드라 이 세션에서 보이지 않는다 — 사용자 삭제 여부 확인 요청 |
| R-U6-2 RUNNING.md 132행 | 닫힘 | 03-log U6 "메인: … 정정, R-U6-2" (`a004cdd`) |
| R-U6-3 `git grep -E` `\b` | 닫힘 | 01-plan 159행 메모, 이 문서 R-4 는 `grep -E` 사용 |
| R-U7F-1 · R-U7F-2 · R-U7F-4 | 닫힘 | review-u7-fix §6 |
| R-U7F-3 "나" 폴백 부작용 | 열림(관찰) | 3차·4차 7/7 `mentions_dropped 0`, 미관찰 — 코드 필터는 D16 결정 7 변경 = 사용자 결정, §7 (다) |
| R-U7F-5 무효 evidence 삭제 | 열림(사용자) | 위 |
| R-U7F-6 `query` 키 집계 | 닫힘 | 3차·4차 7/7 `query` |
| R-U7F3-1 · R-U7F3-2 | 닫힘 | review-u7-fix3 §6, `cf26dce` |
| R-U7F3-3 · R-U7F3-4 | 열림(사용자) | 위 |

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- **(가) 오병합 위험 표본(P10 · ER 보정)** — "박 과장님은 뭐 좋아해?"(`evidence/20261108-2002-u7t-7-identity.txt` trace 608)에서 박 성 과장 후보가 셋(7 민수—별칭 "박 과장"·"박지훈 과장님", `s_emb 0.93`·`s_rule 0.67` / 9 박선우 과장님 / 10 박선영 과장님)인데 판정 LLM 이 9 를 `s_llm 0.9` 로 골라 conf 0.838 ≥ T_merge 0.8 → **자동 merge**. 조회 턴이라 결정 I (a) 로 저장·별칭 학습 0 이었지만 기록 턴이면 자동 병합된다(원칙1). R-U10R-4(호칭 단독 언급) 계열. 권고: P10 평가셋에 "같은 성·같은 직함 2~3명" 함정 케이스 추가, 판정 프롬프트가 "구별 근거 없으면 null" 을 내도록 보정 검토.
- **(나) 결정3-c(b) 설계 메모** — 통과 후보가 있고 판정이 null 이면 identity 되묻기(`forced_reason=no_matched`, `app/er/confidence.py` 302~303행). 조회 턴에서 "모르는 이름" 이 되묻기로 끝나는 것은 설계다(④ 김철수 → 박수/민수/김윤서 선택지). P10 의 "조회 턴 되묻기율" 집계 때 `band_by_threshold == new_person` 이면서 `band == identity` 인 행을 따로 셀 것.
- **(다) R-U7F-3 · R-U7F-5 · R-U7F-6** — "나" 폴백 부작용(`mentions_dropped` 로 "한 번에 한 사람씩" 문장이 붙는 것)은 3·4차 7/7 미관찰; `loop_query.output.mentions` 로 계속 관찰, 반복되면 FIX(코드 필터 = D16 결정 7 변경, 사용자 결정). R-U7F-5 는 evidence 1파일 삭제(사용자). R-U7F-6 은 닫힘(`query` 7/7) — 프롬프트 문장 "query 필드에 써라(person 필드에 써도 받아들인다)" + 스키마 열거의 효과 확인.
- **(라) R-U7F3-3** — 템플릿(E-5) "직장·동" vs LLM 답 "직장 관계, 위계 동(같은 급)" 표기 차. 바꾸려면 E-5 문구 결정(사용자) + `template_query_answer`·`EXACT_*` 테스트 동시 수정.
- **(마) L-007** — `safety-guard.sh` E 절 예외로 메인 세션이 `uvicorn app.main:app --env-file .env …` 를 직접 재기동할 수 있다(`9eb9d2e`). 다음 실 LLM 왕복(P9·P10)은 사용자 셸 기동 없이 메인이 돌릴 수 있다 — 단 `.env` 는 여전히 읽지 않는다.
- **(바) 조회 턴의 `not_callable_by_llm` 은 설계다(01-plan 리스크 R-6)** — 결정 B-3 (b) 로 LLM 이 대상 표시용 `search_person` 을 내고 게이트가 거부한다. P10 이 게이트 거부율을 셀 때 `loop_extract.output.intent` 로 기록/조회 턴을 나눠야 한다(조회 턴의 `not_callable_by_llm`·`query_turn_no_write` 는 결함이 아님).
- **(사) `loop_query` 는 `output` 만 읽는다(R-U4-3)** — `input` 에 같은 dict 가 중복 저장된다(`loop_turn` 관례).
- **(아) 인식 단계 토큰 0** — `loop_extract` 행 토큰은 여전히 0(P5-loop 부터). 조회 턴 비용 집계는 `er_resolve` + `loop_query` 토큰으로만(FIX 후보, 범위 밖).
- **(자) 결정 H #2 양성 표본(R-04-3)** — P10 조회 발화 표본에 카드 facts 와 맞는 질문을 넣어 "facts 값 재진술" 을 실제로 관측할 것. 의도 오분류율(D16 파급)도 P10.
- **(차) 혼합 발화 기록 누락(D16 결정 6)** — ⑤ 에서 `add_event(meal)` 제안이 거부돼 "어제 민수랑 밥 먹었다" 가 기록되지 않았다(설계된 비용). P10 표본으로 관찰 뒤 재결정.
- 인터페이스 요약: `run_turn(..., answerer=None)`·`resume_turn(..., answerer=None)`(결정 K — 라우트 무수정, 운영은 `respond.answerer_from_env()` 지연 해소) · `PendingResume.intent`(`"query"` 일 때만 `context["resume"]["intent"]` 에 실림, version "1") · `loop_query` trace 10키(결정 C) · 상수 `QUERY_TIMELINE_LIMIT=5`·`QUERY_MAX_PERSONS=1`·`QUERY_ANSWER_MAX_LINES=3`·`QUERY_ANSWER_MAX_CHARS=240`(`app/settings.py`, 환경변수 없음) · 게이트 사유 `query_turn_no_write`(7번째) · `PROPOSAL_ARG_SCHEMA.query`(D16 보정 ③).

결과: 완료
확인: 사용자 (2026-11-09) — 완성 확인 질문에 "확인". E-6 1문장 추가·R-U7F3-3 표기 차·"박 과장님" P10 인계를 함께 고지함.
