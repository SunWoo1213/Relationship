# 실행 가이드

README에서 옮겨 온 로컬 실행 · 평가 재현 절차입니다. 요약은 [README 8절](../README.md#8-실행-방법)에 있습니다.

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

**P4b 재실행(같은 명령·같은 40건)** — 위 P4 문단은 첫 실행 기준선이고 고치지 않는다. 그 실행이 게이트에 미달해(`embedding_only` 가 제안 방식을 지배) CR-001 로 확신도 결합과 규칙 필터를 바꾼 뒤 **한 번만** 다시 돌렸다. 바뀐 것은 둘이다 — **D12 관측 신호 재정규화**: `s_rule` 이 미측정(`rule_checked == 0`)이면 0 으로 합산하지 않고 분모에서 빼 `(0.5·s_llm + 0.3·s_emb)/0.8` 로 계산한다(세 신호가 다 있으면 예전 식과 같은 값). **D13 규칙 필터 감점**: 관계 태그·위계 충돌은 후보를 목록에서 빼지 않고 `penalized_by` 로 감점만 하며, 배제는 호칭 사전 모순일 때만 한다. 감점 후보가 자동 연결 구간에 들어오면 `ER_PENALIZED_MERGE_POLICY=ask`(기본) 가 되묻기로 강등한다. 재실행 stamp 는 `reports/pilot/raw-20260922-150931.jsonl.gz`·`traces-20260922-150931.jsonl` 이고, `reports/` 최상위 4파일(`metrics.json`·`calibration.json`·`curve.csv`·`eval.md`)이 그 결과로 갱신됐다 — 첫 실행 결과는 `reports/pilot/<이름>-20260922-042440.*` 사본으로 그대로 남아 있다. 게이트 결과 한 줄: `gate` 의 `t_merge dominated_by d10_direction pass` 가 **`0.8 [] True True`**(첫 실행은 `0.8 ['embedding_only'] True False`). 전후 비교는 `reports/failure_cases.md` §13, 판정식은 그대로다(우리가 미달한 뒤 기준을 고치지 않았다).
