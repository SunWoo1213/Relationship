"""Refs: P2-tools U8 결정 12 -- 요청 단위 세션 의존성 + `ToolContext` 조립.

`get_session()` 은 제너레이터 의존성이다: `SessionLocal()` 로 요청 단위
세션을 만들고, 정상 종료 시 commit, 예외 시 rollback, finally 에서 항상
close 한다. **P9b-auth U3b -- 정의는 `app/db/session.py` 로 옮겼고 이 모듈은 같은
객체를 다시 내보낸다**(`app.auth.deps.current_user` 와의 순환 import 를 끊으려고;
`app.dependency_overrides[get_session]` 키는 그대로 맞는다). 툴 함수는 여전히
commit 하지 않는다(01-plan 결정 2) -- 트랜잭션 경계는 이 의존성(호출자)이 잡는다.

`get_engine()` 은 `SessionLocal()` 이 실제로 호출될 때(즉 요청이 들어와
이 의존성이 실행될 때)까지 지연된다(`app/db/session.py` 의 `_SessionLocalProxy`
-- 리스크 A). 이 모듈을 import 하는 것만으로는 엔진이 생성되지 않는다.

`build_ctx(session, question_id, user)` 는 **답할 `pending_questions` 행을 먼저
조회해 그 행의 `session_id` 로 `ToolContext` 를 만든다**(결정 12) --
클라이언트가 헤더로 주장하는 세션 값보다 저장된 행이 권위 있고, trace 가
질문을 만든 턴과 같은 세션에 묶인다. **P9b-auth U3b(S3.4 답변 소유)** -- 행이
없거나 **로그인한 사용자 소유가 아니면**(`PendingQuestion.user_id != user.id`)
같은 `QuestionNotFound` 를 올려 "없음"과 "남의 것"이 구별되지 않는다(라우트에서 404 로
매핑, `app/main.py`).

## U6 추가분 -- `POST /chat` 용 세션 귀속 + `ToolContext` 조립 (결정 I)

**P9b-auth U3b** -- 대화 `session_id` 는 서버가 계정에서 만든다(`chat_session_id(user_id)`
= `chat:<user_id>`, 결정 S). 예전의 `resolve_session_id()`(`X-Session-Id` 헤더를 읽고 형식
검증, 없으면 uuid4)는 없어졌고 헤더는 무시된다.

`build_chat_ctx()` 는 `build_ctx()`(위, 답 저장 전용)와 **다른** 조립
함수다 -- 옆에 나란히 둔다(01-plan 70행 "그대로 두고 옆에 새 조립 함수를
둔다"). **R-15** -- 임베딩 키가 없는 환경에서는 `embedder=None` 이고 ER 은
`embedding_skipped` 로 돌며, 그때 새로 만든 별칭의 `embedding` 은 NULL 로
남아 이후 다른 표기 검색에서 미검출된다. `build_ctx()`(답 저장 전용)와
달리 채팅 경로는 `create_person`/`update_person(new_alias)` 로 새 별칭을
만들 수 있으므로 실제 임베더를 시도한다 -- 키가 없으면 그 결과가 `None`
일 뿐, 일부러 `None` 을 강제하지 않는다.

`get_proposer()`/`get_judge()`/`get_embedder()` 는 `POST /chat` 이
`run_turn()`/`build_chat_ctx()` 에 넘길 인식/판정/임베딩 공급자를 고르는
FastAPI 의존성이다 -- 운영 경로는 각각 `None`/`None`/`_embedder_from_env()`
를 돌려줘 `run_turn`/ER 이 `proposer_from_env()`/`judge_from_env()` 를
쓰고, 채팅 ctx 는 키가 있으면 실제 임베더를 쓰게 한다. 테스트는
`app.dependency_overrides` 로 `FakeProposer`/`FakeJudge`/`fake_embedder`
를 주입해 네트워크 0 으로 돈다(`get_session` 오버라이드와 같은 관례, P2
결정 13) -- **U6 추가 수정(사용자 승인)**: `build_chat_ctx()` 가 내부에서
직접 `_embedder_from_env()` 를 부르면 테스트가 주입한 `fake_embedder` 가
쓰이지 않고(운영 키가 없는 개발 환경에서는 `embedder=None` 이 되어 merge
문턱을 넘지 못해 되묻기로 빠지고), 반대로 키가 있는 환경에서는 테스트가
실제 OpenAI 를 부르게 된다(네트워크 0 위반). `get_embedder()` 를 별도
의존성으로 빼 `routes.chat` 이 `Depends` 로 주입하고 `build_chat_ctx()` 는
그 값을 인자로 받기만 한다.

## U7 추가분 -- `load_resume_input()` + `build_ctx()` 확장 (재개, R6·R7)

`load_resume_input(session, question_id)` 는 답 저장(`answer_question`)
**뒤에** 불러 `app.agent.types.ResumeInput(kind, context, answer)` 를
값으로 돌려준다(아래 함수 docstring 이 `ResumeInput` 표기 정리를 적는다).
`build_ctx()` 는 이제 `embedder` 를 받는다(기본 `None`, 하위 호환) --
재개가 `create_person`/`update_person(new_alias=…)` 로 새 별칭을 만들 수
있으므로(위 U6 절 "embedder=None 구멍"과 같은 이유) `routes.submit_answer`
가 `get_embedder()`(U6 이 이미 만든 의존성, 그대로 재사용)로 받은 값을
넘긴다. `get_judge()` 도 같은 이유로 `routes.submit_answer` 가 재사용한다
(재개 중 남은 언급을 `resolve()` 할 수 있으므로) -- `get_proposer()` 는
재사용하지 않는다: `resume_turn()` 은 인식 LLM 을 다시 부르지 않으므로
(결정 E) 이 의존성을 주입해도 쓰이지 않아, 불필요한 의존성을 라우트에
더하지 않는다(U7 03-log 에 이 결정을 적는다).

## U6 추가분 -- `POST /briefings/run` 용 의존성 (P6-briefing, Refs: P6-briefing S3.6 R12 원칙9)

`get_briefing_composer()` 는 `get_fact_extractor()` 와 같은 "지연 생성"
규약을 따른다 -- 이 함수 자신은 import 시점(앱 기동)에는 호출되지
않고, `POST /briefings/run` 요청이 들어와 FastAPI 가 이 의존성을 해소할
때에만 `composer_from_env()`(D11, 공급자 선택)를 부른다. 그래서 LLM
공급자 키가 없는 환경에서도 앱 기동·다른 엔드포인트 호출은 깨지지
않는다 -- 실패는 이 엔드포인트를 실제로 부를 때만 `JudgeUnavailable`
로 드러난다. 테스트는 `app.dependency_overrides[get_briefing_composer]`
로 `FakeBriefingComposer`(`app.briefing.compose`)를 주입해 네트워크
0 으로 돈다(`get_proposer`/`get_judge`/`get_embedder`/`get_fact_extractor`
와 같은 관례).

`get_now()` 는 `run_briefings()`(U5)가 대상 선정(`select_due_schedules`)
의 창 계산에 쓸 "지금"을 공급한다. `/chat`·`/answers/{id}` 와 달리 이
엔드포인트는 "다가오는 일정"이라는 **시간 창**으로 대상을 고르므로
(`scheduled_at` 과 "지금"의 차이가 결과를 가른다), 테스트가 일정 시각을
고정된 기준 없이 실제 벽시계와 맞추려면 매 실행마다 변하는 값을
떠안아야 한다 -- 기존 `ctx.now` 주입 관례(`ToolContext.now`, 비-HTTP
테스트가 전부 쓰는 방식)를 HTTP 의존성 모양으로 옮긴 것으로,
`get_proposer`/`get_judge`/`get_embedder` 와 **같은 어휘의 확장**이다
(새 메커니즘을 만들지 않는다). 운영 경로는 실제 시계
(`datetime.now(timezone.utc)`)를 돌려주고, 테스트는
`app.dependency_overrides[get_now]` 로 고정 시계(`lambda: FIXED_NOW`)를
주입한다. `build_briefing_ctx()` 가 이 값을 그대로 `ToolContext.now` 에
싣는다."""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.orm import Session

from app.agent import Proposer, ResumeInput
from app.auth.deps import current_user
from app.briefing import BriefingComposer, Notifier, composer_from_env
from app.db.models import PendingQuestion, User
from app.db.session import get_session
from app.embedding import EmbeddingProvider, OpenAIEmbeddingProvider
from app.er import Judge
from app.memory import FactExtractor
from app.push.notifier import notifier_from_env
from app.tools.context import ToolContext
from app.tools.types import QuestionNotFound

# `get_session` 은 `app.db.session` 에서 온 같은 객체다(모듈 docstring) -- 기존 import 경로
# (`from app.api.deps import get_session`)와 `app.dependency_overrides` 키를 그대로 지킨다.


def chat_session_id(user_id: str) -> str:
    """계정마다 채팅방 하나 -- 대화 `session_id` 는 서버가 계정에서 만든다(결정 S).
    클라이언트가 보낸 헤더 값은 어디에서도 쓰지 않는다."""
    return f"chat:{user_id}"


def build_ctx(
    session: Session,
    question_id: int,
    user: User,
    embedder: EmbeddingProvider | None = None,
) -> ToolContext:
    """답할 `pending_questions` 행을 조회해 그 `session_id` 로 `ToolContext`
    를 만든다(결정 12). 행이 없거나 **로그인한 사용자 소유가 아니면**(S3.4 답변
    소유, F-fbaaae) 같은 `QuestionNotFound` -- 존재 여부를 흘리지 않는다.

    `user_id = user.id`(로그인한 계정), `now` 는 기본값
    (`datetime.now(timezone.utc)`).

    **U7 추가** -- `embedder` 파라미터(기본 `None`, 하위 호환). 답 저장만
    하던 시절(P2)에는 별칭을 만들지 않아 `embedder=None` 고정이었지만,
    이제 이 ctx 로 재개(U7)가 `create_person`/`update_person(new_alias=…)`
    를 부를 수 있으므로(01-plan 70행 리스크 "embedder=None 구멍") 호출자
    (`routes.submit_answer`)가 `get_embedder()` 의존성(운영은
    `_embedder_from_env()`, 테스트는 `fake_embedder`, `build_chat_ctx` 와
    같은 관례, R-15)으로 받은 값을 넘긴다. 아무것도 넘기지 않으면 예전과
    똑같이 `None` 이다."""
    question = session.get(PendingQuestion, question_id)
    if question is None or question.user_id != user.id:
        raise QuestionNotFound("question_not_found")
    return ToolContext(
        session=session,
        session_id=question.session_id,
        user_id=user.id,
        embedder=embedder,
    )


def load_resume_input(session: Session, question_id: int) -> ResumeInput:
    """U7 -- `POST /answers/{question_id}` 뒤 절반이 읽을 재개 재료.
    **답 저장(`answer_question`) 뒤에** 불러야 한다 -- `pending_questions
    .answer` 컬럼이 이미 채워져 있어야 하기 때문이다(아래 참고). 행이
    없으면 `QuestionNotFound`(이미 `build_ctx()`/`answer_question()` 이
    지나간 뒤이므로 실제로는 거의 일어나지 않지만, 이 함수 자신도
    존재를 가정하지 않는다).

    `PendingQuestion` ORM 을 읽는 것은 이 모듈(`build_ctx`·이 함수)뿐이고
    `app/agent/` 는 값(`kind`·`context`·`answer`)만 받는다(H-2 의 (b)
    경로 차단, 판정 표 23행).

    **`ResumeInput` 표기 정리(보고에 남긴 결정, `app/agent/loop.py::
    resume_turn` docstring 과 같은 결정을 여기서도 적용한다)** -- 01-plan
    70행은 `ResumeInput{kind, context, session_id}` 라 적었지만 U1
    (`app/agent/types.py`)이 실제로 만든 필드는 `kind`·`context`·`answer`
    다. 이 함수는 **U1 쪽(실제 타입)을 따른다**: `session_id` 는 넣지
    않는다(`ToolContext.session_id` 가 이미 담당, 결정 12). 대신 `answer`
    는 **요청 본문을 다시 읽지 않고 저장된 행에서 그대로 읽는다** --
    라우트가 이 함수를 부르기 **전에** `answer_question(ctx, question_id,
    body.answer)` 로 이미 `question.answer` 를 저장했으므로, 그 컬럼이
    사용자가 방금 제출한 답과 항상 같다(단일 출처 -- 같은 값을 요청
    본문과 DB 행 두 자리에서 따로 나르지 않는다)."""
    question = session.get(PendingQuestion, question_id)
    if question is None:
        raise QuestionNotFound("question_not_found")
    context = question.context if isinstance(question.context, dict) else {}
    answer = question.answer if isinstance(question.answer, str) else ""
    return ResumeInput(kind=question.kind, context=context, answer=answer)


# ---------------------------------------------------------------------------
# U6 -- `POST /chat` 세션 귀속(결정 I) + `ToolContext` 조립 + 테스트용 오버라이드 지점
# ---------------------------------------------------------------------------

def _embedder_from_env() -> EmbeddingProvider | None:
    """`OPENAI_API_KEY` 가 있으면 실제 임베더(`OpenAIEmbeddingProvider`)를,
    없으면 `None` 을 돌려준다(R-15 -- 조용한 미검출을 트레이드오프로 받되
    숨기지 않는다, 모듈 docstring 참고)."""
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    return OpenAIEmbeddingProvider()


def build_chat_ctx(
    session: Session, user: User, embedder: EmbeddingProvider | None
) -> ToolContext:
    """`POST /chat`(U6) 용 `ToolContext` 조립. `user_id = user.id`(로그인한
    계정), `session_id = chat:<user.id>`(`chat_session_id`, 결정 S -- 서버가
    계정에서 만들고 클라이언트 헤더는 읽지 않는다).

    `embedder` 는 **호출자(`routes.chat`)가 `get_embedder()` 의존성으로
    주입한 값을 그대로 받는다** -- 이 함수 자신은 `_embedder_from_env()`
    를 부르지 않는다(U6 추가 수정, 모듈 docstring 참고). 운영 경로는
    `get_embedder()` 가 돌려준 `_embedder_from_env()` 결과(R-15)가 그대로
    오고, 테스트는 `app.dependency_overrides[get_embedder]` 로 주입한
    `fake_embedder` 가 온다 -- `build_ctx()`(답 저장 전용, `embedder=None`
    고정)와 다르다."""
    return ToolContext(
        session=session,
        session_id=chat_session_id(user.id),
        user_id=user.id,
        embedder=embedder,
    )


def get_proposer() -> Proposer | None:
    """`POST /chat` 이 `run_turn()` 에 넘길 인식 단계 공급자(U2). 운영
    경로는 `None`(`run_turn` 이 `proposer_from_env()` 를 쓴다). 테스트는
    `app.dependency_overrides[get_proposer]` 로 `FakeProposer` 를 주입해
    네트워크 0 으로 돈다(`get_session` 오버라이드와 같은 관례, P2 결정 13)."""
    return None


def get_judge() -> Judge | None:
    """`POST /chat` 이 `run_turn()` 에 넘길 3단계 판정기(P3-er). 운영
    경로는 `None`(ER 이 `judge_from_env()` 를 쓴다). 테스트는 `FakeJudge`
    를 주입한다(`get_proposer()` 와 같은 관례)."""
    return None


def get_embedder() -> EmbeddingProvider | None:
    """`POST /chat` 이 `build_chat_ctx()` 에 넘길 임베더(U6 추가 수정,
    사용자 승인). 운영 경로는 `_embedder_from_env()` 그대로(R-15 -- 키가
    없으면 `None`). 테스트는 `app.dependency_overrides[get_embedder]` 로
    `fake_embedder`(`tests/conftest.py`)를 주입해, 개발 환경에 키가
    없어도 merge 문턱을 넘는 시나리오를 재현하고, 키가 있는 환경에서도
    실제 OpenAI 호출 없이 네트워크 0 으로 돈다(`get_proposer()`/
    `get_judge()` 와 같은 관례)."""
    return _embedder_from_env()


def get_fact_extractor() -> FactExtractor | None:
    """`POST /chat`/`POST /answers/{id}` 이 `run_turn()`/`resume_turn()`
    에 넘길 사실 추출기(P6-memory U6). 운영 경로는 `get_proposer()`/
    `get_judge()` 와 같은 모양으로 항상 `None` 을 돌려준다 -- 다만 그
    둘과 달리 `run_turn`/`resume_turn` 은 이 값을 **즉시** 해소하지
    않는다. `None` 은 `app.memory.hooks.after_record()` 로 그대로
    전달되고, 그 함수가 `_LazyFactExtractor` 로 감싸 승격 트리거가 걸릴
    때(미승격 이벤트 ≥ `MEMORY_PROMOTE_MIN_EVENTS`)만
    `app.memory.extract.extractor_from_env()` 를 해소한다(★ R-10 해소,
    `app/memory/hooks.py` 모듈 docstring 참고) -- 트리거가 걸리지 않는
    대부분의 요청은 API 키가 없어도 그대로 처리된다. 테스트는
    `app.dependency_overrides[get_fact_extractor]` 로
    `FakeFactExtractor`(`app.memory.extract`)를 주입해 네트워크 0 으로
    돈다(`get_proposer()`/`get_judge()`/`get_embedder()` 와 같은 관례)."""
    return None


# ---------------------------------------------------------------------------
# U6 -- `POST /briefings/run` 의존성(P6-briefing, 모듈 docstring "U6 추가분" 참고)
# ---------------------------------------------------------------------------


def get_briefing_composer() -> BriefingComposer:
    """`POST /briefings/run` 이 `run_briefings()` 에 넘길 문장 생성기.
    운영 경로는 요청이 들어올 때 `composer_from_env()`(D11)를 불러
    공급자를 고른다 -- import·앱 기동 시점에는 아무것도 생성하지 않는다
    (모듈 docstring "U6 추가분" 참고, `get_fact_extractor()` 와 같은
    지연 생성 규약). 테스트는
    `app.dependency_overrides[get_briefing_composer]` 로
    `FakeBriefingComposer`(`app.briefing.compose`)를 주입한다."""
    return composer_from_env()


def get_now() -> Callable[[], datetime]:
    """`POST /briefings/run` 이 `ToolContext.now` 에 넘길 시계(모듈
    docstring "U6 추가분" 참고). 운영 경로는 실제 시계를 돌려준다.
    테스트는 `app.dependency_overrides[get_now]` 로 고정 시계를
    주입해(`get_proposer()`/`get_judge()`/`get_embedder()` 와 같은
    관례) 일정의 `scheduled_at` 과 비교되는 "지금"을 고정한다."""
    return lambda: datetime.now(timezone.utc)


def get_notifier(
    session: Session = Depends(get_session),
    now: Callable[[], datetime] = Depends(get_now),
    user: User = Depends(current_user),
) -> Notifier:
    """P7-push U5 -- `POST /briefings/run` 이 `run_briefings()` 에 넘길
    알림기. `notifier_from_env()`(U4)가 VAPID 설정 세 가지 상태(전무 ->
    `NullNotifier`, 반쪽 -> `MisconfiguredNotifier`, 전부 -> `WebPushNotifier`)
    를 알림기로 사상한다 -- 키가 없는 환경에서는 예전과 똑같이
    `push == "not_configured"` 다.

    **세션은 요청과 같은 것**(`Depends(get_session)` 은 같은 요청 안에서
    캐시되므로 엔드포인트의 `session` 과 동일 객체다)을 쓴다 --
    `WebPushNotifier` 가 이 세션으로 구독·인물을 읽고 `push_send` trace 를
    쓰므로, 다른 세션이면 `briefed_at`·trace 가 커밋 시점에 따라 갈린다
    (02-plan-verify R-1). 테스트가 `app.dependency_overrides[get_notifier]`
    로 가짜 알림기를 넣을 때도 오버라이드 함수가 `Depends(get_session)` 을
    선언해 같은 세션을 받아야 한다. `user_id = user.id`(로그인한 계정 -- 그
    사용자의 구독으로만 보낸다, `build_briefing_ctx()` 와 같음), `now` 는
    `get_now()` 가 준 같은 시계다."""
    return notifier_from_env(session, user.id, now)


def build_briefing_ctx(
    session: Session, now: Callable[[], datetime], user: User
) -> ToolContext:
    """`POST /briefings/run`(U6) 용 `ToolContext` 조립. `session_id` 는
    `run_briefings()`(U5)가 내부에서 자신만의 `"briefing:<uuid4>"` 로
    바꿔 쓰므로(결정 I, `app/briefing/run.py` 모듈 docstring "실행 하나의
    session_id" 절) 여기서 넣는 값은 그 전까지만 쓰인다 -- 그래도
    추적 가능하도록 `build_chat_ctx()` 와 같은 생성 관례로
    `"briefings-api:<uuid4>"` 를 쓴다. `user_id = user.id`(로그인한 계정,
    `build_chat_ctx()` 와 같음)."""
    return ToolContext(
        session=session,
        session_id=f"briefings-api:{uuid.uuid4()}",
        user_id=user.id,
        now=now,
    )
