"""Main Jarvis event loop.

Flow:
1. Speak a greeting.
2. Loop:
   a. Listen for an utterance.
   b. If WAKE_WORD is configured and not heard, ignore.
   c. Strip the wake word from the utterance, route it.
   d. Speak the reply. Exit if the router asked us to.
"""

from __future__ import annotations

import datetime as _dt
import logging
import sys

from jarvis.brain import Brain
from jarvis.config import Config, load_config
from jarvis.router import Router
from jarvis.voice import Listener, Speaker


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    # Mute very chatty libraries.
    logging.getLogger("comtypes").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _greeting(config: Config) -> str:
    hour = _dt.datetime.now().hour
    if hour < 12:
        part = "Good morning"
    elif hour < 18:
        part = "Good afternoon"
    else:
        part = "Good evening"
    return f"{part}, {config.user_name}. Jarvis online and ready."


def _strip_wake_word(text: str, wake_word: str) -> str | None:
    """Return the command portion of `text` if the wake word is present, else None.

    If `wake_word` is empty, every utterance is considered a command.
    """
    if not wake_word:
        return text
    if wake_word not in text:
        return None
    # Strip everything up to and including the first occurrence of the wake word.
    idx = text.find(wake_word)
    return text[idx + len(wake_word):].strip(" ,.!?")


def main() -> int:
    _setup_logging()
    log = logging.getLogger("jarvis")

    config = load_config()
    if not config.has_openai:
        print(
            "\033[33mWarning:\033[0m OPENAI_API_KEY is not set. Free-form questions "
            "will not work. Edit your .env file to enable them.\n",
            file=sys.stderr,
        )

    try:
        speaker = Speaker(config)
    except Exception as exc:
        print(f"\033[31mFailed to initialise speaker:\033[0m {exc}", file=sys.stderr)
        return 1

    try:
        listener = Listener(config)
    except Exception as exc:
        print(f"\033[31mFailed to initialise microphone:\033[0m {exc}", file=sys.stderr)
        print(
            "Hint: on Windows, if PyAudio failed to install, run:\n"
            "    pip install pipwin && pipwin install pyaudio",
            file=sys.stderr,
        )
        return 1

    brain = Brain(config)
    router = Router(config, brain)

    speaker.say(_greeting(config))
    if config.wake_word:
        speaker.say(f"Say {config.wake_word} followed by a command.")

    try:
        while True:
            utterance = listener.listen()
            if not utterance:
                continue

            command = _strip_wake_word(utterance, config.wake_word)
            if command is None:
                log.debug("Wake word not detected; ignoring.")
                continue
            if not command:
                speaker.say("Yes?")
                continue

            reply = router.handle(command)
            if reply.text:
                speaker.say(reply.text)
            if reply.should_exit:
                return 0
    except KeyboardInterrupt:
        speaker.say(f"Goodbye, {config.user_name}.")
        return 0
