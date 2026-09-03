# D4 · 임베딩 공급자와 차원

상태: 유효(부분 확정) | 해결하는 검증: R5 | 원문: `docs/resolution-plan.md` §1 D4

**결정 (2026-09-03 사용자 지시로 갱신)**
- **1차 공급자: OpenAI 임베딩 API로 시작한다.** 모델은 P0-embed-pilot에서 OpenAI 모델 중 선택하고(기본 후보 `text-embedding-3-small`), 그 출력 차원으로 `person_aliases.embedding vector(N)`의 N을 확정한다.
- **추후 다른 공급자 API 키를 추가해 성능 비교**한다. 비교는 별도 작업(P10 이전 옵션)이며 1차 결정을 막지 않는다.
- 원안(공급자 2곳을 파일럿에서 동시 비교)은 "OpenAI 먼저, 비교는 나중"으로 순서가 바뀐 것이다.

**이유** Claude API에는 임베딩 엔드포인트가 없다. 공급자 결정을 기다리느라 스키마 차원을 못 정하는 것이 더 큰 지연이다.

**파급 · 코드에서 지켜야 할 것**
- 임베딩 호출은 반드시 `EmbeddingProvider` 인터페이스 뒤에 둔다(`embed(texts) -> list[vector]`, `dimension`). 공급자 교체가 한 클래스 추가로 끝나야 한다.
- 차원 N은 설정값이며 마이그레이션에 하드코딩하되 그 근거를 `reports/embed_pilot.md`에 남긴다. 공급자 바꾸면 재임베딩 마이그레이션이 필요함을 카드에 명시.
- 파일럿 검증 기준은 동일: "팀장↔부장님" 유사도 > "팀장↔이모".
- 환경변수: `OPENAI_API_KEY`(임베딩), `ANTHROPIC_API_KEY`(LLM). `.env.example` 참조.

**갱신 이력** 2026-09-03 — 사용자: "OpenAI API 키로 우선 시작, 추후 다른 모델 API 키로 성능 비교".
