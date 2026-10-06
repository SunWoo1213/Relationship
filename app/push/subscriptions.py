"""Refs: P7-push S3.1 S3.6 R12 FIX-020 -- U2 구독 저장(`save_subscription`·
`list_subscriptions`).

`save_subscription`: 같은 `(user_id, endpoint)` 조합이면 기존 행의
`keys` 만 갱신하고 같은 `id` 를 `created=False` 로 돌려준다. 없으면 새
행을 만들어 `created=True` 로 돌려준다(01-plan 결정 F(i)).

### 동시성 (FIX-020)

`push_subscriptions` 에는 `UNIQUE(user_id, endpoint)` 제약이 있다(0002
리비전, 01-plan 당시 리스크 절 "같은 엔드포인트 경쟁"이 남겨 둔 숙제를
여기서 닫는다). `INSERT ... ON CONFLICT (user_id, endpoint) DO UPDATE
keys` 한 문장으로 끝내 두 요청이 동시에 같은 구독을 보내도 중복 행이
생기지 않는다 -- 조회 후 분기하지 않는다.

`list_subscriptions`: `user_id` 조건이 **항상** 걸린다(security.md §5
"모든 조회는 user_id 조건" -- 판정 표 5행 "사용자 격리"). `WebPushNotifier`
(U4)가 발송 대상 구독을 모을 때 이 함수를 쓴다.

이 모듈은 커밋하지 않는다(`flush()` 까지만) -- 트랜잭션 경계는 호출자
(`app/api/deps.py::get_session`)가 잡는다(`app/tools/questions.py` 와
같은 관례).

엔드포인트 URL·키 값은 이 모듈 어디에도 로그·print 로 쓰지 않는다 --
ORM 으로 읽고 쓸 뿐이다(security.md §1).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import literal_column, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.models import PushSubscription


@dataclass(frozen=True)
class SavedSubscription:
    """`save_subscription()` 의 반환값(01-plan 판정 표 1·2행 "id, created").
    ORM 객체(`PushSubscription`)를 호출자까지 그대로 들고 가지 않고 순수
    값만 돌려준다 -- `app/tools/types.py` 의 `*Out` dataclass 와 같은 경계
    규약이다. HTTP 응답 모양은 `app/api/schemas.py` 가 별도로 감싼다(결정 11)."""

    id: int
    created: bool


def save_subscription(
    session: Session, user_id: str, endpoint: str, keys: dict[str, str]
) -> SavedSubscription:
    """`(user_id, endpoint)` 로 upsert 한다(결정 F(i), 모듈 docstring
    "동시성(FIX-020)" 절). 있으면 `keys` 만 갱신하고 같은 `id` 를
    `created=False` 로 돌려준다. 없으면 새 행을 만들어 `created=True` 로
    돌려준다. `INSERT ... ON CONFLICT DO UPDATE` 한 문장이라 조회 후
    분기하지 않는다 -- 두 요청이 동시에 와도 중복 행이 생기지 않는다."""

    stmt = (
        pg_insert(PushSubscription)
        .values(user_id=user_id, endpoint=endpoint, keys=dict(keys))
        .on_conflict_do_update(
            index_elements=["user_id", "endpoint"],
            set_={"keys": dict(keys)},
        )
        .returning(PushSubscription.id, literal_column("(xmax = 0)").label("inserted"))
    )
    row = session.execute(stmt).one()
    session.flush()
    return SavedSubscription(id=row.id, created=row.inserted)


def list_subscriptions(session: Session, user_id: str) -> list[PushSubscription]:
    """그 사용자(`user_id`)의 구독 전부. `user_id` 조건이 항상 걸린다
    (security.md §5, 판정 표 5행 "사용자 격리" -- 다른 사용자의 구독은
    절대 섞이지 않는다)."""

    rows = (
        session.execute(select(PushSubscription).where(PushSubscription.user_id == user_id))
        .scalars()
        .all()
    )
    return list(rows)
