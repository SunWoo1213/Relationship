"""Refs: P3-baselines P1-pilot-dataset D5 원칙8 -- U6 시나리오 사전 상태 적재기 테스트.

두 층으로 나눠 본다(다른 방식 테스트와 같은 구성).

1. **순수 층**(DB·네트워크 0) -- `scripts/validate_scenarios.py` 의 적재
   함수로 읽은 **실물** `data/scenarios/*.json` 5파일 40건 전부에서 seed
   인물 수·별칭 수를 세어 라벨·manifest 와 대조한다(픽스처를 지어내지
   않는다 -- 01-plan 116행 "의존: P1 데이터셋").
2. **DB 층**(실 PostgreSQL, 롤백 픽스처 `db_session`) -- 적재 결과가
   `seed_persons`+`aliases` 와 **정확히** 일치하고 그 밖의 테이블 증가가
   0 인지(01-plan 105행), `source="confirmed"`·`confirmed_at`(권고 R-6),
   `embedder` 유무가 `embedding IS NOT NULL` 수를 그대로 가르는지(R-6),
   별칭 문자열이 정규화 없이 바이트 단위로 같은지(P1 결정 I), 그리고
   적재한 사전 상태를 `get_resolver("exact_raw")` 가 그대로 읽어
   `merge` 를 내는지(적재기 ↔ resolver 맞물림).

임베딩은 `grouped_embedder`(결정적 가짜)만 쓴다 -- 결정 H(i), 네트워크 0.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    Event,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)
from app.er.types import ERConfig
from app.tools.context import ToolContext
from evaluation.resolvers import get_resolver
from evaluation.scenario_state import (
    ALIAS_SOURCE,
    DEFAULT_SCENARIO_DIR,
    SUPPORTED_SCHEMA_VERSION,
    PersonSpec,
    ScenarioState,
    ScenarioStateError,
    check_schema_version,
    count_seed_persons_and_aliases,
    load_scenario_state,
    load_scenarios,
    seed_person_specs,
)

USER_ID = "scenario-state-user"
CONFIG = ERConfig()

#: `confirmed_at` 을 정확히 대조하기 위한 고정 시각(`ctx.now`).
FIXED_NOW = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)

#: 실물 데이터셋을 한 번만 읽어 공유한다(파일 I/O 만, DB·네트워크 없음).
LOADED: list[tuple[str, dict[str, Any]]] = load_scenarios()
SCENARIOS: dict[str, dict[str, Any]] = {sc["id"]: sc for _, sc in LOADED}

#: 순수 층이 P1 04-review §7 인계 10 의 계약(schema_version 2, 40건)에서
#: 세어 고정한 값. 데이터셋이 바뀌면 여기서 먼저 깨져야 한다(원칙8 --
#: 수치가 조용히 달라지지 않는다).
TOTAL_SCENARIOS = 40
TOTAL_SEED_PERSONS = 56
TOTAL_SEED_ALIASES = 112

MANIFEST: dict[str, Any] = json.loads(
    (DEFAULT_SCENARIO_DIR / "manifest.json").read_text(encoding="utf-8")
)


def _raw_person(scenario: dict[str, Any], gold_id: str) -> dict[str, Any]:
    """라벨 JSON 원본에서 인물 하나를 꺼낸다(테스트의 독립 경로)."""
    for person in scenario["persons"]:
        if person["person_id"] == gold_id:
            return person
    raise AssertionError(f"{scenario['id']}: {gold_id} 가 persons[] 에 없다")


# =========================================================================
# 1. 순수 층 -- 실물 데이터셋 읽기 (DB 없음)
# =========================================================================


def test_load_scenarios_reads_manifest_files_in_order() -> None:
    """읽는 파일과 순서는 manifest 가 정한다(재현성 -- P4 표의 행 순서)."""
    seen_order = list(dict.fromkeys(name for name, _ in LOADED))
    assert seen_order == MANIFEST["files"]
    # manifest.counts 의 키는 카테고리 이름(파일명에서 .json 을 뺀 것)이다.
    assert Counter(
        name.removesuffix(".json") for name, _ in LOADED
    ) == Counter(MANIFEST["counts"])
    assert len(LOADED) == MANIFEST["total"] == TOTAL_SCENARIOS


def test_schema_version_contract_is_two() -> None:
    """P1 04-review §7 인계 10 -- 계약은 `schema_version` 2 다."""
    assert SUPPORTED_SCHEMA_VERSION == 2
    assert MANIFEST["schema_version"] == SUPPORTED_SCHEMA_VERSION


def test_schema_version_mismatch_raises() -> None:
    """버전이 올라가면 조용히 적재하지 않고 멈춘다."""

    class _Dataset:
        manifest_dict = {"schema_version": 3}

    with pytest.raises(ScenarioStateError) as exc:
        check_schema_version(_Dataset())  # type: ignore[arg-type]

    assert "schema_version" in str(exc.value)


def test_missing_manifest_dir_raises() -> None:
    """디렉터리가 없으면 빈 목록이 아니라 오류다(사전 상태 0 은 지표를 왜곡한다)."""
    with pytest.raises(ScenarioStateError):
        load_scenarios(DEFAULT_SCENARIO_DIR / "없는디렉터리")


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_specs_match_labels_exactly(scenario_id: str) -> None:
    """40건 전부 -- seed 인물 목록·별칭이 라벨과 **글자 그대로** 같다."""
    scenario = SCENARIOS[scenario_id]
    specs = seed_person_specs(scenario)

    assert [spec.gold_person_id for spec in specs] == list(scenario["seed_persons"])
    for spec in specs:
        raw = _raw_person(scenario, spec.gold_person_id)
        assert spec.display_name == raw["display_name"]
        assert spec.relation_tag == raw["relation_tag"]
        assert spec.hierarchy == raw["hierarchy"]
        # 추가·추론·정규화 금지(P1 결정 I): 순서까지 그대로.
        assert list(spec.aliases) == list(raw["aliases"])


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_non_seed_persons_are_not_loaded(scenario_id: str) -> None:
    """`seed_persons` 밖 인물은 사전 상태가 아니다(대화에서 처음 등장한다)."""
    scenario = SCENARIOS[scenario_id]
    loaded = {spec.gold_person_id for spec in seed_person_specs(scenario)}

    assert loaded == set(scenario["seed_persons"])
    assert loaded <= {p["person_id"] for p in scenario["persons"]}


def test_dataset_totals_are_fixed() -> None:
    """5파일 40건의 인물 수·별칭 수를 DB 없이 센다(P4 기대값의 출처)."""
    persons = aliases = 0
    for _, scenario in LOADED:
        p_count, a_count = count_seed_persons_and_aliases(scenario)
        persons += p_count
        aliases += a_count

    assert (persons, aliases) == (TOTAL_SEED_PERSONS, TOTAL_SEED_ALIASES)


def test_count_helper_agrees_with_specs() -> None:
    """세는 함수와 적재 대상 목록이 어긋나면 기대값이 둘로 갈린다."""
    for _, scenario in LOADED:
        specs = seed_person_specs(scenario)
        assert count_seed_persons_and_aliases(scenario) == (
            len(specs),
            sum(len(spec.aliases) for spec in specs),
        )


def test_no_duplicate_alias_within_a_person() -> None:
    """실물 데이터 성질 -- 한 인물의 `aliases` 안에 중복 문자열이 없다.

    그래서 "별칭을 그대로 넣는다"가 같은 인물에 같은 문자열 두 행을 만드는
    일로 이어지지 않는다(모듈 docstring "실물 데이터의 성질").
    """
    for _, scenario in LOADED:
        for spec in seed_person_specs(scenario):
            assert len(set(spec.aliases)) == len(spec.aliases), scenario["id"]


def test_display_name_may_also_be_an_alias() -> None:
    """표시 이름이 `aliases` 에도 있는 인물이 실제로 있다(10명).

    이때도 별칭 행을 빼지 않는다 -- 행 수는 항상 `len(aliases)` 여야
    라벨과 정확히 일치한다(01-plan 105행).
    """
    overlap = [
        (scenario["id"], spec.gold_person_id)
        for _, scenario in LOADED
        for spec in seed_person_specs(scenario)
        if spec.display_name in spec.aliases
    ]

    assert len(overlap) == 10


def test_seed_id_missing_from_persons_raises() -> None:
    """라벨 계약 위반은 조용히 건너뛰지 않는다."""
    broken = {
        "id": "sc-broken",
        "persons": [
            {
                "person_id": "p1",
                "display_name": "김민준",
                "relation_tag": "직장",
                "hierarchy": "상",
                "aliases": ["김팀장"],
            }
        ],
        "seed_persons": ["p1", "p9"],
    }

    with pytest.raises(ScenarioStateError) as exc:
        seed_person_specs(broken)

    assert "p9" in str(exc.value)


def test_specs_are_frozen() -> None:
    spec = seed_person_specs(SCENARIOS["sc-025"])[0]

    assert isinstance(spec, PersonSpec)
    with pytest.raises(Exception):
        spec.display_name = "다른 사람"  # type: ignore[misc]


# =========================================================================
# 2. DB 층 -- 실 PostgreSQL + 롤백 픽스처
# =========================================================================


def _ctx(db_session: Any, *, session_id: str, embedder: Any = None) -> ToolContext:
    return ToolContext(
        session=db_session,
        session_id=session_id,
        user_id=USER_ID,
        embedder=embedder,
        now=lambda: FIXED_NOW,
    )


def _counts(db_session: Any) -> dict[str, int]:
    """적재가 건드릴 수 있는 모든 테이블의 현재 행 수."""
    models = {
        "persons": Person,
        "person_aliases": PersonAlias,
        "events": Event,
        "schedules": Schedule,
        "pending_questions": PendingQuestion,
        "person_facts": PersonFact,
        "agent_traces": AgentTrace,
    }
    return {
        name: db_session.execute(select(func.count()).select_from(model)).scalar_one()
        for name, model in models.items()
    }


def _aliases_of(db_session: Any, person_id: int) -> list[PersonAlias]:
    return list(
        db_session.execute(
            select(PersonAlias)
            .where(PersonAlias.person_id == person_id)
            .order_by(PersonAlias.id)
        )
        .scalars()
        .all()
    )


@pytest.mark.dbtest
def test_only_persons_and_aliases_are_created(db_session) -> None:
    """(a) `persons` +seed, `person_aliases` +별칭 총합, 그 밖은 증가 0."""
    scenario = SCENARIOS["sc-025"]
    expected_persons, expected_aliases = count_seed_persons_and_aliases(scenario)
    before = _counts(db_session)

    state = load_scenario_state(_ctx(db_session, session_id="u6-counts"), scenario)

    after = _counts(db_session)
    assert after["persons"] - before["persons"] == expected_persons
    assert after["person_aliases"] - before["person_aliases"] == expected_aliases
    untouched = (
        "events",
        "schedules",
        "pending_questions",
        "person_facts",
        "agent_traces",
    )
    for table in untouched:
        assert after[table] == before[table], table
    assert state.alias_count == expected_aliases
    assert len(state.created_person_ids) == expected_persons


@pytest.mark.dbtest
def test_events_in_labels_do_not_become_rows(db_session) -> None:
    """시나리오에 `events` 라벨이 있어도 사전 상태에는 넣지 않는다."""
    scenario = SCENARIOS["sc-025"]
    assert scenario["events"], "이 시나리오는 events 라벨을 가진다(전제)"
    before = _counts(db_session)["events"]

    load_scenario_state(_ctx(db_session, session_id="u6-events"), scenario)

    assert _counts(db_session)["events"] == before


@pytest.mark.dbtest
def test_person_id_map_points_at_real_rows(db_session) -> None:
    """(b) 매핑의 키 = `seed_persons`, 값 = 실제 `persons` 행."""
    scenario = SCENARIOS["sc-002"]  # seed 2명(라벨 대조에 유리)
    ctx = _ctx(db_session, session_id="u6-map")

    state = load_scenario_state(ctx, scenario)

    assert set(state.person_id_map) == set(scenario["seed_persons"])
    assert list(state.person_id_map.values()) == state.created_person_ids
    for gold_id, person_id in state.person_id_map.items():
        raw = _raw_person(scenario, gold_id)
        person = db_session.get(Person, person_id)
        assert person is not None
        assert person.display_name == raw["display_name"]
        assert person.relation_tag == raw["relation_tag"]
        assert person.hierarchy == raw["hierarchy"]
        assert person.user_id == USER_ID


@pytest.mark.dbtest
def test_aliases_are_stored_byte_identical(db_session) -> None:
    """(e) 별칭 문자열이 JSON 과 바이트 단위로 같다(정규화·추가 없음)."""
    scenario = SCENARIOS["sc-002"]
    ctx = _ctx(db_session, session_id="u6-bytes")

    state = load_scenario_state(ctx, scenario)

    for gold_id, person_id in state.person_id_map.items():
        raw_aliases = _raw_person(scenario, gold_id)["aliases"]
        rows = _aliases_of(db_session, person_id)
        assert [row.alias for row in rows] == list(raw_aliases)
        assert [row.alias.encode("utf-8") for row in rows] == [
            alias.encode("utf-8") for alias in raw_aliases
        ]


@pytest.mark.dbtest
def test_display_name_in_aliases_still_creates_its_row(db_session) -> None:
    """표시 이름과 겹치는 별칭도 행을 만든다(sc-025 "엄마")."""
    scenario = SCENARIOS["sc-025"]
    ctx = _ctx(db_session, session_id="u6-overlap")

    state = load_scenario_state(ctx, scenario)

    person_id = state.person_id_map["p1"]
    rows = _aliases_of(db_session, person_id)
    assert [row.alias for row in rows] == ["엄마", "울엄마"]
    assert db_session.get(Person, person_id).display_name == "엄마"


@pytest.mark.dbtest
def test_alias_source_and_confirmed_at(db_session) -> None:
    """(d) 사전 상태 별칭은 `confirmed` + `confirmed_at=ctx.now()`(R-6)."""
    ctx = _ctx(db_session, session_id="u6-source")

    state = load_scenario_state(ctx, SCENARIOS["sc-002"])

    assert ALIAS_SOURCE == "confirmed"
    assert ALIAS_SOURCE in ALIAS_SOURCES
    for person_id in state.created_person_ids:
        for row in _aliases_of(db_session, person_id):
            assert row.source == ALIAS_SOURCE
            assert row.confirmed_at is not None
            assert row.confirmed_at == FIXED_NOW


@pytest.mark.dbtest
def test_without_embedder_all_embeddings_are_null(db_session) -> None:
    """(c) `embedder=None` -> `embedding IS NOT NULL` 0.

    R-6: `search_person` 은 `embedding IS NOT NULL` 별칭만 검색하므로 이
    상태에서 임베딩 단독·제안 방식은 `embedding_skipped` 로 떨어진다 --
    P4 가 실 임베딩 없이 곡선을 돌리면 안 된다는 근거다.
    """
    ctx = _ctx(db_session, session_id="u6-null-emb")

    state = load_scenario_state(ctx, SCENARIOS["sc-002"])

    embedded = db_session.execute(
        select(func.count())
        .select_from(PersonAlias)
        .where(PersonAlias.person_id.in_(state.created_person_ids))
        .where(PersonAlias.embedding.is_not(None))
    ).scalar_one()
    assert embedded == 0
    assert state.embedded_alias_count == 0
    assert state.alias_count > 0


@pytest.mark.dbtest
def test_with_embedder_every_alias_is_embedded(db_session, grouped_embedder) -> None:
    """(c) `grouped_embedder` 를 주면 임베딩 수 = 별칭 수(R-6)."""
    scenario = SCENARIOS["sc-002"]
    embedder = grouped_embedder({"팀": ["이대리", "이서연", "박과장", "박지훈"]})
    ctx = _ctx(db_session, session_id="u6-emb")

    state = load_scenario_state(ctx, scenario, embedder=embedder)

    embedded = db_session.execute(
        select(func.count())
        .select_from(PersonAlias)
        .where(PersonAlias.person_id.in_(state.created_person_ids))
        .where(PersonAlias.embedding.is_not(None))
    ).scalar_one()
    assert embedded == state.alias_count == state.embedded_alias_count


@pytest.mark.dbtest
def test_ctx_embedder_alone_does_not_embed(db_session, grouped_embedder) -> None:
    """적재의 임베딩 여부는 **인자** 하나가 정한다 -- `ctx.embedder` 를 읽고
    조용히 네트워크·비용을 쓰지 않는다(결정 H(i))."""
    embedder = grouped_embedder({"팀": ["이대리", "이서연"]})
    ctx = _ctx(db_session, session_id="u6-ctx-emb", embedder=embedder)

    state = load_scenario_state(ctx, SCENARIOS["sc-002"])

    assert state.embedded_alias_count == 0


@pytest.mark.dbtest
def test_loaded_state_feeds_exact_raw_resolver(db_session) -> None:
    """(f) 적재기 ↔ resolver 맞물림 -- 사전 상태 별칭을 넣으면 `merge`."""
    scenario = SCENARIOS["sc-025"]
    ctx = _ctx(db_session, session_id="u6-resolver")
    state = load_scenario_state(ctx, scenario)

    resolver = get_resolver("exact_raw")
    decision = resolver.resolve_mention(
        ctx, "울엄마", scenario["utterances"][0], config=CONFIG
    )

    assert decision.decision == "merge"
    assert decision.person_id == state.person_id_map["p1"]


@pytest.mark.dbtest
def test_promotion_title_is_absent_from_seed_state(db_session) -> None:
    """P1 결정 I 가 만든 성질 -- 승진 후 호칭은 사전 상태에 없다.

    sc-001 의 seed 별칭은 "김팀장"·"팀장님" 뿐이라 "부장님"은 문자열
    완전일치로 풀리지 않는다(적재기가 호칭을 보태지 않는다는 증명).
    """
    scenario = SCENARIOS["sc-001"]
    ctx = _ctx(db_session, session_id="u6-promotion")
    load_scenario_state(ctx, scenario)

    decision = get_resolver("exact_raw").resolve_mention(
        ctx, "부장님", scenario["utterances"][0], config=CONFIG
    )

    assert decision.decision == "new_person"


@pytest.mark.dbtest
def test_other_users_state_is_not_touched(db_session) -> None:
    """적재는 `ctx.user_id` 범위로만 들어간다."""
    ctx = _ctx(db_session, session_id="u6-scope")

    state = load_scenario_state(ctx, SCENARIOS["sc-002"])

    user_ids = db_session.execute(
        select(Person.user_id).where(Person.id.in_(state.created_person_ids))
    ).scalars()
    assert set(user_ids) == {USER_ID}


@pytest.mark.dbtest
def test_loading_twice_duplicates_state(db_session) -> None:
    """시나리오 사이 초기화는 **P4 몫**이다(P1 §7 인계 1).

    적재기는 지우지 않는다 -- 두 번 부르면 인물이 두 벌 생기고, 그것이
    러너가 초기화를 해야 한다는 증거다.
    """
    scenario = SCENARIOS["sc-025"]
    ctx = _ctx(db_session, session_id="u6-twice")
    before = _counts(db_session)["persons"]

    first = load_scenario_state(ctx, scenario)
    second = load_scenario_state(ctx, scenario)

    after = _counts(db_session)["persons"]
    expected, _ = count_seed_persons_and_aliases(scenario)
    assert after - before == expected * 2
    assert first.person_id_map["p1"] != second.person_id_map["p1"]


@pytest.mark.dbtest
def test_state_is_frozen_and_jsonable(db_session) -> None:
    """P4 가 원수치를 `metrics.json` 에 실을 수 있어야 한다(원칙8)."""
    ctx = _ctx(db_session, session_id="u6-json")

    state = load_scenario_state(ctx, SCENARIOS["sc-025"])

    assert isinstance(state, ScenarioState)
    assert state.scenario_id == "sc-025"
    with pytest.raises(Exception):
        state.alias_count = 99  # type: ignore[misc]
    assert json.loads(json.dumps(state.to_dict(), ensure_ascii=False)) == state.to_dict()
