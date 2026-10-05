"""Refs: P7-push S3.6 R12 원칙9 -- U1 판정: `app.settings.vapid_config()`/
`push_dev_page_enabled()` 읽기 함수(기본값·오버라이드·`InvalidValue`)와
`app.push.types.VapidConfig`/`VAPID_PARTIAL`/`SendResult`/`FakePushSender`
골격(DB 없이 실행, 네트워크 호출 0)."""

from __future__ import annotations

import pytest

import app.settings as settings
from app.push.types import (
    PUSH_STATUSES,
    PUSH_TRACE_TOOL_NAME,
    SEND_OUTCOMES,
    STEP_PUSH_SEND,
    VAPID_PARTIAL,
    FakePushSender,
    SendResult,
    VapidConfig,
)
from app.tools.types import InvalidValue

# ---------------------------------------------------------------------------
# vapid_config() -- 세 이름 모두 / 전무 / 일부만 (결정 D)
# ---------------------------------------------------------------------------


def test_vapid_config_returns_none_when_all_three_names_missing() -> None:
    assert settings.vapid_config({}) is None


def test_vapid_config_returns_none_when_all_three_names_empty_string() -> None:
    env = {"VAPID_PUBLIC_KEY": "", "VAPID_PRIVATE_KEY": "", "VAPID_SUBJECT": ""}
    assert settings.vapid_config(env) is None


def test_vapid_config_returns_config_object_when_all_three_names_present() -> None:
    env = {
        "VAPID_PUBLIC_KEY": "test-public-key-value",
        "VAPID_PRIVATE_KEY": "test-private-key-value",
        "VAPID_SUBJECT": "mailto:test@example.com",
    }
    config = settings.vapid_config(env)
    assert isinstance(config, VapidConfig)
    assert config.public_key == "test-public-key-value"
    assert config.private_key == "test-private-key-value"
    assert config.subject == "mailto:test@example.com"


@pytest.mark.parametrize(
    "env",
    [
        {"VAPID_PUBLIC_KEY": "only-public"},
        {"VAPID_PRIVATE_KEY": "only-private"},
        {"VAPID_SUBJECT": "mailto:only@example.com"},
        {"VAPID_PUBLIC_KEY": "pub", "VAPID_PRIVATE_KEY": "priv"},  # subject 없음
        {"VAPID_PUBLIC_KEY": "pub", "VAPID_SUBJECT": "mailto:a@b.com"},  # private 없음
        {"VAPID_PRIVATE_KEY": "priv", "VAPID_SUBJECT": "mailto:a@b.com"},  # public 없음
    ],
)
def test_vapid_config_returns_partial_singleton_when_some_names_present(
    env: dict[str, str],
) -> None:
    result = settings.vapid_config(env)
    assert result is VAPID_PARTIAL


def test_vapid_config_subject_empty_string_counts_as_missing() -> None:
    """결정 D "VAPID_SUBJECT 가 비어 있으면 반쪽으로 본다" -- 공개키·
    개인키만 있고 subject 가 빈 문자열이면 '일부만'(반쪽)으로 본다."""
    env = {
        "VAPID_PUBLIC_KEY": "pub",
        "VAPID_PRIVATE_KEY": "priv",
        "VAPID_SUBJECT": "",
    }
    assert settings.vapid_config(env) is VAPID_PARTIAL


def test_vapid_config_uses_os_environ_when_env_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAPID_PUBLIC_KEY", "env-public")
    monkeypatch.setenv("VAPID_PRIVATE_KEY", "env-private")
    monkeypatch.setenv("VAPID_SUBJECT", "mailto:env@example.com")
    config = settings.vapid_config()
    assert isinstance(config, VapidConfig)
    assert config.public_key == "env-public"


# ---------------------------------------------------------------------------
# VapidConfig.__repr__ -- 개인키 값이 나오지 않음 (security §1)
# ---------------------------------------------------------------------------


def test_vapid_config_repr_does_not_contain_private_key_value() -> None:
    config = VapidConfig(
        public_key="pub-value-xyz",
        private_key="super-secret-private-key-value",
        subject="mailto:test@example.com",
    )
    rendered = repr(config)
    assert "super-secret-private-key-value" not in rendered
    assert "pub-value-xyz" in rendered  # 공개키는 비밀이 아니다(security §5)


def test_vapid_config_str_does_not_contain_private_key_value() -> None:
    config = VapidConfig(
        public_key="pub-value-xyz",
        private_key="super-secret-private-key-value",
        subject="mailto:test@example.com",
    )
    assert "super-secret-private-key-value" not in str(config)


def test_vapid_partial_repr_does_not_leak_which_name_was_missing() -> None:
    assert "VAPID_PUBLIC_KEY" not in repr(VAPID_PARTIAL)
    assert "VAPID_PRIVATE_KEY" not in repr(VAPID_PARTIAL)
    assert "VAPID_SUBJECT" not in repr(VAPID_PARTIAL)


# ---------------------------------------------------------------------------
# push_dev_page_enabled() -- 기본 꺼짐 / 1·true 켜짐 / 그 밖 InvalidValue
# ---------------------------------------------------------------------------


def test_push_dev_page_enabled_defaults_to_false_when_env_missing() -> None:
    assert settings.push_dev_page_enabled({}) is False


def test_push_dev_page_enabled_defaults_to_false_when_env_empty_string() -> None:
    assert settings.push_dev_page_enabled({"PUSH_DEV_PAGE_ENABLED": ""}) is False


@pytest.mark.parametrize("raw", ["1", "true"])
def test_push_dev_page_enabled_true_values(raw: str) -> None:
    assert settings.push_dev_page_enabled({"PUSH_DEV_PAGE_ENABLED": raw}) is True


@pytest.mark.parametrize("raw", ["0", "false", "yes", "TRUE", "2"])
def test_push_dev_page_enabled_invalid_raises(raw: str) -> None:
    with pytest.raises(InvalidValue):
        settings.push_dev_page_enabled({"PUSH_DEV_PAGE_ENABLED": raw})


def test_push_dev_page_enabled_uses_os_environ_when_env_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PUSH_DEV_PAGE_ENABLED", "1")
    assert settings.push_dev_page_enabled() is True


# ---------------------------------------------------------------------------
# 코드 상수 3개 (모듈 docstring "PUSH_*" 절)
# ---------------------------------------------------------------------------


def test_push_code_constants_values() -> None:
    assert settings.PUSH_TIMEOUT_SECONDS == 10.0
    assert settings.PUSH_TTL_MAX_SECONDS == 86400
    assert settings.PUSH_BODY_MAX_CHARS == 120


# ---------------------------------------------------------------------------
# app.push.types 골격 -- 상태·trace 어휘, SendResult, FakePushSender
# ---------------------------------------------------------------------------


def test_push_statuses_vocab_has_six_values() -> None:
    assert PUSH_STATUSES == (
        "sent",
        "partial",
        "failed",
        "no_subscription",
        "not_configured",
        "misconfigured",
    )


def test_send_outcomes_vocab_has_five_values() -> None:
    assert SEND_OUTCOMES == ("sent", "gone", "failed", "timeout", "error")


def test_push_trace_vocab_constants_values() -> None:
    assert PUSH_TRACE_TOOL_NAME == "push"
    assert STEP_PUSH_SEND == "push_send"


def test_send_result_to_dict_shape() -> None:
    result = SendResult(outcome="gone", status_code=410, error_class=None)
    assert result.to_dict() == {"outcome": "gone", "status_code": 410, "error_class": None}


def test_fake_push_sender_records_calls_and_default_response() -> None:
    sender = FakePushSender()
    result = sender.send(
        endpoint="https://fcm.googleapis.com/fake/endpoint-1",
        keys={"p256dh": "fake-p256dh", "auth": "fake-auth"},
        payload={"title": "t", "body": "b"},
        vapid_private_key="fake-private-key",
        vapid_subject="mailto:test@example.com",
        ttl=3600,
        timeout=10.0,
    )
    assert result == SendResult("sent", status_code=201)
    assert len(sender.calls) == 1
    assert sender.calls[0]["endpoint"] == "https://fcm.googleapis.com/fake/endpoint-1"
    assert sender.calls[0]["keys"] == {"p256dh": "fake-p256dh", "auth": "fake-auth"}


def test_fake_push_sender_uses_injected_response_table() -> None:
    endpoint = "https://fcm.googleapis.com/fake/endpoint-gone"
    sender = FakePushSender(responses={endpoint: SendResult("gone", status_code=410)})
    result = sender.send(
        endpoint=endpoint,
        keys={"p256dh": "x", "auth": "y"},
        payload={},
        vapid_private_key="fake-private-key",
        vapid_subject="mailto:test@example.com",
        ttl=60,
        timeout=10.0,
    )
    assert result == SendResult("gone", status_code=410)


def test_push_types_module_does_not_import_pywebpush() -> None:
    """결정 G -- `app/push/sender.py`(U4) 가 `pywebpush` 를 import 하는
    **유일한** 모듈이다(01-plan "지킬 불변식" `grep -rln "pywebpush"
    app/` -> 한 줄). U1 골격은 그 이름을 전혀 참조하지 않는다."""
    import inspect

    import app.push.types as push_types_module

    source = inspect.getsource(push_types_module)
    assert "pywebpush" not in source
