# P0-embed-pilot · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-03 19:10 · docs(P0-embed-pilot): 계획·계획검증 승인, 패키지 착수 · pending
- 변경: packages/P0-embed-pilot/01-plan.md, 02-plan-verify.md(기계 검증 PASS 23/FAIL 0, 점검표 8행 통과, 승인: 사용자 2026-09-03), evidence/20260903-verify-plan.txt, 03-log.md 신설. CURRENT.md active: P0-embed-pilot. journal START.
- 이유(기획서·카드 연결): D04 "모델은 P0-embed-pilot에서 OpenAI 모델 중 선택하고 … N을 확정한다". resolution-plan §4 착수 준비 표의 임베딩 공급자 파일럿.
- 정합성 확인: 원칙3·8·9 / D4·D5 / S3.1·S3.3 / 보안 §1·§4 — 위반 없음 (02-plan-verify 점검표)
- 남은 것 · 다음 단위: U1 scripts/embed_pilot.py + tests/test_embed_pilot.py 작성
- Refs: P0-embed-pilot D4 D5 S3.1 S3.3 R5

## 2026-09-03 19:22 · feat(P0-embed-pilot): U1 임베딩 파일럿 스크립트·단위 테스트 · pending
- 변경: scripts/embed_pilot.py(호칭 30개, EmbeddingProvider 프로토콜 + OpenAIEmbeddingProvider, 코사인 행렬, D4 판정 + 보조 4쌍, JSON 저장, 키 없으면 rc=2), tests/test_embed_pilot.py(가짜 공급자, 10 테스트). 01-plan U1 [x].
- 이유(기획서·카드 연결): D04 "임베딩 호출은 반드시 EmbeddingProvider 인터페이스 뒤에 둔다", "파일럿 검증 기준은 동일: 팀장↔부장님 유사도 > 팀장↔이모". resolution-plan §1 D4 "유일하게 허용되는 결정용 코드".
- 정합성 확인: 원칙3(결합식·임계치 불변) / D4·D5 / S3.3 1단계 코사인 유사도 / 보안 §1(키는 환경변수, 값 미출력) — 위반 없음
- 남은 것 · 다음 단위: U2 실제 실행(OPENAI_API_KEY 필요) → reports/embed_pilot.md
- Refs: P0-embed-pilot D4 D5 S3.3 R5

## 2026-09-03 19:40 · eval(P0-embed-pilot): U2 파일럿 실행·리포트 — small/large 둘 다 통과, N=1536 · pending
- 변경: reports/embed_pilot.md(결론·선택 근거 1문단·관찰·한계·행렬 2종), reports/embed_pilot/{text-embedding-3-small,text-embedding-3-large}.json, evidence/20260903-embed-pilot-run.txt·report-tables.md, scripts/embed_pilot.py 콘솔 UTF-8 고정(작은 수정). 01-plan U2 [x].
- 이유(기획서·카드 연결): D04 "그 출력 차원으로 person_aliases.embedding vector(N)의 N을 확정", "근거를 reports/embed_pilot.md에 남긴다".
- 정합성 확인: 원칙1(오병합 후보 적은 쪽 선택 근거) / 원칙8(수치 원본 JSON 보관) / D4 / 보안 §1(키 미출력) — 위반 없음
- 남은 것 · 다음 단위: U3 카드 반영
- Refs: P0-embed-pilot D4 R5 원칙8

## 2026-09-03 19:42 · docs(P0-embed-pilot): U3 카드 반영 — D04 확정·S3.1 vector(1536)·R5 해소 · pending
- 변경: decisions/D04-embedding-provider.md(확정 절·상태), specs/S3.1-schema-v2.md(vector(1536) 주석), review-index.md R5 상태, registry.md 리포트 행, .env.example EMBEDDING_MODEL=text-embedding-3-small 확인(변경 없음). 01-plan U3 [x].
- 이유(기획서·카드 연결): S3.1 "N: D4 파일럿 후 확정". review-index R5 "D4 → P0-embed-pilot".
- 정합성 확인: D4·D5·S3.1 — 위반 없음. 스키마 v2 구조 변경 없음(N 값만 확정)
- 남은 것 · 다음 단위: /devlog done (verify-impl, 04-review)
- Refs: P0-embed-pilot D4 S3.1 R5
