import curses

import cards
import player


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

    def clear_table_windows(self) -> None:
        for table_window in self.table_windows:
            table_window.clear()
            table_window.border(0, 0, 0, 0, 0, 0, 0, 0)
            table_window.refresh()

    def print_game_state(self, players: list[player.Player]) -> None:
        assert len(players) == len(
            self.table_windows
        ), "Number of players must match number of table windows"
        self.clear_table_windows()
        for table_window, p in zip(self.table_windows, players):
            new_y = 0
            lines = p.fmt_visible_state()
            for idx, line in enumerate(lines):
                table_window.addstr(idx + 1, 2, line)
            new_y = max(new_y, len(lines))
            table_window.refresh()

    def clear_hand(self) -> None:
        self.hand_window.clear()
        self.hand_window.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.hand_window.refresh()

    def print_hand(
        self,
        player_name: str,
        hand_lines: list[str],
        hand_len: int,
        played_card_idx: int,
    ) -> None:
        self.clear_hand()
        self.hand_window.addstr(1, 2, f"It's {player_name}'s turn")
        for idx, line in enumerate(hand_lines):
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
        self, colours: list[cards.PropertyColour]
    ) -> None:
        self.clear_hand()
        self.hand_window.addstr(2, 2, "Choose a colour to charge rent on:")
        for idx, colour in enumerate(colours):
            self.hand_window.addstr(3 + idx, 2, f"{idx + 1}. {colour.name}")
        self.hand_window.refresh()

    def log(self, message: str) -> None:
        self.log_window.log(message)

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
