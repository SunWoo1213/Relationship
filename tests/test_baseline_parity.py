"""Refs: P3-baselines S3.7 S3.3 D10 원칙8 -- U7 동일 인터페이스 계약 테스트.

**수용 기준의 증명**이다(01-plan 111·117행): "제안 방식과 동일 인터페이스로
호출 가능" 을 기계로 판정한다 -- `proposed` 를 포함한 다섯 방식 전부를
**같은 테스트 함수**가 **같은 인자**로 호출해 통과해야 한다.

## 이 파일의 규칙 (권고 R-1)

- 방식 목록은 `registry.ALL_METHODS` 를 **속성으로** 수집 시점에 읽는다
  (PEP 562 -- 스냅샷을 이름에 묶지 않는다, `registry.py` docstring).
- **테스트 함수 본문에 방식별 분기가 없다.** 방식마다 다른 것(주입 인자·
  기대 호출 수·`agent_traces` 증분)은 전부 **모듈 상수 표**와 **픽스처의
  이름→팩토리 kwargs 표**에 값으로 둔다. 판정은 02-plan-verify §3 R-1 의
  `grep -nE` 명령(방식 이름으로 갈라지는 네 가지 분기 구문을 찾는다)이
  이 파일에서 **0줄**을 내는 것이다 -- 그 정규식 문자열을 여기에 그대로
  적으면 명령이 자기 자신을 찾아내므로 적지 않는다(증거 파일
  `evidence/*-u7-no-branch.txt` 에 명령과 출력이 있다). 표에서 값을 꺼내
  쓰는 것은 허용 범위이고, 금지되는 것은 단언·호출의 분기다.
- 기대값은 **집합**으로 적는다(`{0}`·`{1}`·`{2}`) -- "허용된 값들"을 표로
  두면 분기 없이 방식별 차이를 단언할 수 있다.

## 무엇을 단언하는가 (01-plan 106행 U7 (i)~(v) + JSON 직렬화)

(i) 반환이 `MentionDecision` 이고 `method` 가 등록 이름과 같다.
(ii) `decision ∈ resolver.supported_decisions ⊆ DECISIONS`.
(iii) `person_id` 는 `merge` 일 때만 not None 이고, 그 id 는 적재한 사전
      상태의 인물이다(불변 규약 3, 원칙1·2).
(iv) 호출 전후 `persons`·`person_aliases`·`pending_questions` 증분 0
     (불변 규약 1). `agent_traces` 만 방식마다 다르므로 표로 둔다 --
     제안 방식 +2(`er_resolve` 1 + 그 안의 `search_person` 1), 임베딩 단독
     +1(`search_person`), 나머지 0. 셋 다 **인물·별칭·질문 상태를 바꾸지
     않는** `@traced` 툴 호출 기록이다(`base.py` 불변 규약 1 단서).
(v) 같은 입력을 두 번 호출하면 `decision`·`person_id`·`score` 가 같다
    (LLM 은 `FakeJudge`·스텁 클라이언트로 고정 -- 원칙8 재현성).
(vi) `to_dict()` 가 `json.dumps()` 를 그대로 통과한다(P4 가 `metrics.json`
     으로 보존한다).

추가로 **방식 정의 카운터**(수용 기준 둘째 문장, 01-plan 115행)를 같은
하네스에서 잰다 -- 완전일치 2변형은 임베딩·LLM 호출 0회, 임베딩 단독은
LLM 호출 0회, `llm_single` 은 스텁 호출 **정확히 1회**. 방식별 단위
테스트가 각자 재는 값이지만, 여기서는 **네 방식이 같은 입력을 받았을 때**
그렇다는 것을 한 표로 본다.

## 입력은 실물 데이터셋에서 온다 (01-plan 116행 "의존: P1 데이터셋")

`data/scenarios/` 의 실물 시나리오 2건(`sc-025` 정상 / `sc-001` 승진
호칭변경)을 U6 적재기(`evaluation.scenario_state.load_scenario_state`)로
적재하고, mention 은 그 시나리오 **첫 발화(turn 0)의 골드 mention** 을
그대로 쓴다 -- 픽스처를 지어내지 않는다.

세 밴드가 실제로 나오는지, 어느 방식이 맞히는지는 **여기서 묻지 않는다**
(그것은 P4-pilot-eval 의 지표다). 이 파일은 "같은 호출이 성립하는가"만
본다.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처, 가짜 임베딩
(`grouped_embedder`), 실 LLM 호출 0회.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

import pytest
from sqlalchemy import func, select

from app.db.models import AgentTrace, PendingQuestion, Person, PersonAlias
from app.er.judge import FakeJudge
from app.er.types import ERConfig
from app.tools.context import ToolContext
from evaluation.resolvers import DECISIONS, MentionDecision, Resolver, get_resolver
from evaluation.resolvers import registry as resolver_registry
from evaluation.resolvers.llm_single import TOOL_NAME
from evaluation.scenario_state import load_scenario_state, load_scenarios

#: **수집 시점**에 속성으로 읽는다(R-1 -- parametrize id 에 방식 이름이
#: 그대로 보이게 하고, 방식이 늘면 이 파일이 자동으로 그것도 돈다).
ALL_METHODS: tuple[str, ...] = resolver_registry.ALL_METHODS

#: 01-plan 114행이 요구하는 다섯 이름(결정 C 로 완전일치가 2변형).
#: `ALL_METHODS` 와 이 튜플이 어긋나면 표들이 방식을 빠뜨린 것이다.
EXPECTED_METHODS: tuple[str, ...] = (
    "proposed",
    "exact_raw",
    "exact_norm",
    "embedding_only",
    "llm_single",
)

USER_ID = "parity-user"
CONFIG = ERConfig()

#: 다섯 방식에 **같은 값**을 넘긴다. `None` 은 "호출자가 힌트를 주지
#: 않는다"이고, 그때 후보 검색을 쓰는 방식만 `derive_hints(mention)` 로
#: 스스로 유도한다(`app/er/candidates.py`) -- P4 러너의 기본 경로와 같다.
HINTS: dict[str, str] | None = None

#: 실물 시나리오 2건: 정상 1 · 승진 호칭변경 1(카테고리가 다른 두 사전
#: 상태에서 같은 계약이 성립하는지 본다).
SCENARIO_IDS: tuple[str, ...] = ("sc-025", "sc-001")

#: `grouped_embedder` 에 줄 그룹표 -- **값은 전부 라벨에 있는 문자열**이다
#: (지어낸 별칭을 넣지 않는다, 원칙8). 같은 그룹 안 문자열끼리 코사인
#: 유사도 ≈0.85, 그룹 밖과는 ≈0. 같은 문자열은 항상 같은 벡터라 임베딩이
#: 결정적이다.
EMBED_GROUPS: dict[str, list[str]] = {
    "sc-025-p1": ["엄마", "울엄마"],
    "sc-001-p1": ["김팀장", "팀장님", "김부장님", "부장님"],
}

#: 호출 1회가 `agent_traces` 에 남기는 행 수(측정값). 인물·별칭·질문
#: 테이블 증분은 **전 방식 0**(불변 규약 1)이고, 여기만 방식마다 다르다.
#: `proposed` 2 = `er_resolve` trace 1 + 그 안에서 부른 `search_person`
#: 툴 trace 1(P3-er 결정5 "trace 행은 1개" + 툴 호출 기록 1).
#: `embedding_only` 1 = `search_person` 툴 trace 1.
ALLOWED_TRACE_DELTA: dict[str, set[int]] = {
    "proposed": {2},
    "exact_raw": {0},
    "exact_norm": {0},
    "embedding_only": {1},
    "llm_single": {0},
}

#: 호출 1회의 임베딩 공급자 호출 수. **완전일치 2변형이 0** 이라는 것이
#: "임베딩을 쓰지 않는다"는 방식 정의의 증거다(01-plan 115행).
ALLOWED_EMBED_CALLS: dict[str, set[int]] = {
    "proposed": {1},
    "exact_raw": {0},
    "exact_norm": {0},
    "embedding_only": {1},
    "llm_single": {0},
}

#: 호출 1회의 LLM 호출 수(`FakeJudge` + 스텁 클라이언트 합산).
#: **완전일치·임베딩 단독이 0**, **`llm_single` 이 정확히 1** 이라는 것이
#: 수용 기준 둘째 문장이다. `proposed` 의 1 은 정의가 아니라 이 입력에서의
#: 측정값이다(후보가 규칙 필터를 통과해 3단계 LLM 판정까지 갔다).
ALLOWED_LLM_CALLS: dict[str, set[int]] = {
    "proposed": {1},
    "exact_raw": {0},
    "exact_norm": {0},
    "embedding_only": {0},
    "llm_single": {1},
}

#: `Resolver.resolve_mention` 의 매개변수(이름, 종류) -- 다섯 방식이 글자
#: 그대로 같아야 "같은 인자로 호출 가능"이 시그니처 수준에서도 성립한다.
EXPECTED_PARAMETERS: tuple[tuple[str, Any], ...] = (
    ("ctx", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ("mention", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ("utterance", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ("hints", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ("config", inspect.Parameter.KEYWORD_ONLY),
)

#: 실물 데이터셋을 한 번만 읽어 공유한다(파일 I/O 만 -- DB·네트워크 없음).
SCENARIOS: dict[str, dict[str, Any]] = {
    sc["id"]: sc for _, sc in load_scenarios()
}


# ---------------------------------------------------------------------------
# 스텁 · 계수기 (네트워크 0)
# ---------------------------------------------------------------------------


class CountingEmbedder:
    """임베딩 공급자 호출 수를 세는 얇은 래퍼(결과는 그대로 통과)."""

    def __init__(self, inner: Callable[[list[str]], list[list[float]]]) -> None:
        self._inner = inner
        self.calls = 0

    def __call__(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return self._inner(texts)


class CountingJudge:
    """`FakeJudge` 를 감싸 3단계 LLM 판정 호출 수를 센다(결정은 그대로)."""

    def __init__(self, inner: FakeJudge) -> None:
        self._inner = inner
        self.calls = 0

    def judge(self, mention: str, utterance: str, candidates: list[Any]) -> Any:
        self.calls += 1
        return self._inner.judge(mention, utterance, candidates)


class _StubMessages:
    def __init__(self, outer: "StubClaudeClient") -> None:
        self._outer = outer

    def create(self, **kwargs: Any) -> Any:
        self._outer.calls.append(kwargs)
        return self._outer.response


class StubClaudeClient:
    """`anthropic.Anthropic` 흉내(네트워크 0) -- 항상 같은 응답을 돌려주므로
    `llm_single` 이 결정적이다(단언 (v))."""

    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.messages = _StubMessages(self)


def _claude_tool_response(payload: dict) -> Any:
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=TOOL_NAME, input=payload)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=20),
        model="stub-model",
        stop_reason="tool_use",
    )


# ---------------------------------------------------------------------------
# 하네스 픽스처 -- 이름 -> 팩토리 kwargs 표는 여기에만 있다 (R-1)
# ---------------------------------------------------------------------------


@dataclass
class ParityHarness:
    """한 시나리오의 사전 상태 + 다섯 방식이 공유하는 호출 인자."""

    scenario_id: str
    ctx: ToolContext
    person_ids: list[int]
    mention: str
    utterance: str
    gold_person_id: str
    kwargs_by_method: dict[str, dict[str, Any]]
    embedder: CountingEmbedder
    judge: CountingJudge
    client: StubClaudeClient

    def reset_counters(self) -> None:
        self.embedder.calls = 0
        self.judge.calls = 0
        self.client.calls.clear()

    @property
    def llm_calls(self) -> int:
        """방식과 무관하게 이 하네스에서 관측된 LLM 호출의 총합."""
        return self.judge.calls + len(self.client.calls)

    def call(self, method: str) -> MentionDecision:
        """다섯 방식을 **같은 인자**로 부르는 단 하나의 호출 지점."""
        resolver = get_resolver(method, **self.kwargs_by_method[method])
        return resolver.resolve_mention(
            self.ctx, self.mention, self.utterance, HINTS, config=CONFIG
        )


def _first_turn_mention(scenario: dict[str, Any]) -> tuple[str, str]:
    """첫 발화(turn 0)의 골드 mention `(surface, gold_person_id)`."""
    for mention in scenario["mentions"]:
        if mention["turn"] == 0:
            return mention["surface"], mention["gold_person_id"]
    raise AssertionError(f"{scenario['id']}: turn 0 mention 이 없다")


def _state_counts(db_session: Any) -> dict[str, int]:
    models = {
        "persons": Person,
        "person_aliases": PersonAlias,
        "pending_questions": PendingQuestion,
    }
    return {
        table: db_session.execute(
            select(func.count()).select_from(model)
        ).scalar_one()
        for table, model in models.items()
    }


def _trace_count(db_session: Any) -> int:
    return db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()


@pytest.fixture()
def parity_harness(db_session, grouped_embedder) -> Callable[[str], ParityHarness]:
    """실물 시나리오를 적재하고 다섯 방식의 하네스를 만든다.

    **이름 → 팩토리 kwargs 표가 이 픽스처 안에 있다**(R-1 허용 범위):
    `proposed` 는 `judge=`, `llm_single` 은 `client=`(+공급자 선택 `env=`)를
    받아야 실 API 없이 결정적으로 돌기 때문이다. 나머지 셋은 인자가 없다 --
    빈 dict 가 "주입할 것이 없다"를 값으로 표현한다.

    스텁 응답의 `matched_person_id` 는 **적재된 실제 `persons.id`** 라서
    `llm_single` 이 사전 상태 밖 id 로 강등되지 않는다. `FakeJudge` 도 같은
    id 들로 표를 만든다(두 방식이 같은 사전 상태를 본다).
    """

    def _make(scenario_id: str) -> ParityHarness:
        scenario = SCENARIOS[scenario_id]
        embedder = CountingEmbedder(grouped_embedder(EMBED_GROUPS))
        ctx = ToolContext(
            session=db_session,
            session_id=f"parity-{scenario_id}",
            user_id=USER_ID,
            embedder=embedder,
        )
        # 적재는 U6 적재기로(중복 구현 금지). `embedder=` 를 명시해야
        # 별칭 임베딩이 채워진다 -- 주지 않으면 임베딩 단독·제안 방식이
        # `embedding_skipped` 로 떨어진다(scenario_state docstring R-6 절).
        state = load_scenario_state(ctx, scenario, embedder=embedder)
        surface, gold_person_id = _first_turn_mention(scenario)

        judge = CountingJudge(
            FakeJudge(table={pid: 0.9 for pid in state.created_person_ids})
        )
        client = StubClaudeClient(
            _claude_tool_response(
                {
                    "decision": "merge",
                    "matched_person_id": state.created_person_ids[0],
                    "s_llm": 0.9,
                    "reason": "stub",
                    "candidate_person_ids": list(state.created_person_ids),
                }
            )
        )
        kwargs_by_method: dict[str, dict[str, Any]] = {
            "proposed": {"judge": judge},
            "exact_raw": {},
            "exact_norm": {},
            "embedding_only": {},
            "llm_single": {"client": client, "env": {"LLM_PROVIDER": "anthropic"}},
        }
        return ParityHarness(
            scenario_id=scenario_id,
            ctx=ctx,
            person_ids=list(state.created_person_ids),
            mention=surface,
            utterance=scenario["utterances"][0],
            gold_person_id=gold_person_id,
            kwargs_by_method=kwargs_by_method,
            embedder=embedder,
            judge=judge,
            client=client,
        )

    return _make


# =========================================================================
# 0. 방식 목록과 표가 어긋나지 않는다
# =========================================================================


def test_all_methods_are_the_five_expected_names() -> None:
    """수용 기준 첫 문장 -- 베이스라인 3종(완전일치 2변형·임베딩 단독·
    LLM 단일)과 `proposed` 가 모두 등록돼 있고 순서가 고정이다."""

    assert ALL_METHODS == EXPECTED_METHODS


@pytest.mark.parametrize(
    "table_name, table",
    [
        ("ALLOWED_TRACE_DELTA", ALLOWED_TRACE_DELTA),
        ("ALLOWED_EMBED_CALLS", ALLOWED_EMBED_CALLS),
        ("ALLOWED_LLM_CALLS", ALLOWED_LLM_CALLS),
    ],
)
def test_expectation_tables_cover_every_method(
    table_name: str, table: dict[str, set[int]]
) -> None:
    """표가 방식을 빠뜨리면 그 방식은 조용히 검사되지 않는다 -- 방식이
    늘면 `KeyError` 가 아니라 여기서 먼저 깨진다(원칙8)."""

    assert set(table) == set(ALL_METHODS), table_name


@pytest.mark.parametrize("name", ALL_METHODS)
def test_factory_creates_a_resolver_without_keys_or_network(name: str) -> None:
    """`get_resolver(name)` 가 인자 없이도 객체를 만든다(실 키·SDK 요구 금지).
    P4 러너가 `for name in ALL_METHODS:` 로 도는 전제다."""

    resolver = get_resolver(name)

    assert isinstance(resolver, Resolver)
    assert resolver.name == name
    assert set(resolver.supported_decisions) <= set(DECISIONS)


@pytest.mark.parametrize("name", ALL_METHODS)
def test_resolve_mention_signature_is_identical(name: str) -> None:
    """(동일 인터페이스) 다섯 방식의 `resolve_mention` 매개변수가 같다."""

    signature = inspect.signature(get_resolver(name).resolve_mention)
    got = tuple((p.name, p.kind) for p in signature.parameters.values())

    assert got == EXPECTED_PARAMETERS


# =========================================================================
# 1. 계약 -- 같은 함수·같은 인자로 다섯 방식 전부 (U7 (i)~(iv), (vi))
# =========================================================================


@pytest.mark.dbtest
@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
@pytest.mark.parametrize("name", ALL_METHODS)
def test_contract_holds_for_every_method(
    db_session, parity_harness, name: str, scenario_id: str
) -> None:
    """수용 기준 넷째 문장의 본체 -- 같은 `ctx`·mention·utterance·`hints`·
    `ERConfig` 로 부르고 (i)~(iv)·(vi)를 단언한다."""

    harness = parity_harness(scenario_id)
    resolver = get_resolver(name, **harness.kwargs_by_method[name])

    before = _state_counts(db_session)
    before_traces = _trace_count(db_session)
    decision = resolver.resolve_mention(
        harness.ctx, harness.mention, harness.utterance, HINTS, config=CONFIG
    )
    after = _state_counts(db_session)
    after_traces = _trace_count(db_session)

    # (i) 반환 타입·정체성
    assert isinstance(decision, MentionDecision)
    assert decision.method == name
    assert decision.mention == harness.mention

    # (ii) 결정 어휘
    assert decision.decision in resolver.supported_decisions
    assert set(resolver.supported_decisions) <= set(DECISIONS)

    # (iii) person_id 는 merge 에서만, 그리고 적재한 사전 상태 안의 인물
    assert (decision.person_id is not None) is (decision.decision == "merge")
    assert decision.person_id is None or decision.person_id in harness.person_ids
    assert 0.0 <= decision.score <= 1.0

    # (iv) 부수효과 0 -- 인물·별칭·질문은 전 방식 증분 0, trace 만 표대로
    assert after == before
    assert after_traces - before_traces in ALLOWED_TRACE_DELTA[name]

    # (vi) JSON 직렬화(P4 가 metrics.json 으로 보존한다)
    dumped = json.dumps(decision.to_dict(), ensure_ascii=False)
    assert json.loads(dumped)["method"] == name


@pytest.mark.dbtest
@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
@pytest.mark.parametrize("name", ALL_METHODS)
def test_same_input_twice_gives_the_same_decision(
    parity_harness, name: str, scenario_id: str
) -> None:
    """(v) 재현성(원칙8) -- 같은 입력 두 번이면 `decision`·`person_id`·
    `score` 가 같다. LLM 은 `FakeJudge`·스텁으로 고정돼 있다."""

    harness = parity_harness(scenario_id)

    first = harness.call(name)
    second = harness.call(name)

    assert (first.decision, first.person_id, first.score) == (
        second.decision,
        second.person_id,
        second.score,
    )
    assert [c.person_id for c in first.candidates] == [
        c.person_id for c in second.candidates
    ]


# =========================================================================
# 2. 방식 정의 카운터 (수용 기준 둘째 문장, 01-plan 115행)
# =========================================================================


@pytest.mark.dbtest
@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
@pytest.mark.parametrize("name", ALL_METHODS)
def test_method_definition_call_counters(
    parity_harness, name: str, scenario_id: str
) -> None:
    """같은 입력에서 각 방식이 임베딩·LLM 을 몇 번 부르는가.

    완전일치 2변형은 둘 다 0, 임베딩 단독은 LLM 0, `llm_single` 은 스텁
    호출 정확히 1(표에 값으로). 방식 정의가 무너지면(예: 완전일치가 몰래
    임베딩을 쓰면) 여기서 깨진다.
    """

    harness = parity_harness(scenario_id)
    harness.reset_counters()

    harness.call(name)

    assert harness.embedder.calls in ALLOWED_EMBED_CALLS[name]
    assert harness.llm_calls in ALLOWED_LLM_CALLS[name]


# =========================================================================
# 3. 한 ctx 에서 다섯 방식을 연달아 (P4 러너가 도는 형태 그대로)
# =========================================================================


@pytest.mark.dbtest
@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_every_method_runs_on_one_shared_ctx(
    db_session, parity_harness, scenario_id: str
) -> None:
    """`for name in ALL_METHODS:` 한 줄로 다섯 방식이 **같은 사전 상태**를
    보고 답한다(01-plan 53행 P4 러너의 형태). 방식 간 순서 의존이 있으면
    (한 방식이 상태를 바꾸면) 여기서 드러난다."""

    harness = parity_harness(scenario_id)
    before = _state_counts(db_session)

    results = {method: harness.call(method) for method in ALL_METHODS}

    assert set(results) == set(EXPECTED_METHODS)
    assert all(isinstance(d, MentionDecision) for d in results.values())
    assert all(d.decision in DECISIONS for d in results.values())
    assert _state_counts(db_session) == before
    # 다섯 답을 한 벌로 직렬화할 수 있다(P4 metrics.json 의 한 행 형태).
    payload = json.dumps(
        {method: d.to_dict() for method, d in results.items()}, ensure_ascii=False
    )
    assert set(json.loads(payload)) == set(ALL_METHODS)
