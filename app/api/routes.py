"""Refs: P2-tools U8 R6 R7 D1 D2 S3.4 -- FastAPI 라우트(`GET /health`,
`POST /answers/{question_id}`, `POST /chat`).

이 모듈은 도메인 예외를 잡지 않는다 -- 예외가 나면 그대로 올라가
`app/main.py` 의 예외 핸들러(결정 11 "예외 매핑은 한 곳에서")가 처리한다.
유일한 예외는 `GET /health` 의 `alembic_version` 조회 실패(테이블 없음)를
그 자리에서 `None` 으로 흡수하는 것과, `POST /chat`·`POST /answers/{id}`
가 루프 예외를 결정 G·H(01-plan U6/U7)에 따라 직접 삼키는 것뿐이다 --
둘 다 "판정"이 아니라 정해진 규약대로 흡수하는 것이다.

## U7 -- `POST /answers/{question_id}` 뒤 절반 (01-plan 94행, R6·R7 을 닫는다)

P2(`answer_question` 호출까지, 답 저장)와 이 라우트를 나눴던 경계가
사라졌다 -- 이제 `submit_answer()` 는 답을 저장한 **뒤에** 같은 요청
안에서 `app.agent.resume_turn()` 을 돌려 저장된 `context` 로 해석 단계부터
재개한다(S3.4 턴 N+1 전체). 예외 처리·부분 롤백 규약은 아래 U6 절과
**같다**(`_record_loop_error` 를 그대로 재사용) -- 유일한 차이는 이
라우트는 인식 LLM 을 다시 부르지 않으므로(결정 E) `get_proposer()` 를
주입하지 않고, 대신 `get_judge()`(재개 중 남은 언급의 `resolve()` 가
쓴다)·`get_embedder()`(재개가 만드는 새 별칭의 임베딩, R-15)만 `POST
/chat` 과 같은 의존성으로 재사용한다는 것이다.

## U6 -- `POST /chat` (01-plan 93행)

`run_turn()`(인식→게이트→해석→기록→응답)을 요청 1건 안에서 한 번 돌린다.
`get_session()`(요청 단위 commit/rollback)을 그대로 재사용하고 툴은
여전히 flush 까지만 한다(P2 결정 2). `LoopError` 계층·공급자 오류
(`app.er.JudgeUnavailable`, judge.py 오류 어휘 6종)·`ToolError` 계층만
여기서 잡아 삼킨다(R-3) -- `sqlalchemy.exc.SQLAlchemyError` 는 잡지
않고 그대로 올려 `get_session()` 의 rollback 을 타게 한다(결정 H,
`PendingRollbackError` 회피). 삼킨 예외는 200 + 결정 G 의 한 줄 응답 +
저장 0 + `loop_error` trace 1행으로 내린다 -- 예외 코드·공급자명·프롬프트는
응답 본문에 담지 않는다(security §1, `_record_loop_error` 참고).

**부분 롤백(사용자 승인, U6 추가 수정)** -- 발화 한 건에 언급이 둘 이상이면
`run_turn()` 내부 해석 구간이 언급을 순서대로 처리한다(결정 C(i)). 앞선
언급이 이미 `merge` 로 확정돼 별칭·trace 가 flush 된 뒤 **다음** 언급의
해석에서 예외가 나면, 앞선 언급의 flush 분이 그대로 남아 결정 G "저장 0"
과 어긋난다(F-b3f6a1). 이를 막기 위해 `run_turn()` 호출 전체를
`session.begin_nested()` 세이브포인트로 감싼다 -- 삼키는 예외가 나면
세이브포인트만 롤백하고(그 턴이 flush 한 모든 행 -- 업무 데이터는 물론
`loop_extract`/`loop_gate`/`tool_call`/`tool_error`/`er_resolve` 등 중간
trace까지 전부) 바깥 트랜잭션에는 손대지 않은 채 `_record_loop_error` 로
`loop_error` 한 행만 새로 남긴다. 그 턴에 무슨 일이 있었는지는 사라진
중간 trace 대신 이 `loop_error` 행의 `output.error`/`output.message` 로만
남는다 -- 이 트레이드오프는 "저장 0"을 정확히 지키기 위해 의도한 것이다
(원칙9의 예외: 실패한 턴은 근거 대신 실패 사실 자체를 남긴다).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agent import LoopError, Proposer, resume_turn, run_turn
from app.agent.types import LOOP_TRACE_TOOL_NAME, STEP_LOOP_ERROR
from app.api.deps import (
    build_chat_ctx,
    build_ctx,
    get_embedder,
    get_judge,
    get_proposer,
    get_session,
    load_resume_input,
    resolve_session_id,
)
from app.api.schemas import (
    AnswerIn,
    AnswerOut,
    ChatIn,
    ChatOut,
    ChatPendingQuestionOut,
    HealthOut,
    StoredOut,
)
from app.db.models import AgentTrace
from app.embedding import EmbeddingProvider
from app.er import Judge, JudgeUnavailable
from app.tools.context import TRACE_MAX_STRING, ToolContext
from app.tools.questions import answer_question
from app.tools.types import ToolError

router = APIRouter()

#: 결정 G -- 루프 예외를 삼켰을 때 보이는 한 줄. 감정·고민 상담 문장이 아니라
#: "지금은 처리하지 못했다"는 사실만 말한다(원칙7 경계 문장과 같은 방향).
_LOOP_ERROR_REPLY = "지금은 기억하지 못했어요. 잠시 뒤 다시 말씀해 주세요."


@router.get("/health", response_model=HealthOut)
def health(session: Session = Depends(get_session)) -> HealthOut:
    """DB 접속 확인(리스크 A -- 접속 확인은 여기서만 한다, `create_app()`/
    lifespan 은 엔진을 만들지도 접속을 확인하지도 않는다).

    `SELECT 1` 이 실패하면(또는 `get_session` 자체가 실패하면) 예외가 그대로
    올라가 `app/main.py` 의 전역 `Exception` 핸들러가 503
    `{"status":"degraded","db":"down","alembic_revision":null}` 로 매핑한다
    (비밀·예외 원문 미포함). `alembic_version` 테이블이 없으면(드문 경우)
    `alembic_revision` 만 `None` 으로 두고 `status`/`db` 는 내려가지 않는다
    -- "접속 실패"와 "테이블 없음"은 다른 상황이다.

    이 엔드포인트는 툴이 아니므로 `agent_traces` 를 남기지 않는다(01-plan
    U8 지시).
    """
    session.execute(text("SELECT 1"))
    try:
        revision = session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
    except Exception:
        session.rollback()
        revision = None
    return HealthOut(status="ok", db="up", alembic_revision=revision)


@router.post("/answers/{question_id}", response_model=AnswerOut)
def submit_answer(
    question_id: int,
    body: AnswerIn,
    session: Session = Depends(get_session),
    judge: Judge | None = Depends(get_judge),
    embedder: EmbeddingProvider | None = Depends(get_embedder),
) -> AnswerOut:
    """S3.4 턴 N+1 **전체**(칩 선택 → 답 저장 → 재개, U7 -- R6·R7 을 닫는다).
    `answer_question` 호출까지는 P2 그대로다(01-plan 결정 1 "그 화살표는
    P5-loop 이 이 라우트를 확장해서 잇는다" -- 이 단위가 그 화살표다).

    답 저장은 항상 **먼저** 끝낸다 -- 이미 답했거나(409 `already_answered`)
    만료됐으면(409 `expired`) `answer_question()` 자체가 예외를 던지므로
    `resume_turn()` 은 아예 불리지 않는다(결정 J 의 1회 소비는 이 순서
    자체가 강제한다 -- 두 번째 재개가 자동으로 막힌다). 저장이 성공한
    **뒤에만** `app.api.deps.load_resume_input()` 으로 저장된 `context` 를
    읽어 재개한다(결정 E -- 해석 단계부터, 인식 LLM 재호출 없음. `question_id`
    는 `resume_turn()` 이 `create_person`(D1) 직전에 `ctx.confirmed_question_id`
    로 세우는 값이다, `app/agent/loop.py::resume_turn` docstring 참고).

    예외 처리는 `POST /chat`(U6)과 **같은 규약**이다(R-3 -- `_record_loop_error`
    를 그대로 재사용하고 중복 구현하지 않는다): `LoopError` 계층·공급자
    오류(`JudgeUnavailable`)·`ToolError` 계층만 여기서 잡아 결정 G 의
    응답으로 내리고, `sqlalchemy.exc.SQLAlchemyError` 는 잡지 않고 그대로
    올려 `get_session()` 의 rollback 을 타게 한다(결정 H). `resume_turn()`
    도 `session.begin_nested()` 세이브포인트 **안에서** 돈다(U6 "부분
    롤백" 절과 같은 이유) -- 삼키는 예외가 나면 재개 턴이 flush 한 모든
    행(재개가 만든 별칭·이벤트·일정·중간 trace)만 사라지고, **답 저장
    자체는 세이브포인트 밖이라 영향받지 않는다**(이미 답했다는 사실은
    남아, 같은 질문으로 세 번째 재개를 시도해도 여전히 409 다)."""
    ctx = build_ctx(session, question_id, embedder=embedder)
    result = answer_question(ctx, question_id, body.answer)
    resume_input = load_resume_input(session, question_id)

    try:
        with session.begin_nested():
            turn = resume_turn(ctx, resume_input, question_id=question_id, judge=judge)
    except (LoopError, JudgeUnavailable, ToolError) as exc:
        error_trace = _record_loop_error(ctx, body.answer, exc)
        return AnswerOut(
            question_id=result.question_id,
            status=result.status,
            reply=_LOOP_ERROR_REPLY,
            stored=StoredOut(persons=0, events=0, schedules=0),
            pending_question=None,
            stop_reason=None,
            trace_ids=[error_trace.id],
        )

    return AnswerOut(
        question_id=result.question_id,
        status=result.status,
        reply=turn.reply,
        stored=StoredOut(**turn.stored.to_dict()),
        pending_question=(
            ChatPendingQuestionOut(**turn.pending_question.to_dict())
            if turn.pending_question is not None
            else None
        ),
        stop_reason=turn.stop_reason,
        trace_ids=list(turn.trace_ids),
    )


def _record_loop_error(ctx: ToolContext, utterance: str, exc: Exception) -> AgentTrace:
    """결정 G·H -- 루프 예외를 삼키며 `loop_error` trace 행 하나를 남긴다
    (모듈 docstring "U6" 참고). `app/tools/context.py::traced()` 가 예외
    시 만드는 `step="tool_error"` 행과는 **다른** 행이다 -- 그 행은 루프
    내부의 어느 `@traced` 단계가 실패했는지를 가리키고, 이 행은 라우트가
    그 예외를 여기서 삼키기로 했다는 턴 단위 사실 자체를 가리킨다(F-4d8d96
    ·F-ca12ad 가 P5 로 넘긴 결정, 결정 H -- 같은(아직 커밋되지 않은)
    세션에 `add()`+`flush()` 할 뿐이므로 라우트가 200 으로 끝나야
    `get_session()` 의 `commit()` 과 함께 이 행도 남는다).

    `type(exc).__name__`·`str(exc)` 만 담는다 -- `LoopError`/`ToolError`/
    `JudgeUnavailable` 서브클래스는 전부 "짧은 코드성 메시지만 담는다"는
    관례를 따르므로(각 클래스 docstring), 예외 원문을 그대로 옮겨도
    프롬프트·공급자명·키가 섞이지 않는다(security §1)."""
    trace = AgentTrace(
        session_id=ctx.session_id,
        step=STEP_LOOP_ERROR,
        tool_name=LOOP_TRACE_TOOL_NAME,
        input={"utterance": utterance[:TRACE_MAX_STRING]},
        output={"error": type(exc).__name__, "message": str(exc)[:TRACE_MAX_STRING]},
        tokens_in=0,
        tokens_out=0,
    )
    ctx.session.add(trace)
    ctx.session.flush()
    return trace


@router.post("/chat", response_model=ChatOut)
def chat(
    body: ChatIn,
    session_id: str = Depends(resolve_session_id),
    session: Session = Depends(get_session),
    proposer: Proposer | None = Depends(get_proposer),
    judge: Judge | None = Depends(get_judge),
    embedder: EmbeddingProvider | None = Depends(get_embedder),
) -> ChatOut:
    """S3.4 턴 N -- 발화 한 건 = 턴 한 번(01-plan U6). 세션 귀속은 결정 I
    (`X-Session-Id` 없으면 서버가 발급해 응답 `session_id` 로 돌려준다).
    단일 사용자 제품 전제(`ctx.user_id = app_user_id()` 고정, `build_chat_ctx`
    참고) -- 다중 사용자 격리는 이 패키지 범위 밖이다.

    `embedder` 는 `get_embedder()` 의존성이 고른다(U6 추가 수정, 사용자
    승인) -- 운영 경로는 `_embedder_from_env()`(R-15), 테스트는
    `app.dependency_overrides[get_embedder]` 로 `fake_embedder` 를 주입해
    네트워크 0 을 지킨다. `build_chat_ctx()` 자신은 더 이상 임베더를
    스스로 고르지 않는다(`deps.py` 모듈 docstring 참고).

    `run_turn()` 이 인식→게이트→해석→기록→응답을 요청 1건 안에서 돈다.
    되묻기로 끝나면(D2) 그 턴은 `ChatOut.pending_question` 을 채운 채
    여기서 끝난다 -- 다음 답은 `POST /answers/{question_id}` 가 받는다.

    예외 처리(모듈 docstring "U6" 절, R-3): `LoopError` 계층·공급자 오류
    (`JudgeUnavailable`)·`ToolError` 계층만 여기서 잡아 결정 G 의 응답으로
    내린다. `sqlalchemy.exc.SQLAlchemyError` 는 잡지 않는다 -- `begin_nested()`
    블록 밖(아래)이므로 그대로 올라가 `get_session()` 이 바깥 트랜잭션
    전체를 rollback 한다(결정 H, 이 파일은 `SQLAlchemyError` 를 import 하지
    않는다 -- 잡을 대상이 아니라는 사실 자체가 코드로 드러난다).

    `run_turn()` 은 `session.begin_nested()` 세이브포인트 **안에서** 돈다
    (모듈 docstring "부분 롤백" 절) -- 삼키는 예외가 나면 그 턴이 flush 한
    모든 행(업무 데이터 + 중간 trace)이 세이브포인트와 함께 사라지고,
    `_record_loop_error()` 가 세이브포인트 **밖**(이 함수 자신의 프레임,
    즉 바깥 트랜잭션)에서 `loop_error` 행 하나만 새로 남긴다 -- 이 행이
    사라진 중간 trace를 대신하는 유일한 근거다. `ctx.last_trace_id` 는
    세이브포인트 롤백 뒤에도 이전(존재하지 않게 된) 행의 id 를 들고 있을
    수 있지만, 이 함수도 `_record_loop_error()` 도 그 값을 읽지 않는다
    (아래 `trace_ids` 는 `error_trace.id` 하나뿐이다) -- 죽은 참조가 응답에
    섞이지 않는다."""
    ctx = build_chat_ctx(session, session_id, embedder)
    try:
        with session.begin_nested():
            turn = run_turn(ctx, body.utterance, proposer=proposer, judge=judge)
    except (LoopError, JudgeUnavailable, ToolError) as exc:
        error_trace = _record_loop_error(ctx, body.utterance, exc)
        return ChatOut(
            reply=_LOOP_ERROR_REPLY,
            session_id=session_id,
            stored=StoredOut(persons=0, events=0, schedules=0),
            pending_question=None,
            stop_reason=None,
            trace_ids=[error_trace.id],
        )
    return ChatOut.model_validate(turn.to_dict())
