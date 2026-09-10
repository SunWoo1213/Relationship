"""Refs: P3-baselines S3.7 D4 D5 D10 원칙2 -- U4 베이스라인 2(임베딩 단독) 테스트.

두 층으로 나눠 본다.

1. **순수 층**(DB·네트워크 0) -- `decide_from_candidates()`. `s_emb` 가
   정확히 `T_merge`/`T_new` 인 경계값이 `app.er.confidence.ge_with_tolerance()`
   와 **같은 결과**를 내는지, 바로 아래 값이 한 칸 내려가는지, 후보 0건·
   동점·임베딩 공급자 없음이 예외 대신 결정 + `forced_reason` 으로 표현되는지
   (불변 규약 2), 동점에서 인물을 **고르지 않는지**(원칙1).
2. **DB 층**(실 PostgreSQL, 롤백 픽스처 `db_session` + `grouped_embedder`) --
   통제한 유사도에서 "팀장↔부장님 > 팀장↔이모"(D4 검증 기준)가 밴드에
   반영되는지, `T_merge` 를 바꾼 `ERConfig` 를 넘기면 같은 입력의 밴드가
   바뀌는지(P4 `T_merge` 스윕 배관, S3.7), 호출 전후 인물·별칭·질문 행 수가
   같은지(불변 규약 1), `get_resolver` 경로와 `ALL_METHODS` 순서.

임베딩은 **결정적 가짜 임베딩**(`grouped_embedder`, 결정 H(i))만 쓴다 --
네트워크 0·실 키 0·비용 0 이고 같은 입력에 같은 수치가 나온다(원칙8).
LLM 클라이언트는 아예 주입 경로가 없다(01-plan 115행 "임베딩 단독은 LLM
호출 0회·규칙 필터 미사용").
"""

from __future__ import annotations

import inspect
import json
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.models import ALIAS_SOURCES, AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.confidence import band_for, ge_with_tolerance
from app.er.types import ERConfig, ScoredCandidate
from app.tools.context import ToolContext
from evaluation.resolvers import DECISIONS, RESOLVERS, get_resolver
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.embedding_only import (
    EMPTY_MENTION,
    EMBEDDING_SKIPPED,
    METHOD_NAME,
    NO_CANDIDATES,
    TIE,
    EmbeddingOnlyResolver,
    approx_equal,
    decide_from_candidates,
)

CONFIG = ERConfig()  # t_merge=0.8, t_new=0.3 (D10 기본값)
USER_ID = "embedding-only-user"


def _candidate(
    person_id: int,
    s_emb: float,
    *,
    display_name: str | None = None,
    embedding_skipped: bool = False,
) -> ScoredCandidate:
    """순수 층이 쓰는 후보 하나. `rule_flags` 는 `search_person` 이 채우는
    6개 중 이 방식이 읽는 하나(`embedding_skipped`)만 세운다."""

    return ScoredCandidate(
        person_id=person_id,
        display_name=display_name or f"인물{person_id}",
        s_emb=s_emb,
        rule_flags={"embedding_skipped": embedding_skipped},
    )


# =========================================================================
# 1. 순수 층 -- 경계값 (DB 없음)
# =========================================================================


def test_s_emb_exactly_t_merge_is_merge() -> None:
    """정확히 `T_merge` 인 값은 `>=` 쪽 -- `band_for()` 규약 그대로(D10)."""
    decision = decide_from_candidates([_candidate(1, CONFIG.t_merge)], CONFIG, mention="팀장")

    assert decision.decision == "merge"
    assert decision.person_id == 1
    assert decision.score == pytest.approx(CONFIG.t_merge)
    assert decision.detail["forced_reason"] is None


def test_s_emb_exactly_t_new_is_identity() -> None:
    decision = decide_from_candidates([_candidate(1, CONFIG.t_new)], CONFIG, mention="팀장")

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.score == pytest.approx(CONFIG.t_new)


@pytest.mark.parametrize(
    ("s_emb", "expected"),
    [
        (0.8 - 1e-3, "identity"),  # T_merge 바로 아래 -> 한 칸 내려간다
        (0.3 - 1e-3, "new_person"),  # T_new 바로 아래
        (1.0, "merge"),
        (0.0, "new_person"),
    ],
)
def test_values_just_below_thresholds_step_down(s_emb: float, expected: str) -> None:
    decision = decide_from_candidates([_candidate(1, s_emb)], CONFIG, mention="팀장")

    assert decision.decision == expected


@pytest.mark.parametrize(
    "s_emb",
    [
        0.0,
        0.3 - 1e-12,
        0.3,
        0.3 + 1e-12,
        0.5,
        0.8 - 1e-12,
        0.8,
        0.8 + 1e-12,
        0.95,
        1.0,
    ],
)
def test_decision_equals_band_for_on_s_emb(s_emb: float) -> None:
    """이 방식의 결정 = `band_for(s_emb, config)` (동점·후보 0건이 아닌 한).
    임계치를 새로 정의하지 않는다는 것의 기계적 증명이다(불변 규약 4,
    결정 D(i))."""

    decision = decide_from_candidates([_candidate(1, s_emb)], CONFIG, mention="팀장")

    assert decision.decision == band_for(s_emb, CONFIG)
    assert decision.detail["band_by_threshold"] == band_for(s_emb, CONFIG)


@pytest.mark.parametrize("threshold_name", ["t_merge", "t_new"])
def test_tolerance_matches_ge_with_tolerance_at_the_boundary(threshold_name: str) -> None:
    """허용오차의 단일 출처(`ge_with_tolerance`, P3-er F-7fe239)를 그대로
    따르는지 -- 부동소수 표현 오차만큼 아래인 값도 `>=` 쪽으로 간다."""

    threshold = getattr(CONFIG, threshold_name)
    nudged = threshold - 1e-12
    assert ge_with_tolerance(nudged, threshold) is True

    decision = decide_from_candidates([_candidate(1, nudged)], CONFIG, mention="팀장")

    assert decision.decision == ("merge" if threshold_name == "t_merge" else "identity")


def test_approx_equal_uses_the_same_tolerance() -> None:
    assert approx_equal(0.8, 0.8) is True
    assert approx_equal(0.8, 0.8 - 1e-12) is True
    assert approx_equal(0.8, 0.79) is False


# =========================================================================
# 2. 순수 층 -- 후보 0건 · 동점 · 공급자 없음 (불변 규약 2)
# =========================================================================


def test_no_candidates_is_new_person_with_forced_reason() -> None:
    decision = decide_from_candidates([], CONFIG, mention="부장님")

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0
    assert decision.candidates == []
    assert decision.detail["forced_reason"] == NO_CANDIDATES
    assert decision.detail["candidate_count"] == 0


def test_tie_above_t_merge_is_identity_not_an_arbitrary_pick() -> None:
    """최고 `s_emb` 가 같은 후보 2건 -- 하나를 임의로 고르는 것이 곧
    오병합이므로 고르지 않는다(원칙1)."""

    decision = decide_from_candidates(
        [_candidate(1, 0.9), _candidate(2, 0.9)], CONFIG, mention="민수"
    )

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert decision.detail["forced_reason"] == TIE
    assert decision.detail["band_by_threshold"] == "merge"  # 강등이 있었다는 근거
    assert decision.detail["tied_person_ids"] == [1, 2]
    assert [c.person_id for c in decision.candidates] == [1, 2]


def test_tie_within_floating_point_tolerance_is_still_a_tie() -> None:
    decision = decide_from_candidates(
        [_candidate(1, 0.9), _candidate(2, 0.9 - 1e-12)], CONFIG, mention="민수"
    )

    assert decision.decision == "identity"
    assert decision.detail["forced_reason"] == TIE


def test_near_tie_beyond_tolerance_still_merges_the_top_candidate() -> None:
    """동점 규칙이 "가까우면 무조건 묻는다"로 번지지 않는지 -- 그렇게 되면
    이 베이스라인이 인위적으로 약해진다(원칙8)."""

    decision = decide_from_candidates(
        [_candidate(1, 0.9), _candidate(2, 0.85)], CONFIG, mention="민수"
    )

    assert decision.decision == "merge"
    assert decision.person_id == 1
    assert decision.detail["forced_reason"] is None
    assert decision.detail["tied_person_ids"] == []


def test_tie_below_t_merge_is_not_a_forced_downgrade() -> None:
    """이미 `identity` 인 밴드에서는 고를 일이 없으므로 `tie` 강등이
    아니다 -- 강등 사유를 부풀리면 P4 가 원인을 잘못 읽는다(원칙9)."""

    decision = decide_from_candidates(
        [_candidate(1, 0.5), _candidate(2, 0.5)], CONFIG, mention="민수"
    )

    assert decision.decision == "identity"
    assert decision.detail["forced_reason"] is None
    assert decision.detail["band_by_threshold"] == "identity"
    assert decision.detail["tied_person_ids"] == [1, 2]


def test_embedding_skipped_gives_zero_score_and_new_person() -> None:
    """공급자 없음 -> `s_emb=0` -> `new_person`(01-plan 103행). 별칭이
    정확히 일치해 후보로 잡힌 인물이라도 이 방식은 `s_emb` 만 보므로
    올라가지 않는다."""

    decision = decide_from_candidates(
        [_candidate(1, 0.0, embedding_skipped=True)], CONFIG, mention="팀장"
    )

    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0
    assert decision.detail["embedding_skipped"] is True
    assert decision.detail["forced_reason"] == EMBEDDING_SKIPPED
    assert decision.candidates[0].signals["embedding_skipped"] == 1.0


def test_embedding_skipped_flag_is_false_when_provider_ran() -> None:
    decision = decide_from_candidates([_candidate(1, 0.9)], CONFIG, mention="팀장")

    assert decision.detail["embedding_skipped"] is False
    assert decision.candidates[0].signals["embedding_skipped"] == 0.0


def test_blank_mention_returns_new_person_without_touching_the_db() -> None:
    """빈 mention 은 `search_person` 이 `InvalidValue` 를 던지는 입력이다 --
    한 방식만 예외로 죽으면 분모가 달라진다(불변 규약 2). `ctx=None` 을
    넘겨 DB 접근이 없다는 것도 함께 보인다."""

    decision = EmbeddingOnlyResolver().resolve_mention(None, "   ", "발화")  # type: ignore[arg-type]

    assert decision.decision == "new_person"
    assert decision.detail["forced_reason"] == EMPTY_MENTION
    assert decision.candidates == []


# =========================================================================
# 3. 순수 층 -- 반환값의 형태·재현성·방식 정의
# =========================================================================


def test_candidates_are_sorted_by_s_emb_then_person_id() -> None:
    decision = decide_from_candidates(
        [_candidate(7, 0.2), _candidate(3, 0.9), _candidate(5, 0.9), _candidate(9, 0.4)],
        CONFIG,
        mention="민수",
    )

    assert [c.person_id for c in decision.candidates] == [3, 5, 9, 7]
    assert [c.score for c in decision.candidates] == [0.9, 0.9, 0.4, 0.2]


def test_all_candidates_are_kept_with_their_own_s_emb() -> None:
    """`identity` 에서 후보 전부가 답이다(불변 규약 3) -- 후보별 점수는 그
    후보의 `s_emb` 자체다."""

    decision = decide_from_candidates(
        [_candidate(1, 0.7), _candidate(2, 0.31)], CONFIG, mention="민수"
    )

    assert decision.decision == "identity"
    assert decision.person_id is None
    assert {c.person_id: c.signals["s_emb"] for c in decision.candidates} == {
        1: pytest.approx(0.7),
        2: pytest.approx(0.31),
    }


def test_signals_do_not_report_an_uncomputed_rule_score() -> None:
    """2단계 규칙 필터를 돌리지 않았으므로 `s_rule` 키는 없다 -- 계산된 적
    없는 값을 0.0 으로 적으면 "규칙 신호가 0 이었다"로 오독된다(원칙9)."""

    decision = decide_from_candidates([_candidate(1, 0.9)], CONFIG, mention="팀장")

    assert set(decision.candidates[0].signals) == {"s_emb", "embedding_skipped"}


def test_detail_declares_which_signals_were_used() -> None:
    decision = decide_from_candidates([_candidate(1, 0.9)], CONFIG, mention="팀장")

    assert decision.detail["uses_embedding"] is True
    assert decision.detail["uses_llm"] is False
    assert decision.detail["uses_rules"] is False
    assert decision.detail["uses_thresholds"] is True
    assert decision.detail["thresholds"] == {"t_merge": 0.8, "t_new": 0.3}


@pytest.mark.parametrize(
    ("s_emb", "expected_kind"),
    [(0.9, None), (0.5, "identity"), (0.1, "new_person")],
)
def test_ask_kind_follows_the_decision(s_emb: float, expected_kind: str | None) -> None:
    """`ask_user` 를 부르지 않고(불변 규약 1) 물었을 `kind` 만 남긴다 --
    P4 `ask_user_rate_by_kind` 입력(eval-harness §2)."""

    decision = decide_from_candidates([_candidate(1, s_emb)], CONFIG, mention="팀장")

    assert decision.detail["ask_kind"] == expected_kind


def test_method_name_is_the_registered_name() -> None:
    decision = decide_from_candidates([_candidate(1, 0.9)], CONFIG, mention="팀장")

    assert decision.method == METHOD_NAME == "embedding_only"


def test_decision_to_dict_is_json_serializable() -> None:
    decision = decide_from_candidates(
        [_candidate(1, 0.9), _candidate(2, 0.4)], CONFIG, mention="팀장"
    )

    dumped = json.loads(json.dumps(decision.to_dict(), ensure_ascii=False))

    assert dumped["method"] == METHOD_NAME
    assert dumped["decision"] == "merge"
    assert dumped["detail"]["top_s_emb"] == pytest.approx(0.9)


def test_same_input_twice_gives_identical_decision() -> None:
    candidates = [_candidate(1, 0.9), _candidate(2, 0.4)]

    first = decide_from_candidates(candidates, CONFIG, mention="팀장").to_dict()
    second = decide_from_candidates(candidates, CONFIG, mention="팀장").to_dict()

    assert first == second


def test_config_changes_the_band_for_the_same_input() -> None:
    """P4 `T_merge` 스윕 배관(S3.7) -- 같은 입력, 다른 임계치, 다른 밴드."""

    candidates = [_candidate(1, 0.85)]

    low = decide_from_candidates(candidates, ERConfig(t_merge=0.8, t_new=0.3), mention="팀장")
    high = decide_from_candidates(candidates, ERConfig(t_merge=0.95, t_new=0.3), mention="팀장")

    assert low.decision == "merge"
    assert low.person_id == 1
    assert high.decision == "identity"
    assert high.person_id is None
    assert low.score == high.score  # 점수는 같고 분기만 달라진다


def test_module_does_not_import_llm_or_rule_stages() -> None:
    """방식의 **정의**를 코드로 단언한다(01-plan 115행) -- 이 모듈은
    3단계 LLM 판정도 2단계 규칙 필터도 부르지 않는다."""

    from evaluation.resolvers import embedding_only

    source = inspect.getsource(embedding_only)
    for forbidden in ("app.er.judge", "app.er.rules", "app.er.pipeline"):
        assert forbidden not in source


def test_resolver_takes_no_client_arguments() -> None:
    """생성자에 주입 경로가 없는 것이 "LLM 호출 0회"의 구조적 보장이다."""

    parameters = list(inspect.signature(EmbeddingOnlyResolver).parameters)

    assert parameters == []


# =========================================================================
# 4. DB 층 (실 PostgreSQL · 롤백 픽스처 · 결정적 가짜 임베딩)
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


def _ctx(db_session: Any, *, session_id: str, embedder: Any = None) -> ToolContext:
    return ToolContext(
        session=db_session, session_id=session_id, user_id=USER_ID, embedder=embedder
    )


def _state_counts(db_session: Any) -> tuple[int, int, int]:
    """부수효과 0(불변 규약 1)을 재는 세 테이블. `agent_traces` 는 여기
    포함하지 않는다 -- `search_person` 이 `@traced` 라 툴 호출 기록 1행이
    남는 것은 감싼 함수의 성질이고 인물 상태를 바꾸지 않는다(proposed.py
    와 같은 예외)."""

    persons = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
    aliases = db_session.execute(select(func.count()).select_from(PersonAlias)).scalar_one()
    questions = db_session.execute(
        select(func.count()).select_from(PendingQuestion)
    ).scalar_one()
    return persons, aliases, questions


def _seed_promotion_state(db_session: Any, embedder: Any) -> tuple[Person, Person]:
    """D4 검증 기준의 사전 상태 -- "팀장"(같은 그룹)과 "이모"(미등재).
    `grouped_embedder` 가 "팀장"·"김팀장"·"부장님" 을 한 그룹으로 묶으므로
    "부장님" 은 팀장 쪽과 유사도 ≈0.85, 이모 쪽과는 ≈0 이다."""

    lead = _make_person(db_session, display_name="김민수", hierarchy="동")
    _add_alias(db_session, lead, "팀장", embedder(["팀장"])[0])
    _add_alias(db_session, lead, "김팀장", embedder(["김팀장"])[0])

    aunt = _make_person(db_session, display_name="이모", relation_tag="가족", hierarchy="상")
    _add_alias(db_session, aunt, "이모", embedder(["이모"])[0])
    return lead, aunt


@pytest.mark.dbtest
def test_promotion_similarity_outranks_unrelated_person_and_reaches_merge(
    db_session, grouped_embedder
) -> None:
    """D4 검증 기준 "팀장↔부장님 > 팀장↔이모" 가 `s_emb` 순위와 밴드에
    그대로 반영되는지."""

    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"]})
    lead, aunt = _seed_promotion_state(db_session, embedder)
    ctx = _ctx(db_session, session_id="embonly-promotion", embedder=embedder)

    decision = get_resolver(METHOD_NAME).resolve_mention(
        ctx, "부장님", "요즘 부장님이 회식을 자주 잡으셔", config=CONFIG
    )

    scores = {c.person_id: c.signals["s_emb"] for c in decision.candidates}
    assert scores[lead.id] > scores[aunt.id]
    assert scores[lead.id] >= 0.8
    assert scores[aunt.id] <= 0.2

    assert decision.decision == "merge"
    assert decision.person_id == lead.id
    assert decision.score == pytest.approx(scores[lead.id])
    assert decision.detail["forced_reason"] is None
    assert decision.candidates[0].person_id == lead.id  # 최고 유사도가 앞


@pytest.mark.dbtest
def test_raising_t_merge_turns_the_same_input_into_identity(
    db_session, grouped_embedder
) -> None:
    """P4 스윕 배관(S3.7) -- 같은 DB 상태·같은 mention 에 `T_merge` 만
    올리면 `merge` 가 `identity` 로 바뀐다(`T_new` 는 0.3 고정)."""

    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"]})
    lead, _ = _seed_promotion_state(db_session, embedder)
    ctx = _ctx(db_session, session_id="embonly-sweep", embedder=embedder)
    resolver = get_resolver(METHOD_NAME)

    low = resolver.resolve_mention(ctx, "부장님", "발화", config=ERConfig(t_merge=0.8, t_new=0.3))
    high = resolver.resolve_mention(ctx, "부장님", "발화", config=ERConfig(t_merge=0.95, t_new=0.3))

    assert low.decision == "merge"
    assert low.person_id == lead.id
    assert high.decision == "identity"
    assert high.person_id is None
    assert high.detail["ask_kind"] == "identity"
    assert low.score == pytest.approx(high.score)
    assert [c.person_id for c in low.candidates] == [c.person_id for c in high.candidates]


@pytest.mark.dbtest
def test_exact_alias_match_without_embedding_provider_is_new_person(db_session) -> None:
    """공급자가 없으면(`ctx.embedder=None`) 별칭이 **정확히** 일치해 후보로
    잡혀도 `s_emb=0` 이라 `new_person` 이다 -- 이 방식이 문자열 일치를
    쓰지 않는다는 증명이자 01-plan 103행의 `embedding_skipped` 경로다."""

    lead = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, lead, "팀장")  # embedding=None
    ctx = _ctx(db_session, session_id="embonly-skipped", embedder=None)

    decision = get_resolver(METHOD_NAME).resolve_mention(ctx, "팀장", "발화", config=CONFIG)

    assert decision.detail["candidate_count"] == 1
    assert decision.detail["embedding_skipped"] is True
    assert decision.detail["forced_reason"] == EMBEDDING_SKIPPED
    assert decision.decision == "new_person"
    assert decision.person_id is None
    assert decision.score == 0.0


@pytest.mark.dbtest
def test_empty_state_yields_no_candidates(db_session, grouped_embedder) -> None:
    embedder = grouped_embedder({"kim": ["팀장", "부장님"]})
    ctx = _ctx(db_session, session_id="embonly-empty", embedder=embedder)

    decision = get_resolver(METHOD_NAME).resolve_mention(ctx, "부장님", "발화", config=CONFIG)

    assert decision.decision == "new_person"
    assert decision.detail["forced_reason"] == NO_CANDIDATES
    assert decision.candidates == []


@pytest.mark.dbtest
def test_other_users_persons_are_not_candidates(db_session, grouped_embedder) -> None:
    """`Person.user_id == ctx.user_id` 범위 밖 인물이 새면 비교가 깨진다."""

    embedder = grouped_embedder({"kim": ["팀장", "부장님"]})
    other = _make_person(db_session, display_name="남의사람", user_id="someone-else")
    _add_alias(db_session, other, "팀장", embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id="embonly-scope", embedder=embedder)

    decision = get_resolver(METHOD_NAME).resolve_mention(ctx, "부장님", "발화", config=CONFIG)

    assert decision.candidates == []
    assert decision.decision == "new_person"


@pytest.mark.dbtest
@pytest.mark.parametrize(
    ("mention", "expected"),
    [("부장님", "merge"), ("이모", "merge"), ("전혀모르는사람", "new_person")],
)
def test_no_side_effect_on_persons_aliases_questions(
    db_session, grouped_embedder, mention: str, expected: str
) -> None:
    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"]})
    _seed_promotion_state(db_session, embedder)
    ctx = _ctx(db_session, session_id=f"embonly-side-{expected}", embedder=embedder)

    before = _state_counts(db_session)
    decision = get_resolver(METHOD_NAME).resolve_mention(ctx, mention, "발화", config=CONFIG)
    db_session.flush()

    assert decision.decision == expected
    assert _state_counts(db_session) == before


@pytest.mark.dbtest
def test_same_input_twice_gives_the_same_decision_against_the_db(
    db_session, grouped_embedder
) -> None:
    embedder = grouped_embedder({"kim": ["팀장", "김팀장", "부장님"]})
    _seed_promotion_state(db_session, embedder)
    ctx = _ctx(db_session, session_id="embonly-repeat", embedder=embedder)
    resolver = get_resolver(METHOD_NAME)

    first = resolver.resolve_mention(ctx, "부장님", "발화", config=CONFIG).to_dict()
    second = resolver.resolve_mention(ctx, "부장님", "발화", config=CONFIG).to_dict()

    assert first == second


@pytest.mark.dbtest
def test_traces_are_the_only_row_written(db_session, grouped_embedder) -> None:
    """`search_person` 의 `@traced` 기록 1행 -- 인물 상태는 그대로다."""

    embedder = grouped_embedder({"kim": ["팀장", "부장님"]})
    _seed_promotion_state(db_session, embedder)
    ctx = _ctx(db_session, session_id="embonly-trace", embedder=embedder)
    before = db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()

    get_resolver(METHOD_NAME).resolve_mention(ctx, "부장님", "발화", config=CONFIG)
    db_session.flush()

    after = db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()
    assert after - before == 1


# =========================================================================
# 5. 방식 표 등록 경로
# =========================================================================


def test_registered_under_the_reserved_name() -> None:
    assert RESOLVERS[METHOD_NAME] is EmbeddingOnlyResolver


def test_get_resolver_returns_the_embedding_only_resolver() -> None:
    resolver = get_resolver(METHOD_NAME)

    assert isinstance(resolver, EmbeddingOnlyResolver)
    assert resolver.name == METHOD_NAME
    assert resolver.supported_decisions == DECISIONS


def test_all_methods_order_after_u4() -> None:
    """등록 순서 = `evaluation/resolvers/__init__.py` 의 import 순서.
    이름은 `metrics.json` 의 키다(P4 인계 4)."""

    assert resolver_registry.ALL_METHODS == (
        "proposed",
        "exact_raw",
        "exact_norm",
        "embedding_only",
    )
