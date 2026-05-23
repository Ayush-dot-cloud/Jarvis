"""
Core Jarvis assistant – orchestrates listening, command routing, and speaking.
"""

import logging

from jarvis.config import ASSISTANT_NAME, GREETING, WAKE_WORD
from jarvis.speech import Speaker, Listener
from jarvis.commands import route_command

logger = logging.getLogger(__name__)


class Jarvis:
    """Main assistant controller."""

    def __init__(self):
        self.speaker = Speaker()
        self.listener = Listener()
        self.running = False

    # ── Public API ────────────────────────────────────────────────────────

    def greet(self) -> None:
        """Greet the user."""
        self.speaker.say(GREETING)

    def start(self) -> None:
        """Start the listen → respond loop."""
        self.running = True
        self.greet()

        while self.running:
            query = self.listener.listen()
            if not query:
                continue

            # Check for wake word (optional continuous-listen mode)
            if WAKE_WORD and not self._contains_wake_word(query):
                continue

            # Strip wake word from query
            query = self._strip_wake_word(query)

            # Exit commands
            if self._is_exit_command(query):
                self.speaker.say("Goodbye! Have a great day.")
                self.stop()
                break

            self._handle(query)

    def stop(self) -> None:
        """Stop the assistant."""
        self.running = False
        logger.info("%s stopped.", ASSISTANT_NAME)

    # ── Internals ─────────────────────────────────────────────────────────

    def _handle(self, query: str) -> None:
        """Route the query and speak the response."""
        response = route_command(query)
        if response:
            self.speaker.say(response)
        else:
            self.speaker.say(
                "I'm not sure how to help with that yet. "
                "Try asking about the time, weather, or say 'open YouTube'."
            )

    @staticmethod
    def _contains_wake_word(query: str) -> bool:
        return WAKE_WORD in query

    @staticmethod
    def _strip_wake_word(query: str) -> str:
        return query.replace(WAKE_WORD, "").strip()

    @staticmethod
    def _is_exit_command(query: str) -> bool:
        exit_phrases = [
            "exit", "quit", "stop", "bye", "goodbye",
            "shutdown", "shut down", "go to sleep", "sleep",
        ]
        return any(phrase in query for phrase in exit_phrases)
