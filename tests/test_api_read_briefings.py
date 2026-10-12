"""Refs: P8-frontend U3 S3.6 D2 R12 원칙9 -- `GET /briefings` 테스트.

원천은 `agent_traces` 의 `briefing_compose` 행(일정마다 최근 1행). 최신 선택·
동률 규칙·종류 필터·소유자 격리·기간 경계·정렬 2차 키·상한·`schedule_id`
모드·원문 부재·필드 매핑·쓰기 0 을 전부 값으로 단언한다.
실 PostgreSQL 필요(`dbtest`). LLM·외부 네트워크 0.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_now, get_session
from app.api.read import BRIEFINGS_LIMIT, BRIEFINGS_LOOKBACK_DAYS
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
)
from app.db.models import AgentTrace, Event, Person, Schedule
from app.main import create_app
from tests.helpers_read_api import assert_no_writes, snapshot_db

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
NOT_FOUND = {"detail": {"code": "not_found"}}
RAW = "팀장님이 또 그러셨어 비밀원문XYZ"


@pytest.fixture()
def client(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    return TestClient(app)


def _person(db, name="민수", user_id="local") -> Person:
    # updated_at 을 과거로 못 박는다: 같은 트랜잭션 안의 `now()` 는 고정이라, 행 생성
    # 직후 값이면 UPDATE(`onupdate=now()`)가 일어나도 값이 같아 변화를 못 잡는다.
    p = Person(
        user_id=user_id,
        display_name=name,
        relation_tag="친구",
        hierarchy="동",
        updated_at=NOW - timedelta(days=30),
    )
    db.add(p)
    db.flush()
    return p


def _schedule(db, person, scheduled_at, title="점심 약속", briefed_at=None) -> Schedule:
    s = Schedule(person_id=person.id, title=title, scheduled_at=scheduled_at, briefed_at=briefed_at)
    db.add(s)
    db.flush()
    return s


def _output(schedule, person, **over):
    out = {
        "schedule_id": schedule.id,
        "person_id": person.id,
        "pattern_trace_id": None,
        "used_facts": [{"key": "취미", "fact_id": 1, "eligible": True}],
        "excluded_facts": [],
        "event_ids": [11, 12],
        "composer": "llm",
        "pattern_sentences": [{"key": "pattern:meal", "sentence": "자주 식사를 함께했어요."}],
        "lines": [{"text": "지난번에 등산 얘기를 했어요.", "basis": {"fact_keys": ["취미"], "event_ids": [11]}}],
        "suggestion": {"text": "등산 안부를 물어보세요.", "basis": {"fact_keys": ["취미"], "event_ids": []}},
        "rejected": [],
        "llm": {"provider": "fake", "model": "fake-1"},
        "push": "not_configured",
    }
    out.update(over)
    return out


def _trace(
    db,
    schedule,
    person,
    created_at,
    step=STEP_BRIEFING_COMPOSE,
    tool_name=BRIEFING_TRACE_TOOL_NAME,
    **over,
) -> AgentTrace:
    t = AgentTrace(
        session_id="briefing:test",
        step=step,
        tool_name=tool_name,
        input={"schedule_id": schedule.id, "person_id": person.id},
        output=_output(schedule, person, **over),
        tokens_in=0,
        tokens_out=0,
        created_at=created_at,
    )
    db.add(t)
    db.flush()
    return t


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _ids(r):
    return [b["schedule"]["id"] for b in r.json()]


# ------------------------------------------------------------------ 값 매핑


def test_응답_필드_매핑_전체_값(client, db_session):
    p = _person(db_session, "김팀장")
    s = _schedule(db_session, p, NOW + timedelta(hours=5), "주간 회의")
    created = NOW - timedelta(hours=2)
    t = _trace(
        db_session, s, p, created,
        composer="template",
        push="sent:1",
        pattern_sentences=[{"key": "pattern:conflict", "sentence": "의견 충돌이 잦아요."}],
        lines=[{"text": "줄1", "basis": {"fact_keys": ["a", "b"], "event_ids": [3, 4]}}],
        suggestion=None,
    )
    r = client.get("/briefings")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    item = body[0]
    assert set(item) == {
        "schedule", "person", "generated_at", "composer", "pattern_sentences",
        "lines", "suggestion", "push", "trace_id",
    }
    assert set(item["schedule"]) == {"id", "title", "scheduled_at"}
    assert set(item["person"]) == {"id", "display_name"}
    assert item["schedule"]["id"] == s.id
    assert item["schedule"]["title"] == "주간 회의"
    assert _dt(item["schedule"]["scheduled_at"]) == NOW + timedelta(hours=5)
    assert item["person"] == {"id": p.id, "display_name": "김팀장"}
    assert _dt(item["generated_at"]) == created  # trace 행의 created_at
    assert item["trace_id"] == t.id  # agent_traces.id
    assert item["composer"] == "template"
    assert item["push"] == "sent:1"
    assert item["pattern_sentences"] == [{"key": "pattern:conflict", "sentence": "의견 충돌이 잦아요."}]
    assert item["lines"] == [{"text": "줄1", "basis": {"fact_keys": ["a", "b"], "event_ids": [3, 4]}}]
    assert item["suggestion"] is None


def test_제안이_있으면_basis_그대로(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    _trace(db_session, s, p, NOW - timedelta(hours=1))
    item = client.get("/briefings").json()[0]
    assert item["suggestion"] == {
        "text": "등산 안부를 물어보세요.",
        "basis": {"fact_keys": ["취미"], "event_ids": []},
    }
    assert item["composer"] == "llm"


# ------------------------------------------------ 원천 선택(최신 1행·종류)


def test_일정마다_최신_1행만(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    _trace(db_session, s, p, NOW - timedelta(hours=5), lines=[{"text": "오래됨", "basis": {}}])
    new = _trace(db_session, s, p, NOW - timedelta(hours=1), lines=[{"text": "최신", "basis": {}}])
    _trace(db_session, s, p, NOW - timedelta(hours=3), lines=[{"text": "중간", "basis": {}}])
    body = client.get("/briefings").json()
    assert len(body) == 1
    assert body[0]["trace_id"] == new.id
    assert [ln["text"] for ln in body[0]["lines"]] == ["최신"]


def test_동률_created_at_이면_id_큰_행(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    same = NOW - timedelta(hours=1)
    a = _trace(db_session, s, p, same, lines=[{"text": "a", "basis": {}}])
    b = _trace(db_session, s, p, same, lines=[{"text": "b", "basis": {}}])
    assert b.id > a.id
    body = client.get("/briefings").json()
    assert [x["trace_id"] for x in body] == [b.id]
    assert [ln["text"] for ln in body[0]["lines"]] == ["b"]


def test_run_과_error_행은_섞이지_않는다(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    compose = _trace(db_session, s, p, NOW - timedelta(hours=3))
    # 더 최근의 같은 tool_name 다른 step 행이 있어도 compose 가 뽑혀야 한다.
    _trace(db_session, s, p, NOW - timedelta(hours=1), step=STEP_BRIEFING_RUN)
    _trace(db_session, s, p, NOW - timedelta(minutes=5), step=STEP_BRIEFING_ERROR)
    body = client.get("/briefings").json()
    assert [x["trace_id"] for x in body] == [compose.id]


def test_다른_tool_name_의_compose_step_은_제외(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    _trace(db_session, s, p, NOW - timedelta(hours=1), tool_name="other_tool")
    assert client.get("/briefings").json() == []


def test_error_만_있는_일정은_제외(client, db_session):
    p = _person(db_session)
    s_err = _schedule(db_session, p, NOW, "오류만")
    s_ok = _schedule(db_session, p, NOW - timedelta(hours=1), "정상")
    _trace(db_session, s_err, p, NOW - timedelta(hours=1), step=STEP_BRIEFING_ERROR)
    _trace(db_session, s_ok, p, NOW - timedelta(hours=1))
    assert _ids(client.get("/briefings")) == [s_ok.id]


# ------------------------------------------------------------ 소유자 격리


def test_다른_사용자_일정은_제외(client, db_session):
    mine = _person(db_session, "나의 사람")
    other = _person(db_session, "남", user_id="other")
    s_mine = _schedule(db_session, mine, NOW)
    s_other = _schedule(db_session, other, NOW)
    _trace(db_session, s_mine, mine, NOW - timedelta(hours=1))
    _trace(db_session, s_other, other, NOW - timedelta(hours=1))
    r = client.get("/briefings")
    assert _ids(r) == [s_mine.id]
    assert "남" not in [b["person"]["display_name"] for b in r.json()]


# --------------------------------------------------------------- 기간 경계


def test_기간_경계_정확히_7일전_포함_7일_1초전_제외_미래_포함(client, db_session):
    assert BRIEFINGS_LOOKBACK_DAYS == 7
    p = _person(db_session)
    edge = _schedule(db_session, p, NOW - timedelta(days=7), "정확히 7일 전")
    out = _schedule(db_session, p, NOW - timedelta(days=7, seconds=1), "7일 1초 전")
    future = _schedule(db_session, p, NOW + timedelta(days=30), "먼 미래")
    for s in (edge, out, future):
        _trace(db_session, s, p, NOW - timedelta(days=1))
    ids = _ids(client.get("/briefings"))
    assert future.id in ids
    assert edge.id in ids
    assert out.id not in ids
    assert ids == [future.id, edge.id]


# ------------------------------------------------------------------- 정렬


def test_정렬_scheduled_at_내림차순과_2차키_id_내림차순(client, db_session):
    p = _person(db_session)
    far = _schedule(db_session, p, NOW + timedelta(days=2), "먼 미래")
    near_a = _schedule(db_session, p, NOW + timedelta(hours=1), "같은 시각 A")
    near_b = _schedule(db_session, p, NOW + timedelta(hours=1), "같은 시각 B")
    past = _schedule(db_session, p, NOW - timedelta(days=2), "과거")
    assert near_b.id > near_a.id
    # trace 생성 순서는 정렬과 무관하게 뒤섞는다.
    for s in (near_a, past, far, near_b):
        _trace(db_session, s, p, NOW - timedelta(hours=1))
    assert _ids(client.get("/briefings")) == [far.id, near_b.id, near_a.id, past.id]


# ------------------------------------------------------------------- 상한


def test_상한_21개_일정이면_20개(client, db_session):
    assert BRIEFINGS_LIMIT == 20
    p = _person(db_session)
    schedules = [
        _schedule(db_session, p, NOW + timedelta(hours=h), f"일정{h}") for h in range(BRIEFINGS_LIMIT + 1)
    ]
    for s in schedules:
        _trace(db_session, s, p, NOW - timedelta(hours=1))
    ids = _ids(client.get("/briefings"))
    assert len(ids) == BRIEFINGS_LIMIT
    # scheduled_at 이 가장 이른 1건(h=0)이 잘린다.
    assert ids == [s.id for s in reversed(schedules[1:])]


# ------------------------------------------------------- schedule_id 모드


def test_schedule_id_필터_1건(client, db_session):
    p = _person(db_session)
    s1 = _schedule(db_session, p, NOW + timedelta(hours=1), "일정1")
    s2 = _schedule(db_session, p, NOW + timedelta(hours=2), "일정2")
    _trace(db_session, s1, p, NOW - timedelta(hours=1))
    t2 = _trace(db_session, s2, p, NOW - timedelta(hours=1))
    body = client.get(f"/briefings?schedule_id={s2.id}").json()
    assert [x["schedule"]["id"] for x in body] == [s2.id]
    assert body[0]["trace_id"] == t2.id


def test_schedule_id_지정_시_기간_밖도_조회됨(client, db_session):
    p = _person(db_session)
    old = _schedule(db_session, p, NOW - timedelta(days=30), "한 달 전")
    _trace(db_session, old, p, NOW - timedelta(days=30))
    assert _ids(client.get("/briefings")) == []  # 기본 모드에선 기간 밖
    assert _ids(client.get(f"/briefings?schedule_id={old.id}")) == [old.id]


def test_schedule_id_일정은_있으나_trace_없으면_빈_목록(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    r = client.get(f"/briefings?schedule_id={s.id}")
    assert r.status_code == 200
    assert r.json() == []


def test_schedule_id_error_만_있어도_빈_목록(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    _trace(db_session, s, p, NOW, step=STEP_BRIEFING_ERROR)
    r = client.get(f"/briefings?schedule_id={s.id}")
    assert r.status_code == 200
    assert r.json() == []


def test_schedule_id_없는_일정은_404(client, db_session):
    _person(db_session)
    r = client.get("/briefings?schedule_id=99999999")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_schedule_id_남의_일정은_404(client, db_session):
    other = _person(db_session, "남", user_id="other")
    s = _schedule(db_session, other, NOW)
    _trace(db_session, s, other, NOW - timedelta(hours=1))
    r = client.get(f"/briefings?schedule_id={s.id}")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_schedule_id_두_404_응답이_같다(client, db_session):
    other = _person(db_session, "남", user_id="other")
    s = _schedule(db_session, other, NOW)
    a = client.get("/briefings?schedule_id=99999999")
    b = client.get(f"/briefings?schedule_id={s.id}")
    assert a.status_code == b.status_code == 404
    assert a.text == b.text


# --------------------------------------------------------------- 원문 부재


def test_응답에_raw_utterance_없음(client, db_session):
    p = _person(db_session)
    e = Event(person_id=p.id, type="meal", content="식사", raw_utterance=RAW, occurred_at=NOW)
    db_session.add(e)
    db_session.flush()
    s = _schedule(db_session, p, NOW)
    _trace(
        db_session, s, p, NOW - timedelta(hours=1),
        lines=[{"text": "식사 얘기", "basis": {"fact_keys": [], "event_ids": [e.id]}}],
        event_ids=[e.id],
    )
    for url in ("/briefings", f"/briefings?schedule_id={s.id}"):
        r = client.get(url)
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.text.count("raw_utterance") == 0
        assert "비밀원문XYZ" not in r.text
        assert r.json()[0]["lines"][0]["basis"]["event_ids"] == [e.id]  # id 만 나간다


# ------------------------------------------------------- 쓰기 0 · trace 0


def test_쓰기_0_trace_0_briefed_at_updated_at_불변(client, db_session):
    p = _person(db_session)
    briefed = NOW - timedelta(hours=7)
    s1 = _schedule(db_session, p, NOW, "브리핑됨", briefed_at=briefed)
    s2 = _schedule(db_session, p, NOW + timedelta(hours=1), "미브리핑")
    _trace(db_session, s1, p, NOW - timedelta(hours=1))
    _trace(db_session, s2, p, NOW - timedelta(hours=1))
    before = snapshot_db(db_session)
    assert len(client.get("/briefings").json()) == 2
    assert len(client.get(f"/briefings?schedule_id={s1.id}").json()) == 1
    assert client.get("/briefings?schedule_id=99999999").status_code == 404
    after = snapshot_db(db_session)
    assert_no_writes(before, after)
    # 값으로 한 번 더: briefed_at 은 정확히 원래 값, 미브리핑은 여전히 NULL.
    assert dict(after.briefed_at) == {s1.id: briefed, s2.id: None}


def test_헬퍼_자체_briefed_at_또는_updated_at_변경은_잡아낸다(db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    before = snapshot_db(db_session)
    s.briefed_at = NOW
    db_session.flush()
    with pytest.raises(AssertionError, match="briefed_at"):
        assert_no_writes(before, snapshot_db(db_session))
    before2 = snapshot_db(db_session)
    p.display_name = "개명"
    db_session.flush()
    with pytest.raises(AssertionError, match="updated_at"):
        assert_no_writes(before2, snapshot_db(db_session))


def test_응답은_JSON_직렬화_가능(client, db_session):
    p = _person(db_session)
    s = _schedule(db_session, p, NOW)
    _trace(db_session, s, p, NOW - timedelta(hours=1))
    json.loads(client.get("/briefings").text)
