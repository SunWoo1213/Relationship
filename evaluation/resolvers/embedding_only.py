"""Refs: P3-baselines S3.7 D4 D5 D10 원칙2 -- 베이스라인 2 임베딩 유사도 단독.

**두 임계치**(base.py 불변 규약 4): 이 방식은 `T_merge`/`T_new` 를 **`s_emb`
에 그대로** 적용한다(결정 D(i)) -- `app.er.confidence.band_for(s_emb, config)`
를 재사용하고 베이스라인 전용 τ 를 새로 두지 않는다. 그래서 P4 곡선의 x축
(`T_merge`, `T_new`=0.3 고정, S3.7)이 이 방식과 제안 방식에 **같은 의미**를
갖고, 같은 스윕이 두 방식의 분기를 함께 움직인다.

## 무엇을 하는 방식인가 (01-plan 56행·103행)

`app.er.candidates.search_candidates()` 를 **재사용**해(중복 구현 금지 --
D5 별칭 단위 top-K -> 인물별 max 유사도) 후보를 얻고, 그 후보들의 `s_emb`
**하나만** 본다. 2단계 규칙 필터(`app/er/rules.py`)도 3단계 LLM 판정
(`app/er/judge.py`)도 부르지 않는다 -- 원칙4 가 요구한 4단계 중 1·4단계만
남긴 형태가 이 베이스라인의 정의다.

| 상태 | 결정 | 근거 |
|---|---|---|
| 최고 `s_emb` >= `T_merge`, 동점 없음 | `merge`(`person_id`=최고 후보, `score`=`s_emb`) | 임계치를 넘은 유일한 후보 |
| 최고 `s_emb` >= `T_merge`, **동점 2건 이상** | `identity`(`person_id` **None**) + `forced_reason="tie"` | 같은 점수 둘 중 하나를 임의로 고르는 것이 곧 오병합이다(원칙1) |
| `T_new` <= 최고 `s_emb` < `T_merge` | `identity`(후보 전부) | 확신도 미달 -> 사람에게 묻는다(원칙1·2) |
| 최고 `s_emb` < `T_new` | `new_person` | 아는 사람으로 볼 근거가 없다 |
| 후보 0건 | `new_person` + `forced_reason="no_candidates"` | 비교할 대상이 없다(예외로 죽지 않는다 -- 불변 규약 2) |

`decision` 은 언제나 `band_for()` 의 결과이거나 그보다 **보수적인 쪽으로만**
움직인다(`merge` -> `identity`). 임계치를 넘지 못한 후보를 이 방식이 위로
끌어올리는 경로는 없다. 강등 여부는 `detail["band_by_threshold"]`(임계치만
적용한 밴드)와 `decision` 의 차이로 드러난다(원칙9).

## 임베딩 공급자가 없을 때 (`embedding_skipped`)

`ctx.embedder` 가 없거나 이 사용자의 별칭에 저장된 임베딩이 하나도 없으면
`search_person` 이 임베딩 검색 자체를 건너뛰고 모든 후보의
`rule_flags["embedding_skipped"] = True`·`similarity = 0.0` 을 세운다
(`app/tools/persons.py` "임베딩 skip 규칙"). 이 방식은 그 `s_emb = 0` 을
그대로 `band_for()` 에 넣는다 -- `T_new` > 0 인 모든 설정(S3.7 은 0.3 으로
고정)에서 결과는 `new_person` 이고, 그 사실은 `detail["embedding_skipped"]
= True` 와 `forced_reason="embedding_skipped"` 로 남는다. 여기서 밴드를
손으로 `new_person` 이라고 **못 박지 않는 이유**는 불변 규약 4 다: 결정은
임계치가 하고, 이 모듈은 임계치를 재정의하지 않는다.

## `score` 의 의미 (base.py `MentionDecision.score` 주석 참조)

`score` 는 **최고 후보의 `s_emb`** 이고 결정 종류와 무관하게 같은 축이다
(후보 0건이면 0.0). 제안 방식의 3신호 결합 확신도(`0.5·s_llm + 0.3·s_emb +
0.2·s_rule`, D3)와 **같은 축에 놓고 비교하면 안 된다** -- 두 수의 의미가
다르다(그 판단은 P4 몫이며 base.py 가 이미 "의미는 방식마다 다르다"고 못
박았다).

## 후보 집합에 대하여 (원칙8 -- 베이스라인을 약하게 만들지 않는다)

`search_person` 의 후보 집합은 (별칭 정확/부분 일치) ∪ (임베딩 top-K) 의
합집합이라 임베딩 유사도가 0 인 인물도 목록에 들어올 수 있다. 이 방식은
그 인물들을 **버리지 않고 후보로 남기되**(원칙9 -- 본 것을 남긴다) 판정에는
`s_emb` 만 쓴다. `rule_flags` 6개는 배제·가점 어디에도 쓰지 않으므로
`signals` 에는 `embedding_skipped` 만 옮긴다(2단계 규칙 필터를 돌리지
않았으므로 `s_rule` 은 계산된 적이 없고, 계산되지 않은 값을 0.0 으로 적어
두면 "규칙 신호가 0 이었다"로 오독된다).

## `top_k` 는 건드리지 않는다 (F-bdd6c5)

`search_candidates(top_k=…)` 인자는 현재 `search_person` 에 전달되지 않아
실제 K 는 `app.settings.SEARCH_TOP_K` 고정이다(P3-er 05-remediation
F-bdd6c5, 열린 소견). 그래서 이 어댑터는 `top_k` 를 **넘기지 않고**
`ERConfig.top_k` 로 스윕하지도 않는다 -- 스윕하면 trace 에 기록되는 K 와
실제 K 가 어긋난다.

## 부수효과 0 (불변 규약 1)

`search_candidates` -> `search_person` 은 조회만 한다. 인물·별칭·질문을
만들지 않는다. 다만 `search_person` 이 `@traced` 이므로 `agent_traces` 에
그 툴 호출 기록 1행이 남는다 -- 감싼 함수의 성질이고 인물 상태를 바꾸지
않는다(proposed.py 와 같은 예외).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.er.candidates import search_candidates
from app.er.confidence import band_for, ge_with_tolerance
from app.settings import er_config
from evaluation.resolvers.base import DECISIONS, MentionDecision, ResolverCandidate
from evaluation.resolvers.registry import register

if TYPE_CHECKING:
    from app.er.types import ERConfig, ScoredCandidate
    from app.tools.context import ToolContext

#: `RESOLVERS` 등록 이름 = `MentionDecision.method` = `metrics.json` 키
#: (P4 인계 4). 바꾸면 P4 산출물 스키마가 바뀐다.
METHOD_NAME = "embedding_only"

#: `detail["forced_reason"]` 어휘(불변 규약 2 -- 예외 대신 사유).
NO_CANDIDATES = "no_candidates"
TIE = "tie"
EMBEDDING_SKIPPED = "embedding_skipped"
EMPTY_MENTION = "empty_mention"

#: `ask_user` 를 부르지 않으므로(불변 규약 1) 물었을 `kind` 만 남긴다 --
#: P4 `ask_user_rate_by_kind`(eval-harness §2) 입력. `proposed.py`·
#: `exact_match.py` 와 같은 대응이다(`merge` 는 묻지 않는다).
_ASK_KIND_BY_DECISION: dict[str, str | None] = {
    "merge": None,
    "identity": "identity",
    "new_person": "new_person",
}


def _clamp01(value: float) -> float:
    numeric = float(value)
    if numeric != numeric:  # NaN -- 어떤 비교에도 False 이므로 따로 거른다.
        return 0.0
    return min(1.0, max(0.0, numeric))


def approx_equal(a: float, b: float) -> bool:
    """`a == b` 를 **`ge_with_tolerance()` 와 같은 허용오차**로 판정한다
    (`a >= b` 이면서 `b >= a`). 동점 판정과 임계치 판정이 서로 다른 오차를
    쓰면 "임계치는 넘었는데 동점은 아니다" 같은 모순이 생긴다 -- 비교
    함수의 단일 출처는 `app.er.confidence.ge_with_tolerance` 하나다
    (P3-er F-7fe239)."""

    return ge_with_tolerance(a, b) and ge_with_tolerance(b, a)


def _signals(candidate: ScoredCandidate) -> dict[str, float]:
    """후보 하나의 원자료. 이 방식이 실제로 본 신호(`s_emb`)와, 그 값을
    해석하는 데 필요한 사실(`embedding_skipped`)만 담는다 -- 모듈 docstring
    "후보 집합에 대하여" 참조."""

    return {
        "s_emb": _clamp01(candidate.s_emb),
        "embedding_skipped": 1.0 if candidate.rule_flags.get("embedding_skipped") else 0.0,
    }


def decide_from_candidates(
    candidates: list[ScoredCandidate],
    config: ERConfig | None = None,
    *,
    mention: str = "",
    hints: dict[str, str] | None = None,
    forced_reason: str | None = None,
) -> MentionDecision:
    """**순수 함수** -- DB·네트워크 없이 후보 목록 -> `MentionDecision`
    (01-plan 103행 "경계값 테스트가 DB 없이 가능하게").

    `config` 가 `None` 이면 `app.settings.er_config()`(환경변수 2층, P3-er
    결정8)를 쓴다 -- 이 모듈이 기본 임계치를 따로 정하면 네 방식의 설정
    출처가 갈라진다(불변 규약 4).

    후보 순서는 `(-s_emb, person_id)` 로 **다시 정렬**한다. 입력 순서는
    `search_person` 의 정렬(exact_alias 우선 -> similarity -> id)이라 이
    방식이 보는 축(`s_emb`)과 다르고, 같은 입력에 같은 목록이 나와야 P4
    수치가 재현된다(원칙8).

    `forced_reason` 인자는 호출자가 이미 아는 사유(예: 빈 mention)를 그대로
    싣기 위한 것이고, 그 경우 판정은 `new_person` 으로 고정된다.
    """

    resolved_config = config if config is not None else er_config()

    ordered = sorted(
        candidates,
        key=lambda candidate: (-_clamp01(candidate.s_emb), candidate.person_id),
    )
    resolver_candidates = [
        ResolverCandidate(
            person_id=candidate.person_id,
            display_name=candidate.display_name,
            # 이 방식에서 후보별 점수는 그 후보의 `s_emb` 자체다(제안
            # 방식과 달리 결합 확신도가 없다).
            score=_clamp01(candidate.s_emb),
            signals=_signals(candidate),
        )
        for candidate in ordered
    ]

    embedding_skipped = bool(ordered) and all(
        bool(candidate.rule_flags.get("embedding_skipped")) for candidate in ordered
    )
    top_s_emb = _clamp01(ordered[0].s_emb) if ordered else 0.0
    tied = [c for c in ordered if approx_equal(_clamp01(c.s_emb), top_s_emb)]
    band_by_threshold = band_for(top_s_emb, resolved_config)

    decision = band_by_threshold
    person_id: int | None = None

    if forced_reason is not None:
        # 호출자가 이미 판정 불가를 알고 있다(예: 빈 mention).
        decision = "new_person"
    elif not ordered:
        # 비교할 후보가 없다 -- 예외가 아니라 결정으로 표현한다(불변 규약 2).
        decision = "new_person"
        forced_reason = NO_CANDIDATES
    elif decision == "merge" and len(tied) > 1:
        # 같은 점수의 두 인물 중 하나를 임의로 고르는 것이 곧 오병합이다
        # (원칙1) -- 고르지 않고 사람에게 묻는다.
        decision = "identity"
        forced_reason = TIE
    elif decision == "merge":
        person_id = ordered[0].person_id

    if forced_reason is None and embedding_skipped:
        # 공급자가 없어 `s_emb` 가 전부 0 인 상태 -- 밴드는 임계치가 정했고
        # (모듈 docstring), 여기서는 그 사실만 사유로 남긴다.
        forced_reason = EMBEDDING_SKIPPED

    detail: dict[str, Any] = {
        "forced_reason": forced_reason,
        # 임계치만 적용했을 때의 밴드. `decision` 과 다르면 강등이 있었다는
        # 뜻이다(원칙9 -- "임계치 때문인가, 동점 때문인가"를 P4 가 가른다).
        "band_by_threshold": band_by_threshold,
        "top_s_emb": top_s_emb,
        "candidate_count": len(ordered),
        "tied_person_ids": [c.person_id for c in tied] if len(tied) > 1 else [],
        "embedding_skipped": embedding_skipped,
        # 실행하지 않으므로(불변 규약 1) 물었을 `kind` 만 남긴다.
        "ask_kind": _ASK_KIND_BY_DECISION[decision],
        # 후보 검색에 실제로 쓰인 hints(`search_candidates` 가 유도했을 수
        # 있다 -- `app.er.dictionary.derive_hints`). 판정에는 쓰지 않는다.
        "hints": dict(hints) if hints else {},
        "thresholds": {
            "t_merge": resolved_config.t_merge,
            "t_new": resolved_config.t_new,
        },
        # 이 방식이 쓴/쓰지 않은 신호(원칙4 의 대비군 정의 -- P4 표에
        # "무엇을 안 쓰고 이만큼 했는가"가 그대로 적힌다).
        "uses_embedding": True,
        "uses_llm": False,
        "uses_rules": False,
        "uses_thresholds": True,
    }

    return MentionDecision(
        method=METHOD_NAME,
        mention=mention,
        decision=decision,
        person_id=person_id,
        score=top_s_emb,
        candidates=resolver_candidates,
        trace_id=None,
        tokens_in=0,
        tokens_out=0,
        detail=detail,
    )


@register(METHOD_NAME)
class EmbeddingOnlyResolver:
    """베이스라인 2 -- 후보 검색(1단계) + 임계치 분기(4단계)뿐.

    `supported_decisions` 는 세 밴드 전부다 -- `band_for()` 를 그대로 쓰므로
    `identity` 가 자연스럽게 나오고(결정 B(i)), 동점에서 하나를 고르게
    만들면 오병합률이 인위적으로 부풀어 베이스라인을 약하게 만드는 셈이
    된다(원칙8).

    LLM 클라이언트도 판정자(`Judge`)도 받지 않는다 -- 생성자에 인자가 없는
    것이 "LLM 호출 0회"(01-plan 115행)의 구조적 보장이다.
    """

    name: str = METHOD_NAME
    supported_decisions: tuple[str, ...] = DECISIONS

    def resolve_mention(
        self,
        ctx: ToolContext,
        mention: str,
        utterance: str,
        hints: dict[str, str] | None = None,
        *,
        config: ERConfig | None = None,
    ) -> MentionDecision:
        """후보 검색 1회 -> 순수 판정 1회.

        `utterance` 는 **받지만 쓰지 않는다** -- 발화 맥락을 읽는 것은 LLM
        판정(3단계)의 일이고, 이 방식이 맥락을 못 본다는 사실 자체가 비교
        정보다. `hints` 는 `search_candidates` 에 그대로 넘어가며(`None`
        이면 `derive_hints(mention)` 유도) 후보를 **배제하지 않는다**
        (`search_person` "후보 집합(배제 없음)").

        빈 mention 은 `search_person` 이 `InvalidValue` 를 던지는 입력이라
        DB 를 부르기 전에 `new_person` + `forced_reason="empty_mention"` 으로
        돌린다(불변 규약 2 -- 한 방식만 예외로 죽으면 분모가 달라진다).
        그 밖의 예외(DB 장애 등)는 삼키지 않는다 -- 인프라 실패를 "성능"으로
        기록하면 그것이야말로 평가의 결함이다(원칙8).
        """

        if mention is None or not mention.strip():
            return decide_from_candidates(
                [],
                config,
                mention=mention or "",
                hints=hints,
                forced_reason=EMPTY_MENTION,
            )

        # `top_k` 를 넘기지 않는다(F-bdd6c5 -- 모듈 docstring 참조).
        found = search_candidates(ctx, mention, hints)
        return decide_from_candidates(
            found.candidates,
            config,
            mention=mention,
            hints=found.hints,
        )
