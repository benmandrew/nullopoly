from __future__ import annotations

import curses
import signal
import sys
from types import FrameType

import game
import player
from interaction import ai, local
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


def run_game(stdscr: curses.window) -> None:
    players = [
        player.Player(
            "Ben",
            local.LocalInteraction(
                stdscr,
                n_players=2,
            ),
        ),
        player.Player("AI", ai.AIInteraction(1)),
    ]
    g = game.Game(players, deck="deck.json")
    set_ai_game_instances(players, g)
    g.start()
    while True:
        try:
            g = game_loop(g)
        except game.WonError:
            break
        g.end_turn()


def curses_exit() -> None:
    curses.curs_set(1)  # Show the cursor again
    curses.endwin()


def curses_main(stdscr: curses.window) -> None:
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    try:
        run_game(stdscr)
    except Exception:
        curses_exit()
        raise


def signal_handler(_sig: int, _frame: FrameType | None) -> None:
    curses_exit()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    curses.wrapper(curses_main)
