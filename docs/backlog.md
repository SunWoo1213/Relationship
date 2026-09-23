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
- [ ] [eval-agent] LLM 비용 실측 — `reports/cost_estimate.md` / 의존: 없음 / 수용기준: 시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정 — **P4-pilot-eval U6 로 흡수**(사용자 결정 B, 2026-09-11: 40건 실측으로 150건 외삽. 문장·수용기준은 그대로, 완료 판정은 P4 04-review 에서)
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

- [ ] [backend-agent] `DELETE /persons/{id}` — 인물 단위 완전 삭제 / 의존: P2 / 수용기준: 인물·별칭·사실·이벤트·일정이 FK CASCADE 로 함께 지워지고, `pending_questions.context`·`agent_traces.input/output` JSONB 안의 `person_id` 참조도 정리된다. 삭제 전 확인을 요구하고, 남의 인물은 지울 수 없다 / Refs: F-4d2507 security§5 (P1 04-review §7)
  - security.md §5 가 요구하는데 backlog 어느 항목에도 없었다(F-4d2507, P2 04-review 90행이 architect 에게 인계). P5-loop 01-plan 이 다시 지적해 사용자 승인으로 신설(2026-09-23). **P5 에 끼우지 않는다** — 루프의 수용 기준과 성격이 다르다.

### P3

- [x] [backend-agent] ER 4단계 + 확신도 + trace / 의존: P2 / 수용기준: 승진 회귀 테스트 통과, trace에 `confidence_breakdown` 존재 — **완료(2026-09-06, P3-er, verifier 04-review `완료`; R4 실호출은 스모크 사용자 실행 후 보강)**
- [x] [eval-agent] 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능
  - 세분화는 `docs/wiki/packages/P3-baselines/01-plan.md` (U1~U8). 위 행의 문장·수용기준은 권위이며 바꾸지 않는다. 코드 위치 `evaluation/`(결정 A).
  - [ ] U1 공통 인터페이스 `Resolver`·`MentionDecision`·방식 표 `RESOLVERS` + 계약 테스트
  - [ ] U2 제안 방식 어댑터 (`app.er.resolve` 감싸기, `app/` 무수정)
  - [ ] U3 베이스라인 1 문자열 완전일치 (raw·norm 두 변형, 동명이인 → identity)
  - [ ] U4 베이스라인 2 임베딩 단독 (`search_candidates`·`band_for` 재사용)
  - [ ] U5 베이스라인 3 LLM 단일 프롬프트 (결정까지 LLM, `candidate_person_ids`, 오류 매핑 공개 승격 1건) + 스모크 스크립트
  - [ ] U6 시나리오 사전 상태 적재기 (`seed_persons`+`aliases` 그대로, P4 재사용)
  - [ ] U7 동일 인터페이스 계약 테스트 `tests/test_baseline_parity.py` (수용 기준 증명)
  - [ ] U8 수용 기준 기계 검증 evidence + registry + README 실행법
- [x] [backend-agent] LLM 판정기 공급자 확장 — Gemini 구현 + 공급자 등록표·활성 스위치 / 의존: P3-er, P3-baselines / 수용기준: `LLM_PROVIDER` ∈ {anthropic, openai, gemini} 각각으로 `judge_from_env()`·`caller_from_env()` 가 해당 공급자의 판정기를 만들고, 비활성·미지 공급자는 `InvalidValue` 로 거부하며, 신규 테스트는 네트워크 0(스텁)이고 기존 pytest 전건이 통과한다
  - 세분화는 `docs/wiki/packages/P3-llm-providers/01-plan.md` (U1~U4). 위 행의 문장·수용기준은 권위이며 바꾸지 않는다. 수정 대상 `app/` 파일은 `app/er/judge.py`·`app/settings.py` 뿐(결정 J 이후 두 번째 예외).
  - [x] U1 공급자 등록표·활성 스위치 (이름→팩토리 표, `LLM_PROVIDER` 선택, 활성 목록 환경변수, 꺼진 공급자 거부) + 테스트
  - [x] U2 `GeminiJudge` (`google-genai`, `response_schema` 로 `JUDGEMENT_SCHEMA` 강제, 오류 어휘 동일) + 의존성 핀 + 스텁 테스트
  - [x] U3 `GeminiSingleCaller` (`evaluation/resolvers/llm_single.py`, 같은 등록표·같은 스위치 재사용) + 스텁 테스트
  - [x] U4 문서·evidence (`.env.example`·README 두 절·user-setup 01/03/08·D 카드·registry·회귀 전건 evidence)
  - **U1 착수 전 사용자 결정 7건**(01-plan "리스크·미결" 1~7): 활성 스위치 이름·기본값 / 기본 `LLM_PROVIDER` / Gemini 기본 모델명 / 구조화 출력 실패 어휘 / 의존성 핀 위치 / D 카드 신설 여부 / 실 Gemini 스모크 카드 위치

### P4 — 게이트

- [x] [eval-agent] **파일럿 평가** (오병합률·미검출률·보정표·곡선 초안) / 의존: P3, P3-llm-providers / 수용기준: `reports/metrics.json`, `reports/calibration.json` 생성. **미달이면 재시도가 아니라 실패 케이스 분석을 산출물로 남기고 ER 설계(resolution-plan 3.3)를 재설계한다** — **부분완료(2026-09-22, verifier 04-review)**: 실 실행 ef18143(openai gpt-4o-mini-2024-07-18, 40건·7050행), 게이트 결정 K 미달(`embedding_only` 지배, D10 방향 ✔), 실패 케이스 분석 ea1bbb2(`reports/failure_cases.md`: 2단계 규칙 필터 배제 6건·4단계 미측정 s_rule=0 합산 상한 0.80). 재설계 = `/devlog change` CR(①4단계 가중치 재정규화 + ②2단계 배제→감점, 사용자 결정). P5 미착수

### P4b — 게이트 재도전 (CR-001)

- [x] [backend-agent + eval-agent] **ER 재설계 후 파일럿 재실행** — D12(관측 신호 재정규화)·D13(규칙 필터 감점) 구현 + 새 stamp 재실행 + 게이트 재판정 / 의존: P4 부분완료(adf9f1b), CR-001 승인 / 수용기준: `app/er/confidence.py`·`rules.py`·`pipeline.py`·`types.py`(+`settings.py` 설정값) 가 D12·D13 "코드에서 지켜야 할 것" 전부 충족(회귀 3종 유지), `--recheck-traces` `max_abs_diff=0.0`(weights_effective), 새 stamp `reports/pilot/raw-<ts>.jsonl.gz`·`reports/metrics.json` 로 결정 K 게이트 `0.8 [] True True`, `sc-015` 오병합·`sc-007` 미검출 아님, P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경. 미달이면 재실행 없이 failure_cases 갱신 + 사용자 결정
  - 01-plan 결정 항목: 감점 후보의 `≥ T_merge` 보수 분기(권장 강등)·설정값 이름 / 완화 재검색 존치 / `weights` vs `weights_effective` 거부 규약 / 재실행 비용 상한

### P5

- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개
  - 세분화는 `docs/wiki/packages/P5-loop/01-plan.md` (U1~U7). 70행의 문장·수용 기준은 바꾸지 않는다.
  - 01-plan 결정 항목(사용자 확정 2026-09-23, 전부 (i)): 툴 선택은 코드가 한다(LLM 은 구조화 추출만) / 응답은 템플릿 / 재개는 해석 단계부터 / 되묻기로 끝나도 되돌리지 않는다 / 순차 처리·첫 되묻기에서 턴 종료 / 추출 개수 상한 / `loop_` trace 어휘 / 오류는 200 으로 삼켜 같은 트랜잭션에 커밋 / 세션 id 는 서버 발급·격리 부재 명시 / 확인 질문은 409 + `context` 바인딩 / 일정 시각 미확정은 `ask_user(kind="schedule")`

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
  - P5-loop 결정 K 가 만드는 `ask_user(kind="schedule")` 이 `ask_user_rate_by_kind` 의 분모에 들어간다(P4 04-review 214행: "kind=schedule 은 P5 루프가 만든 뒤 P10 이 잰다"). P4b 실측 되묻기는 kind 가 `identity` 뿐이었다.

### P11

- [ ] [사용자] 데모 리허설 스크립트 (발표일 기준 날짜 재계산) / 의존: P9 / 수용기준: 승진 시나리오·수동 트리거 포함

## 리스크 로그 (기획서 9장)

- **다중 사용자 격리가 없다(F-fbaaae)** → `pending_questions`·`agent_traces` 에 `user_id` 컬럼이 없어 세션 단위 귀속만 하고 사용자 단위 격리는 하지 못한다. 단일 사용자(`app_user_id()` 고정) 전제에서는 문제가 드러나지 않지만 **P9 배포 전에 다시 꺼내야 하는 부채**다. 스키마 변경(S3.1)이 필요하므로 P5-loop 범위 밖이고, P5 는 이 사실을 모듈 docstring·README 에 명시만 한다(01-plan 결정 I(i), architect 개정 제안 4 · 사용자 승인 2026-09-23).

- 엔티티 해석 성능 미달 → **P4 파일럿 평가 시점**에 점검, 실패 케이스 분석을 산출물로
- 1인 개발 범위 초과 → 프론트 3화면 고정, 음성·메시지 초안 제외
- LLM API 비용 → 소형 모델·프롬프트 캐싱·`metrics.json` 재사용, 착수 준비의 `cost_estimate.md`로 사전 추정
- `s_llm` 자기보고 점수의 신뢰성 → **P4 파일럿 평가 시점**에 보정표(`reports/calibration.json`)로 검증
- 임베딩 공급자 미확정(D4) → 착수 준비 파일럿 전까지 스키마의 `vector(N)` 차원을 고정하지 않는다
- 평가 데이터셋 편향(P1-pilot-dataset) → 생성(eval-agent)과 라벨 검수(verifier·사용자)를 분리, 생성 모델·프롬프트를 `manifest.json` 에 기록, 문어체 편향은 과대평가 방향이므로 검수 항목으로 강제(원칙8)
