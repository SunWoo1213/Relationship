"""Refs: P1-pilot-dataset S3.7 S3.1 원칙8

평가 시나리오 데이터셋(`data/scenarios/`)의 스키마 검증 + 교차 무결성 검사.

이 스크립트는 **골드 라벨이 스스로 모순되지 않는지**만 본다. 지표(오병합률·
미검출률·F1)는 P4-pilot-eval 이 계산한다. 위반을 못 잡는 검증기는 검증기가
아니므로(01-plan U1), 검사 항목마다 함수를 분리해
`tests/test_validate_scenarios.py` 가 일부러 깨뜨린 표본으로 각각을 확인한다.

사용::

    python scripts/validate_scenarios.py                 # 기본 --dir data/scenarios
    python scripts/validate_scenarios.py --json          # 기계 판독 요약(JSON 한 덩어리)
    python scripts/validate_scenarios.py --strict        # manifest.files 의 없는 파일도 FAIL

종료 코드: 0 = 오류 없음, 1 = 오류 하나 이상, 2 = 인자·경로 문제.

**네트워크·DB·LLM 을 쓰지 않는다.** `app/` 도 import 하지 않는다(01-plan 5행 —
데이터셋은 제품 코드에 런타임 의존하지 않는다). 값 집합(`events.type` 7종,
관계 태그 5종, 위계 3종)은 `data/scenarios/schema.json` 의 enum 으로 **복제**해
두고, 그 복제본이 `app.db.models` 의 튜플과 글자 그대로 같은지는 테스트가
대조한다.

검사 항목 (번호는 01-plan U1 의 위반 표본 번호와 같다)
------------------------------------------------------
(0)  적재  — `manifest.json` / 카테고리 파일 읽기 실패           `load_dataset`
(1)  스키마 위반                            `check_schema` / `check_manifest_schema`
(2)  `gold_person_id` 가 그 시나리오 `persons[].person_id` 밖    `check_gold_person_id`
     — H-1: `ambiguous: true` 인 mention 만 `null` 을 허용한다. `ambiguous` 가
       없거나 false 인데 `null` 이면 FAIL.
(3)  `turn` 이 `utterances` 범위 밖 (mentions·events 둘 다)      `check_turn_range`
(4)  `id` 전역 중복                                              `check_unique_ids`
(5)  `events[].type` 이 enum 밖 (스키마와 중복이지만 별도 메시지) `check_event_types`
(6)  manifest `counts`·`total` 과 실제 건수 불일치           `check_manifest_counts`
(7)  `persons` 의 이름이 manifest `virtual_names` 밖           `check_virtual_names`
(8)  manifest `ambiguous_mention_count` 불일치              `check_ambiguous_count`
(9)  `seed_persons` 가 `persons` 의 부분집합이 아님          `check_seed_persons`
(10) manifest `trap_count` 불일치                              `check_trap_count`
(11) — **비워 둔다.** 파일명 <-> `category` 일치 검사는 U5 예정.
(12) `mentions[].surface` 가 그 turn 의 발화에 없음     `check_surface_in_utterance`
(13) 발화 길이·턴 수가 구어체 규칙 밖                     `check_utterance_shape`

교차 검사는 12항목((1)~(10)·(12)·(13))이고, 여기에 적재 (0) 을 더한 13행이
사람이 읽는 출력·`--json` 요약의 검사 줄이다. (11) 은 번호만 예약해 둔다 —
비워 둔 번호에 PASS 를 찍으면 하지 않은 검사가 통과로 보인다.

구어체 규칙 (검사 (13), 01-plan 리스크 "한국어 구어체 부족")
--------------------------------------------------------
01-plan 85행: "LLM 초안은 문어체·완결 문장으로 기울고 ... 완화: ... (d) **발화
길이 8~60자** 규칙을 두고 검수 항목에 넣는다. 이 리스크가 현실화되면 P4 수치가
실사용보다 좋게 나온다 — 즉 **과대평가 방향의 편향**이므로 반드시 검수에서
잡는다." 턴 수 2~6 은 같은 규칙을 U2 생성 프롬프트가 옮겨 적은 값이다
(`evidence/20260906-1850-gen-prompt-u2.md` 28행 "발화 길이 8~60자, 턴 수 2~6").

경계값은 모듈 상수 `UTTERANCE_MIN_CHARS`/`UTTERANCE_MAX_CHARS`/`MIN_TURNS`/
`MAX_TURNS` 에 둔다. 길이는 **공백을 포함한 문자 수**(`len(str)`)다 — 형태소·
어절이 아니라 사람이 눈으로 셀 수 있는 값이어야 검수에서 다툼이 없다.

이름 판정 규칙 (검사 (7), 01-plan 리스크 "개인정보")
----------------------------------------------------
검사 대상 문자열은 두 가지뿐이다.

1. 모든 `persons[].display_name` — 길이·형태와 무관하게 **항상** 검사한다
   (실명이 들어갈 확률이 가장 높은 필드다).
2. `persons[].aliases[]` 중 한글 2~4자(`^[가-힣]{2,4}$`)인 원소.

이 문자열이 `manifest.json` 의 `virtual_names` 에 **완전 일치**로 없으면 FAIL.

규칙을 일부러 넓게 잡았다. "김팀장"·"부장님" 같은 직급 호칭도 한글 2~4자라
걸리므로 `virtual_names` 에 함께 적어야 한다. 화이트리스트가 부풀어도
개인정보 유출을 놓치는 것보다 낫다(원칙1 의 비대칭 비용과 같은 판단이다 —
검증기가 놓치는 쪽이 훨씬 비싸다).

**한계(숨기지 않는다)**: `utterances` 본문은 검사하지 않는다. 형태소 분석
없이 한국어 문장에서 이름 경계를 자르면 오탐이 쏟아져 검증기가 무력해진다.
발화 속 실명은 U5 검수 패킷과 U6 라벨 검수(사람)의 항목이다.

남긴 결정
---------
* **manifest 스키마 위치** — `schema.json` 의 `$defs` 가 아니라 별도 파일
  `data/scenarios/manifest.schema.json`. `schema.json` 의 루트는 이미 "시나리오
  객체" 이므로 매니페스트를 `$defs` 에 넣으면 소비자(P3-baselines·
  P4-pilot-eval)가 "어떤 `$ref` 를 써야 하는가" 를 알아야 하고 두 스키마의
  `schema_version` 을 따로 올릴 수도 없다. 파일을 나누면 각각 루트에서 바로
  검증된다.
* **없는 시나리오 파일** — 기본 모드에서는 `manifest.files` 에 적혀 있어도
  파일이 없으면 **0건**으로 다루고 오류로 세지 않는다. U1 시점에는 5파일이
  아직 없고(U2~U4 가 만든다) 그래도 검증기가 돌아야 하기 때문이다. 대신
  `--strict` 를 주면 없는 파일이 FAIL 이다 — U5·U7 의 수용 기준 검증은
  `--strict` 로 돌려 "파일이 없어서 0건" 과 "정말 0건" 을 구분한다.
* **`id` 규칙** — 전역 연번 `sc-001`(카테고리 접두 아님, R-7).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - 설치 안내만 하고 즉시 종료
    print(
        "jsonschema 가 설치돼 있지 않다: pip install -r requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from None

#: 기본 데이터 디렉터리(저장소 루트 기준 상대 경로).
DEFAULT_DIR = Path("data/scenarios")

SCENARIO_SCHEMA_FILE = "schema.json"
MANIFEST_SCHEMA_FILE = "manifest.schema.json"
MANIFEST_FILE = "manifest.json"

#: 스키마 파일들은 시나리오 파일이 아니다(fallback 탐색에서 제외).
NON_SCENARIO_FILES = frozenset(
    {SCENARIO_SCHEMA_FILE, MANIFEST_SCHEMA_FILE, MANIFEST_FILE}
)

#: 카테고리 순서. 출력·집계의 결정적 순서를 위해 고정한다(원칙8).
CATEGORIES: tuple[str, ...] = (
    "promotion",
    "pronoun",
    "alias",
    "normal",
    "new_person",
)

#: 검사 (7) 의 "한글 2~4자 성명 패턴". 위 docstring "이름 판정 규칙" 참조.
KOREAN_NAME_PATTERN = re.compile("^[가-힣]{2,4}$")

#: 검사 (13) 발화 길이 경계(문자 수, 공백 포함). 근거는 위 docstring "구어체 규칙"
#: 절 — 01-plan 리스크 "한국어 구어체 부족" 의 완화책 (d).
UTTERANCE_MIN_CHARS = 8
UTTERANCE_MAX_CHARS = 60

#: 검사 (13) 시나리오당 턴 수 경계. 같은 절 참조(U2 생성 프롬프트 28행).
MIN_TURNS = 2
MAX_TURNS = 6

#: 검사 번호 -> 사람이 읽는 이름(출력·JSON 요약에서 같은 문자열을 쓴다).
CHECK_NAMES: dict[str, str] = {
    "0": "적재(manifest·시나리오 파일 읽기)",
    "1": "스키마 위반",
    "2": "gold_person_id 교차(H-1 ambiguous 예외 포함)",
    "3": "turn 범위",
    "4": "id 전역 유일",
    "5": "events.type enum",
    "6": "manifest counts·total 일치",
    "7": "virtual_names 화이트리스트",
    "8": "manifest ambiguous_mention_count 일치",
    "9": "seed_persons ⊆ persons",
    "10": "manifest trap_count 일치",
    # (11) 파일명<->category 일치는 U5 예정 — 하지 않는 검사에 PASS 를 찍지 않는다.
    "12": "mentions.surface 가 그 turn 발화 안",
    "13": "발화 길이·턴 수(구어체 규칙)",
}


# --------------------------------------------------------------------------
# 자료 구조
# --------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Issue:
    """검사 하나가 찾은 위반 하나. `order=True` 라 정렬이 결정적이다(원칙8)."""

    check: str
    code: str
    where: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "check": self.check,
            "check_name": CHECK_NAMES.get(self.check, ""),
            "code": self.code,
            "where": self.where,
            "message": self.message,
        }

    def line(self) -> str:
        return f"[FAIL] ({self.check}) {self.code} {self.where}: {self.message}"


@dataclass
class FileEntry:
    """카테고리 파일 하나의 적재 결과. 스키마 위반 원소도 그대로 담는다."""

    name: str
    path: Path
    exists: bool
    scenarios: list[Any] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.scenarios)


@dataclass
class Dataset:
    directory: Path
    manifest: Any
    files: list[FileEntry]

    @property
    def scenarios(self) -> list[tuple[str, Any]]:
        """`(파일명, 시나리오)` 목록. 파일 순서 → 파일 안 순서로 결정적이다."""
        return [(entry.name, sc) for entry in self.files for sc in entry.scenarios]

    @property
    def manifest_dict(self) -> dict[str, Any] | None:
        """manifest 가 dict 일 때만 돌려준다(아니면 검사 (0)/(1) 이 이미 보고)."""
        return self.manifest if isinstance(self.manifest, dict) else None


@dataclass
class Report:
    directory: Path
    strict: bool
    dataset: Dataset
    issues: list[Issue]

    @property
    def ok(self) -> bool:
        return not self.issues

    def summary(self) -> dict[str, Any]:
        """`--json` 이 그대로 출력하는 기계 판독 요약."""
        actual = _actual_counts(self.dataset)
        return {
            "ok": self.ok,
            "dir": self.directory.as_posix(),
            "strict": self.strict,
            "schema_version": _manifest_value(self.dataset, "schema_version"),
            "files": [
                {"file": e.name, "exists": e.exists, "count": e.count}
                for e in self.dataset.files
            ],
            "counts": {c: actual.get(c, 0) for c in CATEGORIES},
            "total": sum(actual.get(c, 0) for c in CATEGORIES),
            "scenario_count": len(self.dataset.scenarios),
            "ambiguous_mention_count": _actual_ambiguous_mentions(self.dataset),
            "trap_count": _actual_traps(self.dataset),
            "issue_count": len(self.issues),
            "issues": [i.as_dict() for i in self.issues],
        }


# --------------------------------------------------------------------------
# 작은 도우미 (전부 방어적으로 — 스키마 위반 자료가 들어와도 죽지 않는다)
# --------------------------------------------------------------------------


def _scenario_id(scenario: Any) -> str:
    if isinstance(scenario, dict) and isinstance(scenario.get("id"), str):
        return scenario["id"]
    return "<id 없음>"


def _where(file_name: str, scenario: Any, suffix: str = "") -> str:
    base = f"{file_name}:{_scenario_id(scenario)}"
    return f"{base}:{suffix}" if suffix else base


def _dict_items(value: Any) -> list[dict[str, Any]]:
    """리스트 안의 dict 원소만 추린다(다른 타입은 스키마 검사가 잡는다)."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _person_ids(scenario: dict[str, Any]) -> set[str]:
    return {
        p["person_id"]
        for p in _dict_items(scenario.get("persons"))
        if isinstance(p.get("person_id"), str)
    }


def _manifest_value(dataset: Dataset, key: str) -> Any:
    manifest = dataset.manifest_dict
    return None if manifest is None else manifest.get(key)


def _actual_counts(dataset: Dataset) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for _, scenario in dataset.scenarios:
        if isinstance(scenario, dict) and isinstance(scenario.get("category"), str):
            counter[scenario["category"]] += 1
    return dict(counter)


def _actual_ambiguous_mentions(dataset: Dataset) -> int:
    total = 0
    for _, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        for mention in _dict_items(scenario.get("mentions")):
            if mention.get("ambiguous") is True:
                total += 1
    return total


def _actual_traps(dataset: Dataset) -> int:
    return sum(
        1
        for _, scenario in dataset.scenarios
        if isinstance(scenario, dict) and "trap" in scenario
    )


def event_type_enum(scenario_schema: Any) -> tuple[str, ...]:
    """스키마의 `$defs.event.properties.type.enum` 을 값 집합의 단일 출처로 쓴다.

    검사 (5) 가 스키마와 별도 메시지를 내되 **다른 목록을 들고 있지는 않게**
    하기 위해서다(하드코딩 두 벌이 어긋나는 것이 더 나쁜 실패다).
    """
    try:
        return tuple(scenario_schema["$defs"]["event"]["properties"]["type"]["enum"])
    except (TypeError, KeyError):  # pragma: no cover - 스키마 파일이 깨진 경우
        return ()


# --------------------------------------------------------------------------
# 적재 (검사 0)
# --------------------------------------------------------------------------


def load_json_file(path: Path) -> tuple[Any, str | None]:
    """`(값, 오류메시지)`. 읽기·파싱에 성공하면 오류는 None."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "파일이 없다"
    except json.JSONDecodeError as exc:
        return None, f"JSON 파싱 실패: {exc}"
    except OSError as exc:  # pragma: no cover - 권한 등
        return None, f"읽기 실패: {exc}"


def load_schemas(directory: Path) -> tuple[Any, Any, list[Issue]]:
    """시나리오 스키마와 매니페스트 스키마를 읽는다."""
    issues: list[Issue] = []
    scenario_schema, err = load_json_file(directory / SCENARIO_SCHEMA_FILE)
    if err:
        issues.append(Issue("0", "SCHEMA_LOAD", SCENARIO_SCHEMA_FILE, err))
    manifest_schema, err = load_json_file(directory / MANIFEST_SCHEMA_FILE)
    if err:
        issues.append(Issue("0", "SCHEMA_LOAD", MANIFEST_SCHEMA_FILE, err))
    return scenario_schema, manifest_schema, issues


def scenario_file_names(directory: Path, manifest: Any) -> list[str]:
    """읽을 카테고리 파일 목록. manifest.files 가 권위, 없으면 디렉터리 탐색."""
    if isinstance(manifest, dict):
        files = manifest.get("files")
        if isinstance(files, list) and all(isinstance(f, str) for f in files):
            return list(files)
    return sorted(
        p.name for p in directory.glob("*.json") if p.name not in NON_SCENARIO_FILES
    )


def load_dataset(directory: Path, *, strict: bool = False) -> tuple[Dataset, list[Issue]]:
    """manifest 와 카테고리 파일을 읽는다. 없는 파일은 기본 모드에서 0건."""
    issues: list[Issue] = []

    manifest, err = load_json_file(directory / MANIFEST_FILE)
    if err:
        issues.append(Issue("0", "MANIFEST_LOAD", MANIFEST_FILE, err))

    entries: list[FileEntry] = []
    for name in scenario_file_names(directory, manifest):
        path = directory / name
        if not path.exists():
            if strict:
                issues.append(
                    Issue(
                        "0",
                        "FILE_MISSING",
                        name,
                        "manifest.files 에 있으나 파일이 없다(--strict)",
                    )
                )
            entries.append(FileEntry(name=name, path=path, exists=False))
            continue
        value, err = load_json_file(path)
        if err:
            issues.append(Issue("1", "FILE_NOT_JSON", name, err))
            entries.append(FileEntry(name=name, path=path, exists=True))
            continue
        if not isinstance(value, list):
            issues.append(
                Issue(
                    "1",
                    "FILE_NOT_ARRAY",
                    name,
                    f"카테고리 파일은 시나리오 배열이어야 한다(실제: {type(value).__name__})",
                )
            )
            entries.append(FileEntry(name=name, path=path, exists=True))
            continue
        entries.append(FileEntry(name=name, path=path, exists=True, scenarios=value))

    return Dataset(directory=directory, manifest=manifest, files=entries), issues


# --------------------------------------------------------------------------
# 검사 (1) 스키마
# --------------------------------------------------------------------------


def check_schema(dataset: Dataset, scenario_schema: Any) -> list[Issue]:
    """(1) 시나리오 원소마다 JSON Schema 를 적용한다."""
    if not isinstance(scenario_schema, dict):
        return []
    validator = Draft202012Validator(scenario_schema)
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        for error in sorted(validator.iter_errors(scenario), key=lambda e: e.json_path):
            issues.append(
                Issue(
                    "1",
                    "SCHEMA",
                    _where(file_name, scenario, error.json_path),
                    error.message,
                )
            )
    return issues


def check_manifest_schema(dataset: Dataset, manifest_schema: Any) -> list[Issue]:
    """(1) manifest.json 에 매니페스트 스키마를 적용한다."""
    if not isinstance(manifest_schema, dict) or dataset.manifest is None:
        return []
    validator = Draft202012Validator(manifest_schema)
    return [
        Issue("1", "SCHEMA", f"{MANIFEST_FILE}:{e.json_path}", e.message)
        for e in sorted(validator.iter_errors(dataset.manifest), key=lambda e: e.json_path)
    ]


# --------------------------------------------------------------------------
# 검사 (2)~(5) 시나리오 내부 교차
# --------------------------------------------------------------------------


def check_gold_person_id(dataset: Dataset) -> list[Issue]:
    """(2) gold_person_id 는 그 시나리오의 persons 안에 있어야 한다.

    H-1 예외: `ambiguous: true` 인 mention 만 `null` 을 허용한다. `ambiguous`
    가 없거나 false 인데 `null` 이면 FAIL — 라벨을 비워 두고 지표 분모에서
    슬쩍 빠지는 일을 막는다(원칙8).
    """
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        known = _person_ids(scenario)
        for index, mention in enumerate(_dict_items(scenario.get("mentions"))):
            spot = f"mentions[{index}]({mention.get('surface', '?')})"
            gold = mention.get("gold_person_id")
            if gold is None:
                if mention.get("ambiguous") is not True:
                    issues.append(
                        Issue(
                            "2",
                            "GOLD_NULL_NOT_AMBIGUOUS",
                            _where(file_name, scenario, spot),
                            "gold_person_id: null 은 ambiguous: true 인 mention 에만 허용된다(H-1)",
                        )
                    )
                continue
            if isinstance(gold, str) and gold not in known:
                issues.append(
                    Issue(
                        "2",
                        "GOLD_ID_ORPHAN",
                        _where(file_name, scenario, spot),
                        f"gold_person_id={gold!r} 가 persons[].person_id {sorted(known)} 안에 없다",
                    )
                )
    return issues


def check_turn_range(dataset: Dataset) -> list[Issue]:
    """(3) mentions·events 의 turn 이 utterances 인덱스 범위 안이어야 한다."""
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        utterances = scenario.get("utterances")
        if not isinstance(utterances, list):
            continue
        limit = len(utterances)
        for key in ("mentions", "events"):
            for index, item in enumerate(_dict_items(scenario.get(key))):
                turn = item.get("turn")
                if not isinstance(turn, int) or isinstance(turn, bool):
                    continue  # 타입 위반은 스키마 검사 (1) 의 몫
                if not 0 <= turn < limit:
                    issues.append(
                        Issue(
                            "3",
                            "TURN_OUT_OF_RANGE",
                            _where(file_name, scenario, f"{key}[{index}]"),
                            f"turn={turn} 이 utterances 범위(0~{limit - 1}) 밖이다",
                        )
                    )
    return issues


def check_unique_ids(dataset: Dataset) -> list[Issue]:
    """(4) 시나리오 id 는 파일을 가로질러 전역 유일해야 한다."""
    seen: dict[str, str] = {}
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        sid = scenario.get("id")
        if not isinstance(sid, str):
            continue
        if sid in seen:
            issues.append(
                Issue(
                    "4",
                    "DUPLICATE_ID",
                    f"{file_name}:{sid}",
                    f"id 가 {seen[sid]} 와 중복이다(전역 연번 규칙)",
                )
            )
            continue
        seen[sid] = file_name
    return issues


def check_event_types(dataset: Dataset, scenario_schema: Any) -> list[Issue]:
    """(5) events[].type 이 고정 7종 안이어야 한다(스키마와 별도 메시지)."""
    allowed = event_type_enum(scenario_schema)
    if not allowed:
        return []
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        for index, event in enumerate(_dict_items(scenario.get("events"))):
            etype = event.get("type")
            if etype not in allowed:
                issues.append(
                    Issue(
                        "5",
                        "EVENT_TYPE_UNKNOWN",
                        _where(file_name, scenario, f"events[{index}]"),
                        f"type={etype!r} 은 고정 7종 {list(allowed)} 밖이다",
                    )
                )
    return issues


# --------------------------------------------------------------------------
# 검사 (6)~(10) manifest 대조 · seed
# --------------------------------------------------------------------------


def check_manifest_counts(dataset: Dataset) -> list[Issue]:
    """(6) manifest.counts·total 이 실제 시나리오 건수와 같아야 한다."""
    manifest = dataset.manifest_dict
    if manifest is None:
        return []
    actual = _actual_counts(dataset)
    declared = manifest.get("counts")
    issues: list[Issue] = []
    if isinstance(declared, dict):
        for category in CATEGORIES:
            want = declared.get(category)
            got = actual.get(category, 0)
            if want != got:
                issues.append(
                    Issue(
                        "6",
                        "COUNT_MISMATCH",
                        f"{MANIFEST_FILE}:counts.{category}",
                        f"manifest={want} 실제={got}",
                    )
                )
    total_declared = manifest.get("total")
    total_actual = len([s for _, s in dataset.scenarios])
    if total_declared != total_actual:
        issues.append(
            Issue(
                "6",
                "TOTAL_MISMATCH",
                f"{MANIFEST_FILE}:total",
                f"manifest={total_declared} 실제={total_actual}",
            )
        )
    return issues


def check_virtual_names(dataset: Dataset) -> list[Issue]:
    """(7) persons 의 이름이 manifest.virtual_names 화이트리스트 안이어야 한다.

    판정 규칙은 모듈 docstring "이름 판정 규칙" 절에 있다(display_name 전체 +
    한글 2~4자 alias). 개인정보 리스크(01-plan) 때문에 넓게 잡는다.
    """
    manifest = dataset.manifest_dict
    if manifest is None:
        return []
    allowed_raw = manifest.get("virtual_names")
    if not isinstance(allowed_raw, list):
        return []
    allowed = {name for name in allowed_raw if isinstance(name, str)}

    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        for index, person in enumerate(_dict_items(scenario.get("persons"))):
            candidates: list[tuple[str, str]] = []
            display = person.get("display_name")
            if isinstance(display, str):
                candidates.append((f"persons[{index}].display_name", display))
            aliases = person.get("aliases")
            if isinstance(aliases, list):
                for alias_index, alias in enumerate(aliases):
                    if isinstance(alias, str) and KOREAN_NAME_PATTERN.match(alias):
                        candidates.append(
                            (f"persons[{index}].aliases[{alias_index}]", alias)
                        )
            for spot, name in candidates:
                if name not in allowed:
                    issues.append(
                        Issue(
                            "7",
                            "NAME_NOT_IN_VIRTUAL_NAMES",
                            _where(file_name, scenario, spot),
                            f"{name!r} 이 manifest.virtual_names 에 없다(가상 성명 화이트리스트)",
                        )
                    )
    return issues


def check_ambiguous_count(dataset: Dataset) -> list[Issue]:
    """(8) manifest.ambiguous_mention_count 가 실제 ambiguous mention 수와 같아야.

    P4 가 이 값으로 오병합률·미검출률·F1 의 분모를 줄인다(H-1 (3)). 어긋나면
    지표가 조용히 틀린다.
    """
    manifest = dataset.manifest_dict
    if manifest is None:
        return []
    declared = manifest.get("ambiguous_mention_count")
    actual = _actual_ambiguous_mentions(dataset)
    if declared != actual:
        return [
            Issue(
                "8",
                "AMBIGUOUS_COUNT_MISMATCH",
                f"{MANIFEST_FILE}:ambiguous_mention_count",
                f"manifest={declared} 실제={actual}",
            )
        ]
    return []


def check_seed_persons(dataset: Dataset) -> list[Issue]:
    """(9) seed_persons 는 그 시나리오 persons[].person_id 의 부분집합이어야."""
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        seeds = scenario.get("seed_persons")
        if not isinstance(seeds, list):
            continue
        known = _person_ids(scenario)
        for seed in seeds:
            if isinstance(seed, str) and seed not in known:
                issues.append(
                    Issue(
                        "9",
                        "SEED_PERSON_UNKNOWN",
                        _where(file_name, scenario, "seed_persons"),
                        f"{seed!r} 가 persons[].person_id {sorted(known)} 안에 없다",
                    )
                )
    return issues


def check_trap_count(dataset: Dataset) -> list[Issue]:
    """(10) manifest.trap_count 가 trap 필드를 가진 시나리오 수와 같아야 한다."""
    manifest = dataset.manifest_dict
    if manifest is None:
        return []
    declared = manifest.get("trap_count")
    actual = _actual_traps(dataset)
    if declared != actual:
        return [
            Issue(
                "10",
                "TRAP_COUNT_MISMATCH",
                f"{MANIFEST_FILE}:trap_count",
                f"manifest={declared} 실제={actual}",
            )
        ]
    return []


# --------------------------------------------------------------------------
# 검사 (12)~(13) 발화 본문 대조
# --------------------------------------------------------------------------


def check_surface_in_utterance(dataset: Dataset) -> list[Issue]:
    """(12) `mentions[].surface` 는 `utterances[turn]` 안에 그대로 들어 있어야 한다.

    라벨의 `surface` 가 발화에 없으면 그 mention 은 **어떤 모델도 맞힐 수 없는
    라벨**이다(지칭 표현이 원문과 다르다). P4 의 분모에 들어가는 순간 모든 방식의
    Recall 을 똑같이 깎아 베이스라인 비교를 흐린다.

    부분 문자열 **정확 일치**로 본다 — 공백을 정규화하지 않는다. "김 팀장" 과
    "김팀장" 을 검증기가 같다고 봐 주면, 실행기(P3-baselines·P4)가 원문에서
    지칭을 잘라낼 때 쓰는 오프셋과 라벨이 어긋난 채 통과한다.

    `turn` 이 범위 밖이거나 타입이 틀린 경우는 검사 (3)/(1) 의 몫이라 건너뛴다
    (한 결함에 두 번 FAIL 을 내면 소견 수가 부풀어 원인 추적이 어려워진다).
    """
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        utterances = scenario.get("utterances")
        if not isinstance(utterances, list):
            continue
        for index, mention in enumerate(_dict_items(scenario.get("mentions"))):
            surface = mention.get("surface")
            turn = mention.get("turn")
            if not isinstance(surface, str):
                continue  # 타입 위반은 스키마 검사 (1)
            if not isinstance(turn, int) or isinstance(turn, bool):
                continue
            if not 0 <= turn < len(utterances):
                continue  # 범위 위반은 검사 (3)
            utterance = utterances[turn]
            if not isinstance(utterance, str):
                continue
            if surface not in utterance:
                issues.append(
                    Issue(
                        "12",
                        "SURFACE_NOT_IN_UTTERANCE",
                        _where(file_name, scenario, f"mentions[{index}]({surface})"),
                        f"surface={surface!r} 가 utterances[{turn}]={utterance!r} 안에 없다"
                        " (공백 정규화 없이 부분 문자열 정확 일치)",
                    )
                )
    return issues


def check_utterance_shape(dataset: Dataset) -> list[Issue]:
    """(13) 발화 길이 8~60자·시나리오당 턴 수 2~6 (구어체 규칙).

    근거는 모듈 docstring "구어체 규칙" 절(01-plan 리스크 "한국어 구어체 부족",
    U2 생성 프롬프트 28행). 경계는 `UTTERANCE_MIN_CHARS`/`UTTERANCE_MAX_CHARS`/
    `MIN_TURNS`/`MAX_TURNS` 상수이고 **양끝을 포함**한다(8자·60자·2턴·6턴은 통과).

    길이 규칙이 잡는 것은 두 방향의 편향이다. 너무 짧으면("응", "ㅇㅇ") 지칭이
    들어갈 자리가 없어 라벨이 붙지 않고, 너무 길면 LLM 이 쓴 문어체 서술이라
    실사용보다 쉬운 입력이 된다 — 둘 다 P4 수치를 실제보다 좋게 만든다.

    이 검사는 **문체**를 판정하지 않는다(ㅋㅋ·오타·조사 생략은 사람 검수 U6 의
    항목이다). 기계가 셀 수 있는 것만 센다.
    """
    issues: list[Issue] = []
    for file_name, scenario in dataset.scenarios:
        if not isinstance(scenario, dict):
            continue
        utterances = scenario.get("utterances")
        if not isinstance(utterances, list):
            continue  # 타입 위반은 스키마 검사 (1)
        turns = len(utterances)
        if not MIN_TURNS <= turns <= MAX_TURNS:
            issues.append(
                Issue(
                    "13",
                    "TURN_COUNT",
                    _where(file_name, scenario, "utterances"),
                    f"턴 수 {turns} 가 규칙({MIN_TURNS}~{MAX_TURNS}턴) 밖이다",
                )
            )
        for index, utterance in enumerate(utterances):
            if not isinstance(utterance, str):
                continue
            length = len(utterance)
            if not UTTERANCE_MIN_CHARS <= length <= UTTERANCE_MAX_CHARS:
                issues.append(
                    Issue(
                        "13",
                        "UTTERANCE_LENGTH",
                        _where(file_name, scenario, f"utterances[{index}]"),
                        f"길이 {length}자 가 규칙"
                        f"({UTTERANCE_MIN_CHARS}~{UTTERANCE_MAX_CHARS}자, 공백 포함) 밖이다",
                    )
                )
    return issues


# --------------------------------------------------------------------------
# 실행
# --------------------------------------------------------------------------


def run(directory: Path, *, strict: bool = False) -> Report:
    """전 검사를 돌린다. 같은 입력이면 같은 Report 를 낸다(원칙8)."""
    scenario_schema, manifest_schema, issues = load_schemas(directory)
    dataset, load_issues = load_dataset(directory, strict=strict)
    issues.extend(load_issues)

    issues.extend(check_schema(dataset, scenario_schema))
    issues.extend(check_manifest_schema(dataset, manifest_schema))
    issues.extend(check_gold_person_id(dataset))
    issues.extend(check_turn_range(dataset))
    issues.extend(check_unique_ids(dataset))
    issues.extend(check_event_types(dataset, scenario_schema))
    issues.extend(check_manifest_counts(dataset))
    issues.extend(check_virtual_names(dataset))
    issues.extend(check_ambiguous_count(dataset))
    issues.extend(check_seed_persons(dataset))
    issues.extend(check_trap_count(dataset))
    issues.extend(check_surface_in_utterance(dataset))
    issues.extend(check_utterance_shape(dataset))

    return Report(
        directory=directory,
        strict=strict,
        dataset=dataset,
        issues=sorted(issues),
    )


def format_text(report: Report) -> str:
    """사람이 읽는 출력. 검사 번호마다 PASS 한 줄 또는 FAIL 여러 줄."""
    lines = [f"== validate_scenarios {report.directory.as_posix()} =="]
    lines.append(
        f"[info] strict={report.strict} "
        f"schema_version={_manifest_value(report.dataset, 'schema_version')}"
    )
    for entry in report.dataset.files:
        state = f"{entry.count}건" if entry.exists else "파일 없음(0건으로 취급)"
        lines.append(f"[info] {entry.name}: {state}")

    by_check: dict[str, list[Issue]] = {}
    for issue in report.issues:
        by_check.setdefault(issue.check, []).append(issue)

    for number, name in CHECK_NAMES.items():
        found = by_check.get(number, [])
        if not found:
            lines.append(f"[PASS] ({number}) {name}")
            continue
        for issue in found:
            lines.append(issue.line())

    actual = _actual_counts(report.dataset)
    lines.append(
        "[info] 카테고리별: "
        + " ".join(f"{c}={actual.get(c, 0)}" for c in CATEGORIES)
    )
    lines.append(
        f"== 결과: 시나리오 {len(report.dataset.scenarios)}건 / 오류 {len(report.issues)} =="
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="평가 시나리오 데이터셋 검증기(네트워크·DB 없음)."
    )
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_DIR),
        help=f"시나리오 디렉터리(기본 {DEFAULT_DIR.as_posix()})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="기계 판독 요약(파일별 건수·카테고리 합계·오류 목록)을 JSON 으로 출력",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="manifest.files 에 있으나 없는 파일을 FAIL 로 다룬다",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"디렉터리가 없다: {directory.as_posix()}", file=sys.stderr)
        return 2

    report = run(directory, strict=args.strict)
    if args.json:
        print(json.dumps(report.summary(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 0 if report.ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
