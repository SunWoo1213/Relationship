"""Refs: P3-baselines P1-pilot-dataset D5 원칙8 -- 시나리오 사전 상태 적재기.

01-plan 58행·105행 U6, 결정 F(i)("적재기는 이 패키지가 만들고 P4 러너가
재사용한다")·결정 G(i)(네 방식이 **같은 PostgreSQL·같은 `ToolContext`** 를
공유한다)·결정 H(i)(`embedder` 인자를 받되 기본값 `None`, 이 패키지 테스트는
가짜 임베딩만 쓴다).

## 무엇을 적재하는가 (P1 04-review §7 인계 2 -- 그대로 옮긴다)

시나리오 하나의 **`seed_persons` 에 있는 인물만** `persons` 에 넣고, 그
인물의 `aliases` 를 **있는 그대로** `person_aliases` 에 넣는다. 그리고
`gold_person_id`(문자열 "p1"…) → 실제 `persons.id`(정수) 매핑을 돌려준다.

- **추가·추론·정규화를 하지 않는다**(P1 결정 I). `aliases` 는 "대화 시작
  전에 이미 알려진 별칭"만이고 승진 후 호칭("부장님")·대화 중 처음 생기는
  호칭은 **일부러** 빠져 있다. 여기서 호칭을 보태면 별칭 완전일치만으로
  정답이 풀려 호칭 변경 추적을 측정할 수 없게 된다(원칙8 -- 결과가 좋아
  보이게 데이터를 손대지 않는다). 공백 제거·존칭 접미 제거 같은 정규화도
  하지 않는다 -- 별칭 문자열은 JSON 과 **바이트 단위로 같다**.
- `display_name`·`relation_tag`·`hierarchy` 는 `persons` 행의 값이 된다
  (`relation_tag`·`hierarchy` 는 DB CHECK 제약이 값 집합을 강제하므로
  라벨이 어휘를 벗어나면 flush 에서 바로 드러난다).
- **`seed_persons` 밖 인물은 만들지 않는다.** 그 인물들은 대화에서 처음
  등장하는 사람이고, 그들을 등록할지 말지가 곧 측정 대상이다(D1 확인형
  등록·`new_person` 카테고리).
- **`events`·`schedules`·`pending_questions`·`person_facts`·`agent_traces`
  는 한 행도 만들지 않는다.** 시나리오의 `events` 라벨은 P4·P10 의 추출
  평가 정답이지 사전 상태가 아니다.

## 실물 데이터의 성질 (`data/scenarios/*.json`, schema_version 2 기준)

5개 파일 40건에서 `seed_persons` 인물은 **56명**, 그 인물들의 별칭은 모두
합쳐 **112개**다(`count_seed_persons_and_aliases()` 로 DB 없이 셀 수 있다).
다음 두 가지는 실물 JSON 을 세어 확인한 사실이고 적재 규칙에 영향을 준다:

- **한 인물의 `aliases` 안에 중복 문자열은 없다**(40건 전부). 그래서 같은
  별칭 문자열이 한 인물에 두 행 생기는 일은 데이터상 발생하지 않는다.
- **`display_name` 이 `aliases` 에도 들어 있는 경우가 10건 있다**(예:
  sc-025 "엄마" -- `display_name`="엄마", `aliases`=["엄마","울엄마"]).
  이때도 **`aliases` 를 그대로 넣는다** -- `person_aliases` 행 수는 항상
  `len(aliases)` 이고 표시 이름과 겹친다고 별칭 행을 빼지 않는다. 빼면
  "라벨과 정확히 일치"라는 계약(01-plan 105행)이 깨지고, 임베딩 단독·제안
  방식이 보는 별칭 집합이 방식마다 달라진다. `persons.display_name` 은
  별칭 테이블과 별개로 `exact_match.load_known_persons()` 가 함께 읽는다.

## `embedder` 와 `search_person` 의 관계 (권고 R-6 -- 반드시 읽을 것)

`embedder` 를 주면 별칭마다 임베딩을 채우고, 주지 않으면(`None`, 기본값)
`person_aliases.embedding` 은 **전부 NULL** 이다.

    `app/tools/persons.py`(192·205행)의 `search_person` 은
    **`embedding IS NOT NULL` 인 별칭만** 벡터 검색 대상에 넣는다.

따라서 **`embedder` 없이 적재하면 임베딩 단독(`embedding_only`)과 제안
방식(`proposed`)은 `embedding_skipped` 로 떨어진다** -- 후보 검색의 벡터
경로가 통째로 비어 `s_emb=0` 이 되고, 그 결과 두 방식의 수치가 "방식이
나쁜 것"이 아니라 "사전 상태에 벡터가 없는 것"이 된다. P4 가 실 임베딩
없이 곡선을 돌리는 사고를 막기 위해 이 사실을 여기·테스트 양쪽에 적는다
(D5 "새 별칭이 확정(`confirmed_at`)되면 즉시 임베딩한다").

`ctx.embedder` 는 **읽지 않는다**. 적재 시 임베딩 여부는 오직 이 인자
하나가 정한다 -- `ctx` 에 공급자가 꽂혀 있다는 이유로 적재가 조용히
네트워크·비용을 쓰면 결정 H(i)("이 패키지 테스트는 네트워크 0")가 깨진다.

## `source="confirmed"` · `confirmed_at` (권고 R-6)

사전 상태 = "대화 전에 이미 확정돼 있던 별칭"이므로
`person_aliases.source` 는 `"confirmed"`(`app.db.models.ALIAS_SOURCES` 의
값)이고 `confirmed_at` 은 `ctx.now()` 다. `user_said`(대화에서 방금 들은
말)나 `system`(시스템이 만든 것)은 이 자리의 의미가 아니다.

## 이 모듈이 하지 않는 것

- **시나리오 사이 DB 초기화·반복 실행·순서 관리**(P1 §7 인계 1) -- P4
  러너 몫이다. 같은 시나리오를 두 번 적재하면 인물이 두 벌 생긴다(그것이
  곧 "초기화가 필요하다"는 증거이며, 테스트가 그 성질을 고정한다).
- **`commit()`** -- 툴과 같은 규칙으로 `flush()` 까지만 한다(P2 01-plan
  결정 2). 트랜잭션 경계는 호출자(러너·테스트 롤백 픽스처)가 잡는다.
- **지표·판정** -- 여기서는 아무것도 판정하지 않는다.
- **JSON 파싱**(권고 R-7) -- 시나리오 읽기와 `schema_version` 2 확인은
  `scripts/validate_scenarios.py` 의 적재 함수(`load_dataset`)를 그대로
  재사용한다. `scripts/dump_scenarios.py` 가 이미 같은 방식이며, JSON 을
  읽는 코드가 두 벌이면 어긋난다(중복 구현 금지).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.db.models import Person, PersonAlias
from app.embedding import as_provider

if TYPE_CHECKING:  # pragma: no cover - 타입 전용
    from app.embedding import EmbedderCallable, EmbeddingProvider
    from app.tools.context import ToolContext

#: 저장소 루트(= 이 파일의 상위의 상위). 데이터·스크립트 경로의 기준점이라
#: 작업 디렉터리와 무관하게 같은 파일을 읽는다(재현성, 원칙8).
REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_scenarios import (  # noqa: E402 -- sys.path 등록 뒤여야 한다
    Dataset,
    _dict_items,
    _scenario_id,
    load_dataset,
)

#: 시나리오 디렉터리(절대 경로). `validate_scenarios.DEFAULT_DIR` 은 cwd
#: 기준 상대 경로라 여기서 루트를 붙여 고정한다.
DEFAULT_SCENARIO_DIR = REPO_ROOT / "data" / "scenarios"

#: 이 적재기가 읽을 수 있는 스키마 계약(P1 04-review §7 인계 10). 소비자가
#: 더 많은 정보를 원하면 FIX 가 아니라 `schema_version` 승격이므로, 값이
#: 달라지면 조용히 적재하지 않고 멈춘다.
SUPPORTED_SCHEMA_VERSION = 2

#: 사전 상태 별칭의 `person_aliases.source` (권고 R-6).
ALIAS_SOURCE = "confirmed"


class ScenarioStateError(RuntimeError):
    """시나리오를 읽거나 적재할 수 없다(라벨 계약 위반·스키마 버전 불일치).

    적재를 **조용히 건너뛰지 않는다** -- 사전 상태가 비면 그 시나리오의
    모든 방식이 `new_person` 을 내고 그것이 지표에 그대로 섞인다(원칙8).
    """


@dataclass(frozen=True)
class PersonSpec:
    """시나리오 라벨에서 읽은 seed 인물 하나(DB 이전의 순수 값).

    `aliases` 는 JSON 의 순서·문자열 그대로다(정규화·중복 제거 없음).
    """

    gold_person_id: str
    display_name: str
    relation_tag: str
    hierarchy: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioState:
    """`load_scenario_state()` 의 결과 -- 적재된 사전 상태의 요약.

    - `person_id_map` -- `gold_person_id`(문자열) → `persons.id`(정수).
      P4 채점기가 방식의 `person_id` 를 골드와 대조하는 유일한 다리다.
    - `created_person_ids` -- 만든 `persons.id` 를 `seed_persons` 순서로.
    - `alias_count` -- 만든 `person_aliases` 행 수(= 라벨의 별칭 총합).
    - `embedded_alias_count` -- 그중 `embedding IS NOT NULL` 인 행 수.
      `embedder=None` 이면 0 이고, 그때 임베딩 단독·제안 방식은
      `embedding_skipped` 로 떨어진다(모듈 docstring R-6 절).
    """

    scenario_id: str
    person_id_map: dict[str, int] = field(default_factory=dict)
    created_person_ids: list[int] = field(default_factory=list)
    alias_count: int = 0
    embedded_alias_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "person_id_map": dict(self.person_id_map),
            "created_person_ids": list(self.created_person_ids),
            "alias_count": self.alias_count,
            "embedded_alias_count": self.embedded_alias_count,
        }


# --------------------------------------------------------------------------
# 순수 층 -- 라벨 읽기 (DB·네트워크 없음)
# --------------------------------------------------------------------------


def load_scenarios(
    directory: Path | str = DEFAULT_SCENARIO_DIR,
) -> list[tuple[str, dict[str, Any]]]:
    """`(파일명, 시나리오)` 목록을 manifest 순서 그대로 돌려준다.

    `validate_scenarios.load_dataset(strict=True)` 를 감싸는 **얇은 래퍼**다
    (권고 R-7 -- JSON 파서를 새로 쓰지 않는다). 적재 단계 오류(manifest·
    파일 누락·JSON 파싱 실패·배열 아님)가 하나라도 있으면
    `ScenarioStateError` 를 던진다.

    이 함수는 **적재 계층만** 재사용한다 -- 교차 무결성 검사 (2)~(15) 는
    `python scripts/validate_scenarios.py --strict` 의 몫이고, 여기서 다시
    돌리면 같은 검사가 두 곳에서 살게 된다.
    """

    dataset, issues = load_dataset(Path(directory), strict=True)
    if issues:
        lines = "\n".join(issue.line() for issue in issues)
        raise ScenarioStateError(f"시나리오 적재 실패({directory}):\n{lines}")
    check_schema_version(dataset)
    return [
        (name, scenario)
        for name, scenario in dataset.scenarios
        if isinstance(scenario, dict)
    ]


def check_schema_version(dataset: Dataset) -> int:
    """`manifest.schema_version` 이 `SUPPORTED_SCHEMA_VERSION` 인지 본다."""

    manifest = dataset.manifest_dict
    version = manifest.get("schema_version") if manifest else None
    if version != SUPPORTED_SCHEMA_VERSION:
        raise ScenarioStateError(
            f"schema_version 이 {SUPPORTED_SCHEMA_VERSION} 이 아니다(실제: "
            f"{version!r}) -- 적재기가 읽는 계약이 바뀌었다(P1 04-review §7 인계 10)"
        )
    return SUPPORTED_SCHEMA_VERSION


def seed_person_specs(scenario: dict[str, Any]) -> list[PersonSpec]:
    """**순수 함수** -- 시나리오에서 `seed_persons` 인물만 추린다.

    순서는 `seed_persons` 배열 순서다(재현성 -- `persons.id` 부여 순서가
    실행마다 흔들리면 P4 수치가 흔들린다). `seed_persons` 에 있는 id 가
    `persons[]` 에 없으면 `ScenarioStateError` 다(검증기 검사 (9) 가 이미
    막지만, 적재기가 조용히 빼먹으면 사전 상태가 라벨과 달라진다).
    """

    by_id: dict[str, dict[str, Any]] = {}
    for person in _dict_items(scenario.get("persons")):
        person_id = person.get("person_id")
        if isinstance(person_id, str):
            by_id.setdefault(person_id, person)

    specs: list[PersonSpec] = []
    seen: set[str] = set()
    seed_ids = scenario.get("seed_persons")
    for gold_id in seed_ids if isinstance(seed_ids, list) else []:
        if not isinstance(gold_id, str) or gold_id in seen:
            continue
        seen.add(gold_id)
        person = by_id.get(gold_id)
        if person is None:
            raise ScenarioStateError(
                f"{_scenario_id(scenario)}: seed_persons 의 {gold_id!r} 가 "
                "persons[] 에 없다(라벨 계약 위반)"
            )
        aliases = person.get("aliases")
        specs.append(
            PersonSpec(
                gold_person_id=gold_id,
                display_name=str(person.get("display_name")),
                relation_tag=str(person.get("relation_tag")),
                hierarchy=str(person.get("hierarchy")),
                aliases=tuple(
                    alias
                    for alias in (aliases if isinstance(aliases, list) else [])
                    if isinstance(alias, str)
                ),
            )
        )
    return specs


def count_seed_persons_and_aliases(scenario: dict[str, Any]) -> tuple[int, int]:
    """**순수 함수** -- (seed 인물 수, 별칭 총합). DB 없이 기대값을 만든다."""

    specs = seed_person_specs(scenario)
    return len(specs), sum(len(spec.aliases) for spec in specs)


# --------------------------------------------------------------------------
# 적재 층 -- DB (INSERT 만, commit 없음)
# --------------------------------------------------------------------------


def load_scenario_state(
    ctx: ToolContext,
    scenario: dict[str, Any],
    *,
    embedder: EmbeddingProvider | EmbedderCallable | None = None,
) -> ScenarioState:
    """시나리오의 사전 상태를 `ctx.session` 에 적재하고 매핑을 돌려준다.

    `persons`(seed 인물) + `person_aliases`(그 인물의 `aliases` 그대로)만
    만든다. `embedder` 를 주면 별칭 임베딩을 **한 번의 배치 호출**로 채우고,
    주지 않으면 전부 NULL 이다 -- `search_person` 이 `embedding IS NOT NULL`
    별칭만 검색하므로 **embedder 없이 적재하면 임베딩 단독·제안 방식은
    `embedding_skipped` 로 떨어진다**(모듈 docstring R-6 절).

    `ctx.user_id` 범위로 넣고 `ctx.now()` 를 `confirmed_at` 에 쓴다.
    `flush()` 까지만 하고 `commit()` 하지 않는다(트랜잭션은 호출자 몫).
    """

    specs = seed_person_specs(scenario)
    scenario_id = _scenario_id(scenario)

    person_id_map: dict[str, int] = {}
    created_person_ids: list[int] = []
    session = ctx.session

    for spec in specs:
        person = Person(
            user_id=ctx.user_id,
            display_name=spec.display_name,
            relation_tag=spec.relation_tag,
            hierarchy=spec.hierarchy,
        )
        session.add(person)
        session.flush()  # persons.id 를 알아야 매핑을 만든다
        person_id_map[spec.gold_person_id] = person.id
        created_person_ids.append(person.id)

    # 별칭은 (인물 순서, JSON 안 순서) 그대로 -- person_aliases.id 순서가
    # 곧 라벨 순서가 되어 재현성이 유지된다(원칙8).
    flat_aliases: list[tuple[int, str]] = [
        (person_id_map[spec.gold_person_id], alias)
        for spec in specs
        for alias in spec.aliases
    ]

    provider = as_provider(embedder)
    vectors: list[list[float]] | None = None
    if provider is not None and flat_aliases:
        vectors = provider.embed([alias for _, alias in flat_aliases])
        if len(vectors) != len(flat_aliases):
            raise ScenarioStateError(
                f"{scenario_id}: embedder 가 별칭 {len(flat_aliases)}개에 대해 "
                f"{len(vectors)}개 벡터를 돌려줬다"
            )

    now = ctx.now()
    embedded = 0
    for index, (person_id, alias) in enumerate(flat_aliases):
        vector = vectors[index] if vectors is not None else None
        if vector is not None:
            embedded += 1
        session.add(
            PersonAlias(
                person_id=person_id,
                alias=alias,
                source=ALIAS_SOURCE,
                embedding=vector,
                confirmed_at=now,
            )
        )
    session.flush()

    return ScenarioState(
        scenario_id=scenario_id,
        person_id_map=person_id_map,
        created_person_ids=created_person_ids,
        alias_count=len(flat_aliases),
        embedded_alias_count=embedded,
    )


__all__ = [
    "ALIAS_SOURCE",
    "DEFAULT_SCENARIO_DIR",
    "SUPPORTED_SCHEMA_VERSION",
    "PersonSpec",
    "ScenarioState",
    "ScenarioStateError",
    "check_schema_version",
    "count_seed_persons_and_aliases",
    "load_scenario_state",
    "load_scenarios",
    "seed_person_specs",
]
