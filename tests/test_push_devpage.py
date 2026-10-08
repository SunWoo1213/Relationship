"""Refs: P7-push U6 결정 A -- 개발·확인 전용 구독 페이지(판정 22행).

스위치(`PUSH_DEV_PAGE_ENABLED`)가 꺼져 있으면 `/push-dev/` 세 경로가 아예
없고(404), 켜져 있으면 정적 파일 세 개만 서빙한다. 브라우저 동작은 보지 않는다
(U8 사람 확인). 여기서는 서빙·콘텐츠 타입·파일 안의 약속된 문자열·불변식을 본다.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.tools.types import InvalidValue

DEVPAGE_DIR = Path(__file__).resolve().parent.parent / "app" / "push" / "devpage"
PATHS = ("/push-dev/", "/push-dev/sw.js", "/push-dev/devpage.js")


def _client(monkeypatch: pytest.MonkeyPatch, value: str | None) -> TestClient:
    if value is None:
        monkeypatch.delenv("PUSH_DEV_PAGE_ENABLED", raising=False)
    else:
        monkeypatch.setenv("PUSH_DEV_PAGE_ENABLED", value)
    # lifespan 을 돌리지 않는다(with 없음) -- 주기 작업·DB 와 무관하게 정적 경로만 본다.
    return TestClient(create_app())


@pytest.mark.parametrize("value", [None, ""])
@pytest.mark.parametrize("path", PATHS)
def test_off_by_default_three_paths_404(
    monkeypatch: pytest.MonkeyPatch, value: str | None, path: str
) -> None:
    """꺼짐(기본·빈 값) -- 세 경로 모두 404."""
    assert _client(monkeypatch, value).get(path).status_code == 404


@pytest.mark.parametrize("value", ["1", "true"])
def test_on_serves_three_files_with_content_types(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    client = _client(monkeypatch, value)
    html = client.get("/push-dev/")
    sw = client.get("/push-dev/sw.js")
    js = client.get("/push-dev/devpage.js")
    assert html.status_code == sw.status_code == js.status_code == 200
    assert html.headers["content-type"].startswith("text/html")
    assert sw.headers["content-type"].startswith("application/javascript")
    assert js.headers["content-type"].startswith("application/javascript")
    assert 'src="/push-dev/devpage.js"' in html.text


def test_service_worker_has_push_listener_and_show_notification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text = _client(monkeypatch, "1").get("/push-dev/sw.js").text
    assert 'addEventListener("push"' in text
    assert "showNotification" in text
    assert "waitUntil" in text
    assert "postMessage" in text


def test_service_worker_sends_only_receipt_fields_to_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """페이지로 보내는 객체는 received_at·schedule_id·tag 뿐 -- title/body 를 싣지 않는다."""
    text = _client(monkeypatch, "1").get("/push-dev/sw.js").text
    match = re.search(r"var info = \{(.*?)\};", text, re.S)
    assert match is not None
    keys = set(re.findall(r"^\s*(\w+):", match.group(1), re.M))
    assert keys == {"received_at", "schedule_id", "tag"}


def test_devpage_js_subscription_flow_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    text = _client(monkeypatch, "true").get("/push-dev/devpage.js").text
    assert "/push/vapid-public-key" in text
    assert "/push/subscriptions" in text
    assert "userVisibleOnly" in text
    assert "applicationServerKey" in text
    assert "toJSON()" in text
    assert "/push-dev/sw.js" in text
    assert "requestPermission" in text


@pytest.mark.parametrize("value", ["yes", "0", "TRUE", "on"])
def test_invalid_switch_value_raises_invalid_value(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """잘못된 값은 조용히 꺼지지 않는다 -- `briefing_scheduler_enabled()` 와 같은 규약."""
    monkeypatch.setenv("PUSH_DEV_PAGE_ENABLED", value)
    with pytest.raises(InvalidValue):
        create_app()


@pytest.mark.parametrize(
    "path",
    [
        "/push-dev/../main.py",
        "/push-dev/..%2Fmain.py",
        "/push-dev/%2e%2e/main.py",
        "/push-dev/index.html",
        "/push-dev/other.js",
        "/push-dev",
    ],
)
def test_other_paths_not_served(monkeypatch: pytest.MonkeyPatch, path: str) -> None:
    """켜져 있어도 세 파일 외에는 404(경로 탐색 불가). `/push-dev` 는 리다이렉트일 수 있어 본문이 없음만 본다."""
    response = _client(monkeypatch, "1").get(path, follow_redirects=False)
    assert response.status_code in (404, 307)
    assert "create_app" not in response.text


def test_invariant_no_product_data_endpoints_in_devpage() -> None:
    """확인 페이지는 인물·브리핑 자료를 조회하지 않는다(01-plan 불변식)."""
    pattern = re.compile(r"/chat|/briefings|/persons|/answers")
    for name in ("index.html", "sw.js", "devpage.js"):
        assert pattern.search((DEVPAGE_DIR / name).read_text(encoding="utf-8")) is None, name


def test_invariant_no_external_urls_or_inline_script() -> None:
    """외부 CDN·스크립트 없음, 인라인 스크립트 없음."""
    for name in ("index.html", "sw.js", "devpage.js"):
        assert "http" not in (DEVPAGE_DIR / name).read_text(encoding="utf-8"), name
    html = (DEVPAGE_DIR / "index.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S)
    assert scripts, "devpage.js 를 불러오는 script 태그가 있어야 한다"
    assert all(body.strip() == "" for body in scripts), "인라인 스크립트 금지"
    assert 'src="/push-dev/devpage.js"' in html


def test_invariant_page_does_not_draw_title_or_body() -> None:
    """수신 기록 줄은 title/body(인물 이름·제안 문구)를 DOM 에 그리지 않는다."""
    text = (DEVPAGE_DIR / "devpage.js").read_text(encoding="utf-8")
    assert re.search(r"\.(title|body)\b", text) is None
    assert "event.data" in text  # 수신 기록 객체(received_at 등)만 받는다
