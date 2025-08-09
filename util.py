from __future__ import annotations

import curses
import json
import logging.config
import pathlib
import sys
from typing import TYPE_CHECKING

import player
from interaction import ai, dummy

if TYPE_CHECKING:
    from types import FrameType

    import game


class PythonVersionError(Exception):
    pass


def check_python_version() -> None:
    if sys.version_info < (3, 12):
        msg = "Requires Python 3.12 or higher."
        raise PythonVersionError(msg)


def curses_exit() -> None:
    curses.curs_set(1)  # Show the cursor again
    curses.endwin()


def curses_signal_handler(_sig: int, _frame: FrameType | None) -> None:
    curses_exit()
    sys.exit(0)


def create_ai_player(name: str) -> player.Player:
    p = player.Player(
        name,
        dummy.DummyInteraction(),
    )
    inter = ai.AIInteraction(p.index)
    p.inter = inter
    return p


def set_ai_game_instances(players: list[player.Player], g: game.Game) -> None:
    for p in players:
        if isinstance(p.inter, ai.AIInteraction):
            p.inter.set_game_instance(g)


def setup_logging() -> None:
    config_file = pathlib.Path("resources/logging.conf")
    with config_file.open(encoding="utf-8") as f:
        config = json.load(f)
    logging.config.dictConfig(config)
