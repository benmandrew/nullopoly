import curses
from game import GameState
import util


def get_card_choice(stdscr, player) -> int:
    stdscr.addstr(f"Choose a card to play (1-{len(player.hand)}): ")
    while True:
        key = stdscr.getkey()
        if key.isdigit():
            choice = int(key)
            if 1 <= choice <= len(player.hand):
                return choice
        stdscr.addstr("Invalid input. Try again.  ")
        stdscr.refresh()


def curses_main(stdscr: curses.window) -> None:
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()
    game = GameState(["Alice"], "deck.json")
    game.start()
    while True:
        current_player = game.current_player()
        game.deal_to_player(current_player, 2)
        for i in range(3):
            stdscr.clear()
            state_lines = util.strip_ansi(current_player.fmt_state()).split(
                "\n"
            )
            for idx, line in enumerate(state_lines):
                stdscr.addstr(idx, 0, line)
            stdscr.addstr(
                len(state_lines) + 1,
                0,
                f"{3 - i} cards left to play this turn.",
            )
            stdscr.addstr(
                len(state_lines) + 2,
                0,
                f"Choose a card to play (1-{len(current_player.hand)}): ",
            )
            stdscr.refresh()
            choice = get_card_choice(stdscr, current_player)
            current_player.play_card_from_hand(choice - 1)
            if len(current_player.hand) == 0:
                game.deal_from_empty(current_player)
        game.end_turn()
        stdscr.addstr(
            len(state_lines) + 3 + len(current_player.hand) + 5,
            0,
            "Press any key for next turn...",
        )
        stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(curses_main)
