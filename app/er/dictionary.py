"""Refs: P3-er S3.3 결정2 결정10 -- 한국어 호칭 사전 (2단계 규칙 필터의 입력).

`.claude/skills/entity-resolution` "2. 규칙 필터 | 한국어 호칭 사전 + 소속·
위계 제약" 를 위한 표다. 초기 표는 작게 간다(직장 직급 10여 개·가족 호칭
15개 내외·연인/친구/지인 소수·대명사) -- **표 확장은 추측이 아니라 P4
실패 케이스 분석에서만 한다**(01-plan 리스크 "호칭 사전의 범위와 오탐",
원칙8).

## 직급 → 위계 유도 표 (결정10, F-8c6354)

`hierarchy` 는 **사용자 기준** 상/동/하 3값이다(`app/tools/persons.py`
`_HIERARCHY_ORDER`, 재정의하지 않고 값 문자열만 맞춘다). 사용자의 실제
직급을 모르는 채로 직급 호칭을 위계로 바꾸려면 기준선이 필요하므로, 직급
호칭마다 서열 `rank` 를 주고 기준선 `USER_RANK_ANCHOR = 2`(실무 관리자급)
와 비교해 위계를 유도한다 -- `rank > anchor → 상`, `== → 동`, `< → 하`.
`USER_RANK_ANCHOR` 는 이 모듈의 상수로만 두고 환경변수·설정으로 노출하지
않는다(테스트를 통과시키려고 돌릴 수 있는 손잡이를 만들지 않는다, 원칙8).
조정은 P4 실패 케이스 분석 결과로만 한다.

이 값은 **유도값(추정)이며 확정이 아니다**: 호출자가 `hints.hierarchy` 를
주면 그쪽이 우선하고(P5 가 문맥에서 아는 경우), 위계 정보가 전혀 없으면
검사 자체를 건너뛰어 `s_rule` 분모에서 뺀다(결정2 -- 모르면 배제하지 않고
점수도 주지 않는다).

## 모호 항목 ("사장님")

"사장님"처럼 직장(대표)과 지인(가게 주인) 양쪽에 걸리는 항목은 **그룹을
모호로 표시**해(`Entry(group=None, hierarchy=None)`) 어느 쪽으로도
배제하지 않는다(결정2). 모호 항목은 위계도 유도하지 않는다. "대표"는
직장 맥락이 뚜렷하므로 표에 남기고, "사장"/"사장님"만 모호로 뺀다.

## 정규화

`normalize(mention)`: 공백 제거 → 존칭 접미(`님`/`씨`) 제거(최대 1개) →
**성씨 1글자 접두 제거는 나머지가 사전 표제어일 때만**("김팀장" → "팀장",
반면 "이모"는 "모" 가 표제어가 아니므로 그대로 유지된다). 접미 유무는
위계를 바꾸지 않는다(한국어에서 존댓말은 거의 항상 붙으므로 신호가 되지
못한다).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: 결정10 기준선 -- 여기서만 바꾼다(설정·환경변수로 노출하지 않는다).
USER_RANK_ANCHOR = 2

#: 대명사 -- 사전에 없는 지칭이며 `derive_hints` 가 빈 dict 를 돌려주는
#: 근거를 명시적으로 남기기 위한 목록이다(사전에 없으므로 `lookup` 은
#: 이미 `None` 을 주지만, 정보 없음이 "의도"임을 문서화한다).
PRONOUNS = ("그사람", "걔", "그분")


@dataclass(frozen=True)
class Entry:
    """호칭 사전 표제어 하나. `group` 은 `RELATION_TAGS`(가족/연인/친구/
    직장/지인) 값이거나, 모호 항목이면 `None`. `hierarchy` 는 `HIERARCHIES`
    (상/동/하) 값이거나 그룹이 위계와 무관하면 `None`. `rank` 는 직급
    표제어에만 있는 서열(결정10), 그 외는 `None`."""

    group: str | None
    hierarchy: str | None
    rank: int | None = None


def _job_title_entries() -> dict[str, Entry]:
    """결정10 표 그대로. `rank > USER_RANK_ANCHOR → 상`, `== → 동`,
    `< → 하`. "사장"은 여기 넣지 않는다(모호 항목, 아래 `_AMBIGUOUS`)."""

    rank_groups: dict[int, tuple[str, ...]] = {
        0: ("사원", "인턴"),
        1: ("주임", "대리"),
        2: ("과장", "팀장"),
        3: ("차장", "실장"),
        4: ("부장", "본부장"),
        5: ("이사", "상무", "전무"),
        6: ("대표",),
    }
    entries: dict[str, Entry] = {}
    for rank, words in rank_groups.items():
        if rank > USER_RANK_ANCHOR:
            hierarchy = "상"
        elif rank == USER_RANK_ANCHOR:
            hierarchy = "동"
        else:
            hierarchy = "하"
        for word in words:
            entries[word] = Entry(group="직장", hierarchy=hierarchy, rank=rank)
    return entries


_JOB_TITLES: dict[str, Entry] = _job_title_entries()

#: 가족 -- 위계는 상식적 값(부모·조부모·이모/고모/삼촌 상, 형제자매 손위 상·
#: 동생 하). 배우자·본인 항목은 범위 밖(원칙7 -- 사용자-인물 관계만 다룬다).
_FAMILY: dict[str, Entry] = {
    "엄마": Entry("가족", "상"),
    "아빠": Entry("가족", "상"),
    "어머니": Entry("가족", "상"),
    "아버지": Entry("가족", "상"),
    "할머니": Entry("가족", "상"),
    "할아버지": Entry("가족", "상"),
    "이모": Entry("가족", "상"),
    "고모": Entry("가족", "상"),
    "삼촌": Entry("가족", "상"),
    "형": Entry("가족", "상"),
    "누나": Entry("가족", "상"),
    "오빠": Entry("가족", "상"),
    "언니": Entry("가족", "상"),
    "동생": Entry("가족", "하"),
}

_ROMANCE: dict[str, Entry] = {
    "여자친구": Entry("연인", "동"),
    "남자친구": Entry("연인", "동"),
    "자기": Entry("연인", "동"),
}

_FRIEND: dict[str, Entry] = {
    "친구": Entry("친구", "동"),
    "동기": Entry("친구", "동"),
    "베프": Entry("친구", "동"),
}

_ACQUAINTANCE: dict[str, Entry] = {
    "선배": Entry("지인", "상"),
    "후배": Entry("지인", "하"),
    "이웃": Entry("지인", "동"),
}

#: 그룹을 단정할 수 없는 항목(결정2·결정10 "모호 항목") -- 어느 쪽으로도
#: 배제하지 않고 위계도 유도하지 않는다.
_AMBIGUOUS: dict[str, Entry] = {
    "사장": Entry(group=None, hierarchy=None),
}

_DICTIONARY: dict[str, Entry] = {
    **_JOB_TITLES,
    **_FAMILY,
    **_ROMANCE,
    **_FRIEND,
    **_ACQUAINTANCE,
    **_AMBIGUOUS,
}

#: 성씨 1글자 접두 제거 판단에 쓰는 표제어 전체 집합(모호 항목 포함 --
#: "김사장" → "사장" 도 같은 규칙을 적용받는다).
_ALL_HEADWORDS: frozenset[str] = frozenset(_DICTIONARY)

_HONORIFIC_SUFFIXES = ("님", "씨")


def normalize(mention: str | None) -> str:
    """공백 제거 → 존칭 접미 제거(최대 1개) → 성씨 1글자 접두 제거(나머지가
    표제어일 때만). 모듈 docstring "정규화" 절 그대로."""

    if not mention:
        return ""

    stripped = re.sub(r"\s+", "", mention.strip())

    for suffix in _HONORIFIC_SUFFIXES:
        if len(stripped) > len(suffix) and stripped.endswith(suffix):
            stripped = stripped[: -len(suffix)]
            break

    if len(stripped) >= 2:
        remainder = stripped[1:]
        if remainder in _ALL_HEADWORDS:
            stripped = remainder

    return stripped


def lookup(mention: str | None) -> Entry | None:
    """정규화 후 사전에서 찾는다. 없으면(대명사·미등재 고유명사 포함)
    `None` -- "정보 없음"이며 배제 근거가 아니다(결정2)."""

    return _DICTIONARY.get(normalize(mention))


def derive_hints(mention: str | None) -> dict[str, str]:
    """사전 표제어면 `{relation_tag?, hierarchy?}` 를 유도한다. 사전에
    없거나(대명사 "그 사람"/"걔"/"그분" 포함) 모호 항목(`group is None`)
    이면 빈 dict -- "정보 없음"이며, 규칙 필터는 이 빈 dict 를 배제 사유가
    아니라 `s_rule` 분모 제외 근거로만 쓴다(결정2)."""

    entry = lookup(mention)
    if entry is None:
        return {}

    hints: dict[str, str] = {}
    if entry.group is not None:
        hints["relation_tag"] = entry.group
    if entry.hierarchy is not None:
        hints["hierarchy"] = entry.hierarchy
    return hints


def compatible(entry_a: Entry | None, entry_b: Entry | None) -> bool | None:
    """호환 판정 -- 같은 group 이면 `True`, 다르면 `False`, 한쪽이라도
    `None`(정보 없음)이거나 어느 한쪽이 모호 항목(`group is None`)이면
    `None`(평가 불가, 결정2 -- 모르면 배제하지 않는다)."""

    if entry_a is None or entry_b is None:
        return None
    if entry_a.group is None or entry_b.group is None:
        return None
    return entry_a.group == entry_b.group
