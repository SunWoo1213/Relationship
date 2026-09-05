"""Refs: P2-tools S3.2 원칙9 -- ToolContext 실행 맥락 + @traced 관측성 데코레이터.

## embedder 타입 결정 (U2, F-0010e6 와 별개 -- 03-log 에 기록)
`ToolContext.embedder` 는 `app.embedding.EmbeddingProvider` Protocol 이
**아니라** `Callable[[list[str]], list[list[float]]] | None` 로 둔다.
01-plan 은 `app/embedding.py`(Protocol 정의)를 U3 산출물로 명시하므로,
U2 에서 그 파일을 먼저 만들면 U3 의 산출물 목록·registry 신규 행과
어긋난다(파일 소유 단위가 흐려진다). U3 가 `EmbeddingProvider` 를 정의하면
이 자리의 타입 별칭을 그 Protocol 로 좁힌다(TODO: U3). `tests/conftest.py`
의 `fake_embedder` 는 이미 이 Callable 형태(`list[str] -> list[list[float]]`)
를 따르므로 U3 에서 그대로 주입할 수 있다.

## tool_error 행의 한계 (F-4d8d96 -- 우회 구현 금지)
01-plan 결정 2 는 "툴은 commit 하지 않고 `flush()` 까지만 한다"고 정하고,
트랜잭션 경계는 호출자(`app/db/session.py` 의 `session_scope()`, U8 의
`app/api/deps.py` 의 `get_session()`)가 잡는다. `@traced` 가 예외 시 만드는
`step="tool_error"` 행도 **같은 세션**에 `add()` + `flush()` 될 뿐이므로,
호출자가 예외를 잡아 `rollback()` 하면 이 tool_error 행도 함께 사라진다.
즉 이 데코레이터가 보장하는 것은 "예외가 나기 전까지, 같은(아직 커밋되지
않은) 트랜잭션 안에서 조회 가능하다"까지이며, **운영 경로에서 오류 trace
가 DB 에 영구히 남는다는 보장은 아니다**. `tests/test_tools_context.py`
가 tool_error 행을 조회해 통과하는 것은 롤백 픽스처(`db_session`)가 아직
롤백하기 *전* 시점에서 같은 트랜잭션으로 조회하기 때문이다(P2 자체의 예외는
`InvalidValue`/`PersonNotFound`/`ConfirmationRequired` 같은 검증 오류라
원칙9 "판정 근거" 손실에는 해당하지 않는다). 별도 커넥션으로 오류를 영구
기록할지는 **P5-loop 01-plan** 이 결정한다 -- 이 한계를 지금 여기서
우회(예: 별도 커넥션 즉시 커밋)로 고치지 않는다.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from app.db.models import AgentTrace
from app.settings import app_user_id

#: agent_traces.input/output 에 들어가는 개별 문자열 값의 최대 길이. 초과분은
#: 잘라내고 "…[truncated N chars]" 표식을 붙인다(N = 잘려나간 문자 수).
TRACE_MAX_STRING = 2000

#: U3 가 `app.embedding.EmbeddingProvider` Protocol 을 정의할 때까지 쓰는
#: 자리표시자 타입. `list[str] -> list[list[float]]`.
EmbedderCallable = Callable[[list[str]], list[list[float]]]

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ToolContext:
    """모든 툴 함수의 첫 매개변수(01-plan 결정 2 -- `ctx` 하나만 앞에 붙인다).

    툴은 이 객체 밖의 전역 상태를 읽지 않는다. `session` 은 `repr=False`로
    두어 `repr(ctx)`/로그에 SQLAlchemy `Session` 객체(커넥션 정보 포함)가
    통째로 찍히지 않게 한다.
    """

    session: Session = field(repr=False)
    session_id: str
    user_id: str = field(default_factory=app_user_id)
    embedder: EmbedderCallable | None = None
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    confirmed_question_id: int | None = None


def _truncate_string(value: str) -> str:
    """`TRACE_MAX_STRING` 초과 문자열을 절단하고 표식을 붙인다."""
    if len(value) <= TRACE_MAX_STRING:
        return value
    removed = len(value) - TRACE_MAX_STRING
    return f"{value[:TRACE_MAX_STRING]}…[truncated {removed} chars]"


def to_jsonable(obj: Any) -> Any:
    """`@traced` 의 input/output(JSONB 컬럼)에 저장 가능한 값으로 변환한다.

    우선순위: `to_dict()` 가 있는 객체(전부 *Out dataclass) → 그 결과를 재귀
    변환 / `datetime` → `isoformat()` 문자열 / `Decimal`·`float`·`int`·
    `bool`·`None` → 그대로 / `dict` → 키를 `str()`, 값을 재귀 변환 /
    `list`·`tuple`·`set` → 각 원소 재귀 변환 / 문자열 → 길이 초과 시 절단 /
    그 밖의 값 → `str()` 후 절단.

    `ToolContext` 는 이 함수에 절대 넘기지 않는다 -- `@traced` 가 인자를
    바인딩할 때 `ctx` 이름을 미리 제외한다.
    """
    if obj is None or isinstance(obj, (bool, int, float, Decimal)):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, str):
        return _truncate_string(obj)
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_jsonable(to_dict())
    if isinstance(obj, dict):
        return {str(key): to_jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(value) for value in obj]
    return _truncate_string(str(obj))


def traced(tool_name: str) -> Callable[[F], F]:
    """`agent_traces` 기록 데코레이터(원칙9). 대상 함수 시그니처는
    `(ctx, *args, **kwargs)`.

    성공: `step="tool_call"`, `input`=ctx 를 뺀 인자의 이름→값 매핑을
    `to_jsonable` 로 변환한 것, `output`=반환값을 `to_jsonable` 로 변환한
    것(반환값이 `*Out` 이면 사실상 `to_dict()`), `tokens_in=tokens_out=0`
    (P2 에는 LLM 호출이 없다).

    예외: `step="tool_error"`, `output={"error": 예외 클래스명,
    "message": str(e)[:TRACE_MAX_STRING]}` 를 남기고 **예외를 다시 올린다**
    (F-4d8d96 한계는 모듈 docstring 참고).

    `functools.wraps` 로 `__name__`·`__doc__`·`__wrapped__` 를 보존하되,
    `wrapper.__signature__` 를 원함수의 시그니처로 명시해 `inspect.signature`
    가 `ctx` 를 포함한 원래 모양 그대로 보이게 한다(U9 `tools_check.py` 가
    이 시그니처를 본다).
    """

    def decorator(fn: F) -> F:
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(ctx: ToolContext, *args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(ctx, *args, **kwargs)
            bound.apply_defaults()
            input_args = {
                name: value for name, value in bound.arguments.items() if name != "ctx"
            }
            input_payload = to_jsonable(input_args)

            try:
                result = fn(ctx, *args, **kwargs)
            except Exception as exc:
                ctx.session.add(
                    AgentTrace(
                        session_id=ctx.session_id,
                        step="tool_error",
                        tool_name=tool_name,
                        input=input_payload,
                        output={
                            "error": type(exc).__name__,
                            "message": str(exc)[:TRACE_MAX_STRING],
                        },
                        tokens_in=0,
                        tokens_out=0,
                    )
                )
                ctx.session.flush()
                raise

            ctx.session.add(
                AgentTrace(
                    session_id=ctx.session_id,
                    step="tool_call",
                    tool_name=tool_name,
                    input=input_payload,
                    output=to_jsonable(result),
                    tokens_in=0,
                    tokens_out=0,
                )
            )
            ctx.session.flush()
            return result

        wrapper.__signature__ = signature  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
