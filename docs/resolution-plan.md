# 기획서 검증 항목 해결 계획서

> 대상: `docs/proposal-review.md`의 20개 항목.
> 전제: **개발 일정(기획서 7장, CLAUDE.md·backlog의 M1~M4 마일스톤)은 폐기한다.** 이 계획서는 날짜 대신 **의존성 순서**로만 작업을 배열한다.
> 상태: 계획 단계. 이 문서의 어떤 항목도 아직 구현하지 않았다.
> 작성일: 2026-09-03

---

## 0. 일정 폐기로 달라지는 것

| 검증 항목 | 처리 |
|-----------|------|
| 1. ER이 DB에 의존 | 날짜 충돌은 사라진다. 의존성(스키마 → ER)만 3장의 순서로 남긴다. |
| 2. 기획서와 하네스 마일스톤 불일치 | 양쪽 마일스톤을 모두 삭제하므로 해소된다. |
| 20. AWS 크레딧 조건 | 기간 계산이 없어지므로 "크레딧 잔액 확인 + Budgets 알림"만 남긴다. |

일정 폐기 시 고쳐야 할 파일과 위치(문서 정합화 단계에서 수행):

| 파일 | 삭제·수정할 내용 |
|------|------------------|
| `CLAUDE.md` | 문서 전체에 마일스톤 언급 없음. `docs/backlog.md` 설명만 유지 |
| `docs/backlog.md` | "마일스톤 (4개월)" 절과 `(M1)` 접두어 형식 삭제. 태스크 형식을 `- [ ] [담당] 태스크 / 의존: ... / 수용기준: ...`로 변경 |
| `.claude/agents/architect.md` | "작업 절차 1"의 4개월·4마일스톤 규칙 삭제. "1개월 차 점검" 문구를 "ER 파일럿 평가를 루프·프론트보다 먼저"로 변경 |
| `docs/proposal.md` | 원본이므로 본문은 유지. 상단 안내문에 "7장 개발 일정은 폐기됨, `docs/resolution-plan.md` 참조" 한 줄 추가 |

---

## 1. 먼저 내려야 할 결정 (D1~D10)

각 결정에는 권장안을 붙였다. 권장안을 그대로 승인하면 2장부터 바로 진행할 수 있다. 사용자만 정할 수 있는 것은 **[사용자]**, 권장안으로 충분한 것은 **[권장안 승인]** 으로 표시했다.

### D1. 신규 인물 등록 시 확인 여부 — 검증 6 **[권장안 승인]**

- 권장: **확인형.** 확신도 低이면 `ask_user(kind="new_person")`로 "○○을 기억해둘까요?"를 묻고, 승인 시 `create_person`.
- 이유: 데모 1번·부록 채팅 화면이 확인형이고, "모른다를 판단하는 행동"이라는 설계 서사와 일치한다. 자동 등록은 오탐 인물(예: 연예인, 지나가는 언급)을 카드로 만든다.
- 파급: `ask_user`에 `kind` 인자(`identity` / `new_person` / `schedule`)가 생기고, 지표 "ask_user 발생률"을 kind별로 분리 집계한다.

### D2. `ask_user`의 실행 모델 — 검증 7 **[권장안 승인]**

- 권장: **비동기 대기 질문.** `ask_user`는 질문을 DB에 저장하고 `{question_id, status: "pending"}`을 즉시 반환한다. 에이전트 루프는 그 턴을 종료한다. 사용자가 칩을 누르면 `POST /answers/{question_id}`가 루프를 재개한다.
- 이유: 웹 채팅에서 툴이 한 요청 안에서 사용자 답을 기다릴 수 없다. 인메모리 대기는 서버 재시작에 사라진다.
- 파급: `pending_questions` 테이블 추가(3장 스키마 v2). 시그니처는 `ask_user(kind, question, options, context) → PendingQuestion`으로 바뀐다. "별도 툴 유지" 원칙은 그대로다.

### D3. 확신도 산출식 — 검증 4 **[권장안 승인]**

- 권장: 세 신호를 다음처럼 정의한다.
  - `s_llm`: LLM이 **구조화 출력**으로 직접 내는 0~1 점수(로그 확률 아님).
  - `s_emb`: 후보 검색의 코사인 유사도(0~1로 정규화).
  - `s_rule`: 규칙 필터 통과 항목 수 / 검사 항목 수(위계 일치, 관계 태그 일치, 호칭 사전 호환).
  - `confidence = w1·s_llm + w2·s_emb + w3·s_rule`, 초기 가중치 0.5 / 0.3 / 0.2. 가중치는 파일럿 평가에서 조정한다.
- **보정표**: `s_llm` 구간(0.1 단위)별 실제 정답률을 파일럿 세트로 산출해 `reports/calibration.json`에 저장한다. 이 표가 "자기보고 점수를 왜 믿을 수 있는가"의 근거가 된다.
- 파급: 기획서 3.4·10장, `entity-resolution` 스킬의 "LLM 출력 확률" 문구 수정.

### D4. 임베딩 공급자와 차원 — 검증 5 **[사용자]**

- Claude API에는 임베딩 엔드포인트가 없다. 별도 공급자를 정해야 한다.
- 결정 방법: 후보 공급자 2곳을 골라 **한국어 짧은 호칭 30개**("팀장", "김팀장", "부장님", "그 사람", "이모", "과장님" 등)로 유사도 행렬을 뽑아 비교한다. "팀장↔부장님"이 "팀장↔이모"보다 높게 나오는 쪽을 택한다.
- 차원: 결정된 모델의 출력 차원으로 `person_embeddings`·별칭 임베딩의 `vector(N)`을 확정한다. 기획서의 1536은 확정값이 아니다.
- 이 결정은 4장 "착수 준비"에서 파일럿 스크립트로 수행하며, 그 스크립트가 유일하게 허용되는 "결정용 코드"다.

### D5. 임베딩 단위 — 검증 9 **[권장안 승인]**

- 권장: **별칭 단위 임베딩.** `person_aliases`에 `embedding` 컬럼을 두고, 후보 검색은 별칭 top-K → 인물별 최대값으로 집계한다. `person_embeddings` 테이블은 삭제한다.
- 이유: "김팀장"으로 만든 벡터 하나로 "부장님"을 찾을 수 없다. 별칭이 쌓일수록 검색이 좋아진다는 4장의 주장이 이 구조에서만 성립한다.

### D6. 승진 후 표시 이름 — 검증 18 **[권장안 승인]**

- 권장: `display_name`은 **사용자가 확인한 가장 최근 호칭**으로 갱신하고, 이전 호칭은 `person_aliases`에 남긴다. 카드 상단에 "이전: 김팀장" 형식으로 이력을 표시한다.
- 데모 5번 브리핑 문구는 "김부장 회의"로 바뀐다. 승진 반영이 눈에 보이므로 데모에 유리하다.

### D7. CloudFront → EC2 TLS — 검증 14 **[권장안 승인]**

- 권장: EC2에 Caddy(자동 Let's Encrypt)를 리버스 프록시로 두고 CloudFront 오리진을 HTTPS로 설정한다. ALB는 비용 때문에 쓰지 않는다.
- 부수 결정: RDS는 프라이빗 서브넷(NAT 불필요), EC2만 퍼블릭 서브넷. CloudFront용 ACM 인증서는 us-east-1에서 발급.

### D8. 제목의 "관계 그래프" — 검증 17 **[사용자]**

- 선택지: (a) 제목을 "개인 관계 메모리 기반 브리핑 시스템"으로 바꾼다. (b) 제목 유지, 2장 제외 사유에 "인물 간 관계(엣지)는 향후 확장, 현재는 사용자–인물 관계만"을 명시한다.
- 권장: (a). 심사 질문을 원천 차단한다.

### D9. 반복 패턴 감지 규칙 — 검증 11 **[권장안 승인]**

- 권장: 규칙 기반. 같은 인물의 `events.type`이 최근 90일 내 **3회 이상**이면 승격 시 `person_facts(key="pattern:{type}", value="{n}회 (날짜 목록)", confidence=1.0)`을 생성·갱신한다. LLM은 패턴 문장화만 담당한다.
- 이유: 규칙이면 재현 가능하고 근거(이벤트 ID 목록)가 자동으로 남는다. 2장 포함 목록에 "반복 패턴 감지"를 추가한다.

### D10. 임계치 정의와 스윕 축 — 검증 3 **[권장안 승인]**

- 임계치는 두 개다. `T_merge`(이상이면 자동 연결), `T_new`(미만이면 신규 확인 질문). 그 사이는 동일성 확인 질문.
- 트레이드오프 곡선의 x축은 **`T_merge`** 하나로 고정하고 `T_new`는 0.3으로 둔다. y축은 오병합률과 ask_user(identity) 발생률.
- 문장 수정: "T_merge를 **높이면** 오병합↓ 질문↑". 기획서 5.2와 `eval-harness` 스킬 4절 모두 고친다.

### 그 밖의 소항목 (결정 불필요, 문서 정합화에서 처리)

| 검증 항목 | 처리 |
|-----------|------|
| 10. 툴 시그니처 불일치 | 3장 "툴 시그니처 v2"로 확정 |
| 8. 시맨틱 → 원문 링크 | 3장 스키마 v2에 `fact_sources` 추가 |
| 12. 브리핑 트리거·푸시 구독 | 3장 스키마 v2에 `push_subscriptions` 추가, 주기 작업 설계 |
| 13. LLM 비용 미산정 | 4장 착수 준비에서 시나리오 1건당 토큰 실측 후 예산 항목 추가 |
| 15. 데모 날짜 | 리허설 스크립트 작성 시 발표일 기준 재계산. 기획서 원본은 유지 |
| 16. 예시 수치 | 기획서 상단 안내문에 "부록 A의 수치는 예시"를 명시 |
| 19. 브리핑 제안 vs 상담 제외 | 2장 제외 사유에 경계 문장 추가: "브리핑 제안은 기록된 사실에서 도출되는 한 줄 행동 제안으로 한정" |

---

## 2. 문서 정합화 (결정 승인 후, 코드 작성 전)

담당: architect. 산출물: 아래 파일들의 수정본. 완료 조건: 검증 문서의 20개 항목이 각각 "해소됨 / 폐기 / 3장으로 이관" 중 하나로 표시된다.

| 파일 | 수정 내용 | 근거 항목 |
|------|-----------|-----------|
| `CLAUDE.md` | 데이터 모델을 3장 스키마 v2로 교체. 툴 7종 시그니처를 v2로 교체. 마일스톤 언급 제거. 불변 원칙 6에 "임계치는 T_merge/T_new 두 개" 추가 | 0장, D2, D5, D10, 8, 10, 12 |
| `docs/backlog.md` | 마일스톤 절 삭제. 태스크 형식을 의존성 기반으로 변경. 3장의 작업 패키지를 태스크로 옮김 | 0장 |
| `.claude/agents/architect.md` | 4개월·마일스톤 규칙 삭제. "ER 파일럿 평가를 루프·프론트보다 먼저" 원칙으로 대체 | 0장 |
| `.claude/agents/backend-agent.md` | ask_user 비동기 모델, 별칭 임베딩, fact_sources 추가 반영 | D2, D5, 8 |
| `.claude/skills/entity-resolution/SKILL.md` | "확신도 산출"을 D3 식으로 교체. 임계치 2개 명시. 별칭 임베딩 반영 | D3, D5, D10 |
| `.claude/skills/eval-harness/SKILL.md` | 4절 임계치 방향 수정, x축 = T_merge 명시. ask_user 발생률을 kind별 분리. 보정표 산출물 추가 | D1, D3, D10 |
| `.claude/skills/agent-observability/SKILL.md` | trace에 `confidence_breakdown`(s_llm/s_emb/s_rule)과 `pending_question_id` 필드 추가 | D2, D3 |
| `docs/proposal.md` | 상단 안내문만 수정: 7장 폐기, 부록 수치는 예시, 결정 사항은 이 계획서 참조 | 0장, 16 |
| `docs/proposal-review.md` | 각 항목에 상태 열 추가 | — |

---

## 3. 설계 확정 사항 (구현의 입력이 되는 명세)

이 절은 "무엇을 만들 것인가"를 못 박는다. 아직 코드가 아니다.

### 3.1 스키마 v2

```sql
persons(id, user_id, display_name, relation_tag, hierarchy, created_at, updated_at)
person_aliases(id, person_id, alias, source, embedding vector(N), confirmed_at)  -- N은 D4에서 확정
person_facts(id, person_id, key, value, confidence, updated_at)
fact_sources(fact_id, event_id)                                                  -- 검증 8: 시맨틱 → 원문
events(id, person_id, type, content, raw_utterance, occurred_at, created_at)
schedules(id, person_id, title, scheduled_at, briefed_at)
pending_questions(id, session_id, kind, question, options, context, answer, created_at, answered_at)  -- D2
push_subscriptions(id, user_id, endpoint, keys, created_at)                      -- 검증 12
agent_traces(id, session_id, step, tool_name, input, output, tokens_in, tokens_out, created_at)
```

- `person_embeddings` 삭제 (D5).
- `events.type` 고정 집합: `conflict / praise / meal / meeting / personal_share / favor / other`. 추출 F1 계산의 라벨 집합이 된다 (검증 10).
- `agent_traces.output`에 ER 단계일 때 `candidates[]`, `confidence_breakdown{}`, `decision`을 JSON으로 넣는다.

### 3.2 툴 시그니처 v2

| 툴 | v2 시그니처 | 변경 이유 |
|----|-------------|-----------|
| `search_person` | `(query: str, hints?: {hierarchy?, relation_tag?}) → Candidate[]` | 규칙 필터에 위계·관계 힌트 전달 (검증 10) |
| `create_person` | `(display_name, aliases: str[], relation_tag, hierarchy) → Person` | `tags` → 단수 `relation_tag` (검증 10) |
| `update_person` | `(person_id, facts?: {key,value}[], new_alias?: str, display_name?: str) → Person` | 승진 시 별칭 누적·표시 이름 갱신 경로 (검증 10, D6) |
| `add_event` | `(person_id, type, content, occurred_at, raw_utterance) → Event` | 원문 보존을 툴 인자로 강제 (검증 10). 런타임이 현재 발화를 자동 채움 |
| `add_schedule` | `(person_id, title, scheduled_at) → Schedule` | 변경 없음 |
| `get_briefing` | `(person_id, schedule_id?) → Briefing` | 어느 일정의 브리핑인지 명시. `briefed_at` 기록 |
| `ask_user` | `(kind, question, options, context) → PendingQuestion` | 비동기 모델 (D1, D2) |

`Candidate`는 `{person, similarity, aliases_matched, rule_flags}`를 담아 3단계 LLM 판정의 입력이 된다.

### 3.3 ER 4단계 + 확신도 (D3, D10 반영)

```
1. 후보 검색   별칭 임베딩 top-K(K=10) → 인물별 max 유사도 → s_emb
2. 규칙 필터   호칭 사전 호환 / 위계 일치 / 관계 태그 일치 → 통과 후보만, s_rule
3. LLM 판정   대화 맥락 + 후보 정보 → {matched_person_id | null, s_llm, reason} (구조화 출력)
4. 분기        confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule
              ≥ T_merge      → 연결 (update_person으로 별칭 누적)
              [T_new, T_merge) → ask_user(kind="identity")
              < T_new         → ask_user(kind="new_person")   ← D1
```

- 승진 케이스: 2단계에서 위계 제약을 "인접 위계까지 허용"으로 완화한 재검색 1회. 이 재검색 여부를 trace에 남긴다.
- 초기값 `T_merge = 0.8`, `T_new = 0.3`. 파일럿 평가 후 곡선으로 확정.

### 3.4 ask_user 프로토콜 (D2)

```
턴 N   사용자 발화 → 루프 → ask_user 호출 → pending_questions 저장 → 응답에 question_id 포함 → 턴 종료
턴 N+1 사용자가 칩 선택 → POST /answers/{question_id} → 루프가 저장된 context로 재개 → 후속 툴 호출
```

- 답 없이 다음 발화가 오면 대기 질문은 유지하되 새 발화를 우선 처리한다. 대기 질문은 24시간 후 만료.
- 프론트 채팅 화면의 "확인 칩"은 `pending_questions`의 미답변 항목을 렌더링한 것이다.

### 3.5 메모리 승격과 패턴 감지 (D9, 검증 8·11)

- 승격 트리거: 같은 인물의 미승격 `events`가 5건 이상.
- 승격 동작: LLM이 사실 후보를 뽑고 `person_facts`에 upsert, 각 사실에 `fact_sources`로 근거 이벤트를 연결.
- 패턴: 같은 `type`이 90일 내 3회 이상 → `pattern:{type}` 사실 생성. 근거 이벤트를 `fact_sources`에 연결.
- 원문은 어떤 경우에도 삭제하지 않는다.

### 3.6 브리핑 트리거와 푸시 (검증 12)

- 백엔드 컨테이너 내 주기 작업(1분 간격): `schedules.scheduled_at - now() ≤ 24h AND briefed_at IS NULL`인 항목에 대해 `get_briefing` 실행 → 웹푸시 발송 → `briefed_at` 기록.
- 수동 트리거 엔드포인트 `POST /briefings/run`은 같은 함수를 호출한다. 데모의 "시간 앞당기기"와 "발표자 수동 트리거 버튼"이 이걸로 해결된다.

### 3.7 평가 명세 (D3, D10)

- 데이터셋 스키마는 `eval-harness` 스킬 1절 유지. 카테고리에 `new_person`(신규 등록 판정) 추가.
- 지표 추가: `calibration`(s_llm 구간별 정답률), `ask_user_rate_by_kind`.
- 곡선: x = T_merge ∈ {0.5, 0.55, …, 0.95}, y = 오병합률·ask_user(identity) 발생률·미검출률. `T_new` 고정.
- 베이스라인 3종 + 제안 방식, 동일 데이터·동일 지표.

---

## 4. 착수 준비 (구현 직전에 하는 것, 코드 최소)

| 작업 | 담당 | 산출물 | 완료 조건 |
|------|------|--------|-----------|
| git 저장소 초기화, `.gitignore`, `.env.example` | 사용자 | 첫 커밋 | `git log`에 1건 |
| AWS Budgets 알림 $10/$30/$50, 크레딧 잔액 확인 | 사용자 | 콘솔 스크린샷 또는 메모 | 알림 3개 활성 |
| 임베딩 공급자 파일럿 (D4) | backend-agent | `scripts/embed_pilot.py`, `reports/embed_pilot.md` | 호칭 30개 유사도 행렬 2종, 선택 근거 1문단 |
| LLM 비용 실측 (검증 13) | eval-agent | `reports/cost_estimate.md` | 시나리오 1건당 토큰과 150건×4방식×10임계치 총액 추정 |
| 로컬 docker-compose (pgvector) | backend-agent | `docker-compose.yml` | `SELECT '[1,2,3]'::vector` 성공 |

---

## 5. 구현 순서 (의존성 기반, 날짜 없음)

각 패키지는 앞 패키지의 산출물을 입력으로 쓴다. 병렬 가능한 것은 같은 번호에 묶었다.

| 순서 | 패키지 | 담당 | 의존 | 완료 조건 |
|------|--------|------|------|-----------|
| P1 | 스키마 v2 마이그레이션 (Alembic) | backend-agent | 4장 | 9개 테이블 생성, `events.type` 제약 존재 |
| P1 | 파일럿 데이터셋 30~50건 (승진·대명사·별칭·정상·신규) | eval-agent | 3.7 | `data/scenarios/` JSON, 라벨 검수 완료 |
| P2 | 툴 7종 v2 구현 + 단위 테스트 | backend-agent | P1 | 시그니처 일치, ask_user가 pending_questions에 저장 |
| P3 | ER 4단계 + 확신도 + trace | backend-agent | P2 | 승진 회귀 테스트 통과, trace에 breakdown 존재 |
| P3 | 베이스라인 3종 (문자열·임베딩·LLM 단일) | eval-agent | P1 | 동일 인터페이스로 호출 가능 |
| P4 | **파일럿 평가** (오병합률·미검출률·보정표·곡선 초안) | eval-agent | P3 | `reports/metrics.json`, `reports/calibration.json`. **여기서 미달이면 실패 케이스 분석 후 3.3 재설계** |
| P5 | 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 | backend-agent | P3 | 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작 |
| P6 | 3계층 메모리 승격 + 패턴 감지 + fact_sources | backend-agent | P5 | 승격 후 원문 링크 존재, 패턴 사실 생성 |
| P6 | 브리핑 생성 + 주기 작업 + 수동 트리거 | backend-agent | P5 | `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록 |
| P7 | 웹푸시 (구독 저장, VAPID 발송) | backend-agent | P6 | 데스크톱 Chrome에서 알림 수신 |
| P8 | 프론트 3화면 + PWA | frontend-agent(신설) | P5, P6 | 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면 |
| P9 | Terraform + GitHub Actions + Caddy TLS | infra-agent(신설) | P8 | 배포 URL에서 데모 시나리오 5단계 재현 |
| P10 | 150건 데이터셋 완성 + 최종 평가 + `reports/eval.md` | eval-agent | P4, P9 | metrics.json만으로 eval.md 재생성 |
| P11 | 데모 리허설 스크립트 (발표일 기준 날짜 재계산) | 사용자 | P9 | 승진 시나리오·수동 트리거 포함 |

원칙: **P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다.** ER이 안 되면 루프·프론트는 의미가 없다는 기획서 7장의 정신을 날짜 없이 유지하는 장치다.

---

## 6. 사용자 확인이 필요한 것 (요약)

| 결정 | 선택지 | 권장 |
|------|--------|------|
| D4 임베딩 공급자 | 파일럿 결과로 결정 | 파일럿 먼저 |
| D8 제목 | (a) "관계 메모리" / (b) 유지 + 사유 명시 | (a) |
| D1, D2, D3, D5, D6, D7, D9, D10 | 권장안 승인 여부 | 승인 |

승인되면 2장 문서 정합화부터 architect에게 위임한다. 코드는 4장 착수 준비의 파일럿 스크립트 이전에는 쓰지 않는다.
