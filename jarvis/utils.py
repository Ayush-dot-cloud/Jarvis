"""
Utility helpers for Jarvis.
"""

import logging
from logging.handlers import RotatingFileHandler

from jarvis.config import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """Configure application-wide logging."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(log_format))

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(log_format))

    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    root.addHandler(handler)
    root.addHandler(console)
