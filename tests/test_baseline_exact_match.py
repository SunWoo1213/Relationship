"""Refs: P3-baselines S3.7 원칙1 원칙8 -- U3 베이스라인 1(문자열 완전일치) 테스트.

두 층으로 나눠 본다.

1. **순수 층**(DB·네트워크 0) -- `match_exact()` 와 두 정규화 함수. 일치
   인물 수 0/1/2 이상이 그대로 세 결정으로 가는지, `exact_raw` 와
   `exact_norm` 의 차이가 정확히 "호칭 사전 정규화"인지, 정규화가 mention 과
   별칭 **양쪽에 대칭으로** 걸리는지(권고 R-8).
2. **DB 층**(실 PostgreSQL, 롤백 픽스처 `db_session`) -- 사전 상태 조회 범위
   (`user_id`·`embedding IS NULL` 별칭 포함), 동명이인 2건이 `identity` 로
   가고 인물을 **고르지 않는지**(원칙1), 승진 호칭("부장님")이 사전 상태에
   없어 `new_person` 인지(P1 결정 I 가 만든 성질), 호출 전후 행 수가 같은지
   (불변 규약 1), `get_resolver` 두 이름 경로와 `ALL_METHODS` 순서.

임베딩 공급자·LLM 클라이언트를 **주입하지 않는다** -- 이 방식이 둘 다 쓰지
않는다는 것이 정의이고(01-plan 115행 "완전일치는 임베딩·LLM 호출 0회"),
`ctx.embedder=None` 으로도 완전한 판정이 나오는 것이 그 증명이다.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.dictionary import normalize as dictionary_normalize
from app.er.types import ERConfig
from app.tools.context import ToolContext
from evaluation.resolvers import DECISIONS, RESOLVERS, get_resolver
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.exact_match import (
    EMPTY_AFTER_NORMALIZE,
    NORM_METHOD_NAME,
    RAW_METHOD_NAME,
    ExactMatchResolver,
    ExactNormResolver,
    ExactRawResolver,
    KnownPerson,
    load_known_persons,
    match_exact,
    normalize_dictionary,
    normalize_raw,
)

CONFIG = ERConfig()
USER_ID = "exact-match-user"

#: 순수 층이 공유하는 사전 상태. 별칭·표시 이름이 서로 다른 세 인물.
PERSONS = [
    KnownPerson(person_id=1, display_name="김민수", names=("팀장",)),
    KnownPerson(person_id=2, display_name="박지훈", names=("지훈", "PM")),
    KnownPerson(person_id=3, display_name="이모", names=()),
]


# =========================================================================
# 1. 순수 층 -- match_exact() (DB 없음)
# =========================================================================


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
def test_single_match_returns_one_person_id(normalizer) -> None:
    """일치 1건 -- 두 변형 모두 같은 인물 하나."""
    result = match_exact("팀장", PERSONS, normalizer=normalizer)

    assert result.person_ids == (1,)
    assert result.matched_names[1] == ("팀장",)


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
def test_display_name_is_matched_too(normalizer) -> None:
    """별칭뿐 아니라 `persons.display_name` 도 비교 대상이다(01-plan 55행)."""
    result = match_exact("박지훈", PERSONS, normalizer=normalizer)

    assert result.person_ids == (2,)
    assert result.matched_names[2] == ("박지훈",)


def test_two_matches_return_both_in_input_order() -> None:
    """동명이인 2건 -- 순수 층은 **둘 다** 돌려준다(고르지 않는다, 원칙1).
    순서는 입력 순서 그대로여야 한다(재현성, 원칙8)."""
    homonyms = [
        KnownPerson(person_id=10, display_name="김민수", names=("민수",)),
        KnownPerson(person_id=11, display_name="이민수", names=("민수",)),
    ]

    result = match_exact("민수", homonyms, normalizer=normalize_raw)

    assert result.person_ids == (10, 11)
    assert set(result.matched_names) == {10, 11}


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
def test_no_match_returns_empty(normalizer) -> None:
    result = match_exact("부장님", PERSONS, normalizer=normalizer)

    assert result.person_ids == ()
    assert result.matched_names == {}


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
@pytest.mark.parametrize("mention", ["  팀장  ", "\t팀장\n"])
def test_surrounding_whitespace_is_ignored(normalizer, mention: str) -> None:
    assert match_exact(mention, PERSONS, normalizer=normalizer).person_ids == (1,)


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
@pytest.mark.parametrize("mention", ["pm", "Pm", "PM"])
def test_case_is_folded_in_both_variants(normalizer, mention: str) -> None:
    """대소문자 정리는 두 변형 공통 -- `exact_norm` 이 `exact_raw` 보다
    좁아지는 일이 없어야 두 변형의 비교가 뒤집히지 않는다."""
    assert match_exact(mention, PERSONS, normalizer=normalizer).person_ids == (2,)


def test_inner_whitespace_separates_the_two_variants() -> None:
    """`exact_raw` 는 문자열 내부 공백을 지우지 않는다(순수 완전일치).
    `exact_norm` 은 `normalize()` 가 지운다."""
    assert match_exact("김 민수", PERSONS, normalizer=normalize_raw).person_ids == ()
    assert match_exact("김 민수", PERSONS, normalizer=normalize_dictionary).person_ids == (1,)


# --- 두 변형의 차이: 호칭 사전 정규화 -------------------------------------


def test_exact_raw_does_not_match_surname_prefixed_title() -> None:
    """"김팀장"↔"팀장" 은 문자열이 다르다 -- 순수 완전일치는 못 맞힌다.
    이것이 베이스라인 1a 의 **정의**이며 약점이다(원칙8 -- 숨기지 않는다)."""
    assert match_exact("김팀장", PERSONS, normalizer=normalize_raw).person_ids == ()


def test_exact_norm_matches_surname_prefixed_title() -> None:
    """`normalize()` 가 성씨 1글자 접두를 떼므로 "김팀장" → "팀장"."""
    assert match_exact("김팀장", PERSONS, normalizer=normalize_dictionary).person_ids == (1,)


def test_exact_norm_matches_honorific_suffix() -> None:
    """존칭 접미 1개 제거 -- "팀장님" → "팀장"."""
    assert match_exact("팀장님", PERSONS, normalizer=normalize_raw).person_ids == ()
    assert match_exact("팀장님", PERSONS, normalizer=normalize_dictionary).person_ids == (1,)


def test_normalization_is_symmetric_on_both_sides() -> None:
    """**R-8** -- 별칭 쪽이 "김팀장" 이고 mention 이 "팀장" 인 반대 방향도
    같은 결과여야 한다. 한쪽만 정규화하면 여기서 비대칭이 드러난다."""
    reversed_state = [KnownPerson(person_id=7, display_name="김민수", names=("김팀장",))]

    forward = match_exact("김팀장", PERSONS, normalizer=normalize_dictionary)
    backward = match_exact("팀장", reversed_state, normalizer=normalize_dictionary)

    assert forward.person_ids == (1,)
    assert backward.person_ids == (7,)
    # 정규화 키가 양쪽에서 같은 값으로 모인다.
    assert normalize_dictionary("김팀장") == normalize_dictionary("팀장") == "팀장"


def test_exact_norm_is_a_superset_of_exact_raw() -> None:
    """`exact_norm` 이 맞히는 집합은 `exact_raw` 를 포함한다 -- 사전 정규화를
    더 했는데 오히려 덜 맞으면 두 변형의 해석이 꼬인다."""
    for mention in ["팀장", "박지훈", "PM", " 지훈 ", "김팀장", "팀장님", "이모"]:
        raw = set(match_exact(mention, PERSONS, normalizer=normalize_raw).person_ids)
        norm = set(match_exact(mention, PERSONS, normalizer=normalize_dictionary).person_ids)
        assert raw <= norm, mention


# --- 빈 문자열 (R-8) ------------------------------------------------------


@pytest.mark.parametrize("normalizer", [normalize_raw, normalize_dictionary])
@pytest.mark.parametrize("mention", ["", "   ", "\t\n", None])
def test_empty_mention_matches_nothing(normalizer, mention) -> None:
    """정규화 결과가 빈 문자열이면 아무것도 맞지 않는다 -- 빈 이름과의
    우연한 일치를 막는다(예외로 죽지도 않는다, 불변 규약 2)."""
    assert normalizer(mention or "") == ""
    assert match_exact(mention, PERSONS, normalizer=normalizer).person_ids == ()


def test_honorific_only_mention_is_not_empty_after_normalize() -> None:
    """R-8 의 예("님" 단독)는 실제로는 빈 문자열이 되지 않는다 --
    `app.er.dictionary.normalize()` 는 접미 제거를 `len > len(suffix)` 일
    때만 하므로 "님" 은 그대로 "님" 이다. 그래서 이 입력은 빈 문자열 분기가
    아니라 **일치 0건** 분기로 간다(사실을 그대로 기록해 둔다 -- 원칙8).
    빈 문자열이 되는 입력은 공백뿐인 mention 이다."""
    assert dictionary_normalize("님") == "님"
    assert normalize_dictionary("님") == "님"
    assert match_exact("님", PERSONS, normalizer=normalize_dictionary).person_ids == ()


# =========================================================================
# 2. resolver 층 (DB 없이 결정만) -- 세 결정 · 강제 사유
# =========================================================================


class _FakeSession:
    """`load_known_persons()` 를 대신하지 않는다 -- DB 없이 resolver 를
    돌리기 위해 `execute()` 만 흉내 내는 최소 스텁.

    이 테스트가 쓰는 행은 이 방식이 실제로 보는 세 값
    `(person_id, display_name, alias)` 이고, `load_known_persons()` 의
    SELECT 열(U5 부터 `relation_tag`·`hierarchy` 가 추가되어 다섯 열 --
    베이스라인 3 프롬프트가 두 값을 요구한다)에 맞추는 일은 스텁이 한다.
    완전일치 판정은 두 값을 쓰지 않으므로 `None` 으로 채운다."""

    def __init__(self, rows: list[tuple[int, str, str | None]]) -> None:
        self.rows = rows
        self.executed = 0

    def execute(self, statement: Any) -> Any:  # noqa: ARG002 -- 문장은 보지 않는다
        self.executed += 1
        rows = [
            (person_id, display_name, None, None, alias)
            for person_id, display_name, alias in self.rows
        ]

        class _Result:
            def all(self_inner) -> list[tuple[int, str, None, None, str | None]]:  # noqa: N805
                return rows

        return _Result()


def _stub_ctx(rows: list[tuple[int, str, str | None]]) -> ToolContext:
    return ToolContext(session=_FakeSession(rows), session_id="exact-stub", user_id=USER_ID)


_STUB_ROWS = [
    (1, "김민수", "팀장"),
    (2, "박지훈", "지훈"),
    (2, "박지훈", "PM"),
    (3, "이모", None),
]


@pytest.mark.parametrize("resolver_cls", [ExactRawResolver, ExactNormResolver])
def test_single_match_is_merge_with_person_id_and_score_one(resolver_cls) -> None:
    decision = resolver_cls().resolve_mention(_stub_ctx(_STUB_ROWS), "팀장", "발화")

    assert decision.decision == "merge"
    assert decision.person_id == 1
    assert decision.score == 1.0
    assert [c.person_id for c in decision.candidates] == [1]
    assert decision.candidates[0].signals == {"exact": 1.0}
    assert decision.detail["ask_kind"] is None
    assert decision.detail["forced_reason"] is None
    assert decision.detail["match_count"] == 1
    assert decision.detail["matched_names"] == {"1": ["팀장"]}
    assert decision.trace_id is None
    assert (decision.tokens_in, decision.tokens_out) == (0, 0)


@pytest.mark.parametrize("resolver_cls", [ExactRawResolver, ExactNormResolver])
def test_two_matches_are_identity_without_person_id(resolver_cls) -> None:
    """동명이인 2건 -- 임의로 고르지 않는다(원칙1). 후보 **전부**가 답이다."""
    rows = [(10, "김민수", "민수"), (11, "이민수", "민수")]

    decision = resolver_cls().resolve_mention(_stub_ctx(rows), "민수", "발화")

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert [c.person_id for c in decision.candidates] == [10, 11]
    assert decision.detail["ask_kind"] == "identity"
    assert decision.detail["matched_person_ids"] == [10, 11]


@pytest.mark.parametrize("resolver_cls", [ExactRawResolver, ExactNormResolver])
def test_no_match_is_new_person_with_score_zero(resolver_cls) -> None:
    decision = resolver_cls().resolve_mention(_stub_ctx(_STUB_ROWS), "부장님", "발화")

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0
    assert decision.candidates == []
    assert decision.detail["ask_kind"] == "new_person"
    assert decision.detail["forced_reason"] is None


@pytest.mark.parametrize("resolver_cls", [ExactRawResolver, ExactNormResolver])
def test_blank_mention_is_new_person_with_forced_reason(resolver_cls) -> None:
    """**R-8** -- 정규화 결과가 빈 문자열이면 `new_person` +
    `forced_reason="empty_after_normalize"`. 예외로 죽지 않는다(불변 규약 2)."""
    decision = resolver_cls().resolve_mention(_stub_ctx(_STUB_ROWS), "   ", "발화")

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0
    assert decision.detail["forced_reason"] == EMPTY_AFTER_NORMALIZE
    assert decision.detail["normalized_mention"] == ""
    assert decision.detail["match_count"] == 0


def test_variants_differ_only_by_dictionary_normalization() -> None:
    """같은 사전 상태·같은 mention 에서 두 변형의 결정이 갈리는 지점이
    "김팀장" 이다 -- P4 표의 두 행이 무엇을 뜻하는지의 근거."""
    raw = ExactRawResolver().resolve_mention(_stub_ctx(_STUB_ROWS), "김팀장", "발화")
    norm = ExactNormResolver().resolve_mention(_stub_ctx(_STUB_ROWS), "김팀장", "발화")

    assert raw.decision == "new_person"
    assert raw.method == RAW_METHOD_NAME
    assert norm.decision == "merge"
    assert norm.person_id == 1
    assert norm.method == NORM_METHOD_NAME
    assert norm.detail["normalized_mention"] == "팀장"


def test_config_and_hints_are_accepted_and_ignored() -> None:
    """`config`(`ERConfig`)·`hints`·`utterance` 를 받되 쓰지 않는다 --
    임계치를 바꿔도 결정이 같다(불변 규약 4: 이 방식은 두 임계치를 쓰지 않는다).
    P4 의 `T_merge` 스윕에서 이 방식의 선이 수평인 근거다."""
    low = ERConfig(t_merge=0.5, t_new=0.1)
    high = ERConfig(t_merge=0.95, t_new=0.9)

    a = ExactRawResolver().resolve_mention(_stub_ctx(_STUB_ROWS), "팀장", "발화1", config=low)
    b = ExactRawResolver().resolve_mention(
        _stub_ctx(_STUB_ROWS), "팀장", "전혀 다른 발화", {"hierarchy": "상"}, config=high
    )

    assert a.decision == b.decision == "merge"
    assert a.person_id == b.person_id == 1
    assert a.score == b.score == 1.0
    assert a.detail["uses_thresholds"] is False


def test_decision_to_dict_is_json_serializable() -> None:
    """P4 가 `metrics.json`/캐시로 보존한다(재현성, 원칙8)."""
    decision = ExactNormResolver().resolve_mention(_stub_ctx(_STUB_ROWS), "팀장님", "발화")

    payload = json.loads(json.dumps(decision.to_dict(), ensure_ascii=False))
    assert payload["method"] == NORM_METHOD_NAME
    assert payload["decision"] == "merge"
    assert payload["detail"]["uses_llm"] is False
    assert payload["detail"]["uses_embedding"] is False


@pytest.mark.parametrize("resolver_cls", [ExactRawResolver, ExactNormResolver])
def test_same_input_twice_gives_identical_decision(resolver_cls) -> None:
    ctx = _stub_ctx(_STUB_ROWS)
    resolver = resolver_cls()

    first = resolver.resolve_mention(ctx, "팀장", "발화").to_dict()
    second = resolver.resolve_mention(ctx, "팀장", "발화").to_dict()

    assert first == second


def test_supported_decisions_are_all_three_bands() -> None:
    """결정 B(i) -- 완전일치도 `identity` 를 낼 수 있다(동명이인)."""
    for resolver_cls in (ExactRawResolver, ExactNormResolver):
        assert resolver_cls.supported_decisions == DECISIONS
        assert set(resolver_cls.supported_decisions) <= set(DECISIONS)


def test_normalizer_is_not_bound_to_instance() -> None:
    """`staticmethod` 로 감싸지 않으면 인스턴스 접근 시 `self` 가 첫 인자로
    들어간다 -- 그 사고가 생기면 여기서 잡힌다."""
    assert ExactRawResolver.normalizer("  A ") == "a"
    assert ExactNormResolver.normalizer("김팀장님") == "팀장"
    assert ExactMatchResolver.normalizer("  A ") == "a"


# =========================================================================
# 3. DB 층 (실 PostgreSQL · 롤백 픽스처)
# =========================================================================


def _make_person(
    db_session: Any,
    *,
    display_name: str,
    relation_tag: str = "직장",
    hierarchy: str = "동",
    user_id: str = USER_ID,
) -> Person:
    person = Person(
        user_id=user_id,
        display_name=display_name,
        relation_tag=relation_tag,
        hierarchy=hierarchy,
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(
    db_session: Any, person: Person, alias: str, embedding: list[float] | None = None
) -> None:
    db_session.add(
        PersonAlias(
            person_id=person.id,
            alias=alias,
            source=ALIAS_SOURCES[0],
            embedding=embedding,
        )
    )
    db_session.flush()


def _ctx(db_session: Any, *, session_id: str) -> ToolContext:
    """임베딩 공급자를 **주지 않는다**(`embedder=None`) -- 이 방식은 임베딩을
    쓰지 않으므로 공급자 없이도 완전한 판정이 나와야 한다(01-plan 115행)."""
    return ToolContext(session=db_session, session_id=session_id, user_id=USER_ID)


def _row_counts(db_session: Any) -> tuple[int, int, int, int]:
    """부수효과 0(불변 규약 1)을 재는 네 테이블 -- 완전일치는
    `agent_traces` 조차 쓰지 않는다(`@traced` 를 거치지 않는다)."""
    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    questions = db_session.execute(
        select(func.count()).select_from(PendingQuestion)
    ).scalar_one()
    traces = db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()
    return persons, aliases, questions, traces


@pytest.mark.dbtest
def test_load_known_persons_reads_display_name_and_all_aliases(db_session) -> None:
    """별칭이 없는 인물도 표시 이름으로 실린다(`outerjoin`). `embedding` 이
    NULL 인 별칭도 포함한다 -- `search_person` 과 다른 점이다."""
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")
    _add_alias(db_session, lead, "민수형")
    second = _make_person(db_session, display_name="박지훈")

    persons = load_known_persons(_ctx(db_session, session_id="exact-load"))

    assert [p.person_id for p in persons] == [lead.id, second.id]
    assert persons[0].all_names() == ("김민수", "팀장", "민수형")
    assert persons[1].all_names() == ("박지훈",)


@pytest.mark.dbtest
def test_other_users_persons_are_not_candidates(db_session) -> None:
    """`Person.user_id == ctx.user_id` 범위 밖의 인물이 새면 비교가 깨진다."""
    other = _make_person(db_session, display_name="남의사람", user_id="someone-else")
    _add_alias(db_session, other, "팀장")

    decision = ExactRawResolver().resolve_mention(
        _ctx(db_session, session_id="exact-scope"), "팀장", "발화"
    )

    assert decision.decision == "new_person"
    assert decision.candidates == []


@pytest.mark.dbtest
def test_homonyms_go_to_identity_and_no_person_is_chosen(db_session) -> None:
    """**원칙1** -- 사전 상태에 "민수" 별칭을 가진 인물이 둘이면 하나를
    고르지 않고 `identity`(사람에게 묻는다) 다. 후보 둘이 답이다."""
    first = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, first, "민수")
    second = _make_person(db_session, display_name="이민수")
    _add_alias(db_session, second, "민수")

    decision = ExactRawResolver().resolve_mention(
        _ctx(db_session, session_id="exact-homonym"), "민수", "민수랑 점심 먹었어", config=CONFIG
    )

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert {c.person_id for c in decision.candidates} == {first.id, second.id}
    assert {c.display_name for c in decision.candidates} == {"김민수", "이민수"}
    assert decision.detail["ask_kind"] == "identity"


@pytest.mark.dbtest
@pytest.mark.parametrize("method", [RAW_METHOD_NAME, NORM_METHOD_NAME])
def test_promotion_title_is_new_person_because_state_lacks_it(db_session, method: str) -> None:
    """승진 호칭 -- 사전 상태에는 대화 전 알려진 별칭만 있다(P1 결정 I).
    "부장님" 은 대화에서 배워야 할 호칭이므로 두 변형 모두 `new_person`.
    이것이 이 베이스라인의 실패 유형이고 숨기지 않는다(원칙8)."""
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")

    decision = get_resolver(method).resolve_mention(
        _ctx(db_session, session_id=f"exact-promotion-{method}"),
        "부장님",
        "김부장님이 이번에 승진하셨대",
        config=CONFIG,
    )

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] is None  # 실패가 아니라 판정 결과다


@pytest.mark.dbtest
@pytest.mark.parametrize(
    ("mention", "expected"),
    [("팀장", "merge"), ("민수", "identity"), ("부장님", "new_person"), ("  ", "new_person")],
    ids=["merge", "identity", "new_person", "blank"],
)
def test_no_side_effect_on_any_table(db_session, mention: str, expected: str) -> None:
    """네 결정 어디에서도 행이 생기지 않는다(불변 규약 1) -- 완전일치는
    `SELECT` 만 한다. `proposed` 와 달리 `agent_traces` 도 늘지 않는다."""
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")
    _add_alias(db_session, lead, "민수")
    other = _make_person(db_session, display_name="이민수")
    _add_alias(db_session, other, "민수")

    before = _row_counts(db_session)
    decision = ExactRawResolver().resolve_mention(
        _ctx(db_session, session_id=f"exact-side-effect-{expected}"),
        mention,
        "발화",
        config=CONFIG,
    )

    assert decision.decision == expected
    assert _row_counts(db_session) == before


@pytest.mark.dbtest
def test_exact_norm_matches_surname_prefixed_title_against_real_state(db_session) -> None:
    """DB 사전 상태에서도 두 변형의 차이가 그대로 나온다."""
    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")
    ctx = _ctx(db_session, session_id="exact-norm-db")

    raw = get_resolver(RAW_METHOD_NAME).resolve_mention(ctx, "김팀장", "발화", config=CONFIG)
    norm = get_resolver(NORM_METHOD_NAME).resolve_mention(ctx, "김팀장", "발화", config=CONFIG)

    assert raw.decision == "new_person"
    assert norm.decision == "merge"
    assert norm.person_id == lead.id


# =========================================================================
# 4. 방식 표 등록 경로
# =========================================================================


def test_both_variants_are_registered() -> None:
    assert RESOLVERS[RAW_METHOD_NAME] is ExactRawResolver
    assert RESOLVERS[NORM_METHOD_NAME] is ExactNormResolver


def test_all_methods_order_after_u3() -> None:
    """등록 순서 = `evaluation/resolvers/__init__.py` 의 import 순서.
    이름은 `metrics.json` 의 키다(P4 인계 4).

    이 테스트가 보는 것은 **두 변형이 `proposed` 다음에 이 순서로 온다**는
    것뿐이다 -- 뒤에 붙는 방식(U4 `embedding_only`·U5 `llm_single`)까지
    여기서 단언하면 단위가 추가될 때마다 U3 테스트가 깨진다. 전체 목록은
    그 단위의 테스트가 소유한다(U4: `test_all_methods_order_after_u4`)."""
    assert resolver_registry.ALL_METHODS[:3] == ("proposed", RAW_METHOD_NAME, NORM_METHOD_NAME)


@pytest.mark.parametrize(
    ("method", "expected_cls"),
    [(RAW_METHOD_NAME, ExactRawResolver), (NORM_METHOD_NAME, ExactNormResolver)],
)
def test_get_resolver_returns_the_right_variant(method: str, expected_cls) -> None:
    resolver = get_resolver(method)

    assert isinstance(resolver, expected_cls)
    assert resolver.name == method
    assert resolver.supported_decisions == DECISIONS
