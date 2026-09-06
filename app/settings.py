"""Refs: P2-tools S3.2 S3.3 D5 -- 런타임 설정값의 단일 출처.

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
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover -- 순환 import 회피, 타입 힌트 전용.
    from app.er.types import ERConfig

DEFAULT_APP_USER_ID = "local"

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

#: 임계치 비교 허용오차의 단일 출처(F-7fe239). `app/er/confidence.py` 의
#: `ge_with_tolerance()` 하나만 이 상수를 쓴다 -- `round()` 기반 비교는
#: 쓰지 않는다(경계 폭이 넓어 `T_merge` 미만 confidence 를 merge 로
#: 판정할 위험이 있어 원칙1 의 방향과 반대다).
ER_TOLERANCE = 1e-9


def er_config(env: dict[str, str] | None = None) -> "ERConfig":
    """`.env.example` 이 이름을 정한 `T_MERGE`/`T_NEW`/`W_LLM`/`W_EMB`/
    `W_RULE` 환경변수를 읽어 `ERConfig` 를 만든다(결정8 2층). 이름을 새로
    만들지 않는다 -- `app.tools.types.InvalidValue` 는 `ERConfig` 생성
    자체(가중치 합·임계치 순서 검증)에서 던져지고, 이 함수는 **문자열
    파싱 실패**에도 같은 예외를 사람이 읽는 메시지로 던진다.

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

    t_merge = _read_float("T_MERGE", ER_T_MERGE)
    t_new = _read_float("T_NEW", ER_T_NEW)
    w_llm = _read_float("W_LLM", ER_WEIGHTS["llm"])
    w_emb = _read_float("W_EMB", ER_WEIGHTS["emb"])
    w_rule = _read_float("W_RULE", ER_WEIGHTS["rule"])

    return ERConfig(
        t_merge=t_merge,
        t_new=t_new,
        w_llm=w_llm,
        w_emb=w_emb,
        w_rule=w_rule,
        top_k=ER_TOP_K,
        judge_timeout=ER_JUDGE_TIMEOUT,
        judge_max_retries=ER_JUDGE_MAX_RETRIES,
    )


def app_user_id(env: dict[str, str] | None = None) -> str:
    """`APP_USER_ID` 환경변수를 읽는다. 없으면 `"local"`.

    `env` 를 생략하면 `os.environ` 을 읽는다(실제 실행 경로). 테스트는 평범한
    dict 를 직접 넘겨 `os.environ` 을 건드리지 않고 이 함수를 검증한다
    (app.config.resolve_connection 과 같은 방식).
    """
    if env is None:
        env = dict(os.environ)
    return env.get("APP_USER_ID", DEFAULT_APP_USER_ID)
