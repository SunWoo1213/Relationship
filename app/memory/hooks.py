"""Refs: P6-memory S3.5 R8 R11 원칙9 -- U6 루프 연결. `after_record(ctx,
person_ids, extractor)` 하나만 정의한다. `app/agent/loop.py::_record()` 가
`loop_record` trace 가 끝난 뒤 한 줄로 이 함수를 부른다(01-plan 72행) --
`run_turn`/`resume_turn` 이 모두 `_record()` 를 지나므로 두 경로가 이
한 자리에서 덮인다.

## ★ R-10 해소 -- `extractor` 지연 해소를 "지연 프록시"로 한다

02-plan-verify 권고 R-10(198행)은 "`extractor_from_env()` 호출을
`promote_person` 안, 미승격 판정 뒤에 두어라" 고 적었다. 그런데 U5 가 이미
커밋한 `promote_person(ctx, person_id, extractor)`(`app/memory/promote.py`)
는 `extractor` 를 **필수** 인자로 받고, 트리거 판정도 그 함수 안에서
끝낸다 -- 그 함수 자신은 "주어진 extractor 를 부를지 말지"만 정할 뿐,
"extractor 가 없으면 지금 막 만든다"는 결정을 할 자리가 시그니처에 없다
(`FactExtractor`, `FactExtractor | None` 이 아니다). U5·U4(`extractor`
필수 인자, `validate_extraction`/`FakeFactExtractor`)를 고치지 않기 위해
(02-plan-verify 가 이미 "그러면 U5 코드와 01-plan 71행 문장을 함께
고쳐야 하고 U5 테스트 15건에 영향이 갈 수 있다"고 적은 대가), **이
모듈이 R-10 의 의도**("트리거가 안 걸리면 추출기를 아예 만들지 않는다")
**를 다른 자리에서 지킨다** -- `_LazyFactExtractor` 는 `FactExtractor`
Protocol(`.extract(person, existing_facts, events) -> Extraction`)을
만족하는 얇은 래퍼이고, `extract()` 가 **처음 불릴 때만**
`extractor_from_env()` 로 실제 추출기를 해소해 재사용한다.
`promote_person`/`_promote_and_trace` 는 미승격 이벤트가
`MEMORY_PROMOTE_MIN_EVENTS` 이상일 때만 `extractor.extract()` 를 부르므로
(`app/memory/promote.py::_promote_and_trace`), 트리거가 안 걸리는(대부분의)
턴은 이 프록시가 끝까지 `extractor_from_env()` 를 부르지 않는다 --
`run_turn`/`resume_turn` 을 `extractor` 없이 8곳에서 부르는 기존 회귀
4파일과, API 키가 없는 테스트 환경이 그대로 통과하는 이유다(R-10 근거는
02-plan-verify fact-checks-2 §7~§11, 같은 근거를 03-log U6 항목에도
옮긴다). `app.api.deps.get_fact_extractor()` 도 `get_proposer()`/
`get_judge()` 와 같은 모양으로 운영 경로에 항상 `None` 을 돌려주고, 이
모듈이 `None` 을 받으면 `_LazyFactExtractor()` 로 감싼다.

## 실패 격리 (01-plan 72행)

이번 턴에 이벤트가 저장된 인물 **전부**를 `ctx.session.begin_nested()`
세이브포인트 하나로 감싼다(패턴 → 승격 순서, 결정 C-1). 그 안에서
`sqlalchemy.exc.SQLAlchemyError` 가 아닌 예외가 나면(공급자 오류·
`ToolError` 등) 세이브포인트만 롤백해 이번 호출이 flush 한 모든 행(업무
데이터가 아니라 이 모듈이 만든 것만 -- `memory_pattern`/`memory_promote`
trace, 그 안에서 `@traced` 가 남긴 `tool_error` 행, `PersonFact`/
`FactSource` 변경)을 지운다. **롤백이 끝난 뒤** 바깥(아직 커밋되지 않은
요청 트랜잭션)에서 `memory_error` 행 하나만 새로 남긴다 -- 안에서 쓰면
롤백과 함께 사라진다(01-plan 72행 "그래야 판정 16행의 memory_error 가
남는다"). `SQLAlchemyError` 는 삼키지 않고 그대로 올린다(`app/api/routes.py`
의 R-3 규약과 같은 방향 -- 그 바깥 세이브포인트/`get_session()` 이 대신
처리한다).

이 함수 자신은(`SQLAlchemyError` 를 제외하면) **절대 예외를 올리지
않는다** -- 그래야 `_record()` 를 부른 `run_turn`/`resume_turn` 이 정상
반환해 라우트가 200 으로 응답하고, 이 함수가 세이브포인트를 열기 **전에**
`_record_impl` 이 이미 flush 해 둔 이벤트(`add_event`)를 잃지 않는다.

`person_ids` 가 비어 있으면(이번 턴에 저장된 이벤트가 없음) 세이브포인트
조차 열지 않는다."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.exc import SQLAlchemyError

from app.db.models import AgentTrace
from app.memory.extract import ExistingFact, Extraction, ExtractEvent, FactExtractor, extractor_from_env
from app.memory.patterns import detect_patterns
from app.memory.promote import promote_person
from app.memory.types import MEMORY_TRACE_TOOL_NAME, STEP_MEMORY_ERROR
from app.tools.context import ToolContext

#: `memory_error` output.stage 어휘(결정 F "memory_error: {person_id,
#: stage, error}"). `detect_patterns` 에서 실패하면 "pattern", `promote_
#: person` 에서 실패하면 "promote".
_STAGE_PATTERN = "pattern"
_STAGE_PROMOTE = "promote"


class _LazyFactExtractor:
    """`extractor=None` 일 때 `after_record` 가 대신 넣는 지연 프록시(★
    R-10 해소, 모듈 docstring 참고). `extract()` 가 **처음 불릴 때만**
    `extractor_from_env()` 로 실제 추출기를 만들어 이후 호출에 재사용한다
    -- 트리거가 안 걸리는 호출(`promote_person` 이 `extract()` 를 아예
    부르지 않는 경우)은 이 프록시가 끝까지 실제 추출기를 만들지 않는다."""

    def __init__(self) -> None:
        self._resolved: FactExtractor | None = None

    def extract(
        self,
        person: str,
        existing_facts: Sequence[ExistingFact],
        events: Sequence[ExtractEvent],
    ) -> Extraction:
        if self._resolved is None:
            self._resolved = extractor_from_env()
        return self._resolved.extract(person, existing_facts, events)


def _record_memory_error(ctx: ToolContext, *, person_id: int, stage: str, error: Exception) -> None:
    """`memory_error` trace 행 1개(결정 F). **세이브포인트 롤백이 끝난
    뒤** 바깥 트랜잭션에서만 부른다(모듈 docstring "실패 격리" 참고) --
    안에서 add()+flush() 하면 그 행도 롤백과 함께 사라진다. output 은
    `{person_id, stage, error}` 뿐이다 -- 프롬프트·공급자명·키 원문은
    담지 않는다(security §1, `error` 는 `type(error).__name__` 만)."""

    payload = {"person_id": person_id, "stage": stage, "error": type(error).__name__}
    ctx.session.add(
        AgentTrace(
            session_id=ctx.session_id,
            step=STEP_MEMORY_ERROR,
            tool_name=MEMORY_TRACE_TOOL_NAME,
            input={"person_id": person_id, "stage": stage},
            output=payload,
            tokens_in=0,
            tokens_out=0,
        )
    )
    ctx.session.flush()


def after_record(
    ctx: ToolContext,
    person_ids: Sequence[int],
    extractor: FactExtractor | None = None,
) -> None:
    """01-plan U6 -- 루프 기록 단계(`_record()`) 의 `loop_record` trace 가
    끝난 뒤 부르는 메모리 계층 진입점. 이번 턴에 `add_event` 가 실제로
    실행된 인물마다 ① `detect_patterns` ② `promote_person` 순서로
    돈다(결정 C-1). `extractor` 가 `None` 이면(운영 경로) `_LazyFactExtractor`
    로 감싼다(★ R-10 해소, 모듈 docstring 참고). 실패 격리는 모듈
    docstring "실패 격리" 절 그대로다."""

    if not person_ids:
        return

    resolved_extractor: FactExtractor = extractor if extractor is not None else _LazyFactExtractor()

    person_id = person_ids[0]
    stage = _STAGE_PATTERN
    failure: Exception | None = None
    try:
        with ctx.session.begin_nested():
            for person_id in person_ids:
                stage = _STAGE_PATTERN
                detect_patterns(ctx, person_id)
                stage = _STAGE_PROMOTE
                promote_person(ctx, person_id, resolved_extractor)
    except SQLAlchemyError:
        raise
    except Exception as exc:  # noqa: BLE001 -- 의도적으로 넓게 잡는다(모듈 docstring "실패 격리")
        failure = exc

    if failure is not None:
        _record_memory_error(ctx, person_id=person_id, stage=stage, error=failure)
