import curses
from collections.abc import Callable

import cards
import player


class InvalidChoiceError(Exception):
    """
    Raised when the option taken is invalid.
    """


class LogWindow:
    def __init__(
        self,
        stdscr: curses.window,
        n_lines: int,
        n_cols: int,
        begin_y: int,
        begin_x: int,
    ):
        self.win = stdscr.subwin(n_lines, n_cols, begin_y, begin_x)
        self.log_lines: list[str] = []
        self.log_idx = 0

    def log(self, message: str) -> None:
        self.win.clear()
        if len(self.log_lines) >= 3:
            self.log_lines.pop()
        self.log_lines.append(message)
        self.log_idx += 1
        for i, line in enumerate(self.log_lines):
            s = f"{self.log_idx - len(self.log_lines) + i + 1}."
            self.win.addstr(i, 2, f"{s:<4} {line}")
        self.win.refresh()

    def clear(self) -> None:
        self.win.clear()
        self.log_lines = []
        self.log_idx = 0
        self.win.refresh()


class Window:
    def __init__(self, stdscr: curses.window, n_players: int):
        self.stdscr = stdscr
        height, width = self.stdscr.getmaxyx()
        half_height = height // 2
        log_height = 3
        self.log_window = LogWindow(
            self.stdscr, log_height, width, half_height - log_height, 0
        )
        self.hand_window = self.stdscr.subwin(
            height - half_height, width, half_height, 0
        )
        self.table_windows = []
        for i in range(n_players):
            table_width = width // n_players
            self.table_windows.append(
                self.stdscr.subwin(
                    half_height - log_height, table_width, 0, table_width * i
                )
            )

    def clear_table_window(self, win: curses.window) -> None:
        win.clear()
        win.border(0, 0, 0, 0, 0, 0, 0, 0)
        win.refresh()

    def print_player_state(self, win: curses.window, p: player.Player) -> None:
        self.clear_table_window(win)
        win.addstr(1, 2, f"{p.name}", curses.A_BOLD)
        win.addstr(2, 2, "Properties:")
        idx = 0
        for colour, properties in p.properties.items():
            if not properties.cards:
                continue
            cards_str = ", ".join(
                f"{card.name()} (£{card.value()})" for card in properties.cards
            )
            win.addstr(idx + 3, 4, f"{colour.name.title():<15}: {cards_str}")
            idx += 1
        bank_str = ", ".join(f"£{card.value()}" for card in p.bank)
        win.addstr(idx + 3, 2, f"Bank (£{p.total_bank_value()}): {bank_str}")
        win.refresh()

    def print_game_state(self, players: list[player.Player]) -> None:
        assert len(players) == len(
            self.table_windows
        ), "Number of players must match number of table windows"
        for table_window, p in zip(self.table_windows, players):
            self.print_player_state(table_window, p)

    def clear_hand(self) -> None:
        self.hand_window.clear()
        self.hand_window.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.hand_window.refresh()

    def print_hand(
        self,
        p: player.Player,
        hand_len: int,
        played_card_idx: int,
    ) -> None:
        self.clear_hand()
        self.hand_window.addstr(1, 2, f"It's {p.name}'s turn")
        for idx, line in enumerate(p.fmt_hand()):
            self.hand_window.addstr(idx + 2, 2, line)
        self.hand_window.addstr(
            9,
            2,
            f"{3 - played_card_idx} cards left to play this turn.",
        )
        self.hand_window.addstr(
            10,
            2,
            f"Choose a card to play (1-{hand_len}): ",
        )
        self.hand_window.refresh()

    def print_action_dialog(self) -> None:
        self.clear_hand()
        self.hand_window.addstr(2, 2, "Choose an option:")
        self.hand_window.addstr(3, 2, "1. Play action")
        self.hand_window.addstr(4, 2, "2. Add to bank")
        self.hand_window.refresh()

    def print_target_player_dialog(
        self, players: list[player.Player], exclude: player.Player | None = None
    ) -> None:
        self.clear_hand()
        self.hand_window.addstr(2, 2, "Choose a player to target:")
        idx = 0
        for p in players:
            if p == exclude:
                continue
            self.hand_window.addstr(3 + idx, 2, f"{idx + 1}. {p.name}")
            idx += 1
        self.hand_window.refresh()

    def print_target_property_dialog(self, target: player.Player) -> None:
        self.clear_hand()
        self.hand_window.addstr(2, 2, f"Choose a property from {target.name}:")
        idx = 0
        for _, properties in target.properties.items():
            for prop in properties.cards:
                prop_name = (
                    f"{prop.name()} ({prop.colour().name}) (£{prop.value()})"
                )
                self.hand_window.addstr(3 + idx, 2, f"{idx + 1}. {prop_name}")
                idx += 1
        self.hand_window.refresh()

    def print_rent_colour_choice(
        self, colours: list[tuple[cards.PropertyColour, int]]
    ) -> None:
        self.clear_hand()
        self.hand_window.addstr(2, 2, "Choose a colour to charge rent on:")
        for idx, (colour, rent) in enumerate(colours):
            self.hand_window.addstr(
                3 + idx, 2, f"{idx + 1}. {colour.name} (£{rent})"
            )
        self.hand_window.refresh()

    def log(self, message: str) -> None:
        self.log_window.log(message)

    def get_number_input(self, validation: Callable[[str], bool]) -> int:
        while True:
            key = self.stdscr.getkey()
            if validation(key):
                return int(key)
            self.log("Invalid input, try again")

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
