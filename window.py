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


COLOUR_MAP = {
    cards.PropertyColour.BROWN: 1,
    cards.PropertyColour.LIGHT_BLUE: 2,
    cards.PropertyColour.PINK: 3,
    cards.PropertyColour.ORANGE: 4,
    cards.PropertyColour.RED: 5,
    cards.PropertyColour.YELLOW: 6,
    cards.PropertyColour.GREEN: 7,
    cards.PropertyColour.DARK_BLUE: 8,
    cards.PropertyColour.RAILROAD: 9,
    cards.PropertyColour.UTILITY: 10,
}


class Window:
    def __init__(self, stdscr: curses.window, n_players: int):
        self.stdscr = stdscr
        height, width = self.stdscr.getmaxyx()
        half_height = height // 2
        log_height = 3
        self.log = LogWindow(
            self.stdscr, log_height, width, half_height - log_height, 0
        )
        self.hand = Hand(
            self.stdscr, height - half_height, width, half_height, 0
        )
        self.table = Table(
            self.stdscr, n_players, half_height - log_height, width
        )
        self.init_colours()

    def init_colours(self) -> None:
        assert curses.has_colors(), "Terminal does not support colours"
        assert (
            curses.can_change_color()
        ), "Terminal does not support changing colours"
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    def game_over(self) -> None:
        self.hand.game_over(self.stdscr)

    def draw_log(self, message: str) -> None:
        self.log.log(message)

    def get_number_input(self, validation: Callable[[str], bool]) -> int:
        while True:
            key = self.stdscr.getkey()
            if validation(key):
                return int(key)
            self.log.log("Invalid input, try again")

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


class Table:
    def __init__(
        self, stdscr: curses.window, n_players: int, height: int, width: int
    ):
        self.table_windows = []
        for i in range(n_players):
            table_width = width // n_players
            self.table_windows.append(
                stdscr.subwin(height, table_width, 0, table_width * i)
            )

    def clear(self, win: curses.window) -> None:
        win.clear()
        win.border(0, 0, 0, 0, 0, 0, 0, 0)

    def draw(self, players: list[player.Player]) -> None:
        assert len(players) == len(
            self.table_windows
        ), "Number of players must match number of table windows"
        for table_window, p in zip(self.table_windows, players):
            self.draw_player(table_window, p)

    def draw_player(self, win: curses.window, p: player.Player) -> None:
        self.clear(win)
        win.addstr(1, 2, f"{p.name}", curses.A_BOLD)
        win.addstr(2, 2, "Properties:")
        idx = 0
        for colour, properties in p.properties.items():
            if not properties.cards:
                continue
            self.draw_property(win, colour, properties, idx)
            idx += 1
        bank_str = ", ".join(f"£{card.value()}" for card in p.bank)
        win.addstr(idx + 3, 2, f"Bank (£{p.total_bank_value()}): {bank_str}")
        win.refresh()

    def draw_property(
        self,
        win: curses.window,
        colour: cards.PropertyColour,
        properties: player.PropertySet,
        idx: int,
    ) -> None:
        cards_str = ", ".join(
            f"{card.name()} (£{card.value()})" for card in properties.cards
        )
        # Use a bitwise flag to bold the text if the set is complete
        completed = curses.A_BOLD if properties.is_complete() else 0
        win.addstr(
            idx + 3,
            4,
            colour.pretty(),
            completed | curses.color_pair(COLOUR_MAP[colour]),
        )
        win.addstr(idx + 3, 19, cards_str, completed)


class Hand:
    def __init__(
        self, stdscr: curses.window, height: int, width: int, y: int, x: int
    ):
        self.win = stdscr.subwin(height, width, y, x)

    def clear(self) -> None:
        self.win.clear()
        self.win.border(0, 0, 0, 0, 0, 0, 0, 0)

    def draw(
        self,
        p: player.Player,
        hand_len: int,
        played_card_idx: int,
    ) -> None:
        self.clear()
        self.win.addstr(1, 2, f"It's {p.name}'s turn", curses.A_BOLD)
        for idx, line in enumerate(p.fmt_hand()):
            self.win.addstr(idx + 2, 2, line)
        self.win.addstr(
            9,
            2,
            f"{3 - played_card_idx} cards left to play this turn.",
        )
        self.win.addstr(
            10,
            2,
            f"Choose a card to play (1-{hand_len}): ",
        )
        self.win.refresh()

    def draw_action_dialog(self) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose an option:")
        self.win.addstr(3, 2, "1. Play action")
        self.win.addstr(4, 2, "2. Add to bank")
        self.win.refresh()

    def draw_target_player_dialog(
        self, players: list[player.Player], exclude: player.Player | None = None
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose a player to target:")
        idx = 0
        for p in players:
            if p == exclude:
                continue
            self.win.addstr(3 + idx, 2, f"{idx + 1}. {p.name}")
            idx += 1
        self.win.refresh()

    def draw_target_property_dialog(self, target: player.Player) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Choose a property from {target.name}:")
        idx = 0
        for _, properties in target.properties.items():
            for prop in properties.cards:
                prop_name = (
                    f"{prop.name()} ({prop.colour().name}) (£{prop.value()})"
                )
                self.win.addstr(3 + idx, 2, f"{idx + 1}. {prop_name}")
                idx += 1
        self.win.refresh()

    def draw_rent_colour_choice(
        self, colours: list[tuple[cards.PropertyColour, int]]
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose a colour to charge rent on:")
        for idx, (colour, rent) in enumerate(colours):
            self.win.addstr(
                3 + idx, 2, f"{idx + 1}. {colour.pretty()} (£{rent})"
            )
        self.win.refresh()

    def game_over(self, stdscr: curses.window) -> None:
        self.clear()
        self.win.addstr(1, 2, "Game over!")
        self.win.addstr(2, 2, "Press Enter to close.")
        self.win.refresh()
        while True:
            key = stdscr.getch()
            if key in (10, 13):  # Enter key
                break
