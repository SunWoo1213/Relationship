"""Refs: P9b-auth U12 CR-008 D19 결정 4 AU AV -- MCP 도구 본체 4개 시험(SDK 없이 `tools.py` 직접).

계획 01-plan "도구 계약 — 개정 4"를 값으로 단언한다. 롤백 픽스처(`db_session`)를 쓰므로 DB 에 행이 남지
않는다. LLM·임베딩·외부 네트워크 0. 실 PostgreSQL 이 필요하다(`dbtest`).

- 결과는 `app.api.read` 의 세 함수 결과의 `model_dump(mode="json")` 과 **같다**(브리핑은 `trace_id` 키를 뺀 것).
- 상한은 `monkeypatch` 로 줄여 본다(도구가 호출 시점에 `app.settings` 속성을 읽는다).
- 원문 표식 `RAWMARK-7f3`·닉네임 표식 `닉표식` 은 어느 도구 결과에도 없다(D19 지킬 것 6).
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app import settings
from app.api import read
from app.briefing.types import BRIEFING_TRACE_TOOL_NAME, STEP_BRIEFING_COMPOSE
from app.db.models import (
    AgentTrace,
    ChatMessage,
    Event,
    FactSource,
    McpToken,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    PushSubscription,
    Schedule,
)
from app.mcp_server import tools
from app.mcp_server.tools import McpToolError, name_key
from tests.auth_helpers import make_user

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
UID = "mcptool-a"
OTHER = "mcptool-b"
RAW = "RAWMARK-7f3 팀장님이 또 그러셨어"
NICK = "닉표식"

#: 데이터·trace 표 -- 도구 호출 전후 행 수가 같아야 하는 11개 모델(계획 "데이터·trace 표").
_COUNTED = (
    Person,
    PersonAlias,
    PersonFact,
    FactSource,
    Event,
    Schedule,
    PendingQuestion,
    PushSubscription,
    AgentTrace,
    ChatMessage,
    McpToken,
)


def _person(db, name: str, user_id: str = UID, aliases: tuple[str, ...] = ()) -> Person:
    p = Person(user_id=user_id, display_name=name, relation_tag="직장", hierarchy="상")
    db.add(p)
    db.flush()
    for alias in aliases:
        db.add(PersonAlias(person_id=p.id, alias=alias, source="user"))
    db.flush()
    return p


def _event(db, person: Person, at: datetime, content: str = "점심을 같이 먹음", raw: str = RAW) -> Event:
    e = Event(person_id=person.id, type="meal", content=content, raw_utterance=raw, occurred_at=at)
    db.add(e)
    db.flush()
    return e


def _schedule(db, person: Person, at: datetime, title: str = "주간 회의") -> Schedule:
    s = Schedule(person_id=person.id, title=title, scheduled_at=at)
    db.add(s)
    db.flush()
    return s


def _compose_trace(db, schedule: Schedule, person: Person) -> AgentTrace:
    t = AgentTrace(
        session_id="briefing:test",
        step=STEP_BRIEFING_COMPOSE,
        tool_name=BRIEFING_TRACE_TOOL_NAME,
        input={"schedule_id": schedule.id, "person_id": person.id},
        output={
            "schedule_id": schedule.id,
            "person_id": person.id,
            "composer": "template",
            "pattern_sentences": [],
            "lines": [{"text": "지난번에 점심을 함께했어요.", "basis": {"fact_keys": [], "event_ids": []}}],
            "suggestion": None,
            "push": "not_configured",
        },
        tokens_in=0,
        tokens_out=0,
        created_at=NOW - timedelta(hours=1),
    )
    db.add(t)
    db.flush()
    return t


@pytest.fixture()
def users(db_session):
    make_user(db_session, UID, nickname=NICK)
    make_user(db_session, OTHER, nickname="남닉네임")


def _counts(db) -> list[int]:
    db.flush()
    return [db.scalar(select(func.count()).select_from(m)) for m in _COUNTED]


# ① list_people ---------------------------------------------------------------------------------


def test_list_people_equals_read_list_persons_dump_with_total_and_flag(db_session, users) -> None:
    a = _person(db_session, "김팀장", aliases=("팀장님",))
    b = _person(db_session, "이대리")
    _event(db_session, a, NOW - timedelta(days=1))
    _event(db_session, b, NOW - timedelta(days=3))
    _person(db_session, "남의 사람", user_id=OTHER)

    result = tools.tool_list_people(db_session, UID)

    expected = [p.model_dump(mode="json") for p in read.list_persons(db_session, UID)]
    assert result == {"people": expected, "total": 2, "truncated": False}
    assert [p["id"] for p in result["people"]] == [a.id, b.id]  # list_persons 순서 그대로
    assert result["people"][0]["aliases"] == ["팀장님"]


def test_list_people_limit_cuts_to_first_n_keeps_total_and_sets_truncated(
    db_session, users, monkeypatch
) -> None:
    people = [_person(db_session, f"인물{i}") for i in range(3)]
    for i, p in enumerate(people):  # 최근 접촉 순: 인물0 이 가장 최근
        _event(db_session, p, NOW - timedelta(days=i))
    monkeypatch.setattr(settings, "MCP_LIST_PEOPLE_LIMIT", 2)

    result = tools.tool_list_people(db_session, UID)

    assert [p["id"] for p in result["people"]] == [people[0].id, people[1].id]
    assert result["total"] == 3
    assert result["truncated"] is True


def test_list_people_exactly_at_limit_is_not_truncated(db_session, users, monkeypatch) -> None:
    for i in range(2):
        _person(db_session, f"인물{i}")
    monkeypatch.setattr(settings, "MCP_LIST_PEOPLE_LIMIT", 2)

    result = tools.tool_list_people(db_session, UID)

    assert (result["total"], result["truncated"], len(result["people"])) == (2, False, 2)


# ② find_person ---------------------------------------------------------------------------------


def test_find_person_returns_every_match_in_list_persons_order(db_session, users) -> None:
    older = _person(db_session, "박 과장")
    newer = _person(db_session, "박과장님")
    other = _person(db_session, "이대리")
    _event(db_session, older, NOW - timedelta(days=5))
    _event(db_session, newer, NOW - timedelta(days=1))
    _event(db_session, other, NOW)

    result = tools.tool_find_person(db_session, UID, "박과장")

    assert [m["id"] for m in result["matches"]] == [newer.id, older.id]  # 최근 접촉 순, 둘 다
    assert result["total"] == 2 and result["truncated"] is False


def test_find_person_same_display_name_returns_both_not_one(db_session, users) -> None:
    p1 = _person(db_session, "박 과장")
    p2 = _person(db_session, "박 과장")

    result = tools.tool_find_person(db_session, UID, "박 과장")

    assert sorted(m["id"] for m in result["matches"]) == sorted([p1.id, p2.id])
    assert result["total"] == 2


def test_find_person_matches_alias_case_insensitively(db_session, users) -> None:
    p = _person(db_session, "김팀장", aliases=("park",))

    result = tools.tool_find_person(db_session, UID, "PARK")

    assert [m["id"] for m in result["matches"]] == [p.id]


def test_find_person_nfd_input_matches_nfc_name(db_session, users) -> None:
    p = _person(db_session, "박과장")
    nfd = unicodedata.normalize("NFD", "박과장")
    assert nfd != "박과장"

    result = tools.tool_find_person(db_session, UID, nfd)

    assert [m["id"] for m in result["matches"]] == [p.id]


def test_find_person_without_match_is_empty_not_an_error(db_session, users) -> None:
    _person(db_session, "김팀장")

    result = tools.tool_find_person(db_session, UID, "없는이름")

    assert result == {"matches": [], "total": 0, "truncated": False}


def test_find_person_never_returns_another_accounts_person(db_session, users) -> None:
    _person(db_session, "남의박과장", user_id=OTHER)

    result = tools.tool_find_person(db_session, UID, "박과장")

    assert result["matches"] == []


@pytest.mark.parametrize("bad", ["", "   ", "\t\n", "가" * 51, "  " + "가" * 51 + "  "])
def test_find_person_rejects_blank_or_too_long_name(db_session, users, bad) -> None:
    with pytest.raises(McpToolError) as info:
        tools.tool_find_person(db_session, UID, bad)

    assert info.value.code == "invalid_name"
    assert str(info.value) == "invalid_name"


def test_find_person_name_length_boundary_50_ok_51_invalid(db_session, users) -> None:
    ok = tools.tool_find_person(db_session, UID, "가" * 50)
    padded = tools.tool_find_person(db_session, UID, " " + "가" * 50 + " ")  # 앞뒤 공백은 길이에 안 든다

    assert ok["matches"] == [] and padded["matches"] == []
    with pytest.raises(McpToolError):
        tools.tool_find_person(db_session, UID, "가" * 51)


@pytest.mark.parametrize("weird", ["a\x00b", "\x00", "민\x01지", "민지\x7f", "​민지"])
def test_find_person_control_characters_are_not_a_500(db_session, users, weird) -> None:
    _person(db_session, "김팀장")

    result = tools.tool_find_person(db_session, UID, weird)  # 예외 없이 정상 결과

    assert result["matches"] == []


def test_find_person_limit_truncates_but_keeps_total(db_session, users, monkeypatch) -> None:
    a = _person(db_session, "박과장A")
    b = _person(db_session, "박과장B")
    _event(db_session, a, NOW - timedelta(days=1))
    _event(db_session, b, NOW - timedelta(days=2))
    monkeypatch.setattr(settings, "MCP_FIND_PERSON_LIMIT", 1)

    result = tools.tool_find_person(db_session, UID, "박과장")

    assert [m["id"] for m in result["matches"]] == [a.id]
    assert result["total"] == 2 and result["truncated"] is True


def test_find_person_name_max_len_is_read_at_call_time(db_session, users, monkeypatch) -> None:
    monkeypatch.setattr(settings, "MCP_FIND_NAME_MAX_LEN", 3)

    assert tools.tool_find_person(db_session, UID, "가나다")["matches"] == []
    with pytest.raises(McpToolError):
        tools.tool_find_person(db_session, UID, "가나다라")


def test_name_key_removes_all_whitespace_folds_case_and_normalizes() -> None:
    assert name_key(" 박 \t과\n장 ") == "박과장"
    assert name_key("PaRk") == "park"
    assert name_key(unicodedata.normalize("NFD", "박과장")) == "박과장"


# ③ get_person_card ----------------------------------------------------------------------------


def test_get_person_card_equals_read_dump(db_session, users) -> None:
    p = _person(db_session, "김팀장", aliases=("팀장님",))
    _event(db_session, p, NOW - timedelta(days=2))
    _schedule(db_session, p, NOW + timedelta(days=1))

    result = tools.tool_get_person_card(db_session, UID, p.id, NOW)

    assert result == read.get_person_card(db_session, UID, p.id, NOW).model_dump(mode="json")
    assert result["person"]["id"] == p.id
    assert len(result["timeline"]) == 1 and len(result["upcoming_schedules"]) == 1


def test_get_person_card_other_accounts_and_missing_ids_are_not_found(db_session, users) -> None:
    theirs = _person(db_session, "남의 사람", user_id=OTHER)

    for pid in (theirs.id, theirs.id + 10_000):
        with pytest.raises(McpToolError) as info:
            tools.tool_get_person_card(db_session, UID, pid, NOW)
        assert info.value.code == "not_found"  # 없음과 남의 것이 같은 결과


# ④ list_briefings -----------------------------------------------------------------------------


def test_list_briefings_equals_read_dump_without_trace_id(db_session, users) -> None:
    p = _person(db_session, "김팀장")
    s = _schedule(db_session, p, NOW + timedelta(hours=5))
    trace = _compose_trace(db_session, s, p)

    result = tools.tool_list_briefings(db_session, UID, NOW, None)

    records = read.list_briefings(db_session, UID, NOW, None)
    assert len(records) == 1 and records[0].trace_id == trace.id  # 원천에는 있다
    expected = [{k: v for k, v in r.model_dump(mode="json").items() if k != "trace_id"} for r in records]
    assert result == {"briefings": expected}
    assert "trace_id" not in json.dumps(result)
    assert result["briefings"][0]["schedule"]["id"] == s.id


def test_list_briefings_by_schedule_id_and_other_accounts_schedule_is_not_found(db_session, users) -> None:
    mine = _person(db_session, "김팀장")
    theirs = _person(db_session, "남의 사람", user_id=OTHER)
    my_schedule = _schedule(db_session, mine, NOW + timedelta(hours=5))
    their_schedule = _schedule(db_session, theirs, NOW + timedelta(hours=6))
    _compose_trace(db_session, my_schedule, mine)
    _compose_trace(db_session, their_schedule, theirs)

    only_mine = tools.tool_list_briefings(db_session, UID, NOW, my_schedule.id)

    assert [b["schedule"]["id"] for b in only_mine["briefings"]] == [my_schedule.id]
    with pytest.raises(McpToolError) as info:
        tools.tool_list_briefings(db_session, UID, NOW, their_schedule.id)
    assert info.value.code == "not_found"
    with pytest.raises(McpToolError):
        tools.tool_list_briefings(db_session, UID, NOW, their_schedule.id + 10_000)


# ⑤ 원문·닉네임 표식 ------------------------------------------------------------------------------


def test_no_tool_result_contains_raw_utterance_or_nickname(db_session, users) -> None:
    p = _person(db_session, "김팀장", aliases=("팀장님",))
    _event(db_session, p, NOW - timedelta(days=1), content="점심을 같이 먹음", raw=RAW)
    s = _schedule(db_session, p, NOW + timedelta(hours=5))
    _compose_trace(db_session, s, p)

    dumped = json.dumps(
        [
            tools.tool_list_people(db_session, UID),
            tools.tool_find_person(db_session, UID, "김팀장"),
            tools.tool_get_person_card(db_session, UID, p.id, NOW),
            tools.tool_list_briefings(db_session, UID, NOW, None),
        ],
        ensure_ascii=False,
    )

    assert "RAWMARK-7f3" not in dumped
    assert NICK not in dumped
    assert '"raw_utterance"' not in dumped
    assert "점심을 같이 먹음" in dumped  # 요약(content)은 나간다 -- 원문이 아니라 추출 요약


# ⑥ 읽기 전용 -- 데이터·trace 표 불변 ---------------------------------------------------------------


def test_tools_do_not_change_any_table_row_counts(db_session, users) -> None:
    p = _person(db_session, "김팀장", aliases=("팀장님",))
    _event(db_session, p, NOW - timedelta(days=1))
    s = _schedule(db_session, p, NOW + timedelta(hours=5))
    _compose_trace(db_session, s, p)
    before = _counts(db_session)

    tools.tool_list_people(db_session, UID)
    tools.tool_find_person(db_session, UID, "김팀장")
    tools.tool_get_person_card(db_session, UID, p.id, NOW)
    tools.tool_list_briefings(db_session, UID, NOW, None)

    assert _counts(db_session) == before


# ⑦ import 금지 -- D19 지킬 것 5 ---------------------------------------------------------------------

_FORBIDDEN = re.compile(
    r"^\s*(from|import)\s+(app\.(tools|agent|er|briefing|embedding)|openai|anthropic|google)\b"
)


def test_mcp_server_modules_do_not_import_agent_tools_or_llm_providers() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "mcp_server"
    files = sorted(root.glob("*.py"))
    assert {f.name for f in files} >= {"__init__.py", "tools.py", "auth.py", "server.py"}
    offenders = [
        f"{f.name}:{n}: {line.strip()}"
        for f in files
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1)
        if _FORBIDDEN.match(line)
    ]
    assert offenders == []


def test_tools_module_does_not_import_the_sdk() -> None:
    """`tools.py` 는 SDK 없이 시험할 수 있어야 한다 -- SDK import 는 `server.py` 에만."""
    root = Path(__file__).resolve().parents[1] / "app" / "mcp_server"
    sdk = re.compile(r"^\s*(from|import)\s+mcp\b")
    for name in ("__init__.py", "tools.py", "auth.py"):
        text = (root / name).read_text(encoding="utf-8")
        assert not any(sdk.match(line) for line in text.splitlines()), name
