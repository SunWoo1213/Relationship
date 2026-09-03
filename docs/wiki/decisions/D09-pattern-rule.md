# D9 · 반복 패턴 감지는 규칙 기반

상태: 유효 | 해결하는 검증: R11 | 원문: `docs/resolution-plan.md` §1 D9, §3.5

**결정** 같은 인물의 같은 `events.type`이 최근 90일 내 **3회 이상** → `person_facts(key="pattern:{type}", value="{n}회 (날짜 목록)", confidence=1.0)` 생성·갱신, 근거 이벤트를 `fact_sources`에 연결. LLM은 패턴 **문장화만**.

**이유** 규칙이면 재현 가능하고 근거가 자동으로 남는다(원칙8·9).

**코드에서 지켜야 할 것** 패턴 판정에 LLM을 쓰지 않는다. 90일·3회는 설정값. 적용은 P6-memory.
