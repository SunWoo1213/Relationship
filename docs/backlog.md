# Backlog — architect가 관리하는 단일 진실 소스

> 이 파일은 `architect` 에이전트가 갱신한다. 각 태스크에는 담당 에이전트·의존·수용 기준을 붙인다.
> 형식: `- [ ] [담당] 태스크 / 의존: ... / 수용기준: ...`
>
> **개발 일정(M1~M4, 4개월)은 폐기했다.** 날짜가 아니라 의존성 순서로만 배열한다. 근거: `docs/resolution-plan.md` 0장·5장.
> **원칙: P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다.** 엔티티 해석이 안 되면 루프·프론트는 의미가 없다.
> 설계 명세(스키마 v2·툴 시그니처 v2·ER·ask_user·승격·브리핑·평가)는 `docs/resolution-plan.md` 3장이 권위를 갖는다.

## 착수 준비 (구현 직전, 코드 최소)

- [ ] [사용자] git 저장소 초기화, `.gitignore`, `.env.example` / 의존: 없음 / 수용기준: `git log`에 커밋 1건
- [ ] [사용자] AWS Budgets 알림 $10/$30/$50 설정, 크레딧 잔액 확인 / 의존: 없음 / 수용기준: 알림 3개 활성, 잔액 메모 또는 스크린샷
- [x] [backend-agent] 임베딩 공급자 파일럿 (D4) — `scripts/embed_pilot.py`, `reports/embed_pilot.md` / 의존: 없음 / 수용기준: 한국어 짧은 호칭 30개 유사도 행렬 2종, 선택 근거 1문단, 확정 차원 N 기록
- [ ] [eval-agent] LLM 비용 실측 — `reports/cost_estimate.md` / 의존: 없음 / 수용기준: 시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정
- [x] [backend-agent] 로컬 docker-compose (pgvector) / 의존: 없음 / 수용기준: `SELECT '[1,2,3]'::vector` 성공 — 완료(2026-09-05, 04-review 완료, verify-impl FAIL 0)

## 구현 순서 (P1~P11, 날짜 없음 — 같은 번호는 병렬 가능)

### P1

- [x] [backend-agent] 스키마 v2 마이그레이션 (Alembic) / 의존: 착수 준비(D4 차원 확정, docker-compose) / 수용기준: 9개 테이블 생성, `events.type` 제약 존재 — 완료(2026-09-05, 04-review 완료, verify-impl FAIL 0, R8 R9 구현완료)
- [x] [eval-agent] 파일럿 데이터셋 30~50건 (승진·대명사·별칭·정상·신규) / 의존: 평가 명세(resolution-plan 3.7) / 수용기준: `data/scenarios/` JSON, 라벨 검수 완료 — **완료(2026-09-10, P1-pilot-dataset, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0; 40건·5범주, 라벨 검수 열림 0; 닫는 R 없음 — R3·R4 는 P4 가 닫는다)**
  - 세분화는 `docs/wiki/packages/P1-pilot-dataset/01-plan.md` (U1~U7). 위 행의 문장·수용기준은 권위이며 바꾸지 않는다.
  - [x] U1 스키마 확정 + `data/scenarios/schema.json` + `scripts/validate_scenarios.py` + 검증기 테스트 / 수용: 위반 표본 8종을 전부 FAIL 로 잡는다
  - [x] U2 `promotion` 8건 + `alias` 8건 (오병합 유도 함정 각 3건 이상, 호칭 변이 의도적 포함)
  - [x] U3 `pronoun` 8건 + `normal` 10건 (선행사 명확한 대명사만, 모호 건은 `ambiguous` 플래그 후보)
  - [x] U4 `new_person` 6건 (등록 대상 vs 지나가는 언급, 기대 `ask_user` 는 허용 집합으로 라벨 — D1 D10)
  - [x] U5 전건 무결성 점검 + `manifest.json` 배분표 + 검수 패킷 생성(검수는 하지 않는다)
  - [x] U6 라벨 검수 지적 반영 / 검수자: **verifier 또는 사용자**(eval-agent 자기검수 금지, L-002) / 기록: `packages/P1-pilot-dataset/evidence/<ts>-label-review.md`(열림 0 이 완료 조건)
  - [x] U7 registry 행 · README 데이터셋 절 · 수용 기준 기계 검증 evidence
  - **U1 착수 전 사용자 결정 7건**(01-plan "리스크·미결" A~G): 인물 메타 포함 여부 / 이벤트 골드 라벨 범위 / 일정 골드 라벨 연기 / `ask_user` 라벨 형태 / seed 인물 표현 / 생성 방식(LLM 초안+검수) / 검수 범위·검수자

### P2

- [x] [backend-agent] 툴 7종 v2 구현 + 단위 테스트 / 의존: P1 스키마 / 수용기준: 시그니처가 CLAUDE.md와 일치, `ask_user`가 `pending_questions`에 저장 — 완료(2026-09-05, 04-review 완료, verify-impl FAIL 0, R6 R7 R10 R18 구현완료; FastAPI 골격 health·answers 포함)

### P3

- [x] [backend-agent] ER 4단계 + 확신도 + trace / 의존: P2 / 수용기준: 승진 회귀 테스트 통과, trace에 `confidence_breakdown` 존재 — **완료(2026-09-06, P3-er, verifier 04-review `완료`; R4 실호출은 스모크 사용자 실행 후 보강)**
- [ ] [eval-agent] 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능

### P4 — 게이트

- [ ] [eval-agent] **파일럿 평가** (오병합률·미검출률·보정표·곡선 초안) / 의존: P3 / 수용기준: `reports/metrics.json`, `reports/calibration.json` 생성. **미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다**

### P5

- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, P4 통과 / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개

### P6

- [ ] [backend-agent] 3계층 메모리 승격 + 패턴 감지 + `fact_sources` / 의존: P5 / 수용기준: 승격 후 사실→원문 링크 존재, 90일 3회 규칙으로 `pattern:{type}` 사실 생성
- [ ] [backend-agent] 브리핑 생성 + 주기 작업(1분 간격) + 수동 트리거 / 의존: P5 / 수용기준: `POST /briefings/run`으로 브리핑 생성, `briefed_at` 기록

### P7

- [ ] [backend-agent] 웹푸시 (구독 저장, VAPID 발송) / 의존: P6 / 수용기준: 데스크톱 Chrome에서 알림 수신

### P8

- [ ] [frontend-agent(신설)] 프론트 3화면 + PWA / 의존: P5, P6 / 수용기준: 채팅 확인 칩, 카드 원문 펼치기, 브리핑 화면

### P9

- [ ] [infra-agent(신설)] Terraform + GitHub Actions + Caddy TLS / 의존: P8 / 수용기준: 배포 URL에서 데모 시나리오 5단계 재현

### P10

- [ ] [eval-agent] 150건 데이터셋 완성 + 최종 평가 + `reports/eval.md` / 의존: P4, P9 / 수용기준: `metrics.json`만으로 `eval.md` 재생성

### P11

- [ ] [사용자] 데모 리허설 스크립트 (발표일 기준 날짜 재계산) / 의존: P9 / 수용기준: 승진 시나리오·수동 트리거 포함

## 리스크 로그 (기획서 9장)

- 엔티티 해석 성능 미달 → **P4 파일럿 평가 시점**에 점검, 실패 케이스 분석을 산출물로
- 1인 개발 범위 초과 → 프론트 3화면 고정, 음성·메시지 초안 제외
- LLM API 비용 → 소형 모델·프롬프트 캐싱·`metrics.json` 재사용, 착수 준비의 `cost_estimate.md`로 사전 추정
- `s_llm` 자기보고 점수의 신뢰성 → **P4 파일럿 평가 시점**에 보정표(`reports/calibration.json`)로 검증
- 임베딩 공급자 미확정(D4) → 착수 준비 파일럿 전까지 스키마의 `vector(N)` 차원을 고정하지 않는다
- 평가 데이터셋 편향(P1-pilot-dataset) → 생성(eval-agent)과 라벨 검수(verifier·사용자)를 분리, 생성 모델·프롬프트를 `manifest.json` 에 기록, 문어체 편향은 과대평가 방향이므로 검수 항목으로 강제(원칙8)
