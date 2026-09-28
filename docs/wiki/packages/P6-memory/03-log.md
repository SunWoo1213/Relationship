# P6-memory · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-28 14:55 · docs(P6-memory): 4차 확인 통과·계획 승인 — 패키지 착수 · pending
- 변경: 01-plan(architect 초안 + 1차 개정 + 메인 세션 승인 전 변경: `MEMORY_PROMOTE_MIN_EVENTS` 설정값·25행 표기), 02-plan-verify(verifier 1차 보류 → 2차 통과 → 3차 보류 H-4 → 4차 통과, 승인 줄), 05-remediation(소견 6 해소, 열림 0), evidence 기계 검증·사실 확인 출력, S3.5 한 구절(R-12), backlog P8 새 항목(앱 안 사용자별 메모리 설정 — CR 필요). CURRENT active: P6-memory.
- 이유(기획서·카드 연결): devlog start 7~8단계. S3.5·D14(CR-002)·R8·R11 을 구현할 계획. 사용자 결정 A~G 권장안(B 방법 2), 정리 기준 기본 5 유지·설정값화(S3.5 와 충돌 없음 — verifier 3차 ①).
- 정합성 확인: 원칙 5·6·7·8·9 / D14 D11 D6 / S3.5 S3.1 S3.2 / 보안 §1·§5 — 위반 없음(코드 변경 없음). verify-plan 4b FAIL 0 / WARN 0.
- 남은 것 · 다음 단위: U1(backend-agent, L-004 승인). 이월 F-bbf7fa 3단계(U1), R-10(U6), R-15(U5).
- Refs: P6-memory R8 R11 D14 S3.5 CR-002 L-002 L-004

## 2026-09-28 23:45 · feat(P6-memory): U1 메모리 설정 상수·타입 골격 · pending
- 변경:
  - 만든 파일: `app/memory/__init__.py`(재export 전용, U2~U6 진입점 미import), `app/memory/types.py`(`PatternChange`·`PatternResult`·`ExtractedFact`·`Extraction`·`PromotedFact`·`RejectedFact`·`PromotionResult` 데이터클래스, trace 어휘 `MEMORY_TRACE_TOOL_NAME`/`STEP_MEMORY_PATTERN`/`STEP_MEMORY_PROMOTE`/`STEP_MEMORY_ERROR`/`MEMORY_TRACE_STEPS`, `FACT_KEYS` 9종), `tests/test_memory_patterns.py`(`-k constants` 로만 걸리는 23개 테스트, 패턴 로직 테스트는 U2 몫이라 비움).
  - 고친 파일: `app/settings.py`(`PatternConfig` NamedTuple, `PATTERN_WINDOW_DAYS=365`·`PATTERN_MIN_COUNT=3`·`MEMORY_PROMOTE_MIN_EVENTS=5`·`PATTERN_KEY_PREFIX="pattern:"`·`MEMORY_PROMOTE_MAX_EVENTS=20`·`MEMORY_MAX_FACTS=8`, 읽기 함수 `pattern_config(env=None)`·`promote_min_events(env=None)`, 공용 헬퍼 `_read_positive_int()`), `.env.example`(`PATTERN_WINDOW_DAYS=`·`PATTERN_MIN_COUNT=`·`MEMORY_PROMOTE_MIN_EVENTS=` 세 줄, 값은 비움 — security §1).
  - 고른 상수 값과 근거: `PATTERN_WINDOW_DAYS=365`·`PATTERN_MIN_COUNT=3`(D14/CR-002 그대로), `MEMORY_PROMOTE_MIN_EVENTS=5`(S3.5·2026-09-28 사용자 결정 그대로), `PATTERN_KEY_PREFIX="pattern:"`·`MEMORY_PROMOTE_MAX_EVENTS=20`·`MEMORY_MAX_FACTS=8`(01-plan 결정 D-4·D-7 에 이미 적힌 값 그대로 옮김 — 새로 고른 값 없음). `DEFAULT_FACT_CONFIDENCE`(결정 D-8, 값 1.0)는 P2-tools U4 가 이미 `app/settings.py` 에 만들어 두었고 값도 D-8 권장안(1.0)과 같아 U1 에서 다시 추가하지 않음(중복 금지, registry 재사용).
  - `_read_positive_int()` 규칙: `int(raw)` 변환 실패(빈 문자열 제외) 또는 `value <= 0` 이면 `InvalidValue`. `"3.5"` 는 `int("3.5")` 자체가 `ValueError` 를 내므로 별도 분기 없이 자연스럽게 거부된다(`_read_float`/`_read_choice` 와 같은 관례 — 조용한 기본값 복귀 없음).
  - `pattern_config()` 반환 타입: 01-plan 이 "기간·횟수를 함께 돌려준다"고만 적고 구체 타입을 정하지 않아, `app/er/types.py` 의 `ERConfig`(dataclass) 방식 대신 더 가벼운 `typing.NamedTuple`(`PatternConfig(window_days, min_count)`)을 골랐다 — `pattern_config()` 는 검증 로직이 없는 순수 값 묶음이라 `ERConfig` 급의 `__post_init__` 검증(가중치 합 등)이 필요 없다. `app.settings` 안에 정의해 `app.memory.types` 가 `app.settings` 를 import 하지 않게 했다(패턴 판정에 LLM/설정 계층 순환을 만들지 않기 위함, 원칙6 격리와는 무관하지만 계층 방향을 U2 규약과 맞춤 — `app/memory/patterns.py` 가 `app.settings.pattern_config()` 를 호출하는 방향).
  - `app/memory/types.py` 의 결과 데이터클래스(`PatternResult`/`PromotionResult`/`ExtractedFact`/`Extraction` 등) 필드: 01-plan 이 필드를 명시하지 않아, 결정 F(trace output 모양)를 그대로 옮겨 설계했다 — `PatternResult`/`PromotionResult` 는 각각 `memory_pattern`/`memory_promote` trace output 스키마와 1:1로 대응한다. U2·U5 구현 때 실제로 채우며 필드가 부족하면 그 단위 03-log 에 변경을 남긴다(이 로그가 "판단이 갈렸던 지점"을 남기는 자리).
  - `FACT_KEYS` 9종은 01-plan 결정 D-5 초안 어휘(`job`/`workplace`/`family`/`hobby`/`likes`/`dislikes`/`health`/`life_event`/`contact_note`)를 글자 그대로 옮김 — 새로 고른 키 없음.
- 이유(기획서·카드 연결): D14(CR-002)가 "반복 패턴의 기간·횟수는 설정값(기본 365일·3회)"으로 정했고 S3.5 가 승격 트리거를 5건으로 적었다. 그 숫자를 코드가 한 자리에서 읽고 환경변수로 덮을 수 있게 만든다. 또 U2~U6 이 공유할 결과 타입·trace 어휘(`memory_pattern`·`memory_promote`·`memory_error`, 원칙9)와 사실 키 어휘 `FACT_KEYS`(결정 D-5)를 먼저 고정해 단위마다 어휘가 갈리지 않게 한다. 이 단위에는 도는 로직이 없다.
- 정합성 확인: 원칙 6(패턴 판정은 규칙 — `app/memory/` 에 LLM·임베딩·DB import 0건) · 원칙 7(제외 범위 침범 없음) · 원칙 9(trace 어휘를 상수로 고정) / D14 D11 / S3.1(스키마 무변경) S3.2(툴 시그니처 무변경) S3.5 / 보안 §1(`.env.example` 은 이름·주석만, 값 비움 — 비밀 없음) — 위반 없음.
- 검증(backend-agent 실행 → 메인 세션이 같은 명령을 독립 재실행해 확인):
  - 실행한 명령과 결과: `POSTGRES_PORT=5433 pytest tests/test_memory_patterns.py -k constants -v` → 23 passed. `python -c "import app.memory; print('import ok')"` → `import ok`. `grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example` → 3건(58·59·61행). 회귀 확인: `POSTGRES_PORT=5433 pytest tests/test_settings*.py -q` → 2 passed(기존 `test_settings.py` 2건, 새 테스트는 `test_memory_patterns.py` 로 분리해 그대로 유지).
  - 메인 세션 재확인: 상수 테스트 23 passed · `import app.memory` ok · `.env.example` grep 3건 · **전체 회귀 `POSTGRES_PORT=5433 pytest -q -rs` → 1511 passed, skip 0**(이전 1488 + 새 23). 변경 범위에 `app/agent/`·`app/tools/`·`app/api/`·`alembic/` 없음. 증거 `evidence/20260928-2339-u1-main-recheck.txt`
- 남은 것 · 다음 단위: U2 패턴 감지 규칙(`app/memory/patterns.py`, L-004 위임 승인 먼저). `registry.md` 행 추가·`docs/RUNNING.md` 절은 승인된 계획상 U8 몫이라 이 단위에서 하지 않았다. 이월 R-10(U6), R-15(U5).
- 로컬 환경 메모(이 세션에서 처음 겪음, 판단 갈림): 이 작업공간에 파이썬 venv 가 없었고(Docker 데몬도 꺼져 있었음) 새로 `.venv` 를 만들고 `requirements-dev.txt` 를 설치했다(`.venv/` 는 `.gitignore` 에 이미 있음). 또한 `POSTGRES_PORT=5433 docker compose -p capstone2 up -d postgres` 가 쉘의 기본 작업 디렉터리 대소문자 불일치(`/users/...` vs `/Users/...`)로 Docker Desktop 파일 공유 목록에서 거부되어, `pwd -P` 로 대문자 경로를 확정한 뒤에야 컨테이너가 떴다 — 코드·설정 변경 아님, 다음 세션을 위한 메모.
- 증거: `docs/wiki/packages/P6-memory/evidence/20260928-2336-u1-skeleton.txt`
- Refs: P6-memory D14 CR-002 S3.5 S3.1 S3.2 D11 R8 R11 원칙6 원칙9 security§1
