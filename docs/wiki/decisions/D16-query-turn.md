# D16 · 조회 발화 — 의도 분류, 읽기 전용 조회, 답의 경계

상태: 유효 (대체하는 D 카드 없음 — P5-loop 루프에 분기를 더한다) | 해결하는 검증: 없음(R19 경계 재사용) | 출처: CR-004 (제기·승인 2026-10-28, 사용자 — A 수용, 열린 결정 ①~⑦ 확정) · 변경: `docs/wiki/changes/CR-004.md`

**결정**
1. **의도 분류(①)**: 인식 단계(`app/agent/propose.py`)의 구조화 출력에 `intent: "record" | "query"` 1필드를 더한다(enum 으로 유도 — FIX-015 방식, LLM 자기보고, 추가 호출 없음). 게이트(`app/agent/gate.py`)는 `intent == "query"` 인 턴에서 기록 툴(`add_event`·`add_schedule`·`update_person`·`create_person`) 제안을 **코드로 거부**한다(새 거부 사유 1개 — 어휘는 P5b 01-plan 이 정한다). 조회 턴은 저장 0 이다.
2. **해석은 같은 ER 4단계(원칙1·2·4)**: 조회 발화의 언급도 `app.er.resolve()` → `apply_resolution()` 으로 해석한다. `search_person` 은 여전히 LLM 이 직접 부르지 못한다(게이트 ② 유지). 확신도·임계치를 조회를 위해 낮추지 않는다.
3. **해석이 안 될 때(③-2)**: `identity` 구간(후보가 있을 때)은 기존 `ask_user(kind="identity")` 로 되묻고 답 뒤 재개해 답한다(S3.4 그대로). `new_person` 구간(아예 모르는 사람)은 **되묻지 않고** "기록이 없어요" 로 끝낸다 — 조회 턴에서 "새로 기억할까요" 를 묻지 않는다.
4. **조회(읽기 전용)**: 해석된 `person_id` 로 루프가 **코드로** `app/api/read.py get_person_card()` 를 부른다(P8 U1 조회 함수 재사용, 새 툴·새 API 없음). 근거 = 카드의 사실 전부 + 타임라인 최근 **5건**(⑥, 상수명·환경변수는 P5b 01-plan) + 다가오는 일정 전부 + `relation_tag`·`hierarchy`·`last_contact_at`.
5. **답 생성(②)**: LLM 이 위 근거만으로 1~3줄 자연어 답을 만든다. **R19 금지 표현 검증기**(브리핑 제안에 쓰는 것, `app/briefing/`)를 통과하지 못하면 템플릿 답(마지막 접촉·알고 있는 것 n건·카드 링크)으로 대체한다 — 답이 비지 않는다. 근거에 없는 정보는 "기록이 없어요".
6. **혼합 발화(④)**: `intent == "query"` 면 그 턴은 기록 0(조회 우선, 한 턴 한 의도). 혼합 발화의 기록 누락은 P10 표본으로 관찰 뒤 재결정.
7. **사용자 자신 지칭(⑤)**: "나"·"저" 등은 인식 단계 프롬프트 지시로 언급에서 제외한다(trace 368 의 `search_person("나")` 같은 제안이 생기지 않게).
8. **경계(원칙7)**: 조회 답은 **기록된 사실의 재진술**로 한정한다. 감정·조언·고민·평가를 하지 않는다 — 고민 상담이 아니다. 기획서 2장 제외 칸은 움직이지 않는다.
9. **관측(원칙9)**: 조회 턴도 `agent_traces` 에 의도 분류 결과·해석·조회 입력(인물 id·근거 건수)·답·토큰을 남긴다(step 어휘는 P5b 01-plan).
10. 패키지 이름 **`P5b-query-turn`**(⑦). 프론트 변경 0 — 답은 기존 `reply` 문자열, "인물 카드 보기" 링크 재사용.

**이유**
U10(2026-10-16)에서 사용자가 "박선우 과장님이랑 나는 관계가 뭐야?" 라고 묻자 LLM 은 `search_person` 을 제안했고 게이트가 거부해 "기억한 것이 없어요" 라는 엉뚱한 답이 났다(trace 368). 메모리를 쓰는 길(대화)과 읽는 길(카드·브리핑 화면)이 분리돼 있어 대화에서 기억을 꺼낼 수 없었다. 분류를 LLM 필드 + 코드 게이트로 한 것은 호출 수를 늘리지 않으면서 "조회 턴에 기록" 사고를 구조적으로 막기 위해서다. 답 근거를 카드로 한정하고 검증기를 재사용한 것은 상담(제외 범위)으로 새지 않게 하기 위해서다. new_person 을 되묻지 않는 것은 "물어본 사람" 을 등록 흐름으로 끌고 가지 않기 위해서다.

**파급**
- S 카드: S3.1 스키마·S3.2 툴 7종 시그니처 무변경. **S3.4** 재개 재료(`PendingResume`)에 `intent` 1필드 — 조회 턴의 identity 되묻기 뒤 재개가 조회로 이어지게. S3.5·S3.6 무변경.
- P 패키지: P5-loop(완료) 위에 **P5b-query-turn** 신설. P10 평가 표본에 조회 발화 케이스(의도 오분류율) 추가. P8 프론트 0.
- CLAUDE.md 원칙7 경계 문장에 "조회 답도 기록된 사실의 재진술로 한정" 구절 추가(사용자 결정).
- 기획서: 본문 무변경, 상단 "원본 이후 확정된 사항" 한 줄.

**코드에서 지켜야 할 것** (리뷰어가 grep 으로 확인)
- `propose.py` 구조화 출력 스키마에 `intent` enum `["record","query"]` 가 있고, 다른 필드·툴 제안 스키마는 그대로다.
- `gate.py` 는 `intent == "query"` 턴의 기록 툴 제안을 거부하고 사유를 `loop_gate` trace 에 남긴다. `search_person`·`ask_user`·`get_briefing` 의 `not_callable_by_llm` 은 그대로다.
- `loop.py` 조회 분기는 `app.er.resolve`/`apply_resolution` 을 재사용하고, `get_person_card` 를 **코드로** 부른다. `app/tools/*` 에 새 툴이 없고 `TOOL_NAMES` 는 7종 그대로(`scripts/tools_check.py` 7/7).
- 조회 턴에 `add_event`·`add_schedule`·`update_person`·`create_person` `tool_call` trace 0, `events`·`schedules`·`person_facts`·`persons` 행 수 변화 0(`assert_no_writes` 류 단언).
- `new_person` 구간의 조회 턴은 `pending_questions` 행을 만들지 않는다(③-2). `identity` 구간은 만든다.
- 답 생성 프롬프트에 들어가는 근거는 `get_person_card` 응답에서 온 값뿐이고(발화 원문 + 카드), 타임라인은 최근 5건까지. 답은 R19 검증기를 거치고, 실패 시 템플릿 문자열(프론트 고정 문구가 아니라 서버가 만든 `reply`).
- 프론트(`web/`) diff 0.

**갱신 이력**
- 2026-10-28 신설(CR-004 문서 이행). 구현은 P5b-query-turn — 완료 해시는 그때 적는다.
- 2026-10-28 **보정 2건(P5b 01-plan 결정 F·I, 사용자 수용)**: ① 결정 2 의 "`resolve()` → `apply_resolution()`" — 조회 턴은 **`resolve()` 만** 부르고 `apply_resolution()` 은 `identity` 되묻기 때만 부른다(merge 경로의 `apply_resolution` 이 `update_person(new_alias)` 로 별칭을 쌓아 "조회 턴 저장 0·`update_person` tool_call 0" 과 동시에 성립하지 않았음 — 저장 0 을 우선). ② 결정 10 의 "'인물 카드 보기' 링크 재사용" — 프론트는 `stored > 0` 일 때만 링크를 붙이므로 조회 턴(저장 0)에는 링크가 없다. 프론트 0 을 지키고 답 끝에 "자세한 건 인물 화면에서 볼 수 있어요." 문장만 둔다. 코드 규칙 "조회 턴에 … `update_person` … `tool_call` trace 0" 은 그대로다.
