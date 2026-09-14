# D3 · 확신도 = 3신호 가중합, LLM 로그확률 미사용

상태: 유효 | 해결하는 검증: R4 | 원문: `docs/resolution-plan.md` §1 D3, §3.3

**결정** `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`
- `s_llm`: LLM이 구조화 출력으로 자기보고한 0~1 (로그 확률 아님 — Claude API가 제공하지 않음)
- `s_emb`: 후보 검색 코사인 유사도 0~1 정규화
- `s_rule`: 규칙 통과 수 / 검사 수 (위계 일치, 관계 태그 일치, 호칭 사전 호환)

**보정** `s_llm` 0.1 구간별 실제 정답률 → `reports/calibration.json` (P4). 이 표가 자기보고 점수의 신뢰 근거.

**파급** 가중치는 설정값(파일럿 후 조정). trace `confidence_breakdown{s_llm,s_emb,s_rule,weights,confidence}` 필수(원칙9). 공급자 선택·활성 스위치·기본 공급자는 **D11**(이 공식은 공급자와 무관하게 동일).

**갱신 이력**
- 2026-09-11 파급에 D11 상호참조 1줄(P3-llm-providers 결정 6). 결정 문장 무변경.
