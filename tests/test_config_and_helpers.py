"""Tests for config loading and small helpers."""

from __future__ import annotations

import os
from unittest import mock

from jarvis.config import load_config
from jarvis.main import _strip_wake_word


def test_load_config_uses_defaults_when_env_missing():
    with mock.patch.dict(os.environ, {}, clear=True):
        config = load_config()
    assert config.openai_model == "gpt-4o-mini"
    assert config.wake_word == "jarvis"
    assert config.user_name == "Sir"
    assert config.voice_rate == 185
    assert config.has_openai is False
    assert config.has_weather is False
    assert config.has_news is False


def test_load_config_respects_env():
    env = {
        "OPENAI_API_KEY": "sk-real-key",
        "OPENAI_MODEL": "gpt-4o",
        "WAKE_WORD": "friday",
        "USER_NAME": "Tony",
        "VOICE_RATE": "150",
        "VOICE_INDEX": "1",
        "MIC_CALIBRATION_SECONDS": "0.5",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        config = load_config()
    assert config.openai_api_key == "sk-real-key"
    assert config.openai_model == "gpt-4o"
    assert config.wake_word == "friday"
    assert config.user_name == "Tony"
    assert config.voice_rate == 150
    assert config.voice_index == 1
    assert config.mic_calibration_seconds == 0.5
    assert config.has_openai is True


def test_load_config_ignores_placeholder_key():
    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-your-openai-key-here"}, clear=True):
        config = load_config()
    assert config.has_openai is False


def test_strip_wake_word_returns_command_when_present():
    assert _strip_wake_word("jarvis what time is it", "jarvis") == "what time is it"
    assert _strip_wake_word("hey jarvis open notepad", "jarvis") == "open notepad"


def test_strip_wake_word_returns_none_when_absent():
    assert _strip_wake_word("what time is it", "jarvis") is None


def test_strip_wake_word_empty_wake_word_returns_input():
    assert _strip_wake_word("anything goes", "") == "anything goes"
