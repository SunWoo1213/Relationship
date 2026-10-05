"""Refs: P7-push S3.6 S3.1 R12 원칙9 -- U4 판정: `PyWebPushSender`·
`WebPushNotifier`·`notifier_from_env`(01-plan 판정 표 12·14~21행 + R-6
단언 + R-2 부정 확인).

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433)이 필요하다(`dbtest`,
`db_session` 롤백 픽스처) -- `tests/test_briefing_run.py` 와 같은 관례.
모든 행은 **독립**이다(테스트마다 새 인물·일정·구독을 만든다). 발송은
전부 `FakePushSender`(결정 G) 또는 주입한 가짜 발송 함수를 쓰고,
**실제 푸시 서비스로 아무것도 보내지 않는다**(원칙8). `pywebpush.
webpush` 자체는 파일 전체에 기본적으로 "불리면 실패" 픽스처(`_deny_real_
webpush_by_default`, 결정 G, 판정 21행)를 autouse 로 걸어 둔다 -- 이
파일의 어떤 테스트도 `PyWebPushSender()` 기본값 경로(주입 없음)로 실제
라이브러리를 불렀다면 바로 실패한다. R-2 부정 확인 두 테스트만 이
픽스처를 자신의 테스트 안에서 되돌려 "패치가 실제로 그 경로를 잡는지"
자체를 확인한다.

테스트 VAPID 키는 매번 이 파일 안에서 그 자리에서 만든 일회용 키다(결정
G "저장소에 키 문자열을 남기지 않는다") -- 값은 어디에도 출력하지
않는다. `FakePushSender` 기반 테스트는 이 키를 암호화에 실제로 쓰지
않지만(가짜 발송기는 네트워크·암호 라이브러리 없이 동작), "VAPID 설정
하나"라는 모양 자체는 실제 생성 경로로 만든다.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone

import py_vapid
import pytest
import pywebpush
import requests
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from sqlalchemy import select

from app.briefing.compose import FakeBriefingComposer
from app.briefing.run import run_briefings
from app.briefing.types import (
    BRIEFING_TRACE_TOOL_NAME,
    STEP_BRIEFING_ERROR,
    BriefingLine,
    ComposedBriefing,
    Suggestion,
)
from app.db.models import AgentTrace, Person, PushSubscription, Schedule
from app.push.notifier import WebPushNotifier, notifier_from_env
from app.push.sender import PyWebPushSender
from app.push.types import (
    PUSH_TRACE_TOOL_NAME,
    STEP_PUSH_SEND,
    FakePushSender,
    SendResult,
    VapidConfig,
)
from app.tools.context import ToolContext

dbtest = pytest.mark.dbtest
pytestmark = dbtest

_T0 = datetime(2026, 10, 5, 10, 0, 0, tzinfo=timezone.utc)

#: `pywebpush.webpush` 의 진짜 참조(모듈 import 시점, 어떤 테스트도 아직
#: 패치하지 않은 상태) -- R-2 부정 확인 테스트가 자신의 몸 안에서만 이
#: 값으로 되돌려 "패치 없는 기본 경로가 실제로 그 함수를 부른다"를
#: 확인한다.
_REAL_WEBPUSH = pywebpush.webpush


class _PyWebPushPatchMarker(Exception):
    """판정 21행·R-2 전용 표식 예외. 이 클래스 이름이 결과에 나타나면
    "불리면 실패" 픽스처가 실제로 `pywebpush.webpush` 호출을 가로챘다는
    뜻이다."""


def _raise_patch_marker(**_kwargs: object) -> None:
    raise _PyWebPushPatchMarker("이 파일의 기본 픽스처가 실제 발송 경로를 막았다")


@pytest.fixture(autouse=True)
def _deny_real_webpush_by_default(monkeypatch):
    """결정 G·판정 21행 -- 이 파일의 모든 테스트는 기본적으로
    `pywebpush.webpush` 가 불리면 실패하도록 패치해 둔다. 모든 정상
    테스트는 `FakePushSender`/주입한 가짜 함수만 쓰므로 이 패치에 걸릴
    일이 없다 -- 그래도 걸린다면 어딘가 실제 발송 경로가 실수로 살아
    있다는 뜻이므로 바로 실패한다. R-2 부정 확인 두 테스트만 자신의 몸
    안에서 `monkeypatch.setattr(pywebpush, "webpush", _REAL_WEBPUSH)` 로
    되돌린다."""
    monkeypatch.setattr(pywebpush, "webpush", _raise_patch_marker)


# ---------------------------------------------------------------------------
# 헬퍼 (tests/test_briefing_run.py 와 같은 이름 관례)
# ---------------------------------------------------------------------------


def _make_person(db_session, *, user_id: str, display_name: str = "민수") -> Person:
    person = Person(user_id=user_id, display_name=display_name, relation_tag="친구", hierarchy="동")
    db_session.add(person)
    db_session.flush()
    return person


def _make_schedule(
    db_session, person: Person, *, scheduled_at: datetime, title: str = "저녁 약속"
) -> Schedule:
    schedule = Schedule(person_id=person.id, title=title, scheduled_at=scheduled_at)
    db_session.add(schedule)
    db_session.flush()
    return schedule


def _make_subscription(
    db_session, user_id: str, *, endpoint: str, keys: dict[str, str] | None = None
) -> PushSubscription:
    row = PushSubscription(
        user_id=user_id, endpoint=endpoint, keys=keys or {"p256dh": "p", "auth": "a"}
    )
    db_session.add(row)
    db_session.flush()
    return row


def _composed(suggestion_text: str = "고수 없는 식당을 고르세요") -> ComposedBriefing:
    return ComposedBriefing(
        pattern_sentences=[], lines=[], suggestion=Suggestion(text=suggestion_text, basis={})
    )


def _generate_vapid_key_pair() -> tuple[str, str]:
    """테스트 전용 일회용 VAPID 키 쌍을 **그 자리에서** 만든다(결정 G --
    저장소에 키 문자열을 남기지 않는다, 값은 반환만 하고 출력하지
    않는다)."""
    vapid = py_vapid.Vapid()
    vapid.generate_keys()
    private_raw = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    private_b64 = base64.urlsafe_b64encode(private_raw).rstrip(b"=").decode()
    public_raw = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    public_b64 = base64.urlsafe_b64encode(public_raw).rstrip(b"=").decode()
    return public_b64, private_b64


def _vapid() -> VapidConfig:
    public_key, private_key = _generate_vapid_key_pair()
    return VapidConfig(public_key=public_key, private_key=private_key, subject="mailto:u4-test@example.com")


def _trace_rows(db_session) -> list[AgentTrace]:
    return list(
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == PUSH_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_PUSH_SEND)
            .order_by(AgentTrace.id.asc())
        )
        .scalars()
        .all()
    )


class _FakeResponse:
    """`pywebpush.WebPushException(response=...)` 에 넣는 가짜 응답 --
    `status_code` 속성만 있다(실제 `requests.Response` 와 달리 `.text`
    가 없다 -- 우리 매핑 코드가 그 속성을 읽지 않는다는 것 자체를
    구조적으로 보장한다)."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def _send_fn_raising(exc: Exception):
    def _fn(**_kwargs: object):
        raise exc

    return _fn


def _send_fn_success(status_code: int = 201):
    def _fn(**_kwargs: object) -> _FakeResponse:
        return _FakeResponse(status_code)

    return _fn


# ---------------------------------------------------------------------------
# 판정 12행 -- 원문 미포함(원칙7·security §1)
# ---------------------------------------------------------------------------


def test_notify_payload_sent_to_sender_never_contains_raw_utterance(db_session):
    person = _make_person(db_session, user_id="push-u4-row12")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))
    _make_subscription(db_session, person.user_id, endpoint="https://fcm.example.com/row12")

    watched_raw = "민수는 고수를 진짜 싫어하더라 U4원문감시문자열"
    composed = ComposedBriefing(
        pattern_sentences=[{"key": "pattern:conflict", "sentence": f"패턴문장: {watched_raw}"}],
        lines=[BriefingLine(text=watched_raw, basis={"fact_keys": [], "event_ids": []})],
        suggestion=Suggestion(text="고수 없는 식당을 고르세요", basis={}),
    )

    fake_sender = FakePushSender()
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=fake_sender, vapid=_vapid(), now=lambda: _T0
    )

    status = notifier.notify(schedule, composed)

    assert status == "sent"
    assert len(fake_sender.calls) == 1
    dumped = json.dumps(fake_sender.calls[0], ensure_ascii=False)
    assert watched_raw not in dumped
    assert "패턴문장" not in dumped


# ---------------------------------------------------------------------------
# 판정 14행 -- 구독 0건(결정 C)
# ---------------------------------------------------------------------------


def test_notify_no_subscription_sends_nothing_and_records_trace(db_session):
    person = _make_person(db_session, user_id="push-u4-row14")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))

    fake_sender = FakePushSender()
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=fake_sender, vapid=_vapid(), now=lambda: _T0
    )

    status = notifier.notify(schedule, _composed())

    assert status == "no_subscription"
    assert fake_sender.calls == []
    rows = _trace_rows(db_session)
    assert len(rows) == 1
    assert rows[0].output["status"] == "no_subscription"
    assert rows[0].output["results"] == []
    assert rows[0].output["removed"] == []
    assert rows[0].output["payload"] is None
    assert rows[0].output["ttl"] is None


# ---------------------------------------------------------------------------
# 판정 15행 -- 만료 구독(결정 E): 둘 중 하나만 410
# ---------------------------------------------------------------------------


def test_notify_partial_removes_gone_subscription_keeps_other(db_session):
    person = _make_person(db_session, user_id="push-u4-row15")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))
    gone_sub = _make_subscription(db_session, person.user_id, endpoint="https://fcm.example.com/row15-gone")
    ok_sub = _make_subscription(db_session, person.user_id, endpoint="https://fcm.example.com/row15-ok")

    fake_sender = FakePushSender(
        responses={
            gone_sub.endpoint: SendResult("gone", status_code=410),
            ok_sub.endpoint: SendResult("sent", status_code=201),
        }
    )
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=fake_sender, vapid=_vapid(), now=lambda: _T0
    )

    status = notifier.notify(schedule, _composed())

    assert status == "partial"
    remaining = (
        db_session.execute(select(PushSubscription).where(PushSubscription.user_id == person.user_id))
        .scalars()
        .all()
    )
    assert [row.id for row in remaining] == [ok_sub.id]

    rows = _trace_rows(db_session)
    assert rows[-1].output["removed"] == [gone_sub.id]
    assert rows[-1].output["status"] == "partial"


# ---------------------------------------------------------------------------
# 판정 16행 -- 만료 404 도 같음(유일한 구독)
# ---------------------------------------------------------------------------


def test_notify_single_subscription_404_is_removed_and_status_failed(db_session):
    person = _make_person(db_session, user_id="push-u4-row16")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=3))
    sub = _make_subscription(db_session, person.user_id, endpoint="https://fcm.example.com/row16")

    fake_sender = FakePushSender(responses={sub.endpoint: SendResult("gone", status_code=404)})
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=fake_sender, vapid=_vapid(), now=lambda: _T0
    )

    status = notifier.notify(schedule, _composed())

    assert status == "failed"
    remaining = (
        db_session.execute(select(PushSubscription).where(PushSubscription.user_id == person.user_id))
        .scalars()
        .all()
    )
    assert remaining == []
    rows = _trace_rows(db_session)
    assert rows[-1].output["removed"] == [sub.id]


# ---------------------------------------------------------------------------
# 판정 17행 -- 일시 오류(결정 C): briefed_at 유지, briefing_error 0행,
# 재실행해도 재선정 0·생성기 추가 호출 0(run_briefings 와 함께 돌려 확인)
# ---------------------------------------------------------------------------


def test_run_briefings_with_transient_push_failure_keeps_briefed_at_and_does_not_resend(db_session):
    person = _make_person(db_session, user_id="push-u4-row17")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=1))
    sub = _make_subscription(db_session, person.user_id, endpoint="https://fcm.example.com/row17")

    fake_sender = FakePushSender(responses={sub.endpoint: SendResult("failed", status_code=503)})
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=fake_sender, vapid=_vapid(), now=lambda: _T0
    )
    composer = FakeBriefingComposer()
    ctx = ToolContext(session=db_session, session_id="caller:row17", user_id=person.user_id, now=lambda: _T0)

    result = run_briefings(ctx, composer=composer, notifier=notifier, trigger="manual")

    assert [item["schedule_id"] for item in result.briefings] == [schedule.id]
    assert result.briefings[0]["push"] == "failed"
    assert result.errors == 0

    db_session.refresh(schedule)
    assert schedule.briefed_at == _T0  # briefed_at 은 기록됐다(결정 C(i)).

    error_rows = (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.tool_name == BRIEFING_TRACE_TOOL_NAME)
            .where(AgentTrace.step == STEP_BRIEFING_ERROR)
        )
        .scalars()
        .all()
    )
    assert error_rows == []  # briefing_error 0행.
    assert composer.call_count == 1
    assert len(fake_sender.calls) == 1

    # 같은 조건으로 다시 실행해도 재선정 0 · 생성기 추가 호출 0.
    result2 = run_briefings(ctx, composer=composer, notifier=notifier, trigger="manual")
    assert result2.briefings == []
    assert result2.skipped == []
    assert composer.call_count == 1
    assert len(fake_sender.calls) == 1


# ---------------------------------------------------------------------------
# 판정 18행 -- 발송기 예외 매핑 5종. 어느 경우도 예외가 밖으로 나오지
# 않는다(주입한 send_fn 을 직접 호출해도 pytest.raises 없이 통과해야 함).
# ---------------------------------------------------------------------------


def _send(sender: PyWebPushSender, *, endpoint: str = "https://fcm.example.com/row18") -> SendResult:
    return sender.send(
        endpoint=endpoint,
        keys={"p256dh": "p", "auth": "a"},
        payload={"title": "t", "body": "b"},
        vapid_private_key="dummy-private-key-not-real",
        vapid_subject="mailto:u4-test@example.com",
        ttl=60,
        timeout=1.0,
    )


def test_pywebpush_sender_maps_success_to_sent():
    sender = PyWebPushSender(send_fn=_send_fn_success(201))
    result = _send(sender)
    assert result.outcome == "sent"
    assert result.status_code == 201


def test_pywebpush_sender_maps_404_410_to_gone():
    for status_code in (404, 410):
        exc = pywebpush.WebPushException("x", response=_FakeResponse(status_code))
        sender = PyWebPushSender(send_fn=_send_fn_raising(exc))
        result = _send(sender)
        assert result.outcome == "gone"
        assert result.status_code == status_code


def test_pywebpush_sender_maps_other_http_error_to_failed_with_status_preserved():
    exc = pywebpush.WebPushException("x", response=_FakeResponse(500))
    sender = PyWebPushSender(send_fn=_send_fn_raising(exc))
    result = _send(sender)
    assert result.outcome == "failed"
    assert result.status_code == 500


def test_pywebpush_sender_maps_timeout_to_timeout_with_class_name_only():
    exc = requests.exceptions.Timeout("the socket timed out")
    sender = PyWebPushSender(send_fn=_send_fn_raising(exc))
    result = _send(sender)
    assert result.outcome == "timeout"
    assert result.error_class == "Timeout"
    assert result.status_code is None


def test_pywebpush_sender_maps_arbitrary_exception_to_error_with_class_name_only():
    exc = RuntimeError("some unexpected bug")
    sender = PyWebPushSender(send_fn=_send_fn_raising(exc))
    result = _send(sender)
    assert result.outcome == "error"
    assert result.error_class == "RuntimeError"
    assert result.status_code is None


# ---------------------------------------------------------------------------
# 판정 19행 -- 근거 기록(원칙9): push_send trace 전 필드 모양
# 판정 20행 -- 비밀 미기록(security §1, R-8): 가짜 예외 메시지에 감시
# 문자열(엔드포인트·p256dh·auth)을 넣고 trace·SendResult 어디에도 없음
# ---------------------------------------------------------------------------


def test_notify_records_full_trace_shape_without_leaking_secrets_in_exception_message(db_session):
    person = _make_person(db_session, user_id="push-u4-row19")
    schedule = _make_schedule(db_session, person, scheduled_at=_T0 + timedelta(hours=2))

    watched_endpoint = "https://fcm.example.com/SECRET-row19-endpoint"
    watched_p256dh = "SECRET-row19-p256dh-value"
    watched_auth = "SECRET-row19-auth-value"
    sub = _make_subscription(
        db_session,
        person.user_id,
        endpoint=watched_endpoint,
        keys={"p256dh": watched_p256dh, "auth": watched_auth},
    )

    # R-8 -- 발송 라이브러리의 예외 메시지에는 응답 본문·엔드포인트가
    # 섞일 수 있다(WebPushException.__str__). 가짜 예외 메시지에 감시
    # 문자열을 직접 넣어, 매핑 코드가 `exc.status_code` 속성만 읽고
    # `str(exc)` 는 읽지 않는지를 실제로 증명한다.
    def _leaky_send_fn(**_kwargs: object):
        raise pywebpush.WebPushException(
            f"Push failed for endpoint {watched_endpoint} with key {watched_p256dh} auth {watched_auth}",
            response=_FakeResponse(500),
        )

    sender = PyWebPushSender(send_fn=_leaky_send_fn)
    notifier = WebPushNotifier(
        session=db_session, user_id=person.user_id, sender=sender, vapid=_vapid(), now=lambda: _T0
    )

    status = notifier.notify(schedule, _composed())

    assert status == "failed"
    rows = _trace_rows(db_session)
    assert len(rows) == 1
    row = rows[0]

    # 판정 19행 -- 전 필드 모양.
    assert row.tool_name == PUSH_TRACE_TOOL_NAME
    assert row.step == STEP_PUSH_SEND
    assert row.input == {
        "schedule_id": schedule.id,
        "person_id": person.id,
        "subscription_ids": [sub.id],
    }
    assert row.output["schedule_id"] == schedule.id
    assert row.output["status"] == "failed"
    assert row.output["results"] == [
        {"subscription_id": sub.id, "outcome": "failed", "status_code": 500}
    ]
    assert row.output["removed"] == []
    assert set(row.output["payload"].keys()) == {"title", "body"}
    assert row.output["ttl"] is not None
    assert row.tokens_in == 0
    assert row.tokens_out == 0

    # 판정 20행 -- 비밀 미기록. trace 전체(JSON)에 감시 문자열이 없다.
    dumped = json.dumps({"input": row.input, "output": row.output}, ensure_ascii=False)
    assert watched_endpoint not in dumped
    assert watched_p256dh not in dumped
    assert watched_auth not in dumped


def test_pywebpush_sender_exception_message_secrets_not_in_send_result(db_session):
    """R-8 -- `SendResult` 자체(trace 를 거치지 않고도)에 비밀이 없다."""
    watched_endpoint = "https://fcm.example.com/SECRET-sendresult-endpoint"
    watched_p256dh = "SECRET-sendresult-p256dh"

    exc = pywebpush.WebPushException(
        f"Push failed for endpoint {watched_endpoint} with key {watched_p256dh}",
        response=_FakeResponse(500),
    )
    sender = PyWebPushSender(send_fn=_send_fn_raising(exc))
    result = _send(sender, endpoint=watched_endpoint)

    dumped = json.dumps(result.to_dict(), ensure_ascii=False)
    assert watched_endpoint not in dumped
    assert watched_p256dh not in dumped


# ---------------------------------------------------------------------------
# R-6(security §5) -- 알림기 자신도 인물의 user_id 경계를 확인한다.
# 보완(사용자 결정 2026-10-05): assert -> 명시적 if·fail-closed. 예전에는
# AssertionError 를 올렸으나(아래 옛 기대였던 pytest.raises(AssertionError)),
# 그러면 run_briefings 의 세이브포인트가 롤백돼 briefed_at 이 기록되지
# 않고 다음 주기에 같은 일정이 재선정돼 LLM 생성이 반복된다. 지금은
# 예외 없이 "failed" 를 돌려주고 그 이유를 trace 에 남긴다.
# ---------------------------------------------------------------------------


def test_notify_owner_mismatch_is_fail_closed_without_raising(db_session):
    other_person = _make_person(db_session, user_id="push-u4-r6-other")
    schedule = _make_schedule(db_session, other_person, scheduled_at=_T0 + timedelta(hours=1))

    fake_sender = FakePushSender()
    notifier = WebPushNotifier(
        session=db_session,
        user_id="push-u4-r6-caller",
        sender=fake_sender,
        vapid=_vapid(),
        now=lambda: _T0,
    )

    status = notifier.notify(schedule, _composed())

    assert status == "failed"
    assert fake_sender.calls == []  # 발송기 호출 0.

    remaining = (
        db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == other_person.user_id)
        )
        .scalars()
        .all()
    )
    assert remaining == []  # 애초에 구독이 없었고, 삭제 시도도 없다.

    rows = _trace_rows(db_session)
    assert len(rows) == 1
    assert rows[0].output["status"] == "failed"
    assert rows[0].output["reason"] == "owner_mismatch"
    assert rows[0].output["results"] == []
    assert rows[0].output["removed"] == []
    assert rows[0].output["payload"] is None
    assert rows[0].output["ttl"] is None
    # 서로 다른 user_id 값 자체는 trace 어디에도 없다 -- "달랐다"는
    # 사실만 남는다(security §1).
    dumped = json.dumps({"input": rows[0].input, "output": rows[0].output}, ensure_ascii=False)
    assert other_person.user_id not in dumped
    assert "push-u4-r6-caller" not in dumped


def test_run_briefings_with_owner_mismatch_records_briefed_at_and_does_not_resend(db_session):
    """row17(일시 오류) 과 같은 패턴 -- owner_mismatch 도 예외를 올리지
    않으므로 briefed_at 이 기록되고, 같은 조건으로 재실행해도 재선정
    0·생성기 추가 호출 0 이다(롤백 반복이 없다는 것의 증명)."""

    other_person = _make_person(db_session, user_id="push-u4-r6run-other")
    schedule = _make_schedule(db_session, other_person, scheduled_at=_T0 + timedelta(hours=1))

    fake_sender = FakePushSender()
    notifier = WebPushNotifier(
        session=db_session,
        user_id="push-u4-r6run-caller",
        sender=fake_sender,
        vapid=_vapid(),
        now=lambda: _T0,
    )
    composer = FakeBriefingComposer()
    # ctx.user_id 는 schedule 의 소유 인물(other_person)과 일치시켜야
    # select_due_schedules() 가 이 일정을 고른다 -- notifier 쪽 user_id
    # 만 다르게 둬서 R-6 불일치를 알림기 내부에서만 재현한다.
    ctx = ToolContext(
        session=db_session, session_id="caller:r6run", user_id=other_person.user_id, now=lambda: _T0
    )

    result = run_briefings(ctx, composer=composer, notifier=notifier, trigger="manual")

    assert [item["schedule_id"] for item in result.briefings] == [schedule.id]
    assert result.briefings[0]["push"] == "failed"
    assert result.errors == 0

    db_session.refresh(schedule)
    assert schedule.briefed_at == _T0  # briefed_at 은 기록됐다(예외 없음).

    assert composer.call_count == 1
    assert len(fake_sender.calls) == 0

    # 같은 조건으로 다시 실행해도 재선정 0 · 생성기 추가 호출 0.
    result2 = run_briefings(ctx, composer=composer, notifier=notifier, trigger="manual")
    assert result2.briefings == []
    assert result2.skipped == []
    assert composer.call_count == 1
    assert len(fake_sender.calls) == 0


# ---------------------------------------------------------------------------
# 판정 21행(결정 G) -- 네트워크 0. 위의 모든 테스트가 autouse 픽스처
# (`_deny_real_webpush_by_default`) 아래에서도 전부 통과한다는 것 자체가
# "실제 발송 함수 호출 0"의 증거다. 아래 두 테스트는 R-2(그 패치가 실제로
# 기본 경로를 잡는지 부정 확인)를 직접 증명한다.
# ---------------------------------------------------------------------------


def test_r2_default_sender_path_is_actually_intercepted_by_the_fixture():
    """픽스처가 켜진 채(이 파일 기본값) `PyWebPushSender()` 를 **주입 없이**
    부르면 `_PyWebPushPatchMarker` 로 잡힌다 -- `app/push/sender.py` 가
    `pywebpush.webpush` 를 호출 시점에 속성으로 찾는다는 것(R-2)의
    양성 확인."""
    sender = PyWebPushSender()  # send_fn 주입 없음 -- 기본값 경로.
    result = _send(sender)

    assert result.outcome == "error"
    assert result.error_class == "_PyWebPushPatchMarker"


def test_r2_negative_check_unpatched_default_path_really_calls_the_library(monkeypatch):
    """R-2 부정 확인 -- 픽스처를 이 테스트 안에서만 되돌리면(`pywebpush.
    webpush` 를 진짜 함수로 복원), 주입 없는 기본 경로가 **실제로 그
    함수를 호출**한다는 것을 보인다. 진짜 키가 아닌 문자열
    (`vapid_private_key="dummy-private-key-not-real"`)을 쓰므로 그
    라이브러리는 서명 단계에서 곧바로 실패한다(네트워크 접속 이전 --
    `requests` 세션이 열리지 않는다, security §4 "외부 전송 0" 과
    충돌하지 않는다). 결과의 `error_class` 가 위 양성 테스트의
    `_PyWebPushPatchMarker` 와 **다르면** 진짜 라이브러리 코드가 실행된
    것이다(이름이 같았다면 import 시점에 이름이 먼저 묶여 패치가 전혀
    걸리지 않는 버그였다는 뜻)."""
    monkeypatch.setattr(pywebpush, "webpush", _REAL_WEBPUSH)

    sender = PyWebPushSender()  # send_fn 주입 없음 -- 기본값 경로.
    result = _send(sender)

    assert result.outcome in ("error", "failed", "timeout")
    assert result.error_class != "_PyWebPushPatchMarker"


# ---------------------------------------------------------------------------
# notifier_from_env -- 키 전무/반쪽/전부(01-plan U4 산출물 절)
# ---------------------------------------------------------------------------


def test_notifier_from_env_returns_null_notifier_when_no_keys(db_session):
    from app.briefing.types import NullNotifier

    env = {"VAPID_PUBLIC_KEY": "", "VAPID_PRIVATE_KEY": "", "VAPID_SUBJECT": ""}
    notifier = notifier_from_env(db_session, "push-u4-env-none", lambda: _T0, env=env)

    assert isinstance(notifier, NullNotifier)
    assert notifier.notify(object(), _composed()) == "not_configured"


def test_notifier_from_env_returns_misconfigured_notifier_when_partial(db_session):
    from app.push.notifier import MisconfiguredNotifier

    env = {
        "VAPID_PUBLIC_KEY": "only-public-key",
        "VAPID_PRIVATE_KEY": "",
        "VAPID_SUBJECT": "",
    }
    notifier = notifier_from_env(db_session, "push-u4-env-partial", lambda: _T0, env=env)

    assert isinstance(notifier, MisconfiguredNotifier)
    assert notifier.notify(object(), _composed()) == "misconfigured"


def test_notifier_from_env_returns_web_push_notifier_when_fully_configured(db_session):
    public_key, private_key = _generate_vapid_key_pair()
    env = {
        "VAPID_PUBLIC_KEY": public_key,
        "VAPID_PRIVATE_KEY": private_key,
        "VAPID_SUBJECT": "mailto:u4-test@example.com",
    }
    notifier = notifier_from_env(db_session, "push-u4-env-full", lambda: _T0, env=env)

    assert isinstance(notifier, WebPushNotifier)
    assert isinstance(notifier.sender, PyWebPushSender)
    assert notifier.vapid.private_key == private_key
