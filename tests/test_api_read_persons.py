"""Refs: P8-frontend U1 S3.1 S3.5 원칙9 -- `GET /persons`·`GET /persons/{id}` 테스트.

`TestClient(create_app())` + `get_session`(롤백 픽스처)·`get_now`(고정 시계)
오버라이드. 실 PostgreSQL 필요(`dbtest`). LLM·외부 네트워크 0.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_now, get_session
from app.api.read import TIMELINE_LIMIT
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


@pytest.fixture()
def client(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    return TestClient(app)


def _person(db, name="민수", user_id="local", tag="친구", hier="동") -> Person:
    p = Person(user_id=user_id, display_name=name, relation_tag=tag, hierarchy=hier)
    db.add(p)
    db.flush()
    return p


def _event(db, person, days_ago, type_="meal", raw="비밀 원문 RAW") -> Event:
    e = Event(
        person_id=person.id,
        type=type_,
        content=f"내용{days_ago}",
        raw_utterance=raw,
        occurred_at=NOW - timedelta(days=days_ago),
    )
    db.add(e)
    db.flush()
    return e


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def test_목록_last_contact_는_max_이고_정렬은_max_기준(client, db_session):
    # max 면 A(1일 전) 가 B(10일 전) 보다 앞, min 이면 A(30일 전) 가 B 뒤 -> 변이 감지용.
    a = _person(db_session, "A")
    b = _person(db_session, "B")
    _event(db_session, a, 30)
    _event(db_session, a, 1)
    _event(db_session, b, 10)
    body = client.get("/persons").json()
    assert [r["id"] for r in body] == [a.id, b.id]
    assert _dt(body[0]["last_contact_at"]) == NOW - timedelta(days=1)
    assert _dt(body[1]["last_contact_at"]) == NOW - timedelta(days=10)


def test_카드_last_contact_는_가장_늦은_occurred_at(client, db_session):
    p = _person(db_session)
    _event(db_session, p, 30)
    _event(db_session, p, 1)
    _event(db_session, p, 10)
    body = client.get(f"/persons/{p.id}").json()
    assert _dt(body["last_contact_at"]) == NOW - timedelta(days=1)


def test_카드_별칭은_파이썬_sorted_코드포인트순(client, db_session):
    # 콜레이션 정렬이면 apple 이 Bob 앞에 오지만 sorted() 는 대문자 -> 소문자 -> 한글.
    p = _person(db_session)
    db_session.add_all(
        [PersonAlias(person_id=p.id, alias=a, source="user_said")
         for a in ("가나", "apple", "Zed", "Bob")]
    )
    db_session.flush()
    body = client.get(f"/persons/{p.id}").json()
    assert body["aliases"] == sorted(["가나", "apple", "Zed", "Bob"])
    assert body["aliases"] == ["Bob", "Zed", "apple", "가나"]


def test_다가오는_일정_상한은_10건_가까운_순(client, db_session):
    p = _person(db_session)
    db_session.add_all(
        [Schedule(person_id=p.id, title=f"일정{h}", scheduled_at=NOW + timedelta(hours=h))
         for h in range(11, 0, -1)]  # 11건, 역순 삽입
    )
    db_session.flush()
    body = client.get(f"/persons/{p.id}").json()
    assert [s["title"] for s in body["upcoming_schedules"]] == [f"일정{h}" for h in range(1, 11)]


def test_다가오는_일정_경계_지금은_포함_1초_전은_제외(client, db_session):
    p = _person(db_session)
    db_session.add_all(
        [Schedule(person_id=p.id, title="1초전", scheduled_at=NOW - timedelta(seconds=1)),
         Schedule(person_id=p.id, title="지금", scheduled_at=NOW)]
    )
    db_session.flush()
    body = client.get(f"/persons/{p.id}").json()
    assert [s["title"] for s in body["upcoming_schedules"]] == ["지금"]


def test_목록_정렬_최근순_null_뒤_동률은_id순(client, db_session):
    a = _person(db_session, "A")  # 5일 전
    b = _person(db_session, "B")  # 이벤트 없음
    c = _person(db_session, "C")  # 1일 전
    d = _person(db_session, "D")  # 이벤트 없음
    e1 = _person(db_session, "E")  # C 와 동률
    _event(db_session, a, 5)
    _event(db_session, a, 9)
    _event(db_session, c, 1)
    _event(db_session, e1, 1)
    body = client.get("/persons").json()
    assert [r["id"] for r in body] == [c.id, e1.id, a.id, b.id, d.id]
    assert _dt(body[0]["last_contact_at"]) == NOW - timedelta(days=1)
    assert _dt(body[2]["last_contact_at"]) == NOW - timedelta(days=5)  # A: max(5, 9)
    assert body[3]["last_contact_at"] is None
    assert set(body[0]) == {
        "id", "display_name", "relation_tag", "hierarchy", "last_contact_at", "aliases"
    }


def test_목록은_다른_사용자_인물을_뺀다(client, db_session):
    mine = _person(db_session, "내사람")
    _person(db_session, "남의사람", user_id="other")
    assert [r["id"] for r in client.get("/persons").json()] == [mine.id]


def test_카드_구성과_분리_집계(client, db_session):
    p = _person(db_session)
    db_session.add_all(
        [PersonAlias(person_id=p.id, alias="민수형", source="user_said"),
         PersonAlias(person_id=p.id, alias="민수", source="confirmed")]
    )
    e1 = _event(db_session, p, 3)
    e2 = _event(db_session, p, 2)
    f1 = PersonFact(person_id=p.id, key="취미", value="등산", confidence=1.0)
    f2 = PersonFact(person_id=p.id, key="pattern:meal", value="자주 식사", confidence=1.0)
    f3 = PersonFact(person_id=p.id, key="직업", value="개발자", confidence=1.0)
    db_session.add_all([f1, f2, f3])
    db_session.flush()
    db_session.add_all(
        [FactSource(fact_id=f1.id, event_id=e1.id), FactSource(fact_id=f1.id, event_id=e2.id),
         FactSource(fact_id=f2.id, event_id=e1.id)]
    )
    db_session.add_all(
        [Schedule(person_id=p.id, title="과거", scheduled_at=NOW - timedelta(hours=1)),
         Schedule(person_id=p.id, title="나중", scheduled_at=NOW + timedelta(days=2)),
         Schedule(person_id=p.id, title="곧", scheduled_at=NOW + timedelta(hours=3))]
    )
    db_session.flush()

    r = client.get(f"/persons/{p.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["person"] == {
        "id": p.id, "display_name": "민수", "relation_tag": "친구", "hierarchy": "동"
    }
    assert body["aliases"] == ["민수", "민수형"]
    # 이벤트 3일 전·2일 전 -> max 는 2일 전(손계산: NOW - 2일 = 2026-02-27T09:00Z)
    assert _dt(body["last_contact_at"]) == NOW - timedelta(days=2)
    facts = {f["key"]: f for f in body["facts"]}
    assert set(facts) == {"취미", "직업"}  # pattern: 접두 제외
    assert facts["취미"]["source_count"] == 2
    assert facts["직업"]["source_count"] == 0
    assert [x["key"] for x in body["patterns"]] == ["pattern:meal"]
    assert body["patterns"][0]["source_count"] == 1
    assert [t["id"] for t in body["timeline"]] == [e2.id, e1.id]  # 최근 순
    assert [s["title"] for s in body["upcoming_schedules"]] == ["곧", "나중"]  # 과거 제외, 가까운 순
    assert set(body["upcoming_schedules"][0]) == {"id", "title", "scheduled_at", "briefed_at"}


def test_타임라인_상한(client, db_session):
    p = _person(db_session)
    for d in range(TIMELINE_LIMIT + 5):
        _event(db_session, p, d)
    body = client.get(f"/persons/{p.id}").json()
    assert len(body["timeline"]) == TIMELINE_LIMIT
    assert body["timeline"][0]["content"] == "내용0"


def test_응답에_raw_utterance_가_없다(client, db_session):
    p = _person(db_session)
    _event(db_session, p, 1, raw="절대노출금지")
    for url in ("/persons", f"/persons/{p.id}"):
        text = client.get(url).text
        assert "raw_utterance" not in text
        assert "절대노출금지" not in text
        json.loads(text)


def test_없는_인물과_타사용자_인물은_같은_404(client, db_session):
    other = _person(db_session, user_id="other")
    r1 = client.get(f"/persons/{other.id}")
    r2 = client.get("/persons/99999999")
    assert r1.status_code == r2.status_code == 404
    assert r1.json() == r2.json() == {"detail": {"code": "not_found"}}


def _alias(db, person, *names) -> None:
    db.add_all([PersonAlias(person_id=person.id, alias=n, source="user_said") for n in names])
    db.flush()


def test_목록_별칭은_카드_별칭과_같은_값_같은_순서(client, db_session):
    # 입력 순(Zed, 가나, apple, Bob)과 코드포인트 순(Bob, Zed, apple, 가나)이 다르다.
    p = _person(db_session, "A")
    q = _person(db_session, "B")
    _alias(db_session, p, "Zed", "가나", "apple", "Bob")
    _alias(db_session, q, "민수형", "Cat", "bat")
    rows = {r["id"]: r for r in client.get("/persons").json()}
    assert rows[p.id]["aliases"] == ["Bob", "Zed", "apple", "가나"]
    assert rows[q.id]["aliases"] == ["Cat", "bat", "민수형"]
    for pid in (p.id, q.id):
        assert rows[pid]["aliases"] == client.get(f"/persons/{pid}").json()["aliases"]


def test_목록_별칭_없는_인물은_빈_배열(client, db_session):
    p = _person(db_session, "A")
    q = _person(db_session, "B")
    _alias(db_session, q, "비")
    rows = {r["id"]: r for r in client.get("/persons").json()}
    assert rows[p.id]["aliases"] == []
    assert rows[q.id]["aliases"] == ["비"]


def _count_selects(db_session, client) -> int:
    from sqlalchemy import event

    conn = db_session.get_bind()
    stmts: list[str] = []

    def before(_conn, _cursor, statement, *_a):
        if statement.lstrip().upper().startswith("SELECT"):
            stmts.append(statement)

    event.listen(conn, "before_cursor_execute", before)
    try:
        assert client.get("/persons").status_code == 200
    finally:
        event.remove(conn, "before_cursor_execute", before)
    return len(stmts)


def test_목록_SELECT_수는_인물_수와_무관한_상수(client, db_session):
    for i in range(3):
        _alias(db_session, _person(db_session, f"P{i}"), f"a{i}", f"b{i}")
    n3 = _count_selects(db_session, client)
    for i in range(3, 10):
        _alias(db_session, _person(db_session, f"P{i}"), f"a{i}", f"b{i}")
    n10 = _count_selects(db_session, client)
    assert n3 == n10 == 2  # 목록 1 + 별칭 1


def test_목록_별칭에_다른_사용자_별칭이_섞이지_않는다(client, db_session):
    mine = _person(db_session, "내사람")
    other = _person(db_session, "남의사람", user_id="other")
    _alias(db_session, mine, "내별칭")
    _alias(db_session, other, "남별칭")
    body = client.get("/persons").json()
    assert [(r["id"], r["aliases"]) for r in body] == [(mine.id, ["내별칭"])]
    assert "남별칭" not in client.get("/persons").text


def test_목록_응답에_원문_키가_없다(client, db_session):
    p = _person(db_session)
    _event(db_session, p, 1, raw="절대노출금지")
    _alias(db_session, p, "별칭")
    body = client.get("/persons").json()
    assert set(body[0]).isdisjoint({"raw_utterance", "content"})
    assert "절대노출금지" not in json.dumps(body, ensure_ascii=False)


def test_쓰기_0_trace_0(client, db_session):
    # R-U3-5 ① -- 행 수만이 아니라 `briefed_at`·`updated_at` 값까지 본다(공통 헬퍼).
    # `updated_at` 을 과거로 못 박아야 UPDATE(`onupdate=now()`)가 값 변화로 드러난다.
    p = _person(db_session)
    p.updated_at = NOW - timedelta(days=30)
    e = _event(db_session, p, 1)
    f = PersonFact(person_id=p.id, key="k", value="v", confidence=1.0)
    db_session.add(f)
    db_session.flush()
    briefed = NOW - timedelta(hours=7)
    db_session.add_all(
        [FactSource(fact_id=f.id, event_id=e.id),
         Schedule(person_id=p.id, title="브리핑됨", scheduled_at=NOW + timedelta(hours=1), briefed_at=briefed),
         Schedule(person_id=p.id, title="미브리핑", scheduled_at=NOW + timedelta(hours=2))]
    )
    db_session.flush()

    before = snapshot_db(db_session)
    assert client.get("/persons").status_code == 200
    assert client.get(f"/persons/{p.id}").status_code == 200
    assert client.get("/persons/99999999").status_code == 404
    after = snapshot_db(db_session)
    assert_no_writes(before, after)
    # 값으로 한 번 더: 브리핑됨은 원래 시각 그대로, 미브리핑은 NULL 그대로, 인물은 30일 전 그대로.
    assert sorted(b for _, b in after.briefed_at if b is not None) == [briefed]
    assert dict(after.persons_updated_at)[p.id] == NOW - timedelta(days=30)
