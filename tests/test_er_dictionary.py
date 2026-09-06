"""Refs: P3-er U3 S3.3 결정2 결정10 -- 호칭 사전(`app/er/dictionary.py`)
단위 테스트. DB·네트워크 없음(순수 함수)."""

from __future__ import annotations

import pytest

from app.er import dictionary


# ---------------------------------------------------------------------------
# 결정10 직급 → 위계 유도 표
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mention", "expected_hierarchy"),
    [
        ("부장님", "상"),
        ("김팀장", "동"),
        ("과장", "동"),
        ("사원", "하"),
        ("대리", "하"),
        ("이사", "상"),
    ],
)
def test_job_title_hierarchy_table(mention: str, expected_hierarchy: str) -> None:
    hints = dictionary.derive_hints(mention)
    assert hints.get("relation_tag") == "직장"
    assert hints.get("hierarchy") == expected_hierarchy


def test_job_title_full_rank_table_entries() -> None:
    # 결정10 표 전체가 직장·rank>anchor(2) 규칙대로 유도되는지.
    expected = {
        "사원": "하",
        "인턴": "하",
        "주임": "하",
        "대리": "하",
        "과장": "동",
        "팀장": "동",
        "차장": "상",
        "실장": "상",
        "부장": "상",
        "본부장": "상",
        "이사": "상",
        "상무": "상",
        "전무": "상",
        "대표": "상",
    }
    for word, hierarchy in expected.items():
        entry = dictionary.lookup(word)
        assert entry is not None, word
        assert entry.group == "직장"
        assert entry.hierarchy == hierarchy


def test_ambiguous_title_has_no_group_or_hierarchy() -> None:
    entry = dictionary.lookup("사장")
    assert entry is not None
    assert entry.group is None
    assert entry.hierarchy is None
    # 모호 항목은 hints 를 유도하지 않는다(결정2·결정10).
    assert dictionary.derive_hints("사장님") == {}


# ---------------------------------------------------------------------------
# 정규화
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("김팀장님", "팀장"),
        ("박대리씨", "대리"),
        ("부장님", "부장"),
        ("팀장", "팀장"),
    ],
)
def test_normalize_strips_honorific_and_surname_prefix(raw: str, expected: str) -> None:
    assert dictionary.normalize(raw) == expected


def test_normalize_keeps_family_word_that_looks_like_prefixed_form() -> None:
    # "이모"의 나머지 "모" 는 표제어가 아니므로 접두 제거를 하지 않는다
    # (성씨 1글자 접두 제거는 나머지가 사전 표제어일 때만 -- U3 위임 반례).
    assert dictionary.normalize("이모") == "이모"
    entry = dictionary.lookup("이모")
    assert entry is not None
    assert entry.group == "가족"


def test_normalize_empty_and_whitespace() -> None:
    assert dictionary.normalize("") == ""
    assert dictionary.normalize(None) == ""
    assert dictionary.normalize("  김 팀 장  ") == dictionary.normalize("김팀장")


# ---------------------------------------------------------------------------
# 대명사·미등재 → 정보 없음
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mention", ["그 사람", "걔", "그분", "김민수"])
def test_pronouns_and_unregistered_names_have_no_hints(mention: str) -> None:
    assert dictionary.derive_hints(mention) == {}
    assert dictionary.lookup(mention) is None


# ---------------------------------------------------------------------------
# 가족·연인·친구·지인 대표 항목
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mention", "group", "hierarchy"),
    [
        ("엄마", "가족", "상"),
        ("아빠", "가족", "상"),
        ("이모", "가족", "상"),
        ("동생", "가족", "하"),
        ("여자친구", "연인", "동"),
        ("남자친구", "연인", "동"),
        ("친구", "친구", "동"),
        ("선배", "지인", "상"),
        ("후배", "지인", "하"),
        ("이웃", "지인", "동"),
    ],
)
def test_relationship_group_entries(mention: str, group: str, hierarchy: str) -> None:
    hints = dictionary.derive_hints(mention)
    assert hints == {"relation_tag": group, "hierarchy": hierarchy}


# ---------------------------------------------------------------------------
# compatible() 세 값
# ---------------------------------------------------------------------------


def test_compatible_true_for_same_group() -> None:
    a = dictionary.lookup("팀장")
    b = dictionary.lookup("부장")
    assert dictionary.compatible(a, b) is True


def test_compatible_false_for_different_group() -> None:
    a = dictionary.lookup("팀장")
    b = dictionary.lookup("이모")
    assert dictionary.compatible(a, b) is False


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (None, dictionary.Entry("직장", "동")),
        (dictionary.Entry("직장", "동"), None),
        (None, None),
        (dictionary.Entry(None, None), dictionary.Entry("직장", "동")),
    ],
)
def test_compatible_none_when_info_unavailable(a, b) -> None:
    assert dictionary.compatible(a, b) is None
