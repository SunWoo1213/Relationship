"""Refs: P2-tools 결정9 -- app.settings.app_user_id() 해석 규칙 (DB 없이 실행)."""

from __future__ import annotations

import app.settings as settings


def test_app_user_id_defaults_to_local_when_env_not_set():
    assert settings.app_user_id({}) == "local"


def test_app_user_id_uses_env_value_when_set():
    assert settings.app_user_id({"APP_USER_ID": "demo-user-42"}) == "demo-user-42"
