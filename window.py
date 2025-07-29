import curses
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass

import cards
import player


def int_range_validator(v_min: int, v_max: int) -> Callable[[str], bool]:
    """
    Returns a validation function that checks if a key is a digit
    and within the specified range (inclusive).
    """

    def validator(key: str) -> bool:
        return key.isdigit() and v_min <= int(key) <= v_max

    return validator


def is_enter_key(key: str) -> bool:
    """
    Returns True if the key is an Enter key (either '\n' or '\r').
    """
    return key in ("\n", "\r", chr(10), chr(13))


def init_colours() -> None:
    assert curses.has_colors(), "Terminal does not support colours"
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.BROWN],
        curses.COLOR_WHITE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.LIGHT_BLUE],
        curses.COLOR_CYAN,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.PINK],
        curses.COLOR_MAGENTA,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.ORANGE],
        curses.COLOR_WHITE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.RED],
        curses.COLOR_RED,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.YELLOW],
        curses.COLOR_YELLOW,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.GREEN],
        curses.COLOR_GREEN,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.DARK_BLUE],
        curses.COLOR_BLUE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.RAILROAD],
        curses.COLOR_BLACK,
        curses.COLOR_WHITE,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.UTILITY],
        curses.COLOR_BLACK,
        curses.COLOR_YELLOW,
    )


class InvalidChoiceError(Exception):
    """
    Raised when the option taken is invalid.
    """


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


@dataclass(frozen=True)
class RedrawData:
    current_player: player.Player
    players: list[player.Player]
    n_cards_played: int


class Window:

    def __init__(self, stdscr: curses.window, n_players: int):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self.n_players = n_players
        self.redraw_data: RedrawData | None = None
        self.create_windows()
        init_colours()
        self.input_queue: queue.Queue[str] = queue.Queue()
        threading.Thread(target=self.input_thread, daemon=True).start()

    def create_windows(self) -> None:
        height, width = self.getmaxyx()
        half_height = height // 2
        self.log = Log(
            self.stdscr,
            Log.LOG_HEIGHT,
            width,
            half_height - Log.LOG_HEIGHT,
            0,
        )
        self.hand = Hand(
            self.stdscr, height - half_height, width, half_height, 0
        )
        self.table = Table(
            self.stdscr, self.n_players, half_height - Log.LOG_HEIGHT, width
        )

    def draw(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        self.redraw_data = RedrawData(
            current_player=current_player,
            players=players,
            n_cards_played=n_cards_played,
        )
        self.table.draw(players)
        self.log.draw()
        self.hand.draw(
            current_player,
            len(current_player.hand),
            n_cards_played,
        )

    def input_thread(self) -> None:
        while True:
            try:
                key = self.stdscr.getch()
                if key == -1:
                    continue
                if key == curses.KEY_RESIZE:
                    self.resize()
                else:
                    self.input_queue.put(chr(key))
            except curses.error:
                continue

    def get_number_input(self, v_min: int, v_max: int) -> int:
        while True:
            key = self.input_queue.get()
            if int_range_validator(v_min, v_max)(key):
                return int(key)
            self.log.log("Invalid input, try again")

    def resize(self) -> None:
        assert (
            self.redraw_data is not None
        ), "Redraw data must be set before resizing"
        self.create_windows()
        self.draw(
            self.redraw_data.current_player,
            self.redraw_data.players,
            self.redraw_data.n_cards_played,
        )

    def turn_over(self, next_player_name: str) -> None:
        self.hand.turn_over(self.input_queue, next_player_name)

    def game_over(self) -> None:
        self.hand.game_over(self.input_queue)

    def draw_log(self, message: str) -> None:
        self.log.log(message)

    def clear(self):
        self.stdscr.clear()

    def addstr(self, y: int, x: int, string: str):
        self.stdscr.addstr(y, x, string)

    def refresh(self):
        self.stdscr.refresh()

    def getmaxyx(self) -> tuple[int, int]:
        return self.stdscr.getmaxyx()


class Table:
    def __init__(
        self, stdscr: curses.window, n_players: int, height: int, width: int
    ):
        self.table_windows: list[curses.window] = []
        for i in range(n_players):
            table_width = width // n_players
            self.table_windows.append(
                stdscr.subwin(height, table_width, 0, table_width * i)
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
            completed | curses.color_pair(COLOUR_MAP[colour]),
        )
        win.addstr(idx + 3, 15, cards_str, completed)


class Hand:

    CARD_HEIGHT = 5

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
        x = 2
        for i, card in enumerate(p.hand):
            self.win.addstr(2, x, f"{i + 1}.")
            x = self.draw_card(card, 3, x)
        # for idx, line in enumerate(p.fmt_hand()):
        #     self.win.addstr(idx + 2, 2, line)
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

    def draw_card(self, card: cards.Card, y: int, x: int) -> int:
        """
        Draws a card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        if isinstance(card, cards.ActionCard):
            return self.draw_action_card(card, y, x)
        if isinstance(card, cards.PropertyCard):
            return self.draw_property_card(card, y, x)
        if isinstance(card, cards.MoneyCard):
            return self.draw_money_card(card, y, x)
        raise ValueError(f"Unknown card type: {type(card)}")

    def draw_box(self, y: int, x: int, height: int, width: int) -> None:
        self.win.addch(y, x, curses.ACS_ULCORNER)
        self.win.hline(y, x + 1, curses.ACS_HLINE, width - 2)
        self.win.addch(y, x + width - 1, curses.ACS_URCORNER)
        self.win.vline(y + 1, x, curses.ACS_VLINE, height - 2)
        self.win.vline(y + 1, x + width - 1, curses.ACS_VLINE, height - 2)
        self.win.addch(y + height - 1, x, curses.ACS_LLCORNER)
        self.win.hline(y + height - 1, x + 1, curses.ACS_HLINE, width - 2)
        self.win.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)

    def draw_rent_wild_content(
        self, y: int, x: int, card: cards.ActionCard
    ) -> None:
        assert (
            card.action == cards.ActionType.RENT_WILD
        ), "Action type must be rent wild"
        self.win.addstr(y, x, "Rent")
        self.win.addstr(
            y + 1,
            x,
            "W",
            curses.color_pair(COLOUR_MAP[cards.PropertyColour.RED]),
        )
        self.win.addstr(
            y + 1,
            x + 1,
            "i",
            curses.color_pair(COLOUR_MAP[cards.PropertyColour.GREEN]),
        )
        self.win.addstr(
            y + 1,
            x + 2,
            "l",
            curses.color_pair(COLOUR_MAP[cards.PropertyColour.YELLOW]),
        )
        self.win.addstr(
            y + 1,
            x + 3,
            "d",
            curses.color_pair(COLOUR_MAP[cards.PropertyColour.LIGHT_BLUE]),
        )
        self.win.addstr(y + 2, x, f"£{card.value}")

    def draw_rent_content(self, y: int, x: int, card: cards.ActionCard) -> None:
        assert (
            card.action in cards.RENT_CARD_COLOURS
        ), "Action type must be rent"
        if card.action == cards.ActionType.RENT_WILD:
            self.draw_rent_wild_content(y, x, card)
            return
        colours = cards.RENT_CARD_COLOURS[card.action]
        assert len(colours) == 2, "Rent action must have two colours"
        self.win.addstr(y, x, "Rent")
        first = colours[0].pretty()
        self.win.addstr(
            y + 1, x, f"{first}", curses.color_pair(COLOUR_MAP[colours[0]])
        )
        self.win.addstr(
            y + 1,
            x + len(first) + 1,
            f"{colours[1].pretty()}",
            curses.color_pair(COLOUR_MAP[colours[1]]),
        )
        self.win.addstr(y + 2, x, f"£{card.value}")

    def draw_action_card(self, card: cards.ActionCard, y: int, x: int) -> int:
        """
        Draws an action card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        action_str = card.action.pretty()
        if cards.is_rent_action(card.action):
            rent, colours = action_str.split(" ", 1)
            lines = [rent, colours, f"£{card.value}"]
        else:
            lines = [action_str, "", f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, self.CARD_HEIGHT, width)
        if cards.is_rent_action(card.action):
            self.draw_rent_content(y + 1, x + 2, card)
        else:
            self.win.addstr(y + 1, x + 2, action_str)
            self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

    def draw_property_card(
        self, card: cards.PropertyCard, y: int, x: int
    ) -> int:
        """
        Draws a property card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        colour_str = card.colour.pretty()
        lines = [card.name, colour_str, f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, self.CARD_HEIGHT, width)
        self.win.addstr(y + 1, x + 2, card.name)
        self.win.addstr(
            y + 2, x + 2, colour_str, curses.color_pair(COLOUR_MAP[card.colour])
        )
        self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

    def draw_money_card(self, card: cards.MoneyCard, y: int, x: int) -> int:
        """
        Draws a money card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        lines = ["Money", f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, self.CARD_HEIGHT, width)
        self.win.addstr(y + 1, x + 2, "Money")
        self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

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

    def draw_target_property_dialog(
        self, target: player.Player, without_full_sets=False
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Choose a property from {target.name}:")
        properties = target.properties_to_list(
            without_full_sets=without_full_sets
        )
        for i, prop in enumerate(properties):
            prop_name = f"{prop.name} ({prop.colour.pretty()}) (£{prop.value})"
            self.win.addstr(3 + i, 2, f"{i + 1}. {prop_name}")
        self.win.refresh()

    def draw_target_full_set_dialog(self, target: player.Player) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Choose a full property set from {target.name}:")
        full_sets = [
            colour
            for colour, properties in target.properties.items()
            if properties.is_complete()
        ]
        for idx, colour in enumerate(full_sets):
            self.win.addstr(
                3 + idx,
                2,
                f"{idx + 1}. {colour.pretty()}",
            )
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

    def turn_over(
        self, input_queue: queue.Queue, next_player_name: str
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Next player: {next_player_name}", curses.A_BOLD)
        self.win.addstr(3, 2, "Press Enter to start turn.")
        self.win.refresh()
        while True:
            key = input_queue.get()
            if is_enter_key(key):
                break

    def game_over(self, input_queue: queue.Queue) -> None:
        self.clear()
        self.win.addstr(1, 2, "Game over!")
        self.win.addstr(2, 2, "Press Enter to close.")
        self.win.refresh()
        while True:
            key = input_queue.get()
            if is_enter_key(key):
                break


class Log:

    LOG_HEIGHT = 3

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
        if len(self.log_lines) >= 3:
            self.log_lines.pop()
        self.log_lines.append(message)
        self.log_idx += 1
        self.draw()

    def draw(self) -> None:
        self.win.clear()
        for i, line in enumerate(self.log_lines):
            s = f"{self.log_idx - len(self.log_lines) + i + 1}."
            self.win.addstr(i, 2, f"{s:<4} {line}")
        self.win.refresh()

    def clear(self) -> None:
        self.win.clear()
        self.log_lines = []
        self.log_idx = 0
        self.win.refresh()
