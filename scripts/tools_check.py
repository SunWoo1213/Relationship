"""Refs: P2-tools R10 S3.2 -- CLAUDE.md "툴 7종" 표 ↔ 실제 `inspect.signature` 대조.

사용:
    python scripts/tools_check.py
    python scripts/tools_check.py --claude-md path/to/other.md   # 테스트용(가짜 표 주입)

동작:
  1. CLAUDE.md 의 "## 툴 7종 (제품 속 에이전트가 호출) — 시그니처 v2" 절
     (다음 "## " 제목 전까지)에서 마크다운 표 행 (`| 이름(백틱) | 시그니처(백틱) |`)
     을 순서대로 파싱한다. **7행을 찾지 못하면 통과가 아니라 실패**다
     (rc 1) -- 01-plan 리스크 "표 서식이 바뀌면 검사가 깨진다"의 대응.
  2. 각 시그니처 문자열의 첫 `(...)` 안 매개변수 목록을 이름·옵션 여부로만
     분해한다 -- 타입 주석(`name: type`)은 버리고 이름만 취하고, `name?`
     은 옵션(기본값 있음)으로 표시하며, `{...}`/`[...]` 중첩은 top-level
     콤마 분리에서만 무시한다(값 자체는 보지 않는다).
  3. `app.tools.TOOL_NAMES` 순서로 `app.tools` 에서 실제 함수를 가져와
     `inspect.signature` 와 대조한다 -- 첫 매개변수가 정확히 `ctx` 인지,
     그 뒤 매개변수의 **이름·순서·옵션 여부**가 표와 같은지(01-plan 결정2).
  4. 툴마다 한 줄 출력. `[ok] search_person: CLAUDE.md (query, hints?) ==
     actual (ctx, query, hints=None)` 형태로 기대값(CLAUDE.md)과 실제
     시그니처를 **`ctx` 를 포함한 원형 그대로** 함께 찍는다(F-107a50 --
     ctx 편차가 기록에 남아야 한다). 어긋나면
     `[FAIL] <툴>: expected <...> actual <...>`.
  5. 마지막 줄 `RESULT: n/7 ok`. 하나라도 FAIL 이면 rc 1, 전부 ok 면 rc 0.

DB 접속·환경변수·비밀 없음. `app.tools` 를 import 하는 것 이상의 부작용이
없다(모듈 임포트만으로 DB 접속을 만들지 않는다 -- U8 리스크 "엔진 생성 지연"
과 같은 전제).
"""

from __future__ import annotations

import argparse
import inspect
import re
import sys
from pathlib import Path

# 스크립트로 직접 실행될 때(`python scripts/tools_check.py`) `app` 패키지를
# 찾을 수 있도록 저장소 루트를 sys.path 에 넣는다(scripts/db_check.py·
# scripts/schema_check.py 와 동일한 방식).
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from app.tools import TOOL_NAMES  # noqa: E402

DEFAULT_CLAUDE_MD = _REPO_ROOT / "CLAUDE.md"

#: CLAUDE.md 의 절 제목. 이 제목부터 다음 "## " 제목 전까지만 표를 읽는다
#: (01-plan 리스크 "표 서식이 바뀌면 검사가 깨진다"의 경계).
SECTION_HEADING = "## 툴 7종"

#: 표 데이터 행: `| \`이름\` | \`시그니처 전체\` |` (헤더·구분선 행은 이 패턴에
#: 걸리지 않는다 -- 백틱으로 감싼 셀 두 개를 요구하기 때문).
_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*$", re.MULTILINE)


class ToolTableError(Exception):
    """CLAUDE.md 에서 툴 7종 표를 기대한 형태로 찾지 못했을 때."""


def extract_section(text: str, heading: str) -> str:
    """`heading` 으로 시작하는 절 본문을 다음 "## " 제목 전까지 잘라 돌려준다.

    `heading` 자체를 찾지 못하면 빈 문자열을 돌려준다(호출자가 행 수 0 으로
    처리해 FAIL 을 낸다).
    """
    start = text.find(heading)
    if start == -1:
        return ""
    rest = text[start + len(heading) :]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def parse_tool_table(text: str, heading: str = SECTION_HEADING) -> list[tuple[str, str]]:
    """`(툴 이름, 시그니처 문자열)` 목록을 표 순서 그대로 돌려준다.

    시그니처 문자열은 백틱 안 전체(예: `"(query: str, hints?: {...}) →
    Candidate[]"`) -- 매개변수 파싱은 `parse_params` 가 별도로 한다.
    """
    section = extract_section(text, heading)
    return _ROW_RE.findall(section)


def _split_top_level(params_str: str) -> list[str]:
    """`{...}`/`[...]`/`(...)` 중첩 안의 콤마는 무시하고 top-level 콤마로만
    나눈다."""
    tokens: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in params_str:
        if ch in "{[(":
            depth += 1
            current.append(ch)
        elif ch in "}])":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            tokens.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def parse_params(sig_str: str) -> list[tuple[str, bool]]:
    """시그니처 문자열의 첫 `(...)` 안 매개변수를 `(이름, 옵션 여부)` 목록으로.

    파싱 규칙(위임 프롬프트 그대로): 백틱 안 첫 괄호의 매개변수 목록만 본다,
    `name?` 는 옵션(기본값 있음), `name: type` 은 이름만 취함, `{...}` 중첩은
    (top-level 분리에서만) 무시한다. 반환형(`→ ...`)은 첫 `)` 뒤에 있으므로
    자동으로 버려진다.
    """
    start = sig_str.find("(")
    if start == -1:
        return []
    depth = 0
    end = -1
    for i in range(start, len(sig_str)):
        if sig_str[i] == "(":
            depth += 1
        elif sig_str[i] == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return []
    inner = sig_str[start + 1 : end]

    params: list[tuple[str, bool]] = []
    for token in _split_top_level(inner):
        token = token.strip()
        if not token:
            continue
        name_part = token.split(":", 1)[0].strip()
        optional = name_part.endswith("?")
        name = name_part.rstrip("?").strip()
        params.append((name, optional))
    return params


def format_expected(params: list[tuple[str, bool]]) -> str:
    return "(" + ", ".join(f"{name}?" if opt else name for name, opt in params) + ")"


def format_actual(sig: inspect.Signature) -> str:
    parts = []
    for name, param in sig.parameters.items():
        if param.default is inspect.Parameter.empty:
            parts.append(name)
        else:
            parts.append(f"{name}={param.default!r}")
    return "(" + ", ".join(parts) + ")"


def compare_signature(
    expected_params: list[tuple[str, bool]], sig: inspect.Signature
) -> tuple[bool, str]:
    """`sig`(실제 함수 시그니처, `ctx` 포함)를 `expected_params`(ctx 제외)와
    대조한다. `(일치 여부, 불일치 사유)` 를 돌려준다 -- 일치하면 사유는 빈 문자열.
    """
    actual_names = list(sig.parameters.keys())
    if not actual_names:
        return False, "actual signature has no parameters (expected first param 'ctx')"
    if actual_names[0] != "ctx":
        return False, f"first parameter is '{actual_names[0]}', expected 'ctx'"

    rest = actual_names[1:]
    expected_names = [name for name, _ in expected_params]
    if rest != expected_names:
        return False, f"parameter names/order differ: actual={rest} expected={expected_names}"

    for name, expected_optional in expected_params:
        param = sig.parameters[name]
        actual_optional = param.default is not inspect.Parameter.empty
        if actual_optional != expected_optional:
            return False, (
                f"'{name}' optionality differs: CLAUDE.md optional={expected_optional} "
                f"actual optional={actual_optional}"
            )

    return True, ""


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLAUDE.md 툴 7종 표 ↔ app.tools 실제 시그니처 대조"
    )
    parser.add_argument(
        "--claude-md",
        type=Path,
        default=DEFAULT_CLAUDE_MD,
        help="CLAUDE.md 경로 (테스트에서 가짜 표 주입용, 기본: 저장소 루트 CLAUDE.md)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        text = args.claude_md.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[FAIL] CLAUDE.md 를 읽을 수 없음: {args.claude_md} ({exc})")
        return 1

    rows = parse_tool_table(text)
    if len(rows) != 7:
        print(
            f"[FAIL] CLAUDE.md 툴 표 7행을 찾지 못함 (실제 {len(rows)}행, "
            f"섹션='{SECTION_HEADING}', 파일={args.claude_md})"
        )
        return 1

    expected_by_name = {name: parse_params(sig_str) for name, sig_str in rows}

    import app.tools as tools_module

    tool_functions: dict[str, object] = {
        tool_name: getattr(tools_module, tool_name) for tool_name in TOOL_NAMES
    }

    ok_count = 0
    for tool_name in TOOL_NAMES:
        if tool_name not in expected_by_name:
            print(f"[FAIL] {tool_name}: CLAUDE.md 표에 이 이름의 행이 없음")
            continue

        expected_params = expected_by_name[tool_name]
        func = tool_functions.get(tool_name)
        if func is None:
            print(f"[FAIL] {tool_name}: app.tools 에 이 이름의 함수가 없음")
            continue

        sig = inspect.signature(func)
        matched, reason = compare_signature(expected_params, sig)
        expected_str = format_expected(expected_params)
        actual_str = format_actual(sig)
        if matched:
            ok_count += 1
            print(f"[ok] {tool_name}: CLAUDE.md {expected_str} == actual {actual_str}")
        else:
            print(
                f"[FAIL] {tool_name}: expected {expected_str} actual {actual_str} ({reason})"
            )

    print(f"RESULT: {ok_count}/7 ok")
    return 0 if ok_count == 7 else 1


if __name__ == "__main__":
    sys.exit(main())
