# 대화형 관계 메모리 에이전트

> 자연어 대화에서 자동 구축되는 개인 관계 메모리 기반 브리핑 시스템 — 1인 개발 캡스톤 프로젝트

사용자가 평소처럼 대화하면, 제품 속 **관계 메모리 에이전트**가 인물·사건·일정을 스스로 추출·해석해 장기 메모리를 쌓고, 만남 직전에 필요한 맥락만 요약(브리핑)해 준다. 입력을 요구하지 않는다는 점에서 수동 기록 도구와 다르고, 세션을 넘어 축적되며 같은 인물의 호칭 변이를 하나로 묶는다는 점에서 범용 LLM 채팅과 다르다.

## 왜 어려운가 — 핵심 기여

한국어 대화는 사람을 이름으로 부르지 않는다. 같은 인물이 이렇게 등장한다.

```
팀장 → 김팀장 → 우리 팀장님 → 그 사람 → 걔 → 부장님(승진 후) → 김선배
```

이를 한 인물로 묶는 **엔티티 해석(Entity Resolution)** 이 시스템 전체 성능을 좌우한다. 잘못 병합하면 신뢰가 즉시 무너지고(오병합), 못 묶으면 메모리가 파편화된다(미검출). 이 프로젝트는 **오병합이 미검출보다 훨씬 나쁘다**는 비대칭 비용을 설계의 뿌리로 삼는다.

- **4단계 해석 파이프라인**: 후보 검색(별칭 임베딩 top-K) → 규칙 필터(호칭 사전·위계·관계 태그) → LLM 판정(구조화 출력) → 확신도 미달 시 사용자에게 묻기. LLM 단일 호출로 해석하지 않는다.
- **확신도 3신호 결합**: `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`. LLM 로그 확률은 쓰지 않고, 자기보고 점수를 보정표로 뒷받침한다.
- **임계치 2개**: `T_merge`(초기 0.8) 이상만 자동 연결. 그 미만은 반드시 `ask_user` — 애매하면 "김팀장님 말씀이신가요?", 매우 낮으면 "새로 기억해둘까요?".
- **`ask_user`는 별도 툴**: "모른다"를 에이전트가 스스로 판단하는 행동으로 두고, 비동기 대기 질문(칩 응답 후 루프 재개)으로 구현한다.
- **모든 판정에 근거를 남긴다**: 후보·확신도 분해·툴 호출·토큰을 `agent_traces`에 기록한다.

## 무엇을 만드는가

| 화면 (3개 고정) | 툴 7종 (LLM이 선택·호출) |
|---|---|
| 채팅 | `search_person`, `create_person`, `update_person` |
| 인물 카드 (사실 · 타임라인 · 마지막 접촉) | `add_event`, `add_schedule` |
| 브리핑 | `get_briefing`, `ask_user` |

- **3계층 메모리**: 작업 메모리(최근 N턴) → 에피소드(`events`, 원문 보존) → 시맨틱(`person_facts`, 근거 이벤트 링크 `fact_sources`).
- **반복 패턴 감지(규칙)**: 같은 인물의 같은 사건 유형이 90일 내 3회 이상이면 패턴 사실을 만든다. LLM은 문장화만 한다.
- **브리핑**: 일정 24시간 전에 웹푸시. "제안"은 기록된 사실에서 나오는 한 줄 행동 제안으로 한정한다(고민 상담이 아니다).

**의도적으로 제외한 것**: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, 관계 태그 필터링. "왜 안 했는가"를 설명할 수 있는 것이 범위 통제다.

### 데모 시나리오 (3분)

1. "오늘 김팀장이랑 또 부딪혔어" → 인물 인식, "김팀장을 기억해둘까요?"
2. 몇 턴 대화 → 인물 카드가 실시간으로 채워진다
3. "다음 주 화요일에 그 사람이랑 회의 있어" → 일정 자동 추출
4. ★ "부장님이 또 그러시더라" → "김팀장님 말씀이신가요? 승진하셨다면 반영할게요"
5. 브리핑: "내일 15시 김부장 회의 — 최근 3회 모두 공개 석상 지적 패턴. 1:1 요청을 제안합니다"

## 기술 스택

| 영역 | 선택 |
|---|---|
| 백엔드 | FastAPI (Python), Docker |
| LLM | Claude API (제품 속 에이전트 · 평가) |
| 임베딩 | OpenAI `text-embedding-3-small`, **1536차원** (파일럿으로 확정 — `reports/embed_pilot.md`) |
| DB | PostgreSQL + pgvector (RDS). 별도 벡터 DB 없이 별칭 테이블과 임베딩을 같은 DB에서 조인 |
| 프론트 | React + PWA (S3 + CloudFront) |
| 인프라 | Terraform, GitHub Actions, SSM Parameter Store, EC2 + Caddy(Let's Encrypt) |

데이터 모델(스키마 v2): `persons`, `person_aliases`(별칭 단위 임베딩), `person_facts`, `fact_sources`, `events`, `schedules`, `pending_questions`, `push_subscriptions`, `agent_traces`. 권위 있는 정의는 `CLAUDE.md`와 `docs/wiki/specs/S3.1-schema-v2.md`.

## 평가

- 한국어 대화 150건 데이터셋(승진·대명사·별칭·정상·신규 인물 케이스)으로 P/R/F1, **오병합률**(핵심), 미검출률, 추출 F1, 툴 호출 정확도, `ask_user` 비율, 보정도를 측정한다.
- 베이스라인 3종과 같은 데이터·같은 지표로 비교하고, `T_merge`를 0.5~0.95로 바꾸며 오병합률·질문율·미검출률 트레이드오프 곡선을 그린다.
- 수치는 재현 가능해야 한다. 성능 미달도 결과이며, 재시도 대신 실패 케이스 분석을 산출물로 남긴다. 산출물은 `reports/`.

## 진행 상태

| 단계 | 내용 | 상태 |
|---|---|---|
| P0 | 임베딩 공급자 파일럿 (D4) | **완료** — small/large 모두 기준 통과, `text-embedding-3-small` N=1536 확정 |
| P0 | 로컬 docker-compose (pgvector) | **완료** — `SELECT '[1,2,3]'::vector` 통과, pgvector 0.8.6 (pg16) |
| P0 | LLM 비용 실측 | 대기 |
| P1 | 스키마 v2 마이그레이션 (Alembic) | **완료** — 9테이블·CHECK 4·FK CASCADE 6·`vector(1536)`·인덱스 10, upgrade/downgrade 왕복·`alembic check` 통과, verifier 04-review 완료 |
| P1 | 파일럿 데이터셋 | **완료** — 40건·5범주(승진 8/별칭 8/대명사 8/일반 10/신규 6), `schema_version` 2, `validate_scenarios --strict` rc=0, 라벨 검수 verifier 40/40·사용자 12/12, verifier 04-review 완료(5cac9bf) |
| P2 | 툴 7종 v2 + FastAPI 골격 | **완료** — 시그니처 = CLAUDE.md(tools_check 7/7), ask_user→pending_questions, D1 확인 강제, GET /health·POST /answers, pytest 206, verifier 04-review 완료 |
| P3 | 엔티티 해석 4단계 · 베이스라인 | **ER 완료(verifier 04-review 완료) · 베이스라인 3종 완료(verifier 04-review 완료)** — ER 4단계(app/er) + 확신도 3신호·두 임계치 + trace 1행, 회귀 3종 통과(승진 0.863 merge / 이모 배제 / 동명이인 0.575 identity), 판정기 공급자 중립(Claude·OpenAI·Gemini, `LLM_PROVIDER`·등록표 `JUDGES`·활성 스위치 `LLM_PROVIDERS_ENABLED`, D11). 베이스라인은 `evaluation/` 다섯 방식(`proposed`·`exact_raw`·`exact_norm`·`embedding_only`·`llm_single`)이 같은 함수·같은 인자로 호출 가능(parity 46건, 부수효과 0), pytest 917 |
| P4 | **파일럿 평가(게이트)** — 여기서 임계치·보정표 확정 | **실 실행 완료 · 게이트 미달**(2026-09-22, openai gpt-4o-mini-2024-07-18 + text-embedding-3-small, 40건·7050행, $0.027) — `T_merge` 0.8 에서 제안 방식 오병합 1/132·미검출 1/132·ask_user(identity) 59.8% vs `embedding_only` 0·1·23.5% → 지배됨(D10 방향은 통과). 원칙8 대로 재실행하지 않고 `reports/failure_cases.md`(원인: 2단계 규칙 필터 배제 6건 + 4단계 미측정 `s_rule`=0 합산으로 확신도 상한 0.80)를 남겼다. verifier 04-review 는 **부분완료**로 닫고 `/devlog change`(CR-001)로 넘어갔다 — 아래 P4b 행이 그 재도전이다. |
| P4b | **게이트 재도전(CR-001)** — 확신도 결합·규칙 필터 재설계 후 1회 재실행 | **완료 · 게이트 통과**(2026-09-23). D12 관측 신호 재정규화(미측정 `s_rule` 은 0 으로 합산하지 않고 분모에서 뺀다)와 D13 규칙 필터 감점(관계 태그·위계 충돌은 후보를 빼지 않고 `penalized_by` 로 감점, 배제는 호칭 사전 모순일 때만)을 넣고 같은 40건을 **한 번만** 다시 돌렸다. `T_merge` 0.8 에서 제안 방식 오병합 **0/132**·미검출 **0/132**, 베이스라인 4종 모두 제안 방식을 지배하지 못한다(`0.8 [] True True`). F1 0.8972(정밀도 1.0·재현율 0.8136), 되묻기 31건 23.5%, $0.0274. 판정식은 고치지 않았다. **한계**: 40건·1회 실행이고 실행 간 `s_llm` 자기보고가 136 mention 중 60건 달라 개선을 D12·D13 단독 효과로 분해할 수 없다. 전후 비교는 `reports/failure_cases.md` §13 |
| P5~P9 | 에이전트 루프 · 메모리 · 브리핑 · 푸시 · 프론트 · 인프라 | P4b 게이트 통과(2026-09-23) 후 착수 가능 |

최신 상태는 `docs/wiki/HANDOFF.md`(지금 어디, 다음 무엇)와 `docs/wiki/journal.md`(시간순)에 있다.

## 저장소 구조

```
CLAUDE.md                 프로젝트 규칙 — 불변 원칙 9개, 툴 시그니처 v2, 스키마 v2, 개발 프로세스
docs/proposal.md          기획서 원본 (본문 불변)
docs/proposal-review.md   기획서 검증 20항목
docs/resolution-plan.md   결정 D1~D10 · 설계 명세 S3.1~S3.7 · 구현 순서 P0~P11
docs/backlog.md           작업 목록 (수용 기준의 권위)
docs/wiki/                개발 위키: 검증(R)→결정(D)→명세(S)→패키지(P) 카드, 교훈(L), HANDOFF·journal·registry
scripts/                  결정용 스크립트 (embed_pilot.py — 임베딩 파일럿)
tests/                    단위 테스트
reports/                  평가·파일럿 산출물 (embed_pilot.md, 이후 eval.md · metrics.json · calibration.json)
.claude/                  개발 하네스: 에이전트 4종, 스킬, 훅, 검증 스크립트
```

## 개발 방식 — 코딩 에이전트 하네스

이 저장소는 Claude Code로 개발하며, 에이전트가 기획서 의도에서 벗어나지 않도록 절차를 훅으로 강제한다.

- **계획 → 기계 검증 → 승인 → 구현 → 증거 검증 → 승인 커밋**. 제품 코드는 활성 패키지가 등록된 뒤에만 쓸 수 있다.
- **역할별 모델 분리**: 계획(architect, opus) · 구현(backend-agent, sonnet) · 평가 데이터(eval-agent, opus) · 검증(verifier, fable). 같은 컨텍스트·같은 모델이 자기 결과를 평가하지 않는다.
- **검증은 증거로만**: 스크립트 출력 파일, 테스트 출력, 커밋 해시만 증거다. "확인했습니다"는 검증이 아니다.
- **브랜치**: 작업·푸시는 `dev`, 배포는 `main`. dev를 실서버에서 확인한 뒤에만 승격하고, 그 결정 전에는 다음 작업을 시작하지 않는다.
- **보안**: `.env`·키 파일은 에이전트가 읽지도 쓰지도 않는다. 강제 푸시·이력 파괴·재귀 삭제·외부 전송은 훅이 막는다.

자세한 규칙은 `CLAUDE.md`, 절차는 `.claude/skills/devlog`·`.claude/skills/commit`, 교훈은 `docs/wiki/lessons/`.

## 로컬에서 해 보기

```bash
# 1. 환경변수 — 키 이름만 적힌 .env.example 을 복사해 값을 채운다 (.env 는 git 제외)
cp .env.example .env

# 2. 의존성 (Python 3.13)
pip install openai numpy python-dotenv pytest

# 3. 단위 테스트 (네트워크 불필요)
python -m pytest -q tests/

# 4. 임베딩 파일럿 재현 (OPENAI_API_KEY 필요, 호칭 30개 × 모델 2개 ≈ 240 토큰)
python scripts/embed_pilot.py
```

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

사전 조건: 로컬 DB가 기동 중(위 절)이고 `pip install -r requirements-dev.txt`로 SQLAlchemy·Alembic·psycopg·pgvector·pytest가 설치되어 있다. `alembic.ini`의 `sqlalchemy.url`은 비어 있다 — `alembic/env.py`가 `app.config`를 통해 환경변수에서 접속 정보를 읽는다(`.env`는 읽지 않는다).

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

| 상태 코드 | 의미 |
|---|---|
| 200 | 정상 저장 — `{"question_id": 1, "status": "answered"}` |
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

알려진 한계(P4·P10으로 넘긴다 — 성능에 유리하게 감추지 않는다):

- `occurred_at_kind: absolute` **0건** — 미래 약속 발화를 원문대로 되돌리면서 유일한 사례가 사라졌다. P10에서 과거 절대 날짜 발화를 보충해야 absolute 분모가 생긴다.
- 이벤트 type 편중: 전체 76건 중 `personal_share` 25 · `meal` 17 · `meeting` 12 · `favor` 10 · `conflict` 6 · `other` 5 · `praise` 1. `favor` 10건 중 사용자→인물 방향은 1건뿐이다.
- 위계 `하` 6/60, 발화 길이 10~26자, 턴 수 3~5로 폭이 좁다 — 실사용보다 쉬운 방향, 즉 **과대평가 편향**이다.
- 같은 가상 성명이 시나리오마다 다른 관계로 다시 등장한다. **P4 러너는 시나리오 사이에 DB를 비워야 한다** — 비우지 않으면 사전 상태가 오염돼 베이스라인 비교의 동일 조건이 깨진다.
- 소비자(P3-baselines·P4-pilot-eval)가 mention 단위 정보(함정 대상, 지칭별 기대 질문, 발화 안 위치, 선행사 턴 등)를 더 요구하면 FIX가 아니라 `schema_version`을 올린다.

### 베이스라인 3종 실행법

`evaluation/`은 **평가 장치**다 — 제품 런타임(`app/`)이 아니고, 의존 방향은 `evaluation → app` 한쪽뿐이다(제품 코드는 이 패키지를 import 하지 않는다). 여기 있는 것은 "엔티티 해석을 LLM 한 번으로 하지 않는다"(불변 원칙 4)를 **숫자로 반박당할 수 있게** 만드는 대비군이다: 같은 사전 상태·같은 지칭·같은 `ERConfig`로 네(등록 이름으로는 다섯) 방식을 돌려 S3.7이 요구하는 동일 데이터·동일 지표 비교를 성립시킨다.

| 등록 이름 | 정의 | 임베딩 / LLM 호출 | 모듈 |
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

### 파일럿 평가 실행법 (P4)

`scripts/run_pilot_eval.py` 하나가 사슬 전체를 돈다 — runner(40 시나리오 × 5방식 × `T_merge` 10점 → 원시 JSONL) → metrics → calibration → curve → validate → report. 임계치 10점은 같은 LLM 응답을 재사용하므로 LLM 호출은 mention 당 방식별 1회다(`proposed`·`llm_single` 만 LLM 을 부른다).

```bash
# 1) 비용 추정만 (네트워크·DB 0, 키 불필요)
PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --dry-run --stub --estimate-only

# 2) 사슬 전체를 스텁으로 (네트워크 0, DB 필요) — 산출물은 임시 디렉터리에
POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --dry-run --stub --out <tmp>

# 3) 실 실행 (키를 실은 셸에서 한 번만 — 절차는 docs/user-setup/10-pilot-eval-run.md)
POSTGRES_PORT=5433 PYTHONIOENCODING=utf-8 python scripts/run_pilot_eval.py --out reports/pilot --commit "$(git rev-parse HEAD)" --max-cost-usd 5

# 4) 커밋된 원시 파일 하나로 지표 재계산 (원칙8) / trace 확신도 재계산
PYTHONUTF8=1 python -m evaluation.metrics --rows reports/pilot/raw-<ts>.jsonl.gz --out <tmp>/metrics.json
python scripts/run_pilot_eval.py --recheck-traces reports/pilot/traces-<ts>.jsonl
```

환경변수는 **이름**만 적는다: `OPENAI_API_KEY`(필수 — 판정과 임베딩 `text-embedding-3-small` 이 같은 키), `OPENAI_MODEL`(선택, 기본 `gpt-4o-mini`), `POSTGRES_PORT`(로컬 컨테이너 5433). `.env` 는 스크립트가 읽지 않으며 키가 없으면 rc=2 로 이름만 안내한다. `DATABASE_URL` 이 환경에 있으면 `POSTGRES_PORT` 보다 우선하므로 포트가 어긋나면 그쪽을 맞춘다(`app/config.py`). Windows 에서 JSON 을 읽는 한 줄 명령은 `PYTHONUTF8=1` 을 앞에 둔다.

산출물: `reports/pilot/raw-<ts>.jsonl.gz`(원시 판정, 결정적 gzip — 평문은 커밋하지 않는다) · `reports/pilot/traces-<ts>.jsonl`(er_resolve trace 전량) · `reports/metrics.json`(`gate` 포함) · `reports/calibration.json` · `reports/curve.csv` · `reports/eval.md`(멱등) · `reports/cost_estimate.md`(실측 토큰·150건 외삽) · `reports/failure_cases.md`(미달 시 실패 케이스 분석). 게이트 판정은 `metrics.json.gate`(결정 K: `T_merge` 0.8 에서 어떤 베이스라인도 제안 방식을 지배하지 않고 곡선이 D10 방향) 한 곳에서만 내리고, 미달이면 같은 설정으로 다시 돌리지 않는다.

**P4b 재실행(2026-09-22, 같은 명령·같은 40건)** — 위 P4 문단은 첫 실행 기준선이고 고치지 않는다. 그 실행이 게이트에 미달해(`embedding_only` 가 제안 방식을 지배) CR-001 로 확신도 결합과 규칙 필터를 바꾼 뒤 **한 번만** 다시 돌렸다. 바뀐 것은 둘이다 — **D12 관측 신호 재정규화**: `s_rule` 이 미측정(`rule_checked == 0`)이면 0 으로 합산하지 않고 분모에서 빼 `(0.5·s_llm + 0.3·s_emb)/0.8` 로 계산한다(세 신호가 다 있으면 예전 식과 같은 값). **D13 규칙 필터 감점**: 관계 태그·위계 충돌은 후보를 목록에서 빼지 않고 `penalized_by` 로 감점만 하며, 배제는 호칭 사전 모순일 때만 한다. 감점 후보가 자동 연결 구간에 들어오면 `ER_PENALIZED_MERGE_POLICY=ask`(기본) 가 되묻기로 강등한다. 재실행 stamp 는 `reports/pilot/raw-20260922-150931.jsonl.gz`·`traces-20260922-150931.jsonl` 이고, `reports/` 최상위 4파일(`metrics.json`·`calibration.json`·`curve.csv`·`eval.md`)이 그 결과로 갱신됐다 — 첫 실행 결과는 `reports/pilot/<이름>-20260922-042440.*` 사본으로 그대로 남아 있다. 게이트 결과 한 줄: `gate` 의 `t_merge dominated_by d10_direction pass` 가 **`0.8 [] True True`**(첫 실행은 `0.8 ['embedding_only'] True False`). 전후 비교는 `reports/failure_cases.md` §13, 판정식은 그대로다(우리가 미달한 뒤 기준을 고치지 않았다).

## 문서 안내

| 알고 싶은 것 | 보는 곳 |
|---|---|
| 왜 이렇게 설계했나 | `docs/wiki/decisions/D01~D10` |
| 스키마·툴·해석 파이프라인·평가 명세 | `docs/wiki/specs/S3.1~S3.7` |
| 기획서에서 무엇이 바뀌었나 | `docs/proposal.md` 상단 안내문, `docs/wiki/review-index.md` |
| 실서버에 올린 뒤 무엇을 점검하나 | `SERVER-CHECKLIST.md` (dev → 실서버 검증 → main 승격의 "검증" 기준·증거 규약·되돌리기) |
| 지금 어디까지 왔나 | `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md` |
| **사용자가 직접 해야 하는 것**(API 키·AWS Budgets·실호출 스모크·로컬 DB·배포 비밀·승인 결정) | `docs/user-setup/README.md` 색인 → 카드 01~07 |
| 무엇이 이미 만들어져 있나 | `docs/wiki/registry.md` |
| 평가 데이터셋은 어디에 | `data/scenarios/` (검증기 `scripts/validate_scenarios.py`, 라벨 규칙은 `data/scenarios/schema.json`의 description) |
