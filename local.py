from __future__ import annotations

import curses
import signal
import sys
from types import FrameType

import game
import player
from interaction import local
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


def run_game(stdscr: curses.window) -> None:
    player_names = ["Alice", "Bob"]
    local_interaction = local.LocalInteraction(
        stdscr,
        n_players=len(player_names),
    )
    players = [player.Player(name, local_interaction) for name in player_names]
    g = game.Game(players, deck="deck.json")
    g.start()
    while True:
        try:
            g = game_loop(g)
        except game.WonError:
            break
        g.end_turn()


def curses_main(stdscr: curses.window) -> None:
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    run_game(stdscr)
    curses.endwin()


def signal_handler(_sig: int, _frame: FrameType | None) -> None:
    curses.endwin()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    curses.wrapper(curses_main)
