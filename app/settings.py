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
"""

from __future__ import annotations

import os

DEFAULT_APP_USER_ID = "local"

#: 후보 검색(`search_person`)의 별칭 임베딩 top-K (D5/S3.3).
SEARCH_TOP_K = 10


def app_user_id(env: dict[str, str] | None = None) -> str:
    """`APP_USER_ID` 환경변수를 읽는다. 없으면 `"local"`.

    `env` 를 생략하면 `os.environ` 을 읽는다(실제 실행 경로). 테스트는 평범한
    dict 를 직접 넘겨 `os.environ` 을 건드리지 않고 이 함수를 검증한다
    (app.config.resolve_connection 과 같은 방식).
    """
    if env is None:
        env = dict(os.environ)
    return env.get("APP_USER_ID", DEFAULT_APP_USER_ID)
