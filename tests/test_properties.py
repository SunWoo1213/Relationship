"""Refs: FIX-025 FIX-024 FIX-021 D10 D12 D13 P7-push 원칙1 원칙2 원칙3
원칙7 -- 순수 함수의 "항상 지켜야 할 성질" 을 예시가 아니라 `hypothesis`
로 무작위 탐색해 확인한다. 대상은 전부 **순수 함수**(DB·LLM·네트워크
호출 없음): `app/er/confidence.py::combine`/`band_for`/`decide`,
`app/push/payload.py::build_push_payload`, `app/briefing/compose.py::
validate_briefing`, `app/er/types.py::ERConfig`.

## 이 파일이 하지 않는 것

- 제품 코드(`app/`)를 고치지 않는다(위임 범위, FIX-024/FIX-025). 성질
  탐색 중 실제로 깨지는 입력을 찾으면 **그 입력을 최소 반례로 고정한
  회귀 테스트**만 추가하고, 수정은 사용자 결정을 거쳐 별도 FIX 로
  한다(이 파일의 완료 판정은 `pytest tests/test_properties.py` 가
  **passed** 로 끝나는 것, FIX-024 판정 표 2~5행).

## FIX-024 에서 발견한 위반 -- FIX-025 로 수정 (xfail 8건 -> 일반 테스트)

FIX-024 의 넓은 탐색(`hypothesis`)이 찾은 최소 반례 7종(⑥은 2건)을
FIX-024 는 `xfail(strict=True)` 로만 고정해 두고 제품 코드를 고치지
않았다. **FIX-025 가 아래 7건을 모두 고쳤다** -- 이 파일은 이제 "예외
없음 + 잘못된 설정/항목이 버려지고 이유가 기록된다"를 **일반 테스트**로
단언한다(더 이상 xfail 이 아니다).

1. `app/er/confidence.py::combine` -- `rule_checked=0`(미측정)인데
   `config.w_llm + config.w_emb == 0`(예: `w_llm=0, w_emb=0, w_rule=1`,
   가중치 합 1.0 이라 예전에는 `ERConfig` 생성 자체가 통과했다)이면
   재정규화 분모가 0 이 되어 `ZeroDivisionError` 를 던지던 자리. FIX-025
   는 **`combine()` 호출 이전, `ERConfig` 생성 시점**에 `InvalidValue`
   를 던지도록 막았다(`app/er/types.py::ERConfig.__post_init__`).
   `test_er_config_rejects_weights_that_cannot_renormalize_when_rule_unmeasured`.
2~3. `app/briefing/compose.py::validate_briefing` -- `BriefingLine.text`
   또는 `Suggestion.text` 가 `None`(비문자열)이면 예전에는 금지 표현·
   줄바꿈 검사의 `in` 연산이 `TypeError` 로 죽었다. FIX-025 는 `text`
   타입 가드(`REASON_MALFORMED`)를 앞에 두어 그 줄/제안만 버리고
   나머지는 유지한다.
   `test_validate_briefing_drops_line_with_non_string_text`,
   `test_validate_briefing_drops_suggestion_with_non_string_text`.
4~5. 같은 함수 -- `BriefingLine.basis`/`Suggestion.basis` 가 `None` 이면
   예전에는 `basis.get(...)` 에서 `AttributeError` 로 죽었다. FIX-025
   는 `_is_valid_basis_shape()` 로 `basis` 가 dict 인지부터 확인한다.
   `test_validate_briefing_drops_line_with_none_basis`,
   `test_validate_briefing_drops_suggestion_with_none_basis`.
6. 같은 함수 -- `basis["fact_keys"]`/`basis["event_ids"]` 원소가 해시
   불가능한 값(예: 중첩 리스트)이면 예전에는 `known_fact_keys`/
   `known_event_ids` 집합 멤버십 검사(`in`)에서 `TypeError: unhashable
   type` 로 죽었다. FIX-025 의 `_is_valid_basis_shape()` 는 원소가
   `str`/`int` 가 아니면(리스트·dict 포함) `malformed` 로 거부한다.
   `test_validate_briefing_drops_line_with_unhashable_basis_element`.
7. 같은 함수 -- `pattern_sentences[].sentence` 가 `None` 이 아닌데
   문자열도 아니면(예: 정수) 예전에는 `_extract_mentioned_counts` 의
   정규식 `findall` 이 `TypeError` 로 죽었다(`sentence=None` 자체는
   `missing_pattern` 분기로 원래부터 안전했다). FIX-025 는 타입 가드를
   추가해 그 패턴만 `malformed` 로 거부하고 템플릿 문장으로 채운다.
   `test_validate_briefing_replaces_non_string_pattern_sentence_with_template`.

아래 넓은 탐색 테스트(`test_validate_briefing_never_raises_for_weird_
typed_input`)도 이제 이 7건이 쓰던 입력(`None`·중첩 리스트·비문자열)을
탐색 범위에서 빼지 않는다 -- 고쳤으므로 더 넓혀도 통과해야 한다.
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

from app.briefing.compose import REASON_MALFORMED, validate_briefing
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


#: FIX-025 -- `ERConfig.__post_init__` 가 `w_llm + w_emb` 를 허용 오차
#: 안에서 0 으로 만드는 가중치 조합을 생성 시점에 `InvalidValue` 로
#: 거부하므로, 이 전략이 만드는 가중치는 그 조건을 피해야 `ERConfig(...)`
#: 호출 자체가 깨지지 않는다(1e-9 보다 넉넉한 여유 1e-6 을 둬 경계
#: 부동소수 오차로 인한 가양성/가음성을 피한다).
_RENORMALIZE_MARGIN = 1e-6


@st.composite
def _weights_summing_to_one(draw: st.DrawFn) -> tuple[float, float, float]:
    """`(w_llm, w_emb, w_rule)` -- 합이 1.0(부동소수 표현 오차 이내)인
    세 음이 아닌 가중치. `[0,1]` 위 두 점을 잘라 세 구간 길이로 쓴다.
    `w_llm + w_emb`(= 두 번째 절단점 `b`)가 `ERConfig` 생성을 막을 만큼
    작은 조합은 제외한다(FIX-025, 그 조합은 별도로
    `test_er_config_rejects_weights_that_cannot_renormalize_when_rule_unmeasured`
    가 고정한다)."""
    a, b = sorted(draw(st.lists(_unit_float(), min_size=2, max_size=2)))
    assume(b > _RENORMALIZE_MARGIN)  # w_llm + w_emb == b
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
    이면서 `rule_checked==0` 인 조합(FIX-024 발견①)은 `ERConfig` 생성
    시점에 `InvalidValue` 로 막히므로(FIX-025) `_weights_summing_to_one()`
    전략 자체가 이미 그 조합을 걸러낸다 -- 여기서는 별도 assume 이 필요
    없다."""
    w_llm, w_emb, w_rule = weights
    assume(abs((w_llm + w_emb + w_rule) - 1.0) <= 1e-9)

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
    볼록결합이므로 입력 범위를 벗어날 수 없다. `w_llm+w_emb==0` 조합은
    `_weights_summing_to_one()` 이 이미 걸러낸다(FIX-025)."""
    w_llm, w_emb, w_rule = weights
    assume(abs((w_llm + w_emb + w_rule) - 1.0) <= 1e-9)

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


def test_er_config_rejects_weights_that_cannot_renormalize_when_rule_unmeasured() -> None:
    """FIX-024 발견①을 FIX-025 가 고쳤다 -- `w_llm=w_emb=0·w_rule=1.0`
    (가중치 합 1.0 이라 예전에는 `ERConfig` 생성 자체가 통과했다)은
    `rule_checked=0`(미측정)일 때 `combine()` 의 재정규화 분모
    `w_llm+w_emb` 가 0 이 되어 `ZeroDivisionError` 를 던지던 조합이다.
    FIX-025 는 이 조합 자체를 `ERConfig` **생성 시점**에 `InvalidValue`
    로 막는다 -- `combine()` 은 이제 이 입력으로 호출될 일이 없다."""
    with pytest.raises(InvalidValue):
        ERConfig(w_llm=0.0, w_emb=0.0, w_rule=1.0)


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


def _weird_text() -> st.SearchStrategy[Any]:
    # "이상한 값" -- 빈 문자열·아주 긴 문자열·일반 텍스트(한글·기호 포함)·
    # None·비문자열(정수·리스트). FIX-025 이후 검증기가 이들을 예외 없이
    # `malformed` 로 거부하므로 넓은 탐색에 포함한다(발견②③⑦과 같은
    # 종류의 입력).
    return st.one_of(
        st.none(),
        st.just(""),
        st.text(min_size=0, max_size=200),
        st.integers(),
        st.lists(st.text(max_size=5), max_size=3),
    )


def _fact_key_item() -> st.SearchStrategy[Any]:
    # FIX-025 이후: 해시 불가능한 원소(중첩 리스트)·비문자열·None 도
    # 포함한다(발견⑥과 같은 종류의 입력).
    return st.one_of(
        st.sampled_from(_KNOWN_FACT_KEYS),
        st.text(min_size=0, max_size=12),
        st.none(),
        st.integers(),
        st.lists(st.text(max_size=5), max_size=2),
    )


def _event_id_item() -> st.SearchStrategy[Any]:
    # "거대 정수" 포함(파이썬 int 는 임의 정밀도) + FIX-025 이후 해시
    # 불가능한 원소·비정수·`bool`(FIX-007 관례 -- `bool` 은 `int` 로 치지
    # 않는다)도 포함한다(발견⑥과 같은 종류의 입력).
    return st.one_of(
        st.sampled_from(_KNOWN_EVENT_IDS),
        st.integers(min_value=-(10**15), max_value=10**15),
        st.booleans(),
        st.none(),
        st.text(max_size=5),
        st.lists(st.integers(), max_size=2),
    )


def _basis_strategy() -> st.SearchStrategy[Any]:
    well_formed = st.fixed_dictionaries(
        {
            "fact_keys": st.lists(_fact_key_item(), max_size=4),
            "event_ids": st.lists(_event_id_item(), max_size=4),
        }
    )
    # FIX-025 이후: `basis` 자체가 dict 가 아닌 경우(None·리스트·문자열)도
    # 넓은 탐색에 포함한다(발견④⑤와 같은 종류의 입력).
    return st.one_of(well_formed, st.none(), st.just([]), st.just("not-a-dict"))


def _line_strategy() -> st.SearchStrategy[BriefingLine]:
    return st.builds(BriefingLine, text=_weird_text(), basis=_basis_strategy())


def _suggestion_strategy() -> st.SearchStrategy[Suggestion | None]:
    return st.one_of(st.none(), st.builds(Suggestion, text=_weird_text(), basis=_basis_strategy()))


def _pattern_sentence_strategy() -> st.SearchStrategy[dict[str, Any]]:
    # sentence: FIX-025 이후 비문자열(None 포함)도 넓은 탐색에 포함한다
    # (발견⑦과 같은 종류의 입력).
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
    알려지지 않은 키/거대 id·`None`·중첩 리스트·비문자열)" 값에도 예외를
    던지지 않는다(docstring 약속, 판정 표 5행). FIX-025 가 발견②~⑦을
    고쳐 이제는 이 입력들을 넓은 탐색 범위에서 뺄 필요가 없다 -- 전부
    `malformed` 로 거부되고 나머지 항목은 유지된다."""
    briefing_input = _fuzz_briefing_input()
    result, rejected = validate_briefing(briefing_input, composed)
    assert isinstance(result, ComposedBriefing)
    assert isinstance(rejected, list)


# ---------------------------------------------------------------------------
# 발견②~⑦ 최소 반례 -- FIX-025 가 고친 뒤에도 "예외 없음 + 그 항목이
# 버려지고 rejected 에 이유가 남는다" 가 성립하는지 그대로 고정한다.
# ---------------------------------------------------------------------------


def test_validate_briefing_drops_line_with_non_string_text() -> None:
    """FIX-024 발견②를 FIX-025 가 고쳤다 -- `BriefingLine.text=None`
    (근거는 알려진 사실 키라 `no_basis`/`unknown_basis` 는 통과했을
    값)이면 예전에는 금지 표현 검사 `bad in line.text` 가 `TypeError` 로
    죽었다. 이제는 예외 없이 그 줄만 버리고 `rejected` 에 `malformed`
    사유를 남긴다."""
    briefing_input = _fuzz_briefing_input()
    line = BriefingLine(text=None, basis={"fact_keys": ["likes"], "event_ids": []})  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)

    result, rejected = validate_briefing(briefing_input, composed)

    assert result.lines == []
    assert {"item": {"kind": "line", "text": None, "basis": line.basis}, "reason": REASON_MALFORMED} in rejected


def test_validate_briefing_drops_suggestion_with_non_string_text() -> None:
    """FIX-024 발견③을 FIX-025 가 고쳤다 -- `Suggestion.text=None` 이면
    예전에는 줄바꿈 검사 `"\\n" in suggestion.text` 가 같은 종류의
    `TypeError` 로 죽었다(발견②와 같은 뿌리, 자리만 다르다). 이제는
    제안을 버리고 `malformed` 사유를 남긴다."""
    briefing_input = _fuzz_briefing_input()
    suggestion = Suggestion(text=None, basis={"fact_keys": ["likes"], "event_ids": []})  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[], suggestion=suggestion)

    result, rejected = validate_briefing(briefing_input, composed)

    assert result.suggestion is None
    # `_fuzz_briefing_input()` 은 두 패턴 키(`pattern:conflict`/
    # `pattern:praise`)를 포함하는데 `composed` 가 패턴 문장을 하나도
    # 주지 않아 `missing_pattern` 거부가 함께 섞인다 -- 이 테스트의
    # 관심사가 아니므로 `in` 으로 확인한다.
    assert {
        "item": {"kind": "suggestion", "text": None, "basis": suggestion.basis},
        "reason": REASON_MALFORMED,
    } in rejected


def test_validate_briefing_drops_line_with_none_basis() -> None:
    """FIX-024 발견④를 FIX-025 가 고쳤다 -- `BriefingLine.basis=None`
    이면 예전에는 `line.basis.get(...)` 에서 `AttributeError` 로 죽었다.
    이제는 그 줄을 버리고 `malformed` 사유를 남긴다."""
    briefing_input = _fuzz_briefing_input()
    line = BriefingLine(text="안녕", basis=None)  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)

    result, rejected = validate_briefing(briefing_input, composed)

    assert result.lines == []
    assert {"item": {"kind": "line", "text": "안녕", "basis": None}, "reason": REASON_MALFORMED} in rejected


def test_validate_briefing_drops_suggestion_with_none_basis() -> None:
    """FIX-024 발견⑤를 FIX-025 가 고쳤다 -- `Suggestion.basis=None` 도
    같은 뿌리의 `AttributeError` 였다. 이제는 제안을 버리고 `malformed`
    사유를 남긴다."""
    briefing_input = _fuzz_briefing_input()
    suggestion = Suggestion(text="제안", basis=None)  # type: ignore[arg-type]
    composed = ComposedBriefing(pattern_sentences=[], lines=[], suggestion=suggestion)

    result, rejected = validate_briefing(briefing_input, composed)

    assert result.suggestion is None
    assert {
        "item": {"kind": "suggestion", "text": "제안", "basis": None},
        "reason": REASON_MALFORMED,
    } in rejected


@pytest.mark.parametrize("field", ["fact_keys", "event_ids"])
def test_validate_briefing_drops_line_with_unhashable_basis_element(field: str) -> None:
    """FIX-024 발견⑥을 FIX-025 가 고쳤다 -- `basis["fact_keys"]`(또는
    `event_ids`) 원소가 해시 불가능(예: 중첩 리스트)하면 예전에는 알려진
    키/id 집합 멤버십 검사(`element not in known_set`)가 `TypeError:
    unhashable type` 로 죽었다(FIX-021 이 고친 `pattern_sentences[].key`
    와 같은 종류지만 줄·제안의 근거 원소는 그때 고치지 않았다). 이제는
    `_is_valid_basis_shape()` 가 원소 타입을 먼저 확인해 그 줄을 버리고
    `malformed` 사유를 남긴다."""
    briefing_input = _fuzz_briefing_input()
    basis: dict[str, Any] = {"fact_keys": [], "event_ids": []}
    basis[field] = [["중첩", "리스트"]]
    line = BriefingLine(text="안녕", basis=basis)
    composed = ComposedBriefing(pattern_sentences=[], lines=[line], suggestion=None)

    result, rejected = validate_briefing(briefing_input, composed)

    assert result.lines == []
    assert {"item": {"kind": "line", "text": "안녕", "basis": basis}, "reason": REASON_MALFORMED} in rejected


def test_validate_briefing_replaces_non_string_pattern_sentence_with_template() -> None:
    """FIX-024 발견⑦을 FIX-025 가 고쳤다 -- `pattern_sentences[].sentence`
    가 `None` 이 아니면서 문자열도 아니면(예: 정수) 예전에는
    `_extract_mentioned_counts` 의 정규식 `findall` 이 `TypeError` 로
    죽었다(`sentence=None` 자체는 `missing_pattern` 분기로 원래부터
    안전했다 -- 이 반례와 다르다). 이제는 `malformed` 사유로 거부하고
    규칙 `value` 그대로 템플릿 문장으로 채운다(`missing_pattern` 과 같은
    보강 성격)."""
    briefing_input = _fuzz_briefing_input()
    composed = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": 12345}],
        lines=[],
        suggestion=None,
    )

    result, rejected = validate_briefing(briefing_input, composed)

    # `_fuzz_briefing_input()` 의 `pattern:praise` 는 `composed` 가 문장을
    # 아예 주지 않아 `missing_pattern` 으로 따로 채워진다(이 테스트의
    # 관심사가 아니다) -- `pattern:conflict` 항목만 확인한다.
    assert {"key": "pattern:conflict", "sentence": "3회 (2026-01-01)"} in result.pattern_sentences
    assert {
        "item": {"kind": "pattern", "key": "pattern:conflict", "sentence": 12345},
        "reason": REASON_MALFORMED,
    } in rejected


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
