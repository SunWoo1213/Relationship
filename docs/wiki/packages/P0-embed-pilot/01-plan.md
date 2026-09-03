# P0-embed-pilot · 계획 (01-plan)

상태: 초안 | 담당: backend-agent(초안·구현) / 메인 세션(승인·커밋) | 작성: 2026-09-03
태그 — 패키지: P0-embed-pilot · 닫는 검증: R5 · 기대는 결정: D4 D5 · 구현하는 명세: S3.1 S3.3 · 관련 원칙: 원칙3 원칙8 원칙9
의존: 없음 (착수 준비 항목. 선행 패키지 없음. P4 게이트 해당 없음)

## 목표
기획서 4장 "착수 준비"의 임베딩 공급자 파일럿(D4)을 수행한다. D4 카드의 결정 — "1차 공급자: OpenAI 임베딩 API로 시작한다. 모델은 P0-embed-pilot에서 OpenAI 모델 중 선택하고(기본 후보 `text-embedding-3-small`), 그 출력 차원으로 `person_aliases.embedding vector(N)`의 N을 확정한다" — 를 실제 API 호출로 실행해, 한국어 짧은 호칭 30개의 유사도 행렬을 얻고 모델·차원 N을 확정한다. 파일럿 검증 기준은 D4 그대로 "팀장↔부장님 유사도 > 팀장↔이모"다. 이 스크립트는 resolution-plan §1 D4가 말하는 "유일하게 허용되는 결정용 코드"다.

## 범위
- 포함:
  - 한국어 짧은 호칭 30개 고정 목록(직장 호칭·가족 호칭·대명사·이름+직함 혼합).
  - `EmbeddingProvider` 인터페이스(`embed(texts) -> list[vector]`, `dimension`)와 `OpenAIEmbeddingProvider` 구현(모델명은 인자·환경변수 `EMBEDDING_MODEL`).
  - **유사도 행렬 2종** = OpenAI 모델 2개(`text-embedding-3-small`, `text-embedding-3-large`)의 코사인 유사도 30×30 행렬. D4 갱신(OpenAI 먼저, 타 공급자 비교는 나중)에 따라 "2종"은 공급자 2곳이 아니라 OpenAI 모델 2개로 해석한다.
  - 검증 기준(팀장↔부장님 > 팀장↔이모) 자동 판정과, 별칭 top-K 후보 검색(S3.3 1단계)에 참고할 근접 호칭 쌍 상위/하위 목록.
  - 선택 근거 1문단, 확정 차원 N을 `reports/embed_pilot.md`에 기록하고 D4·S3.1 카드에 반영.
  - 네트워크 없이 도는 단위 테스트(가짜 공급자로 행렬·판정 로직 검증).
- 이 패키지에서 하지 않는 것:
  - 다른 공급자(Voyage·Cohere 등)와의 비교 — D4 "추후 다른 공급자 API 키를 추가해 성능 비교"는 별도 작업.
  - `person_aliases` 테이블 생성·마이그레이션(P1-schema), 후보 검색 함수(P3-er), 백엔드 패키지 구조 결정. `EmbeddingProvider`는 이 스크립트 안에 두고 P2/P3에서 백엔드 모듈로 옮긴다(registry 비고에 기록).
  - 임계치 T_merge/T_new 확정(P4-pilot-eval).

## 산출물 (파일 경로)
- scripts/embed_pilot.py — 호칭 30개, EmbeddingProvider/OpenAIEmbeddingProvider, 코사인 행렬, 판정, 결과 저장
- tests/test_embed_pilot.py — 가짜 공급자로 행렬·판정·차원 검증(네트워크 없음)
- reports/embed_pilot.md — 유사도 행렬 2종 요약, 검증 기준 결과, 선택 근거 1문단, 확정 차원 N
- reports/embed_pilot/text-embedding-3-small.json, reports/embed_pilot/text-embedding-3-large.json — 원본 행렬(재현용)
- docs/wiki/decisions/D04-embedding-provider.md — 확정 모델·N 갱신 이력 추가
- docs/wiki/specs/S3.1-schema-v2.md — `vector(N)` 주석에 확정 N 기입

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)
- [x] U1 스크립트·테스트 작성: `scripts/embed_pilot.py`(호칭 30개, `EmbeddingProvider` 인터페이스, OpenAI 구현, 코사인 행렬, 팀장↔부장님>팀장↔이모 판정, JSON 저장, 키 없으면 명확한 메시지로 종료), `tests/test_embed_pilot.py` 통과 / Refs: P0-embed-pilot D4 D5 S3.3 R5
- [x] U2 파일럿 실행·리포트: 모델 2개로 실행해 `reports/embed_pilot/*.json`과 실행 출력을 `packages/P0-embed-pilot/evidence/`에 남기고 `reports/embed_pilot.md`(행렬 2종 요약·판정 결과·선택 근거 1문단·확정 N) 작성 / Refs: P0-embed-pilot D4 R5 원칙8
- [x] U3 카드 반영: D04 카드 갱신 이력에 확정 모델·N, S3.1 카드 `vector(N)` 주석, review-index R5 상태, registry 행 추가, `.env.example`의 `EMBEDDING_MODEL` 기본값 확인 / Refs: P0-embed-pilot D4 S3.1 R5

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)
- 한국어 짧은 호칭 30개 유사도 행렬 2종, 선택 근거 1문단, 확정 차원 N 기록

## 리스크 · 미결
- `OPENAI_API_KEY`가 `.env`에 없으면 U2를 실행할 수 없다. 스크립트는 `python-dotenv`로 `.env`를 읽되 값은 출력하지 않는다(security.md §1). 키가 없으면 사용자에게 `.env` 작성을 요청하고 U2에서 멈춘다.
- 호출 비용: 호칭 30개 × 모델 2개 = 60개 짧은 입력. 수백 토큰 수준이라 무시할 만하다. 리포트에 실제 사용 토큰(usage)을 남긴다(원칙9의 취지).
- `text-embedding-3-large`는 3072차원이라 pgvector 인덱스(HNSW 최대 2000차원)에 제약이 있다. 판정 기준을 둘 다 통과하면 차원이 작은 쪽(1536)을 기본으로 택하고, 그 이유를 리포트에 적는다.
- 판정 기준(팀장↔부장님 > 팀장↔이모)이 두 모델 모두 실패하면 성능 미달도 결과로 기록하고(원칙8) 사용자에게 다른 공급자 비교를 앞당길지 묻는다.

## 읽은 카드
- `docs/wiki/INDEX.md` 패키지 id 표(P0-embed-pilot 행), `docs/wiki/CURRENT.md`, `docs/wiki/HANDOFF.md`
- `docs/backlog.md` 착수 준비 절(P0 항목 4개)
- `docs/wiki/review-index.md` R5 행
- `docs/wiki/decisions/D04-embedding-provider.md` 전문
- `docs/wiki/specs/S3.1-schema-v2.md` 스키마 절(`person_aliases.embedding vector(N)`), `docs/wiki/specs/S3.3-er-pipeline.md` 1단계 후보 검색
- `docs/resolution-plan.md` §1 D4·D5, §4 착수 준비 표
- `docs/wiki/security.md` §1 비밀, §4 외부 전송 행
- `docs/wiki/registry.md`(grep: embed·임베딩·pilot — 해당 없음)
