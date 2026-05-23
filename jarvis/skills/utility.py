"""Misc utility skills: jokes, weather, news."""

from __future__ import annotations

import logging
from typing import Optional

import requests

try:
    import pyjokes
except ImportError:  # pragma: no cover
    pyjokes = None  # type: ignore[assignment]

from jarvis.config import Config

log = logging.getLogger("jarvis.skills.utility")


def joke() -> str:
    if pyjokes is None:
        return "I'd love to tell you a joke but pyjokes isn't installed."
    try:
        return pyjokes.get_joke()
    except Exception as exc:  # pragma: no cover
        return f"Joke failed: {exc}"


def weather(config: Config, city: Optional[str] = None) -> str:
    if not config.has_weather:
        return (
            "I need an OpenWeatherMap API key to check the weather. "
            "Add OPENWEATHER_API_KEY to your .env file."
        )
    target_city = (city or config.default_city or "").strip()
    if not target_city:
        return "Which city's weather should I check?"

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": target_city,
                "appid": config.openweather_api_key,
                "units": "metric",
            },
            timeout=10,
        )
    except requests.RequestException as exc:
        return f"Weather request failed: {exc}"

    if response.status_code == 404:
        return f"I couldn't find a city called {target_city}."
    if response.status_code != 200:
        return f"Weather service returned an error: {response.status_code}."

    data = response.json()
    description = data.get("weather", [{}])[0].get("description", "unknown conditions")
    temp = data.get("main", {}).get("temp")
    feels_like = data.get("main", {}).get("feels_like")
    humidity = data.get("main", {}).get("humidity")

    parts = [f"In {target_city}, it's {description}"]
    if temp is not None:
        parts.append(f"with a temperature of {round(temp)} degrees Celsius")
    if feels_like is not None:
        parts.append(f"feels like {round(feels_like)}")
    if humidity is not None:
        parts.append(f"humidity {humidity} percent")
    return ", ".join(parts) + "."


def news(config: Config, country: str = "us", limit: int = 5) -> str:
    if not config.has_news:
        return (
            "I need a NewsAPI key to fetch headlines. "
            "Add NEWS_API_KEY to your .env file."
        )
    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": country, "pageSize": limit, "apiKey": config.news_api_key},
            timeout=10,
        )
    except requests.RequestException as exc:
        return f"News request failed: {exc}"

    if response.status_code != 200:
        return f"News service returned an error: {response.status_code}."

    articles = response.json().get("articles", [])
    if not articles:
        return "No headlines available right now."

    headlines = [a.get("title", "").strip() for a in articles if a.get("title")]
    summary = ". ".join(headlines[:limit])
    return f"Here are today's top headlines. {summary}."
