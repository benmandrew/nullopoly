from __future__ import annotations

import argparse
import curses
import pathlib
import signal
import sys

import game
import player
import util
from interaction import local
from window import common


class LocalNamespace(argparse.Namespace):
    deck: pathlib.Path  # Path to the deck file
    players: list[str]
    n_ais: int  # Number of AI players


def get_parser_args() -> LocalNamespace:
    parser = argparse.ArgumentParser(
        description="Run a local game of Nullopoly.",
        epilog="Example usage: python local.py --players Alice Bob --n-ais 2 --deck custom_deck.json",  # noqa: E501, pylint: disable=line-too-long
    )
    parser.add_argument(
        "--deck",
        type=pathlib.Path,
        default=pathlib.Path("resources/deck.json"),
        nargs="?",
        help="Path to the deck file (default: resources/deck.json)",
    )
    parser.add_argument("--players", nargs="*", help="List of player names")
    parser.add_argument(
        "--n-ais",
        type=int,
        default=1,
        help="Number of AI players (default: 1)",
    )
    return parser.parse_args(namespace=LocalNamespace())


def game_loop(g: game.Game) -> game.Game:
    current_player = g.current_player()
    g.deal_to_player(current_player, 2)
    n_cards_played = 0
    while n_cards_played < 3:
        g.draw(n_cards_played)
        try:
            c = g.choose_card_in_hand(current_player)
            g.play_card(c, current_player)
        except common.InvalidChoiceError:
            continue
        n_cards_played += 1
        current_player.remove_card_from_hand(c)
        if not current_player.hand:
            g.deal_from_empty(current_player)
        if g.check_win():
            raise game.WonError
    g.draw(n_cards_played)
    return g


def run_game(stdscr: curses.window, args: LocalNamespace) -> None:
    n_players = args.n_ais + len(args.players)
    players = [
        player.Player(
            name,
            local.LocalInteraction(stdscr, n_players=n_players),
        )
        for name in args.players
    ]
    players.extend(
        [util.create_ai_player(f"AI {i + 1}") for i in range(args.n_ais)],
    )
    g = game.Game(players, deck=args.deck)
    util.set_ai_game_instances(players, g)
    g.start()
    while True:
        try:
            g = game_loop(g)
        except game.WonError:
            break
        g.end_turn()


def curses_main(stdscr: curses.window) -> None:
    args = get_parser_args()
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    try:
        run_game(stdscr, args)
    except Exception:
        util.curses_exit()
        raise


if __name__ == "__main__":
    util.check_python_version()
    if "--help" in sys.argv or "-h" in sys.argv:
        get_parser_args()
    else:
        signal.signal(signal.SIGINT, util.curses_signal_handler)
        curses.wrapper(curses_main)
