import curses

LOG_HEIGHT = 3


class Log:
    def __init__(
        self,
        stdscr: curses.window,
        n_lines: int,
        n_cols: int,
        begin_y: int,
        begin_x: int,
    ) -> None:
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
