"""
Speech recognition and text-to-speech engine for Jarvis.
"""

import logging
import speech_recognition as sr
import pyttsx3

from jarvis.config import (
    SPEECH_RATE,
    SPEECH_VOLUME,
    LISTEN_TIMEOUT,
    PHRASE_TIME_LIMIT,
)

logger = logging.getLogger(__name__)


class Speaker:
    """Text-to-Speech wrapper using pyttsx3."""

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", SPEECH_RATE)
        self.engine.setProperty("volume", SPEECH_VOLUME)
        voices = self.engine.getProperty("voices")
        # Use a male voice if available
        if voices:
            self.engine.setProperty("voice", voices[0].id)

    def say(self, text: str) -> None:
        """Speak the given text aloud."""
        logger.info("Speaking: %s", text)
        print(f"[Jarvis]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()


class Listener:
    """Microphone listener using SpeechRecognition."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def listen(self) -> str:
        """
        Listen to the microphone and return the recognised text.
        Returns an empty string on failure.
        """
        with sr.Microphone() as source:
            logger.info("Listening …")
            print("[*] Listening …")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )
                text = self.recognizer.recognize_google(audio).lower()
                logger.info("Heard: %s", text)
                print(f"[You]: {text}")
                return text
            except sr.WaitTimeoutError:
                logger.debug("Listen timeout – no speech detected.")
            except sr.UnknownValueError:
                logger.debug("Could not understand audio.")
            except sr.RequestError as exc:
                logger.error("Speech recognition API error: %s", exc)
        return ""
