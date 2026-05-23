"""Wrapper around the OpenAI client for free-form 'ask anything' questions."""

from __future__ import annotations

import logging
from typing import List, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]

from jarvis.config import Config

log = logging.getLogger("jarvis.brain")

SYSTEM_PROMPT = (
    "You are Jarvis, a concise, helpful voice assistant modelled after Tony Stark's AI. "
    "Reply in 1-3 sentences unless the user explicitly asks for detail. "
    "Speak naturally — your responses will be read aloud, so avoid markdown, bullet points, "
    "code blocks, or formatting that doesn't sound natural when spoken. "
    "Refer to the user as 'sir' occasionally but not in every reply."
)


class Brain:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = None
        self._history: List[Dict[str, str]] = []
        if config.has_openai:
            if OpenAI is None:
                raise RuntimeError("openai package not installed. Run: pip install -r requirements.txt")
            self._client = OpenAI(api_key=config.openai_api_key)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def ask(self, user_text: str) -> str:
        if not self.enabled:
            return (
                "My OpenAI key isn't configured, so I can't answer freeform questions yet. "
                "Please add your key to the .env file."
            )

        self._history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *self._history[-12:]]

        try:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._config.openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )
            reply = (response.choices[0].message.content or "").strip()
        except Exception as exc:
            log.exception("OpenAI call failed")
            return f"I had trouble reaching the brain: {exc}"

        if reply:
            self._history.append({"role": "assistant", "content": reply})
        return reply or "I'm not sure what to say to that."

    def reset(self) -> None:
        self._history.clear()
