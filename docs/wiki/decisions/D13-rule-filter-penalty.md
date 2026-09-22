# D13 · 2단계 규칙 필터는 후보를 배제하지 않고 감점한다

상태: 유효 | 해결하는 검증: P4 게이트 미달(결정 K) — 제안 방식 오류 2건의 원인 | 출처: CR-001(사용자 A 수용 2026-09-22) ← `reports/failure_cases.md` §1·§2·§8, P4 04-review §7

**결정**
- 2단계 규칙 필터(`app/er/rules.py`)는 `relation_tag_conflict`·`hierarchy_conflict` 인 후보를 **후보 목록에서 제거하지 않는다**. 충돌은 `s_rule = rule_passed / rule_checked` 에 그대로 반영(감점)되고, 후보는 `excluded_by` 대신 **`penalized_by`** 로 표시된 채 3단계 LLM 에 넘어간다 — LLM 이 후보 전체를 비교할 수 있어야 한다.
- `dictionary_conflict`(호칭 사전 그룹 모순)·완화 재검색(승진 인접 위계) 규약은 유지한다. 후보가 0명일 때의 `no_candidates` 강제 경로도 유지.
- **보수 분기(원칙1)**: 감점 후보(`penalized_by` 비어 있지 않음)가 3단계에서 선택되면 `confidence ≥ T_merge` 라도 자동 연결하지 않고 `ask_user(kind="identity")` 로 강등할지는 **P4b-er-redesign 01-plan 의 결정 항목**으로 둔다(기본 권장안: 강등 — 후보가 늘어 오병합 기회가 늘어나는 위험을 40건으로 검증할 수 없기 때문). trace 에 `forced_reason="penalized_candidate"` 로 남긴다.

**이유**
- P4 실 실행에서 규칙 필터가 **골드(정답) 후보를 떨어뜨린** mention 이 6건(`relation_tag_conflict` 2·`hierarchy_conflict` 4). 그중 `sc-015` t0 "부장님" 은 정답 조은우가 제거되고 한지원만 남아 LLM 이 한지원으로 `s_llm 0.9·s_emb 1.0·s_rule 1.0 → 0.95 merge` — **유일한 오병합**. `sc-007` t2 "문실장님" 은 정답이 제거되고 아무도 남지 않아 `no_candidates` — **유일한 미검출**. 나머지 4건은 보류. 즉 제안 방식의 오류 2건이 전부 여기서 시작됐다(`failure_cases.md` §8 표 2행).
- 다른 네 방식은 `sc-015` 에서 전부 `identity` 로 망설였다 — 정답 후보가 목록에 있었기 때문이다. 배제는 LLM 의 비교 기회를 없애 "남은 한 명"에 확신을 몰아준다.
- 힌트(관계 태그·위계)는 발화에서 자동 추론한 값이라 틀릴 수 있다(CLAUDE.md "사용자가 고르지 않고 대화에서 자동 추론"). 추론값 하나로 후보를 영구 배제하는 것은 오병합보다 미검출이 낫다는 원칙1 의 취지와 다르다 — 원칙1 은 **확신이 없으면 묻는 것**이지 후보를 숨기는 것이 아니다.

**파급** (갱신할 S 카드 · 영향 P 패키지 · CLAUDE.md 원칙)
- S3.3 2단계 줄("통과 후보만" → "감점, 후보 유지"), 회귀 3종 조건은 유지(팀장↔이모 배제는 감점 후에도 `< T_merge` 또는 보수 분기로 연결되지 않아야 함 — 회귀로 증명).
- 구현은 **P4b-er-redesign**: `app/er/rules.py`(`_CONFLICT_PRIORITY` 54행 어휘 유지, `relation_tag_conflict` 96행·`hierarchy_conflict` 108행 → 제거 대신 감점 표시, 완화 재검색 167행 재검토 — 배제가 없어지면 재검색의 의미가 줄어드는지 01-plan 이 결정), `app/er/pipeline.py`(2→3단계 후보 전달, 보수 분기), `app/er/confidence.py`(`forced_reason` 어휘 +1), `evaluation/calibration.py` placeholder 판정(`matched_person_id is None` 건수 감소), `tests/test_er_rules*`·`test_er_pipeline*` 기대값.
- P4 기준선 보존, 재실행은 새 stamp(D12 와 동일 규약).
- 위험 계측: P4b 04-review 는 `subsets`(P3-er §7 리스크 계측 — merge 행만)·`penalized_by` 가 있는 merge 건수를 따로 보고한다.

**코드에서 지켜야 할 것** (리뷰어가 grep 으로 확인할 수 있는 문장으로)
- `rules.py` 의 `relation_tag_conflict`·`hierarchy_conflict` 경로가 후보를 목록에서 빼지 않는다(`excluded_by` 에 두 사유가 더 이상 등장하지 않고 `penalized_by` 에 등장한다). `dictionary_conflict` 는 종전 규약.
- 3단계에 전달되는 후보 수 == 1단계 후보 수 − `dictionary_conflict` 제외 수(테스트로 단언).
- 보수 분기 여부는 설정값 하나(`ER_PENALIZED_MERGE_POLICY` 등, 이름은 P4b 01-plan)로 켜고 끌 수 있고 기본값은 01-plan 결정을 따른다. trace 에 적용 여부가 남는다.
- 회귀 3종 통과. `sc-015`·`sc-007` 두 시나리오가 P4b 재실행에서 오병합·미검출이 아니어야 한다(수용 기준에 명시).

**갱신 이력**
- 2026-09-22 신설 — CR-001 A 수용(사용자). 카드는 메인 세션이 기록, 구현은 P4b-er-redesign.
