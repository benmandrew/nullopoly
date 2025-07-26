import curses

import game
import player
import util
import window


def get_card_choice(stdscr: curses.window, p: player.Player) -> int:
    def validation(key: str) -> bool:
        return key.isdigit() and 1 <= int(key) <= len(p.hand)

    return util.get_number_input(stdscr, validation)


def print_game_state(stdscr: curses.window, g: game.Game) -> int:
    new_y = 0
    _, scr_width = stdscr.getmaxyx()
    for i, p in enumerate(g.players):
        x_offset = scr_width * i // len(g.players)
        state_lines = [util.strip_ansi(s) for s in p.fmt_visible_state()]
        for idx, line in enumerate(state_lines):
            stdscr.addstr(idx, x_offset, line)
        new_y = max(new_y, len(state_lines))
    return new_y


def curses_main(stdscr: curses.window) -> None:
    curses.curs_set(0)  # Hide the cursor
    win = window.Window(stdscr)
    g = game.Game(["Alice", "Bob"], deck="deck.json", win=win)
    g.start()
    while True:
        current_player = g.current_player()
        g.deal_to_player(current_player, 2)
        for i in range(3):
            win.print_game_state([p.fmt_visible_state() for p in g.players])
            win.print_hand(
                current_player.name,
                current_player.fmt_hand(),
                len(current_player.hand),
                i,
            )
            choice = get_card_choice(stdscr, current_player)
            c = current_player.remove_card_from_hand(choice - 1)
            if len(current_player.hand) == 0:
                g.deal_from_empty(current_player)
            g.play_card(c, current_player)
        g.charge_payment(current_player, 5)
        g.end_turn()


if __name__ == "__main__":
    curses.wrapper(curses_main)
