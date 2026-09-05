"""Refs: P2-tools R10 S3.2 -- scripts/tools_check.py 회귀(DB 불필요).

`scripts/tools_check.py` 의 파서·대조 함수를 그대로 import 해서 쓴다
(파서 이중 정의 금지, 01-plan 40행 -- `scripts/schema_check.py` 와 같은
방식). 항상 통과하는 테스트를 두지 않기 위해 (c)/(d) 는 일부러 어긋난
입력을 주고 FAIL/예외를 기대한다.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import tools_check as tc  # noqa: E402

import app.tools as tools_module  # noqa: E402

REAL_CLAUDE_MD = Path(__file__).resolve().parent.parent / "CLAUDE.md"

#: 실제 CLAUDE.md 절 그대로 -- 가짜 파일 생성용 베이스 텍스트.
_REAL_SECTION_TEXT = REAL_CLAUDE_MD.read_text(encoding="utf-8")


def _wrap_as_claude_md(section_lines: list[str]) -> str:
    """`## 툴 7종 ...` 절 + 다음 `## ` 제목을 갖춘 최소 CLAUDE.md 본문을 만든다.

    `extract_section` 이 "다음 '## ' 제목 전까지"만 읽으므로, 뒤에 다른
    절이 있는 실제 문서 구조를 재현해 경계 로직도 함께 검증한다.
    """
    return (
        "# 가짜 CLAUDE.md\n\n"
        + tc.SECTION_HEADING
        + " (제품 속 에이전트가 호출) — 시그니처 v2\n\n"
        + "\n".join(section_lines)
        + "\n\n## 데이터 모델\n\n(다음 절 -- 여기는 파싱되지 않아야 한다)\n"
    )


# 실제 7개 행(참일 때 기준선) -- CLAUDE.md 원문에서 그대로 파싱해 재사용한다.
_REAL_ROWS = tc.parse_tool_table(_REAL_SECTION_TEXT)


def _real_row_lines() -> list[str]:
    return [f"| `{name}` | `{sig}` |" for name, sig in _REAL_ROWS]


# ---------------------------------------------------------------------------
# (a) 7툴 각각 parametrize -- 대조 함수가 ok
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tool_name", tc.TOOL_NAMES)
def test_each_tool_matches_claude_md_signature(tool_name: str):
    assert len(_REAL_ROWS) == 7
    expected_by_name = {name: tc.parse_params(sig_str) for name, sig_str in _REAL_ROWS}
    assert tool_name in expected_by_name

    func = getattr(tools_module, tool_name)
    sig = inspect.signature(func)
    matched, reason = tc.compare_signature(expected_by_name[tool_name], sig)
    assert matched, reason


# ---------------------------------------------------------------------------
# (b) 파서가 CLAUDE.md 실제 파일에서 정확히 7행을 뽑는다
# ---------------------------------------------------------------------------


def test_parser_extracts_exactly_7_rows_from_real_claude_md():
    rows = tc.parse_tool_table(REAL_CLAUDE_MD.read_text(encoding="utf-8"))
    assert len(rows) == 7
    assert [name for name, _ in rows] == list(tc.TOOL_NAMES)


def test_main_on_real_claude_md_reports_7_of_7_ok(capsys):
    rc = tc.main(["--claude-md", str(REAL_CLAUDE_MD)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "RESULT: 7/7 ok" in out
    for tool_name in tc.TOOL_NAMES:
        assert f"[ok] {tool_name}:" in out


# ---------------------------------------------------------------------------
# (c) 부정 케이스 -- 가짜 CLAUDE.md
# ---------------------------------------------------------------------------


def test_negative_parameter_name_changed_fails(tmp_path):
    """search_person 의 `query` 를 `search_query` 로 바꾸면 이름 불일치로 FAIL."""
    lines = _real_row_lines()
    assert lines[0].startswith("| `search_person` |")
    lines[0] = lines[0].replace("query: str", "search_query: str")

    fake = tmp_path / "CLAUDE.md"
    fake.write_text(_wrap_as_claude_md(lines), encoding="utf-8")

    rc = tc.main(["--claude-md", str(fake)])
    assert rc == 1


def test_negative_optionality_marker_removed_fails(tmp_path):
    """search_person 의 `hints?` 에서 `?` 를 제거하면(필수로 바뀜) 옵션 불일치로 FAIL."""
    lines = _real_row_lines()
    assert lines[0].startswith("| `search_person` |")
    lines[0] = lines[0].replace("hints?:", "hints:")

    fake = tmp_path / "CLAUDE.md"
    fake.write_text(_wrap_as_claude_md(lines), encoding="utf-8")

    rc = tc.main(["--claude-md", str(fake)])
    assert rc == 1


def test_negative_only_6_rows_fails(tmp_path):
    """행이 6개뿐이면(1개 누락) 통과가 아니라 실패다 -- 01-plan 리스크 대응."""
    lines = _real_row_lines()[:6]

    fake = tmp_path / "CLAUDE.md"
    fake.write_text(_wrap_as_claude_md(lines), encoding="utf-8")

    rc = tc.main(["--claude-md", str(fake)])
    assert rc == 1


def test_negative_missing_claude_md_section_fails(tmp_path):
    """"## 툴 7종" 절 자체가 없으면 0행 → 실패."""
    fake = tmp_path / "CLAUDE.md"
    fake.write_text("# 가짜\n\n## 다른 절\n\n아무 표도 없음\n", encoding="utf-8")

    rc = tc.main(["--claude-md", str(fake)])
    assert rc == 1


def test_negative_only_6_rows_prints_row_count_failure(tmp_path, capsys):
    lines = _real_row_lines()[:6]
    fake = tmp_path / "CLAUDE.md"
    fake.write_text(_wrap_as_claude_md(lines), encoding="utf-8")

    tc.main(["--claude-md", str(fake)])
    out = capsys.readouterr().out
    assert "[FAIL] CLAUDE.md 툴 표 7행을 찾지 못함" in out


# ---------------------------------------------------------------------------
# (d) 첫 매개변수가 ctx 가 아닌 가짜 함수 → FAIL
# ---------------------------------------------------------------------------


def test_negative_first_param_not_ctx_fails():
    def fake_search_person(session, query, hints=None):  # noqa: ANN001 -- 의도된 위반
        raise NotImplementedError

    expected_params = tc.parse_params(dict(_REAL_ROWS)["search_person"])
    matched, reason = tc.compare_signature(
        expected_params, inspect.signature(fake_search_person)
    )
    assert not matched
    assert "ctx" in reason
