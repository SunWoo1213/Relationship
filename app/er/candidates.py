"""Refs: P3-er S3.3 D5 R9 결정1 -- 1단계(후보 검색) 어댑터.

`.claude/skills/entity-resolution` "1. 후보 검색 | 별칭 단위 임베딩 top-K
(K=10) -> 인물별 max 유사도" 를 `search_person`(P2-tools) 위에 얹는다.
**`search_person` 을 재사용한다 -- 재구현하지 않는다**(01-plan 산출물
"`search_person` 재사용", 결정1 "P3/P5 경계").

이 모듈은 DB 쓰기를 하지 않는다. `search_person` 이 이미 연 세션으로
`person_aliases` 를 추가 조회(별칭 전체 채우기, U3 인계)할 뿐이다.

## hints 유도 (호출자가 안 주면 사전에서)

`hints` 가 `None` 이면 `app.er.dictionary.derive_hints(mention)` 으로
유도해 `search_person` 에 그대로 넘긴다. 유도 결과는 `SearchCandidates`
로 함께 돌려준다 -- U6(`pipeline.py`)이 2단계(`rules.py`)·trace 에
**같은 hints** 를 써야 하기 때문이다(호출자가 유도와 규칙 필터에서 각자
다시 유도하면 trace 의 `decision`/`candidates[]` 가 서로 다른 hints 를
전제로 계산될 수 있다).

## s_emb 정규화

`Candidate.similarity` 를 그대로 `ScoredCandidate.s_emb` 로 옮기되,
`rule_flags["embedding_skipped"]` 가 `True` 면(`search_person` 이 임베딩
검색 자체를 하지 않은 경우, 모듈 docstring 참고) `0.0` 으로 강제하고,
값 자체도 방어적으로 `[0, 1]` 로 클램프한다(`combine()` 이 다시 클램프
하지만, `candidates[]` trace 필드에도 클램프된 값을 남겨 P4 재계산이
음수·초과값을 보지 않게 한다).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.db.models import Person, PersonAlias
from app.er.dictionary import derive_hints
from app.er.types import ScoredCandidate
from app.settings import SEARCH_TOP_K
from app.tools.context import ToolContext
from app.tools.persons import search_person
from app.tools.types import Candidate


@dataclass(frozen=True)
class SearchCandidates:
    """`search_candidates()` 반환값 -- 후보 목록과 **실제로 쓰인 hints**.

    `hints` 가 `None` 이면 `derive_hints(mention)` 유도 결과가 여기 담긴다
    (빈 dict 일 수 있다 -- 대명사·미등재 지칭). U6 은 이 값을 그대로
    2단계(`rules.py`)와 trace `decision`/`llm` 에 재사용한다."""

    candidates: list[ScoredCandidate]
    hints: dict[str, str]


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _aliases_for(ctx: ToolContext, person_id: int) -> list[str]:
    """`PersonOut` 에 별칭이 없을 때를 대비해 `person_aliases` 를 직접
    조회한다(U3 인계). `search_person` 의 `PersonOut.aliases` 가 이미
    그 인물의 별칭 전체를 담고 있으면 이 조회는 같은 값을 재확인만 한다."""

    rows = ctx.session.execute(
        select(PersonAlias.alias)
        .join(Person, PersonAlias.person_id == Person.id)
        .where(PersonAlias.person_id == person_id)
        .where(Person.user_id == ctx.user_id)
    ).scalars().all()
    return sorted(rows)


def _to_scored(ctx: ToolContext, candidate: Candidate) -> ScoredCandidate:
    person = candidate.person
    aliases = list(person.aliases) if person.aliases else _aliases_for(ctx, person.id)
    embedding_skipped = bool(candidate.rule_flags.get("embedding_skipped"))
    s_emb = 0.0 if embedding_skipped else _clamp01(candidate.similarity)
    return ScoredCandidate(
        person_id=person.id,
        display_name=person.display_name,
        aliases=aliases,
        relation_tag=person.relation_tag,
        hierarchy=person.hierarchy,
        s_emb=s_emb,
        rule_flags=dict(candidate.rule_flags),
    )


def search_candidates(
    ctx: ToolContext,
    mention: str,
    hints: dict[str, str] | None = None,
    *,
    top_k: int = SEARCH_TOP_K,
) -> SearchCandidates:
    """1단계 어댑터: `search_person` 재사용 + `s_emb` 정규화 + hints 유도.

    `top_k` 는 `search_person`(P2)이 이미 `SEARCH_TOP_K`(`app.settings`)를
    내부 상수로 쓰므로 이 함수에서는 전달하지 않는다 -- 인자는 호출부
    (U6·트레이스)가 실제로 쓰인 `top_k` 값을 명시적으로 기록할 수 있도록
    받아 두되(01-plan 결정8 설정값 3층과 같은 자리), `search_person` 의
    시그니처(S3.2, 변경 금지)에는 넘기지 않는다.

    DB 쓰기 없음 -- `search_person` 자체가 조회만 하고(`@traced` 가
    trace 행 하나를 flush 하는 것은 예외 -- 그 trace 행은 `search_person`
    툴 호출 자체의 기록이지, 인물/별칭 데이터를 바꾸는 것이 아니다).
    """

    effective_hints = hints if hints is not None else derive_hints(mention)
    raw_candidates = search_person(ctx, mention, effective_hints or None)
    scored = [_to_scored(ctx, c) for c in raw_candidates]
    return SearchCandidates(candidates=scored, hints=effective_hints)
