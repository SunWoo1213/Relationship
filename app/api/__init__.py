"""Refs: P2-tools U8 결정 11 -- HTTP 라우터 패키지.

`app/api/{deps,routes,schemas}.py` 로 나눈다(단일 `main.py` 아님). 엔드포인트가
지금은 2개뿐이지만 P5-loop(채팅·재개)·P6·P8(조회 API)가 같은 자리에 라우트를
더할 것이 확정되어 있어, 이 패키지 경계를 먼저 잡아둔다. `app/main.py` 는
조립(팩토리 + 예외 핸들러 등록)만 하는 자리로 남긴다.

이 모듈은 라우터 객체만 재export한다 -- `app/main.py` 가 `from app.api import
router` 로 가져온다.
"""

from __future__ import annotations

from app.api.routes import router

__all__ = ["router"]
