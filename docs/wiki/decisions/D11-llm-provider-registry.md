# D11 · LLM 판정기 공급자 등록표·활성 스위치, 기본 공급자 openai

상태: 유효 | 해결하는 검증: 없음(R4 실호출 검증은 P4·사용자 스모크가 닫는다) | 출처: 논의(2026-09-11, P4-pilot-eval 결정 A · P3-llm-providers 결정 1·2·6 — 사용자 결정)

**결정**
- LLM 판정기(`app/er/judge.py`)와 베이스라인 3 단일 프롬프트 호출자(`evaluation/resolvers/llm_single.py`)는 **공급자를 바꿔 끼울 수 있어야 한다**: 이름→팩토리 **등록표** 하나(`JUDGES`)에서 `LLM_PROVIDER` 로 고른다. 지원 공급자 = `anthropic` · `openai` · `gemini` 세 가지(Gemini 는 P3-llm-providers 에서 구현).
- 개발자가 **원할 때 켜고 끌 수 있다**: 활성 공급자 목록 환경변수 `LLM_PROVIDERS_ENABLED`(쉼표 구분, 기본값 = 전체 켬 `anthropic,openai,gemini`). 꺼진 공급자나 표에 없는 이름을 고르면 **팩토리 호출 시점에 `InvalidValue`** 로 명확히 거부한다(조용한 대체 금지).
- **기본 `LLM_PROVIDER` 는 `openai`** 다(사용자 결정 2, 2026-09-11 — "현재는 OpenAI 로만 실행"). 기획서 전제(제품은 Claude API)와 다르며, 이는 **운영 기본값의 변경**이지 확신도 공식(D3)·판정 프롬프트·구조화 출력 스키마의 변경이 아니다. P4-pilot-eval 실 실행은 `LLM_PROVIDER=openai` 1벌이며 `meta.provider`·`meta.model` 에 기록한다.
- `FakeJudge`(테스트용)는 등록표 **밖**이다 — 환경변수로 진짜 판정기를 가짜로 바꿀 수 없다.
- Gemini 기본 모델명은 두지 않는다(`GEMINI_MODEL` 미설정 시 `InvalidValue`). 구조화 출력 실패는 기존 오류 어휘 6종(`timeout/rate_limit/api_error/connection/schema/out_of_range_id`)만 쓴다 — 어휘를 늘리지 않는다.

**이유**
- 사용자 요구(2026-09-11): "LLM 은 Gemini·OpenAI·Claude 모두 사용할 수 있어야 하고, 공급자는 로직에 들어가면 바꿔 끼울 수 있도록 설계하며, 개발자가 원할 때 켜고 끌 수 있어야 한다." 현재는 `LLM_PROVIDER` 분기만 있고 Gemini 는 이름만 예약돼 있었다.
- 기본값을 "키가 있는 것만 켬"으로 하면 환경에 따라 조용히 달라져 P4 재현성이 깨진다(원칙8). 전체 켬 + 명시적 끄기가 재현 가능하다.
- 기본 공급자를 openai 로 두면 P4 실행·스모크가 같은 기본을 쓰고, 임베딩(D4, OpenAI)과 키 하나로 돈다. 대신 기획서 전제와의 차이를 이 카드가 드러낸다 — 다른 공급자로 돌린 결과는 `meta.provider` 로 구분한다.
- 등록표를 두 벌(judge / llm_single) 만들지 않는다 — `llm_single` 이 `judge.py` 의 표·스위치를 import 해 재사용해야 "같은 환경변수·같은 모델" 보장(P3-baselines R-4)이 유지된다.

**파급** (갱신할 S 카드 · 영향 P 패키지 · CLAUDE.md 원칙)
- S3.3(LLM 판정 절): 공급자 선택·활성 규칙은 이 카드를 참조. D3(확신도 공식)은 변경 없음 — D3 파급에 상호참조 1줄.
- P3-llm-providers(구현: `app/er/judge.py`·`app/settings.py`·`evaluation/resolvers/llm_single.py`·`requirements.txt`·`.env.example`·문서), P4-pilot-eval(실행 OpenAI 1벌, 보정표는 공급자·모델 키로 분리), P10-final-eval(공급자 비교 축).
- CLAUDE.md 원칙3(자기보고 `s_llm` — 공급자마다 눈금이 다를 수 있으므로 보정표는 공급자 키로 나눈다), 원칙4(제품 코드 수정은 `judge.py`·`settings.py` 2파일로 한정), 원칙8(기본값·모델명 추측 금지), 원칙9(`llm.provider`/`llm.model` trace 기록 유지).
- 기획서(`docs/proposal.md`) 본문은 원본 유지. 상단 안내문 갱신 여부는 P3-llm-providers 04-review 에서 판단(운영 기본값 변경이 기획서 "확정 사항" 에 해당하는지).

**코드에서 지켜야 할 것** (리뷰어가 grep 으로 확인할 수 있는 문장으로)
- `app/er/judge.py` 에 이름→팩토리 표 `JUDGES` 가 하나만 있고 `("anthropic", "openai", "gemini")` 세 키를 갖는다. `FakeJudge` 는 그 표에 없다.
- `judge_from_env()`·`caller_from_env()` 는 `LLM_PROVIDER` 와 `LLM_PROVIDERS_ENABLED` 를 읽고, 미지·비활성 공급자에 `InvalidValue` 를 던진다(메시지에 허용 목록 포함). `caller_from_env()` 는 표·스위치를 `judge.py` 에서 import 한다(자체 표 금지).
- `app/settings.py` `LLM_PROVIDER = "openai"`, `.env.example` `LLM_PROVIDER=openai`. `GEMINI_MODEL` 기본값 없음.
- Gemini 경로의 오류 매핑은 `call_with_error_mapping` 어휘 6종만 쓴다(`grep -n "safety\|blocked" app/er/judge.py` 가 새 어휘를 만들지 않는다).
- 키·프롬프트 원문은 로그·예외·evidence 에 남지 않는다(security §1).

**갱신 이력**
- 2026-09-11 신설 — 사용자 결정(P4 결정 A, P3-llm-providers 결정 1·2·6). 카드는 메인 세션이 기록, 구현은 P3-llm-providers U1~U4.
