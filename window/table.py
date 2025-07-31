import curses

import cards
import player
from window import common


class Table:
    def __init__(
        self,
        stdscr: curses.window,
        n_players: int,
        height: int,
        width: int,
    ) -> None:
        self.table_windows: list[curses.window] = []
        for i in range(n_players):
            table_width = width // n_players
            self.table_windows.append(
                stdscr.subwin(height, table_width, 0, table_width * i),
            )

    def resize(self, height: int, width: int) -> None:
        table_width = width // len(self.table_windows)
        for i, t in enumerate(self.table_windows):
            t.resize(height, table_width)
            t.mvwin(0, table_width * i)

    def clear(self, win: curses.window) -> None:
        win.clear()
        win.border(0, 0, 0, 0, 0, 0, 0, 0)

    def draw(self, players: list[player.Player]) -> None:
        assert len(players) == len(
            self.table_windows,
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
        bank_str = ", ".join(f"£{card.value}" for card in p.bank)
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
            f"{card.name} (£{card.value})" for card in properties.cards
        )
        # Use a bitwise flag to bold the text if the set is complete
        completed = curses.A_BOLD if properties.is_complete() else 0
        win.addstr(
            idx + 3,
            4,
            colour.pretty(),
            completed | curses.color_pair(common.COLOUR_MAP[colour]),
        )
        win.addstr(idx + 3, 15, cards_str, completed)
