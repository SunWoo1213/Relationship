"""Refs: P3-baselines S3.7 D10 원칙2 원칙8 -- 네 방식이 공유하는 데이터 계약.

`.claude/skills/eval-harness` §3 은 네 방식(문자열 완전일치·임베딩 단독·
LLM 단일 프롬프트·제안 4단계)을 **동일 데이터·동일 지표**로 비교하라고
요구한다. 그러려면 먼저 **동일 호출**이 성립해야 한다 -- 이 모듈이 그
호출 형태(`Resolver` Protocol)와 답의 형태(`MentionDecision`)를 고정한다.
P4 러너는 `for name in ALL_METHODS:` 한 줄로 네 방식을 돌린다.

## 불변 규약 4개 (네 구현 전부에 적용 · 계약 테스트가 단언한다)

1. **부수효과 0** -- resolver 는 `persons`·`person_aliases`·
   `pending_questions` 에 쓰지 않는다. 어떤 방식도 `ask_user`·
   `create_person`·`update_person`·`apply_resolution` 을 부르지 않는다.
   "무엇을 할지"만 답하고 실행은 P4 러너/P5 몫이다(제안 방식
   `app.er.resolve()` 가 이미 그런 계약이다 -- P3-er 결정4). 제안 방식
   어댑터만 `agent_traces` 행 1개를 남기는데, 그것은 감싼 `resolve()` 의
   성질이며 인물·별칭·질문 상태를 바꾸지 않는다.
2. **예외 비대칭 금지** -- 후보 0건·판정 실패·응답 스키마 위반은 예외로
   던지지 않는다. `decision="new_person"` 또는 `"identity"` 로 표현하고
   이유를 `detail["forced_reason"]` 에 남긴다. 한 방식만 예외로 죽으면
   분모가 달라져 비교가 깨진다(원칙8) -- 그것은 "그 방식의 성능"이 아니라
   "평가의 결함"이다.
3. **`person_id` 는 `merge` 에서만** -- `identity` 는 "사람에게 묻는다"
   이므로 후보 목록(`candidates`)이 답이고 단일 인물을 고르지 않는다.
   `new_person` 도 인물을 가리키지 않는다(원칙1·원칙2). 이 규약은
   `MentionDecision.__post_init__` 이 강제한다 -- 규약을 어긴 구현은 값을
   만들 수조차 없다.
4. **`config` 는 `ERConfig` 를 그대로 재사용**(D10) -- 임계치를 새로
   정의하지 않는다. P4 가 한 프로세스 안에서 `T_merge` 를 스윕하고
   (x축 = `T_merge`, `T_new` = 0.3 고정, S3.7) 네 방식에 **같은 값**을
   넘긴다. 각 방식이 두 임계치를 어떻게 쓰는지(또는 쓰지 않는지)는 그
   방식 모듈의 docstring 에 한 줄로 적는다.

## 결정 어휘 (`DECISIONS`)

`app.er.confidence.band_for()` 가 내는 세 밴드와 **같은 낱말**이다
(`merge` / `identity` / `new_person`, D10). 베이스라인도 이 어휘를 쓰되
방식마다 실제로 낼 수 있는 집합을 `supported_decisions` 로 선언한다
(01-plan 결정 B(i)) -- 완전일치 방식도 동명이인 2건에서는 고를 수 없으므로
`identity` 가 자연스럽고, 임의로 하나를 고르게 하면 오병합률이 인위적으로
부풀어 베이스라인을 약하게 만드는 셈이 된다(원칙8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:  # 런타임 import 없음 -- 이 모듈은 DB·네트워크 없이 import 된다.
    from app.er.types import ERConfig
    from app.tools.context import ToolContext

#: 결정 어휘. `app.er.confidence.band_for()` 의 반환 밴드와 같은 낱말이고
#: 순서는 확신도가 높은 쪽부터다(`>= T_merge` -> `>= T_new` -> 그 외, D10).
#: `tests/test_baseline_base.py` 가 `band_for()` 를 실제로 호출해 이 튜플과
#: 대조한다(이중 출처 방지 -- 어휘가 갈라지면 테스트가 깨진다).
DECISIONS: tuple[str, ...] = ("merge", "identity", "new_person")


@dataclass(frozen=True)
class ResolverCandidate:
    """한 방식이 본 후보 하나. `signals` 는 그 방식의 원자료를 그대로 담는다
    (`s_emb`·`s_rule`·`s_llm`·`exact` 등) -- 방식마다 키가 다른 것이
    정상이고 이름을 억지로 통일하지 않는다(원칙9: 근거를 남긴다).

    `score` 는 그 방식이 이 후보에 준 0~1 점수이며, 점수 개념이 없는
    방식(문자열 완전일치 등)은 일치 여부를 `1.0`/`0.0` 으로 쓴다.
    """

    person_id: int
    display_name: str
    score: float = 0.0
    signals: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_id": self.person_id,
            "display_name": self.display_name,
            "score": self.score,
            "signals": dict(self.signals),
        }


@dataclass(frozen=True)
class MentionDecision:
    """mention 하나에 대한 한 방식의 답. **방식별 원자료의 단일 출처**다
    (01-plan 리스크 "trace 비대칭" -- 제안 방식만 `agent_traces` 를 남기므로
    P4 는 네 방식 모두에 대해 이 반환값을 읽는다).

    - `method` -- `RESOLVERS` 등록 이름 그대로. `reports/metrics.json` 의
      키가 되므로 임의로 바꾸지 않는다(P4 인계 4).
    - `decision` -- `DECISIONS` 중 하나.
    - `person_id` -- `decision == "merge"` 일 때만 not None(불변 규약 3).
    - `score` -- 그 결정의 근거 점수 `[0, 1]`. **의미는 방식마다 다르다**
      (제안 방식은 3신호 결합 확신도, 임베딩 단독은 `s_emb`, 완전일치는
      일치 여부, LLM 단일은 자기보고 `s_llm`). 방식이 서로 다른 점수를
      같은 축으로 비교해도 되는지의 판단은 P4 몫이다.
    - `trace_id`/`tokens_in`/`tokens_out` -- 제안 방식·LLM 방식만 채운다
      (없으면 `None`/`0`).
    - `detail` -- `forced_reason`·정규화형·공급자·모델·`dropped_ids` 등
      방식별 부가 정보. 불변 규약 2 의 실패 사유가 여기 들어간다.

    생성 시 불변 규약을 검증하고 어기면 `ValueError` 를 던진다 -- 잘못된
    결정이 조용히 지표로 흘러 들어가지 않게 한다(원칙8). 이 검증은
    **값의 형태**에 대한 것이지 판정 실패에 대한 것이 아니다(불변 규약 2
    와 충돌하지 않는다 -- 판정 실패는 `forced_reason` 으로 표현된다).
    """

    method: str
    mention: str
    decision: str
    person_id: int | None
    score: float
    candidates: list[ResolverCandidate]
    trace_id: int | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    detail: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS:
            raise ValueError(
                f"MentionDecision: decision must be one of {DECISIONS} "
                f"(got {self.decision!r})"
            )
        if self.decision == "merge":
            if self.person_id is None:
                raise ValueError(
                    'MentionDecision: decision="merge" requires person_id '
                    "(불변 규약 3)"
                )
        elif self.person_id is not None:
            raise ValueError(
                "MentionDecision: person_id is only allowed when "
                f'decision == "merge" (got decision={self.decision!r}, '
                f"person_id={self.person_id!r} -- 불변 규약 3, 원칙1·2)"
            )
        # NaN 은 어떤 비교에도 False 이므로 이 형태가 NaN 도 함께 거른다.
        if not 0.0 <= float(self.score) <= 1.0:
            raise ValueError(
                f"MentionDecision: score must be in [0, 1] (got {self.score!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        """`json.dumps()` 가 그대로 받는 형태(P4 가 `metrics.json`·응답
        캐시로 보존한다 -- 재현성, 원칙8). `detail` 에 무엇을 넣을지는 각
        방식의 책임이며 JSON 직렬화 가능한 값만 넣는다."""
        return {
            "method": self.method,
            "mention": self.mention,
            "decision": self.decision,
            "person_id": self.person_id,
            "score": self.score,
            "candidates": [c.to_dict() for c in self.candidates],
            "trace_id": self.trace_id,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "detail": dict(self.detail),
        }


@runtime_checkable
class Resolver(Protocol):
    """네 방식이 공유하는 호출 형태. 구현체가 이 Protocol 을 **상속할
    필요는 없다**(구조적 타이핑). `@runtime_checkable` 이라 계약 테스트가
    `isinstance()` 로 속성·메서드 존재를 확인할 수 있지만, `isinstance()`
    는 **시그니처까지 보지 않으므로** 진짜 계약 증명은 네 방식을 같은
    인자로 실제 호출하는 `tests/test_baseline_parity.py`(U7) 다.

    - `name` -- `RESOLVERS` 등록 이름과 같아야 한다(`MentionDecision.method`
      로 그대로 나간다).
    - `supported_decisions` -- 그 방식이 실제로 낼 수 있는 결정의 부분집합
      (subset of `DECISIONS`, 01-plan 결정 B(i)).
    - `resolve_mention` -- `mention` 을 **인자로 받는다**. 발화에서 지칭을
      뽑는 일은 P5-loop 이다(P3-er 결정1 의 경계 승계). `hints` 는
      `search_person` 과 같은 `{hierarchy?, relation_tag?}` 형태이고
      `config` 는 `ERConfig` 다(불변 규약 4).
    """

    name: str
    supported_decisions: tuple[str, ...]

    def resolve_mention(
        self,
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: ERConfig | None = None,
    ) -> MentionDecision: ...
