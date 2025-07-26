import curses
import signal
import sys

import game
import window


class WonError(Exception):
    """
    Raised when a player has won the game.
    """


def game_loop(g: game.Game) -> game.Game:
    current_player = g.current_player()
    g.deal_to_player(current_player, 2)
    n_cards_played = 0
    while n_cards_played < 3:
        g.win.print_game_state(g.players)
        g.win.print_hand(
            current_player,
            len(current_player.hand),
            n_cards_played,
        )
        try:
            choice = g.get_card_choice(current_player)
            c = current_player.get_card_in_hand(choice - 1)
            g.play_card(c, current_player)
        except window.InvalidChoiceError:
            continue
        n_cards_played += 1
        current_player.remove_card_from_hand(choice - 1)
        if len(current_player.hand) == 0:
            g.deal_from_empty(current_player)
        if g.check_win():
            raise WonError()
    return g


def curses_main(stdscr: curses.window) -> None:
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    players = ["Alice", "Bob"]
    win = window.Window(stdscr, n_players=len(players))
    g = game.Game(players, deck="deck.json", win=win)
    g.start()
    while True:
        try:
            g = game_loop(g)
        except WonError:
            break
        g.end_turn()
    g.win.game_over()
    curses.endwin()


def signal_handler(_sig, _frame):
    curses.endwin()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    curses.wrapper(curses_main)
