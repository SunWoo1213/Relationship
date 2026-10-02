"""Refs: P2-tools S3.2 S3.3 D5 FIX-005 -- 런타임 설정값의 단일 출처.

이 모듈이 `.env` 를 읽지 않는 이유(security.md §1): 비밀·설정은 `os.environ`
으로만 읽는다. `.env` 파일 자체는 존재 확인도 하지 않는다. `APP_USER_ID`
가 없으면 로컬 단일 사용자 기본값 `"local"` 을 쓴다(01-plan 결정 9,
`.env.example` 에 이름만 추가).

`session_id` 기본 생성 helper(대화 세션을 여는 쪽의 책임)는 U2 이후
(`ToolContext`/FastAPI 요청 조립부)에서 만든다 -- 이 모듈은 값 하나만 다룬다.

## SEARCH_TOP_K (U3)

01-plan 산출물 목록이 이 모듈에 명시한 값 중 `search_person`(U3)이 처음
쓰는 것 -- D5/S3.3 "별칭 top-K(K=10) -> 인물별 max". 나머지 설정값
(`QUESTION_TTL_HOURS`·`BRIEFING_RECENT_EVENTS` 등)은 그것을 쓰는 단위가
필요해질 때 같은 방식으로 이 모듈에 추가한다(선반영하지 않는다).

## ER_* (P3-er U4, 결정8)

`ER_T_MERGE`/`ER_T_NEW`/`ER_WEIGHTS`/`ER_TOP_K`/`ER_JUDGE_TIMEOUT`/
`ER_JUDGE_MAX_RETRIES` 는 `ERConfig` 의 **모듈 상수(1층)** 기본값이다.
2층(오버라이드)은 `.env.example` 에 이미 이름이 있는 `T_MERGE`/`T_NEW`/
`W_LLM`/`W_EMB`/`W_RULE` 환경변수이고 `er_config(env)` 가 읽는다. 3층은
`resolve(config=ERConfig(...))` 인자 주입(P4 스윕, `app/er/confidence.py`
호출자 몫)이다. `ER_TOLERANCE` 는 임계치 비교 허용오차의 **단일 출처**다
(F-7fe239 -- `round()` 기반 비교는 `T_merge` 미만 confidence 를 merge 로
판정할 수 있어 원칙1 과 반대 방향이므로 쓰지 않는다. `app/er/confidence.py`
의 `ge_with_tolerance()` 하나만 이 상수를 쓴다).

`er_config()` 는 `ERConfig`(`app.er.types`)를 **함수 안에서** 지연
import 한다 -- `app.er.types` 가 `app.settings.SEARCH_TOP_K` 를 최상위에서
import 하므로, 이 모듈이 최상위에서 `app.er.types` 를 다시 import 하면
순환 import 가 된다.

## APP_TIMEZONE (FIX-005)

DB 는 계속 UTC(`timestamptz`)로 저장한다 -- 이 설정은 "사람이 말한
시각"을 해석하는 자리(인식 프롬프트의 `now`, 일정 후보 생성, LLM 이
오프셋 없이 준 ISO 8601 문자열 보정)에서만 쓰인다. `ctx.now()` 자체와
DB 저장 방식은 이 설정과 무관하다(`app/agent/loop.py`·`app/agent/
propose.py` 의 각 모듈 docstring "사용자 시간대" 절 참고). 기본값
`Asia/Seoul` 은 단일 사용자 전제(`APP_USER_ID` 고정)에 맞춘 설정값
하나다 -- 사용자별 시간대 컬럼은 다중 사용자 격리와 함께 다룰 몫이다.

## PATTERN_* / MEMORY_PROMOTE_* (D14 -- CR-002, S3.5, P6-memory U1)

반복 패턴 감지(D14)·시맨틱 승격(S3.5) 트리거의 설정값 3개는 `er_config()`
의 `_read_float`/`_read_choice` 와 같은 2층 규약(모듈 상수가 기본값,
`.env.example` 이름이 있는 환경변수가 오버라이드, 생략하면 `os.environ`)
을 따르되 값 규칙이 다르다 -- **양의 정수만** 허용하고 0·음수·비정수
문자열(`"abc"`·`"3.5"` 포함)은 `InvalidValue`(`_read_positive_int()`).
`pattern_config()` 가 기간·횟수를 `PatternConfig` 하나로 함께 돌려주는
이유는 `memory_pattern` trace 가 "이번 판정에 실제로 쓴" 두 값을 같이
적어야 하기 때문이다(D14 "코드에서 지켜야 할 것", 원칙8·9) -- 따로
읽으면 호출자가 서로 다른 시점의 환경을 섞어 쓸 위험이 있다.

`PATTERN_KEY_PREFIX`·`MEMORY_PROMOTE_MAX_EVENTS`·`MEMORY_MAX_FACTS` 는
환경변수가 없는 코드 상수다(P6-memory 01-plan 결정 D-4·D-7) -- 값을
바꾸려면 코드를 고쳐야 재현성이 흔들리지 않는다(원칙8).

## BRIEFING_* (S3.6, P6-briefing U1)

브리핑 트리거(S3.6)가 쓰는 설정값 3개(`BRIEFING_LEAD_HOURS`=24·
`BRIEFING_INTERVAL_SECONDS`=60·`BRIEFING_SUGGESTION_MAX_CHARS`=80, 01-plan
결정 B·A·E)는 환경변수로 덮지 않는 **코드 상수**다 -- `PATTERN_KEY_PREFIX`
와 같은 이유(원칙8, 값을 바꾸려면 코드를 고쳐 재현성을 지킨다). 이
셋과 달리 주기 작업을 켜고 끄는 스위치(`BRIEFING_SCHEDULER_ENABLED`)만
환경변수로 읽는다 -- `briefing_scheduler_enabled(env=None)` 가 비우면
`False`(기본 꺼짐, 01-plan 결정 A "기존 테스트가 `TestClient` 로 앱을
띄울 때 매분 루프가 돌면 안 된다"), `"1"`/`"true"` 는 `True`, 그 밖의
값은 `_read_positive_int()` 와 같은 관례로 `InvalidValue`(조용히 꺼진
채로 되돌아가지 않는다 -- 잘못 설정한 줄 모르고 배포하는 것을 막는다).
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import TYPE_CHECKING, NamedTuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if TYPE_CHECKING:  # pragma: no cover -- 순환 import 회피, 타입 힌트 전용.
    from app.er.types import ERConfig

DEFAULT_APP_USER_ID = "local"

#: 사용자 발화의 상대 시각을 해석하는 기준 IANA 시간대 이름(FIX-005).
#: `.env.example` 의 `APP_TIMEZONE` 이 이 값을 오버라이드한다(`user_
#: timezone()`).
DEFAULT_APP_TIMEZONE = "Asia/Seoul"

#: 후보 검색(`search_person`)의 별칭 임베딩 top-K (D5/S3.3).
SEARCH_TOP_K = 10

#: `ask_user`/`question_status`(U6)가 쓰는 미답변 질문 만료 기한(S3.4
#: "미답변 24시간 후 만료"). `datetime` 산술에 바로 쓸 수 있도록 `timedelta`
#: 로 둔다 -- 시간 수 자체가 필요하면 `.total_seconds() / 3600` 대신 이
#: 상수를 그대로 더/빼는 쪽을 쓴다(단일 출처).
QUESTION_TTL_HOURS = 24
QUESTION_TTL = timedelta(hours=QUESTION_TTL_HOURS)

#: `update_person(facts=[{key,value}])` 로 사용자 발화에서 직접 온 사실의
#: 기본 확신도(01-plan 결정 6). 승격(P6-memory)이 만드는 사실의 confidence
#: 는 그 패키지가 별도로 정한다 -- 이 값은 U4 의 애플리케이션 upsert 에만
#: 쓰인다.
DEFAULT_FACT_CONFIDENCE = 1.0

#: `get_briefing`(U7)이 돌려주는 `recent_events`/`upcoming_schedules` 상한
#: (01-plan 결정 7: `recent_events[N=5]`·`upcoming_schedules[3]`).
BRIEFING_RECENT_EVENTS = 5
BRIEFING_UPCOMING_SCHEDULES = 3

#: ER 두 임계치 초기값(D10, 원칙1·2). `.env.example` 의 `T_MERGE`/`T_NEW`
#: 가 이 값을 오버라이드한다(`er_config()`).
ER_T_MERGE = 0.8
ER_T_NEW = 0.3

#: 확신도 3신호 가중치 초기값(D3, 원칙3). `.env.example` 의 `W_LLM`/`W_EMB`/
#: `W_RULE` 이 이 값을 오버라이드한다(`er_config()`). 키 이름은
#: `ERConfig` 필드 이름(`w_llm`/`w_emb`/`w_rule`)과 다르게 짧게 둔다 --
#: 이 dict 는 사람이 읽는 설정 표시용이고 `ERConfig` 생성 인자는
#: `er_config()` 가 직접 키워드로 넘긴다.
ER_WEIGHTS = {"llm": 0.5, "emb": 0.3, "rule": 0.2}

#: 1단계 후보 검색 top-K -- `search_person` 과 같은 값(D5/S3.3, 결정8).
ER_TOP_K = SEARCH_TOP_K

#: 3단계 LLM 판정 타임아웃(초)·재시도 횟수(결정3(c) -- 1회만 재시도).
ER_JUDGE_TIMEOUT = 20.0
ER_JUDGE_MAX_RETRIES = 1

#: 보수 분기 정책 초기값(D13 "코드에서 지켜야 할 것" 3항, P4b-er-redesign
#: 01-plan 결정 B(i)) -- 감점 후보(`ScoredCandidate.penalized_by` 비어
#: 있지 않음)가 `app/er/pipeline.py` 3단계에서 `band == "merge"` 로
#: 귀속되면 `"ask"`(기본)는 `identity` 로 강등하고, `"merge"`는 강등 없이
#: 그대로 연결한다. `.env.example` 의 `ER_PENALIZED_MERGE_POLICY` 환경변수
#: (2층)가 이 값을 오버라이드한다(`er_config()`). 값 어휘는
#: `app.er.types.ERConfig.penalized_merge_policy`(단일 출처)와 같다.
ER_PENALIZED_MERGE_POLICY = "ask"

#: 3단계 LLM 판정 공급자 기본값(D11 결정 2, 2026-09-11 -- 사용자 결정
#: "현재는 OpenAI 로만 실행"). `app/er/judge.py` 의 `select_provider()`/
#: `judge_from_env()` 와 베이스라인 단일 프롬프트 caller 모듈
#: (`llm_single.py`)의 `caller_from_env()` 가 `LLM_PROVIDER` 환경변수를 읽을 때 이 값이
#: 기본이다. 기획서 전제(Claude)와 다른 **운영 기본값**의 변경이며 확신도
#: 공식(D3)·판정 프롬프트를 바꾸지 않는다(D11 참조). `.env.example` 에
#: 값을 그대로 적는다.
LLM_PROVIDER = "openai"

#: `LLM_PROVIDERS_ENABLED`(D11 결정 1) 미설정·공백만일 때의 기본값 --
#: 표(`app.er.judge.JUDGES`) 전체를 켠 상태다. 끄는 것은 명시적 행위여야
#: 재현성이 유지된다(원칙8) -- "키가 있는 것만 켬" 같은 조용한 기본값은
#: 쓰지 않는다. `app/er/judge.py` 는 이 상수를 **import 해서만** 쓰고
#: 같은 목록 리터럴을 다시 쓰지 않는다(R-4 단일 출처).
LLM_PROVIDERS_ENABLED_DEFAULT = "anthropic,openai,gemini"

#: 임계치 비교 허용오차의 단일 출처(F-7fe239). `app/er/confidence.py` 의
#: `ge_with_tolerance()` 하나만 이 상수를 쓴다 -- `round()` 기반 비교는
#: 쓰지 않는다(경계 폭이 넓어 `T_merge` 미만 confidence 를 merge 로
#: 판정할 위험이 있어 원칙1 의 방향과 반대다).
ER_TOLERANCE = 1e-9

#: P5-loop 결정 A(i) -- 게이트(U3)가 LLM 제안 목록에 적용하는 상한 4종.
#: `LOOP_MAX_MENTIONS`/`LOOP_MAX_EVENTS`/`LOOP_MAX_SCHEDULES` 는 초안
#: 값(언급 5·이벤트 5·일정 3)이고, `LOOP_MAX_PROPOSALS`(R-13, 3차 개정)는
#: `update_person`/`create_person` 제안까지 포함한 총 제안 수 상한이다 --
#: 값 13 은 기존 세 상한의 합(5+5+3)에서 파생한 것이고 새 튜닝값이 아니다.
#: 초과분은 `limit` 사유로 거부되고 `stop_reason="limit"` 가 된다
#: (`app.agent.types.GateLimits`/`GateVerdict` 가 담는 모양, U1).
LOOP_MAX_MENTIONS = 5
LOOP_MAX_EVENTS = 5
LOOP_MAX_SCHEDULES = 3
LOOP_MAX_PROPOSALS = LOOP_MAX_MENTIONS + LOOP_MAX_EVENTS + LOOP_MAX_SCHEDULES

#: `pending_questions.context["resume"]`(`app.agent.types.PendingResume`)
#: 직렬화 바이트 상한 -- 결정 A(i) 의 항목 수 상한이 1차 방어, 이것이
#: 이중 안전장치다(01-plan M-0 "크기 통제" 절, 판정 표 24행). 초과 시
#: `held_drafts` 를 버리고 `dropped` 수만 남긴다(`pending_calls` 는
#: 유지) -- 정확한 채움 규칙은 U4/U5(`app/agent/loop.py`)가 정한다. 이
#: 값은 초기 추정치이고 P5-loop U8 파일럿 실행에서 다시 확인한다.
LOOP_MAX_RESUME_BYTES = 8192

#: 브리핑 대상 선정(U2)의 창 상한 -- "`scheduled_at - now() ≤ 24h`"
#: (S3.6, P6-briefing 결정 B(i) 확정: `now ≤ scheduled_at ≤ now + 24h`,
#: 이미 지난 일정은 제외). `.env.example` 에 없는 코드 상수다(모듈
#: docstring "BRIEFING_*" 절).
BRIEFING_LEAD_HOURS = 24

#: 1분 주기 작업(U7)의 실행 간격(초). 코드 상수 -- 테스트는 이 값을
#: 쓰지 않고 짧은 간격을 직접 주입한다(01-plan U7 "실 시간 1분을
#: 기다리지 않는다").
BRIEFING_INTERVAL_SECONDS = 60

#: 브리핑 제안 한 줄의 최대 글자 수(01-plan 결정 E(ii), 원칙7 "한 줄
#: 행동 제안으로 한정"). 검증기(U4)가 이 값을 넘는 제안을 `too_long`
#: 사유로 거부한다. 코드 상수.
BRIEFING_SUGGESTION_MAX_CHARS = 80


class PatternConfig(NamedTuple):
    """`pattern_config()` 반환 타입 -- 판정 창(일)·최소 횟수를 함께
    실어 날라 `memory_pattern` trace(`window_days`·`min_count`, D14)에
    "이번 판정에 실제로 쓴" 값을 그대로 기록할 수 있게 한다(원칙8·9)."""

    window_days: int
    min_count: int


#: 반복 패턴 감지(D14 -- CR-002, 원칙6) 판정 창(일)의 기본값. `.env.example`
#: 의 `PATTERN_WINDOW_DAYS` 가 이 값을 오버라이드한다(`pattern_config()`,
#: P6-memory U1). 1년 = 365일 고정(윤년 무관 -- D14).
PATTERN_WINDOW_DAYS = 365

#: 반복 패턴 감지(D14) 최소 횟수의 기본값. `.env.example` 의
#: `PATTERN_MIN_COUNT` 가 이 값을 오버라이드한다(`pattern_config()`).
PATTERN_MIN_COUNT = 3

#: 시맨틱 승격(S3.5) 트리거 -- 같은 인물의 미승격 이벤트가 이 값 이상이면
#: 승격(LLM 추출기 1회)이 돈다. 기본 5(2026-09-28 사용자 결정, 기본값
#: 불변). `.env.example` 의 `MEMORY_PROMOTE_MIN_EVENTS` 가 이 값을
#: 오버라이드한다(`promote_min_events()`).
MEMORY_PROMOTE_MIN_EVENTS = 5

#: 승격 사실 키의 예약 접두사(P6-memory 01-plan 결정 D-7) -- LLM 제안
#: (루프 `update_person` 직접 사실이든 승격 추출기든)이 이 접두사로
#: 시작하는 키를 만들 수 없다(`app/tools/persons.py` `update_person`,
#: P6-memory U3). 환경변수로 덮지 않는 코드 상수다.
PATTERN_KEY_PREFIX = "pattern:"

#: 한 번 승격에 추출기 입력으로 넣는 이벤트 상한(오래된 순, 01-plan
#: 결정 D-4). 코드 상수 -- 넘는 이벤트는 거부하지 않고 앞에서 자른다
#: (P6-memory U5).
MEMORY_PROMOTE_MAX_EVENTS = 20

#: 한 번 승격에서 반영하는 사실 상한(01-plan 결정 D-4). 코드 상수 --
#: 초과분은 거부하고 사유를 trace 에 남긴다(P6-memory U5).
MEMORY_MAX_FACTS = 8


def _read_positive_int(env: dict[str, str], name: str, default: int) -> int:
    """환경변수 `name` 을 양의 정수로 읽는다(D14 "양의 정수만"). 없거나
    빈 문자열이면 `default`. 0·음수·비정수 문자열(`"abc"`·`"3.5"` 등)은
    `int()` 변환이 그대로 실패하므로 `InvalidValue` 로 다시 던진다(`er_
    config()` 의 `_read_float`/`_read_choice` 와 같은 관례 -- 조용히
    기본값으로 되돌아가지 않는다)."""
    from app.tools.types import InvalidValue  # 지연 import -- 다른 settings 함수와 같은 관례.

    raw = env.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise InvalidValue(
            f"environment variable {name!r} must be a positive integer "
            f"(got {raw!r})"
        ) from exc
    if value <= 0:
        raise InvalidValue(
            f"environment variable {name!r} must be a positive integer "
            f"(got {raw!r})"
        )
    return value


def pattern_config(env: dict[str, str] | None = None) -> PatternConfig:
    """`.env.example` 의 `PATTERN_WINDOW_DAYS`/`PATTERN_MIN_COUNT` 를 읽어
    `PatternConfig` 로 함께 돌려준다(D14/CR-002, P6-memory U1). 기간·횟수를
    하나로 묶어 돌려주는 이유는 모듈 docstring "PATTERN_* /
    MEMORY_PROMOTE_*" 절을 본다.

    `env` 를 생략하면 `os.environ` 을 읽는다(`app_user_id()`/`er_config()`
    와 같은 규약). `.env` 파일 자체는 읽지 않는다(security.md §1).
    """
    if env is None:
        env = dict(os.environ)
    return PatternConfig(
        window_days=_read_positive_int(env, "PATTERN_WINDOW_DAYS", PATTERN_WINDOW_DAYS),
        min_count=_read_positive_int(env, "PATTERN_MIN_COUNT", PATTERN_MIN_COUNT),
    )


def promote_min_events(env: dict[str, str] | None = None) -> int:
    """`MEMORY_PROMOTE_MIN_EVENTS` 환경변수를 읽는다(S3.5, 기본 5). `env`
    규약은 `pattern_config()` 와 같다."""
    if env is None:
        env = dict(os.environ)
    return _read_positive_int(env, "MEMORY_PROMOTE_MIN_EVENTS", MEMORY_PROMOTE_MIN_EVENTS)


def briefing_scheduler_enabled(env: dict[str, str] | None = None) -> bool:
    """`BRIEFING_SCHEDULER_ENABLED` 환경변수를 읽는다(S3.6, P6-briefing
    01-plan 결정 A(i)). 비었거나 없으면 `False`(기본 꺼짐 -- 기존
    `TestClient` 테스트가 앱을 띄울 때 실제 DB 를 매분 훑는 루프가
    돌면 안 된다). `"1"` 또는 `"true"` 만 `True` 다. 그 밖의 값은
    조용히 꺼진 채로 되돌아가지 않고 `InvalidValue` 로 사람이 읽는
    오류를 낸다(`pattern_config()`/`er_config()` 와 같은 관례 -- 잘못
    설정한 줄 모르고 배포하는 것을 막는다, 원칙8).

    `env` 를 생략하면 `os.environ` 을 읽는다(`app_user_id()`/
    `pattern_config()` 와 같은 규약). `.env` 파일 자체는 읽지 않는다
    (security.md §1).
    """
    from app.tools.types import InvalidValue  # 지연 import -- 다른 settings 함수와 같은 관례.

    if env is None:
        env = dict(os.environ)
    raw = env.get("BRIEFING_SCHEDULER_ENABLED")
    if raw is None or raw == "":
        return False
    if raw in ("1", "true"):
        return True
    raise InvalidValue(
        "environment variable 'BRIEFING_SCHEDULER_ENABLED' must be '1' or "
        f"'true' to enable, or empty to disable (got {raw!r})"
    )


def er_config(env: dict[str, str] | None = None) -> "ERConfig":
    """`.env.example` 이 이름을 정한 `T_MERGE`/`T_NEW`/`W_LLM`/`W_EMB`/
    `W_RULE`/`ER_PENALIZED_MERGE_POLICY`(D13, U3) 환경변수를 읽어
    `ERConfig` 를 만든다(결정8 2층). 이름을 새로 만들지 않는다 --
    `app.tools.types.InvalidValue` 는 `ERConfig` 생성 자체(가중치 합·
    임계치 순서·`penalized_merge_policy` 어휘 검증)에서 던져지고, 이
    함수는 **문자열 파싱 실패**(`float` 변환 실패·허용 어휘 밖 값)에도
    같은 예외를 사람이 읽는 메시지로 던진다.

    `env` 를 생략하면 `os.environ` 을 읽는다(`app_user_id()` 와 같은 규약).
    `.env` 파일 자체는 읽지 않는다(security.md §1).
    """
    from app.er.types import ERConfig  # 지연 import -- 순환 import 회피.
    from app.tools.types import InvalidValue

    if env is None:
        env = dict(os.environ)

    def _read_float(name: str, default: float) -> float:
        raw = env.get(name)
        if raw is None or raw == "":
            return default
        try:
            return float(raw)
        except ValueError as exc:
            raise InvalidValue(
                f"er_config: environment variable {name!r} is not a valid "
                f"float (got {raw!r})"
            ) from exc

    def _read_choice(name: str, default: str, choices: tuple[str, ...]) -> str:
        raw = env.get(name)
        if raw is None or raw == "":
            return default
        if raw not in choices:
            raise InvalidValue(
                f"er_config: environment variable {name!r} must be one of "
                f"{choices} (got {raw!r})"
            )
        return raw

    t_merge = _read_float("T_MERGE", ER_T_MERGE)
    t_new = _read_float("T_NEW", ER_T_NEW)
    w_llm = _read_float("W_LLM", ER_WEIGHTS["llm"])
    w_emb = _read_float("W_EMB", ER_WEIGHTS["emb"])
    w_rule = _read_float("W_RULE", ER_WEIGHTS["rule"])
    penalized_merge_policy = _read_choice(
        "ER_PENALIZED_MERGE_POLICY", ER_PENALIZED_MERGE_POLICY, ("ask", "merge")
    )

    return ERConfig(
        t_merge=t_merge,
        t_new=t_new,
        w_llm=w_llm,
        w_emb=w_emb,
        w_rule=w_rule,
        top_k=ER_TOP_K,
        judge_timeout=ER_JUDGE_TIMEOUT,
        judge_max_retries=ER_JUDGE_MAX_RETRIES,
        penalized_merge_policy=penalized_merge_policy,
    )


def user_timezone(env: dict[str, str] | None = None) -> ZoneInfo:
    """`APP_TIMEZONE` 환경변수(없으면 `DEFAULT_APP_TIMEZONE = "Asia/Seoul"`)
    를 IANA 시간대로 해석한다(FIX-005). 잘못된 이름이면 조용히 UTC 로
    되돌아가지 않고 사람이 읽는 오류를 낸다 -- `app_user_id()`/`er_config()`
    와 같은 `env` 인자 규약(생략하면 `os.environ`, `.env` 파일 자체는 읽지
    않는다, security.md §1)."""
    from app.tools.types import InvalidValue  # 지연 import -- 다른 settings 함수와 같은 관례.

    if env is None:
        env = dict(os.environ)
    name = env.get("APP_TIMEZONE") or DEFAULT_APP_TIMEZONE
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InvalidValue(
            f"user_timezone: APP_TIMEZONE={name!r} 은 유효한 IANA 시간대 이름이 "
            "아니다(예: Asia/Seoul, UTC)"
        ) from exc


def app_user_id(env: dict[str, str] | None = None) -> str:
    """`APP_USER_ID` 환경변수를 읽는다. 없으면 `"local"`.

    `env` 를 생략하면 `os.environ` 을 읽는다(실제 실행 경로). 테스트는 평범한
    dict 를 직접 넘겨 `os.environ` 을 건드리지 않고 이 함수를 검증한다
    (app.config.resolve_connection 과 같은 방식).
    """
    if env is None:
        env = dict(os.environ)
    return env.get("APP_USER_ID", DEFAULT_APP_USER_ID)
