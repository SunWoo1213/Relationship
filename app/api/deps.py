"""Refs: P2-tools U8 결정 12 -- 요청 단위 세션 의존성 + `ToolContext` 조립.

`get_session()` 은 제너레이터 의존성이다: `SessionLocal()` 로 요청 단위
세션을 만들고, 정상 종료 시 commit, 예외 시 rollback, finally 에서 항상
close 한다 -- `app/db/session.py` 의 `session_scope()` 와 같은 규약을
FastAPI 의존성 형태로 옮긴 것이다. 툴 함수는 여전히 commit 하지 않는다
(01-plan 결정 2) -- 트랜잭션 경계는 이 의존성(호출자)이 잡는다.

`get_engine()` 은 `SessionLocal()` 이 실제로 호출될 때(즉 요청이 들어와
이 의존성이 실행될 때)까지 지연된다(`app/db/session.py` 의 `_SessionLocalProxy`
-- 리스크 A). 이 모듈을 import 하는 것만으로는 엔진이 생성되지 않는다.

`build_ctx(session, question_id)` 는 **답할 `pending_questions` 행을 먼저
조회해 그 행의 `session_id` 로 `ToolContext` 를 만든다**(결정 12) --
클라이언트가 헤더로 주장하는 세션 값보다 저장된 행이 권위 있고, trace 가
질문을 만든 턴과 같은 세션에 묶인다. `X-Session-Id` 헤더 규약은 세션을
새로 여는 쪽(P5-loop 의 채팅 엔드포인트)이 정한다 -- 이 모듈은 헤더를
읽지 않는다. 행이 없으면 `QuestionNotFound` 를 올린다(라우트에서 404 로
매핑, `app/main.py`).

## U6 추가분 -- `POST /chat` 용 세션 귀속 + `ToolContext` 조립 (결정 I)

`resolve_session_id()` 는 `X-Session-Id` 헤더가 있으면 형식(길이 1~128,
`[A-Za-z0-9._-]`)을 검증해 그대로 쓰고, 없으면 서버가 `uuid4` 로 새로
발급한다. 형식이 어긋나면 `fastapi.HTTPException(422)` 를 **이 함수 자신이**
던진다 -- `app/main.py` 는 U6 의 허용 파일이 아니므로(01-plan 75행) 새
예외 핸들러를 등록하지 않고 FastAPI 가 기본으로 처리하는 `HTTPException`
을 그대로 쓴다.

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
그 값을 인자로 받기만 한다."""

from __future__ import annotations

import os
import re
import uuid
from collections.abc import Iterator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.agent import Proposer
from app.db.models import PendingQuestion
from app.db.session import SessionLocal
from app.embedding import EmbeddingProvider, OpenAIEmbeddingProvider
from app.er import Judge
from app.settings import app_user_id
from app.tools.context import ToolContext
from app.tools.types import QuestionNotFound


def get_session() -> Iterator[Session]:
    """요청 단위 세션. 정상 종료 시 commit, 예외 시 rollback, 항상 close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def build_ctx(session: Session, question_id: int) -> ToolContext:
    """답할 `pending_questions` 행을 조회해 그 `session_id` 로 `ToolContext`
    를 만든다(결정 12). 행이 없으면 `QuestionNotFound`.

    `user_id = app_user_id()`(로컬 단일 사용자), `embedder=None`(답 저장은
    별칭을 만들지 않는다), `now` 는 기본값(`datetime.now(timezone.utc)`)."""
    question = session.get(PendingQuestion, question_id)
    if question is None:
        raise QuestionNotFound("question_not_found")
    return ToolContext(
        session=session,
        session_id=question.session_id,
        user_id=app_user_id(),
        embedder=None,
    )


# ---------------------------------------------------------------------------
# U6 -- `POST /chat` 세션 귀속(결정 I) + `ToolContext` 조립 + 테스트용 오버라이드 지점
# ---------------------------------------------------------------------------

#: 세션 id 형식 검증(결정 I "길이·문자 집합"). `uuid4()` 표기(16진수 +
#: 하이픈)를 포함하고, 프론트가 직접 지정하는 짧은 태그도 허용한다.
_SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def resolve_session_id(
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
) -> str:
    """S3.4·결정 I -- `X-Session-Id` 헤더가 있으면 형식을 검증해 그대로
    쓰고, 없으면 서버가 `uuid4` 로 새로 발급한다. 형식이 어긋나면 422
    (모듈 docstring "U6 추가분" 참고 -- `app/main.py` 를 고치지 않는다)."""
    if x_session_id is None:
        return str(uuid.uuid4())
    if not _SESSION_ID_PATTERN.fullmatch(x_session_id):
        raise HTTPException(status_code=422, detail={"code": "invalid_session_id"})
    return x_session_id


def _embedder_from_env() -> EmbeddingProvider | None:
    """`OPENAI_API_KEY` 가 있으면 실제 임베더(`OpenAIEmbeddingProvider`)를,
    없으면 `None` 을 돌려준다(R-15 -- 조용한 미검출을 트레이드오프로 받되
    숨기지 않는다, 모듈 docstring 참고)."""
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    return OpenAIEmbeddingProvider()


def build_chat_ctx(
    session: Session, session_id: str, embedder: EmbeddingProvider | None
) -> ToolContext:
    """`POST /chat`(U6) 용 `ToolContext` 조립. `user_id = app_user_id()`
    고정(로컬 단일 사용자 전제, 결정 I -- `pending_questions`/`agent_traces`
    에 `user_id` 컬럼이 없어 다중 사용자 격리는 이 패키지 범위 밖이다).

    `embedder` 는 **호출자(`routes.chat`)가 `get_embedder()` 의존성으로
    주입한 값을 그대로 받는다** -- 이 함수 자신은 `_embedder_from_env()`
    를 부르지 않는다(U6 추가 수정, 모듈 docstring 참고). 운영 경로는
    `get_embedder()` 가 돌려준 `_embedder_from_env()` 결과(R-15)가 그대로
    오고, 테스트는 `app.dependency_overrides[get_embedder]` 로 주입한
    `fake_embedder` 가 온다 -- `build_ctx()`(답 저장 전용, `embedder=None`
    고정)와 다르다."""
    return ToolContext(
        session=session,
        session_id=session_id,
        user_id=app_user_id(),
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
