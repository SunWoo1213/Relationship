"""Refs: P3-er P4b-er-redesign S3.3 결정2 D10 D13 원칙1 원칙4 원칙9 -- 2단계
(규칙 필터). 산식·배제/감점 규약의 권위는 `docs/wiki/specs/S3.3-er-pipeline.md`
·`docs/wiki/decisions/D13-rule-filter-penalty.md` 다(CR-001, 2026-09-22 --
`relation_tag_conflict`·`hierarchy_conflict` 를 배제에서 감점으로 대체).

검사 3종을 평가한다 -- **위계 일치**(hints.hierarchy vs 후보
`ScoredCandidate.hierarchy`), **관계 태그 일치**(hints.relation_tag vs
후보 `relation_tag` 필드), **호칭 사전 호환**(hints.relation_tag vs 후보
`aliases` 를 `app.er.dictionary.lookup` 으로 되짚어 얻은 그룹 -- 사람에게
수동으로 부여된 `relation_tag` 필드와는 다른 신호다: 별칭 자체가 사전
표제어일 때만 평가된다). `s_rule = 통과 수 / 평가 가능한 검사 수`(결정2 --
분모가 0이면 `s_rule = 0.0`, 0.5 같은 중립값을 주지 않는다). 이 분모·분자
계산은 D13 이후에도 그대로다 -- 바뀌는 것은 충돌이 후보를 목록에서
빼느냐(배제) 표시만 다느냐(감점)이다.

**배제는 사전 모순(`dictionary_conflict`)일 때만** 한다(D13). 관계 태그
불일치(`relation_tag_conflict`)·위계 불일치(`hierarchy_conflict`)는 더
이상 배제 사유가 아니다 -- 후보를 목록에서 빼지 않고 `penalized_by` 로
표시한 채 3단계 LLM 에 넘긴다(LLM 이 후보 전체를 비교할 수 있어야 한다,
D13 "이유"). `passed_rules` 의 뜻은 "배제되지 않았다"(=`dictionary_conflict`
가 없다)로 바뀐다 -- 감점된 후보도 `passed_rules=True` 다. `excluded_by`
에는 `dictionary_conflict` 만 등장한다(D13 "코드에서 지켜야 할 것" 1항).
정보가 없어 판단할 수 없는 검사는 여전히 분모에서 빼고 배제·감점 사유로도
쓰지 않는다(결정2).

`penalized_by` 는 `relation_tag_conflict`·`hierarchy_conflict` 충돌을
`_CONFLICT_PRIORITY` 어휘 순서로 정렬한 튜플이다(대표 사유 하나가 아니라
**정렬된 목록** -- `excluded_by` 와 달리 복수 사유를 모두 남긴다, 원칙9
정보 손실 방지, U2 03-log "penalized_by 형태" 결정). **완화 통과
(`relaxed_pass=True`) 후보도 `penalized_by` 를 엄격 평가 그대로 채운다**
(R-4 채택안) -- 인접 위계 완화는 자동 연결 허용 여부를 가르는 별도 신호
(`relaxed_pass`)로만 판별하고, 감점 표시(`penalized_by`) 자체는 지우지
않는다(정보 손실 없음). `dictionary_conflict` 는 `penalized_by` 에
등장하지 않는다 -- 그 후보는 애초에 배제되어 3단계로 가지 않는다.

**엄격 단계(`relaxed=False`)는 위계 불일치를 인접 여부와 무관하게
`penalized_by`/`conflicts` 에 반영**한다. `relaxed=True` 는
`app.tools.persons._is_hierarchy_adjacent` 로 판정한 인접(1칸) 불일치만
통과로 보되, **`rule_passed` 에는 미통과로 계상**하고(완화가 점수를
올려주지 않는다 -- 원칙1) 후보의 `relaxed_pass=True` 로 통과 사실만 따로
남긴다(결정2 "완화 통과의 계상"). 상↔하(2칸) 차이는 완화해도 탈락한다
(여전히 `hierarchy_conflict` 감점이 `conflicts`/`penalized_by` 에 남는다).

`run_rule_stage()` 가 엄격 적용 → (**감점 없는 후보가 하나도 없으면**,
결정 C(i) -- 이전의 "엄격 통과 후보 0" 트리거는 D13 이후 `passed_rules`
가 항상 참에 가까워져 영영 돌지 않으므로 대체됐다) 완화 1회 재평가의
순서를 오케스트레이션한다. 반환하는 `passed` 목록은 이제 "배제되지 않은
후보 전체"(감점 후보 포함)다 -- 3단계에 전달되는 후보 수는 언제나
1단계 후보 수 − `dictionary_conflict` 후보 수와 같다(D13 "코드에서
지켜야 할 것" 2항).

## "재검색"이 아니라 "재평가" (01-plan 리스크 200행)

P2 결정3 에 따라 `search_person` 은 `hints` 로 후보를 배제하지 않으므로,
힌트를 바꿔 다시 불러도 **같은 후보 집합**이 돌아온다. 따라서 여기서
말하는 "완화 재검색 1회"는 **후보를 다시 조회하는 것이 아니라, 이미 가진
같은 후보 집합에 완화된 규칙을 다시 적용하는 것**이다 -- 결과는 재검색과
동일하지만 구현은 순수 재평가다. S3.3 의 "재검색 1회" 문구와 trace 필드
이름(`relaxed_retry`)은 그대로 유지한다.

이 모듈은 **DB·LLM 을 호출하지 않는다**(순수 함수, 인자로 받은
`ScoredCandidate` 리스트만 본다).
"""

from __future__ import annotations

from dataclasses import replace

from app.er import dictionary
from app.er.types import ScoredCandidate
from app.tools.persons import _is_hierarchy_adjacent

#: 어휘 순서는 U3(P3-er) 이 정했고 D13 이후에도 그대로 유지한다(늘리지
#: 않는다) -- `relation_tag_conflict` / `hierarchy_conflict` /
#: `dictionary_conflict`. D13 이전에는 `excluded_by` 대표 사유 하나를
#: 고르는 우선순위였다. D13 이후에는 두 가지 용도로 쓰인다: (1)
#: `excluded_by` -- 이 셋 중 실제로 배제를 일으키는 것은
#: `dictionary_conflict` 뿐이다. (2) `penalized_by` -- 배제되지 않은
#: 충돌(`relation_tag_conflict`·`hierarchy_conflict`)을 이 순서로 정렬한
#: 목록.
_CONFLICT_PRIORITY = ("relation_tag_conflict", "hierarchy_conflict", "dictionary_conflict")

#: `penalized_by` 에는 절대 등장하지 않는 사유 -- 사전 모순은 감점이 아니라
#: 배제다(D13 "코드에서 지켜야 할 것" 1항).
_EXCLUSION_ONLY_CONFLICT = "dictionary_conflict"


def _dictionary_group_for_aliases(aliases: list[str]) -> str | None:
    """후보의 별칭들을 사전에서 되짚어 얻은 그룹. 별칭 중 사전 표제어가
    하나도 없거나(정보 없음), 서로 다른 그룹으로 갈리면(모순 -- 흔치
    않지만 안전하게 "평가 불가"로 처리해 원칙1 의 보수 방향을 따른다)
    `None`."""

    groups: set[str] = set()
    for alias in aliases or ():
        entry = dictionary.lookup(alias)
        if entry is None or entry.group is None:
            continue
        groups.add(entry.group)
    if len(groups) == 1:
        return next(iter(groups))
    return None


def _evaluate(
    candidate: ScoredCandidate,
    hint_relation_tag: str | None,
    hint_hierarchy: str | None,
    *,
    relaxed: bool,
) -> tuple[int, int, set[str], bool, set[str]]:
    """검사 3종을 평가해 `(rule_checked, rule_passed, conflicts, relaxed_pass,
    penalizing_conflicts)` 를 돌려준다. `apply_rules()` 와 `run_rule_stage()`
    의 완화 적격 판정이 같은 로직을 쓰도록 여기 한 곳에 모은다.

    `conflicts` 는 `s_rule` 분자(=`rule_passed`)·`excluded_by`(D13 이후
    `dictionary_conflict` 유무) 판정에 쓰는 원래 집합이다. `penalizing_conflicts`
    는 D13 이 새로 구분한 집합 -- `relation_tag_conflict`·`hierarchy_conflict`
    만 담고, **위계는 `relaxed`·인접 여부와 무관하게 항상 여기 들어간다**
    (R-4 채택안: `penalized_by` 는 엄격 평가 결과를 그대로 담고, 완화 통과
    라는 예외는 `relaxed_pass` 플래그로 별도 판별한다 -- 정보 손실 없음,
    원칙9). `dictionary_conflict` 는 `penalizing_conflicts` 에 넣지 않는다
    -- 그 후보는 배제되어 3단계로 가지 않으므로 감점 표시가 필요 없다."""

    checked = 0
    passed = 0
    conflicts: set[str] = set()
    penalizing_conflicts: set[str] = set()
    relaxed_pass = False

    # 관계 태그 일치: hints.relation_tag vs 후보의 저장된 relation_tag.
    # D13: 불일치는 배제가 아니라 감점(penalizing_conflicts)이다.
    if hint_relation_tag is not None and candidate.relation_tag is not None:
        checked += 1
        if hint_relation_tag == candidate.relation_tag:
            passed += 1
        else:
            conflicts.add("relation_tag_conflict")
            penalizing_conflicts.add("relation_tag_conflict")

    # 위계 일치: hints.hierarchy vs 후보의 저장된 hierarchy.
    # D13: 불일치는 배제가 아니라 감점 -- 완화(relaxed and adjacent) 는
    # 자동 연결 허용 여부(`relaxed_pass`)만 가르고, 감점 표시는 지우지
    # 않는다(penalizing_conflicts 는 relaxed 값과 무관하게 채운다, R-4).
    if hint_hierarchy is not None and candidate.hierarchy is not None:
        checked += 1
        if hint_hierarchy == candidate.hierarchy:
            passed += 1
        else:
            adjacent = _is_hierarchy_adjacent(candidate.hierarchy, hint_hierarchy)
            penalizing_conflicts.add("hierarchy_conflict")
            if relaxed and adjacent:
                relaxed_pass = True  # rule_passed 에는 미계상(결정2).
            else:
                conflicts.add("hierarchy_conflict")

    # 호칭 사전 호환: hints.relation_tag vs 후보 별칭들의 사전 그룹.
    # D13 이후에도 모순은 배제다(종전 규약 그대로, penalizing_conflicts 에는
    # 넣지 않는다).
    dict_group = _dictionary_group_for_aliases(candidate.aliases)
    if hint_relation_tag is not None and dict_group is not None:
        checked += 1
        if dict_group == hint_relation_tag:
            passed += 1
        else:
            conflicts.add("dictionary_conflict")

    return checked, passed, conflicts, relaxed_pass, penalizing_conflicts


def apply_rules(
    candidates: list[ScoredCandidate],
    hints: dict[str, str] | None,
    *,
    relaxed: bool = False,
) -> list[ScoredCandidate]:
    """후보마다 검사 3종을 평가해 `rule_checked`·`rule_passed`·`s_rule`·
    `passed_rules`·`excluded_by`·`relaxed_pass`·`penalized_by` 를 채운 새
    리스트를 돌려준다(입력 리스트·객체는 그대로 둔다 -- 불변 dataclass).

    D13 이후: `excluded_by` 는 `dictionary_conflict` 뿐이고(`_EXCLUSION_ONLY_CONFLICT`),
    `passed_rules` 는 "배제되지 않았다"(`excluded_by is None`)를 뜻한다.
    `penalized_by` 는 `relation_tag_conflict`·`hierarchy_conflict` 를
    `_CONFLICT_PRIORITY` 순서로 정렬한 튜플이다(대표 하나가 아니라 목록 --
    복수 사유를 모두 남긴다, 원칙9)."""

    hints = hints or {}
    hint_relation_tag = hints.get("relation_tag")
    hint_hierarchy = hints.get("hierarchy")

    scored: list[ScoredCandidate] = []
    for candidate in candidates:
        checked, passed, conflicts, relaxed_pass, penalizing_conflicts = _evaluate(
            candidate, hint_relation_tag, hint_hierarchy, relaxed=relaxed
        )
        excluded_by = _EXCLUSION_ONLY_CONFLICT if _EXCLUSION_ONLY_CONFLICT in conflicts else None
        penalized_by = tuple(name for name in _CONFLICT_PRIORITY if name in penalizing_conflicts)
        s_rule = (passed / checked) if checked else 0.0
        scored.append(
            replace(
                candidate,
                rule_checked=checked,
                rule_passed=passed,
                s_rule=s_rule,
                passed_rules=excluded_by is None,
                excluded_by=excluded_by,
                relaxed_pass=relaxed_pass,
                penalized_by=penalized_by,
            )
        )
    return scored


def _hierarchy_only_adjacent_conflict(
    candidate: ScoredCandidate, hint_relation_tag: str | None, hint_hierarchy: str | None
) -> bool:
    """엄격 평가에서 이 후보가 **위계 불일치만으로**, 그리고 그 불일치가
    **인접(1칸)** 일 때만 완화 적격이다(결정2·S3.3, 01-plan 리스크
    "승진 완화 재검색이 오병합을 늘린다" (i)(ii)). 이 적격 판정은 D13
    이후에도 배제 기준(`conflicts`, 사전 모순 포함)을 그대로 쓴다 -- 위계
    불일치 **외에 다른 충돌(관계 태그·사전)이 하나라도 있으면** 적격이
    아니다(완화는 "위계만 문제인" 승진 케이스 전용, 원칙1)."""

    checked, _passed, conflicts, _relaxed_pass, _penalizing_conflicts = _evaluate(
        candidate, hint_relation_tag, hint_hierarchy, relaxed=False
    )
    if conflicts != {"hierarchy_conflict"}:
        return False
    if hint_hierarchy is None or candidate.hierarchy is None:
        return False
    return _is_hierarchy_adjacent(candidate.hierarchy, hint_hierarchy)


def run_rule_stage(
    candidates: list[ScoredCandidate], hints: dict[str, str] | None
) -> tuple[list[ScoredCandidate], list[ScoredCandidate], bool]:
    """엄격 적용 → (**감점 없는 후보가 하나도 없으면**, 위계 불일치만으로
    감점된 인접 후보가 있으면) 완화 1회 재평가. `(passed, all_scored,
    relaxed_retry)` 를 돌려준다.

    `passed` 는 **배제되지 않은 후보 전체**다(D13 -- 감점 후보도 포함,
    "3단계에 전달되는 후보 수 == 1단계 후보 수 − `dictionary_conflict`
    후보 수"). `all_scored` 는 배제된 후보까지 포함한 전체(원칙9 -- 배제도
    trace 에 남긴다). `relaxed_retry` 는 완화 재평가를 **시도했는지**
    (성공 여부와 무관, S3.3 "재검색 여부를 trace 에 남긴다").

    완화 재평가 트리거(결정 C(i), D13 파급): D13 이전에는 "엄격 통과 후보
    0"(=`passed_rules` 가 전부 거짓)이었다. D13 이후 `passed_rules` 는
    "배제되지 않았다"만 뜻하므로 관계 태그·위계 감점 후보도 참이 되어
    이 조건이 영영 거짓이 되지 않는다(완화가 돌지 않는다, 02-plan-verify
    사실 주장 (b)). 그래서 트리거를 **"감점 없는(=`penalized_by` 가 빈)
    후보가 하나도 없다"**로 바꾼다 -- 배제되지 않은 후보 중 하나라도
    완전히 깨끗하면(관계 태그·위계 모두 일치하거나 검사할 정보가 없으면)
    완화를 시도하지 않는다.

    완화는 최대 1회만 시도한다(재귀·반복 없음)."""

    hints = hints or {}
    hint_relation_tag = hints.get("relation_tag")
    hint_hierarchy = hints.get("hierarchy")

    strict_scored = apply_rules(candidates, hints, relaxed=False)
    strict_passed = [c for c in strict_scored if c.passed_rules]
    unpenalized = [c for c in strict_passed if not c.penalized_by]
    if unpenalized:
        return strict_passed, strict_scored, False

    eligible = any(
        _hierarchy_only_adjacent_conflict(c, hint_relation_tag, hint_hierarchy)
        for c in candidates
    )
    if not eligible:
        return strict_passed, strict_scored, False

    relaxed_scored = apply_rules(candidates, hints, relaxed=True)
    relaxed_passed = [c for c in relaxed_scored if c.passed_rules]
    return relaxed_passed, relaxed_scored, True
