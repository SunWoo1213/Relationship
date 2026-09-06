# P1-pilot-dataset · 계획 (01-plan)

상태: 승인됨(사용자 2026-09-06, 02-plan-verify 통과) | 담당: eval-agent (opus, L-002 — 데이터를 만든 쪽이 검수하지 않는다) | 작성: 2026-09-06
태그 — 패키지: P1-pilot-dataset · 닫는 검증: 없음(INDEX.md 패키지 표의 "닫는 R" 열이 `—`. 이 패키지는 R 을 닫지 않고 R3·R4 를 닫는 P4-pilot-eval 의 입력을 만든다) · 기대는 결정: D1 D3 D10 · 구현하는 명세: S3.7 · 관련 원칙: 원칙1 원칙4 원칙7 원칙8 원칙9
의존: P1-schema 완료(`docs/wiki/packages/P1-schema/04-review.md` 115행 `결과: 완료`) · P3-er 완료(`docs/wiki/packages/P3-er/04-review.md` 166행 `결과: 완료`). 다만 이 패키지의 산출물은 JSON 데이터와 검증 스크립트뿐이라 두 패키지의 **코드에 런타임 의존하지 않는다**(스키마 값 집합 `events.type`·관계 태그·위계를 라벨 어휘로 인용할 뿐이다). 게이트: 이 패키지는 P4 이전 단계이므로 P4 게이트 제약을 받지 않는다(backlog 7행 "P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다" 의 대상이 아니다).

## 목표

기획서 5.2(평가·트레이드오프 곡선)와 S3.7 이 요구하는 "한국어 대화 데이터셋 위에서 오병합률과 미검출률을 **분리 측정**한다"를 가능하게 하는 **입력**을 만든다. 즉 이 패키지는 지표를 계산하지 않고, 지표를 계산할 수 있는 **골드 라벨이 붙은 시나리오 30~50건**과 그 라벨을 기계가 검사하는 검증기를 만든다. 승진 호칭 변경·지시대명사·별칭 혼용·정상·신규 등록 판정 다섯 범주를 의도적으로 섞어, P3-baselines 의 베이스라인 3종과 P4-pilot-eval 의 제안 4단계 방식이 **같은 데이터·같은 라벨** 위에서 비교되도록 한다(원칙8: 재현 가능·조작 금지).

## 범위

- 포함:
  - 시나리오 JSON 스키마 확정(eval-harness §1 을 기본으로, P4 가 필요로 하는 필드를 결정 후보로 제시 — "리스크·미결" 참조)과 JSON Schema 파일·검증 스크립트·검증기 단위 테스트.
  - 카테고리별 시나리오 작성 총 **40건**(30~50 범위의 중앙): `promotion` 8 · `pronoun` 8 · `alias` 8 · `normal` 10 · `new_person` 6.
  - 호칭 변이의 **의도적** 포함(eval-harness §1 마지막 줄): 같은 인물을 "김팀장 → 김부장님 → 부장님 → 김선배" 처럼 부르는 변이, 성씨 접두/`님`·`씨` 접미 유무, 직급 없는 별명.
  - 관계 태그(가족·연인·친구·직장·지인) × 위계(상·동·하) 다양성 배분과 그 배분표.
  - 라벨 검수 절차: 검수는 **데이터를 만든 eval-agent 가 아니라 verifier 또는 사용자**가 한다(L-002 취지). 검수 지침·대상 표·기록 파일 경로를 이 패키지가 정하고, 지적 반영까지 포함한다.
  - 위키 registry 행 등록과 저장소 루트 README 의 데이터셋 절 추가, 수용 기준 기계 검증 evidence.
- 이 패키지에서 하지 않는 것:
  - **베이스라인 3종**(문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) — backlog P3 절의 별도 행(P3-baselines).
  - **지표 계산·보정표·트레이드오프 곡선**(`reports/metrics.json`·`reports/calibration.json`·`reports/eval.md`) — P4-pilot-eval.
  - **150건 완성** 과 최종 평가 — P10-final-eval. 여기서는 30~50건 파일럿 규모만.
  - **제품 코드 변경 없음**: `app/` 아래 파일을 만들지도 고치지도 않는다. `alembic/` 마이그레이션도 추가하지 않는다.
  - 실 LLM·실 임베딩 API 호출 없음(검증기는 네트워크를 쓰지 않는다). 비용 실측은 P0-cost 의 `reports/cost_estimate.md`.
  - DB 적재(시나리오를 `persons`/`events` 로 넣는 로더)는 하지 않는다 — 소비자인 P3-baselines·P4-pilot-eval 이 자기 러너에서 읽는다.

## 산출물 (파일 경로)

- `data/scenarios/schema.json` — 시나리오 JSON Schema(Draft 2020-12). 라벨 어휘(`category` 5종, `events.type` 고정 7종, 관계 태그 5종, 위계 3종, `expected_ask_user.allowed` 3종 — `ask_user.kind` 와 별도 enum, R-1)를 enum 으로 고정.
- `data/scenarios/promotion.json` · `data/scenarios/pronoun.json` · `data/scenarios/alias.json` · `data/scenarios/normal.json` · `data/scenarios/new_person.json` — 카테고리별 시나리오 파일(각 파일은 시나리오 배열).
- `data/scenarios/manifest.json` — 파일 목록·카테고리별 건수·관계 태그/위계 배분표·총계(수용 기준의 "30~50건"을 기계가 세는 근거).
- `scripts/validate_scenarios.py` — 스키마 검증 + 교차 무결성 검사(`gold_person_id` 가 그 시나리오의 `persons[].person_id` 안에 있는지, `turn` 인덱스가 `utterances` 범위인지, `id` 전역 유일, 배분표와 실제 건수 일치). 종료 코드 0/1, 네트워크·DB 접근 없음.
- `tests/test_validate_scenarios.py` — 검증기 순수 로직 테스트(정상·위반 케이스 각각. 위반을 못 잡는 검증기는 검증기가 아니다).
- `docs/wiki/packages/P1-pilot-dataset/evidence/<ts>-label-review.md` — 라벨 검수 기록. **작성자는 verifier 또는 사용자**(verifier 의 쓰기 허용 경로가 `evidence/` 이므로 여기에 둔다 — H-3). 형식 고정: 머리 줄 `검수자: verifier (fable, 새 컨텍스트) | 표본: 40/40 | 사용자 검수: 함정 n건·new_person 지나가는 언급 m건`, 지적 표 열 `id | 시나리오 id | 지적 | 상태`(상태 셀 값: `반영 <해시>` / `기각 <사유>` / `열림` — 헤더에 값 이름을 쓰지 않아 grep 오탐 방지, R-10). **`grep -cE '\| *열림 *\|'` 출력 0 이 검수 완료 조건.**
- `docs/wiki/packages/P1-pilot-dataset/evidence/` — 검증기 실행 출력·pytest 출력·건수 집계 출력.
- 위키 registry 표에 데이터셋·스크립트·테스트 행 추가(신규 파일 아님, 기존 표에 행 추가).
- 저장소 루트 README 에 "평가 데이터셋" 절 추가(검증기 실행법 한 줄. 값·키 금지).

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

- [ ] U1 시나리오 스키마 확정 + JSON Schema + 검증기 + 검증기 테스트 (`data/scenarios/schema.json`, `scripts/validate_scenarios.py`, `tests/test_validate_scenarios.py`). eval-harness §1 필드에 "리스크·미결"의 사용자 결정 A~E 결과를 반영해 enum 을 고정한다. 시나리오 0건 상태에서 검증기가 돌고, 일부러 깨뜨린 표본 8종(스키마 위반·미아 `gold_person_id`·범위 밖 `turn`·중복 `id`·미정의 `events.type`·배분표 불일치·`manifest.json` 가상 성명 목록 밖 이름·`ambiguous_mention_count` 와 실제 `ambiguous:true` 수 불일치)을 전부 잡는 것이 완료 판정(R-2·R-9). 교차 검사 예외(H-1): `mentions[].ambiguous == true` 인 mention 만 `gold_person_id: null` 을 허용하고, `ambiguous` 가 없거나 false 면 null 은 FAIL. / Refs: P1-pilot-dataset S3.7 S3.1 원칙8
- [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 호칭이 바뀌어도 같은 인물(D6 별칭 누적 정책과 같은 방향), 별칭 혼용 8건은 "본명/직급/별명/줄임말"이 한 시나리오 안에서 섞이게 한다. 두 카테고리 모두 **오병합 유도 함정**(비슷한 호칭의 다른 인물)을 최소 3건 포함하고 그 건의 `gold_person_id` 를 다르게 준다(원칙1 비대칭 비용을 측정 가능하게). / Refs: P1-pilot-dataset S3.7 D6 D10 원칙1
- [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` 은 "걔·그 사람·아까 걔·그분"의 선행사가 앞 턴에 있는 경우만 쓰고, 선행사가 사람도 정할 수 없는 발화는 그 mention 을 `ambiguous: true`·`gold_person_id: null` 로 라벨한다(H-1 — 결정 D 확정 규칙. 시나리오 자체는 건수에 포함, 해당 mention 만 지표 분모 제외). `normal` 10건은 함정 없는 기준선. / Refs: P1-pilot-dataset S3.7 원칙8
- [ ] U4 `new_person` 6건 작성. 처음 등장하는 인물(등록 대상)과 **지나가는 언급**(연예인·모르는 사람 등, 등록하면 안 되는 것)을 섞어 D1 의 확인형 등록이 옳게 동작하는지 측정 가능하게 한다. 기대 `ask_user` 어휘는 `identity`/`new_person`/없음 중 하나를 **허용 집합**으로 라벨한다(임계치에 따라 달라지므로 단일 정답으로 고정하지 않는다 — D10). / Refs: P1-pilot-dataset S3.7 D1 D10 원칙1
- [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `validate_scenarios.py` 전건 통과 출력, `manifest.json` 의 카테고리·관계 태그·위계 배분표 생성, 그리고 검수자가 볼 수 있게 시나리오를 사람이 읽는 표로 덤프한다(발화 / 언급 표면형 / 골드 인물 / 카테고리 / 함정 여부). 이 단위는 **검수를 하지 않는다** — 검수 요청까지다. / Refs: P1-pilot-dataset S3.7 원칙8 L-002
- [ ] U6 라벨 검수 지적 반영. verifier 또는 사용자가 `evidence/<ts>-label-review.md` 에 남긴 지적(라벨 오류·함정 부족·구어체 부족·개인정보 의심)을 수정하고 U5 의 검증·배분표를 재생성한다. 검수 없이 이 단위를 건너뛰면 수용 기준의 "라벨 검수 완료"가 성립하지 않는다. / Refs: P1-pilot-dataset S3.7 원칙8 원칙9
- [ ] U7 registry 행 추가 · README "평가 데이터셋" 절 · 수용 기준 기계 검증 evidence(건수 30~50 확인 출력, 검증기 rc=0 출력, pytest 출력, 검수 완료 출력 = `evidence/<ts>-label-review.md` 에 대한 `grep -c "반영 "` 과 `grep -c "열림"`(후자 0))를 `evidence/` 에 저장. / Refs: P1-pilot-dataset S3.7 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 파일럿 데이터셋 30~50건 (승진·대명사·별칭·정상·신규) / 의존: 평가 명세(resolution-plan 3.7) / 수용기준: `data/scenarios/` JSON, 라벨 검수 완료

  해석(기계 판정 방법, 위 문장을 바꾸지 않는다):
  - "30~50건" → `scripts/validate_scenarios.py` 가 세는 총 시나리오 수가 30 이상 50 이하. 계획값 40.
  - "(승진·대명사·별칭·정상·신규)" → `category` 5종이 모두 1건 이상이며 배분표가 `manifest.json` 과 일치.
  - "`data/scenarios/` JSON" → 해당 디렉터리에 스키마 검증을 통과하는 JSON 파일이 존재(rc=0 출력이 evidence 에 있다).
  - "라벨 검수 완료" → `evidence/<ts>-label-review.md` 머리 줄에 **eval-agent 가 아닌** 검수자 이름이 있고, 지적 표의 `열림` 상태가 0(`grep -c "열림"` 출력 0)이며 반영 상태에 U6 커밋 해시가 있다.

## 리스크 · 미결

**사용자 결정이 필요한 항목(결정은 메인 세션·사용자가 한다. U1 착수 전에 필요)**

- 결정 A — **인물 메타를 P1 에 넣는가.** eval-harness §1 스키마에는 `gold_person_id` 문자열뿐이다. 제안: 시나리오마다 `persons: [{person_id, display_name, relation_tag, hierarchy, aliases[]}]` 를 넣는다. 이유: P3-baselines 의 문자열 완전일치·임베딩 단독은 "후보 인물 집합"이 없으면 아예 돌릴 수 없고, 제안 방식의 `s_rule`(위계·관계 태그·호칭 사전 호환)은 관계 태그·위계 없이는 계산되지 않는다(D3). 미루면 P4 가 자기 데이터를 지어내게 되고 그때는 원칙8 위반이 된다. **P1 포함 권장.**
- 결정 B — **이벤트 골드 라벨을 P1 에 넣는가.** 제안: `events: [{turn, type, occurred_at_kind}]` 최소 형태로 P1 에 넣되, `type` 은 고정 7종(`conflict/praise/meal/meeting/personal_share/favor/other`)만 쓰고, `occurred_at` 은 절대 시각이 아니라 `relative|absolute|none` 종류만 라벨한다. 이유: 절대 시각 라벨은 "오늘"의 기준일에 묶여 재현성이 깨진다(원칙8). 정밀 `occurred_at` 정규화 평가는 **P10 으로 미룸 권장**. `type` 라벨까지 미루면 S3.7 의 "추출 F1"을 P4 에서 못 낸다.
- 결정 C — **일정(schedule) 골드 라벨.** 제안: **P10 으로 미룸.** 파일럿의 목표 지표는 오병합률·미검출률·보정표이고, 일정 추출은 P5-loop 이후에야 파이프라인이 존재한다. 대신 `normal` 몇 건에 일정 발화를 섞어 두어 P10 에서 라벨만 덧붙일 수 있게 한다.
- 결정 D — **기대 `ask_user` 라벨의 형태.** 제안: 단일 정답이 아니라 `expected_ask_user: {allowed: ["identity","new_person","none"]}` 허용 집합. 이유 D10 — 같은 발화도 `T_merge` 를 0.5→0.95 로 스윕하면 구간이 바뀐다. 단일 정답으로 고정하면 곡선 자체가 라벨을 위반하게 된다. 함께 `ambiguous: true` 플래그(선행사·동명이인이 사람도 못 정하는 건)를 둘지 결정 필요 — 제안: 둔다, 단 지표 계산에서 제외 집합으로 명시.
- 결정 E — **시나리오 사전 상태(seed) 표현.** ER 은 "이미 등록된 인물"이 있어야 판정한다. 제안: 각 시나리오에 `seed_persons`(대화 전 이미 메모리에 있는 인물 id 목록)를 두고, `new_person` 카테고리는 이 목록이 비거나 관련 없는 인물만 갖게 한다. 미정하면 P4 러너가 시나리오마다 임의로 DB 를 채우게 되어 베이스라인 비교의 동일 조건이 깨진다.
- 결정 F — **생성 방식.** 후보: (i) 전수 수작성 (ii) LLM 초안 + 사람 검수 (iii) LLM 전량 생성. 제안: **(ii) 혼합.** 원칙8과의 관계: 데이터셋 조작 금지는 "평가 대상 파이프라인에 유리하도록 데이터를 고르거나 고치지 않는다"는 뜻이므로 LLM 초안 자체는 금지가 아니다. 대신 (a) 생성에 쓴 모델·프롬프트·시드를 `manifest.json` 에 기록하고 (b) **초안 생성 모델과 평가 대상 판정 모델이 같은 경우 그 사실을 명시**하며 (c) 골드 라벨은 사람/verifier 검수를 거친 것만 유효로 한다. (iii) 은 금지 — 라벨과 데이터를 같은 모델이 만들면 평가가 자기 채점이 된다.
- 결정 G — **검수 범위와 검수자.** 제안: verifier 가 **전건 40건 라벨 검수**(표본이 아니라 전수. 40건은 전수 검수가 가능한 규모다). 사용자 검수는 함정 건(오병합 유도)과 `new_person` 지나가는 언급 건에 한정. 검수자가 verifier 인 경우에도 기록은 `label-review.md` 한 파일.

**결정 확정 — 사용자 (2026-09-06, 메인 세션 AskUserQuestion, 전 항목 architect 권장안 채택)**

- A 채택: 시나리오마다 `persons[{person_id, display_name, relation_tag, hierarchy, aliases[]}]` 포함.
- B 채택: `events[{turn, type, occurred_at_kind}]` — `type` 고정 7종, `occurred_at_kind ∈ relative|absolute|none`. 정밀 `occurred_at` 정규화 평가는 P10.
- C 채택: 일정(schedule) 골드 라벨은 P10 으로 미룸. `normal` 일부에 일정 발화만 섞어 둔다.
- D 채택: `expected_ask_user: {allowed: [...]}` 허용 집합 + `ambiguous` 플래그. **H-1 확정(사용자)**: (1) `ambiguous` 는 `mentions[]` 단위 필드, (2) `ambiguous: true` 인 mention 만 `gold_person_id: null` 허용(검증기 예외), (3) 그 시나리오는 30~50 건수와 배분표에 포함하되 `manifest.json` 에 `ambiguous_mention_count` 를 별도로 두고 오병합률·미검출률·F1 분모에서 해당 mention 을 제외한다. `allowed` enum 은 `ask_user.kind` 와 별도 정의(`identity/new_person/none`, R-1).
- E 채택: 시나리오마다 `seed_persons` 명시. `new_person` 은 비거나 무관한 인물만.
- F 채택: (ii) LLM 초안 + 사람/verifier 검수. **H-2 확정(사용자)**: 생성 경로는 **eval-agent(opus) 가 자기 컨텍스트에서 JSON 을 직접 작성**한다(스크립트 API 호출 없음 — "하지 않는 것"의 네트워크 미사용 문장 유지). `manifest.json` 필수 키: `generator.model_id`(eval-agent 모델 id), `generator.prompt_ref`(위임 프롬프트를 저장한 `evidence/<ts>-gen-prompt.md` 경로), `generator.seed: null` + `seed_reason: "대화형 생성"`, `generator.same_family_as_judge: true`(P3-er 판정 모델과 같은 공급자 계열). **금지: 초안 위임 프롬프트에 ER 판정 프롬프트·호칭 사전(`app/er/dictionary`)·임계치 값을 넣지 않는다** — "판정하기 쉬운 데이터만 만드는" 편향 차단. 검수 거친 라벨만 유효, (iii) 전량 LLM 생성(검수 없음) 금지.
- G 채택: verifier 전건(40건) 라벨 검수 + 사용자는 함정 건·`new_person` 지나가는 언급 건 검수. **H-3 확정(사용자)**: 기록은 `evidence/<ts>-label-review.md` 한 파일(산출물 절의 고정 형식). 검수는 **새 verifier 컨텍스트**에서 하고 P4 04-review 에서 라벨을 재해석하지 않는다(R-3, P4 01-plan 인계).

**리스크**

- **개인정보.** 실제 지인·실존 인물의 이름·직장·연락처를 넣지 않는다. 가상 성명 목록을 `manifest.json` 에 두고 그 목록 밖 이름이 나오면 검증기가 FAIL 하게 한다(U1 위반 표본 7종째로 확정, R-2 — 결정 A 와 함께 확정). 연예인 언급이 필요한 `new_person` 건은 실명 대신 "○○ 아이돌" 같은 일반 명사로 쓴다.
- **한국어 구어체 부족.** LLM 초안은 문어체·완결 문장으로 기울고, 실제 사용자는 "오늘 김팀장이랑 또 부딪힘ㅋㅋ", "걔 어제 밥 사줬는데" 처럼 쓴다. 완화: 시나리오마다 (a) 조사 생략·종결어미 축약 (b) 오타 1개 이하 (c) 이모지·ㅋㅋ 허용 (d) 발화 길이 8~60자 규칙 (e) 시나리오당 턴 수 2~6 규칙(U2 생성 프롬프트에서 도입, FIX baee71e 검사 13 으로 기계화 — U5 에서 계획에 명문화)을 두고 검수 항목에 넣는다. 이 리스크가 현실화되면 P4 수치가 실사용보다 좋게 나온다 — 즉 **과대평가 방향의 편향**이므로 반드시 검수에서 잡는다.
- **표본 크기.** 30~50건은 카테고리당 6~10건이라 오병합률의 신뢰구간이 넓다. P4 결과는 "방향과 실패 유형"을 보는 데 쓰고, 운영 임계치 확정은 P10-final-eval 150건에서 한다는 것을 P4 계획에 명시해야 한다.
- **비용.** S3.7 곡선은 시나리오 × 4방식 × 10임계치다. 40건이면 1600 판정, 150건이면 6000 판정. P0-cost(`reports/cost_estimate.md`)가 아직 열려 있어 파일럿 총액이 미상이다. 완화: 결정 F 의 (ii) 로 데이터 생성 비용을 낮추고, P4 는 `reports/metrics.json` 재사용으로 재실행을 피한다(eval-harness §5).
- **함정 난이도의 자의성.** 오병합 유도 건을 너무 쉽게/어렵게 만들면 오병합률이 사실상 저자가 정한 값이 된다. 완화: 함정 건에 `trap: {kind, reason}` 을 라벨하고 검수자가 난이도를 판정하게 한다. 수치가 나쁘게 나오는 것도 결과다(원칙8) — 데이터를 되돌리지 않는다.
- **P3-er 인계 권고와의 관계(P3-er 04-review §6·§7).** 두 건 모두 **데이터셋 형식에 영향을 주지 않는다**는 것을 여기서 확인해 둔다: F-251dc2(trace `candidates[].similarity/aliases_matched` 가 `s_emb`·전체 별칭의 복제)는 P4 가 trace 를 읽어 재계산할 때의 문제이지 골드 라벨의 문제가 아니다. F-bdd6c5(`ERConfig.top_k` 가 실제 검색 K 에 무효)는 **P4 가 `top_k` 를 스윕하지 않는다**는 제약이므로, 데이터셋에 `top_k` 를 전제한 필드를 만들지 않는다. 둘 다 P4-pilot-eval 01-plan 이 결정한다(이 패키지의 결정 사항 아님).
- **소비자와의 계약 미확정.** 스키마를 P1 에서 굳혀도 P3-baselines·P4-pilot-eval 이 다른 필드를 원하면 데이터 재작업이 생긴다. 완화: 결정 A~E 를 U1 전에 사용자 결정으로 닫고, 스키마 파일에 `schema_version` 을 둔다. 변경이 생기면 FIX 가 아니라 `schema_version` 증가 + `manifest.json` 갱신.

**미결(사용자 결정 대상이 아닌, 실행 중 정하는 것)**

- 파일 분할 단위(카테고리별 5파일) 대신 시나리오 1건 1파일로 갈지 — 커밋 diff 가독성 문제. 계획값은 카테고리별 5파일.
- `id` 규칙: `sc-001` 전역 연번(eval-harness §1 예시)과 `promo-001` 카테고리 접두 중 택1. 계획값은 전역 연번 유지(스킬 예시와 일치).

## 읽은 카드

- `docs/backlog.md` — "구현 순서" P1 절(22~23행) · P3 절(31~32행) · P4 게이트 절(36행) · 착수 준비의 LLM 비용 실측 행(15행) · 머리말 6~8행(일정 폐기·P4 게이트·명세 권위) · 리스크 로그(67~73행)
- `docs/wiki/specs/S3.7-eval-spec.md` — 전체(9줄)
- `.claude/skills/eval-harness/SKILL.md` — §1 데이터셋 스키마 · §2 지표 · §5 재현성/비용(§3 베이스라인·§4 곡선은 이 패키지 범위 밖이라 경계 확인용으로만 봄)
- `docs/wiki/decisions/D01-new-person-confirm.md` — "코드에서 지켜야 할 것" 절 + 파급(`ask_user_rate_by_kind`)
- `docs/wiki/decisions/D03-confidence-formula.md` — 결정 3신호 정의 + 보정 절(`s_llm` 구간별 정답률은 P4)
- `docs/wiki/decisions/D10-two-thresholds.md` — 결정·방향·"코드에서 지켜야 할 것" 절
- `docs/wiki/packages/P3-er/04-review.md` — §6 신규 소견 목록(F-251dc2, F-bdd6c5 포함) · §7 "P4-pilot-eval 에 넘기는 것" 전체 · 마지막 2행(`결과: 완료`, 승인)
- `docs/wiki/packages/P1-schema/04-review.md` — 108~116행(인계 사항·`결과: 완료`)
- `docs/wiki/registry.md` — 전체 표를 `data/`·`scenario`·`eval` 로 확인. **데이터셋 종류 행 0개, `data/` 로 시작하는 경로 0개, `scripts/validate_scenarios.py` 없음** → 중복 구현 아님. 기존 `scripts/` 행은 `embed_pilot.py`·`db_check.py`·`schema_check.py`·`tools_check.py`·`backfill_embeddings.py`·`er_smoke.py`·`gitlog.sh` 로 성격이 다름
- `docs/wiki/review-index.md` — 표 전체(이 패키지가 닫는 R 없음. R3·R4 는 P4-pilot-eval, R13 은 P0-cost 가 닫는다)
- `docs/wiki/INDEX.md` — 패키지 id 표(59~79행), 태그 어휘 표
- `docs/wiki/CURRENT.md` — `active: none`, 메모(P1-pilot-dataset·P0-cost 미착수)
- `.claude/gitlog.md` — 브랜치 절(dev `bdf9f70`, main `0527ab8`, 승격 대기 1) · 최근 커밋 20건(P3-er U1~U9 `2b82882`~`b3bcc2d`, 닫는 커밋 `0527ab8`) · 미커밋 변경(`docs/wiki/journal.md`). S3.7 을 `Refs:` 로 다는 커밋은 아직 없다 — 평가 계열 첫 패키지임을 확인
- `.claude/scripts/verify-plan.sh` — 검사 1~7 항목(수용 기준 글자 일치·의존 04-review·산출물 registry 중복 규칙 확인용)
- `docs/wiki/templates/plan.md` — 이 문서의 형식
- CLAUDE.md(컨텍스트 주입) — 원칙1·4·7·8·9, `events.type` 고정 집합, 관계 태그 5종 × 위계 3종
