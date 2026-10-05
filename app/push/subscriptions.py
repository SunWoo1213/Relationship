"""Refs: P7-push S3.1 S3.6 R12 -- U2 구독 저장(`save_subscription`·
`list_subscriptions`).

`save_subscription`: 같은 `(user_id, endpoint)` 조합이면 기존 행의
`keys` 만 갱신하고 같은 `id` 를 `created=False` 로 돌려준다. 없으면 새
행을 만들어 `created=True` 로 돌려준다(01-plan 결정 F(i) "앱에서
`(user_id, endpoint)` 로 조회 후 있으면 `keys` 만 갱신" -- 스키마
(`push_subscriptions`, S3.1)에 유일 제약이 없으므로 앱 계층에서 멱등성을
흉내낸다. 동시 요청 경쟁은 01-plan "지킬 불변식" 밖, 리스크 절 "같은
엔드포인트 경쟁" 참고 -- 이 패키지 범위에서 해결하지 않는다).

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

from sqlalchemy import select
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
    """`(user_id, endpoint)` 로 기존 행을 조회한다(결정 F(i)). 있으면
    `keys` 만 갱신하고 같은 `id` 를 `created=False` 로 돌려준다. 없으면
    새 행을 만들어 `created=True` 로 돌려준다.

    `keys` 는 통째로 새 dict 로 바꿔 넣는다(부분 갱신이 아니다) --
    `PushSubscription.keys` 는 `MutableDict` 가 아니므로 통째 재대입이어야
    SQLAlchemy 가 변경을 감지한다."""

    existing = session.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.endpoint == endpoint,
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.keys = dict(keys)
        session.flush()
        return SavedSubscription(id=existing.id, created=False)

    row = PushSubscription(user_id=user_id, endpoint=endpoint, keys=dict(keys))
    session.add(row)
    session.flush()
    return SavedSubscription(id=row.id, created=True)


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
