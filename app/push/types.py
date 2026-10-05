"""Refs: P7-push S3.6 R12 원칙9 -- U1 골격(상태 어휘 + trace 어휘 +
`SendResult`/`VapidConfig` + `PushSender` Protocol + `FakePushSender`).
도는 발송 로직은 없다.

## 이 모듈이 하지 않는 것

- 실제 발송(`PyWebPushSender`, `app/push/sender.py`)·알림기(`WebPushNotifier`,
  `app/push/notifier.py`)·구독 저장(`app/push/subscriptions.py`)·본문
  작성(`app/push/payload.py`)을 담지 않는다 -- 전부 U2~U4 몫(01-plan
  "산출물" 절). 이 모듈은 그것들이 공유하는 결과 타입·어휘만 고정한다.
- `requirements.txt`(결정 D)에 새로 고정한 VAPID 발송 라이브러리를
  import 하지 않는다. **그 라이브러리를 import 하는 유일한 모듈은 U4
  의 `app/push/sender.py` 다**(01-plan 결정 G "지킬 불변식" -- 그 이름이
  `app/` 안에 단 한 파일에서만 나타나야 한다. 이 모듈·docstring 은
  의도적으로 그 라이브러리 이름 문자열을 쓰지 않는다 -- 글자 그대로
  적으면 그 불변식 grep 이 이 파일도 집어 다단히 깨진다). `PushSender`
  Protocol 은 구조적 타입일 뿐이고, `FakePushSender` 는 네트워크·암호
  라이브러리 없이 동작한다(원칙8 -- 자동 테스트는 전부 가짜 발송기).
- DB(SQLAlchemy 모델)를 import 하지 않는다 -- `app/briefing/types.py`·
  `app/memory/types.py` 와 같은 관례(순수 데이터클래스·상수).

## 이 모듈이 고정하는 것

- `PUSH_STATUSES` -- 일정 하나에 대한 발송 **결과 상태** 어휘 6종(결정
  C·E, `WebPushNotifier.notify()`(U4)·`run_briefings()` 응답
  `briefings[].push`(P6-briefing, 무변경)가 돌려주는 문자열 그대로):
  `sent`(구독 전부 성공) / `partial`(일부만 성공) / `failed`(전부 실패) /
  `no_subscription`(그 사용자의 구독이 0건) / `not_configured`(VAPID 키
  전무, 지금까지의 `NullNotifier` 와 같음) / `misconfigured`(VAPID 키
  일부만 설정 -- 결정 D "반쪽").
- `SEND_OUTCOMES` -- 구독 **하나**에 대한 발송 시도 결과 어휘 5종(판정
  18행 "발송기 예외 매핑"): `sent`(2xx) / `gone`(404·410, 결정 E "행
  삭제") / `failed`(그 밖 HTTP 오류, `status_code` 보존) /
  `timeout`(시간 초과) / `error`(그 밖 예외 -- `error_class` 에 **예외
  클래스 이름만** 담는다, security §1 "메시지에 엔드포인트·응답 본문이
  섞이는 것을 막는다", 02-plan-verify 권고 R-8).
- `SendResult` -- 위 `PushSender.send()`(U4 가 구현)의 반환 타입.
- `VapidConfig`/`VAPID_PARTIAL` -- `app.settings.vapid_config()` 가
  돌려주는 세 가지 값(`VapidConfig` 객체 / `None` / `VAPID_PARTIAL`
  싱글톤, 결정 D "세 이름 모두/전무/일부만"). `VapidConfig` 는 `repr`/
  `str` 에 개인키 **값**이 나오지 않도록 직접 `__repr__` 을 정의한다
  (U1 판정 "설정 객체의 repr 에 개인키 값이 나오지 않음", security §1).
  이 타입을 `app/push/types.py`(DB·LLM 미의존)에 두는 이유는
  `app.er.types.ERConfig` 를 `app.settings.er_config()` 가 지연
  import 하는 것과 같다(순환 import 회피 -- `app.settings` 는 이미
  여러 곳에서 import 되므로 이 모듈 쪽이 지연 import 를 받는 쪽이다).
- `PushSender` Protocol -- VAPID 서명·암호화 발송 한 건을 맡는 자리
  (결정 D·G). 구현체(U4 `PyWebPushSender`)는 예외를 밖으로 올리지
  않고 `SendResult` 로 변환해 돌려준다 -- 이 모듈은 시그니처만 고정한다.
- `FakePushSender` -- 테스트 전용 결정적 `PushSender`(원칙8, 결정 G
  "테스트는 가짜 발송기만"). `responses` = `{endpoint: SendResult}`
  미리 정한 응답 표(엔드포인트별 `SendResult` 주입) -- 표에 없는
  엔드포인트는 기본값 `SendResult("sent", status_code=201)`.
  `calls` 로 호출 인자를 그대로 기록한다(판정 19·20행 "비밀 미기록"
  검사는 **trace**·**응답 본문**에 비밀이 없는지를 보는 것이지 이
  기록 자체를 금지하는 것이 아니다 -- 테스트가 직접 넣은 테스트용
  엔드포인트·키이므로 실비밀이 아니다). 네트워크 호출 0(원칙8).
- `PUSH_TRACE_TOOL_NAME`("push")·`STEP_PUSH_SEND`("push_send") --
  `agent_traces.tool_name`/`.step` 의 단일 출처(결정 F). `app.agent.
  types.LOOP_TRACE_TOOL_NAME`("agent")·`app.er.types.ER_TRACE_TOOL_NAME`
  ("er")·`app.memory.types.MEMORY_TRACE_TOOL_NAME`("memory")·`app.
  briefing.types.BRIEFING_TRACE_TOOL_NAME`("briefing") 과 같은 층위이고
  겹치지 않는다. 일정 발송 1회당 `push_send` 1행(결정 F, U4 가 채운다
  -- 이 모듈은 로직이 없으므로 trace 를 직접 쓰지 않는다).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

# ---------------------------------------------------------------------------
# 상태 어휘 (결정 C·E -- 일정 하나에 대한 발송 결과)
# ---------------------------------------------------------------------------

#: `WebPushNotifier.notify()`(U4)·응답 `briefings[].push`(P6-briefing,
#: 무변경)가 돌려주는 상태 문자열 6종. 순서는 01-plan 산출물 절 나열
#: 그대로다.
PUSH_STATUSES: tuple[str, ...] = (
    "sent",
    "partial",
    "failed",
    "no_subscription",
    "not_configured",
    "misconfigured",
)

# ---------------------------------------------------------------------------
# 구독 하나의 발송 시도 결과 (판정 18행 -- U4 `PyWebPushSender`/
# `WebPushNotifier` 가 쓴다. 이 모듈은 타입만 고정한다)
# ---------------------------------------------------------------------------

#: `SendResult.outcome` 어휘 5종(판정 18행 "발송기 예외 매핑").
SEND_OUTCOMES: tuple[str, ...] = ("sent", "gone", "failed", "timeout", "error")


@dataclass(frozen=True)
class SendResult:
    """구독 하나에 대한 발송 시도 한 번의 결과(판정 18행). `outcome` 은
    `SEND_OUTCOMES` 중 하나. `status_code` 는 `sent`/`gone`/`failed` 일
    때만 채워진다(푸시 서비스가 돌려준 HTTP 상태 코드 -- 엔드포인트·
    구독 키 값은 이 타입에 담지 않는다, security §1). `error_class` 는
    `error` 일 때만 채워지며 **예외 클래스 이름 문자열만**(`str(exc)`
    메시지 자체는 담지 않는다 -- 발송 라이브러리의 예외 클래스의
    메시지에는 엔드포인트·응답 본문이 섞일 수 있다, 02-plan-verify
    권고 R-8)."""

    outcome: str
    status_code: int | None = None
    error_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """`push_send` trace `output.results[]` 항목 모양(결정 F, U4 가
        `WebPushNotifier.notify()` 에서 채운다). `@traced`(`app.tools.
        context.to_jsonable`)가 이 메서드를 우선 쓴다 -- `PatternChange.
        to_dict()` 와 같은 이유."""

        return {
            "outcome": self.outcome,
            "status_code": self.status_code,
            "error_class": self.error_class,
        }


# ---------------------------------------------------------------------------
# VAPID 설정 (결정 D -- `app.settings.vapid_config()` 의 반환 타입)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VapidConfig:
    """VAPID 키 설정 하나(결정 D). 세 이름(`VAPID_PUBLIC_KEY`/
    `VAPID_PRIVATE_KEY`/`VAPID_SUBJECT`) 이 **모두** 있을 때만 만들어진다
    (`app.settings.vapid_config()`). `__repr__` 을 직접 정의해 개인키
    **값**이 로그·에러 메시지·디버거 출력에 나오지 않게 한다(security
    §1, U1 판정 "repr 에 개인키 값이 나오지 않음") -- `@dataclass` 는
    클래스가 이미 `__repr__` 을 정의하면 자동 생성하지 않는다."""

    public_key: str
    private_key: str
    subject: str

    def __repr__(self) -> str:  # noqa: D105 -- 의도적으로 개인키 값을 가린다.
        return (
            "VapidConfig(public_key="
            f"{self.public_key!r}, private_key='***', subject={self.subject!r})"
        )


class _VapidPartial:
    """`vapid_config()`(`app.settings`) 가 세 이름 중 **일부만** 있을 때
    돌려주는 싱글톤 표시자(결정 D "반쪽"). `VapidConfig` 도 `None` 도
    아니다 -- `notifier_from_env()`(U4)가 `is VAPID_PARTIAL` 로 구분해
    상태 `"misconfigured"` 인 알림기를 돌려준다. 어떤 이름이 비어
    있었는지조차 담지 않는다(security §1 -- "조용히 꺼진 것처럼 보이지
    않게" 알리는 것이 목적이지, 설정값 자체를 노출하는 것이 아니다)."""

    def __repr__(self) -> str:
        return "VAPID_PARTIAL"


#: 모듈 전역 싱글톤(비교는 `is` 로 한다. `_VapidPartial()` 을 새로
#: 만들지 않는다 -- 단일 출처).
VAPID_PARTIAL = _VapidPartial()


# ---------------------------------------------------------------------------
# 발송기 자리 (결정 D·G -- U4 `PyWebPushSender` 가 구현. 이 모듈은
# 시그니처만 고정한다)
# ---------------------------------------------------------------------------


class PushSender(Protocol):
    """VAPID 서명·암호화 발송 한 건을 맡는 자리(결정 D·G). 구현체
    (U4 `PyWebPushSender`)는 어떤 예외가 나도 **밖으로 올리지 않고**
    `SendResult` 로 변환해 돌려준다 -- `WebPushNotifier`(U4)가 구독마다
    이 메서드를 부른다. `timeout` 은 초 단위이며 `app.settings.
    PUSH_TIMEOUT_SECONDS` 가 기본값이다(호출자가 주입)."""

    def send(
        self,
        *,
        endpoint: str,
        keys: dict[str, str],
        payload: dict[str, Any],
        vapid_private_key: str,
        vapid_subject: str,
        ttl: int,
        timeout: float,
    ) -> SendResult: ...


@dataclass
class FakePushSender:
    """테스트 전용 결정적 `PushSender`(원칙8, 결정 G "테스트는 가짜
    발송기만" -- 네트워크 호출 0). `responses` = `{endpoint:
    SendResult}` 미리 정한 응답 표 -- 표에 없는 엔드포인트면 기본값
    `SendResult("sent", status_code=201)`.

    `calls` 로 호출 인자를 그대로 기록한다(판정 표 "발송 호출 N회"
    검사용 -- `app.memory.extract.FakeFactExtractor.call_count` 와 같은
    이유, 다만 이 타입은 인자 전체를 기록해 어떤 구독에 무엇을 보냈는지
    테스트가 직접 들여다볼 수 있게 한다). 기록되는 `endpoint`/`keys`
    값은 **테스트가 그 자리에서 만든 가짜 값**이다 -- 실제 구독 비밀을
    이 객체에 담을 일이 없다(실비밀은 U8 실발송 한정, 그때는
    `FakePushSender` 를 쓰지 않는다).
    """

    responses: dict[str, SendResult] = field(default_factory=dict)
    calls: list[dict[str, Any]] = field(default_factory=list)

    def send(
        self,
        *,
        endpoint: str,
        keys: dict[str, str],
        payload: dict[str, Any],
        vapid_private_key: str,
        vapid_subject: str,
        ttl: int,
        timeout: float,
    ) -> SendResult:
        self.calls.append(
            {
                "endpoint": endpoint,
                "keys": dict(keys),
                "payload": dict(payload),
                "ttl": ttl,
                "timeout": timeout,
            }
        )
        return self.responses.get(endpoint, SendResult("sent", status_code=201))


# ---------------------------------------------------------------------------
# agent_traces 어휘 (결정 F -- tool_name 고정 + step 1종)
# ---------------------------------------------------------------------------

#: `agent_traces.tool_name` -- 푸시 계층이 남기는 모든 행의 값(결정 F).
#: `app.agent.types.LOOP_TRACE_TOOL_NAME`("agent")·`app.er.types.
#: ER_TRACE_TOOL_NAME`("er")·`app.memory.types.MEMORY_TRACE_TOOL_NAME`
#: ("memory")·`app.briefing.types.BRIEFING_TRACE_TOOL_NAME`("briefing")
#: 과 같은 층위이며 겹치지 않는다.
PUSH_TRACE_TOOL_NAME = "push"

#: 발송 단계 -- 일정 발송 1회당 1행(결정 F, U4). tokens 는 항상 0(이
#: step 은 LLM 을 부르지 않는다).
STEP_PUSH_SEND = "push_send"
