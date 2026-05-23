"""Built-in command skills.

Each skill module exposes one or more functions registered with the router.
"""

from jarvis.skills import info, media, system, utility, web

__all__ = ["info", "media", "system", "utility", "web"]
