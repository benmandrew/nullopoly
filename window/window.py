import curses
import queue
import threading
from dataclasses import dataclass

import player
from window import common, hand, log, table


@dataclass(frozen=True)
class RedrawData:
    current_player: player.Player
    players: list[player.Player]
    n_cards_played: int


class Window:

    def __init__(self, stdscr: curses.window, n_players: int) -> None:
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self.n_players = n_players
        self.redraw_data: RedrawData | None = None
        self.create_windows()
        common.init_colours()
        self.input_queue: queue.Queue[str] = queue.Queue()
        threading.Thread(target=self.input_thread, daemon=True).start()

    def create_windows(self) -> None:
        height, width = self.getmaxyx()
        half_height = height // 2
        self.log = log.Log(
            self.stdscr,
            log.LOG_HEIGHT,
            width,
            half_height - log.LOG_HEIGHT,
            0,
        )
        self.hand = hand.Hand(
            self.stdscr,
            height - half_height,
            width,
            half_height,
            0,
        )
        self.table = table.Table(
            self.stdscr,
            self.n_players,
            half_height - log.LOG_HEIGHT,
            width,
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
            if common.int_range_validator(v_min, v_max)(key):
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

    def clear(self) -> None:
        self.stdscr.clear()

    def addstr(self, y: int, x: int, string: str) -> None:
        self.stdscr.addstr(y, x, string)

    def refresh(self) -> None:
        self.stdscr.refresh()

    def getmaxyx(self) -> tuple[int, int]:
        return self.stdscr.getmaxyx()
