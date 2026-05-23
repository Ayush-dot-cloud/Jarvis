"""Configuration loaded from environment / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    """Load .env from the project root if present."""
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


_load_env()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    openai_api_key: str
    openai_model: str
    openweather_api_key: str
    news_api_key: str
    default_city: str
    wake_word: str
    voice_index: int
    voice_rate: int
    mic_calibration_seconds: float
    user_name: str

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key) and not self.openai_api_key.startswith("sk-your-")

    @property
    def has_weather(self) -> bool:
        return bool(self.openweather_api_key)

    @property
    def has_news(self) -> bool:
        return bool(self.news_api_key)


def load_config() -> Config:
    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY", "").strip(),
        news_api_key=os.getenv("NEWS_API_KEY", "").strip(),
        default_city=os.getenv("DEFAULT_CITY", "Pune").strip() or "Pune",
        wake_word=os.getenv("WAKE_WORD", "jarvis").strip().lower(),
        voice_index=_get_int("VOICE_INDEX", 0),
        voice_rate=_get_int("VOICE_RATE", 185),
        mic_calibration_seconds=_get_float("MIC_CALIBRATION_SECONDS", 1.0),
        user_name=os.getenv("USER_NAME", "Sir").strip() or "Sir",
    )
