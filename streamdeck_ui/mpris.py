"""Reads playback state from MPRIS media players over D-Bus, using gdbus."""

import re
import subprocess

_PLAYER_RE = re.compile(r"org\.mpris\.MediaPlayer2\.[^'\s,)]+")
_STATUS_RE = re.compile(r"'(Playing|Paused|Stopped)'")
_GDBUS_TIMEOUT = 2  # seconds


def _gdbus(*args: str) -> str:
    """Runs gdbus against the session bus and returns its stdout, or "" on failure."""
    try:
        result = subprocess.run(
            ["gdbus", "call", "--session", *args],
            capture_output=True,
            text=True,
            timeout=_GDBUS_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout


def _player_names() -> list:
    return _PLAYER_RE.findall(
        _gdbus(
            "--dest",
            "org.freedesktop.DBus",
            "--object-path",
            "/org/freedesktop/DBus",
            "--method",
            "org.freedesktop.DBus.ListNames",
        )
    )


def _playback_status(player: str) -> str:
    match = _STATUS_RE.search(
        _gdbus(
            "--dest",
            player,
            "--object-path",
            "/org/mpris/MediaPlayer2",
            "--method",
            "org.freedesktop.DBus.Properties.Get",
            "org.mpris.MediaPlayer2.Player",
            "PlaybackStatus",
        )
    )
    return match.group(1) if match else ""


def is_playing() -> bool:
    """Returns True if any MPRIS player reports PlaybackStatus "Playing".

    A missing session bus, a missing gdbus, or no running player all return False.
    """
    return any(_playback_status(player) == "Playing" for player in _player_names())
