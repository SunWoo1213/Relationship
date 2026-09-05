"""Refs: P2-tools R7 D1 D2 S3.4 -- `ask_user`/`answer_question`/`question_status`
저장 규약 + D1 왕복(`create_person` 과의 맞물림) + D2 동기 대기 없음.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`)를
쓴다(01-plan 결정8). `ctx.now` 를 주입해 24h 만료 경계를 결정적으로 만든다
(01-plan 리스크 "시간 의존 테스트").
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db.models import AgentTrace, PendingQuestion
from app.settings import QUESTION_TTL
from app.tools.context import ToolContext
from app.tools.persons import create_person
from app.tools.questions import (
    QUESTION_STATUSES,
    ask_user,
    answer_question,
    list_pending,
    question_status,
)
from app.tools.types import (
    AFFIRMATIVE_KEY,
    ConfirmationRequired,
    InvalidValue,
    PendingQuestionOut,
    QuestionNotAnswerable,
    QuestionNotFound,
)

pytestmark = pytest.mark.dbtest

_BASE_TIME = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _ctx(
    db_session,
    *,
    session_id: str = "q-test",
    now=None,
    confirmed_question_id: int | None = None,
) -> ToolContext:
    kwargs = {}
    if now is not None:
        kwargs["now"] = now
    return ToolContext(
        session=db_session,
        session_id=session_id,
        confirmed_question_id=confirmed_question_id,
        **kwargs,
    )


def _make_question_row(
    db_session,
    *,
    session_id: str = "q-row-test",
    kind: str = "new_person",
    question: str = "저장할까요?",
    options: list[str] | None = None,
    context: dict | None = None,
    answer: str | None = None,
    answered_at: datetime | None = None,
    created_at: datetime = _BASE_TIME,
) -> PendingQuestion:
    """`question_status`/`answer_question` 경계 테스트용 -- `created_at` 을
    명시해 24h 만료 경계를 결정적으로 만든다(서버 기본값 대신 직접 지정)."""
    if options is None:
        options = ["예", "아니오"]
    if context is None:
        context = {AFFIRMATIVE_KEY: ["예"]}
    row = PendingQuestion(
        session_id=session_id,
        kind=kind,
        question=question,
        options=options,
        context=context,
        answer=answer,
        answered_at=answered_at,
        created_at=created_at,
    )
    db_session.add(row)
    db_session.flush()
    return row


# ---------------------------------------------------------------------------
# 수용 기준 직접 증거: ask_user 호출 → pending_questions 행 존재.
# ---------------------------------------------------------------------------


def test_ask_user_stores_row_and_returns_pending_status(db_session):
    ctx = _ctx(db_session, session_id="evidence-session")

    result = ask_user(
        ctx,
        kind="new_person",
        question="이 사람을 기억해둘까요?",
        options=["응, 기억해줘", "아니, 됐어"],
        context={AFFIRMATIVE_KEY: ["응, 기억해줘"]},
    )

    assert isinstance(result, PendingQuestionOut)
    assert result.status == "pending"

    row = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == result.question_id)
    ).scalar_one()
    assert row.id == result.question_id
    assert row.session_id == "evidence-session"
    assert row.kind == "new_person"
    assert row.question == "이 사람을 기억해둘까요?"
    assert row.options == ["응, 기억해줘", "아니, 됐어"]
    assert row.context == {AFFIRMATIVE_KEY: ["응, 기억해줘"]}
    assert row.answered_at is None


# ---------------------------------------------------------------------------
# ask_user -- kind 3종 성공 + 값 집합 검증.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kind", "context"),
    [
        ("identity", {AFFIRMATIVE_KEY: ["네, 맞아요"]}),
        ("new_person", {AFFIRMATIVE_KEY: ["기억해줘"]}),
        ("schedule", {}),
    ],
)
def test_ask_user_succeeds_for_all_three_kinds(db_session, kind, context):
    assert kind in ("identity", "new_person", "schedule")
    ctx = _ctx(db_session, session_id=f"kind-{kind}")

    result = ask_user(
        ctx,
        kind=kind,
        question="질문",
        options=["네, 맞아요", "기억해줘", "예", "아니오"],
        context=context,
    )

    assert result.kind == kind
    assert result.status == "pending"


def test_ask_user_invalid_kind_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(ctx, kind="unknown_kind", question="질문", options=["예"], context={})


def test_ask_user_empty_question_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(ctx, kind="schedule", question="   ", options=["예", "아니오"], context={})


def test_ask_user_empty_options_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(ctx, kind="schedule", question="질문", options=[], context={})


def test_ask_user_duplicate_options_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(
            ctx, kind="schedule", question="질문", options=["예", "예"], context={}
        )


# ---------------------------------------------------------------------------
# 긍정 답 규약(F-b97a06) -- identity/new_person 전용.
# ---------------------------------------------------------------------------


def test_ask_user_identity_without_affirmative_options_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(ctx, kind="identity", question="질문", options=["예", "아니오"], context={})


def test_ask_user_new_person_with_empty_affirmative_list_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(
            ctx,
            kind="new_person",
            question="질문",
            options=["예", "아니오"],
            context={AFFIRMATIVE_KEY: []},
        )


def test_ask_user_affirmative_options_outside_options_raises(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(
            ctx,
            kind="new_person",
            question="질문",
            options=["예", "아니오"],
            context={AFFIRMATIVE_KEY: ["전혀 다른 값"]},
        )


def test_ask_user_schedule_without_affirmative_options_succeeds(db_session):
    ctx = _ctx(db_session)
    result = ask_user(
        ctx, kind="schedule", question="일정 확인할까요?", options=["예", "아니오"], context={}
    )
    assert result.status == "pending"


# ---------------------------------------------------------------------------
# context 방어(S3.4 "비밀·전체 대화 이력 저장 금지" 최소 방어) + 절단 + 왕복.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "secret_key", ["password", "api_key", "token", "secret", "authorization", "API_KEY"]
)
def test_ask_user_context_with_secret_like_key_raises(db_session, secret_key):
    ctx = _ctx(db_session)
    with pytest.raises(InvalidValue):
        ask_user(
            ctx,
            kind="schedule",
            question="질문",
            options=["예", "아니오"],
            context={secret_key: "x"},
        )


def test_ask_user_context_long_string_is_truncated(db_session):
    ctx = _ctx(db_session, session_id="truncate-test")
    long_value = "가" * 3000

    result = ask_user(
        ctx,
        kind="schedule",
        question="질문",
        options=["예", "아니오"],
        context={"note": long_value},
    )

    row = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == result.question_id)
    ).scalar_one()
    stored_note = row.context["note"]
    assert len(stored_note) < len(long_value)
    assert "truncated" in stored_note


def test_ask_user_context_roundtrips_through_jsonb(db_session):
    ctx = _ctx(db_session, session_id="roundtrip-test")
    context = {
        "utterance": "어제 팀장님이랑 저녁 먹었어",
        "candidate_ids": [1, 2, 3],
        "confidence_breakdown": {"s_llm": 0.6, "s_emb": 0.4, "s_rule": 0.5},
    }

    result = ask_user(
        ctx, kind="identity", question="질문", options=["네", "아니오"],
        context={**context, AFFIRMATIVE_KEY: ["네"]},
    )

    db_session.expire_all()
    row = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == result.question_id)
    ).scalar_one()
    assert row.context == {**context, AFFIRMATIVE_KEY: ["네"]}


# ---------------------------------------------------------------------------
# question_status -- 순수 파생 함수.
# ---------------------------------------------------------------------------


def test_question_status_answered_takes_priority(db_session):
    row = _make_question_row(
        db_session,
        created_at=_BASE_TIME,
        answer="예",
        answered_at=_BASE_TIME + timedelta(hours=100),
    )
    assert question_status(row, _BASE_TIME + timedelta(days=365)) == "answered"


def test_question_status_pending_just_before_24h(db_session):
    row = _make_question_row(db_session, created_at=_BASE_TIME)
    almost_expired = _BASE_TIME + QUESTION_TTL - timedelta(seconds=1)
    assert question_status(row, almost_expired) == "pending"


def test_question_status_expired_exactly_at_24h_and_after(db_session):
    row = _make_question_row(db_session, created_at=_BASE_TIME)
    exactly_at_ttl = _BASE_TIME + QUESTION_TTL
    after_ttl = _BASE_TIME + QUESTION_TTL + timedelta(seconds=1)
    assert question_status(row, exactly_at_ttl) == "expired"
    assert question_status(row, after_ttl) == "expired"


def test_question_status_naive_now_raises_invalid_value(db_session):
    row = _make_question_row(db_session, created_at=_BASE_TIME)
    with pytest.raises(InvalidValue):
        question_status(row, datetime(2026, 1, 2, 12, 0, 0))  # naive


def test_question_statuses_constant_matches_three_values():
    assert set(QUESTION_STATUSES) == {"pending", "answered", "expired"}


# ---------------------------------------------------------------------------
# answer_question.
# ---------------------------------------------------------------------------


def test_answer_question_success_records_answer_and_answered_at(db_session):
    row = _make_question_row(
        db_session, created_at=_BASE_TIME, options=["예", "아니오"]
    )
    fixed_now = _BASE_TIME + timedelta(hours=1)
    ctx = _ctx(db_session, now=lambda: fixed_now)

    result = answer_question(ctx, row.id, "예")

    assert result.status == "answered"
    db_session.expire_all()
    refreshed = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == row.id)
    ).scalar_one()
    assert refreshed.answer == "예"
    assert refreshed.answered_at == fixed_now


def test_answer_question_already_answered_raises(db_session):
    row = _make_question_row(
        db_session,
        created_at=_BASE_TIME,
        answer="예",
        answered_at=_BASE_TIME + timedelta(minutes=5),
    )
    ctx = _ctx(db_session, now=lambda: _BASE_TIME + timedelta(hours=1))

    with pytest.raises(QuestionNotAnswerable) as excinfo:
        answer_question(ctx, row.id, "아니오")
    assert excinfo.value.code == "already_answered"


def test_answer_question_expired_raises_and_keeps_answered_at_null(db_session):
    row = _make_question_row(db_session, created_at=_BASE_TIME)
    after_ttl = _BASE_TIME + QUESTION_TTL + timedelta(minutes=1)
    ctx = _ctx(db_session, now=lambda: after_ttl)

    with pytest.raises(QuestionNotAnswerable) as excinfo:
        answer_question(ctx, row.id, "예")
    assert excinfo.value.code == "expired"

    db_session.expire_all()
    refreshed = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == row.id)
    ).scalar_one()
    assert refreshed.answered_at is None
    assert refreshed.answer is None


def test_answer_question_option_outside_stored_options_raises_and_row_unchanged(db_session):
    row = _make_question_row(
        db_session, created_at=_BASE_TIME, options=["예", "아니오"]
    )
    ctx = _ctx(db_session, now=lambda: _BASE_TIME + timedelta(minutes=1))

    with pytest.raises(InvalidValue):
        answer_question(ctx, row.id, "전혀 다른 답")

    db_session.expire_all()
    refreshed = db_session.execute(
        select(PendingQuestion).where(PendingQuestion.id == row.id)
    ).scalar_one()
    assert refreshed.answer is None
    assert refreshed.answered_at is None


def test_answer_question_nonexistent_id_raises_question_not_found(db_session):
    ctx = _ctx(db_session)
    with pytest.raises(QuestionNotFound):
        answer_question(ctx, 999_999_999, "예")


def test_ask_user_and_answer_question_each_write_one_trace_row(db_session):
    ctx = _ctx(db_session, session_id="trace-questions-1")

    result = ask_user(
        ctx, kind="schedule", question="질문", options=["예", "아니오"], context={}
    )
    answer_question(ctx, result.question_id, "예")

    rows = list(
        db_session.execute(
            select(AgentTrace).where(AgentTrace.session_id == "trace-questions-1")
        ).scalars()
    )
    assert len(rows) == 2
    tool_names = {row.tool_name for row in rows}
    assert tool_names == {"ask_user", "answer_question"}
    for row in rows:
        assert row.step == "tool_call"
        assert row.tokens_in == 0
        assert row.tokens_out == 0


# ---------------------------------------------------------------------------
# D1 왕복 -- ask_user → answer_question → create_person.
# ---------------------------------------------------------------------------


def test_d1_roundtrip_affirmative_answer_allows_create_person(db_session):
    ctx = _ctx(db_session, session_id="d1-roundtrip-yes")

    asked = ask_user(
        ctx,
        kind="new_person",
        question="새 인물로 등록할까요?",
        options=["새 인물로 등록", "기존 인물"],
        context={AFFIRMATIVE_KEY: ["새 인물로 등록"]},
    )
    answer_question(ctx, asked.question_id, "새 인물로 등록")

    create_ctx = _ctx(
        db_session, session_id="d1-roundtrip-yes", confirmed_question_id=asked.question_id
    )
    result = create_person(create_ctx, "김철수", ["팀장"], "직장", "상")
    assert result.display_name == "김철수"


def test_d1_roundtrip_negative_answer_blocks_create_person(db_session):
    ctx = _ctx(db_session, session_id="d1-roundtrip-no")

    asked = ask_user(
        ctx,
        kind="new_person",
        question="새 인물로 등록할까요?",
        options=["새 인물로 등록", "기존 인물"],
        context={AFFIRMATIVE_KEY: ["새 인물로 등록"]},
    )
    answer_question(ctx, asked.question_id, "기존 인물")

    create_ctx = _ctx(
        db_session, session_id="d1-roundtrip-no", confirmed_question_id=asked.question_id
    )
    with pytest.raises(ConfirmationRequired) as excinfo:
        create_person(create_ctx, "김철수", ["팀장"], "직장", "상")
    assert excinfo.value.reason == "not_affirmative"


# ---------------------------------------------------------------------------
# D2 -- 동기 대기 없음.
# ---------------------------------------------------------------------------


def test_ask_user_never_calls_time_sleep(db_session, monkeypatch):
    def _boom(*args, **kwargs):
        raise AssertionError("ask_user must not call time.sleep (D2)")

    monkeypatch.setattr(time, "sleep", _boom)
    ctx = _ctx(db_session, session_id="no-sleep-test")

    result = ask_user(
        ctx, kind="schedule", question="질문", options=["예", "아니오"], context={}
    )
    assert result.status == "pending"


# ---------------------------------------------------------------------------
# list_pending -- 칩용 조회 보조(툴 7종 밖, @traced 없음).
# ---------------------------------------------------------------------------


def test_list_pending_excludes_answered_and_expired(db_session):
    session_id = "list-pending-test"
    pending_row = _make_question_row(
        db_session, session_id=session_id, created_at=_BASE_TIME, question="대기중"
    )
    _make_question_row(
        db_session,
        session_id=session_id,
        created_at=_BASE_TIME,
        question="답변됨",
        answer="예",
        answered_at=_BASE_TIME + timedelta(minutes=1),
    )
    _make_question_row(
        db_session,
        session_id=session_id,
        created_at=_BASE_TIME - QUESTION_TTL - timedelta(hours=1),
        question="만료됨",
    )
    ctx = _ctx(db_session, session_id=session_id, now=lambda: _BASE_TIME + timedelta(minutes=1))

    result = list_pending(ctx)

    assert len(result) == 1
    assert result[0].question_id == pending_row.id
    assert result[0].question == "대기중"
