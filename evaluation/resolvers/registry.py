"""Refs: P3-baselines S3.7 D10 원칙2 원칙8 -- 이름 -> 팩토리 방식 표.

P4 러너가 `for name in ALL_METHODS: resolver = get_resolver(name, **kw)` 한
줄로 네(결정 C 로 다섯) 방식을 같은 데이터에 돌린다. 이 표가 있어야
"동일 데이터·동일 지표"(eval-harness §3)가 코드 수준에서 성립한다.

## 이름 문자열은 계약이다 (P4 인계 4)

여기 등록되는 이름이 `reports/metrics.json` 의 **키**가 되고
`MentionDecision.method` 로 그대로 나간다. 이름을 바꾸면 P4 산출물 스키마가
바뀐다. 예약된 다섯 이름(등록은 각 단위가 한다):

- `proposed`        -- 제안 4단계 하이브리드 어댑터(U2, `app.er.resolve`)
- `exact_raw`       -- 베이스라인 1a 문자열 완전일치, 공백·대소문자만 정리(U3, 결정 C(iii))
- `exact_norm`      -- 베이스라인 1b 완전일치 + `app.er.dictionary.normalize()`(U3, 결정 C(iii))
- `embedding_only`  -- 베이스라인 2 임베딩 단독(U4, `search_candidates` + `band_for`)
- `llm_single`      -- 베이스라인 3 LLM 단일 프롬프트(U5, 결정 E(ii))

U1 시점의 `RESOLVERS` 는 **빈 표**다. 자리표시자를 넣지 않는다 -- 비어
있는 표가 "아직 아무 방식도 구현되지 않았다"는 사실을 정직하게 말한다
(원칙8). 각 방식 모듈이 import 될 때 `register()` 로 자기를 올린다.

## `ALL_METHODS` 는 등록 순서를 유지한다 (그리고 동적이다)

`dict` 는 삽입 순서를 보존하므로 `ALL_METHODS` = `tuple(RESOLVERS)` 이고,
등록 순서 = `evaluation/resolvers/__init__.py` 가 방식 모듈을 import 하는
순서다. 이 값은 **모듈 속성 접근 시점에 계산된다**(PEP 562 `__getattr__`)
-- 그래서 `from evaluation.resolvers import ALL_METHODS` 는 그 순간의
**스냅샷을 이름에 묶는다**. 패키지 `__init__` 이 방식 모듈을 모두 import 한
뒤에 읽으면 완전한 목록이므로 P4 러너는 그대로 써도 되지만, 런타임에
추가 등록이 일어나는 코드(테스트 등)는 `registry.ALL_METHODS` 처럼
**속성으로** 읽어야 한다.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from evaluation.resolvers.base import DECISIONS, Resolver

if TYPE_CHECKING:  # 정적 분석기에게만 타입을 알린다(값은 `__getattr__` 이 만든다).
    ALL_METHODS: tuple[str, ...]

__all__ = ["RESOLVERS", "register", "get_resolver", "ALL_METHODS", "DECISIONS"]

#: 이름 -> 팩토리. 팩토리는 `Resolver` 를 돌려주는 아무 호출 가능 객체다
#: (클래스 자체 또는 `functools.partial`). 인자(`judge=`·스텁 클라이언트
#: 등)는 `get_resolver(name, **kw)` 가 그대로 넘긴다.
RESOLVERS: dict[str, Callable[..., Resolver]] = {}


def register(
    name: str,
    factory: Callable[..., Resolver] | None = None,
) -> Any:
    """방식을 표에 올린다. 두 형태를 모두 지원한다::

        @register("exact_raw")
        class ExactRawResolver: ...

        register("exact_norm", make_exact_norm)

    데코레이터 형태는 **원래 객체를 그대로 돌려준다**(클래스가 감싸지지
    않는다). 같은 이름을 두 번 올리면 `ValueError` -- 조용한 덮어쓰기는
    `metrics.json` 의 키가 가리키는 구현을 바꿔 버려서, 어느 방식의
    수치인지 알 수 없게 된다(원칙8).

    테스트가 임시로 등록할 때는 `RESOLVERS.copy()` 로 스냅샷을 떠 두었다가
    `RESOLVERS.clear(); RESOLVERS.update(snapshot)` 로 되돌린다.
    """

    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"register: name must be a non-empty str (got {name!r})")

    def _add(f: Callable[..., Resolver]) -> Callable[..., Resolver]:
        if not callable(f):
            raise TypeError(f"register({name!r}): factory must be callable (got {f!r})")
        if name in RESOLVERS:
            raise ValueError(
                f"register: {name!r} is already registered "
                f"({RESOLVERS[name]!r}) -- 이름은 metrics.json 의 키다(P4 인계 4)"
            )
        RESOLVERS[name] = f
        return f

    if factory is None:
        return _add
    return _add(factory)


def get_resolver(name: str, /, **kwargs: Any) -> Resolver:
    """이름으로 방식 하나를 만든다. 알 수 없는 이름이면 **등록된 이름
    목록을 담은** `KeyError` 를 던진다 -- P4 러너가 오타를 조용히 건너뛰고
    한 방식이 빠진 채 비교표를 만드는 일을 막는다(원칙8).

    첫 인자는 **위치 전용**(`/`)이다 -- 팩토리가 `name=` 을 인자로 받는
    경우(`get_resolver("exact_raw", name="exact_raw")`)에 이름이 충돌해
    `TypeError: got multiple values for argument 'name'` 이 나기 때문이다
    (U1 테스트에서 실제로 발견).

    `kwargs` 는 팩토리에 그대로 넘어간다(예: `judge=FakeJudge(...)`,
    스텁 LLM 클라이언트). 팩토리가 `resolve_mention` 이 없는 객체를
    돌려주면 `TypeError` 다 -- 계약 위반은 호출 시점이 아니라 생성 시점에
    드러나는 편이 낫다.
    """

    if name not in RESOLVERS:
        registered = ", ".join(RESOLVERS) if RESOLVERS else "(등록된 방식 없음)"
        raise KeyError(
            f"get_resolver: unknown resolver name {name!r}. "
            f"등록된 방식: [{registered}]"
        )
    resolver = RESOLVERS[name](**kwargs)
    if not callable(getattr(resolver, "resolve_mention", None)):
        raise TypeError(
            f"get_resolver({name!r}): factory returned an object without "
            f"resolve_mention() -- Resolver 계약 위반 ({resolver!r})"
        )
    return resolver


def __getattr__(attr: str) -> Any:
    """`ALL_METHODS` 를 접근 시점에 계산한다(PEP 562, 모듈 docstring 참조)."""
    if attr == "ALL_METHODS":
        return tuple(RESOLVERS)
    raise AttributeError(f"module {__name__!r} has no attribute {attr!r}")


def __dir__() -> list[str]:
    return sorted([*globals().keys(), "ALL_METHODS"])
