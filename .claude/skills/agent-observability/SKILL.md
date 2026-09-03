---
name: agent-observability
description: 에이전트가 어떻게 판단했는지 추적 가능하게 만드는 작업법. 각 step의 입력·출력·툴 호출·토큰·후보 목록·확신도를 agent_traces에 기록하고 사후 분석·발표용 뷰로 재현한다. 로깅/트레이스/관측성/근거 추적 작업 시 따른다.
---

# agent-observability — 관측성

## 왜 이렇게 하는가

에이전트가 "왜 그렇게 판단했는지"를 남겨야 오류를 사후 분석하고, 평가 지표를 뽑고, 발표에서 판단 과정을 보여줄 수 있다. 요약의 근거를 추적하려면 원문과 판정 근거를 함께 보존해야 한다.

## 무엇을 기록하나

`agent_traces(id, session_id, step, tool_name, input, output, tokens_in, tokens_out, created_at)`에 각 step마다:
- **step**: 인식 / 해석 / 기록 / 응답 등 루프 단계
- **tool_name**: 호출한 툴 (search_person 등)
- **input / output**: 그 스텝의 입출력
- **tokens_in / tokens_out**: 입력·출력 토큰 사용량 (합산 단일 `tokens` 필드는 쓰지 않는다 — 비용 추정에 단가가 다르다)

엔티티 해석 스텝의 `output`에는 다음을 JSON으로 추가한다.

| 필드 | 내용 |
|------|------|
| `candidates[]` | 후보 목록 `{person_id, similarity, aliases_matched, rule_flags}` |
| `confidence_breakdown` | `{s_llm, s_emb, s_rule, confidence}` — 3신호와 결합값 |
| `decision` | `merge` / `ask_identity` / `ask_new_person` 중 하나 |
| `pending_question_id` | `ask_user`를 호출했다면 저장된 대기 질문 ID |
| `hierarchy_relaxed_retry` | 승진 케이스에서 위계 완화 재검색을 했는지 (true/false) |

## 근거 추적 (승격과 연결)

시맨틱 메모리로 승격(요약)할 때 원문(raw_utterance)을 버리지 않는다. 요약된 사실 → 그 근거가 된 events(원문)로 되짚을 수 있어야 한다. 이 링크는 `fact_sources(fact_id, event_id)`가 담당한다.

## 발표/디버깅 뷰

trace를 세션·인물 기준으로 재생해:
- 어떤 후보를 봤고, 확신도가 얼마였고, 왜 ask_user를 호출했는지 보여준다.
- 오병합/미검출이 발생한 스텝을 짚어낸다.

## 평가와의 연결

`eval-harness`는 agent_traces에서 툴 호출 정확도·`ask_user_rate_by_kind`·보정표(`s_llm` 구간별 정답률)를 추출한다. 따라서 trace 스키마가 지표 계산을 지원해야 한다 — `confidence_breakdown.s_llm`과 `decision`이 없으면 보정표를 만들 수 없다.

## 품질 체크

- [ ] 모든 툴 호출이 trace로 남는가
- [ ] 엔티티 해석 스텝에 `candidates[]`·`confidence_breakdown`·`decision`이 있는가
- [ ] `ask_user` 호출에 `pending_question_id`가 연결되는가
- [ ] 승진 케이스의 `hierarchy_relaxed_retry` 여부가 남는가
- [ ] 토큰이 `tokens_in`/`tokens_out`으로 분리 기록되는가
- [ ] 요약된 사실에서 `fact_sources`로 원문을 되짚을 수 있는가
- [ ] session_id로 한 대화의 전체 판단 흐름을 재생할 수 있는가

## 관련
[[entity-resolution]] — 판정 근거 대상, [[eval-harness]] — trace 기반 지표
