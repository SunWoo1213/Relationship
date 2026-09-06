"""Refs: P2-tools S3.2 원칙9 -- ToolContext 실행 맥락 + @traced 관측성 데코레이터.

## embedder 타입 결정 (U3 에서 좁힘 -- U2 의 TODO 해소)
`ToolContext.embedder` 는 `app.embedding.EmbeddingProvider | EmbedderCallable
| None` 이다. U2 시점에는 `app/embedding.py` 가 아직 없어 로컬 콜러블 타입
별칭만 두었으나(F-0010e6 와 별개 기록), U3 가 그 모듈을 만들면서 이 자리를
좁힌다. 두 형태를 모두 받는 이유는 `tests/conftest.py` 의 `fake_embedder`
(평범한 콜러블)와 향후 P3-er 가 꽂을 `OpenAIEmbeddingProvider`(`.embed()`
메서드를 가진 객체) 를 모두 그대로 받기 위해서다 -- 실제 사용 시점(예:
`search_person`)에서 `app.embedding.as_provider(ctx.embedder)` 로 정규화해
`EmbeddingProvider` 하나로 통일한다. `ToolContext` 자체는 정규화하지
않는다 -- 정규화 시점을 앞당기면 `embedder=None` 인지 아닌지를 툴마다
`as_provider` 를 거쳐야 판별하게 되어 "임베딩 단계를 건너뛴다"는 신호
(`None`)가 흐려진다.

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
우회(예: 별도 커넥션 즉시 커밋)로 고치지 않는다. **이번 단위(P3-er U1)에서도
이 한계는 그대로 유지한다 -- 별도 커넥션 여부는 여전히 P5-loop 의 결정이다.**

## trace 행 id 회수 (P3-er U6, 결정4 "trace 행의 갱신 주체")
`app/er/pipeline.py` 의 `resolve()` 는 `agent_traces` 행 하나를 쓰고 그 행의
id 를 `Resolution.trace_id` 로 돌려줘야 한다(`apply_resolution` 이 나중에
같은 행을 부분 갱신하는 열쇠). `@traced` 는 성공 행을 flush 한 **뒤에만**
자동증가 PK 를 알 수 있고, 그 시점은 감싸인 함수(`fn`)가 이미 반환값을
만들어 돌려준 다음이다 -- 반환값 생성 시점에는 아직 행 id 가 없다. 이를
위해 `ToolContext` 에 `last_trace_id` 필드(기본 `None`)를 추가하고, `traced()`
의 성공 경로가 flush 직후 `ctx.last_trace_id = trace_row.id` 를 채운다. 이
필드는 **모든** `@traced` 호출(6개 기존 툴 포함)에서 갱신되지만, ER 이외의
호출자는 이 값을 읽지 않으므로 동작에 영향이 없다(하위 호환, `traced()` 의
인자·시그니처는 그대로). `resolve()` 는 감싸인 내부 함수 호출 직후
`ctx.last_trace_id` 를 읽어 `dataclasses.replace(result, trace_id=...)` 로
최종 `Resolution` 을 만든다(U6, `app/er/pipeline.py`) -- `Resolution` 자체는
여전히 불변(frozen) dataclass이며 이 필드에 직접 `object.__setattr__` 하지
않는다.

## F-ca12ad -- flush 실패 뒤 tool_error 기록 실패를 조용히 포기한다 (결정7)
P2 시점 코드는 except 경로에서 실패한 flush 뒤 **같은 세션에** tool_error 를
`add()` + `flush()` 했다. flush 가 DB 오류(예: `person_aliases.embedding` 차원
불일치)로 실패하면 그 세션은 SQLAlchemy 가 "이 트랜잭션은 이미 롤백이
필요하다"고 표시한 상태가 되고, 같은 세션에 다시 `flush()` 하면
`sqlalchemy.exc.PendingRollbackError` 가 새로 발생해 **원래 예외를 가리고
호출자에게 그 대신 올라간다**(evidence
`docs/wiki/packages/P2-tools/evidence/20260905-1942-review-tool-error-probe.txt`).
이를 고치기 위해 tool_error 기록 시도를 `ctx.session.begin_nested()`
세이브포인트 **안에서만** 한다 -- 세이브포인트 자체를 열지 못하거나(세션이
이미 무효) 그 안의 `flush()` 가 다시 실패하면 **조용히 포기하고 원래 예외를
`raise`(인자 없는 bare raise)로 그대로 올린다** -- `exc.__context__`/
`__traceback__` 을 새로 바꾸지 않는다. `session.rollback()` 은 호출하지
않는다 -- 호출자가 아직 커밋하지 않은 정상 작업(같은 트랜잭션의 다른 변경)
까지 지워 버리기 때문이다. 이 경로에서는 tool_error 행이 아예 생기지 않을
수 있다(세이브포인트도 못 여는 경우) -- "원래 예외를 절대 가리지 않는다"가
"오류 trace 를 항상 남긴다"보다 우선이다(원칙1 의 비대칭 비용과 같은 방향).
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
from app.embedding import EmbedderCallable, EmbeddingProvider
from app.settings import app_user_id

#: agent_traces.input/output 에 들어가는 개별 문자열 값의 최대 길이. 초과분은
#: 잘라내고 "…[truncated N chars]" 표식을 붙인다(N = 잘려나간 문자 수).
TRACE_MAX_STRING = 2000

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
    embedder: EmbeddingProvider | EmbedderCallable | None = None
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    confirmed_question_id: int | None = None
    last_trace_id: int | None = None


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


def traced(tool_name: str, step: str = "tool_call") -> Callable[[F], F]:
    """`agent_traces` 기록 데코레이터(원칙9). 대상 함수 시그니처는
    `(ctx, *args, **kwargs)`.

    `step`(P3-er U1 확장): 성공 행의 `step` 값. 기존 툴 호출(`@traced("search_person")`
    처럼 인자 하나만 준 호출)은 기본값 `"tool_call"` 그대로 동작한다 -- 이
    확장은 하위 호환을 깨지 않는다. `app/er/pipeline.py`(U6)는
    `@traced("er", step="er_resolve")` 처럼 두 번째 인자로 ER 단계 이름을 쓴다.

    성공: `step`(인자, 기본 `"tool_call"`), `input`=ctx 를 뺀 인자의 이름→값
    매핑을 `to_jsonable` 로 변환한 것, `output`=반환값을 `to_jsonable` 로
    변환한 것(반환값이 `*Out` 이면 사실상 `to_dict()`). `tokens_in`/
    `tokens_out`: 반환값이 `trace_tokens() -> tuple[int, int]` 메서드를
    제공하면 그 결과를 그대로 쓰고(예: ER 판정 결과가 LLM 사용량을 실어
    돌려줄 때), 없으면 `(0, 0)`(P2 툴처럼 LLM 호출이 없는 경우).

    성공 행 flush 직후 `ctx.last_trace_id` 에 그 행의 PK 를 남긴다(P3-er U6
    확장, 모듈 docstring "trace 행 id 회수" 절) -- `resolve()` 가 이 값으로
    `Resolution.trace_id` 를 채운다. 반환값 자체는 바꾸지 않는다.

    예외: `step="tool_error"`(고정 -- 성공 행의 `step` 인자와 무관하다),
    `output={"error": 예외 클래스명, "message": str(e)[:TRACE_MAX_STRING]}`.
    이 기록은 `ctx.session.begin_nested()` 세이브포인트 **안에서만** 시도한다
    -- 세이브포인트를 열지 못하거나 그 안의 flush 가 다시 실패하면(세션이
    이미 무효, F-ca12ad) **조용히 포기**하고 `session.rollback()` 을 부르지
    않은 채 원래 예외를 **bare `raise`** 로 그대로 올린다(`__context__`·
    `__traceback__` 불변, 모듈 docstring "F-ca12ad" 절·결정7 참고).

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
                try:
                    with ctx.session.begin_nested():
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
                except Exception:
                    # 세션이 이미 무효(F-ca12ad) -- tool_error 기록을 조용히
                    # 포기한다. 원래 예외(exc)를 덮지 않는 것이 우선이다.
                    # session.rollback() 은 호출하지 않는다(결정7).
                    pass
                raise

            tokens_in, tokens_out = 0, 0
            trace_tokens = getattr(result, "trace_tokens", None)
            if callable(trace_tokens):
                tokens_in, tokens_out = trace_tokens()

            trace_row = AgentTrace(
                session_id=ctx.session_id,
                step=step,
                tool_name=tool_name,
                input=input_payload,
                output=to_jsonable(result),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
            )
            ctx.session.add(trace_row)
            ctx.session.flush()
            ctx.last_trace_id = trace_row.id
            return result

        wrapper.__signature__ = signature  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
