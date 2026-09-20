# 대화형 관계 메모리 에이전트

[![tests](https://github.com/SunWoo1213/Relationship/actions/workflows/tests.yml/badge.svg)](https://github.com/SunWoo1213/Relationship/actions/workflows/tests.yml)

> 자연어 대화에서 자동 구축되는 개인 관계 메모리 기반 브리핑 시스템 — 1인 개발 캡스톤디자인 2 프로젝트

사용자가 평소처럼 대화하면, 제품 속 **관계 메모리 에이전트**가 인물·사건·일정을 스스로 추출·해석해 장기 메모리를 쌓고, 만남 직전에 필요한 맥락만 요약(브리핑)해 준다. 입력을 요구하지 않는다는 점에서 수동 기록 도구와 다르고, 세션을 넘어 축적되며 같은 인물의 호칭 변이를 하나로 묶는다는 점에서 범용 LLM 채팅과 다르다.

## 한눈에 보기

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | |
|---|---|
| **무엇** | 대화 속 호칭 변이("팀장 → 김팀장 → 부장님")를 한 인물로 묶는 **엔티티 해석 파이프라인**과 그 **평가 장치** (1인 · 캡스톤디자인 2, 진행 중) |
| **지금 있는 것** | 스키마 v2(9테이블 · pgvector), 툴 7종, 엔티티 해석 4단계, 비교 방식 5종, 평가 데이터 40건, pytest 918 passed(LLM · 임베딩은 스텁, 실제 PostgreSQL + pgvector에서 CI 실행) |
| **아직 없는 것** | 성능 수치(파일럿 평가 P4 전), 에이전트 대화 루프 · 브리핑 · 프론트 · 배포. 자동 테스트는 전부 스텁이고, 실제 LLM 호출은 OpenAI 스모크 2건으로만 확인 |
| **핵심 결정 ①** | **오병합이 미검출보다 나쁘다** — 확신도가 기준 미만이면 자동으로 합치지 않고 사용자에게 묻는다 |
| **핵심 결정 ②** | LLM 한 번에 맡기지 않고 **후보 검색 → 규칙 필터 → LLM 판정 → 확신도 분기** 4단계로 나누고, 모든 판정 근거를 trace에 남긴다 |
| **핵심 결정 ③** | **기능보다 평가 장치를 먼저** — 비교 방식 5종을 같은 인터페이스로 만들어 "LLM 한 번이면 되지 않나?"에 숫자로 답할 준비를 했다 |
| **개발 방식** | Claude Code로 개발. 계획 · 구현 · 검증을 다른 모델의 에이전트에 나누고 사람이 단계마다 승인하며, 절차는 훅으로 강제한다([개발 방식](#개발-방식--코딩-에이전트-하네스)) |

## 왜 어려운가 — 핵심 기여

한국어 대화는 사람을 이름으로 부르지 않는다. 같은 인물이 이렇게 등장한다.

```
팀장 → 김팀장 → 우리 팀장님 → 그 사람 → 걔 → 부장님(승진 후) → 김선배
```

이를 한 인물로 묶는 **엔티티 해석(Entity Resolution)** 이 시스템 전체 성능을 좌우한다. 잘못 병합하면 신뢰가 즉시 무너지고(오병합), 못 묶으면 메모리가 파편화된다(미검출). 이 프로젝트는 **오병합이 미검출보다 훨씬 나쁘다**는 비대칭 비용을 설계의 뿌리로 삼는다.

- **4단계 해석 파이프라인**: 후보 검색(별칭 임베딩 top-K) → 규칙 필터(호칭 사전·위계·관계 태그) → LLM 판정(구조화 출력) → 확신도 미달 시 사용자에게 묻기. LLM 단일 호출로 해석하지 않는다.
- **확신도 3신호 결합**: `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`. LLM 로그 확률은 쓰지 않고, 자기보고 점수를 보정표로 뒷받침한다.
- **임계치 2개**: `T_merge`(초기 0.8) 이상만 자동 연결. 그 미만은 반드시 `ask_user` — `[T_new, T_merge)`는 `identity` 질문("김팀장님 말씀이신가요?"), `T_new`(초기 0.3) 미만은 `new_person` 질문("새로 기억해둘까요?"). 두 값은 초기값이며 파일럿 평가(P4) 곡선으로 방향을 보고 최종 평가(P10)에서 확정한다.
- **`ask_user`는 별도 툴**: "모른다"를 에이전트가 스스로 판단하는 행동으로 두고, 비동기 대기 질문(칩 응답 후 루프 재개)으로 구현한다.
- **모든 판정에 근거를 남긴다**: 후보·확신도 분해·툴 호출·토큰을 `agent_traces`에 기록한다.

## 무엇을 만드는가

| 화면 (3개 고정)| 툴 7종 (LLM이 선택·호출) |
|---|---|
| 채팅<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | `search_person`, `create_person`, `update_person` |
| 인물 카드 (사실 · 타임라인 · 마지막 접촉) | `add_event`, `add_schedule` |
| 브리핑 | `get_briefing`, `ask_user` |

- **3계층 메모리**: 작업 메모리(최근 N턴) → 에피소드(`events`, 원문 보존) → 시맨틱(`person_facts`, 근거 이벤트 링크 `fact_sources`).
- **반복 패턴 감지(규칙)**: 같은 인물의 같은 사건 유형이 90일 내 3회 이상이면 패턴 사실을 만든다. LLM은 문장화만 한다.
- **브리핑**: 일정 24시간 전에 웹푸시. "제안"은 기록된 사실에서 나오는 한 줄 행동 제안으로 한정한다(고민 상담이 아니다).

**의도적으로 제외한 것**: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, 화면의 관계 태그 필터링(해석 단계의 관계 태그 규칙 필터와는 별개). "왜 안 했는가"를 설명할 수 있는 것이 범위 통제다.

### 목표 데모 시나리오 (3분)

> 아래는 완성 목표다. 지금은 엔티티 해석 · 툴 · 평가 장치까지 구현했고, 대화 루프 · 인물 카드 · 브리핑 · 웹푸시는 P5 이후에 만든다([진행 상태](#진행-상태)).


1. "오늘 김팀장이랑 또 부딪혔어" → 인물 인식, "김팀장을 기억해둘까요?"
2. 몇 턴 대화 → 인물 카드가 실시간으로 채워진다
3. "다음 주 화요일에 그 사람이랑 회의 있어" → 일정 자동 추출
4. ★ "부장님이 또 그러시더라" → "김팀장님 말씀이신가요? 승진하셨다면 반영할게요"
5. 브리핑: "내일 15시 김부장 회의 — 최근 3회 모두 공개 석상 지적 패턴. 1:1 요청을 제안합니다"

## 기술 스택

| 영역| 선택 |
|---|---|
| 백엔드 | FastAPI (Python), Docker |
| LLM<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | 공급자 중립 판정기 — `anthropic`·`openai`·`gemini` 등록표(`JUDGES`)에서 `LLM_PROVIDER`로 고른다. **기본값 `openai`**(D11, 사용자 결정 — 기획서 전제인 Claude API에서 운영 기본값만 바뀌었고 확신도 공식·프롬프트·출력 스키마는 같다) |
| 임베딩 | OpenAI `text-embedding-3-small`, **1536차원** (파일럿으로 확정 — `reports/embed_pilot.md`) |
| DB | PostgreSQL + pgvector (지금은 로컬 Docker, 운영은 P9에서 결정). 별도 벡터 DB 없이 별칭 테이블과 임베딩을 같은 DB에서 조인 |
| 프론트 | **(계획 · P8)** React + PWA (S3 + CloudFront) — 아직 없음 |
| 인프라 | **(계획 · P9)** Terraform, GitHub Actions, SSM Parameter Store, EC2 + Caddy(Let's Encrypt) — 아직 없음 |

데이터 모델(스키마 v2): `persons`, `person_aliases`(별칭 단위 임베딩), `person_facts`, `fact_sources`, `events`, `schedules`, `pending_questions`, `push_subscriptions`, `agent_traces`. 권위 있는 정의는 `CLAUDE.md`와 `docs/wiki/specs/S3.1-schema-v2.md`.

## 평가

- **지금(P4 파일럿)**: 파일럿 데이터셋 **40건**(아래 "평가 데이터셋" 절)으로 인물 해석 지표만 잰다 — P/R/F1, **오병합률**(핵심), 미검출률, `ask_user` 종류별 비율, 보정도.
- **목표(P10 최종)**: 한국어 대화 **150건**(승진·대명사·별칭·정상·신규 인물)으로 넓히고, 이벤트 추출 F1·툴 호출 정확도를 더한다. 추출 주체인 에이전트 루프(P5)가 생긴 뒤라야 잴 수 있어서 P4 범위에서 뺐다.
- 베이스라인 3종과 같은 데이터·같은 지표로 비교하고, `T_merge`를 0.5~0.95(0.05 간격 10점, `T_new` 0.3 고정)로 바꾸며 오병합률·질문율·미검출률 트레이드오프 곡선을 그린다.
- 수치는 재현 가능해야 한다. 성능 미달도 결과이며, 재시도 대신 실패 케이스 분석을 산출물로 남긴다. 산출물은 `reports/`(현재는 `embed_pilot.md`만 있다).

### P4 파일럿 평가 파이프라인 (계획 초안 — `docs/wiki/packages/P4-pilot-eval/01-plan.md`, 701fb8d)

```
data/scenarios 40건 ─ 시나리오마다 사전 상태 적재·끝나면 되돌림(오염 방지)
   └ 다섯 방식 × mention × T_merge 10점  ── evaluation/runner.py
        ▼
reports/pilot/raw-<ts>.jsonl   원시 판정 (LLM 응답을 다시 사지 않도록 먼저 저장)
        ▼ 지표는 이 파일에서만 계산
reports/metrics.json      오병합률·미검출률·P/R/F1·ask_user 종류별 비율   (evaluation/metrics.py)
reports/calibration.json  s_llm 0.1 구간별 실제 정답률, 공급자·모델별 분리  (evaluation/calibration.py)
reports/curve.csv         T_merge 스윕 곡선                                (evaluation/curve.py)
reports/eval.md           metrics.json 한 파일만 읽어 생성(멱등)             (evaluation/report.py)
reports/failure_cases.md  오병합·미검출·강제 강등 유형별 분석 — 미달이 아니어도 만든다
```

- 실행은 `LLM_PROVIDER=openai` 1벌(D11)이며 `meta.provider`·`meta.model`에 기록한다. LLM 비용 실측(P0-cost)은 이 패키지의 U6로 흡수했다(40건 실측 → 150건 외삽).
- 하지 않는 것: `app/` 수정, 골드 라벨 수정(수치가 나빠도 `data/`를 손대지 않는다), `top_k`·가중치 스윕(40건으로 튜닝하면 과적합), 운영 임계치 확정(P10 몫).
- 게이트: 수치가 나쁘면 재시도가 아니라 `failure_cases.md` + ER 설계(S3.3) 재설계 여부를 사용자 결정으로 올린다. **P4를 통과하기 전에는 P5 이후를 시작하지 않는다.**

## 진행 상태

| 단계| 내용 | 상태 |
|---|---|---|
| P0 | 임베딩 공급자 파일럿 (D4) | **완료** — small/large 모두 기준 통과, `text-embedding-3-small` N=1536 확정 |
| P0 | 로컬 docker-compose (pgvector) | **완료** — `SELECT '[1,2,3]'::vector` 통과, pgvector 0.8.6 (pg16) |
| P0 | LLM 비용 실측 | **P4-pilot-eval U6로 흡수**(사용자 결정 — 40건 실측으로 150건 외삽) |
| P1 | 스키마 v2 마이그레이션 (Alembic) | **완료** — 9테이블·CHECK 4·FK CASCADE 6·`vector(1536)`·인덱스 10, upgrade/downgrade 왕복·`alembic check` 통과, verifier 04-review 완료 |
| P1 | 파일럿 데이터셋 | **완료** — 40건·5범주(승진 8/별칭 8/대명사 8/일반 10/신규 6), `schema_version` 2, `validate_scenarios --strict` rc=0, 라벨 검수 verifier 40/40·사용자 12/12, verifier 04-review 완료(5cac9bf) |
| P2 | 툴 7종 v2 + FastAPI 골격 | **완료** — 시그니처 = CLAUDE.md(tools_check 7/7), ask_user→pending_questions, D1 확인 강제, GET /health·POST /answers, pytest 206, verifier 04-review 완료 |
| P3 | 엔티티 해석 4단계 (P3-er) | **완료**(verifier 04-review 완료) — ER 4단계(`app/er`) + 확신도 3신호·두 임계치 + trace 1행, 회귀 3종 통과(승진 0.863 merge / 이모 배제 / 동명이인 0.575 identity) |
| P3 | 베이스라인 3종 (P3-baselines) | **완료**(verifier 04-review 완료) — `evaluation/` 다섯 방식(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`)이 같은 함수·같은 인자로 호출 가능(parity 46건, 부수효과 0) |
| P3<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | LLM 공급자 등록표 (P3-llm-providers) | **완료**(verifier 04-review 완료, 수용 기준 11/11·부정 검사 43/43) — 등록표 `JUDGES`(anthropic·openai·gemini)·활성 스위치 `LLM_PROVIDERS_ENABLED`·기본 `openai`(D11), Gemini 판정기 구현, pytest 918 passed. **실 API 호출로 검증된 공급자는 1/3(openai)** — `er_smoke.py`("부장님" → 후보 중 부장 인물, 확신도 0.838 · merge)와 `baseline_smoke.py`(llm_single, identity 질문)가 gpt-4o-mini로 통과했다(`docs/wiki/evidence/20260919-openai-live-smoke.txt`). anthropic · gemini 실호출과 소견 F-87c597 종결은 P4에서 한다 |
| P4 | **파일럿 평가(게이트)** — 곡선·보정표 초안, 임계치 방향 확인 | **계획 초안**(701fb8d, 결정 A~K) — 착수 대기 |
| P5~P9 | 에이전트 루프 · 메모리·패턴 · 브리핑 · 웹푸시 · 프론트 3화면 · 인프라(Terraform·Actions·Caddy) | P4 통과 후 |
| P10 | 150건 데이터셋 완성 + 최종 평가 + `reports/eval.md` | P4·P9 후 |
| P11 | 데모 리허설(사용자) | P9 후 |

최신 상태는 `docs/wiki/HANDOFF.md`(지금 어디, 다음 무엇)와 `docs/wiki/journal.md`(시간순)에 있다.

**다음 할 일** (`HANDOFF.md` 기준): ① P4-pilot-eval 착수 — 01-plan 초안에 P3-llm-providers 완료 해시를 채우고 `/devlog start` → verifier 계획 검증 → 사용자 계획 승인 ② 사용자 실호출 스모크(user-setup 03·08) ③ P9 전에 AWS 배포 결정 10개 확정(user-setup 09).

## 설계 과정 — 기획서 검증에서 커밋까지

코드를 쓰기 전에 기획서부터 검증했다. 기획서 원본(`docs/proposal.md`)은 고치지 않고, 문제를 번호로 기록한 뒤 결정·명세·작업 패키지로 이어 붙여 **모든 커밋이 왜 생겼는지 거꾸로 추적**할 수 있게 했다.

```
기획서 원본 ─검증→ R1~R20 ─결정→ D1~D11 ─명세→ S3.1~S3.7 ─구현→ 패키지 P0~P11 ─커밋→ Refs: P D S R
(proposal.md)   (proposal-review.md, H5·M9·L6)  (decisions/)    (specs/)            (packages/<id>/)
```

- **예 — R4 → D3**: 기획서는 확신도에 "LLM 출력 확률"을 쓰겠다고 했지만 Claude API는 로그 확률을 주지 않는다(R4, 심각도 H). 그래서 D3에서 확신도를 "구조화 출력 자기보고 `s_llm` + 임베딩 + 규칙" 3신호 결합으로 바꾸고, 자기보고 점수는 보정표(`calibration.json`)로 뒷받침하기로 했다. P3-er가 구현했고 P4가 보정표로 검증한다.
- 그 밖의 예: 트레이드오프 문장의 임계치 방향이 반대였다(R3 → D10, 두 임계치). 인물당 임베딩 1개는 호칭 변이에 불리했다(R9 → D5 별칭 단위 임베딩). 기획서 7장 월별 일정은 의존성과 충돌해 **폐기**하고 날짜 없는 의존 순서로 바꿨다(R1·R2). 부록의 "F1 0.87·오병합률 3%"는 측정 결과가 아니라 예시라고 원본 상단 안내문에 밝혔다(R16).
- 기획서가 바뀌면 `/devlog change`로 이 사슬을 거꾸로 타 영향 범위(R→D→S→P→`git log --grep`)를 구하고, 이행 중에는 `CURRENT.md`의 `frozen`으로 제품 코드 쓰기를 막는다.

## 저장소 구조

```
CLAUDE.md                 프로젝트 규칙 — 불변 원칙 9개, 툴 시그니처 v2, 스키마 v2, 개발 프로세스
SERVER-CHECKLIST.md       실서버 점검 가이드 (배포 직후 점검·되돌리기·승격 기준)
app/                      제품 코드 — api/(FastAPI 라우트) · db/(모델·세션) · tools/(툴 7종) · er/(엔티티 해석 4단계) · embedding.py · settings.py
alembic/                  스키마 마이그레이션 (versions/0001_schema_v2.py)
evaluation/               평가 장치 — resolvers/(다섯 방식·공통 인터페이스) · scenario_state.py(사전 상태 적재)
data/scenarios/           파일럿 데이터셋 40건 · schema.json(라벨 규칙) · manifest.json(배분표)
scripts/                  검사: db_check · schema_check · tools_check · validate_scenarios / 데이터: dump_scenarios · backfill_embeddings / 실호출: embed_pilot · er_smoke · baseline_smoke
tests/                    pytest (DB 없이 도는 단위 테스트 + 로컬 DB가 있어야 도는 통합 테스트)
reports/                  평가·파일럿 산출물 (embed_pilot.md, 이후 eval.md · metrics.json · calibration.json)
docker-compose.yml, docker/  로컬 PostgreSQL + pgvector (initdb에서 vector 확장)
requirements.txt, requirements-dev.txt  런타임 / 개발·테스트 의존성 (== 고정)
docs/proposal.md          기획서 원본 (본문 불변, 상단 안내문만 갱신)
docs/proposal-review.md   기획서 검증 20항목
docs/resolution-plan.md   결정 D1~D10 · 설계 명세 S3.1~S3.7 · 착수 준비(P0) · 구현 순서 P1~P11
docs/backlog.md           작업 목록 (수용 기준의 권위)
docs/user-setup/          사용자가 직접 해야 하는 설정·결정 카드 01~09
docs/wiki/                개발 위키: 검증(R)→결정(D)→명세(S)→패키지(P) 카드, 교훈(L), 보안·검증 규칙, HANDOFF·journal·registry
.claude/                  개발 하네스: 에이전트 4종, 스킬 5종, 훅 10개, 검증 스크립트
.githooks/pre-commit      git 자체가 집행하는 비밀 파일·비밀 문자열·5MB 초과 파일 커밋 차단
```

## 개발 방식 — 코딩 에이전트 하네스

이 저장소는 Claude Code로 개발하며, 에이전트가 기획서 의도에서 벗어나지 않도록 절차를 훅으로 강제한다. 2026-09-03 ~ 09-15에 82커밋, 패키지 8개를 닫았다.

### 패키지 생애주기

모든 작업은 패키지(`docs/wiki/packages/<id>/`) 하나에서 같은 다섯 문서를 거친다.

```
01-plan ── architect 초안, 범위·산출물·수용 기준·결정 표
02-plan-verify ── verify-plan.sh 기계 검증 + verifier 점검표 8행 → 사용자 계획 승인 → CURRENT.md active
03-log ── 작업 단위(U1, U2 …)마다 구현 → 테스트 → 승인 커밋, 판단·실측 기록
04-review ── verify-impl.sh + verifier 완료 검토(수용 기준 표를 evidence로 한 행씩 판정) → 사용자 승인
05-remediation ── FAIL/WARN 소견(F-xxxxxx)의 원인·해결 단계·재검증
```

- 커밋 이력도 이 형태다: `docs(<id>): 계획·계획검증 승인` → `feat(<id>): U1 …` ~ `U9` → `docs(<id>): 완료 검토 04-review`. 증거는 패키지별 `evidence/`에 남기며 지금까지 **evidence 파일 508개**다(pytest 출력, 검증 스크립트 출력, SQL 조회 결과, 검수 기록).
- `registry.md`(무엇이 이미 있나 — 단위 시작 전 grep해 중복 구현을 막는다), `journal.md`(시간순), `HANDOFF.md`(지금 어디·다음 무엇)를 커밋마다 갱신한다.

### 역할 분리와 승인 게이트

- **역할별 모델 분리**: 계획(architect, opus) · 구현(backend-agent, sonnet) · 평가 데이터(eval-agent, opus) · 검증(verifier, fable). 같은 컨텍스트·같은 모델이 자기 결과를 평가하지 않는다 — 점검표·완료 검토에 `검증자: verifier`가 없으면 검증 스크립트가 FAIL한다.
- **사람이 단계마다 승인한다**: 에이전트 위임 시작(계획·구현·검증), 계획, 커밋(LLM이 변경·이유·검증·Refs 초안 → 사용자 승인), 푸시, main 승격이 모두 사용자 승인 대상이다. 서브에이전트는 커밋하지 않는다.
- **게이트**: 제품 코드는 `CURRENT.md`에 활성 패키지가 있어야 쓸 수 있고(한 번에 하나), 기획서 변경 중(`frozen`)이면 전부 막힌다. P4 파일럿 평가 전에는 P5 이후를 시작하지 않는다.
- **컨텍스트 소진 대비**: 세션 시작·압축 직후 `HANDOFF.md`가 자동 주입되고, 변경 파일보다 HANDOFF가 오래됐으면 Stop 훅이 턴 종료를 막는다. 중단된 작업이 있으면 다른 일보다 먼저 사용자에게 우선순위를 묻는다(`/devlog resume`).

### 검증은 증거로만 — 소견(F-xxxxxx) 루프

스크립트 출력 파일, 테스트 출력, 커밋 해시, 존재하는 파일 경로만 증거다. "확인했습니다"는 검증이 아니다(`docs/wiki/verification.md`).

```
verify-plan.sh / verify-impl.sh / pytest → findings.py → 05-remediation.md 에 F-xxxxxx 블록
→ 원인 가설 · 확인 명령 출력 · 해결 단계(각 단계에 완료 판정 명령) → 조치 → 같은 명령으로 재검증
→ 3회 재검증 후에도 열려 있으면 재시도하지 않고 사용자에게 보고
```

- 소견은 지우지 않는다 — 8개 패키지의 `05-remediation.md`에 90여 건이 "무엇이 왜 실패했고 어떻게 고쳤나"로 남아 있다.
- 실례: **F-ca12ad** — P2-tools 리뷰가 찾은 `@traced`의 `tool_error` 경로 결함(flush 실패 뒤 같은 세션에 trace를 쓰려다 `PendingRollbackError`가 원래 예외를 가림)을 P3-er U1에서 세이브포인트로 고쳤다(2b82882). **F-7bea05·F-1ba055** — 데이터가 0건이던 시점의 상태를 단정하던 검증기 테스트가 시나리오 추가로 깨진 것을, 시점과 무관한 단정으로 바꿔 해소했다(baee71e). **F-4ef1a3** — 수용 기준과 검증 스크립트 규칙이 충돌해 verifier가 "부분완료"로 판정했고, 우회하지 않고 사용자 결정으로 풀었다(P3-llm-providers). **F-87c597**(실호출 미검증)은 P4·사용자 스모크가 닫을 때까지 열어 둔다.

### 교훈 — 사고가 규칙이 되고, 규칙이 훅이 된다

| 교훈| 무슨 일이 있었나 | 바뀐 규칙 | 집행 |
|---|---|---|---|
| L-001<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | 첫 커밋 2건을 `main`에 직접 푸시 | 작업·푸시는 `dev`, `main`은 승격으로만 + 에이전트 git log 연동 | `safety-guard.sh`가 main 직접 푸시 차단(승격은 승인 마커가 있을 때 `dev:main`만), `gitlog.sh` |
| L-002 | 한 세션·한 모델이 계획·점검표·완료 검토를 모두 씀 | 계획·구현·검증을 다른 모델·새 컨텍스트로 분리, verifier 신설 | `verify-plan.sh`·`verify-impl.sh`가 검증자 줄 없으면 FAIL |
| L-003 | dev 푸시 직후 사용자 결정 없이 다음 작업 시작 | 푸시 뒤에는 승격/수정 결정까지 멈춤 | `.awaiting-decision` 마커를 훅이 강제 |
| L-004 | 계획 승인 직후 에이전트 5회를 스스로 연쇄 위임 | 계획·구현·검증 단계는 매번 묻고 시작 | `delegate-guard.sh`(Agent 도구 PreToolUse) |

네 교훈 모두 첫날 하네스 커밋(d6d1afb·64f92e4·4df323f·9d23fd7)으로 반영됐다. 자세한 경위는 `docs/wiki/lessons/`.

### 하네스 구성

- **에이전트 4종**(`.claude/agents/`) · **스킬 5종**(`devlog` 패키지 절차, `commit` 승인 커밋, `entity-resolution`, `eval-harness`, `agent-observability`).
- **훅 10개**(`.claude/hooks/`): `safety-guard`(파괴 명령·외부 전송·main 직접 푸시) · `commit-guard`(승인 없는 커밋·푸시, 승인 후 바뀐 초안) · `secret-guard`(비밀 파일 쓰기·키 문자열 삽입) · `stage-gate`(활성 패키지·동결) · `delegate-guard`(위임 승인) · `approve-commit`(사용자 승인 직후 1회용 마커 발급) · `commit-cleanup`(마커 폐기·journal 기록) · `handoff-check`(Stop) · `session-start`(HANDOFF 주입) · `precompact`(압축 시점 기록).
- **검증 스크립트**(`.claude/scripts/`): `verify-plan.sh` · `verify-impl.sh` · `findings.py` · `gitlog.sh` · `test-guards.sh`(훅 자체 테스트 — 결과는 `docs/wiki/evidence/20260903-test-guards*.txt`, 실패 0).
- **권한 거부 목록**(`.claude/settings.json`): `.env`·`*.pem`·`*.key`·`*.tfstate` 읽기, `sudo`, `rm -rf`, `git push --force`, `git reset --hard`, 승인 마커 파일 직접 쓰기.
- **git pre-commit**(`.githooks/`): 훅과 별개로 git 자체가 비밀 파일·5MB 초과 파일 커밋을 막는다.

### 브랜치와 승격

작업·푸시는 `dev`, 배포는 `main`. 원칙은 dev를 실서버에서 검증한 뒤 `/commit release`로 승격하는 것이다(`SERVER-CHECKLIST.md`). **아직 실서버가 없으므로(P9 전)** 지금까지의 승격은 패키지 단위로 로컬 검증(pytest·`verify-impl.sh` FAIL 0)과 사용자 결정만으로 했다 — 이 사실을 `HANDOFF.md`에 명시해 두었고, 첫 실서버 검증은 P9 배포 뒤 체크리스트로 한다. dev 푸시 뒤에는 사용자가 승격/수정/보류를 정할 때까지 멈춘다(예: P1-schema 중간 푸시는 "패키지 단위로 승격"하기로 보류).

### 보안

- **비밀**: `.env`·키 파일은 에이전트가 읽지도 쓰지도 않는다. 코드는 `os.environ`으로만 읽고, 문서·로그·evidence·예외 메시지에는 변수 **이름**만 남긴다.
- **파괴 명령 금지**: 강제 푸시·이력 파괴·재귀 삭제·`sudo`, `terraform destroy`/`apply -auto-approve`, `docker … prune`/`volume rm`/`compose down -v`, 셸 `DROP`/`TRUNCATE`(스키마 변경은 Alembic 파일로), 외부 전송(`curl -d`, `scp` 등)은 훅이 막는다. 막히면 우회하지 않고 사용자에게 명령을 보여 직접 실행을 요청한다.
- **제품이 지킬 것**(기획서 9장 제3자 개인정보): 인물 단위 완전 삭제(CASCADE), `pending_questions.context`에 재개에 필요한 것만 저장, 모든 조회에 `user_id` 조건, VAPID 개인키는 SSM, DB는 프라이빗 서브넷·저장/전송 암호화. 평가 데이터에는 가상 성명만 쓴다.
- 권위 문서: `docs/wiki/security.md`.

### 사용자 몫 분리

에이전트가 **할 수 없거나 해서는 안 되는 일**(비밀 값 입력, AWS 콘솔 조작, 실 API 호출, 승인 결정)은 `docs/user-setup/` 카드 9개로 분리했다. 카드마다 "언제 필요한가 → 왜 사용자 몫인가 → 절차 → 끝났다는 증거 → 에이전트에게 알릴 말" 순서다. 현재 LLM·임베딩 키 미입력, AWS Budgets 미완, 실호출 스모크 03·08 미실행이다.

자세한 규칙은 `CLAUDE.md`, 절차는 `.claude/skills/devlog`·`.claude/skills/commit`, 교훈은 `docs/wiki/lessons/`.

## 로컬에서 해 보기

```bash
# 1. 환경변수 — 키 이름만 적힌 .env.example 을 복사해 값을 채운다 (.env 는 git 제외)
cp .env.example .env

# 2. 의존성 (Python 3.13) — 런타임 + 개발·테스트 의존성, 버전은 == 로 고정
pip install -r requirements-dev.txt

# 3. 테스트 (네트워크 불필요 — LLM·임베딩은 전부 스텁)
python -m pytest -q tests/

# 4. 임베딩 파일럿 재현 (OPENAI_API_KEY 필요, 호칭 30개 × 모델 2개 = 236 토큰)
python scripts/embed_pilot.py
```

로컬 DB가 떠 있지 않으면 DB가 필요한 통합 테스트는 **skip**되고 DB 없이 도는 테스트만 통과한다(예: P3-baselines 시점 627 passed · 232 skipped). 전체 통과(현재 918 passed)는 아래 "로컬 DB"와 "스키마 마이그레이션"을 마친 뒤 `POSTGRES_PORT`를 맞춰 실행한 결과다.

### 로컬 DB (docker-compose + pgvector)

사전 조건: Docker Desktop 실행 중. `.env`가 없다면 `.env.example`을 복사해 시작하고, DB 절의 `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` / `POSTGRES_PORT` 4개와 `DATABASE_URL`을 **같은 값**으로 유지한다(포트를 바꾸면 둘 다 바꾼다).

```bash
# 1. 기동
docker compose up -d

# 2. 상태 확인 (STATUS 열이 healthy 인지 확인)
docker compose ps

# 3. 접속 검사 (psycopg 설치 후 실행)
pip install "psycopg[binary]"
python scripts/db_check.py
# 기대 출력: extversion, SELECT '[1,2,3]'::vector -> [1,2,3], 종료 코드 0

# 4. 중지 (컨테이너만 내린다 — 데이터 볼륨은 유지)
docker compose down
```

- **볼륨 삭제 금지**: 데이터 볼륨 `pgdata`를 지우는 옵션(`security.md` §4가 금지하는 compose 옵션·`docker volume rm`·prune)은 쓰지 않는다. `docker compose down`만 쓴다.
- **5432 포트 충돌**: 로컬에 이미 다른 PostgreSQL이 5432를 쓰고 있으면 기동이 실패한다. `.env`의 `POSTGRES_PORT`와 `DATABASE_URL`의 포트를 **같이** 다른 값(예: 5433)으로 바꾼다. `db_check.py`는 두 값이 어긋나면 변수 이름만 경고하고(비밀번호 값은 출력하지 않는다) 종료 코드는 바꾸지 않는다.
- **이미지 태그 메모(미결)**: `pgvector/pgvector:pg16`으로 시작한다. RDS PostgreSQL 메이저 버전이 정해지는 P9-infra에서 이 태그를 재확인한다.
- P1-schema(스키마 마이그레이션)는 이 로컬 DB가 떠 있는 것을 선행 조건으로 쓴다.

### 스키마 마이그레이션 (Alembic)

사전 조건: 로컬 DB가 기동 중(위 절)이고 `pip install -r requirements-dev.txt`로 런타임 의존성(`requirements.txt` — SQLAlchemy·Alembic·psycopg·pgvector·FastAPI·uvicorn·httpx·openai·anthropic·google-genai)과 개발 의존성(pytest·jsonschema)이 설치되어 있다. `alembic.ini`의 `sqlalchemy.url`은 비어 있다 — `alembic/env.py`가 `app.config`를 통해 환경변수에서 접속 정보를 읽는다(`.env`는 읽지 않는다).

```bash
# 적용 (9개 테이블 + CHECK 4 + FK CASCADE 6 + vector(1536) + 인덱스 10)
alembic upgrade head

# 검사 (서버 버전·확장·9테이블·CHECK·FK·인덱스·person_embeddings 부재)
python scripts/schema_check.py

# 모델↔마이그레이션 일치 확인 (변경 없음이 기대값)
alembic check

# 되돌리기 — 빈 개발 DB에서만. 데이터가 있는 DB에서는 사용자가 직접 판단한다(볼륨 삭제 대신 이 명령을 쓴다)
alembic downgrade base
```

로컬 포트가 5432가 아니면(위 절의 5433 예시) 셸 변수로 앞에 붙인다:

```bash
# bash
POSTGRES_PORT=5433 alembic upgrade head
```

```powershell
# PowerShell
$env:POSTGRES_PORT="5433"; alembic upgrade head
```

서버 버전은 로컬 pg16 기준으로 검증했다(`scripts/schema_check.py`·`scripts/db_check.py`의 `SELECT version()` 출력). RDS 메이저 버전은 P9-infra에서 재확인한다.

마이그레이션 설계 판단(P1-schema):

- `0001`은 `alembic revision --autogenerate` 초안을 검토해 보정했다 — 초안에 빠진 `CREATE EXTENSION IF NOT EXISTS vector`를 추가하고, `Vector(1536)`·CHECK 이름·부분 인덱스 조건·CASCADE 6·복합 PK는 항목별로 확인했다(원본 초안은 evidence에 보존, 보정 내역은 파일 머리 주석).
- **벡터 인덱스(HNSW/IVFFlat)는 일부러 만들지 않았다** — 데이터 0건 시점에는 순차 스캔이 더 빠르고, `m`·`ef_construction`·거리 연산자를 정당화할 측정치가 없다(원칙 8). 실제 후보 검색 쿼리와 데이터가 생긴 뒤 추가한다.
- 증거: upgrade → downgrade base → upgrade 왕복 출력, `alembic check` "변경 없음", `schema_check.py` 구조 검사 출력이 `docs/wiki/packages/P1-schema/evidence/`에 있다.
- 임베딩 공급자를 바꾸면 `person_aliases.embedding` 전체를 재임베딩하는 마이그레이션이 필요하다(D4).

### 백엔드 실행 (FastAPI)

사전 조건: 로컬 DB가 기동 중이고(위 절) `alembic upgrade head`가 적용되어 있다(9개 테이블). `pip install -r requirements.txt`로 `fastapi`·`uvicorn[standard]`·`httpx`가 설치되어 있어야 한다.

```bash
# bash — 로컬 포트가 5432가 아니면(위 절의 5433 예시) 셸 변수로 앞에 붙인다
POSTGRES_PORT=5433 python -m uvicorn app.main:app --reload
```

```powershell
# PowerShell
$env:POSTGRES_PORT="5433"; python -m uvicorn app.main:app --reload
```

```bash
curl http://localhost:8000/health
```

기대 출력: `{"status":"ok","db":"up","alembic_revision":"0001"}` (DB 접속이 안 되면 503 `{"status":"degraded","db":"down"}` — 접속 문자열·비밀번호는 어떤 경우에도 본문에 나오지 않는다).

`ask_user`가 저장한 질문에 답하는 예:

```bash
curl -X POST http://localhost:8000/answers/1 \
  -H "Content-Type: application/json" \
  -d '{"answer": "응, 기억해줘"}'
```

| 상태 코드| 의미 |
|---|---|
| 200<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | 정상 저장 — `{"question_id": 1, "status": "answered"}` |
| 404 | 그런 `question_id`가 없음 |
| 409 | 이미 답했거나(already_answered) 24시간이 지나 만료됨(expired) |
| 422 | 저장된 `options` 밖의 답, 요청 본문 형식 오류 |

이 두 엔드포인트(`GET /health`, `POST /answers/{question_id}`)는 답 저장까지만 한다 — 채팅·에이전트 루프(발화 → 툴 선택 → 응답, 저장된 context로 루프 재개)는 P5 에서 붙는다.

### 엔티티 해석(ER) 실행법

`app/er/`가 4단계(후보 검색 → 규칙 필터 → LLM 판정 → 확신도 분기)를 구현한다. 아래 명령은 실 PostgreSQL(로컬 포트가 5432가 아니면 `POSTGRES_PORT`를 앞에 붙인다)과 `.env`를 읽지 않는 `os.environ` 기반 설정을 전제로 한다 — **값·키 문자열은 이 문서에 적지 않는다.**

```bash
# 회귀 3종(승진 연결·이모 배제·동명이인 분리) 단독
POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k "promotion or aunt or homonym"

# 전체 테스트
POSTGRES_PORT=5433 python -m pytest tests/ -q -rs
```

- 승진 회귀의 `agent_traces` 증거(SQL 조회 결과)를 다시 만들려면 `ER_EVIDENCE_STAMP`로 접두를 준다 — 접두가 없으면 파일을 만들지 않는다(반복 실행이 저장소를 어지럽히지 않도록):

```bash
ER_EVIDENCE_STAMP=<접두> POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k promotion
```

- **NULL 임베딩 백필** (`person_aliases.embedding IS NULL`인 별칭을 채운다, 기본은 쓰기 없는 조회):

```bash
POSTGRES_PORT=5433 python scripts/backfill_embeddings.py --dry-run
POSTGRES_PORT=5433 python scripts/backfill_embeddings.py --apply   # OPENAI_API_KEY 필요 — 없으면 종료 코드 2
```

- **실 LLM 판정 스모크** (후보 2개짜리 판정 1회, 자동 테스트에는 포함하지 않는다 — 재현 불가능한 지표를 만들지 않기 위해):

```bash
python scripts/er_smoke.py                       # LLM_PROVIDER=openai(기본), OPENAI_API_KEY·OPENAI_MODEL 필요
python scripts/er_smoke.py --provider anthropic   # ANTHROPIC_API_KEY·ANTHROPIC_MODEL 필요
python scripts/er_smoke.py --provider gemini      # GEMINI_API_KEY·GEMINI_MODEL 필요(기본 모델 없음 — 미설정 시 InvalidValue)
```

  키가 없으면 종료 코드 2로 안내만 하고 끝난다(키·프롬프트 원문은 어떤 경우에도 출력하지 않는다). 출력은 `{provider, model, tokens_in, tokens_out, s_llm, matched_person_id, reason, confidence, band}` 키를 가진 JSON 한 줄이다. 지원 공급자는 `anthropic`·`openai`·`gemini` 세 가지이며(D11 등록표 `JUDGES`), `LLM_PROVIDERS_ENABLED`(쉼표 구분, 비우면 전체 켬)로 개발자가 원하는 공급자만 켤 수 있다 — 꺼진 공급자나 표에 없는 이름을 `LLM_PROVIDER`/`--provider`로 고르면 즉시 `InvalidValue`(메시지에 활성 목록)로 거부된다.

- **임계치·가중치 조정**: 환경변수 이름 `T_MERGE`·`T_NEW`·`W_LLM`·`W_EMB`·`W_RULE`(값은 `.env.example`에 이름만 있다 — 이 문서와 에이전트는 `.env`를 읽지 않는다). 조정은 P4-pilot-eval의 트레이드오프 곡선 결과로만 한다.

### 평가 데이터셋(파일럿 40건)

`data/scenarios/`는 엔티티 해석·이벤트 추출을 채점하기 위한 **한국어 대화 시나리오 40건**과 그 골드 라벨이다. 지표 계산(오병합률·미검출률·트레이드오프 곡선)은 여기서 하지 않는다 — P4-pilot-eval이 이 데이터를 읽어서 한다. 실명·연락처는 들어 있지 않다(가상 성명 목록 밖 이름은 검증기가 FAIL 한다).

- 5 카테고리: `promotion` 8(sc-001~008, 승진 호칭 변경) · `alias` 8(sc-009~016, 별칭 혼용) · `pronoun` 8(sc-017~024, 지시대명사) · `normal` 10(sc-025~034, 함정 없는 기준선) · `new_person` 6(sc-035~040, 신규 등록 판정).
- `schema_version` 2. 시나리오 1건 = 발화열 + 골드 라벨: `persons[]`(가상 성명·관계 태그·위계·별칭) · `seed_persons`(대화 전 이미 등록돼 있는 인물) · `mentions[]`(지칭 표면형 → 골드 인물) · `passing_mentions[]`(등록하면 안 되는 지나가는 언급) · `events[]`(`turn`·`type` 7종·`occurred_at_kind`) · `expected_ask_user.allowed`(허용 집합) · `trap`(오병합 유도 함정).
- 오병합 유도 함정 12건, `ambiguous` mention 3건, 일정 발화 4건. 일정(schedule) 골드 라벨은 없다 — P10에서 덧붙인다.

실행법(네트워크·DB·LLM을 쓰지 않는다):

```bash
python scripts/validate_scenarios.py --strict              # 검사 (0)~(15), rc 0/1
python scripts/validate_scenarios.py --strict --json       # 기계 판독 요약(ok·total·counts·issue_count)
python scripts/validate_scenarios.py --write-distribution  # manifest.json 배분표 재계산(멱등, 항상 LF)
python scripts/dump_scenarios.py --out <경로>.md            # 사람이 읽는 검수 패킷
python -m pytest tests/test_validate_scenarios.py -q       # 검증기 자체 테스트 69건
```

라벨 규칙 요약(권위는 `data/scenarios/schema.json`의 각 필드 description):

- `persons[].aliases`는 **대화 시작 전에 이미 알려진 별칭만** 적는다. 승진 후 호칭처럼 시스템이 대화에서 배워야 할 호칭은 넣지 않고, 두 인물이 나눠 쓸 수 있는 호칭(팀장님·부장님 …)은 양쪽 다 넣거나 양쪽 다 뺀다 — 비대칭이면 별칭 완전일치만으로 정답이 새어 나가 함정이 함정이 아니게 된다.
- `events` 규칙: (a) `occurred_at_kind`는 **그 턴 안의 시점 낱말만** 본다(앞 턴에서 상속하지 않고 문장 성분을 가리지 않는다. 시점 낱말이 있으면 `relative`, 날짜·시각이면 `absolute`, 없으면 `none`. 기간 표현은 시점이 아니다) (b) 미래 약속·계획은 이벤트가 아니다 (c) 승진·이직·취업 같은 신상 소식은 `personal_share` (d) 사용자가 참여하지 않은 사건(전해 들은 근황·인물끼리 한 일)도 `personal_share` — `meal`/`meeting`/`favor`/`conflict`/`praise`/`other`는 **사용자–인물 사이 사건**에만 쓴다 (e) 잔소리는 `conflict`. 행위의 한쪽이 사용자이면 어느 방향이든 호의는 `favor`, 업무 지시·과제 부과는 `other`이고, 부작위("그냥 넘어가주셨는데")는 사건이 아니다.
- `mentions[].ambiguous: true`인 지칭만 `gold_person_id: null`을 허용하며, 그 지칭은 오병합률·미검출률·F1 분모에서 뺀다(개수는 `manifest.json`의 `ambiguous_mention_count`).
- `passing_mentions[]`는 정답 인물이 **없는** 지칭이다. 여기서 인물 생성이나 `ask_user(kind=new_person)`이 나오면 오탐으로 센다.

검수 절차(데이터를 만든 쪽이 검수하지 않는다):

1. eval-agent가 시나리오를 쓰고 `dump_scenarios.py`로 검수 패킷을 만든다 — 패킷은 판정하지 않고 판정할 것을 나열한다.
2. verifier가 **새 컨텍스트**에서 전건 40/40을 검수해 지적을 남기고, 반영본을 재검수해 상태를 닫는다(반영한 사람이 자기 지적을 닫지 않는다).
3. 사용자가 함정 건과 지나가는 언급 건을 검수한다.
4. 기록은 한 파일: `docs/wiki/packages/P1-pilot-dataset/evidence/20260906-1938-label-review.md`(지적 22건 → 반영 21·기각 1·**열림 0**, 사용자 12/12 동의). 수용 기준 기계 검증 출력은 같은 폴더의 `20260907-1300-u7-acceptance.txt`.

라벨 결정 이력(검수 4라운드 — 위 규칙 요약은 이 과정에서 생겼다):

| 라운드| 지적| 무엇이 드러났고 어떻게 정했나 | 반영 커밋|
|---|---|---|---|
| 최초 검수<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | #1~#17<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | 오병합 유도 함정 8건(promotion 4 + alias 4) 중 **실제로 문맥 판정을 요구하는 것은 3건**뿐이었다 — 별칭 목록이 비대칭이라 완전일치만으로 정답이 새거나, 함정이 발화에 없거나, 사람도 못 푸는 연결을 정답으로 둔 건이 있었다. → 결정 I(aliases는 대화 전 알려진 것만·공유 호칭은 대칭), 결정 J(events 규칙 — 전해 들은 사건은 `personal_share`) 로 전건 재라벨, sc-002·sc-012 재작성. 실존 공인과 동명인 가상 성명 4건은 결정 L로 허용(흔한 이름, 문맥이 공인 아님) | 76add8a<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
| 재검수 | #18~#20 | 시간 표현 판정에 eval-agent가 임의로 세운 통사 하위 규칙이 끼어들었고(→ 결정 M: 그 턴에 시점 낱말이 있으면 문장 성분과 무관하게 `relative`), 지시 표현 mention 누락과 같은 구조인데 이벤트가 빠진 턴이 나왔다(→ 사용자–인물 행위 규칙). 라벨 규칙에 맞추려고 사용자 결정 없이 발화를 바꾼 sc-005 t4는 원문으로 되돌리고 이벤트만 뺐다(결정 N — 라벨을 맞추려고 데이터를 바꾸지 않는다) — 그 결과 `absolute` 표본이 1 → 0이 됐지만 성능에 유리하게 고치지 않고 손실을 그대로 기록했다 | 6906af4 |
| 3차 재검수 | #21~#22 | 사용자가 한쪽인 행위 규칙을 전건(160턴)에 적용하자 sc-034 t1 1건이 어긋났고(결정 O), `favor` 정의 문구가 한 방향만 적고 있었다(결정 P — 방향 무관) | aeed0bd |
| 4차 재검수 | — | 열림 0 확인, `--strict` rc=0 → 사용자 12건(함정 9 + 지나가는 언급 3) 검수 12/12 동의 | f78e9dc |

원칙: 검수자는 데이터를 고치지 않고 지적만 남기며, 반영은 eval-agent가, 지적을 닫는 것은 다시 검수자가 한다. 기각도 사용자 결정으로만 한다.

알려진 한계(P4·P10으로 넘긴다 — 성능에 유리하게 감추지 않는다):

- `occurred_at_kind: absolute` **0건** — 미래 약속 발화를 원문대로 되돌리면서 유일한 사례가 사라졌다. P10에서 과거 절대 날짜 발화를 보충해야 absolute 분모가 생긴다.
- 이벤트 type 편중: 전체 76건 중 `personal_share` 25 · `meal` 17 · `meeting` 12 · `favor` 10 · `conflict` 6 · `other` 5 · `praise` 1. `favor` 10건 중 사용자→인물 방향은 1건뿐이다.
- 위계 `하` 6/60, 발화 길이 10~26자, 턴 수 3~5로 폭이 좁다 — 실사용보다 쉬운 방향, 즉 **과대평가 편향**이다.
- 같은 가상 성명이 시나리오마다 다른 관계로 다시 등장한다. **P4 러너는 시나리오 사이에 DB를 비워야 한다** — 비우지 않으면 사전 상태가 오염돼 베이스라인 비교의 동일 조건이 깨진다.
- 소비자(P3-baselines·P4-pilot-eval)가 mention 단위 정보(함정 대상, 지칭별 기대 질문, 발화 안 위치, 선행사 턴 등)를 더 요구하면 FIX가 아니라 `schema_version`을 올린다.

### 베이스라인 3종 실행법

`evaluation/`은 **평가 장치**다 — 제품 런타임(`app/`)이 아니고, 의존 방향은 `evaluation → app` 한쪽뿐이다(제품 코드는 이 패키지를 import 하지 않는다). 여기 있는 것은 "엔티티 해석을 LLM 한 번으로 하지 않는다"(불변 원칙 4)를 **숫자로 반박당할 수 있게** 만드는 대비군이다: 같은 사전 상태·같은 지칭·같은 `ERConfig`로 네(등록 이름으로는 다섯) 방식을 돌려 S3.7이 요구하는 동일 데이터·동일 지표 비교를 성립시킨다.

| 등록 이름| 정의 | 임베딩 / LLM 호출| 모듈 |
|---|---|---|---|
| `proposed` | 제안 4단계 하이브리드(후보 검색 → 규칙 필터 → LLM 판정 → 두 임계치) 어댑터 | 1 / 0~1 | `evaluation/resolvers/proposed.py` |
| `exact_raw` | 문자열 완전일치(앞뒤 공백·대소문자만 정리) | 0 / 0 | `evaluation/resolvers/exact_match.py` |
| `exact_norm` | 완전일치 + 호칭 정규화(`app.er.dictionary.normalize()`를 지칭·별칭 양쪽에) | 0 / 0 | `evaluation/resolvers/exact_match.py` |
| `embedding_only` | 별칭 임베딩 top-K → 인물별 max 유사도에 두 임계치만 적용(규칙·LLM 없음) | 1 / 0 | `evaluation/resolvers/embedding_only.py` |
| `llm_single` | 사전 상태 **전체 인물 목록** + 발화를 구조화 출력 **한 번**에 보내 결정까지 받는다 | 0 / 1 | `evaluation/resolvers/llm_single.py` |

다섯 방식의 호출 형태는 글자 그대로 같다 — `get_resolver(name, **kwargs).resolve_mention(ctx, mention, utterance, hints=None, *, config=ERConfig())` → `MentionDecision{method, decision, person_id, score, candidates, signals, detail, tokens_in, tokens_out}`. `decision`은 `merge`/`identity`/`new_person`(D10과 같은 어휘)이고 `person_id`는 `merge`일 때만 채워진다. 어떤 방식도 인물·별칭·질문을 **쓰지 않는다**(부수효과 0 — 무엇을 할지만 답하고 실행은 P4 러너 몫이다). 시나리오의 사전 상태(`seed_persons` + `aliases`)를 DB에 적재하는 단일 출처는 `evaluation/scenario_state.py`의 `load_scenario_state(ctx, scenario, embedder=…)`이다(`embedder`를 주지 않으면 별칭 임베딩이 비어 임베딩 기반 두 방식이 `embedding_skipped`로 떨어진다).

```bash
# 방식 목록(= metrics.json 키)
python -c "from evaluation.resolvers import ALL_METHODS; print(ALL_METHODS)"

# 동일 인터페이스 계약 — 다섯 방식을 같은 함수·같은 인자로 호출(실물 시나리오 2건 적재)
POSTGRES_PORT=5433 python -m pytest tests/test_baseline_parity.py -q -rs

# 방식별 정의(완전일치 임베딩·LLM 0회 / 임베딩 단독 LLM 0회 / 단일 프롬프트 LLM 정확히 1회)
POSTGRES_PORT=5433 python -m pytest tests/test_baseline_exact_match.py tests/test_baseline_embedding_only.py tests/test_baseline_llm_single.py -q -rs
```

위 테스트는 전부 스텁(가짜 임베딩·`FakeJudge`·스텁 클라이언트)으로 돌아 **네트워크 호출 0**이다. 실제 공급자로 한 번 확인하려면:

```bash
python scripts/baseline_smoke.py                    # LLM_PROVIDER=openai(기본) · 사전 상태 3명 · 지칭 1건 · 실 LLM 1회, DB 미사용
python scripts/baseline_smoke.py --provider gemini   # GEMINI_API_KEY·GEMINI_MODEL 필요(기본 모델 없음 — 미설정 시 InvalidValue)
```

  환경변수 이름은 제안 방식과 같다 — `LLM_PROVIDER`·`ANTHROPIC_MODEL`·`OPENAI_MODEL`·`GEMINI_MODEL`과 키 이름 `ANTHROPIC_API_KEY`·`OPENAI_API_KEY`·`GEMINI_API_KEY`(값은 이 문서에도 `.env`에도 의존하지 않는다. 셸 환경에만 둔다). 세 공급자는 같은 등록표(D11 `JUDGES`)와 활성 스위치 `LLM_PROVIDERS_ENABLED`를 `judge.py`에서 재사용한다(표를 두 벌 두지 않는다). 종료 코드는 **2 = 키 없음**(이름만 안내), **3 = LLM 호출·응답 오류**이며, 출력 JSON 한 줄에는 프롬프트 **길이와 인물 수**만 들어간다(프롬프트 원문·키는 어떤 경우에도 출력하지 않는다).

이 절은 **인터페이스까지**다. 밴드 분포·정답률·오병합률·트레이드오프 곡선은 P4-pilot-eval이 이 다섯 이름으로 측정해 `reports/metrics.json`에 남긴다 — 여기서 수치를 말하지 않는 이유는 재현 가능한 수치만 리포트에 넣기 위해서다(불변 원칙 8).

## 배포 계획 (P9 — 아직 착수 전)

기준 문서는 `docs/user-setup/09-aws-deploy.md`(처음 규모: 사용자 몇 명)와 D7(TLS)이다.

```
브라우저(PWA) ─HTTPS→ CloudFront ─ /      → S3 (React 정적 빌드, 비공개 버킷)
                                 └ /api/* → EC2 1대: Caddy(Let's Encrypt) → FastAPI(Docker) → PostgreSQL + pgvector
비밀: SSM Parameter Store   배포: GitHub Actions(OIDC, 장기 키 없음) → SSM Run Command   비용 알림: AWS Budgets $10/$30/$50
```

- **D7 그대로**: ALB 없음, NAT 없음. 권장안은 443을 CloudFront 대역에만 열고, 서버 접속은 SSH(22) 대신 SSM Session Manager를 쓰는 것이다.
- **DB 두 안**: A안 — 같은 EC2의 docker compose(월 약 $22, 매일 `pg_dump` → S3 백업 필수) / B안 — RDS db.t4g.micro(월 약 $38). A안을 고르면 기술 스택(RDS)과 달라지므로 결정 카드(D12)를 남긴다.
- **배포 트리거 권장안은 수동 dispatch(커밋 해시 입력)** — 승격은 사람이 정한다는 L-001·L-003과 맞추고, 롤백은 이전 해시로 다시 dispatch한다.
- 리전·DB 안·인스턴스·도메인 등 **결정 10개**를 P9 착수 전에 사용자가 확정한다. 배포 직후 점검·되돌리기 기준·승격 절차는 `SERVER-CHECKLIST.md`(§0~§8)를 따른다.
- 가장 큰 변동비는 LLM 호출이다 — 비용은 P4 U6 실측으로 잡는다.

## 문서 안내

| 알고 싶은 것 | 보는 곳 |
|---|---|
| 왜 이렇게 설계했나 | `docs/wiki/decisions/D01~D11` |
| 개발 절차·증거·보안 규칙 | `docs/wiki/INDEX.md`(한 장 흐름), `docs/wiki/verification.md`, `docs/wiki/security.md`, `docs/wiki/lessons/` |
| 패키지별 계획·로그·검토·소견 | `docs/wiki/packages/<id>/01~05`, `evidence/` |
| 스키마·툴·해석 파이프라인·평가 명세 | `docs/wiki/specs/S3.1~S3.7` |
| 기획서에서 무엇이 바뀌었나 | `docs/proposal.md` 상단 안내문, `docs/wiki/review-index.md` |
| 실서버에 올린 뒤 무엇을 점검하나 | `SERVER-CHECKLIST.md` (dev → 실서버 검증 → main 승격의 "검증" 기준·증거 규약·되돌리기) |
| 지금 어디까지 왔나 | `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md` |
| **사용자가 직접 해야 하는 것**(API 키·AWS Budgets·실호출 스모크·로컬 DB·배포 비밀·승인 결정·데모·AWS 배포) | `docs/user-setup/README.md` 색인 → 카드 01~09 |
| 무엇이 이미 만들어져 있나 | `docs/wiki/registry.md` |
| 평가 데이터셋은 어디에 | `data/scenarios/` (검증기 `scripts/validate_scenarios.py`, 라벨 규칙은 `data/scenarios/schema.json`의 description) |

## License

MIT — [LICENSE](LICENSE)
