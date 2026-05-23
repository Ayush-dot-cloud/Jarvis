"""Intent routing for Jarvis voice commands.

The router takes a (lower-cased) utterance and returns a `Reply`:
- `Reply.text` is what Jarvis should say.
- `Reply.should_exit` is True if Jarvis should terminate.

Matching is keyword/prefix based. Anything that doesn't match a built-in
skill falls through to the OpenAI `Brain` for a free-form answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from jarvis.brain import Brain
from jarvis.config import Config
from jarvis.skills import info, media, system, utility, web


@dataclass
class Reply:
    text: str
    should_exit: bool = False


EXIT_PATTERNS = re.compile(
    r"\b(exit|quit|goodbye|good bye|bye jarvis|stop jarvis|shut down jarvis|"
    r"shutdown jarvis|that's all|that is all|sleep jarvis|go to sleep)\b"
)

GREETING_PATTERNS = re.compile(r"\b(hello|hi|hey|namaste|good morning|good evening|good afternoon)\b")

THANKS_PATTERNS = re.compile(r"\b(thank you|thanks|thank u|thx)\b")


class Router:
    def __init__(self, config: Config, brain: Brain) -> None:
        self._config = config
        self._brain = brain

    def handle(self, utterance: str) -> Reply:
        text = (utterance or "").strip().lower()
        if not text:
            return Reply(text="")

        # 1. Exit commands.
        if EXIT_PATTERNS.search(text):
            return Reply(text=f"Goodbye, {self._config.user_name}.", should_exit=True)

        # 2. Greetings.
        if GREETING_PATTERNS.search(text) and len(text.split()) <= 4:
            return Reply(text=f"Hello, {self._config.user_name}. How can I help?")

        if THANKS_PATTERNS.search(text) and len(text.split()) <= 4:
            return Reply(text="You're welcome.")

        # 3. Time / date.
        if "time" in text and ("what" in text or "tell" in text or text.strip() == "time"):
            return Reply(text=info.current_time())
        if ("date" in text or "day" in text) and ("what" in text or "today" in text or "tell" in text):
            return Reply(text=info.current_date())

        # 4. Wikipedia — only the explicit prefixes. (Generic 'who is X' / 'what is X'
        # is handled later, after we've checked weather/news/jokes/etc., so questions
        # like 'what is the weather' don't accidentally get sent to Wikipedia.)
        if text.startswith("wikipedia "):
            return Reply(text=info.wikipedia_lookup(text[len("wikipedia "):]))
        if text.startswith("search wikipedia for "):
            return Reply(text=info.wikipedia_lookup(text[len("search wikipedia for "):]))
        if text.startswith("tell me about "):
            return Reply(text=info.wikipedia_lookup(text[len("tell me about "):]))

        # 5. System control.
        if "lock" in text and ("screen" in text or "computer" in text or "pc" in text):
            return Reply(text=system.lock_screen())
        if re.search(r"\bcancel\b.*\b(shutdown|restart|shut down)\b", text):
            return Reply(text=system.cancel_shutdown())
        if re.search(r"\b(shutdown|shut down)\b.*\b(computer|pc|system|laptop)\b", text):
            return Reply(text=system.shutdown())
        if re.search(r"\b(restart|reboot)\b.*\b(computer|pc|system|laptop)\b", text):
            return Reply(text=system.restart())
        if "volume up" in text or "increase volume" in text or "louder" in text:
            return Reply(text=system.volume_up())
        if "volume down" in text or "decrease volume" in text or "quieter" in text:
            return Reply(text=system.volume_down())
        if "mute" in text:
            return Reply(text=system.volume_mute())

        # 6. Open app / site.
        if text.startswith("open "):
            target = text[len("open "):].strip()
            if target in system.KNOWN_APPS_WINDOWS:
                return Reply(text=system.open_app(target))
            return Reply(text=web.open_site(target))
        if text.startswith("launch "):
            return Reply(text=system.open_app(text[len("launch "):]))

        # 7. Media.
        if text.startswith("play music"):
            return Reply(text=media.play_music(text[len("play music"):].lstrip()))
        if text.startswith("play "):
            return Reply(text=web.play_youtube(text[len("play "):]))

        # 8. Search.
        if text.startswith("search for ") or text.startswith("google for "):
            return Reply(text=web.google_search(text.split(" ", 2)[2]))
        if text.startswith("search "):
            return Reply(text=web.google_search(text[len("search "):]))
        if text.startswith("google "):
            return Reply(text=web.google_search(text[len("google "):]))

        # 9. Utility — jokes, weather, news.
        if "joke" in text:
            return Reply(text=utility.joke())
        if "weather" in text:
            city = _extract_city(text)
            return Reply(text=utility.weather(self._config, city))
        if "news" in text or "headline" in text:
            return Reply(text=utility.news(self._config))

        # 9b. Wikipedia fallback for 'who is X' / 'what is X' (after weather/news
        # were checked so we don't steal 'what is the weather').
        if text.startswith("who is ") or text.startswith("who was "):
            return Reply(text=info.wikipedia_lookup(text.split(" ", 2)[2]))
        if text.startswith("what is ") or text.startswith("what was "):
            return Reply(text=info.wikipedia_lookup(text.split(" ", 2)[2]))

        # 10. Reset memory.
        if "reset" in text and ("memory" in text or "context" in text or "history" in text):
            self._brain.reset()
            return Reply(text="Memory cleared.")

        # 11. Fallback to OpenAI brain.
        return Reply(text=self._brain.ask(utterance))


def _extract_city(text: str) -> Optional[str]:
    """Pull a city out of phrases like 'weather in Mumbai' / 'weather at Pune'."""
    match = re.search(r"weather (?:in|at|for) ([a-zA-Z][a-zA-Z\s,]+)", text)
    if match:
        return match.group(1).strip(" .?,!")
    return None
