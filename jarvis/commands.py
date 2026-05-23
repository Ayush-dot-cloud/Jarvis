"""
Command handlers for Jarvis.

Each public function accepts a query string and returns a response string.
"""

import datetime
import logging
import os
import subprocess
import webbrowser

import requests
import wikipedia
import pyjokes

from jarvis.config import WEATHER_API_KEY

logger = logging.getLogger(__name__)


# ── Informational ────────────────────────────────────────────────────────────

def get_time(_query: str = "") -> str:
    """Return the current time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The time is {now}."


def get_date(_query: str = "") -> str:
    """Return today's date."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    return f"Today is {today}."


def get_weather(query: str) -> str:
    """Fetch current weather for a city using OpenWeatherMap."""
    if not WEATHER_API_KEY:
        return "Weather API key is not configured. Set the WEATHER_API_KEY environment variable."

    # Try to extract city name from query
    city = "Delhi"  # default
    keywords = ["weather in", "weather of", "weather for", "weather at"]
    for kw in keywords:
        if kw in query:
            city = query.split(kw)[-1].strip()
            break

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"It's currently {temp}°C with {desc} in {city}."
        return f"Could not get weather data for {city}."
    except Exception as exc:
        logger.error("Weather API error: %s", exc)
        return "Sorry, I couldn't fetch the weather right now."


def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a summary."""
    search_term = query.replace("wikipedia", "").replace("search", "").strip()
    if not search_term:
        return "What would you like me to search on Wikipedia?"
    try:
        result = wikipedia.summary(search_term, sentences=2)
        return result
    except wikipedia.DisambiguationError as exc:
        return f"Multiple results found. Try being more specific: {exc.options[:5]}"
    except wikipedia.PageError:
        return f"No Wikipedia page found for '{search_term}'."
    except Exception as exc:
        logger.error("Wikipedia error: %s", exc)
        return "Sorry, Wikipedia search failed."


# ── Web / Apps ────────────────────────────────────────────────────────────────

def open_website(query: str) -> str:
    """Open a website in the default browser."""
    sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com",
        "whatsapp": "https://web.whatsapp.com",
    }
    for name, url in sites.items():
        if name in query:
            webbrowser.open(url)
            return f"Opening {name}."
    # Fallback – try to build URL from query
    term = query.replace("open", "").strip().replace(" ", "")
    if term:
        webbrowser.open(f"https://www.{term}.com")
        return f"Opening {term}.com."
    return "Which website would you like me to open?"


def google_search(query: str) -> str:
    """Search Google for the given query."""
    search_term = query.replace("google", "").replace("search", "").strip()
    if search_term:
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
        return f"Here are the Google results for '{search_term}'."
    return "What should I search for?"


def play_youtube(query: str) -> str:
    """Search and open YouTube."""
    search_term = (
        query.replace("play", "")
        .replace("youtube", "")
        .replace("on", "")
        .strip()
    )
    if search_term:
        webbrowser.open(
            f"https://www.youtube.com/results?search_query={search_term}"
        )
        return f"Searching YouTube for '{search_term}'."
    return "What would you like to play on YouTube?"


# ── System ────────────────────────────────────────────────────────────────────

def open_application(query: str) -> str:
    """Open a desktop application (Windows)."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
    }
    for name, exe in apps.items():
        if name in query:
            try:
                subprocess.Popen(exe)
                return f"Opening {name}."
            except Exception as exc:
                logger.error("Failed to open %s: %s", name, exc)
                return f"Sorry, I couldn't open {name}."
    return "Which application would you like me to open?"


def system_info(_query: str = "") -> str:
    """Return basic system information."""
    import platform

    info = (
        f"System: {platform.system()} {platform.release()}\n"
        f"Machine: {platform.machine()}\n"
        f"Processor: {platform.processor()}\n"
        f"Python: {platform.python_version()}"
    )
    return info


# ── Fun ───────────────────────────────────────────────────────────────────────

def tell_joke(_query: str = "") -> str:
    """Tell a programming joke."""
    return pyjokes.get_joke()


# ── Command Router ────────────────────────────────────────────────────────────

COMMAND_MAP: list[tuple[list[str], callable]] = [
    (["time"], get_time),
    (["date", "today"], get_date),
    (["weather", "temperature"], get_weather),
    (["wikipedia", "wiki"], search_wikipedia),
    (["play", "youtube"], play_youtube),
    (["google", "search for"], google_search),
    (["open notepad", "open calculator", "open paint", "open cmd",
      "open explorer", "open task manager"], open_application),
    (["open"], open_website),
    (["joke", "funny"], tell_joke),
    (["system info", "system information"], system_info),
]


def route_command(query: str) -> str | None:
    """
    Match the query against known command triggers.
    Returns the command response, or None if no match is found.
    """
    for triggers, handler in COMMAND_MAP:
        for trigger in triggers:
            if trigger in query:
                return handler(query)
    return None
