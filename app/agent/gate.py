"""Refs: P5-loop S3.2 원칙1 원칙4 원칙9 -- U3 게이트(제안을 코드가 거른다,
L(iii) 의 안전장치).

## 이 모듈이 하는 일 (그리고 하지 않는 일)

인식 단계(U2 `propose.py`)가 만든 `Proposal.tool_calls[]` 는 **LLM 이 제안한
것일 뿐**이다. 이 모듈은 그 제안을 실행하기 전에 코드로 거른다 -- 실행
여부의 최종 판정은 이 모듈이지 LLM 이 아니다. `check()` 는 세션·LLM·DB 를
전혀 건드리지 않는 **순수 함수**다(테스트가 세션 없이 돈다, 01-plan U3).

이 모듈이 **하지 않는 것**(원칙1·2·4):
- 인물 해석(`resolve`/`apply_resolution`)을 부르지 않는다 -- "언급 문자열이
  누구인가"는 이 단계의 관심사가 아니다.
- 확신도를 계산·비교하지 않는다. 이 파일 어디에도 임계치·확신도를
  가리키는 영어 어휘를 쓰지 않는다(판정 표 6행) -- 설명이 필요하면
  한국어 "확신도"로 쓴다.
- 툴을 직접 부르지 않는다(`app.tools.*` 함수를 호출하는 코드가 이 모듈
  안에 없다) -- 통과한 제안을 실제로 실행하는 것은 U5(`loop.py`)의 일이다.

## 적용 순서 (①②④③⑤ -- ④가 ③보다 먼저)

01-plan 범위 절 28행: "④ 를 먼저 둬야 판정 표 19행의 `person_id_from_llm`
사유가 따로 남는다" -- `person_id` 를 먼저 걸러내지 않고 인자 스키마(③)를
먼저 돌리면 `person_id` 가 껴 있는 제안이 "미지 인자"로 뭉뚱그려져 `bad_args`
에 묻힌다. 그래서 이 모듈은 제안 하나마다 다음 순서로 딱 하나의 사유에서
멈춘다:

1. ① 화이트리스트 -- `name` 이 `app.tools.TOOL_NAMES`(툴 7종) 밖이면
   `unknown_tool`.
2. ② 호출 가능 집합 -- `name` 이 `search_person`/`ask_user`/`get_briefing`
   이면 `not_callable_by_llm`(오병합 방어는 ER 4단계 안에서만 일어나야
   하고, `get_briefing` 은 P6-briefing 의 몫이다).
3. ④ `person_id` 금지 -- `args` 에 `"person_id"` 키가 있으면 무조건
   `person_id_from_llm`. **LLM 경로에서 `person_id` 는 오직 `resolve()` →
   `apply_resolution()` 을 거쳐서만 얻는다** -- 이것이 L(iii) 의 핵심
   방어다.
4. ③ 인자 스키마 -- `inspect.signature(app.tools.<name>)`(`scripts/
   tools_check.py` 와 같은 출처)에서 루프가 주입하는 인자 셋(`ctx`·
   `person_id`·`raw_utterance`)을 빼고 `person`(언급 문자열)을 더한
   집합과 대조한다. 미지 인자·필수 누락·타입 위반·`add_event.type` 고정
   집합 위반은 `bad_args`. `raw_utterance` 를 준 제안은 (루프가 원문을
   주입하므로) 허용 집합에 없어 `bad_args` 가 된다(원문 덮어쓰기 없음).
   `update_person` 제안에 `display_name` 이 있으면 (다른 검사보다 먼저)
   `needs_confirmation`(D6).
5. ⑤ 상한 -- ①②④③ 을 지난 제안(통과 후보)에 결정 A(i) 4종 상한
   (`LOOP_MAX_MENTIONS`/`EVENTS`/`SCHEDULES`/`PROPOSALS`)을 적용한다.
   언급 = 통과 후보 중 `args["person"]` 서로 다른 값의 수, 이벤트 =
   `add_event` 통과 후보 수, 일정 = `add_schedule` 통과 후보 수(01-plan
   235행). 넘는 제안은 `limit` 로 거부되고 `stop_reason="limit"` 가
   된다.

`create_person` 제안은 위 다섯 관문을 모두 지나면 거부되지 않고 **버킷만
`hint_only`** 로 통과한다(D1 -- 실행은 재개 경로뿐, `app/agent/loop.py`
가 `relation_tag`/`hierarchy` 힌트로만 쓴다). 다른 여섯 툴은 `execute`
버킷이다.

## R-23 (이 단위에서 정한다) -- `scheduled_at`/`occurred_at` 미확정 표현

`add_event.occurred_at`·`add_schedule.scheduled_at` 은 시그니처상 필수
인자이지만, 이 모듈은 **값이 없거나(`None`) 아예 없는 것을 거부하지
않는다** -- 결정 K(i) "이벤트는 확정 못 하면 `now`, 일정은 확정 못 하면
`ask_user(kind="schedule")`" 를 실행할 수 있는 여지를 U5 에 남겨 둬야
하기 때문이다. 반면 **문자열인데 `datetime` 이 아닌 값**(U2
`_convert_datetime_args` 가 ISO 파싱에 실패해 문자열로 남긴 값)은 진짜
형식 오류이므로 `bad_args` 로 거부한다. 요약: `None`/누락 = "미확정"
(통과, U5 가 판단) · 문자열 그대로(파싱 실패) = `bad_args`(이 모듈이
판단). 인식 단계(U2)가 이미 `datetime` 으로 바꾼 값은 그대로 통과한다.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app import tools as app_tools
from app.agent.types import (
    BUCKET_EXECUTE,
    BUCKET_HINT_ONLY,
    AcceptedProposal,
    GateLimits,
    GateVerdict,
    Proposal,
    RejectedProposal,
)
from app.db.models import EVENT_TYPES, HIERARCHIES, RELATION_TAGS
from app.settings import (
    LOOP_MAX_EVENTS,
    LOOP_MAX_MENTIONS,
    LOOP_MAX_PROPOSALS,
    LOOP_MAX_SCHEDULES,
)

# ---------------------------------------------------------------------------
# 거부 사유 어휘 (이 모듈이 단일 출처, 01-plan 60행)
# ---------------------------------------------------------------------------

REASON_UNKNOWN_TOOL = "unknown_tool"
REASON_NOT_CALLABLE_BY_LLM = "not_callable_by_llm"
REASON_BAD_ARGS = "bad_args"
REASON_PERSON_ID_FROM_LLM = "person_id_from_llm"
REASON_NEEDS_CONFIRMATION = "needs_confirmation"
REASON_LIMIT = "limit"

#: 거부 사유 어휘 전체(테스트·trace 검증이 이 튜플로 어휘를 고정한다).
GATE_REJECTION_REASONS: tuple[str, ...] = (
    REASON_UNKNOWN_TOOL,
    REASON_NOT_CALLABLE_BY_LLM,
    REASON_BAD_ARGS,
    REASON_PERSON_ID_FROM_LLM,
    REASON_NEEDS_CONFIRMATION,
    REASON_LIMIT,
)

#: 루프가 주입하는 인자 셋의 단일 출처(01-plan 60행 "주입 인자: `ctx`·
#: `person_id`·`raw_utterance`", R-11). `_arg_spec()` 이 이 집합을 시그니처
#: 에서 뺀다.
INJECTED_ARGS: frozenset[str] = frozenset({"ctx", "person_id", "raw_utterance"})

#: ② 호출 가능 집합에서 뺀다 -- 이 셋은 LLM 이 직접 제안할 수 없다(오병합
#: 방어는 ER 4단계 안에서만, `get_briefing` 은 P6-briefing). `propose.py`
#: 의 `_LLM_NOT_CALLABLE` 은 프롬프트 안내용 사본일 뿐이고, 실제 강제의
#: 단일 출처는 이 상수다(모듈 docstring "① 적용 순서").
NOT_CALLABLE_BY_LLM: frozenset[str] = frozenset({"search_person", "ask_user", "get_briefing"})

#: `occurred_at`/`scheduled_at` -- 값이 없어도(`None`) ③ 에서 "필수 누락"
#: 으로 걸지 않는다(R-23, 위 모듈 docstring). `datetime` 이 아닌 **값이
#: 있는** 경우(파싱 실패 문자열 등)는 여전히 `bad_args`(`_check_field_
#: values`).
_UNCONFIRMED_OK_FIELDS: frozenset[str] = frozenset({"occurred_at", "scheduled_at"})

#: 문자열이어야 하는 필드(등장하는 툴이 다르므로 필드 이름 기준으로 한
#: 표에 모은다 -- ③ 의 타입 위반 검사).
_STRING_FIELDS: tuple[str, ...] = (
    "person",
    "content",
    "title",
    "display_name",
    "new_alias",
)


# ---------------------------------------------------------------------------
# 게이트 설정 (결정 A(i) 4종 상한 -- `app.settings.LOOP_MAX_*` 가 값의
# 단일 출처이고, 이 dataclass 는 그 값을 담아 함수 인자로 주입하는 모양일
# 뿐이다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GateConfig:
    """`check()` 의 상한 설정. 기본값은 `app.settings.LOOP_MAX_*`(결정
    A(i)·R-13) -- 테스트가 값을 좁혀 상한 초과 케이스를 작은 제안 목록으로
    재현할 수 있게 필드로 노출한다."""

    max_mentions: int = LOOP_MAX_MENTIONS
    max_events: int = LOOP_MAX_EVENTS
    max_schedules: int = LOOP_MAX_SCHEDULES
    max_proposals: int = LOOP_MAX_PROPOSALS


# ---------------------------------------------------------------------------
# ③ 인자 스키마 -- inspect.signature 런타임 대조 (게이트 ③ 의 출처,
# `scripts/tools_check.py` 와 같다)
# ---------------------------------------------------------------------------


def _arg_spec(name: str) -> tuple[frozenset[str], frozenset[str]]:
    """`app.tools.<name>` 의 시그니처에서 (필수 인자 이름 집합, 허용 인자
    이름 집합) 을 만든다. `ctx` 는 항상 첫 인자이므로 뺀다. `person_id`
    자리는 `person`(언급 문자열)으로 이름을 바꾸고, `raw_utterance` 는
    허용 집합에서 아예 뺀다(루프가 주입하므로 LLM 제안에 있으면 안
    된다 -- 있으면 `_classify_args` 가 "미지 인자"로 `bad_args` 를
    낸다). `occurred_at`/`scheduled_at` 은 허용 집합에는 남기되 필수
    집합에서는 뺀다(R-23, 모듈 docstring)."""

    fn = getattr(app_tools, name)
    params = list(inspect.signature(fn).parameters.values())[1:]  # ctx 제외

    required: set[str] = set()
    allowed: set[str] = set()
    for param in params:
        if param.name == "raw_utterance":
            continue
        label = "person" if param.name == "person_id" else param.name
        allowed.add(label)
        if label in _UNCONFIRMED_OK_FIELDS:
            continue
        if param.default is inspect.Parameter.empty:
            required.add(label)

    return frozenset(required), frozenset(allowed)


def _missing_or_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _check_field_values(name: str, args: dict[str, Any]) -> str | None:
    """③ 타입·고정 집합 위반 검사(필수/미지 여부는 이미 `_classify_args`
    가 확인한 뒤 호출된다). 문제 없으면 `None`."""

    for field in _UNCONFIRMED_OK_FIELDS:
        if field in args:
            value = args[field]
            if value is not None and not isinstance(value, datetime):
                # ISO 파싱 실패 문자열 등 -- "미확정"이 아니라 형식 오류(R-23).
                return REASON_BAD_ARGS

    if "type" in args and args["type"] not in EVENT_TYPES:
        return REASON_BAD_ARGS
    if "relation_tag" in args and args["relation_tag"] not in RELATION_TAGS:
        return REASON_BAD_ARGS
    if "hierarchy" in args and args["hierarchy"] not in HIERARCHIES:
        return REASON_BAD_ARGS

    for field in _STRING_FIELDS:
        if field in args and not isinstance(args[field], str):
            return REASON_BAD_ARGS

    if "aliases" in args:
        aliases = args["aliases"]
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            return REASON_BAD_ARGS

    if "facts" in args:
        facts = args["facts"]
        if not isinstance(facts, list):
            return REASON_BAD_ARGS
        for item in facts:
            if not isinstance(item, dict) or set(item) != {"key", "value"}:
                return REASON_BAD_ARGS
            if not isinstance(item["key"], str) or not isinstance(item["value"], str):
                return REASON_BAD_ARGS

    return None


def _classify_args(name: str, args: dict[str, Any]) -> str | None:
    """③ 인자 스키마 검사(+ `update_person.display_name` 의
    `needs_confirmation`). 문제 없으면 `None`."""

    if name == "update_person" and "display_name" in args:
        # D6 -- 표시 이름 변경은 확인 질문을 거쳐야 한다. 재개 경로에서만
        # 실행되고(U7), 기록 단계(U5)는 이 사유로 걸러진 제안을 절대
        # 실행하지 않는다.
        return REASON_NEEDS_CONFIRMATION

    required, allowed = _arg_spec(name)

    for key in args:
        if key not in allowed:
            return REASON_BAD_ARGS

    for key in required:
        if _missing_or_blank(args.get(key)):
            return REASON_BAD_ARGS

    return _check_field_values(name, args)


# ---------------------------------------------------------------------------
# check() -- ①②④③⑤ 를 순서대로 적용하는 게이트 본체
# ---------------------------------------------------------------------------


def check(proposal: Proposal, *, config: GateConfig | None = None) -> GateVerdict:
    """`loop_gate.output` 의 바탕이 되는 `GateVerdict` 를 만든다. 세션·
    LLM·DB 를 건드리지 않는 순수 함수 -- 제안을 실행하지 않는다(U5 의
    일).

    적용 순서는 모듈 docstring 의 ①②④③⑤ 그대로다. `config` 를 생략하면
    `app.settings.LOOP_MAX_*` 기본값을 쓴다(테스트는 작은 상한을 주입해
    `limit` 사유를 재현한다)."""

    cfg = config or GateConfig()

    rejected: list[RejectedProposal] = []
    passed: list[AcceptedProposal] = []  # ⑤ 상한 검사 전 -- ①②④③ 통과분

    for index, call in enumerate(proposal.tool_calls):
        name = call.name
        args = call.args

        if name not in app_tools.TOOL_NAMES:  # ① 화이트리스트
            rejected.append(RejectedProposal(index=index, name=name, reason=REASON_UNKNOWN_TOOL))
            continue

        if name in NOT_CALLABLE_BY_LLM:  # ② 호출 가능 집합
            rejected.append(
                RejectedProposal(index=index, name=name, reason=REASON_NOT_CALLABLE_BY_LLM)
            )
            continue

        if "person_id" in args:  # ④ person_id 금지 (③ 보다 먼저)
            rejected.append(
                RejectedProposal(index=index, name=name, reason=REASON_PERSON_ID_FROM_LLM)
            )
            continue

        reason = _classify_args(name, args)  # ③ 인자 스키마
        if reason is not None:
            rejected.append(RejectedProposal(index=index, name=name, reason=reason))
            continue

        bucket = BUCKET_HINT_ONLY if name == "create_person" else BUCKET_EXECUTE
        passed.append(AcceptedProposal(index=index, name=name, bucket=bucket))

    accepted, limit_rejected, stop_reason = _apply_limits(proposal, passed, cfg)
    rejected.extend(limit_rejected)
    rejected.sort(key=lambda r: r.index)

    limits = GateLimits(
        mentions=cfg.max_mentions,
        events=cfg.max_events,
        schedules=cfg.max_schedules,
        proposals=cfg.max_proposals,
    )
    return GateVerdict(accepted=accepted, rejected=rejected, limits=limits, stop_reason=stop_reason)


def _apply_limits(
    proposal: Proposal, passed: list[AcceptedProposal], cfg: GateConfig
) -> tuple[list[AcceptedProposal], list[RejectedProposal], str | None]:
    """⑤ 상한. `passed`(①②④③ 통과분)를 인덱스 순서대로 훑으며 총 개수·
    언급 수·이벤트 수·일정 수를 센다 -- 결정 A(i)·R-13. 넘는 제안은
    `limit` 로 거부한다."""

    accepted: list[AcceptedProposal] = []
    limit_rejected: list[RejectedProposal] = []
    stop_reason: str | None = None

    mentions_seen: set[str] = set()
    event_count = 0
    schedule_count = 0

    for ap in passed:
        args = proposal.tool_calls[ap.index].args
        mention = args.get("person")
        is_new_mention = (
            ap.name in ("update_person", "add_event", "add_schedule")
            and isinstance(mention, str)
        )

        over = len(accepted) >= cfg.max_proposals
        if not over and ap.name == "add_event" and event_count >= cfg.max_events:
            over = True
        if not over and ap.name == "add_schedule" and schedule_count >= cfg.max_schedules:
            over = True
        if (
            not over
            and is_new_mention
            and mention not in mentions_seen
            and len(mentions_seen) >= cfg.max_mentions
        ):
            over = True

        if over:
            limit_rejected.append(RejectedProposal(index=ap.index, name=ap.name, reason=REASON_LIMIT))
            stop_reason = REASON_LIMIT
            continue

        if is_new_mention:
            mentions_seen.add(mention)
        if ap.name == "add_event":
            event_count += 1
        elif ap.name == "add_schedule":
            schedule_count += 1
        accepted.append(ap)

    return accepted, limit_rejected, stop_reason
