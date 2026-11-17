"""Refs: P9b-auth U12 CR-008 D19 결정 4·5 AQ AR AS AT -- MCP 서버 생성·도구 등록(SDK import 는 이 파일에만).

`build_mcp_endpoint(session_factory, now)` 는 **호출마다 새** SDK 서버와 세션 관리자를 만든다(세션
관리자의 `run()` 은 인스턴스당 한 번만 되므로 `create_app()` 이 여러 번 불리는 시험에서도 서로 섞이지
않는다). 돌려주는 것: `(BearerAuthApp 으로 감싼 ASGI 앱, 세션 관리자)` -- `main.create_app()` 이 앞의 것을
정확 경로 `Route("/mcp")` 로 붙이고 뒤의 것을 `_lifespan` 에서 `run()` 한다.

## SDK 실물에서 정한 것 (mcp 2.3.0 — 03-log 에 파일:줄)

- 고수준 서버 클래스 `mcp.server.mcpserver.MCPServer`(v1 의 `FastMCP` 는 v2 에서 사라졌다).
- 무상태·JSON 응답: `streamable_http_app(stateless_http=True, json_response=True, ...)`.
- 호스트 검사(DNS 재바인딩 보호) 끄기(결정 AS): `transport_security=TransportSecuritySettings(
  enable_dns_rebinding_protection=False)` -- 넘기지 않으면 기본 `host="127.0.0.1"` 이라 SDK 가 localhost 만
  허용하는 검사를 자동으로 켠다.
- 사용자 id 전달(결정 AT): 인증 래퍼가 `scope["state"]` 에 싣고, 도구가 `ctx.request_context.request.scope`
  에서 읽는다(contextvar 가 아니라 요청 범위 -- SDK 의 태스크 구조에 기대지 않는다).
- SDK 의 인증 기능(`TokenVerifier`·`AuthSettings`·보호 리소스 메타데이터)은 쓰지 않는다(결정 AN).
- 오류 결과: SDK 가 `ToolError` 를 `Error executing tool <이름>: …` 로 감싸므로, 도구가 직접
  `CallToolResult(is_error=True, content=[코드 문자열 하나])` 를 돌려준다(SDK 는 이를 그대로 통과시킨다).

도구 호출 로그(결정 AW): `uvicorn.error.mcp` 에 한 줄 -- 이름·user·결과 개수뿐. 도구 인자 값(인물
이름·id)·토큰은 넣지 않는다.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import anyio.to_thread
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.streamable_http_manager import StreamableHTTPASGIApp, StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from sqlalchemy.orm import Session
from starlette.types import ASGIApp

from app.mcp_server import tools
from app.mcp_server.auth import USER_ID_STATE_KEY, BearerAuthApp
from app.mcp_server.tools import McpToolError

SERVER_NAME = "relmemo"

_log = logging.getLogger("uvicorn.error.mcp")

#: 모든 도구 설명의 공통 꼬리(01-plan "설명(description) 문구").
_TAIL = "사용자가 대화로 기록한 사실의 조회입니다. 기록에 없는 것은 없다고 말하세요."

DESC_LIST_PEOPLE = "내 관계 메모리에 기록된 인물 목록입니다(최근 접촉 순, 최대 200명). " + _TAIL
DESC_FIND_PERSON = (
    "이름이나 별칭에 이 글자가 들어간 인물을 모두 찾습니다(띄어쓰기·대소문자 무시, 최대 50명). "
    "여러 명이면 하나로 고르지 말고 사용자에게 누구인지 물으세요. " + _TAIL
)
DESC_GET_PERSON_CARD = (
    "인물 한 명의 카드입니다 — 기록된 사실, 반복 패턴, 최근 사건 20개, 다가오는 일정 10개. "
    "person_id 는 list_people·find_person 결과의 id 입니다. " + _TAIL
)
DESC_LIST_BRIEFINGS = (
    "만남 전에 만들어 둔 브리핑 목록입니다(최근 7일 이후 일정, 최대 20개). "
    "schedule_id 를 주면 그 일정의 브리핑만 돌려줍니다. 새 브리핑을 만들지 않습니다. " + _TAIL
)

#: 모든 도구 표시 -- 읽기 전용(D19 지킬 것 5).
_ANNOTATIONS = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)


def _ok(payload: dict[str, Any]) -> CallToolResult:
    """구조화 결과와 텍스트가 같은 JSON 객체."""
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))],
        structured_content=payload,
    )


def _error(code: str) -> CallToolResult:
    """도구 오류 결과 -- 텍스트는 코드 문자열 하나뿐."""
    return CallToolResult(content=[TextContent(type="text", text=code)], is_error=True)


def _read_user_id(ctx: Context) -> str | None:
    """인증 래퍼가 `scope["state"]` 에 실은 사용자 id. 읽지 못하면 `None`(기본 사용자로 내려가지 않는다)."""
    try:
        request = ctx.request_context.request
        value = request.scope.get("state", {}).get(USER_ID_STATE_KEY)  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001 -- 어떤 이유로든 못 읽으면 조회하지 않는다
        return None
    return value if isinstance(value, str) and value else None


def _count(name: str, result: dict[str, Any]) -> int:
    if name == "list_people":
        return len(result["people"])
    if name == "find_person":
        return len(result["matches"])
    if name == "get_person_card":
        return 1
    return len(result["briefings"])


def build_mcp_endpoint(
    session_factory: Callable[[], Session], now: Callable[[], datetime]
) -> tuple[ASGIApp, StreamableHTTPSessionManager]:
    """SDK 서버를 새로 만들어 `(인증 래퍼로 감싼 ASGI 앱, 세션 관리자)` 를 돌려준다.

    `now` 는 인증 만료 판정용 시계(시험이 덮어쓴다). 도구의 "현재 시각"(카드·브리핑 기간)은 계약대로
    `datetime.now(timezone.utc)` 다.
    """
    server = MCPServer(SERVER_NAME)

    async def _invoke(
        ctx: Context, name: str, call: Callable[[Session, str], dict[str, Any]]
    ) -> CallToolResult:
        user_id = _read_user_id(ctx)
        if user_id is None:  # R5-1 -- 조회하지 않고 오류. 첫 계정·기본 사용자로 내려가지 않는다.
            _log.info("mcp_tool name=%s user=%s items=%d", name, "-", 0)
            return _error("internal_error")

        def _work() -> dict[str, Any]:
            session = session_factory()
            try:
                return call(session, user_id)  # 읽기 전용 -- commit 하지 않는다
            finally:
                session.close()

        try:
            result = await anyio.to_thread.run_sync(_work)
        except McpToolError as exc:
            _log.info("mcp_tool name=%s user=%s items=%d", name, user_id, 0)
            return _error(exc.code)
        except Exception:  # noqa: BLE001 -- 예상 밖 예외는 원문 없이 `internal_error` 하나로
            _log.info("mcp_tool name=%s user=%s items=%d", name, user_id, 0)
            return _error("internal_error")
        _log.info("mcp_tool name=%s user=%s items=%d", name, user_id, _count(name, result))
        return _ok(result)

    async def list_people(ctx: Context) -> CallToolResult:
        return await _invoke(ctx, "list_people", lambda s, uid: tools.tool_list_people(s, uid))

    async def find_person(name: str, ctx: Context) -> CallToolResult:
        return await _invoke(
            ctx, "find_person", lambda s, uid: tools.tool_find_person(s, uid, name)
        )

    async def get_person_card(person_id: int, ctx: Context) -> CallToolResult:
        return await _invoke(
            ctx,
            "get_person_card",
            lambda s, uid: tools.tool_get_person_card(s, uid, person_id, datetime.now(timezone.utc)),
        )

    async def list_briefings(ctx: Context, schedule_id: int | None = None) -> CallToolResult:
        return await _invoke(
            ctx,
            "list_briefings",
            lambda s, uid: tools.tool_list_briefings(
                s, uid, datetime.now(timezone.utc), schedule_id
            ),
        )

    for fn, title, description in (
        (list_people, "인물 목록", DESC_LIST_PEOPLE),
        (find_person, "이름으로 인물 찾기", DESC_FIND_PERSON),
        (get_person_card, "인물 카드", DESC_GET_PERSON_CARD),
        (list_briefings, "저장된 브리핑", DESC_LIST_BRIEFINGS),
    ):
        server.add_tool(
            fn,
            name=fn.__name__,
            title=title,
            description=description,
            annotations=_ANNOTATIONS,
            structured_output=False,
        )

    # 호스트 검사를 끈다(결정 AS) -- 이 경로의 자격은 브라우저가 싣지 않는 Bearer 헤더다.
    server.streamable_http_app(
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    manager = server.session_manager
    return BearerAuthApp(StreamableHTTPASGIApp(manager), session_factory, now), manager
