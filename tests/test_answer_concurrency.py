"""Refs: FIX-019 P5-loop S3.4 D2 원칙1 -- 같은 `pending_questions` 행에
동시에 답이 와도 재개는 한 번만 돈다.

증상(FIX-019.md): `answer_question()` 이 `ctx.session.get(PendingQuestion,
question_id)` 로 **잠금 없이** 읽는다. 두 요청이 거의 동시에 오면 둘 다
`answered_at IS NULL` 을 읽고 둘 다 통과해 `POST /answers/{id}` 가 저장된
context 로 **루프 재개를 두 번** 돈다 -- 순차 요청에서만 성립하던
"재개 최대 1회"(결정 J)가 동시 요청에서는 깨진다.

(a) 툴 수준: 커넥션 둘(`db_engine` 직접 커밋, `tests/test_briefing_select.py`
의 `test_select_due_schedules_concurrent_sessions_skip_locked` 패턴)로 A 가
`answer_question()` 을 호출해 행을 잠근 채 아직 커밋하지 않고 있는 동안
B 를 별도 스레드에서 호출한다. 수정 전(잠금 없음)에는 B 가 A 의 커밋을
기다리지 않고 곧바로 통과한다 -- 그 자체가 결함 재현이다. 수정 후
(`with_for_update=True`)에는 B 가 A 의 커밋까지 블로킹되고, 커밋 후에는
최신(answered) 행을 읽어 `QuestionNotAnswerable("already_answered")` 로
끝난다.

(b) API 수준: `POST /answers/{question_id}` 두 요청을 스레드 둘로 실제
동시에 보낸다. `app.api.routes.answer_question`/`resume_turn` 을 얇게
감싸 A 가 행을 잠근 뒤(커밋 전) B 를 시작하고, B 가 A 의 잠금을 실제로
기다리는지(즉시 끝나지 않는지) 먼저 확인한 뒤 A 를 풀어 준다 -- 정확히
하나는 200, 하나는 409 여야 하고, 재개 로직(`resume_turn`)은 정확히
1회만 불려야 한다(가짜 제안기 불필요 -- schedule 질문은 재개 중
`resolve_mentions()` 가 빈 언급 목록을 받아 judge/proposer 를 아예 부르지
않는다, `app/agent/loop.py::resume_turn` "schedule" 절 참고).

두 테스트 모두 `db_session`(바깥 트랜잭션 + 롤백)이 아니라 `db_engine` 으로
직접 커밋한다 -- 잠금 경쟁은 커밋되지 않은 행으로는 재현할 수 없다(위
briefing 테스트의 주석과 같은 이유, R-1). 끝에서 이 테스트가 만든 행만
지운다(테이블 전체 삭제·TRUNCATE 금지).
"""

from __future__ import annotations

import threading
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

import app.api.routes as routes_module
from app.agent.types import SCHEDULE_UNKNOWN_OPTION
from app.db.models import PendingQuestion, Person, Schedule
from app.main import create_app
from app.settings import app_user_id
from app.tools.context import ToolContext
from app.tools.questions import answer_question, ask_user
from app.tools.types import QuestionNotAnswerable

dbtest = pytest.mark.dbtest
pytestmark = dbtest

#: 스레드 대기 상한(초) -- 교착·무한 대기를 막는다. A 는 항상 이 테스트
#: 코드 자신이 명시적으로 풀어 주므로(Postgres 잠금 타임아웃에 기대지
#: 않는다), 이 값을 넘기면 설계가 잘못된 것이지 느린 환경 탓이 아니다.
_WAIT_TIMEOUT = 5.0

_SCHEDULE_LABEL = "내일 저녁 7시"
_SCHEDULE_ISO = "2026-10-06T19:00:00+09:00"


def _make_person_and_schedule_question(engine) -> tuple[int, int]:
    """커밋된 인물 1건 + `schedule` 질문 1건을 만든다(이미 답으로 확정된
    인물을 가리키는 `add_schedule` 제안 하나만 들고 있다 -- 재개가 판정
    없이 `add_schedule` 만 부르는 가장 단순한 경로, 모듈 docstring
    참고). 반환값은 `(person_id, question_id)`.

    `user_id=app_user_id()`(고정값, 기본 `"local"`) -- (b) API 수준 테스트는
    `POST /answers/{id}` 가 실제로 타는 `build_ctx()` 를 그대로 쓰고,
    그 함수는 `ctx.user_id` 를 항상 `app_user_id()` 로 고정한다(단일
    사용자 제품 전제, `app/api/deps.py` 참고). 여기서 임의의 `user_id` 를
    쓰면 `add_schedule` 의 소유권 검사(security.md §5 격리)가
    `PersonNotFound` 로 막아 재개 자체가 실패한다 -- (a)/(b) 가 같은
    헬퍼를 쓰므로 둘 다 이 고정값을 쓴다. 정리(`_cleanup`)는 `user_id`
    가 아니라 이 함수가 돌려준 `person_id`/`question_id` 로 지정 삭제한다
    (같은 고정 `user_id` 를 쓰는 다른 테스트 데이터를 건드리지 않는다)."""
    setup_session = Session(bind=engine)
    try:
        person = Person(
            user_id=app_user_id(),
            display_name="동시성테스트",
            relation_tag="친구",
            hierarchy="동",
        )
        setup_session.add(person)
        setup_session.flush()

        ctx = ToolContext(
            session=setup_session, session_id=f"concurrency-setup-{uuid.uuid4().hex}"
        )
        asked = ask_user(
            ctx,
            kind="schedule",
            question="약속, 언제로 기억할까요?",
            options=[_SCHEDULE_LABEL, SCHEDULE_UNKNOWN_OPTION],
            context={
                "utterance": "약속 잡기로 했어",
                "resume": {
                    "pending_calls": [
                        {
                            "index": 0,
                            "name": "add_schedule",
                            "args": {"person": "동시성테스트", "title": "약속"},
                        }
                    ],
                    "schedule": {
                        "person_id": person.id,
                        "title": "약속",
                        "call_index": 0,
                    },
                    "schedule_options": {_SCHEDULE_LABEL: _SCHEDULE_ISO},
                },
            },
        )
        setup_session.commit()
        return person.id, asked.question_id
    finally:
        setup_session.close()


def _cleanup(engine, *, person_id: int, question_id: int) -> None:
    """이 테스트가 만든 행만 **지정 ID** 로 지운다(person_id/question_id 는
    `_make_person_and_schedule_question` 이 돌려준 값 -- 여러 테스트가
    같은 고정 `user_id=app_user_id()` 를 공유하므로 `user_id` 로 범위를
    좁히면 다른 테스트 데이터까지 지울 수 있다, 테이블 전체 삭제 금지)."""
    cleanup = Session(bind=engine)
    try:
        cleanup.execute(delete(Schedule).where(Schedule.person_id == person_id))
        cleanup.execute(delete(PendingQuestion).where(PendingQuestion.id == question_id))
        cleanup.execute(delete(Person).where(Person.id == person_id))
        cleanup.commit()

        remaining = cleanup.execute(
            select(Person).where(Person.id == person_id)
        ).scalars().all()
        assert remaining == []
    finally:
        cleanup.close()


# ---------------------------------------------------------------------------
# (a) 툴 수준 -- answer_question() 자체의 잠금 경쟁
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_answer_question_second_connection_sees_already_answered(db_engine) -> None:
    """A 가 `answer_question()` 으로 행을 잠근 채(FOR UPDATE, 커밋 전) 들고
    있는 동안 B 를 별도 스레드에서 부른다. 수정 전에는 B 가 A 의 커밋을
    기다리지 않고 곧바로 통과한다(결함 재현 -- 아래 두 `assert
    thread_b.is_alive()` 가 실패로 그것을 드러낸다). 수정 후에는 B 가
    블로킹됐다가 A 커밋 뒤 `QuestionNotAnswerable("already_answered")`
    로 끝난다."""
    person_id, question_id = _make_person_and_schedule_question(db_engine)

    conn_a = db_engine.connect()
    conn_b = db_engine.connect()
    session_a = Session(bind=conn_a)
    session_b = Session(bind=conn_b)
    try:
        session_a.begin()
        ctx_a = ToolContext(session=session_a, session_id="answer-concurrency-tool-a")
        result_a = answer_question(ctx_a, question_id, _SCHEDULE_LABEL)
        assert result_a.status == "answered"
        # A 는 행을 잠근 채(with_for_update) 아직 커밋하지 않는다.

        session_b.begin()
        ctx_b = ToolContext(session=session_b, session_id="answer-concurrency-tool-b")

        result_holder: dict[str, object] = {}

        def _call_b() -> None:
            try:
                answer_question(ctx_b, question_id, _SCHEDULE_LABEL)
            except Exception as exc:  # noqa: BLE001 -- 스레드 경계로 예외를 넘긴다
                result_holder["error"] = exc
            else:
                result_holder["ok"] = True

        thread_b = threading.Thread(target=_call_b)
        thread_b.start()
        # A 가 커밋하기 전에는 B 가 FOR UPDATE 대기로 블로킹돼 있어야
        # 한다 -- 수정 전 코드는 잠금이 없어 여기서 곧바로 끝나 버린다
        # (결함 재현).
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 잠금을 기다리지 않고 곧바로 끝났다 -- "
            "answer_question() 이 아직 with_for_update 없이 읽는다(FIX-019 결함)"
        )

        session_a.commit()

        thread_b.join(timeout=_WAIT_TIMEOUT)
        assert not thread_b.is_alive(), "B 가 A 커밋 후에도 끝나지 않았다"

        assert "error" in result_holder, "B 가 already_answered 없이 통과했다(오병합 경로 재현)"
        error = result_holder["error"]
        assert isinstance(error, QuestionNotAnswerable)
        assert error.code == "already_answered"

        session_b.rollback()
    finally:
        session_a.close()
        session_b.close()
        conn_a.close()
        conn_b.close()
        _cleanup(db_engine, person_id=person_id, question_id=question_id)


# ---------------------------------------------------------------------------
# (b) API 수준 -- POST /answers/{id} 두 번 동시 요청
# ---------------------------------------------------------------------------


@pytest.mark.dbtest
def test_post_answers_concurrent_requests_exactly_one_resume(db_engine, monkeypatch) -> None:
    """`POST /answers/{question_id}` 두 요청이 거의 동시에 오면 정확히
    하나만 200·하나만 409 여야 하고, 재개 로직(`resume_turn`)은 정확히
    1회만 불려야 한다(결정 J "재개 최대 1회" 가 동시 요청에서도 성립).

    `get_session` 을 오버라이드하지 않는다 -- 운영 경로(`app.api.deps.
    get_session`) 그대로 요청마다 새 커넥션/트랜잭션을 열어야 실제 잠금
    경쟁이 재현된다(`db_session` 롤백 픽스처로는 같은 세션을 공유해 경쟁
    자체가 성립하지 않는다). 대신 `app.api.routes.answer_question`/
    `resume_turn` 을 얇게 감싸 A 가 행을 잠근 뒤(커밋 전) B 를 시작하는
    순서를 결정적으로 만든다 -- 실제 판정 로직은 건드리지 않고 원본
    함수를 그대로 호출한다."""
    person_id, question_id = _make_person_and_schedule_question(db_engine)

    # 아래 어느 assert 가 실패해도(특히 결함이 재현되는 수정 전 코드로
    # 돌릴 때) 이 테스트가 커밋한 인물·일정·질문 행이 DB 에 남지 않도록
    # 본문 전체를 try/finally 로 감싼다 -- 실패 경로에서 정리가 빠지면
    # 전역 집계(`select(Schedule)` 전체 개수 등)를 쓰는 다른 테스트가
    # 이 테스트의 잔여 행 때문에 깨진다(실제로 한 번 그렇게 깨졌다).
    try:
        app = create_app()
        client = TestClient(app)

        real_answer_question = routes_module.answer_question
        real_resume_turn = routes_module.resume_turn

        lock_acquired = threading.Event()
        release_first = threading.Event()
        call_order_lock = threading.Lock()
        call_index = {"n": 0}

        def _patched_answer_question(ctx, qid, answer):
            with call_order_lock:
                call_index["n"] += 1
                my_index = call_index["n"]
            result = real_answer_question(ctx, qid, answer)
            if my_index == 1:
                # A -- 행을 잠근(FOR UPDATE) 채 B 가 시작할 때까지 대기한다.
                lock_acquired.set()
                released = release_first.wait(timeout=_WAIT_TIMEOUT)
                assert released, "메인 스레드가 release_first 를 제때 세우지 않았다"
            return result

        resume_calls: list[int] = []

        def _counting_resume_turn(*args, **kwargs):
            resume_calls.append(1)
            return real_resume_turn(*args, **kwargs)

        monkeypatch.setattr(routes_module, "answer_question", _patched_answer_question)
        monkeypatch.setattr(routes_module, "resume_turn", _counting_resume_turn)

        responses: dict[str, object] = {}
        errors: dict[str, object] = {}

        def _post(label: str) -> None:
            try:
                responses[label] = client.post(
                    f"/answers/{question_id}", json={"answer": _SCHEDULE_LABEL}
                )
            except Exception as exc:  # noqa: BLE001 -- 스레드 경계로 예외를 넘긴다
                errors[label] = exc

        thread_a = threading.Thread(target=_post, args=("a",))
        thread_a.start()
        assert lock_acquired.wait(timeout=_WAIT_TIMEOUT), "A 가 잠금을 잡지 못했다"

        thread_b = threading.Thread(target=_post, args=("b",))
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "B 가 A 의 잠금을 기다리지 않고 곧바로 끝났다 -- 동시 요청에서도 "
            "재개가 한 번만 도는지 확인할 수 없다(FIX-019 결함 재현)"
        )

        release_first.set()
        thread_a.join(timeout=_WAIT_TIMEOUT)
        thread_b.join(timeout=_WAIT_TIMEOUT)

        assert not thread_a.is_alive()
        assert not thread_b.is_alive()
        assert not errors, f"요청 스레드에서 예외 발생: {errors}"

        status_codes = sorted(resp.status_code for resp in responses.values())
        assert status_codes == [200, 409], responses

        for resp in responses.values():
            if resp.status_code == 409:
                assert resp.json()["detail"]["code"] == "already_answered"
            else:
                body = resp.json()
                assert body["status"] == "answered"
                assert body["stored"]["schedules"] == 1

        assert len(resume_calls) == 1, "resume_turn() 이 1회가 아니게 불렸다(재개 중복)"

        check_session = Session(bind=db_engine)
        try:
            schedules = (
                check_session.execute(select(Schedule).where(Schedule.person_id == person_id))
                .scalars()
                .all()
            )
            assert len(schedules) == 1
        finally:
            check_session.close()
    finally:
        _cleanup(db_engine, person_id=person_id, question_id=question_id)
