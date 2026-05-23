"""Web-related skills: open websites, Google search, YouTube."""

from __future__ import annotations

import logging
import urllib.parse
import webbrowser
from typing import Any, Optional

log = logging.getLogger("jarvis.skills.web")


def _get_pywhatkit() -> Optional[Any]:
    """Import pywhatkit lazily.

    pywhatkit -> pyautogui -> mouseinfo eagerly opens an X `Display`, which
    fails on headless Linux (e.g. CI) with `KeyError: 'DISPLAY'`. Loading it
    lazily lets the rest of the module import cleanly on any platform.
    """
    try:
        import pywhatkit  # noqa: WPS433 - intentional local import

        return pywhatkit
    except Exception as exc:  # pragma: no cover - depends on platform
        log.debug("pywhatkit unavailable: %s", exc)
        return None


KNOWN_SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "stack overflow": "https://stackoverflow.com",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "chatgpt": "https://chat.openai.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
}


def open_site(name: str) -> str:
    name = name.strip().lower()
    if not name:
        return "Which site should I open?"
    url = KNOWN_SITES.get(name)
    if url is None:
        if "." in name:
            url = name if name.startswith("http") else f"https://{name}"
        else:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(name)}"
            webbrowser.open(search_url)
            return f"Searching Google for {name}."
    webbrowser.open(url)
    return f"Opening {name}."


def google_search(query: str) -> str:
    query = query.strip()
    if not query:
        return "What should I search for?"
    pwk = _get_pywhatkit()
    if pwk is not None:
        try:
            pwk.search(query)
            return f"Searching Google for {query}."
        except Exception as exc:  # pragma: no cover
            log.warning("pywhatkit.search failed, falling back: %s", exc)
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    webbrowser.open(url)
    return f"Searching Google for {query}."


def play_youtube(query: str) -> str:
    query = query.strip()
    if not query:
        return "What should I play on YouTube?"
    pwk = _get_pywhatkit()
    if pwk is not None:
        try:
            pwk.playonyt(query)
            return f"Playing {query} on YouTube."
        except Exception as exc:  # pragma: no cover
            log.warning("pywhatkit.playonyt failed, falling back: %s", exc)
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}."
