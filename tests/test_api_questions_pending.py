"""Refs: P8-frontend U3 S3.4 D2 원칙9 -- `GET /questions/pending` 테스트.

기존 `app.tools.questions.list_pending` 를 재사용하므로 여기서는 라우트 계약
(헤더 규약·필드 5개·세션 격리·만료 경계·정렬·쓰기 0)을 값으로 단언한다.
실 PostgreSQL 필요(`dbtest`). LLM·외부 네트워크 0.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.api.deps import get_now, get_session
from app.db.models import PendingQuestion
from app.main import create_app
from tests.auth_helpers import logged_in_client
from tests.helpers_read_api import assert_no_writes, snapshot_db

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
# U3b -- 대화 세션은 서버가 계정에서 만든다(`chat:<user_id>`). 이 파일의 로그인 사용자는 `local`.
SID = "chat:local"


@pytest.fixture()
def client(db_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: NOW)
    return logged_in_client(app, db_session)


def _q(
    db,
    session_id=SID,
    kind="identity",
    question="질문",
    options=("예", "아니오"),
    created_at=None,
    answered_at=None,
) -> PendingQuestion:
    q = PendingQuestion(
        session_id=session_id,
        user_id="local",
        kind=kind,
        question=question,
        options=list(options),
        context={"k": "v"},
        created_at=created_at or NOW - timedelta(minutes=1),
        answered_at=answered_at,
        answer=("예" if answered_at is not None else None),
    )
    db.add(q)
    db.flush()
    return q


def _get(client, sid=None):
    """`sid` 가 있으면 `X-Session-Id` 로 보낸다 -- 서버는 이 헤더를 무시한다(U3b)."""
    headers = {"X-Session-Id": sid} if sid is not None else {}
    return client.get("/questions/pending", headers=headers)


def test_헤더_없어도_계정_채팅방의_질문이_나오고_쓰기_0(client, db_session):
    # U3b ③ -- 헤더 없는 요청의 기대가 "빈 목록"에서 "로그인 계정 기준 목록"으로 바뀌었다.
    mine = _q(db_session)
    _q(db_session, session_id="sess-other", question="다른 세션 질문")  # 나가지 않는다
    before = snapshot_db(db_session)
    r = client.get("/questions/pending")
    assert r.status_code == 200
    assert [x["question_id"] for x in r.json()] == [mine.id]
    assert_no_writes(before, snapshot_db(db_session))


def test_형식_위반_세션_헤더는_무시되고_계정_목록이_나온다(client, db_session):
    # U3b ① -- 예전의 422 `invalid_session_id` 는 없어졌다(헤더를 읽지 않는다).
    mine = _q(db_session)
    for bad in ["a b", "a@b", "x" * 129, "a/b", ""]:
        r = client.get("/questions/pending", headers={"X-Session-Id": bad})
        assert r.status_code == 200, bad
        assert [x["question_id"] for x in r.json()] == [mine.id], bad


def test_필드_5개_값_일치(client, db_session):
    q = _q(db_session, kind="new_person", question="민수를 기억할까요?", options=("기억해줘", "아니"))
    r = _get(client)
    assert r.status_code == 200
    assert r.json() == [
        {
            "question_id": q.id,
            "status": "pending",
            "kind": "new_person",
            "question": "민수를 기억할까요?",
            "options": ["기억해줘", "아니"],
        }
    ]


def test_created_at_오름차순(client, db_session):
    # 삽입 순서와 created_at 순서를 일부러 다르게 한다.
    late = _q(db_session, question="늦음", created_at=NOW - timedelta(minutes=1))
    early = _q(db_session, question="이름", created_at=NOW - timedelta(hours=3))
    mid = _q(db_session, question="중간", created_at=NOW - timedelta(hours=1))
    ids = [x["question_id"] for x in _get(client).json()]
    assert ids == [early.id, mid.id, late.id]


def test_다른_세션_질문은_제외(client, db_session):
    mine = _q(db_session, session_id=SID, question="내 것")
    _q(db_session, session_id="sess-other", question="남의 세션")
    body = _get(client).json()
    assert [x["question_id"] for x in body] == [mine.id]
    assert [x["question"] for x in body] == ["내 것"]


def test_답변된_질문은_제외(client, db_session):
    open_q = _q(db_session, question="열림")
    _q(db_session, question="답함", answered_at=NOW - timedelta(seconds=30))
    assert [x["question_id"] for x in _get(client).json()] == [open_q.id]


def test_만료_경계_24시간(client, db_session):
    fresh = _q(db_session, question="23시간59분59초", created_at=NOW - timedelta(hours=24) + timedelta(seconds=1))
    _q(db_session, question="정확히 24시간", created_at=NOW - timedelta(hours=24))
    _q(db_session, question="25시간", created_at=NOW - timedelta(hours=25))
    assert [x["question_id"] for x in _get(client).json()] == [fresh.id]


def test_쓰기_0_trace_0(client, db_session):
    _q(db_session, question="열림")
    _q(db_session, question="답함", answered_at=NOW)
    _q(db_session, question="만료", created_at=NOW - timedelta(days=2))
    before = snapshot_db(db_session)
    assert len(_get(client).json()) == 1
    # U3b ③ -- 다른 세션 헤더를 보내도 무시된다(예전 기대는 빈 목록).
    assert len(_get(client, "none").json()) == 1
    assert len(client.get("/questions/pending").json()) == 1
    after = snapshot_db(db_session)
    assert_no_writes(before, after)
    assert after.counts == before.counts
