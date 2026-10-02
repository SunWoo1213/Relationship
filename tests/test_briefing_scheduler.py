"""Refs: P6-briefing S3.6 R12 원칙8 -- U7 1분 주기 작업 테스트(01-plan
판정 표 3·25·26행).

`app/briefing/scheduler.py` 의 `run_scheduler_loop`/`start_scheduler_task`
는 간격·실행 함수를 테스트가 주입할 수 있게 지어졌다(모듈 docstring
"테스트가 간격·실행 함수를 주입하는 방법" 절) -- 이 파일은 그 주입
경로로 실 시간 1분을 기다리지 않고(짧은 간격 0.02초 + 넉넉한 여유
0.3초 안팎) 스위치 on/off·내구성·종료 시 취소를 확인한다.

`with TestClient(create_app()) as client:` 로 **반드시 컨텍스트 매니저로
진입**해야 lifespan 이 실제로 돈다(그냥 `TestClient(app)` 은 lifespan을
부르지 않는다 -- `tests/test_api.py`·`test_api_chat.py` 등 기존 파일이
전부 `with` 없이 쓰는 이유이기도 하다, 그래서 그 파일들은 스위치가
기본 꺼짐이든 아니든 애초에 영향을 받지 않는다. 판정 표 25·26행과 함께
적은 "기존 `TestClient` 사용 테스트 4파일 회귀"는 이 파일이 아니라
별도로 그 4파일을 그대로 재실행해 확인한다).

판정 3행("같은 `run_briefings` 객체")은 실 DB 세션을 여는
`default_run_once()`(`session_scope()`)와 `POST /briefings/run` 엔드포인트
양쪽을 한 테스트에서 돌리므로 `dbtest` 마커가 필요하다 -- 그 밖의
테스트(스위치 on/off·내구성·잘못된 스위치 값)는 주입한 가짜 `run_once`
가 DB 를 전혀 건드리지 않으므로 마커가 없다(`tests/test_briefing_select.py`
의 "-k constants" 절과 같은 관례 -- 실제로 픽스처를 쓰는 테스트에만
마커를 붙인다).
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes_module
import app.briefing.run as run_module
import app.briefing.scheduler as scheduler_module
from app.api.deps import get_briefing_composer, get_now, get_session
from app.briefing.compose import FakeBriefingComposer
from app.main import create_app
from app.tools.types import InvalidValue

#: 테스트 전용 짧은 간격(초). 01-plan U7 "실 시간 1분을 기다리지 않는다".
_FAST_INTERVAL = 0.02

#: 루프가 몇 주기 돌 시간을 벌어 주는 대기(초) -- `_FAST_INTERVAL` 의 10배
#: 이상이라 최소 10회는 돈다. 전체 테스트가 매달리지 않도록 1초를 넘기지
#: 않는다(하드 상한).
_WAIT = 0.3

#: `POST /briefings/run`(판정 3행 전용) 창 선정의 기준 "지금".
_NOW = datetime(2026, 4, 1, 9, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 판정 25 -- 스위치 on/off, 종료 시 취소
# ---------------------------------------------------------------------------


def test_scheduler_disabled_by_default_does_not_call_run_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """스위치를 비워 두면(기본값) `TestClient` 컨텍스트에 들어가도 주입한
    실행 함수가 한 번도 불리지 않는다(판정 25 "꺼짐")."""

    monkeypatch.delenv("BRIEFING_SCHEDULER_ENABLED", raising=False)
    calls: list[int] = []
    monkeypatch.setattr(scheduler_module, "BRIEFING_INTERVAL_SECONDS", _FAST_INTERVAL)
    monkeypatch.setattr(scheduler_module, "default_run_once", lambda: calls.append(1))

    with TestClient(create_app()):
        time.sleep(_WAIT)

    assert calls == []


def test_scheduler_enabled_calls_run_once_and_stops_after_context_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """스위치를 켜면 간격마다 주입한 실행 함수가 불리고(호출 ≥ 1), 컨텍스트
    (앱) 종료 뒤에는 태스크가 취소·완료되어 더 이상 불리지 않는다(판정 25
    "켜짐" + 종료 확인). "더 이상 불리지 않는다"를 직접 보이기 위해
    컨텍스트를 나온 뒤 한 번 더 같은 길이만큼 기다려 호출 수가 더
    늘지 않는지 본다 -- 태스크가 살아 있었다면 이 사이에 적어도 한 번은
    더 불렸을 것이다(간격이 대기 시간의 1/15 수준이므로)."""

    monkeypatch.setenv("BRIEFING_SCHEDULER_ENABLED", "1")
    calls: list[int] = []
    monkeypatch.setattr(scheduler_module, "BRIEFING_INTERVAL_SECONDS", _FAST_INTERVAL)
    monkeypatch.setattr(scheduler_module, "default_run_once", lambda: calls.append(1))

    with TestClient(create_app()):
        time.sleep(_WAIT)
        count_during = len(calls)

    assert count_during >= 1

    count_at_exit = len(calls)
    time.sleep(_WAIT)
    assert len(calls) == count_at_exit, (
        "컨텍스트 종료 뒤에도 호출 수가 늘었다 -- 태스크가 취소되지 않고 계속 돌고 있다"
    )


# ---------------------------------------------------------------------------
# 판정 26 -- 내구성(한 주기의 예외가 다음 주기를 막지 않는다)
# ---------------------------------------------------------------------------


def test_scheduler_keeps_running_after_run_once_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """주입한 실행 함수가 첫 호출에서 예외를 내도 루프는 죽지 않고 다음
    주기에 다시 불린다(판정 26)."""

    monkeypatch.setenv("BRIEFING_SCHEDULER_ENABLED", "1")
    calls: list[int] = []

    def _flaky_run_once() -> None:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom -- 첫 호출만 일부러 실패")

    monkeypatch.setattr(scheduler_module, "BRIEFING_INTERVAL_SECONDS", _FAST_INTERVAL)
    monkeypatch.setattr(scheduler_module, "default_run_once", _flaky_run_once)

    with TestClient(create_app()):
        time.sleep(_WAIT)

    # 첫 호출은 예외를 냈으니(기록만 되고 결과에 반영 안 됨) 적어도 2회 이상
    # 불려야 "다음 주기에 다시 호출됨" 이 성립한다.
    assert len(calls) >= 2


# ---------------------------------------------------------------------------
# 지킬 불변식 -- 잘못된 스위치 값은 앱 시작 자체를 실패시킨다(원칙8)
# ---------------------------------------------------------------------------


def test_invalid_switch_value_fails_app_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    """`BRIEFING_SCHEDULER_ENABLED` 가 `1`/`true`/빈 문자열이 아니면 조용히
    꺼진 채로 넘어가지 않고 lifespan 시작이 그대로 실패한다(원칙8)."""

    monkeypatch.setenv("BRIEFING_SCHEDULER_ENABLED", "yes-please")

    with pytest.raises(InvalidValue):
        with TestClient(create_app()):
            pass  # pragma: no cover -- 시작 단계에서 이미 예외가 난다.


# ---------------------------------------------------------------------------
# 판정 3 -- 엔드포인트(U6)와 주기 작업(U7)이 같은 run_briefings 를 부른다
# ---------------------------------------------------------------------------

@pytest.mark.dbtest
def test_manual_endpoint_and_scheduler_call_the_same_run_briefings_object(
    monkeypatch: pytest.MonkeyPatch, db_session
) -> None:
    """`app/api/routes.py`(U6)와 `app/briefing/scheduler.py`(U7)는 **같은**
    `app.briefing.run.run_briefings` 객체를 참조하고(정적 확인), 실제로
    불러 보면 `trigger` 값만 `manual`/`scheduler` 로 다르다(01-plan
    판정 표 3행)."""

    # 정적 확인 -- 세 이름이 전부 같은 함수 객체를 가리킨다(모듈이 각자
    # `from app.briefing(.run) import run_briefings` 로 들여온 이름이지만,
    # 바인딩된 객체 자체는 하나다).
    assert routes_module.run_briefings is scheduler_module.run_briefings is run_module.run_briefings

    calls: list[dict[str, Any]] = []

    def _fake_run_briefings(ctx, **kwargs: Any):
        calls.append(kwargs)
        return SimpleNamespace(
            session_id="fake-run-id",
            now=_NOW,
            briefings=[],
            skipped=[],
            errors=0,
        )

    # "가짜로 바꿔 끼움" -- 엔드포인트가 보는 이름과 주기 작업이 보는
    # 이름 양쪽을 **같은** 가짜로 바꾼다. 주기 작업 쪽은 실 LLM 공급자
    # 선택(`composer_from_env()`)도 네트워크 0 인 가짜로 바꾼다 --
    # `run_briefings` 자체가 가짜라 composer 값은 쓰이지 않지만, 호출
    # 표현식(`composer=composer_from_env()`)은 여전히 평가되므로 키
    # 없이도 안전하게 두기 위함이다(원칙8 -- 네트워크 0).
    monkeypatch.setattr(routes_module, "run_briefings", _fake_run_briefings)
    monkeypatch.setattr(scheduler_module, "run_briefings", _fake_run_briefings)
    monkeypatch.setattr(scheduler_module, "composer_from_env", lambda: FakeBriefingComposer())

    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_now] = lambda: (lambda: _NOW)
    app.dependency_overrides[get_briefing_composer] = lambda: FakeBriefingComposer()
    client = TestClient(app)

    resp = client.post("/briefings/run")
    assert resp.status_code == 200

    scheduler_module.default_run_once()

    assert len(calls) == 2
    triggers = {call["trigger"] for call in calls}
    assert triggers == {"manual", "scheduler"}
