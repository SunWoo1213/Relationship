"""Refs: P8-frontend U2 S3.1 R8 원칙9 -- 원문 조회 두 엔드포인트 테스트.

`GET /events/{event_id}/raw`·`GET /persons/{person_id}/facts/{fact_id}/sources`.
계약 값(원문 일치·정렬·상한·404 네 경우·행 수 불변)을 전부 값으로 단언한다.
실 PostgreSQL 필요(`dbtest`). LLM·외부 네트워크 0.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_now, get_session
from app.api.read import FACT_SOURCES_LIMIT
from app.db.models import (
    Event,
    FactSource,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)
from app.main import create_app
from tests.helpers_read_api import assert_no_writes, snapshot_db

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
NOT_FOUND = {"detail": {"code": "not_found"}}

# 특수문자·줄바꿈·탭·이모지·따옴표·HTML·앞뒤 공백까지 한 문자열에 -- 가공되면 달라진다.
TRICKY_RAW = '  "팀장님"이 <b>또</b> 그러셨어 😅\n둘째 줄\t탭 \\n 리터럴 & ​끝  '


@pytest.fixture()
def client(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    return TestClient(app)


def _person(db, name="민수", user_id="local") -> Person:
    p = Person(user_id=user_id, display_name=name, relation_tag="친구", hierarchy="동")
    db.add(p)
    db.flush()
    return p


def _event(db, person, when=None, type_="meal", content="내용", raw="원문") -> Event:
    e = Event(
        person_id=person.id,
        type=type_,
        content=content,
        raw_utterance=raw,
        occurred_at=when or NOW,
    )
    db.add(e)
    db.flush()
    return e


def _fact(db, person, key="취미", value="등산", events=()) -> PersonFact:
    f = PersonFact(person_id=person.id, key=key, value=value, confidence=1.0)
    db.add(f)
    db.flush()
    for e in events:
        db.add(FactSource(fact_id=f.id, event_id=e.id))
    db.flush()
    return f


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------- 이벤트 원문


def test_이벤트_원문_응답_전체_값(client, db_session):
    p = _person(db_session)
    when = NOW - timedelta(days=3)
    e = _event(db_session, p, when, type_="conflict", content="말다툼", raw=TRICKY_RAW)
    r = client.get(f"/events/{e.id}/raw")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"event_id", "person_id", "type", "content", "occurred_at", "raw_utterance"}
    assert body["event_id"] == e.id
    assert body["person_id"] == p.id
    assert body["type"] == "conflict"
    assert body["content"] == "말다툼"
    assert _dt(body["occurred_at"]) == when
    assert body["raw_utterance"] == TRICKY_RAW  # 한 글자도 가공되지 않는다


def test_이벤트_원문은_두_이벤트를_섞지_않는다(client, db_session):
    p = _person(db_session)
    e1 = _event(db_session, p, raw="첫째 원문")
    e2 = _event(db_session, p, raw="둘째 원문")
    assert client.get(f"/events/{e1.id}/raw").json()["raw_utterance"] == "첫째 원문"
    assert client.get(f"/events/{e2.id}/raw").json()["raw_utterance"] == "둘째 원문"


def test_이벤트_원문_긴_문자열도_자르지_않는다(client, db_session):
    p = _person(db_session)
    raw = "가" * 5000
    e = _event(db_session, p, raw=raw)
    assert client.get(f"/events/{e.id}/raw").json()["raw_utterance"] == raw


def test_이벤트_404_없는_이벤트(client, db_session):
    _person(db_session)
    r = client.get("/events/99999999/raw")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_이벤트_404_타사용자_이벤트(client, db_session):
    # persons.user_id 조인 조건을 지우면 200 이 되어 실패한다.
    other = _person(db_session, "남", user_id="other")
    e = _event(db_session, other, raw="남의 비밀")
    r = client.get(f"/events/{e.id}/raw")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    assert "남의 비밀" not in r.text


# ------------------------------------------------------------------ 사실 근거


def test_근거_응답_전체_값과_내림차순(client, db_session):
    p = _person(db_session)
    # 삽입은 오래된 -> 최신 순이 아니게 섞는다(순서가 뒤집히면 실패).
    e_mid = _event(db_session, p, NOW - timedelta(days=5), "meal", "중간", "원문-중간")
    e_old = _event(db_session, p, NOW - timedelta(days=9), "conflict", "오래됨", TRICKY_RAW)
    e_new = _event(db_session, p, NOW - timedelta(days=1), "praise", "최신", "원문-최신")
    f = _fact(db_session, p, "취미", "등산", [e_mid, e_old, e_new])
    r = client.get(f"/persons/{p.id}/facts/{f.id}/sources")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"fact", "sources"}
    assert body["fact"] == {"id": f.id, "key": "취미", "value": "등산"}
    assert [s["event_id"] for s in body["sources"]] == [e_new.id, e_mid.id, e_old.id]
    assert [s["raw_utterance"] for s in body["sources"]] == ["원문-최신", "원문-중간", TRICKY_RAW]
    assert [s["type"] for s in body["sources"]] == ["praise", "meal", "conflict"]
    assert [s["content"] for s in body["sources"]] == ["최신", "중간", "오래됨"]
    assert [_dt(s["occurred_at"]) for s in body["sources"]] == [
        NOW - timedelta(days=1),
        NOW - timedelta(days=5),
        NOW - timedelta(days=9),
    ]
    assert set(body["sources"][0]) == {
        "event_id", "type", "content", "occurred_at", "raw_utterance"
    }


def test_근거_동률_occurred_at_은_id_내림차순(client, db_session):
    p = _person(db_session)
    a = _event(db_session, p, NOW, raw="a")
    b = _event(db_session, p, NOW, raw="b")
    c = _event(db_session, p, NOW, raw="c")
    f = _fact(db_session, p, events=[a, b, c])  # id 오름차순 a<b<c
    ids = [s["event_id"] for s in client.get(f"/persons/{p.id}/facts/{f.id}/sources").json()["sources"]]
    assert ids == [c.id, b.id, a.id]


def test_근거_상한(client, db_session):
    p = _person(db_session)
    events = [
        _event(db_session, p, NOW - timedelta(days=d), raw=f"원문{d}")
        for d in range(FACT_SOURCES_LIMIT + 5)
    ]
    f = _fact(db_session, p, events=events)
    body = client.get(f"/persons/{p.id}/facts/{f.id}/sources").json()
    assert FACT_SOURCES_LIMIT == 20
    assert len(body["sources"]) == FACT_SOURCES_LIMIT
    # 최신 20건만 남고 가장 오래된 5건이 잘린다.
    assert [s["raw_utterance"] for s in body["sources"]] == [
        f"원문{d}" for d in range(FACT_SOURCES_LIMIT)
    ]


def test_근거_없는_사실은_빈_목록(client, db_session):
    p = _person(db_session)
    f = _fact(db_session, p)
    r = client.get(f"/persons/{p.id}/facts/{f.id}/sources")
    assert r.status_code == 200
    assert r.json() == {"fact": {"id": f.id, "key": "취미", "value": "등산"}, "sources": []}


def test_근거는_다른_사실의_원문을_섞지_않는다(client, db_session):
    p = _person(db_session)
    e1 = _event(db_session, p, raw="사실1 근거")
    e2 = _event(db_session, p, raw="사실2 근거")
    f1 = _fact(db_session, p, "k1", "v1", [e1])
    _fact(db_session, p, "k2", "v2", [e2])
    srcs = client.get(f"/persons/{p.id}/facts/{f1.id}/sources").json()["sources"]
    assert [s["raw_utterance"] for s in srcs] == ["사실1 근거"]


def test_근거_404_없는_사실(client, db_session):
    p = _person(db_session)
    r = client.get(f"/persons/{p.id}/facts/99999999/sources")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_근거_404_없는_인물(client, db_session):
    p = _person(db_session)
    f = _fact(db_session, p)
    r = client.get(f"/persons/99999999/facts/{f.id}/sources")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_근거_404_남의_인물_경로의_남의_사실(client, db_session):
    # persons.user_id 조인 조건을 지우면 200 이 되어 실패한다.
    other = _person(db_session, "남", user_id="other")
    e = _event(db_session, other, raw="남의 비밀")
    f = _fact(db_session, other, events=[e])
    r = client.get(f"/persons/{other.id}/facts/{f.id}/sources")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    assert "남의 비밀" not in r.text


def test_근거_404_내_다른_인물의_사실을_경로_인물에_끼운_경우(client, db_session):
    # person_facts.person_id 조건을 지우면 200 이 되어 실패한다.
    a = _person(db_session, "A")
    b = _person(db_session, "B")
    e = _event(db_session, b, raw="B 의 원문")
    fb = _fact(db_session, b, events=[e])
    r = client.get(f"/persons/{a.id}/facts/{fb.id}/sources")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    assert "B 의 원문" not in r.text


def test_근거_404_남의_인물_경로에_내_사실을_끼운_경우(client, db_session):
    mine = _person(db_session, "내사람")
    other = _person(db_session, "남", user_id="other")
    e = _event(db_session, mine, raw="내 원문")
    f = _fact(db_session, mine, events=[e])
    r = client.get(f"/persons/{other.id}/facts/{f.id}/sources")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_근거_세_404_응답이_서로_같다(client, db_session):
    a = _person(db_session, "A")
    b = _person(db_session, "B")
    other = _person(db_session, "남", user_id="other")
    fb = _fact(db_session, b)
    fo = _fact(db_session, other)
    bodies = [
        client.get(f"/persons/{a.id}/facts/99999999/sources"),  # 없음
        client.get(f"/persons/{other.id}/facts/{fo.id}/sources"),  # 남의 것
        client.get(f"/persons/{a.id}/facts/{fb.id}/sources"),  # 내 다른 인물의 사실
    ]
    assert {r.status_code for r in bodies} == {404}
    assert all(r.json() == NOT_FOUND for r in bodies)
    assert len({r.text for r in bodies}) == 1


def test_근거에_다른_인물_이벤트가_연결돼_있어도_나가지_않는다(client, db_session):
    # 데이터 오염 방어: fact_sources 가 타 사용자 이벤트를 가리켜도 응답에서 제외.
    p = _person(db_session)
    other = _person(db_session, "남", user_id="other")
    mine_e = _event(db_session, p, raw="내 원문")
    foreign_e = _event(db_session, other, raw="남의 비밀")
    f = _fact(db_session, p, events=[mine_e, foreign_e])
    r = client.get(f"/persons/{p.id}/facts/{f.id}/sources")
    assert [s["raw_utterance"] for s in r.json()["sources"]] == ["내 원문"]
    assert "남의 비밀" not in r.text


# ----------------------------------------------------------- 쓰기 0 · trace 0


def test_쓰기_0_trace_0(client, db_session):
    # R-U3-5 ① -- 행 수만이 아니라 `briefed_at`·`updated_at` 값까지 본다(공통 헬퍼).
    # `updated_at` 을 과거로 못 박아야 UPDATE(`onupdate=now()`)가 값 변화로 드러난다.
    p = _person(db_session)
    p.updated_at = NOW - timedelta(days=30)
    e = _event(db_session, p, raw="원문")
    f = _fact(db_session, p, events=[e])
    briefed = NOW - timedelta(hours=7)
    db_session.add_all(
        [PersonAlias(person_id=p.id, alias="민수형", source="user_said"),
         Schedule(person_id=p.id, title="약속", scheduled_at=NOW + timedelta(days=1), briefed_at=briefed)]
    )
    db_session.flush()

    before = snapshot_db(db_session)
    assert client.get(f"/events/{e.id}/raw").status_code == 200
    assert client.get(f"/persons/{p.id}/facts/{f.id}/sources").status_code == 200
    assert client.get("/events/99999999/raw").status_code == 404
    assert client.get(f"/persons/{p.id}/facts/99999999/sources").status_code == 404
    after = snapshot_db(db_session)
    assert_no_writes(before, after)
    # 값으로 한 번 더: 브리핑 시각과 인물 갱신 시각은 넣은 값 그대로.
    assert sorted(b for _, b in after.briefed_at if b is not None) == [briefed]
    assert dict(after.persons_updated_at)[p.id] == NOW - timedelta(days=30)
