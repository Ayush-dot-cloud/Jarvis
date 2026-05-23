"""Unit tests for the intent router.

These tests stub the OpenAI brain and the side-effecting skills so they run
without a network, microphone, or speakers.
"""

from __future__ import annotations

from unittest import mock

import pytest

from jarvis.config import Config
from jarvis.router import Router, _extract_city


def _config() -> Config:
    return Config(
        openai_api_key="",
        openai_model="gpt-4o-mini",
        openweather_api_key="",
        news_api_key="",
        default_city="Pune",
        wake_word="jarvis",
        voice_index=0,
        voice_rate=185,
        mic_calibration_seconds=0.0,
        user_name="Sir",
    )


class _FakeBrain:
    def __init__(self) -> None:
        self.asked: list[str] = []
        self.reset_called = False

    def ask(self, text: str) -> str:
        self.asked.append(text)
        return f"brain:{text}"

    def reset(self) -> None:
        self.reset_called = True


def _router() -> tuple[Router, _FakeBrain]:
    brain = _FakeBrain()
    return Router(_config(), brain), brain  # type: ignore[arg-type]


def test_exit_phrases_set_should_exit():
    router, _ = _router()
    for phrase in ["exit", "goodbye", "stop jarvis", "go to sleep"]:
        reply = router.handle(phrase)
        assert reply.should_exit is True
        assert "goodbye" in reply.text.lower()


def test_greetings_are_short_circuited():
    router, brain = _router()
    reply = router.handle("hello")
    assert "hello" in reply.text.lower()
    assert brain.asked == []


def test_time_command_returns_time_string():
    router, _ = _router()
    reply = router.handle("what is the time")
    assert "time is" in reply.text.lower()


def test_date_command_returns_date_string():
    router, _ = _router()
    reply = router.handle("what is today's date")
    assert "today is" in reply.text.lower()


def test_wikipedia_prefix_routes_to_info_module():
    router, _ = _router()
    with mock.patch("jarvis.router.info.wikipedia_lookup", return_value="WIKI") as m:
        reply = router.handle("wikipedia python programming")
    m.assert_called_once_with("python programming")
    assert reply.text == "WIKI"


def test_open_known_app_routes_to_system_open_app():
    router, _ = _router()
    with mock.patch("jarvis.router.system.open_app", return_value="OPEN_APP") as m:
        reply = router.handle("open notepad")
    m.assert_called_once_with("notepad")
    assert reply.text == "OPEN_APP"


def test_open_unknown_app_routes_to_web_open_site():
    router, _ = _router()
    with mock.patch("jarvis.router.web.open_site", return_value="OPEN_SITE") as m:
        reply = router.handle("open youtube")
    m.assert_called_once_with("youtube")
    assert reply.text == "OPEN_SITE"


def test_play_routes_to_youtube():
    router, _ = _router()
    with mock.patch("jarvis.router.web.play_youtube", return_value="PLAY") as m:
        reply = router.handle("play despacito")
    m.assert_called_once_with("despacito")
    assert reply.text == "PLAY"


def test_play_music_routes_to_media_module():
    router, _ = _router()
    with mock.patch("jarvis.router.media.play_music", return_value="MUSIC") as m:
        reply = router.handle("play music lofi")
    m.assert_called_once_with("lofi")
    assert reply.text == "MUSIC"


def test_search_routes_to_google_search():
    router, _ = _router()
    with mock.patch("jarvis.router.web.google_search", return_value="SEARCH") as m:
        reply = router.handle("search latest python news")
    m.assert_called_once_with("latest python news")
    assert reply.text == "SEARCH"


def test_volume_up():
    router, _ = _router()
    with mock.patch("jarvis.router.system.volume_up", return_value="UP") as m:
        reply = router.handle("volume up please")
    m.assert_called_once()
    assert reply.text == "UP"


def test_joke():
    router, _ = _router()
    with mock.patch("jarvis.router.utility.joke", return_value="JOKE") as m:
        reply = router.handle("tell me a joke")
    m.assert_called_once()
    assert reply.text == "JOKE"


def test_weather_with_city_extracted():
    router, _ = _router()
    with mock.patch("jarvis.router.utility.weather", return_value="WEATHER") as m:
        reply = router.handle("what's the weather in Mumbai")
    args, _ = m.call_args
    # Router lowercases all input before matching.
    assert args[1] == "mumbai"
    assert reply.text == "WEATHER"


def test_weather_without_city_passes_none():
    router, _ = _router()
    with mock.patch("jarvis.router.utility.weather", return_value="WEATHER") as m:
        router.handle("what is the weather")
    args, _ = m.call_args
    assert args[1] is None


def test_news_routes_to_news_skill():
    router, _ = _router()
    with mock.patch("jarvis.router.utility.news", return_value="NEWS") as m:
        reply = router.handle("read me the news")
    m.assert_called_once()
    assert reply.text == "NEWS"


def test_reset_memory_calls_brain_reset():
    router, brain = _router()
    reply = router.handle("reset your memory")
    assert brain.reset_called is True
    assert "cleared" in reply.text.lower()


def test_fallback_routes_to_brain():
    router, brain = _router()
    reply = router.handle("explain quantum entanglement to me")
    assert brain.asked == ["explain quantum entanglement to me"]
    assert reply.text == "brain:explain quantum entanglement to me"


def test_empty_input_returns_empty():
    router, _ = _router()
    reply = router.handle("")
    assert reply.text == ""
    assert reply.should_exit is False


def test_extract_city_helper():
    assert _extract_city("weather in mumbai") == "mumbai"
    assert _extract_city("weather at delhi today") == "delhi today"
    assert _extract_city("weather for new york") == "new york"
    assert _extract_city("what is the weather") is None
