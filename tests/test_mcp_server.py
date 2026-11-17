"""Refs: P9b-auth U12 CR-008 D19 D18 -- `/mcp` HTTP 왕복 시험(공식 SDK, 무상태·JSON 응답).

`MCP_ENABLED=1` 을 `monkeypatch.setenv` 한 뒤 `with TestClient(create_app(), base_url="https://testserver") as c:`
로 lifespan(세션 관리자 `run()`)을 돌린다. `follow_redirects=False`. 세션은 `app.main.SessionLocal` 을 롤백
픽스처(`db_session`)를 감싼 "닫지 않는 프록시"로 바꿔 끼워 DB 에 행이 남지 않게 한다. 시계는
`app.dependency_overrides[get_auth_now]` 로 고정한다(토큰 API 시험과 같은 방식).

토큰 값은 단언 실패 메시지에 넣지 않는다(D19 지킬 것 7). 실 PostgreSQL 이 필요하다(`dbtest`).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.deps import get_auth_now
from app.auth.mcp_tokens import issue_mcp_token, revoke_mcp_token
from app.auth.sessions import cookie_name, create_session
from app.db.models import (
    AgentTrace,
    ChatMessage,
    Event,
    FactSource,
    McpToken,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    PushSubscription,
    Schedule,
)
from app.db.session import get_session
from app.main import create_app
from app.settings import mcp_enabled
from app.tools.types import InvalidValue
from tests.auth_helpers import make_user

pytestmark = pytest.mark.dbtest

REPO_ROOT = Path(__file__).resolve().parents[1]
T0 = datetime(2026, 11, 18, 9, 0, 0, tzinfo=timezone.utc)
UNAUTH = {"detail": {"code": "unauthenticated"}}
ACCEPT = "application/json, text/event-stream"
UID_A = "mcpsrv-a"
UID_B = "mcpsrv-b"
TOOL_NAMES = {"list_people", "find_person", "get_person_card", "list_briefings"}
TAIL = "사용자가 대화로 기록한 사실의 조회입니다. 기록에 없는 것은 없다고 말하세요."

_COUNTED = (
    Person,
    PersonAlias,
    PersonFact,
    FactSource,
    Event,
    Schedule,
    PendingQuestion,
    PushSubscription,
    AgentTrace,
    ChatMessage,
    McpToken,
)


class _Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


class _SharedSession:
    """롤백 픽스처 세션을 감싸되 `close()` 를 하지 않는 프록시 -- 도구·래퍼가 세션을 닫아도 데이터가 남는다."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def __getattr__(self, name: str) -> Any:
        return getattr(self._session, name)

    def close(self) -> None:  # noqa: D401 -- 의도적 no-op
        return None


@pytest.fixture()
def clock() -> _Clock:
    return _Clock(T0)


@pytest.fixture()
def enabled_app(db_session, clock, monkeypatch):
    monkeypatch.setenv("MCP_ENABLED", "1")
    monkeypatch.setattr("app.main.SessionLocal", lambda: _SharedSession(db_session))
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_auth_now] = lambda: clock
    return app


@pytest.fixture()
def client(enabled_app):
    with TestClient(
        enabled_app,
        base_url="https://testserver",
        follow_redirects=False,
        raise_server_exceptions=False,
    ) as c:
        yield c


def _rpc(client: TestClient, token: str | None, method: str, params: dict | None = None, **kw: Any):
    headers = {"Accept": ACCEPT, "Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    headers.update(kw.pop("headers", {}))
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    return client.post("/mcp", json=body, headers=headers, **kw)


def _call(client: TestClient, token: str, name: str, arguments: dict | None = None) -> dict:
    resp = _rpc(client, token, "tools/call", {"name": name, "arguments": arguments or {}})
    assert resp.status_code == 200, resp.text
    return resp.json()["result"]


def _text(result: dict) -> str:
    return result["content"][0]["text"]


def _issue(db, uid: str, now: datetime = T0, nickname: str | None = None) -> str:
    make_user(db, uid, nickname=nickname)
    token, _created, _expires = issue_mcp_token(db, uid, now)
    return token


def _person(db, uid: str, name: str, aliases: tuple[str, ...] = ()) -> Person:
    p = Person(user_id=uid, display_name=name, relation_tag="직장", hierarchy="상")
    db.add(p)
    db.flush()
    for a in aliases:
        db.add(PersonAlias(person_id=p.id, alias=a, source="user"))
    db.flush()
    return p


def _counts(db) -> list[int]:
    db.flush()
    return [db.scalar(select(func.count()).select_from(m)) for m in _COUNTED]


def _row(db) -> McpToken:
    db.flush()
    return db.scalar(select(McpToken))


# ① 꺼짐 ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("raw", [None, "", "0", "false"])
def test_disabled_app_has_no_mcp_route(monkeypatch, raw) -> None:
    if raw is None:
        monkeypatch.delenv("MCP_ENABLED", raising=False)
    else:
        monkeypatch.setenv("MCP_ENABLED", raw)

    app = create_app()  # `0`·`false` 도 예외 없이 뜬다(F5-1)
    client = TestClient(app, base_url="https://testserver", follow_redirects=False)

    assert client.post("/mcp").status_code == 404
    assert client.get("/mcp").status_code == 404
    assert not hasattr(app.state, "mcp_session_manager")


def test_import_app_main_does_not_import_the_sdk_when_disabled() -> None:
    env = {k: v for k, v in os.environ.items() if k != "MCP_ENABLED"}
    code = (
        "import app.main, sys; "
        "print(any(m == 'mcp' or m.startswith('mcp.') for m in sys.modules))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=120
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    assert proc.stdout.strip() == "False"


def test_invalid_switch_value_fails_app_start(monkeypatch) -> None:
    monkeypatch.setenv("MCP_ENABLED", "yes")

    with pytest.raises(InvalidValue):
        create_app()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(None, False), ("", False), ("0", False), ("false", False), ("1", True), ("true", True)],
)
def test_mcp_enabled_values(raw, expected) -> None:
    env = {} if raw is None else {"MCP_ENABLED": raw}

    assert mcp_enabled(env) is expected


@pytest.mark.parametrize("raw", ["yes", "TRUE", "on", "2", " 1"])
def test_mcp_enabled_rejects_other_values(raw) -> None:
    with pytest.raises(InvalidValue):
        mcp_enabled({"MCP_ENABLED": raw})


# ② 401 은 전부 같은 응답 --------------------------------------------------------------------------


def _assert_401(resp) -> None:
    assert resp.status_code == 401
    assert resp.json() == UNAUTH
    assert resp.headers["WWW-Authenticate"].startswith("Bearer")
    assert resp.headers["Content-Type"].startswith("application/json")


def test_no_header_is_401(client, db_session) -> None:
    _issue(db_session, UID_A)

    _assert_401(_rpc(client, None, "tools/list"))
    _assert_401(client.get("/mcp"))


@pytest.mark.parametrize("header", ["Basic dXNlcjpwYXNz", "Bearer", "Bearer ", "Bearer     ", "Token abc"])
def test_non_bearer_or_empty_value_is_401(client, db_session, header) -> None:
    _issue(db_session, UID_A)

    _assert_401(_rpc(client, None, "tools/list", headers={"Authorization": header}))


def test_unknown_token_is_401(client, db_session) -> None:
    _issue(db_session, UID_A)

    _assert_401(_rpc(client, "x" * 43, "tools/list"))


def test_expired_token_is_401_but_one_second_before_is_ok(client, db_session, clock) -> None:
    token = _issue(db_session, UID_A)
    expires = T0 + timedelta(days=7)

    clock.now = expires - timedelta(seconds=1)
    assert _rpc(client, token, "tools/list").status_code == 200
    clock.now = expires  # 같은 순간은 만료
    _assert_401(_rpc(client, token, "tools/list"))


def test_revoked_token_is_401(client, db_session) -> None:
    token = _issue(db_session, UID_A)
    assert _rpc(client, token, "tools/list").status_code == 200

    revoke_mcp_token(db_session, UID_A)

    _assert_401(_rpc(client, token, "tools/list"))


def test_superseded_token_is_401_and_new_one_works(client, db_session, clock) -> None:
    old = _issue(db_session, UID_A)
    clock.now = T0 + timedelta(minutes=1)
    new, _c, _e = issue_mcp_token(db_session, UID_A, clock.now)

    _assert_401(_rpc(client, old, "tools/list"))
    assert _rpc(client, new, "tools/list").status_code == 200


def test_scheme_is_case_insensitive_and_value_is_stripped(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    for header in (f"bearer {token}", f"BEARER {token}", f"Bearer   {token}  "):
        resp = _rpc(client, None, "tools/list", headers={"Authorization": header})
        assert resp.status_code == 200, header.split(" ")[0]


def test_missing_or_non_bearer_header_never_queries_the_database(enabled_app, monkeypatch) -> None:
    """엔진에 묶이지 않은 세션 팩토리 -- DB 에 가면 오류(500)가 난다. 헤더 없음·다른 스킴·빈 값은 401."""
    monkeypatch.setattr("app.main.SessionLocal", lambda: Session())
    app = create_app()
    with TestClient(app, base_url="https://testserver", follow_redirects=False) as c:
        for header in (None, "Basic abc", "Bearer ", "Bearer"):
            extra = {} if header is None else {"Authorization": header}
            resp = c.post("/mcp", json={}, headers={"Accept": ACCEPT, **extra})
            _assert_401(resp)


# ③ 쿠키·쿼리 문자열은 자격이 아니다 ---------------------------------------------------------------


def test_login_cookie_alone_is_not_a_credential(client, db_session) -> None:
    make_user(db_session, UID_A)
    client.cookies.set(cookie_name(), create_session(db_session, UID_A, T0))

    _assert_401(_rpc(client, None, "tools/list"))
    assert client.get("/auth/me").status_code == 200  # 쿠키 자체는 유효한 로그인이다


@pytest.mark.parametrize("param", ["token", "access_token"])
def test_query_string_token_is_not_a_credential(client, db_session, param) -> None:
    token = _issue(db_session, UID_A)

    resp = client.post(
        f"/mcp?{param}={token}",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Accept": ACCEPT},
    )

    _assert_401(resp)


def test_bearer_header_is_not_a_credential_for_other_routes(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    resp = client.get("/persons", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 401
    assert resp.json() == UNAUTH


# ④ 정확 경로 -- 3xx 없음 ---------------------------------------------------------------------------


def test_exact_path_is_served_without_redirect(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    resp = _rpc(client, token, "tools/list")

    assert resp.status_code == 200
    assert not 300 <= resp.status_code < 400
    assert "location" not in resp.headers


def test_foreign_origin_post_is_rejected_by_the_existing_middleware(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    resp = _rpc(client, token, "tools/list", headers={"Origin": "https://evil.example"})

    assert resp.status_code == 403
    assert resp.json() == {"detail": {"code": "bad_origin"}}


# ⑤ 도구 목록 ----------------------------------------------------------------------------------------


def test_tools_list_is_exactly_the_four_read_only_tools(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    resp = _rpc(client, token, "tools/list")

    tools = {t["name"]: t for t in resp.json()["result"]["tools"]}
    assert set(tools) == TOOL_NAMES
    for name, t in tools.items():
        ann = t["annotations"]
        assert ann["readOnlyHint"] is True, name
        assert ann["destructiveHint"] is False, name
        assert ann["idempotentHint"] is True, name
        assert ann["openWorldHint"] is False, name
        props = t["inputSchema"].get("properties", {})
        assert "user_id" not in props and "username" not in props, name
        assert t["description"].endswith(TAIL), name
        assert t["title"] and not t["title"].isascii(), name  # 한국어 제목
    assert tools["list_people"]["inputSchema"].get("properties", {}) == {}
    assert tools["find_person"]["inputSchema"]["required"] == ["name"]
    assert tools["get_person_card"]["inputSchema"]["required"] == ["person_id"]
    assert tools["get_person_card"]["inputSchema"]["properties"]["person_id"]["type"] == "integer"
    assert "schedule_id" in tools["list_briefings"]["inputSchema"]["properties"]
    assert "schedule_id" not in tools["list_briefings"]["inputSchema"].get("required", [])
    assert tools["list_people"]["title"] == "인물 목록"
    assert tools["find_person"]["title"] == "이름으로 인물 찾기"
    assert tools["get_person_card"]["title"] == "인물 카드"
    assert tools["list_briefings"]["title"] == "저장된 브리핑"
    assert tools["list_people"]["description"].startswith(
        "내 관계 메모리에 기록된 인물 목록입니다(최근 접촉 순, 최대 200명). "
    )
    assert tools["find_person"]["description"].startswith(
        "이름이나 별칭에 이 글자가 들어간 인물을 모두 찾습니다(띄어쓰기·대소문자 무시, 최대 50명). "
        "여러 명이면 하나로 고르지 말고 사용자에게 누구인지 물으세요. "
    )
    assert tools["get_person_card"]["description"].startswith(
        "인물 한 명의 카드입니다 — 기록된 사실, 반복 패턴, 최근 사건 20개, 다가오는 일정 10개. "
    )
    assert tools["list_briefings"]["description"].startswith(
        "만남 전에 만들어 둔 브리핑 목록입니다(최근 7일 이후 일정, 최대 20개). "
    )


def test_initialize_reports_server_name_relmemo(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    resp = _rpc(
        client,
        token,
        "initialize",
        {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}},
    )

    assert resp.status_code == 200
    assert resp.json()["result"]["serverInfo"]["name"] == "relmemo"


# ⑥ 격리 ---------------------------------------------------------------------------------------------


def test_each_token_sees_only_its_own_accounts_people_across_alternating_calls(client, db_session) -> None:
    token_a = _issue(db_session, UID_A)
    token_b = _issue(db_session, UID_B)
    a = _person(db_session, UID_A, "에이의 팀장", aliases=("에이별칭",))
    b = _person(db_session, UID_B, "비의 부장")

    for _ in range(3):  # 번갈아 여러 번 -- 요청 사이에 사용자 id 가 섞이지 않는다(R5-1)
        ra = _call(client, token_a, "list_people")
        rb = _call(client, token_b, "list_people")
        assert [p["id"] for p in ra["structuredContent"]["people"]] == [a.id]
        assert [p["id"] for p in rb["structuredContent"]["people"]] == [b.id]
        assert ra["structuredContent"]["total"] == 1 and rb["structuredContent"]["total"] == 1


def test_other_accounts_card_is_not_found_and_find_person_is_empty(client, db_session) -> None:
    token_a = _issue(db_session, UID_A)
    _issue(db_session, UID_B)
    theirs = _person(db_session, UID_B, "비의 부장")

    card = _call(client, token_a, "get_person_card", {"person_id": theirs.id})
    found = _call(client, token_a, "find_person", {"name": "비의 부장"})

    assert card["isError"] is True
    assert _text(card) == "not_found"
    assert found["isError"] is False
    assert found["structuredContent"] == {"matches": [], "total": 0, "truncated": False}


def test_result_text_and_structured_content_are_the_same_json_object(client, db_session) -> None:
    token = _issue(db_session, UID_A)
    p = _person(db_session, UID_A, "김팀장", aliases=("팀장님",))

    result = _call(client, token, "list_people")

    assert result["isError"] is False
    assert json.loads(_text(result)) == result["structuredContent"]
    assert result["structuredContent"]["people"][0]["id"] == p.id
    assert result["structuredContent"]["people"][0]["aliases"] == ["팀장님"]
    card = _call(client, token, "get_person_card", {"person_id": p.id})
    assert json.loads(_text(card)) == card["structuredContent"]
    assert card["structuredContent"]["person"]["id"] == p.id


def test_list_briefings_other_accounts_schedule_is_not_found_and_overall_is_empty(client, db_session) -> None:
    token_a = _issue(db_session, UID_A)
    _issue(db_session, UID_B)
    theirs = _person(db_session, UID_B, "비의 부장")
    s = Schedule(person_id=theirs.id, title="회의", scheduled_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(s)
    db_session.flush()

    overall = _call(client, token_a, "list_briefings")
    other = _call(client, token_a, "list_briefings", {"schedule_id": s.id})

    assert overall["structuredContent"] == {"briefings": []}
    assert other["isError"] is True and _text(other) == "not_found"


def test_find_person_blank_name_is_invalid_name_error_result(client, db_session) -> None:
    token = _issue(db_session, UID_A)

    result = _call(client, token, "find_person", {"name": "   "})

    assert result["isError"] is True
    assert _text(result) == "invalid_name"


def test_unexpected_exception_becomes_internal_error_without_leaking(client, db_session, monkeypatch) -> None:
    token = _issue(db_session, UID_A)

    def _boom(*_a: object, **_k: object) -> dict:
        raise RuntimeError("SECRET-SQL-TEXT select * from users")

    monkeypatch.setattr("app.mcp_server.tools.tool_list_people", _boom)

    resp = _rpc(client, token, "tools/call", {"name": "list_people", "arguments": {}})

    result = resp.json()["result"]
    assert result["isError"] is True
    assert _text(result) == "internal_error"
    assert "SECRET" not in resp.text


def test_missing_user_id_in_request_scope_is_internal_error_not_a_default_user() -> None:
    """R5-1 -- 사용자 id 를 못 읽으면 조회하지 않고 `internal_error`(기본 사용자로 내려가지 않는다)."""
    from app.mcp_server.server import _read_user_id

    no_request = SimpleNamespace(request_context=SimpleNamespace(request=None))
    no_state = SimpleNamespace(request_context=SimpleNamespace(request=SimpleNamespace(scope={})))
    empty = SimpleNamespace(
        request_context=SimpleNamespace(
            request=SimpleNamespace(scope={"state": {"relmemo_mcp_user_id": ""}})
        )
    )
    ok = SimpleNamespace(
        request_context=SimpleNamespace(
            request=SimpleNamespace(scope={"state": {"relmemo_mcp_user_id": "u-1"}})
        )
    )

    assert _read_user_id(no_request) is None  # type: ignore[arg-type]
    assert _read_user_id(no_state) is None  # type: ignore[arg-type]
    assert _read_user_id(empty) is None  # type: ignore[arg-type]
    assert _read_user_id(ok) == "u-1"  # type: ignore[arg-type]


# ⑦ last_used_at ---------------------------------------------------------------------------------------


def test_last_used_at_is_set_on_success_and_not_touched_by_a_401(client, db_session, clock) -> None:
    token = _issue(db_session, UID_A)
    assert _row(db_session).last_used_at is None

    _assert_401(_rpc(client, "y" * 43, "tools/list"))
    _assert_401(_rpc(client, None, "tools/list"))
    assert _row(db_session).last_used_at is None  # 401 뒤 변화 0

    clock.now = T0 + timedelta(hours=3)
    assert _rpc(client, token, "tools/list").status_code == 200
    assert _row(db_session).last_used_at == T0 + timedelta(hours=3)


# ⑧ 로그 -----------------------------------------------------------------------------------------------


def test_one_log_line_per_tool_call_without_token_or_argument_values(client, db_session, caplog) -> None:
    token = _issue(db_session, UID_A)
    p = _person(db_session, UID_A, "고유한이름씨")

    with caplog.at_level(logging.DEBUG):
        _call(client, token, "list_people")
        _call(client, token, "find_person", {"name": "고유한이름"})
        _call(client, token, "get_person_card", {"person_id": p.id})
        _call(client, token, "get_person_card", {"person_id": p.id + 99_999})
        _call(client, token, "list_briefings")

    lines = [r.getMessage() for r in caplog.records if r.name == "uvicorn.error.mcp"]
    assert lines == [
        f"mcp_tool name=list_people user={UID_A} items=1",
        f"mcp_tool name=find_person user={UID_A} items=1",
        f"mcp_tool name=get_person_card user={UID_A} items=1",
        f"mcp_tool name=get_person_card user={UID_A} items=0",  # 오류는 0
        f"mcp_tool name=list_briefings user={UID_A} items=0",
    ]
    for record in caplog.records:
        rendered = record.getMessage() + " " + str(record.args)
        assert token not in rendered
        assert "고유한이름" not in rendered
        assert str(p.id) not in rendered.replace(UID_A, "")


# ⑨ 읽기 전용 -- 데이터·trace 표 불변 -----------------------------------------------------------------------


def test_tool_calls_do_not_change_row_counts(client, db_session, clock) -> None:
    token = _issue(db_session, UID_A)
    p = _person(db_session, UID_A, "김팀장")
    db_session.add(Event(person_id=p.id, type="meal", content="점심", raw_utterance="원문", occurred_at=T0))
    db_session.flush()
    before = _counts(db_session)

    clock.now = T0 + timedelta(minutes=5)
    _call(client, token, "list_people")
    _call(client, token, "find_person", {"name": "김팀장"})
    _call(client, token, "get_person_card", {"person_id": p.id})
    _call(client, token, "list_briefings")

    assert _counts(db_session) == before  # `mcp_tokens` 는 last_used_at 갱신뿐이라 행 수가 같다


def test_each_create_app_gets_its_own_session_manager_and_both_lifespans_run(enabled_app, db_session) -> None:
    """세션 관리자의 `run()` 은 인스턴스당 한 번만 된다 -- 앱마다 새로 만들어 서로 섞이지 않는다."""
    other = create_app()
    other.dependency_overrides[get_auth_now] = lambda: _Clock(T0)
    token = _issue(db_session, UID_A)

    assert enabled_app.state.mcp_session_manager is not other.state.mcp_session_manager
    for app in (enabled_app, other):
        with TestClient(app, base_url="https://testserver", follow_redirects=False) as c:
            assert _rpc(c, token, "tools/list").status_code == 200
