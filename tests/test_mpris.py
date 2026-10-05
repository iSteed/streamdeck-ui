import subprocess
from unittest import mock

from streamdeck_ui import mpris

LIST_NAMES = "(['org.freedesktop.DBus', ':1.20', 'org.mpris.MediaPlayer2.firefox', 'org.mpris.MediaPlayer2.chromium'],)\n"


def fake_gdbus(statuses):
    """Returns a stand-in for subprocess.run that answers gdbus calls from a player -> status map."""

    def run(args, **_kwargs):
        if any(arg.endswith(".ListNames") for arg in args):
            stdout = LIST_NAMES
        else:
            dest = args[args.index("--dest") + 1]
            stdout = f"(<'{statuses[dest]}'>,)\n" if dest in statuses else ""
        return subprocess.CompletedProcess(args, 0, stdout, "")

    return run


def test_is_playing_when_a_player_is_playing():
    with mock.patch(
        "subprocess.run",
        side_effect=fake_gdbus(
            {
                "org.mpris.MediaPlayer2.firefox": "Playing",
                "org.mpris.MediaPlayer2.chromium": "Paused",
            }
        ),
    ):
        assert mpris.is_playing() is True


def test_not_playing_when_players_are_paused_or_stopped():
    with mock.patch(
        "subprocess.run",
        side_effect=fake_gdbus(
            {
                "org.mpris.MediaPlayer2.firefox": "Stopped",
                "org.mpris.MediaPlayer2.chromium": "Paused",
            }
        ),
    ):
        assert mpris.is_playing() is False


def test_not_playing_when_no_player_is_running():
    with mock.patch.object(mpris, "_player_names", return_value=[]):
        assert mpris.is_playing() is False


def test_not_playing_when_gdbus_is_missing():
    with mock.patch("subprocess.run", side_effect=FileNotFoundError):
        assert mpris.is_playing() is False
