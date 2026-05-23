"""Speech recognition (mic in) and text-to-speech (speakers out).

We use:
- `pyttsx3` for offline TTS (uses Windows SAPI5 on Windows).
- `speech_recognition` + Google's free web recognizer for STT.

Both wrapped so the rest of the app stays simple.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

try:
    import pyttsx3
except ImportError:  # pragma: no cover - import-time fallback for CI
    pyttsx3 = None  # type: ignore[assignment]

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None  # type: ignore[assignment]

from jarvis.config import Config

log = logging.getLogger("jarvis.voice")


class Speaker:
    """Thread-safe wrapper around pyttsx3 for synchronous speech."""

    def __init__(self, config: Config) -> None:
        if pyttsx3 is None:
            raise RuntimeError(
                "pyttsx3 is not installed. Run: pip install -r requirements.txt"
            )
        self._engine = pyttsx3.init()
        self._lock = threading.Lock()
        self._configure(config)

    def _configure(self, config: Config) -> None:
        try:
            self._engine.setProperty("rate", config.voice_rate)
        except Exception as exc:  # pragma: no cover
            log.warning("Could not set voice rate: %s", exc)

        try:
            voices = self._engine.getProperty("voices") or []
            if voices:
                idx = max(0, min(config.voice_index, len(voices) - 1))
                self._engine.setProperty("voice", voices[idx].id)
        except Exception as exc:  # pragma: no cover
            log.warning("Could not set voice: %s", exc)

    def say(self, text: str) -> None:
        if not text:
            return
        log.info("Jarvis: %s", text)
        print(f"\033[36mJarvis:\033[0m {text}")
        with self._lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except RuntimeError:
                # pyttsx3 sometimes raises if runAndWait is called twice quickly
                pass


class Listener:
    """Wrap speech_recognition.Recognizer + Microphone."""

    def __init__(self, config: Config) -> None:
        if sr is None:
            raise RuntimeError(
                "SpeechRecognition / PyAudio not installed. Run: pip install -r requirements.txt"
            )
        self._recognizer = sr.Recognizer()
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.pause_threshold = 0.8
        self._microphone = sr.Microphone()
        self._calibration_seconds = config.mic_calibration_seconds

        with self._microphone as source:
            log.info("Calibrating microphone for ambient noise...")
            self._recognizer.adjust_for_ambient_noise(
                source, duration=self._calibration_seconds
            )

    def listen(self, timeout: Optional[float] = None, phrase_time_limit: float = 8.0) -> Optional[str]:
        """Listen once and return recognized text (lowercased), or None on timeout/error."""
        try:
            with self._microphone as source:
                print("\033[90m[listening...]\033[0m")
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
        except sr.WaitTimeoutError:
            return None
        except Exception as exc:
            log.warning("Listen error: %s", exc)
            return None

        try:
            text = self._recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as exc:
            log.warning("Speech recognition service error: %s", exc)
            return None

        text = text.strip().lower()
        if text:
            print(f"\033[33mYou:\033[0m {text}")
        return text or None
