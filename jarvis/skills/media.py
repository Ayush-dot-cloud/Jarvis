"""Media playback shortcuts (just wraps YouTube for music for now)."""

from __future__ import annotations

from jarvis.skills.web import play_youtube


def play_music(query: str) -> str:
    if not query.strip():
        query = "lofi hip hop radio"
    return play_youtube(query)
