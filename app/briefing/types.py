"""Refs: P6-briefing S3.6 R12 원칙9 -- U1 골격(결과 타입 + trace 어휘 +
금지 표현 목록 + `Notifier`/`NullNotifier`). 도는 로직은 없다.

## 이 모듈이 하지 않는 것

- 대상 선정·패턴 재계산·문장 생성·실행 로직을 담지 않는다
  (`app/briefing/select.py`·`inputs.py`·`compose.py`·`run.py`는 각각
  U2·U3·U4·U5 몫, 01-plan "산출물" 절).
- DB(SQLAlchemy 모델)·LLM·임베딩을 import 하지 않는다 -- 이 모듈은
  순수 데이터클래스·상수뿐이다(`app/memory/types.py` 와 같은 관례).
  `Notifier.notify()`/`NullNotifier.notify()` 의 `schedule` 인자는
  실제로는 `app.db.models.Schedule` 이지만, 이 모듈에서는 `Any` 로만
  적어 DB 의존을 피한다 -- 실제 호출부(U5 `run.py`)가 구체 타입을 안다.

## 이 모듈이 고정하는 것

- `BriefingInput` -- `build_briefing_input(ctx, schedule)`(U3)의 반환
  모양. 패턴 재계산(결정 K)·`get_briefing` 자료 중 결정 F 로 정리한
  사실(`used_facts`/`excluded_facts`)·결정 G 의 근거 원문 조회 결과를
  담는다. 필드는 U3 가 실제 조립 로직을 쓸 때 채우며, 지금은 모양만
  고정한다(값 형식은 `to_dict()` 가 JSON 으로 직렬화 가능함을 보장하는
  선에서만 고른다 -- 세부 키 이름은 U3 03-log 에서 확정될 수 있다).
- `ComposedBriefing`/`BriefingLine`/`Suggestion` -- `BriefingComposer.
  compose(...)`(U4)의 반환 모양이자 결정 D 권장 구조화 출력 스키마
  (`{pattern_sentences, lines, suggestion}`) 그대로다. `basis` 는
  `{"fact_keys": [...], "event_ids": [...]}` 모양의 평범한 dict 로 둔다
  -- 검증기(U4 `validate_briefing()`)가 이 모양을 강제하며, 이 모듈
  자체는 구조를 검사하지 않는다(로직 없음). `tokens_in`/`tokens_out`/
  `provider`/`model` 은 U4 가 이 골격에 더한 필드다(U1 03-log "필드가
  부족하면 그 단위 03-log 에 남긴다" 규약, `app/memory/types.py::
  Extraction`/`PromotionResult` 와 같은 이유) -- `compose()` 가 직접
  `ComposedBriefing` 을 반환하므로(승격의 `Extraction`→`PromotionResult`
  처럼 감싸는 중간 타입이 없다), 생성기 사용량을 실어 나를 자리가 이
  타입 자체여야 한다. `to_dict()` 는 **이 네 필드를 싣지 않는다** --
  결정 D 스키마 3 키(`pattern_sentences`/`lines`/`suggestion`) 그대로
  유지해 API 응답·`briefing_compose` trace `output` 양쪽에서 같은 모양을
  재사용할 수 있게 한다(U5 가 `provider`/`model`/토큰은 trace `output`
  의 다른 키 `llm{provider, model}`로 따로 옮겨 담는다, 결정 I).
- `BriefingRunResult` -- `run_briefings(...)`(U5)의 반환 타입이자
  `POST /briefings/run`(U6) 응답·`briefing_run` trace output(결정 I)의
  바탕.
- `BRIEFING_TRACE_TOOL_NAME`("briefing")·step 3종(`briefing_run`/
  `briefing_compose`/`briefing_error`, 결정 I) -- `agent_traces.
  tool_name`/`.step` 의 단일 출처. `app.agent.types.LOOP_TRACE_TOOL_NAME`
  ("agent")·`app.er.types.ER_TRACE_TOOL_NAME`("er")·`app.memory.types.
  MEMORY_TRACE_TOOL_NAME`("memory") 와 같은 층위이고 겹치지 않는다.
- `BRIEFING_FORBIDDEN_EXPRESSIONS` -- 원칙7 경계(제안은 기록된 사실의
  한 줄 행동 제안, 감정·고민 대화 금지)를 지키는 검증기(U4)의 금지
  표현 목록 초안(01-plan 결정 E(ii)). 완전하지 않다 -- 돌려 말하면
  통과한다(01-plan 193행 한계, P10-final-eval 인계).
- `Notifier` Protocol·`NullNotifier`(결정 J(i)) -- 푸시를 보낼 자리만
  둔다. `NullNotifier` 는 아무것도 보내지 않고 항상 `"not_configured"`
  를 돌려준다. P7-push 가 이 자리에 `WebPushNotifier` 를 끼운다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

# ---------------------------------------------------------------------------
# 브리핑 입력 (U3 `build_briefing_input()` 이 반환. 로직은 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BriefingInput:
    """`build_briefing_input(ctx, schedule)`(U3)의 반환 타입. `used_facts`/
    `excluded_facts`/`recent_events` 는 전부 평범한 dict 목록이다(결정 F
    사실 정리·결정 G 근거 원문 조회 결과를 U3 가 채운다 -- 이 모듈은
    형식을 강제하지 않는다, 로직 없음)."""

    schedule_id: int
    person_id: int
    scheduled_at: datetime
    title: str
    pattern_trace_id: int | None = None
    used_facts: list[dict[str, Any]] = field(default_factory=list)
    excluded_facts: list[dict[str, Any]] = field(default_factory=list)
    recent_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """`@traced`(`app.tools.context.to_jsonable`)가 이 메서드를
        우선 쓴다 -- `PatternResult.to_dict()` 와 같은 이유."""

        return {
            "schedule_id": self.schedule_id,
            "person_id": self.person_id,
            "scheduled_at": self.scheduled_at.isoformat(),
            "title": self.title,
            "pattern_trace_id": self.pattern_trace_id,
            "used_facts": [dict(fact) for fact in self.used_facts],
            "excluded_facts": [dict(fact) for fact in self.excluded_facts],
            "recent_events": [dict(event) for event in self.recent_events],
        }


# ---------------------------------------------------------------------------
# 브리핑 문장 생성 결과 (U4 `BriefingComposer.compose()` 가 반환. 로직은
# 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BriefingLine:
    """요약 줄 하나(패턴 문장 제외) -- 결정 D 권장 스키마
    `lines:[{text, basis:{fact_keys:[], event_ids:[]}}]`. `basis` 는
    `{"fact_keys": [...], "event_ids": [...]}` 모양의 평범한 dict 다."""

    text: str
    basis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "basis": dict(self.basis)}


@dataclass(frozen=True)
class Suggestion:
    """한 줄 행동 제안(원칙7) -- 결정 D 권장 스키마
    `suggestion:{text, basis:{fact_keys:[], event_ids:[]}} | null`."""

    text: str
    basis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "basis": dict(self.basis)}


@dataclass(frozen=True)
class ComposedBriefing:
    """`BriefingComposer.compose(briefing_input)`(U4)의 반환 타입 --
    결정 D 권장 구조화 출력 스키마 그대로(`{pattern_sentences, lines,
    suggestion}`). `pattern_sentences` 는 `{"key": str, "sentence": str}`
    dict 목록이다 -- 패턴 판정은 규칙이 이미 끝낸 값이고 LLM 은
    문장화만 하므로(원칙6), 이 모듈은 그 값을 별도 타입으로 감싸지
    않는다."""

    pattern_sentences: list[dict[str, Any]] = field(default_factory=list)
    lines: list[BriefingLine] = field(default_factory=list)
    suggestion: Suggestion | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    provider: str | None = None
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """결정 D 스키마 3 키 그대로(`tokens_in`/`tokens_out`/`provider`/
        `model` 은 싣지 않는다 -- 모듈 docstring 참고)."""

        return {
            "pattern_sentences": [dict(item) for item in self.pattern_sentences],
            "lines": [line.to_dict() for line in self.lines],
            "suggestion": self.suggestion.to_dict() if self.suggestion is not None else None,
        }

    def trace_tokens(self) -> tuple[int, int]:
        """`app/tools/context.py::traced` docstring "성공" 절의 훅과 같은
        이름 관례(U4 가 직접 `@traced` 로 감싸지는 않지만, U5 가 이
        메서드를 호출해 `briefing_compose` trace 의 `tokens_in`/
        `tokens_out` 을 채운다 -- `Extraction`/`PromotionResult` 와 같은
        이유)."""

        return (self.tokens_in, self.tokens_out)


# ---------------------------------------------------------------------------
# 실행 결과 (U5 `run_briefings()` 가 반환. 로직은 아직 없음)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BriefingRunResult:
    """`run_briefings(...)`(U5)의 반환 타입이자 `POST /briefings/run`
    (U6) 응답·`briefing_run` trace output(결정 I)의 바탕. `briefings`/
    `skipped` 항목 하나하나는 평범한 dict 다 -- U6 가 응답 모양으로
    그대로 쓸 수 있게 한다.

    **U6 추가 -- `session_id`**: 이 실행이 남긴 모든 trace 가 공유하는
    `"briefing:<uuid4>"`(결정 I, `run.py` 의 `run_ctx.session_id`)다. U5
    시점에는 이 값을 돌려줄 필요가 없어(테스트가 `tool_name`+`step` 으로
    trace 를 조회했다, `app/briefing/run.py` 모듈 docstring "실행 하나의
    session_id" 절) 필드가 없었지만, `POST /briefings/run` 응답의
    `run_id`(위임 프롬프트 요구)가 바로 이 값이어야 그 실행이 남긴
    trace 를 사용자가 되짚을 수 있다(원칙9) -- 그래서 U6 가 이 필드를
    더한다. 기존 호출부(U5 테스트)는 `to_dict()` 를 쓰지 않고 DB 조회로
    trace 를 찾으므로 이 추가로 깨지지 않는다(U6 03-log 확인)."""

    trigger: str
    now: datetime
    session_id: str
    briefings: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    errors: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger": self.trigger,
            "now": self.now.isoformat(),
            "session_id": self.session_id,
            "briefings": [dict(item) for item in self.briefings],
            "skipped": [dict(item) for item in self.skipped],
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# agent_traces 어휘 (결정 I -- tool_name 고정 + step 3종)
# ---------------------------------------------------------------------------

#: `agent_traces.tool_name` -- 브리핑 계층이 남기는 모든 행의 값(결정 I).
#: `app.agent.types.LOOP_TRACE_TOOL_NAME`("agent")·`app.er.types.
#: ER_TRACE_TOOL_NAME`("er")·`app.memory.types.MEMORY_TRACE_TOOL_NAME`
#: ("memory") 와 같은 층위이며 겹치지 않는다.
BRIEFING_TRACE_TOOL_NAME = "briefing"

#: 실행 단계 -- 실행(주기 한 번 또는 수동 한 번) 끝에 1행(결정 I, U5).
#: tokens 는 항상 0(이 step 자체는 LLM 을 부르지 않는다).
STEP_BRIEFING_RUN = "briefing_run"

#: 생성 단계 -- 일정마다 1행(결정 I, U5). tokens in/out 은 생성기
#: 사용량(템플릿 대체면 0/0).
STEP_BRIEFING_COMPOSE = "briefing_compose"

#: 오류 전용 -- 일정 단위 실패 1행(결정 I, U5, 세이브포인트 롤백 뒤
#: 바깥 트랜잭션에서 기록). 정상 진행 step 이 아니므로 아래
#: `BRIEFING_TRACE_STEPS` 에는 포함하지 않는다(`app.memory.types.
#: STEP_MEMORY_ERROR` 와 같은 관례).
STEP_BRIEFING_ERROR = "briefing_error"

#: 정상 진행 step 2종(결정 I 나열 순서 그대로 -- 실행 → 생성).
BRIEFING_TRACE_STEPS: tuple[str, ...] = (STEP_BRIEFING_RUN, STEP_BRIEFING_COMPOSE)

# ---------------------------------------------------------------------------
# 금지 표현 목록 (01-plan 결정 E(ii) 초안 -- 원칙7 경계의 보조 방어)
# ---------------------------------------------------------------------------

#: 검증기(U4)가 제안과 요약 줄에서 거부하는 감정·고민·상담 관련 표현 초안. 이
#: 목록은 완전하지 않다(01-plan 193행 "돌려 말하면 통과한다") -- 1차
#: 방어는 프롬프트의 "근거 필수" 지시이고 이 목록은 보조다. 값을
#: 바꾸려면 코드를 고친다(환경변수로 덮지 않는 코드 상수, 원칙8).
BRIEFING_FORBIDDEN_EXPRESSIONS: tuple[str, ...] = (
    "기분",
    "감정",
    "위로",
    "고민",
    "상담",
    "스트레스",
    "마음이",
    "마음을",  # U4 실 LLM 재확인 -- "팀장님의 마음을 이해하고 배려하는 대화" 가 통과했다
    "배려",  # 같은 사례. "마음" 전체는 "마음에 드는 식당" 같은 정상 문장까지 막으므로 조사까지 붙여 좁게 잡는다
    "힘드",
    "힘들",  # U4 실 LLM 확인 -- "힘드" 는 "힘드셨" 만 잡고 "힘들어"·"힘들 거예요" 는 놓쳤다
    "우울",
    "속상",
    "서운",
)

# ---------------------------------------------------------------------------
# 푸시 발송 자리 (결정 J(i) -- P7-push 가 Notifier 구현체를 끼운다)
# ---------------------------------------------------------------------------


class Notifier(Protocol):
    """푸시 발송 자리(결정 J). `notify()` 는 그 일정의 생성된 브리핑을
    어딘가로 보내고 상태 문자열을 돌려준다(`"not_configured"`/P7-push 가
    정할 그 밖의 어휘). **인자에 원문(`raw_utterance`)을 담지 않는다**
    (01-plan "지킬 불변식" -- 응답·`Notifier` 인자에 원문을 싣지 않는다).
    `schedule` 타입은 실제로 `app.db.models.Schedule` 이지만 이 모듈은
    DB 를 import 하지 않으므로 `Any` 로만 적는다(모듈 docstring)."""

    def notify(self, schedule: Any, composed: ComposedBriefing) -> str: ...


@dataclass(frozen=True)
class NullNotifier:
    """기본 `Notifier`(결정 J(i)) -- 아무것도 보내지 않고 항상
    `"not_configured"` 를 돌려준다. P7-push 이전까지 이 자리를 채운다
    (`app/memory/extract.py::FakeFactExtractor` 와 달리 이 타입은
    테스트 전용이 아니라 **운영 기본값**이다 -- 01-plan 결정 J)."""

    def notify(self, schedule: Any, composed: ComposedBriefing) -> str:
        return "not_configured"
