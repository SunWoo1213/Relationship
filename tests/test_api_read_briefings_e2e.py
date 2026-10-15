"""Refs: P8-frontend U9b 판정표 9·10행 S3.6 R12 R-U3-6 원칙9 -- `GET /briefings` 끝에서 끝.

U3 의 `test_api_read_briefings.py` 는 `agent_traces` 에 `briefing_compose` 행을 **직접 넣어**
조회 규칙을 시험했다(review-u3 32행). 여기서는 trace 를 **실제 실행이 만든다**:

- 일정 하나는 실제 `POST /briefings/run` 으로, 다른 하나는 `run_briefings(trigger="scheduler")`
  (1분 주기 작업이 부르는 바로 그 함수)로 브리핑한다.
- 그 뒤 `GET /briefings` 응답이 그 실행이 남긴 `briefing_compose.output` 과 값으로 같은지 비교한다.

문장 생성기는 `FakeBriefingComposer`(결정적, 네트워크 0), 알림기는 `NullNotifier`, "지금" 은
`get_now` 로 고정. 실 PostgreSQL 필요(`dbtest`). 실제 LLM·실제 푸시 0.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import get_briefing_composer, get_notifier, get_now, get_session
from app.briefing import NullNotifier, run_briefings
from app.briefing.compose import FakeBriefingComposer
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_COMPOSE,
    STEP_BRIEFING_ERROR,
    STEP_BRIEFING_RUN,
)
from app.db.models import AgentTrace, Event, FactSource, Person, PersonFact, Schedule
from app.main import create_app
from app.tools.context import ToolContext

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
RAW = "팀장님이 또 그러셨어 비밀원문XYZ"


@pytest.fixture()
def env(db_session):
    """(client, composer) -- 한 composer 인스턴스를 API 와 직접 호출이 같이 쓴다."""
    composer = FakeBriefingComposer()
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    app.dependency_overrides[get_briefing_composer] = lambda: composer
    app.dependency_overrides[get_notifier] = lambda: NullNotifier()
    return TestClient(app), composer


def _person(db, name="김팀장", user_id="local") -> Person:
    p = Person(user_id=user_id, display_name=name, relation_tag="직장", hierarchy="상")
    db.add(p)
    db.flush()
    return p


def _event(db, person, raw=RAW) -> Event:
    e = Event(
        person_id=person.id, type="meal", content="점심 식사", raw_utterance=raw,
        occurred_at=NOW - timedelta(days=3),
    )
    db.add(e)
    db.flush()
    return e


def _fact(db, person, event, key="hobby", value="등산") -> PersonFact:
    # 키는 승격 어휘 `FACT_KEYS`(hobby 등)여야 브리핑 입력의 used_facts 에 들어간다.
    f = PersonFact(person_id=person.id, key=key, value=value, confidence=0.9)
    db.add(f)
    db.flush()
    db.add(FactSource(fact_id=f.id, event_id=event.id))  # 근거가 있어야 제안의 기반이 된다
    db.flush()
    return f


def _schedule(db, person, hours_from_now, title) -> Schedule:
    s = Schedule(person_id=person.id, title=title, scheduled_at=NOW + timedelta(hours=hours_from_now))
    db.add(s)
    db.flush()
    return s


def _raw(line_text, suggestion_text, event_id):
    """FakeBriefingComposer 표의 한 칸 -- 기반(fact_keys·event_ids)이 입력에 있는 값이라 검증을 통과한다."""
    return {
        "pattern_sentences": [],
        "lines": [{"text": line_text, "basis": {"fact_keys": ["hobby"], "event_ids": [event_id]}}],
        "suggestion": {"text": suggestion_text, "basis": {"fact_keys": ["hobby"], "event_ids": []}},
    }


def _ctx(db, user_id="local"):
    return ToolContext(session=db, session_id="briefing-scheduler:u9b", user_id=user_id, now=lambda: NOW)


def _compose_rows(db, schedule_id):
    rows = db.execute(
        select(AgentTrace)
        .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
        .where(AgentTrace.step == STEP_BRIEFING_COMPOSE)
        .order_by(AgentTrace.id)
    ).scalars().all()
    return [t for t in rows if t.output["schedule_id"] == schedule_id]


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def test_9행_수동_실행과_주기_실행이_만든_trace_를_그대로_읽는다(env, db_session):
    client, composer = env
    p = _person(db_session)
    e = _event(db_session, p)
    _fact(db_session, p, e)
    s1 = _schedule(db_session, p, 5, "주간 회의")
    s2 = _schedule(db_session, p, 8, "저녁 약속")
    composer.table[s1.id] = _raw("수동 실행 줄", "수동 제안", e.id)
    composer.table[s2.id] = _raw("주기 실행 줄", "주기 제안", e.id)

    # 경로 1: 실제 POST /briefings/run (trigger="manual")
    resp = client.post("/briefings/run", json={"schedule_id": s1.id})
    assert resp.status_code == 200
    assert [b["schedule_id"] for b in resp.json()["briefings"]] == [s1.id]
    # 경로 2: 1분 주기 작업과 같은 함수 (trigger="scheduler") -- s1 은 briefed_at 이 찍혀 s2 만 대상
    result = run_briefings(_ctx(db_session), composer=composer, notifier=NullNotifier(), trigger="scheduler")
    assert [b["schedule_id"] for b in result.briefings] == [s2.id]

    r = client.get("/briefings")
    assert r.status_code == 200
    body = r.json()
    assert [b["schedule"]["id"] for b in body] == [s2.id, s1.id]  # scheduled_at 내림차순
    for item, sched, line, sugg in (
        (body[0], s2, "주기 실행 줄", "주기 제안"),
        (body[1], s1, "수동 실행 줄", "수동 제안"),
    ):
        rows = _compose_rows(db_session, sched.id)
        assert len(rows) == 1  # 실제 실행이 compose 행을 정확히 1개 남겼다
        out = rows[0].output
        assert item["trace_id"] == rows[0].id
        assert item["lines"] == out["lines"]
        assert item["suggestion"] == out["suggestion"]
        assert item["pattern_sentences"] == out["pattern_sentences"]
        assert item["composer"] == out["composer"] == "llm"  # 검증을 통과한 생성기 출력
        assert item["push"] == out["push"]
        # 생성기가 낸 문장이 거부되지 않고 그대로 실렸다
        assert [ln["text"] for ln in item["lines"]] == [line], out["rejected"]
        assert item["suggestion"]["text"] == sugg
        assert item["schedule"]["title"] == sched.title
        assert item["person"] == {"id": p.id, "display_name": "김팀장"}
        assert _dt(item["generated_at"]) == rows[0].created_at
    # 두 실행의 trigger 가 각각 기록됐다(run trace 는 실행마다 1행)
    triggers = sorted(
        t.output["trigger"]
        for t in db_session.execute(
            select(AgentTrace).where(AgentTrace.step == STEP_BRIEFING_RUN)
        ).scalars()
    )
    assert triggers == ["manual", "scheduler"]


def test_10행_재실행_사용자_범위_원문_다른_step_혼입(env, db_session):
    client, composer = env
    p = _person(db_session)
    e = _event(db_session, p)
    _fact(db_session, p, e)
    s1 = _schedule(db_session, p, 5, "주간 회의")
    s3 = _schedule(db_session, p, 6, "오류만 있는 일정")
    other = _person(db_session, "남", user_id="other")
    s_b = _schedule(db_session, other, 3, "남의 일정")
    e_b = _event(db_session, other, raw="남의 비밀")
    _fact(db_session, other, e_b)

    # (a) 같은 일정을 지정해 2회 실행 -- 두 번째 응답을 다르게
    composer.table[s1.id] = _raw("첫째 실행", "첫째 제안", e.id)
    assert client.post("/briefings/run", json={"schedule_id": s1.id}).status_code == 200
    composer.table[s1.id] = _raw("둘째 실행", "둘째 제안", e.id)
    assert client.post("/briefings/run", json={"schedule_id": s1.id}).status_code == 200
    rows = _compose_rows(db_session, s1.id)
    assert len(rows) == 2 and rows[1].id > rows[0].id  # 실제 실행이 2행을 남겼다

    # (b) 사용자 B 의 브리핑도 실제 실행으로 만든다 (APP_USER_ID 는 "local" 이라 목록에 없어야 한다)
    result_b = run_briefings(
        _ctx(db_session, user_id="other"), composer=composer, notifier=NullNotifier(),
        schedule_id=s_b.id, trigger="manual",
    )
    assert [b["schedule_id"] for b in result_b.briefings] == [s_b.id]
    assert len(_compose_rows(db_session, s_b.id)) == 1

    # (c) 일정 1 의 compose 보다 **나중** 행으로 직접 넣은 error 행(혼입 검출 재료). 일정 3 은 error 행만.
    #     실제 run 행은 실행이 남긴 것이며 output 에 최상위 schedule_id 가 없다(run.py 308~317행) -- 그래서
    #     schedule_id 조인에 걸리지 않아 혼입 검출 재료가 아니다. run 행 혼입은 U3 단위
    #     test_run_과_error_행은_섞이지_않는다 가 직접 삽입으로 맡는다.
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    for sid, step in ((s1.id, STEP_BRIEFING_ERROR), (s3.id, STEP_BRIEFING_ERROR)):
        db_session.add(
            AgentTrace(
                session_id="briefing:u9b", step=step, tool_name=BRIEFING_TRACE_TOOL_NAME,
                input={"schedule_id": sid, "person_id": p.id},
                output={"schedule_id": sid, "person_id": p.id, "error": "시험용 오류"},
                tokens_in=0, tokens_out=0, created_at=later,
            )
        )
    db_session.flush()
    run_rows = db_session.execute(
        select(AgentTrace).where(AgentTrace.step == STEP_BRIEFING_RUN)
    ).scalars().all()
    assert len(run_rows) == 3  # 실제 run 행(s1 두 번 + s_b 한 번) -- output 에 최상위 schedule_id 없음, 혼입 재료 아님

    r = client.get("/briefings")
    body = r.json()
    assert [b["schedule"]["id"] for b in body] == [s1.id]  # 내 것만 · 일정 3(error 만)·남의 일정 없음
    assert body[0]["trace_id"] == rows[1].id  # 두 번째 실행
    assert [ln["text"] for ln in body[0]["lines"]] == ["둘째 실행"]
    assert body[0]["suggestion"]["text"] == "둘째 제안"
    assert body[0]["lines"] == rows[1].output["lines"]
    # 원문·남의 정보 0
    assert "raw_utterance" not in r.text
    assert "비밀원문XYZ" not in r.text
    assert "남의 비밀" not in r.text
    assert "남의 일정" not in r.text
    # schedule_id 모드도 같은 행을 읽는다
    one = client.get(f"/briefings?schedule_id={s1.id}").json()
    assert [b["trace_id"] for b in one] == [rows[1].id]
