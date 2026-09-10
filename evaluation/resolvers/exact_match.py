"""Refs: P3-baselines S3.7 원칙1 원칙8 -- 베이스라인 1 문자열 완전일치(2변형).

**두 임계치**(base.py 불변 규약 4): 이 방식은 `T_merge`/`T_new` 를 **쓰지
않는다** -- 판정이 "일치한 인물 수"(0/1/2 이상)로만 갈리므로 `config` 는
받되 읽지 않는다(같은 호출 형태를 유지하기 위한 인자다). 따라서 P4 의
`T_merge` 스윕 곡선에서 이 방식의 두 선(오병합률·미검출률)은 **수평선**이
되고, 그것이 곧 "임계치로 조절할 수 없는 방식"이라는 비교 정보다.

## 무엇을 하는 방식인가 (01-plan 55행·102행, 결정 C(iii))

사전 상태의 `person_aliases.alias` 와 `persons.display_name` 을 mention 과
**문자열로만** 대조한다. 임베딩·LLM·규칙 필터를 쓰지 않고 네트워크 호출이
0 이며 DB 는 `SELECT` 만 한다(불변 규약 1 -- 부수효과 0).

| 일치한 **인물 수** | 결정 | 근거 |
|---|---|---|
| 1 | `merge` (`person_id`, `score` 1.0) | 유일하게 가리키는 사람이 있다 |
| 2 이상 | `identity` (`person_id` **None**, 후보 전부) | 동명이인을 임의로 고르지 않는다(원칙1) |
| 0 | `new_person` (`score` 0.0) | 아는 이름이 아니다 |

"2 이상 → `identity`" 는 결정 B(i)다. 임의로 하나를 고르게 하면 오병합률이
인위적으로 부풀어 **베이스라인을 부당하게 약하게 만드는 셈**이 된다 --
약한 대비군으로 이긴 비교는 원칙8 위반이다.

## 두 변형 (결정 C(iii) -- 둘 다 등록해 P4 가 둘 다 보고한다)

- `exact_raw` -- 앞뒤 공백과 대소문자만 정리한 **순수** 완전일치
  (`normalize_raw`). "문자열 완전일치"라는 이름에 가장 충실한 형태.
- `exact_norm` -- `app.er.dictionary.normalize()`(공백 제거 → 존칭 접미
  최대 1개 제거 → 성씨 1글자 접두 제거) 를 적용한 완전일치
  (`normalize_dictionary`). 호칭 사전은 제안 방식의 구성요소지만, 주지
  않으면 베이스라인이 부당하게 약해진다 -- 두 변형을 함께 내는 것이
  정직한 비교다(원칙8).

**정규화는 양쪽에 대칭으로 적용한다(권고 R-8).** mention 과 별칭·표시
이름을 **같은 함수**에 통과시킨 뒤 비교한다. 한쪽만 정규화하면
"김팀장"↔"팀장" 이 방향에 따라 다르게 매칭되어 방식의 정의가 흐려진다.
정규화 결과가 빈 문자열인 mention(예: "님" 단독)은 비교할 것이 없으므로
`new_person` + `detail["forced_reason"] = "empty_after_normalize"` 다
(불변 규약 2 -- 예외로 죽지 않는다).

## `score` 의 의미 (base.py `MentionDecision.score` 주석 참조)

이 방식에는 확신도 개념이 없다. `score` 는 **일치 여부**(1.0/0.0)일 뿐이며
`identity`(동명이인 2건) 에서도 1.0 이다 -- "문자열은 정확히 맞았지만
사람을 특정하지 못했다"는 뜻이다. 제안 방식의 결합 확신도와 **같은 축에
놓고 비교하면 안 된다**(그 판단은 P4 몫이고, base.py 가 이미 "의미는
방식마다 다르다"고 못 박았다).

## 사전 상태를 읽는 범위

`Person.user_id == ctx.user_id` 인 인물만 본다(다른 사용자의 인물이
후보로 새면 비교가 깨진다). `search_person` 과 달리 **`embedding IS NULL`
인 별칭도 그대로 쓴다** -- 문자열 비교에 벡터가 필요 없기 때문이고, 그래서
이 방식은 임베딩 공급자 없이도 P4 에서 완전한 수치를 낸다(비용 0).
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from app.db.models import Person, PersonAlias
from app.er.dictionary import normalize as dictionary_normalize
from evaluation.resolvers.base import DECISIONS, MentionDecision, ResolverCandidate
from evaluation.resolvers.registry import register

if TYPE_CHECKING:
    from app.er.types import ERConfig
    from app.tools.context import ToolContext

#: `RESOLVERS` 등록 이름 = `MentionDecision.method` = `metrics.json` 키
#: (P4 인계 4). 바꾸면 P4 산출물 스키마가 바뀐다.
RAW_METHOD_NAME = "exact_raw"
NORM_METHOD_NAME = "exact_norm"

#: 정규화 후 mention 이 비었을 때의 사유(권고 R-8).
EMPTY_AFTER_NORMALIZE = "empty_after_normalize"

#: `ask_user` 를 부르지 않으므로(불변 규약 1) 물었을 `kind` 만 남긴다 --
#: P4 `ask_user_rate_by_kind`(eval-harness §2) 입력. `proposed.py` 와 같은
#: 대응이다(`merge` 는 묻지 않는다).
_ASK_KIND_BY_DECISION: dict[str, str | None] = {
    "merge": None,
    "identity": "identity",
    "new_person": "new_person",
}

Normalizer = Callable[[str], str]


def normalize_raw(text: str | None) -> str:
    """변형 a -- 앞뒤 공백과 대소문자만 정리한다(결정 C(i)).

    한글에는 대소문자가 없지만 별칭에 로마자("Kim", "PM")가 섞일 수 있어
    `casefold()` 를 쓴다(`lower()` 보다 유니코드 대소문자 접기가 넓다).
    **문자열 내부의 공백은 건드리지 않는다** -- 그것까지 지우면 이미
    "완전일치"가 아니라 정규화다(그 역할은 `exact_norm` 이 맡는다).
    """

    if not text:
        return ""
    return text.strip().casefold()


def normalize_dictionary(text: str | None) -> str:
    """변형 b -- `app.er.dictionary.normalize()` + 대소문자 접기(결정 C(ii)).

    `app/er/dictionary.py` 를 **그대로 import 해 재사용**한다(중복 구현
    금지). 그 함수가 공백을 전부 제거하고 존칭 접미·성씨 접두를 떼므로
    "김팀장"·"팀장님"·"김 팀장" 이 모두 "팀장" 으로 모인다.

    `casefold()` 를 뒤에 붙이는 이유는 이 변형이 `exact_raw` 의
    **상위집합**이 되게 하기 위해서다 -- 사전 정규화를 더 했는데 로마자
    대소문자에서 오히려 덜 맞으면 두 변형의 비교가 뒤집혀 해석이 꼬인다.
    """

    return dictionary_normalize(text).casefold()


@dataclass(frozen=True)
class KnownPerson:
    """사전 상태의 인물 하나 = 그 인물을 가리키는 **문자열들**.

    `names` 는 `persons.display_name` + 그 인물의 `person_aliases.alias`
    전부이며 **저장된 원문 그대로**다(정규화는 비교 시점에 양쪽에 대칭으로
    적용한다 -- R-8). DB 를 쓰지 않는 단위 테스트가 이 값을 손으로 만들 수
    있어야 하므로 순수 dataclass 다.
    """

    person_id: int
    display_name: str
    names: tuple[str, ...] = ()

    def all_names(self) -> tuple[str, ...]:
        """표시 이름 + 별칭(중복 제거, 등장 순서 유지)."""
        seen: OrderedDict[str, None] = OrderedDict()
        for name in (self.display_name, *self.names):
            if name:
                seen.setdefault(name, None)
        return tuple(seen)


@dataclass(frozen=True)
class ExactMatch:
    """`match_exact()` 의 결과 -- 어느 인물이 **어떤 이름으로** 맞았는지.

    맞은 이름(`matched_names`)까지 돌려주는 이유는 원칙9다: P4 가
    "'부장님' 이 표시 이름으로 맞았나 별칭으로 맞았나"를 사후에 알 수 있어야
    실패 유형 분석이 된다.
    """

    person_ids: tuple[int, ...] = ()
    matched_names: dict[int, tuple[str, ...]] = field(default_factory=dict)


def match_exact(
    mention: str | None,
    persons: list[KnownPerson],
    *,
    normalizer: Normalizer,
) -> ExactMatch:
    """**순수 함수** -- DB·네트워크 없이 완전일치 인물을 찾는다(01-plan 102행).

    `normalizer` 를 `mention` 과 각 인물의 이름 **양쪽에** 적용한 뒤 비교한다
    (R-8 -- 한쪽만 정규화하면 "김팀장"↔"팀장" 이 비대칭이 된다). 정규화된
    mention 이 빈 문자열이면 **아무것도 맞지 않는다**(빈 이름과의 우연한
    일치를 막는다). 그 사실을 결정으로 옮기는 일은 호출자(resolver)가 한다.

    반환 순서는 `persons` 의 순서를 그대로 유지한다 -- resolver 가 만드는
    `candidates` 의 순서가 호출마다 흔들리면 재현성이 깨진다(원칙8).
    """

    key = normalizer(mention or "")
    if not key:
        return ExactMatch()

    person_ids: list[int] = []
    matched_names: dict[int, tuple[str, ...]] = {}
    for person in persons:
        hits = tuple(
            name
            for name in person.all_names()
            if normalizer(name) == key
        )
        if hits:
            person_ids.append(person.person_id)
            matched_names[person.person_id] = hits
    return ExactMatch(person_ids=tuple(person_ids), matched_names=matched_names)


def load_known_persons(ctx: ToolContext) -> list[KnownPerson]:
    """사전 상태 조회(**`SELECT` 만** -- 불변 규약 1).

    `Person.user_id == ctx.user_id` 범위의 인물 전부를 `persons.id` 오름차순
    으로, 각 인물의 별칭은 `person_aliases.id` 오름차순으로 담는다(결정적
    순서 = 재현성, 원칙8). 별칭이 하나도 없는 인물도 표시 이름으로 비교
    대상이 되어야 하므로 `outerjoin` 이다.

    `embedding IS NULL` 인 별칭도 포함한다 -- 문자열 비교에는 벡터가 필요
    없다(모듈 docstring "사전 상태를 읽는 범위").
    """

    rows = ctx.session.execute(
        select(Person.id, Person.display_name, PersonAlias.alias)
        .outerjoin(PersonAlias, PersonAlias.person_id == Person.id)
        .where(Person.user_id == ctx.user_id)
        .order_by(Person.id, PersonAlias.id)
    ).all()

    by_id: OrderedDict[int, tuple[str, list[str]]] = OrderedDict()
    for person_id, display_name, alias in rows:
        entry = by_id.setdefault(person_id, (display_name, []))
        if alias is not None:
            entry[1].append(alias)
    return [
        KnownPerson(person_id=pid, display_name=display_name, names=tuple(aliases))
        for pid, (display_name, aliases) in by_id.items()
    ]


def to_mention_decision(
    match: ExactMatch,
    persons: list[KnownPerson],
    *,
    method: str,
    mention: str,
    normalized_mention: str,
    forced_reason: str | None = None,
) -> MentionDecision:
    """일치 결과 -> `MentionDecision` 순수 변환(DB·네트워크 없음).

    후보(`candidates`)에는 **맞은 인물만** 담는다. 이 방식은 맞지 않은
    인물에 줄 점수가 없으므로(유사도 개념이 없다) 전 인물을 후보로 싣는
    것은 근거가 아니라 잡음이다 -- `new_person` 의 후보 목록은 빈 목록이
    맞다(원칙9 는 "있는 근거를 남기라"이지 "없는 근거를 지어내라"가 아니다).
    """

    display_by_id = {p.person_id: p.display_name for p in persons}
    ids = match.person_ids

    if len(ids) == 1 and forced_reason is None:
        decision = "merge"
        person_id: int | None = ids[0]
        score = 1.0
    elif len(ids) >= 2 and forced_reason is None:
        decision = "identity"
        person_id = None
        score = 1.0
    else:
        decision = "new_person"
        person_id = None
        score = 0.0
        ids = ()

    candidates = [
        ResolverCandidate(
            person_id=pid,
            display_name=display_by_id.get(pid, ""),
            # 점수 개념이 없는 방식은 일치 여부를 1.0/0.0 으로 쓴다
            # (base.py `ResolverCandidate.score`).
            score=1.0,
            signals={"exact": 1.0},
        )
        for pid in ids
    ]

    detail: dict[str, Any] = {
        "variant": method,
        "normalized_mention": normalized_mention,
        "match_count": len(ids),
        "matched_person_ids": list(ids),
        "matched_names": {str(pid): list(match.matched_names[pid]) for pid in ids},
        "forced_reason": forced_reason,
        "ask_kind": _ASK_KIND_BY_DECISION[decision],
        # 이 방식이 쓰지 않은 신호를 명시한다(원칙4 의 대비군 정의 --
        # P4 표에 "무엇을 안 쓰고 이만큼 했는가"가 그대로 적힌다).
        "uses_embedding": False,
        "uses_llm": False,
        "uses_rules": False,
        "uses_thresholds": False,
    }

    return MentionDecision(
        method=method,
        mention=mention,
        decision=decision,
        person_id=person_id,
        score=score,
        candidates=candidates,
        trace_id=None,
        tokens_in=0,
        tokens_out=0,
        detail=detail,
    )


class ExactMatchResolver:
    """두 변형이 공유하는 구현. 변형은 `name` 과 `normalizer` 만 다르다.

    `supported_decisions` 는 **세 밴드 전부**다 -- 완전일치도 동명이인
    2건에서는 `identity` 를 내야 하고(결정 B(i)), 그것이 원칙1 이 요구하는
    행동이다.
    """

    name: str = ""
    supported_decisions: tuple[str, ...] = DECISIONS

    #: 변형의 정규화 함수. `staticmethod` 로 감싸야 인스턴스 접근 시
    #: 바인딩되지 않는다(첫 인자에 `self` 가 들어가는 사고 방지).
    normalizer: Normalizer = staticmethod(normalize_raw)

    def resolve_mention(
        self,
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: ERConfig | None = None,
    ) -> MentionDecision:
        """사전 상태 조회 1회 -> 순수 판정 1회.

        `utterance`·`hints`·`config` 는 **받지만 쓰지 않는다** -- 네 방식이
        같은 호출 형태를 갖게 하려는 인자이고(base.py `Resolver`), 이 방식이
        발화 맥락과 임계치를 쓰지 않는다는 사실 자체가 비교 정보다.
        임계치를 여기서 새로 정의하지 않는다(불변 규약 4).
        """

        normalizer: Normalizer = type(self).normalizer
        normalized = normalizer(mention or "")
        persons = load_known_persons(ctx)

        if not normalized:
            # 비교할 문자열이 없다 -- 예외로 죽지 않고 사유를 남긴다(R-8,
            # 불변 규약 2).
            return to_mention_decision(
                ExactMatch(),
                persons,
                method=self.name,
                mention=mention,
                normalized_mention=normalized,
                forced_reason=EMPTY_AFTER_NORMALIZE,
            )

        match = match_exact(mention, persons, normalizer=normalizer)
        return to_mention_decision(
            match,
            persons,
            method=self.name,
            mention=mention,
            normalized_mention=normalized,
        )


@register(RAW_METHOD_NAME)
class ExactRawResolver(ExactMatchResolver):
    """베이스라인 1a -- 앞뒤 공백·대소문자만 정리한 순수 완전일치."""

    name: str = RAW_METHOD_NAME
    normalizer: Normalizer = staticmethod(normalize_raw)


@register(NORM_METHOD_NAME)
class ExactNormResolver(ExactMatchResolver):
    """베이스라인 1b -- `app.er.dictionary.normalize()` 를 양쪽에 적용(R-8)."""

    name: str = NORM_METHOD_NAME
    normalizer: Normalizer = staticmethod(normalize_dictionary)
