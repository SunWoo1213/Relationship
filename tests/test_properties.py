"""Refs: FIX-024 FIX-021 D10 D12 D13 P7-push 원칙1 원칙2 원칙3 원칙7 --
순수 함수의 "항상 지켜야 할 성질" 을 예시가 아니라 `hypothesis` 로 무작위
탐색해 확인한다. 대상은 전부 **순수 함수**(DB·LLM·네트워크 호출 없음):
`app/er/confidence.py::combine`/`band_for`/`decide`, `app/push/
payload.py::build_push_payload`, `app/briefing/compose.py::
validate_briefing`.

## 이 파일이 하지 않는 것

- 제품 코드(`app/`)를 고치지 않는다(위임 범위, FIX-024). 성질 탐색 중
  실제로 깨지는 입력을 찾으면 **그 입력을 최소 반례로 고정한 회귀
  테스트**(`pytest.raises` 로 "지금 이렇게 예외를 던진다"를 그대로
  단언)만 추가하고, 그 입력은 "항상 성립해야 하는" 넓은 성질 테스트의
  탐색 범위에서는 `assume()`/전용 전략으로 제외한다 -- 성질 테스트
  자체가 실패 상태로 남지 않는다(이 파일의 완료 판정은 `pytest
  tests/test_properties.py` 가 **passed** 로 끝나는 것, FIX-024 판정
  표 2~5행). 아래 "FIX-024 에서 발견한 위반(보고용, 미수정)" 절에 모든
  최소 반례를 모아 둔다.

## FIX-024 에서 발견한 위반(보고용, 미수정)

제품 코드는 고치지 않고 아래 7개 최소 반례를 회귀 테스트로만 고정한다
(각 테스트 docstring 에 반복). 사용자 결정 후 별도 FIX 로 다룬다.

1. `app/er/confidence.py::combine` -- `rule_checked=0`(미측정)인데
   `config.w_llm + config.w_emb == 0`(예: `w_llm=0, w_emb=0, w_rule=1`,
   가중치 합 1.0 이라 `ERConfig` 생성 자체는 통과)이면 분모가 0 이 되어
   `ZeroDivisionError` 를 던진다 -- `InvalidValue` 가 아니라 처리되지
   않은 예외. `test_combine_raises_zero_division_when_rule_unmeasured_and_llm_emb_weights_zero_FOUND`.
2~3. `app/briefing/compose.py::validate_briefing` -- `BriefingLine.text`
   또는 `Suggestion.text` 가 `None` 이면(기본 근거는 정상적으로 알려진
   값이라 `no_basis`/`unknown_basis` 를 통과) 금지 표현·줄바꿈 검사의
   `in` 연산이 `TypeError: argument of type 'NoneType' is not
   iterable`(제안) / `not a container or iterable`(요약 줄)로 죽는다.
   `test_validate_briefing_raises_when_line_text_is_none_FOUND`,
   `test_validate_briefing_raises_when_suggestion_text_is_none_FOUND`.
4~5. 같은 함수 -- `BriefingLine.basis`/`Suggestion.basis` 가 `None` 이면
   `basis.get(...)` 에서 `AttributeError` 로 죽는다.
   `test_validate_briefing_raises_when_line_basis_is_none_FOUND`,
   `test_validate_briefing_raises_when_suggestion_basis_is_none_FOUND`.
6. 같은 함수 -- `basis["fact_keys"]`/`basis["event_ids"]` 원소가 해시
   불가능한 값(예: 중첩 리스트)이면 `known_fact_keys`/`known_event_ids`
   집합 멤버십 검사(`in`)에서 `TypeError: unhashable type`. FIX-021
   이 고친 `pattern_sentences[].key` 와 **같은 종류**지만 그때 고친
   자리가 아니다(줄·제안의 근거 원소는 아직 `isinstance` 가드가 없다).
   `test_validate_briefing_raises_when_fact_keys_element_is_unhashable_FOUND`.
7. 같은 함수 -- `pattern_sentences[].sentence` 가 `None` 이 아닌데
   문자열도 아니면(예: 정수) `_extract_mentioned_counts` 의 정규식
   `findall` 이 `TypeError: expected string or bytes-like object` 로
   죽는다(`sentence=None` 자체는 `missing_pattern` 분기로 안전하게
   처리된다 -- 이 반례와 다르다).
   `test_validate_briefing_raises_when_pattern_sentence_is_non_string_non_none_FOUND`.

이 7건은 전부 FIX-021 이 세운 전제("`validate_briefing()` 은 `raw` 를
**직접** 받을 수도 있어 `_parse_composed` 를 거치지 않은 경로를
보장하지 않는다")와 같은 자리에서 나왔다 -- FIX-021 은 `key` 필드 하나만
고쳤고, 나머지 필드(`text`·`basis`·`fact_keys`/`event_ids` 원소·
`sentence`)는 그대로다.
"""

from __future__ import annotations

import json
import string
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from app.briefing.compose import validate_briefing
from app.briefing.types import BriefingInput, BriefingLine, ComposedBriefing, Suggestion
from app.er.confidence import band_for, combine, decide
from app.er.types import ERConfig, Judgement, ScoredCandidate
from app.push.payload import build_push_payload
from app.settings import PUSH_BODY_MAX_CHARS, PUSH_TTL_MAX_SECONDS
from app.tools.types import InvalidValue

#: 파일 전체 공통 설정(판정 표 6행) -- 예시 수 상한으로 CI 시간을 관리하고
#: `derandomize=True` 로 매 실행 같은 예시 집합을 써 재현성을 보장한다
#: (seed 를 별도로 출력할 필요가 없다 -- 항상 같은 시드로 고정되므로).
#: `deadline=None` -- 느린 CI 러너에서 개별 예시 시간 제한으로 깨지는
#: 것을 막는다(함수 자체는 순수·가볍다, 느려질 이유가 없다).
_HYP = settings(max_examples=60, deadline=None, derandomize=True)

_BAND_RANK = {"new_person": 0, "identity": 1, "merge": 2}


# ---------------------------------------------------------------------------
# 공유 전략
# ---------------------------------------------------------------------------


def _unit_float() -> st.SearchStrategy[float]:
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


@st.composite
def _weights_summing_to_one(draw: st.DrawFn) -> tuple[float, float, float]:
    """`(w_llm, w_emb, w_rule)` -- 합이 1.0(부동소수 표현 오차 이내)인
    세 음이 아닌 가중치. `[0,1]` 위 두 점을 잘라 세 구간 길이로 쓴다."""
    a, b = sorted(draw(st.lists(_unit_float(), min_size=2, max_size=2)))
    return a, b - a, 1.0 - b


@st.composite
def _threshold_pair(draw: st.DrawFn) -> tuple[float, float]:
    """`(t_new, t_merge)` -- `t_new <= t_merge` 를 만족하는 쌍(원칙2)."""
    t_new, t_merge = sorted(draw(st.lists(_unit_float(), min_size=2, max_size=2)))
    return t_new, t_merge


@st.composite
def _scored_candidate(draw: st.DrawFn, person_id: int) -> ScoredCandidate:
    s_emb = draw(_unit_float())
    s_rule = draw(_unit_float())
    rule_checked = draw(st.integers(min_value=0, max_value=5))
    rule_passed = draw(st.integers(min_value=0, max_value=rule_checked)) if rule_checked > 0 else 0
    return ScoredCandidate(
        person_id=person_id,
        display_name=f"person-{person_id}",
        aliases=[f"alias-{person_id}"],
        s_emb=s_emb,
        s_rule=s_rule,
        rule_checked=rule_checked,
        rule_passed=rule_passed,
        passed_rules=True,
    )


# ===========================================================================
# 2. app/er/confidence.py::combine -- 결합 함수
# ===========================================================================


@given(
    weights=_weights_summing_to_one(),
    s_llm=_unit_float(),
    s_emb=_unit_float(),
    s_rule=_unit_float(),
    rule_checked=st.integers(min_value=0, max_value=5),
)
@_HYP
def test_combine_result_within_unit_interval(
    weights: tuple[float, float, float],
    s_llm: float,
    s_emb: float,
    s_rule: float,
    rule_checked: int,
) -> None:
    """신호 ∈ [0,1] 이면 결과 ∈ [0,1](판정 표 2행 1절). `w_llm+w_emb==0`
    이면서 `rule_checked==0` 인 조합은 별도 발견(①)으로 고정했으므로
    여기서는 제외한다(아래 `assume`)."""
    w_llm, w_emb, w_rule = weights
    assume(abs((w_llm + w_emb + w_rule) - 1.0) <= 1e-9)
    assume(not (rule_checked == 0 and (w_llm + w_emb) < 1e-12))

    config = ERConfig(w_llm=w_llm, w_emb=w_emb, w_rule=w_rule)
    confidence = combine(s_llm, s_emb, s_rule, config, rule_checked=rule_checked)
    assert -1e-9 <= confidence <= 1.0 + 1e-9


@given(
    weights=_weights_summing_to_one(),
    s_llm=_unit_float(),
    s_emb=_unit_float(),
    s_rule=_unit_float(),
    rule_checked=st.integers(min_value=0, max_value=5),
)
@_HYP
def test_combine_result_within_observed_signal_range(
    weights: tuple[float, float, float],
    s_llm: float,
    s_emb: float,
    s_rule: float,
    rule_checked: int,
) -> None:
    """관측된 신호만 재정규화한 결과는 관측 신호들의 min~max 사이(D12,
    판정 표 2행 2절) -- 가중합(가중치 음수 없음·합 1)은 항상 입력들의
    볼록결합이므로 입력 범위를 벗어날 수 없다."""
    w_llm, w_emb, w_rule = weights
    assume(abs((w_llm + w_emb + w_rule) - 1.0) <= 1e-9)
    assume(not (rule_checked == 0 and (w_llm + w_emb) < 1e-12))

    config = ERConfig(w_llm=w_llm, w_emb=w_emb, w_rule=w_rule)
    confidence = combine(s_llm, s_emb, s_rule, config, rule_checked=rule_checked)

    observed = [s_llm, s_emb, s_rule] if rule_checked > 0 else [s_llm, s_emb]
    lo, hi = min(observed), max(observed)
    assert lo - 1e-9 <= confidence <= hi + 1e-9


@given(
    which_signal=st.sampled_from(["llm", "emb", "rule"]),
    rule_checked=st.integers(min_value=0, max_value=5),
)
@_HYP
def test_combine_single_signal_alone_never_reaches_merge_default_config(
    which_signal: str, rule_checked: int
) -> None:
    """어느 신호 하나만 1 이고 나머지가 0 이면(기본 설정 가중치
    `w_llm=0.5·w_emb=0.3·w_rule=0.2`, `T_merge=0.8`) merge 임계치 미만이다
    (원칙3·D12, 판정 표 2행 3절). 계산 근거: 측정됨(`rule_checked>0`)인
    경우 최댓값은 `w_llm=0.5`; 미측정(`rule_checked=0`, `s_rule` 무시)인
    경우 재정규화 가중치 최댓값은 `w_llm/(w_llm+w_emb)=0.625`. 둘 다
    `T_merge=0.8` 미만이므로 이 성질은 **기본 설정에서 실제로 성립한다**
    (임의 가중치로 일반화하면 `w_llm` 이 `T_merge` 보다 크게 설정될 수
    있어 성립하지 않는다 -- 그래서 여기서는 기본 `ERConfig()` 로 고정해
    "원칙 문장 그대로" 단언한다)."""
    config = ERConfig()
    s_llm = 1.0 if which_signal == "llm" else 0.0
    s_emb = 1.0 if which_signal == "emb" else 0.0
    s_rule = 1.0 if which_signal == "rule" else 0.0

    confidence = combine(s_llm, s_emb, s_rule, config, rule_checked=rule_checked)
    assert confidence < config.t_merge
    assert band_for(confidence, config) != "merge"


@pytest.mark.xfail(strict=True, raises=ZeroDivisionError, reason="FIX-024 발견① -- FIX-025 에서 수정 예정(고치면 통과해 xfail 표시를 떼라고 알린다)")
def test_combine_raises_zero_division_when_rule_unmeasured_and_llm_emb_weights_zero_FOUND() -> None:
    """FIX-024 발견①(보고, 미수정) -- `rule_checked=0`(미측정)이고
    `w_llm=w_emb=0·w_rule=1.0`(가중치 합 1.0 이라 `ERConfig` 생성 자체는
    통과)이면 `combine()` 이 `(w_llm*s_llm+w_emb*s_emb)/(w_llm+w_emb)`
    에서 0 으로 나눠 `ZeroDivisionError` 를 던진다. `InvalidValue` 가
    아니라 처리되지 않은 예외라서, 호출부가 이 경로만 따로 잡지 않으면
    그대로 올라간다(원칙8 "잘못된 입력으로 조용히 계산하지 않는다" 는
    지켜지지만 예외 종류가 설계 의도와 다르다). 최소 반례:
    `combine(0.0, 0.0, 0.0, ERConfig(w_llm=0.0, w_emb=0.0, w_rule=1.0),
    rule_checked=0)`. 제품 코드는 고치지 않는다(FIX-024 위임 범위) --
    사용자 결정 후 별도 FIX."""
    config = ERConfig(w_llm=0.0, w_emb=0.0, w_rule=1.0)
    combine(0.0, 0.0, 0.0, config, rule_checked=0)


# ===========================================================================
# 3. app/er/confidence.py::band_for / decide -- 구간 판정
# ===========================================================================


@given(t=_threshold_pair(), confidence=_unit_float())
@_HYP
def test_band_for_returns_one_of_three_bands(t: tuple[float, float], confidence: float) -> None:
    """결과는 merge/identity/new_person 중 하나(판정 표 3행 1절)."""
    t_new, t_merge = t
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    assert band_for(confidence, config) in _BAND_RANK


@given(t=_threshold_pair(), c1=_unit_float(), c2=_unit_float())
@_HYP
def test_band_for_monotonic_in_confidence(t: tuple[float, float], c1: float, c2: float) -> None:
    """확신도가 높을수록 같은 구간이거나 더 위 구간이다(판정 표 3행 2절,
    `new_person < identity < merge` 순서)."""
    t_new, t_merge = t
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    lo, hi = sorted([c1, c2])
    assert _BAND_RANK[band_for(lo, config)] <= _BAND_RANK[band_for(hi, config)]


@given(t=_threshold_pair(), confidence=_unit_float())
@_HYP
def test_band_for_matches_threshold_table_away_from_boundary(
    t: tuple[float, float], confidence: float
) -> None:
    """경계 `T_merge`·`T_new` 판정이 원칙2 의 구간표와 일치한다(판정 표
    3행 3절) -- `band_for()` 구현(`ge_with_tolerance`)과 독립적인
    오라클로 비교하기 위해, 허용오차(`ER_TOLERANCE`, 1e-9 급)보다 훨씬
    넓은 여유(1e-6)를 두고 경계에서 먼 값만 단언한다(경계 바로 위의
    부동소수 허용오차 동작은 `tests/test_er_confidence.py` 의 전용
    경계 테스트가 이미 고정한다)."""
    t_new, t_merge = t
    margin = 1e-6
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    band = band_for(confidence, config)

    if confidence >= t_merge + margin:
        assert band == "merge"
    elif confidence < t_new - margin:
        assert band == "new_person"
    elif t_new + margin <= confidence < t_merge - margin:
        assert band == "identity"
    # 경계 margin 안쪽 값은 허용오차 로직에 맡기고 여기서는 단언하지 않는다.


@given(
    t=_threshold_pair(),
    llm_failed=st.booleans(),
    has_judgement=st.booleans(),
    s_llm=_unit_float(),
)
@_HYP
def test_decide_no_candidates_always_new_person(
    t: tuple[float, float], llm_failed: bool, has_judgement: bool, s_llm: float
) -> None:
    """통과 후보 0건이면 `judgement`/`llm_failed` 와 무관하게 항상
    `new_person`(결정5, `no_candidates` 최우선)."""
    t_new, t_merge = t
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    judgement = Judgement(matched_person_id=None, s_llm=s_llm, reason="r") if has_judgement else None
    result = decide(judgement=judgement, passed=[], llm_failed=llm_failed, config=config)
    assert result.band == "new_person"


@given(
    t=_threshold_pair(),
    ids=st.lists(st.integers(min_value=1, max_value=10_000), min_size=1, max_size=3, unique=True),
    mode=st.sampled_from(["llm_failed", "no_matched", "out_of_range"]),
)
@_HYP
def test_decide_forced_paths_never_merge(
    t: tuple[float, float], ids: list[int], mode: str
) -> None:
    """원칙1·2: llm 실패·null 판정·범위 밖 id 는 통과 후보가 있어도
    `merge` 로 귀속되지 않는다(`tests/test_er_confidence.py` 의 2000회
    스윕과 같은 불변식을 hypothesis 로도 고정)."""
    t_new, t_merge = t
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    passed = [
        ScoredCandidate(
            person_id=pid, display_name=f"p{pid}", s_emb=1.0, s_rule=1.0, rule_checked=1, rule_passed=1, passed_rules=True
        )
        for pid in ids
    ]

    if mode == "llm_failed":
        result = decide(judgement=None, passed=passed, llm_failed=True, config=config)
    elif mode == "no_matched":
        judgement = Judgement(matched_person_id=None, s_llm=1.0, reason="r")
        result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)
    else:
        out_of_range_id = max(ids) + 1
        judgement = Judgement(matched_person_id=out_of_range_id, s_llm=1.0, reason="r")
        result = decide(judgement=judgement, passed=passed, llm_failed=False, config=config)

    assert result.band != "merge"
    assert result.band in _BAND_RANK


@given(
    t=_threshold_pair(),
    s_emb=_unit_float(),
    s_rule=_unit_float(),
    rule_checked=st.integers(min_value=1, max_value=5),
    s_llm_a=_unit_float(),
    s_llm_b=_unit_float(),
)
@_HYP
def test_decide_normal_path_monotonic_in_s_llm(
    t: tuple[float, float],
    s_emb: float,
    s_rule: float,
    rule_checked: int,
    s_llm_a: float,
    s_llm_b: float,
) -> None:
    """정상 경로(통과 후보 귀속)에서 `s_llm` 이 높을수록 같은 구간이거나
    더 위 구간이다(판정 표 3행 2절, `decide()` 전체 파이프라인 수준)."""
    t_new, t_merge = t
    config = ERConfig(t_new=t_new, t_merge=t_merge)
    candidate = ScoredCandidate(
        person_id=1,
        display_name="p1",
        s_emb=s_emb,
        s_rule=s_rule,
        rule_checked=rule_checked,
        rule_passed=rule_checked,
        passed_rules=True,
    )
    lo, hi = sorted([s_llm_a, s_llm_b])

    result_lo = decide(
        judgement=Judgement(matched_person_id=1, s_llm=lo, reason="r"),
        passed=[candidate],
        llm_failed=False,
        config=config,
    )
    result_hi = decide(
        judgement=Judgement(matched_person_id=1, s_llm=hi, reason="r"),
        passed=[candidate],
        llm_failed=False,
        config=config,
    )
    assert _BAND_RANK[result_lo.band] <= _BAND_RANK[result_hi.band]


# ===========================================================================
# 4. app/push/payload.py::build_push_payload -- 길이·TTL·원문 미노출
# ===========================================================================

#: 감시 문자열(마커)과 인물 이름·일정 제목·제안 텍스트가 **문자 집합
#: 자체로 겹치지 않게** 둔다(우연한 부분 문자열 충돌을 `assume()` 없이
#: 원천 차단) -- 한글 음절(가~힣)과 영문 대문자+숫자는 교집합이 없다.
_MARKER_ALPHABET = string.ascii_uppercase + string.digits
_KOREAN_SYLLABLES = st.characters(min_codepoint=0xAC00, max_codepoint=0xD7A3)


def _korean_text(min_size: int, max_size: int) -> st.SearchStrategy[str]:
    return st.text(alphabet=_KOREAN_SYLLABLES, min_size=min_size, max_size=max_size)


def _marker_text() -> st.SearchStrategy[str]:
    # "충분히 긴 무작위 문자열"(위임 프롬프트) -- 24~40자.
    return st.text(alphabet=_MARKER_ALPHABET, min_size=24, max_size=40)


@given(
    display_name=_korean_text(1, 10),
    schedule_title=_korean_text(1, 15),
    suggestion_text=_korean_text(0, 80),
    marker=_marker_text(),
    delta_seconds=st.integers(min_value=-10_000_000, max_value=200_000_000),
)
@_HYP
def test_build_push_payload_properties(
    display_name: str,
    schedule_title: str,
    suggestion_text: str,
    marker: str,
    delta_seconds: int,
) -> None:
    """본문 길이 ≤ `PUSH_BODY_MAX_CHARS` · ttl ∈ [60, `PUSH_TTL_MAX_SECONDS`]
    · 요약 줄·패턴 문장에 넣은 마커가 결과 어디에도 없다(결정 B·원칙7,
    판정 표 4행). 마커는 한글 전용 필드(`display_name`/`schedule_title`/
    `suggestion_text`)와 문자 집합이 겹치지 않아 우연한 포함이 불가능하다."""
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    scheduled_at = now + timedelta(seconds=delta_seconds)
    schedule = SimpleNamespace(id=1, title=schedule_title, scheduled_at=scheduled_at)
    composed = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": f"{marker} 패턴 문장"}],
        lines=[
            BriefingLine(text=f"{marker} 요약 줄", basis={"fact_keys": [], "event_ids": [1]}),
        ],
        suggestion=Suggestion(text=suggestion_text, basis={"fact_keys": [], "event_ids": [1]})
        if suggestion_text
        else None,
    )

    payload = build_push_payload(schedule, display_name, composed, now)

    assert len(payload["body"]) <= PUSH_BODY_MAX_CHARS
    assert 60 <= payload["ttl"] <= PUSH_TTL_MAX_SECONDS

    dumped = json.dumps(payload, ensure_ascii=False)
    assert marker not in dumped


# ===========================================================================
# 5. app/briefing/compose.py::validate_briefing -- 무예외
# ===========================================================================

#: "알려진" 사실 키·이벤트 id 우주 -- 일부 생성 입력이 이 안에 들고(정상
#: 수락 경로), 일부는 밖에 들어(거부 경로) 더 많은 분기를 실제로 탄다.
_KNOWN_FACT_KEYS = ["likes", "dislikes", "pattern:conflict", "pattern:praise"]
_KNOWN_EVENT_IDS = [101, 102, 103]


def _fuzz_briefing_input() -> BriefingInput:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    used_facts: list[dict[str, Any]] = [
        {
            "key": key,
            "fact_id": i,
            "value": "3회 (2026-01-01)" if key.startswith("pattern:") else "v",
            "confidence": 1.0,
            "updated_at": now.isoformat(),
            "eligible": True,
            "sources": [],
        }
        for i, key in enumerate(_KNOWN_FACT_KEYS)
    ]
    recent_events = [
        {
            "id": eid,
            "person_id": 1,
            "type": "meal",
            "content": "c",
            "occurred_at": now.isoformat(),
            "created_at": now.isoformat(),
        }
        for eid in _KNOWN_EVENT_IDS
    ]
    return BriefingInput(
        schedule_id=1, person_id=1, scheduled_at=now, title="t",
        used_facts=used_facts, recent_events=recent_events,
    )


def _weird_text() -> st.SearchStrategy[str]:
    # "이상한 값" -- 빈 문자열·아주 긴 문자열·일반 텍스트(한글·기호 포함).
    # None 은 여기 넣지 않는다 -- 발견②③으로 이미 별도 고정했다.
    return st.one_of(st.just(""), st.text(min_size=0, max_size=200))


def _fact_key_item() -> st.SearchStrategy[str]:
    return st.one_of(st.sampled_from(_KNOWN_FACT_KEYS), st.text(min_size=0, max_size=12))


def _event_id_item() -> st.SearchStrategy[int]:
    # "거대 정수" 포함 -- 파이썬 int 는 임의 정밀도라 오버플로가 없다.
    return st.one_of(st.sampled_from(_KNOWN_EVENT_IDS), st.integers(min_value=-(10**15), max_value=10**15))


def _basis_strategy() -> st.SearchStrategy[dict[str, Any]]:
    # 원소는 전부 해시 가능(str/int) -- 해시 불가 원소는 발견⑥으로
    # 별도 고정했다(이 전략의 탐색 범위 밖).
    return st.fixed_dictionaries(
        {
            "fact_keys": st.lists(_fact_key_item(), max_size=4),
            "event_ids": st.lists(_event_id_item(), max_size=4),
        }
    )


def _line_strategy() -> st.SearchStrategy[BriefingLine]:
    return st.builds(BriefingLine, text=_weird_text(), basis=_basis_strategy())


def _suggestion_strategy() -> st.SearchStrategy[Suggestion | None]:
    return st.one_of(st.none(), st.builds(Suggestion, text=_weird_text(), basis=_basis_strategy()))


def _pattern_sentence_strategy() -> st.SearchStrategy[dict[str, Any]]:
    # sentence 는 문자열만(비 None·비문자열은 발견⑦로 별도 고정).
    return st.fixed_dictionaries(
        {
            "key": st.one_of(st.sampled_from(_KNOWN_FACT_KEYS), st.just("unknown:key"), st.just("")),
            "sentence": _weird_text(),
        }
    )


def _composed_strategy() -> st.SearchStrategy[ComposedBriefing]:
    return st.builds(
        ComposedBriefing,
        pattern_sentences=st.lists(_pattern_sentence_strategy(), max_size=3),
        lines=st.lists(_line_strategy(), max_size=4),
        suggestion=_suggestion_strategy(),
    )


@given(composed=_composed_strategy())
@_HYP
def test_validate_briefing_never_raises_for_weird_typed_input(composed: ComposedBriefing) -> None:
    """`from_type`/`builds` 로 만든 "이상한(빈 문자열·아주 긴 문자열·
    알려지지 않은 키/거대 id)" 값에도 예외를 던지지 않는다(docstring
    약속, 판정 표 5행) -- 단, `text`/`basis` 가 `None` 이거나 근거 원소가
    해시 불가능하거나 패턴 문장이 비문자열인 입력은 발견②~⑦로 이미 고정된
    별도 반례라 이 넓은 탐색 범위에서는 제외한다(모듈 docstring 설명)."""
    briefing_input = _fuzz_briefing_input()
    result, rejected = validate_briefing(briefing_input, composed)
    assert isinstance(result, ComposedBriefing)
    assert isinstance(rejected, list)


# ---------------------------------------------------------------------------
# 발견②~⑦ 최소 반례(보고용, 미수정) -- 위 넓은 탐색에서 의도적으로 제외한
# 입력들이 실제로 무엇을 던지는지 고정한다.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, raises=TypeError, reason="FIX-024 발견② -- FIX-025 에서 수정 예정")
def test_validate_briefing_raises_when_line_text_is_none_FOUND() -> None:
    """FIX-024 발견②(보고, 미수정) -- `BriefingLine.text=None`(근거는
    알려진 사실 키라 `no_basis`/`unknown_basis` 를 통과)이면 금지 표현
    검사 `bad in line.text` 가 `TypeError: argument of type 'NoneType'
    is not a container or iterable` 로 죽는다. 최소 반례: 아래 그대로.
    제품 코드는 고치지 않는다(FIX-024 위임 범위) -- 사용자 결정 후 별도
    FIX."""
    briefing_input = _fuzz_briefing_input()
    line = BriefingLine(text=None, basis={"fact_keys": ["likes"], "event_ids": []})  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)
    validate_briefing(briefing_input, composed)


@pytest.mark.xfail(strict=True, raises=TypeError, reason="FIX-024 발견③ -- FIX-025 에서 수정 예정")
def test_validate_briefing_raises_when_suggestion_text_is_none_FOUND() -> None:
    """FIX-024 발견③(보고, 미수정) -- `Suggestion.text=None` 이면 줄바꿈
    검사 `"\\n" in suggestion.text` 가 같은 종류의 `TypeError` 로 죽는다
    (발견②와 같은 뿌리, 자리만 다르다). 제품 코드는 고치지 않는다."""
    briefing_input = _fuzz_briefing_input()
    suggestion = Suggestion(text=None, basis={"fact_keys": ["likes"], "event_ids": []})  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[], suggestion=suggestion)
    validate_briefing(briefing_input, composed)


@pytest.mark.xfail(strict=True, raises=AttributeError, reason="FIX-024 발견④ -- FIX-025 에서 수정 예정")
def test_validate_briefing_raises_when_line_basis_is_none_FOUND() -> None:
    """FIX-024 발견④(보고, 미수정) -- `BriefingLine.basis=None` 이면
    `line.basis.get(...)` 에서 `AttributeError: 'NoneType' object has no
    attribute 'get'`. 제품 코드는 고치지 않는다."""
    briefing_input = _fuzz_briefing_input()
    line = BriefingLine(text="안녕", basis=None)  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)
    validate_briefing(briefing_input, composed)


@pytest.mark.xfail(strict=True, raises=AttributeError, reason="FIX-024 발견⑤ -- FIX-025 에서 수정 예정")
def test_validate_briefing_raises_when_suggestion_basis_is_none_FOUND() -> None:
    """FIX-024 발견⑤(보고, 미수정) -- `Suggestion.basis=None` 도 같은
    뿌리의 `AttributeError`. 제품 코드는 고치지 않는다."""
    briefing_input = _fuzz_briefing_input()
    suggestion = Suggestion(text="제안", basis=None)  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[], suggestion=suggestion)
    validate_briefing(briefing_input, composed)


@pytest.mark.xfail(strict=True, raises=TypeError, reason="FIX-024 발견⑥ -- FIX-025 에서 수정 예정")
@pytest.mark.parametrize("field", ["fact_keys", "event_ids"])
def test_validate_briefing_raises_when_fact_keys_element_is_unhashable_FOUND(field: str) -> None:
    """FIX-024 발견⑥(보고, 미수정) -- `basis["fact_keys"]`(또는
    `event_ids`) 원소가 해시 불가능(예: 중첩 리스트)하면 알려진 키/id
    집합 멤버십 검사(`element not in known_set`)가 `TypeError:
    unhashable type`. FIX-021 이 고친 `pattern_sentences[].key` 와 같은
    종류의 문제지만 **줄·제안의 근거 원소**는 아직 `isinstance` 가드가
    없다. 제품 코드는 고치지 않는다."""
    briefing_input = _fuzz_briefing_input()
    basis: dict[str, Any] = {"fact_keys": [], "event_ids": []}
    basis[field] = [["중첩", "리스트"]]
    line = BriefingLine(text="안녕", basis=basis)
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)
    validate_briefing(briefing_input, composed)


@pytest.mark.xfail(strict=True, raises=TypeError, reason="FIX-024 발견⑦ -- FIX-025 에서 수정 예정")
def test_validate_briefing_raises_when_pattern_sentence_is_non_string_non_none_FOUND() -> None:
    """FIX-024 발견⑦(보고, 미수정) -- `pattern_sentences[].sentence` 가
    `None` 이 아니면서 문자열도 아니면(예: 정수) `_extract_mentioned_
    counts` 의 정규식 `findall` 이 `TypeError: expected string or
    bytes-like object` 로 죽는다(`sentence=None` 자체는 `missing_
    pattern` 분기로 안전하다 -- 이 반례와 다르다). 제품 코드는 고치지
    않는다."""
    briefing_input = _fuzz_briefing_input()
    composed = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": 12345}],
        lines=[],
        suggestion=None,
    )
    validate_briefing(briefing_input, composed)


# ===========================================================================
# 가중치 합 검증 경유 -- 전략 자체가 유효한 ERConfig 를 만드는지 교차 확인
# ===========================================================================


@given(weights=_weights_summing_to_one())
@_HYP
def test_weights_strategy_produces_valid_er_config(weights: tuple[float, float, float]) -> None:
    """`_weights_summing_to_one()` 이 실제로 `ERConfig` 가 받아들이는
    가중치를 만드는지(생성 자체가 `InvalidValue` 로 죽지 않는지) 확인한다
    -- 이 파일의 다른 테스트가 전부 이 전략에 의존하므로 전략 자체의
    유효성을 별도로 고정한다."""
    w_llm, w_emb, w_rule = weights
    try:
        ERConfig(w_llm=w_llm, w_emb=w_emb, w_rule=w_rule)
    except InvalidValue as exc:  # pragma: no cover -- 전략이 깨졌다면 여기서 드러난다.
        pytest.fail(f"_weights_summing_to_one() 이 유효하지 않은 가중치를 만들었다: {weights} ({exc})")
