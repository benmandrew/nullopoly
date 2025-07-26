import curses

import game
import window


def print_game_state(stdscr: curses.window, g: game.Game) -> int:
    new_y = 0
    _, scr_width = stdscr.getmaxyx()
    for i, p in enumerate(g.players):
        x_offset = scr_width * i // len(g.players)
        state_lines = p.fmt_visible_state()
        for idx, line in enumerate(state_lines):
            stdscr.addstr(idx, x_offset, line)
        new_y = max(new_y, len(state_lines))
    return new_y


def curses_main(stdscr: curses.window) -> None:
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    assert curses.has_colors(), "Terminal does not support colors"
    win = window.Window(stdscr, n_players=2)
    g = game.Game(["Alice", "Bob"], deck="deck.json", win=win)
    g.start()
    while True:
        current_player = g.current_player()
        g.deal_to_player(current_player, 2)
        n_cards_played = 0
        while n_cards_played < 3:
            win.print_game_state(g.players)
            win.print_hand(
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
        g.end_turn()


if __name__ == "__main__":
    curses.wrapper(curses_main)
