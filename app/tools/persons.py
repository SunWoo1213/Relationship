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

## `create_person`/`update_person` -- 긍정 답 규약 (F-b97a06, U4 에서 확정)

D1("승인 시에만 `create_person`")과 D6("확인을 거친 경우에만 `display_name`
갱신")은 **답했는가**가 아니라 **무엇이라 답했는가**를 요구한다. 이 모듈은
그 판별 규약을 다음과 같이 정한다 -- `app/tools/questions.py`(U6)의
`ask_user` 가 같은 규약으로 `pending_questions.context` 를 채워야 한다:

- `pending_questions.context`(JSONB)에 `app.tools.types.AFFIRMATIVE_KEY`
  (`"affirmative_options"`) 키로 긍정 선택지 문자열 목록을 넣는다.
  예: `{"affirmative_options": ["응, 기억해줘"]}`.
- 이 키가 없으면(구버전 질문, 호출자 실수) **거부가 기본값**이다 -- 원칙1과
  같은 비대칭: "긍정인지 알 수 없음"을 "긍정 아님"으로 취급한다.
- `pending_questions.answer` 가 `affirmative_options` 안에 있어야만
  `_require_confirmation` 이 통과한다.

`_require_confirmation(ctx, kinds=...)` 은 이 규약과 D1 강제의 나머지 조건
(존재·`kind`·`answered_at`·`session_id`)을 한 곳에서 검사한다. 예외
(`ConfirmationRequired`) 메시지에는 사유 코드(`reason` 속성)만 담고 질문
원문·답 문자열은 절대 넣지 않는다 -- `question_id` 가 아예 없는 경우와
있지만 조건 미충족인 경우를 같은 방식으로 다뤄, 존재 여부 자체를 흘리지
않는다.

## 별칭 격상 규칙 (미결 7, D5)

같은 인물에 같은 문자열 별칭이 이미 있으면 새 행을 만들지 않고 `source`
(필요하면 `confirmed_at`)만 **격상**한다 -- 별칭은 삭제·격하하지 않는다.
격상 순서는 `ALIAS_SOURCES = ("user_said", "confirmed", "system")` 의
튜플 순서 그대로다(인덱스가 클수록 상위):

| 기존 \\ 신규 | user_said | confirmed | system |
|---|---|---|---|
| `user_said` | 유지(같은 값, 변화 없음) | **confirmed 로 격상** | **system 으로 격상** |
| `confirmed` | 유지(격하 없음) | 유지(같은 값) | **system 으로 격상** |
| `system` | 유지(격하 없음) | 유지(격하 없음) | 유지(같은 값) |

`confirmed_at` 은 격상 결과가 `confirmed` 이고 아직 비어 있을 때만 채운다.
`system` 으로 격상되어도 기존 `confirmed_at` 값은 지우지 않는다(확인
이력을 잃지 않는다). 다른 인물의 같은 별칭 문자열은 이 규칙과 무관하다
(동명이인 허용, 막지 않는다).
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    ALIAS_SOURCES,
    HIERARCHIES,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    RELATION_TAGS,
)
from app.embedding import EmbedderCallable, EmbeddingProvider, as_provider
from app.settings import DEFAULT_FACT_CONFIDENCE, SEARCH_TOP_K
from app.tools.context import ToolContext, traced
from app.tools.types import (
    AFFIRMATIVE_KEY,
    Candidate,
    ConfirmationRequired,
    InvalidValue,
    PersonNotFound,
    PersonOut,
)

#: 별칭 격상 순서(모듈 docstring "별칭 격상 규칙" 표 참고). 인덱스가 클수록
#: 상위 -- `ALIAS_SOURCES` 튜플 순서 그대로다(단일 출처: 이 상수를 재정의하지
#: 않는다).
_ALIAS_RANK = {source: index for index, source in enumerate(ALIAS_SOURCES)}

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


def _require_confirmation(
    ctx: ToolContext, *, kinds: tuple[str, ...]
) -> PendingQuestion:
    """D1/D6 확인 검사 + F-b97a06 긍정 답 규약(모듈 docstring 참고).

    `create_person`/`update_person(display_name=...)` 가 진행되려면 다음이
    **모두** 참이어야 한다. 하나라도 아니면 `ConfirmationRequired`(사유는
    `reason` 속성에만 -- 질문 원문·답 문자열은 예외 메시지에 담지 않는다):

    1. `ctx.confirmed_question_id` 가 `None` 이 아니다 (`no_confirmation`).
    2. 그 id 의 `pending_questions` 행이 존재한다 -- 없으면 존재 여부를
       흘리지 않기 위해 `QuestionNotFound` 가 아니라 이 예외를 그대로 쓴다
       (`not_found`).
    3. `kind` 가 `kinds` 안에 있다 (`wrong_kind`).
    4. `answered_at IS NOT NULL` (`not_answered`).
    5. `session_id == ctx.session_id` (`session_mismatch`).
    6. `context` 에 `AFFIRMATIVE_KEY` 가 있고 `answer` 가 그 목록 안에 있다
       (`not_affirmative`) -- 키가 없으면 안전한 기본값으로 거부한다.

    통과하면 그 `PendingQuestion` 행을 돌려준다(호출자가 재사용할 일은
    없지만, 검사 결과를 재조회 없이 넘길 수 있게 한다).
    """
    if ctx.confirmed_question_id is None:
        raise ConfirmationRequired("no_confirmation")

    question = ctx.session.get(PendingQuestion, ctx.confirmed_question_id)
    if question is None:
        raise ConfirmationRequired("not_found")

    if question.kind not in kinds:
        raise ConfirmationRequired("wrong_kind")

    if question.answered_at is None:
        raise ConfirmationRequired("not_answered")

    if question.session_id != ctx.session_id:
        raise ConfirmationRequired("session_mismatch")

    context = question.context if isinstance(question.context, dict) else {}
    affirmative_options = context.get(AFFIRMATIVE_KEY)
    if not affirmative_options or question.answer not in affirmative_options:
        raise ConfirmationRequired("not_affirmative")

    return question


def _dedupe_aliases(raw: list[str]) -> list[str]:
    """strip → 빈 값 제외 → 중복 제거(대소문자 구분 유지, 첫 등장 순서 보존)."""
    seen: set[str] = set()
    result: list[str] = []
    for item in raw:
        stripped = item.strip() if isinstance(item, str) else ""
        if not stripped or stripped in seen:
            continue
        seen.add(stripped)
        result.append(stripped)
    return result


def _add_alias(
    session: Session,
    person: Person,
    alias: str,
    *,
    source: str,
    embedder: "EmbeddingProvider | EmbedderCallable | None" = None,
    confirmed_at=None,
) -> PersonAlias:
    """별칭 upsert(모듈 docstring "별칭 격상 규칙" 표). 같은 인물에 같은
    문자열이 이미 있으면 새 행을 만들지 않고 격상만 한다 -- 삭제·격하 없음
    (미결 7, D6). 새로 만들 때 `embedder` 가 있으면(`app.embedding.as_provider`
    로 정규화) 그 자리에서 임베딩을 채운다(D5 "확정되면 즉시 임베딩").
    """
    existing = session.execute(
        select(PersonAlias)
        .where(PersonAlias.person_id == person.id)
        .where(PersonAlias.alias == alias)
    ).scalar_one_or_none()

    if existing is not None:
        if _ALIAS_RANK[source] > _ALIAS_RANK[existing.source]:
            existing.source = source
            if source == ALIAS_SOURCES[1] and existing.confirmed_at is None:
                existing.confirmed_at = confirmed_at
            session.flush()
        return existing

    embedding = None
    provider = as_provider(embedder)
    if provider is not None:
        embedding = provider.embed([alias])[0]

    row = PersonAlias(
        person_id=person.id,
        alias=alias,
        source=source,
        embedding=embedding,
        confirmed_at=confirmed_at if source == ALIAS_SOURCES[1] else None,
    )
    session.add(row)
    session.flush()
    return row


def _owned_person(session: Session, person_id: int, user_id: str) -> Person:
    """`person_id` 를 `user_id` 소유로 조회한다(security.md §5 인물 조회 격리).

    없거나 다른 `user_id` 소유면 `PersonNotFound`. `update_person` 과
    `app/tools/records.py`(U5 `add_event`/`add_schedule`)가 이 helper 를
    공유한다 -- 소유 확인 로직을 두 곳에 중복 구현하지 않는다.
    """
    person = session.execute(
        select(Person).where(Person.id == person_id).where(Person.user_id == user_id)
    ).scalar_one_or_none()
    if person is None:
        raise PersonNotFound("person_not_found")
    return person


def _person_out(session: Session, person: Person) -> PersonOut:
    """`person` 의 현재 별칭 전체를 조회해 `PersonOut` 으로 만든다."""
    aliases = (
        session.execute(
            select(PersonAlias.alias).where(PersonAlias.person_id == person.id)
        )
        .scalars()
        .all()
    )
    return PersonOut(
        id=person.id,
        display_name=person.display_name,
        relation_tag=person.relation_tag,
        hierarchy=person.hierarchy,
        aliases=sorted(aliases),
    )


@traced("create_person")
def create_person(
    ctx: ToolContext,
    display_name: str,
    aliases: list[str],
    relation_tag: str,
    hierarchy: str,
) -> PersonOut:
    """S3.2 시그니처: `(display_name, aliases, relation_tag, hierarchy) -> Person`.

    D1(원칙1): **answered `new_person` 질문을 거치지 않으면 절대 실행하지
    않는다.** 직접 호출은 `_require_confirmation` 에서 `ConfirmationRequired`
    로 실패해야 한다(D01 카드 "코드에서 지켜야 할 것"). 확신도·후보 검색·
    다른 인물과의 병합은 이 함수의 일이 아니다 -- `search_person`/P3-er 가
    이미 끝낸 판정의 결과로서만 호출된다.

    별칭 처리: `aliases` 는 strip·중복 제거 후 각각 `confirmed`
    (`confirmed_at=ctx.now()`, 확인 질문을 거쳤으므로) 로, `display_name`
    자체는 `system` 별칭으로 누적한다(격상 규칙이 중복을 정리한다).
    """
    _require_confirmation(ctx, kinds=("new_person",))

    if display_name is None or not display_name.strip():
        raise InvalidValue("create_person: display_name must not be empty")
    normalized_display_name = display_name.strip()

    if relation_tag not in RELATION_TAGS:
        raise InvalidValue(f"create_person: invalid relation_tag '{relation_tag}'")
    if hierarchy not in HIERARCHIES:
        raise InvalidValue(f"create_person: invalid hierarchy '{hierarchy}'")

    person = Person(
        user_id=ctx.user_id,
        display_name=normalized_display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )
    ctx.session.add(person)
    ctx.session.flush()

    confirmed_at = ctx.now()
    for alias in _dedupe_aliases(list(aliases or [])):
        _add_alias(
            ctx.session,
            person,
            alias,
            source=ALIAS_SOURCES[1],
            embedder=ctx.embedder,
            confirmed_at=confirmed_at,
        )

    _add_alias(
        ctx.session,
        person,
        normalized_display_name,
        source=ALIAS_SOURCES[2],
        embedder=ctx.embedder,
    )

    ctx.session.flush()
    return _person_out(ctx.session, person)


@traced("update_person")
def update_person(
    ctx: ToolContext,
    person_id: int,
    facts: list[dict[str, str]] | None = None,
    new_alias: str | None = None,
    display_name: str | None = None,
) -> PersonOut:
    """S3.2 시그니처: `(person_id, facts?, new_alias?, display_name?) -> Person`.

    확신도·병합·다른 인물로의 연결은 이 함수에 **없다**(원칙1) -- 여기서
    다루는 것은 오직 "이미 정해진 이 `person_id`" 하나의 별칭 누적·사실
    upsert·표시 이름 갱신뿐이다.

    - `display_name` 은 현재 값과 다를 때만 확인(answered `identity` 또는
      `new_person` 질문, D6)을 요구하고, 통과하면 갱신 + 새 이름을 `system`
      별칭으로 누적한다(F-2418ef). 이전 표시 이름의 별칭 행은 지우지 않는다.
      같은 값이면 확인도 변경도 없다.
    - `new_alias` 는 `user_said` 로 upsert(격상 규칙, 미결 7). 다른 인물의
      같은 별칭 문자열은 막지 않는다(동명이인).
    - `facts` 는 `(person_id, key)` 애플리케이션 upsert(결정 6) --
      `DEFAULT_FACT_CONFIDENCE` 로 값·확신도를 갱신하거나 새로 만든다.
    - 세 인자 모두 `None` 이면 `InvalidValue`.
    """
    if facts is None and new_alias is None and display_name is None:
        raise InvalidValue("update_person: at least one of facts/new_alias/display_name required")

    person = _owned_person(ctx.session, person_id, ctx.user_id)

    if display_name is not None:
        if not display_name.strip():
            raise InvalidValue("update_person: display_name must not be empty")
        normalized_display_name = display_name.strip()
        if normalized_display_name != person.display_name:
            _require_confirmation(ctx, kinds=("identity", "new_person"))
            person.display_name = normalized_display_name
            _add_alias(
                ctx.session,
                person,
                normalized_display_name,
                source=ALIAS_SOURCES[2],
                embedder=ctx.embedder,
            )
            ctx.session.flush()

    if new_alias is not None:
        if not new_alias.strip():
            raise InvalidValue("update_person: new_alias must not be empty")
        _add_alias(
            ctx.session,
            person,
            new_alias.strip(),
            source=ALIAS_SOURCES[0],
            embedder=ctx.embedder,
        )

    if facts is not None:
        for fact in facts:
            key = fact.get("key") if isinstance(fact, dict) else None
            value = fact.get("value") if isinstance(fact, dict) else None
            if not isinstance(key, str) or not key.strip():
                raise InvalidValue("update_person: fact key must be a non-empty string")
            if not isinstance(value, str) or not value.strip():
                raise InvalidValue("update_person: fact value must be a non-empty string")
            normalized_key = key.strip()
            normalized_value = value.strip()

            existing_fact = (
                ctx.session.execute(
                    select(PersonFact)
                    .where(PersonFact.person_id == person.id)
                    .where(PersonFact.key == normalized_key)
                    .order_by(PersonFact.updated_at.desc())
                )
                .scalars()
                .first()
            )
            if existing_fact is not None:
                existing_fact.value = normalized_value
                existing_fact.confidence = DEFAULT_FACT_CONFIDENCE
            else:
                ctx.session.add(
                    PersonFact(
                        person_id=person.id,
                        key=normalized_key,
                        value=normalized_value,
                        confidence=DEFAULT_FACT_CONFIDENCE,
                    )
                )

    ctx.session.flush()
    return _person_out(ctx.session, person)
