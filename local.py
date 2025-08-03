from __future__ import annotations

import argparse
import curses
import signal
import sys
from types import FrameType

import game
import player
from interaction import ai, dummy, local
from window import common


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


def set_ai_game_instances(players: list[player.Player], g: game.Game) -> None:
    for p in players:
        if isinstance(p.inter, ai.AIInteraction):
            p.inter.set_game_instance(g)


def create_ai_player(name: str) -> player.Player:
    p = player.Player(
        name,
        dummy.DummyInteraction(),
    )
    inter = ai.AIInteraction(p.index)
    p.inter = inter
    return p


class LocalNamespace(argparse.Namespace):
    deck: str
    players: list[str]
    number_of_ais: int


def run_game(stdscr: curses.window, args: LocalNamespace) -> None:
    n_players = args.number_of_ais + len(args.players)
    players = [
        player.Player(
            name,
            local.LocalInteraction(stdscr, n_players=n_players),
        )
        for name in args.players
    ]
    players.extend(
        [create_ai_player(f"AI {i + 1}") for i in range(args.number_of_ais)],
    )
    g = game.Game(players, deck=args.deck, starting_cards=1)
    set_ai_game_instances(players, g)
    g.start()
    while True:
        try:
            g = game_loop(g)
        except game.WonError:
            break
        g.end_turn()


def get_parser_args() -> LocalNamespace:
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument(
        "--deck",
        type=str,
        default="deck.json",
        nargs="?",
        help="Path to the deck file (default: deck.json)",
    )
    parser.add_argument("--players", nargs="*", help="List of player names")
    parser.add_argument(
        "--number-of-ais",
        type=int,
        default=1,
        help="Number of AI players (default: 1)",
    )
    return parser.parse_args(namespace=LocalNamespace())


def curses_exit() -> None:
    curses.curs_set(1)  # Show the cursor again
    curses.endwin()


def curses_main(stdscr: curses.window) -> None:
    args = get_parser_args()
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    try:
        run_game(stdscr, args)
    except Exception:
        curses_exit()
        raise


def signal_handler(_sig: int, _frame: FrameType | None) -> None:
    curses_exit()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    curses.wrapper(curses_main)
