"""
Configuration settings for Jarvis.
"""

import os
from pathlib import Path

# ── Directories ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Speech Settings ──────────────────────────────────────────────────────────
WAKE_WORD = "jarvis"
SPEECH_RATE = 175          # words per minute for TTS
SPEECH_VOLUME = 1.0        # 0.0 to 1.0
LISTEN_TIMEOUT = 5         # seconds to wait for speech
PHRASE_TIME_LIMIT = 10     # max seconds for a single phrase

# ── API Keys (set via environment variables) ──────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")  # OpenWeatherMap

# ── Assistant Persona ─────────────────────────────────────────────────────────
ASSISTANT_NAME = "Jarvis"
GREETING = f"Hello! I am {ASSISTANT_NAME}, your personal assistant. How can I help you today?"

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = LOG_DIR / "jarvis.log"
LOG_LEVEL = "INFO"
