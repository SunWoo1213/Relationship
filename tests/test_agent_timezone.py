"""Refs: FIX-005 P5-loop S3.4 원칙8 원칙9 -- 사용자 시간대 보정 회귀
테스트(수정안 5행 ①~⑦).

증상: "어제 대학 동기 서준이랑 저녁 먹었어" 처럼 사람이 한국 시간으로
말한 시각이 UTC 기준으로 계산되어, 저장된 `occurred_at`·일정 후보 칩
문구가 실제로는 다른 현지 시각을 가리켰다(`docs/wiki/fixes/FIX-005.md`).

이 파일은 DB 저장까지 확인하는 통합 테스트(①④⑤, `dbtest` 마커)와
DB 없이 순수 로직만 보는 단위 테스트(②③⑥⑦)를 함께 둔다 -- 항목마다
가장 가까운 계층(파서/설정값 vs 전체 턴)에서 검증한다. 실제 LLM·임베딩
호출은 없다(`FakeProposer`/`FakeJudge`/`fake_embedder`, 원칙8).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.agent.loop import run_turn
from app.agent.propose import FakeProposer, build_propose_prompt, validate_proposal
from app.db.models import ALIAS_SOURCES, Event, PendingQuestion, Person, PersonAlias
from app.er.judge import FakeJudge
from app.settings import user_timezone
from app.tools.context import ToolContext
from app.tools.types import InvalidValue

# conftest.py 의 규약(dbtest 는 실제로 db_session/db_engine 을 쓰는
# 테스트에만 붙인다) -- 이 파일은 ①④⑤(run_turn, 실 DB)만 db_session 을
# 쓰고 ②③⑥⑦은 순수 로직이라 모듈 전체에 pytestmark 를 걸지 않는다.
# db_session 을 쓰는 테스트마다 개별로 @pytest.mark.dbtest 를 붙인다.


# ---------------------------------------------------------------------------
# 헬퍼 (tests/test_agent_loop.py 와 같은 모양 -- 각 테스트 파일이 독립적
# 으로 읽혀야 한다는 이 저장소 기존 관례를 따라 import 로 묶지 않고 여기
# 다시 정의한다)
# ---------------------------------------------------------------------------


def _make_person(
    db_session, *, display_name: str, relation_tag: str = "직장", hierarchy: str = "동"
) -> Person:
    person = Person(
        user_id="local", display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session, person: Person, alias: str, *, embedding) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=ALIAS_SOURCES[0], embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


# ---------------------------------------------------------------------------
# ① 오프셋 없는 occurred_at -- 저장값이 사용자 시간대 기준으로 해석된다
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_run_turn_stores_naive_occurred_at_as_user_timezone_instant(db_session, fake_embedder):
    """FIX-005 증상 재현·수정 확인. `FakeProposer` 가 오프셋 없는
    `"2026-09-24T18:00:00"` 을 주면, 사용자 시간대(기본 Asia/Seoul,
    +09:00)로 해석돼 저장된 `events.occurred_at` 은 UTC 로 2026-09-24
    09:00 이다(FIX-005.md 증상 문단의 기대값과 동일)."""

    session_id = "tz-u1-naive-occurred-at"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "서준", embedding=fake_embedder(["서준"])[0])
    # ctx.now() 자체는 임의의 UTC 시각이면 된다 -- 한국은 DST 가 없어
    # astimezone(Asia/Seoul) 오프셋은 항상 +09:00 이다.
    ctx = ToolContext(
        session=db_session,
        session_id=session_id,
        embedder=fake_embedder,
        now=lambda: datetime(2026, 9, 25, 3, 0, 0, tzinfo=timezone.utc),
    )

    utterance = "어제 서준이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "서준",
                "type": "meal",
                "content": "저녁 먹었어",
                "occurred_at": "2026-09-24T18:00:00",
            },
        }
    ]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.stored.events == 1
    event = db_session.execute(select(Event).where(Event.person_id == person.id)).scalar_one()
    assert event.occurred_at.astimezone(timezone.utc) == datetime(
        2026, 9, 24, 9, 0, 0, tzinfo=timezone.utc
    )


# ---------------------------------------------------------------------------
# ② 오프셋이 이미 있는 값은 그대로 존중한다 (now 의 오프셋과 달라도)
# ---------------------------------------------------------------------------


def test_validate_proposal_keeps_explicit_offset_even_when_tz_differs_from_now():
    raw = {
        "tool_calls": [
            {
                "name": "add_schedule",
                "args": {"person": "민수", "title": "약속", "scheduled_at": "2026-10-02T19:00:00+09:00"},
            }
        ]
    }
    # tz 인자로 넘긴 시간대(UTC)와 문자열 자체의 오프셋(+09:00)이 다르다
    # -- 파서는 문자열의 오프셋을 그대로 존중해야 한다(재해석하지 않는다).
    call = validate_proposal(raw, tz=timezone.utc).tool_calls[0]
    assert call.args["scheduled_at"] == datetime(
        2026, 10, 2, 19, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")
    )


# ---------------------------------------------------------------------------
# ③ +00:00 오프셋도 그대로 존중한다 (tz 인자가 KST 여도 UTC 로 재해석하지
# 않는다)
# ---------------------------------------------------------------------------


def test_validate_proposal_keeps_explicit_zero_offset_even_when_tz_is_kst():
    raw = {
        "tool_calls": [
            {
                "name": "add_event",
                "args": {"person": "민수", "type": "meal", "content": "저녁", "occurred_at": "2026-09-24T18:00:00+00:00"},
            }
        ]
    }
    call = validate_proposal(raw, tz=ZoneInfo("Asia/Seoul")).tool_calls[0]
    assert call.args["occurred_at"] == datetime(2026, 9, 24, 18, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# ④ 일정 후보(_schedule_candidates) -- 칩 문구의 날짜가 사용자 시간대
# 기준이고, 저장용 isoformat 도 같은 현지 시각을 가리킨다
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_schedule_candidates_use_user_timezone_wall_clock(db_session, fake_embedder):
    """고정 `now = 2026-09-24T23:30+00`(KST 로는 9월 25일 08:30)일 때,
    일정 후보는 KST 9월 26일·27일 저녁 7시다 -- UTC 기준으로 계산했다면
    "저녁 7시" 칩이 가리키는 순간이 KST 새벽 4시가 되어(FIX-005 증상 2)
    날짜도 하루씩 어긋났을 것이다."""

    session_id = "tz-u4-schedule-candidates"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    fixed_now = datetime(2026, 9, 24, 23, 30, 0, tzinfo=timezone.utc)
    ctx = ToolContext(session=db_session, session_id=session_id, embedder=fake_embedder, now=lambda: fixed_now)

    utterance = "팀장이랑 다음에 약속 잡기로 했어"
    calls = [{"name": "add_schedule", "args": {"person": "팀장", "title": "약속"}}]

    result = run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={person.id: 0.95}),
    )

    assert result.pending_question is not None
    assert result.pending_question.kind == "schedule"

    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    assert "9월 26일 저녁 7시" in row.options
    assert "9월 27일 저녁 7시" in row.options

    resume = row.context["resume"]
    assert resume["schedule_options"]["9월 26일 저녁 7시"] == "2026-09-26T19:00:00+09:00"
    assert resume["schedule_options"]["9월 27일 저녁 7시"] == "2026-09-27T19:00:00+09:00"


# ---------------------------------------------------------------------------
# ⑤ 인식 프롬프트의 now -- run_turn 이 넘기는 now 가 +09:00 로 지역화됐다
# ---------------------------------------------------------------------------


class _RecordingProposer:
    """`now` 인자를 기록만 하는 테스트 전용 `Proposer` -- `run_turn` 이
    인식 단계에 넘기는 `now` 가 사용자 시간대로 지역화됐는지 확인한다
    (FIX-005). `FakeProposer` 를 쓰지 않는 이유는 `FakeProposer` 가 표
    조회만 하고 받은 `now` 를 밖으로 드러내지 않기 때문이다."""

    def __init__(self) -> None:
        self.captured: list[datetime] = []

    def propose(self, utterance: str, now: datetime):
        self.captured.append(now)
        return validate_proposal({"tool_calls": []}, tz=now.tzinfo or timezone.utc)


@pytest.mark.dbtest
def test_run_turn_passes_user_timezone_localized_now_to_proposer(db_session, fake_embedder):
    session_id = "tz-u5-propose-now"
    ctx = ToolContext(
        session=db_session,
        session_id=session_id,
        embedder=fake_embedder,
        now=lambda: datetime(2026, 9, 24, 3, 0, 0, tzinfo=timezone.utc),
    )
    proposer = _RecordingProposer()

    run_turn(ctx, "그냥 인사", proposer=proposer, judge=FakeJudge(table={}))

    assert len(proposer.captured) == 1
    now = proposer.captured[0]
    assert now.utcoffset() == timedelta(hours=9)
    assert now.isoformat().endswith("+09:00")

    _, user_text = build_propose_prompt("그냥 인사", now)
    assert "+09:00" in user_text


# ---------------------------------------------------------------------------
# ⑥ APP_TIMEZONE 을 바꾸면 결과도 따라 바뀐다
# ---------------------------------------------------------------------------


def test_user_timezone_changes_with_app_timezone_env():
    assert user_timezone({}).key == "Asia/Seoul"
    assert user_timezone({"APP_TIMEZONE": "Asia/Seoul"}).key == "Asia/Seoul"
    assert user_timezone({"APP_TIMEZONE": "America/New_York"}).key == "America/New_York"


# ---------------------------------------------------------------------------
# ⑦ 잘못된 시간대 이름은 오류를 낸다
# ---------------------------------------------------------------------------


def test_user_timezone_rejects_invalid_name():
    with pytest.raises(InvalidValue):
        user_timezone({"APP_TIMEZONE": "Not/AZone"})
