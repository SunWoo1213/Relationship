# P3-llm-providers · 계획 (01-plan)

상태: 초안 | 담당: backend-agent | 작성: 2026-09-11
태그 — 패키지: P3-llm-providers · 닫는 검증: 없음(INDEX 패키지 표 "닫는 R" 열이 `—`. R4 는 P4 가 닫는다) · 기대는 결정: D3 (신설 후보 D11) · 구현하는 명세: S3.3 (LLM 판정 절) · 관련 원칙: 원칙3 원칙4 원칙8 원칙9
의존: **P3-er 완료**(`packages/P3-er/04-review.md` `결과: 완료`·승인 2026-09-06, 닫는 커밋 `0527ab8` — 고칠 대상인 `app/er/judge.py` 가 여기서 나왔다. `b1f2782` 가 `Judge` Protocol·`ClaudeJudge`·`OpenAIJudge`·`judge_from_env()`·`_KNOWN_PROVIDERS` 와 `.env.example` 의 `GEMINI_*` 이름 예약을 만들었다). **P3-baselines 완료**(`packages/P3-baselines/04-review.md` `결과: 완료`·승인 2026-09-11, 닫는 커밋 `5a1bcbe` — 같이 고칠 `evaluation/resolvers/llm_single.py` 의 `caller_from_env()` 와 결정 J 공개 승격 `call_with_error_mapping` 이 `0d98e47` 에서 나왔다). `.claude/gitlog.md`(2026-09-11 12:57) 기준 `dev = 5a1bcbe`, `main(origin) = 0e3447a`, 승격 대기 10, **`P3-llm-providers` 태그 커밋 0건**(미착수 정상). **P4 게이트는 이 패키지에 해당하지 않는다**(게이트는 P5 이후) — 오히려 이 패키지가 P4 착수 **전에** 끝나야 한다(P4 01-plan 5행 의존 줄에 이미 적혀 있다).

## 목표

사용자 요구(2026-09-11): "**LLM 은 Gemini·OpenAI·Claude 모두 사용할 수 있어야 한다. 공급자는 로직에 들어가면 바꿔 끼울 수 있도록 설계하고, 개발자가 원할 때 켜고 끌 수 있어야 한다.**" P3-er 이 이미 공급자 중립 **구조**(핵심 = `Judge` Protocol·`build_prompt()`·`JUDGEMENT_SCHEMA`·`validate_judgement()`·오류 어휘 6종, 공급자별 구현 = "구조화 출력을 받아 dict 로 만드는 부분"만)를 만들어 두었으므로, 이 패키지가 할 일은 셋이다 — (a) `judge_from_env()`·`caller_from_env()` 안에 하드코딩된 `if provider == …` 사다리를 **이름→팩토리 등록표 하나**로 바꿔 공급자 추가가 표에 행 하나 더하는 일이 되게 하고, (b) 개발자가 환경변수로 공급자를 **켜고 끌** 수 있게 하며, (c) 예약만 되어 있던 `gemini` 를 실제로 구현한다(`app/er/judge.py` 460행·`llm_single.py` 502행의 `InvalidValue("… 아직 구현되지 않았다 — google-genai 의존성 추가 필요")` 를 지운다). S3.3 의 3단계("대화 맥락 + 후보 → `{matched_person_id | null, s_llm, reason}` 구조화 출력")와 D3("`s_llm` 은 **어떤 공급자의 API 도 제공하지 않는** 로그확률이 아니라 자기보고 점수")는 공급자에 의존하지 않는 문장이므로, 공급자를 늘려도 명세·결정은 바뀌지 않는다 — 바뀌는 것은 "그 문장을 어느 SDK 로 실행하는가"뿐이다. 이 패키지는 **판정 로직·프롬프트·확신도 결합을 한 줄도 바꾸지 않는다**(원칙8 — 공급자 확장이 성능 변화로 둔갑하면 P4 수치의 해석이 깨진다).

## 범위

- 포함:
  - **공급자 등록표(`app/er/judge.py`)** — `_KNOWN_PROVIDERS` 튜플과 `if/elif` 사다리를 `JUDGES: dict[str, Callable[[], Judge]]` 이름→팩토리 표로 대체한다. 표에 있는 이름 = 지원 공급자 전체이고, `judge_from_env()` 는 `LLM_PROVIDER` 로 표를 조회할 뿐 공급자 이름을 본문에 쓰지 않는다(P3-baselines U1 `RESOLVERS` 와 같은 꼴 — 새 패턴을 발명하지 않는다).
  - **활성 스위치** — `LLM_PROVIDERS_ENABLED`(결정 1) 로 표의 부분집합만 사용 가능하게 한다. 꺼진 공급자를 `LLM_PROVIDER` 로 고르면 **팩토리 호출 시점에 즉시** `InvalidValue("LLM_PROVIDER='gemini' 는 LLM_PROVIDERS_ENABLED 에 없다 (활성: anthropic, openai)")` 로 거절한다 — 판정 중간(`judge()` 호출 시점)에 죽지 않는다. 미지 이름은 지금처럼 `InvalidValue`(메시지에 표의 키 목록).
  - **`GeminiJudge`(`app/er/judge.py`)** — `google-genai` SDK. 구조화 출력은 `response_mime_type="application/json"` + `response_schema`(= `JUDGEMENT_SCHEMA` 와 **같은 스키마 딕셔너리**, SDK 가 요구하는 바깥 모양만 감싼다), `temperature=0`, 타임아웃 `ER_JUDGE_TIMEOUT`, 재시도 `ER_JUDGE_MAX_RETRIES`(=1, 결정3-c). 응답 파싱 후 **같은** `validate_judgement(raw, allowed_ids)` 를 거친다(검증 이중 출처 금지, F-5a97ef). 키는 SDK 가 `GEMINI_API_KEY` 를 환경변수에서 읽게 두고 코드가 변수로 옮기지 않는다(security §1). `Judgement.provider="gemini"`.
  - **오류 어휘 통일** — `JudgeUnavailable.error` 는 기존 6종(`timeout`/`rate_limit`/`api_error`/`connection`/`schema`/`out_of_range_id`) 그대로. Gemini SDK 예외 → 이 어휘 매핑 표는 아래 "Gemini 오류 매핑" 절.
  - **`GeminiSingleCaller`(`evaluation/resolvers/llm_single.py`)** — 베이스라인 3 의 단일 프롬프트 호출부. `RESOLUTION_SCHEMA` 를 같은 방식으로 강제하고, `caller_from_env()` 도 U1 의 **같은 등록표·같은 활성 스위치**를 읽는다(R-4 "제안 방식과 같은 환경변수"를 유지. 표를 두 벌 만들지 않는다 — 중복 구현 금지).
  - **의존성 핀** — `requirements.txt` 에 `google-genai==<설치 버전>`(결정 5). 지연 import 유지 — SDK·키 없이도 `import app.er.judge` 가 깨지지 않아야 한다(현 `ClaudeJudge`·`OpenAIJudge` 와 동일 규약, 테스트가 단언한다).
  - **스텁 테스트** — `tests/test_er_judge.py`(기존 36건에 추가) + `tests/test_baseline_llm_single.py`(기존 69건에 추가), 네트워크 0·실 키 0. 등록표·스위치 전용 단언(활성/비활성/미지 이름, 세 공급자 각각 생성, `FakeJudge` 는 표 밖).
  - **문서** — `.env.example` 주석(이름만), `README.md` 217행 "엔티티 해석(ER) 실행법"·293행 "베이스라인 3종 실행법" 의 환경변수 문단, `docs/user-setup/01-env-keys.md` 표의 `GEMINI_*` 행(현재 "예약값. 미구현"), 03·08 스모크 카드의 `--provider gemini` 경로(결정 7), D 카드(결정 6), `docs/wiki/registry.md` 행.
- 이 패키지에서 하지 않는 것:
  - **P4 실행·지표·보정표** — P4-pilot-eval. 이 패키지는 `reports/` 아래에 아무것도 만들지 않는다.
  - **공급자·모델 성능 비교 실험**("Gemini 가 더 낫다") — 모델 비교는 P4(공급자별 보정표)·P10 몫이고, 수치는 eval-agent 가 낸다(원칙8 — 구현자가 자기 성능을 재지 않는다).
  - **프롬프트·판정 로직·확신도 결합·임계치 변경** — `build_prompt()`·`JUDGEMENT_SCHEMA`·`validate_judgement()`·`app/er/confidence.py` 는 **읽기만** 한다. 공급자 추가가 기존 두 공급자의 동작을 바꾸면 안 된다(회귀 전건 통과가 조건).
  - **임베딩 공급자 확장**(`EMBEDDING_PROVIDER`) — D4 는 OpenAI 로 시작하기로 확정되어 있고, 이 패키지는 **LLM 판정기**만 다룬다. `app/embedding.py` 무수정.
  - **비동기·스트리밍·배치 API**, 공급자별 캐시·요금 계산 — 범위 밖.
  - **`app/` 의 그 밖 파일 수정** — `app/er/judge.py`·`app/settings.py` 둘뿐. `git diff --name-only -- app/` 로 증명한다.

## 산출물 (파일 경로)

- app/er/judge.py — 등록표(`JUDGES`)·`enabled_providers()`·`judge_from_env()` 재작성, `GeminiJudge` 추가, 모듈 docstring 의 "팩토리" 절 갱신
- app/settings.py — `LLM_PROVIDERS_ENABLED` 기본값 상수(이름은 결정 1), 기존 `LLM_PROVIDER` 주석 갱신
- evaluation/resolvers/llm_single.py — `GeminiSingleCaller` 추가, `caller_from_env()` 가 U1 등록표·스위치 재사용
- requirements.txt — `google-genai==<버전>` 핀 1줄(Refs 주석 포함, 기존 관행)
- tests/test_er_judge.py — 등록표·스위치·`GeminiJudge` 단언 추가(기존 36건 무수정 통과)
- tests/test_baseline_llm_single.py — `GeminiSingleCaller`·`caller_from_env` 단언 추가(기존 69건 무수정 통과)
- .env.example — 4~11행 주석에서 "gemini(미구현, 예약)" 제거, 활성 스위치 이름 추가(값 비움)
- README.md — 217행·293행 두 절의 환경변수 문단
- docs/user-setup/01-env-keys.md — `GEMINI_API_KEY`·`GEMINI_MODEL` 행(예약 → 사용 가능), 활성 스위치 한 줄
- docs/user-setup/03-er-smoke.md · 08-baseline-smoke.md — `--provider gemini` 경로(결정 7. 새 카드 09 를 택하면 `docs/user-setup/09-gemini-smoke.md` + README 색인 행)
- docs/wiki/decisions/D11-llm-provider-registry.md — 결정 6 이 (i) 이면 신설, (ii) 면 `D03-confidence-formula.md` 의 갱신 이력에 "개정 3"
- docs/wiki/registry.md — `app/er/judge.py`(82행)·`llm_single.py`(119행)·`.env.example`(36행) 비고 갱신 + 신규 행 필요 시 추가
- docs/wiki/packages/P3-llm-providers/evidence/ — pytest 출력·`git diff --name-only -- app/`·공급자 3종 생성 확인·스위치 거부 메시지

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

- [ ] U1 **공급자 등록표·활성 스위치**: `app/er/judge.py` 에 `JUDGES`(이름→무인자 팩토리) 표와 `enabled_providers(env)`·`judge_from_env(env=None)` 재작성 — `if provider == "anthropic"` 사다리 제거, 표 조회 + 활성 집합 검사 2단계로. `app/settings.py` 에 활성 목록 기본값 상수(결정 1). `FakeJudge` 는 **표에 넣지 않는다**(테스트 전용 — 환경변수로 실제 판정기를 가짜로 바꿀 수 있으면 원칙8·원칙9 의 근거가 무의미해진다). 오류 메시지에 키 값·프롬프트를 넣지 않는다. `tests/test_er_judge.py` — 세 이름 각각 `judge_from_env` 가 해당 클래스를 만든다(gemini 는 U2 전까지 xfail 대신 **U2 에서 함께 추가**), 꺼진 공급자 `InvalidValue`(메시지에 활성 목록), 미지 이름 `InvalidValue`(메시지에 표 키 목록), 활성 목록 미설정 시 기본값, 공백·대소문자 처리, `FakeJudge` 가 표에 없음, 기존 36건 무수정 통과 / Refs: P3-llm-providers S3.3 D3 원칙8
- [ ] U2 **`GeminiJudge`**: `google-genai` 지연 import, 클라이언트 생성(키 인자 미전달 — SDK 가 `GEMINI_API_KEY` 를 읽는다), `model` 기본값 `os.environ.get("GEMINI_MODEL", <결정 3>)` 을 **생성 시점**에 읽는다(`ClaudeJudge`·`OpenAIJudge` 와 동일 규약), `response_schema` = `JUDGEMENT_SCHEMA`, `temperature=0`, 타임아웃·재시도 1, 응답 텍스트 → `json.loads` 실패 시 `JudgeUnavailable("schema")`, 성공 시 `validate_judgement()` 공유, 토큰은 `usage_metadata` 에서, `provider="gemini"`. SDK 예외 → 어휘 매핑은 아래 표(`call_with_error_mapping` 의 모듈 덕타이핑이 맞지 않으면 **같은 어휘를 쓰는 두 번째 공유 헬퍼**를 두고 기존 함수는 손대지 않는다). `requirements.txt` 핀. `tests/test_er_judge.py` — 스텁 클라이언트로 요청 본문(모델·스키마·temperature 0)·파싱·`out_of_range_id`·오류 4종+`schema`·키 미노출(표식 문자열이 요청·예외·출력에 없음)·SDK 없이 모듈 import 가능 / Refs: P3-llm-providers S3.3 D3 원칙4 원칙8 원칙9
- [ ] U3 **`GeminiSingleCaller`**: `evaluation/resolvers/llm_single.py` 에 `RESOLUTION_SCHEMA` 를 같은 방식으로 강제하는 caller 추가. `caller_from_env()` 는 **U1 등록표·활성 스위치를 import 해 재사용**한다(공급자 이름 목록·거부 메시지 규칙을 복제하지 않는다 — 두 진입점이 같은 환경변수를 읽는다는 R-4 를 유지). `app/er/judge.call_with_error_mapping`(또는 U2 의 Gemini 매핑 헬퍼) 재사용 — `llm.error` 어휘가 다섯 방식에 동일해야 한다(결정 J). `tests/test_baseline_llm_single.py` — 스텁으로 요청·파싱·강등 5경로·오류 매핑·키 미노출, `caller_from_env` 가 gemini 를 만들고 꺼진 상태에서는 거부, 기존 69건 무수정 통과 / Refs: P3-llm-providers S3.7 D3 원칙8
- [ ] U4 **문서·evidence**: `.env.example` 주석(이름만), README 두 절, `docs/user-setup/01-env-keys.md` `GEMINI_*` 행·활성 스위치, 03·08(또는 09, 결정 7) 스모크 카드의 `--provider gemini`, D 카드(결정 6), `docs/wiki/registry.md` 행. evidence: 전체 `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs`, P3-er 회귀 `tests/test_er_judge.py tests/test_er_pipeline.py`(54건), parity `tests/test_baseline_parity.py`(46건), `python scripts/tools_check.py` 7/7, `git diff --name-only <U1 직전 해시>..HEAD -- app/` = `app/er/judge.py`·`app/settings.py` 2줄 / Refs: P3-llm-providers 원칙8 원칙9

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [backend-agent] LLM 판정기 공급자 확장 — Gemini 구현 + 공급자 등록표·활성 스위치 / 의존: P3-er, P3-baselines / 수용기준: `LLM_PROVIDER` ∈ {anthropic, openai, gemini} 각각으로 `judge_from_env()`·`caller_from_env()` 가 해당 공급자의 판정기를 만들고, 비활성·미지 공급자는 `InvalidValue` 로 거부하며, 신규 테스트는 네트워크 0(스텁)이고 기존 pytest 전건이 통과한다

  해석(기계 판정 방법, 위 문장을 바꾸지 않는다):
  - "`LLM_PROVIDER` ∈ {anthropic, openai, gemini} 각각으로 … 해당 공급자의 판정기를 만들고" → 세 이름 각각에 대해 `judge_from_env({"LLM_PROVIDER": name, ...})` 가 `ClaudeJudge`/`OpenAIJudge`/`GeminiJudge` 인스턴스를, `caller_from_env(...)` 가 대응 caller 를 돌려준다. **키 없이도 객체 생성까지는 성공**해야 한다(네트워크는 `judge()` 호출 시점에만). 테스트가 세 이름을 parametrize 한다.
  - "비활성·미지 공급자는 `InvalidValue` 로 거부" → 활성 목록에서 뺀 공급자와 표에 없는 이름(`"llama"` 등) 모두 `app.tools.types.InvalidValue`. 거부는 **팩토리 호출 시점**이고 메시지에 사람이 읽을 원인(활성 목록 / 표 키 목록)이 들어간다. 키 값·프롬프트는 메시지에 없다.
  - "신규 테스트는 네트워크 0(스텁)" → 새 테스트는 전부 스텁 클라이언트 주입이고 실 키·실 호출이 없다. `python -m pytest tests/test_er_judge.py tests/test_baseline_llm_single.py -q` 가 키 없는 환경에서 통과하고 skip 0.
  - "기존 pytest 전건이 통과" → `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` 가 **실패 0·skip 0**. 특히 P3-er 회귀 54건·parity 46건이 **무수정**으로 통과한다(공급자 확장이 기존 동작을 바꾸지 않았다는 증거).

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

| 무엇 | 명령 | 기대 출력 |
|------|------|-----------|
| 세 공급자 생성 | `python -m pytest tests/test_er_judge.py -q -k provider` | 세 이름 parametrize 통과, skip 0 |
| 등록표 키 | `python -c "from app.er.judge import JUDGES; print(sorted(JUDGES))"` | `['anthropic', 'gemini', 'openai']` (`fake` 없음) |
| 활성 스위치 거부 | `python -c "import os;os.environ['LLM_PROVIDERS_ENABLED']='anthropic';from app.er.judge import judge_from_env;judge_from_env({'LLM_PROVIDER':'gemini'})"` | `InvalidValue` + 활성 목록이 보이는 메시지(비정상 종료) |
| 미지 이름 거부 | 같은 방식으로 `LLM_PROVIDER=llama` | `InvalidValue` + 표 키 목록 |
| 두 진입점이 같은 표 | `python -c "from app.er import judge; from evaluation.resolvers import llm_single; print(llm_single.CALLERS.keys() == judge.JUDGES.keys())"`(이름은 구현 시 확정) | `True` — 목록이 한 곳에서 온다 |
| SDK·키 없이 import | `python -c "import app.er.judge, evaluation.resolvers.llm_single; print('ok')"` | `ok`(지연 import 유지) |
| P3-er 회귀 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_judge.py tests/test_er_pipeline.py -q` | 기존 54건 + 신규, 실패 0 |
| parity 무변경 | `POSTGRES_PORT=5433 python -m pytest tests/test_baseline_parity.py -q -rs` | 46건 통과, skip 0 |
| 전체 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 전건 통과(현재 859건 + 신규), 실패 0·skip 0 |
| `app/` 수정 범위 | `git diff --name-only <U1 직전 해시>..HEAD -- app/` | 정확히 2줄: `app/er/judge.py`·`app/settings.py` |
| 툴 시그니처 무변경 | `python scripts/tools_check.py` | `7/7 ok` |
| 실 Gemini 1회(키 있을 때만 · **사용자 실행**) | `python scripts/er_smoke.py --provider gemini` · `python scripts/baseline_smoke.py --provider gemini` | `provider`·`model`·`s_llm`·`tokens_*` 출력, 키·프롬프트 원문 미출력. 키 없으면 종료 코드 2 |

- 증거 경로: `docs/wiki/packages/P3-llm-providers/evidence/`. 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security.md §1·§6). 실호출은 자동 테스트에 넣지 않는다(원칙8 — 재현 불가능).

## Gemini 오류 매핑 (U2 에서 확정, 어휘는 기존 6종에서 **늘리지 않는다**)

기존 `call_with_error_mapping(errors_module, fn)` 은 `APITimeoutError`/`RateLimitError`/`APIStatusError`/`APIConnectionError` **네 이름을 가진 모듈**을 받는 덕타이핑이다(anthropic·openai 가 우연히 같은 이름을 쓴다). `google-genai` 는 예외 계층이 다르므로(`google.genai.errors.APIError` 계열 + HTTP 상태 코드) 그대로 꽂히지 않는다. **기존 함수를 고치지 말고**(두 공급자의 동작 변경 = 회귀 위험) 같은 어휘를 반환하는 Gemini 전용 매핑을 둔다.

| 발생 상황 | 어휘(`JudgeUnavailable.error`) |
|-----------|------------------------------|
| 요청 타임아웃(SDK 타임아웃·`TimeoutError`) | `timeout` |
| 429 / 할당량 초과 | `rate_limit` |
| 그 밖 4xx·5xx API 오류 | `api_error` |
| 네트워크 연결 실패·DNS | `connection` |
| 응답이 JSON 아님 · 스키마 위반 · 후보 블록 없음 · 안전 필터로 본문 없음 | `schema` |
| 통과 후보 밖 `matched_person_id` | `out_of_range_id`(`validate_judgement` 가 낸다 — 공유) |

- **U2 착수 시 반드시 실측한다**: `python -c "import google.genai.errors as e; print([n for n in dir(e) if n[0].isupper()])"` 출력을 evidence 로 남기고, 위 표의 왼쪽 열을 설치된 SDK 의 실제 클래스·속성 이름으로 채운다. 문서에서 본 이름을 추측으로 적지 않는다(원칙8).
- 재시도: `ClaudeJudge`/`OpenAIJudge` 는 SDK 의 `max_retries` 에 위임한다(결정3-c "1회만"). `google-genai` 에 동등한 설정이 없으면 판정기 안에 **1회만** 재시도하는 최소 루프를 두되 `timeout`·`connection` 에만 적용하고 그 사실을 docstring 에 적는다. 재시도 횟수를 늘리지 않는다.

## 리스크 · 미결

**사용자 결정이 필요한 항목(결정은 메인 세션·사용자가 한다. U1 착수 전에 필요)**

- **결정 1 — 활성 스위치의 이름과 기본값.** (i) `LLM_PROVIDERS_ENABLED="anthropic,openai,gemini"`, **기본은 표 전체 켬**(**권장** — "개발자가 원할 때 끈다"는 요구의 최소 구현이고, 기본값이 현재 동작과 같아 회귀가 없다. 끄는 것은 명시적 행위다) / (ii) 같은 이름이되 **기본은 키가 있는 공급자만**(편하지만 `os.environ` 의 키 **존재 여부**를 코드가 들여다보게 되고 — security §1 의 "존재 여부만" 은 허용이나 — 환경에 따라 조용히 달라져 P4 재현성이 깨진다, 원칙8) / (iii) 공급자마다 개별 플래그 `LLM_PROVIDER_GEMINI_ENABLED=0`(세밀하지만 이름이 공급자 수만큼 늘고 `.env.example` 이 지저분해진다).
- **결정 2 — 기본 `LLM_PROVIDER`.** (i) **`anthropic` 유지**(**권장** — 기획서 전제가 Claude 이고, 기본값을 바꾸면 `app/settings.py`·`.env.example`·회귀 테스트 기대값이 함께 흔들린다. P4 실 실행은 결정 A 대로 `LLM_PROVIDER=openai` 를 **명시 설정**으로 넘기고 `meta.provider` 에 기록해 증명한다) / (ii) `openai` 로 변경(P4 실행 명령이 짧아지지만 기획서 전제와 어긋나고, 잊고 안 켠 사람이 조용히 OpenAI 를 쓰게 된다) / (iii) 기본값 없애고 미설정 시 오류(가장 명시적이나 기존 테스트·스크립트가 전부 환경변수를 요구하게 되어 변경 폭이 크다).
- **결정 3 — Gemini 기본 모델명(`GEMINI_MODEL` 미설정 시).** (i) 기본값을 **두지 않고** 미설정 시 `InvalidValue`(**권장** — Claude/OpenAI 는 기존 기본값이 있지만, 모델 이름은 공급자 사정으로 자주 바뀌고 잘못된 기본값은 실행 시점에 404 로 드러나 원인 파악이 늦다. 이름을 사용자가 `.env` 에 넣게 하면 `docs/user-setup/01` 카드가 단일 출처가 된다) / (ii) 소형 모델 하나를 기본값으로 박는다(Claude·OpenAI 와 일관되지만 이름을 **추측으로** 코드에 넣게 된다 — 원칙8 과 충돌. 넣는다면 사용자가 콘솔에서 확인한 이름을 받아 적는다) / (iii) 기본값을 두되 `.env.example` 주석에 "콘솔에서 확인해 바꾸라"고 명시.
- **결정 4 — 구조화 출력 실패 시 어휘.** (i) **기존 `schema` 재사용**(**권장** — 어휘를 늘리면 P4 의 `llm.error` 집계 범주가 공급자마다 달라져 비교가 깨진다. 안전 필터로 본문이 비는 Gemini 특유 상황도 "스키마대로 된 판정을 못 받았다"는 점에서 같다) / (ii) `safety_block` 등 신설(원인 분석은 쉬워지나 P3-er·P3-baselines 의 6종 어휘 계약과 P4 집계 표를 바꿔야 한다. 필요하면 `detail`/`reason` 에 부가 정보만 남기는 절충).
- **결정 5 — 의존성 핀.** 이 저장소는 **`requirements.txt` + `requirements-dev.txt`** 를 쓰고 `pyproject.toml` 이 없다(P3-baselines 01-plan 174행이 확인). (i) `requirements.txt` 에 `google-genai==<설치 버전>` 을 기존 관행대로 `# Refs:` 주석과 함께 추가(**권장**) / (ii) 선택 의존성으로 분리(`requirements-optional.txt` 신설 — 설치 안 한 환경에서 gemini 를 끄는 게 자연스러워지지만 파일이 늘고 CI 경로가 갈린다). 어느 쪽이든 **버전은 실제로 설치한 뒤 `pip show` 출력으로 적는다**(추측 금지).
- **결정 6 — D 카드 처리.** (i) **`D11-llm-provider-registry.md` 신설**(**권장** — D03 의 결정 문장은 `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule` 과 "로그확률 미사용"이고 이번 작업이 그 문장을 **바꾸지 않는다**. `decisions/README.md` 규칙은 "결정이 바뀌면 대체" 인데 여기서는 새 결정이 **추가**되는 것이므로 D11 이 맞다. D03 의 **파급** 에 "공급자 선택·활성은 D11" 한 줄 상호참조만 더한다) / (ii) D03 에 "개정 3" 으로 흡수(P3-er 이 `.env.example` 에 `LLM_PROVIDER` 를 넣을 때 쓴 "결정 3 개정 2" 표기와 이어지지만 — 그 "결정 3" 은 **P3-er 패키지 내부 결정 번호**이지 위키 카드 `D3` 가 아니다. 두 번호 체계를 섞으면 `git log --grep 'D3'` 영향 범위 추적이 오염된다) / (iii) 카드 없이 01-plan 에만 기록(추적 태그가 없어 다음 패키지가 근거를 못 찾는다).
- **결정 7 — 실 Gemini 스모크 카드.** (i) **기존 03·08 카드에 `--provider gemini` 한 줄씩 추가**(**권장** — 두 스크립트 모두 이미 `--provider` 인자를 갖고 있어 새 절차가 없다. 카드 수가 늘지 않는다) / (ii) `docs/user-setup/09-gemini-smoke.md` 신설 + README 색인 행(공급자별 절차를 분리해 보기는 좋으나 03·08 과 내용이 90% 겹친다) / (iii) 스모크를 요구하지 않는다(**비권장** — Gemini 는 실호출이 한 번도 없는 상태로 P4 에 들어가고, R4 "실호출 미검증" 꼬리표가 공급자 수만큼 늘어난다).

**결정 확정 (사용자, 2026-09-11 — 메인 세션 기록. 위 선택지 문단은 원문 보존)**

| 결정 | 확정 | 계획에 미치는 것 |
|------|------|------------------|
| 1 활성 스위치 | **(i)** `LLM_PROVIDERS_ENABLED="anthropic,openai,gemini"`, 기본 전체 켬. 끄는 것은 명시적 행위 | U1 — 꺼진 공급자 선택 시 `InvalidValue`(팩토리 호출 시점) |
| 2 기본 `LLM_PROVIDER` | **(ii) `openai` 로 변경**(사용자 결정 — "현재는 OpenAI 로만 실행". 기획서 전제 Claude 와의 차이는 D11 카드 결정 문장·파급에 기록) | U1 `app/settings.py` 기본값 `"openai"`, `.env.example` 6행 `LLM_PROVIDER=openai`, `judge_from_env`·`caller_from_env` 기본 분기 회귀 테스트 기대값 갱신(테스트가 기본값을 단언하면 새 기본으로, `env=` 주입 테스트는 무변경). P4 결정 A 와 정합 |
| 3 Gemini 기본 모델명 | **(i)** 기본값 없음, `GEMINI_MODEL` 미설정 시 `InvalidValue` | U2; `docs/user-setup/01` 이 이름의 단일 출처 |
| 4 구조화 출력 실패 어휘 | **(i)** 기존 `schema` 재사용, 부가 정보는 `detail`/`reason` 에만 | U2 오류 매핑 표 |
| 5 의존성 핀 | **(i)** `requirements.txt` 에 `google-genai==<pip show 실측>` + `# Refs:` 주석 | U2 |
| 6 D 카드 | **(i)** `D11-llm-provider-registry.md` 신설 + D03 파급에 상호참조 1줄. **결정 2(기본 openai)도 D11 에 적는다** | U4 |
| 7 실 Gemini 스모크 | **(i)** 03·08 카드에 `--provider gemini` 한 줄씩(사용자 몫) | U4 |

**리스크(결정이 아니라 지켜볼 것)**

- **SDK 표면 차이가 계획보다 클 수 있다.** `google-genai` 의 구조화 출력은 `response_schema` 가 **pydantic 타입 또는 제한된 JSON Schema 부분집합**만 받을 수 있다. `JUDGEMENT_SCHEMA`(`additionalProperties`·`nullable` 등)가 그대로 안 들어가면 **스키마를 고치지 말고**(세 공급자 공유 자산이다) Gemini 쪽에서 감싸는 변환 함수를 두고, 변환 결과가 원 스키마와 같은 필드·자료형을 요구한다는 것을 테스트로 단언한다. 변환조차 불가능하면 멈추고 사용자 결정으로 올린다.
- **`s_llm` 자기보고 눈금이 공급자마다 다르다**(D3 의 보정 근거에 직접 영향). 같은 후보에 Claude 는 0.9, Gemini 는 0.7 을 줄 수 있으므로 **보정표를 공급자 키로 분리**해야 하는데, P4 01-plan U3 이 이미 "공급자·모델별로 나눈다"로 반영해 두었다 — 이 패키지는 그 전제를 깨지 않게 `Judgement.provider`·`model` 을 반드시 채운다. 임계치 `T_merge` 는 공급자별로 다시 봐야 할 수 있다는 사실을 P4 로 넘긴다.
- **실호출 미검증(R4 의 꼬리표가 늘어난다).** 자동 테스트는 전부 스텁이므로 Gemini 의 실제 응답 모양은 사용자 스모크에서 처음 확인된다. `docs/user-setup/03`·`08` 이 **미실행** 상태(F-87c597 열림)이므로, 이 패키지가 끝나도 세 공급자 중 **실호출로 검증된 것이 0개** 라는 사실을 04-review 에 그대로 적는다(원칙8).
- **기존 두 공급자의 회귀.** 등록표 도입은 `judge_from_env()` 본문을 갈아엎는 변경이다. 안전장치는 "기존 `tests/test_er_judge.py` 36건·parity 46건 **무수정** 통과" 하나뿐이므로, 테스트를 고쳐서 통과시키는 일이 있으면 그 자체를 findings 로 올린다.
- **비용.** 이 패키지는 네트워크 호출 0 으로 끝난다(스텁). 실 비용은 사용자 스모크 2회와 P4 실행에서 발생한다. Gemini 키 발급·무료 티어 한도는 사용자 몫(`docs/user-setup/01`).
- **범위 이탈 유혹.** "공급자를 늘린 김에 모델도 비교해 보자"는 P4·P10 이다. 여기서 수치를 내면 구현자가 자기 성능을 재는 셈이 된다(L-002·원칙8).

**P4-pilot-eval 로 넘기는 것**

1. **의존 줄 갱신** — P4 01-plan 5행에 이미 `P3-llm-providers 완료(추가 의존…)` 가 적혀 있다. 이 패키지 04-review 승인 뒤 **닫는 커밋 해시**를 그 자리에 채운다(architect·메인 세션 몫, 이 패키지는 P4 문서를 고치지 않는다).
2. **`meta.provider` 값 집합** — `metrics.json`·`calibration.json` 의 `meta.provider` 는 `JUDGES` 표의 키(`anthropic`|`openai`|`gemini`)와 `Judgement.provider` 문자열을 그대로 쓴다. 값 집합의 단일 출처는 이 패키지의 등록표이며, P4 판정 명령(`run_mode == "real"`, `provider` 가 `stub`/`fake` 아님)은 그대로 유효하다. `fake` 는 표 밖이므로 등록표 조회로는 절대 나오지 않는다.
3. **결정 A 재확인** — P4 실 실행은 OpenAI 1벌. 이 패키지가 Gemini 를 켜더라도 P4 는 `LLM_PROVIDER=openai` 를 명시 설정으로 넘기고 `meta` 에 기록한다. Gemini 로 한 벌 더 돌릴지는 P4 착수 시 비용·시간을 보고 **사용자가** 정한다(기본은 안 돈다).
4. **공급자별 보정표 그룹 키** — P4 U3 이 이미 `provider`·`model`·`method` 로 나누기로 했으므로 공급자가 셋이 되어도 스키마 변경이 없다.

## 읽은 카드

- `.claude/gitlog.md`(2026-09-11 12:57) — 브랜치(dev 5a1bcbe = origin/dev, main 0e3447a, 승격 대기 10)·최근 커밋 20건(b1f2782 는 20건 밖이라 registry 82행의 커밋 열로 확인, 0d98e47 결정 J 승격 확인, L-001)
- `docs/wiki/INDEX.md` 57~79행 — 패키지 표 형식·"닫는 R" 열·"P4 이전에 P5 이후를 시작하지 않는다"
- `docs/backlog.md` 38~56행 — P3 절 항목 형식·P4 행 원문
- `docs/wiki/decisions/D03-confidence-formula.md` — 전문(결정·보정·파급·갱신 이력 "없음" → 결정 6 의 근거)
- `docs/wiki/decisions/README.md` · `docs/wiki/templates/decision.md` — 카드 규칙(D11 부터 새 번호, 대체 vs 추가)
- `docs/wiki/specs/S3.3-er-pipeline.md` 6~18행 — 4단계 표의 3단계 문장·"LLM 단일 호출로 대체 금지"
- `docs/wiki/security.md` §1 — 비밀 규칙 5행(이름만·`os.environ`·로그 미기록)
- `app/er/judge.py` 1~60행(모듈 docstring 의 공급자 중립 설계·팩토리 절)·178~200행(`call_with_error_mapping` 덕타이핑)·203~235행(`ClaudeJudge` 강제 `tool_use`)·291~332행(`OpenAIJudge` function calling)·380~486행(`FakeJudge`·`_KNOWN_PROVIDERS`·`judge_from_env`)
- `app/settings.py` 75~97행 — `ER_JUDGE_TIMEOUT`·`ER_JUDGE_MAX_RETRIES`·`LLM_PROVIDER`
- `evaluation/resolvers/llm_single.py` 440~511행 — `caller_from_env()` 의 공급자 분기·gemini 예외
- `requirements.txt` 전문 — 핀 관행(`# Refs:` 주석, `openai==2.33.0`·`anthropic==1.4.0`, `google-genai` 없음)
- `.env.example` 1~16행 — LLM 절 주석·`GEMINI_API_KEY`/`GEMINI_MODEL` 예약
- `docs/wiki/registry.md` 36행(.env.example)·82행(judge.py)·90행(test_er_judge.py)·108~124행(evaluation/ 전체·llm_single·baseline_smoke·parity) — 재사용 대상·중복 금지 확인
- `docs/user-setup/README.md` 색인 표(01~08) · `docs/user-setup/01-env-keys.md` 전문 — 키 이름 안내 형식·`GEMINI_*` "예약값. 미구현" 행
- `scripts/er_smoke.py`·`scripts/baseline_smoke.py` — `--provider` 인자·`_REQUIRED_KEY_BY_PROVIDER` 존재 확인(grep)
- `README.md` 217행·293행 — 고칠 두 절의 제목 위치(grep)
- `docs/wiki/packages/P3-baselines/01-plan.md` 전문 — 형식(작업 단위·수용 기준 해석 블록·판정 방법 표·결정 확정 블록), 174행 "현재 저장소에 `pyproject.toml` 이 없다"
- `docs/wiki/packages/P4-pilot-eval/01-plan.md` 1~10행·결정 A(185행)·`meta.provider` 판정(82행)·보정표 그룹 키(22행) — 넘길 것 확인(이 문서는 고치지 않았다)
- `docs/wiki/templates/plan.md` — 이 문서의 형식
- `docs/proposal.md` — 열지 않음(S3.3·D3 카드가 필요한 문장을 담고 있다)
