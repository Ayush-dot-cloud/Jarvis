"""Information lookups: time, date, Wikipedia."""

from __future__ import annotations

import datetime as _dt
import logging

try:
    import wikipedia
except ImportError:  # pragma: no cover
    wikipedia = None  # type: ignore[assignment]

log = logging.getLogger("jarvis.skills.info")


def current_time() -> str:
    now = _dt.datetime.now().strftime("%I:%M %p").lstrip("0")
    return f"The time is {now}."


def current_date() -> str:
    today = _dt.datetime.now().strftime("%A, %B %d, %Y")
    return f"Today is {today}."


def wikipedia_lookup(query: str) -> str:
    if wikipedia is None:
        return "The wikipedia package isn't installed."

    query = query.strip()
    if not query:
        return "What should I look up on Wikipedia?"

    try:
        summary = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
    except wikipedia.DisambiguationError as exc:
        options = ", ".join(exc.options[:3])
        return f"That term is ambiguous. Did you mean: {options}?"
    except wikipedia.PageError:
        return f"I couldn't find a Wikipedia page for {query}."
    except Exception as exc:  # pragma: no cover
        log.warning("Wikipedia error: %s", exc)
        return f"Wikipedia lookup failed: {exc}"

    return summary
