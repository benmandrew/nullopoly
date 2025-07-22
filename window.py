import curses
import util


class Window:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        height, width = stdscr.getmaxyx()
        half_height = height // 2
        self.table_window = stdscr.subwin(half_height, width, 0, 0)
        self.hand_window = stdscr.subwin(
            height - half_height, width, half_height, 0
        )

    def print_game_state(self, player_state_lines: list[list[str]]) -> None:
        self.table_window.clear()
        new_y = 0
        _, scr_width = self.table_window.getmaxyx()
        for i, lines in enumerate(player_state_lines):
            x_offset = scr_width * i // len(player_state_lines)
            for idx, line in enumerate(lines):
                self.table_window.addstr(idx, x_offset, util.strip_ansi(line))
            new_y = max(new_y, len(lines))
        self.table_window.refresh()

    def print_hand(
        self,
        player_name: str,
        hand_lines: list[str],
        hand_len: int,
        played_card_idx: int,
    ) -> None:
        self.hand_window.clear()
        self.hand_window.addstr(0, 0, f"It's {player_name}'s turn")
        lines = [util.strip_ansi(s) for s in hand_lines]
        for idx, line in enumerate(lines):
            self.hand_window.addstr(idx + 1, 0, line)
        self.hand_window.addstr(
            8,
            0,
            f"{3 - played_card_idx} cards left to play this turn.",
        )
        self.hand_window.addstr(
            9,
            0,
            f"Choose a card to play (1-{hand_len}): ",
        )
        self.hand_window.refresh()

    def print_action_dialog(self) -> None:
        self.hand_window.addstr(10, 0, "Choose an option:")
        self.hand_window.addstr(11, 0, "1. Play action")
        self.hand_window.addstr(12, 0, "2. Add to bank")
        self.hand_window.refresh()

    def clear(self):
        self.stdscr.clear()

    def addstr(self, y: int, x: int, string: str):
        self.stdscr.addstr(y, x, string)

    def refresh(self):
        self.stdscr.refresh()

    def getmaxyx(self) -> tuple[int, int]:
        return self.stdscr.getmaxyx()

    def getkey(self) -> str:
        return self.stdscr.getkey()
