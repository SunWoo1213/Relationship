# D14 · 반복 패턴 규칙 — 기간·횟수는 설정값, 기본 365일·3회

상태: 유효 (D9 를 대체, CR-002) | 해결하는 검증: R11 | 원문: `docs/resolution-plan.md` §1 D9(CR-002 주석), §3.5 · 변경: `docs/wiki/changes/CR-002.md`

**결정** 같은 인물의 같은 `events.type` 이 **최근 `PATTERN_WINDOW_DAYS`일(기본 365일 = 1년) 내 `PATTERN_MIN_COUNT`회(기본 3회) 이상** → `person_facts(key="pattern:{type}", value="{n}회 (날짜 목록)", confidence=1.0)` 생성·갱신, 근거 이벤트를 `fact_sources` 에 연결. LLM 은 패턴 **문장화만**. 규칙 기반·값 형식·확신도·근거 연결은 D9 그대로다.

**이유** 90일은 사용자에게 너무 짧았다(2026-09-28). 다만 창이 길면 명절 식사 같은 일상도 패턴이 되므로, 기간과 횟수를 코드 수정 없이 바꿀 수 있게 설정값으로 둔다. 규칙이면 재현 가능하고 근거가 자동으로 남는다(원칙8·9).

**코드에서 지켜야 할 것**
- 패턴 판정에 LLM 을 쓰지 않는다.
- 기본값은 `app/settings.py` 한 곳(`PATTERN_WINDOW_DAYS = 365`, `PATTERN_MIN_COUNT = 3`). 환경변수 `PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT` 가 있으면 그 값(양의 정수만, 아니면 오류, 비우면 기본값). `.env.example` 에 기본값 줄.
- 1년 = 365일 고정(윤년 무관). 창 = `[now − PATTERN_WINDOW_DAYS일, now]`, `occurred_at` 기준.
- 실제 쓴 기간·횟수를 패턴 trace(`memory_pattern`)에 기록한다 — 설정을 바꿔도 과거 판정을 재현할 수 있게(원칙8·9).
- 적용은 P6-memory.
