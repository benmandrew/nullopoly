import curses
from game import GameState
import util
from player import PlayerState
import window


def get_card_choice(stdscr: curses.window, player: PlayerState) -> int:
    def validation(key: str) -> bool:
        return key.isdigit() and 1 <= int(key) <= len(player.hand)

    return util.get_number_input(stdscr, validation)


def print_game_state(stdscr: curses.window, game: GameState) -> int:
    new_y = 0
    _, scr_width = stdscr.getmaxyx()
    for i, player in enumerate(game.players):
        x_offset = scr_width * i // len(game.players)
        state_lines = [util.strip_ansi(s) for s in player.fmt_visible_state()]
        for idx, line in enumerate(state_lines):
            stdscr.addstr(idx, x_offset, line)
        new_y = max(new_y, len(state_lines))
    return new_y


def curses_main(stdscr: curses.window) -> None:
    curses.curs_set(0)  # Hide the cursor
    win = window.Window(stdscr)
    game = GameState(["Alice", "Bob"], "deck.json")
    game.start()
    while True:
        current_player = game.current_player()
        game.deal_to_player(current_player, 2)
        for i in range(3):
            win.print_game_state(
                [player.fmt_visible_state() for player in game.players]
            )
            win.print_hand(
                current_player.name,
                current_player.fmt_hand(),
                len(current_player.hand),
                i,
            )
            choice = get_card_choice(stdscr, current_player)
            current_player.play_card_from_hand(choice - 1, win)
            if len(current_player.hand) == 0:
                game.deal_from_empty(current_player)
        game.end_turn()


if __name__ == "__main__":
    curses.wrapper(curses_main)
