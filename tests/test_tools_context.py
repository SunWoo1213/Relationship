"""Refs: P2-tools S3.2 원칙9 F-4d8d96 -- ToolContext·@traced 관측성 데코레이터.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다. U3~U7 의 실제 툴이 아직 없으므로, 데코레이터 자체를 검증하는 더미
함수를 이 파일 안에서 `@traced` 로 감싼다.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.db.models import AgentTrace
from app.tools.context import TRACE_MAX_STRING, ToolContext, to_jsonable, traced
from app.tools.types import InvalidValue, PersonOut

pytestmark = pytest.mark.dbtest


@traced("dummy_success")
def _dummy_success(ctx: ToolContext, name: str, when: datetime) -> PersonOut:
    return PersonOut(id=1, display_name=name, relation_tag="지인", hierarchy="동", aliases=["a"])


@traced("dummy_error")
def _dummy_error(ctx: ToolContext, value: str) -> None:
    raise InvalidValue(f"bad:{value}")


@traced("dummy_long")
def _dummy_long(ctx: ToolContext, text_value: str) -> str:
    return "ok"


def _rows_for(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == session_id)
        ).scalars()
    )


def test_traced_success_writes_exactly_one_tool_call_row(db_session):
    session_id = "trace-success-1"
    ctx = ToolContext(session=db_session, session_id=session_id)
    when = datetime(2026, 1, 1, tzinfo=timezone.utc)

    result = _dummy_success(ctx, "김팀장", when=when)

    rows = _rows_for(db_session, session_id)
    assert len(rows) == 1
    row = rows[0]
    assert row.step == "tool_call"
    assert row.tool_name == "dummy_success"
    assert row.session_id == session_id
    assert "ctx" not in row.input
    assert row.input == {"name": "김팀장", "when": when.isoformat()}
    assert row.output == result.to_dict()
    assert row.tokens_in == 0
    assert row.tokens_out == 0


def test_traced_exception_writes_tool_error_row_and_reraises(db_session):
    session_id = "trace-error-1"
    ctx = ToolContext(session=db_session, session_id=session_id)

    with pytest.raises(InvalidValue):
        _dummy_error(ctx, "x")

    rows = _rows_for(db_session, session_id)
    assert len(rows) == 1
    row = rows[0]
    assert row.step == "tool_error"
    assert row.tool_name == "dummy_error"
    assert row.input == {"value": "x"}
    assert row.output["error"] == "InvalidValue"
    assert row.output["message"] == "bad:x"
    assert row.tokens_in == 0
    assert row.tokens_out == 0


def test_traced_truncates_long_string_argument(db_session):
    session_id = "trace-trunc-1"
    ctx = ToolContext(session=db_session, session_id=session_id)
    long_value = "가" * 3000

    _dummy_long(ctx, long_value)

    row = db_session.execute(
        select(AgentTrace).where(AgentTrace.session_id == session_id)
    ).scalar_one()
    stored = row.input["text_value"]
    assert "truncated" in stored
    assert stored.startswith("가" * TRACE_MAX_STRING)
    assert len(stored) <= TRACE_MAX_STRING + len("…[truncated 1000 chars]") + 5


def test_traced_datetime_argument_becomes_isoformat_string(db_session):
    session_id = "trace-dt-1"
    ctx = ToolContext(session=db_session, session_id=session_id)
    when = datetime(2026, 3, 4, 5, 6, tzinfo=timezone.utc)

    _dummy_success(ctx, "이대리", when=when)

    row = db_session.execute(
        select(AgentTrace).where(AgentTrace.session_id == session_id)
    ).scalar_one()
    assert row.input["when"] == when.isoformat()
    assert isinstance(row.input["when"], str)


def test_traced_preserves_original_function_signature():
    original_signature = inspect.signature(_dummy_success.__wrapped__)
    assert inspect.signature(_dummy_success) == original_signature


def test_tool_context_repr_excludes_session_object_repr():
    class _FakeSession:
        def __repr__(self) -> str:  # pragma: no cover -- only used via repr()
            return "<FakeSessionRepr SECRET_MARKER_e91a>"

    ctx = ToolContext(session=_FakeSession(), session_id="s1")
    assert "SECRET_MARKER_e91a" not in repr(ctx)
    assert "session_id='s1'" in repr(ctx)


def test_to_jsonable_handles_nested_structures_without_ctx():
    payload = {"a": [1, "x", {"b": None}], "c": (1, 2)}
    assert to_jsonable(payload) == {"a": [1, "x", {"b": None}], "c": [1, 2]}
