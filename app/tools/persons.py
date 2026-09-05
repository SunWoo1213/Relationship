"""Refs: P2-tools S3.2 S3.3 D4 D5 원칙1 원칙2 원칙4 -- `search_person`: 후보 검색.

`.claude/skills/entity-resolution` 의 4단계 중 **1단계(후보 검색)만** 여기서
한다. 이 함수는 확신도(`s_llm`/`s_emb`/`s_rule`/`confidence`)를 계산하지
않고, 임계치(`T_merge`/`T_new`)로 후보를 배제하거나 자동으로 인물을
병합/생성하지 않는다 -- 그 판정은 전부 **P3-er**(2~4단계)의 몫이다
(01-plan 결정3, 원칙1·2·4: 오병합은 미검출보다 훨씬 나쁘고, ER 은 LLM 단일
호출로 하지 않는다). 이 함수가 하는 일은 "인물별로 신호를 모아 `Candidate`
로 돌려주는 것"까지다.

## 후보 집합 (배제 없음)

`hints`(`hierarchy`/`relation_tag`)는 후보를 **배제하지 않는다** -- 오직
`rule_flags` 를 채우는 데만 쓴다. 후보 집합은 (별칭 정확/부분 일치로 찾은
인물) ∪ (임베딩 top-K 로 찾은 인물) 의 합집합이다. `hints` 와 무관한 인물도
그대로 후보에 남는다(승진 완화 재검색이 쓸 `hierarchy_adjacent` 신호가
여기서 미리 채워진다 -- S3.3 1단계 문서 참고).

## 임베딩 skip 규칙 (전역 판단)

`ctx.embedder` 가 없거나, 있어도 이 사용자의 별칭 중 `embedding IS NOT NULL`
인 것이 하나도 없으면 임베딩 검색 자체를 하지 않는다 -- 이때는 **모든**
후보의 `rule_flags["embedding_skipped"] = True`, `similarity = 0.0` 이다.
임베딩 검색이 실제로 돌았다면 `embedding_skipped = False` 이고, 그 인물의
별칭이 top-K 안에 하나도 없었던 경우에도(순수 별칭 매칭으로만 후보가 된
경우) `similarity = 0.0` 이 된다 -- "검색을 안 했다"와 "검색했지만 상위
K 안에 없었다"는 다른 사실이므로 플래그를 나누지 않고 전자만 표시한다.
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select

from app.db.models import HIERARCHIES, Person, PersonAlias, RELATION_TAGS
from app.embedding import as_provider
from app.settings import SEARCH_TOP_K
from app.tools.context import ToolContext, traced
from app.tools.types import Candidate, InvalidValue, PersonOut

#: S3.3 1단계 "승진 완화 재검색"이 쓰는 인접 관계 -- 상↔동, 동↔하 만 인접.
#: 상↔하 는 인접이 아니다(두 단계 차이).
_HIERARCHY_ORDER = {value: index for index, value in enumerate(HIERARCHIES)}

_HINT_KEYS = ("hierarchy", "relation_tag")


def _is_hierarchy_adjacent(a: str, b: str) -> bool:
    return abs(_HIERARCHY_ORDER[a] - _HIERARCHY_ORDER[b]) == 1


def _validate_hints(hints: dict[str, str] | None) -> tuple[str | None, str | None]:
    """`hints` 의 키·값 집합을 검증하고 `(hierarchy, relation_tag)` 로 정규화한다.

    허용 키는 `hierarchy`/`relation_tag` 뿐이며, 값은 각각 `HIERARCHIES`/
    `RELATION_TAGS` 안이어야 한다. 벗어나면 `InvalidValue`.
    """
    if not hints:
        return None, None

    for key in hints:
        if key not in _HINT_KEYS:
            raise InvalidValue(f"search_person: unknown hint key '{key}'")

    hierarchy_hint = hints.get("hierarchy")
    if hierarchy_hint is not None and hierarchy_hint not in HIERARCHIES:
        raise InvalidValue(f"search_person: invalid hierarchy hint '{hierarchy_hint}'")

    relation_tag_hint = hints.get("relation_tag")
    if relation_tag_hint is not None and relation_tag_hint not in RELATION_TAGS:
        raise InvalidValue(f"search_person: invalid relation_tag hint '{relation_tag_hint}'")

    return hierarchy_hint, relation_tag_hint


@traced("search_person")
def search_person(
    ctx: ToolContext, query: str, hints: dict[str, str] | None = None
) -> list[Candidate]:
    """S3.2 시그니처: `(query, hints?) -> Candidate[]`.

    자동 병합·확신도 계산·`ask_user` 호출은 **없다**(원칙1·2·4 -- 판정은
    P3-er). 이 함수는 신호만 모은다: 별칭 정확/부분 일치, 임베딩 코사인
    유사도(인물별 max), `hints` 대조 결과.
    """
    if query is None or not query.strip():
        raise InvalidValue("search_person: query must not be empty")

    hierarchy_hint, relation_tag_hint = _validate_hints(hints)

    session = ctx.session
    q = query.strip()
    q_lower = q.lower()

    # -- 별칭 정확/부분 일치 + 전체 별칭 목록(PersonOut.aliases 용) --
    # 사용자 한 명의 인물·별칭 규모는 작으므로(로컬 단일 사용자 데모) 한 번에
    # 불러와 파이썬에서 매칭한다 -- 양방향 부분 일치("김팀장" ↔ "팀장")를
    # SQL ILIKE 만으로 표현하려면 컬럼을 패턴 쪽에 두는 additional 쿼리가
    # 필요해 오히려 복잡해진다.
    rows = session.execute(
        select(Person, PersonAlias)
        .join(PersonAlias, PersonAlias.person_id == Person.id)
        .where(Person.user_id == ctx.user_id)
    ).all()

    persons_by_id: dict[int, Person] = {}
    aliases_by_person: dict[int, list[str]] = defaultdict(list)
    exact_alias_persons: dict[int, set[str]] = defaultdict(set)
    partial_alias_persons: dict[int, set[str]] = defaultdict(set)

    for person, alias in rows:
        persons_by_id[person.id] = person
        alias_str = alias.alias
        aliases_by_person[person.id].append(alias_str)
        alias_lower = alias_str.lower()
        if alias_lower == q_lower:
            exact_alias_persons[person.id].add(alias_str)
        elif len(q) >= 2 and (q_lower in alias_lower or alias_lower in q_lower):
            partial_alias_persons[person.id].add(alias_str)

    # -- 임베딩 top-K (별칭 단위, D5) → 인물별 max --
    provider = as_provider(ctx.embedder)
    embedded_alias_count = 0
    if provider is not None:
        embedded_alias_count = session.execute(
            select(func.count())
            .select_from(PersonAlias)
            .join(Person, PersonAlias.person_id == Person.id)
            .where(Person.user_id == ctx.user_id)
            .where(PersonAlias.embedding.is_not(None))
        ).scalar_one()

    embedding_ran = provider is not None and embedded_alias_count > 0
    similarity_by_person: dict[int, float] = {}

    if embedding_ran:
        query_vector = provider.embed([q])[0]
        distance_col = PersonAlias.embedding.cosine_distance(query_vector).label("distance")
        topk_stmt = (
            select(PersonAlias.person_id, distance_col)
            .join(Person, PersonAlias.person_id == Person.id)
            .where(Person.user_id == ctx.user_id)
            .where(PersonAlias.embedding.is_not(None))
            .order_by(distance_col)
            .limit(SEARCH_TOP_K)
        )
        for person_id, distance in session.execute(topk_stmt).all():
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))
            if similarity > similarity_by_person.get(person_id, -1.0):
                similarity_by_person[person_id] = similarity

    # -- 후보 집합 = 별칭 일치 ∪ 임베딩 top-K (합집합, 배제 없음) --
    candidate_ids = (
        set(exact_alias_persons) | set(partial_alias_persons) | set(similarity_by_person)
    )

    candidates: list[Candidate] = []
    for person_id in candidate_ids:
        person = persons_by_id[person_id]
        exact_set = exact_alias_persons.get(person_id, set())
        partial_set = partial_alias_persons.get(person_id, set())
        aliases_matched = sorted(exact_set) + sorted(partial_set - exact_set)

        rule_flags = {
            "exact_alias": bool(exact_set),
            "partial_alias": bool(partial_set),
            "hierarchy_match": (
                hierarchy_hint is not None and person.hierarchy == hierarchy_hint
            ),
            "relation_tag_match": (
                relation_tag_hint is not None and person.relation_tag == relation_tag_hint
            ),
            "hierarchy_adjacent": (
                hierarchy_hint is not None
                and _is_hierarchy_adjacent(person.hierarchy, hierarchy_hint)
            ),
            "embedding_skipped": not embedding_ran,
        }
        similarity = similarity_by_person.get(person_id, 0.0) if embedding_ran else 0.0

        person_out = PersonOut(
            id=person.id,
            display_name=person.display_name,
            relation_tag=person.relation_tag,
            hierarchy=person.hierarchy,
            aliases=sorted(aliases_by_person[person_id]),
        )
        candidates.append(
            Candidate(
                person=person_out,
                similarity=similarity,
                aliases_matched=aliases_matched,
                rule_flags=rule_flags,
            )
        )

    # 결정적 정렬: exact_alias 우선 → similarity 내림차순 → person.id 오름차순.
    candidates.sort(
        key=lambda c: (0 if c.rule_flags["exact_alias"] else 1, -c.similarity, c.person.id)
    )
    return candidates
