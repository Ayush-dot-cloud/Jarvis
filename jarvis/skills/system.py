"""System control skills: open apps, volume, lock/shutdown.

Most of these are Windows-focused but degrade gracefully on other OSes.
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess

log = logging.getLogger("jarvis.skills.system")


IS_WINDOWS = platform.system() == "Windows"


KNOWN_APPS_WINDOWS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "settings": "ms-settings:",
    "edge": "msedge.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "vscode": "code.exe",
    "visual studio code": "code.exe",
    "code": "code.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
}


def open_app(name: str) -> str:
    name = name.strip().lower()
    if not name:
        return "Which app should I open?"

    if IS_WINDOWS:
        target = KNOWN_APPS_WINDOWS.get(name, name)
        try:
            os.startfile(target)  # type: ignore[attr-defined]
            return f"Opening {name}."
        except FileNotFoundError:
            try:
                subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
                return f"Opening {name}."
            except Exception as exc:
                log.warning("open_app failed: %s", exc)
                return f"I couldn't find an app called {name}."
        except Exception as exc:
            log.warning("open_app error: %s", exc)
            return f"I couldn't open {name}: {exc}"

    executable = shutil.which(name)
    if not executable:
        return f"I don't know how to open {name} on this system."
    try:
        subprocess.Popen([executable])
        return f"Opening {name}."
    except Exception as exc:
        return f"I couldn't open {name}: {exc}"


def volume_up() -> str:
    if IS_WINDOWS:
        _send_keys("{VOLUME_UP}", repeat=5)
        return "Volume up."
    return "Volume control is only supported on Windows for now."


def volume_down() -> str:
    if IS_WINDOWS:
        _send_keys("{VOLUME_DOWN}", repeat=5)
        return "Volume down."
    return "Volume control is only supported on Windows for now."


def volume_mute() -> str:
    if IS_WINDOWS:
        _send_keys("{VOLUME_MUTE}")
        return "Muted."
    return "Volume control is only supported on Windows for now."


def lock_screen() -> str:
    if IS_WINDOWS:
        try:
            import ctypes

            ctypes.windll.user32.LockWorkStation()  # type: ignore[attr-defined]
            return "Locking the screen."
        except Exception as exc:
            return f"Could not lock: {exc}"
    return "Lock is only supported on Windows for now."


def shutdown(delay_seconds: int = 30) -> str:
    if IS_WINDOWS:
        try:
            subprocess.Popen(["shutdown", "/s", "/t", str(delay_seconds)])
            return f"Shutting down in {delay_seconds} seconds. Say 'cancel shutdown' to abort."
        except Exception as exc:
            return f"Could not shut down: {exc}"
    return "Shutdown is only supported on Windows for now."


def cancel_shutdown() -> str:
    if IS_WINDOWS:
        try:
            subprocess.Popen(["shutdown", "/a"])
            return "Shutdown cancelled."
        except Exception as exc:
            return f"Could not cancel: {exc}"
    return "Not applicable on this system."


def restart(delay_seconds: int = 30) -> str:
    if IS_WINDOWS:
        try:
            subprocess.Popen(["shutdown", "/r", "/t", str(delay_seconds)])
            return f"Restarting in {delay_seconds} seconds. Say 'cancel shutdown' to abort."
        except Exception as exc:
            return f"Could not restart: {exc}"
    return "Restart is only supported on Windows for now."


def _send_keys(key: str, repeat: int = 1) -> None:
    """Use a tiny PowerShell SendKeys call to drive media/volume keys on Windows."""
    if not IS_WINDOWS:
        return
    script = (
        "$wsh = New-Object -ComObject WScript.Shell; "
        + ";".join([f"$wsh.SendKeys('{key}')"] * repeat)
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:  # pragma: no cover
        log.warning("SendKeys failed: %s", exc)
