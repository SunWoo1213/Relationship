"""Refs: P3-er S3.3 결정2 D10 원칙1 원칙4 -- 2단계(규칙 필터).

검사 3종을 평가한다 -- **위계 일치**(hints.hierarchy vs 후보
`ScoredCandidate.hierarchy`), **관계 태그 일치**(hints.relation_tag vs
후보 `relation_tag` 필드), **호칭 사전 호환**(hints.relation_tag vs 후보
`aliases` 를 `app.er.dictionary.lookup` 으로 되짚어 얻은 그룹 -- 사람에게
수동으로 부여된 `relation_tag` 필드와는 다른 신호다: 별칭 자체가 사전
표제어일 때만 평가된다). `s_rule = 통과 수 / 평가 가능한 검사 수`(결정2 --
분모가 0이면 `s_rule = 0.0`, 0.5 같은 중립값을 주지 않는다).

**배제는 모순일 때만** 한다 -- 정보가 없어 판단할 수 없는 검사는 분모에서
빼고 배제 사유로도 쓰지 않는다(미검출을 늘리지 않으면서 오병합만 막는다,
결정2). `excluded_by` 는 충돌이 여러 개일 때 `relation_tag_conflict` >
`hierarchy_conflict` > `dictionary_conflict` 순으로 대표 사유 하나만
남긴다 -- 모든 개별 충돌은 배제 판정 자체(=`passed_rules=False`)에
반영되므로 순위는 표시용이다. 배제된 후보도 `candidates[]` 에
`passed_rules=false`·`excluded_by` 와 함께 그대로 남는다(원칙9 -- 배제도
근거다).

**엄격 단계(`relaxed=False`)는 위계 불일치를 인접 여부와 무관하게
탈락**시킨다. `relaxed=True` 는 `app.tools.persons._is_hierarchy_adjacent`
로 판정한 인접(1칸) 불일치만 통과로 보되, **`rule_passed` 에는 미통과로
계상**하고(완화가 점수를 올려주지 않는다 -- 원칙1) 후보의
`relaxed_pass=True` 로 통과 사실만 따로 남긴다(결정2 "완화 통과의
계상"). 상↔하(2칸) 차이는 완화해도 탈락한다.

`run_rule_stage()` 가 엄격 적용 → (통과 0 이고 위계 불일치**만**으로 탈락한
인접 후보가 있으면) 완화 1회 재평가의 순서를 오케스트레이션한다.

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

#: `excluded_by` 대표 사유 우선순위 (U3 위임 프롬프트 항목3의 어휘 순서
#: 그대로 -- `relation_tag_conflict` / `hierarchy_conflict` /
#: `dictionary_conflict`).
_CONFLICT_PRIORITY = ("relation_tag_conflict", "hierarchy_conflict", "dictionary_conflict")


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
) -> tuple[int, int, set[str], bool]:
    """검사 3종을 평가해 `(rule_checked, rule_passed, conflicts, relaxed_pass)`
    를 돌려준다. `apply_rules()` 와 `run_rule_stage()` 의 완화 적격 판정이
    같은 로직을 쓰도록 여기 한 곳에 모은다."""

    checked = 0
    passed = 0
    conflicts: set[str] = set()
    relaxed_pass = False

    # 관계 태그 일치: hints.relation_tag vs 후보의 저장된 relation_tag.
    if hint_relation_tag is not None and candidate.relation_tag is not None:
        checked += 1
        if hint_relation_tag == candidate.relation_tag:
            passed += 1
        else:
            conflicts.add("relation_tag_conflict")

    # 위계 일치: hints.hierarchy vs 후보의 저장된 hierarchy.
    if hint_hierarchy is not None and candidate.hierarchy is not None:
        checked += 1
        if hint_hierarchy == candidate.hierarchy:
            passed += 1
        else:
            adjacent = _is_hierarchy_adjacent(candidate.hierarchy, hint_hierarchy)
            if relaxed and adjacent:
                relaxed_pass = True  # rule_passed 에는 미계상(결정2).
            else:
                conflicts.add("hierarchy_conflict")

    # 호칭 사전 호환: hints.relation_tag vs 후보 별칭들의 사전 그룹.
    dict_group = _dictionary_group_for_aliases(candidate.aliases)
    if hint_relation_tag is not None and dict_group is not None:
        checked += 1
        if dict_group == hint_relation_tag:
            passed += 1
        else:
            conflicts.add("dictionary_conflict")

    return checked, passed, conflicts, relaxed_pass


def apply_rules(
    candidates: list[ScoredCandidate],
    hints: dict[str, str] | None,
    *,
    relaxed: bool = False,
) -> list[ScoredCandidate]:
    """후보마다 검사 3종을 평가해 `rule_checked`·`rule_passed`·`s_rule`·
    `passed_rules`·`excluded_by`·`relaxed_pass` 를 채운 새 리스트를
    돌려준다(입력 리스트·객체는 그대로 둔다 -- 불변 dataclass)."""

    hints = hints or {}
    hint_relation_tag = hints.get("relation_tag")
    hint_hierarchy = hints.get("hierarchy")

    scored: list[ScoredCandidate] = []
    for candidate in candidates:
        checked, passed, conflicts, relaxed_pass = _evaluate(
            candidate, hint_relation_tag, hint_hierarchy, relaxed=relaxed
        )
        excluded_by = next((name for name in _CONFLICT_PRIORITY if name in conflicts), None)
        s_rule = (passed / checked) if checked else 0.0
        scored.append(
            replace(
                candidate,
                rule_checked=checked,
                rule_passed=passed,
                s_rule=s_rule,
                passed_rules=not conflicts,
                excluded_by=excluded_by,
                relaxed_pass=relaxed_pass,
            )
        )
    return scored


def _hierarchy_only_adjacent_conflict(
    candidate: ScoredCandidate, hint_relation_tag: str | None, hint_hierarchy: str | None
) -> bool:
    """엄격 평가에서 이 후보가 **위계 불일치만으로**, 그리고 그 불일치가
    **인접(1칸)** 일 때만 완화 적격이다(결정2·S3.3, 01-plan 리스크
    "승진 완화 재검색이 오병합을 늘린다" (i)(ii))."""

    checked, _passed, conflicts, _relaxed_pass = _evaluate(
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
    """엄격 적용 → (통과 0 이고 위계 불일치만으로 탈락한 인접 후보가 있으면)
    완화 1회 재평가. `(passed, all_scored, relaxed_retry)` 를 돌려준다 --
    `passed` 는 통과 후보만, `all_scored` 는 배제된 후보를 포함한 전체
    (원칙9 -- 배제도 trace 에 남긴다), `relaxed_retry` 는 완화 재평가를
    **시도했는지**(성공 여부와 무관, S3.3 "재검색 여부를 trace 에 남긴다").
    완화는 최대 1회만 시도한다(재귀·반복 없음)."""

    hints = hints or {}
    hint_relation_tag = hints.get("relation_tag")
    hint_hierarchy = hints.get("hierarchy")

    strict_scored = apply_rules(candidates, hints, relaxed=False)
    strict_passed = [c for c in strict_scored if c.passed_rules]
    if strict_passed:
        return strict_passed, strict_scored, False

    eligible = any(
        _hierarchy_only_adjacent_conflict(c, hint_relation_tag, hint_hierarchy)
        for c in candidates
    )
    if not eligible:
        return [], strict_scored, False

    relaxed_scored = apply_rules(candidates, hints, relaxed=True)
    relaxed_passed = [c for c in relaxed_scored if c.passed_rules]
    return relaxed_passed, relaxed_scored, True
