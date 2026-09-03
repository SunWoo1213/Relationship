# P0-embed-pilot · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: 메인 세션(Claude) | 날짜: 2026-09-03

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P0-embed-pilot | tee docs/wiki/packages/P0-embed-pilot/evidence/20260903-verify-plan.txt`
```
== verify-plan P0-embed-pilot  (2026-09-03 19:05) ==
PASS  존재: docs/wiki/packages/P0-embed-pilot/01-plan.md
PASS  존재: docs/wiki/packages/P0-embed-pilot/02-plan-verify.md
PASS  카드 존재: D04
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-embed-pilot
PASS  검증 항목 존재: R5
PASS  Refs 있음: - [ ] U1 스크립트·테스트 작성: `scripts/embed_pilo
PASS  Refs 있음: - [ ] U2 파일럿 실행·리포트: 모델 2개로 실행�
PASS  Refs 있음: - [ ] U3 카드 반영: D04 카드 갱신 이력에 확정 �
PASS  backlog 일치: 한국어 짧은 호칭 30개 유사도 행렬 2종, 선택 
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: scripts/embed_pilot.py
PASS  registry 중복 없음: tests/test_embed_pilot.py
PASS  registry 중복 없음: reports/embed_pilot.md
PASS  registry 중복 없음: reports/embed_pilot/text-embedding-3-small.json
PASS  registry 중복 없음: reports/embed_pilot/text-embedding-3-large.json
PASS  registry 중복 없음: docs/wiki/decisions/D04-embedding-provider.md
PASS  registry 중복 없음: docs/wiki/specs/S3.1-schema-v2.md
== 결과: FAIL=0 WARN=0 ==
```
증거 파일: `docs/wiki/packages/P0-embed-pilot/evidence/20260903-verify-plan.txt`
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py P0-embed-pilot evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | CLAUDE.md 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱". 계획의 산출물은 호칭 임베딩 유사도 행렬·리포트뿐이며 대화·인물 저장 기능이 없다. |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | CLAUDE.md 원칙3 "confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule" — 이 패키지는 s_emb 의 공급자·차원만 정하고 결합식·임계치를 건드리지 않는다. 원칙8 "성능 미달도 결과다" — 01-plan 리스크에 "두 모델 모두 실패하면 성능 미달도 결과로 기록"을 명시. 원칙9 취지로 usage 토큰을 리포트에 남긴다. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | D04-embedding-provider.md "임베딩 호출은 반드시 `EmbeddingProvider` 인터페이스 뒤에 둔다(`embed(texts) -> list[vector]`, `dimension`)" → U1 에 동일 인터페이스. "파일럿 검증 기준은 동일: 팀장↔부장님 유사도 > 팀장↔이모" → U1 판정 로직. "차원 N은 … 근거를 `reports/embed_pilot.md`에 남긴다" → U2. D05-alias-level-embedding.md "별칭 단위 임베딩 … `person_embeddings` 삭제" → 계획은 별칭(호칭) 단위 임베딩만 다룬다. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | S3.1-schema-v2.md "person_aliases(… embedding vector(N) …) -- N: D4 파일럿 후 확정" → U3 에서 N 기입. S3.3-er-pipeline.md "1. 후보 검색 별칭 임베딩 top-K(K=10) → 인물별 max 유사도 → s_emb" → 코사인 유사도를 쓰며 툴 시그니처·임계치·ask_user 는 건드리지 않는다. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | docs/backlog.md 착수 준비 "임베딩 공급자 파일럿 (D4) … / 의존: 없음". INDEX.md 패키지 표에서 P0 는 P4 게이트 대상(P5 이후)이 아니다. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | docs/backlog.md "수용기준: 한국어 짧은 호칭 30개 유사도 행렬 2종, 선택 근거 1문단, 확정 차원 N 기록" — 01-plan 수용 기준 절과 동일(기계 검증 4번 PASS). |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 01-plan U1~U3 각 줄 끝 `Refs: P0-embed-pilot D4 …`(기계 검증 3번 PASS). |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | security.md §1 "`os.environ["OPENAI_API_KEY"]` 로 읽는다", "환경변수 전체 출력 … 금지" → 스크립트는 환경변수로만 읽고 값을 출력하지 않는다. §4 "외부 API 호출은 코드(SDK)로, 키는 환경변수" → OpenAI SDK 호출. 전송하는 데이터는 고정 호칭 30개뿐이며 사용자 데이터·삭제 명령 없음. |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
- 없음

## 4. 결정
결과: 통과
승인: 사용자 (2026-09-03)
