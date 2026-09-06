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
from sqlalchemy.exc import PendingRollbackError

from app.db.models import AgentTrace, PendingQuestion, Person, PersonAlias
from app.tools.context import TRACE_MAX_STRING, ToolContext, to_jsonable, traced
from app.tools.persons import create_person
from app.tools.types import AFFIRMATIVE_KEY, InvalidValue, PersonOut

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


@traced("dummy_flush_failure")
def _dummy_flush_failure(ctx: ToolContext) -> None:
    """F-ca12ad 재현 수단(U2 전환, F-3ca6b5): flush 시점에만 드러나는 DB
    오류(`person_aliases.alias` NOT NULL 위반)를 강제로 일으킨다. 첫 번째
    `flush()`(person 행)는 성공하고, 두 번째 `flush()`(alias=None)만 실패한다
    -- U1 시점의 1535차원 가짜 공급자 재현은 이제 `check_dimension()`(U2)이
    flush 전에 가로채므로 더 이상 flush 실패를 만들지 못한다."""
    person = Person(
        user_id=ctx.user_id, display_name="flush-fail", relation_tag="지인", hierarchy="동"
    )
    ctx.session.add(person)
    ctx.session.flush()
    ctx.session.add(PersonAlias(person_id=person.id, alias=None, source="system"))
    ctx.session.flush()


class _FakeTokenResult:
    """`trace_tokens()` 를 제공하는 가짜 반환값 -- U1 `traced()` 확장의
    tokens 회수 경로를 검증하는 데만 쓴다(ER 판정 결과의 최소 모양)."""

    def __init__(self, tokens_in: int, tokens_out: int) -> None:
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out

    def trace_tokens(self) -> tuple[int, int]:
        return (self.tokens_in, self.tokens_out)


@traced("fake", step="er_resolve")
def _fake_step_with_tokens(ctx: ToolContext, mention: str) -> _FakeTokenResult:
    return _FakeTokenResult(tokens_in=12, tokens_out=34)


def _rows_for(db_session, session_id: str) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == session_id)
        ).scalars()
    )


def _make_pending_question(
    db_session,
    *,
    session_id: str,
    kind: str = "new_person",
    question: str = "저장할까요?",
    options: list[str] | None = None,
    answer: str | None = "예",
) -> PendingQuestion:
    """P2 의 `tests/test_tools_persons.py._make_pending_question` 과 같은
    규약(F-b97a06 긍정 답)을 이 파일 안에서 자체적으로 구성한다(테스트 파일간
    헬퍼 비공유 관례 -- `test_tools_records.py` 도 같은 방식)."""
    if options is None:
        options = ["예", "아니오"]
    row = PendingQuestion(
        session_id=session_id,
        kind=kind,
        question=question,
        options=options,
        context={AFFIRMATIVE_KEY: ["예"]},
        answer=answer,
        answered_at=datetime.now(timezone.utc),
    )
    db_session.add(row)
    db_session.flush()
    return row


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


# U2 에서 전환 완료(F-3ca6b5): `app.embedding.check_dimension()` 이 flush
# 전에 차원 불일치를 잡게 되어, U1 시점 재현 수단(1535차원 가짜 공급자)은
# 더 이상 flush 실패를 만들지 못한다. 재현 수단을 강제 flush 실패
# (`person_aliases.alias` NOT NULL 위반, `_dummy_flush_failure`)로 바꿔
# F-ca12ad 회귀를 유지한다. 차원 불일치의 "flush 전 사전 검출" 경로는 아래
# `test_add_alias_rejects_dimension_mismatch_before_flush` 가 대신 검증한다.
def test_traced_flush_failure_preserves_original_error(db_session):
    """F-ca12ad: 두 번째 `flush()`(NOT NULL 위반)가 실패했을 때, 호출자가
    받는 예외는 `PendingRollbackError` 가 아니라 원래 DB 오류(`DataError`/
    `StatementError`/`IntegrityError` 계열)여야 한다. `__context__` 도
    `PendingRollbackError` 로 덮이지 않아야 한다(결정7)."""
    session_id = "trace-flush-fail-1"
    ctx = ToolContext(session=db_session, session_id=session_id)

    with pytest.raises(Exception) as exc_info:
        _dummy_flush_failure(ctx)

    exc = exc_info.value
    assert not isinstance(exc, PendingRollbackError)
    assert type(exc).__name__ in {"DataError", "StatementError", "IntegrityError"}
    assert not isinstance(exc.__context__, PendingRollbackError)

    # `_dummy_flush_failure`(정상 flush 로 이미 person 행까지 쓴 뒤 두 번째
    # flush 에서 실패)의 세션은 이 시점에 SQLAlchemy 상 DEACTIVE 상태다 --
    # 실제 호출자(예: `get_session()`)가 그렇듯, 여기서도 회복을 위해
    # 명시적으로 `rollback()` 한다. 이것은 테스트가 세션을 계속 쓰기 위한
    # 정리이지 `traced()` 구현이 부르는 것이 아니다(구현은 절대
    # `session.rollback()` 을 부르지 않는다 -- 결정7. 위에서 이미
    # `begin_nested()` 가 세션 무효 상태를 감지해 조용히 포기했다는 것을
    # exc 가 원래 DB 오류 그대로임이 보여 준다).
    db_session.rollback()

    # 세이브포인트 안에서 tool_error 기록을 시도했지만 세션이 이미 무효라
    # 열 수 없었으므로(F-ca12ad) tool_error 행도, person 행도 남지 않는다
    # (rollback 이 미커밋 전체를 되돌린다) -- "원래 예외를 가리지 않는다"가
    # "오류 trace 를 항상 남긴다"보다 우선이라는 문서화된 트레이드오프다.
    rows = _rows_for(db_session, session_id)
    for row in rows:
        assert row.step == "tool_error"
        assert row.output["error"] == type(exc).__name__


def test_add_alias_rejects_dimension_mismatch_before_flush(db_session):
    """F-3ca6b5: 차원 불일치는 flush 전에 `check_dimension()` 이 사람이 읽는
    오류(`InvalidValue`)로 막는다 -- `DataError`/`PendingRollbackError` 가
    아니다. 이 예외는 평범한 파이썬 예외이므로 세션을 무효로 만들지 않고,
    `@traced` 의 `tool_error` 기록이 정상적으로 남는다(F-ca12ad 경로와
    다르다)."""
    session_id = "trace-dimension-1"
    question = _make_pending_question(db_session, session_id=session_id, kind="new_person")
    ctx = ToolContext(
        session=db_session,
        session_id=session_id,
        confirmed_question_id=question.id,
        embedder=lambda texts: [[0.1] * 1535 for _ in texts],
    )

    with pytest.raises(InvalidValue):
        create_person(ctx, "김철수", [], "직장", "상")

    rows = _rows_for(db_session, session_id)
    error_rows = [row for row in rows if row.step == "tool_error"]
    assert len(error_rows) == 1
    assert error_rows[0].output["error"] == "InvalidValue"
    assert error_rows[0].tool_name == "create_person"


def test_traced_step_argument_and_trace_tokens_are_recorded(db_session):
    session_id = "trace-step-tokens-1"
    ctx = ToolContext(session=db_session, session_id=session_id)

    result = _fake_step_with_tokens(ctx, "부장님")

    row = db_session.execute(
        select(AgentTrace).where(AgentTrace.session_id == session_id)
    ).scalar_one()
    assert row.step == "er_resolve"
    assert row.tool_name == "fake"
    assert row.tokens_in == result.tokens_in == 12
    assert row.tokens_out == result.tokens_out == 34


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
