#!/usr/bin/env python3
"""
Jarvis – A personal, voice-activated AI assistant.

Usage:
    python main.py
"""

from jarvis.utils import setup_logging
from jarvis.assistant import Jarvis


def main():
    setup_logging()
    assistant = Jarvis()
    try:
        assistant.start()
    except KeyboardInterrupt:
        assistant.stop()
        print("\n[Jarvis]: Goodbye!")


if __name__ == "__main__":
    main()
