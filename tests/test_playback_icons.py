from unittest import mock

from streamdeck_ui import api
from streamdeck_ui.display.image_filter import ImageFilter

PLAY = "/icons/play.png"
PAUSE = "/icons/pause.png"


def make_server():
    server = api.StreamDeckServer()
    server.state = {
        "SERIAL": {
            "buttons": {
                "0": {
                    "12": {"icon": PLAY, "mpris_icons": {"playing": PAUSE, "paused": PLAY}},
                    "11": {"icon": "/icons/prev.png"},
                }
            }
        }
    }
    server.display_handlers = {"SERIAL": mock.Mock()}
    return server


def icon_drawn(server):
    """Returns the icon path the display was last given for key 12."""
    filters = server.display_handlers["SERIAL"].replace.call_args.args[2]
    return next(f.file for f in filters if isinstance(f, ImageFilter))


def test_button_shows_play_icon_when_not_playing():
    server = make_server()
    server.update_button_filters("SERIAL", "0", "12")
    assert icon_drawn(server) == PLAY


def test_set_playing_switches_to_pause_icon_and_back():
    server = make_server()
    server.update_button_filters("SERIAL", "0", "12")

    server.set_playing(True)
    assert icon_drawn(server) == PAUSE

    server.set_playing(False)
    assert icon_drawn(server) == PLAY


def test_set_playing_only_redraws_mpris_buttons():
    server = make_server()
    server.set_playing(True)
    server.display_handlers["SERIAL"].replace.reset_mock()

    server.set_playing(False)
    # replace(page, button, filters): only key 12 has mpris_icons, so key 11 is not redrawn
    buttons_redrawn = [c.args[1] for c in server.display_handlers["SERIAL"].replace.call_args_list]
    assert buttons_redrawn == ["12"]


def test_set_playing_reports_whether_state_changed():
    server = make_server()
    assert server.set_playing(True) is True
    assert server.set_playing(True) is False
    assert server.set_playing(False) is True
